from __future__ import annotations

import ast
import hashlib
import importlib
from pathlib import Path

import pytest
import iris_tooling

from iris_tooling.domains.public_text.evaluate import (
    PublicTextEvaluationError,
    determine_qualified_disposition,
    evaluate_threshold,
)
from iris_tooling.domains.public_text.inputs import (
    NaturalizationProvenanceInputs,
    PublicTextInputError,
    load_json_bytes,
)
from iris_tooling.domains.public_text.naturalization import select_rank
from iris_tooling.domains.public_text import cli as public_text_cli
from iris_tooling.domains.public_text import naturalization_application


def test_threshold_and_disposition_are_pure_domain_contracts() -> None:
    assert evaluate_threshold(
        numerator=1,
        denominator=4,
        threshold={"operator": "le", "value": {"numerator": 1, "denominator": 2}},
    )
    assert determine_qualified_disposition(
        technical_blocker_count=0,
        effective_blocking_finding_count=0,
        advisory_debt_count=1,
        active_waiver_count=0,
    ) == "deferred_internal_debt"
    with pytest.raises(PublicTextEvaluationError):
        evaluate_threshold(numerator=-1, denominator=1, threshold={"operator": "none", "value": None})


def test_strict_input_and_candidate_rank_are_deterministic() -> None:
    with pytest.raises(PublicTextInputError, match="duplicate JSON key"):
        load_json_bytes(b'{"a":1,"a":2}', label="fixture")
    assert select_rank("candidate", "stratum", "Base.Hammer") == select_rank(
        "candidate", "stratum", "Base.Hammer"
    )


def test_naturalization_provenance_is_explicit_and_fail_closed(
    tmp_path: Path,
) -> None:
    paths = {
        role: tmp_path / f"{role}.txt"
        for role in ("roadmap", "plan_review", "cycle2_review")
    }
    for role, path in paths.items():
        path.write_text(role, encoding="utf-8")
    expected = {
        role: hashlib.sha256(path.read_bytes()).hexdigest()
        for role, path in paths.items()
    }
    inputs = NaturalizationProvenanceInputs(**paths)

    rows = inputs.binding_rows(
        expected_hashes=expected,
        hash_file=lambda path: hashlib.sha256(path.read_bytes()).hexdigest(),
    )

    assert [row["role"] for row in rows] == [
        "roadmap",
        "plan_review",
        "cycle2_review",
    ]
    assert all(row["hash_match"] for row in rows)
    paths["roadmap"].unlink()
    with pytest.raises(PublicTextInputError, match="explicit.*input missing"):
        inputs.binding_rows(
            expected_hashes=expected,
            hash_file=lambda path: hashlib.sha256(path.read_bytes()).hexdigest(),
        )


def test_public_text_build_modules_are_thin_facades() -> None:
    package_root = Path(iris_tooling.__file__).resolve().parent
    facade_paths = (
        package_root / "build" / "public_text_quality_acceptance.py",
        package_root
        / "build"
        / "run_dvf_3_3_korean_prose_naturalization.py",
    )
    for path in facade_paths:
        module = ast.parse(path.read_text(encoding="utf-8"))
        assert not any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            for node in module.body
        )


def test_phase0_cli_forwards_all_explicit_provenance_inputs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = {
        role: tmp_path / f"{role}.txt"
        for role in ("roadmap", "plan_review", "cycle2_review")
    }
    for role, path in paths.items():
        path.write_text(role, encoding="utf-8")
    captured: dict[str, object] = {}

    def fake_run(**kwargs: object) -> dict[str, str]:
        captured.update(kwargs)
        return {"status": "PASS"}

    monkeypatch.setattr(naturalization_application, "run_naturalization_mode", fake_run)
    result = public_text_cli.main(
        [
            "naturalization", "--attempt-id", "hardening-probe",
            "--mode", "phase0-preflight", "--attempt-root", str(tmp_path / "attempt"),
            "--roadmap-input", str(paths["roadmap"]),
            "--plan-review-input", str(paths["plan_review"]),
            "--cycle2-review-input", str(paths["cycle2_review"]),
        ]
    )

    assert result == 0
    provenance = captured["provenance_inputs"]
    assert isinstance(provenance, NaturalizationProvenanceInputs)
    assert provenance == NaturalizationProvenanceInputs(
        roadmap=paths["roadmap"].resolve(),
        plan_review=paths["plan_review"].resolve(),
        cycle2_review=paths["cycle2_review"].resolve(),
    )


def test_phase0_cli_missing_input_fails_closed_without_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def unexpected_run(**kwargs: object) -> dict[str, str]:
        raise AssertionError(f"unexpected dispatch: {kwargs}")

    monkeypatch.setattr(
        naturalization_application, "run_naturalization_mode", unexpected_run
    )
    result = public_text_cli.main(
        [
            "naturalization", "--attempt-id", "hardening-probe",
            "--mode", "phase0-preflight", "--attempt-root", str(tmp_path / "attempt"),
            "--roadmap-input", str(tmp_path / "roadmap.txt"),
            "--plan-review-input", str(tmp_path / "plan-review.txt"),
        ]
    )

    assert result == 2
    assert "requires --roadmap-input" in capsys.readouterr().err


def test_public_text_owner_chain_has_only_explicit_static_exports() -> None:
    package_root = Path(iris_tooling.__file__).resolve().parent
    domain_root = package_root / "domains" / "public_text"
    paths = sorted(domain_root.glob("acceptance_*.py"))
    paths.extend(sorted(domain_root.glob("naturalization_*.py")))
    paths.append(domain_root / "cli.py")
    paths.extend(
        (
            package_root / "build" / "public_text_quality_acceptance.py",
            package_root / "build" / "run_dvf_3_3_korean_prose_naturalization.py",
        )
    )

    for path in paths:
        module = ast.parse(path.read_text(encoding="utf-8"))
        assert not any(
            isinstance(node, ast.ImportFrom)
            and any(alias.name == "*" for alias in node.names)
            for node in ast.walk(module)
        ), path
        all_assignments = [
            node
            for node in module.body
            if isinstance(node, (ast.Assign, ast.AnnAssign))
            and any(
                isinstance(target, ast.Name) and target.id == "__all__"
                for target in (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
            )
        ]
        assert len(all_assignments) == 1, path
        value = all_assignments[0].value
        assert isinstance(value, ast.Tuple), path
        assert all(
            isinstance(element, ast.Constant) and isinstance(element.value, str)
            for element in value.elts
        ), path
        relative_module = path.relative_to(package_root).with_suffix("")
        module_name = "iris_tooling." + ".".join(relative_module.parts)
        imported_module = importlib.import_module(module_name)
        assert set(imported_module.__all__) <= set(vars(imported_module)), path


def test_public_text_compatibility_facades_export_only_declared_api() -> None:
    module_names = (
        "iris_tooling.build.public_text_quality_acceptance",
        "iris_tooling.build.run_dvf_3_3_korean_prose_naturalization",
    )
    for module_name in module_names:
        module = importlib.import_module(module_name)
        public_names = {name for name in vars(module) if not name.startswith("_")}
        assert public_names == set(module.__all__)


def test_current_package_has_no_machine_local_source_paths() -> None:
    package_root = Path(iris_tooling.__file__).resolve().parent
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in package_root.rglob("*.py")
    )
    assert "C:\\Users\\MW" not in source
    assert "G:\\Program Files" not in source
