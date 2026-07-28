from __future__ import annotations


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
            if assertion.get("authority_state") != "approved_candidate":
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
    facts_sha256,
    manifest_path,
    manifest_sha256,
    schema_path,
    schema_sha256,
    proposition_license_path,
    proposition_license_sha256,
    explicit_non_current_input_override,
):
    """Return the exact inputs opened by the actual Phase 2 consumer."""
    return {
        "producer": "naturalization_actual_phase2_consumer",
        "facts_path": str(facts_path),
        "facts_sha256": facts_sha256,
        "manifest_path": str(manifest_path),
        "manifest_sha256": manifest_sha256,
        "schema_path": str(schema_path),
        "schema_sha256": schema_sha256,
        "proposition_license_path": str(proposition_license_path),
        "proposition_license_sha256": proposition_license_sha256,
        "explicit_non_current_input_override": explicit_non_current_input_override,
        "current_facts_read_count": 0 if explicit_non_current_input_override else 1,
        "render_write_count": 0,
    }
# END DVF FOOD SEMANTIC CANDIDATE PATCH
