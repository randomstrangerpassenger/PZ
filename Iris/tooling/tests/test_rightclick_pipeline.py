from __future__ import annotations

import importlib.util

from iris_tooling.domains.rightclick import pipeline_v24


def test_noncurrent_capability_module_is_not_packaged() -> None:
    assert (
        importlib.util.find_spec("iris_tooling.domains.rightclick.capability")
        is None
    )


def test_fulltype_parser_preserves_unqualified_type() -> None:
    assert pipeline_v24.parse_fulltype_item_type("Base.Hammer") == "Hammer"
    assert pipeline_v24.parse_fulltype_item_type("Hammer") == "Hammer"


def test_semicolon_list_is_normalized() -> None:
    assert pipeline_v24.parse_semicolon_list(" Tool ;WaterSource;; Tool ") == {
        "Tool",
        "WaterSource",
    }
    assert pipeline_v24.parse_semicolon_list(None) == set()


def test_truthy_contract_is_explicit() -> None:
    for value in (True, "true", "TRUE", "1", 1):
        assert pipeline_v24.is_truthy(value)
    for value in (False, "True", "yes", 0, None):
        assert not pipeline_v24.is_truthy(value)


def test_anchor_slug_is_stable() -> None:
    assert (
        pipeline_v24.normalize_slug(
            "lua/client/ISUI/ISWorldObjectContextMenu.lua::onAddFuel"
        )
        == "lua_client_isui_isworldobjectcontextmenu_onaddfuel"
    )


def test_canonical_hash_ignores_mapping_order() -> None:
    assert pipeline_v24.compute_sha256({"a": 1, "b": 2}) == (
        pipeline_v24.compute_sha256({"b": 2, "a": 1})
    )


def test_proof_merge_fails_closed_on_boolean_conflict() -> None:
    logger = pipeline_v24.PipelineLogger()

    merged, conflicted = pipeline_v24.merge_prove_value(
        True,
        False,
        "persistent_change",
        "Base.Hammer",
        logger,
    )

    assert merged is None
    assert conflicted is True
    assert logger.has_fails()


def test_item_matchers_cover_current_v24_types() -> None:
    item = {
        "Tags": "Tool;CanOpener",
        "Categories": "Survival;Cooking",
        "DisplayCategory": "Tool",
        "Type": "Normal",
        "CanStoreWater": "true",
    }

    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "type", "value": "TinOpener"})
    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "tag", "value": "CanOpener"})
    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "property", "value": "CanStoreWater"})
    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "category", "value": "Cooking"})
    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "display_category", "value": "Tool"})
    assert pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "script_type", "value": "Normal"})
    assert not pipeline_v24.match_item(item, "Base.TinOpener", {"match_type": "unsupported", "value": "Normal"})


def test_property_based_reviews_are_routed_deterministically() -> None:
    decisions = {
        "Base.Zed": {
            "decision": "PASS",
            "review_reason": "",
            "rule_ids": ["pass"],
        },
        "Base.Bucket": {
            "decision": "REVIEW",
            "review_reason": "property_based exclusion (auto conclusion forbidden)",
            "rule_ids": ["water"],
        },
    }

    assert pipeline_v24.collect_property_based_items(decisions) == {
        "Base.Bucket": {
            "fulltype": "Base.Bucket",
            "rule_ids": ["water"],
            "review_reason": "property_based exclusion (auto conclusion forbidden)",
        }
    }
