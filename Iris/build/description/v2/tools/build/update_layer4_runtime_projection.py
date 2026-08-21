"""Install a validated complete Layer 4 projection with rollback."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from generate_layer4_runtime_projection import (
    CHUNK_ROOT_REL,
    DEFAULT_REPOSITORY_ROOT,
    FACADE_REL,
    generate_projection,
    render_projection,
)
from validate_layer4_runtime_projection import validate_projection


class Layer4UpdateError(RuntimeError):
    pass


def _managed_paths(root: Path) -> set[Path]:
    paths = {FACADE_REL} if (root / FACADE_REL).is_file() else set()
    chunk_root = root / CHUNK_ROOT_REL
    if chunk_root.is_dir():
        for path in chunk_root.glob("Chunk[0-9][0-9][0-9].lua"):
            paths.add(path.relative_to(root))
        for name in ("RequirementsLookup.lua", "ChunkIndex.lua", "LineCountIndex.lua"):
            if (chunk_root / name).is_file():
                paths.add((chunk_root / name).relative_to(root))
    return paths


def _git(repository_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args], cwd=repository_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check
    )


def _predecessor_paths(repository_root: Path, commit: str) -> set[Path]:
    prefix = CHUNK_ROOT_REL.as_posix()
    result = _git(repository_root, "ls-tree", "-r", "--name-only", commit, "--", FACADE_REL.as_posix(), prefix)
    paths: set[Path] = set()
    for raw in result.stdout.decode("utf-8").splitlines():
        path = Path(raw)
        if path == FACADE_REL or (
            path.parent == CHUNK_ROOT_REL
            and (path.name.startswith("Chunk") and path.suffix == ".lua"
                 or path.name in {"RequirementsLookup.lua", "ChunkIndex.lua", "LineCountIndex.lua"})
        ):
            paths.add(path)
    return paths


def _assert_predecessor(repository_root: Path, commit: str) -> None:
    current_paths = _managed_paths(repository_root)
    predecessor_paths = _predecessor_paths(repository_root, commit)
    if current_paths != predecessor_paths:
        raise Layer4UpdateError("current generated file universe does not match expected predecessor")
    for path in sorted(current_paths):
        expected_oid = _git(repository_root, "rev-parse", f"{commit}:{path.as_posix()}").stdout.strip()
        current_oid = _git(
            repository_root,
            "hash-object",
            f"--path={path.as_posix()}",
            path.as_posix(),
        ).stdout.strip()
        if current_oid != expected_oid:
            raise Layer4UpdateError(f"current generated file differs from predecessor: {path}")


def _matches(root: Path, rendered: dict[Path, bytes]) -> bool:
    return _managed_paths(root) == set(rendered) and all(
        (root / path).read_bytes() == content for path, content in rendered.items()
    )


def update_projection(repository_root: Path, expected_predecessor_commit: str) -> str:
    repository_root = repository_root.resolve()
    with tempfile.TemporaryDirectory(prefix="iris-layer4-update-") as temp_name:
        temp_root = Path(temp_name)
        candidate_a = temp_root / "candidate-a"
        candidate_b = temp_root / "candidate-b"
        generate_projection(candidate_a, repository_root)
        generate_projection(candidate_b, repository_root)
        rendered_a, _metrics = render_projection(repository_root)
        if any((candidate_a / path).read_bytes() != (candidate_b / path).read_bytes() for path in rendered_a):
            raise Layer4UpdateError("candidate A/B generation differs")
        validate_projection(candidate_a, repository_root)

        if _matches(repository_root, rendered_a):
            return "no-op"
        _assert_predecessor(repository_root, expected_predecessor_commit)

        backup_root = temp_root / "backup"
        original_paths = _managed_paths(repository_root)
        for path in original_paths:
            destination = backup_root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(repository_root / path, destination)
        try:
            for path in original_paths - set(rendered_a):
                (repository_root / path).unlink()
            for path in rendered_a:
                destination = repository_root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(candidate_a / path, destination)
            validate_projection(repository_root, repository_root)
        except Exception:
            for path in _managed_paths(repository_root):
                (repository_root / path).unlink()
            for path in original_paths:
                destination = repository_root / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup_root / path, destination)
            raise
    return "applied"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-root", type=Path, default=DEFAULT_REPOSITORY_ROOT)
    parser.add_argument("--expected-predecessor-commit", required=True)
    args = parser.parse_args()
    try:
        result = update_projection(args.repository_root, args.expected_predecessor_commit)
    except (Layer4UpdateError, OSError, subprocess.CalledProcessError) as exc:
        print(f"FAIL: {exc}")
        return 1
    print(f"PASS: Layer 4 guarded update {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
