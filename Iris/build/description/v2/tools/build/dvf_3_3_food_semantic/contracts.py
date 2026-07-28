from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


CONTRACT_VERSION = "dvf3_3_food_semantic_authority_v1"
ATTEMPT_ROOT_FRAGMENT = (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_food_semantic_facts_authority/attempts"
)


class FoodSemanticError(RuntimeError):
    """Fail-loud contract error."""


@dataclass(frozen=True)
class ArtifactIdentity:
    path: str
    sha256: str
    byte_count: int


@dataclass(frozen=True)
class PropositionLineage:
    item_identity: str
    source_family: str
    source_artifact_path: str
    source_artifact_sha256: str
    source_item_locator: str
    source_field: str
    source_value: Any
    normalization_operations: tuple[str, ...]
    allowlist_identity: str
    rule_identity: str
    rule_output_signal: str
    writer_attempt_identity: str
    fact_field: str
    fact_value: str
    signal_to_fact_mapping_id: str
    mapping_version: str
    fact_proposition_identity: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["normalization_operations"] = list(self.normalization_operations)
        return payload


def repo_root() -> Path:
    return Path(__file__).resolve().parents[7]


def repo_path(value: str | Path, *, root: Path | None = None) -> Path:
    base = (root or repo_root()).resolve()
    path = Path(value)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def relative_posix(path: Path, *, root: Path | None = None) -> str:
    base = (root or repo_root()).resolve()
    return path.resolve().relative_to(base).as_posix()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def identity(path: Path, *, root: Path | None = None) -> ArtifactIdentity:
    return ArtifactIdentity(
        path=relative_posix(path, root=root),
        sha256=sha256_file(path),
        byte_count=path.stat().st_size,
    )


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def canonical_jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return "".join(
        json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for row in rows
    ).encode("utf-8")


def write_once_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = path.read_bytes()
        if existing != payload:
            raise FoodSemanticError(f"write-once artifact already differs: {path}")
        return
    path.write_bytes(payload)


def write_json(path: Path, value: Any, *, write_once: bool = True) -> None:
    payload = canonical_json_bytes(value)
    if write_once:
        write_once_bytes(path, payload)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def write_jsonl(
    path: Path, rows: Iterable[Mapping[str, Any]], *, write_once: bool = True
) -> None:
    payload = canonical_jsonl_bytes(rows)
    if write_once:
        write_once_bytes(path, payload)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise FoodSemanticError(f"{path}:{line_number}: JSONL row is not an object")
        result.append(value)
    return result


def iter_jsonl_with_raw(path: Path) -> Iterator[tuple[dict[str, Any], bytes]]:
    with path.open("rb") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            value = json.loads(raw.decode("utf-8"))
            if not isinstance(value, dict):
                raise FoodSemanticError(
                    f"{path}:{line_number}: JSONL row is not an object"
                )
            yield value, raw


def logical_line_count(text: str) -> int:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")
    return 0 if not normalized else len(normalized.split("\n"))


def normalized_snapshot_between(
    text: str, begin_marker: str, end_marker: str
) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    try:
        inner = normalized.split(begin_marker, 1)[1].split(end_marker, 1)[0]
    except IndexError as exc:
        raise FoodSemanticError("requirements snapshot markers are missing") from exc
    return inner.strip("\n") + "\n"


def canonical_member_digest(members: Iterable[str]) -> str:
    ordered = sorted(members)
    return sha256_text("".join(f"{member}\n" for member in ordered))


def canonical_proposition_id(item_id: str, axis: str, value: str) -> str:
    return "fsp:" + sha256_text(f"{item_id}\0{axis}\0{value}")[:24]


def canonical_batch_id(
    schema_sha256: str, queue_sha256: str, ordered_members: Sequence[str]
) -> str:
    member_digest = sha256_text("".join(f"{member}\n" for member in ordered_members))
    return "fsb:" + sha256_text(
        f"{schema_sha256}\0{queue_sha256}\0{member_digest}"
    )[:24]


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def assert_attempt_output_root(output_root: Path, *, root: Path | None = None) -> None:
    base = (root or repo_root()).resolve()
    expected_parent = (base / ATTEMPT_ROOT_FRAGMENT).resolve()
    resolved = output_root.resolve()
    if not is_relative_to(resolved, expected_parent) or resolved == expected_parent:
        raise FoodSemanticError(
            f"output root must be an attempt child of {expected_parent}: {resolved}"
        )


def assert_safe_writer_sink(
    sink: Path,
    *,
    attempt_root: Path,
    forbidden_roots: Iterable[Path],
) -> None:
    resolved = sink.resolve()
    if not is_relative_to(resolved, attempt_root.resolve()):
        raise FoodSemanticError(f"writer sink escapes attempt root: {resolved}")
    for forbidden in forbidden_roots:
        candidate = forbidden.resolve()
        if resolved == candidate or is_relative_to(resolved, candidate):
            raise FoodSemanticError(f"writer sink is protected: {resolved}")


def artifact_manifest(
    paths: Iterable[Path], *, root: Path | None = None
) -> list[dict[str, Any]]:
    return [
        asdict(identity(path, root=root))
        for path in sorted(paths, key=lambda value: relative_posix(value, root=root))
        if path.is_file()
    ]


def hash_tree(path: Path, *, root: Path | None = None) -> dict[str, Any]:
    files = [candidate for candidate in path.rglob("*") if candidate.is_file()]
    rows = artifact_manifest(files, root=root)
    payload = "".join(f"{row['path']}\t{row['sha256']}\n" for row in rows)
    return {
        "root": relative_posix(path, root=root),
        "file_count": len(rows),
        "inventory_sha256": sha256_text(payload),
        "files": rows,
    }
