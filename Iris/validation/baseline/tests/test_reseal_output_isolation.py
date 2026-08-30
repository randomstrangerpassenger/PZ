from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

from Iris.validation.baseline.qualification_contracts import AdmissionError, require_external


REPO = Path(__file__).resolve().parents[4]
MANIFEST = REPO / "Iris/validation/execution/required_validations.json"
RESEAL_TOOLS = (
    REPO / "Iris/build/description/v2/tools/build/dvf_3_3_current_route_required_validation_evidence_freshness_reseal.py",
    REPO / "Iris/build/description/v2/tools/build/dvf_3_3_current_source_authority_drift_verification_adoption_reseal.py",
)


def _round3_conftest_module():
    path = REPO / "Iris/build/description/v2/tests/conftest.py"
    spec = importlib.util.spec_from_file_location("iris_round3_conftest_probe", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_external_root_cannot_be_nested_under_checkout(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    try:
        require_external(repo, repo / "out", "result root")
    except AdmissionError as exc:
        assert exc.code == "durable_root_inside_subject_checkout"
    else:
        raise AssertionError("repository-local output was accepted")


def test_configured_current_legacy_projection_rejects_local_root_before_write() -> None:
    module = _round3_conftest_module()
    target = REPO / "configured-current-local-write-probe"
    assert not target.exists()
    try:
        module._new_external_output_root(target)
    except RuntimeError as exc:
        assert "outside the repository" in str(exc)
    else:
        raise AssertionError("repository-local legacy projection root was accepted")
    assert not target.exists()


def test_current_validation_reseal_projects_without_live_manifest_write(tmp_path: Path) -> None:
    before = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    for index, tool in enumerate(RESEAL_TOOLS):
        root = tmp_path / f"reseal-{index}"
        completed = subprocess.run(
            [sys.executable, "-B", str(tool), "--mode", "manifest-only", "--root", str(root), "--execution-context", "current_validation"],
            cwd=REPO,
            text=True,
            capture_output=True,
            check=False,
        )
        # current_validation intentionally does not adopt the projection.  An
        # authority-adoption predicate may therefore be non-PASS; isolation is
        # the contract under test and parser/IO failures remain unacceptable.
        assert completed.returncode in {0, 1}, completed.stdout + completed.stderr
        projection = root / "phase3/current_route_required_validations.projection.json"
        assert projection.is_file()
    assert hashlib.sha256(MANIFEST.read_bytes()).hexdigest() == before


def test_current_validation_reseal_rejects_repository_local_root() -> None:
    tool = RESEAL_TOOLS[0]
    completed = subprocess.run(
        [sys.executable, "-B", str(tool), "--mode", "manifest-only", "--root", str(REPO / "Iris/build/description/v2/staging/reseal-probe"), "--execution-context", "current_validation"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 2
    assert "repository-external" in completed.stderr
