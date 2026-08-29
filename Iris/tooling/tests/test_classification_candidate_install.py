from __future__ import annotations

from pathlib import Path

import pytest

from iris_tooling.domains.classification.cli import (
    ALLOWED_FILES,
    LAYER2_MANIFEST_NAME,
    _external_root,
    _sha256,
    _write_manifest,
    build_layer2_owner,
    install,
    install_layer2_owner,
    validate_layer2_owner,
)


def _candidate(root: Path) -> tuple[Path, str]:
    root.mkdir()
    for filename in ALLOWED_FILES:
        (root / filename).write_text(f"return {{ name = '{filename}' }}\n", encoding="utf-8")
    manifest = _write_manifest(root)
    return root, _sha256(manifest)


def test_hash_bound_install_copies_only_allowlisted_candidate_files(tmp_path: Path) -> None:
    candidate, manifest_sha256 = _candidate(tmp_path / "candidate")
    runtime = tmp_path / "runtime"

    assert install(candidate, manifest_sha256, runtime_data_root=runtime) == 0
    assert {path.name for path in runtime.iterdir()} == set(ALLOWED_FILES)
    assert all((runtime / name).read_bytes() == (candidate / name).read_bytes() for name in ALLOWED_FILES)

    (candidate / ALLOWED_FILES[0]).write_text("corrupt\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="candidate hash mismatch"):
        install(candidate, manifest_sha256, runtime_data_root=runtime)

    layer2_candidate = tmp_path / "layer2-candidate"
    assert build_layer2_owner(layer2_candidate) == 0
    layer2_manifest_sha256 = _sha256(layer2_candidate / LAYER2_MANIFEST_NAME)
    assert validate_layer2_owner(layer2_candidate, layer2_manifest_sha256) == 0
    installed_owner_output = tmp_path / "installed" / "classification_layer2_owner_output.json"
    assert install_layer2_owner(
        layer2_candidate,
        layer2_manifest_sha256,
        output_path=installed_owner_output,
    ) == 0
    assert installed_owner_output.read_bytes() == (
        layer2_candidate / "classification_layer2_owner_output.json"
    ).read_bytes()


def test_candidate_boundary_rejects_wrong_manifest_extra_file_and_repo_root(tmp_path: Path) -> None:
    candidate, manifest_sha256 = _candidate(tmp_path / "candidate")
    with pytest.raises(SystemExit, match="manifest hash mismatch"):
        install(candidate, "0" * 64, runtime_data_root=tmp_path / "runtime")

    (candidate / "unexpected.lua").write_text("return {}\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="unexpected file set"):
        install(candidate, manifest_sha256, runtime_data_root=tmp_path / "runtime")

    repository_root = Path(__file__).resolve().parents[3]
    with pytest.raises(SystemExit, match="outside the repository"):
        _external_root(repository_root, "test")
