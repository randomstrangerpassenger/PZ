from __future__ import annotations

import pytest

from iris_tooling.domains.tooltip_t1.audit import (
    _layer4_candidates,
    _slot_selected_layer4,
    classify_menu_relation,
    public_surface_reason,
)
from iris_tooling.domains.tooltip_t1.models import (
    LocaleSurfaceReadiness,
    MenuParityStatus,
    SemanticSlotState,
    Slot,
    TooltipContractError,
    mock_consume,
)
from iris_tooling.domains.tooltip_t1.projection import Layer4Candidate, select_layer4, verify_invariants


@pytest.mark.parametrize(
    "case",
    ["both", "recipe_only", "rightclick_only", "capacity", "duplicate", "ineligible", "permutation", "selection_structure", "authority_type_guard"],
)
def test_layer4_projection_invariance(case: str) -> None:
    recipe = Layer4Candidate("uc.recipe.a", "recipe")
    recipe_b = Layer4Candidate("uc.recipe.b", "recipe")
    right = Layer4Candidate("uc.action.a", "rightclick")
    if case == "both":
        selected, _ = select_layer4([recipe_b, right, recipe])
        assert {row.source for row in selected} == {"recipe", "rightclick"}
    elif case == "recipe_only":
        selected, _ = select_layer4([recipe_b, recipe])
        assert len(selected) == 2 and {row.source for row in selected} == {"recipe"}
    elif case == "rightclick_only":
        assert [row.interaction_id for row in select_layer4([right])[0]] == ["uc.action.a"]
    elif case == "capacity":
        selected, dispositions = select_layer4([recipe, recipe_b, Layer4Candidate("uc.recipe.c", "recipe")])
        assert len(selected) == 2 and any(row.disposition == "excluded_capacity" for row in dispositions)
    elif case == "duplicate":
        _, dispositions = select_layer4([recipe, recipe])
        assert any(row.disposition == "excluded_exact_duplicate_identity" for row in dispositions)
    elif case == "ineligible":
        rows = [Layer4Candidate("", "recipe"), Layer4Candidate("uc.exclusion.x", "rightclick", line_kind="exclusion"), Layer4Candidate("uc.x", "unknown")]
        selected, dispositions = select_layer4(rows)
        assert not selected and {row.disposition for row in dispositions} == {"correction_missing_identity", "ineligible_exclusion", "ineligible_not_public"}
    elif case == "permutation":
        result = verify_invariants([recipe, recipe_b, right])
        assert result["permutation"]["changed"] is False
    elif case == "selection_structure":
        result = verify_invariants([recipe, recipe_b, right])
        isolation = result["readiness_isolation"]
        assert isolation["forbidden_readiness_fields_present"] is False
        assert "localized_surfaces" not in isolation["selection_input_fields"]
        assert "menu_consumer_identity_ref" not in isolation["selection_input_fields"]
    else:
        locale_bearing_slot = Slot(
            "S3",
            "uc.recipe.a",
            SemanticSlotState.SELECTED,
            {"ko": "가", "en": "A"},
            {"ko": LocaleSurfaceReadiness.READY, "en": LocaleSurfaceReadiness.READY},
        )
        with pytest.raises(TooltipContractError, match="IDENTITY_ONLY"):
            select_layer4([locale_bearing_slot])
        with pytest.raises(TooltipContractError, match="AUTHORITY_CEILING"):
            _layer4_candidates({"use_cases": [{
                "use_case_id": "uc.recipe.a",
                "surface": "recipe_ui",
                "line_kind": "evidence",
                "display_by_locale": {"ko": "가", "en": "A"},
            }]})


@pytest.mark.parametrize(
    "case",
    ["shared_relation", "missing_relation", "lexical_similarity_rejected", "forbidden_ko", "forbidden_en", "allowed_contrast", "no_fallback", "locale_pair", "identity_relation", "fixed_order", "cr_rejected", "lf_rejected", "width_advisory"],
)
def test_locale_menu_public_text(case: str) -> None:
    row = {
        "schema_version": "iris-tooltip-t2-handoff-v1",
        "subject_binding_ref": "subject_binding.json",
        "full_type": "Base.X",
        "slots": [{"slot_id": "S2", "semantic_identity": "fact:x", "localized_surfaces": {"ko": "사실", "en": "Fact"}}],
    }
    lexical = {"ko_forbidden": ["추천", "최고"], "en_forbidden": ["recommended", "best"]}
    if case == "shared_relation":
        assert classify_menu_relation(["uc.recipe.a"], {"uc.recipe.a"}) is MenuParityStatus.VERIFIED
    elif case in {"missing_relation", "lexical_similarity_rejected"}:
        consumer = set() if case == "missing_relation" else {"uc.recipe.A"}
        assert classify_menu_relation(["uc.recipe.a"], consumer) is MenuParityStatus.CORRECTION_REQUIRED
    elif case in {"forbidden_ko", "forbidden_en"}:
        locale = "ko" if case == "forbidden_ko" else "en"
        text = "최고 선택" if locale == "ko" else "Recommended choice"
        assert public_surface_reason(text, locale, lexical) == "LOCALE_FORBIDDEN_EXPRESSION"
    elif case == "allowed_contrast":
        assert public_surface_reason("presentation order", "en", lexical) is None
    elif case == "no_fallback":
        row["slots"][0]["localized_surfaces"]["en"] = None
        with pytest.raises(TooltipContractError, match="unavailable"):
            mock_consume(row, "en")
    elif case == "locale_pair":
        candidate = Layer4Candidate("uc.recipe.a", "recipe")
        slot = _slot_selected_layer4(
            "S3",
            candidate,
            {"uc.recipe.a": {"localized_surfaces": {"ko": "레시피에 사용된다.", "en": None}, "authority_ref": "owner#record"}},
            {},
            lexical,
        )
        assert slot.locale_readiness["ko"] is LocaleSurfaceReadiness.READY
        assert slot.locale_readiness["en"] is LocaleSurfaceReadiness.CORRECTION_REQUIRED
        assert slot.localized_surfaces["en"] is None
    elif case == "identity_relation":
        mapping = {
            "uc.recipe.a": {"localized_surfaces": {"ko": "같은 문장", "en": "Same text"}, "authority_ref": "owner#a"},
            "uc.recipe.b": {"localized_surfaces": {"ko": "같은 문장", "en": "Same text"}, "authority_ref": "owner#b"},
        }
        a = _slot_selected_layer4("S3", Layer4Candidate("uc.recipe.a", "recipe"), mapping, {}, lexical)
        b = _slot_selected_layer4("S3", Layer4Candidate("uc.recipe.b", "recipe"), mapping, {}, lexical)
        assert a.semantic_identity != b.semantic_identity and a.authority_ref != b.authority_ref
    elif case == "fixed_order":
        row["slots"].insert(0, {"slot_id": "S3", "semantic_identity": "uc:x", "localized_surfaces": {"ko": "행동", "en": "Action"}})
        with pytest.raises(TooltipContractError, match="fixed semantic order"):
            mock_consume(row, "ko")
    elif case in {"cr_rejected", "lf_rejected"}:
        row["slots"][0]["localized_surfaces"]["ko"] = "두\r줄" if case == "cr_rejected" else "두\n줄"
        with pytest.raises(TooltipContractError, match="multiline"):
            mock_consume(row, "ko")
    else:
        row["slots"][0]["localized_surfaces"]["en"] = "A" * 1000
        assert mock_consume(row, "en") == ["A" * 1000]
