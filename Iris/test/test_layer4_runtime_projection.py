from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
from iris_tooling.build import generate_layer4_runtime_projection as generator
from iris_tooling.build import update_layer4_runtime_projection as updater
from iris_tooling.build import validate_layer4_runtime_projection as validator


def test_complete_generation_is_deterministic_and_valid(tmp_path: Path) -> None:
    candidate_a = tmp_path / "a"
    candidate_b = tmp_path / "b"
    metrics_a = generator.generate_projection(candidate_a, REPOSITORY_ROOT)
    metrics_b = generator.generate_projection(candidate_b, REPOSITORY_ROOT)

    assert metrics_a == metrics_b
    assert metrics_a["fulltype_count"] == 1631
    assert metrics_a["recipe_row_count"] == 791
    assert metrics_a["generated_file_count"] == 13
    expected, _metrics = generator.render_projection(REPOSITORY_ROOT)
    assert all((candidate_a / path).read_bytes() == (candidate_b / path).read_bytes() for path in expected)
    assert validator.validate_projection(candidate_a, REPOSITORY_ROOT) == metrics_a


def test_validator_rejects_missing_and_modified_generated_content(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate"
    generator.generate_projection(candidate, REPOSITORY_ROOT)
    first_chunk = candidate / generator.CHUNK_ROOT_REL / "Chunk001.lua"
    original = first_chunk.read_text(encoding="utf-8")
    first_chunk.write_text(original.replace("recipe_id = ", "recipe_key = ", 1), encoding="utf-8")
    with pytest.raises(validator.Layer4ValidationError, match="source/order/schema mismatch"):
        validator.validate_projection(candidate, REPOSITORY_ROOT)

    first_chunk.write_text(original, encoding="utf-8")
    first_chunk.unlink()
    with pytest.raises(validator.Layer4ValidationError, match="file universe mismatch"):
        validator.validate_projection(candidate, REPOSITORY_ROOT)


def _git(repository_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repository_root, check=True, text=True, capture_output=True
    )
    return result.stdout.strip()


def _prepare_fake_repository(tmp_path: Path) -> tuple[Path, str]:
    repository = tmp_path / "repository"
    target = repository / updater.FACADE_REL
    target.parent.mkdir(parents=True)
    target.write_bytes(b"old\n")
    _git(repository, "init")
    _git(repository, "config", "user.email", "layer4@example.invalid")
    _git(repository, "config", "user.name", "Layer4 Test")
    _git(repository, "add", ".")
    _git(repository, "commit", "-m", "predecessor")
    return repository, _git(repository, "rev-parse", "HEAD")


def _install_fakes(monkeypatch: pytest.MonkeyPatch, fail_post_apply: bool = False) -> None:
    rendered = {updater.FACADE_REL: b"new\n"}

    def fake_generate(candidate_root: Path, _repository_root: Path) -> dict[str, int]:
        destination = candidate_root / updater.FACADE_REL
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(rendered[updater.FACADE_REL])
        return {"generated_file_count": 1}

    calls = 0

    def fake_validate(candidate_root: Path, _repository_root: Path, parity_root=None):
        nonlocal calls
        calls += 1
        if fail_post_apply and calls == 2:
            raise validator.Layer4ValidationError("injected post-apply failure")
        assert (candidate_root / updater.FACADE_REL).read_bytes() == b"new\n"
        return {"generated_file_count": 1}

    monkeypatch.setattr(updater, "generate_projection", fake_generate)
    monkeypatch.setattr(updater, "render_projection", lambda _root: (rendered, {}))
    monkeypatch.setattr(updater, "validate_projection", fake_validate)


def test_guarded_updater_applies_then_reapply_is_noop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository, predecessor = _prepare_fake_repository(tmp_path)
    _install_fakes(monkeypatch)
    assert updater.update_projection(repository, predecessor) == "applied"
    assert (repository / updater.FACADE_REL).read_bytes() == b"new\n"
    assert updater.update_projection(repository, predecessor) == "no-op"


def test_guarded_updater_restores_predecessor_on_post_apply_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository, predecessor = _prepare_fake_repository(tmp_path)
    _install_fakes(monkeypatch, fail_post_apply=True)
    with pytest.raises(validator.Layer4ValidationError, match="injected post-apply failure"):
        updater.update_projection(repository, predecessor)
    assert (repository / updater.FACADE_REL).read_bytes() == b"old\n"
