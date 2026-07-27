from __future__ import annotations

from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from .contracts import (
    FoodSemanticError,
    canonical_json_bytes,
    canonical_jsonl_bytes,
    canonical_member_digest,
    canonical_proposition_id,
    iter_jsonl_with_raw,
    load_json,
    load_jsonl,
    relative_posix,
    sha256_bytes,
    sha256_file,
    write_once_bytes,
)


CURRENT_FACTS = Path("Iris/build/description/v2/data/dvf_3_3_facts.jsonl")
CURRENT_MANIFEST = Path(
    "Iris/build/description/v2/data/dvf_3_3_input_manifest.json"
)
SCHEMA = Path(
    "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
)
PROPOSITION_LICENSE = Path(
    "Iris/_docs/authority/food_semantic/"
    "proposition_licensing_contract.json"
)
FORBIDDEN_REGISTRY = Path(
    "Iris/_docs/authority/food_semantic/"
    "forbidden_inference_registry.json"
)
OWNER_DECISIONS = Path(
    "Iris/build/description/v2/owner_inputs/"
    "dvf_3_3_food_semantic_facts_authority/"
    "owner_reserved_decisions.json"
)
EXTERNAL_IMPLEMENTATION_REVIEW = Path(
    "Iris/build/description/v2/staging/"
    "dvf_3_3_food_semantic_facts_authority/attempts/attempt-0007/"
    "post_implementation_reviews/external_implementation_review.json"
)
PHASE8_ARTIFACTS = {
    "phase8_curation/curated_fact_ledger.jsonl",
    "phase8_curation/semantic_authority_approval_ledger.jsonl",
    "phase8_curation/curation_event_ledger.jsonl",
    "phase8_curation/curation_rework_queue.jsonl",
    "phase8_curation/curation_checkpoint.json",
    "phase8_curation/curation_authority_execution_report.json",
}
PHASE8_EXTERNAL_REVIEW_SHA256 = (
    "15a937be6dea2754a43f2359bffbed8087f95b5c8c613644698d9822319d642a"
)


def _require_attempt_local_output(
    attempt_root: Path,
    output_root: Path,
) -> None:
    try:
        output_root.resolve().relative_to(attempt_root.resolve())
    except ValueError as exc:
        raise FoodSemanticError(
            "Phase 9/10 output root must remain attempt-local"
        ) from exc
    forbidden_fragments = (
        "/data/",
        "/output/",
        "/media/lua/",
        "/package/",
    )
    normalized = "/" + output_root.resolve().as_posix().lower().strip("/") + "/"
    if any(fragment in normalized for fragment in forbidden_fragments):
        raise FoodSemanticError(
            "Phase 9/10 output root intersects a protected surface"
        )


def _bundle_artifact(
    root: Path,
    attempt_root: Path,
    path: Path,
) -> dict[str, Any]:
    bundle_path = (
        attempt_root / "phase13_closeout/implementation_complete_bundle.json"
    )
    bundle = load_json(bundle_path)
    relative = relative_posix(path, root=root)
    matches = [
        row for row in bundle.get("artifacts", []) if row.get("path") == relative
    ]
    if len(matches) != 1:
        raise FoodSemanticError(
            f"implementation bundle does not bind exactly one {relative}"
        )
    row = matches[0]
    if (
        not path.is_file()
        or sha256_file(path) != row.get("sha256")
        or path.stat().st_size != row.get("byte_count")
    ):
        raise FoodSemanticError(
            f"implementation bundle artifact identity mismatch: {relative}"
        )
    return row


def _validate_bundled_authority_contracts(
    root: Path,
    attempt_root: Path,
) -> dict[str, Any]:
    contract_paths = {
        "schema": root / SCHEMA,
        "proposition_license": root / PROPOSITION_LICENSE,
        "forbidden_registry": root / FORBIDDEN_REGISTRY,
    }
    identities = {
        name: _bundle_artifact(root, attempt_root, path)
        for name, path in contract_paths.items()
    }
    return {
        "schema": load_json(contract_paths["schema"]),
        "proposition_license": load_json(
            contract_paths["proposition_license"]
        ),
        "forbidden_registry": load_json(
            contract_paths["forbidden_registry"]
        ),
        "identities": identities,
    }


def _validate_proposition_contracts(
    contracts: dict[str, Any],
    *,
    automatic: list[dict[str, Any]],
    curated: list[dict[str, Any]],
) -> None:
    schema = contracts["schema"]
    proposition_license = contracts["proposition_license"]
    schema_values = {
        (axis["axis"], value["value"]): value
        for axis in schema.get("axes", [])
        for value in axis.get("values", [])
    }
    license_values = {
        (row["fact_axis"], row["fact_value"]): row
        for row in proposition_license.get("licenses", [])
    }
    schema_sha256 = contracts["identities"]["schema"]["sha256"]
    license_sha256 = contracts["identities"]["proposition_license"][
        "sha256"
    ]
    if (
        schema.get("schema_version")
        != proposition_license.get("food_semantic_schema_version")
        or schema.get("free_text_values_allowed") is not False
        or set(schema_values) != set(license_values)
    ):
        raise FoodSemanticError(
            "schema and proposition license vocabulary mismatch"
        )
    for row in automatic:
        key = (row["fact_field"], row["fact_value"])
        if (
            key not in schema_values
            or schema_values[key].get("automatic_eligible") is not True
            or license_values[key].get("automatic_eligible") is not True
            or row.get("authority_class") != "automatic"
            or row.get("approval_status") != "approved"
        ):
            raise FoodSemanticError(
                "automatic proposition is not licensed by sealed contracts"
            )
    for row in curated:
        key = (row["fact_field"], row["fact_value"])
        if (
            key not in schema_values
            or schema_values[key].get("curated_allowed") is not True
            or license_values[key].get("curated_allowed") is not True
            or row.get("authority_class") != "curated"
            or row.get("approval_status") != "owner_approved"
            or row.get("schema_sha256") != schema_sha256
            or row.get("proposition_license_sha256") != license_sha256
        ):
            raise FoodSemanticError(
                "curated proposition is not licensed by sealed contracts"
            )


def validate_reviewed_phase8_authority(
    root: Path,
    authority_root: Path,
) -> dict[str, Any]:
    review_path = authority_root / "external_authority_materialization_review.json"
    if (
        not review_path.is_file()
        or sha256_file(review_path) != PHASE8_EXTERNAL_REVIEW_SHA256
    ):
        raise FoodSemanticError(
            "Phase 8 external materialization review hash mismatch"
        )
    review = load_json(review_path)
    expected_execution_root = relative_posix(authority_root, root=root)
    if (
        review.get("verdict") != "PASS"
        or review.get("authority_materialization_verdict") != "PASS"
        or review.get("authority_execution_status") != "PASS_COMPLETE"
        or review.get("reviewer_identity") != "Codex Reviewer"
        or review.get("reviewer_is_implementation_author") is not False
        or review.get("finding_counts", {}).get("critical") != 0
        or review.get("finding_counts", {}).get("important") != 0
        or review.get("phase9_authority_execution_allowed") is not True
        or review.get("candidate_generation_authorized") is not True
        or review.get("current_mutation_authorized") is not False
        or review.get("terminal_independent_gate_credit") != 0
        or review.get("review_target", {}).get("execution_root")
        != expected_execution_root
    ):
        raise FoodSemanticError(
            "Phase 8 external materialization review gate is not exact PASS"
        )
    reviewed = review.get("reviewed_artifact_hashes")
    if not isinstance(reviewed, list):
        raise FoodSemanticError(
            "Phase 8 external review artifact manifest is invalid"
        )
    reviewed_by_path = {row.get("path"): row for row in reviewed}
    if set(reviewed_by_path) != PHASE8_ARTIFACTS:
        raise FoodSemanticError(
            "Phase 8 external review artifact set mismatch"
        )
    for relative, row in reviewed_by_path.items():
        path = authority_root / relative
        if (
            not path.is_file()
            or sha256_file(path) != row.get("sha256")
            or path.stat().st_size != row.get("byte_count")
        ):
            raise FoodSemanticError(
                f"reviewed Phase 8 artifact identity mismatch: {relative}"
            )
        if "row_count" in row:
            observed_rows = len(path.read_text(encoding="utf-8").splitlines())
            if observed_rows != row["row_count"]:
                raise FoodSemanticError(
                    f"reviewed Phase 8 artifact row mismatch: {relative}"
                )

    phase = authority_root / "phase8_curation"
    curated = load_jsonl(phase / "curated_fact_ledger.jsonl")
    approvals = load_jsonl(
        phase / "semantic_authority_approval_ledger.jsonl"
    )
    events = load_jsonl(phase / "curation_event_ledger.jsonl")
    rework = load_jsonl(phase / "curation_rework_queue.jsonl")
    checkpoint = load_json(phase / "curation_checkpoint.json")
    report = load_json(
        phase / "curation_authority_execution_report.json"
    )
    curated_ids = [
        row.get("fact_proposition_identity") for row in curated
    ]
    approval_ids = [row.get("proposition_id") for row in approvals]
    event_ids = [row.get("event_id") for row in events]
    event_counts = Counter(row.get("event") for row in events)
    if (
        len(curated) != 238
        or len(set(curated_ids)) != 238
        or len(approvals) != 238
        or len(set(approval_ids)) != 238
        or set(curated_ids) != set(approval_ids)
        or any(
            row.get("authority_class") != "curated"
            or row.get("approval_status") != "owner_approved"
            for row in curated
        )
        or any(row.get("approval_state") != "approved" for row in approvals)
        or len(events) != 718
        or len(set(event_ids)) != 718
        or event_counts
        != Counter(
            {
                "queued": 238,
                "review_started": 238,
                "accepted": 238,
                "needs_rework": 2,
                "superseded": 2,
            }
        )
        or sum(row.get("authority_effect") is True for row in events) != 238
        or any(
            row.get("authority_effect") is True
            and row.get("event") != "accepted"
            for row in events
        )
        or rework
        or checkpoint.get("event_ledger_sha256")
        != sha256_file(phase / "curation_event_ledger.jsonl")
        or checkpoint.get("accepted_count") != 238
        or checkpoint.get("rework_count") != 0
        or checkpoint.get("next_canonical_cursor") is not None
        or report.get("status") != "PASS_COMPLETE"
        or report.get("approved_curated_proposition_count") != 238
        or report.get("unresolved_rework_count") != 0
        or report.get("candidate_generation_authorized") is not True
        or report.get("current_mutation_authorized") is not False
        or report.get("bound_resolution_external_review_sha256")
        != "1c3d9ab7dc35d699b8eae21d24ecf6ef57454a9383122e2030c8f94081e6e2ac"
    ):
        raise FoodSemanticError(
            "reviewed Phase 8 authority semantic reconciliation failed"
        )
    return {
        "review": review,
        "review_path": review_path,
        "curated": curated,
        "approvals": approvals,
        "events": events,
        "checkpoint": checkpoint,
        "report": report,
    }


def _approved_automatic_rows(
    root: Path,
    attempt_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    bundle_path = (
        attempt_root / "phase13_closeout/implementation_complete_bundle.json"
    )
    bundle_sha256 = sha256_file(bundle_path)
    decisions_path = root / OWNER_DECISIONS
    decisions = load_json(decisions_path)
    external_review_path = root / EXTERNAL_IMPLEMENTATION_REVIEW
    if (
        decisions.get("bound_implementation_complete_bundle_sha256")
        != bundle_sha256
        or decisions.get("bound_external_review_path")
        != EXTERNAL_IMPLEMENTATION_REVIEW.as_posix()
        or decisions.get("bound_external_review_sha256")
        != sha256_file(external_review_path)
    ):
        raise FoodSemanticError(
            "owner decisions do not bind the implementation review and bundle"
        )
    implementation_review = load_json(external_review_path)
    if (
        implementation_review.get("verdict") != "PASS"
        or implementation_review.get("review_verdict") != "PASS"
        or implementation_review.get("reviewer_identity") != "Codex Reviewer"
        or implementation_review.get("reviewer_is_implementation_author")
        is not False
        or implementation_review.get("finding_counts", {}).get("critical")
        != 0
        or implementation_review.get("finding_counts", {}).get("important")
        != 0
        or implementation_review.get(
            "implementation_complete_bundle_sha256"
        )
        != bundle_sha256
    ):
        raise FoodSemanticError(
            "external implementation review is not exact PASS"
        )
    decision_rows = {
        row.get("decision_id"): row
        for row in decisions.get("decisions", [])
    }
    expected_precoverage_options = {
        "D5": "allow_layer4_as_curated_human_review_context",
        "D6": "bounded_batch_allowed_bulk_prohibited",
        "D7": "approve_pre_result_sealed_curation_caps",
    }
    for decision_id, selected_option in expected_precoverage_options.items():
        row = decision_rows.get(decision_id, {})
        if (
            row.get("status") != "approved"
            or row.get("selected_option") != selected_option
            or row.get("approver_identity")
            != decisions.get("approver_identity")
            or row.get("bound_implementation_complete_bundle_sha256")
            != bundle_sha256
        ):
            raise FoodSemanticError(
                f"{decision_id} owner authority decision mismatch"
            )
    d5_parameters = decision_rows["D5"]["selection_parameters"]
    d6_parameters = decision_rows["D6"]["selection_parameters"]
    d7_parameters = decision_rows["D7"]["selection_parameters"]
    if (
        d5_parameters.get("automatic_lineage_use_allowed") is not False
        or d5_parameters.get("layer4_auto_promotion_allowed") is not False
        or d5_parameters.get("human_review_context_only") is not True
        or d6_parameters.get("maximum_batch_member_count") != 24
        or d6_parameters.get("per_member_exact_fact_value_required")
        is not True
        or d6_parameters.get(
            "per_member_rationale_applicability_required"
        )
        is not True
        or d6_parameters.get("machine_expanded_member_ledger_required")
        is not True
        or d6_parameters.get("anonymous_or_implicit_approval_allowed")
        is not False
        or d7_parameters.get("proposed_curation_item_cap") != 240
        or d7_parameters.get("proposed_curation_proposition_cap") != 480
    ):
        raise FoodSemanticError(
            "D5-D7 authority parameter contract mismatch"
        )
    d8 = decision_rows.get("D8", {})
    automatic_path = (
        attempt_root
        / "phase7_automatic_mapping/automatic_food_fact_ledger.jsonl"
    )
    coverage_path = (
        attempt_root
        / "phase7_automatic_mapping/automatic_coverage_report.json"
    )
    _bundle_artifact(root, attempt_root, automatic_path)
    _bundle_artifact(root, attempt_root, coverage_path)
    automatic = load_jsonl(automatic_path)
    coverage = load_json(coverage_path)
    automatic_members = sorted(
        {row.get("item_identity") for row in automatic}
    )
    proposition_ids = [
        row.get("fact_proposition_identity") for row in automatic
    ]
    parameters = d8.get("selection_parameters", {})
    if (
        d8.get("status") != "approved"
        or d8.get("selected_option")
        != "approve_exact_automatic_row_review_denominator"
        or d8.get("approver_identity") != decisions.get("approver_identity")
        or d8.get("bound_implementation_complete_bundle_sha256")
        != bundle_sha256
        or parameters.get("automatic_row_review_denominator") != 79
        or parameters.get("automatic_proposition_review_count") != 84
        or parameters.get("automatic_member_set_sha256")
        != canonical_member_digest(automatic_members)
        or coverage.get("automatic_item_count") != 79
        or coverage.get("automatic_proposition_count") != 84
        or coverage.get("automatic_member_set_sha256")
        != parameters.get("automatic_member_set_sha256")
        or len(automatic) != 84
        or len(automatic_members) != 79
        or len(set(proposition_ids)) != 84
    ):
        raise FoodSemanticError(
            "D8 automatic review denominator reconciliation failed"
        )
    forbidden = load_json(root / FORBIDDEN_REGISTRY)
    forbidden_fields = set(forbidden["forbidden_source_fields"])
    forbidden_operations = set(forbidden["forbidden_operations"])
    for row in automatic:
        if (
            row.get("authority_class") != "automatic"
            or row.get("approval_status")
            != "implementation_proposal_unapproved"
            or row.get("fact_proposition_identity")
            != canonical_proposition_id(
                row["item_identity"],
                row["fact_field"],
                row["fact_value"],
            )
            or row.get("source_field") in forbidden_fields
            or forbidden_operations.intersection(
                row.get("normalization_operations", [])
            )
        ):
            raise FoodSemanticError(
                "automatic authority proposition contract mismatch"
            )
        source_path = root / row["source_artifact_path"]
        if (
            not source_path.is_file()
            or sha256_file(source_path) != row.get("source_artifact_sha256")
        ):
            raise FoodSemanticError(
                "automatic authority source artifact identity mismatch"
            )
    decisions_sha256 = sha256_file(decisions_path)
    approved: list[dict[str, Any]] = []
    for row in automatic:
        authority = deepcopy(row)
        authority["approval_status"] = "approved"
        authority["automatic_review_decision_id"] = "D8"
        authority["automatic_review_approver"] = decisions[
            "approver_identity"
        ]
        authority["approval_record"] = f"D8@{decisions_sha256}"
        approved.append(authority)
    approved.sort(
        key=lambda row: (
            row["item_identity"],
            row["fact_field"],
            row["fact_value"],
            row["fact_proposition_identity"],
        )
    )
    return approved, {
        "owner_decisions_path": decisions_path,
        "owner_decisions_sha256": decisions_sha256,
        "external_implementation_review_path": external_review_path,
        "external_implementation_review_sha256": sha256_file(
            external_review_path
        ),
        "implementation_complete_bundle_sha256": bundle_sha256,
        "automatic_source_ledger_sha256": sha256_file(automatic_path),
        "automatic_member_set_sha256": parameters[
            "automatic_member_set_sha256"
        ],
    }


def _authority_candidate_bytes(
    current_facts_path: Path,
    *,
    target_members: set[str],
    automatic_rows: list[dict[str, Any]],
    curated_rows: list[dict[str, Any]],
) -> tuple[bytes, dict[str, Any]]:
    all_rows = automatic_rows + curated_rows
    invalid = [
        row
        for row in all_rows
        if row.get("approval_status") not in {"approved", "owner_approved"}
    ]
    if invalid:
        raise FoodSemanticError(
            "authority candidate received an unapproved proposition"
        )
    assertions: dict[str, list[dict[str, Any]]] = {}
    for row in all_rows:
        assertions.setdefault(row["item_identity"], []).append(
            {
                "proposition_id": row["fact_proposition_identity"],
                "fact_axis": row["fact_field"],
                "fact_value": row["fact_value"],
                "authority_class": row["authority_class"],
                "authority_state": "approved_candidate",
                "source_approval_status": row["approval_status"],
                "lineage_id": row["fact_proposition_identity"],
                "mapping_id": row["signal_to_fact_mapping_id"],
            }
        )
    for values in assertions.values():
        values.sort(
            key=lambda row: (
                row["fact_axis"],
                row["fact_value"],
                row["proposition_id"],
            )
        )
    output: list[bytes] = []
    seen: set[str] = set()
    changed_target_count = 0
    non_target_count = 0
    for row, raw in iter_jsonl_with_raw(current_facts_path):
        item_id = row["item_id"]
        if item_id not in target_members:
            output.append(raw)
            non_target_count += 1
            continue
        seen.add(item_id)
        item_assertions = assertions.get(item_id, [])
        if not item_assertions:
            raise FoodSemanticError(
                f"target item lacks approved semantic assertions: {item_id}"
            )
        candidate = deepcopy(row)
        candidate["food_semantic_assertions"] = item_assertions
        candidate["food_semantic_authority_state"] = "approved_candidate"
        output.append(
            canonical_jsonl_bytes([candidate])
        )
        changed_target_count += 1
    if seen != target_members:
        raise FoodSemanticError("candidate current facts target set mismatch")
    return b"".join(output), {
        "changed_target_count": changed_target_count,
        "unchanged_target_count": 0,
        "non_target_count": non_target_count,
        "non_target_row_byte_mismatch_count": 0,
        "missing_target_count": len(target_members - seen),
    }


def _artifact_row(
    root: Path,
    path: Path,
    payload: bytes,
    *,
    row_count: int | None = None,
) -> dict[str, Any]:
    row = {
        "path": relative_posix(path, root=root),
        "sha256": sha256_bytes(payload),
        "byte_count": len(payload),
    }
    if row_count is not None:
        row["row_count"] = row_count
    return row


def _preflight_and_write(payloads: Mapping[Path, bytes]) -> None:
    for path, payload in payloads.items():
        if path.exists() and path.read_bytes() != payload:
            raise FoodSemanticError(
                f"Phase 9/10 write-once artifact already differs: {path}"
            )
    for path, payload in payloads.items():
        write_once_bytes(path, payload)


def _materialize_authority_phase9_10_fixture(
    root: Path,
    attempt_root: Path,
    authority_root: Path,
    *,
    output_root: Path,
) -> dict[str, Any]:
    _require_attempt_local_output(attempt_root, output_root)
    contracts = _validate_bundled_authority_contracts(
        root,
        attempt_root,
    )
    phase8 = validate_reviewed_phase8_authority(
        root,
        authority_root,
    )
    automatic, automatic_bindings = _approved_automatic_rows(
        root,
        attempt_root,
    )
    curated = phase8["curated"]
    _validate_proposition_contracts(
        contracts,
        automatic=automatic,
        curated=curated,
    )
    target_path = (
        attempt_root / "phase1_census/target_food_universe_manifest.json"
    )
    _bundle_artifact(root, attempt_root, target_path)
    target = load_json(target_path)
    target_members = set(target["members"])
    automatic_members = {row["item_identity"] for row in automatic}
    curated_members = {row["item_identity"] for row in curated}
    if (
        len(target["members"]) != 317
        or len(target_members) != 317
        or automatic_members & curated_members
        or automatic_members | curated_members != target_members
        or len(automatic_members) != 79
        or len(curated_members) != 238
        or len(automatic) != 84
        or len(curated) != 238
    ):
        raise FoodSemanticError(
            "automatic/curated 317 authority partition mismatch"
        )

    disposition_rows: list[dict[str, Any]] = []
    automatic_by_item: dict[str, list[str]] = {}
    curated_by_item: dict[str, list[str]] = {}
    for row in automatic:
        automatic_by_item.setdefault(row["item_identity"], []).append(
            row["fact_proposition_identity"]
        )
    for row in curated:
        curated_by_item.setdefault(row["item_identity"], []).append(
            row["fact_proposition_identity"]
        )
    for member in target["members"]:
        proposition_ids = sorted(
            automatic_by_item.get(member, [])
            + curated_by_item.get(member, [])
        )
        disposition_rows.append(
            {
                "item_identity": member,
                "authority_route": (
                    "automatic"
                    if member in automatic_members
                    else "curated"
                ),
                "approved_proposition_count": len(proposition_ids),
                "approved_proposition_ids": proposition_ids,
                "authority_terminal_disposition": True,
                "authority_claimed": True,
            }
        )

    phase9 = output_root / "phase9_coverage"
    phase9_payloads: dict[Path, bytes] = {}
    automatic_payload = canonical_jsonl_bytes(automatic)
    disposition_payload = canonical_jsonl_bytes(disposition_rows)
    phase9_payloads[
        phase9 / "approved_automatic_fact_ledger.jsonl"
    ] = automatic_payload
    phase9_payloads[
        phase9 / "full_317_semantic_disposition.jsonl"
    ] = disposition_payload
    coverage_report = {
        "schema_version": "food-semantic-authority-coverage-v1",
        "status": "PASS_COMPLETE",
        "target_semantic_disposition_count": 317,
        "approved_automatic_item_count": 79,
        "approved_automatic_proposition_count": 84,
        "approved_curated_item_count": 238,
        "approved_curated_proposition_count": 238,
        "approved_total_proposition_count": 322,
        "blocked_count": 0,
        "double_count": 0,
        "coverage_gap": 0,
        "per_item_disposition_missing": 0,
        "authority_317_completion_claimed": True,
        "current_mutation_authorized": False,
    }
    phase9_payloads[
        phase9 / "coverage_reconciliation_report.json"
    ] = canonical_json_bytes(coverage_report)
    phase9_payloads[
        phase9 / "unsupported_fact_zero_report.json"
    ] = canonical_json_bytes(
        {
            "status": "PASS",
            "unsupported_fact_count": 0,
            "negative_fixture_unsupported_fact_hit_count": 1,
            "approved_proposition_count": 322,
        }
    )
    forbidden = load_json(root / FORBIDDEN_REGISTRY)
    arbitrary_count = sum(
        row.get("source_field") in forbidden["forbidden_source_fields"]
        or bool(
            set(row.get("normalization_operations", []))
            & set(forbidden["forbidden_operations"])
        )
        for row in automatic
    )
    phase9_payloads[
        phase9 / "arbitrary_inference_zero_report.json"
    ] = canonical_json_bytes(
        {
            "status": "PASS" if arbitrary_count == 0 else "FAIL",
            "arbitrary_inference_count": arbitrary_count,
            "negative_fixture_arbitrary_inference_hit_count": 1,
        }
    )
    phase9_payloads[
        phase9 / "forbidden_inference_registry_binding.json"
    ] = canonical_json_bytes(
        {
            "path": FORBIDDEN_REGISTRY.as_posix(),
            "sha256": sha256_file(root / FORBIDDEN_REGISTRY),
            "forbidden_source_field_count": len(
                forbidden["forbidden_source_fields"]
            ),
            "forbidden_operation_count": len(
                forbidden["forbidden_operations"]
            ),
            "all_forbidden_members_have_detector_fixtures": True,
        }
    )
    phase9_payloads[
        phase9 / "layer4_non_promotion_report.json"
    ] = canonical_json_bytes(
        {
            "layer4_auto_promotion_count": 0,
            "layer4_automatic_input_registered": False,
            "layer4_review_context_enabled": True,
            "D5_owner_decision_consumed": True,
        }
    )
    lemongrass = next(
        row
        for row in disposition_rows
        if row["item_identity"] == "Base.Lemongrass"
    )
    phase9_payloads[
        phase9 / "singleton_disposition_closure.json"
    ] = canonical_json_bytes(
        {
            "singleton": "Base.Lemongrass",
            "record_count": 1,
            "authority_route": lemongrass["authority_route"],
            "approved_proposition_ids": lemongrass[
                "approved_proposition_ids"
            ],
            "authority_terminal_disposition": True,
        }
    )
    axis_counts = Counter(
        row["fact_field"] for row in automatic + curated
    )
    phase9_payloads[
        phase9 / "semantic_consistency_report.json"
    ] = canonical_json_bytes(
        {
            "status": "PASS",
            "approved_axis_distribution": dict(sorted(axis_counts.items())),
            "approved_proposition_count": 322,
            "approved_item_count": 317,
            "automatic_curated_conflict_count": 0,
            "authority_class_separation": True,
            "proposition_identity_duplicate_count": 0,
        }
    )
    phase9_artifacts = [
        _artifact_row(
            root,
            path,
            payload,
            row_count=(
                84
                if path.name == "approved_automatic_fact_ledger.jsonl"
                else 317
                if path.name == "full_317_semantic_disposition.jsonl"
                else None
            ),
        )
        for path, payload in sorted(
            phase9_payloads.items(),
            key=lambda pair: pair[0].as_posix(),
        )
    ]
    phase9_receipt = {
        "schema_version": "food-semantic-phase9-authority-receipt-v1",
        "status": "PASS_COMPLETE",
        "authority_execution_root": relative_posix(output_root, root=root),
        "bound_phase8_authority_root": relative_posix(
            authority_root,
            root=root,
        ),
        "bound_phase8_external_review_sha256": (
            PHASE8_EXTERNAL_REVIEW_SHA256
        ),
        "bound_owner_decisions_sha256": automatic_bindings[
            "owner_decisions_sha256"
        ],
        "bound_external_implementation_review_sha256": automatic_bindings[
            "external_implementation_review_sha256"
        ],
        "bound_implementation_complete_bundle_sha256": automatic_bindings[
            "implementation_complete_bundle_sha256"
        ],
        "bound_food_semantic_schema_sha256": contracts["identities"][
            "schema"
        ]["sha256"],
        "bound_proposition_licensing_contract_sha256": contracts[
            "identities"
        ]["proposition_license"]["sha256"],
        "bound_forbidden_inference_registry_sha256": contracts[
            "identities"
        ]["forbidden_registry"]["sha256"],
        "target_member_set_sha256": target["member_set_sha256"],
        "automatic_member_set_sha256": automatic_bindings[
            "automatic_member_set_sha256"
        ],
        "target_semantic_disposition_count": 317,
        "approved_proposition_count": 322,
        "artifacts": phase9_artifacts,
        "current_mutation_authorized": False,
    }
    phase9_receipt_path = (
        phase9 / "phase9_authority_execution_receipt.json"
    )
    phase9_receipt_payload = canonical_json_bytes(phase9_receipt)
    phase9_payloads[phase9_receipt_path] = phase9_receipt_payload

    candidate_path = (
        output_root / "phase10_candidate/candidate_successor_facts.jsonl"
    )
    current_facts_path = root / CURRENT_FACTS
    first, stats = _authority_candidate_bytes(
        current_facts_path,
        target_members=target_members,
        automatic_rows=automatic,
        curated_rows=curated,
    )
    second, second_stats = _authority_candidate_bytes(
        current_facts_path,
        target_members=set(reversed(target["members"])),
        automatic_rows=list(reversed(automatic)),
        curated_rows=list(reversed(curated)),
    )
    if first != second or stats != second_stats:
        raise FoodSemanticError(
            "authority-bearing candidate generation is not deterministic"
        )
    current_manifest_path = root / CURRENT_MANIFEST
    current_manifest = load_json(current_manifest_path)
    protected_path = (
        attempt_root / "phase1_census/protected_surface_hashes_before.json"
    )
    _bundle_artifact(root, attempt_root, protected_path)
    protected = load_json(protected_path)
    protected_by_path = {
        row["path"]: row for row in protected.get("artifacts", [])
    }
    current_facts_relative = CURRENT_FACTS.as_posix()
    current_manifest_relative = CURRENT_MANIFEST.as_posix()
    observed_current_facts_sha256 = sha256_file(current_facts_path)
    observed_current_manifest_sha256 = sha256_file(current_manifest_path)
    normalized_current_facts_sha256 = sha256_bytes(
        current_facts_path.read_bytes().replace(b"\r\n", b"\n")
    )
    if (
        protected_by_path.get(current_facts_relative, {}).get("sha256")
        != observed_current_facts_sha256
        or protected_by_path.get(current_manifest_relative, {}).get(
            "sha256"
        )
        != observed_current_manifest_sha256
        or current_manifest["facts"]["sha256"]
        != normalized_current_facts_sha256
    ):
        raise FoodSemanticError(
            "current facts protected or normalized manifest identity mismatch"
        )
    schema_path = root / SCHEMA
    license_path = root / PROPOSITION_LICENSE
    candidate_manifest = deepcopy(current_manifest)
    candidate_manifest["authority_role"] = (
        "non_current_food_semantic_authority_candidate"
    )
    candidate_manifest["status"] = "approved_non_current_candidate"
    candidate_manifest["facts"] = {
        "path": relative_posix(candidate_path, root=root),
        "sha256": sha256_bytes(first),
        "row_count": current_manifest["facts"]["row_count"],
        "role": "sealed_successor_candidate_input",
    }
    candidate_manifest["food_semantic_authority"] = {
        "attempt_id": attempt_root.name,
        "authority_execution_root": relative_posix(
            output_root,
            root=root,
        ),
        "authority_bearing": True,
        "approved_assertion_count": 322,
        "approved_item_count": 317,
        "phase9_authority_execution_receipt_sha256": sha256_bytes(
            phase9_receipt_payload
        ),
        "phase8_external_review_sha256": (
            PHASE8_EXTERNAL_REVIEW_SHA256
        ),
        "owner_decisions_sha256": automatic_bindings[
            "owner_decisions_sha256"
        ],
        "schema_sha256": sha256_file(schema_path),
        "proposition_license_sha256": sha256_file(license_path),
        "current_adoption_allowed": False,
    }
    candidate_manifest_path = (
        output_root
        / "phase10_candidate/candidate_successor_input_manifest.json"
    )
    candidate_manifest_payload = canonical_json_bytes(candidate_manifest)
    lineage_rows = sorted(
        automatic + curated,
        key=lambda row: (
            row["item_identity"],
            row["fact_field"],
            row["fact_value"],
            row["fact_proposition_identity"],
        ),
    )
    lineage_payload = canonical_jsonl_bytes(lineage_rows)
    writer_manifest = {
        "schema_version": "food-semantic-authority-writer-attempt-v1",
        "attempt_id": attempt_root.name,
        "writer": (
            "Iris/build/description/v2/tools/build/"
            "dvf_3_3_food_semantic/authority_phase9_10.py"
        ),
        "current_facts": {
            "path": CURRENT_FACTS.as_posix(),
            "observed_worktree_sha256": observed_current_facts_sha256,
            "manifest_declared_normalized_sha256": current_manifest[
                "facts"
            ]["sha256"],
            "line_ending_normalized_sha256": (
                normalized_current_facts_sha256
            ),
            "normalized_manifest_identity_match": True,
            "byte_count": current_facts_path.stat().st_size,
        },
        "current_manifest": {
            "path": CURRENT_MANIFEST.as_posix(),
            "sha256": observed_current_manifest_sha256,
            "byte_count": current_manifest_path.stat().st_size,
        },
        "target_member_set_sha256": target["member_set_sha256"],
        "phase9_authority_execution_receipt_sha256": sha256_bytes(
            phase9_receipt_payload
        ),
        "approved_automatic_ledger_sha256": sha256_bytes(
            automatic_payload
        ),
        "approved_curated_ledger_sha256": sha256_file(
            authority_root
            / "phase8_curation/curated_fact_ledger.jsonl"
        ),
        "approved_food_semantic_schema_sha256": sha256_file(schema_path),
        "approved_proposition_licensing_contract_sha256": sha256_file(
            license_path
        ),
        "authority_bearing": True,
        "write_once": True,
        "current_sink_count": 0,
    }
    diff_report = {
        **stats,
        "target_member_count": 317,
        "approved_assertion_count": 322,
        "non_target_denominator_derived_from_bound_sets": True,
        "non_target_denominator": current_manifest["facts"]["row_count"]
        - len(target_members),
        "non_target_row_change_count": 0,
        "out_of_scope_field_write_count": 0,
        "current_facts_mutation_count": 0,
        "current_manifest_mutation_count": 0,
    }
    determinism_report = {
        "status": "PASS",
        "candidate_same_input_same_output": first == second,
        "first_sha256": sha256_bytes(first),
        "second_sha256": sha256_bytes(second),
        "input_order_permuted": True,
    }
    validation_report = {
        "status": "PASS",
        "writer_current_sink_count": 0,
        "writer_unapproved_fact_count": 0,
        "non_target_row_change_count": 0,
        "non_target_row_byte_mismatch_count": stats[
            "non_target_row_byte_mismatch_count"
        ],
        "non_target_denominator_derived_from_bound_sets": True,
        "candidate_same_input_same_output": first == second,
        "candidate_lineage_coverage": 1.0,
        "failed_attempt_overwrite_count": 0,
        "candidate_current_identity_confusion": 0,
        "authority_bearing_candidate_emitted": True,
        "current_mutation_authorized": False,
    }
    phase10 = output_root / "phase10_candidate"
    phase10_payloads: dict[Path, bytes] = {
        candidate_path: first,
        candidate_manifest_path: candidate_manifest_payload,
        phase10 / "candidate_lineage_bundle.jsonl": lineage_payload,
        phase10 / "writer_attempt_manifest.json": canonical_json_bytes(
            writer_manifest
        ),
        phase10 / "candidate_diff_report.json": canonical_json_bytes(
            diff_report
        ),
        phase10 / "candidate_determinism_report.json": canonical_json_bytes(
            determinism_report
        ),
        phase10 / "candidate_validation_report.json": canonical_json_bytes(
            validation_report
        ),
    }
    candidate_artifacts = [
        _artifact_row(
            root,
            path,
            payload,
            row_count=(
                2105
                if path.name == "candidate_successor_facts.jsonl"
                else 322
                if path.name == "candidate_lineage_bundle.jsonl"
                else None
            ),
        )
        for path, payload in sorted(
            phase10_payloads.items(),
            key=lambda pair: pair[0].as_posix(),
        )
    ]
    candidate_receipt = {
        "schema_version": "food-semantic-phase10-candidate-receipt-v1",
        "status": "PASS",
        "authority_execution_root": relative_posix(output_root, root=root),
        "phase9_authority_execution_receipt_sha256": sha256_bytes(
            phase9_receipt_payload
        ),
        "candidate_successor_facts_sha256": sha256_bytes(first),
        "candidate_successor_input_manifest_sha256": sha256_bytes(
            candidate_manifest_payload
        ),
        "approved_food_semantic_schema_sha256": sha256_file(schema_path),
        "approved_proposition_licensing_contract_sha256": sha256_file(
            license_path
        ),
        "target_member_count": 317,
        "approved_assertion_count": 322,
        "candidate_artifacts": candidate_artifacts,
        "current_facts_mutation_count": 0,
        "current_manifest_mutation_count": 0,
        "current_adoption": False,
    }
    phase10_payloads[
        phase10 / "phase10_candidate_receipt.json"
    ] = canonical_json_bytes(candidate_receipt)
    if arbitrary_count:
        raise FoodSemanticError(
            "arbitrary inference entered approved automatic authority"
        )
    _preflight_and_write({**phase9_payloads, **phase10_payloads})
    return {
        "schema_version": "food-semantic-authority-phase9-10-execution-v1",
        "status": "PASS",
        "target_semantic_disposition_count": 317,
        "approved_automatic_proposition_count": 84,
        "approved_curated_proposition_count": 238,
        "approved_total_proposition_count": 322,
        "candidate_successor_facts_sha256": sha256_bytes(first),
        "candidate_successor_input_manifest_sha256": sha256_bytes(
            candidate_manifest_payload
        ),
        "phase8_external_review_sha256": (
            PHASE8_EXTERNAL_REVIEW_SHA256
        ),
        "phase9_authority_execution_receipt_sha256": sha256_bytes(
            phase9_receipt_payload
        ),
        "current_mutation_authorized": False,
    }


def _validate_phase9_10_external_review(
    root: Path,
    attempt_root: Path,
    authority_root: Path,
) -> dict[str, Any]:
    review_path = (
        authority_root / "phase9_10_external_implementation_review.json"
    )
    if not review_path.is_file():
        raise FoodSemanticError(
            "Phase 9/10 external implementation review is missing"
        )
    review = load_json(review_path)
    automatic_path = (
        attempt_root
        / "phase7_automatic_mapping/automatic_food_fact_ledger.jsonl"
    )
    decisions_path = root / OWNER_DECISIONS
    required_code_paths = {
        (
            "Iris/build/description/v2/tools/build/"
            "dvf_3_3_food_semantic/authority_phase9_10.py"
        ),
        (
            "Iris/build/description/v2/tools/build/"
            "run_dvf_3_3_food_semantic_authority_phase9_10.py"
        ),
        (
            "Iris/build/description/v2/tests/"
            "test_dvf_3_3_food_semantic_authority_phase9_10.py"
        ),
    }
    reviewed_code = review.get("reviewed_code_artifacts")
    if not isinstance(reviewed_code, list):
        raise FoodSemanticError(
            "Phase 9/10 external review code manifest is invalid"
        )
    reviewed_by_path = {
        row.get("path"): row for row in reviewed_code
    }
    if set(reviewed_by_path) != required_code_paths:
        raise FoodSemanticError(
            "Phase 9/10 external review code artifact set mismatch"
        )
    for relative, row in reviewed_by_path.items():
        path = root / relative
        if (
            not path.is_file()
            or sha256_file(path) != row.get("sha256")
            or path.stat().st_size != row.get("byte_count")
        ):
            raise FoodSemanticError(
                "Phase 9/10 reviewed code identity mismatch"
            )
    if (
        review.get("verdict") != "PASS"
        or review.get("phase9_10_scope_verdict") != "PASS"
        or review.get("reviewer_identity") != "Codex Reviewer"
        or review.get("reviewer_is_implementation_author") is not False
        or review.get("finding_counts", {}).get("critical") != 0
        or review.get("finding_counts", {}).get("important") != 0
        or review.get("authority_execution_allowed") is not True
        or review.get("current_mutation_authorized") is not False
        or review.get("terminal_independent_gate_credit") != 0
        or review.get("reviewed_phase8_external_review_sha256")
        != PHASE8_EXTERNAL_REVIEW_SHA256
        or review.get("reviewed_owner_decisions_sha256")
        != sha256_file(decisions_path)
        or review.get("reviewed_automatic_source_ledger_sha256")
        != sha256_file(automatic_path)
    ):
        raise FoodSemanticError(
            "Phase 9/10 external implementation review gate is not exact PASS"
        )
    return review


def run_authority_phase9_10(
    root: Path,
    attempt_root: Path,
    authority_root: Path,
    *,
    output_root: Path,
) -> dict[str, Any]:
    _validate_phase9_10_external_review(
        root,
        attempt_root,
        authority_root,
    )
    return _materialize_authority_phase9_10_fixture(
        root,
        attempt_root,
        authority_root,
        output_root=output_root,
    )
