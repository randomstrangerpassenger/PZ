from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping


class PublicTextInputError(ValueError):
    """Raised when a strict public-text input cannot be decoded."""


@dataclass(frozen=True)
class NaturalizationProvenanceInputs:
    """Explicit machine-independent inputs required by naturalization Phase 0."""

    roadmap: Path
    plan_review: Path
    cycle2_review: Path

    @property
    def paths(self) -> tuple[Path, Path, Path]:
        return (self.roadmap, self.plan_review, self.cycle2_review)

    def binding_rows(
        self,
        *,
        expected_hashes: Mapping[str, str],
        hash_file: Callable[[Path], str],
    ) -> list[dict[str, Any]]:
        by_role = {
            "roadmap": self.roadmap,
            "plan_review": self.plan_review,
            "cycle2_review": self.cycle2_review,
        }
        if set(expected_hashes) != set(by_role):
            raise PublicTextInputError("naturalization provenance roles are incomplete")
        rows: list[dict[str, Any]] = []
        for role, path in by_role.items():
            if not path.is_file():
                raise PublicTextInputError(
                    f"explicit naturalization provenance input missing: {role}: {path}"
                )
            expected_hash = expected_hashes[role]
            actual_hash = hash_file(path)
            rows.append(
                {
                    "role": role,
                    "path": str(path),
                    "expected_sha256": expected_hash,
                    "actual_sha256": actual_hash,
                    "hash_match": actual_hash == expected_hash,
                }
            )
        return rows


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PublicTextInputError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_bytes(raw: bytes, *, label: str) -> Any:
    try:
        return json.loads(
            raw.decode("utf-8-sig"), object_pairs_hook=_reject_duplicates
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PublicTextInputError(f"cannot read strict JSON: {label}") from exc


def load_json(path: Path) -> Any:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise PublicTextInputError(f"cannot read strict JSON: {path}") from exc
    return load_json_bytes(raw, label=str(path))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as exc:
        raise PublicTextInputError(f"cannot read strict JSONL: {path}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(lines, start=1):
        if not raw_line.strip():
            continue
        try:
            value = json.loads(raw_line, object_pairs_hook=_reject_duplicates)
        except json.JSONDecodeError as exc:
            raise PublicTextInputError(
                f"cannot read strict JSONL: {path}:{line_number}"
            ) from exc
        if not isinstance(value, dict):
            raise PublicTextInputError(
                f"JSONL row must be object: {path}:{line_number}"
            )
        rows.append(value)
    return rows
