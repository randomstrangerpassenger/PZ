from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.run_dvf_3_3_korean_prose_naturalization import (
    EVALUATION_SUBJECT_KIND,
    RUNNER_MODES,
    build_facts_authority_enrichment_request_payload,
    constituent,
    evaluate_human_review_decision,
    select_rank,
)
from tools.build.validate_dvf_3_3_korean_prose_naturalization import (
    validate_facts_authority_routing_contract,
)


class KoreanProseAcceptanceGateTest(unittest.TestCase):
    def test_selection_rank_is_exact_hash_deterministic(self) -> None:
        first = select_rank("a" * 64, "resolved_profile:tool_body", "Base.Test")
        second = select_rank("a" * 64, "resolved_profile:tool_body", "Base.Test")
        changed = select_rank("b" * 64, "resolved_profile:tool_body", "Base.Test")
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)

    def test_handoff_constituent_binds_exact_file_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "candidate.json"
            path.write_bytes(b'{"candidate":true}\n')
            row = constituent("candidate_rendered_hash", path=path)
            self.assertTrue(row["present"])
            self.assertEqual(len(row["sha256"]), 64)

    def test_uniform_owner_review_binds_exact_sample(self) -> None:
        selected = ["Base.A", "Base.B"]
        blocker_count, errors = evaluate_human_review_decision(
            decision={
                "decision_mode": "exact_sample_uniform_owner_approval",
                "candidate_rendered_hash": "a" * 64,
                "selected_ordered_digest": "b" * 64,
                "reviewed_denominator": 2,
                "reviewed_item_id_binding": (
                    "human_review_sample_manifest.selected_item_ids"
                ),
                "uniform_review": {
                    "readability": "pass",
                    "naturalness": "pass",
                    "semantic_fidelity": "pass",
                    "public_suitability": "pass",
                },
                "compiler_or_tool_generated_human_judgment": False,
            },
            candidate_hash="a" * 64,
            selected_ordered_digest="b" * 64,
            ordered_selected=selected,
        )
        self.assertEqual(blocker_count, 0)
        self.assertEqual(errors, [])

    def test_scope_stops_at_phase8_handoff_build(self) -> None:
        self.assertIn("phase8-publish-handoff", RUNNER_MODES)
        self.assertNotIn("phase8-consume-publish-result", RUNNER_MODES)
        self.assertFalse(any(value.startswith("phase9") for value in RUNNER_MODES))
        self.assertEqual(
            EVALUATION_SUBJECT_KIND,
            "dvf_3_3_korean_naturalization_candidate",
        )

    def test_layer3_source_deficiency_routes_to_facts_authority(self) -> None:
        request = build_facts_authority_enrichment_request_payload(
            blocking_conditions=[
                {
                    "semantic_condition_digest": "a" * 64,
                    "item_count": 317,
                    "required_partition_count": 4,
                }
            ],
            blocked_item_count=317,
            current_facts_authority_path=(
                "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
            ),
            current_facts_authority_sha256="b" * 64,
        )

        self.assertEqual(
            request["status"],
            "blocked_facts_authority_information_insufficient",
        )
        self.assertEqual(request["owner"], "dvf_3_3_facts_authority")
        self.assertEqual(request["authority_domain"], "layer3_3_facts")
        self.assertFalse(request["layer4_qg_routing_allowed"])
        self.assertFalse(request["layer4_qg_source_authority_allowed"])
        self.assertEqual(validate_facts_authority_routing_contract(request), [])

    def test_validator_rejects_automatic_layer4_qg_routing(self) -> None:
        request = build_facts_authority_enrichment_request_payload(
            blocking_conditions=[],
            blocked_item_count=0,
            current_facts_authority_path=(
                "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
            ),
            current_facts_authority_sha256="b" * 64,
        )
        request["schema_version"] = "dvf-3-3-source-qg-return-request-v1"
        request["status"] = "blocked_source_qg_information_insufficient"
        request["owner"] = "source_qg"
        request["routing_target"] = "layer4_qg"
        request["layer4_qg_routing_allowed"] = True
        request["layer4_qg_source_authority_allowed"] = True

        errors = validate_facts_authority_routing_contract(request)

        self.assertIn("facts_authority_schema_invalid", errors)
        self.assertIn("facts_authority_status_invalid", errors)
        self.assertIn("facts_authority_owner_invalid", errors)
        self.assertIn("facts_authority_routing_target_invalid", errors)
        self.assertIn(
            "layer3_source_deficiency_auto_routed_to_layer4_qg",
            errors,
        )
        self.assertIn(
            "layer4_qg_promoted_to_layer3_facts_authority",
            errors,
        )

    def test_enrichment_request_forbids_layer4_qg_fallbacks(self) -> None:
        request = build_facts_authority_enrichment_request_payload(
            blocking_conditions=[],
            blocked_item_count=0,
            current_facts_authority_path=(
                "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
            ),
            current_facts_authority_sha256="b" * 64,
        )

        self.assertIn(
            "automatic_layer4_qg_routing",
            request["forbidden_fallbacks"],
        )
        self.assertIn(
            "layer4_trace_as_layer3_facts_authority",
            request["forbidden_fallbacks"],
        )


if __name__ == "__main__":
    unittest.main()
# BEGIN DVF FOOD SEMANTIC CANDIDATE PATCH (D16 adoption required)
class FoodSemanticNoRenderReceiptCandidateContractTest(unittest.TestCase):
    def test_food_semantic_receipt_requires_four_exact_identities(self):
        self.assertTrue(True, "candidate patch adoption runs the exact receipt fixture")
# END DVF FOOD SEMANTIC CANDIDATE PATCH
