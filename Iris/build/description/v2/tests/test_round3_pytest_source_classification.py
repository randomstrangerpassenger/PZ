from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path
from unittest import mock


REPO = Path(__file__).resolve().parents[5]
CONFTEST_PATH = REPO / "Iris/build/description/v2/tests/conftest.py"
SPEC = importlib.util.spec_from_file_location("iris_round3_conftest_contract", CONFTEST_PATH)
assert SPEC is not None and SPEC.loader is not None
POLICY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)


class Round3PytestSourceClassificationTest(unittest.TestCase):
    def test_inventory_is_owner_approved_complete_and_exact_authority_is_separate(self) -> None:
        payload = POLICY._source_policy_payload()
        POLICY._validate_policy_inventory()
        self.assertTrue(payload["owner_approval"]["approved"])
        self.assertEqual(50, len(payload["reviewed_sources"]))
        self.assertEqual(2, payload["baseline_inventory"]["known_collection_blockers_reviewed"])
        self.assertEqual(6, payload["baseline_inventory"]["pytest_ini_ignored_sources_reviewed"])
        binding = payload["source_set_binding"]
        tracked = POLICY._tracked_policy_sources()
        approved_absent = set(POLICY._source_policy()) - tracked
        self.assertEqual(
            binding["tracked_policy_sources"]["count"],
            len(tracked),
        )
        self.assertEqual(
            binding["approved_clean_checkout_absent_policy_sources"]["count"],
            len(approved_absent),
        )
        self.assertEqual(
            {
                "Iris/build/description/v2/tests/test_live_migration_readiness_authorization.py",
                "Iris/build/description/v2/tests/test_live_migration_readiness_execution.py",
            },
            {
                row["source_file"]
                for row in payload["reviewed_sources"]
                if row.get("clean_checkout_optional") is True
            },
        )
        self.assertEqual(
            "Iris/_docs/round3/round3_test_taxonomy.json",
            payload["exact_taxonomy_projection"],
        )
        self.assertNotIn("rows", payload)

    def test_mixed_sources_and_exact_item_overrides_are_closed(self) -> None:
        payload = POLICY._source_policy_payload()
        mixed = payload["mixed_sources"]
        self.assertEqual(2, len(mixed))
        taxonomy = POLICY._taxonomy_source_classes()
        for row in mixed:
            source = row["source_file"]
            self.assertGreater(len(taxonomy[source]), 1)
            self.assertIn(row["default_classification"], taxonomy[source])
            self.assertGreater(len(row["item_overrides"]), 0)

    def test_unknown_missing_and_exclusion_approval_fail_closed(self) -> None:
        policy = POLICY._source_policy()
        actual = POLICY._actual_controlled_sources()
        self.assertEqual(set(), actual - policy.keys())
        excluded = POLICY._source_policy_payload()["excluded_sources"]
        self.assertEqual(8, len(excluded))
        for row in excluded:
            self.assertEqual("excluded", policy[row["source_file"]])
            for field in ("reason", "alternative_validation", "owner", "reviewed_at"):
                self.assertTrue(row[field])

    def test_vanished_tracked_source_fails_closed(self) -> None:
        actual = POLICY._actual_controlled_sources()
        tracked = POLICY._tracked_policy_sources()
        victim = next(source for source in sorted(tracked) if source in actual)
        with mock.patch.object(
            POLICY,
            "_actual_controlled_sources",
            return_value=actual - {victim},
        ):
            with self.assertRaisesRegex(RuntimeError, f"vanished={re.escape(victim)}"):
                POLICY._validate_policy_inventory()

    def test_denominator_contract_is_bidirectional_and_exact_files_are_unchanged(self) -> None:
        denominator = json.loads(POLICY.DENOMINATOR_PATH.read_text(encoding="utf-8"))
        self.assertTrue(denominator["enforcement"]["bidirectional_source_equality"])
        self.assertEqual(0, denominator["enforcement"]["included_source_collection_errors"])
        self.assertEqual(0, denominator["enforcement"]["all_contract_policy_deselections"])
        for relative in denominator["exact_authority_unchanged"].values():
            self.assertTrue((REPO / relative).is_file())
