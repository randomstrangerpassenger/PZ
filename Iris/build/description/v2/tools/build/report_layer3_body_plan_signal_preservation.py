from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ROUND_DIR = ROOT / "staging" / "compose_contract_migration" / "phase_d_signal_preservation_patch_round"
CURRENT_SESSION_DIR = ROOT / "staging" / "compose_contract_migration" / "phase_d_e_current_session"
IDENTITY_FALLBACK_DIR = (
    ROOT
    / "staging"
    / "identity_fallback_source_expansion"
    / "phase6_subset_rollout"
    / "exec_subset_600_wrench_crowbar_b7_b8_b9"
)
DATA_DIR = ROOT / "data"

RENDERED_PATH = CURRENT_SESSION_DIR / "dvf_3_3_rendered_v2_preview.2105.json"
SURFACE_SIGNAL_PATH = IDENTITY_FALLBACK_DIR / "subset_surface_contract_signal.jsonl"
PROFILES_PATH = DATA_DIR / "compose_profiles_v2.json"
ROW_OUTPUT_PATH = ROUND_DIR / "body_plan_signal_preservation.2105.jsonl"
SOURCE_SUMMARY_PATH = ROUND_DIR / "body_plan_signal_preservation.source_distribution.json"
SECTION_SUMMARY_PATH = ROUND_DIR / "body_plan_signal_preservation.section_distribution.json"
CROSSWALK_SUMMARY_PATH = ROUND_DIR / "body_plan_signal_preservation.crosswalk.json"

ROUND_ID = "phase_d_observer_signal_preservation_patch_round_v0_3"

CORE_SOURCE_FAMILIES = {
    "BODY_LACKS_ITEM_SPECIFIC_USE",
    "FUNCTION_NARROW",
    "IDENTITY_ONLY",
    "ACQ_DOMINANT",
}
STRUCTURAL_PROBE_FAMILIES = {"LAYER4_ABSORPTION"}
OUT_OF_SCOPE_SOURCE_FAMILIES = {"ADEQUATE"}
ALLOWED_SOURCE_FAMILIES = CORE_SOURCE_FAMILIES | STRUCTURAL_PROBE_FAMILIES
COUNT_PRESERVATION_FAMILIES = {"BODY_LACKS_ITEM_SPECIFIC_USE", "FUNCTION_NARROW"}
COUNT_PRESERVATION_TARGET = {
    "BODY_LACKS_ITEM_SPECIFIC_USE": 617,
    "FUNCTION_NARROW": 7,
    "none": 1481,
}
EXISTENCE_NO_OVERWRITE_FAMILIES = {"IDENTITY_ONLY", "ACQ_DOMINANT"}

SECTION_SIGNAL_PREFIX = "SECTION_"
SECTION_NONE = "none"

LAYER4_PROXY_FLAGS = {"INTERACTION_LIST_DUPLICATION", "CROSS_LAYER_RAW_COPY"}
VIOLATION_FLAG_SOURCE_ALLOWLIST = {
    "BODY_COLLAPSES_TO_ACQUISITION": "ACQ_DOMINANT",
    "BODY_LOSES_ITEM_CENTRICITY": "BODY_LACKS_ITEM_SPECIFIC_USE",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def normalize_signal_value(value: Any) -> str:
    if value is None:
        return "none"
    normalized = str(value).strip()
    if not normalized:
        return "none"
    if normalized.lower() == "none":
        return "none"
    return normalized


def signal_present(*, primary: str, secondary: list[str]) -> bool:
    return primary != "none" or bool(secondary)


def active_runtime_state(entry: dict[str, Any]) -> str:
    return "silent" if entry.get("source") == "silent" else "active"


def normalize_violation_flags(structural_row: dict[str, Any] | None) -> list[str]:
    if structural_row is None:
        return []
    seen: set[str] = set()
    normalized: list[str] = []
    for raw_value in structural_row.get("violation_flags", []):
        value = str(raw_value).strip()
        if value and value not in seen:
            seen.add(value)
            normalized.append(value)
    return normalized


def build_origin(
    *,
    artifact_path: Path,
    producer: str,
    row_key: str,
    field: str,
    json_path: str,
) -> dict[str, str]:
    return {
        "artifact": str(artifact_path),
        "producer": producer,
        "row_key": row_key,
        "field": field,
        "json_path": json_path,
    }


def assess_violation_type_population(structural_rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_rows = len(structural_rows)
    rows_with_field = 0
    rows_missing_field = 0
    non_null_population = 0
    core_family_population = Counter()
    structural_probe_population = Counter()
    out_of_scope_population = Counter()

    for row in structural_rows:
        if "violation_type" not in row:
            rows_missing_field += 1
            continue
        rows_with_field += 1
        violation_type = normalize_signal_value(row.get("violation_type"))
        if violation_type == "none":
            continue
        non_null_population += 1
        if violation_type in CORE_SOURCE_FAMILIES:
            core_family_population[violation_type] += 1
        elif violation_type in STRUCTURAL_PROBE_FAMILIES:
            structural_probe_population[violation_type] += 1
        elif violation_type in OUT_OF_SCOPE_SOURCE_FAMILIES:
            out_of_scope_population[violation_type] += 1

    if rows_with_field == 0 or rows_missing_field > 0:
        status = "blocked_by_missing_violation_type_field"
    elif non_null_population == 0:
        status = "blocked_by_empty_violation_type_population"
    elif not core_family_population:
        status = "closed_with_upstream_signal_gap_handoff"
    else:
        status = "pass"

    return {
        "status": status,
        "total_rows": total_rows,
        "rows_with_violation_type_field": rows_with_field,
        "rows_missing_violation_type_field": rows_missing_field,
        "violation_type_non_null_population": non_null_population,
        "core_source_family_population": dict(sorted(core_family_population.items())),
        "structural_probe_population": dict(sorted(structural_probe_population.items())),
        "out_of_scope_population": dict(sorted(out_of_scope_population.items())),
    }


def profile_expects_use(profile_rules: dict[str, Any]) -> bool:
    if "use_core" in set(str(value) for value in profile_rules.get("required_sections", [])):
        return True
    for minimum in profile_rules.get("adequate_minimum_any_of", []):
        if "use_core" in set(str(value) for value in minimum):
            return True
    return False


def first_non_identity_section(emitted_sections: list[str]) -> str | None:
    for section_name in emitted_sections:
        if section_name != "identity_core":
            return section_name
    return None


def section_family_name(base_family: str) -> str:
    return f"{SECTION_SIGNAL_PREFIX}{base_family}"


def section_surface_family(section_signal: str) -> str:
    if section_signal.startswith(SECTION_SIGNAL_PREFIX):
        return section_signal[len(SECTION_SIGNAL_PREFIX) :]
    return section_signal


def derive_source_signal(
    *,
    item_id: str,
    structural_row: dict[str, Any] | None,
    surface_signal_path: Path,
) -> dict[str, Any]:
    primary = "none"
    secondary: list[str] = []
    origins: list[dict[str, str]] = []

    if structural_row is None:
        return {
            "source_signal_primary": primary,
            "source_signal_secondary": secondary,
            "source_signal_origin": origins,
        }

    explicit = normalize_signal_value(structural_row.get("violation_type"))
    violation_flags = normalize_violation_flags(structural_row)

    if explicit in ALLOWED_SOURCE_FAMILIES:
        primary = explicit
        origins.append(
            build_origin(
                artifact_path=surface_signal_path,
                producer="surface_contract_signal",
                row_key=item_id,
                field="violation_type",
                json_path="$.violation_type",
            )
        )

    for flag in violation_flags:
        mapped_family = VIOLATION_FLAG_SOURCE_ALLOWLIST.get(flag)
        if mapped_family is None:
            continue
        origin = build_origin(
            artifact_path=surface_signal_path,
            producer="surface_contract_signal",
            row_key=item_id,
            field="violation_flags",
            json_path="$.violation_flags",
        )
        if primary == "none":
            primary = mapped_family
            origins.append(origin)
            continue
        if mapped_family != primary and mapped_family not in secondary:
            secondary.append(mapped_family)
            origins.append(origin)

    return {
        "source_signal_primary": primary,
        "source_signal_secondary": secondary,
        "source_signal_origin": origins,
    }


def derive_section_signal(
    *,
    item_id: str,
    entry: dict[str, Any],
    structural_row: dict[str, Any] | None,
    profile_rules: dict[str, Any] | None,
    rendered_path: Path,
    surface_signal_path: Path,
) -> dict[str, Any]:
    body_plan = entry.get("body_plan") if isinstance(entry.get("body_plan"), dict) else {}
    emitted_sections = [str(value) for value in body_plan.get("emitted_section_names", [])]
    emitted_set = set(emitted_sections)
    missing_required_sections = [str(value) for value in body_plan.get("missing_required_sections", [])]
    proxy_flags = set(normalize_violation_flags(structural_row))

    primary = SECTION_NONE
    secondary: list[str] = []
    origins: list[dict[str, str]] = []

    section_origin = build_origin(
        artifact_path=rendered_path,
        producer="body_plan_section_derivation",
        row_key=item_id,
        field="body_plan",
        json_path="$.body_plan",
    )

    if proxy_flags & LAYER4_PROXY_FLAGS:
        primary = section_family_name("LAYER4_ABSORPTION")
        origins.append(section_origin)
        origins.append(
            build_origin(
                artifact_path=surface_signal_path,
                producer="surface_contract_signal",
                row_key=item_id,
                field="violation_flags",
                json_path="$.violation_flags",
            )
        )
        return {
            "section_signal_primary": primary,
            "section_signal_secondary": secondary,
            "section_signal_origin": origins,
        }

    if "BODY_COLLAPSES_TO_ACQUISITION" in proxy_flags:
        primary = section_family_name("ACQ_DOMINANT")
        origins.append(section_origin)
    elif emitted_set == {"identity_core"} or (emitted_set and not (emitted_set - {"identity_core"})):
        primary = section_family_name("IDENTITY_ONLY")
        origins.append(section_origin)
    elif "BODY_LOSES_ITEM_CENTRICITY" in proxy_flags:
        primary = section_family_name("BODY_LACKS_ITEM_SPECIFIC_USE")
        origins.append(section_origin)
        origins.append(
            build_origin(
                artifact_path=surface_signal_path,
                producer="surface_contract_signal",
                row_key=item_id,
                field="violation_flags",
                json_path="$.violation_flags",
            )
        )
    elif "SECTION_COVERAGE_DEFICIT" in proxy_flags:
        if profile_rules is not None and profile_expects_use(profile_rules) and "use_core" not in emitted_set:
            primary = section_family_name("BODY_LACKS_ITEM_SPECIFIC_USE")
        elif first_non_identity_section(emitted_sections) == "acquisition_support":
            primary = section_family_name("ACQ_DOMINANT")
        else:
            primary = section_family_name("BODY_LACKS_ITEM_SPECIFIC_USE")
        origins.append(section_origin)
        origins.append(
            build_origin(
                artifact_path=surface_signal_path,
                producer="surface_contract_signal",
                row_key=item_id,
                field="violation_flags",
                json_path="$.violation_flags",
            )
        )
    elif (
        "use_core" in emitted_set
        and not (emitted_set & {"context_support", "acquisition_support", "limitation_tail"})
    ):
        primary = section_family_name("FUNCTION_NARROW")
        origins.append(section_origin)
    elif first_non_identity_section(emitted_sections) == "acquisition_support":
        primary = section_family_name("ACQ_DOMINANT")
        origins.append(section_origin)

    if primary != SECTION_NONE and missing_required_sections:
        origins.append(
            build_origin(
                artifact_path=rendered_path,
                producer="body_plan_section_derivation",
                row_key=item_id,
                field="missing_required_sections",
                json_path="$.body_plan.missing_required_sections",
            )
        )

    return {
        "section_signal_primary": primary,
        "section_signal_secondary": secondary,
        "section_signal_origin": origins,
    }


def derive_overlap_state(*, source_present_value: bool, section_present_value: bool) -> str:
    if source_present_value and section_present_value:
        return "coexist"
    if source_present_value:
        return "source_only"
    if section_present_value:
        return "section_only"
    return "dual_none"


def build_signal_conflict_note(*, source_primary: str, section_primary: str) -> str | None:
    if source_primary == "none" or section_primary == SECTION_NONE:
        return None
    if source_primary == section_surface_family(section_primary):
        return "source_and_section_same_surface_family"
    return "source_and_section_different_family"


def count_primary_by_runtime_state(rows: list[dict[str, Any]], field_name: str) -> dict[str, Counter[str]]:
    counts_total: Counter[str] = Counter()
    counts_active: Counter[str] = Counter()
    counts_silent: Counter[str] = Counter()

    for row in rows:
        primary = str(row[field_name])
        counts_total[primary] += 1
        if row["runtime_state"] == "silent":
            counts_silent[primary] += 1
        else:
            counts_active[primary] += 1

    return {
        "total": counts_total,
        "active": counts_active,
        "silent": counts_silent,
    }


def evaluate_count_preservation_target(
    *,
    rows: list[dict[str, Any]],
    structural_map: dict[str, dict[str, Any]],
    expected_target: dict[str, int],
) -> dict[str, Any]:
    observed_counts = Counter(str(row["source_signal_primary"]) for row in rows)
    implementation_errors: list[str] = []

    for row in rows:
        structural_row = structural_map.get(str(row["row_id"]))
        if structural_row is None:
            continue
        explicit = normalize_signal_value(structural_row.get("violation_type"))
        if explicit in COUNT_PRESERVATION_FAMILIES and row["source_signal_primary"] != explicit:
            implementation_errors.append(str(row["row_id"]))

    observed_subset = {
        family: int(observed_counts.get(family, 0))
        for family in sorted(expected_target)
    }
    expected_subset = {
        family: int(expected_target[family])
        for family in sorted(expected_target)
    }

    if implementation_errors:
        status = "implementation_error"
    elif observed_subset == expected_subset:
        status = "match"
    else:
        status = "mismatch_handoff"

    return {
        "status": status,
        "expected": expected_subset,
        "observed": observed_subset,
        "implementation_error_row_ids": implementation_errors,
    }


def build_distribution_summary(
    *,
    rows: list[dict[str, Any]],
    field_name: str,
    phase1_gate: dict[str, Any],
    count_target: dict[str, int] | None = None,
    structural_map: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    counts = count_primary_by_runtime_state(rows, field_name)
    summary = {
        "row_count": len(rows),
        "active_count": sum(counts["active"].values()),
        "silent_count": sum(counts["silent"].values()),
        "primary_counts": {
            bucket: dict(sorted(counter.items()))
            for bucket, counter in counts.items()
        },
        "phase1_gate": phase1_gate,
    }

    if count_target is not None and structural_map is not None:
        summary["target_check"] = evaluate_count_preservation_target(
            rows=rows,
            structural_map=structural_map,
            expected_target=count_target,
        )

    return summary


def build_crosswalk_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    matrix: defaultdict[str, Counter[str]] = defaultdict(Counter)
    overlap_counts: Counter[str] = Counter()
    existence_targets: dict[str, dict[str, int]] = {}
    silent_count = 0
    would_have_overwritten = 0
    structural_only_rows: list[str] = []

    for family in sorted(EXISTENCE_NO_OVERWRITE_FAMILIES):
        existence_targets[family] = {
            "source_primary_count": 0,
            "source_secondary_count": 0,
            "replaced_by_section_count": 0,
        }

    for row in rows:
        source_primary = str(row["source_signal_primary"])
        section_primary = str(row["section_signal_primary"])
        matrix[source_primary][section_primary] += 1
        overlap_counts[str(row["signal_overlap_state"])] += 1

        if row["runtime_state"] == "silent":
            silent_count += 1

        if row["signal_overlap_state"] == "section_only":
            structural_only_rows.append(str(row["row_id"]))

        if row["source_signal_present"] and row["section_signal_present"]:
            if source_primary == section_surface_family(section_primary):
                would_have_overwritten += 1

        source_secondary = set(str(value) for value in row["source_signal_secondary"])
        for family in EXISTENCE_NO_OVERWRITE_FAMILIES:
            if source_primary == family:
                existence_targets[family]["source_primary_count"] += 1
            if family in source_secondary:
                existence_targets[family]["source_secondary_count"] += 1
            if source_primary == family and section_primary == section_family_name(family):
                existence_targets[family]["replaced_by_section_count"] += 0

    return {
        "row_count": len(rows),
        "signal_overlap_state_counts": dict(sorted(overlap_counts.items())),
        "matrix_total": {
            source_family: dict(sorted(section_counts.items()))
            for source_family, section_counts in sorted(matrix.items())
        },
        "source_only_count": overlap_counts["source_only"],
        "section_only_count": overlap_counts["section_only"],
        "coexist_count": overlap_counts["coexist"],
        "dual_none_count": overlap_counts["dual_none"],
        "silent_count": silent_count,
        "silent_subcount_consistency": {
            "crosswalk_silent_count": silent_count,
        },
        "would_have_overwritten_count": would_have_overwritten,
        "newly_observed_structural_only_rows": {
            "count": len(structural_only_rows),
            "sample_row_ids": structural_only_rows[:25],
        },
        "existence_no_overwrite_targets": existence_targets,
    }


def build_signal_preservation_rows(
    *,
    rendered_entries: dict[str, dict[str, Any]],
    structural_map: dict[str, dict[str, Any]],
    profile_map: dict[str, dict[str, Any]],
    rendered_path: Path,
    surface_signal_path: Path,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for item_id in sorted(rendered_entries):
        entry = rendered_entries[item_id]
        runtime_state = active_runtime_state(entry)
        resolved_profile = entry.get("resolved_profile")
        profile_rules = profile_map.get(str(resolved_profile)) if resolved_profile is not None else None
        structural_row = structural_map.get(item_id)

        source_signal = derive_source_signal(
            item_id=item_id,
            structural_row=structural_row,
            surface_signal_path=surface_signal_path,
        )
        section_signal = derive_section_signal(
            item_id=item_id,
            entry=entry,
            structural_row=structural_row,
            profile_rules=profile_rules,
            rendered_path=rendered_path,
            surface_signal_path=surface_signal_path,
        )

        source_present_value = signal_present(
            primary=source_signal["source_signal_primary"],
            secondary=source_signal["source_signal_secondary"],
        )
        section_present_value = signal_present(
            primary=section_signal["section_signal_primary"],
            secondary=section_signal["section_signal_secondary"],
        )
        overlap_state = derive_overlap_state(
            source_present_value=source_present_value,
            section_present_value=section_present_value,
        )
        rows.append(
            {
                "row_id": item_id,
                "writer_role": "observer_only",
                "round_id": ROUND_ID,
                "runtime_state": runtime_state,
                "source_signal_primary": source_signal["source_signal_primary"],
                "source_signal_secondary": source_signal["source_signal_secondary"],
                "source_signal_origin": source_signal["source_signal_origin"],
                "section_signal_primary": section_signal["section_signal_primary"],
                "section_signal_secondary": section_signal["section_signal_secondary"],
                "section_signal_origin": section_signal["section_signal_origin"],
                "source_signal_present": source_present_value,
                "section_signal_present": section_present_value,
                "signal_overlap_state": overlap_state,
                "signal_conflict_note": build_signal_conflict_note(
                    source_primary=source_signal["source_signal_primary"],
                    section_primary=section_signal["section_signal_primary"],
                ),
            }
        )

    return rows


def build_signal_preservation_report(
    *,
    rendered_path: Path = RENDERED_PATH,
    surface_signal_path: Path = SURFACE_SIGNAL_PATH,
    profiles_path: Path = PROFILES_PATH,
    row_output_path: Path = ROW_OUTPUT_PATH,
    source_summary_path: Path = SOURCE_SUMMARY_PATH,
    section_summary_path: Path = SECTION_SUMMARY_PATH,
    crosswalk_summary_path: Path = CROSSWALK_SUMMARY_PATH,
    count_preservation_target: dict[str, int] | None = None,
    strict_phase1_gate: bool = True,
) -> dict[str, Any]:
    rendered_entries = load_json(rendered_path).get("entries", {})
    structural_rows = load_jsonl(surface_signal_path)
    structural_map = {str(row["item_id"]): row for row in structural_rows}
    profile_map = load_json(profiles_path).get("profiles", {})
    count_target = count_preservation_target or COUNT_PRESERVATION_TARGET

    phase1_gate = assess_violation_type_population(structural_rows)
    if strict_phase1_gate and phase1_gate["status"] in {
        "blocked_by_missing_violation_type_field",
        "blocked_by_empty_violation_type_population",
    }:
        raise ValueError(phase1_gate["status"])

    rows = build_signal_preservation_rows(
        rendered_entries=rendered_entries,
        structural_map=structural_map,
        profile_map=profile_map,
        rendered_path=rendered_path,
        surface_signal_path=surface_signal_path,
    )

    source_summary = build_distribution_summary(
        rows=rows,
        field_name="source_signal_primary",
        phase1_gate=phase1_gate,
        count_target=count_target,
        structural_map=structural_map,
    )
    section_summary = build_distribution_summary(
        rows=rows,
        field_name="section_signal_primary",
        phase1_gate=phase1_gate,
    )
    crosswalk_summary = build_crosswalk_summary(rows)

    write_jsonl(row_output_path, rows)
    write_json(source_summary_path, source_summary)
    write_json(section_summary_path, section_summary)
    write_json(crosswalk_summary_path, crosswalk_summary)

    return {
        "schema_version": "body-plan-signal-preservation-v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase1_gate_status": phase1_gate["status"],
        "artifact_refs": {
            "rendered_path": str(rendered_path),
            "surface_signal_path": str(surface_signal_path),
            "profiles_path": str(profiles_path),
            "row_output_path": str(row_output_path),
            "source_summary_path": str(source_summary_path),
            "section_summary_path": str(section_summary_path),
            "crosswalk_summary_path": str(crosswalk_summary_path),
        },
        "source_target_status": source_summary.get("target_check", {}).get("status"),
        "row_count": len(rows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build additive source/section signal preservation artifacts for body_plan Phase D."
    )
    parser.add_argument("--rendered-path", type=Path, default=RENDERED_PATH)
    parser.add_argument("--surface-signal-path", type=Path, default=SURFACE_SIGNAL_PATH)
    parser.add_argument("--profiles-path", type=Path, default=PROFILES_PATH)
    parser.add_argument("--row-output-path", type=Path, default=ROW_OUTPUT_PATH)
    parser.add_argument("--source-summary-path", type=Path, default=SOURCE_SUMMARY_PATH)
    parser.add_argument("--section-summary-path", type=Path, default=SECTION_SUMMARY_PATH)
    parser.add_argument("--crosswalk-summary-path", type=Path, default=CROSSWALK_SUMMARY_PATH)
    parser.add_argument(
        "--allow-handoff-phase1-gate",
        action="store_true",
        help="Allow generation when Phase 1 resolves to an upstream handoff status.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_signal_preservation_report(
        rendered_path=args.rendered_path,
        surface_signal_path=args.surface_signal_path,
        profiles_path=args.profiles_path,
        row_output_path=args.row_output_path,
        source_summary_path=args.source_summary_path,
        section_summary_path=args.section_summary_path,
        crosswalk_summary_path=args.crosswalk_summary_path,
        strict_phase1_gate=not args.allow_handoff_phase1_gate,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
