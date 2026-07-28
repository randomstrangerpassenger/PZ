from __future__ import annotations

from pathlib import Path


# BEGIN DVF FOOD SEMANTIC CANDIDATE PATCH (D16 adoption required)
def validate_food_semantic_consumed_input_receipt(
    receipt,
    selected_binding,
    *,
    repository_root=None,
    expected_projection=None,
):
    """Fail closed unless the actual consumer receipt matches all four identities."""
    expected = {
        "facts_sha256": selected_binding["successor_facts_sha256"],
        "manifest_sha256": selected_binding["successor_input_manifest_sha256"],
        "schema_sha256": selected_binding["approved_food_semantic_schema_sha256"],
        "proposition_license_sha256": selected_binding[
            "approved_proposition_licensing_contract_sha256"
        ],
    }
    mismatches = [
        field for field, value in expected.items() if receipt.get(field) != value
    ]
    four_identity_match = not mismatches
    if receipt.get("producer") != "naturalization_actual_phase2_consumer":
        mismatches.append("producer")
    if receipt.get("explicit_non_current_input_override") is not True:
        mismatches.append("explicit_non_current_input_override")
    if receipt.get("current_facts_read_count") != 0:
        mismatches.append("current_facts_read_count")
    if receipt.get("render_write_count") != 0:
        mismatches.append("render_write_count")
    if receipt.get("opened_input_count") != 4:
        mismatches.append("opened_input_count")
    if receipt.get("phase2_primary_opened_input_count") != 4:
        mismatches.append("phase2_primary_opened_input_count")
    if receipt.get("threshold_authority_opened_input_count") != 2:
        mismatches.append("threshold_authority_opened_input_count")
    if receipt.get("total_opened_input_count") != 6:
        mismatches.append("total_opened_input_count")
    if not isinstance(receipt.get("facts_row_count"), int) or receipt.get(
        "facts_row_count", 0
    ) <= 0:
        mismatches.append("facts_row_count")
    if not isinstance(
        receipt.get("food_semantic_proposition_count"), int
    ) or receipt.get("food_semantic_proposition_count", 0) <= 0:
        mismatches.append("food_semantic_proposition_count")
    inventory_sha256 = receipt.get(
        "food_semantic_proposition_inventory_sha256"
    )
    if not isinstance(inventory_sha256, str) or len(inventory_sha256) != 64:
        mismatches.append("food_semantic_proposition_inventory_sha256")
    if expected_projection is None:
        mismatches.append("expected_projection")
    else:
        projection_fields = {
            "food_semantic_proposition_inventory_sha256": (
                "inventory_sha256"
            ),
            "food_semantic_proposition_count": "proposition_count",
            "food_semantic_item_count": "item_count",
            "food_semantic_item_set_sha256": "item_set_sha256",
            "required_fact_axes": "required_fact_axes",
            "meaningful_partition_count": "meaningful_partition_count",
        }
        for receipt_field, expected_field in projection_fields.items():
            if receipt.get(receipt_field) != expected_projection.get(
                expected_field
            ):
                mismatches.append(receipt_field)
    for zero_field in (
        "required_axis_missing_item_count",
        "duplicate_proposition_id_count",
        "invalid_schema_proposition_count",
        "invalid_license_proposition_count",
    ):
        if receipt.get(zero_field) != 0:
            mismatches.append(zero_field)
    if receipt.get("food_semantic_item_count") != selected_binding.get(
        "target_member_count"
    ):
        mismatches.append("target_member_count")
    if receipt.get("food_semantic_item_set_sha256") != selected_binding.get(
        "target_member_set_sha256"
    ):
        mismatches.append("target_member_set_sha256")
    if receipt.get("required_fact_axes") != selected_binding.get(
        "required_fact_axes"
    ):
        mismatches.append("required_fact_axes")
    if receipt.get("manifest_declared_food_semantic_item_count") != receipt.get(
        "food_semantic_item_count"
    ):
        mismatches.append("manifest_declared_food_semantic_item_count")
    if receipt.get(
        "manifest_declared_food_semantic_item_set_sha256"
    ) != receipt.get("food_semantic_item_set_sha256"):
        mismatches.append("manifest_declared_food_semantic_item_set_sha256")
    if receipt.get("manifest_declared_required_fact_axes") != receipt.get(
        "required_fact_axes"
    ):
        mismatches.append("manifest_declared_required_fact_axes")
    if receipt.get(
        "manifest_declared_food_semantic_proposition_count"
    ) != receipt.get("food_semantic_proposition_count"):
        mismatches.append("manifest_declared_food_semantic_proposition_count")
    if receipt.get(
        "manifest_declared_food_semantic_proposition_inventory_sha256"
    ) != receipt.get("food_semantic_proposition_inventory_sha256"):
        mismatches.append(
            "manifest_declared_food_semantic_proposition_inventory_sha256"
        )
    minimum_partition = selected_binding.get("minimum_meaningful_partition")
    if (
        not isinstance(minimum_partition, int)
        or receipt.get("meaningful_partition_count", 0) < minimum_partition
    ):
        mismatches.append("minimum_meaningful_partition")
    if receipt.get("manifest_facts_sha256_match") is not True:
        mismatches.append("manifest_facts_sha256_match")
    if receipt.get("manifest_facts_path_match") is not True:
        mismatches.append("manifest_facts_path_match")
    maximum_same_skeleton_group = receipt.get(
        "maximum_same_skeleton_group"
    )
    bound_threshold_value = receipt.get("bound_threshold_value")
    if (
        not isinstance(maximum_same_skeleton_group, int)
        or not isinstance(bound_threshold_value, int)
        or maximum_same_skeleton_group > bound_threshold_value
    ):
        mismatches.append("maximum_same_skeleton_group_within_bound")
    if receipt.get("manifest_declared_facts_sha256") != receipt.get(
        "facts_sha256"
    ):
        mismatches.append("manifest_declared_facts_sha256")
    for path_field in (
        "facts_path",
        "manifest_path",
        "schema_path",
        "proposition_license_path",
    ):
        if not receipt.get(path_field):
            mismatches.append(path_field)
    comparison_root = repository_root or selected_binding.get("repository_root")
    selected_paths = {
        "facts_path": selected_binding.get("successor_facts_path"),
        "manifest_path": selected_binding.get("successor_input_manifest_path"),
        "schema_path": selected_binding.get("approved_food_semantic_schema_path"),
        "proposition_license_path": selected_binding.get(
            "approved_proposition_licensing_contract_path"
        ),
    }
    for receipt_field, selected_path in selected_paths.items():
        if selected_path is None:
            mismatches.append(f"selected_{receipt_field}")
            continue
        expected_path = Path(selected_path)
        if not expected_path.is_absolute():
            if not comparison_root:
                mismatches.append(f"{receipt_field}:repository_root")
                continue
            expected_path = Path(comparison_root) / expected_path
        if Path(receipt.get(receipt_field, "")).resolve() != expected_path.resolve():
            mismatches.append(receipt_field)
    return {
        "status": "PASS" if not mismatches else "FAIL",
        "mismatches": sorted(set(mismatches)),
        "four_identity_match": four_identity_match,
        "exact_projection_match": not any(
            mismatch
            for mismatch in mismatches
            if mismatch
            not in {
                "facts_sha256",
                "manifest_sha256",
                "schema_sha256",
                "proposition_license_sha256",
            }
        ),
    }
# END DVF FOOD SEMANTIC CANDIDATE PATCH
