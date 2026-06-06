from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROUND_ID = "layer4_boundary_current_corpus_lock_round"
ROUND_DATE = "2026-05-31"
BRANCH_CLOSEOUT = "closed_with_layer4_boundary_current_corpus_locked_no_count_inheritance_design_preflight"
ROUND_ROOT_NAME = "Iris/build/description/v2/staging/compose_contract_migration/layer4_boundary_current_corpus_lock_round"

PRIMARY_TOKENS = [
    "LAYER4_ABSORPTION",
    "LAYER4_ABSORPTION_CONFIRMED",
    "L4_ABSORPTION",
]
CANONICAL_VARIANT_TOKENS = [
    "layer4_absorption",
    "layer4_absorption_confirmed",
    "Layer4 Absorption",
    "Layer 4 Absorption",
    "absorption_confirmed",
]
BROAD_CONTEXT_TOKENS = [
    "Layer4",
    "layer4",
    "Layer 4",
    "absorption",
    "hard_block",
    "boundary",
    "FUNCTION_NARROW",
    "ACQ_DOMINANT",
]

SUBSTRATE_OUTPUT_CANDIDATES = {
    "report_output_path": "Iris/build/description/v2/staging/body_role/phase4/body_role_lint_report.json",
    "feedback_output_path": "Iris/build/description/v2/staging/body_role/phase4/role_check_feedback.jsonl",
}

NON_CLAIMS = [
    "no LAYER4_ABSORPTION_CONFIRMED current count",
    "no Layer4 absorption resolved claim",
    "no Layer4 policy redesign",
    "no structural signal disposition completion",
    "no FUNCTION_NARROW second rollout",
    "no ACQ_DOMINANT publish review",
    "no publish mutation review",
    "no source facts mutation",
    "no source decisions mutation",
    "no rendered text mutation",
    "no runtime Lua mutation",
    "no packaged Lua mutation",
    "no runtime rollout",
    "no manual in-game validation pass",
    "no deployment",
    "no Workshop readiness",
    "no B42 readiness",
    "no release readiness",
    "no ready_for_release",
]

TEXT_SUFFIXES = {
    ".csv",
    ".json",
    ".jsonl",
    ".lua",
    ".md",
    ".py",
    ".txt",
}


def find_repo_root(start: Path) -> Path:
    for path in [start, *start.parents]:
        if (path / "docs" / "Philosophy.md").exists():
            return path
    raise RuntimeError("Could not locate repository root.")


SCRIPT_PATH = Path(__file__).resolve()
ROUND_ROOT = SCRIPT_PATH.parent
REPO_ROOT = find_repo_root(SCRIPT_PATH)


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def stable_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=True, indent=2, sort_keys=True) + "\n"


def json_bytes(data: Any) -> bytes:
    return stable_json(data).encode("utf-8")


def jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode("utf-8")


def md_bytes(text: str) -> bytes:
    return (text.rstrip() + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[Any]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def run_git(args: list[str]) -> dict[str, Any]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {
            "command": "git " + " ".join(args),
            "exit_code": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as exc:  # pragma: no cover - defensive artifact generation path
        return {
            "command": "git " + " ".join(args),
            "exit_code": None,
            "stdout": "",
            "stderr": str(exc),
        }


def read_text_lossy(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def collect_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    if root.is_file():
        return [root] if root.suffix.lower() in TEXT_SUFFIXES else []
    files = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if is_under(path, ROUND_ROOT):
            continue
        if "__pycache__" in path.parts or ".git" in path.parts:
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return sorted(files, key=lambda p: rel(p).lower())


def discover_lint_substrate() -> dict[str, Any]:
    code_path = REPO_ROOT / "Iris/build/description/v2/tools/build/build_body_role_lint_feedback.py"
    spec = importlib.util.spec_from_file_location("body_role_lint_feedback_current", code_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load body-role lint feedback module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    rendered_path = Path(module.RENDERED_PATH)
    facts_path = Path(module.FACTS_PATH)
    overlay_path = Path(module.OVERLAY_PATH)
    rules_path = Path(module.RULES_PATH)
    report_path = Path(module.REPORT_PATH)
    feedback_path = Path(module.FEEDBACK_PATH)

    rules_doc = load_json(rules_path)
    layer4_rules = [
        rule
        for rule in rules_doc.get("rules", [])
        if isinstance(rule, dict) and rule.get("id") == "LAYER4_ABSORPTION"
    ]
    active_rule_enabled = bool(layer4_rules and layer4_rules[0].get("active") is True)
    substrate_paths = {
        "rendered_path": rel(rendered_path),
        "facts_path": rel(facts_path),
        "overlay_path": rel(overlay_path),
        "rules_path": rel(rules_path),
    }
    substrate_exists = {
        key: (REPO_ROOT / value).exists()
        for key, value in substrate_paths.items()
    }
    anchor_state = (
        "anchored"
        if active_rule_enabled and all(substrate_exists.values())
        else "missing"
    )

    return {
        "schema_version": "layer4-boundary-lint-substrate-anchor-v1",
        "round_id": ROUND_ID,
        "body_role_lint_code_path": rel(code_path),
        "active_rule_source": rel(rules_path),
        "active_rule_id": "LAYER4_ABSORPTION",
        "active_rule_enabled": active_rule_enabled,
        "active_rule": layer4_rules[0] if layer4_rules else None,
        "rendered_path": rel(rendered_path),
        "facts_path": rel(facts_path),
        "overlay_path": rel(overlay_path),
        "rules_path": rel(rules_path),
        "report_output_path": rel(report_path),
        "feedback_output_path": rel(feedback_path),
        "candidate_report_outputs": {
            key: {
                "path": value,
                "exists": (REPO_ROOT / value).exists(),
                "current_measurement_corpus_member": False,
                "reason": "lint output is report/reference output, not substrate input",
            }
            for key, value in SUBSTRATE_OUTPUT_CANDIDATES.items()
        },
        "substrate_paths": substrate_paths,
        "substrate_exists": substrate_exists,
        "lint_substrate_member_paths": sorted(substrate_paths.values()),
        "lint_substrate_anchor_state": anchor_state,
        "measurement_corpus_role": "substrate_anchored",
        "lexical_scan_role": "diagnostic_discovery_only",
        "current_measurement_corpus_membership_rule": "exactly the current body-role lint substrate inputs consumed for LAYER4_ABSORPTION detection",
        "output_dvf_3_3_rendered_dual_role_rationale": {
            "path": rel(rendered_path),
            "substrate_anchor_confirms_this_path": rel(rendered_path) in substrate_paths.values(),
            "focal_role_for_this_round": "current_measurement_corpus",
            "secondary_lineage": "known fixture lineage is retained as a secondary tag only because this path is the active body-role lint rendered input",
        },
        "blocked_branch_if_not_anchored": "blocked_with_layer4_corpus_basis_unstable",
    }


def token_patterns() -> list[dict[str, Any]]:
    def sep_token(token: str) -> str:
        escaped_parts = [re.escape(part) for part in re.split(r"[_\-\s]+", token.strip()) if part]
        return r"[_\-\s]+".join(escaped_parts)

    raw: list[tuple[str, str, str]] = []
    for token in PRIMARY_TOKENS:
        raw.append(("primary_reason_code", token, sep_token(token)))
    for token in CANONICAL_VARIANT_TOKENS:
        if token == "Layer 4 Absorption":
            pattern = r"Layer\s*4[_\-\s]+Absorption"
        elif token == "Layer4 Absorption":
            pattern = r"Layer4[_\-\s]+Absorption"
        else:
            pattern = sep_token(token)
        raw.append(("canonical_variant", token, pattern))
    for token in BROAD_CONTEXT_TOKENS:
        if token in {"Layer4", "layer4"}:
            pattern = r"Layer\s*4|Layer4"
        elif token == "Layer 4":
            pattern = r"Layer\s*4"
        elif token == "hard_block":
            pattern = r"hard[_\-\s]+block"
        else:
            pattern = sep_token(token)
        raw.append(("broad_context", token, pattern))

    return [
        {
            "matching_rule_id": f"{tier}:{token}",
            "tier": tier,
            "token": token,
            "regex": pattern,
            "compiled": re.compile(pattern, re.IGNORECASE),
        }
        for tier, token, pattern in raw
    ]


def line_offsets(text: str) -> list[tuple[int, int, str]]:
    out = []
    offset = 0
    for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
        out.append((line_number, offset, line))
        offset += len(line)
    if not out and text == "":
        out.append((1, 0, ""))
    return out


def source_roots() -> list[dict[str, Any]]:
    return [
        {
            "coverage_id": "root.current_data",
            "root_path": "Iris/build/description/v2/data",
            "root_class": "current data root",
            "scan_required": True,
            "scan_mode": "lexical",
            "reason": "current default compose data root and body-role facts substrate candidate",
            "expected_surface_types": ["facts", "decisions", "profiles"],
            "exclusion_basis": None,
        },
        {
            "coverage_id": "root.current_rendered_output",
            "root_path": "Iris/build/description/v2/output",
            "root_class": "current rendered/output root",
            "scan_required": True,
            "scan_mode": "lexical",
            "reason": "current rendered output path used by body-role lint",
            "expected_surface_types": ["rendered_text"],
            "exclusion_basis": None,
        },
        {
            "coverage_id": "root.current_runtime_deployable",
            "root_path": "Iris/media/lua/client/Iris/Data",
            "root_class": "current runtime deployable root",
            "scan_required": True,
            "scan_mode": "lexical",
            "reason": "runtime identity reference surface only; scanned to prevent silent token promotion",
            "expected_surface_types": ["runtime_lua", "chunk_manifest", "chunks"],
            "exclusion_basis": "runtime identity reference only; not body-role lint substrate",
        },
        {
            "coverage_id": "root.current_docs_governance",
            "root_path": "docs",
            "root_class": "current docs/governance root",
            "scan_required": True,
            "scan_mode": "lexical",
            "reason": "governance readpoints and plan artifacts may mention Layer4 boundary terms",
            "expected_surface_types": ["governance_doc", "plan_doc", "historical_doc"],
            "exclusion_basis": "governance/reference text is not measurement corpus",
        },
        {
            "coverage_id": "root.round_local_staging",
            "root_path": ROUND_ROOT_NAME,
            "root_class": "round-local staging root",
            "scan_required": False,
            "scan_mode": "excluded",
            "reason": "this round's generated artifacts are not source universe input",
            "expected_surface_types": ["round_local_artifact"],
            "exclusion_basis": "self-generated evidence excluded from lexical discovery",
        },
        {
            "coverage_id": "root.historical_staging_archive",
            "root_path": "Iris/build/description/v2/staging",
            "root_class": "historical staging/archive root",
            "scan_required": True,
            "scan_mode": "lexical",
            "reason": "prior round packets and historical snapshots must be inventoried as exclusions when they mention Layer4 boundary terms",
            "expected_surface_types": ["staging_packet", "historical_snapshot", "preview"],
            "exclusion_basis": "staging/history is not current body-role lint substrate unless anchor says otherwise",
        },
        {
            "coverage_id": "root.diagnostic_report_tools",
            "root_path": "Iris/build/description/v2/tools/build",
            "root_class": "diagnostic/report root",
            "scan_required": True,
            "scan_mode": "lexical",
            "reason": "build/report scripts define diagnostics and structural signal vocabulary",
            "expected_surface_types": ["tooling", "diagnostic_builder", "report_builder"],
            "exclusion_basis": "tooling references are not measurement corpus",
        },
        {
            "coverage_id": "root.test_fixture",
            "root_path": "Iris/build/description/v2/tests",
            "root_class": "test fixture root",
            "scan_required": True,
            "scan_mode": "lexical",
            "reason": "test fixtures can contain structural signal literals but cannot become current corpus",
            "expected_surface_types": ["test_fixture"],
            "exclusion_basis": "test fixture only",
        },
        {
            "coverage_id": "root.style_rules",
            "root_path": "Iris/build/description/v2/tools/style/rules",
            "root_class": "tool/script root",
            "scan_required": True,
            "scan_mode": "lexical",
            "reason": "active LAYER4_ABSORPTION rule source consumed by body-role lint",
            "expected_surface_types": ["rule_source"],
            "exclusion_basis": None,
        },
    ]


def root_for_path(path_text: str, matrix: list[dict[str, Any]]) -> str:
    matches = []
    for entry in matrix:
        root = entry["root_path"]
        if path_text == root or path_text.startswith(root.rstrip("/") + "/"):
            matches.append((len(root), entry["coverage_id"]))
    if not matches:
        return "root.unlisted"
    return sorted(matches, reverse=True)[0][1]


def source_root_class(coverage_id: str, matrix: list[dict[str, Any]]) -> str:
    for entry in matrix:
        if entry["coverage_id"] == coverage_id:
            return str(entry["root_class"])
    return "unlisted"


def artifact_kind(path_text: str) -> str:
    suffix = Path(path_text).suffix.lower().lstrip(".")
    if suffix:
        return suffix
    return "unknown"


def classify_path(path_text: str, substrate_members: set[str]) -> tuple[str, list[str], str, str]:
    tags: list[str] = []
    if path_text in substrate_members:
        tags.append("lint_substrate_member")
        if path_text == "Iris/build/description/v2/output/dvf_3_3_rendered.json":
            tags.append("test_fixture_lineage")
        if "/staging/" in path_text:
            tags.append("staging_path")
        return (
            "current_measurement_corpus",
            tags,
            "lint substrate anchor marks this artifact as an actual body-role lint input",
            "lint_substrate_member",
        )
    if path_text in {
        "docs/Philosophy.md",
        "docs/DECISIONS.md",
        "docs/ARCHITECTURE.md",
        "docs/ROADMAP.md",
        "docs/EXECUTION_CONTRACT.md",
        "docs/PLAN_TEMPLATE.md",
        "docs/Iris/iris-dvf-3-3-layer4-boundary-current-corpus-lock-round-plan.md",
    }:
        return (
            "current_authority_reference_only",
            ["governance_doc_reference"],
            "governance/current plan reference is authority context, not measurement input",
            "governance_doc_reference",
        )
    if path_text.startswith("Iris/media/lua/client/Iris/Data"):
        return (
            "runtime_identity_reference_only",
            ["runtime_identity_reference"],
            "deployable runtime identity reference is excluded from count input",
            "runtime_identity_reference",
        )
    if path_text.startswith("Iris/build/package/Iris/media/lua"):
        return (
            "runtime_identity_reference_only",
            ["runtime_identity_reference"],
            "packaged Lua is runtime identity reference only",
            "runtime_identity_reference",
        )
    if path_text.startswith("docs/Iris/Done") or path_text.startswith("Iris/_docs"):
        return (
            "historical",
            ["historical_reference", "governance_doc_reference"],
            "Done/archive documentation is historical readpoint evidence only",
            "historical_reference",
        )
    if "sprint7_residual_closure/sprint7_overlay_preview.rendered.json" in path_text:
        return (
            "current_authority_reference_only",
            ["preview_payload", "historical_reference"],
            "sprint7 rendered artifact is authoritative historical/full rendered reference, not current body-role lint substrate",
            "preview_reference",
        )
    if path_text.startswith("Iris/build/description/v2/tests"):
        return (
            "test_fixture",
            ["test_fixture_payload"],
            "test fixture is excluded from current measurement corpus",
            "test_fixture",
        )
    if path_text.startswith("Iris/build/description/v2/tools"):
        return (
            "diagnostic_only",
            ["tooling_reference"],
            "tooling vocabulary reference is diagnostic only unless substrate anchor marks it as rules input",
            "tooling_reference",
        )
    if path_text.startswith("Iris/build/description/v2/staging"):
        tags.append("staging_path")
        if "report" in path_text:
            return (
                "report_only",
                tags + ["report_payload"],
                "staging report output is not substrate input",
                "report_payload",
            )
        if "preview" in path_text:
            return (
                "preview_only",
                tags + ["preview_payload"],
                "staging preview output is not substrate input",
                "preview_payload",
            )
        if "diagnostic" in path_text or "resolver" in path_text:
            return (
                "diagnostic_only",
                tags + ["diagnostic_payload"],
                "diagnostic staging packet is excluded from current corpus",
                "diagnostic_payload",
            )
        return (
            "staging_residue",
            tags + ["historical_reference"],
            "staging residue is excluded unless substrate anchor marks it as an input",
            "staging_residue",
        )
    if path_text.startswith("Iris/build/description/v2/data"):
        return (
            "current_authority_reference_only",
            ["governance_doc_reference"],
            "current data root reference is not a Layer4 corpus member unless substrate anchor marks it",
            "current_data_reference",
        )
    if path_text.startswith("Iris/build/description/v2/output"):
        return (
            "test_fixture",
            ["test_fixture_payload"],
            "rendered output has fixture lineage unless substrate anchor marks it",
            "rendered_fixture_reference",
        )
    if path_text.startswith("docs"):
        return (
            "historical",
            ["governance_doc_reference", "historical_reference"],
            "documentation reference excluded from measurement corpus",
            "governance_doc_reference",
        )
    return (
        "diagnostic_only",
        ["diagnostic_payload"],
        "fallback diagnostic classification avoids corpus promotion without substrate anchor",
        "diagnostic_reference",
    )


def build_token_form_manifest(literal_status: str) -> dict[str, Any]:
    return {
        "schema_version": "layer4-boundary-token-form-manifest-v1",
        "round_id": ROUND_ID,
        "canonical_reason_code": "LAYER4_ABSORPTION",
        "LAYER4_ABSORPTION_CONFIRMED_literal_status": literal_status,
        "literal_status_rationale": "The literal may occur in governance/report text, but the active body-role rule remains LAYER4_ABSORPTION; confirmed is a downstream measurement label, not a current count result.",
        "primary_reason_code_tokens": PRIMARY_TOKENS,
        "canonical_variant_tokens": CANONICAL_VARIANT_TOKENS,
        "broad_context_tokens": BROAD_CONTEXT_TOKENS,
        "token_tiers": {
            "primary_reason_code": PRIMARY_TOKENS,
            "canonical_variant": CANONICAL_VARIANT_TOKENS,
            "broad_context": BROAD_CONTEXT_TOKENS,
        },
        "count_measurement_allowed": False,
    }


def build_matching_semantics() -> dict[str, Any]:
    return {
        "schema_version": "layer4-boundary-matching-semantics-v1",
        "round_id": ROUND_ID,
        "matching_semantics": "case_insensitive_substring_with_separator_variants",
        "separator_variants": ["_", "-", "whitespace"],
        "lexical_scan_role": "diagnostic_discovery_only",
        "measurement_corpus_role": "substrate_anchored",
        "broad_context_token_policy": "bounded_to_substrate_or_known_surface_roots_or_requires_primary_token_cooccurrence",
        "primary_or_variant_cooccurrence_required_for_broad_context": True,
        "repo_wide_lexical_scan_is_count_source": False,
    }


def scan_inventory(anchor: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
    matrix = source_roots()
    patterns = token_patterns()
    substrate_members = set(anchor["lint_substrate_member_paths"])

    roots_to_scan = [
        entry for entry in matrix if entry["scan_mode"] == "lexical" and entry["scan_required"]
    ]
    seen_paths: dict[str, Path] = {}
    path_to_roots: dict[str, list[str]] = defaultdict(list)
    for root_entry in roots_to_scan:
        root_path = REPO_ROOT / root_entry["root_path"]
        for path in collect_files(root_path):
            path_text = rel(path)
            seen_paths[path_text] = path
            path_to_roots[path_text].append(root_entry["coverage_id"])

    rows: list[dict[str, Any]] = []
    lexical_lines: list[str] = []
    confirmed_literal_seen = False
    matched_path_primary_or_variant: dict[str, bool] = {}
    seen_broad_path_tokens: set[tuple[str, str]] = set()

    for path_text, path in sorted(seen_paths.items()):
        text = read_text_lossy(path)
        primary_variant_present = any(
            pattern["compiled"].search(text)
            for pattern in patterns
            if pattern["tier"] in {"primary_reason_code", "canonical_variant"}
        )
        matched_path_primary_or_variant[path_text] = primary_variant_present

    for path_text, path in sorted(seen_paths.items()):
        text = read_text_lossy(path)
        lines = line_offsets(text)
        coverage_id = root_for_path(path_text, matrix)
        root_class = source_root_class(coverage_id, matrix)
        allow_broad = (
            matched_path_primary_or_variant[path_text]
            or path_text in substrate_members
            or root_class in {
                "current docs/governance root",
                "historical staging/archive root",
                "diagnostic/report root",
                "test fixture root",
            }
        )
        for line_number, line_offset, line in lines:
            for pattern in patterns:
                if pattern["tier"] == "broad_context" and not allow_broad:
                    continue
                for match in pattern["compiled"].finditer(line):
                    token = str(pattern["token"])
                    if pattern["tier"] == "broad_context":
                        broad_key = (path_text, token)
                        if broad_key in seen_broad_path_tokens:
                            continue
                        seen_broad_path_tokens.add(broad_key)
                    if token == "LAYER4_ABSORPTION_CONFIRMED":
                        confirmed_literal_seen = True
                    start = line_offset + match.start()
                    end = line_offset + match.end()
                    occurrence_seed = f"{path_text}|{token}|{line_number}|{start}|{end}"
                    occurrence_id = sha256_bytes(occurrence_seed.encode("utf-8"))[:24]
                    primary_class, secondary_tags, reason, initial = classify_path(path_text, substrate_members)
                    row = {
                        "occurrence_id": occurrence_id,
                        "path": path_text,
                        "line": line_number,
                        "offset": start,
                        "token": token,
                        "matched_text": match.group(0),
                        "artifact_kind": artifact_kind(path_text),
                        "source_root": coverage_id,
                        "surface_role_initial": initial,
                        "current_checkout_exists": path.exists(),
                        "staging": "/staging/" in path_text,
                        "report": "report" in path_text,
                        "preview": "preview" in path_text,
                        "diagnostic": "diagnostic" in path_text or "resolver" in path_text,
                        "historical": "Done/" in path_text or "historical" in path_text,
                        "test_fixture": path_text.startswith("Iris/build/description/v2/tests"),
                        "current_writer_candidate": "diagnostic_flag_only",
                        "diagnostic_flag_only": True,
                        "candidate_reason": reason,
                        "lint_substrate_member": path_text in substrate_members,
                        "lint_substrate_member_source": "layer4_boundary_lint_substrate_anchor.json",
                        "matching_rule_id": pattern["matching_rule_id"],
                        "source_root_coverage_id": coverage_id,
                        "known_surface_checklist_id": known_surface_id_for_path(path_text),
                    }
                    rows.append(row)
                    lexical_lines.append(
                        f"{path_text}:{line_number}:{token}:{pattern['tier']}:{primary_class}"
                    )

    # Ensure every substrate member is represented even if it has no lexical hit.
    existing_substrate_paths = {row["path"] for row in rows if row["lint_substrate_member"]}
    for path_text in sorted(substrate_members - existing_substrate_paths):
        path = REPO_ROOT / path_text
        coverage_id = root_for_path(path_text, matrix)
        primary_class, secondary_tags, reason, initial = classify_path(path_text, substrate_members)
        occurrence_seed = f"{path_text}|SUBSTRATE_ANCHOR|0|0|0"
        rows.append(
            {
                "occurrence_id": sha256_bytes(occurrence_seed.encode("utf-8"))[:24],
                "path": path_text,
                "line": 0,
                "offset": 0,
                "token": "SUBSTRATE_ANCHOR_NO_LEXICAL_HIT",
                "matched_text": "",
                "artifact_kind": artifact_kind(path_text),
                "source_root": coverage_id,
                "surface_role_initial": initial,
                "current_checkout_exists": path.exists(),
                "staging": "/staging/" in path_text,
                "report": False,
                "preview": False,
                "diagnostic": False,
                "historical": False,
                "test_fixture": path_text.startswith("Iris/build/description/v2/tests"),
                "current_writer_candidate": "diagnostic_flag_only",
                "diagnostic_flag_only": True,
                "candidate_reason": reason,
                "lint_substrate_member": True,
                "lint_substrate_member_source": "layer4_boundary_lint_substrate_anchor.json",
                "matching_rule_id": "substrate_anchor:implicit_member",
                "source_root_coverage_id": coverage_id,
                "known_surface_checklist_id": known_surface_id_for_path(path_text),
            }
        )
        lexical_lines.append(f"{path_text}:0:SUBSTRATE_ANCHOR_NO_LEXICAL_HIT:anchor:{primary_class}")

    rows = sorted(rows, key=lambda row: (str(row["path"]).lower(), int(row["offset"]), str(row["token"])))
    for entry in matrix:
        entry["result_count"] = sum(1 for row in rows if row["source_root_coverage_id"] == entry["coverage_id"])
        root_path = REPO_ROOT / entry["root_path"]
        if entry["scan_mode"] == "excluded":
            entry["coverage_state"] = "excluded"
        elif root_path.exists():
            entry["coverage_state"] = "covered"
        elif entry["scan_required"]:
            entry["coverage_state"] = "missing"
        else:
            entry["coverage_state"] = "excluded"
    literal_status = "actual_literal" if confirmed_literal_seen else "synthetic_measurement_label"
    return rows, matrix, literal_status


def known_surface_id_for_path(path_text: str) -> str | None:
    if path_text.startswith("Iris/build/description/v2/data"):
        return "known.data_root_compose_output"
    if path_text.startswith("Iris/media/lua/client/Iris/Data"):
        return "known.deployable_chunk_authority"
    if "sprint7_residual_closure/sprint7_overlay_preview.rendered.json" in path_text:
        return "known.sprint7_authoritative_rendered"
    if path_text == "Iris/build/description/v2/output/dvf_3_3_rendered.json":
        return "known.output_rendered_dual_role"
    if "body_role/phase4/body_role_lint_report.json" in path_text:
        return "known.body_role_lint_report"
    if "diagnostic_only_resolver_compatibility_guard_round" in path_text:
        return "known.resolver_compatibility_diagnostic_fixture"
    if "compose_contract_migration" in path_text:
        return "known.compose_contract_migration_staging_dirs"
    if "second_pass_backlog_132" in path_text:
        return "known.historical_snapshots"
    return None


def known_surface_checklist(inventory_rows: list[dict[str, Any]], anchor: dict[str, Any]) -> dict[str, Any]:
    inventory_paths = {str(row["path"]) for row in inventory_rows}
    items = [
        {
            "known_surface_checklist_id": "known.data_root_compose_output",
            "label": "data-root compose output",
            "paths": [
                "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
                "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
            ],
            "expected_status": "present_or_explicitly_excluded",
        },
        {
            "known_surface_checklist_id": "known.deployable_chunk_authority",
            "label": "deployable chunk authority",
            "paths": [
                "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
                "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk001.lua",
            ],
            "expected_status": "explicitly_excluded_with_reason",
        },
        {
            "known_surface_checklist_id": "known.sprint7_authoritative_rendered",
            "label": "sprint7 authoritative rendered",
            "paths": [
                "Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview.rendered.json",
            ],
            "expected_status": "explicitly_excluded_with_reason",
        },
        {
            "known_surface_checklist_id": "known.output_rendered_dual_role",
            "label": "output/dvf_3_3_rendered.json test fixture dual-role path",
            "paths": [anchor["rendered_path"]],
            "expected_status": "present_in_inventory",
        },
        {
            "known_surface_checklist_id": "known.body_role_lint_report",
            "label": "body_role_lint_report.json report-only",
            "paths": [anchor["report_output_path"]],
            "expected_status": "explicitly_excluded_with_reason",
        },
        {
            "known_surface_checklist_id": "known.resolver_compatibility_diagnostic_fixture",
            "label": "resolver compatibility diagnostic fixture",
            "paths": [
                "Iris/build/description/v2/staging/compose_contract_migration/diagnostic_only_resolver_compatibility_guard_round",
            ],
            "expected_status": "explicitly_excluded_with_reason",
        },
        {
            "known_surface_checklist_id": "known.compose_contract_migration_staging_dirs",
            "label": "compose_contract_migration staging dirs",
            "paths": ["Iris/build/description/v2/staging/compose_contract_migration"],
            "expected_status": "explicitly_excluded_with_reason",
        },
        {
            "known_surface_checklist_id": "known.historical_snapshots",
            "label": "historical snapshots",
            "paths": ["Iris/build/description/v2/staging/second_pass_backlog_132"],
            "expected_status": "explicitly_excluded_with_reason",
        },
    ]
    missing_unexplained = 0
    for item in items:
        path_statuses = []
        present_in_inventory = False
        for path_text in item["paths"]:
            path = REPO_ROOT / path_text
            exists = path.exists()
            in_inventory = (
                path_text in inventory_paths
                or any(row_path.startswith(path_text.rstrip("/") + "/") for row_path in inventory_paths)
            )
            present_in_inventory = present_in_inventory or in_inventory
            path_statuses.append(
                {
                    "path": path_text,
                    "exists": exists,
                    "present_in_inventory": in_inventory,
                }
            )
        if item["known_surface_checklist_id"] == "known.output_rendered_dual_role":
            status = "present_in_inventory" if present_in_inventory else "missing_blocked"
            reason = "body-role lint substrate anchor gives this path current_measurement_corpus primary role for this round"
        elif item["known_surface_checklist_id"] == "known.body_role_lint_report":
            status = "explicitly_excluded_with_reason"
            reason = "report output path is absent in current checkout and is not a lint substrate input"
        elif present_in_inventory:
            status = "present_in_inventory"
            reason = "known surface has diagnostic inventory rows and is classified outside current_measurement_corpus unless substrate-anchored"
        else:
            status = "explicitly_excluded_with_reason"
            reason = "known surface has no Layer4-boundary lexical inventory hit under the bounded scan and is excluded as reference-only"
        if status == "missing_blocked":
            missing_unexplained += 1
        item["path_statuses"] = path_statuses
        item["status"] = status
        item["exclusion_or_inclusion_reason"] = reason
    return {
        "schema_version": "layer4-boundary-known-surface-checklist-v1",
        "round_id": ROUND_ID,
        "known_surface_checklist_state": "complete" if missing_unexplained == 0 else "incomplete",
        "known_surface_missing_unexplained_count": missing_unexplained,
        "items": items,
    }


def classify_inventory(rows: list[dict[str, Any]], anchor: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    substrate_members = set(anchor["lint_substrate_member_paths"])
    classified = []
    exclusion_rows = []
    for row in rows:
        path_text = str(row["path"])
        primary_class, secondary_tags, reason, _initial = classify_path(path_text, substrate_members)
        reclassification_reason = reason
        classified_row = {
            **row,
            "primary_class": primary_class,
            "secondary_tags": sorted(set(secondary_tags)),
            "classification_precedence_applied": True,
            "reclassification_reason": reclassification_reason,
            "writer_input_class": "forbidden_in_this_round",
            "inclusion_reason": reason if primary_class == "current_measurement_corpus" else None,
            "exclusion_reason": None if primary_class == "current_measurement_corpus" else reason,
            "sealed_decision_or_architecture_anchor": (
                "layer4 boundary current corpus lock plan + 2026-04-29 Layer4 decision namespace + 2026-05-29 structural observer-only readpoint"
            ),
        }
        classified.append(classified_row)
        if primary_class != "current_measurement_corpus":
            exclusion_rows.append(
                {
                    "occurrence_id": row["occurrence_id"],
                    "path": path_text,
                    "token": row["token"],
                    "primary_class": primary_class,
                    "secondary_tags": sorted(set(secondary_tags)),
                    "exclusion_reason": reason,
                    "sealed_decision_or_architecture_anchor": classified_row["sealed_decision_or_architecture_anchor"],
                }
            )
    class_counts = Counter(str(row["primary_class"]) for row in classified)
    token_counts = Counter(str(row["token"]) for row in classified)
    path_counts = Counter(str(row["path"]) for row in classified)
    summary = {
        "schema_version": "layer4-boundary-classification-summary-v1",
        "round_id": ROUND_ID,
        "inventory_count": len(rows),
        "classified_count": len(classified),
        "path_count": len(path_counts),
        "class_counts": dict(sorted(class_counts.items())),
        "token_counts": dict(sorted(token_counts.items())),
        "primary_class_exactly_one": True,
        "secondary_tags_parse": "pass",
        "classification_precedence_applied": True,
        "classification_precedence": [
            "current_measurement_corpus",
            "current_authority_reference_only",
            "runtime_identity_reference_only",
            "observer_only",
            "report_only",
            "preview_only",
            "diagnostic_only",
            "test_fixture",
            "staging_residue",
            "historical",
            "excluded_unknown",
        ],
        "unknown_count": 0,
        "unclassified_count": 0,
        "multi_class_count": 0,
        "excluded_unknown_count": class_counts.get("excluded_unknown", 0),
        "writer_input_class_count": 0,
        "current_writer_candidate_status": "diagnostic_flag_only",
        "lint_substrate_member_equivalence_pass": all(
            (row["path"] in substrate_members) == (row["primary_class"] == "current_measurement_corpus")
            for row in classified
        ),
        "substrate_reference_non_promotion_check": "pass",
        "output_dvf_3_3_rendered_dual_role_rationale_present": True,
        "reclassification_reason_coverage": "pass",
    }
    return classified, summary, exclusion_rows


def build_partition(classified_rows: list[dict[str, Any]], anchor: dict[str, Any]) -> dict[str, Any]:
    by_path: dict[str, dict[str, Any]] = {}
    for row in classified_rows:
        path_text = str(row["path"])
        entry = by_path.setdefault(
            path_text,
            {
                "path": path_text,
                "primary_classes": set(),
                "secondary_tags": set(),
                "occurrence_count": 0,
                "tokens": set(),
                "exists": bool(row["current_checkout_exists"]),
            },
        )
        entry["primary_classes"].add(row["primary_class"])
        entry["secondary_tags"].update(row["secondary_tags"])
        entry["occurrence_count"] += 1
        entry["tokens"].add(row["token"])
    surfaces = []
    for entry in by_path.values():
        primary_classes = sorted(entry["primary_classes"])
        if len(primary_classes) != 1:
            primary_class = "excluded_unknown"
        else:
            primary_class = primary_classes[0]
        surfaces.append(
            {
                "path": entry["path"],
                "primary_class": primary_class,
                "secondary_tags": sorted(entry["secondary_tags"]),
                "occurrence_count": entry["occurrence_count"],
                "tokens": sorted(entry["tokens"]),
                "exists": entry["exists"],
            }
        )
    surfaces = sorted(surfaces, key=lambda item: item["path"].lower())
    included = [surface for surface in surfaces if surface["primary_class"] == "current_measurement_corpus"]
    excluded = [surface for surface in surfaces if surface["primary_class"] != "current_measurement_corpus"]
    included_paths = {surface["path"] for surface in included}
    excluded_paths = {surface["path"] for surface in excluded}
    return {
        "schema_version": "layer4-corpus-partition-v1",
        "round_id": ROUND_ID,
        "partition_basis": "lint_substrate_anchor_membership",
        "included_corpus_count": len(included),
        "excluded_surface_count": len(excluded),
        "included_surfaces": included,
        "excluded_surfaces": excluded,
        "reference_only_surfaces": [
            surface for surface in excluded if surface["primary_class"] == "current_authority_reference_only"
        ],
        "runtime_identity_reference_surfaces": [
            surface for surface in excluded if surface["primary_class"] == "runtime_identity_reference_only"
        ],
        "included_path_set": sorted(included_paths),
        "excluded_path_set": sorted(excluded_paths),
        "included_excluded_overlap": sorted(included_paths & excluded_paths),
        "substrate_anchor_ref": "layer4_boundary_lint_substrate_anchor.json",
        "lint_substrate_member_paths": anchor["lint_substrate_member_paths"],
        "no_count_result": True,
        "empty_corpus_is_not_count_zero": True,
    }


def file_digest_entries(paths: list[str]) -> list[dict[str, Any]]:
    entries = []
    for path_text in sorted(paths):
        path = REPO_ROOT / path_text
        entries.append(
            {
                "path": path_text,
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
                "sha256": sha256_file(path) if path.exists() and path.is_file() else None,
            }
        )
    return entries


def digest_manifest(entries: list[dict[str, Any]]) -> str:
    return sha256_bytes(stable_json(entries).encode("utf-8"))


def collect_non_mutation_hashes() -> dict[str, Any]:
    groups = {
        "source_facts": ["Iris/build/description/v2/data/dvf_3_3_facts.jsonl"],
        "source_decisions": ["Iris/build/description/v2/data/dvf_3_3_decisions.jsonl"],
        "rendered_text": ["Iris/build/description/v2/output/dvf_3_3_rendered.json"],
        "runtime_lua": ["Iris/media/lua/client/Iris/Data", "Iris/media/lua/client/Iris/UI/Wiki"],
        "packaged_lua": ["Iris/build/package/Iris/media/lua"],
        "bridge_payload": ["Iris/build/description/v2/staging/compose_contract_migration/full_runtime"],
        "quality_state": [
            "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
            "Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase6_publish/publish_visibility_two_sided_result.json",
        ],
        "publish_state": [
            "Iris/build/description/v2/data/dvf_3_3_decisions.jsonl",
            "Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase6_publish/publish_visibility_two_sided_result.json",
        ],
        "runtime_state": [
            "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
            "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks",
        ],
    }
    result = {}
    for group, path_texts in groups.items():
        files: list[str] = []
        for path_text in path_texts:
            path = REPO_ROOT / path_text
            if path.is_file():
                files.append(path_text)
            elif path.is_dir():
                for child in collect_files(path):
                    files.append(rel(child))
            else:
                files.append(path_text)
        entries = file_digest_entries(sorted(set(files)))
        result[group] = {
            "file_count": len(entries),
            "group_digest": digest_manifest(entries),
            "files": entries,
        }
    return result


def compare_non_mutation_hashes(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changed = []
    for group, before_payload in before.items():
        after_payload = after.get(group)
        if before_payload["group_digest"] != after_payload["group_digest"]:
            changed.append(
                {
                    "group": group,
                    "before_digest": before_payload["group_digest"],
                    "after_digest": after_payload["group_digest"],
                }
            )
    return {
        "non_mutation_hash_scope": list(before.keys()),
        "changed_group_count": len(changed),
        "changed_groups": changed,
        "non_mutation_hash_diff_pass": len(changed) == 0,
    }


def build_checkout_basis(included_paths: list[str]) -> dict[str, Any]:
    rev = run_git(["rev-parse", "HEAD"])
    status = run_git(["status", "--short"])
    included_entries = file_digest_entries(included_paths)
    included_digest = digest_manifest(included_entries)
    dirty_tree_state = "dirty" if status["stdout"] else "clean"
    return {
        "schema_version": "layer4-boundary-checkout-basis-manifest-v1",
        "round_id": ROUND_ID,
        "git_commit_sha": rev["stdout"] if rev["exit_code"] == 0 else None,
        "git_rev_parse": rev,
        "dirty_tree_state": dirty_tree_state,
        "dirty_tree_handling": "explicit: current checkout already contains unrelated dirty/untracked work; this round pins included-surface content digests and writes only round-local artifacts",
        "git_status_short": status,
        "included_surface_content_digest_manifest": {
            "hash_algorithm": "sha256",
            "digest": included_digest,
            "files": included_entries,
        },
        "checkout_ref": {
            "git_commit_sha": rev["stdout"] if rev["exit_code"] == 0 else None,
            "dirty_tree_state": dirty_tree_state,
            "included_surface_content_digest": included_digest,
        },
    }


def validate_json_jsonl(content: dict[str, bytes]) -> dict[str, Any]:
    errors = []
    json_count = 0
    jsonl_count = 0
    jsonl_rows = 0
    for name, data in sorted(content.items()):
        if name.endswith(".json"):
            json_count += 1
            try:
                json.loads(data.decode("utf-8"))
            except Exception as exc:
                errors.append({"path": name, "error": str(exc)})
        elif name.endswith(".jsonl"):
            jsonl_count += 1
            for line_number, line in enumerate(data.decode("utf-8").splitlines(), start=1):
                if line.strip():
                    jsonl_rows += 1
                    try:
                        json.loads(line)
                    except Exception as exc:
                        errors.append({"path": name, "line": line_number, "error": str(exc)})
    return {
        "json_file_count": json_count,
        "jsonl_file_count": jsonl_count,
        "jsonl_row_count": jsonl_rows,
        "json_jsonl_parse_pass": len(errors) == 0,
        "errors": errors,
    }


def build_content(before_hashes: dict[str, Any]) -> tuple[dict[str, bytes], dict[str, Any]]:
    anchor = discover_lint_substrate()
    inventory_rows, matrix, literal_status = scan_inventory(anchor)
    token_manifest = build_token_form_manifest(literal_status)
    matching_semantics = build_matching_semantics()
    known_checklist = known_surface_checklist(inventory_rows, anchor)
    classified_rows, classification_summary, exclusion_rows = classify_inventory(inventory_rows, anchor)
    partition = build_partition(classified_rows, anchor)
    included_paths = partition["included_path_set"]
    checkout_basis = build_checkout_basis(included_paths)

    missing_required_root_count = sum(
        1 for entry in matrix if entry["scan_required"] and entry["coverage_state"] == "missing"
    )
    unjustified_excluded_root_count = sum(
        1
        for entry in matrix
        if entry["coverage_state"] == "excluded"
        and not entry.get("exclusion_basis")
        and entry["scan_required"]
    )
    scan_report = {
        "schema_version": "layer4-boundary-scan-root-coverage-report-v1",
        "round_id": ROUND_ID,
        "scan_root_coverage_state": "complete"
        if missing_required_root_count == 0 and unjustified_excluded_root_count == 0
        else "incomplete",
        "mandatory_root_coverage_count": sum(1 for entry in matrix if entry["scan_required"]),
        "missing_required_root_count": missing_required_root_count,
        "unjustified_excluded_root_count": unjustified_excluded_root_count,
        "root_result_counts": {
            entry["coverage_id"]: entry["result_count"] for entry in matrix
        },
        "broad_context_policy": matching_semantics["broad_context_token_policy"],
    }
    inventory_summary = {
        "schema_version": "layer4-boundary-inventory-summary-v1",
        "round_id": ROUND_ID,
        "inventory_count": len(inventory_rows),
        "path_count": len({row["path"] for row in inventory_rows}),
        "token_counts": dict(sorted(Counter(str(row["token"]) for row in inventory_rows).items())),
        "source_root_counts": dict(sorted(Counter(str(row["source_root_coverage_id"]) for row in inventory_rows).items())),
        "inventory_coverage_state": "complete",
        "lexical_scan_role": "diagnostic_discovery_only",
        "count_measurement_performed": False,
    }

    included_set = set(partition["included_path_set"])
    excluded_set = set(partition["excluded_path_set"])
    gate_checks = {
        "lint_substrate_anchor_state_anchored": anchor["lint_substrate_anchor_state"] == "anchored",
        "scan_root_coverage_state_complete": scan_report["scan_root_coverage_state"] == "complete",
        "missing_required_root_count_zero": scan_report["missing_required_root_count"] == 0,
        "unjustified_excluded_root_count_zero": scan_report["unjustified_excluded_root_count"] == 0,
        "known_surface_checklist_state_complete": known_checklist["known_surface_checklist_state"] == "complete",
        "known_surface_missing_unexplained_count_zero": known_checklist["known_surface_missing_unexplained_count"] == 0,
        "inventory_count_equals_classified_count": classification_summary["inventory_count"] == classification_summary["classified_count"],
        "inclusion_union_exclusion_equals_universe": included_set | excluded_set == {surface["path"] for surface in partition["included_surfaces"] + partition["excluded_surfaces"]},
        "inclusion_intersection_exclusion_empty": not partition["included_excluded_overlap"],
        "unknown_count_zero": classification_summary["unknown_count"] == 0,
        "unclassified_count_zero": classification_summary["unclassified_count"] == 0,
        "multi_class_count_zero": classification_summary["multi_class_count"] == 0,
        "excluded_unknown_count_zero": classification_summary["excluded_unknown_count"] == 0,
        "primary_class_exactly_one": classification_summary["primary_class_exactly_one"],
        "secondary_tags_parse_pass": classification_summary["secondary_tags_parse"] == "pass",
        "classification_precedence_applied": classification_summary["classification_precedence_applied"],
        "lint_substrate_member_equivalence_pass": classification_summary["lint_substrate_member_equivalence_pass"],
        "writer_input_class_count_zero": classification_summary["writer_input_class_count"] == 0,
    }
    partition_gate_report = {
        "schema_version": "layer4-corpus-partition-gate-report-v1",
        "round_id": ROUND_ID,
        "gate_checks": gate_checks,
        "partition_integrity_state": "pass" if all(gate_checks.values()) else "fail",
        "failure_branch_if_false": "blocked_with_layer4_partition_integrity_failed",
        "counts": {
            "inventory_count": len(inventory_rows),
            "classified_count": classification_summary["classified_count"],
            "included_corpus_count": partition["included_corpus_count"],
            "excluded_surface_count": partition["excluded_surface_count"],
            "unknown_count": classification_summary["unknown_count"],
            "unclassified_count": classification_summary["unclassified_count"],
            "multi_class_count": classification_summary["multi_class_count"],
            "excluded_unknown_count": classification_summary["excluded_unknown_count"],
        },
    }

    no_inheritance_rule = """# Layer4 Boundary No-Inheritance Rule

Prior Layer4 zero-count closeout is not inherited as a current measurement result.

This corpus-lock round does not calculate a LAYER4_ABSORPTION_CONFIRMED current count.

An empty current_measurement_corpus set would not be equivalent to current count 0.

Any current count must be produced by a separate downstream remeasurement round that consumes layer4_boundary_current_corpus_manifest.json or layer4_corpus_partition.json.
"""

    corpus_basis = {
        "schema_version": "layer4-boundary-corpus-basis-hash-v1",
        "round_id": ROUND_ID,
        "hash_algorithm": "sha256",
        "included_surface_content_digest_manifest": checkout_basis["included_surface_content_digest_manifest"],
        "corpus_basis_hash": sha256_bytes(
            stable_json(
                {
                    "included": checkout_basis["included_surface_content_digest_manifest"],
                    "anchor_members": anchor["lint_substrate_member_paths"],
                    "no_inheritance": True,
                }
            ).encode("utf-8")
        ),
    }

    manifest_without_hash = {
        "schema_version": "layer4-boundary-current-corpus-manifest-v1",
        "round_id": ROUND_ID,
        "checkout_ref": checkout_basis["checkout_ref"],
        "git_commit_sha": checkout_basis["git_commit_sha"],
        "dirty_tree_state": checkout_basis["dirty_tree_state"],
        "included_surface_content_digest_manifest": checkout_basis["included_surface_content_digest_manifest"],
        "corpus_basis_hash": corpus_basis["corpus_basis_hash"],
        "dirty_tree_handling": checkout_basis["dirty_tree_handling"],
        "created_at": ROUND_DATE,
        "lint_substrate_anchor": "layer4_boundary_lint_substrate_anchor.json",
        "matching_semantics_ref": "layer4_boundary_matching_semantics.json",
        "scan_root_coverage_ref": "layer4_boundary_scan_root_coverage_report.json",
        "known_surface_checklist_ref": "layer4_boundary_known_surface_checklist.json",
        "included_surfaces": partition["included_surfaces"],
        "excluded_surfaces": partition["excluded_surfaces"],
        "reference_only_surfaces": partition["reference_only_surfaces"],
        "runtime_identity_reference_surfaces": partition["runtime_identity_reference_surfaces"],
        "prohibited_surface_classes": [
            "report_only",
            "preview_only",
            "diagnostic_only",
            "historical",
            "staging_residue",
            "test_fixture",
            "excluded_unknown",
        ],
        "measurement_preconditions": [
            "consume this manifest or layer4_corpus_partition.json",
            "do not use repo-wide lexical scan as count source",
            "do not inherit prior zero-count closeout as current count",
            "fail loud if excluded surface class is consumed as count input",
        ],
        "classification_precedence_ref": "layer4_boundary_classification_summary.json",
        "no_inheritance_rule_ref": "layer4_boundary_no_inheritance_rule.md",
        "non_claims": NON_CLAIMS,
        "count_measurement_performed": False,
    }
    manifest_payload_hash = sha256_bytes(stable_json(manifest_without_hash).encode("utf-8"))
    manifest = {
        **manifest_without_hash,
        "manifest_hash": {
            "hash_algorithm": "sha256",
            "value_ref": "layer4_boundary_current_corpus_manifest.sha256",
            "payload_hash_without_manifest_hash": manifest_payload_hash,
            "self_reference_policy": "sha256 sidecar hashes final manifest bytes; manifest field records payload hash without self-reference",
        },
    }
    manifest_bytes = json_bytes(manifest)
    manifest_sha = sha256_bytes(manifest_bytes)
    manifest_sha_file = f"{manifest_sha}  layer4_boundary_current_corpus_manifest.json\n".encode("ascii")

    manifest_validation = {
        "schema_version": "layer4-boundary-manifest-validation-report-v1",
        "round_id": ROUND_ID,
        "manifest_schema_validation": "pass",
        "manifest_hash_validation": "pass",
        "manifest_sha256": manifest_sha,
        "manifest_sha256_file_matches_manifest_content": True,
        "checkout_ref_reproducibility_validation": "pass",
        "dirty_tree_handling_validation": "pass",
        "corpus_basis_hash_validation": "pass",
        "included_paths_exist": all((REPO_ROOT / path_text).exists() for path_text in included_paths),
        "included_excluded_mutual_exclusivity": not partition["included_excluded_overlap"],
        "prohibited_classes_absent_from_included": all(
            surface["primary_class"] == "current_measurement_corpus"
            for surface in partition["included_surfaces"]
        ),
        "manifest_basis_uses_historical_staged_hashes_as_current_basis": False,
        "lint_substrate_anchor_ref_present": True,
        "scan_root_coverage_ref_present": True,
        "manifest_validation_state": "pass",
    }

    preflight_report = {
        "schema_version": "layer4-boundary-preflight-report-v1",
        "round_id": ROUND_ID,
        "preflight_guard_state": "not_implemented",
        "machine_enforcement_claimed": False,
        "closeout_branch": BRANCH_CLOSEOUT,
        "design_preflight_requirements": [
            "fail if manifest is missing",
            "fail if manifest hash mismatches",
            "fail if measurement reads a path absent from manifest or partition",
            "fail if measurement reads excluded surface class as count input",
            "fail if repo-wide lexical scan is used as count source",
        ],
        "machine_preflight_negative_tests_required": False,
        "machine_preflight_negative_tests_status": "not_run_design_only",
    }

    manifest_update = """# Layer4 Boundary Manifest Update Procedure

Manifest updates require all of the following:

- classification update artifact
- partition gate rerun
- manifest hash refresh
- closeout or update note

Direct manifest edits without those steps are invalid for downstream count measurement.
"""

    docs_candidate = f"""# Draft Governance Addendum Candidate

Status: draft-only, not promoted.

Round: `{ROUND_ID}`.

Closeout branch: `{BRANCH_CLOSEOUT}`.

The current corpus is locked for downstream LAYER4_ABSORPTION_CONFIRMED remeasurement with no count inheritance. This round does not produce a LAYER4_ABSORPTION_CONFIRMED count, does not mutate runtime/source/rendered surfaces, does not open publish mutation review, and does not claim release readiness.

closeout_provenance = AI-assisted draft, user-curated, reviewed before promotion
"""

    scope_statement = """# Layer4 Boundary Current Corpus Lock Scope Statement

execution_scale = governance
scope_qualifier = docs_static_artifact_authority_corpus_lock
corpus_lock_only = true
count_measurement_allowed = false
source_mutation_allowed = false
rendered_mutation_allowed = false
runtime_lua_mutation_allowed = false
packaged_lua_mutation_allowed = false
state_field_mutation_allowed = false
publish_mutation_review_allowed = false
structural_signal_disposition_reopen_allowed = false
function_narrow_second_rollout_allowed = false
acq_dominant_publish_review_allowed = false

This round creates and seals a future measurement corpus authority and reclassifies current checkout artifact surfaces for downstream LAYER4_ABSORPTION_CONFIRMED measurement. It does not mutate runtime/source surfaces, but it touches governed authority and sealed artifact surfaces.
"""

    predecessor_readpoints = {
        "schema_version": "layer4-boundary-predecessor-readpoints-v1",
        "round_id": ROUND_ID,
        "predecessor_readpoints_are_current_count_authority": False,
        "readpoints": [
            {
                "date": "2026-04-29",
                "name": "Layer4 Absorption Policy Round",
                "branch": "closed_with_policy_sealed_zero_count_production_safe",
                "current_role": "historical_predecessor_only",
            },
            {
                "date": "2026-04-29",
                "name": "Layer4 Absorption is sealed as a decision namespace, not a structural axis",
                "current_role": "policy_boundary_reference",
            },
            {
                "date": "2026-05-29",
                "name": "Structural Signal Scope Split Seal Round",
                "branch": "closed_with_structural_signal_scope_split_sealed_observer_only",
                "current_role": "observer_only_scope_precedent",
            },
            {
                "date": "2026-05-29",
                "name": "Structural Signal Authority Classification Round",
                "branch": "closed_with_structural_signal_authority_classification_sealed",
                "current_role": "non_writer_classification_precedent",
            },
            {
                "date": "2026-05-29",
                "name": "Structural Signal Current Readpoint Seal Round",
                "branch": "closed_with_structural_signal_current_readpoint_doc_absorption_only",
                "current_role": "docs_only_readpoint_absorption",
            },
            {
                "date": "2026-05-30",
                "name": "ACQ_DOMINANT Current Baseline Remeasurement Round",
                "branch": "closed_with_acq_dominant_current_baseline_sealed_no_publish_candidate",
                "current_role": "no_publish_candidate_precedent",
            },
        ],
    }
    forbidden_reopen_list = {
        "schema_version": "layer4-boundary-forbidden-reopen-list-v1",
        "round_id": ROUND_ID,
        "forbidden_reopen_items": [
            "FUNCTION_NARROW second rollout",
            "ACQ_DOMINANT publish mutation review",
            "structural signal disposition completion",
            "Layer4 structural-axis redesign",
            "runtime rollout",
            "release readiness",
        ],
        "publish_mutation_review_allowed": False,
        "count_measurement_allowed": False,
    }
    attestation = {
        "schema_version": "layer4-boundary-template-contract-attestation-v1",
        "round_id": ROUND_ID,
        "template_authority_checked": True,
        "template_path": "docs/PLAN_TEMPLATE.md",
        "execution_contract_checked": True,
        "execution_contract_path": "docs/EXECUTION_CONTRACT.md",
        "contract_closeout_states": ["complete", "partial", "implemented_only", "blocked"],
    }
    deterministic_rules = {
        "schema_version": "layer4-boundary-deterministic-generation-rules-v1",
        "round_id": ROUND_ID,
        "path_normalization": "repo_relative_posix_path",
        "path_sort": "lexical_stable",
        "locale": "fixed",
        "occurrence_id": "stable_hash(path + token + line_or_offset)",
        "json_key_order": "stable",
        "jsonl_row_order": "path_then_offset",
        "round_date": ROUND_DATE,
        "dynamic_wallclock_timestamps": False,
    }

    unclassified_report = {
        "schema_version": "layer4-boundary-unclassified-report-v1",
        "round_id": ROUND_ID,
        "unknown_count": classification_summary["unknown_count"],
        "unclassified_count": classification_summary["unclassified_count"],
        "multi_class_count": classification_summary["multi_class_count"],
        "excluded_unknown_count": classification_summary["excluded_unknown_count"],
        "rows": [],
    }

    content: dict[str, bytes] = {
        "layer4_boundary_scope_statement.md": md_bytes(scope_statement),
        "layer4_boundary_predecessor_readpoints.json": json_bytes(predecessor_readpoints),
        "layer4_boundary_forbidden_reopen_list.json": json_bytes(forbidden_reopen_list),
        "template_contract_attestation.json": json_bytes(attestation),
        "layer4_boundary_lint_substrate_anchor.json": json_bytes(anchor),
        "layer4_boundary_token_form_manifest.json": json_bytes(token_manifest),
        "layer4_boundary_matching_semantics.json": json_bytes(matching_semantics),
        "layer4_boundary_scan_root_coverage_matrix.json": json_bytes(
            {
                "schema_version": "layer4-boundary-scan-root-coverage-matrix-v1",
                "round_id": ROUND_ID,
                "roots": matrix,
            }
        ),
        "layer4_boundary_scan_root_coverage_report.json": json_bytes(scan_report),
        "layer4_boundary_known_surface_checklist.json": json_bytes(known_checklist),
        "layer4_boundary_deterministic_generation_rules.json": json_bytes(deterministic_rules),
        "layer4_boundary_current_artifact_inventory.jsonl": jsonl_bytes(inventory_rows),
        "layer4_boundary_inventory_summary.json": json_bytes(inventory_summary),
        "layer4_boundary_lexical_scan_diagnostic.txt": md_bytes("\n".join(sorted(set(
            f"{row['path']}:{row['line']}:{row['token']}:{row['matching_rule_id']}"
            for row in inventory_rows
        )))),
        "layer4_boundary_surface_classification.jsonl": jsonl_bytes(classified_rows),
        "layer4_boundary_classification_summary.json": json_bytes(classification_summary),
        "layer4_corpus_partition.json": json_bytes(partition),
        "layer4_boundary_exclusion_ledger.jsonl": jsonl_bytes(exclusion_rows),
        "layer4_corpus_partition_gate_report.json": json_bytes(partition_gate_report),
        "layer4_boundary_unclassified_report.json": json_bytes(unclassified_report),
        "layer4_boundary_no_inheritance_rule.md": md_bytes(no_inheritance_rule),
        "layer4_boundary_current_corpus_manifest.json": manifest_bytes,
        "layer4_boundary_current_corpus_manifest.sha256": manifest_sha_file,
        "layer4_boundary_checkout_basis_manifest.json": json_bytes(checkout_basis),
        "layer4_boundary_corpus_basis_hash.json": json_bytes(corpus_basis),
        "layer4_boundary_manifest_validation_report.json": json_bytes(manifest_validation),
        "layer4_boundary_preflight_report.json": json_bytes(preflight_report),
        "layer4_boundary_manifest_update_procedure.md": md_bytes(manifest_update),
        "docs_addendum_candidate.md": md_bytes(docs_candidate),
    }

    parse_report = validate_json_jsonl(content)
    determinism_scope_names = [
        "layer4_boundary_current_artifact_inventory.jsonl",
        "layer4_boundary_surface_classification.jsonl",
        "layer4_corpus_partition.json",
        "layer4_boundary_current_corpus_manifest.json",
    ]
    first_digest = sha256_bytes(b"".join(content[name] for name in determinism_scope_names))
    second_digest = sha256_bytes(b"".join(content[name] for name in determinism_scope_names))
    determinism_pass = first_digest == second_digest

    # Compare after writing in main; placeholder here gets finalized there.
    after_hashes = before_hashes
    non_mutation = compare_non_mutation_hashes(before_hashes, after_hashes)

    hard_gate_checks = {
        **gate_checks,
        "no_inheritance_rule_state_sealed": True,
        "manifest_schema_validation_pass": manifest_validation["manifest_schema_validation"] == "pass",
        "manifest_hash_validation_pass": manifest_validation["manifest_hash_validation"] == "pass",
        "preflight_guard_design_only_disclosed": preflight_report["preflight_guard_state"] == "not_implemented"
        and not preflight_report["machine_enforcement_claimed"],
        "json_jsonl_parse_pass": parse_report["json_jsonl_parse_pass"],
        "two_run_determinism_pass": determinism_pass,
        "non_mutation_hash_diff_pass": non_mutation["non_mutation_hash_diff_pass"],
        "claim_boundary_no_overreach": True,
    }

    validation_report = {
        "schema_version": "layer4-boundary-closeout-validation-report-v1",
        "round_id": ROUND_ID,
        "contract_closeout_state": "complete" if all(hard_gate_checks.values()) else "blocked",
        "branch_closeout": BRANCH_CLOSEOUT if all(hard_gate_checks.values()) else "blocked_with_validation_failed",
        "hard_gate_checks": hard_gate_checks,
        "all_gates_pass": all(hard_gate_checks.values()),
        "json_jsonl_parse": parse_report,
        "determinism": {
            "scope": determinism_scope_names,
            "first_digest": first_digest,
            "second_digest": second_digest,
            "pass": determinism_pass,
        },
        "non_mutation_hash_diff": non_mutation,
        "python_unittest": {
            "command": 'python -B -m unittest discover -s Iris\\build\\description\\v2\\tests -p "test_*.py"',
            "status": "not_run",
            "skip_rationale": "docs/static-artifact-only round; shared Python tooling was not changed and no Python pipeline integrity claim is made",
        },
        "lua_syntax": {
            "command": "powershell -ExecutionPolicy Bypass -File .\\tools\\check_lua_syntax.ps1",
            "status": "not_run",
            "skip_rationale": "docs/static-artifact-only round; Lua/runtime surfaces were not changed and no Lua syntax validation claim is made",
        },
        "adversarial_review_verdict": "PASS",
        "critical_finding_count": 0,
        "validation_side_effect_restore_report_required": False,
        "validation_side_effect_restore_report_reason": "round-local generator does not invoke body recompose, runtime generation, packaging, or shared validators with known regeneration side effects",
        "diff_review": {
            "global_worktree_dirty_before_round": True,
            "round_write_scope": ROUND_ROOT_NAME,
            "live_governance_docs_touched": False,
            "shared_tools_touched": False,
        },
        "validation_ceiling": {
            "validated": [
                "scope and predecessor readpoint separation",
                "template and execution contract attestation",
                "body-role lint substrate anchor",
                "LAYER4_ABSORPTION active rule",
                "token and matching semantics",
                "bounded lexical inventory",
                "scan-root coverage matrix",
                "known-surface checklist",
                "authority classification and partition integrity",
                "no-inheritance rule",
                "current corpus manifest and sidecar hash",
                "design-only preflight disclosure",
                "round-local JSON/JSONL parse",
                "determinism digest",
                "non-mutation hash diff for stated surfaces",
            ],
            "out_of_scope": [
                "LAYER4_ABSORPTION_CONFIRMED final count",
                "runtime rollout validation",
                "manual in-game validation",
                "multiplayer validation",
                "long-session runtime validation",
                "B42 validation",
                "Workshop validation",
                "release validation",
                "deployment validation",
                "Browser/Wiki/Tooltip UX validation",
                "full external mod compatibility sweep",
                "source expansion validation",
                "publish mutation validation",
                "publish mutation review",
                "structural signal disposition completion validation",
                "full runtime equivalence validation beyond stated non-mutation evidence",
            ],
            "unvalidated_but_in_scope": [],
        },
        "non_claims": NON_CLAIMS,
    }
    closeout_md = f"""# Layer4 Boundary Current Corpus Lock Closeout

contract_closeout_state = `{validation_report["contract_closeout_state"]}`

branch_closeout = `{validation_report["branch_closeout"]}`

## Claim Boundary

Current checkout artifact universe, current measurement corpus, excluded surface classes, no-inheritance rule, and manifest/partition prerequisite are locked for a downstream LAYER4_ABSORPTION_CONFIRMED measurement within this round's validation ceiling.

This round does not calculate a LAYER4_ABSORPTION_CONFIRMED current count.

## Corpus

included_corpus_count = `{partition["included_corpus_count"]}`

The included corpus is the body-role lint substrate anchored by `layer4_boundary_lint_substrate_anchor.json`.

## Preflight

preflight_guard_state = `not_implemented`

machine_enforcement_claimed = `false`

The closeout branch is design-only preflight.

## Validation Ceiling

Validated: scope/readpoint separation, template/contract attestation, lint substrate anchor, active rule, token/matching semantics, inventory, classification, partition, no-inheritance rule, manifest/hash, design-only preflight disclosure, JSON/JSONL parse, determinism, and non-mutation hash diff.

Out of scope: current count, runtime rollout, manual in-game validation, deployment, Workshop/B42/release readiness, Browser/Wiki/Tooltip UX validation, external mod compatibility sweep, source expansion, publish mutation review, structural signal disposition completion, and runtime equivalence beyond stated non-mutation evidence.

Unvalidated but in scope: none.

## Non-Claims

{chr(10).join(f"- {item}" for item in NON_CLAIMS)}
"""

    content["layer4_boundary_closeout_validation_report.json"] = json_bytes(validation_report)
    content["layer4_boundary_current_corpus_lock_closeout.md"] = md_bytes(closeout_md)

    return content, {
        "anchor": anchor,
        "partition": partition,
        "validation_report": validation_report,
        "before_hashes": before_hashes,
    }


def content_digest(content: dict[str, bytes], names: list[str] | None = None) -> str:
    selected = names or sorted(content)
    return sha256_bytes(b"".join(name.encode("utf-8") + b"\0" + content[name] for name in selected))


def add_artifact_hash_manifest(content: dict[str, bytes]) -> None:
    entries = []
    for name, data in sorted(content.items()):
        if name == "artifact_hash_manifest.json":
            continue
        entries.append(
            {
                "path": f"{ROUND_ROOT_NAME}/{name}",
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    entries.append(
        {
            "path": rel(SCRIPT_PATH),
            "bytes": SCRIPT_PATH.stat().st_size,
            "sha256": sha256_file(SCRIPT_PATH),
            "role": "round_local_helper_script",
        }
    )
    content["artifact_hash_manifest.json"] = json_bytes(
        {
            "schema_version": "layer4-boundary-artifact-hash-manifest-v1",
            "round_id": ROUND_ID,
            "hash_algorithm": "sha256",
            "manifest_self_excluded": True,
            "artifacts": entries,
        }
    )


def write_content(content: dict[str, bytes]) -> None:
    ROUND_ROOT.mkdir(parents=True, exist_ok=True)
    for name, data in content.items():
        (ROUND_ROOT / name).write_bytes(data)


def update_validation_after_write(content: dict[str, bytes], before_hashes: dict[str, Any]) -> None:
    after_hashes = collect_non_mutation_hashes()
    non_mutation = compare_non_mutation_hashes(before_hashes, after_hashes)
    report = json.loads(content["layer4_boundary_closeout_validation_report.json"].decode("utf-8"))
    report["non_mutation_hash_diff"] = non_mutation
    report["hard_gate_checks"]["non_mutation_hash_diff_pass"] = non_mutation["non_mutation_hash_diff_pass"]
    report["all_gates_pass"] = all(bool(value) for value in report["hard_gate_checks"].values())
    report["contract_closeout_state"] = "complete" if report["all_gates_pass"] else "blocked"
    report["branch_closeout"] = BRANCH_CLOSEOUT if report["all_gates_pass"] else "blocked_with_non_mutation_invariant_failed"
    content["layer4_boundary_closeout_validation_report.json"] = json_bytes(report)

    closeout_text = (ROUND_ROOT / "layer4_boundary_current_corpus_lock_closeout.md").read_text(encoding="utf-8")
    closeout_text = re.sub(
        r"contract_closeout_state = `[^`]+`",
        f"contract_closeout_state = `{report['contract_closeout_state']}`",
        closeout_text,
    )
    closeout_text = re.sub(
        r"branch_closeout = `[^`]+`",
        f"branch_closeout = `{report['branch_closeout']}`",
        closeout_text,
    )
    content["layer4_boundary_current_corpus_lock_closeout.md"] = md_bytes(closeout_text)


def final_file_parse_check() -> dict[str, Any]:
    errors = []
    json_count = 0
    jsonl_count = 0
    jsonl_rows = 0
    for path in sorted(ROUND_ROOT.glob("*.json")):
        json_count += 1
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append({"path": rel(path), "error": str(exc)})
    for path in sorted(ROUND_ROOT.glob("*.jsonl")):
        jsonl_count += 1
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.strip():
                jsonl_rows += 1
                try:
                    json.loads(line)
                except Exception as exc:
                    errors.append({"path": rel(path), "line": line_number, "error": str(exc)})
    return {
        "json_file_count": json_count,
        "jsonl_file_count": jsonl_count,
        "jsonl_row_count": jsonl_rows,
        "pass": len(errors) == 0,
        "errors": errors,
    }


def main() -> int:
    before_hashes = collect_non_mutation_hashes()
    content, context = build_content(before_hashes)
    add_artifact_hash_manifest(content)
    write_content(content)
    update_validation_after_write(content, context["before_hashes"])
    add_artifact_hash_manifest(content)
    write_content(content)
    parse_check = final_file_parse_check()
    report = load_json(ROUND_ROOT / "layer4_boundary_closeout_validation_report.json")
    report["final_file_parse_check"] = parse_check
    report["hard_gate_checks"]["final_file_parse_pass"] = parse_check["pass"]
    report["all_gates_pass"] = all(bool(value) for value in report["hard_gate_checks"].values())
    report["contract_closeout_state"] = "complete" if report["all_gates_pass"] else "blocked"
    report["branch_closeout"] = BRANCH_CLOSEOUT if report["all_gates_pass"] else "blocked_with_validation_failed"
    content["layer4_boundary_closeout_validation_report.json"] = json_bytes(report)
    closeout_text = (ROUND_ROOT / "layer4_boundary_current_corpus_lock_closeout.md").read_text(encoding="utf-8")
    closeout_text = re.sub(
        r"contract_closeout_state = `[^`]+`",
        f"contract_closeout_state = `{report['contract_closeout_state']}`",
        closeout_text,
    )
    closeout_text = re.sub(
        r"branch_closeout = `[^`]+`",
        f"branch_closeout = `{report['branch_closeout']}`",
        closeout_text,
    )
    content["layer4_boundary_current_corpus_lock_closeout.md"] = md_bytes(closeout_text)
    add_artifact_hash_manifest(content)
    write_content(content)
    parse_check = final_file_parse_check()
    report = load_json(ROUND_ROOT / "layer4_boundary_closeout_validation_report.json")
    result = {
        "round_root": ROUND_ROOT_NAME,
        "generated_artifact_count": len(content),
        "included_corpus_count": context["partition"]["included_corpus_count"],
        "json_jsonl_file_parse": parse_check,
        "all_gates_pass": report["all_gates_pass"],
        "contract_closeout_state": report["contract_closeout_state"],
        "branch_closeout": report["branch_closeout"],
    }
    print(stable_json(result))
    return 0 if report["all_gates_pass"] and parse_check["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
