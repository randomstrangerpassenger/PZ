from __future__ import annotations

from .acceptance_reporting import *  # noqa: F401,F403

def write_once_or_same(
    path: Path, value: Any, *, repository_root: Path = REPO_ROOT
) -> str:
    desired = pretty_json_bytes(value)
    return write_once_bytes(path, desired, repository_root=repository_root)



def load_jsonl_strict(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        raw_lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as exc:
        raise FoundationContractError(f"cannot load UTF-8 JSONL {path}: {exc}") from exc
    for line_number, raw_line in enumerate(raw_lines, start=1):
        if not raw_line.strip():
            continue
        try:
            row = json.loads(raw_line, object_pairs_hook=_reject_duplicate_pairs)
        except json.JSONDecodeError as exc:
            raise FoundationContractError(
                f"cannot load strict JSONL {path}:{line_number}: {exc}"
            ) from exc
        if not isinstance(row, dict):
            raise FoundationContractError(
                f"JSONL row must be an object: {path}:{line_number}"
            )
        rows.append(row)
    return rows


def canonical_jsonl_bytes(rows: Iterable[dict[str, Any]]) -> bytes:
    return b"".join(canonical_json_bytes(row) + b"\n" for row in rows)


def write_once_bytes(
    path: Path, desired: bytes, *, repository_root: Path = REPO_ROOT
) -> str:
    if os.name != "nt":
        if path.exists():
            if path.read_bytes() != desired:
                raise FoundationContractError(
                    f"write-once conflict at {repo_relative(path)}"
                )
            return "already_identical"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(desired)
        return "created"

    target = _validated_repository_artifact_target(
        path, repository_root=repository_root
    )
    target_filesystem = _windows_extended_length_path(target)
    try:
        if _filesystem_path_exists(target_filesystem):
            if _read_filesystem_bytes(target_filesystem) != desired:
                raise FoundationContractError(
                    f"write-once conflict at {repo_relative(path)}"
                )
            return "already_identical"

        parent = target.parent
        parent_filesystem = _windows_extended_length_path(parent)
        os.makedirs(parent_filesystem, exist_ok=True)
        revalidated = _validated_repository_artifact_target(
            path, repository_root=repository_root
        )
        if revalidated != target:
            raise FoundationContractError(
                "artifact target changed while its parent was being prepared"
            )

        temporary = parent / f".{target.name}.tmp-{uuid.uuid4().hex}"
        temporary_filesystem = _windows_extended_length_path(temporary)
        descriptor: int | None = None
        try:
            descriptor = os.open(
                temporary_filesystem,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0),
                0o600,
            )
            view = memoryview(desired)
            offset = 0
            while offset < len(view):
                written = os.write(descriptor, view[offset:])
                if written <= 0:
                    raise OSError("artifact temporary write made no progress")
                offset += written
            os.fsync(descriptor)
            os.close(descriptor)
            descriptor = None

            temporary_stat = os.stat(temporary_filesystem)
            temporary_bytes = _read_filesystem_bytes(temporary_filesystem)
            if temporary_stat.st_size != len(desired) or temporary_bytes != desired:
                raise FoundationContractError(
                    "artifact temporary sibling failed byte/hash verification"
                )
            if _filesystem_path_exists(target_filesystem):
                current = _read_filesystem_bytes(target_filesystem)
                if current != desired:
                    raise FoundationContractError(
                        f"write-once conflict at {repo_relative(path)}"
                    )
                os.unlink(temporary_filesystem)
                return "already_identical"

            os.replace(temporary_filesystem, target_filesystem)
            target_stat = os.stat(target_filesystem)
            target_bytes = _read_filesystem_bytes(target_filesystem)
            if target_stat.st_size != len(desired) or target_bytes != desired:
                raise FoundationContractError(
                    "atomically installed artifact failed byte/hash verification"
                )
            return "created"
        except Exception:
            if descriptor is not None:
                os.close(descriptor)
            try:
                os.unlink(temporary_filesystem)
            except FileNotFoundError:
                pass
            raise
    except FoundationContractError:
        raise
    except OSError as exc:
        raise FoundationContractError(
            f"long-path-safe artifact write failed at {repo_relative(path)}: {exc}"
        ) from exc


def write_once_text(path: Path, text: str) -> str:
    return write_once_bytes(path, text.replace("\r\n", "\n").encode("utf-8"))

__all__ = [
    name for name in globals() if not name.startswith("__")
]
