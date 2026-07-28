# BEGIN DVF FOOD SEMANTIC CANDIDATE PATCH (D16 adoption required)
def validate_food_semantic_consumed_input_receipt(receipt, selected_binding):
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
    if receipt.get("producer") != "naturalization_actual_phase2_consumer":
        mismatches.append("producer")
    if receipt.get("render_write_count") != 0:
        mismatches.append("render_write_count")
    return {
        "status": "PASS" if not mismatches else "FAIL",
        "mismatches": sorted(set(mismatches)),
        "four_identity_match": not mismatches,
    }
# END DVF FOOD SEMANTIC CANDIDATE PATCH
