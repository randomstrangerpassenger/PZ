from __future__ import annotations

import ast
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import export_dvf_3_3_lua_bridge as bridge


class RegistryRuntimeCompatibilityBridgeTest(unittest.TestCase):
    def test_exporter_has_no_direct_canonical_analyzer_import(self) -> None:
        tree = ast.parse(Path(bridge.__file__).read_text(encoding="utf-8"))
        forbidden = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (
                node.module or ""
            ).endswith("dvf_3_3_registry_runtime_compatibility"):
                forbidden.append(node.lineno)
            if isinstance(node, ast.Import) and any(
                alias.name.endswith("dvf_3_3_registry_runtime_compatibility")
                for alias in node.names
            ):
                forbidden.append(node.lineno)
        self.assertEqual(forbidden, [])

    def test_unbound_direct_call_fails_before_writer_without_live_adoption(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            rendered = root / "rendered.json"
            rendered.write_text(
                json.dumps(
                    {
                        "meta": {"stats": {"total": 1}},
                        "entries": {
                            "Base.Item": {
                                "source": "fixture",
                                "text_ko": "fixture",
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            required = root / "required.json"
            required.write_text(
                json.dumps({"schema_version": "fixture"}),
                encoding="utf-8",
            )
            output_root = root / "output"
            with mock.patch.object(
                bridge,
                "CURRENT_REQUIRED_VALIDATIONS",
                required,
            ):
                with self.assertRaisesRegex(
                    bridge.BridgeExportContractError,
                    "compatibility_policy_context_required",
                ):
                    bridge.export_lua_bridge(
                        rendered_path=rendered,
                        output_root=output_root,
                        report_path=root / "report.json",
                    )
            self.assertFalse(output_root.exists())

    def test_preflight_occurs_before_json_materialization(self) -> None:
        source = Path(bridge.__file__).read_text(encoding="utf-8")
        function = next(
            node
            for node in ast.parse(source).body
            if isinstance(node, ast.FunctionDef) and node.name == "export_lua_bridge"
        )
        calls = [
            (
                node.lineno,
                node.func.id if isinstance(node.func, ast.Name) else "",
            )
            for node in ast.walk(function)
            if isinstance(node, ast.Call)
        ]
        preflight_line = min(
            line
            for line, name in calls
            if name == "run_registry_compatibility_preflight"
        )
        load_line = min(line for line, name in calls if name == "load_json")
        self.assertLess(preflight_line, load_line)

    def test_successor_current_alignment_fails_before_writer(self) -> None:
        required = json.loads(
            bridge.CURRENT_REQUIRED_VALIDATIONS.read_text(encoding="utf-8")
        )
        alignment = required["registry_runtime_compatibility"][
            "current_source_alignment"
        ]
        self.assertEqual(
            bridge.sha256_file(bridge.CURRENT_FACTS),
            alignment["applies_when_current_facts_sha256"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output_root = root / "output"
            with self.assertRaisesRegex(
                bridge.BridgeExportContractError,
                "registry_runtime_compatibility_current_source_stale",
            ):
                bridge.export_lua_bridge(
                    rendered_path=root / "unread-rendered.json",
                    output_root=output_root,
                    report_path=root / "report.json",
                )
            self.assertFalse(output_root.exists())
            self.assertFalse((root / "report.json").exists())

    def test_explicit_canonical_invocation_cannot_bypass_stale_alignment(self) -> None:
        required = json.loads(
            bridge.CURRENT_REQUIRED_VALIDATIONS.read_text(encoding="utf-8")
        )
        alignment = required["registry_runtime_compatibility"][
            "current_source_alignment"
        ]
        self.assertEqual(
            bridge.sha256_file(bridge.CURRENT_FACTS),
            alignment["applies_when_current_facts_sha256"],
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output_root = root / "output"
            invocation = bridge.RegistryCompatibilityInvocation(
                policy_context="canonical_durable",
                policy_path=root / "unread-policy.json",
                disposition_path=root / "unread-disposition.json",
                binding_manifest_path=root / "unread-binding.json",
                bridge_preflight_input_manifest=root / "unread-input.json",
                bridge_preflight_receipt=root / "unwritten-receipt.json",
            )
            with self.assertRaisesRegex(
                bridge.BridgeExportContractError,
                "registry_runtime_compatibility_current_source_stale",
            ):
                bridge.export_lua_bridge(
                    rendered_path=root / "unread-rendered.json",
                    output_root=output_root,
                    report_path=root / "report.json",
                    registry_compatibility=invocation,
                )
            self.assertFalse(output_root.exists())
            self.assertFalse(invocation.bridge_preflight_receipt.exists())


if __name__ == "__main__":
    unittest.main()
