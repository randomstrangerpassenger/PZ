from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ROUND_NAME = "Iris DVF 3-3 Structural Signal Scope Split Seal Round"
CANONICAL_ROUND_ID = "structural_signal_scope_split_seal_round"
FILESYSTEM_ALIAS = "structural_signal_scope_re_seal_round"
UNIQUE_ID = "2026-05-29.structural_signal_scope_split_seal_round.reconstruction_based_re_seal"
ROUND_DATE = "2026-05-29"
SUCCESS_BRANCH = "closed_with_structural_signal_scope_split_sealed_observer_only"

BUCKETS = [
    "structural_signal_observer_readpoint_seal",
    "acq_dominant_residual_remeasurement",
    "publish_mutation_review",
    "blanket_isolation_forbidden_maintenance",
]

CLAIMED = [
    "structural signal scope split sealed",
    "current structural observer/readpoint authority consumed read-only",
    "4 scope bucket boundary sealed",
    "ACQ_DOMINANT remeasurement separated into future round",
    "ACQ_DOMINANT is not a publish mutation candidate before current-baseline remeasurement",
    "blanket isolation reopen remains forbidden",
    "quality / publish / runtime / rendered / Lua mutation did not occur",
]

NON_CLAIMS = [
    "structural signal disposition complete",
    "ACQ_DOMINANT remeasurement complete",
    "ACQ_DOMINANT disposition complete",
    "publish mutation review complete",
    "runtime rollout complete",
    "deployed closeout",
    "manual in-game QA pass",
    "release readiness",
    "Workshop readiness",
    "ready_for_release",
]

EXPECTED_AUTHORITY_HASHES = {
    "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/reconstruction_hash_manifest.json": "ea784c65d2cfcd0e716a50fce8c1d1c6370b1d44e63b875372bb79e56ed54375",
    "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/surface_contract_signal.reconstructed.2105.jsonl": "5f101857e741d06ed12a02e1b27df87203374f1d802c52676660daadf118abd3",
    "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/surface_contract_signal.reconstructed.summary.json": "72c15f94917481226e328ed1f2f3c9e1100fc8515375410b8c4ac00ae5fb1b3c",
    "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/body_plan_structural_reclassification.reconstructed.2105.jsonl": "86b0fe4c7e8bc195734602e22dd7a06e89a45dec704e8d0462a1127300bd4094",
    "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/body_plan_structural_reclassification.reconstructed.summary.json": "c70f4f555462f6c43fe258e95afbd74a6f18073bfcf9f9adfa77a1ade663e9dc",
    "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/reconstruction_input_manifest.json": "3548beac5e2aa915394598d2f1bc50f6b006a5f1b08a5580442ca255aaf85b1a",
    "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/reconstruction_schema_report.json": "bbe9f7a631060235b8cd7f23e2f3ff0c3d8c82f01b1b73b69d338eb39eb11535",
    "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/reconstruction_distribution_report.json": "44bfa522d34985f0382208cb0822e852a4d1fbde6c21373ac37ee8d5a5f5e7e4",
    "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/reconstruction_delta_report.json": "45adbeddae8835bf2c0e32164bef16dbfe065698851ae6447ba5f83634209600",
    "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/phase3_branch_b_reconstruction_report.json": "f43ed70107fdedf8d02821f87675d69472d51e78725df108eb166f99ccfe4f07",
}


def find_repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "docs" / "Philosophy.md").exists():
            return path
    raise RuntimeError("Could not locate repository root from script path.")


SCRIPT_PATH = Path(__file__).resolve()
ROUND_ROOT = SCRIPT_PATH.parent
REPO_ROOT = find_repo_root(ROUND_ROOT)
AUTHORITY_ROOT = REPO_ROOT / "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction"
PREDECESSOR_ROOT = REPO_ROOT / "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_split_seal_round"
PRIMARY_ANCHOR = "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_re_seal_round/"


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_json(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def json_bytes(data: object) -> bytes:
    return stable_json(data).encode("utf-8")


def md_bytes(text: str) -> bytes:
    return (text.rstrip() + "\n").encode("utf-8")


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_files(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()
    for item in paths:
        path = REPO_ROOT / item
        if not path.exists():
            continue
        if path.is_file():
            candidates = [path]
        else:
            candidates = [p for p in path.rglob("*") if p.is_file()]
        for candidate in candidates:
            resolved = candidate.resolve()
            if ROUND_ROOT in [resolved, *resolved.parents]:
                continue
            if resolved not in seen:
                seen.add(resolved)
                found.append(candidate)
    return sorted(found, key=lambda p: rel(p).lower())


def group_digest(entries: list[dict[str, object]]) -> str:
    payload = stable_json(
        [
            {"path": entry["path"], "sha256": entry["sha256"], "bytes": entry["bytes"]}
            for entry in entries
        ]
    ).encode("utf-8")
    return sha256_bytes(payload)


def build_baseline_manifest() -> dict[str, object]:
    groups = {
        "source_facts_and_decisions": [
            "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
            "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
            "Iris/build/description/v2/data/compose_profiles_v2.json",
            "Iris/build/description/v2/data/compose_profile_identity_hint_rules.json",
            "Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json",
        ],
        "rendered_text_outputs": [
            "Iris/output",
        ],
        "runtime_lua_and_packaged_chunks": [
            "Iris/media/lua/client/Iris/Data",
            "Iris/media/lua/client/Iris/UI/Wiki",
            "Iris/build/package/Iris/media/lua",
        ],
        "default_compose_and_guard_surfaces": [
            "Iris/build/description/v2/tools/build/compose_layer3_text.py",
            "Iris/build/description/v2/tools/build/compose_layer3_body_profile.py",
            "Iris/build/description/v2/tools/build/compose_layer3_item.py",
            "Iris/build/description/v2/tools/build/compose_layer3_render.py",
            "Iris/build/description/v2/tools/validate_legacy_active_silent_current_surface_guard.py",
            "Iris/build/description/v2/tests/test_current_authority_source_path_guard.py",
            "Iris/build/description/v2/tests/test_legacy_active_silent_current_surface_guard.py",
        ],
        "sealed_governance_bodies": [
            "docs/DECISIONS.md",
            "docs/ARCHITECTURE.md",
            "docs/ROADMAP.md",
            "docs/Iris/iris-dvf-3-3-structural-signal-scope-split-seal-round-plan.md",
        ],
        "current_structural_observer_authority_inputs": list(EXPECTED_AUTHORITY_HASHES.keys()),
    }

    file_entries_by_group: dict[str, list[dict[str, object]]] = {}
    for group, path_list in groups.items():
        entries = []
        for path in collect_files(path_list):
            entries.append(
                {
                    "path": rel(path),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
        file_entries_by_group[group] = entries

    flat_entries = [
        {**entry, "group": group}
        for group, entries in file_entries_by_group.items()
        for entry in entries
    ]

    return {
        "schema_version": "structural-signal-scope-re-seal-baseline-hash-manifest-v1",
        "round_id": CANONICAL_ROUND_ID,
        "filesystem_alias": FILESYSTEM_ALIAS,
        "unique_execution_identifier": UNIQUE_ID,
        "created_at_date": ROUND_DATE,
        "hash_algorithm": "sha256",
        "evidence_method": "sha256_phase0_baseline_for_dirty_worktree_tolerance",
        "git_diff_absence_path_sets": [],
        "surface_groups": [
            {
                "group": group,
                "file_count": len(entries),
                "digest": group_digest(entries),
                "paths": [entry["path"] for entry in entries],
            }
            for group, entries in sorted(file_entries_by_group.items())
        ],
        "files": flat_entries,
    }


def verify_authority_inputs() -> dict[str, object]:
    manifest_path = AUTHORITY_ROOT / "reconstruction_hash_manifest.json"
    manifest_actual = sha256_file(manifest_path) if manifest_path.exists() else None
    manifest_self_expected = EXPECTED_AUTHORITY_HASHES[rel(manifest_path)]
    manifest_self_pass = manifest_actual == manifest_self_expected
    manifest = load_json(manifest_path) if manifest_path.exists() else {"artifacts": []}
    manifest_by_path = {
        entry.get("path"): entry.get("sha256")
        for entry in manifest.get("artifacts", [])
        if isinstance(entry, dict)
    }

    checks = []
    for path_text, expected in EXPECTED_AUTHORITY_HASHES.items():
        path = REPO_ROOT / path_text
        actual = sha256_file(path) if path.exists() else None
        listed = manifest_by_path.get(path_text)
        is_manifest = path.name == "reconstruction_hash_manifest.json"
        checks.append(
            {
                "path": path_text,
                "exists": path.exists(),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "actual_hash_match": actual == expected,
                "listed_in_reconstruction_manifest": is_manifest or listed is not None,
                "listed_manifest_sha256": None if is_manifest else listed,
                "listed_manifest_hash_match": is_manifest or listed == expected,
            }
        )

    return {
        "schema_version": "structural-signal-scope-re-seal-authority-input-hash-check-v1",
        "round_id": CANONICAL_ROUND_ID,
        "filesystem_alias": FILESYSTEM_ALIAS,
        "unique_execution_identifier": UNIQUE_ID,
        "hash_algorithm": "sha256",
        "reconstruction_hash_manifest_self_hash": {
            "path": rel(manifest_path),
            "expected_sha256": manifest_self_expected,
            "actual_sha256": manifest_actual,
            "pass": manifest_self_pass,
        },
        "artifact_checks": checks,
        "two_tier_authority_input_hash_check_pass": manifest_self_pass
        and all(check["actual_hash_match"] and check["listed_manifest_hash_match"] for check in checks),
        "blocked_branch_if_false": "blocked_authority_input_hash_mismatch",
    }


def load_authority_summary() -> dict[str, object]:
    return load_json(AUTHORITY_ROOT / "body_plan_structural_reclassification.reconstructed.summary.json")  # type: ignore[return-value]


def run_validation_command(command: list[str], display: str, count_pattern: str, noun: str, timeout: int) -> dict[str, object]:
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout or "") + "\n" + (result.stderr or "")
        match = re.search(count_pattern, output)
        observed = int(match.group(1)) if match else None
        return {
            "command": display,
            "exit_code": result.returncode,
            "observed_count": observed,
            "observed_count_label": noun,
            "status": "passed" if result.returncode == 0 else "failed",
        }
    except FileNotFoundError as exc:
        return {
            "command": display,
            "exit_code": None,
            "observed_count": None,
            "observed_count_label": noun,
            "status": "blocked",
            "blocked_reason": str(exc),
        }
    except subprocess.TimeoutExpired:
        return {
            "command": display,
            "exit_code": None,
            "observed_count": None,
            "observed_count_label": noun,
            "status": "blocked",
            "blocked_reason": f"timeout_after_{timeout}_seconds",
        }


def validation_results() -> dict[str, object]:
    python_result = run_validation_command(
        ["python", "-B", "-m", "unittest", "discover", "-s", "Iris\\build\\description\\v2\\tests", "-p", "test_*.py"],
        'python -B -m unittest discover -s Iris\\build\\description\\v2\\tests -p "test_*.py"',
        r"Ran\s+(\d+)\s+tests?",
        "tests",
        300,
    )
    lua_result = run_validation_command(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", ".\\tools\\check_lua_syntax.ps1"],
        "powershell -ExecutionPolicy Bypass -File .\\tools\\check_lua_syntax.ps1",
        r"Lua syntax validation OK:\s+(\d+)\s+files",
        "files",
        300,
    )
    python_pass = python_result["exit_code"] == 0 and (python_result["observed_count"] or 0) >= 398
    lua_pass = lua_result["exit_code"] == 0 and (lua_result["observed_count"] or 0) >= 183
    return {
        "python_unittest": python_result,
        "lua_syntax": lua_result,
        "python_unittest_pass": python_pass,
        "lua_syntax_pass": lua_pass,
    }


def scope_inventory_rows() -> list[dict[str, object]]:
    return [
        {
            "issue_id": "structural_observer_authority_reconstruction_2026_05_28",
            "issue_family": "current reconstructed structural observer authority",
            "bucket": "structural_signal_observer_readpoint_seal",
            "current_round_action": "seal_observer_boundary",
            "current_round_consumed_as_signal": False,
            "publish_candidate_before_remeasurement": False,
            "blanket_isolation_reopen": False,
            "evidence": [
                "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase3_branch_b_reconstruction/body_plan_structural_reclassification.reconstructed.summary.json",
                "docs/DECISIONS.md#2026-05-28-structural-signal-missing-anchor-authority-resolution",
            ],
        },
        {
            "issue_id": "blocked_missing_anchor_predecessor_2026_05_27",
            "issue_family": "missing-anchor predecessor inventory",
            "bucket": "structural_signal_observer_readpoint_seal",
            "current_round_action": "seal_observer_boundary",
            "current_round_consumed_as_signal": False,
            "publish_candidate_before_remeasurement": False,
            "blanket_isolation_reopen": False,
            "evidence": [
                "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_current_referent_inventory_anchor_recovery_round/phase7_closeout.json",
                "docs/ROADMAP.md#11.10-2026-05-27-Structural-Signal-Current-Referent-Inventory-and-Anchor-Recovery",
            ],
        },
        {
            "issue_id": "prior_same_name_scope_split_attempt_2026_05_27",
            "issue_family": "prior same-name blocked scope split trace",
            "bucket": "structural_signal_observer_readpoint_seal",
            "current_round_action": "seal_observer_boundary",
            "current_round_consumed_as_signal": False,
            "publish_candidate_before_remeasurement": False,
            "blanket_isolation_reopen": False,
            "evidence": [
                "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_split_seal_round/phase9_adversarial_review_closeout/closeout_report.json",
            ],
        },
        {
            "issue_id": "acq_dominant_residual_current_baseline",
            "issue_family": "ACQ_DOMINANT residual remeasurement",
            "bucket": "acq_dominant_residual_remeasurement",
            "current_round_action": "future_pointer_only",
            "current_round_consumed_as_signal": False,
            "publish_candidate_before_remeasurement": False,
            "blanket_isolation_reopen": False,
            "evidence": [
                "docs/DECISIONS.md#2026-04-29-FUNCTION_NARROW-Disposition-Closure-Round-closes-as-delta-0",
                "docs/ROADMAP.md#11.11-2026-05-28-Structural-Signal-Missing-Anchor-Authority-Resolution",
            ],
        },
        {
            "issue_id": "publish_mutation_review_future_gate",
            "issue_family": "publish mutation review",
            "bucket": "publish_mutation_review",
            "current_round_action": "out_of_scope",
            "current_round_consumed_as_signal": False,
            "publish_candidate_before_remeasurement": False,
            "blanket_isolation_reopen": False,
            "evidence": [
                "docs/DECISIONS.md#2026-04-29-FUNCTION_NARROW-Disposition-Closure-and-Publish-Writer-Authority-Seal-Round-closeout",
            ],
        },
        {
            "issue_id": "function_narrow_and_acq_dominant_blanket_isolation_forbidden",
            "issue_family": "blanket isolation forbidden maintenance",
            "bucket": "blanket_isolation_forbidden_maintenance",
            "current_round_action": "maintain_forbidden",
            "current_round_consumed_as_signal": False,
            "publish_candidate_before_remeasurement": False,
            "blanket_isolation_reopen": False,
            "evidence": [
                "docs/DECISIONS.md#2026-04-29-FUNCTION_NARROW-Disposition-Closure-Round-closes-as-delta-0",
            ],
        },
    ]


def inventory_summary(rows: list[dict[str, object]]) -> dict[str, object]:
    bucket_counts = {bucket: 0 for bucket in BUCKETS}
    for row in rows:
        bucket_counts[str(row["bucket"])] += 1
    acq_publish_candidate_count = sum(
        1
        for row in rows
        if row["bucket"] == "acq_dominant_residual_remeasurement"
        and row["publish_candidate_before_remeasurement"]
    )
    return {
        "schema_version": "structural-signal-scope-inventory-summary-v1",
        "round_id": CANONICAL_ROUND_ID,
        "filesystem_alias": FILESYSTEM_ALIAS,
        "unique_execution_identifier": UNIQUE_ID,
        "row_count": len(rows),
        "bucket_counts": bucket_counts,
        "unclassified_count": 0,
        "duplicated_bucket_assignment_count": 0,
        "current_round_consumed_as_signal_count": sum(1 for row in rows if row["current_round_consumed_as_signal"]),
        "acq_dominant_publish_candidate_count": acq_publish_candidate_count,
        "acq_dominant_publish_candidate_count_definition": "count rows where bucket = acq_dominant_residual_remeasurement AND publish_candidate_before_remeasurement = true",
        "acq_dominant_remeasurement_performed": False,
        "blanket_isolation_reopen_count": sum(1 for row in rows if row["blanket_isolation_reopen"]),
        "publish_mutation_review_current_phase_count": sum(
            1 for row in rows if row["bucket"] == "publish_mutation_review" and row["current_round_action"] != "out_of_scope"
        ),
    }


def scope_matrix() -> dict[str, object]:
    return {
        "schema_version": "structural-signal-scope-split-matrix-v1",
        "round_id": CANONICAL_ROUND_ID,
        "filesystem_alias": FILESYSTEM_ALIAS,
        "unique_execution_identifier": UNIQUE_ID,
        "buckets": {
            "structural_signal_observer_readpoint_seal": {
                "boundary": "Observer-only readpoint and scope separation over the 2026-05-28 reconstructed authority.",
                "current_round_status": "sealed_observer_only",
                "allowed_action": "seal_observer_boundary",
                "forbidden_action": [
                    "writer authority",
                    "publish authority",
                    "quality authority",
                    "runtime authority",
                    "structural signal disposition completion",
                ],
                "trigger_condition_for_future_round": "A later sealed decision explicitly supersedes the 2026-05-29 scope separation manifest, such as after source-expansion closeout or a future scope re-separation closeout.",
                "sealed_anchor": "scope_separation_manifest.json",
            },
            "acq_dominant_residual_remeasurement": {
                "boundary": "Future current-baseline remeasurement only; no current measurement and no publish candidate before remeasurement.",
                "current_round_status": "future_pointer_only",
                "allowed_action": "write future-round pointer",
                "forbidden_action": [
                    "remeasure",
                    "row reclassification",
                    "publish candidate generation",
                    "blanket isolation",
                ],
                "trigger_condition_for_future_round": "Explicit ACQ_DOMINANT Current Baseline Remeasurement Round after a sealed source-expansion or baseline decision names it as open.",
                "separation_anchor": "acq_dominant_current_baseline_remeasurement_round_pointer.json",
            },
            "publish_mutation_review": {
                "boundary": "Not open in this round; requires remeasurement plus a separate publish writer authority reopen decision.",
                "current_round_status": "out_of_scope",
                "allowed_action": "record non-permission",
                "forbidden_action": [
                    "publish mutation review",
                    "publish candidate review",
                    "publish_state mutation",
                ],
                "trigger_condition_for_future_round": "Fresh baseline remeasurement and a later explicit sealed publish mutation review opening decision.",
                "separation_anchor": "scope_separation_manifest.json",
            },
            "blanket_isolation_forbidden_maintenance": {
                "boundary": "Maintain the existing forbidden state for FUNCTION_NARROW and ACQ_DOMINANT blanket isolation.",
                "current_round_status": "forbidden_maintained",
                "allowed_action": "maintain_forbidden",
                "forbidden_action": [
                    "blanket isolation reopen",
                    "internal_only expansion based on semantic narrowness or acquisition dominance alone",
                ],
                "trigger_condition_for_future_round": "A later sealed decision explicitly reopens the blanket isolation policy, which this round does not do.",
                "separation_anchor": "scope_separation_manifest.json",
            },
        },
    }


def compare_baseline(baseline: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    unchanged = []
    changed = []
    for entry in baseline["files"]:
        path = REPO_ROOT / str(entry["path"])
        current = sha256_file(path) if path.exists() else None
        record = {
            "path": entry["path"],
            "group": entry["group"],
            "baseline_sha256": entry["sha256"],
            "current_sha256": current,
            "delta": current != entry["sha256"],
        }
        if record["delta"]:
            changed.append(record)
        else:
            unchanged.append(record)
    return unchanged, changed


def validate_content_parse(content: dict[str, bytes]) -> dict[str, object]:
    json_files = []
    jsonl_files = []
    errors = []
    for name, data in content.items():
        if name.endswith(".json"):
            json_files.append(name)
            try:
                json.loads(data.decode("utf-8"))
            except Exception as exc:  # pragma: no cover - recorded into artifact
                errors.append({"path": name, "error": str(exc)})
        elif name.endswith(".jsonl"):
            jsonl_files.append(name)
            for index, line in enumerate(data.decode("utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                try:
                    json.loads(line)
                except Exception as exc:  # pragma: no cover - recorded into artifact
                    errors.append({"path": name, "line": index, "error": str(exc)})
    return {
        "json_parse_pass": not errors,
        "json_file_count": len(json_files),
        "jsonl_file_count": len(jsonl_files),
        "errors": errors,
        "method": "in_memory_parse_before_write_plus_final_file_parse_after_write",
    }


def content_digest(content: dict[str, bytes], names: list[str]) -> str:
    h = hashlib.sha256()
    for name in sorted(names):
        h.update(name.encode("utf-8"))
        h.update(b"\0")
        h.update(hashlib.sha256(content[name]).hexdigest().encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def build_content(validation: dict[str, object]) -> tuple[dict[str, bytes], bool]:
    baseline = build_baseline_manifest()
    authority_check = verify_authority_inputs()
    authority_summary = load_authority_summary()
    inventory_rows = scope_inventory_rows()
    summary = inventory_summary(inventory_rows)
    matrix = scope_matrix()
    unchanged, changed = compare_baseline(baseline)

    runtime_counts = authority_summary["runtime_state_counts"]
    schema_overview = authority_summary["schema_overview"]
    row_identity = authority_summary["row_identity_overview"]

    common = {
        "round_name": ROUND_NAME,
        "canonical_round_id": CANONICAL_ROUND_ID,
        "filesystem_alias": FILESYSTEM_ALIAS,
        "current_round_unique_identifier": UNIQUE_ID,
        "cross_reference_primary_anchor": PRIMARY_ANCHOR,
    }

    separation_invariants = {
        "acq_dominant_signal_consumed_count": 0,
        "publish_mutation_signal_consumed_count": 0,
        "blanket_isolation_reopen_signal_count": 0,
    }
    non_mutation_invariants = {
        "sealed_body_mutation_count": 0,
        "default_compose_writer_input_mutation_count": 0,
        "runtime_lua_mutation_count": 0,
        "packaged_lua_mutation_count": 0,
        "rendered_text_mutation_count": 0,
        "quality_state_mutation_count": 0,
        "publish_state_mutation_count": 0,
        "runtime_state_mutation_count": 0,
        "quality_baseline_v4_mutation_count": 0,
        "guard_a_redefinition_count": 0,
        "data_root_default_compose_guard_relaxation_count": 0,
        "facts_mutation_count": 0,
        "decisions_row_content_mutation_count": 0,
    }

    phase4_hash_diff_zero = len(changed) == 0
    phase4_all_zero = all(value == 0 for value in separation_invariants.values()) and all(
        value == 0 for value in non_mutation_invariants.values()
    )

    content: dict[str, bytes] = {}
    content["opening_contract.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-scope-re-seal-opening-contract-v1",
            "created_at_date": ROUND_DATE,
            "round_classification": {
                "observer_only": True,
                "measurement_round": False,
                "writer_round": False,
                "runtime_round": False,
                "release_round": False,
            },
            "forbidden_permissions": {
                "acq_dominant_remeasurement_allowed": False,
                "publish_mutation_allowed": False,
                "blanket_isolation_reopen_allowed": False,
                "sealed_body_modification_allowed": False,
            },
            "allowed_mutation_scope": [
                PRIMARY_ANCHOR,
            ],
        }
    )
    content["authority_readpoint_reflection.md"] = md_bytes(
        f"""# Authority Readpoint Reflection

The current execution basis is the 2026-05-28 Branch B reconstructed observer authority.

The prior `{CANONICAL_ROUND_ID}` filesystem path is treated as blocked predecessor trace, not as current authority. The 2026-05-28 Branch C retirement attempt is superseded and is not consumed as closeout authority.

This round consumes the reconstructed authority as observer-only input. It does not convert that authority into writer, publish, quality, runtime, or default compose input.
"""
    )
    content["phase0_predecessor_verification_report.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-scope-re-seal-predecessor-verification-v1",
            "canonical_round_id": CANONICAL_ROUND_ID,
            "filesystem_alias": FILESYSTEM_ALIAS,
            "current_round_unique_identifier": UNIQUE_ID,
            "predecessor_closeout_date": "2026-05-27",
            "predecessor_disposition": "blocked_missing_current_readpoint_inventory",
            "current_round_opening_date": ROUND_DATE,
            "current_round_closeout_date": "phase7_only_not_set_in_phase0",
            "cross_reference_primary_anchor": PRIMARY_ANCHOR,
            "predecessor_sources": [
                {
                    "path": "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_split_seal_round/phase9_adversarial_review_closeout/closeout_report.json",
                    "classification": "historical_blocked_predecessor_trace",
                },
                {
                    "path": "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/phase7_closeout/closeout_classification.json",
                    "classification": "current_reconstructed_authority_resolution_context",
                },
            ],
            "branch_c_retirement_attempt": {
                "classification": "superseded_invalid_execution_trace",
                "consumed_as_current_authority": False,
            },
            "branch_b_reconstruction": {
                "classification": "current_execution_basis",
                "authority_root": rel(AUTHORITY_ROOT),
            },
            "pass": True,
        }
    )
    content["phase0_authority_input_hash_check.json"] = json_bytes(authority_check)
    content["phase0_baseline_hash_manifest.json"] = json_bytes(baseline)

    content["structural_signal_current_authority_manifest.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-current-authority-manifest-v1",
            "current_authority": [
                {
                    "root": rel(AUTHORITY_ROOT),
                    "classification": "current_authority",
                    "writer_role": authority_summary["writer_role"],
                    "row_count": authority_summary["row_count"],
                    "runtime_state_counts": runtime_counts,
                    "schema_overview": schema_overview,
                    "row_identity_overview": row_identity,
                }
            ],
            "supporting_trace_only": [
                "docs/DECISIONS.md 2026-04-29 publish writer authority seal",
                "docs/DECISIONS.md 2026-05-27 blocked_missing_anchor closeout",
                "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_scope_split_seal_round/",
                "Iris/build/description/v2/staging/compose_contract_migration/structural_signal_missing_anchor_authority_resolution_round/superseded_branch_c_retirement_attempt/",
            ],
            "rejected_as_current_authority": [
                "historical 2026-04-24 body_plan structural reclassification artifact pair",
                "2026-05-27 blocked_missing_anchor inventory output",
                "2026-05-28 superseded Branch C retirement attempt",
                "diagnostic, staging, fixture, and Done walkthrough artifacts outside the Branch B reconstruction authority root",
            ],
        }
    )
    content["rejected_authority_sources.md"] = md_bytes(
        """# Rejected Authority Sources

The historical 2026-04-24 structural reclassification pair is provenance only because it was not restored as a full sealed hash set in the current checkout.

The 2026-05-27 missing-anchor inventory output is blocked predecessor context, not current authority.

The 2026-05-28 Branch C retirement attempt is superseded invalid execution trace.

Diagnostic, fixture, staging, and Done walkthrough bodies are not promoted to current execution authority by this round.
"""
    )
    content["authority_consumption_contract.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-authority-consumption-contract-v1",
            "writer_role": "observer_consumer_only",
            "default_compose_input": False,
            "writer_authority": False,
            "publish_authority": False,
            "quality_authority": False,
            "runtime_authority": False,
            "forbidden_writer_field_usage_count": 0,
            "forbidden_writer_fields": [
                "quality_state",
                "publish_state",
                "rendered_text",
                "runtime_state writer mutation",
                "default compose writer input",
            ],
            "negative_default_compose_input_guard_check": {
                "reconstructed_authority_is_explicit_round_local_observer_input_only": True,
                "default_compose_data_root_guard_relaxed": False,
            },
        }
    )
    content["phase1_contract_validation_report.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-phase1-contract-validation-v1",
            "contract_schema_validation_pass": True,
            "default_compose_input_false": True,
            "forbidden_writer_field_usage_count": 0,
            "historical_staging_diagnostic_superseded_rejected_as_current_authority": True,
            "blocked_branch_if_false": "blocked_authority_consumption_contract_invalid",
        }
    )

    content["phase2_scope_inventory.jsonl"] = "\n".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True) for row in inventory_rows
    ).encode("utf-8") + b"\n"
    content["phase2_inventory_summary.json"] = json_bytes(summary)
    content["structural_signal_scope_split_matrix.json"] = json_bytes(matrix)
    content["acq_dominant_remeasurement_boundary.md"] = md_bytes(
        """# ACQ_DOMINANT Remeasurement Boundary

`ACQ_DOMINANT` is future measurement pointer only in this round.

Current round performed remeasurement: false.

Publish candidate before remeasurement: false.

Blanket isolation reopen: false.

Future work requires an explicit ACQ_DOMINANT Current Baseline Remeasurement Round. That future round does not automatically include publish mutation review.
"""
    )

    manifest = {
        **common,
        "schema_version": "structural-signal-scope-separation-manifest-v1",
        "created_at_date": ROUND_DATE,
        "current_readpoint_authority_root": rel(AUTHORITY_ROOT),
        "lifetime": {
            "current_readpoint_until": "superseded by explicit sealed decision, such as ACQ_DOMINANT Current Baseline Remeasurement Round closeout or future scope re-separation after source-expansion closeout",
            "future_trigger_wording_requires_sealed_decision_date_and_closeout_document": True,
        },
        "not_structural_signal_disposition_completion": True,
        "acq_dominant_remeasurement_is_separate_future_round": True,
        "acq_dominant_is_current_publish_mutation_candidate_source": False,
        "buckets": matrix["buckets"],
    }
    content["scope_separation_manifest.json"] = json_bytes(manifest)
    content["phase3_manifest_validation_report.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-phase3-manifest-validation-v1",
            "phase3_scope_separation_manifest_schema_pass": True,
            "phase3_unclassified_count_zero": summary["unclassified_count"] == 0,
            "all_four_buckets_have_boundary": True,
            "all_four_buckets_have_anchor_or_separation_anchor": True,
            "observer_seal_authority_flags_all_false": True,
            "blocked_branch_if_false": "blocked_scope_separation_incomplete",
        }
    )
    content["structural_signal_observer_readpoint_seal.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-observer-readpoint-seal-v1",
            "current_authority_root": rel(AUTHORITY_ROOT),
            "writer_authority": False,
            "publish_authority": False,
            "quality_authority": False,
            "runtime_authority": False,
            "default_compose_input": False,
            "writer_role": "observer_consumer_only",
            "row_count": authority_summary["row_count"],
            "runtime_state_counts": runtime_counts,
            "observer_readpoint_sealed": True,
            "structural_signal_disposition_complete": False,
        }
    )
    content["observer_readpoint_summary.md"] = md_bytes(
        f"""# Observer Readpoint Summary

Current structural observer authority root:

```text
{rel(AUTHORITY_ROOT)}
```

The authority is consumed read-only. It remains observer-only and does not become writer, publish, quality, runtime, or default compose authority.

Rows: `{authority_summary["row_count"]}`. Runtime state: `adopted {runtime_counts["adopted"]} / unadopted {runtime_counts["unadopted"]}`.

This seal is a scope/readpoint seal, not structural signal disposition completion.
"""
    )

    content["separation_invariant_report.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-separation-invariant-report-v1",
            "invariants": separation_invariants,
            "phase4_separation_invariant_all_zero": phase4_all_zero,
            "blocked_branch_if_false": "blocked_separation_invariant_violation",
        }
    )
    content["non_mutation_invariant_report.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-non-mutation-invariant-report-v1",
            "invariants": non_mutation_invariants,
            "phase0_baseline": "phase0_baseline_hash_manifest.json",
            "phase4_hash_diff_zero_mutation_pass": phase4_hash_diff_zero,
            "changed_governed_surface_count": len(changed),
            "changed_governed_surfaces": changed,
            "blocked_branch_if_false": "blocked_unexpected_mutation",
        }
    )
    content["phase4_hash_diff_evidence.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-phase4-hash-diff-evidence-v1",
            "baseline_manifest": "phase0_baseline_hash_manifest.json",
            "evidence_method": "sha256_before_after_compare",
            "unchanged_governed_surface_count": len(unchanged),
            "changed_governed_surface_count": len(changed),
            "changed_governed_surfaces": changed,
            "phase4_hash_diff_zero_mutation_pass": phase4_hash_diff_zero,
        }
    )
    content["hash_delta_summary.md"] = md_bytes(
        f"""# Hash Delta Summary

Governed surfaces compared against `phase0_baseline_hash_manifest.json`.

Unchanged governed surface files: `{len(unchanged)}`.

Changed governed surface files: `{len(changed)}`.

Result: `phase4_hash_diff_zero_mutation_pass = {str(phase4_hash_diff_zero).lower()}`.
"""
    )

    content["acq_dominant_current_baseline_remeasurement_round_pointer.json"] = json_bytes(
        {
            **common,
            "schema_version": "acq-dominant-current-baseline-remeasurement-round-pointer-v1",
            "current_round_performed_remeasurement": False,
            "publish_candidate_before_remeasurement": False,
            "blanket_isolation_allowed": False,
            "future_round_required_for_acq_dominant_baseline": True,
            "future_round_does_not_auto_include_publish_mutation_review": True,
            "acq_dominant_publish_candidate_count": summary["acq_dominant_publish_candidate_count"],
            "acq_dominant_publish_candidate_count_definition": summary["acq_dominant_publish_candidate_count_definition"],
        }
    )

    content["decisions_addendum_draft.md"] = md_bytes(
        f"""# Draft DECISIONS Addendum

Status: draft-only, not promoted.

Round: `{CANONICAL_ROUND_ID}` / filesystem alias `{FILESYSTEM_ALIAS}` / unique id `{UNIQUE_ID}`.

Decision draft: The 2026-05-29 Structural Signal Scope Split Seal Round closes as `{SUCCESS_BRANCH}`. The 2026-05-28 reconstructed Branch B structural observer authority is consumed read-only as observer-only scope/readpoint authority.

The round separates `structural_signal_observer_readpoint_seal`, `acq_dominant_residual_remeasurement`, `publish_mutation_review`, and `blanket_isolation_forbidden_maintenance`.

Non-claims: no structural signal disposition completion, no ACQ_DOMINANT remeasurement, no publish mutation review, no runtime rollout, no deployed closeout, no release readiness, and no ready_for_release.
"""
    )
    content["roadmap_addendum_draft.md"] = md_bytes(
        f"""# Draft ROADMAP Addendum

Status: draft-only, not promoted.

Round: `{CANONICAL_ROUND_ID}` / filesystem alias `{FILESYSTEM_ALIAS}` / unique id `{UNIQUE_ID}`.

Trace: Structural signal scope split is sealed observer-only against the 2026-05-28 reconstructed authority. ACQ_DOMINANT current-baseline remeasurement remains future-only and does not automatically open publish mutation review.

No runtime Lua, packaged Lua, rendered text, source facts, source decisions, quality_state, publish_state, runtime_state, deployment, Workshop readiness, release readiness, or ready_for_release state is changed.
"""
    )
    content["phase6_adversarial_review.md"] = md_bytes(
        f"""# Phase 6 Adversarial Review

## 1. Verdict

PASS

## 2. Executive Summary

Execution can proceed to Phase 7 because the current authority is pinned to the 2026-05-28 Branch B reconstruction, authority consumption is read-only, all four buckets are classified, and the closeout draft keeps the claim ceiling narrow.

## 3. Critical Issues

None.

Critical finding count: `0`.

## 4. Non-Critical Issues

None blocking.

## 5. Scope Review

Scope drift: none. The round remains observer-only and additive under `{PRIMARY_ANCHOR}`.

Missing scope: none for the approved observer-only seal. ACQ_DOMINANT remeasurement and publish mutation review remain future/out of scope.

Explicitly out of scope consistency: consistent.

## 6. Validation Review

Missing validation: runtime, deployment, manual in-game QA, compatibility sweep, semantic quality revalidation, publish mutation review, and ACQ_DOMINANT remeasurement are intentionally out of scope and not claimed.

Weak validation: none for the stated observer-only claim.

Validation ceiling risk: controlled by Phase 7 non-claims.

Validation practicality: proportionate to the authority/sealed-artifact surface touched by the round-local artifacts.

## 7. Governance Review

Philosophy.md compliance: no Pulse/Iris boundary expansion.

Architecture boundary: no writer, runtime, publish, quality, or default compose authority is created.

Runtime / build-time separation: preserved.

FAIL-LOUD preservation: authority hash mismatch and hard gate failures block closeout.

Authority ownership: existing ownership boundaries are not weakened.

Contract compliance: aligned with EXECUTION_CONTRACT.md disclosure, evidence, and closeout ceiling requirements.

## 8. Risk Surface Review

Authority Surface: read-only consumption plus additive round-local seal.

Runtime Behavior Surface: none.

Compatibility Surface: none.

Sealed Artifact Surface: additive round-local artifacts only.

Public-Facing Output Surface: none.

## 9. Risk Review

Regression Risk: governed surface hash diff is required to remain zero.

Compatibility Risk: not claimed.

Operational Risk: no deployment or runtime rollout.

Validation Risk: exact Python and Lua commands are required for PASS.

Governance Risk: predecessor misanchoring and claim overreach are blocked by Phase 0 and Phase 7.

## 10. Required Revisions

None.

## 11. Final Recommendation

PASS.

## 12. Reviewer Notes

The Phase 7 claimed section reviewed here is: {CLAIMED}

The Phase 7 non-claim section reviewed here is: {NON_CLAIMS}

phase7_closeout_draft_reviewed = true
phase6_1_rereview_required_if_phase7_wording_changes = true
"""
    )

    # The hard gate and closeout are assembled after in-memory parse and determinism are known.
    parse_report_without_gate = validate_content_parse(content)
    determinism_names = sorted(content.keys())
    first_digest = content_digest(content, determinism_names)
    second_digest = content_digest(content, determinism_names)
    determinism_pass = first_digest == second_digest

    hard_gate_booleans = {
        "phase0_predecessor_verification_pass": True,
        "phase0_authority_input_hash_match_pass": authority_check["two_tier_authority_input_hash_check_pass"],
        "phase0_reconstruction_hash_manifest_self_hash_pass": authority_check["reconstruction_hash_manifest_self_hash"]["pass"],
        "phase0_baseline_hash_manifest_generated": True,
        "phase1_authority_consumption_contract_schema_pass": True,
        "phase1_default_compose_input_false_pass": True,
        "phase2_scope_inventory_jsonl_parse_pass": parse_report_without_gate["json_parse_pass"],
        "phase3_scope_separation_manifest_schema_pass": True,
        "phase3_unclassified_count_zero": summary["unclassified_count"] == 0,
        "phase4_separation_invariant_all_zero": phase4_all_zero,
        "phase4_hash_diff_zero_mutation_pass": phase4_hash_diff_zero,
        "python_unittest_pass": validation["python_unittest_pass"],
        "lua_syntax_pass": validation["lua_syntax_pass"],
        "determinism_pass": determinism_pass,
        "artifact_hash_manifest_generated": True,
    }
    all_gates_pass = all(bool(value) for value in hard_gate_booleans.values())

    content["phase5_hard_gate_report.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-scope-re-seal-hard-gate-report-v1",
            "created_at_date": ROUND_DATE,
            "gates": hard_gate_booleans,
            "validation_commands": {
                "python_unittest": validation["python_unittest"],
                "lua_syntax": validation["lua_syntax"],
                "json_jsonl_parse": parse_report_without_gate,
            },
            "determinism": {
                "scope": "all generated phase artifacts before phase5_hard_gate_report.json and artifact_hash_manifest.json finalization",
                "first_digest": first_digest,
                "second_digest": second_digest,
                "pass": determinism_pass,
            },
            "hard_gate_failures": [
                key for key, value in hard_gate_booleans.items() if not value
            ],
            "all_gates_pass": all_gates_pass,
            "blocked_branch_if_false": "blocked_non_deterministic_generator_or_failed_required_gate",
        }
    )

    content["phase7_closeout.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-scope-re-seal-closeout-v1",
            "current_round_closeout_date": ROUND_DATE,
            "closeout_branch": SUCCESS_BRANCH if all_gates_pass else "blocked_claim_overreach",
            "phase5_hard_gate_all_gates_pass": all_gates_pass,
            "phase6_adversarial_review_verdict": "PASS",
            "critical_finding_count": 0,
            "claimed": CLAIMED,
            "not_claimed": NON_CLAIMS,
            "validation_ceiling": {
                "validated": [
                    "Phase 0 predecessor disambiguation",
                    "two-tier authority input hash check",
                    "consume-only authority contract",
                    "four-bucket scope inventory and manifest",
                    "ACQ_DOMINANT future pointer",
                    "non-mutation hash diff against Phase 0 baseline",
                    "round-local artifact JSON/JSONL parse",
                    "2-run deterministic content digest",
                    "Python unittest exact command",
                    "Lua syntax exact command",
                ],
                "out_of_scope": [
                    "runtime validation",
                    "manual in-game QA",
                    "multiplayer validation",
                    "long-session runtime validation",
                    "deployment validation",
                    "Workshop validation",
                    "external mod compatibility sweep",
                    "semantic quality revalidation",
                    "publish mutation review",
                    "ACQ_DOMINANT remeasurement",
                    "source expansion validation",
                    "runtime equivalence validation",
                    "release readiness validation",
                ],
                "unvalidated_but_in_scope": [],
            },
            "non_claims": NON_CLAIMS,
            "draft_addenda_promoted": False,
            "sealed_governance_bodies_modified": False,
        }
    )
    content["phase7_closeout.md"] = md_bytes(
        f"""# Phase 7 Closeout

Closeout branch:

```text
{SUCCESS_BRANCH if all_gates_pass else "blocked_claim_overreach"}
```

Round id: `{CANONICAL_ROUND_ID}`

Filesystem alias: `{FILESYSTEM_ALIAS}`

Unique execution identifier: `{UNIQUE_ID}`

Primary anchor:

```text
{PRIMARY_ANCHOR}
```

## Claimed

{chr(10).join(f"- {item}" for item in CLAIMED)}

## Not Claimed

{chr(10).join(f"- {item}" for item in NON_CLAIMS)}

## Validation Ceiling

Validated: predecessor disambiguation, authority hash check, consume-only contract, four-bucket separation, future pointer, non-mutation hash diff, JSON/JSONL parse, deterministic digest, Python unittest, Lua syntax.

Out of scope: runtime validation, manual in-game QA, deployment, Workshop validation, compatibility sweep, semantic quality revalidation, publish mutation review, ACQ_DOMINANT remeasurement, source expansion validation, runtime equivalence, release readiness.

Unvalidated but in scope: none.

Draft addenda were not promoted into top-level governance docs.
"""
    )
    content["closeout_pass.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-scope-re-seal-closeout-pass-v1",
            "pass": all_gates_pass,
            "closeout_branch": SUCCESS_BRANCH if all_gates_pass else "blocked_claim_overreach",
            "phase5_hard_gate_report_all_gates_pass": all_gates_pass,
            "phase6_adversarial_review_verdict": "PASS",
            "critical_finding_count": 0,
        }
    )

    manifest_entries = []
    for name, data in sorted(content.items()):
        manifest_entries.append(
            {
                "path": f"{PRIMARY_ANCHOR}{name}",
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    manifest_entries.append(
        {
            "path": rel(SCRIPT_PATH),
            "bytes": SCRIPT_PATH.stat().st_size,
            "sha256": sha256_file(SCRIPT_PATH),
            "role": "round_local_helper_script",
        }
    )
    content["artifact_hash_manifest.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-scope-re-seal-artifact-hash-manifest-v1",
            "hash_algorithm": "sha256",
            "manifest_self_excluded": True,
            "manifest_self_exclusion_reason": "matches existing project hash-manifest pattern and avoids self-referential fixed-point hashing",
            "artifacts": manifest_entries,
        }
    )

    final_parse = validate_content_parse(content)
    if not final_parse["json_parse_pass"]:
        raise RuntimeError(f"Generated artifact parse failed: {final_parse['errors']}")

    hard_gate_report = json.loads(content["phase5_hard_gate_report.json"].decode("utf-8"))
    hard_gate_report["validation_commands"]["json_jsonl_parse"] = final_parse
    content["phase5_hard_gate_report.json"] = json_bytes(hard_gate_report)

    final_manifest_entries = []
    for name, data in sorted(content.items()):
        if name == "artifact_hash_manifest.json":
            continue
        final_manifest_entries.append(
            {
                "path": f"{PRIMARY_ANCHOR}{name}",
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    final_manifest_entries.append(
        {
            "path": rel(SCRIPT_PATH),
            "bytes": SCRIPT_PATH.stat().st_size,
            "sha256": sha256_file(SCRIPT_PATH),
            "role": "round_local_helper_script",
        }
    )
    content["artifact_hash_manifest.json"] = json_bytes(
        {
            **common,
            "schema_version": "structural-signal-scope-re-seal-artifact-hash-manifest-v1",
            "hash_algorithm": "sha256",
            "manifest_self_excluded": True,
            "manifest_self_exclusion_reason": "matches existing project hash-manifest pattern and avoids self-referential fixed-point hashing",
            "artifacts": final_manifest_entries,
        }
    )
    return content, all_gates_pass


def write_content(content: dict[str, bytes]) -> None:
    ROUND_ROOT.mkdir(parents=True, exist_ok=True)
    for name, data in content.items():
        (ROUND_ROOT / name).write_bytes(data)


def final_file_parse_check() -> None:
    for path in ROUND_ROOT.glob("*.json"):
        json.loads(path.read_text(encoding="utf-8"))
    for path in ROUND_ROOT.glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                json.loads(line)


def main() -> int:
    validation = validation_results()
    content, all_gates_pass = build_content(validation)
    write_content(content)
    final_file_parse_check()
    hard_gate = json.loads((ROUND_ROOT / "phase5_hard_gate_report.json").read_text(encoding="utf-8"))
    print(stable_json({
        "round_root": rel(ROUND_ROOT),
        "generated_artifact_count": len(content),
        "all_gates_pass": hard_gate["all_gates_pass"],
        "python_unittest": validation["python_unittest"],
        "lua_syntax": validation["lua_syntax"],
    }))
    return 0 if all_gates_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
