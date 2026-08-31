"""Optional source-bound composition within the offline Body Compiler.

Material is approved upstream; this module neither reads game scripts nor
derives membership, conditions or facts from names, classifications or prose.
The seven canonical inputs carry declarations, material and explicit routing.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from string import Formatter
from typing import Any

from .compose_layer3_io import entries_sha256, file_sha256, load_json, load_jsonl

SCHEMA = "layer3-shared-composition-v1"
LOCALES = {"ko", "en"}
RETAIN_REASONS = {"already_adequate", "source_gap", "protected", "source_hold", "empty_core"}


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def fail(code: str, item: str) -> None:
    raise ValueError(f"LAYER3_COMPOSITION_{code}:{item}")


def localized(value: Any, item: str) -> dict[str, str]:
    if (not isinstance(value, dict) or set(value) != LOCALES
            or any(not isinstance(v, str) or not v.strip() or any(c in v for c in "\r\n{}")
                   for v in value.values())):
        fail("LOCALE_INVALID", item)
    return value


def parameters(template: str, item: str) -> set[str]:
    result = set()
    try:
        for _, field, spec, conversion in Formatter().parse(template):
            if field is not None:
                if not field.isidentifier() or spec or conversion:
                    fail("TEMPLATE_INVALID", item)
                result.add(field)
    except (ValueError, AttributeError):
        fail("TEMPLATE_INVALID", item)
    return result


def render_block(block: Any, values: dict[str, dict[str, str]], item: str) -> tuple[dict[str, str], set[str]]:
    if not isinstance(block, dict) or set(block) != LOCALES:
        fail("LOCALE_INVALID", item)
    slots = {locale: parameters(block[locale], item) for locale in sorted(LOCALES)}
    if slots["ko"] != slots["en"]:
        fail("LOCALE_CLAIM_MISMATCH", item)
    if not slots["ko"].issubset(values):
        fail("MISSING_BINDING", item)
    rendered = {locale: block[locale].format_map({k: v[locale] for k, v in values.items()})
                for locale in sorted(LOCALES)}
    return localized(rendered, item), slots["ko"]


def compose_item_shared(*, item_id: str, facts: dict, current_entry: dict,
                        binding: dict, definitions: dict) -> dict:
    mode = binding.get("mode")
    if mode == "retained":
        if binding.get("reason") not in RETAIN_REASONS or digest(current_entry) != binding.get("entry_sha256"):
            fail("RETENTION_MISMATCH", item_id)
        return deepcopy(current_entry)
    if mode not in {"shared", "explicit"}:
        fail("MODE_INVALID", item_id)
    material = facts.get("slot_meta", {}).get("body_material")
    if (not isinstance(material, dict) or material.get("schema_version") != SCHEMA
            or material.get("approval") != "owner_preapproved_source_bound_material"
            or not material.get("authority_ref")
            or digest(material) != binding.get("material_sha256")):
        fail("MATERIAL_INVALID", item_id)
    core_ids = current_entry.get("role_material", {}).get("core_source_fact_ids")
    if not isinstance(core_ids, list) or len(core_ids) != 1 or core_ids != [material.get("core_fact_id")]:
        fail("SINGLE_CORE_REQUIRED", item_id)
    source_slots = material.get("source_slots")
    if not isinstance(source_slots, dict) or "primary_use" not in source_slots:
        fail("SOURCE_BINDING_MISSING", item_id)
    for slot, expected in source_slots.items():
        if digest(facts.get(slot)) != expected:
            fail("SOURCE_STALE", item_id)
    origins = facts.get("fact_origin", {}).get("primary_use", [])
    source_ids = ["l3rf-" + digest({"item_id": item_id, "source_slot": "primary_use",
                  "source_value_hash": hashlib.sha256(facts["primary_use"].encode("utf-8")).hexdigest(),
                  "fact_origin": origin}) for origin in origins]
    if core_ids[0] not in source_ids:
        fail("SOURCE_ID_MISMATCH", item_id)
    refs = material.get("source_refs")
    if (not isinstance(refs, list) or not refs
            or any(not isinstance(ref, dict) or not ref.get("path") or not ref.get("locator")
                   or len(ref.get("sha256", "")) != 64 for ref in refs)):
        fail("SOURCE_REFERENCE_MISSING", item_id)
    values = material.get("values")
    if not isinstance(values, dict) or not values:
        fail("MISSING_BINDING", item_id)
    for value in values.values():
        localized(value, item_id)
    if mode == "shared":
        definition = definitions.get(binding.get("composition_id"))
        if not isinstance(definition, dict):
            fail("UNKNOWN_COMPOSITION", item_id)
    else:
        definition = binding.get("expression")
        if not isinstance(definition, dict) or not binding.get("exception_reason"):
            fail("EXCEPTION_INVALID", item_id)
    conditions = material.get("condition_parameters")
    effects = material.get("effect_parameters")
    if (not isinstance(conditions, list) or not isinstance(effects, list) or not effects
            or len(set(conditions)) != len(conditions) or len(set(effects)) != len(effects)):
        fail("CLAIM_BINDING_INVALID", item_id)
    core, core_slots = render_block(definition.get("core"), values, item_id)
    if not set(conditions + effects).issubset(core_slots):
        fail("REQUIRED_CORE_CLAIM_MISSING", item_id)
    menu_blocks = definition.get("menu_blocks", {})
    selected = binding.get("menu_blocks", [])
    if (not isinstance(menu_blocks, dict) or not isinstance(selected, list)
            or len(set(selected)) != len(selected) or not set(selected).issubset(menu_blocks)):
        fail("OPTIONAL_BLOCK_INVALID", item_id)
    body = dict(core)
    used = set(core_slots)
    for block_id in selected:
        block, slots = render_block(menu_blocks[block_id], values, item_id)
        used.update(slots)
        for locale in sorted(LOCALES):
            body[locale] += " " + block[locale]
    if used != set(values):
        fail("UNUSED_BINDING", item_id)
    for detail in binding.get("retained_details", []):
        slot = detail.get("source_slot")
        if slot not in source_slots or digest(facts.get(slot)) != detail.get("source_sha256"):
            fail("DETAIL_SOURCE_MISMATCH", item_id)
        surface = localized(detail.get("localized_surfaces"), item_id)
        # These are source-slot surfaces, never a substring of a rendered body.
        if surface["ko"].rstrip(".") != str(facts[slot]).rstrip("."):
            fail("DETAIL_SOURCE_MISMATCH", item_id)
        separator = "\n\n" if slot == "acquisition_hint" else " "
        for locale in sorted(LOCALES):
            prefix = "획득 방법: " if slot == "acquisition_hint" and locale == "ko" else ""
            body[locale] += separator + prefix + surface[locale]
    result = deepcopy(current_entry)
    result["text_ko"] = body["ko"]
    result["body_composition"] = {
        "schema_version": SCHEMA, "mode": mode,
        "composition_id": binding.get("composition_id"),
        "material_sha256": digest(material), "binding_sha256": digest(binding),
        "core_fact_id": core_ids[0], "core": core, "menu": body,
    }
    return result


def compose_shared_candidate(*, facts_list: list[dict], overlay_list: list[dict],
                             profiles: dict, predecessor: dict) -> dict:
    def index(rows: list[dict]) -> dict:
        result = {}
        for row in rows:
            key = row.get("item_id")
            if not isinstance(key, str) or key in result:
                fail("DUPLICATE_OR_INVALID_KEY", str(key))
            result[key] = row
        return result
    facts = index(facts_list)
    overlay = index(overlay_list)
    entries = predecessor.get("entries")
    if not isinstance(entries, dict) or set(entries) != set(facts) or set(entries) != set(overlay):
        fail("UNIVERSE_MISMATCH", "candidate")
    contract = profiles.get("shared_composition")
    if not isinstance(contract, dict) or contract.get("schema_version") != SCHEMA:
        fail("SCHEMA_INVALID", "profiles")
    result = deepcopy(predecessor)
    for key in sorted(entries):
        binding = overlay[key].get("body_composition")
        if not isinstance(binding, dict):
            fail("ROUTE_MISSING", key)
        result["entries"][key] = compose_item_shared(item_id=key, facts=facts[key],
            current_entry=entries[key], binding=binding, definitions=contract["definitions"])
    result["meta"]["entries_sha256"] = entries_sha256(result["entries"])
    result["meta"]["shared_composition"] = {
        "schema_version": SCHEMA,
        "inputs_sha256": {"facts": digest(facts), "overlay": digest(overlay), "profiles": digest(profiles)},
        "approval": "owner_preapproval_for_candidate_adoption",
        "approval_ref": contract["authority_ref"],
        "human_observation": "not_performed",
    }
    return result


def approved_compositions(repository_root: Path, rendered: dict) -> dict:
    """Read generation-bound bilingual outputs; never silently fall back."""
    from .dvf_3_3_generation_contract import CANONICAL_INPUTS, repository_path
    candidate = load_json(repository_path(repository_root, CANONICAL_INPUTS[6]))
    adoption = candidate.get("meta", {}).get("shared_composition")
    if adoption is None:
        if any("body_composition" in row for row in rendered.values()):
            fail("ADOPTION_MISSING", "candidate")
        return {}
    if (adoption.get("schema_version") != SCHEMA
            or adoption.get("approval") != "owner_preapproval_for_candidate_adoption"
            or not adoption.get("approval_ref")):
        fail("ADOPTION_INVALID", "candidate")
    facts = load_jsonl(repository_path(repository_root, CANONICAL_INPUTS[0]))
    overlay = load_jsonl(repository_path(repository_root, CANONICAL_INPUTS[2]))
    profiles = load_json(repository_path(repository_root, CANONICAL_INPUTS[3]))
    expected = {"facts": digest({row["item_id"]: row for row in facts}),
                "overlay": digest({row["item_id"]: row for row in overlay}), "profiles": digest(profiles)}
    if adoption.get("inputs_sha256") != expected:
        fail("INPUT_STALE", "candidate")
    recomposed = compose_shared_candidate(facts_list=facts, overlay_list=overlay,
        profiles=profiles, predecessor=candidate)
    if recomposed["entries"] != rendered:
        fail("OUTPUT_MISMATCH", "candidate")
    return {key: row["body_composition"] for key, row in rendered.items() if "body_composition" in row}


def build_shared_candidate(repository_root: Path, output_path: Path) -> dict:
    from .dvf_3_3_generation_contract import CANONICAL_INPUTS, ensure_external_generation_root, repository_path
    output_path = output_path.resolve()
    ensure_external_generation_root(repository_root, output_path)
    if output_path.exists():
        fail("OUTPUT_EXISTS", str(output_path))
    paths = [repository_path(repository_root, relative) for relative in CANONICAL_INPUTS]
    result = compose_shared_candidate(facts_list=load_jsonl(paths[0]), overlay_list=load_jsonl(paths[2]),
                                      profiles=load_json(paths[3]), predecessor=load_json(paths[6]))
    # Existing bilingual context adoption still refers to the same source slots.
    if "general_description_integration" in result["meta"]:
        result["meta"]["general_description_integration"]["facts_sha256"] = file_sha256(paths[0])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8", newline="\n")
    return {"status": "BUILT_NOT_ADOPTED", "output": str(output_path), "sha256": file_sha256(output_path),
            "entries": len(result["entries"])}
