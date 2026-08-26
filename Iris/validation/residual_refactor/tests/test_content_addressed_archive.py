from __future__ import annotations

import json
from pathlib import Path
import subprocess
import zipfile

import pytest

from Iris.validation.residual_refactor.content_addressed_archive import (
    ArchiveError,
    create_archive,
    restore_archive,
    verify_archive,
)


def repository(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repository"
    root.mkdir()
    (root / "tracked.txt").write_bytes(b"same\n")
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "archive@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Archive Test"], cwd=root, check=True)
    subprocess.run(["git", "add", "tracked.txt"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-m", "source"], cwd=root, check=True, capture_output=True)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, text=True, capture_output=True).stdout.strip()
    return root, commit


def selection(tmp_path: Path) -> Path:
    path = tmp_path / "selection.json"
    path.write_text(json.dumps({"rows": [{"logical_path": "tracked.txt", "source_domain": "tracked_git_blob", "role": "historical_reproduction"}]}), encoding="utf-8")
    return path


def test_create_verify_restore_is_deterministic(tmp_path: Path) -> None:
    repo, commit = repository(tmp_path)
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    selected = selection(tmp_path)
    create_archive(repo, commit, repo, selected, first, "test-store")
    create_archive(repo, commit, repo, selected, second, "test-store")
    assert first.read_bytes() == second.read_bytes()
    assert verify_archive(first)["logical_file_count"] == 1
    restored = tmp_path / "restored"
    restored.mkdir()
    receipt = restore_archive(first, restored)
    assert receipt["status"] == "PASS"
    assert (restored / "tracked.txt").read_bytes() == b"same\n"


@pytest.mark.parametrize("logical", ["../escape", "/absolute", "C:/drive", "a\\b"])
def test_path_escape_is_rejected(tmp_path: Path, logical: str) -> None:
    repo, commit = repository(tmp_path)
    selected = tmp_path / "bad.json"
    selected.write_text(json.dumps({"rows": [{"logical_path": logical, "source_domain": "tracked_git_blob"}]}), encoding="utf-8")
    with pytest.raises(ArchiveError):
        create_archive(repo, commit, repo, selected, tmp_path / "bad.zip", "test-store")


def test_duplicate_and_corrupt_object_fail_closed(tmp_path: Path) -> None:
    repo, commit = repository(tmp_path)
    archive = tmp_path / "archive.zip"
    create_archive(repo, commit, repo, selection(tmp_path), archive, "test-store")
    with zipfile.ZipFile(archive) as source:
        members = {name: source.read(name) for name in source.namelist()}
    object_name = next(name for name in members if name.startswith("objects/"))
    members[object_name] = b"corrupt"
    corrupt = tmp_path / "corrupt.zip"
    with zipfile.ZipFile(corrupt, "w") as output:
        for name, payload in members.items():
            output.writestr(name, payload)
    with pytest.raises(ArchiveError):
        verify_archive(corrupt)


def test_duplicate_logical_path_is_rejected(tmp_path: Path) -> None:
    repo, commit = repository(tmp_path)
    selected = tmp_path / "duplicate.json"
    row = {"logical_path": "tracked.txt", "source_domain": "tracked_git_blob"}
    selected.write_text(json.dumps({"rows": [row, row]}), encoding="utf-8")
    with pytest.raises(ArchiveError, match="duplicate archive logical path"):
        create_archive(repo, commit, repo, selected, tmp_path / "duplicate.zip", "test-store")


def test_missing_object_and_nonempty_restore_fail_closed(tmp_path: Path) -> None:
    repo, commit = repository(tmp_path)
    archive = tmp_path / "archive.zip"
    create_archive(repo, commit, repo, selection(tmp_path), archive, "test-store")
    with zipfile.ZipFile(archive) as source:
        members = {name: source.read(name) for name in source.namelist() if not name.startswith("objects/")}
    missing = tmp_path / "missing.zip"
    with zipfile.ZipFile(missing, "w") as output:
        for name, payload in members.items():
            output.writestr(name, payload)
    with pytest.raises(ArchiveError):
        verify_archive(missing)

    restored = tmp_path / "nonempty"
    restored.mkdir()
    (restored / "occupied").write_text("occupied", encoding="utf-8")
    with pytest.raises(ArchiveError, match="existing empty directory"):
        restore_archive(archive, restored)


def test_custody_symlink_is_rejected(tmp_path: Path) -> None:
    repo, commit = repository(tmp_path)
    external = tmp_path / "external.txt"
    external.write_bytes(b"external")
    link = repo / "custody-link.txt"
    try:
        link.symlink_to(external)
    except OSError:
        pytest.skip("symlink creation is unavailable")
    selected = tmp_path / "symlink.json"
    selected.write_text(
        json.dumps({"rows": [{"logical_path": "custody-link.txt", "source_domain": "custody_file"}]}),
        encoding="utf-8",
    )
    with pytest.raises(ArchiveError, match="unsafe or absent"):
        create_archive(repo, commit, repo, selected, tmp_path / "symlink.zip", "test-store")
