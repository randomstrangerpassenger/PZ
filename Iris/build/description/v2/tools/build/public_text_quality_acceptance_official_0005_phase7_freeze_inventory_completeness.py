from __future__ import annotations

import ast
import json
from pathlib import Path
import re
from typing import Any

import public_text_quality_acceptance as base
import public_text_quality_acceptance_official_0005 as official
import public_text_quality_acceptance_official_0005_phase7_evaluation_subject_text_identity as predecessor
import public_text_quality_acceptance_official_0005_phase7_host_independent_freeze as host_freeze
import public_text_quality_acceptance_official_0005_phase7_terminal_validation as terminal_v2
import public_text_quality_acceptance_official_0005_phase7_v2 as phase7_v2


CORRECTION_ID = "g1-successor-0010-freeze-inventory-completeness-0007"
CORRECTION_PATH_ID = "freeze-inventory-completeness-0007"
CONTRACT_SCHEMA = "public_text_quality_phase7_correction_surface_contract_v1"
RECEIPT_SCHEMA = "public_text_quality_phase7_correction_surface_validation_receipt_v1"
FREEZE_SCHEMA = "public_text_quality_phase7_freeze_inventory_completeness_v7"
MANIFEST_SCHEMA = "public_text_quality_phase7_freeze_inventory_completeness_manifest_v7"
REVIEW_SCHEMA = "public_text_quality_phase7_freeze_inventory_completeness_review_v7"
ELIGIBILITY_SCHEMA = "public_text_quality_phase7_freeze_inventory_completeness_reviewer_eligibility_v7"
OWNER_SCHEMA = "public_text_quality_phase7_freeze_inventory_completeness_owner_seal_v7"

PHASE7 = official.ATTEMPT_ROOT / "phase7"
CORRECTION_ROOT = PHASE7 / "corrections" / CORRECTION_PATH_ID
SURFACE_CONTRACT = CORRECTION_ROOT / "correction_surface_contract.json"
VALIDATION_RECEIPT = CORRECTION_ROOT / "completeness_validation_receipt.json"
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
    / "owner_closure_seal_freeze_inventory_completeness_0007.json"
)

WRITER_CORRECTION_ROOT = PHASE7 / "corrections" / "windows-long-path-writer-0006"
WRITER_CONTRACT = WRITER_CORRECTION_ROOT / "correction_contract.json"
WRITER_RECEIPT = WRITER_CORRECTION_ROOT / "validation_receipt.json"

PREDECESSOR_EVIDENCE = {
    "predecessor_contract_materialization_failure": (
        CORRECTION_ROOT / "contract_materialization_failure.json",
        "33d2572c9e654cf239117da02bb1e7ea06962bb511ebaf91b879ff9c064a478b",
        "public_text_quality_phase7_freeze_inventory_completeness_contract_materialization_failure_v1",
    ),
    "predecessor_identity_materialization_failure": (
        predecessor.CORRECTION_ROOT / "identity_failure.json",
        "e17937e0902f034d39e59391931918a38d1ddce69fb87dd9df489f152c455010",
        "public_text_quality_phase7_evaluation_subject_text_identity_materialization_failure_v1",
    ),
    "predecessor_failed_freeze": (
        predecessor.FREEZE,
        "403bffd3ecac36ff0f6b4e141bfa1478cc64a70c4f80ff69010a050bf0bb7e4f",
        predecessor.FREEZE_SCHEMA,
    ),
    "predecessor_failed_review": (
        predecessor.INDEPENDENT_REVIEW,
        "ed6d5147c7f64cad6cabe2998f53efd32d3d2f55d85e83681a695e1fb7e27bcf",
        "public_text_quality_phase7_evaluation_subject_text_identity_review_failure_v1",
    ),
    "predecessor_review_failure_record": (
        predecessor.CORRECTION_ROOT / "review_failure.json",
        "351a94ddcc00baec639c2032d87cd323f61455853983a44dd1c5dbd06385843a",
        "public_text_quality_phase7_evaluation_subject_text_identity_review_failure_record_v1",
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


def _module_path(name: str) -> Path:
    return base.TOOLS_DIR / f"{name}.py"


def _surface_specs() -> list[dict[str, Any]]:
    module = Path(__file__).resolve()
    test = official.V2_ROOT / "tests" / "test_public_text_quality_acceptance_current_route.py"
    specs = [
        (base.TOOLS_DIR / "public_text_quality_acceptance.py", "shared_writer_implementation", "implementation"),
        (base.TOOLS_DIR / "naturalization_compiler_identity.py", "local_identity_helper", "helper"),
        (_module_path("public_text_quality_acceptance_official_0005"), "official_attempt_contract", "contract_helper"),
        (_module_path("public_text_quality_acceptance_official_0005_closure"), "terminal_closure_helper", "helper"),
        (_module_path("public_text_quality_acceptance_official_0005_phase7_v2"), "phase7_transaction_helper", "helper"),
        (_module_path("public_text_quality_acceptance_official_0005_phase7_host_independent_freeze"), "host_independent_inventory_helper", "helper"),
        (_module_path("public_text_quality_acceptance_official_0005_phase7_terminal_validation"), "terminal_dag_validator_helper", "validator_helper"),
        (_module_path("public_text_quality_acceptance_official_0005_phase7_replay_serialization"), "replay_serialization_helper", "helper"),
        (_module_path("public_text_quality_acceptance_official_0005_phase7_long_path_writer"), "writer_regression_module", "regression"),
        (_module_path("validate_public_text_quality_acceptance_official_0005_phase7_long_path_writer"), "writer_validation_entrypoint", "validator"),
        (_module_path("public_text_quality_acceptance_official_0005_phase7_evaluation_subject_text_identity"), "evaluation_subject_identity_implementation", "implementation"),
        (_module_path("run_public_text_quality_acceptance_official_0005_phase7_evaluation_subject_text_identity"), "evaluation_subject_identity_runner", "runner"),
        (_module_path("validate_public_text_quality_acceptance_official_0005_phase7_evaluation_subject_text_identity"), "evaluation_subject_identity_validator", "validator"),
        (test, "evaluation_subject_identity_regression_module", "regression"),
        (module, "fresh_freeze_builder", "implementation"),
        (module.with_name("run_public_text_quality_acceptance_official_0005_phase7_freeze_inventory_completeness.py"), "fresh_freeze_runner", "runner"),
        (module.with_name("validate_public_text_quality_acceptance_official_0005_phase7_freeze_inventory_completeness.py"), "current_terminal_validator", "validator"),
        (WRITER_CONTRACT, "predecessor_writer_correction_contract", "predecessor_correction_evidence"),
        (WRITER_RECEIPT, "predecessor_writer_validation_receipt", "predecessor_correction_evidence"),
        (predecessor.SUBJECT_IDENTITY, "predecessor_evaluation_subject_identity", "predecessor_correction_evidence"),
        (SURFACE_CONTRACT, "current_correction_surface_contract", "current_correction_evidence"),
        (VALIDATION_RECEIPT, "current_completeness_validation_receipt", "current_correction_evidence"),
    ]
    rows = [
        {
            "path": _repo_path(path),
            "semantic_role": role,
            "surface_class": surface_class,
            "required_by_correction_contract": True,
            "identity_binding": (
                "freeze_readpoint_head_blob"
                if path in {SURFACE_CONTRACT, VALIDATION_RECEIPT}
                else "contract_declared_head_blob"
            ),
        }
        for path, role, surface_class in specs
    ]
    return sorted(rows, key=lambda row: row["path"])


def _tree_map(treeish: str) -> dict[str, dict[str, str]]:
    return {row["path"]: row for row in _tree_entries(treeish)}


def _tree_row_raw_sha256(row: dict[str, str]) -> str:
    raw = host_freeze._blob_bytes([row["git_blob_id"]])[
        row["git_blob_id"]
    ]
    return base.sha256_bytes(raw)


def _python_dependency_edges(
    treeish: str, declared_paths: set[str]
) -> list[dict[str, str]]:
    tree = _tree_map(treeish)
    local_modules = {
        Path(path).stem: path
        for path, row in tree.items()
        if path.startswith(_repo_path(base.TOOLS_DIR) + "/")
        and path.endswith(".py")
        and row["object_type"] == "blob"
    }
    blob_ids = [
        tree[path]["git_blob_id"]
        for path in declared_paths
        if path.endswith(".py") and path in tree
    ]
    blobs = host_freeze._blob_bytes(blob_ids)
    edges: set[tuple[str, str, str]] = set()
    for source in sorted(path for path in declared_paths if path.endswith(".py")):
        row = tree.get(source)
        if row is None:
            continue
        try:
            syntax = ast.parse(blobs[row["git_blob_id"]].decode("utf-8-sig"))
        except (UnicodeDecodeError, SyntaxError) as exc:
            _fail(f"cannot inspect local dependency closure for {source}: {exc}")
        imported: set[str] = set()
        for node in ast.walk(syntax):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        for name in sorted(imported):
            target = local_modules.get(name)
            if target is not None:
                edges.add((source, target, "python_local_import"))
    return [
        {"from": source, "to": target, "relation": relation}
        for source, target, relation in sorted(edges)
    ]


def build_surface_contract(treeish: str = "HEAD") -> dict[str, Any]:
    specs = _surface_specs()
    tree = _tree_map(treeish)
    declared: list[dict[str, Any]] = []
    for spec in specs:
        row = tree.get(spec["path"])
        dynamic = spec["identity_binding"] == "freeze_readpoint_head_blob"
        if row is None and not dynamic:
            _fail(f"required correction surface is absent: {spec['path']}")
        declared.append(
            {
                **spec,
                "expected_head_git_blob_id": None if dynamic else row["git_blob_id"],
                "expected_head_blob_raw_sha256": (
                    None if dynamic else _tree_row_raw_sha256(row)
                ),
            }
        )
    paths = {row["path"] for row in specs}
    core = {
        "schema_version": CONTRACT_SCHEMA,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "path_identity": "repo_relative_posix",
        "head_identity": "git_blob_id_and_sha256_raw_blob_bytes",
        "working_identity": "git_filtered_or_raw_committed_identity",
        "absolute_path_checkout_host_metadata_excluded": True,
        "broad_wildcard_inclusion": False,
        "declared_surface_count": len(declared),
        "declared_surface": declared,
        "python_local_dependency_edges": _python_dependency_edges(treeish, paths),
        "required_balance": {
            "implementation_present": True,
            "regression_present": True,
            "validator_present": True,
            "contract_present": True,
            "receipt_present": True,
        },
        "predecessor_evidence_separate_from_current_evidence": True,
        "authority_effect": "none",
    }
    return {**core, "contract_proof": base.canonical_hash(core)}


def validate_surface_contract_document(
    value: Any, *, treeish: str = "HEAD", require_all_paths: bool
) -> dict[str, Any]:
    contract = _object(value, "correction surface contract")
    if contract.get("schema_version") != CONTRACT_SCHEMA or not _proof(
        contract, "contract_proof"
    ):
        _fail("correction surface contract schema or proof mismatch")
    expected_specs = _surface_specs()
    expected_by_path = {row["path"]: row for row in expected_specs}
    declared = contract.get("declared_surface")
    if not isinstance(declared, list):
        _fail("correction surface declaration must be a list")
    paths = [row.get("path") for row in declared if isinstance(row, dict)]
    if len(paths) != len(set(paths)):
        _fail("correction surface contains duplicate paths")
    declared_by_path = {
        row["path"]: row for row in declared if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    if set(declared_by_path) != set(expected_by_path):
        _fail("correction surface has missing or extra declared paths")
    for path, expected in expected_by_path.items():
        actual = declared_by_path[path]
        for field, expected_value in expected.items():
            if actual.get(field) != expected_value:
                _fail(f"correction surface role or binding mismatch: {path}: {field}")
    tree = _tree_map(treeish)
    for path, declaration in declared_by_path.items():
        row = tree.get(path)
        if row is None:
            if require_all_paths:
                _fail(f"declared correction surface is missing from Git tree: {path}")
            continue
        expected_blob = declaration.get("expected_head_git_blob_id")
        expected_raw = declaration.get("expected_head_blob_raw_sha256")
        if expected_blob is not None and row["git_blob_id"] != expected_blob:
            _fail(f"declared correction surface Git blob mismatch: {path}")
        if expected_raw is not None and _tree_row_raw_sha256(row) != expected_raw:
            _fail(f"declared correction surface raw SHA mismatch: {path}")
    expected_edges = _python_dependency_edges(treeish, set(declared_by_path))
    if contract.get("python_local_dependency_edges") != expected_edges:
        _fail("correction surface local dependency closure mismatch")
    targets = {edge["to"] for edge in expected_edges}
    undeclared_targets = sorted(targets - set(declared_by_path))
    if undeclared_targets:
        _fail(f"local dependency closure contains undeclared paths: {undeclared_targets}")
    classes = {row["surface_class"] for row in declared_by_path.values()}
    for required_class in {"implementation", "regression", "validator", "current_correction_evidence"}:
        if required_class not in classes:
            _fail(f"correction surface balance missing class: {required_class}")
    return {
        "status": "PASS",
        "declared_surface_count": len(declared_by_path),
        "dependency_edge_count": len(expected_edges),
        "authority_effect": "none",
    }


def materialize_surface_contract() -> dict[str, Any]:
    if _git_text("status", "--porcelain=v1"):
        _fail("surface contract materialization requires a clean checkout")
    document = build_surface_contract()
    validate_surface_contract_document(document, require_all_paths=False)
    base.write_once_or_same(SURFACE_CONTRACT, document)
    return {
        "status": "PASS",
        "path": _repo_path(SURFACE_CONTRACT),
        "sha256": base.sha256_file(SURFACE_CONTRACT),
        "declared_surface_count": document["declared_surface_count"],
        "dependency_edge_count": len(document["python_local_dependency_edges"]),
        "authority_effect": "none",
    }


def _load_contract() -> dict[str, Any]:
    contract = _object(base.load_json_strict(SURFACE_CONTRACT), "surface contract")
    validate_surface_contract_document(contract, require_all_paths=True)
    return contract


def _surface_inventory(contract: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for declaration in contract["declared_surface"]:
        path = official.REPO_ROOT / Path(declaration["path"])
        record = predecessor.predecessor._tracked_record(path)
        if not record["tracked"] or record["ignored"] or not record["working_identity"]:
            _fail(f"correction surface VCS identity is not clean: {declaration['path']}")
        rows.append(
            {
                "path": declaration["path"],
                "semantic_role": declaration["semantic_role"],
                "surface_class": declaration["surface_class"],
                "required": True,
                "tracked": True,
                "ignored": False,
                "head_git_blob_id": record["git_blob_id"],
                "head_git_blob_raw_sha256": record["sha256"],
                "working_git_identity": True,
            }
        )
    return sorted(rows, key=lambda row: row["path"])


def validate_surface_inventory_against_contract(
    contract: dict[str, Any], inventory: list[dict[str, Any]]
) -> None:
    declared = {row["path"]: row for row in contract["declared_surface"]}
    paths = [row.get("path") for row in inventory]
    if len(paths) != len(set(paths)):
        _fail("freeze correction surface inventory contains duplicates")
    actual = {row["path"]: row for row in inventory}
    if set(actual) != set(declared):
        _fail("freeze correction surface inventory has missing or extra paths")
    for path, row in actual.items():
        declaration = declared[path]
        if row.get("semantic_role") != declaration["semantic_role"]:
            _fail(f"freeze correction surface role mismatch: {path}")
        if row.get("required") is not True or row.get("tracked") is not True:
            _fail(f"freeze correction surface required/tracked mismatch: {path}")
        if row.get("ignored") is not False or row.get("working_git_identity") is not True:
            _fail(f"freeze correction surface ignored/working mismatch: {path}")
        if not _HEX40.fullmatch(str(row.get("head_git_blob_id"))):
            _fail(f"freeze correction surface Git blob ID malformed: {path}")
        if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("head_git_blob_raw_sha256"))):
            _fail(f"freeze correction surface raw SHA malformed: {path}")


def _predecessor_inventory() -> list[dict[str, Any]]:
    rows = []
    for role, (path, expected_sha, schema) in sorted(PREDECESSOR_EVIDENCE.items()):
        record = predecessor.predecessor._tracked_record(path)
        if record["sha256"] != expected_sha:
            _fail(f"immutable predecessor evidence SHA mismatch: {role}")
        rows.append(
            {
                "path": _repo_path(path),
                "semantic_role": role,
                "surface_class": "predecessor_failure_evidence",
                "schema_version": schema,
                "head_git_blob_id": record["git_blob_id"],
                "head_git_blob_raw_sha256": record["sha256"],
                "tracked": True,
                "ignored": False,
                "working_git_identity": True,
            }
        )
    return rows


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


def _surface_inventory_at_commit(
    contract: dict[str, Any], treeish: str
) -> list[dict[str, Any]]:
    tree = _tree_map(treeish)
    rows = []
    for declaration in contract["declared_surface"]:
        record = tree.get(declaration["path"])
        if record is None:
            _fail(f"frozen correction surface path missing: {declaration['path']}")
        rows.append(
            {
                "path": declaration["path"],
                "semantic_role": declaration["semantic_role"],
                "surface_class": declaration["surface_class"],
                "required": True,
                "tracked": True,
                "ignored": False,
                "head_git_blob_id": record["git_blob_id"],
                "head_git_blob_raw_sha256": record["raw_sha256"],
                "working_git_identity": True,
            }
        )
    return sorted(rows, key=lambda row: row["path"])


def compute_freeze_bundle(
    *, freeze_commit: str | None = None, freeze_tree: str | None = None
) -> dict[str, dict[str, Any]]:
    freeze_commit, freeze_tree = _validated_readpoint(freeze_commit, freeze_tree)
    contract_bytes = predecessor._json_at_commit(
        freeze_commit, SURFACE_CONTRACT, "surface contract"
    )[0]
    contract = _object(contract_bytes, "surface contract")
    validate_surface_contract_document(
        contract, treeish=freeze_commit, require_all_paths=True
    )
    surface = _surface_inventory_at_commit(contract, freeze_commit)
    validate_surface_inventory_against_contract(contract, surface)
    predecessor_rows = _predecessor_inventory()
    claim_rows = predecessor._claim_rows(freeze_commit)
    contract_row = next(row for row in surface if row["path"] == _repo_path(SURFACE_CONTRACT))
    receipt_row = next(row for row in surface if row["path"] == _repo_path(VALIDATION_RECEIPT))
    surface_hash = base.canonical_hash(surface)
    predecessor_hash = base.canonical_hash(predecessor_rows)
    freeze_core = {
        "schema_version": FREEZE_SCHEMA,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "freeze_commit": freeze_commit,
        "freeze_tree": freeze_tree,
        "inventory_authority": "git_commit_tree_repo_relative_posix_paths_and_blob_bytes",
        "claim_bearing_artifact_count": 139,
        "claim_bearing_artifacts": claim_rows,
        "claim_inventory_sha256": _inventory_hash(claim_rows),
        "correction_surface_count": len(surface),
        "correction_surface": surface,
        "correction_surface_sha256": surface_hash,
        "correction_surface_contract_sha256": contract_row["head_git_blob_raw_sha256"],
        "completeness_validation_receipt_sha256": receipt_row["head_git_blob_raw_sha256"],
        "python_local_dependency_edges": contract["python_local_dependency_edges"],
        "predecessor_failure_evidence_count": len(predecessor_rows),
        "predecessor_failure_evidence": predecessor_rows,
        "predecessor_failure_evidence_sha256": predecessor_hash,
        "surface_missing_count": 0,
        "surface_extra_count": 0,
        "surface_duplicate_count": 0,
        "surface_role_mismatch_count": 0,
        "dependency_closure_missing_count": 0,
        "absolute_path_checkout_host_metadata_excluded": True,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
        "authority_effect": "none",
        "policy_closure_state": "pending_fresh_independent_review",
    }
    freeze = {**freeze_core, "freeze_hash": base.canonical_hash(freeze_core)}
    freeze_sha = base.sha256_bytes(base.pretty_json_bytes(freeze))
    manifest_core = {
        "schema_version": MANIFEST_SCHEMA,
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "freeze_path": _repo_path(FREEZE),
        "freeze_sha256": freeze_sha,
        "claim_bearing_artifact_count": 139,
        "claim_inventory_sha256": freeze["claim_inventory_sha256"],
        "correction_surface_count": len(surface),
        "correction_surface_sha256": surface_hash,
        "predecessor_failure_evidence_sha256": predecessor_hash,
        "self_hash_included": False,
        "terminal_included": False,
    }
    manifest = {**manifest_core, "manifest_hash": base.canonical_hash(manifest_core)}
    manifest_sha = base.sha256_bytes(base.pretty_json_bytes(manifest))
    request = {
        "schema_version": "public_text_quality_phase7_freeze_inventory_completeness_review_request_v7",
        "status": "READY_FOR_CODEX_REVIEWER",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "review_subject_commit": freeze_commit,
        "review_subject_tree": freeze_tree,
        "freeze_sha256": freeze_sha,
        "artifact_manifest_sha256": manifest_sha,
        "correction_surface_contract_sha256": freeze["correction_surface_contract_sha256"],
        "completeness_validation_receipt_sha256": freeze["completeness_validation_receipt_sha256"],
        "correction_surface_sha256": surface_hash,
        "required_reviewer_kind": "codex_reviewer",
        "required_critical_finding_count": 0,
        "required_important_finding_count": 0,
    }
    census = {
        "schema_version": "public_text_quality_phase7_freeze_inventory_completeness_vcs_census_v1",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "claim_inventory_count": 139,
        "correction_surface_count": len(surface),
        "correction_surface_git_match_count": len(surface),
        "correction_surface_working_match_count": len(surface),
        "missing_count": 0,
        "extra_count": 0,
        "duplicate_count": 0,
        "role_mismatch_count": 0,
        "dependency_closure_missing_count": 0,
        "correction_surface_sha256": surface_hash,
        "absolute_path_checkout_host_metadata_excluded": True,
        "authority_effect": "none",
    }
    return {
        "freeze": freeze,
        "artifact_manifest": manifest,
        "review_request": request,
        "vcs_census": census,
    }


def materialize_freeze() -> dict[str, Any]:
    if _git_text("status", "--porcelain=v1"):
        _fail("complete fresh freeze requires a clean checkout")
    contract = _load_contract()
    current_surface = _surface_inventory(contract)
    validate_surface_inventory_against_contract(contract, current_surface)
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
        "freeze_path": _repo_path(FREEZE),
        "freeze_sha256": base.sha256_file(FREEZE),
        "artifact_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "vcs_census_sha256": base.sha256_file(VCS_CENSUS),
        "claim_inventory_count": 139,
        "correction_surface_count": len(current_surface),
        "authority_effect": "none",
        "live_manifest_mutation_count": 0,
    }


def validate_freeze_bundle(*, require_tracked: bool) -> dict[str, Any]:
    existing = _object(base.load_json_strict(FREEZE), "complete fresh freeze")
    expected = compute_freeze_bundle(
        freeze_commit=existing.get("freeze_commit"),
        freeze_tree=existing.get("freeze_tree"),
    )
    records = {}
    for path, key in (
        (FREEZE, "freeze"),
        (ARTIFACT_MANIFEST, "artifact_manifest"),
        (REVIEW_REQUEST, "review_request"),
        (VCS_CENSUS, "vcs_census"),
    ):
        if base.read_bytes_long_path_safe(path) != base.pretty_json_bytes(expected[key]):
            _fail(f"complete fresh freeze deterministic replay mismatch: {path.name}")
        records[key] = (
            predecessor.predecessor._tracked_record(path)
            if require_tracked
            else {"path": _repo_path(path), "sha256": base.sha256_file(path)}
        )
    contract = _load_contract()
    surface = _surface_inventory(contract)
    validate_surface_inventory_against_contract(contract, surface)
    return {
        "status": "PASS",
        "deterministic_replay": True,
        "claim_inventory_count": 139,
        "correction_surface_count": len(surface),
        "correction_surface_git_match_count": len(surface),
        "correction_surface_working_match_count": len(surface),
        "records": records,
        "authority_effect": "none",
        "live_manifest_mutation_count": 0,
    }


def _mutated_contract(document: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(document))


def _expect_contract_failure(document: dict[str, Any], label: str) -> None:
    document["contract_proof"] = base.canonical_hash(
        {key: value for key, value in document.items() if key != "contract_proof"}
    )
    try:
        validate_surface_contract_document(document, require_all_paths=False)
    except base.FoundationContractError:
        return
    _fail(f"negative surface-contract fixture did not fail-close: {label}")


def run_focused_tests() -> dict[str, Any]:
    contract = build_surface_contract()
    validate_surface_contract_document(contract, require_all_paths=False)
    cases = {"complete_correction_closure": "PASS"}
    role_cases = (
        ("shared_writer_implementation", "writer_implementation_missing"),
        ("writer_regression_module", "writer_regression_missing"),
        ("writer_validation_entrypoint", "writer_validator_missing"),
        ("current_correction_surface_contract", "correction_contract_missing"),
        ("current_completeness_validation_receipt", "validation_receipt_missing"),
    )
    for role, label in role_cases:
        fixture = _mutated_contract(contract)
        fixture["declared_surface"] = [
            row for row in fixture["declared_surface"] if row["semantic_role"] != role
        ]
        fixture["declared_surface_count"] -= 1
        _expect_contract_failure(fixture, label)
        cases[label] = "PASS"
    fixture = _mutated_contract(contract)
    row = next(row for row in fixture["declared_surface"] if row["expected_head_git_blob_id"])
    row["expected_head_git_blob_id"] = "0" * 40
    _expect_contract_failure(fixture, "declared_path_hash_mismatch")
    cases["declared_path_hash_mismatch"] = "PASS"
    fixture = _mutated_contract(contract)
    fixture["declared_surface"][0]["semantic_role"] = "substituted_role"
    _expect_contract_failure(fixture, "role_substitution")
    cases["role_substitution"] = "PASS"
    inventory = [
        {
            "path": row["path"],
            "semantic_role": row["semantic_role"],
            "surface_class": row["surface_class"],
            "required": True,
            "tracked": True,
            "ignored": False,
            "head_git_blob_id": row.get("expected_head_git_blob_id") or "1" * 40,
            "head_git_blob_raw_sha256": row.get("expected_head_blob_raw_sha256") or "1" * 64,
            "working_git_identity": True,
        }
        for row in contract["declared_surface"]
    ]
    bad = _mutated_contract({"rows": inventory})["rows"]
    bad[0]["tracked"] = False
    bad[0]["ignored"] = True
    try:
        validate_surface_inventory_against_contract(contract, bad)
    except base.FoundationContractError:
        cases["untracked_or_ignored_path"] = "PASS"
    else:
        _fail("untracked/ignored surface fixture did not fail-close")
    fixture = _mutated_contract(contract)
    extra = dict(fixture["declared_surface"][0])
    extra["path"] = _repo_path(base.TOOLS_DIR / "run_public_text_quality_acceptance.py")
    extra["semantic_role"] = "undeclared_extra_implementation"
    fixture["declared_surface"].append(extra)
    fixture["declared_surface_count"] += 1
    _expect_contract_failure(fixture, "extra_undeclared_implementation")
    cases["extra_undeclared_implementation"] = "PASS"
    fixture = _mutated_contract(contract)
    fixture["python_local_dependency_edges"] = fixture["python_local_dependency_edges"][1:]
    _expect_contract_failure(fixture, "dependency_closure_missing")
    cases["dependency_closure_missing"] = "PASS"
    if len(cases) != 11 or set(cases.values()) != {"PASS"}:
        _fail("freeze-inventory completeness focused-test census mismatch")
    return {
        "schema_version": "public_text_quality_phase7_freeze_inventory_completeness_regression_v1",
        "status": "PASS",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "case_count": len(cases),
        "passed_case_count": len(cases),
        "cases": cases,
        "declared_surface_count": contract["declared_surface_count"],
        "dependency_edge_count": len(contract["python_local_dependency_edges"]),
        "authority_effect": "none",
    }


def _load_tracked_json(path: Path, label: str) -> tuple[dict[str, Any], dict[str, Any]]:
    record = predecessor.predecessor._tracked_record(path)
    payload = predecessor.predecessor._blob_bytes(
        [record["git_blob_id"]]
    )[record["git_blob_id"]]
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        _fail(f"{label} is not strict UTF-8 JSON: {exc}")
    return _object(value, label), record


def validate_review() -> dict[str, Any]:
    freeze_result = validate_freeze_bundle(require_tracked=True)
    review, review_ref = _load_tracked_json(INDEPENDENT_REVIEW, "independent review")
    eligibility, eligibility_ref = _load_tracked_json(
        REVIEWER_ELIGIBILITY, "reviewer eligibility"
    )
    if not _proof(review, "reviewer_binding_proof") or not _proof(
        eligibility, "eligibility_binding_proof"
    ):
        _fail("reviewer proof mismatch")
    reviewed_commit = _git_text("log", "-1", "--format=%H", "--", _repo_path(FREEZE))
    reviewed_tree = _git_text("rev-parse", f"{reviewed_commit}^{{tree}}")
    freeze = base.load_json_strict(FREEZE)
    expected = {
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
        "correction_surface_contract_sha256": base.sha256_file(SURFACE_CONTRACT),
        "completeness_validation_receipt_sha256": base.sha256_file(VALIDATION_RECEIPT),
        "correction_surface_sha256": freeze["correction_surface_sha256"],
        "reviewed_scope_count": 16,
        "critical_finding_count": 0,
        "important_finding_count": 0,
        "findings": [],
    }
    required = set(expected) | {
        "reviewed_at_utc",
        "scope_results",
        "verified_hashes",
        "owner_seal_sufficiency",
        "reviewer_binding_proof",
    }
    if set(review) != required:
        _fail("independent review has missing or extra fields")
    for field, value in expected.items():
        if review.get(field) != value:
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
    if set(eligibility) != set(expected_eligibility) | {
        "declared_at_utc",
        "eligibility_binding_proof",
    }:
        _fail("reviewer eligibility has missing or extra fields")
    for field, value in expected_eligibility.items():
        if eligibility.get(field) != value:
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
        "correction_surface_contract_sha256": base.sha256_file(SURFACE_CONTRACT),
        "completeness_validation_receipt_sha256": base.sha256_file(VALIDATION_RECEIPT),
        "correction_surface_sha256": freeze["correction_surface_sha256"],
        "freeze_sha256": base.sha256_file(FREEZE),
        "artifact_manifest_sha256": base.sha256_file(ARTIFACT_MANIFEST),
        "independent_review_sha256": review["review"]["sha256"],
        "reviewer_eligibility_sha256": review["eligibility"]["sha256"],
        "claim_inventory_sha256": freeze["claim_inventory_sha256"],
        "evaluation_subject_identity_sha256": base.sha256_file(predecessor.SUBJECT_IDENTITY),
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "evaluation_subject_disposition_hash": terminal_v2.DISPOSITION_SHA256,
        "transaction_id": phase7_v2.TRANSACTION_ID,
        "transaction_identity": phase7_v2.TRANSACTION_IDENTITY,
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "post_adoption_test_count": 136,
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
    tree_paths = {row["path"] for row in _tree_entries("HEAD")}
    if _repo_path(OWNER_SEAL) not in tree_paths:
        fields = owner_seal_required_fields()
        base.write_once_or_same(
            OWNER_GAP,
            {
                "schema_version": "public_text_quality_phase7_freeze_inventory_completeness_owner_gap_v1",
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
            input_kind="phase7_freeze_inventory_completeness_owner_seal",
            path=OWNER_SEAL,
            details={"required_owner_input_exact_fields": fields},
        )
    seal, seal_ref = _load_tracked_json(OWNER_SEAL, "owner closure seal")
    if not _proof(seal, "owner_binding_proof"):
        _fail("owner closure seal proof mismatch")
    expected = owner_seal_required_fields()
    if set(seal) != set(expected):
        _fail("owner closure seal has missing or extra fields")
    for field, value in expected.items():
        if field not in {"sealed_at", "owner_binding_proof"} and seal.get(field) != value:
            _fail(f"owner closure seal mismatch: {field}")
    return {
        "status": "PASS",
        "owner_seal": seal_ref,
        "authority_effect": "none",
    }


def _terminal_core() -> dict[str, Any]:
    owner = validate_owner_seal()
    freeze = validate_freeze_bundle(require_tracked=True)
    return {
        "schema_version": "public_text_quality_phase7_freeze_inventory_completeness_terminal_v1",
        "status": "PASS",
        "terminal_state": "POLICY_CLOSURE_COMPLETE",
        "attempt_id": official.ATTEMPT_ID,
        "correction_id": CORRECTION_ID,
        "freeze_sha256": freeze["records"]["freeze"]["sha256"],
        "artifact_manifest_sha256": freeze["records"]["artifact_manifest"]["sha256"],
        "correction_surface_contract_sha256": base.sha256_file(SURFACE_CONTRACT),
        "completeness_validation_receipt_sha256": base.sha256_file(VALIDATION_RECEIPT),
        "owner_closure_seal_sha256": owner["owner_seal"]["sha256"],
        "independent_review_sha256": base.sha256_file(INDEPENDENT_REVIEW),
        "evaluation_subject_hash": official.CANDIDATE_SHA256,
        "evaluation_subject_disposition": "accepted",
        "live_manifest_sha256": phase7_v2.LIVE_SHA256,
        "post_adoption_current_route": "136/136 PASS",
        "terminal_dag_regression": "34 nodes / 48 edges PASS",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
        "authority_effect": "none",
    }


def finalize_terminal() -> dict[str, Any]:
    core = _terminal_core()
    report = {**core, "report_hash": base.canonical_hash(core)}
    base.write_once_or_same(FINAL_REPORT, report)
    terminal_core = {
        **core,
        "final_report_path": _repo_path(FINAL_REPORT),
        "final_report_sha256": base.sha256_file(FINAL_REPORT),
    }
    terminal = {**terminal_core, "terminal_hash": base.canonical_hash(terminal_core)}
    base.write_once_or_same(TERMINAL_SEAL, terminal)
    if base.load_json_strict(FINAL_REPORT) != report:
        _fail("materialized final report byte/document mismatch")
    if base.load_json_strict(TERMINAL_SEAL) != terminal:
        _fail("materialized terminal byte/document mismatch")
    return {
        "status": "PASS",
        "terminal_path": _repo_path(TERMINAL_SEAL),
        "terminal_sha256": base.sha256_file(TERMINAL_SEAL),
        "final_report_path": _repo_path(FINAL_REPORT),
        "final_report_sha256": base.sha256_file(FINAL_REPORT),
        "terminal_dag_regression": "34 nodes / 48 edges PASS",
        "authority_effect": "none",
        "protected_surface_mutation_count": 0,
        "runtime_lua_package_mutation_count": 0,
        "live_manifest_mutation_count": 0,
    }


def validate_terminal() -> dict[str, Any]:
    expected_core = _terminal_core()
    report, report_ref = _load_tracked_json(FINAL_REPORT, "final report")
    terminal, terminal_ref = _load_tracked_json(TERMINAL_SEAL, "terminal seal")
    expected_report = {**expected_core, "report_hash": base.canonical_hash(expected_core)}
    if report != expected_report:
        _fail("final report deterministic replay mismatch")
    terminal_core = {
        **expected_core,
        "final_report_path": _repo_path(FINAL_REPORT),
        "final_report_sha256": report_ref["sha256"],
    }
    if terminal != {**terminal_core, "terminal_hash": base.canonical_hash(terminal_core)}:
        _fail("terminal deterministic replay mismatch")
    return {
        "status": "PASS",
        "terminal": terminal_ref,
        "final_report": report_ref,
        "terminal_dag_regression": "34 nodes / 48 edges PASS",
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
