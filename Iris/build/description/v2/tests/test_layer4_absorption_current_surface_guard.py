from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

from clean_checkout_test_paths import external_test_path
from Iris.build.description.v2.tools.validate_layer4_absorption_current_surface_guard import (
    UNAUTHORIZED_CONSUMPTION_ERROR_CODE,
    build_report,
)


NAMESPACE = "LAYER4_ABSORPTION_CONFIRMED"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


class Layer4AbsorptionCurrentSurfaceGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = external_test_path(
            "_tmp_layer4_absorption_current_surface_guard"
        )
        self.reset_tmp_dir()

    def reset_tmp_dir(self) -> None:
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

    def test_synthetic_surface_dispositions(self) -> None:
        cases = (
            (
                "allowed_governance_and_test_surfaces",
                {
                    "docs/Iris/round.md": f"{NAMESPACE} remains a governance readpoint.\n",
                    "Iris/_archive/staging/round/evidence.json": json.dumps({"namespace": NAMESPACE}),
                    "Iris/build/description/v2/staging/round/evidence.json": json.dumps({"namespace": NAMESPACE}),
                    "Iris/build/description/v2/tests/fixture.py": f'VALUE = "{NAMESPACE}"\n',
                    "Iris/build/description/v2/tools/build/build_dvf_3_3_round_a_round_b_parallel_execution.py": f'ROUND_A_LEGACY = "{NAMESPACE}"\n',
                },
                "pass",
                0,
            ),
            (
                "runtime_lua",
                {"Iris/media/lua/client/Iris/UI/Wiki/Layer4Consumer.lua": f'local namespace = "{NAMESPACE}"\n'},
                "fail",
                1,
            ),
            (
                "source_and_rendered_payload",
                {
                    "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl": json.dumps({"namespace": NAMESPACE}),
                    "Iris/build/description/v2/output/dvf_3_3_rendered.json": json.dumps({"namespace": NAMESPACE}),
                },
                "fail",
                2,
            ),
            (
                "current_build_script",
                {"Iris/build/description/v2/tools/build/compose_new_layer4_consumer.py": f'NAMESPACE = "{NAMESPACE}"\n'},
                "fail",
                1,
            ),
        )
        for case_id, files, expected_status, expected_rejected in cases:
            with self.subTest(case_id=case_id):
                self.reset_tmp_dir()
                for relative, text in files.items():
                    write_text(self.tmp_dir / relative, text)
                report = build_report(self.tmp_dir)
                self.assertEqual(report["status"], expected_status)
                self.assertEqual(
                    report["summary"]["rejected_occurrence_count"],
                    expected_rejected,
                )
                if expected_status == "fail":
                    self.assertEqual(
                        report["error_code"],
                        UNAUTHORIZED_CONSUMPTION_ERROR_CODE,
                    )


if __name__ == "__main__":
    unittest.main()
