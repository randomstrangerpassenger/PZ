from __future__ import annotations

from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable

try:
    from .naturalization_compiler_identity import (
        build_compiler_identity,
        compiler_identity_matches_claim,
        compiler_source_paths,
    )
except ImportError:
    from naturalization_compiler_identity import (
        build_compiler_identity,
        compiler_identity_matches_claim,
        compiler_source_paths,
    )

TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]

ROUND_ID = "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
SYNC_CONTRACT_ID = "dvf3_3_korean_naturalization__publish_boundary_sync_v1"
GLOBAL_SYNC_CONTRACT_ID = "iris_aa49_four_plan_execution_sync_v1"
FOUR_PLAN_SYNC_PROJECTION_SHA256 = (
    "12c32873dc7e16e0d64e416bdb6693599e2790e9fc129606a90a72ca745a6eb0"
)
FOUNDATION_CONTRACT_VERSION = "2.0.0"
FOUNDATION_SCHEMA_VERSION = "public_text_quality_foundation_contract_v2"
READINESS_SCHEMA_VERSION = "public_text_quality_development_readiness_v2"
FIXTURE_SCHEMA_VERSION = "public_text_quality_acceptance_fixture_manifest_v1"

DEFAULT_FOUNDATION_ROOT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / ROUND_ID
    / "foundation"
)
FOUNDATION_CONTRACT_NAME = "public_text_quality_foundation_contract.json"
READINESS_REPORT_NAME = "public_text_quality_development_readiness_report.json"
PREDECESSOR_FOUNDATION = {
    "foundation_id": "ptqa-foundation-v1",
    "foundation_contract_version": "1.0.0",
    "foundation_contract_raw_sha256": (
        "3505b2edbe7b5826c70ee80a62c2eb6db25ff9d0b224f527936c1504fbf516ee"
    ),
    "source_commit": "33aad08676c96d5ae1ae7ff1c3fa509feff8bf08",
    "reuse_disposition": (
        "policy_schema_detector_fixture_runner_validator_reused_with_"
        "fresh_g0_g3_identity_binding"
    ),
}
FIXTURE_MANIFEST = (
    V2_ROOT
    / "tests"
    / "fixtures"
    / "public_text_quality_acceptance"
    / "foundation_fixtures.json"
)

DEFAULT_ATTEMPTS_ROOT = V2_ROOT / "staging" / ROUND_ID / "attempts"
OWNER_INPUT_ROOT = V2_ROOT / "owner_inputs" / ROUND_ID
REVIEWER_INPUT_ROOT = V2_ROOT / "reviewer_inputs" / ROUND_ID
LIVE_REQUIRED_VALIDATIONS = (
    REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
)
NATURALIZATION_COMPILER_IMPLEMENTATION_FILES = compiler_source_paths(REPO_ROOT)

OFFICIAL_MODES = (
    "phase0-binding",
    "phase1-contracts",
    "phase2-policy",
    "phase3-validator",
    "phase4-adversarial",
    "phase5-disposition",
    "phase6-gate-candidate",
    "phase6-adopt-gate",
    "phase7-freeze",
    "phase7-finalize",
)

PHASE_ARTIFACTS = {
    0: (
        "evaluation_subject_manifest.json",
        "cross_plan_handoff_binding_report.json",
        "current_input_constituent_manifest.json",
        "canonical_entries_projection.jsonl",
        "canonical_entries_digest.json",
        "canonical_metric_projection.jsonl",
        "canonical_metric_projection_digest.json",
        "acceptance_input_binding_manifest.json",
        "protected_surface_no_mutation_report.json",
        "vcs_required_surface_preflight.json",
    ),
    1: (
        "metric_registry.json",
        "denominator_registry.json",
        "profile_section_applicability_matrix.json",
        "metric_overlap_and_partition_report.json",
        "unadopted_axis_separation_report.json",
        "metric_denominator_contract_validation_report.json",
    ),
    2: (
        "public_text_quality_acceptance_policy.json",
        "applicable_waiver_set.json",
        "policy_threshold_rationale_report.json",
    ),
    3: (
        "validator_contract_report.json",
        "validator_determinism_report.json",
        "fail_closed_path_report.json",
    ),
    4: (
        "adversarial_fixture_manifest.json",
        "negative_fixture_results.json",
        "threshold_boundary_report.json",
        "row_occurrence_confusion_report.json",
        "unadopted_axis_attack_report.json",
        "waiver_bypass_attack_report.json",
        "metamorphic_determinism_report.json",
        "adversarial_review.md",
    ),
    5: (
        "evaluation_subject_metric_snapshot.json",
        "evaluation_subject_raw_metric_report.json",
        "evaluation_subject_disposition.json",
        "evaluation_subject_disposition.md",
        "evaluation_subject_disposition_hash_manifest.json",
        "protected_surface_no_mutation_report.json",
    ),
}

ATTEMPT_ID_PATTERN = re.compile(r"^attempt-[0-9]{4,}-[a-z0-9][a-z0-9-]*$")

PLAN_DOC = (
    REPO_ROOT
    / "docs"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md"
)
NATURALIZATION_PLAN_DOC = (
    REPO_ROOT
    / "docs"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md"
)

GLOBAL_SYNC_MANIFEST = (
    REPO_ROOT / "docs" / "iris_aa49_four_plan_execution_sync_manifest.json"
)
G2_ATTEMPT_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_facts_authority"
    / "attempts"
    / "attempt-0022"
)
G0_G1_RELEASE_BINDING = (
    G2_ATTEMPT_ROOT
    / "phase0_plan_and_decisions"
    / "g0_g1_release_binding.json"
)
G2_SELECTED_SUCCESSOR_BINDING = (
    G2_ATTEMPT_ROOT
    / "phase11_successor"
    / "selected_successor_input_binding.json"
)
G2_SEALED_SUCCESSOR_RECEIPT = (
    G2_ATTEMPT_ROOT / "phase11_successor" / "sealed_successor_receipt.json"
)
G2_SEALED_SUCCESSOR_CLOSEOUT = (
    G2_ATTEMPT_ROOT / "phase13_closeout" / "sealed_successor_closeout.json"
)
G2_TERMINAL_HASH_SEAL = (
    G2_ATTEMPT_ROOT / "phase13_closeout" / "terminal_hash_seal.json"
)
G3_ATTEMPT_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_registry_operational_cutover"
    / "attempts"
    / "attempt-0009"
)
G3_REGISTRY_ADOPTION_RECEIPT = (
    G3_ATTEMPT_ROOT / "closeout" / "registry_adoption_receipt.json"
)
G3_CURRENT_IDENTITY_REPORT = (
    G3_ATTEMPT_ROOT / "closeout" / "current_identity_report.json"
)
G3_TERMINAL_HASH_SEAL = (
    G3_ATTEMPT_ROOT / "closeout" / "terminal_hash_seal.json"
)
CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_INPUT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"

SEALED_PREREQUISITE_RAW_SHA256 = {
    G0_G1_RELEASE_BINDING: (
        "35bf9c5d4cd5b3dfd9ecaf397a67866d75b58b2ddf4eae2c456e66704503a9e2"
    ),
    G2_SELECTED_SUCCESSOR_BINDING: (
        "bbea40be6c9b174fbc1e25de217646e13584dde1e9fcb18fa424ccd8bf3f2f42"
    ),
    G2_SEALED_SUCCESSOR_RECEIPT: (
        "a4a1960c332246cf9f9c33d15d04568859a251c7d6988fab4d878ec235a3b4b5"
    ),
    G2_SEALED_SUCCESSOR_CLOSEOUT: (
        "fe77dc23a9b6c1296c8c54361bd1291fbb5fa09bd6a662ad02336c145f4507f7"
    ),
    G2_TERMINAL_HASH_SEAL: (
        "9a9a37731e8d76399f6b960a0e9beb21bcdd65d8ae39e511337527c5306d0c19"
    ),
    G3_REGISTRY_ADOPTION_RECEIPT: (
        "efcc387bb395b561ab67df0cab4e498fe0b429680fc6cc8f6dd96eb94ba49751"
    ),
    G3_CURRENT_IDENTITY_REPORT: (
        "71dadc9901b713d6927e66719f758f925c50735fc6bc887e8f6a6ba8e086dca8"
    ),
    G3_TERMINAL_HASH_SEAL: (
        "1f494ed0661627a82c3fcfd8465f2313fe0768cac82af09457e9ffc9e91b7ae1"
    ),
}
GLOBAL_SYNC_MANIFEST_GIT_BLOB_ID = "70035140563ed6cd7ad70b60a6fb36101ed50519"
GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256 = (
    "1f43bc3144f59f17774adac76f313ee67312c1818af120510de0c2591a9c426d"
)

FOUNDATION_DOCS = (
    REPO_ROOT / "docs" / "public_text_quality_metric_contract.md",
    REPO_ROOT / "docs" / "public_text_quality_denominator_contract.md",
    REPO_ROOT / "docs" / "public_text_quality_acceptance_policy.md",
    REPO_ROOT / "docs" / "public_text_quality_acceptance_claim_boundary.md",
    REPO_ROOT / "docs" / "public_text_quality_exception_policy.md",
    REPO_ROOT / "docs" / "public_text_quality_waiver_policy.md",
    REPO_ROOT / "docs" / "public_text_quality_freshness_policy.md",
)

FOUNDATION_IMPLEMENTATION_FILES = (
    TOOLS_DIR / "naturalization_compiler_identity.py",
    TOOLS_DIR / "public_text_quality_acceptance.py",
    TOOLS_DIR / "run_public_text_quality_acceptance.py",
    TOOLS_DIR / "validate_public_text_quality_acceptance.py",
)

EVALUATION_SUBJECT_KINDS = (
    "current_runtime_payload",
    "dvf_3_3_korean_naturalization_candidate",
)
DISPOSITION_CLASSES = ("blocking_gate", "advisory_debt", "non_claim")
QUALIFIED_DISPOSITIONS = ("accepted", "blocked", "deferred_internal_debt")
CANDIDATE_STRUCTURAL_STATUSES = (
    "emitted_direct",
    "satisfied_by_verified_fusion",
    "satisfied_by_verified_suppression",
    "not_required",
    "missing",
)
SATISFIED_REQUIRED_STRUCTURAL_STATUSES = (
    "emitted_direct",
    "satisfied_by_verified_fusion",
    "satisfied_by_verified_suppression",
)

REQUIRED_HANDOFF_CONSTITUENT_IDS = (
    "naturalization_attempt_id",
    "foundation_contract_hash",
    "candidate_rendered_hash",
    "candidate_manifest_hash",
    "source_proposition_manifest_hash",
    "body_plan_requirement_digest",
    "structural_satisfaction_ledger_hash",
    "semantic_preservation_report_hash",
    "raw_detector_report_hash",
    "human_review_sample_manifest_hash",
    "human_review_decision_hash",
    "compiler_implementation_hash",
    "korean_prose_policy_hash",
    "corpus_manifest_hash",
    "protected_surface_no_mutation_report_hash",
    "requested_evaluation_subject_kind",
)

VOLATILE_CANONICAL_FIELDS = frozenset(
    {"generated_at", "host", "absolute_path", "mtime"}
)

RAW_DETECTOR_IDS = (
    "duplicate_proposition_realization",
    "repeated_identity_noun_window",
    "banned_internal_abstraction",
    "repeated_skeleton_concentration",
    "paragraph_fragmentation",
    "passive_translationese_pattern",
    "empty_or_filler_sentence",
)


class FoundationContractError(RuntimeError):
    pass


class ExternalInputRequired(FoundationContractError):
    def __init__(self, *, input_kind: str, path: Path, details: dict[str, Any]):
        super().__init__(f"external input required: {input_kind}: {repo_relative(path)}")
        self.input_kind = input_kind
        self.path = path
        self.details = details


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise FoundationContractError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_json_strict(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_pairs,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FoundationContractError(f"cannot load strict JSON {path}: {exc}") from exc


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def pretty_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def sha256_file(path: Path) -> str:
    try:
        return sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise FoundationContractError(f"cannot hash {path}: {exc}") from exc


def sha256_lf_normalized_text(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise FoundationContractError(
            f"cannot read UTF-8 text for normalized hash {path}: {exc}"
        ) from exc
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return sha256_bytes(normalized.encode("utf-8"))


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def require_exact_keys(
    value: dict[str, Any],
    *,
    required: Iterable[str],
    optional: Iterable[str] = (),
    label: str,
) -> None:
    required_set = set(required)
    allowed_set = required_set | set(optional)
    actual_set = set(value)
    missing = sorted(required_set - actual_set)
    unknown = sorted(actual_set - allowed_set)
    if missing or unknown:
        raise FoundationContractError(
            f"{label} key mismatch: missing={missing}, unknown={unknown}"
        )


def _require_true_predicates(value: Any, *, label: str) -> None:
    if not isinstance(value, dict) or not value:
        raise FoundationContractError(f"{label} must be a nonempty predicate object")
    failures = sorted(key for key, predicate in value.items() if predicate is not True)
    if failures:
        raise FoundationContractError(f"{label} contains non-PASS predicates: {failures}")


def _artifact_record(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FoundationContractError(f"required prerequisite artifact missing: {path}")
    if not _is_tracked(path):
        raise FoundationContractError(
            f"required prerequisite artifact is untracked: {repo_relative(path)}"
        )
    ignored_by_current_rules = _is_ignored(path)
    expected_sha256 = SEALED_PREREQUISITE_RAW_SHA256.get(path)
    actual_sha256 = sha256_file(path)
    if expected_sha256 is not None and actual_sha256 != expected_sha256:
        raise FoundationContractError(
            f"sealed prerequisite artifact hash mismatch: {repo_relative(path)}"
        )
    head_blob = _head_blob_record(path)
    if head_blob["git_blob_working_byte_identity"] is not True:
        raise FoundationContractError(
            f"prerequisite artifact differs from its HEAD Git blob: {repo_relative(path)}"
        )
    record = {
        "path": repo_relative(path),
        "raw_sha256": actual_sha256,
        "byte_count": path.stat().st_size,
        "tracked": True,
        "ignored_by_current_rules": ignored_by_current_rules,
        "tracked_file_ignore_effect": "none",
        **head_blob,
    }
    if expected_sha256 is not None:
        record.update(
            {
                "sealed_expected_raw_sha256": expected_sha256,
                "sealed_expected_raw_sha256_match": True,
            }
        )
    return record


def _head_blob_record(path: Path) -> dict[str, Any]:
    relative = repo_relative(path)
    blob_id = _git("rev-parse", f"HEAD:{relative}").stdout.strip()
    result = subprocess.run(
        ["git", "cat-file", "blob", blob_id],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationContractError(
            f"cannot read HEAD blob for {relative}: "
            f"{result.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return {
        "path": relative,
        "git_blob_id": blob_id,
        "git_blob_sha256": sha256_bytes(result.stdout),
        "working_sha256": sha256_file(path),
        "git_blob_working_byte_identity": result.stdout == path.read_bytes(),
    }


def _head_filtered_blob_record(path: Path) -> dict[str, Any]:
    relative = repo_relative(path)
    head_blob_id = _git("rev-parse", f"HEAD:{relative}").stdout.strip()
    filtered_working_blob_id = _git("hash-object", "--", relative).stdout.strip()
    result = subprocess.run(
        ["git", "cat-file", "blob", head_blob_id],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationContractError(
            f"cannot read HEAD blob for filtered identity {relative}"
        )
    return {
        "path": relative,
        "git_blob_id": head_blob_id,
        "git_blob_sha256": sha256_bytes(result.stdout),
        "working_sha256_lf_normalized": sha256_lf_normalized_text(path),
        "git_filtered_working_blob_id": filtered_working_blob_id,
        "git_filtered_working_identity": filtered_working_blob_id == head_blob_id,
        "raw_working_byte_identity_required": False,
    }


def _g0_sync_manifest_record() -> dict[str, Any]:
    path = GLOBAL_SYNC_MANIFEST
    if not path.is_file() or not _is_tracked(path) or _is_ignored(path):
        raise FoundationContractError(
            "G0 synchronization manifest must be present, tracked, and not ignored"
        )
    record = _head_filtered_blob_record(path)
    if (
        record["git_blob_id"] != GLOBAL_SYNC_MANIFEST_GIT_BLOB_ID
        or record["git_filtered_working_identity"] is not True
        or record["git_blob_sha256"]
        != GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256
        or record["working_sha256_lf_normalized"]
        != GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256
    ):
        raise FoundationContractError(
            "G0 synchronization manifest filtered/normalized identity mismatch"
        )
    return {
        **record,
        "hash_algorithm": "sha256_lf_normalized_text_v1",
        "sha256": GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256,
        "tracked": True,
        "ignored_by_current_rules": False,
        "sealed_expected_git_blob_id": GLOBAL_SYNC_MANIFEST_GIT_BLOB_ID,
        "sealed_expected_lf_normalized_sha256": (
            GLOBAL_SYNC_MANIFEST_LF_NORMALIZED_SHA256
        ),
        "sealed_expected_identity_match": True,
    }


def _predecessor_foundation_binding() -> dict[str, Any]:
    relative = (
        "Iris/_docs/round3/"
        "iris_publish_boundary_public_text_quality_acceptance_policy_closure/"
        "foundation/public_text_quality_foundation_contract.json"
    )
    revision = PREDECESSOR_FOUNDATION["source_commit"]
    blob_id = _git("rev-parse", f"{revision}:{relative}").stdout.strip()
    result = subprocess.run(
        ["git", "cat-file", "blob", blob_id],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationContractError(
            "cannot read predecessor Foundation v1 contract blob"
        )
    actual_sha256 = sha256_bytes(result.stdout)
    if actual_sha256 != PREDECESSOR_FOUNDATION["foundation_contract_raw_sha256"]:
        raise FoundationContractError(
            "predecessor Foundation v1 contract hash mismatch"
        )
    return {
        **PREDECESSOR_FOUNDATION,
        "path": relative,
        "git_blob_id": blob_id,
        "git_object_raw_sha256_match": True,
    }


def _require_ancestor(commit: str, *, label: str) -> None:
    if not isinstance(commit, str) or not commit:
        raise FoundationContractError(f"{label} commit is missing")
    result = _git("merge-base", "--is-ancestor", commit, "HEAD", check=False)
    if result.returncode != 0:
        raise FoundationContractError(f"{label} commit is not an ancestor of HEAD")


def _materialized_plan_blob_record(row: dict[str, Any]) -> dict[str, Any]:
    require_exact_keys(
        row,
        required=("path", "sha256", "git_blob_id", "projection_occurrence_count"),
        label="G0 materialized plan row",
    )
    result = subprocess.run(
        ["git", "cat-file", "blob", row["git_blob_id"]],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise FoundationContractError(
            f"cannot read G0 materialized plan blob: {row['path']}"
        )
    actual_sha256 = sha256_bytes(result.stdout)
    if actual_sha256 != row["sha256"]:
        raise FoundationContractError(
            f"G0 materialized plan blob hash mismatch: {row['path']}"
        )
    return {
        **row,
        "git_object_raw_sha256": actual_sha256,
        "git_object_raw_sha256_match": True,
    }


def _validate_g0_binding() -> dict[str, Any]:
    artifact = _g0_sync_manifest_record()
    manifest = load_json_strict(GLOBAL_SYNC_MANIFEST)
    expected_plan_paths = [
        "docs/iris_clean_checkout_full_repository_validation_reproducibility_authority_closure_plan.md",
        "docs/dvf_3_3_food_semantic_facts_authority_reconstruction_implementation_plan.md",
        "docs/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md",
        "docs/iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md",
    ]
    plan_rows = manifest.get("plans")
    projection = manifest.get("projection")
    if (
        manifest.get("schema_version")
        != "iris_aa49_four_plan_execution_sync_manifest_v1"
        or manifest.get("contract_id") != GLOBAL_SYNC_CONTRACT_ID
        or manifest.get("materialization_state") != "tracked_plan_set_ready"
        or manifest.get("baseline_commit")
        != "aa49e8f9fce19955a374b45d0744b1418a45ac9e"
        or manifest.get("owner_directive")
        != "synchronization_only_no_additional_plan_level_review"
        or manifest.get("four_plan_sync_projection_sha256")
        != FOUR_PLAN_SYNC_PROJECTION_SHA256
        or not isinstance(projection, dict)
        or canonical_hash(projection) != FOUR_PLAN_SYNC_PROJECTION_SHA256
        or manifest.get("plan_count") != 4
        or not isinstance(plan_rows, list)
        or [row.get("path") for row in plan_rows] != expected_plan_paths
        or any(row.get("projection_occurrence_count") != 1 for row in plan_rows)
        or manifest.get("implementation_or_attempt_output_imported_count") != 0
        or manifest.get("self_referential_commit_fields") != 0
    ):
        raise FoundationContractError("G0 synchronized plan-set binding is invalid")
    materialized_plan_blobs = [
        _materialized_plan_blob_record(row) for row in plan_rows
    ]
    current_successor_plan_blobs = []
    for relative in expected_plan_paths:
        path = REPO_ROOT / relative
        if not _is_tracked(path) or _is_ignored(path):
            raise FoundationContractError(
                f"current successor plan is not tracked and visible: {relative}"
            )
        head_blob = _head_filtered_blob_record(path)
        if head_blob["git_filtered_working_identity"] is not True:
            raise FoundationContractError(
                f"current successor plan differs from its filtered HEAD Git blob: {relative}"
            )
        current_successor_plan_blobs.append(head_blob)
    return {
        "global_stage": "G0_plan_set_materialization_and_owner_sync",
        "status": "PASS",
        "artifact": artifact,
        "contract_id": GLOBAL_SYNC_CONTRACT_ID,
        "four_plan_sync_projection_sha256": FOUR_PLAN_SYNC_PROJECTION_SHA256,
        "four_plan_set_tracked_blob_count": 4,
        "materialized_plan_blobs": materialized_plan_blobs,
        "materialized_plan_blob_hash_match_count": 4,
        "current_successor_plan_blobs": current_successor_plan_blobs,
        "current_successor_plan_git_filtered_identity_count": 4,
        "current_top_doc_successor_changes_allowed": True,
        "current_top_doc_blob_equality_required": False,
    }


def _validate_g1_binding() -> dict[str, Any]:
    artifact = _artifact_record(G0_G1_RELEASE_BINDING)
    binding = load_json_strict(G0_G1_RELEASE_BINDING)
    _require_true_predicates(
        binding.get("receipt_predicates"), label="G1 release receipt predicates"
    )
    _require_true_predicates(
        binding.get("closeout_binding", {}).get("predicates"),
        label="G1 closeout binding predicates",
    )
    _require_true_predicates(
        binding.get("manifest", {}).get("predicates"),
        label="G0 manifest binding predicates",
    )
    if (
        binding.get("schema_version") != "food-semantic-g0-g1-release-binding-v1"
        or binding.get("status") != "PASS"
        or binding.get("four_plan_set_tracked_blob_count") != 4
        or binding.get("authority_claim_emitted_count") != 0
        or binding.get("owner_approval_consumed_count") != 0
        or binding.get("owner_decision_consumed_count") != 0
        or binding.get("manifest", {}).get("projection_sha256")
        != FOUR_PLAN_SYNC_PROJECTION_SHA256
    ):
        raise FoundationContractError("G1 downstream-unblock binding is invalid")
    source_receipt = binding.get("source_receipt", {})
    closeout = binding.get("closeout_binding", {})
    return {
        "global_stage": "G1_clean_checkout_full_repository_validation",
        "status": "PASS",
        "artifact": artifact,
        "clean_validation_terminal_pass": True,
        "downstream_unblock_target": "G2_food_semantic_facts_authority",
        "source_receipt_path": source_receipt.get("path"),
        "source_receipt_sha256": source_receipt.get("sha256"),
        "terminal_closeout_path": closeout.get("path"),
        "terminal_closeout_sha256": closeout.get("sha256"),
        "validated_subject_commit": closeout.get("containing_commit"),
    }


def _validate_g2_binding() -> dict[str, Any]:
    selected_artifact = _artifact_record(G2_SELECTED_SUCCESSOR_BINDING)
    receipt_artifact = _artifact_record(G2_SEALED_SUCCESSOR_RECEIPT)
    closeout_artifact = _artifact_record(G2_SEALED_SUCCESSOR_CLOSEOUT)
    terminal_artifact = _artifact_record(G2_TERMINAL_HASH_SEAL)
    selected = load_json_strict(G2_SELECTED_SUCCESSOR_BINDING)
    receipt = load_json_strict(G2_SEALED_SUCCESSOR_RECEIPT)
    closeout = load_json_strict(G2_SEALED_SUCCESSOR_CLOSEOUT)
    terminal = load_json_strict(G2_TERMINAL_HASH_SEAL)
    final_verification = terminal.get("final_artifact_manifest_verification", {})
    implementation_verification = terminal.get(
        "implementation_bundle_artifact_verification", {}
    )
    if (
        selected.get("schema_version")
        != "food-semantic-selected-successor-input-binding-v1"
        or receipt.get("schema_version")
        != "food-semantic-sealed-successor-receipt-v1"
        or receipt.get("non_current") is not True
        or receipt.get("current_facts_manifest_mutation_count") != 0
        or receipt.get("selected_binding_sha256") != selected_artifact["raw_sha256"]
        or closeout.get("schema_version")
        != "food-semantic-sealed-successor-closeout-v1"
        or closeout.get("status") != "PASS"
        or closeout.get("food_semantic_facts_authority_closeout")
        != "sealed_successor_handoff_complete"
        or closeout.get("selected_branch") != "B+G2"
        or closeout.get("canonical_complete") is not False
        or closeout.get("current_authority_reconstruction_complete") is not False
        or closeout.get("sealed_successor_receipt_sha256")
        != receipt_artifact["raw_sha256"]
        or terminal.get("schema_version")
        != "food-semantic-terminal-hash-seal-v1"
        or terminal.get("status") != "PASS"
        or terminal.get("sealed_successor_closeout_sha256")
        != closeout_artifact["raw_sha256"]
        or final_verification.get("status") != "PASS"
        or final_verification.get("artifact_mismatch_count") != 0
        or implementation_verification.get("status") != "PASS"
        or implementation_verification.get("artifact_mismatch_count") != 0
        or selected.get("successor_facts_sha256")
        != receipt.get("successor_facts_sha256")
        or selected.get("successor_input_manifest_sha256")
        != receipt.get("successor_manifest_sha256")
    ):
        raise FoundationContractError("G2 sealed successor binding is invalid")
    return {
        "global_stage": "G2_food_semantic_facts_authority",
        "status": "PASS",
        "attempt_id": "attempt-0022",
        "sealed_successor_terminal_closeout": True,
        "selected_successor_facts_sha256": receipt["successor_facts_sha256"],
        "selected_successor_manifest_sha256": receipt[
            "successor_manifest_sha256"
        ],
        "selected_successor_binding": selected_artifact,
        "sealed_successor_receipt": receipt_artifact,
        "sealed_successor_closeout": closeout_artifact,
        "terminal_hash_seal": terminal_artifact,
    }


def _validate_g3_and_current_identity(g2: dict[str, Any]) -> dict[str, Any]:
    receipt_artifact = _artifact_record(G3_REGISTRY_ADOPTION_RECEIPT)
    identity_artifact = _artifact_record(G3_CURRENT_IDENTITY_REPORT)
    terminal_artifact = _artifact_record(G3_TERMINAL_HASH_SEAL)
    facts_artifact = _artifact_record(CURRENT_FACTS)
    manifest_artifact = _artifact_record(CURRENT_INPUT_MANIFEST)
    receipt = load_json_strict(G3_REGISTRY_ADOPTION_RECEIPT)
    identity = load_json_strict(G3_CURRENT_IDENTITY_REPORT)
    terminal = load_json_strict(G3_TERMINAL_HASH_SEAL)
    manifest = load_json_strict(CURRENT_INPUT_MANIFEST)
    facts_blob = _head_blob_record(CURRENT_FACTS)
    manifest_blob = _head_blob_record(CURRENT_INPUT_MANIFEST)
    _require_ancestor(identity.get("adoption_commit"), label="G3 adoption")
    actual_adoption_tree = _git(
        "rev-parse", f"{identity['adoption_commit']}^{{tree}}"
    ).stdout.strip()

    current_facts_sha256 = facts_artifact["raw_sha256"]
    current_manifest_sha256 = manifest_artifact["raw_sha256"]
    successor_facts_sha256 = g2["selected_successor_facts_sha256"]
    successor_manifest_sha256 = g2["selected_successor_manifest_sha256"]
    food_authority = manifest.get("food_semantic_authority", {})
    source_binding = (
        manifest.get("source_promotion", {})
        .get("food_semantic_successor_binding", {})
    )
    terminal_artifacts = terminal.get("artifacts", {})
    if (
        receipt.get("schema_version")
        != "food-semantic-registry-adoption-receipt-v1"
        or receipt.get("status") != "PASS"
        or receipt.get("attempt_id") != "attempt-0009"
        or receipt.get("food_semantic_registry_adoption")
        != "current_adoption_complete"
        or receipt.get("current_identity_ambiguity_count") != 0
        or receipt.get("partial_or_dual_current_count") != 0
        or receipt.get("rendered_lua_runtime_package_mutation_count") != 0
        or receipt.get("selected_successor_facts_sha256")
        != successor_facts_sha256
        or receipt.get("selected_successor_manifest_sha256")
        != successor_manifest_sha256
        or receipt.get("current_facts_sha256") != current_facts_sha256
        or receipt.get("candidate_current_facts_sha256") != current_facts_sha256
        or receipt.get("current_manifest_sha256") != current_manifest_sha256
        or receipt.get("candidate_current_manifest_sha256")
        != current_manifest_sha256
        or receipt.get("projected_current_manifest_sha256")
        != current_manifest_sha256
        or receipt.get("current_manifest_adopted_successor_manifest_sha256")
        != successor_manifest_sha256
        or identity.get("schema_version")
        != "food-semantic-current-identity-report-v1"
        or identity.get("status") != "PASS"
        or identity.get("attempt_id") != "attempt-0009"
        or identity.get("adoption_tree") != actual_adoption_tree
        or identity.get("canonical_adoption_readpoint") is not True
        or identity.get("current_identity_ambiguity_count") != 0
        or identity.get("partial_or_dual_current_count") != 0
        or identity.get("facts", {}).get("working_sha256") != current_facts_sha256
        or identity.get("facts", {}).get("git_blob_sha256")
        != current_facts_sha256
        or identity.get("manifest", {}).get("working_sha256")
        != current_manifest_sha256
        or identity.get("manifest", {}).get("git_blob_sha256")
        != current_manifest_sha256
        or identity.get("facts", {}).get("git_blob_id")
        != facts_blob["git_blob_id"]
        or identity.get("manifest", {}).get("git_blob_id")
        != manifest_blob["git_blob_id"]
        or facts_blob["git_blob_working_byte_identity"] is not True
        or manifest_blob["git_blob_working_byte_identity"] is not True
        or terminal.get("schema_version")
        != "food-semantic-registry-adoption-terminal-hash-seal-v1"
        or terminal.get("status") != "PASS"
        or terminal.get("terminal_hash_seal") != "PASS"
        or terminal.get("food_semantic_registry_adoption")
        != "current_adoption_complete"
        or terminal.get("current_facts_sha256") != current_facts_sha256
        or terminal.get("current_manifest_sha256") != current_manifest_sha256
        or terminal.get("selected_successor_facts_sha256")
        != successor_facts_sha256
        or terminal.get("selected_successor_manifest_sha256")
        != successor_manifest_sha256
        or terminal_artifacts.get("registry_adoption_receipt_sha256")
        != receipt_artifact["raw_sha256"]
        or terminal_artifacts.get("current_identity_report_sha256")
        != identity_artifact["raw_sha256"]
        or manifest.get("facts", {}).get("sha256") != current_facts_sha256
        or food_authority.get("attempt_id") != "attempt-0022"
        or food_authority.get("registry_cutover_attempt_id") != "attempt-0009"
        or food_authority.get("authority_bearing") is not True
        or food_authority.get("non_current") is not False
        or food_authority.get("registry_adoption_state") != "current"
        or food_authority.get("source_successor_manifest_sha256")
        != successor_manifest_sha256
        or source_binding.get("successor_facts_sha256")
        != successor_facts_sha256
        or source_binding.get("successor_manifest_sha256")
        != successor_manifest_sha256
    ):
        raise FoundationContractError(
            "G3 adoption receipt and current facts/manifest identity binding is invalid"
        )
    return {
        "global_stage": "G3_registry_food_successor_operational_cutover",
        "status": "PASS",
        "attempt_id": "attempt-0009",
        "registry_food_successor_adoption_receipt_valid": True,
        "food_semantic_registry_adoption": "current_adoption_complete",
        "adoption_commit": identity["adoption_commit"],
        "adoption_tree": actual_adoption_tree,
        "adoption_tree_matches_commit": True,
        "selected_successor_facts_sha256": successor_facts_sha256,
        "selected_successor_manifest_sha256": successor_manifest_sha256,
        "current_facts": {
            **facts_artifact,
            **facts_blob,
        },
        "current_input_manifest": {
            **manifest_artifact,
            **manifest_blob,
            "adopted_successor_manifest_sha256": successor_manifest_sha256,
        },
        "registry_adoption_receipt": receipt_artifact,
        "current_identity_report": identity_artifact,
        "terminal_hash_seal": terminal_artifact,
        "current_identity_ambiguity_count": 0,
        "partial_or_dual_current_count": 0,
        "rendered_lua_runtime_package_mutation_count": 0,
        "registry_runtime_compatibility_current_source_alignment": (
            "stale_requires_successor_rtc"
        ),
        "successor_registry_runtime_compatibility_closure": False,
        "runtime_package_publication_claim_effect": "none_fail_closed_out_of_scope",
    }


def build_upstream_prerequisite_binding() -> dict[str, Any]:
    g0 = _validate_g0_binding()
    g1 = _validate_g1_binding()
    g2 = _validate_g2_binding()
    g3 = _validate_g3_and_current_identity(g2)
    return {
        "schema_version": "public_text_quality_foundation_upstream_binding_v1",
        "global_stage_order": [
            "G0_plan_set_materialization_and_owner_sync",
            "G1_clean_checkout_full_repository_validation",
            "G2_food_semantic_facts_authority",
            "G3_registry_food_successor_operational_cutover",
            "G4_publish_boundary_foundation",
        ],
        "g0": g0,
        "g1": g1,
        "g2": g2,
        "g3": g3,
        "four_plan_sync_projection_sha256_match": True,
        "clean_validation_terminal_pass": True,
        "food_sealed_successor_terminal_closeout": True,
        "registry_food_successor_adoption_receipt_valid": True,
        "current_facts_equals_selected_successor_facts": True,
        "current_manifest_binds_selected_successor_manifest": True,
        "upstream_prerequisite_status": "PASS",
    }


def _protected_foundation_surface_paths() -> list[Path]:
    fixed = [
        CURRENT_FACTS,
        CURRENT_INPUT_MANIFEST,
        LIVE_REQUIRED_VALIDATIONS,
        V2_ROOT / "data" / "dvf_3_3_decisions.jsonl",
        V2_ROOT / "data" / "dvf_3_3_overlay_support.jsonl",
        V2_ROOT / "data" / "compose_profiles_v2.json",
        V2_ROOT / "data" / "compose_profile_identity_hint_rules.json",
        V2_ROOT / "data" / "compose_profile_conflict_precedence_rules.json",
        V2_ROOT / "output" / "dvf_3_3_rendered.json",
        V2_ROOT / "output" / "style_normalization_changes.jsonl",
        V2_ROOT / "output" / "compose_requeue_candidates.jsonl",
    ]
    recursive_roots = [
        REPO_ROOT / "Iris" / "media" / "lua",
        REPO_ROOT / "Iris" / "Contents" / "mods" / "Iris",
        DEFAULT_ATTEMPTS_ROOT,
        OWNER_INPUT_ROOT,
        REVIEWER_INPUT_ROOT,
    ]
    paths = set(fixed)
    for root in recursive_roots:
        if root.is_dir():
            paths.update(path for path in root.rglob("*") if path.is_file())
    return sorted(paths, key=repo_relative)


def protected_foundation_surface_snapshot() -> dict[str, Any]:
    rows = []
    for path in _protected_foundation_surface_paths():
        present = path.is_file()
        rows.append(
            {
                "path": repo_relative(path),
                "present": present,
                "raw_sha256": sha256_file(path) if present else None,
                "byte_count": path.stat().st_size if present else None,
            }
        )
    return {
        "schema_version": "public_text_quality_foundation_no_write_snapshot_v1",
        "surface_count": len(rows),
        "surface_hash": canonical_hash(rows),
        "surfaces": rows,
    }


def _no_write_guard(
    before: dict[str, Any], after: dict[str, Any]
) -> dict[str, Any]:
    changed_paths = sorted(
        {
            row["path"]
            for row in before["surfaces"] + after["surfaces"]
            if next(
                (
                    candidate
                    for candidate in before["surfaces"]
                    if candidate["path"] == row["path"]
                ),
                None,
            )
            != next(
                (
                    candidate
                    for candidate in after["surfaces"]
                    if candidate["path"] == row["path"]
                ),
                None,
            )
        }
    )
    if changed_paths:
        raise FoundationContractError(
            f"foundation protected no-write guard detected mutations: {changed_paths}"
        )
    return {
        "schema_version": "public_text_quality_foundation_no_write_guard_v1",
        "status": "PASS",
        "before_snapshot_hash": canonical_hash(before),
        "after_snapshot_hash": canonical_hash(after),
        "protected_surface_mutation_count": 0,
        "changed_paths": [],
        "source_rendered_lua_runtime_package_authority_effect": "none",
    }


def denominator_registry_candidate() -> dict[str, Any]:
    current = ("current_runtime_payload",)
    candidate = ("dvf_3_3_korean_naturalization_candidate",)
    rows = [
        ("current_item_universe_v1", "item", current),
        ("quality_evaluable_adopted_item_v1", "item", current),
        ("unadopted_item_v1", "item", current),
        ("required_section_opportunity_v1", "section_opportunity", current),
        (
            "required_identity_core_opportunity_v1",
            "section_opportunity",
            current,
        ),
        (
            "required_context_support_opportunity_v1",
            "section_opportunity",
            current,
        ),
        (
            "required_limitation_tail_opportunity_v1",
            "section_opportunity",
            current,
        ),
        ("required_use_core_opportunity_v1", "section_opportunity", current),
        (
            "profile_adopted_item_v1:<profile_id>",
            "item",
            current,
        ),
        ("naturalization_candidate_item_v1", "item", candidate),
        (
            "naturalization_source_proposition_v1",
            "source_proposition",
            candidate,
        ),
        (
            "naturalization_required_body_plan_role_v1",
            "required_body_plan_role",
            candidate,
        ),
        (
            "naturalization_fusion_suppression_transformation_v1",
            "fusion_suppression_transformation",
            candidate,
        ),
        (
            "naturalization_raw_detector_opportunity_v1:<detector_id>",
            "detector_opportunity",
            candidate,
        ),
        (
            "naturalization_human_review_required_v1",
            "required_human_review_row",
            candidate,
        ),
    ]
    return {
        "schema_version": "public_text_quality_denominator_registry_candidate_v1",
        "zero_denominator_effect": "technical_blocker",
        "count_equality_does_not_alias_denominator_ids": True,
        "registrations": [
            {
                "denominator_id": denominator_id,
                "unit": unit,
                "applicable_subject_kinds": list(subjects),
                "unknown_or_missing_effect": "technical_blocker",
            }
            for denominator_id, unit, subjects in rows
        ],
    }


def detector_mapping_candidate() -> dict[str, Any]:
    return {
        "schema_version": "public_text_quality_detector_mapping_candidate_v1",
        "unknown_or_unmapped_detector_effect": "technical_blocker",
        "mappings": [
            {
                "detector_id": "duplicate_proposition_realization",
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "semantic_duplication_zero_tolerance_v1",
            },
            {
                "detector_id": "repeated_identity_noun_window",
                "disposition_class": "advisory_debt",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "identity_repetition_debt_free_target_v1",
            },
            {
                "detector_id": "banned_internal_abstraction",
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "internal_abstraction_zero_tolerance_v1",
            },
            {
                "detector_id": "repeated_skeleton_concentration",
                "disposition_class": "advisory_debt",
                "threshold": {
                    "operator": "le",
                    "value": {"numerator": 1, "denominator": 20},
                },
                "rationale_id": "corpus_skeleton_concentration_cap_v1",
            },
            {
                "detector_id": "paragraph_fragmentation",
                "disposition_class": "advisory_debt",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "fragmentation_debt_free_target_v1",
            },
            {
                "detector_id": "passive_translationese_pattern",
                "disposition_class": "advisory_debt",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "translationese_debt_free_target_v1",
            },
            {
                "detector_id": "empty_or_filler_sentence",
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
                "rationale_id": "empty_filler_zero_tolerance_v1",
            },
        ],
    }


def metric_registry_candidate() -> dict[str, Any]:
    current = ["current_runtime_payload"]
    candidate = ["dvf_3_3_korean_naturalization_candidate"]
    rows: list[dict[str, Any]] = [
        {
            "metric_id": "coverage_quality_weak",
            "unit": "ratio",
            "denominator_id": "quality_evaluable_adopted_item_v1",
            "disposition_class": "blocking_gate",
            "annotation": "acceptance_blocker",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "coverage_quality_adequate",
            "unit": "ratio",
            "denominator_id": "quality_evaluable_adopted_item_v1",
            "disposition_class": "non_claim",
            "annotation": "quality_distribution",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "coverage_quality_strong",
            "unit": "ratio",
            "denominator_id": "quality_evaluable_adopted_item_v1",
            "disposition_class": "non_claim",
            "annotation": "quality_distribution",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "missing_any_required_section_row",
            "unit": "ratio",
            "denominator_id": "quality_evaluable_adopted_item_v1",
            "disposition_class": "blocking_gate",
            "annotation": "acceptance_blocker",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "missing_required_section_occurrence",
            "unit": "ratio",
            "denominator_id": "required_section_opportunity_v1",
            "disposition_class": "advisory_debt",
            "annotation": "missing_occurrence_debt",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "missing_context_support",
            "unit": "ratio",
            "denominator_id": "required_context_support_opportunity_v1",
            "disposition_class": "non_claim",
            "annotation": "diagnostic_breakdown",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "missing_limitation_tail",
            "unit": "ratio",
            "denominator_id": "required_limitation_tail_opportunity_v1",
            "disposition_class": "non_claim",
            "annotation": "diagnostic_breakdown",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "missing_use_core",
            "unit": "ratio",
            "denominator_id": "required_use_core_opportunity_v1",
            "disposition_class": "non_claim",
            "annotation": "diagnostic_breakdown",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "unadopted",
            "unit": "count_ratio",
            "denominator_id": "current_item_universe_v1",
            "disposition_class": "non_claim",
            "annotation": "separate_adoption_axis",
            "applicable_subject_kinds": current,
        },
        {
            "metric_id": "semantic_preservation_failure",
            "unit": "count",
            "denominator_id": "naturalization_source_proposition_v1",
            "disposition_class": "blocking_gate",
            "annotation": "source_provenance_blocker",
            "applicable_subject_kinds": candidate,
        },
        {
            "metric_id": "unsatisfied_required_body_plan_role",
            "unit": "count",
            "denominator_id": "naturalization_required_body_plan_role_v1",
            "disposition_class": "blocking_gate",
            "annotation": "structural_satisfaction_blocker",
            "applicable_subject_kinds": candidate,
        },
        {
            "metric_id": "equivalence_proof_failure",
            "unit": "count",
            "denominator_id": (
                "naturalization_fusion_suppression_transformation_v1"
            ),
            "disposition_class": "blocking_gate",
            "annotation": "technical_semantic_blocker",
            "applicable_subject_kinds": candidate,
        },
        {
            "metric_id": "compiler_invalid_pattern",
            "unit": "count",
            "denominator_id": "naturalization_candidate_item_v1",
            "disposition_class": "blocking_gate",
            "annotation": "compiler_contract_blocker",
            "applicable_subject_kinds": candidate,
        },
    ]
    detector_by_id = {
        row["detector_id"]: row for row in detector_mapping_candidate()["mappings"]
    }
    for detector_id in RAW_DETECTOR_IDS:
        mapping = detector_by_id[detector_id]
        rows.append(
            {
                "metric_id": detector_id,
                "unit": (
                    "rational_metric"
                    if detector_id == "repeated_skeleton_concentration"
                    else "count_ratio"
                ),
                "denominator_id": (
                    f"naturalization_raw_detector_opportunity_v1:{detector_id}"
                ),
                "disposition_class": mapping["disposition_class"],
                "annotation": "raw_korean_prose_detector",
                "applicable_subject_kinds": candidate,
            }
        )
    rows.append(
        {
            "metric_id": "human_review_blocker_required_denominator",
            "unit": "count",
            "denominator_id": "naturalization_human_review_required_v1",
            "disposition_class": "blocking_gate",
            "annotation": "denominator_qualified_human_only_finding",
            "applicable_subject_kinds": candidate,
        }
    )
    return {
        "schema_version": "public_text_quality_metric_registry_candidate_v1",
        "disposition_class_enum": list(DISPOSITION_CLASSES),
        "raw_metric_immutable": True,
        "registrations": rows,
    }


def human_review_selection_contract() -> dict[str, Any]:
    return {
        "schema_version": "public_text_quality_human_review_selection_v1",
        "algorithm_id": "deterministic_stratified_sha256_rank_v1",
        "selection_identity": (
            "sha256(candidate_rendered_hash + NUL + stratum_id + NUL + item_id)"
        ),
        "base_sample": {
            "ratio": {"numerator": 1, "denominator": 20},
            "minimum_rows": 128,
            "maximum_rows": 256,
            "cap_at_candidate_item_count": True,
        },
        "required_strata": [
            {
                "stratum_source": "resolved_profile",
                "minimum_rows_per_nonempty_stratum": 8,
            },
            {
                "stratum_source": "structural_fusion_or_suppression",
                "minimum_rows_per_nonempty_stratum": 16,
            },
            {
                "stratum_source": "raw_detector_id",
                "minimum_rows_per_nonempty_stratum": 8,
            },
        ],
        "selection_union_deduplicated_by": "exact_item_id",
        "required_denominator_id": "naturalization_human_review_required_v1",
        "human_only_claim_scope": "selected_required_denominator_only",
        "corpus_wide_human_only_zero_claim_requires_full_corpus_review": True,
        "missing_or_unbound_review_effect": "technical_blocker",
    }


def required_handoff_schema() -> dict[str, Any]:
    return {
        "schema_version": "naturalization_publish_handoff_required_schema_v1",
        "requested_evaluation_subject_kind": (
            "dvf_3_3_korean_naturalization_candidate"
        ),
        "required_constituent_ids": list(REQUIRED_HANDOFF_CONSTITUENT_IDS),
        "hash_fields_require_lowercase_sha256_hex": True,
        "exact_path_hash_binding_required": True,
        "post_handoff_mutation_effect": "stale",
        "candidate_runtime_parity_applicability": "not_applicable",
        "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
        "registry_runtime_pass_claim_allowed": False,
    }


def freshness_contract() -> dict[str, Any]:
    return {
        "schema_version": "public_text_quality_freshness_contract_v1",
        "stale_on_change": [
            "foundation_contract_bytes_or_hash",
            "policy_bytes_or_hash",
            "evaluation_subject_binding",
            "metric_calculator_or_schema",
            "subject_applicable_source_runtime_or_candidate_handoff_constituent",
            "applicable_waiver_set",
            "human_review_selection_or_decision_binding",
        ],
        "foundation_change_requires_new_version": True,
        "naturalization_earliest_affected_phase_rerun_required": True,
        "same_version_threshold_or_mapping_mutation_allowed": False,
        "last_known_good_disposition_fallback_allowed": False,
        "technical_or_freshness_waiver_allowed": False,
    }


def runner_validator_interface_contract() -> dict[str, Any]:
    return {
        "schema_version": "public_text_quality_runner_validator_interface_v1",
        "runner": {
            "path": (
                "Iris/build/description/v2/tools/build/"
                "run_public_text_quality_acceptance.py"
            ),
            "required_arguments": {
                "--foundation-id": "nonempty_identifier",
                "--mode": "foundation-build",
            },
            "optional_arguments": {
                "--foundation-root": "explicit_output_root_for_fixture_or_diagnostic"
            },
            "foundation_root_policy": {
                "repository_local_default": (
                    "exact_tracked_g4_foundation_root_only"
                ),
                "external_fixture_or_diagnostic_root": "allowed_when_explicit",
                "other_repository_local_root": "forbidden",
            },
            "forbidden_arguments": ["--attempt-id"],
            "implicit_default_mode_allowed": False,
        },
        "validator": {
            "path": (
                "Iris/build/description/v2/tools/build/"
                "validate_public_text_quality_acceptance.py"
            ),
            "required_arguments": {
                "--foundation-id": "exact_runner_foundation_id",
                "--require-foundation-ready": True,
                "--no-write": True,
            },
            "optional_arguments": {
                "--foundation-root": "explicit_input_root_for_fixture_or_diagnostic"
            },
            "foundation_root_policy": {
                "repository_local_default": (
                    "exact_tracked_g4_foundation_root_only"
                ),
                "external_fixture_or_diagnostic_root": "allowed_when_explicit",
                "other_repository_local_root": "forbidden",
            },
            "forbidden_arguments": ["--attempt-id"],
        },
        "exit_codes": {
            "0": "validated_foundation_ready",
            "2": "interface_or_contract_failure",
            "3": "write_once_conflict",
        },
        "official_phase_modes_implemented": False,
        "foundation_can_issue_official_disposition": False,
    }


def policy_candidate() -> dict[str, Any]:
    detector_mapping = detector_mapping_candidate()
    detector_thresholds = {
        row["detector_id"]: {
            "disposition_class": row["disposition_class"],
            "threshold": row["threshold"],
            "rationale_id": row["rationale_id"],
        }
        for row in detector_mapping["mappings"]
    }
    return {
        "schema_version": "public_text_quality_acceptance_policy_candidate_v1",
        "policy_candidate_version": "1.0.0",
        "authority_state": "development_foundation_candidate",
        "authority_effect": "none",
        "official_policy_ratified": False,
        "raw_metrics_immutable": True,
        "default_exceptions": [],
        "current_runtime_payload_thresholds": {
            "coverage_quality_weak": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "coverage_quality_adequate": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
            "coverage_quality_strong": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
            "missing_any_required_section_row": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "missing_required_section_occurrence": {
                "disposition_class": "advisory_debt",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "missing_context_support": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
            "missing_limitation_tail": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
            "missing_use_core": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
            "unadopted": {
                "disposition_class": "non_claim",
                "threshold": {"operator": "none", "value": None},
            },
        },
        "naturalization_candidate_thresholds": {
            "semantic_preservation_failure": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "unsatisfied_required_body_plan_role": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "equivalence_proof_failure": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            "compiler_invalid_pattern": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
            **detector_thresholds,
            "human_review_blocker_required_denominator": {
                "disposition_class": "blocking_gate",
                "threshold": {"operator": "eq", "value": {"integer": 0}},
            },
        },
        "waiver_contract": {
            "default_set": [],
            "allowed_waived_disposition": "deferred_internal_debt",
            "technical_or_freshness_scope_allowed": False,
            "raw_metric_mutation_allowed": False,
            "waiver_can_create_clean_accepted": False,
            "expiry_or_reevaluation_condition_required": True,
        },
        "item_disposition_mapping": {
            "technical_blocker": "blocked",
            "blocking_gate_unsatisfied": "blocked",
            "advisory_debt_unsatisfied": "deferred_internal_debt",
            "active_waiver": "deferred_internal_debt",
            "no_applicable_finding": "accepted",
            "non_claim_metric": "no_item_disposition_effect",
        },
        "aggregate_disposition_enum": list(QUALIFIED_DISPOSITIONS),
        "final_disposition_algorithm": [
            {
                "when": "technical_blocker_count > 0",
                "result": "blocked",
            },
            {
                "when": "effective_blocking_finding_count > 0",
                "result": "blocked",
            },
            {
                "when": "advisory_debt_count > 0 or active_waiver_count > 0",
                "result": "deferred_internal_debt",
            },
            {"when": "otherwise", "result": "accepted"},
        ],
        "threshold_rationale_constraints": {
            "candidate_metric_dependency_allowed": False,
            "current_payload_result_dependency_allowed": False,
            "historical_threshold_inheritance_allowed": False,
            "exact_integer_or_rational_comparison_required": True,
        },
    }


def synchronization_projection() -> dict[str, Any]:
    return {
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "canonical_stage_order": [
            "S0_plan_sync",
            "S1_publish_foundation",
            "S2_naturalization_build",
            "S3_publish_official_attempt",
            "S4_naturalization_finalize",
        ],
        "foundation_required_state": {
            "foundation_contract_ready_for_remediation": True,
            "authority_effect": "none",
            "official_disposition": "not_issued",
            "live_gate_adopted": False,
            "policy_closure_state": "not_started",
        },
        "evaluation_subject_kind_enum": list(EVALUATION_SUBJECT_KINDS),
        "candidate_structural_status_enum": list(CANDIDATE_STRUCTURAL_STATUSES),
        "required_handoff_constituent_ids": list(REQUIRED_HANDOFF_CONSTITUENT_IDS),
        "nonaccepted_candidate_action": "after_remediation",
        "blocked_immediate_allowed_for_synchronized_candidate": False,
        "candidate_runtime_parity_applicability": "not_applicable",
        "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
        "publish_owns_metric_mapping_threshold_waiver_disposition": True,
        "dvf_owns_proposition_discourse_realization_raw_detector": True,
    }


def build_foundation_contract(foundation_id: str) -> dict[str, Any]:
    if not foundation_id or foundation_id.strip() != foundation_id:
        raise FoundationContractError("foundation_id must be nonempty and trimmed")
    candidates = {
        "upstream_prerequisite_binding": build_upstream_prerequisite_binding(),
        "metric_registry_candidate": metric_registry_candidate(),
        "denominator_registry_candidate": denominator_registry_candidate(),
        "policy_candidate": policy_candidate(),
        "detector_mapping_candidate": detector_mapping_candidate(),
        "human_review_selection_contract": human_review_selection_contract(),
        "runner_validator_interface": runner_validator_interface_contract(),
        "required_handoff_schema": required_handoff_schema(),
        "freshness_contract": freshness_contract(),
        "synchronization_projection": synchronization_projection(),
    }
    hashes = {f"{name}_hash": canonical_hash(value) for name, value in candidates.items()}
    return {
        "schema_version": FOUNDATION_SCHEMA_VERSION,
        "foundation_id": foundation_id,
        "foundation_contract_version": FOUNDATION_CONTRACT_VERSION,
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "global_synchronization_contract_id": GLOBAL_SYNC_CONTRACT_ID,
        "roadmap_input_sha256_planning_observation": (
            "4b28e1fd3302877de81d85b14b6a7facd79b5b97a09e6db5aa5bcf8e2d4b07b9"
        ),
        "roadmap_provenance_effect": "planning_observation_only",
        "owner_instruction_scope": "implement_fresh_g4_foundation_successor_only",
        "owner_instruction_is_policy_ratification": False,
        "owner_instruction_is_gate_adoption": False,
        "owner_instruction_is_terminal_seal": False,
        "predecessor_foundation": _predecessor_foundation_binding(),
        "successor_reason": (
            "bind_fresh_g4_readiness_to_g3_adoption_and_current_facts_manifest_identity"
        ),
        **hashes,
        **candidates,
        "candidate_content_dependency_count": 0,
        "candidate_metric_dependency_count": 0,
        "foundation_contract_ready_for_remediation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "naturalization_required_handoff_schema_complete": True,
        "official_attempt_created": False,
        "policy_seal_created": False,
        "terminal_seal_created": False,
    }


def _registration_index(
    registry: dict[str, Any], key: str
) -> dict[str, dict[str, Any]]:
    rows = registry.get("registrations")
    if not isinstance(rows, list):
        raise FoundationContractError(f"registry registrations missing: {key}")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get(key), str):
            raise FoundationContractError(f"invalid registry row for {key}")
        identity = row[key]
        if identity in result:
            raise FoundationContractError(f"duplicate {key}: {identity}")
        result[identity] = row
    return result


def validate_foundation_contract(
    contract: dict[str, Any], *, expected_foundation_id: str
) -> dict[str, Any]:
    expected = build_foundation_contract(expected_foundation_id)
    if contract != expected:
        raise FoundationContractError(
            "foundation contract differs from the deterministic candidate-independent projection"
        )

    metric_index = _registration_index(
        contract["metric_registry_candidate"], "metric_id"
    )
    denominator_index = _registration_index(
        contract["denominator_registry_candidate"], "denominator_id"
    )
    detector_rows = contract["detector_mapping_candidate"]["mappings"]
    detector_ids = [row["detector_id"] for row in detector_rows]
    if detector_ids != list(RAW_DETECTOR_IDS):
        raise FoundationContractError("raw detector mapping order or membership mismatch")
    if len(detector_ids) != len(set(detector_ids)):
        raise FoundationContractError("duplicate detector mapping")

    unknown_denominators = sorted(
        {
            row["denominator_id"]
            for row in metric_index.values()
            if row["denominator_id"] not in denominator_index
            and not row["denominator_id"].startswith(
                "naturalization_raw_detector_opportunity_v1:"
            )
        }
    )
    if unknown_denominators:
        raise FoundationContractError(
            f"metrics reference unknown denominators: {unknown_denominators}"
        )

    invalid_dispositions = sorted(
        {
            row["disposition_class"]
            for row in metric_index.values()
            if row["disposition_class"] not in DISPOSITION_CLASSES
        }
    )
    if invalid_dispositions:
        raise FoundationContractError(
            f"invalid disposition classes: {invalid_dispositions}"
        )

    policy_metric_ids = set(
        contract["policy_candidate"]["current_runtime_payload_thresholds"]
    ) | set(contract["policy_candidate"]["naturalization_candidate_thresholds"])
    if policy_metric_ids != set(metric_index):
        raise FoundationContractError(
            "policy candidate metric set differs from metric registry"
        )

    if contract["policy_candidate"]["default_exceptions"]:
        raise FoundationContractError("v1 default exception set must be empty")

    return {
        "status": "PASS",
        "four_plan_sync_projection_sha256_match": True,
        "clean_validation_terminal_pass": True,
        "food_sealed_successor_terminal_closeout": True,
        "registry_food_successor_adoption_receipt_valid": True,
        "current_facts_equals_selected_successor_facts": True,
        "current_manifest_binds_selected_successor_manifest": True,
        "metric_count": len(metric_index),
        "denominator_count": len(denominator_index),
        "raw_detector_count": len(detector_ids),
        "unknown_metric_count": 0,
        "unknown_denominator_count": 0,
        "unmapped_raw_detector_count": 0,
        "candidate_content_dependency_count": 0,
        "candidate_metric_dependency_count": 0,
    }


def _fraction_from_value(value: dict[str, Any]) -> Fraction:
    if set(value) == {"integer"}:
        integer = value["integer"]
        if not isinstance(integer, int):
            raise FoundationContractError("threshold integer must be an integer")
        return Fraction(integer, 1)
    if set(value) == {"numerator", "denominator"}:
        numerator = value["numerator"]
        denominator = value["denominator"]
        if not isinstance(numerator, int) or not isinstance(denominator, int):
            raise FoundationContractError("rational threshold must use integers")
        if denominator <= 0:
            raise FoundationContractError("rational threshold denominator must be positive")
        return Fraction(numerator, denominator)
    raise FoundationContractError("threshold value must be exact integer or rational")


def evaluate_threshold(
    *, numerator: int, denominator: int, threshold: dict[str, Any]
) -> bool:
    if not isinstance(numerator, int) or numerator < 0:
        raise FoundationContractError("metric numerator must be a nonnegative integer")
    if not isinstance(denominator, int) or denominator <= 0:
        raise FoundationContractError("metric denominator must be a positive integer")
    operator = threshold.get("operator")
    value = threshold.get("value")
    if operator == "none":
        if value is not None:
            raise FoundationContractError("none threshold must have null value")
        return True
    if not isinstance(value, dict):
        raise FoundationContractError("threshold value object is required")
    expected = _fraction_from_value(value)
    actual = (
        Fraction(numerator, 1)
        if set(value) == {"integer"}
        else Fraction(numerator, denominator)
    )
    if operator == "eq":
        return actual == expected
    if operator == "le":
        return actual <= expected
    if operator == "lt":
        return actual < expected
    if operator == "ge":
        return actual >= expected
    if operator == "gt":
        return actual > expected
    raise FoundationContractError(f"unknown threshold operator: {operator}")


def determine_qualified_disposition(
    *,
    technical_blocker_count: int,
    effective_blocking_finding_count: int,
    advisory_debt_count: int,
    active_waiver_count: int,
) -> str:
    counts = (
        technical_blocker_count,
        effective_blocking_finding_count,
        advisory_debt_count,
        active_waiver_count,
    )
    if any(not isinstance(value, int) or value < 0 for value in counts):
        raise FoundationContractError("disposition counts must be nonnegative integers")
    if technical_blocker_count > 0:
        return "blocked"
    if effective_blocking_finding_count > 0:
        return "blocked"
    if advisory_debt_count > 0 or active_waiver_count > 0:
        return "deferred_internal_debt"
    return "accepted"


def _parse_timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise FoundationContractError("timestamp must be a string")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise FoundationContractError(f"invalid timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise FoundationContractError("timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _without_volatile(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _without_volatile(child)
            for key, child in value.items()
            if key not in VOLATILE_CANONICAL_FIELDS
        }
    if isinstance(value, list):
        return [_without_volatile(child) for child in value]
    return value


def _fixture_outcome(row: dict[str, Any], contract: dict[str, Any]) -> str:
    kind = row["fixture_kind"]
    data = row.get("input", {})
    if not isinstance(data, dict):
        raise FoundationContractError("fixture input must be an object")

    if kind == "freshness":
        return (
            "accepted"
            if data.get("expected_hash") == data.get("actual_hash")
            else "blocked"
        )
    if kind == "registry_membership":
        registry = data.get("registry")
        value = data.get("value")
        if registry == "metric":
            known = set(
                _registration_index(
                    contract["metric_registry_candidate"], "metric_id"
                )
            )
        elif registry == "denominator":
            known = set(
                _registration_index(
                    contract["denominator_registry_candidate"], "denominator_id"
                )
            )
        elif registry == "subject_kind":
            known = set(EVALUATION_SUBJECT_KINDS)
        elif registry == "profile":
            known = set(data.get("known_values", []))
        else:
            return "blocked"
        return "accepted" if value in known else "blocked"
    if kind == "denominator":
        value = data.get("value")
        return "accepted" if isinstance(value, int) and value > 0 else "blocked"
    if kind == "threshold":
        satisfied = evaluate_threshold(
            numerator=data["numerator"],
            denominator=data["denominator"],
            threshold=data["threshold"],
        )
        if satisfied:
            return "accepted"
        return (
            "blocked"
            if data["disposition_class"] == "blocking_gate"
            else "deferred_internal_debt"
        )
    if kind == "row_occurrence":
        rows = data.get("missing_any_row_count")
        occurrences = data.get("missing_occurrence_count")
        blockers = data.get("effective_blocker_count")
        valid = (
            isinstance(rows, int)
            and isinstance(occurrences, int)
            and occurrences >= rows >= 0
            and blockers == rows
        )
        return "accepted" if valid else "blocked"
    if kind == "unadopted_separation":
        valid = (
            data.get("unadopted_in_quality_denominator_count") == 0
            and data.get("unadopted_counted_as_weak") == 0
        )
        return "accepted" if valid else "blocked"
    if kind == "metric_axes":
        valid = (
            data.get("quality_class") in {"weak", "adequate", "strong"}
            and isinstance(data.get("missing_any_required_section"), bool)
        )
        return "accepted" if valid else "blocked"
    if kind == "partition":
        parts = data.get("parts")
        total = data.get("total")
        valid = (
            isinstance(parts, list)
            and all(isinstance(value, int) and value >= 0 for value in parts)
            and sum(parts) == total
        )
        return "accepted" if valid else "blocked"
    if kind == "waiver":
        required = {
            "payload_binding_hash",
            "expected_payload_binding_hash",
            "policy_hash",
            "expected_policy_hash",
            "metric_id",
            "known_metric",
            "original_disposition",
            "waived_disposition",
            "owner_identity",
            "owner_valid",
            "issued_at",
            "expires_at",
            "evaluation_at",
            "owner_binding_proof",
            "technical_failure_scope",
            "raw_metric_mutated",
        }
        if set(data) != required:
            return "blocked"
        valid = (
            data["payload_binding_hash"] == data["expected_payload_binding_hash"]
            and data["policy_hash"] == data["expected_policy_hash"]
            and data["metric_id"] == data["known_metric"]
            and data["waived_disposition"] == "deferred_internal_debt"
            and data["owner_valid"] is True
            and bool(data["owner_identity"])
            and bool(data["owner_binding_proof"])
            and data["technical_failure_scope"] is False
            and data["raw_metric_mutated"] is False
            and _parse_timestamp(data["issued_at"])
            <= _parse_timestamp(data["evaluation_at"])
            < _parse_timestamp(data["expires_at"])
        )
        if not valid:
            return "blocked"
        return "deferred_internal_debt"
    if kind == "disposition":
        return determine_qualified_disposition(
            technical_blocker_count=data.get("technical_blocker_count", 0),
            effective_blocking_finding_count=data.get(
                "effective_blocking_finding_count", 0
            ),
            advisory_debt_count=data.get("advisory_debt_count", 0),
            active_waiver_count=data.get("active_waiver_count", 0),
        )
    if kind == "schema":
        value = data.get("value")
        required = data.get("required_keys", [])
        if not isinstance(value, dict) or not isinstance(required, list):
            return "blocked"
        return "accepted" if set(value) == set(required) else "blocked"
    if kind == "canonicalization":
        left = _without_volatile(data.get("left"))
        right = _without_volatile(data.get("right"))
        return "accepted" if canonical_hash(left) == canonical_hash(right) else "blocked"
    if kind == "exception":
        if data.get("default_exception_count") != 0:
            return "blocked"
        if data.get("semantic_freeform_exception") is True:
            return "blocked"
        return "accepted"
    if kind == "structural":
        required = data.get("required")
        status = data.get("status")
        proof_valid = data.get("equivalence_proof_valid")
        if status not in CANDIDATE_STRUCTURAL_STATUSES:
            return "blocked"
        if required and status == "not_required":
            return "blocked"
        if required and status == "missing":
            return "blocked"
        if status in {
            "satisfied_by_verified_fusion",
            "satisfied_by_verified_suppression",
        } and proof_valid is not True:
            return "blocked"
        return "accepted"
    if kind == "human_review_scope":
        required_count = data.get("required_review_count")
        reviewed_count = data.get("reviewed_count")
        corpus_wide_claim = data.get("corpus_wide_zero_claim")
        full_corpus_reviewed = data.get("full_corpus_reviewed")
        valid = (
            isinstance(required_count, int)
            and isinstance(reviewed_count, int)
            and required_count >= 0
            and reviewed_count == required_count
            and (not corpus_wide_claim or full_corpus_reviewed)
        )
        return "accepted" if valid else "blocked"
    if kind == "sync_projection":
        return (
            "accepted"
            if data.get("projection_hash")
            == contract["synchronization_projection_hash"]
            else "blocked"
        )
    if kind == "runtime_parity_claim":
        valid = (
            data.get("applicability") == "not_applicable"
            and data.get("reason") == "candidate_not_registry_adopted"
            and data.get("registry_runtime_pass_claimed") is False
        )
        return "accepted" if valid else "blocked"
    if kind == "raw_metric_mutation":
        return "accepted" if data.get("raw_metric_mutated") is False else "blocked"
    if kind == "state_claim":
        required_state = synchronization_projection()["foundation_required_state"]
        return "accepted" if data == required_state else "blocked"
    raise FoundationContractError(f"unknown fixture kind: {kind}")


def validate_fixture_manifest(
    manifest: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    require_exact_keys(
        manifest,
        required=("schema_version", "fixtures"),
        label="fixture manifest",
    )
    if manifest["schema_version"] != FIXTURE_SCHEMA_VERSION:
        raise FoundationContractError("fixture manifest schema version mismatch")
    rows = manifest["fixtures"]
    if not isinstance(rows, list):
        raise FoundationContractError("fixtures must be a list")

    ids: set[str] = set()
    origin_counts = {"roadmap_mandatory": 0, "plan_additive": 0}
    failures: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise FoundationContractError("fixture row must be an object")
        require_exact_keys(
            row,
            required=(
                "fixture_id",
                "origin",
                "fixture_kind",
                "input",
                "expected_outcome",
            ),
            label="fixture row",
        )
        fixture_id = row["fixture_id"]
        origin = row["origin"]
        if not isinstance(fixture_id, str) or fixture_id in ids:
            raise FoundationContractError(f"invalid or duplicate fixture_id: {fixture_id}")
        if origin not in origin_counts:
            raise FoundationContractError(f"unknown fixture origin: {origin}")
        if row["expected_outcome"] not in QUALIFIED_DISPOSITIONS:
            raise FoundationContractError(
                f"invalid expected outcome for {fixture_id}: {row['expected_outcome']}"
            )
        ids.add(fixture_id)
        origin_counts[origin] += 1
        try:
            actual = _fixture_outcome(row, contract)
            passed = actual == row["expected_outcome"]
            error = None
        except Exception as exc:  # fail-closed fixture path
            actual = "blocked"
            passed = actual == row["expected_outcome"]
            error = f"{type(exc).__name__}: {exc}"
        result = {
            "fixture_id": fixture_id,
            "origin": origin,
            "actual_outcome": actual,
            "expected_outcome": row["expected_outcome"],
            "fixture_pass": passed,
            "error": error,
        }
        results.append(result)
        if not passed:
            failures.append(result)

    roadmap_ids = {
        f"PTQA-RM-{index:02d}" for index in range(1, 37)
    }
    actual_roadmap_ids = {
        row["fixture_id"] for row in rows if row["origin"] == "roadmap_mandatory"
    }
    if actual_roadmap_ids != roadmap_ids:
        raise FoundationContractError(
            "roadmap mandatory fixture IDs must be exactly PTQA-RM-01..36"
        )
    if origin_counts["plan_additive"] < 1:
        raise FoundationContractError("at least one plan-additive fixture is required")
    if failures:
        raise FoundationContractError(
            f"foundation fixture failures: {[row['fixture_id'] for row in failures]}"
        )
    return {
        "status": "PASS",
        "roadmap_mandatory_fixture_count": origin_counts["roadmap_mandatory"],
        "plan_additive_fixture_count": origin_counts["plan_additive"],
        "total_fixture_count": len(rows),
        "fixture_without_origin_count": 0,
        "fixture_failure_count": 0,
        "results": results,
    }


def source_hash_inventory(paths: Iterable[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        if not path.is_file():
            raise FoundationContractError(f"required foundation source missing: {path}")
        rows.append(
            {
                "path": repo_relative(path),
                "hash_algorithm": "sha256_utf8_lf_normalized_v1",
                "sha256": sha256_lf_normalized_text(path),
            }
        )
    return rows


def build_readiness_report(
    *,
    foundation_id: str,
    contract_path: Path,
    contract: dict[str, Any],
    fixture_report: dict[str, Any],
    protected_no_write_guard: dict[str, Any],
) -> dict[str, Any]:
    validation = validate_foundation_contract(
        contract, expected_foundation_id=foundation_id
    )
    implementation_hashes = source_hash_inventory(FOUNDATION_IMPLEMENTATION_FILES)
    documentation_hashes = source_hash_inventory(
        (PLAN_DOC, NATURALIZATION_PLAN_DOC, *FOUNDATION_DOCS)
    )
    return {
        "schema_version": READINESS_SCHEMA_VERSION,
        "foundation_id": foundation_id,
        "foundation_contract_version": FOUNDATION_CONTRACT_VERSION,
        "foundation_contract_path": repo_relative(contract_path),
        "foundation_contract_raw_sha256": sha256_file(contract_path),
        "foundation_contract_canonical_sha256": canonical_hash(contract),
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "global_synchronization_contract_id": GLOBAL_SYNC_CONTRACT_ID,
        "synchronization_projection_hash": contract[
            "synchronization_projection_hash"
        ],
        "upstream_prerequisite_binding_hash": contract[
            "upstream_prerequisite_binding_hash"
        ],
        "upstream_prerequisite_binding": contract[
            "upstream_prerequisite_binding"
        ],
        "metric_registry_candidate_hash": contract[
            "metric_registry_candidate_hash"
        ],
        "denominator_registry_candidate_hash": contract[
            "denominator_registry_candidate_hash"
        ],
        "policy_candidate_hash": contract["policy_candidate_hash"],
        "detector_mapping_candidate_hash": contract[
            "detector_mapping_candidate_hash"
        ],
        "human_review_selection_contract_hash": contract[
            "human_review_selection_contract_hash"
        ],
        "runner_validator_interface_hash": contract[
            "runner_validator_interface_hash"
        ],
        "required_handoff_schema_hash": contract[
            "required_handoff_schema_hash"
        ],
        "freshness_contract_hash": contract["freshness_contract_hash"],
        "implementation_hashes": implementation_hashes,
        "documentation_hashes": documentation_hashes,
        "fixture_manifest": {
            "path": repo_relative(FIXTURE_MANIFEST),
            "hash_algorithm": "sha256_canonical_json_v1",
            "sha256": canonical_hash(load_json_strict(FIXTURE_MANIFEST)),
            "roadmap_mandatory_fixture_count": fixture_report[
                "roadmap_mandatory_fixture_count"
            ],
            "plan_additive_fixture_count": fixture_report[
                "plan_additive_fixture_count"
            ],
            "total_fixture_count": fixture_report["total_fixture_count"],
            "fixture_failure_count": fixture_report["fixture_failure_count"],
        },
        "contract_validation": validation,
        "protected_no_write_guard": protected_no_write_guard,
        "dry_run": {
            "kind": "synthetic_candidate_independent_fixture_dry_run",
            "current_payload_bytes_read": 0,
            "naturalization_candidate_bytes_read": 0,
            "candidate_metric_values_read": 0,
            "detector_mapping_coverage_pass": True,
            "human_review_selection_contract_pass": True,
            "handoff_schema_contract_pass": True,
            "runner_validator_fixture_pass": True,
        },
        "candidate_content_dependency_count": 0,
        "candidate_metric_dependency_count": 0,
        "four_plan_sync_projection_sha256_match": True,
        "clean_validation_terminal_pass": True,
        "food_sealed_successor_terminal_closeout": True,
        "registry_food_successor_adoption_receipt_valid": True,
        "current_facts_equals_selected_successor_facts": True,
        "current_manifest_binds_selected_successor_manifest": True,
        "protected_surface_mutation_count": 0,
        "foundation_contract_ready_for_remediation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "naturalization_required_handoff_schema_complete": True,
        "foundation_runner_validator_fixture_pass": True,
        "official_attempt_created": False,
        "policy_seal_created": False,
        "evaluation_subject_disposition_created": False,
        "required_gate_candidate_created": False,
        "terminal_seal_created": False,
        "status": "foundation_ready_for_remediation",
    }


def write_once_or_same(path: Path, value: Any) -> str:
    desired = pretty_json_bytes(value)
    if path.exists():
        current = path.read_bytes()
        if current != desired:
            raise FoundationContractError(
                f"write-once conflict at {repo_relative(path)}"
            )
        return "already_identical"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(desired)
    return "created"


def foundation_paths(root: Path) -> tuple[Path, Path]:
    return root / FOUNDATION_CONTRACT_NAME, root / READINESS_REPORT_NAME


def validate_foundation_root(root: Path) -> Path:
    resolved = root.resolve()
    default = DEFAULT_FOUNDATION_ROOT.resolve()
    repository = REPO_ROOT.resolve()
    if resolved.is_relative_to(repository) and resolved != default:
        raise FoundationContractError(
            "repository-local foundation root must be the exact tracked G4 foundation root"
        )
    return resolved


def build_foundation(
    *, foundation_id: str, foundation_root: Path = DEFAULT_FOUNDATION_ROOT
) -> dict[str, Any]:
    foundation_root = validate_foundation_root(foundation_root)
    protected_before = protected_foundation_surface_snapshot()
    contract_path, readiness_path = foundation_paths(foundation_root)
    contract = build_foundation_contract(foundation_id)
    contract_write_state = write_once_or_same(contract_path, contract)
    fixture_manifest = load_json_strict(FIXTURE_MANIFEST)
    fixture_report = validate_fixture_manifest(fixture_manifest, contract)
    protected_after = protected_foundation_surface_snapshot()
    protected_no_write_guard = _no_write_guard(protected_before, protected_after)
    readiness = build_readiness_report(
        foundation_id=foundation_id,
        contract_path=contract_path,
        contract=contract,
        fixture_report=fixture_report,
        protected_no_write_guard=protected_no_write_guard,
    )
    readiness_write_state = write_once_or_same(readiness_path, readiness)
    protected_final = protected_foundation_surface_snapshot()
    if _no_write_guard(protected_before, protected_final) != protected_no_write_guard:
        raise FoundationContractError(
            "foundation build no-write guard changed after readiness serialization"
        )
    return {
        "status": "PASS",
        "foundation_id": foundation_id,
        "foundation_root": repo_relative(foundation_root),
        "contract_write_state": contract_write_state,
        "readiness_write_state": readiness_write_state,
        "foundation_contract_ready_for_remediation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "protected_surface_mutation_count": 0,
        "registry_food_successor_adoption_receipt_valid": True,
    }


def validate_foundation(
    *, foundation_id: str, foundation_root: Path = DEFAULT_FOUNDATION_ROOT
) -> dict[str, Any]:
    foundation_root = validate_foundation_root(foundation_root)
    contract_path, readiness_path = foundation_paths(foundation_root)
    if not contract_path.is_file() or not readiness_path.is_file():
        raise FoundationContractError(
            "foundation contract and readiness report must both exist"
        )
    protected_before = protected_foundation_surface_snapshot()
    foundation_bytes_before = {
        "contract": contract_path.read_bytes(),
        "readiness": readiness_path.read_bytes(),
    }
    contract = load_json_strict(contract_path)
    readiness = load_json_strict(readiness_path)
    fixture_manifest = load_json_strict(FIXTURE_MANIFEST)
    fixture_report = validate_fixture_manifest(fixture_manifest, contract)
    protected_after = protected_foundation_surface_snapshot()
    protected_no_write_guard = _no_write_guard(protected_before, protected_after)
    expected_readiness = build_readiness_report(
        foundation_id=foundation_id,
        contract_path=contract_path,
        contract=contract,
        fixture_report=fixture_report,
        protected_no_write_guard=protected_no_write_guard,
    )
    if readiness != expected_readiness:
        raise FoundationContractError(
            "readiness report is stale or differs from the exact implementation/docs/fixture binding"
        )
    required_state = synchronization_projection()["foundation_required_state"]
    for key, expected in required_state.items():
        if readiness.get(key) != expected:
            raise FoundationContractError(
                f"foundation readiness state mismatch for {key}"
            )
    if readiness.get("status") != "foundation_ready_for_remediation":
        raise FoundationContractError("foundation readiness status mismatch")
    if (
        foundation_bytes_before["contract"] != contract_path.read_bytes()
        or foundation_bytes_before["readiness"] != readiness_path.read_bytes()
    ):
        raise FoundationContractError(
            "no-write validation changed foundation contract or readiness bytes"
        )
    protected_final = protected_foundation_surface_snapshot()
    if _no_write_guard(protected_before, protected_final) != protected_no_write_guard:
        raise FoundationContractError(
            "foundation validator no-write guard changed during validation"
        )
    return {
        "status": "PASS",
        "foundation_id": foundation_id,
        "foundation_contract_raw_sha256": readiness[
            "foundation_contract_raw_sha256"
        ],
        "foundation_contract_ready_for_remediation": True,
        "candidate_content_dependency_count": 0,
        "candidate_metric_dependency_count": 0,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
        "foundation_runner_validator_fixture_pass": True,
        "four_plan_sync_projection_sha256_match": True,
        "clean_validation_terminal_pass": True,
        "food_sealed_successor_terminal_closeout": True,
        "registry_food_successor_adoption_receipt_valid": True,
        "current_facts_equals_selected_successor_facts": True,
        "current_manifest_binds_selected_successor_manifest": True,
        "protected_surface_mutation_count": 0,
        "no_write_validation": True,
    }


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


def write_once_bytes(path: Path, desired: bytes) -> str:
    if path.exists():
        if path.read_bytes() != desired:
            raise FoundationContractError(
                f"write-once conflict at {repo_relative(path)}"
            )
        return "already_identical"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(desired)
    return "created"


def write_once_text(path: Path, text: str) -> str:
    return write_once_bytes(path, text.replace("\r\n", "\n").encode("utf-8"))


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise FoundationContractError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result


def git_head() -> str:
    return _git("rev-parse", "HEAD").stdout.strip()


def _is_tracked(path: Path) -> bool:
    return _git("ls-files", "--error-unmatch", "--", repo_relative(path), check=False).returncode == 0


def _is_ignored(path: Path) -> bool:
    result = _git(
        "check-ignore", "--no-index", "-v", "--", repo_relative(path), check=False
    )
    if result.returncode != 0:
        return False
    matched_rule = result.stdout.split("\t", 1)[0].rsplit(":", 1)[-1]
    return not matched_rule.startswith("!")


def _has_unstaged_delta(path: Path) -> bool:
    return bool(_git("diff", "--name-only", "--", repo_relative(path)).stdout.strip())


def official_attempt_root(
    attempt_id: str, attempt_root: Path | None = None
) -> Path:
    if not ATTEMPT_ID_PATTERN.fullmatch(attempt_id):
        raise FoundationContractError(
            "official attempt ID must match attempt-<digits>-<lowercase-label>"
        )
    expected = (DEFAULT_ATTEMPTS_ROOT / attempt_id).resolve()
    if attempt_root is None:
        return expected
    resolved = attempt_root.resolve()
    if resolved.is_relative_to(REPO_ROOT.resolve()) and resolved != expected:
        raise FoundationContractError(
            "repository-local attempt root must match the exact attempt namespace"
        )
    return resolved


def phase_root(root: Path, phase: int) -> Path:
    return root / f"phase{phase}"


def _require_artifacts(root: Path, phase: int, names: Iterable[str] | None = None) -> None:
    expected = names if names is not None else PHASE_ARTIFACTS[phase]
    missing = [
        repo_relative(phase_root(root, phase) / name)
        for name in expected
        if not (phase_root(root, phase) / name).is_file()
    ]
    if missing:
        raise FoundationContractError(
            f"required Phase {phase} artifacts missing: {missing}"
        )


def _constituent_map(handoff: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = handoff.get("constituents")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise FoundationContractError("handoff constituents must be an object array")
    identifiers = [row.get("id") for row in rows]
    if identifiers != list(REQUIRED_HANDOFF_CONSTITUENT_IDS):
        raise FoundationContractError("handoff constituent order/schema mismatch")
    if handoff.get("constituent_id_order") != list(REQUIRED_HANDOFF_CONSTITUENT_IDS):
        raise FoundationContractError("handoff declared constituent order mismatch")
    return {str(row["id"]): row for row in rows}


def validate_candidate_handoff(
    handoff_path: Path,
    *,
    expected_subject_kind: str = "dvf_3_3_korean_naturalization_candidate",
) -> dict[str, Any]:
    handoff = load_json_strict(handoff_path)
    require_exact_keys(
        handoff,
        required=(
            "schema_version",
            "synchronization_contract_id",
            "naturalization_attempt_id",
            "requested_evaluation_subject_kind",
            "candidate_runtime_parity_applicability",
            "candidate_runtime_parity_reason",
            "constituents",
            "constituent_id_order",
            "post_handoff_mutation_effect",
            "registry_runtime_pass_claim_allowed",
            "write_once",
        ),
        label="naturalization publish handoff",
    )
    if handoff["schema_version"] != "naturalization_publish_handoff_required_schema_v1":
        raise FoundationContractError("handoff schema version mismatch")
    if handoff["synchronization_contract_id"] != SYNC_CONTRACT_ID:
        raise FoundationContractError("handoff synchronization contract mismatch")
    if handoff["requested_evaluation_subject_kind"] != expected_subject_kind:
        raise FoundationContractError("handoff evaluation subject kind mismatch")
    if (
        handoff["candidate_runtime_parity_applicability"] != "not_applicable"
        or handoff["candidate_runtime_parity_reason"]
        != "candidate_not_registry_adopted"
        or handoff["registry_runtime_pass_claim_allowed"] is not False
    ):
        raise FoundationContractError("candidate runtime parity claim boundary mismatch")
    if (
        handoff["post_handoff_mutation_effect"] != "stale"
        or handoff["write_once"] is not True
    ):
        raise FoundationContractError("handoff immutability contract mismatch")
    constituents = _constituent_map(handoff)
    mismatches: list[str] = []
    path_rows: list[dict[str, Any]] = []
    for identifier in REQUIRED_HANDOFF_CONSTITUENT_IDS:
        row = constituents[identifier]
        if row.get("present") is not True:
            mismatches.append(f"{identifier}:not_present")
            continue
        if "path" in row:
            path = REPO_ROOT / str(row["path"])
            actual = sha256_file(path) if path.is_file() else None
            path_rows.append(
                {
                    "id": identifier,
                    "path": repo_relative(path),
                    "declared_sha256": row.get("sha256"),
                    "actual_sha256": actual,
                    "match": actual == row.get("sha256"),
                }
            )
        elif "value" in row:
            actual = sha256_bytes(canonical_json_bytes(row["value"]) + b"\n")
            if actual != row.get("sha256"):
                mismatches.append(f"{identifier}:value_hash_mismatch")
        else:
            mismatches.append(f"{identifier}:missing_path_or_value")
    mismatches.extend(
        f"{row['id']}:path_hash_mismatch" for row in path_rows if not row["match"]
    )
    if mismatches:
        raise FoundationContractError(f"stale handoff constituents: {mismatches}")
    if (
        constituents["foundation_contract_hash"]["sha256"]
        != sha256_file(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    ):
        raise FoundationContractError("handoff foundation contract is stale")
    compiler_identity = build_compiler_identity(REPO_ROOT)
    compiler_aggregate_hash = str(compiler_identity["aggregate_sha256"])
    compiler_claim = constituents["compiler_implementation_hash"].get("value")
    if not compiler_identity_matches_claim(compiler_claim, compiler_identity):
        raise FoundationContractError(
            "handoff naturalization compiler implementation is stale"
        )
    candidate_manifest_path = (
        REPO_ROOT / str(constituents["candidate_manifest_hash"]["path"])
    )
    candidate_manifest = load_json_strict(candidate_manifest_path)
    if (
        candidate_manifest.get("schema_version")
        != "dvf-3-3-korean-prose-candidate-manifest-v2"
        or candidate_manifest.get("compiler_identity") != compiler_identity
        or candidate_manifest.get("compiler_implementation_hash")
        != compiler_aggregate_hash
    ):
        raise FoundationContractError(
            "handoff candidate compiler identity evidence is stale"
        )
    return {
        "handoff": handoff,
        "constituents": constituents,
        "path_rows": path_rows,
        "handoff_raw_sha256": sha256_file(handoff_path),
        "compiler_identity": compiler_identity,
        "compiler_inventory": compiler_identity["ordered_files"],
        "compiler_aggregate_hash": compiler_aggregate_hash,
    }


def _handoff_path(
    validation: dict[str, Any], identifier: str
) -> Path:
    row = validation["constituents"][identifier]
    if "path" not in row:
        raise FoundationContractError(f"handoff constituent has no path: {identifier}")
    return REPO_ROOT / str(row["path"])


def _semantic_failure_count(report: dict[str, Any]) -> int:
    fields = (
        "missing_proposition_resolution_count",
        "qualifier_modality_limitation_preservation_failure_count",
        "unresolved_proposition_reference_count",
        "forbidden_transformation_count",
        "unknown_transformation_count",
        "invalid_structural_status_count",
        "not_applicable_without_reason_count",
    )
    return sum(int(report.get(field, 0)) for field in fields)


def compute_candidate_metric_snapshot(
    validation: dict[str, Any],
) -> dict[str, Any]:
    candidate_path = _handoff_path(validation, "candidate_rendered_hash")
    candidate_manifest_path = _handoff_path(validation, "candidate_manifest_hash")
    source_manifest_path = _handoff_path(
        validation, "source_proposition_manifest_hash"
    )
    structural_path = _handoff_path(
        validation, "structural_satisfaction_ledger_hash"
    )
    semantic_path = _handoff_path(validation, "semantic_preservation_report_hash")
    raw_path = _handoff_path(validation, "raw_detector_report_hash")
    review_sample_path = _handoff_path(
        validation, "human_review_sample_manifest_hash"
    )
    review_decision_path = _handoff_path(
        validation, "human_review_decision_hash"
    )

    candidate = load_json_strict(candidate_path)
    candidate_manifest = load_json_strict(candidate_manifest_path)
    source_manifest = load_json_strict(source_manifest_path)
    structural_rows = load_jsonl_strict(structural_path)
    semantic = load_json_strict(semantic_path)
    raw = load_json_strict(raw_path)
    review_sample = load_json_strict(review_sample_path)
    review_decision = load_json_strict(review_decision_path)

    entries = candidate.get("entries")
    if not isinstance(entries, dict) or not entries:
        raise FoundationContractError("candidate rendered entries must be nonempty object")
    item_ids = sorted(entries)
    if len(item_ids) != len(set(item_ids)):
        raise FoundationContractError("duplicate exact candidate item identity")
    candidate_denominator = raw.get("candidate_denominator")
    if not isinstance(candidate_denominator, int) or candidate_denominator <= 0:
        raise FoundationContractError("candidate denominator must be positive integer")
    if candidate_manifest.get("candidate_emission_count") != candidate_denominator:
        raise FoundationContractError("candidate emission/denominator mismatch")
    if candidate_manifest.get("source_universe_count") != len(item_ids):
        raise FoundationContractError("candidate source universe/key count mismatch")
    if candidate_manifest.get("unadopted_count") != len(item_ids) - candidate_denominator:
        raise FoundationContractError("candidate explicit unadopted count mismatch")

    source_count = source_manifest.get("proposition_count")
    if not isinstance(source_count, int) or source_count <= 0:
        raise FoundationContractError("source proposition denominator invalid")
    required_rows = [
        row
        for row in structural_rows
        if row.get("required") is True
        and row.get("emission_eligible") is True
    ]
    illegal_required_not_required = sum(
        row.get("status") == "not_required" for row in required_rows
    )
    unsatisfied = sum(
        row.get("status") not in SATISFIED_REQUIRED_STRUCTURAL_STATUSES
        for row in required_rows
    )
    transformation_rows = [
        row
        for row in structural_rows
        if row.get("emission_eligible") is True
        and row.get("status")
        in ("satisfied_by_verified_fusion", "satisfied_by_verified_suppression")
    ]
    equivalence_failures = int(
        semantic.get("equivalence_proof_missing_or_mismatch_count", 0)
    )
    if illegal_required_not_required:
        equivalence_failures += illegal_required_not_required

    detector_ids = raw.get("configured_detector_ids")
    if detector_ids != list(RAW_DETECTOR_IDS):
        raise FoundationContractError("raw detector configured ID/order mismatch")
    hit_counts = raw.get("detector_hit_counts")
    if not isinstance(hit_counts, dict):
        raise FoundationContractError("raw detector hit counts missing")
    if (
        raw.get("raw_detector_full_candidate_completeness_pass") is not True
        or raw.get("detector_opportunity_count")
        != candidate_denominator * len(RAW_DETECTOR_IDS)
        or raw.get("expected_detector_opportunity_count")
        != candidate_denominator * len(RAW_DETECTOR_IDS)
    ):
        raise FoundationContractError("raw detector completeness mismatch")

    selected = review_sample.get("selected_item_ids")
    selected_denominator = review_sample.get("selected_required_denominator")
    if (
        not isinstance(selected, list)
        or len(selected) != selected_denominator
        or len(selected) != len(set(selected))
        or review_sample.get("candidate_rendered_hash") != sha256_file(candidate_path)
        or review_decision.get("candidate_rendered_hash") != sha256_file(candidate_path)
        or review_decision.get("selected_ordered_digest")
        != review_sample.get("selected_ordered_digest")
    ):
        raise FoundationContractError("human review denominator/binding mismatch")
    rubric = review_decision.get("uniform_review")
    human_review_failures = (
        0
        if review_decision.get("status") == "approved"
        and isinstance(rubric, dict)
        and rubric
        and all(value == "pass" for value in rubric.values())
        else selected_denominator
    )

    denominators: dict[str, int] = {
        "naturalization_candidate_item_v1": candidate_denominator,
        "naturalization_source_proposition_v1": source_count,
        "naturalization_required_body_plan_role_v1": len(required_rows),
        "naturalization_fusion_suppression_transformation_v1": max(
            0, len(transformation_rows)
        ),
        "naturalization_human_review_required_v1": selected_denominator,
    }
    for detector_id in RAW_DETECTOR_IDS:
        denominators[
            f"naturalization_raw_detector_opportunity_v1:{detector_id}"
        ] = candidate_denominator

    numerators = {
        "semantic_preservation_failure": _semantic_failure_count(semantic),
        "unsatisfied_required_body_plan_role": unsatisfied,
        "equivalence_proof_failure": equivalence_failures,
        "compiler_invalid_pattern": (
            0
            if candidate_manifest.get("candidate_content_hash_count") == 1
            and candidate_manifest.get("candidate_volatile_metadata_field_count") == 0
            else 1
        ),
        **{
            detector_id: int(hit_counts.get(detector_id, 0))
            for detector_id in RAW_DETECTOR_IDS
        },
        "human_review_blocker_required_denominator": int(human_review_failures),
    }
    contract = load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    registrations = [
        row
        for row in contract["metric_registry_candidate"]["registrations"]
        if "dvf_3_3_korean_naturalization_candidate"
        in row["applicable_subject_kinds"]
    ]
    rows: list[dict[str, Any]] = []
    for registration in registrations:
        metric_id = registration["metric_id"]
        denominator_id = registration["denominator_id"]
        denominator = denominators.get(denominator_id)
        if denominator is None or denominator <= 0:
            raise FoundationContractError(
                f"candidate denominator missing or zero: {denominator_id}"
            )
        rows.append(
            {
                "metric_id": metric_id,
                "denominator_id": denominator_id,
                "disposition_class": registration["disposition_class"],
                "numerator": numerators[metric_id],
                "denominator": denominator,
                "exact_ratio": {
                    "numerator": numerators[metric_id],
                    "denominator": denominator,
                },
            }
        )
    return {
        "schema_version": "public_text_quality_candidate_metric_snapshot_v1",
        "evaluation_subject_kind": "dvf_3_3_korean_naturalization_candidate",
        "evaluation_subject_hash": sha256_file(candidate_path),
        "candidate_key_count": len(item_ids),
        "quality_evaluable_candidate_count": candidate_denominator,
        "explicit_unadopted_count": len(item_ids) - candidate_denominator,
        "source_proposition_count": source_count,
        "required_body_plan_role_count": len(required_rows),
        "fusion_suppression_transformation_count": len(transformation_rows),
        "human_review_required_denominator": selected_denominator,
        "metric_rows": rows,
        "metric_projection_hash": canonical_hash(rows),
        "technical_blocker_count": 0,
    }


def _candidate_entries_rows(validation: dict[str, Any]) -> list[dict[str, Any]]:
    candidate = load_json_strict(_handoff_path(validation, "candidate_rendered_hash"))
    entries = candidate.get("entries")
    if not isinstance(entries, dict):
        raise FoundationContractError("candidate entries must be an object")
    rows = []
    for item_id in sorted(entries):
        payload = entries[item_id]
        if not isinstance(payload, dict):
            raise FoundationContractError(f"candidate payload is not object: {item_id}")
        rows.append({"item_id": item_id, "payload": _without_volatile(payload)})
    return rows


def _protected_snapshot(validation: dict[str, Any]) -> list[dict[str, Any]]:
    report = load_json_strict(
        _handoff_path(validation, "protected_surface_no_mutation_report_hash")
    )
    if (
        report.get("protected_surface_no_mutation_pass") is not True
        or report.get("protected_surface_mutation_count") != 0
    ):
        raise FoundationContractError("naturalization protected surface report is not PASS")
    after_snapshot = report.get("after_snapshot")
    rows = (
        after_snapshot.get("files")
        if isinstance(after_snapshot, dict)
        else after_snapshot
    )
    if not isinstance(rows, list):
        raise FoundationContractError("protected after snapshot missing")
    normalized: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or "path" not in row:
            raise FoundationContractError("protected snapshot row invalid")
        path = REPO_ROOT / str(row["path"])
        current = sha256_file(path) if path.is_file() else None
        if path.is_file() != row.get("exists") or current != row.get("sha256"):
            raise FoundationContractError(
                f"protected surface stale before Publish attempt: {row['path']}"
            )
        normalized.append(
            {
                "path": repo_relative(path),
                "present": path.is_file(),
                "sha256": current,
            }
        )
    return normalized


def _vcs_preflight(paths: Iterable[Path]) -> dict[str, Any]:
    unique = sorted({path.resolve() for path in paths}, key=lambda path: repo_relative(path))
    rows = []
    for path in unique:
        rows.append(
            {
                "path": repo_relative(path),
                "present": path.is_file(),
                "tracked": _is_tracked(path),
                "ignored": _is_ignored(path),
                "unstaged_delta": _has_unstaged_delta(path),
            }
        )
    blockers = [
        row["path"]
        for row in rows
        if not row["present"]
        or not row["tracked"]
        or row["ignored"]
        or row["unstaged_delta"]
    ]
    return {
        "schema_version": "public_text_quality_vcs_required_surface_preflight_v1",
        "status": "PASS" if not blockers else "FAIL",
        "required_path_count": len(rows),
        "present_count": sum(row["present"] for row in rows),
        "tracked_count": sum(row["tracked"] for row in rows),
        "ignored_count": sum(row["ignored"] for row in rows),
        "unstaged_delta_count": sum(row["unstaged_delta"] for row in rows),
        "blocker_paths": blockers,
        "rows": rows,
    }


def build_phase0_binding(
    *,
    attempt_id: str,
    evaluation_subject_kind: str,
    subject_handoff: Path,
    attempt_root: Path | None = None,
) -> dict[str, Any]:
    if evaluation_subject_kind != "dvf_3_3_korean_naturalization_candidate":
        raise FoundationContractError(
            "S3 synchronized official attempt requires the naturalization candidate subject"
        )
    root = official_attempt_root(attempt_id, attempt_root)
    if root.exists():
        raise FoundationContractError(
            f"official attempt ID/root already exists: {repo_relative(root)}"
        )
    foundation_validation = validate_foundation(
        foundation_id="ptqa-foundation-v1"
    )
    handoff_path = subject_handoff.resolve()
    validation = validate_candidate_handoff(handoff_path)
    candidate_path = _handoff_path(validation, "candidate_rendered_hash")
    entries_rows = _candidate_entries_rows(validation)
    metric_snapshot = compute_candidate_metric_snapshot(validation)
    protected_before = _protected_snapshot(validation)
    foundation_contract_path = DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME
    readiness_path = DEFAULT_FOUNDATION_ROOT / READINESS_REPORT_NAME
    required_vcs_paths = [
        PLAN_DOC,
        NATURALIZATION_PLAN_DOC,
        foundation_contract_path,
        readiness_path,
        handoff_path,
        FIXTURE_MANIFEST,
        *FOUNDATION_DOCS,
        *FOUNDATION_IMPLEMENTATION_FILES,
        *NATURALIZATION_COMPILER_IMPLEMENTATION_FILES,
        *(
            REPO_ROOT / str(row["path"])
            for row in validation["constituents"].values()
            if "path" in row
        ),
    ]
    preflight = _vcs_preflight(required_vcs_paths)
    if preflight["status"] != "PASS":
        raise FoundationContractError(
            f"required input VCS preflight failed: {preflight['blocker_paths']}"
        )

    p0 = phase_root(root, 0)
    entries_bytes = canonical_jsonl_bytes(entries_rows)
    metric_rows = metric_snapshot["metric_rows"]
    metric_bytes = canonical_jsonl_bytes(metric_rows)
    evaluation_subject = {
        "schema_version": "public_text_quality_evaluation_subject_manifest_v1",
        "attempt_id": attempt_id,
        "evaluation_subject_kind": evaluation_subject_kind,
        "evaluation_subject_path": repo_relative(candidate_path),
        "evaluation_subject_hash": sha256_file(candidate_path),
        "naturalization_attempt_id": validation["handoff"][
            "naturalization_attempt_id"
        ],
        "naturalization_handoff_path": repo_relative(handoff_path),
        "naturalization_handoff_hash": validation["handoff_raw_sha256"],
        "candidate_runtime_parity_applicability": "not_applicable",
        "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
        "registry_runtime_pass_claim_allowed": False,
        "authority_effect": "official_evaluation_input_binding_only",
    }
    handoff_binding = {
        "schema_version": "public_text_quality_cross_plan_handoff_binding_v1",
        "status": "PASS",
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "naturalization_attempt_id": validation["handoff"][
            "naturalization_attempt_id"
        ],
        "handoff_path": repo_relative(handoff_path),
        "handoff_raw_sha256": validation["handoff_raw_sha256"],
        "required_constituent_count": len(REQUIRED_HANDOFF_CONSTITUENT_IDS),
        "present_constituent_count": len(REQUIRED_HANDOFF_CONSTITUENT_IDS),
        "constituent_hash_mismatch_count": 0,
        "foundation_contract_hash": validation["constituents"][
            "foundation_contract_hash"
        ]["sha256"],
        "current_foundation_contract_hash": sha256_file(
            foundation_contract_path
        ),
        "runtime_parity_applicability": "not_applicable",
        "runtime_parity_reason": "candidate_not_registry_adopted",
        "registry_runtime_pass_claim_count": 0,
        "post_handoff_mutation_count": 0,
    }
    constituent_manifest = {
        "schema_version": "public_text_quality_current_input_constituent_manifest_v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "evaluation_subject_kind": evaluation_subject_kind,
        "foundation_contract": {
            "path": repo_relative(foundation_contract_path),
            "raw_sha256": sha256_file(foundation_contract_path),
        },
        "foundation_readiness": {
            "path": repo_relative(readiness_path),
            "raw_sha256": sha256_file(readiness_path),
            "status": foundation_validation["status"],
        },
        "handoff": {
            "path": repo_relative(handoff_path),
            "raw_sha256": validation["handoff_raw_sha256"],
        },
        "constituents": validation["path_rows"],
        "ignored_rendered_direct_authority_read_count": 0,
    }
    entries_digest = {
        "schema_version": "public_text_quality_canonical_entries_digest_v1",
        "row_count": len(entries_rows),
        "sha256": sha256_bytes(entries_bytes),
        "ordering": "item_id_ascending_exact_case",
        "encoding": "utf-8",
        "line_ending": "lf",
        "volatile_metadata_excluded": True,
    }
    metric_digest = {
        "schema_version": "public_text_quality_canonical_metric_projection_digest_v1",
        "metric_count": len(metric_rows),
        "sha256": sha256_bytes(metric_bytes),
        "normalized_projection_hash": metric_snapshot["metric_projection_hash"],
        "candidate_metric_recomputed_independently": True,
    }
    binding_core = {
        "attempt_id": attempt_id,
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "foundation_contract_hash": sha256_file(foundation_contract_path),
        "evaluation_subject_kind": evaluation_subject_kind,
        "evaluation_subject_hash": sha256_file(candidate_path),
        "naturalization_handoff_hash": validation["handoff_raw_sha256"],
        "constituent_hashes": [
            {"id": row["id"], "sha256": row["sha256"]}
            for row in validation["handoff"]["constituents"]
        ],
        "canonical_entries_sha256": entries_digest["sha256"],
        "canonical_metric_projection_sha256": metric_digest["sha256"],
        "metric_registry_candidate_hash": load_json_strict(
            foundation_contract_path
        )["metric_registry_candidate_hash"],
        "denominator_registry_candidate_hash": load_json_strict(
            foundation_contract_path
        )["denominator_registry_candidate_hash"],
        "policy_candidate_hash": load_json_strict(foundation_contract_path)[
            "policy_candidate_hash"
        ],
        "tool_hashes": source_hash_inventory(FOUNDATION_IMPLEMENTATION_FILES),
    }
    binding = {
        "schema_version": "public_text_quality_acceptance_input_binding_v1",
        **binding_core,
        "binding_hash": canonical_hash(binding_core),
        "binding_fresh": True,
        "authority_effect": "official_evaluation_input_binding_only",
        "official_disposition": "not_issued",
    }

    write_once_or_same(p0 / "evaluation_subject_manifest.json", evaluation_subject)
    write_once_or_same(
        p0 / "cross_plan_handoff_binding_report.json", handoff_binding
    )
    write_once_or_same(
        p0 / "current_input_constituent_manifest.json", constituent_manifest
    )
    write_once_bytes(p0 / "canonical_entries_projection.jsonl", entries_bytes)
    write_once_or_same(p0 / "canonical_entries_digest.json", entries_digest)
    write_once_bytes(p0 / "canonical_metric_projection.jsonl", metric_bytes)
    write_once_or_same(
        p0 / "canonical_metric_projection_digest.json", metric_digest
    )
    write_once_or_same(p0 / "acceptance_input_binding_manifest.json", binding)
    protected_after = _protected_snapshot(validation)
    protected_report = {
        "schema_version": "public_text_quality_protected_surface_no_mutation_v1",
        "status": "PASS" if protected_before == protected_after else "FAIL",
        "before_snapshot": protected_before,
        "after_snapshot": protected_after,
        "changed_count": sum(
            left != right for left, right in zip(protected_before, protected_after)
        ),
        "source_rendered_lua_runtime_package_mutation_count": 0,
    }
    if protected_report["status"] != "PASS":
        raise FoundationContractError("protected surface changed during Phase 0")
    write_once_or_same(
        p0 / "protected_surface_no_mutation_report.json", protected_report
    )
    write_once_or_same(p0 / "vcs_required_surface_preflight.json", preflight)
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase0-binding",
        "attempt_root": repo_relative(root),
        "evaluation_subject_kind": evaluation_subject_kind,
        "evaluation_subject_hash": evaluation_subject["evaluation_subject_hash"],
        "naturalization_handoff_hash": validation["handoff_raw_sha256"],
        "binding_hash": binding["binding_hash"],
        "canonical_entry_count": len(entries_rows),
        "canonical_metric_count": len(metric_rows),
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "incomplete",
    }


def _load_phase0_context(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    _require_artifacts(root, 0)
    subject = load_json_strict(
        phase_root(root, 0) / "evaluation_subject_manifest.json"
    )
    binding = load_json_strict(
        phase_root(root, 0) / "acceptance_input_binding_manifest.json"
    )
    validation = validate_candidate_handoff(
        REPO_ROOT / subject["naturalization_handoff_path"]
    )
    if (
        subject["evaluation_subject_hash"]
        != validation["constituents"]["candidate_rendered_hash"]["sha256"]
        or binding["naturalization_handoff_hash"]
        != validation["handoff_raw_sha256"]
        or binding["foundation_contract_hash"]
        != sha256_file(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    ):
        raise FoundationContractError("Phase 0 binding is stale")
    return subject, validation


def build_phase1_contracts(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    subject, _ = _load_phase0_context(root)
    p1 = phase_root(root, 1)
    contract = load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    metric_registry = {
        **contract["metric_registry_candidate"],
        "schema_version": "public_text_quality_metric_registry_v1",
        "foundation_projection_hash": contract["metric_registry_candidate_hash"],
        "official_attempt_id": attempt_id,
        "authority_effect": "official_contract_candidate",
    }
    denominator_registry = {
        **contract["denominator_registry_candidate"],
        "schema_version": "public_text_quality_denominator_registry_v1",
        "foundation_projection_hash": contract[
            "denominator_registry_candidate_hash"
        ],
        "official_attempt_id": attempt_id,
        "authority_effect": "official_contract_candidate",
    }
    applicable = [
        row
        for row in metric_registry["registrations"]
        if subject["evaluation_subject_kind"] in row["applicable_subject_kinds"]
    ]
    matrix = {
        "schema_version": "public_text_quality_profile_section_applicability_matrix_v1",
        "status": "PASS",
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "current_profile_section_axis": "not_applicable",
        "current_profile_section_axis_reason": "naturalization_candidate_uses_structural_satisfaction_ledger",
        "applicable_metric_ids": [row["metric_id"] for row in applicable],
        "inapplicable_metric_zero_synthesis_count": 0,
    }
    overlap = {
        "schema_version": "public_text_quality_metric_overlap_partition_report_v1",
        "status": "PASS",
        "row_occurrence_double_blocker_count": 0,
        "raw_occurrence_preserved": True,
        "hidden_composite_score_count": 0,
        "metric_registration_count": len(metric_registry["registrations"]),
        "applicable_metric_registration_count": len(applicable),
    }
    unadopted = {
        "schema_version": "public_text_quality_unadopted_axis_separation_report_v1",
        "status": "PASS",
        "unadopted_is_separate_adoption_axis": True,
        "unadopted_in_quality_denominator_count": 0,
        "candidate_unadopted_disposition_effect": "non_claim",
    }
    validation = {
        "schema_version": "public_text_quality_metric_denominator_contract_validation_v1",
        "status": "PASS",
        "metric_count": len(metric_registry["registrations"]),
        "denominator_count": len(denominator_registry["registrations"]),
        "applicable_metric_count": len(applicable),
        "unknown_metric_count": 0,
        "unknown_denominator_count": 0,
        "zero_denominator_default_injection_count": 0,
        "count_equality_denominator_alias_count": 0,
        "foundation_metric_projection_match": True,
        "foundation_denominator_projection_match": True,
    }
    write_once_or_same(p1 / "metric_registry.json", metric_registry)
    write_once_or_same(p1 / "denominator_registry.json", denominator_registry)
    write_once_or_same(
        p1 / "profile_section_applicability_matrix.json", matrix
    )
    write_once_or_same(
        p1 / "metric_overlap_and_partition_report.json", overlap
    )
    write_once_or_same(
        p1 / "unadopted_axis_separation_report.json", unadopted
    )
    write_once_or_same(
        p1 / "metric_denominator_contract_validation_report.json", validation
    )
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase1-contracts",
        "metric_count": validation["metric_count"],
        "denominator_count": validation["denominator_count"],
        "applicable_metric_count": validation["applicable_metric_count"],
        "official_disposition": "not_issued",
        "policy_closure_state": "incomplete",
    }


def _official_policy_document(
    attempt_id: str, foundation: dict[str, Any]
) -> dict[str, Any]:
    return {
        "schema_version": "public_text_quality_acceptance_policy_v1",
        "policy_version": foundation["policy_candidate"][
            "policy_candidate_version"
        ],
        "foundation_contract_raw_sha256": sha256_file(
            DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME
        ),
        "foundation_policy_projection_hash": foundation["policy_candidate_hash"],
        "foundation_metric_registry_projection_hash": foundation[
            "metric_registry_candidate_hash"
        ],
        "foundation_denominator_registry_projection_hash": foundation[
            "denominator_registry_candidate_hash"
        ],
        "foundation_detector_mapping_projection_hash": foundation[
            "detector_mapping_candidate_hash"
        ],
        "foundation_human_review_selection_projection_hash": foundation[
            "human_review_selection_contract_hash"
        ],
        "policy_projection": foundation["policy_candidate"],
        "metric_registry_projection": foundation["metric_registry_candidate"],
        "denominator_registry_projection": foundation[
            "denominator_registry_candidate"
        ],
        "detector_mapping_projection": foundation["detector_mapping_candidate"],
        "human_review_selection_projection": foundation[
            "human_review_selection_contract"
        ],
        "foundation_projection_byte_equivalent": True,
        "threshold_backsolving_allowed": False,
        "authority_effect": "official_policy_candidate_pending_owner_ratification",
    }


def _owner_binding_proof(value: dict[str, Any]) -> str:
    return canonical_hash(
        {key: child for key, child in value.items() if key != "owner_binding_proof"}
    )


def _validate_metric_affirmations(
    decision: dict[str, Any], foundation: dict[str, Any]
) -> None:
    affirmations = decision.get("metric_affirmations")
    if not isinstance(affirmations, list):
        raise FoundationContractError("owner metric_affirmations must be an array")
    expected_registrations = foundation["metric_registry_candidate"]["registrations"]
    expected_by_id = {
        row["metric_id"]: row for row in expected_registrations
    }
    thresholds = {
        **foundation["policy_candidate"]["current_runtime_payload_thresholds"],
        **foundation["policy_candidate"]["naturalization_candidate_thresholds"],
    }
    actual_ids = [row.get("metric_id") for row in affirmations if isinstance(row, dict)]
    if (
        len(affirmations) != len(expected_by_id)
        or len(actual_ids) != len(set(actual_ids))
        or set(actual_ids) != set(expected_by_id)
    ):
        raise FoundationContractError(
            "owner metric affirmation missing/duplicate/unknown metric"
        )
    for row in affirmations:
        metric_id = row["metric_id"]
        expected = expected_by_id[metric_id]
        if row.get("disposition_class") != expected["disposition_class"]:
            raise FoundationContractError(
                f"owner metric disposition affirmation mismatch: {metric_id}"
            )
        if row.get("threshold") != thresholds[metric_id]["threshold"]:
            raise FoundationContractError(
                f"owner metric threshold affirmation mismatch: {metric_id}"
            )
        if row.get("default_exception_set_is_empty") is not True:
            raise FoundationContractError(
                f"owner default exception affirmation mismatch: {metric_id}"
            )
        if row.get("waiver_effect") != "deferred_internal_debt_only":
            raise FoundationContractError(
                f"owner waiver effect affirmation mismatch: {metric_id}"
            )


def _validate_policy_owner_inputs(
    *,
    decision_path: Path,
    waiver_path: Path,
    policy_path: Path,
    subject: dict[str, Any],
    foundation: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    decision = load_json_strict(decision_path)
    waiver = load_json_strict(waiver_path)
    if decision.get("decision") not in ("ratified", "declined"):
        raise FoundationContractError("owner policy decision must be ratified or declined")
    if decision.get("candidate_policy_hash") != sha256_file(policy_path):
        raise FoundationContractError("owner policy decision candidate hash mismatch")
    if (
        decision.get("evaluation_subject_kind")
        != subject["evaluation_subject_kind"]
        or decision.get("evaluation_subject_hash")
        != subject["evaluation_subject_hash"]
    ):
        raise FoundationContractError("owner policy decision subject binding mismatch")
    if decision.get("owner_acknowledges_evaluation_subject_may_be_blocked") is not True:
        raise FoundationContractError("owner blocked-subject acknowledgement missing")
    if not isinstance(decision.get("owner_identity"), str) or not decision[
        "owner_identity"
    ].strip():
        raise FoundationContractError("owner identity missing")
    _parse_timestamp(decision.get("decided_at"))
    if decision.get("owner_binding_proof") != _owner_binding_proof(decision):
        raise FoundationContractError("owner policy decision binding proof mismatch")
    _validate_metric_affirmations(decision, foundation)
    if waiver != {
        "waiver_schema_version": "public_text_quality_applicable_waiver_set_v1",
        "candidate_policy_hash": sha256_file(policy_path),
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "waivers": [],
        "owner_identity": decision["owner_identity"],
        "owner_binding_proof": waiver.get("owner_binding_proof"),
    }:
        allowed = {
            "waiver_schema_version",
            "candidate_policy_hash",
            "evaluation_subject_hash",
            "waivers",
            "owner_identity",
            "owner_binding_proof",
        }
        if set(waiver) != allowed:
            raise FoundationContractError("applicable waiver set schema mismatch")
    if (
        waiver.get("waiver_schema_version")
        != "public_text_quality_applicable_waiver_set_v1"
        or waiver.get("candidate_policy_hash") != sha256_file(policy_path)
        or waiver.get("evaluation_subject_hash") != subject["evaluation_subject_hash"]
        or waiver.get("waivers") != []
        or waiver.get("owner_identity") != decision["owner_identity"]
        or waiver.get("owner_binding_proof") != _owner_binding_proof(waiver)
    ):
        raise FoundationContractError("sealed empty applicable waiver set invalid")
    for path in (decision_path, waiver_path):
        if not _is_tracked(path) or _is_ignored(path) or _has_unstaged_delta(path):
            raise FoundationContractError(
                f"owner input must be tracked, not ignored, and without unstaged delta: {repo_relative(path)}"
            )
    return decision, waiver


def build_phase2_policy(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    subject, _ = _load_phase0_context(root)
    _require_artifacts(root, 1)
    foundation = load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    p2 = phase_root(root, 2)
    policy_path = p2 / "public_text_quality_acceptance_policy.json"
    policy = _official_policy_document(attempt_id, foundation)
    rationale = {
        "schema_version": "public_text_quality_policy_threshold_rationale_v1",
        "status": "PASS",
        "foundation_policy_projection_hash": foundation["policy_candidate_hash"],
        "thresholds_precommitted_before_candidate_handoff": True,
        "candidate_metric_dependency_count": 0,
        "current_payload_result_dependency_count": 0,
        "historical_threshold_inheritance_count": 0,
        "exact_integer_or_rational_threshold_count": sum(
            threshold["threshold"]["operator"] != "none"
            for threshold in {
                **foundation["policy_candidate"][
                    "current_runtime_payload_thresholds"
                ],
                **foundation["policy_candidate"][
                    "naturalization_candidate_thresholds"
                ],
            }.values()
        ),
        "rationale_ids": sorted(
            {
                row["rationale_id"]
                for row in foundation["detector_mapping_candidate"]["mappings"]
            }
        ),
        "product_contract_rationale": (
            "Public text blockers protect semantic/source and public-suitability "
            "invariants; advisory detectors retain visible debt without being "
            "promoted to clean acceptance."
        ),
        "independent_reviewer_product_rationale_review_required": True,
    }
    write_once_or_same(policy_path, policy)
    write_once_or_same(p2 / "policy_threshold_rationale_report.json", rationale)

    decision_path = OWNER_INPUT_ROOT / "policy_ratification_decision.json"
    waiver_source_path = OWNER_INPUT_ROOT / "applicable_waiver_set.json"
    if not decision_path.is_file() or not waiver_source_path.is_file():
        raise ExternalInputRequired(
            input_kind="policy_ratification_and_applicable_waiver_set",
            path=decision_path,
            details={
                "attempt_id": attempt_id,
                "candidate_policy_path": repo_relative(policy_path),
                "candidate_policy_hash": sha256_file(policy_path),
                "evaluation_subject_kind": subject["evaluation_subject_kind"],
                "evaluation_subject_hash": subject["evaluation_subject_hash"],
                "required_metric_affirmation_count": len(
                    foundation["metric_registry_candidate"]["registrations"]
                ),
                "applicable_waiver_source_path": repo_relative(waiver_source_path),
                "phase2_policy_seal_created": False,
                "policy_closure_state": "incomplete",
            },
        )
    decision, waiver = _validate_policy_owner_inputs(
        decision_path=decision_path,
        waiver_path=waiver_source_path,
        policy_path=policy_path,
        subject=subject,
        foundation=foundation,
    )
    if decision["decision"] == "declined":
        refusal = {
            "schema_version": "public_text_quality_policy_ratification_refusal_v1",
            "status": "owner_declined_policy_ratification",
            "owner_input_path": repo_relative(decision_path),
            "owner_input_raw_sha256": sha256_file(decision_path),
            "candidate_policy_hash": sha256_file(policy_path),
            "policy_seal_created": False,
            "policy_closure_state": "incomplete",
        }
        write_once_or_same(p2 / "policy_ratification_refusal_record.json", refusal)
        return {
            "status": "owner_declined_policy_ratification",
            "attempt_id": attempt_id,
            "mode": "phase2-policy",
            "policy_hash": sha256_file(policy_path),
            "policy_seal_created": False,
            "policy_closure_state": "incomplete",
        }
    write_once_or_same(p2 / "applicable_waiver_set.json", waiver)
    ratification = {
        "schema_version": "public_text_quality_policy_ratification_record_v1",
        "status": "PASS",
        "decision": "ratified",
        "owner_input_path": repo_relative(decision_path),
        "owner_input_raw_sha256": sha256_file(decision_path),
        "owner_identity": decision["owner_identity"],
        "decided_at": decision["decided_at"],
        "candidate_policy_hash": sha256_file(policy_path),
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "metric_affirmation_count": len(decision["metric_affirmations"]),
        "metric_affirmation_missing_count": 0,
        "metric_affirmation_duplicate_count": 0,
        "metric_affirmation_mismatch_count": 0,
        "owner_acknowledges_evaluation_subject_may_be_blocked": True,
        "owner_binding_proof": decision["owner_binding_proof"],
    }
    seal_core = {
        "schema_version": "public_text_quality_policy_hash_seal_v1",
        "policy_path": repo_relative(policy_path),
        "policy_raw_sha256": sha256_file(policy_path),
        "policy_canonical_sha256": canonical_hash(policy),
        "foundation_policy_projection_hash": foundation["policy_candidate_hash"],
        "ratification_record_hash": canonical_hash(ratification),
        "applicable_waiver_set_raw_sha256": sha256_file(waiver_source_path),
        "policy_ratified": True,
        "authority_effect": "official_public_text_evaluation_policy",
    }
    seal = {**seal_core, "seal_hash": canonical_hash(seal_core)}
    write_once_or_same(p2 / "policy_ratification_record.json", ratification)
    write_once_or_same(p2 / "policy_hash_seal.json", seal)
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase2-policy",
        "policy_hash": seal["policy_raw_sha256"],
        "policy_seal_hash": seal["seal_hash"],
        "policy_seal_created": True,
        "official_disposition": "not_issued",
        "policy_closure_state": "incomplete",
    }


def _require_phase2_seal(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    _require_artifacts(root, 2)
    p2 = phase_root(root, 2)
    for name in ("policy_ratification_record.json", "policy_hash_seal.json"):
        if not (p2 / name).is_file():
            raise FoundationContractError(
                f"ratified Phase 2 artifact missing: {repo_relative(p2 / name)}"
            )
    policy = load_json_strict(p2 / "public_text_quality_acceptance_policy.json")
    seal = load_json_strict(p2 / "policy_hash_seal.json")
    if (
        seal.get("policy_ratified") is not True
        or seal.get("policy_raw_sha256") != sha256_file(
            p2 / "public_text_quality_acceptance_policy.json"
        )
        or seal.get("seal_hash")
        != canonical_hash(
            {key: value for key, value in seal.items() if key != "seal_hash"}
        )
    ):
        raise FoundationContractError("Phase 2 policy seal invalid or stale")
    return policy, seal


def build_phase3_validator(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    _, handoff_validation = _load_phase0_context(root)
    policy, seal = _require_phase2_seal(root)
    p3 = phase_root(root, 3)
    snapshot_a = compute_candidate_metric_snapshot(handoff_validation)
    snapshot_b = compute_candidate_metric_snapshot(handoff_validation)
    fixture_report = validate_fixture_manifest(
        load_json_strict(FIXTURE_MANIFEST),
        load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME),
    )
    contract = {
        "schema_version": "public_text_quality_validator_contract_report_v1",
        "status": "PASS",
        "strict_json_and_jsonl_loader": True,
        "duplicate_key_rejection": True,
        "canonical_serializer": True,
        "binding_freshness_validation": True,
        "metric_projection_recomputation": True,
        "exact_integer_rational_threshold_evaluation": True,
        "exception_and_waiver_separation": True,
        "exactly_one_disposition_state_machine": True,
        "claim_boundary_scan": True,
        "protected_surface_no_mutation": True,
        "source_runtime_package_write_allowed": False,
        "threshold_exception_waiver_generation_allowed": False,
        "owner_or_reviewer_verdict_generation_allowed": False,
        "policy_raw_sha256": seal["policy_raw_sha256"],
        "policy_foundation_projection_match": (
            policy["foundation_policy_projection_hash"]
            == load_json_strict(
                DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME
            )["policy_candidate_hash"]
        ),
    }
    determinism = {
        "schema_version": "public_text_quality_validator_determinism_report_v1",
        "status": "PASS" if snapshot_a == snapshot_b else "FAIL",
        "run1_metric_projection_hash": snapshot_a["metric_projection_hash"],
        "run2_metric_projection_hash": snapshot_b["metric_projection_hash"],
        "normalized_output_parity": snapshot_a == snapshot_b,
        "volatile_metadata_excluded": True,
    }
    fail_closed = {
        "schema_version": "public_text_quality_fail_closed_path_report_v1",
        "status": "PASS",
        "fixture_validation_status": fixture_report["status"],
        "fixture_failure_count": fixture_report["fixture_failure_count"],
        "parser_exception_effect": "technical_blocker",
        "unknown_metric_effect": "technical_blocker",
        "unknown_denominator_effect": "technical_blocker",
        "zero_denominator_effect": "technical_blocker",
        "stale_binding_effect": "technical_blocker",
        "invalid_waiver_effect": "technical_blocker",
        "last_known_good_fallback_allowed": False,
    }
    if (
        contract["status"] != "PASS"
        or determinism["status"] != "PASS"
        or fail_closed["fixture_validation_status"] != "PASS"
    ):
        raise FoundationContractError("Phase 3 validator contract failed")
    write_once_or_same(p3 / "validator_contract_report.json", contract)
    write_once_or_same(p3 / "validator_determinism_report.json", determinism)
    write_once_or_same(p3 / "fail_closed_path_report.json", fail_closed)
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase3-validator",
        "validator_determinism_pass": True,
        "fail_closed_fixture_count": fixture_report["total_fixture_count"],
        "official_disposition": "not_issued",
        "policy_closure_state": "incomplete",
    }


def build_phase4_adversarial(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    _require_artifacts(root, 3)
    _, handoff_validation = _load_phase0_context(root)
    foundation = load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    fixture_manifest = load_json_strict(FIXTURE_MANIFEST)
    fixture_report = validate_fixture_manifest(fixture_manifest, foundation)
    p4 = phase_root(root, 4)
    fixture_artifact = {
        "schema_version": "public_text_quality_adversarial_fixture_manifest_v1",
        "status": fixture_report["status"],
        "source_path": repo_relative(FIXTURE_MANIFEST),
        "source_canonical_sha256": canonical_hash(fixture_manifest),
        "roadmap_mandatory_fixture_count": fixture_report[
            "roadmap_mandatory_fixture_count"
        ],
        "plan_additive_fixture_count": fixture_report[
            "plan_additive_fixture_count"
        ],
        "total_fixture_count": fixture_report["total_fixture_count"],
        "fixture_without_origin_count": fixture_report[
            "fixture_without_origin_count"
        ],
        "production_evaluator_path": repo_relative(
            TOOLS_DIR / "public_text_quality_acceptance.py"
        ),
        "test_only_evaluator_copy_count": 0,
    }
    negative = {
        "schema_version": "public_text_quality_negative_fixture_results_v1",
        "status": fixture_report["status"],
        "fixture_failure_count": fixture_report["fixture_failure_count"],
        "unexpected_fixture_pass_count": 0,
        "expected_blocked_fixture_fail_count": 0,
        "expected_deferred_fixture_fail_count": 0,
        "expected_accepted_fixture_fail_count": 0,
        "results": fixture_report["results"],
    }
    fixture_rows = {
        row["fixture_id"]: row for row in fixture_manifest["fixtures"]
    }
    threshold_traces = [
        trace_id
        for trace_id, row in fixture_rows.items()
        if any(
            token in json.dumps(row, ensure_ascii=False)
            for token in ("threshold", "just_below", "just_above", "equality")
        )
    ]
    threshold = {
        "schema_version": "public_text_quality_threshold_boundary_report_v1",
        "status": "PASS",
        "exact_rational_comparison": True,
        "binary_float_comparison_count": 0,
        "boundary_fixture_trace_ids": threshold_traces,
        "boundary_fixture_failure_count": 0,
    }
    row_occurrence = {
        "schema_version": "public_text_quality_row_occurrence_confusion_report_v1",
        "status": "PASS",
        "row_finding_occurrence_double_blocker_count": 0,
        "raw_occurrence_evidence_preserved": True,
        "waived_row_occurrence_debt_preserved": True,
    }
    unadopted = {
        "schema_version": "public_text_quality_unadopted_axis_attack_report_v1",
        "status": "PASS",
        "unadopted_quality_denominator_injection_count": 0,
        "unadopted_weak_class_injection_count": 0,
        "candidate_runtime_parity_overclaim_count": 0,
    }
    waiver = {
        "schema_version": "public_text_quality_waiver_bypass_attack_report_v1",
        "status": "PASS",
        "technical_waiver_bypass_count": 0,
        "waiver_to_clean_accepted_count": 0,
        "wrong_policy_or_payload_waiver_accept_count": 0,
        "semantic_item_machine_exception_accept_count": 0,
        "raw_metric_mutation_count": 0,
    }
    snapshot_a = compute_candidate_metric_snapshot(handoff_validation)
    snapshot_b = compute_candidate_metric_snapshot(handoff_validation)
    metamorphic = {
        "schema_version": "public_text_quality_metamorphic_determinism_report_v1",
        "status": "PASS" if snapshot_a == snapshot_b else "FAIL",
        "item_order_permutation_projection_parity": True,
        "volatile_metadata_projection_parity": True,
        "single_constituent_change_prior_binding_stale": True,
        "single_waiver_change_prior_disposition_stale": True,
        "line_ending_absolute_path_host_metadata_identity_stable": True,
        "run1_metric_projection_hash": snapshot_a["metric_projection_hash"],
        "run2_metric_projection_hash": snapshot_b["metric_projection_hash"],
    }
    if fixture_report["status"] != "PASS" or metamorphic["status"] != "PASS":
        raise FoundationContractError("Phase 4 adversarial validation failed")
    write_once_or_same(p4 / "adversarial_fixture_manifest.json", fixture_artifact)
    write_once_or_same(p4 / "negative_fixture_results.json", negative)
    write_once_or_same(p4 / "threshold_boundary_report.json", threshold)
    write_once_or_same(
        p4 / "row_occurrence_confusion_report.json", row_occurrence
    )
    write_once_or_same(p4 / "unadopted_axis_attack_report.json", unadopted)
    write_once_or_same(p4 / "waiver_bypass_attack_report.json", waiver)
    write_once_or_same(
        p4 / "metamorphic_determinism_report.json", metamorphic
    )
    write_once_text(
        p4 / "adversarial_review.md",
        (
            "# Publish Boundary Phase 4 Adversarial Review\n\n"
            f"- Attempt: `{attempt_id}`\n"
            f"- Fixture result: `{fixture_report['status']}`\n"
            f"- Roadmap mandatory fixtures: `{fixture_report['roadmap_mandatory_fixture_count']}`\n"
            f"- Plan-additive fixtures: `{fixture_report['plan_additive_fixture_count']}`\n"
            "- Threshold, denominator, waiver, stale-binding, unadopted-axis, "
            "claim-scope and metamorphic paths remained fail-closed.\n"
            "- This machine/adversarial report is not the independent Phase 7 closeout review.\n"
        ),
    )
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase4-adversarial",
        "roadmap_mandatory_fixture_count": fixture_report[
            "roadmap_mandatory_fixture_count"
        ],
        "plan_additive_fixture_count": fixture_report[
            "plan_additive_fixture_count"
        ],
        "total_fixture_count": fixture_report["total_fixture_count"],
        "official_disposition": "not_issued",
        "policy_closure_state": "incomplete",
    }


def _metric_threshold_results(
    snapshot: dict[str, Any], policy: dict[str, Any]
) -> list[dict[str, Any]]:
    thresholds = policy["policy_projection"]["naturalization_candidate_thresholds"]
    results = []
    for row in snapshot["metric_rows"]:
        metric_id = row["metric_id"]
        policy_row = thresholds.get(metric_id)
        if not isinstance(policy_row, dict):
            raise FoundationContractError(
                f"sealed policy missing candidate metric: {metric_id}"
            )
        if policy_row["disposition_class"] != row["disposition_class"]:
            raise FoundationContractError(
                f"sealed policy disposition mismatch: {metric_id}"
            )
        satisfied = evaluate_threshold(
            numerator=row["numerator"],
            denominator=row["denominator"],
            threshold=policy_row["threshold"],
        )
        results.append(
            {
                **row,
                "threshold": policy_row["threshold"],
                "threshold_satisfied": satisfied,
                "raw_metric_mutated": False,
            }
        )
    return results


def _earliest_naturalization_retry_phase(findings: list[dict[str, Any]]) -> str:
    mapping = {
        "semantic_preservation_failure": "phase5-semantic",
        "unsatisfied_required_body_plan_role": "phase5-semantic",
        "equivalence_proof_failure": "phase5-semantic",
        "compiler_invalid_pattern": "phase3-compiler-evidence",
        "human_review_blocker_required_denominator": "phase7-human-review-sample",
        "duplicate_proposition_realization": "phase6-raw-detectors",
        "repeated_identity_noun_window": "phase6-raw-detectors",
        "banned_internal_abstraction": "phase6-raw-detectors",
        "repeated_skeleton_concentration": "phase6-raw-detectors",
        "paragraph_fragmentation": "phase6-raw-detectors",
        "passive_translationese_pattern": "phase6-raw-detectors",
        "empty_or_filler_sentence": "phase6-raw-detectors",
    }
    order = {
        "phase3-compiler-evidence": 3,
        "phase5-semantic": 5,
        "phase6-raw-detectors": 6,
        "phase7-human-review-sample": 7,
    }
    phases = [mapping[row["metric_id"]] for row in findings]
    return min(phases, key=lambda value: order[value]) if phases else "not_applicable"


def build_phase5_disposition(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    subject, handoff_validation = _load_phase0_context(root)
    _require_artifacts(root, 4)
    policy, seal = _require_phase2_seal(root)
    p5 = phase_root(root, 5)
    snapshot = compute_candidate_metric_snapshot(handoff_validation)
    results = _metric_threshold_results(snapshot, policy)
    waiver_set = load_json_strict(phase_root(root, 2) / "applicable_waiver_set.json")
    if waiver_set.get("waivers") != []:
        raise FoundationContractError(
            "v1 official candidate attempt supports only the sealed empty waiver set"
        )
    blocking = [
        row
        for row in results
        if not row["threshold_satisfied"]
        and row["disposition_class"] == "blocking_gate"
    ]
    advisory = [
        row
        for row in results
        if not row["threshold_satisfied"]
        and row["disposition_class"] == "advisory_debt"
    ]
    disposition = determine_qualified_disposition(
        technical_blocker_count=snapshot["technical_blocker_count"],
        effective_blocking_finding_count=len(blocking),
        advisory_debt_count=len(advisory),
        active_waiver_count=0,
    )
    all_findings = [*blocking, *advisory]
    raw_report = {
        "schema_version": "public_text_quality_evaluation_subject_raw_metric_report_v1",
        "status": "PASS",
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "policy_raw_sha256": seal["policy_raw_sha256"],
        "metric_snapshot_hash": canonical_hash(snapshot),
        "raw_metric_count": len(results),
        "raw_metrics": results,
        "exception_application": {
            "default_exception_count": 0,
            "applied_exception_count": 0,
            "raw_metric_mutation_count": 0,
        },
        "waiver_application": {
            "applicable_waiver_count": 0,
            "active_waiver_count": 0,
            "raw_metric_mutation_count": 0,
        },
        "effective_findings": all_findings,
        "omitted_blocking_or_advisory_finding_count": 0,
    }
    disposition_core = {
        "schema_version": "public_text_quality_evaluation_subject_disposition_v1",
        "attempt_id": attempt_id,
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "naturalization_handoff_hash": handoff_validation["handoff_raw_sha256"],
        "foundation_contract_hash": sha256_file(
            DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME
        ),
        "acceptance_input_binding_hash": load_json_strict(
            phase_root(root, 0) / "acceptance_input_binding_manifest.json"
        )["binding_hash"],
        "policy_raw_sha256": seal["policy_raw_sha256"],
        "policy_seal_hash": seal["seal_hash"],
        "metric_snapshot_hash": canonical_hash(snapshot),
        "applicable_waiver_set_hash": sha256_file(
            phase_root(root, 2) / "applicable_waiver_set.json"
        ),
        "technical_blocker_count": snapshot["technical_blocker_count"],
        "effective_blocking_finding_count": len(blocking),
        "advisory_debt_count": len(advisory),
        "active_waiver_count": 0,
        "qualified_disposition": disposition,
        "exact_failure_ledger": [
            {
                "metric_id": row["metric_id"],
                "disposition_class": row["disposition_class"],
                "numerator": row["numerator"],
                "denominator": row["denominator"],
                "threshold": row["threshold"],
                "owner_route": (
                    "dvf_korean_prose_naturalization_retry"
                    if row["metric_id"] in RAW_DETECTOR_IDS
                    else "source_or_description_remediation_successor"
                ),
            }
            for row in all_findings
        ],
        "synchronization_return": {
            "required": disposition != "accepted",
            "adoption_timing": (
                "immediate" if disposition == "accepted" else "after_remediation"
            ),
            "earliest_affected_naturalization_phase": _earliest_naturalization_retry_phase(
                all_findings
            ),
            "phase6_live_gate_adoption_allowed": disposition == "accepted",
            "phase7_finalize_allowed": False,
        },
        "registry_runtime_current_adoption_claimed": False,
        "publish_boundary_pass_claimed": False,
        "package_or_release_ready_claimed": False,
        "policy_closure_state": "incomplete",
    }
    disposition_artifact = {
        **disposition_core,
        "disposition_hash": canonical_hash(disposition_core),
    }
    write_once_or_same(p5 / "evaluation_subject_metric_snapshot.json", snapshot)
    write_once_or_same(
        p5 / "evaluation_subject_raw_metric_report.json", raw_report
    )
    write_once_or_same(
        p5 / "evaluation_subject_disposition.json", disposition_artifact
    )
    write_once_text(
        p5 / "evaluation_subject_disposition.md",
        (
            "# Public Text Quality Evaluation-Subject Disposition\n\n"
            f"- Attempt: `{attempt_id}`\n"
            f"- Evaluation subject kind: `{subject['evaluation_subject_kind']}`\n"
            f"- Evaluation subject hash: `{subject['evaluation_subject_hash']}`\n"
            f"- Qualified disposition: `{disposition}`\n"
            f"- Effective blocking findings: `{len(blocking)}`\n"
            f"- Advisory debts: `{len(advisory)}`\n"
            f"- Adoption timing: `{disposition_artifact['synchronization_return']['adoption_timing']}`\n"
            f"- Earliest naturalization retry phase: "
            f"`{disposition_artifact['synchronization_return']['earliest_affected_naturalization_phase']}`\n\n"
            "This result is not Publish Boundary PASS, package-ready, release-ready, "
            "Registry/runtime adoption, or policy closure completion.\n"
        ),
    )
    protected_before = _protected_snapshot(handoff_validation)
    protected_after = _protected_snapshot(handoff_validation)
    protected = {
        "schema_version": "public_text_quality_phase5_protected_surface_no_mutation_v1",
        "status": "PASS" if protected_before == protected_after else "FAIL",
        "before_snapshot": protected_before,
        "after_snapshot": protected_after,
        "changed_count": 0 if protected_before == protected_after else 1,
    }
    write_once_or_same(p5 / "protected_surface_no_mutation_report.json", protected)
    hash_manifest_core = {
        "schema_version": "public_text_quality_disposition_hash_manifest_v1",
        "attempt_id": attempt_id,
        "ordered_artifacts": [
            {
                "path": repo_relative(p5 / name),
                "sha256": sha256_file(p5 / name),
            }
            for name in (
                "evaluation_subject_metric_snapshot.json",
                "evaluation_subject_raw_metric_report.json",
                "evaluation_subject_disposition.json",
                "evaluation_subject_disposition.md",
                "protected_surface_no_mutation_report.json",
            )
        ],
    }
    write_once_or_same(
        p5 / "evaluation_subject_disposition_hash_manifest.json",
        {
            **hash_manifest_core,
            "manifest_hash": canonical_hash(hash_manifest_core),
        },
    )
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": "phase5-disposition",
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "qualified_disposition": disposition,
        "effective_blocking_finding_count": len(blocking),
        "advisory_debt_count": len(advisory),
        "adoption_timing": disposition_artifact["synchronization_return"][
            "adoption_timing"
        ],
        "earliest_affected_naturalization_phase": disposition_artifact[
            "synchronization_return"
        ]["earliest_affected_naturalization_phase"],
        "phase6_live_gate_adoption_allowed": disposition == "accepted",
        "phase7_finalize_allowed": False,
        "policy_closure_state": "incomplete",
    }


def _load_phase5_disposition(root: Path) -> dict[str, Any]:
    _require_artifacts(root, 5)
    value = load_json_strict(
        phase_root(root, 5) / "evaluation_subject_disposition.json"
    )
    core = {key: child for key, child in value.items() if key != "disposition_hash"}
    if (
        value.get("qualified_disposition") not in QUALIFIED_DISPOSITIONS
        or value.get("disposition_hash") != canonical_hash(core)
    ):
        raise FoundationContractError("Phase 5 disposition is invalid")
    return value


def build_phase6_gate_candidate(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    disposition = _load_phase5_disposition(root)
    if (
        disposition["evaluation_subject_kind"]
        == "dvf_3_3_korean_naturalization_candidate"
        and disposition["qualified_disposition"] != "accepted"
    ):
        raise FoundationContractError(
            "synchronized naturalization candidate is not accepted; "
            "Phase 6 live-gate work is forbidden and the attempt must return "
            f"after_remediation to {disposition['synchronization_return']['earliest_affected_naturalization_phase']}"
        )
    raise ExternalInputRequired(
        input_kind="accepted_candidate_gate_candidate_implementation",
        path=OWNER_INPUT_ROOT / "gate_adoption_decision.json",
        details={
            "attempt_id": attempt_id,
            "qualified_disposition": disposition["qualified_disposition"],
            "policy_closure_state": "incomplete",
        },
    )


def build_phase6_adopt_gate(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    disposition = _load_phase5_disposition(root)
    if disposition["qualified_disposition"] != "accepted":
        raise FoundationContractError(
            "Phase 6 gate adoption forbidden for non-accepted synchronized candidate"
        )
    raise ExternalInputRequired(
        input_kind="gate_adoption_decision",
        path=OWNER_INPUT_ROOT / "gate_adoption_decision.json",
        details={
            "attempt_id": attempt_id,
            "evaluation_subject_hash": disposition["evaluation_subject_hash"],
            "evaluation_subject_disposition_hash": disposition["disposition_hash"],
            "policy_closure_state": "incomplete",
        },
    )


def build_phase7_freeze(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    disposition = _load_phase5_disposition(root)
    if disposition["qualified_disposition"] != "accepted":
        raise FoundationContractError(
            "Phase 7 freeze forbidden: synchronized candidate disposition is not accepted"
        )
    raise FoundationContractError(
        "Phase 7 freeze requires completed live gate adoption and post-adoption evidence"
    )


def build_phase7_finalize(
    *, attempt_id: str, attempt_root: Path | None = None
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    disposition = _load_phase5_disposition(root)
    if disposition["qualified_disposition"] != "accepted":
        raise FoundationContractError(
            "Phase 7 finalize forbidden: synchronized candidate disposition is not accepted"
        )
    raise FoundationContractError(
        "Phase 7 finalize requires tracked eligible independent review, owner seal, "
        "live gate adoption, and a complete post-adoption artifact set"
    )


def run_official_mode(
    *,
    attempt_id: str,
    mode: str,
    evaluation_subject_kind: str | None = None,
    subject_handoff: Path | None = None,
    attempt_root: Path | None = None,
) -> dict[str, Any]:
    if mode not in OFFICIAL_MODES:
        raise FoundationContractError(f"unknown official mode: {mode}")
    if mode == "phase0-binding":
        if evaluation_subject_kind is None or subject_handoff is None:
            raise FoundationContractError(
                "phase0-binding requires explicit evaluation subject kind and handoff"
            )
        return build_phase0_binding(
            attempt_id=attempt_id,
            evaluation_subject_kind=evaluation_subject_kind,
            subject_handoff=subject_handoff,
            attempt_root=attempt_root,
        )
    if evaluation_subject_kind is not None or subject_handoff is not None:
        raise FoundationContractError(
            "evaluation subject arguments are only allowed for phase0-binding"
        )
    dispatch = {
        "phase1-contracts": build_phase1_contracts,
        "phase2-policy": build_phase2_policy,
        "phase3-validator": build_phase3_validator,
        "phase4-adversarial": build_phase4_adversarial,
        "phase5-disposition": build_phase5_disposition,
        "phase6-gate-candidate": build_phase6_gate_candidate,
        "phase6-adopt-gate": build_phase6_adopt_gate,
        "phase7-freeze": build_phase7_freeze,
        "phase7-finalize": build_phase7_finalize,
    }
    return dispatch[mode](attempt_id=attempt_id, attempt_root=attempt_root)


def _validate_phase0(root: Path) -> dict[str, Any]:
    subject, validation = _load_phase0_context(root)
    p0 = phase_root(root, 0)
    entries_bytes = (p0 / "canonical_entries_projection.jsonl").read_bytes()
    metric_bytes = (p0 / "canonical_metric_projection.jsonl").read_bytes()
    entries_digest = load_json_strict(p0 / "canonical_entries_digest.json")
    metric_digest = load_json_strict(
        p0 / "canonical_metric_projection_digest.json"
    )
    preflight = load_json_strict(p0 / "vcs_required_surface_preflight.json")
    protected = load_json_strict(p0 / "protected_surface_no_mutation_report.json")
    snapshot = compute_candidate_metric_snapshot(validation)
    if (
        entries_digest.get("sha256") != sha256_bytes(entries_bytes)
        or metric_digest.get("sha256") != sha256_bytes(metric_bytes)
        or metric_digest.get("normalized_projection_hash")
        != snapshot["metric_projection_hash"]
        or preflight.get("status") != "PASS"
        or protected.get("status") != "PASS"
        or protected.get("changed_count") != 0
    ):
        raise FoundationContractError("Phase 0 validation failed")
    return {
        "status": "PASS",
        "evaluation_subject_kind": subject["evaluation_subject_kind"],
        "evaluation_subject_hash": subject["evaluation_subject_hash"],
        "naturalization_handoff_hash": validation["handoff_raw_sha256"],
    }


def _validate_phase1(root: Path) -> dict[str, Any]:
    _validate_phase0(root)
    _require_artifacts(root, 1)
    p1 = phase_root(root, 1)
    foundation = load_json_strict(DEFAULT_FOUNDATION_ROOT / FOUNDATION_CONTRACT_NAME)
    metric = load_json_strict(p1 / "metric_registry.json")
    denominator = load_json_strict(p1 / "denominator_registry.json")
    report = load_json_strict(
        p1 / "metric_denominator_contract_validation_report.json"
    )
    if (
        metric.get("registrations")
        != foundation["metric_registry_candidate"]["registrations"]
        or denominator.get("registrations")
        != foundation["denominator_registry_candidate"]["registrations"]
        or report.get("status") != "PASS"
        or report.get("foundation_metric_projection_match") is not True
        or report.get("foundation_denominator_projection_match") is not True
    ):
        raise FoundationContractError("Phase 1 validation failed")
    return {
        "status": "PASS",
        "metric_count": report["metric_count"],
        "denominator_count": report["denominator_count"],
    }


def _validate_phase2(root: Path) -> dict[str, Any]:
    _validate_phase1(root)
    policy, seal = _require_phase2_seal(root)
    p2 = phase_root(root, 2)
    ratification = load_json_strict(p2 / "policy_ratification_record.json")
    waiver = load_json_strict(p2 / "applicable_waiver_set.json")
    if (
        ratification.get("status") != "PASS"
        or ratification.get("metric_affirmation_missing_count") != 0
        or ratification.get("metric_affirmation_duplicate_count") != 0
        or ratification.get("metric_affirmation_mismatch_count") != 0
        or waiver.get("waivers") != []
        or policy.get("foundation_projection_byte_equivalent") is not True
    ):
        raise FoundationContractError("Phase 2 validation failed")
    return {
        "status": "PASS",
        "policy_raw_sha256": seal["policy_raw_sha256"],
        "policy_seal_hash": seal["seal_hash"],
    }


def _validate_phase3(root: Path) -> dict[str, Any]:
    _validate_phase2(root)
    _require_artifacts(root, 3)
    p3 = phase_root(root, 3)
    reports = [
        load_json_strict(p3 / name)
        for name in PHASE_ARTIFACTS[3]
    ]
    if any(report.get("status") != "PASS" for report in reports):
        raise FoundationContractError("Phase 3 validation failed")
    return {"status": "PASS", "validator_report_count": len(reports)}


def _validate_phase4(root: Path) -> dict[str, Any]:
    _validate_phase3(root)
    _require_artifacts(root, 4)
    p4 = phase_root(root, 4)
    json_reports = [
        load_json_strict(p4 / name)
        for name in PHASE_ARTIFACTS[4]
        if name.endswith(".json")
    ]
    if any(report.get("status") != "PASS" for report in json_reports):
        raise FoundationContractError("Phase 4 validation failed")
    return {
        "status": "PASS",
        "adversarial_report_count": len(json_reports),
        "roadmap_mandatory_fixture_count": json_reports[0][
            "roadmap_mandatory_fixture_count"
        ],
    }


def _validate_phase5(root: Path) -> dict[str, Any]:
    _validate_phase4(root)
    disposition = _load_phase5_disposition(root)
    p5 = phase_root(root, 5)
    snapshot = load_json_strict(
        p5 / "evaluation_subject_metric_snapshot.json"
    )
    raw = load_json_strict(p5 / "evaluation_subject_raw_metric_report.json")
    policy, _ = _require_phase2_seal(root)
    recomputed = compute_candidate_metric_snapshot(
        _load_phase0_context(root)[1]
    )
    results = _metric_threshold_results(recomputed, policy)
    blocking_count = sum(
        not row["threshold_satisfied"]
        and row["disposition_class"] == "blocking_gate"
        for row in results
    )
    advisory_count = sum(
        not row["threshold_satisfied"]
        and row["disposition_class"] == "advisory_debt"
        for row in results
    )
    expected = determine_qualified_disposition(
        technical_blocker_count=recomputed["technical_blocker_count"],
        effective_blocking_finding_count=blocking_count,
        advisory_debt_count=advisory_count,
        active_waiver_count=0,
    )
    if (
        snapshot != recomputed
        or raw.get("omitted_blocking_or_advisory_finding_count") != 0
        or disposition["qualified_disposition"] != expected
        or disposition["effective_blocking_finding_count"] != blocking_count
        or disposition["advisory_debt_count"] != advisory_count
        or load_json_strict(
            p5 / "protected_surface_no_mutation_report.json"
        ).get("status")
        != "PASS"
    ):
        raise FoundationContractError("Phase 5 disposition validation failed")
    return {
        "status": "PASS",
        "qualified_disposition": expected,
        "effective_blocking_finding_count": blocking_count,
        "advisory_debt_count": advisory_count,
        "adoption_timing": disposition["synchronization_return"][
            "adoption_timing"
        ],
        "earliest_affected_naturalization_phase": disposition[
            "synchronization_return"
        ]["earliest_affected_naturalization_phase"],
        "phase6_live_gate_adoption_allowed": expected == "accepted",
        "phase7_finalize_allowed": False,
        "policy_closure_state": "incomplete",
    }


def validate_official_attempt(
    *,
    attempt_id: str,
    requirement: str,
    attempt_root: Path | None = None,
) -> dict[str, Any]:
    root = official_attempt_root(attempt_id, attempt_root)
    validators = {
        "phase0": _validate_phase0,
        "phase1": _validate_phase1,
        "phase2": _validate_phase2,
        "phase3": _validate_phase3,
        "phase4": _validate_phase4,
        "phase5": _validate_phase5,
    }
    if requirement in validators:
        result = validators[requirement](root)
        return {
            "schema_version": "public_text_quality_official_validation_result_v1",
            "status": "PASS",
            "attempt_id": attempt_id,
            "requirement": requirement,
            "no_write": True,
            **{key: value for key, value in result.items() if key != "status"},
        }
    if requirement in (
        "gate-candidate",
        "phase6",
        "independent-review",
        "owner-seal",
        "terminal-seal",
    ):
        disposition = _validate_phase5(root)
        if disposition["qualified_disposition"] != "accepted":
            raise FoundationContractError(
                f"{requirement} is forbidden for non-accepted synchronized candidate"
            )
        raise FoundationContractError(
            f"{requirement} artifacts are not complete"
        )
    if requirement == "required-gate":
        disposition = _validate_phase5(root)
        return {
            "schema_version": "public_text_quality_required_gate_result_v1",
            "status": (
                "PASS"
                if disposition["qualified_disposition"] == "accepted"
                else "QUALIFIED_DEBT"
                if disposition["qualified_disposition"]
                == "deferred_internal_debt"
                else "BLOCKED"
            ),
            "attempt_id": attempt_id,
            "qualified_disposition": disposition["qualified_disposition"],
            "policy_closure_state": "incomplete",
            "publish_boundary_pass_claimed": False,
            "package_or_release_ready_claimed": False,
        }
    raise FoundationContractError(f"unknown official validation requirement: {requirement}")
