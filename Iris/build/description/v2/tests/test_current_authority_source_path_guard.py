from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.compose_layer3_text import (
    DATA_DIR,
    DEFAULT_CURRENT_AUTHORITY_INPUT_PATH_ERROR_CODE,
    DEFAULT_MODE,
    DIAGNOSTIC_RESOLVER_MODE,
    default_entrypoint_paths,
    enforce_current_authority_input_contract,
    main as compose_main,
)


def current_authority_paths(**overrides: Path) -> dict[str, Path | None]:
    paths: dict[str, Path | None] = {
        "facts_path": DATA_DIR / "dvf_3_3_facts.jsonl",
        "decisions_path": DATA_DIR / "dvf_3_3_decisions.jsonl",
        "overlay_path": DATA_DIR / "dvf_3_3_overlay_support.jsonl",
        "profiles_path": DATA_DIR / "compose_profiles_v2.json",
        "identity_rules_path": DATA_DIR / "compose_profile_identity_hint_rules.json",
        "precedence_rules_path": DATA_DIR / "compose_profile_conflict_precedence_rules.json",
    }
    paths.update(overrides)
    return paths


class CurrentAuthoritySourcePathGuardTest(unittest.TestCase):
    def test_default_entrypoint_rejects_staging_current_authority_input(self) -> None:
        with self.assertRaisesRegex(ValueError, DEFAULT_CURRENT_AUTHORITY_INPUT_PATH_ERROR_CODE):
            compose_main(
                [
                    "--compose-context",
                    "current",
                    "--facts-path",
                    str(ROOT / "staging" / "round" / "facts.jsonl"),
                    "--output-path",
                    str(ROOT / "tests" / "_tmp_current_authority_guard" / "rendered.json"),
                    "--style-log-path",
                    str(ROOT / "tests" / "_tmp_current_authority_guard" / "style_log.jsonl"),
                ]
            )

    def test_default_contract_rejects_test_fixture_current_authority_input(self) -> None:
        with self.assertRaisesRegex(ValueError, DEFAULT_CURRENT_AUTHORITY_INPUT_PATH_ERROR_CODE):
            enforce_current_authority_input_contract(
                DEFAULT_MODE,
                current_authority_paths(
                    decisions_path=ROOT / "tests" / "fixtures" / "dvf_3_3_decisions.jsonl",
                ),
            )

    def test_default_contract_accepts_data_current_authority_inputs(self) -> None:
        enforce_current_authority_input_contract(DEFAULT_MODE, current_authority_paths())

    def test_default_entrypoint_uses_current_overlay_support(self) -> None:
        defaults = default_entrypoint_paths(DEFAULT_MODE)

        self.assertEqual(defaults["overlay_path"], DATA_DIR / "dvf_3_3_overlay_support.jsonl")

    def test_default_contract_rejects_staging_overlay_input(self) -> None:
        with self.assertRaisesRegex(ValueError, DEFAULT_CURRENT_AUTHORITY_INPUT_PATH_ERROR_CODE):
            enforce_current_authority_input_contract(
                DEFAULT_MODE,
                current_authority_paths(
                    overlay_path=ROOT / "staging" / "compose_contract_migration" / "layer3_body_source_overlay.jsonl",
                ),
            )

    def test_diagnostic_contract_allows_non_data_diagnostic_readpoint(self) -> None:
        enforce_current_authority_input_contract(
            DIAGNOSTIC_RESOLVER_MODE,
            current_authority_paths(
                facts_path=ROOT / "staging" / "diagnostic" / "facts.jsonl",
                decisions_path=ROOT / "tests" / "fixtures" / "decisions.jsonl",
            ),
        )


if __name__ == "__main__":
    unittest.main()
