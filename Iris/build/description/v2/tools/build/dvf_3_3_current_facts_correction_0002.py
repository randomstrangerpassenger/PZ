from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Iterable


TOOLS_DIR = Path(__file__).resolve().parent
V2_ROOT = TOOLS_DIR.parents[1]
REPO_ROOT = V2_ROOT.parents[3]

CURRENT_FACTS = V2_ROOT / "data" / "dvf_3_3_facts.jsonl"
CURRENT_MANIFEST = V2_ROOT / "data" / "dvf_3_3_input_manifest.json"
SPEC = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "authority"
    / "current_facts_correction"
    / "correction-0002.json"
)
REVIEWER_ATTESTATION = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "round3"
    / "dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure"
    / "codex_reviewer_phase7_blocked_attestation.json"
)
PREVIOUS_RECEIPT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_registry_operational_cutover"
    / "attempts"
    / "attempt-0010"
    / "closeout"
    / "registry_correction_adoption_receipt.json"
)
PREVIOUS_SUCCESSOR_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_current_facts_correction_successor"
    / "successors"
    / "correction-0001"
)
PREVIOUS_SUCCESSOR_FACTS = PREVIOUS_SUCCESSOR_ROOT / "successor_facts.jsonl"
PREVIOUS_PATCH_LEDGER = (
    PREVIOUS_SUCCESSOR_ROOT / "correction_patch_ledger.jsonl"
)
G2_SUCCESSOR_FACTS = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_food_semantic_facts_authority"
    / "attempts"
    / "attempt-0022"
    / "authority_execution"
    / "successor_facts.jsonl"
)
ITEMSCRIPT = REPO_ROOT / "Iris" / "input" / "items_itemscript.json"
RECIPES = REPO_ROOT / "Iris" / "input" / "recipes_index_full.json"
KO_ITEM_NAMES = (
    REPO_ROOT / "lua" / "shared" / "Translate" / "KO" / "ItemName_KO.txt"
)

SUCCESSOR_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_current_facts_correction_successor"
    / "successors"
    / "correction-0002"
)
INPUT_IDENTITY = SUCCESSOR_ROOT / "predecessor_input_identity.json"
ATTESTATION_BINDING = SUCCESSOR_ROOT / "reviewer_attestation_binding.json"
FULL_CENSUS = SUCCESSOR_ROOT / "full_cohort_census.jsonl"
COHORT_SUMMARY = SUCCESSOR_ROOT / "cohort_summary.json"
ROW_LINEAGE = SUCCESSOR_ROOT / "row_source_lineage.jsonl"
PATCH_LEDGER = SUCCESSOR_ROOT / "correction_patch_ledger.jsonl"
UNRESOLVED_ROWS = SUCCESSOR_ROOT / "unresolved_rows.jsonl"
SEED_NON_REGRESSION = SUCCESSOR_ROOT / "seed_preexisting_defect_report.json"
NON_TARGET_IDENTITY = SUCCESSOR_ROOT / "non_target_byte_identity_report.json"
PREVIOUS_REGRESSION = SUCCESSOR_ROOT / "correction_0001_regression_report.json"
SUCCESSOR_FACTS = SUCCESSOR_ROOT / "successor_facts.jsonl"
SUCCESSOR_MANIFEST = SUCCESSOR_ROOT / "successor_input_manifest.json"
SUCCESSOR_RECEIPT = SUCCESSOR_ROOT / "successor_receipt.json"


class CorrectionError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    if not path.is_file():
        raise CorrectionError(f"required_file_missing:{repo_relative(path)}")
    return sha256_bytes(path.read_bytes())


def canonical_lf_sha256_file(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return sha256_bytes(data)


def canonical_bytes(payload: Any) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
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
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise CorrectionError(f"json_object_required:{repo_relative(path)}")
    return payload


def read_jsonl_bytes(
    path: Path,
) -> tuple[list[dict[str, Any]], list[bytes]]:
    raw_lines = path.read_bytes().splitlines(keepends=True)
    rows: list[dict[str, Any]] = []
    for number, raw in enumerate(raw_lines, start=1):
        if not raw.strip():
            raise CorrectionError(
                f"blank_jsonl_line:{repo_relative(path)}:{number}"
            )
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise CorrectionError(
                f"jsonl_object_required:{repo_relative(path)}:{number}"
            )
        rows.append(payload)
    return rows, raw_lines


def write_generated(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_json(path: Path, payload: Any) -> None:
    write_generated(path, canonical_bytes(payload))


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
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
    write_generated(path, data)


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


def rows_by_id(
    rows: list[dict[str, Any]], raw_lines: list[bytes]
) -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    structured: dict[str, dict[str, Any]] = {}
    raw: dict[str, bytes] = {}
    for row, raw_line in zip(rows, raw_lines, strict=True):
        item_id = str(row.get("item_id"))
        if item_id in structured:
            raise CorrectionError(f"duplicate_item_id:{item_id}")
        structured[item_id] = row
        raw[item_id] = raw_line
    return structured, raw


def generation_rule_id(row: dict[str, Any]) -> str:
    origins = row.get("fact_origin", {}).get("primary_use", [])
    cluster = row.get("slot_meta", {}).get("interaction_cluster", {})
    if "cluster_summary" in origins:
        return (
            "primary_use.cluster_summary:"
            f"{cluster.get('selected_cluster')}:"
            f"{cluster.get('cluster_skeleton')}"
        )
    if len(origins) == 1:
        return f"primary_use.{origins[0]}"
    return "primary_use." + "+".join(str(value) for value in origins)


def build_cohorts(
    rows: list[dict[str, Any]], spec: dict[str, Any]
) -> tuple[dict[str, list[str]], dict[str, str]]:
    members: dict[str, list[str]] = {}
    cohort_for_item: dict[str, str] = {}
    for selector in spec["cohort_selectors"]:
        cohort_id = selector["cohort_id"]
        selected: list[str] = []
        for row in rows:
            cluster = row.get("slot_meta", {}).get(
                "interaction_cluster", {}
            )
            if (
                cluster.get("selected_cluster") == selector["cluster"]
                and cluster.get("cluster_skeleton")
                == selector["expected_skeleton"]
                and row.get("primary_use")
                == selector["expected_primary_use"]
                and "cluster_summary"
                in row.get("fact_origin", {}).get("primary_use", [])
            ):
                selected.append(str(row["item_id"]))
        if len(selected) != selector["expected_count"]:
            raise CorrectionError(
                f"cohort_count_mismatch:{cohort_id}:"
                f"expected={selector['expected_count']}:actual={len(selected)}"
            )
        members[cohort_id] = selected
        for item_id in selected:
            if item_id in cohort_for_item:
                raise CorrectionError(f"overlapping_cohorts:{item_id}")
            cohort_for_item[item_id] = cohort_id
    if len(members) != spec["expected_investigated_cohort_count"]:
        raise CorrectionError("investigated_cohort_count_mismatch")
    if len(cohort_for_item) != spec["expected_unique_investigated_row_count"]:
        raise CorrectionError("investigated_row_count_mismatch")
    return members, cohort_for_item


def expand_ledger(
    structured: dict[str, dict[str, Any]],
    cohort_members: dict[str, list[str]],
    spec: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    ledger: list[dict[str, Any]] = []
    rule_for_item: dict[str, dict[str, Any]] = {}
    changed_fields: set[tuple[str, str]] = set()
    profiles = spec["evidence_profiles"]
    for rule in spec["correction_rules"]:
        cohort_id = rule["cohort_id"]
        if cohort_id not in cohort_members:
            raise CorrectionError(f"unknown_rule_cohort:{cohort_id}")
        profile_id = rule["evidence_profile"]
        if profile_id not in profiles:
            raise CorrectionError(f"unknown_evidence_profile:{profile_id}")
        for source_path in profiles[profile_id]["paths"]:
            if not (REPO_ROOT / source_path).is_file():
                raise CorrectionError(
                    f"missing_evidence_source:{rule['rule_id']}:{source_path}"
                )
        for item_id in rule["target_item_ids"]:
            if item_id not in cohort_members[cohort_id]:
                raise CorrectionError(
                    f"target_outside_cohort:{rule['rule_id']}:{item_id}"
                )
            if item_id in rule_for_item:
                raise CorrectionError(f"multiple_rules_for_item:{item_id}")
            rule_for_item[item_id] = rule
            row = structured[item_id]
            for field, change in rule["changes"].items():
                expected = change["expected"]
                replacement = change["replacement"]
                if row.get(field) != expected:
                    raise CorrectionError(
                        f"preimage_mismatch:{item_id}:{field}"
                    )
                if (item_id, field) in changed_fields:
                    raise CorrectionError(
                        f"duplicate_field_change:{item_id}:{field}"
                    )
                changed_fields.add((item_id, field))
                ledger.append(
                    {
                        "schema_version": (
                            "dvf-3-3-current-facts-correction-patch-v2"
                        ),
                        "successor_id": spec["successor_id"],
                        "item_id": item_id,
                        "field": field,
                        "generation_rule_id": generation_rule_id(row),
                        "predecessor_fact_origin": row.get("fact_origin"),
                        "cluster": row.get("slot_meta", {}).get(
                            "interaction_cluster"
                        ),
                        "cohort_id": cohort_id,
                        "correction_rule_id": rule["rule_id"],
                        "predecessor_value": expected,
                        "successor_value": replacement,
                        "reason": rule["reason"],
                        "evidence_profile": profile_id,
                        "approved_source_paths": profiles[profile_id]["paths"],
                        "allowed_operations": profiles[profile_id][
                            "allowed_operations"
                        ],
                        "layer4_evidence_consumed": False,
                    }
                )
    if len(rule_for_item) != spec["expected_corrected_row_count"]:
        raise CorrectionError(
            "corrected_row_count_mismatch:"
            f"expected={spec['expected_corrected_row_count']}:"
            f"actual={len(rule_for_item)}"
        )
    return ledger, rule_for_item


def load_korean_names() -> tuple[dict[str, str], dict[str, int]]:
    names: dict[str, str] = {}
    line_numbers: dict[str, int] = {}
    pattern = re.compile(
        r'^\s*ItemName_([A-Za-z0-9_.-]+)\s*=\s*"([^"]*)",?\s*$'
    )
    raw = KO_ITEM_NAMES.read_bytes()
    encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    for number, line in enumerate(
        raw.decode(encoding).splitlines(), start=1
    ):
        match = pattern.match(line)
        if match:
            names[match.group(1)] = match.group(2)
            line_numbers[match.group(1)] = number
    return names, line_numbers


def source_artifact_binding(paths: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "path": path,
            "sha256": sha256_file(REPO_ROOT / path),
        }
        for path in paths
    ]


def build_lineage(
    structured: dict[str, dict[str, Any]],
    cohort_for_item: dict[str, str],
    rule_for_item: dict[str, dict[str, Any]],
    spec: dict[str, Any],
) -> list[dict[str, Any]]:
    itemscript = read_json(ITEMSCRIPT)
    recipes = read_json(RECIPES).get("items", {})
    if not isinstance(recipes, dict):
        raise CorrectionError("recipes_items_object_required")
    korean_names, korean_name_lines = load_korean_names()
    rows: list[dict[str, Any]] = []
    for item_id in sorted(cohort_for_item):
        source_item = itemscript.get(item_id)
        if not isinstance(source_item, dict):
            raise CorrectionError(f"itemscript_row_missing:{item_id}")
        rule = rule_for_item.get(item_id)
        if rule is not None:
            profile_id = rule["evidence_profile"]
            correction_rule_id = rule["rule_id"]
            disposition = "corrected"
        elif item_id == "Base.BlowTorch":
            profile_id = "itemscript_and_static_recipe"
            correction_rule_id = None
            disposition = "unchanged_control"
            if source_item.get("DisplayCategory") != "Tool":
                raise CorrectionError("blowtorch_control_source_mismatch")
        else:
            profile_id = "item_identity_and_itemscript"
            correction_rule_id = None
            disposition = "unchanged_control"
            if (
                source_item.get("Type") != "WeaponPart"
                and source_item.get("DisplayCategory") != "WeaponPart"
            ):
                raise CorrectionError(
                    f"unreviewed_control_without_weapon_part_source:{item_id}"
                )
        profile = spec["evidence_profiles"][profile_id]
        current = structured[item_id]
        rows.append(
            {
                "schema_version": (
                    "dvf-3-3-current-facts-correction-row-lineage-v2"
                ),
                "successor_id": spec["successor_id"],
                "item_id": item_id,
                "disposition": disposition,
                "cohort_id": cohort_for_item[item_id],
                "generation_rule_id": generation_rule_id(current),
                "generation_rule_value": current.get("primary_use"),
                "predecessor_fact_origin": current.get("fact_origin"),
                "predecessor_cluster": current.get("slot_meta", {}).get(
                    "interaction_cluster"
                ),
                "correction_rule_id": correction_rule_id,
                "evidence_profile": profile_id,
                "authority_class": profile["authority_class"],
                "allowed_operations": profile["allowed_operations"],
                "approved_source_artifacts": source_artifact_binding(
                    profile["paths"]
                ),
                "source_values": {
                    "itemscript_json_pointer": f"/{item_id}",
                    "itemscript": source_item,
                    "korean_item_name": korean_names.get(item_id),
                    "korean_item_name_line": korean_name_lines.get(item_id),
                    "static_recipe_relations": recipes.get(item_id, []),
                },
                "layer4_evidence_consumed": False,
                "unsupported_inference_count": 0,
            }
        )
    return rows


def build_full_census(
    rows: list[dict[str, Any]],
    cohort_for_item: dict[str, str],
    rule_for_item: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    census: list[dict[str, Any]] = []
    for row_number, row in enumerate(rows, start=1):
        item_id = str(row["item_id"])
        cluster = row.get("slot_meta", {}).get("interaction_cluster", {})
        if item_id in rule_for_item:
            disposition = "corrected"
        elif item_id in cohort_for_item:
            disposition = "unchanged_control"
        else:
            disposition = "outside_seed_sibling_cohorts"
        census.append(
            {
                "schema_version": (
                    "dvf-3-3-current-facts-full-cohort-census-row-v2"
                ),
                "row_number": row_number,
                "item_id": item_id,
                "generation_rule_id": generation_rule_id(row),
                "fact_origin": row.get("fact_origin"),
                "selected_cluster": cluster.get("selected_cluster"),
                "selected_role": cluster.get("selected_role"),
                "cluster_skeleton": cluster.get("cluster_skeleton"),
                "investigated_cohort_id": cohort_for_item.get(item_id),
                "correction_rule_id": (
                    rule_for_item.get(item_id, {}).get("rule_id")
                ),
                "disposition": disposition,
            }
        )
    return census


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
        item_id = str(row["item_id"])
        changes = patches.get(item_id)
        if not changes:
            output.append(raw_line)
            continue
        successor = copy.deepcopy(row)
        successor.update(changes)
        newline = b"\r\n" if raw_line.endswith(b"\r\n") else b"\n"
        encoded = json.dumps(
            successor,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        output.append(encoded + newline)
    return b"".join(output)


def origin_screen(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "primary_use_cluster_summary": sum(
            "cluster_summary"
            in row.get("fact_origin", {}).get("primary_use", [])
            for row in rows
        ),
        "primary_use_identity_fallback": sum(
            "identity_fallback"
            in row.get("fact_origin", {}).get("primary_use", [])
            for row in rows
        ),
        "primary_use_role_fallback": sum(
            "role_fallback"
            in row.get("fact_origin", {}).get("primary_use", [])
            for row in rows
        ),
        "primary_use_direct_use": sum(
            "direct_use"
            in row.get("fact_origin", {}).get("primary_use", [])
            for row in rows
        ),
    }


def build_manifest(
    predecessor: dict[str, Any],
    spec: dict[str, Any],
    successor_facts_sha256: str,
    corrected_count: int,
    patch_count: int,
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
    food["registry_adoption_state"] = "correction_successor_0002_sealed"
    binding = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-successor-binding-v2"
        ),
        "successor_id": spec["successor_id"],
        "predecessor_current_facts_sha256": (
            spec["predecessor_current_facts_sha256"]
        ),
        "predecessor_current_manifest_sha256": (
            spec["predecessor_current_manifest_sha256"]
        ),
        "previous_correction_receipt_path": repo_relative(PREVIOUS_RECEIPT),
        "previous_correction_receipt_sha256": (
            spec["previous_correction_receipt_sha256"]
        ),
        "reviewer_attestation_path": repo_relative(REVIEWER_ATTESTATION),
        "reviewer_attestation_sha256": (
            spec["reviewer_attestation_sha256"]
        ),
        "correction_spec_path": repo_relative(SPEC),
        "correction_spec_sha256": sha256_file(SPEC),
        "full_cohort_census_path": repo_relative(FULL_CENSUS),
        "full_cohort_census_sha256": sha256_file(FULL_CENSUS),
        "row_source_lineage_path": repo_relative(ROW_LINEAGE),
        "row_source_lineage_sha256": sha256_file(ROW_LINEAGE),
        "correction_patch_ledger_path": repo_relative(PATCH_LEDGER),
        "correction_patch_ledger_sha256": sha256_file(PATCH_LEDGER),
        "investigated_cohort_count": (
            spec["expected_investigated_cohort_count"]
        ),
        "investigated_row_count": (
            spec["expected_unique_investigated_row_count"]
        ),
        "corrected_row_count": corrected_count,
        "correction_patch_count": patch_count,
        "unchanged_control_count": (
            spec["expected_unchanged_control_count"]
        ),
        "unresolved_row_count": spec["expected_unresolved_row_count"],
        "layer4_evidence_consumed_count": 0,
        "registry_cutover_performed": False,
        "current_authority_mutated": False,
        "append_only": True,
    }
    payload["current_facts_correction_successor"] = binding
    payload["source_promotion"][
        "current_facts_correction_successor_0002_binding"
    ] = {
        **binding,
        "successor_facts_path": repo_relative(SUCCESSOR_FACTS),
        "successor_facts_sha256": successor_facts_sha256,
    }
    return payload


def main() -> None:
    spec = read_json(SPEC)
    if spec.get("successor_id") != "correction-0002":
        raise CorrectionError("successor_id_mismatch")
    if git_output("rev-parse", "HEAD") != spec["input_commit"]:
        raise CorrectionError("input_commit_mismatch")
    if git_output("rev-parse", "HEAD^{tree}") != spec["input_tree"]:
        raise CorrectionError("input_tree_mismatch")
    require_hash(
        CURRENT_FACTS,
        spec["predecessor_current_facts_sha256"],
        "predecessor_current_facts",
    )
    require_hash(
        CURRENT_MANIFEST,
        spec["predecessor_current_manifest_sha256"],
        "predecessor_current_manifest",
    )
    require_hash(
        PREVIOUS_RECEIPT,
        spec["previous_correction_receipt_sha256"],
        "previous_correction_receipt",
    )
    require_hash(
        REVIEWER_ATTESTATION,
        spec["reviewer_attestation_sha256"],
        "reviewer_attestation",
    )
    rows, raw_lines = read_jsonl_bytes(CURRENT_FACTS)
    if len(rows) != spec["source_row_count"]:
        raise CorrectionError("source_row_count_mismatch")
    structured, predecessor_raw = rows_by_id(rows, raw_lines)
    cohorts, cohort_for_item = build_cohorts(rows, spec)
    ledger, rule_for_item = expand_ledger(
        structured, cohorts, spec
    )
    controls = set(cohort_for_item) - set(rule_for_item)
    if len(controls) != spec["expected_unchanged_control_count"]:
        raise CorrectionError("unchanged_control_count_mismatch")
    expected_controls = {"Base.BlowTorch"} | {
        item_id
        for item_id in cohorts["cluster_gun_modding"]
        if item_id
        not in {"Base.Saw", "Base.Shotgun", "Base.DoubleBarrelShotgun"}
    }
    if controls != expected_controls:
        raise CorrectionError("unchanged_control_set_mismatch")
    actual_origins = origin_screen(rows)
    if actual_origins != spec["origin_screen_counts"]:
        raise CorrectionError(
            f"origin_screen_mismatch:{actual_origins}"
        )

    attestation = read_json(REVIEWER_ATTESTATION)
    attested_source_blockers = {
        blocker["item_id"]
        for blocker in attestation.get("blockers", [])
        if blocker.get("ownership") == "current_facts_source"
    }
    if attested_source_blockers != set(spec["seed_blocked_item_ids"]):
        raise CorrectionError("reviewer_seed_binding_mismatch")

    input_identity = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-input-identity-v2"
        ),
        "status": "PASS",
        "input_commit": spec["input_commit"],
        "input_tree": spec["input_tree"],
        "predecessor_current_facts": {
            "path": repo_relative(CURRENT_FACTS),
            "sha256": sha256_file(CURRENT_FACTS),
            "row_count": len(rows),
        },
        "predecessor_current_manifest": {
            "path": repo_relative(CURRENT_MANIFEST),
            "sha256": sha256_file(CURRENT_MANIFEST),
        },
        "previous_correction_receipt": {
            "path": repo_relative(PREVIOUS_RECEIPT),
            "sha256": sha256_file(PREVIOUS_RECEIPT),
        },
        "food_changes_0_to_13_mutation_count": 0,
        "attempt_0022_mutation_count": 0,
        "current_authority_mutation_count": 0,
        "registry_cutover_count": 0,
        "foundation_mutation_count": 0,
        "naturalization_attempt_mutation_count": 0,
    }
    write_json(INPUT_IDENTITY, input_identity)
    attestation_binding = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-reviewer-binding-v2"
        ),
        "status": "PASS",
        "reviewer_attestation_path": repo_relative(REVIEWER_ATTESTATION),
        "reviewer_attestation_sha256": sha256_file(REVIEWER_ATTESTATION),
        "reviewer_identity": attestation.get("reviewer", {}).get("identity"),
        "attestation_status": attestation.get("status"),
        "current_facts_source_blocker_count": len(
            attested_source_blockers
        ),
        "current_facts_source_blocker_item_ids": sorted(
            attested_source_blockers
        ),
        "seed_set_exact_match": True,
        "compiler_blockers_out_of_scope": True,
    }
    write_json(ATTESTATION_BINDING, attestation_binding)

    full_census = build_full_census(rows, cohort_for_item, rule_for_item)
    write_jsonl(FULL_CENSUS, full_census)
    write_jsonl(PATCH_LEDGER, ledger)
    lineage = build_lineage(
        structured, cohort_for_item, rule_for_item, spec
    )
    write_jsonl(ROW_LINEAGE, lineage)
    write_jsonl(UNRESOLVED_ROWS, [])

    cohort_summary = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-cohort-summary-v2"
        ),
        "status": "PASS",
        "source_row_count": len(rows),
        "full_census_row_count": len(full_census),
        "origin_screen": actual_origins,
        "seed_blocker_count": len(spec["seed_blocked_item_ids"]),
        "investigated_semantic_cohort_count": len(cohorts),
        "exact_generation_rule_cohort_count": len(cohorts),
        "cohort_denominators": {
            cohort_id: len(item_ids)
            for cohort_id, item_ids in sorted(cohorts.items())
        },
        "unique_investigated_row_count": len(cohort_for_item),
        "corrected_row_count": len(rule_for_item),
        "unchanged_control_count": len(controls),
        "unresolved_row_count": 0,
        "correction_patch_count": len(ledger),
        "corrected_item_ids_sha256": canonical_hash(
            sorted(rule_for_item)
        ),
        "unchanged_control_item_ids": sorted(controls),
        "unchanged_control_item_ids_sha256": canonical_hash(
            sorted(controls)
        ),
        "outside_cohort_row_count": len(rows) - len(cohort_for_item),
        "layer4_evidence_consumed_count": 0,
        "unsupported_inference_count": 0,
        "full_cohort_census_sha256": sha256_file(FULL_CENSUS),
        "row_source_lineage_sha256": sha256_file(ROW_LINEAGE),
        "correction_patch_ledger_sha256": sha256_file(PATCH_LEDGER),
    }
    write_json(COHORT_SUMMARY, cohort_summary)

    g2_rows, g2_raw_lines = read_jsonl_bytes(G2_SUCCESSOR_FACTS)
    _, g2_raw = rows_by_id(g2_rows, g2_raw_lines)
    seed_mismatches = [
        item_id
        for item_id in spec["seed_blocked_item_ids"]
        if g2_raw.get(item_id) != predecessor_raw.get(item_id)
    ]
    if seed_mismatches:
        raise CorrectionError(
            f"seed_not_preexisting:{','.join(seed_mismatches)}"
        )
    seed_report = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-seed-preexisting-v2"
        ),
        "status": "PASS",
        "g2_successor_facts_path": repo_relative(G2_SUCCESSOR_FACTS),
        "g2_successor_facts_sha256": sha256_file(G2_SUCCESSOR_FACTS),
        "current_predecessor_facts_sha256": sha256_file(CURRENT_FACTS),
        "seed_denominator": len(spec["seed_blocked_item_ids"]),
        "byte_identical_before_after_correction_0001_count": (
            len(spec["seed_blocked_item_ids"])
        ),
        "mismatch_count": 0,
        "mismatch_item_ids": [],
        "classification": (
            "preexisting_facts_defects_omitted_from_prior_cohort"
        ),
    }
    write_json(SEED_NON_REGRESSION, seed_report)

    successor_bytes = build_successor_facts(rows, raw_lines, ledger)
    write_generated(SUCCESSOR_FACTS, successor_bytes)
    successor_rows, successor_raw_lines = read_jsonl_bytes(SUCCESSOR_FACTS)
    successor_structured, successor_raw = rows_by_id(
        successor_rows, successor_raw_lines
    )
    if [row["item_id"] for row in successor_rows] != [
        row["item_id"] for row in rows
    ]:
        raise CorrectionError("successor_item_order_changed")
    if len(successor_structured) != len(structured):
        raise CorrectionError("successor_item_universe_changed")
    non_target_mismatches = [
        item_id
        for item_id in structured
        if item_id not in rule_for_item
        and predecessor_raw[item_id] != successor_raw[item_id]
    ]
    if non_target_mismatches:
        raise CorrectionError(
            "non_target_byte_identity_mismatch:"
            + ",".join(non_target_mismatches[:10])
        )
    non_target_ids = sorted(set(structured) - set(rule_for_item))
    non_target_report = {
        "schema_version": (
            "dvf-3-3-current-facts-non-target-byte-identity-v2"
        ),
        "status": "PASS",
        "source_row_count": len(rows),
        "corrected_target_row_count": len(rule_for_item),
        "non_target_row_denominator": len(non_target_ids),
        "non_target_byte_identical_count": len(non_target_ids),
        "non_target_byte_mismatch_count": 0,
        "non_target_byte_mismatch_item_ids": [],
        "non_target_item_ids_sha256": canonical_hash(non_target_ids),
        "row_order_preserved": True,
        "item_id_universe_preserved": True,
    }
    write_json(NON_TARGET_IDENTITY, non_target_report)

    previous_ledger_rows, _ = read_jsonl_bytes(PREVIOUS_PATCH_LEDGER)
    previous_corrected_ids = sorted(
        {str(row["item_id"]) for row in previous_ledger_rows}
    )
    if len(previous_corrected_ids) != 184:
        raise CorrectionError("previous_corrected_denominator_mismatch")
    previous_rows, previous_raw_lines = read_jsonl_bytes(
        PREVIOUS_SUCCESSOR_FACTS
    )
    _, previous_raw = rows_by_id(previous_rows, previous_raw_lines)
    predecessor_regressions = [
        item_id
        for item_id in previous_corrected_ids
        if predecessor_raw.get(item_id) != previous_raw.get(item_id)
    ]
    successor_regressions = [
        item_id
        for item_id in previous_corrected_ids
        if successor_raw.get(item_id) != predecessor_raw.get(item_id)
    ]
    overlap = sorted(set(previous_corrected_ids) & set(rule_for_item))
    if predecessor_regressions or successor_regressions or overlap:
        raise CorrectionError(
            "correction_0001_regression:"
            f"predecessor={len(predecessor_regressions)}:"
            f"successor={len(successor_regressions)}:"
            f"overlap={len(overlap)}"
        )
    previous_regression_report = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-0001-regression-v2"
        ),
        "status": "PASS",
        "previous_correction_receipt_path": repo_relative(PREVIOUS_RECEIPT),
        "previous_correction_receipt_sha256": sha256_file(PREVIOUS_RECEIPT),
        "previous_correction_successor_facts_path": repo_relative(
            PREVIOUS_SUCCESSOR_FACTS
        ),
        "previous_correction_successor_facts_sha256": sha256_file(
            PREVIOUS_SUCCESSOR_FACTS
        ),
        "previous_corrected_row_denominator": len(previous_corrected_ids),
        "predecessor_matches_correction_0001_count": (
            len(previous_corrected_ids)
        ),
        "successor_preserved_correction_0001_count": (
            len(previous_corrected_ids)
        ),
        "regression_count": 0,
        "regression_item_ids": [],
        "correction_0002_overlap_count": 0,
        "correction_0002_overlap_item_ids": [],
    }
    write_json(PREVIOUS_REGRESSION, previous_regression_report)

    successor_facts_sha256 = sha256_file(SUCCESSOR_FACTS)
    manifest = build_manifest(
        read_json(CURRENT_MANIFEST),
        spec,
        successor_facts_sha256,
        len(rule_for_item),
        len(ledger),
    )
    write_json(SUCCESSOR_MANIFEST, manifest)

    artifacts = [
        INPUT_IDENTITY,
        ATTESTATION_BINDING,
        FULL_CENSUS,
        COHORT_SUMMARY,
        ROW_LINEAGE,
        PATCH_LEDGER,
        UNRESOLVED_ROWS,
        SEED_NON_REGRESSION,
        NON_TARGET_IDENTITY,
        PREVIOUS_REGRESSION,
        SUCCESSOR_FACTS,
        SUCCESSOR_MANIFEST,
    ]
    receipt = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-successor-receipt-v2"
        ),
        "status": "PASS",
        "successor_id": spec["successor_id"],
        "input_commit": spec["input_commit"],
        "input_tree": spec["input_tree"],
        "predecessor_current_facts_sha256": sha256_file(CURRENT_FACTS),
        "predecessor_current_manifest_sha256": sha256_file(
            CURRENT_MANIFEST
        ),
        "previous_correction_receipt_sha256": sha256_file(
            PREVIOUS_RECEIPT
        ),
        "reviewer_attestation_path": repo_relative(REVIEWER_ATTESTATION),
        "reviewer_attestation_sha256": sha256_file(REVIEWER_ATTESTATION),
        "source_row_count": len(rows),
        "successor_row_count": len(successor_rows),
        "investigated_semantic_cohort_count": len(cohorts),
        "exact_generation_rule_cohort_count": len(cohorts),
        "unique_investigated_row_count": len(cohort_for_item),
        "corrected_row_count": len(rule_for_item),
        "correction_patch_count": len(ledger),
        "unchanged_control_count": len(controls),
        "unresolved_row_count": 0,
        "non_target_byte_identity_denominator": len(non_target_ids),
        "non_target_byte_identity_count": len(non_target_ids),
        "previous_correction_regression_denominator": (
            len(previous_corrected_ids)
        ),
        "previous_correction_regression_count": 0,
        "seed_preexisting_byte_identity_denominator": (
            len(spec["seed_blocked_item_ids"])
        ),
        "seed_preexisting_byte_identity_count": (
            len(spec["seed_blocked_item_ids"])
        ),
        "successor_facts_path": repo_relative(SUCCESSOR_FACTS),
        "successor_facts_sha256": successor_facts_sha256,
        "successor_manifest_path": repo_relative(SUCCESSOR_MANIFEST),
        "successor_manifest_sha256": sha256_file(SUCCESSOR_MANIFEST),
        "correction_spec_path": repo_relative(SPEC),
        "correction_spec_sha256": sha256_file(SPEC),
        "writer_path": repo_relative(Path(__file__)),
        "writer_canonical_lf_sha256": canonical_lf_sha256_file(
            Path(__file__)
        ),
        "artifact_bindings": {
            repo_relative(path): sha256_file(path) for path in artifacts
        },
        "layer4_evidence_consumed_count": 0,
        "unsupported_inference_count": 0,
        "current_facts_mutation_count": 0,
        "current_manifest_mutation_count": 0,
        "registry_cutover_count": 0,
        "food_changes_0_to_13_mutation_count": 0,
        "attempt_0022_mutation_count": 0,
        "foundation_mutation_count": 0,
        "naturalization_attempt_mutation_count": 0,
        "correction_0001_mutation_count": 0,
        "append_only": True,
        "vcs_commit_binding_deferred_until_commit": True,
    }
    write_json(SUCCESSOR_RECEIPT, receipt)
    print(
        json.dumps(
            {
                "status": "PASS",
                "successor_id": spec["successor_id"],
                "investigated_cohort_count": len(cohorts),
                "investigated_row_count": len(cohort_for_item),
                "corrected_row_count": len(rule_for_item),
                "correction_patch_count": len(ledger),
                "unchanged_control_count": len(controls),
                "unresolved_row_count": 0,
                "successor_facts_sha256": successor_facts_sha256,
                "successor_manifest_sha256": sha256_file(
                    SUCCESSOR_MANIFEST
                ),
                "successor_receipt_path": repo_relative(SUCCESSOR_RECEIPT),
                "successor_receipt_sha256": sha256_file(SUCCESSOR_RECEIPT),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
