from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
from typing import Mapping


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]

COMPILER_IDENTITY_ALGORITHM_ID = (
    "naturalization_compiler_identity_sha256_lf_normalized_ordered_paths_v2"
)
COMPILER_FILE_HASH_ALGORITHM_ID = "sha256_crlf_and_lone_cr_to_lf_bytes_v1"
COMPILER_IDENTITY_SCHEMA_VERSION = "naturalization_compiler_identity_evidence_v2"

COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER = (
    "Iris/build/description/v2/tools/build/compose_layer3_text.py",
    "Iris/build/description/v2/tools/build/compose_layer3_body_profile.py",
    "Iris/build/description/v2/tools/build/compose_layer3_item.py",
    "Iris/build/description/v2/tools/build/compose_layer3_render.py",
    "Iris/build/description/v2/tools/build/compose_layer3_blocks.py",
    "Iris/build/description/v2/tools/build/compose_layer3_identity.py",
    "Iris/build/description/v2/tools/build/compose_layer3_io.py",
    (
        "Iris/build/description/v2/tools/build/"
        "run_dvf_3_3_korean_prose_naturalization.py"
    ),
    (
        "Iris/build/description/v2/tools/build/"
        "validate_dvf_3_3_korean_prose_naturalization.py"
    ),
)

_LOWER_SHA256 = re.compile(r"[0-9a-f]{64}")


class CompilerIdentityError(ValueError):
    pass


def canonicalize_compiler_source_bytes(raw: bytes) -> bytes:
    return raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def compiler_source_paths(repo_root: Path = REPO_ROOT) -> tuple[Path, ...]:
    root = repo_root.resolve()
    return tuple(
        root.joinpath(*PurePosixPath(relative).parts)
        for relative in COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER
    )


def build_compiler_identity_from_bytes(
    contents_by_repo_relative_posix_path: Mapping[str, bytes],
) -> dict[str, object]:
    expected = set(COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER)
    actual = set(contents_by_repo_relative_posix_path)
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        raise CompilerIdentityError(
            f"compiler identity path set mismatch: missing={missing}, "
            f"unexpected={unexpected}"
        )

    ordered_files: list[dict[str, object]] = []
    aggregate_files: list[dict[str, str]] = []
    for ordinal, relative in enumerate(
        COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER
    ):
        raw = contents_by_repo_relative_posix_path[relative]
        if not isinstance(raw, bytes):
            raise CompilerIdentityError(
                f"compiler identity content is not bytes: {relative}"
            )
        canonical = canonicalize_compiler_source_bytes(raw)
        canonical_sha256 = _sha256(canonical)
        ordered_files.append(
            {
                "ordinal": ordinal,
                "path": relative,
                "hash_algorithm_id": COMPILER_FILE_HASH_ALGORITHM_ID,
                "canonical_sha256": canonical_sha256,
            }
        )
        aggregate_files.append(
            {
                "path": relative,
                "sha256": canonical_sha256,
            }
        )

    aggregate_payload = {
        "algorithm_id": COMPILER_IDENTITY_ALGORITHM_ID,
        "ordered_files": aggregate_files,
    }
    return {
        "schema_version": COMPILER_IDENTITY_SCHEMA_VERSION,
        "algorithm_id": COMPILER_IDENTITY_ALGORITHM_ID,
        "path_order": list(COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER),
        "ordered_files": ordered_files,
        "aggregate_sha256": _sha256(_canonical_json_bytes(aggregate_payload)),
        "content_normalization": "replace_crlf_then_lone_cr_with_lf",
        "path_form": "repo_relative_posix",
        "excluded_identity_inputs": [
            "absolute_path",
            "mtime",
            "worktree_location",
            "host_metadata",
            "raw_line_ending_representation",
        ],
    }


def build_compiler_identity(
    repo_root: Path = REPO_ROOT,
) -> dict[str, object]:
    paths = compiler_source_paths(repo_root)
    contents = {
        relative: path.read_bytes()
        for relative, path in zip(
            COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER,
            paths,
            strict=True,
        )
    }
    return build_compiler_identity_from_bytes(contents)


def compiler_identity_matches_claim(
    claimed_aggregate_sha256: object,
    evidence: Mapping[str, object],
) -> bool:
    return (
        isinstance(claimed_aggregate_sha256, str)
        and _LOWER_SHA256.fullmatch(claimed_aggregate_sha256) is not None
        and evidence.get("algorithm_id") == COMPILER_IDENTITY_ALGORITHM_ID
        and evidence.get("aggregate_sha256") == claimed_aggregate_sha256
    )


def main() -> int:
    print(
        json.dumps(
            build_compiler_identity(),
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
