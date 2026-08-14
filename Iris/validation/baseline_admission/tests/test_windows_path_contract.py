from __future__ import annotations

from pathlib import Path

from Iris.validation.baseline_admission.iris_baseline_admission_common import path_preflight, read_json


CONTRACT = read_json(Path(__file__).resolve().parents[1] / "contracts/windows_path_contract.json")


def test_declared_root_is_accepted() -> None:
    assert path_preflight(CONTRACT, Path("C:/i"))["status"] == "PASS"


def test_over_budget_root_is_named_rejection() -> None:
    root = Path("C:/" + ("x" * 80))
    report = path_preflight(CONTRACT, root)
    assert report["status"] == "REJECTED"
    assert report["failure_code"] == "windows_path_contract_rejected"
