from __future__ import annotations

import json
import shutil
import sys
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.compose_layer3_text import (
    DEFAULT_MODE,
    ENTRYPOINT_MODES,
    DIAGNOSTIC_RESOLVER_MODE,
    build_rendered,
    main as compose_main,
    parse_args,
    resolve_entrypoint_paths,
)
from tools.build.compose_layer3_body_profile import (
    DEFAULT_LEGACY_COMPAT_LABEL_ERROR_CODE,
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


class ComposeLayer3TextV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = ROOT / "tests" / "_tmp_compose_v2"
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
                    "state": "active",
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

    def test_default_entrypoint_uses_body_plan_for_legacy_label_mapping(self) -> None:
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
                    "state": "active",
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

        result = compose_main(
            [
                "--facts-path",
                str(facts_path),
                "--decisions-path",
                str(decisions_path),
                "--profiles-path",
                str(profiles_path),
                "--output-path",
                str(output_path),
                "--overlay-path",
                str(overlay_path),
                "--style-log-path",
                str(style_log_path),
                "--identity-rules-path",
                str(identity_rules_path),
                "--precedence-rules-path",
                str(precedence_rules_path),
            ]
        )

        self.assertEqual(result, 0)
        rendered = json.loads(output_path.read_text(encoding="utf-8"))
        entry = rendered["entries"]["Base.LegacyMappedPart"]
        self.assertEqual(entry["source"], "composed_v2_preview")
        self.assertEqual(entry["resolved_profile"], "material_body")
        self.assertIn("body_plan", entry)
        self.assertNotIn("quality_flag", entry)

    def test_default_resolver_rejects_legacy_compat_fallback_labels(self) -> None:
        for legacy_label in ("interaction_tool", "interaction_component", "interaction_output"):
            with self.subTest(legacy_label=legacy_label):
                with self.assertRaisesRegex(ValueError, DEFAULT_LEGACY_COMPAT_LABEL_ERROR_CODE):
                    resolve_body_profile(
                        facts={"item_id": f"Base.{legacy_label}", "identity_hint": "미분류"},
                        decision={
                            "item_id": f"Base.{legacy_label}",
                            "compose_profile": legacy_label,
                            "selected_role": None,
                        },
                        identity_hint_target_map={},
                        precedence_rules={},
                    )

    def test_default_resolver_rejects_malformed_legacy_compat_label(self) -> None:
        with self.assertRaisesRegex(ValueError, DEFAULT_LEGACY_COMPAT_LABEL_ERROR_CODE):
            resolve_body_profile(
                facts={"item_id": "Base.MalformedLegacy", "identity_hint": "미분류"},
                decision={
                    "item_id": "Base.MalformedLegacy",
                    "compose_profile": "interaction_tool:malformed",
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
                    "state": "active",
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
            compose_main(
                [
                    "--facts-path",
                    str(facts_path),
                    "--decisions-path",
                    str(decisions_path),
                    "--profiles-path",
                    str(profiles_path),
                    "--output-path",
                    str(output_path),
                    "--overlay-path",
                    str(overlay_path),
                    "--style-log-path",
                    str(style_log_path),
                    "--identity-rules-path",
                    str(identity_rules_path),
                    "--precedence-rules-path",
                    str(precedence_rules_path),
                ]
            )

    def test_legacy_adapter_entrypoint_modes_are_removed(self) -> None:
        self.assertNotIn("compat_legacy", ENTRYPOINT_MODES)
        self.assertNotIn("diagnostic_legacy", ENTRYPOINT_MODES)
        for legacy_mode in ("compat_legacy", "diagnostic_legacy"):
            with self.subTest(legacy_mode=legacy_mode):
                with self.assertRaises(SystemExit):
                    with redirect_stderr(StringIO()):
                        parse_args(["--mode", legacy_mode])

    def test_diagnostic_resolver_rejects_canonical_output_path(self) -> None:
        args = [
            "--mode",
            DIAGNOSTIC_RESOLVER_MODE,
            "--output-path",
            str(self.tmp_dir / "diagnostic_resolver_rendered.json"),
        ]

        with self.assertRaisesRegex(ValueError, "diagnostic_resolver output_path must stay under"):
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
                    "state": "active",
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
                    "state": "active",
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
