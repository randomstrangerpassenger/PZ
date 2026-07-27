from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.authority_phase9_10 import (
    _materialize_authority_phase9_10_fixture,
    _validate_bundled_authority_contracts,
    _validate_phase9_10_external_review,
    run_authority_phase9_10,
)
from tools.build.dvf_3_3_food_semantic.contracts import (
    FoodSemanticError,
    iter_jsonl_with_raw,
    load_json,
    load_jsonl,
    sha256_file,
    write_json,
    write_jsonl,
)


ATTEMPT_ROOT = (
    V2_ROOT
    / "staging/dvf_3_3_food_semantic_facts_authority/"
    "attempts/attempt-0007"
)
AUTHORITY_ROOT = (
    ATTEMPT_ROOT
    / "post_implementation_authority/authority-execution-0002"
)
CURRENT_FACTS = (
    V2_ROOT / "data/dvf_3_3_facts.jsonl"
)
CURRENT_MANIFEST = (
    V2_ROOT / "data/dvf_3_3_input_manifest.json"
)


class FoodSemanticAuthorityPhase910Test(unittest.TestCase):
    def test_reviewed_authority_closes_317_and_builds_candidate(
        self,
    ) -> None:
        before_facts = sha256_file(CURRENT_FACTS)
        before_manifest = sha256_file(CURRENT_MANIFEST)
        with tempfile.TemporaryDirectory(
            dir=ATTEMPT_ROOT / "post_implementation_authority"
        ) as temp_dir:
            output_root = Path(temp_dir) / "authority-fixture"
            report = _materialize_authority_phase9_10_fixture(
                REPO_ROOT,
                ATTEMPT_ROOT,
                AUTHORITY_ROOT,
                output_root=output_root,
            )
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(
                report["target_semantic_disposition_count"],
                317,
            )
            self.assertEqual(
                report["approved_total_proposition_count"],
                322,
            )
            phase9 = output_root / "phase9_coverage"
            automatic = load_jsonl(
                phase9 / "approved_automatic_fact_ledger.jsonl"
            )
            disposition = load_jsonl(
                phase9 / "full_317_semantic_disposition.jsonl"
            )
            self.assertEqual(len(automatic), 84)
            self.assertEqual(len(disposition), 317)
            self.assertTrue(
                all(
                    row["approval_status"] == "approved"
                    and row["automatic_review_decision_id"] == "D8"
                    for row in automatic
                )
            )
            self.assertTrue(
                all(
                    row["authority_terminal_disposition"] is True
                    for row in disposition
                )
            )
            coverage = load_json(
                phase9 / "coverage_reconciliation_report.json"
            )
            self.assertEqual(coverage["status"], "PASS_COMPLETE")
            self.assertEqual(coverage["coverage_gap"], 0)
            self.assertEqual(coverage["double_count"], 0)

            phase10 = output_root / "phase10_candidate"
            candidate_path = (
                phase10 / "candidate_successor_facts.jsonl"
            )
            candidate_rows = load_jsonl(candidate_path)
            self.assertEqual(len(candidate_rows), 2105)
            changed = [
                row
                for row in candidate_rows
                if row.get("food_semantic_authority_state")
                == "approved_candidate"
            ]
            self.assertEqual(len(changed), 317)
            assertions = [
                assertion
                for row in changed
                for assertion in row["food_semantic_assertions"]
            ]
            self.assertEqual(len(assertions), 322)
            self.assertTrue(
                all(
                    row["authority_state"] == "approved_candidate"
                    for row in assertions
                )
            )
            current_by_item = {
                row["item_id"]: (row, raw)
                for row, raw in iter_jsonl_with_raw(CURRENT_FACTS)
            }
            candidate_by_item = {
                row["item_id"]: (row, raw)
                for row, raw in iter_jsonl_with_raw(candidate_path)
            }
            changed_ids = {row["item_id"] for row in changed}
            self.assertEqual(
                {
                    item_id: raw
                    for item_id, (_, raw) in candidate_by_item.items()
                    if item_id not in changed_ids
                },
                {
                    item_id: raw
                    for item_id, (_, raw) in current_by_item.items()
                    if item_id not in changed_ids
                },
            )
            for item_id in changed_ids:
                current_row = current_by_item[item_id][0]
                candidate_row = candidate_by_item[item_id][0]
                self.assertTrue(
                    all(
                        candidate_row[key] == value
                        for key, value in current_row.items()
                    )
                )
            validation = load_json(
                phase10 / "candidate_validation_report.json"
            )
            self.assertEqual(validation["status"], "PASS")
            self.assertEqual(
                validation["non_target_row_byte_mismatch_count"],
                0,
            )
            before_files = {
                path.relative_to(output_root).as_posix(): path.read_bytes()
                for path in output_root.rglob("*")
                if path.is_file()
            }
            rerun = _materialize_authority_phase9_10_fixture(
                REPO_ROOT,
                ATTEMPT_ROOT,
                AUTHORITY_ROOT,
                output_root=output_root,
            )
            self.assertEqual(rerun, report)
            after_files = {
                path.relative_to(output_root).as_posix(): path.read_bytes()
                for path in output_root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(after_files, before_files)
        self.assertEqual(sha256_file(CURRENT_FACTS), before_facts)
        self.assertEqual(sha256_file(CURRENT_MANIFEST), before_manifest)

    def test_missing_phase8_review_blocks_before_output(self) -> None:
        with tempfile.TemporaryDirectory(
            dir=ATTEMPT_ROOT / "post_implementation_authority"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            authority_copy = temp_root / "authority-input"
            shutil.copytree(AUTHORITY_ROOT, authority_copy)
            (
                authority_copy
                / "external_authority_materialization_review.json"
            ).unlink()
            output_root = temp_root / "authority-output"
            with self.assertRaises(FoodSemanticError):
                _materialize_authority_phase9_10_fixture(
                    REPO_ROOT,
                    ATTEMPT_ROOT,
                    authority_copy,
                    output_root=output_root,
                )
            self.assertFalse((output_root / "phase9_coverage").exists())
            self.assertFalse((output_root / "phase10_candidate").exists())

    def test_authority_execution_requires_external_code_review(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            dir=ATTEMPT_ROOT / "post_implementation_authority"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            authority_copy = temp_root / "authority-input"
            shutil.copytree(AUTHORITY_ROOT, authority_copy)
            review_path = (
                authority_copy
                / "phase9_10_external_implementation_review.json"
            )
            if review_path.exists():
                review_path.unlink()
            output_root = temp_root / "authority-output"
            with self.assertRaises(FoodSemanticError):
                run_authority_phase9_10(
                    REPO_ROOT,
                    ATTEMPT_ROOT,
                    authority_copy,
                    output_root=output_root,
                )
            self.assertFalse((output_root / "phase9_coverage").exists())
            self.assertFalse((output_root / "phase10_candidate").exists())

    def test_external_code_review_gate_is_exact_and_tamper_evident(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            dir=ATTEMPT_ROOT / "post_implementation_authority"
        ) as temp_dir:
            authority_copy = Path(temp_dir) / "authority-input"
            shutil.copytree(AUTHORITY_ROOT, authority_copy)
            code_paths = [
                (
                    "Iris/build/description/v2/tools/build/"
                    "dvf_3_3_food_semantic/authority_phase9_10.py"
                ),
                (
                    "Iris/build/description/v2/tools/build/"
                    "run_dvf_3_3_food_semantic_authority_phase9_10.py"
                ),
                (
                    "Iris/build/description/v2/tests/"
                    "test_dvf_3_3_food_semantic_authority_phase9_10.py"
                ),
            ]
            decisions_path = (
                V2_ROOT
                / "owner_inputs/"
                "dvf_3_3_food_semantic_facts_authority/"
                "owner_reserved_decisions.json"
            )
            automatic_path = (
                ATTEMPT_ROOT
                / "phase7_automatic_mapping/"
                "automatic_food_fact_ledger.jsonl"
            )
            review = {
                "verdict": "PASS",
                "phase9_10_scope_verdict": "PASS",
                "reviewer_identity": "Codex Reviewer",
                "reviewer_is_implementation_author": False,
                "finding_counts": {
                    "critical": 0,
                    "important": 0,
                    "minor": 0,
                },
                "authority_execution_allowed": True,
                "current_mutation_authorized": False,
                "terminal_independent_gate_credit": 0,
                "reviewed_phase8_external_review_sha256": (
                    "15a937be6dea2754a43f2359bffbed8087f95b5c8c613"
                    "644698d9822319d642a"
                ),
                "reviewed_owner_decisions_sha256": sha256_file(
                    decisions_path
                ),
                "reviewed_automatic_source_ledger_sha256": sha256_file(
                    automatic_path
                ),
                "reviewed_code_artifacts": [
                    {
                        "path": relative,
                        "sha256": sha256_file(REPO_ROOT / relative),
                        "byte_count": (REPO_ROOT / relative).stat().st_size,
                    }
                    for relative in code_paths
                ],
            }
            review_path = (
                authority_copy
                / "phase9_10_external_implementation_review.json"
            )
            write_json(review_path, review, write_once=False)
            accepted = _validate_phase9_10_external_review(
                REPO_ROOT,
                ATTEMPT_ROOT,
                authority_copy,
            )
            self.assertEqual(accepted["verdict"], "PASS")
            review["reviewed_code_artifacts"][0]["sha256"] = "0" * 64
            write_json(review_path, review, write_once=False)
            with self.assertRaises(FoodSemanticError):
                _validate_phase9_10_external_review(
                    REPO_ROOT,
                    ATTEMPT_ROOT,
                    authority_copy,
                )

    def test_all_three_sealed_contract_drifts_are_rejected(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(
            dir=REPO_ROOT
        ) as temp_dir:
            fixture_root = Path(temp_dir) / "repo"
            fixture_attempt = (
                fixture_root
                / "Iris/build/description/v2/staging/"
                "dvf_3_3_food_semantic_facts_authority/"
                "attempts/attempt-0007"
            )
            bundle_source = (
                ATTEMPT_ROOT
                / "phase13_closeout/"
                "implementation_complete_bundle.json"
            )
            bundle_target = (
                fixture_attempt
                / "phase13_closeout/"
                "implementation_complete_bundle.json"
            )
            bundle_target.parent.mkdir(parents=True)
            shutil.copy2(bundle_source, bundle_target)
            relative_contracts = [
                (
                    "Iris/_docs/authority/food_semantic/"
                    "food_semantic_schema.json"
                ),
                (
                    "Iris/_docs/authority/food_semantic/"
                    "proposition_licensing_contract.json"
                ),
                (
                    "Iris/_docs/authority/food_semantic/"
                    "forbidden_inference_registry.json"
                ),
            ]
            for relative in relative_contracts:
                target = fixture_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(REPO_ROOT / relative, target)
            sealed = _validate_bundled_authority_contracts(
                fixture_root,
                fixture_attempt,
            )
            self.assertEqual(len(sealed["identities"]), 3)
            for relative in relative_contracts:
                target = fixture_root / relative
                original = target.read_bytes()
                target.write_bytes(original + b" ")
                with self.assertRaises(FoodSemanticError):
                    _validate_bundled_authority_contracts(
                        fixture_root,
                        fixture_attempt,
                    )
                target.write_bytes(original)

    def test_phase8_tamper_blocks_before_output(self) -> None:
        with tempfile.TemporaryDirectory(
            dir=ATTEMPT_ROOT / "post_implementation_authority"
        ) as temp_dir:
            temp_root = Path(temp_dir)
            authority_copy = temp_root / "authority-input"
            shutil.copytree(AUTHORITY_ROOT, authority_copy)
            curated_path = (
                authority_copy
                / "phase8_curation/curated_fact_ledger.jsonl"
            )
            rows = load_jsonl(curated_path)
            write_jsonl(curated_path, rows[:-1], write_once=False)
            output_root = temp_root / "authority-output"
            with self.assertRaises(FoodSemanticError):
                _materialize_authority_phase9_10_fixture(
                    REPO_ROOT,
                    ATTEMPT_ROOT,
                    authority_copy,
                    output_root=output_root,
                )
            self.assertFalse((output_root / "phase9_coverage").exists())
            self.assertFalse((output_root / "phase10_candidate").exists())

    def test_protected_output_sink_is_rejected(self) -> None:
        with self.assertRaises(FoodSemanticError):
            _materialize_authority_phase9_10_fixture(
                REPO_ROOT,
                ATTEMPT_ROOT,
                AUTHORITY_ROOT,
                output_root=V2_ROOT / "data",
            )


if __name__ == "__main__":
    unittest.main()
