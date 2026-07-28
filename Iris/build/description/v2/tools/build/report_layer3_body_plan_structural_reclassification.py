from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.report_layer3_body_plan_signal_preservation import (
    COUNT_PRESERVATION_TARGET,
    PROFILES_PATH as CANONICAL_PROFILES_PATH,
    RENDERED_PATH as CANONICAL_RENDERED_PATH,
    SURFACE_SIGNAL_PATH as CANONICAL_SURFACE_SIGNAL_PATH,
    assess_violation_type_population,
    build_crosswalk_summary,
    build_distribution_summary,
    build_signal_preservation_rows,
)

ROUND_DIR = (
    ROOT
    / "staging"
    / "compose_contract_migration"
    / "phase_d_structural_reclassification_code_path_convergence_round"
)
PHASE4_DIR = ROUND_DIR / "phase4_artifacts"
LEGACY_DIR = ROUND_DIR / "diagnostic" / "legacy_view"

RENDERED_PATH = CANONICAL_RENDERED_PATH
SURFACE_SIGNAL_PATH = CANONICAL_SURFACE_SIGNAL_PATH
PROFILES_PATH = CANONICAL_PROFILES_PATH

ROW_OUTPUT_PATH = PHASE4_DIR / "body_plan_structural_reclassification.2105.jsonl"
SUMMARY_PATH = PHASE4_DIR / "body_plan_structural_reclassification.2105.summary.json"
SOURCE_SUMMARY_PATH = PHASE4_DIR / "body_plan_structural_reclassification.source_distribution.json"
SECTION_SUMMARY_PATH = PHASE4_DIR / "body_plan_structural_reclassification.section_distribution.json"
OVERLAP_SUMMARY_PATH = PHASE4_DIR / "body_plan_structural_reclassification.overlap_distribution.json"
CROSSWALK_SUMMARY_PATH = PHASE4_DIR / "body_plan_structural_reclassification.crosswalk.json"
ARTIFACT_VALIDATION_PATH = (
    PHASE4_DIR / "body_plan_structural_reclassification.artifact_validation_report.json"
)
LEGACY_ROW_OUTPUT_PATH = LEGACY_DIR / "body_plan_structural_reclassification_legacy_single_slot.2105.jsonl"
LEGACY_SUMMARY_PATH = LEGACY_DIR / "body_plan_structural_reclassification_legacy_single_slot.summary.json"

ROUND_ID = "phase_d_structural_reclassification_code_path_convergence_round_v0_1"

SECTION_DISTRIBUTION_TARGET = {
    "SECTION_FUNCTION_NARROW": 1433,
    "none": 672,
}
OVERLAP_DISTRIBUTION_TARGET = {
    "coexist": 557,
    "dual_none": 605,
    "section_only": 876,
    "source_only": 67,
}
FORBIDDEN_WRITER_FIELDS = {
    "quality_state",
    "publish_state",
    "text_ko",
    "rendered_text",
    "quality_publish_decision_preview",
}
LAYER4_PROXY_FLAGS = {"INTERACTION_LIST_DUPLICATION", "CROSS_LAYER_RAW_COPY"}


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


def add_check(checks: list[dict[str, Any]], *, code: str, passed: bool, details: Any) -> None:
    checks.append({"code": code, "status": "pass" if passed else "fail", "details": details})


def active_runtime_state(entry: dict[str, Any]) -> str:
    return "silent" if entry.get("source") == "silent" else "active"


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


def derive_family_reclassification(
    *,
    entry: dict[str, Any],
    structural_row: dict[str, Any] | None,
    profile_rules: dict[str, Any] | None,
) -> tuple[str, str, list[str]]:
    body_plan = entry.get("body_plan") if isinstance(entry.get("body_plan"), dict) else {}
    emitted_sections = [str(value) for value in body_plan.get("emitted_section_names", [])]
    emitted_set = set(emitted_sections)
    missing_required_sections = [str(value) for value in body_plan.get("missing_required_sections", [])]
    proxy_flags = set()
    if structural_row is not None:
        proxy_flags = set(str(value) for value in structural_row.get("violation_flags", []))

    evidence: list[str] = [
        f"emitted={','.join(emitted_sections) if emitted_sections else 'none'}",
        f"missing_required={','.join(missing_required_sections) if missing_required_sections else 'none'}",
        f"proxy_flags={','.join(sorted(proxy_flags)) if proxy_flags else 'none'}",
    ]

    if proxy_flags & LAYER4_PROXY_FLAGS:
        return "LAYER4_ABSORPTION", "hard_block_candidate", evidence

    if "BODY_COLLAPSES_TO_ACQUISITION" in proxy_flags:
        return "ACQ_DOMINANT", "publish_isolation_candidate", evidence

    if emitted_set == {"identity_core"} or (emitted_set and not (emitted_set - {"identity_core"})):
        return "IDENTITY_ONLY", "publish_isolation_candidate", evidence

    if "BODY_LOSES_ITEM_CENTRICITY" in proxy_flags:
        return "BODY_LACKS_ITEM_SPECIFIC_USE", "publish_isolation_candidate", evidence

    if "SECTION_COVERAGE_DEFICIT" in proxy_flags:
        if profile_rules is not None and profile_expects_use(profile_rules) and "use_core" not in emitted_set:
            return "BODY_LACKS_ITEM_SPECIFIC_USE", "publish_isolation_candidate", evidence
        if first_non_identity_section(emitted_sections) == "acquisition_support":
            return "ACQ_DOMINANT", "publish_isolation_candidate", evidence
        return "BODY_LACKS_ITEM_SPECIFIC_USE", "publish_isolation_candidate", evidence

    if (
        "use_core" in emitted_set
        and not (emitted_set & {"context_support", "acquisition_support", "limitation_tail"})
    ):
        return "FUNCTION_NARROW", "advisory_only", evidence

    if first_non_identity_section(emitted_sections) == "acquisition_support":
        return "ACQ_DOMINANT", "advisory_only", evidence

    return "none", "advisory_only", evidence


def signal_distribution_from_family_counts(family_counts: Counter[str]) -> dict[str, int]:
    return {
        str(family): int(count)
        for family, count in sorted(family_counts.items())
        if str(family) != "none"
    }


def build_legacy_view(
    *,
    rendered_entries: dict[str, dict[str, Any]],
    structural_map: dict[str, dict[str, Any]],
    profile_map: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    runtime_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    tier_counts: Counter[str] = Counter()
    proxy_flag_counts: Counter[str] = Counter()
    resolved_profile_counts: Counter[str] = Counter()

    for item_id in sorted(rendered_entries):
        entry = rendered_entries[item_id]
        runtime_state = active_runtime_state(entry)
        runtime_counts[runtime_state] += 1

        resolved_profile = entry.get("resolved_profile")
        profile_rules = profile_map.get(str(resolved_profile)) if resolved_profile is not None else None
        structural_row = structural_map.get(item_id)
        body_plan = entry.get("body_plan") if isinstance(entry.get("body_plan"), dict) else {}
        proxy_flags = [] if structural_row is None else list(structural_row.get("violation_flags", []))
        for flag in proxy_flags:
            proxy_flag_counts[str(flag)] += 1

        if runtime_state == "silent":
            family = "none"
            tier = "advisory_only"
            evidence = ["runtime_state=silent"]
        else:
            family, tier, evidence = derive_family_reclassification(
                entry=entry,
                structural_row=structural_row,
                profile_rules=profile_rules,
            )
            if resolved_profile is not None:
                resolved_profile_counts[str(resolved_profile)] += 1

        family_counts[family] += 1
        tier_counts[tier] += 1
        rows.append(
            {
                "item_id": item_id,
                "writer_role": "observer_only",
                "runtime_state": runtime_state,
                "resolved_profile": resolved_profile,
                "emitted_section_names": list(body_plan.get("emitted_section_names", [])),
                "missing_required_sections": list(body_plan.get("missing_required_sections", [])),
                "proxy_violation_flags": proxy_flags,
                "legacy_family_reclassification": family,
                "recommended_tier": tier,
                "hard_block_candidate": tier == "hard_block_candidate",
                "evidence": "; ".join(evidence),
            }
        )

    summary = {
        "schema_version": "body-plan-structural-reclassification-legacy-single-slot-v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "row_count": len(rows),
        "writer_role": "observer_only",
        "runtime_state_counts": dict(sorted(runtime_counts.items())),
        "resolved_profile_counts": dict(sorted(resolved_profile_counts.items())),
        "legacy_family_reclassification_counts": dict(sorted(family_counts.items())),
        "signal_distribution": signal_distribution_from_family_counts(family_counts),
        "recommended_tier_counts": dict(sorted(tier_counts.items())),
        "proxy_violation_flag_counts": dict(sorted(proxy_flag_counts.items())),
        "hard_block_candidate_count": tier_counts["hard_block_candidate"],
    }
    return rows, summary


def build_exact_target_check(
    *,
    observed_counts: Counter[str],
    expected_target: dict[str, int],
    implementation_error_row_ids: list[str] | None = None,
) -> dict[str, Any]:
    implementation_errors = list(implementation_error_row_ids or [])
    observed = {family: int(observed_counts.get(family, 0)) for family in sorted(expected_target)}
    expected = {family: int(expected_target[family]) for family in sorted(expected_target)}
    if implementation_errors:
        status = "implementation_error"
    elif observed == expected:
        status = "match"
    else:
        status = "mismatch"
    return {
        "status": status,
        "expected": expected,
        "observed": observed,
        "implementation_error_row_ids": implementation_errors,
    }


def build_overlap_distribution_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_counts: Counter[str] = Counter()
    active_counts: Counter[str] = Counter()
    silent_counts: Counter[str] = Counter()
    for row in rows:
        overlap_state = str(row["signal_overlap_state"])
        total_counts[overlap_state] += 1
        if row["runtime_state"] == "silent":
            silent_counts[overlap_state] += 1
        else:
            active_counts[overlap_state] += 1

    return {
        "row_count": len(rows),
        "active_count": sum(active_counts.values()),
        "silent_count": sum(silent_counts.values()),
        "counts": {
            "total": dict(sorted(total_counts.items())),
            "active": dict(sorted(active_counts.items())),
            "silent": dict(sorted(silent_counts.items())),
        },
        "target_check": build_exact_target_check(
            observed_counts=total_counts,
            expected_target=OVERLAP_DISTRIBUTION_TARGET,
        ),
    }


def build_artifact_validation_report(
    *,
    rows: list[dict[str, Any]],
    source_summary: dict[str, Any],
    section_summary: dict[str, Any],
    overlap_summary: dict[str, Any],
    crosswalk_summary: dict[str, Any],
    linked_artifacts: dict[str, str],
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    forbidden_field_hits = sorted(
        {
            field
            for row in rows
            for field in FORBIDDEN_WRITER_FIELDS
            if field in row
        }
    )
    required_pointer_keys = {
        "source_distribution",
        "section_distribution",
        "overlap_distribution",
        "crosswalk",
        "artifact_validation_report",
    }
    source_total = sum(int(value) for value in source_summary["primary_counts"]["total"].values())
    section_total = sum(int(value) for value in section_summary["primary_counts"]["total"].values())
    overlap_total = sum(int(value) for value in overlap_summary["counts"]["total"].values())
    crosswalk_total = sum(int(value) for value in crosswalk_summary["signal_overlap_state_counts"].values())

    add_check(
        checks,
        code="writer_role_observer_only",
        passed=all(row.get("writer_role") == "observer_only" for row in rows),
        details={
            "non_observer_rows": [row.get("row_id") for row in rows if row.get("writer_role") != "observer_only"][:20]
        },
    )
    add_check(
        checks,
        code="canonical_rows_expose_dual_axis_fields",
        passed=all(
            {
                "source_signal_primary",
                "source_signal_secondary",
                "source_signal_origin",
                "source_signal_present",
                "section_signal_primary",
                "section_signal_secondary",
                "section_signal_origin",
                "section_signal_present",
                "signal_overlap_state",
            }.issubset(row)
            and "legacy_family_reclassification" not in row
            for row in rows
        ),
        details={"row_count": len(rows)},
    )
    add_check(
        checks,
        code="forbidden_writer_fields_absent",
        passed=not forbidden_field_hits,
        details={"forbidden_field_hits": forbidden_field_hits},
    )
    add_check(
        checks,
        code="source_summary_internally_consistent",
        passed=(
            source_summary["row_count"] == len(rows)
            and source_summary["active_count"] + source_summary["silent_count"] == source_summary["row_count"]
            and source_total == source_summary["row_count"]
        ),
        details=source_summary,
    )
    add_check(
        checks,
        code="section_summary_internally_consistent",
        passed=(
            section_summary["row_count"] == len(rows)
            and section_summary["active_count"] + section_summary["silent_count"] == section_summary["row_count"]
            and section_total == section_summary["row_count"]
        ),
        details=section_summary,
    )
    add_check(
        checks,
        code="overlap_summary_internally_consistent",
        passed=(
            overlap_summary["row_count"] == len(rows)
            and overlap_summary["active_count"] + overlap_summary["silent_count"] == overlap_summary["row_count"]
            and overlap_total == overlap_summary["row_count"]
        ),
        details=overlap_summary,
    )
    add_check(
        checks,
        code="crosswalk_totals_consistent",
        passed=(
            crosswalk_summary["row_count"] == len(rows)
            and crosswalk_total == crosswalk_summary["row_count"]
            and crosswalk_summary["signal_overlap_state_counts"] == overlap_summary["counts"]["total"]
        ),
        details={
            "crosswalk_signal_overlap_state_counts": crosswalk_summary["signal_overlap_state_counts"],
            "overlap_summary_total": overlap_summary["counts"]["total"],
        },
    )
    add_check(
        checks,
        code="summary_pointer_integrity",
        passed=required_pointer_keys.issubset(linked_artifacts) and all(linked_artifacts.values()),
        details={"linked_artifacts": linked_artifacts},
    )

    failures = [check["code"] for check in checks if check["status"] != "pass"]
    return {
        "schema_version": "body-plan-structural-reclassification-artifact-validation-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": "pass" if not failures else "blocked",
        "checks": checks,
        "failure_count": len(failures),
        "failures": failures,
    }


def build_canonical_summary(
    *,
    rows: list[dict[str, Any]],
    phase1_gate: dict[str, Any],
    source_summary: dict[str, Any],
    section_summary: dict[str, Any],
    overlap_summary: dict[str, Any],
    crosswalk_summary: dict[str, Any],
    artifact_validation: dict[str, Any],
    linked_artifacts: dict[str, str],
    rendered_path: Path,
    surface_signal_path: Path,
    profiles_path: Path,
    row_output_path: Path,
    legacy_summary: dict[str, Any],
    emit_legacy_view: bool,
    legacy_row_output_path: Path,
    legacy_summary_path: Path,
) -> dict[str, Any]:
    legacy_compat_summary = {
        "mode": "diagnostic_only",
        "legacy_family_reclassification_counts": legacy_summary["legacy_family_reclassification_counts"],
        "signal_distribution": legacy_summary["signal_distribution"],
        "recommended_tier_counts": legacy_summary["recommended_tier_counts"],
        "proxy_violation_flag_counts": legacy_summary["proxy_violation_flag_counts"],
        "hard_block_candidate_count": legacy_summary["hard_block_candidate_count"],
    }
    if emit_legacy_view:
        legacy_compat_summary["diagnostic_artifact_refs"] = {
            "legacy_row_output_path": str(legacy_row_output_path),
            "legacy_summary_path": str(legacy_summary_path),
        }

    return {
        "schema_version": "body-plan-structural-reclassification-summary-v1",
        "summary_schema_version": "body-plan-structural-reclassification-summary-stable-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_read_model": "dual_axis_canonical",
        "phase1_gate_status": phase1_gate["status"],
        "artifact_refs": {
            "rendered_path": str(rendered_path),
            "surface_signal_path": str(surface_signal_path),
            "profiles_path": str(profiles_path),
            "row_output_path": str(row_output_path),
        },
        "row_count": len(rows),
        "writer_role": "observer_only",
        "runtime_state_counts": dict(
            sorted(Counter(str(row["runtime_state"]) for row in rows).items())
        ),
        "hard_block_candidate_count": legacy_summary["hard_block_candidate_count"],
        "source_signal_primary_counts": source_summary["primary_counts"]["total"],
        "section_signal_primary_counts": section_summary["primary_counts"]["total"],
        "signal_overlap_state_counts": overlap_summary["counts"]["total"],
        "source_target_check": source_summary["target_check"],
        "section_target_check": section_summary["target_check"],
        "overlap_target_check": overlap_summary["target_check"],
        "artifact_validation_overview": {
            "overall_status": artifact_validation["overall_status"],
            "failure_count": artifact_validation["failure_count"],
            "failures": artifact_validation["failures"],
        },
        "linked_artifacts": linked_artifacts,
        "legacy_compat_summary": legacy_compat_summary,
        "crosswalk_summary": {
            "would_have_overwritten_count": crosswalk_summary["would_have_overwritten_count"],
            "existence_no_overwrite_targets": crosswalk_summary["existence_no_overwrite_targets"],
        },
    }


def build_reclassification_report(
    *,
    rendered_path: Path = RENDERED_PATH,
    surface_signal_path: Path = SURFACE_SIGNAL_PATH,
    profiles_path: Path = PROFILES_PATH,
    output_path: Path = ROW_OUTPUT_PATH,
    summary_path: Path = SUMMARY_PATH,
    source_summary_path: Path = SOURCE_SUMMARY_PATH,
    section_summary_path: Path = SECTION_SUMMARY_PATH,
    overlap_summary_path: Path = OVERLAP_SUMMARY_PATH,
    crosswalk_summary_path: Path = CROSSWALK_SUMMARY_PATH,
    artifact_validation_path: Path = ARTIFACT_VALIDATION_PATH,
    emit_legacy_view: bool = False,
    legacy_row_output_path: Path = LEGACY_ROW_OUTPUT_PATH,
    legacy_summary_path: Path = LEGACY_SUMMARY_PATH,
    strict_phase1_gate: bool = True,
) -> dict[str, Any]:
    rendered_entries = load_json(rendered_path).get("entries", {})
    structural_rows = load_jsonl(surface_signal_path)
    structural_map = {str(row["item_id"]): row for row in structural_rows}
    profile_map = load_json(profiles_path).get("profiles", {})

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
    for row in rows:
        row["round_id"] = ROUND_ID

    legacy_rows, legacy_summary = build_legacy_view(
        rendered_entries=rendered_entries,
        structural_map=structural_map,
        profile_map=profile_map,
    )

    source_summary = build_distribution_summary(
        rows=rows,
        field_name="source_signal_primary",
        phase1_gate=phase1_gate,
        count_target=COUNT_PRESERVATION_TARGET,
        structural_map=structural_map,
    )
    source_summary["target_check"] = build_exact_target_check(
        observed_counts=Counter(str(row["source_signal_primary"]) for row in rows),
        expected_target=COUNT_PRESERVATION_TARGET,
        implementation_error_row_ids=source_summary["target_check"]["implementation_error_row_ids"],
    )

    section_summary = build_distribution_summary(
        rows=rows,
        field_name="section_signal_primary",
        phase1_gate=phase1_gate,
    )
    section_summary["target_check"] = build_exact_target_check(
        observed_counts=Counter(str(row["section_signal_primary"]) for row in rows),
        expected_target=SECTION_DISTRIBUTION_TARGET,
    )

    overlap_summary = build_overlap_distribution_summary(rows)
    crosswalk_summary = build_crosswalk_summary(rows)

    linked_artifacts = {
        "source_distribution": str(source_summary_path),
        "section_distribution": str(section_summary_path),
        "overlap_distribution": str(overlap_summary_path),
        "crosswalk": str(crosswalk_summary_path),
        "artifact_validation_report": str(artifact_validation_path),
    }
    artifact_validation = build_artifact_validation_report(
        rows=rows,
        source_summary=source_summary,
        section_summary=section_summary,
        overlap_summary=overlap_summary,
        crosswalk_summary=crosswalk_summary,
        linked_artifacts=linked_artifacts,
    )
    summary = build_canonical_summary(
        rows=rows,
        phase1_gate=phase1_gate,
        source_summary=source_summary,
        section_summary=section_summary,
        overlap_summary=overlap_summary,
        crosswalk_summary=crosswalk_summary,
        artifact_validation=artifact_validation,
        linked_artifacts=linked_artifacts,
        rendered_path=rendered_path,
        surface_signal_path=surface_signal_path,
        profiles_path=profiles_path,
        row_output_path=output_path,
        legacy_summary=legacy_summary,
        emit_legacy_view=emit_legacy_view,
        legacy_row_output_path=legacy_row_output_path,
        legacy_summary_path=legacy_summary_path,
    )

    write_jsonl(output_path, rows)
    write_json(summary_path, summary)
    write_json(source_summary_path, source_summary)
    write_json(section_summary_path, section_summary)
    write_json(overlap_summary_path, overlap_summary)
    write_json(crosswalk_summary_path, crosswalk_summary)
    write_json(artifact_validation_path, artifact_validation)

    if emit_legacy_view:
        write_jsonl(legacy_row_output_path, legacy_rows)
        write_json(legacy_summary_path, legacy_summary)

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit canonical dual-axis structural reclassification artifacts for the observer default path."
    )
    parser.add_argument("--rendered-path", type=Path, default=RENDERED_PATH)
    parser.add_argument("--surface-signal-path", type=Path, default=SURFACE_SIGNAL_PATH)
    parser.add_argument("--profiles-path", type=Path, default=PROFILES_PATH)
    parser.add_argument("--output-path", type=Path, default=ROW_OUTPUT_PATH)
    parser.add_argument("--summary-path", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--source-summary-path", type=Path, default=SOURCE_SUMMARY_PATH)
    parser.add_argument("--section-summary-path", type=Path, default=SECTION_SUMMARY_PATH)
    parser.add_argument("--overlap-summary-path", type=Path, default=OVERLAP_SUMMARY_PATH)
    parser.add_argument("--crosswalk-summary-path", type=Path, default=CROSSWALK_SUMMARY_PATH)
    parser.add_argument("--artifact-validation-path", type=Path, default=ARTIFACT_VALIDATION_PATH)
    parser.add_argument(
        "--emit-legacy-view",
        action="store_true",
        help="Write explicit diagnostic legacy single-slot artifacts alongside the canonical default outputs.",
    )
    parser.add_argument("--legacy-row-output-path", type=Path, default=LEGACY_ROW_OUTPUT_PATH)
    parser.add_argument("--legacy-summary-path", type=Path, default=LEGACY_SUMMARY_PATH)
    parser.add_argument(
        "--allow-handoff-phase1-gate",
        action="store_true",
        help="Allow generation when Phase 1 resolves to an upstream handoff status.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = build_reclassification_report(
        rendered_path=args.rendered_path,
        surface_signal_path=args.surface_signal_path,
        profiles_path=args.profiles_path,
        output_path=args.output_path,
        summary_path=args.summary_path,
        source_summary_path=args.source_summary_path,
        section_summary_path=args.section_summary_path,
        overlap_summary_path=args.overlap_summary_path,
        crosswalk_summary_path=args.crosswalk_summary_path,
        artifact_validation_path=args.artifact_validation_path,
        emit_legacy_view=args.emit_legacy_view,
        legacy_row_output_path=args.legacy_row_output_path,
        legacy_summary_path=args.legacy_summary_path,
        strict_phase1_gate=not args.allow_handoff_phase1_gate,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
