from __future__ import annotations

import hashlib
import json
from pathlib import Path


EXPECTED_THRESHOLD_POLICY_SHA256 = (
    "50c2fdf90e43b2a44b7aed78115fa57f6555b6013c5224bb7080de005b83a9de"
)
EXPECTED_THRESHOLD_POLICY_GIT_BLOB_ID = (
    "1f97932227128978b6a046734aa68c60e188d5a9"
)
EXPECTED_THRESHOLD_POLICY_SOURCE_COMMIT = (
    "36021201ab24dd5c1cf5525d33fcd0d11577e795"
)
EXPECTED_THRESHOLD_DENOMINATOR_BINDING_SHA256 = (
    "310308a7377423f5bec4615de58244da2c4b305014dd835838313d29287df30e"
)
REPEATED_SKELETON_DETECTOR_ID = "repeated_skeleton_concentration"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_jsonl(path: Path):
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"invalid facts JSONL at line {line_number}: {path}"
                    ) from exc
    return rows


def _canonical_jsonl_bytes(rows):
    return "".join(
        json.dumps(
            row,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
        for row in rows
    ).encode("utf-8")


def _member_set_sha256(members):
    return hashlib.sha256(
        "".join(f"{member}\n" for member in sorted(members)).encode("utf-8")
    ).hexdigest()


def _canonical_profile_skeleton(profile):
    return json.dumps(
        sorted(profile),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def build_food_semantic_skeleton_group_report(
    inventory,
    *,
    threshold_policy_path,
    threshold_denominator_binding_path,
):
    """Run the bound Naturalization skeleton detector in no-render mode."""
    policy_path = Path(threshold_policy_path).resolve()
    policy_sha256 = _sha256_file(policy_path)
    if policy_sha256 != EXPECTED_THRESHOLD_POLICY_SHA256:
        raise ValueError("canonical Naturalization threshold policy drift")
    with policy_path.open("r", encoding="utf-8") as handle:
        policy = json.load(handle)
    if REPEATED_SKELETON_DETECTOR_ID not in policy.get(
        "raw_detector_ids", []
    ):
        raise ValueError("canonical repeated-skeleton detector id is missing")
    ratio = policy["detectors"][REPEATED_SKELETON_DETECTOR_ID]["ratio"]
    numerator = int(ratio["numerator"])
    denominator = int(ratio["denominator"])
    if numerator != 1 or denominator != 20:
        raise ValueError("canonical repeated-skeleton ratio changed")
    denominator_binding_path = Path(
        threshold_denominator_binding_path
    ).resolve()
    if (
        _sha256_file(denominator_binding_path)
        != EXPECTED_THRESHOLD_DENOMINATOR_BINDING_SHA256
    ):
        raise ValueError("canonical Naturalization denominator binding drift")
    with denominator_binding_path.open("r", encoding="utf-8") as handle:
        denominator_binding = json.load(handle)
    canonical_candidate_denominator = int(
        denominator_binding["candidate_denominator"]
    )
    preserved_threshold_value = int(
        denominator_binding["maximum_repetition_count"]
    )
    profiles_by_item = {}
    for row in inventory:
        profiles_by_item.setdefault(row["item_id"], []).append(
            (row["fact_axis"], row["fact_value"])
        )
    group_members = {}
    for item_id, profile in profiles_by_item.items():
        skeleton = _canonical_profile_skeleton(profile)
        group_members.setdefault(skeleton, []).append(item_id)
    groups = [
        {
            "skeleton_sha256": hashlib.sha256(
                skeleton.encode("utf-8")
            ).hexdigest(),
            "member_count": len(members),
            "member_set_sha256": _member_set_sha256(members),
        }
        for skeleton, members in group_members.items()
    ]
    groups.sort(key=lambda row: (-row["member_count"], row["skeleton_sha256"]))
    evaluated_food_item_count = len(profiles_by_item)
    bound_threshold_value = (
        canonical_candidate_denominator * numerator // denominator
    )
    if bound_threshold_value != preserved_threshold_value:
        raise ValueError("canonical Naturalization threshold value drift")
    maximum_same_skeleton_group = groups[0]["member_count"] if groups else 0
    detector_path = Path(__file__).resolve()
    threshold_binding = {
        "schema_version": "food-semantic-threshold-authority-binding-v1",
        "status": "PASS",
        "policy_path": str(policy_path),
        "policy_sha256": policy_sha256,
        "policy_source_path": (
            "Iris/build/description/v2/data/korean_prose_naturalization/"
            "korean_prose_policy.json"
        ),
        "policy_source_commit": EXPECTED_THRESHOLD_POLICY_SOURCE_COMMIT,
        "policy_source_git_blob_id": EXPECTED_THRESHOLD_POLICY_GIT_BLOB_ID,
        "policy_source_sha256": EXPECTED_THRESHOLD_POLICY_SHA256,
        "policy_ratio": {
            "numerator": numerator,
            "denominator": denominator,
        },
        "policy_resolved_candidate_count": canonical_candidate_denominator,
        "policy_resolved_threshold_value": bound_threshold_value,
        "denominator_binding_path": str(denominator_binding_path),
        "denominator_binding_sha256": _sha256_file(
            denominator_binding_path
        ),
        "detector_id": REPEATED_SKELETON_DETECTOR_ID,
        "detector_path": str(detector_path),
        "detector_sha256": _sha256_file(detector_path),
        "detector_symbol": "build_food_semantic_skeleton_group_report",
        "detector_value_source": "bound_policy",
        "detector_resolved_ratio": {
            "numerator": numerator,
            "denominator": denominator,
        },
        "detector_resolved_threshold_value": bound_threshold_value,
        "bound_threshold_value": bound_threshold_value,
        "threshold_source_identity_bound": True,
        "threshold_source_value_unchanged": True,
        "threshold_policy_detector_identity_match": True,
        "threshold_authority_mismatch_classification": "none",
        "threshold_authority_unclassified_mismatch_count": 0,
        "acceptance_threshold_owned_here": False,
        "compatibility_raw_detector_bound_only": True,
    }
    skeleton_report = {
        "schema_version": "food-semantic-skeleton-group-report-v1",
        "status": (
            "PASS"
            if maximum_same_skeleton_group <= bound_threshold_value
            else "FAIL"
        ),
        "producer": "naturalization_actual_phase2_consumer",
        "detector_id": REPEATED_SKELETON_DETECTOR_ID,
        "detector_symbol": "build_food_semantic_skeleton_group_report",
        "grouping_input": "actual_food_semantic_proposition_inventory",
        "canonical_candidate_denominator": canonical_candidate_denominator,
        "evaluated_food_item_count": evaluated_food_item_count,
        "evaluation_scope": (
            "actual food-semantic projection of the preserved oversized "
            "food skeleton condition"
        ),
        "skeleton_group_count": len(groups),
        "groups": groups,
        "maximum_same_skeleton_group": maximum_same_skeleton_group,
        "bound_threshold_value": bound_threshold_value,
        "maximum_same_skeleton_group_within_bound": (
            maximum_same_skeleton_group <= bound_threshold_value
        ),
        "render_write_count": 0,
    }
    return {
        "threshold_authority_binding": threshold_binding,
        "skeleton_group_report": skeleton_report,
    }


# BEGIN DVF FOOD SEMANTIC CANDIDATE PATCH (D16 adoption required)
def build_food_semantic_proposition_inventory(
    facts_rows,
    *,
    schema_sha256,
    proposition_license_sha256,
):
    """Project approved structured assertions without inventing propositions."""
    inventory = []
    for facts in facts_rows:
        for assertion in facts.get("food_semantic_assertions", []):
            if assertion.get("authority_state") not in {
                "approved",
                "owner_approved",
            }:
                continue
            inventory.append(
                {
                    "item_id": facts["item_id"],
                    "proposition_id": assertion["proposition_id"],
                    "fact_axis": assertion["fact_axis"],
                    "fact_value": assertion["fact_value"],
                    "authority_class": assertion["authority_class"],
                    "source_or_approval_lineage_id": assertion["lineage_id"],
                    "schema_sha256": schema_sha256,
                    "proposition_license_sha256": proposition_license_sha256,
                }
            )
    return sorted(
        inventory,
        key=lambda row: (
            row["item_id"],
            row["fact_axis"],
            row["fact_value"],
            row["proposition_id"],
        ),
    )


def consume_food_semantic_inputs_no_render(
    *,
    facts_path,
    manifest_path,
    schema_path,
    proposition_license_path,
    explicit_non_current_input_override,
    repository_root=None,
    facts_sha256=None,
    manifest_sha256=None,
    schema_sha256=None,
    proposition_license_sha256=None,
    threshold_policy_path=None,
    threshold_denominator_binding_path=None,
):
    """Open all Phase 2 inputs and return their computed no-render identities."""
    if explicit_non_current_input_override is not True:
        raise ValueError("Branch B requires an explicit non-current input override")
    paths = {
        "facts": Path(facts_path).resolve(),
        "manifest": Path(manifest_path).resolve(),
        "schema": Path(schema_path).resolve(),
        "proposition_license": Path(proposition_license_path).resolve(),
    }
    computed = {
        f"{name}_sha256": _sha256_file(path) for name, path in paths.items()
    }
    supplied = {
        "facts_sha256": facts_sha256,
        "manifest_sha256": manifest_sha256,
        "schema_sha256": schema_sha256,
        "proposition_license_sha256": proposition_license_sha256,
    }
    supplied_mismatches = [
        field
        for field, value in supplied.items()
        if value is not None and value != computed[field]
    ]
    if supplied_mismatches:
        raise ValueError(
            "caller-supplied input identity mismatch: "
            + ",".join(sorted(supplied_mismatches))
        )
    facts_rows = _load_jsonl(paths["facts"])
    with paths["manifest"].open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    with paths["schema"].open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    with paths["proposition_license"].open("r", encoding="utf-8") as handle:
        proposition_license = json.load(handle)
    manifest_declared_facts_sha256 = manifest.get("facts", {}).get("sha256")
    if manifest_declared_facts_sha256 != computed["facts_sha256"]:
        raise ValueError("manifest facts SHA-256 does not match opened facts")
    manifest_declared_facts_path = manifest.get("facts", {}).get("path")
    if not manifest_declared_facts_path:
        raise ValueError("manifest lacks the selected facts path")
    declared_path = Path(manifest_declared_facts_path)
    if not declared_path.is_absolute():
        declared_path = Path(repository_root or Path.cwd()) / declared_path
    manifest_facts_path_match = (
        declared_path.resolve() == paths["facts"]
    )
    if not manifest_facts_path_match:
        raise ValueError("manifest facts path does not match opened facts")
    food_authority = manifest.get("food_semantic_authority", {})
    for field, expected_value in (
        ("schema_sha256", computed["schema_sha256"]),
        (
            "proposition_license_sha256",
            computed["proposition_license_sha256"],
        ),
    ):
        if food_authority.get(field) != expected_value:
            raise ValueError(f"manifest food authority {field} mismatch")
    inventory = build_food_semantic_proposition_inventory(
        facts_rows,
        schema_sha256=computed["schema_sha256"],
        proposition_license_sha256=computed[
            "proposition_license_sha256"
        ],
    )
    inventory_bytes = _canonical_jsonl_bytes(inventory)
    allowed_values = {
        axis["axis"]: {value["value"] for value in axis["values"]}
        for axis in schema["axes"]
    }
    required_axes = sorted(
        axis["axis"]
        for axis in schema["axes"]
        if axis["cardinality"] == "one_or_more"
    )
    license_index = {
        (row["fact_axis"], row["fact_value"]): row
        for row in proposition_license["licenses"]
    }
    invalid_schema_count = 0
    invalid_license_count = 0
    proposition_ids = []
    axes_by_item = {}
    profiles_by_item = {}
    for row in inventory:
        proposition_ids.append(row["proposition_id"])
        axes_by_item.setdefault(row["item_id"], set()).add(row["fact_axis"])
        profiles_by_item.setdefault(row["item_id"], []).append(
            (row["fact_axis"], row["fact_value"])
        )
        if row["fact_value"] not in allowed_values.get(row["fact_axis"], set()):
            invalid_schema_count += 1
        license_row = license_index.get((row["fact_axis"], row["fact_value"]))
        if license_row is None or (
            row["authority_class"] == "automatic"
            and license_row.get("automatic_eligible") is not True
        ) or (
            row["authority_class"] == "curated"
            and license_row.get("curated_allowed") is not True
        ):
            invalid_license_count += 1
    projected_members = set(axes_by_item)
    required_axis_missing = {
        item_id: sorted(set(required_axes) - axes)
        for item_id, axes in sorted(axes_by_item.items())
        if set(required_axes) - axes
    }
    meaningful_profiles = {
        tuple(sorted(profile)) for profile in profiles_by_item.values()
    }
    if threshold_policy_path is None:
        raise ValueError("canonical threshold policy path is required")
    if threshold_denominator_binding_path is None:
        raise ValueError("canonical threshold denominator binding path is required")
    skeleton_evaluation = build_food_semantic_skeleton_group_report(
        inventory,
        threshold_policy_path=threshold_policy_path,
        threshold_denominator_binding_path=(
            threshold_denominator_binding_path
        ),
    )
    receipt = {
        "producer": "naturalization_actual_phase2_consumer",
        "facts_path": str(paths["facts"]),
        "facts_sha256": computed["facts_sha256"],
        "manifest_path": str(paths["manifest"]),
        "manifest_sha256": computed["manifest_sha256"],
        "schema_path": str(paths["schema"]),
        "schema_sha256": computed["schema_sha256"],
        "proposition_license_path": str(paths["proposition_license"]),
        "proposition_license_sha256": computed[
            "proposition_license_sha256"
        ],
        "manifest_declared_facts_sha256": manifest_declared_facts_sha256,
        "manifest_declared_facts_path": manifest_declared_facts_path,
        "manifest_facts_sha256_match": True,
        "manifest_facts_path_match": True,
        "opened_input_count": 4,
        "phase2_primary_opened_input_count": 4,
        "threshold_authority_opened_input_count": 2,
        "total_opened_input_count": 6,
        "facts_row_count": len(facts_rows),
        "food_semantic_proposition_count": len(inventory),
        "food_semantic_proposition_inventory_sha256": hashlib.sha256(
            inventory_bytes
        ).hexdigest(),
        "food_semantic_item_count": len(projected_members),
        "food_semantic_item_set_sha256": _member_set_sha256(
            projected_members
        ),
        "required_fact_axes": required_axes,
        "required_axis_missing_item_count": len(required_axis_missing),
        "required_axis_missing_by_item": required_axis_missing,
        "duplicate_proposition_id_count": (
            len(proposition_ids) - len(set(proposition_ids))
        ),
        "invalid_schema_proposition_count": invalid_schema_count,
        "invalid_license_proposition_count": invalid_license_count,
        "meaningful_partition_count": len(meaningful_profiles),
        "maximum_same_skeleton_group": skeleton_evaluation[
            "skeleton_group_report"
        ]["maximum_same_skeleton_group"],
        "bound_threshold_value": skeleton_evaluation[
            "threshold_authority_binding"
        ]["bound_threshold_value"],
        "manifest_declared_food_semantic_item_count": food_authority.get(
            "target_member_count"
        ),
        "manifest_declared_food_semantic_item_set_sha256": food_authority.get(
            "target_member_set_sha256"
        ),
        "manifest_declared_required_fact_axes": food_authority.get(
            "required_fact_axes"
        ),
        "manifest_declared_food_semantic_proposition_count": (
            food_authority.get("proposition_count")
        ),
        "manifest_declared_food_semantic_proposition_inventory_sha256": (
            food_authority.get("proposition_inventory_sha256")
        ),
        "explicit_non_current_input_override": True,
        "current_facts_read_count": 0,
        "render_write_count": 0,
    }
    return {
        "receipt": receipt,
        "inventory": inventory,
        **skeleton_evaluation,
    }


def build_food_semantic_no_render_receipt(**kwargs):
    """Compatibility wrapper returning the actual consumer receipt only."""
    return consume_food_semantic_inputs_no_render(**kwargs)["receipt"]
# END DVF FOOD SEMANTIC CANDIDATE PATCH
