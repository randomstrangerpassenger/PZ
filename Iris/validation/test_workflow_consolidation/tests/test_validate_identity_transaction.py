from __future__ import annotations

from Iris.validation.test_workflow_consolidation.validate_identity_transaction import validate_transactions


def _observation(*changed_axes: str) -> dict[str, object]:
    axes = {
        "source_classification",
        "denominator",
        "taxonomy",
        "required_validation",
        "evidence_mapping",
    }
    return {
        "changed_axes": list(changed_axes),
        "artifact_identities": {
            axis: {
                "path": f"{axis}.json",
                "base_git_blob_id": "before",
                "terminal_git_blob_id": "after" if axis in changed_axes else "before",
            }
            for axis in axes
        },
    }


def test_no_identity_change_transaction_is_complete() -> None:
    families = [
        {"family_id": "pilot", "disposition": "adopted", "authority_bound": False}
    ]
    transactions = [
        {
            "family_id": "pilot",
            "changed_authority_axes": [],
            "atomic_members": ["implementation", "contract_mapping"],
            "implementation_paths": ["test_pilot.py"],
            "predecessor_mapping_preserved": True,
            "schema_version": "iris_test_workflow_identity_transaction_v1",
            "status": "PASS",
            "transaction_kind": "identity_preserving",
        }
    ]
    assert validate_transactions(families, transactions, _observation())["status"] == "PASS"


def test_partial_authority_transaction_fails() -> None:
    families = [
        {"family_id": "family", "disposition": "adopted", "authority_bound": True}
    ]
    transactions = [
        {
            "family_id": "family",
            "changed_authority_axes": ["taxonomy"],
            "atomic_members": ["implementation"],
            "implementation_paths": ["test_family.py"],
            "predecessor_mapping_preserved": True,
            "schema_version": "iris_test_workflow_identity_transaction_v1",
            "status": "PASS",
            "transaction_kind": "authority_bound_migration",
        }
    ]
    assert validate_transactions(families, transactions, _observation("taxonomy"))["status"] == "FAIL"


def test_observed_authority_change_requires_first_real_migration_receipt() -> None:
    families = [
        {"family_id": "family", "disposition": "adopted", "authority_bound": True}
    ]
    transactions = [
        {
            "family_id": "family",
            "changed_authority_axes": ["taxonomy"],
            "atomic_members": ["implementation", "contract_mapping", "taxonomy"],
            "implementation_paths": ["test_family.py"],
            "predecessor_mapping_preserved": True,
            "schema_version": "iris_test_workflow_identity_transaction_v1",
            "status": "PASS",
            "transaction_kind": "authority_bound_migration",
        }
    ]
    report = validate_transactions(
        families, transactions, _observation("taxonomy")
    )
    assert report["status"] == "FAIL"
    assert report["first_real_authority_bound_migration"] == "FAIL"
