from __future__ import annotations

from .naturalization_context import *  # noqa: F401,F403

class NaturalizationError(RuntimeError):
    pass


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise NaturalizationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return load_public_text_json(path)
    except PublicTextInputError as exc:
        raise NaturalizationError(f"cannot read strict JSON: {path}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        return load_public_text_jsonl(path)
    except PublicTextInputError as exc:
        raise NaturalizationError(f"cannot read strict JSONL: {path}") from exc


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def pretty_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as exc:
        raise NaturalizationError(f"cannot hash file: {path}") from exc
    return digest.hexdigest()


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def compact_canonical_hash(value: Any) -> str:
    return sha256_bytes(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def write_once_or_same(path: Path, value: Any) -> str:
    encoded = pretty_json_bytes(value)
    if path.exists():
        if path.read_bytes() != encoded:
            raise NaturalizationError(f"write-once conflict: {path}")
        return sha256_bytes(encoded)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return sha256_bytes(encoded)


def write_jsonl_once_or_same(path: Path, rows: Iterable[dict[str, Any]]) -> str:
    encoded = b"".join(canonical_json_bytes(row) for row in rows)
    if path.exists():
        if path.read_bytes() != encoded:
            raise NaturalizationError(f"write-once conflict: {path}")
        return sha256_bytes(encoded)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return sha256_bytes(encoded)


def require_files(paths: Iterable[Path]) -> None:
    missing = [repo_relative(path) for path in paths if not path.is_file()]
    if missing:
        raise NaturalizationError(f"missing required files: {missing}")


def attempt_root_for(attempt_id: str, explicit_root: Path | None = None) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,63}", attempt_id):
        raise NaturalizationError("attempt-id must match [a-z0-9][a-z0-9._-]{2,63}")
    root = (
        explicit_root.resolve()
        if explicit_root is not None
        else (DEFAULT_ATTEMPT_PARENT / attempt_id).resolve()
    )
    if explicit_root is None and root.parent != DEFAULT_ATTEMPT_PARENT.resolve():
        raise NaturalizationError("default attempt root escaped canonical parent")
    return root


def phase_root(attempt_root: Path, phase: int) -> Path:
    return attempt_root / f"phase{phase}"


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise NaturalizationError(
            f"git command failed ({result.returncode}): {' '.join(args)}"
        )
    return result.stdout.strip()


def protected_snapshot() -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for path in PROTECTED_PATHS:
        files.append(
            {
                "path": repo_relative(path),
                "exists": path.is_file(),
                "sha256": sha256_file(path) if path.is_file() else None,
            }
        )
    chunk_dir = (
        REPO_ROOT
        / "Iris"
        / "media"
        / "lua"
        / "client"
        / "Iris"
        / "Data"
        / "IrisLayer3DataChunks"
    )
    chunk_rows = [
        {"path": repo_relative(path), "sha256": sha256_file(path)}
        for path in sorted(chunk_dir.glob("*.lua"))
    ]
    return {
        "schema_version": "dvf-3-3-protected-surface-snapshot-v1",
        "files": files,
        "runtime_chunk_count": len(chunk_rows),
        "runtime_chunks_digest": canonical_hash(chunk_rows),
    }


def normalize_legacy_rendered(value: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(value, ensure_ascii=False))
    meta = normalized.get("meta")
    if isinstance(meta, dict):
        meta.pop("generated_at", None)
    return normalized


def manifest_binding_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        {
            "id": "facts",
            "path": str(manifest["facts"]["path"]),
            "declared_sha256": str(manifest["facts"]["sha256"]),
        },
        {
            "id": "decisions",
            "path": str(manifest["decisions"]["path"]),
            "declared_sha256": str(manifest["decisions"]["sha256"]),
        },
    ]
    overlay = manifest["overlays"][0]
    rows.append(
        {
            "id": "overlay",
            "path": str(overlay["path"]),
            "declared_sha256": str(overlay["sha256"]),
        }
    )
    for key, identifier in (
        ("profiles_path", "profiles"),
        ("identity_rules_path", "identity_rules"),
        ("precedence_rules_path", "precedence_rules"),
    ):
        rows.append(
            {
                "id": identifier,
                "path": str(manifest["compose_authority"][key]),
                "declared_sha256": str(
                    manifest["compose_authority"][key.replace("_path", "_sha256")]
                ),
            }
        )
    for row in rows:
        path = REPO_ROOT / row["path"]
        row["actual_sha256"] = sha256_file(path) if path.is_file() else None
        row["hash_match"] = row["actual_sha256"] == row["declared_sha256"]
    return rows

__all__ = [
    name for name in globals() if not name.startswith("__")
]
