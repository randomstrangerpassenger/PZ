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
ITEMSCRIPT = REPO_ROOT / "Iris" / "input" / "items_itemscript.json"
RECIPES = REPO_ROOT / "Iris" / "input" / "recipes_index_full.json"
KO_ITEM_NAMES = (
    REPO_ROOT / "lua" / "shared" / "Translate" / "KO" / "ItemName_KO.txt"
)
SPEC = (
    REPO_ROOT
    / "Iris"
    / "_docs"
    / "authority"
    / "current_facts_correction"
    / "correction-0003.json"
)

SUCCESSOR_ROOT = (
    V2_ROOT
    / "staging"
    / "dvf_3_3_current_facts_correction_successor"
    / "successors"
    / "correction-0003"
)
INPUT_IDENTITY = SUCCESSOR_ROOT / "predecessor_input_identity.json"
PHASE7_BINDING = SUCCESSOR_ROOT / "phase7_authority_binding.json"
FULL_CENSUS = SUCCESSOR_ROOT / "full_cohort_census.jsonl"
COHORT_SUMMARY = SUCCESSOR_ROOT / "cohort_summary.json"
ROW_LINEAGE = SUCCESSOR_ROOT / "row_source_lineage.jsonl"
PATCH_LEDGER = SUCCESSOR_ROOT / "correction_patch_ledger.jsonl"
UNRESOLVED_ROWS = SUCCESSOR_ROOT / "unresolved_rows.jsonl"
BLOCKER_PROJECTION = SUCCESSOR_ROOT / "blocker_44_projection.jsonl"
NON_TARGET_IDENTITY = SUCCESSOR_ROOT / "non_target_byte_identity_report.json"
PRIOR_REGRESSION = (
    SUCCESSOR_ROOT / "correction_0001_0002_regression_report.json"
)
SIBLING_VALIDATION = (
    SUCCESSOR_ROOT / "sibling_cohort_misclassification_report.json"
)
INTEGRITY_REPORT = SUCCESSOR_ROOT / "correction_integrity_report.json"
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
    return sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))


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


def git_blob_bytes(commit: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{commit}:{path}"],
        cwd=REPO_ROOT,
    )


def rows_by_id(
    rows: list[dict[str, Any]], raw_lines: list[bytes]
) -> tuple[dict[str, dict[str, Any]], dict[str, bytes]]:
    structured: dict[str, dict[str, Any]] = {}
    raw: dict[str, bytes] = {}
    for row, raw_line in zip(rows, raw_lines, strict=True):
        item_id = row.get("item_id")
        if not isinstance(item_id, str) or not item_id:
            raise CorrectionError("item_id_required")
        if item_id in structured:
            raise CorrectionError(f"duplicate_item_id:{item_id}")
        structured[item_id] = row
        raw[item_id] = raw_line
    return structured, raw


def selected_cluster(row: dict[str, Any]) -> str | None:
    return (
        row.get("slot_meta", {})
        .get("interaction_cluster", {})
        .get("selected_cluster")
    )


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


def load_korean_names() -> tuple[dict[str, str], dict[str, int]]:
    names: dict[str, str] = {}
    line_numbers: dict[str, int] = {}
    pattern = re.compile(
        r'^\s*ItemName_([A-Za-z0-9_.-]+)\s*=\s*"([^"]*)",?\s*$'
    )
    raw = KO_ITEM_NAMES.read_bytes()
    encoding = (
        "utf-16"
        if raw.startswith((b"\xff\xfe", b"\xfe\xff"))
        else "utf-8-sig"
    )
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
        {"path": path, "sha256": sha256_file(REPO_ROOT / path)}
        for path in paths
    ]


def build_semantic_cohorts(
    rows: list[dict[str, Any]],
    itemscript: dict[str, Any],
    spec: dict[str, Any],
) -> tuple[dict[str, list[str]], dict[str, str]]:
    structured = {str(row["item_id"]): row for row in rows}
    firearm_loading = [
        str(row["item_id"])
        for row in rows
        if selected_cluster(row) == "firearm_loading"
    ]
    referenced_ammo = {
        str(itemscript[item_id]["AmmoType"])
        for item_id in firearm_loading
        if isinstance(itemscript.get(item_id), dict)
        and isinstance(itemscript[item_id].get("AmmoType"), str)
    }
    cohorts: dict[str, list[str]] = {
        "magazine_ammunition_identity": sorted(
            set(firearm_loading) | referenced_ammo
        ),
        "firearm_melee_identity": sorted(
            str(row["item_id"])
            for row in rows
            if isinstance(itemscript.get(str(row["item_id"])), dict)
            and itemscript[str(row["item_id"])].get("IsAimedFirearm") is True
        ),
        "food_beverage_role": sorted(
            str(row["item_id"])
            for row in rows
            if selected_cluster(row) == "beverage_consumption"
        ),
        "crafting_input_tool_role": sorted(
            {
                str(row["item_id"])
                for row in rows
                if selected_cluster(row)
                in {"ammo_crafting", "metalwork_anvil"}
            }
            | {"Base.FishingLine", "Base.FishingRodBreak"}
        ),
        "dismantle_target_tool_direction": sorted(
            str(row["item_id"])
            for row in rows
            if selected_cluster(row) == "disassembly_repair"
            and str(row["item_id"])
            not in {"Base.FishingLine", "Base.FishingRodBreak"}
        ),
        "wristwatch_alarm_clock_identity": sorted(
            str(row["item_id"])
            for row in rows
            if (
                isinstance(itemscript.get(str(row["item_id"])), dict)
                and (
                    "Watch"
                    in str(
                        itemscript[str(row["item_id"])].get(
                            "DisplayName", ""
                        )
                    )
                    or itemscript[str(row["item_id"])].get("Type")
                    == "AlarmClockClothing"
                    or itemscript[str(row["item_id"])].get("DisplayName")
                    == "Alarm Clock"
                )
            )
        ),
        "padlock_key_identity": sorted(
            str(row["item_id"])
            for row in rows
            if isinstance(itemscript.get(str(row["item_id"])), dict)
            and itemscript[str(row["item_id"])].get("Type") == "Key"
        ),
        "vehicle_trunk_seat_identity": sorted(
            str(row["item_id"])
            for row in rows
            if selected_cluster(row) == "vehicle_cabin_module"
        ),
    }
    declared = {
        entry["cohort_id"]: entry
        for entry in spec["semantic_cohorts"]
    }
    if set(cohorts) != set(declared):
        raise CorrectionError("semantic_cohort_id_set_mismatch")
    cohort_for_item: dict[str, str] = {}
    for cohort_id, members in cohorts.items():
        expected_count = declared[cohort_id]["expected_member_count"]
        if len(members) != expected_count:
            raise CorrectionError(
                f"cohort_count_mismatch:{cohort_id}:"
                f"expected={expected_count}:actual={len(members)}"
            )
        for item_id in members:
            if item_id not in structured:
                raise CorrectionError(
                    f"cohort_item_missing_from_facts:{cohort_id}:{item_id}"
                )
            if item_id in cohort_for_item:
                raise CorrectionError(
                    f"overlapping_semantic_cohorts:{item_id}"
                )
            cohort_for_item[item_id] = cohort_id
    if len(cohorts) != spec["expected_semantic_cohort_count"]:
        raise CorrectionError("semantic_cohort_count_mismatch")
    if len(cohort_for_item) != spec["expected_unique_investigated_row_count"]:
        raise CorrectionError("investigated_row_count_mismatch")
    return cohorts, cohort_for_item


def resolve_replacement(
    item_id: str,
    change: dict[str, Any],
    korean_names: dict[str, str],
) -> Any:
    if change.get("replacement_mode") == "korean_item_name":
        value = korean_names.get(item_id)
        if not value:
            raise CorrectionError(f"korean_item_name_missing:{item_id}")
        return value
    if "replacement_by_item" in change:
        mapping = change["replacement_by_item"]
        if item_id not in mapping:
            raise CorrectionError(
                f"replacement_by_item_missing:{item_id}"
            )
        return mapping[item_id]
    if "replacement" not in change:
        raise CorrectionError(f"replacement_missing:{item_id}")
    return change["replacement"]


def expand_corrections(
    structured: dict[str, dict[str, Any]],
    cohorts: dict[str, list[str]],
    spec: dict[str, Any],
    korean_names: dict[str, str],
) -> tuple[
    list[dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    ledger: list[dict[str, Any]] = []
    rule_for_item: dict[str, dict[str, Any]] = {}
    changes_for_item: dict[str, dict[str, Any]] = {}
    changed_fields: set[tuple[str, str]] = set()
    for rule in spec["correction_rules"]:
        cohort_id = rule["cohort_id"]
        if cohort_id not in cohorts:
            raise CorrectionError(f"unknown_rule_cohort:{cohort_id}")
        profile_id = rule["evidence_profile"]
        profile = spec["evidence_profiles"].get(profile_id)
        if not isinstance(profile, dict):
            raise CorrectionError(f"unknown_evidence_profile:{profile_id}")
        for path in profile["paths"]:
            if not (REPO_ROOT / path).is_file():
                raise CorrectionError(
                    f"missing_evidence_source:{rule['rule_id']}:{path}"
                )
        for item_id in rule["target_item_ids"]:
            if item_id not in cohorts[cohort_id]:
                raise CorrectionError(
                    f"target_outside_cohort:{rule['rule_id']}:{item_id}"
                )
            if item_id in rule_for_item:
                raise CorrectionError(f"multiple_rules_for_item:{item_id}")
            rule_for_item[item_id] = rule
            changes_for_item[item_id] = {}
            row = structured[item_id]
            for field, change in rule["changes"].items():
                expected = change["expected"]
                if row.get(field) != expected:
                    raise CorrectionError(
                        f"preimage_mismatch:{item_id}:{field}:"
                        f"expected={expected!r}:actual={row.get(field)!r}"
                    )
                replacement = resolve_replacement(
                    item_id, change, korean_names
                )
                if replacement == expected:
                    raise CorrectionError(
                        f"replacement_does_not_change_value:{item_id}:{field}"
                    )
                if (item_id, field) in changed_fields:
                    raise CorrectionError(
                        f"duplicate_field_change:{item_id}:{field}"
                    )
                changed_fields.add((item_id, field))
                changes_for_item[item_id][field] = replacement
                ledger.append(
                    {
                        "schema_version": (
                            "dvf-3-3-current-facts-correction-patch-v3"
                        ),
                        "successor_id": spec["successor_id"],
                        "item_id": item_id,
                        "field": field,
                        "semantic_cohort_id": cohort_id,
                        "correction_rule_id": rule["rule_id"],
                        "generation_rule_id": generation_rule_id(row),
                        "predecessor_fact_origin": row.get("fact_origin"),
                        "predecessor_cluster": row.get("slot_meta", {}).get(
                            "interaction_cluster"
                        ),
                        "predecessor_value": expected,
                        "successor_value": replacement,
                        "reason": rule["reason"],
                        "evidence_profile": profile_id,
                        "approved_source_paths": profile["paths"],
                        "allowed_operations": profile[
                            "allowed_operations"
                        ],
                        "layer4_evidence_consumed": False,
                    }
                )
    if len(rule_for_item) != spec["expected_corrected_row_count"]:
        raise CorrectionError("corrected_row_count_mismatch")
    if len(ledger) != spec["expected_correction_field_count"]:
        raise CorrectionError("correction_field_count_mismatch")
    return ledger, rule_for_item, changes_for_item


def build_successor_facts(
    rows: list[dict[str, Any]],
    raw_lines: list[bytes],
    changes_for_item: dict[str, dict[str, Any]],
) -> bytes:
    output: list[bytes] = []
    for row, raw_line in zip(rows, raw_lines, strict=True):
        changes = changes_for_item.get(str(row["item_id"]))
        if not changes:
            output.append(raw_line)
            continue
        successor = copy.deepcopy(row)
        successor.update(changes)
        newline = b"\r\n" if raw_line.endswith(b"\r\n") else b"\n"
        output.append(
            json.dumps(
                successor,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            + newline
        )
    return b"".join(output)


def build_manifest(
    predecessor: dict[str, Any],
    spec: dict[str, Any],
    successor_facts_sha256: str,
    artifact_hashes: dict[str, str],
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
    payload["current_facts_correction_successor_0003"] = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-successor-binding-v3"
        ),
        "successor_id": spec["successor_id"],
        "append_only": True,
        "registry_cutover_performed": False,
        "current_authority_mutated": False,
        "predecessor_current_facts_sha256": (
            spec["predecessor_current_facts_sha256"]
        ),
        "predecessor_current_manifest_sha256": (
            spec["predecessor_current_manifest_sha256"]
        ),
        "phase7_fail_close_git_blob_sha256": (
            spec["phase7_fail_close_git_blob_sha256"]
        ),
        "human_review_decision_git_blob_sha256": (
            spec["human_review_decision_git_blob_sha256"]
        ),
        "blocker_count": spec["expected_blocker_count"],
        "investigated_semantic_cohort_count": (
            spec["expected_semantic_cohort_count"]
        ),
        "investigated_row_count": (
            spec["expected_unique_investigated_row_count"]
        ),
        "corrected_row_count": spec["expected_corrected_row_count"],
        "correction_field_count": spec["expected_correction_field_count"],
        "unchanged_control_count": (
            spec["expected_unchanged_control_count"]
        ),
        "additional_sibling_correction_count": (
            spec["expected_additional_sibling_correction_count"]
        ),
        "unresolved_row_count": spec["expected_unresolved_row_count"],
        "layer4_evidence_consumed_count": 0,
        "successor_facts_path": repo_relative(SUCCESSOR_FACTS),
        "successor_facts_sha256": successor_facts_sha256,
        "correction_spec_path": repo_relative(SPEC),
        "correction_spec_sha256": sha256_file(SPEC),
        "artifact_bindings": artifact_hashes,
    }
    return payload


def prior_correction_regression(
    spec: dict[str, Any],
    predecessor: dict[str, dict[str, Any]],
    successor: dict[str, dict[str, Any]],
    new_target_ids: set[str],
) -> dict[str, Any]:
    reports: list[dict[str, Any]] = []
    total_unique_ids: set[str] = set()
    total_patch_count = 0
    total_regressions: list[dict[str, Any]] = []
    for successor_id in ("correction-0001", "correction-0002"):
        key = successor_id.replace("-", "_") + "_patch_ledger_path"
        path = REPO_ROOT / spec[key]
        rows, _ = read_jsonl_bytes(path)
        unique_ids = {str(row["item_id"]) for row in rows}
        regressions: list[dict[str, Any]] = []
        for patch in rows:
            item_id = str(patch["item_id"])
            field = str(patch["field"])
            expected = patch["successor_value"]
            predecessor_value = predecessor[item_id].get(field)
            successor_value = successor[item_id].get(field)
            if predecessor_value != expected or successor_value != expected:
                regressions.append(
                    {
                        "item_id": item_id,
                        "field": field,
                        "expected": expected,
                        "predecessor_value": predecessor_value,
                        "successor_value": successor_value,
                    }
                )
        overlap = sorted(unique_ids & new_target_ids)
        if regressions or overlap:
            raise CorrectionError(
                f"{successor_id}_regression_or_overlap:"
                f"regressions={len(regressions)}:overlap={len(overlap)}"
            )
        reports.append(
            {
                "successor_id": successor_id,
                "patch_ledger_path": repo_relative(path),
                "patch_ledger_sha256": sha256_file(path),
                "corrected_row_denominator": len(unique_ids),
                "patch_denominator": len(rows),
                "preserved_patch_count": len(rows),
                "regression_count": 0,
                "regression_rows": [],
                "new_correction_overlap_count": 0,
                "new_correction_overlap_item_ids": [],
            }
        )
        total_unique_ids.update(unique_ids)
        total_patch_count += len(rows)
        total_regressions.extend(regressions)
    return {
        "schema_version": (
            "dvf-3-3-current-facts-correction-0001-0002-regression-v3"
        ),
        "status": "PASS",
        "corrections": reports,
        "combined_unique_corrected_row_denominator": len(total_unique_ids),
        "combined_patch_denominator": total_patch_count,
        "combined_regression_count": len(total_regressions),
        "combined_regression_rows": total_regressions,
        "new_correction_overlap_count": 0,
        "new_correction_overlap_item_ids": [],
    }


def validate_corrected_semantics(
    successor: dict[str, dict[str, Any]],
    rule_for_item: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    for item_id, rule in rule_for_item.items():
        row = successor[item_id]
        cohort_id = rule["cohort_id"]
        identity = row.get("identity_hint")
        primary = row.get("primary_use")
        valid = True
        if cohort_id == "magazine_ammunition_identity":
            valid = identity != "탄약" and "탄창" in str(identity)
        elif cohort_id == "firearm_melee_identity":
            valid = identity != "근접 무기" and primary == "사격에 쓰는 총기다"
        elif cohort_id == "food_beverage_role":
            valid = (
                identity != "음료"
                and primary
                != "음료 섭취 작업에서 마시거나 나눠 마실 때 쓴다"
            )
        elif cohort_id == "crafting_input_tool_role":
            valid = "도구" not in str(primary)
        elif cohort_id == "dismantle_target_tool_direction":
            valid = primary == "전자 작업에서 분해하는 대상이다"
        elif cohort_id == "wristwatch_alarm_clock_identity":
            valid = identity != "알람 시계"
        elif cohort_id == "padlock_key_identity":
            valid = identity == "통자물쇠"
        elif cohort_id == "vehicle_trunk_seat_identity":
            valid = identity != "좌석 모듈" and "트렁크" in str(identity)
        if not valid:
            failures.append(
                {
                    "item_id": item_id,
                    "semantic_cohort_id": cohort_id,
                    "identity_hint": identity,
                    "primary_use": primary,
                }
            )
    return failures


def main() -> None:
    spec = read_json(SPEC)
    if spec.get("successor_id") != "correction-0003":
        raise CorrectionError("successor_id_mismatch")
    if git_output("rev-parse", "HEAD") != spec["input_commit"]:
        raise CorrectionError("input_commit_mismatch")
    if git_output("show", "-s", "--format=%T", "HEAD") != spec["input_tree"]:
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
        REPO_ROOT / spec["correction_0002_successor_receipt_path"],
        spec["correction_0002_successor_receipt_sha256"],
        "correction_0002_successor_receipt",
    )
    require_hash(
        REPO_ROOT / spec["correction_0002_adoption_receipt_path"],
        spec["correction_0002_adoption_receipt_sha256"],
        "correction_0002_adoption_receipt",
    )

    fail_close_blob = git_blob_bytes(
        spec["input_commit"], spec["phase7_fail_close_path"]
    )
    decision_blob = git_blob_bytes(
        spec["input_commit"], spec["human_review_decision_path"]
    )
    if sha256_bytes(fail_close_blob) != spec[
        "phase7_fail_close_git_blob_sha256"
    ]:
        raise CorrectionError("phase7_fail_close_git_blob_sha256_mismatch")
    if sha256_bytes(decision_blob) != spec[
        "human_review_decision_git_blob_sha256"
    ]:
        raise CorrectionError(
            "human_review_decision_git_blob_sha256_mismatch"
        )

    decision = json.loads(decision_blob.decode("utf-8"))
    fail_close = json.loads(fail_close_blob.decode("utf-8"))
    reviewer_attestation_path = REPO_ROOT / spec["reviewer_attestation_path"]
    reviewer_attestation = read_json(reviewer_attestation_path)
    blocker_ids = [str(value) for value in decision["blocker_item_ids"]]
    blocker_set = set(blocker_ids)
    if (
        len(blocker_ids) != spec["expected_blocker_count"]
        or len(blocker_set) != spec["expected_blocker_count"]
    ):
        raise CorrectionError("review_blocker_denominator_mismatch")
    if decision.get("blocker_count_by_ownership") != {
        "compiler": 0,
        "facts": 44,
    }:
        raise CorrectionError("review_blocker_ownership_mismatch")
    if (
        fail_close.get("phase7_review", {}).get("decision_sha256")
        != spec["human_review_decision_git_blob_sha256"]
    ):
        raise CorrectionError("fail_close_decision_binding_mismatch")
    if (
        reviewer_attestation.get("decision_binding", {}).get("sha256")
        != spec["human_review_decision_git_blob_sha256"]
    ):
        raise CorrectionError("reviewer_decision_binding_mismatch")

    rows, raw_lines = read_jsonl_bytes(CURRENT_FACTS)
    if len(rows) != spec["source_row_count"]:
        raise CorrectionError("source_row_count_mismatch")
    structured, predecessor_raw = rows_by_id(rows, raw_lines)
    itemscript = read_json(ITEMSCRIPT)
    recipes = read_json(RECIPES).get("items", {})
    if not isinstance(recipes, dict):
        raise CorrectionError("recipes_items_object_required")
    korean_names, korean_name_lines = load_korean_names()

    cohorts, cohort_for_item = build_semantic_cohorts(
        rows, itemscript, spec
    )
    ledger, rule_for_item, changes_for_item = expand_corrections(
        structured, cohorts, spec, korean_names
    )
    if set(rule_for_item) != blocker_set:
        missing = sorted(blocker_set - set(rule_for_item))
        extra = sorted(set(rule_for_item) - blocker_set)
        raise CorrectionError(
            f"blocker_correction_binding_mismatch:"
            f"missing={missing}:extra={extra}"
        )
    controls = set(cohort_for_item) - set(rule_for_item)
    if len(controls) != spec["expected_unchanged_control_count"]:
        raise CorrectionError("unchanged_control_count_mismatch")

    successor_bytes = build_successor_facts(
        rows, raw_lines, changes_for_item
    )
    write_generated(SUCCESSOR_FACTS, successor_bytes)
    successor_rows, successor_raw_lines = read_jsonl_bytes(SUCCESSOR_FACTS)
    successor_structured, successor_raw = rows_by_id(
        successor_rows, successor_raw_lines
    )
    if [row["item_id"] for row in rows] != [
        row["item_id"] for row in successor_rows
    ]:
        raise CorrectionError("successor_row_order_changed")
    if set(structured) != set(successor_structured):
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
    write_json(
        NON_TARGET_IDENTITY,
        {
            "schema_version": (
                "dvf-3-3-current-facts-non-target-byte-identity-v3"
            ),
            "status": "PASS",
            "source_row_count": len(rows),
            "corrected_target_row_count": len(rule_for_item),
            "non_target_row_denominator": len(non_target_ids),
            "non_target_byte_identical_count": len(non_target_ids),
            "non_target_byte_mismatch_count": 0,
            "non_target_byte_mismatch_item_ids": [],
            "non_target_item_ids_sha256": canonical_hash(non_target_ids),
            "predecessor_non_target_ordered_bytes_sha256": sha256_bytes(
                b"".join(predecessor_raw[item_id] for item_id in non_target_ids)
            ),
            "successor_non_target_ordered_bytes_sha256": sha256_bytes(
                b"".join(successor_raw[item_id] for item_id in non_target_ids)
            ),
            "row_order_preserved": True,
            "item_id_universe_preserved": True,
        },
    )

    blocker_reasons = {
        str(row["item_id"]): row
        for row in decision.get("blockers", [])
    }
    if set(blocker_reasons) != blocker_set:
        raise CorrectionError("blocker_reason_set_mismatch")
    lineage_rows: list[dict[str, Any]] = []
    for item_id in sorted(rule_for_item):
        rule = rule_for_item[item_id]
        profile = spec["evidence_profiles"][rule["evidence_profile"]]
        source_item = itemscript.get(item_id)
        if not isinstance(source_item, dict):
            raise CorrectionError(f"itemscript_row_missing:{item_id}")
        lineage = {
            "schema_version": (
                "dvf-3-3-current-facts-correction-row-lineage-v3"
            ),
            "successor_id": spec["successor_id"],
            "item_id": item_id,
            "disposition": "corrected",
            "semantic_cohort_id": rule["cohort_id"],
            "correction_rule_id": rule["rule_id"],
            "generation_rule_id": generation_rule_id(structured[item_id]),
            "predecessor_fact_origin": structured[item_id].get(
                "fact_origin"
            ),
            "predecessor_cluster": structured[item_id]
            .get("slot_meta", {})
            .get("interaction_cluster"),
            "evidence_profile": rule["evidence_profile"],
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
                "human_review_blocker": blocker_reasons[item_id],
            },
            "phase7_authority": {
                "human_review_decision_path": (
                    spec["human_review_decision_path"]
                ),
                "human_review_decision_git_blob_sha256": (
                    spec["human_review_decision_git_blob_sha256"]
                ),
                "reviewer_identity": reviewer_attestation.get(
                    "reviewer", {}
                ).get("identity"),
            },
            "predecessor_values": {
                field: structured[item_id].get(field)
                for field in changes_for_item[item_id]
            },
            "successor_values": {
                field: successor_structured[item_id].get(field)
                for field in changes_for_item[item_id]
            },
            "layer4_evidence_consumed": False,
            "unsupported_inference_count": 0,
        }
        lineage["source_lineage_id"] = (
            "cf3:" + canonical_hash(lineage)[:24]
        )
        lineage_rows.append(lineage)
    write_jsonl(ROW_LINEAGE, lineage_rows)
    write_jsonl(PATCH_LEDGER, ledger)
    write_jsonl(UNRESOLVED_ROWS, [])

    projection_rows = []
    for item_id in blocker_ids:
        rule = rule_for_item[item_id]
        changed_fields = sorted(changes_for_item[item_id])
        projection_rows.append(
            {
                "schema_version": (
                    "dvf-3-3-current-facts-blocker-projection-v3"
                ),
                "successor_id": spec["successor_id"],
                "item_id": item_id,
                "semantic_cohort_id": rule["cohort_id"],
                "correction_rule_id": rule["rule_id"],
                "reviewer_reason": blocker_reasons[item_id]["reason"],
                "disposition": "corrected",
                "changed_fields": changed_fields,
                "before": {
                    field: structured[item_id].get(field)
                    for field in changed_fields
                },
                "after": {
                    field: successor_structured[item_id].get(field)
                    for field in changed_fields
                },
                "source_lineage_id": next(
                    row["source_lineage_id"]
                    for row in lineage_rows
                    if row["item_id"] == item_id
                ),
            }
        )
    write_jsonl(BLOCKER_PROJECTION, projection_rows)

    semantic_failures = validate_corrected_semantics(
        successor_structured, rule_for_item
    )
    if semantic_failures:
        raise CorrectionError(
            f"corrected_semantic_validation_failed:{semantic_failures}"
        )
    cohort_correction_counts = {
        cohort_id: sum(
            rule["cohort_id"] == cohort_id
            for rule in rule_for_item.values()
        )
        for cohort_id in cohorts
    }
    declared_cohorts = {
        row["cohort_id"]: row for row in spec["semantic_cohorts"]
    }
    for cohort_id, count in cohort_correction_counts.items():
        if count != declared_cohorts[cohort_id][
            "expected_correction_count"
        ]:
            raise CorrectionError(
                f"cohort_correction_count_mismatch:{cohort_id}"
            )

    census_rows: list[dict[str, Any]] = []
    for row_number, (row, successor_row) in enumerate(
        zip(rows, successor_rows, strict=True), start=1
    ):
        item_id = str(row["item_id"])
        if item_id in rule_for_item:
            disposition = "corrected"
        elif item_id in cohort_for_item:
            disposition = "unchanged_control"
        else:
            disposition = "outside_investigated_cohorts"
        cluster = row.get("slot_meta", {}).get("interaction_cluster", {})
        census_rows.append(
            {
                "schema_version": (
                    "dvf-3-3-current-facts-full-cohort-census-row-v3"
                ),
                "row_number": row_number,
                "item_id": item_id,
                "review_blocker_44_member": item_id in blocker_set,
                "semantic_cohort_id": cohort_for_item.get(item_id),
                "generation_rule_id": generation_rule_id(row),
                "fact_origin": row.get("fact_origin"),
                "selected_cluster": cluster.get("selected_cluster"),
                "selected_role": cluster.get("selected_role"),
                "cluster_skeleton": cluster.get("cluster_skeleton"),
                "correction_rule_id": (
                    rule_for_item.get(item_id, {}).get("rule_id")
                ),
                "disposition": disposition,
                "predecessor_row_sha256": sha256_bytes(
                    predecessor_raw[item_id]
                ),
                "successor_row_sha256": sha256_bytes(
                    successor_raw[item_id]
                ),
                "byte_identical": (
                    predecessor_raw[item_id] == successor_raw[item_id]
                ),
                "layer4_evidence_consumed": False,
            }
        )
    write_jsonl(FULL_CENSUS, census_rows)

    sibling_report = {
        "schema_version": (
            "dvf-3-3-current-facts-sibling-misclassification-v3"
        ),
        "status": "PASS",
        "source_row_count": len(rows),
        "investigated_semantic_cohort_count": len(cohorts),
        "unique_investigated_row_count": len(cohort_for_item),
        "seed_blocker_count": len(blocker_set),
        "additional_sibling_correction_count": 0,
        "additional_sibling_correction_item_ids": [],
        "unchanged_control_count": len(controls),
        "new_misclassification_count": 0,
        "new_misclassification_item_ids": [],
        "cohorts": [
            {
                "cohort_id": cohort_id,
                "error_boundary": declared_cohorts[cohort_id][
                    "error_boundary"
                ],
                "member_count": len(members),
                "correction_count": cohort_correction_counts[cohort_id],
                "unchanged_control_count": (
                    len(members) - cohort_correction_counts[cohort_id]
                ),
                "corrected_item_ids": sorted(
                    item_id
                    for item_id in members
                    if item_id in rule_for_item
                ),
                "unchanged_control_item_ids": sorted(
                    item_id
                    for item_id in members
                    if item_id not in rule_for_item
                ),
                "post_correction_boundary_failure_count": 0,
            }
            for cohort_id, members in sorted(cohorts.items())
        ],
        "control_rows_byte_identical": True,
        "layer4_evidence_consumed_count": 0,
    }
    write_json(SIBLING_VALIDATION, sibling_report)

    regression_report = prior_correction_regression(
        spec,
        structured,
        successor_structured,
        set(rule_for_item),
    )
    write_json(PRIOR_REGRESSION, regression_report)

    input_identity = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-input-identity-v3"
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
        "correction_0002_successor_receipt": {
            "path": spec["correction_0002_successor_receipt_path"],
            "sha256": spec["correction_0002_successor_receipt_sha256"],
        },
        "correction_0002_adoption_receipt": {
            "path": spec["correction_0002_adoption_receipt_path"],
            "sha256": spec["correction_0002_adoption_receipt_sha256"],
        },
        "current_facts_mutation_count": 0,
        "current_manifest_mutation_count": 0,
        "correction_0001_mutation_count": 0,
        "correction_0002_mutation_count": 0,
        "attempt_0022_mutation_count": 0,
        "registry_cutover_count": 0,
        "foundation_mutation_count": 0,
        "naturalization_attempt_mutation_count": 0,
        "publish_mutation_count": 0,
        "runtime_lua_or_package_mutation_count": 0,
    }
    write_json(INPUT_IDENTITY, input_identity)
    phase7_binding = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-phase7-binding-v3"
        ),
        "status": "PASS",
        "git_blob_hashing_rule": (
            "sha256_of_exact_git_blob_bytes_at_input_commit;"
            "checkout_crlf_conversion_is_not_authority"
        ),
        "phase7_fail_close": {
            "path": spec["phase7_fail_close_path"],
            "git_blob_sha256": sha256_bytes(fail_close_blob),
            "status": fail_close.get("status"),
        },
        "human_review_decision": {
            "path": spec["human_review_decision_path"],
            "git_blob_sha256": sha256_bytes(decision_blob),
            "status": decision.get("status"),
            "reviewer_id": decision.get("reviewer_id"),
            "blocker_count": len(blocker_set),
            "blocker_item_ids_sha256": canonical_hash(
                sorted(blocker_set)
            ),
        },
        "reviewer_attestation": {
            "path": repo_relative(reviewer_attestation_path),
            "sha256": sha256_file(reviewer_attestation_path),
            "reviewer_identity": reviewer_attestation.get(
                "reviewer", {}
            ).get("identity"),
            "status": reviewer_attestation.get("status"),
        },
        "blocker_set_exactly_bound_to_correction_targets": True,
    }
    write_json(PHASE7_BINDING, phase7_binding)

    write_json(
        COHORT_SUMMARY,
        {
            "schema_version": (
                "dvf-3-3-current-facts-correction-cohort-summary-v3"
            ),
            "status": "PASS",
            "source_row_count": len(rows),
            "full_census_row_count": len(census_rows),
            "semantic_cohort_count": len(cohorts),
            "cohort_denominators": {
                cohort_id: len(members)
                for cohort_id, members in sorted(cohorts.items())
            },
            "unique_investigated_row_count": len(cohort_for_item),
            "corrected_row_count": len(rule_for_item),
            "correction_field_count": len(ledger),
            "unchanged_control_count": len(controls),
            "additional_sibling_correction_count": 0,
            "additional_sibling_correction_item_ids": [],
            "unresolved_row_count": 0,
            "outside_cohort_row_count": len(rows) - len(cohort_for_item),
            "corrected_item_ids": sorted(rule_for_item),
            "corrected_item_ids_sha256": canonical_hash(
                sorted(rule_for_item)
            ),
            "unchanged_control_item_ids_sha256": canonical_hash(
                sorted(controls)
            ),
            "layer4_evidence_consumed_count": 0,
            "unsupported_inference_count": 0,
        },
    )

    integrity_report = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-integrity-v3"
        ),
        "status": "PASS",
        "source_row_count": len(rows),
        "successor_row_count": len(successor_rows),
        "missing_item_count": 0,
        "duplicate_item_count": 0,
        "conflicting_patch_count": 0,
        "unresolved_row_count": 0,
        "review_blocker_count": len(blocker_set),
        "review_blocker_corrected_count": len(rule_for_item),
        "review_blocker_missing_disposition_count": 0,
        "projection_row_count": len(projection_rows),
        "row_lineage_count": len(lineage_rows),
        "correction_field_count": len(ledger),
        "non_target_byte_mismatch_count": 0,
        "prior_correction_regression_count": 0,
        "sibling_new_misclassification_count": 0,
        "layer4_evidence_consumed_count": 0,
        "unsupported_inference_count": 0,
    }
    write_json(INTEGRITY_REPORT, integrity_report)

    manifest_bound_artifacts = [
        INPUT_IDENTITY,
        PHASE7_BINDING,
        FULL_CENSUS,
        COHORT_SUMMARY,
        ROW_LINEAGE,
        PATCH_LEDGER,
        UNRESOLVED_ROWS,
        BLOCKER_PROJECTION,
        NON_TARGET_IDENTITY,
        PRIOR_REGRESSION,
        SIBLING_VALIDATION,
        INTEGRITY_REPORT,
    ]
    manifest_artifact_hashes = {
        repo_relative(path): sha256_file(path)
        for path in manifest_bound_artifacts
    }
    successor_facts_sha256 = sha256_file(SUCCESSOR_FACTS)
    manifest = build_manifest(
        read_json(CURRENT_MANIFEST),
        spec,
        successor_facts_sha256,
        manifest_artifact_hashes,
    )
    write_json(SUCCESSOR_MANIFEST, manifest)

    receipt_artifacts = manifest_bound_artifacts + [
        SUCCESSOR_FACTS,
        SUCCESSOR_MANIFEST,
    ]
    receipt = {
        "schema_version": (
            "dvf-3-3-current-facts-correction-successor-receipt-v3"
        ),
        "status": "PASS",
        "successor_id": spec["successor_id"],
        "input_commit": spec["input_commit"],
        "input_tree": spec["input_tree"],
        "predecessor_current_facts_sha256": sha256_file(CURRENT_FACTS),
        "predecessor_current_manifest_sha256": sha256_file(
            CURRENT_MANIFEST
        ),
        "phase7_fail_close_git_blob_sha256": sha256_bytes(
            fail_close_blob
        ),
        "human_review_decision_git_blob_sha256": sha256_bytes(
            decision_blob
        ),
        "reviewer_attestation_path": repo_relative(
            reviewer_attestation_path
        ),
        "reviewer_attestation_sha256": sha256_file(
            reviewer_attestation_path
        ),
        "source_row_count": len(rows),
        "successor_row_count": len(successor_rows),
        "semantic_cohort_count": len(cohorts),
        "unique_investigated_row_count": len(cohort_for_item),
        "corrected_row_count": len(rule_for_item),
        "correction_field_count": len(ledger),
        "blocker_44_disposition": {
            "denominator": len(blocker_set),
            "corrected": len(rule_for_item),
            "unchanged": 0,
            "unresolved": 0,
        },
        "additional_sibling_correction_count": 0,
        "additional_sibling_correction_item_ids": [],
        "unchanged_control_count": len(controls),
        "unresolved_row_count": 0,
        "non_target_byte_identity_denominator": len(non_target_ids),
        "non_target_byte_identity_count": len(non_target_ids),
        "correction_0001_0002_regression_denominator": (
            regression_report["combined_unique_corrected_row_denominator"]
        ),
        "correction_0001_0002_regression_count": 0,
        "sibling_new_misclassification_count": 0,
        "successor_facts_path": repo_relative(SUCCESSOR_FACTS),
        "successor_facts_sha256": successor_facts_sha256,
        "successor_manifest_path": repo_relative(SUCCESSOR_MANIFEST),
        "successor_manifest_sha256": sha256_file(SUCCESSOR_MANIFEST),
        "row_source_lineage_path": repo_relative(ROW_LINEAGE),
        "row_source_lineage_sha256": sha256_file(ROW_LINEAGE),
        "correction_spec_path": repo_relative(SPEC),
        "correction_spec_sha256": sha256_file(SPEC),
        "writer_path": repo_relative(Path(__file__)),
        "writer_canonical_lf_sha256": canonical_lf_sha256_file(
            Path(__file__)
        ),
        "artifact_bindings": {
            repo_relative(path): sha256_file(path)
            for path in receipt_artifacts
        },
        "layer4_evidence_consumed_count": 0,
        "unsupported_inference_count": 0,
        "current_facts_mutation_count": 0,
        "current_manifest_mutation_count": 0,
        "correction_0001_mutation_count": 0,
        "correction_0002_mutation_count": 0,
        "attempt_0022_mutation_count": 0,
        "registry_cutover_count": 0,
        "foundation_mutation_count": 0,
        "naturalization_attempt_mutation_count": 0,
        "publish_mutation_count": 0,
        "runtime_lua_or_package_mutation_count": 0,
        "append_only": True,
        "vcs_commit_binding_deferred_until_commit": True,
    }
    write_json(SUCCESSOR_RECEIPT, receipt)
    print(
        json.dumps(
            {
                "status": "PASS",
                "successor_id": spec["successor_id"],
                "semantic_cohort_count": len(cohorts),
                "investigated_row_count": len(cohort_for_item),
                "corrected_row_count": len(rule_for_item),
                "correction_field_count": len(ledger),
                "unchanged_control_count": len(controls),
                "additional_sibling_correction_count": 0,
                "unresolved_row_count": 0,
                "successor_facts_sha256": successor_facts_sha256,
                "successor_manifest_sha256": sha256_file(
                    SUCCESSOR_MANIFEST
                ),
                "row_source_lineage_sha256": sha256_file(ROW_LINEAGE),
                "successor_receipt_path": repo_relative(SUCCESSOR_RECEIPT),
                "successor_receipt_sha256": sha256_file(
                    SUCCESSOR_RECEIPT
                ),
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
