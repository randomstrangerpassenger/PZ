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


def build_food_semantic_no_render_receipt(
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
        json.load(handle)
    with paths["proposition_license"].open("r", encoding="utf-8") as handle:
        json.load(handle)
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
    inventory = build_food_semantic_proposition_inventory(
        facts_rows,
        schema_sha256=computed["schema_sha256"],
        proposition_license_sha256=computed[
            "proposition_license_sha256"
        ],
    )
    inventory_bytes = (
        "".join(
            json.dumps(
                row,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
            for row in inventory
        )
    ).encode("utf-8")
    return {
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
        "explicit_non_current_input_override": True,
        "current_facts_read_count": 0,
        "render_write_count": 0,
    }
# END DVF FOOD SEMANTIC CANDIDATE PATCH
