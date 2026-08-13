from __future__ import annotations

from Iris.validation.test_workflow_consolidation.validate_identity_transaction import validate_transactions


def test_no_identity_change_transaction_is_complete() -> None:
    families = [{"family_id": "pilot", "disposition": "adopted"}]
    transactions = [
        {
            "family_id": "pilot",
            "changed_authority_axes": [],
            "atomic_members": ["implementation", "contract_mapping"],
            "predecessor_mapping_preserved": True,
        }
    ]
    assert validate_transactions(families, transactions)["status"] == "PASS"


def test_partial_authority_transaction_fails() -> None:
    families = [{"family_id": "family", "disposition": "adopted"}]
    transactions = [
        {
            "family_id": "family",
            "changed_authority_axes": ["taxonomy"],
            "atomic_members": ["implementation"],
            "predecessor_mapping_preserved": True,
        }
    ]
    assert validate_transactions(families, transactions)["status"] == "FAIL"
