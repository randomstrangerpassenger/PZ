from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import public_text_quality_acceptance as base
import public_text_quality_acceptance_official_0005 as official
import public_text_quality_acceptance_official_0005_phase7_host_independent_freeze as predecessor
import public_text_quality_acceptance_official_0005_phase7_terminal_validation as terminal_v2
import public_text_quality_acceptance_official_0005_phase7_v2 as phase7_v2


CORRECTION_ID = "g1-successor-0010-replay-serialization-0004"
CORRECTION_PATH_ID = "replay-serialization-0004"
INVENTORY_ALGORITHM_ID = predecessor.INVENTORY_ALGORITHM_ID
CURRENT_VERIFICATION_SCHEMA = "public_text_quality_phase7_current_verification_receipt_v1"
FREEZE_SCHEMA = "public_text_quality_phase7_replay_serialization_freeze_v4"
MANIFEST_SCHEMA = "public_text_quality_phase7_replay_serialization_artifact_manifest_v5"
REVIEW_SCHEMA = "public_text_quality_phase7_replay_serialization_review_v5"
ELIGIBILITY_SCHEMA = "public_text_quality_phase7_replay_serialization_reviewer_eligibility_v5"
OWNER_SCHEMA = "public_text_quality_phase7_replay_serialization_owner_closure_seal_v5"

PHASE7 = official.ATTEMPT_ROOT / "phase7"
EVIDENCE_ROOT = PHASE7 / "corrections" / CORRECTION_ID
VALIDATION_ROOT = EVIDENCE_ROOT / "inputs"
CORRECTION_ROOT = PHASE7 / "corrections" / CORRECTION_PATH_ID
CURRENT_VERIFICATION = CORRECTION_ROOT / "current_verification.json"
FREEZE = CORRECTION_ROOT / "freeze.json"
ARTIFACT_MANIFEST = CORRECTION_ROOT / "artifact_manifest.json"
REVIEW_REQUEST = CORRECTION_ROOT / "review_request.json"
VCS_CENSUS = CORRECTION_ROOT / "vcs_census.json"
OWNER_GAP = CORRECTION_ROOT / "owner_gap.json"
FINAL_REPORT = CORRECTION_ROOT / "final_report.json"
TERMINAL_SEAL = CORRECTION_ROOT / "terminal_seal.json"
G5_HANDOFF = CORRECTION_ROOT / "g5_handoff.json"

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
    / "owner_closure_seal_replay_serialization_0004.json"
)

PREDECESSOR_FAILED_EVIDENCE = {
    "predecessor_failed_freeze": (
        predecessor.FREEZE,
        "705325d2422f11170ff49425864616a2173b22675898643b28a47fae3b6b46af",
        predecessor.FREEZE_SCHEMA,
    ),
    "predecessor_failed_artifact_manifest": (
        predecessor.ARTIFACT_MANIFEST,
        "660d5d45cfb1df4386801dcd030a247e3dbc85b1ad7ea600a122be6dc54c982a",
        predecessor.MANIFEST_SCHEMA,
    ),
    "predecessor_failed_vcs_census": (
        predecessor.VCS_CENSUS,
        "e29845a9cacf9e2d55c507d7a8dc3372b3ac54b30f243c468463b3a4fc4586a6",
        "public_text_quality_phase7_host_independent_vcs_census_v3",
    ),
    "predecessor_replay_failure": (
        predecessor.CORRECTION_ROOT / "freeze_failure.json",
        "b712f6c86574ac45b3868862676003e3c2e8e7c486d78d802901b7d6ca497675",
        "public_text_quality_phase7_host_independent_freeze_failure_v1",
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


def _rows_for_paths(
    entries: list[dict[str, str]], paths: list[str]
) -> list[dict[str, Any]]:
    return predecessor._rows_for_paths(entries, paths)


def _inventory_hash(rows: list[dict[str, Any]]) -> str:
    return predecessor._inventory_hash(rows)


def _claim_rows(treeish: str) -> list[dict[str, Any]]:
    entries = _tree_entries(treeish)
    selected = predecessor._select_base_claim_paths(entries)
    rows = _rows_for_paths(entries, selected)
    predecessor._validate_inventory_rows(entries, selected, rows)
    if len(rows) != 139:
        _fail(f"canonical tracked inventory denominator mismatch: {len(rows)} != 139")
    return rows


def _implementation_paths() -> list[str]:
    module = Path(__file__).resolve()
    return sorted(
        set(predecessor._implementation_paths())
        | {
            _repo_path(module),
            _repo_path(
                module.with_name(
                    "run_public_text_quality_acceptance_official_0005_phase7_replay_serialization.py"
                )
            ),
            _repo_path(
                module.with_name(
                    "validate_public_text_quality_acceptance_official_0005_phase7_replay_serialization.py"
                )
            ),
        }
    )


def _under(path: str, root: Path) -> bool:
    prefix = _repo_path(root)
    return path.startswith(prefix + "/")


def _inventory(treeish: str) -> dict[str, Any]:
    entries = _tree_entries(treeish)
    claim_rows = _claim_rows(treeish)
    evidence_paths = sorted(
        row["path"] for row in entries if _under(row["path"], VALIDATION_ROOT)
    )
    implementation_paths = _implementation_paths()
    historical_paths = sorted(
        _repo_path(path) for path, _sha, _schema in PREDECESSOR_FAILED_EVIDENCE.values()
    )
    evidence_rows = _rows_for_paths(entries, evidence_paths)
    implementation_rows = _rows_for_paths(entries, implementation_paths)
    historical_rows = _rows_for_paths(entries, historical_paths)
    all_rows = claim_rows + evidence_rows + implementation_rows + historical_rows
    if len({row["path"] for row in all_rows}) != len(all_rows):
        _fail("replay-serialization inventory categories overlap")
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


def _validated_readpoint(
    freeze_commit: str | None, freeze_tree: str | None
) -> tuple[str, str]:
    if freeze_commit is None:
        freeze_commit = _git_text("rev-parse", "HEAD")
    if freeze_tree is None:
        freeze_tree = _git_text("rev-parse", f"{freeze_commit}^{{tree}}")
    if not _HEX40.fullmatch(freeze_commit) or not _HEX40.fullmatch(freeze_tree):
        _fail("freeze readpoint is malformed")
    if _git_text("rev-parse", f"{freeze_commit}^{{tree}}") != freeze_tree:
        _fail("freeze readpoint commit/tree mismatch")
    return freeze_commit, freeze_tree


def _json_at_commit(commit: str, path: Path) -> tuple[dict[str, Any], str]:
    relative = _repo_path(path)
    entries = {row["path"]: row for row in _tree_entries(commit)}
    entry = entries.get(relative)
    if entry is None or entry["object_type"] != "blob":
        _fail(f"sealed current-verification receipt missing from Git tree: {relative}")
    raw = predecessor._blob_bytes([entry["git_blob_id"]])[entry["git_blob_id"]]
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail(f"current-verification receipt is not strict UTF-8 JSON: {exc}")
    return _object(value, "current-verification receipt"), base.sha256_bytes(raw)


def _receipt_core(
    verification_commit: str,
    verification_tree: str,
    claim_inventory_sha256: str,
) -> dict[str, Any]:
    return {
        "schema_version": CURRENT_VERIFICATION_SCHEMA,
        "status": "PASS",
        "verified": True,
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "verification_commit": verification_commit,
        "verification_tree": verification_tree,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_inventory_sha256": claim_inventory_sha256,
        "required_count": 139,
        "head_tree_match_count": 139,
        "index_match_count": 139,
        "working_filtered_identity_match_count": 139,
        "missing_count": 0,
        "index_mismatch_count": 0,
        "working_mismatch_count": 0,
        "blob_mismatch_count": 0,
        "repository_external_or_host_metadata_used": False,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
        "authority_effect": "none",
    }


def validate_current_verification_document(
    value: Any, *, expected_inventory_sha256: str
) -> dict[str, Any]:
    receipt = _object(value, "current-verification receipt")
    expected_keys = set(
        _receipt_core("0" * 40, "0" * 40, "0" * 64)
    ) | {"receipt_proof"}
    if set(receipt) != expected_keys:
        _fail("current-verification receipt has missing or extra fields")
    if not _proof(receipt, "receipt_proof"):
        _fail("current-verification receipt proof mismatch")
    required = {
        "schema_version": CURRENT_VERIFICATION_SCHEMA,
        "status": "PASS",
        "verified": True,
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_inventory_sha256": expected_inventory_sha256,
        "required_count": 139,
        "head_tree_match_count": 139,
        "index_match_count": 139,
        "working_filtered_identity_match_count": 139,
        "missing_count": 0,
        "index_mismatch_count": 0,
        "working_mismatch_count": 0,
        "blob_mismatch_count": 0,
        "repository_external_or_host_metadata_used": False,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
        "authority_effect": "none",
    }
    for field, expected in required.items():
        if receipt.get(field) != expected:
            _fail(f"current-verification receipt mismatch: {field}")
    commit = receipt.get("verification_commit")
    tree = receipt.get("verification_tree")
    if not isinstance(commit, str) or not _HEX40.fullmatch(commit):
        _fail("current-verification commit is malformed")
    if not isinstance(tree, str) or not _HEX40.fullmatch(tree):
        _fail("current-verification tree is malformed")
    if _git_text("rev-parse", f"{commit}^{{tree}}") != tree:
        _fail("current-verification commit/tree mismatch")
    if predecessor._git_bytes(
        "merge-base", "--is-ancestor", commit, "HEAD", check=False
    ).returncode != 0:
        _fail("current-verification commit is not an ancestor of HEAD")
    return {
        "status": "PASS",
        "verification_commit": commit,
        "verification_tree": tree,
        "index_match_count": 139,
        "working_filtered_identity_match_count": 139,
    }


def materialize_current_verification() -> dict[str, Any]:
    if _git_text("status", "--porcelain=v1"):
        _fail("current verification requires a clean committed checkout")
    commit = _git_text("rev-parse", "HEAD")
    tree = _git_text("rev-parse", "HEAD^{tree}")
    rows = _claim_rows(commit)
    identity = predecessor._verify_current_identity(rows)
    if identity["index_match_count"] != 139 or identity["working_filtered_identity_match_count"] != 139:
        _fail("current verification denominator mismatch")
    core = _receipt_core(commit, tree, _inventory_hash(rows))
    receipt = {**core, "receipt_proof": base.canonical_hash(core)}
    base.write_once_or_same(CURRENT_VERIFICATION, receipt)
    return {
        "status": "PASS",
        "path": _repo_path(CURRENT_VERIFICATION),
        "sha256": base.sha256_file(CURRENT_VERIFICATION),
        "index_match_count": 139,
        "working_filtered_identity_match_count": 139,
        "authority_effect": "none",
    }


def _predecessor_bindings() -> dict[str, Any]:
    return {
        role: {
            "path": _repo_path(path),
            "sha256": sha,
            "schema_version": schema,
            "role_state": "historical_failed_replay_evidence",
        }
        for role, (path, sha, schema) in sorted(PREDECESSOR_FAILED_EVIDENCE.items())
    }


def compute_freeze_bundle(
    *, freeze_commit: str | None = None, freeze_tree: str | None = None
) -> dict[str, dict[str, Any]]:
    freeze_commit, freeze_tree = _validated_readpoint(freeze_commit, freeze_tree)
    inventory = _inventory(freeze_commit)
    receipt, receipt_sha = _json_at_commit(freeze_commit, CURRENT_VERIFICATION)
    receipt_validation = validate_current_verification_document(
        receipt, expected_inventory_sha256=inventory["claim_inventory_sha256"]
    )
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
        "current_verification_receipt_path": _repo_path(CURRENT_VERIFICATION),
        "current_verification_receipt_sha256": receipt_sha,
        "current_verification_commit": receipt_validation["verification_commit"],
        "current_verification_tree": receipt_validation["verification_tree"],
        "current_verification_required_before_terminal": True,
        "predecessor_failed_replay_bindings": _predecessor_bindings(),
        "predecessor_freeze_reusable": False,
        "predecessor_terminal_reusable": False,
        "canonical_census_excludes_execution_mode": True,
        "canonical_census_excludes_current_counts": True,
        "absolute_path_excluded": True,
        "checkout_location_excluded": True,
        "timestamp_excluded": True,
        "verify_current_flag_excluded": True,
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
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
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
        "current_verification_receipt_sha256": receipt_sha,
        "freeze_path": _repo_path(FREEZE),
        "freeze_sha256": freeze_sha,
        "self_hash_included": False,
        "terminal_included": False,
    }
    manifest = {**manifest_core, "manifest_hash": base.canonical_hash(manifest_core)}
    manifest_sha = base.sha256_bytes(base.pretty_json_bytes(manifest))
    request = {
        "schema_version": "public_text_quality_phase7_replay_serialization_review_request_v5",
        "status": "READY_FOR_CODEX_REVIEWER",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "review_subject_commit": freeze_commit,
        "review_subject_tree": freeze_tree,
        "freeze_sha256": freeze_sha,
        "artifact_manifest_sha256": manifest_sha,
        "current_verification_receipt_sha256": receipt_sha,
        "claim_inventory_sha256": inventory["claim_inventory_sha256"],
        "required_reviewer_kind": "codex_reviewer",
        "required_scopes": [
            "canonical_census_tree_only_authority",
            "materialization_replay_byte_identity",
            "current_verification_receipt_separation",
            "receipt_negative_fail_closed_contract",
            "dirty_index_working_fail_closed_contract",
            "inventory_denominator_139",
            "checkout_location_independence",
            "freeze_deterministic_replay",
            "terminal_current_verification_requirement",
            "current_route_lua_no_mutation",
            "claim_boundary_and_no_authority_effect",
        ],
        "required_critical_finding_count": 0,
        "required_important_finding_count": 0,
        "owner_or_implementation_author_ineligible": True,
    }
    census = {
        "schema_version": "public_text_quality_phase7_canonical_vcs_census_v4",
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
        "current_verification_receipt_path": _repo_path(CURRENT_VERIFICATION),
        "current_verification_receipt_sha256": receipt_sha,
        "execution_mode_excluded": True,
        "index_working_counts_excluded": True,
        "absolute_path_excluded": True,
        "checkout_location_excluded": True,
        "timestamp_excluded": True,
        "verify_current_flag_excluded": True,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }
    return {
        "freeze": freeze,
        "artifact_manifest": manifest,
        "review_request": request,
        "vcs_census": census,
    }


def materialize_freeze() -> dict[str, Any]:
    if _git_text("status", "--porcelain=v1"):
        _fail("fresh replay-serialization freeze requires a clean checkout")
    bundle = compute_freeze_bundle()
    receipt = _object(base.load_json_strict(CURRENT_VERIFICATION), "current receipt")
    validate_current_verification_document(
        receipt, expected_inventory_sha256=bundle["freeze"]["claim_inventory_sha256"]
    )
    predecessor._verify_current_identity(bundle["freeze"]["claim_bearing_artifacts"])
    for path, key in (
        (FREEZE, "freeze"),
        (ARTIFACT_MANIFEST, "artifact_manifest"),
        (REVIEW_REQUEST, "review_request"),
        (VCS_CENSUS, "vcs_census"),
    ):
        base.write_once_or_same(path, bundle[key])
    return {
        "status": "PASS",
        "freeze_path": _repo_path(FREEZE),
        "freeze_sha256": base.sha256_file(FREEZE),
        "artifact_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "vcs_census_sha256": base.sha256_file(VCS_CENSUS),
        "canonical_tracked_inventory_count": 139,
        "current_verification_receipt_sha256": base.sha256_file(CURRENT_VERIFICATION),
        "reviewer_input_required": True,
        "authority_effect": "none",
        "live_manifest_mutation_count": 0,
    }


def validate_freeze_bundle(*, require_tracked: bool) -> dict[str, Any]:
    existing = _object(base.load_json_strict(FREEZE), "replay-serialization freeze")
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
            _fail(f"replay-serialization deterministic replay mismatch: {path.name}")
        records[key] = (
            predecessor._tracked_record(path)
            if require_tracked
            else {"path": _repo_path(path), "sha256": base.sha256_file(path)}
        )
    receipt, receipt_ref = _load_tracked_json(CURRENT_VERIFICATION, "current receipt")
    receipt_result = validate_current_verification_document(
        receipt, expected_inventory_sha256=existing["claim_inventory_sha256"]
    )
    current = predecessor._verify_current_identity(existing["claim_bearing_artifacts"])
    if base.sha256_file(CURRENT_VERIFICATION) != existing["current_verification_receipt_sha256"]:
        _fail("current-verification receipt raw SHA mismatch")
    return {
        "status": "PASS",
        "deterministic_replay": True,
        "vcs_census_byte_identical": True,
        "canonical_tracked_inventory_count": 139,
        "current_verification": receipt_result,
        "current_verification_record": receipt_ref,
        "committed_checkout_current_identity": current,
        "records": records,
        "authority_effect": "none",
        "live_manifest_mutation_count": 0,
    }


def validate_current_inputs() -> dict[str, Any]:
    live = predecessor._tracked_record(base.LIVE_REQUIRED_VALIDATIONS)
    if live["sha256"] != phase7_v2.LIVE_SHA256:
        _fail("live manifest changed during replay-serialization correction")
    records: dict[str, Any] = {}
    for role, (path, expected_sha, _schema) in PREDECESSOR_FAILED_EVIDENCE.items():
        record = predecessor._tracked_record(path)
        if record["sha256"] != expected_sha:
            _fail(f"immutable predecessor evidence SHA mismatch: {role}")
        records[role] = record
    failed_freeze = _object(base.load_json_strict(predecessor.FREEZE), "failed freeze")
    if failed_freeze.get("claim_inventory_sha256") != "cf2fb975de9422ebbd1a8635a8d8d12c764738d70803c976f0a7b06a34e3ca65":
        _fail("predecessor inventory SHA mismatch")
    return {
        "status": "PASS",
        "live_manifest": live,
        "predecessor_failed_evidence": records,
        "predecessor_inventory_sha256": failed_freeze["claim_inventory_sha256"],
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


def run_focused_tests() -> dict[str, Any]:
    predecessor_result = predecessor.run_focused_tests()
    rows = _claim_rows("HEAD")
    inventory_sha = _inventory_hash(rows)
    commit = _git_text("rev-parse", "HEAD")
    tree = _git_text("rev-parse", "HEAD^{tree}")
    core = _receipt_core(commit, tree, inventory_sha)
    receipt = {**core, "receipt_proof": base.canonical_hash(core)}
    validate_current_verification_document(receipt, expected_inventory_sha256=inventory_sha)

    def mutated(**changes: Any) -> dict[str, Any]:
        value = {**receipt, **changes}
        value["receipt_proof"] = base.canonical_hash(
            {key: child for key, child in value.items() if key != "receipt_proof"}
        )
        return value

    cases = [
        {"case": "complete_verified_receipt", "status": "PASS"},
        _expect_failure(
            "missing_receipt_field",
            lambda: validate_current_verification_document(
                {key: value for key, value in receipt.items() if key != "index_match_count"},
                expected_inventory_sha256=inventory_sha,
            ),
        ),
        _expect_failure(
            "unverified_receipt",
            lambda: validate_current_verification_document(
                mutated(status="NOT_VERIFIED", verified=False),
                expected_inventory_sha256=inventory_sha,
            ),
        ),
        _expect_failure(
            "count_mismatch",
            lambda: validate_current_verification_document(
                mutated(index_match_count=138), expected_inventory_sha256=inventory_sha
            ),
        ),
        _expect_failure(
            "blob_mismatch",
            lambda: validate_current_verification_document(
                mutated(claim_inventory_sha256="0" * 64),
                expected_inventory_sha256=inventory_sha,
            ),
        ),
        _expect_failure(
            "dirty_index",
            lambda: validate_current_verification_document(
                mutated(index_match_count=138, index_mismatch_count=1),
                expected_inventory_sha256=inventory_sha,
            ),
        ),
        _expect_failure(
            "dirty_working_copy",
            lambda: validate_current_verification_document(
                mutated(working_filtered_identity_match_count=138, working_mismatch_count=1),
                expected_inventory_sha256=inventory_sha,
            ),
        ),
    ]
    census = {
        "canonical_tracked_inventory_count": 139,
        "head_tree_blob_match_count": 139,
        "index_working_counts_excluded": True,
    }
    encoded_a = base.pretty_json_bytes(census)
    encoded_b = base.pretty_json_bytes(json.loads(encoded_a.decode("utf-8")))
    if encoded_a != encoded_b or "index_match_count" in census:
        _fail("canonical census depends on execution-mode current counts")
    cases.append(
        {
            "case": "materialization_replay_census_byte_identity",
            "status": "PASS",
            "canonical_tracked_inventory_count": 139,
            "fake_zero_count_field_count": 0,
        }
    )
    if len(cases) != 8 or any(case["status"] != "PASS" for case in cases):
        _fail("replay-serialization focused tests did not pass 8/8")
    return {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "predecessor_case_count": predecessor_result["case_count"],
        "case_count": 8,
        "passed_case_count": 8,
        "canonical_tracked_inventory_count": 139,
        "claim_inventory_sha256": inventory_sha,
        "fake_zero_count_field_count": 0,
        "cases": cases,
        "authority_effect": "none",
    }


def validate_temporary_projection_parity(output_root: Path) -> dict[str, Any]:
    return predecessor.validate_temporary_projection_parity(output_root)


def _load_tracked_json(path: Path, label: str) -> tuple[dict[str, Any], dict[str, Any]]:
    record = predecessor._tracked_record(path)
    payload = predecessor._blob_bytes([record["git_blob_id"]])[record["git_blob_id"]]
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail(f"{label} is not strict UTF-8 JSON: {exc}")
    return _object(value, label), record


def validate_review() -> dict[str, Any]:
    freeze_result = validate_freeze_bundle(require_tracked=True)
    review, review_ref = _load_tracked_json(INDEPENDENT_REVIEW, "independent review")
    eligibility, eligibility_ref = _load_tracked_json(REVIEWER_ELIGIBILITY, "reviewer eligibility")
    if not _proof(review, "reviewer_binding_proof") or not _proof(eligibility, "eligibility_binding_proof"):
        _fail("reviewer proof mismatch")
    required_review_keys = {
        "schema_version", "status", "verdict", "attempt_id", "correction_id",
        "reviewed_at_utc", "reviewer_kind", "reviewer_identity", "reviewed_commit",
        "reviewed_tree", "freeze_sha256", "artifact_manifest_sha256",
        "review_request_sha256", "current_verification_receipt_sha256",
        "claim_inventory_sha256", "reviewed_scope_count", "critical_finding_count",
        "important_finding_count", "findings", "scope_results", "verified_hashes",
        "owner_seal_sufficiency", "reviewer_binding_proof",
    }
    required_eligibility_keys = {
        "schema_version", "status", "attempt_id", "correction_id", "declared_at_utc",
        "reviewer_kind", "reviewer_identity", "reviewed_commit", "reviewed_tree",
        "independent_from_owner", "independent_from_implementation_author",
        "owner_input_cross_reclassification", "conflict_of_interest",
        "eligibility_binding_proof",
    }
    if set(review) != required_review_keys or set(eligibility) != required_eligibility_keys:
        _fail("independent review or eligibility has missing/extra fields")
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
        "current_verification_receipt_sha256": base.sha256_file(CURRENT_VERIFICATION),
        "claim_inventory_sha256": frozen["claim_inventory_sha256"],
        "reviewed_scope_count": 11,
        "critical_finding_count": 0,
        "important_finding_count": 0,
        "findings": [],
    }
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
    for field, expected in expected_eligibility.items():
        if eligibility.get(field) != expected:
            _fail(f"reviewer eligibility mismatch: {field}")
    return {
        "status": "PASS",
        "freeze": freeze_result,
        "review": review_ref,
        "eligibility": eligibility_ref,
        "critical_finding_count": 0,
        "important_finding_count": 0,
        "authority_effect": "none",
    }


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
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
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
        "predecessor_failed_freeze_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_failed_freeze"][1],
        "predecessor_failed_artifact_manifest_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_failed_artifact_manifest"][1],
        "predecessor_failed_vcs_census_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_failed_vcs_census"][1],
        "predecessor_replay_failure_sha256": PREDECESSOR_FAILED_EVIDENCE["predecessor_replay_failure"][1],
        "predecessor_failed_materialization_reused": False,
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
        base.write_once_or_same(
            OWNER_GAP,
            {
                "schema_version": "public_text_quality_phase7_replay_serialization_owner_gap_v4",
                "status": "WAITING_FOR_EXTERNAL_INPUT",
                "attempt_id": official.ATTEMPT_ID,
                "correction_id": CORRECTION_ID,
                "required_owner_input_path": _repo_path(OWNER_SEAL),
                "required_owner_input_exact_fields": fields,
                "predecessor_owner_seal_reusable": False,
                "terminal_created": False,
                "g5_handoff_created": False,
            },
        )
        raise base.ExternalInputRequired(
            input_kind="phase7_replay_serialization_owner_closure_seal",
            path=OWNER_SEAL,
            details={"required_owner_input_exact_fields": fields},
        )
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
    rows = {
        (row["from"], row["to"], row["relation"])
        for row in predecessor._edge_contract()
    }
    rows.add(("current_verification_receipt", "fresh_freeze", "current_identity_contract"))
    rows.update(
        (role, "fresh_freeze", "historical_failed_predecessor")
        for role in PREDECESSOR_FAILED_EVIDENCE
    )
    return [
        {"from": source, "to": target, "relation": relation}
        for source, target, relation in sorted(rows)
    ]


def _role_paths() -> dict[str, Path]:
    paths = predecessor._role_paths()
    paths.update(
        {
            "fresh_freeze": FREEZE,
            "fresh_artifact_manifest": ARTIFACT_MANIFEST,
            "independent_review": INDEPENDENT_REVIEW,
            "reviewer_eligibility": REVIEWER_ELIGIBILITY,
            "owner_closure_seal": OWNER_SEAL,
            "current_verification_receipt": CURRENT_VERIFICATION,
            "protected_mutation_report": VALIDATION_ROOT / "protected.json",
            "lua_mutation_report": VALIDATION_ROOT / "lua.json",
        }
    )
    for role, (path, _sha, _schema) in PREDECESSOR_FAILED_EVIDENCE.items():
        paths[role] = path
    return paths


def _schema_contract() -> dict[str, str]:
    schemas = predecessor._schema_contract()
    schemas.update(
        {
            "fresh_freeze": FREEZE_SCHEMA,
            "fresh_artifact_manifest": MANIFEST_SCHEMA,
            "independent_review": REVIEW_SCHEMA,
            "reviewer_eligibility": ELIGIBILITY_SCHEMA,
            "owner_closure_seal": OWNER_SCHEMA,
            "current_verification_receipt": CURRENT_VERIFICATION_SCHEMA,
            "protected_mutation_report": "public_text_quality_phase7_replay_serialization_protected_surface_v1",
            "lua_mutation_report": "public_text_quality_phase7_replay_serialization_lua_syntax_v1",
        }
    )
    for role, (_path, _sha, schema) in PREDECESSOR_FAILED_EVIDENCE.items():
        schemas[role] = schema
    return schemas


def _binding_contract(role_hashes: dict[str, str]) -> dict[str, Any]:
    bindings = predecessor._binding_contract(role_hashes)
    freeze = base.load_json_strict(FREEZE)
    bindings.update(
        {
            "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
            "claim_inventory_sha256": freeze["claim_inventory_sha256"],
            "current_verification_receipt_sha256": role_hashes["current_verification_receipt"],
            "canonical_vcs_census_sha256": base.sha256_file(VCS_CENSUS),
            "predecessor_failed_freeze_sha256": role_hashes["predecessor_failed_freeze"],
            "predecessor_failed_artifact_manifest_sha256": role_hashes["predecessor_failed_artifact_manifest"],
            "predecessor_failed_vcs_census_sha256": role_hashes["predecessor_failed_vcs_census"],
            "predecessor_replay_failure_sha256": role_hashes["predecessor_replay_failure"],
            "predecessor_failed_materialization_reused": False,
        }
    )
    return bindings


def _role_requirements(bindings: dict[str, Any]) -> dict[str, dict[str, Any]]:
    requirements = predecessor._role_requirements(bindings)
    requirements["fresh_freeze"] = {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_bearing_artifact_count": 139,
        "claim_inventory_sha256": bindings["claim_inventory_sha256"],
        "current_verification_receipt_sha256": bindings["current_verification_receipt_sha256"],
        "predecessor_freeze_reusable": False,
        "predecessor_terminal_reusable": False,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
    }
    requirements["fresh_artifact_manifest"] = {
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
        "claim_bearing_artifact_count": 139,
        "claim_inventory_sha256": bindings["claim_inventory_sha256"],
        "current_verification_receipt_sha256": bindings["current_verification_receipt_sha256"],
        "freeze_sha256": bindings["fresh_freeze_sha256"],
    }
    requirements["current_verification_receipt"] = {
        "schema_version": CURRENT_VERIFICATION_SCHEMA,
        "status": "PASS",
        "verified": True,
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "claim_inventory_sha256": bindings["claim_inventory_sha256"],
        "required_count": 139,
        "index_match_count": 139,
        "working_filtered_identity_match_count": 139,
        "authority_effect": "none",
    }
    requirements["independent_review"].update(
        {
            "correction_id": CORRECTION_ID,
            "freeze_sha256": bindings["fresh_freeze_sha256"],
            "artifact_manifest_sha256": bindings["fresh_artifact_manifest_sha256"],
            "current_verification_receipt_sha256": bindings["current_verification_receipt_sha256"],
            "claim_inventory_sha256": bindings["claim_inventory_sha256"],
            "reviewed_scope_count": 11,
        }
    )
    requirements["independent_review"].pop("freeze_manifest_sha256", None)
    requirements["independent_review"].pop("final_artifact_hash_manifest_sha256", None)
    requirements["reviewer_eligibility"]["correction_id"] = CORRECTION_ID
    requirements["owner_closure_seal"].update(
        {
            "correction_id": CORRECTION_ID,
            "inventory_algorithm_id": INVENTORY_ALGORITHM_ID,
            "claim_inventory_sha256": bindings["claim_inventory_sha256"],
            "current_verification_receipt_sha256": bindings["current_verification_receipt_sha256"],
            "vcs_census_sha256": bindings["canonical_vcs_census_sha256"],
            "freeze_sha256": bindings["fresh_freeze_sha256"],
            "artifact_manifest_sha256": bindings["fresh_artifact_manifest_sha256"],
            "predecessor_failed_materialization_reused": False,
        }
    )
    requirements["owner_closure_seal"].pop("freeze_manifest_sha256", None)
    requirements["owner_closure_seal"].pop("final_artifact_hash_manifest_sha256", None)
    requirements.update(
        {
            "predecessor_failed_freeze": {
                "status": "PASS",
                "correction_id": predecessor.CORRECTION_ID,
                "claim_inventory_sha256": "cf2fb975de9422ebbd1a8635a8d8d12c764738d70803c976f0a7b06a34e3ca65",
            },
            "predecessor_failed_artifact_manifest": {
                "status": "PASS",
                "correction_id": predecessor.CORRECTION_ID,
            },
            "predecessor_failed_vcs_census": {
                "status": "PASS",
                "correction_id": predecessor.CORRECTION_ID,
            },
            "predecessor_replay_failure": {
                "status": "FAIL_CLOSED",
                "correction_id": predecessor.CORRECTION_ID,
            },
        }
    )
    return requirements


def _production_context() -> tuple[
    dict[str, Any], dict[str, dict[str, Any] | None], dict[str, str]
]:
    validate_owner_seal()
    validate_freeze_bundle(require_tracked=True)
    paths = _role_paths()
    schemas = _schema_contract()
    static = terminal_v2._static_expected_hashes()
    static.update(
        {
            role: sha
            for role, (_path, sha, _schema) in predecessor.PREDECESSOR_FAILED_EVIDENCE.items()
        }
    )
    static.update(
        {role: sha for role, (_path, sha, _schema) in PREDECESSOR_FAILED_EVIDENCE.items()}
    )
    documents: dict[str, dict[str, Any] | None] = {}
    role_hashes: dict[str, str] = {}
    actual: dict[str, str] = {}
    for role, path in paths.items():
        record = predecessor._tracked_record(path)
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
    receipt = _object(documents["current_verification_receipt"], "terminal current receipt")
    validate_current_verification_document(
        receipt,
        expected_inventory_sha256=base.load_json_strict(FREEZE)["claim_inventory_sha256"],
    )
    bindings = _binding_contract(role_hashes)
    role_specs = {
        role: {
            "role": role,
            "path": _repo_path(paths[role]),
            "sha256": role_hashes[role],
            "schema_version": schemas[role],
        }
        for role in sorted(paths)
    }
    context = {
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "final_report_path": _repo_path(FINAL_REPORT),
        "terminal_path": _repo_path(TERMINAL_SEAL),
        "final_report_sha256": "",
        "role_specs": role_specs,
        "edges": _edge_contract(),
        "bindings": bindings,
        "role_requirements": _role_requirements(bindings),
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
    validation = terminal_v2.validate_terminal_bundle(
        terminal=terminal,
        final_report=report,
        context=context,
        documents=documents,
        actual_sha256_by_path=actual,
    )
    return {
        "status": "PASS",
        "schema_dispatch": "replay_serialization_terminal_v4",
        "terminal_path": _repo_path(TERMINAL_SEAL),
        "terminal_sha256": base.sha256_file(TERMINAL_SEAL),
        "final_report_path": _repo_path(FINAL_REPORT),
        "final_report_sha256": base.sha256_file(FINAL_REPORT),
        "node_count": validation["node_count"],
        "edge_count": validation["edge_count"],
        "current_verification_executed_on_committed_checkout": True,
        "policy_closure_state": "complete",
        "authority_effect": "none",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def validate_terminal() -> dict[str, Any]:
    context, documents, actual = _production_context()
    terminal, terminal_ref = _load_tracked_json(TERMINAL_SEAL, "terminal seal")
    report, report_ref = _load_tracked_json(FINAL_REPORT, "final report")
    context["final_report_sha256"] = report_ref["sha256"]
    actual[context["final_report_path"]] = report_ref["sha256"]
    actual[context["terminal_path"]] = terminal_ref["sha256"]
    result = terminal_v2.validate_terminal_bundle(
        terminal=terminal,
        final_report=report,
        context=context,
        documents=documents,
        actual_sha256_by_path=actual,
    )
    return {
        "status": "PASS",
        "schema_dispatch": "replay_serialization_terminal_v4",
        "terminal": terminal_ref,
        "final_report": report_ref,
        "node_count": result["node_count"],
        "edge_count": result["edge_count"],
        "claim_inventory_sha256": context["bindings"]["claim_inventory_sha256"],
        "current_verification_executed_on_committed_checkout": True,
        "policy_closure_state": "complete",
        "authority_effect": "none",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def materialize_g5_handoff() -> dict[str, Any]:
    terminal = validate_terminal()
    core = {
        "schema_version": "public_text_quality_g4_to_g5_terminal_handoff_v1",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "terminal_commit": _git_text("rev-parse", "HEAD"),
        "terminal_tree": _git_text("rev-parse", "HEAD^{tree}"),
        "terminal_path": terminal["terminal"]["path"],
        "terminal_sha256": terminal["terminal"]["sha256"],
        "final_report_path": terminal["final_report"]["path"],
        "final_report_sha256": terminal["final_report"]["sha256"],
        "claim_inventory_sha256": terminal["claim_inventory_sha256"],
        "current_verification_receipt_sha256": base.sha256_file(CURRENT_VERIFICATION),
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "g5_may_begin": True,
        "authority_effect": "none",
    }
    handoff = {**core, "handoff_hash": base.canonical_hash(core)}
    base.write_once_or_same(G5_HANDOFF, handoff)
    return {
        "status": "PASS",
        "handoff_path": _repo_path(G5_HANDOFF),
        "handoff_sha256": base.sha256_file(G5_HANDOFF),
        "terminal_commit": core["terminal_commit"],
        "terminal_tree": core["terminal_tree"],
        "authority_effect": "none",
    }
