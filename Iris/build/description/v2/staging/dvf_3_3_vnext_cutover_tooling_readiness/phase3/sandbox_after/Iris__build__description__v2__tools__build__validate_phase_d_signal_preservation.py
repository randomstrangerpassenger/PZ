from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sys


ROOT = Path(__file__).resolve().parents[2]
IRIS_MOD_ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.build.report_layer3_body_plan_signal_preservation import (  # noqa: E402
    EXISTENCE_NO_OVERWRITE_FAMILIES,
    section_surface_family,
)


CURRENT_SESSION_DIR = ROOT / "staging" / "compose_contract_migration" / "phase_d_e_current_session"
ROUND_DIR = ROOT / "staging" / "compose_contract_migration" / "phase_d_signal_preservation_patch_round"

BASELINE_PATH = ROUND_DIR / "phase_d_signal_preservation_baseline.json"
ROW_PATH = ROUND_DIR / "body_plan_signal_preservation.2105.jsonl"  # DVF_AUTHORITY_ROLE_MIGRATION[67e89d2716cbdb9cb1af54685cd64265] DVF_AUTHORITY_ROLE_MIGRATION[67e89d2716cbdb9cb1af54685cd64265]
SOURCE_SUMMARY_PATH = ROUND_DIR / "body_plan_signal_preservation.source_distribution.json"
SECTION_SUMMARY_PATH = ROUND_DIR / "body_plan_signal_preservation.section_distribution.json"
CROSSWALK_SUMMARY_PATH = ROUND_DIR / "body_plan_signal_preservation.crosswalk.json"
REGRESSION_GATE_PATH = CURRENT_SESSION_DIR / "body_plan_v2_regression_gate_report.2105.json"  # DVF_AUTHORITY_ROLE_MIGRATION[004fe41efccb9cffaaa6c22a605d9dab] DVF_AUTHORITY_ROLE_MIGRATION[004fe41efccb9cffaaa6c22a605d9dab]
STRUCTURAL_ROW_PATH = CURRENT_SESSION_DIR / "body_plan_structural_reclassification.2105.jsonl"  # DVF_AUTHORITY_ROLE_MIGRATION[61806c5bde359b91bef5807eb1b58551] DVF_AUTHORITY_ROLE_MIGRATION[61806c5bde359b91bef5807eb1b58551]
STRUCTURAL_SUMMARY_PATH = CURRENT_SESSION_DIR / "body_plan_structural_reclassification.2105.summary.json"  # DVF_AUTHORITY_ROLE_MIGRATION[9bb6d46026c6d9cac74f25365857f36e] DVF_AUTHORITY_ROLE_MIGRATION[9bb6d46026c6d9cac74f25365857f36e]
STAGED_LUA_PATH = CURRENT_SESSION_DIR / "IrisLayer3Data.body_plan_v2.2105.staged.lua"  # DVF_AUTHORITY_ROLE_MIGRATION[87292b01a87cf88f73be18cc38c43602] DVF_AUTHORITY_ROLE_MIGRATION[87292b01a87cf88f73be18cc38c43602]
WORKSPACE_LUA_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3Data.lua"
OUTPUT_JSON_PATH = ROUND_DIR / "phase_d_signal_preservation_validation_report.json"
OUTPUT_MD_PATH = ROUND_DIR / "phase_d_signal_preservation_validation_report.md"


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


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def add_check(checks: list[dict[str, Any]], *, code: str, passed: bool, details: Any) -> None:
    checks.append({"code": code, "status": "pass" if passed else "fail", "details": details})


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Phase D Signal Preservation Validation Report",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- overall_status: `{payload['overall_status']}`",
        f"- failure_count: `{payload['failure_count']}`",
    ]
    if payload["failures"]:
        lines.append(f"- failures: `{', '.join(payload['failures'])}`")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for check in payload["checks"]:
        lines.append(f"- `{check['code']}`: `{check['status']}`")
    return "\n".join(lines) + "\n"


def build_validation_report(
    *,
    baseline_path: Path = BASELINE_PATH,
    row_path: Path = ROW_PATH,
    source_summary_path: Path = SOURCE_SUMMARY_PATH,
    section_summary_path: Path = SECTION_SUMMARY_PATH,
    crosswalk_summary_path: Path = CROSSWALK_SUMMARY_PATH,
    regression_gate_path: Path = REGRESSION_GATE_PATH,
    structural_row_path: Path = STRUCTURAL_ROW_PATH,
    structural_summary_path: Path = STRUCTURAL_SUMMARY_PATH,
    staged_lua_path: Path = STAGED_LUA_PATH,
    workspace_lua_path: Path = WORKSPACE_LUA_PATH,
    output_json_path: Path = OUTPUT_JSON_PATH,
    output_md_path: Path = OUTPUT_MD_PATH,
) -> dict[str, Any]:
    baseline = load_json(baseline_path)
    rows = load_jsonl(row_path)
    source_summary = load_json(source_summary_path)
    section_summary = load_json(section_summary_path)
    crosswalk_summary = load_json(crosswalk_summary_path)
    regression_gate = load_json(regression_gate_path)

    checks: list[dict[str, Any]] = []
    forbidden_fields = {"quality_state", "publish_state", "text_ko", "rendered_text"}
    row_runtime_counts = {
        "active": sum(1 for row in rows if row["runtime_state"] == "active"),
        "silent": sum(1 for row in rows if row["runtime_state"] == "silent"),
    }
    signal_overlap_total = sum(int(value) for value in crosswalk_summary["signal_overlap_state_counts"].values())
    forbidden_field_hits = sorted(
        {
            field
            for row in rows
            for field in forbidden_fields
            if field in row
        }
    )
    layer4_overwrite_violations = [
        row["row_id"]
        for row in rows
        if row["section_signal_primary"] == "SECTION_LAYER4_ABSORPTION"
        and row["source_signal_present"]
        and row["signal_overlap_state"] != "coexist"
    ]
    existence_target_violations = {
        family: crosswalk_summary["existence_no_overwrite_targets"][family]["replaced_by_section_count"]
        for family in EXISTENCE_NO_OVERWRITE_FAMILIES
    }

    add_check(
        checks,
        code="row_count_matches_baseline",
        passed=len(rows) == int(baseline["baseline"]["row_count"]),
        details={"actual": len(rows), "expected": baseline["baseline"]["row_count"]},
    )
    add_check(
        checks,
        code="writer_role_observer_only",
        passed=all(row["writer_role"] == "observer_only" for row in rows),
        details={"non_observer_rows": [row["row_id"] for row in rows if row["writer_role"] != "observer_only"][:20]},
    )
    add_check(
        checks,
        code="forbidden_fields_absent",
        passed=not forbidden_field_hits,
        details={"forbidden_field_hits": forbidden_field_hits},
    )
    add_check(
        checks,
        code="runtime_state_counts_unchanged",
        passed=row_runtime_counts == baseline["baseline"]["runtime_state_counts"],
        details={"actual": row_runtime_counts, "expected": baseline["baseline"]["runtime_state_counts"]},
    )
    add_check(
        checks,
        code="runtime_path_total_unchanged",
        passed=regression_gate["snapshot"]["runtime_path_counts"] == baseline["baseline"]["runtime_path_total"],
        details={
            "actual": regression_gate["snapshot"]["runtime_path_counts"],
            "expected": baseline["baseline"]["runtime_path_total"],
        },
    )
    add_check(
        checks,
        code="publish_split_unchanged",
        passed=regression_gate["snapshot"]["publish_state_counts"] == baseline["baseline"]["publish_split_active"],
        details={
            "actual": regression_gate["snapshot"]["publish_state_counts"],
            "expected": baseline["baseline"]["publish_split_active"],
        },
    )
    add_check(
        checks,
        code="quality_split_unchanged",
        passed=regression_gate["snapshot"]["quality_state_counts"] == baseline["baseline"]["quality_split_active"],
        details={
            "actual": regression_gate["snapshot"]["quality_state_counts"],
            "expected": baseline["baseline"]["quality_split_active"],
        },
    )
    add_check(
        checks,
        code="staged_lua_hash_unchanged",
        passed=sha256_file(staged_lua_path) == baseline["hashes"]["staged_lua_sha256"],
        details={"actual": sha256_file(staged_lua_path), "expected": baseline["hashes"]["staged_lua_sha256"]},
    )
    add_check(
        checks,
        code="workspace_lua_hash_unchanged",
        passed=sha256_file(workspace_lua_path) == baseline["hashes"]["workspace_lua_sha256"],
        details={
            "actual": sha256_file(workspace_lua_path),
            "expected": baseline["hashes"]["workspace_lua_sha256"],
        },
    )
    add_check(
        checks,
        code="existing_structural_artifact_hash_unchanged",
        passed=(
            sha256_file(structural_row_path) == baseline["hashes"]["structural_row_sha256"]
            and sha256_file(structural_summary_path) == baseline["hashes"]["structural_summary_sha256"]
        ),
        details={
            "row_actual": sha256_file(structural_row_path),
            "row_expected": baseline["hashes"]["structural_row_sha256"],
            "summary_actual": sha256_file(structural_summary_path),
            "summary_expected": baseline["hashes"]["structural_summary_sha256"],
        },
    )
    add_check(
        checks,
        code="source_distribution_target_status_allowed",
        passed=source_summary["target_check"]["status"] in {"match", "mismatch_handoff"},
        details={"status": source_summary["target_check"]["status"]},
    )
    add_check(
        checks,
        code="implementation_error_not_present",
        passed=source_summary["target_check"]["status"] != "implementation_error",
        details={"status": source_summary["target_check"]["status"]},
    )
    add_check(
        checks,
        code="existence_no_overwrite_targets_preserved",
        passed=all(value == 0 for value in existence_target_violations.values()),
        details=existence_target_violations,
    )
    add_check(
        checks,
        code="layer4_section_does_not_overwrite_source",
        passed=not layer4_overwrite_violations,
        details={"row_ids": layer4_overwrite_violations[:20]},
    )
    add_check(
        checks,
        code="source_summary_internally_consistent",
        passed=(
            source_summary["active_count"] + source_summary["silent_count"] == source_summary["row_count"]
            and sum(source_summary["primary_counts"]["total"].values()) == source_summary["row_count"]
            and sum(source_summary["primary_counts"]["active"].values()) == source_summary["active_count"]
            and sum(source_summary["primary_counts"]["silent"].values()) == source_summary["silent_count"]
        ),
        details=source_summary,
    )
    add_check(
        checks,
        code="section_summary_internally_consistent",
        passed=(
            section_summary["active_count"] + section_summary["silent_count"] == section_summary["row_count"]
            and sum(section_summary["primary_counts"]["total"].values()) == section_summary["row_count"]
            and sum(section_summary["primary_counts"]["active"].values()) == section_summary["active_count"]
            and sum(section_summary["primary_counts"]["silent"].values()) == section_summary["silent_count"]
        ),
        details=section_summary,
    )
    add_check(
        checks,
        code="crosswalk_totals_internally_consistent",
        passed=(
            signal_overlap_total == crosswalk_summary["row_count"]
            and (
                crosswalk_summary["source_only_count"]
                + crosswalk_summary["section_only_count"]
                + crosswalk_summary["coexist_count"]
                + crosswalk_summary["dual_none_count"]
            )
            == crosswalk_summary["row_count"]
        ),
        details=crosswalk_summary["signal_overlap_state_counts"],
    )
    add_check(
        checks,
        code="silent_row_subcounts_internally_consistent",
        passed=(
            source_summary["silent_count"] + source_summary["active_count"] == source_summary["row_count"]
            and crosswalk_summary["silent_count"] == source_summary["silent_count"]
        ),
        details={
            "source_summary": {
                "active_count": source_summary["active_count"],
                "silent_count": source_summary["silent_count"],
                "row_count": source_summary["row_count"],
            },
            "crosswalk_silent_count": crosswalk_summary["silent_count"],
        },
    )
    add_check(
        checks,
        code="hard_block_candidate_not_interpreted_as_writer_effect",
        passed=int(baseline["baseline"]["hard_block_candidate_count"]) == 0,
        details={"hard_block_candidate_count": baseline["baseline"]["hard_block_candidate_count"]},
    )

    failures = [check["code"] for check in checks if check["status"] != "pass"]
    payload = {
        "schema_version": "phase-d-signal-preservation-validation-v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": "pass" if not failures else "blocked",
        "artifact_refs": {
            "baseline_path": str(baseline_path),
            "row_path": str(row_path),
            "source_summary_path": str(source_summary_path),
            "section_summary_path": str(section_summary_path),
            "crosswalk_summary_path": str(crosswalk_summary_path),
            "regression_gate_path": str(regression_gate_path),
            "structural_row_path": str(structural_row_path),
            "structural_summary_path": str(structural_summary_path),
            "staged_lua_path": str(staged_lua_path),
            "workspace_lua_path": str(workspace_lua_path),
        },
        "checks": checks,
        "failure_count": len(failures),
        "failures": failures,
    }
    write_json(output_json_path, payload)
    write_text(output_md_path, render_markdown(payload))
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Phase D signal preservation additive artifacts.")
    parser.add_argument("--baseline-path", type=Path, default=BASELINE_PATH)
    parser.add_argument("--row-path", type=Path, default=ROW_PATH)
    parser.add_argument("--source-summary-path", type=Path, default=SOURCE_SUMMARY_PATH)
    parser.add_argument("--section-summary-path", type=Path, default=SECTION_SUMMARY_PATH)
    parser.add_argument("--crosswalk-summary-path", type=Path, default=CROSSWALK_SUMMARY_PATH)
    parser.add_argument("--regression-gate-path", type=Path, default=REGRESSION_GATE_PATH)
    parser.add_argument("--structural-row-path", type=Path, default=STRUCTURAL_ROW_PATH)
    parser.add_argument("--structural-summary-path", type=Path, default=STRUCTURAL_SUMMARY_PATH)
    parser.add_argument("--staged-lua-path", type=Path, default=STAGED_LUA_PATH)
    parser.add_argument("--workspace-lua-path", type=Path, default=WORKSPACE_LUA_PATH)
    parser.add_argument("--output-json-path", type=Path, default=OUTPUT_JSON_PATH)
    parser.add_argument("--output-md-path", type=Path, default=OUTPUT_MD_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_validation_report(
        baseline_path=args.baseline_path,
        row_path=args.row_path,
        source_summary_path=args.source_summary_path,
        section_summary_path=args.section_summary_path,
        crosswalk_summary_path=args.crosswalk_summary_path,
        regression_gate_path=args.regression_gate_path,
        structural_row_path=args.structural_row_path,
        structural_summary_path=args.structural_summary_path,
        staged_lua_path=args.staged_lua_path,
        workspace_lua_path=args.workspace_lua_path,
        output_json_path=args.output_json_path,
        output_md_path=args.output_md_path,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
