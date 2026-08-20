from __future__ import annotations

from collections import Counter
import copy
from dataclasses import dataclass
from datetime import datetime
import hashlib
from itertools import product
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any, Iterable

MODULE_V2_ROOT = Path(__file__).resolve().parents[2]
if str(MODULE_V2_ROOT) not in sys.path:
    sys.path.insert(0, str(MODULE_V2_ROOT))

from tools.build.dvf_3_3_generation_contract import (
    CANONICAL_INPUTS,
    GENERATOR_IMPLEMENTATION_FILES,
    derive_generation_id,
    generator_identity,
    media_type_for,
    output_universe_sha256,
)
from tools.build.compose_layer3_body_profile import (
    build_body_plan_sections,
)


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]

DATA_ROOT = V2_ROOT / "data" / "item_page_information_sufficiency"
DEFAULT_CONTRACT_PATH = DATA_ROOT / "assessment_contract.json"
DEFAULT_RATIFICATION_PATH = DATA_ROOT / "policy_ratification_contract.json"
DEFAULT_OUTPUT_ROOT = V2_ROOT / "output" / "item_page_information_sufficiency"

SCHEMA_VERSION = "iris-item-page-information-sufficiency-result-v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GENERATION_RE = re.compile(r'generation_id\s*=\s*"([a-z0-9-]+)"')
RATIFICATION_IDS = tuple(f"IPS-RAT-{index:02d}" for index in range(1, 11))
DISPOSITIONS = (
    "information_sufficient",
    "evidence_limited",
    "known_information_missing",
    "unresolved",
)
LAYER3_INPUT_IDENTITY_POLICY = {
    "json": "sha256_canonical_json_lf_v1",
    "jsonl": "sha256_canonical_jsonl_records_lf_v1",
    "generator_source": "sha256_utf8_lf_normalized_text_v1",
    "legacy_descriptor_bridge": "accept only when current UTF-8 content reproduces the descriptor raw hash by LF/CRLF conversion alone",
    "runtime_and_generated_outputs": "sha256_raw_bytes_v1",
    "semantic_content_mismatch": "fail_closed",
}

NON_BASELINE_FACT_FIELDS = (
    "primary_use",
    "secondary_use",
    "acquisition_hint",
    "processing_hint",
    "limitation_hint",
    "special_context",
)
FACT_FIELD_SOURCE = {field: f"facts.{field}" for field in NON_BASELINE_FACT_FIELDS}


@dataclass(frozen=True)
class AssessmentFailure(RuntimeError):
    domain: str
    code: str
    detail: str

    def __str__(self) -> str:
        return f"{self.domain}:{self.code}:{self.detail}"


def fail(domain: str, code: str, detail: str) -> None:
    raise AssessmentFailure(domain, code, detail)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("technical", "duplicate_json_key", key)
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_strict_object)
    except AssessmentFailure:
        raise
    except FileNotFoundError:
        fail("environment", "missing_input", portable(path))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("technical", "invalid_json", f"{portable(path)}:{type(exc).__name__}")


def load_jsonl(path: Path, identity_key: str) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        fail("environment", "missing_input", portable(path))
    except (OSError, UnicodeError) as exc:
        fail("environment", "unreadable_input", f"{portable(path)}:{type(exc).__name__}")
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line, object_pairs_hook=_strict_object)
        except (json.JSONDecodeError, AssessmentFailure) as exc:
            if isinstance(exc, AssessmentFailure):
                raise
            fail("technical", "invalid_jsonl", f"{portable(path)}:{line_number}")
        if not isinstance(row, dict) or not isinstance(row.get(identity_key), str):
            fail("technical", "invalid_jsonl_identity", f"{portable(path)}:{line_number}")
        identity = row[identity_key]
        if identity in rows:
            fail("technical", "duplicate_row_identity", f"{portable(path)}:{identity}")
        rows[identity] = row
    return rows


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def raw_hash(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
    except FileNotFoundError:
        fail("environment", "missing_input", portable(path))
    except OSError:
        fail("environment", "unreadable_input", portable(path))
    return digest.hexdigest()


def canonical_jsonl_hash(path: Path) -> str:
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        fail("environment", "missing_input", portable(path))
    except OSError:
        fail("environment", "unreadable_input", portable(path))
    return hashlib.sha256(
        _canonical_producer_content_bytes(data, ".jsonl")
    ).hexdigest()


def _lf_normalized_utf8_bytes(data: bytes) -> bytes:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        fail("technical", "producer_input_not_utf8_text", "canonical_input")
    normalized = text.replace("\r\n", "\n")
    if "\r" in normalized:
        fail("technical", "unsupported_lone_carriage_return", "canonical_input")
    return normalized.encode("utf-8")


def _canonical_producer_content_bytes(data: bytes, suffix: str) -> bytes:
    normalized = _lf_normalized_utf8_bytes(data)
    try:
        if suffix == ".json":
            value = json.loads(normalized.decode("utf-8"), object_pairs_hook=_strict_object)
            return canonical_bytes(value)
        if suffix == ".jsonl":
            rows = [
                json.loads(line, object_pairs_hook=_strict_object)
                for line in normalized.decode("utf-8").splitlines()
                if line.strip()
            ]
            return b"".join(canonical_bytes(row) for row in rows)
    except AssessmentFailure:
        raise
    except (UnicodeError, json.JSONDecodeError):
        fail("technical", "invalid_canonical_producer_input", suffix)
    fail("technical", "unsupported_canonical_input_media_type", suffix)


def _descriptor_text_identity_mode(data: bytes, record: dict[str, Any]) -> str | None:
    declared_sha = record.get("raw_byte_sha256")
    declared_size = record.get("size")
    lf_bytes = _lf_normalized_utf8_bytes(data)
    if hashlib.sha256(data).hexdigest() == declared_sha and len(data) == declared_size:
        return "raw_byte_exact"
    newline_variants = {lf_bytes, lf_bytes.replace(b"\n", b"\r\n")}
    if any(
        hashlib.sha256(candidate).hexdigest() == declared_sha
        and len(candidate) == declared_size
        for candidate in newline_variants
    ):
        return "utf8_newline_equivalent"
    return None


def portable(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def repo_path(value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        fail("technical", "invalid_repository_path", str(value))
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts:
        fail("technical", "repository_path_escape", value)
    path = REPO_ROOT.joinpath(*pure.parts)
    try:
        if not path.resolve().is_relative_to(REPO_ROOT.resolve()):
            fail("technical", "repository_path_escape", value)
    except OSError:
        fail("environment", "unresolvable_path", value)
    return path


def ensure_repository_path(path: Path, label: str) -> Path:
    try:
        resolved = path.resolve()
        if not resolved.is_relative_to(REPO_ROOT.resolve()):
            fail("technical", "path_outside_repository", label)
    except OSError:
        fail("environment", "unresolvable_path", label)
    return resolved


def identity(path: Path) -> dict[str, Any]:
    return {
        "path": portable(path),
        "raw_sha256": raw_hash(path),
        "size": path.stat().st_size,
    }


def producer_content_identity(path: Path) -> dict[str, Any]:
    try:
        data = path.read_bytes()
    except FileNotFoundError:
        fail("environment", "missing_input", portable(path))
    except OSError:
        fail("environment", "unreadable_input", portable(path))
    suffix = path.suffix.lower()
    algorithm = {
        ".json": "sha256_canonical_json_lf_v1",
        ".jsonl": "sha256_canonical_jsonl_records_lf_v1",
    }.get(suffix)
    if algorithm is None:
        fail("technical", "unsupported_canonical_input_media_type", portable(path))
    return {
        "path": portable(path),
        "identity_algorithm": algorithm,
        "sha256": hashlib.sha256(
            _canonical_producer_content_bytes(data, suffix)
        ).hexdigest(),
        "diagnostic_raw_sha256": hashlib.sha256(data).hexdigest(),
        "diagnostic_size": len(data),
    }


def _require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        fail("technical", "invalid_sha256", label)
    return value


def _verify_file_record(record: Any, label: str) -> Path:
    if not isinstance(record, dict) or set(record) != {"path", "canonical_json_sha256"}:
        fail("technical", "invalid_file_record", label)
    path = repo_path(record["path"])
    expected = _require_sha(record["canonical_json_sha256"], f"{label}.canonical_json_sha256")
    if canonical_hash(load_json(path)) != expected:
        fail("environment", "input_hash_mismatch", label)
    return path


def _generator_source_subject_map(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list) or len(value) != len(GENERATOR_IMPLEMENTATION_FILES):
        fail("policy", "generator_source_subject_set_mismatch", "generator_source_subjects")
    paths = [record.get("path") if isinstance(record, dict) else None for record in value]
    if paths != list(GENERATOR_IMPLEMENTATION_FILES) or len(paths) != len(set(paths)):
        fail("policy", "generator_source_subject_set_mismatch", "generator_source_subjects")
    result: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(value):
        if (
            not isinstance(record, dict)
            or set(record) != {"path", "identity_algorithm", "sha256"}
            or record.get("identity_algorithm")
            != "sha256_utf8_lf_normalized_text_v1"
        ):
            fail("policy", "generator_source_subject_invalid", str(index))
        _require_sha(record.get("sha256"), f"generator_source_subjects.{index}.sha256")
        result[record["path"]] = record
    return result


def ratification_record_projection(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "owner_identity": contract.get("owner_identity"),
        "decision_timestamp": contract.get("decision_timestamp"),
        "proposal_subject_sha256": contract.get("proposal_subject_sha256"),
        "ratifications": contract.get("ratifications"),
        "adopted_contract_subjects": contract.get("adopted_contract_subjects"),
    }


def adopted_contract_subject(value: dict[str, Any]) -> dict[str, Any]:
    subject = copy.deepcopy(value)
    subject.pop("ratification_record_identity", None)
    if subject.get("schema_version") == "item-page-information-sufficiency-contract-v1":
        records = subject.get("adopted_contracts", {})
        subject["adopted_contracts"] = {
            name: {"path": record.get("path")}
            for name, record in sorted(records.items())
            if isinstance(record, dict)
        }
    return subject


def validate_policy(
    assessment_contract: dict[str, Any],
    ratification_contract: dict[str, Any],
    *,
    require_ratified: bool,
) -> dict[str, Path]:
    if assessment_contract.get("schema_version") != "item-page-information-sufficiency-contract-v1":
        fail("technical", "assessment_contract_schema_mismatch", "assessment_contract")
    if ratification_contract.get("schema_version") != "item-page-information-sufficiency-ratification-v1":
        fail("technical", "ratification_contract_schema_mismatch", "ratification_contract")
    owner_identity = ratification_contract.get("owner_identity")
    if not isinstance(owner_identity, str) or not owner_identity.strip():
        fail("policy", "ratification_owner_identity_missing", "owner_identity")
    decision_timestamp = ratification_contract.get("decision_timestamp")
    if not isinstance(decision_timestamp, str):
        fail("policy", "ratification_timestamp_invalid", "decision_timestamp")
    try:
        parsed_timestamp = datetime.fromisoformat(decision_timestamp)
    except ValueError:
        fail("policy", "ratification_timestamp_invalid", "decision_timestamp")
    if parsed_timestamp.tzinfo is None or parsed_timestamp.utcoffset() is None:
        fail("policy", "ratification_timestamp_timezone_missing", "decision_timestamp")
    if require_ratified and ratification_contract.get("ratification_state") != "ratified":
        fail("policy", "policy_not_ratified", "ratification_state")
    proposal_sha = _require_sha(
        ratification_contract.get("proposal_subject_sha256"), "proposal_subject_sha256"
    )
    if ratification_contract.get("proposal_subject_hash_algorithm") != "sha256_canonical_json_lf_v1":
        fail("policy", "proposal_subject_hash_algorithm_mismatch", "proposal_subject")
    proposal_path = repo_path(ratification_contract.get("proposal_path", ""))
    if canonical_hash(load_json(proposal_path)) != proposal_sha:
        fail("policy", "proposal_subject_hash_mismatch", portable(proposal_path))
    rows = ratification_contract.get("ratifications")
    if not isinstance(rows, list):
        fail("policy", "ratification_list_missing", "ratifications")
    if any(not isinstance(row, dict) for row in rows):
        fail("policy", "ratification_row_invalid", "ratifications")
    ids = [row.get("id") for row in rows]
    if tuple(ids) != RATIFICATION_IDS or any(row.get("decision") != "ratified" for row in rows):
        fail("policy", "ratification_incomplete", ",".join(map(str, ids)))
    record_identity = canonical_hash(ratification_record_projection(ratification_contract))
    if ratification_contract.get("ratification_record_identity") != record_identity:
        fail("policy", "ratification_record_identity_mismatch", "ratification_contract")
    if assessment_contract.get("ratification_state") != "ratified":
        fail("policy", "proposal_contract_forbidden", "assessment_contract")
    if assessment_contract.get("layer3_input_identity_policy") != LAYER3_INPUT_IDENTITY_POLICY:
        fail("policy", "layer3_input_identity_policy_mismatch", "assessment_contract")
    _generator_source_subject_map(
        assessment_contract.get("layer3_generator_source_subjects")
    )
    if assessment_contract.get("proposal_subject_sha256") != proposal_sha:
        fail("policy", "adopted_proposal_binding_mismatch", "assessment_contract")
    if assessment_contract.get("ratification_record_identity") != record_identity:
        fail("policy", "adopted_ratification_binding_mismatch", "assessment_contract")
    records = ratification_contract.get("adopted_contracts")
    if not isinstance(records, dict) or set(records) != {
        "assessment_contract",
        "baseline_field_registry",
        "layer3_state_derivation_contract",
        "layer4_state_derivation_contract",
    }:
        fail("policy", "adopted_contract_set_mismatch", "adopted_contracts")
    paths = {name: _verify_file_record(record, name) for name, record in records.items()}
    declared_subjects = ratification_contract.get("adopted_contract_subjects")
    if not isinstance(declared_subjects, dict) or set(declared_subjects) != set(paths):
        fail("policy", "adopted_contract_subject_set_mismatch", "adopted_contract_subjects")
    for name, path in paths.items():
        observed_subject_sha = canonical_hash(adopted_contract_subject(load_json(path)))
        if declared_subjects.get(name) != observed_subject_sha:
            fail("policy", "adopted_contract_subject_mismatch", name)
    declared_assessment_path = paths["assessment_contract"].resolve()
    if declared_assessment_path != repo_path(assessment_contract["contract_path"]).resolve():
        fail("policy", "assessment_contract_path_mismatch", portable(declared_assessment_path))
    for key in (
        "baseline_field_registry",
        "layer3_state_derivation_contract",
        "layer4_state_derivation_contract",
    ):
        declared = assessment_contract.get("adopted_contracts", {}).get(key)
        if declared != records[key]:
            fail("policy", "assessment_contract_hash_binding_mismatch", key)
    return paths


def _load_denominator(path: Path) -> dict[str, dict[str, Any]]:
    value = load_json(path)
    if not isinstance(value, dict):
        fail("technical", "denominator_not_object", portable(path))
    for fulltype, row in value.items():
        if not isinstance(fulltype, str) or not isinstance(row, dict):
            fail("technical", "invalid_denominator_row", str(fulltype))
        if row.get("FullType") != fulltype:
            fail("technical", "denominator_identity_mismatch", fulltype)
    return value


def _sorted_key_hash(keys: Iterable[str]) -> str:
    return hashlib.sha256(("\n".join(sorted(keys)) + "\n").encode("utf-8")).hexdigest()


def _field_types(values: list[Any]) -> list[str]:
    result = set()
    for value in values:
        if value is None:
            result.add("null")
        elif isinstance(value, bool):
            result.add("boolean")
        elif isinstance(value, int):
            result.add("integer")
        elif isinstance(value, float):
            result.add("number")
        elif isinstance(value, str):
            result.add("string")
        else:
            result.add(type(value).__name__)
    return sorted(result)


def validate_baseline_registry(
    registry: dict[str, Any], denominator: dict[str, dict[str, Any]]
) -> None:
    if registry.get("schema_version") != "item-page-baseline-field-registry-v1":
        fail("policy", "baseline_registry_schema_mismatch", "baseline_field_registry")
    if registry.get("ratification_state") != "ratified":
        fail("policy", "baseline_registry_not_ratified", "baseline_field_registry")
    fields = registry.get("fields")
    if not isinstance(fields, list) or not fields:
        fail("policy", "baseline_registry_empty", "fields")
    universe = {field for row in denominator.values() for field in row}
    for entry in fields:
        if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
            fail("policy", "invalid_baseline_field", "fields")
        name = entry["name"]
        if name not in universe:
            fail("policy", "baseline_field_not_in_itemscript", name)
        actual = _field_types([row[name] for row in denominator.values() if name in row])
        if actual != entry.get("observed_types"):
            fail("environment", "baseline_field_type_drift", name)
    if registry.get("lower_bound_bias", {}).get("direction") != "information_sufficient":
        fail("policy", "baseline_bias_direction_missing", "lower_bound_bias")


def _parse_current_generation(pointer_path: Path) -> str:
    try:
        text = pointer_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        fail("environment", "pointer_unreadable", portable(pointer_path))
    matches = GENERATION_RE.findall(text)
    if len(matches) != 1:
        fail("technical", "ambiguous_generation_pointer", portable(pointer_path))
    return matches[0]


def _installed_generation_output_identity(
    pointer_path: Path, generation_root: Path, generation_id: str
) -> list[dict[str, Any]]:
    generation_prefix = f"runtime/IrisLayer3Generations/{generation_id}/"
    installed_outputs: list[tuple[str, Path]] = [
        ("runtime/IrisLayer3DataCurrent.lua", pointer_path)
    ]
    for installed in sorted(generation_root.rglob("*")):
        if not installed.is_file() or installed.name == "generation_descriptor.json":
            continue
        relative = installed.relative_to(generation_root).as_posix()
        if relative == "dvf_3_3_rendered.json":
            logical_path = relative
        elif relative == "IrisLayer3DataChunkIndex.lua":
            logical_path = "runtime/IrisLayer3DataChunkIndex.lua"
        elif relative.startswith("Chunks/") and relative.endswith(".lua"):
            logical_path = generation_prefix + relative
        else:
            fail("technical", "unknown_installed_generation_output", relative)
        installed_outputs.append((logical_path, installed))
    return [
        {
            "path": logical_path,
            "media_type": media_type_for(path.name),
            "raw_byte_sha256": raw_hash(path),
            "size": path.stat().st_size,
        }
        for logical_path, path in sorted(installed_outputs)
    ]


def _validate_generation(
    pointer_path: Path,
    generator_source_subjects: Any = None,
) -> tuple[
    str,
    Path,
    dict[str, Any],
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    generation_id = _parse_current_generation(pointer_path)
    generation_root = pointer_path.parent / "IrisLayer3Generations" / generation_id
    descriptor_path = generation_root / "generation_descriptor.json"
    descriptor = load_json(descriptor_path)
    if descriptor.get("generation_id") != generation_id:
        fail("environment", "generation_descriptor_pointer_mismatch", generation_id)
    inputs = descriptor.get("canonical_inputs")
    if not isinstance(inputs, list) or len(inputs) != 7:
        fail("environment", "generation_canonical_input_count_mismatch", generation_id)
    declared_paths = [
        record.get("path") if isinstance(record, dict) else None for record in inputs
    ]
    if declared_paths != list(CANONICAL_INPUTS):
        fail("environment", "generation_input_path_set_mismatch", generation_id)
    input_validation = []
    for index, record in enumerate(inputs):
        legacy_fields = {"path", "raw_byte_sha256", "size"}
        canonical_fields = legacy_fields | {
            "content_identity_algorithm",
            "canonical_content_sha256",
        }
        if (
            not isinstance(record, dict)
            or frozenset(record) not in {
                frozenset(legacy_fields),
                frozenset(canonical_fields),
            }
            or not isinstance(record.get("size"), int)
            or not SHA256_RE.fullmatch(str(record.get("raw_byte_sha256", "")))
        ):
            fail("technical", "invalid_generation_input_record", str(index))
        path = repo_path(record["path"])
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            fail("environment", "missing_input", portable(path))
        except OSError:
            fail("environment", "unreadable_input", portable(path))
        if path.suffix.lower() not in {".json", ".jsonl"}:
            fail("technical", "unsupported_canonical_input_media_type", portable(path))
        canonical_content_sha256 = hashlib.sha256(
            _canonical_producer_content_bytes(data, path.suffix.lower())
        ).hexdigest()
        algorithm = record.get("content_identity_algorithm")
        if algorithm is not None:
            expected_algorithm = {
                ".json": "sha256_canonical_json_lf_v1",
                ".jsonl": "sha256_canonical_jsonl_records_lf_v1",
            }[path.suffix.lower()]
            if (
                algorithm != expected_algorithm
                or record.get("canonical_content_sha256") != canonical_content_sha256
            ):
                fail("environment", "generation_input_content_mismatch", portable(path))
            mode = "canonical_content_exact"
        else:
            mode = _descriptor_text_identity_mode(data, record)
        if mode is None:
            fail("environment", "generation_input_content_mismatch", portable(path))
        input_validation.append(
            {
                "path": record["path"],
                "descriptor_raw_byte_sha256": record["raw_byte_sha256"],
                "current_raw_byte_sha256": hashlib.sha256(data).hexdigest(),
                "canonical_content_sha256": canonical_content_sha256,
                "validation_mode": mode,
            }
        )
    generator = descriptor.get("generator")
    if generator_source_subjects is None:
        generator_source_subjects = load_json(DEFAULT_CONTRACT_PATH).get(
            "layer3_generator_source_subjects"
        )
    generator_source_subject_map = _generator_source_subject_map(
        generator_source_subjects
    )
    expected_generator = generator_identity(REPO_ROOT)
    if not isinstance(generator, dict) or any(
        generator.get(key) != expected_generator.get(key)
        for key in ("contract_version", "serializer", "chunking")
    ):
        fail("environment", "generation_generator_identity_mismatch", generation_id)
    implementation_files = generator.get("implementation_files")
    if not isinstance(implementation_files, list) or [
        record.get("path") if isinstance(record, dict) else None
        for record in implementation_files
    ] != list(GENERATOR_IMPLEMENTATION_FILES):
        fail("environment", "generation_generator_path_set_mismatch", generation_id)
    generator_source_validation = []
    for index, record in enumerate(implementation_files):
        if (
            not isinstance(record, dict)
            or set(record) != {"path", "raw_byte_sha256", "size"}
            or not isinstance(record.get("size"), int)
            or not SHA256_RE.fullmatch(str(record.get("raw_byte_sha256", "")))
        ):
            fail("technical", "invalid_generator_implementation_record", str(index))
        path = repo_path(record["path"])
        try:
            data = path.read_bytes()
        except FileNotFoundError:
            fail("environment", "missing_input", portable(path))
        except OSError:
            fail("environment", "unreadable_input", portable(path))
        mode = _descriptor_text_identity_mode(data, record)
        lf_normalized_source_sha256 = hashlib.sha256(
            _lf_normalized_utf8_bytes(data)
        ).hexdigest()
        ratified_source = generator_source_subject_map[record["path"]]
        if lf_normalized_source_sha256 != ratified_source["sha256"]:
            fail("environment", "generation_generator_content_mismatch", portable(path))
        validation_mode = mode or "ratified_lf_normalized_source_exact"
        generator_source_validation.append(
            {
                "path": record["path"],
                "descriptor_raw_byte_sha256": record["raw_byte_sha256"],
                "current_raw_byte_sha256": hashlib.sha256(data).hexdigest(),
                "lf_normalized_source_sha256": lf_normalized_source_sha256,
                "ratified_identity_algorithm": ratified_source["identity_algorithm"],
                "descriptor_legacy_compatibility_mode": mode,
                "validation_mode": validation_mode,
            }
        )
    expected_generation_id = derive_generation_id(inputs, generator)
    if generation_id != expected_generation_id:
        fail("environment", "content_derived_generation_id_mismatch", generation_id)
    outputs = descriptor.get("outputs")
    if not isinstance(outputs, list) or output_universe_sha256(outputs) != descriptor.get("output_universe_sha256"):
        fail("environment", "generation_output_universe_identity_mismatch", generation_id)
    expected_outputs = _installed_generation_output_identity(
        pointer_path, generation_root, generation_id
    )
    if outputs != expected_outputs:
        fail("environment", "generation_output_identity_mismatch", generation_id)
    rendered_path = generation_root / "dvf_3_3_rendered.json"
    rendered = load_json(rendered_path)
    entries = rendered.get("entries")
    if not isinstance(entries, dict):
        fail("technical", "rendered_entries_missing", portable(rendered_path))
    if rendered.get("meta", {}).get("stats", {}).get("total") != len(entries):
        fail("environment", "rendered_row_count_mismatch", portable(rendered_path))
    return (
        generation_id,
        generation_root,
        descriptor,
        rendered,
        input_validation,
        generator_source_validation,
    )


def _positive_layer4_rows(fulltype: str, value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, dict) or not isinstance(value.get("use_cases"), list):
        fail("technical", "malformed_layer4_use_case_set", fulltype)
    result = []
    seen_ids: set[str] = set()
    for index, row in enumerate(value["use_cases"]):
        if not isinstance(row, dict):
            fail("technical", "malformed_layer4_use_case_row", f"{fulltype}:{index}")
        use_case_id = row.get("use_case_id")
        if not isinstance(use_case_id, str) or not use_case_id:
            fail("technical", "missing_layer4_use_case_id", f"{fulltype}:{index}")
        if use_case_id in seen_ids:
            fail("technical", "duplicate_layer4_use_case_id", f"{fulltype}:{use_case_id}")
        seen_ids.add(use_case_id)
        if row.get("line_kind") not in {"evidence", "exclusion"}:
            fail("technical", "unsupported_layer4_line_kind", f"{fulltype}:{use_case_id}")
        sources = row.get("evidence_sources")
        if not isinstance(sources, list):
            fail("technical", "malformed_layer4_evidence_sources", f"{fulltype}:{use_case_id}")
        for source_index, source in enumerate(sources):
            if (
                not isinstance(source, dict)
                or not isinstance(source.get("decision"), str)
                or not isinstance(source.get("source_type"), str)
            ):
                fail(
                    "technical",
                    "malformed_layer4_evidence_source",
                    f"{fulltype}:{use_case_id}:{source_index}",
                )
            if source["source_type"] not in {"recipe_evidence", "rightclick"}:
                fail(
                    "technical",
                    "unsupported_layer4_evidence_source_type",
                    f"{fulltype}:{use_case_id}:{source['source_type']}",
                )
            if source["decision"] not in {"PASS", "NO"}:
                fail(
                    "technical",
                    "unsupported_layer4_evidence_decision",
                    f"{fulltype}:{use_case_id}:{source['decision']}",
                )
        if row["line_kind"] == "evidence" and any(
            source["decision"] == "PASS" for source in sources
        ):
            result.append(row)
    return result


def _displayed_layer4_ids(fulltype: str, description: Any) -> tuple[set[str], set[str]]:
    if description is None:
        return set(), set()
    if not isinstance(description, dict):
        fail("technical", "malformed_layer4_description", fulltype)
    block = description.get("use_case_block")
    if block is None:
        return set(), set()
    if not isinstance(block, dict) or not isinstance(block.get("items"), list):
        fail("technical", "malformed_layer4_use_case_block", fulltype)
    displayed: set[str] = set()
    positive: set[str] = set()
    seen_ids: set[str] = set()
    for index, row in enumerate(block["items"]):
        if not isinstance(row, dict):
            fail("technical", "malformed_layer4_display_row", f"{fulltype}:{index}")
        use_case_id = row.get("use_case_id")
        if not isinstance(use_case_id, str) or not use_case_id:
            fail("technical", "missing_layer4_display_id", f"{fulltype}:{index}")
        if use_case_id in seen_ids:
            fail("technical", "duplicate_layer4_display_id", f"{fulltype}:{use_case_id}")
        seen_ids.add(use_case_id)
        line_kind = row.get("line_kind")
        if line_kind not in {"evidence", "exclusion"}:
            fail("technical", "malformed_layer4_display_line_kind", f"{fulltype}:{use_case_id}")
        displayed.add(use_case_id)
        if line_kind == "evidence":
            positive.add(use_case_id)
    return displayed, positive


def _layer3_state(
    fulltype: str,
    fact: dict[str, Any] | None,
    decision: dict[str, Any] | None,
    rendered: dict[str, Any] | None,
    input_hashes: dict[str, str],
    producer_emitted_sections: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    propositions = [
        {
            "field": field,
            "value": fact.get(field),
            "required_source_field": FACT_FIELD_SOURCE[field],
        }
        for field in NON_BASELINE_FACT_FIELDS
        if fact is not None and fact.get(field) not in (None, "", [], {})
    ]
    text = rendered.get("text_ko") if isinstance(rendered, dict) else None
    text_present = isinstance(text, str) and bool(text.strip())
    body_plan = rendered.get("body_plan", {}) if isinstance(rendered, dict) else {}
    emitted_sections = set(body_plan.get("emitted_section_names", [])) if isinstance(body_plan, dict) else set()
    emitted_source_fields: set[str] = set()
    if producer_emitted_sections is not None:
        if any(
            not isinstance(section, dict)
            or not isinstance(section.get("section"), str)
            or not isinstance(section.get("source_fields"), list)
            or not isinstance(section.get("slots"), list)
            for section in producer_emitted_sections
        ):
            fail("technical", "malformed_layer3_emitted_section", fulltype)
        producer_names = [section["section"] for section in producer_emitted_sections]
        if len(producer_names) != len(set(producer_names)):
            fail("technical", "duplicate_layer3_emitted_section_name", fulltype)
        declared_section_names = (
            body_plan.get("emitted_section_names", [])
            if isinstance(body_plan, dict)
            else []
        )
        if producer_names != declared_section_names:
            fail("environment", "layer3_body_plan_identity_mismatch", fulltype)
        for section in producer_emitted_sections:
            for source_field in section["source_fields"]:
                if not isinstance(source_field, str):
                    fail("technical", "malformed_layer3_source_field", fulltype)
                emitted_source_fields.add(source_field)
    else:
        if (
            "use_core" in emitted_sections
            and fact is not None
            and fact.get("primary_use") not in (None, "")
        ):
            emitted_source_fields.add("facts.primary_use")
        if (
            "acquisition_support" in emitted_sections
            and fact is not None
            and fact.get("acquisition_hint") not in (None, "")
        ):
            emitted_source_fields.add("facts.acquisition_hint")
        if "limitation_tail" in emitted_sections and fact is not None:
            for field in ("limitation_hint", "processing_hint", "special_context"):
                if fact.get(field) not in (None, ""):
                    emitted_source_fields.add(f"facts.{field}")
                    break
    represented_fields = sorted(
        proposition["field"]
        for proposition in propositions
        if proposition["required_source_field"] in emitted_source_fields
    )
    all_propositions_bound = bool(propositions) and len(represented_fields) == len(propositions)
    sealed_row_absence = fact is None and decision is None and rendered is None
    if not sealed_row_absence and (
        fact is None or decision is None or decision.get("state") not in {"adopted"}
    ):
        availability = "unresolved"
        requiredness = "unresolved"
        representation = "unresolved"
        reason = "producer_decision_not_adopted"
    elif propositions:
        availability = "approved_fact_present"
        requiredness = "required"
        representation = "represented" if text_present and all_propositions_bound else "missing"
        reason = "approved_nonbaseline_proposition_in_sealed_set"
    else:
        availability = "approved_fact_set_empty"
        requiredness = "not_required"
        representation = "represented" if text_present else "missing"
        reason = "no_approved_nonbaseline_proposition_in_sealed_set"
    if availability == "unresolved":
        contribution = "unresolved"
    elif text_present and all_propositions_bound:
        contribution = "self_sufficient"
    elif text_present and represented_fields:
        contribution = "supporting_context"
    elif text_present:
        contribution = "identity_only"
    else:
        contribution = "absent"
    return {
        "artifact_set_materialization": "sealed_complete",
        "fact_availability": availability,
        "contribution": contribution,
        "requiredness": requiredness,
        "representation": representation,
        "approved_nonbaseline_propositions": propositions,
        "represented_proposition_fields": represented_fields,
        "emitted_section_names": sorted(emitted_sections),
        "emitted_source_fields": sorted(emitted_source_fields),
        "provenance": {
            "facts_sha256": input_hashes["layer3_facts"],
            "decisions_sha256": input_hashes["layer3_decisions"],
            "overlay_sha256": input_hashes.get("layer3_overlay"),
            "profiles_sha256": input_hashes.get("layer3_profiles"),
            "rendered_sha256": input_hashes["layer3_rendered"],
            "facts_ref": fact.get("item_id") if fact else None,
            "decision_state": decision.get("state") if decision else None,
        },
        "reasons": [reason, "layer2_primary_subcategory_excluded_from_positive_contribution"],
    }


def _layer4_state(
    fulltype: str,
    usecase: dict[str, Any] | None,
    description: dict[str, Any] | None,
    input_hashes: dict[str, str],
) -> dict[str, Any]:
    positive = _positive_layer4_rows(fulltype, usecase)
    approved_ids = sorted(row["use_case_id"] for row in positive)
    displayed_ids, displayed_positive_ids = _displayed_layer4_ids(fulltype, description)
    declared_rows = {
        row["use_case_id"]: row
        for row in usecase["use_cases"]
    } if isinstance(usecase, dict) else {}
    unknown_displayed = displayed_ids - set(declared_rows)
    if unknown_displayed:
        return {
            "artifact_set_materialization": "sealed_complete",
            "fact_availability": "unresolved",
            "applicability": "unresolved",
            "representation": "unresolved",
            "scope_limitation": "none",
            "approved_use_case_ids": approved_ids,
            "represented_use_case_ids": sorted(set(approved_ids) & displayed_positive_ids),
            "provenance": {
                "usecases_sha256": input_hashes["layer4_usecases"],
                "descriptions_sha256": input_hashes["layer4_descriptions"],
            },
            "reasons": [
                "public_use_case_without_exact_fulltype_source_binding",
                f"unbound_use_case_id:{sorted(unknown_displayed)[0]}",
                "recipe_and_rightclick_are_independent_equal_sources",
            ],
        }
    unapproved_positive = {
        use_case_id
        for use_case_id in displayed_positive_ids
        if declared_rows[use_case_id].get("line_kind") == "evidence"
        and use_case_id not in approved_ids
    }
    if unapproved_positive:
        return {
            "artifact_set_materialization": "sealed_complete",
            "fact_availability": "unresolved",
            "applicability": "unresolved",
            "representation": "unresolved",
            "scope_limitation": "none",
            "approved_use_case_ids": approved_ids,
            "represented_use_case_ids": sorted(set(approved_ids) & displayed_positive_ids),
            "provenance": {
                "usecases_sha256": input_hashes["layer4_usecases"],
                "descriptions_sha256": input_hashes["layer4_descriptions"],
            },
            "reasons": [
                "public_positive_without_approved_pass_binding",
                f"unapproved_use_case_id:{sorted(unapproved_positive)[0]}",
                "recipe_and_rightclick_are_independent_equal_sources",
            ],
        }
    represented_ids = sorted(set(approved_ids) & displayed_positive_ids)
    if approved_ids:
        availability = "approved_fact_present"
        applicability = "applicable"
        representation = "represented" if set(approved_ids) <= displayed_positive_ids else "missing"
        scope = "none"
        reason = "approved_pass_use_case_bound_to_public_representation" if representation == "represented" else "under_rendered"
    else:
        availability = "approved_fact_set_empty"
        applicability = "unresolved"
        representation = "missing"
        scope = "blocked_by_negative_authority"
        reason = "no_pass_fact_in_sealed_declared_set"
    return {
        "artifact_set_materialization": "sealed_complete",
        "fact_availability": availability,
        "applicability": applicability,
        "representation": representation,
        "scope_limitation": scope,
        "approved_use_case_ids": approved_ids,
        "represented_use_case_ids": represented_ids,
        "provenance": {
            "usecases_sha256": input_hashes["layer4_usecases"],
            "descriptions_sha256": input_hashes["layer4_descriptions"],
        },
        "reasons": [reason, "recipe_and_rightclick_are_independent_equal_sources"],
    }


def decide_disposition(layer3: dict[str, Any], layer4: dict[str, Any]) -> tuple[str, str, list[str]]:
    incoherent_reasons = state_vector_incoherence(layer3, layer4)
    if incoherent_reasons:
        return "unresolved", "IPS-PREC-05", ["incoherent_state_vector", *incoherent_reasons]
    l3_missing = layer3["requiredness"] == "required" and layer3["representation"] == "missing"
    l4_missing = layer4["applicability"] == "applicable" and layer4["representation"] == "missing"
    if l3_missing or l4_missing:
        reasons = []
        if l3_missing:
            reasons.append("required_layer3_confirmed_fact_not_represented")
        if l4_missing:
            reasons.append("applicable_layer4_confirmed_fact_not_represented")
        return "known_information_missing", "IPS-PREC-01", reasons
    l3_unresolved = any(
        layer3[key] == "unresolved"
        for key in ("fact_availability", "requiredness", "representation")
    )
    blocked_tuple = (
        layer4["artifact_set_materialization"] == "sealed_complete"
        and layer4["fact_availability"] == "approved_fact_set_empty"
        and layer4["applicability"] == "unresolved"
        and layer4["representation"] == "missing"
        and layer4["scope_limitation"] == "blocked_by_negative_authority"
    )
    l4_unresolved = (
        layer4["fact_availability"] == "unresolved"
        or layer4["representation"] == "unresolved"
        or (layer4["applicability"] == "unresolved" and not blocked_tuple)
    )
    if l3_unresolved or l4_unresolved:
        return "unresolved", "IPS-PREC-02", ["material_assessment_axis_unresolved"]
    represented_nonbaseline = (
        layer3["fact_availability"] == "approved_fact_present"
        and layer3["representation"] == "represented"
    ) or (
        layer4["fact_availability"] == "approved_fact_present"
        and layer4["representation"] == "represented"
    )
    if represented_nonbaseline:
        reasons = ["confirmed_nonbaseline_fact_represented"]
        if blocked_tuple:
            reasons.append("layer4_negative_authority_scope_limitation_preserved")
        return "information_sufficient", "IPS-PREC-03", reasons
    if (
        layer3["artifact_set_materialization"] == "sealed_complete"
        and layer4["artifact_set_materialization"] == "sealed_complete"
        and layer3["fact_availability"] == "approved_fact_set_empty"
        and layer4["fact_availability"] == "approved_fact_set_empty"
        and layer3["requiredness"] in {"optional", "not_required"}
        and not represented_nonbaseline
    ):
        return "evidence_limited", "IPS-PREC-04", [
            "both_declared_artifact_sets_empty_for_fulltype",
            "no_world_level_negative_claim",
        ]
    return "unresolved", "IPS-PREC-05", ["unmatched_state_vector_fail_closed"]


def state_vector_incoherence(layer3: dict[str, Any], layer4: dict[str, Any]) -> list[str]:
    reasons = []
    if layer3.get("artifact_set_materialization") != "sealed_complete":
        reasons.append("layer3_artifact_set_not_sealed_complete")
    l3_tuple = (
        layer3.get("fact_availability"),
        layer3.get("contribution"),
        layer3.get("requiredness"),
        layer3.get("representation"),
    )
    l3_coherent = (
        l3_tuple[0] == "approved_fact_present"
        and l3_tuple[2] in {"required", "optional"}
        and (
            (l3_tuple[3] == "represented" and l3_tuple[1] == "self_sufficient")
            or (
                l3_tuple[3] == "missing"
                and l3_tuple[1] in {"supporting_context", "identity_only", "absent"}
            )
        )
    ) or (
        l3_tuple[0] == "approved_fact_set_empty"
        and l3_tuple[2] in {"not_required", "optional"}
        and (
            (l3_tuple[3] == "represented" and l3_tuple[1] == "identity_only")
            or (l3_tuple[3] == "missing" and l3_tuple[1] == "absent")
        )
    ) or l3_tuple == ("unresolved", "unresolved", "unresolved", "unresolved")
    if not l3_coherent:
        reasons.append("layer3_axis_tuple_incoherent")
    if layer4.get("artifact_set_materialization") != "sealed_complete":
        reasons.append("layer4_artifact_set_not_sealed_complete")
    l4_tuple = (
        layer4.get("fact_availability"),
        layer4.get("applicability"),
        layer4.get("representation"),
        layer4.get("scope_limitation"),
    )
    l4_coherent = (
        l4_tuple[0] == "approved_fact_present"
        and l4_tuple[1] == "applicable"
        and l4_tuple[2] in {"represented", "missing"}
        and l4_tuple[3] == "none"
    ) or l4_tuple == (
        "approved_fact_set_empty",
        "unresolved",
        "missing",
        "blocked_by_negative_authority",
    ) or l4_tuple == ("unresolved", "unresolved", "unresolved", "none")
    if not l4_coherent:
        reasons.append("layer4_axis_tuple_incoherent")
    return reasons


def matrix_totality_check(layer3_contract: dict[str, Any], layer4_contract: dict[str, Any]) -> bool:
    l3_axes = layer3_contract.get("axes", {})
    l4_axes = layer4_contract.get("axes", {})
    required_axes = (
        l3_axes.get("fact_availability"),
        l3_axes.get("contribution"),
        l3_axes.get("requiredness"),
        l3_axes.get("representation"),
        l4_axes.get("fact_availability"),
        l4_axes.get("applicability"),
        l4_axes.get("representation"),
        l4_axes.get("scope_limitation"),
    )
    if any(not isinstance(axis, list) or not axis for axis in required_axes):
        return False
    reached_rules: set[str] = set()
    for values in product(*required_axes):
        layer3 = {
            "artifact_set_materialization": "sealed_complete",
            "fact_availability": values[0],
            "contribution": values[1],
            "requiredness": values[2],
            "representation": values[3],
        }
        layer4 = {
            "artifact_set_materialization": "sealed_complete",
            "fact_availability": values[4],
            "applicability": values[5],
            "representation": values[6],
            "scope_limitation": values[7],
        }
        first = decide_disposition(layer3, layer4)
        second = decide_disposition(copy.deepcopy(layer3), copy.deepcopy(layer4))
        if first != second or first[0] not in DISPOSITIONS or first[1] not in {
            "IPS-PREC-01", "IPS-PREC-02", "IPS-PREC-03", "IPS-PREC-04", "IPS-PREC-05"
        }:
            return False
        reached_rules.add(first[1])
        if state_vector_incoherence(layer3, layer4):
            expected = ("unresolved", "IPS-PREC-05")
        elif (
            layer3["requiredness"] == "required"
            and layer3["representation"] == "missing"
        ) or (
            layer4["applicability"] == "applicable"
            and layer4["representation"] == "missing"
        ):
            expected = ("known_information_missing", "IPS-PREC-01")
        elif layer3["fact_availability"] == "unresolved" or layer4[
            "fact_availability"
        ] == "unresolved":
            expected = ("unresolved", "IPS-PREC-02")
        elif (
            layer3["fact_availability"] == "approved_fact_present"
            and layer3["representation"] == "represented"
        ) or (
            layer4["fact_availability"] == "approved_fact_present"
            and layer4["representation"] == "represented"
        ):
            expected = ("information_sufficient", "IPS-PREC-03")
        elif (
            layer3["fact_availability"] == "approved_fact_set_empty"
            and layer4["fact_availability"] == "approved_fact_set_empty"
            and layer3["requiredness"] in {"optional", "not_required"}
        ):
            expected = ("evidence_limited", "IPS-PREC-04")
        else:
            expected = ("unresolved", "IPS-PREC-05")
        if first[:2] != expected:
            return False
    return reached_rules == {f"IPS-PREC-{index:02d}" for index in range(1, 6)}


def _scalar_tokens(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        for nested in value.values():
            yield from _scalar_tokens(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _scalar_tokens(nested)
    else:
        yield value


def _protected_surface(generation_root: Path, descriptor: dict[str, Any]) -> list[Path]:
    paths: set[Path] = set()
    for record in descriptor.get("canonical_inputs", []):
        path = repo_path(record["path"])
        if not path.is_file():
            fail("environment", "protected_surface_input_missing", portable(path))
        paths.add(path)
    generator = descriptor.get("generator")
    implementation_files = generator.get("implementation_files") if isinstance(generator, dict) else None
    if not isinstance(implementation_files, list) or not implementation_files:
        fail("environment", "protected_generator_source_set_missing", "generator")
    for record in implementation_files:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            fail("technical", "protected_generator_source_record_invalid", "generator")
        path = repo_path(record["path"])
        if not path.is_file():
            fail("environment", "protected_generator_source_missing", portable(path))
        paths.add(path)
    explicit = [
        "Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua",
        "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua",
        "Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua",
        "Iris/media/lua/client/Iris/Data/layer3_renderer.lua",
        "Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptions.lua",
        "Iris/media/lua/client/Iris/Data/IrisUseCaseDescriptionsLookup.lua",
        "Iris/media/lua/client/Iris/Data/IrisUseCaseLabelMap.lua",
        "Iris/build/description/v2/data/upstream_usecases_by_fulltype.json",
        "Iris/output/descriptions_by_fulltype.v2.4.json",
        "Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua",
        "Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua",
        "Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua",
        "Iris/media/lua/client/Iris/UI/Tooltip/IrisTooltipSummary.lua",
        "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserItemIndex.lua",
    ]
    for value in explicit:
        path = repo_path(value)
        if not path.is_file():
            fail("environment", "protected_surface_explicit_file_missing", value)
        paths.add(path)
    if not generation_root.is_dir():
        fail("environment", "protected_generation_root_missing", portable(generation_root))
    paths.update(path for path in generation_root.rglob("*") if path.is_file())
    return sorted(paths, key=portable)


def _terminology_mapping() -> dict[str, Any]:
    rows = [
        ("설명", "Layer 3 body", "confirmed descriptive context", "none", "keep"),
        ("개요", "Layer 1 identity and core facts", "baseline summary", "none", "keep"),
        ("활용", "Layer 4 use_case", "Recipe and Right-click use", "none", "keep"),
        ("관련 제작", "Layer 4 Recipe navigation", "recipe connection", "none", "keep"),
        ("제작", "Layer 4 Recipe source", "recipe interaction", "none", "keep"),
        ("상호작용", "Layer 4 Right-click source", "context-menu interaction", "none", "keep"),
        ("요구 조건", "Layer 4 requirement", "use-case requirements", "possible breadth ambiguity", "defer"),
    ]
    return {
        "schema_version": "item-page-terminology-responsibility-mapping-v1",
        "runtime_mutation": False,
        "menu_surface": "detailed",
        "tooltip_surface": "same-confirmed-facts-maximum-four-lines",
        "entries": [
            {
                "heading": heading,
                "actual_layer_responsibility": responsibility,
                "implied_scope": scope,
                "mismatch_type": mismatch,
                "disposition": disposition,
            }
            for heading, responsibility, scope, mismatch, disposition in rows
        ],
    }


def _runtime_drift_report() -> dict[str, Any]:
    return {
        "schema_version": "item-page-baseline-runtime-drift-report-v1",
        "baseline_authority": "items_itemscript_explicit_registry_lower_bound",
        "consumer_cross_check_only": True,
        "bias_direction": "information_sufficient",
        "drift_fields": [
            {"field": "minDamage/maxDamage/conditionMax/minRange/maxRange/criticalChance", "observable_source": "runtime item weapon methods", "affected_family": "weapon"},
            {"field": "boredomChange/calories", "observable_source": "runtime item food methods", "affected_family": "food"},
            {"field": "numberOfPages/lvlSkillTrained/numLevelsTrained", "observable_source": "runtime item literature methods", "affected_family": "literature"},
            {"field": "capacity/waterproof/insulation", "observable_source": "runtime item moveable methods", "affected_family": "moveable"},
        ],
        "limitation": "Runtime-only values are not synthesized; omission can make a confirmed runtime field appear marginal and bias disposition toward information_sufficient.",
    }


def _load_exception_ledger(path: Path, denominator: set[str]) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        fail("environment", "missing_input", portable(path))
    rows = load_jsonl(path, "fulltype")
    for fulltype, row in rows.items():
        if fulltype not in denominator:
            fail("technical", "ledger_row_out_of_universe", fulltype)
        if row.get("authority_effect") != "none" or row.get("semantic_production") is not False or row.get("terminal_state_override_allowed") is not False:
            fail("policy", "exception_ledger_authority_violation", fulltype)
    return rows


def _load_representative_cases(
    path: Path,
    denominator: set[str],
    expected_anchor_fulltypes: Iterable[str] | None = None,
) -> tuple[dict[str, Any], list[Path]]:
    value = load_json(path)
    if (
        not isinstance(value, dict)
        or value.get("schema_version")
        != "item-page-information-sufficiency-representative-cases-v1"
        or value.get("authority_effect") != "none"
        or not isinstance(value.get("cases"), list)
        or not value["cases"]
    ):
        fail("technical", "representative_cases_contract_invalid", portable(path))
    fixture_prefix = (
        "Iris/build/description/v2/tests/fixtures/"
        "item_page_information_sufficiency/"
    )
    case_ids: set[str] = set()
    fixture_paths: list[Path] = []
    for index, case in enumerate(value["cases"]):
        if not isinstance(case, dict):
            fail("technical", "representative_case_invalid", str(index))
        case_id = case.get("case_id")
        coverage = case.get("coverage")
        if (
            not isinstance(case_id, str)
            or not case_id
            or case_id in case_ids
            or not isinstance(coverage, list)
            or not coverage
            or any(not isinstance(label, str) or not label for label in coverage)
        ):
            fail("technical", "representative_case_invalid", str(index))
        case_ids.add(case_id)
        has_fulltype = "fulltype" in case
        has_fixture = "fixture" in case
        if has_fulltype == has_fixture:
            fail("technical", "representative_case_subject_invalid", case_id)
        if has_fulltype:
            if case["fulltype"] not in denominator:
                fail("technical", "representative_fulltype_out_of_universe", case_id)
            continue
        fixture = case["fixture"]
        if (
            not isinstance(fixture, str)
            or not fixture.startswith(fixture_prefix)
            or not fixture.endswith(".json")
        ):
            fail("technical", "representative_fixture_path_invalid", case_id)
        fixture_path = repo_path(fixture)
        fixture_value = load_json(fixture_path)
        derived_fixture_keys = {
            "fact",
            "decision",
            "rendered",
            "emitted_sections",
            "usecase",
            "description",
            "expected",
            "expected_rule",
        }
        direct_state_fixture_keys = {
            "layer3_state",
            "usecase",
            "description",
            "expected",
            "expected_rule",
        }
        if (
            not isinstance(fixture_value, dict)
            or frozenset(fixture_value)
            not in {frozenset(derived_fixture_keys), frozenset(direct_state_fixture_keys)}
        ):
            fail("technical", "representative_fixture_shape_invalid", case_id)
        fixture_paths.append(fixture_path)
    if len(fixture_paths) != len(set(fixture_paths)):
        fail("technical", "duplicate_representative_fixture", portable(path))
    if expected_anchor_fulltypes is not None:
        expected_anchor_mapping = {
            "anchor-ammo-mold": "Base.223BulletsMold",
            "anchor-tongs": "Base.Tongs",
            "current-unadopted": "Base.Broom",
        }
        observed_anchor_mapping = {
            case["case_id"]: case["fulltype"]
            for case in value["cases"]
            if "fulltype" in case
        }
        if (
            observed_anchor_mapping != expected_anchor_mapping
            or set(expected_anchor_mapping.values()) != set(expected_anchor_fulltypes)
        ):
            fail("policy", "representative_anchor_binding_mismatch", portable(path))
    return value, fixture_paths


def _recompute_layer3_emitted_sections(
    fulltype: str,
    fact: dict[str, Any] | None,
    rendered: dict[str, Any] | None,
    overlay: dict[str, Any] | None,
    profiles: dict[str, Any],
) -> list[dict[str, Any]]:
    if rendered is None:
        return []
    if fact is None or not isinstance(rendered, dict):
        fail("technical", "layer3_body_plan_without_fact", fulltype)
    rendered_body_plan = rendered.get("body_plan")
    if rendered_body_plan is None:
        return []
    if not isinstance(rendered_body_plan, dict):
        fail("technical", "malformed_layer3_rendered_body_plan", fulltype)
    profile_name = rendered.get("resolved_profile")
    profile_map = profiles.get("profiles")
    if (
        not isinstance(profile_name, str)
        or not isinstance(profile_map, dict)
        or not isinstance(profile_map.get(profile_name), dict)
    ):
        fail("technical", "layer3_profile_binding_missing", fulltype)
    try:
        plan = build_body_plan_sections(
            facts=fact,
            overlay_row=overlay,
            profile_name=profile_name,
            profile_spec=profile_map[profile_name],
        )
    except (KeyError, TypeError, ValueError) as exc:
        fail("technical", "layer3_body_plan_recomputation_failed", f"{fulltype}:{type(exc).__name__}")
    sections = plan.get("emitted_sections")
    if not isinstance(sections, list):
        fail("technical", "layer3_emitted_sections_missing", fulltype)
    declared_names = rendered_body_plan.get("emitted_section_names")
    if not isinstance(declared_names, list) or any(
        not isinstance(name, str) for name in declared_names
    ):
        fail("technical", "layer3_declared_section_names_missing", fulltype)
    if len(declared_names) != len(set(declared_names)):
        fail("technical", "duplicate_layer3_declared_section_name", fulltype)
    recomputed_names = [
        section.get("section") if isinstance(section, dict) else None
        for section in sections
    ]
    if any(not isinstance(name, str) or not name for name in recomputed_names):
        fail("technical", "malformed_layer3_recomputed_section", fulltype)
    if len(recomputed_names) != len(set(recomputed_names)):
        fail("technical", "duplicate_layer3_recomputed_section_name", fulltype)
    by_name = {
        section.get("section"): section
        for section in sections
        if isinstance(section, dict) and isinstance(section.get("section"), str)
    }
    missing = [name for name in declared_names if name not in by_name]
    if (
        "context_support" in missing
        and fact.get("special_context") not in (None, "")
    ):
        by_name["context_support"] = {
            "section": "context_support",
            "slots": ["special_context"],
            "source_fields": ["facts.special_context"],
            "source_binding": "legacy_candidate_special_context",
        }
        missing.remove("context_support")
    if missing:
        fail(
            "environment",
            "layer3_declared_section_source_binding_missing",
            f"{fulltype}:{missing[0]}",
        )
    return [by_name[name] for name in declared_names]


def build_assessment(
    contract_path: Path = DEFAULT_CONTRACT_PATH,
    ratification_path: Path = DEFAULT_RATIFICATION_PATH,
    *,
    require_ratified_policy: bool = True,
) -> dict[str, bytes]:
    contract_path = ensure_repository_path(contract_path, "assessment_contract")
    ratification_path = ensure_repository_path(ratification_path, "ratification_contract")
    contract = load_json(contract_path)
    ratification = load_json(ratification_path)
    adopted_paths = validate_policy(contract, ratification, require_ratified=require_ratified_policy)
    if adopted_paths["assessment_contract"].resolve() != contract_path.resolve():
        fail("policy", "non_adopted_assessment_contract_forbidden", portable(contract_path))
    baseline = load_json(adopted_paths["baseline_field_registry"])
    l3_contract = load_json(adopted_paths["layer3_state_derivation_contract"])
    l4_contract = load_json(adopted_paths["layer4_state_derivation_contract"])
    if l3_contract.get("input_identity") != {
        "json": "canonical JSON content",
        "jsonl": "ordered canonical JSON record content",
        "generator_source": "UTF-8 LF-normalized source text with exact declared paths and generator contract",
        "newline_policy": "UTF-8 CRLF and LF are semantically equivalent",
        "legacy_descriptor_bridge": "raw descriptor identity must be reproducible from current content by newline conversion alone",
        "generated_output_identity": "raw bytes",
    }:
        fail("policy", "layer3_derivation_identity_policy_mismatch", "layer3_contract")
    if "not_applicable" in canonical_bytes(l4_contract).decode("utf-8"):
        fail("policy", "current_not_applicable_token_forbidden", "layer4_state_derivation_contract")

    inputs = contract.get("inputs", {})
    denominator_path = repo_path(inputs["denominator"])
    pointer_path = repo_path(inputs["layer3_current_pointer"])
    usecases_path = repo_path(inputs["layer4_usecases"])
    descriptions_path = repo_path(inputs["layer4_descriptions"])
    ledger_path = repo_path(inputs["exception_ledger"])
    representative_cases_path = repo_path(inputs["representative_cases"])
    denominator = _load_denominator(denominator_path)
    representative_cases, representative_fixture_paths = _load_representative_cases(
        representative_cases_path, set(denominator), contract.get("anchors", [])
    )
    validate_baseline_registry(baseline, denominator)
    (
        generation_id,
        generation_root,
        descriptor,
        rendered_doc,
        canonical_input_validation,
        generator_source_validation,
    ) = _validate_generation(
        pointer_path, contract.get("layer3_generator_source_subjects")
    )
    canonical_inputs = {Path(row["path"]).name: repo_path(row["path"]) for row in descriptor["canonical_inputs"]}
    facts_path = canonical_inputs.get("dvf_3_3_facts.jsonl")
    decisions_path = canonical_inputs.get("dvf_3_3_decisions.jsonl")
    overlay_path = canonical_inputs.get("dvf_3_3_overlay_support.jsonl")
    profiles_path = canonical_inputs.get("compose_profiles_v2.json")
    if (
        facts_path is None
        or decisions_path is None
        or overlay_path is None
        or profiles_path is None
    ):
        fail("environment", "generation_provenance_input_missing", generation_id)
    facts = load_jsonl(facts_path, "item_id")
    decisions = load_jsonl(decisions_path, "item_id")
    overlays = load_jsonl(overlay_path, "item_id")
    profiles = load_json(profiles_path)
    rendered = rendered_doc["entries"]
    usecases_doc = load_json(usecases_path)
    descriptions_doc = load_json(descriptions_path)
    usecases = usecases_doc.get("fulltypes")
    descriptions = descriptions_doc.get("fulltypes")
    if not isinstance(usecases, dict) or not isinstance(descriptions, dict):
        fail("technical", "layer4_declared_set_missing", "layer4")
    universe = set(denominator)
    for label, values in (("facts", facts), ("decisions", decisions), ("overlays", overlays), ("rendered", rendered), ("usecases", usecases), ("descriptions", descriptions)):
        extra = set(values) - universe
        if extra:
            fail("technical", "producer_row_out_of_universe", f"{label}:{sorted(extra)[0]}")
    ledger = _load_exception_ledger(ledger_path, universe)

    producer_identities = {
        "denominator": producer_content_identity(denominator_path),
        "layer3_facts": producer_content_identity(facts_path),
        "layer3_decisions": producer_content_identity(decisions_path),
        "layer3_overlay": producer_content_identity(overlay_path),
        "layer3_profiles": producer_content_identity(profiles_path),
        "layer4_usecases": producer_content_identity(usecases_path),
        "layer4_descriptions": producer_content_identity(descriptions_path),
        "exception_ledger": producer_content_identity(ledger_path),
        "representative_cases": producer_content_identity(representative_cases_path),
        "representative_fixtures": [
            producer_content_identity(path) for path in representative_fixture_paths
        ],
    }
    input_hashes = {
        "denominator": producer_identities["denominator"]["sha256"],
        "layer3_pointer": raw_hash(pointer_path),
        "layer3_descriptor": raw_hash(generation_root / "generation_descriptor.json"),
        "layer3_facts": producer_identities["layer3_facts"]["sha256"],
        "layer3_decisions": producer_identities["layer3_decisions"]["sha256"],
        "layer3_overlay": producer_identities["layer3_overlay"]["sha256"],
        "layer3_profiles": producer_identities["layer3_profiles"]["sha256"],
        "layer3_rendered": raw_hash(generation_root / "dvf_3_3_rendered.json"),
        "layer4_usecases": producer_identities["layer4_usecases"]["sha256"],
        "layer4_descriptions": producer_identities["layer4_descriptions"]["sha256"],
        "exception_ledger": producer_identities["exception_ledger"]["sha256"],
        "representative_cases": producer_identities["representative_cases"]["sha256"],
        "representative_fixtures": hashlib.sha256(
            canonical_bytes(
                [
                    {
                        key: record[key]
                        for key in ("path", "identity_algorithm", "sha256")
                    }
                    for record in producer_identities["representative_fixtures"]
                ]
            )
        ).hexdigest(),
        "baseline_registry": canonical_hash(baseline),
        "layer3_contract": canonical_hash(l3_contract),
        "layer4_contract": canonical_hash(l4_contract),
        "assessment_contract": canonical_hash(contract),
        "ratification_contract": canonical_hash(ratification),
    }
    protected_paths = sorted(
        {
            *_protected_surface(generation_root, descriptor),
            ledger_path,
            representative_cases_path,
            *representative_fixture_paths,
        },
        key=portable,
    )
    protected_before = {portable(path): raw_hash(path) for path in protected_paths}
    rows: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    disposition_counts: Counter[str] = Counter()
    reason_counts: Counter[str] = Counter()
    l3_counts: Counter[str] = Counter()
    l4_counts: Counter[str] = Counter()
    residue_count = 0
    residue_routed = 0
    unresolved_unrouted = 0
    baseline_names = [entry["name"] for entry in baseline["fields"]]
    compact_input_identities = {
        "generation_id": generation_id,
        "denominator_sha256": input_hashes["denominator"],
        "layer3_descriptor_sha256": input_hashes["layer3_descriptor"],
        "layer4_usecases_sha256": input_hashes["layer4_usecases"],
        "layer4_descriptions_sha256": input_hashes["layer4_descriptions"],
        "exception_ledger_sha256": input_hashes["exception_ledger"],
    }
    for fulltype in sorted(denominator):
        item = denominator[fulltype]
        emitted_sections = _recompute_layer3_emitted_sections(
            fulltype,
            facts.get(fulltype),
            rendered.get(fulltype),
            overlays.get(fulltype),
            profiles,
        )
        l3 = _layer3_state(
            fulltype,
            facts.get(fulltype),
            decisions.get(fulltype),
            rendered.get(fulltype),
            input_hashes,
            emitted_sections,
        )
        l4 = _layer4_state(fulltype, usecases.get(fulltype), descriptions.get(fulltype), input_hashes)
        disposition, rule, page_reasons = decide_disposition(l3, l4)
        ledger_row = ledger.get(fulltype)
        residue = l3["requiredness"] == "unresolved" or l4["fact_availability"] == "unresolved"
        if residue:
            residue_count += 1
            if ledger_row:
                residue_routed += 1
            else:
                unresolved_unrouted += 1
                if "unrouted_derivation_residue" not in page_reasons:
                    page_reasons.append("unrouted_derivation_residue")
        scope_limitations = []
        if l4["scope_limitation"] != "none":
            scope_limitations.append(l4["scope_limitation"])
        row = {
            "schema_version": SCHEMA_VERSION,
            "fulltype": fulltype,
            "input_identities": compact_input_identities,
            "baseline": {
                "registry_sha256": input_hashes["baseline_registry"],
                "display_name_identity": item.get("DisplayName"),
                "present_fields": [name for name in baseline_names if name in item],
                "lower_bound": True,
            },
            "layer3": l3,
            "layer4": l4,
            "exception_routing": {
                "ledger_entry_present": ledger_row is not None,
                "routing_status": ledger_row.get("routing_status") if ledger_row else "none",
                "authority_effect": "none",
                "terminal_state_override_allowed": False,
                "ledger_sha256": input_hashes["exception_ledger"],
                "ledger_identity_algorithm": producer_identities["exception_ledger"]["identity_algorithm"],
                "ledger_ref": fulltype if ledger_row else None,
            },
            "applied_precedence_rule": rule,
            "page_disposition": disposition,
            "page_reasons": page_reasons,
            "scope_limitations": scope_limitations,
            "execution_status": "PASS",
            "publish_verdict": False,
        }
        rows.append(row)
        disposition_counts[disposition] += 1
        for reason in page_reasons:
            reason_counts[reason] += 1
        l3_counts[f"{l3['requiredness']}|{l3['representation']}"] += 1
        l4_counts[f"{l4['applicability']}|{l4['representation']}|{l4['scope_limitation']}"] += 1
        if disposition in {"known_information_missing", "unresolved"}:
            gaps.append({
                "fulltype": fulltype,
                "page_disposition": disposition,
                "applied_precedence_rule": rule,
                "page_reasons": page_reasons,
                "scope_limitations": scope_limitations,
            })
    page_bytes = b"".join(canonical_bytes(row) for row in rows)
    gap_bytes = b"".join(canonical_bytes(row) for row in gaps)
    result_sha = hashlib.sha256(page_bytes).hexdigest()
    evidence_limited_count = disposition_counts["evidence_limited"]
    matrix_total = matrix_totality_check(l3_contract, l4_contract)
    misclassified_count = 0
    for row in rows:
        l3 = row["layer3"]
        l4 = row["layer4"]
        known_missing = (
            l3["requiredness"] == "required" and l3["representation"] == "missing"
        ) or (
            l4["applicability"] == "applicable" and l4["representation"] == "missing"
        )
        incoherent = bool(state_vector_incoherence(l3, l4))
        if (known_missing or incoherent) and row["page_disposition"] == "information_sufficient":
            misclassified_count += 1
    current_not_applicable_count = sum(
        token == "not_applicable" for row in rows for token in _scalar_tokens(row)
    )
    if evidence_limited_count == 0:
        validation_status = "POLICY_REVIEW_REQUIRED"
    elif not matrix_total or misclassified_count or current_not_applicable_count:
        validation_status = "FAIL"
    else:
        validation_status = "PASS"
    denominator_count = len(denominator)
    summary = {
        "schema_version": "item-page-information-sufficiency-summary-v1",
        "execution_status": validation_status,
        "result_sha256": result_sha,
        "result_identity_algorithm": "sha256_page_assessment_jsonl_raw_bytes_v1",
        "denominator_count": denominator_count,
        "assessed_count": len(rows),
        "disposition_counts": {key: disposition_counts[key] for key in DISPOSITIONS},
        "reason_code_counts": dict(sorted(reason_counts.items())),
        "layer3_state_cross_tab": dict(sorted(l3_counts.items())),
        "layer4_state_cross_tab": dict(sorted(l4_counts.items())),
        "input_hashes": input_hashes,
        "ledger_observability": {
            "ledger_row_count": len(ledger),
            "denominator_with_ledger_entry_count": len(set(ledger) & universe),
            "denominator_without_ledger_entry_count": denominator_count - len(set(ledger) & universe),
            "derivation_residue_count": residue_count,
            "residue_routed_count": residue_routed,
            "residue_unrouted_count": residue_count - residue_routed,
            "unresolved_due_to_unrouted_residue_count": unresolved_unrouted,
            "ledger_coverage_ratio": len(set(ledger) & universe) / denominator_count,
        },
        "limitations": [
            "current vanilla offline snapshot only",
            "baseline registry is an ItemScript-preserved lower bound and biases toward information_sufficient",
            "sealed_complete does not claim extraction coverage, semantic completeness, or world-level absence",
            "assessment is Publish Boundary component evidence, not a Publish Boundary verdict",
        ],
    }
    manifest = {
        "schema_version": "item-page-information-sufficiency-input-manifest-v1",
        "result_sha256": result_sha,
        "ratification_record_identity": ratification["ratification_record_identity"],
        "proposal_subject_sha256": ratification["proposal_subject_sha256"],
        "denominator": {
            **producer_identities["denominator"],
            "row_count": denominator_count,
            "sorted_key_sha256": _sorted_key_hash(denominator),
            "casefold_collision_groups": sorted(
                [sorted(group) for group in _casefold_groups(denominator) if len(group) > 1]
            ),
        },
        "layer3": {
            "pointer": identity(pointer_path),
            "generation_id": generation_id,
            "generation_descriptor": identity(generation_root / "generation_descriptor.json"),
            "canonical_inputs": descriptor["canonical_inputs"],
            "canonical_input_validation": canonical_input_validation,
            "generator_source_validation": generator_source_validation,
            "rendered_row_count": len(rendered),
            "rendered_sorted_key_sha256": _sorted_key_hash(rendered),
        },
        "layer4": {
            "usecases": {**producer_identities["layer4_usecases"], "row_count": len(usecases), "sorted_key_sha256": _sorted_key_hash(usecases)},
            "descriptions": {**producer_identities["layer4_descriptions"], "row_count": len(descriptions), "sorted_key_sha256": _sorted_key_hash(descriptions)},
        },
        "representative_cases": {
            **producer_identities["representative_cases"],
            "case_count": len(representative_cases["cases"]),
            "fixtures": producer_identities["representative_fixtures"],
        },
        "exception_ledger": {
            **producer_identities["exception_ledger"],
            "row_count": len(ledger),
            "authority_effect": "none",
        },
        "excluded_input_roles": ["historical", "staging_except_descriptor_declared_canonical_input", "diagnostic", "iar_attempt_nonce_receipt_adoption"],
    }
    anchor_ids = contract.get("anchors", [])
    row_by_id = {row["fulltype"]: row for row in rows}
    anchors = {
        "schema_version": "item-page-information-sufficiency-anchor-assessment-v1",
        "anchors": [row_by_id[value] for value in anchor_ids if value in row_by_id],
        "generic_evaluator_path": True,
        "item_specific_branches": False,
    }
    protected_after = {portable(path): raw_hash(path) for path in protected_paths}
    protected_report = {
        "schema_version": "item-page-information-sufficiency-protected-surface-hash-report-v1",
        "status": "PASS" if protected_before == protected_after else "FAIL",
        "mutation_count": sum(protected_before.get(key) != protected_after.get(key) for key in set(protected_before) | set(protected_after)),
        "before": protected_before,
        "after": protected_after,
    }
    validation_report = {
        "schema_version": "item-page-information-sufficiency-validation-report-v1",
        "status": validation_status,
        "checks": {
            "ratification_complete": True,
            "denominator_row_set_equal": len(rows) == denominator_count and {row["fulltype"] for row in rows} == universe,
            "distribution_sums_to_denominator": sum(disposition_counts.values()) == denominator_count,
            "matrix_total_function": matrix_total,
            "derivation_level_evidence_limited_reachable": evidence_limited_count > 0,
            "current_not_applicable_emission_count": current_not_applicable_count,
            "protected_surface_non_mutation": protected_before == protected_after,
            "known_or_unresolved_misclassified_sufficient_count": misclassified_count,
        },
        "non_claims": ["no_public_text_quality_pass", "no_publish_boundary_pass", "no_release_readiness", "no_runtime_mutation"],
    }
    return {
        "assessment_input_manifest.json": canonical_bytes(manifest),
        "page_assessment.jsonl": page_bytes,
        "assessment_summary.json": canonical_bytes(summary),
        "information_gap_inventory.jsonl": gap_bytes,
        "anchor_assessment.json": canonical_bytes(anchors),
        "terminology_responsibility_mapping.json": canonical_bytes(_terminology_mapping()),
        "baseline_runtime_drift_report.json": canonical_bytes(_runtime_drift_report()),
        "protected_surface_hash_report.json": canonical_bytes(protected_report),
        "validation_report.json": canonical_bytes(validation_report),
    }


def _casefold_groups(keys: Iterable[str]) -> list[list[str]]:
    groups: dict[str, list[str]] = {}
    for key in keys:
        groups.setdefault(key.casefold(), []).append(key)
    return list(groups.values())


def write_bundle(bundle: dict[str, bytes], output_root: Path) -> None:
    allowed_output_parent = (V2_ROOT / "output").resolve()
    try:
        resolved = output_root.resolve()
        if not resolved.is_relative_to(allowed_output_parent):
            fail("technical", "output_outside_designated_root", str(output_root))
    except OSError:
        fail("environment", "output_path_unresolvable", str(output_root))
    output_root.mkdir(parents=True, exist_ok=True)
    allowed = set(bundle)
    existing = {path.name for path in output_root.iterdir() if path.is_file()}
    unexpected = existing - allowed
    if unexpected:
        fail("technical", "unexpected_output_file", sorted(unexpected)[0])
    for name, payload in bundle.items():
        target = output_root / name
        if target.is_symlink():
            fail("technical", "output_target_symlink_forbidden", portable(target))
        temporary = output_root / f".{name}.ips-tmp"
        if temporary.exists() or temporary.is_symlink():
            fail("technical", "stale_output_temporary_file", portable(temporary))
        temporary.write_bytes(payload)
        temporary.replace(target)


def validate_bundle(
    bundle: dict[str, bytes],
    result_root: Path,
    compare_root: Path | None = None,
) -> dict[str, Any]:
    result_root = ensure_repository_path(result_root, "result_root")
    if compare_root is not None:
        compare_root = ensure_repository_path(compare_root, "compare_result_root")
    mismatches = []
    for name, expected in bundle.items():
        path = result_root / name
        try:
            actual = path.read_bytes()
        except FileNotFoundError:
            mismatches.append(f"missing:{name}")
            continue
        if actual != expected:
            mismatches.append(f"content:{name}")
        if compare_root is not None:
            try:
                compared = (compare_root / name).read_bytes()
            except FileNotFoundError:
                mismatches.append(f"compare_missing:{name}")
            else:
                if actual != compared:
                    mismatches.append(f"compare_content:{name}")
    summary = json.loads(bundle["assessment_summary.json"])
    return {
        "schema_version": "item-page-information-sufficiency-no-write-validation-v1",
        "status": "PASS" if not mismatches and summary["execution_status"] == "PASS" else summary["execution_status"] if not mismatches else "FAIL",
        "no_write": True,
        "mismatches": mismatches,
        "result_sha256": summary["result_sha256"],
        "validated_file_count": len(bundle),
    }


def validate_canonical_successor_binding(result_sha256: str) -> dict[str, Any]:
    root = REPO_ROOT / "Iris" / "_docs" / "round3" / "item_page_information_sufficiency" / result_sha256
    manifest_path = root / "canonical_successor_subject_manifest.json"
    review_path = root / "independent_review.json"
    seal_path = root / "owner_seal.json"
    closeout_path = root / "axis_qualified_closeout.json"
    manifest = load_json(manifest_path)
    if (
        manifest.get("schema_version")
        != "item-page-information-sufficiency-canonical-successor-subject-manifest-v1"
    ):
        fail("governance", "successor_manifest_schema_mismatch", result_sha256)
    manifest_sha = canonical_hash(manifest)
    if manifest.get("manifest_hash_algorithm") != "sha256_canonical_json_lf_v1":
        fail("governance", "successor_manifest_hash_algorithm_mismatch", result_sha256)
    subject_records = manifest.get("subject_files")
    if not isinstance(subject_records, list) or not subject_records:
        fail("governance", "successor_subject_files_missing", result_sha256)
    assessment_contract = load_json(DEFAULT_CONTRACT_PATH)
    pointer_path = repo_path(assessment_contract["inputs"]["layer3_current_pointer"])
    generation_id = _parse_current_generation(pointer_path)
    descriptor_path = (
        pointer_path.parent
        / "IrisLayer3Generations"
        / generation_id
        / "generation_descriptor.json"
    )
    descriptor = load_json(descriptor_path)
    descriptor_generator = descriptor.get("generator")
    implementation_records = (
        descriptor_generator.get("implementation_files")
        if isinstance(descriptor_generator, dict)
        else None
    )
    if not isinstance(implementation_records, list) or not implementation_records:
        fail("governance", "successor_generator_source_set_missing", result_sha256)
    denominator = _load_denominator(
        repo_path(assessment_contract["inputs"]["denominator"])
    )
    representative_cases_path = repo_path(
        assessment_contract["inputs"]["representative_cases"]
    )
    _, representative_fixture_paths = _load_representative_cases(
        representative_cases_path,
        set(denominator),
        assessment_contract.get("anchors", []),
    )
    result_names = {
        "assessment_input_manifest.json",
        "page_assessment.jsonl",
        "assessment_summary.json",
        "information_gap_inventory.jsonl",
        "anchor_assessment.json",
        "terminology_responsibility_mapping.json",
        "baseline_runtime_drift_report.json",
        "protected_surface_hash_report.json",
        "validation_report.json",
    }
    required_subject_paths = {
        ".gitattributes",
        "Iris/_docs/round3/round3_active_core_closure.json",
        "docs/iris_item_page_information_sufficiency_policy.md",
        "Iris/build/description/v2/data/item_page_information_sufficiency/assessment_contract.json",
        "Iris/build/description/v2/data/item_page_information_sufficiency/policy_ratification_contract.json",
        "Iris/build/description/v2/data/item_page_information_sufficiency/baseline_field_registry.json",
        "Iris/build/description/v2/data/item_page_information_sufficiency/layer3_state_derivation_contract.json",
        "Iris/build/description/v2/data/item_page_information_sufficiency/layer4_state_derivation_contract.json",
        "Iris/build/description/v2/data/item_page_information_sufficiency/state_exception_ledger.jsonl",
        assessment_contract["inputs"]["representative_cases"],
        "Iris/build/description/v2/tools/build/item_page_information_sufficiency.py",
        "Iris/build/description/v2/tools/build/run_item_page_information_sufficiency_assessment.py",
        "Iris/build/description/v2/tools/build/validate_item_page_information_sufficiency_assessment.py",
        "Iris/build/description/v2/tests/test_item_page_information_sufficiency.py",
        "Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py",
        "Iris/build/description/v2/tools/build/dvf_3_3_consumer_migration_normalization_common.py",
        "Iris/build/description/v2/tools/build/validate_dvf_3_3_consumer_migration_input_normalization.py",
        "Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py",
        "Iris/build/description/v2/tools/build/dvf_3_3_closeout_reentry_guard_seal_common.py",
        "Iris/build/description/v2/tests/test_dvf_3_3_closeout_reentry_guard_seal.py",
        "Iris/test/validate_residual_refactor_surfaces.ps1",
        "Iris/build/description/v2/tests/test_iris_residual_contract_surfaces.py",
        "Iris/_docs/round3/item_page_information_sufficiency/63077bf221b5af4874bbeb78fecd02708a7472564942b8e7e4d129df9a77b480/protected_surface_working_overlay.json",
        assessment_contract["inputs"]["denominator"],
        assessment_contract["inputs"]["layer3_current_pointer"],
        assessment_contract["inputs"]["layer4_usecases"],
        assessment_contract["inputs"]["layer4_descriptions"],
        portable(descriptor_path),
        *(
            record["path"]
            for record in descriptor.get("canonical_inputs", [])
            if isinstance(record, dict) and isinstance(record.get("path"), str)
        ),
        *(
            record["path"]
            for record in implementation_records
            if isinstance(record, dict) and isinstance(record.get("path"), str)
        ),
        *(portable(path) for path in representative_fixture_paths),
        *(
            portable(DEFAULT_OUTPUT_ROOT / name)
            for name in result_names
        ),
    }
    declared_subject_paths = {
        record.get("path") for record in subject_records if isinstance(record, dict)
    }
    if declared_subject_paths != required_subject_paths or len(subject_records) != len(
        required_subject_paths
    ):
        fail("governance", "successor_subject_file_set_mismatch", result_sha256)
    canonical_json_paths = {
        "Iris/_docs/round3/round3_active_core_closure.json",
        "Iris/_docs/round3/item_page_information_sufficiency/63077bf221b5af4874bbeb78fecd02708a7472564942b8e7e4d129df9a77b480/protected_surface_working_overlay.json",
        "Iris/build/description/v2/data/item_page_information_sufficiency/assessment_contract.json",
        "Iris/build/description/v2/data/item_page_information_sufficiency/policy_ratification_contract.json",
        "Iris/build/description/v2/data/item_page_information_sufficiency/baseline_field_registry.json",
        "Iris/build/description/v2/data/item_page_information_sufficiency/layer3_state_derivation_contract.json",
        "Iris/build/description/v2/data/item_page_information_sufficiency/layer4_state_derivation_contract.json",
        assessment_contract["inputs"]["denominator"],
        assessment_contract["inputs"]["layer4_usecases"],
        assessment_contract["inputs"]["layer4_descriptions"],
        assessment_contract["inputs"]["representative_cases"],
        *(portable(path) for path in representative_fixture_paths),
        *(
            record["path"]
            for record in descriptor.get("canonical_inputs", [])
            if isinstance(record, dict)
            and isinstance(record.get("path"), str)
            and Path(record["path"]).suffix.lower() == ".json"
        ),
    }
    canonical_jsonl_paths = {
        "Iris/build/description/v2/data/item_page_information_sufficiency/state_exception_ledger.jsonl",
        *(
            record["path"]
            for record in descriptor.get("canonical_inputs", [])
            if isinstance(record, dict)
            and isinstance(record.get("path"), str)
            and Path(record["path"]).suffix.lower() == ".jsonl"
        ),
    }
    lf_normalized_source_paths = {
        record["path"]
        for record in implementation_records
        if isinstance(record, dict) and isinstance(record.get("path"), str)
    }
    lf_normalized_source_paths.update(
        {
            ".gitattributes",
            "Iris/build/description/v2/tests/test_item_page_information_sufficiency.py",
            "Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py",
            "Iris/build/description/v2/tools/build/item_page_information_sufficiency.py",
            "Iris/build/description/v2/tools/build/run_item_page_information_sufficiency_assessment.py",
            "Iris/build/description/v2/tools/build/validate_item_page_information_sufficiency_assessment.py",
            "Iris/build/description/v2/tools/build/dvf_3_3_consumer_migration_normalization_common.py",
            "Iris/build/description/v2/tools/build/validate_dvf_3_3_consumer_migration_input_normalization.py",
            "Iris/build/description/v2/tests/test_dvf_3_3_consumer_migration_input_normalization.py",
            "Iris/build/description/v2/tools/build/dvf_3_3_closeout_reentry_guard_seal_common.py",
            "Iris/build/description/v2/tests/test_dvf_3_3_closeout_reentry_guard_seal.py",
            "Iris/test/validate_residual_refactor_surfaces.ps1",
            "Iris/build/description/v2/tests/test_iris_residual_contract_surfaces.py",
        }
    )
    expected_algorithms = {
        path: "sha256_raw_bytes_v1" for path in required_subject_paths
    }
    for path in canonical_json_paths:
        expected_algorithms[path] = "sha256_canonical_json_lf_v1"
    for path in canonical_jsonl_paths:
        expected_algorithms[path] = "sha256_canonical_jsonl_records_lf_v1"
    for path in lf_normalized_source_paths:
        expected_algorithms[path] = "sha256_utf8_lf_normalized_text_v1"
    for record in subject_records:
        if not isinstance(record, dict):
            fail("governance", "invalid_successor_subject_record", result_sha256)
        subject_path = repo_path(record.get("path", ""))
        algorithm = record.get("identity_algorithm")
        expected_algorithm = expected_algorithms.get(record.get("path"))
        if algorithm != expected_algorithm:
            fail(
                "governance",
                "successor_subject_identity_algorithm_mismatch",
                str(record.get("path")),
            )
        if algorithm == "sha256_raw_bytes_v1":
            observed = raw_hash(subject_path)
        elif algorithm == "sha256_canonical_json_lf_v1":
            observed = canonical_hash(load_json(subject_path))
        elif algorithm == "sha256_canonical_jsonl_records_lf_v1":
            observed = canonical_jsonl_hash(subject_path)
        elif algorithm == "sha256_utf8_lf_normalized_text_v1":
            try:
                source_data = subject_path.read_bytes()
            except FileNotFoundError:
                fail("environment", "missing_input", portable(subject_path))
            except OSError:
                fail("environment", "unreadable_input", portable(subject_path))
            observed = hashlib.sha256(
                _lf_normalized_utf8_bytes(source_data)
            ).hexdigest()
        else:
            fail("governance", "unknown_successor_subject_identity_algorithm", str(algorithm))
        if observed != record.get("sha256"):
            fail("governance", "successor_subject_identity_mismatch", portable(subject_path))
    bound_entries = manifest.get("bound_governance_successors")
    expected_bound_paths = {
        "Iris/_docs/round3/current_route_required_validations.json",
        "Iris/_docs/authority/iris_current_authority_manifest.json",
        "docs/DECISIONS.md",
        "docs/ARCHITECTURE.md",
        "docs/ROADMAP.md",
    }
    if not isinstance(bound_entries, list) or len(bound_entries) != 5 or {
        record.get("path") for record in bound_entries if isinstance(record, dict)
    } != expected_bound_paths:
        fail("governance", "bound_successor_entry_set_mismatch", result_sha256)
    expected_selectors = {
        "Iris/_docs/round3/current_route_required_validations.json": {
            "selector_type": "json_entry_id",
            "entry_id": "IPS-GOV-ROUTE-01",
        },
        "Iris/_docs/authority/iris_current_authority_manifest.json": {
            "selector_type": "json_entry_id",
            "entry_id": "IPS-GOV-AUTHORITY-01",
        },
        "docs/DECISIONS.md": {
            "selector_type": "markdown_markers",
            "start_marker": "<!-- IPS-GOV-DECISIONS-01-START -->",
            "end_marker": "<!-- IPS-GOV-DECISIONS-01-END -->",
        },
        "docs/ARCHITECTURE.md": {
            "selector_type": "markdown_markers",
            "start_marker": "<!-- IPS-GOV-ARCHITECTURE-01-START -->",
            "end_marker": "<!-- IPS-GOV-ARCHITECTURE-01-END -->",
        },
        "docs/ROADMAP.md": {
            "selector_type": "markdown_markers",
            "start_marker": "<!-- IPS-GOV-ROADMAP-01-START -->",
            "end_marker": "<!-- IPS-GOV-ROADMAP-01-END -->",
        },
    }
    for record in bound_entries:
        if not isinstance(record, dict):
            fail("governance", "invalid_bound_successor_entry", result_sha256)
        expected_selector = expected_selectors[record["path"]]
        if any(record.get(key) != value for key, value in expected_selector.items()):
            fail("governance", "bound_successor_selector_mismatch", record["path"])
    container_drift = []
    for record in bound_entries:
        path = repo_path(record.get("path", ""))
        selector_type = record.get("selector_type")
        if selector_type == "json_entry_id":
            payload = load_json(path)
            matches = _find_entry_id(payload, record.get("entry_id"))
            if len(matches) != 1:
                fail("governance", "bound_json_entry_ambiguous", portable(path))
            observed_entry_sha = canonical_hash(matches[0])
        elif selector_type == "markdown_markers":
            observed_entry_sha = _markdown_segment_hash(
                path,
                record.get("start_marker"),
                record.get("end_marker"),
            )
        else:
            fail("governance", "unknown_bound_entry_selector", str(selector_type))
        if observed_entry_sha != record.get("entry_sha256"):
            fail("governance", "bound_successor_entry_identity_mismatch", portable(path))
        current_container_hash = raw_hash(path)
        if current_container_hash != record.get("freeze_container_raw_sha256"):
            container_drift.append(portable(path))
    review = load_json(review_path)
    seal = load_json(seal_path)
    closeout = load_json(closeout_path)
    expected_successor_schemas = {
        "review": "item-page-information-sufficiency-independent-review-v1",
        "seal": "item-page-information-sufficiency-owner-seal-v1",
        "closeout": "item-page-information-sufficiency-axis-qualified-closeout-v1",
    }
    if review.get("schema_version") != expected_successor_schemas["review"]:
        fail("governance", "independent_review_schema_mismatch", result_sha256)
    if seal.get("schema_version") != expected_successor_schemas["seal"]:
        fail("governance", "owner_seal_schema_mismatch", result_sha256)
    if closeout.get("schema_version") != expected_successor_schemas["closeout"]:
        fail("governance", "axis_qualified_closeout_schema_mismatch", result_sha256)
    if manifest.get("result_sha256") != result_sha256:
        fail("governance", "successor_result_binding_mismatch", result_sha256)
    eligibility = review.get("reviewer_eligibility")
    if (
        not isinstance(review.get("reviewer_identity"), str)
        or not review["reviewer_identity"]
        or not isinstance(eligibility, dict)
        or eligibility.get("eligible") is not True
        or eligibility.get("disqualifying_roles") != []
        or review.get("review_scope") != "exact_canonical_successor_subject_manifest"
    ):
        fail("governance", "independent_review_eligibility_mismatch", result_sha256)
    if review.get("canonical_successor_subject_manifest_sha256") != manifest_sha or review.get("verdict") != "APPROVED":
        fail("governance", "independent_review_binding_mismatch", result_sha256)
    review_sha = canonical_hash(review)
    if seal.get("canonical_successor_subject_manifest_sha256") != manifest_sha or seal.get("independent_review_sha256") != review_sha or seal.get("decision") != "sealed":
        fail("governance", "owner_seal_binding_mismatch", result_sha256)
    ratification = load_json(DEFAULT_RATIFICATION_PATH)
    if (
        seal.get("owner_identity") != ratification.get("owner_identity")
        or seal.get("owner_identity") == review.get("reviewer_identity")
    ):
        fail("governance", "reviewer_owner_identity_conflict", result_sha256)
    seal_sha = canonical_hash(seal)
    if closeout.get("status") != "page_sufficiency_assessment_complete" or closeout.get("canonical_successor_subject_manifest_sha256") != manifest_sha or closeout.get("independent_review_sha256") != review_sha or closeout.get("owner_seal_sha256") != seal_sha:
        fail("governance", "axis_qualified_closeout_binding_mismatch", result_sha256)
    return {
        "status": "PASS",
        "manifest_sha256": manifest_sha,
        "bound_entry_count": len(bound_entries),
        "diagnostic_container_raw_hash_drift": container_drift,
    }


def _find_entry_id(value: Any, entry_id: Any) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if value.get("entry_id") == entry_id:
            matches.append(value)
        for nested in value.values():
            matches.extend(_find_entry_id(nested, entry_id))
    elif isinstance(value, list):
        for nested in value:
            matches.extend(_find_entry_id(nested, entry_id))
    return matches


def _markdown_segment_hash(path: Path, start_marker: Any, end_marker: Any) -> str:
    if not isinstance(start_marker, str) or not isinstance(end_marker, str):
        fail("governance", "invalid_markdown_boundary", portable(path))
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    if text.count(start_marker) != 1 or text.count(end_marker) != 1:
        fail("governance", "ambiguous_markdown_boundary", portable(path))
    start = text.find(start_marker)
    end_start = text.find(end_marker)
    if start < 0 or end_start <= start:
        fail("governance", "invalid_markdown_boundary_order", portable(path))
    end = end_start + len(end_marker)
    return hashlib.sha256(text[start:end].encode("utf-8")).hexdigest()


def error_payload(exc: AssessmentFailure) -> dict[str, Any]:
    core = {
        "schema_version": "item-page-information-sufficiency-execution-error-v1",
        "status": "FAIL",
        "failure_domain": exc.domain,
        "failure_code": exc.code,
        "detail": exc.detail,
    }
    return {**core, "deterministic_error_hash": canonical_hash(core)}
