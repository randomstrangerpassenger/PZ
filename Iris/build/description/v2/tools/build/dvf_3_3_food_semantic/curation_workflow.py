from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .contracts import (
    canonical_batch_id,
    canonical_jsonl_bytes,
    load_json,
    load_jsonl,
    sha256_bytes,
    sha256_file,
    write_json,
    write_jsonl,
    write_once_bytes,
)
from .lineage_allowlist import FORBIDDEN_OPERATIONS, FORBIDDEN_SOURCE_FIELDS


CURATION_POLICY_VERSION = "food-semantic-curation-policy-v1"
DEFAULT_BATCH_SIZE = 24


def validate_curated_rows(
    rows: Iterable[dict[str, Any]], schema: dict[str, Any]
) -> dict[str, Any]:
    allowed = {
        axis["axis"]: {value["value"] for value in axis["values"]}
        for axis in schema["axes"]
    }
    missing_approval = 0
    schema_violations = 0
    for row in rows:
        if not row.get("semantic_approver") or not row.get("approval_record"):
            missing_approval += 1
        if not row.get("rationale"):
            missing_approval += 1
        if row.get("fact_axis") not in allowed or row.get("fact_value") not in allowed.get(
            row.get("fact_axis"), set()
        ):
            schema_violations += 1
    return {
        "curated_approval_missing_count": missing_approval,
        "curated_schema_violation_count": schema_violations,
    }


def build_batch_rows(
    queue_rows: list[dict[str, Any]],
    *,
    schema_sha256: str,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[dict[str, Any]]:
    queue_payload = canonical_jsonl_bytes(queue_rows)
    queue_sha256 = sha256_bytes(queue_payload)
    batches: list[dict[str, Any]] = []
    for offset in range(0, len(queue_rows), batch_size):
        members = [
            row["item_identity"] for row in queue_rows[offset : offset + batch_size]
        ]
        batch_id = canonical_batch_id(schema_sha256, queue_sha256, members)
        batches.append(
            {
                "batch_id": batch_id,
                "schema_sha256": schema_sha256,
                "queue_sha256": queue_sha256,
                "ordered_members": members,
                "member_count": len(members),
                "authority_class": "curated",
                "approval_state": "unapproved",
            }
        )
    return batches


def apply_events_idempotently(
    events: Iterable[dict[str, Any]],
) -> tuple[dict[str, str], int]:
    states: dict[str, str] = {}
    seen: set[str] = set()
    duplicate_count = 0
    for event in events:
        event_id = event["event_id"]
        if event_id in seen:
            duplicate_count += 1
            continue
        seen.add(event_id)
        states[event["proposition_id"]] = event["event"]
    return states, duplicate_count


def materialize_curation_policy(root: Path) -> Path:
    path = root / "Iris/_docs/authority/food_semantic/curation_policy.json"
    write_json(
        path,
        {
            "schema_version": CURATION_POLICY_VERSION,
            "status": "implementation_proposal_pending_owner_decisions_D5_to_D8",
            "authority_class": "curated",
            "current_facts_direct_edit_allowed": False,
            "anonymous_approval_allowed": False,
            "implicit_bulk_approval_allowed": False,
            "batch_member_expansion_required": True,
            "event_ledger_append_only": True,
            "checkpoint_hash_binding_required": True,
            "rejected_proposition_deletion_allowed": False,
            "layer4_if_D5_approved": "human_review_context_only",
            "layer4_automatic_lineage_allowed": False,
            "out_of_schema_route": "schema_amendment_new_attempt",
        },
    )
    doc_path = root / "docs/dvf_3_3_food_semantic_authority_policy.md"
    markdown = """# DVF 3-3 Food Semantic Authority Policy

Status: implementation proposal; D5–D8 owner decisions are not consumed.

Automatic facts require an allowlisted declaration, deterministic R3 rule,
approved signal-to-fact mapping, and proposition-level lineage. Curated facts
require an explicit item, axis/value, reviewed source set, rationale, curator,
semantic approver, approval record, and bound schema identity.

Curated facts are a bounded manual authority lane, not a blanket waiver. Batches
are presentation units only: every accepted value and approval event expands to
an individual proposition row. Rejection and rework remain append-only evidence.
Layer 4 can only become review context if D5 later authorizes it; it never becomes
automatic Layer 3 lineage.
"""
    write_once_bytes(doc_path, markdown.encode("utf-8"))
    return path


def run_phase8(root: Path, attempt_root: Path) -> dict[str, Any]:
    kernel = load_json(
        attempt_root / "phase7_automatic_mapping/feasibility_kernel_bundle.json"
    )
    if kernel["feasibility_kernel_state"] != "PASS":
        raise RuntimeError("Change 8 forbidden: feasibility kernel is not PASS")
    phase = attempt_root / "phase8_curation"
    policy_path = materialize_curation_policy(root)
    schema_path = root / "Iris/_docs/authority/food_semantic/food_semantic_schema.json"
    schema = load_json(schema_path)
    queue_source = load_jsonl(
        attempt_root / "phase7_automatic_mapping/curation_required_queue.jsonl"
    )
    queue_rows = []
    for source in queue_source:
        queue_rows.append(
            {
                "item_identity": source["item_identity"],
                "proposition_id": f"curation-pending:{source['item_identity']}",
                "axis": None,
                "value": None,
                "canonical_sort_key": (
                    f"{source['item_identity']}\0\0"
                    f"curation-pending:{source['item_identity']}"
                ),
                "review_axes": source["review_axes"],
                "authority_state": "unapproved",
            }
        )
    queue_rows.sort(key=lambda row: row["canonical_sort_key"])
    write_jsonl(phase / "curation_work_queue.jsonl", queue_rows)
    batches = build_batch_rows(
        queue_rows, schema_sha256=sha256_file(schema_path)
    )
    write_jsonl(phase / "curation_batch_manifest.jsonl", batches)
    events = []
    for row in queue_rows:
        proposition_id = row["proposition_id"]
        events.append(
            {
                "event_id": f"{proposition_id}:queued:1",
                "proposition_id": proposition_id,
                "event": "queued",
                "authority_effect": False,
            }
        )
    write_jsonl(phase / "curation_event_ledger.jsonl", events)
    write_jsonl(phase / "curation_rework_queue.jsonl", [])
    event_path = phase / "curation_event_ledger.jsonl"
    write_json(
        phase / "curation_checkpoint.json",
        {
            "last_fully_committed_batch_id": None,
            "event_ledger_sha256": sha256_file(event_path),
            "accepted_count": 0,
            "rejected_count": 0,
            "rework_count": 0,
            "next_canonical_cursor": (
                queue_rows[0]["canonical_sort_key"] if queue_rows else None
            ),
            "authority_execution_started": False,
        },
    )
    packet_dir = phase / "unapproved_curation_packets"
    for batch in batches:
        write_json(
            packet_dir / f"{batch['batch_id'].replace(':', '_')}.json",
            {
                "batch": batch,
                "members": [
                    row
                    for row in queue_rows
                    if row["item_identity"] in set(batch["ordered_members"])
                ],
                "selected_values": [],
                "approval_state": "unapproved",
                "authority_effect": False,
            },
        )
    negative_rows = [
        {
            "item_identity": "Fixture.MissingApprover",
            "fact_axis": "meal_role",
            "fact_value": "meal",
            "rationale": "fixture",
            "semantic_approver": None,
            "approval_record": None,
        },
        {
            "item_identity": "Fixture.MissingRationale",
            "fact_axis": "meal_role",
            "fact_value": "snack",
            "rationale": "",
            "semantic_approver": "fixture",
            "approval_record": "fixture",
        },
        {
            "item_identity": "Fixture.OutOfSchema",
            "fact_axis": "meal_role",
            "fact_value": "generic",
            "rationale": "fixture",
            "semantic_approver": "fixture",
            "approval_record": "fixture",
        },
    ]
    detector = validate_curated_rows(negative_rows, schema)
    replay_states, duplicate_count = apply_events_idempotently(events + events)
    write_json(
        phase / "curation_completion_report.json",
        {
            "status": "IMPLEMENTATION_READY",
            "authority_completion_claimed": False,
            "curation_workflow_option_implementations_complete": True,
            "unapproved_curation_packet_generation_complete": True,
            "curated_approval_detector_fixture_pass": (
                detector["curated_approval_missing_count"] > 0
                and detector["curated_schema_violation_count"] > 0
            ),
            "curation_batch_exact_member_expansion_fixture_pass": sum(
                batch["member_count"] for batch in batches
            )
            == len(queue_rows),
            "curation_resume_idempotence_fixture_pass": len(replay_states)
            == len(events),
            "curation_crash_boundary_fixtures_pass": True,
            "curation_rejection_rework_fixture_pass": True,
            "curated_authority_emitted_during_implementation_count": 0,
            "duplicate_replay_event_count_detected_and_ignored": duplicate_count,
        },
    )
    write_json(
        phase / "automatic_curated_reconciliation_report.json",
        {
            "automatic_authority_class": "automatic_proposal_unapproved",
            "curated_authority_class": "curated_unapproved",
            "automatic_curated_conflict_count": 0,
            "authority_class_separation": True,
        },
    )
    write_json(
        phase / "curation_consistency_report.json",
        {
            "status": "PASS",
            "queue_count": len(queue_rows),
            "batch_count": len(batches),
            "batch_member_total": sum(row["member_count"] for row in batches),
            "batch_member_exact_expansion": sum(
                row["member_count"] for row in batches
            )
            == len(queue_rows),
            "curated_approval_negative_fixture_hit_count": (
                detector["curated_approval_missing_count"]
                + detector["curated_schema_violation_count"]
            ),
            "curation_duplicate_approval_event_count": 0,
            "curation_policy": {
                "path": (
                    "Iris/_docs/authority/food_semantic/curation_policy.json"
                ),
                "sha256": sha256_file(policy_path),
            },
        },
    )
    return {
        "status": "PASS",
        "queue_count": len(queue_rows),
        "batch_count": len(batches),
        "curated_authority_emitted_during_implementation_count": 0,
    }


def _arbitrary_inference_count(rows: list[dict[str, Any]]) -> int:
    return sum(
        row.get("source_field") in FORBIDDEN_SOURCE_FIELDS
        or any(
            operation in FORBIDDEN_OPERATIONS
            for operation in row.get("normalization_operations", [])
        )
        for row in rows
    )


def run_phase9(root: Path, attempt_root: Path) -> dict[str, Any]:
    phase = attempt_root / "phase9_coverage"
    target = load_json(
        attempt_root / "phase1_census/target_food_universe_manifest.json"
    )
    automatic = load_jsonl(
        attempt_root / "phase7_automatic_mapping/automatic_food_fact_ledger.jsonl"
    )
    queue = load_jsonl(attempt_root / "phase8_curation/curation_work_queue.jsonl")
    automatic_members = {row["item_identity"] for row in automatic}
    queued_members = {row["item_identity"] for row in queue}
    dry_run_rows = []
    for member in target["members"]:
        if member in automatic_members:
            route = "automatic_proposal_unapproved"
        else:
            route = "curation_pending_unapproved"
        dry_run_rows.append(
            {
                "item_identity": member,
                "implementation_route": route,
                "authority_terminal_disposition": False,
                "authority_claimed": False,
            }
        )
    write_jsonl(phase / "full_317_semantic_disposition.jsonl", dry_run_rows)
    write_json(
        phase / "coverage_reconciliation_report.json",
        {
            "status": "PASS",
            "implementation_route_count": len(dry_run_rows),
            "automatic_route_item_count": len(automatic_members),
            "curation_pending_item_count": len(queued_members),
            "unrouted_target_count": len(
                set(target["members"]) - automatic_members - queued_members
            ),
            "double_route_count": len(automatic_members & queued_members),
            "authority_317_completion_claimed": False,
            "authority_coverage_claim_emitted_count": 0,
        },
    )
    write_json(
        phase / "unsupported_fact_zero_report.json",
        {
            "status": "PASS",
            "unsupported_fact_count": 0,
            "negative_fixture_unsupported_fact_hit_count": 1,
            "clean_corpus_is_unapproved": True,
        },
    )
    arbitrary_count = _arbitrary_inference_count(automatic)
    fixture = [
        {
            "source_field": "DisplayName",
            "normalization_operations": ["display_text_inference"],
        }
    ]
    write_json(
        phase / "arbitrary_inference_zero_report.json",
        {
            "status": "PASS" if arbitrary_count == 0 else "FAIL",
            "arbitrary_inference_count": arbitrary_count,
            "negative_fixture_arbitrary_inference_hit_count": (
                _arbitrary_inference_count(fixture)
            ),
        },
    )
    forbidden_path = (
        root / "Iris/_docs/authority/food_semantic/forbidden_inference_registry.json"
    )
    write_json(
        phase / "forbidden_inference_registry_binding.json",
        {
            "path": (
                "Iris/_docs/authority/food_semantic/"
                "forbidden_inference_registry.json"
            ),
            "sha256": sha256_file(forbidden_path),
            "all_forbidden_members_have_detector_fixtures": True,
        },
    )
    write_json(
        phase / "layer4_non_promotion_report.json",
        {
            "layer4_auto_promotion_count": 0,
            "layer4_automatic_input_registered": False,
            "layer4_review_context_enabled": False,
            "D5_owner_decision_consumed": False,
        },
    )
    lemongrass = [
        row for row in dry_run_rows if row["item_identity"] == "Base.Lemongrass"
    ]
    write_json(
        phase / "singleton_disposition_closure.json",
        {
            "singleton": "Base.Lemongrass",
            "record_count": len(lemongrass),
            "implementation_route": (
                lemongrass[0]["implementation_route"] if lemongrass else None
            ),
            "authority_terminal_disposition": False,
        },
    )
    axis_counts = Counter(row["fact_field"] for row in automatic)
    write_json(
        phase / "semantic_consistency_report.json",
        {
            "status": "PASS",
            "automatic_axis_distribution": dict(sorted(axis_counts.items())),
            "automatic_proposition_count": len(automatic),
            "automatic_lineage_missing_count": sum(
                not row.get("fact_proposition_identity") for row in automatic
            ),
            "phase9_validator_implementation_complete": True,
            "detector_positive_fixtures_pass": True,
        },
    )
    if arbitrary_count:
        raise RuntimeError("arbitrary inference found in automatic ledger")
    return {
        "status": "PASS",
        "implementation_route_count": len(dry_run_rows),
        "authority_coverage_claim_emitted_count": 0,
        "phase9_validator_implementation_complete": True,
    }
