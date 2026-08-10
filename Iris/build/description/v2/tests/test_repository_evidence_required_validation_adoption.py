from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
PREDECESSOR = REPO / "Iris/_docs/refactor/repository_evidence_lightweighting/predecessor_subject_manifest.json"
POLICY = REPO / "Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json"
APPROVAL = REPO / "Iris/_docs/refactor/repository_evidence_lightweighting/owner_policy_approval.json"
ADOPTION = REPO / "Iris/_docs/refactor/repository_evidence_lightweighting/required_validation_adoption_receipt.json"
TAXONOMY = REPO / "Iris/_docs/round3/round3_test_taxonomy.json"
REQUIRED = REPO / "Iris/_docs/round3/current_route_required_validations.json"
FULL_GATE = REPO / "Iris/validation/clean_checkout/contracts/full_repository_gate.json"

TEST_IDS = (
    "test_repository_evidence_required_validation_adoption.RepositoryEvidenceRequiredValidationAdoptionTest.test_predecessor_subject_is_exact",
    "test_repository_evidence_required_validation_adoption.RepositoryEvidenceRequiredValidationAdoptionTest.test_successor_policy_owner_approval_and_representation_boundary_are_adopted",
    "test_repository_evidence_required_validation_adoption.RepositoryEvidenceRequiredValidationAdoptionTest.test_taxonomy_required_validation_and_full_gate_are_bound",
    "test_repository_evidence_required_validation_adoption.RepositoryEvidenceRequiredValidationAdoptionTest.test_durable_cas_roots_are_trackable_and_clean_checkout_available",
)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=check,
    )


def tracked_blob(relative: str, revision: str = "HEAD") -> str:
    return git("rev-parse", f"{revision}:{relative}").stdout.strip()


class RepositoryEvidenceRequiredValidationAdoptionTest(unittest.TestCase):
    def test_predecessor_subject_is_exact(self) -> None:
        manifest = load_json(PREDECESSOR)
        self.assertEqual(
            manifest["schema_version"],
            "iris_repository_evidence_lightweighting_predecessor_subject_v1",
        )
        subject = manifest["subject"]
        self.assertEqual(subject["commit"], "df498f95aa334bdf3a74167e900ca8a04a2550d6")
        self.assertEqual(subject["tree"], "da5e2447b8a8dcce392a4b8f22908f58cfc9d44d")
        self.assertFalse(subject["dirty_delta_allowed"])
        self.assertFalse(subject["base_plus_delta_fallback_allowed"])
        self.assertEqual(
            git("rev-parse", f"{subject['commit']}^{{tree}}").stdout.strip(),
            subject["tree"],
        )
        rows = manifest["predecessor_census"]["rows"]
        self.assertEqual(len(rows), 9)
        for row in rows:
            self.assertEqual(tracked_blob(row["path"], subject["commit"]), row["git_blob_id"])
        validation = manifest["c0_a_validation"]
        self.assertEqual(validation["status"], "PASS")
        self.assertEqual(len(validation["materializations"]), 2)
        self.assertTrue(all(row["exit_code"] == 0 for row in validation["materializations"]))

    def test_successor_policy_owner_approval_and_representation_boundary_are_adopted(self) -> None:
        policy = load_json(POLICY)
        approval = load_json(APPROVAL)
        self.assertEqual(
            policy["schema_version"],
            "iris_repository_evidence_lightweighting_output_policy_v1",
        )
        boundary = policy["authority_boundary"]
        self.assertEqual(boundary["cas_authority_class"], "raw_byte_representation_only")
        self.assertFalse(boundary["cas_is_source_authority"])
        self.assertFalse(boundary["cas_is_runtime_authority"])
        self.assertFalse(boundary["cas_is_semantic_authority"])
        self.assertEqual(
            approval["schema_version"],
            "iris_repository_evidence_lightweighting_owner_policy_approval_v1",
        )
        self.assertEqual(
            approval["policy"]["git_blob_id"],
            tracked_blob("Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json"),
        )
        self.assertEqual(approval["policy"]["raw_sha256"], sha256(POLICY))
        decisions = approval["decisions"]
        self.assertTrue(decisions["repository_local_cas_promotion_approved"])
        self.assertTrue(decisions["cold_store_backend_approved"])
        self.assertTrue(decisions["payload_deletion_authority_approved"])

    def test_taxonomy_required_validation_and_full_gate_are_bound(self) -> None:
        taxonomy = load_json(TAXONOMY)
        required = load_json(REQUIRED)
        gate = load_json(FULL_GATE)
        adoption = load_json(ADOPTION)
        taxonomy_rows = {row["test_id"]: row for row in taxonomy["rows"]}
        required_rows = {row["test_id"]: row for row in required["required_tests"]}
        for test_id in TEST_IDS:
            self.assertIn(test_id, taxonomy_rows)
            self.assertEqual(taxonomy_rows[test_id]["contract_class"], "current")
            self.assertEqual(taxonomy_rows[test_id]["state"], "ok")
            self.assertEqual(
                taxonomy_rows[test_id]["source_file"],
                "Iris/build/description/v2/tests/test_repository_evidence_required_validation_adoption.py",
            )
            self.assertIn(test_id, required_rows)
            self.assertTrue(required_rows[test_id]["required"])
        selection = gate["required_pytest_selection"]
        self.assertEqual(selection["taxonomy_path"], "Iris/_docs/round3/round3_test_taxonomy.json")
        self.assertEqual(selection["contract_class"], "current")
        self.assertEqual(selection["state"], "ok")
        self.assertEqual(
            adoption["schema_version"],
            "iris_repository_evidence_lightweighting_required_validation_adoption_v1",
        )
        for name, relative in adoption["bound_inputs"].items():
            revision = (
                "63ec5cb0a43834ff1d189cd09716defe4e4a54bf"
                if name
                in {
                    "adoption_test_source",
                    "gitattributes",
                    "gitignore",
                    "protected_surface_successor",
                    "required_validations",
                    "test_taxonomy",
                }
                else "HEAD"
            )
            self.assertEqual(relative["git_blob_id"], tracked_blob(relative["path"], revision), name)

    def test_durable_cas_roots_are_trackable_and_clean_checkout_available(self) -> None:
        policy = load_json(POLICY)
        allowed = policy["durable_repository_storage"]["allowed_roots"]
        self.assertEqual(
            allowed,
            [
                "Iris/build/description/v2/evidence/objects/sha256",
                "Iris/build/description/v2/evidence/references",
            ],
        )
        probes = (
            "Iris/build/description/v2/evidence/objects/sha256/aa/" + "a" * 64,
            "Iris/build/description/v2/evidence/references/bootstrap-probe.json",
        )
        for probe in probes:
            ignored = git("check-ignore", "--quiet", "--", probe, check=False)
            self.assertEqual(ignored.returncode, 1, probe)
        for relative in (
            "Iris/_docs/refactor/repository_evidence_lightweighting/predecessor_subject_manifest.json",
            "Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json",
            "Iris/_docs/refactor/repository_evidence_lightweighting/owner_policy_approval.json",
            "Iris/_docs/refactor/repository_evidence_lightweighting/required_validation_adoption_receipt.json",
        ):
            git("ls-files", "--error-unmatch", "--", relative)
            self.assertEqual(
                git("hash-object", f"--path={relative}", str(REPO / relative)).stdout.strip(),
                tracked_blob(relative),
            )


if __name__ == "__main__":
    unittest.main()
