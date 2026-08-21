from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
IRIS_ROOT = REPOSITORY_ROOT / "Iris"
PLAN_PATH = REPOSITORY_ROOT / "docs" / "새 폴더" / "iris_layer4_adaptive_interaction_density_presentation_plan.md"
WALKTHROUGH_PATH = REPOSITORY_ROOT / "docs" / "iris_layer4_gate3_source_migration_unblock_walkthrough.md"
OWNER_PACKET_PATH = (
    REPOSITORY_ROOT
    / "docs"
    / "iris_layer4_adaptive_interaction_density_presentation_owner_decision_packet.md"
)
OWNER_SEAL_PATH = (
    IRIS_ROOT
    / "build"
    / "description"
    / "v2"
    / "owner_inputs"
    / "iris_layer4_adaptive_interaction_density_presentation"
    / "owner_policy_seal.json"
)
STAGING_ROOT = (
    IRIS_ROOT
    / "build"
    / "description"
    / "v2"
    / "staging"
    / "iris_layer4_adaptive_interaction_density_presentation"
)
REPORT_PATH = STAGING_ROOT / "contract_report.json"
PATH_SELECTION_PATH = STAGING_ROOT / "path_selection.json"
NO_MUTATION_PATH = STAGING_ROOT / "preseal_no_current_mutation.json"
STABLE_ID_CANDIDATE_PATH = STAGING_ROOT / "stable_id_plumbing_candidate.json"
SELF_GENERATED_REPORT_PATHS = {
    repository_path
    for repository_path in (
        "Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/contract_report.json",
        "Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/path_selection.json",
        "Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/preseal_no_current_mutation.json",
        "Iris/build/description/v2/staging/iris_layer4_adaptive_interaction_density_presentation/stable_id_plumbing_candidate.json",
    )
}
DECLARED_IMPLEMENTATION_SUBJECT_PATHS = {
    "Iris/build/recipe_evidence_pipeline.py",
    "Iris/build/description/v2/tools/build/validate_interaction_presentation_contract.py",
    "Iris/build/tests/test_recipe_evidence.py",
    "Iris/evidence/rightclick/pipeline.py",
    "Iris/media/lua/client/Iris/Data/IrisCapabilities.lua",
    "Iris/output/capability_by_fulltype.json",
    "Iris/output/recipe_evidence_decisions.v2.4.json",
    "Iris/output/recipe_nav_registry.v2.4.json",
    "Iris/output/usecases_by_fulltype.v2.4.json",
    "Iris/test/test_interaction_presentation_contract.py",
    "Iris/test/test_rightclick_pipeline.py",
    "docs/iris_layer4_adaptive_interaction_density_presentation_decision_packet.md",
    "docs/iris_layer4_adaptive_interaction_density_presentation_closeout.md",
    "docs/iris_layer4_gate3_source_migration_unblock_walkthrough.md",
    "docs/iris_layer4_adaptive_interaction_density_presentation_owner_decision_packet.md",
    "Iris/build/description/v2/owner_inputs/iris_layer4_adaptive_interaction_density_presentation/owner_policy_seal.json",
    "docs/\uc0c8 \ud3f4\ub354/iris_layer4_adaptive_interaction_density_presentation_plan.md",
    *SELF_GENERATED_REPORT_PATHS,
}

UPSTREAM_PATH = IRIS_ROOT / "build" / "description" / "v2" / "data" / "upstream_usecases_by_fulltype.json"
QG_USECASES_PATH = IRIS_ROOT / "output" / "usecases_by_fulltype.v2.4.json"
DESCRIPTIONS_PATH = IRIS_ROOT / "output" / "descriptions_by_fulltype.v2.4.json"
CAPABILITIES_PATH = IRIS_ROOT / "output" / "capability_by_fulltype.json"
CAPABILITIES_LUA_PATH = IRIS_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "IrisCapabilities.lua"
RIGHTCLICK_SOURCE_PATH = IRIS_ROOT / "input" / "rightclick_source_index.json"
RECIPE_INDEX_PATH = IRIS_ROOT / "output" / "recipe_index.v2.4.json"
RECIPE_DECISIONS_PATH = IRIS_ROOT / "output" / "recipe_evidence_decisions.v2.4.json"
RECIPE_NAV_PATH = IRIS_ROOT / "output" / "recipe_nav_registry.v2.4.json"
RUNTIME_DATA_ROOT = IRIS_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "UseCaseDescriptions"
LINE_COUNT_PATH = RUNTIME_DATA_ROOT / "LineCountIndex.lua"
CHUNK_INDEX_PATH = RUNTIME_DATA_ROOT / "ChunkIndex.lua"

SUPPORTED_SURFACES = {"recipe_ui", "context_menu"}

# Audited structural edges. These are not display-label mappings. Each legacy
# capability may map only to the listed QG identity + right-click rule lineage.
CAPABILITY_CROSSWALK: dict[str, frozenset[tuple[str, tuple[str, ...]]]] = {
    "can_add_generator_fuel": frozenset(
        {("uc.action.fuel", ("rule_worldobject_predicatepetrol",))}
    ),
    "can_attach_weapon_mod": frozenset(
        {("uc.action.attach_weapon_part", ("rule_inventorypane_weaponpart",))}
    ),
    "can_extinguish_fire": frozenset(
        {("uc.action.extinguish_fire", ("rule_firefighting_isextinguisher",))}
    ),
    "can_open_canned_food": frozenset(
        {("uc.action.open_can", ("rule_cm_surface_recipe_open_canned",))}
    ),
    "can_remove_embedded_object": frozenset(
        {
            (
                "uc.action.foreign_body_removal",
                ("rule_healthpanel_hremovebullet", "rule_healthpanel_hremoveglass"),
            )
        }
    ),
    "can_scrap_moveables": frozenset(
        {
            ("uc.action.construction", ("rule_tooldef_hammer",)),
            ("uc.action.metal_cutting", ("rule_tooldef_blowtorch",)),
            ("uc.action.screw_disassembly", ("rule_tooldef_screwdriver",)),
            ("uc.action.wood_cutting", ("rule_tooldef_saw",)),
        }
    ),
    "can_stitch_wound": frozenset(
        {("uc.action.wound_suturing", ("rule_healthpanel_hstitch",))}
    ),
}

PROTECTED_EXACT_PATHS = {
    "docs/ARCHITECTURE.md",
    "docs/DECISIONS.md",
    "docs/ROADMAP.md",
    "Iris/media/lua/client/Iris/API/UseCases.lua",
    "Iris/media/lua/client/Iris/Data/IrisRecipeIndexData.lua",
    "Iris/media/lua/client/Iris/Data/IrisTranslationData.lua",
    "Iris/media/lua/client/Iris/Data/IrisUseCaseLabelMap.lua",
    "Iris/media/lua/client/Iris/UI/Browser/IrisBrowser.lua",
    "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua",
    "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionCollector.lua",
    "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionPolicy.lua",
    "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua",
    "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua",
    "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionState.lua",
    "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserListController.lua",
    "Iris/media/lua/client/Iris/UI/Browser/IrisRequirementPolicy.lua",
    "Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua",
    "Iris/media/lua/client/Iris/UI/Wiki/IrisWikiPanel.lua",
    "Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua",
    "Iris/media/lua/shared/translate/en/Iris_en.txt",
    "Iris/media/lua/shared/translate/ko/Iris_ko.txt",
    "Iris/_dev/media/lua/client/Iris/Dev/BrowserInteractionDensityAcceptanceHarness.lua",
}
PROTECTED_PREFIXES = ("Iris/media/lua/client/Iris/Data/UseCaseDescriptions/",)

PLANNING_RECIPE_ONLY = {
    ("Base.HandTorch", "remove_battery"),
    ("Base.Rubberducky2", "remove_battery"),
    ("Base.Torch", "remove_battery"),
}

APPROVED_EXECUTION_BASE_COMMIT = "bfdee1c29f82181e15b5924c750e6d44acf41fcc"
APPROVED_EXECUTION_BASE_TREE = "aee455bd36881e1167d454d470300a4f67fa3cf4"
APPROVED_PLAN_SHA256 = "f38d8bf976ec3b8b3d219e2c5e73090a0566a6113b2d658366f26dbdea116580"
APPROVED_WALKTHROUGH_SHA256 = "a96a3a6e453d8df0f7549450020dd33b58f2f70cb748038c2bee369f88b376af"
APPROVED_OWNER_MESSAGE_SHA256 = "66a65dabef10bf9839e9d94871e092c33bf4a900fea88d0db0f905997e8ff9ce"
APPROVED_OWNER_SEAL_SHA256 = "2ed2fda9de08ee71694e7c793ec6db7ba811755263dc0a5b0f7b1d140a2345a5"
APPROVED_QG_ONLY = {
    ("Base.BallPeenHammer", "uc.action.construction"),
    ("Base.GardenSaw", "uc.action.wood_cutting"),
    ("Base.HammerStone", "uc.action.construction"),
}
EXISTING_RENDERER_PATH = "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua"
EXISTING_COLLECTOR_PATH = "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionCollector.lua"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob_sha256(ref: str, repository_path: str) -> str:
    content = subprocess.check_output(
        ["git", "show", f"{ref}:{repository_path}"], cwd=REPOSITORY_ROOT
    )
    return hashlib.sha256(content).hexdigest()


def validate_owner_policy_seal(
    *, capability_report: dict[str, Any], recipe_report: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    seal = load_json(OWNER_SEAL_PATH)
    resolved_tree = subprocess.run(
        ["git", "rev-parse", f"{APPROVED_EXECUTION_BASE_COMMIT}^{{tree}}"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout.strip()
    qg_only = {
        (entry.get("fulltype"), entry.get("use_case_id"))
        for entry in seal.get("qg_only_publication", {}).get("relations", [])
    }
    current_qg_only = {
        (entry.get("fulltype"), entry.get("use_case_id"))
        for entry in capability_report.get("qg_only", [])
    }
    checks = {
        "owner_seal_identity": sha256_path(OWNER_SEAL_PATH) == APPROVED_OWNER_SEAL_SHA256,
        "owner_seal_schema_status": seal.get("schema_version") == "iris-layer4-owner-policy-seal-v2"
        and seal.get("status") == "approved",
        "owner_seal_approval_source": seal.get("approval_source", {}).get("sha256")
        == APPROVED_OWNER_MESSAGE_SHA256,
        "owner_seal_execution_base": seal.get("execution_base")
        == {"commit": APPROVED_EXECUTION_BASE_COMMIT, "tree": APPROVED_EXECUTION_BASE_TREE}
        and resolved_tree == APPROVED_EXECUTION_BASE_TREE,
        "owner_seal_plan": seal.get("plan", {}).get("sha256") == sha256_path(PLAN_PATH)
        == APPROVED_PLAN_SHA256,
        "owner_seal_walkthrough": seal.get("gate3_walkthrough", {}).get("sha256")
        == sha256_path(WALKTHROUGH_PATH)
        == APPROVED_WALKTHROUGH_SHA256,
        "owner_seal_packet": seal.get("decision_packet", {}).get("sha256")
        == sha256_path(OWNER_PACKET_PATH),
        "owner_seal_gate3": capability_report.get("capability_only_count") == 0
        and recipe_report.get("recipe_only_count") == 0,
        "owner_seal_qg_only": qg_only == current_qg_only == APPROVED_QG_ONLY,
        "owner_seal_rat08": seal.get("ratifications", {}).get("L4-RAT-08", {}).get("status")
        == "not_applicable",
        "historical_owner_seal_consumed": seal.get("historical_artifacts", {}).get(
            "historical_staging_seal_consumed"
        )
        is False,
    }
    errors = sorted(name for name, passed in checks.items() if not passed)

    return (
        {
            "status": "approved" if not errors else "invalid",
            "path": repository_relative(OWNER_SEAL_PATH),
            "sha256": sha256_path(OWNER_SEAL_PATH),
            "decision_packet_path": repository_relative(OWNER_PACKET_PATH),
            "decision_packet_sha256": sha256_path(OWNER_PACKET_PATH),
            "execution_base_commit": APPROVED_EXECUTION_BASE_COMMIT,
            "execution_base_tree": APPROVED_EXECUTION_BASE_TREE,
            "ratifications": seal.get("ratifications", {}),
            "qg_only_publication": [
                {"fulltype": fulltype, "use_case_id": use_case_id}
                for fulltype, use_case_id in sorted(qg_only)
            ],
            "historical_staging_seal_consumed": False,
            "errors": sorted(errors),
        },
        errors,
    )


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def repository_relative(path: Path) -> str:
    return path.resolve().relative_to(REPOSITORY_ROOT.resolve()).as_posix()


def normalize_fulltype(value: str) -> str:
    value = value.strip()
    return value if "." in value else f"Base.{value}"


def positive_rows(entry: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in entry.get("use_cases", []) if row.get("line_kind") != "exclusion"]


def build_current_qg_fulltypes(
    upstream_fulltypes: dict[str, Any], runtime_rows: dict[str, list[tuple[str, str, str]]]
) -> dict[str, Any]:
    """Bind structured upstream rows to the installed generated row order/denominator."""
    result: dict[str, Any] = {}
    for fulltype in sorted(set(upstream_fulltypes) | set(runtime_rows)):
        upstream_rows = upstream_fulltypes.get(fulltype, {}).get("use_cases", [])
        upstream_by_identity = {
            str(row.get("use_case_id") or ""): row
            for row in upstream_rows
            if row.get("line_kind") != "exclusion"
        }
        ordered_positive = [
            upstream_by_identity.get(
                identity,
                {"use_case_id": identity, "surface": surface, "line_kind": line_kind},
            )
            for identity, surface, line_kind in runtime_rows.get(fulltype, [])
        ]
        exclusions = [row for row in upstream_rows if row.get("line_kind") == "exclusion"]
        result[fulltype] = {"use_cases": [*ordered_positive, *exclusions]}
    return result


def evidence_rule_ids(row: dict[str, Any], source_type: str) -> tuple[str, ...]:
    return tuple(
        sorted(
            str(source["rule_id"])
            for source in row.get("evidence_sources", [])
            if source.get("source_type") == source_type and source.get("rule_id")
        )
    )


def qg_context_tuple(fulltype: str, row: dict[str, Any]) -> tuple[str, str, tuple[str, ...]]:
    return (fulltype, str(row.get("use_case_id") or ""), evidence_rule_ids(row, "rightclick"))


def tuple_record(values: tuple[Any, ...], names: tuple[str, ...]) -> dict[str, Any]:
    return {name: value for name, value in zip(names, values, strict=True)}


def build_density_and_schema_report(
    fulltypes: dict[str, Any], *, small_max: int, dense_min: int
) -> tuple[dict[str, Any], dict[str, list[tuple[str, dict[str, Any]]]]]:
    if small_max < 2 or dense_min != small_max + 1:
        raise ValueError("density thresholds must satisfy small_max >= 2 and dense_min == small_max + 1")

    buckets = Counter()
    exact_small: list[str] = []
    exact_dense: list[str] = []
    max_count = -1
    max_items: list[str] = []
    source_counts = Counter()
    both_source_items = 0
    duplicate_identities: list[dict[str, Any]] = []
    missing_identities: list[dict[str, Any]] = []
    unknown_surfaces: list[dict[str, Any]] = []
    both_surfaces: list[dict[str, Any]] = []
    source_surface_mismatches: list[dict[str, Any]] = []
    rows_by_surface: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)

    for fulltype in sorted(fulltypes):
        all_rows = fulltypes[fulltype].get("use_cases", [])
        rows = positive_rows(fulltypes[fulltype])
        count = len(rows)
        if count == 0:
            buckets["0"] += 1
        elif count == 1:
            buckets["1"] += 1
        elif count <= small_max:
            buckets[f"2-{small_max}"] += 1
        else:
            buckets[f"{dense_min}+"] += 1
        if count == small_max:
            exact_small.append(fulltype)
        if count == dense_min:
            exact_dense.append(fulltype)
        if count > max_count:
            max_count = count
            max_items = [fulltype]
        elif count == max_count:
            max_items.append(fulltype)

        identities = [str(row.get("use_case_id") or "") for row in rows]
        duplicates = sorted(identity for identity, total in Counter(identities).items() if identity and total > 1)
        if duplicates:
            duplicate_identities.append({"fulltype": fulltype, "identities": duplicates})

        positive_surfaces = set()
        for ordinal, row in enumerate(all_rows):
            identity = str(row.get("use_case_id") or "")
            surface = str(row.get("surface") or "")
            if not identity:
                missing_identities.append({"fulltype": fulltype, "ordinal": ordinal})
            if surface == "both":
                both_surfaces.append({"fulltype": fulltype, "identity": identity, "ordinal": ordinal})
            elif surface not in SUPPORTED_SURFACES:
                unknown_surfaces.append(
                    {"fulltype": fulltype, "identity": identity, "ordinal": ordinal, "surface": surface}
                )

            source_types = {
                str(source.get("source_type") or "") for source in row.get("evidence_sources", [])
            }
            expected_source = "recipe_evidence" if surface == "recipe_ui" else "rightclick"
            if surface in SUPPORTED_SURFACES and expected_source not in source_types:
                source_surface_mismatches.append(
                    {
                        "fulltype": fulltype,
                        "identity": identity,
                        "surface": surface,
                        "source_types": sorted(source_types),
                    }
                )

            if row.get("line_kind") != "exclusion" and surface in SUPPORTED_SURFACES:
                rows_by_surface[surface].append((fulltype, row))
                source_counts[surface] += 1
                positive_surfaces.add(surface)
        if positive_surfaces == SUPPORTED_SURFACES:
            both_source_items += 1

    return (
        {
            "threshold": {"small_max": small_max, "dense_min": dense_min},
            "bucket_counts": dict(sorted(buckets.items())),
            "exact_small_boundary_fulltypes": exact_small,
            "exact_dense_boundary_fulltypes": exact_dense,
            "max_positive_count": max_count,
            "max_positive_fulltypes": max_items,
            "positive_line_count": sum(source_counts.values()),
            "recipe_positive_line_count": source_counts["recipe_ui"],
            "rightclick_positive_line_count": source_counts["context_menu"],
            "both_source_item_count": both_source_items,
            "duplicate_identity_count": len(duplicate_identities),
            "duplicate_identities": duplicate_identities,
            "missing_identity_count": len(missing_identities),
            "missing_identities": missing_identities,
            "unknown_surface_count": len(unknown_surfaces),
            "unknown_surfaces": unknown_surfaces,
            "surface_both_count": len(both_surfaces),
            "surface_both": both_surfaces,
            "source_surface_mismatch_count": len(source_surface_mismatches),
            "source_surface_mismatches": source_surface_mismatches,
        },
        rows_by_surface,
    )


def build_capability_crosswalk_report(
    capabilities: dict[str, list[str]], context_rows: list[tuple[str, dict[str, Any]]]
) -> dict[str, Any]:
    raw_legacy = sorted((fulltype, capability) for fulltype, values in capabilities.items() for capability in values)
    raw_qg = sorted(qg_context_tuple(fulltype, row) for fulltype, row in context_rows)
    qg_by_fulltype: dict[str, list[tuple[str, str, tuple[str, ...]]]] = defaultdict(list)
    for qg_tuple in raw_qg:
        qg_by_fulltype[qg_tuple[0]].append(qg_tuple)

    intersections: list[dict[str, Any]] = []
    capability_only: list[dict[str, Any]] = []
    consumed_qg: set[tuple[str, str, tuple[str, ...]]] = set()
    unknown_capabilities: list[dict[str, str]] = []

    for fulltype, capability in raw_legacy:
        allowed = CAPABILITY_CROSSWALK.get(capability)
        if allowed is None:
            unknown_capabilities.append({"fulltype": fulltype, "capability_id": capability})
            capability_only.append(
                {"fulltype": fulltype, "capability_id": capability, "reason": "unknown_capability_family"}
            )
            continue
        matches = [
            qg_tuple
            for qg_tuple in qg_by_fulltype.get(fulltype, [])
            if (qg_tuple[1], qg_tuple[2]) in allowed
        ]
        if not matches:
            capability_only.append(
                {
                    "fulltype": fulltype,
                    "capability_id": capability,
                    "reason": "no_structured_qg_context_tuple",
                }
            )
            continue
        for qg_tuple in matches:
            consumed_qg.add(qg_tuple)
            intersections.append(
                {
                    "legacy": {"fulltype": fulltype, "capability_id": capability},
                    "qg": tuple_record(
                        qg_tuple, ("fulltype", "use_case_id", "rightclick_rule_ids")
                    ),
                }
            )

    qg_only = [
        tuple_record(qg_tuple, ("fulltype", "use_case_id", "rightclick_rule_ids"))
        for qg_tuple in raw_qg
        if qg_tuple not in consumed_qg
    ]
    return {
        "audited_crosswalk": {
            capability: [
                {"use_case_id": use_case_id, "rightclick_rule_ids": list(rule_ids)}
                for use_case_id, rule_ids in sorted(edges)
            ]
            for capability, edges in sorted(CAPABILITY_CROSSWALK.items())
        },
        "legacy_tuple_count": len(raw_legacy),
        "qg_context_tuple_count": len(raw_qg),
        "mapped_intersection_count": len(intersections),
        "capability_only_count": len(capability_only),
        "qg_only_count": len(qg_only),
        "raw_legacy_tuples": [
            {"fulltype": fulltype, "capability_id": capability} for fulltype, capability in raw_legacy
        ],
        "raw_qg_tuples": [
            tuple_record(qg_tuple, ("fulltype", "use_case_id", "rightclick_rule_ids"))
            for qg_tuple in raw_qg
        ],
        "mapped_intersection": intersections,
        "capability_only": capability_only,
        "qg_only": qg_only,
        "unknown_capability_count": len(unknown_capabilities),
        "unknown_capabilities": unknown_capabilities,
        "count_equality_is_not_identity_parity": len(raw_legacy) == len(raw_qg),
    }


def build_legacy_recipe_tuples(recipe_index: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for recipe_key, recipe in sorted(recipe_index.get("recipes", {}).items()):
        recipe_id = str(recipe.get("recipe_id") or "")
        tuple_recipe_id = recipe_id or str(recipe_key)
        for role, field in (("input", "inputs"), ("keep", "keeps")):
            for raw_fulltype in recipe.get(field, []) or []:
                fulltype = normalize_fulltype(str(raw_fulltype))
                key = (fulltype, tuple_recipe_id)
                record = result.setdefault(
                    key,
                    {
                        "fulltype": fulltype,
                        "recipe_id": tuple_recipe_id,
                        "producer_recipe_id_present": bool(recipe_id),
                        "roles": [],
                        "recipe_index_key": str(recipe_key),
                    },
                )
                if role not in record["roles"]:
                    record["roles"].append(role)
    for record in result.values():
        record["roles"].sort()
    return result


def build_qg_recipe_tuples(
    recipe_rows: list[tuple[str, dict[str, Any]]],
    recipe_decisions: dict[str, Any],
    recipe_nav: dict[str, Any],
) -> tuple[dict[tuple[str, str], dict[str, Any]], list[dict[str, Any]]]:
    rules = recipe_decisions.get("rules", {})
    nav_entries = recipe_nav.get("entries", {})
    complete: dict[tuple[str, str], dict[str, Any]] = {}
    incomplete: list[dict[str, Any]] = []
    for fulltype, row in recipe_rows:
        use_case_id = str(row.get("use_case_id") or "")
        rule_ids = evidence_rule_ids(row, "recipe_evidence")
        nav_entry = nav_entries.get(use_case_id)
        decision_recipe_ids = {
            str(rules[rule_id].get("recipe_id") or "") for rule_id in rule_ids if rule_id in rules
        }
        decision_recipe_ids.discard("")
        # The current registry's historical field name is recipe_id, but its
        # structured value is the uc.recipe.* identity. The legacy recipe_id
        # remains owned by recipe_evidence_decisions rule lineage.
        nav_registry_identity = (
            str(nav_entry.get("recipe_id") or "") if isinstance(nav_entry, dict) else ""
        )
        structured_complete = (
            bool(use_case_id)
            and len(rule_ids) == 1
            and len(decision_recipe_ids) == 1
            and bool(nav_registry_identity)
            and nav_registry_identity == use_case_id
        )
        record = {
            "fulltype": fulltype,
            "use_case_id": use_case_id,
            "rule_ids": list(rule_ids),
            "decision_recipe_ids": sorted(decision_recipe_ids),
            "nav_registry_identity": nav_registry_identity or None,
            "nav_eligible": nav_entry.get("nav_eligible") if isinstance(nav_entry, dict) else None,
            "navigation_target": {
                key: nav_entry.get(key)
                for key in ("original_name", "category", "nav_eligible")
                if isinstance(nav_entry, dict) and key in nav_entry
            },
        }
        if not structured_complete:
            record["reason"] = "incomplete_qg_recipe_identity_or_navigation_lineage"
            incomplete.append(record)
            continue
        recipe_id = next(iter(decision_recipe_ids))
        key = (fulltype, recipe_id)
        if key in complete:
            record["reason"] = "duplicate_qg_recipe_tuple"
            incomplete.append(record)
            continue
        record["recipe_id"] = recipe_id
        complete[key] = record
    return complete, incomplete


def classify_recipe_only(
    legacy_record: dict[str, Any],
    *,
    recipe_rows_by_fulltype: dict[str, list[dict[str, Any]]],
    rules_by_recipe_id: dict[str, list[tuple[str, dict[str, Any]]]],
) -> tuple[str, str]:
    if not legacy_record.get("producer_recipe_id_present"):
        return "identity_unavailable", "producer_recipe_id_missing"
    fulltype = legacy_record["fulltype"]
    recipe_id = legacy_record["recipe_id"]
    matching_rules = rules_by_recipe_id.get(recipe_id, [])
    for rule_id, rule in matching_rules:
        matched = set(rule.get("matched_fulltypes", []) or []) | set(
            rule.get("matched_keep_fulltypes", []) or []
        )
        if str(rule.get("decision") or "").upper() == "NO" and fulltype in matched:
            return "qg_decided_no", f"decision_no:{rule_id}"

    for row in recipe_rows_by_fulltype.get(fulltype, []):
        for rule_id in evidence_rule_ids(row, "recipe_evidence"):
            rule = dict(matching_rules).get(rule_id)
            if rule is not None and str(rule.get("recipe_id") or "") == recipe_id:
                return "identity_unavailable", "positive_qg_row_identity_incomplete"

    if not matching_rules:
        return "qg_absent", "no_rule"
    if not any(str(rule.get("decision") or "") for _, rule in matching_rules):
        return "qg_absent", "no_decision_record"
    return "qg_absent", "positive_row_unmaterialized"


def build_recipe_crosswalk_report(
    recipe_index: dict[str, Any],
    recipe_decisions: dict[str, Any],
    recipe_nav: dict[str, Any],
    recipe_rows: list[tuple[str, dict[str, Any]]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    legacy = build_legacy_recipe_tuples(recipe_index)
    qg, incomplete_qg = build_qg_recipe_tuples(recipe_rows, recipe_decisions, recipe_nav)
    legacy_keys = set(legacy)
    qg_keys = set(qg)
    intersection_keys = sorted(legacy_keys & qg_keys)
    recipe_only_keys = sorted(legacy_keys - qg_keys)
    qg_recipe_only_keys = sorted(qg_keys - legacy_keys)

    rules_by_recipe_id: dict[str, list[tuple[str, dict[str, Any]]]] = defaultdict(list)
    for rule_id, rule in recipe_decisions.get("rules", {}).items():
        recipe_id = str(rule.get("recipe_id") or "")
        if recipe_id:
            rules_by_recipe_id[recipe_id].append((str(rule_id), rule))
    recipe_rows_by_fulltype: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fulltype, row in recipe_rows:
        recipe_rows_by_fulltype[fulltype].append(row)

    categories: dict[str, list[dict[str, Any]]] = {
        "identity_unavailable": [],
        "qg_absent": [],
        "qg_decided_no": [],
    }
    recipe_only: list[dict[str, Any]] = []
    for key in recipe_only_keys:
        category, subreason = classify_recipe_only(
            legacy[key],
            recipe_rows_by_fulltype=recipe_rows_by_fulltype,
            rules_by_recipe_id=rules_by_recipe_id,
        )
        record = {
            **legacy[key],
            "failure_category": category,
            "subreason": subreason,
            "responsibility": {
                "identity_unavailable": "producer_qg_structured_identity_prerequisite",
                "qg_absent": "L4-RAT-08_owner_disposition_qg_coverage_scope",
                "qg_decided_no": "L4-RAT-08_owner_disposition_qg_reconsideration_scope",
            }[category],
        }
        recipe_only.append(record)
        categories[category].append(record)

    category_sets = {
        name: {(record["fulltype"], record["recipe_id"]) for record in records}
        for name, records in categories.items()
    }
    category_union = set().union(*category_sets.values())
    pairwise_intersections = {
        f"{left}&{right}": len(category_sets[left] & category_sets[right])
        for index, left in enumerate(categories)
        for right in list(categories)[index + 1 :]
    }

    current_recipe_index_lua = IRIS_ROOT / "media" / "lua" / "client" / "Iris" / "Data" / "IrisRecipeIndexData.lua"
    recipe_index_lua_text = current_recipe_index_lua.read_text(encoding="utf-8")
    chunks_text = "\n".join(path.read_text(encoding="utf-8") for path in sorted(RUNTIME_DATA_ROOT.glob("Chunk*.lua")))
    runtime_plumbing = {
        "common_prerequisite_not_taxonomy_bucket": True,
        "current_recipe_index_data_has_recipe_id_field": bool(re.search(r"\brecipe_id\s*=", recipe_index_lua_text)),
        "current_recipe_nav_ref_has_recipe_id_field": bool(
            re.search(r"recipe_nav_ref\s*=\s*\{[^\n}]*\brecipe_id\s*=", chunks_text)
        ),
    }
    # Layer 4 consumes the QG navigation projection directly. The retained
    # RecipeIndex facade remains public compatibility, not presentation input.
    runtime_plumbing["required"] = not runtime_plumbing[
        "current_recipe_nav_ref_has_recipe_id_field"
    ]

    report = {
        "legacy_recipe_tuple_count": len(legacy_keys),
        "qg_recipe_tuple_count": len(qg_keys),
        "mapped_recipe_intersection_count": len(intersection_keys),
        "recipe_only_count": len(recipe_only_keys),
        "qg_recipe_only_count": len(qg_recipe_only_keys),
        "raw_legacy_tuples": [legacy[key] for key in sorted(legacy)],
        "raw_qg_tuples": [qg[key] for key in sorted(qg)],
        "mapped_recipe_intersection": [
            {"legacy": legacy[key], "qg": qg[key]} for key in intersection_keys
        ],
        "recipe_only": recipe_only,
        "qg_recipe_only": [qg[key] for key in qg_recipe_only_keys],
        "incomplete_qg_recipe_rows": incomplete_qg,
        "failure_categories": categories,
        "category_union_matches_recipe_only": category_union == set(recipe_only_keys),
        "category_pairwise_intersection_counts": pairwise_intersections,
        "category_pairwise_disjoint": all(count == 0 for count in pairwise_intersections.values()),
        "planning_snapshot_drift": {
            "planning_legacy_count": 794,
            "planning_qg_count": 791,
            "planning_intersection_count": 791,
            "planning_recipe_only_count": 3,
            "planning_qg_recipe_only_count": 0,
            "planning_recipe_only_tuples": [
                {"fulltype": fulltype, "recipe_id": recipe_id}
                for fulltype, recipe_id in sorted(PLANNING_RECIPE_ONLY)
            ],
            "fresh_recipe_only_matches_planning": set(recipe_only_keys) == PLANNING_RECIPE_ONLY,
        },
        "runtime_stable_id_plumbing": runtime_plumbing,
        "count_equality_is_not_identity_parity": len(legacy_keys) == len(qg_keys),
    }

    candidate = {
        "schema_version": "iris-layer4-stable-id-plumbing-candidate-v1",
        "status": "isolated_off_live_candidate_only",
        "current_installation": False,
        "gate_effect": "none_until_external_source_adoption_and_fresh_gate3_census",
        "legacy_recipe_rows": [
            {
                "fulltype": record["fulltype"],
                "recipe_id": record["recipe_id"],
                "roles": record["roles"],
                "canonical_qg_use_case_id": qg.get(key, {}).get("use_case_id"),
                "canonical_qg_rule_ids": qg.get(key, {}).get("rule_ids", []),
                "canonical_nav_registry_identity": qg.get(key, {}).get("nav_registry_identity"),
            }
            for key, record in sorted(legacy.items())
        ],
        "unmapped_recipe_only": recipe_only,
    }
    candidate["payload_sha256"] = hashlib.sha256(canonical_json_bytes(candidate)).hexdigest()
    return report, candidate


def _lua_ascii_unescape(value: str) -> str:
    return value.replace(r"\"", '"').replace(r"\\", "\\")


def parse_runtime_chunks() -> dict[str, list[tuple[str, str, str]]]:
    entry_re = re.compile(r'^chunk\["((?:\\.|[^"\\])*)"\] = \{$')
    label_re = re.compile(r'\blabel_key = "((?:\\.|[^"\\])*)"')
    surface_re = re.compile(r'\bsurface = "((?:\\.|[^"\\])*)"')
    kind_re = re.compile(r'\bline_kind = "((?:\\.|[^"\\])*)"')
    result: dict[str, list[tuple[str, str, str]]] = {}
    for path in sorted(RUNTIME_DATA_ROOT.glob("Chunk[0-9][0-9][0-9].lua")):
        current_fulltype: str | None = None
        in_lines = False
        for line in path.read_text(encoding="utf-8").splitlines():
            entry_match = entry_re.match(line)
            if entry_match:
                current_fulltype = _lua_ascii_unescape(entry_match.group(1))
                result[current_fulltype] = []
                in_lines = False
                continue
            if current_fulltype is None:
                continue
            if line == "    lines = {":
                in_lines = True
                continue
            if in_lines and line == "    },":
                in_lines = False
                continue
            if not in_lines:
                continue
            label = label_re.search(line)
            if not label:
                continue
            surface = surface_re.search(line)
            kind = kind_re.search(line)
            result[current_fulltype].append(
                (
                    _lua_ascii_unescape(label.group(1)),
                    _lua_ascii_unescape(surface.group(1)) if surface else "",
                    _lua_ascii_unescape(kind.group(1)) if kind else "",
                )
            )
    return result


def parse_line_count_index() -> dict[str, int]:
    pattern = re.compile(r'^\s*\["((?:\\.|[^"\\])*)"\]\s*=\s*(\d+),\s*$')
    result: dict[str, int] = {}
    for line in LINE_COUNT_PATH.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            result[_lua_ascii_unescape(match.group(1))] = int(match.group(2))
    return result


def build_runtime_projection_report(fulltypes: dict[str, Any]) -> dict[str, Any]:
    runtime = parse_runtime_chunks()
    line_counts = parse_line_count_index()
    source = {
        fulltype: [
            (str(row.get("use_case_id") or ""), str(row.get("surface") or ""), str(row.get("line_kind") or ""))
            for row in positive_rows(entry)
        ]
        for fulltype, entry in fulltypes.items()
    }
    identity_mismatches = [
        {
            "fulltype": fulltype,
            "source": source.get(fulltype, []),
            "runtime": runtime.get(fulltype, []),
        }
        for fulltype in sorted(set(source) | set(runtime))
        if source.get(fulltype, []) != runtime.get(fulltype, [])
    ]
    count_mismatches = [
        {
            "fulltype": fulltype,
            "source_count": len(source.get(fulltype, [])),
            "line_count_index": line_counts.get(fulltype),
        }
        for fulltype in sorted(set(source) | set(line_counts))
        if len(source.get(fulltype, [])) != line_counts.get(fulltype)
    ]
    return {
        "source_entry_count": len(source),
        "runtime_chunk_entry_count": len(runtime),
        "line_count_index_entry_count": len(line_counts),
        "identity_order_mismatch_count": len(identity_mismatches),
        "identity_order_mismatches": identity_mismatches,
        "line_count_mismatch_count": len(count_mismatches),
        "line_count_mismatches": count_mismatches,
        "chunk_index_sha256": sha256_path(CHUNK_INDEX_PATH),
        "line_count_index_sha256": sha256_path(LINE_COUNT_PATH),
    }


def git_changed_paths() -> list[str]:
    commands = (
        ["git", "diff", "--name-only", "--no-renames", "HEAD", "--"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    paths: set[str] = set()
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        paths.update(line.strip().replace("\\", "/") for line in completed.stdout.splitlines() if line.strip())
    return sorted(paths)


def is_protected_path(path: str) -> bool:
    return path in PROTECTED_EXACT_PATHS or any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def protected_current_files() -> list[Path]:
    paths = [REPOSITORY_ROOT / path for path in sorted(PROTECTED_EXACT_PATHS) if (REPOSITORY_ROOT / path).is_file()]
    for prefix in PROTECTED_PREFIXES:
        root = REPOSITORY_ROOT / prefix
        if root.exists():
            paths.extend(path for path in sorted(root.rglob("*")) if path.is_file())
    return sorted(set(paths))


def build_no_mutation_report() -> dict[str, Any]:
    changed = [path for path in git_changed_paths() if path not in SELF_GENERATED_REPORT_PATHS]
    subject_changes = [path for path in changed if path in DECLARED_IMPLEMENTATION_SUBJECT_PATHS]
    unrelated_changes = [path for path in changed if path not in DECLARED_IMPLEMENTATION_SUBJECT_PATHS]
    protected_changes = [path for path in subject_changes if is_protected_path(path)]
    unrelated_protected_changes = [path for path in unrelated_changes if is_protected_path(path)]
    inspected = [
        {"path": repository_relative(path), "sha256": sha256_path(path)} for path in protected_current_files()
    ]
    return {
        "schema_version": "iris-layer4-preseal-no-current-mutation-v1",
        "protected_path_count": len(inspected),
        "protected_paths": inspected,
        "all_changed_paths": changed,
        "declared_implementation_subject_paths": sorted(DECLARED_IMPLEMENTATION_SUBJECT_PATHS),
        "subject_changed_paths": subject_changes,
        "preexisting_or_concurrent_changes_outside_subject": unrelated_changes,
        "self_generated_report_paths_excluded_from_recursive_status_input": sorted(
            SELF_GENERATED_REPORT_PATHS
        ),
        "protected_changed_paths": protected_changes,
        "protected_changes_outside_subject": unrelated_protected_changes,
        "policy_dependent_current_mutation_count": len(protected_changes),
        "assertion": "PASS" if not protected_changes else "FAIL",
        "unrelated_or_permitted_changes_are_not_hidden": True,
    }


def input_hashes() -> list[dict[str, str]]:
    paths = [
        PLAN_PATH,
        WALKTHROUGH_PATH,
        UPSTREAM_PATH,
        QG_USECASES_PATH,
        DESCRIPTIONS_PATH,
        CAPABILITIES_PATH,
        CAPABILITIES_LUA_PATH,
        RIGHTCLICK_SOURCE_PATH,
        RECIPE_INDEX_PATH,
        RECIPE_DECISIONS_PATH,
        RECIPE_NAV_PATH,
        CHUNK_INDEX_PATH,
        LINE_COUNT_PATH,
        *sorted(RUNTIME_DATA_ROOT.glob("Chunk[0-9][0-9][0-9].lua")),
    ]
    return [{"path": repository_relative(path), "sha256": sha256_path(path)} for path in paths]


def build_contract_report(*, small_max: int, dense_min: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    upstream = load_json(UPSTREAM_PATH)
    installed_fulltypes = build_current_qg_fulltypes(
        upstream.get("fulltypes", {}), parse_runtime_chunks()
    )
    density, rows_by_surface = build_density_and_schema_report(
        installed_fulltypes, small_max=small_max, dense_min=dense_min
    )
    # Gate 3 is a source-migration readiness gate. Compare the legacy producer
    # facts to the canonical QG producer output, not to the older installed
    # Layer 4 projection; installation remains a later, separately governed gate.
    qg_source = load_json(QG_USECASES_PATH)
    qg_source_schema, qg_rows_by_surface = build_density_and_schema_report(
        qg_source.get("fulltypes", {}), small_max=small_max, dense_min=dense_min
    )
    capabilities = load_json(CAPABILITIES_PATH)
    capability_report = build_capability_crosswalk_report(
        capabilities, qg_rows_by_surface["context_menu"]
    )
    recipe_report, stable_id_candidate = build_recipe_crosswalk_report(
        load_json(RECIPE_INDEX_PATH),
        load_json(RECIPE_DECISIONS_PATH),
        load_json(RECIPE_NAV_PATH),
        qg_rows_by_surface["recipe_ui"],
    )
    owner_policy, owner_policy_errors = validate_owner_policy_seal(
        capability_report=capability_report,
        recipe_report=recipe_report,
    )
    runtime_report = build_runtime_projection_report(installed_fulltypes)
    no_mutation = build_no_mutation_report()

    gate3_pass = (
        capability_report["capability_only_count"] == 0
        and recipe_report["recipe_only_count"] == 0
    )
    # Gate 3 is deliberately independent from presentation-policy approval.
    # The previous owner seal is ineligible for this subject and is not loaded.
    contract_errors: list[str] = []
    if density["duplicate_identity_count"]:
        contract_errors.append("duplicate_qg_identity")
    if density["missing_identity_count"]:
        contract_errors.append("missing_qg_identity")
    if density["unknown_surface_count"] or density["surface_both_count"]:
        contract_errors.append("unsupported_qg_surface")
    if density["source_surface_mismatch_count"]:
        contract_errors.append("qg_source_surface_mismatch")
    if qg_source_schema["duplicate_identity_count"]:
        contract_errors.append("canonical_qg_duplicate_identity")
    if qg_source_schema["missing_identity_count"]:
        contract_errors.append("canonical_qg_missing_identity")
    if qg_source_schema["unknown_surface_count"] or qg_source_schema["surface_both_count"]:
        contract_errors.append("canonical_qg_unsupported_surface")
    if qg_source_schema["source_surface_mismatch_count"]:
        contract_errors.append("canonical_qg_source_surface_mismatch")
    if capability_report["unknown_capability_count"]:
        contract_errors.append("unknown_capability_family")
    if not recipe_report["category_union_matches_recipe_only"]:
        contract_errors.append("recipe_only_category_union_mismatch")
    if not recipe_report["category_pairwise_disjoint"]:
        contract_errors.append("recipe_only_category_overlap")
    if runtime_report["identity_order_mismatch_count"]:
        contract_errors.append("runtime_chunk_identity_order_mismatch")
    if runtime_report["line_count_mismatch_count"]:
        contract_errors.append("runtime_line_count_mismatch")
    contract_errors.extend(owner_policy_errors)
    if not gate3_pass and no_mutation["policy_dependent_current_mutation_count"]:
        contract_errors.append("preseal_policy_dependent_current_mutation")

    rat08_binding_status = (
        "not_applicable_no_recipe_only"
        if recipe_report["recipe_only_count"] == 0
        else "required_but_unapproved"
    )
    owner_sealed = not owner_policy_errors and gate3_pass
    layer4_build_root = IRIS_ROOT / "build" / "description" / "v2" / "tools" / "build"
    generation_contract_available = all(
        (layer4_build_root / name).is_file()
        for name in (
            "generate_layer4_runtime_projection.py",
            "validate_layer4_runtime_projection.py",
            "update_layer4_runtime_projection.py",
        )
    )
    generated_plumbing_required = recipe_report["runtime_stable_id_plumbing"]["required"]
    partial_generated_boundary = owner_sealed and generated_plumbing_required and not generation_contract_available
    path_selection = {
        "schema_version": "iris-layer4-execution-path-selection-v2",
        "owner_policy_seal_status": owner_policy["status"],
        "owner_policy_seal_sha256": owner_policy["sha256"],
        "rat08_binding_status": rat08_binding_status,
        "capability_only_count": capability_report["capability_only_count"],
        "recipe_only_count": recipe_report["recipe_only_count"],
        "gate3_status": "PASS" if gate3_pass else "BLOCKED",
        "selected_execution_path": (
            "gate3_owner_sealed_layer4_generation_contract_blocked_partial"
            if partial_generated_boundary
            else "gate3_owner_policy_sealed_full_implementation"
            if owner_sealed
            else "gate3_source_migration_unblocked_owner_seal_invalid"
            if gate3_pass
            else "preseal_gate3_blocked"
        ),
        "change2_and_later_policy_dependent_current_implementation": (
            "change2_mutation_independent_only_projection_dependent_deferred"
            if partial_generated_boundary
            else "authorized"
            if owner_sealed
            else "blocked_pending_valid_owner_policy_seal"
            if gate3_pass
            else "blocked_by_gate3"
        ),
        "mixed_qg_legacy_recipe_projection": "forbidden",
        "layer4_generation_contract_available": generation_contract_available,
        "generated_stable_id_plumbing_required": generated_plumbing_required,
        "projection_dependent_scope": "deferred" if partial_generated_boundary else "authorized",
        "existing_renderer_and_recipe_fallback": "preserve" if partial_generated_boundary else "cutover_authorized",
        "preserved_projection_paths": {
            path: {
                "execution_base_sha256": git_blob_sha256(APPROVED_EXECUTION_BASE_COMMIT, path),
                "current_sha256": git_blob_sha256("HEAD", path),
                "byte_identical": git_blob_sha256(APPROVED_EXECUTION_BASE_COMMIT, path)
                == git_blob_sha256("HEAD", path),
            }
            for path in (EXISTING_RENDERER_PATH, EXISTING_COLLECTOR_PATH)
        },
        "required_validation": (
            ["V1", "V2", "V3", "V4", "V7"]
            if partial_generated_boundary
            else ["V1", "V2", "V3", "V4", "V5", "V6", "V7"]
            if owner_sealed
            else ["V1", "V4"]
            if gate3_pass
            else ["V1"]
        ),
        "not_applicable": (
            {
                "V5": "adaptive_projection_and_dev_harness_not_installed",
                "V6": "installed_current_generation_package_projection_absent",
            }
            if partial_generated_boundary
            else {}
            if owner_sealed
            else
            {
                "V2": "no_change2_or_adaptive_ui_subject",
                "V3": "no_controlled_current_denominator_change_subject",
                "V5": "no_adaptive_runtime_or_dev_harness_subject",
                "V6": "no_adaptive_implementation_package_projection_subject",
                "V7": "source_correction_impact_recorded_in_gate3_walkthrough",
            }
            if gate3_pass
            else {
                "V2": "no_change2_subject",
                "V3": "no_controlled_current_denominator_change_subject",
                "V4": "no_current_lua_change",
                "V5": "no_adaptive_runtime_or_dev_harness_subject",
                "V6": "no_installed_or_no-mutation_implementation_projection_subject",
                "V7": "no_tracked_implementation_impact_subject",
            }
        ),
        "closeout_ceiling": (
            "partial"
            if partial_generated_boundary
            else "full_implementation_validation_required"
            if owner_sealed
            else "gate3_pass_owner_approval_required"
            if gate3_pass
            else "blocked"
        ),
    }

    report = {
        "schema_version": "iris-layer4-interaction-presentation-contract-report-v1",
        "execution_subject": {
            "plan_path": repository_relative(PLAN_PATH),
            "plan_sha256": sha256_path(PLAN_PATH),
            "walkthrough_path": repository_relative(WALKTHROUGH_PATH),
            "walkthrough_sha256": sha256_path(WALKTHROUGH_PATH),
            "execution_base_commit": APPROVED_EXECUTION_BASE_COMMIT,
            "execution_base_tree": APPROVED_EXECUTION_BASE_TREE,
            "owner_policy_seal": owner_policy,
            "runtime_fact_correction_approval": {
                "status": "explicitly_approved",
                "source": "user_instruction_2026-08-21",
                "artifact": repository_relative(CAPABILITIES_LUA_PATH),
                "scope": "remove_three_false_can_scrap_moveables_facts",
                "not_adaptive_policy_approval": True,
            },
        },
        "input_hashes": input_hashes(),
        "threshold_binding": {
            "small_max": small_max,
            "dense_min": dense_min,
            "source": "owner_policy_seal:L4-RAT-01",
            "proposal_not_sealed": False,
            "validator_or_test_literal_is_authority": False,
            "owner_policy_status": owner_policy["status"],
        },
        "source_order_binding": {
            "source_order": ["recipe", "rightclick"],
            "source": "owner_policy_seal:L4-RAT-04",
        },
        "density_and_schema": density,
        "canonical_qg_source_schema": qg_source_schema,
        "capability_crosswalk": capability_report,
        "recipe_crosswalk": recipe_report,
        "rat08_dispositions": [],
        "rat08_status": rat08_binding_status,
        "policy_authorization": {
            "status": owner_policy["status"],
            "required_ratifications": [f"L4-RAT-{number:02d}" for number in range(1, 8)],
            "rat08": rat08_binding_status,
            "qg_only_publication_status": "approved",
            "qg_only_count": capability_report["qg_only_count"],
            "existing_owner_seal_eligible": False,
            "fresh_owner_seal_sha256": owner_policy["sha256"],
        },
        "runtime_projection_parity": runtime_report,
        "gate3": {
            "expression": "capability_only == 0 AND recipe_only == 0",
            "status": "PASS" if gate3_pass else "BLOCKED",
            "capability_only_count": capability_report["capability_only_count"],
            "recipe_only_count": recipe_report["recipe_only_count"],
            "owner_disposition_does_not_override_raw_gate": True,
        },
        "contract_errors": sorted(set(contract_errors)),
        "execution_status": "PASS" if not contract_errors else "FAIL",
        "closeout_state_ceiling": path_selection["closeout_ceiling"],
    }
    report["report_payload_sha256"] = hashlib.sha256(canonical_json_bytes(report)).hexdigest()
    path_selection["contract_report_payload_sha256"] = report["report_payload_sha256"]
    no_mutation["contract_report_payload_sha256"] = report["report_payload_sha256"]
    stable_id_candidate["contract_report_payload_sha256"] = report["report_payload_sha256"]
    return report, path_selection, no_mutation, stable_id_candidate


def write_contract_artifacts(*, small_max: int, dense_min: int) -> dict[str, Any]:
    report, path_selection, no_mutation, stable_id_candidate = build_contract_report(
        small_max=small_max, dense_min=dense_min
    )
    write_json(REPORT_PATH, report)
    write_json(PATH_SELECTION_PATH, path_selection)
    write_json(NO_MUTATION_PATH, no_mutation)
    write_json(STABLE_ID_CANDIDATE_PATH, stable_id_candidate)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the Iris Layer 4 pre-implementation census and migration-gate report."
    )
    parser.add_argument("--small-max", type=int, required=True)
    parser.add_argument("--dense-min", type=int, required=True)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    report = write_contract_artifacts(small_max=args.small_max, dense_min=args.dense_min)
    print(
        json.dumps(
            {
                "execution_status": report["execution_status"],
                "gate3_status": report["gate3"]["status"],
                "capability_only_count": report["gate3"]["capability_only_count"],
                "recipe_only_count": report["gate3"]["recipe_only_count"],
                "report_path": repository_relative(REPORT_PATH),
                "report_payload_sha256": report["report_payload_sha256"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if report["execution_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
