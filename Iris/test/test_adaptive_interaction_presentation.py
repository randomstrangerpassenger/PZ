from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
LUA_ROOT = REPOSITORY_ROOT / "Iris/media/lua/client/Iris/UI/Browser"
BUILD_ROOT = REPOSITORY_ROOT / "Iris/build/description/v2/tools/build"
if str(BUILD_ROOT) not in sys.path:
    sys.path.insert(0, str(BUILD_ROOT))

import build_layer3_english_localization as layer3_english  # noqa: E402


def test_standalone_projection_and_state_harness() -> None:
    result = subprocess.run(
        [
            "lua",
            str(REPOSITORY_ROOT / "Iris/test/lua/browser_interaction_density_acceptance_harness.lua"),
            str(REPOSITORY_ROOT),
        ],
        cwd=REPOSITORY_ROOT,
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PASS browser interaction density acceptance" in result.stdout


def test_collector_terminal_is_qg_only_and_single_scroll() -> None:
    sources = "\n".join(
        (LUA_ROOT / name).read_text(encoding="utf-8")
        for name in (
            "IrisBrowserInteractionCollector.lua",
            "IrisBrowserInteractionProjection.lua",
            "IrisBrowserInteractionRenderer.lua",
        )
    )
    for forbidden in (
        "IrisCapabilities",
        "getCapabilities",
        "getRecipeConnectionsForItem",
        "model.connections",
        "recipeNameSet",
    ):
        assert forbidden not in sources
    assert "ISScrollingListBox" not in sources
    assert 'Collector.collect(deps.model.interactionState' in sources


def test_qg_only_public_rows_and_installed_recipe_ids() -> None:
    descriptions = json.loads(
        (REPOSITORY_ROOT / "Iris/output/descriptions_by_fulltype.v2.4.json").read_text(encoding="utf-8")
    )["fulltypes"]
    expected = {
        ("Base.BallPeenHammer", "uc.action.construction"),
        ("Base.GardenSaw", "uc.action.wood_cutting"),
        ("Base.HammerStone", "uc.action.construction"),
    }
    observed = {
        (fulltype, row["use_case_id"])
        for fulltype, identity in expected
        for row in descriptions[fulltype]["use_case_block"]["items"]
        if row["use_case_id"] == identity and row["surface"] == "context_menu"
    }
    assert observed == expected

    chunk_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(
            (REPOSITORY_ROOT / "Iris/media/lua/client/Iris/Data/UseCaseDescriptions").glob("Chunk*.lua")
        )
    )
    assert chunk_text.count('label_key = "uc.recipe.') == 791
    assert chunk_text.count("recipe_nav_ref = { recipe_id = ") == 791


def test_full_qg_positive_identity_set_is_projection_compatible() -> None:
    fulltypes = json.loads(
        (REPOSITORY_ROOT / "Iris/output/descriptions_by_fulltype.v2.4.json").read_text(encoding="utf-8")
    )["fulltypes"]
    observed = 0
    for fulltype, payload in fulltypes.items():
        seen: set[str] = set()
        for row in payload.get("use_case_block", {}).get("items", []):
            identity = row["use_case_id"]
            if identity.startswith("uc.exclusion."):
                continue
            assert identity not in seen, (fulltype, identity)
            seen.add(identity)
            assert row["surface"] in {"recipe_ui", "context_menu"}
            observed += 1
    assert observed == 877


def test_named_density_anchors_match_current_qg_source() -> None:
    fulltypes = json.loads(
        (REPOSITORY_ROOT / "Iris/output/descriptions_by_fulltype.v2.4.json").read_text(encoding="utf-8")
    )["fulltypes"]

    def positive_rows(fulltype: str) -> list[dict[str, object]]:
        return [
            row
            for row in fulltypes[fulltype]["use_case_block"]["items"]
            if not row["use_case_id"].startswith("uc.exclusion.")
        ]

    mold = positive_rows("Base.223BulletsMold")
    assert [(row["use_case_id"], row["surface"]) for row in mold] == [
        ("uc.recipe.make_223_bullets", "recipe_ui")
    ]

    tongs = positive_rows("Base.Tongs")
    assert len(tongs) == 33
    assert all(row["surface"] == "recipe_ui" for row in tongs)


def test_ko_en_adaptive_keys_are_complete() -> None:
    required = {
        "Iris_Interaction_SourceRecipe",
        "Iris_Interaction_SourceRightClick",
        "Iris_Interaction_VerifiedEmpty",
        "Iris_Interaction_Unavailable",
        "Iris_Interaction_Compact",
        "Iris_Interaction_Full",
        "Iris_Interaction_Visible",
        "Iris_Interaction_Requirements",
        "Iris_Interaction_Construction",
        "Iris_Interaction_WoodCutting",
    }
    for locale in ("en", "ko"):
        text = (REPOSITORY_ROOT / f"Iris/media/lua/shared/translate/{locale}/Iris_{locale}.txt").read_text(
            encoding="utf-8"
        )
        assert all(f"{key} = " in text for key in required)


def test_layer3_english_keys_follow_current_public_ko_projection() -> None:
    english_entries, _generation_id, _metrics = layer3_english.build_english_entries(
        REPOSITORY_ROOT
    )
    projection = json.loads(
        (
            REPOSITORY_ROOT
            / "Iris/build/description/v2/data/layer3_body_role_realign/approved_upstream/candidate_rendered.json"
        ).read_text(encoding="utf-8")
    )["entries"]
    public_ko_keys = {fulltype for fulltype, entry in projection.items() if entry.get("text_ko")}

    assert set(english_entries) == public_ko_keys
    assert len(english_entries) == 2072
