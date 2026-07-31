from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import public_text_quality_acceptance as base
import public_text_quality_acceptance_official_0005 as official
import public_text_quality_acceptance_official_0005_closure as legacy


CORRECTION_ID = "g1-successor-0010-consumer-0001"
PHASE7 = official.ATTEMPT_ROOT / "phase7"
CORRECTION_ROOT = PHASE7 / "corrections" / CORRECTION_ID
FREEZE = CORRECTION_ROOT / "final_evidence_freeze_manifest.json"
ARTIFACT_MANIFEST = CORRECTION_ROOT / "final_artifact_hash_manifest.json"
REVIEW_REQUEST = CORRECTION_ROOT / "independent_review_request.json"
VCS_CENSUS = CORRECTION_ROOT / "vcs_authority_census_pre_review.json"
OWNER_GAP = CORRECTION_ROOT / "owner_closure_seal_gap.json"
FINAL_REPORT = CORRECTION_ROOT / "final_public_text_quality_policy_closure_report.json"
TERMINAL_SEAL = CORRECTION_ROOT / "terminal_hash_seal.json"

REVIEWER_ROOT = (
    official.V2_ROOT
    / "reviewer_inputs"
    / base.ROUND_ID
    / official.ATTEMPT_ID
    / CORRECTION_ID
)
INDEPENDENT_REVIEW = REVIEWER_ROOT / "independent_review.json"
REVIEWER_ELIGIBILITY = REVIEWER_ROOT / "reviewer_eligibility_declaration.json"
OWNER_SEAL = (
    official.OWNER_INPUT_ROOT
    / "owner_closure_seal_g1_successor_0010_consumer_0001.json"
)

G1_SUBJECT_COMMIT = "e5f1d7c0f4635340014667d882f82bcec40bc27c"
G1_SUBJECT_TREE = "0bf68cd938b865eb03f6976b6fe02e6840a3f7d6"
G1_GATE = (
    official.REPO_ROOT
    / "Iris/validation/clean_checkout/evidence/"
    "full_repository_gate_manifest_successor_0010.json"
)
G1_GATE_SHA256 = "2378a6abe78fa115d0de66763413f27d233dce325ff195e48b655f5ddfe252c1"
G1_CLOSEOUT = (
    official.REPO_ROOT
    / "Iris/validation/clean_checkout/authority/"
    "full_repository_technical_debt_closeout_successor_0010.json"
)
G1_CLOSEOUT_SHA256 = "d481f9b8a488838595f2db3990ba29116314c82c86ab1ee3762db08c181c57ab"
G1_CANONICAL_SHA256 = "2140c2be9ccaeb78860249eb756214aa74ef01227e33fadc0c671655a29fc516"

R10 = official.ATTEMPT_ROOT / "phase6" / "r10-0001"
TRANSACTION_ID = "g1-successor-0010-readoption-0001"
TRANSACTION_IDENTITY = "c055f10506f4d4c308bc4521f284eaf630a06ee48fd9d1f933597212824da2a1"
TRANSACTION_CONTRACT = R10 / "readoption_transaction_contract.json"
TRANSACTION_CONTRACT_SHA256 = "e4d7637609f94b4f2ef98c8c9ba53b466b6ce8c4a81fbdb16aff4747c8e4f1df"
OWNER_INPUT = (
    official.OWNER_INPUT_ROOT
    / "gate_readoption_decision_g1_successor_0010.json"
)
OWNER_INPUT_SHA256 = "2442cc1217049d8af392d9a4837e58986f31efbe5f8faa2ca088768c2c42b14e"
LIVE_RECEIPT = R10 / "live_readoption_receipt.json"
LIVE_RECEIPT_SHA256 = "e31f90fc4b66d23a763cdddc07ed908a647674513b9362fdb91d565f10ed51d6"
POST_ROUTE = R10 / "post_adoption.json"
POST_ROUTE_SHA256 = "d29f8b27d067188c71f3167aba6a280d4fb3633ebce65dbdefb5e7fc6fd6c1c9"
POST_EXECUTION_RECEIPT = R10 / "post_adoption_execution_receipt.json"
PHASE6_PASS = R10 / "phase6_readoption_pass_record.json"
LUA_RECEIPT = R10 / "lua_syntax_no_regression_receipt.json"

LIVE_SHA256 = "3107201fd7e6da0c8a97a3c8d9ee8119d2d4d9768d0da3fcbcb306cc2447c75b"
CANDIDATE = official.ATTEMPT_ROOT / "phase6" / "required_gate_candidate.json"
CANDIDATE_SHA256 = LIVE_SHA256
PATCH = official.ATTEMPT_ROOT / "phase6" / "required_gate_patch.json"
PATCH_SHA256 = "fc2068f1018e9f8ace56e31958702616710d38c38914cb2307c6e598e1db42ad"
DISPOSITION_SHA256 = "2a944a8f7e683726229aade6a9afc12e0475b8e46cf980c24dc03a36be560e64"
POLICY_SHA256 = "12bf2c9e025108f217bf5c7304a900694503cebe08fc96d60cdf4c96a48267f0"

PREDECESSOR_FREEZE = PHASE7 / "final_evidence_freeze_manifest.json"
PREDECESSOR_FREEZE_SHA256 = "92568d6609e55c6a371852063a807ebe8a17d33d83a5fc84a70ea5f59c863d25"
PREDECESSOR_REVIEW_FAILURE = PHASE7 / "independent_review_failure_record.json"
PREDECESSOR_REVIEW_FAILURE_SHA256 = "8e9c2b60afe7a74d2addb0840ae20644d10f6c7c11117468a579581271c024a6"

SCHEMA_V1 = "public_text_quality_phase7_final_evidence_freeze_v1"
SCHEMA_V2 = "public_text_quality_phase7_final_evidence_freeze_v2"


def _fail(message: str) -> None:
    raise base.FoundationContractError(message)


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{label} must be an object")
    return value


def _exact(value: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    for field, wanted in expected.items():
        if value.get(field) != wanted:
            _fail(f"{label} mismatch: {field}")


def _proof(value: dict[str, Any], field: str) -> bool:
    core = {key: child for key, child in value.items() if key != field}
    return value.get(field) == base.canonical_hash(core)


def validate_freeze_document(value: Any) -> dict[str, Any]:
    freeze = _object(value, "Phase 7 freeze")
    schema = freeze.get("schema_version")
    if schema not in {SCHEMA_V1, SCHEMA_V2}:
        _fail("unknown Phase 7 freeze schema")
    core = {key: child for key, child in freeze.items() if key != "freeze_hash"}
    if freeze.get("freeze_hash") != base.canonical_hash(core):
        _fail("Phase 7 freeze canonical hash mismatch")
    _exact(
        freeze,
        {"status": "PASS", "attempt_id": official.ATTEMPT_ID},
        "Phase 7 freeze",
    )
    rows = freeze.get("claim_bearing_artifacts")
    implementation = freeze.get("implementation_paths")
    if (
        not isinstance(rows, list)
        or freeze.get("claim_bearing_artifact_count") != len(rows)
        or not isinstance(implementation, list)
        or freeze.get("implementation_path_count") != len(implementation)
    ):
        _fail("Phase 7 freeze artifact denominator is malformed")
    if schema == SCHEMA_V1:
        _exact(
            freeze,
            {
                "g1_gate_manifest_sha256": legacy.G1_GATE_MANIFEST_SHA256,
                "g1_closeout_sha256": legacy.G1_CLOSEOUT_SHA256,
                "live_manifest_sha256": LIVE_SHA256,
                "evaluation_subject_disposition": "accepted",
            },
            "historical v1 freeze",
        )
        dispatch = "historical_v1"
    else:
        _exact(
            freeze,
            {
                "g1_validated_subject_commit": G1_SUBJECT_COMMIT,
                "g1_validated_subject_tree": G1_SUBJECT_TREE,
                "g1_gate_manifest_sha256": G1_GATE_SHA256,
                "g1_closeout_sha256": G1_CLOSEOUT_SHA256,
                "readoption_transaction_id": TRANSACTION_ID,
                "readoption_transaction_identity": TRANSACTION_IDENTITY,
                "readoption_transaction_contract_sha256": TRANSACTION_CONTRACT_SHA256,
                "owner_input_sha256": OWNER_INPUT_SHA256,
                "live_readoption_receipt_sha256": LIVE_RECEIPT_SHA256,
                "phase6_post_adoption_route_sha256": POST_ROUTE_SHA256,
                "live_manifest_sha256": LIVE_SHA256,
                "candidate_manifest_sha256": CANDIDATE_SHA256,
                "candidate_patch_sha256": PATCH_SHA256,
                "evaluation_subject_disposition": "accepted",
                "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
                "protected_surface_mutation_count": 0,
                "runtime_lua_package_mutation_count": 0,
            },
            "current v2 freeze",
        )
        dispatch = "current_v2_successor_0010"
    return {
        "status": "PASS",
        "schema_version": schema,
        "schema_dispatch": dispatch,
        "artifact_count": len(rows),
        "implementation_count": len(implementation),
    }


def _focused_fixture(schema: str) -> dict[str, Any]:
    common: dict[str, Any] = {
        "schema_version": schema,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "live_manifest_sha256": LIVE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "claim_bearing_artifact_count": 0,
        "claim_bearing_artifacts": [],
        "implementation_path_count": 0,
        "implementation_paths": [],
    }
    if schema == SCHEMA_V1:
        common.update(
            {
                "g1_gate_manifest_sha256": legacy.G1_GATE_MANIFEST_SHA256,
                "g1_closeout_sha256": legacy.G1_CLOSEOUT_SHA256,
            }
        )
    elif schema == SCHEMA_V2:
        common.update(
            {
                "g1_validated_subject_commit": G1_SUBJECT_COMMIT,
                "g1_validated_subject_tree": G1_SUBJECT_TREE,
                "g1_gate_manifest_sha256": G1_GATE_SHA256,
                "g1_closeout_sha256": G1_CLOSEOUT_SHA256,
                "readoption_transaction_id": TRANSACTION_ID,
                "readoption_transaction_identity": TRANSACTION_IDENTITY,
                "readoption_transaction_contract_sha256": TRANSACTION_CONTRACT_SHA256,
                "owner_input_sha256": OWNER_INPUT_SHA256,
                "live_readoption_receipt_sha256": LIVE_RECEIPT_SHA256,
                "phase6_post_adoption_route_sha256": POST_ROUTE_SHA256,
                "candidate_manifest_sha256": CANDIDATE_SHA256,
                "candidate_patch_sha256": PATCH_SHA256,
                "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
                "protected_surface_mutation_count": 0,
                "runtime_lua_package_mutation_count": 0,
            }
        )
    common["freeze_hash"] = base.canonical_hash(common)
    return common


def _focused_expect_rejection(payload: dict[str, Any], label: str) -> None:
    try:
        validate_freeze_document(payload)
    except base.FoundationContractError:
        return
    _fail(f"focused negative case did not fail-close: {label}")


def run_focused_schema_tests() -> dict[str, Any]:
    historical = _focused_fixture(SCHEMA_V1)
    current = _focused_fixture(SCHEMA_V2)
    historical_result = validate_freeze_document(historical)
    current_result = validate_freeze_document(current)

    unknown = json.loads(json.dumps(current))
    unknown["schema_version"] = "unknown-phase7-schema"
    unknown["freeze_hash"] = base.canonical_hash(
        {key: child for key, child in unknown.items() if key != "freeze_hash"}
    )
    malformed = json.loads(json.dumps(current))
    del malformed["claim_bearing_artifacts"]
    malformed["freeze_hash"] = base.canonical_hash(
        {key: child for key, child in malformed.items() if key != "freeze_hash"}
    )
    _focused_expect_rejection(unknown, "unknown_schema")
    _focused_expect_rejection(malformed, "malformed_schema")

    mismatch_fields = (
        "g1_validated_subject_commit",
        "readoption_transaction_identity",
        "live_readoption_receipt_sha256",
    )
    for field in mismatch_fields:
        mismatch = json.loads(json.dumps(current))
        mismatch[field] = "0" * 64
        mismatch["freeze_hash"] = base.canonical_hash(
            {key: child for key, child in mismatch.items() if key != "freeze_hash"}
        )
        _focused_expect_rejection(mismatch, f"mismatch:{field}")

    replay = json.loads(json.dumps(current))
    if base.pretty_json_bytes(current) != base.pretty_json_bytes(replay):
        _fail("focused deterministic replay bytes mismatch")
    if validate_freeze_document(current) != validate_freeze_document(replay):
        _fail("focused deterministic replay result mismatch")
    return {
        "status": "PASS",
        "case_count": 4,
        "cases": {
            "historical_v1_and_current_v2_acceptance": {
                "status": "PASS",
                "historical_dispatch": historical_result["schema_dispatch"],
                "current_dispatch": current_result["schema_dispatch"],
            },
            "unknown_and_malformed_schema_rejection": {"status": "PASS"},
            "successor_transaction_hash_mismatch_rejection": {
                "status": "PASS",
                "mismatch_field_count": len(mismatch_fields),
            },
            "deterministic_document_replay": {"status": "PASS"},
        },
    }


def _raw(path: Path, expected: str, label: str) -> dict[str, Any]:
    actual = base.sha256_file(path)
    if actual != expected:
        _fail(f"{label} raw SHA mismatch")
    record = legacy._tracked_head_record(path)
    if record["sha256"] != expected:
        _fail(f"{label} HEAD SHA mismatch")
    return record


def validate_current_inputs() -> dict[str, Any]:
    gate = _raw(G1_GATE, G1_GATE_SHA256, "G1 successor 0010 gate")
    closeout = _raw(G1_CLOSEOUT, G1_CLOSEOUT_SHA256, "G1 successor 0010 closeout")
    transaction = _raw(
        TRANSACTION_CONTRACT,
        TRANSACTION_CONTRACT_SHA256,
        "readoption transaction contract",
    )
    transaction_value = _object(
        base.load_json_strict(TRANSACTION_CONTRACT), "readoption transaction contract"
    )
    transaction_core = {
        key: child
        for key, child in transaction_value.items()
        if key != "transaction_identity"
    }
    _exact(
        transaction_value,
        {
            "transaction_id": TRANSACTION_ID,
            "transaction_identity": TRANSACTION_IDENTITY,
            "g1_validated_subject_commit": G1_SUBJECT_COMMIT,
            "g1_validated_subject_tree": G1_SUBJECT_TREE,
            "g1_gate_successor_sha256": G1_GATE_SHA256,
            "g1_closeout_successor_sha256": G1_CLOSEOUT_SHA256,
        },
        "readoption transaction contract",
    )
    if base.canonical_hash(transaction_core) != TRANSACTION_IDENTITY:
        _fail("readoption transaction identity mismatch")
    owner = _raw(OWNER_INPUT, OWNER_INPUT_SHA256, "readoption owner input")
    owner_value = _object(base.load_json_strict(OWNER_INPUT), "readoption owner input")
    if not _proof(owner_value, "owner_binding_proof"):
        _fail("readoption owner binding proof mismatch")
    _exact(
        owner_value,
        {
            "decision": "adopt",
            "transaction_id": TRANSACTION_ID,
            "transaction_identity": TRANSACTION_IDENTITY,
            "readoption_transaction_contract_sha256": TRANSACTION_CONTRACT_SHA256,
            "live_manifest_base_sha256": legacy.LIVE_BASE_SHA256,
            "candidate_manifest_sha256": CANDIDATE_SHA256,
            "candidate_patch_sha256": PATCH_SHA256,
            "live_gate_readoption_authorized": True,
            "phase7_authorized_after_post_adoption_pass": True,
            "automatic_rollback_authorized": False,
        },
        "readoption owner input",
    )
    receipt = _raw(LIVE_RECEIPT, LIVE_RECEIPT_SHA256, "live readoption receipt")
    receipt_value = _object(base.load_json_strict(LIVE_RECEIPT), "live readoption receipt")
    _exact(
        receipt_value,
        {
            "transaction_id": TRANSACTION_ID,
            "transaction_identity": TRANSACTION_IDENTITY,
            "live_manifest_before_sha256": legacy.LIVE_BASE_SHA256,
            "live_manifest_after_sha256": LIVE_SHA256,
            "required_artifact_addition_count": 10,
            "required_test_addition_count": 1,
            "removed_or_modified_existing_row_count": 0,
            "existing_entry_reorder_count": 0,
            "automatic_rollback_authorized": False,
        },
        "live readoption receipt",
    )
    post = _raw(POST_ROUTE, POST_ROUTE_SHA256, "post-adoption route")
    post_value = _object(base.load_json_strict(POST_ROUTE), "post-adoption route")
    _exact(
        post_value,
        {"success": True, "test_count": 136, "selected_identity_count": 136},
        "post-adoption route",
    )
    if post_value.get("failures") != [] or post_value.get("errors") != []:
        _fail("post-adoption route contains failures")
    live = _raw(base.LIVE_REQUIRED_VALIDATIONS, LIVE_SHA256, "live manifest")
    candidate = _raw(CANDIDATE, CANDIDATE_SHA256, "candidate manifest")
    patch = _raw(PATCH, PATCH_SHA256, "candidate patch")
    if base.LIVE_REQUIRED_VALIDATIONS.read_bytes() != CANDIDATE.read_bytes():
        _fail("live manifest does not equal candidate bytes")
    phase6 = _object(base.load_json_strict(PHASE6_PASS), "Phase 6 pass record")
    _exact(
        phase6,
        {
            "status": "PASS",
            "transaction_identity": TRANSACTION_IDENTITY,
            "post_adoption_result_sha256": POST_ROUTE_SHA256,
            "live_manifest_sha256": LIVE_SHA256,
            "phase6_blocker_count": 0,
            "protected_surface_mutation_count": 0,
            "runtime_lua_package_mutation_count": 0,
            "phase7_allowed": True,
        },
        "Phase 6 pass record",
    )
    lua = _object(base.load_json_strict(LUA_RECEIPT), "Lua receipt")
    _exact(
        lua,
        {"status": "PASS", "exit_code": 0, "validated_lua_file_count": 94},
        "Lua receipt",
    )
    predecessor_freeze = _raw(
        PREDECESSOR_FREEZE,
        PREDECESSOR_FREEZE_SHA256,
        "predecessor Phase 7 freeze",
    )
    predecessor_failure = _raw(
        PREDECESSOR_REVIEW_FAILURE,
        PREDECESSOR_REVIEW_FAILURE_SHA256,
        "predecessor Phase 7 review failure",
    )
    return {
        "status": "PASS",
        "g1_gate": gate,
        "g1_closeout": closeout,
        "transaction": transaction,
        "owner_input": owner,
        "live_receipt": receipt,
        "post_route": post,
        "live_manifest": live,
        "candidate": candidate,
        "patch": patch,
        "predecessor_freeze": predecessor_freeze,
        "predecessor_review_failure": predecessor_failure,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
    }


def _rows(paths: Iterable[Path]) -> list[dict[str, Any]]:
    unique = {str(path.resolve()).lower(): path.resolve() for path in paths}
    return [
        legacy._tracked_head_record(path)
        for path in sorted(unique.values(), key=base.repo_relative)
    ]


def _freeze_paths() -> tuple[list[Path], list[Path]]:
    paths: list[Path] = []
    for phase in range(6):
        paths.extend(
            path
            for path in (official.ATTEMPT_ROOT / f"phase{phase}").iterdir()
            if path.is_file()
        )
    paths.extend(path for path in (official.ATTEMPT_ROOT / "phase6").rglob("*") if path.is_file())
    paths.extend(
        path
        for path in PHASE7.iterdir()
        if path.is_file()
    )
    predecessor_reviewer = (
        official.V2_ROOT
        / "reviewer_inputs"
        / base.ROUND_ID
        / official.ATTEMPT_ID
    )
    paths.extend(path for path in predecessor_reviewer.iterdir() if path.is_file())
    paths.extend(
        [
            G1_GATE,
            G1_CLOSEOUT,
            official.POLICY_OWNER_INPUT,
            official.WAIVER_OWNER_INPUT,
            OWNER_INPUT,
            base.LIVE_REQUIRED_VALIDATIONS,
            official.FOUNDATION_CONTRACT,
            official.G4_READINESS,
            official.PHASE8_HANDOFF,
            official.PHASE8_CLOSEOUT,
            official.TERMINAL_CLOSEOUT,
            official.CANDIDATE,
            official.TRACE,
        ]
    )
    module = Path(__file__).resolve()
    implementation = [
        official.THIS_MODULE,
        official.RUNNER_MODULE,
        official.VALIDATOR_MODULE,
        Path(legacy.__file__).resolve(),
        module,
        module.with_name("run_public_text_quality_acceptance_official_0005_phase7_v2.py"),
        module.with_name("validate_public_text_quality_acceptance_official_0005_phase7_v2.py"),
        official.CURRENT_ROUTE_TEST,
        official.REPO_ROOT / "Iris/_docs/round3/round3_run_contract_tests.py",
        official.REPO_ROOT
        / "Iris/build/description/v2/tools/build/"
        "dvf_3_3_closeout_reentry_guard_seal_common.py",
    ]
    return paths, implementation


def _validated_freeze_readpoint(
    freeze_commit: str | None,
    freeze_tree: str | None,
) -> tuple[str, str]:
    if freeze_commit is None and freeze_tree is None:
        return base.git_head(), legacy._head_tree()
    if not isinstance(freeze_commit, str) or not isinstance(freeze_tree, str):
        _fail("fresh Phase 7 freeze readpoint is malformed")
    observed_tree = legacy._git(
        "rev-parse", f"{freeze_commit}^{{tree}}", check=False
    )
    if observed_tree.returncode != 0 or observed_tree.stdout.strip() != freeze_tree:
        _fail("fresh Phase 7 freeze commit/tree mismatch")
    ancestry = legacy._git(
        "merge-base", "--is-ancestor", freeze_commit, "HEAD", check=False
    )
    if ancestry.returncode != 0:
        _fail("fresh Phase 7 freeze readpoint is not an ancestor of HEAD")
    return freeze_commit, freeze_tree


def compute_freeze_bundle(
    *,
    freeze_commit: str | None = None,
    freeze_tree: str | None = None,
) -> dict[str, dict[str, Any]]:
    freeze_commit, freeze_tree = _validated_freeze_readpoint(
        freeze_commit, freeze_tree
    )
    current = validate_current_inputs()
    artifact_paths, implementation_paths = _freeze_paths()
    artifacts = _rows(artifact_paths)
    implementation = _rows(implementation_paths)
    freeze_core = {
        "schema_version": SCHEMA_V2,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "freeze_commit": freeze_commit,
        "freeze_tree": freeze_tree,
        "g1_validated_subject_commit": G1_SUBJECT_COMMIT,
        "g1_validated_subject_tree": G1_SUBJECT_TREE,
        "g1_gate_manifest_sha256": G1_GATE_SHA256,
        "g1_closeout_sha256": G1_CLOSEOUT_SHA256,
        "g1_clean_checkout_canonical_sha256": G1_CANONICAL_SHA256,
        "readoption_transaction_id": TRANSACTION_ID,
        "readoption_transaction_identity": TRANSACTION_IDENTITY,
        "readoption_transaction_contract_sha256": TRANSACTION_CONTRACT_SHA256,
        "owner_input_sha256": OWNER_INPUT_SHA256,
        "owner_binding_proof_valid": True,
        "live_readoption_receipt_sha256": LIVE_RECEIPT_SHA256,
        "phase6_readoption_pass_sha256": base.sha256_file(PHASE6_PASS),
        "phase6_post_adoption_route_sha256": POST_ROUTE_SHA256,
        "phase6_post_adoption_execution_receipt_sha256": base.sha256_file(
            POST_EXECUTION_RECEIPT
        ),
        "lua_syntax_no_regression_receipt_sha256": base.sha256_file(LUA_RECEIPT),
        "live_manifest_sha256": LIVE_SHA256,
        "candidate_manifest_sha256": CANDIDATE_SHA256,
        "candidate_patch_sha256": PATCH_SHA256,
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_sha256": POLICY_SHA256,
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
        "claim_bearing_artifact_count": len(artifacts),
        "claim_bearing_artifacts": artifacts,
        "implementation_path_count": len(implementation),
        "implementation_paths": implementation,
        "historical_v1_schema_supported": True,
        "current_v2_schema_supported": True,
        "unknown_schema_fail_closed": True,
        "predecessor_failure_preserved": True,
        "predecessor_freeze_sha256": current["predecessor_freeze"]["sha256"],
        "predecessor_review_failure_sha256": current[
            "predecessor_review_failure"
        ]["sha256"],
        "live_required_gate_adopted": True,
        "post_adoption_artifact_set_complete": True,
        "post_adoption_current_route": "136/136 PASS",
        "phase6_blocker_count": 0,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "policy_closure_state": "pending_fresh_independent_review",
    }
    freeze = {**freeze_core, "freeze_hash": base.canonical_hash(freeze_core)}
    freeze_sha = base.sha256_bytes(base.pretty_json_bytes(freeze))
    manifest_core = {
        "schema_version": "public_text_quality_phase7_final_artifact_hash_manifest_v2",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "self_hash_included": False,
        "terminal_seal_included": False,
        "ordered_artifact_count": len(artifacts),
        "ordered_artifacts": artifacts,
        "freeze_manifest_path": base.repo_relative(FREEZE),
        "freeze_manifest_sha256": freeze_sha,
    }
    manifest = {**manifest_core, "manifest_hash": base.canonical_hash(manifest_core)}
    manifest_sha = base.sha256_bytes(base.pretty_json_bytes(manifest))
    request = {
        "schema_version": "public_text_quality_phase7_independent_review_request_v2",
        "status": "READY_FOR_CODEX_REVIEWER",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "review_subject_commit": freeze_commit,
        "review_subject_tree": freeze_tree,
        "freeze_manifest_sha256": freeze_sha,
        "final_artifact_hash_manifest_sha256": manifest_sha,
        "required_reviewer_kind": "codex_reviewer",
        "required_scopes": [
            "schema_dispatch_and_fail_closed_behavior",
            "policy_and_denominator_unchanged",
            "exact_accepted_disposition",
            "g1_successor_0010_phase6_readoption",
            "additive_live_gate_effect",
            "predecessor_failure_preservation",
            "claim_boundary",
        ],
        "required_critical_finding_count": 0,
        "required_important_finding_count": 0,
        "owner_or_implementation_author_ineligible": True,
    }
    census = {
        "schema_version": "public_text_quality_phase7_pre_review_vcs_census_v2",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "claim_bearing_artifact_required_count": len(artifacts),
        "claim_bearing_artifact_tracked_count": len(artifacts),
        "claim_bearing_artifact_ignored_count": 0,
        "implementation_required_count": len(implementation),
        "implementation_tracked_count": len(implementation),
        "implementation_ignored_count": 0,
        "protected_surface_mutation_count": 0,
        "live_manifest_sha256": LIVE_SHA256,
    }
    return {
        "freeze": freeze,
        "artifact_manifest": manifest,
        "review_request": request,
        "vcs_census": census,
    }


def materialize_freeze() -> dict[str, Any]:
    if legacy._git("status", "--porcelain=v1").stdout.strip():
        _fail("fresh Phase 7 freeze requires a clean checkout")
    bundle = compute_freeze_bundle()
    for path, key in (
        (FREEZE, "freeze"),
        (ARTIFACT_MANIFEST, "artifact_manifest"),
        (REVIEW_REQUEST, "review_request"),
        (VCS_CENSUS, "vcs_census"),
    ):
        base.write_once_or_same(path, bundle[key])
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "freeze_path": base.repo_relative(FREEZE),
        "freeze_sha256": base.sha256_file(FREEZE),
        "artifact_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "review_request_sha256": base.sha256_file(REVIEW_REQUEST),
        "reviewer_input_required": True,
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def validate_freeze_bundle(*, require_tracked: bool) -> dict[str, Any]:
    existing_freeze = _object(base.load_json_strict(FREEZE), "fresh Phase 7 freeze")
    expected = compute_freeze_bundle(
        freeze_commit=existing_freeze.get("freeze_commit"),
        freeze_tree=existing_freeze.get("freeze_tree"),
    )
    records: dict[str, Any] = {}
    for path, key in (
        (FREEZE, "freeze"),
        (ARTIFACT_MANIFEST, "artifact_manifest"),
        (REVIEW_REQUEST, "review_request"),
        (VCS_CENSUS, "vcs_census"),
    ):
        if path.read_bytes() != base.pretty_json_bytes(expected[key]):
            _fail(f"fresh Phase 7 deterministic replay mismatch: {path.name}")
        records[key] = (
            legacy._tracked_head_record(path)
            if require_tracked
            else {"path": base.repo_relative(path), "sha256": base.sha256_file(path)}
        )
    dispatch = validate_freeze_document(base.load_json_strict(FREEZE))
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "schema_dispatch": dispatch,
        "deterministic_replay": True,
        "records": records,
        "protected_surface_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def validate_review() -> dict[str, Any]:
    freeze = validate_freeze_bundle(require_tracked=True)
    review_ref = legacy._tracked_head_record(INDEPENDENT_REVIEW)
    eligibility_ref = legacy._tracked_head_record(REVIEWER_ELIGIBILITY)
    review = _object(base.load_json_strict(INDEPENDENT_REVIEW), "review")
    eligibility = _object(base.load_json_strict(REVIEWER_ELIGIBILITY), "eligibility")
    if not _proof(review, "reviewer_binding_proof"):
        _fail("reviewer binding proof mismatch")
    if not _proof(eligibility, "eligibility_binding_proof"):
        _fail("reviewer eligibility proof mismatch")
    _exact(
        review,
        {
            "schema_version": "public_text_quality_phase7_independent_review_v2",
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "reviewer_kind": "codex_reviewer",
            "reviewer_identity": "codex_reviewer",
            "freeze_manifest_sha256": base.sha256_file(FREEZE),
            "final_artifact_hash_manifest_sha256": base.sha256_file(
                ARTIFACT_MANIFEST
            ),
            "reviewed_scope_count": 7,
            "critical_finding_count": 0,
            "important_finding_count": 0,
            "findings": [],
        },
        "review",
    )
    _exact(
        eligibility,
        {
            "schema_version": "public_text_quality_phase7_reviewer_eligibility_v2",
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "reviewer_kind": "codex_reviewer",
            "reviewer_identity": "codex_reviewer",
            "independent_from_owner": True,
            "independent_from_implementation_author": True,
            "owner_input_cross_reclassification": False,
            "conflict_of_interest": False,
        },
        "reviewer eligibility",
    )
    return {
        "status": "PASS",
        "freeze": freeze,
        "review": review_ref,
        "eligibility": eligibility_ref,
        "critical_finding_count": 0,
        "important_finding_count": 0,
    }


def owner_seal_required_fields() -> dict[str, Any]:
    review = validate_review()
    return {
        "schema_version": "public_text_quality_phase7_owner_closure_seal_v2",
        "status": "PASS",
        "decision": "seal_policy_closure",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "transaction_id": TRANSACTION_ID,
        "transaction_identity": TRANSACTION_IDENTITY,
        "freeze_manifest_sha256": base.sha256_file(FREEZE),
        "final_artifact_hash_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "independent_review_sha256": review["review"]["sha256"],
        "reviewer_eligibility_sha256": review["eligibility"]["sha256"],
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_sha256": POLICY_SHA256,
        "live_manifest_sha256": LIVE_SHA256,
        "live_required_gate_adopted": True,
        "post_adoption_artifact_set_complete": True,
        "policy_closure_state": "complete",
        "owner_identity": "repository_owner_via_direct_codex_instruction",
        "sealed_at": "ACTUAL_UTC_TIME_OF_OWNER_DECISION",
        "owner_binding_proof": "SHA256_CANONICAL_JSON_OF_ALL_OTHER_FIELDS",
    }


def validate_owner_seal() -> dict[str, Any]:
    if not OWNER_SEAL.is_file():
        fields = owner_seal_required_fields()
        base.write_once_or_same(
            OWNER_GAP,
            {
                "schema_version": "public_text_quality_phase7_owner_seal_gap_v1",
                "status": "WAITING_FOR_EXTERNAL_INPUT",
                "attempt_id": official.ATTEMPT_ID,
                "correction_id": CORRECTION_ID,
                "required_owner_input_path": base.repo_relative(OWNER_SEAL),
                "required_owner_input_exact_fields": fields,
                "current_readoption_authorization_sufficient": False,
                "reason": "current authorization does not bind the fresh freeze and independent review hashes",
                "terminal_created": False,
            },
        )
        raise base.ExternalInputRequired(
            input_kind="phase7_owner_closure_seal",
            path=OWNER_SEAL,
            details={"required_owner_input_exact_fields": fields},
        )
    review = validate_review()
    seal_ref = legacy._tracked_head_record(OWNER_SEAL)
    seal = _object(base.load_json_strict(OWNER_SEAL), "owner seal")
    if not _proof(seal, "owner_binding_proof"):
        _fail("owner seal binding proof mismatch")
    expected = owner_seal_required_fields()
    for field, value in expected.items():
        if field in {"sealed_at", "owner_binding_proof"}:
            continue
        if seal.get(field) != value:
            _fail(f"owner seal mismatch: {field}")
    if not isinstance(seal.get("sealed_at"), str):
        _fail("owner seal timestamp missing")
    return {"status": "PASS", "owner_seal": seal_ref, "review": review}


def finalize_terminal() -> dict[str, Any]:
    owner = validate_owner_seal()
    terminal_inputs = [
        legacy._tracked_head_record(path)
        for path in (
            FREEZE,
            ARTIFACT_MANIFEST,
            REVIEW_REQUEST,
            VCS_CENSUS,
            INDEPENDENT_REVIEW,
            REVIEWER_ELIGIBILITY,
            OWNER_SEAL,
            LIVE_RECEIPT,
            POST_ROUTE,
            PHASE6_PASS,
        )
    ]
    terminal_inputs.sort(key=lambda row: row["path"])
    report_core = {
        "schema_version": "public_text_quality_policy_closure_report_v2",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "qualified_disposition": "accepted",
        "transaction_identity": TRANSACTION_IDENTITY,
        "live_manifest_sha256": LIVE_SHA256,
        "independent_review_sha256": owner["review"]["review"]["sha256"],
        "owner_seal_sha256": owner["owner_seal"]["sha256"],
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "policy_closure_state": "complete",
    }
    report = {**report_core, "closeout_hash": base.canonical_hash(report_core)}
    base.write_once_or_same(FINAL_REPORT, report)
    terminal_core = {
        "schema_version": "public_text_quality_acceptance_terminal_hash_seal_v2",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "terminal_claim": "Public Text Quality Acceptance Policy Closure: complete",
        "sealed_input_count": len(terminal_inputs),
        "sealed_inputs": terminal_inputs,
        "final_closeout_sha256": base.sha256_file(FINAL_REPORT),
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "qualified_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_sha256": POLICY_SHA256,
        "live_manifest_sha256": LIVE_SHA256,
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
        "live_required_gate_adopted": True,
        "policy_closure_state": "complete",
        "terminal_hash_seal_valid": True,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
    }
    terminal = {**terminal_core, "terminal_hash": base.canonical_hash(terminal_core)}
    base.write_once_or_same(TERMINAL_SEAL, terminal)
    return {
        "status": "PASS",
        "terminal_path": base.repo_relative(TERMINAL_SEAL),
        "terminal_sha256": base.sha256_file(TERMINAL_SEAL),
        "policy_closure_state": "complete",
    }


def validate_terminal() -> dict[str, Any]:
    owner = validate_owner_seal()
    terminal_ref = legacy._tracked_head_record(TERMINAL_SEAL)
    report_ref = legacy._tracked_head_record(FINAL_REPORT)
    terminal = _object(base.load_json_strict(TERMINAL_SEAL), "terminal seal")
    core = {key: child for key, child in terminal.items() if key != "terminal_hash"}
    if terminal.get("terminal_hash") != base.canonical_hash(core):
        _fail("terminal canonical hash mismatch")
    _exact(
        terminal,
        {
            "status": "PASS",
            "correction_id": CORRECTION_ID,
            "live_manifest_sha256": LIVE_SHA256,
            "policy_closure_state": "complete",
            "protected_surface_mutation_count": 0,
            "runtime_lua_package_mutation_count": 0,
        },
        "terminal seal",
    )
    return {
        "status": "PASS",
        "terminal": terminal_ref,
        "final_report": report_ref,
        "owner": owner,
        "policy_closure_state": "complete",
    }
