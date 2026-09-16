"""Compatibility adapter for public-text composition.

Retained for existing build imports and dynamic callers.
"""
from __future__ import annotations

from iris_tooling.domains.public_text.composition.io import (
    Any,
    FILE_HASH_CONTRACT,
    JSONL_BYTE_CONTRACT,
    Path,
    _iter_binary_chunks,
    _serialize_jsonl_row,
    _strict_windows_path,
    entries_sha256,
    file_sha256,
    hashlib,
    json,
    load_json,
    load_jsonl,
    load_optional_jsonl_map,
    os,
    write_jsonl,
)
