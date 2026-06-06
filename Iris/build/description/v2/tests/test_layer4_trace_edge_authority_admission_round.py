from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = (
    ROOT
    / "staging"
    / "compose_contract_migration"
    / "layer4_trace_edge_authority_admission_round"
    / "generate_round_artifacts.py"
)


def load_generator():
    spec = importlib.util.spec_from_file_location(
        "layer4_trace_edge_authority_admission_round_generator",
        GENERATOR_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load layer4 trace-edge generator.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Layer4TraceEdgeAuthorityAdmissionRoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = load_generator()

    def test_generated_edges_are_relation_only_and_deterministic(self):
        first_edges, first_report = self.generator.build_generated_edges()
        second_edges, second_report = self.generator.build_generated_edges()

        self.assertEqual(first_edges, second_edges)
        self.assertGreater(first_report["generated_edge_count"], 0)
        self.assertEqual(first_report["generated_edge_count"], second_report["generated_edge_count"])

        allowed_keys = set(self.generator.EDGE_REQUIRED_FIELDS)
        for edge in first_edges:
            self.assertEqual(set(edge), allowed_keys)
            self.assertEqual(edge["edge_type"], self.generator.EDGE_TYPE)
            self.assertEqual(edge["edge_basis"], "generated_body_plan_relation_trace")
            self.assertNotIn("authority_class", edge)
            self.assertNotIn("admission_state", edge)

    def test_forbidden_basis_fails_loud(self):
        edges, _report = self.generator.build_generated_edges()
        self.assertGreater(len(edges), 0)
        invalid_edge = dict(edges[0])
        invalid_edge["edge_basis"] = "text_similarity"

        errors = self.generator.validate_edge(
            invalid_edge,
            self.generator.load_locked_row_ids(),
        )

        self.assertIn("edge_basis_invalid_or_forbidden", errors)

    def test_admission_fields_are_rejected_from_edge_rows(self):
        edges, _report = self.generator.build_generated_edges()
        self.assertGreater(len(edges), 0)
        invalid_edge = dict(edges[0])
        invalid_edge["authority_class"] = "current_detector_input"
        invalid_edge["admission_state"] = "admitted"

        errors = self.generator.validate_edge(
            invalid_edge,
            self.generator.load_locked_row_ids(),
        )

        self.assertIn("forbidden_field:authority_class", errors)
        self.assertIn("forbidden_field:admission_state", errors)

    def test_branch_decision_requires_generation_evidence_for_production(self):
        recovery_summary = {"explicit_trace_edge_candidate_count": 0}
        schema_report = {"schema_validation_pass": True}
        no_evidence_report = {
            "generated_edge_count": 0,
            "generation_time_relation_evidence": None,
        }

        deferred = self.generator.build_branch_decision(
            recovery_summary,
            no_evidence_report,
            schema_report,
            non_mutation_pinned=True,
        )
        self.assertEqual(deferred["branch_decision"], "NOT_RECOVERABLE_PRODUCTION_DEFERRED")

        edges, generation_report = self.generator.build_generated_edges()
        self.assertGreater(len(edges), 0)
        approved = self.generator.build_branch_decision(
            recovery_summary,
            generation_report,
            schema_report,
            non_mutation_pinned=True,
        )
        self.assertEqual(approved["branch_decision"], "NOT_RECOVERABLE_PRODUCTION_APPROVED")
        self.assertIsNotNone(
            approved["production_approval_basis"]["generation_time_relation_evidence"]
        )


if __name__ == "__main__":
    unittest.main()
