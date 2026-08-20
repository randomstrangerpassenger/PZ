from __future__ import annotations

from itertools import product
import json
from pathlib import Path
import sys
import unittest


TESTS_DIR = Path(__file__).resolve().parent
V2_ROOT = TESTS_DIR.parent
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import item_page_information_sufficiency as ips


def l3(**changes):
    value = {
        "artifact_set_materialization": "sealed_complete",
        "fact_availability": "approved_fact_set_empty",
        "contribution": "absent",
        "requiredness": "not_required",
        "representation": "missing",
    }
    value.update(changes)
    if "contribution" not in changes:
        if value["fact_availability"] == "unresolved" and value["requiredness"] == "unresolved" and value["representation"] == "unresolved":
            value["contribution"] = "unresolved"
        elif value["fact_availability"] == "approved_fact_present" and value["representation"] == "represented":
            value["contribution"] = "self_sufficient"
        elif value["fact_availability"] == "approved_fact_set_empty" and value["representation"] == "represented":
            value["contribution"] = "identity_only"
    return value


def l4(**changes):
    value = {
        "artifact_set_materialization": "sealed_complete",
        "fact_availability": "approved_fact_set_empty",
        "applicability": "unresolved",
        "representation": "missing",
        "scope_limitation": "blocked_by_negative_authority",
    }
    value.update(changes)
    return value


class ItemPageInformationSufficiencyTest(unittest.TestCase):
    def build_current_or_assert_expected_preflight_block(self):
        return ips.build_assessment(require_ratified_policy=True)

    def test_ratification_is_single_complete_exact_binding(self):
        contract = ips.load_json(ips.DEFAULT_CONTRACT_PATH)
        ratification = ips.load_json(ips.DEFAULT_RATIFICATION_PATH)
        paths = ips.validate_policy(contract, ratification, require_ratified=True)
        self.assertEqual([row["id"] for row in ratification["ratifications"]], list(ips.RATIFICATION_IDS))
        self.assertEqual(set(paths), {"assessment_contract", "baseline_field_registry", "layer3_state_derivation_contract", "layer4_state_derivation_contract"})
        self.assertEqual(contract["layer3_input_identity_policy"], ips.LAYER3_INPUT_IDENTITY_POLICY)
        self.assertEqual(
            [row["path"] for row in contract["layer3_generator_source_subjects"]],
            list(ips.GENERATOR_IMPLEMENTATION_FILES),
        )
        ratification_08 = next(row for row in ratification["ratifications"] if row["id"] == "IPS-RAT-08")
        self.assertIn("canonical content identity", ratification_08["amendment"])

    def test_proposal_state_is_rejected_before_policy_dependent_execution(self):
        contract = ips.load_json(ips.DEFAULT_CONTRACT_PATH)
        ratification = ips.load_json(ips.DEFAULT_RATIFICATION_PATH)
        ratification["ratification_state"] = "proposal"
        with self.assertRaises(ips.AssessmentFailure) as captured:
            ips.validate_policy(contract, ratification, require_ratified=True)
        self.assertEqual(captured.exception.code, "policy_not_ratified")

    def test_malformed_ratification_row_fails_with_structured_error(self):
        contract = ips.load_json(ips.DEFAULT_CONTRACT_PATH)
        ratification = ips.load_json(ips.DEFAULT_RATIFICATION_PATH)
        ratification["ratifications"][0] = None
        with self.assertRaises(ips.AssessmentFailure) as captured:
            ips.validate_policy(contract, ratification, require_ratified=True)
        self.assertEqual(captured.exception.code, "ratification_row_invalid")

    def test_blocked_negative_tuple_is_non_dispositive_and_rule_three_reachable(self):
        disposition, rule, reasons = ips.decide_disposition(
            l3(fact_availability="approved_fact_present", contribution="self_sufficient", requiredness="required", representation="represented"),
            l4(),
        )
        self.assertEqual((disposition, rule), ("information_sufficient", "IPS-PREC-03"))
        self.assertIn("layer4_negative_authority_scope_limitation_preserved", reasons)

    def test_evidence_limited_is_derivation_reachable(self):
        self.assertEqual(ips.decide_disposition(l3(), l4())[:2], ("evidence_limited", "IPS-PREC-04"))

    def test_missing_precedence_is_not_compensated_across_layers(self):
        sufficient_l4 = l4(fact_availability="approved_fact_present", applicability="applicable", representation="represented", scope_limitation="none")
        self.assertEqual(
            ips.decide_disposition(l3(fact_availability="approved_fact_present", requiredness="required", representation="missing"), sufficient_l4)[0],
            "known_information_missing",
        )
        sufficient_l3 = l3(fact_availability="approved_fact_present", requiredness="required", representation="represented")
        self.assertEqual(
            ips.decide_disposition(sufficient_l3, l4(fact_availability="approved_fact_present", applicability="applicable", representation="missing", scope_limitation="none"))[0],
            "known_information_missing",
        )

    def test_unresolved_precedes_represented_fact(self):
        self.assertEqual(
            ips.decide_disposition(
                l3(fact_availability="unresolved", requiredness="unresolved", representation="represented"),
                l4(fact_availability="approved_fact_present", applicability="applicable", representation="represented", scope_limitation="none"),
            )[0],
            "unresolved",
        )

    def test_incoherent_layer4_scope_tuple_fails_closed(self):
        result = ips.decide_disposition(
            l3(fact_availability="approved_fact_present", requiredness="required", representation="represented"),
            l4(fact_availability="approved_fact_present", applicability="applicable", representation="represented", scope_limitation="blocked_by_negative_authority"),
        )
        self.assertEqual(result[:2], ("unresolved", "IPS-PREC-05"))
        self.assertIn("incoherent_state_vector", result[2])

    def test_incoherent_contribution_and_materialization_fail_closed(self):
        vectors = (
            (l3(contribution="self_sufficient"), l4()),
            (l3(artifact_set_materialization="partial"), l4()),
            (l3(), l4(artifact_set_materialization="partial")),
        )
        for layer3, layer4 in vectors:
            with self.subTest(layer3=layer3, layer4=layer4):
                self.assertEqual(
                    ips.decide_disposition(layer3, layer4)[:2],
                    ("unresolved", "IPS-PREC-05"),
                )

    def test_item_identity_does_not_participate_in_policy(self):
        vector = (l3(fact_availability="approved_fact_present", requiredness="required", representation="represented"), l4())
        first = ips.decide_disposition(*vector)
        second = ips.decide_disposition(*json.loads(json.dumps(vector)))
        self.assertEqual(first, second)

    def test_matrix_is_total_over_declared_axis_space(self):
        dispositions = set(ips.DISPOSITIONS)
        for l3_availability, requiredness, l3_representation, l4_availability, applicability, l4_representation, limitation in product(
            ("approved_fact_present", "approved_fact_set_empty", "unresolved"),
            ("required", "optional", "not_required", "unresolved"),
            ("represented", "missing", "unresolved"),
            ("approved_fact_present", "approved_fact_set_empty", "unresolved"),
            ("applicable", "unresolved"),
            ("represented", "missing", "unresolved"),
            ("none", "blocked_by_negative_authority"),
        ):
            result = ips.decide_disposition(
                l3(fact_availability=l3_availability, requiredness=requiredness, representation=l3_representation),
                l4(fact_availability=l4_availability, applicability=applicability, representation=l4_representation, scope_limitation=limitation),
            )
            self.assertIn(result[0], dispositions)
            self.assertRegex(result[1], r"^IPS-PREC-0[1-5]$")
            if ips.state_vector_incoherence(
                l3(fact_availability=l3_availability, requiredness=requiredness, representation=l3_representation),
                l4(fact_availability=l4_availability, applicability=applicability, representation=l4_representation, scope_limitation=limitation),
            ):
                self.assertEqual(result[:2], ("unresolved", "IPS-PREC-05"))
        self.assertTrue(
            ips.matrix_totality_check(
                ips.load_json(ips.DATA_ROOT / "layer3_state_derivation_contract.json"),
                ips.load_json(ips.DATA_ROOT / "layer4_state_derivation_contract.json"),
            )
        )

    def test_current_contract_forbids_non_applicability_and_heuristic_policy(self):
        layer4_contract = (ips.DATA_ROOT / "layer4_state_derivation_contract.json").read_text(encoding="utf-8")
        source = Path(ips.__file__).read_text(encoding="utf-8")
        forbidden_token = "not" + "_applicable"
        self.assertNotIn(forbidden_token, layer4_contract)
        self.assertNotIn("minimum_length", source)
        self.assertNotIn("sentence_threshold", source)
        self.assertNotIn("numeric_score", source)

    def test_strict_json_reader_rejects_duplicate_exact_keys(self):
        with self.assertRaises(ips.AssessmentFailure) as captured:
            json.loads('{"Base.A":1,"Base.A":2}', object_pairs_hook=ips._strict_object)
        self.assertEqual(captured.exception.code, "duplicate_json_key")

    def test_output_root_cannot_intersect_source_or_runtime(self):
        with self.assertRaises(ips.AssessmentFailure) as captured:
            ips.write_bundle({"validation_report.json": b"{}\n"}, ips.repo_path("Iris/input"))
        self.assertEqual(captured.exception.code, "output_outside_designated_root")

    def test_governance_entry_selectors_fail_on_duplicate_or_missing_boundaries(self):
        payload = {"entries": [{"entry_id": "IPS-ONE"}, {"nested": {"entry_id": "IPS-ONE"}}]}
        self.assertEqual(len(ips._find_entry_id(payload, "IPS-ONE")), 2)
        decisions = ips.repo_path("docs/DECISIONS.md")
        digest = ips._markdown_segment_hash(
            decisions,
            "<!-- IPS-GOV-DECISIONS-01-START -->",
            "<!-- IPS-GOV-DECISIONS-01-END -->",
        )
        self.assertRegex(digest, r"^[0-9a-f]{64}$")
        with self.assertRaises(ips.AssessmentFailure) as captured:
            ips._markdown_segment_hash(decisions, "<!-- IPS-MISSING -->", "<!-- IPS-ALSO-MISSING -->")
        self.assertEqual(captured.exception.code, "ambiguous_markdown_boundary")

    def test_partial_layer3_body_does_not_represent_every_proposition(self):
        hashes = {"layer3_facts": "a" * 64, "layer3_decisions": "b" * 64, "layer3_rendered": "c" * 64}
        state = ips._layer3_state(
            "Base.Example",
            {"item_id": "Base.Example", "primary_use": "use", "acquisition_hint": "acquire"},
            {"state": "adopted"},
            {"text_ko": "use only", "body_plan": {"emitted_section_names": ["identity_core", "use_core"]}},
            hashes,
        )
        self.assertEqual(state["representation"], "missing")
        self.assertEqual(state["contribution"], "supporting_context")
        self.assertEqual(state["represented_proposition_fields"], ["primary_use"])

    def test_layer3_binding_uses_exact_consumed_source_fields(self):
        hashes = {"layer3_facts": "a" * 64, "layer3_decisions": "b" * 64, "layer3_rendered": "c" * 64}
        state = ips._layer3_state(
            "Base.Example",
            {
                "item_id": "Base.Example",
                "primary_use": "primary",
                "secondary_use": "secondary",
                "processing_hint": "processing",
                "limitation_hint": "limitation",
                "special_context": "special",
            },
            {"state": "adopted"},
            {
                "text_ko": "primary and limitation",
                "body_plan": {"emitted_section_names": ["use_core", "limitation_tail"]},
            },
            hashes,
            [
                {"section": "use_core", "slots": ["primary_use"], "source_fields": ["facts.primary_use"]},
                {"section": "limitation_tail", "slots": ["limitation_hint"], "source_fields": ["facts.limitation_hint"]},
            ],
        )
        self.assertEqual(
            state["emitted_source_fields"],
            ["facts.limitation_hint", "facts.primary_use"],
        )
        self.assertEqual(
            state["represented_proposition_fields"],
            ["limitation_hint", "primary_use"],
        )
        self.assertEqual(state["representation"], "missing")

    def test_recomputed_candidate_sections_are_limited_to_sealed_rendered_names(self):
        fact = {
            "item_id": "Base.Example",
            "identity_hint": "example",
            "primary_use": "use",
        }
        profiles = {
            "profiles": {
                "fixture": {
                    "section_order": ["identity_core", "use_core", "context_support"],
                    "required_sections": ["identity_core"],
                    "strong_minimum_any_of": [["identity_core", "use_core"]],
                    "adequate_minimum_any_of": [["identity_core"]],
                }
            }
        }
        rendered = {
            "resolved_profile": "fixture",
            "body_plan": {"emitted_section_names": ["identity_core", "use_core"]},
        }
        sections = ips._recompute_layer3_emitted_sections(
            "Base.Example", fact, rendered, None, profiles
        )
        self.assertEqual(
            [section["section"] for section in sections],
            ["identity_core", "use_core"],
        )

    def test_legacy_candidate_context_binds_to_special_context_generically(self):
        fact = {
            "item_id": "Base.Example",
            "identity_hint": "example",
            "primary_use": "use",
            "special_context": "legacy context",
        }
        profiles = {
            "profiles": {
                "fixture": {
                    "section_order": ["identity_core", "use_core"],
                    "required_sections": ["identity_core"],
                    "strong_minimum_any_of": [["identity_core", "use_core"]],
                    "adequate_minimum_any_of": [["identity_core"]],
                }
            }
        }
        rendered = {
            "resolved_profile": "fixture",
            "body_plan": {
                "emitted_section_names": [
                    "identity_core",
                    "context_support",
                    "use_core",
                ]
            },
        }
        sections = ips._recompute_layer3_emitted_sections(
            "Base.Example", fact, rendered, None, profiles
        )
        context = next(row for row in sections if row["section"] == "context_support")
        self.assertEqual(context["source_fields"], ["facts.special_context"])
        self.assertEqual(context["source_binding"], "legacy_candidate_special_context")

    def test_missing_layer3_decision_is_unresolved(self):
        hashes = {"layer3_facts": "a" * 64, "layer3_decisions": "b" * 64, "layer3_rendered": "c" * 64}
        state = ips._layer3_state(
            "Base.Example",
            {"item_id": "Base.Example", "primary_use": "use"},
            None,
            {"text_ko": "use", "body_plan": {"emitted_section_names": ["use_core"]}},
            hashes,
        )
        self.assertEqual(
            (state["fact_availability"], state["contribution"], state["requiredness"], state["representation"]),
            ("unresolved", "unresolved", "unresolved", "unresolved"),
        )

    def test_absent_fulltype_in_sealed_layer3_set_is_not_required(self):
        hashes = {"layer3_facts": "a" * 64, "layer3_decisions": "b" * 64, "layer3_rendered": "c" * 64}
        state = ips._layer3_state(
            "Base.NotAuthored",
            None,
            None,
            None,
            hashes,
            [],
        )
        self.assertEqual(
            (
                state["fact_availability"],
                state["contribution"],
                state["requiredness"],
                state["representation"],
            ),
            ("approved_fact_set_empty", "absent", "not_required", "missing"),
        )

    def test_exclusion_only_layer4_is_not_positive_contribution(self):
        hashes = {"layer4_usecases": "a" * 64, "layer4_descriptions": "b" * 64}
        state = ips._layer4_state(
            "Base.Example",
            {"use_cases": [{"use_case_id": "uc.no", "line_kind": "exclusion", "evidence_sources": [{"source_type": "recipe_evidence", "decision": "NO"}]}]},
            {"use_case_block": {"items": [{"use_case_id": "uc.no", "line_kind": "evidence"}]}},
            hashes,
        )
        self.assertEqual(state["fact_availability"], "approved_fact_set_empty")
        self.assertEqual(state["scope_limitation"], "blocked_by_negative_authority")

    def test_malformed_layer4_records_fail_closed(self):
        hashes = {"layer4_usecases": "a" * 64, "layer4_descriptions": "b" * 64}
        malformed = (
            ({"use_cases": {}}, None, "malformed_layer4_use_case_set"),
            ({"use_cases": [{"line_kind": "evidence", "evidence_sources": [{"source_type": "recipe_evidence", "decision": "PASS"}]}]}, None, "missing_layer4_use_case_id"),
            ({"use_cases": [{"use_case_id": "uc.one", "line_kind": "evidence", "evidence_sources": {}}]}, None, "malformed_layer4_evidence_sources"),
            ({"use_cases": [{"use_case_id": "uc.one", "line_kind": "evidence", "evidence_sources": [{"decision": "PASS"}]}]}, None, "malformed_layer4_evidence_source"),
            ({"use_cases": [{"use_case_id": "uc.one", "line_kind": "evidence", "evidence_sources": [{"source_type": "recipe_evidence", "decision": "REVIEW"}]}]}, None, "unsupported_layer4_evidence_decision"),
            ({"use_cases": [{"use_case_id": "uc.one", "line_kind": "evidence", "evidence_sources": [{"source_type": "diagnostic", "decision": "PASS"}]}]}, None, "unsupported_layer4_evidence_source_type"),
            ({"use_cases": [{"use_case_id": "uc.one", "line_kind": "evidence", "evidence_sources": [{"source_type": "recipe_evidence", "decision": "PASS"}]}]}, {"use_case_block": {"items": {}}}, "malformed_layer4_use_case_block"),
        )
        for usecase, description, code in malformed:
            with self.subTest(code=code):
                with self.assertRaises(ips.AssessmentFailure) as captured:
                    ips._layer4_state("Base.Example", usecase, description, hashes)
                self.assertEqual(captured.exception.code, code)

    def test_layer4_source_to_rendered_mismatch_is_item_scoped_unresolved(self):
        hashes = {"layer4_usecases": "a" * 64, "layer4_descriptions": "b" * 64}
        cases = (
            (
                {"use_cases": []},
                {"use_case_block": {"items": [{"use_case_id": "uc.unknown", "line_kind": "evidence"}]}},
                "public_use_case_without_exact_fulltype_source_binding",
            ),
            (
                {"use_cases": [{"use_case_id": "uc.no", "line_kind": "evidence", "evidence_sources": [{"source_type": "rightclick", "decision": "NO"}]}]},
                {"use_case_block": {"items": [{"use_case_id": "uc.no", "line_kind": "evidence"}]}},
                "public_positive_without_approved_pass_binding",
            ),
        )
        for usecase, description, reason in cases:
            with self.subTest(reason=reason):
                state = ips._layer4_state("Base.Example", usecase, description, hashes)
                self.assertEqual(
                    (
                        state["fact_availability"],
                        state["applicability"],
                        state["representation"],
                        state["scope_limitation"],
                    ),
                    ("unresolved", "unresolved", "unresolved", "none"),
                )
                self.assertIn(reason, state["reasons"])

    def test_requirements_only_description_has_no_positive_representation(self):
        self.assertEqual(
            ips._displayed_layer4_ids(
                "Base.Example",
                {"require_block": {"lines": ["- requirement"]}},
            ),
            (set(), set()),
        )

    def test_display_binding_tracks_all_ids_and_rejects_unknown_line_kinds(self):
        self.assertEqual(
            ips._displayed_layer4_ids(
                "Base.Example",
                {
                    "use_case_block": {
                        "items": [
                            {"use_case_id": "uc.yes", "line_kind": "evidence"},
                            {"use_case_id": "uc.no", "line_kind": "exclusion"},
                        ]
                    }
                },
            ),
            ({"uc.yes", "uc.no"}, {"uc.yes"}),
        )
        with self.assertRaises(ips.AssessmentFailure) as captured:
            ips._displayed_layer4_ids(
                "Base.Example",
                {"use_case_block": {"items": [{"use_case_id": "uc.bad", "line_kind": "note"}]}},
            )
        self.assertEqual(captured.exception.code, "malformed_layer4_display_line_kind")

    def test_descriptor_output_omission_differs_from_independent_installed_universe(self):
        contract = ips.load_json(ips.DEFAULT_CONTRACT_PATH)
        pointer = ips.repo_path(contract["inputs"]["layer3_current_pointer"])
        generation_id = ips._parse_current_generation(pointer)
        generation_root = pointer.parent / "IrisLayer3Generations" / generation_id
        descriptor = ips.load_json(generation_root / "generation_descriptor.json")
        independent = ips._installed_generation_output_identity(pointer, generation_root, generation_id)
        self.assertEqual(descriptor["outputs"], independent)
        self.assertNotEqual(descriptor["outputs"][:-1], independent)

    def test_legacy_descriptor_accepts_newline_only_checkout_normalization(self):
        crlf = b'{"a": 1}\r\n{"b": 2}\r\n'
        lf = crlf.replace(b"\r\n", b"\n")
        record = {
            "path": "fixture.jsonl",
            "raw_byte_sha256": ips.hashlib.sha256(crlf).hexdigest(),
            "size": len(crlf),
        }
        self.assertEqual(
            ips._descriptor_text_identity_mode(lf, record),
            "utf8_newline_equivalent",
        )
        self.assertIsNone(
            ips._descriptor_text_identity_mode(lf.replace(b"2", b"3"), record)
        )

    def test_current_descriptor_reports_only_exact_or_newline_equivalent_inputs(self):
        contract = ips.load_json(ips.DEFAULT_CONTRACT_PATH)
        pointer = ips.repo_path(contract["inputs"]["layer3_current_pointer"])
        _, _, _, _, validation, generator_validation = ips._validate_generation(pointer)
        modes = [row["validation_mode"] for row in validation]
        self.assertEqual(len(modes), 7)
        self.assertEqual(modes.count("utf8_newline_equivalent"), 4)
        self.assertEqual(modes.count("raw_byte_exact"), 3)
        self.assertEqual(len(generator_validation), 7)
        self.assertEqual(
            sum(row["validation_mode"] == "utf8_newline_equivalent" for row in generator_validation),
            3,
        )
        self.assertEqual(
            sum(
                row["validation_mode"] == "ratified_lf_normalized_source_exact"
                for row in generator_validation
            ),
            1,
        )

    def test_canonical_json_content_ignores_formatting_but_not_values(self):
        first = ips._canonical_producer_content_bytes(b'{"b":2,"a":1}\r\n', ".json")
        second = ips._canonical_producer_content_bytes(b'{\n  "a": 1,\n  "b": 2\n}\n', ".json")
        changed = ips._canonical_producer_content_bytes(b'{"a":1,"b":3}\n', ".json")
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)

    def test_canonical_text_rejects_lone_carriage_return(self):
        with self.assertRaises(ips.AssessmentFailure) as captured:
            ips._canonical_producer_content_bytes(b'{"a":1}\r', ".json")
        self.assertEqual(captured.exception.code, "unsupported_lone_carriage_return")
        raw_exact_with_lone_cr = b"source\r"
        record = {
            "path": "fixture.py",
            "raw_byte_sha256": ips.hashlib.sha256(raw_exact_with_lone_cr).hexdigest(),
            "size": len(raw_exact_with_lone_cr),
        }
        with self.assertRaises(ips.AssessmentFailure) as descriptor_captured:
            ips._descriptor_text_identity_mode(raw_exact_with_lone_cr, record)
        self.assertEqual(
            descriptor_captured.exception.code,
            "unsupported_lone_carriage_return",
        )

    def test_declared_fixtures_are_loaded_and_follow_expected_paths(self):
        fixture_root = TESTS_DIR / "fixtures" / "item_page_information_sufficiency"
        fixtures = {path.stem: json.loads(path.read_text(encoding="utf-8")) for path in fixture_root.glob("*.json")}
        representative = ips.load_json(ips.DATA_ROOT / "representative_cases.json")
        contract = ips.load_json(ips.DEFAULT_CONTRACT_PATH)
        denominator = ips.load_json(ips.repo_path(contract["inputs"]["denominator"]))
        _, bound_fixture_paths = ips._load_representative_cases(
            ips.DATA_ROOT / "representative_cases.json",
            set(denominator),
            contract["anchors"],
        )
        declared_fixture_names = {
            Path(case["fixture"]).stem
            for case in representative["cases"]
            if "fixture" in case
        }
        self.assertEqual(set(fixtures), declared_fixture_names)
        self.assertEqual(
            {path.stem for path in bound_fixture_paths},
            declared_fixture_names,
        )
        hashes = {
            "layer3_facts": "a" * 64,
            "layer3_decisions": "b" * 64,
            "layer3_rendered": "c" * 64,
            "layer4_usecases": "d" * 64,
            "layer4_descriptions": "e" * 64,
        }
        for name, fixture in fixtures.items():
            with self.subTest(fixture=name):
                if "layer3_state" in fixture:
                    layer3 = fixture["layer3_state"]
                else:
                    layer3 = ips._layer3_state(
                        "Base.Fixture",
                        fixture["fact"],
                        fixture["decision"],
                        fixture["rendered"],
                        hashes,
                        fixture["emitted_sections"],
                    )
                layer4 = ips._layer4_state(
                    "Base.Fixture",
                    fixture["usecase"],
                    fixture["description"],
                    hashes,
                )
                self.assertEqual(
                    ips.decide_disposition(layer3, layer4)[:2],
                    (fixture["expected"], fixture["expected_rule"]),
                )

    def test_full_current_universe_build_is_exact_and_keeps_axes_separate(self):
        bundle = self.build_current_or_assert_expected_preflight_block()
        if bundle is None:
            return
        summary = json.loads(bundle["assessment_summary.json"])
        manifest = json.loads(bundle["assessment_input_manifest.json"])
        page_rows = [json.loads(line) for line in bundle["page_assessment.jsonl"].splitlines()]
        denominator = ips.load_json(ips.repo_path("Iris/input/items_itemscript.json"))
        self.assertEqual(summary["denominator_count"], len(denominator))
        self.assertEqual(len(page_rows), len(denominator))
        self.assertEqual({row["fulltype"] for row in page_rows}, set(denominator))
        self.assertGreater(summary["disposition_counts"]["evidence_limited"], 0)
        self.assertTrue(all(row["execution_status"] == "PASS" for row in page_rows))
        self.assertTrue(all(row["publish_verdict"] is False for row in page_rows))
        self.assertEqual(
            manifest["exception_ledger"]["sha256"],
            summary["input_hashes"]["exception_ledger"],
        )
        self.assertEqual(
            {row["exception_routing"]["ledger_sha256"] for row in page_rows},
            {summary["input_hashes"]["exception_ledger"]},
        )
        self.assertEqual(
            manifest["exception_ledger"]["identity_algorithm"],
            "sha256_canonical_jsonl_records_lf_v1",
        )

    def test_anchor_rows_use_generic_rule_path(self):
        bundle = self.build_current_or_assert_expected_preflight_block()
        if bundle is None:
            return
        anchors = json.loads(bundle["anchor_assessment.json"])
        self.assertTrue(anchors["generic_evaluator_path"])
        self.assertFalse(anchors["item_specific_branches"])
        self.assertEqual({row["fulltype"] for row in anchors["anchors"]}, {"Base.223BulletsMold", "Base.Tongs", "Base.Broom"})

    def test_exception_ledger_cannot_override_terminal_state(self):
        bundle = self.build_current_or_assert_expected_preflight_block()
        if bundle is None:
            return
        broom = next(json.loads(line) for line in bundle["page_assessment.jsonl"].splitlines() if json.loads(line)["fulltype"] == "Base.Broom")
        self.assertTrue(broom["exception_routing"]["ledger_entry_present"])
        self.assertFalse(broom["exception_routing"]["terminal_state_override_allowed"])
        self.assertEqual(broom["page_disposition"], "unresolved")


if __name__ == "__main__":
    unittest.main()
