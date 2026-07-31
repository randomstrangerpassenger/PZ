from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest
from copy import deepcopy


REPO_ROOT = Path(__file__).resolve().parents[5]
VALIDATOR = (
    REPO_ROOT
    / "Iris"
    / "build"
    / "description"
    / "v2"
    / "tools"
    / "build"
    / "validate_public_text_quality_acceptance_official_0005.py"
)
TOOLS_ROOT = VALIDATOR.parent
PHASE7_V2_VALIDATOR = TOOLS_ROOT / (
    "validate_public_text_quality_acceptance_official_0005_phase7_v2.py"
)


def _phase7_module():
    if str(TOOLS_ROOT) not in sys.path:
        sys.path.insert(0, str(TOOLS_ROOT))
    import public_text_quality_acceptance as base
    import public_text_quality_acceptance_official_0005_phase7_v2 as phase7

    return base, phase7


def _sealed(payload: dict[str, object]) -> dict[str, object]:
    base, _ = _phase7_module()
    core = deepcopy(payload)
    return {**core, "freeze_hash": base.canonical_hash(core)}


class PublicTextQualityAcceptanceCurrentRouteTest(unittest.TestCase):
    @staticmethod
    def _v1_fixture() -> dict[str, object]:
        _, phase7 = _phase7_module()
        return _sealed(
            {
                "schema_version": phase7.SCHEMA_V1,
                "status": "PASS",
                "attempt_id": "attempt-0005-official",
                "g1_gate_manifest_sha256": phase7.legacy.G1_GATE_MANIFEST_SHA256,
                "g1_closeout_sha256": phase7.legacy.G1_CLOSEOUT_SHA256,
                "live_manifest_sha256": phase7.LIVE_SHA256,
                "evaluation_subject_disposition": "accepted",
                "claim_bearing_artifact_count": 0,
                "claim_bearing_artifacts": [],
                "implementation_path_count": 0,
                "implementation_paths": [],
            }
        )

    @staticmethod
    def _v2_fixture() -> dict[str, object]:
        _, phase7 = _phase7_module()
        return _sealed(
            {
                "schema_version": phase7.SCHEMA_V2,
                "status": "PASS",
                "attempt_id": "attempt-0005-official",
                "g1_validated_subject_commit": phase7.G1_SUBJECT_COMMIT,
                "g1_validated_subject_tree": phase7.G1_SUBJECT_TREE,
                "g1_gate_manifest_sha256": phase7.G1_GATE_SHA256,
                "g1_closeout_sha256": phase7.G1_CLOSEOUT_SHA256,
                "readoption_transaction_id": phase7.TRANSACTION_ID,
                "readoption_transaction_identity": phase7.TRANSACTION_IDENTITY,
                "readoption_transaction_contract_sha256": phase7.TRANSACTION_CONTRACT_SHA256,
                "owner_input_sha256": phase7.OWNER_INPUT_SHA256,
                "live_readoption_receipt_sha256": phase7.LIVE_RECEIPT_SHA256,
                "phase6_post_adoption_route_sha256": phase7.POST_ROUTE_SHA256,
                "live_manifest_sha256": phase7.LIVE_SHA256,
                "candidate_manifest_sha256": phase7.CANDIDATE_SHA256,
                "candidate_patch_sha256": phase7.PATCH_SHA256,
                "evaluation_subject_disposition": "accepted",
                "evaluation_subject_disposition_hash": phase7.DISPOSITION_SHA256,
                "protected_surface_mutation_count": 0,
                "runtime_lua_package_mutation_count": 0,
                "claim_bearing_artifact_count": 0,
                "claim_bearing_artifacts": [],
                "implementation_path_count": 0,
                "implementation_paths": [],
            }
        )

    def test_phase7_schema_dispatch_accepts_historical_v1_and_current_v2(self) -> None:
        _, phase7 = _phase7_module()
        historical = phase7.validate_freeze_document(self._v1_fixture())
        current = phase7.validate_freeze_document(self._v2_fixture())
        self.assertEqual(historical["schema_dispatch"], "historical_v1")
        self.assertEqual(current["schema_dispatch"], "current_v2_successor_0010")

    def test_phase7_schema_dispatch_rejects_unknown_and_malformed(self) -> None:
        base, phase7 = _phase7_module()
        unknown = self._v2_fixture()
        unknown["schema_version"] = "unknown-phase7-schema"
        unknown["freeze_hash"] = base.canonical_hash(
            {key: value for key, value in unknown.items() if key != "freeze_hash"}
        )
        with self.assertRaises(base.FoundationContractError):
            phase7.validate_freeze_document(unknown)
        malformed = self._v2_fixture()
        del malformed["claim_bearing_artifacts"]
        malformed["freeze_hash"] = base.canonical_hash(
            {key: value for key, value in malformed.items() if key != "freeze_hash"}
        )
        with self.assertRaises(base.FoundationContractError):
            phase7.validate_freeze_document(malformed)

    def test_phase7_schema_dispatch_rejects_successor_transaction_hash_mismatch(self) -> None:
        base, phase7 = _phase7_module()
        for field in (
            "g1_validated_subject_commit",
            "readoption_transaction_identity",
            "live_readoption_receipt_sha256",
        ):
            payload = self._v2_fixture()
            payload[field] = "0" * 64
            payload["freeze_hash"] = base.canonical_hash(
                {key: value for key, value in payload.items() if key != "freeze_hash"}
            )
            with self.subTest(field=field), self.assertRaises(
                base.FoundationContractError
            ):
                phase7.validate_freeze_document(payload)

    def test_phase7_freeze_document_replay_is_deterministic(self) -> None:
        base, phase7 = _phase7_module()
        first = self._v2_fixture()
        second = deepcopy(first)
        self.assertEqual(base.pretty_json_bytes(first), base.pretty_json_bytes(second))
        self.assertEqual(
            phase7.validate_freeze_document(first),
            phase7.validate_freeze_document(second),
        )

    def test_required_gate_runs_standalone_subprocess(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(VALIDATOR),
                "--attempt-id",
                "attempt-0005-official",
                "--required-gate",
                "--no-write",
            ],
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["qualified_disposition"], "accepted")
        self.assertFalse(payload["publish_boundary_pass_claimed"])
        self.assertFalse(payload["package_or_release_ready_claimed"])


if __name__ == "__main__":
    unittest.main()
