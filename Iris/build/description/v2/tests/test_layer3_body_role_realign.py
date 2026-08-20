from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


BUILD_DIR = Path(__file__).resolve().parents[1] / "tools" / "build"
sys.path.insert(0, str(BUILD_DIR))

from layer3_body_role_realign import (  # noqa: E402
    RoleRealignError,
    classify_disposition,
    classify_readiness,
    compose_fact_inventory,
    compose_role_material,
    duplicate_assessment,
    index_rows,
    load_item_denominator,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[5]
CONFIG_ROOT = REPOSITORY_ROOT / "Iris/build/description/v2/data/layer3_body_role_realign"
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures/layer3_body_role_realign"


def fixture_inventory():
    payload = json.loads((FIXTURE_ROOT / "mapping_cases.json").read_text(encoding="utf-8"))
    mapping = json.loads((CONFIG_ROOT / "fact_kind_mapping_contract.json").read_text(encoding="utf-8"))
    facts = index_rows(payload["facts"], "item_id", "FACT")
    decisions = index_rows(payload["decisions"], "item_id", "DECISION")
    return compose_fact_inventory(
        facts_by_item=facts,
        decisions_by_item=decisions,
        mapping_contract=mapping,
    )


def test_mapping_is_closed_and_special_context_fails_to_review():
    inventory, coverage = fixture_inventory()
    assert coverage["unresolved_mapping_count"] == 0
    by_item = {}
    for row in inventory:
        by_item.setdefault(row["item_id"], []).append(row)
    assert classify_readiness(by_item["Base.Role"], None, "stale_one_off_evidence")[0] == "description_ready"
    assert classify_readiness(by_item["Base.Acquisition"], None, "stale_one_off_evidence")[0] == "acquisition_only"
    assert classify_readiness(by_item["Base.Review"], None, "stale_one_off_evidence")[0] == "review_required"


def test_unmapped_origin_fails_closed_without_rendered_text_fallback():
    mapping = json.loads((CONFIG_ROOT / "fact_kind_mapping_contract.json").read_text(encoding="utf-8"))
    fact = {
        "item_id": "Base.Unknown",
        "identity_hint": "물품",
        "primary_use": "문장을 읽어 추정하면 안 된다",
        "fact_origin": {"identity_hint": ["seed"], "primary_use": ["unknown_origin"]},
    }
    with pytest.raises(RoleRealignError, match="BLOCKED_MAPPING_CONTRACT"):
        compose_fact_inventory(
            facts_by_item={"Base.Unknown": fact},
            decisions_by_item={"Base.Unknown": {"item_id": "Base.Unknown"}},
            mapping_contract=mapping,
        )


def test_acquisition_only_projection_does_not_create_core_description():
    inventory, _ = fixture_inventory()
    facts = [row for row in inventory if row["item_id"] == "Base.Acquisition"]
    material = compose_role_material(
        "Base.Acquisition",
        facts,
        "acquisition_only",
        {"body_plan": {"emitted_section_names": ["acquisition_support"]}},
    )
    assert material["core_description"] is None
    assert material["acquisition_information"] == "상자에서 얻는다."
    assert material["menu_text_ko"] == "획득 방법: 상자에서 얻는다."
    disposition, _ = classify_disposition(
        current_text="물품이다.\n\n획득 방법: 상자에서 획득",
        material=material,
        item_facts=facts,
    )
    assert disposition == "reduce"


def test_short_role_is_not_rejected_by_length():
    inventory, _ = fixture_inventory()
    facts = [row for row in inventory if row["item_id"] == "Base.Role"]
    material = compose_role_material("Base.Role", facts, "description_ready", None)
    assert material["core_description"] == "작업에 쓴다."


def test_exact_duplicate_signal_blocks_only_different_semantic_sets():
    shared = {
        "menu_text_ko": "같은 역할이다.",
        "semantic_consumed_fact_set": ["same"],
    }
    nonblocking = duplicate_assessment(
        [{"item_id": "Base.A", **shared}, {"item_id": "Base.B", **shared}]
    )
    assert nonblocking["exact_duplicate_group_count"] == 1
    assert nonblocking["differing_semantic_fact_set_blocking_count"] == 0
    blocking = duplicate_assessment(
        [
            {"item_id": "Base.A", **shared},
            {"item_id": "Base.B", "menu_text_ko": "같은 역할이다.", "semantic_consumed_fact_set": ["different"]},
        ]
    )
    assert blocking["differing_semantic_fact_set_blocking_count"] == 1


def test_optional_axes_only_affect_readiness_not_disposition():
    ips = {"page_disposition": "evidence_limited", "layer3": {"requiredness": "not_required", "representation": "missing"}}
    assert classify_readiness([], ips, "current_snapshot")[0] == "omission_allowed"
    material = compose_role_material("Base.Empty", [], "omission_allowed", None)
    disposition, _ = classify_disposition(current_text="기존 문장.", material=material, item_facts=[])
    assert disposition == "hide"


def test_case_distinct_fulltypes_remain_independent_canonical_keys():
    items = load_item_denominator(REPOSITORY_ROOT / "Iris/input/items_itemscript.json")
    assert "Base.LemonGrass" in items
    assert "Base.Lemongrass" in items
    assert len({"Base.LemonGrass", "Base.Lemongrass"} & set(items)) == 2


def test_unresolved_layer3_axes_override_acquisition_only_readiness():
    inventory, _ = fixture_inventory()
    facts = [row for row in inventory if row["item_id"] == "Base.Acquisition"]
    ips = {"layer3": {"requiredness": "unresolved", "representation": "unresolved"}}
    readiness, reasons = classify_readiness(facts, ips, "current_snapshot")
    assert readiness == "review_required"
    assert reasons == ["one_off_layer3_axes_unresolved"]
