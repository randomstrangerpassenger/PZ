from __future__ import annotations

import hashlib
import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.compose_layer3_text import (
    BODY_PLAN_PROFILES_PATH,
    BODY_SOURCE_OVERLAY_PATH,
    COMPOSE_CONTEXT_OUTPUT_CLASS_ERROR_CODE,
    COMPOSE_CONTEXT_REQUIRED_ERROR_CODE,
    COMPOSE_CURRENT_UNLISTED_OUTPUT_ERROR_CODE,
    COMPOSE_PROFILE_CLASS_ERROR_CODE,
    CURRENT_COMPOSE_CONTEXT,
    DATA_DIR,
    HISTORICAL_COMPOSE_CONTEXT,
    IDENTITY_RULES_PATH,
    OUTPUT_DIR,
    PRECEDENCE_RULES_PATH,
    STAGING_COMPOSE_CONTEXT,
    STYLE_LOG_PATH,
    ComposeEntrypointGuardError,
    build_rendered,
)


def file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


class ComposeEntrypointGuardHardeningTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = ROOT / "tests" / "_tmp_compose_entrypoint_guard"
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def write_legacy_inputs(self) -> tuple[Path, Path, Path, Path]:
        facts_path = self.tmp_dir / "facts.jsonl"
        decisions_path = self.tmp_dir / "decisions.jsonl"
        profiles_path = self.tmp_dir / "legacy_profiles.json"
        overlay_path = self.tmp_dir / "overlay.jsonl"
        write_jsonl(
            facts_path,
            [
                {
                    "item_id": "Base.GuardTool",
                    "identity_hint": "tool",
                    "primary_use": "used by guard tests",
                    "acquisition_hint": None,
                    "secondary_use": None,
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
                    "item_id": "Base.GuardTool",
                    "state": "active",
                    "compose_profile": "interaction_tool",
                    "override_mode": "none",
                    "selected_cluster": None,
                }
            ],
        )
        write_jsonl(overlay_path, [])
        write_json(
            profiles_path,
            {
                "interaction_tool": {
                    "sentence_plan": [
                        {"slots": ["identity_hint"], "required": True, "template": "{identity_hint}."},
                        {"slots": ["primary_use"], "required": True, "template": "{primary_use}."},
                    ]
                }
            },
        )
        return facts_path, decisions_path, profiles_path, overlay_path

    def assert_guard_error(self, reason: str, callback) -> None:
        with self.assertRaises(ComposeEntrypointGuardError) as raised:
            callback()
        self.assertIn(reason, str(raised.exception))

    def test_direct_current_equivalent_output_requires_context(self) -> None:
        self.assert_guard_error(
            COMPOSE_CONTEXT_REQUIRED_ERROR_CODE,
            lambda: build_rendered(
                DATA_DIR / "dvf_3_3_facts.jsonl",
                DATA_DIR / "dvf_3_3_decisions.jsonl",
                BODY_PLAN_PROFILES_PATH,
                OUTPUT_DIR / "dvf_3_3_rendered.json",
                BODY_SOURCE_OVERLAY_PATH,
                STYLE_LOG_PATH,
                None,
                IDENTITY_RULES_PATH,
                PRECEDENCE_RULES_PATH,
            ),
        )

    def test_explicit_non_current_output_requires_context(self) -> None:
        facts_path, decisions_path, profiles_path, overlay_path = self.write_legacy_inputs()
        self.assert_guard_error(
            COMPOSE_CONTEXT_REQUIRED_ERROR_CODE,
            lambda: build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                self.tmp_dir / "rendered.json",
                overlay_path,
                self.tmp_dir / "style_log.jsonl",
            ),
        )

    def test_direct_current_fixture_with_v2_profile_passes(self) -> None:
        rendered = build_rendered(
            DATA_DIR / "dvf_3_3_facts.jsonl",
            DATA_DIR / "dvf_3_3_decisions.jsonl",
            BODY_PLAN_PROFILES_PATH,
            self.tmp_dir / "dvf_3_3_rendered.json",
            DATA_DIR / "dvf_3_3_overlay_support.jsonl",
            self.tmp_dir / "style_normalization_changes.jsonl",
            None,
            IDENTITY_RULES_PATH,
            PRECEDENCE_RULES_PATH,
            compose_context=CURRENT_COMPOSE_CONTEXT,
        )

        self.assertIn("entries", rendered)
        self.assertTrue((self.tmp_dir / "dvf_3_3_rendered.json").exists())

    def test_legacy_profile_cannot_write_current_output_and_leaves_hash_unchanged(self) -> None:
        facts_path, decisions_path, profiles_path, overlay_path = self.write_legacy_inputs()
        current_output = OUTPUT_DIR / "dvf_3_3_rendered.json"
        before_hash = file_hash(current_output)

        self.assert_guard_error(
            COMPOSE_PROFILE_CLASS_ERROR_CODE,
            lambda: build_rendered(
                facts_path,
                decisions_path,
                profiles_path,
                current_output,
                overlay_path,
                STYLE_LOG_PATH,
                compose_context=CURRENT_COMPOSE_CONTEXT,
            ),
        )

        self.assertEqual(before_hash, file_hash(current_output))

    def test_staging_context_cannot_target_current_equivalent_output(self) -> None:
        self.assert_guard_error(
            COMPOSE_CONTEXT_OUTPUT_CLASS_ERROR_CODE,
            lambda: build_rendered(
                DATA_DIR / "dvf_3_3_facts.jsonl",
                DATA_DIR / "dvf_3_3_decisions.jsonl",
                BODY_PLAN_PROFILES_PATH,
                OUTPUT_DIR / "dvf_3_3_rendered.json",
                BODY_SOURCE_OVERLAY_PATH,
                STYLE_LOG_PATH,
                None,
                IDENTITY_RULES_PATH,
                PRECEDENCE_RULES_PATH,
                compose_context=STAGING_COMPOSE_CONTEXT,
            ),
        )

    def test_unlisted_output_root_target_is_rejected_before_write(self) -> None:
        shadow_output = OUTPUT_DIR / "dvf_3_3_rendered_shadow_guard_test.json"
        before_hash = file_hash(shadow_output)

        self.assert_guard_error(
            COMPOSE_CURRENT_UNLISTED_OUTPUT_ERROR_CODE,
            lambda: build_rendered(
                DATA_DIR / "dvf_3_3_facts.jsonl",
                DATA_DIR / "dvf_3_3_decisions.jsonl",
                BODY_PLAN_PROFILES_PATH,
                shadow_output,
                BODY_SOURCE_OVERLAY_PATH,
                STYLE_LOG_PATH,
                None,
                IDENTITY_RULES_PATH,
                PRECEDENCE_RULES_PATH,
                compose_context=CURRENT_COMPOSE_CONTEXT,
            ),
        )

        self.assertEqual(before_hash, file_hash(shadow_output))

    def test_legacy_profile_explicit_historical_output_passes(self) -> None:
        facts_path, decisions_path, profiles_path, overlay_path = self.write_legacy_inputs()
        output_path = self.tmp_dir / "historical_rendered.json"

        rendered = build_rendered(
            facts_path,
            decisions_path,
            profiles_path,
            output_path,
            overlay_path,
            self.tmp_dir / "historical_style_log.jsonl",
            compose_context=HISTORICAL_COMPOSE_CONTEXT,
        )

        self.assertIn("Base.GuardTool", rendered["entries"])
        self.assertTrue(output_path.exists())


if __name__ == "__main__":
    unittest.main()
