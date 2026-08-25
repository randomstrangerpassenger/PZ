from __future__ import annotations

import ast
import hashlib
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
        assert path.stat().st_size < 1_000


def test_current_package_has_no_machine_local_source_paths() -> None:
    package_root = Path(iris_tooling.__file__).resolve().parent
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in package_root.rglob("*.py")
    )
    assert "C:\\Users\\MW" not in source
    assert "G:\\Program Files" not in source
