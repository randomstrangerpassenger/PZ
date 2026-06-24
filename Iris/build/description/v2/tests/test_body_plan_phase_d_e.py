from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.build_body_plan_v2_runtime_rollout import build_runtime_rollout
from tools.build.report_layer3_body_plan_structural_reclassification import (
    build_reclassification_report,
)
from tools.build.validate_body_plan_full_runtime_regression_gate import (
    build_regression_gate_report,
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


class BodyPlanPhaseDETest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = ROOT / "tests" / "_tmp_body_plan_phase_d_e"
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def test_structural_reclassification_emits_dual_axis_default_summary(self) -> None:
        rendered_path = self.tmp_dir / "rendered.json"
        signal_path = self.tmp_dir / "signals.jsonl"
        profiles_path = self.tmp_dir / "profiles.json"
        output_path = self.tmp_dir / "structural.2105.jsonl"
        summary_path = self.tmp_dir / "structural.2105.summary.json"
        source_summary_path = self.tmp_dir / "source_distribution.json"
        section_summary_path = self.tmp_dir / "section_distribution.json"
        overlap_summary_path = self.tmp_dir / "overlap_distribution.json"
        crosswalk_summary_path = self.tmp_dir / "crosswalk.json"
        artifact_validation_path = self.tmp_dir / "artifact_validation.json"
        legacy_row_output_path = self.tmp_dir / "legacy.2105.jsonl"
        legacy_summary_path = self.tmp_dir / "legacy.summary.json"

        write_json(
            rendered_path,
            {
                "entries": {
                    "Base.Body": {
                        "source": "composed_v2_preview",
                        "resolved_profile": "tool_body",
                        "body_plan": {
                            "emitted_section_names": ["identity_core"],
                            "missing_required_sections": ["use_core"],
                        },
                    },
                    "Base.Layer4": {
                        "source": "composed_v2_preview",
                        "resolved_profile": "tool_body",
                        "body_plan": {
                            "emitted_section_names": ["identity_core", "use_core", "context_support"],
                            "missing_required_sections": [],
                        },
                    },
                }
            },
        )
        write_jsonl(
            signal_path,
            [
                {
                    "item_id": "Base.Body",
                    "violation_type": "none",
                    "violation_flags": ["SECTION_COVERAGE_DEFICIT"],
                },
                {
                    "item_id": "Base.Layer4",
                    "violation_type": "LAYER4_ABSORPTION",
                    "violation_flags": ["INTERACTION_LIST_DUPLICATION"],
                },
            ],
        )
        write_json(
            profiles_path,
            {
                "profiles": {
                    "tool_body": {
                        "required_sections": ["identity_core", "use_core"],
                        "adequate_minimum_any_of": [["identity_core", "use_core"]],
                    }
                }
            },
        )

        summary = build_reclassification_report(
            rendered_path=rendered_path,
            surface_signal_path=signal_path,
            profiles_path=profiles_path,
            output_path=output_path,
            summary_path=summary_path,
            source_summary_path=source_summary_path,
            section_summary_path=section_summary_path,
            overlap_summary_path=overlap_summary_path,
            crosswalk_summary_path=crosswalk_summary_path,
            artifact_validation_path=artifact_validation_path,
            legacy_row_output_path=legacy_row_output_path,
            legacy_summary_path=legacy_summary_path,
        )

        rows = [
            json.loads(line)
            for line in output_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        by_item = {row["row_id"]: row for row in rows}
        self.assertEqual(
            by_item["Base.Body"]["source_signal_primary"],
            "none",
        )
        self.assertEqual(
            by_item["Base.Body"]["section_signal_primary"],
            "SECTION_IDENTITY_ONLY",
        )
        self.assertEqual(by_item["Base.Body"]["signal_overlap_state"], "section_only")
        self.assertEqual(by_item["Base.Layer4"]["source_signal_primary"], "LAYER4_ABSORPTION")
        self.assertEqual(by_item["Base.Layer4"]["section_signal_primary"], "SECTION_LAYER4_ABSORPTION")
        self.assertEqual(by_item["Base.Layer4"]["signal_overlap_state"], "coexist")
        self.assertEqual(summary["current_read_model"], "dual_axis_canonical")
        self.assertEqual(summary["hard_block_candidate_count"], 1)
        self.assertEqual(
            summary["legacy_compat_summary"]["legacy_family_reclassification_counts"],
            {"IDENTITY_ONLY": 1, "LAYER4_ABSORPTION": 1},
        )
        self.assertEqual(
            summary["linked_artifacts"]["source_distribution"],
            str(source_summary_path),
        )
        self.assertFalse(legacy_row_output_path.exists())
        self.assertFalse(legacy_summary_path.exists())

        artifact_validation = json.loads(artifact_validation_path.read_text(encoding="utf-8"))
        self.assertEqual(artifact_validation["overall_status"], "pass")

    def test_structural_reclassification_can_emit_explicit_legacy_view(self) -> None:
        rendered_path = self.tmp_dir / "rendered.json"
        signal_path = self.tmp_dir / "signals.jsonl"
        profiles_path = self.tmp_dir / "profiles.json"
        output_path = self.tmp_dir / "structural.2105.jsonl"
        summary_path = self.tmp_dir / "structural.2105.summary.json"
        source_summary_path = self.tmp_dir / "source_distribution.json"
        section_summary_path = self.tmp_dir / "section_distribution.json"
        overlap_summary_path = self.tmp_dir / "overlap_distribution.json"
        crosswalk_summary_path = self.tmp_dir / "crosswalk.json"
        artifact_validation_path = self.tmp_dir / "artifact_validation.json"
        legacy_row_output_path = self.tmp_dir / "legacy.2105.jsonl"
        legacy_summary_path = self.tmp_dir / "legacy.summary.json"

        write_json(
            rendered_path,
            {
                "entries": {
                    "Base.Legacy": {
                        "source": "composed_v2_preview",
                        "resolved_profile": "tool_body",
                        "body_plan": {
                            "emitted_section_names": ["identity_core", "use_core"],
                            "missing_required_sections": [],
                        },
                    }
                }
            },
        )
        write_jsonl(
            signal_path,
            [
                {
                    "item_id": "Base.Legacy",
                    "violation_type": "BODY_LACKS_ITEM_SPECIFIC_USE",
                    "violation_flags": [],
                }
            ],
        )
        write_json(
            profiles_path,
            {
                "profiles": {
                    "tool_body": {
                        "required_sections": ["identity_core", "use_core"],
                        "adequate_minimum_any_of": [["identity_core", "use_core"]],
                    }
                }
            },
        )

        summary = build_reclassification_report(
            rendered_path=rendered_path,
            surface_signal_path=signal_path,
            profiles_path=profiles_path,
            output_path=output_path,
            summary_path=summary_path,
            source_summary_path=source_summary_path,
            section_summary_path=section_summary_path,
            overlap_summary_path=overlap_summary_path,
            crosswalk_summary_path=crosswalk_summary_path,
            artifact_validation_path=artifact_validation_path,
            emit_legacy_view=True,
            legacy_row_output_path=legacy_row_output_path,
            legacy_summary_path=legacy_summary_path,
        )

        self.assertTrue(legacy_row_output_path.exists())
        self.assertTrue(legacy_summary_path.exists())
        self.assertEqual(
            summary["legacy_compat_summary"]["diagnostic_artifact_refs"]["legacy_row_output_path"],
            str(legacy_row_output_path),
        )
        legacy_rows = [
            json.loads(line)
            for line in legacy_row_output_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(legacy_rows[0]["legacy_family_reclassification"], "FUNCTION_NARROW")

    def test_regression_gate_passes_when_all_component_gates_are_green(self) -> None:
        rendered_summary_path = self.tmp_dir / "rendered.summary.json"
        quality_summary_path = self.tmp_dir / "quality.summary.json"
        delta_summary_path = self.tmp_dir / "delta.summary.json"
        blocker_summary_path = self.tmp_dir / "blockers.summary.json"
        determinism_path = self.tmp_dir / "determinism.json"
        legacy_diff_path = self.tmp_dir / "legacy_diff.json"
        structural_summary_path = self.tmp_dir / "structural.summary.json"
        output_path = self.tmp_dir / "gate.json"

        write_json(rendered_summary_path, {"row_count": 2, "silent_count": 1})
        write_json(
            quality_summary_path,
            {
                "runtime_state_counts": {"active": 1, "silent": 1},
                "quality_state_counts": {"strong": 1},
                "publish_state_counts": {"exposed": 1},
            },
        )
        write_json(
            delta_summary_path,
            {
                "row_count": 2,
                "delta_classification_counts": {"expected_delta": 1, "no_delta": 1},
                "unexpected_reason_counts": {},
                "publish_transition_counts": {},
            },
        )
        write_json(blocker_summary_path, {"blocker_count": 0})
        write_json(determinism_path, {"overall_pass": True})
        write_json(legacy_diff_path, {"accidental_change_count": 0})
        write_json(
            structural_summary_path,
            {
                "row_count": 2,
                "writer_role": "observer_only",
                "hard_block_candidate_count": 0,
                "legacy_compat_summary": {
                    "legacy_family_reclassification_counts": {"none": 2},
                },
            },
        )

        report = build_regression_gate_report(
            rendered_summary_path=rendered_summary_path,
            quality_summary_path=quality_summary_path,
            delta_summary_path=delta_summary_path,
            blocker_summary_path=blocker_summary_path,
            determinism_report_path=determinism_path,
            legacy_diff_report_path=legacy_diff_path,
            structural_reclassification_summary_path=structural_summary_path,
            output_path=output_path,
            enforce_current_baseline=False,
        )

        self.assertEqual(report["overall_status"], "pass")
        self.assertFalse(report["failures"])

    def test_runtime_rollout_exports_lua_that_matches_staged_payload(self) -> None:
        rendered_path = self.tmp_dir / "rendered.json"
        publish_path = self.tmp_dir / "publish.jsonl"
        gate_path = self.tmp_dir / "gate.json"
        lua_path = self.tmp_dir / "IrisLayer3Data.lua"
        bridge_report_path = self.tmp_dir / "bridge.json"
        runtime_report_path = self.tmp_dir / "runtime.json"
        rollout_report_path = self.tmp_dir / "rollout.json"

        write_json(
            rendered_path,
            {
                "meta": {"stats": {"total": 1}},
                "entries": {
                    "Base.Sample": {
                        "text_ko": "샘플 도구다.",
                        "source": "composed_v2_preview",
                    }
                },
            },
        )
        write_jsonl(
            publish_path,
            [
                {
                    "item_id": "Base.Sample",
                    "publish_state": "exposed",
                }
            ],
        )
        write_json(gate_path, {"overall_status": "pass"})

        report = build_runtime_rollout(
            rendered_path=rendered_path,
            publish_preview_path=publish_path,
            regression_gate_path=gate_path,
            staged_lua_output_path=None,
            lua_output_path=lua_path,
            bridge_report_path=bridge_report_path,
            runtime_report_path=runtime_report_path,
            rollout_report_path=rollout_report_path,
        )

        self.assertEqual(report["overall_status"], "pass")
        chunk_manifest_path = lua_path.parent / "IrisLayer3DataChunks.lua"
        chunk_dir = lua_path.parent / "IrisLayer3DataChunks"
        self.assertFalse(lua_path.exists())
        self.assertTrue(chunk_manifest_path.exists())
        self.assertIn("IrisLayer3Data = data", chunk_manifest_path.read_text(encoding="utf-8"))
        self.assertIn("Base.Sample", (chunk_dir / "Chunk001.lua").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
