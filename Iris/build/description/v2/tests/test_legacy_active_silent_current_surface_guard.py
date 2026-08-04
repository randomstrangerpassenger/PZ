from __future__ import annotations

import hashlib
import json
from argparse import Namespace
import shutil
import subprocess
import sys
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FROZEN_REFERENCE_SHA256 = "f1d9e8715afe205d13e037bd31bbaf0a38f6803c3d92fea14bfb704a6f36f75a"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from clean_checkout_test_paths import external_test_path
from tools.build import build_legacy_active_silent_current_surface_guard_round as guard_builder
from tools.validate_legacy_active_silent_current_surface_guard import (
    ALLOWLIST_TOO_BROAD_ERROR_CODE,
    CURRENT_SURFACE_ERROR_CODE,
    DEFAULT_MANIFEST,
    DEFAULT_RUNTIME_STATE_ERROR_CODE,
    LEGACY_METRIC_RENDERED_ERROR_CODE,
    ScanBackendUnavailable,
    SUCCESSOR_OUTPUT_POLICY_RELATIVE,
    UNALLOWLISTED_ERROR_CODE,
    _atomic_store_object,
    _authorized_output_path,
    iter_scan_files,
    load_manifest,
    load_occurrence_stream,
    scan_path,
    validate_repo,
    validate_successor_output_policy,
    verify_occurrence_stream_reference,
    write_inventory_files,
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class LegacyActiveSilentCurrentSurfaceGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = external_test_path(
            "_tmp_legacy_active_silent_guard"
        )
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def manifest(self) -> dict:
        return {
            "round_root": "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round",
            "scan_surfaces": [
                {
                    "id": "current",
                    "role": "current_source",
                    "path_globs": [
                        "Iris/build/description/v2/data/**/*.jsonl",
                        "Iris/build/description/v2/output/**/*.json",
                        "Iris/media/lua/client/Iris/Data/**/*.lua",
                        "Iris/output/**/*.json",
                    ],
                },
                {
                    "id": "historical",
                    "role": "historical_substrate",
                    "path_globs": ["docs/**/*.md"],
                },
                {
                    "id": "diagnostic",
                    "role": "diagnostic_source",
                    "path_globs": ["Iris/build/description/v2/tools/**/*.py"],
                },
            ],
            "scan_exclusions": [
                {
                    "id": "round_output",
                    "role": "current_guard_run_output",
                    "path_globs": [
                        "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/**"
                    ],
                },
                {
                    "id": "report_staging",
                    "role": "report_only_staging_residue",
                    "path_globs": ["Iris/build/description/v2/staging/**"],
                },
            ],
            "hard_fail_surfaces": [
                {
                    "id": "writer",
                    "path_globs": ["Iris/build/description/v2/data/**/*.jsonl"],
                    "occurrence_kinds": ["runtime_state_value", "source_value", "writer_output_label_value"],
                },
                {
                    "id": "operator",
                    "path_globs": ["Iris/build/description/v2/output/**/*.json"],
                    "occurrence_kinds": ["operator_label_value", "current_report_label_value", "writer_output_label_value"],
                },
                {
                    "id": "lua",
                    "path_globs": ["Iris/media/lua/client/Iris/Data/**/*.lua"],
                    "occurrence_kinds": ["source_value"],
                },
            ],
            "allow_surfaces": [
                {
                    "id": "docs",
                    "path_globs": ["docs/Iris/**"],
                    "occurrence_kinds": ["historical_quote", "plain_text", "diagnostic_alias", "legacy_metric_key"],
                    "reason": "historical docs",
                    "must_not_be_current_output": True,
                },
                {
                    "id": "staging",
                    "path_globs": ["Iris/build/description/v2/staging/**"],
                    "occurrence_kinds": ["historical_quote", "plain_text", "diagnostic_alias", "legacy_metric_key"],
                    "reason": "diagnostic staging",
                    "must_not_be_current_output": True,
                },
                {
                    "id": "legacy_metrics",
                    "path_globs": ["Iris/output/**/*.json"],
                    "occurrence_kinds": ["legacy_metric_key", "plain_text"],
                    "reason": "legacy metric keys",
                    "must_not_be_current_output": True,
                },
            ],
        }

    def test_default_manifest_is_durable_role_scoped_successor(self) -> None:
        self.assertEqual(
            ROOT.parents[3]
            / "Iris/_docs/refactor/repository_runtime_lightweighting"
            / "current_surface_guard_successor_manifest.json",
            DEFAULT_MANIFEST,
        )
        manifest = load_manifest(DEFAULT_MANIFEST)
        roles = {surface["role"] for surface in manifest["scan_surfaces"]}
        self.assertEqual(
            {
                "current_source",
                "protected_runtime",
                "tests",
                "build_tool_source",
                "historical_substrate",
            },
            roles,
        )
        self.assertEqual(
            {
                "current_guard_run_output",
                "report_only_staging_residue",
                "cold_archive_payload",
            },
            {surface["role"] for surface in manifest["scan_exclusions"]},
        )
        attributes = subprocess.run(
            [
                "git",
                "check-attr",
                "text",
                "eol",
                "--",
                predecessor := (
                    "Iris/build/description/v2/staging/compose_contract_migration/"
                    "legacy_active_silent_current_surface_guard_round/phase1_manifest/"
                    "current_surface_guard_referent_manifest.json"
                ),
                "Iris/_docs/refactor/repository_runtime_lightweighting/receipt.json",
                "Iris/_docs/refactor/repository_runtime_lightweighting/manifest.jsonl",
                "Iris/_docs/round3/round3_test_taxonomy.json",
                "Iris/_docs/round3/current_route_required_validations.json",
            ],
            cwd=ROOT.parents[3],
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        for path in (
            predecessor,
            "Iris/_docs/refactor/repository_runtime_lightweighting/receipt.json",
            "Iris/_docs/refactor/repository_runtime_lightweighting/manifest.jsonl",
            "Iris/_docs/round3/round3_test_taxonomy.json",
            "Iris/_docs/round3/current_route_required_validations.json",
        ):
            self.assertIn(f"{path}: text: set", attributes)
            self.assertIn(f"{path}: eol: lf", attributes)

    def test_default_manifest_includes_docs_json_authority_and_excludes_guard_output(self) -> None:
        manifest = load_manifest(DEFAULT_MANIFEST)
        expected = {
            "Iris/_docs/round3/current_route_required_validations.json",
            "Iris/_docs/refactor/repository_runtime_lightweighting/governance_ledger.jsonl",
            "Iris/_docs/refactor/residual_refactor/diagnostic_advisory_dispositions.json",
        }
        for relative in expected:
            write_text(self.tmp_dir / relative, '{"operator_label":"active"}\n')
        write_text(
            self.tmp_dir
            / "Iris/build/description/v2/staging/compose_contract_migration"
            / "legacy_active_silent_current_surface_guard_round/phase5_guard/report.json",
            '{"current_report_label":"silent"}\n',
        )

        census = iter_scan_files(self.tmp_dir, manifest, scan_backend="python")

        self.assertEqual(
            expected,
            {path.relative_to(self.tmp_dir).as_posix() for path in census.files},
        )
        self.assertEqual(
            1,
            census.receipt["excluded_role_counts"]["current_guard_run_output"],
        )

    def test_producer_keeps_repository_and_sealed_predecessor_unchanged(self) -> None:
        predecessor = (
            ROOT
            / "staging/compose_contract_migration"
            / "legacy_active_silent_current_surface_guard_round/phase1_manifest"
            / "current_surface_guard_referent_manifest.json"
        )
        predecessor_sha256 = hashlib.sha256(predecessor.read_bytes()).hexdigest()
        status_before = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT.parents[3],
            text=True,
            capture_output=True,
            check=True,
        ).stdout
        run_root = external_test_path("_tmp_guard_producer_external_only")
        if run_root.exists():
            shutil.rmtree(run_root)
        work_root = run_root / "work"
        result_root = run_root / "result"
        work_root.mkdir(parents=True)
        result_root.mkdir()
        allocation_receipt = run_root / "allocation.json"
        allocation_receipt.write_text("{}\n", encoding="utf-8", newline="\n")

        digest = hashlib.sha256(b"").hexdigest()
        occurrence_reference = {
            "schema_version": "legacy-active-silent-occurrence-stream-reference-v1",
            "logical_id": "legacy-active-silent-current-surface-occurrences",
            "sha256": digest,
            "bytes": 0,
            "row_count": 0,
            "media_type": "application/x-ndjson",
            "producer_version": "legacy-active-silent-current-surface-guard-v1",
            "disposition_counts": {},
            "error_code_counts": {},
            "object": {
                "algorithm": "sha256",
                "relative_path": f"objects/sha256/{digest[:2]}/{digest}",
                "lifecycle_role": "retained_current_required",
            },
        }
        report = {
            "schema_version": "legacy-active-silent-current-surface-guard-report-v1",
            "status": "pass",
            "summary": {
                "occurrence_count": 0,
                "hard_fail_current_label_occurrence_count": 0,
                "unclassified_occurrence_count": 0,
                "allowed_occurrence_count": 0,
                "non_label_occurrence_count": 0,
                "covered_by_existing_guard_count": 0,
                "manifest_error_count": 0,
                "gate_a_pass": True,
            },
            "errors": [],
            "error_summary": {"count": 0, "code_counts": {}},
            "occurrence_stream": occurrence_reference,
            "scan_receipt": {"backend": "python", "denominator_count": 0},
        }

        def fake_validate_repo(*_args: object, **_kwargs: object) -> dict:
            object_path = result_root / occurrence_reference["object"]["relative_path"]
            object_path.parent.mkdir(parents=True, exist_ok=True)
            object_path.write_bytes(b"")
            return report

        arguments = Namespace(
            work_root=str(work_root),
            result_root=str(result_root),
            allocation_receipt=str(allocation_receipt),
            scan_backend="python",
            scan_timeout=60,
        )
        allocation = {
            "run_id": "0" * 32,
            "claim_id": "guard-producer-test",
            "attempt_id": "external-only",
            "allocation_profile": "checkpoint",
            "allocation_ledger": {"path": str(run_root / "ledger.jsonl")},
        }
        try:
            with (
                mock.patch.object(guard_builder, "parse_args", return_value=arguments),
                mock.patch.object(
                    guard_builder,
                    "load_and_validate_output_policy",
                    return_value={
                        "external_subroots": guard_builder.AUTHORIZED_RESULT_SUBROOTS,
                        "approval": "owner_approved",
                    },
                ),
                mock.patch.object(
                    guard_builder,
                    "load_and_validate_allocation_receipt",
                    return_value=allocation,
                ),
                mock.patch.object(guard_builder, "validate_repo", side_effect=fake_validate_repo),
            ):
                self.assertEqual(0, guard_builder.main())

            self.assertEqual(
                predecessor_sha256,
                hashlib.sha256(predecessor.read_bytes()).hexdigest(),
            )
            load_manifest(DEFAULT_MANIFEST)
            phase_root = (
                result_root
                / "phases/legacy_active_silent_current_surface_guard_round"
            )
            closeout = json.loads(
                (phase_root / "phase7_closeout/closeout.json").read_text(encoding="utf-8")
            )
            hard_gate = json.loads(
                (phase_root / "phase6_validation/phase6_hard_gate_report.json").read_text(
                    encoding="utf-8"
                )
            )
            producer_receipt = json.loads(
                (result_root / "logs/legacy_active_silent_guard_producer_receipt.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("implemented_pending_external_checkpoint", closeout["closeout_state"])
            self.assertEqual("pending_external_checkpoint", hard_gate["overall_status"])
            self.assertEqual(0, hard_gate["nested_native_process_count"])
            self.assertEqual("PENDING_EXTERNAL_CHECKPOINT", producer_receipt["status"])
            self.assertEqual("PASS", producer_receipt["execution_status"])
            self.assertEqual(
                "pending_external_checkpoint",
                producer_receipt["adoption_validation_status"],
            )
            status_after = subprocess.run(
                ["git", "status", "--porcelain=v1", "--untracked-files=all"],
                cwd=ROOT.parents[3],
                text=True,
                capture_output=True,
                check=True,
            ).stdout
            self.assertEqual(status_before, status_after)
        finally:
            if run_root.exists():
                shutil.rmtree(run_root)

    def test_positive_allowed_surfaces_and_non_label_words_pass(self) -> None:
        write_text(
            self.tmp_dir / "docs" / "Iris" / "history.md",
            "Historical active/silent text and a silent failure note stay quoted.\n",
        )
        write_text(
            self.tmp_dir / "Iris" / "output" / "layer3_stats.json",
            json.dumps({"active_count": 2084, "silent_count": 21}, indent=2),
        )
        write_text(
            self.tmp_dir / "Iris" / "build" / "description" / "v2" / "staging" / "round" / "report.json",
            json.dumps({"diagnostic_alias": "active/silent read-only legacy alias"}, indent=2),
        )
        write_text(
            self.tmp_dir / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "View.lua",
            "local activeView = true\n",
        )

        report = validate_repo(self.tmp_dir, self.manifest(), scan_backend="python")

        self.assertEqual(report["status"], "pass")
        self.assertTrue(report["summary"]["gate_a_pass"])

    def test_runtime_state_legacy_value_is_owned_by_existing_guard_only(self) -> None:
        write_text(
            self.tmp_dir / "Iris" / "build" / "description" / "v2" / "data" / "decisions.jsonl",
            '{"item_id":"Base.Legacy","state":"active"}\n',
        )

        report = validate_repo(self.tmp_dir, self.manifest(), scan_backend="python")
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(DEFAULT_RUNTIME_STATE_ERROR_CODE, codes)
        self.assertNotIn(CURRENT_SURFACE_ERROR_CODE, codes)

    def test_lua_source_silent_current_surface_fails_with_new_guard(self) -> None:
        write_text(
            self.tmp_dir / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks" / "Chunk001.lua",
            'return { ["source"] = "silent" }\n',
        )

        report = validate_repo(self.tmp_dir, self.manifest(), scan_backend="python")
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(CURRENT_SURFACE_ERROR_CODE, codes)

    def test_generated_operator_current_label_fails_with_new_guard(self) -> None:
        write_text(
            self.tmp_dir / "Iris" / "build" / "description" / "v2" / "output" / "operator_report.json",
            json.dumps({"current_report_label": "active"}, indent=2),
        )

        report = validate_repo(self.tmp_dir, self.manifest(), scan_backend="python")
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(CURRENT_SURFACE_ERROR_CODE, codes)

    def test_legacy_metric_key_rendered_as_current_label_fails(self) -> None:
        write_text(
            self.tmp_dir / "Iris" / "output" / "layer3_stats.json",
            json.dumps({"label": "active_count"}, indent=2),
        )

        report = validate_repo(self.tmp_dir, self.manifest(), scan_backend="python")
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(LEGACY_METRIC_RENDERED_ERROR_CODE, codes)

    def test_too_broad_allowlist_rule_fails(self) -> None:
        manifest = self.manifest()
        manifest["allow_surfaces"].append(
            {
                "id": "bad",
                "path_globs": ["Iris/**"],
                "occurrence_kinds": ["plain_text"],
                "reason": "too broad",
                "must_not_be_current_output": True,
            }
        )

        report = validate_repo(self.tmp_dir, manifest, scan_backend="python")
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(ALLOWLIST_TOO_BROAD_ERROR_CODE, codes)

    def test_allow_path_with_unapproved_current_occurrence_kind_fails(self) -> None:
        write_text(
            self.tmp_dir / "Iris" / "output" / "operator.json",
            '{"source":"active"}\n',
        )

        report = validate_repo(self.tmp_dir, self.manifest(), scan_backend="python")
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(UNALLOWLISTED_ERROR_CODE, codes)
        self.assertFalse(report["summary"]["gate_a_pass"])

    def test_allow_rule_cannot_admit_current_label_occurrence_kind(self) -> None:
        manifest = self.manifest()
        manifest["allow_surfaces"].append(
            {
                "id": "forged-current-allow",
                "path_globs": ["Iris/special/**/*.json"],
                "occurrence_kinds": ["source_value"],
                "reason": "forged narrow allow",
                "must_not_be_current_output": True,
            }
        )

        report = validate_repo(self.tmp_dir, manifest, scan_backend="python")
        codes = [error["code"] for error in report["errors"]]

        self.assertIn(ALLOWLIST_TOO_BROAD_ERROR_CODE, codes)

    def test_scan_surface_includes_current_historical_and_diagnostic_roles(self) -> None:
        current = self.tmp_dir / "Iris" / "build" / "description" / "v2" / "data" / "decisions.jsonl"
        historical = self.tmp_dir / "docs" / "Iris" / "history.md"
        diagnostic = self.tmp_dir / "Iris" / "build" / "description" / "v2" / "tools" / "probe.py"
        write_text(current, '{"state":"active"}\n')
        write_text(historical, "historical silent label\n")
        write_text(diagnostic, "# diagnostic active alias\n")

        census = iter_scan_files(self.tmp_dir, self.manifest(), scan_backend="python")

        self.assertEqual(
            [path.relative_to(self.tmp_dir).as_posix() for path in census.files],
            [
                "Iris/build/description/v2/data/decisions.jsonl",
                "Iris/build/description/v2/tools/probe.py",
                "docs/Iris/history.md",
            ],
        )

    def test_rg_and_python_backends_produce_identical_canonical_path_list(self) -> None:
        write_text(self.tmp_dir / "docs" / "Iris" / "history.md", "historical active label\n")
        write_text(
            self.tmp_dir / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "View.lua",
            "local silentView = true\n",
        )

        rg_census = iter_scan_files(self.tmp_dir, self.manifest(), scan_backend="rg")
        python_census = iter_scan_files(self.tmp_dir, self.manifest(), scan_backend="python")

        self.assertEqual(rg_census.receipt["canonical_path_list_sha256"], python_census.receipt["canonical_path_list_sha256"])
        self.assertEqual(rg_census.receipt["input_census_sha256"], python_census.receipt["input_census_sha256"])

    def test_old_full_payload_and_new_stream_verdict_parity_on_frozen_named_census(self) -> None:
        frozen_path = ROOT / "tests" / "fixtures" / "legacy_active_silent_guard_frozen_reference.json"
        frozen_bytes = frozen_path.read_bytes()
        self.assertEqual(hashlib.sha256(frozen_bytes).hexdigest(), FROZEN_REFERENCE_SHA256)
        frozen = json.loads(frozen_bytes.decode("utf-8"))
        write_text(self.tmp_dir / "docs" / "Iris" / "history.md", "Historical active alias.\n")
        write_text(
            self.tmp_dir / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "Current.lua",
            'return { ["source"] = "silent" }\n',
        )
        write_text(
            self.tmp_dir / "Iris" / "output" / "operator.json",
            '{"source":"active"}\n',
        )
        manifest = self.manifest()
        census = iter_scan_files(self.tmp_dir, manifest, scan_backend=frozen["backend"])
        legacy_occurrences = []
        for path in census.files:
            legacy_occurrences.extend(scan_path(path, self.tmp_dir, manifest))
        legacy_occurrences.sort(key=lambda item: (item.path, item.line, item.column, item.token))

        new_report = validate_repo(self.tmp_dir, manifest, scan_backend=frozen["backend"])

        self.assertEqual(
            [path.relative_to(self.tmp_dir).as_posix() for path in census.files],
            frozen["canonical_paths"],
        )
        self.assertEqual([item.as_dict() for item in legacy_occurrences], frozen["legacy_full_payload_occurrences"])
        self.assertEqual(new_report["scan_receipt"]["selected_backend"], frozen["backend"])
        self.assertEqual(new_report["scan_receipt"]["canonical_path_list_sha256"], census.receipt["canonical_path_list_sha256"])
        self.assertEqual(new_report["summary"], frozen["summary"])

    def test_rg_missing_timeout_and_abnormal_exit_fail_loud_without_fallback(self) -> None:
        with mock.patch(
            "tools.validate_legacy_active_silent_current_surface_guard.subprocess.run",
            side_effect=FileNotFoundError("rg missing"),
        ):
            with self.assertRaisesRegex(ScanBackendUnavailable, "scan_backend_unavailable.*missing"):
                iter_scan_files(self.tmp_dir, self.manifest(), scan_backend="rg")

        with mock.patch(
            "tools.validate_legacy_active_silent_current_surface_guard.subprocess.run",
            side_effect=subprocess.TimeoutExpired(["rg"], 60),
        ):
            with self.assertRaisesRegex(ScanBackendUnavailable, "scan_backend_unavailable.*timeout"):
                iter_scan_files(self.tmp_dir, self.manifest(), scan_backend="rg")

        abnormal = subprocess.CompletedProcess(["rg", "--version"], 7, stdout="", stderr="boom")
        with mock.patch(
            "tools.validate_legacy_active_silent_current_surface_guard.subprocess.run",
            return_value=abnormal,
        ):
            with self.assertRaisesRegex(ScanBackendUnavailable, "scan_backend_unavailable.*abnormal_exit"):
                iter_scan_files(self.tmp_dir, self.manifest(), scan_backend="rg")

    def test_report_only_and_round_owned_output_are_excluded(self) -> None:
        round_report = (
            self.tmp_dir
            / "Iris"
            / "build"
            / "description"
            / "v2"
            / "staging"
            / "compose_contract_migration"
            / "legacy_active_silent_current_surface_guard_round"
            / "phase5_guard"
            / "current_surface_guard_report.json"
        )
        write_text(round_report, '{"current_report_label":"active"}\n')
        write_text(
            self.tmp_dir / "Iris" / "build" / "description" / "v2" / "staging" / "other" / "report.json",
            '{"current_report_label":"silent"}\n',
        )

        census = iter_scan_files(self.tmp_dir, self.manifest(), scan_backend="python")

        self.assertEqual(census.files, ())
        self.assertEqual(census.receipt["excluded_role_counts"]["current_guard_run_output"], 1)
        self.assertEqual(census.receipt["excluded_role_counts"]["report_only_staging_residue"], 1)

    def test_single_canonical_stream_reference_integrity_and_missing_object_failure(self) -> None:
        write_text(self.tmp_dir / "docs" / "Iris" / "history.md", "historical active label\n")
        result_root = external_test_path("_tmp_legacy_active_silent_result")
        if result_root.exists():
            shutil.rmtree(result_root)
        result_root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(result_root, ignore_errors=True))

        report = validate_repo(
            self.tmp_dir,
            self.manifest(),
            scan_backend="python",
            result_root=result_root,
        )
        rows = load_occurrence_stream(report["occurrence_stream"], result_root)
        object_files = [path for path in result_root.rglob("*") if path.is_file()]

        self.assertEqual(len(rows), report["summary"]["occurrence_count"])
        self.assertEqual(len(object_files), 1)
        object_files[0].unlink()
        with self.assertRaises(FileNotFoundError):
            load_occurrence_stream(report["occurrence_stream"], result_root)

    def test_stream_count_and_phase_summary_tampering_fail_loud(self) -> None:
        write_text(self.tmp_dir / "docs" / "Iris" / "history.md", "historical active label\n")
        result_root = external_test_path("_tmp_legacy_active_silent_tamper_result")
        if result_root.exists():
            shutil.rmtree(result_root)
        result_root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(result_root, ignore_errors=True))
        report = validate_repo(
            self.tmp_dir,
            self.manifest(),
            scan_backend="python",
            result_root=result_root,
        )

        tampered_reference = json.loads(json.dumps(report["occurrence_stream"]))
        tampered_reference["disposition_counts"]["allowed"] = 999
        with self.assertRaisesRegex(ValueError, "disposition counts mismatch"):
            verify_occurrence_stream_reference(tampered_reference, result_root)

        tampered_report = json.loads(json.dumps(report))
        tampered_report["summary"]["occurrence_count"] += 1
        with self.assertRaisesRegex(ValueError, "summary mismatch: occurrence_count"):
            write_inventory_files(tampered_report, result_root / "phases", result_root)

    def test_persistent_output_path_rejects_checkout_and_result_root_escape(self) -> None:
        result_root = external_test_path("_tmp_legacy_active_silent_authorized_result")
        unrelated = external_test_path("_tmp_legacy_active_silent_unrelated")
        for path in (result_root, unrelated):
            if path.exists():
                shutil.rmtree(path)
            path.mkdir(parents=True)
            self.addCleanup(lambda target=path: shutil.rmtree(target, ignore_errors=True))

        with self.assertRaisesRegex(ValueError, "escapes authorized result root"):
            _authorized_output_path(result_root, self.tmp_dir / "report.json", allowed_subroots={"logs"})
        with self.assertRaisesRegex(ValueError, "escapes authorized result root"):
            _authorized_output_path(result_root, unrelated / "report.json", allowed_subroots={"logs"})
        authorized = _authorized_output_path(
            result_root,
            result_root / "logs" / "report.json",
            allowed_subroots={"logs"},
        )
        self.assertEqual(authorized, (result_root / "logs" / "report.json").resolve())

        repository_root = ROOT.parents[3]
        canonical_policy = repository_root / SUCCESSOR_OUTPUT_POLICY_RELATIVE
        validated_policy = validate_successor_output_policy(repository_root, canonical_policy)
        self.assertEqual(validated_policy["external_subroots"], ["objects", "phases", "logs", "package"])

        forged_repo = self.tmp_dir / "forged-policy-repo"
        forged_policy_path = forged_repo / SUCCESSOR_OUTPUT_POLICY_RELATIVE
        forged_policy_path.parent.mkdir(parents=True, exist_ok=True)
        forged_policy = json.loads(canonical_policy.read_text(encoding="utf-8"))
        forged_policy["external_subroots"] = ["objects", "logs"]
        forged_policy_path.write_text(json.dumps(forged_policy), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "external subroots mismatch"):
            validate_successor_output_policy(forged_repo, forged_policy_path)

    def test_consecutive_run_does_not_grow_census_or_occurrence_hash(self) -> None:
        write_text(self.tmp_dir / "docs" / "Iris" / "history.md", "historical active label\n")
        result_root = external_test_path("_tmp_legacy_active_silent_repeat_result")
        if result_root.exists():
            shutil.rmtree(result_root)
        result_root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(result_root, ignore_errors=True))

        first = validate_repo(
            self.tmp_dir,
            self.manifest(),
            scan_backend="python",
            result_root=result_root,
        )
        second = validate_repo(
            self.tmp_dir,
            self.manifest(),
            scan_backend="python",
            result_root=result_root,
        )

        self.assertEqual(first["scan_receipt"]["input_census_sha256"], second["scan_receipt"]["input_census_sha256"])
        self.assertEqual(first["occurrence_stream"]["sha256"], second["occurrence_stream"]["sha256"])
        self.assertEqual(len([path for path in result_root.rglob("*") if path.is_file()]), 1)

    def test_content_addressing_separates_changed_payload_and_isolates_two_runs(self) -> None:
        source = self.tmp_dir / "docs" / "Iris" / "history.md"
        write_text(source, "Historical active alias.\n")
        run_a = external_test_path("_tmp_legacy_active_silent_isolation_a")
        run_b = external_test_path("_tmp_legacy_active_silent_isolation_b")
        for path in (run_a, run_b):
            if path.exists():
                shutil.rmtree(path)
            path.mkdir(parents=True)
            self.addCleanup(lambda target=path: shutil.rmtree(target, ignore_errors=True))

        first_a = validate_repo(self.tmp_dir, self.manifest(), scan_backend="python", result_root=run_a)
        first_b = validate_repo(self.tmp_dir, self.manifest(), scan_backend="python", result_root=run_b)
        self.assertEqual(first_a["occurrence_stream"]["sha256"], first_b["occurrence_stream"]["sha256"])

        shutil.rmtree(run_a)
        self.assertEqual(
            len(load_occurrence_stream(first_b["occurrence_stream"], run_b)),
            first_b["summary"]["occurrence_count"],
        )

        write_text(source, "Historical silent alias.\n")
        changed_b = validate_repo(self.tmp_dir, self.manifest(), scan_backend="python", result_root=run_b)
        self.assertNotEqual(first_b["occurrence_stream"]["sha256"], changed_b["occurrence_stream"]["sha256"])
        self.assertEqual(len([path for path in run_b.rglob("*") if path.is_file()]), 2)

    def test_interrupted_object_write_leaves_no_canonical_object(self) -> None:
        result_root = external_test_path("_tmp_legacy_active_silent_interrupted_result")
        if result_root.exists():
            shutil.rmtree(result_root)
        result_root.mkdir(parents=True)
        self.addCleanup(lambda: shutil.rmtree(result_root, ignore_errors=True))

        with mock.patch(
            "tools.validate_legacy_active_silent_current_surface_guard.os.link",
            side_effect=OSError("injected interruption"),
        ):
            with self.assertRaisesRegex(OSError, "injected interruption"):
                _atomic_store_object(result_root, b'{"token":"active"}\n')

        self.assertEqual([path for path in result_root.rglob("*") if path.is_file()], [])


if __name__ == "__main__":
    unittest.main()
