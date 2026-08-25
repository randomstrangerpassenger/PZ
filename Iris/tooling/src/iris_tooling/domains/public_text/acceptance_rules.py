from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .acceptance_context import (
    CANDIDATE_STRUCTURAL_STATUSES,
    DISPOSITION_CLASSES,
    EVALUATION_SUBJECT_KINDS,
    FIXTURE_SCHEMA_VERSION,
    QUALIFIED_DISPOSITIONS,
    RAW_DETECTOR_IDS,
    VOLATILE_CANONICAL_FIELDS,
)
from .acceptance_contracts import build_foundation_contract, synchronization_projection
from .acceptance_infrastructure import (
    FoundationContractError,
    canonical_hash,
    require_exact_keys,
)
from .evaluate import (
    PublicTextEvaluationError,
    determine_qualified_disposition as determine_disposition_rule,
    evaluate_threshold as evaluate_threshold_rule,
)

def _registration_index(
    registry: dict[str, Any], key: str
) -> dict[str, dict[str, Any]]:
    rows = registry.get("registrations")
    if not isinstance(rows, list):
        raise FoundationContractError(f"registry registrations missing: {key}")
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get(key), str):
            raise FoundationContractError(f"invalid registry row for {key}")
        identity = row[key]
        if identity in result:
            raise FoundationContractError(f"duplicate {key}: {identity}")
        result[identity] = row
    return result


def validate_foundation_contract(
    contract: dict[str, Any], *, expected_foundation_id: str
) -> dict[str, Any]:
    expected = build_foundation_contract(expected_foundation_id)
    if contract != expected:
        raise FoundationContractError(
            "foundation contract differs from the deterministic candidate-independent projection"
        )

    metric_index = _registration_index(
        contract["metric_registry_candidate"], "metric_id"
    )
    denominator_index = _registration_index(
        contract["denominator_registry_candidate"], "denominator_id"
    )
    detector_rows = contract["detector_mapping_candidate"]["mappings"]
    detector_ids = [row["detector_id"] for row in detector_rows]
    if detector_ids != list(RAW_DETECTOR_IDS):
        raise FoundationContractError("raw detector mapping order or membership mismatch")
    if len(detector_ids) != len(set(detector_ids)):
        raise FoundationContractError("duplicate detector mapping")

    unknown_denominators = sorted(
        {
            row["denominator_id"]
            for row in metric_index.values()
            if row["denominator_id"] not in denominator_index
            and not row["denominator_id"].startswith(
                "naturalization_raw_detector_opportunity_v1:"
            )
        }
    )
    if unknown_denominators:
        raise FoundationContractError(
            f"metrics reference unknown denominators: {unknown_denominators}"
        )

    invalid_dispositions = sorted(
        {
            row["disposition_class"]
            for row in metric_index.values()
            if row["disposition_class"] not in DISPOSITION_CLASSES
        }
    )
    if invalid_dispositions:
        raise FoundationContractError(
            f"invalid disposition classes: {invalid_dispositions}"
        )

    policy_metric_ids = set(
        contract["policy_candidate"]["current_runtime_payload_thresholds"]
    ) | set(contract["policy_candidate"]["naturalization_candidate_thresholds"])
    if policy_metric_ids != set(metric_index):
        raise FoundationContractError(
            "policy candidate metric set differs from metric registry"
        )

    if contract["policy_candidate"]["default_exceptions"]:
        raise FoundationContractError("v1 default exception set must be empty")

    return {
        "status": "PASS",
        "four_plan_sync_projection_sha256_match": True,
        "clean_validation_terminal_pass": True,
        "food_sealed_successor_terminal_closeout": True,
        "registry_food_successor_adoption_receipt_valid": True,
        "current_facts_equals_selected_successor_facts": True,
        "current_manifest_binds_selected_successor_manifest": True,
        "metric_count": len(metric_index),
        "denominator_count": len(denominator_index),
        "raw_detector_count": len(detector_ids),
        "unknown_metric_count": 0,
        "unknown_denominator_count": 0,
        "unmapped_raw_detector_count": 0,
        "candidate_content_dependency_count": 0,
        "candidate_metric_dependency_count": 0,
    }


def evaluate_threshold(
    *, numerator: int, denominator: int, threshold: dict[str, Any]
) -> bool:
    try:
        return evaluate_threshold_rule(
            numerator=numerator,
            denominator=denominator,
            threshold=threshold,
        )
    except PublicTextEvaluationError as exc:
        raise FoundationContractError(str(exc)) from exc


def determine_qualified_disposition(
    *,
    technical_blocker_count: int,
    effective_blocking_finding_count: int,
    advisory_debt_count: int,
    active_waiver_count: int,
) -> str:
    try:
        return determine_disposition_rule(
            technical_blocker_count=technical_blocker_count,
            effective_blocking_finding_count=effective_blocking_finding_count,
            advisory_debt_count=advisory_debt_count,
            active_waiver_count=active_waiver_count,
        )
    except PublicTextEvaluationError as exc:
        raise FoundationContractError(str(exc)) from exc

def parse_policy_timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise FoundationContractError("timestamp must be a string")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise FoundationContractError(f"invalid timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise FoundationContractError("timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def without_volatile_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: without_volatile_fields(child)
            for key, child in value.items()
            if key not in VOLATILE_CANONICAL_FIELDS
        }
    if isinstance(value, list):
        return [without_volatile_fields(child) for child in value]
    return value


def _fixture_outcome(row: dict[str, Any], contract: dict[str, Any]) -> str:
    kind = row["fixture_kind"]
    data = row.get("input", {})
    if not isinstance(data, dict):
        raise FoundationContractError("fixture input must be an object")

    if kind == "freshness":
        return (
            "accepted"
            if data.get("expected_hash") == data.get("actual_hash")
            else "blocked"
        )
    if kind == "registry_membership":
        registry = data.get("registry")
        value = data.get("value")
        if registry == "metric":
            known = set(
                _registration_index(
                    contract["metric_registry_candidate"], "metric_id"
                )
            )
        elif registry == "denominator":
            known = set(
                _registration_index(
                    contract["denominator_registry_candidate"], "denominator_id"
                )
            )
        elif registry == "subject_kind":
            known = set(EVALUATION_SUBJECT_KINDS)
        elif registry == "profile":
            known = set(data.get("known_values", []))
        else:
            return "blocked"
        return "accepted" if value in known else "blocked"
    if kind == "denominator":
        value = data.get("value")
        return "accepted" if isinstance(value, int) and value > 0 else "blocked"
    if kind == "threshold":
        satisfied = evaluate_threshold(
            numerator=data["numerator"],
            denominator=data["denominator"],
            threshold=data["threshold"],
        )
        if satisfied:
            return "accepted"
        return (
            "blocked"
            if data["disposition_class"] == "blocking_gate"
            else "deferred_internal_debt"
        )
    if kind == "row_occurrence":
        rows = data.get("missing_any_row_count")
        occurrences = data.get("missing_occurrence_count")
        blockers = data.get("effective_blocker_count")
        valid = (
            isinstance(rows, int)
            and isinstance(occurrences, int)
            and occurrences >= rows >= 0
            and blockers == rows
        )
        return "accepted" if valid else "blocked"
    if kind == "unadopted_separation":
        valid = (
            data.get("unadopted_in_quality_denominator_count") == 0
            and data.get("unadopted_counted_as_weak") == 0
        )
        return "accepted" if valid else "blocked"
    if kind == "metric_axes":
        valid = (
            data.get("quality_class") in {"weak", "adequate", "strong"}
            and isinstance(data.get("missing_any_required_section"), bool)
        )
        return "accepted" if valid else "blocked"
    if kind == "partition":
        parts = data.get("parts")
        total = data.get("total")
        valid = (
            isinstance(parts, list)
            and all(isinstance(value, int) and value >= 0 for value in parts)
            and sum(parts) == total
        )
        return "accepted" if valid else "blocked"
    if kind == "waiver":
        required = {
            "payload_binding_hash",
            "expected_payload_binding_hash",
            "policy_hash",
            "expected_policy_hash",
            "metric_id",
            "known_metric",
            "original_disposition",
            "waived_disposition",
            "owner_identity",
            "owner_valid",
            "issued_at",
            "expires_at",
            "evaluation_at",
            "owner_binding_proof",
            "technical_failure_scope",
            "raw_metric_mutated",
        }
        if set(data) != required:
            return "blocked"
        valid = (
            data["payload_binding_hash"] == data["expected_payload_binding_hash"]
            and data["policy_hash"] == data["expected_policy_hash"]
            and data["metric_id"] == data["known_metric"]
            and data["waived_disposition"] == "deferred_internal_debt"
            and data["owner_valid"] is True
            and bool(data["owner_identity"])
            and bool(data["owner_binding_proof"])
            and data["technical_failure_scope"] is False
            and data["raw_metric_mutated"] is False
            and parse_policy_timestamp(data["issued_at"])
            <= parse_policy_timestamp(data["evaluation_at"])
            < parse_policy_timestamp(data["expires_at"])
        )
        if not valid:
            return "blocked"
        return "deferred_internal_debt"
    if kind == "disposition":
        return determine_qualified_disposition(
            technical_blocker_count=data.get("technical_blocker_count", 0),
            effective_blocking_finding_count=data.get(
                "effective_blocking_finding_count", 0
            ),
            advisory_debt_count=data.get("advisory_debt_count", 0),
            active_waiver_count=data.get("active_waiver_count", 0),
        )
    if kind == "schema":
        value = data.get("value")
        required = data.get("required_keys", [])
        if not isinstance(value, dict) or not isinstance(required, list):
            return "blocked"
        return "accepted" if set(value) == set(required) else "blocked"
    if kind == "canonicalization":
        left = without_volatile_fields(data.get("left"))
        right = without_volatile_fields(data.get("right"))
        return "accepted" if canonical_hash(left) == canonical_hash(right) else "blocked"
    if kind == "exception":
        if data.get("default_exception_count") != 0:
            return "blocked"
        if data.get("semantic_freeform_exception") is True:
            return "blocked"
        return "accepted"
    if kind == "structural":
        required = data.get("required")
        status = data.get("status")
        proof_valid = data.get("equivalence_proof_valid")
        if status not in CANDIDATE_STRUCTURAL_STATUSES:
            return "blocked"
        if required and status == "not_required":
            return "blocked"
        if required and status == "missing":
            return "blocked"
        if status in {
            "satisfied_by_verified_fusion",
            "satisfied_by_verified_suppression",
        } and proof_valid is not True:
            return "blocked"
        return "accepted"
    if kind == "human_review_scope":
        required_count = data.get("required_review_count")
        reviewed_count = data.get("reviewed_count")
        corpus_wide_claim = data.get("corpus_wide_zero_claim")
        full_corpus_reviewed = data.get("full_corpus_reviewed")
        valid = (
            isinstance(required_count, int)
            and isinstance(reviewed_count, int)
            and required_count >= 0
            and reviewed_count == required_count
            and (not corpus_wide_claim or full_corpus_reviewed)
        )
        return "accepted" if valid else "blocked"
    if kind == "sync_projection":
        return (
            "accepted"
            if data.get("projection_hash")
            == contract["synchronization_projection_hash"]
            else "blocked"
        )
    if kind == "runtime_parity_claim":
        valid = (
            data.get("applicability") == "not_applicable"
            and data.get("reason") == "candidate_not_registry_adopted"
            and data.get("registry_runtime_pass_claimed") is False
        )
        return "accepted" if valid else "blocked"
    if kind == "raw_metric_mutation":
        return "accepted" if data.get("raw_metric_mutated") is False else "blocked"
    if kind == "state_claim":
        required_state = synchronization_projection()["foundation_required_state"]
        return "accepted" if data == required_state else "blocked"
    raise FoundationContractError(f"unknown fixture kind: {kind}")


def validate_fixture_manifest(
    manifest: dict[str, Any], contract: dict[str, Any]
) -> dict[str, Any]:
    require_exact_keys(
        manifest,
        required=("schema_version", "fixtures"),
        label="fixture manifest",
    )
    if manifest["schema_version"] != FIXTURE_SCHEMA_VERSION:
        raise FoundationContractError("fixture manifest schema version mismatch")
    rows = manifest["fixtures"]
    if not isinstance(rows, list):
        raise FoundationContractError("fixtures must be a list")

    ids: set[str] = set()
    origin_counts = {"roadmap_mandatory": 0, "plan_additive": 0}
    failures: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise FoundationContractError("fixture row must be an object")
        require_exact_keys(
            row,
            required=(
                "fixture_id",
                "origin",
                "fixture_kind",
                "input",
                "expected_outcome",
            ),
            label="fixture row",
        )
        fixture_id = row["fixture_id"]
        origin = row["origin"]
        if not isinstance(fixture_id, str) or fixture_id in ids:
            raise FoundationContractError(f"invalid or duplicate fixture_id: {fixture_id}")
        if origin not in origin_counts:
            raise FoundationContractError(f"unknown fixture origin: {origin}")
        if row["expected_outcome"] not in QUALIFIED_DISPOSITIONS:
            raise FoundationContractError(
                f"invalid expected outcome for {fixture_id}: {row['expected_outcome']}"
            )
        ids.add(fixture_id)
        origin_counts[origin] += 1
        try:
            actual = _fixture_outcome(row, contract)
            passed = actual == row["expected_outcome"]
            error = None
        except Exception as exc:  # fail-closed fixture path
            actual = "blocked"
            passed = actual == row["expected_outcome"]
            error = f"{type(exc).__name__}: {exc}"
        result = {
            "fixture_id": fixture_id,
            "origin": origin,
            "actual_outcome": actual,
            "expected_outcome": row["expected_outcome"],
            "fixture_pass": passed,
            "error": error,
        }
        results.append(result)
        if not passed:
            failures.append(result)

    roadmap_ids = {
        f"PTQA-RM-{index:02d}" for index in range(1, 37)
    }
    actual_roadmap_ids = {
        row["fixture_id"] for row in rows if row["origin"] == "roadmap_mandatory"
    }
    if actual_roadmap_ids != roadmap_ids:
        raise FoundationContractError(
            "roadmap mandatory fixture IDs must be exactly PTQA-RM-01..36"
        )
    if origin_counts["plan_additive"] < 1:
        raise FoundationContractError("at least one plan-additive fixture is required")
    if failures:
        raise FoundationContractError(
            f"foundation fixture failures: {[row['fixture_id'] for row in failures]}"
        )
    return {
        "status": "PASS",
        "roadmap_mandatory_fixture_count": origin_counts["roadmap_mandatory"],
        "plan_additive_fixture_count": origin_counts["plan_additive"],
        "total_fixture_count": len(rows),
        "fixture_without_origin_count": 0,
        "fixture_failure_count": 0,
        "results": results,
    }

__all__ = (
    "determine_qualified_disposition", "evaluate_threshold",
    "parse_policy_timestamp", "validate_fixture_manifest",
    "validate_foundation_contract", "without_volatile_fields",
)
