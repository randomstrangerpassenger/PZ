from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path
from typing import Any


V2_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = V2_ROOT.parents[3]

DATA_DIR = V2_ROOT / "data"
OUTPUT_DIR = V2_ROOT / "output"
STAGING_DIR = V2_ROOT / "staging"
ROUND_STAGING_DIR = STAGING_DIR / "layer3_current_authority_reconstruction"
DOCS_DIR = REPO_ROOT / "docs"

CANONICAL_FACTS = DATA_DIR / "dvf_3_3_facts.jsonl"
CANONICAL_DECISIONS = DATA_DIR / "dvf_3_3_decisions.jsonl"
CANONICAL_RENDERED = OUTPUT_DIR / "dvf_3_3_rendered.json"
COMPOSE_PROFILES_V2 = DATA_DIR / "compose_profiles_v2.json"
IDENTITY_RULES = DATA_DIR / "compose_profile_identity_hint_rules.json"
PRECEDENCE_RULES = DATA_DIR / "compose_profile_conflict_precedence_rules.json"
BODY_SOURCE_OVERLAY = STAGING_DIR / "compose_contract_migration" / "layer3_body_source_overlay.jsonl"

HISTORICAL_FULL_DIR = STAGING_DIR / "interaction_cluster" / "historical_snapshot" / "full_runtime"
SOURCE_COVERAGE_DIR = STAGING_DIR / "interaction_cluster" / "source_coverage_runtime"
INTEGRATED_FACTS = SOURCE_COVERAGE_DIR / "dvf_3_3_facts.integrated.jsonl"
INTEGRATED_DECISIONS = SOURCE_COVERAGE_DIR / "dvf_3_3_decisions.integrated.jsonl"
INTEGRATED_RENDERED = SOURCE_COVERAGE_DIR / "dvf_3_3_rendered.integrated.json"
SOURCE_COVERAGE_SUMMARY = SOURCE_COVERAGE_DIR / "source_coverage_runtime_summary.json"

RUNTIME_DATA_DIR = REPO_ROOT / "Iris" / "media" / "lua" / "client" / "Iris" / "Data"
RUNTIME_CHUNK_MANIFEST = RUNTIME_DATA_DIR / "IrisLayer3DataChunks.lua"
RUNTIME_CHUNK_DIR = RUNTIME_DATA_DIR / "IrisLayer3DataChunks"
PACKAGE_RUNTIME_DATA_DIR = (
    REPO_ROOT / "Iris" / "build" / "package" / "Iris" / "media" / "lua" / "client" / "Iris" / "Data"
)
PACKAGE_CHUNK_MANIFEST = PACKAGE_RUNTIME_DATA_DIR / "IrisLayer3DataChunks.lua"
PACKAGE_CHUNK_DIR = PACKAGE_RUNTIME_DATA_DIR / "IrisLayer3DataChunks"

INVENTORY_JSON = DOCS_DIR / "layer3_current_authority_reconstruction_inventory.json"
INVENTORY_MD = DOCS_DIR / "layer3_current_authority_reconstruction_inventory.md"
PROVENANCE_JSON = DOCS_DIR / "layer3_current_authority_reconstruction_provenance.json"
PROVENANCE_MD = DOCS_DIR / "layer3_current_authority_reconstruction_provenance.md"
MANIFEST_SCHEMA_MD = DOCS_DIR / "layer3_current_authority_reconstruction_manifest_schema.md"
FACTS_DECISIONS_REPORT_MD = DOCS_DIR / "layer3_current_facts_decisions_reconstruction_report.md"
COMPOSE_ALIGNMENT_MD = DOCS_DIR / "layer3_compose_authority_alignment_report.md"
REGENERATION_REPORT_MD = DOCS_DIR / "layer3_rendered_regeneration_report.md"
PARITY_REPORT_MD = DOCS_DIR / "layer3_rendered_runtime_parity_report.md"
FIXTURE_DISCLAIMER_MD = DOCS_DIR / "layer3_fixture_authority_disclaimer.md"
SCOPE_LOCK_MD = DOCS_DIR / "layer3-current-authority-reconstruction-scope-lock.md"
CLOSEOUT_MD = DOCS_DIR / "layer3-current-authority-reconstruction-closeout.md"
DECISIONS_DRAFT_MD = DOCS_DIR / "layer3_current_authority_reconstruction_decisions_draft.md"
ROADMAP_DRAFT_MD = DOCS_DIR / "layer3_current_authority_reconstruction_roadmap_draft.md"

INPUT_MANIFEST = DATA_DIR / "dvf_3_3_input_manifest.json"
STAGED_RENDERED = ROUND_STAGING_DIR / "dvf_3_3_rendered.regenerated.json"
CANONICAL_HASH_JSON = ROUND_STAGING_DIR / "dvf_3_3_rendered.canonical_hash.json"
EQUIVALENCE_JSON = ROUND_STAGING_DIR / "rendered_runtime_equivalence.json"
MISMATCH_INVENTORY_JSON = ROUND_STAGING_DIR / "mismatch_inventory.json"
FIXTURE_GUARD_JSON = ROUND_STAGING_DIR / "fixture_contamination_guard_report.json"
CANONICAL_JSON_FORM = ROUND_STAGING_DIR / "canonical_json_form.json"
PROMOTION_ELIGIBILITY_JSON = ROUND_STAGING_DIR / "promotion_eligibility_report.json"
ADVERSARIAL_REVIEW_MD = ROUND_STAGING_DIR / "post_execution_adversarial_review.md"
EXPLICIT_AUTHOR_SEAL_JSON = ROUND_STAGING_DIR / "explicit_author_seal.json"

ROUND_ID = "layer3-current-authority-reconstruction"
AUTHORITY_DATE = "2026-06-12"
EXPECTED_RUNTIME_VOCABULARY = ["adopted", "unadopted"]
FIXTURE_THRESHOLD = 10

LUA_ENTRY_HEADER_RE = re.compile(r'^\s+\["(?P<key>(?:\\\\|\\"|[^"])*)"\]\s*=\s*\{$')
LUA_FIELD_RE = re.compile(r'^\s+\["(?P<field>[^"]+)"\]\s*=\s*"(?P<value>(?:\\\\|\\"|[^"])*)",\s*$')
MANIFEST_MODULE_RE = re.compile(r'"(?P<module>Iris/Data/IrisLayer3DataChunks/Chunk\d{3})"')
MANIFEST_TOTAL_RE = re.compile(r"-- Total runtime entries: (?P<count>\d+)")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix().replace("\\", "/")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, text: str) -> None:
    ensure_parent(path)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_hash(payload: Any) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object at {path}")
    return payload


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                row = json.loads(line)
                if isinstance(row, dict):
                    rows.append(row)
    return rows


def count_jsonl(path: Path) -> dict[str, Any]:
    rows = read_jsonl(path)
    keys = [str(row.get("item_id")) for row in rows if row.get("item_id") is not None]
    return {
        "row_count": len(rows),
        "key_count": len(keys),
        "unique_key_count": len(set(keys)),
        "duplicate_key_count": len(keys) - len(set(keys)),
        "state_counts": dict(sorted(Counter(str(row.get("state")) for row in rows if "state" in row).items())),
    }


def rendered_summary(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    entries = payload.get("entries", {})
    if not isinstance(entries, dict):
        entries = {}
    source_counts = Counter()
    publish_counts = Counter()
    missing_text = 0
    for entry in entries.values():
        if not isinstance(entry, dict):
            continue
        source_counts[str(entry.get("source"))] += 1
        if "publish_state" in entry:
            publish_counts[str(entry.get("publish_state"))] += 1
        if not entry.get("text_ko"):
            missing_text += 1
    return {
        "entry_count": len(entries),
        "unique_key_count": len(set(entries)),
        "duplicate_key_count": len(entries) - len(set(entries)),
        "source_counts": dict(sorted(source_counts.items())),
        "publish_state_counts": dict(sorted(publish_counts.items())),
        "missing_text_count": missing_text,
        "entries_sha256": payload.get("meta", {}).get("entries_sha256") if isinstance(payload.get("meta"), dict) else None,
        "meta_stats": payload.get("meta", {}).get("stats") if isinstance(payload.get("meta"), dict) else None,
    }


def path_record(path: Path, disposition: str, reason: str) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": rel(path),
        "exists": path.exists(),
        "disposition": disposition,
        "reason": reason,
        "bytes": path.stat().st_size if path.exists() and path.is_file() else None,
        "sha256": sha256_file(path),
    }
    if path.exists() and path.is_file():
        suffix = path.suffix.lower()
        try:
            if suffix == ".jsonl":
                record.update(count_jsonl(path))
            elif suffix == ".json":
                payload = read_json(path)
                if "entries" in payload:
                    record.update(rendered_summary(path))
                elif "schema_version" in payload or "meta" in payload:
                    record["json_top_level_keys"] = sorted(payload.keys())
            elif suffix == ".lua" and "IrisLayer3DataChunks" in path.as_posix():
                record.update(lua_file_summary(path))
        except Exception as exc:  # inventory must stay diagnostic and fail-loud in record form
            record["inspection_error"] = f"{type(exc).__name__}: {exc}"
    return record


def decode_lua_string(value: str) -> str:
    output = bytearray()
    index = 0
    while index < len(value):
        char = value[index]
        if char != "\\":
            output.extend(char.encode("utf-8"))
            index += 1
            continue
        next_index = index + 1
        digits = []
        while next_index < len(value) and len(digits) < 3 and value[next_index].isdigit():
            digits.append(value[next_index])
            next_index += 1
        if digits:
            output.append(int("".join(digits), 10))
            index = next_index
            continue
        if next_index >= len(value):
            output.append(ord("\\"))
            index += 1
            continue
        escaped = value[next_index]
        mapping = {"n": b"\n", "r": b"\r", "t": b"\t", "\\": b"\\", '"': b'"'}
        output.extend(mapping.get(escaped, escaped.encode("utf-8")))
        index = next_index + 1
    return output.decode("utf-8")


def parse_lua_chunk(path: Path) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    current_key: str | None = None
    current_entry: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if current_key is None:
            match = LUA_ENTRY_HEADER_RE.match(line)
            if match:
                current_key = decode_lua_string(match.group("key"))
                current_entry = {}
            continue
        if line.strip() == "},":
            entries[current_key] = current_entry
            current_key = None
            current_entry = {}
            continue
        field_match = LUA_FIELD_RE.match(line)
        if field_match:
            current_entry[field_match.group("field")] = decode_lua_string(field_match.group("value"))
    if current_key is not None:
        raise ValueError(f"unclosed Lua entry in {path}")
    return entries


def lua_file_summary(path: Path) -> dict[str, Any]:
    if path.name == "IrisLayer3DataChunks.lua":
        text = path.read_text(encoding="utf-8")
        total_match = MANIFEST_TOTAL_RE.search(text)
        modules = MANIFEST_MODULE_RE.findall(text)
        return {
            "runtime_manifest_entry_count": int(total_match.group("count")) if total_match else None,
            "runtime_manifest_chunk_count": len(modules),
            "runtime_manifest_modules": modules,
        }
    entries = parse_lua_chunk(path)
    return {
        "runtime_chunk_entry_count": len(entries),
        "source_counts": dict(sorted(Counter(entry.get("source", "__missing__") for entry in entries.values()).items())),
        "publish_state_counts": dict(
            sorted(Counter(entry.get("publish_state", "__missing__") for entry in entries.values()).items())
        ),
    }


def load_runtime_chunks(chunk_dir: Path = RUNTIME_CHUNK_DIR) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    for chunk_path in sorted(chunk_dir.glob("Chunk*.lua")):
        chunk_entries = parse_lua_chunk(chunk_path)
        overlap = set(entries).intersection(chunk_entries)
        if overlap:
            raise ValueError(f"duplicate runtime chunk keys: {sorted(overlap)[:5]}")
        entries.update(chunk_entries)
    return entries


def rendered_entries(path: Path) -> dict[str, dict[str, Any]]:
    payload = read_json(path)
    entries = payload.get("entries", {})
    if not isinstance(entries, dict):
        return {}
    return {str(key): value for key, value in entries.items() if isinstance(value, dict)}


def discover_inventory_paths() -> list[Path]:
    explicit = [
        CANONICAL_FACTS,
        CANONICAL_DECISIONS,
        CANONICAL_RENDERED,
        COMPOSE_PROFILES_V2,
        IDENTITY_RULES,
        PRECEDENCE_RULES,
        BODY_SOURCE_OVERLAY,
        HISTORICAL_FULL_DIR / "dvf_3_3_facts.full.jsonl",
        HISTORICAL_FULL_DIR / "dvf_3_3_decisions.full.jsonl",
        HISTORICAL_FULL_DIR / "dvf_3_3_rendered.full.json",
        HISTORICAL_FULL_DIR / "historical_runtime_summary.json",
        INTEGRATED_FACTS,
        INTEGRATED_DECISIONS,
        INTEGRATED_RENDERED,
        SOURCE_COVERAGE_SUMMARY,
        RUNTIME_CHUNK_MANIFEST,
        PACKAGE_CHUNK_MANIFEST,
        DOCS_DIR / "layer3-current-authority-reconstruction-plan.md",
        DOCS_DIR / "dvf_contract_current_reseal.md",
        DOCS_DIR / "dvf_current_authority_inventory.json",
    ]
    discovered: set[Path] = {path for path in explicit if path.exists()}
    roots = [V2_ROOT / "tools", V2_ROOT / "tests", DOCS_DIR]
    patterns = (
        "dvf_3_3",
        "layer3",
        "Layer3",
        "compose_profiles",
        "body_source_overlay",
        "IrisLayer3DataChunks",
        "current_authority",
    )
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and any(pattern in path.name or pattern in path.as_posix() for pattern in patterns):
                discovered.add(path)
    for chunk_dir in (RUNTIME_CHUNK_DIR, PACKAGE_CHUNK_DIR):
        if chunk_dir.exists():
            discovered.update(path for path in chunk_dir.glob("Chunk*.lua") if path.is_file())
    return sorted(discovered, key=lambda item: rel(item))


def classify_path(path: Path) -> tuple[str, str]:
    relative = rel(path)
    name = path.name
    if path in {RUNTIME_CHUNK_MANIFEST, PACKAGE_CHUNK_MANIFEST} or "IrisLayer3DataChunks/Chunk" in relative:
        return "runtime_deployable_authority", "runtime chunk manifest or chunk payload; comparison reference only"
    if path in {CANONICAL_FACTS, CANONICAL_DECISIONS, CANONICAL_RENDERED, BODY_SOURCE_OVERLAY}:
        return "fixture_non_authority", "current checkout surface has fixture cardinality and is excluded from full authority"
    if path in {INTEGRATED_FACTS, INTEGRATED_DECISIONS}:
        return "current_source_candidate", "full-scale source candidate with independent source_coverage provenance"
    if path == INTEGRATED_RENDERED:
        return "current_output_candidate", "full-scale rendered candidate for key-universe comparison; legacy text shape blocks promotion"
    if path == SOURCE_COVERAGE_SUMMARY:
        return "current_source_candidate", "provenance summary for integrated 2105 key universe"
    if HISTORICAL_FULL_DIR in path.parents:
        return "historical_predecessor", "historical 1050-row predecessor branch"
    if name.startswith("compose_profiles") or name.startswith("compose_profile_"):
        return "current_source_candidate", "compose authority input"
    if "tests" in path.parts:
        return "diagnostic_only", "test support surface"
    if "tools" in path.parts:
        return "diagnostic_only", "build or validation tool surface"
    if relative.startswith("docs/layer3_current_authority_reconstruction") or relative.endswith(
        "layer3-current-authority-reconstruction-plan.md"
    ):
        return "generated_derivative", "round plan or generated closeout support"
    if relative.startswith("docs/dvf"):
        return "historical_predecessor", "prior DVF reconciliation readpoint"
    if "staging" in path.parts:
        return "staging_non_authority", "staging artifact; not authority unless separately sealed"
    return "diagnostic_only", "classified as diagnostic support by fallback rule"


def build_inventory() -> dict[str, Any]:
    records = []
    for path in discover_inventory_paths():
        disposition, reason = classify_path(path)
        records.append(path_record(path, disposition, reason))
    disposition_counts = Counter(record["disposition"] for record in records)
    return {
        "schema_version": "layer3-current-authority-reconstruction-inventory-v0",
        "round_id": ROUND_ID,
        "generated_at": now_iso(),
        "inventory_count": len(records),
        "classified_count": len(records),
        "unclassified_count": 0,
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "records": records,
    }


def key_set_from_jsonl(path: Path) -> set[str]:
    return {str(row["item_id"]) for row in read_jsonl(path) if row.get("item_id") is not None}


def build_provenance(runtime_entries: dict[str, dict[str, str]]) -> dict[str, Any]:
    facts_keys = key_set_from_jsonl(INTEGRATED_FACTS) if INTEGRATED_FACTS.exists() else set()
    decisions_rows = read_jsonl(INTEGRATED_DECISIONS) if INTEGRATED_DECISIONS.exists() else []
    decisions_keys = {str(row["item_id"]) for row in decisions_rows if row.get("item_id") is not None}
    rendered_keys = set(rendered_entries(INTEGRATED_RENDERED)) if INTEGRATED_RENDERED.exists() else set()
    runtime_keys = set(runtime_entries)
    summary = read_json(SOURCE_COVERAGE_SUMMARY) if SOURCE_COVERAGE_SUMMARY.exists() else {}
    branch = "B4_mixed_partial"
    unavailable = [
        "full body-source overlay for body-plan v2 regeneration is unavailable in current checkout",
        "deployed runtime chunks use composed_v2_preview/publish_state shape not reproduced by integrated rendered candidate",
        "canonical data/output files contain 6-entry fixture surfaces only",
    ]
    return {
        "schema_version": "layer3-current-authority-reconstruction-provenance-v0",
        "round_id": ROUND_ID,
        "generated_at": now_iso(),
        "branch": branch,
        "closeout_state": "partial",
        "branch_reason": "full 2105 source key universe is recoverable, but current runtime text/build overlay authority is unavailable",
        "source_candidates": {
            "facts": rel(INTEGRATED_FACTS),
            "decisions": rel(INTEGRATED_DECISIONS),
            "rendered_key_universe_candidate": rel(INTEGRATED_RENDERED),
            "summary": rel(SOURCE_COVERAGE_SUMMARY),
        },
        "expected_universe_basis": {
            "basis": "source_coverage_runtime_summary plus integrated facts/decisions/rendered key sets",
            "facts_count": len(facts_keys),
            "decisions_count": len(decisions_keys),
            "rendered_count": len(rendered_keys),
            "runtime_observed_count": len(runtime_keys),
            "summary_projected_count": summary.get("merged_runtime_row_count"),
            "summary_matches_projection": summary.get("projection_comparison", {}).get("matches_projection")
            if isinstance(summary.get("projection_comparison"), dict)
            else None,
        },
        "key_set_measurement": {
            "facts_minus_decisions": sorted(facts_keys - decisions_keys)[:50],
            "decisions_minus_facts": sorted(decisions_keys - facts_keys)[:50],
            "rendered_minus_decisions": sorted(rendered_keys - decisions_keys)[:50],
            "decisions_minus_rendered": sorted(decisions_keys - rendered_keys)[:50],
            "runtime_minus_rendered": sorted(runtime_keys - rendered_keys)[:50],
            "rendered_minus_runtime": sorted(rendered_keys - runtime_keys)[:50],
        },
        "unavailable_surfaces": unavailable,
        "original_authority_vs_replacement_boundary": {
            "original_current_runtime_source": "not recovered",
            "replacement_reconstruction": "requires separately approved reconstruction scope; not authorized by this round",
        },
        "runtime_chunks_used_as": "comparison reference only; not source authority",
    }


def build_manifest(provenance: dict[str, Any]) -> dict[str, Any]:
    facts_summary = count_jsonl(INTEGRATED_FACTS)
    decisions_summary = count_jsonl(INTEGRATED_DECISIONS)
    rendered = rendered_summary(INTEGRATED_RENDERED)
    return {
        "schema_version": "dvf-3-3-input-manifest-v0",
        "round_id": ROUND_ID,
        "authority_date": AUTHORITY_DATE,
        "status": "partial",
        "provenance_branch": provenance["branch"],
        "provenance_json": rel(PROVENANCE_JSON),
        "facts": {"path": rel(INTEGRATED_FACTS), "row_count": facts_summary["row_count"], "sha256": sha256_file(INTEGRATED_FACTS)},
        "decisions": {
            "path": rel(INTEGRATED_DECISIONS),
            "row_count": decisions_summary["row_count"],
            "sha256": sha256_file(INTEGRATED_DECISIONS),
            "state_counts": decisions_summary["state_counts"],
        },
        "expected_universe": {
            "source": "provenance-derived from source_coverage_runtime integrated artifacts",
            "facts_count": facts_summary["row_count"],
            "decisions_count": decisions_summary["row_count"],
            "rendered_count": rendered["entry_count"],
            "adopted_unadopted_split": "unavailable for source validation; legacy active/silent source split is diagnostic only",
        },
        "compose_authority": {
            "profiles_path": rel(COMPOSE_PROFILES_V2),
            "profiles_sha256": sha256_file(COMPOSE_PROFILES_V2),
            "identity_rules_path": rel(IDENTITY_RULES),
            "identity_rules_sha256": sha256_file(IDENTITY_RULES),
            "precedence_rules_path": rel(PRECEDENCE_RULES),
            "precedence_rules_sha256": sha256_file(PRECEDENCE_RULES),
            "body_plan_alias": "body-plan v2 is alias only for compose_profiles_v2.json + body_plan",
        },
        "overlays": [
            {
                "path": None,
                "sha256": None,
                "row_count": None,
                "status": "full_body_plan_v2_overlay_unavailable",
                "observed_fixture_surface": rel(BODY_SOURCE_OVERLAY),
            }
        ],
        "normalizer_linter_validator_references": [
            "tools/style/normalizer.py",
            "tools/style/linter.py",
            "tools/build/validate_layer3_decisions.py",
        ],
        "expected_rendered_staging_path": rel(STAGED_RENDERED),
        "expected_runtime_vocabulary": EXPECTED_RUNTIME_VOCABULARY,
        "fixture_exclusion_rule": {
            "production_manifest_must_not_reference_fixture_paths": True,
            "fixture_threshold": FIXTURE_THRESHOLD,
            "excluded_paths": [rel(CANONICAL_FACTS), rel(CANONICAL_DECISIONS), rel(CANONICAL_RENDERED), rel(BODY_SOURCE_OVERLAY)],
        },
        "canonical_hash_fields": {
            "included_entry_fields": ["text_ko", "source", "publish_state"],
            "ordering": "sort entries by item id and fields by key",
            "hash": "sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')))",
        },
    }


def canonical_entry(entry: dict[str, Any]) -> dict[str, Any]:
    return {key: entry.get(key) for key in ("text_ko", "source", "publish_state") if key in entry}


def canonical_entries(entries: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {key: canonical_entry(entries[key]) for key in sorted(entries)}


def compare_rendered_to_runtime(rendered_path: Path, runtime_entries: dict[str, dict[str, str]]) -> tuple[dict[str, Any], dict[str, Any]]:
    rendered = rendered_entries(rendered_path)
    rendered_keys = set(rendered)
    runtime_keys = set(runtime_entries)
    missing_in_runtime = sorted(rendered_keys - runtime_keys)
    missing_in_rendered = sorted(runtime_keys - rendered_keys)

    common = sorted(rendered_keys & runtime_keys)
    l2_mismatches: list[dict[str, Any]] = []
    l3_mismatches: list[dict[str, Any]] = []
    source_mismatches = 0
    publish_mismatches = 0
    text_mismatches = 0
    for key in common:
        rendered_entry = canonical_entry(rendered[key])
        runtime_entry = canonical_entry(runtime_entries[key])
        if set(rendered_entry) != set(runtime_entry):
            l2_mismatches.append(
                {
                    "item_id": key,
                    "rendered_fields": sorted(rendered_entry),
                    "runtime_fields": sorted(runtime_entry),
                }
            )
        if rendered_entry.get("source") != runtime_entry.get("source"):
            source_mismatches += 1
        if rendered_entry.get("publish_state") != runtime_entry.get("publish_state"):
            publish_mismatches += 1
        if rendered_entry.get("text_ko") != runtime_entry.get("text_ko"):
            text_mismatches += 1
            if len(l3_mismatches) < 100:
                l3_mismatches.append(
                    {
                        "item_id": key,
                        "rendered": rendered_entry,
                        "runtime": runtime_entry,
                    }
                )

    runtime_manifest_text = RUNTIME_CHUNK_MANIFEST.read_text(encoding="utf-8") if RUNTIME_CHUNK_MANIFEST.exists() else ""
    manifest_count_match = MANIFEST_TOTAL_RE.search(runtime_manifest_text)
    manifest_modules = MANIFEST_MODULE_RE.findall(runtime_manifest_text)
    equivalence = {
        "schema_version": "layer3-rendered-runtime-equivalence-v0",
        "round_id": ROUND_ID,
        "generated_at": now_iso(),
        "rendered_path": rel(rendered_path),
        "runtime_manifest_path": rel(RUNTIME_CHUNK_MANIFEST),
        "runtime_chunk_dir": rel(RUNTIME_CHUNK_DIR),
        "rendered_count": len(rendered),
        "runtime_count": len(runtime_entries),
        "tiers": {
            "L0_entry_set_parity": {
                "status": "PASS" if not missing_in_runtime and not missing_in_rendered else "FAIL",
                "missing_in_runtime_count": len(missing_in_runtime),
                "missing_in_rendered_count": len(missing_in_rendered),
            },
            "L1_disposition_parity": {
                "status": "FAIL",
                "reason": "rendered candidate uses legacy active/silent-derived source fields; runtime uses publish_state exposed/internal_only",
                "source_mismatch_count": source_mismatches,
                "publish_state_mismatch_count": publish_mismatches,
            },
            "L2_structural_schema_parity": {
                "status": "PASS" if not l2_mismatches else "FAIL",
                "mismatch_count": len(l2_mismatches),
            },
            "L3_body_text_state_canonical_parity": {
                "status": "PASS" if source_mismatches == 0 and publish_mismatches == 0 and text_mismatches == 0 else "FAIL",
                "source_mismatch_count": source_mismatches,
                "publish_state_mismatch_count": publish_mismatches,
                "text_mismatch_count": text_mismatches,
            },
            "L4_byte_parity": {
                "status": "MEASURED_NOT_REQUIRED",
                "rendered_file_sha256": sha256_file(rendered_path),
                "runtime_manifest_sha256": sha256_file(RUNTIME_CHUNK_MANIFEST),
            },
        },
        "required_L0_L3_gate": "FAIL",
        "deployed_state_reference_measurement": {
            "manifest_entry_count": int(manifest_count_match.group("count")) if manifest_count_match else None,
            "manifest_chunk_count": len(manifest_modules),
            "actual_chunk_count": len(list(RUNTIME_CHUNK_DIR.glob("Chunk*.lua"))) if RUNTIME_CHUNK_DIR.exists() else 0,
            "manifest_references_complete": len(manifest_modules)
            == len(list(RUNTIME_CHUNK_DIR.glob("Chunk*.lua")))
            if RUNTIME_CHUNK_DIR.exists()
            else False,
            "monolith_chunk_dual_deployment": (RUNTIME_DATA_DIR / "IrisLayer3Data.lua").exists(),
        },
        "runtime_parser_compose_repair": {
            "runtime_json_parser_introduced": False,
            "runtime_compose_introduced": False,
            "runtime_repair_introduced": False,
        },
    }
    mismatch_inventory = {
        "schema_version": "layer3-rendered-runtime-mismatch-inventory-v0",
        "missing_in_runtime": missing_in_runtime,
        "missing_in_rendered": missing_in_rendered,
        "schema_mismatches_sample": l2_mismatches[:100],
        "body_text_state_mismatches_sample": l3_mismatches,
        "source_mismatch_count": source_mismatches,
        "publish_state_mismatch_count": publish_mismatches,
        "text_mismatch_count": text_mismatches,
    }
    if (
        equivalence["tiers"]["L0_entry_set_parity"]["status"] == "PASS"
        and equivalence["tiers"]["L1_disposition_parity"]["status"] == "PASS"
        and equivalence["tiers"]["L2_structural_schema_parity"]["status"] == "PASS"
        and equivalence["tiers"]["L3_body_text_state_canonical_parity"]["status"] == "PASS"
    ):
        equivalence["required_L0_L3_gate"] = "PASS"
    return equivalence, mismatch_inventory


def build_fixture_guard_report(manifest: dict[str, Any]) -> dict[str, Any]:
    canonical_records = {
        rel(CANONICAL_FACTS): count_jsonl(CANONICAL_FACTS),
        rel(CANONICAL_DECISIONS): count_jsonl(CANONICAL_DECISIONS),
        rel(CANONICAL_RENDERED): rendered_summary(CANONICAL_RENDERED),
        rel(BODY_SOURCE_OVERLAY): count_jsonl(BODY_SOURCE_OVERLAY),
    }
    production_refs = {
        manifest.get("facts", {}).get("path"),
        manifest.get("decisions", {}).get("path"),
        manifest.get("compose_authority", {}).get("profiles_path"),
        manifest.get("compose_authority", {}).get("identity_rules_path"),
        manifest.get("compose_authority", {}).get("precedence_rules_path"),
    }
    for overlay in manifest.get("overlays", []):
        if isinstance(overlay, dict):
            production_refs.add(overlay.get("path"))
    fixture_refs = [
        path
        for path in [CANONICAL_FACTS, CANONICAL_DECISIONS, CANONICAL_RENDERED, BODY_SOURCE_OVERLAY]
        if rel(path) in production_refs
    ]
    direct_read_failures = []
    for path, summary in canonical_records.items():
        count = summary.get("row_count", summary.get("entry_count"))
        if count is not None and count <= FIXTURE_THRESHOLD:
            direct_read_failures.append(
                {
                    "path": path,
                    "count": count,
                    "guard": "DIRECT_PRODUCTION_READ_REJECTED_FIXTURE_CARDINALITY",
                }
            )
    return {
        "schema_version": "layer3-fixture-contamination-guard-report-v0",
        "round_id": ROUND_ID,
        "generated_at": now_iso(),
        "status": "PASS",
        "production_manifest_fixture_reference_count": len(fixture_refs),
        "production_manifest_fixture_references": [rel(path) for path in fixture_refs],
        "direct_read_fixture_guard_count": len(direct_read_failures),
        "direct_read_fixture_failures": direct_read_failures,
        "canonical_fixture_summaries": canonical_records,
        "production_manifest_contamination_count": 0 if not fixture_refs else len(fixture_refs),
        "test_mode_fixture_opt_in_required": True,
    }


def build_promotion_report(provenance: dict[str, Any], equivalence: dict[str, Any], fixture_guard: dict[str, Any]) -> dict[str, Any]:
    gates = {
        "provenance_basis_gate": provenance["branch"] in {"B1_single_located", "B1_multiple_consistent_located", "B2_upstream_regenerable"},
        "manifest_integrity_gate": True,
        "source_cardinality_gate": provenance["expected_universe_basis"]["facts_count"]
        == provenance["expected_universe_basis"]["decisions_count"]
        == provenance["expected_universe_basis"]["rendered_count"],
        "deterministic_regeneration_gate": False,
        "fixture_contamination_gate": fixture_guard["production_manifest_contamination_count"] == 0,
        "required_equivalence_gate": equivalence["required_L0_L3_gate"] == "PASS",
        "canonical_promotion_eligibility_gate": False,
        "post_execution_adversarial_review_gate": False,
        "explicit_author_seal_gate": False,
    }
    blockers = [
        "provenance branch is B4_mixed_partial",
        "full body-plan v2 overlay/source needed for deterministic regeneration is unavailable",
        "required L0-L3 equivalence gate failed",
        "canonical promotion not authorized",
    ]
    return {
        "schema_version": "layer3-canonical-promotion-eligibility-v0",
        "round_id": ROUND_ID,
        "generated_at": now_iso(),
        "status": "INELIGIBLE",
        "closeout_state": "partial",
        "gates": gates,
        "blockers": blockers,
        "canonical_target": rel(CANONICAL_RENDERED),
        "canonical_write_completed": False,
    }


def docs_table(rows: list[tuple[str, Any]]) -> str:
    lines = ["| Field | Value |", "| --- | --- |"]
    for key, value in rows:
        if isinstance(value, (dict, list)):
            rendered = "`" + json.dumps(value, ensure_ascii=False, sort_keys=True)[:400].replace("|", "\\|") + "`"
        else:
            rendered = str(value).replace("|", "\\|")
        lines.append(f"| {key} | {rendered} |")
    return "\n".join(lines)


def write_markdown_docs(
    inventory: dict[str, Any],
    provenance: dict[str, Any],
    manifest: dict[str, Any],
    equivalence: dict[str, Any],
    mismatch_inventory: dict[str, Any],
    fixture_guard: dict[str, Any],
    promotion: dict[str, Any],
) -> None:
    write_text(
        SCOPE_LOCK_MD,
        f"""# Layer3 Current Authority Reconstruction Scope Lock

Status: closeout support / non-runtime-mutation scope lock.

This round asks whether the deployed Layer3 runtime chunk authority can be regenerated from a sealed current source/build path whose key universe is independently derived from provenance.

Runtime chunks remain runtime deployable authority only:

- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`

The 6-entry canonical data/output files are fixture/non-authority for full-scale source reconstruction until a separate promotion explicitly changes that status.

Out of scope: runtime Lua mutation, chunk payload mutation, runtime parser/compose/repair, semantic quality judgment, release readiness, Workshop readiness, and Layer4 / ACQ_DOMINANT / Acquisition Lexical reopen.
""",
    )
    write_text(
        FIXTURE_DISCLAIMER_MD,
        f"""# Layer3 Fixture Authority Disclaimer

Status: closeout support.

The following current-checkout files have fixture cardinality and are not full current authority:

- `{rel(CANONICAL_FACTS)}`
- `{rel(CANONICAL_DECISIONS)}`
- `{rel(CANONICAL_RENDERED)}`
- `{rel(BODY_SOURCE_OVERLAY)}`

Production reconstruction manifests must not reference these paths for full-scale authority. Direct production reads of these paths are guarded as fixture-cardinality failures by `{rel(FIXTURE_GUARD_JSON)}`.
""",
    )
    write_text(
        INVENTORY_MD,
        f"""# Layer3 Current Authority Reconstruction Inventory

Status: generated closeout support.

{docs_table([
    ("inventory_count", inventory["inventory_count"]),
    ("classified_count", inventory["classified_count"]),
    ("unclassified_count", inventory["unclassified_count"]),
    ("disposition_counts", inventory["disposition_counts"]),
])}

Full machine-readable inventory: `{rel(INVENTORY_JSON)}`.
""",
    )
    write_text(
        PROVENANCE_MD,
        f"""# Layer3 Current Authority Reconstruction Provenance

Status: partial terminal provenance readpoint.

{docs_table([
    ("branch", provenance["branch"]),
    ("closeout_state", provenance["closeout_state"]),
    ("branch_reason", provenance["branch_reason"]),
    ("expected_universe_basis", provenance["expected_universe_basis"]),
    ("runtime_chunks_used_as", provenance["runtime_chunks_used_as"]),
])}

Unavailable surfaces:

{chr(10).join(f"- {item}" for item in provenance["unavailable_surfaces"])}

Machine-readable provenance: `{rel(PROVENANCE_JSON)}`.
""",
    )
    write_text(
        MANIFEST_SCHEMA_MD,
        f"""# Layer3 Current Authority Reconstruction Manifest Schema

Status: schema note for `{rel(INPUT_MANIFEST)}`.

Required fields:

- `schema_version`
- `round_id`
- `authority_date`
- `status`
- `provenance_branch`
- `facts.path`, `facts.row_count`, `facts.sha256`
- `decisions.path`, `decisions.row_count`, `decisions.sha256`
- `expected_universe`
- `compose_authority`
- `overlays`
- `expected_rendered_staging_path`
- `expected_runtime_vocabulary`
- `fixture_exclusion_rule`
- `canonical_hash_fields`

Expected counts must cite provenance, not runtime chunk backfill. Runtime chunk data may only appear in equivalence measurement.
""",
    )
    write_text(
        FACTS_DECISIONS_REPORT_MD,
        f"""# Layer3 Facts / Decisions Reconstruction Report

Status: partial.

{docs_table([
    ("facts_path", manifest["facts"]["path"]),
    ("facts_row_count", manifest["facts"]["row_count"]),
    ("decisions_path", manifest["decisions"]["path"]),
    ("decisions_row_count", manifest["decisions"]["row_count"]),
    ("rendered_count", manifest["expected_universe"]["rendered_count"]),
    ("state_counts", manifest["decisions"]["state_counts"]),
])}

Facts, decisions, and integrated rendered key sets are all 2105 in the source-coverage branch. This seals a key-universe basis, but the decisions still use legacy `active / silent` vocabulary and therefore are not current writer payload authority.
""",
    )
    write_text(
        COMPOSE_ALIGNMENT_MD,
        f"""# Layer3 Compose Authority Alignment Report

Status: partial.

`compose_profiles_v2.json + body_plan` remains the compose authority label. `body-plan v2` is an alias label only.

{docs_table([
    ("profiles_path", manifest["compose_authority"]["profiles_path"]),
    ("identity_rules_path", manifest["compose_authority"]["identity_rules_path"]),
    ("precedence_rules_path", manifest["compose_authority"]["precedence_rules_path"]),
    ("body_source_overlay_path", manifest["overlays"][0]["path"]),
    ("body_source_overlay_status", manifest["overlays"][0]["status"]),
])}

The full 2105-row body-source overlay required to regenerate the deployed body-plan v2 chunk text is unavailable in the current checkout. The available overlay is a 6-row fixture surface.
""",
    )
    write_text(
        REGENERATION_REPORT_MD,
        f"""# Layer3 Rendered Regeneration Report

Status: not regenerated / partial.

No canonical output was overwritten. No runtime chunk was modified.

Staged regeneration to `{rel(STAGED_RENDERED)}` is not claimed because the full body-plan v2 overlay/source needed by the current runtime text is unavailable. The round therefore does not seal deterministic full-scale regeneration.

Canonical JSON form is recorded at `{rel(CANONICAL_JSON_FORM)}` for comparison rules only.
""",
    )
    write_text(
        PARITY_REPORT_MD,
        f"""# Layer3 Rendered Runtime Parity Report

Status: unresolved required equivalence.

Comparison reference: runtime chunk manifest and chunk files only. Rendered candidate: `{rel(INTEGRATED_RENDERED)}`.

{docs_table([
    ("rendered_count", equivalence["rendered_count"]),
    ("runtime_count", equivalence["runtime_count"]),
    ("L0", equivalence["tiers"]["L0_entry_set_parity"]),
    ("L1", equivalence["tiers"]["L1_disposition_parity"]),
    ("L2", equivalence["tiers"]["L2_structural_schema_parity"]),
    ("L3", equivalence["tiers"]["L3_body_text_state_canonical_parity"]),
    ("required_L0_L3_gate", equivalence["required_L0_L3_gate"]),
    ("mismatch_counts", {k: mismatch_inventory[k] for k in ("source_mismatch_count", "publish_state_mismatch_count", "text_mismatch_count")}),
])}

L4 byte parity is measured-only and not required by this round.
""",
    )
    write_text(
        ADVERSARIAL_REVIEW_MD,
        f"""# Post-Execution Adversarial Review

Status: NOT_PERFORMED_PROMOTION_INELIGIBLE.

Canonical promotion is ineligible because the provenance branch is `{provenance["branch"]}` and the required L0-L3 equivalence gate is `{equivalence["required_L0_L3_gate"]}`.

This file records that the human promotion review gate was not used to authorize a canonical write.
""",
    )
    write_text(
        CLOSEOUT_MD,
        f"""# Layer3 Current Authority Reconstruction Closeout

Status: `partial`.

## Result

This round sealed a partial provenance readpoint. The source-coverage integrated branch provides a 2105-key facts/decisions/rendered universe, but the current runtime chunk text cannot be regenerated from a sealed full current body-plan v2 source path in this checkout.

## Branch

- Provenance branch: `{provenance["branch"]}`
- Closeout state: `partial`
- Reason: {provenance["branch_reason"]}

## Authority Boundaries

- Runtime chunk manifest and chunk files remain deployable runtime authority only.
- Runtime chunks were used as comparison reference, not source authority.
- The 6-entry canonical data/output files are fixture/non-authority for full-scale reconstruction.
- No canonical rendered output was promoted.
- No runtime chunk payload was modified.

## Equivalence

{docs_table([
    ("L0 entry-set parity", equivalence["tiers"]["L0_entry_set_parity"]["status"]),
    ("L1 disposition parity", equivalence["tiers"]["L1_disposition_parity"]["status"]),
    ("L2 schema parity", equivalence["tiers"]["L2_structural_schema_parity"]["status"]),
    ("L3 body/state parity", equivalence["tiers"]["L3_body_text_state_canonical_parity"]["status"]),
    ("required L0-L3 gate", equivalence["required_L0_L3_gate"]),
])}

## Promotion

Canonical promotion status: `{promotion["status"]}`.

Promotion blockers:

{chr(10).join(f"- {item}" for item in promotion["blockers"])}

## Validation Artifacts

- `{rel(INVENTORY_JSON)}`
- `{rel(PROVENANCE_JSON)}`
- `{rel(INPUT_MANIFEST)}`
- `{rel(EQUIVALENCE_JSON)}`
- `{rel(MISMATCH_INVENTORY_JSON)}`
- `{rel(FIXTURE_GUARD_JSON)}`
- `{rel(PROMOTION_ELIGIBILITY_JSON)}`

## Non-Decisions

This closeout does not claim release readiness, Workshop readiness, B42 readiness, semantic quality completion, public exposure, runtime rollout, package validation, manual in-game QA, Layer4 reopen, ACQ_DOMINANT reopen, or Acquisition Lexical reopen.
""",
    )
    write_text(
        DECISIONS_DRAFT_MD,
        f"""# DECISIONS.md Draft - Layer3 Current Authority Reconstruction

Suggested compact ledger entry:

### Iris DVF 3-3 - Layer3 current authority reconstruction partial readpoint

- Status: partial terminal readpoint / closeout support
- Decision: The source-coverage integrated branch seals a 2105-key source universe, but current runtime chunk text is not regenerable from a sealed full body-plan v2 source path in the current checkout.
- Current basis: `{rel(CLOSEOUT_MD)}`, `{rel(PROVENANCE_JSON)}`, `{rel(EQUIVALENCE_JSON)}`.
- Non-decision: no runtime mutation, no canonical rendered promotion, no release readiness, no semantic quality completion.
""",
    )
    write_text(
        ROADMAP_DRAFT_MD,
        f"""# ROADMAP.md Draft - Layer3 Current Authority Reconstruction

Suggested Iris Doing/Conditional Reopen note:

- Layer3 current authority reconstruction closed as `partial`: a 2105-key source universe exists through source-coverage integrated artifacts, but full current body-plan v2 regeneration authority is unavailable. Any replacement reconstruction or canonical output promotion requires a separate approved plan.
""",
    )


def generate() -> dict[str, Any]:
    ROUND_STAGING_DIR.mkdir(parents=True, exist_ok=True)
    runtime_entries = load_runtime_chunks()
    inventory = build_inventory()
    provenance = build_provenance(runtime_entries)
    manifest = build_manifest(provenance)
    equivalence, mismatch_inventory = compare_rendered_to_runtime(INTEGRATED_RENDERED, runtime_entries)
    fixture_guard = build_fixture_guard_report(manifest)
    promotion = build_promotion_report(provenance, equivalence, fixture_guard)
    canonical_form = {
        "schema_version": "layer3-canonical-json-form-v0",
        "included_fields": ["text_ko", "source", "publish_state"],
        "excluded_fields": ["meta.generated_at", "formatting-only JSON whitespace"],
        "normalization_rules": [
            "sort item ids",
            "sort object keys",
            "preserve text_ko exactly after JSON decoding",
            "do not normalize source or publish_state values",
        ],
        "ordering_rules": "entries sorted by item id; JSON object keys sorted",
        "hash_procedure": "sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')))",
        "rendered_candidate_hash": canonical_json_hash(canonical_entries(rendered_entries(INTEGRATED_RENDERED))),
        "runtime_candidate_hash": canonical_json_hash(canonical_entries(runtime_entries)),
    }
    canonical_hash = {
        "schema_version": "layer3-rendered-canonical-hash-v0",
        "rendered_path": rel(INTEGRATED_RENDERED),
        "canonical_json_form_path": rel(CANONICAL_JSON_FORM),
        "canonical_hash": canonical_form["rendered_candidate_hash"],
        "repeated_regeneration_hash_identical": False,
        "reason": "deterministic full-scale regeneration not executed because full body-plan v2 overlay/source is unavailable",
    }
    explicit_author_seal = {
        "schema_version": "layer3-explicit-author-seal-v0",
        "round_id": ROUND_ID,
        "status": "NOT_RECORDED_PROMOTION_INELIGIBLE",
        "single_write_authority": None,
        "target_path": rel(CANONICAL_RENDERED),
        "promoted_artifact_hash": None,
        "closeout": rel(CLOSEOUT_MD),
    }

    write_json(INVENTORY_JSON, inventory)
    write_json(PROVENANCE_JSON, provenance)
    write_json(INPUT_MANIFEST, manifest)
    write_json(EQUIVALENCE_JSON, equivalence)
    write_json(MISMATCH_INVENTORY_JSON, mismatch_inventory)
    write_json(FIXTURE_GUARD_JSON, fixture_guard)
    write_json(CANONICAL_JSON_FORM, canonical_form)
    write_json(CANONICAL_HASH_JSON, canonical_hash)
    write_json(PROMOTION_ELIGIBILITY_JSON, promotion)
    write_json(EXPLICIT_AUTHOR_SEAL_JSON, explicit_author_seal)
    write_markdown_docs(inventory, provenance, manifest, equivalence, mismatch_inventory, fixture_guard, promotion)
    return {
        "status": "partial",
        "branch": provenance["branch"],
        "inventory_count": inventory["inventory_count"],
        "runtime_count": equivalence["runtime_count"],
        "rendered_count": equivalence["rendered_count"],
        "required_L0_L3_gate": equivalence["required_L0_L3_gate"],
        "closeout": rel(CLOSEOUT_MD),
    }


def validate_generated() -> dict[str, Any]:
    required_paths = [
        INVENTORY_JSON,
        INVENTORY_MD,
        PROVENANCE_JSON,
        PROVENANCE_MD,
        INPUT_MANIFEST,
        EQUIVALENCE_JSON,
        MISMATCH_INVENTORY_JSON,
        FIXTURE_GUARD_JSON,
        CANONICAL_JSON_FORM,
        CANONICAL_HASH_JSON,
        PROMOTION_ELIGIBILITY_JSON,
        ADVERSARIAL_REVIEW_MD,
        EXPLICIT_AUTHOR_SEAL_JSON,
        CLOSEOUT_MD,
    ]
    missing = [rel(path) for path in required_paths if not path.exists()]
    inventory = read_json(INVENTORY_JSON) if INVENTORY_JSON.exists() else {}
    provenance = read_json(PROVENANCE_JSON) if PROVENANCE_JSON.exists() else {}
    manifest = read_json(INPUT_MANIFEST) if INPUT_MANIFEST.exists() else {}
    equivalence = read_json(EQUIVALENCE_JSON) if EQUIVALENCE_JSON.exists() else {}
    fixture_guard = read_json(FIXTURE_GUARD_JSON) if FIXTURE_GUARD_JSON.exists() else {}
    promotion = read_json(PROMOTION_ELIGIBILITY_JSON) if PROMOTION_ELIGIBILITY_JSON.exists() else {}
    errors = []
    if missing:
        errors.append({"code": "missing_generated_artifacts", "paths": missing})
    if inventory.get("unclassified_count") != 0:
        errors.append({"code": "inventory_unclassified_nonzero"})
    if provenance.get("branch") != "B4_mixed_partial":
        errors.append({"code": "unexpected_provenance_branch", "branch": provenance.get("branch")})
    if manifest.get("status") != "partial":
        errors.append({"code": "unexpected_manifest_status", "status": manifest.get("status")})
    if equivalence.get("required_L0_L3_gate") != "FAIL":
        errors.append({"code": "unexpected_equivalence_gate", "gate": equivalence.get("required_L0_L3_gate")})
    if fixture_guard.get("production_manifest_contamination_count") != 0:
        errors.append({"code": "fixture_manifest_contamination"})
    if promotion.get("status") != "INELIGIBLE":
        errors.append({"code": "unexpected_promotion_status", "status": promotion.get("status")})
    return {
        "schema_version": "layer3-current-authority-reconstruction-validation-v0",
        "status": "pass" if not errors else "fail",
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Layer3 current authority reconstruction artifacts.")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args(argv)
    if not args.validate_only:
        result = generate()
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    validation = validate_generated()
    print(json.dumps(validation, ensure_ascii=False, sort_keys=True))
    return 0 if validation["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
