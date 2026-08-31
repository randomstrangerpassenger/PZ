from __future__ import annotations

import json
from copy import deepcopy
import hashlib
import shutil
import sys
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


from clean_checkout_test_paths import external_test_path
from iris_tooling.build.compose_layer3_text import (
    DEFAULT_MODE,
    ENTRYPOINT_MODES,
    DIAGNOSTIC_RESOLVER_MODE,
    DIAGNOSTIC_COMPOSE_CONTEXT,
    STAGING_COMPOSE_CONTEXT,
    build_rendered,
    main as compose_main,
    parse_args,
    resolve_entrypoint_paths,
)
from iris_tooling.build.compose_layer3_body_profile import (
    DEFAULT_LEGACY_COMPAT_LABEL_ERROR_CODE,
    DEFAULT_LEGACY_RUNTIME_STATE_ERROR_CODE,
    DIAGNOSTIC_RESOLVER_AUTHORITY_MODE,
    resolve_body_profile,
)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


class SharedCompositionTest(unittest.TestCase):
    def fixture(self):
        from iris_tooling.build.compose_layer3_shared import SCHEMA, digest
        facts, overlay, entries = [], [], {}
        for key, target in (("Base.First", "first"), ("Base.Second", "second")):
            source = f"Approved {target} use and effect under a condition"
            fact_id = "l3rf-" + digest({"item_id": key, "source_slot": "primary_use",
                "source_value_hash": hashlib.sha256(source.encode()).hexdigest(), "fact_origin": "direct_use"})
            material = {"schema_version": SCHEMA, "approval": "owner_preapproved_source_bound_material",
                "authority_ref": "fixture", "core_fact_id": fact_id, "source_slots": {"primary_use": digest(source)},
                "source_refs": [{"path": "fixture", "locator": key, "sha256": "a" * 64}],
                "values": {"condition": {"ko": "조건 충족 시", "en": "under the condition"},
                           "use": {"ko": target + " 용도", "en": target + " use"},
                           "effect": {"ko": "추가 효과", "en": "additional effect"}},
                "condition_parameters": ["condition"], "effect_parameters": ["use", "effect"]}
            facts.append({"item_id": key, "primary_use": source, "fact_origin": {"primary_use": ["direct_use"]},
                          "slot_meta": {"body_material": material}})
            overlay.append({"item_id": key, "body_composition": {"mode": "shared", "composition_id": "uses",
                           "material_sha256": digest(material), "menu_blocks": []}})
            entries[key] = {"text_ko": source, "role_material": {"core_source_fact_ids": [fact_id]}}
        entries["Base.Retained"] = {"text_ko": "그대로 유지", "role_material": {"core_source_fact_ids": []}}
        facts.append({"item_id": "Base.Retained"})
        overlay.append({"item_id": "Base.Retained", "body_composition": {"mode": "retained",
                        "reason": "empty_core", "entry_sha256": digest(entries["Base.Retained"])}})
        profiles = {"shared_composition": {"schema_version": SCHEMA, "authority_ref": "fixture",
            "definitions": {"uses": {"core": {"ko": "{condition} {use} 및 {effect}.",
                                               "en": "{use} and {effect} {condition}."}, "menu_blocks": {}}}}}
        return dict(facts_list=facts, overlay_list=overlay, profiles=profiles, predecessor={"meta": {}, "entries": entries})

    def test_shared_edit_propagates_and_preserves_conditions_multiple_uses_and_retention(self):
        from iris_tooling.build.compose_layer3_shared import compose_shared_candidate
        inputs = self.fixture()
        before = compose_shared_candidate(**inputs)
        reordered = deepcopy(inputs)
        reordered["facts_list"].reverse()
        reordered["overlay_list"].reverse()
        self.assertEqual(before, compose_shared_candidate(**reordered))
        inputs["profiles"]["shared_composition"]["definitions"]["uses"]["core"]["ko"] = "{condition} {use}. {effect}."
        after = compose_shared_candidate(**inputs)
        self.assertEqual(after["entries"]["Base.Retained"], inputs["predecessor"]["entries"]["Base.Retained"])
        for key in ("Base.First", "Base.Second"):
            self.assertNotEqual(before["entries"][key]["text_ko"], after["entries"][key]["text_ko"])
            core = after["entries"][key]["body_composition"]["core"]
            self.assertIn("조건 충족 시", core["ko"])
            self.assertIn("추가 효과", core["ko"])
            self.assertIn("additional effect", core["en"])
            self.assertEqual(before["entries"][key]["role_material"], after["entries"][key]["role_material"])

    def test_invalid_bindings_fail_without_falling_back_and_explicit_exception_is_supported(self):
        from iris_tooling.build.compose_layer3_shared import compose_shared_candidate, digest
        inputs = self.fixture()
        mutations = {
            "unknown": lambda x: x["overlay_list"][0]["body_composition"].update(composition_id="missing"),
            "missing": lambda x: x["facts_list"][0]["slot_meta"]["body_material"]["values"].pop("effect"),
            "condition": lambda x: x["profiles"]["shared_composition"]["definitions"]["uses"]["core"].update(ko="{use} {effect}", en="{use} {effect}"),
            "locale": lambda x: x["profiles"]["shared_composition"]["definitions"]["uses"]["core"].update(en="{use} {condition}"),
            "source": lambda x: x["facts_list"][0].update(primary_use="changed source"),
            "duplicate": lambda x: x["facts_list"].append(deepcopy(x["facts_list"][0])),
            "optional": lambda x: x["overlay_list"][0]["body_composition"].update(menu_blocks=["unknown"]),
            "retained": lambda x: x["predecessor"]["entries"]["Base.Retained"].update(text_ko="changed"),
            "exception": lambda x: x["overlay_list"][0]["body_composition"].update(mode="explicit"),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                changed = deepcopy(inputs)
                mutate(changed)
                changed["overlay_list"][0]["body_composition"]["material_sha256"] = digest(changed["facts_list"][0]["slot_meta"]["body_material"])
                with self.assertRaises(ValueError):
                    compose_shared_candidate(**changed)
        route = inputs["overlay_list"][0]["body_composition"]
        route.update(mode="explicit", exception_reason="approved fixture exception",
                     expression=deepcopy(inputs["profiles"]["shared_composition"]["definitions"]["uses"]))
        self.assertEqual(compose_shared_candidate(**inputs)["entries"]["Base.First"]["body_composition"]["mode"], "explicit")


class ComposeLayer3TextV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = external_test_path("_tmp_compose_v2")
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def write_shared_inputs(self) -> tuple[Path, Path, Path]:
        profiles_path = self.tmp_dir / "profiles_v2.json"
        identity_rules_path = self.tmp_dir / "identity_rules.json"
        precedence_rules_path = self.tmp_dir / "precedence_rules.json"

        write_json(
            profiles_path,
            {
                "schema_version": "compose-profiles-v2",
                "section_names": [
                    "identity_core",
                    "use_core",
                    "context_support",
                    "acquisition_support",
                    "limitation_tail",
                    "meta_tail",
                ],
                "render_rules": {
                    "paragraph_separator": "\n\n",
                    "insert_when_emitted_section_count_at_least": 2,
                },
                "profiles": {
                    "tool_body": {
                        "required_sections": ["identity_core", "use_core"],
                        "optional_sections": ["context_support", "acquisition_support", "limitation_tail"],
                        "section_order": [
                            "identity_core",
                            "use_core",
                            "context_support",
                            "limitation_tail",
                            "acquisition_support",
                        ],
                        "adequate_minimum_any_of": [["identity_core", "use_core"]],
                        "strong_minimum_any_of": [
                            ["identity_core", "use_core", "context_support"],
                            ["identity_core", "use_core", "acquisition_support"],
                        ],
                    },
                    "material_body": {
                        "required_sections": ["identity_core", "context_support"],
                        "optional_sections": ["use_core", "acquisition_support", "limitation_tail"],
                        "section_order": [
                            "identity_core",
                            "context_support",
                            "use_core",
                            "limitation_tail",
                            "acquisition_support",
                        ],
                        "adequate_minimum_any_of": [["identity_core", "context_support"]],
                        "strong_minimum_any_of": [
                            ["identity_core", "context_support", "use_core"],
                            ["identity_core", "context_support", "acquisition_support"],
                        ],
                    },
                },
            },
        )
        write_json(
            identity_rules_path,
            {
                "identity_hint_profile_targets": {
                    "도구": "tool_body",
                    "재료": "material_body",
                }
            },
        )
        write_json(
            precedence_rules_path,
            {
                "default_resolution": "identity_family_target",
                "eligible_identity_family_targets": [
                    "consumable_body",
                    "wearable_body",
                    "container_body",
                ],
            },
        )
        return profiles_path, identity_rules_path, precedence_rules_path

    def test_v2_selected_role_precedence_resolves_material_body(self) -> None:
        facts_path = self.tmp_dir / "facts.jsonl"
        decisions_path = self.tmp_dir / "decisions.jsonl"
        overlay_path = self.tmp_dir / "overlay.jsonl"
        output_path = self.tmp_dir / "rendered.json"
        style_log_path = self.tmp_dir / "style_log.jsonl"
        profiles_path, identity_rules_path, precedence_rules_path = self.write_shared_inputs()

        write_jsonl(
            facts_path,
            [
                {
                    "item_id": "Base.ModKit",
                    "identity_hint": "도구",
                    "primary_use": "총기 개조 작업에 들어가는 부품이다",
                    "acquisition_hint": "총포상과 작업대 주변에서 발견된다",
                    "processing_hint": None,
                    "special_context": None,
                    "limitation_hint": None,
                    "notes": None,
                    "fact_origin": {"primary_use": ["cluster_summary"]},
                }
            ],
        )
        write_jsonl(
            decisions_path,
            [
                {
                    "item_id": "Base.ModKit",
                    "state": "adopted",
                    "compose_profile": "interaction_component",
                    "override_mode": "none",
                    "selected_role": "material",
                    "selected_cluster": "gun_modding",
                }
            ],
        )
        write_jsonl(
            overlay_path,
            [
                {
                    "item_id": "Base.ModKit",
                    "layer1_identity_hint": "도구",
                    "layer2_anchor_hint": None,
                    "layer4_context_hint": "총기 개조 작업",
                }
            ],
        )

        rendered = build_rendered(
            facts_path,
            decisions_path,
            profiles_path,
            output_path,
            overlay_path,
            style_log_path,
            None,
            identity_rules_path,
            precedence_rules_path,
            compose_context=STAGING_COMPOSE_CONTEXT,
        )

        entry = rendered["entries"]["Base.ModKit"]
        self.assertEqual(entry["source"], "composed_v2_preview")
        self.assertEqual(entry["resolved_profile"], "material_body")
        self.assertEqual(entry["resolution_source"], "selected_role_precedence")
        self.assertEqual(entry["coverage_quality_candidate"], "strong")
        self.assertEqual(
            entry["text_ko"],
            "도구다.\n\n총기 개조 작업 맥락에서 쓰인다.\n\n총기 개조 작업에 들어가는 부품이다.\n\n총포상과 작업대 주변에서 발견된다.",
        )
        self.assertEqual(
            entry["body_plan"]["emitted_section_names"],
            ["identity_core", "context_support", "use_core", "acquisition_support"],
        )
        self.assertEqual(entry["body_plan"]["missing_required_sections"], [])
        self.assertEqual(
            rendered["meta"]["stats"]["resolution_source_counts"],
            {"selected_role_precedence": 1},
        )

    def test_default_entrypoint_mode_resolves_body_plan_profiles(self) -> None:
        args = parse_args([])
        paths = resolve_entrypoint_paths(args)

        self.assertEqual(args.mode, DEFAULT_MODE)
        self.assertEqual(paths["profiles_path"].name, "compose_profiles_v2.json")
        self.assertIsNone(paths["output_path"])
        self.assertIsNone(paths["style_log_path"])

    def test_default_entrypoint_rejects_legacy_profiles(self) -> None:
        legacy_profiles_path = self.tmp_dir / "legacy_profiles.json"
        write_json(
            legacy_profiles_path,
            {
                "interaction_tool": {
                    "sentence_plan": [
                        {"template": "{identity_hint}다."},
                    ],
                },
            },
        )

        with self.assertRaisesRegex(ValueError, "default mode requires compose_profiles_v2"):
            compose_main(
                [
                    "--profiles-path",
                    str(legacy_profiles_path),
                    "--output-path",
                    str(self.tmp_dir / "rendered.json"),
                    "--style-log-path",
                    str(self.tmp_dir / "style_log.jsonl"),
                ]
            )

    def test_default_entrypoint_rejects_legacy_runtime_state(self) -> None:
        facts_path = self.tmp_dir / "legacy_state_facts.jsonl"
        decisions_path = self.tmp_dir / "legacy_state_decisions.jsonl"
        overlay_path = self.tmp_dir / "legacy_state_overlay.jsonl"
        output_path = self.tmp_dir / "legacy_state_rendered.json"
        style_log_path = self.tmp_dir / "legacy_state_style_log.jsonl"
        profiles_path, identity_rules_path, precedence_rules_path = self.write_shared_inputs()

        write_jsonl(
            facts_path,
            [
                {
                    "item_id": "Base.LegacyState",
                    "identity_hint": "도구",
                    "primary_use": "테스트 도구다",
                    "acquisition_hint": None,
                    "processing_hint": None,
                    "special_context": None,
                    "limitation_hint": None,
                    "notes": None,
                    "fact_origin": {"primary_use": ["test"]},
                }
            ],
        )
        write_jsonl(
            decisions_path,
            [
                {
                    "item_id": "Base.LegacyState",
                    "state": "active",
                    "compose_profile": "tool_body",
                    "override_mode": "none",
                    "selected_role": "tool",
                    "selected_cluster": None,
                }
            ],
        )
        write_jsonl(overlay_path, [])

        with self.assertRaisesRegex(ValueError, DEFAULT_LEGACY_RUNTIME_STATE_ERROR_CODE):
            build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                output_path,
                overlay_path,
                style_log_path,
                None,
                identity_rules_path,
                precedence_rules_path,
                compose_context=STAGING_COMPOSE_CONTEXT,
            )

    def test_diagnostic_resolver_allows_legacy_runtime_state_alias(self) -> None:
        facts_path = self.tmp_dir / "diagnostic_legacy_state_facts.jsonl"
        decisions_path = self.tmp_dir / "diagnostic_legacy_state_decisions.jsonl"
        overlay_path = self.tmp_dir / "diagnostic_legacy_state_overlay.jsonl"
        output_path = self.tmp_dir / "diagnostic_legacy_state_rendered.json"
        style_log_path = self.tmp_dir / "diagnostic_legacy_state_style_log.jsonl"
        profiles_path, identity_rules_path, precedence_rules_path = self.write_shared_inputs()

        write_jsonl(
            facts_path,
            [
                {
                    "item_id": "Base.LegacySilentState",
                    "identity_hint": "재료",
                    "primary_use": "진단용 재료다",
                    "acquisition_hint": None,
                    "processing_hint": None,
                    "special_context": None,
                    "limitation_hint": None,
                    "notes": None,
                    "fact_origin": {"primary_use": ["test"]},
                }
            ],
        )
        write_jsonl(
            decisions_path,
            [
                {
                    "item_id": "Base.LegacySilentState",
                    "state": "silent",
                    "compose_profile": "material_body",
                    "override_mode": "none",
                    "selected_role": "material",
                    "selected_cluster": None,
                }
            ],
        )
        write_jsonl(overlay_path, [])

        rendered = build_rendered(
            facts_path,
            decisions_path,
            profiles_path,
            output_path,
            overlay_path,
            style_log_path,
            None,
            identity_rules_path,
            precedence_rules_path,  # DVF_AUTHORITY_ROLE_MIGRATION[c3141d75308dcae56d0e58d279669429]
            resolver_authority_mode=DIAGNOSTIC_RESOLVER_AUTHORITY_MODE,
            compose_context=DIAGNOSTIC_COMPOSE_CONTEXT,
        )

        self.assertEqual(rendered["entries"]["Base.LegacySilentState"]["source"], "unadopted")

    def test_default_resolver_uses_body_plan_for_legacy_label_mapping(self) -> None:
        facts_path = self.tmp_dir / "entrypoint_facts.jsonl"
        decisions_path = self.tmp_dir / "entrypoint_decisions.jsonl"
        overlay_path = self.tmp_dir / "entrypoint_overlay.jsonl"
        output_path = self.tmp_dir / "entrypoint_rendered.json"
        style_log_path = self.tmp_dir / "entrypoint_style_log.jsonl"
        profiles_path, identity_rules_path, precedence_rules_path = self.write_shared_inputs()

        write_jsonl(
            facts_path,
            [
                {
                    "item_id": "Base.LegacyMappedPart",
                    "identity_hint": "재료",
                    "primary_use": "수리 작업에 쓰는 부품이다",
                    "acquisition_hint": "창고에서 발견된다",
                    "processing_hint": None,
                    "special_context": None,
                    "limitation_hint": None,
                    "notes": None,
                    "fact_origin": {"primary_use": ["cluster_summary"]},
                }
            ],
        )
        write_jsonl(
            decisions_path,
            [
                {
                    "item_id": "Base.LegacyMappedPart",
                    "state": "adopted",
                    "compose_profile": "interaction_component",
                    "override_mode": "none",
                    "selected_role": None,
                    "selected_cluster": "repair",
                }
            ],
        )
        write_jsonl(
            overlay_path,
            [
                {
                    "item_id": "Base.LegacyMappedPart",
                    "layer1_identity_hint": "재료",
                    "layer2_anchor_hint": None,
                    "layer4_context_hint": "수리 작업",
                }
            ],
        )

        rendered = build_rendered(
            facts_path,
            decisions_path,
            profiles_path,
            output_path,
            overlay_path,
            style_log_path,
            None,
            identity_rules_path,
            precedence_rules_path,
            compose_context=STAGING_COMPOSE_CONTEXT,
        )

        entry = rendered["entries"]["Base.LegacyMappedPart"]
        self.assertEqual(entry["source"], "composed_v2_preview")
        self.assertEqual(entry["resolved_profile"], "material_body")
        self.assertIn("body_plan", entry)
        self.assertNotIn("quality_flag", entry)

    def test_default_resolver_rejects_named_legacy_compat_labels(self) -> None:
        cases = {
            "interaction_tool": ("Base.interaction_tool", "interaction_tool"),
            "interaction_component": ("Base.interaction_component", "interaction_component"),
            "interaction_output": ("Base.interaction_output", "interaction_output"),
            "malformed": ("Base.MalformedLegacy", "interaction_tool:malformed"),
        }
        for case_id, (item_id, compose_profile) in cases.items():
            with self.subTest(case_id=case_id):
                with self.assertRaisesRegex(ValueError, DEFAULT_LEGACY_COMPAT_LABEL_ERROR_CODE):
                    resolve_body_profile(
                        facts={"item_id": item_id, "identity_hint": "미분류"},
                        decision={
                            "item_id": item_id,
                            "compose_profile": compose_profile,
                            "selected_role": None,
                        },
                        identity_hint_target_map={},
                        precedence_rules={},
                    )

    def test_diagnostic_resolver_allows_explicit_legacy_mapping(self) -> None:
        resolved_profile, resolution_source, trace = resolve_body_profile(
            facts={"item_id": "Base.LegacyDiagnostic", "identity_hint": "미분류"},
            decision={
                "item_id": "Base.LegacyDiagnostic",
                "compose_profile": "interaction_component",
                "selected_role": None,
            },
            identity_hint_target_map={},
            precedence_rules={},
            resolver_authority_mode=DIAGNOSTIC_RESOLVER_AUTHORITY_MODE,
        )

        self.assertEqual(resolved_profile, "material_body")
        self.assertEqual(resolution_source, "legacy_fallback_target")
        self.assertEqual(trace["legacy_fallback_target"], "material_body")

    def test_default_entrypoint_rejects_legacy_fallback_row(self) -> None:
        facts_path = self.tmp_dir / "legacy_fallback_facts.jsonl"
        decisions_path = self.tmp_dir / "legacy_fallback_decisions.jsonl"
        overlay_path = self.tmp_dir / "legacy_fallback_overlay.jsonl"
        output_path = self.tmp_dir / "legacy_fallback_rendered.json"
        style_log_path = self.tmp_dir / "legacy_fallback_style_log.jsonl"
        profiles_path, identity_rules_path, precedence_rules_path = self.write_shared_inputs()

        write_jsonl(
            facts_path,
            [
                {
                    "item_id": "Base.LegacyFallbackOnly",
                    "identity_hint": "미분류",
                    "primary_use": "legacy fallback probe",
                    "acquisition_hint": None,
                    "processing_hint": None,
                    "special_context": None,
                    "limitation_hint": None,
                    "notes": None,
                    "fact_origin": {"primary_use": ["test"]},
                }
            ],
        )
        write_jsonl(
            decisions_path,
            [
                {
                    "item_id": "Base.LegacyFallbackOnly",
                    "state": "adopted",
                    "compose_profile": "interaction_tool",
                    "override_mode": "none",
                    "selected_role": None,
                    "selected_cluster": None,
                }
            ],
        )
        write_jsonl(
            overlay_path,
            [
                {
                    "item_id": "Base.LegacyFallbackOnly",
                    "layer1_identity_hint": "미분류",
                    "layer2_anchor_hint": None,
                    "layer4_context_hint": None,
                }
            ],
        )

        with self.assertRaisesRegex(ValueError, DEFAULT_LEGACY_COMPAT_LABEL_ERROR_CODE):
            build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                output_path,
                overlay_path,
                style_log_path,
                None,
                identity_rules_path,
                precedence_rules_path,
                compose_context=STAGING_COMPOSE_CONTEXT,
            )

    def test_legacy_adapter_entrypoint_modes_are_removed(self) -> None:
        self.assertNotIn("compat_legacy", ENTRYPOINT_MODES)
        self.assertNotIn("diagnostic_legacy", ENTRYPOINT_MODES)
        for legacy_mode in ("compat_legacy", "diagnostic_legacy"):
            with self.subTest(legacy_mode=legacy_mode):
                with self.assertRaises(SystemExit):
                    with redirect_stderr(StringIO()):
                        parse_args(["--mode", legacy_mode])

    def test_diagnostic_resolver_requires_all_external_outputs(self) -> None:
        args = [
            "--mode",
            DIAGNOSTIC_RESOLVER_MODE,
            "--output-path",
            str(self.tmp_dir / "diagnostic_resolver_rendered.json"),
        ]

        with self.assertRaisesRegex(ValueError, "COMPOSE_EXTERNAL_OUTPUT_REQUIRED"):
            compose_main(args)

    def test_direct_diagnostic_resolver_rejects_canonical_output_path(self) -> None:
        profiles_path, identity_rules_path, precedence_rules_path = self.write_shared_inputs()

        with self.assertRaisesRegex(
            ValueError,
            "diagnostic resolver output_path must not write under canonical",
        ):
            build_rendered(
                self.tmp_dir / "facts.jsonl",
                self.tmp_dir / "decisions.jsonl",
                profiles_path,
                ROOT / "output" / "diagnostic_resolver_rendered.json",
                self.tmp_dir / "overlay.jsonl",
                self.tmp_dir / "style_log.jsonl",
                None,
                identity_rules_path,
                precedence_rules_path,
                DIAGNOSTIC_RESOLVER_AUTHORITY_MODE,
                compose_context=DIAGNOSTIC_COMPOSE_CONTEXT,
            )

    def test_v2_missing_required_context_section_stays_weak_without_context_fallback(self) -> None:
        facts_path = self.tmp_dir / "facts.jsonl"
        decisions_path = self.tmp_dir / "decisions.jsonl"
        overlay_path = self.tmp_dir / "overlay.jsonl"
        output_path = self.tmp_dir / "rendered.json"
        style_log_path = self.tmp_dir / "style_log.jsonl"
        profiles_path, identity_rules_path, precedence_rules_path = self.write_shared_inputs()

        write_jsonl(
            facts_path,
            [
                {
                    "item_id": "Base.LoosePowder",
                    "identity_hint": "재료",
                    "primary_use": "탄약용 화약 재료다",
                    "acquisition_hint": "재장전 관련 보관함에서 발견된다",
                    "processing_hint": None,
                    "special_context": None,
                    "limitation_hint": None,
                    "notes": None,
                    "fact_origin": {"primary_use": ["cluster_summary"]},
                }
            ],
        )
        write_jsonl(
            decisions_path,
            [
                {
                    "item_id": "Base.LoosePowder",
                    "state": "adopted",
                    "compose_profile": "interaction_component",
                    "override_mode": "none",
                    "selected_role": None,
                    "selected_cluster": "ammo_reloading",
                }
            ],
        )
        write_jsonl(
            overlay_path,
            [
                {
                    "item_id": "Base.LoosePowder",
                    "layer1_identity_hint": "재료",
                    "layer2_anchor_hint": None,
                    "layer4_context_hint": None,
                }
            ],
        )

        rendered = build_rendered(
            facts_path,
            decisions_path,
            profiles_path,
            output_path,
            overlay_path,
            style_log_path,
            None,
            identity_rules_path,
            precedence_rules_path,
            compose_context=STAGING_COMPOSE_CONTEXT,
        )

        entry = rendered["entries"]["Base.LoosePowder"]
        self.assertEqual(entry["resolved_profile"], "material_body")
        self.assertEqual(entry["resolution_source"], "identity_family_target")
        self.assertEqual(entry["coverage_quality_candidate"], "weak")
        self.assertEqual(
            entry["text_ko"],
            "재료다.\n\n탄약용 화약 재료다.\n\n재장전 관련 보관함에서 발견된다.",
        )
        self.assertEqual(
            entry["body_plan"]["emitted_section_names"],
            ["identity_core", "use_core", "acquisition_support"],
        )
        self.assertEqual(entry["body_plan"]["missing_required_sections"], ["context_support"])
        self.assertEqual(
            rendered["meta"]["stats"]["missing_required_section_counts"],
            {"context_support": 1},
        )

    def test_v2_optional_context_is_suppressed_when_primary_use_already_covers_it(self) -> None:
        facts_path = self.tmp_dir / "facts.jsonl"
        decisions_path = self.tmp_dir / "decisions.jsonl"
        overlay_path = self.tmp_dir / "overlay.jsonl"
        output_path = self.tmp_dir / "rendered.json"
        style_log_path = self.tmp_dir / "style_log.jsonl"
        profiles_path, identity_rules_path, precedence_rules_path = self.write_shared_inputs()

        write_jsonl(
            facts_path,
            [
                {
                    "item_id": "Base.Tongs",
                    "identity_hint": "도구",
                    "primary_use": "금속 단조 작업에 쓰는 도구다",
                    "acquisition_hint": "대장간에서 발견된다",
                    "processing_hint": None,
                    "special_context": None,
                    "limitation_hint": None,
                    "notes": None,
                    "fact_origin": {"primary_use": ["cluster_summary"]},
                }
            ],
        )
        write_jsonl(
            decisions_path,
            [
                {
                    "item_id": "Base.Tongs",
                    "state": "adopted",
                    "compose_profile": "interaction_tool",
                    "override_mode": "none",
                    "selected_role": "tool",
                    "selected_cluster": "metalwork_anvil",
                }
            ],
        )
        write_jsonl(
            overlay_path,
            [
                {
                    "item_id": "Base.Tongs",
                    "layer1_identity_hint": "도구",
                    "layer2_anchor_hint": None,
                    "layer4_context_hint": "금속 단조 작업",
                }
            ],
        )

        rendered = build_rendered(
            facts_path,
            decisions_path,
            profiles_path,
            output_path,
            overlay_path,
            style_log_path,
            None,
            identity_rules_path,
            precedence_rules_path,
            compose_context=STAGING_COMPOSE_CONTEXT,
        )

        entry = rendered["entries"]["Base.Tongs"]
        self.assertEqual(entry["resolved_profile"], "tool_body")
        self.assertEqual(entry["resolution_source"], "identity_role_aligned")
        self.assertEqual(entry["coverage_quality_candidate"], "strong")
        self.assertEqual(
            entry["text_ko"],
            "도구다.\n\n금속 단조 작업에 쓰는 도구다.\n\n대장간에서 발견된다.",
        )
        self.assertEqual(
            entry["body_plan"]["emitted_section_names"],
            ["identity_core", "use_core", "acquisition_support"],
        )
        self.assertNotIn("context_support", entry["body_plan"]["emitted_section_names"])


if __name__ == "__main__":
    unittest.main()
