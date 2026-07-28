from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"invalid facts JSONL at line {line_number}: {path}"
                    ) from exc
    return rows


def _canonical_jsonl_bytes(rows):
    return "".join(
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in rows
    ).encode("utf-8")


def _member_set_sha256(members):
    return hashlib.sha256(
        "".join(f"{member}\n" for member in sorted(members)).encode("utf-8")
    ).hexdigest()


# BEGIN DVF FOOD SEMANTIC CANDIDATE PATCH (D16 adoption required)
def build_food_semantic_proposition_inventory(
    facts_rows,
    *,
    schema_sha256,
    proposition_license_sha256,
):
    """Project approved structured assertions without inventing propositions."""
    inventory = []
    for facts in facts_rows:
        for assertion in facts.get("food_semantic_assertions", []):
            if assertion.get("authority_state") not in {
                "approved",
                "owner_approved",
            }:
                continue
            inventory.append(
                {
                    "item_id": facts["item_id"],
                    "proposition_id": assertion["proposition_id"],
                    "fact_axis": assertion["fact_axis"],
                    "fact_value": assertion["fact_value"],
                    "authority_class": assertion["authority_class"],
                    "source_or_approval_lineage_id": assertion["lineage_id"],
                    "schema_sha256": schema_sha256,
                    "proposition_license_sha256": proposition_license_sha256,
                }
            )
    return sorted(
        inventory,
        key=lambda row: (
            row["item_id"],
            row["fact_axis"],
            row["fact_value"],
            row["proposition_id"],
        ),
    )


def consume_food_semantic_inputs_no_render(
    *,
    facts_path,
    manifest_path,
    schema_path,
    proposition_license_path,
    explicit_non_current_input_override,
    repository_root=None,
    facts_sha256=None,
    manifest_sha256=None,
    schema_sha256=None,
    proposition_license_sha256=None,
):
    """Open all Phase 2 inputs and return their computed no-render identities."""
    if explicit_non_current_input_override is not True:
        raise ValueError("Branch B requires an explicit non-current input override")
    paths = {
        "facts": Path(facts_path).resolve(),
        "manifest": Path(manifest_path).resolve(),
        "schema": Path(schema_path).resolve(),
        "proposition_license": Path(proposition_license_path).resolve(),
    }
    computed = {
        f"{name}_sha256": _sha256_file(path) for name, path in paths.items()
    }
    supplied = {
        "facts_sha256": facts_sha256,
        "manifest_sha256": manifest_sha256,
        "schema_sha256": schema_sha256,
        "proposition_license_sha256": proposition_license_sha256,
    }
    supplied_mismatches = [
        field
        for field, value in supplied.items()
        if value is not None and value != computed[field]
    ]
    if supplied_mismatches:
        raise ValueError(
            "caller-supplied input identity mismatch: "
            + ",".join(sorted(supplied_mismatches))
        )
    facts_rows = _load_jsonl(paths["facts"])
    with paths["manifest"].open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    with paths["schema"].open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    with paths["proposition_license"].open("r", encoding="utf-8") as handle:
        proposition_license = json.load(handle)
    manifest_declared_facts_sha256 = manifest.get("facts", {}).get("sha256")
    if manifest_declared_facts_sha256 != computed["facts_sha256"]:
        raise ValueError("manifest facts SHA-256 does not match opened facts")
    manifest_declared_facts_path = manifest.get("facts", {}).get("path")
    if not manifest_declared_facts_path:
        raise ValueError("manifest lacks the selected facts path")
    declared_path = Path(manifest_declared_facts_path)
    if not declared_path.is_absolute():
        declared_path = Path(repository_root or Path.cwd()) / declared_path
    manifest_facts_path_match = (
        declared_path.resolve() == paths["facts"]
    )
    if not manifest_facts_path_match:
        raise ValueError("manifest facts path does not match opened facts")
    food_authority = manifest.get("food_semantic_authority", {})
    for field, expected_value in (
        ("schema_sha256", computed["schema_sha256"]),
        (
            "proposition_license_sha256",
            computed["proposition_license_sha256"],
        ),
    ):
        if food_authority.get(field) != expected_value:
            raise ValueError(f"manifest food authority {field} mismatch")
    inventory = build_food_semantic_proposition_inventory(
        facts_rows,
        schema_sha256=computed["schema_sha256"],
        proposition_license_sha256=computed[
            "proposition_license_sha256"
        ],
    )
    inventory_bytes = _canonical_jsonl_bytes(inventory)
    allowed_values = {
        axis["axis"]: {value["value"] for value in axis["values"]}
        for axis in schema["axes"]
    }
    required_axes = sorted(
        axis["axis"]
        for axis in schema["axes"]
        if axis["cardinality"] == "one_or_more"
    )
    license_index = {
        (row["fact_axis"], row["fact_value"]): row
        for row in proposition_license["licenses"]
    }
    invalid_schema_count = 0
    invalid_license_count = 0
    proposition_ids = []
    axes_by_item = {}
    profiles_by_item = {}
    for row in inventory:
        proposition_ids.append(row["proposition_id"])
        axes_by_item.setdefault(row["item_id"], set()).add(row["fact_axis"])
        profiles_by_item.setdefault(row["item_id"], []).append(
            (row["fact_axis"], row["fact_value"])
        )
        if row["fact_value"] not in allowed_values.get(row["fact_axis"], set()):
            invalid_schema_count += 1
        license_row = license_index.get((row["fact_axis"], row["fact_value"]))
        if license_row is None or (
            row["authority_class"] == "automatic"
            and license_row.get("automatic_eligible") is not True
        ) or (
            row["authority_class"] == "curated"
            and license_row.get("curated_allowed") is not True
        ):
            invalid_license_count += 1
    projected_members = set(axes_by_item)
    required_axis_missing = {
        item_id: sorted(set(required_axes) - axes)
        for item_id, axes in sorted(axes_by_item.items())
        if set(required_axes) - axes
    }
    meaningful_profiles = {
        tuple(sorted(profile)) for profile in profiles_by_item.values()
    }
    receipt = {
        "producer": "naturalization_actual_phase2_consumer",
        "facts_path": str(paths["facts"]),
        "facts_sha256": computed["facts_sha256"],
        "manifest_path": str(paths["manifest"]),
        "manifest_sha256": computed["manifest_sha256"],
        "schema_path": str(paths["schema"]),
        "schema_sha256": computed["schema_sha256"],
        "proposition_license_path": str(paths["proposition_license"]),
        "proposition_license_sha256": computed[
            "proposition_license_sha256"
        ],
        "manifest_declared_facts_sha256": manifest_declared_facts_sha256,
        "manifest_declared_facts_path": manifest_declared_facts_path,
        "manifest_facts_sha256_match": True,
        "manifest_facts_path_match": True,
        "opened_input_count": 4,
        "facts_row_count": len(facts_rows),
        "food_semantic_proposition_count": len(inventory),
        "food_semantic_proposition_inventory_sha256": hashlib.sha256(
            inventory_bytes
        ).hexdigest(),
        "food_semantic_item_count": len(projected_members),
        "food_semantic_item_set_sha256": _member_set_sha256(
            projected_members
        ),
        "required_fact_axes": required_axes,
        "required_axis_missing_item_count": len(required_axis_missing),
        "required_axis_missing_by_item": required_axis_missing,
        "duplicate_proposition_id_count": (
            len(proposition_ids) - len(set(proposition_ids))
        ),
        "invalid_schema_proposition_count": invalid_schema_count,
        "invalid_license_proposition_count": invalid_license_count,
        "meaningful_partition_count": len(meaningful_profiles),
        "manifest_declared_food_semantic_item_count": food_authority.get(
            "target_member_count"
        ),
        "manifest_declared_food_semantic_item_set_sha256": food_authority.get(
            "target_member_set_sha256"
        ),
        "manifest_declared_required_fact_axes": food_authority.get(
            "required_fact_axes"
        ),
        "manifest_declared_food_semantic_proposition_count": (
            food_authority.get("proposition_count")
        ),
        "manifest_declared_food_semantic_proposition_inventory_sha256": (
            food_authority.get("proposition_inventory_sha256")
        ),
        "explicit_non_current_input_override": True,
        "current_facts_read_count": 0,
        "render_write_count": 0,
    }
    return {"receipt": receipt, "inventory": inventory}


def build_food_semantic_no_render_receipt(**kwargs):
    """Compatibility wrapper returning the actual consumer receipt only."""
    return consume_food_semantic_inputs_no_render(**kwargs)["receipt"]
# END DVF FOOD SEMANTIC CANDIDATE PATCH
