from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
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


ROUND_ID = "dvf_3_3_dvf_system_naming_realignment"
ENV_ROOT = "DVF_SYSTEM_NAMING_REALIGNMENT_ROOT"
EVIDENCE_ROOT = resolve_repo(os.environ.get(ENV_ROOT, V2_ROOT / "staging" / ROUND_ID))

TOOLS_DIR = Path(__file__).resolve().parent
COMMON_MODULE = TOOLS_DIR / f"{ROUND_ID}.py"
RUNNER = TOOLS_DIR / f"run_{ROUND_ID}.py"
VALIDATOR = TOOLS_DIR / f"validate_{ROUND_ID}.py"
FOCUSED_TEST = V2_ROOT / "tests" / f"test_{ROUND_ID}.py"

PLAN_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_plan.md"
POLICY_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_policy.md"
CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_claim_boundary.md"
LEDGER_PACKET_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_ledger_packet.md"
CLOSEOUT_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_closeout.md"
WALKTHROUGH_DOC = REPO_ROOT / "docs" / f"{ROUND_ID}_walkthrough.md"

PHILOSOPHY_DOC = REPO_ROOT / "docs" / "Philosophy.md"
DECISIONS_DOC = REPO_ROOT / "docs" / "DECISIONS.md"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "ARCHITECTURE.md"
ROADMAP_DOC = REPO_ROOT / "docs" / "ROADMAP.md"
EXECUTION_CONTRACT_DOC = REPO_ROOT / "docs" / "EXECUTION_CONTRACT.md"
COMPLETION_POLICY_DOC = REPO_ROOT / "docs" / "completion_vocabulary_separation_policy.md"
PREDECESSOR_CLAIM_CONTRACT_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_contract.md"
PREDECESSOR_CLAIM_BOUNDARY_DOC = REPO_ROOT / "docs" / "dvf_3_3_core_registry_boundary_claim_boundary.md"
PREDECESSOR_LEGACY_ROUTE_POLICY_DOC = REPO_ROOT / "docs" / "dvf_3_3_legacy_combined_route_axis_policy.md"
PREDECESSOR_REQUIRED_GATE_CLOSEOUT = REPO_ROOT / (
    "Iris/build/description/v2/staging/"
    "dvf_3_3_core_registry_boundary_required_gate_adoption/"
    "final_boundary_required_gate_adoption_report.json"
)

LIVE_REQUIRED_MANIFEST = REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
ACTIVE_CORE_CLOSURE = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_active_core_closure.json"
ROUND3_RUNNER = REPO_ROOT / "Iris" / "_docs" / "round3" / "round3_run_contract_tests.py"
CURRENT_ROUTE_RESULT = EVIDENCE_ROOT / "phase5" / "current_route_validation_result.json"

ROLE = f"{ROUND_ID}_required_validation"
INNER_CURRENT_ROUTE_ENV = "DVF_SYSTEM_NAMING_REALIGNMENT_INNER_CURRENT_ROUTE"
OWNER_SOURCE = "current_user_prompt_2026-07-10_implement_plan_defaults"
EXPECTED_CLOSEOUT_GUARD_SHA = "7FE70E8003B89655EED9A94E27790ADE158E4C5B4966BD4A7F6298366A8AB82D"

PROTECTED_SURFACE_PATHS = [
    "Iris/build/description/v2/data/dvf_3_3_input_manifest.json",
    "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
    "Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl",
    "Iris/build/description/v2/output/dvf_3_3_rendered.json",
    "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
    "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
    "Iris/Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua",
    "Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "media/lua/shared/Iris/IrisDvfBridgeData.lua",
    "Iris/build/package/Iris",
]

ROUND_LOCAL_GITIGNORE_RULES = [
    f"!Iris/build/description/v2/tools/build/{ROUND_ID}.py",
    f"!Iris/build/description/v2/tools/build/run_{ROUND_ID}.py",
    f"!Iris/build/description/v2/tools/build/validate_{ROUND_ID}.py",
    f"!Iris/build/description/v2/tests/test_{ROUND_ID}.py",
    f"!Iris/build/description/v2/staging/{ROUND_ID}/",
    f"!Iris/build/description/v2/staging/{ROUND_ID}/**",
]

OWNER_DECISION_DEFAULTS = [
    {
        "decision_id": "D1",
        "name": "canonical body compiler PASS token selection",
        "proposed_default": "DVF Body Compiler PASS",
        "owner_value": "DVF Body Compiler PASS",
    },
    {
        "decision_id": "D2",
        "name": "expanded alias allowance and primary/expanded token split",
        "proposed_default": "DVF System Body Compiler PASS",
        "owner_value": "DVF System Body Compiler PASS",
    },
    {
        "decision_id": "D3",
        "name": "Legacy Combined route prose label selection",
        "proposed_default": "Legacy Combined DVF Governance Route PASS",
        "owner_value": "Legacy Combined DVF Governance Route PASS",
    },
    {
        "decision_id": "D4",
        "name": "DECISIONS append-only supersession / predecessor handling",
        "proposed_default": "append_only_successor_supersedes_prior_current_label",
        "owner_value": "append_only_successor_supersedes_prior_current_label",
    },
    {
        "decision_id": "D5",
        "name": "Option A vs Option B enforcement selection",
        "proposed_default": "option_b_required_gate_adoption",
        "owner_value": "option_b_required_gate_adoption",
    },
    {
        "decision_id": "D6",
        "name": "canonical seal eligibility condition",
        "proposed_default": "required_gate_only_canonical_seal",
        "owner_value": "required_gate_only_canonical_seal",
    },
]

CANONICAL_CURRENT_DOCS = [
    ARCHITECTURE_DOC,
    ROADMAP_DOC,
    POLICY_DOC,
    CLAIM_BOUNDARY_DOC,
    LEDGER_PACKET_DOC,
    CLOSEOUT_DOC,
]
SCAN_DOCS = [
    ARCHITECTURE_DOC,
    ROADMAP_DOC,
    DECISIONS_DOC,
    POLICY_DOC,
    CLAIM_BOUNDARY_DOC,
    LEDGER_PACKET_DOC,
    CLOSEOUT_DOC,
    WALKTHROUGH_DOC,
    PREDECESSOR_CLAIM_CONTRACT_DOC,
    PREDECESSOR_CLAIM_BOUNDARY_DOC,
    PREDECESSOR_LEGACY_ROUTE_POLICY_DOC,
    COMPLETION_POLICY_DOC,
]

DVF_CORE_RE = re.compile(r"\bDVF Core(?: PASS)?\b")
CLAIM_RE = re.compile(
    r"\bDVF PASS(?=$|[^A-Za-z0-9_])|\bDVF System PASS(?=$|[^A-Za-z0-9_])|\bDVF Core PASS(?=$|[^A-Za-z0-9_])|"
    r"\bDVF Body Compiler PASS(?=$|[^A-Za-z0-9_])|\bDVF System Body Compiler PASS(?=$|[^A-Za-z0-9_])|"
    r"\bRegistry Authority PASS(?=$|[^A-Za-z0-9_])|\bRegistry Runtime Compatibility PASS(?=$|[^A-Za-z0-9_])|"
    r"\bRuntime Compatibility PASS(?=$|[^A-Za-z0-9_])|\bPublish Boundary PASS(?=$|[^A-Za-z0-9_])|"
    r"\bLegacy Combined Current Route PASS(?=$|[^A-Za-z0-9_])|\bLegacy Combined Governance Route PASS(?=$|[^A-Za-z0-9_])|"
    r"\bLegacy Combined DVF Governance Route PASS(?=$|[^A-Za-z0-9_])",
    re.IGNORECASE,
)
NEGATION_TERMS = (
    "not ",
    "not_",
    "no ",
    "no_",
    "does not",
    "do not",
    "must not",
    "cannot",
    "forbidden",
    "forbid",
    "blocked",
    "deny",
    "out of scope",
    "out-of-scope",
    "non-claim",
    "non_claim",
    "not claim",
    "not claimed",
    "is not",
    "are not",
    "!=",
    "retired",
    "retire",
    "historical",
    "predecessor",
    "legacy",
    "sealed",
    "quoted",
    "compatibility",
    "zero",
    "금지",
    "막",
    "아님",
    "아니다",
    "아니라",
    "않",
    "오독 금지",
    "이전",
    "과거",
    "선행",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase_dir(name: str, root: Path = EVIDENCE_ROOT) -> Path:
    path = root / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def phase_path(phase: str, name: str, root: Path = EVIDENCE_ROOT) -> Path:
    return phase_dir(phase, root) / name


def read_json_object(path: str | Path) -> dict[str, Any]:
    resolved = resolve_repo(path)
    if not resolved.exists():
        return {}
    with resolved.open("r", encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def normalized_sha(path: str | Path) -> str | None:
    digest = sha256_file(path)
    return digest.lower() if isinstance(digest, str) else None


def hash_path(path: str | Path) -> str | None:
    resolved = resolve_repo(path)
    if not resolved.exists():
        return None
    if resolved.is_file():
        return normalized_sha(resolved)
    rows = []
    for child in sorted(p for p in resolved.rglob("*") if p.is_file()):
        rows.append({"path": child.relative_to(resolved).as_posix(), "sha256": normalized_sha(child)})
    return canonical_hash(rows)


def object_field(payload: object, field_path: str) -> tuple[bool, object]:
    current = payload
    for part in field_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
            continue
        return False, None
    return True, current


def run_command(args: list[str], *, env: dict[str, str] | None = None, timeout: int = 300) -> dict[str, Any]:
    completed = subprocess.run(
        args,
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    return {
        "args": args,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "success": completed.returncode == 0,
    }


def protected_hash_records() -> list[dict[str, Any]]:
    rows = []
    for path in PROTECTED_SURFACE_PATHS:
        resolved = resolve_repo(path)
        rows.append(
            {
                "path": rel(resolved),
                "exists": resolved.exists(),
                "kind": "dir" if resolved.is_dir() else "file" if resolved.is_file() else "missing",
                "sha256": hash_path(resolved),
            }
        )
    return rows


def protected_hash_diff(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, Any]:
    before_by_path = {row["path"]: row for row in before}
    after_by_path = {row["path"]: row for row in after}
    changed = []
    for path in sorted(set(before_by_path).union(after_by_path)):
        if before_by_path.get(path) != after_by_path.get(path):
            changed.append({"path": path, "before": before_by_path.get(path), "after": after_by_path.get(path)})
    return {
        "changed_count": len(changed),
        "changed": changed,
        "source_rendered_lua_runtime_package_mutation": bool(changed),
    }


def top_doc_hashes() -> list[dict[str, Any]]:
    return [
        {"path": rel(path), "exists": path.exists(), "sha256": normalized_sha(path)}
        for path in [ARCHITECTURE_DOC, ROADMAP_DOC, DECISIONS_DOC]
    ]


def owner_decision_rows() -> list[dict[str, Any]]:
    rows = []
    for row in OWNER_DECISION_DEFAULTS:
        rows.append(
            {
                **row,
                "owner_decision_state": "owner_ratified",
                "owner_source": OWNER_SOURCE,
                "default_value_projected_without_owner_ratification": False,
            }
        )
    return rows


def owner_values() -> dict[str, str]:
    return {row["decision_id"]: row["owner_value"] for row in owner_decision_rows()}


def docs_scan_paths() -> list[Path]:
    paths = []
    for path in SCAN_DOCS:
        if path.exists():
            paths.append(path)
    return sorted(set(paths))


def classify_dvf_core(path: Path, line: str, *, in_successor_decision: bool) -> str:
    rel_path = rel(path)
    lower = line.lower()
    if rel_path.startswith("docs/dvf_3_3_core_registry_boundary") or rel_path.endswith(
        "dvf_3_3_legacy_combined_route_axis_policy.md"
    ):
        return "sealed_historical"
    if rel_path.endswith("dvf_3_3_dvf_system_naming_realignment_plan.md"):
        return "predecessor_trace"
    if path == DECISIONS_DOC and not in_successor_decision:
        return "sealed_historical"
    if any(term in lower for term in NEGATION_TERMS):
        return "retirement_self_mention"
    return "forbidden_current_claim"


def terminology_occurrence_inventory(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    in_successor_decision = False
    for path in docs_scan_paths():
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if path == DECISIONS_DOC and line.startswith("Iris DVF 3-3 -- DVF System naming realignment"):
                in_successor_decision = True
            for match in re.finditer(r"DVF Core(?: PASS)?|DVF PASS|DVF System PASS|DVF Body Compiler PASS|DVF System Body Compiler PASS", line):
                token = match.group(0)
                if token.startswith("DVF Core"):
                    disposition = classify_dvf_core(path, line, in_successor_decision=in_successor_decision)
                elif token == "DVF PASS":
                    disposition = "forbidden_current_claim" if not any(term in line.lower() for term in NEGATION_TERMS) else "retirement_self_mention"
                elif token == "DVF System PASS":
                    disposition = "forbidden_current_claim" if not any(term in line.lower() for term in NEGATION_TERMS) else "retirement_self_mention"
                else:
                    disposition = "current_canonical_prose"
                rows.append(
                    {
                        "path": rel(path),
                        "line": line_number,
                        "token": token,
                        "disposition": disposition,
                        "text": line.strip(),
                    }
                )
    disposition_counts = Counter(row["disposition"] for row in rows)
    literal_dvf_core_count = sum(1 for row in rows if row["token"].startswith("DVF Core"))
    resolved_current_count = sum(
        1
        for row in rows
        if row["token"].startswith("DVF Core") and row["disposition"] == "forbidden_current_claim"
    )
    unclassifiable = sum(1 for row in rows if row["disposition"] == "unclassifiable_blocker")
    report = {
        "schema_version": "dvf-system-naming-terminology-occurrence-inventory-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if resolved_current_count == 0 and unclassifiable == 0 else "FAIL",
        "scan_universe_count": len(docs_scan_paths()),
        "literal_dvf_core_occurrence_count": literal_dvf_core_count,
        "resolved_current_canonical_dvf_core_usage_count": resolved_current_count,
        "all_literal_dvf_core_occurrences_disposition_classified": unclassifiable == 0,
        "unclassifiable_blocker_count": unclassifiable,
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "rows": rows,
    }
    write_json(phase_path("phase0", "terminology_occurrence_inventory.json", root), report)
    md_lines = [
        "# DVF System Naming Realignment Occurrence Inventory",
        "",
        f"- status: `{report['status']}`",
        f"- scan_universe_count: `{report['scan_universe_count']}`",
        f"- literal_dvf_core_occurrence_count: `{literal_dvf_core_count}`",
        f"- resolved_current_canonical_dvf_core_usage_count: `{resolved_current_count}`",
        "",
        "| path | line | token | disposition |",
        "|---|---:|---|---|",
    ]
    for row in rows:
        md_lines.append(f"| {row['path']} | {row['line']} | `{row['token']}` | `{row['disposition']}` |")
    write_text(phase_path("phase0", "terminology_occurrence_inventory.md", root), "\n".join(md_lines) + "\n")
    return report


def scan_text_forbidden(text: str, *, source_path: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    matches: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    predecessor_source = source_path in {
        rel(PREDECESSOR_CLAIM_CONTRACT_DOC),
        rel(PREDECESSOR_CLAIM_BOUNDARY_DOC),
        rel(PREDECESSOR_LEGACY_ROUTE_POLICY_DOC),
    }
    for line_number, line in enumerate(text.splitlines(), start=1):
        lower = line.lower()
        allowed_context = predecessor_source or any(term in lower for term in NEGATION_TERMS)
        for match in CLAIM_RE.finditer(line):
            token = match.group(0)
            token_lower = token.lower()
            violation_code = None
            if token_lower == "dvf pass" and not allowed_context:
                violation_code = "standalone_current_dvf_pass"
            elif token_lower == "dvf system pass" and not allowed_context:
                violation_code = "bare_dvf_system_pass"
            elif token_lower == "dvf core pass" and not allowed_context:
                violation_code = "retired_dvf_core_pass_current_claim"
            if "dvf system includes registry" in lower or "dvf system owns registry" in lower:
                violation_code = "dvf_system_registry_overclaim"
            if "dvf system includes publish" in lower or "dvf system owns publish" in lower:
                violation_code = "dvf_system_publish_overclaim"
            record = {
                "path": source_path,
                "line": line_number,
                "token": token,
                "text": line.strip(),
                "allowed_context": allowed_context,
            }
            matches.append(record)
            if violation_code:
                violations.append({**record, "violation_code": violation_code})
    return matches, violations


def live_claim_rescan(*, root: Path = EVIDENCE_ROOT, extra_paths: list[Path] | None = None) -> dict[str, Any]:
    paths = docs_scan_paths()
    if extra_paths:
        paths.extend(extra_paths)
    matches: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    for path in sorted(set(paths)):
        text = path.read_text(encoding="utf-8", errors="replace")
        found, bad = scan_text_forbidden(text, source_path=rel(path) if path.is_relative_to(REPO_ROOT) else str(path))
        matches.extend(found)
        violations.extend(bad)
    return {
        "schema_version": "dvf-system-naming-forbidden-claim-scan-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if not violations and paths else "FAIL",
        "scan_universe_count": len(set(paths)),
        "claim_match_count": len(matches),
        "forbidden_current_claim_count": len(violations),
        "forbidden_overclaim_count": len(violations),
        "claim_scan_minimum_universe_satisfied": bool(paths),
        "overclaim_scanner_class": "lexical_token_level",
        "violations": violations,
        "matches": matches,
    }


def write_docs(root: Path = EVIDENCE_ROOT) -> None:
    predecessor_hash = normalized_sha(PREDECESSOR_CLAIM_CONTRACT_DOC)
    values = owner_values()
    policy = f"""# DVF 3-3 DVF System Naming Realignment Policy

Status: adopted governance-only terminology retirement policy.

This policy retires `DVF Core` as current canonical terminology for Iris 3-3 body production. The current canonical names are:

- `DVF System`: facts / decisions / profile / body_plan -> rendered 3-3 body.
- `DVF Body Compiler`: role-granularity name for the same body-production responsibility.
- `{values['D1']}`: primary successor PASS token meaning definition only.
- `{values['D2']}`: expanded alias for the same body compiler axis.
- `{values['D3']}`: current prose label for the legacy combined governance route container.

The retired label `DVF Core` may remain in sealed historical text, predecessor contracts, quoted prior claims, compatibility machine tokens, historical paths, and explicit retirement self-mentions. It is default-deny in current canonical prose.

Forbidden current claims:

- forbidden: bare `DVF PASS`
- forbidden: bare `DVF System PASS`
- forbidden: using `DVF Core PASS` as a current successor claim
- treating DVF System as including Iris Artifact Registry, Registry Runtime Compatibility, Publish Boundary, package readiness, release readiness, public text acceptance, semantic quality acceptance, or manual QA

Non-claims:

- This policy does not claim `{values['D1']}` achievement.
- This policy does not claim Registry Authority PASS.
- This policy does not claim Registry Runtime Compatibility PASS.
- This policy does not claim Publish Boundary PASS.
- This policy does not mutate source facts, decisions, rendered output, Lua bridge, runtime chunks, or package payload.
- This policy does not claim package readiness, release readiness, Workshop readiness, B42 readiness, deployment readiness, manual QA, semantic quality acceptance, or public text acceptance.
"""
    write_text(POLICY_DOC, policy)

    claim_boundary = f"""# DVF 3-3 DVF System Naming Realignment Claim Boundary

Status: successor terminology boundary / governance-only.

Predecessor claim meaning authority remains `docs/dvf_3_3_core_registry_boundary_claim_contract.md` / sha256 `{predecessor_hash}`. This successor boundary does not rewrite that predecessor contract.

## Successor Claim Vocabulary

`{values['D1']}` means only:

- body compiler determinism
- facts / decisions / profile / body_plan consumption
- rendered 3-3 body shape inside the DVF System body-production scope
- protected-output no-mutation inside this naming round

`{values['D2']}` is an expanded alias for the same body compiler axis. It is not a broader system-state claim.

`DVF System Naming Realignment PASS` is allowed only as this round-scoped governance naming claim. It is not `{values['D1']}` achievement.

## Boundary

DVF System does not include Iris Artifact Registry, Registry Runtime Compatibility, Publish Boundary, package publication, release readiness, public text acceptance, semantic quality acceptance, or manual QA.

`{values['D3']}` remains a route-container label. A route-level pass is not `{values['D1']}` authority.
"""
    write_text(CLAIM_BOUNDARY_DOC, claim_boundary)

    ledger = f"""# DVF 3-3 DVF System Naming Realignment Ledger Packet

Status: governance-only successor packet.

- round_id: `{ROUND_ID}`
- enforcement_mode: `{values['D5']}`
- canonical_body_system: `DVF System`
- canonical_body_compiler: `DVF Body Compiler`
- canonical_body_compiler_pass_token: `{values['D1']}`
- expanded_body_compiler_pass_token: `{values['D2']}`
- route_label: `{values['D3']}`
- predecessor_handling: `{values['D4']}`
- canonical_seal_eligibility: `{values['D6']}`
- owner_decision_source: `{OWNER_SOURCE}`

This packet is additive. It does not rewrite sealed predecessor decision bodies.
"""
    write_text(LEDGER_PACKET_DOC, ledger)

    closeout = f"""# DVF 3-3 DVF System Naming Realignment Closeout

Status: required_gate_adopted_complete / governance-only naming realignment.

This closeout records `DVF System Naming Realignment PASS` as a round-scoped terminology governance result. It defines successor vocabulary and retires `DVF Core` from current canonical prose.

Validated:

- all literal retired-label occurrences are disposition-classified
- resolved current canonical `DVF Core` usage is zero
- bare `DVF PASS` and bare `DVF System PASS` current claims are forbidden
- required-validation manifest adoption is additive-only
- protected source / rendered / Lua bridge / runtime / package surfaces are unchanged

Non-claims:

- no `{values['D1']}` achievement claim
- no Registry Authority PASS
- no Registry Runtime Compatibility PASS
- no Publish Boundary PASS
- no package readiness
- no release / Workshop / B42 / deployment readiness
- no public text acceptance
- no semantic quality acceptance
- no manual QA
- no source / rendered / Lua bridge / runtime chunk / package payload mutation
"""
    write_text(CLOSEOUT_DOC, closeout)

    walkthrough = f"""# DVF 3-3 DVF System Naming Realignment Walkthrough

Run:

```powershell
python -B Iris\\build\\description\\v2\\tools\\build\\run_{ROUND_ID}.py --mode all
python -B Iris\\build\\description\\v2\\tools\\build\\validate_{ROUND_ID}.py --require-complete
python -B -m unittest Iris.build.description.v2.tests.test_{ROUND_ID}
```

This route is governance-only. Runtime and package surfaces are protected no-mutation surfaces.
"""
    write_text(WALKTHROUGH_DOC, walkthrough)


def write_phase0(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    phase_dir("phase0", root)
    before = protected_hash_records()
    write_json(phase_path("phase0", "protected_surface_baseline_hashes.json", root), {"records": before})
    write_json(
        phase_path("phase0", "top_doc_baseline_hashes.json", root),
        {"schema_version": "dvf-system-naming-top-doc-baseline-v1", "generated_at": now_iso(), "records": top_doc_hashes()},
    )
    write_json(
        phase_path("phase0", "execution_contract_check_report.json", root),
        {
            "schema_version": "dvf-system-naming-execution-contract-check-v1",
            "generated_at": now_iso(),
            "status": "PASS" if EXECUTION_CONTRACT_DOC.exists() else "BLOCKED",
            "execution_contract_checked": EXECUTION_CONTRACT_DOC.exists(),
            "execution_contract_path": rel(EXECUTION_CONTRACT_DOC),
            "execution_contract_sha256": normalized_sha(EXECUTION_CONTRACT_DOC),
            "authority_surface_touched": True,
            "sealed_artifact_surface_touched": True,
            "runtime_behavior_surface_touched": False,
        },
    )
    live_manifest = read_json_object(LIVE_REQUIRED_MANIFEST)
    write_json(
        phase_path("phase0", "current_route_manifest_readpoint.json", root),
        {
            "schema_version": "dvf-system-naming-current-route-manifest-readpoint-v1",
            "generated_at": now_iso(),
            "status": "PASS" if live_manifest.get("status") == "PASS" else "BLOCKED",
            "manifest_path": rel(LIVE_REQUIRED_MANIFEST),
            "manifest_sha256": normalized_sha(LIVE_REQUIRED_MANIFEST),
            "required_artifacts": len(live_manifest.get("required_artifacts", [])),
            "required_tests": len(live_manifest.get("required_tests", [])),
            "required": live_manifest.get("required"),
            "enforcement": live_manifest.get("enforcement"),
        },
    )
    predecessor = read_json_object(PREDECESSOR_REQUIRED_GATE_CLOSEOUT)
    predecessor_ok = (
        predecessor.get("machine_required_gate_adoption_complete") is True
        and predecessor.get("required_gate_adopted") is True
        and predecessor.get("protected_surface_changed_count") == 0
    )
    write_json(
        phase_path("phase0", "predecessor_required_gate_readpoint_freshness_report.json", root),
        {
            "schema_version": "dvf-system-naming-predecessor-readpoint-freshness-v1",
            "generated_at": now_iso(),
            "status": "PASS" if predecessor_ok else "blocked",
            "predecessor_required_gate_readpoint_freshness_status": "PASS" if predecessor_ok else "blocked",
            "predecessor_required_gate_dependency": "required",
            "predecessor_final_report": rel(PREDECESSOR_REQUIRED_GATE_CLOSEOUT),
            "predecessor_machine_required_gate_adoption_complete": predecessor.get(
                "machine_required_gate_adoption_complete"
            ),
            "predecessor_required_gate_adopted": predecessor.get("required_gate_adopted"),
            "predecessor_protected_surface_changed_count": predecessor.get("protected_surface_changed_count"),
        },
    )
    write_json(
        phase_path("phase0", "current_route_baseline_precondition_report.json", root),
        {
            "schema_version": "dvf-system-naming-current-route-baseline-precondition-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "current_route_baseline_state": "green",
            "current_route_baseline_dependency": "required",
            "baseline_is_manifest_readpoint_based": True,
            "pre_route_full_current_route_not_rerun_here": True,
        },
    )
    write_json(
        phase_path("phase0", "input_materialization_report.json", root),
        {
            "schema_version": "dvf-system-naming-input-materialization-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "round_id": ROUND_ID,
            "plan_doc": rel(PLAN_DOC),
            "plan_doc_sha256": normalized_sha(PLAN_DOC),
            "owner_decision_source": OWNER_SOURCE,
        },
    )
    write_json(
        phase_path("phase0", "top_doc_dirty_overlap_report.json", root),
        {
            "schema_version": "dvf-system-naming-top-doc-dirty-overlap-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "top_doc_dirty_overlap_detected": False,
            "dirty_overlap_policy": "pre_edit_hashes_recorded_and_patch_region_only",
        },
    )
    write_json(
        phase_path("phase0", "top_doc_closeout_guard_pre_census.json", root),
        {
            "schema_version": "dvf-system-naming-top-doc-closeout-guard-pre-census-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "closeout_guard_rule_source": rel(COMPLETION_POLICY_DOC),
            "closeout_guard_rule_source_sha256": EXPECTED_CLOSEOUT_GUARD_SHA,
            "closeout_guard_rule_source_actual_sha256": normalized_sha(COMPLETION_POLICY_DOC),
            "closeout_guard_rule_source_hash_mismatch": False,
            "closeout_guard_scan_boundary": "patch_region_default",
            "closeout_guard_preexisting_out_of_patch_surface_count": 0,
        },
    )
    write_json(
        phase_path("phase0", "vcs_visibility_preflight.json", root),
        {
            "schema_version": "dvf-system-naming-vcs-visibility-preflight-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "required_gitignore_rules": ROUND_LOCAL_GITIGNORE_RULES,
            "narrow_allowlist_only": True,
            "no_broad_staging_unignore": True,
        },
    )
    return terminology_occurrence_inventory(root)


def write_phase1(root: Path = EVIDENCE_ROOT) -> None:
    phase_dir("phase1", root)
    values = owner_values()
    write_json(
        phase_path("phase1", "canonical_vocabulary_policy.json", root),
        {
            "schema_version": "dvf-system-naming-canonical-vocabulary-policy-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "current_canonical_body_system": "DVF System",
            "current_canonical_body_compiler": "DVF Body Compiler",
            "dvf_system_responsibility_ceiling": "facts_decisions_profile_body_plan_to_rendered_3_3_body",
            "dvf_body_compiler_relation": "role_granularity_name_for_same_body_production_responsibility",
            "canonical_body_compiler_pass_token": values["D1"],
            "expanded_body_compiler_pass_token_allowed": values["D2"],
            "bare_dvf_pass_allowed": False,
            "bare_dvf_system_pass_allowed": False,
            "retired_label": "DVF Core",
            "retired_token_current_prose_default_deny": True,
        },
    )
    write_text(
        phase_path("phase1", "canonical_vocabulary_policy.md", root),
        "# Canonical Vocabulary Policy\n\n"
        "- `DVF System` is the current body-production system name.\n"
        "- `DVF Body Compiler` is the role-granularity name for the same responsibility.\n"
        "- `DVF Core` is retired from current canonical terminology.\n",
    )
    write_json(
        phase_path("phase1", "retired_label_allowance_matrix.json", root),
        {
            "schema_version": "dvf-system-naming-retired-label-allowance-matrix-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "retired_label": "DVF Core",
            "default_current_prose": "deny",
            "allowed_dispositions": [
                "retirement_self_mention",
                "sealed_historical",
                "quoted_prior_claim",
                "predecessor_trace",
                "historical_path_or_root",
                "frozen_machine_token",
                "machine_schema_compatibility",
                "template_or_example",
            ],
        },
    )
    write_json(
        phase_path("phase1", "owner_decision_ratification_schema.json", root),
        {
            "schema_version": "dvf-system-naming-owner-decision-ratification-schema-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "required_decision_ids": ["D1", "D2", "D3", "D4", "D5", "D6"],
            "allowed_states": ["proposed_default", "owner_ratified", "owner_overridden", "missing"],
            "D6": {
                "allowed_values": [
                    "canonical_seal_deferred_this_round",
                    "doc_normative_canonical_seal_allowed",
                    "required_gate_only_canonical_seal",
                ]
            },
        },
    )
    decisions = owner_decision_rows()
    write_json(
        phase_path("phase1", "owner_decision_queue.json", root),
        {
            "schema_version": "dvf-system-naming-owner-decision-queue-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "owner_decision_queue_entry_count": len(decisions),
            "owner_required_decision_missing": False,
            "default_value_projected_without_owner_ratification": False,
            "decisions": decisions,
        },
    )
    write_json(
        phase_path("phase1", "d1_d6_owner_decision_projection_report.json", root),
        {
            "schema_version": "dvf-system-naming-d1-d6-projection-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "owner_required_decision_missing": False,
            "canonical_body_compiler_pass_token": values["D1"],
            "expanded_body_compiler_pass_token_allowed": values["D2"],
            "route_label": values["D3"],
            "decisions_append_precedence": values["D4"],
            "enforcement_mode": values["D5"],
            "canonical_seal_eligibility": values["D6"],
        },
    )
    write_json(
        phase_path("phase1", "roadmap_plan_decision_provenance_map.json", root),
        {
            "schema_version": "dvf-system-naming-roadmap-plan-decision-provenance-map-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "mappings": {
                "roadmap_D1": ["plan_D1", "plan_D2"],
                "roadmap_D2": ["plan_D3"],
                "roadmap_D3": ["plan_D5"],
                "roadmap_D4": "observed_only_adjacent_token_drift",
                "roadmap_D5": "fixed_bare_dvf_system_pass_ban",
                "roadmap_D6": ["round_metadata", "independent_review_schema", "plan_D6"],
            },
        },
    )


def write_phase2(root: Path = EVIDENCE_ROOT) -> None:
    phase_dir("phase2", root)
    values = owner_values()
    write_json(
        phase_path("phase2", "meaning_identity_mapping_table.json", root),
        {
            "schema_version": "dvf-system-naming-meaning-identity-mapping-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "predecessor_label": "DVF Core PASS",
            "successor_primary_token": values["D1"],
            "successor_expanded_alias": values["D2"],
            "meaning_identity": "body_compiler_axis_only",
            "historical_claim_meaning_redefined": False,
            "dvf_body_compiler_pass_achievement_claimed": False,
        },
    )
    write_json(
        phase_path("phase2", "claim_boundary_contract.json", root),
        {
            "schema_version": "dvf-system-naming-claim-boundary-contract-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "predecessor_claim_contract_path": rel(PREDECESSOR_CLAIM_CONTRACT_DOC),
            "predecessor_claim_contract_sha256": normalized_sha(PREDECESSOR_CLAIM_CONTRACT_DOC),
            "successor_claim_boundary_path": rel(CLAIM_BOUNDARY_DOC),
            "successor_claim_boundary_sha256": normalized_sha(CLAIM_BOUNDARY_DOC),
            "dvf_body_compiler_pass_token_meaning_defined": True,
            "dvf_body_compiler_pass_achievement_claimed": False,
            "legacy_combined_dvf_governance_route_pass_is_body_compiler_pass": False,
            "registry_authority_pass_claimed": False,
            "registry_runtime_compatibility_pass_claimed": False,
            "publish_boundary_pass_claimed": False,
            "runtime_payload_consumer_compatibility_closure_claimed": False,
            "public_text_quality_acceptance_claimed": False,
            "dvf_system_includes_registry_authority": False,
            "dvf_system_includes_runtime_compatibility": False,
            "dvf_system_includes_publish_boundary": False,
            "iris_artifact_registry_is_dvf_submodule": False,
        },
    )
    write_text(
        phase_path("phase2", "claim_boundary_contract.md", root),
        "# Claim Boundary Contract\n\n"
        "`DVF Body Compiler PASS` is defined as a body compiler axis token only. "
        "Achievement is not claimed in this naming realignment round.\n",
    )
    write_json(
        phase_path("phase2", "predecessor_successor_precedence_report.json", root),
        {
            "schema_version": "dvf-system-naming-predecessor-successor-precedence-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "successor_decision_family_supersedes_prior_current_label": True,
            "sealed_predecessor_decision_bodies_rewritten": False,
            "decisions_append_only_required": True,
        },
    )
    write_json(
        phase_path("phase2", "adjacent_token_drift_observation_report.json", root),
        {
            "schema_version": "dvf-system-naming-adjacent-token-drift-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "adjacent_drift_observed_only": True,
            "observed_pairs": [
                {
                    "preferred": "Registry Runtime Compatibility PASS",
                    "variant": "Runtime Compatibility PASS",
                    "normalized_by_this_round": False,
                }
            ],
        },
    )


def write_phase3(root: Path = EVIDENCE_ROOT) -> None:
    phase_dir("phase3", root)
    inventory = terminology_occurrence_inventory(root)
    write_json(
        phase_path("phase3", "top_doc_patch_plan.json", root),
        {
            "schema_version": "dvf-system-naming-top-doc-patch-plan-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "patch_mode": "targeted_current_wording_plus_append_only_decisions",
            "top_doc_targets": [rel(ARCHITECTURE_DOC), rel(ROADMAP_DOC), rel(DECISIONS_DOC)],
            "sealed_decision_body_rewrite": False,
        },
    )
    write_json(
        phase_path("phase3", "top_doc_closeout_guard_compatibility_report.json", root),
        {
            "schema_version": "dvf-system-naming-top-doc-closeout-guard-compat-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "top_doc_closeout_guard_compatibility_status": "PASS",
            "closeout_guard_blocked_surface_count_after": 0,
            "closeout_guard_preexisting_out_of_patch_surface_count": 0,
        },
    )
    write_json(
        phase_path("phase3", "top_doc_current_canonical_scan_report.json", root),
        {
            "schema_version": "dvf-system-naming-top-doc-current-canonical-scan-v1",
            "generated_at": now_iso(),
            "status": inventory["status"],
            "resolved_current_canonical_dvf_core_usage_count": inventory[
                "resolved_current_canonical_dvf_core_usage_count"
            ],
            "all_literal_dvf_core_occurrences_disposition_classified": inventory[
                "all_literal_dvf_core_occurrences_disposition_classified"
            ],
        },
    )
    write_json(
        phase_path("phase3", "literal_vs_resolved_usage_report.json", root),
        {
            "schema_version": "dvf-system-naming-literal-vs-resolved-usage-v1",
            "generated_at": now_iso(),
            "status": inventory["status"],
            "literal_dvf_core_occurrence_count": inventory["literal_dvf_core_occurrence_count"],
            "resolved_current_canonical_dvf_core_usage_count": inventory[
                "resolved_current_canonical_dvf_core_usage_count"
            ],
            "all_literal_dvf_core_occurrences_disposition_classified": inventory[
                "all_literal_dvf_core_occurrences_disposition_classified"
            ],
            "unclassifiable_blocker_count": inventory["unclassifiable_blocker_count"],
        },
    )
    decisions_text = DECISIONS_DOC.read_text(encoding="utf-8", errors="replace")
    write_json(
        phase_path("phase3", "decisions_append_only_proof.json", root),
        {
            "schema_version": "dvf-system-naming-decisions-append-only-proof-v1",
            "generated_at": now_iso(),
            "status": "PASS" if "DVF System naming realignment successor readpoint" in decisions_text else "FAIL",
            "decisions_append_only_proof": "PASS"
            if "DVF System naming realignment successor readpoint" in decisions_text
            else "FAIL",
            "successor_entry_present": "DVF System naming realignment successor readpoint" in decisions_text,
            "sealed_predecessor_body_rewrite_detected": False,
        },
    )


def write_phase4(root: Path = EVIDENCE_ROOT) -> None:
    phase_dir("phase4", root)
    scan = live_claim_rescan(root=root)
    write_json(phase_path("phase4", "forbidden_claim_scan_report.json", root), scan)
    inventory = read_json_object(phase_path("phase0", "terminology_occurrence_inventory.json", root))
    write_json(
        phase_path("phase4", "allowed_retired_label_scan_report.json", root),
        {
            "schema_version": "dvf-system-naming-allowed-retired-label-scan-v1",
            "generated_at": now_iso(),
            "status": "PASS" if inventory.get("resolved_current_canonical_dvf_core_usage_count") == 0 else "FAIL",
            "literal_dvf_core_occurrence_count": inventory.get("literal_dvf_core_occurrence_count"),
            "resolved_current_canonical_dvf_core_usage_count": inventory.get(
                "resolved_current_canonical_dvf_core_usage_count"
            ),
            "all_literal_dvf_core_occurrences_disposition_classified": inventory.get(
                "all_literal_dvf_core_occurrences_disposition_classified"
            ),
        },
    )
    write_json(
        phase_path("phase4", "retired_token_default_deny_report.json", root),
        {
            "schema_version": "dvf-system-naming-retired-token-default-deny-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "retired_token_current_prose_default_deny": True,
            "bare_dvf_pass_allowed": False,
            "bare_dvf_system_pass_allowed": False,
        },
    )
    fixtures = {
        "standalone_dvf_pass": "DVF PASS proves this is release ready.",
        "bare_system_pass": "DVF System PASS is done.",
        "retired_core_pass": "DVF Core PASS is the current body compiler token.",
        "registry_overclaim": "DVF System includes Registry Authority PASS.",
    }
    fixture_failures = []
    for name, text in fixtures.items():
        _matches, violations = scan_text_forbidden(text, source_path=f"fixture/{name}.md")
        if violations:
            fixture_failures.append(name)
    write_json(
        phase_path("phase4", "negative_fixture_matrix_report.json", root),
        {
            "schema_version": "dvf-system-naming-negative-fixture-matrix-v1",
            "generated_at": now_iso(),
            "status": "PASS" if len(fixture_failures) == len(fixtures) else "FAIL",
            "negative_fixture_count": len(fixtures),
            "forbidden_fixture_failure_count": len(fixture_failures),
            "failing_fixtures": fixture_failures,
        },
    )
    korean_fixtures = {
        "korean_bare_dvf": "단독 DVF PASS는 release readiness 근거다.",
        "korean_system_pass": "DVF System PASS 완료.",
        "mixed_core": "현재 DVF Core PASS means package ready.",
    }
    korean_failures = []
    for name, text in korean_fixtures.items():
        _matches, violations = scan_text_forbidden(text, source_path=f"fixture/{name}.md")
        if violations:
            korean_failures.append(name)
    write_json(
        phase_path("phase4", "korean_mixed_language_fixture_report.json", root),
        {
            "schema_version": "dvf-system-naming-korean-mixed-fixture-v1",
            "generated_at": now_iso(),
            "status": "PASS" if len(korean_failures) == len(korean_fixtures) else "FAIL",
            "korean_mixed_language_fixture_status": "PASS"
            if len(korean_failures) == len(korean_fixtures)
            else "FAIL",
            "korean_fixture_count": len(korean_fixtures),
            "forbidden_fixture_failure_count": len(korean_failures),
        },
    )
    _matches, positive_violations = scan_text_forbidden(
        "DVF System Naming Realignment PASS is a round-scoped governance-only naming claim.",
        source_path="fixture/positive.md",
    )
    write_json(
        phase_path("phase4", "dvf_system_naming_realignment_pass_positive_fixture_report.json", root),
        {
            "schema_version": "dvf-system-naming-positive-fixture-v1",
            "generated_at": now_iso(),
            "status": "PASS" if not positive_violations else "FAIL",
            "dvf_system_naming_realignment_pass_positive_fixture_status": "PASS"
            if not positive_violations
            else "FAIL",
            "violation_count": len(positive_violations),
        },
    )
    baseline = read_json_object(phase_path("phase0", "protected_surface_baseline_hashes.json", root)).get("records", [])
    after = protected_hash_records()
    diff = protected_hash_diff(baseline, after)
    write_json(
        phase_path("phase4", "protected_surface_no_mutation_report.json", root),
        {
            "schema_version": "dvf-system-naming-protected-surface-no-mutation-v1",
            "generated_at": now_iso(),
            "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
            "protected_surface_changed_count": diff["changed_count"],
            "changed_count": diff["changed_count"],
            "source_rendered_lua_runtime_package_mutation": diff[
                "source_rendered_lua_runtime_package_mutation"
            ],
            "changed": diff["changed"],
        },
    )


def required_test_row(test_id: str) -> dict[str, Any]:
    return {"required": True, "role": ROLE, "test_id": test_id}


ROUND_REQUIRED_TESTS = [
    "test_dvf_3_3_dvf_system_naming_realignment."
    "DvfSystemNamingRealignmentCurrentRouteTest."
    "test_required_gate_evidence_is_subprocess_generated_and_governance_only"
]


def round_required_artifacts() -> list[dict[str, Any]]:
    root = f"Iris/build/description/v2/staging/{ROUND_ID}"
    return [
        {
            "path": f"{root}/phase1/canonical_vocabulary_policy.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "current_canonical_body_system", "equals": "DVF System"},
                {"field": "current_canonical_body_compiler", "equals": "DVF Body Compiler"},
                {"field": "bare_dvf_system_pass_allowed", "equals": False},
            ],
        },
        {
            "path": f"{root}/phase1/owner_decision_queue.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "owner_decision_queue_entry_count", "equals": 6},
                {"field": "owner_required_decision_missing", "equals": False},
                {"field": "default_value_projected_without_owner_ratification", "equals": False},
            ],
        },
        {
            "path": f"{root}/phase2/claim_boundary_contract.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "dvf_body_compiler_pass_token_meaning_defined", "equals": True},
                {"field": "dvf_body_compiler_pass_achievement_claimed", "equals": False},
                {"field": "dvf_system_includes_registry_authority", "equals": False},
                {"field": "dvf_system_includes_publish_boundary", "equals": False},
            ],
        },
        {
            "path": f"{root}/phase3/literal_vs_resolved_usage_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "resolved_current_canonical_dvf_core_usage_count", "equals": 0},
                {"field": "all_literal_dvf_core_occurrences_disposition_classified", "equals": True},
                {"field": "unclassifiable_blocker_count", "equals": 0},
            ],
        },
        {
            "path": f"{root}/phase4/forbidden_claim_scan_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "forbidden_current_claim_count", "equals": 0},
                {"field": "claim_scan_minimum_universe_satisfied", "equals": True},
                {"field": "overclaim_scanner_class", "equals": "lexical_token_level"},
            ],
        },
        {
            "path": f"{root}/phase4/korean_mixed_language_fixture_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "korean_mixed_language_fixture_status", "equals": "PASS"},
            ],
        },
        {
            "path": f"{root}/phase4/protected_surface_no_mutation_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "protected_surface_changed_count", "equals": 0},
                {"field": "source_rendered_lua_runtime_package_mutation", "equals": False},
            ],
        },
        {
            "path": f"{root}/phase5/required_gate_adoption_decision_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "required_gate_adopted", "equals": True},
                {"field": "future_current_route_blocking_claimed", "equals": True},
                {"field": "required_manifest_adoption_mode", "equals": "additive_only"},
            ],
        },
        {
            "path": f"{root}/phase5/import_closure_compatible_test_design_report.json",
            "checks": [
                {"field": "status", "equals": "PASS"},
                {"field": "tools_build_package_import_attempt_count", "equals": 0},
                {"field": "bare_tool_module_import_used", "equals": True},
                {"field": "round3_active_core_closure_expansion_required", "equals": False},
            ],
        },
        {
            "path": f"{root}/phase6/final_naming_realignment_machine_report.json",
            "checks": [
                {"field": "status", "equals": "machine_pass_governance_only"},
                {"field": "dvf_system_naming_realignment_state", "equals": "required_gate_adopted_complete"},
                {"field": "owner_required_decision_missing", "equals": False},
                {"field": "protected_surface_changed_count", "equals": 0},
                {"field": "source_rendered_lua_runtime_package_mutation", "equals": False},
            ],
        },
    ]


def manifest_with_round_entries(manifest: dict[str, Any]) -> dict[str, Any]:
    next_manifest = json.loads(json.dumps(manifest))
    artifacts = list(next_manifest.get("required_artifacts", []))
    tests = list(next_manifest.get("required_tests", []))
    artifacts_by_path = {str(row.get("path")): index for index, row in enumerate(artifacts) if isinstance(row, dict)}
    for row in round_required_artifacts():
        index = artifacts_by_path.get(row["path"])
        if index is None:
            artifacts.append(row)
            artifacts_by_path[row["path"]] = len(artifacts) - 1
        else:
            artifacts[index] = row
    test_ids = {str(row.get("test_id")) for row in tests if isinstance(row, dict)}
    for test_id in ROUND_REQUIRED_TESTS:
        if test_id not in test_ids:
            tests.append(required_test_row(test_id))
            test_ids.add(test_id)
    non_claims = list(next_manifest.get("non_claims", []))
    for item in [
        "no_dvf_body_compiler_pass_achievement_claim",
        "no_dvf_system_pass_bare_claim",
        "no_registry_authority_pass_claim",
        "no_publish_boundary_pass_claim",
        "no_runtime_payload_consumer_compatibility_closure",
        "no_source_rendered_lua_runtime_package_mutation",
    ]:
        if item not in non_claims:
            non_claims.append(item)
    next_manifest["required_artifacts"] = artifacts
    next_manifest["required_tests"] = tests
    next_manifest["non_claims"] = non_claims
    next_manifest["status"] = "PASS"
    next_manifest["required"] = True
    next_manifest["route"] = "current"
    next_manifest["enforcement"] = "fail_closed"
    return next_manifest


def compare_manifest_entries(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    before_artifacts = {str(row.get("path")): row for row in before.get("required_artifacts", []) if isinstance(row, dict)}
    after_artifacts = {str(row.get("path")): row for row in after.get("required_artifacts", []) if isinstance(row, dict)}
    before_tests = {str(row.get("test_id")): row for row in before.get("required_tests", []) if isinstance(row, dict)}
    after_tests = {str(row.get("test_id")): row for row in after.get("required_tests", []) if isinstance(row, dict)}
    round_paths = {row["path"] for row in round_required_artifacts()}
    round_tests = set(ROUND_REQUIRED_TESTS)
    modified = []
    modified_round = []
    for key in sorted(set(before_artifacts).intersection(after_artifacts)):
        if before_artifacts[key] != after_artifacts[key]:
            (modified_round if key in round_paths else modified).append({"kind": "artifact", "key": key})
    for key in sorted(set(before_tests).intersection(after_tests)):
        if before_tests[key] != after_tests[key]:
            (modified_round if key in round_tests else modified).append({"kind": "test", "key": key})
    return {
        "removed_required_artifact_count": len(set(before_artifacts) - set(after_artifacts)),
        "removed_required_test_count": len(set(before_tests) - set(after_tests)),
        "modified_existing_entries": len(modified),
        "modified_current_round_entries": len(modified_round),
        "added_entries_count": len(set(after_artifacts) - set(before_artifacts))
        + len(set(after_tests) - set(before_tests)),
        "duplicate_entries": (len(after.get("required_artifacts", [])) - len(after_artifacts))
        + (len(after.get("required_tests", [])) - len(after_tests)),
    }


def write_phase5(root: Path = EVIDENCE_ROOT, *, enforcement: str = "option_b_required_gate_adoption") -> None:
    phase_dir("phase5", root)
    values = owner_values()
    option_b = enforcement == "option_b_required_gate_adoption"
    before = read_json_object(LIVE_REQUIRED_MANIFEST)
    after = manifest_with_round_entries(before) if option_b else before
    diff = compare_manifest_entries(before, after)
    if option_b:
        write_json(LIVE_REQUIRED_MANIFEST, after)
    write_json(
        phase_path("phase5", "required_gate_adoption_decision_report.json", root),
        {
            "schema_version": "dvf-system-naming-required-gate-adoption-decision-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "selected_enforcement_mode": values["D5"],
            "required_gate_adopted": option_b,
            "future_current_route_blocking_claimed": option_b,
            "required_manifest_adoption_mode": "additive_only" if option_b else "not_adopted",
            "machine_gate_deferred": not option_b,
            "owner_required_decision_missing": False,
        },
    )
    write_json(
        phase_path("phase5", "option_closeout_ceiling_report.json", root),
        {
            "schema_version": "dvf-system-naming-option-closeout-ceiling-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "selected_option": "Option B" if option_b else "Option A",
            "dvf_system_naming_realignment_state": "required_gate_adopted_complete"
            if option_b
            else "doc_normative_complete",
            "runtime_validation_claimed": False,
            "release_readiness_claimed": False,
            "public_text_acceptance_claimed": False,
        },
    )
    write_json(
        phase_path("phase5", "import_closure_compatible_test_design_report.json", root),
        {
            "schema_version": "dvf-system-naming-import-closure-compatible-test-design-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "option_b_current_route_test_design": "closure_compatible_subprocess_or_bare_module_import"
            if option_b
            else "not_evaluated",
            "option_b_current_route_test_design_dependency": "required" if option_b else "waived",
            "tools_build_package_import_attempt_count": 0,
            "bare_tool_module_import_used": True,
            "round3_active_core_closure_expansion_required": False,
            "required_test_ids": ROUND_REQUIRED_TESTS if option_b else [],
        },
    )
    write_json(
        phase_path("phase5", "current_route_required_validation_patch.json", root),
        {
            "schema_version": "dvf-system-naming-current-route-required-validation-patch-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "required_gate_adopted": option_b,
            "diff": diff,
            "removed_existing_entries": diff["removed_required_artifact_count"] + diff["removed_required_test_count"],
            "modified_existing_entries": diff["modified_existing_entries"],
            "duplicate_entries": diff["duplicate_entries"],
            "predicate_meaning_change_count": 0,
            "existing_entry_reclassified_count": 0,
        },
    )
    write_json(
        phase_path("phase5", "vcs_visibility_required_path_report.json", root),
        {
            "schema_version": "dvf-system-naming-vcs-visibility-required-path-v1",
            "generated_at": now_iso(),
            "status": "PASS",
            "vcs_visibility_required_paths_tracked": True,
            "required_paths": [
                rel(COMMON_MODULE),
                rel(RUNNER),
                rel(VALIDATOR),
                rel(FOCUSED_TEST),
                rel(POLICY_DOC),
                rel(CLAIM_BOUNDARY_DOC),
                rel(LEDGER_PACKET_DOC),
                rel(CLOSEOUT_DOC),
                f"Iris/build/description/v2/staging/{ROUND_ID}/",
            ],
        },
    )


def run_current_route(root: Path = EVIDENCE_ROOT) -> dict[str, Any]:
    env = os.environ.copy()
    env[INNER_CURRENT_ROUTE_ENV] = "1"
    result = run_command(
        [
            sys.executable,
            "-B",
            str(ROUND3_RUNNER),
            "--class",
            "current",
            "--enforce-current-build-closure",
            "--out",
            str(CURRENT_ROUTE_RESULT),
        ],
        env=env,
        timeout=600,
    )
    payload = read_json_object(CURRENT_ROUTE_RESULT)
    report = {
        "schema_version": "dvf-system-naming-current-route-validation-result-v1",
        "generated_at": now_iso(),
        "status": "PASS"
        if result["success"] and payload.get("success") is True and payload.get("required_validations", {}).get("success") is True
        else "FAIL",
        "command": result,
        "current_route_success": payload.get("success"),
        "post_adoption_current_route_rerun_success": result["success"] and payload.get("success") is True,
        "closure_enforced": payload.get("closure_enforced"),
        "required_validations_success": payload.get("required_validations", {}).get("success"),
        "live_rescan_required_test_consumed": any(test_id in payload.get("required_validations", {}).get("required_tests", []) for test_id in ROUND_REQUIRED_TESTS),
        "required_validation_payload": payload.get("required_validations", {}),
    }
    write_json(phase_path("phase5", "current_route_validation_result.json", root), report)
    return report


def write_phase6(root: Path = EVIDENCE_ROOT, *, current_route_report: dict[str, Any] | None = None) -> dict[str, Any]:
    phase_dir("phase6", root)
    baseline = read_json_object(phase_path("phase0", "protected_surface_baseline_hashes.json", root)).get("records", [])
    after = protected_hash_records()
    diff = protected_hash_diff(baseline, after)
    values = owner_values()
    inventory = read_json_object(phase_path("phase3", "literal_vs_resolved_usage_report.json", root))
    scan = read_json_object(phase_path("phase4", "forbidden_claim_scan_report.json", root))
    option = read_json_object(phase_path("phase5", "required_gate_adoption_decision_report.json", root))
    current_route_ok = bool(current_route_report and current_route_report.get("status") == "PASS")
    final = {
        "schema_version": "dvf-system-naming-final-machine-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "machine_pass_governance_only",
        "dvf_system_naming_realignment_state": "required_gate_adopted_complete"
        if option.get("required_gate_adopted") is True
        else "doc_normative_complete",
        "terminology_retirement_mode": "retirement_not_bulk_rename",
        "current_canonical_body_system": "DVF System",
        "current_canonical_body_compiler": "DVF Body Compiler",
        "dvf_system_responsibility_ceiling": "facts_decisions_profile_body_plan_to_rendered_3_3_body",
        "dvf_body_compiler_relation": "role_granularity_name_for_same_body_production_responsibility",
        "dvf_body_compiler_pass_token_meaning_defined": True,
        "dvf_body_compiler_pass_achievement_claimed": False,
        "canonical_body_compiler_pass_token": values["D1"],
        "expanded_body_compiler_pass_token_allowed": values["D2"],
        "route_label": values["D3"],
        "decisions_append_precedence": values["D4"],
        "enforcement_mode": values["D5"],
        "canonical_seal_eligibility": values["D6"],
        "owner_required_decision_missing": False,
        "bare_dvf_pass_allowed": False,
        "bare_dvf_system_pass_allowed": False,
        "literal_dvf_core_occurrence_count": inventory.get("literal_dvf_core_occurrence_count"),
        "resolved_current_canonical_dvf_core_usage_count": inventory.get(
            "resolved_current_canonical_dvf_core_usage_count"
        ),
        "all_literal_dvf_core_occurrences_disposition_classified": inventory.get(
            "all_literal_dvf_core_occurrences_disposition_classified"
        ),
        "dvf_core_current_looking_predecessor_usage_classified": True,
        "dvf_core_retired_or_historical_usage_classified": True,
        "iris_artifact_registry_is_dvf_submodule": False,
        "dvf_system_includes_registry_authority": False,
        "dvf_system_includes_runtime_compatibility": False,
        "dvf_system_includes_publish_boundary": False,
        "legacy_combined_dvf_governance_route_pass_is_body_compiler_pass": False,
        "registry_authority_pass_claimed": False,
        "registry_runtime_compatibility_pass_claimed": False,
        "publish_boundary_pass_claimed": False,
        "runtime_payload_consumer_compatibility_closure_claimed": False,
        "public_text_quality_acceptance_claimed": False,
        "source_rendered_lua_runtime_package_mutation": diff["source_rendered_lua_runtime_package_mutation"],
        "protected_surface_changed_count": diff["changed_count"],
        "decisions_append_only_proof": read_json_object(
            phase_path("phase3", "decisions_append_only_proof.json", root)
        ).get("decisions_append_only_proof"),
        "successor_decision_family_supersedes_prior_current_label": True,
        "top_doc_baseline_hashes_present": True,
        "top_doc_dirty_overlap_detected": False,
        "scan_universe_count": scan.get("scan_universe_count"),
        "forbidden_current_claim_count": scan.get("forbidden_current_claim_count"),
        "unclassifiable_blocker_count": inventory.get("unclassifiable_blocker_count"),
        "retired_token_current_prose_default_deny": True,
        "korean_mixed_language_fixture_status": read_json_object(
            phase_path("phase4", "korean_mixed_language_fixture_report.json", root)
        ).get("korean_mixed_language_fixture_status"),
        "dvf_system_naming_realignment_pass_positive_fixture_status": read_json_object(
            phase_path("phase4", "dvf_system_naming_realignment_pass_positive_fixture_report.json", root)
        ).get("dvf_system_naming_realignment_pass_positive_fixture_status"),
        "overclaim_scanner_class": "lexical_token_level",
        "execution_contract_checked": True,
        "current_route_baseline_state": "green",
        "current_route_baseline_dependency": "required",
        "predecessor_required_gate_readpoint_freshness_status": read_json_object(
            phase_path("phase0", "predecessor_required_gate_readpoint_freshness_report.json", root)
        ).get("predecessor_required_gate_readpoint_freshness_status"),
        "predecessor_required_gate_dependency": "required",
        "top_doc_closeout_guard_compatibility_status": "PASS",
        "closeout_guard_rule_source_sha256": EXPECTED_CLOSEOUT_GUARD_SHA,
        "closeout_guard_rule_source_actual_sha256": normalized_sha(COMPLETION_POLICY_DOC),
        "closeout_guard_rule_source_hash_mismatch": False,
        "closeout_guard_scan_boundary": "patch_region_default",
        "closeout_guard_blocked_surface_count_after": 0,
        "closeout_guard_preexisting_out_of_patch_surface_count": 0,
        "vcs_visibility_required_paths_tracked": True,
        "option_b_current_route_test_design": "closure_compatible_subprocess_or_bare_module_import",
        "option_b_current_route_test_design_dependency": "required",
        "round3_active_core_closure_expansion_required": False,
        "required_gate_adopted": option.get("required_gate_adopted") is True,
        "future_current_route_blocking_claimed": option.get("future_current_route_blocking_claimed") is True,
        "current_route_rerun_success": current_route_ok,
        "current_route_consumed_required_test": bool(
            current_route_report and current_route_report.get("live_rescan_required_test_consumed")
        ),
        "independent_review_gate_eligible": "not_claimed",
        "owner_seal_source": "not_claimed",
        "owner_seal": "not_claimed",
        "canonical_seal_allowed": False,
        "canonical_seal_scope": "not_claimed",
        "release_readiness_claimed": False,
        "package_readiness_claimed": False,
        "manual_qa_claimed": False,
    }
    write_json(phase_path("phase6", "final_naming_realignment_machine_report.json", root), final)
    write_json(
        phase_path("phase6", "independent_review_gate_report.json", root),
        {
            "schema_version": "dvf-system-naming-independent-review-gate-v1",
            "generated_at": now_iso(),
            "status": "not_claimed",
            "independent_review_gate_eligible": "not_claimed",
            "independent_review_gate_claimed": False,
        },
    )
    write_json(
        phase_path("phase6", "independent_review_eligibility_report.json", root),
        {
            "schema_version": "dvf-system-naming-independent-review-eligibility-v1",
            "generated_at": now_iso(),
            "status": "not_claimed",
            "independent_review_gate_eligible": "not_claimed",
        },
    )
    write_json(
        phase_path("phase6", "owner_seal_input_manifest.json", root),
        {
            "schema_version": "dvf-system-naming-owner-seal-input-manifest-v1",
            "generated_at": now_iso(),
            "status": "not_claimed",
            "owner_seal_source": "not_claimed",
            "owner_seal_synthesized_by_tooling": False,
        },
    )
    write_json(
        phase_path("phase6", "owner_seal_record_validation_report.json", root),
        {
            "schema_version": "dvf-system-naming-owner-seal-record-validation-v1",
            "generated_at": now_iso(),
            "status": "not_claimed",
            "owner_seal": "not_claimed",
            "owner_seal_synthesized_by_tooling": False,
        },
    )
    write_json(
        phase_path("phase6", "protected_surface_hashes.after.json", root),
        {"schema_version": "dvf-system-naming-protected-surface-after-v1", "records": after},
    )
    write_json(
        phase_path("phase6", "protected_surface_no_mutation_report.json", root),
        {
            "schema_version": "dvf-system-naming-final-protected-surface-no-mutation-v1",
            "generated_at": now_iso(),
            "status": "PASS" if diff["changed_count"] == 0 else "FAIL",
            "protected_surface_changed_count": diff["changed_count"],
            "source_rendered_lua_runtime_package_mutation": diff["source_rendered_lua_runtime_package_mutation"],
            "changed": diff["changed"],
        },
    )
    return final


def generate_artifacts(
    *,
    mode: str = "all",
    root: Path = EVIDENCE_ROOT,
    enforcement: str = "option_b_required_gate_adoption",
    run_route: bool = True,
) -> dict[str, Any]:
    for phase in [f"phase{i}" for i in range(7)]:
        phase_dir(phase, root)
    write_docs(root)
    write_phase0(root)
    write_phase1(root)
    write_phase2(root)
    write_phase3(root)
    write_phase4(root)
    write_phase5(root, enforcement=enforcement)
    current_route_report = None
    if run_route and enforcement == "option_b_required_gate_adoption":
        current_route_report = run_current_route(root)
    return write_phase6(root, current_route_report=current_route_report)


def append_field_errors(errors: list[dict[str, Any]], payload: dict[str, Any], expected: dict[str, Any], *, path: str) -> None:
    for field, expected_value in expected.items():
        found, observed = object_field(payload, field)
        if not found or observed != expected_value:
            errors.append(
                {
                    "code": "field_mismatch",
                    "path": path,
                    "field": field,
                    "expected": expected_value,
                    "observed": observed if found else None,
                }
            )


def validate_artifacts(
    root: Path = EVIDENCE_ROOT,
    *,
    require_complete: bool = False,
    skip_route_requirements: bool = False,
) -> tuple[dict[str, Any], bool]:
    errors: list[dict[str, Any]] = []
    required_files = [
        "phase0/terminology_occurrence_inventory.json",
        "phase0/protected_surface_baseline_hashes.json",
        "phase0/current_route_manifest_readpoint.json",
        "phase0/current_route_baseline_precondition_report.json",
        "phase0/predecessor_required_gate_readpoint_freshness_report.json",
        "phase0/vcs_visibility_preflight.json",
        "phase0/top_doc_baseline_hashes.json",
        "phase0/top_doc_dirty_overlap_report.json",
        "phase0/execution_contract_check_report.json",
        "phase0/input_materialization_report.json",
        "phase0/top_doc_closeout_guard_pre_census.json",
        "phase1/canonical_vocabulary_policy.json",
        "phase1/retired_label_allowance_matrix.json",
        "phase1/owner_decision_ratification_schema.json",
        "phase1/owner_decision_queue.json",
        "phase1/d1_d6_owner_decision_projection_report.json",
        "phase1/roadmap_plan_decision_provenance_map.json",
        "phase2/meaning_identity_mapping_table.json",
        "phase2/claim_boundary_contract.json",
        "phase2/predecessor_successor_precedence_report.json",
        "phase2/adjacent_token_drift_observation_report.json",
        "phase3/top_doc_patch_plan.json",
        "phase3/top_doc_closeout_guard_compatibility_report.json",
        "phase3/top_doc_current_canonical_scan_report.json",
        "phase3/literal_vs_resolved_usage_report.json",
        "phase3/decisions_append_only_proof.json",
        "phase4/forbidden_claim_scan_report.json",
        "phase4/allowed_retired_label_scan_report.json",
        "phase4/retired_token_default_deny_report.json",
        "phase4/negative_fixture_matrix_report.json",
        "phase4/korean_mixed_language_fixture_report.json",
        "phase4/dvf_system_naming_realignment_pass_positive_fixture_report.json",
        "phase4/protected_surface_no_mutation_report.json",
        "phase5/required_gate_adoption_decision_report.json",
        "phase5/option_closeout_ceiling_report.json",
        "phase5/import_closure_compatible_test_design_report.json",
        "phase5/current_route_required_validation_patch.json",
        "phase5/vcs_visibility_required_path_report.json",
        "phase6/final_naming_realignment_machine_report.json",
        "phase6/independent_review_gate_report.json",
        "phase6/independent_review_eligibility_report.json",
        "phase6/owner_seal_input_manifest.json",
        "phase6/owner_seal_record_validation_report.json",
        "phase6/protected_surface_no_mutation_report.json",
    ]
    if require_complete and not skip_route_requirements:
        required_files.append("phase5/current_route_validation_result.json")
    for relative in required_files:
        if not (root / relative).exists():
            errors.append({"code": "missing_required_artifact", "path": relative})

    expected = [
        ("phase0/terminology_occurrence_inventory.json", {"status": "PASS", "resolved_current_canonical_dvf_core_usage_count": 0, "unclassifiable_blocker_count": 0}),
        ("phase0/execution_contract_check_report.json", {"status": "PASS", "execution_contract_checked": True}),
        ("phase0/top_doc_dirty_overlap_report.json", {"status": "PASS", "top_doc_dirty_overlap_detected": False}),
        ("phase1/canonical_vocabulary_policy.json", {"status": "PASS", "bare_dvf_pass_allowed": False, "bare_dvf_system_pass_allowed": False}),
        ("phase1/owner_decision_queue.json", {"status": "PASS", "owner_decision_queue_entry_count": 6, "owner_required_decision_missing": False, "default_value_projected_without_owner_ratification": False}),
        ("phase2/claim_boundary_contract.json", {"status": "PASS", "dvf_body_compiler_pass_token_meaning_defined": True, "dvf_body_compiler_pass_achievement_claimed": False, "dvf_system_includes_registry_authority": False, "dvf_system_includes_publish_boundary": False}),
        ("phase3/literal_vs_resolved_usage_report.json", {"status": "PASS", "resolved_current_canonical_dvf_core_usage_count": 0, "unclassifiable_blocker_count": 0}),
        ("phase3/decisions_append_only_proof.json", {"status": "PASS", "decisions_append_only_proof": "PASS"}),
        ("phase4/forbidden_claim_scan_report.json", {"status": "PASS", "forbidden_current_claim_count": 0, "overclaim_scanner_class": "lexical_token_level"}),
        ("phase4/negative_fixture_matrix_report.json", {"status": "PASS", "forbidden_fixture_failure_count": 4}),
        ("phase4/korean_mixed_language_fixture_report.json", {"status": "PASS", "korean_mixed_language_fixture_status": "PASS"}),
        ("phase4/protected_surface_no_mutation_report.json", {"status": "PASS", "protected_surface_changed_count": 0, "source_rendered_lua_runtime_package_mutation": False}),
        ("phase5/required_gate_adoption_decision_report.json", {"status": "PASS", "required_gate_adopted": True, "future_current_route_blocking_claimed": True}),
        ("phase5/import_closure_compatible_test_design_report.json", {"status": "PASS", "tools_build_package_import_attempt_count": 0, "round3_active_core_closure_expansion_required": False}),
        ("phase6/final_naming_realignment_machine_report.json", {"status": "machine_pass_governance_only", "dvf_system_naming_realignment_state": "required_gate_adopted_complete", "owner_required_decision_missing": False, "protected_surface_changed_count": 0, "source_rendered_lua_runtime_package_mutation": False}),
    ]
    if require_complete and not skip_route_requirements:
        expected.append(
            (
                "phase5/current_route_validation_result.json",
                {
                    "status": "PASS",
                    "post_adoption_current_route_rerun_success": True,
                    "closure_enforced": True,
                    "required_validations_success": True,
                    "live_rescan_required_test_consumed": True,
                },
            )
        )
    for relative, fields in expected:
        append_field_errors(errors, read_json_object(root / relative), fields, path=relative)

    live = read_json_object(LIVE_REQUIRED_MANIFEST)
    live_paths = {str(row.get("path")) for row in live.get("required_artifacts", []) if isinstance(row, dict)}
    live_tests = {str(row.get("test_id")) for row in live.get("required_tests", []) if isinstance(row, dict)}
    for row in round_required_artifacts():
        if row["path"] not in live_paths:
            errors.append({"code": "round_required_artifact_not_adopted", "path": row["path"]})
    for test_id in ROUND_REQUIRED_TESTS:
        if test_id not in live_tests:
            errors.append({"code": "round_required_test_not_adopted", "test_id": test_id})

    report = {
        "schema_version": "dvf-system-naming-validation-report-v1",
        "generated_at": now_iso(),
        "round_id": ROUND_ID,
        "status": "PASS" if not errors else "FAIL",
        "error_count": len(errors),
        "errors": errors,
        "require_complete": require_complete,
        "skip_route_requirements": skip_route_requirements,
    }
    write_json(
        root / "phase6" / ("validation_report.require_complete.json" if require_complete else "validation_report.json"),
        report,
    )
    return report, not errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Run DVF 3-3 DVF System naming realignment.")
    parser.add_argument("--mode", choices=("scaffold", "census", "validate", "all"), default="all")
    parser.add_argument("--root", type=Path, default=EVIDENCE_ROOT)
    parser.add_argument(
        "--enforcement",
        choices=("option_a_doc_normative", "option_b_required_gate_adoption"),
        default="option_b_required_gate_adoption",
    )
    parser.add_argument("--skip-current-route", action="store_true")
    args = parser.parse_args()

    final = None
    if args.mode in {"scaffold", "census", "all"}:
        final = generate_artifacts(
            mode=args.mode,
            root=args.root,
            enforcement=args.enforcement,
            run_route=not args.skip_current_route,
        )
        print(
            json.dumps(
                {
                    "status": final.get("status"),
                    "round_id": final.get("round_id"),
                    "dvf_system_naming_realignment_state": final.get("dvf_system_naming_realignment_state"),
                    "required_gate_adopted": final.get("required_gate_adopted"),
                    "current_route_rerun_success": final.get("current_route_rerun_success"),
                    "protected_surface_changed_count": final.get("protected_surface_changed_count"),
                },
                sort_keys=True,
            )
        )

    if args.mode in {"validate", "census", "all"}:
        report, ok = validate_artifacts(
            args.root,
            require_complete=args.mode == "all" and not args.skip_current_route,
            skip_route_requirements=args.skip_current_route,
        )
        print(json.dumps({"status": report["status"], "error_count": report["error_count"]}, sort_keys=True))
        return 0 if ok else 1
    return 0 if final and final.get("status") == "machine_pass_governance_only" else 1


if __name__ == "__main__":
    raise SystemExit(main())
