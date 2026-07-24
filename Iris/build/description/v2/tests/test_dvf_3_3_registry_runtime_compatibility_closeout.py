from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import dvf_3_3_registry_runtime_compatibility as rtc
from tools.build import dvf_3_3_registry_runtime_compatibility_closeout as closeout
from tools.build import run_dvf_3_3_registry_runtime_compatibility as runner


def binding() -> dict[str, str]:
    return {
        "pre_adoption_live_manifest_sha256": "1" * 64,
        "post_adoption_live_manifest_sha256": "2" * 64,
        "selected_durable_bundle_id": "3" * 64,
        "selected_bundle_manifest_sha256": "4" * 64,
        "adopted_row_identity": "registry_runtime_compatibility::bundle::live",
    }


def final_machine() -> dict[str, object]:
    return {
        "schema_version": "rtc-final-machine-report-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": "attempt-0008",
        "implementation_identity": "implementation-agent",
        **binding(),
    }


def review_payload() -> dict[str, object]:
    return {
        "schema_version": "rtc-independent-review-v1",
        "round_id": rtc.ROUND_ID,
        "attempt_id": "attempt-0008",
        "status": "PASS",
        "verdict": "PASS",
        "reviewer_identity": "independent-agent",
        "same_implementation_agent_or_session_identity": False,
        "eligibility": {
            "not_roadmap_author": True,
            "not_plan_author_or_coauthor": True,
            "not_implementation_author_or_coauthor": True,
            "not_owner_or_disposition_signer": True,
            "distinct_agent_and_session_identity": True,
        },
        "open_critical_finding_count": 0,
        "open_major_finding_count": 0,
        "unresolved_finding_count": 0,
        "artifacts_reviewed": [
            {"path": "required.json", "sha256": "5" * 64}
        ],
        "rerun_commands": [
            {"command": "uv run python -m unittest", "exit_code": 0, "status": "PASS"}
        ],
        **binding(),
    }


class RegistryRuntimeCompatibilityCloseoutTest(unittest.TestCase):
    def test_packet_role_contract_is_exactly_nine(self) -> None:
        self.assertEqual(len(closeout.NINE_PACKET_ROLES), 9)
        self.assertEqual(len(set(closeout.NINE_PACKET_ROLES)), 9)
        self.assertEqual(
            set(closeout.NINE_PACKET_ROLES),
            set(closeout.CLOSEOUT_ROLE_FILES),
        )

    def test_review_accepts_distinct_eligible_identity(self) -> None:
        review = review_payload()
        accepted = closeout.validate_independent_review_payload(
            review=review,
            final_machine=final_machine(),
            required_artifacts={"required.json": "5" * 64},
        )
        self.assertEqual(accepted["verdict"], "PASS")

    def test_review_rejects_implementation_identity(self) -> None:
        review = review_payload()
        review["reviewer_identity"] = "implementation-agent"
        with self.assertRaises(rtc.CompatibilityError) as caught:
            closeout.validate_independent_review_payload(
                review=review,
                final_machine=final_machine(),
                required_artifacts={"required.json": "5" * 64},
            )
        self.assertEqual(
            caught.exception.code,
            "closeout_independent_reviewer_identity_conflict",
        )

    def test_review_rejects_missing_artifact_hash(self) -> None:
        with self.assertRaises(rtc.CompatibilityError) as caught:
            closeout.validate_independent_review_payload(
                review=review_payload(),
                final_machine=final_machine(),
                required_artifacts={"other.json": "6" * 64},
            )
        self.assertEqual(
            caught.exception.code,
            "closeout_independent_review_coverage_incomplete",
        )

    def test_write_once_is_idempotent_but_rejects_changed_bytes(self) -> None:
        with tempfile.TemporaryDirectory(dir=V2_ROOT / "staging") as temporary:
            path = Path(temporary) / "record.json"
            closeout.write_json_idempotent(path, {"status": "PASS"})
            closeout.write_json_idempotent(path, {"status": "PASS"})
            with self.assertRaises(rtc.CompatibilityError) as caught:
                closeout.write_json_idempotent(path, {"status": "FAIL"})
            self.assertEqual(
                caught.exception.code,
                "closeout_write_once_conflict",
            )

    def test_live_selection_can_be_superseded_additively(self) -> None:
        before = {
            "schema_version": "required-v1",
            "required_artifacts": [{"path": "old.json", "checks": []}],
            "required_tests": [{"test_id": "old.test", "reason": "old"}],
            "registry_runtime_compatibility": {
                "schema_version": "rtc-live-required-selection-v1",
                "policy_lifecycle_state": "live_required_gate_adopted",
                "candidate_manifest_probe": False,
                "bundle_id": "old",
            },
        }
        after = copy.deepcopy(before)
        after["registry_runtime_compatibility"] = {
            "schema_version": "rtc-live-required-selection-v1",
            "policy_lifecycle_state": "live_required_gate_adopted",
            "candidate_manifest_probe": False,
            "bundle_id": "new",
        }
        after["required_artifacts"].append({"path": "new.json", "checks": []})
        result = runner.validate_additive_required_manifest(
            before=before,
            after=after,
        )
        self.assertEqual(result["replaced_selection_count"], 1)
        self.assertEqual(result["superseded_bundle_id"], "old")
        self.assertEqual(result["existing_artifact_removal_count"], 0)

    def test_live_selection_replacement_rejects_existing_row_change(self) -> None:
        before = {
            "required_artifacts": [{"path": "old.json", "checks": []}],
            "required_tests": [],
            "registry_runtime_compatibility": {
                "schema_version": "rtc-live-required-selection-v1",
                "policy_lifecycle_state": "live_required_gate_adopted",
                "candidate_manifest_probe": False,
                "bundle_id": "old",
            },
        }
        after = copy.deepcopy(before)
        after["required_artifacts"][0]["path"] = "changed.json"
        after["registry_runtime_compatibility"]["bundle_id"] = "new"
        with self.assertRaises(rtc.CompatibilityError) as caught:
            runner.validate_additive_required_manifest(
                before=before,
                after=after,
            )
        self.assertEqual(
            caught.exception.code,
            "live_required_manifest_non_additive_diff",
        )

    def test_governance_pending_is_not_terminal_failure(self) -> None:
        with self.assertRaises(rtc.CompatibilityError) as caught:
            runner.command_terminal_failure(
                SimpleNamespace(failure_stage="post_implementation_review")
            )
        self.assertEqual(
            caught.exception.code,
            "terminal_before_closeout_forbidden",
        )


if __name__ == "__main__":
    unittest.main()
