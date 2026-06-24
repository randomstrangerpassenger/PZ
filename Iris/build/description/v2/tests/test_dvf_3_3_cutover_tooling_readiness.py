from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_vnext_cutover_tooling_readiness"

sys.path.insert(0, str(TOOLS))

from dvf_3_3_cutover_tooling_readiness_common import MANDATORY_COMMAND_FIELDS  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


class DvfCutoverToolingReadinessTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        scripts = [
            "generate_dvf_3_3_overlay_support_artifact.py",
            "manage_dvf_3_3_runtime_chunk_cutover.py",
            "apply_dvf_3_3_consumer_migration.py",
            "generate_dvf_3_3_row_level_migration_ledger.py",
            "validate_dvf_3_3_actual_diff_to_ledger.py",
            "validate_dvf_3_3_command_surface_mapping.py",
        ]
        for script in scripts:
            result = subprocess.run(
                [sys.executable, "-B", str(TOOLS / script)],
                cwd=REPO,
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                raise AssertionError(f"{script} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

    def test_phase0_command_mapping_has_downstream_compatibility_fields(self) -> None:
        mapping = load_json(ROOT / "phase0/command_surface_mapping.json")
        contracts = load_json(ROOT / "phase0/minimum_schema_contracts.json")

        self.assertEqual(mapping["mapping_owner"], "cutover_tooling_readiness_round")
        self.assertEqual(set(contracts["mandatory_fields"]["command_surface_mapping.json"]), set(MANDATORY_COMMAND_FIELDS))
        self.assertEqual(len(mapping["commands"]), 6)
        for row in mapping["commands"]:
            for field in MANDATORY_COMMAND_FIELDS:
                self.assertIn(field, row)
            self.assertIn("validation_family", row)
            self.assertIn("concrete_command_or_tool", row)
            self.assertIn("expected_artifact", row)
            self.assertIn("blocking_condition", row)

    def test_overlay_support_is_deterministic_and_not_source_authority(self) -> None:
        lineage = load_json(ROOT / "phase1/overlay_input_lineage_report.json")
        manifest = load_json(ROOT / "phase1/overlay_support_manifest.json")
        seal = load_json(ROOT / "phase1/overlay_support_seal_report.json")
        rows = load_jsonl(ROOT / "phase1/dvf_3_3_overlay_support.jsonl")

        self.assertEqual(lineage["status"], "PASS")
        self.assertEqual(lineage["output_role"], "compose_support_not_source_authority")
        self.assertTrue(lineage["fixture_as_authority_rejected"])
        self.assertEqual(manifest["status"], "PASS")
        self.assertEqual(manifest["overlay_row_count"], len(rows))
        self.assertEqual(manifest["role"], "compose_support_not_source_authority")
        self.assertEqual(seal["status"], "PASS")
        self.assertTrue(seal["same_input_deterministic"])

    def test_runtime_chunk_tool_uses_mirror_apply_and_restore_only(self) -> None:
        snapshot = load_json(ROOT / "phase2/predecessor_runtime_snapshot_manifest.json")
        candidate = load_json(ROOT / "phase2/candidate_bundle_validation_report.json")
        apply_report = load_json(ROOT / "phase2/atomic_cutover_mirror_apply_report.json")
        restore = load_json(ROOT / "phase2/restore_probe_report.json")
        live_probe = load_json(ROOT / "phase2/exact_live_target_probe_report.json")
        template = load_json(ROOT / "phase6/runtime_cutover_live_command_template.json")

        self.assertEqual(snapshot["status"], "PASS")
        self.assertEqual(candidate["status"], "PASS")
        self.assertEqual(apply_report["status"], "PASS")
        self.assertTrue(apply_report["actual_atomic_replace"])
        self.assertTrue(apply_report["actual_restore_probe"])
        self.assertTrue(apply_report["restore_hash_equal_to_predecessor"])
        self.assertEqual(restore["status"], "PASS")
        self.assertEqual(live_probe["probe_mode"], "read_only")
        self.assertFalse(apply_report["live_runtime_mutated"])
        self.assertTrue(template["forbidden_readiness_execution"])
        self.assertFalse(template["template_executed_in_readiness"])

    def test_consumer_migration_sandbox_and_row_ledger_are_complete(self) -> None:
        preflight = load_json(ROOT / "phase3/consumer_migration_materialization_preflight_report.json")
        actual = load_json(ROOT / "phase3/consumer_migration_actual_report.json")
        forbidden = load_json(ROOT / "phase3/change_forbidden_zero_mutation_report.json")
        generation = load_json(ROOT / "phase3/row_level_migration_ledger_generation_report.json")
        ledger = load_jsonl(ROOT / "phase3/row_level_migration_ledger.jsonl")

        self.assertEqual(preflight["verdict"], "PASS")
        self.assertEqual(preflight["change_required_row_count"], 311)
        self.assertEqual(preflight["blocked_rows"], [])
        self.assertEqual(actual["status"], "PASS")
        self.assertEqual(actual["apply_row_count"], 163)
        self.assertFalse(actual["live_repo_mutated"])
        self.assertEqual(forbidden["change_forbidden_occurrence_denominator"], 27558)
        self.assertEqual(forbidden["change_forbidden_occurrence_mutation_count"], 0)
        self.assertEqual(generation["status"], "PASS")
        self.assertEqual(len(ledger), 311)
        self.assertEqual(generation["mutation_row_count"], 163)

    def test_actual_diff_maps_bijectively_to_ledger(self) -> None:
        report = load_json(ROOT / "phase4/actual_diff_to_ledger_report.json")
        bijection = load_json(ROOT / "phase4/diff_hunk_ledger_bijection_report.json")
        no_mutation = load_json(ROOT / "phase4/protected_surface_no_mutation_verdict.json")

        self.assertEqual(report["verdict"], "PASS")
        self.assertEqual(report["mapped_hunk_count"], 163)
        self.assertEqual(report["unmapped_hunk_count"], 0)
        self.assertEqual(report["orphan_ledger_count"], 0)
        self.assertEqual(report["forbidden_row_diff_count"], 0)
        self.assertEqual(report["protected_surface_diff_count"], 0)
        self.assertEqual(bijection["status"], "PASS")
        self.assertEqual(no_mutation["status"], "PASS")
        self.assertEqual(no_mutation["changed_count"], 0)

    def test_command_surface_and_final_reports_do_not_overclaim_cutover(self) -> None:
        mapping_report = load_json(ROOT / "phase5/command_surface_mapping_validation_report.json")
        compatibility = load_json(ROOT / "phase6/tool_contract_compatibility_manifest.json")
        final = load_json(ROOT / "phase6/final_tooling_readiness_contract_report.json")
        closeout = (REPO / "docs/dvf_3_3_vnext_current_authority_cutover_tooling_readiness_closeout.md").read_text(
            encoding="utf-8"
        )
        ledger_packet = (ROOT / "phase6/ledger_update_packet.md").read_text(encoding="utf-8")

        self.assertEqual(mapping_report["status"], "PASS")
        self.assertEqual(compatibility["verdict"], "PASS")
        self.assertEqual(compatibility["fixed_downstream_plan_compatibility"], "PASS")
        self.assertEqual(final["status"], "PASS")
        self.assertIn("no_live_runtime_chunk_replacement", final["non_claims"])
        self.assertIn("does not claim current authority adoption", closeout)
        self.assertTrue(ledger_packet.startswith("Draft-only ledger packet; not applied"))


if __name__ == "__main__":
    unittest.main()
