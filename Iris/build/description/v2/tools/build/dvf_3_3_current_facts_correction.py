from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Iterable, Sequence


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]
CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
CORRECTION_SPEC = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "authority"
    / "current_facts_correction"
    / "correction-0001.json"
)
CORRECTION_SPEC_REVIEW = CORRECTION_SPEC.with_name(
    "codex_reviewer_spec_attestation.json"
)
SUCCESSOR_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_current_facts_correction_successor"
    / "successors"
    / "correction-0001"
)
CUTOVER_ATTEMPTS_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_registry_operational_cutover"
    / "attempts"
)
INITIAL_ADOPTION_RECEIPT = (
    CUTOVER_ATTEMPTS_ROOT
    / "attempt-0009"
    / "closeout"
    / "registry_adoption_receipt.json"
)
BLOCKER_REQUEST = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "facts_authority_review_blocker_request_attempt_0018.json"
)
REVIEWER_ATTESTATION = BLOCKER_REQUEST.with_name(
    "codex_reviewer_attestation_attempt_0018.json"
)
G2_TERMINAL_HASH_SEAL = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_facts_authority"
    / "attempts"
    / "attempt-0022"
    / "phase13_closeout"
    / "terminal_hash_seal.json"
)

CURRENT_FACTS_PREIMAGE_SHA256 = (
    "1ef1785f12d53fbfdca7e96d372079c16fcec276cbae93280e62908c8a891b40"
)
CURRENT_MANIFEST_PREIMAGE_SHA256 = (
    "7a282be929217f0c117bc1fd86f84b4146d34e92dc1d2833c3c0f943c371c43c"
)
INITIAL_ADOPTION_RECEIPT_SHA256 = (
    "efcc387bb395b561ab67df0cab4e498fe0b429680fc6cc8f6dd96eb94ba49751"
)
BLOCKER_REQUEST_SHA256 = (
    "86f4ad91fad0b8de03e9e037fc1b84a20ebf08fb6251fd69fc2c31b6c504588f"
)
REVIEWER_ATTESTATION_SHA256 = (
    "04b54e150544b68f10b4cc080c39b76cb0b4ec59b6c5bd73be34a5f62d542b6e"
)
G2_TERMINAL_HASH_SEAL_SHA256 = (
    "9a9a37731e8d76399f6b960a0e9beb21bcdd65d8ae39e511337527c5306d0c19"
)
CURRENT_FACTS_REL = "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
CURRENT_MANIFEST_REL = (
    "Iris/build/description/v2/data/dvf_3_3_input_manifest.json"
)
SUCCESSOR_FACTS = SUCCESSOR_ROOT / "successor_facts.jsonl"
SUCCESSOR_MANIFEST = SUCCESSOR_ROOT / "successor_input_manifest.json"
SUCCESSOR_RECEIPT = SUCCESSOR_ROOT / "successor_receipt.json"
COHORT_INVENTORY = SUCCESSOR_ROOT / "cohort_inventory.jsonl"
COHORT_SUMMARY = SUCCESSOR_ROOT / "cohort_summary.json"
PATCH_LEDGER = SUCCESSOR_ROOT / "correction_patch_ledger.jsonl"


class CorrectionError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    if not path.is_file():
        raise CorrectionError(f"required_file_missing:{repo_relative(path)}")
    return sha256_bytes(path.read_bytes())


def canonical_bytes(payload: Any) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def canonical_hash(payload: Any) -> str:
    return sha256_bytes(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    )


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CorrectionError(f"invalid_json:{repo_relative(path)}") from exc
    if not isinstance(payload, dict):
        raise CorrectionError(f"json_object_required:{repo_relative(path)}")
    return payload


def read_jsonl_with_bytes(path: Path) -> tuple[list[dict[str, Any]], list[bytes]]:
    raw_lines = path.read_bytes().splitlines(keepends=True)
    rows: list[dict[str, Any]] = []
    for index, raw_line in enumerate(raw_lines, start=1):
        if not raw_line.strip():
            raise CorrectionError(f"blank_jsonl_line:{repo_relative(path)}:{index}")
        try:
            row = json.loads(raw_line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise CorrectionError(
                f"invalid_jsonl:{repo_relative(path)}:{index}"
            ) from exc
        if not isinstance(row, dict):
            raise CorrectionError(
                f"jsonl_object_required:{repo_relative(path)}:{index}"
            )
        rows.append(row)
    return rows, raw_lines


def write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise CorrectionError(f"append_only_conflict:{repo_relative(path)}")
        return
    with path.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())


def write_once_json(path: Path, payload: Any) -> None:
    write_once(path, canonical_bytes(payload))


def write_once_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    data = b"".join(
        (
            json.dumps(
                row,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")
        for row in rows
    )
    write_once(path, data)


def require_hash(path: Path, expected: str, label: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise CorrectionError(f"{label}_sha256_mismatch:{actual}")


def git_output(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
    ).strip()


def selector_matches(row: dict[str, Any], selector: dict[str, Any]) -> bool:
    kind = selector.get("kind")
    if kind in {"cluster", "cluster_role"}:
        cluster = row.get("slot_meta", {}).get("interaction_cluster", {})
        required_role = selector.get("role")
        return (
            cluster.get("selected_cluster") == selector.get("cluster")
            and (
                required_role is None
                or cluster.get("selected_role") == required_role
            )
            and selector.get("origin")
            in row.get("fact_origin", {}).get("primary_use", [])
        )
    if kind == "identity_fallback":
        return (
            row.get("identity_hint") == selector.get("identity_hint")
            and selector.get("origin")
            in row.get("fact_origin", {}).get("primary_use", [])
        )
    if kind in {"exact_field_value", "seed_value"}:
        field = selector.get("field")
        return (
            isinstance(field, str)
            and row.get(field) == selector.get("value")
            and selector.get("origin")
            in row.get("fact_origin", {}).get(field, [])
        )
    raise CorrectionError(f"unknown_cohort_selector_kind:{kind}")


def build_cohort_inventory(
    rows: list[dict[str, Any]], spec: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, set[str]]]:
    inventory: list[dict[str, Any]] = []
    members_by_id: dict[str, set[str]] = {}
    for selector in spec.get("cohort_selectors", []):
        selector_id = selector.get("selector_id")
        if not isinstance(selector_id, str) or not selector_id:
            raise CorrectionError("cohort_selector_id_invalid")
        if selector_id in members_by_id:
            raise CorrectionError(f"duplicate_cohort_selector:{selector_id}")
        members = [row for row in rows if selector_matches(row, selector)]
        item_ids = [str(row["item_id"]) for row in members]
        expected_count = selector.get("expected_count")
        if len(item_ids) != expected_count:
            raise CorrectionError(
                f"cohort_count_mismatch:{selector_id}:"
                f"expected={expected_count}:actual={len(item_ids)}"
            )
        members_by_id[selector_id] = set(item_ids)
        for row in members:
            inventory.append(
                {
                    "schema_version": "dvf-3-3-current-facts-cohort-row-v1",
                    "selector_id": selector_id,
                    "selector_kind": selector.get("kind"),
                    "item_id": row["item_id"],
                    "identity_hint": row.get("identity_hint"),
                    "primary_use": row.get("primary_use"),
                    "acquisition_hint": row.get("acquisition_hint"),
                    "fact_origin": row.get("fact_origin"),
                    "interaction_cluster": row.get("slot_meta", {}).get(
                        "interaction_cluster"
                    ),
                }
            )
    unique_members = {
        item_id for members in members_by_id.values() for item_id in members
    }
    if len(rows) != spec.get("source_row_count"):
        raise CorrectionError(
            f"source_row_count_mismatch:{len(rows)}"
        )
    if len(unique_members) != spec.get("unique_cohort_denominator"):
        raise CorrectionError(
            "unique_cohort_denominator_mismatch:"
            f"expected={spec.get('unique_cohort_denominator')}:"
            f"actual={len(unique_members)}"
        )
    return inventory, members_by_id


def build_origin_screen(
    rows: list[dict[str, Any]], spec: dict[str, Any]
) -> dict[str, Any]:
    counts = {
        "acquisition_hint_seed": sum(
            1
            for row in rows
            if "seed"
            in row.get("fact_origin", {}).get("acquisition_hint", [])
        ),
        "primary_use_cluster_summary": sum(
            1
            for row in rows
            if "cluster_summary"
            in row.get("fact_origin", {}).get("primary_use", [])
        ),
        "primary_use_identity_fallback": sum(
            1
            for row in rows
            if "identity_fallback"
            in row.get("fact_origin", {}).get("primary_use", [])
        ),
        "primary_use_role_fallback": sum(
            1
            for row in rows
            if "role_fallback"
            in row.get("fact_origin", {}).get("primary_use", [])
        ),
        "primary_use_direct_use": sum(
            1
            for row in rows
            if "direct_use"
            in row.get("fact_origin", {}).get("primary_use", [])
        ),
    }
    if counts != spec.get("origin_screen_counts"):
        raise CorrectionError(
            "origin_screen_count_mismatch:"
            f"expected={spec.get('origin_screen_counts')}:actual={counts}"
        )
    return {
        **counts,
        "origin_alone_is_not_a_narrowing_predicate": True,
        "full_universe_screened": len(rows) == spec.get("source_row_count"),
    }


def expand_patch_ledger(
    rows_by_id: dict[str, dict[str, Any]],
    members_by_id: dict[str, set[str]],
    spec: dict[str, Any],
) -> list[dict[str, Any]]:
    ledger: list[dict[str, Any]] = []
    changed_fields: set[tuple[str, str]] = set()
    for rule in spec.get("correction_rules", []):
        rule_id = rule.get("rule_id")
        selector_id = rule.get("selector_id")
        if selector_id not in members_by_id:
            raise CorrectionError(f"correction_selector_unknown:{selector_id}")
        target_ids = rule.get("target_item_ids")
        if target_ids == "ALL":
            targets = sorted(members_by_id[selector_id])
        elif isinstance(target_ids, list):
            targets = sorted(str(value) for value in target_ids)
        else:
            raise CorrectionError(f"correction_targets_invalid:{rule_id}")
        if not set(targets).issubset(members_by_id[selector_id]):
            raise CorrectionError(f"correction_target_outside_cohort:{rule_id}")
        changes = rule.get("changes")
        if not isinstance(changes, dict) or not changes:
            raise CorrectionError(f"correction_changes_invalid:{rule_id}")
        evidence_paths = rule.get("authority_evidence")
        if not isinstance(evidence_paths, list) or not evidence_paths:
            raise CorrectionError(f"correction_evidence_invalid:{rule_id}")
        for evidence_path in evidence_paths:
            if (
                not isinstance(evidence_path, str)
                or not evidence_path
                or not (REPO_ROOT / evidence_path).is_file()
            ):
                raise CorrectionError(
                    f"correction_evidence_missing:{rule_id}:{evidence_path}"
                )
        for item_id in targets:
            row = rows_by_id[item_id]
            for field, values in changes.items():
                if not isinstance(values, dict):
                    raise CorrectionError(
                        f"correction_change_invalid:{rule_id}:{field}"
                    )
                expected = values.get("expected")
                replacement = values.get("replacement")
                if row.get(field) != expected:
                    raise CorrectionError(
                        f"correction_preimage_mismatch:{rule_id}:"
                        f"{item_id}:{field}"
                    )
                key = (item_id, field)
                if key in changed_fields:
                    raise CorrectionError(
                        f"duplicate_correction_field:{item_id}:{field}"
                    )
                changed_fields.add(key)
                ledger.append(
                    {
                        "schema_version": (
                            "dvf-3-3-current-facts-correction-patch-v1"
                        ),
                        "rule_id": rule_id,
                        "selector_id": selector_id,
                        "item_id": item_id,
                        "field": field,
                        "predecessor_value": expected,
                        "successor_value": replacement,
                        "reason": rule.get("reason"),
                        "authority_evidence": rule.get("authority_evidence"),
                    }
                )
    corrected_items = {row["item_id"] for row in ledger}
    if len(corrected_items) != spec.get("corrected_item_count"):
        raise CorrectionError(
            "corrected_item_count_mismatch:"
            f"expected={spec.get('corrected_item_count')}:"
            f"actual={len(corrected_items)}"
        )
    return ledger


def build_successor_facts(
    rows: list[dict[str, Any]],
    raw_lines: list[bytes],
    ledger: list[dict[str, Any]],
) -> bytes:
    patches: dict[str, dict[str, Any]] = {}
    for patch in ledger:
        patches.setdefault(patch["item_id"], {})[patch["field"]] = patch[
            "successor_value"
        ]
    output: list[bytes] = []
    for row, raw_line in zip(rows, raw_lines, strict=True):
        changes = patches.get(str(row["item_id"]))
        if not changes:
            output.append(raw_line)
            continue
        successor = copy.deepcopy(row)
        successor.update(changes)
        output.append(
            (
                json.dumps(
                    successor,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            ).encode("utf-8")
        )
    return b"".join(output)


def build_successor_manifest(
    predecessor: dict[str, Any],
    successor_facts_sha256: str,
    spec: dict[str, Any],
    ledger: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = copy.deepcopy(predecessor)
    payload["status"] = "sealed_correction_successor"
    payload["authority_role"] = "sealed_non_current_correction_successor"
    payload["facts"] = {
        **payload["facts"],
        "path": repo_relative(SUCCESSOR_FACTS),
        "role": "sealed_non_current_correction_successor",
        "sha256": successor_facts_sha256,
    }
    food = payload["food_semantic_authority"]
    food["non_current"] = True
    food["current_adoption_allowed"] = False
    food["registry_adoption_state"] = "correction_successor_sealed"
    payload["current_facts_correction"] = {
        "schema_version": "dvf-3-3-current-facts-correction-binding-v1",
        "successor_id": spec["successor_id"],
        "predecessor_current_facts_sha256": CURRENT_FACTS_PREIMAGE_SHA256,
        "predecessor_current_manifest_sha256": CURRENT_MANIFEST_PREIMAGE_SHA256,
        "initial_g3_adoption_receipt_path": repo_relative(
            INITIAL_ADOPTION_RECEIPT
        ),
        "initial_g3_adoption_receipt_sha256": INITIAL_ADOPTION_RECEIPT_SHA256,
        "blocked_naturalization_attempt_id": "attempt-0018-g3-reseal-a",
        "blocked_attempt_reentry_allowed": False,
        "reviewer_attestation_sha256": REVIEWER_ATTESTATION_SHA256,
        "cohort_source_row_count": spec["source_row_count"],
        "unique_cohort_denominator": spec["unique_cohort_denominator"],
        "corrected_item_count": spec["corrected_item_count"],
        "correction_patch_count": len(ledger),
        "correction_spec_path": repo_relative(CORRECTION_SPEC),
        "correction_spec_sha256": sha256_file(CORRECTION_SPEC),
        "correction_spec_review_path": repo_relative(CORRECTION_SPEC_REVIEW),
        "correction_spec_review_sha256": sha256_file(
            CORRECTION_SPEC_REVIEW
        ),
        "cohort_inventory_path": repo_relative(COHORT_INVENTORY),
        "cohort_inventory_sha256": sha256_file(COHORT_INVENTORY),
        "correction_patch_ledger_path": repo_relative(PATCH_LEDGER),
        "correction_patch_ledger_sha256": sha256_file(PATCH_LEDGER),
        "append_only": True,
        "attempt_0022_mutated": False,
        "attempt_0009_receipt_mutated": False,
    }
    return payload


def command_build_successor() -> dict[str, Any]:
    require_hash(CURRENT_FACTS, CURRENT_FACTS_PREIMAGE_SHA256, "current_facts")
    require_hash(
        CURRENT_MANIFEST, CURRENT_MANIFEST_PREIMAGE_SHA256, "current_manifest"
    )
    require_hash(
        INITIAL_ADOPTION_RECEIPT,
        INITIAL_ADOPTION_RECEIPT_SHA256,
        "initial_adoption_receipt",
    )
    require_hash(BLOCKER_REQUEST, BLOCKER_REQUEST_SHA256, "blocker_request")
    require_hash(
        REVIEWER_ATTESTATION,
        REVIEWER_ATTESTATION_SHA256,
        "reviewer_attestation",
    )
    require_hash(
        G2_TERMINAL_HASH_SEAL,
        G2_TERMINAL_HASH_SEAL_SHA256,
        "g2_attempt_0022_terminal_hash_seal",
    )
    spec = read_json(CORRECTION_SPEC)
    if spec.get("successor_id") != "correction-0001":
        raise CorrectionError("successor_id_mismatch")
    spec_review = read_json(CORRECTION_SPEC_REVIEW)
    if spec_review.get("status") != "PASS":
        raise CorrectionError("correction_spec_review_not_pass")
    if spec_review.get("correction_spec_sha256") != sha256_file(
        CORRECTION_SPEC
    ):
        raise CorrectionError("correction_spec_review_binding_mismatch")
    rows, raw_lines = read_jsonl_with_bytes(CURRENT_FACTS)
    rows_by_id = {str(row["item_id"]): row for row in rows}
    if len(rows_by_id) != len(rows):
        raise CorrectionError("duplicate_current_fact_item_id")
    inventory, members_by_id = build_cohort_inventory(rows, spec)
    origin_screen = build_origin_screen(rows, spec)
    ledger = expand_patch_ledger(rows_by_id, members_by_id, spec)
    write_once_jsonl(COHORT_INVENTORY, inventory)
    write_once_jsonl(PATCH_LEDGER, ledger)
    unique_members = sorted(
        {item_id for members in members_by_id.values() for item_id in members}
    )
    summary = {
        "schema_version": "dvf-3-3-current-facts-cohort-summary-v1",
        "status": "PASS",
        "source_facts_sha256": sha256_file(CURRENT_FACTS),
        "source_row_count": len(rows),
        "origin_screen": origin_screen,
        "seed_blocker_count": len(spec["seed_blocked_item_ids"]),
        "selector_count": len(members_by_id),
        "selector_denominators": {
            selector_id: len(members)
            for selector_id, members in sorted(members_by_id.items())
        },
        "unique_cohort_denominator": len(unique_members),
        "unique_cohort_item_ids_sha256": canonical_hash(unique_members),
        "corrected_item_count": spec["corrected_item_count"],
        "unmodified_investigated_control_count": (
            len(unique_members) - spec["corrected_item_count"]
        ),
        "cohort_inventory_sha256": sha256_file(COHORT_INVENTORY),
        "correction_spec_sha256": sha256_file(CORRECTION_SPEC),
    }
    write_once_json(COHORT_SUMMARY, summary)
    successor_bytes = build_successor_facts(rows, raw_lines, ledger)
    write_once(SUCCESSOR_FACTS, successor_bytes)
    successor_sha256 = sha256_file(SUCCESSOR_FACTS)
    successor_manifest = build_successor_manifest(
        read_json(CURRENT_MANIFEST), successor_sha256, spec, ledger
    )
    write_once_json(SUCCESSOR_MANIFEST, successor_manifest)
    receipt = {
        "schema_version": "dvf-3-3-current-facts-correction-successor-receipt-v1",
        "status": "PASS",
        "successor_id": spec["successor_id"],
        "predecessor_current_facts_sha256": CURRENT_FACTS_PREIMAGE_SHA256,
        "predecessor_current_manifest_sha256": CURRENT_MANIFEST_PREIMAGE_SHA256,
        "successor_facts_path": repo_relative(SUCCESSOR_FACTS),
        "successor_facts_sha256": successor_sha256,
        "successor_manifest_path": repo_relative(SUCCESSOR_MANIFEST),
        "successor_manifest_sha256": sha256_file(SUCCESSOR_MANIFEST),
        "correction_spec_sha256": sha256_file(CORRECTION_SPEC),
        "correction_spec_review_sha256": sha256_file(
            CORRECTION_SPEC_REVIEW
        ),
        "source_row_count": len(rows),
        "successor_row_count": len(read_jsonl_with_bytes(SUCCESSOR_FACTS)[0]),
        "unique_cohort_denominator": len(unique_members),
        "corrected_item_count": spec["corrected_item_count"],
        "correction_patch_count": len(ledger),
        "unchanged_row_byte_identity_count": (
            len(rows) - spec["corrected_item_count"]
        ),
        "attempt_0022_mutation_count": 0,
        "attempt_0022_terminal_hash_seal_sha256": sha256_file(
            G2_TERMINAL_HASH_SEAL
        ),
        "attempt_0009_receipt_mutation_count": 0,
        "current_authority_mutation_count": 0,
        "registry_correction_cutover_required": True,
        "append_only": True,
    }
    write_once_json(SUCCESSOR_RECEIPT, receipt)
    return {**receipt, "successor_receipt_sha256": sha256_file(SUCCESSOR_RECEIPT)}


def command_analyze() -> dict[str, Any]:
    require_hash(CURRENT_FACTS, CURRENT_FACTS_PREIMAGE_SHA256, "current_facts")
    spec = read_json(CORRECTION_SPEC)
    rows, _ = read_jsonl_with_bytes(CURRENT_FACTS)
    rows_by_id = {str(row["item_id"]): row for row in rows}
    inventory, members_by_id = build_cohort_inventory(rows, spec)
    origin_screen = build_origin_screen(rows, spec)
    ledger = expand_patch_ledger(rows_by_id, members_by_id, spec)
    unique_members = {
        item_id for members in members_by_id.values() for item_id in members
    }
    corrected_items = {str(row["item_id"]) for row in ledger}
    return {
        "schema_version": "dvf-3-3-current-facts-correction-analysis-v1",
        "status": "PASS",
        "source_row_count": len(rows),
        "selector_count": len(members_by_id),
        "inventory_occurrence_count": len(inventory),
        "origin_screen": origin_screen,
        "unique_cohort_denominator": len(unique_members),
        "corrected_item_count": len(corrected_items),
        "correction_patch_count": len(ledger),
        "unmodified_investigated_control_count": (
            len(unique_members) - len(corrected_items)
        ),
        "current_authority_mutation_count": 0,
        "successor_artifact_created": False,
    }


def cutover_root(attempt_id: str) -> Path:
    if attempt_id != "attempt-0010":
        raise CorrectionError("correction_cutover_attempt_id_must_be_attempt-0010")
    return CUTOVER_ATTEMPTS_ROOT / attempt_id


def build_current_projection(
    successor_manifest: dict[str, Any], attempt_id: str
) -> dict[str, Any]:
    payload = copy.deepcopy(successor_manifest)
    payload["status"] = "current_authority"
    payload["authority_role"] = "successor_current_source_authority"
    payload["facts"]["path"] = CURRENT_FACTS_REL
    payload["facts"]["role"] = "current_source_authority"
    food = payload["food_semantic_authority"]
    food["non_current"] = False
    food["current_adoption_allowed"] = True
    food["registry_adoption_state"] = "current_with_correction_successor"
    correction = payload["current_facts_correction"]
    correction["registry_cutover_attempt_id"] = attempt_id
    correction["registry_adoption_state"] = "current"
    correction["source_correction_manifest_sha256"] = sha256_file(
        SUCCESSOR_MANIFEST
    )
    payload["source_promotion"]["current_facts_correction_binding"] = {
        "successor_id": correction["successor_id"],
        "predecessor_current_facts_sha256": CURRENT_FACTS_PREIMAGE_SHA256,
        "predecessor_current_manifest_sha256": CURRENT_MANIFEST_PREIMAGE_SHA256,
        "successor_facts_path": repo_relative(SUCCESSOR_FACTS),
        "successor_facts_sha256": sha256_file(SUCCESSOR_FACTS),
        "successor_manifest_path": repo_relative(SUCCESSOR_MANIFEST),
        "successor_manifest_sha256": sha256_file(SUCCESSOR_MANIFEST),
        "registry_cutover_attempt_id": attempt_id,
        "initial_g3_adoption_receipt_path": repo_relative(
            INITIAL_ADOPTION_RECEIPT
        ),
        "initial_g3_adoption_receipt_sha256": INITIAL_ADOPTION_RECEIPT_SHA256,
        "predecessor_restoration_allowed": False,
        "append_only": True,
    }
    return payload


def command_prepare(attempt_id: str) -> dict[str, Any]:
    root = cutover_root(attempt_id)
    if root.exists():
        raise CorrectionError(f"attempt_already_exists:{attempt_id}")
    require_hash(CURRENT_FACTS, CURRENT_FACTS_PREIMAGE_SHA256, "current_facts")
    require_hash(
        CURRENT_MANIFEST, CURRENT_MANIFEST_PREIMAGE_SHA256, "current_manifest"
    )
    require_hash(
        INITIAL_ADOPTION_RECEIPT,
        INITIAL_ADOPTION_RECEIPT_SHA256,
        "initial_adoption_receipt",
    )
    successor_receipt = read_json(SUCCESSOR_RECEIPT)
    if successor_receipt.get("status") != "PASS":
        raise CorrectionError("successor_receipt_not_pass")
    candidate_facts = root / "candidate" / "current_facts.jsonl"
    candidate_manifest = root / "candidate" / "current_input_manifest.json"
    write_once(candidate_facts, SUCCESSOR_FACTS.read_bytes())
    projection = build_current_projection(read_json(SUCCESSOR_MANIFEST), attempt_id)
    write_once_json(candidate_manifest, projection)
    implementation_commit = git_output("rev-parse", "HEAD")
    implementation_tree = git_output("rev-parse", "HEAD^{tree}")
    preflight = {
        "schema_version": (
            "dvf-3-3-registry-correction-cutover-preflight-v1"
        ),
        "status": "PASS",
        "attempt_id": attempt_id,
        "implementation_commit": implementation_commit,
        "implementation_tree": implementation_tree,
        "predecessor_current_facts_sha256": sha256_file(CURRENT_FACTS),
        "predecessor_current_manifest_sha256": sha256_file(CURRENT_MANIFEST),
        "successor_facts_sha256": sha256_file(SUCCESSOR_FACTS),
        "successor_manifest_sha256": sha256_file(SUCCESSOR_MANIFEST),
        "candidate_current_facts_sha256": sha256_file(candidate_facts),
        "candidate_current_manifest_sha256": sha256_file(candidate_manifest),
        "initial_adoption_receipt_sha256": sha256_file(
            INITIAL_ADOPTION_RECEIPT
        ),
        "attempt_0022_mutation_count": 0,
        "attempt_0009_receipt_mutation_count": 0,
        "live_write_count": 0,
        "manifest_last_transaction_required": True,
    }
    write_once_json(root / "preflight" / "current_preimage_report.json", preflight)
    journal = {
        "schema_version": "dvf-3-3-registry-correction-cutover-journal-v1",
        "attempt_id": attempt_id,
        "state": "prepared",
        "facts_replaced": False,
        "manifest_replaced": False,
        "verified": False,
        "committed": False,
    }
    write_once_json(root / "transaction" / "cutover_journal.json", journal)
    return preflight


def command_authorize(
    attempt_id: str, approver: str, nonce: str
) -> dict[str, Any]:
    root = cutover_root(attempt_id)
    preflight = read_json(root / "preflight" / "current_preimage_report.json")
    review_path = root / "reviews" / "independent_pre_cutover_review.json"
    review = read_json(review_path)
    if review.get("status") != "PASS":
        raise CorrectionError("independent_pre_cutover_review_not_pass")
    if len(nonce.strip()) < 16:
        raise CorrectionError("authorization_nonce_too_short")
    authorization = {
        "schema_version": (
            "dvf-3-3-registry-correction-cutover-owner-authorization-v1"
        ),
        "verdict": "PASS",
        "attempt_id": attempt_id,
        "implementation_commit": preflight["implementation_commit"],
        "implementation_tree": preflight["implementation_tree"],
        "successor_facts_sha256": preflight["successor_facts_sha256"],
        "successor_manifest_sha256": preflight["successor_manifest_sha256"],
        "candidate_current_facts_sha256": preflight[
            "candidate_current_facts_sha256"
        ],
        "candidate_current_manifest_sha256": preflight[
            "candidate_current_manifest_sha256"
        ],
        "predecessor_current_facts_sha256": CURRENT_FACTS_PREIMAGE_SHA256,
        "predecessor_current_manifest_sha256": CURRENT_MANIFEST_PREIMAGE_SHA256,
        "independent_pre_cutover_review_sha256": sha256_file(review_path),
        "allowed_target_paths": [CURRENT_FACTS_REL, CURRENT_MANIFEST_REL],
        "authorization_nonce": nonce,
        "approver_identity": approver,
        "approval_basis": "repository_owner_preapproval_in_codex_thread",
        "approval_time": utc_now(),
        "one_use": True,
    }
    write_once_json(
        root / "authorization" / "owner_correction_cutover_authorization.json",
        authorization,
    )
    return {
        "status": "PASS",
        "attempt_id": attempt_id,
        "authorization_sha256": sha256_file(
            root
            / "authorization"
            / "owner_correction_cutover_authorization.json"
        ),
    }


def atomic_replace(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.correction-cutover.tmp")
    if temporary.exists():
        temporary.unlink()
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def replace_json(path: Path, payload: dict[str, Any]) -> None:
    atomic_replace(path, canonical_bytes(payload))


def command_apply(attempt_id: str) -> dict[str, Any]:
    root = cutover_root(attempt_id)
    preflight = read_json(root / "preflight" / "current_preimage_report.json")
    auth_path = (
        root / "authorization" / "owner_correction_cutover_authorization.json"
    )
    authorization = read_json(auth_path)
    if authorization.get("verdict") != "PASS":
        raise CorrectionError("owner_authorization_not_pass")
    if authorization.get("candidate_current_facts_sha256") != preflight.get(
        "candidate_current_facts_sha256"
    ):
        raise CorrectionError("authorized_facts_candidate_mismatch")
    if authorization.get("candidate_current_manifest_sha256") != preflight.get(
        "candidate_current_manifest_sha256"
    ):
        raise CorrectionError("authorized_manifest_candidate_mismatch")
    require_hash(CURRENT_FACTS, CURRENT_FACTS_PREIMAGE_SHA256, "current_facts")
    require_hash(
        CURRENT_MANIFEST, CURRENT_MANIFEST_PREIMAGE_SHA256, "current_manifest"
    )
    nonce_path = root / "transaction" / "nonce_consumption.json"
    if nonce_path.exists():
        raise CorrectionError("authorization_nonce_already_consumed")
    lock_path = CUTOVER_ATTEMPTS_ROOT.parent / ".current-facts-correction.lock"
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise CorrectionError("registry_correction_cutover_lock_busy") from exc
    try:
        os.write(lock_fd, attempt_id.encode("utf-8"))
        os.fsync(lock_fd)
        os.close(lock_fd)
        rollback_facts = root / "transaction" / "rollback_current_facts.jsonl"
        rollback_manifest = (
            root / "transaction" / "rollback_current_input_manifest.json"
        )
        write_once(rollback_facts, CURRENT_FACTS.read_bytes())
        write_once(rollback_manifest, CURRENT_MANIFEST.read_bytes())
        rollback = {
            "schema_version": (
                "dvf-3-3-registry-correction-rollback-manifest-v1"
            ),
            "facts_sha256": sha256_file(rollback_facts),
            "manifest_sha256": sha256_file(rollback_manifest),
            "target_facts_path": CURRENT_FACTS_REL,
            "target_manifest_path": CURRENT_MANIFEST_REL,
        }
        write_once_json(
            root / "transaction" / "rollback_snapshot_manifest.json",
            rollback,
        )
        write_once_json(
            nonce_path,
            {
                "schema_version": (
                    "dvf-3-3-registry-correction-nonce-consumption-v1"
                ),
                "status": "CONSUMED",
                "attempt_id": attempt_id,
                "authorization_nonce": authorization["authorization_nonce"],
                "owner_authorization_sha256": sha256_file(auth_path),
                "consumed_at": utc_now(),
                "same_attempt_retry_allowed": False,
            },
        )
        candidate_facts = root / "candidate" / "current_facts.jsonl"
        candidate_manifest = root / "candidate" / "current_input_manifest.json"
        try:
            atomic_replace(CURRENT_FACTS, candidate_facts.read_bytes())
            journal = read_json(root / "transaction" / "cutover_journal.json")
            journal.update({"state": "facts_replaced", "facts_replaced": True})
            replace_json(root / "transaction" / "cutover_journal.json", journal)
            atomic_replace(CURRENT_MANIFEST, candidate_manifest.read_bytes())
            journal.update(
                {
                    "state": "manifest_replaced",
                    "manifest_replaced": True,
                }
            )
            replace_json(root / "transaction" / "cutover_journal.json", journal)
            require_hash(
                CURRENT_FACTS,
                preflight["candidate_current_facts_sha256"],
                "installed_current_facts",
            )
            require_hash(
                CURRENT_MANIFEST,
                preflight["candidate_current_manifest_sha256"],
                "installed_current_manifest",
            )
        except Exception:
            atomic_replace(CURRENT_FACTS, rollback_facts.read_bytes())
            atomic_replace(CURRENT_MANIFEST, rollback_manifest.read_bytes())
            raise
        journal.update(
            {
                "state": "committed",
                "verified": True,
                "committed": True,
                "committed_at": utc_now(),
            }
        )
        replace_json(root / "transaction" / "cutover_journal.json", journal)
        receipt = {
            "schema_version": (
                "dvf-3-3-registry-correction-adoption-receipt-v1"
            ),
            "status": "PASS",
            "attempt_id": attempt_id,
            "registry_correction_cutover": "current_adoption_complete",
            "predecessor_current_facts_sha256": CURRENT_FACTS_PREIMAGE_SHA256,
            "predecessor_current_manifest_sha256": (
                CURRENT_MANIFEST_PREIMAGE_SHA256
            ),
            "current_facts_sha256": sha256_file(CURRENT_FACTS),
            "current_manifest_sha256": sha256_file(CURRENT_MANIFEST),
            "correction_successor_facts_sha256": sha256_file(SUCCESSOR_FACTS),
            "correction_successor_manifest_sha256": sha256_file(
                SUCCESSOR_MANIFEST
            ),
            "initial_g3_adoption_receipt_path": repo_relative(
                INITIAL_ADOPTION_RECEIPT
            ),
            "initial_g3_adoption_receipt_sha256": sha256_file(
                INITIAL_ADOPTION_RECEIPT
            ),
            "owner_authorization_sha256": sha256_file(auth_path),
            "independent_pre_cutover_review_sha256": authorization[
                "independent_pre_cutover_review_sha256"
            ],
            "manifest_last": True,
            "process_crash_recoverable": True,
            "single_filesystem_primitive_atomicity_claimed": False,
            "partial_or_dual_current_count": 0,
            "attempt_0022_mutation_count": 0,
            "attempt_0009_receipt_mutation_count": 0,
            "rendered_lua_runtime_package_mutation_count": 0,
            "official_naturalization_attempt_allowed": True,
            "official_publish_attempt_allowed": False,
            "live_publish_gate_mutation_allowed": False,
            "git_blob_identity_status": "pending_adoption_commit",
        }
        write_once_json(
            root / "closeout" / "registry_correction_adoption_receipt.json",
            receipt,
        )
        return receipt
    finally:
        try:
            os.close(lock_fd)
        except OSError:
            pass
        if lock_path.exists():
            lock_path.unlink()


def command_verify_committed(attempt_id: str) -> dict[str, Any]:
    root = cutover_root(attempt_id)
    receipt_path = (
        root / "closeout" / "registry_correction_adoption_receipt.json"
    )
    receipt = read_json(receipt_path)
    if receipt.get("status") != "PASS":
        raise CorrectionError("correction_adoption_receipt_not_pass")
    head = git_output("rev-parse", "HEAD")
    tree = git_output("rev-parse", "HEAD^{tree}")
    facts_blob = subprocess.check_output(
        ["git", "show", f"HEAD:{CURRENT_FACTS_REL}"], cwd=REPO_ROOT
    )
    manifest_blob = subprocess.check_output(
        ["git", "show", f"HEAD:{CURRENT_MANIFEST_REL}"], cwd=REPO_ROOT
    )
    current_facts_sha256 = sha256_file(CURRENT_FACTS)
    current_manifest_sha256 = sha256_file(CURRENT_MANIFEST)
    identity = {
        "schema_version": (
            "dvf-3-3-registry-correction-current-identity-report-v1"
        ),
        "status": "PASS",
        "attempt_id": attempt_id,
        "adoption_commit": head,
        "adoption_tree": tree,
        "current_facts_working_sha256": current_facts_sha256,
        "current_facts_git_blob_sha256": sha256_bytes(facts_blob),
        "current_manifest_working_sha256": current_manifest_sha256,
        "current_manifest_git_blob_sha256": sha256_bytes(manifest_blob),
        "facts_working_blob_identity": (
            current_facts_sha256 == sha256_bytes(facts_blob)
        ),
        "manifest_working_blob_identity": (
            current_manifest_sha256 == sha256_bytes(manifest_blob)
        ),
        "partial_or_dual_current_count": 0,
        "attempt_0022_mutation_count": 0,
        "attempt_0009_receipt_mutation_count": 0,
    }
    if not (
        identity["facts_working_blob_identity"]
        and identity["manifest_working_blob_identity"]
    ):
        raise CorrectionError("committed_working_blob_identity_mismatch")
    write_once_json(
        root / "closeout" / "current_correction_identity_report.json",
        identity,
    )
    terminal = {
        "schema_version": (
            "dvf-3-3-registry-correction-terminal-hash-seal-v1"
        ),
        "status": "PASS",
        "attempt_id": attempt_id,
        "registry_correction_cutover": "current_adoption_complete",
        "adoption_commit": head,
        "adoption_tree": tree,
        "current_facts_sha256": current_facts_sha256,
        "current_manifest_sha256": current_manifest_sha256,
        "successor_receipt_sha256": sha256_file(SUCCESSOR_RECEIPT),
        "registry_correction_adoption_receipt_sha256": sha256_file(
            receipt_path
        ),
        "current_correction_identity_report_sha256": sha256_file(
            root / "closeout" / "current_correction_identity_report.json"
        ),
        "initial_g3_adoption_receipt_sha256": sha256_file(
            INITIAL_ADOPTION_RECEIPT
        ),
        "attempt_0022_mutation_count": 0,
        "attempt_0009_receipt_mutation_count": 0,
        "official_publish_attempt_created": False,
        "live_publish_gate_mutated": False,
    }
    write_once_json(
        root / "closeout" / "terminal_correction_hash_seal.json", terminal
    )
    return {
        **terminal,
        "terminal_correction_hash_seal_sha256": sha256_file(
            root / "closeout" / "terminal_correction_hash_seal.json"
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Build and atomically adopt the append-only DVF 3-3 current-facts "
            "correction successor."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("analyze")
    subparsers.add_parser("build-successor")
    prepare = subparsers.add_parser("prepare-cutover")
    prepare.add_argument("--attempt-id", required=True)
    authorize = subparsers.add_parser("authorize")
    authorize.add_argument("--attempt-id", required=True)
    authorize.add_argument("--approver", required=True)
    authorize.add_argument("--nonce", required=True)
    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--attempt-id", required=True)
    verify = subparsers.add_parser("verify-committed")
    verify.add_argument("--attempt-id", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "analyze":
            result = command_analyze()
        elif args.command == "build-successor":
            result = command_build_successor()
        elif args.command == "prepare-cutover":
            result = command_prepare(args.attempt_id)
        elif args.command == "authorize":
            result = command_authorize(
                args.attempt_id, args.approver, args.nonce
            )
        elif args.command == "apply":
            result = command_apply(args.attempt_id)
        else:
            result = command_verify_committed(args.attempt_id)
    except (
        CorrectionError,
        OSError,
        KeyError,
        ValueError,
        subprocess.CalledProcessError,
    ) as exc:
        print(
            json.dumps(
                {
                    "schema_version": (
                        "dvf-3-3-current-facts-correction-error-v1"
                    ),
                    "status": "BLOCKED",
                    "error": str(exc),
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
