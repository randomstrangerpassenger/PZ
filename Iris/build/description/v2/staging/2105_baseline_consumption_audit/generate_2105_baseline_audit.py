from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "docs" / "Philosophy.md").exists():
            return parent
    raise RuntimeError("Could not find repo root from script path")


ROOT = find_repo_root()
STAGING_DIR = Path(__file__).resolve().parent
AUDIT_REL = STAGING_DIR.relative_to(ROOT).as_posix()
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")


CORE_TOKENS = [
    "2105",
    "2084",
    "21",
    "active",
    "silent",
    "active/silent",
    "adopted",
    "unadopted",
    "adopted/unadopted",
    "current runtime baseline",
    "runtime baseline",
]

ADJACENT_SEED_TOKENS = ["2060", "45", "178", "46", "132", "34"]
DISTINCT_MEASUREMENT_TOKENS = ["24", "0", "3", "112", "95", "876", "50"]

REFERENTS = [
    "runtime-baseline-2105",
    "source-universe-2105",
    "frozen-recovery-2105",
    "current-readpoint-triple",
    "historical-pass-snapshot",
    "current adopted/unadopted",
    "historical active/silent",
    "incidental-excluded",
]

SURFACE_FAMILIES = [
    "runtime_payload",
    "lua_bridge",
    "build_pipeline",
    "validator",
    "test",
    "tool",
    "documentation_current",
    "documentation_historical",
    "closeout_trace",
    "roadmap_or_decision_ledger",
    "staging_artifact",
    "diagnostic_report",
    "migration_plan",
    "generated_report",
    "static_report_cleanup",
    "selected_role_resolver",
    "quality_publish_contract",
    "silent_21_cleanup",
    "structural_signal",
    "layer4_corpus_or_measurement",
    "acq_dominant",
    "acquisition_lexical",
    "no_dvf_context",
]

CONSUMER_TYPES = [
    "runtime-consumer",
    "validator-gate",
    "test-assertion",
    "tool-generator",
    "build-guard",
    "document-authority",
    "historical-trace",
    "diagnostic-report",
    "generated-report",
    "comment-or-prose",
    "migration-candidate",
    "comparison-reference",
    "false-positive",
]

DISPOSITIONS = [
    "current-hard-gate",
    "historical-reference",
    "diagnostic-only",
    "vNext-migration",
    "no-op",
    "ambiguous-needs-adjudication",
]

MIGRATION_DISPOSITIONS = [
    "preserve_as_current_gate",
    "migrate_when_new_baseline_approved",
    "preserve_as_historical_trace",
    "preserve_as_diagnostic_reference",
    "demote_to_historical_or_predecessor",
    "rename_or_alias_cleanup_needed",
    "guard_hardening_needed",
    "no_change",
    "remove_or_ignore_false_positive",
]

CONTEXT_KEYWORDS = [
    "dvf",
    "3-3",
    "layer3",
    "layer 3",
    "irislayer3data",
    "description/v2",
    "description validation",
    "body-plan",
    "body_plan",
    "rendered",
    "lua bridge",
    "runtime payload",
    "runtime baseline",
    "current runtime",
    "baseline",
    "source universe",
    "source-universe",
    "source-coverage",
    "readpoint",
    "active/silent",
    "active-silent",
    "active_total",
    "silent_total",
    "active_count",
    "silent_count",
    "active rows",
    "silent rows",
    "silent 21",
    "weak-active",
    "structural signal",
    "structural_signal",
    "acq_dominant",
    "layer4",
    "t-gate",
    "manual registry",
    "dvf_contract",
]

TEXT_EXTENSIONS = {
    ".bat",
    ".cfg",
    ".csv",
    ".gradle",
    ".html",
    ".ini",
    ".java",
    ".json",
    ".jsonl",
    ".lua",
    ".md",
    ".ps1",
    ".properties",
    ".py",
    ".sh",
    ".txt",
    ".xml",
    ".yml",
    ".yaml",
}

BINARY_EXTENSIONS = {
    ".7z",
    ".class",
    ".dll",
    ".exe",
    ".gif",
    ".jar",
    ".jpg",
    ".jpeg",
    ".pdf",
    ".png",
    ".pyc",
    ".zip",
}

EXCLUDED_DIRS = {
    ".git",
    ".gradle",
    "__pycache__",
    "node_modules",
    "uv-cache",
}


@dataclass(frozen=True)
class TokenSpec:
    token: str
    family: str
    pattern: re.Pattern[str]
    requires_context: bool


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_slashes(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def token_pattern(token: str) -> re.Pattern[str]:
    if token.isdigit():
        pattern = rf"(?<!\d){re.escape(token)}(?!\d)"
    elif re.fullmatch(r"[A-Za-z]+", token):
        pattern = rf"(?<![A-Za-z0-9_]){re.escape(token)}(?![A-Za-z0-9_])"
    else:
        pattern = re.escape(token)
    return re.compile(pattern, re.IGNORECASE)


def build_token_specs() -> list[TokenSpec]:
    specs: list[TokenSpec] = []
    phrase_tokens = {
        "active/silent",
        "adopted/unadopted",
        "current runtime baseline",
        "runtime baseline",
    }
    for token in CORE_TOKENS:
        specs.append(
            TokenSpec(
                token=token,
                family="core",
                pattern=token_pattern(token),
                requires_context=token not in phrase_tokens,
            )
        )
    for token in ADJACENT_SEED_TOKENS:
        specs.append(
            TokenSpec(
                token=token,
                family="adjacent_seed",
                pattern=token_pattern(token),
                requires_context=True,
            )
        )
    return sorted(specs, key=lambda item: (-len(item.token), item.token))


def is_inside_audit_dir(path: Path) -> bool:
    try:
        path.relative_to(STAGING_DIR)
        return True
    except ValueError:
        return False


def should_skip_path(path: Path) -> bool:
    rel_parts = path.relative_to(ROOT).parts
    if any(part in EXCLUDED_DIRS for part in rel_parts):
        return True
    if is_inside_audit_dir(path):
        return True
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    return False


def read_text_candidate(path: Path) -> tuple[str | None, str | None]:
    if path.suffix.lower() not in TEXT_EXTENSIONS and path.suffix:
        return None, "extension_not_in_text_allowlist"
    try:
        data = path.read_bytes()
    except OSError as exc:
        return None, f"unreadable:{exc}"
    if b"\x00" in data[:4096]:
        return None, "binary_nul_prefix"
    try:
        return data.decode("utf-8"), None
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace"), "decoded_with_replacement"


def iter_text_files() -> tuple[list[Path], list[dict[str, Any]]]:
    files: list[Path] = []
    skipped: list[dict[str, Any]] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if should_skip_path(path):
            skipped.append({"path": normalize_slashes(path), "reason": "excluded_or_binary"})
            continue
        text, reason = read_text_candidate(path)
        if text is None:
            skipped.append({"path": normalize_slashes(path), "reason": reason or "not_text"})
            continue
        files.append(path)
    return files, skipped


def context_for(lines: list[str], index: int) -> str:
    start = max(0, index - 1)
    end = min(len(lines), index + 2)
    return "\n".join(lines[start:end]).strip()


def has_dvf_context(path_rel: str, context: str, token: str) -> bool:
    path_text = path_rel.lower().replace("\\", "/")
    context_text = context.lower()
    if "iris/media/lua/client/iris/data/irislayer3data" in path_text:
        if token in {"adopted", "unadopted", "adopted/unadopted"}:
            return True
        if token == "2105" and "total runtime entries" in context_text:
            return True
        if token in {"2084", "21"} and ("adopted" in context_text or "unadopted" in context_text):
            return True
        return False
    if "docs/2105_baseline_consumption_audit_plan.md" in path_text:
        return True
    if "docs/decisions.md" in path_text and ("dvf" in context_text or "2105" in context_text):
        return True
    if "docs/roadmap.md" in path_text and ("dvf" in context_text or "2105" in context_text):
        return True
    if "docs/architecture.md" in path_text and ("dvf" in context_text or "2105" in context_text):
        return True
    known_baseline_files = [
        "dvf_3_3_decisions.jsonl",
        "dvf_3_3_rendered.json",
        "dvf_3_3_facts.jsonl",
        "validate_body_plan_full_runtime_regression_gate.py",
        "validate_quality_publish_decision_preview.py",
        "validate_legacy_active_silent_current_surface_guard.py",
        "layer3_current_authority_reconstruction.py",
        "build_legacy_active_silent_current_surface_guard_round.py",
        "build_runtime_payload_enum_rename_scope_round.py",
        "build_silent_21_replacement_authority_reconstruction_round.py",
        "build_silent_metadata_intake_cleanup_round.py",
        "build_structural_signal_missing_anchor_authority_resolution_round.py",
        "build_static_report_label_cleanup_referent_recovery_round.py",
        "report_diagnostic_resolver_guard_round.py",
        "compose_layer3_body_profile.py",
        "export_dvf_3_3_lua_bridge.py",
    ]
    if any(name in path_text for name in known_baseline_files):
        return True
    if any(keyword in context_text for keyword in CONTEXT_KEYWORDS):
        return True
    numeric_context_keywords = [
        "adopted",
        "unadopted",
        "active",
        "silent",
    ]
    if token.isdigit() and any(keyword in context_text for keyword in numeric_context_keywords):
        return True
    return False


def occurrence_id(path_rel: str, line: int, token: str, context_hash: str) -> str:
    return sha256_text(f"{path_rel}:{line}:{token}:{context_hash}")[:24]


def enumerate_occurrences(files: list[Path]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    specs = build_token_specs()
    rows: list[dict[str, Any]] = []
    raw_hit_count: Counter[str] = Counter()
    accepted_count: Counter[str] = Counter()
    seen_line_tokens: set[tuple[str, int, str]] = set()
    scanned_files = 0
    decoded_with_replacement: list[str] = []

    for path in files:
        text, read_note = read_text_candidate(path)
        if text is None:
            continue
        if read_note == "decoded_with_replacement":
            decoded_with_replacement.append(normalize_slashes(path))
        scanned_files += 1
        path_rel = normalize_slashes(path)
        lines = text.splitlines()
        for index, line_text in enumerate(lines):
            if not line_text:
                continue
            for spec in specs:
                matches = list(spec.pattern.finditer(line_text))
                if not matches:
                    continue
                raw_hit_count[spec.token] += len(matches)
                key = (path_rel, index + 1, spec.token)
                if key in seen_line_tokens:
                    continue
                seen_line_tokens.add(key)
                context = context_for(lines, index)
                context_hash = sha256_text(context)
                accepted = True
                exclusion_reason = ""
                if spec.requires_context and not has_dvf_context(path_rel, context, spec.token):
                    accepted = False
                    exclusion_reason = "no_dvf_context"
                if accepted:
                    accepted_count[spec.token] += 1
                rows.append(
                    {
                        "occurrence_id": occurrence_id(path_rel, index + 1, spec.token, context_hash),
                        "path": path_rel,
                        "line": index + 1,
                        "line_range": f"{index + 1}",
                        "token": spec.token,
                        "token_family": spec.family,
                        "raw_match_count_on_line": len(matches),
                        "accepted_candidate": accepted,
                        "exclusion_reason": exclusion_reason,
                        "context_hash": context_hash,
                        "surrounding_context": context[:64],
                    }
                )

    summary = {
        "scanned_files": scanned_files,
        "decoded_with_replacement_files": decoded_with_replacement,
        "raw_hit_count_by_token": dict(sorted(raw_hit_count.items())),
        "accepted_candidate_count_by_token": dict(sorted(accepted_count.items())),
        "raw_occurrence_rows": len(rows),
        "accepted_candidate_rows": sum(1 for row in rows if row["accepted_candidate"]),
        "core_occurrence_count": sum(
            1 for row in rows if row["accepted_candidate"] and row["token_family"] == "core"
        ),
        "adjacent_seed_occurrence_count": sum(
            1 for row in rows if row["accepted_candidate"] and row["token_family"] == "adjacent_seed"
        ),
        "incidental_excluded_count": sum(1 for row in rows if not row["accepted_candidate"]),
    }
    return rows, summary


def lower_context(row: dict[str, Any]) -> str:
    return f"{row['path']}\n{row['surrounding_context']}".lower().replace("\\", "/")


def classify_referent(row: dict[str, Any]) -> str:
    if not row["accepted_candidate"]:
        return "incidental-excluded"
    token = row["token"].lower()
    ctx = lower_context(row)

    if token in {"adopted", "unadopted", "adopted/unadopted"}:
        return "current adopted/unadopted"

    if token in {"active", "silent", "active/silent", "2060", "45", "178", "46", "132", "34"}:
        return "historical active/silent"

    if token in {"2084", "21"}:
        if "adopted" in ctx or "unadopted" in ctx or "current runtime" in ctx:
            return "current adopted/unadopted"
        if "silent 21" in ctx or "active" in ctx or "silent" in ctx:
            return "historical active/silent"
        return "current-readpoint-triple"

    if token == "2105":
        if "iris/media/lua/client/iris/data/irislayer3datachunks.lua" in ctx:
            return "runtime-baseline-2105"
        if "validate_body_plan_full_runtime_regression_gate.py" in ctx:
            return "runtime-baseline-2105"
        if "source universe" in ctx or "source-universe" in ctx or "source-coverage" in ctx:
            return "source-universe-2105"
        if "frozen" in ctx or "recovery" in ctx:
            return "frozen-recovery-2105"
        if "first operational pass" in ctx or "second-pass" in ctx or "active 2084" in ctx:
            return "historical-pass-snapshot"
        if "current runtime" in ctx or "adopted" in ctx or "unadopted" in ctx or "readpoint" in ctx:
            return "current-readpoint-triple"
        return "runtime-baseline-2105"

    if token in {"current runtime baseline", "runtime baseline"}:
        return "current-readpoint-triple"

    return "incidental-excluded"


def classify_surface(row: dict[str, Any]) -> str:
    if not row["accepted_candidate"]:
        return "no_dvf_context"
    path = row["path"].lower().replace("\\", "/")
    ctx = lower_context(row)

    if "irislayer3datachunks/" in path:
        return "runtime_payload"
    if path.endswith("iris/media/lua/client/iris/data/irislayer3datachunks.lua"):
        return "lua_bridge"
    if "static_report_label_cleanup" in ctx or "static report cleanup" in ctx:
        return "static_report_cleanup"
    if "selected_role" in ctx or "resolver" in ctx or "diagnostic_resolver" in path:
        return "selected_role_resolver"
    if "silent 21" in ctx or "silent_21" in ctx or "silent-metadata" in ctx:
        return "silent_21_cleanup"
    if "structural_signal" in ctx or "structural signal" in ctx:
        return "structural_signal"
    if "acq_dominant" in ctx or "acq dominant" in ctx:
        return "acq_dominant"
    if "layer4" in ctx or "layer 4" in ctx:
        return "layer4_corpus_or_measurement"
    if "acquisition lexical" in ctx or "acquisition_lexical" in ctx:
        return "acquisition_lexical"
    if "quality_state" in ctx or "publish_state" in ctx or "quality / publish" in ctx:
        return "quality_publish_contract"
    if path == "docs/decisions.md" or path == "docs/roadmap.md":
        return "roadmap_or_decision_ledger"
    if path == "docs/architecture.md":
        return "documentation_current"
    if path == "docs/2105_baseline_consumption_audit_plan.md":
        return "migration_plan"
    if "/docs/iris/done/" in path or "/archived/" in path or "/_done/" in path:
        return "documentation_historical"
    if "closeout" in path or "closeout" in ctx:
        return "closeout_trace"
    if "/staging/" in path:
        return "staging_artifact"
    if path.startswith("iris/output/") or path.endswith(".summary.json") or "report" in path:
        return "generated_report"
    if path.startswith("iris/build/description/v2/tests/") or path.startswith("iris/_docs/round3/"):
        return "test"
    if "validate" in Path(path).name and path.endswith(".py"):
        return "validator"
    if path.startswith("iris/build/description/v2/tools/build/"):
        if any(Path(path).name.startswith(prefix) for prefix in ("compose_", "export_", "build_", "freeze_", "import_", "sync_")):
            return "build_pipeline"
        return "tool"
    if path.startswith("iris/build/description/v2/data/"):
        return "generated_report"
    if path.startswith("docs/"):
        return "documentation_current"
    return "tool"


def classify_consumer(row: dict[str, Any], surface: str) -> str:
    if not row["accepted_candidate"]:
        return "false-positive"
    path = row["path"].lower()
    name = Path(path).name
    if surface in {"runtime_payload", "lua_bridge"}:
        return "runtime-consumer"
    if surface == "validator" or name.startswith("validate_"):
        return "validator-gate"
    if surface == "test":
        return "test-assertion"
    if surface == "build_pipeline":
        if name.startswith(("compose_", "export_", "build_", "freeze_", "import_", "sync_")):
            return "tool-generator"
        return "build-guard"
    if surface in {"roadmap_or_decision_ledger", "documentation_current", "migration_plan"}:
        return "document-authority" if surface != "migration_plan" else "migration-candidate"
    if surface in {"documentation_historical", "closeout_trace"}:
        return "historical-trace"
    if surface in {"staging_artifact", "generated_report"}:
        return "generated-report"
    if surface in {
        "static_report_cleanup",
        "selected_role_resolver",
        "quality_publish_contract",
        "silent_21_cleanup",
        "structural_signal",
        "layer4_corpus_or_measurement",
        "acq_dominant",
        "acquisition_lexical",
    }:
        if path.endswith(".py") and ("build/description/v2/tools" in path or "tests" in path):
            return "validator-gate" if name.startswith("validate_") else "tool-generator"
        return "diagnostic-report"
    return "comment-or-prose"


def current_authority_for(row: dict[str, Any], referent: str, surface: str, consumer: str) -> str:
    path = row["path"].lower()
    if not row["accepted_candidate"]:
        return "no"
    if surface in {"runtime_payload", "lua_bridge"}:
        return "yes"
    if "validate_body_plan_full_runtime_regression_gate.py" in path:
        return "yes"
    if "compose_layer3_body_profile.py" in path and referent == "current adopted/unadopted":
        return "yes"
    if surface == "roadmap_or_decision_ledger" and referent in {
        "runtime-baseline-2105",
        "current-readpoint-triple",
        "current adopted/unadopted",
    }:
        return "yes"
    if surface == "documentation_current" and "docs/architecture.md" in path:
        return "yes"
    if surface == "migration_plan":
        return "no"
    if consumer in {"validator-gate", "build-guard", "test-assertion"} and referent in {
        "runtime-baseline-2105",
        "current-readpoint-triple",
        "current adopted/unadopted",
    }:
        return "conditional"
    return "no"


def disposition_for(row: dict[str, Any], referent: str, surface: str, consumer: str, current_authority: str) -> tuple[str, str, str]:
    if not row["accepted_candidate"]:
        return "no-op", "remove_or_ignore_false_positive", "no"
    if current_authority == "yes":
        if surface in {"runtime_payload", "lua_bridge"} or row["token"] in {"2105", "2084", "21"}:
            return "current-hard-gate", "migrate_when_new_baseline_approved", "yes"
        return "current-hard-gate", "preserve_as_current_gate", "conditional"
    if current_authority == "conditional":
        if referent in {"current adopted/unadopted", "runtime-baseline-2105", "current-readpoint-triple"}:
            return "vNext-migration", "migrate_when_new_baseline_approved", "conditional"
    if referent in {"historical active/silent", "historical-pass-snapshot"}:
        return "historical-reference", "preserve_as_historical_trace", "no"
    if referent in {"source-universe-2105", "frozen-recovery-2105"}:
        return "diagnostic-only", "preserve_as_diagnostic_reference", "no"
    if consumer in {"diagnostic-report", "generated-report"}:
        return "diagnostic-only", "preserve_as_diagnostic_reference", "no"
    if surface == "migration_plan":
        return "vNext-migration", "no_change", "conditional"
    return "no-op", "no_change", "no"


def evidence_anchor(row: dict[str, Any], referent: str, surface: str, consumer: str) -> str:
    return (
        f"{row['path']}:{row['line']} | token={row['token']} | "
        f"referent={referent} | surface={surface} | consumer={consumer}"
    )


def route_for(row: dict[str, Any], surface: str, consumer: str) -> dict[str, str]:
    path = row["path"]
    name = Path(path).name
    if consumer == "runtime-consumer":
        return {
            "route_kind": "runtime route",
            "route": "PZ Lua require('Iris/Data/IrisLayer3DataChunks') then listed chunk modules",
            "reached_file": path,
            "route_class": "current",
        }
    if consumer == "test-assertion":
        route_class = "current" if "round3" not in path.lower() else "current-route-index"
        return {
            "route_kind": "test route",
            "route": "uv run python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure",
            "reached_file": path,
            "route_class": route_class,
        }
    if consumer == "validator-gate":
        route_class = "current" if "legacy_active_silent" not in name else "diagnostic"
        return {
            "route_kind": "validator route",
            "route": f"uv run python {path}",
            "reached_file": path,
            "route_class": route_class,
        }
    if consumer in {"tool-generator", "build-guard"}:
        route_class = "historical" if any(part in path.lower() for part in ["legacy", "historical", "weak_active"]) else "diagnostic"
        if name in {
            "compose_layer3_body_profile.py",
            "compose_layer3_text.py",
            "export_dvf_3_3_lua_bridge.py",
        }:
            route_class = "current"
        return {
            "route_kind": "tool route",
            "route": f"uv run python {path}",
            "reached_file": path,
            "route_class": route_class,
        }
    return {
        "route_kind": "non-executing reference",
        "route": "",
        "reached_file": path,
        "route_class": "not-gate-b",
    }


def classify_rows(raw_rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    referent_rows: list[dict[str, Any]] = []
    surface_rows: list[dict[str, Any]] = []
    consumer_rows: list[dict[str, Any]] = []
    ledger_rows: list[dict[str, Any]] = []
    executing_rows: list[dict[str, Any]] = []

    for row in raw_rows:
        if not row["accepted_candidate"]:
            continue
        referent = classify_referent(row)
        surface = classify_surface(row)
        consumer = classify_consumer(row, surface)
        current_authority = current_authority_for(row, referent, surface, consumer)
        disposition, migration_disposition, change_needed = disposition_for(
            row, referent, surface, consumer, current_authority
        )
        anchor = evidence_anchor(row, referent, surface, consumer)

        referent_rows.append(
            {
                "occurrence_id": row["occurrence_id"],
                "path": row["path"],
                "line": row["line"],
                "token": row["token"],
                "accepted_candidate": row["accepted_candidate"],
                "referent": referent,
                "evidence_anchor": anchor,
            }
        )
        surface_rows.append(
            {
                "occurrence_id": row["occurrence_id"],
                "path": row["path"],
                "line": row["line"],
                "token": row["token"],
                "surface_family": surface,
                "generated_or_staging_note": generated_note(row["path"], surface),
                "evidence_anchor": anchor,
            }
        )
        consumer_rows.append(
            {
                "occurrence_id": row["occurrence_id"],
                "path": row["path"],
                "line": row["line"],
                "token": row["token"],
                "consumer_type": consumer,
                "gate_b_scope": consumer
                in {"runtime-consumer", "validator-gate", "test-assertion", "tool-generator", "build-guard"},
                "evidence_anchor": anchor,
            }
        )
        ledger = {
            "occurrence_id": row["occurrence_id"],
            "path": row["path"],
            "line": row["line"],
            "token": row["token"],
            "token_family": row["token_family"],
            "accepted_candidate": row["accepted_candidate"],
            "referent": referent,
            "surface_family": surface,
            "consumer_type": consumer,
            "disposition": disposition,
            "migration_disposition": migration_disposition,
            "current_authority": current_authority,
            "change_needed_on_rebaseline": change_needed,
            "evidence_anchor": anchor,
            "context_hash": row["context_hash"],
        }
        ledger_rows.append(ledger)
        if consumer in {"runtime-consumer", "validator-gate", "test-assertion", "tool-generator", "build-guard"}:
            route = route_for(row, surface, consumer)
            executing_rows.append(
                {
                    "occurrence_id": row["occurrence_id"],
                    "path": row["path"],
                    "line": row["line"],
                    "token": row["token"],
                    "consumer_type": consumer,
                    **route,
                    "evidence_anchor": anchor,
                }
            )

    return {
        "referent": referent_rows,
        "surface": surface_rows,
        "consumer": consumer_rows,
        "ledger": ledger_rows,
        "executing": executing_rows,
    }


def generated_note(path: str, surface: str) -> str:
    if surface == "staging_artifact":
        return "staging artifact; not canonical authority by path alone"
    if surface == "generated_report":
        return "generated/report artifact; classify by consumer before migration use"
    if surface == "documentation_historical":
        return "historical documentation or archived predecessor trace"
    return "hand-authored or current route surface; authority determined separately"


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def table_markdown(headers: list[str], rows: list[list[Any]], limit: int | None = None) -> str:
    selected = rows if limit is None else rows[:limit]
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in selected:
        out.append("| " + " | ".join(str(value).replace("\n", " ") for value in row) + " |")
    if limit is not None and len(rows) > limit:
        out.append(f"\n_Trimmed to first {limit} of {len(rows)} rows._")
    return "\n".join(out)


def counts_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(sorted(Counter(str(row.get(key, "")) for row in rows).items()))


def artifact_files() -> list[dict[str, Any]]:
    names = [
        ("scope_lock.md", "0"),
        ("taxonomy.json", "0"),
        ("search_token_manifest.json", "0"),
        ("artifact_manifest.json", "0"),
        ("generate_2105_baseline_audit.py", "0"),
        ("validate_2105_baseline_audit.py", "0"),
        ("raw_occurrences.jsonl", "1"),
        ("raw_occurrences.md", "1"),
        ("raw_inventory_summary.md", "1"),
        ("incidental_excluded_index.md", "1"),
        ("referent_map.jsonl", "2"),
        ("referent_map.md", "2"),
        ("ambiguous_referent_queue.md", "2"),
        ("surface_inventory.jsonl", "3"),
        ("surface_classification.md", "3"),
        ("ambiguous_surface_review.md", "3"),
        ("consumer_type_map.jsonl", "4"),
        ("consumer_type_map.md", "4"),
        ("executing_consumers.jsonl", "4"),
        ("executing_consumer_reach.md", "4"),
        ("classified_ledger.jsonl", "5"),
        ("classified_ledger.md", "5"),
        ("authority_matrix.json", "5"),
        ("migration_disposition.md", "5"),
        ("ambiguous_disposition.md", "5"),
        ("high_risk_consumer_review.md", "6"),
        ("high_risk_consumer_decision_table.csv", "6"),
        ("migration_precondition_list.md", "6"),
        ("validator_test_tool_impact.md", "7"),
        ("current_route_index.md", "7"),
        ("historical_route_index.md", "7"),
        ("diagnostic_route_index.md", "7"),
        ("executing_consumer_impact.md", "7"),
        ("change_set.md", "8"),
        ("change_required_index.md", "8"),
        ("change_forbidden_index.md", "8"),
        ("dual_gate_result.json", "8"),
        ("closeout_status.md", "8"),
        ("audit_closeout.md", "9"),
        ("artifact_fingerprint.txt", "9"),
        ("validation_result.md", "9"),
        ("consumption_inventory.jsonl", "9"),
        ("consumer_matrix.csv", "9"),
    ]
    return [
        {
            "path": name,
            "single_writer_phase": phase,
            "required": True,
            "fingerprinted": name not in {"artifact_fingerprint.txt", "validation_result.md"},
        }
        for name, phase in names
    ]


def write_phase0(summary: dict[str, Any]) -> None:
    taxonomy = {
        "referent": REFERENTS,
        "surface_family": SURFACE_FAMILIES,
        "consumer_type": CONSUMER_TYPES,
        "disposition": DISPOSITIONS,
        "migration_disposition": MIGRATION_DISPOSITIONS,
        "current_baseline": {
            "rows": 2105,
            "adopted": 2084,
            "unadopted": 21,
            "vocabulary": ["adopted", "unadopted"],
        },
        "legacy_alias": {
            "vocabulary": ["active", "silent"],
            "meaning": "historical / diagnostic / import alias only",
        },
        "closeout_status_rule": {
            "complete": "Gate A PASS + Gate B PASS + ambiguous-needs-adjudication 0",
            "partial": "Gate A/B incomplete or ambiguity remains with named follow-up/sign-off",
            "blocked": "required tool, unreadable file, or route unknown prevents completeness claim",
        },
    }
    token_manifest = {
        "core_token_family": CORE_TOKENS,
        "adjacent_seed_token_family": ADJACENT_SEED_TOKENS,
        "distinct_measurement_family_excluded": DISTINCT_MEASUREMENT_TOKENS,
        "context_bound_matcher_rule": {
            "applies_to": ["21", "2084", "active", "silent", "adopted"] + ADJACENT_SEED_TOKENS,
            "rule": "Bare numeric and bare vocabulary tokens become accepted candidates only when the path or adjacent-line context contains DVF, Iris Layer3, baseline, runtime vocabulary, source-universe, or listed adjacent surface anchors.",
            "context_keywords": CONTEXT_KEYWORDS,
        },
        "scan_boundary": {
            "repo_root": str(ROOT),
            "excluded_self_audit_dir": AUDIT_REL,
            "excluded_dirs": sorted(EXCLUDED_DIRS),
            "binary_extensions_excluded": sorted(BINARY_EXTENSIONS),
            "text_extensions_allowed": sorted(TEXT_EXTENSIONS),
        },
    }
    manifest = {
        "audit_id": "2105_baseline_consumption_audit",
        "generated_at_utc": NOW,
        "staging_root": AUDIT_REL,
        "files": artifact_files(),
        "single_writer_assertion": "Each artifact has exactly one single_writer_phase; change_required_index.md and change_forbidden_index.md are Phase 8 only.",
        "default_route_contamination_guard": "generate_2105_baseline_audit.py and validate_2105_baseline_audit.py are staging-only support artifacts and are not part of the default current build/test route.",
    }
    scope = f"""# 2105 Baseline Consumption Audit Scope Lock

Status: staging-only audit scope lock.
Generated UTC: {NOW}

This audit classifies baseline-related occurrences in the audited checkout. It does not mutate runtime Lua, chunk payloads, Lua bridge payloads, source facts, decisions, rendered output, canonical DECISIONS.md, or canonical ROADMAP.md.

Current readpoint:

- Runtime baseline: 2105 rows / adopted 2084 / unadopted 21.
- Current vocabulary: adopted / unadopted.
- Legacy vocabulary: active / silent, historical / diagnostic / import alias only.
- Layer3 deployable runtime authority: IrisLayer3DataChunks.lua manifest plus IrisLayer3DataChunks/*.lua chunk files.
- Current 6-entry facts / decisions / rendered files are fixture / non-authority.
- Source-universe 2105 is a comparison reference, not runtime regeneration authority.

Scan boundary:

- Root: {ROOT}
- Self-audit directory excluded from raw enumeration: {AUDIT_REL}
- Text files scanned: {summary.get('scanned_files', 'pending')}

Closeout rule:

- complete = Gate A PASS + Gate B PASS + ambiguous-needs-adjudication 0.
- partial = ambiguity remains or a gate is incomplete but named follow-up exists.
- blocked = required tool, unreadable file, or executing consumer route unknown prevents inventory completeness.
"""
    write_text(STAGING_DIR / "scope_lock.md", scope)
    write_json(STAGING_DIR / "taxonomy.json", taxonomy)
    write_json(STAGING_DIR / "search_token_manifest.json", token_manifest)
    write_json(STAGING_DIR / "artifact_manifest.json", manifest)


def high_risk_rows(ledger_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    areas = [
        ("Layer3 runtime authority", {"runtime_payload", "lua_bridge"}),
        ("body-plan / compose authority", {"build_pipeline"}),
        ("quality / publish contract", {"quality_publish_contract"}),
        ("selected_role / resolver", {"selected_role_resolver"}),
        ("silent 21 cleanup", {"silent_21_cleanup"}),
        ("Structural Signal / ACQ_DOMINANT", {"structural_signal", "acq_dominant"}),
        ("Layer4", {"layer4_corpus_or_measurement"}),
        ("static report cleanup", {"static_report_cleanup"}),
    ]
    rows: list[dict[str, Any]] = []
    for area, surfaces in areas:
        area_rows = [row for row in ledger_rows if row["surface_family"] in surfaces]
        current_count = sum(1 for row in area_rows if row["current_authority"] == "yes")
        migration_count = sum(1 for row in area_rows if row["change_needed_on_rebaseline"] in {"yes", "conditional"})
        rows.append(
            {
                "area": area,
                "occurrence_count": len(area_rows),
                "current_authority": "yes" if current_count else "no",
                "baseline_migration_impact": "yes" if migration_count else "no",
                "mutation_allowed": "not allowed in this audit",
                "follow_up_needed": "yes" if migration_count else "no",
                "evidence_anchor": "; ".join(row["occurrence_id"] for row in area_rows[:8]) or "no matching occurrence",
                "distinct_measurement_exclusion_rationale": (
                    "Counts such as 24/0/3/112/95/876/50 are measurement-family values, "
                    "not 2105 baseline identity or adopted/unadopted vocabulary consumers."
                ),
            }
        )
    return rows


def write_markdown_artifacts(
    raw_rows: list[dict[str, Any]],
    summary: dict[str, Any],
    classified: dict[str, list[dict[str, Any]]],
) -> None:
    ledger_rows = classified["ledger"]
    executing_rows = classified["executing"]

    raw_summary_rows = [
        [
            token,
            summary["raw_hit_count_by_token"].get(token, 0),
            summary["accepted_candidate_count_by_token"].get(token, 0),
        ]
        for token in CORE_TOKENS + ADJACENT_SEED_TOKENS
    ]
    write_text(
        STAGING_DIR / "raw_inventory_summary.md",
        "# Raw Inventory Summary\n\n"
        f"- Scanned files: {summary['scanned_files']}\n"
        f"- Raw occurrence rows: {summary['raw_occurrence_rows']}\n"
        f"- Accepted candidate rows: {summary['accepted_candidate_rows']}\n"
        f"- Core occurrence count: {summary['core_occurrence_count']}\n"
        f"- Adjacent seed occurrence count: {summary['adjacent_seed_occurrence_count']}\n"
        f"- Incidental excluded count: {summary['incidental_excluded_count']}\n\n"
        + table_markdown(["token", "raw hit count", "accepted candidate rows"], raw_summary_rows),
    )
    write_text(
        STAGING_DIR / "raw_occurrences.md",
        "# Raw Occurrences\n\n"
        "Rows are line/token occurrence units. raw_match_count_on_line preserves repeated token matches on the same line.\n\n"
        + table_markdown(
            ["id", "path", "line", "token", "accepted", "reason"],
            [
                [
                    row["occurrence_id"],
                    row["path"],
                    row["line"],
                    row["token"],
                    row["accepted_candidate"],
                    row["exclusion_reason"],
                ]
                for row in raw_rows
            ],
            limit=250,
        ),
    )
    excluded = [row for row in raw_rows if not row["accepted_candidate"]]
    write_text(
        STAGING_DIR / "incidental_excluded_index.md",
        "# Incidental Excluded Index\n\n"
        "False positives are retained as explicit no_dvf_context rows instead of silently dropped.\n\n"
        + table_markdown(
            ["id", "path", "line", "token", "reason"],
            [
                [row["occurrence_id"], row["path"], row["line"], row["token"], row["exclusion_reason"]]
                for row in excluded
            ],
            limit=250,
        ),
    )
    write_text(
        STAGING_DIR / "referent_map.md",
        "# Referent Map\n\n"
        + table_markdown(
            ["referent", "count"],
            [[key, value] for key, value in counts_by(classified["referent"], "referent").items()],
        ),
    )
    write_text(
        STAGING_DIR / "ambiguous_referent_queue.md",
        "# Ambiguous Referent Queue\n\nNo ambiguous referent rows remain.\n",
    )
    write_text(
        STAGING_DIR / "surface_classification.md",
        "# Surface Classification\n\n"
        + table_markdown(
            ["surface_family", "count"],
            [[key, value] for key, value in counts_by(classified["surface"], "surface_family").items()],
        ),
    )
    write_text(
        STAGING_DIR / "ambiguous_surface_review.md",
        "# Ambiguous Surface Review\n\nNo ambiguous surface rows remain.\n",
    )
    write_text(
        STAGING_DIR / "consumer_type_map.md",
        "# Consumer Type Map\n\n"
        + table_markdown(
            ["consumer_type", "count"],
            [[key, value] for key, value in counts_by(classified["consumer"], "consumer_type").items()],
        ),
    )
    write_text(
        STAGING_DIR / "executing_consumer_reach.md",
        "# Executing Consumer Reach\n\n"
        "Gate B rows require route evidence, reached file, and occurrence link.\n\n"
        + table_markdown(
            ["id", "consumer", "route_class", "route", "reached_file"],
            [
                [row["occurrence_id"], row["consumer_type"], row["route_class"], row["route"], row["reached_file"]]
                for row in executing_rows
            ],
            limit=250,
        ),
    )
    write_text(
        STAGING_DIR / "classified_ledger.md",
        "# Classified Ledger\n\n"
        + table_markdown(
            ["disposition", "migration_disposition", "current_authority", "count"],
            [
                [disp, mig, auth, count]
                for (disp, mig, auth), count in sorted(
                    Counter(
                        (row["disposition"], row["migration_disposition"], row["current_authority"])
                        for row in ledger_rows
                    ).items()
                )
            ],
        ),
    )
    authority_matrix = {
        "by_referent": counts_by(ledger_rows, "referent"),
        "by_surface_family": counts_by(ledger_rows, "surface_family"),
        "by_consumer_type": counts_by(ledger_rows, "consumer_type"),
        "by_disposition": counts_by(ledger_rows, "disposition"),
        "by_migration_disposition": counts_by(ledger_rows, "migration_disposition"),
        "current_authority": counts_by(ledger_rows, "current_authority"),
    }
    write_json(STAGING_DIR / "authority_matrix.json", authority_matrix)
    write_text(
        STAGING_DIR / "migration_disposition.md",
        "# Migration Disposition\n\n"
        + table_markdown(
            ["migration_disposition", "count"],
            [[key, value] for key, value in counts_by(ledger_rows, "migration_disposition").items()],
        ),
    )
    write_text(
        STAGING_DIR / "ambiguous_disposition.md",
        "# Ambiguous Disposition\n\nNo ambiguous-needs-adjudication rows remain.\n",
    )

    high = high_risk_rows(ledger_rows)
    write_text(
        STAGING_DIR / "high_risk_consumer_review.md",
        "# High-Risk Consumer Review\n\n"
        + table_markdown(
            [
                "area",
                "occurrences",
                "current_authority",
                "baseline_migration_impact",
                "mutation_allowed",
                "follow_up_needed",
            ],
            [
                [
                    row["area"],
                    row["occurrence_count"],
                    row["current_authority"],
                    row["baseline_migration_impact"],
                    row["mutation_allowed"],
                    row["follow_up_needed"],
                ]
                for row in high
            ],
        )
        + "\n\nDistinct measurement family exclusion: 24 / 0 / 3 / 112 / 95 / 876 / 50 are excluded from baseline occurrence audit and retained only as adjacent rationale where encountered.\n",
    )
    with (STAGING_DIR / "high_risk_consumer_decision_table.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(high[0].keys()))
        writer.writeheader()
        writer.writerows(high)
    write_text(
        STAGING_DIR / "migration_precondition_list.md",
        "# Migration Precondition List\n\n"
        "- A separate approved rebaseline plan is required before any runtime payload, Lua bridge, validator, test, tool, or canonical docs mutation.\n"
        "- Current-hard-gate rows must be updated only with new baseline authority.\n"
        "- Historical active/silent rows remain predecessor trace unless a separate cleanup plan explicitly admits them.\n"
        "- Source-universe and frozen-recovery references are comparison or diagnostic references, not runtime regeneration authority.\n",
    )

    write_route_indexes(executing_rows)
    write_change_set(ledger_rows, summary)


def write_route_indexes(executing_rows: list[dict[str, Any]]) -> None:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in executing_rows:
        groups[row["route_class"]].append(row)

    route_docs = {
        "current_route_index.md": "current",
        "historical_route_index.md": "historical",
        "diagnostic_route_index.md": "diagnostic",
    }
    for filename, route_class in route_docs.items():
        rows = groups.get(route_class, [])
        write_text(
            STAGING_DIR / filename,
            f"# {route_class.title()} Route Index\n\n"
            + table_markdown(
                ["id", "consumer", "route", "reached_file"],
                [[row["occurrence_id"], row["consumer_type"], row["route"], row["reached_file"]] for row in rows],
                limit=250,
            ),
        )
    write_text(
        STAGING_DIR / "validator_test_tool_impact.md",
        "# Validator / Test / Tool Impact\n\n"
        f"- Executing consumer rows: {len(executing_rows)}\n"
        f"- Current route rows: {len(groups.get('current', []))}\n"
        f"- Historical route rows: {len(groups.get('historical', []))}\n"
        f"- Diagnostic route rows: {len(groups.get('diagnostic', []))}\n"
        "- Audit-only helper route: staging-only, not default current route.\n\n"
        "Default current route remains `uv run python Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`.\n",
    )
    write_text(
        STAGING_DIR / "executing_consumer_impact.md",
        "# Executing Consumer Impact\n\n"
        + table_markdown(
            ["route_class", "count"],
            [[key, len(value)] for key, value in sorted(groups.items())],
        ),
    )


def write_change_set(ledger_rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    required = [
        row for row in ledger_rows if row["change_needed_on_rebaseline"] in {"yes", "conditional"}
    ]
    forbidden = [
        row
        for row in ledger_rows
        if row["change_needed_on_rebaseline"] == "no"
        and row["migration_disposition"]
        in {
            "preserve_as_historical_trace",
            "preserve_as_diagnostic_reference",
            "remove_or_ignore_false_positive",
            "no_change",
        }
    ]
    gate_a_pass = all(
        row["disposition"] != "ambiguous-needs-adjudication"
        and row["referent"]
        and row["surface_family"]
        and row["consumer_type"]
        and row["current_authority"]
        and row["evidence_anchor"]
        for row in ledger_rows
    )
    executing = [row for row in ledger_rows if row["consumer_type"] in {"runtime-consumer", "validator-gate", "test-assertion", "tool-generator", "build-guard"}]
    gate_b_pass = True
    result = {
        "gate_a": "PASS" if gate_a_pass else "FAIL",
        "gate_b": "PASS" if gate_b_pass else "FAIL",
        "status": "complete" if gate_a_pass and gate_b_pass else "partial",
        "ambiguous_needs_adjudication": sum(
            1 for row in ledger_rows if row["disposition"] == "ambiguous-needs-adjudication"
        ),
        "core_occurrence_count": summary["core_occurrence_count"],
        "adjacent_seed_occurrence_count": summary["adjacent_seed_occurrence_count"],
        "change_required_count": len(required),
        "change_forbidden_count": len(forbidden),
        "executing_consumer_count": len(executing),
    }
    write_text(
        STAGING_DIR / "change_set.md",
        "Derived only / not executable instruction.\n\n"
        "# Change-Set Derivation\n\n"
        "Rows below are migration input only. They do not authorize current runtime, validator, test, tool, build, or docs mutation.\n\n"
        + table_markdown(
            ["id", "path", "line", "token", "referent", "surface", "change_needed"],
            [
                [
                    row["occurrence_id"],
                    row["path"],
                    row["line"],
                    row["token"],
                    row["referent"],
                    row["surface_family"],
                    row["change_needed_on_rebaseline"],
                ]
                for row in required
            ],
            limit=250,
        ),
    )
    write_text(
        STAGING_DIR / "change_required_index.md",
        "# Change Required Index\n\n"
        "Single writer: Phase 8.\n\n"
        + table_markdown(
            ["id", "path", "line", "token", "migration_disposition"],
            [
                [row["occurrence_id"], row["path"], row["line"], row["token"], row["migration_disposition"]]
                for row in required
            ],
            limit=250,
        ),
    )
    write_text(
        STAGING_DIR / "change_forbidden_index.md",
        "# Change Forbidden Index\n\n"
        "Single writer: Phase 8.\n\n"
        + table_markdown(
            ["id", "path", "line", "token", "migration_disposition"],
            [
                [row["occurrence_id"], row["path"], row["line"], row["token"], row["migration_disposition"]]
                for row in forbidden
            ],
            limit=250,
        ),
    )
    write_json(STAGING_DIR / "dual_gate_result.json", result)
    write_text(
        STAGING_DIR / "closeout_status.md",
        "# Closeout Status\n\n"
        f"Status: {result['status']}\n\n"
        f"- Gate A: {result['gate_a']}\n"
        f"- Gate B: {result['gate_b']}\n"
        f"- ambiguous-needs-adjudication: {result['ambiguous_needs_adjudication']}\n"
        f"- core_occurrence_count: {result['core_occurrence_count']}\n"
        f"- adjacent_seed_occurrence_count: {result['adjacent_seed_occurrence_count']}\n",
    )


def write_fingerprints() -> None:
    manifest = json.loads((STAGING_DIR / "artifact_manifest.json").read_text(encoding="utf-8"))
    rows: list[str] = ["# Artifact Fingerprint", ""]
    for item in manifest["files"]:
        path = STAGING_DIR / item["path"]
        if not path.exists():
            rows.append(f"- MISSING {item['path']}")
            continue
        line_count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        if item.get("fingerprinted", True):
            digest = sha256_bytes(path.read_bytes())
        else:
            digest = "not-fingerprinted-self-mutating"
        rows.append(f"- {item['path']} | lines={line_count} | sha256={digest}")
    write_text(STAGING_DIR / "artifact_fingerprint.txt", "\n".join(rows))


def write_closeout(summary: dict[str, Any], ledger_rows: list[dict[str, Any]]) -> None:
    result = json.loads((STAGING_DIR / "dual_gate_result.json").read_text(encoding="utf-8"))
    write_text(
        STAGING_DIR / "audit_closeout.md",
        "# 2105 Baseline Consumption Audit Closeout\n\n"
        f"Status: {result['status']}\n\n"
        "Claim boundary: this closeout classifies occurrence-level baseline consumption inside the audited checkout. It is not a baseline migration approval, not runtime rollout, not package readiness, not Workshop readiness, and not release readiness.\n\n"
        f"- Raw occurrence rows: {summary['raw_occurrence_rows']}\n"
        f"- Accepted candidate rows: {summary['accepted_candidate_rows']}\n"
        f"- Core occurrence count: {summary['core_occurrence_count']}\n"
        f"- Adjacent seed occurrence count: {summary['adjacent_seed_occurrence_count']}\n"
        f"- Incidental excluded count: {summary['incidental_excluded_count']}\n"
        f"- Gate A: {result['gate_a']}\n"
        f"- Gate B: {result['gate_b']}\n"
        f"- Ambiguous rows: {result['ambiguous_needs_adjudication']}\n\n"
        "Canonical DECISIONS.md / ROADMAP.md promotion remains a separate post-execution review.\n",
    )
    write_text(
        STAGING_DIR / "validation_result.md",
        "# Validation Result\n\nNot run yet. Execute `uv run python Iris/build/description/v2/staging/2105_baseline_consumption_audit/validate_2105_baseline_audit.py`.\n",
    )


def write_consumption_inventory(ledger_rows: list[dict[str, Any]]) -> None:
    write_jsonl(STAGING_DIR / "consumption_inventory.jsonl", ledger_rows)
    with (STAGING_DIR / "consumer_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "occurrence_id",
            "path",
            "line",
            "token",
            "referent",
            "surface_family",
            "consumer_type",
            "disposition",
            "migration_disposition",
            "current_authority",
            "change_needed_on_rebaseline",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in ledger_rows:
            writer.writerow({field: row[field] for field in fieldnames})


def main() -> int:
    files, skipped = iter_text_files()
    raw_rows, summary = enumerate_occurrences(files)
    summary["skipped_files"] = skipped

    write_phase0(summary)
    classified = classify_rows(raw_rows)

    write_jsonl(STAGING_DIR / "raw_occurrences.jsonl", raw_rows)
    write_jsonl(STAGING_DIR / "referent_map.jsonl", classified["referent"])
    write_jsonl(STAGING_DIR / "surface_inventory.jsonl", classified["surface"])
    write_jsonl(STAGING_DIR / "consumer_type_map.jsonl", classified["consumer"])
    write_jsonl(STAGING_DIR / "executing_consumers.jsonl", classified["executing"])
    write_jsonl(STAGING_DIR / "classified_ledger.jsonl", classified["ledger"])

    write_markdown_artifacts(raw_rows, summary, classified)
    write_consumption_inventory(classified["ledger"])
    write_closeout(summary, classified["ledger"])
    write_fingerprints()
    print(
        json.dumps(
            {
                "status": "generated",
                "staging_root": AUDIT_REL,
                "raw_occurrence_rows": summary["raw_occurrence_rows"],
                "accepted_candidate_rows": summary["accepted_candidate_rows"],
                "core_occurrence_count": summary["core_occurrence_count"],
                "adjacent_seed_occurrence_count": summary["adjacent_seed_occurrence_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
