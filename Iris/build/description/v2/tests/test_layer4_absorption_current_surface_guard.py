from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.validate_layer4_absorption_current_surface_guard import (
    UNAUTHORIZED_CONSUMPTION_ERROR_CODE,
    build_report,
)


NAMESPACE = "LAYER4_ABSORPTION_CONFIRMED"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class Layer4AbsorptionCurrentSurfaceGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = ROOT / "tests" / "_tmp_layer4_absorption_current_surface_guard"
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir)

    def test_current_repo_has_no_unauthorized_consumption(self) -> None:
        report = build_report(ROOT.parents[3])

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["rejected_occurrence_count"], 0)

    def test_docs_staging_tests_and_historical_predecessor_are_allowed(self) -> None:
        write_text(
            self.tmp_dir / "docs" / "Iris" / "round.md",
            f"{NAMESPACE} remains a governance readpoint.\n",
        )
        write_text(
            self.tmp_dir
            / "Iris"
            / "build"
            / "description"
            / "v2"
            / "staging"
            / "round"
            / "evidence.json",
            json.dumps({"namespace": NAMESPACE}, indent=2),
        )
        write_text(
            self.tmp_dir
            / "Iris"
            / "build"
            / "description"
            / "v2"
            / "tests"
            / "fixture.py",
            f'VALUE = "{NAMESPACE}"\n',
        )
        write_text(
            self.tmp_dir
            / "Iris"
            / "build"
            / "description"
            / "v2"
            / "tools"
            / "build"
            / "build_dvf_3_3_round_a_round_b_parallel_execution.py",
            f'ROUND_A_LEGACY = "{NAMESPACE}"\n',
        )

        report = build_report(self.tmp_dir)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["summary"]["rejected_occurrence_count"], 0)

    def test_runtime_lua_consumption_fails(self) -> None:
        write_text(
            self.tmp_dir
            / "Iris"
            / "media"
            / "lua"
            / "client"
            / "Iris"
            / "UI"
            / "Wiki"
            / "Layer4Consumer.lua",
            f'local namespace = "{NAMESPACE}"\n',
        )

        report = build_report(self.tmp_dir)

        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["error_code"], UNAUTHORIZED_CONSUMPTION_ERROR_CODE)
        self.assertEqual(report["summary"]["rejected_occurrence_count"], 1)

    def test_source_or_rendered_payload_consumption_fails(self) -> None:
        write_text(
            self.tmp_dir
            / "Iris"
            / "build"
            / "description"
            / "v2"
            / "data"
            / "dvf_3_3_decisions.jsonl",
            json.dumps({"namespace": NAMESPACE}) + "\n",
        )
        write_text(
            self.tmp_dir
            / "Iris"
            / "build"
            / "description"
            / "v2"
            / "output"
            / "dvf_3_3_rendered.json",
            json.dumps({"namespace": NAMESPACE}, indent=2),
        )

        report = build_report(self.tmp_dir)

        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["summary"]["rejected_occurrence_count"], 2)

    def test_current_build_script_consumption_fails_without_explicit_allow(self) -> None:
        write_text(
            self.tmp_dir
            / "Iris"
            / "build"
            / "description"
            / "v2"
            / "tools"
            / "build"
            / "compose_new_layer4_consumer.py",
            f'NAMESPACE = "{NAMESPACE}"\n',
        )

        report = build_report(self.tmp_dir)

        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["summary"]["rejected_occurrence_count"], 1)


if __name__ == "__main__":
    unittest.main()
