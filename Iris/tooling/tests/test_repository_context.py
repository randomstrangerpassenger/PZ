from __future__ import annotations

from pathlib import Path

import pytest

from iris_tooling.build.repository_context import RepositoryContext, RepositoryContextError


def test_repository_context_requires_an_iris_git_checkout(tmp_path: Path) -> None:
    with pytest.raises(RepositoryContextError, match="not a Git checkout"):
        RepositoryContext.create(tmp_path)


def test_repository_context_exposes_explicit_project_paths(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "Iris" / "build" / "description" / "v2").mkdir(parents=True)
    context = RepositoryContext.create(tmp_path)
    assert context.iris_root == tmp_path / "Iris"
    assert context.description_v2_root == tmp_path / "Iris" / "build" / "description" / "v2"
