from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
HARNESS = REPO / "Iris/test/lua/runtime_optimization_metrics_harness.lua"
EVIDENCE = REPO / "Iris/_docs/refactor/codebase_optimization"
TEST_PREFIX = (
    "Iris/build/description/v2/tests/"
    "test_iris_runtime_optimization_metrics.py::"
    "RuntimeOptimizationMetricsTest::"
)


def signature_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


class RuntimeOptimizationMetricsTest(unittest.TestCase):
    def run_mode(self, mode: str) -> dict[str, str]:
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(HARNESS), str(REPO), mode],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        result: dict[str, str] = {}
        for line in completed.stdout.splitlines():
            key, separator, value = line.partition("=")
            if separator:
                result[key] = value
        self.assertEqual(mode, result.get("mode"))
        return result

    def receipt(self, name: str) -> dict:
        return json.loads((EVIDENCE / name).read_text(encoding="utf-8"))

    def assert_common_receipt(self, receipt: dict, method: str) -> None:
        self.assertEqual("iris-runtime-optimization-receipt-v1", receipt["schema_version"])
        self.assertEqual(TEST_PREFIX + method, receipt["test_id"])
        self.assertEqual(64, len(receipt["denominator"]["sha256"]))
        self.assertIn(receipt["disposition"], {"adopted", "complete/no-op", "deferred"})

    def test_baseline_generation_identity_receipts(self) -> None:
        baseline_0 = self.receipt("baseline_0.json")
        baseline_1 = self.receipt("baseline_1.json")
        self.assertEqual("a4677cb4c5f49d30f7e85c578d644345a2db1d65", baseline_0["commit"])
        self.assertEqual("59e14df282f94fce5deef2cc4132a6f16b382a2b", baseline_0["tree"])
        self.assertEqual("a940cf18e129bb3f144d35545aa4ff93357f2a40", baseline_1["commit"])
        self.assertEqual("abd178b4b9d3d68848a0a898eba3b840642e3cb0", baseline_1["tree"])
        self.assertNotEqual(baseline_0["commit"], baseline_1["commit"])
        self.assertEqual("fixed_standalone_lua_fixture", baseline_0["environment"]["runtime"])
        self.assertEqual("fixed_standalone_lua_fixture", baseline_1["environment"]["runtime"])

    def test_change_5_tooltip_allocation_receipt(self) -> None:
        method = "test_change_5_tooltip_allocation_receipt"
        receipt = self.receipt("change_5_tooltip.json")
        self.assert_common_receipt(receipt, method)
        after = self.run_mode("tooltip")
        expected = receipt["raw_samples"]["after"]
        for key, value in expected.items():
            self.assertEqual(value, int(after[key]))
        self.assertEqual(1000, int(after["inactive_renders"]))
        for key in (
            "inactive_summary_loads",
            "inactive_summary_gets",
            "inactive_temporary_tables",
            "inactive_draw_calls",
        ):
            self.assertEqual(0, int(after[key]), key)
        self.assertEqual(1, int(after["warm_display_builds"]))
        self.assertEqual(0, int(after["warm_line_copies"]))
        self.assertEqual("adopted", receipt["disposition"])

    def test_change_6a_search_location_copy_receipt(self) -> None:
        method = "test_change_6a_search_location_copy_receipt"
        receipt = self.receipt("change_6a_search_location_copy.json")
        self.assert_common_receipt(receipt, method)
        after = self.run_mode("search")
        expected = receipt["raw_samples"]["after"]
        for key, value in expected.items():
            if key == "signature_sha256":
                self.assertEqual(value, signature_sha256(after["signature"]))
            else:
                self.assertEqual(value, int(after[key]))
        before = receipt["raw_samples"]["before"]
        before_target = sum(before[key] for key in (
            "location_lookups", "internal_row_copies", "public_row_copies"
        ))
        after_target = sum(int(after[key]) for key in (
            "location_lookups", "internal_row_copies", "public_row_copies"
        ))
        self.assertGreater(before_target, 0)
        self.assertGreaterEqual((before_target - after_target) / before_target, 0.50)
        self.assertLessEqual(int(after["public_row_copies"]), int(after["returned_rows"]))
        self.assertEqual(before["signature_sha256"], signature_sha256(after["signature"]))
        self.assertEqual("adopted", receipt["disposition"])

    def test_change_6b_capability_mask_receipt(self) -> None:
        method = "test_change_6b_capability_mask_receipt"
        receipt = self.receipt("change_6b_capability_mask.json")
        self.assert_common_receipt(receipt, method)
        after = self.run_mode("viewmodel")
        expected = receipt["raw_samples"]["after"]
        for key, value in expected.items():
            if key == "signature_sha256":
                self.assertEqual(value, signature_sha256(after["signature"]))
            else:
                self.assertEqual(value, int(after[key]))
        before = receipt["raw_samples"]["before"]
        reduction = (
            before["engine_method_calls"] - int(after["engine_method_calls"])
        ) / before["engine_method_calls"]
        self.assertGreaterEqual(reduction, 0.30)
        self.assertEqual(before["signature_sha256"], signature_sha256(after["signature"]))
        self.assertGreater(sum(int(after[key]) for key in (
            "food_skips", "weapon_skips", "literature_skips", "moveable_skips"
        )), 0)
        self.assertEqual("PASS", after["custom_hybrid_parity"])
        self.assertEqual("adopted", receipt["disposition"])

    def test_change_6b_static_projection_instance_isolation_receipt(self) -> None:
        method = "test_change_6b_static_projection_instance_isolation_receipt"
        receipt = self.receipt("change_6b_static_projection.json")
        self.assert_common_receipt(receipt, method)
        current = self.run_mode("viewmodel")
        self.assertEqual("PASS", current["instance_isolation"])
        self.assertEqual(
            receipt["raw_samples"]["isolation_scope"],
            current["isolation_scope"],
        )
        self.assertEqual(
            ["ScriptItem-to-InventoryItem", "Browser-to-Wiki caller order"],
            receipt["raw_samples"]["excluded_claims"],
        )
        self.assertEqual(0, int(current["static_cache_hits"]))
        self.assertEqual("complete/no-op", receipt["disposition"])
        self.assertEqual("purity_and_generation_invalidation_not_closed", receipt["trigger"]["result"])

    def assert_deferred_pz_receipt(self, name: str, method: str) -> None:
        receipt = self.receipt(name)
        self.assert_common_receipt(receipt, method)
        self.assertEqual("deferred", receipt["disposition"])
        self.assertEqual("unvalidated_but_in_scope", receipt["trigger"]["result"])
        self.assertEqual(10, receipt["denominator"]["required_runs"])
        self.assertEqual([], receipt["raw_samples"])
        self.assertEqual(
            "actual_project_zomboid_runtime_unavailable",
            receipt["validation_limit"],
        )

    def test_change_6c_search_debounce_receipt(self) -> None:
        self.assert_deferred_pz_receipt(
            "change_6c_search_debounce.json",
            "test_change_6c_search_debounce_receipt",
        )

    def test_change_6c_incremental_build_receipt(self) -> None:
        self.assert_deferred_pz_receipt(
            "change_6c_incremental_build.json",
            "test_change_6c_incremental_build_receipt",
        )

    def test_change_7_tooltip_static_receipt(self) -> None:
        self.assert_deferred_pz_receipt(
            "change_7_tooltip_static.json",
            "test_change_7_tooltip_static_receipt",
        )

    def test_change_7_linecount_receipt(self) -> None:
        self.assert_deferred_pz_receipt(
            "change_7_linecount_validation.json",
            "test_change_7_linecount_receipt",
        )

    def test_change_10_ordering_receipt(self) -> None:
        method = "test_change_10_ordering_receipt"
        receipt = self.receipt("change_10_ordering.json")
        self.assert_common_receipt(receipt, method)
        after = self.run_mode("ordering")
        expected = receipt["raw_samples"]["after"]
        self.assertEqual(expected["rows"], int(after["rows"]))
        self.assertEqual(
            expected["signature_sha256"], signature_sha256(after["signature"])
        )
        self.assertLessEqual(
            int(after["sort_key_derivations"]), int(after["rows"]) + 1
        )
        before = receipt["raw_samples"]["before"]
        self.assertGreater(before["sort_key_derivations"], before["rows"] + 1)
        self.assertEqual(before["signature_sha256"], signature_sha256(after["signature"]))
        self.assertEqual("adopted", receipt["disposition"])

    def test_metric_harness_run_a_run_b_determinism(self) -> None:
        for mode in ("search", "tooltip", "viewmodel", "ordering"):
            with self.subTest(mode=mode):
                self.assertEqual(self.run_mode(mode), self.run_mode(mode))


if __name__ == "__main__":
    unittest.main()
