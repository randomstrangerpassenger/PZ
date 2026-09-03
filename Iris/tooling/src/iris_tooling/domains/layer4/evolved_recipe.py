"""Build 41 EvolvedRecipe source accounting and typed runtime projection.

The producer owns only source-proven item-to-food-type relations.  It does not
flatten evolved recipes into fixed recipes and never creates recipe navigation.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any, Iterable, Sequence

from iris_tooling.domains.tooltip_static_data_projection.serialization import lua_string


SCHEMA_VERSION = "iris-layer4-evolved-recipe-owner-v3"
CANDIDATE_SCHEMA_VERSION = "iris-layer4-evolved-recipe-candidate-v6"
DEFAULT_REPOSITORY_ROOT = Path(__file__).resolve().parents[6]
OWNER_RELATIVE_PATH = Path(
    "Iris/build/description/v2/data/evolved_recipe_owner.b41.json"
)
RUNTIME_RELATIVE_PATH = Path(
    "Iris/media/lua/client/Iris/Data/IrisEvolvedRecipeLookup.lua"
)
CANDIDATE_MANIFEST_NAME = "candidate_manifest.json"
ITEM_INVENTORY_RELATIVE_PATH = Path("Iris/input/items_itemscript.json")

ITEM_SOURCE_PATHS = (
    Path("media/scripts/items_food.txt"),
    Path("media/scripts/farming.txt"),
)
DEFINITION_SOURCE_PATH = Path("media/scripts/evolvedrecipes.txt")
LOCALE_SOURCE_PATHS = {
    "EN": Path("media/lua/shared/Translate/EN/ContextMenu_EN.txt"),
    "KO": Path("media/lua/shared/Translate/KO/ContextMenu_KO.txt"),
}
SEMANTIC_SOURCE_PATHS = (
    Path("media/lua/client/ISUI/ISInventoryPaneContextMenu.lua"),
    Path("media/lua/client/TimedActions/ISAddItemInRecipe.lua"),
)
TRANSLATOR_CLASS_PATH = Path("zombie/core/Translator.class")
CONFIRMED_FIRST_WINS_TRANSLATOR_SHA256 = {
    "b09aeeb6d473eacd2cc4bc1ce0176a1aed29b4f3d0bf56203fc2c90e9d54fdbf"
}
SUPPORTED_LOCALES = ("EN", "KO")
SUPPORTED_ROLES = {"base_item", "ingredient", "spice"}
SUPPORTED_CONDITIONS = {"cooked"}
FORBIDDEN_FIXED_RECIPE_FIELDS = {
    "rule_id",
    "recipe_id",
    "recipe_nav_ref",
    "result_item",
    "ResultItem",
}
PLANNED_BASELINE = {
    "lexical_occurrences_by_source": {
        "media/scripts/items_food.txt": 333,
        "media/scripts/farming.txt": 14,
    },
    "active_property_row_count": 226,
    "raw_token_count": 2187,
    "definition_count": 38,
}

STANDALONE_TARGET_LABELS = {
    "Beer": {"KO": "텀블러에 담긴 맥주", "EN": "beer in a tumbler"},
    "Beer2": {"KO": "컵에 담긴 맥주", "EN": "beer in a cup"},
    "Beverage": {"KO": "텀블러 음료", "EN": "beverage in a tumbler"},
    "Beverage2": {"KO": "컵 음료", "EN": "beverage in a cup"},
    "Bread": {"KO": "빵", "EN": "bread"},
    "Burger": {"KO": "버거", "EN": "a burger"},
    "Burrito": {"KO": "부리토", "EN": "a burrito"},
    "Cake": {"KO": "케이크", "EN": "a cake"},
    "ConeIcecream": {"KO": "아이스크림 콘", "EN": "an ice cream cone"},
    "FruitSalad": {"KO": "과일 샐러드", "EN": "fruit salad"},
    "HotDrink": {"KO": "머그 음료", "EN": "a drink in a mug"},
    "HotDrinkRed": {"KO": "빨간 머그 음료", "EN": "a drink in a red mug"},
    "HotDrinkSpiffo": {"KO": "스피포 머그 음료", "EN": "a drink in a Spiffo mug"},
    "HotDrinkTea": {"KO": "찻잔 음료", "EN": "a drink in a teacup"},
    "HotDrinkWhite": {"KO": "하얀 머그 음료", "EN": "a drink in a white mug"},
    "Muffin": {"KO": "머핀", "EN": "muffins"},
    "Oatmeal": {"KO": "오트밀 한 그릇", "EN": "a bowl of oatmeal"},
    "Omelette": {"KO": "오믈렛", "EN": "an omelette"},
    "Pancakes": {"KO": "팬케이크", "EN": "pancakes"},
    "PastaPan": {"KO": "소스팬 파스타", "EN": "pasta in a saucepan"},
    "PastaPot": {"KO": "냄비 파스타", "EN": "pasta in a cooking pot"},
    "Pie": {"KO": "세이보리 파이", "EN": "a savory pie"},
    "PieSweet": {"KO": "달콤한 파이", "EN": "a sweet pie"},
    "Pizza": {"KO": "피자", "EN": "a pizza"},
    "RicePan": {"KO": "소스팬 밥", "EN": "rice in a saucepan"},
    "RicePot": {"KO": "냄비 밥", "EN": "rice in a cooking pot"},
    "Roasted Vegetables": {"KO": "구운 채소", "EN": "roasted vegetables"},
    "Salad": {"KO": "샐러드", "EN": "a salad"},
    "Sandwich": {"KO": "식빵 샌드위치", "EN": "a sandwich"},
    "Sandwich Baguette": {"KO": "바게트 샌드위치", "EN": "a baguette sandwich"},
    "Soup": {"KO": "수프", "EN": "soup"},
    "Stew": {"KO": "스튜", "EN": "stew"},
    "Stir fry": {"KO": "프라이팬 볶음", "EN": "stir-fry in a frying pan"},
    "Stir fry Griddle Pan": {"KO": "그리들 팬 볶음", "EN": "stir-fry on a griddle pan"},
    "Taco": {"KO": "타코", "EN": "a taco"},
    "Toast": {"KO": "토스트", "EN": "toast"},
    "Waffles": {"KO": "와플", "EN": "waffles"},
    "WineInGlass": {"KO": "와인잔에 담긴 와인", "EN": "wine in a glass"},
}


class EvolvedRecipeError(RuntimeError):
    pass


@dataclass(frozen=True)
class NamedBlock:
    name: str
    header_start: int
    body_start: int
    body_end: int


@dataclass(frozen=True)
class ItemPropertyRow:
    full_type: str
    source: str
    item_line: int
    property_line: int
    raw_value: str
    spice_value: str | None
    obsolete: bool


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _read_text(path: Path) -> tuple[bytes, str]:
    try:
        raw = path.read_bytes()
        encoding = "utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
        return raw, raw.decode(encoding)
    except (OSError, UnicodeDecodeError) as exc:
        raise EvolvedRecipeError(f"cannot read Build 41 source {path}: {exc}") from exc


def _source_record(source_root: Path, relative_path: Path) -> dict[str, Any]:
    path = source_root / relative_path
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise EvolvedRecipeError(f"cannot read Build 41 source {path}: {exc}") from exc
    return {
        "path": relative_path.as_posix(),
        "bytes": len(raw),
        "sha256": _sha256_bytes(raw),
    }


def _load_item_inventory(
    repository_root: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    path = repository_root.resolve() / ITEM_INVENTORY_RELATIVE_PATH
    try:
        raw = path.read_bytes()
        value = json.loads(raw.decode("utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvolvedRecipeError(f"cannot load item inventory {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvolvedRecipeError("item inventory must be an object")
    items: dict[str, dict[str, Any]] = {}
    for full_type, item in value.items():
        if (
            not isinstance(full_type, str)
            or not full_type
            or not isinstance(item, dict)
            or item.get("FullType") != full_type
            or not isinstance(item.get("Type"), str)
            or not item["Type"]
        ):
            raise EvolvedRecipeError(f"invalid item inventory row: {full_type!r}")
        items[full_type] = item
    return items, {
        "repository_path": ITEM_INVENTORY_RELATIVE_PATH.as_posix(),
        "bytes": len(raw),
        "sha256": _sha256_bytes(raw),
        "item_count": len(items),
    }


def _mask_comments(text: str) -> str:
    """Replace comments with spaces while preserving offsets and newlines."""

    output = list(text)
    index = 0
    state = "code"
    quote = ""
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if state == "block":
            if char == "*" and following == "/":
                output[index] = " "
                output[index + 1] = " "
                index += 2
                state = "code"
                continue
            if char not in "\r\n":
                output[index] = " "
            index += 1
            continue
        if state == "line":
            if char in "\r\n":
                state = "code"
            else:
                output[index] = " "
            index += 1
            continue
        if state == "string":
            if char == "\\":
                index += 2
                continue
            if char == quote:
                state = "code"
            index += 1
            continue
        if char in {'"', "'"}:
            state = "string"
            quote = char
            index += 1
            continue
        if char == "/" and following == "*":
            output[index] = " "
            output[index + 1] = " "
            index += 2
            state = "block"
            continue
        if char == "/" and following == "/":
            output[index] = " "
            output[index + 1] = " "
            index += 2
            state = "line"
            continue
        index += 1
    if state == "block":
        raise EvolvedRecipeError("unterminated block comment in Build 41 script")
    return "".join(output)


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _matching_brace(text: str, opening: int, limit: int) -> int:
    depth = 0
    for index in range(opening, limit):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    raise EvolvedRecipeError(
        f"unclosed block beginning at line {_line_number(text, opening)}"
    )


def _named_blocks(
    text: str,
    keyword: str,
    start: int = 0,
    end: int | None = None,
    *,
    spaced_name: bool = False,
) -> list[NamedBlock]:
    limit = len(text) if end is None else end
    name_pattern = r"([^\r\n{]+?)" if spaced_name else r"([^\s{]+)"
    pattern = re.compile(
        rf"(?m)^[ \t]*{re.escape(keyword)}[ \t]+{name_pattern}[ \t]*"
        rf"(?:\r?\n[ \t]*)?\{{"
    )
    blocks: list[NamedBlock] = []
    for match in pattern.finditer(text, start, limit):
        opening = match.end() - 1
        closing = _matching_brace(text, opening, limit)
        blocks.append(
            NamedBlock(
                name=match.group(1).strip(),
                header_start=match.start(),
                body_start=opening + 1,
                body_end=closing,
            )
        )
    return blocks


def _field_occurrences(
    text: str,
    block: NamedBlock,
    field_name: str,
    separator: str,
) -> list[tuple[str, int]]:
    pattern = re.compile(
        rf"(?m)^[ \t]*{re.escape(field_name)}[ \t]*{re.escape(separator)}"
        rf"[ \t]*([^,\r\n]*)[ \t]*,?[ \t]*\r?$"
    )
    return [
        (match.group(1).strip(), _line_number(text, match.start()))
        for match in pattern.finditer(text, block.body_start, block.body_end)
    ]


def _single_field_value(
    occurrences: list[tuple[str, int]], field_name: str, full_type: str
) -> str | None:
    if not occurrences:
        return None
    values = {value for value, _line in occurrences}
    if len(values) != 1:
        raise EvolvedRecipeError(
            f"{full_type}: conflicting {field_name} values: {sorted(values)}"
        )
    return occurrences[0][0]


def _parse_item_source(
    source_root: Path, relative_path: Path
) -> tuple[list[ItemPropertyRow], dict[str, Any]]:
    raw, text = _read_text(source_root / relative_path)
    masked = _mask_comments(text)
    rows: list[ItemPropertyRow] = []
    for module in _named_blocks(masked, "module"):
        for item in _named_blocks(
            masked, "item", module.body_start, module.body_end
        ):
            full_type = f"{module.name}.{item.name}"
            evolved = _field_occurrences(masked, item, "EvolvedRecipe", "=")
            if not evolved:
                continue
            spice = _single_field_value(
                _field_occurrences(masked, item, "Spice", "="),
                "Spice",
                full_type,
            )
            obsolete_value = _single_field_value(
                _field_occurrences(masked, item, "OBSOLETE", "="),
                "OBSOLETE",
                full_type,
            )
            obsolete = str(obsolete_value or "false").strip().lower() == "true"
            for raw_value, property_line in evolved:
                rows.append(
                    ItemPropertyRow(
                        full_type=full_type,
                        source=relative_path.as_posix(),
                        item_line=_line_number(masked, item.header_start),
                        property_line=property_line,
                        raw_value=raw_value,
                        spice_value=spice,
                        obsolete=obsolete,
                    )
                )
    lexical = text.count("EvolvedRecipe")
    name_surface = text.count("EvolvedRecipeName")
    inactive_or_commented = lexical - name_surface - len(rows)
    if inactive_or_commented < 0:
        raise EvolvedRecipeError(f"{relative_path}: lexical accounting is negative")
    return rows, {
        "path": relative_path.as_posix(),
        "bytes": len(raw),
        "sha256": _sha256_bytes(raw),
        "lexical_occurrence_count": lexical,
        "active_property_row_count": len(rows),
        "non_target_occurrences": {
            "evolved_recipe_name_surface": name_surface,
            "inactive_or_commented_property": inactive_or_commented,
        },
    }


def _parse_definitions(
    source_root: Path,
) -> tuple[dict[str, dict[str, Any]], list[str], dict[str, Any]]:
    raw, text = _read_text(source_root / DEFINITION_SOURCE_PATH)
    masked = _mask_comments(text)
    definitions: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    for module in _named_blocks(masked, "module"):
        for block in _named_blocks(
            masked,
            "evolvedrecipe",
            module.body_start,
            module.body_end,
            spaced_name=True,
        ):
            fields: dict[str, str] = {}
            field_pattern = re.compile(
                r"(?m)^[ \t]*([A-Za-z][A-Za-z0-9_]*)[ \t]*:[ \t]*"
                r"([^,\r\n]*)[ \t]*,?[ \t]*\r?$"
            )
            for match in field_pattern.finditer(masked, block.body_start, block.body_end):
                fields[match.group(1)] = match.group(2).strip()
            if block.name in definitions:
                duplicates.append(block.name)
                continue
            base_items = _field_occurrences(masked, block, "BaseItem", ":")
            if len(base_items) != 1 or not base_items[0][0]:
                raise EvolvedRecipeError(
                    f"{block.name}: definition must have exactly one BaseItem"
                )
            base_item_id, base_item_line = base_items[0]
            base_item_full_type = (
                base_item_id if "." in base_item_id else f"{module.name}.{base_item_id}"
            )
            definitions[block.name] = {
                "food_type_id": block.name,
                "module": module.name,
                "fields": dict(sorted(fields.items())),
                "base_item": {
                    "item_id": base_item_id,
                    "full_type": base_item_full_type,
                    "source_role": "definition_base_item",
                    "provenance": {
                        "source": DEFINITION_SOURCE_PATH.as_posix(),
                        "definition_line": _line_number(masked, block.header_start),
                        "field_line": base_item_line,
                    },
                },
                "provenance": {
                    "source": DEFINITION_SOURCE_PATH.as_posix(),
                    "line": _line_number(masked, block.header_start),
                },
            }
    return definitions, sorted(set(duplicates)), {
        "path": DEFINITION_SOURCE_PATH.as_posix(),
        "bytes": len(raw),
        "sha256": _sha256_bytes(raw),
        "definition_count": len(definitions),
        "duplicate_definition_ids": sorted(set(duplicates)),
    }


def _unescape_locale_value(value: str) -> str:
    return value.replace(r"\"", '"').replace(r"\\", "\\")


def _parse_locale(
    source_root: Path, locale: str
) -> tuple[dict[str, str], dict[str, list[dict[str, Any]]], dict[str, Any]]:
    relative_path = LOCALE_SOURCE_PATHS[locale]
    raw, text = _read_text(source_root / relative_path)
    pattern = re.compile(
        r'(?m)^[ \t]*(ContextMenu_EvolvedRecipe_.+?)[ \t]*=[ \t]*'
        r'"((?:[^"\\]|\\.)*)"[ \t]*,?[ \t]*\r?$'
    )
    effective: dict[str, str] = {}
    occurrences: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for match in pattern.finditer(text):
        key = match.group(1).strip()
        value = _unescape_locale_value(match.group(2))
        record = {
            "line": _line_number(text, match.start()),
            "value": value,
        }
        occurrences[key].append(record)
        if key not in effective:
            effective[key] = value
    duplicates = {
        key: values for key, values in sorted(occurrences.items()) if len(values) > 1
    }
    return effective, duplicates, {
        "path": relative_path.as_posix(),
        "bytes": len(raw),
        "sha256": _sha256_bytes(raw),
        "matched_key_count": sum(len(values) for values in occurrences.values()),
        "unique_key_count": len(effective),
        "duplicate_keys": duplicates,
        "duplicate_policy": "first_definition_wins",
    }


def _relation_identity(
    full_type: str, food_type_id: str, role: str, conditions: Iterable[str]
) -> str:
    material = "\0".join(
        (full_type, food_type_id, role, ",".join(sorted(conditions)))
    ).encode("utf-8")
    return "qg.evolved_recipe." + hashlib.sha256(material).hexdigest()[:20]


def _display(
    target: str, role: str, conditions: Sequence[str], locale: str
) -> str:
    cooked = "cooked" in conditions
    if locale == "KO":
        if role == "base_item":
            return f"{target} 준비에 사용할 수 있음"
        if role == "spice":
            if cooked:
                return f"{target}에 양념으로 넣으려면 먼저 익혀야 함"
            return f"{target}에 양념으로 넣을 수 있음"
        if cooked:
            return f"{target}에 재료로 넣으려면 먼저 익혀야 함"
        return f"{target}에 재료로 넣을 수 있음"
    if role == "base_item":
        return f"Can be used to prepare {target}"
    if role == "spice":
        if cooked:
            return f"Can be added to {target} as seasoning after cooking"
        return f"Can be added to {target} as seasoning"
    if cooked:
        return f"Can be added to {target} as an ingredient after cooking"
    return f"Can be added to {target} as an ingredient"


def _token_provenance(row: ItemPropertyRow, token_index: int) -> dict[str, Any]:
    return {
        "source": row.source,
        "item_line": row.item_line,
        "property_line": row.property_line,
        "token_index": token_index,
    }


def _review(
    row: ItemPropertyRow, token: str, token_index: int, reason: str
) -> dict[str, Any]:
    return {
        "full_type": row.full_type,
        "raw_token": token,
        "reason": reason,
        "provenance": _token_provenance(row, token_index),
    }


def build_owner(
    source_root: Path, repository_root: Path = DEFAULT_REPOSITORY_ROOT
) -> dict[str, Any]:
    source_root = source_root.resolve()
    repository_root = repository_root.resolve()
    item_inventory, item_inventory_record = _load_item_inventory(repository_root)
    item_rows: list[ItemPropertyRow] = []
    item_records: list[dict[str, Any]] = []
    for relative_path in ITEM_SOURCE_PATHS:
        rows, record = _parse_item_source(source_root, relative_path)
        item_rows.extend(rows)
        item_records.append(record)

    definitions, definition_duplicates, definition_record = _parse_definitions(source_root)
    if set(STANDALONE_TARGET_LABELS) != set(definitions):
        raise EvolvedRecipeError(
            "standalone target label registry differs from exact food type definitions: "
            f"missing={sorted(set(definitions) - set(STANDALONE_TARGET_LABELS))}, "
            f"extra={sorted(set(STANDALONE_TARGET_LABELS) - set(definitions))}"
        )
    for food_type_id, target_labels in STANDALONE_TARGET_LABELS.items():
        if set(target_labels) != set(SUPPORTED_LOCALES) or any(
            not isinstance(target_labels[locale], str) or not target_labels[locale]
            for locale in SUPPORTED_LOCALES
        ):
            raise EvolvedRecipeError(
                f"{food_type_id}: standalone target label registry is incomplete"
            )
    definition_base_types: dict[str, str] = {}
    for food_type_id, definition in definitions.items():
        base_full_type = definition["base_item"]["full_type"]
        item = item_inventory.get(base_full_type)
        if item is None:
            raise EvolvedRecipeError(
                f"{food_type_id}: definition BaseItem is absent from exact item inventory: "
                f"{base_full_type}"
            )
        definition_base_types[food_type_id] = item["Type"]
        definition["base_item"]["item_type"] = item["Type"]
    translator_record = _source_record(source_root, TRANSLATOR_CLASS_PATH)
    translator_confirmed = (
        translator_record["sha256"] in CONFIRMED_FIRST_WINS_TRANSLATOR_SHA256
    )
    locales: dict[str, dict[str, str]] = {}
    locale_duplicates: dict[str, dict[str, list[dict[str, Any]]]] = {}
    locale_records: list[dict[str, Any]] = []
    for locale in SUPPORTED_LOCALES:
        effective, duplicates, record = _parse_locale(source_root, locale)
        locales[locale] = effective
        locale_duplicates[locale] = duplicates
        locale_records.append({"locale": locale, **record})

    review_rows: list[dict[str, Any]] = []
    definition_base_review: list[dict[str, Any]] = []
    non_target_tokens: list[dict[str, Any]] = []
    candidates: dict[tuple[str, str, str, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    raw_token_count = 0
    for row in item_rows:
        raw_tokens = row.raw_value.split(";")
        for token_index, raw_token in enumerate(raw_tokens, 1):
            token = raw_token.strip()
            raw_token_count += 1
            if row.obsolete:
                non_target_tokens.append(
                    {
                        "full_type": row.full_type,
                        "raw_token": token,
                        "reason": "obsolete_item",
                        "provenance": _token_provenance(row, token_index),
                    }
                )
                continue
            if not token:
                review_rows.append(_review(row, token, token_index, "empty_token"))
                continue
            if ":" not in token:
                review_rows.append(_review(row, token, token_index, "malformed_token"))
                continue
            food_type_id, amount_and_modifiers = token.rsplit(":", 1)
            food_type_id = food_type_id.strip()
            parts = [value.strip() for value in amount_and_modifiers.split("|")]
            if not food_type_id or not parts[0].isdigit() or int(parts[0]) <= 0:
                review_rows.append(_review(row, token, token_index, "malformed_token"))
                continue
            modifiers = parts[1:]
            if any(not modifier for modifier in modifiers):
                review_rows.append(_review(row, token, token_index, "malformed_modifier"))
                continue
            unknown_modifiers = sorted(set(modifiers) - {"Cooked"})
            if unknown_modifiers:
                review_rows.append(_review(row, token, token_index, "unknown_modifier"))
                continue
            spice_value = (row.spice_value or "false").strip().lower()
            if spice_value not in {"true", "false"}:
                review_rows.append(_review(row, token, token_index, "invalid_spice_value"))
                continue
            if food_type_id not in definitions:
                review_rows.append(
                    _review(row, token, token_index, "food_type_definition_missing")
                )
                continue
            if food_type_id in definition_duplicates:
                review_rows.append(
                    _review(row, token, token_index, "food_type_definition_duplicated")
                )
                continue
            missing_locale = False
            duplicate_unconfirmed = False
            for locale in SUPPORTED_LOCALES:
                key = "ContextMenu_EvolvedRecipe_" + food_type_id
                if not locales[locale].get(key):
                    missing_locale = True
                if key in locale_duplicates[locale] and not translator_confirmed:
                    duplicate_unconfirmed = True
            if missing_locale:
                review_rows.append(_review(row, token, token_index, "locale_missing"))
                continue
            if duplicate_unconfirmed:
                review_rows.append(
                    _review(row, token, token_index, "locale_duplicate_policy_unconfirmed")
                )
                continue
            role = "spice" if spice_value == "true" else "ingredient"
            conditions = tuple(["cooked"] if "Cooked" in modifiers else [])
            candidates[(row.full_type, food_type_id, role, conditions)].append(
                {
                    "full_type": row.full_type,
                    "food_type_id": food_type_id,
                    "role": role,
                    "conditions": conditions,
                    "source_use": int(parts[0]),
                    "raw_token": token,
                    "provenance": _token_provenance(row, token_index),
                }
            )

    relations_by_fulltype: dict[str, list[dict[str, Any]]] = defaultdict(list)
    pass_source_token_count = 0
    deduplicated_source_token_count = 0
    for semantic_key in sorted(candidates):
        grouped = candidates[semantic_key]
        uses = {candidate["source_use"] for candidate in grouped}
        if len(uses) != 1:
            for candidate in grouped:
                review_rows.append(
                    {
                        "full_type": candidate["full_type"],
                        "raw_token": candidate["raw_token"],
                        "reason": "conflicting_use_amount",
                        "provenance": candidate["provenance"],
                    }
                )
            continue
        full_type, food_type_id, role, conditions = semantic_key
        relation_id = _relation_identity(full_type, food_type_id, role, conditions)
        display_by_locale = {}
        for locale in SUPPORTED_LOCALES:
            display_by_locale[locale] = _display(
                STANDALONE_TARGET_LABELS[food_type_id][locale],
                role,
                conditions,
                locale,
            )
        provenance = sorted(
            (candidate["provenance"] for candidate in grouped),
            key=lambda value: (
                value["source"],
                value["property_line"],
                value["token_index"],
            ),
        )
        relations_by_fulltype[full_type].append(
            {
                "relation_id": relation_id,
                "full_type": full_type,
                "food_type_id": food_type_id,
                "role": role,
                "conditions": list(conditions),
                "source_use": next(iter(uses)),
                "decision": "PASS",
                "reason": "exact_source_relation",
                "display_by_locale": display_by_locale,
                "provenance": provenance,
            }
        )
        pass_source_token_count += len(grouped)
        deduplicated_source_token_count += len(grouped) - 1

    definition_base_relation_count = 0
    for food_type_id in sorted(definitions):
        definition = definitions[food_type_id]
        base_item = definition["base_item"]
        full_type = base_item["full_type"]
        key = "ContextMenu_EvolvedRecipe_" + food_type_id
        reason = None
        if any(not locales[locale].get(key) for locale in SUPPORTED_LOCALES):
            reason = "locale_missing"
        elif any(
            key in locale_duplicates[locale] and not translator_confirmed
            for locale in SUPPORTED_LOCALES
        ):
            reason = "locale_duplicate_policy_unconfirmed"
        if reason:
            definition_base_review.append(
                {
                    "full_type": full_type,
                    "food_type_id": food_type_id,
                    "role": "base_item",
                    "reason": reason,
                    "provenance": {
                        **base_item["provenance"],
                        "source_role": base_item["source_role"],
                    },
                }
            )
            continue
        role = "base_item"
        conditions: tuple[str, ...] = ()
        display_by_locale = {
            locale: _display(
                STANDALONE_TARGET_LABELS[food_type_id][locale],
                role,
                conditions,
                locale,
            )
            for locale in SUPPORTED_LOCALES
        }
        relations_by_fulltype[full_type].append(
            {
                "relation_id": _relation_identity(
                    full_type, food_type_id, role, conditions
                ),
                "full_type": full_type,
                "food_type_id": food_type_id,
                "role": role,
                "conditions": [],
                "decision": "PASS",
                "reason": "exact_definition_base_relation",
                "display_by_locale": display_by_locale,
                "provenance": [
                    {
                        **base_item["provenance"],
                        "source_role": base_item["source_role"],
                    }
                ],
            }
        )
        definition_base_relation_count += 1

    for full_type, relations in relations_by_fulltype.items():
        relations.sort(
            key=lambda value: (
                value["food_type_id"],
                value["role"],
                value["conditions"],
                value["relation_id"],
            )
        )

    review_rows.sort(
        key=lambda value: (
            value["full_type"],
            value["provenance"]["source"],
            value["provenance"]["property_line"],
            value["provenance"]["token_index"],
        )
    )
    non_target_tokens.sort(
        key=lambda value: (
            value["full_type"],
            value["provenance"]["source"],
            value["provenance"]["property_line"],
            value["provenance"]["token_index"],
        )
    )
    definition_base_review.sort(
        key=lambda value: (
            value["full_type"],
            value["food_type_id"],
            value["reason"],
        )
    )

    lexical_count = sum(record["lexical_occurrence_count"] for record in item_records)
    active_row_count = len(item_rows)
    non_target_occurrence_count = sum(
        sum(record["non_target_occurrences"].values()) for record in item_records
    )
    pass_relation_count = sum(len(rows) for rows in relations_by_fulltype.values())
    definition_base_full_types = [
        definition["base_item"]["full_type"] for definition in definitions.values()
    ]
    non_food_definition_base_full_types = [
        definitions[food_type_id]["base_item"]["full_type"]
        for food_type_id in definitions
        if definition_base_types[food_type_id] != "Food"
    ]
    census = {
        "lexical_occurrence_count": lexical_count,
        "active_property_row_count": active_row_count,
        "non_target_occurrence_count": non_target_occurrence_count,
        "raw_token_count": raw_token_count,
        "pass_source_token_count": pass_source_token_count,
        "pass_relation_count": pass_relation_count,
        "review_token_count": len(review_rows),
        "non_target_token_count": len(non_target_tokens),
        "deduplicated_source_token_count": deduplicated_source_token_count,
        "unique_public_fulltype_count": len(relations_by_fulltype),
        "definition_count": len(definitions),
        "definition_base_occurrence_count": len(definition_base_full_types),
        "definition_base_relation_count": definition_base_relation_count,
        "definition_base_review_count": len(definition_base_review),
        "unique_definition_base_fulltype_count": len(set(definition_base_full_types)),
        "non_food_definition_base_occurrence_count": len(
            non_food_definition_base_full_types
        ),
        "unique_non_food_definition_base_fulltype_count": len(
            set(non_food_definition_base_full_types)
        ),
        "definition_base_item_type_occurrences": dict(
            sorted(Counter(definition_base_types.values()).items())
        ),
    }
    if lexical_count != active_row_count + non_target_occurrence_count:
        raise EvolvedRecipeError("lexical occurrence accounting failed")
    if raw_token_count != (
        pass_source_token_count + len(review_rows) + len(non_target_tokens)
    ):
        raise EvolvedRecipeError("relation token accounting failed")

    observed_baseline = {
        "lexical_occurrences_by_source": {
            record["path"]: record["lexical_occurrence_count"] for record in item_records
        },
        "active_property_row_count": active_row_count,
        "raw_token_count": raw_token_count,
        "definition_count": len(definitions),
    }
    baseline_delta = {
        "lexical_occurrences_by_source": {
            path: observed_baseline["lexical_occurrences_by_source"].get(path, 0) - expected
            for path, expected in PLANNED_BASELINE[
                "lexical_occurrences_by_source"
            ].items()
        },
        "active_property_row_count": active_row_count
        - PLANNED_BASELINE["active_property_row_count"],
        "raw_token_count": raw_token_count - PLANNED_BASELINE["raw_token_count"],
        "definition_count": len(definitions) - PLANNED_BASELINE["definition_count"],
    }

    source_files = [*item_records, definition_record, *locale_records]
    source_files.extend(
        _source_record(source_root, relative_path)
        for relative_path in SEMANTIC_SOURCE_PATHS
    )
    source_files.append(translator_record)
    owner = {
        "schema_version": SCHEMA_VERSION,
        "status": "source_accounted",
        "owner": "Iris Layer 4 QG",
        "game_source": {
            "branch": "Build 41",
            "source_root": source_root.as_posix(),
            "files": source_files,
        },
        "item_inventory": item_inventory_record,
        "semantic_basis": {
            "item_relation_property": "EvolvedRecipe",
            "role_property": "Spice",
            "definition_relation_field": "BaseItem",
            "definition_participation_role": "base_item",
            "supported_token_modifier": "Cooked",
            "runtime_eligibility_calls": [
                "EvolvedRecipe.getItemsCanBeUse",
                "EvolvedRecipe.needToBeCooked",
                "EvolvedRecipe.addItem",
                "EvolvedRecipe.getItemRecipe",
            ],
            "runtime_limit": "Java eligibility implementation is not reconstructed",
        },
        "locale_resolution": {
            "policy": "first_definition_wins",
            "policy_confirmed": translator_confirmed,
            "confirmation": {
                "class": "zombie.core.Translator",
                "method": "parseFile",
                "behavior": "containsKey guard precedes HashMap.put",
                **translator_record,
            },
            "effective_food_type_labels": {
                locale: {
                    food_type_id: locales[locale][
                        "ContextMenu_EvolvedRecipe_" + food_type_id
                    ]
                    for food_type_id in sorted(definitions)
                    if locales[locale].get(
                        "ContextMenu_EvolvedRecipe_" + food_type_id
                    )
                }
                for locale in SUPPORTED_LOCALES
            },
            "duplicate_keys": locale_duplicates,
        },
        "standalone_target_labels": {
            food_type_id: dict(STANDALONE_TARGET_LABELS[food_type_id])
            for food_type_id in sorted(STANDALONE_TARGET_LABELS)
        },
        "baseline_comparison": {
            "planned": PLANNED_BASELINE,
            "observed": observed_baseline,
            "delta": baseline_delta,
        },
        "census": census,
        "food_type_definitions": {
            key: definitions[key] for key in sorted(definitions)
        },
        "relations_by_fulltype": {
            key: relations_by_fulltype[key] for key in sorted(relations_by_fulltype)
        },
        "review": review_rows,
        "definition_base_review": definition_base_review,
        "non_target_tokens": non_target_tokens,
    }
    validate_owner(owner)
    return owner


def validate_owner(owner: dict[str, Any]) -> dict[str, int]:
    if owner.get("schema_version") != SCHEMA_VERSION:
        raise EvolvedRecipeError("owner schema version mismatch")
    if owner.get("status") != "source_accounted":
        raise EvolvedRecipeError("owner output is not source-accounted")
    census = owner.get("census")
    relations_by_fulltype = owner.get("relations_by_fulltype")
    definitions = owner.get("food_type_definitions")
    locale_resolution = owner.get("locale_resolution")
    target_labels = owner.get("standalone_target_labels")
    item_inventory = owner.get("item_inventory")
    review_rows = owner.get("review")
    definition_base_review = owner.get("definition_base_review")
    non_target_tokens = owner.get("non_target_tokens")
    if (
        not isinstance(census, dict)
        or not isinstance(relations_by_fulltype, dict)
        or not isinstance(definitions, dict)
        or not isinstance(locale_resolution, dict)
        or not isinstance(target_labels, dict)
        or not isinstance(item_inventory, dict)
    ):
        raise EvolvedRecipeError("owner output is structurally incomplete")
    if (
        not isinstance(review_rows, list)
        or not isinstance(definition_base_review, list)
        or not isinstance(non_target_tokens, list)
    ):
        raise EvolvedRecipeError("owner disposition arrays are missing")
    labels = locale_resolution.get("effective_food_type_labels")
    if not isinstance(labels, dict) or any(
        not isinstance(labels.get(locale), dict) for locale in SUPPORTED_LOCALES
    ):
        raise EvolvedRecipeError("owner locale labels are missing")
    if item_inventory.get("repository_path") != ITEM_INVENTORY_RELATIVE_PATH.as_posix():
        raise EvolvedRecipeError("owner item inventory binding is invalid")
    if set(target_labels) != set(definitions) or any(
        not isinstance(target_labels[food_type_id], dict)
        or set(target_labels[food_type_id]) != set(SUPPORTED_LOCALES)
        or any(
            not isinstance(target_labels[food_type_id][locale], str)
            or not target_labels[food_type_id][locale]
            for locale in SUPPORTED_LOCALES
        )
        for food_type_id in target_labels
    ):
        raise EvolvedRecipeError("standalone target label registry is invalid")
    expected_target_labels = {
        food_type_id: dict(STANDALONE_TARGET_LABELS[food_type_id])
        for food_type_id in sorted(STANDALONE_TARGET_LABELS)
    }
    if target_labels != expected_target_labels:
        raise EvolvedRecipeError("standalone target labels differ from audited registry")

    definition_base_full_types: list[str] = []
    non_food_definition_base_full_types: list[str] = []
    definition_base_type_occurrences: Counter[str] = Counter()
    for food_type_id, definition in definitions.items():
        if not isinstance(food_type_id, str) or not isinstance(definition, dict):
            raise EvolvedRecipeError("invalid food type definition")
        base_item = definition.get("base_item")
        if (
            not isinstance(base_item, dict)
            or base_item.get("source_role") != "definition_base_item"
            or not isinstance(base_item.get("full_type"), str)
            or not base_item["full_type"]
            or not isinstance(base_item.get("item_type"), str)
            or not base_item["item_type"]
            or not isinstance(base_item.get("provenance"), dict)
        ):
            raise EvolvedRecipeError(f"{food_type_id}: invalid definition BaseItem")
        definition_base_full_types.append(base_item["full_type"])
        definition_base_type_occurrences[base_item["item_type"]] += 1
        if base_item["item_type"] != "Food":
            non_food_definition_base_full_types.append(base_item["full_type"])

    seen_relations: set[str] = set()
    pass_source_token_count = 0
    definition_base_relation_count = 0
    passed_definition_food_types: set[str] = set()
    relation_count = 0
    for full_type in sorted(relations_by_fulltype):
        relations = relations_by_fulltype[full_type]
        if not isinstance(full_type, str) or not full_type or not isinstance(relations, list):
            raise EvolvedRecipeError("invalid FullType relation collection")
        semantic_order: list[tuple[Any, ...]] = []
        for relation in relations:
            if not isinstance(relation, dict):
                raise EvolvedRecipeError(f"{full_type}: relation must be an object")
            forbidden = FORBIDDEN_FIXED_RECIPE_FIELDS.intersection(relation)
            if forbidden:
                raise EvolvedRecipeError(
                    f"{full_type}: EvolvedRecipe relation has fixed Recipe fields {sorted(forbidden)}"
                )
            if relation.get("decision") != "PASS" or relation.get("full_type") != full_type:
                raise EvolvedRecipeError(f"{full_type}: non-PASS public relation")
            food_type_id = relation.get("food_type_id")
            role = relation.get("role")
            conditions = relation.get("conditions")
            display_by_locale = relation.get("display_by_locale")
            provenance = relation.get("provenance")
            if not isinstance(food_type_id, str) or not food_type_id:
                raise EvolvedRecipeError(f"{full_type}: blank food type")
            if role not in SUPPORTED_ROLES:
                raise EvolvedRecipeError(f"{full_type}/{food_type_id}: invalid role")
            if (
                not isinstance(conditions, list)
                or conditions != sorted(set(conditions))
                or not set(conditions).issubset(SUPPORTED_CONDITIONS)
            ):
                raise EvolvedRecipeError(
                    f"{full_type}/{food_type_id}: invalid relation conditions"
                )
            expected_identity = _relation_identity(
                full_type, food_type_id, role, conditions
            )
            identity = relation.get("relation_id")
            if identity != expected_identity or identity in seen_relations:
                raise EvolvedRecipeError(
                    f"{full_type}/{food_type_id}: unstable or duplicate relation identity"
                )
            seen_relations.add(identity)
            if (
                not isinstance(display_by_locale, dict)
                or set(display_by_locale) != set(SUPPORTED_LOCALES)
                or any(
                    not isinstance(display_by_locale[locale], str)
                    or not display_by_locale[locale]
                    for locale in SUPPORTED_LOCALES
                )
            ):
                raise EvolvedRecipeError(
                    f"{full_type}/{food_type_id}: KO/EN display parity failed"
                )
            for locale in SUPPORTED_LOCALES:
                display = display_by_locale[locale]
                if f"({food_type_id})" in display:
                    raise EvolvedRecipeError(
                        f"{full_type}/{food_type_id}: internal food type leaked into {locale} display"
                    )
                if "Evolved" in display:
                    raise EvolvedRecipeError(
                        f"{full_type}/{food_type_id}: internal Evolved term leaked into {locale} display"
                    )
            if not isinstance(provenance, list) or not provenance:
                raise EvolvedRecipeError(
                    f"{full_type}/{food_type_id}: provenance is missing"
                )
            source_label_missing = any(
                not isinstance(labels[locale].get(food_type_id), str)
                or not labels[locale][food_type_id]
                for locale in SUPPORTED_LOCALES
            )
            if source_label_missing or any(
                display_by_locale[locale]
                != _display(
                    target_labels[food_type_id][locale], role, conditions, locale
                )
                for locale in SUPPORTED_LOCALES
            ):
                raise EvolvedRecipeError(
                    f"{full_type}/{food_type_id}: display is not source-derived"
                )
            if role == "base_item":
                definition = definitions.get(food_type_id)
                base_item = definition.get("base_item") if isinstance(definition, dict) else None
                if (
                    conditions
                    or relation.get("reason") != "exact_definition_base_relation"
                    or "source_use" in relation
                    or not isinstance(base_item, dict)
                    or base_item.get("full_type") != full_type
                    or len(provenance) != 1
                    or provenance[0].get("source_role") != "definition_base_item"
                    or food_type_id in passed_definition_food_types
                ):
                    raise EvolvedRecipeError(
                        f"{full_type}/{food_type_id}: invalid definition BaseItem relation"
                    )
                passed_definition_food_types.add(food_type_id)
                definition_base_relation_count += 1
            else:
                if (
                    relation.get("reason") != "exact_source_relation"
                    or not isinstance(relation.get("source_use"), int)
                    or relation["source_use"] <= 0
                ):
                    raise EvolvedRecipeError(
                        f"{full_type}/{food_type_id}: invalid item-property relation"
                    )
                pass_source_token_count += len(provenance)
            relation_count += 1
            semantic_order.append((food_type_id, role, conditions, identity))
        if semantic_order != sorted(semantic_order):
            raise EvolvedRecipeError(f"{full_type}: public relation order is unstable")
    if census.get("pass_relation_count") != relation_count:
        raise EvolvedRecipeError("PASS relation census mismatch")
    if census.get("pass_source_token_count") != pass_source_token_count:
        raise EvolvedRecipeError("PASS source-token census mismatch")
    if census.get("review_token_count") != len(review_rows):
        raise EvolvedRecipeError("REVIEW token census mismatch")
    reviewed_definition_food_types: set[str] = set()
    for row in definition_base_review:
        if (
            not isinstance(row, dict)
            or row.get("role") != "base_item"
            or row.get("food_type_id") not in definitions
            or row["food_type_id"] in reviewed_definition_food_types
            or row["food_type_id"] in passed_definition_food_types
            or row.get("full_type")
            != definitions[row["food_type_id"]]["base_item"]["full_type"]
            or row.get("reason")
            not in {"locale_missing", "locale_duplicate_policy_unconfirmed"}
            or not isinstance(row.get("provenance"), dict)
            or row["provenance"].get("source_role") != "definition_base_item"
        ):
            raise EvolvedRecipeError("invalid definition BaseItem REVIEW disposition")
        reviewed_definition_food_types.add(row["food_type_id"])
    if passed_definition_food_types | reviewed_definition_food_types != set(definitions):
        raise EvolvedRecipeError("definition BaseItem dispositions do not close")
    if census.get("definition_base_occurrence_count") != len(definitions):
        raise EvolvedRecipeError("definition BaseItem occurrence census mismatch")
    if census.get("definition_base_relation_count") != definition_base_relation_count:
        raise EvolvedRecipeError("definition BaseItem PASS census mismatch")
    if census.get("definition_base_review_count") != len(definition_base_review):
        raise EvolvedRecipeError("definition BaseItem REVIEW census mismatch")
    if census.get("unique_definition_base_fulltype_count") != len(
        set(definition_base_full_types)
    ):
        raise EvolvedRecipeError("unique definition BaseItem census mismatch")
    if census.get("non_food_definition_base_occurrence_count") != len(
        non_food_definition_base_full_types
    ):
        raise EvolvedRecipeError("non-Food definition BaseItem occurrence mismatch")
    if census.get("unique_non_food_definition_base_fulltype_count") != len(
        set(non_food_definition_base_full_types)
    ):
        raise EvolvedRecipeError("unique non-Food definition BaseItem census mismatch")
    if census.get("definition_base_item_type_occurrences") != dict(
        sorted(definition_base_type_occurrences.items())
    ):
        raise EvolvedRecipeError("definition BaseItem type census mismatch")
    if census.get("non_target_token_count") != len(non_target_tokens):
        raise EvolvedRecipeError("non-target token census mismatch")
    if census.get("raw_token_count") != (
        pass_source_token_count + len(review_rows) + len(non_target_tokens)
    ):
        raise EvolvedRecipeError("raw token disposition does not close")
    if census.get("lexical_occurrence_count") != (
        census.get("active_property_row_count", -1)
        + census.get("non_target_occurrence_count", -1)
    ):
        raise EvolvedRecipeError("lexical occurrence disposition does not close")
    return {
        "pass_relation_count": relation_count,
        "definition_base_relation_count": definition_base_relation_count,
        "review_token_count": len(review_rows),
        "non_target_token_count": len(non_target_tokens),
        "unique_public_fulltype_count": len(relations_by_fulltype),
    }


def write_owner(
    source_root: Path,
    output_path: Path,
    repository_root: Path = DEFAULT_REPOSITORY_ROOT,
) -> dict[str, Any]:
    owner = build_owner(source_root, repository_root)
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=output_path.name + ".",
        suffix=".tmp",
        dir=output_path.parent,
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
        handle.write(_canonical_json_bytes(owner))
    os.replace(temporary, output_path)
    return owner


def load_owner(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvolvedRecipeError(f"cannot load owner output {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvolvedRecipeError("owner output must be an object")
    validate_owner(value)
    return value


def render_runtime(owner: dict[str, Any]) -> bytes:
    metrics = validate_owner(owner)
    lines = [
        "-- Iris Build 41 EvolvedRecipe lookup",
        "-- Auto-generated from source-accounted Layer 4 QG owner data.",
        f"-- Candidate contract: {CANDIDATE_SCHEMA_VERSION}",
        "-- Fixed Recipe navigation fields are intentionally absent.",
        "local records = {",
    ]
    relations_by_fulltype = owner["relations_by_fulltype"]
    for full_type in sorted(relations_by_fulltype):
        lines.append(f"    [{lua_string(full_type)}] = {{")
        for relation in relations_by_fulltype[full_type]:
            conditions = ", ".join(
                lua_string(value) for value in relation["conditions"]
            )
            display = relation["display_by_locale"]
            lines.append(
                "        { relation_id = "
                + lua_string(relation["relation_id"])
                + ", food_type_id = "
                + lua_string(relation["food_type_id"])
                + ", role = "
                + lua_string(relation["role"])
                + ", conditions = {"
                + conditions
                + "}, display_by_locale = { EN = "
                + lua_string(display["EN"])
                + ", KO = "
                + lua_string(display["KO"])
                + " } },"
            )
        lines.append("    },")
    lines.extend(
        [
            "}",
            "",
            "local IrisEvolvedRecipeLookup = {}",
            "",
            "function IrisEvolvedRecipeLookup.get(fullType)",
            "    if type(fullType) ~= \"string\" or fullType == \"\" then",
            "        return {status = \"fault\", reason = \"invalid_fulltype\", relations = {}}",
            "    end",
            "    local relations = records[fullType]",
            "    if not relations then",
            "        return {status = \"verified_empty\", reason = \"lookup_miss\", relations = {}}",
            "    end",
            "    return {status = \"available\", relations = relations}",
            "end",
            "",
            f"IrisEvolvedRecipeLookup.relationCount = {metrics['pass_relation_count']}",
            f"IrisEvolvedRecipeLookup.fullTypeCount = {metrics['unique_public_fulltype_count']}",
            "",
            "return IrisEvolvedRecipeLookup",
            "",
        ]
    )
    return "\n".join(lines).encode("utf-8")


def _candidate_manifest(owner_bytes: bytes, runtime_bytes: bytes, owner: dict[str, Any]) -> dict[str, Any]:
    metrics = validate_owner(owner)
    return {
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "status": "candidate_not_adopted",
        "owner_sha256": _sha256_bytes(owner_bytes),
        "runtime_path": RUNTIME_RELATIVE_PATH.as_posix(),
        "runtime_sha256": _sha256_bytes(runtime_bytes),
        "metrics": metrics,
    }


def _assert_external(root: Path, repository_root: Path) -> None:
    resolved = root.resolve()
    repository = repository_root.resolve()
    if resolved == repository or repository in resolved.parents or resolved in repository.parents:
        raise EvolvedRecipeError(
            f"candidate root must be external to the repository: {resolved}"
        )


def generate_candidate(
    owner_path: Path, candidate_root: Path, repository_root: Path = DEFAULT_REPOSITORY_ROOT
) -> dict[str, Any]:
    _assert_external(candidate_root, repository_root)
    owner_bytes = owner_path.read_bytes()
    owner = load_owner(owner_path)
    runtime_bytes = render_runtime(owner)
    manifest = _candidate_manifest(owner_bytes, runtime_bytes, owner)
    runtime_path = candidate_root.resolve() / RUNTIME_RELATIVE_PATH
    runtime_path.parent.mkdir(parents=True, exist_ok=True)
    runtime_path.write_bytes(runtime_bytes)
    (candidate_root.resolve() / CANDIDATE_MANIFEST_NAME).write_bytes(
        _canonical_json_bytes(manifest)
    )
    return manifest


def validate_candidate(
    owner_path: Path, candidate_root: Path, repository_root: Path = DEFAULT_REPOSITORY_ROOT
) -> dict[str, Any]:
    _assert_external(candidate_root, repository_root)
    owner_bytes = owner_path.read_bytes()
    owner = load_owner(owner_path)
    expected_runtime = render_runtime(owner)
    expected_manifest = _candidate_manifest(owner_bytes, expected_runtime, owner)
    runtime_path = candidate_root.resolve() / RUNTIME_RELATIVE_PATH
    manifest_path = candidate_root.resolve() / CANDIDATE_MANIFEST_NAME
    try:
        actual_runtime = runtime_path.read_bytes()
        actual_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvolvedRecipeError(f"candidate is incomplete: {exc}") from exc
    if actual_runtime != expected_runtime:
        raise EvolvedRecipeError("candidate runtime bytes differ from owner projection")
    if actual_manifest != expected_manifest:
        raise EvolvedRecipeError("candidate manifest differs from owner projection")
    if any(
        field.encode("utf-8") in actual_runtime
        for field in ("recipe_nav_ref", "recipe_id", "rule_id")
    ):
        raise EvolvedRecipeError("candidate contains synthetic fixed Recipe fields")
    return expected_manifest


def stage_candidate_package(
    owner_path: Path,
    candidate_root: Path,
    package_output_root: Path,
    repository_root: Path = DEFAULT_REPOSITORY_ROOT,
) -> dict[str, Any]:
    candidate_manifest = validate_candidate(
        owner_path, candidate_root, repository_root
    )
    _assert_external(package_output_root, repository_root)
    package_output_root = package_output_root.resolve()
    mod_root = package_output_root / "Iris"
    package_manifest_path = package_output_root / "Iris.package_manifest.sha256.json"
    if not mod_root.is_dir() or not package_manifest_path.is_file():
        raise EvolvedRecipeError(
            "base Iris package and package manifest must be staged before candidate overlay"
        )
    try:
        package_manifest = json.loads(
            package_manifest_path.read_text(encoding="utf-8-sig")
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise EvolvedRecipeError(f"cannot load Iris package manifest: {exc}") from exc
    if not isinstance(package_manifest, dict):
        raise EvolvedRecipeError("Iris package manifest must be an object")

    source = candidate_root.resolve() / RUNTIME_RELATIVE_PATH
    destination = mod_root / RUNTIME_RELATIVE_PATH.relative_to("Iris")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if destination.read_bytes() != source.read_bytes():
        raise EvolvedRecipeError("candidate package runtime byte parity failed")

    files = []
    package_files = sorted(
        (path for path in mod_root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(mod_root).as_posix(),
    )
    for path in package_files:
        raw = path.read_bytes()
        files.append(
            {
                "path": path.relative_to(mod_root).as_posix(),
                "sha256": _sha256_bytes(raw),
                "bytes": len(raw),
            }
        )
    package_manifest["file_count"] = len(files)
    package_manifest["files"] = files
    package_manifest["evolved_recipe_candidate"] = {
        "status": "candidate_not_adopted",
        "owner_sha256": candidate_manifest["owner_sha256"],
        "runtime_path": RUNTIME_RELATIVE_PATH.relative_to("Iris").as_posix(),
        "runtime_sha256": candidate_manifest["runtime_sha256"],
    }
    package_manifest_path.write_bytes(_canonical_json_bytes(package_manifest))
    return package_manifest["evolved_recipe_candidate"]


def adopt_candidate(
    owner_path: Path,
    candidate_root: Path,
    repository_root: Path,
    observed_runtime_sha256: str,
) -> str:
    manifest = validate_candidate(owner_path, candidate_root, repository_root)
    expected_sha256 = manifest["runtime_sha256"]
    if observed_runtime_sha256.lower() != expected_sha256:
        raise EvolvedRecipeError("observed candidate hash does not match candidate runtime")
    source = candidate_root.resolve() / RUNTIME_RELATIVE_PATH
    destination = repository_root.resolve() / RUNTIME_RELATIVE_PATH
    if destination.is_file() and destination.read_bytes() == source.read_bytes():
        return "no-op"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="iris-er-adopt-") as temporary_name:
        temporary_root = Path(temporary_name)
        backup = temporary_root / destination.name
        had_destination = destination.is_file()
        if had_destination:
            shutil.copy2(destination, backup)
        try:
            replacement = destination.with_suffix(destination.suffix + ".tmp")
            shutil.copy2(source, replacement)
            os.replace(replacement, destination)
            if destination.read_bytes() != source.read_bytes():
                raise EvolvedRecipeError("post-adoption byte parity failed")
        except Exception:
            if had_destination:
                shutil.copy2(backup, destination)
            elif destination.exists():
                destination.unlink()
            raise
    return "applied"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    owner = subparsers.add_parser("owner")
    owner.add_argument("--source-root", type=Path, required=True)
    owner.add_argument("--output", type=Path, required=True)
    owner.add_argument(
        "--repository-root", type=Path, default=DEFAULT_REPOSITORY_ROOT
    )

    candidate = subparsers.add_parser("candidate")
    candidate.add_argument("--owner", type=Path, required=True)
    candidate.add_argument("--candidate-root", type=Path, required=True)
    candidate.add_argument(
        "--repository-root", type=Path, default=DEFAULT_REPOSITORY_ROOT
    )

    validate = subparsers.add_parser("validate")
    validate.add_argument("--owner", type=Path, required=True)
    validate.add_argument("--candidate-root", type=Path, required=True)
    validate.add_argument(
        "--repository-root", type=Path, default=DEFAULT_REPOSITORY_ROOT
    )

    package = subparsers.add_parser("package")
    package.add_argument("--owner", type=Path, required=True)
    package.add_argument("--candidate-root", type=Path, required=True)
    package.add_argument("--package-output-root", type=Path, required=True)
    package.add_argument(
        "--repository-root", type=Path, default=DEFAULT_REPOSITORY_ROOT
    )

    adopt = subparsers.add_parser("adopt")
    adopt.add_argument("--owner", type=Path, required=True)
    adopt.add_argument("--candidate-root", type=Path, required=True)
    adopt.add_argument("--repository-root", type=Path, required=True)
    adopt.add_argument("--observed-runtime-sha256", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "owner":
            owner = write_owner(args.source_root, args.output, args.repository_root)
            print("PASS: EvolvedRecipe source-accounted owner output")
            print(json.dumps(owner["census"], sort_keys=True))
        elif args.command == "candidate":
            manifest = generate_candidate(
                args.owner, args.candidate_root, args.repository_root
            )
            print("PASS: EvolvedRecipe candidate generated")
            print(json.dumps(manifest, sort_keys=True))
        elif args.command == "validate":
            manifest = validate_candidate(
                args.owner, args.candidate_root, args.repository_root
            )
            print("PASS: EvolvedRecipe candidate")
            print(json.dumps(manifest, sort_keys=True))
        elif args.command == "package":
            record = stage_candidate_package(
                args.owner,
                args.candidate_root,
                args.package_output_root,
                args.repository_root,
            )
            print("PASS: EvolvedRecipe candidate package staged")
            print(json.dumps(record, sort_keys=True))
        elif args.command == "adopt":
            result = adopt_candidate(
                args.owner,
                args.candidate_root,
                args.repository_root,
                args.observed_runtime_sha256,
            )
            print(f"PASS: EvolvedRecipe guarded adoption {result}")
        else:
            raise EvolvedRecipeError(f"unsupported command {args.command}")
    except (EvolvedRecipeError, OSError) as exc:
        print(f"FAIL: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
