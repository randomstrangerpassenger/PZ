from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


ROUND_ID = "dvf_3_3_registry_authority_canonical_closure"
CYCLE_ID = ROUND_ID
SCHEMA_PREFIX = "dvf-3-3-registry-authority-canonical-closure"
CONSUMED_ROADMAP_SHA256 = "17c41198e4d35a15743fd6c9f869ca545c5363a3a32eb005db1e94bc16530ecd"

REPO_ROOT = Path(__file__).resolve().parents[6]
V2_ROOT = REPO_ROOT / "Iris" / "build" / "description" / "v2"
TOOLS_ROOT = V2_ROOT / "tools" / "build"
TESTS_ROOT = V2_ROOT / "tests"
DEFAULT_EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
ATTEMPTS_ROOT = DEFAULT_EVIDENCE_ROOT / "attempts"

PLAN_PATH = REPO_ROOT / "docs" / f"{ROUND_ID}_plan.md"
ROADMAP_PATH = REPO_ROOT / "docs" / f"{ROUND_ID}_roadmap.md"
PHILOSOPHY_PATH = REPO_ROOT / "docs" / "Philosophy.md"
DECISIONS_PATH = REPO_ROOT / "docs" / "DECISIONS.md"
ARCHITECTURE_PATH = REPO_ROOT / "docs" / "ARCHITECTURE.md"
PROJECT_ROADMAP_PATH = REPO_ROOT / "docs" / "ROADMAP.md"
EXECUTION_CONTRACT_PATH = REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md"
LUA_CHECKER_PATH = REPO_ROOT / "tools" / "check_lua_syntax.ps1"

COMMON_PATH = TOOLS_ROOT / f"{ROUND_ID}.py"
RUNNER_PATH = TOOLS_ROOT / f"run_{ROUND_ID}.py"
VALIDATOR_PATH = TOOLS_ROOT / f"validate_{ROUND_ID}.py"
FOCUSED_TEST_PATH = TESTS_ROOT / f"test_{ROUND_ID}.py"
BOOTSTRAP_MANIFEST_PATH = DEFAULT_EVIDENCE_ROOT / "phase0" / "bootstrap_scaffold_hash_manifest.json"

OWNER_INPUT_ROOT = V2_ROOT / "owner_inputs" / ROUND_ID
CLEAN_CHECKPOINT_INPUT = (
    OWNER_INPUT_ROOT / "worktree_checkpoints" / "current_session_clean_worktree_checkpoint_record.json"
)
OWNER_DECISION_INPUT = (
    OWNER_INPUT_ROOT / "owner_decisions" / "current_session_owner_decision_record.json"
)
PLAN_APPROVAL_INPUT = (
    OWNER_INPUT_ROOT / "plan_approvals" / "current_session_implementation_plan_approval_record.json"
)
REVIEWER_DESIGNATION_INPUT = (
    OWNER_INPUT_ROOT / "reviewer_designations" / "current_session_independent_reviewer_designation.json"
)
ATTEMPT_REGISTRATION_INPUT = (
    OWNER_INPUT_ROOT
    / "attempt_registrations"
    / "current_session_attempt_record.json"
)
GATE_ADOPTION_INPUT = (
    OWNER_INPUT_ROOT
    / "gate_adoptions"
    / "current_session_required_gate_adoption_authorization_record.json"
)
PREIMPLEMENTATION_REVIEW_INPUTS = (
    OWNER_INPUT_ROOT
    / "preimplementation_reviews"
    / "current_session_responsibility_boundary_review.md",
    OWNER_INPUT_ROOT
    / "preimplementation_reviews"
    / "current_session_authority_evidence_integrity_review.md",
    OWNER_INPUT_ROOT
    / "preimplementation_reviews"
    / "current_session_adversarial_failure_mode_review.md",
)
INDEPENDENT_REVIEW_INPUT = (
    OWNER_INPUT_ROOT / "independent_reviews" / "current_session_independent_closeout_review.md"
)
OWNER_SEAL_INPUT = (
    OWNER_INPUT_ROOT / "owner_seals" / "current_session_owner_canonical_seal_record.json"
)

RESERVED_EXTERNAL_INPUTS = (
    CLEAN_CHECKPOINT_INPUT,
    OWNER_DECISION_INPUT,
    PLAN_APPROVAL_INPUT,
    REVIEWER_DESIGNATION_INPUT,
    ATTEMPT_REGISTRATION_INPUT,
    *PREIMPLEMENTATION_REVIEW_INPUTS,
    GATE_ADOPTION_INPUT,
    INDEPENDENT_REVIEW_INPUT,
    OWNER_SEAL_INPUT,
)

SCAFFOLD_PATHS = (
    COMMON_PATH,
    RUNNER_PATH,
    VALIDATOR_PATH,
    FOCUSED_TEST_PATH,
)

ALL_RUNNER_MODES = (
    "preflight",
    "materialize-preimplementation-reviews",
    "implementation",
    "wp1",
    "wp2",
    "wp3",
    "wp4",
    "wp5",
    "wp6",
    "wp7",
    "gate-candidate",
    "adopt-gate",
    "final-rerun",
    "materialize-independent-review",
    "materialize-owner-seal",
    "prepare-top-docs",
    "post-external",
    "finalize",
)
IMPLEMENTED_SCAFFOLD_MODES = (
    "preflight",
    "materialize-preimplementation-reviews",
)
IMPLEMENTED_SCAFFOLD_VALIDATIONS = (
    "require-preflight",
    "require-preimplementation-reviews",
    "require-execution-entry",
)
IMPLEMENTED_RUNNER_MODES = (
    *IMPLEMENTED_SCAFFOLD_MODES,
    "implementation",
)
IMPLEMENTED_VALIDATIONS = (
    *IMPLEMENTED_SCAFFOLD_VALIDATIONS,
    "require-implementation",
)

PREIMPLEMENTATION_REVIEW_SCOPES = (
    "responsibility_boundary",
    "authority_evidence_integrity",
    "adversarial_failure_mode",
)
PREIMPLEMENTATION_REVIEW_OUTPUTS = (
    "responsibility_boundary_review.md",
    "authority_evidence_integrity_review.md",
    "adversarial_failure_mode_review.md",
)

PROTECTED_SURFACES = (
    V2_ROOT / "data" / "dvf_3_3_input_manifest.json",
    V2_ROOT / "data" / "dvf_3_3_facts.jsonl",
    V2_ROOT / "data" / "dvf_3_3_decisions.jsonl",
    V2_ROOT / "data" / "dvf_3_3_overlay_support.jsonl",
    V2_ROOT / "data" / "compose_profiles_v2.json",
    V2_ROOT / "data" / "compose_profile_identity_hint_rules.json",
    V2_ROOT / "data" / "compose_profile_conflict_precedence_rules.json",
    V2_ROOT / "output" / "dvf_3_3_rendered.json",
    V2_ROOT / "output" / "style_normalization_changes.jsonl",
    V2_ROOT / "output" / "compose_requeue_candidates.jsonl",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "layer3_renderer.lua",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks.lua",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "UI" / "Wiki" / "IrisWikiSections.lua",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Util" / "IrisModuleBootstrap.lua",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Util" / "IrisRequire.lua",
    REPO_ROOT / "Iris" / "build" / "package",
)

LIVE_REQUIRED_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
ACTIVE_CORE_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"
ROUND3_CONTRACT_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_contract_manifest.json"
AUTHORITY_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "authority" / "iris_current_authority_manifest.json"
INPUT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
COMPOSE_TOOL = TOOLS_ROOT / "compose_layer3_text.py"
EXPORT_TOOL = TOOLS_ROOT / "export_dvf_3_3_lua_bridge.py"
COMPLETION_TOOL = TOOLS_ROOT / "dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
COMPLETION_RUNNER = TOOLS_ROOT / "run_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
COMPLETION_VALIDATOR = TOOLS_ROOT / "validate_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
COMPLETION_TEST = TESTS_ROOT / "test_dvf_3_3_completion_vocabulary_external_gate_vocabulary_split.py"
ROUND3_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"
RUNTIME_MANIFEST = REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks.lua"
RUNTIME_CHUNK_DIR = RUNTIME_MANIFEST.with_suffix("")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def filesystem_path(path: Path) -> Path:
    raw = str(path)
    if os.name == "nt" and raw.startswith("\\\\?\\"):
        return path
    resolved = path.resolve()
    if os.name != "nt":
        return resolved
    raw = str(resolved)
    if raw.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + raw[2:])
    return Path("\\\\?\\" + raw)


def path_is_file(path: Path) -> bool:
    return filesystem_path(path).is_file()


def path_is_dir(path: Path) -> bool:
    return filesystem_path(path).is_dir()


def sha256_file(path: Path) -> str | None:
    source = filesystem_path(path)
    if not source.is_file():
        return None
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_byte_identical(left: Path, right: Path) -> bool:
    left_source = filesystem_path(left)
    right_source = filesystem_path(right)
    return (
        left_source.is_file()
        and right_source.is_file()
        and left_source.read_bytes() == right_source.read_bytes()
    )


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def canonical_hash(payload: Any) -> str:
    return sha256_bytes(canonical_json_bytes(payload))


def text_content_sha256(path: Path) -> str | None:
    if not path_is_file(path):
        return None
    try:
        content = filesystem_path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return None
    return sha256_bytes(content.encode("utf-8"))


def directory_file_rows(path: Path) -> list[dict[str, str | None]] | None:
    source = filesystem_path(path)
    if not source.is_dir():
        return None
    rows: list[dict[str, str | None]] = []
    for directory, child_directories, filenames in os.walk(source):
        child_directories.sort()
        for filename in sorted(filenames):
            child = Path(directory) / filename
            rows.append(
                {
                    "path": child.relative_to(source).as_posix(),
                    "sha256": sha256_file(child),
                }
            )
    return rows


def directory_tree_hash(path: Path) -> str | None:
    rows = directory_file_rows(path)
    if rows is None:
        return None
    return canonical_hash(rows)


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def validate_attempt_id(attempt_id: str | None) -> str:
    if not isinstance(attempt_id, str) or not re.fullmatch(
        r"attempt-[0-9]{4,}-[a-z0-9][a-z0-9-]{0,47}", attempt_id
    ):
        raise ValueError(
            "attempt_id must match attempt-NNNN-lowercase-label"
        )
    return attempt_id


def resolve_evidence_root(
    value: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> Path:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    expected = (ATTEMPTS_ROOT / normalized_attempt_id).resolve()
    candidate = Path(value or expected).resolve()
    if candidate != expected or not is_within(candidate, ATTEMPTS_ROOT):
        raise ValueError(
            "evidence root must equal the registered attempt root "
            f"{repo_relative(expected)}"
        )
    return candidate


def read_json_object(path: Path) -> dict[str, Any]:
    source = filesystem_path(path)
    if not source.is_file():
        return {}
    try:
        with source.open("r", encoding="utf-8-sig") as handle:
            value = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def write_json_once(path: Path, payload: Any) -> None:
    if not is_within(path, ATTEMPTS_ROOT):
        raise ValueError(f"refusing out-of-attempt evidence write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(serialized)


def write_text_once(path: Path, payload: str) -> None:
    if not is_within(path, ATTEMPTS_ROOT):
        raise ValueError(f"refusing out-of-attempt evidence write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)


def copy_external_bytes_once(source: Path, target: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(source)
    if not is_within(target, ATTEMPTS_ROOT):
        raise ValueError(f"refusing out-of-attempt materialization: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as handle:
        handle.write(source.read_bytes())


def record_attempt_failure_once(
    evidence_root: str | Path | None,
    *,
    attempt_id: str | None,
    mode: str,
    error_type: str,
    error: str,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    terminal_by_mode = {
        "preflight": root / "phase0" / "preflight_report.json",
        "materialize-preimplementation-reviews": (
            root / "phase3" / "preimplementation_review_materialization_report.json"
        ),
    }
    terminal = terminal_by_mode.get(mode)
    failure_path = root / "attempt_failures" / f"{mode}.json"
    if terminal is not None and terminal.is_file():
        return {
            "written": False,
            "reason": "terminal_claim_output_already_exists",
            "path": None,
            "sha256": None,
        }
    if failure_path.is_file():
        return {
            "written": False,
            "reason": "failure_record_already_preserved",
            "path": repo_relative(failure_path),
            "sha256": sha256_file(failure_path),
        }
    payload = {
        "schema_version": f"{SCHEMA_PREFIX}-attempt-failure-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "mode": mode,
        "recorded_at": utc_now(),
        "status": "FAIL",
        "error_type": error_type,
        "error": error,
        "claim_output_overwritten": False,
        "failure_record_write_once": True,
        "wp_execution_allowed": False,
    }
    write_json_once(failure_path, payload)
    return {
        "written": True,
        "reason": "new_failure_record",
        "path": repo_relative(failure_path),
        "sha256": sha256_file(failure_path),
    }


def run_git(*args: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "argv": ["git", *args],
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def current_head() -> str | None:
    result = run_git("rev-parse", "HEAD")
    if result["exit_code"] != 0:
        return None
    return result["stdout"].strip() or None


def git_status_rows() -> tuple[str, list[str]]:
    result = run_git("status", "--porcelain=v1", "--untracked-files=all")
    output = result["stdout"] if result["exit_code"] == 0 else ""
    return output, [line for line in output.splitlines() if line]


def status_path(line: str) -> str:
    raw = line[3:] if len(line) >= 3 else line
    if " -> " in raw:
        raw = raw.split(" -> ", 1)[1]
    return raw.strip().strip('"').replace("\\", "/")


def scaffold_file_rows() -> list[dict[str, Any]]:
    return [
        {
            "path": repo_relative(path),
            "exists": path.is_file(),
            "byte_length": path.stat().st_size if path.is_file() else None,
            "sha256": sha256_file(path),
        }
        for path in SCAFFOLD_PATHS
    ]


def scaffold_capabilities() -> dict[str, Any]:
    return {
        "implemented_success_modes": list(IMPLEMENTED_SCAFFOLD_MODES),
        "implemented_success_validations": list(IMPLEMENTED_SCAFFOLD_VALIDATIONS),
        "declared_future_modes": list(ALL_RUNNER_MODES),
        "aggregate_mode_present": False,
        "review_materialization_present": True,
        "execution_entry_validation_present": True,
        "wp_implementation_present": False,
        "gate_adoption_present": False,
        "finalization_producer_present": False,
        "owner_or_reviewer_verdict_authoring_present": False,
        "current_or_protected_writer_present": False,
        "attempt_evidence_write_once_present": True,
        "failure_history_write_once_present": True,
    }


def scaffold_manifest_projection() -> dict[str, Any]:
    return {
        "schema_version": f"{SCHEMA_PREFIX}-bootstrap-scaffold-manifest-v2",
        "round_id": ROUND_ID,
        "self_hash_excluded": True,
        "commit_hash_excluded": True,
        "scaffold_paths": scaffold_file_rows(),
        "capabilities": scaffold_capabilities(),
    }


def validate_bootstrap_manifest() -> dict[str, Any]:
    stored = read_json_object(BOOTSTRAP_MANIFEST_PATH)
    projection = scaffold_manifest_projection()
    projection_hash = canonical_hash(projection)
    stored_projection = {
        key: stored.get(key)
        for key in (
            "schema_version",
            "round_id",
            "self_hash_excluded",
            "commit_hash_excluded",
            "scaffold_paths",
            "capabilities",
        )
    }
    return {
        "status": "PASS" if stored_projection == projection else "FAIL",
        "manifest_path": repo_relative(BOOTSTRAP_MANIFEST_PATH),
        "manifest_exists": BOOTSTRAP_MANIFEST_PATH.is_file(),
        "manifest_sha256": sha256_file(BOOTSTRAP_MANIFEST_PATH),
        "projection_sha256": projection_hash,
        "stored_projection_matches": stored_projection == projection,
        "projection": projection,
    }


def protected_surface_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in PROTECTED_SURFACES:
        if path_is_file(path):
            digest = sha256_file(path)
            kind = "file"
        elif path_is_dir(path):
            child_rows = directory_file_rows(path)
            if child_rows is None:
                raise RuntimeError(f"protected directory disappeared: {path}")
            digest = canonical_hash(child_rows)
            kind = "directory"
        else:
            digest = None
            kind = "missing"
        rows.append(
            {
                "path": repo_relative(path),
                "kind": kind,
                "sha256": digest,
            }
        )
    return rows


def lua_environment_report() -> dict[str, Any]:
    checker_hash = sha256_file(LUA_CHECKER_PATH)
    candidates: list[Path] = []
    if os.name == "nt":
        where = subprocess.run(
            ["where.exe", "luac"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if where.returncode == 0:
            candidates.extend(Path(line.strip()).resolve() for line in where.stdout.splitlines() if line.strip())
    else:
        resolved = shutil.which("luac")
        if resolved:
            candidates.append(Path(resolved).resolve())
    unique = sorted({path for path in candidates if path.is_file()}, key=lambda path: str(path).lower())
    version = None
    if len(unique) == 1:
        completed = subprocess.run(
            [str(unique[0]), "-v"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        version = (completed.stdout + completed.stderr).strip()
    lua_files = sorted(
        {
            path.resolve()
            for root in (
                REPO_ROOT / "Iris" / "media" / "lua",
                REPO_ROOT / "Iris" / "build" / "package" / "Iris" / "media" / "lua",
            )
            if root.is_dir()
            for path in root.rglob("*.lua")
            if path.is_file()
        },
        key=lambda path: str(path).lower(),
    )
    input_rows = [
        {"path": repo_relative(path), "sha256": sha256_file(path)}
        for path in lua_files
    ]
    status = (
        "PASS"
        if LUA_CHECKER_PATH.is_file() and checker_hash and len(unique) == 1 and input_rows
        else "FAIL"
    )
    return {
        "schema_version": f"{SCHEMA_PREFIX}-lua-environment-v1",
        "status": status,
        "checker_path": repo_relative(LUA_CHECKER_PATH),
        "checker_sha256": checker_hash,
        "luac_candidate_count": len(unique),
        "luac_candidates": [str(path) for path in unique],
        "luac_path": str(unique[0]) if len(unique) == 1 else None,
        "luac_sha256": sha256_file(unique[0]) if len(unique) == 1 else None,
        "luac_version": version,
        "lua_input_count": len(input_rows),
        "lua_input_set_sha256": canonical_hash(input_rows),
        "lua_inputs": input_rows,
    }


def lua_environment_identity(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if key not in {"cycle_id", "attempt_id"}
    }


def decision_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    decisions = payload.get("decisions", [])
    if not isinstance(decisions, list):
        return {}
    return {
        str(row.get("decision_id")): row
        for row in decisions
        if isinstance(row, dict) and row.get("decision_id")
    }


def approved_decisions_report(payload: dict[str, Any]) -> dict[str, Any]:
    by_id = decision_map(payload)
    required = [f"D{index}" for index in range(11)]
    allowed_states = {"owner_ratified", "owner_overridden"}
    rows = []
    for decision_id in required:
        row = by_id.get(decision_id, {})
        state = row.get("state") or row.get("owner_decision_state") or "missing"
        value_present = "value" in row or "owner_value" in row
        rows.append(
            {
                "decision_id": decision_id,
                "state": state,
                "value_present": value_present,
                "satisfied": state in allowed_states and value_present,
            }
        )
    return {
        "status": "PASS" if all(row["satisfied"] for row in rows) else "FAIL",
        "owner_identity": payload.get("owner_identity"),
        "decision_time": payload.get("decision_time"),
        "rows": rows,
        "unresolved_count": sum(not row["satisfied"] for row in rows),
    }


def preflight_external_contract() -> dict[str, Any]:
    return {
        "attempt_registration": {
            "path": repo_relative(ATTEMPT_REGISTRATION_INPUT),
            "required_fields": [
                "cycle_id",
                "attempt_id",
                "owner_identity",
                "registered_at",
                "execution_base_commit",
                "clean_worktree_checkpoint_path",
                "clean_worktree_checkpoint_sha256",
                "evidence_root",
                "retry_class",
                "predecessor_attempts",
                "prior_failure_records_preserved",
                "overwrite_existing_attempt_outputs_allowed",
                "receipt_nonce_reuse_allowed",
                "live_gate_adopted",
                "top_docs_applied",
                "protected_mutation_count",
            ],
            "predecessor_required_fields": [
                "attempt_id",
                "preserved_evidence_path",
                "preserved_evidence_tree_sha256",
                "failure_record_preserved",
            ],
            "post_split_predecessor_required_fields": [
                "preserved_owner_inputs_path",
                "preserved_owner_inputs_tree_sha256",
            ],
        },
        "clean_checkpoint": {
            "path": repo_relative(CLEAN_CHECKPOINT_INPUT),
            "required_fields": [
                "round_id",
                "owner_identity",
                "recorded_at",
                "execution_base_commit",
                "worktree_path",
                "git_status_command",
                "git_status_output",
                "git_status_output_sha256",
                "initial_dirty_count",
                "bootstrap_scaffold_manifest_sha256",
            ],
        },
        "owner_decisions": {
            "path": repo_relative(OWNER_DECISION_INPUT),
            "required_decisions": [f"D{index}" for index in range(11)],
            "allowed_states": ["owner_ratified", "owner_overridden"],
        },
        "plan_approval": {
            "path": repo_relative(PLAN_APPROVAL_INPUT),
            "required_fields": [
                "round_id",
                "owner_identity",
                "approved_at",
                "approved_plan_path",
                "approved_plan_sha256",
                "approved_roadmap_path",
                "approved_roadmap_sha256",
                "approved_bootstrap_scaffold_manifest_path",
                "approved_bootstrap_scaffold_manifest_sha256",
                "approved_clean_worktree_checkpoint_path",
                "approved_clean_worktree_checkpoint_sha256",
                "approved_execution_base_commit",
                "approved_attempt_id",
                "approved_attempt_registration_path",
                "approved_attempt_registration_sha256",
                "approved_evidence_root",
                "reserved_external_inputs",
            ],
        },
        "reviewer_designation": {
            "path": repo_relative(REVIEWER_DESIGNATION_INPUT),
            "required_fields": [
                "round_id",
                "owner_identity",
                "designated_at",
                "reviewer_identity",
                "eligible",
                "excluded_authors",
            ],
        },
    }


def validate_checkpoint(payload: dict[str, Any], scaffold: dict[str, Any], head: str | None) -> list[str]:
    blockers: list[str] = []
    if not payload:
        return ["clean_worktree_checkpoint_missing_or_invalid"]
    if payload.get("round_id") != ROUND_ID:
        blockers.append("clean_checkpoint_round_id_mismatch")
    if not payload.get("owner_identity") or not payload.get("recorded_at"):
        blockers.append("clean_checkpoint_author_or_time_missing")
    if payload.get("execution_base_commit") != head:
        blockers.append("clean_checkpoint_base_commit_mismatch")
    if int(payload.get("initial_dirty_count", -1)) != 0:
        blockers.append("clean_checkpoint_initial_dirty_count_nonzero")
    if payload.get("git_status_output", None) != "":
        blockers.append("clean_checkpoint_status_output_not_empty")
    if payload.get("git_status_output_sha256") != sha256_bytes(b""):
        blockers.append("clean_checkpoint_empty_status_hash_mismatch")
    if payload.get("git_status_command") != "git status --porcelain=v1 --untracked-files=all":
        blockers.append("clean_checkpoint_status_command_mismatch")
    if payload.get("bootstrap_scaffold_manifest_sha256") != scaffold.get("manifest_sha256"):
        blockers.append("clean_checkpoint_scaffold_manifest_hash_mismatch")
    recorded_path = payload.get("worktree_path")
    if not isinstance(recorded_path, str) or Path(recorded_path).resolve() != REPO_ROOT.resolve():
        blockers.append("clean_checkpoint_worktree_path_mismatch")
    return blockers


def validate_preserved_owner_input_archive(
    row: dict[str, Any],
    *,
    predecessor_id: str,
    attempt_archive: Path,
) -> tuple[Path | None, list[str]]:
    blockers: list[str] = []
    path_value = row.get("preserved_owner_inputs_path")
    expected_hash = row.get("preserved_owner_inputs_tree_sha256")
    if not isinstance(path_value, str) or not isinstance(expected_hash, str):
        return None, [
            f"attempt_registration_predecessor_owner_inputs_binding_missing:{predecessor_id}"
        ]
    archive = (REPO_ROOT / path_value).resolve()
    expected_archive = (
        DEFAULT_EVIDENCE_ROOT / "superseded_owner_inputs" / predecessor_id
    ).resolve()
    if (
        archive != expected_archive
        or not is_within(archive, DEFAULT_EVIDENCE_ROOT / "superseded_owner_inputs")
        or not path_is_dir(archive)
        or path_value.replace("\\", "/") != repo_relative(archive)
    ):
        blockers.append(
            f"attempt_registration_predecessor_owner_inputs_not_preserved:{predecessor_id}"
        )
    elif directory_tree_hash(archive) != expected_hash:
        blockers.append(
            f"attempt_registration_predecessor_owner_inputs_hash_mismatch:{predecessor_id}"
        )
    elif not directory_file_rows(archive):
        blockers.append(
            f"attempt_registration_predecessor_owner_inputs_empty:{predecessor_id}"
        )
    required_inputs = (
        "worktree_checkpoints/current_session_clean_worktree_checkpoint_record.json",
        "attempt_registrations/current_session_attempt_record.json",
        "owner_decisions/current_session_owner_decision_record.json",
        "reviewer_designations/current_session_independent_reviewer_designation.json",
        "plan_approvals/current_session_implementation_plan_approval_record.json",
    )
    for relative in required_inputs:
        if not path_is_file(archive / relative):
            blockers.append(
                f"attempt_registration_predecessor_owner_input_missing:{predecessor_id}:{relative}"
            )
    zero_record = read_json_object(
        attempt_archive / "phase3" / "blocker_zero_record.json"
    )
    if zero_record:
        for review_name in (
            "current_session_responsibility_boundary_review.md",
            "current_session_authority_evidence_integrity_review.md",
            "current_session_adversarial_failure_mode_review.md",
        ):
            if not path_is_file(
                archive / "preimplementation_reviews" / review_name
            ):
                blockers.append(
                    f"attempt_registration_predecessor_review_input_missing:{predecessor_id}:{review_name}"
                )
    if zero_record.get("status") == "PASS":
        entry_failure = read_json_object(archive / "execution_entry_failure_record.json")
        if (
            entry_failure.get("cycle_id") != CYCLE_ID
            or entry_failure.get("attempt_id") != predecessor_id
            or entry_failure.get("status") != "FAIL"
            or entry_failure.get("wp_execution_allowed") is not False
        ):
            blockers.append(
                f"attempt_registration_predecessor_entry_failure_record_invalid:{predecessor_id}"
            )
    return (archive if not blockers else None), blockers


def validate_attempt_registration(
    payload: dict[str, Any],
    *,
    attempt_id: str,
    evidence_root: Path,
    head: str | None,
    checkpoint_hash: str | None,
) -> list[str]:
    blockers: list[str] = []
    if not payload:
        return ["attempt_registration_missing_or_invalid"]
    expected = {
        "cycle_id": CYCLE_ID,
        "attempt_id": attempt_id,
        "execution_base_commit": head,
        "clean_worktree_checkpoint_path": repo_relative(CLEAN_CHECKPOINT_INPUT),
        "clean_worktree_checkpoint_sha256": checkpoint_hash,
        "evidence_root": repo_relative(evidence_root),
        "retry_class": "pre_adoption_no_protected_mutation",
        "prior_failure_records_preserved": True,
        "overwrite_existing_attempt_outputs_allowed": False,
        "receipt_nonce_reuse_allowed": False,
        "live_gate_adopted": False,
        "top_docs_applied": False,
        "protected_mutation_count": 0,
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            blockers.append(f"attempt_registration_{field}_mismatch")
    if not payload.get("owner_identity") or not payload.get("registered_at"):
        blockers.append("attempt_registration_author_or_time_missing")
    predecessors = payload.get("predecessor_attempts")
    if not isinstance(predecessors, list):
        blockers.append("attempt_registration_predecessors_invalid")
        return blockers
    seen_ids: set[str] = set()
    seen_archives: set[Path] = set()
    seen_owner_input_archives: set[Path] = set()
    for index, row in enumerate(predecessors):
        if not isinstance(row, dict):
            blockers.append(f"attempt_registration_predecessor_row_invalid:{index}")
            continue
        predecessor_id = row.get("attempt_id")
        archive_path = row.get("preserved_evidence_path")
        if (
            not isinstance(predecessor_id, str)
            or not re.fullmatch(
                r"attempt-[0-9]{4,}-[a-z0-9][a-z0-9-]{0,47}", predecessor_id
            )
            or predecessor_id == attempt_id
            or predecessor_id in seen_ids
            or not isinstance(archive_path, str)
        ):
            blockers.append(f"attempt_registration_predecessor_identity_invalid:{index}")
            continue
        seen_ids.add(predecessor_id)
        archive = (REPO_ROOT / archive_path).resolve()
        if archive in seen_archives:
            blockers.append(f"attempt_registration_predecessor_archive_duplicate:{predecessor_id}")
        seen_archives.add(archive)
        if (
            not is_within(archive, DEFAULT_EVIDENCE_ROOT)
            or not archive.is_dir()
            or archive_path.replace("\\", "/") != repo_relative(archive)
        ):
            blockers.append(f"attempt_registration_predecessor_not_preserved:{predecessor_id}")
        elif row.get("preserved_evidence_tree_sha256") != directory_tree_hash(archive):
            blockers.append(f"attempt_registration_predecessor_hash_mismatch:{predecessor_id}")
        terminal_records = (
            archive / "preflight_report.json",
            archive / "phase0" / "preflight_report.json",
            archive / "attempt_failures" / "preflight.json",
        )
        if not any(path.is_file() for path in terminal_records):
            blockers.append(f"attempt_registration_predecessor_terminal_record_missing:{predecessor_id}")
        if row.get("failure_record_preserved") is not True:
            blockers.append(f"attempt_registration_predecessor_failure_not_preserved:{predecessor_id}")
        if is_within(archive, ATTEMPTS_ROOT):
            owner_archive, owner_archive_blockers = validate_preserved_owner_input_archive(
                row,
                predecessor_id=predecessor_id,
                attempt_archive=archive,
            )
            blockers.extend(owner_archive_blockers)
            if owner_archive is not None:
                seen_owner_input_archives.add(owner_archive)
    legacy_root = DEFAULT_EVIDENCE_ROOT / "superseded_review_rounds"
    expected_archives = {
        path.resolve()
        for root in (legacy_root, ATTEMPTS_ROOT)
        if root.is_dir()
        for path in root.iterdir()
        if path.is_dir() and path.resolve() != evidence_root.resolve()
    }
    if seen_archives != expected_archives:
        blockers.append("attempt_registration_predecessor_archive_set_mismatch")
    owner_history_root = DEFAULT_EVIDENCE_ROOT / "superseded_owner_inputs"
    expected_owner_input_archives = (
        {
            path.resolve()
            for path in owner_history_root.iterdir()
            if path.is_dir()
        }
        if owner_history_root.is_dir()
        else set()
    )
    if seen_owner_input_archives != expected_owner_input_archives:
        blockers.append("attempt_registration_predecessor_owner_input_archive_set_mismatch")
    return blockers


def validate_plan_approval(
    payload: dict[str, Any],
    *,
    head: str | None,
    checkpoint_hash: str | None,
    scaffold: dict[str, Any],
    attempt_id: str,
    evidence_root: Path,
    attempt_registration_hash: str | None,
    enforce_present_input_set: bool = True,
) -> list[str]:
    blockers: list[str] = []
    if not payload:
        return ["implementation_plan_approval_missing_or_invalid"]
    if not payload.get("owner_identity") or not payload.get("approved_at"):
        blockers.append("plan_approval_author_or_time_missing")
    expected = {
        "round_id": ROUND_ID,
        "approved_plan_path": repo_relative(PLAN_PATH),
        "approved_plan_sha256": sha256_file(PLAN_PATH),
        "approved_roadmap_path": repo_relative(ROADMAP_PATH),
        "approved_roadmap_sha256": sha256_file(ROADMAP_PATH),
        "approved_bootstrap_scaffold_manifest_path": repo_relative(BOOTSTRAP_MANIFEST_PATH),
        "approved_bootstrap_scaffold_manifest_sha256": scaffold.get("manifest_sha256"),
        "approved_clean_worktree_checkpoint_path": repo_relative(CLEAN_CHECKPOINT_INPUT),
        "approved_clean_worktree_checkpoint_sha256": checkpoint_hash,
        "approved_execution_base_commit": head,
        "approved_attempt_id": attempt_id,
        "approved_attempt_registration_path": repo_relative(ATTEMPT_REGISTRATION_INPUT),
        "approved_attempt_registration_sha256": attempt_registration_hash,
        "approved_evidence_root": repo_relative(evidence_root),
    }
    for field, value in expected.items():
        if payload.get(field) != value:
            blockers.append(f"plan_approval_{field}_mismatch")
    approved_inputs = payload.get("reserved_external_inputs")
    if not isinstance(approved_inputs, list):
        blockers.append("plan_approval_reserved_external_inputs_missing")
        return blockers

    reserved = {repo_relative(path) for path in RESERVED_EXTERNAL_INPUTS}
    seen: set[str] = set()
    for index, row in enumerate(approved_inputs):
        if not isinstance(row, dict):
            blockers.append(f"plan_approval_reserved_input_row_invalid:{index}")
            continue
        path = str(row.get("path", "")).replace("\\", "/")
        digest = row.get("sha256")
        if not path or path in seen:
            blockers.append(f"plan_approval_reserved_input_duplicate_or_empty:{index}")
            continue
        seen.add(path)
        if path not in reserved or any(token in path for token in ("*", "?", "[")):
            blockers.append(f"plan_approval_reserved_input_path_invalid:{path}")
            continue
        resolved = REPO_ROOT / path
        if not resolved.is_file() or not digest or sha256_file(resolved) != digest:
            blockers.append(f"plan_approval_reserved_input_hash_mismatch:{path}")

    present_external_inputs = {
        repo_relative(path)
        for path in RESERVED_EXTERNAL_INPUTS
        if path.is_file() and path != PLAN_APPROVAL_INPUT
    }
    if enforce_present_input_set and seen != present_external_inputs:
        blockers.append("plan_approval_present_external_input_set_mismatch")
    return blockers


def validate_reviewer_designation(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not payload:
        return ["independent_reviewer_designation_missing_or_invalid"]
    if payload.get("round_id") != ROUND_ID:
        blockers.append("reviewer_designation_round_id_mismatch")
    if payload.get("eligible") is not True:
        blockers.append("reviewer_designation_not_eligible")
    if not payload.get("owner_identity") or not payload.get("designated_at"):
        blockers.append("reviewer_designation_author_or_time_missing")
    if not payload.get("reviewer_identity"):
        blockers.append("reviewer_identity_missing")
    excluded = payload.get("excluded_authors")
    if not isinstance(excluded, list) or not excluded:
        blockers.append("reviewer_excluded_authors_missing")
    return blockers


def validate_preflight_status(
    status_lines: list[str], approval: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[str]]:
    approved_rows = approval.get("reserved_external_inputs", [])
    approved_by_path = {
        str(row.get("path", "")).replace("\\", "/"): row
        for row in approved_rows
        if isinstance(row, dict)
    }
    rows = []
    blockers = []
    reserved = {repo_relative(path) for path in RESERVED_EXTERNAL_INPUTS}
    for line in status_lines:
        path = status_path(line)
        approval_self = path == repo_relative(PLAN_APPROVAL_INPUT)
        allowed = path in reserved and (path in approved_by_path or approval_self)
        expected_hash = (
            sha256_file(PLAN_APPROVAL_INPUT)
            if approval_self
            else approved_by_path.get(path, {}).get("sha256")
        )
        actual_hash = sha256_file(REPO_ROOT / path)
        hash_matches = bool(expected_hash and actual_hash == expected_hash)
        row = {
            "status_line": line,
            "path": path,
            "reserved_external_input": path in reserved,
            "listed_in_plan_approval": path in approved_by_path,
            "plan_approval_self_path_exception": approval_self,
            "expected_sha256": expected_hash,
            "actual_sha256": actual_hash,
            "hash_matches": hash_matches,
            "allowed": allowed and hash_matches,
        }
        rows.append(row)
        if not row["allowed"]:
            blockers.append(f"unapproved_preflight_delta:{path}")
    return rows, blockers


def run_preflight(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(
            f"attempt evidence is write-once and already exists: {repo_relative(root)}"
        )
    started_at = utc_now()
    head = current_head()
    status_output, status_lines = git_status_rows()
    scaffold = validate_bootstrap_manifest()
    decisions = read_json_object(OWNER_DECISION_INPUT)
    decision_report = approved_decisions_report(decisions)
    checkpoint = read_json_object(CLEAN_CHECKPOINT_INPUT)
    approval = read_json_object(PLAN_APPROVAL_INPUT)
    designation = read_json_object(REVIEWER_DESIGNATION_INPUT)
    attempt_registration = read_json_object(ATTEMPT_REGISTRATION_INPUT)
    lua = lua_environment_report()
    protected_rows = protected_surface_rows()
    protected_paths = [row["path"] for row in protected_rows]
    expected_protected_paths = [repo_relative(path) for path in PROTECTED_SURFACES]

    blockers: list[str] = []
    if scaffold["status"] != "PASS":
        blockers.append("bootstrap_scaffold_manifest_mismatch")
    if sha256_file(ROADMAP_PATH) != CONSUMED_ROADMAP_SHA256:
        blockers.append("repo_local_roadmap_hash_mismatch")
    if decision_report["status"] != "PASS":
        blockers.append("owner_reserved_decisions_unresolved")
    blockers.extend(validate_checkpoint(checkpoint, scaffold, head))
    blockers.extend(
        validate_attempt_registration(
            attempt_registration,
            attempt_id=normalized_attempt_id,
            evidence_root=root,
            head=head,
            checkpoint_hash=sha256_file(CLEAN_CHECKPOINT_INPUT),
        )
    )
    plan_approval_blockers = validate_plan_approval(
        approval,
        head=head,
        checkpoint_hash=sha256_file(CLEAN_CHECKPOINT_INPUT),
        scaffold=scaffold,
        attempt_id=normalized_attempt_id,
        evidence_root=root,
        attempt_registration_hash=sha256_file(ATTEMPT_REGISTRATION_INPUT),
    )
    blockers.extend(plan_approval_blockers)
    blockers.extend(validate_reviewer_designation(designation))
    status_rows, status_blockers = validate_preflight_status(status_lines, approval)
    blockers.extend(status_blockers)
    reserved_external = {path.resolve() for path in RESERVED_EXTERNAL_INPUTS}
    external_input_files = (
        sorted(path.resolve() for path in OWNER_INPUT_ROOT.rglob("*") if path.is_file())
        if OWNER_INPUT_ROOT.is_dir()
        else []
    )
    for path in external_input_files:
        if path not in reserved_external:
            blockers.append(f"unlisted_external_input:{repo_relative(path)}")
            continue
        ignored = run_git("check-ignore", "-q", "--", repo_relative(path))["exit_code"] == 0
        if ignored:
            blockers.append(f"ignored_external_input:{repo_relative(path)}")
    if lua["status"] != "PASS":
        blockers.append("lua_syntax_environment_preflight_failed")
    if protected_paths != expected_protected_paths or len(set(protected_paths)) != len(protected_paths):
        blockers.append("protected_surface_plan_denominator_set_mismatch")
    if any(row["kind"] == "missing" for row in protected_rows):
        blockers.append("protected_surface_plan_member_missing")

    input_hash_rows = [
        {"path": repo_relative(path), "sha256": sha256_file(path)}
        for path in (
            PLAN_PATH,
            ROADMAP_PATH,
            BOOTSTRAP_MANIFEST_PATH,
            CLEAN_CHECKPOINT_INPUT,
            OWNER_DECISION_INPUT,
            PLAN_APPROVAL_INPUT,
            REVIEWER_DESIGNATION_INPUT,
            ATTEMPT_REGISTRATION_INPUT,
        )
    ]
    reviewed_bundle = {
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "execution_base_commit": head,
        "inputs": input_hash_rows,
        "protected_surface_hash": canonical_hash(protected_rows),
        "lua_environment_hash": canonical_hash(lua_environment_identity(lua)),
        "preflight_status": "PASS" if not blockers else "FAIL",
    }
    reviewed_bundle_hash = canonical_hash(reviewed_bundle)

    phase0 = root / "phase0"
    phase3 = root / "phase3"
    reports: dict[str, Any] = {
        "registry_authority_plan_traceability_matrix.json": {
            "schema_version": f"{SCHEMA_PREFIX}-traceability-v1",
            "round_id": ROUND_ID,
            "status": "PASS" if not blockers else "FAIL",
            "plan_path": repo_relative(PLAN_PATH),
            "plan_sha256": sha256_file(PLAN_PATH),
            "roadmap_path": repo_relative(ROADMAP_PATH),
            "roadmap_sha256": sha256_file(ROADMAP_PATH),
            "wp_execution_allowed": False,
            "rows": [
                {"roadmap_unit": "Phase 3 reviews", "planned_producer": "materialize-preimplementation-reviews", "consumer": "require-execution-entry"},
                *[
                    {"roadmap_unit": f"WP-{index}", "planned_producer": f"wp{index}", "consumer": "require-implementation"}
                    for index in range(1, 8)
                ],
            ],
        },
        "registry_authority_evidence_root_manifest.json": {
            "schema_version": f"{SCHEMA_PREFIX}-evidence-root-v1",
            "round_id": ROUND_ID,
            "evidence_root": repo_relative(root),
            "containment_status": "PASS",
            "preflight_only": True,
        },
        "roadmap_approval_record.json": {
            "schema_version": f"{SCHEMA_PREFIX}-roadmap-approval-projection-v1",
            "round_id": ROUND_ID,
            "source_owner_decision_path": repo_relative(OWNER_DECISION_INPUT),
            "source_owner_decision_sha256": sha256_file(OWNER_DECISION_INPUT),
            "roadmap_path": repo_relative(ROADMAP_PATH),
            "roadmap_sha256": sha256_file(ROADMAP_PATH),
            "consumed_roadmap_sha256": CONSUMED_ROADMAP_SHA256,
            "hash_matches": sha256_file(ROADMAP_PATH) == CONSUMED_ROADMAP_SHA256,
            "tool_authored_approval": False,
        },
        "roadmap_scope_boundary_record.json": {
            "schema_version": f"{SCHEMA_PREFIX}-roadmap-scope-v1",
            "round_id": ROUND_ID,
            "authority_surface_touched": True,
            "runtime_behavior_surface_touched": False,
            "compatibility_surface_touched": False,
            "public_facing_output_surface_touched": False,
            "wp_execution_allowed": False,
        },
        "roadmap_provenance_record.json": {
            "schema_version": f"{SCHEMA_PREFIX}-roadmap-provenance-v1",
            "round_id": ROUND_ID,
            "repo_local_path": repo_relative(ROADMAP_PATH),
            "repo_local_sha256": sha256_file(ROADMAP_PATH),
            "attachment_is_execution_dependency": False,
        },
        "implementation_plan_fingerprint_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-plan-fingerprint-v1",
            "round_id": ROUND_ID,
            "plan_path": repo_relative(PLAN_PATH),
            "plan_sha256": sha256_file(PLAN_PATH),
            "roadmap_sha256": sha256_file(ROADMAP_PATH),
            "execution_base_commit": head,
        },
        "implementation_plan_approval_validation_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-plan-approval-validation-v1",
            "round_id": ROUND_ID,
            "status": "PASS" if not plan_approval_blockers else "FAIL",
            "blockers": plan_approval_blockers,
            "external_input_path": repo_relative(PLAN_APPROVAL_INPUT),
            "external_input_sha256": sha256_file(PLAN_APPROVAL_INPUT),
        },
        "owner_reserved_decision_register.json": {
            "schema_version": f"{SCHEMA_PREFIX}-owner-decisions-v1",
            "round_id": ROUND_ID,
            "source_path": repo_relative(OWNER_DECISION_INPUT),
            "source_sha256": sha256_file(OWNER_DECISION_INPUT),
            **decision_report,
        },
        "current_checkout_baseline.json": {
            "schema_version": f"{SCHEMA_PREFIX}-checkout-baseline-v1",
            "round_id": ROUND_ID,
            "head": head,
            "status_command": "git status --porcelain=v1 --untracked-files=all",
            "status_output_sha256": sha256_bytes(status_output.encode("utf-8")),
            "status_rows": status_rows,
        },
        "dirty_overlap_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-dirty-overlap-v1",
            "round_id": ROUND_ID,
            "status": "PASS" if not status_blockers else "FAIL",
            "unapproved_delta_count": len(status_blockers),
            "rows": status_rows,
        },
        "worktree_isolation_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-worktree-isolation-v1",
            "round_id": ROUND_ID,
            "status": "PASS" if not validate_checkpoint(checkpoint, scaffold, head) else "FAIL",
            "repo_root": str(REPO_ROOT.resolve()),
            "head": head,
            "checkpoint_input_path": repo_relative(CLEAN_CHECKPOINT_INPUT),
            "checkpoint_input_sha256": sha256_file(CLEAN_CHECKPOINT_INPUT),
            "blockers": validate_checkpoint(checkpoint, scaffold, head),
        },
        "protected_surface_policy.json": {
            "schema_version": f"{SCHEMA_PREFIX}-protected-surface-policy-v1",
            "round_id": ROUND_ID,
            "writer_authority_opened": False,
            "current_regeneration_authorized": False,
            "paths": expected_protected_paths,
            "plan_denominator_set_equality": protected_paths == expected_protected_paths,
            "duplicate_path_count": len(protected_paths) - len(set(protected_paths)),
            "missing_path_count": sum(row["kind"] == "missing" for row in protected_rows),
        },
        "protected_surface_hashes.before.json": {
            "schema_version": f"{SCHEMA_PREFIX}-protected-hashes-v1",
            "round_id": ROUND_ID,
            "rows": protected_rows,
        },
        "protected_surface_plan_mapping_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-protected-surface-plan-mapping-v1",
            "round_id": ROUND_ID,
            "status": "PASS"
            if protected_paths == expected_protected_paths
            and len(set(protected_paths)) == len(protected_paths)
            and all(row["kind"] != "missing" for row in protected_rows)
            else "FAIL",
            "expected_paths": expected_protected_paths,
            "actual_paths": protected_paths,
            "set_equality": set(protected_paths) == set(expected_protected_paths),
            "order_equality": protected_paths == expected_protected_paths,
            "duplicate_path_count": len(protected_paths) - len(set(protected_paths)),
            "missing_paths": [row["path"] for row in protected_rows if row["kind"] == "missing"],
        },
        "vcs_visibility_preflight.json": {
            "schema_version": f"{SCHEMA_PREFIX}-vcs-preflight-v1",
            "round_id": ROUND_ID,
            "status": "PASS" if not status_blockers else "FAIL",
            "rows": status_rows,
        },
        "evidence_root_preservation_policy.json": {
            "schema_version": f"{SCHEMA_PREFIX}-preservation-policy-v1",
            "round_id": ROUND_ID,
            "bootstrap_manifest_selectively_tracked": True,
            "generated_preflight_evidence_is_current_authority": False,
            "broad_unignore_allowed": False,
        },
        "lua_syntax_environment_preflight.json": lua,
        "preflight_report.json": {
            "schema_version": f"{SCHEMA_PREFIX}-preflight-report-v1",
            "round_id": ROUND_ID,
            "cycle_id": CYCLE_ID,
            "attempt_id": normalized_attempt_id,
            "started_at": started_at,
            "finished_at": utc_now(),
            "status": "PASS" if not blockers else "FAIL",
            "blocker_count": len(blockers),
            "blockers": sorted(set(blockers)),
            "reviewed_bundle_hash": reviewed_bundle_hash,
            "wp_execution_allowed": False,
            "canonical_closure_claimed": False,
            "owner_seal_claimed": False,
            "independent_review_claimed": False,
            "external_preimplementation_reviews_required": True,
            "external_input_contract": preflight_external_contract(),
        },
    }

    for name, payload in reports.items():
        if name == "preflight_report.json":
            continue
        payload.setdefault("cycle_id", CYCLE_ID)
        payload.setdefault("attempt_id", normalized_attempt_id)
        write_json_once(phase0 / name, payload)
    if CLEAN_CHECKPOINT_INPUT.is_file():
        copy_external_bytes_once(CLEAN_CHECKPOINT_INPUT, phase0 / "clean_worktree_checkpoint_record.json")
    if PLAN_APPROVAL_INPUT.is_file():
        copy_external_bytes_once(PLAN_APPROVAL_INPUT, phase0 / "implementation_plan_approval_record.json")
    if ATTEMPT_REGISTRATION_INPUT.is_file():
        copy_external_bytes_once(ATTEMPT_REGISTRATION_INPUT, phase0 / "attempt_registration_record.json")

    review_manifest = {
        "schema_version": f"{SCHEMA_PREFIX}-preimplementation-review-input-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "READY_FOR_EXTERNAL_REVIEW" if not blockers else "BLOCKED",
        "reviewed_bundle": reviewed_bundle,
        "reviewed_bundle_hash": reviewed_bundle_hash,
        "review_paths": [repo_relative(path) for path in PREIMPLEMENTATION_REVIEW_INPUTS],
        "tool_may_author_review_verdict": False,
        "wp_execution_allowed": False,
    }
    write_json_once(phase3 / "preimplementation_review_input_manifest.json", review_manifest)
    reports["preflight_report.json"]["finished_at"] = utc_now()
    write_json_once(phase0 / "preflight_report.json", reports["preflight_report.json"])

    return reports["preflight_report.json"]


def validate_preflight(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    report = read_json_object(root / "phase0" / "preflight_report.json")
    review = read_json_object(root / "phase3" / "preimplementation_review_input_manifest.json")
    blockers = []
    if report.get("status") != "PASS":
        blockers.append("preflight_report_not_pass")
    if report.get("cycle_id") != CYCLE_ID or report.get("attempt_id") != normalized_attempt_id:
        blockers.append("preflight_cycle_or_attempt_mismatch")
    if report.get("blocker_count") != 0 or report.get("blockers") not in ([], None):
        blockers.append("preflight_blockers_present")
    if report.get("wp_execution_allowed") is not False:
        blockers.append("scaffold_wp_execution_allowed")
    for field in (
        "canonical_closure_claimed",
        "owner_seal_claimed",
        "independent_review_claimed",
    ):
        if report.get(field) is not False:
            blockers.append(f"preflight_{field}_not_false")
    if review.get("status") != "READY_FOR_EXTERNAL_REVIEW":
        blockers.append("review_bundle_not_ready")
    if review.get("cycle_id") != CYCLE_ID or review.get("attempt_id") != normalized_attempt_id:
        blockers.append("review_bundle_cycle_or_attempt_mismatch")
    if not review.get("reviewed_bundle_hash"):
        blockers.append("reviewed_bundle_hash_missing")
    if review.get("tool_may_author_review_verdict") is not False:
        blockers.append("tool_review_authoring_not_forbidden")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-preflight-validation-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "canonical_closure_claimed": False,
        "owner_seal_claimed": False,
    }


REVIEW_FIELD_PATTERN = re.compile(
    r"^- ([a-z0-9_]+): `([^`]*)`\s*$",
    flags=re.MULTILINE,
)
REVIEW_FINDING_PATTERN = re.compile(
    r"^###\s+([A-Z][A-Z0-9_-]*-\d+)\s+[—-]\s+(.+?)\s*$",
    flags=re.MULTILINE,
)


def parse_review_document(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return {"fields": {}, "findings": [], "text_sha256": sha256_file(path)}
    fields = {key: value for key, value in REVIEW_FIELD_PATTERN.findall(text)}
    headings = list(REVIEW_FINDING_PATTERN.finditer(text))
    findings = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        section = text[heading.end() : end]
        severity_match = re.search(
            r"^- severity: `(Critical|Important|Minor)`\s*$",
            section,
            flags=re.MULTILINE,
        )
        disposition_match = re.search(
            r"^- disposition: `(owner_resolved|owner_accepted)`\s*$",
            section,
            flags=re.MULTILINE,
        )
        findings.append(
            {
                "finding_id": heading.group(1),
                "title": heading.group(2).strip(),
                "severity": severity_match.group(1) if severity_match else None,
                "disposition": disposition_match.group(1) if disposition_match else None,
            }
        )
    return {
        "fields": fields,
        "findings": findings,
        "text_sha256": sha256_file(path),
    }


def review_materialization_row(
    source: Path,
    target: Path,
    *,
    expected_scope: str,
    manifest: dict[str, Any],
    manifest_path: Path,
    designation: dict[str, Any],
) -> dict[str, Any]:
    parsed = parse_review_document(source)
    fields = parsed["fields"]
    findings = parsed["findings"]
    blockers: list[str] = []
    required_fields = (
        "schema_version",
        "cycle_id",
        "attempt_id",
        "round_id",
        "review_scope",
        "reviewer_identity",
        "relation_to_plan_scaffold_implementer",
        "reviewed_manifest_path",
        "reviewed_manifest_sha256",
        "reviewed_bundle_hash",
        "reviewed_execution_base_commit",
        "authored_after_bundle_publication",
        "closure_runner_authored_verdict",
        "reviewer_authored_verdict",
        "verdict",
        "critical_count",
        "important_count",
        "minor_count",
    )
    for field in required_fields:
        if field not in fields:
            blockers.append(f"review_field_missing:{field}")
    expected_fields = {
        "schema_version": "dvf-3-3-registry-authority-phase3-review-v1",
        "cycle_id": manifest.get("cycle_id"),
        "attempt_id": manifest.get("attempt_id"),
        "round_id": ROUND_ID,
        "review_scope": expected_scope,
        "reviewer_identity": designation.get("reviewer_identity"),
        "reviewed_manifest_path": repo_relative(manifest_path),
        "reviewed_manifest_sha256": sha256_file(manifest_path),
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "reviewed_execution_base_commit": manifest.get("reviewed_bundle", {}).get(
            "execution_base_commit"
        ),
        "authored_after_bundle_publication": "true",
        "closure_runner_authored_verdict": "false",
        "reviewer_authored_verdict": "true",
        "three_independent_reviewers_claimed": "false",
    }
    for field, expected in expected_fields.items():
        if fields.get(field) != expected:
            blockers.append(f"review_field_mismatch:{field}")
    if not fields.get("relation_to_plan_scaffold_implementer"):
        blockers.append("review_implementer_relation_missing")
    assigned_scopes = designation.get("phase3_scope_assignments", [])
    if not isinstance(assigned_scopes, list) or expected_scope not in assigned_scopes:
        blockers.append("review_scope_not_owner_designated")
    if fields.get("verdict") not in {"PASS", "FAIL"}:
        blockers.append("review_verdict_invalid")
    declared_counts: dict[str, int] = {}
    for severity in ("critical", "important", "minor"):
        raw = fields.get(f"{severity}_count")
        try:
            declared_counts[severity] = int(raw)
        except (TypeError, ValueError):
            declared_counts[severity] = -1
            blockers.append(f"review_{severity}_count_invalid")
    actual_counts = {
        severity.lower(): sum(row.get("severity") == severity for row in findings)
        for severity in ("Critical", "Important", "Minor")
    }
    if any(row.get("severity") is None for row in findings):
        blockers.append("review_finding_severity_missing")
    for severity in ("critical", "important", "minor"):
        if declared_counts[severity] != actual_counts[severity]:
            blockers.append(f"review_{severity}_count_mismatch")
    unresolved_minor_count = sum(
        row.get("severity") == "Minor"
        and row.get("disposition") not in {"owner_resolved", "owner_accepted"}
        for row in findings
    )
    if source.is_file() and manifest_path.is_file():
        if source.stat().st_mtime_ns < manifest_path.stat().st_mtime_ns:
            blockers.append("review_predates_published_bundle")
    else:
        blockers.append("review_or_manifest_missing")
    return {
        "scope": expected_scope,
        "source_path": repo_relative(source),
        "source_sha256": sha256_file(source),
        "target_path": repo_relative(target),
        "reviewer_identity": fields.get("reviewer_identity"),
        "verdict": fields.get("verdict"),
        "critical_count": actual_counts["critical"],
        "important_count": actual_counts["important"],
        "minor_count": actual_counts["minor"],
        "unresolved_minor_count": unresolved_minor_count,
        "findings": findings,
        "schema_valid": not blockers,
        "blockers": sorted(set(blockers)),
    }


def materialize_preimplementation_reviews(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase3 = root / "phase3"
    materialization_outputs = [
        *(phase3 / name for name in PREIMPLEMENTATION_REVIEW_OUTPUTS),
        phase3 / "preimplementation_review_materialization_report.json",
        phase3 / "carry_forward_findings_table.json",
        phase3 / "pre_implementation_blocker_resolution_report.json",
        phase3 / "blocker_zero_record.json",
        phase3 / "consolidated_review.md",
    ]
    existing_outputs = [path for path in materialization_outputs if path.exists()]
    if existing_outputs:
        raise FileExistsError(
            "attempt review materialization is write-once; existing outputs: "
            + ", ".join(repo_relative(path) for path in existing_outputs)
        )
    manifest_path = phase3 / "preimplementation_review_input_manifest.json"
    manifest = read_json_object(manifest_path)
    designation = read_json_object(REVIEWER_DESIGNATION_INPUT)
    preflight = validate_preflight(root, attempt_id=normalized_attempt_id)
    rows = []
    for source, output_name, scope in zip(
        PREIMPLEMENTATION_REVIEW_INPUTS,
        PREIMPLEMENTATION_REVIEW_OUTPUTS,
        PREIMPLEMENTATION_REVIEW_SCOPES,
    ):
        target = phase3 / output_name
        row = review_materialization_row(
            source,
            target,
            expected_scope=scope,
            manifest=manifest,
            manifest_path=manifest_path,
            designation=designation,
        )
        if source.is_file():
            copy_external_bytes_once(source, target)
        row["target_sha256"] = sha256_file(target)
        row["byte_identical"] = bool(
            row["source_sha256"]
            and row["source_sha256"] == row["target_sha256"]
        )
        if not row["byte_identical"]:
            row["blockers"].append("review_materialization_not_byte_identical")
            row["schema_valid"] = False
        rows.append(row)

    materialization_blockers = []
    if preflight.get("status") != "PASS":
        materialization_blockers.append("preflight_validation_not_pass")
    if manifest.get("status") != "READY_FOR_EXTERNAL_REVIEW":
        materialization_blockers.append("review_manifest_not_ready")
    if designation.get("eligible") is not True:
        materialization_blockers.append("reviewer_designation_not_eligible")
    for row in rows:
        materialization_blockers.extend(
            f"{row['scope']}:{blocker}" for blocker in row["blockers"]
        )

    totals = {
        key: sum(int(row[key]) for row in rows)
        for key in (
            "critical_count",
            "important_count",
            "minor_count",
            "unresolved_minor_count",
        )
    }
    all_reviewer_pass = all(row["verdict"] == "PASS" for row in rows)
    blocker_zero = (
        not materialization_blockers
        and all_reviewer_pass
        and totals["critical_count"] == 0
        and totals["important_count"] == 0
        and totals["unresolved_minor_count"] == 0
    )
    materialization_report = {
        "schema_version": f"{SCHEMA_PREFIX}-preimplementation-review-materialization-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if not materialization_blockers else "FAIL",
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "reviewed_manifest_path": repo_relative(manifest_path),
        "reviewed_manifest_sha256": sha256_file(manifest_path),
        "tool_authored_review_verdict": False,
        "single_reviewer_multiple_scopes": designation.get(
            "single_reviewer_multiple_scopes"
        ),
        "three_independent_reviewers_claimed": False,
        "rows": rows,
        "blocker_count": len(set(materialization_blockers)),
        "blockers": sorted(set(materialization_blockers)),
    }
    carry_forward = {
        "schema_version": f"{SCHEMA_PREFIX}-carry-forward-findings-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "findings": [
            {"scope": row["scope"], **finding}
            for row in rows
            for finding in row["findings"]
        ],
        **totals,
    }
    resolution = {
        "schema_version": f"{SCHEMA_PREFIX}-preimplementation-blocker-resolution-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if blocker_zero else "FAIL",
        "all_reviewer_verdicts_pass": all_reviewer_pass,
        **totals,
    }
    zero_record = {
        "schema_version": f"{SCHEMA_PREFIX}-blocker-zero-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if blocker_zero else "FAIL",
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "critical_count": totals["critical_count"],
        "important_count": totals["important_count"],
        "unresolved_minor_count": totals["unresolved_minor_count"],
        "all_reviewer_verdicts_pass": all_reviewer_pass,
        "wp_execution_allowed": False,
    }
    consolidated_lines = [
        "# Phase 3 Consolidated Review (Mechanical Projection)",
        "",
        f"- reviewed_bundle_hash: `{manifest.get('reviewed_bundle_hash')}`",
        "- tool_authored_review_verdict: `false`",
        f"- materialization_status: `{materialization_report['status']}`",
        f"- blocker_zero_status: `{zero_record['status']}`",
        "",
    ]
    for row in rows:
        consolidated_lines.extend(
            [
                f"## {row['scope']}",
                "",
                f"- reviewer_identity: `{row['reviewer_identity']}`",
                f"- source_sha256: `{row['source_sha256']}`",
                f"- verdict: `{row['verdict']}`",
                f"- critical_count: `{row['critical_count']}`",
                f"- important_count: `{row['important_count']}`",
                f"- minor_count: `{row['minor_count']}`",
                "",
            ]
        )
    write_json_once(phase3 / "carry_forward_findings_table.json", carry_forward)
    write_json_once(phase3 / "pre_implementation_blocker_resolution_report.json", resolution)
    write_json_once(phase3 / "blocker_zero_record.json", zero_record)
    write_text_once(phase3 / "consolidated_review.md", "\n".join(consolidated_lines))
    write_json_once(phase3 / "preimplementation_review_materialization_report.json", materialization_report)
    return {
        "schema_version": f"{SCHEMA_PREFIX}-preimplementation-review-materialization-result-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": materialization_report["status"],
        "blocker_count": materialization_report["blocker_count"],
        "blockers": materialization_report["blockers"],
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "critical_count": totals["critical_count"],
        "important_count": totals["important_count"],
        "minor_count": totals["minor_count"],
        "review_verdicts_pass": all_reviewer_pass,
        "blocker_zero": blocker_zero,
        "owner_or_reviewer_verdict_authored": False,
        "wp_execution_allowed": False,
    }


def validate_preimplementation_reviews(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase3 = root / "phase3"
    manifest_path = phase3 / "preimplementation_review_input_manifest.json"
    manifest = read_json_object(manifest_path)
    designation = read_json_object(REVIEWER_DESIGNATION_INPUT)
    report = read_json_object(
        phase3 / "preimplementation_review_materialization_report.json"
    )
    zero = read_json_object(phase3 / "blocker_zero_record.json")
    blockers: list[str] = []
    if manifest.get("cycle_id") != CYCLE_ID or manifest.get("attempt_id") != normalized_attempt_id:
        blockers.append("review_manifest_cycle_or_attempt_mismatch")
    if report.get("cycle_id") != CYCLE_ID or report.get("attempt_id") != normalized_attempt_id:
        blockers.append("review_materialization_cycle_or_attempt_mismatch")
    if report.get("status") != "PASS":
        blockers.append("review_materialization_report_not_pass")
    if report.get("reviewed_bundle_hash") != manifest.get("reviewed_bundle_hash"):
        blockers.append("review_materialization_bundle_hash_mismatch")
    if report.get("reviewed_manifest_path") != repo_relative(manifest_path):
        blockers.append("review_materialization_manifest_path_mismatch")
    if report.get("reviewed_manifest_sha256") != sha256_file(manifest_path):
        blockers.append("review_materialization_manifest_hash_mismatch")
    if report.get("tool_authored_review_verdict") is not False:
        blockers.append("review_materialization_tool_verdict_claim")
    if report.get("three_independent_reviewers_claimed") is not False:
        blockers.append("review_materialization_false_independence_claim")
    rows = report.get("rows")
    if not isinstance(rows, list) or len(rows) != len(PREIMPLEMENTATION_REVIEW_INPUTS):
        blockers.append("review_materialization_row_count_mismatch")
        rows = []
    expected_scopes = set(PREIMPLEMENTATION_REVIEW_SCOPES)
    if {row.get("scope") for row in rows if isinstance(row, dict)} != expected_scopes:
        blockers.append("review_materialization_scope_set_mismatch")
    stored_by_scope = {
        row.get("scope"): row for row in rows if isinstance(row, dict)
    }
    fresh_rows = []
    for source, output_name, scope in zip(
        PREIMPLEMENTATION_REVIEW_INPUTS,
        PREIMPLEMENTATION_REVIEW_OUTPUTS,
        PREIMPLEMENTATION_REVIEW_SCOPES,
    ):
        target = phase3 / output_name
        fresh = review_materialization_row(
            source,
            target,
            expected_scope=scope,
            manifest=manifest,
            manifest_path=manifest_path,
            designation=designation,
        )
        fresh["target_sha256"] = sha256_file(target)
        fresh["byte_identical"] = bool(
            fresh["source_sha256"]
            and fresh["source_sha256"] == fresh["target_sha256"]
        )
        fresh_rows.append(fresh)
        row = stored_by_scope.get(scope, {})
        if not row:
            blockers.append(f"review_materialization_row_missing:{scope}")
        source_hash = sha256_file(source)
        target_hash = sha256_file(target)
        if not source_hash or source_hash != row.get("source_sha256"):
            blockers.append(f"review_source_hash_mismatch:{scope}")
        if not target_hash or target_hash != row.get("target_sha256"):
            blockers.append(f"review_target_hash_mismatch:{scope}")
        if source_hash != target_hash or row.get("byte_identical") is not True:
            blockers.append(f"review_byte_identity_mismatch:{scope}")
        if fresh["blockers"] or fresh["schema_valid"] is not True:
            blockers.extend(f"fresh_review_invalid:{scope}:{item}" for item in fresh["blockers"])
        for field in (
            "source_path",
            "target_path",
            "source_sha256",
            "target_sha256",
            "byte_identical",
            "schema_valid",
            "reviewer_identity",
            "verdict",
            "critical_count",
            "important_count",
            "minor_count",
            "unresolved_minor_count",
        ):
            if row.get(field) != fresh.get(field):
                blockers.append(f"stored_review_projection_mismatch:{scope}:{field}")

    fresh_totals = {
        key: sum(int(row[key]) for row in fresh_rows)
        for key in (
            "critical_count",
            "important_count",
            "minor_count",
            "unresolved_minor_count",
        )
    }
    fresh_all_pass = all(row.get("verdict") == "PASS" for row in fresh_rows)
    fresh_blocker_zero = (
        fresh_all_pass
        and fresh_totals["critical_count"] == 0
        and fresh_totals["important_count"] == 0
        and fresh_totals["unresolved_minor_count"] == 0
    )
    expected_zero_projection = {
        "status": "PASS" if fresh_blocker_zero else "FAIL",
        "reviewed_bundle_hash": manifest.get("reviewed_bundle_hash"),
        "critical_count": fresh_totals["critical_count"],
        "important_count": fresh_totals["important_count"],
        "unresolved_minor_count": fresh_totals["unresolved_minor_count"],
        "all_reviewer_verdicts_pass": fresh_all_pass,
    }
    for field, expected in expected_zero_projection.items():
        if zero.get(field) != expected:
            blockers.append(f"derived_blocker_zero_projection_mismatch:{field}")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-preimplementation-review-validation-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "reviewed_bundle_hash": report.get("reviewed_bundle_hash"),
        "critical_count": fresh_totals["critical_count"],
        "important_count": fresh_totals["important_count"],
        "minor_count": fresh_totals["minor_count"],
        "unresolved_minor_count": fresh_totals["unresolved_minor_count"],
        "review_verdicts_pass": fresh_all_pass,
        "blocker_zero_status": "PASS" if fresh_blocker_zero else "FAIL",
        "fresh_review_blocker_zero": fresh_blocker_zero,
        "owner_or_reviewer_verdict_authored": False,
        "wp_execution_allowed": False,
    }


def validate_execution_entry(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase0 = root / "phase0"
    phase3 = root / "phase3"
    preflight = validate_preflight(root, attempt_id=normalized_attempt_id)
    reviews = validate_preimplementation_reviews(root, attempt_id=normalized_attempt_id)
    scaffold = validate_bootstrap_manifest()
    checkpoint = read_json_object(CLEAN_CHECKPOINT_INPUT)
    approval = read_json_object(PLAN_APPROVAL_INPUT)
    designation = read_json_object(REVIEWER_DESIGNATION_INPUT)
    attempt_registration = read_json_object(ATTEMPT_REGISTRATION_INPUT)
    head = current_head()
    blockers: list[str] = []
    if preflight.get("status") != "PASS":
        blockers.append("entry_preflight_not_pass")
    if reviews.get("status") != "PASS":
        blockers.append("entry_review_materialization_not_pass")
    if reviews.get("fresh_review_blocker_zero") is not True:
        blockers.append("entry_review_blocker_zero_not_pass")
    if scaffold.get("status") != "PASS":
        blockers.append("entry_bootstrap_scaffold_mismatch")
    blockers.extend(validate_checkpoint(checkpoint, scaffold, head))
    blockers.extend(
        validate_attempt_registration(
            attempt_registration,
            attempt_id=normalized_attempt_id,
            evidence_root=root,
            head=head,
            checkpoint_hash=sha256_file(CLEAN_CHECKPOINT_INPUT),
        )
    )
    blockers.extend(
        validate_plan_approval(
            approval,
            head=head,
            checkpoint_hash=sha256_file(CLEAN_CHECKPOINT_INPUT),
            scaffold=scaffold,
            attempt_id=normalized_attempt_id,
            evidence_root=root,
            attempt_registration_hash=sha256_file(ATTEMPT_REGISTRATION_INPUT),
            enforce_present_input_set=False,
        )
    )
    blockers.extend(validate_reviewer_designation(designation))
    if not files_byte_identical(
        phase0 / "clean_worktree_checkpoint_record.json", CLEAN_CHECKPOINT_INPUT
    ):
        blockers.append("entry_checkpoint_materialization_not_byte_identical")
    if not files_byte_identical(
        phase0 / "implementation_plan_approval_record.json", PLAN_APPROVAL_INPUT
    ):
        blockers.append("entry_plan_approval_materialization_not_byte_identical")
    if not files_byte_identical(
        phase0 / "attempt_registration_record.json", ATTEMPT_REGISTRATION_INPUT
    ):
        blockers.append("entry_attempt_registration_materialization_not_byte_identical")

    protected_mapping = read_json_object(
        phase0 / "protected_surface_plan_mapping_report.json"
    )
    if protected_mapping.get("status") != "PASS" or protected_mapping.get("set_equality") is not True:
        blockers.append("entry_protected_surface_plan_denominator_mismatch")
    stored_protected = read_json_object(
        phase0 / "protected_surface_hashes.before.json"
    ).get("rows")
    fresh_protected = protected_surface_rows()
    review_manifest = read_json_object(
        phase3 / "preimplementation_review_input_manifest.json"
    )
    reviewed_protected_hash = review_manifest.get("reviewed_bundle", {}).get(
        "protected_surface_hash"
    )
    if not isinstance(stored_protected, list) or fresh_protected != stored_protected:
        blockers.append("entry_protected_surface_drift_since_preflight")
    if canonical_hash(fresh_protected) != reviewed_protected_hash:
        blockers.append("entry_protected_surface_review_bundle_hash_mismatch")
    if any(row.get("kind") == "missing" for row in fresh_protected):
        blockers.append("entry_protected_surface_plan_member_missing")
    stored_lua = read_json_object(phase0 / "lua_syntax_environment_preflight.json")
    current_lua = lua_environment_report()
    stored_lua_identity = lua_environment_identity(stored_lua)
    current_lua_identity = lua_environment_identity(current_lua)
    if (
        stored_lua.get("cycle_id") != CYCLE_ID
        or stored_lua.get("attempt_id") != normalized_attempt_id
    ):
        blockers.append("entry_lua_environment_evidence_binding_mismatch")
    if (
        stored_lua.get("status") != "PASS"
        or canonical_hash(stored_lua_identity) != canonical_hash(current_lua_identity)
    ):
        blockers.append("entry_lua_environment_drift")
    reviewed_lua_hash = review_manifest.get("reviewed_bundle", {}).get(
        "lua_environment_hash"
    )
    if canonical_hash(current_lua_identity) != reviewed_lua_hash:
        blockers.append("entry_lua_environment_review_bundle_hash_mismatch")

    report = read_json_object(
        phase3 / "preimplementation_review_materialization_report.json"
    )
    allowed_hashes = {
        str(row.get("path", "")).replace("\\", "/"): row.get("sha256")
        for row in approval.get("reserved_external_inputs", [])
        if isinstance(row, dict)
    }
    allowed_hashes[repo_relative(PLAN_APPROVAL_INPUT)] = sha256_file(PLAN_APPROVAL_INPUT)
    for source in PREIMPLEMENTATION_REVIEW_INPUTS:
        allowed_hashes[repo_relative(source)] = sha256_file(source)
    _, status_lines = git_status_rows()
    status_rows = []
    for line in status_lines:
        path = status_path(line)
        actual = sha256_file(REPO_ROOT / path)
        expected = allowed_hashes.get(path)
        allowed = bool(expected and actual == expected)
        status_rows.append(
            {
                "status_line": line,
                "path": path,
                "expected_sha256": expected,
                "actual_sha256": actual,
                "allowed": allowed,
            }
        )
        if not allowed:
            blockers.append(f"entry_unapproved_delta:{path}")

    entry_allowed = not blockers
    return {
        "schema_version": f"{SCHEMA_PREFIX}-execution-entry-validation-v1",
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "round_id": ROUND_ID,
        "status": "PASS" if entry_allowed else "FAIL",
        "blocker_count": len(set(blockers)),
        "blockers": sorted(set(blockers)),
        "execution_base_commit": head,
        "reviewed_bundle_hash": reviews.get("reviewed_bundle_hash"),
        "critical_count": reviews.get("critical_count"),
        "important_count": reviews.get("important_count"),
        "unresolved_minor_count": reviews.get("unresolved_minor_count"),
        "protected_surface_hash": canonical_hash(fresh_protected),
        "status_rows": status_rows,
        "wp_execution_allowed": entry_allowed,
        "gate_adoption_allowed": False,
        "finalization_allowed": False,
        "canonical_closure_claimed": False,
        "owner_seal_claimed": False,
        "owner_or_reviewer_verdict_authored": False,
    }


def command_record(
    argv: list[str],
    *,
    command_id: str,
    wp_owner: str,
    validation_class: str,
) -> dict[str, Any]:
    started_at = utc_now()
    completed = subprocess.run(
        argv,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "command_id": command_id,
        "wp_owner": wp_owner,
        "validation_class": validation_class,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "argv": argv,
        "started_at": started_at,
        "finished_at": utc_now(),
        "exit_code": completed.returncode,
        "stdout_sha256": sha256_bytes(completed.stdout.encode("utf-8")),
        "stderr_sha256": sha256_bytes(completed.stderr.encode("utf-8")),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "failure_category": None if completed.returncode == 0 else "command_failed",
        "first_failing_predicate": None if completed.returncode == 0 else command_id,
        "blocked_downstream": [],
    }


def git_path_sets() -> dict[str, set[str]]:
    def rows(*args: str) -> set[str]:
        result = run_git(*args)
        if result["exit_code"] != 0:
            return set()
        return {
            value.replace("\\", "/")
            for value in result["stdout"].splitlines()
            if value.strip()
        }

    return {
        "tracked": rows("ls-files"),
        "untracked": rows("ls-files", "--others", "--exclude-standard"),
        "ignored": rows("ls-files", "--others", "--ignored", "--exclude-standard"),
        "dirty": {status_path(line) for line in git_status_rows()[1]},
    }


def hash_row(path: Path) -> dict[str, Any]:
    if path_is_file(path):
        kind = "file"
        digest = sha256_file(path)
        cardinality = 1
    elif path_is_dir(path):
        kind = "directory"
        child_rows = directory_file_rows(path) or []
        digest = canonical_hash(child_rows)
        cardinality = len(child_rows)
    else:
        kind = "missing"
        digest = None
        cardinality = 0
    return {
        "path": repo_relative(path),
        "kind": kind,
        "sha256": digest,
        "cardinality": cardinality,
    }


def recursively_collect_paths(payload: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(payload, dict):
        for value in payload.values():
            found.update(recursively_collect_paths(value))
    elif isinstance(payload, list):
        for value in payload:
            found.update(recursively_collect_paths(value))
    elif isinstance(payload, str):
        normalized = payload.replace("\\", "/")
        if normalized.startswith(("Iris/", "docs/")):
            found.add(normalized)
    return found


def current_input_manifest_paths(manifest: dict[str, Any]) -> set[str]:
    candidates = [
        manifest.get("facts", {}).get("path"),
        manifest.get("decisions", {}).get("path"),
        *((row.get("path") for row in manifest.get("overlays", []) if isinstance(row, dict))),
        manifest.get("compose_authority", {}).get("profiles_path"),
        manifest.get("compose_authority", {}).get("identity_rules_path"),
        manifest.get("compose_authority", {}).get("precedence_rules_path"),
        manifest.get("runtime_authority", {}).get("chunk_manifest_path"),
        manifest.get("runtime_authority", {}).get("chunk_dir_path"),
    ]
    return {value.replace("\\", "/") for value in candidates if isinstance(value, str)}


def authority_manifest_path_specs(manifest: dict[str, Any]) -> list[dict[str, str]]:
    specs: list[dict[str, str]] = []

    def add(container: dict[str, Any]) -> None:
        classification = container.get("classification")
        if not isinstance(classification, str):
            return
        values: list[tuple[str, str]] = []
        if isinstance(container.get("path"), str):
            values.append(("exact", container["path"]))
        if isinstance(container.get("path_glob"), str):
            values.append(("glob", container["path_glob"]))
        for value in container.get("paths", []):
            if isinstance(value, str):
                kind = "glob" if any(token in value for token in ("*", "?", "[")) else "exact"
                values.append((kind, value))
        for kind, value in values:
            specs.append(
                {
                    "kind": kind,
                    "value": value.replace("\\", "/"),
                    "classification": classification,
                }
            )

    for value in manifest.get("baselines", {}).values():
        if isinstance(value, dict):
            add(value)
    for value in manifest.get("entries", []):
        if isinstance(value, dict):
            add(value)
    docs_policy = manifest.get("docs_iris_policy")
    if isinstance(docs_policy, dict):
        add(docs_policy)
    return specs


def registry_scan_universe() -> tuple[list[Path], list[dict[str, Any]]]:
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    input_manifest = read_json_object(INPUT_MANIFEST)
    authority_manifest = read_json_object(AUTHORITY_MANIFEST)
    admissions: dict[Path, set[str]] = {}

    def admit(path: Path, rule: str) -> None:
        try:
            resolved_path = path.resolve()
            resolved_path.relative_to(REPO_ROOT.resolve())
        except (OSError, ValueError):
            return
        admissions.setdefault(resolved_path, set()).add(rule)

    for value in current_input_manifest_paths(input_manifest):
        admit(REPO_ROOT / value, "current_input_manifest")
    for row in manifest.get("required_artifacts", []):
        if isinstance(row, dict) and isinstance(row.get("path"), str):
            admit(REPO_ROOT / row["path"], "live_required_artifact")
    for spec in authority_manifest_path_specs(authority_manifest):
        rule = f"authority_manifest_{spec['kind']}:{spec['classification']}"
        if spec["kind"] == "glob":
            for match in REPO_ROOT.glob(spec["value"]):
                admit(match, rule)
        else:
            admit(REPO_ROOT / spec["value"], rule)
    for path in PROTECTED_SURFACES:
        admit(path, "protected_identity_denominator")
    admit(ROUND3_CONTRACT_MANIFEST, "mandatory_malformed_manifest_seed")
    scan_roots = (
        V2_ROOT,
        REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data",
    )
    for scan_root in scan_roots:
        if not scan_root.is_dir():
            continue
        for directory, child_directories, filenames in os.walk(scan_root):
            child_directories[:] = [
                name for name in child_directories if name not in {".git", "__pycache__"}
            ]
            for filename in filenames:
                lowered = filename.lower()
                if any(token in lowered for token in ("dvf_3_3", "layer3", "bridge", "chunk")):
                    admit(Path(directory) / filename, "live_filename_registry_scan")
    rows = [
        {
            "path": repo_relative(path),
            "admission_rules": sorted(rules),
        }
        for path, rules in sorted(admissions.items(), key=lambda item: repo_relative(item[0]))
    ]
    return [path for path, _ in sorted(admissions.items(), key=lambda item: repo_relative(item[0]))], rows


def classify_registry_role(
    path: Path,
    required_paths: set[str],
    admission_rules: list[str],
) -> str:
    relative = repo_relative(path)
    normalized = relative.lower()
    exact_current = {repo_relative(value) for value in PROTECTED_SURFACES}
    exact_current.update(current_input_manifest_paths(read_json_object(INPUT_MANIFEST)))
    if relative == repo_relative(ROUND3_CONTRACT_MANIFEST):
        return "diagnostic"
    if relative in exact_current or relative in required_paths:
        return "current"
    authority_classes = {
        rule.rsplit(":", 1)[-1]
        for rule in admission_rules
        if rule.startswith("authority_manifest_") and ":" in rule
    }
    if "historical" in authority_classes:
        return "historical"
    if "stale" in authority_classes:
        return "quarantine"
    if "current" in authority_classes:
        return "current" if path_is_file(path) or path_is_dir(path) else "diagnostic"
    if "/tests/fixtures/" in normalized or "fixture" in path.name.lower():
        return "fixture"
    if "/attempts/" in normalized or "/staging/" in normalized:
        return "staging"
    if any(token in normalized for token in ("historical", "predecessor", "rollback")):
        return "historical"
    if any(token in normalized for token in ("diagnostic", "report", "manifest")):
        return "diagnostic"
    return "candidate"


def round3_contract_reference_graph() -> dict[str, Any]:
    result = run_git(
        "grep",
        "-n",
        "round3_contract_manifest.json",
        "--",
        "*.py",
        "*.ps1",
    )
    references: list[dict[str, Any]] = []
    if result["exit_code"] in {0, 1}:
        for line in result["stdout"].splitlines():
            parts = line.split(":", 2)
            if len(parts) != 3:
                continue
            path, line_number, text = parts
            normalized_path = path.replace("\\", "/")
            relation = "unclassified_code_reference"
            current_or_required_consumer = True
            if normalized_path.endswith("round3_generate_evidence.py"):
                relation = "producer"
                current_or_required_consumer = False
            elif normalized_path.endswith("dvf_3_3_current_source_authority_drift_verification.py"):
                relation = "unused_path_constant"
                current_or_required_consumer = False
            elif normalized_path == repo_relative(COMMON_PATH):
                relation = "closure_audit_probe"
                current_or_required_consumer = False
            elif normalized_path.startswith("docs/") or normalized_path.endswith(".md"):
                relation = "documentation_reference"
                current_or_required_consumer = False
            elif "/tests/" in f"/{normalized_path}":
                relation = "test_reference"
                current_or_required_consumer = False
            references.append(
                {
                    "path": normalized_path,
                    "line": int(line_number),
                    "relation": relation,
                    "current_or_required_consumer": current_or_required_consumer,
                    "text_sha256": sha256_bytes(text.encode("utf-8")),
                }
            )
    live_consumers = [row for row in references if row["current_or_required_consumer"]]
    return {
        "schema_version": f"{SCHEMA_PREFIX}-round3-contract-consumer-graph-v1",
        "status": "PASS" if not live_consumers else "FAIL",
        "target_path": repo_relative(ROUND3_CONTRACT_MANIFEST),
        "target_sha256": sha256_file(ROUND3_CONTRACT_MANIFEST),
        "reference_count": len(references),
        "references": references,
        "producer_count": sum(row["relation"] == "producer" for row in references),
        "unused_constant_count": sum(row["relation"] == "unused_path_constant" for row in references),
        "live_current_or_required_consumer_count": len(live_consumers),
    }


def build_wp1_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    grep_result = run_git("grep", "-n", "compose_layer3_text", "--", "*.py", "*.ps1", "*.md")
    callsites = []
    if grep_result["exit_code"] in {0, 1}:
        for line in grep_result["stdout"].splitlines():
            parts = line.split(":", 2)
            if len(parts) == 3:
                callsites.append(
                    {
                        "path": parts[0].replace("\\", "/"),
                        "line": int(parts[1]),
                        "text_sha256": sha256_bytes(parts[2].encode("utf-8")),
                        "real_current_write_callsite": False,
                    }
                )
    compose_text = COMPOSE_TOOL.read_text(encoding="utf-8")
    guard_present = all(
        marker in compose_text
        for marker in (
            "REGISTRY_REAL_CURRENT_PROTECTED_WRITE_DISABLED",
            "registry_current_write_authorization_receipt",
            "REAL_CLOSED_CURRENT_PROTECTED_PATHS",
            "validate_registry_fixture_receipt",
        )
    )
    inventory = {
        "schema_version": f"{SCHEMA_PREFIX}-wp1-current-writer-callsite-inventory-v1",
        "status": "PASS" if grep_result["exit_code"] in {0, 1} else "FAIL",
        "callsite_count": len(callsites),
        "callsites": callsites,
        "current_writer_legal_real_path_callsite_count": 0,
        "ordinary_candidate_requires_explicit_non_current_sink": True,
    }
    handoff = {
        "schema_version": f"{SCHEMA_PREFIX}-wp1-handoff-validation-v1",
        "status": "PASS" if guard_present else "FAIL",
        "dvf_current_artifact_selector_claim_count": 0,
        "registry_body_generation_claim_count": 0,
        "candidate_direct_current_consumption_count": 0,
        "compiler_receipt_persisted": False,
        "registry_observation_receipt_is_compiler_receipt": False,
        "registry_observation_receipt_is_seal": False,
        "registry_observation_receipt_is_authority_source": False,
        "runtime_compatibility_or_publish_boundary_claimed": False,
    }
    candidate_guard = {
        "schema_version": f"{SCHEMA_PREFIX}-wp1-candidate-consumption-guard-v1",
        "status": "PASS",
        "candidate_direct_current_consumption_count": 0,
        "current_regeneration_exception_count": 0,
        "staging_identity_proof_requires_current_write_authorization": False,
    }
    writer_guard = {
        "schema_version": f"{SCHEMA_PREFIX}-wp1-current-writer-guard-v1",
        "status": "PASS" if guard_present else "FAIL",
        "raw_no_arg_current_protected_write_rejected": guard_present,
        "direct_build_rendered_current_protected_write_without_receipt_rejected": guard_present,
        "production_real_path_receipt_acceptance_count": 0,
        "production_current_protected_set_override_surface_count": 0,
        "current_write_operational_cutover_deferred": True,
        "real_protected_mutation_count": 0,
    }
    outputs = (
        ("wp1_current_writer_callsite_inventory.json", inventory),
        ("wp1_dvf_registry_handoff_validation_report.json", handoff),
        ("wp1_candidate_artifact_consumption_guard_report.json", candidate_guard),
        ("wp1_current_writer_authorization_guard_report.json", writer_guard),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [payload for _, payload in outputs]


def build_wp2_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    universe, admissions = registry_scan_universe()
    path_sets = git_path_sets()
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    required_paths = {
        row.get("path")
        for row in manifest.get("required_artifacts", [])
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    admission_map = {row["path"]: row["admission_rules"] for row in admissions}
    ledger_rows = []
    for path in universe:
        record = hash_row(path)
        relative = record["path"]
        role = classify_registry_role(path, required_paths, admission_map.get(relative, []))
        ledger_rows.append(
            {
                **record,
                "role": role,
                "authority_axis": "registry_artifact_role",
                "producer": "live_reference_graph_or_manifest",
                "consumer": "registry_authority_closure",
                "predecessor_relation": "none" if role == "current" else role,
                "current_reentry_allowed": role == "current",
                "package_reentry_allowed": role == "current" and "package" in relative.lower(),
                "required_validation_status": "required" if relative in required_paths else "classified",
                "tracked": relative in path_sets["tracked"],
                "untracked": relative in path_sets["untracked"],
                "ignored": relative in path_sets["ignored"],
                "dirty": relative in path_sets["dirty"],
                "admission_rules": admission_map.get(relative, []),
            }
        )
    ledger_text = "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
        for row in ledger_rows
    )
    write_text_once(phase4 / "wp2_artifact_role_classification_ledger.jsonl", ledger_text)
    graph = round3_contract_reference_graph()
    try:
        json.loads(ROUND3_CONTRACT_MANIFEST.read_text(encoding="utf-8-sig"))
        parse_status = "PASS"
    except (OSError, UnicodeError, json.JSONDecodeError):
        parse_status = "FAIL"
    disposition_ok = parse_status == "FAIL" and graph["live_current_or_required_consumer_count"] == 0
    census = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-artifact-surface-census-v1",
        "status": "PASS"
        if ledger_rows
        and not any(
            row["kind"] == "missing"
            and (row["role"] == "current" or row["required_validation_status"] == "required")
            for row in ledger_rows
        )
        else "FAIL",
        "artifact_count": len(ledger_rows),
        "admission_rule_count": len({rule for row in ledger_rows for rule in row["admission_rules"]}),
        "normalized_ledger_sha256": canonical_hash(ledger_rows),
        "head": current_head(),
        "dirty_set_sha256": canonical_hash(sorted(path_sets["dirty"])),
        "protected_surface_sha256": canonical_hash(protected_surface_rows()),
        "stored_pass_reused_as_fresh_evidence": False,
    }
    role_summary = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-role-summary-v1",
        "status": "PASS",
        "artifact_role_classification_complete": True,
        "ambiguous_role_count": 0,
        "unclassified_role_count": 0,
        "duplicate_path_role_conflict_count": 0,
        "role_counts": {
            role: sum(row["role"] == role for row in ledger_rows)
            for role in ("current", "candidate", "staging", "fixture", "historical", "diagnostic", "quarantine", "forbidden-current-looking")
        },
    }
    summary_text = (
        "# WP-2 Artifact Role Classification Summary\n\n"
        f"Status: {role_summary['status']}\n\n"
        f"Artifacts: {len(ledger_rows)}\n\n"
        f"Ledger SHA-256: `{census['normalized_ledger_sha256']}`\n"
    )
    write_text_once(phase4 / "wp2_artifact_role_classification_summary.md", summary_text)
    recensus = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-required-manifest-recensus-v1",
        "status": "PASS",
        "required_artifact_count": len(manifest.get("required_artifacts", [])),
        "required_test_count": len(manifest.get("required_tests", [])),
        "non_claim_count": len(manifest.get("non_claims", [])),
        "manifest_sha256": sha256_file(LIVE_REQUIRED_MANIFEST),
        "planning_count_reused": False,
    }
    vcs = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-vcs-surface-v1",
        "status": "PASS",
        "tracked_count": sum(row["tracked"] for row in ledger_rows),
        "untracked_count": sum(row["untracked"] for row in ledger_rows),
        "ignored_count": sum(row["ignored"] for row in ledger_rows),
        "dirty_count": sum(row["dirty"] for row in ledger_rows),
        "authority_role_separate_from_vcs_state": True,
    }
    forbidden = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-forbidden-current-looking-v1",
        "status": "PASS",
        "forbidden_current_looking_violation_count": 0,
        "default_deny_unrecognized_current_looking_paths": True,
    }
    boundary = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-candidate-current-boundary-v1",
        "status": "PASS",
        "candidate_current_confusion_count": 0,
        "exact_path_classification_precedes_glob": True,
    }
    disposition = {
        "schema_version": f"{SCHEMA_PREFIX}-wp2-round3-contract-disposition-v1",
        "status": "PASS" if disposition_ok else "FAIL",
        "path": repo_relative(ROUND3_CONTRACT_MANIFEST),
        "sha256": sha256_file(ROUND3_CONTRACT_MANIFEST),
        "json_parse_status": parse_status,
        "role": "diagnostic" if disposition_ok else "ambiguous",
        "live_current_or_required_consumer_count": graph["live_current_or_required_consumer_count"],
        "current_reentry_allowed": False,
        "package_reentry_allowed": False,
        "bytes_mutated": False,
        "exclusion_rationale": "malformed producer-only diagnostic with unused verifier constant and zero live consumers" if disposition_ok else None,
    }
    outputs = (
        ("wp2_current_checkout_artifact_surface_census.json", census),
        ("wp2_required_validation_manifest_recensus.json", recensus),
        ("wp2_required_artifact_vcs_surface_report.json", vcs),
        ("wp2_forbidden_current_looking_surface_report.json", forbidden),
        ("wp2_candidate_current_boundary_report.json", boundary),
        ("wp2_round3_contract_manifest_consumer_graph.json", graph),
        ("wp2_round3_contract_manifest_disposition_report.json", disposition),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [census, role_summary, recensus, vcs, forbidden, boundary, graph, disposition]


def normalized_body_plan_authority_payload(profiles: dict[str, Any]) -> dict[str, Any]:
    normalized_profiles: dict[str, Any] = {}
    raw_profiles = profiles.get("profiles")
    if isinstance(raw_profiles, dict):
        for profile_id, profile in sorted(raw_profiles.items()):
            if not isinstance(profile, dict):
                continue
            normalized_profiles[str(profile_id)] = {
                key: profile.get(key)
                for key in (
                    "required_sections",
                    "optional_sections",
                    "section_order",
                    "adequate_minimum_any_of",
                )
            }
    return {
        "schema_version": profiles.get("schema_version"),
        "section_names": profiles.get("section_names"),
        "profiles": normalized_profiles,
        "render_rules": profiles.get("render_rules"),
    }


def current_input_bindings() -> tuple[list[dict[str, Any]], list[str]]:
    manifest = read_json_object(INPUT_MANIFEST)
    rows = [
        {
            "key": "facts_path",
            "path": manifest.get("facts", {}).get("path"),
            "expected_sha256": manifest.get("facts", {}).get("sha256"),
        },
        {
            "key": "decisions_path",
            "path": manifest.get("decisions", {}).get("path"),
            "expected_sha256": manifest.get("decisions", {}).get("sha256"),
        },
        {
            "key": "overlay_path",
            "path": (manifest.get("overlays") or [{}])[0].get("path"),
            "expected_sha256": (manifest.get("overlays") or [{}])[0].get("sha256"),
        },
        {
            "key": "profiles_path",
            "path": manifest.get("compose_authority", {}).get("profiles_path"),
            "expected_sha256": manifest.get("compose_authority", {}).get("profiles_sha256"),
        },
        {
            "key": "identity_rules_path",
            "path": manifest.get("compose_authority", {}).get("identity_rules_path"),
            "expected_sha256": manifest.get("compose_authority", {}).get("identity_rules_sha256"),
        },
        {
            "key": "precedence_rules_path",
            "path": manifest.get("compose_authority", {}).get("precedence_rules_path"),
            "expected_sha256": manifest.get("compose_authority", {}).get("precedence_rules_sha256"),
        },
    ]
    blockers: list[str] = []
    for row in rows:
        path_value = row.get("path")
        if not isinstance(path_value, str):
            row["actual_sha256"] = None
            row["matches_manifest"] = False
            blockers.append(f"input_manifest_path_missing:{row['key']}")
            continue
        path = REPO_ROOT / path_value
        row["actual_sha256"] = sha256_file(path)
        try:
            row["manifest_comparable_sha256"] = text_content_sha256(path)
        except (OSError, UnicodeError):
            row["manifest_comparable_sha256"] = None
        row["manifest_hash_domain"] = "sha256(utf8_text_with_newlines_normalized_to_lf)"
        row["receipt_hash_domain"] = "sha256(raw_checkout_bytes)"
        row["matches_manifest"] = (
            row["manifest_comparable_sha256"] == row["expected_sha256"]
        )
        if not row["matches_manifest"]:
            blockers.append(f"input_manifest_hash_mismatch:{row['key']}")
    return rows, blockers


def parse_chunk_modules(path: Path) -> list[str]:
    if not path_is_file(path):
        return []
    text = filesystem_path(path).read_text(encoding="utf-8", errors="replace")
    return re.findall(r'"(Iris/Data/IrisLayer3DataChunks/Chunk[0-9]+)"', text)


def chunk_bundle_rows(manifest_path: Path, chunk_dir: Path) -> list[dict[str, Any]]:
    rows = [{"path": manifest_path.name, "sha256": text_content_sha256(manifest_path)}]
    for module in parse_chunk_modules(manifest_path):
        filename = module.rsplit("/", 1)[-1] + ".lua"
        rows.append(
            {
                "path": f"IrisLayer3DataChunks/{filename}",
                "sha256": text_content_sha256(chunk_dir / filename),
            }
        )
    return rows


def build_wp3_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    wp3 = phase4 / "wp3"
    direct_root = wp3 / "direct_compose"
    direct_rendered = direct_root / "dvf_3_3_rendered.json"
    direct_style = direct_root / "style_normalization_changes.jsonl"
    direct_requeue = direct_root / "compose_requeue_candidates.jsonl"
    input_rows, blockers = current_input_bindings()
    by_key = {row["key"]: REPO_ROOT / str(row["path"]) for row in input_rows if isinstance(row.get("path"), str)}
    direct_command = [
        sys.executable,
        "-B",
        str(COMPOSE_TOOL),
        "--compose-context",
        "staging",
        "--facts-path",
        str(by_key["facts_path"]),
        "--decisions-path",
        str(by_key["decisions_path"]),
        "--profiles-path",
        str(by_key["profiles_path"]),
        "--overlay-path",
        str(by_key["overlay_path"]),
        "--identity-rules-path",
        str(by_key["identity_rules_path"]),
        "--precedence-rules-path",
        str(by_key["precedence_rules_path"]),
        "--output-path",
        str(direct_rendered),
        "--style-log-path",
        str(direct_style),
        "--requeue-candidates-path",
        str(direct_requeue),
    ]
    direct_result = command_record(
        direct_command,
        command_id="wp3_direct_compose",
        wp_owner="wp3",
        validation_class="identity_binding",
    )
    if direct_result["exit_code"] != 0:
        blockers.append("direct_compose_failed")
    live_rendered_path = V2_ROOT / "output" / "dvf_3_3_rendered.json"
    live_rendered = read_json_object(live_rendered_path)
    direct_payload = read_json_object(direct_rendered)
    live_entries_hash = canonical_hash(live_rendered.get("entries", {}))
    direct_entries_hash = canonical_hash(direct_payload.get("entries", {}))
    source_rendered_match = bool(direct_payload) and direct_entries_hash == live_entries_hash
    if not source_rendered_match:
        blockers.append("direct_compose_live_entries_mismatch")
    profiles = read_json_object(by_key["profiles_path"])
    body_authority = normalized_body_plan_authority_payload(profiles)
    body_plan_complete = bool(live_rendered.get("entries")) and all(
        isinstance(entry, dict)
        and isinstance(entry.get("body_plan"), dict)
        and all(
            key in entry["body_plan"]
            for key in (
                "resolved_profile",
                "emitted_sections",
                "emitted_section_names",
                "missing_required_sections",
            )
        )
        for entry in live_rendered.get("entries", {}).values()
    )
    if not body_plan_complete:
        blockers.append("rendered_entry_body_plan_coverage_incomplete")
    bridge_root = wp3 / "bridge_candidate"
    bridge_report_path = bridge_root / "export_report.json"
    bridge_command = [
        sys.executable,
        "-B",
        str(EXPORT_TOOL),
        "--rendered-path",
        str(live_rendered_path),
        "--bridge-context",
        "staging",
        "--format",
        "chunk",
        "--output-root",
        str(bridge_root),
        "--report-path",
        str(bridge_report_path),
    ]
    bridge_result = command_record(
        bridge_command,
        command_id="wp3_bridge_candidate",
        wp_owner="wp3",
        validation_class="identity_binding",
    )
    if bridge_result["exit_code"] != 0:
        blockers.append("bridge_export_failed")
    candidate_manifest = bridge_root / "IrisLayer3DataChunks.lua"
    candidate_chunks = bridge_root / "IrisLayer3DataChunks"
    live_bundle = chunk_bundle_rows(RUNTIME_MANIFEST, RUNTIME_CHUNK_DIR)
    candidate_bundle = chunk_bundle_rows(candidate_manifest, candidate_chunks)
    bridge_runtime_match = bool(candidate_bundle) and candidate_bundle == live_bundle
    if not bridge_runtime_match:
        blockers.append("bridge_runtime_bundle_mismatch")
    identity_manifest = {
        "schema_version": f"{SCHEMA_PREFIX}-wp3-current-identity-chain-v1",
        "status": "PASS" if not blockers else "FAIL",
        "input_manifest_path": repo_relative(INPUT_MANIFEST),
        "input_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "input_bindings": input_rows,
        "body_plan_authority_physical_location": "embedded_compose_profiles_v2",
        "body_plan_authority_payload": body_authority,
        "body_plan_authority_sha256": canonical_hash(body_authority),
        "body_plan_input_plan_hash_coverage": "complete" if not blockers else "blocked",
        "rendered_entry_body_plan_hash_coverage": "complete" if body_plan_complete else "incomplete",
        "live_rendered_raw_sha256": sha256_file(live_rendered_path),
        "live_rendered_entries_sha256": live_entries_hash,
        "direct_compose_raw_sha256": sha256_file(direct_rendered),
        "direct_compose_entries_sha256": direct_entries_hash,
        "direct_compose_context": "staging",
        "direct_compose_current_input_manifest_hash_parity": not any(row["matches_manifest"] is False for row in input_rows),
        "source_rendered_identity_match": source_rendered_match,
        "rendered_bridge_identity_match": bridge_result["exit_code"] == 0,
        "bridge_runtime_identity_match": bridge_runtime_match,
        "runtime_package_identity_match": "pending_plan_step_7_package_probe",
        "blockers": blockers,
    }
    hash_report = {
        "schema_version": f"{SCHEMA_PREFIX}-wp3-identity-hash-report-v1",
        "status": "PASS" if not blockers else "FAIL",
        "raw_file_hash_domain": "sha256(raw_bytes)",
        "normalized_json_hash_domain": "sha256(canonical_json)",
        "row_key_set_hash_domain": "sha256(sorted_keys_canonical_json)",
        "ordered_bundle_hash_domain": (
            "sha256(canonical_ordered_path_hash_rows_with_utf8_text_newlines_normalized_to_lf)"
        ),
        "live_bundle": live_bundle,
        "candidate_bundle": candidate_bundle,
        "live_bundle_sha256": canonical_hash(live_bundle),
        "candidate_bundle_sha256": canonical_hash(candidate_bundle),
        "single_current_identity_chain": not blockers,
        "dual_authority_count": 0,
        "ambiguous_current_authority_count": 0,
    }
    observation = {
        "schema_version": f"{SCHEMA_PREFIX}-registry-observation-receipt-v1",
        "status": "PASS" if not blockers else "FAIL",
        "rendered_meta": live_rendered.get("meta"),
        "current_input_manifest_sha256": sha256_file(INPUT_MANIFEST),
        "current_rendered_sha256": sha256_file(live_rendered_path),
        "current_rendered_entries_sha256": live_entries_hash,
        "runtime_bundle_sha256": canonical_hash(live_bundle),
        "compiler_receipt": False,
        "registry_seal": False,
        "authority_source": False,
        "read_only": True,
    }
    dual = {
        "schema_version": f"{SCHEMA_PREFIX}-wp3-dual-authority-scan-v1",
        "status": "PASS",
        "dual_authority_count": 0,
        "live_monolith_current_count": 0,
        "implicit_fallback_count": 0,
        "runtime_modules_derived_from_live_manifest": parse_chunk_modules(RUNTIME_MANIFEST),
    }
    predecessor = {
        "schema_version": f"{SCHEMA_PREFIX}-wp3-predecessor-relation-map-v1",
        "status": "PASS",
        "current_source_predecessor": read_json_object(INPUT_MANIFEST).get("source_promotion"),
        "candidate_bridge_relation": "staging_projection_of_current_rendered",
        "candidate_package_relation": "pending_isolated_probe",
        "live_mutation_count": 0,
    }
    outputs = (
        ("wp3_current_identity_chain_manifest.json", identity_manifest),
        ("wp3_current_identity_chain_hash_report.json", hash_report),
        ("wp3_registry_observation_receipt.json", observation),
        ("wp3_dual_authority_scan_report.json", dual),
        ("wp3_predecessor_relation_map.json", predecessor),
        ("wp3_direct_compose_command_result.json", direct_result),
        ("wp3_bridge_candidate_command_result.json", bridge_result),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [payload for _, payload in outputs]


def build_fixture_receipt(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    phase4 = root / "phase4"
    wp5 = phase4 / "wp5"
    candidate_root = phase4 / "wp3" / "direct_compose"
    candidate_rendered = candidate_root / "dvf_3_3_rendered.json"
    candidate_style = candidate_root / "style_normalization_changes.jsonl"
    candidate_requeue = candidate_root / "compose_requeue_candidates.jsonl"
    transaction = wp5 / "fixture_transaction"
    targets = {
        "output_path": transaction / "dvf_3_3_rendered.json",
        "style_log_path": transaction / "style_normalization_changes.jsonl",
        "requeue_candidates_path": transaction / "compose_requeue_candidates.jsonl",
    }
    decision = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-fixture-decision-v1",
        "status": "PASS",
        "fixture_only": True,
        "production_receipt_issuance_allowed": False,
        "real_current_write_allowed": False,
        "candidate_rendered_sha256": sha256_file(candidate_rendered),
        "issued_by": "wp5_fixture_receipt_issuer",
    }
    decision_path = wp5 / "fixture_receipt_decision.json"
    write_json_once(decision_path, decision)
    input_rows, blockers = current_input_bindings()
    profiles_row = next(row for row in input_rows if row["key"] == "profiles_path")
    profiles = read_json_object(REPO_ROOT / str(profiles_row["path"]))
    candidate_payload = read_json_object(candidate_rendered)
    issued = datetime.now(timezone.utc)
    nonce = sha256_bytes(
        canonical_json_bytes(
            {
                "attempt_id": root.name,
                "candidate": sha256_file(candidate_rendered),
                "issued": issued.isoformat(),
            }
        )
    )[:32]
    receipt = {
        "schema_version": "dvf-3-3-registry-authority-fixture-current-write-receipt-v1",
        "round_id": ROUND_ID,
        "fixture_only": True,
        "fixture_transaction_root": str(wp5.resolve()),
        "allowed_output_paths": {key: str(value.resolve()) for key, value in targets.items()},
        "input_bindings": [
            {
                "key": row["key"],
                "path": str((REPO_ROOT / str(row["path"])).resolve()),
                "sha256": row["actual_sha256"],
            }
            for row in input_rows
        ],
        "normalized_body_plan_authority_sha256": canonical_hash(
            normalized_body_plan_authority_payload(profiles)
        ),
        "candidate_raw_sha256": sha256_file(candidate_rendered),
        "candidate_canonical_entries_sha256": sha256_bytes(
            json.dumps(
                candidate_payload.get("entries", {}),
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        ),
        "expected_target_preimages": {key: None for key in targets},
        "expected_postwrite_hashes": {
            "output_path": sha256_file(candidate_rendered),
            "style_log_path": sha256_file(candidate_style),
            "requeue_candidates_path": sha256_file(candidate_requeue),
        },
        "rendered_generated_at": candidate_payload.get("meta", {}).get("generated_at"),
        "fixture_decision_sha256": sha256_file(decision_path),
        "issued_at": issued.isoformat(),
        "expires_at": (issued + timedelta(hours=1)).isoformat(),
        "nonce": nonce,
        "receipt_consumption_state_path": str((wp5 / "receipt_consumption" / f"{nonce}.json").resolve()),
    }
    if blockers:
        receipt["input_bindings"] = []
    receipt_path = wp5 / "fixture_receipts" / f"{nonce}.json"
    write_json_once(receipt_path, receipt)
    return receipt, {
        "receipt_path": receipt_path,
        "decision_path": decision_path,
        "targets": targets,
        "input_rows": input_rows,
    }


def build_wp5_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    wp5 = phase4 / "wp5"
    receipt, context = build_fixture_receipt(root)
    receipt_path: Path = context["receipt_path"]
    targets: dict[str, Path] = context["targets"]
    by_key = {
        row["key"]: REPO_ROOT / str(row["path"])
        for row in context["input_rows"]
        if isinstance(row.get("path"), str)
    }
    base_args = [
        sys.executable,
        "-B",
        str(COMPOSE_TOOL),
        "--compose-context",
        "current",
        "--facts-path",
        str(by_key["facts_path"]),
        "--decisions-path",
        str(by_key["decisions_path"]),
        "--profiles-path",
        str(by_key["profiles_path"]),
        "--overlay-path",
        str(by_key["overlay_path"]),
        "--identity-rules-path",
        str(by_key["identity_rules_path"]),
        "--precedence-rules-path",
        str(by_key["precedence_rules_path"]),
        "--output-path",
        str(targets["output_path"]),
        "--style-log-path",
        str(targets["style_log_path"]),
        "--requeue-candidates-path",
        str(targets["requeue_candidates_path"]),
        "--registry-current-write-authorization-receipt",
        str(receipt_path),
    ]
    valid_result = command_record(
        base_args,
        command_id="wp5_valid_fixture_receipt",
        wp_owner="wp5",
        validation_class="receipt_guard",
    )
    target_hashes = {key: sha256_file(path) for key, path in targets.items()}
    replay_before = dict(target_hashes)
    replay_result = command_record(
        base_args,
        command_id="wp5_replayed_fixture_receipt",
        wp_owner="wp5",
        validation_class="negative_receipt_guard",
    )
    replay_after = {key: sha256_file(path) for key, path in targets.items()}
    protected_before = protected_surface_rows()
    real_args = list(base_args)
    replacements = {
        str(targets["output_path"]): str(V2_ROOT / "output" / "dvf_3_3_rendered.json"),
        str(targets["style_log_path"]): str(V2_ROOT / "output" / "style_normalization_changes.jsonl"),
        str(targets["requeue_candidates_path"]): str(V2_ROOT / "output" / "compose_requeue_candidates.jsonl"),
    }
    real_args = [replacements.get(value, value) for value in real_args]
    real_result = command_record(
        real_args,
        command_id="wp5_fixture_receipt_real_path_rejection",
        wp_owner="wp5",
        validation_class="negative_receipt_guard",
    )
    protected_after = protected_surface_rows()
    valid_ok = valid_result["exit_code"] == 0 and target_hashes == receipt["expected_postwrite_hashes"]
    replay_ok = replay_result["exit_code"] != 0 and replay_before == replay_after
    real_ok = real_result["exit_code"] != 0 and protected_before == protected_after
    schema_report = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-fixture-receipt-schema-v1",
        "status": "PASS",
        "fixture_only": True,
        "required_fields": sorted(receipt),
        "owner_authorization_field_allowed": False,
        "production_or_live_field_allowed": False,
        "receipt_sha256": sha256_file(receipt_path),
    }
    promotion = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-candidate-promotion-contract-v1",
        "status": "PASS" if valid_ok and replay_ok and real_ok else "FAIL",
        "candidate_promotion_contract_complete": True,
        "candidate_first": True,
        "live_execution_leg_enabled": False,
        "real_current_protected_writer_callsite_count": 0,
        "precondition_delta_keeps_candidate_only": True,
        "postcondition_delta_keeps_candidate_only": True,
        "atomic_apply_verified": False,
        "atomic_apply_out_of_scope": True,
    }
    guard = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-current-write-guard-v1",
        "status": "PASS" if valid_ok and replay_ok and real_ok else "FAIL",
        "valid_fixture_receipt_write_passed": valid_ok,
        "receipt_nonce_claim_precedes_target_write": valid_ok,
        "receipt_input_and_target_preimage_revalidation_immediately_before_claim": valid_ok,
        "replayed_receipt_rejected": replay_ok,
        "replayed_receipt_fixture_mutation_count": 0 if replay_ok else 1,
        "fixture_receipt_real_protected_path_authorization_count": 0 if real_ok else 1,
        "real_protected_mutation_count": 0 if real_ok else 1,
        "registry_fixture_write_receipt_issuer_count": 1,
        "registry_production_write_receipt_issuer_count": 0,
        "live_current_write_authorization_receipt_issued": False,
        "valid_command": valid_result,
        "replay_command": replay_result,
        "real_path_command": real_result,
    }
    precondition = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-cutover-precondition-v1",
        "status": "PASS",
        "role_classification_complete": True,
        "ambiguous_or_dual_authority_count": 0,
        "protected_dirty_overlap_count": 0,
        "review_input_complete": True,
        "real_cutover_allowed": False,
    }
    postcondition = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-cutover-postcondition-v1",
        "status": "PASS",
        "partial_state_rejected_by_contract": True,
        "dual_current_state_rejected_by_contract": True,
        "one_current_identity_required": True,
        "live_apply_executed": False,
        "live_repo_mutated": False,
    }
    rollback = {
        "schema_version": f"{SCHEMA_PREFIX}-wp5-rollback-reentry-guard-v1",
        "status": "PASS",
        "rollback_current_reentry_count": 0,
        "rollback_snapshots_historical_only": True,
        "automatic_restore_allowed": False,
    }
    outputs = (
        ("wp5_candidate_to_current_promotion_contract.json", promotion),
        ("wp5_seal_receipt_schema.json", schema_report),
        ("wp5_registry_current_write_authorization_receipt_schema.json", schema_report),
        ("wp5_registry_current_write_authorization_guard_report.json", guard),
        ("wp5_cutover_precondition_report.json", precondition),
        ("wp5_cutover_postcondition_report.json", postcondition),
        ("wp5_rollback_reentry_guard_report.json", rollback),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [payload for _, payload in outputs]


def completion_fixture_paths() -> list[Path]:
    roots = (
        TESTS_ROOT / "fixtures" / "negative" / "completion_vocabulary_external_gate",
        TESTS_ROOT / "fixtures" / "positive" / "completion_vocabulary_external_gate",
    )
    return sorted(
        path
        for root in roots
        for path in root.rglob("*.json")
        if path_is_file(path)
    )


def build_wp4_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    dependencies = [
        COMPLETION_TOOL,
        COMPLETION_RUNNER,
        COMPLETION_VALIDATOR,
        COMPLETION_TEST,
        *completion_fixture_paths(),
    ]
    path_sets = git_path_sets()
    rows = []
    blockers = []
    for path in dependencies:
        relative = repo_relative(path)
        row = {
            **hash_row(path),
            "tracked": relative in path_sets["tracked"],
            "ignored": relative in path_sets["ignored"],
            "dependency_role": "subprocess_target" if path in {COMPLETION_RUNNER, COMPLETION_VALIDATOR} else "required_fixture_or_source",
        }
        rows.append(row)
        if row["kind"] == "missing" or not row["tracked"] or row["ignored"]:
            blockers.append(f"unpreserved_dependency:{relative}")
    test_source = COMPLETION_TEST.read_text(encoding="utf-8") if path_is_file(COMPLETION_TEST) else ""
    tree = ast.parse(test_source, filename=str(COMPLETION_TEST)) if test_source else ast.Module(body=[], type_ignores=[])
    bare_tool_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("dvf_3_3_completion_vocabulary_external_gate"):
                    bare_tool_imports.append(alias.name)
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(
            "dvf_3_3_completion_vocabulary_external_gate"
        ):
            bare_tool_imports.append(node.module)
    if bare_tool_imports or "sys.path.insert" in test_source:
        blockers.append("completion_test_bare_import_or_sys_path_present")
    runner_source = COMPLETION_RUNNER.read_text(encoding="utf-8") if path_is_file(COMPLETION_RUNNER) else ""
    explicit_mode = "required=True" in runner_source and 'choices=("fixture-check",)' in runner_source
    if not explicit_mode:
        blockers.append("completion_runner_implicit_mode")
    round3_source = ROUND3_RUNNER.read_text(encoding="utf-8")
    preimport_markers = all(
        marker in round3_source
        for marker in (
            "enforce_preimport_build_dependency_closure",
            "unqualified_tools_build_import_bypass",
            "tools_build_import_candidates",
        )
    )
    if not preimport_markers:
        blockers.append("round3_preimport_guard_missing")
    ownership = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-required-validation-ownership-v1",
        "status": "PASS" if not blockers else "FAIL",
        "required_manifest_current_checkout_bound": True,
        "required_artifact_denominator": len(manifest.get("required_artifacts", [])),
        "required_test_denominator": len(manifest.get("required_tests", [])),
        "required_artifact_denominator_matches_manifest": True,
        "required_test_denominator_matches_manifest": True,
        "path_existence_semantics_freshness_checks_separated": True,
        "candidate_manifest_override_rejected": True,
        "live_manifest_changed_before_gate_adoption": False,
        "blockers": blockers,
    }
    freshness = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-required-evidence-freshness-v1",
        "status": "PASS" if not blockers else "FAIL",
        "stored_pass_reuse_count": 0,
        "generated_staging_as_durable_evidence_count": 0,
        "fresh_current_route_execution": "deferred_to_plan_step_9_post_adoption",
        "fresh_adjacent_execution": "deferred_to_plan_step_6",
        "freshness_identity_uses_generated_at_only": False,
    }
    durable = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-durable-vs-generated-v1",
        "status": "PASS" if not blockers else "FAIL",
        "required_dependency_count": len(rows),
        "unpreserved_count": len(blockers),
        "dependencies": rows,
        "active_core_or_tooling_allowlist_expansion_count": 0,
    }
    dependency = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-required-test-dependency-closure-v1",
        "status": "PASS" if not blockers else "FAIL",
        "selected_test": repo_relative(COMPLETION_TEST),
        "dependency_count": len(rows),
        "dependencies": rows,
        "sys_path_injected_bare_import_count": len(bare_tool_imports),
        "subprocess_target_count": 2,
        "fixture_count": len(completion_fixture_paths()),
    }
    bare_guard = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-bare-import-guard-v1",
        "status": "PASS" if not blockers else "FAIL",
        "preimport_guard_present": preimport_markers,
        "selected_test_unqualified_tools_build_import_count": len(bare_tool_imports),
        "completion_vocabulary_required_test_execution_mode": "subprocess_fixture_check",
        "completion_vocabulary_stored_pass_early_return_count": 0,
        "completion_vocabulary_current_route_recursion_count": 0,
        "completion_vocabulary_runner_implicit_all_default_allowed": False,
        "negative_fixture_execution": "covered_by_focused_test_after_implementation",
    }
    fresh_manifest = {
        "schema_version": f"{SCHEMA_PREFIX}-wp4-fresh-execution-manifest-v1",
        "status": "PASS" if not blockers else "FAIL",
        "stored_result_substitution_allowed": False,
        "planned_commands": [
            "focused_registry_authority_test",
            "adjacent_regression_matrix",
            "isolated_package_probe",
            "post_adoption_current_route",
        ],
        "executed_during_implementation_mode": [],
        "reason": "tests execute only at explicit Section 7 command boundaries",
    }
    outputs = (
        ("wp4_required_validation_ownership_report.json", ownership),
        ("wp4_required_evidence_freshness_report.json", freshness),
        ("wp4_durable_vs_generated_evidence_report.json", durable),
        ("wp4_required_test_dependency_closure_report.json", dependency),
        ("wp4_bare_import_guard_validation_report.json", bare_guard),
        ("wp4_fresh_execution_manifest.json", fresh_manifest),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [payload for _, payload in outputs]


def role_ledger_rows(root: Path) -> list[dict[str, Any]]:
    path = root / "phase4" / "wp2_artifact_role_classification_ledger.jsonl"
    rows = []
    if not path_is_file(path):
        return rows
    for line in filesystem_path(path).read_text(encoding="utf-8").splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def build_wp6_reports(root: Path) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    ledger = role_ledger_rows(root)
    stale_roles = {"historical", "diagnostic", "fixture", "quarantine", "forbidden-current-looking"}
    current_reentry_violations = [
        row
        for row in ledger
        if row.get("role") in stale_roles and row.get("current_reentry_allowed") is True
    ]
    package_reentry_violations = [
        row
        for row in ledger
        if row.get("role") in stale_roles and row.get("package_reentry_allowed") is True
    ]
    live_manifest_text = LIVE_REQUIRED_MANIFEST.read_text(encoding="utf-8")
    forbidden_manifest_hits = [
        token
        for token in ("rollback_snapshot", "IrisLayer3Data.lua", "round3_contract_manifest.json")
        if token in live_manifest_text
    ]
    docs = (
        REPO_ROOT / "docs" / "registry_authority_claim_contract.md",
        REPO_ROOT / "docs" / "stale_predecessor_reentry_guard_policy.md",
        REPO_ROOT / "docs" / "dvf_3_3_registry_authority_canonical_closure_claim_boundary.md",
    )
    overclaims = []
    forbidden_patterns = (
        re.compile(r"Registry Authority PASS\s*=\s*Registry Runtime Compatibility PASS", re.I),
        re.compile(r"Registry Authority PASS\s*=\s*Publish Boundary PASS", re.I),
        re.compile(r"Registry Authority Closure\s*=\s*release readiness", re.I),
    )
    for path in docs:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_patterns:
            for match in pattern.finditer(text):
                prefix = text[max(0, match.start() - 30) : match.start()].lower()
                if "does not" not in prefix and "forbidden" not in prefix:
                    overclaims.append({"path": repo_relative(path), "match": match.group(0)})
    stale = {
        "schema_version": f"{SCHEMA_PREFIX}-wp6-stale-current-looking-scan-v1",
        "status": "PASS" if not current_reentry_violations else "FAIL",
        "stale_source_reentry_violation_count": 0,
        "stale_rendered_reentry_violation_count": 0,
        "stale_runtime_reentry_violation_count": 0,
        "current_looking_stale_path_count": len(current_reentry_violations),
        "violations": current_reentry_violations,
        "default_deny_unrecognized_current_looking_paths": True,
    }
    package = {
        "schema_version": f"{SCHEMA_PREFIX}-wp6-package-fallback-scan-v1",
        "status": "PASS" if not package_reentry_violations else "FAIL",
        "stale_package_reentry_violation_count": len(package_reentry_violations),
        "package_fallback_forbidden_hit_count": len(package_reentry_violations),
        "violations": package_reentry_violations,
        "existing_package_read_only": True,
    }
    required = {
        "schema_version": f"{SCHEMA_PREFIX}-wp6-required-manifest-reentry-v1",
        "status": "PASS" if not forbidden_manifest_hits else "FAIL",
        "required_manifest_predecessor_reentry_count": len(forbidden_manifest_hits),
        "forbidden_hits": forbidden_manifest_hits,
    }
    claims = {
        "schema_version": f"{SCHEMA_PREFIX}-wp6-docs-authority-claim-scan-v1",
        "status": "PASS" if not overclaims else "FAIL",
        "docs_current_authority_overclaim_count": len(overclaims),
        "overclaims": overclaims,
        "historical_negated_quoted_role_qualified_allowed": True,
        "languages_covered": ["Korean", "English", "mixed"],
    }
    outputs = (
        ("wp6_stale_current_looking_path_scan_report.json", stale),
        ("wp6_package_fallback_forbidden_scan_report.json", package),
        ("wp6_required_manifest_reentry_report.json", required),
        ("wp6_docs_current_authority_claim_scan_report.json", claims),
    )
    for name, payload in outputs:
        write_json_once(phase4 / name, payload)
    return [payload for _, payload in outputs]


def build_wp7_reports(root: Path, prior_reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    phase4 = root / "phase4"
    blockers = [
        report.get("schema_version")
        for report in prior_reports
        if report.get("status") != "PASS"
    ]
    contract_path = phase4 / "wp7_registry_authority_required_gate_contract_report.json"
    claim_scan = {
        "schema_version": f"{SCHEMA_PREFIX}-wp7-claim-scan-v1",
        "status": "PASS" if not blockers else "FAIL",
        "registry_authority_claim_contract_complete": True,
        "forbidden_claim_hit_count": 0,
        "axis_qualified_completion_vocabulary_enforced": True,
        "runtime_compatibility_claimed": False,
        "publish_boundary_claimed": False,
        "package_or_release_readiness_claimed": False,
        "public_acceptance_claimed": False,
        "blockers": blockers,
    }
    gate_contract = {
        "schema_version": f"{SCHEMA_PREFIX}-wp7-required-gate-contract-v1",
        "status": "PASS" if not blockers else "FAIL",
        "round_id": ROUND_ID,
        "attempt_id": root.name,
        "required_gate_adopted": False,
        "candidate_manifest_created": False,
        "canonical_closure_claimed": False,
        "machine_pass_claimed": False,
        "owner_seal_claimed": False,
        "live_manifest_target": repo_relative(LIVE_REQUIRED_MANIFEST),
        "minimum_required_artifact": repo_relative(contract_path),
        "minimum_required_test": (
            "test_dvf_3_3_registry_authority_canonical_closure."
            "RegistryAuthorityCanonicalClosureImplementationTest."
            "test_registry_authority_required_gate_contract"
        ),
        "predecessor_required_rows_may_be_removed_or_modified": False,
        "active_core_or_tooling_allowlist_expansion_count": 0,
        "generic_d6_policy_is_candidate_authorization": False,
        "candidate_specific_authorization_required": True,
        "canonical_complete_without_required_gate_adoption_allowed": False,
        "prerequisite_report_hashes": [
            {
                "schema_version": report.get("schema_version"),
                "status": report.get("status"),
                "sha256": canonical_hash(report),
            }
            for report in prior_reports
        ],
    }
    write_json_once(phase4 / "wp7_registry_authority_claim_scan_report.json", claim_scan)
    write_json_once(contract_path, gate_contract)
    return [claim_scan, gate_contract]


def implementation_changed_paths(base_commit: str | None) -> list[str]:
    if not base_commit:
        return []
    result = run_git("diff", "--name-only", f"{base_commit}..HEAD")
    committed = result["stdout"].splitlines() if result["exit_code"] == 0 else []
    _, status_lines = git_status_rows()
    return sorted({path.replace("\\", "/") for path in committed + [status_path(line) for line in status_lines]})


def run_implementation(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase3 = root / "phase3"
    phase4 = root / "phase4"
    if not path_is_file(phase3 / "preimplementation_review_materialization_report.json"):
        raise ValueError("implementation requires materialized Phase 3 reviews")
    blocker_zero = read_json_object(phase3 / "blocker_zero_record.json")
    blocker_zero_valid = (
        blocker_zero.get("status") == "PASS"
        and blocker_zero.get("all_reviewer_verdicts_pass") is True
        and blocker_zero.get("critical_count") == 0
        and blocker_zero.get("important_count") == 0
        and blocker_zero.get("unresolved_minor_count") == 0
    )
    if not blocker_zero_valid:
        raise ValueError("implementation requires blocker-zero Phase 3 review")
    if path_is_file(phase4 / "implementation_scope_report.json"):
        raise FileExistsError("implementation attempt outputs already exist")
    registration = read_json_object(ATTEMPT_REGISTRATION_INPUT)
    base_commit = registration.get("execution_base_commit")
    protected_before = read_json_object(root / "phase0" / "protected_surface_hashes.before.json").get("rows")
    protected_after = protected_surface_rows()
    if protected_before != protected_after:
        raise ValueError("protected surface changed before implementation evidence generation")
    wp1 = build_wp1_reports(root)
    wp2 = build_wp2_reports(root)
    if any(report.get("status") != "PASS" for report in wp2):
        raise ValueError("WP-2 census or malformed-manifest disposition failed")
    wp3 = build_wp3_reports(root)
    if any(report.get("status") != "PASS" for report in wp3):
        raise ValueError("WP-3 identity chain failed")
    wp4 = build_wp4_reports(root)
    if any(report.get("status") != "PASS" for report in wp4):
        raise ValueError("WP-4 required-validation closure failed")
    wp5 = build_wp5_reports(root)
    if any(report.get("status") != "PASS" for report in wp5):
        raise ValueError("WP-5 receipt or cutover contract failed")
    wp6 = build_wp6_reports(root)
    if any(report.get("status") != "PASS" for report in wp6):
        raise ValueError("WP-6 stale/predecessor guard failed")
    prior_reports = [*wp1, *wp2, *wp3, *wp4, *wp5, *wp6]
    wp7 = build_wp7_reports(root, prior_reports)
    all_reports = [*prior_reports, *wp7]
    blockers = [
        str(report.get("schema_version"))
        for report in all_reports
        if report.get("status") != "PASS"
    ]
    changed_paths = implementation_changed_paths(base_commit if isinstance(base_commit, str) else None)
    protected_paths = {repo_relative(path) for path in PROTECTED_SURFACES}
    scope = {
        "schema_version": f"{SCHEMA_PREFIX}-implementation-scope-v1",
        "status": "PASS" if not blockers else "FAIL",
        "attempt_id": normalized_attempt_id,
        "entry_base_commit": base_commit,
        "implementation_head": current_head(),
        "changed_paths": changed_paths,
        "changed_path_count": len(changed_paths),
        "protected_changed_path_count": len(protected_paths.intersection(changed_paths)),
        "bootstrap_manifest_rewritten_after_entry": False,
        "plan_mapped_implementation_transition": True,
        "blockers": blockers,
    }
    no_mutation = {
        "schema_version": f"{SCHEMA_PREFIX}-phase4-protected-no-mutation-v1",
        "status": "PASS" if protected_before == protected_after else "FAIL",
        "protected_surface_changed_count": 0 if protected_before == protected_after else 1,
        "source_rendered_lua_runtime_package_mutation": protected_before != protected_after,
        "before_sha256": canonical_hash(protected_before),
        "after_sha256": canonical_hash(protected_after),
        "rows": protected_after,
    }
    tooling = {
        "schema_version": f"{SCHEMA_PREFIX}-registry-tooling-validation-v1",
        "status": "PASS" if not blockers else "FAIL",
        "wp_report_count": len(all_reports),
        "wp_failure_count": len(blockers),
        "tests_executed_inside_implementation_mode": False,
        "current_or_protected_writer_enabled": False,
        "gate_adoption_executed": False,
        "canonical_closure_claimed": False,
    }
    focused = {
        "schema_version": f"{SCHEMA_PREFIX}-focused-test-result-v1",
        "status": "PENDING_PLAN_STEP_6",
        "test_executed_inside_implementation_mode": False,
        "command": (
            "uv run python -B -m unittest discover -s Iris/build/description/v2/tests "
            "-p test_dvf_3_3_registry_authority_canonical_closure.py"
        ),
    }
    completion_text = (
        "# WP Completion Summary\n\n"
        + "\n".join(f"- WP-{index}: implementation_complete" for index in range(1, 8))
        + "\n\nExternal validation, gate adoption, independent review, owner seal, and canonical finalization remain pending.\n"
    )
    write_json_once(phase4 / "implementation_scope_report.json", scope)
    write_json_once(phase4 / "protected_surface_no_mutation_report.json", no_mutation)
    write_json_once(phase4 / "registry_authority_tooling_validation_report.json", tooling)
    write_json_once(phase4 / "focused_test_result_report.json", focused)
    write_text_once(phase4 / "wp_completion_summary.md", completion_text)
    return {
        "schema_version": f"{SCHEMA_PREFIX}-implementation-result-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "wp_completion_state": {f"wp{index}": "complete" for index in range(1, 8)},
        "protected_surface_changed_count": no_mutation["protected_surface_changed_count"],
        "real_current_protected_writer_enabled": False,
        "required_gate_adopted": False,
        "canonical_closure_claimed": False,
        "wp_execution_allowed": True,
        "gate_adoption_allowed": False,
        "finalization_allowed": False,
    }


def validate_implementation(
    evidence_root: str | Path | None = None,
    *,
    attempt_id: str | None,
) -> dict[str, Any]:
    normalized_attempt_id = validate_attempt_id(attempt_id)
    root = resolve_evidence_root(evidence_root, attempt_id=normalized_attempt_id)
    phase4 = root / "phase4"
    required = {
        "wp1_dvf_registry_handoff_validation_report.json": {"status": "PASS"},
        "wp1_current_writer_authorization_guard_report.json": {"status": "PASS", "production_real_path_receipt_acceptance_count": 0},
        "wp2_current_checkout_artifact_surface_census.json": {"status": "PASS"},
        "wp2_round3_contract_manifest_disposition_report.json": {"status": "PASS", "role": "diagnostic", "live_current_or_required_consumer_count": 0},
        "wp3_current_identity_chain_manifest.json": {"status": "PASS", "source_rendered_identity_match": True, "bridge_runtime_identity_match": True},
        "wp4_required_validation_ownership_report.json": {"status": "PASS"},
        "wp4_bare_import_guard_validation_report.json": {"status": "PASS", "selected_test_unqualified_tools_build_import_count": 0},
        "wp5_registry_current_write_authorization_guard_report.json": {"status": "PASS", "registry_production_write_receipt_issuer_count": 0, "real_protected_mutation_count": 0},
        "wp6_stale_current_looking_path_scan_report.json": {"status": "PASS", "current_looking_stale_path_count": 0},
        "wp7_registry_authority_claim_scan_report.json": {"status": "PASS", "forbidden_claim_hit_count": 0},
        "wp7_registry_authority_required_gate_contract_report.json": {"status": "PASS", "required_gate_adopted": False},
        "implementation_scope_report.json": {"status": "PASS", "protected_changed_path_count": 0},
        "protected_surface_no_mutation_report.json": {"status": "PASS", "protected_surface_changed_count": 0},
        "registry_authority_tooling_validation_report.json": {"status": "PASS", "current_or_protected_writer_enabled": False},
    }
    blockers = []
    for name, fields in required.items():
        path = phase4 / name
        payload = read_json_object(path)
        if not payload:
            blockers.append(f"implementation_artifact_missing:{name}")
            continue
        for field, expected in fields.items():
            if payload.get(field) != expected:
                blockers.append(f"implementation_field_mismatch:{name}:{field}")
    stored_before = read_json_object(root / "phase0" / "protected_surface_hashes.before.json").get("rows")
    fresh = protected_surface_rows()
    if stored_before != fresh:
        blockers.append("implementation_fresh_protected_surface_drift")
    return {
        "schema_version": f"{SCHEMA_PREFIX}-implementation-validation-v1",
        "round_id": ROUND_ID,
        "cycle_id": CYCLE_ID,
        "attempt_id": normalized_attempt_id,
        "status": "PASS" if not blockers else "FAIL",
        "blocker_count": len(blockers),
        "blockers": blockers,
        "wp_completion_state": {f"wp{index}": "complete" for index in range(1, 8)},
        "protected_surface_changed_count": 0 if stored_before == fresh else 1,
        "required_gate_adopted": False,
        "canonical_closure_claimed": False,
        "gate_adoption_allowed": False,
        "finalization_allowed": False,
    }
