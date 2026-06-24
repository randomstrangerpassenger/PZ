from __future__ import annotations

import json
import hashlib
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "docs" / "Philosophy.md").exists():
            return parent
    raise RuntimeError("Could not find repo root from script path")


ROOT = find_repo_root()
STAGING_DIR = Path(__file__).resolve().parent


def load_json(path: str) -> Any:
    return json.loads((STAGING_DIR / path).read_text(encoding="utf-8"))


def load_jsonl(path: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with (STAGING_DIR / path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            row["_line_number"] = line_number
            rows.append(row)
    return rows


def nonblank(value: Any) -> bool:
    return value is not None and value != ""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def update_fingerprints(manifest: dict[str, Any]) -> None:
    rows = ["# Artifact Fingerprint", ""]
    for item in manifest["files"]:
        path = STAGING_DIR / item["path"]
        if not path.exists():
            rows.append(f"- MISSING {item['path']}")
            continue
        if item["path"] == "artifact_fingerprint.txt":
            rows.append("- artifact_fingerprint.txt | lines=self-mutating | sha256=not-fingerprinted-self-mutating")
            continue
        line_count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        if item.get("fingerprinted", True):
            digest = sha256_bytes(path.read_bytes())
        else:
            digest = "not-fingerprinted-self-mutating"
        rows.append(f"- {item['path']} | lines={line_count} | sha256={digest}")
    (STAGING_DIR / "artifact_fingerprint.txt").write_text("\n".join(rows).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    manifest = load_json("artifact_manifest.json")
    taxonomy = load_json("taxonomy.json")
    token_manifest = load_json("search_token_manifest.json")

    expected_files = sorted(item["path"] for item in manifest["files"])
    actual_files = sorted(path.name for path in STAGING_DIR.iterdir() if path.is_file())
    if expected_files != actual_files:
        errors.append(
            "artifact manifest mismatch: "
            f"missing={sorted(set(expected_files) - set(actual_files))}, "
            f"extra={sorted(set(actual_files) - set(expected_files))}"
        )

    phase_by_path = {item["path"]: str(item["single_writer_phase"]) for item in manifest["files"]}
    if phase_by_path.get("change_required_index.md") != "8":
        errors.append("change_required_index.md must have Phase 8 as single writer")
    if phase_by_path.get("change_forbidden_index.md") != "8":
        errors.append("change_forbidden_index.md must have Phase 8 as single writer")
    if not token_manifest.get("context_bound_matcher_rule", {}).get("rule"):
        errors.append("search_token_manifest.json lacks context-bound matcher rule")
    if "24" not in token_manifest.get("distinct_measurement_family_excluded", []):
        errors.append("distinct measurement exclusion is missing expected seed 24")

    raw_rows = load_jsonl("raw_occurrences.jsonl")
    referent_rows = load_jsonl("referent_map.jsonl")
    surface_rows = load_jsonl("surface_inventory.jsonl")
    consumer_rows = load_jsonl("consumer_type_map.jsonl")
    executing_rows = load_jsonl("executing_consumers.jsonl")
    ledger_rows = load_jsonl("classified_ledger.jsonl")
    inventory_rows = load_jsonl("consumption_inventory.jsonl")

    raw_required = {
        "occurrence_id",
        "path",
        "line",
        "line_range",
        "token",
        "token_family",
        "accepted_candidate",
        "exclusion_reason",
        "context_hash",
        "surrounding_context",
    }
    ledger_required = {
        "occurrence_id",
        "path",
        "line",
        "token",
        "token_family",
        "accepted_candidate",
        "referent",
        "surface_family",
        "consumer_type",
        "disposition",
        "migration_disposition",
        "current_authority",
        "change_needed_on_rebaseline",
        "evidence_anchor",
        "context_hash",
    }

    raw_ids = [row["occurrence_id"] for row in raw_rows if "occurrence_id" in row]
    if len(raw_ids) != len(set(raw_ids)):
        dupes = [key for key, count in Counter(raw_ids).items() if count > 1]
        errors.append(f"duplicate occurrence_id values: {dupes[:10]}")

    for row in raw_rows:
        missing = raw_required - set(row)
        if missing:
            errors.append(f"raw_occurrences row {row.get('_line_number')} missing fields {sorted(missing)}")
        if row.get("token_family") not in {"core", "adjacent_seed"}:
            errors.append(f"raw_occurrences row {row.get('_line_number')} has invalid token_family")
        if not row.get("accepted_candidate") and row.get("exclusion_reason") not in {"no_dvf_context"}:
            errors.append(f"raw false-positive row {row.get('occurrence_id')} lacks explicit exclusion reason")

    accepted_raw_count = sum(1 for row in raw_rows if row.get("accepted_candidate"))
    if not (
        len(referent_rows)
        == len(surface_rows)
        == len(consumer_rows)
        == len(ledger_rows)
        == accepted_raw_count
    ):
        errors.append(
            "classification row counts must equal accepted raw candidate count: "
            f"raw={len(raw_rows)} referent={len(referent_rows)} surface={len(surface_rows)} "
            f"consumer={len(consumer_rows)} ledger={len(ledger_rows)} accepted={accepted_raw_count}"
        )
    if len(inventory_rows) != len(ledger_rows):
        errors.append("consumption_inventory.jsonl row count must equal classified_ledger.jsonl")

    valid_referents = set(taxonomy["referent"])
    valid_surfaces = set(taxonomy["surface_family"])
    valid_consumers = set(taxonomy["consumer_type"])
    valid_dispositions = set(taxonomy["disposition"])
    valid_migrations = set(taxonomy["migration_disposition"])
    raw_id_set = set(raw_ids)

    for row in ledger_rows:
        missing = ledger_required - set(row)
        if missing:
            errors.append(f"ledger row {row.get('_line_number')} missing fields {sorted(missing)}")
            continue
        if row["occurrence_id"] not in raw_id_set:
            errors.append(f"ledger row links unknown occurrence_id {row['occurrence_id']}")
        if row["referent"] not in valid_referents:
            errors.append(f"invalid referent {row['referent']} in {row['occurrence_id']}")
        if row["surface_family"] not in valid_surfaces:
            errors.append(f"invalid surface_family {row['surface_family']} in {row['occurrence_id']}")
        if row["consumer_type"] not in valid_consumers:
            errors.append(f"invalid consumer_type {row['consumer_type']} in {row['occurrence_id']}")
        if row["disposition"] not in valid_dispositions:
            errors.append(f"invalid disposition {row['disposition']} in {row['occurrence_id']}")
        if row["migration_disposition"] not in valid_migrations:
            errors.append(f"invalid migration_disposition {row['migration_disposition']} in {row['occurrence_id']}")
        for field in [
            "referent",
            "surface_family",
            "consumer_type",
            "disposition",
            "migration_disposition",
            "current_authority",
            "change_needed_on_rebaseline",
            "evidence_anchor",
        ]:
            if not nonblank(row.get(field)):
                errors.append(f"blank {field} in {row['occurrence_id']}")

    ambiguous = [row for row in ledger_rows if row.get("disposition") == "ambiguous-needs-adjudication"]
    if ambiguous:
        errors.append(f"ambiguous-needs-adjudication rows remain: {len(ambiguous)}")

    for row in executing_rows:
        if row.get("occurrence_id") not in raw_id_set:
            errors.append(f"executing consumer links unknown occurrence_id {row.get('occurrence_id')}")
        for field in ["route", "reached_file", "route_class", "evidence_anchor"]:
            if not nonblank(row.get(field)):
                errors.append(f"executing consumer {row.get('occurrence_id')} missing {field}")
        reached = ROOT / str(row.get("reached_file", ""))
        if not reached.exists():
            errors.append(f"executing consumer reached_file does not exist: {row.get('reached_file')}")

    dual_gate = load_json("dual_gate_result.json")
    if dual_gate.get("gate_a") != "PASS":
        errors.append("dual_gate_result gate_a is not PASS")
    if dual_gate.get("gate_b") != "PASS":
        errors.append("dual_gate_result gate_b is not PASS")
    if dual_gate.get("ambiguous_needs_adjudication") != 0:
        errors.append("dual_gate_result ambiguous_needs_adjudication is not 0")
    if dual_gate.get("status") != "complete":
        errors.append("dual_gate_result status is not complete")

    required_indexes = [
        "change_set.md",
        "change_required_index.md",
        "change_forbidden_index.md",
        "high_risk_consumer_review.md",
        "validator_test_tool_impact.md",
        "audit_closeout.md",
        "artifact_fingerprint.txt",
    ]
    for filename in required_indexes:
        text = (STAGING_DIR / filename).read_text(encoding="utf-8")
        if not text.strip():
            errors.append(f"{filename} is empty")

    result = "PASS" if not errors else "FAIL"
    validation_text = [
        "# Validation Result",
        "",
        f"Result: {result}",
        f"Validated UTC: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        f"- raw_occurrences: {len(raw_rows)}",
        f"- classified_ledger: {len(ledger_rows)}",
        f"- executing_consumers: {len(executing_rows)}",
        f"- ambiguous-needs-adjudication: {len(ambiguous)}",
        f"- Gate A: {dual_gate.get('gate_a')}",
        f"- Gate B: {dual_gate.get('gate_b')}",
        "",
    ]
    if warnings:
        validation_text.extend(["## Warnings", ""])
        validation_text.extend(f"- {warning}" for warning in warnings)
        validation_text.append("")
    if errors:
        validation_text.extend(["## Errors", ""])
        validation_text.extend(f"- {error}" for error in errors)
        validation_text.append("")
    else:
        validation_text.append("All required artifact, enum, blank-field, and Gate A/B checks passed.")
    (STAGING_DIR / "validation_result.md").write_text("\n".join(validation_text).rstrip() + "\n", encoding="utf-8")
    update_fingerprints(manifest)

    print(json.dumps({"result": result, "errors": len(errors), "warnings": len(warnings)}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
