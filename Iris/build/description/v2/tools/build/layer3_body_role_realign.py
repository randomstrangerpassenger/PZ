from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable


SCALAR_SLOTS = (
    "identity_hint",
    "primary_use",
    "acquisition_hint",
    "secondary_use",
    "processing_hint",
    "limitation_hint",
    "notes",
    "special_context",
)
DESCRIPTION_KINDS = frozenset(
    {
        "role",
        "target",
        "action",
        "result",
        "consumption_or_retention",
        "condition",
        "restriction",
    }
)
DISPOSITIONS = frozenset({"keep", "reduce", "revise", "hide", "review_hold"})
READINESS_STATES = frozenset(
    {
        "description_ready",
        "acquisition_only",
        "omission_allowed",
        "insufficient_material",
        "review_required",
    }
)


class RoleRealignError(RuntimeError):
    pass


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise RoleRealignError(f"DUPLICATE_JSON_KEY: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RoleRealignError(f"INVALID_JSON: {path}: {exc}") from exc


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            try:
                row = json.loads(raw, object_pairs_hook=_no_duplicate_object)
            except (json.JSONDecodeError, RoleRealignError) as exc:
                raise RoleRealignError(f"INVALID_JSONL: {path}:{line_number}: {exc}") from exc
            if not isinstance(row, dict):
                raise RoleRealignError(f"JSONL_ROW_NOT_OBJECT: {path}:{line_number}")
            rows.append(row)
    except (OSError, UnicodeError) as exc:
        raise RoleRealignError(f"INVALID_JSONL: {path}: {exc}") from exc
    return rows


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def canonical_jsonl_sha256(rows: Iterable[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(canonical_bytes(row))
        digest.update(b"\n")
    return digest.hexdigest()


def raw_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def set_sha256(values: Iterable[str]) -> str:
    return canonical_sha256(sorted(set(values)))


def has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def ensure_sentence(value: str) -> str:
    text = value.strip()
    if not text:
        return text
    return text if text[-1] in ".!?。！？" else f"{text}."


def repository_root_from_script() -> Path:
    return Path(__file__).resolve().parents[6]


def relative_path(repository_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError as exc:
        raise RoleRealignError(f"PATH_OUTSIDE_REPOSITORY: {path}") from exc


@dataclass(frozen=True)
class CurrentGeneration:
    generation_id: str
    root: Path
    rendered_path: Path
    descriptor_path: Path
    pointer_path: Path


def resolve_current_generation(repository_root: Path) -> CurrentGeneration:
    pointer = repository_root / "Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua"
    try:
        pointer_text = pointer.read_text(encoding="utf-8")
    except OSError as exc:
        raise RoleRealignError(f"CURRENT_POINTER_UNREADABLE: {pointer}") from exc
    matches = re.findall(r'\bgeneration_id\s*=\s*"([^"]+)"', pointer_text)
    if len(matches) != 1:
        raise RoleRealignError("CURRENT_POINTER_GENERATION_ID_NOT_EXACTLY_ONE")
    generation_id = matches[0]
    if not re.fullmatch(r"dvf33-[0-9a-f]{64}", generation_id):
        raise RoleRealignError(f"INVALID_CURRENT_GENERATION_ID: {generation_id}")
    root = (
        repository_root
        / "Iris/media/lua/client/Iris/Data/IrisLayer3Generations"
        / generation_id
    )
    rendered = root / "dvf_3_3_rendered.json"
    descriptor = root / "generation_descriptor.json"
    if not rendered.is_file() or not descriptor.is_file():
        raise RoleRealignError(f"INCOMPLETE_CURRENT_GENERATION: {generation_id}")
    return CurrentGeneration(generation_id, root, rendered, descriptor, pointer)


def load_item_denominator(path: Path) -> dict[str, dict[str, Any]]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise RoleRealignError("ITEM_DENOMINATOR_NOT_OBJECT")
    items: dict[str, dict[str, Any]] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or not isinstance(value, dict):
            raise RoleRealignError("INVALID_ITEM_DENOMINATOR_ROW")
        fulltype = value.get("FullType")
        if fulltype != key or not has_text(fulltype):
            raise RoleRealignError(f"MISSING_OR_MISMATCHED_FULLTYPE: {key}")
        items[key] = value
    return dict(sorted(items.items()))


def index_rows(rows: Iterable[dict[str, Any]], field: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        key = row.get(field)
        if not has_text(key):
            raise RoleRealignError(f"{label}_MISSING_KEY")
        assert isinstance(key, str)
        if key in result:
            raise RoleRealignError(f"{label}_DUPLICATE_KEY: {key}")
        result[key] = row
    return result


def source_value_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def scalar_fact_id(item_id: str, source_slot: str, value: str, fact_origin: str) -> str:
    return "l3rf-" + canonical_sha256(
        {
            "item_id": item_id,
            "source_slot": source_slot,
            "source_value_hash": source_value_hash(value),
            "fact_origin": fact_origin,
        }
    )


def _cluster_lineage_state(fact: dict[str, Any], decision: dict[str, Any] | None) -> str:
    item_id = fact.get("item_id")
    if (
        decision
        and decision.get("item_id") == item_id
        and decision.get("facts_ref") == item_id
        and decision.get("state") == "adopted"
        and decision.get("cluster_used") is True
        and decision.get("use_source") == "cluster_summary"
    ):
        return "layer3_approval_bound"
    return "layer3_approval_unbound"


def _mapping_index(contract: dict[str, Any]) -> dict[tuple[str, str, str | None], dict[str, Any]]:
    result: dict[tuple[str, str, str | None], dict[str, Any]] = {}
    for row in contract.get("scalar_mappings", []):
        key = (row.get("source_slot"), row.get("fact_origin"), row.get("lineage_state"))
        if key in result:
            raise RoleRealignError(f"DUPLICATE_MAPPING_RULE: {key}")
        result[key] = row
    return result


def compose_fact_inventory(
    *,
    facts_by_item: dict[str, dict[str, Any]],
    decisions_by_item: dict[str, dict[str, Any]],
    mapping_contract: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    closed = set(mapping_contract.get("closed_fact_kinds", []))
    mapping_index = _mapping_index(mapping_contract)
    inventory: list[dict[str, Any]] = []
    observed: Counter[str] = Counter()
    unresolved: list[dict[str, Any]] = []

    for item_id in sorted(facts_by_item):
        fact = facts_by_item[item_id]
        origins_by_slot = fact.get("fact_origin") or {}
        if not isinstance(origins_by_slot, dict):
            raise RoleRealignError(f"INVALID_FACT_ORIGIN: {item_id}")
        for slot in SCALAR_SLOTS:
            value = fact.get(slot)
            if not has_text(value):
                continue
            assert isinstance(value, str)
            origins = origins_by_slot.get(slot)
            if not isinstance(origins, list) or not origins:
                origins = ["origin_missing"]
            for origin in origins:
                if not has_text(origin):
                    raise RoleRealignError(f"INVALID_FACT_ORIGIN_VALUE: {item_id}:{slot}")
                assert isinstance(origin, str)
                lineage_state = None
                if slot == "primary_use" and origin == "cluster_summary":
                    lineage_state = _cluster_lineage_state(
                        fact, decisions_by_item.get(item_id)
                    )
                mapping = mapping_index.get((slot, origin, lineage_state))
                if mapping is None:
                    mapping = mapping_index.get((slot, origin, None))
                observed_key = f"{slot}|{origin}|{lineage_state or '-'}"
                observed[observed_key] += 1
                if mapping is None:
                    unresolved.append(
                        {
                            "item_id": item_id,
                            "source_slot": slot,
                            "fact_origin": origin,
                            "lineage_state": lineage_state,
                        }
                    )
                    continue
                outcome = mapping.get("outcome")
                kind = mapping.get("fact_kind")
                if outcome not in {"eligible_kind", "not_eligible", "review_required"}:
                    raise RoleRealignError(f"UNKNOWN_MAPPING_OUTCOME: {mapping.get('rule_id')}")
                if outcome == "eligible_kind" and kind not in closed:
                    raise RoleRealignError(f"MAPPING_KIND_OUTSIDE_CLOSED_SET: {kind}")
                inventory.append(
                    {
                        "item_id": item_id,
                        "fact_id": scalar_fact_id(item_id, slot, value, origin),
                        "semantic_fact_key": canonical_sha256(
                            {
                                "fact_kind": kind,
                                "source_value_hash": source_value_hash(value),
                                "fact_origin": origin,
                            }
                        ),
                        "source_path": "Iris/build/description/v2/data/dvf_3_3_facts.jsonl",
                        "source_slot": slot,
                        "source_value": value.strip(),
                        "source_value_sha256": source_value_hash(value.strip()),
                        "fact_origin": origin,
                        "lineage_state": lineage_state,
                        "mapping_rule_id": mapping.get("rule_id"),
                        "mapping_outcome": outcome,
                        "fact_kind": kind,
                        "description_eligible": bool(mapping.get("description_eligible")),
                        "acquisition_eligible": bool(mapping.get("acquisition_eligible")),
                    }
                )

    coverage = {
        "schema_version": "iris-layer3-role-realign-mapping-coverage-v1",
        "observed_combinations": dict(sorted(observed.items())),
        "observed_combination_count": len(observed),
        "mapped_fact_count": len(inventory),
        "unresolved_mapping_count": len(unresolved),
        "unresolved_mappings": unresolved,
        "structured_lineage_observed_count": 0,
        "new_layer4_promotion_count": 0,
        "semantic_rendered_string_parsing_count": 0,
    }
    if unresolved:
        raise RoleRealignError(
            f"BLOCKED_MAPPING_CONTRACT: {len(unresolved)} unresolved source combinations"
        )
    return inventory, coverage


def load_ips_evidence(
    *,
    repository_root: Path,
    binding: dict[str, Any],
    current: CurrentGeneration,
    item_ids: set[str],
    facts_rows: list[dict[str, Any]],
    decisions_rows: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    file_checks: list[dict[str, Any]] = []
    missing_or_invalid = False
    for bound in binding.get("bound_files", []):
        path = repository_root / bound["path"]
        actual = raw_sha256(path) if path.is_file() else None
        matches = actual == bound.get("raw_byte_sha256")
        file_checks.append(
            {"path": bound["path"], "expected_sha256": bound.get("raw_byte_sha256"), "actual_sha256": actual, "matches": matches}
        )
        missing_or_invalid = missing_or_invalid or not matches

    page_path = repository_root / "Iris/build/description/v2/output/item_page_information_sufficiency/page_assessment.jsonl"
    summary_path = repository_root / "Iris/build/description/v2/output/item_page_information_sufficiency/assessment_summary.json"
    try:
        pages = load_jsonl(page_path)
        summary = load_json(summary_path)
        page_by_item = index_rows(pages, "fulltype", "IPS_PAGE")
    except RoleRealignError:
        pages = []
        summary = {}
        page_by_item = {}
        missing_or_invalid = True

    expected = binding.get("expected_result", {})
    disposition_counts = Counter(row.get("page_disposition") for row in pages)
    schema_ok = all(
        row.get("schema_version") == "iris-item-page-information-sufficiency-result-v1"
        and isinstance(row.get("layer3"), dict)
        for row in pages
    )
    result_hash_ok = raw_sha256(page_path) == expected.get("result_sha256") if page_path.is_file() else False
    key_set_ok = set(page_by_item) == item_ids
    count_ok = len(pages) == expected.get("denominator_count")
    disposition_ok = dict(sorted(disposition_counts.items())) == dict(
        sorted(expected.get("disposition_counts", {}).items())
    )
    missing_or_invalid = missing_or_invalid or not all(
        (schema_ok, result_hash_ok, key_set_ok, count_ok, disposition_ok)
    )

    summary_hashes = summary.get("input_hashes", {}) if isinstance(summary, dict) else {}
    descriptor = load_json(current.descriptor_path)
    current_checks = {
        "generation_id": all(
            row.get("input_identities", {}).get("generation_id") == current.generation_id
            for row in pages
        ) if pages else False,
        "layer3_rendered": summary_hashes.get("layer3_rendered") == raw_sha256(current.rendered_path),
        "layer3_pointer": summary_hashes.get("layer3_pointer") == raw_sha256(current.pointer_path),
        "layer3_descriptor": summary_hashes.get("layer3_descriptor") in {
            raw_sha256(current.descriptor_path), canonical_sha256(descriptor)
        },
        "layer3_facts": summary_hashes.get("layer3_facts") == canonical_jsonl_sha256(facts_rows),
        "layer3_decisions": summary_hashes.get("layer3_decisions") == canonical_jsonl_sha256(decisions_rows),
    }
    stale = not all(current_checks.values())
    if missing_or_invalid:
        evidence_status = "missing_or_invalid"
    elif stale:
        evidence_status = "stale_one_off_evidence"
    else:
        evidence_status = "current_snapshot"
    report = {
        "schema_version": "iris-layer3-role-realign-problem1-drift-v1",
        "evidence_status": evidence_status,
        "authority_effect": "none",
        "replay_required": False,
        "file_checks": file_checks,
        "page_row_count": len(pages),
        "page_key_set_matches_item_denominator": key_set_ok,
        "page_schema_valid": schema_ok,
        "page_result_sha256_matches": result_hash_ok,
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "current_input_checks": current_checks,
        "removed_evaluator_dependency_count": 0,
        "top_level_page_disposition_mapping_count": 0,
    }
    return page_by_item, report


def classify_readiness(
    facts: list[dict[str, Any]],
    ips_row: dict[str, Any] | None,
    evidence_status: str,
) -> tuple[str, list[str]]:
    if any(row["mapping_outcome"] == "review_required" for row in facts):
        return "review_required", ["mapping_contract_requires_review"]
    if evidence_status == "current_snapshot" and ips_row:
        layer3 = ips_row.get("layer3", {})
        requiredness = layer3.get("requiredness")
        representation = layer3.get("representation")
        if requiredness == "unresolved" or representation == "unresolved":
            return "review_required", ["one_off_layer3_axes_unresolved"]
    if any(row["description_eligible"] for row in facts):
        return "description_ready", ["confirmed_description_eligible_fact_present"]
    if any(row["acquisition_eligible"] for row in facts):
        return "acquisition_only", ["confirmed_acquisition_fact_without_description_material"]
    if evidence_status == "current_snapshot" and ips_row:
        layer3 = ips_row.get("layer3", {})
        requiredness = layer3.get("requiredness")
        if requiredness in {"optional", "not_required"}:
            return "omission_allowed", ["sealed_set_scoped_layer3_omission_prerequisite"]
        if requiredness == "required":
            return "insufficient_material", ["required_layer3_without_eligible_core_material"]
    return "insufficient_material", ["no_confirmed_description_or_acquisition_material"]


def compose_role_material(
    item_id: str,
    item_facts: list[dict[str, Any]],
    readiness: str,
    current_entry: dict[str, Any] | None,
) -> dict[str, Any]:
    description_facts = [row for row in item_facts if row["description_eligible"]]
    acquisition_facts = [row for row in item_facts if row["acquisition_eligible"]]
    core_description = None
    if readiness == "description_ready" and description_facts:
        core_description = " ".join(ensure_sentence(row["source_value"]) for row in description_facts)
    acquisition_information = (
        " ".join(ensure_sentence(row["source_value"]) for row in acquisition_facts)
        if acquisition_facts
        else None
    )
    emitted = set(((current_entry or {}).get("body_plan") or {}).get("emitted_section_names") or [])
    current_expressed_ids = [
        row["fact_id"] for row in acquisition_facts if "acquisition_support" in emitted
    ]
    menu_public_ids = list(current_expressed_ids)
    transformations: list[str] = []
    if acquisition_facts:
        transformations.append("separate_acquisition_role_v1")
    if description_facts:
        transformations.extend(
            [
                "remove_exact_identity_classification_repetition_v1",
                "place_confirmed_fact_frame_v1",
            ]
        )
    menu_acquisition = " ".join(
        ensure_sentence(row["source_value"])
        for row in acquisition_facts
        if row["fact_id"] in set(menu_public_ids)
    ) or None
    if readiness in {"review_required", "omission_allowed", "insufficient_material"}:
        menu_text = None
    elif core_description and menu_acquisition:
        menu_text = f"{core_description}\n\n획득 방법: {menu_acquisition}"
    elif core_description:
        menu_text = core_description
    elif menu_acquisition:
        menu_text = f"획득 방법: {menu_acquisition}"
    else:
        menu_text = None
    return {
        "item_id": item_id,
        "core_description": core_description,
        "acquisition_information": acquisition_information,
        "core_source_fact_ids": [row["fact_id"] for row in description_facts],
        "acquisition_source_fact_ids": [row["fact_id"] for row in acquisition_facts],
        "current_expressed_acquisition_fact_ids": current_expressed_ids,
        "menu_public_acquisition_fact_ids": menu_public_ids,
        "semantic_consumed_fact_set": sorted(
            row["semantic_fact_key"] for row in description_facts + [
                row for row in acquisition_facts if row["fact_id"] in set(menu_public_ids)
            ]
        ),
        "transformation_trace": transformations,
        "readiness_ref": readiness,
        "menu_text_ko": menu_text,
        "tooltip_input_ready": bool(core_description or acquisition_information),
    }


def classify_disposition(
    *, current_text: str, material: dict[str, Any], item_facts: list[dict[str, Any]]
) -> tuple[str, list[str]]:
    if any(row["mapping_outcome"] == "review_required" for row in item_facts):
        return "review_hold", ["mapping_contract_requires_review"]
    candidate = material.get("menu_text_ko")
    if not has_text(candidate):
        return "hide", ["no_publicly_eligible_role_material"]
    if candidate == current_text:
        return "keep", ["candidate_byte_equal_to_current_body"]
    if material.get("core_description") is None and material.get("acquisition_information"):
        return "reduce", ["acquisition_only_role_projection"]
    return "revise", ["registered_role_separation_or_fact_frame"]


def duplicate_assessment(material_rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in material_rows:
        if has_text(row.get("menu_text_ko")):
            groups[row["menu_text_ko"]].append(row)
    duplicate_groups = [rows for rows in groups.values() if len(rows) > 1]
    differing: list[dict[str, Any]] = []
    for rows in duplicate_groups:
        semantic_sets = {
            canonical_sha256(row["semantic_consumed_fact_set"]) for row in rows
        }
        if len(semantic_sets) > 1:
            differing.append(
                {
                    "text_sha256": hashlib.sha256(rows[0]["menu_text_ko"].encode("utf-8")).hexdigest(),
                    "item_ids": sorted(row["item_id"] for row in rows),
                    "semantic_set_count": len(semantic_sets),
                }
            )
    return {
        "exact_duplicate_group_count": len(duplicate_groups),
        "exact_duplicate_row_count": sum(len(rows) for rows in duplicate_groups),
        "differing_semantic_fact_set_blocking_count": len(differing),
        "differing_semantic_fact_set_findings": differing,
        "registered_bad_duplicate_count": 0,
        "registered_bad_skeleton_count": 0,
        "registered_awkward_expression_count": 0,
        "unregistered_frequency_signal_is_blocking": False,
    }


def build_successor_rendered(
    *, current_rendered: dict[str, Any], material_by_item: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    current_entries = current_rendered.get("entries", {})
    if not isinstance(current_entries, dict):
        raise RoleRealignError("CURRENT_RENDERED_ENTRIES_NOT_OBJECT")
    entries: dict[str, Any] = {}
    emitted = 0
    for item_id in sorted(current_entries):
        material = material_by_item[item_id]
        text = material.get("menu_text_ko")
        if has_text(text):
            emitted += 1
        entries[item_id] = {
            "text_ko": text,
            "source": "layer3_role_realign_staging_v1" if has_text(text) else "layer3_role_realign_silent_v1",
            "role_material": {
                "core_source_fact_ids": material["core_source_fact_ids"],
                "acquisition_source_fact_ids": material["acquisition_source_fact_ids"],
                "menu_public_acquisition_fact_ids": material["menu_public_acquisition_fact_ids"],
            },
        }
    entries_hash = canonical_sha256(entries)
    return {
        "meta": {
            "version": "iris-layer3-role-realign-staging-rendered-v1",
            "generated_at": "content-derived-generation",
            "entries_sha256": entries_hash,
            "stats": {"total": len(entries), "candidate_emitted": emitted, "silent": len(entries) - emitted},
            "authority_effect": "none",
            "installation_status": "off_live",
        },
        "entries": entries,
    }
