from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


V2_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V2_ROOT.parents[3]
TOOLS = V2_ROOT / "tools" / "build"
FIXTURES = V2_ROOT / "tests" / "fixtures" / "iar_public_text_assessment"
RUNNER = TOOLS / "run_iar_public_text_assessment.py"
VALIDATOR = TOOLS / "validate_iar_public_text_assessment.py"
CONTRACT = (
    V2_ROOT
    / "data"
    / "iar_public_text_assessment"
    / "iar_public_text_assessment_contract.json"
)
INTEGRATION_INPUT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "iar_public_text_assessment"
    / "subjects"
    / "dvf_3_3_korean_naturalization_candidate"
    / "ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437"
    / "assessment_input.json"
)
HANDOFF = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "attempt-0024-publish-remediation-a"
    / "phase8"
    / "publish_acceptance_handoff_manifest.json"
)

if str(V2_ROOT) not in sys.path:
    sys.path.insert(0, str(V2_ROOT))

from tools.build import iar_public_text_assessment as iar
from tools.build import public_text_quality_acceptance as ptqa


class IarPublicTextAssessmentTest(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", *args],
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

    def temporary_root(self) -> tempfile.TemporaryDirectory[str]:
        return tempfile.TemporaryDirectory(dir=V2_ROOT / ".tmp")

    def write_input(self, root: Path, value: dict[str, object]) -> Path:
        path = root / "assessment_input.json"
        path.write_text(
            json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return path

    def test_generic_schema_runner_validator_and_deterministic_replay(self) -> None:
        with self.temporary_root() as temp_dir:
            output = Path(temp_dir) / "assessment_result.json"
            command = (
                str(RUNNER),
                "--input",
                str(FIXTURES / "dvf_assessment_input.json"),
                "--output",
                str(output),
                "--contract",
                str(CONTRACT),
            )
            first = self.run_cli(*command)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            first_bytes = output.read_bytes()
            second = self.run_cli(*command)
            self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
            self.assertEqual(first_bytes, output.read_bytes())
            validation = self.run_cli(
                str(VALIDATOR),
                "--input",
                str(FIXTURES / "dvf_assessment_input.json"),
                "--result",
                str(output),
                "--contract",
                str(CONTRACT),
                "--no-write",
            )
            self.assertEqual(
                validation.returncode,
                0,
                validation.stdout + validation.stderr,
            )
            payload = json.loads(validation.stdout)
            self.assertEqual(payload["status"], "PASS")
            self.assertEqual(payload["assessment_status"], "PASS")
            self.assertTrue(payload["no_write"])

    def test_subject_policy_and_ruleset_hash_mismatch_fail_closed(self) -> None:
        original = json.loads(
            (FIXTURES / "dvf_assessment_input.json").read_text(encoding="utf-8")
        )
        cases = (
            ("subject", "sha256", "environment", "text_identity_mismatch"),
            ("policy", "sha256", "environment", "text_identity_mismatch"),
            ("policy", "ruleset_sha256", "iar", "policy_ruleset_hash_mismatch"),
        )
        with self.temporary_root() as temp_dir:
            root = Path(temp_dir)
            for index, (section, field, domain, code) in enumerate(cases):
                changed = json.loads(json.dumps(original))
                changed[section][field] = f"{index + 1:064x}"
                path = self.write_input(root, changed)
                with self.assertRaises(iar.AssessmentFailure) as raised:
                    iar.build_assessment(path, contract_path=CONTRACT)
                self.assertEqual(raised.exception.domain, domain)
                self.assertEqual(raised.exception.code, code)

    def test_actual_finding_is_distinct_from_orchestration_failure(self) -> None:
        finding_result = iar.build_assessment(
            FIXTURES / "qg_assessment_input.json", contract_path=CONTRACT
        )
        self.assertEqual(finding_result["status"], "FAIL")
        self.assertEqual(finding_result["finding_count"], 1)
        self.assertEqual(
            finding_result["failure_attribution"]["subject_defect_counts"][
                "candidate"
            ],
            1,
        )
        self.assertEqual(
            sum(
                finding_result["failure_attribution"][
                    "technical_failure_counts"
                ].values()
            ),
            0,
        )

        def failing_writer(_path: Path, _result: dict[str, object]) -> None:
            raise OSError("temporary writer failure")

        with self.temporary_root() as temp_dir:
            with self.assertRaises(iar.AssessmentFailure) as raised:
                iar.materialize_assessment(
                    FIXTURES / "dvf_assessment_input.json",
                    Path(temp_dir) / "result.json",
                    contract_path=CONTRACT,
                    writer=failing_writer,
                )
        self.assertEqual(raised.exception.domain, "orchestration")
        envelope = iar.execution_error_payload(raised.exception)
        self.assertEqual(
            envelope["failure_attribution"]["temporary_orchestration_failure_count"],
            1,
        )
        self.assertEqual(
            sum(envelope["failure_attribution"]["subject_defect_counts"].values()),
            0,
        )

    def test_dvf_and_qg_subject_type_fixtures(self) -> None:
        dvf = iar.build_assessment(
            FIXTURES / "dvf_assessment_input.json", contract_path=CONTRACT
        )
        qg = iar.build_assessment(
            FIXTURES / "qg_assessment_input.json", contract_path=CONTRACT
        )
        self.assertEqual(dvf["subject"]["kind"], "dvf_fixture_subject")
        self.assertEqual(qg["subject"]["kind"], "qg_fixture_subject")
        self.assertEqual(dvf["status"], "PASS")
        self.assertEqual(qg["status"], "FAIL")
        self.assertEqual(dvf["metrics"][0]["metric_id"], "semantic_preservation_failure")
        self.assertEqual(qg["metrics"][0]["metric_id"], "coverage_quality_weak")

    def test_valid_fail_result_is_reproducible_not_a_runner_error(self) -> None:
        with self.temporary_root() as temp_dir:
            output = Path(temp_dir) / "assessment_result.json"
            run = self.run_cli(
                str(RUNNER),
                "--input",
                str(FIXTURES / "qg_assessment_input.json"),
                "--output",
                str(output),
                "--contract",
                str(CONTRACT),
            )
            self.assertEqual(run.returncode, 5, run.stdout + run.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "FAIL")
            self.assertEqual(payload["finding_count"], 1)
            validate = self.run_cli(
                str(VALIDATOR),
                "--input",
                str(FIXTURES / "qg_assessment_input.json"),
                "--result",
                str(output),
                "--contract",
                str(CONTRACT),
                "--no-write",
            )
            self.assertEqual(validate.returncode, 5, validate.stdout + validate.stderr)
            validation = json.loads(validate.stdout)
            self.assertEqual(validation["status"], "PASS")
            self.assertEqual(validation["assessment_status"], "FAIL")

    def test_preserved_candidate_reproduces_existing_detector_policy_result(self) -> None:
        generic = iar.build_assessment(INTEGRATION_INPUT, contract_path=CONTRACT)
        handoff = ptqa.validate_candidate_handoff(HANDOFF)
        existing = ptqa.compute_candidate_metric_snapshot(handoff)
        generic_projection = [
            {
                key: row[key]
                for key in (
                    "metric_id",
                    "denominator_id",
                    "disposition_class",
                    "numerator",
                    "denominator",
                    "exact_ratio",
                )
            }
            for row in generic["metrics"]
        ]
        self.assertEqual(generic_projection, existing["metric_rows"])
        self.assertEqual(
            generic["subject"]["sha256"],
            "ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437",
        )
        self.assertEqual(generic["metric_count"], 12)
        self.assertEqual(generic["finding_count"], 0)
        self.assertEqual(generic["status"], "PASS")
        self.assertTrue(all(row["threshold_satisfied"] for row in generic["metrics"]))
        self.assertEqual(generic["authority_effect"], "none")

    def test_existing_metric_policy_detector_projections_are_unchanged(self) -> None:
        foundation_path = (
            REPO_ROOT
            / "Iris"
            / "_docs"
            / "round3"
            / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
            / "foundation"
            / "public_text_quality_foundation_contract.json"
        )
        foundation = ptqa.load_json_strict(foundation_path)
        projections = (
            (
                ptqa.metric_registry_candidate(),
                foundation["metric_registry_candidate_hash"],
            ),
            (
                ptqa.denominator_registry_candidate(),
                foundation["denominator_registry_candidate_hash"],
            ),
            (
                ptqa.policy_candidate(),
                foundation["policy_candidate_hash"],
            ),
            (
                ptqa.detector_mapping_candidate(),
                foundation["detector_mapping_candidate_hash"],
            ),
        )
        for projection, expected_hash in projections:
            self.assertEqual(ptqa.canonical_hash(projection), expected_hash)


if __name__ == "__main__":
    unittest.main()
