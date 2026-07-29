from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


V2_ROOT = Path(__file__).resolve().parents[1]
if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build.compose_layer3_io import file_sha256
from tools.build.compose_layer3_text import (
    STAGING_COMPOSE_CONTEXT,
    ComposeEntrypointGuardError,
    build_candidate_rendered,
)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


class KoreanProseCandidateRouteTest(unittest.TestCase):
    def build_fixture(self, root: Path, output_root: Path) -> tuple[Path, Path]:
        facts = root / "facts.jsonl"
        decisions = root / "decisions.jsonl"
        profiles = root / "profiles.json"
        identity = root / "identity.json"
        precedence = root / "precedence.json"
        policy = root / "policy.json"
        propositions = root / "propositions.jsonl"
        requirements = root / "requirements.jsonl"
        write_jsonl(
            facts,
            [
                {
                    "item_id": "Base.Test",
                    "identity_hint": "도구",
                    "primary_use": "수리 작업에서 쓰는 도구다",
                }
            ],
        )
        write_jsonl(
            decisions,
            [{"item_id": "Base.Test", "state": "adopted", "selected_role": "tool"}],
        )
        write_json(
            profiles,
            {
                "schema_version": "compose-profiles-v2",
                "profiles": {
                    "tool_body": {
                        "required_sections": ["identity_core", "use_core"],
                        "optional_sections": [],
                        "section_order": ["identity_core", "use_core"],
                    }
                },
            },
        )
        write_json(identity, {"identity_hint_profile_targets": {}})
        write_json(precedence, {})
        write_json(
            policy,
            {"realization_constraints": {"paragraph_split_character_threshold": 220}},
        )
        write_jsonl(
            propositions,
            [
                {
                    "item_id": "Base.Test",
                    "proposition_id": "Base.Test#identity",
                    "role": "identity",
                    "source_path": "facts.jsonl",
                    "source_field": "facts.identity_hint",
                    "source_value": "도구",
                    "semantic_key": "identity-key",
                },
                {
                    "item_id": "Base.Test",
                    "proposition_id": "Base.Test#use",
                    "role": "use",
                    "source_path": "facts.jsonl",
                    "source_field": "facts.primary_use",
                    "source_value": "수리 작업에서 쓰는 도구다",
                    "semantic_key": "use-key",
                },
            ],
        )
        write_jsonl(
            requirements,
            [
                {
                    "item_id": "Base.Test",
                    "requirement_id": "Base.Test#identity_core",
                    "resolved_profile": "tool_body",
                    "section_name": "identity_core",
                    "role": "identity",
                    "required": True,
                    "optional": False,
                    "ordering_index": 0,
                    "applicable_proposition_ids": ["Base.Test#identity"],
                    "emission_eligible": True,
                },
                {
                    "item_id": "Base.Test",
                    "requirement_id": "Base.Test#use_core",
                    "resolved_profile": "tool_body",
                    "section_name": "use_core",
                    "role": "use",
                    "required": True,
                    "optional": False,
                    "ordering_index": 1,
                    "applicable_proposition_ids": ["Base.Test#use"],
                    "emission_eligible": True,
                },
            ],
        )
        output = output_root / "candidate.json"
        trace = output_root / "trace.jsonl"
        build_candidate_rendered(
            facts_path=facts,
            decisions_path=decisions,
            profiles_path=profiles,
            identity_rules_path=identity,
            precedence_rules_path=precedence,
            policy_path=policy,
            source_proposition_inventory_path=propositions,
            body_plan_requirement_inventory_path=requirements,
            output_path=output,
            trace_path=trace,
            structural_path=output_root / "structural.jsonl",
            proposition_resolution_path=output_root / "resolution.jsonl",
            equivalence_proof_path=output_root / "proof.jsonl",
            attempt_root=output_root,
            compose_context=STAGING_COMPOSE_CONTEXT,
            expected_policy_sha256=file_sha256(policy),
        )
        return output, trace

    def test_candidate_bytes_are_directory_independent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            output_a, trace_a = self.build_fixture(base / "inputs", base / "attempt-a")
            output_b, trace_b = self.build_fixture(base / "inputs", base / "attempt-b")
            self.assertEqual(output_a.read_bytes(), output_b.read_bytes())
            self.assertEqual(trace_a.read_bytes(), trace_b.read_bytes())
            self.assertNotIn(b"attempt-a", output_a.read_bytes())

    def test_candidate_rejects_output_outside_attempt_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            inputs = base / "inputs"
            attempt = base / "attempt"
            self.build_fixture(inputs, attempt)
            with self.assertRaises(ComposeEntrypointGuardError):
                build_candidate_rendered(
                    facts_path=inputs / "facts.jsonl",
                    decisions_path=inputs / "decisions.jsonl",
                    profiles_path=inputs / "profiles.json",
                    identity_rules_path=inputs / "identity.json",
                    precedence_rules_path=inputs / "precedence.json",
                    policy_path=inputs / "policy.json",
                    source_proposition_inventory_path=inputs / "propositions.jsonl",
                    body_plan_requirement_inventory_path=inputs / "requirements.jsonl",
                    output_path=base / "outside.json",
                    trace_path=attempt / "trace2.jsonl",
                    structural_path=attempt / "structural2.jsonl",
                    proposition_resolution_path=attempt / "resolution2.jsonl",
                    equivalence_proof_path=attempt / "proof2.jsonl",
                    attempt_root=attempt,
                    compose_context=STAGING_COMPOSE_CONTEXT,
                    expected_policy_sha256=file_sha256(inputs / "policy.json"),
                )


if __name__ == "__main__":
    unittest.main()
