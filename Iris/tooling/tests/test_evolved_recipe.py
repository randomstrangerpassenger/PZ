from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from iris_tooling.domains.layer4 import evolved_recipe


FIXTURE_TARGET_LABELS = {
    "Burger": {"KO": "버거", "EN": "Burger"},
    "FruitSalad": {"KO": "과일 샐러드", "EN": "Fruit salad"},
    "Salad": {"KO": "샐러드", "EN": "Salad"},
    "Sandwich": {"KO": "식빵 샌드위치", "EN": "Sandwich"},
    "Soup": {"KO": "수프", "EN": "Soup"},
    "Stew": {"KO": "스튜", "EN": "Stew"},
}


def _write(path: Path, value: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, bytes):
        path.write_bytes(value)
    else:
        path.write_text(value, encoding="utf-8")


def _source_fixture(root: Path, repository_root: Path | None = None) -> bytes:
    repository_root = repository_root or root
    _write(
        repository_root / evolved_recipe.ITEM_INVENTORY_RELATIVE_PATH,
        json.dumps(
            {
                "Base.Bowl": {"FullType": "Base.Bowl", "Type": "Normal"},
                "Base.BreadSlices": {
                    "FullType": "Base.BreadSlices",
                    "Type": "Food",
                },
                "Base.WaterPot": {
                    "FullType": "Base.WaterPot",
                    "Type": "Drainable",
                },
            },
            sort_keys=True,
        )
        + "\n",
    )
    _write(
        root / "media/scripts/items_food.txt",
        """
module Base
{
    item Apple
    {
        Spice = false,
        EvolvedRecipe = Soup:2;Stew:1|Cooked;Missing:1,
    }
    item Pepper
    {
        Spice = true,
        EvolvedRecipe = Soup:1;Soup:1,
    }
    item BreadSlices
    {
        EvolvedRecipe = Soup:1,
    }
    item OldFood
    {
        OBSOLETE = true,
        EvolvedRecipe = Soup:1,
    }
    item LabelOnly
    {
        EvolvedRecipeName = Label,
    }
    /* EvolvedRecipe = Soup:99, */
}
""".strip()
        + "\n",
    )
    _write(
        root / "media/scripts/farming.txt",
        """
module farming
{
    item Cabbage
    {
        EvolvedRecipe = Soup:1;BadToken,
    }
}
""".strip()
        + "\n",
    )
    _write(
        root / "media/scripts/evolvedrecipes.txt",
        """
module Base
{
    evolvedrecipe Soup
    {
        BaseItem:WaterPot,
        ResultItem:Soup,
    }
    evolvedrecipe Stew
    {
        BaseItem:WaterPot,
        ResultItem:Stew,
    }
    evolvedrecipe Salad
    {
        BaseItem:Bowl,
        ResultItem:Salad,
    }
    evolvedrecipe FruitSalad
    {
        BaseItem:Bowl,
        ResultItem:FruitSalad,
    }
    evolvedrecipe Sandwich
    {
        BaseItem:BreadSlices,
        ResultItem:Sandwich,
    }
    evolvedrecipe Burger
    {
        BaseItem:BreadSlices,
        ResultItem:Burger,
    }
}
""".strip()
        + "\n",
    )
    _write(
        root / "media/lua/shared/Translate/EN/ContextMenu_EN.txt",
        """
ContextMenu_EN = {
    ContextMenu_EvolvedRecipe_Soup = "Soup first",
    ContextMenu_EvolvedRecipe_Soup = "Soup second",
    ContextMenu_EvolvedRecipe_Stew = "Stew",
    ContextMenu_EvolvedRecipe_Salad = "Salad",
    ContextMenu_EvolvedRecipe_FruitSalad = "Fruit Salad",
    ContextMenu_EvolvedRecipe_Sandwich = "Sandwich",
    ContextMenu_EvolvedRecipe_Burger = "Burger",
}
""".strip()
        + "\n",
    )
    _write(
        root / "media/lua/shared/Translate/KO/ContextMenu_KO.txt",
        """
ContextMenu_KO = {
    ContextMenu_EvolvedRecipe_Soup = "텀블러",
    ContextMenu_EvolvedRecipe_Soup = "두 번째 텀블러",
    ContextMenu_EvolvedRecipe_Stew = "스튜",
    ContextMenu_EvolvedRecipe_Salad = "샐러드",
    ContextMenu_EvolvedRecipe_FruitSalad = "과일 샐러드",
    ContextMenu_EvolvedRecipe_Sandwich = "샌드위치",
    ContextMenu_EvolvedRecipe_Burger = "버거",
}
""".strip()
        + "\n",
    )
    for relative in evolved_recipe.SEMANTIC_SOURCE_PATHS:
        _write(root / relative, "-- fixture semantic source\n")
    translator = b"fixture confirms first definition wins"
    _write(root / evolved_recipe.TRANSLATOR_CLASS_PATH, translator)
    return translator


def test_source_accounting_semantics_and_locale_review_isolation(
    tmp_path: Path, monkeypatch
) -> None:
    translator = _source_fixture(tmp_path)
    monkeypatch.setattr(
        evolved_recipe,
        "CONFIRMED_FIRST_WINS_TRANSLATOR_SHA256",
        {hashlib.sha256(translator).hexdigest()},
    )
    monkeypatch.setattr(
        evolved_recipe, "STANDALONE_TARGET_LABELS", FIXTURE_TARGET_LABELS
    )

    first = evolved_recipe.build_owner(tmp_path, tmp_path)
    second = evolved_recipe.build_owner(tmp_path, tmp_path)
    assert first == second

    assert first["census"] == {
        "lexical_occurrence_count": 7,
        "active_property_row_count": 5,
        "non_target_occurrence_count": 2,
        "raw_token_count": 9,
        "pass_source_token_count": 6,
        "pass_relation_count": 11,
        "review_token_count": 2,
        "non_target_token_count": 1,
        "deduplicated_source_token_count": 1,
        "unique_public_fulltype_count": 6,
        "definition_count": 6,
        "definition_base_occurrence_count": 6,
        "definition_base_relation_count": 6,
        "definition_base_review_count": 0,
        "unique_definition_base_fulltype_count": 3,
        "non_food_definition_base_occurrence_count": 4,
        "unique_non_food_definition_base_fulltype_count": 2,
        "definition_base_item_type_occurrences": {
            "Drainable": 2,
            "Food": 2,
            "Normal": 2,
        },
    }
    apple = first["relations_by_fulltype"]["Base.Apple"]
    assert [relation["food_type_id"] for relation in apple] == ["Soup", "Stew"]
    assert apple[0]["role"] == "ingredient"
    assert apple[0]["conditions"] == []
    assert apple[0]["display_by_locale"]["EN"] == (
        "Soup · Can be added as an ingredient"
    )
    assert apple[0]["display_by_locale"]["KO"] == "수프 · 재료로 추가 가능"
    assert apple[0]["target_label_by_locale"] == {"EN": "Soup", "KO": "수프"}
    assert apple[0]["action_by_locale"] == {
        "EN": "Can be added as an ingredient",
        "KO": "재료로 추가 가능",
    }
    assert apple[0]["action_key"] == "ingredient:none"
    assert apple[0]["canonical_ordinal"] == 1
    assert "(Soup)" not in apple[0]["display_by_locale"]["EN"]
    assert apple[1]["conditions"] == ["cooked"]
    assert apple[1]["display_by_locale"]["KO"] == (
        "스튜 · 익힌 뒤 재료로 추가 가능"
    )
    assert first["relations_by_fulltype"]["Base.Pepper"][0]["display_by_locale"]["KO"] == (
        "수프 · 양념으로 추가 가능"
    )
    assert first["relations_by_fulltype"]["Base.Pepper"][0]["role"] == "spice"
    assert len(first["relations_by_fulltype"]["Base.Pepper"][0]["provenance"]) == 2
    water_pot = first["relations_by_fulltype"]["Base.WaterPot"]
    assert [(row["food_type_id"], row["role"]) for row in water_pot] == [
        ("Soup", "base_item"),
        ("Stew", "base_item"),
    ]
    assert water_pot[0]["display_by_locale"] == {
        "EN": "Soup · Used to start preparation",
        "KO": "수프 · 조리 시작에 사용",
    }
    bowl = first["relations_by_fulltype"]["Base.Bowl"]
    assert {(row["food_type_id"], row["role"]) for row in bowl} == {
        ("Salad", "base_item"),
        ("FruitSalad", "base_item"),
    }
    bread = first["relations_by_fulltype"]["Base.BreadSlices"]
    assert {(row["food_type_id"], row["role"]) for row in bread} == {
        ("Burger", "base_item"),
        ("Sandwich", "base_item"),
        ("Soup", "ingredient"),
    }
    for relation in [*water_pot, *bowl]:
        assert relation["conditions"] == []
        assert relation["provenance"][0]["source_role"] == "definition_base_item"
    assert {row["reason"] for row in first["review"]} == {
        "food_type_definition_missing",
        "malformed_token",
    }
    assert first["non_target_tokens"][0]["reason"] == "obsolete_item"
    for full_type, relations in first["relations_by_fulltype"].items():
        for relation in relations:
            assert relation["full_type"] == full_type
            assert relation["source_full_type"] == full_type
            assert relation["target_id"] == relation["food_type_id"]
            assert relation["relation_id"].startswith("qg.evolved_recipe.")
            assert not evolved_recipe.FORBIDDEN_FIXED_RECIPE_FIELDS.intersection(relation)


def test_unknown_duplicate_locale_policy_stays_out_of_public_runtime(
    tmp_path: Path, monkeypatch
) -> None:
    _source_fixture(tmp_path)
    monkeypatch.setattr(
        evolved_recipe, "CONFIRMED_FIRST_WINS_TRANSLATOR_SHA256", set()
    )
    monkeypatch.setattr(
        evolved_recipe, "STANDALONE_TARGET_LABELS", FIXTURE_TARGET_LABELS
    )

    owner = evolved_recipe.build_owner(tmp_path, tmp_path)
    assert owner["locale_resolution"]["policy_confirmed"] is False
    assert {row["reason"] for row in owner["review"]} >= {
        "locale_duplicate_policy_unconfirmed"
    }
    assert "Base.Pepper" not in owner["relations_by_fulltype"]
    assert [
        relation["food_type_id"]
        for relation in owner["relations_by_fulltype"]["Base.Apple"]
    ] == ["Stew"]
    assert [
        relation["food_type_id"]
        for relation in owner["relations_by_fulltype"]["Base.WaterPot"]
    ] == ["Stew"]
    assert owner["census"]["definition_base_review_count"] == 1


def test_canonical_owner_includes_all_definition_base_relations() -> None:
    owner = evolved_recipe.load_owner(
        evolved_recipe.DEFAULT_REPOSITORY_ROOT / evolved_recipe.OWNER_RELATIVE_PATH
    )
    census = owner["census"]
    assert census["definition_base_occurrence_count"] == 38
    assert census["definition_base_relation_count"] == 38
    assert census["definition_base_review_count"] == 0
    assert census["unique_definition_base_fulltype_count"] == 32
    assert census["non_food_definition_base_occurrence_count"] == 17
    assert census["unique_non_food_definition_base_fulltype_count"] == 13
    assert census["definition_base_item_type_occurrences"] == {
        "Drainable": 7,
        "Food": 21,
        "Normal": 8,
        "Weapon": 2,
    }
    assert owner["standalone_target_labels"]["Beer"] == {
        "KO": "텀블러에 담긴 맥주",
        "EN": "Beer in a tumbler",
    }
    assert len(owner["standalone_target_labels"]) == 38
    assert owner["standalone_target_labels"]["Beverage"]["KO"] == "텀블러에 담긴 음료"
    assert owner["standalone_target_labels"]["HotDrink"]["KO"] == "머그잔에 담긴 음료"
    assert owner["standalone_target_labels"]["PastaPan"]["KO"] == "소스팬에 담긴 파스타"
    assert owner["standalone_target_labels"]["RicePot"]["KO"] == "냄비에 담긴 밥"
    assert owner["standalone_target_labels"]["Beverage"] != (
        owner["standalone_target_labels"]["Beverage2"]
    )
    assert owner["standalone_target_labels"]["PastaPan"] != (
        owner["standalone_target_labels"]["PastaPot"]
    )
    assert owner["standalone_target_labels"]["Stir fry"] != (
        owner["standalone_target_labels"]["Stir fry Griddle Pan"]
    )
    observed_actions = set()
    for full_type, relations in owner["relations_by_fulltype"].items():
        assert [row["canonical_ordinal"] for row in relations] == list(
            range(1, len(relations) + 1)
        )
        for relation in relations:
            assert relation["source_full_type"] == full_type
            assert relation["target_id"] == relation["food_type_id"]
            observed_actions.add((relation["role"], tuple(relation["conditions"])))
            for locale in evolved_recipe.SUPPORTED_LOCALES:
                assert relation["display_by_locale"][locale] == (
                    relation["target_label_by_locale"][locale]
                    + " · "
                    + relation["action_by_locale"][locale]
                )
            assert " — " not in relation["display_by_locale"]["EN"]
            assert " — " not in relation["display_by_locale"]["KO"]
    assert observed_actions == set(evolved_recipe.ACTION_PHRASES)

    assert {
        (row["food_type_id"], row["role"])
        for row in owner["relations_by_fulltype"]["Base.Bowl"]
    } == {("FruitSalad", "base_item"), ("Salad", "base_item")}
    assert {
        (row["food_type_id"], row["role"])
        for row in owner["relations_by_fulltype"]["Base.WaterPot"]
    } == {("Soup", "base_item"), ("Stew", "base_item")}
    bread = {
        (row["food_type_id"], row["role"])
        for row in owner["relations_by_fulltype"]["Base.BreadSlices"]
    }
    assert {
        ("Sandwich", "base_item"),
        ("Burger", "base_item"),
        ("Salad", "ingredient"),
        ("Soup", "ingredient"),
        ("Stew", "ingredient"),
    } <= bread
    salt_beer = next(
        row
        for row in owner["relations_by_fulltype"]["Base.Salt"]
        if row["food_type_id"] == "Beer"
    )
    assert salt_beer["display_by_locale"] == {
        "KO": "텀블러에 담긴 맥주 · 양념으로 추가 가능",
        "EN": "Beer in a tumbler · Can be added as seasoning",
    }


def test_candidate_projection_is_deterministic_and_owner_traced(
    tmp_path: Path, monkeypatch
) -> None:
    source_root = tmp_path / "source"
    repository_root = tmp_path / "repository"
    repository_root.mkdir()
    translator = _source_fixture(source_root, repository_root)
    monkeypatch.setattr(
        evolved_recipe,
        "CONFIRMED_FIRST_WINS_TRANSLATOR_SHA256",
        {hashlib.sha256(translator).hexdigest()},
    )
    monkeypatch.setattr(
        evolved_recipe, "STANDALONE_TARGET_LABELS", FIXTURE_TARGET_LABELS
    )
    owner_path = tmp_path / "owner.json"
    evolved_recipe.write_owner(source_root, owner_path, repository_root)
    candidate_a = tmp_path / "candidate-a"
    candidate_b = tmp_path / "candidate-b"

    manifest_a = evolved_recipe.generate_candidate(
        owner_path, candidate_a, repository_root
    )
    manifest_b = evolved_recipe.generate_candidate(
        owner_path, candidate_b, repository_root
    )
    assert manifest_a == manifest_b
    assert evolved_recipe.validate_candidate(
        owner_path, candidate_a, repository_root
    ) == manifest_a
    assert evolved_recipe.validate_candidate(
        owner_path, candidate_b, repository_root
    ) == manifest_b

    runtime_a = (candidate_a / evolved_recipe.RUNTIME_RELATIVE_PATH).read_bytes()
    runtime_b = (candidate_b / evolved_recipe.RUNTIME_RELATIVE_PATH).read_bytes()
    assert runtime_a == runtime_b
    assert manifest_a["schema_version"] == "iris-layer4-evolved-recipe-candidate-v7"
    assert b"recipe_nav_ref" not in runtime_a
    assert b"recipe_id" not in runtime_a
    assert b"rule_id" not in runtime_a
    assert b"ResultItem" not in runtime_a
    assert all(byte < 128 for byte in runtime_a)
    assert "텀블러".encode("utf-8") not in runtime_a

    runtime_script = f"""
local lookup = assert(dofile([[{(candidate_a / evolved_recipe.RUNTIME_RELATIVE_PATH).as_posix()}]]))
local apple = lookup.get("Base.Apple").relations
local pepper = lookup.get("Base.Pepper").relations
local waterPot = lookup.get("Base.WaterPot").relations
assert(apple[1].source_full_type == "Base.Apple")
assert(apple[1].target_id == "Soup")
assert(apple[1].canonical_ordinal == 1)
assert(apple[1].target_label_by_locale.KO == "수프")
assert(apple[1].action_by_locale.KO == "재료로 추가 가능")
assert(apple[1].action_key == "ingredient:none")
io.write(apple[1].display_by_locale.KO, string.char(31))
io.write(apple[2].display_by_locale.KO, string.char(31))
io.write(pepper[1].display_by_locale.KO, string.char(31))
io.write(waterPot[1].display_by_locale.KO)
"""
    runtime_result = subprocess.run(
        ["lua", "-e", runtime_script], capture_output=True, check=True
    )
    assert runtime_result.stdout.split(b"\x1f") == [
        "수프 · 재료로 추가 가능".encode("utf-8"),
        "스튜 · 익힌 뒤 재료로 추가 가능".encode("utf-8"),
        "수프 · 양념으로 추가 가능".encode("utf-8"),
        "수프 · 조리 시작에 사용".encode("utf-8"),
    ]

    escape_sample = '텀블러 — 향신료 · 익힌 뒤 "인용" \\ 경로\n다음 줄'
    literal_result = subprocess.run(
        ["lua", "-e", f"io.write({evolved_recipe.lua_string(escape_sample)})"],
        capture_output=True,
        check=True,
    )
    assert literal_result.stdout.replace(b"\r\n", b"\n") == escape_sample.encode(
        "utf-8"
    )

    package_output = tmp_path / "package"
    package_mod = package_output / "Iris"
    _write(package_mod / "mod.info", "name=Iris\n")
    _write(
        package_output / "Iris.package_manifest.sha256.json",
        '{"schema_version":"iris-package-manifest-v1","file_count":0,"files":[]}\n',
    )
    package_record = evolved_recipe.stage_candidate_package(
        owner_path, candidate_a, package_output, repository_root
    )
    packaged_runtime = (
        package_mod / evolved_recipe.RUNTIME_RELATIVE_PATH.relative_to("Iris")
    )
    assert packaged_runtime.read_bytes() == runtime_a
    assert package_record["runtime_sha256"] == manifest_a["runtime_sha256"]
