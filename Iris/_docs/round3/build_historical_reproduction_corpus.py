#!/usr/bin/env python
"""Capture complete Round 3 route inputs into a deterministic tracked corpus."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
TAXONOMY = REPO / "Iris" / "_docs" / "round3" / "round3_test_taxonomy.json"
OUTPUT_DIR = REPO / "Iris" / "_docs" / "refactor" / "core_refactor"
ARCHIVE = OUTPUT_DIR / "historical_reproduction_corpus.zip"
MANIFEST = OUTPUT_DIR / "historical_reproduction_corpus.json"
TOOLS_BUILD_ROOT = REPO / "Iris" / "build" / "description" / "v2" / "tools" / "build"
SANDBOX_BASELINE = (
    REPO
    / "Iris"
    / "build"
    / "description"
    / "v2"
    / "staging"
    / "dvf_3_3_vnext_cutover_tooling_readiness"
    / "phase3"
    / "sandbox_baseline"
)
MIGRATION_MARKER = re.compile(
    r" DVF_AUTHORITY_ROLE_MIGRATION\[[0-9a-f]{32}\]"
)
HISTORICAL_TOOL_SUPPORT_PATHS: tuple[str, ...] = ()
HISTORICAL_FIXTURE_ROOTS = (
    "Iris/build/description/v2/data",
    "Iris/build/description/v2/output",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion",
    "Iris/build/description/v2/staging/interaction_cluster",
    "Iris/build/description/v2/staging/semantic_quality",
    "Iris/build/description/v2/staging/source_coverage",
    "Iris/build/phase3_output",
    "Iris/input",
    "Iris/media/lua",
    "lua/server",
    "scripts",
)
HISTORICAL_FIXTURE_PATHS = (
    "Iris/build/description/v2/data/compose_profiles.json",
    "Iris/build/description/v2/data/cluster_summary_templates.json",
    "Iris/build/description/v2/data/interaction_cluster_base_facts.jsonl",
    "Iris/build/description/v2/data/interaction_cluster_overlay.jsonl",
    "Iris/build/description/v2/data/interaction_cluster_usecase_rules.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_c1b_reuse_promotion_preview/role_fallback_hollow_c1b_reuse_promotion_preview.summary.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_followup_split.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_net_new_work_packages.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_policy_review/role_fallback_hollow_policy_review_memo.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_policy_review/role_fallback_hollow_policy_outcome_projection.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_policy_review/role_fallback_hollow_policy_resolution_packet.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_policy_review/role_fallback_hollow_policy_review_rows.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_post_block_c_apply_status.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_post_policy_default_closeout_status.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_residual_after_c1b_reuse.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_residual_tail_handoff.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_residual_tail_round_closeout.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_residual_tail_source_discovery_status.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_residual_tail_source_discovery_round.json",
    "Iris/build/description/v2/staging/compose_contract_migration/full_runtime/role_fallback_hollow_terminal_status.json",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/closure_policy_round/closeout/closure_policy_round_closeout_report.json",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/closure_policy_round/closure_policy_round_manifest.json",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/identity_fallback_terminal_handoff.json",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/identity_fallback_terminal_status.json",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/phase3_taxonomy_manifest/phase3_residual_taxonomy_manifest.json",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_remaining_identity_fallback_rows.jsonl",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/phase6_subset_rollout/exec_subset_600_wrench_crowbar_b7_b8_b9/subset_distribution_remeasurement.json",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_closeout_report.json",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/closeout/residual_round_post_closeout_branch_decision.json",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/residual_round_manifest.json",
    "Iris/build/description/v2/staging/identity_fallback_source_expansion/residual_round/scope_lock/residual_round_scope_lock.json",
    "Iris/build/description/v2/staging/source_coverage/block_b/tier_selection.json",
    "Iris/build/description/v2/staging/source_coverage/block_b/uncovered_group_inventory.json",
    "Iris/build/description/v2/staging/source_coverage/block_a/block_a_baseline_summary.json",
    "Iris/build/description/v2/staging/source_coverage/block_a/uncovered_items_with_classification.json",
    "Iris/build/description/v2/staging/source_coverage/block_c/b1_consumable_package/b1_consumable_package_summary.json",
    "Iris/build/description/v2/staging/source_coverage/block_c/b2_literature_package/b2_literature_package_summary.json",
    "Iris/build/description/v2/staging/source_coverage/block_c/c1a_vehicle_package/c1a_vehicle_package_summary.json",
    "Iris/build/description/v2/staging/source_coverage/block_c/c1a_vehicle_package/c1a_vehicle_coverage_report.json",
    "Iris/build/description/v2/staging/source_coverage/block_c/b3_resource_package/b3_resource_package_summary.json",
    "Iris/build/description/v2/staging/source_coverage/block_c/role_fallback_hollow_manual_residual_blocker_memo.json",
    "Iris/build/description/v2/staging/source_coverage/block_c/role_fallback_hollow_source_promotion_manifest.json",
    "Iris/build/description/v2/staging/source_coverage/block_c/role_fallback_hollow_residual_tail_source_discovery_round/c1-f/c1-f_residual_tail_source_discovery_rows.json",
    "Iris/build/description/v2/staging/source_coverage/block_c/role_fallback_hollow_residual_tail_source_discovery_round/c1-g/c1-g_residual_tail_source_discovery_rows.json",
    "Iris/build/description/v2/staging/source_coverage/c1r_scope/c1r_subset_partition.json",
    "Iris/build/description/v2/staging/source_coverage/c1_scope/c1_subset_partition.json",
    "Iris/build/description/v2/staging/source_coverage/post_b/post_b_projection_summary.json",
    "Iris/build/description/v2/staging/interaction_cluster/historical_snapshot/phase_c_pilot/phase_c_policy_excluded.review.jsonl",
    "Iris/input/items_itemscript.json",
    "Iris/build/description/v2/tools/style/rules/structural_rules.json",
    "scripts/camping.txt",
    "scripts/items.txt",
)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_python_payload(path: Path, *, strip_markers: bool = False) -> bytes:
    text = path.read_text(encoding="utf-8")
    if strip_markers:
        text = MIGRATION_MARKER.sub("", text)
    return text.encode("utf-8")


def tracked_paths() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO,
        check=True,
        capture_output=True,
    )
    return {
        value.decode("utf-8").replace("\\", "/")
        for value in result.stdout.split(b"\0")
        if value
    }


def sandbox_source_for(target_relative: str) -> Path:
    encoded = target_relative.replace("/", "__")
    return SANDBOX_BASELINE / encoded


def add_entry(
    entries: dict[str, dict],
    *,
    target_relative: str,
    source: Path,
    entry_kind: str,
    source_kind: str,
    strip_markers: bool = False,
) -> None:
    if target_relative in entries:
        raise ValueError(f"duplicate reproduction corpus target: {target_relative}")
    payload = canonical_python_payload(source, strip_markers=strip_markers)
    entries[target_relative] = {
        "path": target_relative,
        "entry_kind": entry_kind,
        "sha256": sha256(payload),
        "source_kind": source_kind,
        "source_path": source.relative_to(REPO).as_posix(),
        "payload": payload,
    }


def main() -> int:
    tracked = tracked_paths()
    taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    route_test_paths = sorted(
        {
            row["source_file"]
            for row in taxonomy["rows"]
        }
    )

    entries: dict[str, dict] = {}
    for target_relative in route_test_paths:
        live_source = REPO / target_relative
        if live_source.is_file():
            add_entry(
                entries,
                target_relative=target_relative,
                source=live_source,
                entry_kind="route_test",
                source_kind=(
                    "tracked_live_route_test"
                    if target_relative in tracked
                    else "ignored_live_reproduction"
                ),
            )
            continue
        sandbox_source = sandbox_source_for(target_relative)
        if not sandbox_source.is_file():
            raise FileNotFoundError(
                f"route test has no live or sandbox reproduction source: {target_relative}"
            )
        add_entry(
            entries,
            target_relative=target_relative,
            source=sandbox_source,
            entry_kind="route_test",
            source_kind="tracked_sandbox_marker_recovery",
            strip_markers=True,
        )

    for live_source in sorted(TOOLS_BUILD_ROOT.rglob("*.py")):
        target_relative = live_source.relative_to(REPO).as_posix()
        add_entry(
            entries,
            target_relative=target_relative,
            source=live_source,
            entry_kind="build_support",
            source_kind=(
                "tracked_live_build_support"
                if target_relative in tracked
                else "ignored_live_reproduction"
            ),
        )

    for module in (
        "validate_phase_d_signal_preservation.py",
        "validate_structural_reclassification_convergence.py",
    ):
        target_relative = (
            "Iris/build/description/v2/tools/build/" + module
        )
        if target_relative in entries or target_relative in tracked:
            continue
        sandbox_source = sandbox_source_for(target_relative)
        if not sandbox_source.is_file():
            raise FileNotFoundError(
                f"build support has no sandbox reproduction source: {target_relative}"
            )
        add_entry(
            entries,
            target_relative=target_relative,
            source=sandbox_source,
            entry_kind="build_support",
            source_kind="tracked_sandbox_marker_recovery",
            strip_markers=True,
        )

    for target_relative in HISTORICAL_TOOL_SUPPORT_PATHS:
        source = REPO / target_relative
        if not source.is_file():
            raise FileNotFoundError(f"historical tool support missing: {target_relative}")
        add_entry(
            entries,
            target_relative=target_relative,
            source=source,
            entry_kind="tool_support",
            source_kind=(
                "tracked_live_tool_support"
                if target_relative in tracked
                else "ignored_live_reproduction"
            ),
        )

    fixture_paths = set(HISTORICAL_FIXTURE_PATHS)
    for root_relative in HISTORICAL_FIXTURE_ROOTS:
        root = REPO / root_relative
        if not root.is_dir():
            raise FileNotFoundError(f"historical fixture root missing: {root_relative}")
        fixture_paths.update(
            path.relative_to(REPO).as_posix()
            for path in root.rglob("*")
            if path.is_file()
        )

    for target_relative in sorted(fixture_paths):
        source = REPO / target_relative
        if not source.is_file():
            raise FileNotFoundError(f"historical fixture missing: {target_relative}")
        add_entry(
            entries,
            target_relative=target_relative,
            source=source,
            entry_kind="route_fixture",
            source_kind=(
                "tracked_live_fixture"
                if target_relative in tracked
                else "ignored_live_reproduction"
            ),
        )

    ordered_paths = sorted(entries)
    if route_test_paths != [
        path for path in ordered_paths if entries[path]["entry_kind"] == "route_test"
    ]:
        raise ValueError("route test capture denominator mismatch")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "w") as corpus:
        for path in ordered_paths:
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            corpus.writestr(info, entries[path]["payload"])

    manifest_rows = [
        {key: value for key, value in entries[path].items() if key != "payload"}
        for path in ordered_paths
    ]
    manifest = {
        "schema_version": "iris-historical-reproduction-corpus-v1",
        "purpose": "Self-contained ignored historical and diagnostic route reproduction for exact-commit clean checkout validation.",
        "archive_path": ARCHIVE.relative_to(REPO).as_posix(),
        "archive_sha256": sha256(ARCHIVE.read_bytes()),
        "row_count": len(manifest_rows),
        "route_test_count": len(route_test_paths),
        "build_support_count": sum(
            row["entry_kind"] == "build_support" for row in manifest_rows
        ),
        "tool_support_count": len(HISTORICAL_TOOL_SUPPORT_PATHS),
        "route_fixture_count": len(fixture_paths),
        "expected_entry_paths_sha256": sha256(
            "\n".join(ordered_paths).encode("utf-8")
        ),
        "expected_route_test_paths_sha256": sha256(
            "\n".join(route_test_paths).encode("utf-8")
        ),
        "canonicalization": "Python UTF-8 text read with universal newlines and emitted as UTF-8 LF bytes",
        "rows": manifest_rows,
    }
    MANIFEST.write_bytes(
        (json.dumps(manifest, ensure_ascii=True, indent=2) + "\n").encode("utf-8")
    )
    print(
        json.dumps(
            {
                "archive_sha256": manifest["archive_sha256"],
                "row_count": manifest["row_count"],
                "route_test_count": manifest["route_test_count"],
                "build_support_count": manifest["build_support_count"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
