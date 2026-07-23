from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.compose_layer3_text import HISTORICAL_COMPOSE_CONTEXT, build_rendered


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


class ComposeLayer3TextOverlayTest(unittest.TestCase):
    def test_build_rendered_applies_quality_flag_from_overlay(self) -> None:
        tmp_dir = ROOT / "tests" / "_tmp_compose_overlay"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            facts_path = tmp_dir / "facts.jsonl"
            decisions_path = tmp_dir / "decisions.jsonl"
            profiles_path = tmp_dir / "profiles.json"
            overlay_path = tmp_dir / "overlay.jsonl"
            output_path = tmp_dir / "rendered.json"
            style_log_path = tmp_dir / "style_log.jsonl"
            requeue_candidates_path = tmp_dir / "requeue.jsonl"

            write_jsonl(
                facts_path,
                [
                    {
                        "item_id": "Base.Tool",
                        "identity_hint": "도구",
                        "acquisition_hint": "작업장 주변에서 발견된다",
                        "primary_use": "수리 작업에 쓰는 도구다",
                        "secondary_use": None,
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
                        "item_id": "Base.Tool",
                        "state": "active",
                        "compose_profile": "interaction_tool",
                        "override_mode": "none",
                        "selected_cluster": "tool_kit",
                    }
                ],
            )
            write_jsonl(
                overlay_path,
                [
                    {
                        "item_id": "Base.Tool",
                        "layer3_role_check": "FUNCTION_NARROW",
                        "representative_slot": "primary_use",
                        "body_slot_hints": {
                            "secondary_use_present": False,
                            "distinctive_mechanic_present": False,
                            "acquisition_should_trail": True,
                            "item_specific_cue_required": True,
                        },
                        "representative_slot_override": False,
                    }
                ],
            )
            profiles_path.write_text(
                json.dumps(
                    {
                        "interaction_tool": {
                            "sentence_plan": [
                                {"slots": ["identity_hint"], "required": True, "template": "{identity_hint}."},
                                {"slots": ["primary_use"], "required": True, "template": "{primary_use}."},
                                {"slots": ["acquisition_hint"], "required": False, "template": "{acquisition_hint}."},
                            ]
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            rendered = build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                output_path,
                overlay_path,
                style_log_path,
                requeue_candidates_path,
                compose_context=HISTORICAL_COMPOSE_CONTEXT,
            )

            entry = rendered["entries"]["Base.Tool"]
            requeue_rows = [
                json.loads(line)
                for line in requeue_candidates_path.read_text(encoding="utf-8").splitlines()
                if line
            ]
            self.assertEqual(entry["text_ko"], "도구. 수리 작업에 쓰는 도구다. 작업장 주변에서 발견된다.")
            self.assertEqual(entry["quality_flag"], "function_narrow")
            self.assertEqual(rendered["meta"]["stats"]["quality_flagged"], 1)
            self.assertEqual(rendered["meta"]["stats"]["requeue_candidates"], 1)
            self.assertEqual(rendered["meta"]["overlay_path"], str(overlay_path))
            self.assertEqual(
                requeue_rows,
                [
                    {
                        "item_id": "Base.Tool",
                        "layer3_role_check": "FUNCTION_NARROW",
                        "quality_flag": "function_narrow",
                        "requeue_reason": "NEEDS_CLUSTER_REDESIGN",
                    }
                ],
            )
        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)

    def test_acq_dominant_sets_flag_only_when_reordered(self) -> None:
        tmp_dir = ROOT / "tests" / "_tmp_compose_overlay_acq"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            facts_path = tmp_dir / "facts.jsonl"
            decisions_path = tmp_dir / "decisions.jsonl"
            profiles_path = tmp_dir / "profiles.json"
            overlay_path = tmp_dir / "overlay.jsonl"
            output_path = tmp_dir / "rendered.json"
            style_log_path = tmp_dir / "style_log.jsonl"
            requeue_candidates_path = tmp_dir / "requeue.jsonl"

            write_jsonl(
                facts_path,
                [
                    {
                        "item_id": "Base.Acq",
                        "identity_hint": "재료",
                        "acquisition_hint": "보관함에서 발견된다",
                        "primary_use": "조립 작업에 들어가는 재료다",
                        "secondary_use": None,
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
                        "item_id": "Base.Acq",
                        "state": "active",
                        "compose_profile": "interaction_tool",
                        "override_mode": "none",
                        "selected_cluster": "assembly",
                    }
                ],
            )
            write_jsonl(
                overlay_path,
                [
                    {
                        "item_id": "Base.Acq",
                        "layer3_role_check": "ACQ_DOMINANT",
                        "representative_slot": "primary_use",
                        "body_slot_hints": {
                            "secondary_use_present": False,
                            "distinctive_mechanic_present": False,
                            "acquisition_should_trail": True,
                            "item_specific_cue_required": False,
                        },
                        "representative_slot_override": False,
                    }
                ],
            )
            profiles_path.write_text(
                json.dumps(
                    {
                        "interaction_tool": {
                            "sentence_plan": [
                                {"slots": ["acquisition_hint"], "required": False, "template": "{acquisition_hint}."},
                                {"slots": ["identity_hint"], "required": True, "template": "{identity_hint}."},
                                {"slots": ["primary_use"], "required": True, "template": "{primary_use}."},
                            ]
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            rendered = build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                output_path,
                overlay_path,
                style_log_path,
                requeue_candidates_path,
                compose_context=HISTORICAL_COMPOSE_CONTEXT,
            )

            entry = rendered["entries"]["Base.Acq"]
            requeue_rows = [
                json.loads(line)
                for line in requeue_candidates_path.read_text(encoding="utf-8").splitlines()
                if line
            ]
            self.assertEqual(entry["text_ko"], "재료. 조립 작업에 들어가는 재료다. 보관함에서 발견된다.")
            self.assertEqual(entry["quality_flag"], "acq_dominant_reordered")
            self.assertEqual(
                requeue_rows,
                [
                    {
                        "item_id": "Base.Acq",
                        "layer3_role_check": "ACQ_DOMINANT",
                        "quality_flag": "acq_dominant_reordered",
                        "requeue_reason": "NEEDS_COMPOSE_TUNING",
                    }
                ],
            )
        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)

    def test_representative_override_promotes_primary_and_drops_conflicting_identity(self) -> None:
        tmp_dir = ROOT / "tests" / "_tmp_compose_overlay_representative_override"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            facts_path = tmp_dir / "facts.jsonl"
            decisions_path = tmp_dir / "decisions.jsonl"
            profiles_path = tmp_dir / "profiles.json"
            overlay_path = tmp_dir / "overlay.jsonl"
            output_path = tmp_dir / "rendered.json"
            style_log_path = tmp_dir / "style_log.jsonl"
            requeue_candidates_path = tmp_dir / "requeue.jsonl"

            write_jsonl(
                facts_path,
                [
                    {
                        "item_id": "Base.ModKit",
                        "identity_hint": "도구",
                        "acquisition_hint": "총포상과 작업대 주변에서 발견된다",
                        "primary_use": "총기 개조 작업에 들어가는 부품이다",
                        "secondary_use": None,
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
                        "selected_cluster": "gun_modding",
                    }
                ],
            )
            write_jsonl(
                overlay_path,
                [
                    {
                        "item_id": "Base.ModKit",
                        "layer3_role_check": "FUNCTION_NARROW",
                        "representative_slot": "primary_use",
                        "body_slot_hints": {
                            "secondary_use_present": False,
                            "distinctive_mechanic_present": False,
                            "acquisition_should_trail": True,
                            "item_specific_cue_required": True,
                        },
                        "representative_slot_override": True,
                    }
                ],
            )
            profiles_path.write_text(
                json.dumps(
                    {
                        "interaction_component": {
                            "sentence_plan": [
                                {"slots": ["identity_hint"], "required": True, "template": "{identity_hint}."},
                                {"slots": ["primary_use"], "required": True, "template": "{primary_use}."},
                                {"slots": ["acquisition_hint"], "required": False, "template": "{acquisition_hint}."},
                            ]
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            rendered = build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                output_path,
                overlay_path,
                style_log_path,
                compose_context=HISTORICAL_COMPOSE_CONTEXT,
            )

            entry = rendered["entries"]["Base.ModKit"]
            self.assertEqual(entry["text_ko"], "총기 개조 작업에 들어가는 부품이다. 총포상과 작업대 주변에서 발견된다.")
            self.assertEqual(entry["quality_flag"], "function_narrow")
        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)

    def test_strong_function_narrow_repairs_focus_without_quality_flag(self) -> None:
        tmp_dir = ROOT / "tests" / "_tmp_compose_overlay_strong_function_narrow"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            facts_path = tmp_dir / "facts.jsonl"
            decisions_path = tmp_dir / "decisions.jsonl"
            profiles_path = tmp_dir / "profiles.json"
            overlay_path = tmp_dir / "overlay.jsonl"
            output_path = tmp_dir / "rendered.json"
            style_log_path = tmp_dir / "style_log.jsonl"
            requeue_candidates_path = tmp_dir / "requeue.jsonl"

            write_jsonl(
                facts_path,
                [
                    {
                        "item_id": "Base.StrongNarrow",
                        "identity_hint": "도구",
                        "acquisition_hint": "총포상에서 발견된다",
                        "primary_use": "총기 개조 작업에 들어가는 부품이다",
                        "secondary_use": None,
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
                        "item_id": "Base.StrongNarrow",
                        "state": "active",
                        "compose_profile": "interaction_component",
                        "override_mode": "none",
                        "selected_cluster": "gun_modding",
                    }
                ],
            )
            write_jsonl(
                overlay_path,
                [
                    {
                        "item_id": "Base.StrongNarrow",
                        "layer3_role_check": "FUNCTION_NARROW",
                        "semantic_quality": "strong",
                        "representative_slot": "primary_use",
                        "body_slot_hints": {
                            "secondary_use_present": False,
                            "distinctive_mechanic_present": False,
                            "acquisition_should_trail": True,
                            "item_specific_cue_required": True,
                        },
                        "representative_slot_override": False,
                    }
                ],
            )
            profiles_path.write_text(
                json.dumps(
                    {
                        "interaction_component": {
                            "sentence_plan": [
                                {"slots": ["identity_hint"], "required": True, "template": "{identity_hint}."},
                                {"slots": ["primary_use"], "required": True, "template": "{primary_use}."},
                                {"slots": ["acquisition_hint"], "required": False, "template": "{acquisition_hint}."},
                            ]
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            rendered = build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                output_path,
                overlay_path,
                style_log_path,
                compose_context=HISTORICAL_COMPOSE_CONTEXT,
            )

            entry = rendered["entries"]["Base.StrongNarrow"]
            self.assertEqual(entry["text_ko"], "총기 개조 작업에 들어가는 부품이다. 총포상에서 발견된다.")
            self.assertNotIn("quality_flag", entry)
        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)

    def test_identity_only_drops_generic_identity_echo(self) -> None:
        tmp_dir = ROOT / "tests" / "_tmp_compose_overlay_identity_only"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            facts_path = tmp_dir / "facts.jsonl"
            decisions_path = tmp_dir / "decisions.jsonl"
            profiles_path = tmp_dir / "profiles.json"
            overlay_path = tmp_dir / "overlay.jsonl"
            output_path = tmp_dir / "rendered.json"
            style_log_path = tmp_dir / "style_log.jsonl"
            requeue_candidates_path = tmp_dir / "requeue.jsonl"

            write_jsonl(
                facts_path,
                [
                    {
                        "item_id": "Base.Identity",
                        "identity_hint": "도구",
                        "acquisition_hint": "창고에서 발견된다",
                        "primary_use": "도구다",
                        "secondary_use": None,
                        "processing_hint": None,
                        "special_context": None,
                        "limitation_hint": None,
                        "notes": None,
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    }
                ],
            )
            write_jsonl(
                decisions_path,
                [
                    {
                        "item_id": "Base.Identity",
                        "state": "active",
                        "compose_profile": "interaction_tool",
                        "override_mode": "none",
                        "selected_cluster": None,
                    }
                ],
            )
            write_jsonl(
                overlay_path,
                [
                    {
                        "item_id": "Base.Identity",
                        "layer3_role_check": "IDENTITY_ONLY",
                        "representative_slot": "identity_hint",
                        "body_slot_hints": {
                            "secondary_use_present": False,
                            "distinctive_mechanic_present": False,
                            "acquisition_should_trail": True,
                            "item_specific_cue_required": True,
                        },
                        "representative_slot_override": False,
                    }
                ],
            )
            profiles_path.write_text(
                json.dumps(
                    {
                        "interaction_tool": {
                            "sentence_plan": [
                                {"slots": ["identity_hint"], "required": True, "template": "{identity_hint}."},
                                {"slots": ["primary_use"], "required": True, "template": "{primary_use}."},
                                {"slots": ["acquisition_hint"], "required": False, "template": "{acquisition_hint}."},
                            ]
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            rendered = build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                output_path,
                overlay_path,
                style_log_path,
                requeue_candidates_path,
                compose_context=HISTORICAL_COMPOSE_CONTEXT,
            )

            entry = rendered["entries"]["Base.Identity"]
            requeue_rows = [
                json.loads(line)
                for line in requeue_candidates_path.read_text(encoding="utf-8").splitlines()
                if line
            ]
            self.assertEqual(entry["text_ko"], "도구. 창고에서 발견된다.")
            self.assertEqual(entry["quality_flag"], "identity_only")
            self.assertEqual(
                requeue_rows,
                [
                    {
                        "item_id": "Base.Identity",
                        "layer3_role_check": "IDENTITY_ONLY",
                        "quality_flag": "identity_only",
                        "requeue_reason": "NEEDS_SOURCE_EXPANSION",
                    }
                ],
            )
        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)

    def test_secondary_and_distinctive_slots_render_between_primary_and_acquisition(self) -> None:
        tmp_dir = ROOT / "tests" / "_tmp_compose_overlay_secondary_distinctive"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            facts_path = tmp_dir / "facts.jsonl"
            decisions_path = tmp_dir / "decisions.jsonl"
            profiles_path = tmp_dir / "profiles.json"
            overlay_path = tmp_dir / "overlay.jsonl"
            output_path = tmp_dir / "rendered.json"
            style_log_path = tmp_dir / "style_log.jsonl"

            write_jsonl(
                facts_path,
                [
                    {
                        "item_id": "Base.Tongs",
                        "identity_hint": "도구",
                        "acquisition_hint": "대장간에서 발견된다",
                        "primary_use": "금속 단조에 쓰는 도구다",
                        "secondary_use": "가열한 재료를 집어 옮길 때도 쓴다",
                        "processing_hint": "가열 후 사용한다",
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
                        "selected_cluster": "metalwork_anvil",
                    }
                ],
            )
            write_jsonl(
                overlay_path,
                [
                    {
                        "item_id": "Base.Tongs",
                        "layer3_role_check": "ADEQUATE",
                        "representative_slot": "primary_use",
                        "body_slot_hints": {
                            "secondary_use_present": True,
                            "distinctive_mechanic_present": True,
                            "acquisition_should_trail": True,
                            "item_specific_cue_required": False,
                        },
                        "representative_slot_override": False,
                    }
                ],
            )
            profiles_path.write_text(
                json.dumps(
                    {
                        "interaction_tool": {
                            "sentence_plan": [
                                {"slots": ["identity_hint"], "required": True, "template": "{identity_hint}."},
                                {"slots": ["primary_use"], "required": True, "template": "{primary_use}."},
                                {"slots": ["secondary_use"], "required": False, "template": "{secondary_use}."},
                                {
                                    "slots": ["distinctive_mechanic_hint"],
                                    "required": False,
                                    "template": "{distinctive_mechanic_hint}.",
                                },
                                {"slots": ["acquisition_hint"], "required": False, "template": "{acquisition_hint}."},
                            ]
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            rendered = build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                output_path,
                overlay_path,
                style_log_path,
                compose_context=HISTORICAL_COMPOSE_CONTEXT,
            )

            entry = rendered["entries"]["Base.Tongs"]
            self.assertEqual(
                entry["text_ko"],
                "도구. 금속 단조에 쓰는 도구다. 가열한 재료를 집어 옮길 때도 쓴다. 가열 후 사용한다. 대장간에서 발견된다.",
            )
            self.assertNotIn("quality_flag", entry)
        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)

    def test_identity_only_suppresses_secondary_and_distinctive_slots(self) -> None:
        tmp_dir = ROOT / "tests" / "_tmp_compose_overlay_identity_only_suppression"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        try:
            facts_path = tmp_dir / "facts.jsonl"
            decisions_path = tmp_dir / "decisions.jsonl"
            profiles_path = tmp_dir / "profiles.json"
            overlay_path = tmp_dir / "overlay.jsonl"
            output_path = tmp_dir / "rendered.json"
            style_log_path = tmp_dir / "style_log.jsonl"

            write_jsonl(
                facts_path,
                [
                    {
                        "item_id": "Base.Identity",
                        "identity_hint": "도구",
                        "acquisition_hint": "창고에서 발견된다",
                        "primary_use": "도구다",
                        "secondary_use": "간단한 수리에 쓰인다",
                        "processing_hint": "가열 후 사용한다",
                        "special_context": None,
                        "limitation_hint": None,
                        "notes": None,
                        "fact_origin": {"primary_use": ["identity_fallback"]},
                    }
                ],
            )
            write_jsonl(
                decisions_path,
                [
                    {
                        "item_id": "Base.Identity",
                        "state": "active",
                        "compose_profile": "interaction_tool",
                        "override_mode": "none",
                        "selected_cluster": None,
                    }
                ],
            )
            write_jsonl(
                overlay_path,
                [
                    {
                        "item_id": "Base.Identity",
                        "layer3_role_check": "IDENTITY_ONLY",
                        "representative_slot": "identity_hint",
                        "body_slot_hints": {
                            "secondary_use_present": True,
                            "distinctive_mechanic_present": True,
                            "acquisition_should_trail": True,
                            "item_specific_cue_required": True,
                        },
                        "representative_slot_override": False,
                    }
                ],
            )
            profiles_path.write_text(
                json.dumps(
                    {
                        "interaction_tool": {
                            "sentence_plan": [
                                {"slots": ["identity_hint"], "required": True, "template": "{identity_hint}."},
                                {"slots": ["primary_use"], "required": True, "template": "{primary_use}."},
                                {"slots": ["secondary_use"], "required": False, "template": "{secondary_use}."},
                                {
                                    "slots": ["distinctive_mechanic_hint"],
                                    "required": False,
                                    "template": "{distinctive_mechanic_hint}.",
                                },
                                {"slots": ["acquisition_hint"], "required": False, "template": "{acquisition_hint}."},
                            ]
                        }
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            rendered = build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                output_path,
                overlay_path,
                style_log_path,
                compose_context=HISTORICAL_COMPOSE_CONTEXT,
            )

            entry = rendered["entries"]["Base.Identity"]
            self.assertEqual(entry["text_ko"], "도구. 창고에서 발견된다.")
            self.assertEqual(entry["quality_flag"], "identity_only")
        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
