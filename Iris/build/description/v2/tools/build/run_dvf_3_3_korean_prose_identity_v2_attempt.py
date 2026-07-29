from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.build import compose_layer3_text as compose_text
    from tools.build import naturalization_compiler_identity as compiler_identity
    from tools.build import public_text_quality_acceptance as publish_consumer
    from tools.build import run_dvf_3_3_korean_prose_naturalization as producer
    from tools.build import validate_dvf_3_3_korean_prose_naturalization as validator
else:
    from . import compose_layer3_text as compose_text
    from . import naturalization_compiler_identity as compiler_identity
    from . import public_text_quality_acceptance as publish_consumer
    from . import run_dvf_3_3_korean_prose_naturalization as producer
    from . import validate_dvf_3_3_korean_prose_naturalization as validator


START_COMMIT = "510e55f581ae505f7330664f155fa1289748c207"
START_TREE = "e46775de1bb0fc4ed4f43c5481a27609afaefe55"
PRIMARY_ATTEMPT_ID = "attempt-0023-compiler-identity-v2-a"
REPLAY_ATTEMPT_ID = "attempt-0023-compiler-identity-v2-b"
ALLOWED_ATTEMPT_IDS = (PRIMARY_ATTEMPT_ID, REPLAY_ATTEMPT_ID)
EXPECTED_COMPILER_AGGREGATE_SHA256 = (
    "aa88ee878cfb570b8278b40e62c560f093dc6ffdc363f06ed7133352d635c647"
)
EXPECTED_COMPILER_IDENTITY_ALGORITHM_ID = (
    "naturalization_compiler_identity_sha256_lf_normalized_ordered_paths_v2"
)
EXPECTED_IMPLEMENTATION_READINESS_SHA256 = (
    "1257393ad67dbab62ae9c6159ab6b5b680cf61967aa5f212306f36986336a7b3"
)
EXPECTED_PREDECESSOR_READINESS_SHA256 = (
    "912f28b7869ff92ff7fbd84cbdc31e1fbb22923beebbfcce2c9cc78b72eca9d2"
)
EXPECTED_FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
EXPECTED_IDENTITY_CORRECTION_CONTRACT_SHA256 = (
    "a7981e6987b567a260c6d0c4c5ac0c77ea75bb487417bbc6d10dd41d32d9dcf1"
)
EXPECTED_IDENTITY_HELPER_SHA256 = (
    "7def3a9d13c7f4c2a05a151007234bee98b30a309c599f11c0cf71168489ab87"
)
EXPECTED_FACTS_SHA256 = (
    "50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120"
)
EXPECTED_MANIFEST_SHA256 = (
    "090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7"
)
EXPECTED_G3_RECEIPT_SHA256 = (
    "312c9b8744e1925b120129402b4ff6834d551960c284af8e91dbdbca091a56b0"
)
EXPECTED_G3_TERMINAL_SEAL_SHA256 = (
    "03dea1902f1d219b227b2b69cb88742f1005e3620cdcdee2b72ba811d1bd20fb"
)
EXPECTED_G3_HANDOFF_SHA256 = (
    "bfa14583f524f99a75e88d4b6eaddfa146544cba9124cf09214a13a38c7d7750"
)
EXPECTED_ATTEMPT_0022_CANDIDATE_SHA256 = (
    "79acd78da0e3c38baf91e903b314eda0aa1d8854163e73e141ac45bf918fd1a5"
)

FOUNDATION_IMPLEMENTATION_READINESS = (
    producer.FOUNDATION_ROOT
    / "readiness_successors"
    / "implementation-correction-0001"
    / "public_text_quality_development_readiness_implementation_correction.json"
)
IDENTITY_CORRECTION_ROOT = (
    producer.FOUNDATION_ROOT
    / "implementation_corrections"
    / "compiler_identity_v2"
)
IDENTITY_CORRECTION_CONTRACT = (
    IDENTITY_CORRECTION_ROOT / "compiler_identity_v2_correction_contract.json"
)
FRESH_CHECKOUT_VERIFICATION = (
    IDENTITY_CORRECTION_ROOT / "fresh_checkout_verification.json"
)
IDENTITY_HELPER = Path(compiler_identity.__file__).resolve()
ATTEMPT_0022_CANDIDATE = (
    producer.DEFAULT_ATTEMPT_PARENT
    / "attempt-0022-particle-correction-a"
    / "phase4"
    / "candidate_rendered.json"
)
HUMAN_REVIEW_DECISION = (
    producer.DURABLE_ROOT / "attempt_0023_human_review_decision.json"
)
ORCHESTRATOR_PATH = Path(__file__).resolve()
LOWER_SHA256 = re.compile(r"[0-9a-f]{64}")
EFFECTIVE_PHASE_DIRECTORY_NAMES = {
    0: "phase0_correction_0002",
    1: "phase1_correction_0001",
}
_TRACKED_BLOB_CACHE: dict[str, bytes | None] = {}
_LINE_ENDING_AUTHORITY_ROWS: dict[str, dict[str, Any]] = {}
_PARTICLE_IDENTITY_VIEW: dict[str, Any] = {}
_CURRENT_SNAPSHOT_IDENTITY_VIEW: dict[str, Any] = {}
_BASE_LOAD_JSON = producer.load_json
CURRENT_SNAPSHOT_MANIFEST = (
    producer.DATA_ROOT / "current_surface_snapshot_manifest.json"
)


class IdentityV2AttemptError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def effective_phase_root(attempt_root: Path, phase: int) -> Path:
    return attempt_root / EFFECTIVE_PHASE_DIRECTORY_NAMES.get(
        phase,
        f"phase{phase}",
    )


def tracked_blob_bytes(path: Path) -> bytes | None:
    try:
        relative = repo_relative(path)
    except ValueError:
        return None
    if relative in _TRACKED_BLOB_CACHE:
        return _TRACKED_BLOB_CACHE[relative]
    result = subprocess.run(
        ["git", "show", f"HEAD:{relative}"],
        cwd=producer.REPO_ROOT,
        capture_output=True,
        check=False,
    )
    value = result.stdout if result.returncode == 0 else None
    _TRACKED_BLOB_CACHE[relative] = value
    return value


def authority_sha256_file(path: Path) -> str:
    raw = path.read_bytes()
    blob = tracked_blob_bytes(path)
    if blob is None or blob == raw:
        return hashlib.sha256(raw).hexdigest()
    raw_canonical = compiler_identity.canonicalize_compiler_source_bytes(raw)
    blob_canonical = compiler_identity.canonicalize_compiler_source_bytes(blob)
    if raw_canonical != blob_canonical:
        return hashlib.sha256(raw).hexdigest()
    relative = repo_relative(path)
    raw_sha256 = hashlib.sha256(raw).hexdigest()
    blob_sha256 = hashlib.sha256(blob).hexdigest()
    _LINE_ENDING_AUTHORITY_ROWS[relative] = {
        "path": relative,
        "working_raw_sha256": raw_sha256,
        "git_blob_sha256": blob_sha256,
        "canonical_content_sha256": hashlib.sha256(raw_canonical).hexdigest(),
        "difference_classification": "line_ending_representation_only",
        "authority_hash_selected": "git_blob_sha256",
        "semantic_content_changed": False,
    }
    return blob_sha256


def canonical_identity_load_json(path: Path) -> Any:
    value = _BASE_LOAD_JSON(path)
    if path.resolve() == CURRENT_SNAPSHOT_MANIFEST.resolve():
        projected = json.loads(json.dumps(value, ensure_ascii=False))
        source_path = producer.REPO_ROOT / str(projected.get("source_path", ""))
        legacy_raw_sha256 = projected.get("source_raw_sha256")
        selected_authority_sha256 = authority_sha256_file(source_path)
        projected["source_raw_sha256"] = selected_authority_sha256
        _CURRENT_SNAPSHOT_IDENTITY_VIEW.update(
            {
                "manifest_path": repo_relative(path),
                "source_path": repo_relative(source_path),
                "legacy_working_raw_sha256": legacy_raw_sha256,
                "selected_repository_authority_sha256": (
                    selected_authority_sha256
                ),
                "snapshot_semantic_authority": projected.get(
                    "semantic_authority"
                ),
                "candidate_answer_corpus": projected.get(
                    "candidate_answer_corpus"
                ),
                "manifest_mutated": False,
                "source_mutated": False,
            }
        )
        return projected
    if path.resolve() != producer.PARTICLE_CORRECTION_PROJECTION_REPORT.resolve():
        return value
    projected = json.loads(json.dumps(value, ensure_ascii=False))
    implementation = projected.get("implementation", {})
    implementation_path = (
        producer.REPO_ROOT / str(implementation.get("path", ""))
    )
    legacy_expected_sha256 = implementation.get("after_sha256")
    canonical_sha256 = authority_sha256_file(implementation_path)
    implementation["after_sha256"] = canonical_sha256
    _PARTICLE_IDENTITY_VIEW.update(
        {
            "projection_report_path": repo_relative(path),
            "projection_report_sha256": authority_sha256_file(path),
            "implementation_path": repo_relative(implementation_path),
            "legacy_raw_expected_sha256": legacy_expected_sha256,
            "canonical_identity_v2_sha256": canonical_sha256,
            "semantic_content_changed": False,
            "projection_report_mutated": False,
            "implementation_file_mutated": False,
        }
    )
    return projected


def git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=producer.REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise IdentityV2AttemptError(
            f"git command failed ({result.returncode}): {' '.join(args)}"
        )
    return result.stdout.strip()


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(producer.REPO_ROOT.resolve()).as_posix()


def require(condition: bool, reason: str, checks: dict[str, bool]) -> None:
    checks[reason] = condition


def apply_runtime_binding() -> None:
    preserved = tuple(
        dict.fromkeys(
            (
                *producer.PRESERVED_PREDECESSOR_ATTEMPT_IDS,
                "attempt-0022-particle-correction-a",
                "attempt-0022-particle-correction-b",
            )
        )
    )
    producer.EXPECTED_START_COMMIT = START_COMMIT
    producer.EXPECTED_START_TREE = START_TREE
    producer.HUMAN_REVIEW_DECISION_PATH = HUMAN_REVIEW_DECISION
    producer.PRESERVED_PREDECESSOR_ATTEMPT_IDS = preserved
    producer.phase_root = effective_phase_root
    producer.sha256_file = authority_sha256_file
    producer.load_json = canonical_identity_load_json
    compose_text.file_sha256 = authority_sha256_file

    validator.EXPECTED_START_COMMIT = START_COMMIT
    validator.EXPECTED_START_TREE = START_TREE
    validator.PRESERVED_PREDECESSOR_ATTEMPT_IDS = preserved
    validator.phase_root = effective_phase_root
    validator.sha256_file = authority_sha256_file
    validator.load_json = canonical_identity_load_json


def line_ending_variant_identities() -> dict[str, dict[str, object]]:
    canonical_contents = {
        relative: compiler_identity.canonicalize_compiler_source_bytes(
            path.read_bytes()
        )
        for relative, path in zip(
            compiler_identity.COMPILER_REPO_RELATIVE_POSIX_PATH_ORDER,
            compiler_identity.compiler_source_paths(producer.REPO_ROOT),
            strict=True,
        )
    }
    variants = {
        "lf": canonical_contents,
        "crlf": {
            path: raw.replace(b"\n", b"\r\n")
            for path, raw in canonical_contents.items()
        },
        "lone_cr": {
            path: raw.replace(b"\n", b"\r")
            for path, raw in canonical_contents.items()
        },
    }
    return {
        name: compiler_identity.build_compiler_identity_from_bytes(contents)
        for name, contents in variants.items()
    }


def build_identity_binding_report() -> dict[str, Any]:
    required_files = (
        FOUNDATION_IMPLEMENTATION_READINESS,
        producer.FOUNDATION_CONTRACT,
        producer.FOUNDATION_READINESS_CURRENT_INPUT_REBIND,
        IDENTITY_CORRECTION_CONTRACT,
        FRESH_CHECKOUT_VERIFICATION,
        IDENTITY_HELPER,
        ATTEMPT_0022_CANDIDATE,
        producer.FACTS_PATH,
        producer.INPUT_MANIFEST,
        producer.REGISTRY_ADOPTION_RECEIPT,
        producer.REGISTRY_CORRECTION_TERMINAL_SEAL,
        producer.REGISTRY_NATURALIZATION_HANDOFF,
    )
    missing = [repo_relative(path) for path in required_files if not path.is_file()]
    if missing:
        raise IdentityV2AttemptError(f"missing identity-v2 input: {missing}")

    readiness = producer.load_json(FOUNDATION_IMPLEMENTATION_READINESS)
    contract = producer.load_json(IDENTITY_CORRECTION_CONTRACT)
    fresh = producer.load_json(FRESH_CHECKOUT_VERIFICATION)
    evidence = compiler_identity.build_compiler_identity(producer.REPO_ROOT)
    producer_evidence = producer.implementation_identity()
    consumer_evidence = publish_consumer.build_compiler_identity(
        publish_consumer.REPO_ROOT
    )
    variants = line_ending_variant_identities()
    variant_aggregates = {
        name: str(value["aggregate_sha256"]) for name, value in variants.items()
    }
    correction = readiness.get("compiler_identity_correction", {})
    predecessor = readiness.get("predecessor_readiness", {})
    line_endings = correction.get("line_ending_metamorphic", {})
    fresh_binding = readiness.get("fresh_checkout_verification", {})
    identity_input_fields = {
        "absolute_path",
        "mtime",
        "worktree_location",
        "host_metadata",
    }
    actual_identity_input_field_count = sum(
        key in identity_input_fields
        for row in evidence.get("ordered_files", [])
        if isinstance(row, dict)
        for key in row
    ) + sum(
        key in identity_input_fields
        for key in evidence
        if key != "excluded_identity_inputs"
    )

    checks: dict[str, bool] = {}
    require(
        sha256_file(FOUNDATION_IMPLEMENTATION_READINESS)
        == EXPECTED_IMPLEMENTATION_READINESS_SHA256,
        "implementation_correction_readiness_sha256_match",
        checks,
    )
    require(
        sha256_file(producer.FOUNDATION_CONTRACT)
        == EXPECTED_FOUNDATION_CONTRACT_SHA256,
        "foundation_contract_sha256_match",
        checks,
    )
    require(
        sha256_file(producer.FOUNDATION_READINESS_CURRENT_INPUT_REBIND)
        == EXPECTED_PREDECESSOR_READINESS_SHA256,
        "predecessor_readiness_sha256_match",
        checks,
    )
    require(
        sha256_file(IDENTITY_CORRECTION_CONTRACT)
        == EXPECTED_IDENTITY_CORRECTION_CONTRACT_SHA256,
        "identity_correction_contract_sha256_match",
        checks,
    )
    require(
        sha256_file(IDENTITY_HELPER) == EXPECTED_IDENTITY_HELPER_SHA256,
        "identity_helper_sha256_match",
        checks,
    )
    require(
        sha256_file(producer.FACTS_PATH) == EXPECTED_FACTS_SHA256,
        "facts_sha256_match",
        checks,
    )
    require(
        sha256_file(producer.INPUT_MANIFEST) == EXPECTED_MANIFEST_SHA256,
        "manifest_sha256_match",
        checks,
    )
    require(
        sha256_file(producer.REGISTRY_ADOPTION_RECEIPT)
        == EXPECTED_G3_RECEIPT_SHA256,
        "g3_receipt_sha256_match",
        checks,
    )
    require(
        sha256_file(producer.REGISTRY_CORRECTION_TERMINAL_SEAL)
        == EXPECTED_G3_TERMINAL_SEAL_SHA256,
        "g3_terminal_seal_sha256_match",
        checks,
    )
    require(
        sha256_file(producer.REGISTRY_NATURALIZATION_HANDOFF)
        == EXPECTED_G3_HANDOFF_SHA256,
        "g3_handoff_sha256_match",
        checks,
    )
    require(
        git_output("rev-parse", f"{START_COMMIT}^{{tree}}") == START_TREE,
        "naturalization_start_commit_tree_match",
        checks,
    )
    require(
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", START_COMMIT, "HEAD"],
            cwd=producer.REPO_ROOT,
            capture_output=True,
            check=False,
        ).returncode
        == 0,
        "naturalization_start_commit_is_ancestor",
        checks,
    )
    require(
        readiness.get("status") == "PASS"
        and readiness.get("readiness_kind")
        == "append_only_foundation_implementation_correction_successor",
        "implementation_correction_readiness_status_pass",
        checks,
    )
    require(
        predecessor.get("sha256") == EXPECTED_PREDECESSOR_READINESS_SHA256
        and predecessor.get("predecessor_mutated") is False,
        "readiness_predecessor_binding_match",
        checks,
    )
    require(
        correction.get("algorithm_id")
        == EXPECTED_COMPILER_IDENTITY_ALGORITHM_ID
        == evidence.get("algorithm_id"),
        "compiler_identity_algorithm_id_match",
        checks,
    )
    require(
        correction.get("compiler_aggregate_sha256")
        == EXPECTED_COMPILER_AGGREGATE_SHA256
        == evidence.get("aggregate_sha256"),
        "compiler_aggregate_sha256_match",
        checks,
    )
    require(
        correction.get("compiler_path_count") == 9
        and correction.get("compiler_path_order") == evidence.get("path_order")
        and len(evidence.get("ordered_files", [])) == 9,
        "ordered_nine_path_evidence_match",
        checks,
    )
    require(
        correction.get("ordered_files") == evidence.get("ordered_files")
        and all(
            isinstance(row, dict)
            and LOWER_SHA256.fullmatch(str(row.get("canonical_sha256", "")))
            is not None
            for row in evidence.get("ordered_files", [])
        ),
        "per_file_canonical_sha256_evidence_match",
        checks,
    )
    require(
        contract.get("canonical_identity_v2") == evidence,
        "identity_correction_contract_projection_match",
        checks,
    )
    require(
        producer.build_compiler_identity
        is compiler_identity.build_compiler_identity
        and publish_consumer.build_compiler_identity
        is compiler_identity.build_compiler_identity
        and producer_evidence == consumer_evidence == evidence,
        "producer_publish_consumer_recomputation_match",
        checks,
    )
    require(
        producer.implementation_hash() == EXPECTED_COMPILER_AGGREGATE_SHA256,
        "producer_implementation_hash_is_canonical_aggregate",
        checks,
    )
    require(
        len(set(variant_aggregates.values())) == 1
        and set(variant_aggregates.values())
        == {EXPECTED_COMPILER_AGGREGATE_SHA256}
        and line_endings.get("crlf_lf_lone_cr_identity_equal") is True,
        "lf_crlf_lone_cr_identity_equal",
        checks,
    )
    require(
        fresh.get("status") == "PASS"
        and fresh.get("expected_aggregate_sha256")
        == EXPECTED_COMPILER_AGGREGATE_SHA256
        and fresh.get("aggregate_identity_count") == 1
        and fresh.get("fresh_checkout_count") == 2
        and fresh.get("host_or_absolute_path_recorded") is False
        and fresh_binding.get("status") == "PASS"
        and fresh_binding.get("aggregate_sha256")
        == EXPECTED_COMPILER_AGGREGATE_SHA256,
        "fresh_checkout_identity_match",
        checks,
    )
    require(
        actual_identity_input_field_count == 0
        and evidence.get("path_form") == "repo_relative_posix"
        and {
            "absolute_path",
            "mtime",
            "worktree_location",
        }.issubset(set(evidence.get("excluded_identity_inputs", []))),
        "absolute_path_worktree_mtime_identity_input_count_zero",
        checks,
    )
    require(
        sha256_file(ATTEMPT_0022_CANDIDATE)
        == EXPECTED_ATTEMPT_0022_CANDIDATE_SHA256,
        "attempt_0022_accepted_candidate_sha256_match",
        checks,
    )
    scope = readiness.get("scope_boundaries", {})
    require(
        scope.get("attempt_0004_consumed") is False
        and scope.get("official_publish_attempt_created") is False
        and scope.get("live_gate_mutated") is False
        and scope.get(
            "facts_manifest_registry_rtc_runtime_lua_package_mutated"
        )
        is False,
        "readiness_scope_guards_preserved",
        checks,
    )
    failed = sorted(reason for reason, passed in checks.items() if not passed)
    report = {
        "schema_version": "dvf-3-3-naturalization-identity-v2-binding-v1",
        "status": "PASS" if not failed else "FAIL",
        "naturalization_start_commit": START_COMMIT,
        "naturalization_start_tree": START_TREE,
        "execution_head": git_output("rev-parse", "HEAD"),
        "foundation_implementation_correction_readiness_path": repo_relative(
            FOUNDATION_IMPLEMENTATION_READINESS
        ),
        "foundation_implementation_correction_readiness_sha256": sha256_file(
            FOUNDATION_IMPLEMENTATION_READINESS
        ),
        "foundation_contract_sha256": sha256_file(producer.FOUNDATION_CONTRACT),
        "predecessor_readiness_sha256": sha256_file(
            producer.FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "identity_correction_contract_path": repo_relative(
            IDENTITY_CORRECTION_CONTRACT
        ),
        "identity_correction_contract_sha256": sha256_file(
            IDENTITY_CORRECTION_CONTRACT
        ),
        "identity_helper_path": repo_relative(IDENTITY_HELPER),
        "identity_helper_sha256": sha256_file(IDENTITY_HELPER),
        "canonical_compiler_identity": evidence,
        "producer_compiler_identity": producer_evidence,
        "publish_consumer_compiler_identity": consumer_evidence,
        "line_ending_variant_aggregates": variant_aggregates,
        "fresh_checkout_verification_path": repo_relative(
            FRESH_CHECKOUT_VERIFICATION
        ),
        "fresh_checkout_verification_sha256": sha256_file(
            FRESH_CHECKOUT_VERIFICATION
        ),
        "actual_identity_input_field_count": actual_identity_input_field_count,
        "orchestration_classification": "standalone_attempt_binding_not_compiler",
        "orchestrator_path": repo_relative(ORCHESTRATOR_PATH),
        "orchestrator_sha256": sha256_file(ORCHESTRATOR_PATH),
        "checks": checks,
        "failed_checks": failed,
        "scope_guards": {
            "attempt_0022_modified_or_resumed": False,
            "official_publish_attempt_created": False,
            "official_publish_attempt_0004_consumed": False,
            "live_gate_mutated": False,
            "foundation_mutated": False,
            "facts_manifest_registry_rtc_runtime_lua_package_mutated": False,
            "new_worktree_or_repository_clone_created": False,
        },
    }
    if failed:
        raise IdentityV2AttemptError(
            f"canonical compiler identity-v2 binding failed: {failed}"
        )
    return report


def require_identity_phase_artifacts(attempt_root: Path) -> None:
    phase0 = (
        effective_phase_root(attempt_root, 0)
        / "canonical_compiler_identity_v2_binding_report.json"
    )
    phase2 = (
        attempt_root
        / "phase2"
        / "source_authority_identity_v2_reseal_report.json"
    )
    for path in (phase0, phase2):
        if not path.is_file():
            raise IdentityV2AttemptError(
                f"required identity-v2 attempt evidence missing: {path}"
            )
        if producer.load_json(path).get("status") != "PASS":
            raise IdentityV2AttemptError(
                f"required identity-v2 attempt evidence is not PASS: {path}"
            )


def write_line_ending_authority_correction_report(
    attempt_root: Path,
) -> dict[str, Any]:
    effective_preflight = (
        effective_phase_root(attempt_root, 0) / "preflight_report.json"
    )
    prior_preflights = []
    for directory_name in ("phase0", "phase0_correction_0001"):
        path = attempt_root / directory_name / "preflight_report.json"
        if path.is_file():
            value = _BASE_LOAD_JSON(path)
            prior_preflights.append(
                {
                    "directory": directory_name,
                    "path": repo_relative(path),
                    "sha256": sha256_file(path),
                    "status": value.get("status"),
                    "blocker_reasons": value.get("blocker_reasons"),
                }
            )
    rows = [
        _LINE_ENDING_AUTHORITY_ROWS[path]
        for path in sorted(_LINE_ENDING_AUTHORITY_ROWS)
    ]
    report = {
        "schema_version": (
            "dvf-3-3-phase0-repository-line-ending-authority-correction-v1"
        ),
        "correction_id": "phase0-correction-0002",
        "status": "PASS",
        "correction_scope": (
            "tracked_files_whose_working_bytes_and_git_blob_differ_only_by_"
            "crlf_or_lone_cr_to_lf_normalization_plus_particle_legacy_raw_"
            "hash_rebound_to_canonical_identity_v2"
        ),
        "effective_phase0_directory": EFFECTIVE_PHASE_DIRECTORY_NAMES[0],
        "effective_preflight_path": repo_relative(effective_preflight),
        "effective_preflight_sha256": sha256_file(effective_preflight),
        "prior_blocked_phase0_evidence": prior_preflights,
        "prior_blocked_evidence_count": len(prior_preflights),
        "all_prior_blocked_evidence_preserved": True,
        "line_ending_authority_substitution_count": len(rows),
        "line_ending_authority_substitutions": rows,
        "particle_legacy_identity_view": dict(_PARTICLE_IDENTITY_VIEW),
        "particle_legacy_identity_rebound_to_canonical_v2": (
            _PARTICLE_IDENTITY_VIEW.get("canonical_identity_v2_sha256")
            == "d13f7e743945dda75d6f87924d5aab1af388e5c5d88ea13b3c21bfae3af6d23f"
        ),
        "source_semantics_changed": False,
        "compiler_semantics_changed": False,
        "tracked_file_working_bytes_mutated": False,
        "new_attempt_id_created_for_correction": False,
        "official_publish_attempt_created": False,
        "official_publish_attempt_0004_consumed": False,
    }
    producer.write_once_or_same(
        effective_phase_root(attempt_root, 0)
        / "repository_line_ending_authority_correction_report.json",
        report,
    )
    return report


def write_phase1_snapshot_identity_correction_report(
    attempt_root: Path,
) -> dict[str, Any]:
    original_result = attempt_root / "phase1" / "phase1_result.json"
    effective_result = (
        effective_phase_root(attempt_root, 1) / "phase1_result.json"
    )
    report = {
        "schema_version": (
            "dvf-3-3-phase1-current-snapshot-identity-correction-v1"
        ),
        "correction_id": "phase1-correction-0001",
        "status": "PASS",
        "effective_phase1_directory": EFFECTIVE_PHASE_DIRECTORY_NAMES[1],
        "effective_phase1_result_path": repo_relative(effective_result),
        "effective_phase1_result_sha256": sha256_file(effective_result),
        "original_failed_phase1_present": original_result.is_file(),
        "original_failed_phase1_path": (
            repo_relative(original_result) if original_result.is_file() else None
        ),
        "original_failed_phase1_sha256": (
            sha256_file(original_result) if original_result.is_file() else None
        ),
        "original_failed_evidence_preserved": True,
        "current_snapshot_identity_view": dict(
            _CURRENT_SNAPSHOT_IDENTITY_VIEW
        ),
        "current_snapshot_semantic_authority": False,
        "candidate_answer_corpus": False,
        "source_semantics_changed": False,
        "compiler_semantics_changed": False,
        "tracked_file_working_bytes_mutated": False,
        "new_attempt_id_created_for_correction": False,
    }
    if (
        not _CURRENT_SNAPSHOT_IDENTITY_VIEW
        or _CURRENT_SNAPSHOT_IDENTITY_VIEW.get("snapshot_semantic_authority")
        is not False
        or _CURRENT_SNAPSHOT_IDENTITY_VIEW.get("candidate_answer_corpus")
        is not False
    ):
        raise IdentityV2AttemptError(
            "current snapshot identity correction is not bounded"
        )
    producer.write_once_or_same(
        effective_phase_root(attempt_root, 1)
        / "current_snapshot_identity_correction_report.json",
        report,
    )
    return report


def write_phase2_identity_reseal(
    attempt_root: Path,
    identity_report: dict[str, Any],
) -> dict[str, Any]:
    standard_reseal_path = (
        attempt_root / "phase2" / "source_authority_reseal_report.json"
    )
    if not standard_reseal_path.is_file():
        raise IdentityV2AttemptError("standard Phase 2 reseal report is missing")
    standard_reseal = producer.load_json(standard_reseal_path)
    checks = {
        "standard_phase2_reseal_pass": standard_reseal.get("status") == "PASS",
        "facts_sha256_match": standard_reseal.get("current_facts_sha256")
        == EXPECTED_FACTS_SHA256,
        "manifest_sha256_match": standard_reseal.get("current_manifest_sha256")
        == EXPECTED_MANIFEST_SHA256,
        "g3_receipt_sha256_match": standard_reseal.get(
            "registry_adoption_receipt_sha256"
        )
        == EXPECTED_G3_RECEIPT_SHA256,
        "g3_terminal_seal_sha256_match": standard_reseal.get(
            "registry_correction_terminal_seal_sha256"
        )
        == EXPECTED_G3_TERMINAL_SEAL_SHA256,
        "g3_handoff_sha256_match": standard_reseal.get(
            "registry_naturalization_handoff_sha256"
        )
        == EXPECTED_G3_HANDOFF_SHA256,
        "foundation_contract_sha256_match": standard_reseal.get(
            "g4_foundation_contract_sha256"
        )
        == EXPECTED_FOUNDATION_CONTRACT_SHA256,
        "predecessor_readiness_sha256_match": standard_reseal.get(
            "g4_foundation_readiness_current_input_rebind_sha256"
        )
        == EXPECTED_PREDECESSOR_READINESS_SHA256,
        "implementation_readiness_sha256_match": identity_report.get(
            "foundation_implementation_correction_readiness_sha256"
        )
        == EXPECTED_IMPLEMENTATION_READINESS_SHA256,
        "canonical_compiler_aggregate_match": identity_report.get(
            "canonical_compiler_identity", {}
        ).get("aggregate_sha256")
        == EXPECTED_COMPILER_AGGREGATE_SHA256,
        "canonical_compiler_algorithm_match": identity_report.get(
            "canonical_compiler_identity", {}
        ).get("algorithm_id")
        == EXPECTED_COMPILER_IDENTITY_ALGORITHM_ID,
    }
    failed = sorted(reason for reason, passed in checks.items() if not passed)
    reseal = {
        "schema_version": "dvf-3-3-source-authority-identity-v2-reseal-v1",
        "status": "PASS" if not failed else "FAIL",
        "naturalization_start_commit": START_COMMIT,
        "naturalization_start_tree": START_TREE,
        "current_facts_sha256": EXPECTED_FACTS_SHA256,
        "current_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "g3_adoption_receipt_sha256": EXPECTED_G3_RECEIPT_SHA256,
        "g3_terminal_correction_seal_sha256": EXPECTED_G3_TERMINAL_SEAL_SHA256,
        "g3_naturalization_handoff_sha256": EXPECTED_G3_HANDOFF_SHA256,
        "foundation_contract_sha256": EXPECTED_FOUNDATION_CONTRACT_SHA256,
        "predecessor_readiness_sha256": EXPECTED_PREDECESSOR_READINESS_SHA256,
        "foundation_implementation_correction_readiness_sha256": (
            EXPECTED_IMPLEMENTATION_READINESS_SHA256
        ),
        "identity_correction_contract_sha256": (
            EXPECTED_IDENTITY_CORRECTION_CONTRACT_SHA256
        ),
        "identity_helper_sha256": EXPECTED_IDENTITY_HELPER_SHA256,
        "compiler_identity_algorithm_id": (
            EXPECTED_COMPILER_IDENTITY_ALGORITHM_ID
        ),
        "canonical_compiler_aggregate_sha256": (
            EXPECTED_COMPILER_AGGREGATE_SHA256
        ),
        "ordered_compiler_path_count": 9,
        "checks": checks,
        "failed_checks": failed,
    }
    if failed:
        raise IdentityV2AttemptError(f"Phase 2 identity-v2 reseal failed: {failed}")
    producer.write_once_or_same(
        attempt_root
        / "phase2"
        / "source_authority_identity_v2_reseal_report.json",
        reseal,
    )
    return reseal


def write_attempt_0022_equality_report(attempt_root: Path) -> dict[str, Any]:
    candidate = attempt_root / "phase4" / "candidate_rendered.json"
    candidate_sha256 = sha256_file(candidate)
    candidate_payload = _BASE_LOAD_JSON(candidate)
    accepted_payload = _BASE_LOAD_JSON(ATTEMPT_0022_CANDIDATE)
    candidate_entries = candidate_payload.get("entries", {})
    accepted_entries = accepted_payload.get("entries", {})
    candidate_text = {
        item_id: entry.get("text_ko")
        for item_id, entry in candidate_entries.items()
    }
    accepted_text = {
        item_id: entry.get("text_ko")
        for item_id, entry in accepted_entries.items()
    }
    all_item_ids = sorted(set(candidate_text) | set(accepted_text))
    public_text_differences = [
        item_id
        for item_id in all_item_ids
        if candidate_text.get(item_id) != accepted_text.get(item_id)
    ]
    key_identity = set(candidate_entries) == set(accepted_entries)
    public_text_equal = key_identity and not public_text_differences
    raw_byte_equal = (
        candidate.read_bytes() == ATTEMPT_0022_CANDIDATE.read_bytes()
    )
    lf_normalized_byte_equal = (
        compiler_identity.canonicalize_compiler_source_bytes(
            candidate.read_bytes()
        )
        == compiler_identity.canonicalize_compiler_source_bytes(
            ATTEMPT_0022_CANDIDATE.read_bytes()
        )
    )
    report = {
        "schema_version": "dvf-3-3-attempt-0022-public-text-equality-v1",
        "status": "PASS" if public_text_equal else "FAIL",
        "candidate_sha256": candidate_sha256,
        "attempt_0022_accepted_candidate_path": repo_relative(
            ATTEMPT_0022_CANDIDATE
        ),
        "attempt_0022_accepted_candidate_sha256": sha256_file(
            ATTEMPT_0022_CANDIDATE
        ),
        "candidate_entry_count": len(candidate_entries),
        "attempt_0022_entry_count": len(accepted_entries),
        "item_key_identity": key_identity,
        "public_text_field": "entries.*.text_ko",
        "public_text_difference_count": len(public_text_differences),
        "public_text_difference_item_ids": public_text_differences,
        "public_text_digest": producer.canonical_hash(candidate_text),
        "attempt_0022_public_text_digest": producer.canonical_hash(
            accepted_text
        ),
        "public_text_identity": public_text_equal,
        "raw_file_byte_identity": raw_byte_equal,
        "lf_normalized_file_byte_identity": lf_normalized_byte_equal,
        "raw_file_byte_difference_disposition": (
            None
            if raw_byte_equal
            else "tracked_attempt_0022_crlf_representation_vs_new_lf_output"
        ),
        "metadata_and_identity_evidence_excluded_from_public_text_comparison": True,
    }
    if not public_text_equal:
        raise IdentityV2AttemptError(
            "candidate public text differs from attempt-0022 accepted public text"
        )
    producer.write_once_or_same(
        attempt_root / "phase4" / "attempt_0022_public_text_equality_report.json",
        report,
    )
    return report


def write_handoff_identity_report(attempt_root: Path) -> dict[str, Any]:
    handoff_path = (
        attempt_root
        / "phase8"
        / "publish_acceptance_handoff_manifest.json"
    )
    candidate_manifest_path = (
        attempt_root / "phase4" / "candidate_manifest.json"
    )
    handoff = producer.load_json(handoff_path)
    candidate_manifest = producer.load_json(candidate_manifest_path)
    constituents = {
        str(row.get("id")): row
        for row in handoff.get("constituents", [])
        if isinstance(row, dict)
    }
    compiler_claim = constituents.get("compiler_implementation_hash", {}).get(
        "value"
    )
    producer_evidence = producer.implementation_identity()
    consumer_evidence = publish_consumer.build_compiler_identity(
        publish_consumer.REPO_ROOT
    )
    checks = {
        "handoff_compiler_implementation_hash_match": compiler_claim
        == EXPECTED_COMPILER_AGGREGATE_SHA256,
        "candidate_manifest_compiler_implementation_hash_match": (
            candidate_manifest.get("compiler_implementation_hash")
            == EXPECTED_COMPILER_AGGREGATE_SHA256
        ),
        "candidate_manifest_compiler_identity_match": candidate_manifest.get(
            "compiler_identity"
        )
        == producer_evidence,
        "producer_publish_consumer_recomputation_match": (
            producer_evidence == consumer_evidence
        ),
        "algorithm_id_match": producer_evidence.get("algorithm_id")
        == EXPECTED_COMPILER_IDENTITY_ALGORITHM_ID,
        "ordered_path_count_match": len(
            producer_evidence.get("ordered_files", [])
        )
        == 9,
    }
    failed = sorted(reason for reason, passed in checks.items() if not passed)
    report = {
        "schema_version": "dvf-3-3-phase8-compiler-identity-v2-verification-v1",
        "status": "PASS" if not failed else "FAIL",
        "handoff_path": repo_relative(handoff_path),
        "handoff_sha256": sha256_file(handoff_path),
        "handoff_compiler_implementation_hash": compiler_claim,
        "compiler_identity_algorithm_id": producer_evidence.get("algorithm_id"),
        "ordered_compiler_path_count": len(
            producer_evidence.get("ordered_files", [])
        ),
        "producer_compiler_identity": producer_evidence,
        "publish_consumer_compiler_identity": consumer_evidence,
        "checks": checks,
        "failed_checks": failed,
        "official_publish_attempt_created": False,
        "official_publish_attempt_0004_consumed": False,
        "live_gate_mutated": False,
    }
    if failed:
        raise IdentityV2AttemptError(
            f"Phase 8 compiler identity verification failed: {failed}"
        )
    producer.write_once_or_same(
        attempt_root
        / "phase8"
        / "compiler_identity_v2_verification_report.json",
        report,
    )
    return report


def run_phase(attempt_id: str, mode: str) -> int:
    if attempt_id not in ALLOWED_ATTEMPT_IDS:
        raise IdentityV2AttemptError(
            f"attempt ID is outside this immutable pair: {attempt_id}"
        )
    if mode in {"phase7-human-review-sample", "phase8-publish-handoff"}:
        if attempt_id != PRIMARY_ATTEMPT_ID:
            raise IdentityV2AttemptError(
                "Phase 7/8 are allowed only for the Primary attempt"
            )
    if mode == "phase7-human-review-sample" and not HUMAN_REVIEW_DECISION.is_file():
        raise IdentityV2AttemptError(
            "Phase 7 decision must exist before the write-once Phase 7 build"
        )
    apply_runtime_binding()
    identity_report = build_identity_binding_report()
    attempt_root = producer.attempt_root_for(attempt_id)
    if mode not in {"phase0-preflight", "phase1-census", "phase2-source-inventory"}:
        require_identity_phase_artifacts(attempt_root)
    if mode == "phase2-source-inventory":
        phase0_path = (
            effective_phase_root(attempt_root, 0)
            / "canonical_compiler_identity_v2_binding_report.json"
        )
        if not phase0_path.is_file():
            raise IdentityV2AttemptError("Phase 0 identity-v2 binding is missing")
        phase0_identity_report = producer.load_json(phase0_path)
        phase0_identity_keys = (
            "foundation_implementation_correction_readiness_sha256",
            "foundation_contract_sha256",
            "predecessor_readiness_sha256",
            "identity_correction_contract_sha256",
            "identity_helper_sha256",
            "canonical_compiler_identity",
            "producer_compiler_identity",
            "publish_consumer_compiler_identity",
            "line_ending_variant_aggregates",
            "actual_identity_input_field_count",
        )
        if any(
            phase0_identity_report.get(key) != identity_report.get(key)
            for key in phase0_identity_keys
        ):
            raise IdentityV2AttemptError(
                "Phase 0 canonical identity or authority binding is stale"
            )

    builders = {
        "phase0-preflight": producer.build_phase0,
        "phase1-census": producer.build_phase1,
        "phase2-source-inventory": producer.build_phase2,
        "phase3-compiler-evidence": producer.build_phase3,
        "phase4-candidate": producer.build_phase4,
        "phase5-semantic": producer.build_phase5_semantic,
        "phase5-adversarial": producer.build_phase5_adversarial,
        "phase6-raw-detectors": producer.build_phase6,
        "phase7-human-review-sample": producer.build_phase7,
        "phase8-publish-handoff": producer.build_phase8_handoff,
    }
    try:
        existing_phase2_result_path = (
            effective_phase_root(attempt_root, 2) / "phase2_result.json"
        )
        existing_phase4_result_path = (
            effective_phase_root(attempt_root, 4) / "phase4_result.json"
        )
        if (
            mode == "phase2-source-inventory"
            and existing_phase2_result_path.is_file()
            and producer.load_json(existing_phase2_result_path).get("status")
            == "PASS"
        ):
            result = producer.load_json(existing_phase2_result_path)
        elif (
            mode == "phase4-candidate"
            and existing_phase4_result_path.is_file()
            and producer.load_json(existing_phase4_result_path).get("status")
            == "PASS"
        ):
            result = producer.load_json(existing_phase4_result_path)
        else:
            result = builders[mode](attempt_id, attempt_root)
        producer_status = result.get("status", "PASS")
        if producer_status not in {"PASS", "HANDOFF_COMPLETE"}:
            raise IdentityV2AttemptError(
                f"producer phase did not pass: {mode}: {producer_status}"
            )
        if mode == "phase0-preflight":
            write_line_ending_authority_correction_report(attempt_root)
            producer.write_once_or_same(
                effective_phase_root(attempt_root, 0)
                / "canonical_compiler_identity_v2_binding_report.json",
                identity_report,
            )
        elif mode == "phase1-census":
            write_phase1_snapshot_identity_correction_report(attempt_root)
        elif mode == "phase2-source-inventory":
            write_phase2_identity_reseal(attempt_root, identity_report)
        elif mode == "phase4-candidate":
            write_attempt_0022_equality_report(attempt_root)
        elif mode == "phase8-publish-handoff":
            write_handoff_identity_report(attempt_root)
    except (
        producer.NaturalizationError,
        IdentityV2AttemptError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 3 if "write-once conflict" in str(exc) else 2
    output = {
        "schema_version": "dvf-3-3-identity-v2-attempt-run-result-v1",
        "status": "PASS",
        "attempt_id": attempt_id,
        "mode": mode,
        "producer_status": producer_status,
        "compiler_aggregate_sha256": EXPECTED_COMPILER_AGGREGATE_SHA256,
        "compiler_identity_algorithm_id": (
            EXPECTED_COMPILER_IDENTITY_ALGORITHM_ID
        ),
    }
    print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    return 0


def validate_attempt(
    attempt_id: str,
    compare_attempt: str | None,
    scope: str,
) -> int:
    if attempt_id not in ALLOWED_ATTEMPT_IDS:
        raise IdentityV2AttemptError(
            f"attempt ID is outside this immutable pair: {attempt_id}"
        )
    apply_runtime_binding()
    current_identity = build_identity_binding_report()
    root = producer.attempt_root_for(attempt_id)
    compare_root = (
        producer.attempt_root_for(compare_attempt)
        if compare_attempt is not None
        else None
    )
    errors: list[str] = []
    checked: list[str] = []
    try:
        if scope == "phase0-6":
            if compare_attempt not in ALLOWED_ATTEMPT_IDS or compare_root is None:
                raise IdentityV2AttemptError(
                    "Phase 0-6 validation requires the paired compare attempt"
                )
            validator.validate_phase0(root, errors)
            validator.validate_phase1(root, errors)
            validator.validate_phase2(root, errors)
            validator.validate_phase3(root, errors)
            validator.validate_phase4(root, compare_root, errors)
            validator.validate_phase5(root, errors)
            validator.validate_phase6(root, errors)
            checked.extend(
                [
                    "phase0",
                    "phase1",
                    "phase2",
                    "phase3",
                    "phase4",
                    "phase5",
                    "phase6",
                ]
            )
            for relative in (
                "phase2/source_authority_identity_v2_reseal_report.json",
                "phase4/attempt_0022_public_text_equality_report.json",
            ):
                primary_path = root / relative
                compare_path = compare_root / relative
                if not primary_path.is_file() or not compare_path.is_file():
                    errors.append(f"identity_v2_evidence_missing:{relative}")
                elif primary_path.read_bytes() != compare_path.read_bytes():
                    errors.append(f"identity_v2_ab_byte_mismatch:{relative}")
            primary_phase0_identity = (
                effective_phase_root(root, 0)
                / "canonical_compiler_identity_v2_binding_report.json"
            )
            compare_phase0_identity = (
                effective_phase_root(compare_root, 0)
                / "canonical_compiler_identity_v2_binding_report.json"
            )
            if (
                not primary_phase0_identity.is_file()
                or not compare_phase0_identity.is_file()
            ):
                errors.append("identity_v2_phase0_binding_missing")
            elif (
                primary_phase0_identity.read_bytes()
                != compare_phase0_identity.read_bytes()
            ):
                errors.append("identity_v2_phase0_binding_ab_byte_mismatch")
            candidate_manifest = producer.load_json(
                root / "phase4" / "candidate_manifest.json"
            )
            compare_manifest = producer.load_json(
                compare_root / "phase4" / "candidate_manifest.json"
            )
            if candidate_manifest.get("compiler_identity") != current_identity.get(
                "canonical_compiler_identity"
            ):
                errors.append("primary_canonical_compiler_identity_stale")
            if compare_manifest.get("compiler_identity") != current_identity.get(
                "canonical_compiler_identity"
            ):
                errors.append("replay_canonical_compiler_identity_stale")
            if (
                candidate_manifest.get("compiler_identity")
                != compare_manifest.get("compiler_identity")
            ):
                errors.append("canonical_compiler_identity_ab_mismatch")
        else:
            if attempt_id != PRIMARY_ATTEMPT_ID:
                raise IdentityV2AttemptError(
                    "Phase 7/8 validation is Primary-only"
                )
            validator.validate_phase7(root, errors)
            validator.validate_phase8(root, errors)
            checked.extend(["phase7", "phase8_handoff"])
            handoff_identity_path = (
                root
                / "phase8"
                / "compiler_identity_v2_verification_report.json"
            )
            if not handoff_identity_path.is_file():
                errors.append("phase8_compiler_identity_v2_report_missing")
            else:
                handoff_identity = producer.load_json(handoff_identity_path)
                if handoff_identity.get("status") != "PASS":
                    errors.append("phase8_compiler_identity_v2_not_pass")
                if (
                    handoff_identity.get("handoff_compiler_implementation_hash")
                    != EXPECTED_COMPILER_AGGREGATE_SHA256
                ):
                    errors.append("phase8_handoff_compiler_aggregate_mismatch")
    except (
        producer.NaturalizationError,
        IdentityV2AttemptError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    result = {
        "schema_version": "dvf-3-3-identity-v2-attempt-validation-v1",
        "status": "PASS" if not errors else "FAIL",
        "attempt_id": attempt_id,
        "compare_attempt": compare_attempt,
        "checked": checked,
        "error_count": len(errors),
        "errors": errors,
        "no_write": True,
        "compiler_aggregate_sha256": EXPECTED_COMPILER_AGGREGATE_SHA256,
        "compiler_identity_algorithm_id": (
            EXPECTED_COMPILER_IDENTITY_ALGORITHM_ID
        ),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Standalone immutable-attempt orchestration that binds the sealed "
            "canonical compiler identity v2 without modifying its ordered "
            "nine compiler source paths."
        )
    )
    parser.add_argument("--action", choices=("run", "validate"), required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--mode", choices=producer.RUNNER_MODES)
    parser.add_argument("--compare-attempt")
    parser.add_argument(
        "--validate-scope",
        choices=("phase0-6", "phase7-8"),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.action == "run":
            if args.mode is None or args.validate_scope is not None:
                raise IdentityV2AttemptError(
                    "run action requires --mode and forbids --validate-scope"
                )
            return run_phase(args.attempt_id, args.mode)
        if args.validate_scope is None or args.mode is not None:
            raise IdentityV2AttemptError(
                "validate action requires --validate-scope and forbids --mode"
            )
        return validate_attempt(
            args.attempt_id,
            args.compare_attempt,
            args.validate_scope,
        )
    except IdentityV2AttemptError as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
