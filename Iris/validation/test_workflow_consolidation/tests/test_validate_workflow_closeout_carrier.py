from __future__ import annotations

from Iris.validation.test_workflow_consolidation.validate_workflow_closeout_carrier import validate_carrier


def test_pointer_self_reference_is_rejected(monkeypatch, tmp_path) -> None:
    responses = {
        ("rev-parse", "HEAD"): "carrier",
        ("rev-list", "--parents", "-n", "1", "carrier"): "carrier terminal",
        ("diff", "--name-only", "terminal", "carrier"): "Iris/_docs/refactor/test_workflow_consolidation/terminal_evidence_pointer.json",
    }
    monkeypatch.setattr(
        "Iris.validation.test_workflow_consolidation.validate_workflow_closeout_carrier.git",
        lambda _repo, *args: responses[args],
    )
    report = validate_carrier(
        tmp_path,
        "terminal",
        {"schema_version": "iris_test_workflow_terminal_evidence_pointer_v1", "carrier_commit": "carrier"},
        {"schema_version": "iris_test_workflow_closeout_carrier_manifest_v1", "entries": []},
    )
    assert report["status"] == "FAIL"
