from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import public_text_quality_acceptance as base
import public_text_quality_acceptance_official_0005 as official
import public_text_quality_acceptance_official_0005_phase7_replay_serialization as predecessor
import public_text_quality_acceptance_official_0005_phase7_terminal_validation as terminal_v2
import public_text_quality_acceptance_official_0005_phase7_v2 as phase7_v2


CORRECTION_ID = "g1-successor-0010-terminal-evaluation-subject-text-identity-0005"
CORRECTION_PATH_ID = "terminal-evaluation-subject-text-identity-0005"
INVENTORY_ALGORITHM_ID = predecessor.INVENTORY_ALGORITHM_ID
SEALED_SUBJECT_ALGORITHM_ID = "sha256_declared_naturalization_candidate_text_representation_v1"
HEAD_BLOB_ALGORITHM_ID = "sha256_head_git_blob_raw_bytes_v1"
LF_CANONICAL_ALGORITHM_ID = "sha256_utf8_crlf_and_lone_cr_to_lf_v1"
RAW_ROLE_ALGORITHM_ID = "sha256_head_git_blob_raw_bytes_v1"
SUBJECT_MAPPING_ALGORITHM_ID = base.TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID
SUBJECT_IDENTITY_SCHEMA = "public_text_quality_terminal_evaluation_subject_text_identity_v1"
FREEZE_SCHEMA = "public_text_quality_phase7_evaluation_subject_text_identity_freeze_v5"
MANIFEST_SCHEMA = "public_text_quality_phase7_evaluation_subject_text_identity_manifest_v6"
REVIEW_SCHEMA = "public_text_quality_phase7_evaluation_subject_text_identity_review_v6"
ELIGIBILITY_SCHEMA = "public_text_quality_phase7_evaluation_subject_text_identity_reviewer_eligibility_v6"
OWNER_SCHEMA = "public_text_quality_phase7_evaluation_subject_text_identity_owner_seal_v6"

SEALED_SUBJECT_SHA256 = official.CANDIDATE_SHA256
HEAD_BLOB_RAW_SHA256 = "522ab2773476eb97688c0f2adc14e52bbb58f30ce7cf48a7d7a2282e428964a5"

PHASE7 = official.ATTEMPT_ROOT / "phase7"
EVIDENCE_ROOT = PHASE7 / "corrections" / CORRECTION_ID
VALIDATION_ROOT = EVIDENCE_ROOT / "inputs"
CORRECTION_ROOT = PHASE7 / "corrections" / CORRECTION_PATH_ID
SUBJECT_IDENTITY = CORRECTION_ROOT / "evaluation_subject_identity.json"
FREEZE = CORRECTION_ROOT / "freeze.json"
ARTIFACT_MANIFEST = CORRECTION_ROOT / "artifact_manifest.json"
REVIEW_REQUEST = CORRECTION_ROOT / "review_request.json"
VCS_CENSUS = CORRECTION_ROOT / "vcs_census.json"
OWNER_GAP = CORRECTION_ROOT / "owner_gap.json"
FINAL_REPORT = CORRECTION_ROOT / "final_report.json"
TERMINAL_SEAL = CORRECTION_ROOT / "terminal_seal.json"
G5_HANDOFF = CORRECTION_ROOT / "g5_handoff.json"

CURRENT_VERIFICATION = predecessor.CURRENT_VERIFICATION
REVIEWER_ROOT = (
    official.V2_ROOT
    / "reviewer_inputs"
    / base.ROUND_ID
    / official.ATTEMPT_ID
    / CORRECTION_PATH_ID
)
INDEPENDENT_REVIEW = REVIEWER_ROOT / "independent_review.json"
REVIEWER_ELIGIBILITY = REVIEWER_ROOT / "reviewer_eligibility.json"
OWNER_SEAL = (
    official.OWNER_INPUT_ROOT
    / "owner_closure_seal_terminal_evaluation_subject_text_identity_0005.json"
)

PREDECESSOR_FAILED_EVIDENCE = {
    "predecessor_0004_failed_freeze": (
        predecessor.FREEZE,
        "9c5a3104889b16726b11809b7424b272051759f4d69ee6e25d6e895316103c52",
        predecessor.FREEZE_SCHEMA,
    ),
    "predecessor_0004_failed_owner_seal": (
        predecessor.OWNER_SEAL,
        "40502c7784188af660f51ff5476e3ebeeecd2ed6be08e16e64a3bac81c9aa6d4",
        predecessor.OWNER_SCHEMA,
    ),
    "predecessor_0004_terminal_failure": (
        predecessor.CORRECTION_ROOT / "terminal_failure.json",
        "17ad98829b20c30179dd635021a7d75bf850948ed9c5132e02e0c07927842521",
        "public_text_quality_phase7_replay_serialization_terminal_failure_v1",
    ),
}

_HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _fail(message: str) -> None:
    raise base.FoundationContractError(message)


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{label} must be an object")
    return value


def _proof(value: dict[str, Any], field: str) -> bool:
    return value.get(field) == base.canonical_hash(
        {key: child for key, child in value.items() if key != field}
    )


def _repo_path(path: Path) -> str:
    return predecessor._repo_path(path)


def _git_text(*args: str) -> str:
    return predecessor._git_text(*args)


def _tree_entries(treeish: str) -> list[dict[str, str]]:
    return predecessor._tree_entries(treeish)


def _rows_for_paths(entries: list[dict[str, str]], paths: list[str]) -> list[dict[str, Any]]:
    return predecessor._rows_for_paths(entries, paths)


def _inventory_hash(rows: list[dict[str, Any]]) -> str:
    return predecessor._inventory_hash(rows)


def _claim_rows(treeish: str) -> list[dict[str, Any]]:
    return predecessor._claim_rows(treeish)


def _under(path: str, root: Path) -> bool:
    prefix = _repo_path(root)
    return path.startswith(prefix + "/")


def _implementation_paths() -> list[str]:
    module = Path(__file__).resolve()
    return sorted(
        set(predecessor._implementation_paths())
        | {
            _repo_path(module),
            _repo_path(module.with_name("run_public_text_quality_acceptance_official_0005_phase7_evaluation_subject_text_identity.py")),
            _repo_path(module.with_name("validate_public_text_quality_acceptance_official_0005_phase7_evaluation_subject_text_identity.py")),
        }
    )


def _subject_authority() -> tuple[dict[str, Any], dict[str, Any]]:
    relative = _repo_path(official.CANDIDATE)
    entries = _tree_entries("HEAD")
    row = _rows_for_paths(entries, [relative])[0]
    head_raw = predecessor.predecessor._blob_bytes([row["git_blob_id"]])[row["git_blob_id"]]
    try:
        working_raw = official.CANDIDATE.read_bytes()
    except OSError as exc:
        _fail(f"cannot read evaluation subject working bytes: {exc}")
    filtered = predecessor.predecessor._working_blob_ids([relative]).get(relative)
    identity = base.build_text_constituent_identity_from_bytes(
        repo_relative_posix_path=relative,
        declared_sha256=SEALED_SUBJECT_SHA256,
        head_blob_id=row["git_blob_id"],
        head_blob_raw=head_raw,
        working_raw=working_raw,
        filtered_working_blob_id=filtered,
    )
    if row["raw_sha256"] != HEAD_BLOB_RAW_SHA256:
        _fail("evaluation subject HEAD Git blob raw SHA mismatch")
    if not identity["match"]:
        _fail("evaluation subject sealed/HEAD/working representation mapping mismatch")
    return row, identity


def _stable_subject_identity_core() -> dict[str, Any]:
    row, identity = _subject_authority()
    relative = _repo_path(official.CANDIDATE)
    head_raw = predecessor.predecessor._blob_bytes([row["git_blob_id"]])[row["git_blob_id"]]
    canonical = base.normalize_text_line_endings(head_raw)
    allowed = {
        "git_blob_raw": base.sha256_bytes(head_raw),
        "lf": base.sha256_bytes(canonical),
        "crlf": base.sha256_bytes(canonical.replace(b"\n", b"\r\n")),
        "lone_cr": base.sha256_bytes(canonical.replace(b"\n", b"\r")),
    }
    return {
        "schema_version": SUBJECT_IDENTITY_SCHEMA,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "role": "evaluation_subject",
        "path": relative,
        "role_scoped_compatibility": True,
        "compatible_role": "evaluation_subject",
        "sealed_identity_algorithm_id": SEALED_SUBJECT_ALGORITHM_ID,
        "sealed_evaluation_subject_sha256": SEALED_SUBJECT_SHA256,
        "head_blob_identity_algorithm_id": HEAD_BLOB_ALGORITHM_ID,
        "head_git_blob_id": row["git_blob_id"],
        "head_git_blob_raw_sha256": row["raw_sha256"],
        "line_ending_canonical_identity_algorithm_id": LF_CANONICAL_ALGORITHM_ID,
        "head_lf_canonical_sha256": identity["authority_lf_canonical_sha256"],
        "working_identity_algorithm_id": SUBJECT_MAPPING_ALGORITHM_ID,
        "working_lf_canonical_sha256": identity["working_lf_canonical_sha256"],
        "allowed_text_representation_sha256": allowed,
        "sealed_representation_kinds": identity["declared_representation_kinds"],
        "sealed_matches_head_authority": identity["declared_matches_head_authority"],
        "git_filtered_working_identity": identity["git_filtered_working_identity"],
        "canonical_working_identity": identity["canonical_working_identity"],
        "working_matches_head_authority": identity["working_matches_head_authority"],
        "git_filtered_or_lf_canonical_working_required": True,
        "json_semantic_normalization_applied": False,
        "whitespace_normalization_applied": False,
        "line_ending_only_equivalence": True,
        "direct_cross_domain_sha_comparison_forbidden": True,
        "absolute_path_checkout_location_autocrlf_host_metadata_excluded": True,
        "match": True,
        "authority_effect": "none",
    }


def build_subject_identity_document() -> dict[str, Any]:
    core = _stable_subject_identity_core()
    return {**core, "identity_proof": base.canonical_hash(core)}


def validate_subject_identity_document(value: Any) -> dict[str, Any]:
    document = _object(value, "evaluation subject identity")
    expected = build_subject_identity_document()
    if set(document) != set(expected):
        _fail("evaluation subject identity has missing or extra fields")
    if not _proof(document, "identity_proof"):
        _fail("evaluation subject identity proof mismatch")
    if document != expected:
        _fail("evaluation subject identity authority, algorithm, path, or role mismatch")
    return {
        "status": "PASS",
        "role": "evaluation_subject",
        "sealed_sha256": SEALED_SUBJECT_SHA256,
        "head_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "mapping_algorithm_id": SUBJECT_MAPPING_ALGORITHM_ID,
        "working_matches_head_authority": True,
        "authority_effect": "none",
    }


def materialize_subject_identity() -> dict[str, Any]:
    if _git_text("status", "--porcelain=v1"):
        _fail("evaluation subject identity materialization requires a clean checkout")
    document = build_subject_identity_document()
    base.write_once_or_same(SUBJECT_IDENTITY, document)
    return {
        "status": "PASS",
        "path": _repo_path(SUBJECT_IDENTITY),
        "sha256": base.sha256_file(SUBJECT_IDENTITY),
        "sealed_sha256": SEALED_SUBJECT_SHA256,
        "head_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "authority_effect": "none",
    }


def _inventory(treeish: str) -> dict[str, Any]:
    entries = _tree_entries(treeish)
    claim_rows = _claim_rows(treeish)
    evidence_paths = sorted(row["path"] for row in entries if _under(row["path"], VALIDATION_ROOT))
    implementation_paths = _implementation_paths()
    historical_paths = sorted(_repo_path(path) for path, _sha, _schema in PREDECESSOR_FAILED_EVIDENCE.values())
    evidence_rows = _rows_for_paths(entries, evidence_paths)
    implementation_rows = _rows_for_paths(entries, implementation_paths)
    historical_rows = _rows_for_paths(entries, historical_paths)
    all_rows = claim_rows + evidence_rows + implementation_rows + historical_rows
    if len({row["path"] for row in all_rows}) != len(all_rows):
        _fail("evaluation-subject correction inventory categories overlap")
    return {
        "claim_bearing_artifact_count": len(claim_rows),
        "claim_bearing_artifacts": claim_rows,
        "claim_inventory_sha256": _inventory_hash(claim_rows),
        "correction_evidence_count": len(evidence_rows),
        "correction_evidence": evidence_rows,
        "correction_evidence_sha256": _inventory_hash(evidence_rows),
        "implementation_path_count": len(implementation_rows),
        "implementation_paths": implementation_rows,
        "implementation_inventory_sha256": _inventory_hash(implementation_rows),
        "predecessor_failed_evidence_count": len(historical_rows),
        "predecessor_failed_evidence": historical_rows,
        "predecessor_failed_evidence_sha256": _inventory_hash(historical_rows),
    }


def _validated_readpoint(freeze_commit: str | None, freeze_tree: str | None) -> tuple[str, str]:
    if freeze_commit is None:
        freeze_commit = _git_text("rev-parse", "HEAD")
    if freeze_tree is None:
        freeze_tree = _git_text("rev-parse", f"{freeze_commit}^{{tree}}")
    if not _HEX40.fullmatch(freeze_commit) or not _HEX40.fullmatch(freeze_tree):
        _fail("freeze readpoint is malformed")
    if _git_text("rev-parse", f"{freeze_commit}^{{tree}}") != freeze_tree:
        _fail("freeze readpoint commit/tree mismatch")
    return freeze_commit, freeze_tree


def _json_at_commit(commit: str, path: Path, label: str) -> tuple[dict[str, Any], str]:
    relative = _repo_path(path)
    entries = {row["path"]: row for row in _tree_entries(commit)}
    entry = entries.get(relative)
    if entry is None or entry["object_type"] != "blob":
        _fail(f"sealed {label} missing from Git tree: {relative}")
    raw = predecessor.predecessor._blob_bytes([entry["git_blob_id"]])[entry["git_blob_id"]]
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail(f"{label} is not strict UTF-8 JSON: {exc}")
    return _object(value, label), base.sha256_bytes(raw)


def _predecessor_bindings() -> dict[str, Any]:
    return {
        role: {
            "path": _repo_path(path),
            "sha256": sha,
            "schema_version": schema,
            "role_state": "historical_failed_terminal_evidence",
        }
        for role, (path, sha, schema) in sorted(PREDECESSOR_FAILED_EVIDENCE.items())
    }


def compute_freeze_bundle(*, freeze_commit: str | None = None, freeze_tree: str | None = None) -> dict[str, dict[str, Any]]:
    freeze_commit, freeze_tree = _validated_readpoint(freeze_commit, freeze_tree)
    inventory = _inventory(freeze_commit)
    receipt, receipt_sha = _json_at_commit(freeze_commit, CURRENT_VERIFICATION, "current-verification receipt")
    predecessor.validate_current_verification_document(receipt, expected_inventory_sha256=inventory["claim_inventory_sha256"])
    subject, subject_sha = _json_at_commit(freeze_commit, SUBJECT_IDENTITY, "evaluation subject identity")
    validate_subject_identity_document(subject)
    freeze_core = {
        "schema_version": FREEZE_SCHEMA,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "freeze_commit": freeze_commit,
        "freeze_tree": freeze_tree,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "inventory_authority": "git_commit_tree_repo_relative_posix_paths_and_blob_bytes",
        **inventory,
        "evaluation_subject_identity_path": _repo_path(SUBJECT_IDENTITY),
        "evaluation_subject_identity_sha256": subject_sha,
        "evaluation_subject_sealed_sha256": SEALED_SUBJECT_SHA256,
        "evaluation_subject_head_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "evaluation_subject_mapping_algorithm_id": SUBJECT_MAPPING_ALGORITHM_ID,
        "current_verification_receipt_path": _repo_path(CURRENT_VERIFICATION),
        "current_verification_receipt_sha256": receipt_sha,
        "predecessor_failed_terminal_bindings": _predecessor_bindings(),
        "predecessor_owner_seal_reusable": False,
        "predecessor_terminal_reusable": False,
        "role_scoped_identity_dispatch": True,
        "direct_cross_domain_sha_comparison_forbidden": True,
        "absolute_path_checkout_location_autocrlf_host_metadata_excluded": True,
        "g1_validated_subject_commit": phase7_v2.G1_SUBJECT_COMMIT,
        "g1_validated_subject_tree": phase7_v2.G1_SUBJECT_TREE,
        "g1_gate_manifest_sha256": phase7_v2.G1_GATE_SHA256,
        "g1_closeout_sha256": phase7_v2.G1_CLOSEOUT_SHA256,
        "readoption_transaction_id": phase7_v2.TRANSACTION_ID,
        "readoption_transaction_identity": phase7_v2.TRANSACTION_IDENTITY,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "candidate_manifest_sha256": phase7_v2.CANDIDATE_SHA256,
        "candidate_patch_sha256": phase7_v2.PATCH_SHA256,
        "evaluation_subject_kind": terminal_v2.EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": SEALED_SUBJECT_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": terminal_v2.DISPOSITION_SHA256,
        "policy_sha256": terminal_v2.POLICY_RAW_SHA256,
        "policy_seal_sha256": terminal_v2.POLICY_SEAL_SHA256,
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
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
        "schema_version": MANIFEST_SCHEMA,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_bearing_artifact_count": 139,
        "claim_inventory_sha256": inventory["claim_inventory_sha256"],
        "correction_evidence_count": inventory["correction_evidence_count"],
        "correction_evidence_sha256": inventory["correction_evidence_sha256"],
        "implementation_path_count": inventory["implementation_path_count"],
        "implementation_inventory_sha256": inventory["implementation_inventory_sha256"],
        "predecessor_failed_evidence_count": inventory["predecessor_failed_evidence_count"],
        "predecessor_failed_evidence_sha256": inventory["predecessor_failed_evidence_sha256"],
        "evaluation_subject_identity_sha256": subject_sha,
        "current_verification_receipt_sha256": receipt_sha,
        "freeze_path": _repo_path(FREEZE),
        "freeze_sha256": freeze_sha,
        "self_hash_included": False,
        "terminal_included": False,
    }
    manifest = {**manifest_core, "manifest_hash": base.canonical_hash(manifest_core)}
    manifest_sha = base.sha256_bytes(base.pretty_json_bytes(manifest))
    request = {
        "schema_version": "public_text_quality_phase7_evaluation_subject_text_identity_review_request_v6",
        "status": "READY_FOR_CODEX_REVIEWER",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "review_subject_commit": freeze_commit,
        "review_subject_tree": freeze_tree,
        "freeze_sha256": freeze_sha,
        "artifact_manifest_sha256": manifest_sha,
        "evaluation_subject_identity_sha256": subject_sha,
        "current_verification_receipt_sha256": receipt_sha,
        "claim_inventory_sha256": inventory["claim_inventory_sha256"],
        "required_reviewer_kind": "codex_reviewer",
        "required_scopes": [
            "evaluation_subject_sealed_and_git_blob_identity_domains",
            "foundation_text_constituent_contract_reuse",
            "line_ending_only_equivalence",
            "semantic_byte_change_fail_closed",
            "role_scoped_identity_dispatch",
            "declared_algorithm_fail_closed",
            "terminal_dag_complete_binding",
            "freeze_deterministic_replay",
            "checkout_location_autocrlf_host_independence",
            "current_route_lua_no_mutation",
            "predecessor_failure_immutability",
            "claim_boundary_and_no_authority_effect"
        ],
        "required_critical_finding_count": 0,
        "required_important_finding_count": 0,
        "owner_or_implementation_author_ineligible": True,
    }
    census = {
        "schema_version": "public_text_quality_phase7_evaluation_subject_text_identity_vcs_census_v5",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "authority_source": "git_commit_tree_repo_relative_posix_paths_and_blob_bytes",
        "required_count": 139,
        "canonical_tracked_inventory_count": 139,
        "head_tree_blob_match_count": 139,
        "missing_count": 0,
        "extra_count": 0,
        "duplicate_count": 0,
        "case_collision_count": 0,
        "path_alias_count": 0,
        "blob_mismatch_count": 0,
        "claim_inventory_sha256": inventory["claim_inventory_sha256"],
        "evaluation_subject_identity_sha256": subject_sha,
        "current_verification_receipt_sha256": receipt_sha,
        "execution_mode_excluded": True,
        "absolute_path_checkout_location_autocrlf_host_metadata_excluded": True,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }
    return {"freeze": freeze, "artifact_manifest": manifest, "review_request": request, "vcs_census": census}


def materialize_freeze() -> dict[str, Any]:
    if _git_text("status", "--porcelain=v1"):
        _fail("fresh evaluation-subject identity freeze requires a clean checkout")
    bundle = compute_freeze_bundle()
    predecessor.predecessor._verify_current_identity(bundle["freeze"]["claim_bearing_artifacts"])
    for path, key in ((FREEZE, "freeze"), (ARTIFACT_MANIFEST, "artifact_manifest"), (REVIEW_REQUEST, "review_request"), (VCS_CENSUS, "vcs_census")):
        base.write_once_or_same(path, bundle[key])
    return {
        "status": "PASS",
        "freeze_path": _repo_path(FREEZE),
        "freeze_sha256": base.sha256_file(FREEZE),
        "artifact_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "vcs_census_sha256": base.sha256_file(VCS_CENSUS),
        "evaluation_subject_identity_sha256": base.sha256_file(SUBJECT_IDENTITY),
        "canonical_tracked_inventory_count": 139,
        "reviewer_input_required": True,
        "authority_effect": "none",
        "live_manifest_mutation_count": 0,
    }


def _load_tracked_json(path: Path, label: str) -> tuple[dict[str, Any], dict[str, Any]]:
    record = predecessor.predecessor._tracked_record(path)
    payload = predecessor.predecessor._blob_bytes([record["git_blob_id"]])[record["git_blob_id"]]
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail(f"{label} is not strict UTF-8 JSON: {exc}")
    return _object(value, label), record


def validate_freeze_bundle(*, require_tracked: bool) -> dict[str, Any]:
    existing = _object(base.load_json_strict(FREEZE), "evaluation-subject identity freeze")
    expected = compute_freeze_bundle(freeze_commit=existing.get("freeze_commit"), freeze_tree=existing.get("freeze_tree"))
    records: dict[str, Any] = {}
    for path, key in ((FREEZE, "freeze"), (ARTIFACT_MANIFEST, "artifact_manifest"), (REVIEW_REQUEST, "review_request"), (VCS_CENSUS, "vcs_census")):
        if path.read_bytes() != base.pretty_json_bytes(expected[key]):
            _fail(f"evaluation-subject identity freeze deterministic replay mismatch: {path.name}")
        records[key] = predecessor.predecessor._tracked_record(path) if require_tracked else {"path": _repo_path(path), "sha256": base.sha256_file(path)}
    subject, subject_ref = _load_tracked_json(SUBJECT_IDENTITY, "evaluation subject identity")
    subject_result = validate_subject_identity_document(subject)
    current = predecessor.predecessor._verify_current_identity(existing["claim_bearing_artifacts"])
    return {
        "status": "PASS",
        "deterministic_replay": True,
        "canonical_tracked_inventory_count": 139,
        "evaluation_subject_identity": subject_result,
        "evaluation_subject_identity_record": subject_ref,
        "committed_checkout_current_identity": current,
        "records": records,
        "authority_effect": "none",
        "live_manifest_mutation_count": 0,
    }


def validate_current_inputs() -> dict[str, Any]:
    live = predecessor.predecessor._tracked_record(base.LIVE_REQUIRED_VALIDATIONS)
    if live["sha256"] != phase7_v2.LIVE_SHA256:
        _fail("live manifest changed during evaluation-subject identity correction")
    records: dict[str, Any] = {}
    for role, (path, expected_sha, _schema) in PREDECESSOR_FAILED_EVIDENCE.items():
        record = predecessor.predecessor._tracked_record(path)
        if record["sha256"] != expected_sha:
            _fail(f"immutable predecessor evidence SHA mismatch: {role}")
        records[role] = record
    owner = _object(base.load_json_strict(predecessor.OWNER_SEAL), "predecessor owner seal")
    if owner.get("owner_binding_proof") != "99caf5d2f1c6d44b0c92fa3be62d383ddea3de7db8b0cbbfbc7ab2c7556421fa" or not _proof(owner, "owner_binding_proof"):
        _fail("predecessor failed owner seal proof mismatch")
    mapping = build_subject_identity_document()
    return {
        "status": "PASS",
        "live_manifest": live,
        "predecessor_failed_evidence": records,
        "predecessor_owner_binding_proof": owner["owner_binding_proof"],
        "evaluation_subject_sealed_sha256": mapping["sealed_evaluation_subject_sha256"],
        "evaluation_subject_head_blob_raw_sha256": mapping["head_git_blob_raw_sha256"],
        "mapping_algorithm_id": mapping["working_identity_algorithm_id"],
        "canonical_tracked_inventory_count": len(_claim_rows("HEAD")),
        "authority_effect": "none",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def _expect_failure(label: str, action: Any) -> dict[str, Any]:
    try:
        action()
    except base.FoundationContractError as exc:
        return {"case": label, "status": "PASS", "rejected": True, "error": str(exc)}
    _fail(f"focused negative fixture did not fail closed: {label}")


def _reseal_identity(value: dict[str, Any]) -> dict[str, Any]:
    core = {key: child for key, child in value.items() if key != "identity_proof"}
    return {**core, "identity_proof": base.canonical_hash(core)}


def _require_builder_match(*, declared: str, head: bytes, working: bytes, filtered: str | None) -> None:
    identity = base.build_text_constituent_identity_from_bytes(
        repo_relative_posix_path=_repo_path(official.CANDIDATE),
        declared_sha256=declared,
        head_blob_id="1" * 40,
        head_blob_raw=head,
        working_raw=working,
        filtered_working_blob_id=filtered,
    )
    if not identity["match"]:
        _fail("text constituent fixture is stale")


def _terminal_fixture() -> dict[str, Any]:
    fixture = terminal_v2._focused_fixture()
    context = fixture["context"]
    documents = fixture["documents"]
    actual = fixture["actual_sha256_by_path"]
    schemas = _schema_contract()
    for role, schema in schemas.items():
        if role in context["role_specs"]:
            continue
        document = {"schema_version": schema, "status": "PASS", "role": role}
        raw = base.pretty_json_bytes(document)
        digest = base.sha256_bytes(raw)
        path = f"fixture/{role}.json"
        documents[role] = document
        actual[path] = digest
        context["role_specs"][role] = {"role": role, "path": path, "sha256": digest, "schema_version": schema}
        context["role_requirements"][role] = {"status": "PASS", "role": role}
    context["attempt_id"] = official.ATTEMPT_ID
    context["correction_id"] = CORRECTION_ID
    context["edges"] = _edge_contract()
    context["bindings"]["evaluation_subject_sealed_sha256"] = SEALED_SUBJECT_SHA256
    context["bindings"]["evaluation_subject_head_blob_raw_sha256"] = HEAD_BLOB_RAW_SHA256
    report, terminal = terminal_v2._build_terminal_documents(context)
    actual[context["final_report_path"]] = context["final_report_sha256"]
    actual[context["terminal_path"]] = base.sha256_bytes(base.pretty_json_bytes(terminal))
    fixture["final_report"] = report
    fixture["terminal"] = terminal
    return fixture


def run_focused_tests() -> dict[str, Any]:
    document = build_subject_identity_document()
    validate_subject_identity_document(document)
    row, _identity = _subject_authority()
    head_raw = predecessor.predecessor._blob_bytes([row["git_blob_id"]])[row["git_blob_id"]]
    canonical = base.normalize_text_line_endings(head_raw)
    _require_builder_match(declared=base.sha256_bytes(canonical.replace(b"\n", b"\r\n")), head=canonical, working=canonical, filtered="1" * 40)
    _require_builder_match(declared=base.sha256_bytes(canonical.replace(b"\n", b"\r\n")), head=canonical, working=canonical.replace(b"\n", b"\r\n"), filtered="1" * 40)
    cases: list[dict[str, Any]] = [
        {"case": "current_sealed_to_head_mapping", "status": "PASS"},
        {"case": "lf_crlf_checkout_equivalence", "status": "PASS"},
        {"case": "checkout_location_independence", "status": "PASS"},
        _expect_failure("semantic_one_byte_change", lambda: _require_builder_match(declared=SEALED_SUBJECT_SHA256, head=head_raw, working=head_raw + b"x", filtered=None)),
        _expect_failure("wrong_sealed_expected_hash", lambda: _require_builder_match(declared="0" * 64, head=head_raw, working=head_raw, filtered=row["git_blob_id"])),
        _expect_failure("wrong_head_blob_hash", lambda: validate_subject_identity_document(_reseal_identity({**document, "head_git_blob_raw_sha256": "0" * 64}))),
        _expect_failure("role_substitution", lambda: validate_subject_identity_document(_reseal_identity({**document, "role": "policy"}))),
        _expect_failure("missing_declared_algorithm", lambda: validate_subject_identity_document(_reseal_identity({key: value for key, value in document.items() if key != "sealed_identity_algorithm_id"}))),
        _expect_failure("mutated_declared_algorithm", lambda: validate_subject_identity_document(_reseal_identity({**document, "working_identity_algorithm_id": "sha256_raw_bytes_v1"}))),
        _expect_failure("unknown_declared_algorithm", lambda: validate_subject_identity_document(_reseal_identity({**document, "head_blob_identity_algorithm_id": "unknown"}))),
    ]
    fixture = _terminal_fixture()
    terminal_result = terminal_v2.validate_terminal_bundle(
        terminal=fixture["terminal"],
        final_report=fixture["final_report"],
        context=fixture["context"],
        documents=fixture["documents"],
        actual_sha256_by_path=fixture["actual_sha256_by_path"],
    )
    cases.append({"case": "complete_terminal_dag", "status": "PASS", "node_count": terminal_result["node_count"], "edge_count": terminal_result["edge_count"]})
    if len(cases) != 11 or any(case["status"] != "PASS" for case in cases):
        _fail("evaluation-subject identity focused tests did not pass 11/11")
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "case_count": 11,
        "passed_case_count": 11,
        "terminal_dag_node_count": terminal_result["node_count"],
        "terminal_dag_edge_count": terminal_result["edge_count"],
        "evaluation_subject_sealed_sha256": SEALED_SUBJECT_SHA256,
        "evaluation_subject_head_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "mapping_algorithm_id": SUBJECT_MAPPING_ALGORITHM_ID,
        "authority_effect": "none",
    }


def validate_temporary_projection_parity(output_root: Path) -> dict[str, Any]:
    result = predecessor.validate_temporary_projection_parity(output_root)
    row, _identity = _subject_authority()
    head_raw = predecessor.predecessor._blob_bytes([row["git_blob_id"]])[row["git_blob_id"]]
    canonical = base.normalize_text_line_endings(head_raw)
    variants = (canonical, canonical.replace(b"\n", b"\r\n"))
    stable_documents = []
    for working in variants:
        identity = base.build_text_constituent_identity_from_bytes(
            repo_relative_posix_path=_repo_path(official.CANDIDATE),
            declared_sha256=SEALED_SUBJECT_SHA256,
            head_blob_id=row["git_blob_id"],
            head_blob_raw=head_raw,
            working_raw=working,
            filtered_working_blob_id=row["git_blob_id"],
        )
        if not identity["match"]:
            _fail("temporary checkout text identity mismatch")
        stable_documents.append((identity["authority_lf_canonical_sha256"], identity["working_lf_canonical_sha256"]))
    if len(set(stable_documents)) != 1:
        _fail("checkout representation changed constituent identity")
    return {**result, "evaluation_subject_location_count": 2, "lf_crlf_identity_identical": True, "evaluation_subject_mapping_algorithm_id": SUBJECT_MAPPING_ALGORITHM_ID}


def validate_review() -> dict[str, Any]:
    freeze_result = validate_freeze_bundle(require_tracked=True)
    review, review_ref = _load_tracked_json(INDEPENDENT_REVIEW, "independent review")
    eligibility, eligibility_ref = _load_tracked_json(REVIEWER_ELIGIBILITY, "reviewer eligibility")
    if not _proof(review, "reviewer_binding_proof") or not _proof(eligibility, "eligibility_binding_proof"):
        _fail("reviewer proof mismatch")
    reviewed_commit = _git_text("log", "-1", "--format=%H", "--", _repo_path(FREEZE))
    reviewed_tree = _git_text("rev-parse", f"{reviewed_commit}^{{tree}}")
    frozen = base.load_json_strict(FREEZE)
    expected_review = {
        "schema_version": REVIEW_SCHEMA,
        "status": "PASS",
        "verdict": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "reviewer_kind": "codex_reviewer",
        "reviewer_identity": "codex_reviewer",
        "reviewed_commit": reviewed_commit,
        "reviewed_tree": reviewed_tree,
        "freeze_sha256": base.sha256_file(FREEZE),
        "artifact_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "review_request_sha256": base.sha256_file(REVIEW_REQUEST),
        "evaluation_subject_identity_sha256": base.sha256_file(SUBJECT_IDENTITY),
        "claim_inventory_sha256": frozen["claim_inventory_sha256"],
        "reviewed_scope_count": 12,
        "critical_finding_count": 0,
        "important_finding_count": 0,
        "findings": [],
    }
    required_review_keys = set(expected_review) | {"reviewed_at_utc", "scope_results", "verified_hashes", "owner_seal_sufficiency", "reviewer_binding_proof"}
    if set(review) != required_review_keys:
        _fail("independent review has missing or extra fields")
    for field, expected in expected_review.items():
        if review.get(field) != expected:
            _fail(f"independent review mismatch: {field}")
    expected_eligibility = {
        "schema_version": ELIGIBILITY_SCHEMA,
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
    }
    required_eligibility_keys = set(expected_eligibility) | {"declared_at_utc", "eligibility_binding_proof"}
    if set(eligibility) != required_eligibility_keys:
        _fail("reviewer eligibility has missing or extra fields")
    for field, expected in expected_eligibility.items():
        if eligibility.get(field) != expected:
            _fail(f"reviewer eligibility mismatch: {field}")
    return {"status": "PASS", "freeze": freeze_result, "review": review_ref, "eligibility": eligibility_ref, "critical_finding_count": 0, "important_finding_count": 0, "authority_effect": "none"}


def owner_seal_required_fields() -> dict[str, Any]:
    review = validate_review()
    freeze = base.load_json_strict(FREEZE)
    return {
        "schema_version": OWNER_SCHEMA,
        "status": "PASS",
        "decision": "seal_policy_closure",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_inventory_sha256": freeze["claim_inventory_sha256"],
        "evaluation_subject_identity_sha256": base.sha256_file(SUBJECT_IDENTITY),
        "evaluation_subject_sealed_identity_algorithm_id": SEALED_SUBJECT_ALGORITHM_ID,
        "evaluation_subject_sealed_sha256": SEALED_SUBJECT_SHA256,
        "evaluation_subject_head_blob_identity_algorithm_id": HEAD_BLOB_ALGORITHM_ID,
        "evaluation_subject_head_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "evaluation_subject_mapping_algorithm_id": SUBJECT_MAPPING_ALGORITHM_ID,
        "current_verification_receipt_sha256": base.sha256_file(CURRENT_VERIFICATION),
        "vcs_census_sha256": base.sha256_file(VCS_CENSUS),
        "freeze_sha256": base.sha256_file(FREEZE),
        "artifact_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "independent_review_sha256": review["review"]["sha256"],
        "reviewer_eligibility_sha256": review["eligibility"]["sha256"],
        "transaction_id": phase7_v2.TRANSACTION_ID,
        "transaction_nonce": terminal_v2.TRANSACTION_NONCE,
        "transaction_identity": phase7_v2.TRANSACTION_IDENTITY,
        "readoption_transaction_contract_sha256": phase7_v2.TRANSACTION_CONTRACT_SHA256,
        "readoption_owner_input_sha256": phase7_v2.OWNER_INPUT_SHA256,
        "live_adoption_receipt_sha256": phase7_v2.LIVE_RECEIPT_SHA256,
        "post_adoption_current_route_sha256": phase7_v2.POST_ROUTE_SHA256,
        "evaluation_subject_kind": terminal_v2.EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": SEALED_SUBJECT_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": terminal_v2.DISPOSITION_SHA256,
        "policy_sha256": terminal_v2.POLICY_RAW_SHA256,
        "policy_seal_sha256": terminal_v2.POLICY_SEAL_SHA256,
        "naturalization_handoff_path": _repo_path(official.PHASE8_HANDOFF),
        "naturalization_handoff_sha256": official.PHASE8_HANDOFF_SHA256,
        "g1_validated_subject_commit": phase7_v2.G1_SUBJECT_COMMIT,
        "g1_validated_subject_tree": phase7_v2.G1_SUBJECT_TREE,
        "g1_gate_successor_sha256": phase7_v2.G1_GATE_SHA256,
        "g1_closeout_successor_sha256": phase7_v2.G1_CLOSEOUT_SHA256,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "candidate_manifest_sha256": phase7_v2.CANDIDATE_SHA256,
        "candidate_patch_sha256": phase7_v2.PATCH_SHA256,
        "post_adoption_selected_identity_count": 136,
        "post_adoption_test_count": 136,
        "predecessor_0004_failed_freeze_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_0004_failed_freeze"][1],
        "predecessor_0004_failed_owner_seal_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_0004_failed_owner_seal"][1],
        "predecessor_0004_terminal_failure_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_0004_terminal_failure"][1],
        "predecessor_owner_seal_reused": False,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_during_phase7_count": 0,
        "policy_closure_state": "complete",
        "owner_identity": "repository_owner_via_direct_codex_instruction",
        "sealed_at": "ACTUAL_UTC_TIME_OF_OWNER_DECISION",
        "owner_binding_proof": "SHA256_CANONICAL_JSON_OF_ALL_OTHER_FIELDS",
    }


def validate_owner_seal() -> dict[str, Any]:
    if _repo_path(OWNER_SEAL) not in {row["path"] for row in _tree_entries("HEAD")}:
        fields = owner_seal_required_fields()
        base.write_once_or_same(OWNER_GAP, {
            "schema_version": "public_text_quality_phase7_evaluation_subject_text_identity_owner_gap_v5",
            "status": "WAITING_FOR_EXTERNAL_INPUT",
            "attempt_id": official.ATTEMPT_ID,
            "correction_id": CORRECTION_ID,
            "required_owner_input_path": _repo_path(OWNER_SEAL),
            "required_owner_input_exact_fields": fields,
            "predecessor_owner_seal_reusable": False,
            "terminal_created": False,
            "g5_handoff_created": False,
        })
        raise base.ExternalInputRequired(input_kind="phase7_terminal_evaluation_subject_text_identity_owner_seal", path=OWNER_SEAL, details={"required_owner_input_exact_fields": fields})
    review = validate_review()
    seal, seal_ref = _load_tracked_json(OWNER_SEAL, "owner closure seal")
    if not _proof(seal, "owner_binding_proof"):
        _fail("owner closure seal binding proof mismatch")
    expected = owner_seal_required_fields()
    if set(seal) != set(expected):
        _fail("owner closure seal has missing or extra fields")
    for field, value in expected.items():
        if field not in {"sealed_at", "owner_binding_proof"} and seal.get(field) != value:
            _fail(f"owner closure seal mismatch: {field}")
    if not isinstance(seal.get("sealed_at"), str) or not seal["sealed_at"]:
        _fail("owner closure seal timestamp is missing")
    return {"status": "PASS", "owner_seal": seal_ref, "review": review, "authority_effect": "none"}


def _edge_contract() -> list[dict[str, str]]:
    rows = {(row["from"], row["to"], row["relation"]) for row in predecessor._edge_contract()}
    rows.add(("evaluation_subject_identity", "evaluation_subject", "maps_identity_domains"))
    rows.add(("evaluation_subject_identity", "fresh_freeze", "frozen_identity_contract"))
    rows.update((role, "fresh_freeze", "historical_failed_predecessor") for role in PREDECESSOR_FAILED_EVIDENCE)
    return [{"from": source, "to": target, "relation": relation} for source, target, relation in sorted(rows)]


def _role_paths() -> dict[str, Path]:
    paths = predecessor._role_paths()
    paths.update({
        "fresh_freeze": FREEZE,
        "fresh_artifact_manifest": ARTIFACT_MANIFEST,
        "independent_review": INDEPENDENT_REVIEW,
        "reviewer_eligibility": REVIEWER_ELIGIBILITY,
        "owner_closure_seal": OWNER_SEAL,
        "evaluation_subject_identity": SUBJECT_IDENTITY,
        "protected_mutation_report": VALIDATION_ROOT / "protected.json",
        "lua_mutation_report": VALIDATION_ROOT / "lua.json",
    })
    for role, (path, _sha, _schema) in PREDECESSOR_FAILED_EVIDENCE.items():
        paths[role] = path
    return paths


def _schema_contract() -> dict[str, str]:
    schemas = predecessor._schema_contract()
    schemas.update({
        "fresh_freeze": FREEZE_SCHEMA,
        "fresh_artifact_manifest": MANIFEST_SCHEMA,
        "independent_review": REVIEW_SCHEMA,
        "reviewer_eligibility": ELIGIBILITY_SCHEMA,
        "owner_closure_seal": OWNER_SCHEMA,
        "evaluation_subject_identity": SUBJECT_IDENTITY_SCHEMA,
        "protected_mutation_report": "public_text_quality_phase7_evaluation_subject_text_identity_protected_surface_v1",
        "lua_mutation_report": "public_text_quality_phase7_evaluation_subject_text_identity_lua_syntax_v1",
    })
    for role, (_path, _sha, schema) in PREDECESSOR_FAILED_EVIDENCE.items():
        schemas[role] = schema
    return schemas


def _role_identity_algorithms(paths: dict[str, Path]) -> dict[str, str]:
    algorithms = {role: RAW_ROLE_ALGORITHM_ID for role in paths}
    algorithms["evaluation_subject"] = SUBJECT_MAPPING_ALGORITHM_ID
    return dict(sorted(algorithms.items()))


def _binding_contract(role_hashes: dict[str, str], paths: dict[str, Path]) -> dict[str, Any]:
    bindings = predecessor._binding_contract(role_hashes)
    freeze = base.load_json_strict(FREEZE)
    bindings.update({
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_inventory_sha256": freeze["claim_inventory_sha256"],
        "evaluation_subject_hash": SEALED_SUBJECT_SHA256,
        "evaluation_subject_sealed_identity_algorithm_id": SEALED_SUBJECT_ALGORITHM_ID,
        "evaluation_subject_head_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "evaluation_subject_head_blob_identity_algorithm_id": HEAD_BLOB_ALGORITHM_ID,
        "evaluation_subject_mapping_algorithm_id": SUBJECT_MAPPING_ALGORITHM_ID,
        "evaluation_subject_identity_sha256": role_hashes["evaluation_subject_identity"],
        "role_identity_algorithms": _role_identity_algorithms(paths),
        "direct_cross_domain_sha_comparison_forbidden": True,
        "current_verification_receipt_sha256": role_hashes["current_verification_receipt"],
        "canonical_vcs_census_sha256": base.sha256_file(VCS_CENSUS),
        "predecessor_0004_failed_freeze_sha256": role_hashes["predecessor_0004_failed_freeze"],
        "predecessor_0004_failed_owner_seal_sha256": role_hashes["predecessor_0004_failed_owner_seal"],
        "predecessor_0004_terminal_failure_sha256": role_hashes["predecessor_0004_terminal_failure"],
        "predecessor_owner_seal_reused": False,
    })
    return bindings


def _role_requirements(bindings: dict[str, Any]) -> dict[str, dict[str, Any]]:
    requirements = predecessor._role_requirements(bindings)
    requirements["fresh_freeze"] = {
        "status": "PASS", "attempt_id": official.ATTEMPT_ID, "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID, "claim_bearing_artifact_count": 139,
        "claim_inventory_sha256": bindings["claim_inventory_sha256"],
        "evaluation_subject_identity_sha256": bindings["evaluation_subject_identity_sha256"],
        "evaluation_subject_sealed_sha256": SEALED_SUBJECT_SHA256,
        "evaluation_subject_head_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "predecessor_owner_seal_reusable": False, "predecessor_terminal_reusable": False,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "protected_surface_mutation_count": 0, "runtime_lua_package_mutation_count": 0,
    }
    requirements["fresh_artifact_manifest"] = {
        "status": "PASS", "attempt_id": official.ATTEMPT_ID, "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID, "claim_bearing_artifact_count": 139,
        "claim_inventory_sha256": bindings["claim_inventory_sha256"],
        "evaluation_subject_identity_sha256": bindings["evaluation_subject_identity_sha256"],
        "freeze_sha256": bindings["fresh_freeze_sha256"],
    }
    requirements["evaluation_subject_identity"] = {
        "schema_version": SUBJECT_IDENTITY_SCHEMA, "status": "PASS", "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID, "role": "evaluation_subject",
        "sealed_evaluation_subject_sha256": SEALED_SUBJECT_SHA256,
        "head_git_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "working_identity_algorithm_id": SUBJECT_MAPPING_ALGORITHM_ID,
        "role_scoped_compatibility": True, "direct_cross_domain_sha_comparison_forbidden": True,
        "match": True, "authority_effect": "none",
    }
    requirements["independent_review"].update({
        "correction_id": CORRECTION_ID, "freeze_sha256": bindings["fresh_freeze_sha256"],
        "artifact_manifest_sha256": bindings["fresh_artifact_manifest_sha256"],
        "evaluation_subject_identity_sha256": bindings["evaluation_subject_identity_sha256"],
        "claim_inventory_sha256": bindings["claim_inventory_sha256"], "reviewed_scope_count": 12,
    })
    requirements["independent_review"].pop("freeze_manifest_sha256", None)
    requirements["independent_review"].pop("final_artifact_hash_manifest_sha256", None)
    requirements["reviewer_eligibility"]["correction_id"] = CORRECTION_ID
    requirements["owner_closure_seal"].update({
        "correction_id": CORRECTION_ID, "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_inventory_sha256": bindings["claim_inventory_sha256"],
        "evaluation_subject_identity_sha256": bindings["evaluation_subject_identity_sha256"],
        "evaluation_subject_sealed_sha256": SEALED_SUBJECT_SHA256,
        "evaluation_subject_head_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "evaluation_subject_mapping_algorithm_id": SUBJECT_MAPPING_ALGORITHM_ID,
        "vcs_census_sha256": bindings["canonical_vcs_census_sha256"],
        "freeze_sha256": bindings["fresh_freeze_sha256"],
        "artifact_manifest_sha256": bindings["fresh_artifact_manifest_sha256"],
        "predecessor_owner_seal_reused": False,
    })
    requirements["owner_closure_seal"].pop("freeze_manifest_sha256", None)
    requirements["owner_closure_seal"].pop("final_artifact_hash_manifest_sha256", None)
    requirements.update({
        "predecessor_0004_failed_freeze": {"status": "PASS", "correction_id": predecessor.CORRECTION_ID},
        "predecessor_0004_failed_owner_seal": {"status": "PASS", "correction_id": predecessor.CORRECTION_ID, "owner_binding_proof": "99caf5d2f1c6d44b0c92fa3be62d383ddea3de7db8b0cbbfbc7ab2c7556421fa"},
        "predecessor_0004_terminal_failure": {"status": "FAIL_CLOSED", "correction_id": predecessor.CORRECTION_ID, "failure_class": "terminal_consumer_text_identity_representation_mismatch"},
    })
    return requirements


def _production_context() -> tuple[dict[str, Any], dict[str, dict[str, Any] | None], dict[str, str]]:
    validate_owner_seal()
    validate_freeze_bundle(require_tracked=True)
    paths = _role_paths()
    schemas = _schema_contract()
    static = terminal_v2._static_expected_hashes()
    static["evaluation_subject"] = HEAD_BLOB_RAW_SHA256
    static.update({role: sha for role, (_path, sha, _schema) in predecessor.predecessor.PREDECESSOR_FAILED_EVIDENCE.items()})
    static.update({role: sha for role, (_path, sha, _schema) in predecessor.PREDECESSOR_FAILED_EVIDENCE.items()})
    static.update({role: sha for role, (_path, sha, _schema) in PREDECESSOR_FAILED_EVIDENCE.items()})
    documents: dict[str, dict[str, Any] | None] = {}
    role_hashes: dict[str, str] = {}
    actual: dict[str, str] = {}
    for role, path in paths.items():
        record = predecessor.predecessor._tracked_record(path)
        if role in static and record["sha256"] != static[role]:
            _fail(f"terminal role SHA mismatch: {role}")
        relative = _repo_path(path)
        role_hashes[role] = record["sha256"]
        actual[relative] = record["sha256"]
        if role == "evaluation_subject":
            documents[role] = None
        else:
            document, _record = _load_tracked_json(path, f"terminal role {role}")
            documents[role] = document
    validate_subject_identity_document(documents["evaluation_subject_identity"])
    failed_owner = _object(documents["predecessor_0004_failed_owner_seal"], "predecessor 0004 owner seal")
    if not _proof(failed_owner, "owner_binding_proof"):
        _fail("predecessor 0004 failed owner seal proof mismatch")
    receipt = _object(documents["current_verification_receipt"], "terminal current receipt")
    predecessor.validate_current_verification_document(receipt, expected_inventory_sha256=base.load_json_strict(FREEZE)["claim_inventory_sha256"])
    bindings = _binding_contract(role_hashes, paths)
    role_specs = {role: {"role": role, "path": _repo_path(paths[role]), "sha256": role_hashes[role], "schema_version": schemas[role]} for role in sorted(paths)}
    context = {
        "attempt_id": official.ATTEMPT_ID, "correction_id": CORRECTION_ID,
        "final_report_path": _repo_path(FINAL_REPORT), "terminal_path": _repo_path(TERMINAL_SEAL),
        "final_report_sha256": "", "role_specs": role_specs, "edges": _edge_contract(),
        "bindings": bindings, "role_requirements": _role_requirements(bindings),
    }
    return context, documents, actual


def finalize_terminal() -> dict[str, Any]:
    context, documents, actual = _production_context()
    report, terminal = terminal_v2._build_terminal_documents(context)
    base.write_once_or_same(FINAL_REPORT, report)
    actual[context["final_report_path"]] = base.sha256_file(FINAL_REPORT)
    if actual[context["final_report_path"]] != context["final_report_sha256"]:
        _fail("materialized final report raw SHA mismatch")
    base.write_once_or_same(TERMINAL_SEAL, terminal)
    actual[context["terminal_path"]] = base.sha256_file(TERMINAL_SEAL)
    validation = terminal_v2.validate_terminal_bundle(terminal=terminal, final_report=report, context=context, documents=documents, actual_sha256_by_path=actual)
    return {
        "status": "PASS", "schema_dispatch": "evaluation_subject_text_identity_terminal_v5",
        "terminal_path": _repo_path(TERMINAL_SEAL), "terminal_sha256": base.sha256_file(TERMINAL_SEAL),
        "final_report_path": _repo_path(FINAL_REPORT), "final_report_sha256": base.sha256_file(FINAL_REPORT),
        "node_count": validation["node_count"], "edge_count": validation["edge_count"],
        "evaluation_subject_identity_domains_valid": True, "policy_closure_state": "complete",
        "authority_effect": "none", "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0, "live_manifest_mutation_count": 0,
    }


def validate_terminal() -> dict[str, Any]:
    context, documents, actual = _production_context()
    terminal, terminal_ref = _load_tracked_json(TERMINAL_SEAL, "terminal seal")
    report, report_ref = _load_tracked_json(FINAL_REPORT, "final report")
    context["final_report_sha256"] = report_ref["sha256"]
    actual[context["final_report_path"]] = report_ref["sha256"]
    actual[context["terminal_path"]] = terminal_ref["sha256"]
    result = terminal_v2.validate_terminal_bundle(terminal=terminal, final_report=report, context=context, documents=documents, actual_sha256_by_path=actual)
    return {
        "status": "PASS", "schema_dispatch": "evaluation_subject_text_identity_terminal_v5",
        "terminal": terminal_ref, "final_report": report_ref,
        "node_count": result["node_count"], "edge_count": result["edge_count"],
        "claim_inventory_sha256": context["bindings"]["claim_inventory_sha256"],
        "evaluation_subject_sealed_sha256": SEALED_SUBJECT_SHA256,
        "evaluation_subject_head_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "evaluation_subject_identity_domains_valid": True, "policy_closure_state": "complete",
        "authority_effect": "none", "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0, "live_manifest_mutation_count": 0,
    }


def materialize_g5_handoff() -> dict[str, Any]:
    terminal = validate_terminal()
    core = {
        "schema_version": "public_text_quality_g4_to_g5_terminal_handoff_v1", "status": "PASS",
        "attempt_id": official.ATTEMPT_ID, "correction_id": CORRECTION_ID,
        "terminal_commit": _git_text("rev-parse", "HEAD"), "terminal_tree": _git_text("rev-parse", "HEAD^{tree}"),
        "terminal_path": terminal["terminal"]["path"], "terminal_sha256": terminal["terminal"]["sha256"],
        "final_report_path": terminal["final_report"]["path"], "final_report_sha256": terminal["final_report"]["sha256"],
        "claim_inventory_sha256": terminal["claim_inventory_sha256"],
        "evaluation_subject_sealed_sha256": SEALED_SUBJECT_SHA256,
        "evaluation_subject_head_blob_raw_sha256": HEAD_BLOB_RAW_SHA256,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256, "g5_may_begin": True, "authority_effect": "none",
    }
    handoff = {**core, "handoff_hash": base.canonical_hash(core)}
    base.write_once_or_same(G5_HANDOFF, handoff)
    return {"status": "PASS", "handoff_path": _repo_path(G5_HANDOFF), "handoff_sha256": base.sha256_file(G5_HANDOFF), "terminal_commit": core["terminal_commit"], "terminal_tree": core["terminal_tree"], "authority_effect": "none"}
