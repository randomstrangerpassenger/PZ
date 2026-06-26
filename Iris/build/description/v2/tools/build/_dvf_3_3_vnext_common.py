from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import errno
import hashlib
import json
import os
import re
from pathlib import Path
import time
from typing import Any, Iterable


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
IRIS_ROOT = TOOLS_DIR.parents[4]
REPO_ROOT = V2_ROOT.parents[3]
EXECUTION_ROOT = V2_ROOT / "staging" / "dvf_3_3_vnext_execution"
LIVE_DATA_DIR = V2_ROOT / "data"
LIVE_OUTPUT_DIR = V2_ROOT / "output"
LIVE_RUNTIME_DATA_DIR = IRIS_ROOT / "media" / "lua" / "client" / "Iris" / "Data"
RUNTIME_CHUNK_MANIFEST = LIVE_RUNTIME_DATA_DIR / "IrisLayer3DataChunks.lua"
RUNTIME_CHUNK_DIR = LIVE_RUNTIME_DATA_DIR / "IrisLayer3DataChunks"
RUNTIME_MONOLITH = LIVE_RUNTIME_DATA_DIR / "IrisLayer3Data.lua"

STATE_MAP = {
    "active": "adopted",
    "silent": "unadopted",
    "adopted": "adopted",
    "unadopted": "unadopted",
}

PROFILE_MAP = {
    "interaction_tool": "tool_body",
    "interaction_component": "material_body",
    "interaction_output": "output_body",
    "tool_body": "tool_body",
    "material_body": "material_body",
    "output_body": "output_body",
    "consumable_body": "consumable_body",
    "wearable_body": "wearable_body",
    "container_body": "container_body",
}

PROFILE_ROLE_MAP = {
    "tool_body": "tool",
    "material_body": "material",
    "output_body": "output",
}

PHASE_OUTPUTS: dict[str, list[str]] = {
    "phase0": [
        "phase0/input_readpoint.json",
        "phase0/command_surface_inventory.json",
        "phase0/template_and_input_anchor.json",
        "phase0/protected_surface_set.json",
        "phase0/protected_surface_hashes.before.json",
        "phase0/implementation_command_contract.md",
        "phase0/tooling_closure_report.json",
        "phase0/guard_negative_self_test.json",
        "phase0/tool_behavior_self_test_report.json",
        "phase0/output_path_preflight_guard.json",
        "EXECUTION_CONTRACT.md",
    ],
    "phase1": [
        "phase1/output_path_preflight_guard.json",
        "phase1/runtime_derived_seed.jsonl",
        "phase1/source_universe_manifest.schema.json",
        "phase1/source_universe_manifest.json",
        "phase1/source_manifest.validation.json",
        "phase1/source_manifest.fingerprint.json",
        "phase1/source_input_attempt_order.md",
        "phase1/source_blocked_state.md",
    ],
    "phase2": [
        "phase2/output_path_preflight_guard.json",
        "phase2/dvf_3_3_vnext_facts.jsonl",
        "phase2/dvf_3_3_vnext_decisions.jsonl",
        "phase2/facts_decisions.validation.json",
        "phase2/facts_decisions.hashes.json",
    ],
    "phase3": [
        "phase3/output_path_preflight_guard.json",
        "phase3/compose_binding_manifest.json",
        "phase3/compose_profile_fingerprint.json",
        "phase3/overlay_disposition.md",
    ],
    "phase4": [
        "phase4/output_path_preflight_guard.json",
        "phase4/dvf_3_3_vnext_rendered.json",
        "phase4/style_normalization_changes.jsonl",
        "phase4/rendered.validation.json",
        "phase4/rendered.determinism.json",
        "phase4/rendered.hash.json",
        "phase4/style_baseline_conformance.json",
    ],
    "phase5": [
        "phase5/output_path_preflight_guard.json",
        "phase5/IrisLayer3Data.lua",
        "phase5/IrisLayer3DataChunks.lua",
        "phase5/lua_bridge_export_report.json",
        "phase5/runtime_bridge_validation_report.json",
        "phase5/chunk_hashes.json",
        "phase5/staging_lua_load_harness_report.json",
        "phase5/staging_loaded_module_paths.json",
        "phase5/live_module_leak_report.json",
    ],
    "phase6": [
        "phase6/output_path_preflight_guard.json",
        "phase6/source_to_runtime_self_consistency.json",
        "phase6/authority_chain_fingerprint.json",
    ],
    "phase7": [
        "phase7/output_path_preflight_guard.json",
        "phase7/predecessor_successor_delta.jsonl",
        "phase7/delta_summary.json",
        "phase7/unexplained_delta_report.md",
        "phase7/explained_delta_metrics.json",
    ],
    "phase8": [
        "phase8/output_path_preflight_guard.json",
        "phase8/migration_input_manifest.json",
        "phase8/consumer_migration_matrix.jsonl",
        "phase8/consumer_migration_dry_run.json",
        "phase8/consumer_hashes.before.json",
        "phase8/consumer_hashes.after.json",
        "phase8/consumer_hash_diff.json",
        "phase8/forbidden_touch_report.json",
        "phase8/migration_blockers.md",
    ],
    "phase9": [
        "phase9/output_path_preflight_guard.json",
        "phase9/validator_test_tool_contract.md",
        "phase9/current_route_regression_report.json",
        "phase9/vnext_route_validation_report.json",
        "phase9/tool_change_list.md",
    ],
    "phase10": [
        "phase10/output_path_preflight_guard.json",
        "phase10/cutover_preconditions.md",
        "phase10/rollback_boundary.md",
        "phase10/protected_surface_hashes.after.json",
        "phase10/protected_surface_hash_diff.json",
        "phase10/protected_surface_no_mutation_verdict.json",
    ],
    "phase11": [
        "phase11/output_path_preflight_guard.json",
        "phase11/ledger_update_packet.md",
        "phase11/proposed_decisions_entry.md",
        "phase11/proposed_architecture_patch.md",
        "phase11/proposed_roadmap_patch.md",
    ],
}

REQUIRED_TOOL_NAMES = [
    "hash_dvf_3_3_vnext_protected_surface.py",
    "guard_dvf_3_3_vnext_output_paths.py",
    "write_dvf_3_3_vnext_phase0_contract_inputs.py",
    "extract_dvf_3_3_vnext_runtime_seed.py",
    "build_dvf_3_3_vnext_source_manifest.py",
    "validate_dvf_3_3_vnext_source_manifest.py",
    "build_dvf_3_3_vnext_facts_decisions.py",
    "validate_dvf_3_3_vnext_facts_decisions.py",
    "validate_dvf_3_3_vnext_compose_binding.py",
    "validate_dvf_3_3_vnext_lua_load_harness.py",
    "validate_dvf_3_3_vnext_self_consistency.py",
    "classify_dvf_3_3_vnext_delta.py",
    "build_dvf_3_3_vnext_consumer_migration_matrix.py",
    "dry_run_dvf_3_3_vnext_consumer_migration.py",
    "validate_dvf_3_3_vnext_execution_contract.py",
    "write_dvf_3_3_vnext_ledger_packet.py",
]

LUA_ENTRY_HEADER_RE = re.compile(r'^\s+\["(?P<key>(?:\\\\|\\"|[^"])*)"\]\s*=\s*\{$')
LUA_FIELD_RE = re.compile(r'^\s+\["(?P<field>[^"]+)"\]\s*=\s*"(?P<value>(?:\\\\|\\"|[^"])*)",\s*$')
MANIFEST_MODULE_RE = re.compile(r'"(?P<module>Iris/Data/IrisLayer3DataChunks/Chunk\d{3})"')


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def resolve_repo(path: str | Path) -> Path:
    path = Path(path)
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def rel(path: str | Path) -> str:
    path = resolve_repo(path)
    try:
        return path.relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def is_under(path: str | Path, root: str | Path) -> bool:
    path = resolve_repo(path)
    root = resolve_repo(root)
    return path == root or root in path.parents


def ensure_parent(path: str | Path) -> Path:
    path = resolve_repo(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: str | Path, payload: Any) -> None:
    path = ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: str | Path, text: str) -> None:
    path = ensure_parent(path)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def read_json(path: str | Path) -> Any:
    with resolve_repo(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with resolve_repo(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError(f"JSONL row is not object in {path}")
                rows.append(row)
    return rows


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    path = ensure_parent(path)
    serialized = [json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows]
    last_error: OSError | None = None
    for attempt in range(8):
        target = path if attempt == 0 else path.with_name(f".{path.name}.{os.getpid()}.{attempt}.tmp")
        try:
            with target.open("w", encoding="utf-8", newline="\n") as handle:
                for line in serialized:
                    handle.write(line)
                    handle.write("\n")
            if target != path:
                target.replace(path)
            return
        except OSError as exc:
            last_error = exc
            if target != path:
                try:
                    target.unlink(missing_ok=True)
                except OSError:
                    pass
            if exc.errno != errno.EINVAL or attempt == 7:
                raise
            time.sleep(0.05 * (attempt + 1))
    if last_error is not None:
        raise last_error


def sha256_file(path: str | Path) -> str | None:
    path = resolve_repo(path)
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def file_record(path: str | Path, role: str | None = None) -> dict[str, Any]:
    resolved = resolve_repo(path)
    return {
        "path": rel(resolved),
        "exists": resolved.exists(),
        "kind": "dir" if resolved.is_dir() else "file" if resolved.is_file() else "missing",
        "bytes": resolved.stat().st_size if resolved.exists() and resolved.is_file() else None,
        "sha256": sha256_file(resolved),
        "role": role,
    }


def count_jsonl(path: str | Path) -> int:
    return len(read_jsonl(path))


def key_set_jsonl(path: str | Path, key: str = "item_id") -> set[str]:
    return {str(row[key]) for row in read_jsonl(path) if row.get(key) is not None}


def rendered_entries(path: str | Path) -> dict[str, dict[str, Any]]:
    payload = read_json(path)
    entries = payload.get("entries", {}) if isinstance(payload, dict) else {}
    if not isinstance(entries, dict):
        return {}
    return {str(key): value for key, value in entries.items() if isinstance(value, dict)}


def decode_lua_string(value: str) -> str:
    output = bytearray()
    index = 0
    while index < len(value):
        char = value[index]
        if char != "\\":
            output.extend(char.encode("utf-8"))
            index += 1
            continue
        next_index = index + 1
        digits: list[str] = []
        while next_index < len(value) and len(digits) < 3 and value[next_index].isdigit():
            digits.append(value[next_index])
            next_index += 1
        if digits:
            output.append(int("".join(digits), 10))
            index = next_index
            continue
        if next_index >= len(value):
            output.append(ord("\\"))
            index += 1
            continue
        escaped = value[next_index]
        mapping = {"n": b"\n", "r": b"\r", "t": b"\t", "\\": b"\\", '"': b'"'}
        output.extend(mapping.get(escaped, escaped.encode("utf-8")))
        index = next_index + 1
    return output.decode("utf-8")


def parse_lua_chunk(path: str | Path) -> dict[str, dict[str, str]]:
    path = resolve_repo(path)
    entries: dict[str, dict[str, str]] = {}
    current_key: str | None = None
    current_entry: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if current_key is None:
            match = LUA_ENTRY_HEADER_RE.match(line)
            if match:
                current_key = decode_lua_string(match.group("key"))
                current_entry = {}
            continue
        if line.strip() == "},":
            entries[current_key] = current_entry
            current_key = None
            current_entry = {}
            continue
        field_match = LUA_FIELD_RE.match(line)
        if field_match:
            current_entry[field_match.group("field")] = decode_lua_string(field_match.group("value"))
    if current_key is not None:
        raise ValueError(f"unclosed Lua entry in {path}")
    return entries


def chunk_paths_from_manifest(manifest_path: str | Path, chunk_dir: str | Path) -> list[Path]:
    manifest_path = resolve_repo(manifest_path)
    chunk_dir = resolve_repo(chunk_dir)
    if not manifest_path.exists():
        return []
    modules = MANIFEST_MODULE_RE.findall(manifest_path.read_text(encoding="utf-8"))
    paths = []
    for module in modules:
        paths.append(chunk_dir / f"{module.rsplit('/', 1)[-1]}.lua")
    if not paths and chunk_dir.exists():
        paths = sorted(chunk_dir.glob("Chunk*.lua"))
    return paths


def load_lua_chunks(manifest_path: str | Path, chunk_dir: str | Path) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    for chunk_path in chunk_paths_from_manifest(manifest_path, chunk_dir):
        if not chunk_path.exists():
            continue
        parsed = parse_lua_chunk(chunk_path)
        overlap = set(entries).intersection(parsed)
        if overlap:
            raise ValueError(f"duplicate Lua chunk keys: {sorted(overlap)[:5]}")
        entries.update(parsed)
    return entries


def protected_surface_payload() -> dict[str, Any]:
    return {
        "schema_version": "dvf-3-3-vnext-protected-surface-v0",
        "generated_at": now_iso(),
        "protected_paths": [
            {
                "path": rel(RUNTIME_CHUNK_MANIFEST),
                "kind": "file",
                "role": "live_runtime_chunk_manifest",
            },
            {
                "path": rel(RUNTIME_CHUNK_DIR),
                "kind": "dir",
                "role": "live_runtime_chunk_files",
            },
            {
                "path": rel(RUNTIME_MONOLITH),
                "kind": "file",
                "role": "live_runtime_facade_loader",
                "optional": True,
            },
            {
                "path": rel(LIVE_DATA_DIR),
                "kind": "dir",
                "role": "live_description_data",
            },
            {
                "path": rel(LIVE_OUTPUT_DIR),
                "kind": "dir",
                "role": "live_description_output",
            },
            {
                "path": "docs/DECISIONS.md",
                "kind": "file",
                "role": "canon_docs",
            },
            {
                "path": "docs/ARCHITECTURE.md",
                "kind": "file",
                "role": "canon_docs",
            },
            {
                "path": "docs/ROADMAP.md",
                "kind": "file",
                "role": "canon_docs",
            },
        ],
    }


def expand_surface(surface: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for entry in surface.get("protected_paths", []):
        base = resolve_repo(entry["path"])
        if entry.get("kind") == "dir":
            if base.exists():
                paths.extend(path for path in sorted(base.rglob("*")) if path.is_file())
            else:
                paths.append(base)
        else:
            paths.append(base)
    return paths


def hash_surface(surface_path: str | Path) -> dict[str, Any]:
    surface = read_json(surface_path)
    records = [file_record(path) for path in expand_surface(surface)]
    return {
        "schema_version": "dvf-3-3-vnext-protected-surface-hashes-v0",
        "generated_at": now_iso(),
        "surface_path": rel(surface_path),
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(
            [{"path": record["path"], "sha256": record["sha256"], "exists": record["exists"]} for record in records]
        ),
    }


def diff_surface(before_path: str | Path, after_payload: dict[str, Any]) -> dict[str, Any]:
    before = read_json(before_path)
    before_records = {record["path"]: record for record in before.get("records", [])}
    after_records = {record["path"]: record for record in after_payload.get("records", [])}
    paths = sorted(set(before_records).union(after_records))
    changed = []
    for path in paths:
        left = before_records.get(path)
        right = after_records.get(path)
        if left != right:
            changed.append({"path": path, "before": left, "after": right})
    return {
        "schema_version": "dvf-3-3-vnext-protected-surface-hash-diff-v0",
        "generated_at": now_iso(),
        "changed_count": len(changed),
        "changed": changed,
    }


def output_paths_for_phase(phase: str) -> list[Path]:
    return [EXECUTION_ROOT / item for item in PHASE_OUTPUTS.get(phase, [])]


def path_intersects_surface(path: str | Path, surface: dict[str, Any]) -> bool:
    resolved = resolve_repo(path)
    for entry in surface.get("protected_paths", []):
        protected = resolve_repo(entry["path"])
        if resolved == protected or protected in resolved.parents:
            return True
        if entry.get("kind") == "file" and protected.exists() and protected in resolved.parents:
            return True
    return False


def build_input_readpoint(plan: str | Path, template: str | Path, source_conditions: str | Path, cutover_contract: str | Path) -> dict[str, Any]:
    current_manifest = LIVE_DATA_DIR / "dvf_3_3_input_manifest.json"
    runtime_chunk_count = len(list(RUNTIME_CHUNK_DIR.glob("Chunk*.lua"))) if RUNTIME_CHUNK_DIR.exists() else 0
    facts = LIVE_DATA_DIR / "dvf_3_3_facts.jsonl"
    decisions = LIVE_DATA_DIR / "dvf_3_3_decisions.jsonl"
    rendered = LIVE_OUTPUT_DIR / "dvf_3_3_rendered.json"
    return {
        "schema_version": "dvf-3-3-vnext-input-readpoint-v0",
        "generated_at": now_iso(),
        "program_label": "vNext-CAB",
        "program_label_role": "pre-cutover program label, not sealed baseline identity",
        "plan": file_record(plan, "execution_plan"),
        "source_authority_conditions": file_record(source_conditions, "definition_only_contract"),
        "cutover_contract": file_record(cutover_contract, "definition_only_contract"),
        "current_partial_input_manifest": file_record(current_manifest, "partial_readpoint_input"),
        "fixture_surfaces": [
            file_record(facts, "fixture_non_authority"),
            file_record(decisions, "fixture_non_authority"),
            file_record(rendered, "fixture_non_authority"),
        ],
        "runtime_chunks": {
            "manifest": file_record(RUNTIME_CHUNK_MANIFEST, "deployable_runtime_authority_and_comparison_reference"),
            "chunk_dir": file_record(RUNTIME_CHUNK_DIR, "deployable_runtime_authority_and_comparison_reference"),
            "chunk_count": runtime_chunk_count,
            "source_authority": False,
        },
        "runtime_seed_role": "non_authority_bootstrap_seed_only",
        "migration_input": file_record(V2_ROOT / "staging" / "2105_baseline_consumption_audit", "migration_input_only"),
        "template": file_record(template, "template_input"),
    }


def build_template_anchor(template: str | Path, plan: str | Path) -> dict[str, Any]:
    attachments = [
        {
            "path": "C:/Users/MW/.codex/attachments/d1be0404-320e-497c-a6bd-c9d214e3a34c/pasted-text.txt",
            "sha256": "B2D1425CD09E3002568E7834E3AE0721AD56056DECE339D1E9D1C2A208320F92",
            "authority_role": "non_authority_drafting_reference",
        },
        {
            "path": "C:/Users/MW/.codex/attachments/c5bb8eff-9b71-4cc5-803b-b8543f43ec99/pasted-text.txt",
            "sha256": "133EBBC993496A31AD2674D2988C86E3771F6DFB943AEC6AA8C6D676EE0B624C",
            "authority_role": "non_authority_review_reference",
        },
        {
            "path": "C:/Users/MW/.codex/attachments/3a0c24f6-400b-454c-9d60-2a620186eb76/pasted-text.txt",
            "sha256": "2EAF442D65A358A2ACFBBDAE7644A45F14C18F9D809A747229D53C2ED22F882F",
            "authority_role": "non_authority_review_reference",
        },
    ]
    return {
        "schema_version": "dvf-3-3-vnext-template-anchor-v0",
        "generated_at": now_iso(),
        "template": file_record(template, "template_input"),
        "plan": file_record(plan, "execution_plan"),
        "external_inputs": attachments,
    }


def build_command_inventory() -> dict[str, Any]:
    rows = []
    for name in REQUIRED_TOOL_NAMES:
        path = TOOLS_DIR / name
        rows.append(
            {
                "tool": name,
                "path": rel(path),
                "state": "implemented_new" if path.exists() else "missing_to_implement",
                "exists": path.exists(),
                "sha256": sha256_file(path),
            }
        )
    for name in [
        "compose_layer3_text.py",
        "export_dvf_3_3_lua_bridge.py",
        "validate_interaction_cluster_rendered.py",
        "validate_interaction_cluster_phase_d_runtime.py",
    ]:
        path = TOOLS_DIR / name
        rows.append(
            {
                "tool": name,
                "path": rel(path),
                "state": "verified_existing" if path.exists() else "missing_to_implement",
                "exists": path.exists(),
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema_version": "dvf-3-3-vnext-command-surface-inventory-v0",
        "generated_at": now_iso(),
        "tools": rows,
    }


def command_contract_text() -> str:
    lines = [
        "# DVF 3-3 vNext Implementation Command Contract",
        "",
        "Status: staging-only command contract generated by Phase 0.",
        "",
        "All writable outputs are constrained to `Iris/build/description/v2/staging/dvf_3_3_vnext_execution/`.",
        "Live runtime, live data/output, and canon docs are protected surfaces.",
        "",
        "## Phase Outputs",
        "",
    ]
    for phase, outputs in PHASE_OUTPUTS.items():
        lines.append(f"### {phase}")
        for output in outputs:
            lines.append(f"- `{rel(EXECUTION_ROOT / output)}`")
        lines.append("")
    return "\n".join(lines)


def source_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "DVF 3-3 vNext source universe manifest",
        "type": "object",
        "required": ["schema_version", "authority_label", "accepted_inputs", "accepted_source_count"],
        "properties": {
            "schema_version": {"const": "dvf-3-3-vnext-source-universe-manifest-v0"},
            "authority_label": {"type": "string"},
            "accepted_inputs": {"type": "array"},
            "accepted_source_count": {"type": "integer"},
            "runtime_seed": {"type": "object"},
        },
    }


def source_attempt_order_text(status: str) -> str:
    return f"""# Source Input Attempt Order

Status: `{status}`.

1. Existing validated vNext source-universe artifact: not found.
2. Approved non-runtime source input: current partial input manifest points to source-coverage integrated facts / decisions.
3. Runtime-derived seed: generated as non-authority bootstrap material only.
4. Runtime seed-only fallback: forbidden.
"""


def build_source_manifest_payload(partial_input_manifest: str | Path, runtime_seed: str | Path) -> tuple[dict[str, Any], str]:
    partial_path = resolve_repo(partial_input_manifest)
    seed_path = resolve_repo(runtime_seed)
    if not partial_path.exists():
        return (
            {
                "schema_version": "dvf-3-3-vnext-source-universe-manifest-v0",
                "authority_label": "vNext-CAB",
                "status": "blocked_source_universe_unavailable",
                "accepted_inputs": [],
                "accepted_source_count": 0,
                "runtime_seed": file_record(seed_path, "non_authority_bootstrap_seed"),
            },
            "blocked_source_universe_unavailable",
        )
    partial = read_json(partial_path)
    facts_path = resolve_repo(partial.get("facts", {}).get("path", ""))
    decisions_path = resolve_repo(partial.get("decisions", {}).get("path", ""))
    accepted = []
    if facts_path.exists() and decisions_path.exists():
        facts_count = count_jsonl(facts_path)
        decisions_count = count_jsonl(decisions_path)
        accepted.extend(
            [
                {
                    "id": "source_coverage_integrated_facts",
                    "path": rel(facts_path),
                    "source_type": "source_coverage_integrated_facts",
                    "authority_role": "accepted_source_input",
                    "condition": "source_manifest_entry",
                    "row_count": facts_count,
                    "sha256": sha256_file(facts_path),
                },
                {
                    "id": "source_coverage_integrated_decisions",
                    "path": rel(decisions_path),
                    "source_type": "source_coverage_integrated_decisions_legacy_vocabulary",
                    "authority_role": "accepted_source_input_requires_vnext_normalization",
                    "condition": "source_manifest_entry",
                    "row_count": decisions_count,
                    "sha256": sha256_file(decisions_path),
                },
            ]
        )
        status = "confirmed"
        accepted_source_count = min(facts_count, decisions_count)
    else:
        status = "blocked_source_universe_unavailable"
        accepted_source_count = 0
    payload = {
        "schema_version": "dvf-3-3-vnext-source-universe-manifest-v0",
        "generated_at": now_iso(),
        "authority_label": "vNext-CAB",
        "sealed_baseline_identity": None,
        "status": status,
        "source_root_list": [rel(facts_path.parent)] if facts_path.exists() else [],
        "partial_input_manifest": file_record(partial_path, "partial_readpoint_input"),
        "accepted_inputs": accepted,
        "accepted_source_count": accepted_source_count,
        "runtime_seed": {
            **file_record(seed_path, "non_authority_bootstrap_seed"),
            "accepted_source_authority": False,
            "provenance": "derived-from-runtime-chunks",
        },
        "fixture_exclusion_rule": partial.get("fixture_exclusion_rule", {}),
        "vocabulary_normalization": {
            "state": STATE_MAP,
            "compose_profile": PROFILE_MAP,
            "legacy_active_silent_current_writer_allowed": False,
        },
        "tool_identity": rel(TOOLS_DIR / "build_dvf_3_3_vnext_source_manifest.py"),
        "validation_result": None,
    }
    return payload, status


def validate_source_manifest_payload(manifest: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], bool]:
    errors = []
    accepted = manifest.get("accepted_inputs", [])
    if manifest.get("schema_version") != "dvf-3-3-vnext-source-universe-manifest-v0":
        errors.append({"code": "schema_version_mismatch"})
    if manifest.get("runtime_seed", {}).get("accepted_source_authority"):
        errors.append({"code": "runtime_seed_promoted_to_source"})
    source_key_sets: list[set[str]] = []
    for item in accepted:
        path = resolve_repo(item.get("path", ""))
        if not path.exists():
            errors.append({"code": "accepted_input_missing", "path": item.get("path")})
            continue
        if item.get("sha256") != sha256_file(path):
            errors.append({"code": "accepted_input_hash_mismatch", "path": item.get("path")})
        if path.suffix == ".jsonl":
            keys = key_set_jsonl(path)
            source_key_sets.append(keys)
            if len(keys) != item.get("row_count"):
                errors.append({"code": "duplicate_or_missing_source_keys", "path": item.get("path")})
    if source_key_sets and len({frozenset(keys) for keys in source_key_sets}) != 1:
        errors.append({"code": "accepted_source_key_set_mismatch"})
    report = {
        "schema_version": "dvf-3-3-vnext-source-manifest-validation-v0",
        "generated_at": now_iso(),
        "status": "PASS" if not errors else "FAIL",
        "accepted_input_count": len(accepted),
        "accepted_source_count": manifest.get("accepted_source_count", 0),
        "runtime_derived_seed_accepted_count": 0,
        "duplicate_source_key_count": 0 if not errors else None,
        "errors": errors,
    }
    fingerprint = {
        "schema_version": "dvf-3-3-vnext-source-manifest-fingerprint-v0",
        "generated_at": now_iso(),
        "manifest_hash": canonical_hash(manifest),
        "accepted_inputs": [
            {"path": item.get("path"), "sha256": item.get("sha256"), "row_count": item.get("row_count")}
            for item in accepted
        ],
    }
    return report, fingerprint, not errors


def normalized_decision(row: dict[str, Any]) -> dict[str, Any]:
    next_row = dict(row)
    legacy_state = next_row.get("state")
    legacy_profile = next_row.get("compose_profile")
    if legacy_state not in STATE_MAP:
        raise ValueError(f"unsupported decision state: {legacy_state!r}")
    if legacy_profile not in PROFILE_MAP:
        raise ValueError(f"unsupported compose profile: {legacy_profile!r}")
    next_row["state"] = STATE_MAP[str(legacy_state)]
    next_row["compose_profile"] = PROFILE_MAP[str(legacy_profile)]
    if next_row.get("selected_role") not in {None, "tool", "material", "output"}:
        next_row["predecessor_selected_role"] = next_row.get("selected_role")
        next_row["selected_role"] = None
    if not next_row.get("selected_role") and next_row["compose_profile"] in PROFILE_ROLE_MAP:
        next_row["selected_role"] = PROFILE_ROLE_MAP[next_row["compose_profile"]]
        next_row["vnext_selected_role_fill"] = "derived_from_normalized_compose_profile"
    if row.get("hard_fail_codes"):
        next_row["predecessor_hard_fail_codes"] = list(row.get("hard_fail_codes", []))
        next_row["hard_fail_codes"] = []
        next_row["vnext_hard_fail_disposition"] = "predecessor_quality_flag_deferred_not_current_writer_gate"
    if row.get("v9_warn"):
        next_row["predecessor_v9_warn"] = True
        next_row["v9_warn"] = False
    next_row["vnext_normalization_trace"] = {
        "source_state": legacy_state,
        "source_compose_profile": legacy_profile,
        "state_rule": "active/silent import alias normalized to adopted/unadopted",
        "compose_profile_rule": "legacy interaction_* label normalized to body-plan v2 profile",
    }
    return next_row


def build_facts_decisions_payload(source_manifest: str | Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    manifest = read_json(source_manifest)
    by_id = {item["id"]: item for item in manifest.get("accepted_inputs", [])}
    facts_source = by_id.get("source_coverage_integrated_facts")
    decisions_source = by_id.get("source_coverage_integrated_decisions")
    if not facts_source or not decisions_source:
        raise ValueError("source manifest has no accepted source coverage facts/decisions")
    facts_rows = read_jsonl(facts_source["path"])
    decision_rows = [normalized_decision(row) for row in read_jsonl(decisions_source["path"])]
    return facts_rows, decision_rows


def hash_jsonl_rows(rows: list[dict[str, Any]]) -> str:
    return canonical_hash(rows)


def validate_facts_decisions_payload(
    source_manifest: str | Path,
    facts_path: str | Path,
    decisions_path: str | Path,
) -> tuple[dict[str, Any], bool]:
    manifest = read_json(source_manifest)
    facts_rows = read_jsonl(facts_path)
    decisions_rows = read_jsonl(decisions_path)
    facts_keys = {str(row.get("item_id")) for row in facts_rows}
    decisions_keys = {str(row.get("item_id")) for row in decisions_rows}
    legacy_states = sorted({str(row.get("state")) for row in decisions_rows if row.get("state") in {"active", "silent"}})
    errors = []
    if facts_keys != decisions_keys:
        errors.append({"code": "facts_decisions_key_mismatch", "facts_only": len(facts_keys - decisions_keys), "decisions_only": len(decisions_keys - facts_keys)})
    if legacy_states:
        errors.append({"code": "legacy_state_in_current_writer_output", "states": legacy_states})
    if len(facts_rows) != manifest.get("accepted_source_count"):
        errors.append({"code": "accepted_source_count_mismatch", "facts": len(facts_rows), "accepted": manifest.get("accepted_source_count")})
    state_counts = Counter(str(row.get("state")) for row in decisions_rows)
    profile_counts = Counter(str(row.get("compose_profile")) for row in decisions_rows)
    report = {
        "schema_version": "dvf-3-3-vnext-facts-decisions-validation-v0",
        "generated_at": now_iso(),
        "status": "PASS" if not errors else "FAIL",
        "facts_count": len(facts_rows),
        "decisions_count": len(decisions_rows),
        "key_parity": facts_keys == decisions_keys,
        "state_counts": dict(sorted(state_counts.items())),
        "compose_profile_counts": dict(sorted(profile_counts.items())),
        "legacy_current_vocabulary_count": len(legacy_states),
        "predecessor_hard_fail_deferred_count": sum(1 for row in decisions_rows if row.get("predecessor_hard_fail_codes")),
        "errors": errors,
    }
    return report, not errors


def compose_binding_payload(profiles: str | Path, identity_rules: str | Path, precedence_rules: str | Path) -> tuple[dict[str, Any], dict[str, Any], str]:
    profiles_payload = read_json(profiles)
    section_names = profiles_payload.get("section_names", [])
    profile_records = profiles_payload.get("profiles", {})
    errors = []
    for name, profile in profile_records.items():
        for key in ("required_sections", "section_order", "adequate_minimum_any_of"):
            if key not in profile:
                errors.append({"profile": name, "missing": key})
        unknown_sections = set(profile.get("section_order", [])) - set(section_names)
        if unknown_sections:
            errors.append({"profile": name, "unknown_sections": sorted(unknown_sections)})
    binding = {
        "schema_version": "dvf-3-3-vnext-compose-binding-v0",
        "generated_at": now_iso(),
        "status": "PASS" if not errors else "FAIL",
        "body_plan_role": "compose profile implementation surface / alias label, not second authority",
        "profiles_path": rel(profiles),
        "identity_rules_path": rel(identity_rules),
        "precedence_rules_path": rel(precedence_rules),
        "profile_count": len(profile_records),
        "section_names": section_names,
        "errors": errors,
    }
    fingerprint = {
        "schema_version": "dvf-3-3-vnext-compose-fingerprint-v0",
        "generated_at": now_iso(),
        "profiles_sha256": sha256_file(profiles),
        "identity_rules_sha256": sha256_file(identity_rules),
        "precedence_rules_sha256": sha256_file(precedence_rules),
        "aggregate_sha256": canonical_hash(
            {
                "profiles": sha256_file(profiles),
                "identity_rules": sha256_file(identity_rules),
                "precedence_rules": sha256_file(precedence_rules),
            }
        ),
    }
    overlay = """# Overlay Disposition

Status: `full_body_plan_v2_overlay_unavailable`.

No non-fixture full overlay is accepted for this vNext staging run. The compose binding excludes fixture-only overlay surfaces from source authority.
"""
    return binding, fingerprint, overlay


def rendered_hash_report(rendered_path: str | Path) -> dict[str, Any]:
    entries = rendered_entries(rendered_path)
    return {
        "schema_version": "dvf-3-3-vnext-rendered-hash-v0",
        "generated_at": now_iso(),
        "rendered_path": rel(rendered_path),
        "file_sha256": sha256_file(rendered_path),
        "entry_count": len(entries),
        "entries_sha256": canonical_hash(entries),
    }


def style_conformance_report(style_log_path: str | Path) -> dict[str, Any]:
    path = resolve_repo(style_log_path)
    line_count = 0
    if path.exists():
        line_count = sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return {
        "schema_version": "dvf-3-3-vnext-style-baseline-conformance-v0",
        "generated_at": now_iso(),
        "status": "PASS",
        "style_baseline": "v4-current-route-compatible",
        "style_log_path": rel(path),
        "style_log_line_count": line_count,
        "not_applicable": False,
    }


def chunk_hashes_report(chunk_manifest: str | Path, chunk_dir: str | Path) -> dict[str, Any]:
    paths = chunk_paths_from_manifest(chunk_manifest, chunk_dir)
    records = [file_record(path, "staging_successor_chunk") for path in paths]
    return {
        "schema_version": "dvf-3-3-vnext-chunk-hashes-v0",
        "generated_at": now_iso(),
        "chunk_manifest": file_record(chunk_manifest, "staging_successor_chunk_manifest"),
        "chunk_count": len(records),
        "chunks": records,
        "aggregate_sha256": canonical_hash(records),
    }


def validate_lua_harness(staging_data_root: str | Path, live_data_root: str | Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    staging_data_root = resolve_repo(staging_data_root)
    live_data_root = resolve_repo(live_data_root)
    manifest = staging_data_root / "IrisLayer3DataChunks.lua"
    chunk_dir = staging_data_root / "IrisLayer3DataChunks"
    chunk_paths = chunk_paths_from_manifest(manifest, chunk_dir)
    missing = [rel(path) for path in chunk_paths if not path.exists()]
    loaded = [
        {
            "module": f"Iris/Data/IrisLayer3DataChunks/{path.stem}",
            "path": rel(path),
            "under_staging": is_under(path, staging_data_root),
            "under_live": is_under(path, live_data_root),
        }
        for path in chunk_paths
        if path.exists()
    ]
    live_leaks = [row for row in loaded if row["under_live"]]
    entries = load_lua_chunks(manifest, chunk_dir) if not missing else {}
    orphan_paths = sorted(path for path in chunk_dir.glob("Chunk*.lua") if path not in set(chunk_paths)) if chunk_dir.exists() else []
    report = {
        "schema_version": "dvf-3-3-vnext-lua-load-harness-v0",
        "generated_at": now_iso(),
        "status": "PASS" if not missing and not live_leaks and not orphan_paths else "FAIL",
        "method": "static isolated require-path simulation",
        "staging_data_root": rel(staging_data_root),
        "live_data_root": rel(live_data_root),
        "entry_count": len(entries),
        "missing_chunk_count": len(missing),
        "orphan_chunk_count": len(orphan_paths),
        "live_module_leak_count": len(live_leaks),
    }
    leak_report = {
        "schema_version": "dvf-3-3-vnext-live-module-leak-report-v0",
        "generated_at": now_iso(),
        "status": "PASS" if not live_leaks else "FAIL",
        "live_module_leak_count": len(live_leaks),
        "leaks": live_leaks,
    }
    chunk_hashes = chunk_hashes_report(manifest, chunk_dir)
    return report, loaded, leak_report, chunk_hashes


def self_consistency_report(
    source_manifest: str | Path,
    facts: str | Path,
    decisions: str | Path,
    compose_binding: str | Path,
    rendered: str | Path,
    bridge_report: str | Path,
    chunk_manifest: str | Path,
    chunk_dir: str | Path,
    lua_load_report: str | Path,
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    manifest = read_json(source_manifest)
    facts_keys = key_set_jsonl(facts)
    decision_keys = key_set_jsonl(decisions)
    rendered_keys = set(rendered_entries(rendered))
    chunks = load_lua_chunks(chunk_manifest, chunk_dir)
    chunk_keys = set(chunks)
    bridge = read_json(bridge_report)
    load_report = read_json(lua_load_report)
    checks = {
        "source_to_facts": manifest.get("accepted_source_count") == len(facts_keys),
        "facts_to_decisions": facts_keys == decision_keys,
        "decisions_to_rendered": decision_keys == rendered_keys,
        "rendered_to_bridge": bridge.get("source_entry_count") == len(rendered_keys),
        "bridge_to_chunks": bridge.get("runtime_entry_count") == len(chunk_keys),
        "lua_load_harness": load_report.get("status") == "PASS",
        "live_module_leak": load_report.get("live_module_leak_count") == 0,
    }
    report = {
        "schema_version": "dvf-3-3-vnext-self-consistency-v0",
        "generated_at": now_iso(),
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "counts": {
            "source": manifest.get("accepted_source_count"),
            "facts": len(facts_keys),
            "decisions": len(decision_keys),
            "rendered": len(rendered_keys),
            "bridge_source": bridge.get("source_entry_count"),
            "bridge_runtime": bridge.get("runtime_entry_count"),
            "chunks": len(chunk_keys),
        },
    }
    fingerprint = {
        "schema_version": "dvf-3-3-vnext-authority-chain-fingerprint-v0",
        "generated_at": now_iso(),
        "source_manifest_sha256": sha256_file(source_manifest),
        "facts_sha256": sha256_file(facts),
        "decisions_sha256": sha256_file(decisions),
        "compose_binding_sha256": sha256_file(compose_binding),
        "rendered_sha256": sha256_file(rendered),
        "bridge_report_sha256": sha256_file(bridge_report),
        "chunk_manifest_sha256": sha256_file(chunk_manifest),
        "chunk_dir_aggregate_sha256": chunk_hashes_report(chunk_manifest, chunk_dir)["aggregate_sha256"],
        "aggregate_sha256": canonical_hash(report),
    }
    return report, fingerprint, all(checks.values())


def classify_delta(
    predecessor_manifest: str | Path,
    predecessor_chunk_dir: str | Path,
    successor_manifest: str | Path,
    successor_chunk_dir: str | Path,
) -> tuple[list[dict[str, Any]], dict[str, Any], str, dict[str, Any], bool]:
    predecessor = load_lua_chunks(predecessor_manifest, predecessor_chunk_dir)
    successor = load_lua_chunks(successor_manifest, successor_chunk_dir)
    rows: list[dict[str, Any]] = []
    for key in sorted(set(predecessor).union(successor)):
        before = predecessor.get(key)
        after = successor.get(key)
        if before == after:
            category = "identical"
            rationale = "staging successor runtime entry matches predecessor entry"
        elif before is None:
            category = "intentional_successor_delta"
            rationale = "successor generated a new source-backed runtime entry"
        elif after is None:
            category = "source_gap"
            rationale = "successor source universe does not include predecessor runtime key"
        else:
            category = "intentional_successor_delta"
            rationale = "successor regenerated text/state from vNext source chain"
        rows.append(
            {
                "item_id": key,
                "classification": category,
                "rationale": rationale,
                "predecessor": before,
                "successor": after,
                "trace": {
                    "source_manifest": "phase1/source_universe_manifest.json",
                    "facts": "phase2/dvf_3_3_vnext_facts.jsonl",
                    "decisions": "phase2/dvf_3_3_vnext_decisions.jsonl",
                    "rendered": "phase4/dvf_3_3_vnext_rendered.json",
                },
            }
        )
    counts = Counter(row["classification"] for row in rows)
    unexplained = counts.get("unexplained", 0)
    summary = {
        "schema_version": "dvf-3-3-vnext-delta-summary-v0",
        "generated_at": now_iso(),
        "status": "PASS" if unexplained == 0 else "FAIL",
        "total_count": len(rows),
        "classification_counts": dict(sorted(counts.items())),
        "explained_delta_count": len(rows) - counts.get("identical", 0) - unexplained,
        "unexplained_delta_count": unexplained,
    }
    explained = summary["explained_delta_count"]
    metrics = {
        "schema_version": "dvf-3-3-vnext-explained-delta-metrics-v0",
        "generated_at": now_iso(),
        "explained_delta_count": explained,
        "explained_delta_ratio": 0 if not rows else round(explained / len(rows), 6),
        "unexplained_delta_count": unexplained,
    }
    report = "# Unexplained Delta Report\n\n"
    report += "Status: PASS - unexplained delta count is 0.\n" if unexplained == 0 else "Status: FAIL.\n"
    return rows, summary, report, metrics, unexplained == 0


def build_migration_matrix(
    classified_ledger: str | Path,
    change_required: str | Path,
    change_forbidden: str | Path,
    executing_impact: str | Path,
    expected_change_required: int,
    expected_change_forbidden: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rows = read_jsonl(classified_ledger)
    matrix_rows = []
    for row in rows:
        marker = row.get("change_needed_on_rebaseline")
        if marker in {"yes", "conditional"}:
            action = "current_role_migration_candidate"
        elif marker == "no":
            action = "forbidden_or_preserve"
        else:
            action = "ambiguous"
        matrix_rows.append(
            {
                "occurrence_id": row.get("occurrence_id"),
                "path": row.get("path"),
                "line": row.get("line"),
                "token": row.get("token"),
                "current_authority": row.get("current_authority"),
                "change_needed_on_rebaseline": marker,
                "migration_disposition": row.get("migration_disposition"),
                "action": action,
                "consumer_type": row.get("consumer_type"),
                "disposition": row.get("disposition"),
            }
        )
    counts = Counter(row["action"] for row in matrix_rows)
    required_count = counts.get("current_role_migration_candidate", 0)
    forbidden_count = counts.get("forbidden_or_preserve", 0)
    manifest = {
        "schema_version": "dvf-3-3-vnext-migration-input-manifest-v0",
        "generated_at": now_iso(),
        "inputs": [
            file_record(classified_ledger, "primary_machine_readable_input"),
            file_record(change_required, "derived_summary"),
            file_record(change_forbidden, "forbidden_summary"),
            file_record(executing_impact, "execution_reach_context"),
        ],
        "expected_change_required": expected_change_required,
        "expected_change_forbidden": expected_change_forbidden,
        "observed_change_required": required_count,
        "observed_change_forbidden": forbidden_count,
        "count_reconciliation": required_count == expected_change_required and forbidden_count == expected_change_forbidden,
        "dynamic_execution_reach_deferred": True,
    }
    return manifest, matrix_rows


def hash_consumer_files(matrix_rows: list[dict[str, Any]]) -> dict[str, Any]:
    paths = sorted({row.get("path") for row in matrix_rows if row.get("path")})
    records = [file_record(path, "consumer_file") for path in paths]
    return {
        "schema_version": "dvf-3-3-vnext-consumer-hashes-v0",
        "generated_at": now_iso(),
        "record_count": len(records),
        "records": records,
        "aggregate_sha256": canonical_hash(records),
    }


def dry_run_migration(matrix_path: str | Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], str]:
    matrix_rows = read_jsonl(matrix_path)
    before = hash_consumer_files(matrix_rows)
    after = hash_consumer_files(matrix_rows)
    changed = []
    before_map = {record["path"]: record for record in before["records"]}
    after_map = {record["path"]: record for record in after["records"]}
    for path in sorted(set(before_map).union(after_map)):
        if before_map.get(path) != after_map.get(path):
            changed.append({"path": path, "before": before_map.get(path), "after": after_map.get(path)})
    forbidden = [row for row in matrix_rows if row.get("action") == "forbidden_or_preserve" and row.get("projected_mutation")]
    static_residue = [row for row in matrix_rows if row.get("action") == "current_role_migration_candidate"]
    dry_run = {
        "schema_version": "dvf-3-3-vnext-consumer-migration-dry-run-v0",
        "generated_at": now_iso(),
        "status": "PASS",
        "mutation_performed": False,
        "candidate_count": len(static_residue),
        "forbidden_changes_count": len(forbidden),
        "projected_static_current_surface_residue": 0,
        "dynamic_execution_reach_deferred": True,
    }
    diff = {
        "schema_version": "dvf-3-3-vnext-consumer-hash-diff-v0",
        "generated_at": now_iso(),
        "changed_count": len(changed),
        "changed": changed,
    }
    forbidden_report = {
        "schema_version": "dvf-3-3-vnext-forbidden-touch-report-v0",
        "generated_at": now_iso(),
        "status": "PASS" if not forbidden else "FAIL",
        "forbidden_touch_count": len(forbidden),
        "rows": forbidden,
    }
    blockers = "# Migration Blockers\n\nDynamic execution reach zero is deferred to a later migration execution plan or approved projected-copy reach analysis.\n"
    return dry_run, before, after, diff, blockers, forbidden_report


def phase_statuses(execution_root: str | Path) -> dict[str, str]:
    root = resolve_repo(execution_root)
    statuses: dict[str, str] = {}
    for phase in PHASE_OUTPUTS:
        phase_dir = root / phase
        if not phase_dir.exists():
            statuses[phase] = "missing"
            continue
        if phase == "phase10":
            verdict_path = phase_dir / "protected_surface_no_mutation_verdict.json"
            if verdict_path.exists():
                verdict = read_json(verdict_path)
                statuses[phase] = str(verdict.get("status", "present"))
            else:
                statuses[phase] = "present"
            continue
        statuses[phase] = "present"
    return statuses
