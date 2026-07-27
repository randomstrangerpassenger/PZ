from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.authority_phase11 import (
    OWNER_DECISIONS_SHA256,
    PHASE9_10_OUTPUT_REVIEW_SHA256,
    _materialize_authority_phase11_fixture,
    _phase11_payloads,
    _validate_owner_branch_decisions,
    _validate_phase11_external_implementation_review,
    _validate_phase9_10_output_review,
)
from tools.build.dvf_3_3_food_semantic.contracts import FoodSemanticError


ATTEMPT_ROOT = (
    V2_ROOT
    / "staging/dvf_3_3_food_semantic_facts_authority/"
    "attempts/attempt-0007"
)
AUTHORITY_ROOT = (
    ATTEMPT_ROOT
    / "post_implementation_authority/authority-execution-0002"
)


class FoodSemanticAuthorityPhase11Test(unittest.TestCase):
    def test_reviewed_phase9_10_output_gate_is_exact(self) -> None:
        review = _validate_phase9_10_output_review(
            REPO_ROOT,
            ATTEMPT_ROOT,
            AUTHORITY_ROOT,
        )
        self.assertEqual(review["verdict"], "PASS")
        self.assertEqual(
            PHASE9_10_OUTPUT_REVIEW_SHA256,
            (
                "d679374037286737867295bf6cbe5ea9"
                "f5a944cbc9e3ee3d1f7e13da9297b23b"
            ),
        )
        self.assertEqual(len(review["reviewed_artifacts"]), 18)

    def test_owner_D9_D12_branch_contract_is_exact(self) -> None:
        decisions, d9, d12 = _validate_owner_branch_decisions(REPO_ROOT)
        self.assertEqual(
            OWNER_DECISIONS_SHA256,
            (
                "3abf570cc58a791a729671c3731f524b"
                "75acb9ec8e5cd5f89afb4c6097e6213a"
            ),
        )
        self.assertEqual(decisions["record_status"], "approved")
        self.assertEqual(d9["selection_parameters"]["selected_branch"], "B")
        self.assertFalse(
            d9["selection_parameters"]["current_mutation_allowed"]
        )
        self.assertFalse(
            d12["selection_parameters"][
                "predecessor_current_reentry_allowed"
            ]
        )

    def test_public_gate_blocks_without_external_review(self) -> None:
        with tempfile.TemporaryDirectory(
            dir=AUTHORITY_ROOT
        ) as temp_dir:
            temp_authority = Path(temp_dir)
            with self.assertRaisesRegex(
                FoodSemanticError,
                "external implementation review is missing",
            ):
                _validate_phase11_external_implementation_review(
                    REPO_ROOT,
                    temp_authority,
                )

    def test_fixture_materializes_sealed_non_current_successor(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="p11-fixture-",
            dir=AUTHORITY_ROOT,
        ) as temp_dir:
            output = Path(temp_dir)
            result = _materialize_authority_phase11_fixture(
                REPO_ROOT,
                ATTEMPT_ROOT,
                AUTHORITY_ROOT,
                output,
            )
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["selected_branch"], "B")
            self.assertTrue(result["non_current"])
            self.assertEqual(result["target_member_count"], 317)
            self.assertEqual(result["approved_assertion_count"], 322)
            self.assertEqual(result["current_facts_mutation_count"], 0)
            self.assertEqual(result["current_manifest_mutation_count"], 0)
            self.assertFalse(
                result["registry_operational_cutover_executed"]
            )
            binding = json.loads(
                (output / "selected_successor_input_binding.json").read_text(
                    encoding="utf-8"
                )
            )
            receipt = json.loads(
                (output / "sealed_successor_receipt.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(binding["selected_branch"], "B")
            self.assertTrue(binding["only_authorized_phase12_input"])
            self.assertTrue(receipt["non_current"])
            self.assertEqual(receipt["registry_adoption_receipt_emitted_count"], 0)

    def test_fixture_is_idempotent_and_differing_rerun_fails_closed(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            prefix="p11-fixture-",
            dir=AUTHORITY_ROOT,
        ) as temp_dir:
            output = Path(temp_dir)
            first = _materialize_authority_phase11_fixture(
                REPO_ROOT,
                ATTEMPT_ROOT,
                AUTHORITY_ROOT,
                output,
            )
            before = {
                path.name: path.read_bytes()
                for path in output.iterdir()
                if path.is_file()
            }
            second = _materialize_authority_phase11_fixture(
                REPO_ROOT,
                ATTEMPT_ROOT,
                AUTHORITY_ROOT,
                output,
            )
            after = {
                path.name: path.read_bytes()
                for path in output.iterdir()
                if path.is_file()
            }
            self.assertEqual(first, second)
            self.assertEqual(before, after)
            tampered = output / "selected_successor_input_binding.json"
            tampered.write_bytes(tampered.read_bytes() + b" ")
            other_before = {
                name: payload
                for name, payload in after.items()
                if name != tampered.name
            }
            with self.assertRaisesRegex(
                FoodSemanticError,
                "write-once Phase 11 artifact already differs",
            ):
                _materialize_authority_phase11_fixture(
                    REPO_ROOT,
                    ATTEMPT_ROOT,
                    AUTHORITY_ROOT,
                    output,
                )
            other_after = {
                path.name: path.read_bytes()
                for path in output.iterdir()
                if path.is_file() and path.name != tampered.name
            }
            self.assertEqual(other_before, other_after)

    def test_output_sink_must_remain_phase11_authority_local(self) -> None:
        with tempfile.TemporaryDirectory(
            dir=ATTEMPT_ROOT
        ) as temp_dir:
            escaped = Path(temp_dir) / "phase11_successor-escaped"
            with self.assertRaisesRegex(
                FoodSemanticError,
                "authority-execution-local",
            ):
                _phase11_payloads(
                    REPO_ROOT,
                    ATTEMPT_ROOT,
                    AUTHORITY_ROOT,
                    escaped,
                )


if __name__ == "__main__":
    unittest.main()
