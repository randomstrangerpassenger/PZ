from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
from typing import Any


SCHEMA_VERSION = (
    "dvf-3-3-registry-authority-canonical-closure-"
    "frozen-predecessor-fixture-v1"
)
ROLE = "frozen_predecessor_input"

NORMALIZATION_EXISTENCE_TARGETS = (
    "Iris/build/description/v2/tests/test_post_cleanup_phase2_adoption_validation.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_pkg1_resource4e.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_pkg2_combat_reuse.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_pkg3a_construction_repair_materials.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_pkg3b_vehicle_service_utility.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_pkg3c_camping_and_fire_setup.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_pkg3d_water_and_container_handling.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_pkg3g_household_access_and_safety.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_pkg4_combat_devices_and_firearms.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_pkg5_tool_trap_and_utility_net_new.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_pkg6_residual_tail.py",
    "Iris/build/description/v2/tests/test_post_cleanup_phase3_runtime_integration.py",
    "Iris/build/description/v2/tests/test_source_coverage_hold_policy.py",
    "Iris/build/description/v2/tests/test_source_coverage_post_c.py",
    "Iris/build/description/v2/tools/build/validate_body_plan_full_runtime_regression_gate.py",
    "Iris/build/description/v2/tools/build/validate_phase_d_signal_preservation.py",
    "Iris/build/description/v2/tools/build/validate_structural_reclassification_convergence.py",
)

FIXED_PREDECESSOR_TARGETS = (
    (
        "Iris/build/description/v2/staging/"
        "dvf_3_3_vnext_consumer_migration_input_normalization/phase6/"
        "consumer_migration_reconciled_input_manifest.json"
    ),
    (
        "Iris/build/description/v2/staging/"
        "dvf_3_3_vnext_consumer_migration_input_normalization/phase6/"
        "row_disposition_ledger.for_readiness.jsonl"
    ),
    (
        "Iris/build/description/v2/staging/"
        "dvf_3_3_vnext_current_authority_cutover/phase10/"
        "claim_boundary_report.json"
    ),
    (
        "Iris/build/description/v2/staging/"
        "dvf_3_3_vnext_current_authority_cutover/phase4/"
        "old_new_dual_current_absence_report.json"
    ),
    (
        "Iris/build/description/v2/staging/"
        "dvf_3_3_vnext_execution/phase11/"
        "final_execution_contract_report.json"
    ),
)

ROLLBACK_RUNTIME_ROOT = (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_vnext_current_authority_cutover/phase0/"
    "rollback_snapshot_payload/Iris/media/lua/client/Iris/Data"
)
ROLLBACK_RUNTIME_TARGETS = (
    f"{ROLLBACK_RUNTIME_ROOT}/IrisLayer3DataChunks.lua",
    *(
        f"{ROLLBACK_RUNTIME_ROOT}/IrisLayer3DataChunks/Chunk{index:03d}.lua"
        for index in range(1, 12)
    ),
)
TARGET_PATHS = tuple(
    sorted(
        {
            *NORMALIZATION_EXISTENCE_TARGETS,
            *FIXED_PREDECESSOR_TARGETS,
            *ROLLBACK_RUNTIME_TARGETS,
        }
    )
)

CANDIDATE_SEED_TARGETS = frozenset(
    {
        *FIXED_PREDECESSOR_TARGETS[2:],
        *ROLLBACK_RUNTIME_TARGETS,
    }
)
NORMALIZATION_SOURCE_TARGETS = frozenset(NORMALIZATION_EXISTENCE_TARGETS)
ARCHIVE_ONLY_TARGETS = frozenset(FIXED_PREDECESSOR_TARGETS[:2])


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git_output(source_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=source_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def source_is_ignored_untracked(source_root: Path, target: str) -> bool:
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", target],
        cwd=source_root,
        capture_output=True,
        check=False,
    )
    ignored = subprocess.run(
        ["git", "check-ignore", "--quiet", "--", target],
        cwd=source_root,
        capture_output=True,
        check=False,
    )
    return tracked.returncode != 0 and ignored.returncode == 0


def validate_target(target: str) -> None:
    path = PurePosixPath(target)
    if path.is_absolute() or ".." in path.parts or target != path.as_posix():
        raise ValueError(f"unsafe fixture target path: {target}")


def capture(source_root: Path, output_root: Path) -> dict[str, Any]:
    source_root = source_root.resolve()
    output_root = output_root.resolve()
    if output_root.exists():
        raise FileExistsError(f"fixture output is write-once: {output_root}")
    payload_root = output_root / "payload"
    payload_root.mkdir(parents=True)

    rows: list[dict[str, Any]] = []
    for index, target in enumerate(TARGET_PATHS):
        validate_target(target)
        source = source_root / Path(target)
        if not source.is_file():
            raise FileNotFoundError(f"frozen source missing: {target}")
        if not source_is_ignored_untracked(source_root, target):
            raise ValueError(
                "frozen source must be ignored and untracked predecessor "
                f"evidence: {target}"
            )
        payload = source.read_bytes()
        payload_sha256 = sha256_bytes(payload)
        payload_path = f"payload/{index:04d}.bin"
        destination = output_root / Path(payload_path)
        destination.write_bytes(payload)
        rows.append(
            {
                "target_path": target,
                "payload_path": payload_path,
                "sha256": payload_sha256,
                "byte_length": len(payload),
                "role": ROLE,
                "source_git_state": "ignored_untracked",
                "isolated_candidate_only": True,
                "live_materialization_allowed": False,
            }
        )

    candidate_seed_payload_paths = [
        row["payload_path"]
        for row in rows
        if row["target_path"] in CANDIDATE_SEED_TARGETS
    ]
    normalization_source_payload_paths = [
        row["payload_path"]
        for row in rows
        if row["target_path"] in NORMALIZATION_SOURCE_TARGETS
    ]
    archive_only_payload_paths = [
        row["payload_path"]
        for row in rows
        if row["target_path"] in ARCHIVE_ONLY_TARGETS
    ]
    usage_partition = {
        "archive_only_payload_paths": archive_only_payload_paths,
        "candidate_seed_payload_paths": candidate_seed_payload_paths,
        "normalization_source_payload_paths": (
            normalization_source_payload_paths
        ),
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "status": "PASS",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "source_checkout_commit": git_output(
            source_root, "rev-parse", "HEAD"
        ),
        "role": ROLE,
        "authority_claimed": False,
        "current_route_authority_claimed": False,
        "isolated_candidate_only": True,
        "live_materialization_allowed": False,
        "candidate_discard_required": True,
        **usage_partition,
        "usage_partition_sha256": canonical_hash(usage_partition),
        "file_count": len(rows),
        "total_byte_length": sum(row["byte_length"] for row in rows),
        "rows": rows,
        "rows_sha256": canonical_hash(rows),
    }
    (output_root / "manifest.json").write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--source-root", type=Path, required=True)
    value.add_argument("--output-root", type=Path, required=True)
    return value


def main() -> int:
    args = parser().parse_args()
    manifest = capture(args.source_root, args.output_root)
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "file_count": manifest["file_count"],
                "total_byte_length": manifest["total_byte_length"],
                "rows_sha256": manifest["rows_sha256"],
                "usage_partition_sha256": manifest[
                    "usage_partition_sha256"
                ],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
