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

FULL_RUNTIME_DIR = ROOT / "staging" / "compose_contract_migration" / "full_runtime"

RENDERED_PATH = FULL_RUNTIME_DIR / "dvf_3_3_rendered_v2_preview.full.json"
PUBLISH_PREVIEW_PATH = FULL_RUNTIME_DIR / "quality_publish_decision_v2_preview.full.jsonl"
REGRESSION_GATE_PATH = FULL_RUNTIME_DIR / "body_plan_v2_regression_gate_report.json"
LUA_OUTPUT_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "IrisLayer3Data.lua"
BRIDGE_REPORT_PATH = FULL_RUNTIME_DIR / "body_plan_v2_lua_bridge_report.json"
RUNTIME_REPORT_PATH = FULL_RUNTIME_DIR / "body_plan_v2_runtime_validation_report.json"
ROLLOUT_REPORT_PATH = FULL_RUNTIME_DIR / "body_plan_v2_runtime_rollout_report.json"
STAGED_LUA_OUTPUT_PATH = FULL_RUNTIME_DIR / "IrisLayer3Data.body_plan_v2.staged.lua"

LAYER3_RENDERER_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "layer3_renderer.lua"
BOOT_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "AIrisBoot.lua"
MAIN_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "IrisMain.lua"
CONTEXT_MENU_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Wiki" / "IrisContextMenu.lua"
BROWSER_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Browser" / "IrisBrowser.lua"
PANEL_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Wiki" / "IrisWikiPanel.lua"
WIKI_SECTIONS_PATH = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "UI" / "Wiki" / "IrisWikiSections.lua"

from tools.build.export_dvf_3_3_lua_bridge import (  # noqa: E402
    export_lua_bridge,
)
from tools.build.validate_interaction_cluster_phase_d_runtime import (  # noqa: E402
    build_phase_d_runtime_report,
)


def load_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def build_runtime_rollout(
    *,
    rendered_path: Path = RENDERED_PATH,
    publish_preview_path: Path = PUBLISH_PREVIEW_PATH,
    regression_gate_path: Path = REGRESSION_GATE_PATH,
    staged_lua_output_path: Path | None = None,
    lua_output_path: Path = LUA_OUTPUT_PATH,
    bridge_report_path: Path = BRIDGE_REPORT_PATH,
    runtime_report_path: Path = RUNTIME_REPORT_PATH,
    rollout_report_path: Path = ROLLOUT_REPORT_PATH,
    chunk_output_dir: Path | None = None,
    chunk_manifest_path: Path | None = None,
    expected_bridge_row_count: int | None = None,
    expected_internal_only_count: int | None = None,
    expected_exposed_count: int | None = None,
    baseline_lua_sha256: str | None = None,
) -> dict[str, Any]:
    previous_lua_sha256 = sha256_file(lua_output_path) if lua_output_path.exists() else None
    regression_gate = load_report(regression_gate_path)
    resolved_chunk_output_dir = chunk_output_dir or lua_output_path.parent / "IrisLayer3DataChunks"
    resolved_chunk_manifest_path = chunk_manifest_path or lua_output_path.parent / "IrisLayer3DataChunks.lua"
    if regression_gate.get("overall_status") != "pass":
        report = {
            "schema_version": "body-plan-v2-runtime-rollout-report-v0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "overall_status": "blocked",
            "block_reason": "regression_gate_not_pass",
            "artifact_refs": {
                "rendered_path": str(rendered_path),
                "publish_preview_path": str(publish_preview_path),
                "regression_gate_path": str(regression_gate_path),
                "staged_lua_output_path": None if staged_lua_output_path is None else str(staged_lua_output_path),
                "lua_output_path": str(lua_output_path),
                "bridge_report_path": str(bridge_report_path),
                "runtime_report_path": str(runtime_report_path),
                "chunk_manifest_path": str(resolved_chunk_manifest_path),
                "chunk_output_dir": str(resolved_chunk_output_dir),
            },
            "checks": [
                {
                    "code": "regression_gate_pass",
                    "status": "fail",
                    "details": regression_gate.get("overall_status"),
                }
            ],
            "failure_count": 1,
            "failures": ["regression_gate_pass"],
        }
        write_json(rollout_report_path, report)
        return report
    export_output_path = staged_lua_output_path or lua_output_path
    bridge_report = export_lua_bridge(
        rendered_path=rendered_path,
        publish_preview_path=publish_preview_path,
        lua_output_path=export_output_path,
        report_path=bridge_report_path,
        chunk_output_dir=resolved_chunk_output_dir,
        chunk_manifest_path=resolved_chunk_manifest_path,
    )
    runtime_report = build_phase_d_runtime_report(
        rendered_path=rendered_path,
        bridge_report_path=bridge_report_path,
        layer3_chunk_manifest_path=resolved_chunk_manifest_path,
        layer3_chunk_dir=resolved_chunk_output_dir,
        layer3_renderer_path=LAYER3_RENDERER_PATH,
        boot_path=BOOT_PATH,
        main_path=MAIN_PATH,
        context_menu_path=CONTEXT_MENU_PATH,
        browser_path=BROWSER_PATH,
        panel_path=PANEL_PATH,
        wiki_sections_path=WIKI_SECTIONS_PATH,
        output_path=runtime_report_path,
    )

    chunk_manifest_exists = resolved_chunk_manifest_path.exists()
    chunk_files = sorted(resolved_chunk_output_dir.glob("Chunk*.lua")) if resolved_chunk_output_dir.exists() else []
    chunk_artifact_verified = (
        bridge_report.get("format") == "chunk"
        and bridge_report.get("monolith_generated") is False
        and chunk_manifest_exists
        and bool(chunk_files)
        and not lua_output_path.exists()
        and (staged_lua_output_path is None or not staged_lua_output_path.exists())
    )
    runtime_publish_counts = bridge_report.get("runtime_publish_state_counts") or {}

    checks = [
        {
            "code": "regression_gate_pass",
            "status": "pass" if regression_gate.get("overall_status") == "pass" else "fail",
            "details": regression_gate.get("overall_status"),
        },
        {
            "code": "lua_bridge_export_pass",
            "status": "pass" if bridge_report.get("pass") is True else "fail",
            "details": {
                "source_entry_count": bridge_report.get("source_entry_count"),
                "runtime_entry_count": bridge_report.get("runtime_entry_count"),
                "runtime_publish_state_counts": bridge_report.get("runtime_publish_state_counts"),
            },
        },
        {
            "code": "bridge_row_count_matches_expected",
            "status": (
                "pass"
                if expected_bridge_row_count is None
                or (
                    bridge_report.get("source_entry_count") == expected_bridge_row_count
                    and bridge_report.get("runtime_entry_count") == expected_bridge_row_count
                )
                else "fail"
            ),
            "details": {
                "source_entry_count": bridge_report.get("source_entry_count"),
                "runtime_entry_count": bridge_report.get("runtime_entry_count"),
                "expected": expected_bridge_row_count,
            },
        },
        {
            "code": "bridge_publish_split_matches_expected",
            "status": (
                "pass"
                if expected_internal_only_count is None
                or expected_exposed_count is None
                or (
                    runtime_publish_counts.get("internal_only") == expected_internal_only_count
                    and runtime_publish_counts.get("exposed") == expected_exposed_count
                )
                else "fail"
            ),
            "details": {
                "runtime_publish_state_counts": runtime_publish_counts,
                "expected": {
                    "internal_only": expected_internal_only_count,
                    "exposed": expected_exposed_count,
                },
            },
        },
        {
            "code": "runtime_validation_ready",
            "status": (
                "pass"
                if runtime_report.get("overall_status") == "ready_for_in_game_validation"
                else "fail"
            ),
            "details": runtime_report.get("overall_status"),
        },
        {
            "code": "chunk_artifact_verified",
            "status": "pass" if chunk_artifact_verified else "fail",
            "details": {
                "chunk_manifest_path": str(resolved_chunk_manifest_path),
                "chunk_manifest_sha256": (
                    sha256_file(resolved_chunk_manifest_path) if resolved_chunk_manifest_path.exists() else None
                ),
                "chunk_count": len(chunk_files),
                "lua_output_path_exists": lua_output_path.exists(),
                "staged_lua_output_path_exists": (
                    None if staged_lua_output_path is None else staged_lua_output_path.exists()
                ),
            },
        },
    ]
    failures = [check["code"] for check in checks if check["status"] != "pass"]
    report = {
        "schema_version": "body-plan-v2-runtime-rollout-report-v0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "overall_status": "pass" if not failures else "blocked",
        "artifact_refs": {
            "rendered_path": str(rendered_path),
            "publish_preview_path": str(publish_preview_path),
            "regression_gate_path": str(regression_gate_path),
            "staged_lua_output_path": None if staged_lua_output_path is None else str(staged_lua_output_path),
            "lua_output_path": str(lua_output_path),
            "bridge_report_path": str(bridge_report_path),
            "runtime_report_path": str(runtime_report_path),
            "chunk_manifest_path": str(resolved_chunk_manifest_path),
            "chunk_output_dir": str(resolved_chunk_output_dir),
        },
        "previous_lua_sha256": previous_lua_sha256,
        "baseline_lua_sha256": baseline_lua_sha256,
        "new_chunk_manifest_sha256": (
            sha256_file(resolved_chunk_manifest_path) if resolved_chunk_manifest_path.exists() else None
        ),
        "status_label": (
            "ready_for_in_game_validation"
            if not failures and runtime_report.get("overall_status") == "ready_for_in_game_validation"
            else "blocked"
        ),
        "checks": checks,
        "failure_count": len(failures),
        "failures": failures,
    }
    write_json(rollout_report_path, report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Roll out body_plan v2 full-runtime data to Iris Lua bridge.")
    parser.add_argument("--rendered-path", type=Path, default=RENDERED_PATH)
    parser.add_argument("--publish-preview-path", type=Path, default=PUBLISH_PREVIEW_PATH)
    parser.add_argument("--regression-gate-path", type=Path, default=REGRESSION_GATE_PATH)
    parser.add_argument("--staged-lua-output-path", type=Path, default=None)
    parser.add_argument("--lua-output-path", type=Path, default=LUA_OUTPUT_PATH)
    parser.add_argument("--bridge-report-path", type=Path, default=BRIDGE_REPORT_PATH)
    parser.add_argument("--runtime-report-path", type=Path, default=RUNTIME_REPORT_PATH)
    parser.add_argument("--rollout-report-path", type=Path, default=ROLLOUT_REPORT_PATH)
    parser.add_argument("--chunk-output-dir", type=Path, default=None)
    parser.add_argument("--chunk-manifest-path", type=Path, default=None)
    parser.add_argument("--expected-bridge-row-count", type=int, default=None)
    parser.add_argument("--expected-internal-only-count", type=int, default=None)
    parser.add_argument("--expected-exposed-count", type=int, default=None)
    parser.add_argument("--baseline-lua-sha256", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_runtime_rollout(
        rendered_path=args.rendered_path,
        publish_preview_path=args.publish_preview_path,
        regression_gate_path=args.regression_gate_path,
        staged_lua_output_path=args.staged_lua_output_path,
        lua_output_path=args.lua_output_path,
        bridge_report_path=args.bridge_report_path,
        runtime_report_path=args.runtime_report_path,
        rollout_report_path=args.rollout_report_path,
        chunk_output_dir=args.chunk_output_dir,
        chunk_manifest_path=args.chunk_manifest_path,
        expected_bridge_row_count=args.expected_bridge_row_count,
        expected_internal_only_count=args.expected_internal_only_count,
        expected_exposed_count=args.expected_exposed_count,
        baseline_lua_sha256=args.baseline_lua_sha256,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["overall_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
