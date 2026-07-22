from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_byte_identical(left: Path, right: Path) -> bool:
    return (
        left.is_file()
        and right.is_file()
        and left.read_bytes() == right.read_bytes()
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


def directory_tree_hash(path: Path) -> str | None:
    if not path.is_dir():
        return None
    rows = [
        {
            "path": child.relative_to(path).as_posix(),
            "sha256": sha256_file(child),
        }
        for child in sorted(item for item in path.rglob("*") if item.is_file())
    ]
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
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
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
        if path.is_file():
            digest = sha256_file(path)
            kind = "file"
        elif path.is_dir():
            child_rows = [
                {
                    "path": child.relative_to(path).as_posix(),
                    "sha256": sha256_file(child),
                }
                for child in sorted(item for item in path.rglob("*") if item.is_file())
            ]
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
        "lua_environment_hash": canonical_hash(lua),
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
    if stored_lua.get("status") != "PASS" or canonical_hash(stored_lua) != canonical_hash(current_lua):
        blockers.append("entry_lua_environment_drift")
    reviewed_lua_hash = review_manifest.get("reviewed_bundle", {}).get(
        "lua_environment_hash"
    )
    if canonical_hash(current_lua) != reviewed_lua_hash:
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
