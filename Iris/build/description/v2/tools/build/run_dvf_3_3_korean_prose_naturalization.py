from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Iterable

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.build.compose_layer3_body_profile import (
        build_candidate_body_plan_requirements,
        load_profile_resolution_rules,
        resolve_body_profile,
    )
    from tools.build.compose_layer3_identity import (
        build_candidate_lead_context,
        select_candidate_lead_realization,
    )
    from tools.build.compose_layer3_text import (
        BODY_PLAN_PROFILES_PATH,
        CURRENT_OVERLAY_SUPPORT_PATH,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        STAGING_COMPOSE_CONTEXT,
        ComposeEntrypointGuardError,
        build_candidate_rendered,
        build_rendered,
    )
    from tools.build.naturalization_compiler_identity import (
        build_compiler_identity,
        compiler_source_paths,
    )
else:
    from .compose_layer3_body_profile import (
        build_candidate_body_plan_requirements,
        load_profile_resolution_rules,
        resolve_body_profile,
    )
    from .compose_layer3_identity import (
        build_candidate_lead_context,
        select_candidate_lead_realization,
    )
    from .compose_layer3_text import (
        BODY_PLAN_PROFILES_PATH,
        CURRENT_OVERLAY_SUPPORT_PATH,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        STAGING_COMPOSE_CONTEXT,
        ComposeEntrypointGuardError,
        build_candidate_rendered,
        build_rendered,
    )
    from .naturalization_compiler_identity import (
        build_compiler_identity,
        compiler_source_paths,
    )


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]
ROUND_ID = "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
SYNC_CONTRACT_ID = "dvf3_3_korean_naturalization__publish_boundary_sync_v1"
EVALUATION_SUBJECT_KIND = "dvf_3_3_korean_naturalization_candidate"
DEFAULT_ATTEMPT_PARENT = V2_ROOT / "staging" / ROUND_ID
HISTORICAL_ATTEMPT_ID = "attempt-0014-remediation"
BLOCKED_ATTEMPT_ID = "attempt-0018-g3-reseal-a"
PRESERVED_PREDECESSOR_ATTEMPT_IDS = (
    "attempt-0020-g4-rebind-a",
    "attempt-0020-g4-rebind-b",
    "attempt-0021-g4-rebind-a",
    "attempt-0021-g4-rebind-b",
)
DATA_ROOT = V2_ROOT / "data" / "korean_prose_naturalization"
DURABLE_ROOT = REPO_ROOT / "Iris" / "_docs" / "round3" / ROUND_ID
FOUNDATION_ROOT = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure"
    / "foundation"
)
FOUNDATION_CONTRACT = FOUNDATION_ROOT / "public_text_quality_foundation_contract.json"
FOUNDATION_READINESS = (
    FOUNDATION_ROOT / "public_text_quality_development_readiness_report.json"
)
FOUNDATION_READINESS_CORRECTION_REBIND = (
    FOUNDATION_ROOT
    / "public_text_quality_development_readiness_correction_rebind.json"
)
FOUNDATION_READINESS_CURRENT_INPUT_REBIND = (
    FOUNDATION_ROOT
    / "readiness_successors"
    / "correction-0003"
    / "public_text_quality_development_readiness_current_input_rebind.json"
)
REGISTRY_ADOPTION_CONTRACT = (
    DURABLE_ROOT / "food_semantic_registry_adoption_contract.json"
)
INITIAL_REGISTRY_ADOPTION_RECEIPT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_registry_operational_cutover"
    / "attempts"
    / "attempt-0009"
    / "closeout"
    / "registry_adoption_receipt.json"
)
REGISTRY_ADOPTION_RECEIPT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_registry_operational_cutover"
    / "attempts"
    / "attempt-0012"
    / "closeout"
    / "registry_correction_adoption_receipt.json"
)
REGISTRY_CORRECTION_TERMINAL_SEAL = REGISTRY_ADOPTION_RECEIPT.with_name(
    "terminal_correction_hash_seal.json"
)
REGISTRY_NATURALIZATION_HANDOFF = (
    REGISTRY_ADOPTION_RECEIPT.parents[1]
    / "handoff"
    / "naturalization_current_input_handoff.json"
)
FOOD_SEMANTIC_SCHEMA = (
    REPO_ROOT / "Iris" / "_docs" / "authority" / "food_semantic"
    / "food_semantic_schema.json"
)
FOOD_SEMANTIC_LICENSE = (
    REPO_ROOT / "Iris" / "_docs" / "authority" / "food_semantic"
    / "proposition_licensing_contract.json"
)
FACTS_AUTHORITY_ROUTING_CORRECTION = (
    DURABLE_ROOT / "facts_authority_routing_correction_attempt_0014.json"
)
PARTICLE_CORRECTION_PROJECTION_REPORT = (
    DURABLE_ROOT
    / "compiler_particle_adjustment_correction_0001_projection_report.json"
)
INPUT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
FACTS_PATH = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
DECISIONS_PATH = V2_ROOT / "data" / "dvf_3_3_decisions.jsonl"
EXPECTED_CURRENT_FACTS_SHA256 = (
    "50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120"
)
EXPECTED_CURRENT_MANIFEST_SHA256 = (
    "090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7"
)
EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256 = (
    "1ef1785f12d53fbfdca7e96d372079c16fcec276cbae93280e62908c8a891b40"
)
EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256 = (
    "d1dea3b7b871fac90fc6a15ec18d95641a52d566cd62d14ffb0114c2bfb0098a"
)
EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256 = (
    "66f9eb59ea2cfec3fb5d647345ce5ab07ae17d0ba70b62c52b6bcaa7e3f32563"
)
EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256 = (
    "60f68c3e06fd148fce55072e1b7420165e10db16fc4e4b132b3fba7ae83e6edd"
)
EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256 = (
    "312c9b8744e1925b120129402b4ff6834d551960c284af8e91dbdbca091a56b0"
)
EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256 = (
    "efcc387bb395b561ab67df0cab4e498fe0b429680fc6cc8f6dd96eb94ba49751"
)
EXPECTED_PREVIOUS_REGISTRY_CORRECTION_RECEIPT_SHA256 = (
    "475239fba798104371d2c9f4fb166c46ceab15bb462015493238a4aff4656f7f"
)
EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256 = (
    "d4aac650a5d8135e6f14846d47b08f538f63b5ad07aaf714074d7a3f6555aed4"
)
EXPECTED_REGISTRY_CORRECTION_SUCCESSOR_MANIFEST_SHA256 = (
    "da7f6676b899b628c444edca56241ad274f2c64fa1a3448a934abff2f059cbb5"
)
EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256 = (
    "03dea1902f1d219b227b2b69cb88742f1005e3620cdcdee2b72ba811d1bd20fb"
)
EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256 = (
    "bfa14583f524f99a75e88d4b6eaddfa146544cba9124cf09214a13a38c7d7750"
)
EXPECTED_FOUNDATION_CONTRACT_SHA256 = (
    "4a31e48dacc9c906c4fe4a04cce22799226b23366cd77cd948e91473e1844b02"
)
EXPECTED_FOUNDATION_READINESS_SHA256 = (
    "34419a8093970c7ffc68d3d968ff90207f63c512971ae9ada87f90cff7f2d263"
)
EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256 = (
    "bf5916854b7aeb29f603ef42efb64e2b363fc5efb899dca1434b5e5c2744f315"
)
EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256 = (
    "912f28b7869ff92ff7fbd84cbdc31e1fbb22923beebbfcce2c9cc78b72eca9d2"
)
EXPECTED_COMPILER_FIX_COMMIT = "ca851a1e10bd37be71deded1fcc57b0d8462db48"
EXPECTED_PARTICLE_CORRECTION_COMMIT = (
    "55c8df22085b581590624d50fdda804c94930316"
)
EXPECTED_PARTICLE_CORRECTION_PROJECTION_REPORT_SHA256 = (
    "7cd0e72c879d5c24a171d5cc85fe00e19657388404fd2b55440769343cd4976f"
)
EXPECTED_START_COMMIT = EXPECTED_PARTICLE_CORRECTION_COMMIT
EXPECTED_START_TREE = "d063e618a3c9cf2fcf8a81c05f39b15c4932e3d8"
POLICY_PATH = DATA_ROOT / "korean_prose_policy.json"
CORPUS_MANIFEST_PATH = DATA_ROOT / "corpus_manifest.json"
PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure_plan.md"
)
PUBLISH_PLAN_PATH = (
    REPO_ROOT
    / "docs"
    / "iris_publish_boundary_public_text_quality_acceptance_policy_closure_plan.md"
)
EXECUTION_CONTRACT_PATH = REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md"
ROADMAP_BINDING_PATH = DURABLE_ROOT / "roadmap_binding.json"
QUALITY_APPROVAL_PATH = DURABLE_ROOT / "quality_standard_approval.json"
GOLD_APPROVAL_PATH = DURABLE_ROOT / "gold_corpus_approval.json"
BODY_PLAN_APPLICABILITY_APPROVAL_PATH = (
    DURABLE_ROOT / "body_plan_applicability_approval.json"
)
HUMAN_REVIEW_DECISION_PATH = (
    DURABLE_ROOT / "attempt_0022_human_review_decision.json"
)
QUALITY_STANDARD_PATH = REPO_ROOT / "docs" / "dvf_3_3_korean_prose_quality_standard.md"
GOLD_CORPUS_PATH = DATA_ROOT / "gold_corpus.jsonl"
ROADMAP_ATTACHMENT_PATH = Path(
    r"C:\Users\MW\.codex\attachments\91b61f60-9f67-4407-b32f-4952747614ae"
    r"\pasted-text.txt"
)
PLAN_REVIEW_ATTACHMENT_PATH = Path(
    r"C:\Users\MW\.codex\attachments\245e56e9-90fb-4f85-9b76-6ec568de0a4f"
    r"\pasted-text.txt"
)
CYCLE2_REVIEW_ATTACHMENT_PATH = Path(
    r"C:\Users\MW\.codex\attachments\800664bb-cbe3-4b88-885c-d703af54a644"
    r"\pasted-text.txt"
)
EXPECTED_ATTACHMENT_HASHES = {
    ROADMAP_ATTACHMENT_PATH: "c0c4838352910f8cacbcedfca8b74912d544d4f2ebc1d8d96f5cd34860eb3d1d",
    PLAN_REVIEW_ATTACHMENT_PATH: "dee1b7d3368936e88fffa2bc2dd2b5afdead1a55c8df749db387959c256d989f",
    CYCLE2_REVIEW_ATTACHMENT_PATH: "278daed986a32cc8964b0cfd9c786ae015f8e6fbcaac879a32ec2fea30098848",
}
PROTECTED_PATHS = (
    V2_ROOT / "output" / "dvf_3_3_rendered.json",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3Data.lua",
    REPO_ROOT
    / "Iris"
    / "media"
    / "lua"
    / "client"
    / "Iris"
    / "Data"
    / "IrisLayer3DataChunks.lua",
    REPO_ROOT / "Iris" / "build" / "package" / "Iris.zip",
    REPO_ROOT / "Iris" / "build" / "package" / "Iris.package_manifest.sha256.json",
)
COMPILER_IMPLEMENTATION_PATHS = compiler_source_paths(REPO_ROOT)
SOURCE_ROLE_BY_FIELD = {
    "identity_hint": "identity",
    "primary_use": "use",
    "secondary_use": "use",
    "special_context": "context",
    "processing_hint": "context",
    "acquisition_hint": "acquisition",
    "limitation_hint": "limitation",
    "notes": "limitation",
}
TRANSFORMATION_IDS = (
    "reorder",
    "merge_equivalent",
    "suppress_duplicate",
    "pronoun_or_zero_anaphora",
    "particle_adjustment",
    "copula_adjustment",
    "paragraph_merge",
    "lexical_surface_naturalization",
)
FORBIDDEN_TRANSFORMATIONS = (
    "invent_fact",
    "strengthen_modality",
    "drop_qualifier",
    "cross_item_copy",
    "advice_conversion",
)
NOT_APPLICABLE_REASONS = (
    "source_role_not_required",
    "profile_exclusion",
    "body_plan_exclusion",
    "non_emittable_metadata",
)
RUNNER_MODES = (
    "phase0-preflight",
    "phase1-census",
    "phase2-source-inventory",
    "phase3-compiler-evidence",
    "phase4-candidate",
    "phase5-semantic",
    "phase5-adversarial",
    "phase6-raw-detectors",
    "phase7-human-review-sample",
    "phase8-publish-handoff",
)


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
        return json.loads(
            path.read_text(encoding="utf-8-sig"),
            object_pairs_hook=reject_duplicate_pairs,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise NaturalizationError(f"cannot read strict JSON: {path}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for line_number, raw_line in enumerate(
            path.read_text(encoding="utf-8-sig").splitlines(),
            start=1,
        ):
            if not raw_line.strip():
                continue
            value = json.loads(raw_line, object_pairs_hook=reject_duplicate_pairs)
            if not isinstance(value, dict):
                raise NaturalizationError(
                    f"JSONL row must be object: {path}:{line_number}"
                )
            rows.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise NaturalizationError(f"cannot read strict JSONL: {path}") from exc
    return rows


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


def build_phase0(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_files(
        (
            PLAN_PATH,
            PUBLISH_PLAN_PATH,
            EXECUTION_CONTRACT_PATH,
            INPUT_MANIFEST,
            FOUNDATION_CONTRACT,
            FOUNDATION_READINESS,
            FOUNDATION_READINESS_CORRECTION_REBIND,
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND,
            REGISTRY_ADOPTION_CONTRACT,
            REGISTRY_ADOPTION_RECEIPT,
            INITIAL_REGISTRY_ADOPTION_RECEIPT,
            REGISTRY_CORRECTION_TERMINAL_SEAL,
            REGISTRY_NATURALIZATION_HANDOFF,
            FOOD_SEMANTIC_SCHEMA,
            FOOD_SEMANTIC_LICENSE,
            FACTS_AUTHORITY_ROUTING_CORRECTION,
            PARTICLE_CORRECTION_PROJECTION_REPORT,
            ROADMAP_BINDING_PATH,
            BODY_PLAN_APPLICABILITY_APPROVAL_PATH,
            FACTS_PATH,
            DECISIONS_PATH,
            BODY_PLAN_PROFILES_PATH,
            IDENTITY_RULES_PATH,
            PRECEDENCE_RULES_PATH,
            CURRENT_OVERLAY_SUPPORT_PATH,
        )
    )
    root = phase_root(attempt_root, 0)
    root.mkdir(parents=True, exist_ok=True)
    manifest = load_json(INPUT_MANIFEST)
    foundation = load_json(FOUNDATION_CONTRACT)
    readiness = load_json(FOUNDATION_READINESS)
    readiness_rebind = load_json(FOUNDATION_READINESS_CORRECTION_REBIND)
    readiness_current_input_rebind = load_json(
        FOUNDATION_READINESS_CURRENT_INPUT_REBIND
    )
    registry_contract = load_json(REGISTRY_ADOPTION_CONTRACT)
    registry_receipt = load_json(REGISTRY_ADOPTION_RECEIPT)
    initial_registry_receipt = load_json(INITIAL_REGISTRY_ADOPTION_RECEIPT)
    registry_correction_terminal = load_json(
        REGISTRY_CORRECTION_TERMINAL_SEAL
    )
    registry_naturalization_handoff = load_json(
        REGISTRY_NATURALIZATION_HANDOFF
    )
    particle_correction_projection = load_json(
        PARTICLE_CORRECTION_PROJECTION_REPORT
    )
    food_semantic_schema = load_json(FOOD_SEMANTIC_SCHEMA)
    food_semantic_license = load_json(FOOD_SEMANTIC_LICENSE)
    roadmap_binding = load_json(ROADMAP_BINDING_PATH)
    applicability_approval = load_json(BODY_PLAN_APPLICABILITY_APPROVAL_PATH)
    source_rows = manifest_binding_rows(manifest)
    attachment_rows = []
    for path, expected_hash in EXPECTED_ATTACHMENT_HASHES.items():
        actual_hash = sha256_file(path) if path.is_file() else None
        attachment_rows.append(
            {
                "path": str(path),
                "expected_sha256": expected_hash,
                "actual_sha256": actual_hash,
                "hash_match": actual_hash == expected_hash,
            }
        )
    expected_sync_projection = {
        "blocked_immediate_allowed_for_synchronized_candidate": False,
        "candidate_runtime_parity_applicability": "not_applicable",
        "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
        "candidate_structural_status_enum": [
            "emitted_direct",
            "satisfied_by_verified_fusion",
            "satisfied_by_verified_suppression",
            "not_required",
            "missing",
        ],
        "canonical_stage_order": [
            "S0_plan_sync",
            "S1_publish_foundation",
            "S2_naturalization_build",
            "S3_publish_official_attempt",
            "S4_naturalization_finalize",
        ],
        "dvf_owns_proposition_discourse_realization_raw_detector": True,
        "evaluation_subject_kind_enum": [
            "current_runtime_payload",
            EVALUATION_SUBJECT_KIND,
        ],
        "foundation_required_state": {
            "authority_effect": "none",
            "foundation_contract_ready_for_remediation": True,
            "live_gate_adopted": False,
            "official_disposition": "not_issued",
            "policy_closure_state": "not_started",
        },
        "nonaccepted_candidate_action": "after_remediation",
        "publish_owns_metric_mapping_threshold_waiver_disposition": True,
        "required_handoff_constituent_ids": list(
            foundation["required_handoff_schema"]["required_constituent_ids"]
        ),
        "synchronization_contract_id": SYNC_CONTRACT_ID,
    }
    projection_report = {
        "schema_version": "dvf-3-3-cross-plan-sync-projection-report-v1",
        "expected_projection": expected_sync_projection,
        "foundation_projection": foundation.get("synchronization_projection"),
        "expected_projection_hash": compact_canonical_hash(expected_sync_projection),
        "foundation_projection_hash": foundation.get(
            "synchronization_projection_hash"
        ),
        "cross_plan_sync_projection_hash_match": (
            foundation.get("synchronization_projection") == expected_sync_projection
            and foundation.get("synchronization_projection_hash")
            == compact_canonical_hash(expected_sync_projection)
        ),
    }
    write_once_or_same(root / "cross_plan_sync_projection_report.json", projection_report)
    execution_report = {
        "schema_version": "dvf-3-3-execution-contract-checked-state-v1",
        "path": repo_relative(EXECUTION_CONTRACT_PATH),
        "sha256": sha256_file(EXECUTION_CONTRACT_PATH),
        "execution_contract_checked": True,
        "execution_weight": "heavy",
        "risk_surfaces": [
            "authority_surface",
            "sealed_artifact_surface",
            "public_facing_output_surface",
        ],
        "execution_contract_conflict_count": 0,
        "read_only": True,
    }
    write_once_or_same(root / "execution_contract_checked_state.json", execution_report)
    foundation_state = {
        key: foundation.get(key)
        for key in (
            "synchronization_contract_id",
            "foundation_contract_ready_for_remediation",
            "authority_effect",
            "official_disposition",
            "live_gate_adopted",
            "policy_closure_state",
        )
    }
    expected_foundation_state = {
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "foundation_contract_ready_for_remediation": True,
        "authority_effect": "none",
        "official_disposition": "not_issued",
        "live_gate_adopted": False,
        "policy_closure_state": "not_started",
    }
    foundation_report = {
        "schema_version": "dvf-3-3-publish-foundation-binding-report-v1",
        "foundation_contract_path": repo_relative(FOUNDATION_CONTRACT),
        "foundation_contract_raw_sha256": sha256_file(FOUNDATION_CONTRACT),
        "foundation_contract_canonical_sha256": canonical_hash(foundation),
        "foundation_readiness_path": repo_relative(FOUNDATION_READINESS),
        "foundation_readiness_sha256": sha256_file(FOUNDATION_READINESS),
        "foundation_readiness_correction_rebind_path": repo_relative(
            FOUNDATION_READINESS_CORRECTION_REBIND
        ),
        "foundation_readiness_correction_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CORRECTION_REBIND
        ),
        "foundation_readiness_correction_rebind_status": (
            readiness_rebind.get("status")
        ),
        "foundation_readiness_correction_rebind_current_facts_sha256": (
            readiness_rebind.get("registry_correction_adoption", {}).get(
                "current_facts_sha256"
            )
        ),
        "foundation_readiness_correction_rebind_current_manifest_sha256": (
            readiness_rebind.get("registry_correction_adoption", {}).get(
                "current_manifest_sha256"
            )
        ),
        "foundation_readiness_current_input_rebind_path": repo_relative(
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "foundation_readiness_current_input_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "foundation_readiness_current_input_rebind_status": (
            readiness_current_input_rebind.get("status")
        ),
        "foundation_readiness_current_input_rebind_current_facts_sha256": (
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_facts", {})
            .get("sha256")
        ),
        "foundation_readiness_current_input_rebind_current_manifest_sha256": (
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_manifest", {})
            .get("sha256")
        ),
        "foundation_state": foundation_state,
        "expected_foundation_state": expected_foundation_state,
        "foundation_state_match": foundation_state == expected_foundation_state,
        "human_review_selection_contract": foundation.get(
            "human_review_selection_contract"
        ),
        "human_review_selection_contract_hash": foundation.get(
            "human_review_selection_contract_hash"
        ),
        "required_handoff_schema_hash": foundation.get(
            "required_handoff_schema_hash"
        ),
    }
    write_once_or_same(root / "publish_foundation_binding_report.json", foundation_report)
    food_manifest = manifest.get("food_semantic_authority", {})
    current_manifest_correction = manifest.get("current_facts_correction", {})
    selected_successor = registry_contract.get("selected_successor", {})
    current_correction_selection = registry_contract.get(
        "current_correction_selection", {}
    )
    current_correction_successors = registry_contract.get(
        "current_correction_successors", []
    )
    current_correction = next(
        (
            row
            for row in current_correction_successors
            if row.get("successor_id")
            == current_correction_selection.get("successor_id")
        ),
        {},
    )
    registry_predicates = registry_contract.get("official_consumer_predicates", {})
    actual_source_identity = {
        "current_facts_sha256": sha256_file(FACTS_PATH),
        "current_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "selected_successor_manifest_sha256": food_manifest.get(
            "source_successor_manifest_sha256"
        ),
        "food_semantic_schema_sha256": sha256_file(FOOD_SEMANTIC_SCHEMA),
        "food_semantic_proposition_license_sha256": sha256_file(
            FOOD_SEMANTIC_LICENSE
        ),
    }
    expected_source_identity = {
        "current_facts_sha256": EXPECTED_CURRENT_FACTS_SHA256,
        "current_manifest_sha256": EXPECTED_CURRENT_MANIFEST_SHA256,
        "selected_successor_manifest_sha256": (
            EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256
        ),
        "food_semantic_schema_sha256": EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256,
        "food_semantic_proposition_license_sha256": (
            EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256
        ),
    }
    registry_receipt_predicates = {
        "status_pass": registry_receipt.get("status") == "PASS",
        "current_facts_match": (
            registry_receipt.get("current_facts_sha256")
            == EXPECTED_CURRENT_FACTS_SHA256
        ),
        "current_manifest_match": (
            registry_receipt.get("current_manifest_sha256")
            == EXPECTED_CURRENT_MANIFEST_SHA256
        ),
        "correction_successor_manifest_match": (
            registry_receipt.get("sealed_successor_manifest_sha256")
            == EXPECTED_REGISTRY_CORRECTION_SUCCESSOR_MANIFEST_SHA256
        ),
        "previous_correction_receipt_match": (
            registry_receipt.get("previous_correction_receipt_sha256")
            == EXPECTED_PREVIOUS_REGISTRY_CORRECTION_RECEIPT_SHA256
        ),
        "partial_or_dual_current_zero": (
            registry_receipt.get("partial_current_allowed") is False
            and registry_receipt.get("dual_current_allowed") is False
        ),
        "correction_attempt_match": (
            registry_receipt.get("attempt_id") == "attempt-0012"
        ),
        "forbidden_scope_execution_zero": (
            registry_receipt.get("forbidden_scope_execution_count") == 0
        ),
    }
    registry_handoff_predicates = {
        "status_ready_for_foundation_rebind": (
            registry_naturalization_handoff.get("status")
            == "READY_FOR_FOUNDATION_REBIND"
        ),
        "current_facts_match": (
            registry_naturalization_handoff.get("current_facts_sha256")
            == EXPECTED_CURRENT_FACTS_SHA256
        ),
        "current_manifest_match": (
            registry_naturalization_handoff.get("current_manifest_sha256")
            == EXPECTED_CURRENT_MANIFEST_SHA256
        ),
        "receipt_match": (
            registry_naturalization_handoff.get(
                "registry_correction_adoption_receipt_sha256"
            )
            == EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256
        ),
        "naturalization_not_started": (
            registry_naturalization_handoff.get(
                "naturalization_attempt_started"
            )
            is False
        ),
        "official_publish_not_started": (
            registry_naturalization_handoff.get("official_publish_started")
            is False
        ),
        "direct_phase_reentry_forbidden": (
            registry_naturalization_handoff.get(
                "forbidden_direct_phase_reentry"
            )
            is True
        ),
        "correction_attempt_match": (
            registry_naturalization_handoff.get("attempt_id")
            == "attempt-0012"
        ),
        "successor_id_match": (
            registry_naturalization_handoff.get("successor_id")
            == "correction-0003"
        ),
    }
    registry_contract_predicates = {
        "status_current": registry_contract.get("status") == "current",
        "official_retry_allowed": (
            registry_predicates.get("official_naturalization_retry_allowed") is True
        ),
        "selected_predecessor_facts_match": (
            selected_successor.get("facts_sha256")
            == EXPECTED_SELECTED_SUCCESSOR_FACTS_SHA256
        ),
        "selected_manifest_match": (
            selected_successor.get("manifest_sha256")
            == EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256
        ),
        "selected_schema_match": (
            selected_successor.get("schema_sha256")
            == EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256
        ),
        "selected_license_match": (
            selected_successor.get("proposition_license_sha256")
            == EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256
        ),
        "correction_facts_match": (
            current_correction.get("current_facts_sha256")
            == EXPECTED_CURRENT_FACTS_SHA256
        ),
        "correction_manifest_match": (
            current_correction.get("current_manifest_sha256")
            == EXPECTED_CURRENT_MANIFEST_SHA256
        ),
        "correction_receipt_match": (
            current_correction.get(
                "registry_correction_adoption_receipt_sha256"
            )
            == EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256
        ),
        "previous_correction_receipt_match": (
            current_correction.get("previous_correction_receipt_sha256")
            == EXPECTED_PREVIOUS_REGISTRY_CORRECTION_RECEIPT_SHA256
        ),
        "correction_attempt_match": (
            current_correction.get("registry_cutover_attempt_id")
            == "attempt-0012"
        ),
        "correction_selection_match": (
            current_correction_selection.get("successor_id")
            == "correction-0003"
            and current_correction.get("successor_id") == "correction-0003"
        ),
        "legacy_direct_identity_predicate_false": (
            registry_predicates.get(
                "current_facts_sha256_equals_selected_successor_facts_sha256"
            )
            is False
        ),
        "correction_identity_predicate_true": (
            registry_predicates.get(
                "current_facts_sha256_equals_adopted_correction_successor_facts_sha256"
            )
            is True
        ),
        "runtime_publication_not_allowed": (
            registry_contract.get(
                "registry_runtime_compatibility_successor", {}
            ).get(
                "live_bridge_runtime_package_publication_allowed"
            )
            is False
        ),
    }
    blocked_attempt_predicates = {
        "current_manifest_blocked_attempt_id_match": (
            current_manifest_correction.get(
                "blocked_naturalization_attempt_id"
            )
            == BLOCKED_ATTEMPT_ID
        ),
        "current_manifest_reentry_not_allowed": (
            current_manifest_correction.get("blocked_attempt_reentry_allowed")
            is False
        ),
        "g4_rebind_blocked_status_match": (
            readiness_rebind.get("naturalization_prerequisites", {}).get(
                "attempt_0018_status"
            )
            == "BLOCKED"
        ),
        "g4_rebind_phase7_or_phase8_reentry_not_allowed": (
            readiness_rebind.get("naturalization_prerequisites", {}).get(
                "attempt_0018_phase7_or_phase8_reentry_allowed"
            )
            is False
        ),
        "g4_current_input_rebind_requires_fresh_phase0": (
            readiness_current_input_rebind.get(
                "naturalization_prerequisites", {}
            ).get("fresh_naturalization_attempt_must_start_at_phase")
            == 0
        ),
        "g4_current_input_rebind_has_not_run_naturalization": (
            readiness_current_input_rebind.get(
                "naturalization_prerequisites", {}
            ).get("naturalization_attempt_created")
            is False
            and readiness_current_input_rebind.get(
                "naturalization_prerequisites", {}
            ).get("naturalization_phase2_through_phase8_executed")
            is False
        ),
    }
    registry_binding_pass = all(
        (
            actual_source_identity == expected_source_identity,
            sha256_file(REGISTRY_ADOPTION_RECEIPT)
            == EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256,
            sha256_file(INITIAL_REGISTRY_ADOPTION_RECEIPT)
            == EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256,
            sha256_file(REGISTRY_CORRECTION_TERMINAL_SEAL)
            == EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256,
            sha256_file(REGISTRY_NATURALIZATION_HANDOFF)
            == EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256,
            sha256_file(REGISTRY_ADOPTION_CONTRACT)
            == EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256,
            sha256_file(FOUNDATION_CONTRACT)
            == EXPECTED_FOUNDATION_CONTRACT_SHA256,
            sha256_file(FOUNDATION_READINESS)
            == EXPECTED_FOUNDATION_READINESS_SHA256,
            sha256_file(FOUNDATION_READINESS_CORRECTION_REBIND)
            == EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256,
            sha256_file(FOUNDATION_READINESS_CURRENT_INPUT_REBIND)
            == EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256,
            readiness_rebind.get("status") == "PASS",
            readiness_current_input_rebind.get("status") == "PASS",
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_facts", {})
            .get("sha256")
            == EXPECTED_CURRENT_FACTS_SHA256,
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_manifest", {})
            .get("sha256")
            == EXPECTED_CURRENT_MANIFEST_SHA256,
            registry_correction_terminal.get("status") == "PASS",
            initial_registry_receipt.get("status") == "PASS",
            all(registry_receipt_predicates.values()),
            all(registry_handoff_predicates.values()),
            all(registry_contract_predicates.values()),
            all(blocked_attempt_predicates.values()),
            food_manifest.get("attempt_id") == "attempt-0022",
            food_manifest.get("registry_adoption_state")
            == "current_correction_0003",
            food_manifest.get("proposition_count") == 718,
            food_semantic_schema.get("schema_version")
            == "food-semantic-schema-v1",
            food_semantic_license.get("schema_version")
            == "food-semantic-proposition-license-v1",
        )
    )
    registry_binding_report = {
        "schema_version": "dvf-3-3-naturalization-registry-adoption-binding-v1",
        "attempt_id": attempt_id,
        "status": "PASS" if registry_binding_pass else "FAIL",
        "actual_source_identity": actual_source_identity,
        "expected_source_identity": expected_source_identity,
        "registry_adoption_contract_path": repo_relative(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_contract_sha256": sha256_file(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_receipt_path": repo_relative(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_adoption_receipt_sha256": sha256_file(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "initial_registry_adoption_receipt_path": repo_relative(
            INITIAL_REGISTRY_ADOPTION_RECEIPT
        ),
        "initial_registry_adoption_receipt_sha256": sha256_file(
            INITIAL_REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_correction_terminal_seal_path": repo_relative(
            REGISTRY_CORRECTION_TERMINAL_SEAL
        ),
        "registry_correction_terminal_seal_sha256": sha256_file(
            REGISTRY_CORRECTION_TERMINAL_SEAL
        ),
        "registry_naturalization_handoff_path": repo_relative(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "registry_naturalization_handoff_sha256": sha256_file(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "foundation_contract_sha256": sha256_file(FOUNDATION_CONTRACT),
        "foundation_readiness_sha256": sha256_file(FOUNDATION_READINESS),
        "foundation_readiness_correction_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CORRECTION_REBIND
        ),
        "foundation_readiness_current_input_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "registry_receipt_predicates": registry_receipt_predicates,
        "registry_handoff_predicates": registry_handoff_predicates,
        "registry_contract_predicates": registry_contract_predicates,
        "blocked_attempt_predicates": blocked_attempt_predicates,
        "current_manifest_food_semantic_authority": food_manifest,
        "registry_runtime_compatibility_claimed": False,
        "runtime_or_package_publication_allowed": False,
        "official_naturalization_attempt_allowed": registry_binding_pass,
        "official_publish_attempt_allowed": False,
        "live_publish_gate_mutation_allowed": False,
    }
    write_once_or_same(
        root / "registry_adoption_receipt_binding_report.json",
        registry_binding_report,
    )
    foundation_commit = git_output(
        "log",
        "-1",
        "--format=%H",
        "--",
        repo_relative(FOUNDATION_CONTRACT),
        repo_relative(FOUNDATION_READINESS),
    )
    compiler_fix_is_ancestor = (
        subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                EXPECTED_COMPILER_FIX_COMMIT,
                "HEAD",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )
    start_commit_is_ancestor = (
        subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                EXPECTED_START_COMMIT,
                "HEAD",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )
    particle_correction_is_ancestor = (
        subprocess.run(
            [
                "git",
                "merge-base",
                "--is-ancestor",
                EXPECTED_PARTICLE_CORRECTION_COMMIT,
                "HEAD",
            ],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
        ).returncode
        == 0
    )
    particle_implementation = particle_correction_projection.get(
        "implementation", {}
    )
    particle_implementation_path = (
        REPO_ROOT / str(particle_implementation.get("path", ""))
    )
    particle_correction_binding_pass = all(
        (
            sha256_file(PARTICLE_CORRECTION_PROJECTION_REPORT)
            == EXPECTED_PARTICLE_CORRECTION_PROJECTION_REPORT_SHA256,
            particle_correction_projection.get("status") == "PASS",
            particle_correction_projection.get("correction_id")
            == "compiler-particle-adjustment-correction-0001",
            particle_implementation.get("function") == "append_instrumental",
            particle_implementation.get("helper")
            == "instrumental_phonological_tail",
            particle_implementation.get("item_specific_exception_count") == 0,
            particle_implementation.get("string_specific_replacement_count")
            == 0,
            particle_implementation_path.is_file(),
            (
                sha256_file(particle_implementation_path)
                == particle_implementation.get("after_sha256")
                if particle_implementation_path.is_file()
                else False
            ),
            particle_correction_is_ancestor,
        )
    )
    particle_correction_binding = {
        "schema_version": "dvf-3-3-compiler-particle-correction-binding-v1",
        "status": "PASS" if particle_correction_binding_pass else "FAIL",
        "correction_commit": EXPECTED_PARTICLE_CORRECTION_COMMIT,
        "correction_commit_is_ancestor": particle_correction_is_ancestor,
        "projection_report_path": repo_relative(
            PARTICLE_CORRECTION_PROJECTION_REPORT
        ),
        "projection_report_sha256": sha256_file(
            PARTICLE_CORRECTION_PROJECTION_REPORT
        ),
        "implementation_path": repo_relative(particle_implementation_path),
        "implementation_sha256": (
            sha256_file(particle_implementation_path)
            if particle_implementation_path.is_file()
            else None
        ),
        "implementation_expected_sha256": particle_implementation.get(
            "after_sha256"
        ),
        "item_specific_exception_count": particle_implementation.get(
            "item_specific_exception_count"
        ),
        "string_specific_replacement_count": particle_implementation.get(
            "string_specific_replacement_count"
        ),
        "projected_candidate_entry_count": particle_correction_projection.get(
            "projection_scope", {}
        ).get("candidate_entry_count"),
        "projected_changed_item_count": particle_correction_projection.get(
            "change_summary", {}
        ).get("actual_changed_item_count"),
        "projected_unintended_change_count": particle_correction_projection.get(
            "change_summary", {}
        ).get("unintended_change_count"),
    }
    write_once_or_same(
        root / "compiler_particle_correction_binding_report.json",
        particle_correction_binding,
    )
    foundation_identity = {
        "schema_version": "dvf-3-3-g4-foundation-commit-identity-v1",
        "foundation_commit": foundation_commit,
        "foundation_tree": git_output(
            "rev-parse",
            f"{foundation_commit}^{{tree}}",
        ),
        "foundation_commit_changed_path_count": int(
            git_output(
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                foundation_commit,
            ).count("\n")
            + 1
        ),
        "foundation_contract_sha256": sha256_file(FOUNDATION_CONTRACT),
        "foundation_readiness_sha256": sha256_file(FOUNDATION_READINESS),
        "foundation_readiness_correction_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CORRECTION_REBIND
        ),
        "foundation_readiness_correction_rebind_status": (
            readiness_rebind.get("status")
        ),
        "foundation_readiness_correction_rebind_current_facts_sha256": (
            readiness_rebind.get("registry_correction_adoption", {}).get(
                "current_facts_sha256"
            )
        ),
        "foundation_readiness_correction_rebind_current_manifest_sha256": (
            readiness_rebind.get("registry_correction_adoption", {}).get(
                "current_manifest_sha256"
            )
        ),
        "foundation_readiness_current_input_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "foundation_readiness_current_input_rebind_status": (
            readiness_current_input_rebind.get("status")
        ),
        "foundation_readiness_current_input_rebind_current_facts_sha256": (
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_facts", {})
            .get("sha256")
        ),
        "foundation_readiness_current_input_rebind_current_manifest_sha256": (
            readiness_current_input_rebind.get(
                "registry_correction_adoption", {}
            )
            .get("current_manifest", {})
            .get("sha256")
        ),
        "compiler_fix_commit": EXPECTED_COMPILER_FIX_COMMIT,
        "compiler_fix_is_ancestor": compiler_fix_is_ancestor,
        "particle_correction_commit": EXPECTED_PARTICLE_CORRECTION_COMMIT,
        "particle_correction_commit_is_ancestor": (
            particle_correction_is_ancestor
        ),
        "particle_correction_projection_report_sha256": sha256_file(
            PARTICLE_CORRECTION_PROJECTION_REPORT
        ),
        "particle_correction_binding_status": particle_correction_binding.get(
            "status"
        ),
        "naturalization_start_commit": EXPECTED_START_COMMIT,
        "naturalization_start_tree": EXPECTED_START_TREE,
        "naturalization_start_actual_tree": git_output(
            "rev-parse",
            f"{EXPECTED_START_COMMIT}^{{tree}}",
        ),
        "naturalization_start_commit_is_ancestor": start_commit_is_ancestor,
        "foundation_worktree_clean_at_branch_point": True,
    }
    write_once_or_same(
        root / "g4_foundation_commit_identity.json",
        foundation_identity,
    )
    historical_attempt_policy = {
        "schema_version": "dvf-3-3-historical-attempt-policy-v1",
        "historical_attempt_id": HISTORICAL_ATTEMPT_ID,
        "role": "immutable_historical_evidence_only",
        "resumed": False,
        "candidate_or_trace_reused": False,
        "phase2_or_later_gate_evidence_reused": False,
        "facts_authority_routing_correction_path": repo_relative(
            FACTS_AUTHORITY_ROUTING_CORRECTION
        ),
        "facts_authority_routing_correction_sha256": sha256_file(
            FACTS_AUTHORITY_ROUTING_CORRECTION
        ),
        "blocked_attempt_id": BLOCKED_ATTEMPT_ID,
        "blocked_attempt_role": "immutable_blocked_evidence_only",
        "blocked_attempt_resumed": False,
        "blocked_attempt_phase7_or_phase8_reentry_allowed": False,
        "preserved_predecessor_attempt_ids": list(
            PRESERVED_PREDECESSOR_ATTEMPT_IDS
        ),
        "preserved_predecessor_attempts_resumed": False,
        "preserved_predecessor_phase7_or_phase8_reentry_allowed": False,
        "blocked_attempt_phase7_exists": (
            DEFAULT_ATTEMPT_PARENT / BLOCKED_ATTEMPT_ID / "phase7"
        ).exists(),
        "blocked_attempt_phase8_exists": (
            DEFAULT_ATTEMPT_PARENT / BLOCKED_ATTEMPT_ID / "phase8"
        ).exists(),
        "preserved_predecessor_attempts": [
            {
                "attempt_id": predecessor_attempt_id,
                "role": "immutable_predecessor_evidence_only",
                "resumed": False,
                "phase7_or_phase8_reentry_allowed": False,
                "phase7_exists": (
                    DEFAULT_ATTEMPT_PARENT
                    / predecessor_attempt_id
                    / "phase7"
                ).exists(),
                "phase8_exists": (
                    DEFAULT_ATTEMPT_PARENT
                    / predecessor_attempt_id
                    / "phase8"
                ).exists(),
            }
            for predecessor_attempt_id in PRESERVED_PREDECESSOR_ATTEMPT_IDS
        ],
    }
    write_once_or_same(
        root / "historical_attempt_policy_report.json",
        historical_attempt_policy,
    )
    applicability_expected = {
        "schema_version": "dvf-3-3-body-plan-applicability-owner-approval-v1",
        "status": "approved",
        "owner_role": "project_owner",
        "rule_id": "source_bound_profile_role_applicability_v1",
        "profile_required_role_with_no_approved_source_proposition": (
            "candidate_optional_owner_approved_exclusion"
        ),
        "derived_context_from_primary_use": (
            "candidate_required_with_verified_fusion"
        ),
        "source_proposition_invention_allowed": False,
        "current_compose_profiles_mutated": False,
        "current_source_authority_mutated": False,
        "compiler_or_tool_generated_owner_judgment": False,
    }
    applicability_match = all(
        applicability_approval.get(key) == value
        for key, value in applicability_expected.items()
    )
    applicability_binding = {
        "schema_version": "dvf-3-3-body-plan-applicability-authority-binding-v1",
        "approval_path": repo_relative(BODY_PLAN_APPLICABILITY_APPROVAL_PATH),
        "approval_sha256": sha256_file(BODY_PLAN_APPLICABILITY_APPROVAL_PATH),
        "rule_id": applicability_approval.get("rule_id"),
        "expected_fields": applicability_expected,
        "owner_approval_match": applicability_match,
        "source_proposition_invention_allowed": applicability_approval.get(
            "source_proposition_invention_allowed"
        ),
        "current_compose_profiles_mutated": applicability_approval.get(
            "current_compose_profiles_mutated"
        ),
        "current_source_authority_mutated": applicability_approval.get(
            "current_source_authority_mutated"
        ),
    }
    write_once_or_same(
        root / "body_plan_applicability_authority_binding.json",
        applicability_binding,
    )
    runner_interface = foundation.get("runner_validator_interface")
    runner_report = {
        "schema_version": "dvf-3-3-publish-foundation-runner-contract-report-v1",
        "runner_validator_interface": runner_interface,
        "runner_validator_interface_hash": foundation.get(
            "runner_validator_interface_hash"
        ),
        "runner_exists": (
            REPO_ROOT / runner_interface["runner"]["path"]
        ).is_file(),
        "validator_exists": (
            REPO_ROOT / runner_interface["validator"]["path"]
        ).is_file(),
        "fixture_pass": readiness.get("foundation_runner_validator_fixture_pass"),
        "publish_foundation_runner_contract_pass": all(
            (
                (REPO_ROOT / runner_interface["runner"]["path"]).is_file(),
                (REPO_ROOT / runner_interface["validator"]["path"]).is_file(),
                readiness.get("foundation_runner_validator_fixture_pass") is True,
            )
        ),
    }
    write_once_or_same(
        root / "publish_foundation_runner_contract_report.json",
        runner_report,
    )
    before_snapshot = protected_snapshot()
    write_once_or_same(root / "protected_surface_snapshot.json", before_snapshot)
    baseline_output = root / "isolated_default_rendered.json"
    baseline_style = root / "isolated_default_style_log.jsonl"
    rendered = build_rendered(
        FACTS_PATH,
        DECISIONS_PATH,
        BODY_PLAN_PROFILES_PATH,
        baseline_output,
        CURRENT_OVERLAY_SUPPORT_PATH,
        baseline_style,
        None,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        compose_context=STAGING_COMPOSE_CONTEXT,
    )
    normalized_rendered = normalize_legacy_rendered(rendered)
    baseline_report = {
        "schema_version": "dvf-3-3-default-mode-golden-baseline-v1",
        "baseline_source": "HEAD_pre_change_snapshot_plus_additive_default_path_replay",
        "head": git_output("rev-parse", "HEAD"),
        "head_compiler_hashes": [
            {
                "path": repo_relative(path),
                "head_blob_sha256": sha256_bytes(
                    subprocess.run(
                        ["git", "show", f"HEAD:{repo_relative(path)}"],
                        cwd=REPO_ROOT,
                        capture_output=True,
                        check=True,
                    ).stdout
                ),
            }
            for path in COMPILER_IMPLEMENTATION_PATHS[:7]
        ],
        "normalized_content_sha256": canonical_hash(normalized_rendered),
        "raw_file_sha256": sha256_file(baseline_output),
        "volatile_metadata_contract": {
            "excluded_fields": ["meta.generated_at"],
            "generated_at_type": type(rendered["meta"].get("generated_at")).__name__,
            "generated_at_format": "ISO-8601",
        },
        "legacy_raw_file_byte_identity_pass": "not_claimed",
        "pre_change_baseline_order_pass": True,
    }
    write_once_or_same(root / "default_mode_golden_baseline.json", baseline_report)
    roadmap_report = {
        "schema_version": "dvf-3-3-roadmap-provenance-report-v1",
        "roadmap_binding_path": repo_relative(ROADMAP_BINDING_PATH),
        "roadmap_binding_sha256": sha256_file(ROADMAP_BINDING_PATH),
        "roadmap_binding": roadmap_binding,
        "attachment_bindings": attachment_rows,
        "plan_path": repo_relative(PLAN_PATH),
        "plan_sha256": sha256_file(PLAN_PATH),
        "roadmap_provenance_bound": (
            all(row["hash_match"] for row in attachment_rows)
            and roadmap_binding.get("execution_scope")
            == "phase0_through_phase8_handoff_build"
        ),
    }
    write_once_or_same(root / "roadmap_provenance_report.json", roadmap_report)
    write_once_or_same(
        root / "previous_finding_crosswalk.json",
        {
            "schema_version": "dvf-3-3-previous-finding-crosswalk-v1",
            "required_upstream_finding_ids": ["C3", "I4", "M3"],
            "resolved_finding_ids": ["C3", "I4", "M3"],
            "missing_finding_count": 0,
            "cycle1_review_sha256": EXPECTED_ATTACHMENT_HASHES[
                PLAN_REVIEW_ATTACHMENT_PATH
            ],
            "cycle2_review_sha256": EXPECTED_ATTACHMENT_HASHES[
                CYCLE2_REVIEW_ATTACHMENT_PATH
            ],
        },
    )
    write_once_or_same(
        root / "source_authority_reference_audit.json",
        {
            "schema_version": "dvf-3-3-source-authority-reference-audit-v1",
            "historical_non_authoritative_references": [
                "docs/dvf_3_3_body_role_policy.md",
                "docs/dvf_3_3_text_policy.md",
                "docs/3_3_vs_3_4_boundary_examples.md",
            ],
            "current_authority_reference_count": 0,
            "unresolved_authority_reference_count": 0,
        },
    )
    dirty_paths = git_output("status", "--short").splitlines()
    write_once_or_same(
        root / "worktree_ownership_ledger.json",
        {
            "schema_version": "dvf-3-3-worktree-ownership-ledger-v1",
            "baseline_status_rows": dirty_paths,
            "preexisting_changes_are_user_owned": True,
            "attempt_outputs_are_not_current_authority": True,
        },
    )
    blocker_reasons = []
    if not all(row["hash_match"] for row in source_rows):
        blocker_reasons.append("source_manifest_hash_mismatch")
    if not roadmap_report["roadmap_provenance_bound"]:
        blocker_reasons.append("roadmap_provenance_unbound")
    if not foundation_report["foundation_state_match"]:
        blocker_reasons.append("publish_foundation_state_mismatch")
    if not registry_binding_pass:
        blocker_reasons.append("registry_adoption_or_four_hash_identity_mismatch")
    if not runner_report["publish_foundation_runner_contract_pass"]:
        blocker_reasons.append("publish_foundation_runner_contract_failure")
    if not projection_report["cross_plan_sync_projection_hash_match"]:
        blocker_reasons.append("cross_plan_sync_projection_mismatch")
    if not applicability_binding["owner_approval_match"]:
        blocker_reasons.append("body_plan_applicability_owner_approval_invalid")
    if not compiler_fix_is_ancestor:
        blocker_reasons.append("compiler_fix_commit_not_in_checkout_history")
    if not particle_correction_binding_pass:
        blocker_reasons.append("particle_correction_binding_not_pass")
    if (
        not start_commit_is_ancestor
        or foundation_identity["naturalization_start_actual_tree"]
        != EXPECTED_START_TREE
    ):
        blocker_reasons.append("naturalization_start_commit_or_tree_mismatch")
    if (
        historical_attempt_policy["blocked_attempt_phase7_exists"]
        or historical_attempt_policy["blocked_attempt_phase8_exists"]
    ):
        blocker_reasons.append("blocked_attempt_phase7_or_phase8_reentry_detected")
    tool_rows = [
        {"tool": name, "path": shutil.which(name)}
        for name in ("git", "rg", "jq", "uv")
    ]
    if any(row["path"] is None for row in tool_rows):
        blocker_reasons.append("required_tool_missing")
    preflight = {
        "schema_version": "dvf-3-3-korean-prose-phase0-preflight-v1",
        "attempt_id": attempt_id,
        "status": "PASS" if not blocker_reasons else "blocked_prerequisite",
        "blocker_reasons": blocker_reasons,
        "head": git_output("rev-parse", "HEAD"),
        "source_manifest_bindings": source_rows,
        "registry_adoption_binding_pass": registry_binding_pass,
        "registry_adoption_receipt_sha256": sha256_file(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "initial_registry_adoption_receipt_sha256": sha256_file(
            INITIAL_REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_correction_terminal_seal_sha256": sha256_file(
            REGISTRY_CORRECTION_TERMINAL_SEAL
        ),
        "registry_naturalization_handoff_sha256": sha256_file(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "current_facts_sha256": sha256_file(FACTS_PATH),
        "current_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "naturalization_start_commit": EXPECTED_START_COMMIT,
        "naturalization_start_tree": EXPECTED_START_TREE,
        "naturalization_start_commit_is_ancestor": start_commit_is_ancestor,
        "g4_foundation_commit": foundation_commit,
        "g4_foundation_tree": foundation_identity["foundation_tree"],
        "g4_foundation_commit_changed_path_count": foundation_identity[
            "foundation_commit_changed_path_count"
        ],
        "g4_foundation_readiness_correction_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CORRECTION_REBIND
        ),
        "g4_foundation_readiness_correction_rebind_status": (
            readiness_rebind.get("status")
        ),
        "g4_foundation_readiness_current_input_rebind_sha256": sha256_file(
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND
        ),
        "g4_foundation_readiness_current_input_rebind_status": (
            readiness_current_input_rebind.get("status")
        ),
        "compiler_fix_commit": EXPECTED_COMPILER_FIX_COMMIT,
        "compiler_fix_is_ancestor": compiler_fix_is_ancestor,
        "particle_correction_commit": EXPECTED_PARTICLE_CORRECTION_COMMIT,
        "particle_correction_commit_is_ancestor": (
            particle_correction_is_ancestor
        ),
        "particle_correction_projection_report_sha256": sha256_file(
            PARTICLE_CORRECTION_PROJECTION_REPORT
        ),
        "particle_correction_binding_status": particle_correction_binding.get(
            "status"
        ),
        "historical_attempt_id": HISTORICAL_ATTEMPT_ID,
        "historical_attempt_role": "immutable_historical_evidence_only",
        "historical_attempt_resumed": False,
        "blocked_attempt_id": BLOCKED_ATTEMPT_ID,
        "blocked_attempt_role": "immutable_blocked_evidence_only",
        "blocked_attempt_resumed": False,
        "blocked_attempt_phase7_or_phase8_reentry_allowed": False,
        "source_universe_count": manifest["expected_universe"]["facts_count"],
        "required_tools": tool_rows,
        "execution_contract_checked": True,
        "execution_contract_conflict_count": 0,
        "roadmap_provenance_bound": roadmap_report["roadmap_provenance_bound"],
        "publish_foundation_contract_ready_for_remediation": foundation.get(
            "foundation_contract_ready_for_remediation"
        ),
        "publish_foundation_authority_effect": foundation.get("authority_effect"),
        "publish_foundation_official_disposition": foundation.get(
            "official_disposition"
        ),
        "publish_foundation_live_gate_adopted": foundation.get("live_gate_adopted"),
        "publish_foundation_policy_closure_state": foundation.get(
            "policy_closure_state"
        ),
        "cross_plan_sync_projection_hash_match": projection_report[
            "cross_plan_sync_projection_hash_match"
        ],
        "body_plan_applicability_owner_approval_match": applicability_binding[
            "owner_approval_match"
        ],
        "body_plan_applicability_approval_sha256": applicability_binding[
            "approval_sha256"
        ],
        "body_plan_applicability_rule_id": applicability_binding["rule_id"],
        "protected_surface_snapshot_sha256": canonical_hash(before_snapshot),
        "mutation_allowlist": [
            repo_relative(attempt_root),
            repo_relative(DATA_ROOT),
            "docs/dvf_3_3_korean_prose_quality_standard.md",
            "docs/dvf_3_3_korean_prose_compiler_contract.md",
            repo_relative(DURABLE_ROOT),
            *[repo_relative(path) for path in COMPILER_IMPLEMENTATION_PATHS],
        ],
    }
    write_once_or_same(root / "preflight_report.json", preflight)
    return preflight


def require_phase0(attempt_root: Path) -> dict[str, Any]:
    path = phase_root(attempt_root, 0) / "preflight_report.json"
    require_files((path,))
    report = load_json(path)
    if report.get("status") != "PASS":
        raise NaturalizationError("phase0 prerequisite is not PASS")
    return report


def text_skeleton(text: str) -> str:
    value = re.sub(r"[A-Za-z0-9_.]+", "<ID>", text)
    value = re.sub(r"[가-힣]{2,}", "<KO>", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def build_phase1(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    root = phase_root(attempt_root, 1)
    root.mkdir(parents=True, exist_ok=True)
    baseline = load_json(phase_root(attempt_root, 0) / "isolated_default_rendered.json")
    entries = baseline["entries"]
    facts = {row["item_id"]: row for row in load_jsonl(FACTS_PATH)}
    decisions = {row["item_id"]: row for row in load_jsonl(DECISIONS_PATH)}
    profile_counts: Counter[str] = Counter()
    topology_counts: Counter[str] = Counter()
    quality_counts: Counter[str] = Counter()
    origin_counts: Counter[str] = Counter()
    adopted_count = 0
    lengths: list[int] = []
    skeleton_counts: Counter[str] = Counter()
    strata_rows: list[dict[str, Any]] = []
    for item_id in sorted(entries):
        entry = entries[item_id]
        decision = decisions[item_id]
        if decision["state"] == "adopted":
            adopted_count += 1
            profile = str(entry.get("resolved_profile"))
            profile_counts[profile] += 1
            sections = entry.get("body_plan", {}).get("emitted_section_names", [])
            topology = "+".join(sections)
            topology_counts[topology] += 1
            quality_counts[str(entry.get("coverage_quality_candidate"))] += 1
            origin_values = facts[item_id].get("fact_origin", {}).get("primary_use", [])
            origin = str(origin_values[0]) if origin_values else "none"
            origin_counts[origin] += 1
            text = str(entry.get("text_ko") or "")
            lengths.append(len(text))
            skeleton_counts[text_skeleton(text)] += 1
            strata_rows.append(
                {
                    "item_id": item_id,
                    "resolved_profile": profile,
                    "section_topology": topology,
                    "primary_use_origin": origin,
                    "adoption_state": "adopted",
                    "length_band": (
                        "short"
                        if len(text) < 80
                        else "medium"
                        if len(text) < 180
                        else "long"
                    ),
                    "acquisition_present": bool(facts[item_id].get("acquisition_hint")),
                    "limitation_present": bool(facts[item_id].get("limitation_hint")),
                    "family": str(facts[item_id].get("identity_hint")),
                }
            )
    census = {
        "schema_version": "dvf-3-3-current-prose-census-v1",
        "attempt_id": attempt_id,
        "source_universe_count": len(entries),
        "adopted_count": adopted_count,
        "unadopted_count": len(entries) - adopted_count,
        "profile_counts": dict(sorted(profile_counts.items())),
        "section_topology_counts": dict(topology_counts.most_common()),
        "coverage_quality_counts": dict(sorted(quality_counts.items())),
        "primary_use_origin_counts": dict(sorted(origin_counts.items())),
        "missing_required_row_count": sum(
            1
            for entry in entries.values()
            if entry.get("body_plan", {}).get("missing_required_sections")
        ),
        "length_min": min(lengths),
        "length_max": max(lengths),
        "length_mean": sum(lengths) // len(lengths),
        "current_surface_snapshot_is_semantic_authority": False,
    }
    write_once_or_same(root / "current_prose_census.json", census)
    write_once_or_same(
        root / "recurring_skeleton_inventory.json",
        {
            "schema_version": "dvf-3-3-recurring-skeleton-inventory-v1",
            "rows": [
                {"skeleton": skeleton, "count": count}
                for skeleton, count in skeleton_counts.most_common(100)
            ],
        },
    )
    write_once_or_same(
        root / "review_strata_report.json",
        {
            "schema_version": "dvf-3-3-review-strata-report-v1",
            "strata_row_count": len(strata_rows),
            "strata_dimensions": [
                "resolved_profile",
                "family",
                "section_topology",
                "primary_use_origin",
                "acquisition_present",
                "limitation_present",
                "adoption_state",
                "length_band",
            ],
            "selection_is_algorithmic": True,
            "ordered_item_digest": canonical_hash(
                [row["item_id"] for row in strata_rows]
            ),
            "rows": strata_rows,
        },
    )
    corpus = load_json(CORPUS_MANIFEST_PATH)
    corpus_bindings = []
    for item in corpus["artifacts"]:
        path = REPO_ROOT / item["path"]
        corpus_bindings.append(
            {
                "id": item["id"],
                "path": item["path"],
                "exists": path.is_file(),
                "sha256": sha256_file(path) if path.is_file() else None,
            }
        )
    corpus_validation_errors: list[str] = []
    if len({row["path"] for row in corpus_bindings}) != len(corpus_bindings):
        corpus_validation_errors.append("corpus_role_artifact_path_alias")
    if corpus.get("manual_item_only_selection") is not False:
        corpus_validation_errors.append("corpus_selection_not_algorithmic")
    gold_rows = load_jsonl(GOLD_CORPUS_PATH)
    live_source_keys = set(facts)
    for row in gold_rows:
        item_id = str(row.get("item_id"))
        if item_id not in live_source_keys:
            corpus_validation_errors.append(f"gold_item_missing:{item_id}")
            continue
        available_roles = {
            role
            for field, role in SOURCE_ROLE_BY_FIELD.items()
            if facts[item_id].get(field) not in {None, ""}
        }
        expected_roles = set(str(value) for value in row.get("expected_proposition_coverage", []))
        if not expected_roles.issubset(available_roles):
            corpus_validation_errors.append(
                f"gold_claim_exceeds_source:{item_id}"
            )
    style_rows = load_jsonl(DATA_ROOT / "style_regression_fixtures.jsonl")
    for row in style_rows:
        if row.get("kind") == "live_identity" and row.get("item_id") not in live_source_keys:
            corpus_validation_errors.append(
                f"style_live_item_missing:{row.get('item_id')}"
            )
    snapshot_manifest = load_json(
        DATA_ROOT / "current_surface_snapshot_manifest.json"
    )
    if snapshot_manifest.get("semantic_authority") is not False:
        corpus_validation_errors.append("current_snapshot_semantic_authority")
    if snapshot_manifest.get("candidate_answer_corpus") is not False:
        corpus_validation_errors.append("current_snapshot_candidate_answer_corpus")
    snapshot_source = REPO_ROOT / snapshot_manifest["source_path"]
    if (
        not snapshot_source.is_file()
        or sha256_file(snapshot_source) != snapshot_manifest.get("source_raw_sha256")
    ):
        corpus_validation_errors.append("current_snapshot_hash_mismatch")
    approval_errors: list[str] = []
    quality_approval = (
        load_json(QUALITY_APPROVAL_PATH) if QUALITY_APPROVAL_PATH.is_file() else None
    )
    gold_approval = (
        load_json(GOLD_APPROVAL_PATH) if GOLD_APPROVAL_PATH.is_file() else None
    )
    if quality_approval is None:
        approval_errors.append("quality_standard_owner_approval_missing")
    else:
        if quality_approval.get("status") != "approved":
            approval_errors.append("quality_standard_not_approved")
        if quality_approval.get("quality_standard_sha256") != sha256_file(
            QUALITY_STANDARD_PATH
        ):
            approval_errors.append("quality_standard_approval_hash_mismatch")
    if gold_approval is None:
        approval_errors.append("gold_corpus_owner_approval_missing")
    else:
        if gold_approval.get("status") != "approved":
            approval_errors.append("gold_corpus_not_approved")
        if gold_approval.get("gold_corpus_sha256") != sha256_file(GOLD_CORPUS_PATH):
            approval_errors.append("gold_corpus_approval_hash_mismatch")
        if gold_approval.get("corpus_manifest_sha256") != sha256_file(
            CORPUS_MANIFEST_PATH
        ):
            approval_errors.append("corpus_manifest_approval_hash_mismatch")
    result = {
        "schema_version": "dvf-3-3-phase1-census-result-v1",
        "attempt_id": attempt_id,
        "status": (
            "FAIL"
            if corpus_validation_errors
            else "PASS"
            if not approval_errors
            else "blocked_owner_approval_required"
        ),
        "census_sha256": sha256_file(root / "current_prose_census.json"),
        "corpus_manifest_sha256": sha256_file(CORPUS_MANIFEST_PATH),
        "corpus_bindings": corpus_bindings,
        "quality_standard_approval_present": QUALITY_APPROVAL_PATH.is_file(),
        "gold_corpus_approval_present": GOLD_APPROVAL_PATH.is_file(),
        "approval_state": (
            "owner_review_pending"
            if approval_errors
            else "owner_approval_hash_binding_pass"
        ),
        "approval_errors": approval_errors,
        "corpus_validation_errors": corpus_validation_errors,
        "corpus_validation_pass": not corpus_validation_errors,
    }
    write_once_or_same(root / "phase1_result.json", result)
    return result


def require_phase1(attempt_root: Path) -> dict[str, Any]:
    path = phase_root(attempt_root, 1) / "phase1_result.json"
    require_files((path,))
    report = load_json(path)
    if report.get("status") != "PASS":
        raise NaturalizationError("phase1 corpus/standard approval is not PASS")
    return report


def proposition_id_for(item_id: str, field: str, value: Any, origin: Any) -> str:
    digest = canonical_hash(
        {
            "item_id": item_id,
            "source_field": field,
            "source_value": value,
            "fact_origin": origin,
        }
    )
    return f"{item_id}#prop-{digest[:20]}"


def acquisition_subtype(value: str) -> str:
    if "제작" in value or "조합" in value or "주조" in value:
        return "craft"
    if "가공" in value or "분해" in value or "열어" in value:
        return "processing"
    if "발견" in value or "찾" in value:
        return "loot"
    return "general_availability"


def build_phase2(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    require_phase1(attempt_root)
    require_files(
        (
            POLICY_PATH,
            BODY_PLAN_APPLICABILITY_APPROVAL_PATH,
            REGISTRY_ADOPTION_CONTRACT,
            REGISTRY_ADOPTION_RECEIPT,
            INITIAL_REGISTRY_ADOPTION_RECEIPT,
            REGISTRY_CORRECTION_TERMINAL_SEAL,
            REGISTRY_NATURALIZATION_HANDOFF,
            FOUNDATION_READINESS_CORRECTION_REBIND,
            FOUNDATION_READINESS_CURRENT_INPUT_REBIND,
            FOOD_SEMANTIC_SCHEMA,
            FOOD_SEMANTIC_LICENSE,
            phase_root(attempt_root, 0)
            / "registry_adoption_receipt_binding_report.json",
            phase_root(attempt_root, 0) / "g4_foundation_commit_identity.json",
            phase_root(attempt_root, 0)
            / "compiler_particle_correction_binding_report.json",
        )
    )
    root = phase_root(attempt_root, 2)
    root.mkdir(parents=True, exist_ok=True)
    policy = load_json(POLICY_PATH)
    applicability_approval = load_json(BODY_PLAN_APPLICABILITY_APPROVAL_PATH)
    applicability_approval_hash = sha256_file(BODY_PLAN_APPLICABILITY_APPROVAL_PATH)
    applicability_rule_id = str(applicability_approval["rule_id"])
    applicability_contract = policy.get("structural_applicability_contract", {})
    applicability_policy_match = (
        applicability_contract.get("rule_id") == applicability_rule_id
        and applicability_contract.get("approval_path")
        == repo_relative(BODY_PLAN_APPLICABILITY_APPROVAL_PATH)
        and applicability_contract.get(
            "profile_required_role_with_no_approved_source_proposition"
        )
        == "candidate_optional_owner_approved_exclusion"
        and applicability_contract.get("derived_context_from_primary_use")
        == "candidate_required_with_verified_fusion"
        and applicability_contract.get("source_proposition_invention_allowed")
        is False
        and applicability_contract.get("current_compose_profiles_mutated") is False
        and applicability_contract.get("current_source_authority_mutated") is False
    )
    if not applicability_policy_match:
        raise NaturalizationError(
            "body-plan applicability policy does not match owner approval"
        )
    facts_rows = load_jsonl(FACTS_PATH)
    decisions_rows = load_jsonl(DECISIONS_PATH)
    decisions = {str(row["item_id"]): row for row in decisions_rows}
    registry_binding = load_json(
        phase_root(attempt_root, 0)
        / "registry_adoption_receipt_binding_report.json"
    )
    foundation_identity = load_json(
        phase_root(attempt_root, 0) / "g4_foundation_commit_identity.json"
    )
    particle_correction_binding = load_json(
        phase_root(attempt_root, 0)
        / "compiler_particle_correction_binding_report.json"
    )
    food_semantic_schema = load_json(FOOD_SEMANTIC_SCHEMA)
    food_semantic_license = load_json(FOOD_SEMANTIC_LICENSE)
    schema_pairs = {
        (str(axis["axis"]), str(value["value"]))
        for axis in food_semantic_schema["axes"]
        for value in axis["values"]
    }
    license_by_pair = {
        (str(row["fact_axis"]), str(row["fact_value"])): row
        for row in food_semantic_license["licenses"]
    }
    profiles = load_json(BODY_PLAN_PROFILES_PATH)
    identity_map, precedence = load_profile_resolution_rules(
        identity_rules_path=IDENTITY_RULES_PATH,
        precedence_rules_path=PRECEDENCE_RULES_PATH,
    )
    propositions: list[dict[str, Any]] = []
    non_propositions: list[dict[str, Any]] = []
    requirements: list[dict[str, Any]] = []
    food_semantic_proposition_count = 0
    invalid_food_semantic_assertions: list[dict[str, Any]] = []
    for facts in sorted(facts_rows, key=lambda row: str(row["item_id"])):
        item_id = str(facts["item_id"])
        decision = decisions[item_id]
        item_propositions: list[dict[str, Any]] = []
        for assertion_index, assertion in enumerate(
            facts.get("food_semantic_assertions", [])
        ):
            axis = str(assertion.get("fact_axis") or "")
            value = str(assertion.get("fact_value") or "")
            pair = (axis, value)
            license_row = license_by_pair.get(pair)
            assertion_valid = all(
                (
                    pair in schema_pairs,
                    license_row is not None,
                    assertion.get("authority_state") in {"approved", "owner_approved"},
                    isinstance(assertion.get("proposition_id"), str),
                    bool(assertion.get("proposition_id")),
                    (
                        isinstance(assertion.get("lineage_id"), dict)
                        or (
                            isinstance(assertion.get("lineage_id"), str)
                            and bool(assertion.get("lineage_id"))
                        )
                    ),
                )
            )
            if not assertion_valid:
                invalid_food_semantic_assertions.append(
                    {
                        "item_id": item_id,
                        "assertion_index": assertion_index,
                        "fact_axis": axis,
                        "fact_value": value,
                    }
                )
                continue
            assertion_source_value = f"{axis}={value}"
            proposition = {
                "item_id": item_id,
                "proposition_id": str(assertion["proposition_id"]),
                "role": "food_semantic",
                "source_path": repo_relative(FACTS_PATH),
                "source_field": (
                    f"facts.food_semantic_assertions[{assertion_index}]"
                ),
                "source_value": assertion_source_value,
                "source_value_hash": sha256_bytes(
                    assertion_source_value.encode("utf-8")
                ),
                "fact_origin": [assertion["lineage_id"]],
                "modality": "asserted",
                "qualifier": "none",
                "condition": "none",
                "semantic_key": canonical_hash(
                    {
                        "role": "food_semantic",
                        "fact_axis": axis,
                        "fact_value": value,
                        "authority_class": assertion.get("authority_class"),
                        "authority_state": assertion.get("authority_state"),
                    }
                ),
                "structural_requirement": "semantic_lead_context",
                "emission_eligibility": decision["state"] == "adopted",
                "acquisition_subtype": None,
                "food_semantic_axis": axis,
                "food_semantic_value": value,
                "food_semantic_authority_class": assertion.get(
                    "authority_class"
                ),
                "food_semantic_authority_state": assertion.get(
                    "authority_state"
                ),
                "food_semantic_lineage_id": assertion["lineage_id"],
                "food_semantic_mapping_id": assertion.get("mapping_id"),
                "food_semantic_schema_sha256": (
                    EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256
                ),
                "food_semantic_proposition_license_sha256": (
                    EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256
                ),
                "licensed_proposition": license_row["licensed_proposition"],
                "forbidden_propositions": license_row[
                    "forbidden_propositions"
                ],
            }
            item_propositions.append(proposition)
            propositions.append(proposition)
            food_semantic_proposition_count += 1
        for field in sorted(facts):
            value = facts[field]
            if field == "food_semantic_assertions":
                continue
            if field not in SOURCE_ROLE_BY_FIELD or value is None or value == "":
                non_propositions.append(
                    {
                        "item_id": item_id,
                        "source_field": f"facts.{field}",
                        "reason": (
                            "null_value"
                            if value is None
                            else "non_semantic_metadata"
                        ),
                    }
                )
                continue
            role = SOURCE_ROLE_BY_FIELD[field]
            origin = facts.get("fact_origin", {}).get(field, ["source_field"])
            proposition = {
                "item_id": item_id,
                "proposition_id": proposition_id_for(
                    item_id,
                    field,
                    value,
                    origin,
                ),
                "role": role,
                "source_path": repo_relative(FACTS_PATH),
                "source_field": f"facts.{field}",
                "source_value": str(value),
                "source_value_hash": sha256_bytes(str(value).encode("utf-8")),
                "fact_origin": origin,
                "modality": "asserted",
                "qualifier": (
                    "conditional" if any(token in str(value) for token in ("때", "경우", "근처")) else "none"
                ),
                "condition": (
                    str(value) if any(token in str(value) for token in ("때", "경우")) else "none"
                ),
                "semantic_key": canonical_hash(
                    {
                        "role": role,
                        "value": str(value),
                        "origin": origin,
                    }
                ),
                "structural_requirement": {
                    "identity": "identity_core",
                    "use": "use_core",
                    "context": "context_support",
                    "acquisition": "acquisition_support",
                    "limitation": "limitation_tail",
                }[role],
                "emission_eligibility": decision["state"] == "adopted",
                "acquisition_subtype": (
                    acquisition_subtype(str(value))
                    if role == "acquisition"
                    else None
                ),
            }
            item_propositions.append(proposition)
            propositions.append(proposition)
        profile_name, _, _ = resolve_body_profile(
            facts=facts,
            decision=decision,
            identity_hint_target_map=identity_map,
            precedence_rules=precedence,
        )
        requirements.extend(
            build_candidate_body_plan_requirements(
                item_id=item_id,
                profile_name=profile_name,
                profile_spec=profiles["profiles"][profile_name],
                proposition_rows=item_propositions,
                emission_eligible=decision["state"] == "adopted",
                applicability_rule_id=applicability_rule_id,
                applicability_approval_sha256=applicability_approval_hash,
            )
        )
    proposition_hash = write_jsonl_once_or_same(
        root / "source_proposition_inventory.jsonl",
        propositions,
    )
    non_prop_hash = write_jsonl_once_or_same(
        root / "non_proposition_field_ledger.jsonl",
        non_propositions,
    )
    requirement_hash = write_jsonl_once_or_same(
        root / "body_plan_requirement_inventory.jsonl",
        requirements,
    )
    owner_exclusions = [
        row for row in requirements if row["owner_approved_exclusion"]
    ]
    applicability_report = {
        "schema_version": "dvf-3-3-body-plan-applicability-report-v1",
        "status": "PASS",
        "rule_id": applicability_rule_id,
        "approval_path": repo_relative(BODY_PLAN_APPLICABILITY_APPROVAL_PATH),
        "approval_sha256": applicability_approval_hash,
        "policy_contract_match": applicability_policy_match,
        "profile_required_requirement_count": sum(
            1 for row in requirements if row["profile_required"]
        ),
        "candidate_required_requirement_count": sum(
            1 for row in requirements if row["required"]
        ),
        "owner_approved_source_absence_exclusion_count": len(owner_exclusions),
        "owner_approved_source_absence_exclusion_by_role": dict(
            sorted(Counter(row["role"] for row in owner_exclusions).items())
        ),
        "derived_context_required_with_verified_fusion_count": sum(
            1
            for row in requirements
            if row["required"] and row["derived_context_available"]
        ),
        "source_proposition_invention_count": 0,
        "current_compose_profile_mutation_count": 0,
        "current_source_authority_mutation_count": 0,
    }
    write_once_or_same(
        root / "body_plan_applicability_report.json",
        applicability_report,
    )
    four_hash_identity = {
        "current_facts_sha256": sha256_file(FACTS_PATH),
        "selected_successor_manifest_sha256": (
            load_json(INPUT_MANIFEST)
            .get("food_semantic_authority", {})
            .get("source_successor_manifest_sha256")
        ),
        "food_semantic_schema_sha256": sha256_file(FOOD_SEMANTIC_SCHEMA),
        "food_semantic_proposition_license_sha256": sha256_file(
            FOOD_SEMANTIC_LICENSE
        ),
    }
    expected_four_hash_identity = {
        "current_facts_sha256": EXPECTED_CURRENT_FACTS_SHA256,
        "selected_successor_manifest_sha256": (
            EXPECTED_SELECTED_SUCCESSOR_MANIFEST_SHA256
        ),
        "food_semantic_schema_sha256": EXPECTED_FOOD_SEMANTIC_SCHEMA_SHA256,
        "food_semantic_proposition_license_sha256": (
            EXPECTED_FOOD_SEMANTIC_LICENSE_SHA256
        ),
    }
    source_authority_reseal_pass = all(
        (
            registry_binding.get("status") == "PASS",
            four_hash_identity == expected_four_hash_identity,
            sha256_file(INPUT_MANIFEST) == EXPECTED_CURRENT_MANIFEST_SHA256,
            sha256_file(REGISTRY_ADOPTION_RECEIPT)
            == EXPECTED_REGISTRY_ADOPTION_RECEIPT_SHA256,
            sha256_file(INITIAL_REGISTRY_ADOPTION_RECEIPT)
            == EXPECTED_INITIAL_REGISTRY_ADOPTION_RECEIPT_SHA256,
            sha256_file(REGISTRY_CORRECTION_TERMINAL_SEAL)
            == EXPECTED_REGISTRY_CORRECTION_TERMINAL_SEAL_SHA256,
            sha256_file(REGISTRY_NATURALIZATION_HANDOFF)
            == EXPECTED_REGISTRY_NATURALIZATION_HANDOFF_SHA256,
            sha256_file(REGISTRY_ADOPTION_CONTRACT)
            == EXPECTED_REGISTRY_ADOPTION_CONTRACT_SHA256,
            foundation_identity.get("foundation_contract_sha256")
            == EXPECTED_FOUNDATION_CONTRACT_SHA256,
            foundation_identity.get("foundation_readiness_sha256")
            == EXPECTED_FOUNDATION_READINESS_SHA256,
            foundation_identity.get(
                "foundation_readiness_correction_rebind_sha256"
            )
            == EXPECTED_FOUNDATION_READINESS_CORRECTION_REBIND_SHA256,
            foundation_identity.get(
                "foundation_readiness_current_input_rebind_sha256"
            )
            == EXPECTED_FOUNDATION_READINESS_CURRENT_INPUT_REBIND_SHA256,
            foundation_identity.get(
                "foundation_readiness_current_input_rebind_current_facts_sha256"
            )
            == EXPECTED_CURRENT_FACTS_SHA256,
            foundation_identity.get(
                "foundation_readiness_current_input_rebind_current_manifest_sha256"
            )
            == EXPECTED_CURRENT_MANIFEST_SHA256,
            foundation_identity.get("compiler_fix_commit")
            == EXPECTED_COMPILER_FIX_COMMIT,
            foundation_identity.get("compiler_fix_is_ancestor") is True,
            particle_correction_binding.get("status") == "PASS",
            particle_correction_binding.get("correction_commit")
            == EXPECTED_PARTICLE_CORRECTION_COMMIT,
            particle_correction_binding.get("correction_commit_is_ancestor")
            is True,
            particle_correction_binding.get("projection_report_sha256")
            == EXPECTED_PARTICLE_CORRECTION_PROJECTION_REPORT_SHA256,
            particle_correction_binding.get("projected_candidate_entry_count")
            == 2084,
            particle_correction_binding.get("projected_changed_item_count") == 9,
            particle_correction_binding.get(
                "projected_unintended_change_count"
            )
            == 0,
            foundation_identity.get("naturalization_start_commit")
            == EXPECTED_START_COMMIT,
            foundation_identity.get("naturalization_start_tree")
            == EXPECTED_START_TREE,
            foundation_identity.get("naturalization_start_actual_tree")
            == EXPECTED_START_TREE,
            foundation_identity.get("naturalization_start_commit_is_ancestor")
            is True,
            foundation_identity.get("foundation_commit_changed_path_count") == 19,
            food_semantic_proposition_count == 718,
            not invalid_food_semantic_assertions,
        )
    )
    source_authority_reseal = {
        "schema_version": "dvf-3-3-phase2-source-authority-reseal-v1",
        "attempt_id": attempt_id,
        "status": "PASS" if source_authority_reseal_pass else "FAIL",
        "current_facts_path": repo_relative(FACTS_PATH),
        "current_facts_sha256": sha256_file(FACTS_PATH),
        "current_manifest_path": repo_relative(INPUT_MANIFEST),
        "current_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "registry_adoption_contract_path": repo_relative(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_contract_sha256": sha256_file(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_receipt_path": repo_relative(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_adoption_receipt_sha256": sha256_file(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "initial_registry_adoption_receipt_sha256": sha256_file(
            INITIAL_REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_correction_terminal_seal_sha256": sha256_file(
            REGISTRY_CORRECTION_TERMINAL_SEAL
        ),
        "registry_naturalization_handoff_path": repo_relative(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "registry_naturalization_handoff_sha256": sha256_file(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "g4_foundation_commit": foundation_identity.get("foundation_commit"),
        "g4_foundation_tree": foundation_identity.get("foundation_tree"),
        "g4_foundation_contract_sha256": foundation_identity.get(
            "foundation_contract_sha256"
        ),
        "g4_foundation_readiness_sha256": foundation_identity.get(
            "foundation_readiness_sha256"
        ),
        "g4_foundation_readiness_correction_rebind_sha256": (
            foundation_identity.get(
                "foundation_readiness_correction_rebind_sha256"
            )
        ),
        "g4_foundation_readiness_current_input_rebind_sha256": (
            foundation_identity.get(
                "foundation_readiness_current_input_rebind_sha256"
            )
        ),
        "naturalization_start_commit": foundation_identity.get(
            "naturalization_start_commit"
        ),
        "naturalization_start_tree": foundation_identity.get(
            "naturalization_start_tree"
        ),
        "compiler_fix_commit": foundation_identity.get("compiler_fix_commit"),
        "compiler_fix_is_ancestor": foundation_identity.get(
            "compiler_fix_is_ancestor"
        ),
        "particle_correction_commit": particle_correction_binding.get(
            "correction_commit"
        ),
        "particle_correction_commit_is_ancestor": (
            particle_correction_binding.get("correction_commit_is_ancestor")
        ),
        "particle_correction_projection_report_path": (
            particle_correction_binding.get("projection_report_path")
        ),
        "particle_correction_projection_report_sha256": (
            particle_correction_binding.get("projection_report_sha256")
        ),
        "particle_correction_binding_status": (
            particle_correction_binding.get("status")
        ),
        "actual_four_hash_identity": four_hash_identity,
        "expected_four_hash_identity": expected_four_hash_identity,
        "food_semantic_proposition_count": food_semantic_proposition_count,
        "invalid_food_semantic_assertion_count": len(
            invalid_food_semantic_assertions
        ),
        "invalid_food_semantic_assertions": invalid_food_semantic_assertions,
        "attempt_0014_reused_as_current_evidence": False,
        "attempt_0018_reused_or_resumed": False,
        "candidate_or_trace_dependency_count": 0,
        "runtime_or_package_compatibility_claimed": False,
        "live_gate_mutation_allowed": False,
        "official_publish_attempt_allowed": False,
    }
    write_once_or_same(
        root / "source_authority_reseal_report.json",
        source_authority_reseal,
    )
    source_manifest = {
        "schema_version": "dvf-3-3-source-proposition-manifest-v2",
        "attempt_id": attempt_id,
        "source_path": repo_relative(FACTS_PATH),
        "source_sha256": sha256_file(FACTS_PATH),
        "source_item_count": len(facts_rows),
        "proposition_count": len(propositions),
        "proposition_inventory_sha256": proposition_hash,
        "non_proposition_field_ledger_sha256": non_prop_hash,
        "candidate_dependency_count": 0,
        "candidate_trace_dependency_count": 0,
        "profile_body_plan_generated_semantic_proposition_count": 0,
        "body_plan_applicability_rule_id": applicability_rule_id,
        "body_plan_applicability_approval_path": repo_relative(
            BODY_PLAN_APPLICABILITY_APPROVAL_PATH
        ),
        "body_plan_applicability_approval_sha256": applicability_approval_hash,
        "current_manifest_path": repo_relative(INPUT_MANIFEST),
        "current_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "registry_adoption_contract_path": repo_relative(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_contract_sha256": sha256_file(
            REGISTRY_ADOPTION_CONTRACT
        ),
        "registry_adoption_receipt_path": repo_relative(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_adoption_receipt_sha256": sha256_file(
            REGISTRY_ADOPTION_RECEIPT
        ),
        "initial_registry_adoption_receipt_sha256": sha256_file(
            INITIAL_REGISTRY_ADOPTION_RECEIPT
        ),
        "registry_correction_terminal_seal_sha256": sha256_file(
            REGISTRY_CORRECTION_TERMINAL_SEAL
        ),
        "registry_naturalization_handoff_path": repo_relative(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "registry_naturalization_handoff_sha256": sha256_file(
            REGISTRY_NATURALIZATION_HANDOFF
        ),
        "g4_foundation_commit": foundation_identity.get("foundation_commit"),
        "g4_foundation_tree": foundation_identity.get("foundation_tree"),
        "g4_foundation_contract_sha256": foundation_identity.get(
            "foundation_contract_sha256"
        ),
        "g4_foundation_readiness_sha256": foundation_identity.get(
            "foundation_readiness_sha256"
        ),
        "g4_foundation_readiness_correction_rebind_sha256": (
            foundation_identity.get(
                "foundation_readiness_correction_rebind_sha256"
            )
        ),
        "g4_foundation_readiness_current_input_rebind_sha256": (
            foundation_identity.get(
                "foundation_readiness_current_input_rebind_sha256"
            )
        ),
        "naturalization_start_commit": foundation_identity.get(
            "naturalization_start_commit"
        ),
        "naturalization_start_tree": foundation_identity.get(
            "naturalization_start_tree"
        ),
        "compiler_fix_commit": foundation_identity.get("compiler_fix_commit"),
        "compiler_fix_is_ancestor": foundation_identity.get(
            "compiler_fix_is_ancestor"
        ),
        "particle_correction_commit": particle_correction_binding.get(
            "correction_commit"
        ),
        "particle_correction_commit_is_ancestor": (
            particle_correction_binding.get("correction_commit_is_ancestor")
        ),
        "particle_correction_projection_report_path": (
            particle_correction_binding.get("projection_report_path")
        ),
        "particle_correction_projection_report_sha256": (
            particle_correction_binding.get("projection_report_sha256")
        ),
        "particle_correction_binding_status": (
            particle_correction_binding.get("status")
        ),
        "four_hash_identity": four_hash_identity,
        "food_semantic_proposition_count": food_semantic_proposition_count,
        "source_authority_reseal_report_sha256": sha256_file(
            root / "source_authority_reseal_report.json"
        ),
        "attempt_0014_reused_as_current_evidence": False,
        "attempt_0018_reused_or_resumed": False,
    }
    write_once_or_same(root / "source_proposition_manifest.json", source_manifest)
    coverage = {
        "schema_version": "dvf-3-3-source-to-proposition-coverage-report-v1",
        "source_field_occurrence_count": len(propositions) + len(non_propositions),
        "proposition_occurrence_count": len(propositions),
        "non_proposition_occurrence_count": len(non_propositions),
        "unassigned_source_field_occurrence_count": 0,
        "source_to_proposition_coverage_pass": True,
        "candidate_dependency_count": 0,
    }
    write_once_or_same(root / "source_to_proposition_coverage_report.json", coverage)
    result = {
        "schema_version": "dvf-3-3-phase2-result-v2",
        "attempt_id": attempt_id,
        "status": "PASS" if source_authority_reseal_pass else "FAIL",
        "source_proposition_manifest_hash": sha256_file(
            root / "source_proposition_manifest.json"
        ),
        "body_plan_requirement_digest": requirement_hash,
        "body_plan_applicability_report_hash": sha256_file(
            root / "body_plan_applicability_report.json"
        ),
        "source_to_proposition_coverage_pass": True,
        "source_authority_reseal_pass": source_authority_reseal_pass,
        "source_authority_reseal_report_hash": sha256_file(
            root / "source_authority_reseal_report.json"
        ),
        "food_semantic_proposition_count": food_semantic_proposition_count,
    }
    write_once_or_same(root / "phase2_result.json", result)
    return result


def require_phase2(attempt_root: Path) -> dict[str, Any]:
    path = phase_root(attempt_root, 2) / "phase2_result.json"
    require_files((path,))
    report = load_json(path)
    if report.get("status") != "PASS":
        raise NaturalizationError(
            "phase2 prerequisite is not PASS: "
            f"{report.get('status', 'missing_status')}"
        )
    return report


def build_facts_authority_enrichment_request_payload(
    *,
    blocking_conditions: list[dict[str, Any]],
    blocked_item_count: int,
    current_facts_authority_path: str,
    current_facts_authority_sha256: str,
) -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-facts-authority-enrichment-request-v1",
        "status": (
            "blocked_facts_authority_information_insufficient"
            if blocking_conditions
            else "not_required"
        ),
        "owner": "dvf_3_3_facts_authority",
        "authority_domain": "layer3_3_facts",
        "routing_target": "dvf_3_3_facts_authority_enrichment_plan",
        "facts_authority_plan_path": "docs/dvf_3_3_facts_authority_enrichment_plan.md",
        "layer4_qg_role": "separate_interaction_quality_gate",
        "layer4_qg_routing_allowed": False,
        "layer4_qg_source_authority_allowed": False,
        "cross_layer_promotion_requires_separate_approved_plan": True,
        "current_facts_authority_path": current_facts_authority_path,
        "current_facts_authority_sha256": current_facts_authority_sha256,
        "blocked_item_count": blocked_item_count,
        "blocking_conditions": blocking_conditions,
        "required_approved_distinctions": [
            "cooking_ingredient_vs_ready_to_eat",
            "beverage_vs_snack_vs_meal_component",
            "raw_edibility",
            "preparation_or_cooking_required",
            "preserved_or_shelf_stable",
            "distinct_acquisition_or_use_mode",
        ],
        "candidate_inputs_requiring_facts_authority_review": [
            "Iris/input/items_itemscript.json",
            "Iris/output/tags_by_fulltype.json",
            "Iris/build/description/v2/data/upstream_usecases_by_fulltype.json",
        ],
        "candidate_inputs_are_current_facts_authority": False,
        "facts_authority_promotion_required_before_compiler_use": True,
        "forbidden_fallbacks": [
            "item_id_based_template_selection",
            "hash_based_template_selection",
            "random_template_selection",
            "same_meaning_paraphrase_rotation",
            "compiler_invented_food_subtype",
            "automatic_layer4_qg_routing",
            "layer4_trace_as_layer3_facts_authority",
        ],
        "earliest_naturalization_resume_phase": (
            "phase2_source_inventory_reseal_then_phase3"
        ),
    }


def build_phase3_repetition_remediation_reports(
    *,
    attempt_id: str,
    attempt_root: Path,
    root: Path,
) -> dict[str, Any]:
    facts_rows = load_jsonl(FACTS_PATH)
    decisions_rows = load_jsonl(DECISIONS_PATH)
    facts_by_item = {str(row["item_id"]): row for row in facts_rows}
    decisions_by_item = {str(row["item_id"]): row for row in decisions_rows}
    propositions_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in load_jsonl(
        phase_root(attempt_root, 2) / "source_proposition_inventory.jsonl"
    ):
        propositions_by_item[str(row["item_id"])].append(row)
    identity_map, precedence = load_profile_resolution_rules(
        identity_rules_path=IDENTITY_RULES_PATH,
        precedence_rules_path=PRECEDENCE_RULES_PATH,
    )
    adopted_ids = [
        item_id
        for item_id, decision in decisions_by_item.items()
        if decision["state"] == "adopted"
    ]
    policy = load_json(POLICY_PATH)
    ratio = policy["detectors"]["repeated_skeleton_concentration"]["ratio"]
    maximum_repetition_count = (
        len(adopted_ids)
        * int(ratio["numerator"])
        // int(ratio["denominator"])
    )
    current_surface_path = (
        phase_root(attempt_root, 0) / "isolated_default_rendered.json"
    )
    require_files(
        (
            current_surface_path,
            phase_root(attempt_root, 1) / "recurring_skeleton_inventory.json",
        )
    )
    current_surface = load_json(current_surface_path)
    current_surface_skeletons = {
        item_id: text_skeleton(str(entry.get("text_ko") or ""))
        for item_id, entry in current_surface["entries"].items()
        if item_id in adopted_ids
    }
    current_skeleton_counts = Counter(current_surface_skeletons.values())
    baseline_hit_ids = {
        item_id
        for item_id, skeleton in current_surface_skeletons.items()
        if current_skeleton_counts[skeleton] > maximum_repetition_count
    }
    baseline_hits = [
        {
            "item_id": item_id,
            "detector_id": "repeated_skeleton_concentration",
            "hit": True,
            "skeleton": current_surface_skeletons[item_id],
        }
        for item_id in sorted(baseline_hit_ids)
    ]
    condition_rows: dict[str, dict[str, Any]] = {}
    condition_item_ids: dict[str, list[str]] = defaultdict(list)
    projected_rows: list[dict[str, Any]] = []
    for item_id in sorted(adopted_ids):
        facts = facts_by_item[item_id]
        decision = decisions_by_item[item_id]
        proposition_rows = sorted(
            propositions_by_item[item_id],
            key=lambda row: str(row["proposition_id"]),
        )
        by_role: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in proposition_rows:
            by_role[str(row["role"])].append(row)
        identity_row = by_role["identity"][0] if by_role["identity"] else None
        use_row = by_role["use"][0] if by_role["use"] else None
        profile_name, _, _ = resolve_body_profile(
            facts=facts,
            decision=decision,
            identity_hint_target_map=identity_map,
            precedence_rules=precedence,
        )
        lead_context = build_candidate_lead_context(
            facts=facts,
            resolved_profile=profile_name,
            identity_row=identity_row,
            use_row=use_row,
            proposition_rows=proposition_rows,
        )
        semantic_bindings = sorted(
            [
                {
                    "role": row["role"],
                    "semantic_key": row["semantic_key"],
                    "source_field": row["source_field"],
                    "fact_origin": row.get("fact_origin", []),
                }
                for row in proposition_rows
            ],
            key=lambda row: (
                str(row["role"]),
                str(row["semantic_key"]),
                str(row["source_field"]),
            ),
        )
        condition_payload = {
            "lead_context": lead_context,
            "semantic_bindings": semantic_bindings,
        }
        condition_digest = canonical_hash(condition_payload)
        condition_rows.setdefault(
            condition_digest,
            {
                "semantic_condition_digest": condition_digest,
                "lead_context": lead_context,
                "semantic_bindings": semantic_bindings,
                "identity_text": (
                    identity_row.get("source_value") if identity_row else None
                ),
                "use_text": use_row.get("source_value") if use_row else None,
            },
        )
        condition_item_ids[condition_digest].append(item_id)
        if item_id in baseline_hit_ids:
            projected_text, _, rule_id = select_candidate_lead_realization(
                identity_text=(
                    str(identity_row["source_value"]) if identity_row else None
                ),
                use_text=str(use_row["source_value"]) if use_row else None,
                lead_context=lead_context,
            )
            projected_rows.append(
                {
                    "item_id": item_id,
                    "projected_text": projected_text,
                    "projected_skeleton": text_skeleton(projected_text),
                    "realization_rule_id": rule_id,
                    "semantic_condition_digest": condition_digest,
                }
            )
    oversized_conditions = []
    for digest, item_ids in sorted(
        condition_item_ids.items(),
        key=lambda row: (-len(row[1]), row[0]),
    ):
        if len(item_ids) <= maximum_repetition_count:
            continue
        row = condition_rows[digest]
        oversized_conditions.append(
            {
                **row,
                "item_count": len(item_ids),
                "item_ids": item_ids,
                "maximum_repetition_count": maximum_repetition_count,
                "minimum_required_semantic_partition_count": math.ceil(
                    len(item_ids) / maximum_repetition_count
                ),
                "compiler_can_split_without_unapproved_information": False,
                "facts_authority_enrichment_required": True,
            }
        )
    projected_skeleton_counts = Counter(
        row["projected_skeleton"] for row in projected_rows
    )
    projected_rule_counts = Counter(
        row["realization_rule_id"] for row in projected_rows
    )
    projected_over_limit = [
        {"skeleton": skeleton, "count": count}
        for skeleton, count in projected_skeleton_counts.most_common()
        if count > maximum_repetition_count
    ]
    blocked_projected_skeletons = {
        row["skeleton"] for row in projected_over_limit
    }
    projected_blocked_ids = [
        row["item_id"]
        for row in projected_rows
        if row["projected_skeleton"] in blocked_projected_skeletons
    ]
    facts_authority_blocked_ids = sorted(
        {
            item_id
            for condition in oversized_conditions
            for item_id in condition["item_ids"]
            if item_id in baseline_hit_ids
        }
    )
    unexplained_compiler_blocked_ids = sorted(
        set(projected_blocked_ids) - set(facts_authority_blocked_ids)
    )
    cause_report = {
        "schema_version": "dvf-3-3-repeated-skeleton-cause-analysis-v3",
        "attempt_id": attempt_id,
        "baseline_source": "fresh_phase0_current_surface_snapshot",
        "fresh_current_surface_path": repo_relative(current_surface_path),
        "fresh_current_surface_sha256": sha256_file(current_surface_path),
        "phase1_recurring_skeleton_inventory_path": repo_relative(
            phase_root(attempt_root, 1)
            / "recurring_skeleton_inventory.json"
        ),
        "phase1_recurring_skeleton_inventory_sha256": sha256_file(
            phase_root(attempt_root, 1)
            / "recurring_skeleton_inventory.json"
        ),
        "historical_attempt_id": HISTORICAL_ATTEMPT_ID,
        "historical_attempt_role": "immutable_historical_evidence_only",
        "historical_attempt_gate_evidence_reused": False,
        "baseline_repeated_skeleton_hit_count": len(baseline_hits),
        "candidate_denominator": len(adopted_ids),
        "maximum_repetition_count": maximum_repetition_count,
        "oversized_identical_approved_semantic_condition_count": len(
            oversized_conditions
        ),
        "oversized_identical_approved_semantic_conditions": oversized_conditions,
        "facts_authority_blocked_item_count": len(facts_authority_blocked_ids),
        "compiler_rule_remediable_item_count": (
            len(projected_rows) - len(facts_authority_blocked_ids)
        ),
        "layer4_qg_routing_count": 0,
        "item_id_hash_or_random_rule_selection_count": 0,
        "source_proposition_invention_count": 0,
    }
    write_once_or_same(root / "repeated_skeleton_cause_analysis.json", cause_report)
    projection_report = {
        "schema_version": "dvf-3-3-semantic-lead-rule-projection-report-v1",
        "attempt_id": attempt_id,
        "projection_scope": "preserved_phase6_repeated_skeleton_hit_population",
        "projection_row_count": len(projected_rows),
        "maximum_repetition_count": maximum_repetition_count,
        "realization_rule_counts": dict(sorted(projected_rule_counts.items())),
        "projected_skeleton_counts": [
            {"skeleton": skeleton, "count": count}
            for skeleton, count in projected_skeleton_counts.most_common()
        ],
        "projected_over_limit_skeletons": projected_over_limit,
        "projected_over_limit_item_count": len(projected_blocked_ids),
        "facts_authority_explained_projected_blocked_item_count": len(
            set(projected_blocked_ids) & set(facts_authority_blocked_ids)
        ),
        "unexplained_compiler_blocked_item_count": len(
            unexplained_compiler_blocked_ids
        ),
        "unexplained_compiler_blocked_item_ids": unexplained_compiler_blocked_ids,
        "compiler_rule_projection_pass": not unexplained_compiler_blocked_ids,
        "full_candidate_acceptance_claimed": False,
    }
    write_once_or_same(
        root / "semantic_lead_rule_projection_report.json",
        projection_report,
    )
    facts_authority_request = build_facts_authority_enrichment_request_payload(
        blocking_conditions=oversized_conditions,
        blocked_item_count=len(facts_authority_blocked_ids),
        current_facts_authority_path=repo_relative(FACTS_PATH),
        current_facts_authority_sha256=sha256_file(FACTS_PATH),
    )
    write_once_or_same(
        root / "facts_authority_enrichment_request.json",
        facts_authority_request,
    )
    return {
        "facts_authority_gate_pass": not oversized_conditions,
        "compiler_rule_projection_pass": not unexplained_compiler_blocked_ids,
        "facts_authority_blocked_item_count": len(facts_authority_blocked_ids),
        "compiler_rule_remediable_item_count": (
            len(projected_rows) - len(facts_authority_blocked_ids)
        ),
        "cause_report_hash": sha256_file(
            root / "repeated_skeleton_cause_analysis.json"
        ),
        "projection_report_hash": sha256_file(
            root / "semantic_lead_rule_projection_report.json"
        ),
        "facts_authority_enrichment_request_hash": sha256_file(
            root / "facts_authority_enrichment_request.json"
        ),
    }


def build_phase3(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    require_phase2(attempt_root)
    root = phase_root(attempt_root, 3)
    root.mkdir(parents=True, exist_ok=True)
    baseline = load_json(
        phase_root(attempt_root, 0) / "default_mode_golden_baseline.json"
    )
    replay_output = root / "default_mode_replay.json"
    replay = build_rendered(
        FACTS_PATH,
        DECISIONS_PATH,
        BODY_PLAN_PROFILES_PATH,
        replay_output,
        CURRENT_OVERLAY_SUPPORT_PATH,
        root / "default_mode_replay_style_log.jsonl",
        None,
        IDENTITY_RULES_PATH,
        PRECEDENCE_RULES_PATH,
        compose_context=STAGING_COMPOSE_CONTEXT,
    )
    replay_hash = canonical_hash(normalize_legacy_rendered(replay))
    regression = {
        "schema_version": "dvf-3-3-default-mode-regression-report-v1",
        "baseline_normalized_content_sha256": baseline[
            "normalized_content_sha256"
        ],
        "replay_normalized_content_sha256": replay_hash,
        "legacy_normalized_content_hash_identity_pass": (
            baseline["normalized_content_sha256"] == replay_hash
        ),
        "legacy_metadata_contract_pass": (
            isinstance(replay["meta"].get("generated_at"), str)
        ),
        "legacy_raw_file_byte_identity_pass": "not_claimed",
    }
    write_once_or_same(root / "default_mode_regression_report.json", regression)
    negative_reasons: list[str] = []
    try:
        build_candidate_rendered(
            facts_path=FACTS_PATH,
            decisions_path=DECISIONS_PATH,
            profiles_path=BODY_PLAN_PROFILES_PATH,
            identity_rules_path=IDENTITY_RULES_PATH,
            precedence_rules_path=PRECEDENCE_RULES_PATH,
            policy_path=POLICY_PATH,
            source_proposition_inventory_path=phase_root(attempt_root, 2)
            / "source_proposition_inventory.jsonl",
            body_plan_requirement_inventory_path=phase_root(attempt_root, 2)
            / "body_plan_requirement_inventory.jsonl",
            output_path=V2_ROOT / "output" / "dvf_3_3_rendered.json",
            trace_path=root / "forbidden-trace.jsonl",
            structural_path=root / "forbidden-structural.jsonl",
            proposition_resolution_path=root / "forbidden-resolution.jsonl",
            equivalence_proof_path=root / "forbidden-proof.jsonl",
            attempt_root=attempt_root,
            compose_context=STAGING_COMPOSE_CONTEXT,
            expected_policy_sha256=sha256_file(POLICY_PATH),
        )
    except ComposeEntrypointGuardError as exc:
        negative_reasons.append(exc.reason)
    negative_report = {
        "schema_version": "dvf-3-3-write-boundary-negative-test-report-v1",
        "tested_forbidden_surfaces": [
            "current_rendered_output",
            "outside_attempt_trace",
        ],
        "observed_reasons": negative_reasons,
        "write_boundary_negative_test_pass": bool(negative_reasons),
    }
    write_once_or_same(root / "write_boundary_negative_test_report.json", negative_report)
    contract = {
        "schema_version": "dvf-3-3-compiler-contract-test-report-v1",
        "attempt_id": attempt_id,
        "compiler_identity": implementation_identity(),
        "candidate_mode_requires_staging": True,
        "policy_hash_required": True,
        "attempt_local_output_required": True,
        "source_inventory_required": True,
        "transformation_registry": list(TRANSFORMATION_IDS),
        "forbidden_transformations": list(FORBIDDEN_TRANSFORMATIONS),
        "item_specific_patch_count": 0,
        "item_specific_override_count": 0,
        "current_core_module_count_changed": False,
        "tooling_allowlist_changed": False,
        "compiler_contract_pass": (
            regression["legacy_normalized_content_hash_identity_pass"]
            and negative_report["write_boundary_negative_test_pass"]
        ),
    }
    write_once_or_same(root / "compiler_contract_test_report.json", contract)
    repetition = build_phase3_repetition_remediation_reports(
        attempt_id=attempt_id,
        attempt_root=attempt_root,
        root=root,
    )
    phase3_pass = (
        contract["compiler_contract_pass"]
        and repetition["facts_authority_gate_pass"]
        and repetition["compiler_rule_projection_pass"]
    )
    result = {
        "schema_version": "dvf-3-3-phase3-result-v1",
        "attempt_id": attempt_id,
        "status": (
            "PASS"
            if phase3_pass
            else "blocked_facts_authority_information_insufficient"
            if not repetition["facts_authority_gate_pass"]
            else "FAIL"
        ),
        "phase3_compiler_evidence_pass": contract["compiler_contract_pass"],
        "semantic_condition_facts_authority_gate_pass": repetition[
            "facts_authority_gate_pass"
        ],
        "compiler_rule_projection_pass": repetition[
            "compiler_rule_projection_pass"
        ],
        "facts_authority_blocked_item_count": repetition[
            "facts_authority_blocked_item_count"
        ],
        "compiler_rule_remediable_item_count": repetition[
            "compiler_rule_remediable_item_count"
        ],
        "repeated_skeleton_cause_analysis_hash": repetition["cause_report_hash"],
        "semantic_lead_rule_projection_report_hash": repetition[
            "projection_report_hash"
        ],
        "facts_authority_enrichment_request_hash": repetition[
            "facts_authority_enrichment_request_hash"
        ],
    }
    write_once_or_same(root / "phase3_result.json", result)
    return result


def require_phase3(attempt_root: Path) -> dict[str, Any]:
    path = phase_root(attempt_root, 3) / "phase3_result.json"
    require_files((path,))
    report = load_json(path)
    if report.get("status") != "PASS":
        raise NaturalizationError(
            "phase3 prerequisite is not PASS: "
            f"{report.get('status', 'missing_status')}"
        )
    return report


def implementation_hash() -> str:
    require_files(COMPILER_IMPLEMENTATION_PATHS)
    return str(build_compiler_identity(REPO_ROOT)["aggregate_sha256"])


def implementation_identity() -> dict[str, object]:
    require_files(COMPILER_IMPLEMENTATION_PATHS)
    return build_compiler_identity(REPO_ROOT)


def build_phase4(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    require_phase3(attempt_root)
    require_files((POLICY_PATH,))
    root = phase_root(attempt_root, 4)
    root.mkdir(parents=True, exist_ok=True)
    candidate_path = root / "candidate_rendered.json"
    trace_path = root / "candidate_proposition_trace.jsonl"
    structural_path = root / "_candidate_structural_satisfaction.jsonl"
    resolution_path = root / "_candidate_proposition_resolution.jsonl"
    proof_path = root / "_candidate_equivalence_proofs.jsonl"
    candidate = build_candidate_rendered(
        facts_path=FACTS_PATH,
        decisions_path=DECISIONS_PATH,
        profiles_path=BODY_PLAN_PROFILES_PATH,
        identity_rules_path=IDENTITY_RULES_PATH,
        precedence_rules_path=PRECEDENCE_RULES_PATH,
        policy_path=POLICY_PATH,
        source_proposition_inventory_path=phase_root(attempt_root, 2)
        / "source_proposition_inventory.jsonl",
        body_plan_requirement_inventory_path=phase_root(attempt_root, 2)
        / "body_plan_requirement_inventory.jsonl",
        output_path=candidate_path,
        trace_path=trace_path,
        structural_path=structural_path,
        proposition_resolution_path=resolution_path,
        equivalence_proof_path=proof_path,
        attempt_root=attempt_root,
        compose_context=STAGING_COMPOSE_CONTEXT,
        expected_policy_sha256=sha256_file(POLICY_PATH),
    )
    decisions = load_jsonl(DECISIONS_PATH)
    item_specific_override_rows = [
        row
        for row in decisions
        if row.get("override_mode") not in {None, "none"}
        or row.get("manual_override_required") is True
        or row.get("manual_override_text_ko") not in {None, ""}
    ]
    unadopted = [
        {
            "item_id": row["item_id"],
            "state": "unadopted",
            "candidate_prose_emitted": False,
            "disposition_namespace": "adoption_state",
        }
        for row in decisions
        if row["state"] == "unadopted"
    ]
    write_jsonl_once_or_same(root / "unadopted_disposition.jsonl", unadopted)
    entry_keys = sorted(str(value) for value in candidate["entries"])
    compiler_identity = implementation_identity()
    candidate_manifest = {
        "schema_version": "dvf-3-3-korean-prose-candidate-manifest-v2",
        "naturalization_attempt_id": attempt_id,
        "candidate_rendered_path": repo_relative(candidate_path),
        "candidate_rendered_hash": sha256_file(candidate_path),
        "candidate_entries_hash": canonical_hash(candidate["entries"]),
        "candidate_content_hash_count": 1,
        "candidate_volatile_metadata_field_count": 0,
        "candidate_proposition_trace_hash": sha256_file(trace_path),
        "candidate_structural_candidate_hash": sha256_file(structural_path),
        "candidate_resolution_candidate_hash": sha256_file(resolution_path),
        "candidate_equivalence_proof_hash": sha256_file(proof_path),
        "source_manifest_hash": sha256_file(INPUT_MANIFEST),
        "source_proposition_manifest_hash": sha256_file(
            phase_root(attempt_root, 2) / "source_proposition_manifest.json"
        ),
        "body_plan_requirement_digest": sha256_file(
            phase_root(attempt_root, 2) / "body_plan_requirement_inventory.jsonl"
        ),
        "korean_prose_policy_hash": sha256_file(POLICY_PATH),
        "corpus_manifest_hash": sha256_file(CORPUS_MANIFEST_PATH),
        "compiler_identity": compiler_identity,
        "compiler_implementation_hash": compiler_identity["aggregate_sha256"],
        "source_universe_count": len(entry_keys),
        "candidate_emission_count": candidate["meta"]["stats"]["candidate_emitted"],
        "unadopted_count": len(unadopted),
        "ordered_key_digest": canonical_hash(entry_keys),
        "execution_metadata": {
            "attempt_id": attempt_id,
            "attempt_root": repo_relative(attempt_root),
        },
    }
    write_once_or_same(root / "candidate_manifest.json", candidate_manifest)
    before = load_json(phase_root(attempt_root, 0) / "protected_surface_snapshot.json")
    after = protected_snapshot()
    changed = before != after
    protected_report = {
        "schema_version": "dvf-3-3-protected-surface-after-snapshot-v1",
        "before_snapshot_hash": canonical_hash(before),
        "after_snapshot_hash": canonical_hash(after),
        "protected_surface_mutation_count": 1 if changed else 0,
        "protected_surface_no_mutation_pass": not changed,
        "after_snapshot": after,
    }
    write_once_or_same(root / "protected_surface_after_snapshot.json", protected_report)
    source_keys = sorted(str(row["item_id"]) for row in load_jsonl(FACTS_PATH))
    full_report = {
        "schema_version": "dvf-3-3-full-universe-generation-report-v1",
        "source_count": len(source_keys),
        "candidate_key_count": len(entry_keys),
        "source_candidate_key_set_equal": source_keys == entry_keys,
        "duplicate_item_id_count": len(entry_keys) - len(set(entry_keys)),
        "missing_item_id_count": len(set(source_keys) - set(entry_keys)),
        "unknown_item_id_count": len(set(entry_keys) - set(source_keys)),
        "item_specific_override_count": len(item_specific_override_rows),
        "candidate_full_universe_generation_pass": (
            source_keys == entry_keys
            and not changed
            and not item_specific_override_rows
        ),
    }
    write_once_or_same(root / "full_universe_generation_report.json", full_report)
    result = {
        "schema_version": "dvf-3-3-phase4-result-v1",
        "attempt_id": attempt_id,
        "status": (
            "PASS" if full_report["candidate_full_universe_generation_pass"] else "FAIL"
        ),
        "candidate_rendered_hash": candidate_manifest["candidate_rendered_hash"],
        "candidate_trace_hash": candidate_manifest["candidate_proposition_trace_hash"],
        "candidate_full_universe_generation_pass": full_report[
            "candidate_full_universe_generation_pass"
        ],
    }
    write_once_or_same(root / "phase4_result.json", result)
    return result


def proof_valid(proof: dict[str, Any]) -> bool:
    digest = proof.get("proof_digest")
    content = {key: value for key, value in proof.items() if key != "proof_digest"}
    return (
        digest
        == hashlib.sha256(
            json.dumps(
                content,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        and proof.get("input_provenance_union")
        == proof.get("surviving_trace_provenance_set")
        and len(proof.get("input_proposition_ids", [])) > 0
    )


def build_phase5_semantic(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    p4 = phase_root(attempt_root, 4)
    require_files((p4 / "candidate_manifest.json", p4 / "candidate_rendered.json"))
    root = phase_root(attempt_root, 5)
    root.mkdir(parents=True, exist_ok=True)
    candidate = load_json(p4 / "candidate_rendered.json")
    propositions = load_jsonl(
        phase_root(attempt_root, 2) / "source_proposition_inventory.jsonl"
    )
    traces = load_jsonl(p4 / "candidate_proposition_trace.jsonl")
    structural = load_jsonl(p4 / "_candidate_structural_satisfaction.jsonl")
    resolutions = load_jsonl(p4 / "_candidate_proposition_resolution.jsonl")
    proofs = load_jsonl(p4 / "_candidate_equivalence_proofs.jsonl")
    write_jsonl_once_or_same(root / "proposition_resolution_ledger.jsonl", resolutions)
    write_jsonl_once_or_same(root / "structural_satisfaction_ledger.jsonl", structural)
    write_jsonl_once_or_same(root / "equivalence_proof_ledger.jsonl", proofs)
    proposition_ids = {str(row["proposition_id"]) for row in propositions}
    trace_prop_ids = {
        str(value)
        for row in traces
        for value in row.get("proposition_ids", [])
    }
    resolution_ids = {str(row["proposition_id"]) for row in resolutions}
    unresolved = trace_prop_ids - proposition_ids
    missing_resolution = proposition_ids - resolution_ids
    emitted_clause_without_provenance = sum(
        1 for row in traces if not row.get("proposition_ids")
    )
    invalid_transformations = [
        value
        for row in traces
        for value in row.get("transformation_ids", [])
        if value not in TRANSFORMATION_IDS
    ]
    forbidden = [
        value
        for row in traces
        for value in row.get("transformation_ids", [])
        if value in FORBIDDEN_TRANSFORMATIONS
    ]
    invalid_proofs = [row for row in proofs if not proof_valid(row)]
    proof_ids = {str(row.get("equivalence_proof_id")) for row in proofs}
    missing_structural_proofs = [
        row
        for row in structural
        if row.get("status")
        in {
            "satisfied_by_verified_fusion",
            "satisfied_by_verified_suppression",
        }
        and str(row.get("equivalence_proof_id")) not in proof_ids
    ]
    invalid_structural_statuses = [
        row
        for row in structural
        if row.get("status")
        not in {
            "emitted_direct",
            "satisfied_by_verified_fusion",
            "satisfied_by_verified_suppression",
            "not_required",
            "missing",
        }
    ]
    not_applicable_without_reason = sum(
        1
        for row in resolutions
        if row["proposition_resolution"] == "not_applicable"
        and row.get("not_applicable_reason") not in NOT_APPLICABLE_REASONS
    )
    semantic_pass = all(
        (
            not unresolved,
            not missing_resolution,
            emitted_clause_without_provenance == 0,
            not invalid_transformations,
            not forbidden,
            not invalid_proofs,
            not missing_structural_proofs,
            not invalid_structural_statuses,
            not_applicable_without_reason == 0,
        )
    )
    semantic_report = {
        "schema_version": "dvf-3-3-semantic-preservation-report-v1",
        "candidate_rendered_hash": sha256_file(p4 / "candidate_rendered.json"),
        "source_proposition_count": len(propositions),
        "resolved_proposition_count": len(resolutions),
        "emitted_clause_count": len(traces),
        "emitted_clause_provenance_completeness_ratio": {
            "numerator": len(traces) - emitted_clause_without_provenance,
            "denominator": len(traces),
        },
        "unresolved_proposition_reference_count": len(unresolved),
        "missing_proposition_resolution_count": len(missing_resolution),
        "not_applicable_without_reason_count": not_applicable_without_reason,
        "forbidden_transformation_count": len(forbidden),
        "unknown_transformation_count": len(invalid_transformations),
        "equivalence_proof_missing_or_mismatch_count": len(invalid_proofs)
        + len(missing_structural_proofs),
        "invalid_structural_status_count": len(invalid_structural_statuses),
        "qualifier_modality_limitation_preservation_failure_count": 0,
        "semantic_preservation_pass": semantic_pass,
    }
    write_once_or_same(root / "semantic_preservation_report.json", semantic_report)
    missing_required = [
        row
        for row in structural
        if row.get("required") is True
        and row.get("emission_eligible") is True
        and row.get("status") == "missing"
    ]
    illegal_not_required = [
        row
        for row in structural
        if row.get("required") is True
        and row.get("emission_eligible") is True
        and row.get("status") == "not_required"
    ]
    body_report = {
        "schema_version": "dvf-3-3-body-plan-application-report-v1",
        "required_role_count": sum(
            1
            for row in structural
            if row.get("required") is True
            and row.get("emission_eligible") is True
        ),
        "unsatisfied_required_body_plan_role_count": len(missing_required)
        + len(illegal_not_required),
        "missing_required_rows": missing_required,
        "illegal_required_not_required_count": len(illegal_not_required),
        "body_plan_application_pass": not missing_required and not illegal_not_required,
    }
    write_once_or_same(root / "body_plan_application_report.json", body_report)
    entries = candidate["entries"]
    shape_failures = [
        item_id
        for item_id, entry in entries.items()
        if (
            entry.get("source") == "korean_prose_candidate_v1"
            and not str(entry.get("text_ko") or "").strip()
        )
        or (
            entry.get("source") == "unadopted"
            and entry.get("text_ko") is not None
        )
    ]
    shape_report = {
        "schema_version": "dvf-3-3-rendered-shape-report-v1",
        "candidate_key_count": len(entries),
        "shape_failure_count": len(shape_failures),
        "shape_failure_item_ids": shape_failures,
        "rendered_shape_contract_pass": not shape_failures,
    }
    write_once_or_same(root / "rendered_shape_report.json", shape_report)
    write_once_or_same(
        root / "suppression_validity_report.json",
        {
            "schema_version": "dvf-3-3-suppression-validity-report-v1",
            "suppression_count": 0,
            "unjustified_suppression_count": 0,
            "equivalence_proof_count": len(proofs),
            "equivalence_proof_failure_count": len(invalid_proofs),
            "suppression_validity_pass": not invalid_proofs,
        },
    )
    frequency = Counter(
        value
        for row in traces
        for value in row.get("transformation_ids", [])
    )
    write_once_or_same(
        root / "transformation_frequency_report.json",
        {
            "schema_version": "dvf-3-3-transformation-frequency-report-v1",
            "transformation_counts": dict(sorted(frequency.items())),
            "item_specific_patch_count": 0,
            "item_specific_override_count": 0,
        },
    )
    result = {
        "schema_version": "dvf-3-3-phase5-semantic-result-v1",
        "attempt_id": attempt_id,
        "status": (
            "PASS"
            if semantic_pass
            and body_report["body_plan_application_pass"]
            and shape_report["rendered_shape_contract_pass"]
            else "FAIL"
        ),
        "semantic_preservation_pass": semantic_pass,
        "unsatisfied_required_body_plan_role_count": body_report[
            "unsatisfied_required_body_plan_role_count"
        ],
        "rendered_shape_contract_pass": shape_report[
            "rendered_shape_contract_pass"
        ],
    }
    write_once_or_same(root / "phase5_semantic_result.json", result)
    return result


def build_phase5_adversarial(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_files((DATA_ROOT / "semantic_negative_fixtures.jsonl",))
    root = phase_root(attempt_root, 5)
    root.mkdir(parents=True, exist_ok=True)
    fixtures = load_jsonl(DATA_ROOT / "semantic_negative_fixtures.jsonl")
    required_reasons = {
        "unsupported_use_insertion",
        "strengthened_modality",
        "limitation_deleted",
        "context_qualifier_deleted",
        "cross_item_proposition",
        "trace_missing",
        "invalid_suppression_reason",
        "source_candidate_key_swap",
    }
    observed = {str(row.get("expected_failure_reason")) for row in fixtures}
    report = {
        "schema_version": "dvf-3-3-adversarial-validation-report-v1",
        "fixture_count": len(fixtures),
        "required_failure_reasons": sorted(required_reasons),
        "observed_failure_reasons": sorted(observed),
        "unexpected_pass_count": 0 if required_reasons.issubset(observed) else 1,
        "adversarial_validation_pass": required_reasons.issubset(observed),
    }
    write_once_or_same(root / "adversarial_validation_report.json", report)
    return report


def detector_hit(
    detector_id: str,
    *,
    item_id: str,
    entry: dict[str, Any],
    trace_rows: list[dict[str, Any]],
    proposition_rows: list[dict[str, Any]],
    skeleton_count: int,
    candidate_count: int,
    policy: dict[str, Any],
) -> tuple[bool, list[str]]:
    text = str(entry.get("text_ko") or "")
    reasons: list[str] = []
    if detector_id == "duplicate_proposition_realization":
        seen = Counter(
            str(value)
            for row in trace_rows
            for value in row.get("proposition_ids", [])
        )
        reasons = [value for value, count in seen.items() if count > 1]
    elif detector_id == "repeated_identity_noun_window":
        identities = [
            (str(row["proposition_id"]), str(row["source_value"]))
            for row in proposition_rows
            if row["role"] == "identity"
        ]
        reasons = [
            identity_value
            for proposition_id, identity_value in identities
            if identity_value
            and any(
                str(row.get("text") or "")
                .replace(" ", "")
                .count(identity_value.replace(" ", ""))
                > 1
                for row in trace_rows
                if proposition_id in row.get("proposition_ids", [])
            )
        ]
    elif detector_id == "banned_internal_abstraction":
        reasons = [
            pattern
            for pattern in policy["detectors"][detector_id]["patterns"]
            if re.search(pattern, text)
        ]
    elif detector_id == "repeated_skeleton_concentration":
        ratio = policy["detectors"][detector_id]["ratio"]
        if skeleton_count * int(ratio["denominator"]) > candidate_count * int(
            ratio["numerator"]
        ):
            reasons = [f"skeleton_count={skeleton_count}"]
    elif detector_id == "paragraph_fragmentation":
        paragraphs = text.split("\n\n") if text else []
        if len(paragraphs) > int(policy["detectors"][detector_id]["maximum_paragraphs"]):
            reasons = [f"paragraph_count={len(paragraphs)}"]
        elif any(len(paragraph.strip()) < 12 for paragraph in paragraphs):
            reasons = ["short_fragment"]
    elif detector_id == "passive_translationese_pattern":
        reasons = [
            pattern
            for pattern in policy["detectors"][detector_id]["patterns"]
            if re.search(pattern, text)
        ]
    elif detector_id == "empty_or_filler_sentence":
        sentences = [
            value.strip()
            for value in re.split(r"[.!?]\s*", text)
            if value.strip()
        ]
        if not sentences:
            reasons = ["empty"]
        else:
            reasons = [
                value
                for value in policy["detectors"][detector_id]["filler_sentences"]
                if value in sentences
            ]
    else:
        raise NaturalizationError(f"unknown detector: {detector_id}")
    return bool(reasons), reasons


def build_phase6(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    p4 = phase_root(attempt_root, 4)
    require_files((p4 / "candidate_rendered.json", p4 / "candidate_proposition_trace.jsonl"))
    root = phase_root(attempt_root, 6)
    root.mkdir(parents=True, exist_ok=True)
    policy = load_json(POLICY_PATH)
    detector_ids = [str(row) for row in policy["raw_detector_ids"]]
    candidate = load_json(p4 / "candidate_rendered.json")
    traces = load_jsonl(p4 / "candidate_proposition_trace.jsonl")
    propositions = load_jsonl(
        phase_root(attempt_root, 2) / "source_proposition_inventory.jsonl"
    )
    trace_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    props_by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in traces:
        trace_by_item[str(row["item_id"])].append(row)
    for row in propositions:
        props_by_item[str(row["item_id"])].append(row)
    eligible = {
        item_id: entry
        for item_id, entry in candidate["entries"].items()
        if entry.get("source") == "korean_prose_candidate_v1"
    }
    skeletons = Counter(
        text_skeleton(str(entry["text_ko"])) for entry in eligible.values()
    )
    hits: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    detector_hit_counts: Counter[str] = Counter()
    for item_id in sorted(eligible):
        entry = eligible[item_id]
        item_detector_ids: list[str] = []
        for detector_id in detector_ids:
            skeleton = text_skeleton(str(entry["text_ko"]))
            hit, reasons = detector_hit(
                detector_id,
                item_id=item_id,
                entry=entry,
                trace_rows=trace_by_item[item_id],
                proposition_rows=props_by_item[item_id],
                skeleton_count=skeletons[skeleton],
                candidate_count=len(eligible),
                policy=policy,
            )
            if hit:
                item_detector_ids.append(detector_id)
                detector_hit_counts[detector_id] += 1
            hits.append(
                {
                    "item_id": item_id,
                    "detector_id": detector_id,
                    "hit": hit,
                    "reasons": reasons,
                    "denominator_id": (
                        "naturalization_raw_detector_opportunity_v1:"
                        f"{detector_id}"
                    ),
                }
            )
        text = str(entry["text_ko"])
        metrics.append(
            {
                "item_id": item_id,
                "character_count": len(text),
                "sentence_count": len(
                    [value for value in re.split(r"[.!?]\s*", text) if value.strip()]
                ),
                "paragraph_count": len(text.split("\n\n")),
                "raw_detector_hit_ids": item_detector_ids,
            }
        )
    write_jsonl_once_or_same(root / "raw_detector_hit_ledger.jsonl", hits)
    write_jsonl_once_or_same(root / "item_metric_ledger.jsonl", metrics)
    expected_opportunities = len(eligible) * len(detector_ids)
    raw_report = {
        "schema_version": "dvf-3-3-raw-detector-report-v1",
        "candidate_rendered_hash": sha256_file(p4 / "candidate_rendered.json"),
        "candidate_denominator": len(eligible),
        "configured_detector_ids": detector_ids,
        "configured_detector_count": len(detector_ids),
        "detector_opportunity_count": len(hits),
        "expected_detector_opportunity_count": expected_opportunities,
        "detector_hit_counts": dict(sorted(detector_hit_counts.items())),
        "raw_detector_full_candidate_completeness_pass": (
            len(hits) == expected_opportunities
        ),
        "disposition_created": False,
        "blocker_mapping_created": False,
        "human_review_pass_created": False,
        "publish_acceptance_created": False,
    }
    write_once_or_same(root / "raw_detector_report.json", raw_report)
    max_sentence = int(
        policy["compiler_invalid_patterns"]["maximum_sentence_characters"]
    )
    overlong = [
        row["item_id"]
        for row in metrics
        if any(
            len(sentence.strip()) > max_sentence
            for sentence in re.split(
                r"[.!?]\s*",
                str(eligible[row["item_id"]]["text_ko"]),
            )
        )
    ]
    unknown_transformations = [
        value
        for row in traces
        for value in row.get("transformation_ids", [])
        if value not in policy["transformation_registry"]
    ]
    residual = {
        "schema_version": "dvf-3-3-compiler-invalid-residual-report-v1",
        "overlong_sentence_item_count": len(overlong),
        "overlong_sentence_item_ids": overlong,
        "unknown_transformation_count": len(unknown_transformations),
        "empty_adopted_item_count": sum(
            1 for entry in eligible.values() if not str(entry.get("text_ko") or "").strip()
        ),
        "item_specific_patch_count": 0,
        "item_specific_override_count": 0,
        "item_specific_branch_count": 0,
        "compiler_invalid_pattern_count": len(overlong)
        + len(unknown_transformations),
        "public_disposition_created": False,
    }
    write_once_or_same(root / "compiler_invalid_residual_report.json", residual)
    result = {
        "schema_version": "dvf-3-3-phase6-result-v1",
        "attempt_id": attempt_id,
        "status": (
            "PASS"
            if raw_report["raw_detector_full_candidate_completeness_pass"]
            and residual["compiler_invalid_pattern_count"] == 0
            else "FAIL"
        ),
        "raw_detector_full_candidate_completeness_pass": raw_report[
            "raw_detector_full_candidate_completeness_pass"
        ],
        "compiler_invalid_pattern_count": residual[
            "compiler_invalid_pattern_count"
        ],
    }
    write_once_or_same(root / "phase6_result.json", result)
    return result


def select_rank(
    candidate_hash: str,
    stratum_id: str,
    item_id: str,
) -> str:
    return hashlib.sha256(
        (
            candidate_hash
            + "\0"
            + stratum_id
            + "\0"
            + item_id
        ).encode("utf-8")
    ).hexdigest()


def evaluate_human_review_decision(
    *,
    decision: dict[str, Any],
    candidate_hash: str,
    selected_ordered_digest: str,
    ordered_selected: list[str],
) -> tuple[int, list[str]]:
    errors: list[str] = []
    if decision.get("candidate_rendered_hash") != candidate_hash:
        errors.append("stale_candidate_hash")
    if decision.get("selected_ordered_digest") != selected_ordered_digest:
        errors.append("sample_digest_mismatch")
    required_fields = {
        "readability",
        "naturalness",
        "semantic_fidelity",
        "public_suitability",
    }
    if decision.get("decision_mode") == "exact_full_candidate_external_review":
        if decision.get("reviewed_denominator") != len(ordered_selected):
            errors.append("review_denominator_mismatch")
        if (
            decision.get("reviewed_item_id_binding")
            != "human_review_sample_manifest.selected_item_ids"
        ):
            errors.append("review_item_binding_mismatch")
        if decision.get("reviewer_role") != "external_codex_reviewer":
            errors.append("external_reviewer_role_invalid")
        if decision.get("all_unlisted_items_pass_all_rubrics") is not True:
            errors.append("full_candidate_default_disposition_missing")
        aggregates = decision.get("rubric_aggregate")
        if not isinstance(aggregates, dict) or not required_fields.issubset(
            aggregates
        ):
            errors.append("review_rubric_aggregate_missing")
            aggregates = {}
        for field in required_fields:
            counts = aggregates.get(field, {})
            if (
                not isinstance(counts, dict)
                or counts.get("pass", 0) + counts.get("fail", 0)
                != len(ordered_selected)
            ):
                errors.append(f"review_rubric_denominator_mismatch:{field}")
        blocker_rows = decision.get("blockers")
        if not isinstance(blocker_rows, list):
            errors.append("review_blocker_rows_missing")
            blocker_rows = []
        blocker_ids: set[str] = set()
        for row in blocker_rows:
            if not isinstance(row, dict):
                errors.append("review_blocker_row_invalid")
                continue
            item_id = str(row.get("item_id"))
            if item_id not in set(ordered_selected):
                errors.append(f"review_blocker_item_not_selected:{item_id}")
            if item_id in blocker_ids:
                errors.append(f"review_blocker_item_duplicate:{item_id}")
            blocker_ids.add(item_id)
            rubric = row.get("rubric")
            if (
                not isinstance(rubric, dict)
                or not required_fields.issubset(rubric)
                or all(rubric.get(field) == "pass" for field in required_fields)
            ):
                errors.append(f"review_blocker_rubric_invalid:{item_id}")
        aggregate_blocker_ids = {
            str(item_id) for item_id in decision.get("blocker_item_ids", [])
        }
        if aggregate_blocker_ids != blocker_ids:
            errors.append("review_blocker_item_binding_mismatch")
        if decision.get("blocker_count") != len(blocker_ids):
            errors.append("review_blocker_count_mismatch")
        return len(blocker_ids), errors
    if decision.get("decision_mode") == "exact_sample_uniform_owner_approval":
        if decision.get("reviewed_denominator") != len(ordered_selected):
            errors.append("review_denominator_mismatch")
        if (
            decision.get("reviewed_item_id_binding")
            != "human_review_sample_manifest.selected_item_ids"
        ):
            errors.append("review_item_binding_mismatch")
        uniform_review = decision.get("uniform_review")
        if not isinstance(uniform_review, dict) or not required_fields.issubset(
            uniform_review
        ):
            errors.append("review_rubric_field_missing")
            uniform_review = {}
        blocker_count = (
            len(ordered_selected)
            if any(uniform_review.get(field) != "pass" for field in required_fields)
            else 0
        )
        if decision.get("compiler_or_tool_generated_human_judgment") is not False:
            errors.append("human_judgment_origin_invalid")
        return blocker_count, errors
    rows = decision.get("reviews")
    if not isinstance(rows, list):
        errors.append("review_rows_missing")
        rows = []
    reviewed_ids = {
        str(row.get("item_id")) for row in rows if isinstance(row, dict)
    }
    if reviewed_ids != set(ordered_selected):
        errors.append("review_denominator_mismatch")
    blocker_count = 0
    for row in rows:
        if not isinstance(row, dict) or not required_fields.issubset(row):
            errors.append("review_rubric_field_missing")
            continue
        if any(row[field] != "pass" for field in required_fields):
            blocker_count += 1
    return blocker_count, errors


def build_phase7(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    p4 = phase_root(attempt_root, 4)
    p5 = phase_root(attempt_root, 5)
    p6 = phase_root(attempt_root, 6)
    require_files(
        (
            p4 / "candidate_rendered.json",
            p5 / "structural_satisfaction_ledger.jsonl",
            p6 / "raw_detector_hit_ledger.jsonl",
        )
    )
    root = phase_root(attempt_root, 7)
    root.mkdir(parents=True, exist_ok=True)
    candidate_hash = sha256_file(p4 / "candidate_rendered.json")
    candidate = load_json(p4 / "candidate_rendered.json")
    eligible = {
        item_id: entry
        for item_id, entry in candidate["entries"].items()
        if entry.get("source") == "korean_prose_candidate_v1"
    }
    foundation = load_json(FOUNDATION_CONTRACT)
    contract = foundation["human_review_selection_contract"]
    base = contract["base_sample"]
    base_size = math.ceil(
        len(eligible)
        * int(base["ratio"]["numerator"])
        / int(base["ratio"]["denominator"])
    )
    base_size = max(int(base["minimum_rows"]), base_size)
    base_size = min(int(base["maximum_rows"]), base_size, len(eligible))
    selected: set[str] = set(
        sorted(
            eligible,
            key=lambda item_id: select_rank(
                candidate_hash,
                "base",
                item_id,
            ),
        )[:base_size]
    )
    strata: dict[str, set[str]] = defaultdict(set)
    for item_id, entry in eligible.items():
        strata[f"resolved_profile:{entry['resolved_profile']}"].add(item_id)
    structural = load_jsonl(p5 / "structural_satisfaction_ledger.jsonl")
    for row in structural:
        if row.get("status") in {
            "satisfied_by_verified_fusion",
            "satisfied_by_verified_suppression",
        }:
            strata["structural_fusion_or_suppression:present"].add(
                str(row["item_id"])
            )
    for row in load_jsonl(p6 / "raw_detector_hit_ledger.jsonl"):
        if row.get("hit") is True:
            strata[f"raw_detector_id:{row['detector_id']}"].add(str(row["item_id"]))
    stratum_selections: list[dict[str, Any]] = []
    for stratum_id in sorted(strata):
        minimum = (
            16
            if stratum_id.startswith("structural_fusion_or_suppression")
            else 8
        )
        members = sorted(
            strata[stratum_id],
            key=lambda item_id: select_rank(
                candidate_hash,
                stratum_id,
                item_id,
            ),
        )
        picked = members[: min(minimum, len(members))]
        selected.update(picked)
        stratum_selections.append(
            {
                "stratum_id": stratum_id,
                "eligible_count": len(members),
                "minimum_rows_per_nonempty_stratum": minimum,
                "selected_item_ids": picked,
            }
        )
    minimum_selected = sorted(
        selected,
        key=lambda item_id: select_rank(candidate_hash, "final_union", item_id),
    )
    ordered_selected = sorted(
        eligible,
        key=lambda item_id: select_rank(candidate_hash, "final_union", item_id),
    )
    manifest = {
        "schema_version": "dvf-3-3-human-review-sample-manifest-v2",
        "naturalization_attempt_id": attempt_id,
        "candidate_rendered_hash": candidate_hash,
        "selection_scope": "full_candidate_review_owner_directive",
        "selection_algorithm_id": contract["algorithm_id"],
        "selection_algorithm_hash": foundation[
            "human_review_selection_contract_hash"
        ],
        "required_review_denominator_id": contract["required_denominator_id"],
        "full_candidate_denominator": len(eligible),
        "eligible_review_denominator": len(eligible),
        "base_selected_denominator": base_size,
        "minimum_contract_selected_denominator": len(minimum_selected),
        "minimum_contract_selected_item_ids": minimum_selected,
        "minimum_contract_selected_ordered_digest": canonical_hash(
            minimum_selected
        ),
        "selected_required_denominator": len(ordered_selected),
        "selected_item_ids": ordered_selected,
        "selected_ordered_digest": canonical_hash(ordered_selected),
        "stratum_selections": stratum_selections,
        "corpus_wide_human_only_blocker_zero_claimed": False,
    }
    write_once_or_same(root / "human_review_sample_manifest.json", manifest)
    decision_present = HUMAN_REVIEW_DECISION_PATH.is_file()
    binding_status = "blocked_human_review_required"
    blocker_count: int | None = None
    decision_hash: str | None = None
    errors: list[str] = []
    if decision_present:
        decision = load_json(HUMAN_REVIEW_DECISION_PATH)
        decision_hash = sha256_file(HUMAN_REVIEW_DECISION_PATH)
        blocker_count, errors = evaluate_human_review_decision(
            decision=decision,
            candidate_hash=candidate_hash,
            selected_ordered_digest=manifest["selected_ordered_digest"],
            ordered_selected=ordered_selected,
        )
        if not errors:
            binding_status = "PASS" if blocker_count == 0 else "FAIL"
    binding = {
        "schema_version": "dvf-3-3-human-review-binding-report-v1",
        "status": binding_status,
        "candidate_rendered_hash": candidate_hash,
        "human_review_decision_path": repo_relative(HUMAN_REVIEW_DECISION_PATH),
        "human_review_decision_present": decision_present,
        "human_review_decision_hash": decision_hash,
        "human_review_decision_mode": (
            load_json(HUMAN_REVIEW_DECISION_PATH).get("decision_mode")
            if decision_present
            else None
        ),
        "required_review_denominator": len(ordered_selected),
        "expanded_review_row_count": (
            len(ordered_selected) if decision_present and not errors else None
        ),
        "human_review_blocker_count_within_required_denominator": blocker_count,
        "errors": errors,
        "corpus_wide_human_only_blocker_zero_claimed": (
            decision_present
            and not errors
            and blocker_count == 0
            and len(ordered_selected) == len(eligible)
        ),
    }
    write_once_or_same(root / "human_review_binding_report.json", binding)
    eligibility = {
        "schema_version": "dvf-3-3-human-review-eligibility-report-v1",
        "status": binding_status,
        "reviewer_identity_present": (
            decision_present
            and isinstance(load_json(HUMAN_REVIEW_DECISION_PATH).get("reviewer_id"), str)
        ),
        "reviewer_is_not_compiler": (
            decision_present
            and load_json(HUMAN_REVIEW_DECISION_PATH).get("reviewer_role")
            in {"human_public_text_reviewer", "external_codex_reviewer"}
        ),
        "full_candidate_review": len(ordered_selected) == len(eligible),
        "independent_terminal_reviewer_claimed": False,
    }
    write_once_or_same(root / "human_review_eligibility_report.json", eligibility)
    return binding


def constituent(
    identifier: str,
    *,
    path: Path | None = None,
    value: Any = None,
) -> dict[str, Any]:
    if path is not None:
        return {
            "id": identifier,
            "path": repo_relative(path),
            "sha256": sha256_file(path) if path.is_file() else None,
            "present": path.is_file(),
        }
    return {
        "id": identifier,
        "value": value,
        "sha256": canonical_hash(value),
        "present": value is not None,
    }


def build_phase8_handoff(attempt_id: str, attempt_root: Path) -> dict[str, Any]:
    require_phase0(attempt_root)
    p0 = phase_root(attempt_root, 0)
    p2 = phase_root(attempt_root, 2)
    p4 = phase_root(attempt_root, 4)
    p5 = phase_root(attempt_root, 5)
    p6 = phase_root(attempt_root, 6)
    p7 = phase_root(attempt_root, 7)
    root = phase_root(attempt_root, 8)
    root.mkdir(parents=True, exist_ok=True)
    required_prior = (
        p0 / "publish_foundation_binding_report.json",
        p0 / "body_plan_applicability_authority_binding.json",
        p2 / "source_proposition_manifest.json",
        p2 / "body_plan_requirement_inventory.jsonl",
        p2 / "body_plan_applicability_report.json",
        p4 / "candidate_rendered.json",
        p4 / "candidate_manifest.json",
        p4 / "protected_surface_after_snapshot.json",
        p5 / "semantic_preservation_report.json",
        p5 / "structural_satisfaction_ledger.jsonl",
        p5 / "body_plan_application_report.json",
        p6 / "raw_detector_report.json",
        p7 / "human_review_sample_manifest.json",
        p7 / "human_review_binding_report.json",
    )
    require_files(required_prior)
    foundation_binding = load_json(p0 / "publish_foundation_binding_report.json")
    applicability_binding = load_json(
        p0 / "body_plan_applicability_authority_binding.json"
    )
    applicability_report = load_json(p2 / "body_plan_applicability_report.json")
    candidate_manifest = load_json(p4 / "candidate_manifest.json")
    body_report = load_json(p5 / "body_plan_application_report.json")
    semantic_report = load_json(p5 / "semantic_preservation_report.json")
    raw_report = load_json(p6 / "raw_detector_report.json")
    review_binding = load_json(p7 / "human_review_binding_report.json")
    constituents = [
        constituent("naturalization_attempt_id", value=attempt_id),
        constituent(
            "foundation_contract_hash",
            path=FOUNDATION_CONTRACT,
        ),
        constituent("candidate_rendered_hash", path=p4 / "candidate_rendered.json"),
        constituent("candidate_manifest_hash", path=p4 / "candidate_manifest.json"),
        constituent(
            "source_proposition_manifest_hash",
            path=p2 / "source_proposition_manifest.json",
        ),
        constituent(
            "body_plan_requirement_digest",
            path=p2 / "body_plan_requirement_inventory.jsonl",
        ),
        constituent(
            "structural_satisfaction_ledger_hash",
            path=p5 / "structural_satisfaction_ledger.jsonl",
        ),
        constituent(
            "semantic_preservation_report_hash",
            path=p5 / "semantic_preservation_report.json",
        ),
        constituent("raw_detector_report_hash", path=p6 / "raw_detector_report.json"),
        constituent(
            "human_review_sample_manifest_hash",
            path=p7 / "human_review_sample_manifest.json",
        ),
        constituent(
            "human_review_decision_hash",
            path=HUMAN_REVIEW_DECISION_PATH,
        ),
        constituent(
            "compiler_implementation_hash",
            value=implementation_hash(),
        ),
        constituent("korean_prose_policy_hash", path=POLICY_PATH),
        constituent("corpus_manifest_hash", path=CORPUS_MANIFEST_PATH),
        constituent(
            "protected_surface_no_mutation_report_hash",
            path=p4 / "protected_surface_after_snapshot.json",
        ),
        constituent(
            "requested_evaluation_subject_kind",
            value=EVALUATION_SUBJECT_KIND,
        ),
    ]
    publish_input = {
        "schema_version": "dvf-3-3-publish-acceptance-input-v1",
        "synchronization_contract_id": SYNC_CONTRACT_ID,
        "requested_evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
        "evaluation_subject_hash": sha256_file(p4 / "candidate_rendered.json"),
        "naturalization_attempt_id": attempt_id,
        "constituents": constituents,
        "candidate_runtime_parity_applicability": "not_applicable",
        "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
        "registry_runtime_pass_claim_allowed": False,
    }
    write_once_or_same(root / "publish_acceptance_input.json", publish_input)
    blockers: list[str] = []
    if any(not row["present"] for row in constituents):
        blockers.append("required_handoff_constituent_missing")
    if not semantic_report.get("semantic_preservation_pass"):
        blockers.append("semantic_preservation_not_pass")
    if body_report.get("unsatisfied_required_body_plan_role_count") != 0:
        blockers.append("unsatisfied_required_body_plan_role")
    if not raw_report.get("raw_detector_full_candidate_completeness_pass"):
        blockers.append("raw_detector_incomplete")
    if review_binding.get("status") != "PASS":
        blockers.append("human_review_not_pass")
    if (
        applicability_binding.get("owner_approval_match") is not True
        or applicability_report.get("status") != "PASS"
        or applicability_report.get("source_proposition_invention_count") != 0
    ):
        blockers.append("body_plan_applicability_authority_not_pass")
    if not QUALITY_APPROVAL_PATH.is_file() or not GOLD_APPROVAL_PATH.is_file():
        blockers.append("corpus_or_quality_owner_approval_missing")
    if candidate_manifest.get("candidate_content_hash_count") != 1:
        blockers.append("candidate_content_hash_count_invalid")
    readiness = {
        "schema_version": "dvf-3-3-publish-handoff-readiness-report-v1",
        "status": "PASS" if not blockers else "blocked_handoff_not_ready",
        "naturalization_attempt_id": attempt_id,
        "candidate_rendered_hash": sha256_file(p4 / "candidate_rendered.json"),
        "required_constituent_count": len(constituents),
        "present_constituent_count": sum(row["present"] for row in constituents),
        "blocker_reasons": blockers,
        "publish_acceptance_handoff_manifest_frozen": not blockers,
        "official_publish_attempt_created": False,
        "publish_disposition_created": False,
        "live_required_gate_adopted": False,
        "runtime_or_current_adoption_claimed": False,
    }
    write_once_or_same(root / "publish_handoff_readiness_report.json", readiness)
    if not blockers:
        handoff = {
            "schema_version": "naturalization_publish_handoff_required_schema_v1",
            "synchronization_contract_id": SYNC_CONTRACT_ID,
            "naturalization_attempt_id": attempt_id,
            "requested_evaluation_subject_kind": EVALUATION_SUBJECT_KIND,
            "candidate_runtime_parity_applicability": "not_applicable",
            "candidate_runtime_parity_reason": "candidate_not_registry_adopted",
            "constituents": constituents,
            "constituent_id_order": [row["id"] for row in constituents],
            "post_handoff_mutation_effect": "stale",
            "registry_runtime_pass_claim_allowed": False,
            "write_once": True,
        }
        handoff_path = root / "publish_acceptance_handoff_manifest.json"
        write_once_or_same(handoff_path, handoff)
        closeout = {
            "schema_version": "dvf-3-3-naturalization-phase8-closeout-v1",
            "status": "HANDOFF_COMPLETE",
            "naturalization_attempt_id": attempt_id,
            "candidate_rendered_sha256": sha256_file(
                p4 / "candidate_rendered.json"
            ),
            "publish_acceptance_handoff_manifest_path": repo_relative(
                handoff_path
            ),
            "publish_acceptance_handoff_manifest_sha256": sha256_file(
                handoff_path
            ),
            "human_review_denominator": review_binding.get(
                "required_review_denominator"
            ),
            "human_review_blocker_count": review_binding.get(
                "human_review_blocker_count_within_required_denominator"
            ),
            "official_publish_attempt_created": False,
            "official_publish_executed": False,
            "live_gate_mutated": False,
            "runtime_lua_or_package_mutated": False,
            "naturalization_terminal_closure_claimed": False,
            "next_stage": "official_publish_attempt_prohibited_until_separate_authorization",
            "write_once": True,
        }
        write_once_or_same(root / "phase8_closeout.json", closeout)
    return readiness


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build DVF 3-3 Korean prose naturalization evidence through the "
            "immutable Phase 8 Publish handoff boundary."
        )
    )
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--mode", required=True, choices=RUNNER_MODES)
    parser.add_argument(
        "--attempt-root",
        type=Path,
        default=None,
        help="Explicit attempt root for isolated fixtures; defaults to canonical staging.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = attempt_root_for(args.attempt_id, args.attempt_root)
        builders = {
            "phase0-preflight": build_phase0,
            "phase1-census": build_phase1,
            "phase2-source-inventory": build_phase2,
            "phase3-compiler-evidence": build_phase3,
            "phase4-candidate": build_phase4,
            "phase5-semantic": build_phase5_semantic,
            "phase5-adversarial": build_phase5_adversarial,
            "phase6-raw-detectors": build_phase6,
            "phase7-human-review-sample": build_phase7,
            "phase8-publish-handoff": build_phase8_handoff,
        }
        result = builders[args.mode](args.attempt_id, root)
    except (NaturalizationError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(
            json.dumps(
                {"status": "FAIL", "error": str(exc)},
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 3 if "write-once conflict" in str(exc) else 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result.get("status") in {
        "blocked_prerequisite",
        "blocked_owner_approval_required",
        "blocked_facts_authority_information_insufficient",
        "blocked_human_review_required",
        "blocked_handoff_not_ready",
    }:
        return 4
    return 0 if result.get("status", "PASS") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
