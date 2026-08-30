"""Compile opening-time display variants from existing static/QG owner outputs.

This is a presentation companion to the fixed T2 payload, not a new fact source
or a T1/T2 closeout. Recipe identity and names come from the Menu's QG inputs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from iris_tooling.domains.tooltip_t1.audit import _layer4_candidates, _runtime_rightclick_surfaces
from iris_tooling.domains.tooltip_t1.projection import select_layer4
from .contract import check_surface, load_contract, require
from .serialization import LUA_NAME, lua_bytes, lua_string

DATA_ROOT = Path("Iris/media/lua/client/Iris/Data")
OWNER_ROOT = Path("Iris/build/description/v2/data")
VARIANTS_NAME = "IrisTooltipRecipeVariants.lua"
QUOTED = r'"(?:\\[0-9]{3}|\\["\\]|[^"\\])*"'
# Explicit user disposition for the three current missing KO names. Do not
# silently omit any newly missing name when upstream data changes.
MISSING_NAME_EXCLUSIONS = frozenset({
    "uc.recipe.empty_baking_tray", "uc.recipe.hockeymasksmashbottle",
    "uc.recipe.make_wooden_box_trap",
})


def _decode_literal(value: str) -> str:
    tokens = re.findall(r'\\[0-9]{3}|\\["\\]|[^\\]', value[1:-1])
    raw = bytearray()
    for token in tokens:
        raw.append(int(token[1:]) if token.startswith("\\") and token[1:].isdigit()
                   else ord(token[1:] if token.startswith("\\") else token))
    decoded = raw.decode("utf-8")
    require(lua_string(decoded) == value, "noncanonical Lua string")
    return decoded


def read_static_data(raw: bytes) -> dict:
    """Decode only our canonical literal format; never infer roles from text."""
    data, entry, locale = {}, None, None
    for line in raw.decode("utf-8").splitlines():
        item = re.fullmatch(r"    \[(" + QUOTED + r")\] = \{", line)
        language = re.fullmatch(r"        (ko|en) = (\{\},|\{)", line)
        text = re.fullmatch(r"            (" + QUOTED + r"),", line)
        if item:
            key = _decode_literal(item[1])
            require(key not in data, f"duplicate static FullType: {key}")
            entry = data[key] = {}
        elif language:
            locale = language[1]
            require(entry is not None and locale not in entry, "duplicate/orphan locale")
            entry[locale] = []
        elif text:
            require(entry is not None and locale in entry, "orphan static line")
            entry[locale].append(_decode_literal(text[1]))
        else:
            require(line in {"return {", "}", "    },", "        },"}, "unexpected static syntax")
    require(all(set(row) == {"ko", "en"} for row in data.values()), "missing static locale")
    require(lua_bytes(data) == raw.replace(b"\r\n", b"\n"), "noncanonical static representation")
    return data


def project_recipe_variants(base: dict, usecases: dict, navigation: dict,
                            recipe_surfaces: dict, rightclick_surfaces: dict,
                            contract: dict) -> dict:
    result = {}
    for full_type in sorted(base):
        owner = usecases.get(full_type, {})
        selected, dispositions = select_layer4(_layer4_candidates(owner))
        identities = sorted({row.candidate.interaction_id for row in dispositions
                             if row.candidate.source == "recipe"
                             and row.disposition in {"selected", "excluded_capacity"}})
        if not identities:
            continue
        # Existing structured selection identifies the tail. Text equality is
        # a stale-input guard, not a way of guessing whether a row is Layer 4.
        entry = base[full_type]
        offset = len(entry["ko"]) - len(selected)
        require(offset >= 0 and len(entry["ko"]) == len(entry["en"]), f"{full_type}: bad base rows")
        require(any(row.source == "recipe" for row in selected), f"{full_type}: no selected recipe slot")
        for index, row in enumerate(selected, offset):
            expected = (recipe_surfaces.get(row.interaction_id, {}).get("localized_surfaces", {})
                        if row.source == "recipe" else rightclick_surfaces.get(row.interaction_id, {}))
            require(all(entry[loc][index] == expected.get(loc) for loc in ("ko", "en")),
                    f"{full_type}/{row.interaction_id}: static/QG selection mismatch")
        variants = []
        for identity in identities:
            evidence = [item for item in owner["use_cases"] if item.get("use_case_id") == identity]
            require(evidence and all(any(source.get("source_type") == "recipe_evidence"
                    and source.get("decision") == "PASS" for source in item.get("evidence_sources", []))
                    for item in evidence), f"{full_type}/{identity}: unapproved recipe evidence")
            nav = navigation.get(identity, {})
            require(nav.get("recipe_id") == identity, f"{identity}: recipe navigation identity mismatch")
            complete_names = all(isinstance(nav.get(field), str) and bool(nav[field].strip())
                                 for field in ("translated_name", "original_name"))
            if not complete_names and identity in MISSING_NAME_EXCLUSIONS:
                continue
            variant = {"id": identity}
            for loc, field, label in (("ko", "translated_name", "[레시피] "),
                                      ("en", "original_name", "[Recipe] ")):
                name = nav.get(field)
                require(isinstance(name, str) and bool(name.strip()), f"{identity}/{loc}: missing recipe name")
                surface = label + name
                check_surface(surface, loc, contract, f"{full_type}/{identity}/{loc}")
                rows, added = list(entry[loc][:offset]), False
                for index, row in enumerate(selected, offset):
                    if row.source != "recipe":
                        rows.append(entry[loc][index])
                    elif not added:
                        rows.append(surface)
                        added = True
                require(0 < len(rows) <= 4, f"{full_type}: recipe variant exceeds line budget")
                variant[loc] = rows
            variants.append(variant)
        result[full_type] = {"base": entry, "variants": variants}
        if not variants:
            result[full_type]["without_recipe"] = {
                loc: entry[loc][:offset] + [entry[loc][index] for index, row in enumerate(selected, offset)
                                           if row.source != "recipe"] for loc in ("ko", "en")}
    return result


def variants_bytes(data: dict) -> bytes:
    def arrays(entry, indent):
        return [f"{indent}{loc} = {{" + ", ".join(lua_string(s) for s in entry[loc]) + "},"
                for loc in ("ko", "en")]
    lines = ["-- Generated by tooltip_static_data_projection.recipe_variants; do not edit.", "return {"]
    for key in sorted(data):
        entry = data[key]
        lines.extend([f"    [{lua_string(key)}] = {{", "        base = {"])
        lines.extend(arrays(entry["base"], "            "))
        lines.extend(["        },", "        variants = {"])
        for variant in entry["variants"]:
            lines.extend(["            {", f"                id = {lua_string(variant['id'])},"])
            lines.extend(arrays(variant, "                "))
            lines.append("            },")
        lines.append("        },")
        if "without_recipe" in entry:
            lines.append("        without_recipe = {")
            lines.extend(arrays(entry["without_recipe"], "            "))
            lines.append("        },")
        lines.append("    },")
    lines.append("}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def current_variants(repository: Path) -> dict:
    def owner(name):
        return json.loads((repository / OWNER_ROOT / name).read_text(encoding="utf-8"))
    contract, _ = load_contract(repository)
    return project_recipe_variants(
        read_static_data((repository / DATA_ROOT / LUA_NAME).read_bytes()),
        owner("upstream_usecases_by_fulltype.json")["fulltypes"],
        owner("upstream_recipe_nav_registry.json")["entries"],
        owner("tooltip_t1_layer4_recipe_locale_owner_input.json")["entries"],
        _runtime_rightclick_surfaces(repository), contract,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repository = args.repository_root.resolve()
    output = args.output.resolve()
    require(output.is_relative_to(repository), "recipe presentation output must stay inside repository")
    data = current_variants(repository)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(variants_bytes(data))
    print(f"Recipe presentation: {len(data)} FullTypes, {sum(len(row['variants']) for row in data.values())} variants")


if __name__ == "__main__":
    main()
