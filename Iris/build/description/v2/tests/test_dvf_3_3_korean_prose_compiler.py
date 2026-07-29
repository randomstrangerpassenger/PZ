from __future__ import annotations

import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.compose_layer3_identity import (
    apply_identity_zero_anaphora,
    build_candidate_lead_context,
    naturalize_source_fragment,
    render_candidate_lead,
    select_candidate_lead_realization,
)
from tools.build.compose_layer3_body_profile import (
    build_candidate_body_plan_requirements,
)
from tools.build.compose_layer3_item import compose_item_candidate


class KoreanProseCompilerTest(unittest.TestCase):
    def test_food_rule_uses_structured_semantics_deterministically(self) -> None:
        context = {
            "resolved_profile": "consumable_body",
            "item_family": "food_consumption",
            "identity_semantic_key": "identity-key",
            "use_semantic_key": "use-key",
            "role_combination": ["identity", "use"],
        }
        first = select_candidate_lead_realization(
            identity_text="식품",
            use_text="조리나 식사 준비 작업에서 먹거나 나눠 먹을 때 쓴다",
            lead_context=context,
        )
        second = select_candidate_lead_realization(
            identity_text="식품",
            use_text="조리나 식사 준비 작업에서 먹거나 나눠 먹을 때 쓴다",
            lead_context=context,
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first[0],
            "조리하거나 식사를 준비할 때 먹고 나눌 수 있는 식품이다.",
        )
        self.assertEqual(
            first[2],
            "candidate_lead_food_consumption_nominal_v1",
        )

    def test_semantic_use_categories_choose_distinct_general_rules(self) -> None:
        cooking = select_candidate_lead_realization(
            identity_text="조리 용기",
            use_text="조리 준비 작업에서 재료를 담거나 섞고 익히기 전에 다룰 때 쓴다",
            lead_context={"resolved_profile": "tool_body"},
        )
        vehicle = select_candidate_lead_realization(
            identity_text="트렁크 모듈",
            use_text="차량 정비 작업에서 좌석이나 적재 모듈을 분리하거나 다시 끼울 때 다룬다",
            lead_context={"resolved_profile": "material_body"},
        )
        self.assertEqual(
            cooking[0],
            "재료를 담거나 섞고 익히기 전에 다루는 조리 용기다.",
        )
        self.assertEqual(
            vehicle[0],
            "차량을 정비하며 좌석이나 적재 모듈을 분리하거나 다시 끼울 때 다루는 트렁크 모듈이다.",
        )
        self.assertNotEqual(cooking[2], vehicle[2])

    def test_lead_context_excludes_item_id_and_binds_source_metadata(self) -> None:
        context = build_candidate_lead_context(
            facts={
                "item_id": "Base.Test",
                "slot_meta": {
                    "interaction_cluster": {
                        "selected_cluster": "food_consumption",
                    }
                },
            },
            resolved_profile="consumable_body",
            identity_row={
                "semantic_key": "identity-key",
                "source_field": "facts.identity_hint",
                "fact_origin": ["seed"],
                "role": "identity",
            },
            use_row={
                "semantic_key": "use-key",
                "source_field": "facts.primary_use",
                "fact_origin": ["cluster_summary"],
                "role": "use",
            },
            proposition_rows=[
                {"role": "identity"},
                {"role": "use"},
            ],
        )
        self.assertNotIn("item_id", context)
        self.assertEqual(context["item_family"], "food_consumption")
        self.assertEqual(context["use_source_field"], "facts.primary_use")
        self.assertEqual(context["use_fact_origin"], ["cluster_summary"])

    def test_source_absent_profile_role_uses_owner_approved_exclusion(self) -> None:
        requirements = build_candidate_body_plan_requirements(
            item_id="Base.Test",
            profile_name="tool_body",
            profile_spec={
                "section_order": [
                    "use_core",
                    "context_support",
                    "limitation_tail",
                ],
                "required_sections": [
                    "use_core",
                    "context_support",
                    "limitation_tail",
                ],
                "optional_sections": [],
            },
            proposition_rows=[
                {
                    "role": "use",
                    "proposition_id": "Base.Test#use",
                    "source_value": "응급 처치에 쓰는 도구다",
                }
            ],
            emission_eligible=True,
            applicability_rule_id="source_bound_profile_role_applicability_v1",
            applicability_approval_sha256="a" * 64,
        )
        by_role = {row["role"]: row for row in requirements}
        self.assertTrue(by_role["context"]["profile_required"])
        self.assertTrue(by_role["context"]["required"])
        self.assertTrue(by_role["context"]["derived_context_available"])
        self.assertTrue(by_role["limitation"]["profile_required"])
        self.assertFalse(by_role["limitation"]["required"])
        self.assertTrue(by_role["limitation"]["optional"])
        self.assertTrue(by_role["limitation"]["owner_approved_exclusion"])
        self.assertEqual(
            by_role["limitation"]["candidate_applicability"],
            "owner_approved_source_absence_exclusion",
        )
        self.assertEqual(by_role["limitation"]["applicable_proposition_ids"], [])

    def test_generic_lexical_naturalization_preserves_source_work_lexeme(
        self,
    ) -> None:
        reviewer_regressions = {
            "Base.Hammer": "작업 차량에서 발견된다",
            "Base.Crowbar": "근접 전투나 작업과 작업 차량에 쓴다",
            "Base.MetalPipe": "금속 작업 장소에서 발견된다",
            "Base.Shovel2": "흙 작업과 작업 차량에 쓴다",
            "Radio.RadioBlack": "전자 작업을 지원한다",
            "Radio.WalkieTalkie2": "전자 작업에 쓴다",
            "Radio.TvBlack": "전자 작업에서 쓴다",
            "Base.WoodenMallet": "근접 전투나 작업에 함께 쓰는 도구다",
            "Base.ClubHammer": "근접 전투나 작업에 함께 쓰는 도구다",
            "Base.GardenHoe": "재배와 흙 작업을 지원한다",
            "Base.CordlessPhone": "전자 작업에서 기기를 다룬다",
            "Base.Corkscrew": "주방 작업에서 식기를 다룬다",
            "Base.PlateOrange": "주방 작업을 지원한다",
        }
        self.assertEqual(len(reviewer_regressions), 13)
        for item_id, source in reviewer_regressions.items():
            with self.subTest(item_id=item_id):
                text, transformations = naturalize_source_fragment(source)
                self.assertEqual(text, source)
                self.assertNotIn("과정", text)
                self.assertEqual(transformations, [])

    def test_generic_lexical_naturalization_preserves_workplace_noun(self) -> None:
        text, transformations = naturalize_source_fragment(
            "공사 자재 보관 장소와 작업장에서 발견된다"
        )
        self.assertEqual(text, "공사 자재 보관 장소와 작업장에서 발견된다")
        self.assertEqual(transformations, [])

    def test_generic_lexical_naturalization_rewrites_passive_terminal(self) -> None:
        text, transformations = naturalize_source_fragment(
            "응급 처치에 사용된다"
        )
        self.assertEqual(text, "응급 처치에 쓴다")
        self.assertEqual(transformations, ["lexical_surface_naturalization"])

    def test_candidate_lead_uses_zero_anaphora_when_identity_is_present(self) -> None:
        text, transformations = render_candidate_lead(
            identity_text="탄약",
            use_text="탄약 주조에 쓰는 틀이다",
        )
        self.assertEqual(text, "탄약 주조에 쓰는 틀이다.")
        self.assertIn("pronoun_or_zero_anaphora", transformations)

    def test_followup_clause_uses_identity_zero_anaphora(self) -> None:
        text, applied = apply_identity_zero_anaphora(
            text="탄약을 상자에 담아 얻는다",
            identity_text="탄약",
            antecedent_text="장전 과정에서 탄약을 다룬다.",
        )
        self.assertTrue(applied)
        self.assertEqual(text, "상자에 담아 얻는다")

    def test_candidate_composer_emits_trace_without_item_override(self) -> None:
        propositions = [
            {
                "item_id": "Base.Test",
                "proposition_id": "Base.Test#identity",
                "role": "identity",
                "source_path": "facts.jsonl",
                "source_field": "facts.identity_hint",
                "source_value": "도구",
                "semantic_key": "identity-key",
                "qualifier": "none",
                "condition": "none",
                "modality": "asserted",
            },
            {
                "item_id": "Base.Test",
                "proposition_id": "Base.Test#use",
                "role": "use",
                "source_path": "facts.jsonl",
                "source_field": "facts.primary_use",
                "source_value": "수리에 쓰는 도구다",
                "semantic_key": "use-key",
                "qualifier": "none",
                "condition": "none",
                "modality": "asserted",
            },
        ]
        requirements = [
            {
                "item_id": "Base.Test",
                "requirement_id": "Base.Test#identity_core",
                "resolved_profile": "tool_body",
                "section_name": "identity_core",
                "role": "identity",
                "required": True,
                "optional": False,
                "ordering_index": 0,
                "applicable_proposition_ids": ["Base.Test#identity"],
                "emission_eligible": True,
            },
            {
                "item_id": "Base.Test",
                "requirement_id": "Base.Test#use_core",
                "resolved_profile": "tool_body",
                "section_name": "use_core",
                "role": "use",
                "required": True,
                "optional": False,
                "ordering_index": 1,
                "applicable_proposition_ids": ["Base.Test#use"],
                "emission_eligible": True,
            },
        ]
        entry, traces, structural, resolutions, proofs = compose_item_candidate(
            {"item_id": "Base.Test", "identity_hint": "도구", "primary_use": "수리에 쓰는 도구다"},
            {"item_id": "Base.Test", "state": "adopted", "selected_role": "tool"},
            {"profiles": {"tool_body": {}}},
            identity_hint_target_map={},
            precedence_rules={},
            proposition_rows=propositions,
            requirement_rows=requirements,
            policy={"realization_constraints": {"paragraph_split_character_threshold": 220}},
        )
        self.assertEqual(entry["source"], "korean_prose_candidate_v1")
        self.assertEqual(len(traces), 1)
        self.assertEqual(set(traces[0]["proposition_ids"]), {"Base.Test#identity", "Base.Test#use"})
        self.assertTrue(all(row["status"] == "emitted_direct" for row in structural))
        self.assertTrue(all(row["proposition_resolution"] == "emitted" for row in resolutions))
        self.assertEqual(proofs, [])


if __name__ == "__main__":
    unittest.main()
