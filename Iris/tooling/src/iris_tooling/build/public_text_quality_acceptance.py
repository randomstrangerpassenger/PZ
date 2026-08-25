"""Compatibility facade for the public-text acceptance domain."""

from iris_tooling.build.naturalization_compiler_identity import build_compiler_identity
from iris_tooling.domains.public_text.acceptance_attempt_context import (
    PHASE0_REQUIRED_VCS_CONSUMERS, compute_candidate_metric_snapshot,
    handoff_artifact_path, human_review_blocker_count,
    phase0_required_vcs_preflight, validate_candidate_handoff,
)
from iris_tooling.domains.public_text.acceptance_context import (
    DISPOSITION_CLASSES, FOUNDATION_SCHEMA_VERSION,
    NATURALIZATION_COMPILER_IMPLEMENTATION_FILES, REPO_ROOT,
    TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID,
)
from iris_tooling.domains.public_text.acceptance_disposition import run_official_mode
from iris_tooling.domains.public_text.acceptance_foundation_application import (
    build_foundation, validate_foundation,
)
from iris_tooling.domains.public_text.acceptance_infrastructure import (
    FoundationContractError, build_protected_snapshot_identity_from_bytes,
    build_protected_snapshot_present_row_from_bytes,
    build_text_constituent_identity_from_bytes, canonical_hash,
    head_text_constituent_record, is_ignored, is_tracked, load_json_strict,
    normalize_text_line_endings, pretty_json_bytes, repo_relative, sha256_file,
)
from iris_tooling.domains.public_text.acceptance_rules import evaluate_threshold
from iris_tooling.domains.public_text.acceptance_validation import (
    validate_official_attempt,
)
from iris_tooling.domains.public_text.acceptance_emission import write_once_or_same

__all__ = (
    "DISPOSITION_CLASSES", "FOUNDATION_SCHEMA_VERSION", "FoundationContractError",
    "NATURALIZATION_COMPILER_IMPLEMENTATION_FILES", "PHASE0_REQUIRED_VCS_CONSUMERS",
    "REPO_ROOT", "TEXT_CONSTITUENT_IDENTITY_ALGORITHM_ID", "build_compiler_identity",
    "build_foundation",
    "build_protected_snapshot_identity_from_bytes",
    "build_protected_snapshot_present_row_from_bytes",
    "build_text_constituent_identity_from_bytes", "canonical_hash",
    "compute_candidate_metric_snapshot", "evaluate_threshold", "handoff_artifact_path",
    "head_text_constituent_record", "human_review_blocker_count", "is_ignored",
    "is_tracked", "load_json_strict", "normalize_text_line_endings",
    "phase0_required_vcs_preflight", "pretty_json_bytes", "repo_relative",
    "run_official_mode", "sha256_file", "validate_candidate_handoff",
    "validate_foundation", "validate_official_attempt", "write_once_or_same",
)
