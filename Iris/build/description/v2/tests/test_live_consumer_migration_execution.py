from __future__ import annotations

import hashlib
import json
import os, shutil, subprocess, sys, tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_live_consumer_migration_execution"
SUCCESSOR_ROOT = REPO / "Iris/_docs/refactor/test_precision_lightweighting/terminal_closeout_recovery"

sys.path.insert(0, str(TOOLS))

import dvf_3_3_live_consumer_migration_execution_common as live_common  # noqa: E402
from dvf_3_3_live_consumer_migration_execution_common import materialize_line_patch, validate_all  # noqa: E402
from _dvf_3_3_vnext_common import canonical_hash  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def git_last_change_commit(path: Path) -> str:
    relative = path.resolve().relative_to(REPO.resolve()).as_posix()
    result = subprocess.run(
        ["git", "log", "-1", "--format=%H", "--", relative],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=True,
    )
    commit = result.stdout.strip()
    if not commit:
        raise AssertionError(f"no producer commit for {relative}")
    return commit


def git_bytes(commit: str, path: Path) -> bytes:
    relative = path.resolve().relative_to(REPO.resolve()).as_posix()
    return subprocess.run(
        ["git", "show", f"{commit}:{relative}"],
        cwd=REPO,
        capture_output=True,
        check=True,
    ).stdout


@contextmanager
def isolated_live_evidence_root():
    output_root = os.environ.get("IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT")
    with tempfile.TemporaryDirectory(prefix="iris-live-evidence-", dir=output_root) as value:
        isolated = Path(value) / ROOT.name
        shutil.copytree(ROOT, isolated)
        prefix = ROOT.relative_to(REPO)
        original_resolve, original_rel = live_common.resolve_repo, live_common.rel
        def resolve(path: str | Path) -> Path:
            candidate = Path(path)
            if candidate.is_absolute():
                return candidate.resolve()
            try:
                return (isolated / candidate.relative_to(prefix)).resolve()
            except ValueError:
                return original_resolve(path)
        def rel(path: str | Path) -> str:
            try:
                return (prefix / Path(path).resolve().relative_to(isolated.resolve())).as_posix()
            except ValueError:
                return original_rel(path)
        with mock.patch.multiple(live_common, EVIDENCE_ROOT=isolated, resolve_repo=resolve, rel=rel):
            yield


class LiveConsumerMigrationExecutionTest(unittest.TestCase):
    def test_phase1_reconciles_153_and_163_by_identity(self) -> None:
        report = load_json(ROOT / "phase1/migrated153_vs_sandbox163_reconciliation_report.json")
        disposition = load_json(ROOT / "phase1/reconciliation_set_difference_disposition.json")

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["migrated_count"], 153)
        self.assertEqual(report["sandbox_mutation_count"], 163)
        self.assertEqual(report["migrated153_minus_sandbox163_count"], 0)
        self.assertEqual(report["sandbox163_minus_migrated153_count"], 10)
        self.assertTrue(all(row["forbidden_for_live_mutation"] for row in disposition["sandbox163_minus_migrated153"]))

    def test_phase2_splits_verified_live_and_evidence_only_rows(self) -> None:
        summary = load_json(ROOT / "phase2/live_target_derivation_summary.json")
        excluded = load_jsonl(ROOT / "phase2/excluded_non_live_target_ledger.jsonl")
        required = load_jsonl(ROOT / "phase2/live_mutation_required_ledger.jsonl")

        self.assertEqual(summary["total_migrated_rows"], 153)
        self.assertEqual(summary["live_mutation_required_count"], 0)
        self.assertEqual(summary["excluded_non_live_target_count"], 44)
        self.assertEqual(summary["status_counts"]["live_verified_already"], 109)
        self.assertEqual(len(required), 0)
        self.assertEqual(len(excluded), 44)
        self.assertTrue(all(row["hard_forbidden_authority_surface"] for row in excluded))

    def test_phase3_allows_completion_when_live_rows_are_already_verified(self) -> None:
        pre_apply = load_json(ROOT / "phase3/pre_apply_gate_report.json")
        isolation = load_json(ROOT / "phase3/dirty_target_isolation_report.json")
        patch_bundle = load_json(ROOT / "phase3/frozen_patch_bundle.json")
        apply_ledger = load_jsonl(ROOT / "phase4/live_apply_ledger.jsonl")
        apply_integrity = load_json(ROOT / "phase4/apply_integrity_report.json")

        self.assertEqual(pre_apply["status"], "PASS")
        self.assertEqual(pre_apply["block_codes"], [])
        self.assertEqual(pre_apply["dirty_target_overlap_count"], 0)
        self.assertNotIn("blocked_anchor_drift", pre_apply["block_codes"])
        self.assertEqual(pre_apply["anchor_drift_row_count"], 0)
        self.assertEqual(isolation["dirty_target_overlap_count"], 0)
        self.assertTrue(patch_bundle["line_grouped_patch_bundle"])
        self.assertEqual(patch_bundle["authorization_row_count"], 0)
        self.assertEqual(patch_bundle["line_patch_count"], 0)
        self.assertEqual(apply_ledger, [])
        self.assertEqual(apply_integrity["status"], "NOT_APPLICABLE_NO_LIVE_DIFF_REQUIRED")
        self.assertIsNone(apply_integrity["block_reason"])

    def test_python_patch_materialization_uses_inline_comment_markers(self) -> None:
        row = {
            "path": "Iris/build/description/v2/tools/build/example.py",
            "row_identity_key": "ledger-f613f10e573175b7b39fa4ca00cd1d05",
            "sandbox_after_anchor": "VALUE = 2105 DVF_AUTHORITY_ROLE_MIGRATION[f613f10e573175b7b39fa4ca00cd1d05]",
            "expected_after_anchor": "VALUE = 2105 DVF_AUTHORITY_ROLE_MIGRATION[f613f10e573175b7b39fa4ca00cd1d05]",
        }

        materialized = materialize_line_patch("VALUE = 2105", [row])

        self.assertEqual(materialized["status"], "PASS")
        self.assertEqual(materialized["strategy"], "python_inline_comment_marker")
        self.assertEqual(
            materialized["after_anchor"],
            "VALUE = 2105  # DVF_AUTHORITY_ROLE_MIGRATION[f613f10e573175b7b39fa4ca00cd1d05]",
        )

    def test_phase5_and_closeout_preserve_complete_external_gate_status(self) -> None:
        separation = load_json(ROOT / "phase5/sandbox_live_separation_report.json")
        hard_forbidden = load_json(ROOT / "phase5/hard_forbidden_authority_surface_no_mutation_verdict.json")
        external_gate = load_json(ROOT / "phase7/completion_external_gate_readiness_report.json")
        final = load_json(ROOT / "phase8/final_live_migration_execution_report.json")
        closeout = (REPO / "docs/dvf_3_3_live_consumer_migration_execution_closeout.md").read_text(encoding="utf-8").lower()
        gate_statuses = {gate["gate"]: gate["status"] for gate in external_gate["gates"]}

        self.assertEqual(separation["readiness_sandbox_mutation_rows_counted_as_live_completion"], 0)
        self.assertEqual(hard_forbidden["hard_forbidden_authority_surface_changed_count"], 0)
        self.assertEqual(external_gate["status"], "SATISFIED")
        self.assertEqual(gate_statuses["independent_review"], "satisfied")
        self.assertEqual(gate_statuses["upstream_roadmap_seal"], "satisfied")
        self.assertEqual(external_gate["pending_external_gate_count"], 0)
        self.assertTrue(external_gate["completion_seal_allowed"])
        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["execution_evidence_status"], "PASS")
        self.assertTrue(final["complete_seal_allowed"])
        self.assertIsNone(final["completion_seal_block_reason"])
        self.assertEqual(final["completion_external_gate_status"], "SATISFIED")
        self.assertEqual(final["independent_review_status"], "satisfied")
        self.assertEqual(final["upstream_roadmap_seal_status"], "satisfied")
        self.assertEqual(final["final_status_counts"]["live_verified_already"], 109)
        self.assertFalse(final["sandbox_readiness_evidence_counted_as_live_completion"])
        self.assertIn("not counted as live completion", closeout)
        self.assertIn("external independent review and upstream roadmap seal are satisfied", closeout)
        self.assertIn("no current authority recutover", closeout)
        self.assertIn("no release readiness", closeout)

    def test_independent_review_hash_manifest_covers_external_docs_without_self_hash(self) -> None:
        manifest_path = SUCCESSOR_ROOT / "live_consumer_migration_hash_manifest.successor.json"
        report_path = SUCCESSOR_ROOT / "live_consumer_migration_hash_report.successor.json"
        producer_commit = git_last_change_commit(manifest_path)
        manifest = json.loads(git_bytes(producer_commit, manifest_path))
        report = json.loads(git_bytes(producer_commit, report_path))
        artifact_paths = {row["path"] for row in manifest["artifacts"]}
        expected_doc_paths = {
            "docs/dvf_3_3_live_consumer_migration_execution_closeout.md",
            "docs/dvf_3_3_live_consumer_migration_claim_boundary.md",
            "docs/dvf_3_3_live_consumer_migration_ledger_packet.md",
            "docs/DECISIONS.live_migration_execution.patch.md",
            "docs/ROADMAP.live_migration_execution.patch.md",
        }

        self.assertNotIn(
            "Iris/build/description/v2/staging/dvf_3_3_live_consumer_migration_execution/phase7/independent_review_artifact_hash_manifest.json",
            artifact_paths,
        )
        self.assertNotIn(
            "Iris/build/description/v2/staging/dvf_3_3_live_consumer_migration_execution/phase7/independent_review_artifact_hash_report.json",
            artifact_paths,
        )
        self.assertTrue(expected_doc_paths.issubset(artifact_paths))
        self.assertEqual(manifest["artifact_count"], len(manifest["artifacts"]))
        self.assertEqual(manifest["aggregate_sha256"], canonical_hash(manifest["artifacts"]))

        mismatches = []
        for record in manifest["artifacts"]:
            try:
                payload = git_bytes(producer_commit, REPO / record["path"])
            except subprocess.CalledProcessError:
                mismatches.append(record["path"])
                continue
            if len(payload) != record["bytes"]:
                mismatches.append(record["path"])
                continue
            if hashlib.sha256(payload).hexdigest() != record["sha256"]:
                mismatches.append(record["path"])

        self.assertEqual(mismatches, [])
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["external_review_gate_status"], "SATISFIED")
        self.assertEqual(report["checked_artifact_count"], len(manifest["artifacts"]))
        self.assertEqual(report["stable_artifact_hash_mismatch_count"], 0)

    def test_validator_accepts_complete_external_seal(self) -> None:
        with isolated_live_evidence_root():
            report, ok = validate_all(require_complete=False)
            complete_report, complete_ok = validate_all(require_complete=True, write_report=False)

        self.assertTrue(ok, report["errors"])
        self.assertTrue(complete_ok, complete_report["errors"])


if __name__ == "__main__":
    unittest.main()
