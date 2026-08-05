from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
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
