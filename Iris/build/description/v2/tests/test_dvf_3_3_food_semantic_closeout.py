from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.dvf_3_3_food_semantic.closeout import (
    FORBIDDEN_IMPLEMENTATION_CLAIMS,
    _implementation_files,
    scan_claim_values,
)
from tools.build.dvf_3_3_food_semantic.contracts import FoodSemanticError
from tools.build.dvf_3_3_food_semantic.contracts import load_json
from tools.build.dvf_3_3_food_semantic_facts_authority import (
    FOCUSED_VALIDATION_COMMAND,
    build_parser,
    record_focused_validation,
    resolve_attempt_root,
)


class FoodSemanticCloseoutTest(unittest.TestCase):
    def test_implementation_claim_ceiling(self) -> None:
        staging = V2_ROOT / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=staging) as temp_dir:
            path = Path(temp_dir) / "claims.json"
            path.write_text(
                json.dumps(
                    {
                        "safe": "implementation_complete_proposal_only",
                        "forbidden": "canonical_complete",
                    }
                ),
                encoding="utf-8",
            )
            report = scan_claim_values([path])
            self.assertEqual(report["forbidden_claim_emission_count"], 1)
            self.assertIn("canonical_complete", FORBIDDEN_IMPLEMENTATION_CLAIMS)

    def test_validation_record_fails_closed(self) -> None:
        staging = V2_ROOT / "staging"
        staging.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=staging) as temp_dir:
            attempt_root = Path(temp_dir)
            with self.assertRaises(FoodSemanticError):
                record_focused_validation(
                    attempt_root,
                    command=FOCUSED_VALIDATION_COMMAND,
                    exit_code=1,
                )
            with self.assertRaises(FoodSemanticError):
                record_focused_validation(
                    attempt_root,
                    command="python tests.py",
                    exit_code=0,
                )

    def test_attempt_root_rejects_traversal(self) -> None:
        with self.assertRaises(FoodSemanticError):
            resolve_attempt_root(REPO_ROOT, "../escape")
        valid = resolve_attempt_root(REPO_ROOT, "attempt-0001")
        self.assertEqual(valid.name, "attempt-0001")

    def test_authority_command_is_exposed_but_requires_exact_inputs(self) -> None:
        parser = build_parser()
        args = parser.parse_args(
            ["authority", "--attempt-id", "attempt-0019"]
        )
        self.assertEqual(args.command, "authority")
        self.assertIsNone(args.owner_decisions)
        self.assertIsNone(args.semantic_approval)
        self.assertIsNone(args.external_review)
        self.assertIsNone(args.curated_ledger)
        prepare = parser.parse_args(
            ["prepare-closeout", "--attempt-id", "attempt-0020"]
        )
        self.assertEqual(prepare.command, "prepare-closeout")
        terminal = parser.parse_args(
            ["terminal-seal", "--attempt-id", "attempt-0020"]
        )
        self.assertEqual(terminal.command, "terminal-seal")

    def test_successful_attempt_stays_below_authority_claim_ceiling(self) -> None:
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
        final_machine = load_json(
            attempt
            / "phase13_closeout/implementation_final_machine_report.json"
        )
        claim_scan = load_json(
            attempt / "phase13_closeout/implementation_claim_ceiling_scan.json"
        )
        protected = load_json(
            attempt
            / "phase11_successor/protected_surface_hashes_after.json"
        )
        machine_validation = load_json(
            attempt
            / "phase13_closeout/implementation_machine_validation_report.json"
        )
        self.assertTrue(final_machine["implementation_build_complete"])
        self.assertFalse(final_machine["authority_execution_authorized"])
        self.assertFalse(final_machine["sealed_successor_handoff_complete"])
        self.assertEqual(claim_scan["forbidden_claim_emission_count"], 0)
        self.assertEqual(protected["changed_count"], 0)
        self.assertEqual(machine_validation["status"], "PASS")
        self.assertEqual(machine_validation["blocking_predicate_count"], 0)
        artifact_paths = {
            path.relative_to(REPO_ROOT).as_posix()
            for path in _implementation_files(REPO_ROOT, attempt)
        }
        self.assertTrue(
            {
                (
                    "Iris/build/description/v2/tools/build/"
                    "dvf_3_3_food_semantic/d16_candidate_sources/"
                    "run_dvf_3_3_korean_prose_naturalization.py"
                ),
                (
                    "Iris/build/description/v2/tools/build/"
                    "dvf_3_3_food_semantic/d16_candidate_sources/"
                    "validate_dvf_3_3_korean_prose_naturalization.py"
                ),
                (
                    "Iris/build/description/v2/tools/build/"
                    "dvf_3_3_food_semantic/d16_candidate_sources/"
                    "test_dvf_3_3_korean_prose_acceptance_gate.py"
                ),
                (
                    "Iris/build/description/v2/tools/build/"
                    "dvf_3_3_food_semantic/d16_candidate_sources/"
                    "test_dvf_3_3_korean_prose_semantic_preservation.py"
                ),
            }
            <= artifact_paths
        )


if __name__ == "__main__":
    unittest.main()
