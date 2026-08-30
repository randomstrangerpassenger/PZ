from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from iris_tooling.__main__ import main


def test_help_is_repository_independent(capfd, monkeypatch, tmp_path: Path) -> None:
    assert main([]) == 0
    assert "Iris repository-bound offline build and validation adapter" in capfd.readouterr().out
    repository_root = Path(__file__).resolve().parents[3]
    assert main(
        ["--repository-root", str(repository_root), "inspect", "current"]
    ) == 0
    route = json.loads(capfd.readouterr().out)
    assert route["schema_version"] == "iris-current-route-index-v1"
    assert route["maximum_navigation_hops"] <= 2
    assert route["receipt_query_contract"]["mutable_latest_pointer"] is False
    assert route["historical_opt_in"]["blanket_round3_exclusion"] is False
    for paths in route["routes"].values():
        for path in paths:
            assert (repository_root / path).exists(), path
    assert all(
        (repository_root / path).exists()
        for path in route["default_current_allowlist"]
    )

    entrypoints = repository_root / "Iris/build/ENTRYPOINTS.md"
    current_docs = (
        entrypoints,
        repository_root / "Iris/build/build_import_contract.md",
        repository_root / "Iris/AGENTS.md",
    )
    command_literal = "run_contract_tests.py --class current --list"
    assert [
        path.relative_to(repository_root).as_posix()
        for path in current_docs
        if command_literal in path.read_text(encoding="utf-8")
    ] == ["Iris/build/ENTRYPOINTS.md"]
    assert (repository_root / "Iris/_docs/authority/iris_current_route_index.json").stat().st_size <= 64 * 1024

    cli_source = (
        repository_root / "Iris/tooling/src/iris_tooling/__main__.py"
    ).read_text(encoding="utf-8")
    assert "invoke_receipt_bound_full_gate.ps1" in cli_source
    assert "required_standalone_validations" not in cli_source

    captured_command: list[str] = []

    def fake_run(command, **kwargs):
        captured_command.extend(command)
        assert kwargs["cwd"] == repository_root
        return SimpleNamespace(
            stdout=b'{"schema_version":"launcher-owned"}\n',
            stderr=b"human diagnostic\n",
            returncode=7,
        )

    monkeypatch.setattr("iris_tooling.__main__.subprocess.run", fake_run)
    assert main(
        [
            "--repository-root", str(repository_root),
            "validate", "full",
            "--commit", "a" * 40,
            "--claim-id", "focused-probe",
            "--environment-receipt", str(tmp_path / "environment.json"),
            "--work-root", str(tmp_path / "work"),
            "--result-root", str(tmp_path / "result"),
            "--orchestration-receipt", str(tmp_path / "orchestration.json"),
        ]
    ) == 7
    captured = capfd.readouterr()
    assert captured.out == '{"schema_version":"launcher-owned"}\n'
    assert captured.err == "human diagnostic\n"
    assert any("invoke_receipt_bound_full_gate.ps1" in value for value in captured_command)
    assert not any("run_contract_tests.py" in value for value in captured_command)

    captured_command.clear()
    predecessor_receipts = tmp_path / "predecessor-receipts.json"
    qualification_contract = tmp_path / "qualification-contract.json"
    assert main(
        [
            "--repository-root", str(repository_root),
            "validate", "full",
            "--commit", "b" * 40,
            "--claim-id", "composite-probe",
            "--environment-receipt", str(tmp_path / "environment.json"),
            "--work-root", str(tmp_path / "work-composite"),
            "--result-root", str(tmp_path / "result-composite"),
            "--orchestration-receipt", str(tmp_path / "orchestration-composite.json"),
            "--execution-context", "composite_baseline_admission_chain_stage_6",
            "--predecessor-stage-receipt-set-sha256", "c" * 64,
            "--qualification-contract-sha256", "d" * 64,
            "--predecessor-stage-receipt-set", str(predecessor_receipts),
            "--qualification-contract", str(qualification_contract),
        ]
    ) == 7
    expected_pairs = {
        "-PredecessorStageReceiptSetSha256": "c" * 64,
        "-QualificationContractSha256": "d" * 64,
        "-PredecessorStageReceiptSet": str(predecessor_receipts.resolve()),
        "-QualificationContract": str(qualification_contract.resolve()),
    }
    for flag, value in expected_pairs.items():
        index = captured_command.index(flag)
        assert captured_command[index + 1] == value


@pytest.mark.parametrize("legacy_flag", ["--v22", "--v23", "--v24"])
def test_rightclick_rejects_predecessor_mode_flags(legacy_flag: str) -> None:
    repository_root = Path(__file__).resolve().parents[3]
    with pytest.raises(SystemExit) as error:
        main(
            [
                "--repository-root",
                str(repository_root),
                "rightclick",
                legacy_flag,
            ]
        )
    assert error.value.code == 2
