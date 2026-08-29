from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
from pathlib import Path
import sys
import unicodedata
from typing import Any

from iris_tooling.build.repository_context import require_repository_context
from iris_tooling.domains.tooltip_t1.contract import (
    canonical_bytes,
    load_json,
    sha256_bytes,
    sha256_file,
)
from iris_tooling.domains.tooltip_t1.models import TooltipContractError
from iris_tooling.domains.tooltip_t1.projection import Layer4Candidate, select_layer4


IDENTITY_OWNER_INPUT = Path("Iris/build/description/v2/data/upstream_usecases_by_fulltype.json")
REGISTRY_SCHEMA = Path(
    "Iris/_docs/authority/qg/tooltip_t1_d4_recipe_locale_surface_registry.schema.json"
)
REGISTRY = Path(
    "Iris/_docs/authority/qg/tooltip_t1_d4_recipe_locale_surface_registry.json"
)
OWNER_OUTPUT = Path(
    "Iris/build/description/v2/data/tooltip_t1_layer4_recipe_locale_owner_input.json"
)
SUPPORTED_LOCALES = ("ko", "en")
CANONICAL_FACT_ID = "qg.recipe_participation.v1"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise TooltipContractError(message)


def _selected_recipe_evidence(repository_root: Path) -> dict[str, dict[str, Any]]:
    owner = load_json(repository_root / IDENTITY_OWNER_INPUT)
    fulltypes = owner.get("fulltypes")
    _require(isinstance(fulltypes, dict), "Layer 4 identity owner input has no fulltypes")
    selected_by_identity: dict[str, dict[str, Any]] = {}
    for full_type, row in sorted(fulltypes.items()):
        _require(isinstance(full_type, str) and full_type, "Layer 4 FullType is invalid")
        _require(isinstance(row, dict), f"{full_type}: Layer 4 owner row must be an object")
        use_cases = row.get("use_cases") or []
        _require(isinstance(use_cases, list), f"{full_type}: use_cases must be an array")
        by_identity: dict[str, dict[str, Any]] = {}
        candidates: list[Layer4Candidate] = []
        for use_case in use_cases:
            _require(isinstance(use_case, dict), f"{full_type}: use-case row must be an object")
            identity = use_case.get("use_case_id")
            identity = identity if isinstance(identity, str) else ""
            surface = use_case.get("surface")
            source = (
                "recipe"
                if surface == "recipe_ui"
                else "rightclick"
                if surface == "context_menu"
                else str(surface)
            )
            if source == "recipe" and "display_by_locale" in use_case:
                raise TooltipContractError(
                    f"{full_type}/{identity}: LAYER4_RECIPE_EMBEDDED_LOCALE_AUTHORITY_CEILING_VIOLATION"
                )
            candidates.append(
                Layer4Candidate(
                    interaction_id=identity,
                    source=source,
                    public_state="public",
                    line_kind=str(use_case.get("line_kind") or "unknown"),
                    requirement_only=bool(use_case.get("requirement_only", False)),
                    stable_order_key=use_case.get("stable_order_key"),
                )
            )
            by_identity.setdefault(identity, use_case)
        selected, _ = select_layer4(candidates)
        for index, candidate in enumerate(selected):
            if candidate.source != "recipe":
                continue
            source_row = by_identity.get(candidate.interaction_id)
            _require(isinstance(source_row, dict), f"{full_type}: selected Recipe evidence row missing")
            evidence_sources = source_row.get("evidence_sources")
            _require(
                isinstance(evidence_sources, list) and bool(evidence_sources),
                f"{full_type}/{candidate.interaction_id}: Recipe evidence sources missing",
            )
            relations: list[dict[str, str]] = []
            for evidence in evidence_sources:
                _require(isinstance(evidence, dict), "Recipe evidence relation must be an object")
                if evidence.get("source_type") != "recipe_evidence":
                    continue
                relation = {
                    "source_type": "recipe_evidence",
                    "rule_id": str(evidence.get("rule_id") or ""),
                    "decision": str(evidence.get("decision") or ""),
                    "role": str(evidence.get("role") or ""),
                }
                _require(
                    bool(relation["rule_id"])
                    and relation["decision"] == "PASS"
                    and relation["role"] in {"consume", "keep"},
                    f"{full_type}/{candidate.interaction_id}: inadmissible Recipe evidence relation",
                )
                relations.append(relation)
            _require(bool(relations), f"{full_type}/{candidate.interaction_id}: no PASS Recipe evidence")
            record = selected_by_identity.setdefault(
                candidate.interaction_id,
                {"interaction_id": candidate.interaction_id, "selected_instances": []},
            )
            record["selected_instances"].append(
                {
                    "full_type": full_type,
                    "slot_id": ("S3", "S4")[index],
                    "relations": sorted(
                        relations,
                        key=lambda value: (
                            value["source_type"],
                            value["rule_id"],
                            value["decision"],
                            value["role"],
                        ),
                    ),
                }
            )
    for record in selected_by_identity.values():
        record["selected_instances"].sort(
            key=lambda value: (value["full_type"], value["slot_id"])
        )
    return dict(sorted(selected_by_identity.items()))


def _semantic_refs(instances: list[dict[str, Any]]) -> list[dict[str, str]]:
    refs = {
        (
            relation["source_type"],
            relation["rule_id"],
            relation["decision"],
        )
        for instance in instances
        for relation in instance["relations"]
    }
    return [
        {"source_type": source_type, "rule_id": rule_id, "decision": decision}
        for source_type, rule_id, decision in sorted(refs)
    ]


def selected_recipe_evidence(repository_root: Path) -> dict[str, dict[str, Any]]:
    return _selected_recipe_evidence(repository_root.resolve())


def selected_identity_sha256(selected: dict[str, dict[str, Any]]) -> str:
    return sha256_bytes(canonical_bytes(list(selected)))


def selected_instance_sha256(selected: dict[str, dict[str, Any]]) -> str:
    rows = [
        {"interaction_id": identity, "selected_instances": record["selected_instances"]}
        for identity, record in selected.items()
    ]
    return sha256_bytes(canonical_bytes(rows))


def validate_registry(
    repository_root: Path,
    registry: dict[str, Any] | None = None,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    root = repository_root.resolve()
    value = registry if registry is not None else load_json(root / REGISTRY)
    _require(
        set(value)
        == {
            "schema_version",
            "status",
            "owner",
            "approval_ref",
            "subject_binding",
            "surface_policy",
            "records",
        },
        "D4 Recipe locale registry root fields mismatch",
    )
    _require(
        value.get("schema_version") == "iris-tooltip-t1-d4-recipe-locale-registry-v1",
        "D4 Recipe locale registry schema version mismatch",
    )
    _require(value.get("status") == "owner_approved", "D4 Recipe locale registry is not approved")
    _require(value.get("owner") == "QG/locale owner", "D4 Recipe locale registry owner mismatch")
    _require(
        isinstance(value.get("approval_ref"), str) and bool(value["approval_ref"]),
        "D4 Recipe locale registry approval reference missing",
    )
    binding = value.get("subject_binding")
    _require(isinstance(binding, dict), "D4 Recipe locale registry subject binding missing")
    _require(
        binding.get("predecessor_commit")
        == "6b7118dc229bf8138302696e1aa5e5b7454589dc"
        and binding.get("predecessor_tree")
        == "4eae6fbdb3d0b2cb532f875b96137335a403f2fc",
        "D4 Recipe locale registry predecessor mismatch",
    )
    identity_sha256 = sha256_file(root / IDENTITY_OWNER_INPUT)
    _require(
        binding.get("identity_owner_input") == IDENTITY_OWNER_INPUT.as_posix()
        and binding.get("identity_owner_input_sha256") == identity_sha256,
        "D4 Recipe locale registry identity input binding mismatch",
    )
    policy = value.get("surface_policy")
    _require(
        isinstance(policy, dict)
        and policy.get("canonical_fact_id") == CANONICAL_FACT_ID
        and policy.get("supported_locales") == list(SUPPORTED_LOCALES)
        and policy.get("cross_locale_fallback_allowed") is False
        and policy.get("numeric_width_gate") is None,
        "D4 Recipe locale registry surface policy mismatch",
    )
    records = value.get("records")
    _require(isinstance(records, list), "D4 Recipe locale registry records missing")
    selected = _selected_recipe_evidence(root)
    _require(
        [row.get("interaction_id") for row in records if isinstance(row, dict)]
        == list(selected),
        "D4 Recipe locale registry exact selected identity set/order mismatch",
    )
    validated: dict[str, dict[str, Any]] = {}
    forbidden = {"추천", "최고", "recommended", "best"}
    required_fields = {
        "interaction_id",
        "canonical_fact_id",
        "canonical_semantic_refs",
        "selected_instance_evidence_sha256",
        "selected_instances",
        "localized_surfaces",
        "approval_ref",
        "provenance",
    }
    for row in records:
        _require(isinstance(row, dict) and set(row) == required_fields, "D4 registry record fields mismatch")
        identity = row["interaction_id"]
        expected = selected.get(identity)
        _require(isinstance(expected, dict), f"{identity}: registry identity is not selected")
        instances = expected["selected_instances"]
        _require(row.get("canonical_fact_id") == CANONICAL_FACT_ID, f"{identity}: canonical fact mismatch")
        _require(row.get("canonical_semantic_refs") == _semantic_refs(instances), f"{identity}: semantic refs mismatch")
        _require(row.get("selected_instances") == instances, f"{identity}: selected instance relation mismatch")
        expected_digest = sha256_bytes(
            canonical_bytes({"interaction_id": identity, "selected_instances": instances})
        )
        _require(
            row.get("selected_instance_evidence_sha256") == expected_digest,
            f"{identity}: selected instance evidence digest mismatch",
        )
        surfaces = row.get("localized_surfaces")
        _require(
            isinstance(surfaces, dict) and set(surfaces) == set(SUPPORTED_LOCALES),
            f"{identity}: locale set mismatch",
        )
        for locale in SUPPORTED_LOCALES:
            text = surfaces[locale]
            _require(
                isinstance(text, str)
                and bool(text.strip())
                and "\r" not in text
                and "\n" not in text
                and unicodedata.normalize("NFC", text) == text,
                f"{identity}/{locale}: surface must be non-empty NFC single-line text",
            )
            comparable = text if locale == "ko" else text.lower()
            _require(
                not any(token in comparable for token in forbidden),
                f"{identity}/{locale}: forbidden recommendation expression",
            )
        _require(row.get("approval_ref") == value["approval_ref"], f"{identity}: approval ref mismatch")
        provenance = row.get("provenance")
        _require(
            isinstance(provenance, dict)
            and provenance.get("identity_owner_input") == IDENTITY_OWNER_INPUT.as_posix()
            and provenance.get("identity_owner_input_sha256") == identity_sha256,
            f"{identity}: provenance mismatch",
        )
        validated[identity] = row
    return selected, validated


def build_owner_projection(repository_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    selected, records = validate_registry(root)
    registry_sha256 = sha256_file(root / REGISTRY)
    schema_sha256 = sha256_file(root / REGISTRY_SCHEMA)
    identity_sha256 = sha256_file(root / IDENTITY_OWNER_INPUT)
    return {
        "schema_version": "iris-tooltip-t1-layer4-recipe-locale-owner-input-v1",
        "source": "recipe",
        "supported_locales": list(SUPPORTED_LOCALES),
        "selection_stage": "post_selected_identity_freeze",
        "fallback_allowed": False,
        "source_substitution_allowed": False,
        "subject_binding": {
            "predecessor_commit": "6b7118dc229bf8138302696e1aa5e5b7454589dc",
            "predecessor_tree": "4eae6fbdb3d0b2cb532f875b96137335a403f2fc",
            "identity_owner_input": IDENTITY_OWNER_INPUT.as_posix(),
            "identity_owner_input_sha256": identity_sha256,
            "registry": REGISTRY.as_posix(),
            "registry_sha256": registry_sha256,
            "registry_schema": REGISTRY_SCHEMA.as_posix(),
            "registry_schema_sha256": schema_sha256,
            "selected_identity_sha256": selected_identity_sha256(selected),
            "selected_instance_sha256": selected_instance_sha256(selected),
        },
        "entry_count": len(records),
        "entries": {
            identity: {
                "canonical_fact_id": row["canonical_fact_id"],
                "canonical_semantic_refs": row["canonical_semantic_refs"],
                "localized_surfaces": row["localized_surfaces"],
                "authority_ref": f"{REGISTRY.as_posix()}#records/{index}",
                "approval_ref": row["approval_ref"],
            }
            for index, (identity, row) in enumerate(records.items())
        },
    }


def load_recipe_locale_owner_input(repository_root: Path) -> dict[str, dict[str, Any]]:
    root = repository_root.resolve()
    expected = build_owner_projection(root)
    actual = load_json(root / OWNER_OUTPUT)
    _require(actual == expected, "Recipe locale owner projection is not canonical for the approved registry")
    entries = actual.get("entries")
    _require(isinstance(entries, dict), "Recipe locale owner projection entries missing")
    return entries


def materialize(repository_root: Path, output_root: Path) -> dict[str, Any]:
    root = repository_root.resolve()
    output = output_root.resolve()
    _require(root != output and root not in output.parents, "D4 output root must be repository-external")
    if output.exists():
        _require(output.is_dir() and not any(output.iterdir()), "D4 output root must be empty")
    else:
        output.mkdir(parents=True)
    projection = build_owner_projection(root)
    output_path = output / OWNER_OUTPUT.name
    output_path.write_bytes(canonical_bytes(projection))
    receipt = {
        "schema_version": "iris-tooltip-t1-d4-materialization-receipt-v1",
        "output": output_path.name,
        "output_sha256": sha256_file(output_path),
        "registry_sha256": sha256_file(root / REGISTRY),
        "identity_owner_input_sha256": sha256_file(root / IDENTITY_OWNER_INPUT),
        "entry_count": projection["entry_count"],
        "selected_identity_sha256": projection["subject_binding"]["selected_identity_sha256"],
        "selected_instance_sha256": projection["subject_binding"]["selected_instance_sha256"],
    }
    receipt_path = output / "materialization_receipt.json"
    receipt_path.write_bytes(canonical_bytes(receipt))
    return {**receipt, "receipt_sha256": sha256_file(receipt_path)}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="iris-tooling build layer4 tooltip-t1-d4")
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args(list(argv or ()))
    try:
        result = materialize(require_repository_context().repository_root, args.output_root)
    except (OSError, TooltipContractError) as exc:
        print(f"layer4 tooltip-t1-d4 blocked: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0
