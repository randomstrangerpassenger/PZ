from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.build_structural_reclassification_artifact_hash_guard import (  # noqa: E402
    OUTPUT_JSON_PATH as ARTIFACT_HASH_GUARD_PATH,
)
from tools.build.build_structural_reclassification_entrypoint_surface_guard import (  # noqa: E402
    OUTPUT_JSON_PATH as ENTRYPOINT_SURFACE_GUARD_PATH,
)
from tools.build.report_layer3_body_plan_structural_reclassification import (  # noqa: E402
    ARTIFACT_VALIDATION_PATH,
    CROSSWALK_SUMMARY_PATH,
    OVERLAP_SUMMARY_PATH,
    ROW_OUTPUT_PATH,
    SECTION_SUMMARY_PATH,
    SOURCE_SUMMARY_PATH,
    SUMMARY_PATH,
)


CURRENT_SESSION_DIR = ROOT / "staging" / "compose_contract_migration" / "phase_d_e_current_session"
ROUND_DIR = (
    ROOT
    / "staging"
    / "compose_contract_migration"
    / "phase_d_structural_reclassification_code_path_convergence_round"
)
PHASE5_DIR = ROUND_DIR / "phase5_validation"

REGRESSION_GATE_PATH = CURRENT_SESSION_DIR / "body_plan_v2_regression_gate_report.2105.json"  # DVF_AUTHORITY_ROLE_MIGRATION[ae6f7c411fb7fdf19736919960d558e1] DVF_AUTHORITY_ROLE_MIGRATION[ae6f7c411fb7fdf19736919960d558e1]
RUNTIME_VALIDATION_REPORT_PATH = CURRENT_SESSION_DIR / "body_plan_v2_runtime_validation_report.2105.json"  # DVF_AUTHORITY_ROLE_MIGRATION[cf8fab2f10cf34e57119fb93f2b2020a] DVF_AUTHORITY_ROLE_MIGRATION[cf8fab2f10cf34e57119fb93f2b2020a]
OUTPUT_JSON_PATH = PHASE5_DIR / "convergence_validation_report.json"


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


def add_check(
    checks: list[dict[str, Any]],
    *,
    code: str,
    passed: bool,
    details: Any,
    category: str,
) -> None:
    checks.append(
        {
            "code": code,
            "status": "pass" if passed else "fail",
            "details": details,
            "category": category,
        }
    )


def build_convergence_validation_report(
    *,
    row_path: Path = ROW_OUTPUT_PATH,
    summary_path: Path = SUMMARY_PATH,
    source_summary_path: Path = SOURCE_SUMMARY_PATH,
    section_summary_path: Path = SECTION_SUMMARY_PATH,
    overlap_summary_path: Path = OVERLAP_SUMMARY_PATH,
    crosswalk_summary_path: Path = CROSSWALK_SUMMARY_PATH,
    artifact_validation_path: Path = ARTIFACT_VALIDATION_PATH,
    regression_gate_path: Path = REGRESSION_GATE_PATH,
    runtime_validation_report_path: Path = RUNTIME_VALIDATION_REPORT_PATH,
    entrypoint_surface_guard_path: Path = ENTRYPOINT_SURFACE_GUARD_PATH,
    artifact_hash_guard_path: Path = ARTIFACT_HASH_GUARD_PATH,
    output_json_path: Path = OUTPUT_JSON_PATH,
) -> dict[str, Any]:
    rows = load_jsonl(row_path)
    summary = load_json(summary_path)
    source_summary = load_json(source_summary_path)
    section_summary = load_json(section_summary_path)
    overlap_summary = load_json(overlap_summary_path)
    crosswalk_summary = load_json(crosswalk_summary_path)
    artifact_validation = load_json(artifact_validation_path)
    regression_gate = load_json(regression_gate_path)
    runtime_validation_report = load_json(runtime_validation_report_path)
    entrypoint_surface_guard = load_json(entrypoint_surface_guard_path)
    artifact_hash_guard = load_json(artifact_hash_guard_path)

    checks: list[dict[str, Any]] = []
    row_runtime_counts = {
        "active": sum(1 for row in rows if row.get("runtime_state") == "active"),
        "silent": sum(1 for row in rows if row.get("runtime_state") == "silent"),
    }
    dual_axis_row_violations = [
        str(row.get("row_id"))
        for row in rows
        if not {
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
        or "legacy_family_reclassification" in row
    ]
    forbidden_field_hits = sorted(
        {
            field
            for row in rows
            for field in {
                "quality_state",
                "publish_state",
                "text_ko",
                "rendered_text",
                "quality_baseline_v4",
                "quality_publish_decision_preview",
            }
            if field in row
        }
    )
    existence_target_violations = {
        family: int(targets["replaced_by_section_count"])
        for family, targets in crosswalk_summary["existence_no_overwrite_targets"].items()
    }

    add_check(
        checks,
        code="row_count_matches_regression_snapshot",
        passed=len(rows) == int(regression_gate["snapshot"]["row_count"]),
        details={"actual": len(rows), "expected": regression_gate["snapshot"]["row_count"]},
        category="hard_guard",
    )
    add_check(
        checks,
        code="runtime_state_counts_unchanged",
        passed=(
            row_runtime_counts["active"] == int(regression_gate["snapshot"]["active_count"])
            and row_runtime_counts["silent"] == int(regression_gate["snapshot"]["silent_count"])
        ),
        details={
            "actual": row_runtime_counts,
            "expected": {
                "active": regression_gate["snapshot"]["active_count"],
                "silent": regression_gate["snapshot"]["silent_count"],
            },
        },
        category="hard_guard",
    )
    add_check(
        checks,
        code="dual_axis_rows_present",
        passed=not dual_axis_row_violations,
        details={"row_ids": dual_axis_row_violations[:20]},
        category="hard_guard",
    )
    add_check(
        checks,
        code="summary_declares_dual_axis_current_read_model",
        passed=str(summary.get("current_read_model")) == "dual_axis_canonical",
        details={"current_read_model": summary.get("current_read_model")},
        category="hard_guard",
    )
    add_check(
        checks,
        code="summary_schema_stable_subset_present",
        passed=(
            summary.get("summary_schema_version") is not None
            and isinstance(summary.get("linked_artifacts"), dict)
            and isinstance(summary.get("legacy_compat_summary"), dict)
        ),
        details={
            "summary_schema_version": summary.get("summary_schema_version"),
            "linked_artifacts_keys": sorted((summary.get("linked_artifacts") or {}).keys()),
            "has_legacy_compat_summary": isinstance(summary.get("legacy_compat_summary"), dict),
        },
        category="hard_guard",
    )
    add_check(
        checks,
        code="observer_only_contract_preserved",
        passed=all(str(row.get("writer_role")) == "observer_only" for row in rows),
        details={
            "non_observer_rows": [str(row.get("row_id")) for row in rows if row.get("writer_role") != "observer_only"][
                :20
            ]
        },
        category="hard_guard",
    )
    add_check(
        checks,
        code="forbidden_writer_fields_absent",
        passed=not forbidden_field_hits,
        details={"forbidden_field_hits": forbidden_field_hits},
        category="hard_guard",
    )
    add_check(
        checks,
        code="artifact_validation_report_pass",
        passed=str(artifact_validation.get("overall_status")) == "pass",
        details={"overall_status": artifact_validation.get("overall_status"), "failures": artifact_validation.get("failures")},
        category="hard_guard",
    )
    add_check(
        checks,
        code="entrypoint_surface_guard_pass",
        passed=str(entrypoint_surface_guard.get("overall_status")) == "pass",
        details={"overall_status": entrypoint_surface_guard.get("overall_status"), "failures": entrypoint_surface_guard.get("failures")},
        category="hard_guard",
    )
    add_check(
        checks,
        code="artifact_hash_guard_pass",
        passed=str(artifact_hash_guard.get("overall_status")) == "pass",
        details={"overall_status": artifact_hash_guard.get("overall_status"), "failures": artifact_hash_guard.get("failures")},
        category="hard_guard",
    )
    add_check(
        checks,
        code="runtime_validation_status_unchanged",
        passed=str(runtime_validation_report.get("overall_status")) == "ready_for_in_game_validation",
        details={"overall_status": runtime_validation_report.get("overall_status")},
        category="hard_guard",
    )
    add_check(
        checks,
        code="existence_no_overwrite_targets_preserved",
        passed=all(value == 0 for value in existence_target_violations.values()),
        details=existence_target_violations,
        category="hard_guard",
    )
    add_check(
        checks,
        code="source_distribution_exact_match",
        passed=str(source_summary["target_check"]["status"]) == "match",
        details=source_summary["target_check"],
        category="exact_match",
    )
    add_check(
        checks,
        code="section_distribution_exact_match",
        passed=str(section_summary["target_check"]["status"]) == "match",
        details=section_summary["target_check"],
        category="exact_match",
    )
    add_check(
        checks,
        code="overlap_distribution_exact_match",
        passed=str(overlap_summary["target_check"]["status"]) == "match",
        details=overlap_summary["target_check"],
        category="exact_match",
    )

    hard_failures = [check["code"] for check in checks if check["category"] == "hard_guard" and check["status"] != "pass"]
    exact_match_failures = [
        check["code"] for check in checks if check["category"] == "exact_match" and check["status"] != "pass"
    ]
    if hard_failures:
        overall_status = "blocked"
        recommended_closeout_state = None
    elif exact_match_failures:
        overall_status = "ready_for_handoff"
        recommended_closeout_state = "closed_with_distribution_handoff_to_next_round"
    else:
        overall_status = "pass"
        recommended_closeout_state = "closed_with_canonical_code_path_convergence_applied"

    payload = {
        "schema_version": "structural-reclassification-convergence-validation-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "recommended_closeout_state": recommended_closeout_state,
        "artifact_refs": {
            "row_path": str(row_path),
            "summary_path": str(summary_path),
            "source_summary_path": str(source_summary_path),
            "section_summary_path": str(section_summary_path),
            "overlap_summary_path": str(overlap_summary_path),
            "crosswalk_summary_path": str(crosswalk_summary_path),
            "artifact_validation_path": str(artifact_validation_path),
            "regression_gate_path": str(regression_gate_path),
            "runtime_validation_report_path": str(runtime_validation_report_path),
            "entrypoint_surface_guard_path": str(entrypoint_surface_guard_path),
            "artifact_hash_guard_path": str(artifact_hash_guard_path),
        },
        "checks": checks,
        "hard_failure_count": len(hard_failures),
        "hard_failures": hard_failures,
        "exact_match_failure_count": len(exact_match_failures),
        "exact_match_failures": exact_match_failures,
    }
    write_json(output_json_path, payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate structural reclassification canonical code-path convergence.")
    parser.add_argument("--row-path", type=Path, default=ROW_OUTPUT_PATH)
    parser.add_argument("--summary-path", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--source-summary-path", type=Path, default=SOURCE_SUMMARY_PATH)
    parser.add_argument("--section-summary-path", type=Path, default=SECTION_SUMMARY_PATH)
    parser.add_argument("--overlap-summary-path", type=Path, default=OVERLAP_SUMMARY_PATH)
    parser.add_argument("--crosswalk-summary-path", type=Path, default=CROSSWALK_SUMMARY_PATH)
    parser.add_argument("--artifact-validation-path", type=Path, default=ARTIFACT_VALIDATION_PATH)
    parser.add_argument("--regression-gate-path", type=Path, default=REGRESSION_GATE_PATH)
    parser.add_argument("--runtime-validation-report-path", type=Path, default=RUNTIME_VALIDATION_REPORT_PATH)
    parser.add_argument("--entrypoint-surface-guard-path", type=Path, default=ENTRYPOINT_SURFACE_GUARD_PATH)
    parser.add_argument("--artifact-hash-guard-path", type=Path, default=ARTIFACT_HASH_GUARD_PATH)
    parser.add_argument("--output-json-path", type=Path, default=OUTPUT_JSON_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_convergence_validation_report(
        row_path=args.row_path,
        summary_path=args.summary_path,
        source_summary_path=args.source_summary_path,
        section_summary_path=args.section_summary_path,
        overlap_summary_path=args.overlap_summary_path,
        crosswalk_summary_path=args.crosswalk_summary_path,
        artifact_validation_path=args.artifact_validation_path,
        regression_gate_path=args.regression_gate_path,
        runtime_validation_report_path=args.runtime_validation_report_path,
        entrypoint_surface_guard_path=args.entrypoint_surface_guard_path,
        artifact_hash_guard_path=args.artifact_hash_guard_path,
        output_json_path=args.output_json_path,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
