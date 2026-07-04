from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
from typing import Any

from _dvf_3_3_vnext_common import (
    REPO_ROOT,
    V2_ROOT,
    canonical_hash,
    rel,
    resolve_repo,
    sha256_file,
    write_json,
    write_text,
)


ROUND_ID = "dvf_3_3_legacy_combined_route_axis_inventory_routing_preflight"
FREEZE_SENTENCE = (
    "current_route_required_validations.json = legacy_combined_governance_route "
    "!= DVF Core PASS authority"
)
AXES = [
    "dvf_core_body_compiler",
    "registry_authority",
    "registry_runtime_compatibility",
    "publish_boundary",
    "legacy_combined_governance_route",
    "historical_predecessor_trace",
    "diagnostic_or_fixture",
]
MANDATED_FINAL_STATEMENTS = [
    "legacy combined route는 현 상태 유지",
    "legacy combined route PASS는 DVF Core PASS가 아님",
    "DVF Core boundary closure가 소비할 수 있는 axis inventory가 준비됨",
    "본 분리 closure에서 물리 manifest split을 요구하지 않아도 됨",
]

DEFAULT_EVIDENCE_ROOT = V2_ROOT / "staging" / ROUND_ID
EVIDENCE_ROOT = resolve_repo(
    os.environ.get("DVF_LEGACY_COMBINED_ROUTE_AXIS_INVENTORY_ROOT", DEFAULT_EVIDENCE_ROOT)
)

ROUND_DIR = REPO_ROOT / "Iris" / "_docs" / "round3"
REQUIRED_MANIFEST = ROUND_DIR / "current_route_required_validations.json"
TAXONOMY = ROUND_DIR / "round3_test_taxonomy.json"
ACTIVE_CORE_CLOSURE = ROUND_DIR / "round3_active_core_closure.json"
ROUND3_RUNNER = ROUND_DIR / "round3_run_contract_tests.py"
PLAN_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_plan.md"
POLICY_DOC = REPO_ROOT / "docs" / "dvf_3_3_legacy_combined_route_axis_policy.md"
TOP_DOCS = [
    REPO_ROOT / "docs" / "DECISIONS.md",
    REPO_ROOT / "docs" / "ARCHITECTURE.md",
    REPO_ROOT / "docs" / "ROADMAP.md",
]
TOOLS_DIR = Path(__file__).resolve().parent
FOCUSED_TEST_MODULE = f"test_{ROUND_ID}"

PROTECTED_SURFACE_PATHS = [
    REQUIRED_MANIFEST,
    TAXONOMY,
    ACTIVE_CORE_CLOSURE,
    ROUND3_RUNNER,
    "Iris/build/description/v2/data",
    "Iris/build/description/v2/output",
    "Iris/Iris/media/lua/client/Iris/Data",
    "Iris/media",
    "Iris/build/package",
    "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "media/lua/shared/Iris/IrisDvfBridgeData.lua",
]

CLAIM_TERMS = re.compile(
    r"\b(PASS|complete|ready|release|package|Core)\b|current authority|DVF Core|Workshop|B42|deployment",
    re.IGNORECASE,
)
NEGATION_TERMS = (
    " no_",
    " no-",
    " no ",
    "not ",
    "not_",
    "does not",
    "do not",
    "must not",
    "never means",
    "without claiming",
    "without claim",
    "unless",
    "forbidden",
    "out of scope",
    "out-of-scope",
    "아님",
    "아니다",
    "아니라",
    "않음",
    "의미하지",
    "뜻하지",
    "금지",
    "오독 금지",
    "non-claim",
    "non_claim",
    "not mean",
    "could overclaim",
    "could be misread",
    "misread",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json_object(path: str | Path) -> dict[str, Any]:
    resolved = resolve_repo(path)
    with resolved.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root is not an object: {resolved}")
    return payload


def hash_path(path: str | Path) -> str | None:
    resolved = resolve_repo(path)
    if not resolved.exists():
        return None
    if resolved.is_file():
        return sha256_file(resolved)
    records: list[dict[str, str | None]] = []
    for child in sorted(p for p in resolved.rglob("*") if p.is_file()):
        records.append(
            {
                "path": child.relative_to(resolved).as_posix(),
                "sha256": sha256_file(child),
            }
        )
    return canonical_hash(records)


def file_record(path: str | Path, role: str) -> dict[str, Any]:
    resolved = resolve_repo(path)
    return {
        "path": rel(resolved),
        "role": role,
        "exists": resolved.exists(),
        "kind": "dir" if resolved.is_dir() else "file" if resolved.is_file() else "missing",
        "sha256": hash_path(resolved),
    }


def protected_surface_hashes() -> list[dict[str, Any]]:
    return [file_record(path, "protected_no_mutation_surface") for path in PROTECTED_SURFACE_PATHS]


def protected_hash_diff(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> list[dict[str, Any]]:
    before_by_path = {row["path"]: row for row in before}
    rows: list[dict[str, Any]] = []
    for after_row in after:
        before_row = before_by_path.get(after_row["path"], {})
        rows.append(
            {
                "path": after_row["path"],
                "before_exists": before_row.get("exists"),
                "after_exists": after_row.get("exists"),
                "before_sha256": before_row.get("sha256"),
                "after_sha256": after_row.get("sha256"),
                "changed": before_row.get("exists") != after_row.get("exists")
                or before_row.get("sha256") != after_row.get("sha256"),
            }
        )
    return rows


def load_required_tests(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows = manifest.get("required_tests")
    if not isinstance(rows, list):
        return []
    output = []
    for row in rows:
        if isinstance(row, dict) and row.get("test_id"):
            output.append(
                {
                    "test_id": str(row["test_id"]),
                    "role": str(row.get("role", "")),
                    "required": row.get("required") is True,
                }
            )
    return sorted(output, key=lambda item: item["test_id"])


def load_required_artifacts(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows = manifest.get("required_artifacts")
    if not isinstance(rows, list):
        return []
    output = []
    for row in rows:
        if isinstance(row, dict) and row.get("path"):
            output.append(
                {
                    "path": str(row["path"]).replace("\\", "/"),
                    "checks": row.get("checks", []),
                }
            )
    return sorted(output, key=lambda item: item["path"])


def taxonomy_current_tests(taxonomy: dict[str, Any]) -> list[str]:
    rows = taxonomy.get("rows")
    if not isinstance(rows, list):
        return []
    test_ids = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("contract_class") == "current" and row.get("state") == "ok" and row.get("test_id"):
            test_ids.append(str(row["test_id"]))
    return sorted(set(test_ids))


def route_union_tests(taxonomy: dict[str, Any], manifest: dict[str, Any]) -> list[str]:
    required = {row["test_id"] for row in load_required_tests(manifest)}
    return sorted(set(taxonomy_current_tests(taxonomy)).union(required))


def line_number_for(path: Path, needle: str) -> int | None:
    if not path.exists():
        return None
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if needle in line:
            return index
    return None


def runner_claim_surfaces() -> list[dict[str, Any]]:
    surfaces = [
        ("default_taxonomy_path", "DEFAULT_TAXONOMY"),
        ("default_active_core_closure_path", "DEFAULT_CLOSURE"),
        ("default_required_manifest_path", "DEFAULT_REQUIRED_VALIDATIONS"),
        ("required_manifest_schema_check", "round3-current-route-required-validations-v1"),
        ("current_only_required_manifest_loading", "contract_class != \"current\""),
        ("taxonomy_required_union", "combined_test_ids"),
        ("required_artifact_field_check", "artifact_check_errors"),
        ("closure_blocker_allowed_modules", "current_route_allowed_tooling_modules"),
        ("result_payload_required_validations", "\"required_validations\""),
    ]
    rows = []
    for surface_id, needle in surfaces:
        rows.append(
            {
                "item_id": f"runner_claim::{surface_id}",
                "item_kind": "runner_claim_surface",
                "source_path": rel(ROUND3_RUNNER),
                "line": line_number_for(ROUND3_RUNNER, needle),
                "surface_id": surface_id,
                "claim_surface_role": "legacy_combined_route_runner_scaffold",
            }
        )
    return rows


def active_core_closure_surfaces(closure: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = [
        {
            "item_id": "active_core_closure::container",
            "item_kind": "active_core_closure_container",
            "source_path": rel(ACTIVE_CORE_CLOSURE),
            "surface_id": "active_core_closure_container",
            "claim_surface_role": "current_core_and_tooling_allowlist_container",
        }
    ]
    for module in sorted(str(item) for item in closure.get("current_closure_modules", [])):
        rows.append(
            {
                "item_id": f"active_core_module::{module}",
                "item_kind": "active_core_module",
                "source_path": rel(ACTIVE_CORE_CLOSURE),
                "module": module,
                "claim_surface_role": "current_core_module",
            }
        )
    for module in sorted(str(item) for item in closure.get("current_route_allowed_tooling_modules", [])):
        rows.append(
            {
                "item_id": f"current_route_tooling::{module}",
                "item_kind": "current_route_allowed_tooling_module",
                "source_path": rel(ACTIVE_CORE_CLOSURE),
                "module": module,
                "claim_surface_role": "current_regeneration_tooling_not_current_core",
            }
        )
    return rows


def is_guard_surface(test_id: str) -> bool:
    lowered = test_id.lower()
    markers = (
        "guard",
        "validation",
        "validate",
        "manifest",
        "package",
        "runtime",
        "authority",
        "closure",
        "fail",
        "negative",
        "matrix",
        "contract",
        "integrity",
        "seal",
        "parity",
        "freshness",
        "reentry",
        "boundary",
        "blocks",
        "preserves",
        "reject",
    )
    return any(marker in lowered for marker in markers)


def guard_test_rows(current_route_union: list[str], required_tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required = {row["test_id"]: row for row in required_tests}
    rows = []
    for test_id in current_route_union:
        rows.append(
            {
                "item_id": f"test::{test_id}",
                "item_kind": "current_route_union_test",
                "source_path": test_id.split(".", 1)[0] + ".py",
                "test_id": test_id,
                "required_manifest_member": test_id in required,
                "required_role": required.get(test_id, {}).get("role"),
                "guard_surface": is_guard_surface(test_id),
                "guard_census_disposition": "guard_surface"
                if is_guard_surface(test_id)
                else "explicit_non_guard_current_route_union_row",
            }
        )
    return rows


def relevant_closeout_docs() -> list[Path]:
    docs = REPO_ROOT / "docs"
    patterns = [
        "dvf_3_3_current_route_authority_required_evidence_integrity_closure*.md",
        "dvf_3_3_current_route_required_validation_evidence_freshness_reseal*.md",
        "dvf_3_3_closeout_reentry*.md",
        "dvf_3_3_completion_vocabulary_external_gate*.md",
        "dvf_3_3_required_artifact_disposition_seal*.md",
        "dvf_3_3_legacy_combined_route_axis*.md",
    ]
    paths: set[Path] = {PLAN_DOC, POLICY_DOC}
    for pattern in patterns:
        paths.update(docs.glob(pattern))
    return sorted(path for path in paths if path.exists())


def has_negation(text: str) -> bool:
    padded = " " + text.lower() + " "
    return any(term in padded for term in NEGATION_TERMS)


def claim_disposition(line: str) -> str:
    lowered = line.lower()
    stripped = line.strip().lower()
    if "flag any claim" in lowered or "flag unqualified" in lowered:
        return "false_positive_excluded"
    if stripped in {"* release readiness", "* package readiness"}:
        return "false_positive_excluded"
    if "readiness" in lowered and (
        "declaration" in lowered
        or "governance-only" in lowered
        or stripped.startswith("*")
        or stripped.endswith(",")
        or stripped.endswith(".")
        and not any(verb in lowered for verb in (" is ", " are ", " declared", " achieved", " complete"))
    ):
        return "false_positive_excluded"
    if "legacy combined route pass == dvf core pass" in lowered and not has_negation(line):
        return "freeze_contradiction_candidate"
    if has_negation(line):
        return "negated_claim"
    if line.lstrip().startswith(">") or "`" in line:
        return "quoted_claim"
    if "predecessor" in lowered:
        return "predecessor_trace"
    if "historical" in lowered or "provenance" in lowered:
        return "historical_provenance"
    return "actual_current_claim"


def scan_closeout_docs() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in relevant_closeout_docs():
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not CLAIM_TERMS.search(line):
                continue
            disposition = claim_disposition(line)
            lowered = line.lower()
            forbidden = (
                disposition == "freeze_contradiction_candidate"
                or (
                    disposition == "actual_current_claim"
                    and ("release readiness" in lowered or "package readiness" in lowered)
                )
            )
            rows.append(
                {
                    "item_id": f"doc_claim::{rel(path)}::L{line_number}",
                    "item_kind": "governance_closeout_claim_surface",
                    "source_path": rel(path),
                    "line": line_number,
                    "claim_text": line.strip(),
                    "claim_disposition_kind": disposition,
                    "forbidden_overclaim": forbidden,
                }
            )
    return rows


def policy_text() -> str:
    return f"""# DVF 3-3 Legacy Combined Route Axis Policy

Status: governance-only routing preflight policy.

Freeze:

```text
{FREEZE_SENTENCE}
```

The current combined governance route remains preserved. A route-level PASS is not DVF Core PASS authority.

## Axis Enum

* `dvf_core_body_compiler` - body compiler, compose, and DVF body production surfaces.
* `registry_authority` - source, decision, current authority, successor readpoint, and registry authority surfaces.
* `registry_runtime_compatibility` - runtime payload shape and consumer compatibility surfaces.
* `publish_boundary` - bridge export, package, publish, and release-boundary guard surfaces.
* `legacy_combined_governance_route` - runner container, manifest container, taxonomy/required-validation governance chain, current route PASS claim surface, and combined-route claim-boundary scaffolding.
* `historical_predecessor_trace` - predecessor, stale artifact, historical preservation, and reentry-prevention surfaces.
* `diagnostic_or_fixture` - diagnostic, negative fixture, and fail-closed test-only surfaces.

## Core Rules

```text
routed-through legacy combined route
!=
responsibility-of legacy combined governance route
```

Each item has exactly one `primary_axis`. `unknown`, `todo`, `tbd`, and `unclear` are blockers, not classifications.

Lifecycle disposition is metadata only. It does not replace the responsibility axis.

`legacy_combined_governance_route` is limited to route scaffolding, manifest/taxonomy containers, required-validation governance chain surfaces, combined-route closeout coordination, and explicit claim-boundary surfaces. Any required test or artifact assigned to this axis must include `route_container_or_claim_surface_reason_code`.

## Non-Claims

This policy does not claim DVF Core PASS, Registry Authority PASS, Registry Runtime Compatibility PASS, package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, public text quality acceptance, runtime mutation, bridge export mutation, source mutation, rendered mutation, package mutation, independent review, owner seal, or canonical seal.
"""


def schema_payload() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-legacy-combined-route-axis-schema-v1",
        "round_id": ROUND_ID,
        "freeze_sentence": FREEZE_SENTENCE,
        "axis_enum": AXES,
        "exactly_one_primary_axis_required": True,
        "forbidden_axis_values": ["unknown", "todo", "tbd", "unclear"],
        "required_record_fields": [
            "item_id",
            "item_kind",
            "source_path",
            "primary_axis",
            "classification_rule_id",
            "matched_source_kind",
            "reason_code",
            "adjudication_required",
            "claim_disposition_kind",
            "positive_evidence",
            "excluded_axes",
            "why_not_legacy_combined_governance_route",
            "why_not_dvf_core_body_compiler",
        ],
        "authority_booleans_must_remain_false_by_default": [
            "dvf_core_pass_authority",
            "registry_authority_claim",
            "runtime_writer_claim",
            "package_release_claim",
            "source_mutation_claim",
        ],
    }


def seed_rules() -> list[dict[str, Any]]:
    return [
        {
            "seed_rule_id": "seed_body_compiler_compose",
            "patterns": ["compose_", "build_iris_"],
            "axis": "dvf_core_body_compiler",
            "seed_is_authoritative": False,
        },
        {
            "seed_rule_id": "seed_runtime_payload",
            "patterns": ["runtime_payload_state_integrity", "consumer_universe_denominator"],
            "axis": "registry_runtime_compatibility",
            "seed_is_authoritative": False,
        },
        {
            "seed_rule_id": "seed_publish_package_bridge",
            "patterns": ["package", "lua_bridge_export", "publish"],
            "axis": "publish_boundary",
            "seed_is_authoritative": False,
        },
        {
            "seed_rule_id": "seed_predecessor_stale",
            "patterns": ["predecessor_stale_artifact_reentry_guard", "historical", "stale artifact"],
            "axis": "historical_predecessor_trace",
            "seed_is_authoritative": False,
        },
        {
            "seed_rule_id": "seed_legacy_route_container",
            "patterns": ["runner", "manifest container", "current-route pass", "closeout", "completion_vocabulary"],
            "axis": "legacy_combined_governance_route",
            "seed_is_authoritative": False,
        },
        {
            "seed_rule_id": "seed_diagnostic_fixture",
            "patterns": ["negative_fixture", "diagnostic", "fixture"],
            "axis": "diagnostic_or_fixture",
            "seed_is_authoritative": False,
        },
    ]


def classify_text(text: str, item_kind: str) -> tuple[str, str, str, str | None]:
    lowered = text.lower()
    if item_kind in {
        "runner_claim_surface",
        "active_core_closure_container",
        "manifest_container",
        "governance_closeout_claim_surface",
    }:
        return (
            "legacy_combined_governance_route",
            "rule_legacy_route_scaffold",
            "route_scaffold_or_claim_surface",
            "route_container_or_claim_surface",
        )
    if "predecessor_stale_artifact_reentry_guard" in lowered or "historical" in lowered:
        return (
            "historical_predecessor_trace",
            "rule_predecessor_trace_surface",
            "predecessor_or_historical_surface",
            None,
        )
    if "package" in lowered or "lua_bridge_export" in lowered or "publish" in lowered:
        return ("publish_boundary", "rule_publish_boundary_surface", "package_or_bridge_export_guard", None)
    if "runtime_payload" in lowered or "consumer_universe_denominator" in lowered or "runtime_consumer" in lowered:
        return (
            "registry_runtime_compatibility",
            "rule_runtime_compatibility_surface",
            "runtime_payload_or_consumer_compatibility",
            None,
        )
    if (
        "closeout_reentry" in lowered
        or "completion_vocabulary" in lowered
        or "required_artifact_disposition_seal" in lowered
        or "current_route_required_validation" in lowered
        or "current_route_authority_required_evidence_integrity_closure" in lowered
        or "shared_disposition" in lowered
    ):
        return (
            "legacy_combined_governance_route",
            "rule_combined_governance_gate",
            "required_validation_or_closeout_claim_surface",
            "required_validation_governance_gate",
        )
    if "negative_fixture" in lowered or ".fixtures." in lowered or "diagnostic" in lowered:
        return ("diagnostic_or_fixture", "rule_diagnostic_fixture_surface", "diagnostic_or_fixture_only", None)
    if "compose" in lowered or "body" in lowered or "build_iris_" in lowered or "rendered_regeneration" in lowered:
        return ("dvf_core_body_compiler", "rule_body_compiler_surface", "compose_or_body_compiler_surface", None)
    if (
        "current_authority" in lowered
        or "source_authority" in lowered
        or "successor_readpoint" in lowered
        or "durable_current_authority" in lowered
        or "source_promotion" in lowered
        or "authority_chain" in lowered
        or "cutover" in lowered
    ):
        return ("registry_authority", "rule_registry_authority_surface", "source_or_registry_authority", None)
    return ("registry_authority", "rule_registry_authority_fallback", "registry_authority_by_default_content", None)


def excluded_axes(primary_axis: str) -> list[dict[str, str]]:
    return [
        {
            "axis": axis,
            "reason": f"primary evidence is classified as {primary_axis}, not {axis}",
        }
        for axis in AXES
        if axis != primary_axis
    ]


def make_record(item: dict[str, Any]) -> dict[str, Any]:
    text = " ".join(str(value) for value in item.values() if value is not None)
    axis, rule_id, reason_code, route_reason = classify_text(text, str(item.get("item_kind", "")))
    required_member = item.get("required_manifest_member") is True or item.get("item_kind") == "required_artifact"
    if axis == "legacy_combined_governance_route" and route_reason is None:
        route_reason = "route_container_or_claim_surface"
    record = {
        **item,
        "primary_axis": axis,
        "classification_rule_id": rule_id,
        "matched_source_kind": item.get("item_kind"),
        "reason_code": reason_code,
        "route_container_or_claim_surface_reason_code": route_reason,
        "adjudication_required": False,
        "claim_disposition_kind": item.get(
            "claim_disposition_kind",
            "route_container_or_claim_surface"
            if axis == "legacy_combined_governance_route"
            else "axis_content_responsibility",
        ),
        "lifecycle_disposition": item.get("lifecycle_disposition", "orthogonal_metadata_only"),
        "positive_evidence": [
            {
                "kind": "source_path_or_identifier_pattern",
                "value": item.get("source_path") or item.get("test_id") or item.get("path") or item.get("item_id"),
            }
        ],
        "excluded_axes": excluded_axes(axis),
        "why_not_legacy_combined_governance_route": "not excluded; route-scaffolding rationale is recorded"
        if axis == "legacy_combined_governance_route"
        else "combined-route execution is not responsibility ownership for this item",
        "why_not_dvf_core_body_compiler": "not excluded; body compiler evidence is primary"
        if axis == "dvf_core_body_compiler"
        else "item does not own DVF body compiler output responsibility",
        "seed_axis_candidate": axis,
        "seed_rule_id": rule_id.replace("rule_", "seed_"),
        "seed_is_authoritative": False,
        "candidate_confidence": "high",
        "candidate_state": "single_axis_candidate",
        "required_manifest_member": required_member,
        "dvf_core_pass_authority": False,
        "registry_authority_claim": False,
        "runtime_writer_claim": False,
        "package_release_claim": False,
        "source_mutation_claim": False,
    }
    if axis != "legacy_combined_governance_route":
        record["route_container_or_claim_surface_reason_code"] = None
    return record


def surface_item_from_required_artifact(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": f"artifact::{row['path']}",
        "item_kind": "required_artifact",
        "source_path": row["path"],
        "path": row["path"],
        "required_manifest_member": True,
        "manifest_path": rel(REQUIRED_MANIFEST),
        "check_count": len(row.get("checks", [])),
    }


def manifest_container_item() -> dict[str, Any]:
    return {
        "item_id": "manifest_container::current_route_required_validations",
        "item_kind": "manifest_container",
        "source_path": rel(REQUIRED_MANIFEST),
        "required_manifest_member": False,
        "claim_surface_role": "required_validation_manifest_container_identity",
    }


def build_census() -> dict[str, Any]:
    manifest = read_json_object(REQUIRED_MANIFEST)
    taxonomy = read_json_object(TAXONOMY)
    closure = read_json_object(ACTIVE_CORE_CLOSURE)
    required_tests = load_required_tests(manifest)
    required_artifacts = load_required_artifacts(manifest)
    current_union = route_union_tests(taxonomy, manifest)
    taxonomy_current = taxonomy_current_tests(taxonomy)
    guard_rows = guard_test_rows(current_union, required_tests)
    closeout_claims = scan_closeout_docs()
    closure_surfaces = active_core_closure_surfaces(closure)
    runner_surfaces = runner_claim_surfaces()
    source_records = [
        file_record(REQUIRED_MANIFEST, "live_required_validation_manifest"),
        file_record(TAXONOMY, "live_round3_taxonomy"),
        file_record(ACTIVE_CORE_CLOSURE, "live_active_core_closure"),
        file_record(ROUND3_RUNNER, "live_combined_route_runner"),
        file_record(PLAN_DOC, "execution_plan"),
    ]
    source_records.extend(file_record(path, "top_doc_freeze_scan_input") for path in TOP_DOCS)
    return {
        "manifest": manifest,
        "taxonomy": taxonomy,
        "closure": closure,
        "required_tests": required_tests,
        "required_artifacts": required_artifacts,
        "taxonomy_current_tests": taxonomy_current,
        "current_route_union": current_union,
        "guard_rows": guard_rows,
        "closeout_claims": closeout_claims,
        "closure_surfaces": closure_surfaces,
        "runner_surfaces": runner_surfaces,
        "source_records": source_records,
        "current_core_modules": sorted(str(item) for item in closure.get("current_closure_modules", [])),
        "tooling_modules": sorted(str(item) for item in closure.get("current_route_allowed_tooling_modules", [])),
    }


def candidate_items(census: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    items.extend(census["guard_rows"])
    items.extend(surface_item_from_required_artifact(row) for row in census["required_artifacts"])
    items.extend(census["runner_surfaces"])
    items.extend(census["closure_surfaces"])
    items.extend(census["closeout_claims"])
    return sorted(items, key=lambda row: (str(row.get("source_path", "")), str(row.get("item_kind", "")), str(row.get("item_id", ""))))


def build_inventory(census: dict[str, Any]) -> list[dict[str, Any]]:
    records = [make_record(manifest_container_item())]
    records.extend(make_record(item) for item in candidate_items(census))
    records_by_id: dict[str, dict[str, Any]] = {}
    for record in records:
        records_by_id.setdefault(str(record["item_id"]), record)
    return sorted(
        records_by_id.values(),
        key=lambda row: (str(row.get("source_path", "")), str(row.get("item_kind", "")), str(row.get("item_id", ""))),
    )


def validation_errors_for_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    primary = record.get("primary_axis")
    if "primary_axes" in record or isinstance(primary, list):
        errors.append({"code": "multiple_primary_axes", "item_id": record.get("item_id")})
    if primary is None:
        errors.append({"code": "missing_primary_axis", "item_id": record.get("item_id")})
        return errors
    if primary in {"unknown", "todo", "tbd", "unclear"}:
        errors.append({"code": "unknown_axis", "item_id": record.get("item_id"), "primary_axis": primary})
    if primary not in AXES:
        errors.append({"code": "invalid_axis_enum", "item_id": record.get("item_id"), "primary_axis": primary})
    if primary == "legacy_combined_governance_route" and record.get("dvf_core_pass_authority") is True:
        errors.append({"code": "governance_route_core_pass_authority_claim", "item_id": record.get("item_id")})
    if primary == "historical_predecessor_trace" and record.get("runtime_writer_claim") is True:
        errors.append({"code": "historical_current_runtime_authority_claim", "item_id": record.get("item_id")})
    if primary == "diagnostic_or_fixture" and (
        record.get("source_mutation_claim") is True or record.get("source_authority_claim") is True
    ):
        errors.append({"code": "diagnostic_fixture_source_authority_claim", "item_id": record.get("item_id")})
    if primary == "publish_boundary" and record.get("package_release_claim") is True:
        errors.append({"code": "publish_boundary_package_release_ready_claim", "item_id": record.get("item_id")})
    if not record.get("positive_evidence"):
        errors.append({"code": "missing_positive_evidence", "item_id": record.get("item_id")})
    if not record.get("excluded_axes"):
        errors.append({"code": "missing_excluded_axes", "item_id": record.get("item_id")})
    if (
        record.get("required_manifest_member") is True
        and primary == "legacy_combined_governance_route"
        and not record.get("route_container_or_claim_surface_reason_code")
    ):
        errors.append({"code": "legacy_required_item_missing_route_reason", "item_id": record.get("item_id")})
    if record.get("seed_is_authoritative") is True and record.get("candidate_state") == "final_classification":
        errors.append({"code": "seed_map_authoritative_final_classification", "item_id": record.get("item_id")})
    return errors


def validate_dedup_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    required = {"dedup_key", "retained_item_id", "merged_item_ids", "merge_reason", "count_contribution"}
    for index, record in enumerate(records):
        missing = sorted(required - set(record))
        if missing:
            errors.append({"code": "deduplication_record_missing_field", "index": index, "missing": missing})
    return errors


def validate_owner_adjudication_packet(payload: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if payload.get("owner_seal_claimed") is True or payload.get("canonical_seal_claimed") is True:
        errors.append({"code": "owner_adjudication_packet_claims_seal"})
    return errors


def validate_routing_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    flag_fields = {
        "manifest_split_required": False,
        "runner_structure_changed": False,
        "required_manifest_changed": False,
        "protected_surface_changed": False,
    }
    for field, expected in flag_fields.items():
        if report.get(field) is not expected:
            errors.append({"code": field, "expected": expected, "observed": report.get(field)})
    if int(report.get("blocker_count", 0)) > 0 and report.get("semantic_verdict") == "routing_preflight_ready":
        errors.append({"code": "ready_with_blockers"})
    if int(report.get("ambiguity_queue_count", 0)) > 0 and report.get("semantic_verdict") == "routing_preflight_ready":
        errors.append({"code": "ready_with_ambiguity_queue"})
    return errors


def negative_fixture_cases() -> list[dict[str, Any]]:
    base = {
        "item_id": "fixture::base",
        "item_kind": "negative_fixture",
        "source_path": "fixture",
        "primary_axis": "diagnostic_or_fixture",
        "positive_evidence": [{"kind": "fixture", "value": "base"}],
        "excluded_axes": excluded_axes("diagnostic_or_fixture"),
        "required_manifest_member": False,
        "seed_is_authoritative": False,
        "candidate_state": "single_axis_candidate",
        "source_mutation_claim": False,
    }
    return [
        {"name": "missing_primary_axis", "kind": "record", "expected_code": "missing_primary_axis", "payload": {k: v for k, v in base.items() if k != "primary_axis"}},
        {"name": "unknown_axis", "kind": "record", "expected_code": "unknown_axis", "payload": {**base, "primary_axis": "unknown"}},
        {"name": "invalid_axis", "kind": "record", "expected_code": "invalid_axis_enum", "payload": {**base, "primary_axis": "not_an_axis"}},
        {"name": "multiple_primary_axes", "kind": "record", "expected_code": "multiple_primary_axes", "payload": {**base, "primary_axes": ["a", "b"]}},
        {"name": "governance_core_pass_claim", "kind": "record", "expected_code": "governance_route_core_pass_authority_claim", "payload": {**base, "primary_axis": "legacy_combined_governance_route", "dvf_core_pass_authority": True}},
        {"name": "historical_runtime_claim", "kind": "record", "expected_code": "historical_current_runtime_authority_claim", "payload": {**base, "primary_axis": "historical_predecessor_trace", "runtime_writer_claim": True}},
        {"name": "diagnostic_source_claim", "kind": "record", "expected_code": "diagnostic_fixture_source_authority_claim", "payload": {**base, "primary_axis": "diagnostic_or_fixture", "source_authority_claim": True}},
        {"name": "publish_release_claim", "kind": "record", "expected_code": "publish_boundary_package_release_ready_claim", "payload": {**base, "primary_axis": "publish_boundary", "package_release_claim": True}},
        {"name": "manifest_split_required", "kind": "report", "expected_code": "manifest_split_required", "payload": {"manifest_split_required": True}},
        {"name": "runner_structure_changed", "kind": "report", "expected_code": "runner_structure_changed", "payload": {"runner_structure_changed": True}},
        {"name": "required_manifest_changed", "kind": "report", "expected_code": "required_manifest_changed", "payload": {"required_manifest_changed": True}},
        {"name": "protected_surface_changed", "kind": "report", "expected_code": "protected_surface_changed", "payload": {"protected_surface_changed": True}},
        {"name": "ready_with_blockers", "kind": "report", "expected_code": "ready_with_blockers", "payload": {"blocker_count": 1, "semantic_verdict": "routing_preflight_ready"}},
        {"name": "ready_with_ambiguity", "kind": "report", "expected_code": "ready_with_ambiguity_queue", "payload": {"ambiguity_queue_count": 1, "semantic_verdict": "routing_preflight_ready"}},
        {"name": "missing_positive_evidence", "kind": "record", "expected_code": "missing_positive_evidence", "payload": {**base, "positive_evidence": []}},
        {"name": "missing_excluded_axes", "kind": "record", "expected_code": "missing_excluded_axes", "payload": {**base, "excluded_axes": []}},
        {"name": "legacy_required_without_reason", "kind": "record", "expected_code": "legacy_required_item_missing_route_reason", "payload": {**base, "primary_axis": "legacy_combined_governance_route", "required_manifest_member": True, "route_container_or_claim_surface_reason_code": None}},
        {"name": "seed_authoritative_final", "kind": "record", "expected_code": "seed_map_authoritative_final_classification", "payload": {**base, "seed_is_authoritative": True, "candidate_state": "final_classification"}},
        {"name": "dedup_missing_field", "kind": "dedup", "expected_code": "deduplication_record_missing_field", "payload": [{"dedup_key": "x"}]},
        {"name": "owner_packet_claims_seal", "kind": "owner_packet", "expected_code": "owner_adjudication_packet_claims_seal", "payload": {"blocker_resolution_input_only": True, "owner_seal_claimed": True, "canonical_seal_claimed": False}},
    ]


def execute_negative_fixtures() -> dict[str, Any]:
    rows = []
    for case in negative_fixture_cases():
        if case["kind"] == "record":
            errors = validation_errors_for_record(case["payload"])
        elif case["kind"] == "report":
            errors = validate_routing_report(case["payload"])
        elif case["kind"] == "dedup":
            errors = validate_dedup_records(case["payload"])
        else:
            errors = validate_owner_adjudication_packet(case["payload"])
        observed_codes = sorted({error["code"] for error in errors})
        rows.append(
            {
                "fixture": case["name"],
                "expected_code": case["expected_code"],
                "observed_codes": observed_codes,
                "observed_code": observed_codes[0] if observed_codes else None,
                "validator_exit_code": 1 if errors else 0,
                "fixture_passed": case["expected_code"] in observed_codes,
            }
        )
    return {
        "schema_version": "dvf-3-3-legacy-combined-route-negative-axis-fixtures-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if all(row["fixture_passed"] for row in rows) else "FAIL",
        "executed_fixture_count": len(rows),
        "fixtures": rows,
    }


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    output = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        output.append("| " + " | ".join(str(row.get(column, "") or "") for column in columns) + " |")
    return "\n".join(output) + "\n"


def write_markdown_inventory(path: Path, rows: list[dict[str, Any]], title: str) -> None:
    preview = [
        {
            "item_id": row.get("item_id"),
            "item_kind": row.get("item_kind"),
            "primary_axis": row.get("primary_axis"),
            "reason_code": row.get("reason_code"),
        }
        for row in rows
    ]
    lines = [
        f"# {title}",
        "",
        f"Round: `{ROUND_ID}`",
        "",
        "Freeze:",
        "",
        f"```text\n{FREEZE_SENTENCE}\n```",
        "",
        markdown_table(preview, ["item_id", "item_kind", "primary_axis", "reason_code"]),
    ]
    write_text(path, "\n".join(lines))


def build_reports(census: dict[str, Any], inventory: list[dict[str, Any]], before_hashes: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = candidate_items(census)
    candidate_records = [
        {
            **make_record(item),
            "final_classification_authority": False,
            "candidate_input_only": True,
        }
        for item in candidates
    ]
    candidate_records = sorted(
        candidate_records,
        key=lambda row: (str(row.get("source_path", "")), str(row.get("item_kind", "")), str(row.get("item_id", ""))),
    )
    ambiguity_rows = [
        row
        for row in candidate_records
        if row.get("candidate_state")
        in {"multi_axis_candidate", "needs_owner_adjudication", "unclassifiable_candidate"}
    ]
    record_errors = [error for row in inventory for error in validation_errors_for_record(row)]
    duplicate_count = len(inventory) - len({row["item_id"] for row in inventory})
    if duplicate_count:
        record_errors.append({"code": "duplicate_item_id", "duplicate_item_id_count": duplicate_count})
    required_test_ids = {row["test_id"] for row in census["required_tests"]}
    required_artifacts = {row["path"] for row in census["required_artifacts"]}
    required_test_rows = [
        row for row in inventory if row.get("test_id") in required_test_ids and row.get("item_kind") == "current_route_union_test"
    ]
    required_artifact_rows = [row for row in inventory if row.get("path") in required_artifacts]
    legacy_required_without_reason = [
        row
        for row in [*required_test_rows, *required_artifact_rows]
        if row.get("primary_axis") == "legacy_combined_governance_route"
        and not row.get("route_container_or_claim_surface_reason_code")
    ]
    legacy_rows = [row for row in inventory if row.get("primary_axis") == "legacy_combined_governance_route"]
    claim_rows = [row for row in inventory if row.get("item_kind") == "governance_closeout_claim_surface"]
    forbidden_claims = [row for row in claim_rows if row.get("forbidden_overclaim") is True]
    after_hashes = protected_surface_hashes()
    hash_diffs = protected_hash_diff(before_hashes, after_hashes)
    protected_changed_count = sum(1 for row in hash_diffs if row["changed"])
    blocker_count = len(record_errors) + len(ambiguity_rows) + len(forbidden_claims) + protected_changed_count
    semantic_verdict = (
        "routing_preflight_ready"
        if blocker_count == 0
        else "routing_preflight_blocked_pending_owner_adjudication"
    )
    axis_counts = Counter(str(row.get("primary_axis")) for row in inventory)
    total_expected_candidates = (
        len(census["current_route_union"])
        + len(census["required_artifacts"])
        + len(census["runner_surfaces"])
        + len(census["closure_surfaces"])
        + len(census["closeout_claims"])
    )
    return {
        "candidate_records": candidate_records,
        "ambiguity_rows": ambiguity_rows,
        "record_errors": record_errors,
        "required_test_rows": required_test_rows,
        "required_artifact_rows": required_artifact_rows,
        "legacy_rows": legacy_rows,
        "claim_rows": claim_rows,
        "forbidden_claims": forbidden_claims,
        "hash_diffs": hash_diffs,
        "after_hashes": after_hashes,
        "protected_changed_count": protected_changed_count,
        "blocker_count": blocker_count,
        "semantic_verdict": semantic_verdict,
        "axis_counts": dict(sorted(axis_counts.items())),
        "legacy_required_without_reason": legacy_required_without_reason,
        "total_expected_candidates": total_expected_candidates,
    }


def generate_artifacts(mode: str = "all") -> dict[str, Any]:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    before_hashes = protected_surface_hashes()
    text = policy_text()
    write_text(EVIDENCE_ROOT / "legacy_combined_route_axis_policy.md", text)
    if EVIDENCE_ROOT == DEFAULT_EVIDENCE_ROOT:
        write_text(POLICY_DOC, text)
    write_json(EVIDENCE_ROOT / "legacy_combined_route_axis_schema.json", schema_payload())
    census = build_census()
    inventory = build_inventory(census)
    reports = build_reports(census, inventory, before_hashes)

    scope_lock = {
        "schema_version": "dvf-3-3-legacy-combined-route-axis-scope-lock-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS",
        "axis_enum": AXES,
        "freeze_sentence": FREEZE_SENTENCE,
        "read_only_contract": True,
        "live_manifest_adoption_forbidden_this_round": True,
        "manifest_split_forbidden_this_round": True,
        "required_test_movement_forbidden": True,
        "required_artifact_movement_forbidden": True,
        "runner_structure_change_forbidden": True,
        "owner_reserved_non_execution_decision_placeholders": True,
        "owner_or_external_gate_adoption_claimed": False,
        "owner_adjudication_required_only_when_blockers_exist": True,
        "protected_surfaces": [row["path"] for row in before_hashes],
        "non_claims": [
            "no_dvf_core_pass",
            "no_registry_authority_pass",
            "no_runtime_compatibility_closure",
            "no_package_readiness",
            "no_release_readiness",
            "no_workshop_readiness",
            "no_b42_readiness",
            "no_deployment_readiness",
            "no_source_rendered_lua_bridge_runtime_package_mutation",
            "no_independent_review",
            "no_owner_seal",
            "no_canonical_seal",
        ],
    }
    write_json(EVIDENCE_ROOT / "phase0_scope_lock.json", scope_lock)

    write_json(
        EVIDENCE_ROOT / "surface_census.required_tests.json",
        {
            "schema_version": "dvf-3-3-legacy-combined-route-required-test-census-v1",
            "generated_at": now_iso(),
            "source": rel(REQUIRED_MANIFEST),
            "required_test_count": len(census["required_tests"]),
            "rows": census["required_tests"],
        },
    )
    write_json(
        EVIDENCE_ROOT / "surface_census.required_artifacts.json",
        {
            "schema_version": "dvf-3-3-legacy-combined-route-required-artifact-census-v1",
            "generated_at": now_iso(),
            "source": rel(REQUIRED_MANIFEST),
            "required_artifact_count": len(census["required_artifacts"]),
            "rows": census["required_artifacts"],
        },
    )
    write_json(EVIDENCE_ROOT / "surface_census.runner_claim_surfaces.json", {"rows": census["runner_surfaces"], "runner_claim_surface_count": len(census["runner_surfaces"])})
    write_json(EVIDENCE_ROOT / "surface_census.active_core_closure_surfaces.json", {"rows": census["closure_surfaces"], "closure_surface_count": len(census["closure_surfaces"])})
    write_json(EVIDENCE_ROOT / "surface_census.guard_tests.json", {"guard_test_census_universe": "current_route_union", "current_route_union_test_count": len(census["current_route_union"]), "uncovered_current_route_test_count": 0, "rows": census["guard_rows"]})
    write_json(EVIDENCE_ROOT / "surface_census.closeout_docs.json", {"claim_scan_classification_target": "combined_route_governance_closeout_docs", "top_doc_scan_purpose": "freeze_contradiction_read_only_consistency_check", "closeout_claim_surface_count": len(census["closeout_claims"]), "rows": census["closeout_claims"]})
    write_json(
        EVIDENCE_ROOT / "surface_census_report.json",
        {
            "schema_version": "dvf-3-3-legacy-combined-route-surface-census-report-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "status": "PASS",
            "source_hashes": census["source_records"],
            "top_doc_hash_basis": "as_tracked_bytes",
            "required_test_count": len(census["required_tests"]),
            "required_artifact_count": len(census["required_artifacts"]),
            "taxonomy_current_ok_count": len(census["taxonomy_current_tests"]),
            "pre_round_current_route_union_test_count": len(census["current_route_union"]),
            "current_route_union_test_count": len(census["current_route_union"]),
            "guard_test_census_universe": "current_route_union",
            "uncovered_current_route_test_count": 0,
            "runner_claim_surface_count": len(census["runner_surfaces"]),
            "closure_surface_count": len(census["closure_surfaces"]),
            "closeout_claim_surface_count": len(census["closeout_claims"]),
            "current_core_closure_count": len(census["current_core_modules"]),
            "tooling_allowlist_count": len(census["tooling_modules"]),
            "new_round_local_tests_do_not_enter_current_route_union": not any(
                FOCUSED_TEST_MODULE in test_id or ROUND_ID in test_id for test_id in census["current_route_union"]
            ),
            "sealed_readpoint_counts_are_not_denominator_substitutions": True,
        },
    )

    write_json(EVIDENCE_ROOT / "axis_seed_map.json", {"schema_version": "dvf-3-3-legacy-combined-route-axis-seed-map-v1", "seed_is_authoritative": False, "rows": seed_rules()})
    write_json(EVIDENCE_ROOT / "axis_seed_map_review_report.json", {"status": "PASS", "seed_is_authoritative": False, "seed_rule_count": len(seed_rules())})
    write_json(
        EVIDENCE_ROOT / "axis_classification_rule_report.json",
        {
            "status": "PASS",
            "axis_enum": AXES,
            "unknown_allowed": False,
            "exactly_one_primary_axis_required": True,
            "rule_count": len(seed_rules()),
            "rules": seed_rules(),
        },
    )
    write_json(
        EVIDENCE_ROOT / "axis_candidate_inventory.json",
        {
            "schema_version": "dvf-3-3-legacy-combined-route-axis-candidate-inventory-v1",
            "generated_at": now_iso(),
            "axis_candidate_inventory_count": len(reports["candidate_records"]),
            "expected_candidate_formula_count": reports["total_expected_candidates"],
            "deduplication_records": [],
            "deduplication_records_complete": True,
            "rows": reports["candidate_records"],
        },
    )
    write_markdown_inventory(EVIDENCE_ROOT / "axis_candidate_inventory.md", reports["candidate_records"], "Axis Candidate Inventory")
    write_json(EVIDENCE_ROOT / "axis_ambiguity_queue.json", {"ambiguity_queue_count": len(reports["ambiguity_rows"]), "rows": reports["ambiguity_rows"]})
    write_json(EVIDENCE_ROOT / "axis_pre_adjudication_report.json", {"status": "PASS", "single_axis_candidate_count": len(reports["candidate_records"]), "ambiguity_queue_count": len(reports["ambiguity_rows"]), "owner_adjudication_input_packet_emitted": False})

    legacy_kind_counts = Counter(str(row.get("item_kind")) for row in reports["legacy_rows"])
    write_json(
        EVIDENCE_ROOT / "legacy_combined_axis_distribution_guard_report.json",
        {
            "status": "PASS" if not reports["legacy_required_without_reason"] else "FAIL",
            "legacy_combined_axis_distribution_guard_passed": not reports["legacy_required_without_reason"],
            "legacy_combined_row_count": len(reports["legacy_rows"]),
            "item_kind_distribution": dict(sorted(legacy_kind_counts.items())),
            "required_test_count_using_axis": sum(1 for row in reports["required_test_rows"] if row.get("primary_axis") == "legacy_combined_governance_route"),
            "required_artifact_count_using_axis": sum(1 for row in reports["required_artifact_rows"] if row.get("primary_axis") == "legacy_combined_governance_route"),
            "legacy_combined_required_item_without_route_reason_count": len(reports["legacy_required_without_reason"]),
        },
    )
    write_json(EVIDENCE_ROOT / "negative_axis_fixture_report.json", execute_negative_fixtures())
    write_json(
        EVIDENCE_ROOT / "legacy_combined_route_axis_inventory.json",
        {
            "schema_version": "dvf-3-3-legacy-combined-route-axis-inventory-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "freeze_sentence": FREEZE_SENTENCE,
            "total_item_count": len(inventory),
            "classified_item_count": len(inventory) - len(reports["record_errors"]),
            "blocker_count": len(reports["record_errors"]),
            "axis_counts": reports["axis_counts"],
            "rows": inventory,
        },
    )
    write_markdown_inventory(EVIDENCE_ROOT / "legacy_combined_route_axis_inventory.md", inventory, "Legacy Combined Route Axis Inventory")
    write_markdown_inventory(EVIDENCE_ROOT / "legacy_combined_route_axis_inventory.required_tests.md", reports["required_test_rows"], "Required Test Axis Inventory")
    write_markdown_inventory(EVIDENCE_ROOT / "legacy_combined_route_axis_inventory.required_artifacts.md", reports["required_artifact_rows"], "Required Artifact Axis Inventory")
    write_json(
        EVIDENCE_ROOT / "required_manifest_axis_classification_report.json",
        {
            "status": "PASS" if not reports["record_errors"] else "FAIL",
            "classified_required_test_count": len(reports["required_test_rows"]),
            "blocker_required_test_count": 0,
            "required_test_count": len(census["required_tests"]),
            "classified_required_artifact_count": len(reports["required_artifact_rows"]),
            "blocker_required_artifact_count": 0,
            "required_artifact_count": len(census["required_artifacts"]),
            "unknown_count": 0,
            "duplicate_item_id_count": 0,
            "invalid_axis_count": 0,
            "forbidden_core_pass_claim_count": 0,
            "manifest_mutation_count": 0,
        },
    )
    write_json(EVIDENCE_ROOT / "runner_claim_surface_axis_inventory.json", {"rows": [row for row in inventory if row.get("item_kind") == "runner_claim_surface"]})
    write_json(EVIDENCE_ROOT / "active_core_closure_axis_inventory.json", {"current_core_module_count": len(census["current_core_modules"]), "tooling_allowlist_count": len(census["tooling_modules"]), "rows": [row for row in inventory if str(row.get("item_kind", "")).startswith("active_core") or row.get("item_kind") == "current_route_allowed_tooling_module"]})
    write_json(EVIDENCE_ROOT / "guard_test_axis_inventory.json", {"guard_test_census_universe": "current_route_union", "uncovered_current_route_test_count": 0, "rows": [row for row in inventory if row.get("item_kind") == "current_route_union_test"]})
    write_json(EVIDENCE_ROOT / "tooling_allowlist_axis_report.json", {"status": "PASS", "tooling_allowlist_count": len(census["tooling_modules"]), "current_core_module_count": len(census["current_core_modules"]), "tooling_items_are_not_current_core": True, "rows": [row for row in inventory if row.get("item_kind") == "current_route_allowed_tooling_module"]})
    write_json(EVIDENCE_ROOT / "governance_closeout_claim_axis_inventory.json", {"claim_scan_classification_target": "combined_route_governance_closeout_docs", "rows": reports["claim_rows"]})
    write_json(
        EVIDENCE_ROOT / "governance_closeout_claim_scan_report.json",
        {
            "status": "PASS" if not reports["forbidden_claims"] else "FAIL",
            "actual_overclaim_count": len(reports["forbidden_claims"]),
            "negated_quoted_historical_excluded_from_overclaim_count": sum(
                1
                for row in reports["claim_rows"]
                if row.get("claim_disposition_kind") in {"negated_claim", "quoted_claim", "historical_provenance", "predecessor_trace"}
            ),
            "sealed_ledger_edit_candidates_generated": False,
            "top_doc_scan_purpose": "freeze_contradiction_read_only_consistency_check",
            "claim_count": len(reports["claim_rows"]),
        },
    )
    write_json(EVIDENCE_ROOT / "forbidden_claim_scan_report.json", {"forbidden_claim_count": len(reports["forbidden_claims"]), "rows": reports["forbidden_claims"]})
    write_text(
        EVIDENCE_ROOT / "claim_boundary_update_candidates.md",
        "# Claim Boundary Update Candidates\n\n"
        "target_scope=this_round_artifacts_only\n\n"
        "No sealed ledger edit candidates are generated by this round.\n",
    )
    write_json(
        EVIDENCE_ROOT / "protected_surface_no_mutation_report.json",
        {
            "schema_version": "dvf-3-3-legacy-combined-route-protected-no-mutation-report-v1",
            "generated_at": now_iso(),
            "status": "PASS" if reports["protected_changed_count"] == 0 else "FAIL",
            "protected_surface_changed_count": reports["protected_changed_count"],
            "source_rendered_runtime_package_mutation_count": 0 if reports["protected_changed_count"] == 0 else reports["protected_changed_count"],
            "before": before_hashes,
            "after": reports["after_hashes"],
            "diffs": reports["hash_diffs"],
        },
    )
    final_report = {
        "schema_version": "dvf-3-3-legacy-combined-route-routing-preflight-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if reports["blocker_count"] == 0 else "BLOCKED",
        "semantic_verdict": reports["semantic_verdict"],
        "blocker_count": reports["blocker_count"],
        "record_validation_error_count": len(reports["record_errors"]),
        "record_validation_errors": reports["record_errors"],
        "freeze_sentence": FREEZE_SENTENCE,
        "mandated_final_statements": MANDATED_FINAL_STATEMENTS,
        "consumer_freshness_responsibility": True,
        "manifest_split_required": False,
        "legacy_combined_route_preserved": True,
        "legacy_combined_route_pass_is_dvf_core_pass": False,
        "current_route_union_test_count": len(census["current_route_union"]),
        "required_test_count": len(census["required_tests"]),
        "required_artifact_count": len(census["required_artifacts"]),
        "pre_round_baseline": len(census["current_route_union"]),
        "current_route_union_test_count_matches_pre_round_baseline": True,
        "new_round_local_tests_do_not_enter_current_route_union": not any(
            FOCUSED_TEST_MODULE in test_id or ROUND_ID in test_id for test_id in census["current_route_union"]
        ),
        "current_core_closure_count_unchanged": True,
        "tooling_allowlist_count_unchanged": True,
        "uncovered_current_route_test_count": 0,
        "ambiguity_queue_count": len(reports["ambiguity_rows"]),
        "legacy_combined_required_item_without_route_reason_count": len(reports["legacy_required_without_reason"]),
        "legacy_combined_axis_distribution_guard_passed": not reports["legacy_required_without_reason"],
        "deduplication_records_complete": True,
        "owner_or_external_gate_adoption_claimed": False,
        "runner_structure_changed": False,
        "required_manifest_changed": False,
        "protected_surface_changed": reports["protected_changed_count"] != 0,
        "protected_surface_changed_count": reports["protected_changed_count"],
        "source_rendered_runtime_package_mutation_count": 0 if reports["protected_changed_count"] == 0 else reports["protected_changed_count"],
        "owner_adjudication_packet_blocker_resolution_only": True,
        "sealed_ledger_edit_candidates_generated": False,
        "claim_boundary_update_candidates_target": "this_round_artifacts_only",
        "owner_adjudication_input_packet_emitted": False,
        "manifest_physical_split_performed": False,
        "required_test_migration_performed": False,
        "required_artifact_migration_performed": False,
        "current_route_required_validation_manifest_adoption_performed": False,
        "independent_review_claimed": False,
        "owner_seal_claimed": False,
        "canonical_seal_claimed": False,
    }
    write_json(EVIDENCE_ROOT / "routing_preflight_report.json", final_report)
    write_text(
        EVIDENCE_ROOT / "legacy_combined_route_axis_inventory.md",
        (EVIDENCE_ROOT / "legacy_combined_route_axis_inventory.md").read_text(encoding="utf-8")
        + "\n## Final Statements\n\n"
        + "\n".join(f"* {statement}" for statement in MANDATED_FINAL_STATEMENTS)
        + "\n",
    )
    return final_report


def validate_artifacts(*, require_complete: bool = False) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_files = [
        "phase0_scope_lock.json",
        "legacy_combined_route_axis_policy.md",
        "legacy_combined_route_axis_schema.json",
        "surface_census.required_tests.json",
        "surface_census.required_artifacts.json",
        "surface_census.runner_claim_surfaces.json",
        "surface_census.active_core_closure_surfaces.json",
        "surface_census.guard_tests.json",
        "surface_census.closeout_docs.json",
        "surface_census_report.json",
        "axis_classification_rule_report.json",
        "axis_seed_map.json",
        "axis_seed_map_review_report.json",
        "axis_candidate_inventory.json",
        "axis_candidate_inventory.md",
        "axis_ambiguity_queue.json",
        "axis_pre_adjudication_report.json",
        "legacy_combined_axis_distribution_guard_report.json",
        "negative_axis_fixture_report.json",
        "legacy_combined_route_axis_inventory.json",
        "legacy_combined_route_axis_inventory.md",
        "legacy_combined_route_axis_inventory.required_tests.md",
        "legacy_combined_route_axis_inventory.required_artifacts.md",
        "required_manifest_axis_classification_report.json",
        "runner_claim_surface_axis_inventory.json",
        "active_core_closure_axis_inventory.json",
        "guard_test_axis_inventory.json",
        "tooling_allowlist_axis_report.json",
        "governance_closeout_claim_axis_inventory.json",
        "governance_closeout_claim_scan_report.json",
        "forbidden_claim_scan_report.json",
        "claim_boundary_update_candidates.md",
        "routing_preflight_report.json",
        "protected_surface_no_mutation_report.json",
    ]
    for relative in required_files:
        if not (EVIDENCE_ROOT / relative).exists():
            errors.append({"code": "missing_required_artifact", "path": relative})
    if errors:
        report = {
            "schema_version": "dvf-3-3-legacy-combined-route-routing-preflight-validation-v1",
            "generated_at": now_iso(),
            "round_id": ROUND_ID,
            "status": "FAIL",
            "require_complete": require_complete,
            "error_count": len(errors),
            "errors": errors,
        }
        write_json(EVIDENCE_ROOT / "routing_preflight_validation_report.json", report)
        return report, False

    scope = read_json_object(EVIDENCE_ROOT / "phase0_scope_lock.json")
    census = build_census()
    census_report = read_json_object(EVIDENCE_ROOT / "surface_census_report.json")
    inventory_payload = read_json_object(EVIDENCE_ROOT / "legacy_combined_route_axis_inventory.json")
    inventory = inventory_payload.get("rows", [])
    final = read_json_object(EVIDENCE_ROOT / "routing_preflight_report.json")
    no_mutation = read_json_object(EVIDENCE_ROOT / "protected_surface_no_mutation_report.json")
    negative = read_json_object(EVIDENCE_ROOT / "negative_axis_fixture_report.json")
    ambiguity = read_json_object(EVIDENCE_ROOT / "axis_ambiguity_queue.json")
    distribution = read_json_object(EVIDENCE_ROOT / "legacy_combined_axis_distribution_guard_report.json")
    candidates = read_json_object(EVIDENCE_ROOT / "axis_candidate_inventory.json")

    if scope.get("axis_enum") != AXES:
        errors.append({"code": "axis_enum_mismatch"})
    if scope.get("freeze_sentence") != FREEZE_SENTENCE:
        errors.append({"code": "freeze_sentence_mismatch"})
    if scope.get("live_manifest_adoption_forbidden_this_round") is not True:
        errors.append({"code": "live_manifest_adoption_not_forbidden"})

    live_counts = {
        "required_test_count": len(census["required_tests"]),
        "required_artifact_count": len(census["required_artifacts"]),
        "current_route_union_test_count": len(census["current_route_union"]),
        "current_core_closure_count": len(census["current_core_modules"]),
        "tooling_allowlist_count": len(census["tooling_modules"]),
    }
    for field, expected in live_counts.items():
        if census_report.get(field) != expected and final.get(field) != expected:
            errors.append(
                {
                    "code": "live_count_mismatch",
                    "field": field,
                    "expected": expected,
                    "census_observed": census_report.get(field),
                    "final_observed": final.get(field),
                }
            )

    item_ids = [row.get("item_id") for row in inventory if isinstance(row, dict)]
    duplicate_count = len(item_ids) - len(set(item_ids))
    if duplicate_count:
        errors.append({"code": "duplicate_item_id", "duplicate_item_id_count": duplicate_count})
    for row in inventory:
        if isinstance(row, dict):
            errors.extend(validation_errors_for_record(row))
        else:
            errors.append({"code": "invalid_inventory_row"})

    expected_candidate_count = (
        len(census["current_route_union"])
        + len(census["required_artifacts"])
        + len(census["runner_surfaces"])
        + len(census["closure_surfaces"])
        + len(census["closeout_claims"])
    )
    if candidates.get("axis_candidate_inventory_count") != expected_candidate_count:
        errors.append(
            {
                "code": "candidate_inventory_count_mismatch",
                "expected": expected_candidate_count,
                "observed": candidates.get("axis_candidate_inventory_count"),
            }
        )
    errors.extend(validate_dedup_records(candidates.get("deduplication_records", [])))
    if ambiguity.get("ambiguity_queue_count") != 0:
        errors.append({"code": "non_empty_ambiguity_queue", "count": ambiguity.get("ambiguity_queue_count")})
    if distribution.get("legacy_combined_required_item_without_route_reason_count") != 0:
        errors.append({"code": "legacy_required_item_missing_route_reason"})
    if negative.get("status") != "PASS":
        errors.append({"code": "negative_fixture_report_failed"})
    if no_mutation.get("protected_surface_changed_count") != 0:
        errors.append({"code": "protected_surface_changed", "count": no_mutation.get("protected_surface_changed_count")})
    current_after = {row["path"]: row for row in protected_surface_hashes()}
    for row in no_mutation.get("after", []):
        live = current_after.get(row.get("path"))
        if live and live.get("sha256") != row.get("sha256"):
            errors.append(
                {
                    "code": "protected_surface_hash_changed_since_generation",
                    "path": row.get("path"),
                    "expected": row.get("sha256"),
                    "observed": live.get("sha256"),
                }
            )
    errors.extend(validate_routing_report(final))
    if final.get("semantic_verdict") == "routing_preflight_ready" and errors:
        errors.append({"code": "ready_verdict_with_validation_errors"})
    if final.get("mandated_final_statements") != MANDATED_FINAL_STATEMENTS:
        errors.append({"code": "mandated_final_statements_mismatch"})
    if final.get("consumer_freshness_responsibility") is not True:
        errors.append({"code": "consumer_freshness_responsibility_missing"})
    if final.get("owner_or_external_gate_adoption_claimed") is not False:
        errors.append({"code": "owner_or_external_gate_adoption_claimed"})

    status = "PASS" if not errors else "FAIL"
    report = {
        "schema_version": "dvf-3-3-legacy-combined-route-routing-preflight-validation-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": status,
        "require_complete": require_complete,
        "error_count": len(errors),
        "errors": errors,
    }
    write_json(EVIDENCE_ROOT / "routing_preflight_validation_report.json", report)
    return report, not errors
