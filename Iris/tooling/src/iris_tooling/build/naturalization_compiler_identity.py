"""Compatibility adapter for public-text composition.

Retained for existing build imports and dynamic callers.
"""
from __future__ import annotations

from iris_tooling.domains.public_text.composition.compiler_identity import (
    COMPILER_FILE_HASH_ALGORITHM_ID,
    COMPILER_IDENTITY_ALGORITHM_ID,
    COMPILER_IDENTITY_SCHEMA_VERSION,
    COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER,
    CompilerIdentityError,
    Mapping,
    Path,
    PurePosixPath,
    REPO_ROOT,
    TOOLS_DIR,
    V2_ROOT,
    _LOWER_SHA256,
    _canonical_json_bytes,
    _sha256,
    build_compiler_identity,
    build_compiler_identity_from_bytes,
    build_compiler_identity_from_git,
    canonicalize_compiler_source_bytes,
    compiler_identity_matches_claim,
    compiler_source_paths,
    hashlib,
    json,
    main,
    re,
    require_repository_context,
    subprocess,
)
