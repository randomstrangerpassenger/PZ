from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
ALLOCATOR = REPO / "Iris/validation/clean_checkout/allocate_repository_runtime_lightweighting_roots.ps1"
V2_ROOT = REPO / "Iris/build/description/v2"
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.validate_legacy_active_silent_current_surface_guard import (
    validate_allocation_receipt,
    validate_external_run_roots,
)


def powershell() -> str:
    executable = shutil.which("powershell")
    if executable is None:
        raise AssertionError("Windows PowerShell 5.1 is required by the allocator contract")
    return executable


def create_junction(link: Path, target: Path) -> None:
    completed = subprocess.run(
        [
            powershell(),
            "-NoProfile",
            "-Command",
            "& { param($link, $target) New-Item -ItemType Junction -Path $link -Target $target -ErrorAction Stop | Out-Null }",
            str(link),
            str(target),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)


def allocate(
    protected: Path,
    external: Path,
    *,
    profile: str,
    attempt: str,
    run_id: str | None,
    receipt_name: str,
    failure_injection: str = "none",
) -> subprocess.CompletedProcess[str]:
    command = [
        powershell(),
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ALLOCATOR),
        "-ProtectedRepositoryRoots",
        str(protected),
        "-ClaimId",
        "work-root-fixture",
        "-AttemptId",
        attempt,
        "-AllocationProfile",
        profile,
        "-ExternalParent",
        str(external),
        "-AllocationLedger",
        str(external / "allocation-ledger.jsonl"),
        "-Out",
        str(external / receipt_name),
    ]
    if run_id is not None:
        command.extend(["-RunId", run_id])
    if failure_injection != "none":
        command.extend(["-TestFailureInjection", failure_injection])
    return subprocess.run(
        command,
        cwd=protected,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


class ArtifactWorkRootContractTest(unittest.TestCase):
    def test_omitted_run_id_records_cryptographic_generation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-work-root-generated-run-id-") as temporary:
            root = Path(temporary)
            protected = root / "checkout"
            external = root / "external"
            protected.mkdir()
            external.mkdir()
            result = allocate(
                protected,
                external,
                profile="checkpoint",
                attempt="generated",
                run_id=None,
                receipt_name="generated.json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads((external / "generated.json").read_text(encoding="utf-8-sig"))
            self.assertRegex(receipt["run_id"], r"^[0-9a-f]{32}$")
            self.assertEqual(receipt["run_id_source"], "cryptographic_guid_generated")

    def test_guard_producer_revalidates_allocator_and_ledger_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-guard-allocation-binding-") as temporary:
            root = Path(temporary)
            protected = root / "checkout"
            external = root / "external"
            protected.mkdir()
            external.mkdir()
            result = allocate(
                protected,
                external,
                profile="checkpoint",
                attempt="guard-binding",
                run_id="0" * 32,
                receipt_name="guard-binding.json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt_path = external / "guard-binding.json"
            receipt = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
            work_root = Path(receipt["roots"]["work"]).resolve()
            result_root = Path(receipt["roots"]["result"]).resolve()

            validated = validate_allocation_receipt(
                protected,
                receipt_path,
                work_root,
                result_root,
            )
            self.assertEqual(validated["run_id"], "0" * 32)

            receipt["claim_id"] = "forged-nonempty-claim"
            tampered_path = external / "tampered-allocation.json"
            tampered_path.write_text(json.dumps(receipt), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ledger entry does not bind receipt claim_id"):
                validate_allocation_receipt(
                    protected,
                    tampered_path,
                    work_root,
                    result_root,
                )

    def test_guard_producer_requires_external_disjoint_newly_empty_roots(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-guard-producer-roots-") as temporary:
            root = Path(temporary)
            repository = root / "checkout"
            repository.mkdir()
            nested_work = repository / "work"
            nested_work.mkdir()
            external_work = root / "work"
            external_result = root / "result"
            external_work.mkdir()
            external_result.mkdir()

            with self.assertRaisesRegex(ValueError, "external to the repository"):
                validate_external_run_roots(repository, nested_work, external_result)

            work, result = validate_external_run_roots(repository, external_work, external_result)
            self.assertEqual(work, external_work.resolve())
            self.assertEqual(result, external_result.resolve())

            (external_result / "residue.txt").write_text("occupied\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "empty at producer entry"):
                validate_external_run_roots(repository, external_work, external_result)

    def test_new_external_checkpoint_roots_are_disjoint_existing_and_empty(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-work-root-") as temporary:
            root = Path(temporary)
            protected = root / "checkout"
            external = root / "외부-결과"
            protected.mkdir()
            external.mkdir()
            result = allocate(
                protected,
                external,
                profile="checkpoint",
                attempt="accept",
                run_id="1" * 32,
                receipt_name="accept.json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            receipt = json.loads((external / "accept.json").read_text(encoding="utf-8-sig"))
            self.assertEqual(receipt["pre_create_existence"]["existing_count"], 0)
            self.assertEqual(receipt["ledger_reuse"]["match_count"], 0)
            self.assertEqual(receipt["post_create_empty"]["nonempty_count"], 0)
            ledger = receipt["allocation_ledger"]
            ledger_rows = [
                json.loads(line)
                for line in Path(ledger["path"]).read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual([row["state"] for row in ledger_rows], ["reserved", "committed"])
            self.assertEqual(
                ledger_rows[1]["reservation_entry_sha256"],
                ledger["reservation_entry_sha256"],
            )
            roots = [Path(path).resolve() for path in receipt["roots"].values()]
            self.assertEqual(len(roots), len(set(roots)))
            for allocated in roots:
                self.assertTrue(allocated.is_dir())
                self.assertFalse(any(allocated.iterdir()))
                self.assertNotIn(protected.resolve(), allocated.parents)

    def test_repository_nested_parent_and_preexisting_nonempty_candidate_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-work-root-reject-") as temporary:
            root = Path(temporary)
            protected = root / "checkout"
            protected.mkdir()
            nested = protected / "attempts"
            nested.mkdir()
            rejected_nested = allocate(
                protected,
                nested,
                profile="checkpoint",
                attempt="nested",
                run_id="2" * 32,
                receipt_name="nested.json",
            )
            self.assertNotEqual(rejected_nested.returncode, 0)
            self.assertIn("disjoint", rejected_nested.stderr)

            external = root / "external"
            external.mkdir()
            candidate = external / "checkpoint-work-root-fixture-nonempty-333333333333"
            candidate.mkdir()
            (candidate / "occupied.txt").write_text("occupied\n", encoding="utf-8")
            rejected_existing = allocate(
                protected,
                external,
                profile="checkpoint",
                attempt="nonempty",
                run_id="3" * 32,
                receipt_name="nonempty.json",
            )
            self.assertNotEqual(rejected_existing.returncode, 0)
            self.assertIn("existed before creation", rejected_existing.stderr)
            self.assertEqual((candidate / "occupied.txt").read_text(encoding="utf-8"), "occupied\n")

    def test_reparse_external_parent_alias_into_repository_is_rejected_without_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-work-root-reparse-") as temporary:
            root = Path(temporary)
            protected = root / "checkout"
            repository_target = protected / "junction-output-target"
            protected.mkdir()
            repository_target.mkdir()
            external_alias = root / "external-junction"
            create_junction(external_alias, repository_target)
            rejected = allocate(
                protected,
                external_alias,
                profile="checkpoint",
                attempt="junction",
                run_id="6" * 32,
                receipt_name="junction.json",
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("reparse point", rejected.stderr)
            self.assertFalse((external_alias / "junction.json").exists())
            self.assertFalse(any(repository_target.iterdir()))

    def test_reparse_ledger_leaf_into_repository_is_rejected_without_write(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-work-root-ledger-reparse-") as temporary:
            root = Path(temporary)
            protected = root / "checkout"
            external = root / "external"
            protected.mkdir()
            external.mkdir()
            target = protected / "protected-ledger-target"
            target.mkdir()
            sentinel = target / "owner.txt"
            sentinel.write_text("protected\n", encoding="utf-8")
            ledger_link = external / "allocation-ledger.jsonl"
            create_junction(ledger_link, target)
            rejected = allocate(
                protected,
                external,
                profile="checkpoint",
                attempt="ledger-link",
                run_id="7" * 32,
                receipt_name="ledger-link.json",
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("allocation ledger leaf is a reparse point", rejected.stderr)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "protected\n")
            self.assertTrue(ledger_link.is_junction())
            self.assertFalse((external / "ledger-link.json").exists())

    def test_deleted_prior_run_path_is_still_rejected_by_append_only_ledger(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-work-root-reuse-") as temporary:
            root = Path(temporary)
            protected = root / "checkout"
            external = root / "external"
            protected.mkdir()
            external.mkdir()
            first = allocate(
                protected,
                external,
                profile="physical-capacity",
                attempt="reuse",
                run_id="4" * 32,
                receipt_name="first.json",
            )
            self.assertEqual(first.returncode, 0, first.stderr)
            receipt = json.loads((external / "first.json").read_text(encoding="utf-8-sig"))
            shutil.rmtree(Path(receipt["base"]))
            second = allocate(
                protected,
                external,
                profile="physical-capacity",
                attempt="reuse",
                run_id="4" * 32,
                receipt_name="second.json",
            )
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("used by a prior attempt", second.stderr)
            self.assertFalse((external / "second.json").exists())

    def test_failed_after_reservation_cannot_reuse_candidate_after_cleanup(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-work-root-reservation-failure-") as temporary:
            root = Path(temporary)
            protected = root / "checkout"
            external = root / "external"
            protected.mkdir()
            external.mkdir()
            failed = allocate(
                protected,
                external,
                profile="physical-capacity",
                attempt="reserved-failure",
                run_id="5" * 32,
                receipt_name="failed.json",
                failure_injection="after-reservation",
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("injected failure after durable allocation reservation", failed.stderr)
            self.assertFalse((external / "failed.json").exists())
            candidate = external / "physical-capacity-work-root-fixture-reserved-failure-555555555555"
            self.assertFalse(candidate.exists())
            ledger_path = external / "allocation-ledger.jsonl"
            ledger_rows = [
                json.loads(line)
                for line in ledger_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            self.assertEqual(len(ledger_rows), 1)
            self.assertEqual(ledger_rows[0]["state"], "reserved")

            if candidate.exists():
                shutil.rmtree(candidate)
            replay = allocate(
                protected,
                external,
                profile="physical-capacity",
                attempt="reserved-failure",
                run_id="5" * 32,
                receipt_name="replay.json",
            )
            self.assertNotEqual(replay.returncode, 0)
            self.assertIn("used by a prior attempt", replay.stderr)
            self.assertFalse((external / "replay.json").exists())
            self.assertEqual(len(ledger_path.read_text(encoding="utf-8").splitlines()), 1)

    def test_terminal_run_profiles_are_disjoint_and_run_b_is_minimal(self) -> None:
        with tempfile.TemporaryDirectory(prefix="iris-work-root-terminal-") as temporary:
            root = Path(temporary)
            protected = root / "checkout"
            external = root / "external"
            protected.mkdir()
            external.mkdir()
            run_a = allocate(
                protected,
                external,
                profile="terminal-run-a",
                attempt="run-a",
                run_id="a" * 32,
                receipt_name="run-a.json",
            )
            run_b = allocate(
                protected,
                external,
                profile="terminal-run-b",
                attempt="run-b",
                run_id="b" * 32,
                receipt_name="run-b.json",
            )
            self.assertEqual(run_a.returncode, 0, run_a.stderr)
            self.assertEqual(run_b.returncode, 0, run_b.stderr)
            a = json.loads((external / "run-a.json").read_text(encoding="utf-8-sig"))
            b = json.loads((external / "run-b.json").read_text(encoding="utf-8-sig"))
            self.assertTrue(set(a["roots"].values()).isdisjoint(b["roots"].values()))
            self.assertEqual(set(b["roots"]), {"work", "result", "orchestration_result"})
            self.assertEqual(b["lifecycle_disposition"]["unused_axes"], "not_created")
            self.assertEqual(
                b["lifecycle_disposition"]["reason"], "not_required_for_run_b_profile"
            )
            self.assertTrue(b["lifecycle_disposition"]["empty_verified"])
            self.assertTrue(b["lifecycle_disposition"]["delete_eligible_after_closeout"])


if __name__ == "__main__":
    unittest.main()
