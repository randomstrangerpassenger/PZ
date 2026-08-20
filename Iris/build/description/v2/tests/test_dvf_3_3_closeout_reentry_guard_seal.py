from __future__ import annotations

import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
TOOLS = REPO / "Iris/build/description/v2/tools/build"
ROOT = REPO / "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal"
SCRIPT = TOOLS / "run_dvf_3_3_closeout_reentry_guard_seal.py"


def load_common_module():
    path = TOOLS / "dvf_3_3_closeout_reentry_guard_seal_common.py"
    spec = importlib.util.spec_from_file_location(
        "dvf_3_3_closeout_reentry_guard_seal_common_for_test",
        path,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load closeout reentry guard common module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    sys.path.insert(0, str(TOOLS))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(TOOLS))
    return module

CONTRACT_PROBE_REQUEST = {
    "surface_lines": [
        {
            "fixture_id": "architecture_publish_boundary",
            "path": "docs/ARCHITECTURE.md",
            "text": (
                "Publish Boundary는 public text acceptance, semantic quality "
                "acceptance, package publication, release / Workshop readiness, "
                "manual QA를 별도 축으로 둔다."
            ),
        },
        {
            "fixture_id": "decisions_publish_boundary",
            "path": "docs/DECISIONS.md",
            "text": (
                "  * Publish Boundary 책임은 public text acceptance, semantic "
                "quality acceptance, package publication, release / Workshop "
                "readiness, manual QA다."
            ),
        },
        {
            "fixture_id": "architecture_quality_heading",
            "path": "docs/ARCHITECTURE.md",
            "text": (
                "Public Text Quality / public acceptance / release readiness"
            ),
        },
        {
            "fixture_id": "roadmap_followup_routing",
            "path": "docs/ROADMAP.md",
            "text": (
                "  * 후속 라우팅은 public acceptance / release readiness -> "
                "Publish Boundary Closure로 고정한다."
            ),
        },
        {
            "fixture_id": "blocked_release_readiness",
            "path": "docs/ARCHITECTURE.md",
            "text": "Release readiness is achieved by this closeout.",
        },
    ],
    "predecessor_contexts": [
        "2105 is current hard gate",
        "2084 is runtime authority",
        "21 is current debt",
        (
            "2105 is historical predecessor trace and must not become "
            "current debt"
        ),
    ],
    "claim_texts": [
        "Problem7 PASS makes Problem8 complete",
        "pre-apply readiness means live migration execution complete",
    ],
}
FORBIDDEN_SURFACE_PROBE_REQUEST = {
    "fixture_text": "release readiness achieved\n",
}
STRUCTURED_MANIFEST_PROBE_REQUEST = {
    "fixtures": [
        {
            "fixture_id": "required_artifact_path_identifier",
            "document": {
                "schema_version": "round3-current-route-required-validations-v1",
                "required_artifacts": [
                    {
                        "path": "evidence/public_text_quality_acceptance/report.json",
                        "checks": [],
                    }
                ],
                "required_tests": [],
            },
        },
        {
            "fixture_id": "required_test_id_identifier",
            "document": {
                "schema_version": "round3-current-route-required-validations-v1",
                "required_artifacts": [],
                "required_tests": [
                    {
                        "test_id": (
                            "test_public_text_quality_acceptance."
                            "AcceptanceTest.test_contract"
                        )
                    }
                ],
            },
        },
        {
            "fixture_id": "claim_field_overclaim",
            "document": {
                "schema_version": "round3-current-route-required-validations-v1",
                "claim": "public text acceptance complete",
                "required_artifacts": [],
                "required_tests": [],
            },
        },
        {
            "fixture_id": "reason_required_gate_reference",
            "document": {
                "schema_version": "round3-current-route-required-validations-v1",
                "reason": (
                    "standalone Publish Boundary public-text acceptance "
                    "required gate"
                ),
                "required_artifacts": [],
                "required_tests": [],
            },
        },
        {
            "fixture_id": "reason_required_gate_overclaim",
            "document": {
                "schema_version": "round3-current-route-required-validations-v1",
                "reason": (
                    "standalone public text acceptance required gate "
                    "complete"
                ),
                "required_artifacts": [],
                "required_tests": [],
            },
        },
        {
            "fixture_id": "unknown_field_overclaim",
            "document": {
                "schema_version": "round3-current-route-required-validations-v1",
                "future_note": "public text acceptance complete",
                "required_artifacts": [],
                "required_tests": [],
            },
        },
        {
            "fixture_id": "identifier_object_disguise",
            "document": {
                "schema_version": "round3-current-route-required-validations-v1",
                "required_artifacts": [
                    {
                        "path": {
                            "value": (
                                "evidence/public_text_quality_acceptance/"
                                "report.json"
                            )
                        },
                        "checks": [],
                    }
                ],
                "required_tests": [],
            },
        },
        {
            "fixture_id": "wrong_schema",
            "document": {
                "schema_version": "round3-current-route-required-validations-v0",
                "required_artifacts": [],
                "required_tests": [],
            },
        },
        {
            "fixture_id": "duplicate_schema_key",
            "raw_text": (
                '{"schema_version":"round3-current-route-required-validations-v1",'
                '"schema_version":"round3-current-route-required-validations-v1",'
                '"required_artifacts":[],"required_tests":[]}'
            ),
        },
    ],
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_probe(flag: str, request: dict | None = None) -> dict:
    result = subprocess.run(
        [sys.executable, "-B", str(SCRIPT), flag],
        cwd=REPO,
        input=(
            json.dumps(request, ensure_ascii=False, sort_keys=True)
            if request is not None
            else None
        ),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"closeout probe failed: {flag}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return json.loads(result.stdout.strip().splitlines()[-1])


def load_contract_probe() -> dict:
    return run_probe("--probe-contract", CONTRACT_PROBE_REQUEST)


def run_validation() -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [
            sys.executable,
            "-B",
            str(SCRIPT),
            "--mode",
            "validate",
            "--require-complete",
            "--report-json",
            "--no-write-report",
        ],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    report = json.loads(result.stdout.strip().splitlines()[-1])
    return result, report


class DvfCloseoutReentryGuardSealTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.run_generator()
        result, report = run_validation()
        if result.returncode != 0:
            raise AssertionError(f"closeout/reentry guard validation failed: {report['errors']}")

    @classmethod
    def run_generator(cls) -> None:
        probe = load_contract_probe()
        route_summary = probe["route_summary"]
        if route_summary.get("runner_result_valid") is not True:
            raise AssertionError(
                "tracked historical closeout route baseline is missing or invalid; "
                "synthetic PASS fallback is forbidden"
            )
        final_path = ROOT / "phase7/final_closeout_reentry_guard_seal_report.json"
        if final_path.exists():
            final = load_json(final_path)
            if (
                final.get("status") == "PASS"
                and final.get("machine_contract_status") == "PASS"
                and final.get("canonical_seal_allowed") is True
            ):
                return
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--mode", "generate"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(
                "closeout/reentry guard generation failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

    def test_taxonomy_splits_allowed_and_forbidden_claim_classes(self) -> None:
        taxonomy = load_json(ROOT / "phase2/dvf_3_3_closeout_claim_taxonomy.json")
        report = load_json(ROOT / "phase2/completion_vocabulary_separation_report.json")

        allowed = {row["claim_class"] for row in taxonomy["allowed_claim_classes"]}
        forbidden = {row["claim_class"] for row in taxonomy["forbidden_overclaim_classes"]}

        self.assertEqual(taxonomy["status"], "PASS")
        self.assertFalse(taxonomy["standalone_complete_allowed"])
        self.assertIn("terminal_disposition_complete", allowed)
        self.assertIn("broad_consumer_completion", allowed)
        self.assertIn("cutover_subset_completion", allowed)
        self.assertIn("problem7_full_current_route_validation_pass", allowed)
        self.assertIn("release_readiness", forbidden)
        self.assertIn("runtime_authority_current_without_runtime_authority_input", forbidden)
        self.assertEqual(report["standalone_complete_claim_count"], 0)
        self.assertEqual(report["complete_suffix_violation_count"], 0)

    def test_claim_surface_scan_is_fail_closed_and_not_self_scanned(self) -> None:
        scan = load_json(ROOT / "phase1/claim_surface_scan_manifest.json")
        inventory = load_json(ROOT / "phase1/closeout_claim_surface_inventory.json")
        included = {path.replace("\\", "/") for path in scan["included_files"]}

        self.assertEqual(scan["status"], "PASS")
        self.assertEqual(inventory["status"], "PASS")
        self.assertEqual(scan["missing_required_surface_family_count"], 0)
        self.assertEqual(scan["blocked_claim_surface_count"], 0)
        self.assertEqual(scan["forbidden_overclaim_violation_count"], 0)
        self.assertEqual(scan["forbidden_predecessor_reentry_violation_count"], 0)
        self.assertEqual(inventory["blocked_claim_surface_count"], 0)
        self.assertFalse(
            any(
                path.startswith(
                    "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase1/"
                )
                for path in included
            )
        )
        probe = run_probe(
            "--probe-structured-manifest",
            STRUCTURED_MANIFEST_PROBE_REQUEST,
        )
        cases = probe["cases"]
        for fixture_id, pointer in (
            (
                "required_artifact_path_identifier",
                "/required_artifacts/0/path",
            ),
            (
                "required_test_id_identifier",
                "/required_tests/0/test_id",
            ),
            (
                "reason_required_gate_reference",
                "/reason",
            ),
        ):
            with self.subTest(fixture_id=fixture_id):
                case = cases[fixture_id]
                self.assertEqual(case["status"], "PASS")
                self.assertEqual(case["blocker_count"], 0)
                leaf = next(
                    row
                    for row in case["string_leaves"]
                    if row["json_pointer"] == pointer
                )
                if fixture_id == "reason_required_gate_reference":
                    self.assertEqual(leaf["semantic_role"], "claim_text")
                    self.assertEqual(
                        leaf["classification"],
                        "fail_closed_claim_text_scan",
                    )
                else:
                    self.assertEqual(leaf["semantic_role"], "identifier")
                    self.assertEqual(
                        leaf["classification"],
                        "identifier_excluded_from_claim_text",
                    )
        for fixture_id in (
            "claim_field_overclaim",
            "reason_required_gate_overclaim",
            "unknown_field_overclaim",
            "identifier_object_disguise",
            "wrong_schema",
            "duplicate_schema_key",
        ):
            with self.subTest(fixture_id=fixture_id):
                self.assertEqual(cases[fixture_id]["status"], "FAIL")
                self.assertGreater(cases[fixture_id]["blocker_count"], 0)
        self.assertEqual(
            cases["claim_field_overclaim"]["blockers"][0]["role"],
            "forbidden_overclaim_violation",
        )
        self.assertEqual(
            cases["unknown_field_overclaim"]["blockers"][0]["role"],
            "forbidden_overclaim_violation",
        )
        self.assertTrue(
            any(
                row.get("code") == "identifier_field_container_invalid"
                for row in cases["identifier_object_disguise"]["blockers"]
            )
        )
        self.assertTrue(
            any(
                row.get("code") == "manifest_schema_version_invalid"
                for row in cases["wrong_schema"]["blockers"]
            )
        )
        self.assertTrue(
            any(
                row.get("code") == "strict_json_parse_failed"
                for row in cases["duplicate_schema_key"]["blockers"]
            )
        )

    def test_top_doc_publish_boundary_definitions_do_not_overclaim_readiness(self) -> None:
        probe = load_contract_probe()
        surface_lines = probe["surface_lines"]
        for fixture_id in (
            "architecture_publish_boundary",
            "decisions_publish_boundary",
            "architecture_quality_heading",
            "roadmap_followup_routing",
        ):
            with self.subTest(fixture_id=fixture_id):
                row = surface_lines[fixture_id]
                self.assertIsNotNone(row)
                self.assertEqual(
                    row["role"],
                    "forbidden_overclaim_definition",
                )
                self.assertTrue(row["definition_context"])
                self.assertEqual(row["classification"], "classified")

        blocked = surface_lines["blocked_release_readiness"]
        self.assertIsNotNone(blocked)
        self.assertEqual(blocked["role"], "forbidden_overclaim_violation")
        self.assertFalse(blocked["definition_context"])
        self.assertEqual(blocked["classification"], "blocked")

        common = load_common_module()
        fixtures = (
            (
                common.ARCHITECTURE_DOC,
                "  * Reusable public-text assessment는 DVF/QG subject에 적용되는 오프라인 evidence producer로 유지하며 Publish Boundary가 그 결과의 acceptance를 별도로 판단한다.",
            ),
            (
                common.ARCHITECTURE_DOC,
                "  * public-text acceptance와 publication / release acceptance를 소유한다.",
            ),
            (
                common.DECISIONS_DOC,
                "  * `PublicTextQualityAcceptanceCurrentRouteTest._phase7_self_test()`는 동일 self-test producer를 여러 test가 다시 실행한 뒤 서로 다른 result case만 읽는 명시적 우선 후보다.",
            ),
            (
                common.ROADMAP_DOC,
                "- exact result/subject identity 없이 canonical review/seal을 주장하거나 이 component evidence를 Public Text Quality PASS, Publish Boundary PASS 또는 release readiness로 확대하기",
            ),
        )
        for path, line in fixtures:
            with self.subTest(path=path.name, line=line):
                row = common.classify_surface_line(path, line)
                self.assertIsNotNone(row)
                self.assertEqual(row["classification"], "classified")
                self.assertTrue(row["definition_context"])

        blocked_fixtures = (
            (common.ROADMAP_DOC, "검토 없이 release readiness achieved"),
            (common.ROADMAP_DOC, "release readiness achieved without review"),
            (common.ROADMAP_DOC, "not only reviewed but release readiness complete"),
            (common.ROADMAP_DOC, "not only release readiness but package readiness"),
            (common.ARCHITECTURE_DOC, "이 evaluator가 public-text acceptance authority를 소유한다."),
            (common.DECISIONS_DOC, "`BadTest` producer가 public-text acceptance를 결정하고 승인한다."),
            (common.ARCHITECTURE_DOC, "Publish Boundary가 public-text acceptance 완료를 소유한다."),
        )
        for path, line in blocked_fixtures:
            with self.subTest(blocked_path=path.name, line=line):
                row = common.classify_surface_line(path, line)
                self.assertIsNotNone(row)
                self.assertEqual(row["classification"], "blocked")
                self.assertFalse(row["definition_context"])

    def test_predecessor_reentry_negative_fixtures_fail_closed(self) -> None:
        guard = load_json(ROOT / "phase3/predecessor_reentry_guard_report.json")
        raw = load_json(ROOT / "phase3/raw_predecessor_authority_read_report.json")
        debt = load_json(ROOT / "phase3/current_debt_reentry_report.json")
        dual = load_json(ROOT / "phase3/dual_reentry_authority_report.json")

        self.assertEqual(guard["status"], "PASS")
        self.assertEqual(len(guard["fixtures"]), 5)
        self.assertEqual(guard["predecessor_reentry_violation_count"], 0)
        self.assertEqual(guard["current_hard_gate_predecessor_direct_use_count"], 0)
        self.assertEqual(guard["runtime_authority_predecessor_direct_use_count"], 0)
        self.assertEqual(guard["current_debt_predecessor_direct_use_count"], 0)
        self.assertTrue(all(row["status"] == "PASS" for row in guard["fixtures"]))
        self.assertEqual(raw["RAW_PREDECESSOR_AUTHORITY_READ"], 0)
        self.assertEqual(debt["CURRENT_DEBT_REENTRY"], 0)
        self.assertEqual(dual["dual_reentry_authority_count"], 0)

        contexts = load_contract_probe()["predecessor_contexts"]
        self.assertIn(
            "current_hard_gate_reentry",
            contexts["2105 is current hard gate"],
        )
        self.assertIn(
            "runtime_authority_reentry",
            contexts["2084 is runtime authority"],
        )
        self.assertIn(
            "current_debt_reentry",
            contexts["21 is current debt"],
        )
        self.assertEqual(
            contexts[
                "2105 is historical predecessor trace and must not become "
                "current debt"
            ],
            [],
        )

    def test_closeout_boundary_rejects_problem7_and_readiness_promotion(self) -> None:
        boundary = load_json(ROOT / "phase4/closeout_claim_boundary_guard_report.json")
        promotion = load_json(ROOT / "phase4/problem7_to_closeout_guard_promotion_guard_report.json")

        self.assertEqual(boundary["status"], "PASS")
        self.assertEqual(len(boundary["fixtures"]), 6)
        self.assertEqual(boundary["ambiguous_complete_claim_count"], 0)
        self.assertEqual(boundary["broad_cutover_collision_count"], 0)
        self.assertEqual(boundary["pre_apply_readiness_to_live_completion_promotion_count"], 0)
        self.assertEqual(boundary["problem7_pass_to_closeout_guard_completion_promotion_count"], 0)
        self.assertEqual(boundary["problem7_partial_flattened_to_complete_count"], 0)
        self.assertEqual(boundary["forbidden_overclaim_count"], 0)
        self.assertEqual(promotion["problem7_closeout_state"], "partial")
        self.assertEqual(promotion["problem7_pass_to_closeout_guard_completion_promotion_count"], 0)

        claims = load_contract_probe()["claim_texts"]
        self.assertIn(
            "problem7_to_problem8_completion_promotion",
            claims["Problem7 PASS makes Problem8 complete"],
        )
        self.assertIn(
            "live_migration_execution_complete_without_execution",
            claims[
                "pre-apply readiness means live migration execution complete"
            ],
        )

    def test_manifest_adoption_is_governance_only_and_runner_visible(self) -> None:
        adoption = load_json(ROOT / "phase5/closeout_reentry_guard_manifest_adoption_report.json")
        live_manifest = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")

        self.assertEqual(adoption["status"], "PASS")
        self.assertEqual(adoption["required_gate_adoption_status"], "adopted_required_gate")
        self.assertTrue(adoption["live_manifest_contains_required_artifacts"])
        self.assertTrue(adoption["live_manifest_contains_required_tests"])
        self.assertEqual(adoption["dual_reentry_authority_count"], 0)
        self.assertFalse(adoption["governance_adopted_required_gate_is_runtime_adopted_row"])
        self.assertFalse(adoption["manifest_adoption_creates_runtime_mutation_claim"])

        required_paths = {row["path"] for row in live_manifest["required_artifacts"]}
        required_tests = {row["test_id"] for row in live_manifest["required_tests"]}
        self.assertIn("required_validation_gate_adopted", live_manifest["claim"])
        self.assertIn("axis-qualified", live_manifest["claim"])
        self.assertNotIn("current authority cutover and 2105 consumer migration sealed", live_manifest["claim"])
        self.assertIn(
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_closeout_reentry_guard_seal_report.json",
            required_paths,
        )
        self.assertIn(
            (
                "test_dvf_3_3_closeout_reentry_guard_seal."
                "DvfCloseoutReentryGuardSealTest.test_manifest_adoption_is_governance_only_and_runner_visible"
            ),
            required_tests,
        )

    def test_final_report_allows_canonical_seal_and_keeps_release_out_of_scope(self) -> None:
        common = load_common_module()
        final = load_json(ROOT / "phase7/final_closeout_reentry_guard_seal_report.json")
        no_mutation = load_json(ROOT / "phase7/final_no_mutation_report.json")
        commands = load_json(ROOT / "phase7/final_pinned_command_manifest.json")
        review_hash = load_json(ROOT / "phase7/independent_review_artifact_hash_report.json")
        live_manifest = load_json(REPO / "Iris/_docs/round3/current_route_required_validations.json")
        claim_boundary = (REPO / "docs/dvf_3_3_closeout_reentry_claim_boundary.md").read_text(encoding="utf-8")
        review_paths = {row["path"] for row in review_hash["artifacts"]}
        required_paths = {row["path"] for row in live_manifest["required_artifacts"]}

        self.assertEqual(final["status"], "PASS")
        self.assertEqual(final["machine_contract_status"], "PASS")
        self.assertEqual(final["closeout_state"], "canonical_complete")
        self.assertTrue(final["canonical_seal_allowed"])
        self.assertEqual(final["independent_review_status"], "PASS")
        self.assertEqual(final["protected_source_rendered_lua_runtime_package_changed_count"], 0)
        self.assertIn("no_release_readiness", final["non_claims"])
        self.assertIn("no_public_text_acceptance", final["non_claims"])
        self.assertEqual(no_mutation["changed_count"], 0)
        contract = load_contract_probe()
        self.assertEqual(
            commands["approved_successor_pinned_baseline"][
                "expected_test_count"
            ],
            contract["expected_current_route_test_count"],
        )
        self.assertIn("axis-qualified", claim_boundary)
        self.assertIn("canonical seal is allowed", claim_boundary)
        self.assertEqual(review_hash["status"], "PASS")
        self.assertEqual(review_hash["independent_review_status"], "PASS")
        self.assertTrue(review_hash["canonical_seal_allowed"])
        self.assertEqual(review_hash["primary_review_artifact_missing_count"], 0)
        self.assertEqual(
            review_hash["schema_version"],
            "dvf-3-3-closeout-reentry-independent-review-hash-report-v2",
        )
        self.assertTrue(
            all(
                row["identity_mode"] == "decoded_utf8_eol_lf"
                for row in review_hash["artifacts"]
            )
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lf = root / "lf.md"
            crlf = root / "crlf.md"
            lf.write_bytes(b"first\nsecond\n")
            crlf.write_bytes(b"first\r\nsecond\r\n")
            self.assertEqual(
                common.decoded_utf8_eol_identity(lf),
                common.decoded_utf8_eol_identity(crlf),
            )
        self.assertIn(
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/independent_review_artifact_hash_report.json",
            required_paths,
        )
        for path in {
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/final_closeout_reentry_guard_seal_report.json",
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/full_current_route_validation_result.json",
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase7/validation_report.all.json",
            "Iris/build/description/v2/staging/dvf_3_3_closeout_reentry_guard_seal/phase1/claim_surface_scan_manifest.json",
        }:
            self.assertIn(path, review_paths)

    def test_generate_final_report_reflects_claim_scan_failure(self) -> None:
        probe = run_probe(
            "--probe-forbidden-surface",
            FORBIDDEN_SURFACE_PROBE_REQUEST,
        )
        final = probe["fixture_final"]
        self.assertEqual(final["status"], "FAIL")
        self.assertEqual(final["machine_contract_status"], "FAIL")
        self.assertEqual(final["claim_surface_scan_state"], "FAIL")
        self.assertGreater(
            final["claim_surface_scan_blocked_claim_surface_count"],
            0,
        )
        self.assertFalse(probe["live_evidence_writes_performed"])
        self.assertTrue(probe["candidate_discarded"])
        self.assertEqual(
            probe["candidate_disposition"],
            "discarded_isolated_fixture",
        )

    def test_validator_requires_full_current_route_result_for_complete_contract(self) -> None:
        probe = run_probe("--probe-route-shapes")
        cases = probe["cases"]

        self.assertFalse(cases["missing"]["ok"])
        self.assertIn(
            "full_current_route_validation_missing",
            cases["missing"]["error_codes"],
        )
        self.assertIn(
            "full_current_route_validation_summary_stale",
            cases["missing"]["error_codes"],
        )

        self.assertFalse(cases["malformed"]["ok"])
        self.assertEqual(
            cases["malformed"]["final"]["machine_contract_status"],
            "FAIL",
        )
        self.assertFalse(
            cases["malformed"]["final"][
                "full_current_route_runner_result_valid"
            ]
        )
        self.assertIn(
            "full_current_route_runner_shape_invalid",
            cases["malformed"]["error_codes"],
        )

        self.assertFalse(cases["bad_required"]["ok"])
        self.assertEqual(
            cases["bad_required"]["final"]["machine_contract_status"],
            "FAIL",
        )
        self.assertFalse(
            cases["bad_required"]["final"][
                "full_current_route_runner_result_valid"
            ]
        )
        self.assertIn(
            "full_current_route_runner_shape_invalid",
            cases["bad_required"]["error_codes"],
        )

        self.assertTrue(
            cases["valid"]["ok"],
            cases["valid"]["error_codes"],
        )
        self.assertEqual(
            cases["valid"]["relocated_surface_families"],
            {
                "generated_evidence": "generated_evidence",
                "ledger_packet": "ledger_packets",
                "policy_doc": "docs",
            },
        )
        self.assertFalse(probe["live_evidence_writes_performed"])
        self.assertTrue(
            all(
                row["candidate_discarded"]
                for row in cases.values()
            )
        )


if __name__ == "__main__":
    unittest.main()
