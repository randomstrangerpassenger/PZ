from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
EVIDENCE = REPO / "Iris" / "_docs" / "refactor" / "residual_refactor"
TEST_IDS = {
    "test_iris_residual_runtime_acceptance.IrisResidualRuntimeAcceptanceTest.test_runtime_acceptance_harness_passes_all_registered_axes",
    "test_iris_residual_contract_surfaces.IrisResidualContractSurfacesTest.test_registered_surfaces_preserve_architecture_and_closeout_contracts",
    "test_iris_residual_python_import_matrix.IrisResidualPythonImportMatrixTest.test_direct_module_package_bare_import_and_bytes_match_contract",
    "test_iris_residual_diagnostic_disposition.IrisResidualDiagnosticDispositionTest.test_fingerprints_and_raw_exit_dispositions_fail_closed",
    "test_iris_residual_evidence_roles.IrisResidualEvidenceRolesTest.test_role_schema_index_and_manual_classes_are_fail_closed",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class IrisResidualContractSurfacesTest(unittest.TestCase):
    def test_registered_surfaces_preserve_architecture_and_closeout_contracts(self) -> None:
        taxonomy = load_json(REPO / "Iris/_docs/round3/round3_test_taxonomy.json")
        required = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")
        taxonomy_ids = {row["test_id"] for row in taxonomy["rows"]}
        required_ids = {row["test_id"] for row in required["required_tests"]}
        self.assertTrue(TEST_IDS.issubset(taxonomy_ids))
        self.assertTrue(TEST_IDS.issubset(required_ids))

        runtime_root = REPO / "Iris/media/lua/client/Iris"
        logic_sources = "\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in (runtime_root / "Logic").rglob("*.lua")
        )
        self.assertNotIn('require("Iris/UI/Browser', logic_sources)
        browser_sources = "\n".join(
            path.read_text(encoding="utf-8-sig")
            for path in (runtime_root / "UI/Browser").glob("*.lua")
        )
        self.assertEqual(
            browser_sources.count('require("Iris/Logic/CategoryPresentationOrder")'),
            1,
        )

        tooltip = (runtime_root / "UI/Tooltip/IrisAltTooltip.lua").read_text(encoding="utf-8-sig")
        self.assertNotRegex(tooltip, r"\bmaxLines\b")
        self.assertNotRegex(tooltip, r"#detailLines\s*[<>]=?\s*\d")
        self.assertNotRegex(tooltip, r"table\.remove\s*\(\s*detailLines")
        self.assertIn("tagStr:sub(1, 47)", tooltip)

        successor_path = REPO / "Iris/_docs/refactor/repository_runtime_lightweighting/protected_surface_successor_manifest.json"
        successor = load_json(successor_path)
        attestation = successor["historical_manifest_attestation"]
        with tempfile.TemporaryDirectory(prefix="iris-residual-surfaces-") as temp:
            external_evidence = Path(temp)
            for name in ("phase0_supported_api_manifest.json", "phase0_protected_surface_manifest.json"):
                shutil.copy2(EVIDENCE / name, external_evidence / name)
            completed = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(REPO / "Iris/test/validate_residual_refactor_surfaces.ps1"),
                    "-Mode",
                    "Closeout",
                    "-RepositoryRoot",
                    str(REPO),
                    "-EvidenceRoot",
                    str(external_evidence),
                ],
                cwd=REPO,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            supported = load_json(external_evidence / "final_supported_api_compatibility_report.json")
            protected = load_json(external_evidence / "final_protected_surface_report.json")
            package = load_json(external_evidence / "final_package_identity_report.json")
            claims = load_json(external_evidence / "final_claim_boundary_report.json")
            tampered_attestation_path = external_evidence / "tampered_historical_attestation.json"
            tampered_attestation_path.write_text(
                json.dumps({**attestation, "git_blob_id": "0" * 40}),
                encoding="utf-8",
            )
            tampered = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(REPO / "Iris/test/validate_residual_refactor_surfaces.ps1"),
                    "-Mode",
                    "AttestationProbe",
                    "-RepositoryRoot",
                    str(REPO),
                    "-EvidenceRoot",
                    str(external_evidence),
                    "-HistoricalManifestAttestationPath",
                    str(tampered_attestation_path),
                ],
                cwd=REPO,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(tampered.returncode, 0)
            self.assertIn(
                "repository lightweighting historical manifest attestation blob mismatch",
                tampered.stdout + tampered.stderr,
            )
        self.assertEqual(supported["validation_status"], "passed")
        self.assertEqual(supported["incompatible_count"], 0)
        self.assertEqual(supported["surface_count"], 20)
        self.assertEqual(protected["validation_status"], "passed")
        self.assertEqual(protected["unauthorized_changed_count"], 0)
        attested_blob = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", f"{attestation['commit']}:{attestation['path']}"],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        ).stdout.strip()
        anchor_tree = subprocess.run(
            ["git", "-C", str(REPO), "rev-parse", f"{successor['active_protection_anchor']['commit']}^{{tree}}"],
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=True,
        ).stdout.strip()
        self.assertEqual(
            successor["schema_version"],
            "iris_repository_runtime_lightweighting_protected_surface_successor_v2",
        )
        self.assertEqual(attestation["git_blob_id"], attested_blob)
        self.assertEqual(attestation["interpretation"], "embedded_identity_chain_only")
        self.assertEqual(successor["active_protection_anchor"]["tree"], anchor_tree)
        self.assertEqual(
            protected["repository_lightweighting_successor_manifest"],
            "Iris/_docs/refactor/repository_runtime_lightweighting/protected_surface_successor_manifest.json",
        )
        self.assertEqual(
            protected["repository_lightweighting_successor_schema_version"],
            "iris_repository_runtime_lightweighting_protected_surface_successor_v2",
        )
        self.assertEqual(
            protected["repository_evidence_lightweighting_successor_manifest"],
            "Iris/_docs/refactor/repository_evidence_lightweighting/protected_surface_successor_manifest.json",
        )
        self.assertEqual(
            protected["repository_evidence_lightweighting_successor_schema_version"],
            "iris_repository_evidence_lightweighting_protected_surface_successor_v1",
        )
        self.assertEqual(protected["historical_manifest_attestation"]["git_blob_id"], attested_blob)
        self.assertEqual(protected["historical_subject_object_dereference_count"], 0)
        self.assertTrue(protected["active_protection_anchor"]["final_state_verified"])
        self.assertEqual(
            protected["active_revision_ids"],
            [
                "tooling_track_v2_durable_protection_successor_v1",
                "tooling_track_adoption_checkpoint_v1",
                "repository_evidence_lightweighting_c0_c_bootstrap_v1",
                "repository_evidence_lightweighting_change1_cleanup_v1",
            ],
        )
        self.assertEqual(
            ["common_contract_initial_v1", "common_contract_followup_v1"],
            protected["repository_lightweighting_revision_ids"][:2],
        )
        self.assertEqual(package["validation_status"], "passed")
        self.assertTrue(package["source_candidate_identity_equal"])
        self.assertEqual(claims["validation_status"], "passed")
        self.assertIn("release readiness", claims["non_claims"])


if __name__ == "__main__":
    unittest.main()
