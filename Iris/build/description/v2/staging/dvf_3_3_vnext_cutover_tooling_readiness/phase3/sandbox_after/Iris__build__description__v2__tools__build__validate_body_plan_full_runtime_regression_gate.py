from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .compose_layer3_body_profile import (
        ADOPTED_RUNTIME_STATE,
        UNADOPTED_RUNTIME_STATE,
        normalize_runtime_state,
    )
except ImportError:
    from compose_layer3_body_profile import (
        ADOPTED_RUNTIME_STATE,
        UNADOPTED_RUNTIME_STATE,
        normalize_runtime_state,
    )


ROOT = Path(__file__).resolve().parents[2]
STAGING_DIR = ROOT / "staging" / "compose_contract_migration"
FULL_RUNTIME_DIR = STAGING_DIR / "full_runtime"

RENDERED_SUMMARY_PATH = FULL_RUNTIME_DIR / "dvf_3_3_rendered_v2_preview.summary.full.json"
QUALITY_SUMMARY_PATH = FULL_RUNTIME_DIR / "quality_publish_decision_v2_preview.summary.full.json"
DELTA_SUMMARY_PATH = FULL_RUNTIME_DIR / "dvf_3_3_rendered_v2_delta.summary.full.json"
BLOCKER_SUMMARY_PATH = FULL_RUNTIME_DIR / "dvf_3_3_body_plan_v2_blockers.summary.full.json"
DETERMINISM_REPORT_PATH = STAGING_DIR / "compose_determinism_report.json"
LEGACY_DIFF_REPORT_PATH = STAGING_DIR / "legacy_vs_bodyplan_diff_report.json"
STRUCTURAL_RECLASSIFICATION_SUMMARY_PATH = (
    FULL_RUNTIME_DIR / "body_plan_structural_reclassification.summary.full.json"
)
CURRENT_DECISIONS_PATH = (
    ROOT
    / "staging"
    / "second_pass_backlog_132"
    / "sprint7_residual_closure"
    / "sprint7_overlay_preview_decisions.jsonl"
)
CURRENT_RUNTIME_SUMMARY_PATH = (
    ROOT
    / "staging"
    / "identity_fallback_source_expansion"
    / "phase6_subset_rollout"
    / "exec_subset_600_wrench_crowbar_b7_b8_b9"
    / "subset_runtime_summary.json"
)
QUALITY_BASELINE_V4_PATH = (
    ROOT
    / "staging"
    / "semantic_quality"
    / "phaseE_contract_migration"
    / "quality_baseline_v4.json"
)
OUTPUT_PATH = FULL_RUNTIME_DIR / "body_plan_v2_regression_gate_report.json"

CURRENT_BASELINE = {
    "row_count": 2105,  # DVF_AUTHORITY_ROLE_MIGRATION[96f18502aee9d64196dbd23872a9af6b] DVF_AUTHORITY_ROLE_MIGRATION[96f18502aee9d64196dbd23872a9af6b]
    "runtime_state_counts": {ADOPTED_RUNTIME_STATE: 2084, UNADOPTED_RUNTIME_STATE: 21},  # DVF_AUTHORITY_ROLE_MIGRATION[f613f10e573175b7b39fa4ca00cd1d05] DVF_AUTHORITY_ROLE_MIGRATION[cc544d465ae83b3be43b64e30cc02839] DVF_AUTHORITY_ROLE_MIGRATION[cc544d465ae83b3be43b64e30cc02839] DVF_AUTHORITY_ROLE_MIGRATION[f613f10e573175b7b39fa4ca00cd1d05]
    "runtime_path_counts": {
        "cluster_summary": 2040,
        "identity_fallback": 17,
        "role_fallback": 48,
    },
    "quality_state_counts": {"strong": 1316, "adequate": 0, "weak": 768},
    "publish_state_counts": {"internal_only": 617, "exposed": 1467},
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


def add_check(
    checks: list[dict[str, Any]],
    *,
    code: str,
    passed: bool,
    details: Any,
) -> None:
    checks.append({"code": code, "status": "pass" if passed else "fail", "details": details})


def get_nested(payload: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def normalize_counts(counts: dict[str, Any] | None) -> dict[str, int]:
    return {str(key): int(value) for key, value in (counts or {}).items()}


def normalize_runtime_state_counts(counts: dict[str, Any] | None) -> dict[str, int]:
    normalized: Counter[str] = Counter()
    for key, value in (counts or {}).items():
        normalized[
            normalize_runtime_state(
                key,
                allow_legacy=True,
                field_name="runtime_state",
            )
        ] += int(value)
    return dict(normalized)


def legacy_family_counts_from_summary(structural_summary: dict[str, Any]) -> dict[str, int] | None:
    legacy_compat_summary = structural_summary.get("legacy_compat_summary")
    if isinstance(legacy_compat_summary, dict):
        return normalize_counts(legacy_compat_summary.get("legacy_family_reclassification_counts"))
    legacy_counts = structural_summary.get("legacy_family_reclassification_counts")
    if legacy_counts is None:
        return None
    return normalize_counts(legacy_counts)


def summarize_decisions(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    rows = load_jsonl(path)
    return {
        "row_count": len(rows),
        "runtime_state_counts": dict(
            Counter(
                normalize_runtime_state(
                    row.get("state"),
                    allow_legacy=True,
                    item_id=row.get("item_id"),
                )
                for row in rows
            )
        ),
        "runtime_path_counts": dict(Counter(str(row.get("use_source")) for row in rows)),
    }


def quality_metrics_from_summary(
    *,
    quality_summary: dict[str, Any],
    quality_baseline: dict[str, Any] | None,
) -> dict[str, Any]:
    baseline_runtime = get_nested(quality_baseline or {}, "full_runtime_snapshot", default={})
    baseline_publish = get_nested(quality_baseline or {}, "publish_surface_snapshot", default={})
    return {
        "row_count": quality_summary.get(
            "total_rows",
            baseline_runtime.get("total_rows"),
        ),
        "runtime_state_counts": normalize_runtime_state_counts(
            quality_summary.get("runtime_state_counts")
            or {
                ADOPTED_RUNTIME_STATE: quality_summary.get(
                    "adopted_total",
                    quality_summary.get("active_total", baseline_runtime.get("active_total")),
                ),
                UNADOPTED_RUNTIME_STATE: quality_summary.get(
                    "unadopted_total",
                    quality_summary.get("silent_total", baseline_runtime.get("silent_total")),
                ),
            }
        ),
        "quality_state_counts": normalize_counts(
            quality_summary.get("quality_state_counts")
            or baseline_runtime.get("quality_state_counts")
        ),
        "publish_state_counts": normalize_counts(
            quality_summary.get("publish_state_counts")
            or baseline_publish.get("publish_state_counts")
        ),
    }


def add_axis(
    axes: list[dict[str, Any]],
    *,
    code: str,
    passed: bool,
    details: Any,
) -> None:
    axes.append({"code": code, "status": "pass" if passed else "fail", "details": details})


def build_regression_gate_report(
    *,
    rendered_summary_path: Path = RENDERED_SUMMARY_PATH,
    quality_summary_path: Path = QUALITY_SUMMARY_PATH,
    quality_baseline_path: Path | None = QUALITY_BASELINE_V4_PATH,
    decisions_path: Path | None = CURRENT_DECISIONS_PATH,
    runtime_summary_path: Path | None = CURRENT_RUNTIME_SUMMARY_PATH,
    delta_summary_path: Path = DELTA_SUMMARY_PATH,
    blocker_summary_path: Path = BLOCKER_SUMMARY_PATH,
    determinism_report_path: Path = DETERMINISM_REPORT_PATH,
    legacy_diff_report_path: Path | None = None,
    structural_reclassification_summary_path: Path = STRUCTURAL_RECLASSIFICATION_SUMMARY_PATH,
    output_path: Path = OUTPUT_PATH,
    enforce_current_baseline: bool = True,
) -> dict[str, Any]:
    if not enforce_current_baseline:
        quality_baseline_path = None
        decisions_path = None
        runtime_summary_path = None
    rendered_summary = load_json(rendered_summary_path)
    quality_summary = load_json(quality_summary_path)
    quality_baseline = load_json(quality_baseline_path) if quality_baseline_path else None
    decisions_summary = summarize_decisions(decisions_path)
    runtime_summary = load_json(runtime_summary_path) if runtime_summary_path else None
    runtime_summary_counts = normalize_runtime_state_counts((runtime_summary or {}).get("state_counts"))
    runtime_path_counts = normalize_counts(
        (runtime_summary or {}).get("runtime_path_counts")
        or (decisions_summary or {}).get("runtime_path_counts")
    )
    delta_summary = load_json(delta_summary_path)
    blocker_summary = load_json(blocker_summary_path)
    determinism_report = load_json(determinism_report_path)
    legacy_diff_report = load_json(legacy_diff_report_path) if legacy_diff_report_path else None
    structural_summary = load_json(structural_reclassification_summary_path)
    legacy_family_counts = legacy_family_counts_from_summary(structural_summary)

    row_count = int(rendered_summary.get("row_count", -1))
    unadopted_count = int(
        rendered_summary.get("unadopted_count", rendered_summary.get("silent_count", 0))
    )
    adopted_count = int(rendered_summary.get("row_count", 0)) - unadopted_count
    rendered_runtime_counts = {
        ADOPTED_RUNTIME_STATE: adopted_count,
        UNADOPTED_RUNTIME_STATE: unadopted_count,
    }
    quality_metrics = quality_metrics_from_summary(
        quality_summary=quality_summary,
        quality_baseline=quality_baseline,
    )
    delta_row_count = int(delta_summary.get("row_count", -1))
    structural_row_count = int(structural_summary.get("row_count", -1))
    unexpected_delta_count = int(
        get_nested(delta_summary, "delta_classification_counts", "unexpected_delta", default=0)
    )
    quality_row_count = quality_metrics.get("row_count")
    accidental_change_count = (
        int(legacy_diff_report.get("accidental_change_count", unexpected_delta_count))
        if legacy_diff_report
        else unexpected_delta_count
    )

    expected_row_count = CURRENT_BASELINE["row_count"] if enforce_current_baseline else row_count
    expected_runtime_counts = (
        CURRENT_BASELINE["runtime_state_counts"] if enforce_current_baseline else rendered_runtime_counts
    )
    expected_runtime_path_counts = CURRENT_BASELINE["runtime_path_counts"] if enforce_current_baseline else None
    expected_publish_counts = (
        CURRENT_BASELINE["publish_state_counts"]
        if enforce_current_baseline
        else quality_metrics["publish_state_counts"]
    )
    expected_quality_counts = (
        CURRENT_BASELINE["quality_state_counts"]
        if enforce_current_baseline
        else quality_metrics["quality_state_counts"]
    )

    gate_axes: list[dict[str, Any]] = []
    add_axis(
        gate_axes,
        code="row_count_consistent",
        passed=(
            row_count
            == delta_row_count
            == structural_row_count
            == int((runtime_summary or {}).get("row_count", expected_row_count))
            == (decisions_summary or {}).get("row_count", expected_row_count)
            == expected_row_count
            and (quality_row_count is None or int(quality_row_count) == expected_row_count)
        ),
        details={
            "rendered": row_count,
            "delta": delta_row_count,
            "structural_reclassification": structural_row_count,
            "quality": quality_metrics.get("row_count"),
            "runtime_summary": None if runtime_summary is None else runtime_summary.get("row_count"),
            "decisions": None if decisions_summary is None else decisions_summary.get("row_count"),
            "expected": expected_row_count,
        },
    )
    add_axis(
        gate_axes,
        code="runtime_state_counts_consistent",
        passed=(
            rendered_runtime_counts == expected_runtime_counts
            and quality_metrics["runtime_state_counts"] == expected_runtime_counts
            and (not runtime_summary_counts or runtime_summary_counts == expected_runtime_counts)
            and (
                decisions_summary is None
                or normalize_counts(decisions_summary.get("runtime_state_counts")) == expected_runtime_counts
            )
        ),
        details={
            "rendered": rendered_runtime_counts,
            "quality": quality_metrics["runtime_state_counts"],
            "runtime_summary": None if runtime_summary is None else runtime_summary.get("state_counts"),
            "decisions": None if decisions_summary is None else decisions_summary.get("runtime_state_counts"),
            "expected": expected_runtime_counts,
        },
    )
    add_axis(
        gate_axes,
        code="runtime_path_counts_consistent",
        passed=(
            expected_runtime_path_counts is None
            or runtime_path_counts == expected_runtime_path_counts
        ),
        details={
            "runtime_summary": None if runtime_summary is None else runtime_summary.get("runtime_path_counts"),
            "decisions_fallback": None if decisions_summary is None else decisions_summary.get("runtime_path_counts"),
            "expected": expected_runtime_path_counts,
        },
    )
    add_axis(
        gate_axes,
        code="publish_state_split_consistent",
        passed=quality_metrics["publish_state_counts"] == expected_publish_counts,
        details={
            "actual": quality_metrics["publish_state_counts"],
            "expected": expected_publish_counts,
            "basis": "adopted rows only; unadopted rows excluded",
        },
    )
    add_axis(
        gate_axes,
        code="determinism_pass",
        passed=bool(determinism_report.get("overall_pass")),
        details={"overall_pass": determinism_report.get("overall_pass")},
    )
    add_axis(
        gate_axes,
        code="accidental_change_zero",
        passed=accidental_change_count == 0,
        details={
            "accidental_change_count": accidental_change_count,
            "source": "legacy_diff_report" if legacy_diff_report else "delta_unexpected_count",
        },
    )
    add_axis(
        gate_axes,
        code="unexpected_delta_zero",
        passed=not delta_summary.get("unexpected_reason_counts")
        and unexpected_delta_count == 0,
        details={
            "delta_classification_counts": delta_summary.get("delta_classification_counts"),
            "unexpected_reason_counts": delta_summary.get("unexpected_reason_counts"),
        },
    )
    add_axis(
        gate_axes,
        code="publish_state_no_regression",
        passed="exposed->internal_only" not in delta_summary.get("publish_transition_counts", {}),
        details={"publish_transition_counts": delta_summary.get("publish_transition_counts")},
    )
    add_axis(
        gate_axes,
        code="layer4_hard_block_zero",
        passed=int(structural_summary.get("hard_block_candidate_count", -1)) == 0,
        details={
            "hard_block_candidate_count": structural_summary.get("hard_block_candidate_count"),
            "legacy_family_reclassification_counts": legacy_family_counts,
        },
    )
    quality_distribution_gate = {
        "code": "quality_distribution_gate",
        "status": (
            "pass"
            if quality_metrics["quality_state_counts"] == expected_quality_counts
            else "fail"
        ),
        "details": {
            "actual": quality_metrics["quality_state_counts"],
            "expected": expected_quality_counts,
            "basis": "adopted rows only; unadopted rows excluded",
            "quality_baseline_path": None if quality_baseline_path is None else str(quality_baseline_path),
        },
    }

    checks = gate_axes + [quality_distribution_gate]
    failures = [check["code"] for check in checks if check["status"] != "pass"]
    payload = {
        "schema_version": "body-plan-v2-full-runtime-regression-gate-v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": "pass" if not failures else "blocked",
        "baseline_enforcement": "current_2105_quality_baseline_v4" if enforce_current_baseline else "disabled_for_test_or_diagnostic",  # DVF_AUTHORITY_ROLE_MIGRATION[ce54da4fd80c52d45e65605db4680ef8] DVF_AUTHORITY_ROLE_MIGRATION[ce54da4fd80c52d45e65605db4680ef8]
        "gate_axis_count": len(gate_axes),
        "artifact_refs": {
            "rendered_summary_path": str(rendered_summary_path),
            "quality_summary_path": str(quality_summary_path),
            "quality_baseline_path": None if quality_baseline_path is None else str(quality_baseline_path),
            "decisions_path": None if decisions_path is None else str(decisions_path),
            "runtime_summary_path": None if runtime_summary_path is None else str(runtime_summary_path),
            "delta_summary_path": str(delta_summary_path),
            "blocker_summary_path": str(blocker_summary_path),
            "determinism_report_path": str(determinism_report_path),
            "legacy_diff_report_path": None if legacy_diff_report_path is None else str(legacy_diff_report_path),
            "structural_reclassification_summary_path": str(structural_reclassification_summary_path),
        },
        "snapshot": {
            "row_count": row_count,
            "adopted_count": adopted_count,
            "unadopted_count": unadopted_count,
            "runtime_path_counts": runtime_path_counts,
            "quality_state_counts": quality_metrics["quality_state_counts"],
            "publish_state_counts": quality_metrics["publish_state_counts"],
            "delta_classification_counts": delta_summary.get("delta_classification_counts"),
            "blocker_count": blocker_summary.get("blocker_count"),
            "legacy_family_reclassification_counts": legacy_family_counts,
        },
        "gate_axes": gate_axes,
        "quality_distribution_gate": quality_distribution_gate,
        "checks": checks,
        "failure_count": len(failures),
        "failures": failures,
    }
    write_json(output_path, payload)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate body_plan v2 full-runtime regression gate.")
    parser.add_argument("--rendered-summary-path", type=Path, default=RENDERED_SUMMARY_PATH)
    parser.add_argument("--quality-summary-path", type=Path, default=QUALITY_SUMMARY_PATH)
    parser.add_argument("--quality-baseline-path", type=Path, default=QUALITY_BASELINE_V4_PATH)
    parser.add_argument("--decisions-path", type=Path, default=CURRENT_DECISIONS_PATH)
    parser.add_argument("--runtime-summary-path", type=Path, default=CURRENT_RUNTIME_SUMMARY_PATH)
    parser.add_argument("--delta-summary-path", type=Path, default=DELTA_SUMMARY_PATH)
    parser.add_argument("--blocker-summary-path", type=Path, default=BLOCKER_SUMMARY_PATH)
    parser.add_argument("--determinism-report-path", type=Path, default=DETERMINISM_REPORT_PATH)
    parser.add_argument("--legacy-diff-report-path", type=Path, default=None)
    parser.add_argument(
        "--structural-reclassification-summary-path",
        type=Path,
        default=STRUCTURAL_RECLASSIFICATION_SUMMARY_PATH,
    )
    parser.add_argument("--output-path", type=Path, default=OUTPUT_PATH)
    parser.add_argument(
        "--allow-noncurrent-baseline",
        action="store_true",
        help="Disable sealed 2105 runtime/quality/publish baseline checks for isolated diagnostics only.",  # DVF_AUTHORITY_ROLE_MIGRATION[dc1d11455c9464cb70a886dd401857c7] DVF_AUTHORITY_ROLE_MIGRATION[dc1d11455c9464cb70a886dd401857c7]
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_regression_gate_report(
        rendered_summary_path=args.rendered_summary_path,
        quality_summary_path=args.quality_summary_path,
        quality_baseline_path=args.quality_baseline_path,
        decisions_path=args.decisions_path,
        runtime_summary_path=args.runtime_summary_path,
        delta_summary_path=args.delta_summary_path,
        blocker_summary_path=args.blocker_summary_path,
        determinism_report_path=args.determinism_report_path,
        legacy_diff_report_path=args.legacy_diff_report_path,
        structural_reclassification_summary_path=args.structural_reclassification_summary_path,
        output_path=args.output_path,
        enforce_current_baseline=not args.allow_noncurrent_baseline,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
