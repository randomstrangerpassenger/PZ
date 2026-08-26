from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .repository_context import (
    current_layer3_generation_root,
    require_external_workspace,
    require_repository_context,
)


ROOT = require_repository_context().description_v2_root
IRIS_MOD_ROOT = require_repository_context().iris_root


def default_output_root() -> Path:
    return (
        require_external_workspace("IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT")
        / "lua_bridge_export"
        / "default"
    )
RENDERED_PATH = current_layer3_generation_root() / "dvf_3_3_rendered.json"
LUA_DATA_DIR = IRIS_MOD_ROOT / "media" / "lua" / "client" / "Iris" / "Data"
BRIDGE_DATA_PATH = LUA_DATA_DIR / "IrisLayer3Data.lua"
BRIDGE_CHUNK_DIR = LUA_DATA_DIR / "IrisLayer3DataChunks"
BRIDGE_CHUNK_MANIFEST_PATH = LUA_DATA_DIR / "IrisLayer3DataChunks.lua"
BRIDGE_CHUNK_MODULE_PREFIX = "Iris/Data/IrisLayer3DataChunks"
PACKAGE_DATA_DIR = IRIS_MOD_ROOT / "build" / "package" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data"
PACKAGE_BRIDGE_DATA_PATH = PACKAGE_DATA_DIR / "IrisLayer3Data.lua"
PACKAGE_BRIDGE_CHUNK_DIR = PACKAGE_DATA_DIR / "IrisLayer3DataChunks"
PACKAGE_BRIDGE_CHUNK_MANIFEST_PATH = PACKAGE_DATA_DIR / "IrisLayer3DataChunks.lua"
RUNTIME_FULLTYPE_ALIASES = {
    "Base.CanOpener": ["Base.TinOpener"],
}
RUNTIME_ENTRY_KEYS = ("text_ko", "source", "publish_state")
DEFAULT_CHUNK_SIZE = 200
REPO_ROOT = require_repository_context().repository_root
REGISTRY_COMPATIBILITY_VALIDATOR = (
    ROOT / "tools" / "build" / "validate_dvf_3_3_registry_runtime_compatibility.py"
)
CURRENT_REQUIRED_VALIDATIONS = (
    REPO_ROOT / "Iris" / "_docs" / "round3" / "current_route_required_validations.json"
)
CURRENT_FACTS = ROOT / "data" / "dvf_3_3_facts.jsonl"
LUA_ENTRY_HEADER_RE = re.compile(r'^    \["(?P<full_type>(?:\\\\|\\"|[^"])*)"\] = \{$')
LUA_ENTRY_KEY_RE = re.compile(r'\["(?P<full_type>(?:\\\\|\\"|[^"])*)"\]\s*=\s*\{')
LUA_CHUNK_MODULE_RE = re.compile(r'^\s+"(?P<module>[^"]+/Chunk\d{3})",\s*$')
BRIDGE_CONTEXTS = {"staging", "historical", "diagnostic"}
OUTPUT_FORMATS = {"chunk", "monolith"}


class BridgeExportContractError(ValueError):
    """Raised when an export request violates the bridge output contract."""


ADOPTION_GENERATION_SCHEMA = "validated-naturalization-adoption-generation-contract-v1"
ADOPTION_GENERATION_FIELDS = {
    "schema_version", "authority_effect", "bridge_context",
    "candidate_path", "candidate_sha256", "facts_path", "facts_sha256",
    "input_manifest_path", "input_manifest_sha256",
    "adoption_owned_parent_root", "output_root", "expected_shape",
}


@dataclass(frozen=True)
class RegistryCompatibilityInvocation:
    policy_context: str
    policy_path: Path
    disposition_path: Path
    binding_manifest_path: Path
    bridge_preflight_input_manifest: Path
    bridge_preflight_receipt: Path
    resolution_mode: str = "explicit"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _is_reparse_point(path: Path) -> bool:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return False
    attributes = getattr(metadata, "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def _existing_path_chain(path: Path) -> list[Path]:
    rows: list[Path] = []
    current = path
    while True:
        if current.exists() or current.is_symlink():
            rows.append(current)
        if current.parent == current:
            return rows
        current = current.parent


def validate_adoption_generation_contract(
    *, contract_path: Path, rendered_path: Path, output_root: Path,
    report_path: Path, bridge_context: str
) -> dict[str, Any]:
    if not contract_path.is_file():
        raise BridgeExportContractError("adoption_contract_missing")
    contract = load_json(contract_path)
    if set(contract) != ADOPTION_GENERATION_FIELDS:
        raise BridgeExportContractError("adoption_contract_fields_invalid")
    if contract.get("schema_version") != ADOPTION_GENERATION_SCHEMA:
        raise BridgeExportContractError("adoption_contract_schema_invalid")
    if contract.get("authority_effect") != "none":
        raise BridgeExportContractError("adoption_authority_effect_invalid")
    if bridge_context != "staging" or contract.get("bridge_context") != "staging":
        raise BridgeExportContractError("adoption_bridge_context_invalid")
    paths: dict[str, Path] = {}
    for role, path_field, hash_field in (
        ("candidate", "candidate_path", "candidate_sha256"),
        ("facts", "facts_path", "facts_sha256"),
        ("input_manifest", "input_manifest_path", "input_manifest_sha256"),
    ):
        path = Path(str(contract.get(path_field, "")))
        if not path.is_absolute() or not path.is_file():
            raise BridgeExportContractError(f"{role}_input_missing")
        if hashlib.sha256(path.read_bytes()).hexdigest() != contract.get(hash_field):
            raise BridgeExportContractError(f"{role}_hash_mismatch")
        paths[role] = path.resolve()
    if paths["candidate"] != rendered_path.resolve():
        raise BridgeExportContractError("candidate_path_mismatch")
    parent = Path(str(contract.get("adoption_owned_parent_root", "")))
    contracted_output = Path(str(contract.get("output_root", "")))
    if not parent.is_absolute() or not parent.is_dir() or not contracted_output.is_absolute() or not output_root.is_absolute():
        raise BridgeExportContractError("adoption_output_root_invalid")
    if any(_is_reparse_point(row) for row in _existing_path_chain(parent)) or any(
        _is_reparse_point(row) for row in _existing_path_chain(contracted_output)
    ):
        raise BridgeExportContractError("adoption_output_root_reparse")
    resolved_parent = parent.resolve(strict=True)
    resolved_output = contracted_output.resolve(strict=False)
    if output_root.resolve(strict=False) != resolved_output or resolved_parent not in resolved_output.parents:
        raise BridgeExportContractError("adoption_output_root_escape")
    if report_path.resolve(strict=False) != resolved_output / "bridge_export_report.json":
        raise BridgeExportContractError("adoption_report_path_invalid")
    if contracted_output.exists() and (not contracted_output.is_dir() or any(contracted_output.iterdir())):
        raise BridgeExportContractError("adoption_output_root_not_fresh")
    rendered = load_json(paths["candidate"])
    entries = rendered.get("entries", {})
    observed_shape = {
        "total": len(entries),
        "adopted_public": sum(row.get("source") == "korean_prose_candidate_v1" for row in entries.values()),
        "unadopted": sum(row.get("source") == "unadopted" for row in entries.values()),
        "public_text": sum(isinstance(row.get("text_ko"), str) and bool(row["text_ko"]) for row in entries.values()),
    }
    if contract.get("expected_shape") != observed_shape:
        raise BridgeExportContractError("adoption_expected_shape_mismatch")
    return {
        "schema_version": "validated-naturalization-adoption-generation-validation-v1",
        "status": "PASS", "authority_effect": "none",
        "validation_mode": "adoption_generation", "observed_shape": observed_shape,
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def resolve_path(path: Path) -> Path:
    return path.expanduser().resolve()


def is_same_or_under(path: Path, root: Path) -> bool:
    resolved_path = resolve_path(path)
    resolved_root = resolve_path(root)
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def is_same_under_or_contains(path: Path, root: Path) -> bool:
    resolved_path = resolve_path(path)
    resolved_root = resolve_path(root)
    return (
        resolved_path == resolved_root
        or resolved_root in resolved_path.parents
        or resolved_path in resolved_root.parents
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_utf8_normalized_eol(path: Path) -> str:
    """Hash generated text independent of the checkout's LF/CRLF policy."""
    text = path.read_bytes().decode("utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def reject_stale_current_source_alignment(
    selection: dict[str, Any],
    *,
    isolated_candidate_probe: bool,
) -> None:
    alignment = selection.get("current_source_alignment")
    if alignment is None:
        return
    if not isinstance(alignment, dict):
        raise BridgeExportContractError(
            "registry_runtime_compatibility_current_source_alignment_invalid"
        )
    if alignment.get("state") != "stale_requires_successor_rtc":
        return
    if isolated_candidate_probe:
        if alignment.get("isolated_successor_candidate_probe_allowed") is not True:
            raise BridgeExportContractError(
                "registry_runtime_compatibility_current_source_stale"
            )
        return
    expected_path = alignment.get("applies_when_current_facts_path")
    expected_sha256 = alignment.get("applies_when_current_facts_sha256")
    if (
        expected_path
        != "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
        or not isinstance(expected_sha256, str)
        or len(expected_sha256) != 64
        or not CURRENT_FACTS.is_file()
    ):
        raise BridgeExportContractError(
            "registry_runtime_compatibility_current_source_alignment_invalid"
        )
    if sha256_file(CURRENT_FACTS) == expected_sha256:
        raise BridgeExportContractError(
            "registry_runtime_compatibility_current_source_stale"
        )


def resolve_registry_compatibility_invocation_from_manifest(
    *,
    rendered_path: Path,
    report_path: Path,
    required_manifest: Path,
    candidate_manifest_probe: bool,
) -> RegistryCompatibilityInvocation:
    selected_manifest = required_manifest.resolve()
    if not selected_manifest.is_file():
        raise BridgeExportContractError(
            "compatibility_policy_context_required: required-validation "
            "manifest is missing"
        )
    manifest = load_json(selected_manifest)
    selection = manifest.get("registry_runtime_compatibility")
    if not isinstance(selection, dict):
        raise BridgeExportContractError(
            "compatibility_policy_context_required: live required-validation "
            "manifest has no Registry Runtime Compatibility selection"
        )
    candidate_state_valid = (
        candidate_manifest_probe
        and selection.get("candidate_manifest_probe") is True
        and selection.get("policy_lifecycle_state")
        == "package_guard_active_not_required_gate_adopted"
    )
    reject_stale_current_source_alignment(
        selection,
        isolated_candidate_probe=candidate_state_valid,
    )
    if (
        selection.get("policy_lifecycle_state") != "live_required_gate_adopted"
        and not candidate_state_valid
    ):
        raise BridgeExportContractError(
            "compatibility_policy_context_required: selected policy is not "
            "live-gate adopted"
        )
    bundle_root_value = selection.get("bundle_root")
    if not isinstance(bundle_root_value, str):
        raise BridgeExportContractError(
            "compatibility_policy_context_required: selected bundle root is missing"
        )
    bundle_root = (REPO_ROOT / Path(bundle_root_value)).resolve()
    bundle_manifest = bundle_root / "durable_bundle_manifest.json"
    if (
        not bundle_manifest.is_file()
        or sha256_file(bundle_manifest) != selection.get("bundle_manifest_sha256")
    ):
        raise BridgeExportContractError(
            "live_bundle_manifest_hash_mismatch: required manifest does not bind "
            "the selected durable bundle"
        )
    policy_path = bundle_root / "registry_runtime_compatibility_policy.json"
    disposition_path = bundle_root / "current_collision_disposition.json"
    binding_path = bundle_root / "candidate_contract_binding_manifest.json"
    input_path = report_path.with_name("bridge_preflight_inputs.json")
    receipt_path = report_path.with_name("bridge_preflight_report.json")
    resolution_mode = (
        "candidate_required_manifest_override"
        if candidate_state_valid
        else "post_adoption_live_manifest_default"
    )
    dump_json(
        input_path,
        {
            "schema_version": "rtc-bridge-preflight-input-v1",
            "round_id": "dvf_3_3_registry_runtime_compatibility",
            "producer_attempt_id": selection.get("attempt_id"),
            "resolution_mode": resolution_mode,
            "rendered": {
                "path": str(rendered_path.resolve()),
                "sha256": sha256_file(rendered_path),
                "byte_count": rendered_path.stat().st_size,
            },
            "binding_manifest_path": str(binding_path),
            "binding_manifest_sha256": sha256_file(binding_path),
            "policy_path": str(policy_path),
            "policy_sha256": sha256_file(policy_path),
            "disposition_path": str(disposition_path),
            "disposition_sha256": sha256_file(disposition_path),
            "required_manifest_path": str(selected_manifest),
            "required_manifest_sha256": sha256_file(selected_manifest),
        },
    )
    return RegistryCompatibilityInvocation(
        policy_context="canonical_durable",
        policy_path=policy_path,
        disposition_path=disposition_path,
        binding_manifest_path=binding_path,
        bridge_preflight_input_manifest=input_path,
        bridge_preflight_receipt=receipt_path,
        resolution_mode=resolution_mode,
    )


def resolve_live_registry_compatibility_invocation(
    *,
    rendered_path: Path,
    report_path: Path,
) -> RegistryCompatibilityInvocation:
    return resolve_registry_compatibility_invocation_from_manifest(
        rendered_path=rendered_path,
        report_path=report_path,
        required_manifest=CURRENT_REQUIRED_VALIDATIONS,
        candidate_manifest_probe=False,
    )


def run_registry_compatibility_preflight(
    *,
    rendered_path: Path,
    report_path: Path,
    invocation: RegistryCompatibilityInvocation | None,
) -> tuple[RegistryCompatibilityInvocation, dict[str, Any]]:
    if invocation is not None:
        required_manifest = load_json(CURRENT_REQUIRED_VALIDATIONS)
        current_selection = required_manifest.get(
            "registry_runtime_compatibility"
        )
        if not isinstance(current_selection, dict):
            raise BridgeExportContractError(
                "compatibility_policy_context_required: live "
                "required-validation manifest has no Registry Runtime "
                "Compatibility selection"
            )
        reject_stale_current_source_alignment(
            current_selection,
            isolated_candidate_probe=invocation.policy_context == "candidate",
        )
    selected = invocation or resolve_live_registry_compatibility_invocation(
        rendered_path=rendered_path,
        report_path=report_path,
    )
    required_paths = (
        selected.policy_path,
        selected.disposition_path,
        selected.binding_manifest_path,
        selected.bridge_preflight_input_manifest,
        REGISTRY_COMPATIBILITY_VALIDATOR,
    )
    missing = [str(path) for path in required_paths if not path.is_file()]
    if missing:
        raise BridgeExportContractError(
            f"compatibility_required_input_missing: {missing}"
        )
    python_path = Path(sys.executable).resolve()
    command = [
        str(python_path),
        "-B",
        str(REGISTRY_COMPATIBILITY_VALIDATOR.resolve()),
        "--bridge-preflight",
        "--bridge-preflight-input-manifest",
        str(selected.bridge_preflight_input_manifest.resolve()),
        "--policy-context",
        selected.policy_context,
        "--policy",
        str(selected.policy_path.resolve()),
        "--disposition",
        str(selected.disposition_path.resolve()),
        "--binding-manifest",
        str(selected.binding_manifest_path.resolve()),
        "--out",
        str(selected.bridge_preflight_receipt.resolve()),
    ]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    receipt = (
        load_json(selected.bridge_preflight_receipt)
        if selected.bridge_preflight_receipt.is_file()
        else {}
    )
    execution = {
        "schema_version": "rtc-bridge-preflight-execution-v1",
        "resolution_mode": selected.resolution_mode,
        "command_argv": command,
        "child_exit_code": completed.returncode,
        "child_stdout": completed.stdout,
        "child_stderr": completed.stderr,
        "python_executable_path": str(python_path),
        "python_executable_sha256": sha256_file(python_path),
        "validator_path": str(REGISTRY_COMPATIBILITY_VALIDATOR.resolve()),
        "validator_sha256": sha256_file(REGISTRY_COMPATIBILITY_VALIDATOR),
        "receipt_path": str(selected.bridge_preflight_receipt.resolve()),
        "receipt_sha256": (
            sha256_file(selected.bridge_preflight_receipt)
            if selected.bridge_preflight_receipt.is_file()
            else None
        ),
        "validator_report_status": receipt.get("status"),
    }
    if completed.returncode != 0 or receipt.get("status") != "PASS":
        failure_code = receipt.get("failure_code", "bridge_preflight_child_failed")
        raise BridgeExportContractError(
            f"{failure_code}: validator exited {completed.returncode}; "
            f"stderr={completed.stderr.strip()}"
        )
    if receipt.get("rendered_sha256") != sha256_file(rendered_path):
        raise BridgeExportContractError(
            "bridge_preflight_receipt_rendered_hash_mismatch"
        )
    return selected, execution


def protected_monolith_paths() -> set[Path]:
    return {
        resolve_path(BRIDGE_DATA_PATH),
        resolve_path(PACKAGE_BRIDGE_DATA_PATH),
    }


def protected_chunk_manifests() -> set[Path]:
    return {
        resolve_path(BRIDGE_CHUNK_MANIFEST_PATH),
        resolve_path(PACKAGE_BRIDGE_CHUNK_MANIFEST_PATH),
    }


def protected_chunk_dirs() -> set[Path]:
    return {
        resolve_path(BRIDGE_CHUNK_DIR),
        resolve_path(PACKAGE_BRIDGE_CHUNK_DIR),
    }


def classify_input_scale(rendered: dict[str, Any]) -> str:
    entry_count = len(rendered.get("entries", {}))
    if entry_count == 6:
        return "fixture"
    if entry_count >= 1000:
        return "full"
    return "unknown"


def classify_input_authority_status(input_scale: str, rendered: dict[str, Any]) -> str:
    if input_scale == "fixture":
        return "fixture_non_authority"
    if input_scale == "full":
        return "full_authority_input"
    if rendered.get("entries"):
        return "staging_candidate"
    return "unknown_blocked"


def count_adoption_states(rendered: dict[str, Any], source_entries: dict[str, Any]) -> tuple[int, int]:
    stats = rendered.get("meta", {}).get("stats", {})
    adopted_count = stats.get("adopted_override")
    adopted_composed = stats.get("adopted_composed")
    unadopted_count = stats.get("unadopted")
    if isinstance(adopted_count, int) or isinstance(adopted_composed, int) or isinstance(unadopted_count, int):
        return int(adopted_count or 0) + int(adopted_composed or 0), int(unadopted_count or 0)

    adopted = 0
    unadopted = 0
    for entry in source_entries.values():
        state = entry.get("state") if isinstance(entry, dict) else None
        if state == "adopted":
            adopted += 1
        elif state == "unadopted":
            unadopted += 1
    return adopted, unadopted


def validate_bridge_request(
    *,
    bridge_context: str,
    output_format: str,
    lua_output_path: Path | None,
    chunk_manifest_path: Path | None,
    chunk_output_dir: Path | None,
) -> None:
    if bridge_context not in BRIDGE_CONTEXTS:
        raise BridgeExportContractError(
            f"Unsupported bridge_context {bridge_context!r}; allowed values are diagnostic, historical, staging."
        )
    if output_format not in OUTPUT_FORMATS:
        raise BridgeExportContractError(f"Unsupported bridge output format {output_format!r}.")
    if output_format == "monolith" and bridge_context not in {"diagnostic", "historical"}:
        raise BridgeExportContractError("Monolith Lua bridge output is allowed only in diagnostic or historical context.")
    if output_format == "monolith" and lua_output_path is None:
        raise BridgeExportContractError("Monolith Lua bridge output requires an explicit --lua-output-path.")

    if lua_output_path is not None:
        resolved_lua_path = resolve_path(lua_output_path)
        if resolved_lua_path in protected_monolith_paths():
            raise BridgeExportContractError(f"Refusing to write or target protected monolith bridge path: {lua_output_path}")
        for data_dir in (LUA_DATA_DIR, PACKAGE_DATA_DIR):
            if lua_output_path.name == "IrisLayer3Data.lua" and is_same_or_under(lua_output_path, data_dir):
                raise BridgeExportContractError(f"Refusing current/package-looking monolith path: {lua_output_path}")

    if output_format == "chunk":
        if chunk_manifest_path is None or chunk_output_dir is None:
            raise BridgeExportContractError("Chunk Lua bridge output requires chunk manifest path and chunk output dir.")
        resolved_manifest = resolve_path(chunk_manifest_path)
        if resolved_manifest in protected_chunk_manifests():
            raise BridgeExportContractError(f"Refusing to write protected chunk manifest path: {chunk_manifest_path}")
        for protected_dir in protected_chunk_dirs():
            if is_same_under_or_contains(chunk_output_dir, protected_dir):
                raise BridgeExportContractError(f"Refusing to write protected chunk output dir: {chunk_output_dir}")
        for package_dir in (LUA_DATA_DIR, PACKAGE_DATA_DIR):
            if (
                chunk_manifest_path.name == "IrisLayer3DataChunks.lua"
                and is_same_or_under(chunk_manifest_path, package_dir)
            ):
                raise BridgeExportContractError(f"Refusing current/package-looking chunk manifest path: {chunk_manifest_path}")


def escape_lua_string(value: str) -> str:
    result: list[str] = []
    for ch in value:
        if ord(ch) > 127:
            for byte in ch.encode("utf-8"):
                result.append("\\" + str(byte))
        elif ch == "\\":
            result.append("\\\\")
        elif ch == "\r":
            result.append("\\r")
        elif ch == "\n":
            result.append("\\n")
        elif ch == '"':
            result.append('\\"')
        else:
            result.append(ch)
    return "".join(result)


def to_lua(value: Any, *, indent: int = 0) -> str:
    pad = "    " * indent
    child_pad = "    " * (indent + 1)

    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return f'"{escape_lua_string(value)}"'
    if isinstance(value, list):
        if not value:
            return "{}"
        lines = ["{"]
        for item in value:
            lines.append(f"{child_pad}{to_lua(item, indent=indent + 1)},")
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = ["{"]
        for key in sorted(value):
            lines.append(
                f'{child_pad}["{escape_lua_string(str(key))}"] = {to_lua(value[key], indent=indent + 1)},'
            )
        lines.append(f"{pad}}}")
        return "\n".join(lines)
    raise TypeError(f"Unsupported Lua bridge type: {type(value)!r}")


def build_lua_module(payload: dict[str, Any]) -> str:
    entries = payload.get("entries", {})
    table_literal = to_lua(entries)
    return "\n".join(
        [
            "-- Auto-generated by export_dvf_3_3_lua_bridge.py.",
            "-- Do not edit manually. Rebuild from Iris/build/description/v2/output/dvf_3_3_rendered.json.",
            "",
            f"local data = {table_literal}",
            "",
            "IrisLayer3Data = data",
            "",
            "return data",
            "",
        ]
    )


def build_lua_chunk(entries: dict[str, Any], chunk_number: int) -> str:
    table_literal = to_lua(entries)
    return "\n".join(
        [
            "-- Auto-generated by export_dvf_3_3_lua_bridge.py.",
            "-- Do not edit manually. Rebuild from Iris/build/description/v2/output/dvf_3_3_rendered.json.",
            f"-- Chunk: {chunk_number:03d}",
            "",
            f"return {table_literal}",
            "",
        ]
    )


def build_lua_chunk_from_blocks(
    *,
    entry_blocks: list[list[str]],
    chunk_number: int,
    source_path: Path | str,
) -> str:
    source_label = source_path.as_posix() if isinstance(source_path, Path) else source_path
    lines = [
        "-- Auto-generated by export_dvf_3_3_lua_bridge.py.",
        "-- Do not edit manually. Rebuild from the authoritative Layer 3 runtime source.",
        f"-- Source: {source_label}",
        f"-- Chunk: {chunk_number:03d}",
        "",
        "return {",
    ]
    for entry_block in entry_blocks:
        lines.extend(entry_block)
    lines.extend(["}", ""])
    return "\n".join(lines)


def build_lua_chunk_manifest(
    *,
    chunk_modules: list[str],
    entry_count: int,
    chunk_size: int,
) -> str:
    module_lines = [f'    "{module_name}",' for module_name in chunk_modules]
    chunk_module_table = "\n".join(["local chunkModules = {", *module_lines, "}"])
    return "\n".join(
        [
            "-- Auto-generated by export_dvf_3_3_lua_bridge.py.",
            "-- Do not edit manually. Rebuild from the authoritative Layer 3 runtime source.",
            f"-- Total runtime entries: {entry_count}",
            f"-- Chunks: {len(chunk_modules)} x <= {chunk_size}",
            "",
            "local data = {}",
            "",
            chunk_module_table,
            "",
            "for _, moduleName in ipairs(chunkModules) do",
            "    local chunk = require(moduleName)",
            "    for fullType, entry in pairs(chunk) do",
            "        data[fullType] = entry",
            "    end",
            "end",
            "",
            "IrisLayer3Data = data",
            "",
            "return data",
            "",
        ]
    )


def build_lua_chunk_index(*, chunk_records: list[dict[str, Any]], entry_count: int) -> str:
    lines = [
        "-- Auto-generated by export_dvf_3_3_lua_bridge.py.",
        "-- Routing metadata only; IrisLayer3DataChunks remains the public facade.",
        "-- sha256 hashes strict UTF-8 text after CRLF/CR -> LF normalization.",
        "return {",
        '    schema_version = "iris_layer3_chunk_range_index_v1",',
        f"    entry_count = {entry_count},",
        "    chunks = {",
    ]
    for record in chunk_records:
        lines.append(
            "        { count = %d, first = %s, last = %s, module = %s, sha256 = %s },"
            % (
                record["entry_count"],
                to_lua(record["first"]),
                to_lua(record["last"]),
                to_lua(record["module"]),
                to_lua(record["sha256"]),
            )
        )
    lines.extend(["    },", "}", ""])
    return "\n".join(lines)


def write_lua_chunk_index(
    *, chunk_manifest_path: Path, chunk_records: list[dict[str, Any]], entry_count: int
) -> tuple[Path, str]:
    index_path = chunk_manifest_path.with_name("IrisLayer3DataChunkIndex.lua")
    with index_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(build_lua_chunk_index(chunk_records=chunk_records, entry_count=entry_count))
    return index_path, sha256_file(index_path)


def chunk_entries(entries: dict[str, Any], chunk_size: int) -> list[dict[str, Any]]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    sorted_keys = sorted(entries)
    chunks: list[dict[str, Any]] = []
    for start in range(0, len(sorted_keys), chunk_size):
        chunk_keys = sorted_keys[start : start + chunk_size]
        chunks.append({key: entries[key] for key in chunk_keys})
    return chunks


def extract_lua_entry_blocks(lua_text: str) -> list[tuple[str, list[str]]]:
    lines = lua_text.splitlines()
    try:
        start_index = lines.index("local data = {") + 1
        end_index = lines.index("IrisLayer3Data = data")
    except ValueError as exc:
        raise ValueError("Input Lua file does not match IrisLayer3Data module shape") from exc

    entry_blocks: list[tuple[str, list[str]]] = []
    current_key: str | None = None
    current_block: list[str] = []
    for line in lines[start_index:end_index]:
        if not line:
            continue
        if current_key is None:
            if line == "}":
                break
            match = LUA_ENTRY_HEADER_RE.match(line)
            if match:
                current_key = match.group("full_type")
                current_block = [line]
            elif line.strip():
                raise ValueError(f"Unexpected top-level Lua line before entry: {line!r}")
            continue

        current_block.append(line)
        if line == "    },":
            entry_blocks.append((current_key, current_block))
            current_key = None
            current_block = []

    if current_key is not None:
        raise ValueError(f"Unclosed Lua entry block for {current_key!r}")
    if not entry_blocks:
        raise ValueError("No IrisLayer3Data entries found in input Lua file")
    return entry_blocks


def parse_chunk_manifest_modules(manifest_text: str) -> list[str]:
    modules: list[str] = []
    for line in manifest_text.splitlines():
        match = LUA_CHUNK_MODULE_RE.match(line)
        if match:
            modules.append(match.group("module"))
    return modules


def validate_chunk_bundle(
    *,
    chunk_manifest_path: Path,
    chunk_output_dir: Path,
) -> dict[str, Any]:
    modules = parse_chunk_manifest_modules(chunk_manifest_path.read_text(encoding="utf-8"))
    expected_files = {module.rsplit("/", 1)[-1] + ".lua" for module in modules}
    actual_files = {path.name for path in chunk_output_dir.glob("Chunk*.lua") if path.is_file()}
    missing_chunks = sorted(expected_files - actual_files)
    orphan_chunks = sorted(actual_files - expected_files)

    seen_keys: dict[str, str] = {}
    duplicate_keys: list[dict[str, str]] = []
    chunk_hashes: list[dict[str, Any]] = []
    for module in modules:
        chunk_name = module.rsplit("/", 1)[-1] + ".lua"
        chunk_path = chunk_output_dir / chunk_name
        if not chunk_path.exists():
            continue
        text = chunk_path.read_text(encoding="utf-8")
        keys = [match.group("full_type") for match in LUA_ENTRY_KEY_RE.finditer(text)]
        for key in keys:
            previous = seen_keys.get(key)
            if previous is not None:
                duplicate_keys.append({"full_type": key, "first_chunk": previous, "duplicate_chunk": chunk_name})
            else:
                seen_keys[key] = chunk_name
        chunk_hashes.append(
            {
                "module": module,
                "path": str(chunk_path),
                "sha256": sha256_file(chunk_path),
                "bytes": chunk_path.stat().st_size,
                "entry_count": len(keys),
            }
        )

    failures = []
    if not modules:
        failures.append("manifest_has_no_chunk_modules")
    if missing_chunks:
        failures.append("manifest_references_missing_chunks")
    if orphan_chunks:
        failures.append("chunk_dir_has_orphan_chunks")
    if duplicate_keys:
        failures.append("duplicate_full_type_across_chunks")

    return {
        "schema_version": "iris-lua-bridge-chunk-integrity-v1",
        "chunk_manifest_path": str(chunk_manifest_path),
        "chunk_output_dir": str(chunk_output_dir),
        "chunk_count": len(modules),
        "manifest_modules": modules,
        "missing_chunks": missing_chunks,
        "orphan_chunks": orphan_chunks,
        "duplicate_keys": duplicate_keys,
        "manifest_hash": sha256_file(chunk_manifest_path),
        "chunk_hashes": chunk_hashes,
        "pass": not failures,
        "failures": failures,
    }


def require_valid_chunk_bundle(*, chunk_manifest_path: Path, chunk_output_dir: Path) -> dict[str, Any]:
    report = validate_chunk_bundle(chunk_manifest_path=chunk_manifest_path, chunk_output_dir=chunk_output_dir)
    if not report["pass"]:
        raise BridgeExportContractError(f"Invalid Lua bridge chunk bundle: {', '.join(report['failures'])}")
    return report


def write_chunked_lua_bridge_from_monolith(
    *,
    lua_input_path: Path,
    chunk_output_dir: Path,
    chunk_manifest_path: Path,
    chunk_size: int,
    chunk_module_prefix: str = BRIDGE_CHUNK_MODULE_PREFIX,
    bridge_context: str = "historical",
) -> dict[str, Any]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    validate_bridge_request(
        bridge_context=bridge_context,
        output_format="chunk",
        lua_output_path=None,
        chunk_output_dir=chunk_output_dir,
        chunk_manifest_path=chunk_manifest_path,
    )

    entry_blocks = extract_lua_entry_blocks(lua_input_path.read_text(encoding="utf-8"))
    chunk_output_dir.mkdir(parents=True, exist_ok=True)
    chunk_manifest_path.parent.mkdir(parents=True, exist_ok=True)

    for stale_chunk in chunk_output_dir.glob("Chunk*.lua"):
        if stale_chunk.is_file():
            stale_chunk.unlink()

    chunk_records: list[dict[str, Any]] = []
    chunk_modules: list[str] = []
    for index, start in enumerate(range(0, len(entry_blocks), chunk_size), start=1):
        selected_blocks = entry_blocks[start : start + chunk_size]
        block_slice = [block for _, block in selected_blocks]
        chunk_keys = [key for key, _ in selected_blocks]
        chunk_name = f"Chunk{index:03d}"
        chunk_path = chunk_output_dir / f"{chunk_name}.lua"
        chunk_module_name = f"{chunk_module_prefix}/{chunk_name}"
        with chunk_path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(
                build_lua_chunk_from_blocks(
                    entry_blocks=block_slice,
                    chunk_number=index,
                    source_path=lua_input_path.name,
                )
            )
        chunk_modules.append(chunk_module_name)
        chunk_records.append(
            {
                "module": chunk_module_name,
                "path": str(chunk_path),
                "entry_count": len(block_slice),
                "first": chunk_keys[0],
                "last": chunk_keys[-1],
                "sha256": sha256_utf8_normalized_eol(chunk_path),
            }
        )

    manifest_text = build_lua_chunk_manifest(
        chunk_modules=chunk_modules,
        entry_count=len(entry_blocks),
        chunk_size=chunk_size,
    )
    with chunk_manifest_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(manifest_text)
    chunk_index_path, chunk_index_hash = write_lua_chunk_index(
        chunk_manifest_path=chunk_manifest_path,
        chunk_records=chunk_records,
        entry_count=len(entry_blocks),
    )

    integrity_report = require_valid_chunk_bundle(
        chunk_manifest_path=chunk_manifest_path,
        chunk_output_dir=chunk_output_dir,
    )
    return {
        "schema_version": "interaction-cluster-phase-d-lua-bridge-chunks-from-monolith-v0",
        "source_lua_path": str(lua_input_path),
        "bridge_context": bridge_context,
        "format": "chunk",
        "chunked": True,
        "chunk_size": chunk_size,
        "chunk_count": len(chunk_records),
        "entry_count": len(entry_blocks),
        "runtime_entry_count": len(entry_blocks),
        "chunk_manifest_path": str(chunk_manifest_path),
        "chunk_index_path": str(chunk_index_path),
        "chunk_output_dir": str(chunk_output_dir),
        "chunk_modules": chunk_records,
        "manifest_hash": integrity_report["manifest_hash"],
        "index_hash": chunk_index_hash,
        "chunk_hashes": integrity_report["chunk_hashes"],
        "pass": True,
    }


def write_chunked_lua_bridge(
    *,
    entries: dict[str, Any],
    chunk_output_dir: Path,
    chunk_manifest_path: Path,
    chunk_size: int,
    chunk_module_prefix: str = BRIDGE_CHUNK_MODULE_PREFIX,
    bridge_context: str = "staging",
) -> dict[str, Any]:
    validate_bridge_request(
        bridge_context=bridge_context,
        output_format="chunk",
        lua_output_path=None,
        chunk_output_dir=chunk_output_dir,
        chunk_manifest_path=chunk_manifest_path,
    )
    chunk_output_dir.mkdir(parents=True, exist_ok=True)
    chunk_manifest_path.parent.mkdir(parents=True, exist_ok=True)

    for stale_chunk in chunk_output_dir.glob("Chunk*.lua"):
        if stale_chunk.is_file():
            stale_chunk.unlink()

    chunk_records: list[dict[str, Any]] = []
    chunk_modules: list[str] = []
    for index, chunk in enumerate(chunk_entries(entries, chunk_size), start=1):
        chunk_name = f"Chunk{index:03d}"
        chunk_path = chunk_output_dir / f"{chunk_name}.lua"
        chunk_module_name = f"{chunk_module_prefix}/{chunk_name}"
        with chunk_path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(build_lua_chunk(chunk, index))
        chunk_modules.append(chunk_module_name)
        chunk_records.append(
            {
                "module": chunk_module_name,
                "path": str(chunk_path),
                "entry_count": len(chunk),
                "first": min(chunk),
                "last": max(chunk),
                "sha256": sha256_utf8_normalized_eol(chunk_path),
            }
        )

    manifest_text = build_lua_chunk_manifest(
        chunk_modules=chunk_modules,
        entry_count=len(entries),
        chunk_size=chunk_size,
    )
    with chunk_manifest_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(manifest_text)
    chunk_index_path, chunk_index_hash = write_lua_chunk_index(
        chunk_manifest_path=chunk_manifest_path,
        chunk_records=chunk_records,
        entry_count=len(entries),
    )

    integrity_report = require_valid_chunk_bundle(
        chunk_manifest_path=chunk_manifest_path,
        chunk_output_dir=chunk_output_dir,
    )
    return {
        "chunked": True,
        "chunk_size": chunk_size,
        "chunk_count": len(chunk_records),
        "chunk_manifest_path": str(chunk_manifest_path),
        "chunk_index_path": str(chunk_index_path),
        "chunk_output_dir": str(chunk_output_dir),
        "chunk_modules": chunk_records,
        "manifest_hash": integrity_report["manifest_hash"],
        "index_hash": chunk_index_hash,
        "chunk_hashes": integrity_report["chunk_hashes"],
        "chunk_integrity": integrity_report,
    }


def load_publish_preview_map(path: Path | None) -> dict[str, str]:
    if path is None or not path.exists():
        return {}

    publish_preview_map: dict[str, str] = {}
    for row in load_jsonl(path):
        publish_state = row.get("publish_state")
        item_id = row.get("item_id")
        if item_id and publish_state in {"internal_only", "exposed"}:
            publish_preview_map[str(item_id)] = str(publish_state)
    return publish_preview_map


def merge_publish_state(
    entries: dict[str, Any],
    publish_preview_map: dict[str, str],
) -> tuple[dict[str, Any], dict[str, int]]:
    merged_entries: dict[str, Any] = {}
    counts = {"internal_only": 0, "exposed": 0}

    for full_type, entry in entries.items():
        runtime_entry = dict(entry)
        publish_state = publish_preview_map.get(full_type)
        if publish_state in counts:
            runtime_entry["publish_state"] = publish_state
            counts[publish_state] += 1
        merged_entries[full_type] = runtime_entry

    return merged_entries, counts


def with_runtime_aliases(entries: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    runtime_entries = {
        full_type: {
            key: value
            for key, value in entry.items()
            if key in RUNTIME_ENTRY_KEYS
        }
        for full_type, entry in entries.items()
    }
    applied_aliases: list[dict[str, str]] = []
    for source_full_type, alias_full_types in RUNTIME_FULLTYPE_ALIASES.items():
        source_entry = runtime_entries.get(source_full_type)
        if not source_entry:
            continue
        for alias_full_type in alias_full_types:
            if alias_full_type in runtime_entries:
                continue
            runtime_entries[alias_full_type] = source_entry
            applied_aliases.append(
                {
                    "source_full_type": source_full_type,
                    "alias_full_type": alias_full_type,
                }
            )
    return runtime_entries, applied_aliases


def export_lua_bridge(
    *,
    rendered_path: Path = RENDERED_PATH,
    publish_preview_path: Path | None = None,
    lua_output_path: Path | None = None,
    report_path: Path | None = None,
    chunk_output_dir: Path | None = None,
    chunk_manifest_path: Path | None = None,
    chunk_size: int | None = None,
    chunk_module_prefix: str = BRIDGE_CHUNK_MODULE_PREFIX,
    bridge_context: str = "staging",
    output_format: str = "chunk",
    output_root: Path | None = None,
    registry_compatibility: RegistryCompatibilityInvocation | None = None,
    adoption_generation_validation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_chunk_size = chunk_size if chunk_size is not None else DEFAULT_CHUNK_SIZE
    resolved_output_root = output_root if output_root is not None else default_output_root()
    resolved_report_path = (
        report_path if report_path is not None else resolved_output_root / "bridge_export_report.json"
    )
    if output_format == "chunk":
        resolved_chunk_output_dir = chunk_output_dir if chunk_output_dir is not None else resolved_output_root / "IrisLayer3DataChunks"
        resolved_chunk_manifest_path = (
            chunk_manifest_path if chunk_manifest_path is not None else resolved_output_root / "IrisLayer3DataChunks.lua"
        )
    else:
        resolved_chunk_output_dir = chunk_output_dir
        resolved_chunk_manifest_path = chunk_manifest_path

    validate_bridge_request(
        bridge_context=bridge_context,
        output_format=output_format,
        lua_output_path=lua_output_path,
        chunk_manifest_path=resolved_chunk_manifest_path,
        chunk_output_dir=resolved_chunk_output_dir,
    )

    selected_compatibility = None
    compatibility_preflight = None
    if (
        adoption_generation_validation is None
        and registry_compatibility is not None
    ):
        selected_compatibility, compatibility_preflight = run_registry_compatibility_preflight(
            rendered_path=rendered_path,
            report_path=resolved_report_path,
            invocation=registry_compatibility,
        )
    rendered = load_json(rendered_path)
    source_entries = rendered.get("entries", {})
    publish_preview_map = load_publish_preview_map(publish_preview_path)
    merged_source_entries, source_publish_counts = merge_publish_state(source_entries, publish_preview_map)
    runtime_entries, applied_aliases = with_runtime_aliases(merged_source_entries)
    runtime_publish_counts = {"internal_only": 0, "exposed": 0}
    for entry in runtime_entries.values():
        publish_state = entry.get("publish_state")
        if publish_state in runtime_publish_counts:
            runtime_publish_counts[publish_state] += 1

    chunk_report = {
        "chunked": False,
        "chunk_size": None,
        "chunk_count": 0,
        "chunk_manifest_path": None,
        "chunk_index_path": None,
        "chunk_output_dir": None,
        "chunk_modules": [],
        "manifest_hash": None,
        "index_hash": None,
        "chunk_hashes": [],
        "chunk_integrity": None,
    }
    monolith_generated = False
    if output_format == "monolith":
        assert lua_output_path is not None
        lua_output_path.parent.mkdir(parents=True, exist_ok=True)
        module_text = build_lua_module({"entries": runtime_entries})
        with lua_output_path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(module_text)
        monolith_generated = True
    else:
        assert resolved_chunk_output_dir is not None
        assert resolved_chunk_manifest_path is not None
        chunk_report = write_chunked_lua_bridge(
            entries=runtime_entries,
            chunk_output_dir=resolved_chunk_output_dir,
            chunk_manifest_path=resolved_chunk_manifest_path,
            chunk_size=resolved_chunk_size,
            chunk_module_prefix=chunk_module_prefix,
            bridge_context=bridge_context,
        )

    input_scale = classify_input_scale(rendered)
    input_authority_status = classify_input_authority_status(input_scale, rendered)
    adopted_count, unadopted_count = count_adoption_states(rendered, source_entries)
    authority_kind = "chunk_bridge_output" if output_format == "chunk" else f"{bridge_context}_monolith"

    report = {
        "schema_version": "iris-lua-bridge-export-v1",
        "authority_kind": authority_kind,
        "bridge_context": bridge_context,
        "format": output_format,
        "report_path": str(resolved_report_path),
        "rendered_path": str(rendered_path),
        "input_rendered_path": str(rendered_path),
        "default_input_rendered_path": str(RENDERED_PATH),
        "default_output_root": str(default_output_root()),
        "output_root": str(resolved_output_root),
        "publish_preview_path": str(publish_preview_path) if publish_preview_path else None,
        "lua_output_path": str(lua_output_path) if lua_output_path else None,
        "legacy_lua_output_path_ignored": (
            str(lua_output_path) if lua_output_path is not None and output_format == "chunk" else None
        ),
        "output_manifest_path": chunk_report["chunk_manifest_path"],
        "output_index_path": chunk_report["chunk_index_path"],
        "output_chunk_dir": chunk_report["chunk_output_dir"],
        "source_entry_count": len(source_entries),
        "runtime_entry_count": len(runtime_entries),
        "entry_count": len(runtime_entries),
        "adopted_count": adopted_count,
        "unadopted_count": unadopted_count,
        "source_publish_state_counts": source_publish_counts,
        "runtime_publish_state_counts": runtime_publish_counts,
        "publish_state_entry_count": runtime_publish_counts["internal_only"] + runtime_publish_counts["exposed"],
        "applied_aliases": applied_aliases,
        "meta": rendered.get("meta", {}),
        "monolith_generated": monolith_generated,
        "non_current": bridge_context in {"diagnostic", "historical"} or output_format == "chunk",
        "input_scale": input_scale,
        "input_authority_status": input_authority_status,
        "pass": True,
        **chunk_report,
    }
    if adoption_generation_validation is not None:
        report.update(adoption_generation_validation)
    elif selected_compatibility is not None:
        report["registry_compatibility"] = {
            "policy_context": selected_compatibility.policy_context,
            "policy_path": str(selected_compatibility.policy_path.resolve()),
            "disposition_path": str(selected_compatibility.disposition_path.resolve()),
            "binding_manifest_path": str(selected_compatibility.binding_manifest_path.resolve()),
            "resolution_mode": selected_compatibility.resolution_mode,
            "bridge_preflight": compatibility_preflight,
        }
    else:
        report["applicability"] = {
            "classification": "non_rtc_staging_or_historical_projection",
            "rtc_certification_claimed": False,
            "rtc_guard_applicable": False,
        }
    dump_json(resolved_report_path, report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Iris layer3 runtime data to Lua.")
    parser.add_argument("--rendered-path", type=Path, default=RENDERED_PATH)
    parser.add_argument("--publish-preview-path", type=Path, default=None)
    parser.add_argument("--bridge-context", choices=sorted(BRIDGE_CONTEXTS), default="staging")
    parser.add_argument("--format", choices=sorted(OUTPUT_FORMATS), default="chunk", dest="output_format")
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--lua-output-path", type=Path, default=None)
    parser.add_argument("--report-path", type=Path, default=None)
    parser.add_argument("--chunk-output-dir", type=Path, default=None)
    parser.add_argument("--chunk-manifest-path", type=Path, default=None)
    parser.add_argument("--chunk-size", type=int, default=None)
    parser.add_argument("--chunk-module-prefix", default=BRIDGE_CHUNK_MODULE_PREFIX)
    parser.add_argument(
        "--registry-compatibility-context",
        choices=("candidate", "canonical_durable"),
    )
    parser.add_argument("--registry-compatibility-policy", type=Path)
    parser.add_argument("--registry-compatibility-disposition", type=Path)
    parser.add_argument("--registry-compatibility-binding-manifest", type=Path)
    parser.add_argument("--bridge-preflight-input-manifest", type=Path)
    parser.add_argument("--bridge-preflight-receipt", type=Path)
    parser.add_argument("--adoption-generation", action="store_true")
    parser.add_argument("--adoption-generation-contract", type=Path)
    parser.add_argument(
        "--chunk-existing-lua-path",
        type=Path,
        default=None,
        help="Write chunk manifest/modules from an existing generated IrisLayer3Data.lua without rewriting it.",
    )
    args = parser.parse_args()
    if args.output_root is None:
        args.output_root = default_output_root()
    if args.report_path is None:
        args.report_path = args.output_root / "bridge_export_report.json"
    return args


def main() -> int:
    args = parse_args()
    compatibility_values = (
        args.registry_compatibility_context,
        args.registry_compatibility_policy,
        args.registry_compatibility_disposition,
        args.registry_compatibility_binding_manifest,
        args.bridge_preflight_input_manifest,
        args.bridge_preflight_receipt,
    )
    adoption_selected = args.adoption_generation or args.adoption_generation_contract is not None
    if adoption_selected and (
        not args.adoption_generation
        or args.adoption_generation_contract is None
        or any(value is not None for value in compatibility_values)
        or args.chunk_existing_lua_path is not None
        or args.publish_preview_path is not None
        or args.output_format != "chunk"
        or args.output_root is None
        or args.lua_output_path is not None
        or args.chunk_output_dir is not None
        or args.chunk_manifest_path is not None
        or args.chunk_size is not None
        or args.chunk_module_prefix != BRIDGE_CHUNK_MODULE_PREFIX
    ):
        raise BridgeExportContractError("adoption_generation_mode_mixed")
    if any(value is not None for value in compatibility_values) and not all(
        value is not None for value in compatibility_values
    ):
        raise BridgeExportContractError(
            "partial_registry_compatibility_arguments_forbidden"
        )
    registry_compatibility = (
        RegistryCompatibilityInvocation(
            policy_context=args.registry_compatibility_context,
            policy_path=args.registry_compatibility_policy,
            disposition_path=args.registry_compatibility_disposition,
            binding_manifest_path=args.registry_compatibility_binding_manifest,
            bridge_preflight_input_manifest=args.bridge_preflight_input_manifest,
            bridge_preflight_receipt=args.bridge_preflight_receipt,
            resolution_mode="explicit",
        )
        if all(value is not None for value in compatibility_values)
        else None
    )
    adoption_validation = None
    if adoption_selected:
        adoption_validation = validate_adoption_generation_contract(
            contract_path=args.adoption_generation_contract.resolve(),
            rendered_path=args.rendered_path.resolve(),
            output_root=args.output_root.resolve(),
            report_path=args.report_path.resolve(),
            bridge_context=args.bridge_context,
        )
    if args.chunk_existing_lua_path is not None:
        selected_compatibility, compatibility_preflight = (
            run_registry_compatibility_preflight(
                rendered_path=args.rendered_path,
                report_path=args.report_path,
                invocation=registry_compatibility,
            )
        )
        report = write_chunked_lua_bridge_from_monolith(
            lua_input_path=args.chunk_existing_lua_path,
            chunk_output_dir=(
                args.chunk_output_dir
                if args.chunk_output_dir is not None
                else args.output_root / "IrisLayer3DataChunks"
            ),
            chunk_manifest_path=(
                args.chunk_manifest_path
                if args.chunk_manifest_path is not None
                else args.output_root / "IrisLayer3DataChunks.lua"
            ),
            chunk_size=args.chunk_size if args.chunk_size is not None else DEFAULT_CHUNK_SIZE,
            chunk_module_prefix=args.chunk_module_prefix,
            bridge_context=args.bridge_context,
        )
        report["registry_compatibility"] = {
            "policy_context": selected_compatibility.policy_context,
            "resolution_mode": selected_compatibility.resolution_mode,
            "bridge_preflight": compatibility_preflight,
        }
        dump_json(args.report_path, report)
        print(
            "lua bridge chunks exported from existing monolith:",
            report["entry_count"],
            "entries ->",
            report["chunk_manifest_path"],
        )
        return 0

    report = export_lua_bridge(
        rendered_path=args.rendered_path,
        publish_preview_path=args.publish_preview_path,
        lua_output_path=args.lua_output_path,
        report_path=args.report_path,
        chunk_output_dir=args.chunk_output_dir,
        chunk_manifest_path=args.chunk_manifest_path,
        chunk_size=args.chunk_size,
        chunk_module_prefix=args.chunk_module_prefix,
        bridge_context=args.bridge_context,
        output_format=args.output_format,
        output_root=args.output_root,
        registry_compatibility=registry_compatibility,
        adoption_generation_validation=adoption_validation,
    )
    if report["chunked"]:
        print(
            "lua bridge chunk export:",
            report["entry_count"],
            "entries,",
            report["chunk_count"],
            "chunks ->",
            report["chunk_manifest_path"],
        )
    else:
        print(
            "lua bridge monolith export:",
            report["entry_count"],
            "entries ->",
            report["lua_output_path"],
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
