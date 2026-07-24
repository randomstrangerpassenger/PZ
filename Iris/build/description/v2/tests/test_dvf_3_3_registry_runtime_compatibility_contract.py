from __future__ import annotations

import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import dvf_3_3_registry_runtime_compatibility as rtc


class RegistryRuntimeCompatibilityContractTest(unittest.TestCase):
    def test_promotion_staging_uses_short_same_volume_path(self) -> None:
        runner = (
            V2_ROOT
            / "tools"
            / "build"
            / "run_dvf_3_3_registry_runtime_compatibility.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'REPO_ROOT / "Iris" / "build" / ".rtc-promotion-staging"',
            runner,
        )
        self.assertNotIn('phase5 / "promotion-staging"', runner)

    def test_route_class_enum_is_closed(self) -> None:
        self.assertEqual(
            rtc.ROUTE_CLASSES,
            {
                "executable_current",
                "test_current",
                "operator_current",
                "diagnostic",
                "historical_non_executable",
                "static_reference",
                "unknown",
            },
        )

    def test_ast_finds_import_direct_call_and_subprocess(self) -> None:
        source = "\n".join(
            (
                "from tools.build.export_dvf_3_3_lua_bridge import export_lua_bridge",
                "export_lua_bridge()",
                "subprocess.run(['powershell', 'Iris/tools/package_iris.ps1'])",
            )
        )
        kinds = [row[2] for row in rtc.ast_rows("caller.py", source)]
        self.assertEqual(
            kinds,
            [
                "python_direct_import",
                "python_direct_call",
                "python_subprocess_invocation",
            ],
        )

    def test_historical_and_current_routes_are_not_conflated(self) -> None:
        self.assertEqual(
            rtc.classify_route(
                "Iris/build/description/v2/staging/old/tool.py",
                "python_direct_call",
                "export_lua_bridge()",
            ),
            "historical_non_executable",
        )
        self.assertEqual(
            rtc.classify_route(
                "Iris/build/description/v2/tests/test_bridge.py",
                "python_direct_call",
                "export_lua_bridge()",
            ),
            "test_current",
        )
        self.assertEqual(
            rtc.classify_route(
                "Iris/_docs/authority/current.md",
                "operator_command",
                r"powershell .\Iris\tools\package_iris.ps1 -Clean -Zip",
            ),
            "operator_current",
        )

    def test_every_inventory_row_gets_one_migration_disposition(self) -> None:
        rows = [
            {
                "inventory_row_id": "caller-1",
                "caller_path": "a.py",
                "route_class": "executable_current",
                "migration_required": True,
                "updated_status": "planned_explicit_contract_or_default_wrapper",
                "policy_resolution": "option_a_explicit_or_live_manifest_default",
                "regression_test_id": "fixture",
                "unresolved_status": None,
            },
            {
                "inventory_row_id": "caller-2",
                "caller_path": "old.md",
                "route_class": "historical_non_executable",
                "migration_required": False,
                "updated_status": "classified_no_migration",
                "policy_resolution": "not_applicable",
                "regression_test_id": "not_applicable",
                "unresolved_status": None,
            },
        ]
        matrix = rtc.migration_matrix(rows)
        self.assertEqual(matrix["inventory_row_count"], 2)
        self.assertEqual(matrix["disposition_row_count"], 2)
        self.assertEqual(matrix["inventory_orphan_count"], 0)
        self.assertEqual(matrix["disposition_orphan_count"], 0)
        self.assertEqual(matrix["duplicate_disposition_count"], 0)
        self.assertEqual(matrix["unknown_invocation_count"], 0)
        self.assertEqual(matrix["unmigrated_invocation_count"], 0)

    def test_exporter_omitted_route_has_no_environment_authority(self) -> None:
        exporter = (
            V2_ROOT / "tools" / "build" / "export_dvf_3_3_lua_bridge.py"
        ).read_text(encoding="utf-8")
        self.assertNotIn("os.environ", exporter)
        self.assertNotIn("IRIS_RTC_", exporter)
        self.assertIn(
            "required_manifest=CURRENT_REQUIRED_VALIDATIONS",
            exporter,
        )

    def test_porcelain_parser_preserves_status_and_paths(self) -> None:
        rows = rtc.parse_porcelain_v1_z(
            b" M docs/ROADMAP.md\0?? docs/new plan.md\0"
        )
        self.assertEqual(
            rows,
            [
                {"status": " M", "path": "docs/ROADMAP.md", "prior_path": ""},
                {"status": "??", "path": "docs/new plan.md", "prior_path": ""},
            ],
        )


if __name__ == "__main__":
    unittest.main()
