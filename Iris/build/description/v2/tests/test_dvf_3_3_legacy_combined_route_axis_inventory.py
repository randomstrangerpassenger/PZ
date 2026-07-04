from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROUND_ID = "dvf_3_3_legacy_combined_route_axis_inventory_routing_preflight"
TOOL_BASENAME = "dvf_3_3_legacy_combined_route_axis_inventory"
RUNNER = TOOLS / f"run_{TOOL_BASENAME}.py"
VALIDATOR = TOOLS / f"validate_{TOOL_BASENAME}.py"

sys.path.insert(0, str(TOOLS))
import dvf_3_3_legacy_combined_route_axis_inventory as inventory  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class LegacyCombinedRouteAxisInventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._tempdir = tempfile.TemporaryDirectory(prefix="dvf_legacy_axis_")
        cls.root = Path(cls._tempdir.name) / "evidence"
        cls.env = os.environ.copy()
        cls.env["DVF_LEGACY_COMBINED_ROUTE_AXIS_INVENTORY_ROOT"] = str(cls.root)
        result = subprocess.run(
            [sys.executable, "-B", str(RUNNER), "--mode", "all"],
            cwd=REPO,
            env=cls.env,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "inventory generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    @classmethod
    def tearDownClass(cls) -> None:
        tempdir = getattr(cls, "_tempdir", None)
        if tempdir is not None:
            tempdir.cleanup()

    def run_validator(self, root: Path) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["DVF_LEGACY_COMBINED_ROUTE_AXIS_INVENTORY_ROOT"] = str(root)
        return subprocess.run(
            [sys.executable, "-B", str(VALIDATOR), "--require-complete"],
            cwd=REPO,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )

    def copy_evidence(self, name: str) -> Path:
        target = Path(self._tempdir.name) / name
        shutil.copytree(self.root, target)
        return target

    def test_final_report_preserves_legacy_combined_claim_boundary(self) -> None:
        final = load_json(self.root / "routing_preflight_report.json")

        self.assertEqual(final["semantic_verdict"], "routing_preflight_ready")
        self.assertFalse(final["legacy_combined_route_pass_is_dvf_core_pass"])
        self.assertFalse(final["manifest_split_required"])
        self.assertTrue(final["legacy_combined_route_preserved"])
        self.assertTrue(final["consumer_freshness_responsibility"])
        self.assertEqual(final["blocker_count"], 0)
        self.assertEqual(final["ambiguity_queue_count"], 0)
        self.assertEqual(
            final["mandated_final_statements"],
            inventory.MANDATED_FINAL_STATEMENTS,
        )

    def test_current_route_union_is_full_guard_census_universe(self) -> None:
        census = load_json(self.root / "surface_census_report.json")
        guard = load_json(self.root / "guard_test_axis_inventory.json")

        self.assertEqual(census["guard_test_census_universe"], "current_route_union")
        self.assertEqual(guard["guard_test_census_universe"], "current_route_union")
        self.assertEqual(census["current_route_union_test_count"], len(guard["rows"]))
        self.assertEqual(guard["uncovered_current_route_test_count"], 0)
        self.assertTrue(census["new_round_local_tests_do_not_enter_current_route_union"])

    def test_required_manifest_rows_are_classified_without_unknown_axis(self) -> None:
        report = load_json(self.root / "required_manifest_axis_classification_report.json")
        distribution = load_json(self.root / "legacy_combined_axis_distribution_guard_report.json")
        inventory_payload = load_json(self.root / "legacy_combined_route_axis_inventory.json")

        self.assertEqual(report["unknown_count"], 0)
        self.assertEqual(report["invalid_axis_count"], 0)
        self.assertEqual(report["classified_required_test_count"], report["required_test_count"])
        self.assertEqual(report["classified_required_artifact_count"], report["required_artifact_count"])
        self.assertEqual(distribution["legacy_combined_required_item_without_route_reason_count"], 0)
        for row in inventory_payload["rows"]:
            self.assertIn(row["primary_axis"], inventory.AXES)
            self.assertTrue(row["positive_evidence"], row["item_id"])
            self.assertTrue(row["excluded_axes"], row["item_id"])

    def test_negative_fixture_report_rejects_all_forbidden_shapes(self) -> None:
        payload = load_json(self.root / "negative_axis_fixture_report.json")

        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["executed_fixture_count"], 20)
        for row in payload["fixtures"]:
            self.assertTrue(row["fixture_passed"], row)
            self.assertEqual(row["validator_exit_code"], 1, row)
            self.assertIn(row["expected_code"], row["observed_codes"], row)

    def test_validator_rejects_manifest_split_tamper(self) -> None:
        tampered = self.copy_evidence("tampered_manifest_split")
        path = tampered / "routing_preflight_report.json"
        payload = load_json(path)
        payload["manifest_split_required"] = True
        write_json(path, payload)

        result = self.run_validator(tampered)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(tampered / "routing_preflight_validation_report.json")
        self.assertIn("manifest_split_required", {error["code"] for error in report["errors"]})

    def test_validator_rejects_missing_primary_axis_tamper(self) -> None:
        tampered = self.copy_evidence("tampered_missing_axis")
        path = tampered / "legacy_combined_route_axis_inventory.json"
        payload = load_json(path)
        payload["rows"][0].pop("primary_axis", None)
        write_json(path, payload)

        result = self.run_validator(tampered)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        report = load_json(tampered / "routing_preflight_validation_report.json")
        self.assertIn("missing_primary_axis", {error["code"] for error in report["errors"]})


if __name__ == "__main__":
    unittest.main()
