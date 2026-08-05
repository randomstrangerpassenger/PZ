from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
PRODUCER = REPO / "Iris/validation/residual_refactor/report_artifact_lifecycle.py"
PROMOTER = REPO / "Iris/validation/residual_refactor/promote_artifact_lifecycle_evidence.py"
DURABLE_RELATIVE = Path("Iris/_docs/refactor/repository_runtime_lightweighting")
GIANT_RELATIVE = (
    "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase2_inventory/allowed_occurrence_inventory.json",
    "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase2_inventory/legacy_active_silent_occurrence_inventory.jsonl",
    "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase3_adjudication/occurrence_adjudication_report.json",
    "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/phase5_guard/current_surface_guard_report.json",
)


def git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def produce_physical_evidence(repo: Path, evidence: Path) -> None:
    produced = subprocess.run(
        [
            sys.executable,
            "-B",
            str(PRODUCER),
            "--repo",
            str(repo),
            "--subject-kind",
            "physical_capacity_subject",
            "--out",
            str(evidence / "artifact_role_manifest.jsonl"),
            "--summary-out",
            str(evidence / "baseline_inventory.json"),
            "--subject-receipt-out",
            str(evidence / "physical_subject_receipt.json"),
        ],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if produced.returncode != 0:
        raise AssertionError(produced.stderr)


def make_fixture(root: Path) -> tuple[Path, Path]:
    repo = root / "checkout"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "iris-tests@example.invalid")
    git(repo, "config", "user.name", "Iris Tests")
    source = repo / "docs/contract.md"
    source.parent.mkdir(parents=True)
    source.write_text("contract\n", encoding="utf-8")
    (repo / ".gitignore").write_text(
        "Iris/build/description/v2/staging/compose_contract_migration/legacy_active_silent_current_surface_guard_round/\n",
        encoding="utf-8",
    )
    for index, relative in enumerate(GIANT_RELATIVE, start=1):
        giant = repo / relative
        giant.parent.mkdir(parents=True, exist_ok=True)
        giant.write_text(f"giant-{index}\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture")
    evidence = root / "external-evidence"
    produce_physical_evidence(repo, evidence)
    return repo.resolve(), evidence.resolve()


def promote(repo: Path, evidence: Path, receipt_out: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(PROMOTER),
            "baseline",
            "--repo",
            str(repo),
            "--source-manifest",
            str(evidence / "artifact_role_manifest.jsonl"),
            "--source-summary",
            str(evidence / "baseline_inventory.json"),
            "--subject-receipt",
            str(evidence / "physical_subject_receipt.json"),
            "--destination-root",
            str(repo / DURABLE_RELATIVE),
            "--receipt-out",
            str(receipt_out),
        ],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def successor_argv(repo: Path, evidence: Path, receipt_out: Path) -> list[str]:
    durable = repo / DURABLE_RELATIVE
    return [
        sys.executable,
        "-B",
        str(PROMOTER),
        "baseline-successor",
        "--repo",
        str(repo),
        "--source-manifest",
        str(evidence / "artifact_role_manifest.jsonl"),
        "--source-summary",
        str(evidence / "baseline_inventory.json"),
        "--subject-receipt",
        str(evidence / "physical_subject_receipt.json"),
        "--predecessor-promotion-receipt",
        str(durable / "baseline_promotion_receipt.json"),
        "--destination-root",
        str(durable),
        "--receipt-out",
        str(receipt_out),
    ]


def successor_environment(injected_environment: dict[str, str] | None = None) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(injected_environment or {})
    if injected_environment:
        environment["IRIS_BASELINE_SUCCESSOR_TEST_AUTHORITY"] = (
            "artifact_lifecycle_promotion_fixture_v1"
        )
    return environment


def promote_successor(
    repo: Path,
    evidence: Path,
    receipt_out: Path,
    injected_environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        successor_argv(repo, evidence, receipt_out),
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=successor_environment(injected_environment),
        check=False,
    )


def make_successor_fixture(root: Path) -> tuple[Path, Path, dict[str, bytes]]:
    repo, evidence = make_fixture(root)
    initial_external = root / "operator/initial-baseline-promotion.json"
    initial = promote(repo, evidence, initial_external)
    if initial.returncode != 0:
        raise AssertionError(initial.stderr)
    git(repo, "add", ".")
    git(repo, "commit", "-m", "adopt initial baseline")
    durable = repo / DURABLE_RELATIVE
    predecessor = {
        name: (durable / name).read_bytes()
        for name in (
            "artifact_role_manifest.jsonl",
            "baseline_inventory.json",
            "baseline_promotion_receipt.json",
        )
    }
    successor_evidence = root / "successor-evidence"
    produce_physical_evidence(repo, successor_evidence)
    return repo, successor_evidence, predecessor


def successor_transaction_id(repo: Path, evidence: Path) -> str:
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD", "HEAD^{tree}"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    ).stdout.splitlines()
    durable = repo / DURABLE_RELATIVE
    subject = json.loads((evidence / "physical_subject_receipt.json").read_text(encoding="utf-8"))
    sources = {
        name: {
            "sha256": hashlib.sha256((evidence / name).read_bytes()).hexdigest(),
            "byte_length": (evidence / name).stat().st_size,
        }
        for name in ("artifact_role_manifest.jsonl", "baseline_inventory.json")
    }
    seed = {
        "predecessor_commit": head[0],
        "predecessor_tree": head[1],
        "predecessor_receipt_sha256": hashlib.sha256(
            (durable / "baseline_promotion_receipt.json").read_bytes()
        ).hexdigest(),
        "physical_run_identity": subject["run_identity"],
        "sources": sources,
    }
    encoded = (json.dumps(seed, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:32]


class ArtifactLifecyclePromotionTest(unittest.TestCase):
    def test_baseline_promotion_preserves_bytes_and_dual_receipt_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="b-") as temporary:
            root = Path(temporary)
            repo, evidence = make_fixture(root)
            external_receipt = root / "operator/baseline_promotion_receipt.json"
            result = promote(repo, evidence, external_receipt)
            self.assertEqual(result.returncode, 0, result.stderr)
            durable = repo / DURABLE_RELATIVE
            for name in ("artifact_role_manifest.jsonl", "baseline_inventory.json"):
                self.assertEqual((evidence / name).read_bytes(), (durable / name).read_bytes())
            durable_receipt = durable / "baseline_promotion_receipt.json"
            self.assertEqual(durable_receipt.read_bytes(), external_receipt.read_bytes())
            payload = json.loads(durable_receipt.read_text(encoding="utf-8"))
            self.assertTrue(payload["byte_identity_verified"])
            self.assertEqual(payload["physical_subject"]["physical_resolved_root"], repo.as_posix())
            for row in payload["promoted_files"]:
                self.assertEqual(row["source_sha256"], row["destination_sha256"])
                self.assertEqual(
                    row["source_sha256"],
                    hashlib.sha256(Path(row["destination_path"]).read_bytes()).hexdigest(),
                )

    def test_altered_source_and_wrong_subject_are_rejected_before_durable_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="a-") as temporary:
            root = Path(temporary)
            repo, evidence = make_fixture(root)
            (evidence / "artifact_role_manifest.jsonl").write_bytes(
                (evidence / "artifact_role_manifest.jsonl").read_bytes() + b"{}\n"
            )
            result = promote(repo, evidence, root / "operator/receipt.json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source hash differs", result.stderr)
            self.assertFalse((repo / DURABLE_RELATIVE).exists())

        with tempfile.TemporaryDirectory(prefix="s-") as temporary:
            root = Path(temporary)
            repo, evidence = make_fixture(root)
            receipt_path = evidence / "physical_subject_receipt.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            receipt["subject_kind"] = "validation_subject"
            receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
            result = promote(repo, evidence, root / "operator/receipt.json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("requires physical_capacity_subject", result.stderr)
            self.assertFalse((repo / DURABLE_RELATIVE).exists())

    def test_preexisting_destination_blocks_all_promotion_outputs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="e-") as temporary:
            root = Path(temporary)
            repo, evidence = make_fixture(root)
            durable = repo / DURABLE_RELATIVE
            durable.mkdir(parents=True)
            existing = durable / "baseline_inventory.json"
            existing.write_text("owner bytes\n", encoding="utf-8")
            result = promote(repo, evidence, root / "operator/receipt.json")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(existing.read_text(encoding="utf-8"), "owner bytes\n")
            self.assertFalse((durable / "artifact_role_manifest.jsonl").exists())
            self.assertFalse((durable / "baseline_promotion_receipt.json").exists())

    def test_baseline_successor_replaces_generation_and_preserves_dual_receipt_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="n-") as temporary:
            root = Path(temporary)
            repo, evidence, predecessor = make_successor_fixture(root)
            durable = repo / DURABLE_RELATIVE
            external = root / "operator/successor-baseline-promotion.json"
            result = promote_successor(repo, evidence, external)
            self.assertEqual(result.returncode, 0, result.stderr)
            for name in ("artifact_role_manifest.jsonl", "baseline_inventory.json"):
                self.assertEqual((evidence / name).read_bytes(), (durable / name).read_bytes())
                self.assertNotEqual(predecessor[name], (durable / name).read_bytes())
            receipt = durable / "baseline_promotion_receipt.json"
            self.assertEqual(receipt.read_bytes(), external.read_bytes())
            payload = json.loads(receipt.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schema_version"],
                "iris_repository_runtime_lightweighting_baseline_promotion_v2",
            )
            self.assertEqual(payload["mode"], "baseline")
            self.assertEqual(payload["promotion_strategy"], "successor_transaction")
            self.assertFalse(payload["transaction"]["filesystem_group_atomicity_claimed"])
            self.assertTrue(payload["transaction"]["final_all_new_verified"])
            self.assertFalse(list(durable.glob(".baseline-successor*")))

    def test_baseline_successor_rejects_predecessor_head_mismatch_before_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m-") as temporary:
            root = Path(temporary)
            repo, evidence, _ = make_successor_fixture(root)
            durable = repo / DURABLE_RELATIVE
            baseline = durable / "baseline_inventory.json"
            baseline.write_bytes(baseline.read_bytes() + b" ")
            before = {
                name: (durable / name).read_bytes()
                for name in (
                    "artifact_role_manifest.jsonl",
                    "baseline_inventory.json",
                    "baseline_promotion_receipt.json",
                )
            }
            external = root / "operator/rejected-successor.json"
            result = promote_successor(repo, evidence, external)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("canonical predecessor differs from HEAD", result.stderr)
            for name, expected in before.items():
                self.assertEqual(expected, (durable / name).read_bytes())
            self.assertFalse(external.exists())
            self.assertFalse(list(durable.glob(".baseline-successor*")))

    def test_baseline_successor_rolls_back_after_each_controlled_replace_failure(self) -> None:
        for replace_index in (1, 2, 3):
            with self.subTest(replace_index=replace_index), tempfile.TemporaryDirectory(
                prefix=f"f{replace_index}-"
            ) as temporary:
                root = Path(temporary)
                repo, evidence, predecessor = make_successor_fixture(root)
                durable = repo / DURABLE_RELATIVE
                external = root / "operator/failed-successor.json"
                result = promote_successor(
                    repo,
                    evidence,
                    external,
                    {"IRIS_BASELINE_SUCCESSOR_FAIL_AFTER_REPLACE": str(replace_index)},
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    f"injected baseline successor failure after replace {replace_index}",
                    result.stderr,
                )
                for name, expected in predecessor.items():
                    self.assertEqual(expected, (durable / name).read_bytes())
                self.assertFalse(external.exists())
                self.assertFalse(list(durable.glob(".baseline-successor*")))

    def test_baseline_successor_recovers_interrupted_transaction_before_fresh_rerun(self) -> None:
        with tempfile.TemporaryDirectory(prefix="c-") as temporary:
            root = Path(temporary)
            repo, evidence, predecessor = make_successor_fixture(root)
            durable = repo / DURABLE_RELATIVE
            external = root / "operator/crashed-successor.json"
            crashed = promote_successor(
                repo,
                evidence,
                external,
                {"IRIS_BASELINE_SUCCESSOR_CRASH_AFTER_REPLACE": "2"},
            )
            self.assertEqual(crashed.returncode, 86, crashed.stderr)
            self.assertTrue(list(durable.glob(".baseline-successor-*.journal.json")))

            recovered = promote_successor(repo, evidence, external)
            self.assertNotEqual(recovered.returncode, 0)
            self.assertIn("recovered interrupted baseline successor transaction", recovered.stderr)
            for name, expected in predecessor.items():
                self.assertEqual(expected, (durable / name).read_bytes())
            self.assertFalse(external.exists())
            self.assertFalse(list(durable.glob(".baseline-successor*")))

            rerun = promote_successor(repo, evidence, external)
            self.assertEqual(rerun.returncode, 0, rerun.stderr)
            self.assertEqual(
                external.read_bytes(),
                (durable / "baseline_promotion_receipt.json").read_bytes(),
            )
            self.assertFalse(list(durable.glob(".baseline-successor*")))

    def test_baseline_successor_rejects_concurrent_active_owner(self) -> None:
        with tempfile.TemporaryDirectory(prefix="l-") as temporary:
            root = Path(temporary)
            repo, evidence, _ = make_successor_fixture(root)
            durable = repo / DURABLE_RELATIVE
            external = root / "operator/concurrent-successor.json"
            pause = root / "operator/active-transaction.ready"
            process = subprocess.Popen(
                successor_argv(repo, evidence, external),
                cwd=repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=successor_environment(
                    {"IRIS_BASELINE_SUCCESSOR_PAUSE_AFTER_JOURNAL": str(pause)}
                ),
            )
            try:
                deadline = time.monotonic() + 10.0
                while not pause.is_file() and process.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(pause.is_file(), "first successor did not acquire its transaction lock")
                competing = promote_successor(repo, evidence, external)
                self.assertNotEqual(competing.returncode, 0)
                self.assertIn("currently active", competing.stderr)
                pause.with_name(f"{pause.name}.release").write_text("release\n", encoding="utf-8")
                stdout, stderr = process.communicate(timeout=15)
                self.assertEqual(process.returncode, 0, stderr or stdout)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.communicate()
            self.assertEqual(
                external.read_bytes(),
                (durable / "baseline_promotion_receipt.json").read_bytes(),
            )
            self.assertFalse(list(durable.glob(".baseline-successor*")))

    def test_baseline_successor_recovers_crash_after_external_publication(self) -> None:
        with tempfile.TemporaryDirectory(prefix="x-") as temporary:
            root = Path(temporary)
            repo, evidence, predecessor = make_successor_fixture(root)
            durable = repo / DURABLE_RELATIVE
            external = root / "operator/published-crash-successor.json"
            crashed = promote_successor(
                repo,
                evidence,
                external,
                {"IRIS_BASELINE_SUCCESSOR_CRASH_AFTER_EXTERNAL_PUBLISH": "1"},
            )
            self.assertEqual(crashed.returncode, 84, crashed.stderr)
            self.assertTrue(external.is_file())
            recovered = promote_successor(repo, evidence, external)
            self.assertNotEqual(recovered.returncode, 0)
            self.assertIn("recovered interrupted baseline successor transaction", recovered.stderr)
            for name, expected in predecessor.items():
                self.assertEqual(expected, (durable / name).read_bytes())
            self.assertFalse(external.exists())
            self.assertFalse(list(durable.glob(".baseline-successor*")))
            rerun = promote_successor(repo, evidence, external)
            self.assertEqual(rerun.returncode, 0, rerun.stderr)

    def test_baseline_successor_recovers_lock_only_and_preparing_backup_crashes(self) -> None:
        cases = (
            ("IRIS_BASELINE_SUCCESSOR_CRASH_AFTER_LOCK", "1", 87, True),
            ("IRIS_BASELINE_SUCCESSOR_CRASH_AFTER_JOURNAL_TEMP", "1", 83, True),
            ("IRIS_BASELINE_SUCCESSOR_CRASH_AFTER_BACKUP", "2", 85, False),
        )
        for variable, value, exit_code, direct_rerun in cases:
            with self.subTest(variable=variable), tempfile.TemporaryDirectory(
                prefix="r-"
            ) as temporary:
                root = Path(temporary)
                repo, evidence, predecessor = make_successor_fixture(root)
                durable = repo / DURABLE_RELATIVE
                external = root / "operator/recovered-successor.json"
                crashed = promote_successor(repo, evidence, external, {variable: value})
                self.assertEqual(crashed.returncode, exit_code, crashed.stderr)
                recovered = promote_successor(repo, evidence, external)
                if direct_rerun:
                    self.assertEqual(recovered.returncode, 0, recovered.stderr)
                else:
                    self.assertNotEqual(recovered.returncode, 0)
                    self.assertIn("recovered interrupted baseline successor transaction", recovered.stderr)
                    for name, expected in predecessor.items():
                        self.assertEqual(expected, (durable / name).read_bytes())
                    recovered = promote_successor(repo, evidence, external)
                    self.assertEqual(recovered.returncode, 0, recovered.stderr)
                self.assertFalse(list(durable.glob(".baseline-successor*")))

    def test_baseline_successor_external_collision_rolls_back_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory(prefix="o-") as temporary:
            root = Path(temporary)
            repo, evidence, predecessor = make_successor_fixture(root)
            durable = repo / DURABLE_RELATIVE
            external = root / "operator/collision-successor.json"
            result = promote_successor(
                repo,
                evidence,
                external,
                {"IRIS_BASELINE_SUCCESSOR_CREATE_EXTERNAL_COLLISION": "1"},
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("operator receipt appeared during transaction", result.stderr)
            self.assertEqual(external.read_bytes(), b"test-owner-collision\n")
            for name, expected in predecessor.items():
                self.assertEqual(expected, (durable / name).read_bytes())
            self.assertFalse(list(durable.glob(".baseline-successor*")))

    def test_baseline_successor_preexisting_external_stage_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory(prefix="p-") as temporary:
            root = Path(temporary)
            repo, evidence, predecessor = make_successor_fixture(root)
            durable = repo / DURABLE_RELATIVE
            external = root / "operator/stage-collision-successor.json"
            transaction_id = successor_transaction_id(repo, evidence)
            external_stage = external.with_name(f".{external.name}.{transaction_id}.stage")
            external_stage.parent.mkdir(parents=True, exist_ok=True)
            external_stage.write_bytes(b"owner-stage-bytes\n")
            result = promote_successor(repo, evidence, external)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("operator receipt stage already exists", result.stderr)
            self.assertEqual(external_stage.read_bytes(), b"owner-stage-bytes\n")
            for name, expected in predecessor.items():
                self.assertEqual(expected, (durable / name).read_bytes())
            self.assertFalse(external.exists())
            self.assertFalse(list(durable.glob(".baseline-successor*")))

    def test_baseline_successor_committed_cleanup_recovery_requires_exact_intent(self) -> None:
        with tempfile.TemporaryDirectory(prefix="k-") as temporary:
            root = Path(temporary)
            repo, evidence, predecessor = make_successor_fixture(root)
            durable = repo / DURABLE_RELATIVE
            external = root / "operator/committed-successor.json"
            committed = promote_successor(
                repo,
                evidence,
                external,
                {"IRIS_BASELINE_SUCCESSOR_FAIL_COMMITTED_CLEANUP": "1"},
            )
            self.assertNotEqual(committed.returncode, 0)
            self.assertIn("committed baseline successor cleanup failure", committed.stderr)
            for name, old_bytes in predecessor.items():
                self.assertNotEqual(old_bytes, (durable / name).read_bytes())
            self.assertTrue(list(durable.glob(".baseline-successor-*.journal.json")))

            wrong_external = root / "operator/wrong-successor.json"
            mismatched = promote_successor(repo, evidence, wrong_external)
            self.assertNotEqual(mismatched.returncode, 0)
            self.assertIn("command intent differs", mismatched.stderr)
            self.assertFalse(wrong_external.exists())
            self.assertTrue(list(durable.glob(".baseline-successor-*.journal.json")))

            recovered = promote_successor(repo, evidence, external)
            self.assertEqual(recovered.returncode, 0, recovered.stderr)
            self.assertIn("recovered_committed_transaction", recovered.stdout)
            self.assertEqual(
                external.read_bytes(),
                (durable / "baseline_promotion_receipt.json").read_bytes(),
            )
            self.assertFalse(list(durable.glob(".baseline-successor*")))

    def test_baseline_successor_v2_transaction_semantics_are_mandatory(self) -> None:
        with tempfile.TemporaryDirectory(prefix="v-") as temporary:
            root = Path(temporary)
            repo, evidence, _ = make_successor_fixture(root)
            durable = repo / DURABLE_RELATIVE
            external = root / "operator/v2-successor.json"
            result = promote_successor(repo, evidence, external)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(external.read_text(encoding="utf-8"))
            payload["transaction"].pop("predecessor_files")
            tampered = root / "operator/tampered-v2.json"
            tampered.write_text(json.dumps(payload), encoding="utf-8")
            validator = (
                "import json,sys; from pathlib import Path; "
                "sys.path.insert(0, sys.argv[1]); "
                "from promote_artifact_lifecycle_evidence import validate_baseline_promotion_payload; "
                "validate_baseline_promotion_payload(Path(sys.argv[2]), Path(sys.argv[3]), "
                "json.loads(Path(sys.argv[4]).read_text(encoding='utf-8')))"
            )
            validated = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    "-c",
                    validator,
                    str(PROMOTER.parent),
                    str(repo),
                    str(durable),
                    str(tampered),
                ],
                cwd=repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertNotEqual(validated.returncode, 0)
            self.assertIn("predecessor file set is invalid", validated.stderr)

    def test_terminal_promotion_rejects_semantically_tampered_transition(self) -> None:
        with tempfile.TemporaryDirectory(prefix="t-") as temporary:
            root = Path(temporary)
            repo, evidence = make_fixture(root)
            baseline_external = root / "operator/baseline-promotion.json"
            baseline_result = promote(repo, evidence, baseline_external)
            self.assertEqual(baseline_result.returncode, 0, baseline_result.stderr)
            git(repo, "add", ".")
            git(repo, "commit", "-m", "adopt baseline")
            durable = repo / DURABLE_RELATIVE
            terminal = root / "terminal"
            produced = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(PRODUCER),
                    "--repo",
                    str(repo),
                    "--subject-kind",
                    "physical_capacity_subject",
                    "--baseline",
                    str(durable / "baseline_inventory.json"),
                    "--out",
                    str(terminal / "manifest.jsonl"),
                    "--summary-out",
                    str(terminal / "summary.json"),
                    "--subject-receipt-out",
                    str(terminal / "subject.json"),
                    "--tracking-transition-out",
                    str(terminal / "transition.json"),
                ],
                cwd=repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(produced.returncode, 0, produced.stderr)
            transition_path = terminal / "transition.json"
            transition = json.loads(transition_path.read_text(encoding="utf-8"))
            transition["physical_byte_delta"] += 1
            transition_path.write_text(
                json.dumps(transition, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(PROMOTER),
                    "terminal",
                    "--repo",
                    str(repo),
                    "--baseline-promotion-receipt",
                    str(durable / "baseline_promotion_receipt.json"),
                    "--source-manifest",
                    str(terminal / "manifest.jsonl"),
                    "--source-summary",
                    str(terminal / "summary.json"),
                    "--source-transition",
                    str(transition_path),
                    "--destination-root",
                    str(durable),
                    "--receipt-out",
                    str(root / "operator/terminal-promotion.json"),
                ],
                cwd=repo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("semantic validation failed", result.stderr)
            self.assertFalse((durable / "final_inventory.json").exists())


if __name__ == "__main__":
    unittest.main()
