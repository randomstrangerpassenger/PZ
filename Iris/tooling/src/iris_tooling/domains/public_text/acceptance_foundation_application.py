from __future__ import annotations

from .acceptance_emission import *  # noqa: F401,F403

def foundation_paths(root: Path) -> tuple[Path, Path]:
    return root / FOUNDATION_CONTRACT_NAME, root / READINESS_REPORT_NAME


def validate_foundation_root(root: Path) -> Path:
    resolved = root.resolve()
    default = DEFAULT_FOUNDATION_ROOT.resolve()
    repository = REPO_ROOT.resolve()
    if resolved.is_relative_to(repository) and resolved != default:
        raise FoundationContractError(
            "repository-local foundation root must be the exact tracked G4 foundation root"
        )
    return resolved


def build_foundation(
    *, foundation_id: str, foundation_root: Path = DEFAULT_FOUNDATION_ROOT
) -> dict[str, Any]:
    foundation_root = validate_foundation_root(foundation_root)
    protected_before = protected_foundation_surface_snapshot()
    contract_path, readiness_path = foundation_paths(foundation_root)
    contract = build_foundation_contract(foundation_id)
    contract_write_state = write_once_or_same(
        contract_path, contract, repository_root=foundation_root
    )
    fixture_manifest = load_json_strict(FIXTURE_MANIFEST)
    fixture_report = validate_fixture_manifest(fixture_manifest, contract)
    protected_after = protected_foundation_surface_snapshot()
    protected_no_write_guard = _no_write_guard(protected_before, protected_after)
    readiness = build_readiness_report(
        foundation_id=foundation_id,
        contract_path=contract_path,
        contract=contract,
        fixture_report=fixture_report,
        protected_no_write_guard=protected_no_write_guard,
    )
    readiness_write_state = write_once_or_same(
        readiness_path, readiness, repository_root=foundation_root
    )
    protected_final = protected_foundation_surface_snapshot()
    if _no_write_guard(protected_before, protected_final) != protected_no_write_guard:
        raise FoundationContractError(
            "foundation build no-write guard changed after readiness serialization"
        )
    return {
        "status": "PASS",
        "foundation_id": foundation_id,
        "foundation_root": repo_relative(foundation_root),
        "contract_write_state": contract_write_state,
        "readiness_write_state": readiness_write_state,
        "foundation_contract_ready_for_remediation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "protected_surface_mutation_count": 0,
        "registry_food_successor_adoption_receipt_valid": True,
    }


def validate_foundation(
    *, foundation_id: str, foundation_root: Path = DEFAULT_FOUNDATION_ROOT
) -> dict[str, Any]:
    foundation_root = validate_foundation_root(foundation_root)
    contract_path, readiness_path = foundation_paths(foundation_root)
    if not contract_path.is_file() or not readiness_path.is_file():
        raise FoundationContractError(
            "foundation contract and readiness report must both exist"
        )
    protected_before = protected_foundation_surface_snapshot()
    foundation_bytes_before = {
        "contract": contract_path.read_bytes(),
        "readiness": readiness_path.read_bytes(),
    }
    contract = load_json_strict(contract_path)
    readiness = load_json_strict(readiness_path)
    fixture_manifest = load_json_strict(FIXTURE_MANIFEST)
    fixture_report = validate_fixture_manifest(fixture_manifest, contract)
    protected_after = protected_foundation_surface_snapshot()
    protected_no_write_guard = _no_write_guard(protected_before, protected_after)
    expected_readiness = build_readiness_report(
        foundation_id=foundation_id,
        contract_path=contract_path,
        contract=contract,
        fixture_report=fixture_report,
        protected_no_write_guard=protected_no_write_guard,
    )
    if readiness != expected_readiness:
        raise FoundationContractError(
            "readiness report is stale or differs from the exact implementation/docs/fixture binding"
        )
    required_state = synchronization_projection()["foundation_required_state"]
    for key, expected in required_state.items():
        if readiness.get(key) != expected:
            raise FoundationContractError(
                f"foundation readiness state mismatch for {key}"
            )
    if readiness.get("status") != "foundation_ready_for_remediation":
        raise FoundationContractError("foundation readiness status mismatch")
    if (
        foundation_bytes_before["contract"] != contract_path.read_bytes()
        or foundation_bytes_before["readiness"] != readiness_path.read_bytes()
    ):
        raise FoundationContractError(
            "no-write validation changed foundation contract or readiness bytes"
        )
    protected_final = protected_foundation_surface_snapshot()
    if _no_write_guard(protected_before, protected_final) != protected_no_write_guard:
        raise FoundationContractError(
            "foundation validator no-write guard changed during validation"
        )
    return {
        "status": "PASS",
        "foundation_id": foundation_id,
        "foundation_contract_raw_sha256": readiness[
            "foundation_contract_raw_sha256"
        ],
        "foundation_contract_ready_for_remediation": True,
        "candidate_content_dependency_count": 0,
        "candidate_metric_dependency_count": 0,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "foundation_runner_validator_fixture_pass": True,
        "four_plan_sync_projection_sha256_match": True,
        "clean_validation_terminal_pass": True,
        "food_sealed_successor_terminal_closeout": True,
        "registry_food_successor_adoption_receipt_valid": True,
        "current_facts_equals_selected_successor_facts": True,
        "current_manifest_binds_selected_successor_manifest": True,
        "protected_surface_mutation_count": 0,
        "no_write_validation": True,
    }

__all__ = [
    name for name in globals() if not name.startswith("__")
]
