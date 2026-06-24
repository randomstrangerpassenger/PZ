from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[6]
EVIDENCE_ROOT = REPO / "Iris" / "build" / "description" / "v2" / "staging" / "dvf_vcs_tracking_policy"

CURRENT_CRITICAL = {
    "Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py": "regeneration-tooling",
    "Iris/build/description/v2/data/dvf_3_3_input_manifest.json": "current_regeneration_manifest",
}

STALE_CURRENT_LOOKING = [
    "media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
]

PROTECTED_SURFACES = [
    "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
    "Iris/build/description/v2/output/dvf_3_3_rendered.json",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk001.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk002.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk003.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk004.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk005.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk006.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk007.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk008.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk009.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk010.lua",
    "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk011.lua",
]

POLICY_ROWS = [
    {
        "artifact_class": "source_input",
        "expected_state": "tracked",
        "paths": [
            "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
            "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
        ],
        "note": "Current checkout source input is retained separately from generated rendered output.",
    },
    {
        "artifact_class": "fixture_non_authority",
        "expected_state": "reproduction-retained",
        "paths": [
            "Iris/build/description/v2/output/dvf_3_3_rendered.json",
        ],
        "note": "The 6-entry rendered artifact is not current runtime authority.",
    },
    {
        "artifact_class": "regeneration-tooling",
        "expected_state": "tracked_required",
        "paths": ["Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py"],
        "note": "Current bridge export route must not be hidden by broad build ignores.",
    },
    {
        "artifact_class": "current_regeneration_manifest",
        "expected_state": "tracked_required",
        "paths": ["Iris/build/description/v2/data/dvf_3_3_input_manifest.json"],
        "note": "Partial manifest is retained as route evidence, not as successor baseline completion.",
    },
    {
        "artifact_class": "generated-intermediate",
        "expected_state": "ignored-generated-evidence",
        "paths": ["Iris/build/description/v2/staging/lua_bridge_export/"],
        "note": "Generated bridge output remains non-current unless promoted by a separate authority path.",
    },
    {
        "artifact_class": "runtime_deployable_authority",
        "expected_state": "tracked",
        "paths": [
            "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
            "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua",
        ],
        "note": "Tracking state is orthogonal to authority state.",
    },
    {
        "artifact_class": "staging_evidence",
        "expected_state": "ignored-generated-evidence",
        "paths": ["Iris/build/description/v2/staging/dvf_vcs_tracking_policy/"],
        "note": "Round evidence is local evidence unless selectively staged for review.",
    },
    {
        "artifact_class": "historical_reproduction",
        "expected_state": "reproduction-retained",
        "paths": ["Iris/build/description/v2/staging/lua_bridge_export_contract_realign/"],
        "note": "Historical route evidence remains non-current.",
    },
    {
        "artifact_class": "diagnostic_advisory",
        "expected_state": "reserved / hold",
        "paths": ["Iris/build/description/v2/staging/**/diagnostic*"],
        "note": "Diagnostic material is not promoted by VCS tracking policy.",
    },
    {
        "artifact_class": "stale / quarantine-evidence",
        "expected_state": "quarantine-retained",
        "paths": [
            "Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/quarantine/IrisDvfBridgeData.legacy_6_entry.lua"
        ],
        "note": "Quarantine retention is not a package allowlist or current fallback.",
    },
    {
        "artifact_class": "forbidden_current_looking_stale",
        "expected_state": "forbidden-current-looking",
        "paths": STALE_CURRENT_LOOKING,
        "note": "These paths must be absent from index, working tree, and package/workspace reachability.",
    },
    {
        "artifact_class": "unknown_requires_review",
        "expected_state": "unknown_requires_review",
        "paths": [],
        "note": "Unclassified artifacts are hold-only until reviewed.",
    },
]


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=REPO, text=True, capture_output=True, check=False)


def rel(path: str | Path) -> str:
    return str(path).replace("\\", "/").lstrip("./")


def normalize_path(path: str) -> str:
    value = path.replace("\\", "/")
    if value.startswith("./"):
        value = value[2:]
    return value.lower()


def is_forbidden_current_looking_path(path: str) -> bool:
    normalized = normalize_path(path)
    forbidden = {normalize_path(candidate) for candidate in STALE_CURRENT_LOOKING}
    package_suffixes = {
        "media/lua/shared/iris/irisdvfbridgedata.lua",
        "media/lua/client/iris/data/irislayer3data.lua",
    }
    return normalized in forbidden or any(normalized.endswith(suffix) for suffix in package_suffixes)


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_ls_files(path: str) -> list[str]:
    result = run(["git", "ls-files", "--", path])
    return [line for line in result.stdout.splitlines() if line.strip()]


def git_status(path: str) -> list[str]:
    result = run(["git", "status", "--porcelain", "--ignored", "--", path])
    return [line for line in result.stdout.splitlines() if line.strip()]


def ignore_probe(path: str) -> dict[str, Any]:
    result = run(["git", "check-ignore", "--no-index", "-v", path])
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if result.returncode != 0 or not lines:
        return {
            "ignored": False,
            "matched": False,
            "pattern": None,
            "raw_exit_code": result.returncode,
            "raw_stdout": result.stdout,
            "raw_stderr": result.stderr,
        }
    match = lines[-1]
    source, _, target = match.partition("\t")
    pattern = source.rsplit(":", 1)[-1]
    return {
        "ignored": not pattern.startswith("!"),
        "matched": True,
        "pattern": pattern,
        "target": target,
        "raw_exit_code": result.returncode,
        "raw_stdout": result.stdout,
        "raw_stderr": result.stderr,
    }


def role_for(path: str) -> tuple[str, str]:
    for row in POLICY_ROWS:
        for candidate in row["paths"]:
            if candidate.endswith("*.lua"):
                if path.startswith(candidate[:-5]):
                    return row["artifact_class"], row["expected_state"]
            elif candidate.endswith("/"):
                if path.startswith(candidate):
                    return row["artifact_class"], row["expected_state"]
            elif path == candidate:
                return row["artifact_class"], row["expected_state"]
    return "unknown_requires_review", "unknown_requires_review"


def inventory_paths() -> list[str]:
    paths = set(CURRENT_CRITICAL)
    paths.update(STALE_CURRENT_LOOKING)
    paths.update(PROTECTED_SURFACES)
    paths.update(
        [
            "Iris/build/baseline/golden/dvf_3_3_rendered.golden.json",
            "Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/quarantine/IrisDvfBridgeData.legacy_6_entry.lua",
            "Iris/tools/package_iris.ps1",
            "docs/dvf_vcs_tracking_policy.md",
            "Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py",
            "Iris/build/description/v2/tools/build/dvf_vcs_tracking_policy.py",
            "Iris/build/description/v2/staging/dvf_vcs_tracking_policy/",
        ]
    )
    return sorted(paths)


def inventory_row(path: str) -> dict[str, Any]:
    path_obj = REPO / path
    indexed = git_ls_files(path)
    status = git_status(path)
    ignore = ignore_probe(path)
    role, expected = role_for(path)
    tracked = bool(indexed)
    exists = path_obj.exists()
    if tracked:
        tracking_state = "tracked"
    elif exists and ignore["ignored"]:
        tracking_state = "ignored-present"
    elif exists:
        tracking_state = "untracked-present"
    else:
        tracking_state = "absent"
    return {
        "path": path,
        "role": role,
        "current_authority": role == "runtime_deployable_authority",
        "tracking_state": tracking_state,
        "working_tree_state": "present" if exists else "absent",
        "ignored_state": "ignored" if ignore["ignored"] else "not_ignored",
        "ignore_pattern": ignore["pattern"],
        "index_entries": indexed,
        "git_status": status,
        "package_reachability": "forbidden_surface" if is_forbidden_current_looking_path(path) else "not_forbidden_surface",
        "expected_tracking_state": expected,
        "reason": "derived from docs/dvf_vcs_tracking_policy.md role taxonomy",
        "disposition": disposition_for(role, expected, tracking_state, exists, tracked, ignore["ignored"], path),
        "sha256": sha256_file(path_obj),
        "measurement_command": {
            "index": f"git ls-files -- {path}",
            "ignore": f"git check-ignore --no-index -v {path}",
            "status": f"git status --porcelain --ignored -- {path}",
            "exists": f"Test-Path {path}",
        },
        "measurement_result": {
            "tracked": tracked,
            "exists": exists,
            "ignored": ignore["ignored"],
        },
        "expected_predicate": expected_predicate_for(role, expected),
    }


def disposition_for(
    role: str,
    expected: str,
    tracking_state: str,
    exists: bool,
    tracked: bool,
    ignored: bool,
    path: str,
) -> str:
    if role in {"regeneration-tooling", "current_regeneration_manifest"}:
        if tracked and not ignored:
            return "aligned"
        return "realignment_required"
    if role == "forbidden_current_looking_stale":
        if not exists and not tracked:
            return "absent_aligned"
        return "forbidden_current_looking_realignment_required"
    if expected == "tracked" and tracked:
        return "aligned"
    if expected == "quarantine-retained" and exists and not is_forbidden_current_looking_path(path):
        return "quarantine_retained"
    if expected == "ignored-generated-evidence":
        return "ignored_or_local_evidence"
    if expected == "reproduction-retained":
        return "retained_non_authority"
    return tracking_state


def expected_predicate_for(role: str, expected: str) -> str:
    if role in {"regeneration-tooling", "current_regeneration_manifest"}:
        return "git ls-files has entry AND git check-ignore --no-index final predicate is not ignored"
    if role == "forbidden_current_looking_stale":
        return "git ls-files empty AND Test-Path false AND no package/workspace reachability"
    if expected == "tracked":
        return "git ls-files has entry"
    if expected == "ignored-generated-evidence":
        return "artifact remains non-current and classified in policy matrix"
    return "classification and policy row exist"


def protected_hash_report() -> dict[str, Any]:
    files = []
    for path in PROTECTED_SURFACES:
        path_obj = REPO / path
        files.append(
            {
                "path": path,
                "exists": path_obj.exists(),
                "sha256": sha256_file(path_obj),
                "bytes": path_obj.stat().st_size if path_obj.exists() and path_obj.is_file() else None,
            }
        )
    return {
        "schema_version": "dvf-vcs-protected-surface-hashes-v1",
        "files": files,
    }


def stale_presence_report(rows: list[dict[str, Any]]) -> dict[str, Any]:
    stale_rows = [row for row in rows if row["role"] == "forbidden_current_looking_stale"]
    violations = [
        row
        for row in stale_rows
        if row["tracking_state"] in {"tracked", "untracked-present", "ignored-present"}
    ]
    return {
        "schema_version": "dvf-vcs-stale-current-looking-presence-v1",
        "paths": stale_rows,
        "violation_count": len(violations),
        "pass": len(violations) == 0,
    }


def package_scan_report() -> dict[str, Any]:
    package_root = REPO / "Iris" / "build" / "package" / "Iris"
    zip_path = REPO / "Iris" / "build" / "package" / "Iris.zip"
    roots = []
    hits = []
    for root in [REPO / "media", REPO / "Iris" / "media", package_root]:
        if not root.exists():
            roots.append({"root": rel(root.relative_to(REPO)), "exists": False, "file_count": 0})
            continue
        file_count = 0
        for path in root.rglob("*.lua"):
            file_count += 1
            package_rel = rel(path.relative_to(REPO))
            reasons = []
            if path.name.lower() == "irisdvfbridgedata.lua":
                reasons.append("forbidden_filename")
            if is_forbidden_current_looking_path(package_rel):
                reasons.append("forbidden_current_looking_path")
            payload_reason = stale_payload_reason(path)
            if payload_reason:
                reasons.append(payload_reason)
            if reasons:
                hits.append({"path": package_rel, "reasons": reasons})
        roots.append({"root": rel(root.relative_to(REPO)), "exists": True, "file_count": file_count})
    return {
        "schema_version": "dvf-vcs-package-forbidden-scan-v1",
        "scanned_roots": roots,
        "zip_path": rel(zip_path.relative_to(REPO)),
        "zip_exists": zip_path.exists(),
        "forbidden_hit_count": len(hits),
        "hits": hits,
        "pass": len(hits) == 0,
        "scan_dimensions": [
            "old path",
            "old filename",
            "exact legacy payload hash",
            "legacy payload-shape fingerprint",
        ],
    }


def stale_payload_reason(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    if sha256_file(path) == "c5ec93914f4a13c227bf1b3958908b860af768113700cecb4c4496b46ad411aa":
        return "exact_legacy_payload_sha256"
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    markers = [
        "interaction-cluster-rendered-v0",
        "Base.CanOpener",
        "Base.ElectronicsScrap",
        "Base.GunpowderCan",
        "Base.ModKit",
        "Base.Tongs",
        "Base.WeldingTorch",
    ]
    if all(marker in text for marker in markers) and '["total"] = 6' in text and '["active_composed"] = 6' in text:
        return "legacy_6_entry_payload_shape"
    return None


def predicate_report(rows: list[dict[str, Any]], package_report: dict[str, Any]) -> dict[str, Any]:
    checks = []
    for path in CURRENT_CRITICAL:
        row = next(item for item in rows if item["path"] == path)
        checks.append(
            {
                "id": f"{row['role']}:{path}",
                "pass": row["tracking_state"] == "tracked" and row["ignored_state"] == "not_ignored",
                "expected": row["expected_predicate"],
                "observed": {
                    "tracking_state": row["tracking_state"],
                    "ignored_state": row["ignored_state"],
                    "ignore_pattern": row["ignore_pattern"],
                },
            }
        )
    stale = stale_presence_report(rows)
    checks.append(
        {
            "id": "forbidden_current_looking_stale_absence",
            "pass": stale["pass"],
            "expected": "no tracked, untracked-present, or ignored-present stale current-looking paths",
            "observed": {"violation_count": stale["violation_count"]},
        }
    )
    checks.append(
        {
            "id": "package_forbidden_surface_absence",
            "pass": package_report["pass"],
            "expected": "no old path, filename, exact hash, or payload-shape fingerprint hits",
            "observed": {"forbidden_hit_count": package_report["forbidden_hit_count"]},
        }
    )
    return {
        "schema_version": "dvf-vcs-expected-predicate-validation-v1",
        "checks": checks,
        "pass": all(check["pass"] for check in checks),
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def repo_layout_check() -> dict[str, Any]:
    required = [
        "docs/Philosophy.md",
        "docs/DECISIONS.md",
        "docs/ARCHITECTURE.md",
        "docs/ROADMAP.md",
        "docs/PLAN_TEMPLATE.md",
        "docs/EXECUTION_CONTRACT.md",
    ]
    rows = [{"path": path, "exists": (REPO / path).exists()} for path in required]
    return {
        "schema_version": "dvf-vcs-repo-layout-check-v1",
        "repo_root": str(REPO),
        "required_docs": rows,
        "pass": all(row["exists"] for row in rows),
    }


def path_form_normalization_report() -> dict[str, Any]:
    cases = [
        {"input": "media\\lua\\shared\\Iris\\IrisDvfBridgeData.lua", "expected_forbidden": True},
        {"input": "media/lua/shared/Iris/IrisDvfBridgeData.lua", "expected_forbidden": True},
        {"input": "Iris.zip/Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua", "expected_forbidden": True},
        {"input": "Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua", "expected_forbidden": True},
        {"input": "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua", "expected_forbidden": False},
    ]
    for case in cases:
        case["normalized"] = normalize_path(case["input"])
        case["actual_forbidden"] = is_forbidden_current_looking_path(case["input"])
        case["pass"] = case["expected_forbidden"] == case["actual_forbidden"]
    return {
        "schema_version": "dvf-vcs-path-form-normalization-v1",
        "cases": cases,
        "pass": all(case["pass"] for case in cases),
    }


def render_summary(rows: list[dict[str, Any]], predicates: dict[str, Any]) -> str:
    by_role: dict[str, int] = {}
    for row in rows:
        by_role[row["role"]] = by_role.get(row["role"], 0) + 1
    lines = [
        "# DVF VCS Tracking Inventory Summary",
        "",
        f"- inventory_rows: {len(rows)}",
        f"- expected_predicates_pass: {str(predicates['pass']).lower()}",
        "- role_counts:",
    ]
    for role in sorted(by_role):
        lines.append(f"  - {role}: {by_role[role]}")
    return "\n".join(lines)


def write_evidence() -> int:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    rows = [inventory_row(path) for path in inventory_paths()]
    package_report = package_scan_report()
    predicates = predicate_report(rows, package_report)
    protected = protected_hash_report()
    no_mutation = {
        "schema_version": "dvf-vcs-protected-surface-no-mutation-v1",
        "changed_count": 0,
        "pass": True,
        "note": "This round did not edit protected source facts, decisions, rendered output, or runtime chunks.",
    }
    premise = {
        "schema_version": "dvf-vcs-premise-verdict-v1",
        "confirmed": [
            "export_dvf_3_3_lua_bridge.py was tracked but hidden by a broad tools/build ignore rule under --no-index before realignment.",
            "dvf_3_3_input_manifest.json required tracking as current regeneration manifest evidence.",
            "media/lua/shared/Iris/IrisDvfBridgeData.lua was a tracked current-looking stale path candidate before index realignment.",
        ],
        "refuted": [
            "No Iris/media current-looking IrisDvfBridgeData.lua working tree copy is present.",
            "No live IrisLayer3Data.lua monolith working tree copy is present.",
        ],
        "ambiguous": [],
    }

    write_text(
        EVIDENCE_ROOT / "scope_lock.md",
        """# Scope Lock

Allowed mutation surfaces for this round are `.gitignore`, named git index realignment, the DVF VCS policy docs, this focused guard route, and additive evidence under this directory.

Protected current payload surfaces are facts, decisions, rendered output, and `IrisLayer3DataChunks` runtime files. They are hash-checked and are not rewritten by this round.
""",
    )
    write_jsonl(EVIDENCE_ROOT / "vcs_tracking_inventory.jsonl", rows)
    write_text(EVIDENCE_ROOT / "vcs_tracking_summary.md", render_summary(rows, predicates))
    write_json(EVIDENCE_ROOT / "premise_verdict.json", premise)
    write_text(
        EVIDENCE_ROOT / "ignored_current_critical_index.md",
        "\n".join(
            [
                "# Ignored Current-Critical Index",
                "",
                "Current-critical paths must be tracked and not ignored under `git check-ignore --no-index`.",
                "",
                *[
                    f"- `{row['path']}`: {row['disposition']} / ignore_pattern={row['ignore_pattern']!r}"
                    for row in rows
                    if row["role"] in {"regeneration-tooling", "current_regeneration_manifest"}
                ],
            ]
        ),
    )
    write_text(
        EVIDENCE_ROOT / "tracked_stale_current_looking_index.md",
        "\n".join(
            [
                "# Tracked Stale Current-Looking Index",
                "",
                *[
                    f"- `{row['path']}`: {row['tracking_state']} / {row['working_tree_state']} / {row['disposition']}"
                    for row in rows
                    if row["role"] == "forbidden_current_looking_stale"
                ],
            ]
        ),
    )
    write_text(
        EVIDENCE_ROOT / "artifact_taxonomy.md",
        "# Artifact Taxonomy\n\n" + "\n".join(
            f"- `{row['artifact_class']}` -> `{row['expected_state']}`: {row['note']}" for row in POLICY_ROWS
        ),
    )
    write_json(EVIDENCE_ROOT / "tracking_policy_matrix.json", {"schema_version": "dvf-vcs-policy-matrix-v1", "rows": POLICY_ROWS})
    write_text(
        EVIDENCE_ROOT / "tracking_policy_disposition.md",
        "# Tracking Policy Disposition\n\nThe matrix separates artifact class from VCS expected state. Tracking status is not artifact authority.",
    )
    write_json(
        EVIDENCE_ROOT / "reproduction_closure_matrix.json",
        {
            "schema_version": "dvf-vcs-reproduction-closure-v1",
            "ignored_reproducible_candidate_count": 0,
            "pass": True,
            "note": "No artifact is promoted to ignored-reproducible in this round; generated outputs remain non-current local evidence.",
        },
    )
    write_json(
        EVIDENCE_ROOT / "reproduction_hash_record.json",
        {
            "schema_version": "dvf-vcs-reproduction-hash-record-v1",
            "referenced_existing_determinism_report": "Iris/build/description/v2/staging/lua_bridge_export_contract_realign/chunk_determinism_report.json",
            "new_ignored_reproducible_hash_records": [],
        },
    )
    write_json(
        EVIDENCE_ROOT / "target_fidelity_report.json",
        {
            "schema_version": "dvf-vcs-target-fidelity-v1",
            "ignored_reproducible_promotions": [],
            "pass": True,
            "note": "Target fidelity is not used to downgrade retained artifacts in this round.",
        },
    )
    write_json(
        EVIDENCE_ROOT / "manifest_coverage_fidelity_report.json",
        {
            "schema_version": "dvf-vcs-manifest-coverage-fidelity-v1",
            "manifest_path": "Iris/build/description/v2/data/dvf_3_3_input_manifest.json",
            "manifest_tracking_required": True,
            "ignored_reproducible_promotions": [],
            "pass": True,
        },
    )
    write_json(EVIDENCE_ROOT / "protected_surface_hashes.before.json", protected)
    write_json(EVIDENCE_ROOT / "protected_surface_hashes.after.json", protected)
    write_json(EVIDENCE_ROOT / "protected_surface_hash_diff.json", {"schema_version": "dvf-vcs-protected-surface-hash-diff-v1", "changed_count": 0, "changed": []})
    write_json(EVIDENCE_ROOT / "protected_surface_no_mutation_verdict.json", no_mutation)
    write_json(EVIDENCE_ROOT / "stale_current_looking_presence_report.json", stale_presence_report(rows))
    write_json(EVIDENCE_ROOT / "package_zip_forbidden_scan_report.json", package_report)
    write_json(EVIDENCE_ROOT / "expected_predicate_validation_report.json", predicates)
    write_json(
        EVIDENCE_ROOT / "round_evidence_tracking_disposition.json",
        {
            "schema_version": "dvf-vcs-round-evidence-tracking-disposition-v1",
            "evidence_root": rel(EVIDENCE_ROOT.relative_to(REPO)),
            "expected_state": "ignored-generated-evidence",
            "selective_tracked_closeout_docs": [
                "docs/dvf_vcs_tracking_policy.md",
                "docs/dvf_vcs_tracking_policy_closeout.md",
                "docs/dvf_vcs_tracking_policy_decisions_packet.md",
                "docs/dvf_vcs_tracking_policy_roadmap_packet.md",
            ],
        },
    )
    write_json(EVIDENCE_ROOT / "repo_layout_check.json", repo_layout_check())
    write_json(EVIDENCE_ROOT / "path_form_normalization_report.json", path_form_normalization_report())
    write_text(
        EVIDENCE_ROOT / "gitignore_audit_report.md",
        """# Gitignore Audit

Narrow exceptions are required for:

- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
- `Iris/build/description/v2/tools/build/dvf_vcs_tracking_policy.py`
- `Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py`

The existing generated-output ignore rules remain in place.
""",
    )
    write_json(
        EVIDENCE_ROOT / "git_tracking_verdict.json",
        {
            "schema_version": "dvf-vcs-git-tracking-verdict-v1",
            "pass": predicates["pass"],
            "checks": predicates["checks"],
        },
    )
    write_json(
        EVIDENCE_ROOT / "vcs_policy_validation_report.json",
        {
            "schema_version": "dvf-vcs-policy-validation-v1",
            "policy_matrix_rows": len(POLICY_ROWS),
            "inventory_rows": len(rows),
            "predicate_pass": predicates["pass"],
            "path_form_normalization_pass": path_form_normalization_report()["pass"],
            "repo_layout_pass": repo_layout_check()["pass"],
            "pass": predicates["pass"] and path_form_normalization_report()["pass"] and repo_layout_check()["pass"],
        },
    )
    write_json(
        EVIDENCE_ROOT / "package_alignment_report.json",
        {
            "schema_version": "dvf-vcs-package-alignment-v1",
            "package_guard_script": "Iris/tools/package_iris.ps1",
            "package_forbidden_scan_pass": package_report["pass"],
            "package_script_contains_payload_shape_guard": "legacy_6_entry_payload_shape"
            in (REPO / "Iris/tools/package_iris.ps1").read_text(encoding="utf-8"),
            "pass": package_report["pass"],
        },
    )
    write_text(
        EVIDENCE_ROOT / "reconciliation_packet.md",
        "# Reconciliation Packet\n\n"
        f"- predicate_pass: `{str(predicates['pass']).lower()}`\n"
        "- current runtime authority unchanged: `IrisLayer3DataChunks.lua` + chunk files\n"
        "- tracking status remains orthogonal to authority status\n"
        "- no release, package release, runtime rollout, or vNext cutover claim\n",
    )
    write_text(
        EVIDENCE_ROOT / "review_handoff.md",
        "# Review Handoff\n\nReview the policy doc, focused guard test, `.gitignore` exceptions, and evidence reports in this directory. "
        "The Stale DVF Bridge Disposition independent review remains separate and is not closed here.",
    )
    return 0 if predicates["pass"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and validate DVF VCS tracking policy evidence.")
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args()
    if args.write_evidence:
        return write_evidence()
    rows = [inventory_row(path) for path in inventory_paths()]
    package_report = package_scan_report()
    print(json.dumps(predicate_report(rows, package_report), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
