from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


class RepositoryContextError(RuntimeError):
    """Raised when repository-bound tooling has no explicit repository context."""


@dataclass(frozen=True)
class RepositoryContext:
    repository_root: Path

    @classmethod
    def create(cls, repository_root: str | Path) -> "RepositoryContext":
        root = Path(repository_root).resolve()
        if not (root / ".git").exists():
            raise RepositoryContextError(f"not a Git checkout: {root}")
        if not (root / "Iris" / "build" / "description" / "v2").is_dir():
            raise RepositoryContextError(f"Iris description v2 root is missing: {root}")
        return cls(repository_root=root)

    @property
    def iris_root(self) -> Path:
        return self.repository_root / "Iris"

    @property
    def description_v2_root(self) -> Path:
        return self.iris_root / "build" / "description" / "v2"

    @property
    def predecessor_build_root(self) -> Path:
        return self.description_v2_root / "tools" / "build"


_current_context: RepositoryContext | None = None


def configure_repository(repository_root: str | Path) -> RepositoryContext:
    global _current_context
    context = RepositoryContext.create(repository_root)
    if _current_context is not None and _current_context != context:
        raise RepositoryContextError(
            f"repository context already configured: {_current_context.repository_root}"
        )
    _current_context = context
    return context


def require_repository_context() -> RepositoryContext:
    global _current_context
    if _current_context is None:
        repository_root = os.environ.get("IRIS_REPOSITORY_ROOT")
        if repository_root:
            _current_context = RepositoryContext.create(repository_root)
    if _current_context is None:
        raise RepositoryContextError(
            "repository context is not configured; pass --repository-root, set "
            "IRIS_REPOSITORY_ROOT, or call configure_repository()"
        )
    return _current_context
