from __future__ import annotations

from Iris.validation.test_workflow_consolidation.compare_contract_parity import compare


def test_contract_parity_preserves_probe_status() -> None:
    report = {"deterministic_core": {"probe_results": [{"probe_id": "probe", "status": "PASS"}]}}
    matrix = [{"predecessor_test_id": "old", "successor_probe_id": "probe"}]
    assert compare(matrix, report, report)["status"] == "PASS"
