from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import public_text_quality_acceptance as base
import public_text_quality_acceptance_official_0005 as official
import public_text_quality_acceptance_official_0005_closure as legacy
import public_text_quality_acceptance_official_0005_phase7_v2 as predecessor


CORRECTION_ID = "g1-successor-0010-terminal-validation-0002"
PHASE7 = official.ATTEMPT_ROOT / "phase7"
CORRECTION_ROOT = PHASE7 / "corrections" / CORRECTION_ID
VALIDATION_ROOT = CORRECTION_ROOT / "inputs"
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
    / "owner_closure_seal_g1_successor_0010_terminal_validation_0002.json"
)

DISPOSITION = official.ATTEMPT_ROOT / "phase5" / "evaluation_subject_disposition.json"
DISPOSITION_RAW_SHA256 = "ad49f4bb0924d5f4528b61a4aed0e5338c505ee1b6be8f520abde963aa11b772"
DISPOSITION_SHA256 = predecessor.DISPOSITION_SHA256
POLICY = official.ATTEMPT_ROOT / "phase2" / "public_text_quality_acceptance_policy.json"
POLICY_RAW_SHA256 = predecessor.POLICY_SHA256
POLICY_SEAL = official.ATTEMPT_ROOT / "phase2" / "policy_hash_seal.json"
POLICY_SEAL_RAW_SHA256 = "a925370419bd74905c3b8a39ad9402022f941805e03f27ccdcd5967cac6f09b1"
POLICY_SEAL_SHA256 = "8dc7cf0eb3dea109f0595592da80f9d435b953a89729224ecfa61f53b4bcbf6f"
EVALUATION_SUBJECT_KIND = "dvf_3_3_korean_naturalization_candidate"

TRANSACTION_NONCE = "c8d7e32b-d7a5-4c13-bf06-10c6e7854996"
PREDECESSOR_FREEZE = predecessor.FREEZE
PREDECESSOR_FREEZE_SHA256 = "dc47eeb30f609ce1c76a375fdfeb9279ba6d14471177e0732038e22ad5b7e117"
PREDECESSOR_REVIEW = (
    official.V2_ROOT
    / "reviewer_inputs"
    / base.ROUND_ID
    / official.ATTEMPT_ID
    / predecessor.CORRECTION_ID
    / "independent_review.json"
)
PREDECESSOR_REVIEW_SHA256 = "9e1c6dc623e99c16a93b0dbe4ff454ccf03e206483c581b5c08c2420aaa6185d"
PREDECESSOR_REVIEW_FAILURE = predecessor.CORRECTION_ROOT / "review_failure.json"
PREDECESSOR_REVIEW_FAILURE_SHA256 = (
    "6e1e3fdcc111166b32f72207d246eaa192df0ca4d63056008b85bf04fb45231a"
)

TERMINAL_SCHEMA_V1 = "public_text_quality_acceptance_terminal_hash_seal_v1"
TERMINAL_SCHEMA_V2 = "public_text_quality_acceptance_terminal_hash_seal_v2"
FINAL_REPORT_SCHEMA_V2 = "public_text_quality_policy_closure_report_v2"
DAG_SCHEMA_V1 = "public_text_quality_terminal_sealed_input_dag_v1"


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


def _at(value: dict[str, Any], dotted: str) -> Any:
    current: Any = value
    for segment in dotted.split("."):
        if not isinstance(current, dict) or segment not in current:
            _fail(f"required binding is missing: {dotted}")
        current = current[segment]
    return current


def _copy(value: Any) -> Any:
    return json.loads(json.dumps(value))


def _role_paths() -> dict[str, Path]:
    return {
        "evaluation_subject": official.CANDIDATE,
        "disposition": DISPOSITION,
        "policy": POLICY,
        "policy_seal": POLICY_SEAL,
        "naturalization_handoff": official.PHASE8_HANDOFF,
        "g1_gate_successor": predecessor.G1_GATE,
        "g1_closeout_successor": predecessor.G1_CLOSEOUT,
        "readoption_transaction_contract": predecessor.TRANSACTION_CONTRACT,
        "readoption_owner_input": predecessor.OWNER_INPUT,
        "live_adoption_receipt": predecessor.LIVE_RECEIPT,
        "post_adoption_current_route": predecessor.POST_ROUTE,
        "live_manifest": base.LIVE_REQUIRED_VALIDATIONS,
        "candidate_manifest": predecessor.CANDIDATE,
        "candidate_patch": predecessor.PATCH,
        "fresh_freeze": FREEZE,
        "fresh_artifact_manifest": ARTIFACT_MANIFEST,
        "independent_review": INDEPENDENT_REVIEW,
        "reviewer_eligibility": REVIEWER_ELIGIBILITY,
        "owner_closure_seal": OWNER_SEAL,
        "protected_mutation_report": VALIDATION_ROOT / "protected.json",
        "lua_mutation_report": VALIDATION_ROOT / "lua.json",
    }


def _edge_contract() -> list[dict[str, str]]:
    edges = [
        ("evaluation_subject", "disposition", "evaluated_as"),
        ("policy", "disposition", "governs"),
        ("policy_seal", "disposition", "ratifies"),
        ("naturalization_handoff", "disposition", "binds_subject"),
        ("g1_gate_successor", "fresh_freeze", "clean_checkout_gate"),
        ("g1_closeout_successor", "fresh_freeze", "clean_checkout_closeout"),
        ("evaluation_subject", "fresh_freeze", "frozen_subject"),
        ("disposition", "fresh_freeze", "frozen_disposition"),
        ("policy", "fresh_freeze", "frozen_policy"),
        ("policy_seal", "fresh_freeze", "frozen_policy_seal"),
        ("naturalization_handoff", "fresh_freeze", "frozen_handoff"),
        ("readoption_transaction_contract", "live_adoption_receipt", "authorizes_transaction"),
        ("readoption_owner_input", "live_adoption_receipt", "owner_authorizes"),
        ("candidate_manifest", "live_adoption_receipt", "adopted_candidate"),
        ("candidate_patch", "live_adoption_receipt", "applied_patch"),
        ("live_adoption_receipt", "post_adoption_current_route", "validated_by"),
        ("live_manifest", "post_adoption_current_route", "route_subject"),
        ("readoption_transaction_contract", "fresh_freeze", "frozen_transaction"),
        ("readoption_owner_input", "fresh_freeze", "frozen_owner_input"),
        ("live_adoption_receipt", "fresh_freeze", "frozen_adoption"),
        ("post_adoption_current_route", "fresh_freeze", "frozen_route"),
        ("live_manifest", "fresh_freeze", "frozen_live_manifest"),
        ("candidate_manifest", "fresh_freeze", "frozen_candidate_manifest"),
        ("candidate_patch", "fresh_freeze", "frozen_candidate_patch"),
        ("protected_mutation_report", "fresh_freeze", "frozen_protected_state"),
        ("lua_mutation_report", "fresh_freeze", "frozen_runtime_state"),
        ("fresh_freeze", "independent_review", "review_subject"),
        ("fresh_artifact_manifest", "independent_review", "review_inventory"),
        ("independent_review", "owner_closure_seal", "reviewed_for_owner"),
        ("reviewer_eligibility", "owner_closure_seal", "reviewer_qualified"),
        ("fresh_freeze", "owner_closure_seal", "owner_seals_freeze"),
        ("fresh_artifact_manifest", "owner_closure_seal", "owner_seals_inventory"),
        ("readoption_transaction_contract", "owner_closure_seal", "owner_seals_transaction"),
        ("live_manifest", "owner_closure_seal", "owner_seals_live_state"),
    ]
    return [
        {"from": source, "to": target, "relation": relation}
        for source, target, relation in sorted(edges)
    ]


def _schema_contract() -> dict[str, str]:
    return {
        "evaluation_subject": "opaque_naturalization_candidate_json",
        "disposition": "public_text_quality_evaluation_subject_disposition_v1",
        "policy": "public_text_quality_acceptance_policy_v1",
        "policy_seal": "public_text_quality_policy_hash_seal_v1",
        "naturalization_handoff": "naturalization_publish_handoff_required_schema_v1",
        "g1_gate_successor": "iris-clean-checkout-full-repository-gate-manifest-v10",
        "g1_closeout_successor": "iris_clean_checkout_full_repository_technical_debt_closeout_successor_v10",
        "readoption_transaction_contract": "public_text_quality_exact_gate_readoption_transaction_v1",
        "readoption_owner_input": "public_text_quality_gate_readoption_decision_v1",
        "live_adoption_receipt": "public_text_quality_live_required_gate_readoption_receipt_v1",
        "post_adoption_current_route": "round3-contract-test-run-v1",
        "live_manifest": "round3-current-route-required-validations-v1",
        "candidate_manifest": "round3-current-route-required-validations-v1",
        "candidate_patch": "public_text_quality_required_gate_patch_v1",
        "fresh_freeze": "public_text_quality_phase7_final_evidence_freeze_v2",
        "fresh_artifact_manifest": "public_text_quality_phase7_final_artifact_hash_manifest_v3",
        "independent_review": "public_text_quality_phase7_independent_review_v3",
        "reviewer_eligibility": "public_text_quality_phase7_reviewer_eligibility_v3",
        "owner_closure_seal": "public_text_quality_phase7_owner_closure_seal_v3",
        "protected_mutation_report": "public_text_quality_phase7_terminal_validation_protected_surface_v1",
        "lua_mutation_report": "public_text_quality_phase7_terminal_validation_lua_syntax_v1",
    }


def _static_expected_hashes() -> dict[str, str]:
    return {
        "evaluation_subject": official.CANDIDATE_SHA256,
        "disposition": DISPOSITION_RAW_SHA256,
        "policy": POLICY_RAW_SHA256,
        "policy_seal": POLICY_SEAL_RAW_SHA256,
        "naturalization_handoff": official.PHASE8_HANDOFF_SHA256,
        "g1_gate_successor": predecessor.G1_GATE_SHA256,
        "g1_closeout_successor": predecessor.G1_CLOSEOUT_SHA256,
        "readoption_transaction_contract": predecessor.TRANSACTION_CONTRACT_SHA256,
        "readoption_owner_input": predecessor.OWNER_INPUT_SHA256,
        "live_adoption_receipt": predecessor.LIVE_RECEIPT_SHA256,
        "post_adoption_current_route": predecessor.POST_ROUTE_SHA256,
        "live_manifest": predecessor.LIVE_SHA256,
        "candidate_manifest": predecessor.CANDIDATE_SHA256,
        "candidate_patch": predecessor.PATCH_SHA256,
    }


def _binding_contract(role_hashes: dict[str, str]) -> dict[str, Any]:
    return {
        "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "qualified_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_sha256": POLICY_RAW_SHA256,
        "policy_seal_sha256": POLICY_SEAL_SHA256,
        "naturalization_handoff_path": base.repo_relative(official.PHASE8_HANDOFF),
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
        "g1_validated_subject_commit": predecessor.G1_SUBJECT_COMMIT,
        "g1_validated_subject_tree": predecessor.G1_SUBJECT_TREE,
        "g1_gate_successor_sha256": predecessor.G1_GATE_SHA256,
        "g1_closeout_successor_sha256": predecessor.G1_CLOSEOUT_SHA256,
        "readoption_transaction_id": predecessor.TRANSACTION_ID,
        "readoption_transaction_nonce": TRANSACTION_NONCE,
        "readoption_transaction_identity": predecessor.TRANSACTION_IDENTITY,
        "readoption_transaction_contract_sha256": predecessor.TRANSACTION_CONTRACT_SHA256,
        "readoption_owner_input_sha256": predecessor.OWNER_INPUT_SHA256,
        "live_adoption_receipt_sha256": predecessor.LIVE_RECEIPT_SHA256,
        "post_adoption_current_route_sha256": predecessor.POST_ROUTE_SHA256,
        "post_adoption_selected_identity_count": 136,
        "post_adoption_test_count": 136,
        "live_manifest_sha256": predecessor.LIVE_SHA256,
        "candidate_manifest_sha256": predecessor.CANDIDATE_SHA256,
        "candidate_patch_sha256": predecessor.PATCH_SHA256,
        "fresh_freeze_sha256": role_hashes["fresh_freeze"],
        "fresh_artifact_manifest_sha256": role_hashes["fresh_artifact_manifest"],
        "independent_review_sha256": role_hashes["independent_review"],
        "reviewer_eligibility_sha256": role_hashes["reviewer_eligibility"],
        "owner_closure_seal_sha256": role_hashes["owner_closure_seal"],
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_during_phase7_count": 0,
    }


def _role_requirements(bindings: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        "disposition": {
            "attempt_id": official.ATTEMPT_ID,
            "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
            "evaluation_subject_hash": official.CANDIDATE_SHA256,
            "qualified_disposition": "accepted",
            "disposition_hash": DISPOSITION_SHA256,
            "policy_raw_sha256": POLICY_RAW_SHA256,
            "policy_seal_hash": POLICY_SEAL_SHA256,
            "naturalization_handoff_hash": official.PHASE8_HANDOFF_SHA256,
        },
        "policy_seal": {
            "policy_ratified": True,
            "policy_raw_sha256": POLICY_RAW_SHA256,
            "seal_hash": POLICY_SEAL_SHA256,
        },
        "naturalization_handoff": {
            "naturalization_attempt_id": official.NATURALIZATION_ATTEMPT_ID,
            "requested_evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
            "write_once": True,
            "post_handoff_mutation_effect": "stale",
        },
        "g1_gate_successor": {
            "status": "PASS",
            "validated_subject.commit": predecessor.G1_SUBJECT_COMMIT,
            "validated_subject.tree": predecessor.G1_SUBJECT_TREE,
        },
        "readoption_transaction_contract": {
            "attempt_id": official.ATTEMPT_ID,
            "transaction_id": predecessor.TRANSACTION_ID,
            "transaction_nonce": TRANSACTION_NONCE,
            "transaction_identity": predecessor.TRANSACTION_IDENTITY,
            "g1_validated_subject_commit": predecessor.G1_SUBJECT_COMMIT,
            "g1_validated_subject_tree": predecessor.G1_SUBJECT_TREE,
            "g1_gate_successor_sha256": predecessor.G1_GATE_SHA256,
            "g1_closeout_successor_sha256": predecessor.G1_CLOSEOUT_SHA256,
            "candidate_manifest_sha256": predecessor.CANDIDATE_SHA256,
            "candidate_patch_sha256": predecessor.PATCH_SHA256,
            "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
            "evaluation_subject_hash": official.CANDIDATE_SHA256,
            "evaluation_subject_disposition": "accepted",
            "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        },
        "readoption_owner_input": {
            "decision": "adopt",
            "attempt_id": official.ATTEMPT_ID,
            "transaction_id": predecessor.TRANSACTION_ID,
            "transaction_nonce": TRANSACTION_NONCE,
            "transaction_identity": predecessor.TRANSACTION_IDENTITY,
            "readoption_transaction_contract_sha256": predecessor.TRANSACTION_CONTRACT_SHA256,
            "candidate_manifest_sha256": predecessor.CANDIDATE_SHA256,
            "candidate_patch_sha256": predecessor.PATCH_SHA256,
            "live_gate_readoption_authorized": True,
            "phase7_authorized_after_post_adoption_pass": True,
            "automatic_rollback_authorized": False,
        },
        "live_adoption_receipt": {
            "transaction_id": predecessor.TRANSACTION_ID,
            "transaction_nonce": TRANSACTION_NONCE,
            "transaction_identity": predecessor.TRANSACTION_IDENTITY,
            "owner_decision_sha256": predecessor.OWNER_INPUT_SHA256,
            "readoption_transaction_contract_sha256": predecessor.TRANSACTION_CONTRACT_SHA256,
            "live_manifest_after_sha256": predecessor.LIVE_SHA256,
            "candidate_manifest_sha256": predecessor.CANDIDATE_SHA256,
            "candidate_patch_sha256": predecessor.PATCH_SHA256,
            "live_required_gate_readopted": True,
            "protected_surface_mutation_count": 0,
            "runtime_lua_package_mutation_count": 0,
        },
        "post_adoption_current_route": {
            "success": True,
            "test_count": 136,
            "selected_identity_count": 136,
            "closure_enforced": True,
            "required_validations.success": True,
        },
        "candidate_patch": {
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "base_manifest_sha256": legacy.LIVE_BASE_SHA256,
            "candidate_manifest_sha256": predecessor.CANDIDATE_SHA256,
            "modified_required_artifact_count": 0,
            "modified_required_test_count": 0,
            "removed_required_artifact_count": 0,
            "removed_required_test_count": 0,
            "existing_entry_reorder_count": 0,
            "live_manifest_mutated": False,
        },
        "fresh_freeze": {
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "g1_validated_subject_commit": predecessor.G1_SUBJECT_COMMIT,
            "g1_validated_subject_tree": predecessor.G1_SUBJECT_TREE,
            "g1_gate_manifest_sha256": predecessor.G1_GATE_SHA256,
            "g1_closeout_sha256": predecessor.G1_CLOSEOUT_SHA256,
            "readoption_transaction_identity": predecessor.TRANSACTION_IDENTITY,
            "live_manifest_sha256": predecessor.LIVE_SHA256,
            "candidate_manifest_sha256": predecessor.CANDIDATE_SHA256,
            "candidate_patch_sha256": predecessor.PATCH_SHA256,
            "terminal_validation_complete": True,
            "protected_surface_mutation_count": 0,
            "runtime_lua_package_mutation_count": 0,
        },
        "fresh_artifact_manifest": {
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "freeze_manifest_sha256": bindings["fresh_freeze_sha256"],
        },
        "independent_review": {
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "reviewer_kind": "codex_reviewer",
            "freeze_manifest_sha256": bindings["fresh_freeze_sha256"],
            "final_artifact_hash_manifest_sha256": bindings[
                "fresh_artifact_manifest_sha256"
            ],
            "critical_finding_count": 0,
            "important_finding_count": 0,
        },
        "reviewer_eligibility": {
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "reviewer_kind": "codex_reviewer",
            "independent_from_owner": True,
            "independent_from_implementation_author": True,
            "conflict_of_interest": False,
        },
        "owner_closure_seal": {
            "status": "PASS",
            "decision": "seal_policy_closure",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "transaction_id": predecessor.TRANSACTION_ID,
            "transaction_identity": predecessor.TRANSACTION_IDENTITY,
            "freeze_manifest_sha256": bindings["fresh_freeze_sha256"],
            "final_artifact_hash_manifest_sha256": bindings[
                "fresh_artifact_manifest_sha256"
            ],
            "independent_review_sha256": bindings["independent_review_sha256"],
            "reviewer_eligibility_sha256": bindings[
                "reviewer_eligibility_sha256"
            ],
            "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
            "evaluation_subject_hash": official.CANDIDATE_SHA256,
            "evaluation_subject_disposition": "accepted",
            "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
            "policy_sha256": POLICY_RAW_SHA256,
            "policy_seal_sha256": POLICY_SEAL_SHA256,
            "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
            "live_manifest_sha256": predecessor.LIVE_SHA256,
            "policy_closure_state": "complete",
        },
        "protected_mutation_report": {
            "status": "PASS",
            "protected_surface_mutation_count": 0,
            "runtime_mutation_count": 0,
            "lua_mutation_count": 0,
            "package_mutation_count": 0,
            "live_manifest_mutation_count": 0,
        },
        "lua_mutation_report": {
            "status": "PASS",
            "exit_code": 0,
            "file_count": 94,
            "passed_file_count": 94,
            "runtime_lua_package_mutation_count": 0,
        },
    }


PROOF_FIELDS = {
    "disposition": "disposition_hash",
    "policy_seal": "seal_hash",
    "readoption_transaction_contract": "transaction_identity",
    "readoption_owner_input": "owner_binding_proof",
    "fresh_freeze": "freeze_hash",
    "fresh_artifact_manifest": "manifest_hash",
    "independent_review": "reviewer_binding_proof",
    "reviewer_eligibility": "eligibility_binding_proof",
    "owner_closure_seal": "owner_binding_proof",
}


def _validate_graph(dag: Any, context: dict[str, Any]) -> None:
    dag = _object(dag, "sealed-input DAG")
    if dag.get("schema_version") != DAG_SCHEMA_V1:
        _fail("sealed-input DAG schema mismatch")
    core = {key: child for key, child in dag.items() if key != "dag_hash"}
    if dag.get("dag_hash") != base.canonical_hash(core):
        _fail("sealed-input DAG canonical hash mismatch")
    nodes = dag.get("nodes")
    edges = dag.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        _fail("sealed-input DAG nodes or edges are malformed")
    if dag.get("node_count") != len(nodes) or dag.get("edge_count") != len(edges):
        _fail("sealed-input DAG denominator mismatch")
    expected_roles = set(context["role_specs"])
    observed_roles: list[str] = []
    observed_paths: list[str] = []
    for node in nodes:
        node = _object(node, "sealed-input DAG node")
        if set(node) != {"role", "path", "sha256", "schema_version"}:
            _fail("sealed-input DAG node has missing or extra fields")
        role = node.get("role")
        if not isinstance(role, str) or role not in expected_roles:
            _fail("sealed-input DAG contains an unknown role")
        spec = context["role_specs"][role]
        if node != spec:
            _fail(f"sealed-input DAG role/path/hash substitution: {role}")
        observed_roles.append(role)
        observed_paths.append(node["path"])
    if len(observed_roles) != len(set(observed_roles)):
        _fail("sealed-input DAG contains duplicate roles")
    if len(observed_paths) != len(set(observed_paths)):
        _fail("sealed-input DAG contains duplicate paths")
    if set(observed_roles) != expected_roles:
        _fail("sealed-input DAG has missing or extra nodes")
    expected_edges = {
        (row["from"], row["to"], row["relation"]) for row in context["edges"]
    }
    observed_edges: list[tuple[str, str, str]] = []
    for edge in edges:
        edge = _object(edge, "sealed-input DAG edge")
        if set(edge) != {"from", "to", "relation"}:
            _fail("sealed-input DAG edge has missing or extra fields")
        row = (edge.get("from"), edge.get("to"), edge.get("relation"))
        if not all(isinstance(part, str) for part in row):
            _fail("sealed-input DAG edge is malformed")
        if row[0] not in expected_roles or row[1] not in expected_roles:
            _fail("sealed-input DAG contains a dangling edge")
        if row[0] == row[1]:
            _fail("sealed-input DAG contains a self-cycle")
        observed_edges.append(row)
    if len(observed_edges) != len(set(observed_edges)):
        _fail("sealed-input DAG contains duplicate edges")
    if set(observed_edges) != expected_edges:
        _fail("sealed-input DAG has missing, extra, or substituted edges")
    outgoing: dict[str, list[str]] = {role: [] for role in expected_roles}
    indegree = {role: 0 for role in expected_roles}
    for source, target, _ in observed_edges:
        outgoing[source].append(target)
        indegree[target] += 1
    ready = sorted(role for role, degree in indegree.items() if degree == 0)
    visited = 0
    while ready:
        role = ready.pop(0)
        visited += 1
        for target in outgoing[role]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
                ready.sort()
    if visited != len(expected_roles):
        _fail("sealed-input DAG contains a cycle")


def _validate_role_documents(
    dag: dict[str, Any],
    context: dict[str, Any],
    documents: dict[str, dict[str, Any] | None],
    actual_sha256_by_path: dict[str, str],
) -> None:
    nodes = {row["role"]: row for row in dag["nodes"]}
    if set(actual_sha256_by_path) != {
        spec["path"] for spec in context["role_specs"].values()
    }:
        _fail("sealed-input DAG actual-byte census has missing or extra paths")
    for role, spec in context["role_specs"].items():
        path = spec["path"]
        if actual_sha256_by_path.get(path) != spec["sha256"]:
            _fail(f"sealed-input DAG actual file hash mismatch: {role}")
        if nodes[role]["sha256"] != actual_sha256_by_path[path]:
            _fail(f"sealed-input DAG node/file hash mismatch: {role}")
        document = documents.get(role)
        if role == "evaluation_subject":
            if document is not None:
                _fail("opaque evaluation subject must not be schema-substituted")
            continue
        document = _object(document, f"role document {role}")
        if document.get("schema_version") != spec["schema_version"]:
            _fail(f"role schema mismatch: {role}")
        for dotted, expected in context["role_requirements"].get(role, {}).items():
            if _at(document, dotted) != expected:
                _fail(f"role binding mismatch: {role}:{dotted}")
        proof_field = PROOF_FIELDS.get(role)
        if proof_field and not _proof(document, proof_field):
            _fail(f"role canonical proof mismatch: {role}")


def _validate_historical_v1_terminal(
    terminal: dict[str, Any], *, current_role_required: bool
) -> dict[str, Any]:
    core = {key: child for key, child in terminal.items() if key != "terminal_hash"}
    if terminal.get("terminal_hash") != base.canonical_hash(core):
        _fail("historical v1 terminal canonical hash mismatch")
    _exact(
        terminal,
        {
            "schema_version": TERMINAL_SCHEMA_V1,
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "qualified_disposition": "accepted",
            "policy_closure_state": "complete",
        },
        "historical v1 terminal",
    )
    if current_role_required:
        _fail("historical v1 terminal cannot substitute for the current v2 role")
    return {"status": "PASS", "schema_dispatch": "historical_v1"}


def validate_terminal_bundle(
    *,
    terminal: Any,
    final_report: Any,
    context: dict[str, Any],
    documents: dict[str, dict[str, Any] | None],
    actual_sha256_by_path: dict[str, str],
    current_role_required: bool = True,
) -> dict[str, Any]:
    terminal = _object(terminal, "terminal artifact")
    schema = terminal.get("schema_version")
    if schema == TERMINAL_SCHEMA_V1:
        return _validate_historical_v1_terminal(
            terminal, current_role_required=current_role_required
        )
    if schema != TERMINAL_SCHEMA_V2:
        _fail("unknown terminal schema")
    if not current_role_required:
        _fail("current v2 terminal cannot substitute for a historical v1 role")
    final_report = _object(final_report, "final closeout report")
    terminal_core = {
        key: child for key, child in terminal.items() if key != "terminal_hash"
    }
    report_core = {
        key: child for key, child in final_report.items() if key != "closeout_hash"
    }
    if terminal.get("terminal_hash") != base.canonical_hash(terminal_core):
        _fail("terminal canonical hash mismatch")
    if final_report.get("closeout_hash") != base.canonical_hash(report_core):
        _fail("final closeout internal declared SHA mismatch")
    expected_terminal = {
        "schema_version": TERMINAL_SCHEMA_V2,
        "status": "PASS",
        "attempt_id": context["attempt_id"],
        "correction_id": context["correction_id"],
        "terminal_claim": "Public Text Quality Acceptance Policy Closure: complete",
        "terminal_state": "sealed",
        "policy_closure_state": "complete",
        "final_report_path": context["final_report_path"],
        "final_report_sha256": context["final_report_sha256"],
        "final_report_declared_closeout_hash": final_report.get("closeout_hash"),
        "bindings": context["bindings"],
        "terminal_hash_seal_valid": True,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_during_phase7_count": 0,
    }
    expected_terminal_keys = set(expected_terminal) | {
        "sealed_input_dag_hash",
        "sealed_input_dag",
        "terminal_hash",
    }
    if set(terminal) != expected_terminal_keys:
        _fail("current v2 terminal has missing or extra fields")
    _exact(terminal, expected_terminal, "current v2 terminal")
    expected_report = {
        "schema_version": FINAL_REPORT_SCHEMA_V2,
        "status": "PASS",
        "attempt_id": context["attempt_id"],
        "correction_id": context["correction_id"],
        "terminal_state": "ready_for_terminal_seal",
        "policy_closure_state": "complete",
        "bindings": context["bindings"],
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_during_phase7_count": 0,
    }
    expected_report_keys = set(expected_report) | {
        "sealed_input_dag_hash",
        "sealed_input_dag",
        "closeout_hash",
    }
    if set(final_report) != expected_report_keys:
        _fail("final closeout report has missing or extra fields")
    _exact(final_report, expected_report, "final closeout report")
    actual_report_sha = actual_sha256_by_path.get(context["final_report_path"])
    if actual_report_sha != context["final_report_sha256"]:
        _fail("final closeout actual-byte SHA mismatch")
    if actual_report_sha != base.sha256_bytes(base.pretty_json_bytes(final_report)):
        _fail("final closeout working bytes are not the sealed canonical bytes")
    if terminal.get("final_report_sha256") != actual_report_sha:
        _fail("terminal/final closeout raw SHA mismatch")
    terminal_dag = _object(terminal.get("sealed_input_dag"), "terminal DAG")
    report_dag = _object(final_report.get("sealed_input_dag"), "report DAG")
    if terminal_dag != report_dag:
        _fail("terminal/report sealed-input DAG mismatch")
    if terminal.get("sealed_input_dag_hash") != terminal_dag.get("dag_hash"):
        _fail("terminal sealed-input DAG hash mismatch")
    if final_report.get("sealed_input_dag_hash") != terminal_dag.get("dag_hash"):
        _fail("report sealed-input DAG hash mismatch")
    _validate_graph(terminal_dag, context)
    actual_terminal_sha = actual_sha256_by_path.get(context["terminal_path"])
    if actual_terminal_sha != base.sha256_bytes(base.pretty_json_bytes(terminal)):
        _fail("terminal working bytes are not the sealed canonical bytes")
    role_actual = {
        path: sha
        for path, sha in actual_sha256_by_path.items()
        if path not in {context["final_report_path"], context["terminal_path"]}
    }
    _validate_role_documents(terminal_dag, context, documents, role_actual)
    return {
        "status": "PASS",
        "schema_dispatch": "current_v2_terminal_validation_0002",
        "node_count": terminal_dag["node_count"],
        "edge_count": terminal_dag["edge_count"],
        "final_report_sha256": actual_report_sha,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
    }


def _build_dag(context: dict[str, Any]) -> dict[str, Any]:
    nodes = [
        context["role_specs"][role] for role in sorted(context["role_specs"])
    ]
    core = {
        "schema_version": DAG_SCHEMA_V1,
        "node_count": len(nodes),
        "nodes": nodes,
        "edge_count": len(context["edges"]),
        "edges": context["edges"],
    }
    return {**core, "dag_hash": base.canonical_hash(core)}


def _build_terminal_documents(
    context: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    dag = _build_dag(context)
    report_core = {
        "schema_version": FINAL_REPORT_SCHEMA_V2,
        "status": "PASS",
        "attempt_id": context["attempt_id"],
        "correction_id": context["correction_id"],
        "terminal_state": "ready_for_terminal_seal",
        "policy_closure_state": "complete",
        "bindings": _copy(context["bindings"]),
        "sealed_input_dag_hash": dag["dag_hash"],
        "sealed_input_dag": _copy(dag),
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_during_phase7_count": 0,
    }
    report = {**report_core, "closeout_hash": base.canonical_hash(report_core)}
    report_sha = base.sha256_bytes(base.pretty_json_bytes(report))
    context["final_report_sha256"] = report_sha
    terminal_core = {
        "schema_version": TERMINAL_SCHEMA_V2,
        "status": "PASS",
        "attempt_id": context["attempt_id"],
        "correction_id": context["correction_id"],
        "terminal_claim": "Public Text Quality Acceptance Policy Closure: complete",
        "terminal_state": "sealed",
        "policy_closure_state": "complete",
        "final_report_path": context["final_report_path"],
        "final_report_sha256": report_sha,
        "final_report_declared_closeout_hash": report["closeout_hash"],
        "bindings": _copy(context["bindings"]),
        "sealed_input_dag_hash": dag["dag_hash"],
        "sealed_input_dag": _copy(dag),
        "terminal_hash_seal_valid": True,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_during_phase7_count": 0,
    }
    terminal = {**terminal_core, "terminal_hash": base.canonical_hash(terminal_core)}
    return report, terminal


def _reseal_fixture(fixture: dict[str, Any]) -> None:
    context = fixture["context"]
    terminal = fixture["terminal"]
    report = fixture["final_report"]
    dag = terminal["sealed_input_dag"]
    dag_core = {key: child for key, child in dag.items() if key != "dag_hash"}
    dag["node_count"] = len(dag["nodes"])
    dag["edge_count"] = len(dag["edges"])
    dag_core = {key: child for key, child in dag.items() if key != "dag_hash"}
    dag["dag_hash"] = base.canonical_hash(dag_core)
    report["sealed_input_dag"] = _copy(dag)
    report["sealed_input_dag_hash"] = dag["dag_hash"]
    report_core = {key: child for key, child in report.items() if key != "closeout_hash"}
    report["closeout_hash"] = base.canonical_hash(report_core)
    report_sha = base.sha256_bytes(base.pretty_json_bytes(report))
    context["final_report_sha256"] = report_sha
    fixture["actual_sha256_by_path"][context["final_report_path"]] = report_sha
    terminal["sealed_input_dag_hash"] = dag["dag_hash"]
    terminal["final_report_sha256"] = report_sha
    terminal["final_report_declared_closeout_hash"] = report["closeout_hash"]
    terminal_core = {
        key: child for key, child in terminal.items() if key != "terminal_hash"
    }
    terminal["terminal_hash"] = base.canonical_hash(terminal_core)
    fixture["actual_sha256_by_path"][context["terminal_path"]] = (
        base.sha256_bytes(base.pretty_json_bytes(terminal))
    )


def _fixture_document(schema: str, role: str) -> dict[str, Any]:
    return {"schema_version": schema, "status": "PASS", "role": role}


def _focused_fixture() -> dict[str, Any]:
    schemas = _schema_contract()
    documents: dict[str, dict[str, Any] | None] = {}
    paths = {role: f"fixture/{role}.json" for role in schemas}
    role_requirements: dict[str, dict[str, Any]] = {}
    proof_fields: dict[str, str] = {}
    for role, schema in schemas.items():
        if role == "evaluation_subject":
            documents[role] = None
            continue
        document = _fixture_document(schema, role)
        documents[role] = document
        role_requirements[role] = {"status": "PASS", "role": role}
    for role, field in PROOF_FIELDS.items():
        if role == "evaluation_subject":
            continue
        proof_fields[role] = field
        document = _object(documents[role], role)
        document[field] = base.canonical_hash(document)
    role_hashes: dict[str, str] = {}
    for role, document in documents.items():
        if document is None:
            role_hashes[role] = base.sha256_bytes(b"fixture-evaluation-subject")
        else:
            role_hashes[role] = base.sha256_bytes(base.pretty_json_bytes(document))
    bindings = {
        "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": role_hashes["evaluation_subject"],
        "qualified_disposition": "accepted",
        "evaluation_subject_disposition_hash": "1" * 64,
        "policy_sha256": role_hashes["policy"],
        "policy_seal_sha256": "2" * 64,
        "naturalization_handoff_path": paths["naturalization_handoff"],
        "naturalization_handoff_sha256": role_hashes["naturalization_handoff"],
        "g1_validated_subject_commit": "3" * 40,
        "g1_validated_subject_tree": "4" * 40,
        "g1_gate_successor_sha256": role_hashes["g1_gate_successor"],
        "g1_closeout_successor_sha256": role_hashes["g1_closeout_successor"],
        "readoption_transaction_id": predecessor.TRANSACTION_ID,
        "readoption_transaction_nonce": TRANSACTION_NONCE,
        "readoption_transaction_identity": "5" * 64,
        "readoption_transaction_contract_sha256": role_hashes[
            "readoption_transaction_contract"
        ],
        "readoption_owner_input_sha256": role_hashes["readoption_owner_input"],
        "live_adoption_receipt_sha256": role_hashes["live_adoption_receipt"],
        "post_adoption_current_route_sha256": role_hashes[
            "post_adoption_current_route"
        ],
        "post_adoption_selected_identity_count": 136,
        "post_adoption_test_count": 136,
        "live_manifest_sha256": role_hashes["live_manifest"],
        "candidate_manifest_sha256": role_hashes["candidate_manifest"],
        "candidate_patch_sha256": role_hashes["candidate_patch"],
        "fresh_freeze_sha256": role_hashes["fresh_freeze"],
        "fresh_artifact_manifest_sha256": role_hashes["fresh_artifact_manifest"],
        "independent_review_sha256": role_hashes["independent_review"],
        "reviewer_eligibility_sha256": role_hashes["reviewer_eligibility"],
        "owner_closure_seal_sha256": role_hashes["owner_closure_seal"],
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_during_phase7_count": 0,
    }
    role_specs = {
        role: {
            "role": role,
            "path": paths[role],
            "sha256": role_hashes[role],
            "schema_version": schemas[role],
        }
        for role in schemas
    }
    context = {
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "final_report_path": "fixture/final_report.json",
        "terminal_path": "fixture/terminal.json",
        "final_report_sha256": "",
        "role_specs": role_specs,
        "edges": _edge_contract(),
        "bindings": bindings,
        "role_requirements": role_requirements,
        "proof_fields": proof_fields,
    }
    actual = {spec["path"]: spec["sha256"] for spec in role_specs.values()}
    report, terminal = _build_terminal_documents(context)
    actual[context["final_report_path"]] = context["final_report_sha256"]
    actual[context["terminal_path"]] = base.sha256_bytes(
        base.pretty_json_bytes(terminal)
    )
    return {
        "context": context,
        "documents": documents,
        "actual_sha256_by_path": actual,
        "final_report": report,
        "terminal": terminal,
    }


def _expect_fixture_failure(fixture: dict[str, Any], label: str) -> None:
    try:
        validate_terminal_bundle(**fixture)
    except base.FoundationContractError:
        return
    _fail(f"focused terminal negative case did not fail-close: {label}")


def _binding_mismatch(field: str) -> None:
    fixture = _focused_fixture()
    fixture["terminal"]["bindings"][field] = "0" * 64
    fixture["final_report"]["bindings"][field] = "0" * 64
    _reseal_fixture(fixture)
    _expect_fixture_failure(fixture, f"binding:{field}")


def run_focused_terminal_tests() -> dict[str, Any]:
    passed: list[str] = []
    fixture = _focused_fixture()
    validate_terminal_bundle(**fixture)
    passed.append("complete_binding_pass")

    drift = _focused_fixture()
    drift["actual_sha256_by_path"][drift["context"]["final_report_path"]] = "0" * 64
    _expect_fixture_failure(drift, "final_report_one_byte_drift")
    passed.append("final_report_one_byte_drift_rejected")

    graph_cases = {
        "dag_node_missing": lambda dag: dag["nodes"].pop(),
        "dag_node_extra": lambda dag: dag["nodes"].append(_copy(dag["nodes"][0])),
        "dag_node_substitution": lambda dag: dag["nodes"][0].update(
            {"path": "fixture/substituted.json"}
        ),
        "dag_edge_missing": lambda dag: dag["edges"].pop(),
        "dag_edge_extra": lambda dag: dag["edges"].append(
            {"from": "policy", "to": "owner_closure_seal", "relation": "extra"}
        ),
        "dag_edge_substitution": lambda dag: dag["edges"][0].update(
            {"relation": "substituted"}
        ),
        "dag_cycle": lambda dag: dag["edges"].append(
            {
                "from": "owner_closure_seal",
                "to": "evaluation_subject",
                "relation": "cycle",
            }
        ),
    }
    for label, mutate in graph_cases.items():
        candidate = _focused_fixture()
        mutate(candidate["terminal"]["sealed_input_dag"])
        _reseal_fixture(candidate)
        _expect_fixture_failure(candidate, label)
        passed.append(f"{label}_rejected")

    closeout = _focused_fixture()
    closeout["terminal"]["final_report_declared_closeout_hash"] = "0" * 64
    terminal_core = {
        key: child
        for key, child in closeout["terminal"].items()
        if key != "terminal_hash"
    }
    closeout["terminal"]["terminal_hash"] = base.canonical_hash(terminal_core)
    _expect_fixture_failure(closeout, "final_closeout_sha_mismatch")
    passed.append("final_closeout_sha_mismatch_rejected")

    for field in (
        "evaluation_subject_hash",
        "evaluation_subject_disposition_hash",
        "policy_sha256",
        "naturalization_handoff_sha256",
        "live_manifest_sha256",
    ):
        _binding_mismatch(field)
        passed.append(f"{field}_mismatch_rejected")

    for role in ("independent_review", "owner_closure_seal"):
        missing = _focused_fixture()
        del missing["documents"][role]
        _expect_fixture_failure(missing, f"missing:{role}")
        passed.append(f"{role}_missing_rejected")
        failed = _focused_fixture()
        document = _object(failed["documents"][role], role)
        document["status"] = "FAIL"
        proof_field = PROOF_FIELDS[role]
        document[proof_field] = base.canonical_hash(
            {key: child for key, child in document.items() if key != proof_field}
        )
        new_sha = base.sha256_bytes(base.pretty_json_bytes(document))
        path = failed["context"]["role_specs"][role]["path"]
        failed["context"]["role_specs"][role]["sha256"] = new_sha
        failed["actual_sha256_by_path"][path] = new_sha
        for node in failed["terminal"]["sealed_input_dag"]["nodes"]:
            if node["role"] == role:
                node["sha256"] = new_sha
        _reseal_fixture(failed)
        _expect_fixture_failure(failed, f"failed:{role}")
        passed.append(f"{role}_fail_status_rejected")

    substitution = _focused_fixture()
    for node in substitution["terminal"]["sealed_input_dag"]["nodes"]:
        if node["role"] == "fresh_freeze":
            node["path"] = "fixture/predecessor_v1_freeze.json"
    _reseal_fixture(substitution)
    _expect_fixture_failure(substitution, "predecessor_role_substitution")
    passed.append("predecessor_role_substitution_rejected")

    historical = {
        "schema_version": TERMINAL_SCHEMA_V1,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "qualified_disposition": "accepted",
        "policy_closure_state": "complete",
    }
    historical["terminal_hash"] = base.canonical_hash(historical)
    historical_fixture = _focused_fixture()
    historical_fixture["terminal"] = historical
    _expect_fixture_failure(historical_fixture, "historical_v1_current_substitution")
    historical_result = _validate_historical_v1_terminal(
        historical, current_role_required=False
    )
    passed.append("historical_v1_dispatched_but_current_substitution_rejected")

    unknown = _focused_fixture()
    unknown["terminal"]["schema_version"] = "unknown-terminal-schema"
    _expect_fixture_failure(unknown, "unknown_schema")
    passed.append("unknown_schema_rejected")
    partial = _focused_fixture()
    del partial["terminal"]["bindings"]
    _expect_fixture_failure(partial, "partial_binding")
    passed.append("partial_binding_rejected")
    return {
        "status": "PASS",
        "case_count": len(passed),
        "cases": passed,
        "historical_schema_dispatch": historical_result["schema_dispatch"],
        "current_schema_dispatch": "current_v2_terminal_validation_0002",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "authority_effect": "none",
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
    current = predecessor.validate_current_inputs()
    predecessor_freeze = _raw(
        PREDECESSOR_FREEZE,
        PREDECESSOR_FREEZE_SHA256,
        "predecessor terminal-consumer freeze",
    )
    predecessor_review = _raw(
        PREDECESSOR_REVIEW,
        PREDECESSOR_REVIEW_SHA256,
        "predecessor failed independent review",
    )
    predecessor_failure = _raw(
        PREDECESSOR_REVIEW_FAILURE,
        PREDECESSOR_REVIEW_FAILURE_SHA256,
        "predecessor review failure record",
    )
    disposition = _raw(DISPOSITION, DISPOSITION_RAW_SHA256, "accepted disposition")
    policy = _raw(POLICY, POLICY_RAW_SHA256, "ratified policy")
    policy_seal = _raw(POLICY_SEAL, POLICY_SEAL_RAW_SHA256, "policy seal")
    disposition_value = _object(base.load_json_strict(DISPOSITION), "disposition")
    policy_seal_value = _object(base.load_json_strict(POLICY_SEAL), "policy seal")
    if not _proof(disposition_value, "disposition_hash"):
        _fail("accepted disposition canonical hash mismatch")
    if not _proof(policy_seal_value, "seal_hash"):
        _fail("policy seal canonical hash mismatch")
    _exact(
        disposition_value,
        {
            "attempt_id": official.ATTEMPT_ID,
            "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
            "evaluation_subject_hash": official.CANDIDATE_SHA256,
            "qualified_disposition": "accepted",
            "disposition_hash": DISPOSITION_SHA256,
            "policy_raw_sha256": POLICY_RAW_SHA256,
            "policy_seal_hash": POLICY_SEAL_SHA256,
            "naturalization_handoff_hash": official.PHASE8_HANDOFF_SHA256,
            "technical_blocker_count": 0,
            "effective_blocking_finding_count": 0,
        },
        "accepted disposition",
    )
    _exact(
        policy_seal_value,
        {
            "policy_ratified": True,
            "policy_raw_sha256": POLICY_RAW_SHA256,
            "seal_hash": POLICY_SEAL_SHA256,
        },
        "policy seal",
    )
    return {
        "status": "PASS",
        "predecessor_current_inputs": current,
        "predecessor_freeze": predecessor_freeze,
        "predecessor_review": predecessor_review,
        "predecessor_review_failure": predecessor_failure,
        "disposition": disposition,
        "policy": policy,
        "policy_seal": policy_seal,
        "live_manifest_sha256": predecessor.LIVE_SHA256,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def _unique_paths(paths: list[Path]) -> list[Path]:
    unique: dict[str, Path] = {}
    for path in paths:
        unique[base.repo_relative(path)] = path
    return [unique[key] for key in sorted(unique)]


def _freeze_paths() -> tuple[list[Path], list[Path]]:
    artifacts, implementation = predecessor._freeze_paths()
    artifacts.extend(
        [
            PREDECESSOR_FREEZE,
            predecessor.ARTIFACT_MANIFEST,
            PREDECESSOR_REVIEW,
            PREDECESSOR_REVIEW_FAILURE,
            DISPOSITION,
            POLICY,
            POLICY_SEAL,
        ]
    )
    if VALIDATION_ROOT.is_dir():
        artifacts.extend(
            path for path in VALIDATION_ROOT.rglob("*") if path.is_file()
        )
    module = Path(__file__).resolve()
    implementation.extend(
        [
            module,
            module.with_name(
                "run_public_text_quality_acceptance_official_0005_phase7_terminal_validation.py"
            ),
            module.with_name(
                "validate_public_text_quality_acceptance_official_0005_phase7_terminal_validation.py"
            ),
            official.CURRENT_ROUTE_TEST,
        ]
    )
    return _unique_paths(artifacts), _unique_paths(implementation)


def validate_freeze_document(value: Any) -> dict[str, Any]:
    freeze = _object(value, "Phase 7 freeze")
    schema = freeze.get("schema_version")
    if schema == predecessor.SCHEMA_V1:
        result = predecessor.validate_freeze_document(freeze)
        return {**result, "schema_dispatch": "historical_v1"}
    if schema != predecessor.SCHEMA_V2:
        _fail("unknown Phase 7 freeze schema")
    if freeze.get("correction_id") != CORRECTION_ID:
        result = predecessor.validate_freeze_document(freeze)
        return {**result, "schema_dispatch": "predecessor_current_v2"}
    core = {key: child for key, child in freeze.items() if key != "freeze_hash"}
    if freeze.get("freeze_hash") != base.canonical_hash(core):
        _fail("terminal-validation freeze canonical hash mismatch")
    _exact(
        freeze,
        {
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "g1_validated_subject_commit": predecessor.G1_SUBJECT_COMMIT,
            "g1_validated_subject_tree": predecessor.G1_SUBJECT_TREE,
            "g1_gate_manifest_sha256": predecessor.G1_GATE_SHA256,
            "g1_closeout_sha256": predecessor.G1_CLOSEOUT_SHA256,
            "readoption_transaction_id": predecessor.TRANSACTION_ID,
            "readoption_transaction_identity": predecessor.TRANSACTION_IDENTITY,
            "live_readoption_receipt_sha256": predecessor.LIVE_RECEIPT_SHA256,
            "phase6_post_adoption_route_sha256": predecessor.POST_ROUTE_SHA256,
            "live_manifest_sha256": predecessor.LIVE_SHA256,
            "candidate_manifest_sha256": predecessor.CANDIDATE_SHA256,
            "candidate_patch_sha256": predecessor.PATCH_SHA256,
            "predecessor_freeze_sha256": PREDECESSOR_FREEZE_SHA256,
            "predecessor_failed_review_sha256": PREDECESSOR_REVIEW_SHA256,
            "predecessor_review_failure_sha256": PREDECESSOR_REVIEW_FAILURE_SHA256,
            "terminal_validation_complete": True,
            "terminal_dag_missing_extra_duplicate_dangling_cycle_fail_closed": True,
            "terminal_role_substitution_fail_closed": True,
            "protected_surface_mutation_count": 0,
            "runtime_lua_package_mutation_count": 0,
        },
        "terminal-validation freeze",
    )
    rows = freeze.get("claim_bearing_artifacts")
    implementation = freeze.get("implementation_paths")
    if (
        not isinstance(rows, list)
        or freeze.get("claim_bearing_artifact_count") != len(rows)
        or not isinstance(implementation, list)
        or freeze.get("implementation_path_count") != len(implementation)
    ):
        _fail("terminal-validation freeze artifact denominator is malformed")
    return {
        "status": "PASS",
        "schema_version": schema,
        "schema_dispatch": "current_v2_terminal_validation_0002",
        "artifact_count": len(rows),
        "implementation_count": len(implementation),
    }


def compute_freeze_bundle(
    *,
    freeze_commit: str | None = None,
    freeze_tree: str | None = None,
) -> dict[str, dict[str, Any]]:
    freeze_commit, freeze_tree = predecessor._validated_freeze_readpoint(
        freeze_commit, freeze_tree
    )
    current = validate_current_inputs()
    artifact_paths, implementation_paths = _freeze_paths()
    artifacts = predecessor._rows(artifact_paths)
    implementation = predecessor._rows(implementation_paths)
    freeze_core = {
        "schema_version": predecessor.SCHEMA_V2,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "freeze_commit": freeze_commit,
        "freeze_tree": freeze_tree,
        "g1_validated_subject_commit": predecessor.G1_SUBJECT_COMMIT,
        "g1_validated_subject_tree": predecessor.G1_SUBJECT_TREE,
        "g1_gate_manifest_sha256": predecessor.G1_GATE_SHA256,
        "g1_closeout_sha256": predecessor.G1_CLOSEOUT_SHA256,
        "g1_clean_checkout_canonical_sha256": predecessor.G1_CANONICAL_SHA256,
        "readoption_transaction_id": predecessor.TRANSACTION_ID,
        "readoption_transaction_nonce": TRANSACTION_NONCE,
        "readoption_transaction_identity": predecessor.TRANSACTION_IDENTITY,
        "readoption_transaction_contract_sha256": predecessor.TRANSACTION_CONTRACT_SHA256,
        "owner_input_sha256": predecessor.OWNER_INPUT_SHA256,
        "owner_binding_proof_valid": True,
        "live_readoption_receipt_sha256": predecessor.LIVE_RECEIPT_SHA256,
        "phase6_post_adoption_route_sha256": predecessor.POST_ROUTE_SHA256,
        "live_manifest_sha256": predecessor.LIVE_SHA256,
        "candidate_manifest_sha256": predecessor.CANDIDATE_SHA256,
        "candidate_patch_sha256": predecessor.PATCH_SHA256,
        "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_sha256": POLICY_RAW_SHA256,
        "policy_seal_sha256": POLICY_SEAL_SHA256,
        "naturalization_handoff_path": base.repo_relative(official.PHASE8_HANDOFF),
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
        "predecessor_freeze_sha256": current["predecessor_freeze"]["sha256"],
        "predecessor_failed_review_sha256": current["predecessor_review"]["sha256"],
        "predecessor_review_failure_sha256": current[
            "predecessor_review_failure"
        ]["sha256"],
        "claim_bearing_artifact_count": len(artifacts),
        "claim_bearing_artifacts": artifacts,
        "implementation_path_count": len(implementation),
        "implementation_paths": implementation,
        "historical_v1_schema_supported": True,
        "current_v2_schema_supported": True,
        "unknown_or_partial_schema_fail_closed": True,
        "terminal_validation_complete": True,
        "terminal_actual_bytes_revalidated": True,
        "terminal_dag_missing_extra_duplicate_dangling_cycle_fail_closed": True,
        "terminal_role_substitution_fail_closed": True,
        "live_required_gate_adopted": True,
        "post_adoption_current_route": "136/136 PASS",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
        "policy_closure_state": "pending_fresh_independent_review",
    }
    freeze = {**freeze_core, "freeze_hash": base.canonical_hash(freeze_core)}
    freeze_sha = base.sha256_bytes(base.pretty_json_bytes(freeze))
    manifest_core = {
        "schema_version": "public_text_quality_phase7_final_artifact_hash_manifest_v3",
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
        "schema_version": "public_text_quality_phase7_independent_review_request_v3",
        "status": "READY_FOR_CODEX_REVIEWER",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "review_subject_commit": freeze_commit,
        "review_subject_tree": freeze_tree,
        "freeze_manifest_sha256": freeze_sha,
        "final_artifact_hash_manifest_sha256": manifest_sha,
        "required_reviewer_kind": "codex_reviewer",
        "required_scopes": [
            "terminal_actual_byte_and_final_report_validation",
            "sealed_input_dag_completeness_and_acyclicity",
            "role_substitution_and_schema_fail_closed_behavior",
            "subject_disposition_policy_handoff_bindings",
            "g1_successor_0010_readoption_and_live_gate_bindings",
            "review_and_owner_seal_state_validation",
            "predecessor_failure_preservation",
            "claim_boundary_and_no_mutation",
        ],
        "required_critical_finding_count": 0,
        "required_important_finding_count": 0,
        "owner_or_implementation_author_ineligible": True,
    }
    census = {
        "schema_version": "public_text_quality_phase7_pre_review_vcs_census_v3",
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
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
        "live_manifest_sha256": predecessor.LIVE_SHA256,
    }
    return {
        "freeze": freeze,
        "artifact_manifest": manifest,
        "review_request": request,
        "vcs_census": census,
    }


def materialize_freeze() -> dict[str, Any]:
    if legacy._git("status", "--porcelain=v1").stdout.strip():
        _fail("fresh terminal-validation freeze requires a clean checkout")
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
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def validate_freeze_bundle(*, require_tracked: bool) -> dict[str, Any]:
    existing = _object(base.load_json_strict(FREEZE), "terminal-validation freeze")
    expected = compute_freeze_bundle(
        freeze_commit=existing.get("freeze_commit"),
        freeze_tree=existing.get("freeze_tree"),
    )
    records: dict[str, Any] = {}
    for path, key in (
        (FREEZE, "freeze"),
        (ARTIFACT_MANIFEST, "artifact_manifest"),
        (REVIEW_REQUEST, "review_request"),
        (VCS_CENSUS, "vcs_census"),
    ):
        if path.read_bytes() != base.pretty_json_bytes(expected[key]):
            _fail(f"terminal-validation freeze deterministic replay mismatch: {path.name}")
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
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def validate_review() -> dict[str, Any]:
    freeze = validate_freeze_bundle(require_tracked=True)
    review_ref = legacy._tracked_head_record(INDEPENDENT_REVIEW)
    eligibility_ref = legacy._tracked_head_record(REVIEWER_ELIGIBILITY)
    review = _object(base.load_json_strict(INDEPENDENT_REVIEW), "independent review")
    eligibility = _object(
        base.load_json_strict(REVIEWER_ELIGIBILITY), "reviewer eligibility"
    )
    if not _proof(review, "reviewer_binding_proof"):
        _fail("independent review binding proof mismatch")
    if not _proof(eligibility, "eligibility_binding_proof"):
        _fail("reviewer eligibility binding proof mismatch")
    required_review_keys = {
        "schema_version",
        "status",
        "verdict",
        "attempt_id",
        "correction_id",
        "reviewed_at_utc",
        "reviewer_kind",
        "reviewer_identity",
        "reviewed_commit",
        "reviewed_tree",
        "freeze_manifest_sha256",
        "final_artifact_hash_manifest_sha256",
        "review_request_sha256",
        "reviewed_scope_count",
        "critical_finding_count",
        "important_finding_count",
        "findings",
        "scope_results",
        "verified_hashes",
        "owner_seal_sufficiency",
        "reviewer_binding_proof",
    }
    if set(review) != required_review_keys:
        _fail("independent review has missing or extra fields")
    required_eligibility_keys = {
        "schema_version",
        "status",
        "attempt_id",
        "correction_id",
        "declared_at_utc",
        "reviewer_kind",
        "reviewer_identity",
        "reviewed_commit",
        "reviewed_tree",
        "independent_from_owner",
        "independent_from_implementation_author",
        "owner_input_cross_reclassification",
        "conflict_of_interest",
        "eligibility_binding_proof",
    }
    if set(eligibility) != required_eligibility_keys:
        _fail("reviewer eligibility has missing or extra fields")
    reviewed_commit = legacy._git(
        "log", "-1", "--format=%H", "--", base.repo_relative(FREEZE)
    ).stdout.strip()
    reviewed_tree = legacy._git(
        "rev-parse", f"{reviewed_commit}^{{tree}}"
    ).stdout.strip()
    _exact(
        review,
        {
            "schema_version": "public_text_quality_phase7_independent_review_v3",
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "reviewer_kind": "codex_reviewer",
            "reviewer_identity": "codex_reviewer",
            "reviewed_commit": reviewed_commit,
            "reviewed_tree": reviewed_tree,
            "freeze_manifest_sha256": base.sha256_file(FREEZE),
            "final_artifact_hash_manifest_sha256": base.sha256_file(
                ARTIFACT_MANIFEST
            ),
            "reviewed_scope_count": 8,
            "critical_finding_count": 0,
            "important_finding_count": 0,
            "findings": [],
            "review_request_sha256": base.sha256_file(REVIEW_REQUEST),
            "verdict": "PASS",
        },
        "independent review",
    )
    _exact(
        eligibility,
        {
            "schema_version": "public_text_quality_phase7_reviewer_eligibility_v3",
            "status": "PASS",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "reviewer_kind": "codex_reviewer",
            "reviewer_identity": "codex_reviewer",
            "reviewed_commit": reviewed_commit,
            "reviewed_tree": reviewed_tree,
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
        "schema_version": "public_text_quality_phase7_owner_closure_seal_v3",
        "status": "PASS",
        "decision": "seal_policy_closure",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "transaction_id": predecessor.TRANSACTION_ID,
        "transaction_nonce": TRANSACTION_NONCE,
        "transaction_identity": predecessor.TRANSACTION_IDENTITY,
        "readoption_transaction_contract_sha256": predecessor.TRANSACTION_CONTRACT_SHA256,
        "readoption_owner_input_sha256": predecessor.OWNER_INPUT_SHA256,
        "live_adoption_receipt_sha256": predecessor.LIVE_RECEIPT_SHA256,
        "post_adoption_current_route_sha256": predecessor.POST_ROUTE_SHA256,
        "freeze_manifest_sha256": base.sha256_file(FREEZE),
        "final_artifact_hash_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "independent_review_sha256": review["review"]["sha256"],
        "reviewer_eligibility_sha256": review["eligibility"]["sha256"],
        "evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": DISPOSITION_SHA256,
        "policy_sha256": POLICY_RAW_SHA256,
        "policy_seal_sha256": POLICY_SEAL_SHA256,
        "naturalization_handoff_path": base.repo_relative(official.PHASE8_HANDOFF),
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
        "g1_validated_subject_commit": predecessor.G1_SUBJECT_COMMIT,
        "g1_validated_subject_tree": predecessor.G1_SUBJECT_TREE,
        "g1_gate_successor_sha256": predecessor.G1_GATE_SHA256,
        "g1_closeout_successor_sha256": predecessor.G1_CLOSEOUT_SHA256,
        "live_manifest_sha256": predecessor.LIVE_SHA256,
        "candidate_manifest_sha256": predecessor.CANDIDATE_SHA256,
        "candidate_patch_sha256": predecessor.PATCH_SHA256,
        "post_adoption_selected_identity_count": 136,
        "post_adoption_test_count": 136,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_during_phase7_count": 0,
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
                "schema_version": "public_text_quality_phase7_owner_seal_gap_v2",
                "status": "WAITING_FOR_EXTERNAL_INPUT",
                "attempt_id": official.ATTEMPT_ID,
                "correction_id": CORRECTION_ID,
                "required_owner_input_path": base.repo_relative(OWNER_SEAL),
                "required_owner_input_exact_fields": fields,
                "current_readoption_authorization_sufficient": False,
                "reason": "current authorization does not bind the terminal-validation-0002 freeze and fresh independent review",
                "terminal_created": False,
                "g5_handoff_created": False,
            },
        )
        raise base.ExternalInputRequired(
            input_kind="phase7_owner_closure_seal",
            path=OWNER_SEAL,
            details={"required_owner_input_exact_fields": fields},
        )
    review = validate_review()
    seal_ref = legacy._tracked_head_record(OWNER_SEAL)
    seal = _object(base.load_json_strict(OWNER_SEAL), "owner closure seal")
    if not _proof(seal, "owner_binding_proof"):
        _fail("owner closure seal binding proof mismatch")
    expected = owner_seal_required_fields()
    if set(seal) != set(expected):
        _fail("owner closure seal has missing or extra fields")
    for field, value in expected.items():
        if field in {"sealed_at", "owner_binding_proof"}:
            continue
        if seal.get(field) != value:
            _fail(f"owner closure seal mismatch: {field}")
    if not isinstance(seal.get("sealed_at"), str):
        _fail("owner closure seal timestamp is missing")
    return {"status": "PASS", "owner_seal": seal_ref, "review": review}


def _production_context() -> tuple[
    dict[str, Any],
    dict[str, dict[str, Any] | None],
    dict[str, str],
]:
    validate_owner_seal()
    paths = _role_paths()
    schemas = _schema_contract()
    static_hashes = _static_expected_hashes()
    documents: dict[str, dict[str, Any] | None] = {}
    role_hashes: dict[str, str] = {}
    actual: dict[str, str] = {}
    for role, path in paths.items():
        if not path.is_file():
            _fail(f"terminal DAG role artifact is missing: {role}")
        sha = base.sha256_file(path)
        if role in static_hashes and sha != static_hashes[role]:
            _fail(f"terminal DAG static role SHA mismatch: {role}")
        role_hashes[role] = sha
        relative = base.repo_relative(path)
        actual[relative] = sha
        documents[role] = (
            None if role == "evaluation_subject" else _object(
                base.load_json_strict(path), f"terminal DAG role {role}"
            )
        )
    bindings = _binding_contract(role_hashes)
    role_specs = {
        role: {
            "role": role,
            "path": base.repo_relative(paths[role]),
            "sha256": role_hashes[role],
            "schema_version": schemas[role],
        }
        for role in sorted(paths)
    }
    context = {
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "final_report_path": base.repo_relative(FINAL_REPORT),
        "terminal_path": base.repo_relative(TERMINAL_SEAL),
        "final_report_sha256": "",
        "role_specs": role_specs,
        "edges": _edge_contract(),
        "bindings": bindings,
        "role_requirements": _role_requirements(bindings),
    }
    return context, documents, actual


def finalize_terminal() -> dict[str, Any]:
    context, documents, actual = _production_context()
    report, terminal = _build_terminal_documents(context)
    base.write_once_or_same(FINAL_REPORT, report)
    actual[context["final_report_path"]] = base.sha256_file(FINAL_REPORT)
    if actual[context["final_report_path"]] != context["final_report_sha256"]:
        _fail("materialized final report raw SHA mismatch")
    base.write_once_or_same(TERMINAL_SEAL, terminal)
    actual[context["terminal_path"]] = base.sha256_file(TERMINAL_SEAL)
    validation = validate_terminal_bundle(
        terminal=terminal,
        final_report=report,
        context=context,
        documents=documents,
        actual_sha256_by_path=actual,
    )
    return {
        "status": "PASS",
        "terminal_path": base.repo_relative(TERMINAL_SEAL),
        "terminal_sha256": base.sha256_file(TERMINAL_SEAL),
        "final_report_path": base.repo_relative(FINAL_REPORT),
        "final_report_sha256": base.sha256_file(FINAL_REPORT),
        "validation": validation,
        "policy_closure_state": "complete",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def validate_terminal() -> dict[str, Any]:
    context, documents, actual = _production_context()
    terminal_ref = legacy._tracked_head_record(TERMINAL_SEAL)
    report_ref = legacy._tracked_head_record(FINAL_REPORT)
    context["final_report_sha256"] = report_ref["sha256"]
    actual[context["final_report_path"]] = report_ref["sha256"]
    actual[context["terminal_path"]] = terminal_ref["sha256"]
    for role, spec in context["role_specs"].items():
        record = legacy._tracked_head_record(official.REPO_ROOT / spec["path"])
        if record["sha256"] != spec["sha256"]:
            _fail(f"terminal DAG tracked role identity mismatch: {role}")
    result = validate_terminal_bundle(
        terminal=base.load_json_strict(TERMINAL_SEAL),
        final_report=base.load_json_strict(FINAL_REPORT),
        context=context,
        documents=documents,
        actual_sha256_by_path=actual,
    )
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "terminal": terminal_ref,
        "final_report": report_ref,
        "validation": result,
        "policy_closure_state": "complete",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }
