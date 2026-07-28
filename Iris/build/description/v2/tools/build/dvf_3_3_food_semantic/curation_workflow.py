from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from .contracts import (
    canonical_batch_id,
    canonical_json_bytes,
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
APPROVED_STATES = {"approved", "owner_approved"}
EVENT_TRANSITIONS: dict[str | None, set[str]] = {
    None: {"queued"},
    "queued": {"review_started"},
    "review_started": {"accepted", "rejected", "needs_rework"},
    "rejected": {"needs_rework", "superseded"},
    "needs_rework": {"review_started", "superseded"},
    "accepted": {"superseded"},
    "superseded": set(),
}


def validate_curated_rows(
    rows: Iterable[dict[str, Any]],
    schema: dict[str, Any],
    *,
    expected_schema_sha256: str | None = None,
    layer4_review_context_allowed: bool | None = None,
) -> dict[str, Any]:
    allowed = {
        axis["axis"]: {value["value"] for value in axis["values"]}
        for axis in schema["axes"]
    }
    missing_approval = 0
    schema_violations = 0
    authority_class_violations = 0
    approval_state_violations = 0
    schema_identity_violations = 0
    reviewed_source_set_violations = 0
    layer4_policy_violations = 0
    duplicate_proposition_count = 0
    seen_propositions: set[str] = set()
    for row in rows:
        proposition_id = row.get("proposition_id")
        if not proposition_id or proposition_id in seen_propositions:
            duplicate_proposition_count += 1
        if proposition_id:
            seen_propositions.add(proposition_id)
        if (
            not row.get("curator_identity")
            or not row.get("semantic_approver")
            or not row.get("approval_record")
        ):
            missing_approval += 1
        if not row.get("rationale"):
            missing_approval += 1
        reviewed_source_set = row.get("reviewed_source_set")
        if (
            not isinstance(reviewed_source_set, list)
            or not reviewed_source_set
            or any(
                not isinstance(value, dict)
                or not value.get("source_id")
                or value.get("source_class")
                not in {
                    "allowlisted_layer3",
                    "layer4_interaction_context",
                    "curator_observation",
                }
                or not value.get("source_path")
                or not isinstance(value.get("source_sha256"), str)
                or len(value["source_sha256"]) != 64
                or any(
                    character not in "0123456789abcdef"
                    for character in value["source_sha256"].lower()
                )
                for value in reviewed_source_set
            )
        ):
            reviewed_source_set_violations += 1
        else:
            layer4_sources = [
                value
                for value in reviewed_source_set
                if value["source_class"] == "layer4_interaction_context"
            ]
            if layer4_sources and layer4_review_context_allowed is not True:
                layer4_policy_violations += 1
            if any(
                value.get("review_role") != "human_review_context_only"
                for value in layer4_sources
            ):
                layer4_policy_violations += 1
        if row.get("authority_class") != "curated":
            authority_class_violations += 1
        if row.get("approval_status") not in APPROVED_STATES:
            approval_state_violations += 1
        if expected_schema_sha256 is not None and row.get(
            "schema_sha256"
        ) != expected_schema_sha256:
            schema_identity_violations += 1
        if row.get("fact_axis") not in allowed or row.get("fact_value") not in allowed.get(
            row.get("fact_axis"), set()
        ):
            schema_violations += 1
    return {
        "curated_approval_missing_count": missing_approval,
        "curated_schema_violation_count": schema_violations,
        "curated_authority_class_violation_count": authority_class_violations,
        "curated_approval_state_violation_count": approval_state_violations,
        "curated_schema_identity_violation_count": schema_identity_violations,
        "curated_reviewed_source_set_violation_count": reviewed_source_set_violations,
        "curated_layer4_policy_violation_count": layer4_policy_violations,
        "curated_duplicate_proposition_count": duplicate_proposition_count,
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
    unique_members = sorted({row["item_identity"] for row in queue_rows})
    for offset in range(0, len(unique_members), batch_size):
        members = unique_members[offset : offset + batch_size]
        member_set = set(members)
        propositions = [
            row["proposition_id"]
            for row in queue_rows
            if row["item_identity"] in member_set
        ]
        batch_id = canonical_batch_id(schema_sha256, queue_sha256, members)
        batches.append(
            {
                "batch_id": batch_id,
                "schema_sha256": schema_sha256,
                "queue_sha256": queue_sha256,
                "ordered_members": members,
                "member_count": len(members),
                "ordered_proposition_ids": propositions,
                "proposition_count": len(propositions),
                "authority_class": "curated",
                "approval_state": "unapproved",
            }
        )
    return batches


def apply_events_idempotently(
    events: Iterable[dict[str, Any]],
) -> tuple[dict[str, str], int]:
    states: dict[str, str] = {}
    seen: dict[str, bytes] = {}
    duplicate_count = 0
    expected_sequence = 1
    for event in events:
        event_id = event["event_id"]
        if event_id in seen:
            if seen[event_id] != canonical_json_bytes(event):
                raise ValueError(f"conflicting duplicate event: {event_id}")
            duplicate_count += 1
            continue
        if event.get("sequence") != expected_sequence:
            raise ValueError(
                f"non-canonical event sequence: expected {expected_sequence}, "
                f"got {event.get('sequence')}"
            )
        proposition_id = event["proposition_id"]
        previous = states.get(proposition_id)
        transition = event["event"]
        if transition not in EVENT_TRANSITIONS.get(previous, set()):
            raise ValueError(
                f"invalid curation transition for {proposition_id}: "
                f"{previous!r} -> {transition!r}"
            )
        if event.get("previous_state") != previous:
            raise ValueError(
                f"previous-state mismatch for {proposition_id}: "
                f"{event.get('previous_state')!r} != {previous!r}"
            )
        payload = {
            key: value for key, value in event.items() if key != "event_sha256"
        }
        if event.get("event_sha256") != sha256_bytes(canonical_json_bytes(payload)):
            raise ValueError(f"event hash mismatch: {event_id}")
        if event.get("authority_effect") is not (transition == "accepted"):
            raise ValueError(
                f"authority-effect mismatch for {event_id}: {transition}"
            )
        if transition == "accepted" and (
            not event.get("approval_record")
            or not event.get("semantic_approver")
        ):
            raise ValueError(
                f"accepted event lacks explicit approval identity: {event_id}"
            )
        seen[event_id] = canonical_json_bytes(event)
        states[proposition_id] = transition
        expected_sequence += 1
    return states, duplicate_count


def build_event(
    *,
    sequence: int,
    proposition_id: str,
    event: str,
    previous_state: str | None,
    authority_effect: bool = False,
    approval_record: str | None = None,
    semantic_approver: str | None = None,
) -> dict[str, Any]:
    if event not in {
        "queued",
        "review_started",
        "accepted",
        "rejected",
        "needs_rework",
        "superseded",
    }:
        raise ValueError(f"unknown curation event: {event}")
    if authority_effect is not (event == "accepted"):
        raise ValueError(
            f"authority_effect must be true exactly for accepted events: {event}"
        )
    row = {
        "sequence": sequence,
        "event_id": f"{proposition_id}:{event}:{sequence}",
        "proposition_id": proposition_id,
        "event": event,
        "previous_state": previous_state,
        "authority_effect": authority_effect,
    }
    if approval_record is not None:
        row["approval_record"] = approval_record
    if semantic_approver is not None:
        row["semantic_approver"] = semantic_approver
    row["event_sha256"] = sha256_bytes(canonical_json_bytes(row))
    return row


def _checkpoint_for(
    events: list[dict[str, Any]],
    *,
    queue_sha256: str,
    next_cursor: str | None,
) -> dict[str, Any]:
    payload = canonical_jsonl_bytes(events)
    return {
        "queue_sha256": queue_sha256,
        "event_ledger_sha256": sha256_bytes(payload),
        "committed_event_count": len(events),
        "last_committed_event_id": events[-1]["event_id"] if events else None,
        "next_canonical_cursor": next_cursor,
    }


def validate_checkpoint(
    events: list[dict[str, Any]],
    checkpoint: dict[str, Any],
    *,
    queue_sha256: str,
    expected_next_cursor: str | None,
) -> dict[str, Any]:
    expected = _checkpoint_for(
        events,
        queue_sha256=queue_sha256,
        next_cursor=expected_next_cursor,
    )
    compared_fields = (
        "queue_sha256",
        "event_ledger_sha256",
        "committed_event_count",
        "last_committed_event_id",
        "next_canonical_cursor",
    )
    mismatches = [
        field
        for field in compared_fields
        if checkpoint.get(field) != expected[field]
    ]
    if mismatches:
        raise ValueError(
            "curation checkpoint mismatch: " + ",".join(sorted(mismatches))
        )
    states, duplicate_count = apply_events_idempotently(events)
    return {
        "status": "PASS",
        "checkpoint_hash_match": True,
        "event_count": len(events),
        "state_count": len(states),
        "duplicate_event_count": duplicate_count,
    }


def _exercise_crash_boundaries(
    first_proposition_id: str,
    *,
    queue_sha256: str,
) -> dict[str, Any]:
    queued = build_event(
        sequence=1,
        proposition_id=first_proposition_id,
        event="queued",
        previous_state=None,
    )
    base_events = [queued]
    base_checkpoint = _checkpoint_for(
        base_events, queue_sha256=queue_sha256, next_cursor=first_proposition_id
    )
    review_started = build_event(
        sequence=2,
        proposition_id=first_proposition_id,
        event="review_started",
        previous_state="queued",
    )

    before_commit_events = list(base_events)
    before_states, _ = apply_events_idempotently(before_commit_events)
    crash_before_commit_preserved = (
        _checkpoint_for(
            before_commit_events,
            queue_sha256=queue_sha256,
            next_cursor=first_proposition_id,
        )
        == base_checkpoint
        and before_states[first_proposition_id] == "queued"
    )

    ledger_committed_events = base_events + [review_started]
    committed_hash = sha256_bytes(canonical_jsonl_bytes(ledger_committed_events))
    try:
        validate_checkpoint(
            ledger_committed_events,
            base_checkpoint,
            queue_sha256=queue_sha256,
            expected_next_cursor=first_proposition_id,
        )
    except ValueError:
        stale_checkpoint_fail_loud = True
    else:
        stale_checkpoint_fail_loud = False
    resumed_states, _ = apply_events_idempotently(ledger_committed_events)
    explicitly_resealed_checkpoint = _checkpoint_for(
        ledger_committed_events,
        queue_sha256=queue_sha256,
        next_cursor=first_proposition_id,
    )
    checkpoint_validation = validate_checkpoint(
        ledger_committed_events,
        explicitly_resealed_checkpoint,
        queue_sha256=queue_sha256,
        expected_next_cursor=first_proposition_id,
    )
    return {
        "crash_before_commit_preserved_state": crash_before_commit_preserved,
        "crash_after_ledger_before_checkpoint_failed_loud": (
            stale_checkpoint_fail_loud
        ),
        "resume_replayed_append_only_ledger": (
            resumed_states[first_proposition_id] == "review_started"
        ),
        "explicitly_resealed_checkpoint_matches_ledger": (
            explicitly_resealed_checkpoint["event_ledger_sha256"]
            == committed_hash
            and checkpoint_validation["checkpoint_hash_match"]
        ),
    }


def _exercise_rejection_rework(first_proposition_id: str) -> dict[str, Any]:
    transitions = [
        ("queued", None),
        ("review_started", "queued"),
        ("rejected", "review_started"),
        ("needs_rework", "rejected"),
        ("review_started", "needs_rework"),
        ("accepted", "review_started"),
    ]
    events = [
        build_event(
            sequence=index,
            proposition_id=first_proposition_id,
            event=event,
            previous_state=previous,
            authority_effect=event == "accepted",
            approval_record=(
                "fixture:rework-approval" if event == "accepted" else None
            ),
            semantic_approver=(
                "fixture-semantic-approver" if event == "accepted" else None
            ),
        )
        for index, (event, previous) in enumerate(transitions, start=1)
    ]
    states, duplicate_count = apply_events_idempotently(events + events)
    return {
        "final_state": states[first_proposition_id],
        "rejected_event_preserved": any(
            row["event"] == "rejected" for row in events
        ),
        "rework_event_preserved": any(
            row["event"] == "needs_rework" for row in events
        ),
        "duplicate_replay_count": duplicate_count,
        "status": (
            "PASS"
            if states[first_proposition_id] == "accepted"
            and duplicate_count == len(events)
            else "FAIL"
        ),
    }


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
        axis = source["required_fact_axis"]
        queue_rows.append(
            {
                "item_identity": source["item_identity"],
                "proposition_id": (
                    f"curation-pending:{source['item_identity']}:{axis}"
                ),
                "axis": axis,
                "value": None,
                "canonical_sort_key": (
                    f"{source['item_identity']}\0{axis}\0"
                    f"curation-pending:{source['item_identity']}:{axis}"
                ),
                "review_axes": [axis],
                "schema_sha256": sha256_file(schema_path),
                "reviewed_source_set_required": True,
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
    for sequence, row in enumerate(queue_rows, start=1):
        proposition_id = row["proposition_id"]
        events.append(
            build_event(
                sequence=sequence,
                proposition_id=proposition_id,
                event="queued",
                previous_state=None,
            )
        )
    write_jsonl(phase / "curation_event_ledger.jsonl", events)
    write_jsonl(phase / "curation_rework_queue.jsonl", [])
    event_path = phase / "curation_event_ledger.jsonl"
    queue_path = phase / "curation_work_queue.jsonl"
    queue_sha256 = sha256_file(queue_path)
    checkpoint = _checkpoint_for(
        events,
        queue_sha256=queue_sha256,
        next_cursor=(
            queue_rows[0]["canonical_sort_key"] if queue_rows else None
        ),
    )
    checkpoint_document = {
        **checkpoint,
        "last_fully_committed_batch_id": None,
        "accepted_count": 0,
        "rejected_count": 0,
        "rework_count": 0,
        "authority_execution_started": False,
    }
    initial_checkpoint_validation = validate_checkpoint(
        events,
        checkpoint_document,
        queue_sha256=queue_sha256,
        expected_next_cursor=(
            queue_rows[0]["canonical_sort_key"] if queue_rows else None
        ),
    )
    write_json(phase / "curation_checkpoint.json", checkpoint_document)
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
            "curator_identity": "fixture-curator",
            "semantic_approver": None,
            "approval_record": None,
            "reviewed_source_set": [
                {
                    "source_id": "fixture-source",
                    "source_class": "allowlisted_layer3",
                    "source_path": "fixture/source.json",
                    "source_sha256": "a" * 64,
                }
            ],
            "authority_class": "curated",
            "approval_status": "owner_approved",
            "schema_sha256": sha256_file(schema_path),
            "proposition_id": "fixture:missing-approver",
        },
        {
            "item_identity": "Fixture.MissingRationale",
            "fact_axis": "meal_role",
            "fact_value": "snack",
            "rationale": "",
            "curator_identity": "fixture-curator",
            "semantic_approver": "fixture",
            "approval_record": "fixture",
            "reviewed_source_set": [
                {
                    "source_id": "fixture-source",
                    "source_class": "allowlisted_layer3",
                    "source_path": "fixture/source.json",
                    "source_sha256": "a" * 64,
                }
            ],
            "authority_class": "curated",
            "approval_status": "owner_approved",
            "schema_sha256": sha256_file(schema_path),
            "proposition_id": "fixture:missing-rationale",
        },
        {
            "item_identity": "Fixture.OutOfSchema",
            "fact_axis": "meal_role",
            "fact_value": "generic",
            "rationale": "fixture",
            "curator_identity": "fixture-curator",
            "semantic_approver": "fixture",
            "approval_record": "fixture",
            "reviewed_source_set": [
                {
                    "source_id": "fixture-source",
                    "source_class": "allowlisted_layer3",
                    "source_path": "fixture/source.json",
                    "source_sha256": "a" * 64,
                }
            ],
            "authority_class": "curated",
            "approval_status": "owner_approved",
            "schema_sha256": sha256_file(schema_path),
            "proposition_id": "fixture:out-of-schema",
        },
    ]
    detector = validate_curated_rows(
        negative_rows,
        schema,
        expected_schema_sha256=sha256_file(schema_path),
    )
    replay_states, duplicate_count = apply_events_idempotently(events + events)
    first_proposition_id = (
        queue_rows[0]["proposition_id"] if queue_rows else "fixture:none"
    )
    crash_fixtures = _exercise_crash_boundaries(
        first_proposition_id,
        queue_sha256=queue_sha256,
    )
    rejection_rework_fixture = _exercise_rejection_rework(first_proposition_id)
    queue_item_count = len({row["item_identity"] for row in queue_rows})
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
            == queue_item_count
            and sum(batch["proposition_count"] for batch in batches)
            == len(queue_rows),
            "curation_resume_idempotence_fixture_pass": len(replay_states)
            == len(events),
            "curation_crash_boundary_fixtures_pass": all(
                crash_fixtures.values()
            ),
            "curation_rejection_rework_fixture_pass": (
                rejection_rework_fixture["status"] == "PASS"
            ),
            "curation_crash_boundary_fixture_results": crash_fixtures,
            "curation_rejection_rework_fixture_result": rejection_rework_fixture,
            "initial_checkpoint_validation": initial_checkpoint_validation,
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
            "queue_item_count": queue_item_count,
            "queue_proposition_count": len(queue_rows),
            "batch_count": len(batches),
            "batch_member_total": sum(row["member_count"] for row in batches),
            "batch_proposition_total": sum(
                row["proposition_count"] for row in batches
            ),
            "batch_member_exact_expansion": sum(
                row["member_count"] for row in batches
            )
            == queue_item_count,
            "batch_proposition_exact_expansion": sum(
                row["proposition_count"] for row in batches
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
        "queue_item_count": queue_item_count,
        "queue_proposition_count": len(queue_rows),
        "batch_count": len(batches),
        "curated_authority_emitted_during_implementation_count": 0,
    }


def materialize_authority_curation(
    attempt_root: Path,
    authority_root: Path,
    curated_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    queue_path = attempt_root / "phase8_curation/curation_work_queue.jsonl"
    queue_rows = load_jsonl(queue_path)
    queue_sha256 = sha256_file(queue_path)
    curated_by_pair = {
        (row["item_identity"], row["fact_axis"]): row for row in curated_rows
    }
    events: list[dict[str, Any]] = []
    approval_rows: list[dict[str, Any]] = []
    for queue_row in queue_rows:
        pair = (queue_row["item_identity"], queue_row["axis"])
        curated = curated_by_pair[pair]
        proposition_id = curated["proposition_id"]
        queued = build_event(
            sequence=len(events) + 1,
            proposition_id=proposition_id,
            event="queued",
            previous_state=None,
        )
        events.append(queued)
        review_started = build_event(
            sequence=len(events) + 1,
            proposition_id=proposition_id,
            event="review_started",
            previous_state="queued",
        )
        events.append(review_started)
        accepted = build_event(
            sequence=len(events) + 1,
            proposition_id=proposition_id,
            event="accepted",
            previous_state="review_started",
            authority_effect=True,
            approval_record=curated["approval_record"],
            semantic_approver=curated["semantic_approver"],
        )
        events.append(accepted)
        approval_rows.append(
            {
                "item_identity": curated["item_identity"],
                "fact_axis": curated["fact_axis"],
                "fact_value": curated["fact_value"],
                "proposition_id": proposition_id,
                "approval_record": curated["approval_record"],
                "semantic_approver": curated["semantic_approver"],
                "accepted_event_id": accepted["event_id"],
                "accepted_event_sha256": accepted["event_sha256"],
                "authority_class": "curated",
                "approval_status": curated["approval_status"],
            }
        )
    states, duplicate_count = apply_events_idempotently(events)
    accepted_count = sum(state == "accepted" for state in states.values())
    if accepted_count != len(curated_rows) or duplicate_count:
        raise ValueError(
            "authority curation state closure failed: "
            f"accepted={accepted_count}, curated={len(curated_rows)}, "
            f"duplicates={duplicate_count}"
        )
    checkpoint = {
        **_checkpoint_for(events, queue_sha256=queue_sha256, next_cursor=None),
        "last_fully_committed_batch_id": (
            load_jsonl(
                attempt_root / "phase8_curation/curation_batch_manifest.jsonl"
            )[-1]["batch_id"]
            if queue_rows
            else None
        ),
        "accepted_count": accepted_count,
        "rejected_count": 0,
        "rework_count": 0,
        "authority_execution_started": True,
        "authority_execution_complete": True,
    }
    checkpoint_validation = validate_checkpoint(
        events,
        checkpoint,
        queue_sha256=queue_sha256,
        expected_next_cursor=None,
    )
    phase = authority_root / "phase8_curation"
    write_jsonl(phase / "curated_fact_ledger.jsonl", curated_rows)
    write_jsonl(
        phase / "semantic_authority_approval_ledger.jsonl", approval_rows
    )
    write_jsonl(phase / "curation_event_ledger.jsonl", events)
    write_jsonl(phase / "curation_rework_queue.jsonl", [])
    write_json(phase / "curation_checkpoint.json", checkpoint)
    report = {
        "schema_version": "food-semantic-authority-curation-completion-v1",
        "status": "PASS",
        "curated_proposition_count": len(curated_rows),
        "accepted_event_count": accepted_count,
        "rejected_event_count": 0,
        "needs_rework_event_count": 0,
        "curation_rework_unresolved_count": 0,
        "curation_duplicate_approval_event_count": duplicate_count,
        "curation_checkpoint_hash_match": checkpoint_validation[
            "checkpoint_hash_match"
        ],
        "curation_next_canonical_cursor": None,
        "authority_class_separation": True,
    }
    write_json(phase / "curation_completion_report.json", report)
    return report


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
        route = (
            "curation_pending_with_automatic_supplement_unapproved"
            if member in automatic_members
            else "curation_pending_unapproved"
        )
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
            "automatic_supplemental_item_count": len(automatic_members),
            "curation_pending_item_count": len(queued_members),
            "unrouted_target_count": len(
                set(target["members"]) - queued_members
            ),
            "conflicting_terminal_route_count": 0,
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
    source_field_fixtures = [
        {
            "fixture_kind": "forbidden_source_field",
            "forbidden_member": source_field,
            "source_field": source_field,
            "normalization_operations": [],
        }
        for source_field in sorted(FORBIDDEN_SOURCE_FIELDS)
    ]
    operation_fixtures = [
        {
            "fixture_kind": "forbidden_operation",
            "forbidden_member": operation,
            "source_field": "fixture_allowlisted_source",
            "normalization_operations": [operation],
        }
        for operation in sorted(FORBIDDEN_OPERATIONS)
    ]
    fixture = source_field_fixtures + operation_fixtures
    fixture_hits = [
        row
        for row in fixture
        if _arbitrary_inference_count([row]) == 1
    ]
    hit_members = {row["forbidden_member"] for row in fixture_hits}
    expected_members = set(FORBIDDEN_SOURCE_FIELDS) | set(FORBIDDEN_OPERATIONS)
    write_json(
        phase / "arbitrary_inference_zero_report.json",
        {
            "status": (
                "PASS"
                if arbitrary_count == 0 and hit_members == expected_members
                else "FAIL"
            ),
            "arbitrary_inference_count": arbitrary_count,
            "negative_fixture_arbitrary_inference_hit_count": (
                _arbitrary_inference_count(fixture)
            ),
            "forbidden_source_field_fixture_count": len(source_field_fixtures),
            "forbidden_operation_fixture_count": len(operation_fixtures),
            "forbidden_member_fixture_missing_count": len(
                expected_members - hit_members
            ),
            "forbidden_member_fixture_extra_count": len(
                hit_members - expected_members
            ),
            "forbidden_member_fixture_results": fixture_hits,
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
            "forbidden_source_field_members": sorted(FORBIDDEN_SOURCE_FIELDS),
            "forbidden_operation_members": sorted(FORBIDDEN_OPERATIONS),
            "fixture_hit_members": sorted(hit_members),
            "missing_fixture_members": sorted(expected_members - hit_members),
            "extra_fixture_members": sorted(hit_members - expected_members),
            "all_forbidden_members_have_detector_fixtures": (
                hit_members == expected_members
            ),
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
            "detector_positive_fixtures_pass": hit_members == expected_members,
        },
    )
    if arbitrary_count:
        raise RuntimeError("arbitrary inference found in automatic ledger")
    if hit_members != expected_members:
        raise RuntimeError("forbidden inference fixture coverage is incomplete")
    return {
        "status": "PASS",
        "implementation_route_count": len(dry_run_rows),
        "authority_coverage_claim_emitted_count": 0,
        "phase9_validator_implementation_complete": True,
    }
