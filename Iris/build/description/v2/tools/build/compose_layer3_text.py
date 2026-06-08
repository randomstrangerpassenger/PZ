from __future__ import annotations

import argparse
from collections import Counter
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .compose_layer3_io import (
    entries_sha256,
    file_sha256,
    load_json,
    load_jsonl,
    load_optional_jsonl_map,
    write_jsonl,
)
from .compose_layer3_body_profile import (
    DEFAULT_RESOLVER_AUTHORITY_MODE,
    DIAGNOSTIC_RESOLVER_AUTHORITY_MODE,
    UNADOPTED_RUNTIME_STATE,
    is_body_plan_profiles_v2,
    load_profile_resolution_rules,
)
from .compose_layer3_render import compose_all_legacy, compose_all_v2
from tools.common.paths import V2_ROOT as ROOT


DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"
STAGING_DIR = ROOT / "staging" / "body_role" / "phase2"
EDPAS_DIAGNOSTIC_DIR = ROOT / "staging" / "entrypoint_drift_patch_authority_seal_round" / "diagnostic"
STYLE_LOG_PATH = OUTPUT_DIR / "style_normalization_changes.jsonl"
OVERLAY_PATH = STAGING_DIR / "layer3_role_check_overlay.jsonl"
BODY_SOURCE_OVERLAY_PATH = ROOT / "staging" / "compose_contract_migration" / "layer3_body_source_overlay.jsonl"
IDENTITY_RULES_PATH = DATA_DIR / "compose_profile_identity_hint_rules.json"
PRECEDENCE_RULES_PATH = DATA_DIR / "compose_profile_conflict_precedence_rules.json"
BODY_PLAN_PROFILES_PATH = DATA_DIR / "compose_profiles_v2.json"

DEFAULT_MODE = "default"
DIAGNOSTIC_RESOLVER_MODE = "diagnostic_resolver"
DEFAULT_CURRENT_AUTHORITY_INPUT_PATH_ERROR_CODE = "DEFAULT_CURRENT_AUTHORITY_INPUT_REJECTED_NON_DATA_SOURCE"
CURRENT_AUTHORITY_INPUT_KEYS = (
    "facts_path",
    "decisions_path",
    "profiles_path",
    "identity_rules_path",
    "precedence_rules_path",
)
ENTRYPOINT_MODES = (
    DEFAULT_MODE,
    DIAGNOSTIC_RESOLVER_MODE,
)


def is_under_path(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def enforce_resolver_authority_output_contract(
    *,
    resolver_authority_mode: str,
    output_path: Path,
    style_log_path: Path,
    requeue_candidates_path: Path | None,
) -> None:
    if resolver_authority_mode != DIAGNOSTIC_RESOLVER_AUTHORITY_MODE:
        return
    for key, value in (
        ("output_path", output_path),
        ("style_log_path", style_log_path),
        ("requeue_candidates_path", requeue_candidates_path),
    ):
        if value is not None and is_under_path(value, OUTPUT_DIR):
            raise ValueError(f"diagnostic resolver {key} must not write under canonical {OUTPUT_DIR}")


def enforce_current_authority_input_contract(mode: str, paths: dict[str, Path | None]) -> None:
    if mode != DEFAULT_MODE:
        return
    for key in CURRENT_AUTHORITY_INPUT_KEYS:
        value = paths.get(key)
        if value is None:
            raise ValueError(f"{DEFAULT_CURRENT_AUTHORITY_INPUT_PATH_ERROR_CODE}: default mode {key} is required")
        if not is_under_path(value, DATA_DIR):
            raise ValueError(
                f"{DEFAULT_CURRENT_AUTHORITY_INPUT_PATH_ERROR_CODE}: "
                f"default mode {key} must read current authority input from {DATA_DIR}, got {value}"
            )


def build_rendered(
    facts_path: Path,
    decisions_path: Path,
    profiles_path: Path,
    output_path: Path,
    overlay_path: Path | None = OVERLAY_PATH,
    style_log_path: Path = STYLE_LOG_PATH,
    requeue_candidates_path: Path | None = None,
    identity_rules_path: Path = IDENTITY_RULES_PATH,
    precedence_rules_path: Path = PRECEDENCE_RULES_PATH,
    resolver_authority_mode: str = DEFAULT_RESOLVER_AUTHORITY_MODE,
) -> dict[str, Any]:
    enforce_resolver_authority_output_contract(
        resolver_authority_mode=resolver_authority_mode,
        output_path=output_path,
        style_log_path=style_log_path,
        requeue_candidates_path=requeue_candidates_path,
    )
    facts_list = load_jsonl(facts_path)
    decisions_list = load_jsonl(decisions_path)
    profiles = load_json(profiles_path)
    overlay_map = load_optional_jsonl_map(overlay_path)
    is_v2 = is_body_plan_profiles_v2(profiles)

    if is_v2:
        identity_hint_target_map, precedence_rules = load_profile_resolution_rules(
            identity_rules_path=identity_rules_path,
            precedence_rules_path=precedence_rules_path,
        )
        entries, normalization_logs, requeue_candidates = compose_all_v2(
            facts_list,
            decisions_list,
            overlay_map,
            profiles,
            identity_hint_target_map=identity_hint_target_map,
            precedence_rules=precedence_rules,
            resolver_authority_mode=resolver_authority_mode,
        )
    else:
        entries, normalization_logs, requeue_candidates = compose_all_legacy(
            facts_list,
            decisions_list,
            overlay_map,
            profiles,
            allow_legacy_runtime_state=True,
        )

    stats = {
        "total": len(entries),
        "adopted_override": sum(1 for entry in entries.values() if entry["source"] == "override"),
        "unadopted": sum(1 for entry in entries.values() if entry["source"] == UNADOPTED_RUNTIME_STATE),
    }
    if is_v2:
        resolved_profile_counts = Counter(
            entry.get("resolved_profile")
            for entry in entries.values()
            if entry.get("resolved_profile") is not None
        )
        resolution_source_counts = Counter(
            entry.get("resolution_source")
            for entry in entries.values()
            if entry.get("resolution_source") is not None
        )
        coverage_quality_candidate_counts = Counter(
            entry.get("coverage_quality_candidate")
            for entry in entries.values()
            if entry.get("coverage_quality_candidate") is not None
        )
        missing_required_section_counts = Counter()
        for entry in entries.values():
            for section_name in entry.get("body_plan", {}).get("missing_required_sections", []):
                missing_required_section_counts[str(section_name)] += 1
        stats.update(
            {
                "adopted_composed_v2_preview": sum(
                    1 for entry in entries.values() if entry["source"] == "composed_v2_preview"
                ),
                "resolved_profile_counts": dict(resolved_profile_counts),
                "resolution_source_counts": dict(resolution_source_counts),
                "coverage_quality_candidate_counts": dict(coverage_quality_candidate_counts),
                "missing_required_section_counts": dict(missing_required_section_counts),
            }
        )
    else:
        stats.update(
            {
                "adopted_composed": sum(
                    1 for entry in entries.values() if entry["source"] == "composed"
                ),
                "quality_flagged": sum(
                    1 for entry in entries.values() if entry.get("quality_flag") is not None
                ),
                "requeue_candidates": len(requeue_candidates),
            }
        )

    rendered = {
        "meta": {
            "version": "dvf-3-3-body-plan-v2-preview-v0" if is_v2 else "interaction-cluster-rendered-v0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "facts_sha256": file_sha256(facts_path),
            "decisions_sha256": file_sha256(decisions_path),
            "profiles_sha256": file_sha256(profiles_path),
            "overlay_path": str(overlay_path) if overlay_path is not None else None,
            "overlay_sha256": file_sha256(overlay_path) if overlay_path is not None and overlay_path.exists() else None,
            "entries_sha256": entries_sha256(entries),
            "stats": stats,
        },
        "entries": entries,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(rendered, handle, ensure_ascii=False, indent=2)

    style_log_path.parent.mkdir(parents=True, exist_ok=True)
    with style_log_path.open("w", encoding="utf-8") as handle:
        for log_entry in normalization_logs:
            handle.write(json.dumps(log_entry, ensure_ascii=False))
            handle.write("\n")

    if requeue_candidates_path is not None:
        write_jsonl(requeue_candidates_path, requeue_candidates)
    return rendered


def default_entrypoint_paths(mode: str) -> dict[str, Path | None]:
    if mode == DEFAULT_MODE:
        return {
            "profiles_path": BODY_PLAN_PROFILES_PATH,
            "overlay_path": BODY_SOURCE_OVERLAY_PATH,
            "output_path": OUTPUT_DIR / "dvf_3_3_rendered.json",
            "style_log_path": STYLE_LOG_PATH,
            "requeue_candidates_path": None,
        }
    if mode == DIAGNOSTIC_RESOLVER_MODE:
        return {
            "profiles_path": BODY_PLAN_PROFILES_PATH,
            "overlay_path": BODY_SOURCE_OVERLAY_PATH,
            "output_path": EDPAS_DIAGNOSTIC_DIR / "diagnostic_resolver_dvf_3_3_rendered.json",
            "style_log_path": EDPAS_DIAGNOSTIC_DIR / "diagnostic_resolver_style_log.jsonl",
            "requeue_candidates_path": EDPAS_DIAGNOSTIC_DIR / "diagnostic_resolver_requeue_candidates.jsonl",
        }
    raise ValueError(f"Unknown entrypoint mode: {mode}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose Iris DVF 3-3 layer3 text.")
    parser.add_argument("--mode", choices=ENTRYPOINT_MODES, default=DEFAULT_MODE)
    parser.add_argument("--facts-path", type=Path, default=DATA_DIR / "dvf_3_3_facts.jsonl")
    parser.add_argument("--decisions-path", type=Path, default=DATA_DIR / "dvf_3_3_decisions.jsonl")
    parser.add_argument("--profiles-path", type=Path, default=None)
    parser.add_argument("--output-path", type=Path, default=None)
    parser.add_argument("--overlay-path", type=Path, default=None)
    parser.add_argument("--style-log-path", type=Path, default=None)
    parser.add_argument("--requeue-candidates-path", type=Path, default=None)
    parser.add_argument("--identity-rules-path", type=Path, default=IDENTITY_RULES_PATH)
    parser.add_argument("--precedence-rules-path", type=Path, default=PRECEDENCE_RULES_PATH)
    return parser.parse_args(argv)


def resolve_entrypoint_paths(args: argparse.Namespace) -> dict[str, Path | None]:
    defaults = default_entrypoint_paths(args.mode)
    return {
        "facts_path": args.facts_path,
        "decisions_path": args.decisions_path,
        "profiles_path": args.profiles_path or defaults["profiles_path"],
        "output_path": args.output_path or defaults["output_path"],
        "overlay_path": args.overlay_path or defaults["overlay_path"],
        "style_log_path": args.style_log_path or defaults["style_log_path"],
        "requeue_candidates_path": args.requeue_candidates_path or defaults["requeue_candidates_path"],
        "identity_rules_path": args.identity_rules_path,
        "precedence_rules_path": args.precedence_rules_path,
    }


def enforce_entrypoint_mode_contract(mode: str, paths: dict[str, Path | None]) -> None:
    profiles_path = paths["profiles_path"]
    if profiles_path is None:
        raise ValueError("profiles_path is required")
    profiles = load_json(profiles_path)
    is_v2 = is_body_plan_profiles_v2(profiles)

    if mode in {DEFAULT_MODE, DIAGNOSTIC_RESOLVER_MODE} and not is_v2:
        raise ValueError(f"{mode} mode requires compose_profiles_v2.json / schema compose-profiles-v2")

    enforce_current_authority_input_contract(mode, paths)

    if mode == DIAGNOSTIC_RESOLVER_MODE:
        for key in ("output_path", "style_log_path", "requeue_candidates_path"):
            value = paths.get(key)
            if value is not None and not is_under_path(value, EDPAS_DIAGNOSTIC_DIR):
                raise ValueError(f"{mode} {key} must stay under {EDPAS_DIAGNOSTIC_DIR}")


def resolver_authority_mode_for_entrypoint(mode: str) -> str:
    if mode == DIAGNOSTIC_RESOLVER_MODE:
        return DIAGNOSTIC_RESOLVER_AUTHORITY_MODE
    return DEFAULT_RESOLVER_AUTHORITY_MODE


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = resolve_entrypoint_paths(args)
    enforce_entrypoint_mode_contract(args.mode, paths)
    build_rendered(
        paths["facts_path"],
        paths["decisions_path"],
        paths["profiles_path"],
        paths["output_path"],
        paths["overlay_path"],
        paths["style_log_path"],
        paths["requeue_candidates_path"],
        paths["identity_rules_path"],
        paths["precedence_rules_path"],
        resolver_authority_mode_for_entrypoint(args.mode),
    )
    print("rendered written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
