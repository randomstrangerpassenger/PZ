from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
PRODUCER = REPO / "Iris/validation/residual_refactor/report_artifact_lifecycle.py"
GIANT_RELATIVE = (
    "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round/phase2_inventory/allowed_occurrence_inventory.json",
    "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round/phase2_inventory/legacy_active_silent_occurrence_inventory.jsonl",
    "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round/phase3_adjudication/occurrence_adjudication_report.json",
    "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round/phase5_guard/current_surface_guard_report.json",
)


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout.strip()


def make_repo(root: Path, *, giants: bool) -> Path:
    repo = root / "checkout"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "iris-tests@example.invalid")
    git(repo, "config", "user.name", "Iris Tests")
    (repo / ".gitignore").write_text(
        "Iris/build/description/v2/staging/legacy_active_silent_current_surface_guard_round/\n",
        encoding="utf-8",
    )
    tracked = repo / "docs/contract.md"
    tracked.parent.mkdir(parents=True)
    tracked.write_text("current contract\n", encoding="utf-8")
    if giants:
        for index, relative in enumerate(GIANT_RELATIVE, start=1):
            path = repo / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((f"giant-{index}\n" * index).encode("utf-8"))
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture")
    return repo.resolve()


def run_inventory(repo: Path, output: Path, subject_kind: str = "physical_capacity_subject") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(PRODUCER),
            "--repo",
            str(repo),
            "--subject-kind",
            subject_kind,
            "--out",
            str(output / "artifact_role_manifest.jsonl"),
            "--summary-out",
            str(output / "baseline_inventory.json"),
            "--subject-receipt-out",
            str(output / "subject_receipt.json"),
        ],
        cwd=repo,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def manifest_rows(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def create_directory_reparse(link: Path, target: Path) -> None:
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                (
                    "& { param($link, $target) "
                    "New-Item -ItemType Junction -Path $link -Target $target "
                    "-ErrorAction Stop | Out-Null }"
                ),
                str(link),
                str(target),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise AssertionError(completed.stderr)
    else:
        link.symlink_to(target, target_is_directory=True)


class ArtifactLifecycleInventoryTest(unittest.TestCase):
    def test_junctions_are_held_without_external_traversal(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-lifecycle-reparse-") as temporary:
            root = Path(temporary)
            repo = make_repo(root, giants=True)
            external = root / "outside"
            external.mkdir()
            secret = external / "external-only-secret.txt"
            secret.write_text("must not enter census\n", encoding="utf-8")
            (external / ".tmp_tests").mkdir()
            (external / ".tmp_tests/also-external.txt").write_text(
                "must not be discovered\n", encoding="utf-8"
            )
            scanned_link = (
                repo / "Iris/build/description/v2/tests/junction-to-outside"
            )
            discovery_link = repo / "Iris/discovery-junction"
            create_directory_reparse(scanned_link, external)
            create_directory_reparse(discovery_link, external)

            output = root / "evidence"
            result = run_inventory(repo, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = manifest_rows(output / "artifact_role_manifest.jsonl")
            by_path = {str(row["path"]): row for row in rows}
            for relative in (
                "Iris/build/description/v2/tests/junction-to-outside",
                "Iris/discovery-junction",
            ):
                self.assertIn(relative, by_path)
                self.assertEqual(by_path[relative]["path_access"], "unreadable")
                self.assertEqual(
                    by_path[relative]["error_type"], "ReparseOrSymlinkHold"
                )
            self.assertFalse(
                any("external-only-secret.txt" in str(row["path"]) for row in rows)
            )
            self.assertFalse(
                any("also-external.txt" in str(row["path"]) for row in rows)
            )
            summary = json.loads(
                (output / "baseline_inventory.json").read_text(encoding="utf-8")
            )
            self.assertGreaterEqual(summary["unreadable_count"], 2)
            self.assertFalse(summary["complete_accounting"])

    def test_same_subject_is_byte_stable_and_role_partition_is_complete(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-lifecycle-") as temporary:
            root = Path(temporary)
            repo = make_repo(root, giants=True)
            first = root / "first"
            second = root / "second"
            first_result = run_inventory(repo, first)
            second_result = run_inventory(repo, second)
            self.assertEqual(first_result.returncode, 0, first_result.stderr)
            self.assertEqual(second_result.returncode, 0, second_result.stderr)
            self.assertEqual(
                (first / "artifact_role_manifest.jsonl").read_bytes(),
                (second / "artifact_role_manifest.jsonl").read_bytes(),
            )
            self.assertEqual(
                (first / "baseline_inventory.json").read_bytes(),
                (second / "baseline_inventory.json").read_bytes(),
            )
            summary = json.loads((first / "baseline_inventory.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["subject_kind"], "physical_capacity_subject")
            self.assertEqual(summary["physical_resolved_root"], repo.as_posix())
            self.assertEqual(sum(summary["role_partition_bytes"].values()), summary["physical_bytes"])
            self.assertEqual(summary["unclassified_count"], 0)
            self.assertEqual(summary["unreadable_count"], 0)
            self.assertFalse(summary["archive_delete_allowed"])

    def test_ignored_giants_exist_only_in_physical_denominator_with_exact_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-lifecycle-physical-") as physical_temp, tempfile.TemporaryDirectory(
            prefix="iris-lifecycle-validation-"
        ) as validation_temp:
            physical_root = Path(physical_temp)
            validation_root = Path(validation_temp)
            physical = make_repo(physical_root, giants=True)
            validation = make_repo(validation_root, giants=False)
            physical_out = physical_root / "evidence"
            validation_out = validation_root / "evidence"
            physical_result = run_inventory(physical, physical_out)
            validation_result = run_inventory(validation, validation_out, "validation_subject")
            self.assertEqual(physical_result.returncode, 0, physical_result.stderr)
            self.assertEqual(validation_result.returncode, 0, validation_result.stderr)

            physical_rows = {row["path"]: row for row in manifest_rows(physical_out / "artifact_role_manifest.jsonl")}
            validation_rows = {row["path"]: row for row in manifest_rows(validation_out / "artifact_role_manifest.jsonl")}
            for relative in GIANT_RELATIVE:
                self.assertIn(relative, physical_rows)
                self.assertNotIn(relative, validation_rows)
                row = physical_rows[relative]
                source = physical / relative
                self.assertEqual(row["vcs_state"], "ignored")
                self.assertEqual(row["size_bytes"], source.stat().st_size)
                self.assertEqual(row["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
                self.assertEqual(row["authority_role"], "diagnostic_only")
                self.assertFalse(row["delete_eligible"])
            receipt = json.loads((physical_out / "subject_receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["ignored_giant_count"], 4)
            self.assertEqual(receipt["physical_resolved_root"], physical.as_posix())
            self.assertEqual(receipt["manifest"]["sha256"], hashlib.sha256((physical_out / "artifact_role_manifest.jsonl").read_bytes()).hexdigest())

    def test_repository_local_and_preexisting_outputs_fail_loud(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-lifecycle-output-") as temporary:
            root = Path(temporary)
            repo = make_repo(root, giants=True)
            local = repo / "evidence"
            rejected = run_inventory(repo, local)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("must be outside repository", rejected.stderr)

            external = root / "external"
            external.mkdir()
            (external / "artifact_role_manifest.jsonl").write_text("occupied\n", encoding="utf-8")
            rejected_existing = run_inventory(repo, external)
            self.assertNotEqual(rejected_existing.returncode, 0)
            self.assertIn("output already exists", rejected_existing.stderr)

    def test_console_temp_cache_and_ignored_consumers_are_in_scope(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-lifecycle-scope-") as temporary:
            root = Path(temporary)
            repo = make_repo(root, giants=True)
            additions = {
                "console_log.txt": "console\n",
                ".tmp/owner-backup.txt": "backup\n",
                ".pytest_cache/state.txt": "cache\n",
                "Iris/example/__pycache__/module.pyc": "cache\n",
                "Iris/build/package/projection.txt": "package\n",
                "Iris/output/playtest.log": "output\n",
            }
            for relative, content in additions.items():
                path = repo / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            consumer = repo / "ignored_consumer.py"
            consumer.write_text(
                "from pathlib import Path\nPath('allowed_occurrence_inventory.json').read_text()\n",
                encoding="utf-8",
            )
            import_target = repo / "Iris/build/description/v2/staging/import_target.py"
            import_target.parent.mkdir(parents=True, exist_ok=True)
            import_target.write_text("VALUE = 1\n", encoding="utf-8")
            import_consumer = repo / "Iris/build/description/v2/tests/test_import_consumer.py"
            import_consumer.parent.mkdir(parents=True, exist_ok=True)
            import_consumer.write_text("import import_target\n", encoding="utf-8")
            with (repo / ".gitignore").open("a", encoding="utf-8") as handle:
                handle.write("ignored_consumer.py\n")
            git(repo, "add", ".gitignore")
            git(repo, "commit", "-m", "scope fixture")
            output = root / "evidence"
            result = run_inventory(repo, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = {row["path"]: row for row in manifest_rows(output / "artifact_role_manifest.jsonl")}
            for relative in additions:
                self.assertIn(relative, rows)
                self.assertNotEqual(rows[relative]["authority_role"], "unclassified")
            giant = rows[GIANT_RELATIVE[0]]
            self.assertIn("ignored_consumer.py", giant["direct_consumers"])
            self.assertIn("python_read", giant["consumer_axes"])
            self.assertFalse(giant["zero_live_consumers"])
            imported = rows["Iris/build/description/v2/staging/import_target.py"]
            self.assertIn(
                "Iris/build/description/v2/tests/test_import_consumer.py",
                imported["direct_consumers"],
            )
            self.assertIn("python_import", imported["consumer_axes"])
            self.assertFalse(imported["zero_live_consumers"])

    def test_missing_references_and_real_tracking_transition_are_fail_loud(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-lifecycle-transition-") as temporary:
            root = Path(temporary)
            repo = make_repo(root, giants=True)
            baseline_out = root / "baseline"
            baseline_result = run_inventory(repo, baseline_out)
            self.assertEqual(baseline_result.returncode, 0, baseline_result.stderr)
            baseline_rows = {
                row["path"]: row for row in manifest_rows(baseline_out / "artifact_role_manifest.jsonl")
            }
            self.assertEqual(baseline_rows["Iris/output"]["path_access"], "missing_referenced")

            addition = repo / "Iris/build/description/v2/staging/unapproved.txt"
            addition.parent.mkdir(parents=True, exist_ok=True)
            addition.write_text("new tracked artifact\n", encoding="utf-8")
            git(repo, "add", addition.relative_to(repo).as_posix())
            git(repo, "commit", "-m", "unapproved tracking change")
            terminal = root / "terminal"
            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(PRODUCER),
                    "--repo",
                    str(repo),
                    "--subject-kind",
                    "physical_capacity_subject",
                    "--baseline",
                    str(baseline_out / "baseline_inventory.json"),
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
            self.assertNotEqual(completed.returncode, 0)
            transition = json.loads((terminal / "transition.json").read_text(encoding="utf-8"))
            self.assertEqual(transition["status"], "FAIL")
            self.assertEqual(transition["unapproved_newly_tracked_count"], 1)
            self.assertEqual(
                transition["unapproved_newly_tracked_paths"],
                ["Iris/build/description/v2/staging/unapproved.txt"],
            )


if __name__ == "__main__":
    unittest.main()
