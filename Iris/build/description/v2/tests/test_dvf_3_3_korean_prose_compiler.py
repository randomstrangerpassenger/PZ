from korean_prose_compiler_test_support import *

class KoreanProseCompilerTest(unittest.TestCase):
    def test_acquisition_listing_uses_location_method_and_mixed_labels(self) -> None:
        cases = {
            "작업 차량과 차고, 공구 상자와 공구점에서 발견된다": (
                "획득 장소: 작업 차량, 차고, 공구 상자, 공구점",
                "candidate_acquisition_location_list_v1",
            ),
            "장신구 취급 장소와 장신구 보관 장소, 채집으로 구할 수 있다": (
                "획득: 장신구 취급 장소, 장신구 보관 장소, 채집",
                "candidate_acquisition_mixed_list_v1",
            ),
            "나무막대와 끈, 종이클립이나 못으로 제작한다": (
                "획득 방법: 나무막대, 끈, 종이클립/못으로 제작",
                "candidate_acquisition_method_list_v1",
            ),
        }
        for source, (expected_text, expected_rule) in cases.items():
            with self.subTest(source=source):
                text, transformations, rule = render_acquisition_listing(source)
                self.assertEqual(text, expected_text)
                self.assertEqual(transformations, ["lexical_surface_naturalization"])
                self.assertEqual(rule, expected_rule)
                self.assertNotRegex(text, r"(?:발견된다|구할 수 있다|얻는다|만든다|제작한다)$")

    def test_current_acquisition_corpus_is_fully_list_renderable(self) -> None:
        facts_path = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
        rendered_count = 0

        for raw_line in facts_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(raw_line)
            source = row.get("acquisition_hint")
            if source is None:
                continue
            text, _, _ = render_acquisition_listing(str(source))
            self.assertTrue(text.startswith(("획득 장소: ", "획득 방법: ", "획득: ")))
            self.assertFalse(text.endswith("."))
            rendered_count += 1
        self.assertEqual(rendered_count, 1050)

    def test_acquisition_listing_fails_loud_on_unknown_sentence_shape(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported acquisition listing source"):
            render_acquisition_listing("정의되지 않은 획득 표현이다")

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

    def test_generic_lexical_naturalization_named_cases(self) -> None:
        cases = {
            "action_context": ("장전 준비 작업에서 탄약을 상자에 담을 때 다룬다", "장전 준비하며 탄약을 상자에 담을 때 다룬다", True),
            "electronic_context": ("전자 작업에서 기기를 분해할 때 다룬다", "전자 기기를 분해할 때 다룬다", True),
            "kitchen_context": ("주방 작업에서 식기를 꺼낼 때 다룬다", "주방에서 식기를 꺼낼 때 다룬다", True),
            "relative_use": ("칠하거나 표식을 남기는 작업에 쓰는 도료다", "칠하거나 표식을 남기는 데 쓰는 도료다", True),
            "nominal_use": ("상처 처치 작업에 쓰는 의료 용품이다", "상처 처치에 쓰는 의료 용품이다", True),
            "coordinated_material_use": ("재배와 흙 작업에 쓰는 도구다", "재배하거나 흙을 다룰 때 쓰는 도구다", True),
            "part_context": ("총기 개조 작업에 들어가는 부품이다", "총기 개조에 들어가는 구성품이다", True),
            "during_context": ("차량 정비 작업 중 배터리를 다룰 때 사용된다", "차량 정비 중 배터리를 다룰 때 쓴다", True),
            "workplace": ("금속 작업 장소와 작업 현장에서 발견된다", "금속 작업장과 현장에서 발견된다", True),
            "vehicle": ("작업 차량과 차고에서 발견된다", "현장 차량과 차고에서 발견된다", True),
            "alternative_use": ("근접 전투나 작업에 함께 쓰는 도구다", "근접 전투에서뿐 아니라 다른 쓰임으로도 쓰는 도구다", True),
            "preserved_workplace_noun": ("공사 자재 보관 장소와 작업장에서 발견된다", "공사 자재 보관 장소와 작업장에서 발견된다", False),
            "minimum_form_genitive": ("끈 형태의 재료다", "끈 형태로 된 재료다", True),
        }
        for cohort, (source, expected, transformed) in cases.items():
            with self.subTest(cohort=cohort):
                text, transformations = naturalize_source_fragment(source)
                self.assertEqual(text, expected)
                self.assertNotRegex(text, r"작업(?!장)")
                self.assertNotIn("과정", text)
                if transformed:
                    self.assertIn("lexical_surface_naturalization", transformations)
                else:
                    self.assertEqual(transformations, [])

    def test_generic_zero_anaphora_fuses_repeated_terminal_identity(self) -> None:
        comb = select_candidate_lead_realization(
            identity_text="빗",
            use_text="머리를 빗고 정돈할 때 쓰는 빗이다",
        )
        stone = select_candidate_lead_realization(
            identity_text="돌",
            use_text="돌망치를 만드는 재료로 쓰는 돌이다",
        )
        self.assertEqual(comb[0], "머리를 빗고 정돈할 때 쓴다.")
        self.assertEqual(stone[0], "돌망치를 만드는 재료로 쓴다.")
        self.assertIn("suppress_duplicate", comb[1])
        self.assertIn("suppress_duplicate", stone[1])

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
            candidate_proposition("identity", "facts.identity_hint", "도구", "identity-key"),
            candidate_proposition("use", "facts.primary_use", "수리에 쓰는 도구다", "use-key"),
        ]
        requirements = [
            candidate_requirement("identity_core", "identity", True, False, 0),
            candidate_requirement("use_core", "use", True, False, 1),
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

    def test_candidate_composer_emits_acquisition_as_separate_runtime_line(self) -> None:
        propositions = [
            candidate_proposition("identity", "facts.identity_hint", "도구", "identity-key"),
            candidate_proposition("use", "facts.primary_use", "수리에 쓰는 도구다", "use-key"),
            candidate_proposition(
                "acquisition", "facts.acquisition_hint", "작업 차량과 차고에서 발견된다", "acquisition-key"
            ),
        ]
        requirements = [
            candidate_requirement("identity_core", "identity", True, False, 0),
            candidate_requirement("use_core", "use", True, False, 1),
            candidate_requirement("acquisition_support", "acquisition", False, True, 2),
        ]
        entry, traces, structural, resolutions, proofs = compose_item_candidate(
            {
                "item_id": "Base.Test",
                "identity_hint": "도구",
                "primary_use": "수리에 쓰는 도구다",
                "acquisition_hint": "작업 차량과 차고에서 발견된다",
            },
            {"item_id": "Base.Test", "state": "adopted", "selected_role": "tool"},
            {"profiles": {"tool_body": {}}},
            identity_hint_target_map={},
            precedence_rules={},
            proposition_rows=propositions,
            requirement_rows=requirements,
            policy={"realization_constraints": {"paragraph_split_character_threshold": 220}},
        )
        self.assertEqual(
            entry["text_ko"],
            "수리에 쓰는 도구다.\n\n획득 장소: 작업 차량, 차고",
        )
        acquisition_trace = next(
            row for row in traces if row["ordering_reason"].endswith("acquisition")
        )
        self.assertEqual(acquisition_trace["text"], "획득 장소: 작업 차량, 차고")
        self.assertEqual(
            acquisition_trace["realization_rule_id"],
            "candidate_acquisition_location_list_v1",
        )
        self.assertTrue(all(row["proposition_resolution"] == "emitted" for row in resolutions))
        self.assertEqual(proofs, [])

    def test_current_rendered_and_runtime_chunks_publish_same_text(
        self,
    ) -> None:
        rendered = json.loads(current_rendered_path().read_text(encoding="utf-8"))[
            "entries"
        ]
        runtime = load_current_runtime_chunks()
        self.assertEqual(set(runtime), set(rendered))

        for item_id, rendered_entry in rendered.items():
            self.assertEqual(
                runtime[item_id].get("text_ko"),
                rendered_entry.get("text_ko"),
                item_id,
            )


if __name__ == "__main__":
    unittest.main()
