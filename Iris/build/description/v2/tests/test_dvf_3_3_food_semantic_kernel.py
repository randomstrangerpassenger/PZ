from __future__ import annotations

import sys
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.census_rules import (
    EXPECTED_PREDECESSOR_SHA256,
    PREDECESSOR_PLAN_PATH,
    RULES,
    execute_r3_signals,
    target_ids,
)
from tools.build.dvf_3_3_food_semantic.contracts import (
    canonical_member_digest,
    load_json,
    load_jsonl,
    sha256_text,
)
from tools.build.dvf_3_3_food_semantic.lineage_allowlist import (
    ALLOWED_SOURCE_FIELDS,
    FORBIDDEN_OPERATIONS,
    FORBIDDEN_SOURCE_FIELDS,
)
from tools.build.dvf_3_3_food_semantic.schema_feasibility import (
    AXES,
    PROPOSED_CURATION_ITEM_CAP,
    PROPOSED_CURATION_PROPOSITION_CAP,
    required_axes,
)


class FoodSemanticKernelTest(unittest.TestCase):
    def test_kernel_contracts(self) -> None:
        members = target_ids(REPO_ROOT)
        self.assertEqual(len(members), 317)
        self.assertEqual(len(members), len(set(members)))
        self.assertIn("Base.LemonGrass", members)
        self.assertIn("Base.Lemongrass", members)
        self.assertEqual(len(canonical_member_digest(members)), 64)

        first = execute_r3_signals(REPO_ROOT, members)
        second = execute_r3_signals(REPO_ROOT, list(reversed(members)))
        self.assertEqual(first, second)
        self.assertTrue(first)
        self.assertTrue(all(rule["rule_id"].startswith("R3.") for rule in RULES))
        self.assertTrue(
            all(
                row["source_field"]
                in {entry["field"] for entry in ALLOWED_SOURCE_FIELDS}
                for row in first
            )
        )
        self.assertTrue(
            all(row["source_field"] not in FORBIDDEN_SOURCE_FIELDS for row in first)
        )
        self.assertTrue(
            all(
                not set(row["normalization_operations"]) & set(FORBIDDEN_OPERATIONS)
                for row in first
            )
        )

        schema_values = {
            value["value"] for axis in AXES for value in axis["values"]
        }
        self.assertFalse({"unknown", "generic", "other"} & schema_values)
        self.assertEqual(required_axes(), ("consumption_form", "meal_role"))
        self.assertEqual(PROPOSED_CURATION_ITEM_CAP, 317)
        self.assertEqual(PROPOSED_CURATION_PROPOSITION_CAP, 634)

        predecessor_text = (REPO_ROOT / PREDECESSOR_PLAN_PATH).read_text(
            encoding="utf-8"
        )
        normalized = predecessor_text.replace("\r\n", "\n").replace("\r", "\n")
        self.assertEqual(sha256_text(normalized), EXPECTED_PREDECESSOR_SHA256)

    def test_successful_attempt_kernel_evidence(self) -> None:
        attempts = (
            V2_ROOT
            / "staging/dvf_3_3_food_semantic_facts_authority/attempts"
        )
        successful = [
            path
            for path in attempts.iterdir()
            if (
                path / "implementation_execution_summary.json"
            ).is_file()
            and load_json(path / "implementation_execution_summary.json")[
                "status"
            ]
            == "PASS"
        ]
        self.assertTrue(successful)
        attempt = sorted(successful)[-1]
        g0_g1 = load_json(
            attempt / "phase0_plan_and_decisions/g0_g1_release_binding.json"
        )
        self.assertEqual(g0_g1["status"], "PASS")
        self.assertEqual(g0_g1["four_plan_set_tracked_blob_count"], 4)
        self.assertEqual(g0_g1["blocking_predicates"], [])
        self.assertTrue(
            all(
                all(
                    value
                    for key, value in row.items()
                    if key != "path"
                )
                for row in g0_g1["manifest"]["plan_rows"]
            )
        )
        self.assertTrue(
            all(g0_g1["closeout_binding"]["predicates"].values())
        )
        entry = load_json(
            attempt
            / "phase0_plan_and_decisions/implementation_entry_gate.json"
        )
        self.assertEqual(entry["status"], "PASS")
        self.assertTrue(entry["predicates"]["clean_validation_terminal_pass"])
        self.assertEqual(
            entry["predicates"]["clean_validation_downstream_unblock_target"],
            "G2_food_semantic_facts_authority",
        )
        kernel = load_json(
            attempt
            / "phase7_automatic_mapping/feasibility_kernel_bundle.json"
        )
        self.assertEqual(kernel["feasibility_kernel_state"], "PASS")
        self.assertEqual(kernel["blocking_predicates"], [])
        self.assertEqual(
            kernel["predicates"]["exact_317_automatic_or_curation_route_count"],
            317,
        )
        cap = load_json(
            attempt / "phase6_schema/proposed_curation_caps.json"
        )
        self.assertEqual(cap["proposed_curation_item_cap"], 317)
        self.assertEqual(cap["proposed_curation_proposition_cap"], 634)
        feasibility = load_json(
            attempt
            / "phase7_automatic_mapping/curation_feasibility_report.json"
        )
        self.assertEqual(
            feasibility["predicted_required_curation_items"], 317
        )
        self.assertEqual(
            feasibility["predicted_required_curation_propositions"], 634
        )
        self.assertEqual(feasibility["maximum_propositions_per_item"], 2)
        queue = load_jsonl(
            attempt
            / "phase7_automatic_mapping/curation_required_queue.jsonl"
        )
        target = load_json(
            attempt / "phase1_census/target_food_universe_manifest.json"
        )
        self.assertEqual(len(queue), 634)
        self.assertEqual(
            {
                (row["item_identity"], row["required_fact_axis"])
                for row in queue
            },
            {
                (member, axis)
                for member in target["members"]
                for axis in required_axes()
            },
        )
        reproducibility = load_json(
            attempt
            / "phase2_rule_authority/rule_reproducibility_report.json"
        )
        self.assertEqual(reproducibility["isolated_subprocess_count"], 4)
        self.assertTrue(
            reproducibility["isolated_subprocess_environment_observed"]
        )
        self.assertTrue(
            all(
                row["signal_sha256"]
                == reproducibility["local_signal_sha256"]
                for row in reproducibility["subprocess_fixtures"]
            )
        )
        lineage = load_jsonl(attempt / "phase4_lineage/lineage_ledger.jsonl")
        proposition_ids = [
            row["fact_proposition_identity"] for row in lineage
        ]
        self.assertEqual(len(proposition_ids), len(set(proposition_ids)))
        self.assertTrue(
            all(row["supporting_signal_lineages"] for row in lineage)
        )


if __name__ == "__main__":
    unittest.main()
