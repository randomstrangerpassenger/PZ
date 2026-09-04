from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[5]
AUTHORITY_ROOT = REPO_ROOT / "Iris" / "_docs" / "authority" / "dvf" / "layer3_successor"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _set_sha256(values: list[str]) -> str:
    payload = "".join(f"{value}\n" for value in sorted(set(values))).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _generation_tree_sha256(root: Path) -> tuple[int, str, list[dict[str, str]]]:
    members = []
    for path in sorted(
        (path for path in root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(root).as_posix(),
    ):
        members.append(
            {
                "path": path.relative_to(root).as_posix(),
                "sha256": _sha256(path),
            }
        )
    payload = "".join(
        f"{member['path']}\t{member['sha256']}\n" for member in members
    ).encode("utf-8")
    return len(members), hashlib.sha256(payload).hexdigest(), members


def _validate_case(
    case: dict[str, Any], contract: dict[str, Any]
) -> tuple[bool, str | None]:
    expected = case["expected"]
    if expected == "accept_transition_only":
        return (not case.get("automatic_successor_fact", True), None)

    facts = case.get("facts", [])
    fact_ids = [fact.get("fact_id") for fact in facts]
    if len(fact_ids) != len(set(fact_ids)):
        return False, "duplicate_fact_id"

    allowed_kinds = set(contract["semantic_node"]["allowed_fact_kinds"])
    forbidden_aliases = set(contract["forbidden_representative_aliases"])
    forbidden_sources = set(contract["forbidden_fact_sources"])
    provenance = case.get("provenance", {})
    fact_by_id = {fact["fact_id"]: fact for fact in facts}

    for fact in facts:
        if forbidden_aliases.intersection(fact):
            return False, "forbidden_representative_alias"
        if not set(contract["semantic_node"]["required_fields"]).issubset(fact):
            return False, "missing_required_fact_field"
        if fact["fact_kind"] not in allowed_kinds:
            return False, "unknown_fact_kind"
        if not fact["provenance_refs"]:
            return False, "missing_provenance"
        for provenance_ref in fact["provenance_refs"]:
            source = provenance.get(provenance_ref)
            if source is None:
                return False, "missing_provenance"
            if source.get("source_kind") in forbidden_sources:
                return False, "forbidden_fact_source"

        if fact["fact_kind"] == "context_role":
            target = fact_by_id.get(fact.get("context_fact_ref"))
            if target is None or target["fact_kind"] != "use_context":
                return False, "invalid_context_role_binding"

        if fact["fact_kind"] in {"condition", "constraint"}:
            targets = fact.get("applies_to_fact_refs", [])
            if not targets:
                return False, "invalid_qualifier_binding"
            if any(
                target not in fact_by_id
                or fact_by_id[target]["fact_kind"] in {"condition", "constraint"}
                for target in targets
            ):
                return False, "invalid_qualifier_binding"

        if fact["fact_kind"] == "acquisition_unobtainable" and not fact.get(
            "negative_evidence_refs"
        ):
            return False, "missing_negative_evidence"

    investigation = case.get("investigation", {})
    acquisition_state = investigation.get("acquisition_state")
    acquisition_facts = [
        fact
        for fact in facts
        if fact["fact_kind"] in {"acquisition", "acquisition_unobtainable"}
    ]
    if acquisition_state == "resolved":
        if not acquisition_facts:
            return False, "acquisition_false_resolution"
        if investigation.get("acquisition_axis_complete") is not True:
            return False, "acquisition_axis_not_complete"
    if acquisition_state in {"investigated_unresolved", "not_investigated"}:
        if (
            acquisition_facts
            or investigation.get("acquisition_axis_complete")
            or investigation.get("item_investigation_complete")
        ):
            return False, "acquisition_false_completion"

    surfaces = case.get("surfaces")
    if surfaces:
        menu_refs = set(surfaces.get("menu_fact_refs", []))
        if menu_refs != set(fact_ids):
            return False, "menu_fact_loss"
        tooltip = surfaces.get("tooltip_s2")
        if tooltip:
            represented = set(tooltip["represented_fact_refs"])
            dependencies = set(tooltip["dependency_fact_refs"])
            omitted = set(tooltip["omitted_detail_refs"])
            if not represented.issubset(fact_by_id):
                return False, "tooltip_unknown_fact"
            if not dependencies.issubset(fact_by_id):
                return False, "tooltip_unknown_dependency"
            if tooltip["selection_basis"] in {
                "importance",
                "frequency",
                "efficiency",
                "first_ordinal",
                "profile_label",
            }:
                return False, "forbidden_representative_selection"
            required_dependencies = {
                fact["fact_id"]
                for fact in facts
                if fact["fact_kind"] in {"condition", "constraint"}
                and represented.intersection(fact.get("applies_to_fact_refs", []))
            }
            if not required_dependencies.issubset(dependencies):
                return False, "truth_dependency_loss"
            if omitted - menu_refs:
                return False, "omitted_detail_not_in_menu"

    if case.get("independent_layer4_relations"):
        layer3_ids = set(fact_ids)
        layer4_ids = {
            relation["relation_id"]
            for relation in case["independent_layer4_relations"]
        }
        if layer3_ids.intersection(layer4_ids):
            return False, "layer_identity_leakage"

    return True, None


class Layer3SuccessorContractTest(unittest.TestCase):
    def test_contract_adoption(self) -> None:
        contract = _load_json(AUTHORITY_ROOT / "contract.json")
        casebook = _load_json(AUTHORITY_ROOT / "casebook.json")
        inventory = _load_json(AUTHORITY_ROOT / "predecessor_inventory.json")
        manifest = _load_json(AUTHORITY_ROOT / "contract_manifest.json")

        self.assertEqual(
            contract["schema_version"], "iris-layer3-successor-contract-v1"
        )
        self.assertEqual(
            casebook["schema_version"], "iris-layer3-successor-casebook-v1"
        )
        self.assertEqual(
            inventory["schema_version"],
            "iris-layer3-successor-predecessor-inventory-v1",
        )
        self.assertEqual(
            manifest["schema_version"],
            "iris-layer3-successor-contract-manifest-v1",
        )
        self.assertEqual(contract["status"], "current_semantic_authority")
        self.assertEqual(contract["identity"]["semantic_fact_multiplicity"], "0..N")
        self.assertTrue(contract["identity"]["case_sensitive"])
        self.assertFalse(
            contract["identity"]["ordered_serialization_is_semantically_ranked"]
        )

        expected_axes = {
            "semantic_fact",
            "provenance",
            "investigation",
            "expression",
            "presentation",
        }
        self.assertEqual(set(contract["axes"]), expected_axes)
        axis_owners = [
            owned
            for axis in contract["axes"].values()
            for owned in axis["owns"]
        ]
        self.assertEqual(len(axis_owners), len(set(axis_owners)))
        self.assertFalse(contract["axes"]["provenance"]["rendered_layer_output_is_source"])
        self.assertTrue(contract["axes"]["investigation"]["does_not_create_facts"])
        self.assertTrue(contract["axes"]["expression"]["absence_does_not_delete_fact"])
        self.assertTrue(
            contract["axes"]["presentation"]["does_not_create_or_reselect_facts"]
        )

        self.assertTrue(
            contract["semantic_node"]["bindings"]["context_role"]
            ["item_global_role_forbidden"]
        )
        self.assertTrue(
            contract["semantic_node"]["nested_qualifier_and_top_level_duplicate_forbidden"]
        )
        self.assertIn("primary_use", contract["forbidden_representative_aliases"])
        self.assertIn("headline_fact", contract["forbidden_representative_aliases"])
        self.assertFalse(
            contract["resolution_boundary"]
            ["one_layer_output_may_create_other_layer_fact"]
        )

        vocabulary = contract["vocabulary"]
        self.assertEqual(vocabulary["kind"], "open_versioned_registry")
        self.assertFalse(vocabulary["seed_examples_are_exhaustive"])
        self.assertFalse(
            vocabulary["compatible_extension"]["requires_full_contract_readoption"]
        )
        self.assertTrue(vocabulary["breaking_change"]["requires_contract_revision"])
        self.assertEqual(
            set(vocabulary["admission_required_fields"]),
            {
                "token",
                "axis",
                "definition",
                "positive_examples",
                "negative_examples",
                "evidence_refs",
                "boundary_unchanged",
            },
        )

        acquisition = contract["acquisition"]
        self.assertTrue(acquisition["mandatory_investigation_for_current_layer3_target"])
        self.assertFalse(
            acquisition["investigated_unresolved_is_item_investigation_complete"]
        )
        self.assertFalse(acquisition["not_investigated_is_item_investigation_complete"])
        self.assertTrue(acquisition["resolved_is_acquisition_axis_complete"])
        self.assertFalse(acquisition["resolved_is_item_investigation_complete"])
        self.assertEqual(acquisition["item_investigation_completion_owner"], "DVF-L3-02")
        self.assertTrue(acquisition["resolved_result_is_menu_required"])
        self.assertFalse(acquisition["resolved_result_is_tooltip_required"])
        self.assertEqual(
            contract["semantic_node"]["bindings"]["acquisition_unobtainable"]
            ["current_assignment_count"],
            0,
        )

        profiles = contract["profiles"]
        self.assertIn("first_contact_axis_scope", profiles["allowed_responsibilities"])
        self.assertNotIn("sentence_count", profiles["forbidden_responsibilities"])
        self.assertNotIn("tooltip_s2_selection", profiles["forbidden_responsibilities"])
        self.assertIn(
            "representative_fact_selection_by_importance_frequency_ordinal_or_profile_label",
            profiles["forbidden_responsibilities"],
        )
        self.assertEqual(profiles["first_contact_axis_owner"], "DVF-L3-02")
        self.assertEqual(
            profiles["actual_s2_fact_combination_expression_sentence_and_omission_owner"],
            "DVF-L3-05",
        )

        surfaces = contract["surfaces"]
        self.assertEqual(surfaces["canonical_authority"], "accepted_layer3_fact_set")
        self.assertTrue(surfaces["menu"]["must_preserve_all_accepted_fact_refs"])
        self.assertTrue(surfaces["tooltip_s2"]["represented_fact_refs_required"])
        self.assertTrue(
            surfaces["tooltip_s2"]
            ["selection_by_importance_frequency_or_ordinal_forbidden"]
        )
        self.assertFalse(surfaces["tooltip_s2"]["all_facts_required_in_one_row"])
        self.assertTrue(
            surfaces["tooltip_s2"]
            ["runtime_summary_truncation_reselection_inference_forbidden"]
        )
        self.assertEqual(
            surfaces["retained_tooltip_structure"],
            {
                "logical_rows": "0..4",
                "S1_owner": "Layer 2",
                "S2_owner": "Layer 3",
                "S3_owner": "Layer 4",
                "S4_owner": "Layer 4",
            },
        )

        case_results = {}
        for case in casebook["cases"]:
            valid, reason = _validate_case(case, contract)
            case_results[case["case_id"]] = (valid, reason)
            if case["expected"] in {"accept", "accept_transition_only"}:
                self.assertTrue(valid, msg=f"{case['case_id']}: {reason}")
            else:
                self.assertFalse(valid, msg=case["case_id"])
                self.assertEqual(reason, case["expected_reason"])
        transition_cases = {
            case["predecessor_field"]: case
            for case in casebook["cases"]
            if case["expected"] == "accept_transition_only"
        }
        self.assertFalse(transition_cases["identity_hint"]["automatic_successor_fact"])
        self.assertFalse(transition_cases["special_context"]["automatic_successor_fact"])
        self.assertFalse(transition_cases["special_context"]["automatic_priority"])
        self.assertEqual(
            set(case_results),
            {
                "single_context",
                "materially_distinct_multi_context",
                "same_context_multi_role",
                "truth_qualifying_condition",
                "acquisition_positive",
                "acquisition_investigated_unresolved",
                "acquisition_not_investigated",
                "layer3_broad_layer4_exact",
                "identity_hint_transition",
                "special_context_transition",
                "representative_alias_rejected",
                "layer_output_leakage_rejected",
                "false_acquisition_completion_rejected",
            },
        )
        self.assertEqual(
            sum(reason == "forbidden_fact_source" for valid, reason in case_results.values()),
            1,
        )
        self.assertEqual(
            sum(
                reason == "acquisition_false_completion"
                for valid, reason in case_results.values()
            ),
            1,
        )
        acquisition_positive = next(
            case
            for case in casebook["cases"]
            if case["case_id"] == "acquisition_positive"
        )
        self.assertTrue(
            acquisition_positive["investigation"]["acquisition_axis_complete"]
        )
        self.assertFalse(
            acquisition_positive["investigation"]["item_investigation_complete"]
        )

        expected_concepts = {
            "exact_full_type",
            "source_evidence_provenance",
            "identity_hint",
            "primary_use",
            "secondary_use",
            "special_context",
            "selected_item_global_role",
            "selected_compose_profile_as_semantic_identity",
            "single_core_fact_or_body",
            "acquisition_optional_support_only",
            "readiness_body_disposition",
            "tooltip_s2_single_core_consumption",
            "tooltip_s1_s3_s4_and_zero_to_four_rows",
            "current_corpus_runtime_generation",
        }
        dispositions = inventory["transition_dispositions"]
        self.assertEqual(
            {entry["current_concept"] for entry in dispositions}, expected_concepts
        )
        self.assertEqual(len(dispositions), len(expected_concepts))

        facts_path = REPO_ROOT / inventory["denominators"]["layer3_source_universe"]["source"]
        facts = [json.loads(line) for line in facts_path.read_text(encoding="utf-8").splitlines()]
        decisions_path = (
            REPO_ROOT / inventory["denominators"]["layer3_decision_universe"]["source"]
        )
        decisions = [
            json.loads(line)
            for line in decisions_path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(len(facts), 2105)
        self.assertEqual(len(decisions), 2105)
        self.assertEqual(
            _set_sha256([row["item_id"] for row in facts]),
            inventory["denominators"]["layer3_source_universe"]["exact_set_sha256"],
        )
        self.assertEqual(
            _set_sha256([row["item_id"] for row in decisions]),
            inventory["denominators"]["layer3_decision_universe"]["exact_set_sha256"],
        )
        self.assertEqual(
            sum(bool(row.get("primary_use")) for row in facts),
            inventory["current_fields"]["primary_use_non_empty"],
        )
        self.assertEqual(
            sum(bool(row.get("identity_hint")) for row in facts),
            inventory["current_fields"]["identity_hint_non_empty"],
        )
        self.assertEqual(
            sum(bool(row.get("secondary_use")) for row in facts),
            inventory["current_fields"]["secondary_use_non_empty"],
        )
        self.assertEqual(
            sum(bool(row.get("special_context")) for row in facts),
            inventory["current_fields"]["special_context_non_empty"],
        )
        self.assertEqual(
            sum(bool(row.get("acquisition_hint")) for row in facts),
            inventory["current_fields"]["acquisition_hint_non_empty"],
        )
        self.assertEqual(
            sum(row["state"] == "adopted" for row in decisions),
            inventory["current_decisions"]["adopted"],
        )
        self.assertEqual(
            sum(row["state"] == "unadopted" for row in decisions),
            inventory["current_decisions"]["unadopted"],
        )
        for role, expected_count in inventory["current_decisions"][
            "selected_roles"
        ].items():
            self.assertEqual(
                sum(row["selected_role"] == role for row in decisions), expected_count
            )
        for profile, expected_count in inventory["current_decisions"][
            "compose_profiles"
        ].items():
            self.assertEqual(
                sum(row["compose_profile"] == profile for row in decisions),
                expected_count,
            )

        owner_path = REPO_ROOT / "Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json"
        owner = _load_json(owner_path)
        self.assertEqual(len(owner["entries"]), 2048)
        self.assertEqual(len(owner["absence_entries"]), 175)
        self.assertEqual(
            _set_sha256(list(owner["entries"])),
            inventory["denominators"]["tooltip_layer3_owner_fact_set"]["exact_set_sha256"],
        )
        self.assertEqual(
            _set_sha256(list(owner["absence_entries"])),
            inventory["denominators"]["tooltip_owner_absence_set"]["exact_set_sha256"],
        )
        self.assertTrue(set(owner["entries"]).issubset(row["item_id"] for row in facts))
        self.assertEqual(
            len(set(row["item_id"] for row in facts) - set(owner["entries"])), 57
        )

        for protected in inventory["protected_files"]:
            self.assertEqual(_sha256(REPO_ROOT / protected["path"]), protected["sha256"])
        generation = inventory["current_generation"]
        member_count, tree_sha256, members = _generation_tree_sha256(
            REPO_ROOT / generation["root"]
        )
        self.assertEqual(member_count, generation["member_count"])
        self.assertEqual(tree_sha256, generation["tree_sha256"])
        self.assertEqual(members, generation["members"])

        expected_members = {
            "docs/iris_dvf_layer3_multi_meaning_information_resolution_successor_contract.md",
            "Iris/_docs/authority/dvf/layer3_successor/contract.json",
            "Iris/_docs/authority/dvf/layer3_successor/casebook.json",
            "Iris/_docs/authority/dvf/layer3_successor/predecessor_inventory.json",
        }
        self.assertEqual({member["path"] for member in manifest["members"]}, expected_members)
        self.assertEqual(len(manifest["members"]), 4)
        for member in manifest["members"]:
            self.assertEqual(_sha256(REPO_ROOT / member["path"]), member["sha256"])

        manifest_sha256 = _sha256(AUTHORITY_ROOT / "contract_manifest.json")
        authority_manifest = _load_json(
            REPO_ROOT / "Iris/_docs/authority/iris_current_authority_manifest.json"
        )
        successor_entries = [
            entry
            for entry in authority_manifest["entries"]
            if entry.get("path")
            == "Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json"
        ]
        self.assertEqual(len(successor_entries), 1)
        self.assertEqual(successor_entries[0]["sha256"], manifest_sha256)

        route_index = _load_json(
            REPO_ROOT / "Iris/_docs/authority/iris_current_route_index.json"
        )
        semantic_route = route_index["layer3_successor_semantic_contract"]
        self.assertEqual(
            semantic_route["manifest_path"],
            "Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json",
        )
        self.assertEqual(semantic_route["manifest_sha256"], manifest_sha256)
        self.assertEqual(semantic_route["product_migration_state"], "deferred")

        required_validations = _load_json(
            REPO_ROOT / "Iris/validation/execution/required_validations.json"
        )
        test_id = (
            "test_layer3_successor_contract.Layer3SuccessorContractTest."
            "test_contract_adoption"
        )
        selected = [
            entry
            for entry in required_validations["required_tests"]
            if entry["test_id"] == test_id
        ]
        self.assertEqual(len(selected), 1)
        self.assertTrue(selected[0]["required"])

        for relative_path in [
            "docs/DECISIONS.md",
            "docs/ARCHITECTURE.md",
            "docs/ROADMAP.md",
        ]:
            text = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn(manifest_sha256, text)
            self.assertIn(
                "Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json",
                text,
            )


if __name__ == "__main__":
    unittest.main()
