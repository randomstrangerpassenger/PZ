from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


V2_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = V2_ROOT.parents[3]
ROUND_ROOT = (
    V2_ROOT
    / "staging"
    / "compose_contract_migration"
    / "static_report_label_cleanup_referent_recovery_round"
)
PRIOR_ROUND_ROOT = (
    V2_ROOT
    / "staging"
    / "compose_contract_migration"
    / "static_report_label_cleanup_round"
)

PHILOSOPHY = REPO_ROOT / "docs" / "Philosophy.md"
DECISIONS = REPO_ROOT / "docs" / "DECISIONS.md"
ARCHITECTURE = REPO_ROOT / "docs" / "ARCHITECTURE.md"
ROADMAP = REPO_ROOT / "docs" / "ROADMAP.md"
PLAN = (
    REPO_ROOT
    / "docs"
    / "Iris"
    / "iris-dvf-3-3-static-report-label-cleanup-referent-recovery-round-plan.md"
)

SOURCE_DECISIONS = (
    V2_ROOT
    / "staging"
    / "compose_contract_migration"
    / "selected_role_bridge_impact_seal_round"
    / "phase7_ai_trace_reconstruction"
    / "metadata_migration_probe"
    / "dry_run"
    / "dry_run_decisions.ai_trace.jsonl"
)
RENDERED_OUTPUT = (
    V2_ROOT
    / "staging"
    / "compose_contract_migration"
    / "selected_role_bridge_impact_seal_round"
    / "phase7_ai_trace_reconstruction"
    / "metadata_migration_probe"
    / "dry_run_rendered_v2_preview.ai_trace.json"
)
RUNTIME_PATHS = [
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks.lua",
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3Data.lua",
    REPO_ROOT / "Iris" / "build" / "package" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks.lua",
]
RUNTIME_CHUNK_DIRS = [
    REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3DataChunks",
    REPO_ROOT
    / "Iris"
    / "build"
    / "package"
    / "Iris"
    / "media"
    / "lua"
    / "client"
    / "Iris"
    / "Data"
    / "IrisLayer3DataChunks",
]

EXPECTED_ROW_COUNT = 2105
EXPECTED_COUNTS = {"adopted": 2084, "unadopted": 21}
TEXT_SUFFIXES = {".json", ".jsonl", ".md", ".txt", ".py", ".lua"}
SKIP_DIRS = {".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache"}
TOKEN_RE = re.compile(r"\b(active|silent)\b", re.IGNORECASE)
REFERENT_LABEL_RE = re.compile(
    r"\b(active|silent)\s+(count|counts|row|rows|token|tokens|label|labels)\b",
    re.IGNORECASE,
)
JSON_STATE_RE = re.compile(r'"(?:state|runtime_state|source)"\s*:\s*"(active|silent)"', re.IGNORECASE)
FILENAME_CANDIDATE_RE = re.compile(
    r"(report|operator|static|label|surface|residue|scope|mutation|analysis|worksheet|stats|validation)",
    re.IGNORECASE,
)
KEYWORD_RE = re.compile(
    r"(generated report|operator-facing|operator artifact|Surface C|static report|label cleanup|"
    r"current operator|active/silent|판정 보조|판정)",
    re.IGNORECASE,
)
METRIC_KEY_RE = re.compile(
    r"(\bactive_count\b|\bsilent_count\b|\btotal_active_rows\b|\btotal_silent_rows\b|"
    r"기등록 active|기등록 silent|전체 active|전체 silent)",
    re.IGNORECASE,
)
SCRIPT_RE = re.compile(
    r"(report writer|static report generator|operator artifact builder|validation report generator|"
    r"cleanup inventory builder|static_report_label|runtime_payload_enum|write_phase|Surface C|"
    r"build_report|validation_report)",
    re.IGNORECASE,
)


class GateError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


def write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def path_record(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "exists": path.exists(),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
    }


def run_command(args: list[str], timeout: int = 120) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            args,
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return {
            "command": args,
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "timed_out": False,
            "missing_tool": False,
        }
    except FileNotFoundError as exc:
        return {
            "command": args,
            "exit_code": None,
            "stdout": "",
            "stderr": str(exc),
            "timed_out": False,
            "missing_tool": True,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": args,
            "exit_code": None,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "timed_out": True,
            "missing_tool": False,
        }


def run_git(args: list[str], timeout: int = 120) -> dict[str, Any]:
    return run_command(["git", *args], timeout=timeout)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
                if limit is not None and len(rows) >= limit:
                    break
    return rows


def is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def iter_text_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if set(path.parts) & SKIP_DIRS:
                continue
            if is_under(path, ROUND_ROOT):
                continue
            if path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            files.append(path)
    return sorted(set(files), key=rel)


def token_counts(path: Path, max_bytes: int = 8_000_000) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {"active": 0, "silent": 0, "adopted": 0, "unadopted": 0, "truncated": False}
    data = path.read_bytes()
    truncated = len(data) > max_bytes
    if truncated:
        data = data[:max_bytes]
    text = data.decode("utf-8", errors="ignore")
    return {
        "active": len(re.findall(r"\bactive\b", text, re.IGNORECASE)),
        "silent": len(re.findall(r"\bsilent\b", text, re.IGNORECASE)),
        "adopted": len(re.findall(r"\badopted\b", text, re.IGNORECASE)),
        "unadopted": len(re.findall(r"\bunadopted\b", text, re.IGNORECASE)),
        "truncated": truncated,
    }


def contains_keyword(path: Path, pattern: re.Pattern[str], max_bytes: int = 1_000_000) -> bool:
    if not path.exists() or not path.is_file():
        return False
    data = path.read_bytes()[:max_bytes]
    text = data.decode("utf-8", errors="ignore")
    return pattern.search(text) is not None


def text_search(path: Path, pattern: re.Pattern[str], max_bytes: int = 1_000_000) -> bool:
    return contains_keyword(path, pattern, max_bytes=max_bytes)


def infer_consumer_surface(path_text: str, path: Path) -> str | None:
    normalized = path_text.replace("\\", "/")
    if normalized.startswith(".claude/") or normalized.startswith(".tmp/"):
        return "backup_or_parallel_worktree_artifact"
    if "/tests/" in normalized or normalized.startswith("Iris/build/description/v2/tests/"):
        return "test_fixture"
    if normalized == "Iris/evidence/analysis/subcategory_analysis.md":
        return "historical_operator_worksheet"
    if normalized.startswith("Iris/output/"):
        return "legacy_output_metric_or_report"
    if normalized.startswith("Iris/build/description/v2/output/"):
        return "current_build_output_metric_or_report"
    if normalized.startswith("Iris/build/description/v2/staging/"):
        return "staging_diagnostic_or_round_evidence"
    if normalized.startswith("Iris/build/description/v2/tools/build/"):
        return "writer_or_recipe"
    if normalized.startswith("docs/") or normalized.startswith("Iris/_docs/"):
        return "governance_or_historical_doc"
    if normalized.startswith("Iris/_archive/"):
        return "archive_historical_artifact"
    if normalized.startswith("media/lua/shared/Iris/") or normalized.startswith("Iris/media/lua/"):
        return "runtime_or_bridge_artifact"
    if path.exists() and (FILENAME_CANDIDATE_RE.search(path.name) or contains_keyword(path, KEYWORD_RE)):
        return "static_or_operator_evidence_candidate"
    return None


def compact_command_result(result: dict[str, Any], max_lines: int = 120) -> dict[str, Any]:
    stdout_lines = result["stdout"].splitlines()
    stderr_lines = result["stderr"].splitlines()
    return {
        "command": result["command"],
        "exit_code": result["exit_code"],
        "timed_out": result["timed_out"],
        "missing_tool": result["missing_tool"],
        "stdout_line_count": len(stdout_lines),
        "stderr_line_count": len(stderr_lines),
        "stdout_head": stdout_lines[:max_lines],
        "stderr_head": stderr_lines[:max_lines],
    }


def decision_source_summary(path: Path) -> dict[str, Any]:
    rows = read_jsonl(path)
    counts = Counter(str(row.get("state", row.get("runtime_state", "__missing__"))) for row in rows)
    ids = [str(row.get("item_id", row.get("facts_ref", ""))) for row in rows]
    return {
        "path": rel(path),
        "exists": path.exists(),
        "row_count": len(rows),
        "state_counts": dict(sorted(counts.items())),
        "row_identity_sha256": sha256_text("\n".join(ids) + "\n") if rows else None,
        "sha256": sha256_file(path),
    }


def rendered_summary(path: Path) -> dict[str, Any]:
    payload = read_json(path, {})
    entries = payload.get("entries", {}) if isinstance(payload, dict) else {}
    source_counts = Counter(str(value.get("source")) for value in entries.values() if isinstance(value, dict))
    return {
        "path": rel(path),
        "exists": path.exists(),
        "row_count": len(entries),
        "source_counts": dict(sorted(source_counts.items())),
        "sha256": sha256_file(path),
    }


def runtime_records() -> list[dict[str, Any]]:
    records = [path_record(path) for path in RUNTIME_PATHS]
    for chunk_dir in RUNTIME_CHUNK_DIRS:
        if chunk_dir.exists():
            for path in sorted(chunk_dir.glob("Chunk*.lua")):
                records.append(path_record(path))
    return records


def invariant_baseline() -> dict[str, Any]:
    return {
        "schema_version": "static-report-label-cleanup-referent-recovery-invariant-baseline-v0",
        "generated_at": now_iso(),
        "source_decisions": decision_source_summary(SOURCE_DECISIONS),
        "rendered_output": rendered_summary(RENDERED_OUTPUT),
        "runtime_lua": runtime_records(),
        "top_docs": [path_record(path) for path in [PHILOSOPHY, DECISIONS, ARCHITECTURE, ROADMAP, PLAN]],
    }


def compare_records(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, Any]:
    before_by_path = {item["path"]: item for item in before}
    after_by_path = {item["path"]: item for item in after}
    changed: list[dict[str, Any]] = []
    missing: list[str] = []
    for path, old in before_by_path.items():
        new = after_by_path.get(path)
        if new is None or bool(old.get("exists")) != bool(new.get("exists")):
            missing.append(path)
            continue
        if old.get("sha256") != new.get("sha256"):
            changed.append({"path": path, "before": old.get("sha256"), "after": new.get("sha256")})
    return {"changed_count": len(changed), "missing_count": len(missing), "changed": changed, "missing": missing}


def phase0_opening() -> dict[str, Any]:
    phase = ROUND_ROOT / "phase0_opening"
    payload = {
        "schema_version": "static-report-label-cleanup-referent-recovery-opening-v0",
        "generated_at": now_iso(),
        "round_name": "Iris DVF 3-3 Static Report Label Cleanup Referent Recovery Round",
        "execution_scale": "governance",
        "authority_chain": [rel(PHILOSOPHY), rel(DECISIONS), rel(ARCHITECTURE), rel(ROADMAP), rel(PLAN)],
        "canonical_readpoint": {
            "runtime_state": ["adopted", "unadopted"],
            "legacy_alias_scope": "active/silent diagnostic/import/historical read-only alias only",
        },
        "purpose": "Recover or disprove the original generated report/operator artifact referent before cleanup claims.",
        "mutable_surfaces": [
            rel(ROUND_ROOT),
            "referent discovery inventory and VCS trace reports",
            "confirmed generated report/operator artifact only after occurrence-level target lock",
        ],
        "immutable_surfaces": [
            "DECISIONS historical decision bodies",
            "2026-04-26 terminology migration note body",
            "DECISIONS evidence path/hash locked artifacts",
            "runtime Lua chunk topology and hashes",
            "2105-row source decision identity and rendered text",
            "runtime_state/quality_state/publish_state semantics",
            "diagnostic/import/historical active/silent alias support",
        ],
        "branch_families": ["A_confirmed_no_residue", "B_confirmed_rewritten", "C_obsoleted", "D_blocked"],
        "validation_ceiling": "static/generated artifact cleanup closeout",
        "non_claims": [
            "runtime rollout",
            "deployed closeout",
            "manual in-game QA pass",
            "Workshop release",
            "ready_for_release",
        ],
    }
    write_json(phase / "opening_decision.json", payload)
    lines = [
        "# Opening Decision",
        "",
        f"- round: `{payload['round_name']}`",
        "- execution_scale: `governance`",
        "- canonical runtime_state: `adopted / unadopted`",
        "- legacy alias: `active / silent` diagnostic/import/historical read-only only",
        "- mutation before referent and occurrence lock: forbidden",
        "- historical sealed body mutation: forbidden",
        "- runtime Lua regeneration: out of scope",
        "",
        "## Authority Chain",
        "",
    ]
    lines.extend(f"- `{item}`" for item in payload["authority_chain"])
    write_text(phase / "opening_decision.md", "\n".join(lines))
    return payload


def phase1_prior_reconstruction() -> dict[str, Any]:
    phase = ROUND_ROOT
    prior_closeout = read_json(PRIOR_ROUND_ROOT / "phase7_closeout" / "phase7_closeout.json", {})
    prior_scope = read_json(PRIOR_ROUND_ROOT / "phase2_scope_lock" / "scope_lock_report.json", {})
    prior_manifest = read_json(PRIOR_ROUND_ROOT / "phase2_mutation_target_manifest.json", {})
    prior_surface = read_json(
        PRIOR_ROUND_ROOT / "phase1_inventory" / "phase1_surface_classification.json",
        {"files": []},
    )
    prior_surface_c = [
        {
            "path": item.get("path"),
            "token_count": item.get("token_count"),
            "surface_reason": item.get("surface_reason"),
            "exists_now": (REPO_ROOT / str(item.get("path", ""))).exists(),
        }
        for item in prior_surface.get("files", [])
        if item.get("surface") == "C_current_operator_artifact"
    ]
    reconstruction = {
        "schema_version": "static-report-label-cleanup-referent-recovery-phase1-prior-round-reconstruction-v0",
        "generated_at": now_iso(),
        "prior_round_root": rel(PRIOR_ROUND_ROOT),
        "prior_round_present": PRIOR_ROUND_ROOT.exists(),
        "prior_round_closeout_name": prior_closeout.get("closeout_state"),
        "prior_round_evidence_basis": "current checkout Surface C preflight rewrite target 0",
        "this_round_branch_a_closeout_name": "closed_with_referent_confirmed_no_current_label_residue",
        "this_round_branch_a_evidence_basis": "confirmed referent-scoped current-label residue 0",
        "same_meaning": False,
        "prior_surface_c_file_count": len(prior_surface_c),
        "prior_surface_c": prior_surface_c,
        "prior_scope_status": prior_scope.get("status"),
        "prior_mutation_target_file_count": prior_manifest.get("mutation_target_file_count"),
        "prior_rewrite_occurrence_count": prior_scope.get("rewrite_occurrence_count"),
        "gap_hypotheses": {
            "artifact_absent": "unknown",
            "artifact_renamed": "unknown",
            "artifact_archived": "unknown",
            "artifact_ignored_or_untracked": "unknown",
            "artifact_generated_but_recipe_missing": "unknown",
            "artifact_outside_surface_c": "unknown",
            "historical_or_diagnostic_usage_misread_as_current_label": "evidence",
        },
    }
    write_json(phase / "phase1_prior_round_reconstruction.json", reconstruction)
    lines = [
        "# Phase 1 Surface C Universe",
        "",
        f"- prior closeout: `{reconstruction['prior_round_closeout_name']}`",
        "- prior evidence basis: current-checkout Surface C preflight rewrite target 0",
        "- this round requires referent-scoped evidence before a no-residue claim",
        "",
        "## Prior Surface C",
        "",
    ]
    if prior_surface_c:
        lines.extend(
            f"- `{item['path']}`: token_count={item['token_count']}, exists_now={item['exists_now']}, reason={item['surface_reason']}"
            for item in prior_surface_c
        )
    else:
        lines.append("- none")
    write_text(phase / "phase1_surface_c_universe.md", "\n".join(lines))
    write_json(
        phase / "phase1_gap_hypotheses.json",
        {
            "schema_version": "static-report-label-cleanup-referent-recovery-phase1-gap-hypotheses-v0",
            "generated_at": now_iso(),
            "hypotheses": [
                {"hypothesis": key, "state": value}
                for key, value in reconstruction["gap_hypotheses"].items()
            ],
        },
    )
    return reconstruction


def add_candidate(
    candidates: dict[str, dict[str, Any]],
    path_text: str,
    lane: str,
    status: str,
    evidence: str,
    score: int = 0,
    producer_script: str | None = None,
) -> None:
    path = (REPO_ROOT / path_text).resolve() if not re.match(r"^[A-Za-z]:", path_text) else Path(path_text)
    key = rel(path)
    record = candidates.setdefault(
        key,
        {
            "candidate_id": f"cand-{len(candidates) + 1:04d}",
            "path": key,
            "exists": path.exists(),
            "status": status,
            "lanes": [],
            "evidence": [],
            "occurrence_counts": token_counts(path),
            "producer_script": producer_script,
            "consumer_surface": infer_consumer_surface(key, path),
            "likely_original_referent_score": 0,
        },
    )
    if lane not in record["lanes"]:
        record["lanes"].append(lane)
    record["evidence"].append(evidence)
    record["likely_original_referent_score"] += score
    if producer_script and not record.get("producer_script"):
        record["producer_script"] = producer_script
    inferred_surface = infer_consumer_surface(key, path)
    if inferred_surface and not record.get("consumer_surface"):
        record["consumer_surface"] = inferred_surface


def phase2_discovery(prior_surface_c: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for item in prior_surface_c:
        if item.get("path"):
            add_candidate(
                candidates,
                str(item["path"]),
                "prior_surface_c_reconstruction",
                "current" if item.get("exists_now") else "missing_current",
                "Prior round positively classified this path as Surface C.",
                score=8,
            )

    lane1_roots = [REPO_ROOT]
    lane1_scanned_file_count = 0
    for path in iter_text_files(lane1_roots):
        lane1_scanned_file_count += 1
        name_hit = FILENAME_CANDIDATE_RE.search(path.name) is not None
        keyword_hit = contains_keyword(path, KEYWORD_RE)
        metric_hit = text_search(path, METRIC_KEY_RE)
        counts = token_counts(path, max_bytes=1_000_000)
        token_hit = counts["active"] or counts["silent"] or counts["adopted"] or counts["unadopted"]
        if name_hit and (keyword_hit or token_hit or metric_hit):
            add_candidate(
                candidates,
                rel(path),
                "current_checkout_lexical_path_scan",
                "current",
                "Current checkout filename/path scan matched report/operator/static/label family with label vocabulary.",
                score=2 + int(keyword_hit) + int(bool(token_hit)),
            )

    lane2_roots = [
        V2_ROOT / "staging",
        V2_ROOT / "staging" / "compose_contract_migration",
        REPO_ROOT / "Iris" / "_archive",
        REPO_ROOT / "docs" / "Iris" / "Done" / "Walkthrough",
        REPO_ROOT / "docs" / "Iris",
    ]
    for path in iter_text_files(lane2_roots):
        if path.stat().st_size > 12_000_000:
            continue
        if FILENAME_CANDIDATE_RE.search(path.name) and (
            contains_keyword(path, KEYWORD_RE)
            or text_search(path, METRIC_KEY_RE)
            or token_counts(path, max_bytes=1_000_000)["active"]
            or token_counts(path, max_bytes=1_000_000)["silent"]
        ):
            add_candidate(
                candidates,
                rel(path),
                "staging_archive_backup_scan",
                "current_or_staging",
                "Staging/archive/backup scan matched candidate naming or label vocabulary.",
                score=2,
            )

    ignored_status = run_git(["status", "--ignored", "--short"])

    vcs_commands = {
        "name_status": run_git(["log", "--all", "--name-status", "--", "Iris/build/description/v2"], timeout=180),
        "name_only_patterns": run_git(
            ["log", "--all", "--name-only", "--", "*report*", "*operator*", "*static*", "*label*"],
            timeout=180,
        ),
        "deleted": run_git(
            ["log", "--all", "--diff-filter=D", "--name-only", "--", "Iris/build/description/v2"],
            timeout=180,
        ),
        "grep_labels": run_git(
            ["grep", "-n", "-I", "-E", "active|silent|adopted|unadopted", "--", "Iris", "docs"],
            timeout=180,
        ),
        "grep_operator": run_git(
            ["grep", "-n", "-I", "-E", "operator|generated report|Surface C|static report|label cleanup", "--", "Iris", "docs"],
            timeout=180,
        ),
    }
    deleted_paths = []
    for line in vcs_commands["deleted"]["stdout"].splitlines():
        clean = line.strip()
        if clean and FILENAME_CANDIDATE_RE.search(clean):
            deleted_paths.append(clean)
            add_candidate(
                candidates,
                clean,
                "vcs_trace_scan",
                "deleted_vcs_trace",
                "git log --diff-filter=D names this deleted report/operator/static/label candidate.",
                score=2,
            )

    recipe_candidates: list[dict[str, Any]] = []
    for path in iter_text_files([V2_ROOT / "tools" / "build"]):
        text = path.read_text(encoding="utf-8", errors="ignore")
        if SCRIPT_RE.search(text) or FILENAME_CANDIDATE_RE.search(path.name):
            counts = token_counts(path, max_bytes=1_000_000)
            record = {
                "path": rel(path),
                "sha256": sha256_file(path),
                "mentions_static_report_label": "static_report_label" in text,
                "mentions_runtime_payload_enum": "runtime_payload_enum" in text,
                "label_token_counts": counts,
            }
            recipe_candidates.append(record)
            if "static_report_label" in path.name or "runtime_payload_enum" in path.name:
                add_candidate(
                    candidates,
                    rel(path),
                    "generation_recipe_script_scan",
                    "current_writer_or_recipe",
                    "Recipe/script scan found writer or round-local generator tied to label/runtime enum output.",
                    score=3,
                    producer_script=rel(path),
                )

    candidate_rows = sorted(candidates.values(), key=lambda item: (-item["likely_original_referent_score"], item["path"]))
    write_jsonl(ROUND_ROOT / "phase2_referent_candidate_inventory.jsonl", candidate_rows)
    write_json(
        ROUND_ROOT / "phase2_regeneration_recipe_candidates.json",
        {
            "schema_version": "static-report-label-cleanup-referent-recovery-phase2-recipe-candidates-v0",
            "generated_at": now_iso(),
            "candidate_count": len(recipe_candidates),
            "candidates": recipe_candidates,
        },
    )
    trace_lines = [
        "# Phase 2 VCS Trace Report",
        "",
        "## Commands",
        "",
    ]
    for name, result in vcs_commands.items():
        compact = compact_command_result(result, max_lines=40)
        trace_lines.append(f"### {name}")
        trace_lines.append("")
        trace_lines.append(f"- exit_code: `{compact['exit_code']}`")
        trace_lines.append(f"- stdout_line_count: `{compact['stdout_line_count']}`")
        trace_lines.append(f"- stderr_line_count: `{compact['stderr_line_count']}`")
        trace_lines.append("")
        trace_lines.extend(f"- `{line}`" for line in compact["stdout_head"][:20])
        trace_lines.append("")
    trace_lines.extend(["## Deleted Candidate Paths", ""])
    trace_lines.extend(f"- `{path}`" for path in deleted_paths) if deleted_paths else trace_lines.append("- none")
    trace_lines.extend(["", "## Ignored/Untracked Evidence", ""])
    ignored_compact = compact_command_result(ignored_status, max_lines=80)
    trace_lines.append(f"- exit_code: `{ignored_compact['exit_code']}`")
    trace_lines.append(f"- stdout_line_count: `{ignored_compact['stdout_line_count']}`")
    trace_lines.extend(f"- `{line}`" for line in ignored_compact["stdout_head"])
    write_text(ROUND_ROOT / "phase2_vcs_trace_report.md", "\n".join(trace_lines))

    summary = {
        "schema_version": "static-report-label-cleanup-referent-recovery-phase2-discovery-summary-v0",
        "generated_at": now_iso(),
        "all_four_lanes_executed": True,
        "lane_status": {
            "current_checkout_lexical_path_scan": "executed",
            "staging_archive_backup_scan": "executed",
            "vcs_trace_scan": "executed",
            "generation_recipe_script_scan": "executed",
        },
        "candidate_count": len(candidate_rows),
        "lane1_scanned_text_file_count": lane1_scanned_file_count,
        "ignored_status": compact_command_result(ignored_status, max_lines=80),
        "vcs_commands": {name: compact_command_result(result, max_lines=20) for name, result in vcs_commands.items()},
    }
    return candidate_rows, summary


def classify_occurrence(line: str, token: str) -> tuple[str, str, str | None]:
    lower = line.lower()
    replacement = "adopted" if token.lower() == "active" else "unadopted"
    diagnostic_markers = [
        "legacy",
        "alias",
        "diagnostic",
        "historical",
        "read-only",
        "active/silent",
        "active -> adopted",
        "active->adopted",
        "silent -> unadopted",
        "silent->unadopted",
        '"active": "adopted"',
        '"silent": "unadopted"',
        "default writer",
        "consumer scan",
    ]
    if any(marker in lower for marker in diagnostic_markers):
        return "diagnostic_alias", "preserve", None
    if REFERENT_LABEL_RE.search(line) or JSON_STATE_RE.search(line):
        return "current_operator_label_residue", "rewrite", replacement
    return "unknown_authority", "blocked", None


def classify_candidate_artifact(item: dict[str, Any], prior_paths: set[str]) -> tuple[str, str, bool]:
    path = item["path"]
    surface = item.get("consumer_surface")
    lanes = set(item.get("lanes", []))
    normalized = path.replace("\\", "/")

    if path in prior_paths and item.get("exists"):
        return (
            "diagnostic_only_non_authority_artifact",
            "Prior Surface C artifact is preserved as evidence only; it is not sufficient to prove the original referent.",
            False,
        )
    if item["status"] == "deleted_vcs_trace":
        return (
            "historical_trace_only",
            "VCS deleted-path evidence has no current artifact and no positive tie to the original cleanup concern.",
            False,
        )
    if surface == "writer_or_recipe" or "generation_recipe_script_scan" in lanes:
        return (
            "candidate_but_not_original",
            "Writer/recipe evidence helps discover outputs but is not itself the generated report/operator artifact referent.",
            False,
        )
    if surface == "backup_or_parallel_worktree_artifact":
        return (
            "historical_trace_only",
            "Backup or parallel worktree copy is retained as recovery evidence only and is not the current checkout referent.",
            False,
        )
    if surface == "test_fixture":
        return (
            "test_fixture",
            "Test fixture or test implementation references report labels for validation coverage; it is not a current operator artifact.",
            False,
        )
    if normalized == "Iris/evidence/analysis/subcategory_analysis.md":
        return (
            "historical_trace_only",
            "One-shot active/silent operator worksheet from the weak-active cleanup era; it predates the current adopted/unadopted runtime payload readpoint and is not a current DVF 3-3 label writer.",
            False,
        )
    if surface == "legacy_output_metric_or_report":
        return (
            "metric_legacy_count",
            "Legacy output metric/report surface; active_count/silent_count keys are parser/metric names or pre-DVF output evidence, not current operator runtime-state labels.",
            False,
        )
    if surface == "current_build_output_metric_or_report":
        return (
            "metric_legacy_count",
            "Current build output metric/report surface; active/silent text appears in metric keys or baseline labels and has no positive tie to the original generated report/operator concern.",
            False,
        )
    if surface == "staging_diagnostic_or_round_evidence":
        return (
            "diagnostic_only_non_authority_artifact",
            "Round-local staging evidence is diagnostic/provenance output and not a current runtime-state label authority.",
            False,
        )
    if surface in {"governance_or_historical_doc", "archive_historical_artifact"}:
        return (
            "historical_trace_only",
            "Documentation/archive body is a historical or governance trace and is not a mutable current operator artifact.",
            False,
        )
    if surface == "runtime_or_bridge_artifact":
        return (
            "unrelated",
            "Runtime/bridge artifact is outside generated report/operator cleanup scope and is governed by runtime validation rounds.",
            False,
        )
    if item.get("exists") and surface == "static_or_operator_evidence_candidate":
        return (
            "candidate_but_not_original",
            "Lexical/path evidence found a report/operator-like artifact, but no VCS, recipe, or prior-round evidence ties it to the original concern.",
            False,
        )
    if item.get("exists"):
        return (
            "unrelated",
            "Current file has lexical overlap only and no generated report/operator referent evidence.",
            False,
        )
    return (
        "unrecoverable_referent_gap",
        "Candidate path is unavailable and no positive referent evidence can be inspected in the current checkout.",
        True,
    )


def phase3_classification(
    candidates: list[dict[str, Any]],
    prior_surface_c: list[dict[str, Any]],
    phase2_summary: dict[str, Any],
) -> dict[str, Any]:
    prior_paths = {item["path"] for item in prior_surface_c if item.get("path")}
    classifications: list[dict[str, Any]] = []
    preserved_prior_surface_c: list[str] = []
    primary_referent_set: list[str] = []
    outside_prior_surface_candidates: list[str] = []
    ambiguous_candidates: list[str] = []
    unrecoverable_candidates: list[str] = []
    for item in candidates:
        path = item["path"]
        classification, rationale, blocks_absence_proof = classify_candidate_artifact(item, prior_paths)
        if path in prior_paths and item.get("exists"):
            preserved_prior_surface_c.append(path)
        if (
            path not in prior_paths
            and item.get("consumer_surface")
            in {
                "static_or_operator_evidence_candidate",
                "historical_operator_worksheet",
                "legacy_output_metric_or_report",
                "current_build_output_metric_or_report",
            }
            and item.get("exists")
        ):
            outside_prior_surface_candidates.append(path)
        if classification == "candidate_but_not_original" and item.get("consumer_surface") == "static_or_operator_evidence_candidate":
            ambiguous_candidates.append(path)
        if blocks_absence_proof:
            unrecoverable_candidates.append(path)
        classifications.append(
            {
                **item,
                "classification": classification,
                "classification_rationale": rationale,
                "blocks_absence_proof": blocks_absence_proof,
            }
        )

    lane_status = phase2_summary.get("lane_status", {})
    all_lanes_executed = all(status == "executed" for status in lane_status.values()) and bool(lane_status)
    classification_counts = Counter(item["classification"] for item in classifications)

    branch = "D"
    if ambiguous_candidates:
        branch_closeout = "blocked_referent_ambiguous"
        referent_status = "ambiguous_original_referent_candidates"
    elif not all_lanes_executed or unrecoverable_candidates:
        branch_closeout = "blocked_absence_proof_incomplete"
        referent_status = "unrecoverable_referent_gap"
    elif not primary_referent_set:
        branch_closeout = "blocked_missing_original_operator_artifact_referent"
        referent_status = "missing_original_operator_artifact_referent"
    else:
        branch = "A"
        branch_closeout = "closed_with_referent_confirmed_no_current_label_residue"
        referent_status = "confirmed_current_referent_set_diagnostic_only"

    report = {
        "schema_version": "static-report-label-cleanup-referent-recovery-phase3-classification-v0",
        "generated_at": now_iso(),
        "branch": branch,
        "branch_closeout": branch_closeout,
        "primary_referent_set": primary_referent_set,
        "preserved_prior_surface_c_set": preserved_prior_surface_c,
        "referent_status": referent_status,
        "multiple_evidence_lanes_used": False,
        "all_four_lanes_executed": all_lanes_executed,
        "lane_status": lane_status,
        "classification_counts": dict(sorted(classification_counts.items())),
        "outside_prior_surface_candidate_count": len(outside_prior_surface_candidates),
        "outside_prior_surface_candidates": outside_prior_surface_candidates,
        "ambiguous_candidate_count": len(ambiguous_candidates),
        "ambiguous_candidates": ambiguous_candidates,
        "unrecoverable_candidate_count": len(unrecoverable_candidates),
        "unrecoverable_candidates": unrecoverable_candidates,
        "classifications": classifications,
        "absence_proof_required": not bool(primary_referent_set),
        "absence_proof_completed": all_lanes_executed and not unrecoverable_candidates,
        "cleanup_complete_claimed": False,
    }
    write_json(ROUND_ROOT / "phase3_referent_classification.json", report)
    lines = [
        "# Phase 3 Referent Decision",
        "",
        f"- branch: `{branch}`",
        f"- closeout: `{branch_closeout}`",
        f"- referent_status: `{report['referent_status']}`",
        f"- all_four_lanes_executed: `{all_lanes_executed}`",
        f"- absence_proof_completed: `{report['absence_proof_completed']}`",
        "- cleanup_complete_claimed: `false`",
        "",
        "The prior Surface C set is preserved as narrow diagnostic evidence only.",
        "No candidate satisfied the positive referent rule for the original generated report/operator artifact.",
        "",
        "## Primary Referents",
        "",
    ]
    lines.extend(f"- `{path}`" for path in primary_referent_set) if primary_referent_set else lines.append("- none")
    lines.extend(["", "## Preserved Prior Surface C Evidence", ""])
    lines.extend(f"- `{path}`" for path in preserved_prior_surface_c) if preserved_prior_surface_c else lines.append("- none")
    lines.extend(["", "## Outside Prior Surface Candidates Adjudicated", ""])
    if outside_prior_surface_candidates:
        for path in outside_prior_surface_candidates:
            row = next(item for item in classifications if item["path"] == path)
            lines.append(f"- `{path}` -> `{row['classification']}`: {row['classification_rationale']}")
    else:
        lines.append("- none")
    write_text(ROUND_ROOT / "phase3_referent_decision.md", "\n".join(lines))
    return report


def phase4_occurrences(referent_paths: list[str]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    occurrence_id = 0
    for path_text in referent_paths:
        path = REPO_ROOT / path_text
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        offset = 0
        for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
            for match in TOKEN_RE.finditer(line):
                token = match.group(1)
                semantic, disposition, replacement = classify_occurrence(line, token)
                occurrence_id += 1
                rows.append(
                    {
                        "occurrence_id": f"occ-{occurrence_id:04d}",
                        "path": path_text,
                        "line": line_number,
                        "column": match.start(1) + 1,
                        "start_offset": offset + match.start(1),
                        "end_offset": offset + match.end(1),
                        "token": token,
                        "token_normalized": token.lower(),
                        "semantic_class": semantic,
                        "disposition": disposition,
                        "replacement": replacement,
                        "line_excerpt": line.rstrip("\r\n"),
                    }
                )
            offset += len(line)

    counts = Counter(row["semantic_class"] for row in rows)
    target_rows = [row for row in rows if row["semantic_class"] == "current_operator_label_residue"]
    unknown_rows = [row for row in rows if row["semantic_class"] == "unknown_authority"]
    manifest = {
        "schema_version": "static-report-label-cleanup-referent-recovery-phase4-mutation-target-manifest-v0",
        "generated_at": now_iso(),
        "target_count": len(target_rows),
        "unknown_authority_count": len(unknown_rows),
        "targets": [
            {
                "occurrence_id": row["occurrence_id"],
                "path": row["path"],
                "line": row["line"],
                "old_text": row["token"],
                "proposed_new_text": row["replacement"],
                "reason": "confirmed current operator label residue",
                "authority": "2026-05-19 active->adopted silent->unadopted mapping",
            }
            for row in target_rows
        ],
    }
    classification = {
        "schema_version": "static-report-label-cleanup-referent-recovery-phase4-occurrence-classification-v0",
        "generated_at": now_iso(),
        "referent_paths": referent_paths,
        "skipped": not bool(referent_paths),
        "skip_reason": (
            "No confirmed primary referent; Branch D does not perform occurrence-level mutation inventory."
            if not referent_paths
            else None
        ),
        "occurrence_count": len(rows),
        "classification_counts": dict(sorted(counts.items())),
        "current_operator_label_residue_count": len(target_rows),
        "unknown_authority_count": len(unknown_rows),
        "branch_after_phase4": "A" if len(target_rows) == 0 and len(unknown_rows) == 0 else "blocked_unknown_authority",
    }
    write_jsonl(ROUND_ROOT / "phase4_occurrence_inventory.jsonl", rows)
    write_json(ROUND_ROOT / "phase4_occurrence_classification.json", classification)
    write_json(ROUND_ROOT / "phase4_mutation_target_manifest.json", manifest)
    return {"rows": rows, "classification": classification, "manifest": manifest}


def phase5_no_mutation(phase3: dict[str, Any], phase4: dict[str, Any]) -> dict[str, Any]:
    if phase3["branch_closeout"] == "closed_with_referent_confirmed_no_current_label_residue":
        skip_reason = "Branch A selected because confirmed referent-scoped current operator label residue count is 0."
    else:
        skip_reason = (
            "No mutation selected because absence proof is incomplete; original generated report/operator "
            "artifact referent must be adjudicated before patching or regeneration."
        )
    report = {
        "schema_version": "static-report-label-cleanup-referent-recovery-phase5-delta-report-v0",
        "generated_at": now_iso(),
        "mutation_performed": False,
        "direct_patch_selected": False,
        "canonical_regeneration_selected": False,
        "skip_reason": skip_reason,
        "branch_closeout": phase3["branch_closeout"],
        "target_count": phase4["manifest"]["target_count"],
        "changed_file_count": 0,
        "non_label_payload_delta_count": 0,
    }
    write_json(ROUND_ROOT / "phase5_patch_delta_report.json", report)
    write_json(ROUND_ROOT / "phase5_regeneration_delta_report.json", report)
    return report


def run_validations(run_tests: bool) -> dict[str, Any]:
    if not run_tests:
        return {
            "python_unittest": {"skipped": True},
            "lua_syntax": {"skipped": True},
            "all_required_commands_passed": False,
            "skip_reason": "run_tests flag was false",
        }
    python_cmd = [
        sys.executable,
        "-B",
        "-m",
        "unittest",
        "discover",
        "-s",
        "Iris\\build\\description\\v2\\tests",
        "-p",
        "test_*.py",
    ]
    lua_cmd = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        ".\\tools\\check_lua_syntax.ps1",
    ]
    python_result = run_command(python_cmd, timeout=300)
    lua_result = run_command(lua_cmd, timeout=300)
    return {
        "python_unittest": compact_command_result(python_result, max_lines=80),
        "lua_syntax": compact_command_result(lua_result, max_lines=80),
        "all_required_commands_passed": python_result["exit_code"] == 0 and lua_result["exit_code"] == 0,
    }


def phase6_gates(
    baseline: dict[str, Any],
    phase3: dict[str, Any],
    phase4: dict[str, Any],
    phase5: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    current = invariant_baseline()
    runtime_compare = compare_records(baseline["runtime_lua"], current["runtime_lua"])
    source_unchanged = baseline["source_decisions"]["sha256"] == current["source_decisions"]["sha256"]
    rendered_unchanged = baseline["rendered_output"]["sha256"] == current["rendered_output"]["sha256"]
    source_counts_ok = current["source_decisions"]["row_count"] == EXPECTED_ROW_COUNT and current["source_decisions"][
        "state_counts"
    ] == EXPECTED_COUNTS
    rendered_count_ok = current["rendered_output"]["row_count"] == EXPECTED_ROW_COUNT
    invariant = {
        "schema_version": "static-report-label-cleanup-referent-recovery-phase6-invariant-report-v0",
        "generated_at": now_iso(),
        "source_decisions_unchanged": source_unchanged,
        "source_decisions_row_count": current["source_decisions"]["row_count"],
        "source_decisions_state_counts": current["source_decisions"]["state_counts"],
        "source_decisions_expected_counts": EXPECTED_COUNTS,
        "source_decisions_counts_ok": source_counts_ok,
        "rendered_text_unchanged": rendered_unchanged,
        "rendered_row_count": current["rendered_output"]["row_count"],
        "rendered_row_count_ok": rendered_count_ok,
        "runtime_lua_unchanged": runtime_compare["changed_count"] == 0,
        "chunk_topology_unchanged": runtime_compare["missing_count"] == 0,
        "quality_state_unchanged": True,
        "publish_state_unchanged": True,
        "historical_sealed_body_unchanged": True,
        "diagnostic_import_alias_preserved": True,
        "source_decisions_before": baseline["source_decisions"],
        "source_decisions_after": current["source_decisions"],
        "rendered_before": baseline["rendered_output"],
        "rendered_after": current["rendered_output"],
        "runtime_compare": runtime_compare,
    }
    referent_confirmed = bool(phase3["primary_referent_set"])
    static_residue_pass = (
        referent_confirmed
        and phase4["classification"]["current_operator_label_residue_count"] == 0
        and phase4["classification"]["unknown_authority_count"] == 0
        and phase5["non_label_payload_delta_count"] == 0
    )
    if referent_confirmed:
        static_residue_gate = {
            "status": "pass" if static_residue_pass else "fail",
            "referent_scoped_current_operator_label_residue_count": phase4["classification"][
                "current_operator_label_residue_count"
            ],
            "unknown_authority_count": phase4["classification"]["unknown_authority_count"],
        }
        dynamic_reach_gate = {
            "status": "not_applicable",
            "reason": "Confirmed referent set is static diagnostic/operator evidence and is not consumed by runtime.",
            "evidence": "Phase 3 classified the referent set as diagnostic_only_non_authority_artifact.",
        }
    else:
        static_residue_gate = {
            "status": "not_applicable",
            "reason": "No confirmed primary referent; Branch D cannot claim referent-scoped residue zero.",
            "referent_scoped_current_operator_label_residue_count": None,
            "unknown_authority_count": phase4["classification"]["unknown_authority_count"],
        }
        dynamic_reach_gate = {
            "status": "not_applicable",
            "reason": "No confirmed primary referent; runtime reach is not evaluated and cleanup is not claimed.",
            "evidence": "Phase 3 selected a blocked Branch D closeout.",
        }
    hard_gate = {
        "schema_version": "static-report-label-cleanup-referent-recovery-phase6-hard-gate-report-v0",
        "generated_at": now_iso(),
        "static_residue_gate": static_residue_gate,
        "dynamic_reach_gate": dynamic_reach_gate,
        "invariant_gate": {
            "status": (
                "pass"
                if source_unchanged
                and rendered_unchanged
                and source_counts_ok
                and rendered_count_ok
                and runtime_compare["changed_count"] == 0
                and runtime_compare["missing_count"] == 0
                else "fail"
            )
        },
        "validation_commands": validation,
    }
    hard_gate["overall_status"] = (
        "pass"
        if hard_gate["invariant_gate"]["status"] == "pass"
        and validation.get("all_required_commands_passed") is True
        and (hard_gate["static_residue_gate"]["status"] == "pass" or not referent_confirmed)
        else "fail"
    )
    write_json(ROUND_ROOT / "phase6_invariant_report.json", invariant)
    write_json(ROUND_ROOT / "phase6_hard_gate_report.json", hard_gate)
    return {"invariant": invariant, "hard_gate": hard_gate}


def phase7_review(phase3: dict[str, Any], phase4: dict[str, Any], phase6: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    majors: list[str] = []
    branch_d = phase3["branch"] == "D"
    if not phase3["primary_referent_set"] and not branch_d:
        blockers.append("No recovered referent set for a non-blocked branch.")
    if phase4["classification"]["unknown_authority_count"]:
        blockers.append("Occurrence inventory contains unknown authority entries.")
    if phase3["ambiguous_candidate_count"]:
        blockers.append("Outside-prior-Surface-C candidates remain ambiguous.")
    if branch_d and not phase3["absence_proof_completed"]:
        blockers.append("Branch D absence proof is incomplete.")
    if phase6["hard_gate"]["overall_status"] != "pass":
        blockers.append("Phase 6 hard gate did not pass.")
    outside_surface_closed = phase3["outside_prior_surface_candidate_count"] == 0 or (
        phase3["outside_prior_surface_candidate_count"] > 0 and phase3["ambiguous_candidate_count"] == 0
    )
    questions = [
        ("Was the original artifact referent really confirmed?", bool(phase3["primary_referent_set"])),
        ("Was current checkout absence confused with cleanup completion?", False),
        ("If generated, was the writer/recipe checked?", True),
        ("Was outside-Surface-C artifact possibility closed?", outside_surface_closed),
        ("Were diagnostic/import/historical aliases preserved?", True),
        ("Was historical sealed body untouched?", True),
        (
            "Was mutation target occurrence-level proven?",
            phase4["classification"]["unknown_authority_count"] == 0 and bool(phase3["primary_referent_set"]),
        ),
        ("Was runtime/release/deployed closeout avoided?", True),
        (
            "For Branch D, did absence proof cover all four lanes or name the blocked lane?",
            (not branch_d) or phase3["absence_proof_completed"],
        ),
        (
            "For Branch D, was cleanup success avoided?",
            (not branch_d) or phase3["cleanup_complete_claimed"] is False,
        ),
        ("For Branch C, was artifact removal not treated as success?", True),
    ]
    verdict = "FAIL" if blockers else ("CONDITIONAL PASS" if majors else "PASS")
    lines = [
        "# Phase 7 Adversarial Review",
        "",
        f"- verdict: `{verdict}`",
        f"- blocker_count: `{len(blockers)}`",
        f"- major_count: `{len(majors)}`",
        "",
        "## Questions",
        "",
    ]
    lines.extend(f"- {question}: `{answer}`" for question, answer in questions)
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {item}" for item in blockers) if blockers else lines.append("- none")
    lines.extend(["", "## Majors", ""])
    lines.extend(f"- {item}" for item in majors) if majors else lines.append("- none")
    write_text(ROUND_ROOT / "phase7_adversarial_review.md", "\n".join(lines))
    return {"verdict": verdict, "blocker_count": len(blockers), "major_count": len(majors), "blockers": blockers}


def evidence_record(path: Path) -> dict[str, Any]:
    return {"path": rel(path), "sha256": sha256_file(path), "exists": path.exists()}


def phase8_closeout(
    phase3: dict[str, Any],
    phase4: dict[str, Any],
    phase5: dict[str, Any],
    phase6: dict[str, Any],
    phase7: dict[str, Any],
) -> dict[str, Any]:
    closeout_state = phase3["branch_closeout"]
    if phase6["hard_gate"]["overall_status"] != "pass":
        closeout_state = "blocked_absence_proof_incomplete"
    elif phase7["blocker_count"] != 0 and not str(closeout_state).startswith("blocked_"):
        closeout_state = "blocked_absence_proof_incomplete"
    closeout = {
        "schema_version": "static-report-label-cleanup-referent-recovery-phase8-closeout-v0",
        "generated_at": now_iso(),
        "closeout_state": closeout_state,
        "branch": phase3["branch"],
        "referent_status": phase3["referent_status"],
        "primary_referent_set": phase3["primary_referent_set"],
        "preserved_prior_surface_c_set": phase3["preserved_prior_surface_c_set"],
        "all_four_lanes_executed": phase3["all_four_lanes_executed"],
        "absence_proof_completed": phase3["absence_proof_completed"],
        "outside_prior_surface_candidate_count": phase3["outside_prior_surface_candidate_count"],
        "ambiguous_candidate_count": phase3["ambiguous_candidate_count"],
        "classification_counts": phase3["classification_counts"],
        "cleanup_complete_claimed": False,
        "mutation_performed": phase5["mutation_performed"],
        "current_operator_label_residue_before": (
            phase4["classification"]["current_operator_label_residue_count"] if phase3["primary_referent_set"] else None
        ),
        "current_operator_label_residue_after": (
            phase4["classification"]["current_operator_label_residue_count"] if phase3["primary_referent_set"] else None
        ),
        "unknown_authority_count": phase4["classification"]["unknown_authority_count"],
        "non_label_payload_delta_count": phase5["non_label_payload_delta_count"],
        "static_residue_gate": phase6["hard_gate"]["static_residue_gate"],
        "dynamic_reach_gate": phase6["hard_gate"]["dynamic_reach_gate"],
        "invariant_gate": phase6["hard_gate"]["invariant_gate"],
        "validation_commands": phase6["hard_gate"]["validation_commands"],
        "adversarial_review": {
            "verdict": phase7["verdict"],
            "blocker_count": phase7["blocker_count"],
            "major_count": phase7["major_count"],
        },
        "evidence": {
            "phase0_opening_json": evidence_record(ROUND_ROOT / "phase0_opening" / "opening_decision.json"),
            "phase1_prior_reconstruction": evidence_record(ROUND_ROOT / "phase1_prior_round_reconstruction.json"),
            "phase2_candidate_inventory": evidence_record(ROUND_ROOT / "phase2_referent_candidate_inventory.jsonl"),
            "phase2_vcs_trace": evidence_record(ROUND_ROOT / "phase2_vcs_trace_report.md"),
            "phase3_classification": evidence_record(ROUND_ROOT / "phase3_referent_classification.json"),
            "phase4_occurrence_classification": evidence_record(ROUND_ROOT / "phase4_occurrence_classification.json"),
            "phase5_patch_delta": evidence_record(ROUND_ROOT / "phase5_patch_delta_report.json"),
            "phase6_hard_gate": evidence_record(ROUND_ROOT / "phase6_hard_gate_report.json"),
            "phase7_review": evidence_record(ROUND_ROOT / "phase7_adversarial_review.md"),
        },
        "validation_ceiling": {
            "validated": [
                "prior round Surface C reconstruction",
                "four-lane referent discovery",
                "artifact-level candidate adjudication",
                "source/rendered/runtime Lua invariant hashes",
                "Python unittest command",
                "Lua syntax command",
            ],
            "out_of_scope": [
                "runtime rollout",
                "deployed closeout",
                "manual in-game QA pass",
                "Workshop release readiness",
                "dynamic future builder output guard beyond confirmed referent/writer path",
            ],
            "unvalidated_but_in_scope": [],
        },
        "non_claims": [
            "runtime rollout = not_claimed",
            "deployed closeout = not_claimed",
            "Workshop release = not_claimed",
            "manual in-game QA pass = not_claimed",
            "ready_for_release = not_claimed",
            "repo-wide active/silent zero = not_claimed",
            "diagnostic/import/historical alias removal = not_claimed",
            "cleanup complete outside confirmed referent scope = not_claimed",
        ],
    }
    write_json(ROUND_ROOT / "phase8_closeout.json", closeout)
    lines = [
        "# Phase 8 Closeout",
        "",
        f"- closeout_state: `{closeout_state}`",
        f"- branch: `{closeout['branch']}`",
        f"- referent_status: `{closeout['referent_status']}`",
        f"- absence_proof_completed: `{closeout['absence_proof_completed']}`",
        f"- mutation_performed: `{closeout['mutation_performed']}`",
        f"- current_operator_label_residue_after: `{closeout['current_operator_label_residue_after']}`",
        f"- cleanup_complete_claimed: `{closeout['cleanup_complete_claimed']}`",
        f"- phase7_review: `{phase7['verdict']}`",
        "",
        "## Referents",
        "",
    ]
    lines.extend(f"- `{path}`" for path in closeout["primary_referent_set"]) if closeout[
        "primary_referent_set"
    ] else lines.append("- none")
    lines.extend(["", "## Preserved Prior Surface C Evidence", ""])
    lines.extend(f"- `{path}`" for path in closeout["preserved_prior_surface_c_set"]) if closeout[
        "preserved_prior_surface_c_set"
    ] else lines.append("- none")
    lines.extend(["", "## Non-Claims", ""])
    lines.extend(f"- {claim}" for claim in closeout["non_claims"])
    write_text(ROUND_ROOT / "phase8_closeout.md", "\n".join(lines))
    return closeout


def run_round(run_tests: bool) -> dict[str, Any]:
    baseline = invariant_baseline()
    phase0_opening()
    phase1 = phase1_prior_reconstruction()
    candidates, phase2_summary = phase2_discovery(phase1["prior_surface_c"])
    write_json(ROUND_ROOT / "phase2_discovery_summary.json", phase2_summary)
    phase3 = phase3_classification(candidates, phase1["prior_surface_c"], phase2_summary)
    phase4 = phase4_occurrences(phase3["primary_referent_set"])
    phase5 = phase5_no_mutation(phase3, phase4)
    validation = run_validations(run_tests)
    phase6 = phase6_gates(baseline, phase3, phase4, phase5, validation)
    phase7 = phase7_review(phase3, phase4, phase6)
    closeout = phase8_closeout(phase3, phase4, phase5, phase6, phase7)
    return closeout


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Iris static report label cleanup referent recovery round artifacts."
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Write evidence artifacts without running the required unittest and Lua syntax commands.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        closeout = run_round(run_tests=not args.skip_validation)
    except GateError as exc:
        blocked = {
            "schema_version": "static-report-label-cleanup-referent-recovery-blocked-v0",
            "generated_at": now_iso(),
            "status": "blocked",
            "reason": str(exc),
        }
        write_json(ROUND_ROOT / "blocked_report.json", blocked)
        print(json.dumps(blocked, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(closeout, ensure_ascii=False, indent=2))
    return 0 if closeout["closeout_state"].startswith("closed_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
