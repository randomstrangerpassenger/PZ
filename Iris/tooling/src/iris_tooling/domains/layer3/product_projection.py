"""Build one off-live bilingual Menu/Tooltip/Recipe product from adopted L3.

This consumer owns serialization and binding only. It never selects facts or
rewrites expressions, and does not install into the current source tree.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

from . import expression_results as expression
from iris_tooling.domains.classification.layer2_contract import OWNER_OUTPUT
from iris_tooling.domains.classification.layer2_validator import validate_owner_output
from iris_tooling.domains.layer4.tooltip_t1_d4 import load_recipe_locale_owner_input
from iris_tooling.domains.tooltip_t1.audit import (
    _layer4_candidates, _runtime_rightclick_surfaces, layer2_title_surfaces,
)
from iris_tooling.domains.tooltip_t1.projection import select_layer4
from iris_tooling.domains.tooltip_static_data_projection.contract import (
    AcceptedInput, load_contract, read_handoff, require,
)
from iris_tooling.domains.tooltip_static_data_projection.projection import project
from iris_tooling.domains.tooltip_static_data_projection.recipe_variants import (
    DATA_ROOT, OWNER_ROOT, VARIANTS_NAME, project_recipe_variants,
    read_static_data, variants_bytes,
)
from iris_tooling.domains.tooltip_static_data_projection.serialization import lua_bytes, lua_string

SCHEMA = "iris-layer3-product-v1"
BINDING = {"path": expression.ROOT + "/manifest.json",
           "sha256": "cff8acd83715e70c6e7b82553d47e538c7f75131437491d7cf6781875f5435be"}
GENERATIONS = "IrisLayer3ProductGenerations"
POINTER = "IrisLayer3ProductCurrent.lua"
CODE = "Iris/tooling/src/iris_tooling/domains/layer3/"
CONTRACT = "docs/iris_layer3_product_consumption_contract.md"
LOCALES = ("ko", "en")


def canonical(value):
    return expression.canonical(value)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def local(root: Path, relative: str) -> Path:
    """No external input, traversal, aliases or reparse traversal in a product."""
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts and "\\" not in relative,
            "unsafe product path: " + relative)
    resolved = root.resolve() / path
    require(resolved.resolve().is_relative_to(root.resolve()), "product path escapes repository")
    cursor = resolved
    while cursor != root.resolve():
        require(not cursor.is_symlink() and not cursor.is_junction(), "product reparse path")
        cursor = cursor.parent
    return resolved


def read_json(root, relative):
    return json.loads(local(root, str(relative).replace("\\", "/")).read_bytes())


def binding(root, relative):
    return {"path": relative, "sha256": digest(local(root, relative).read_bytes())}


def new_output(root, output):
    require(not output.exists(), "output must be new")
    if output.is_relative_to(root):
        require(output.is_relative_to(root / ".tmp"), "output overlaps repository source")
        local(root, output.relative_to(root).as_posix())
    else:
        require(not root.is_relative_to(output), "output is repository ancestor")
        require(not {p.lower() for p in output.parts} & {"zomboid", "projectzomboid"}, "live install output forbidden")
    cursor = output
    while cursor != cursor.parent:
        require(not cursor.is_symlink() and not cursor.is_junction(), "output reparse path")
        cursor = cursor.parent


def preserved_slots(root, payload):
    """Reconstitute current structured owner slots; never infer roles from rows.

    The admitted T1 handoff supplies exact support and semantic identities.
    Current owner surfaces are then projected and compared against current Lua.
    A stale *surface* in the old handoff is recorded, not silently called fresh.
    """
    contract, _ = load_contract(root)
    route = read_json(root, "Iris/_docs/authority/iris_current_route_index.json")
    locator = route["tooltip_t1_production_handoff"]
    # A disposable checkout consumes the same explicitly adopted readpoint.
    # Its location is not inferred from an archive, working directory or env.
    # read_handoff below still binds every member, subject and exact support.
    handoff = Path(locator["final_root"])
    require(handoff.is_absolute() and ".." not in handoff.parts, "handoff locator must be absolute")
    require(handoff.resolve() == handoff, "handoff locator alias")
    for name in ("subject_binding.json", "t2_handoff_input.jsonl", "t2_handoff_manifest.json", "axis_separated_final_closeout_record.json"):
        local(handoff, name)
    accepted = read_handoff(handoff, locator, support_count=contract["support_count"],
                            support_sha256=contract["support_sha256"])
    validate_owner_output(root)
    classification = read_json(root, OWNER_OUTPUT.as_posix())
    classified = {r["full_type"]: r for r in classification["rows"]}
    silence = {r["full_type"] for r in classification["layer2_display_silence_entries"]}
    usecases = read_json(root, (OWNER_ROOT / "upstream_usecases_by_fulltype.json").as_posix())["fulltypes"]
    navigation = read_json(root, (OWNER_ROOT / "upstream_recipe_nav_registry.json").as_posix())["entries"]
    recipe = load_recipe_locale_owner_input(root)
    rightclick = _runtime_rightclick_surfaces(root)
    fixed = read_static_data(local(root, (DATA_ROOT / "IrisTooltipStaticData.lua").as_posix()).read_bytes())
    support = {r["full_type"] for r in accepted.rows}
    targets = {r["item_id"] for r in payload["items"]}
    require(len(targets) == 2105 and len(support) == 2280 and targets <= support
            and len(support - targets) == 175 and set(fixed) == support, "exact support/target mismatch")
    rows, drift = [], []
    for old in accepted.rows:
        key = old["full_type"]
        slots = []
        cls = classified.get(key)
        if cls and cls["terminal_state"] == "resolved":
            slots.append({"slot_id": "S1", "semantic_identity": cls["classification_identity"],
                          "localized_surfaces": layer2_title_surfaces(cls)})
        else:
            require(key in silence, key + ": missing classification absence")
        selected, _ = select_layer4(_layer4_candidates(usecases.get(key, {})))
        for index, item in enumerate(selected, 3):
            surfaces = (recipe[item.interaction_id]["localized_surfaces"] if item.source == "recipe"
                        else rightclick[item.interaction_id])
            slots.append({"slot_id": "S" + str(index), "semantic_identity": item.interaction_id,
                          "localized_surfaces": deepcopy(surfaces)})
        old_preserved = [s for s in old["slots"] if s["slot_id"] != "S2"]
        require([(s["slot_id"], s["semantic_identity"]) for s in slots] ==
                [(s["slot_id"], s["semantic_identity"]) for s in old_preserved],
                key + ": preserved owner identity drift")
        for old_slot, slot in zip(old_preserved, slots):
            if old_slot != slot:
                drift.append({"item_id": key, "slot_id": slot["slot_id"],
                              "previous": old_slot, "current": slot})
        # Reconstruct the complete predecessor using its structured L3 owner;
        # no physical row is assigned a role on the basis of its position.
        rows.append({"full_type": key, "slots": slots})
    l3 = read_json(root, (OWNER_ROOT / "tooltip_t1_layer3_owner_input.json").as_posix())["entries"]
    baseline_rows = deepcopy(rows)
    for row in baseline_rows:
        old = l3.get(row["full_type"])
        if old:
            row["slots"].append({"slot_id": "S2", "semantic_identity": old["fact_id"],
                                 "localized_surfaces": old["localized_surfaces"]})
        row["slots"].sort(key=lambda s: s["slot_id"])
    baseline, _, _ = project(AcceptedInput(tuple(baseline_rows), accepted.binding), contract)
    require(baseline == fixed, "current owner projection differs from fixed Tooltip; admission blocked")
    recipe_args = (usecases, navigation, recipe, rightclick, contract)
    previous_variants = project_recipe_variants(fixed, *recipe_args)
    require(variants_bytes(previous_variants) == local(root, (DATA_ROOT / VARIANTS_NAME).as_posix()).read_bytes().replace(b"\r\n", b"\n"),
            "current Recipe companion owner drift")
    return rows, accepted.binding, drift, fixed, previous_variants, recipe_args


def menu_projection(payload):
    runtime, mapping = {}, {}
    for item in payload["items"]:
        key = item["item_id"]
        require(key not in runtime, "duplicate Menu FullType")
        runtime[key], mapping[key] = {}, {}
        for locale in LOCALES:
            blocks = deepcopy(item["locales"][locale]["expanded"])
            texts = [block["text"] for block in blocks]
            runtime[key][locale] = {"blocks": texts, "text": "\n".join(texts)}
            mapping[key][locale] = deepcopy(item["locales"][locale])
    return runtime, mapping


def tooltip_projection(payload, preserved, owner_binding, contract):
    items = {r["item_id"]: r for r in payload["items"]}
    rows = deepcopy(preserved)
    for row in rows:
        item = items.get(row["full_type"])
        if item:
            s2 = {loc: item["locales"][loc]["s2"] for loc in LOCALES}
            require(s2["ko"]["logical_rows"] == s2["en"]["logical_rows"] in (0, 1), "S2 locale shape mismatch")
            if s2["ko"]["logical_rows"]:
                require(s2["ko"]["represented_fact_refs"] == s2["en"]["represented_fact_refs"], "S2 locale fact mismatch")
                row["slots"].append({"slot_id": "S2", "semantic_identity": "expression:" + digest(canonical(s2["ko"]["represented_fact_refs"])),
                                     "localized_surfaces": {loc: s2[loc]["text"] for loc in LOCALES}})
        row["slots"].sort(key=lambda slot: slot["slot_id"])
    data, provenance, summary = project(AcceptedInput(tuple(rows), {
        "adapter": SCHEMA, "expression": BINDING, "preserved_owner": owner_binding}), contract)
    return data, provenance, summary


def lua_value(value):
    if isinstance(value, str):
        return lua_string(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "{" + ",".join(lua_value(v) for v in value) + "}"
    if isinstance(value, dict):
        return "{" + ",".join("[" + lua_string(k) + "]=" + lua_value(value[k]) for k in sorted(value)) + "}"
    raise ValueError("unsupported runtime value")


def table_bytes(value):
    return ("return " + lua_value(value) + "\n").encode("utf-8")


def input_bindings(root):
    paths = [OWNER_OUTPUT.as_posix(),
             *( (OWNER_ROOT / n).as_posix() for n in (
                 "upstream_usecases_by_fulltype.json", "upstream_recipe_nav_registry.json",
                 "tooltip_t1_layer4_recipe_locale_owner_input.json", "tooltip_t1_layer3_owner_input.json")),
             "Iris/_docs/authority/iris_current_route_index.json",
             "Iris/_docs/authority/iris_current_authority_manifest.json",
             "Iris/media/lua/shared/translate/ko/Iris_ko.txt", "Iris/media/lua/shared/translate/en/Iris_en.txt",
             "Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua"]
    for name in ("IrisLayer3DataCurrent.lua", "IrisTooltipStaticData.lua", VARIANTS_NAME,
                 "IrisEvolvedRecipeLookup.lua"):
        paths.append((DATA_ROOT / name).as_posix())
    for directory in ("Layer3English", "EvolvedRecipe", "UseCaseDescriptions", "RecipeNavigation"):
        paths.extend(p.relative_to(root).as_posix() for p in sorted(local(root, (DATA_ROOT / directory).as_posix()).rglob("*.lua")))
    return [binding(root, p) for p in sorted(set(paths))]


def build_product(root: Path, output: Path):
    root, output = root.resolve(), output.resolve()
    require(not local(root, (DATA_ROOT / "IrisLayer3Product.lock").as_posix()).exists(), "product writer locked")
    new_output(root, output)
    before = input_bindings(root)
    adopted = expression.load(root, BINDING, mode="adopted")
    payload = adopted["payload"]
    preserved, owner, drift, previous, previous_variants, recipe_args = preserved_slots(root, payload)
    menu, mapping = menu_projection(payload)
    tooltip, provenance, summary = tooltip_projection(payload, preserved, owner, recipe_args[-1])
    variants = project_recipe_variants(tooltip, *recipe_args)
    require({k: [v["id"] for v in r["variants"]] for k, r in variants.items()} ==
            {k: [v["id"] for v in r["variants"]] for k, r in previous_variants.items()}, "Recipe selection domain changed")
    producers = [binding(root, CODE + name + ".py") for name in ("product_projection", "product_install")]
    producers.append(binding(root, CONTRACT))
    for name in ("IrisLayer3DataLookup.lua", "IrisLayer3EnglishLookup.lua", "layer3_renderer.lua",
                 "IrisTooltipStaticDataLookup.lua"):
        producers.append(binding(root, (DATA_ROOT / name).as_posix()))
    for path in ("Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua",
                 "Iris/media/lua/client/Iris/UI/Layer3/IrisLayer3DisplayFormatter.lua",
                 "Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua"):
        producers.append(binding(root, path))
    for name in ("package_iris.ps1", "Layer3PackageProjection.psm1", "RuntimeLookupIndexIdentity.psm1"):
        producers.append(binding(root, "Iris/tools/" + name))
    # The logical payload digest precedes product ID injection. Raw member
    # hashes below bind the final bytes; neither digest includes the manifest.
    identity = {"schema": SCHEMA, "expression": BINDING, "owners": before, "producer": producers,
                "payload_sha256": digest(canonical({"menu": menu, "tooltip": tooltip, "recipe": variants}))}
    product_id = "l3p-" + digest(canonical(identity))
    prefix = "Iris/Data/" + GENERATIONS + "/" + product_id + "/"
    files, records = {}, []
    keys = sorted(menu)
    for start in range(0, len(keys), 200):
        group = keys[start:start + 200]
        name = "Chunks/Chunk%03d" % (start // 200 + 1)
        entries = {k: {"item_id": k, "product_id": product_id, "locales": menu[k],
                       "text_ko": menu[k]["ko"]["text"], "publish_state": "public"} for k in group}
        raw = table_bytes(entries)
        files[name + ".lua"] = raw
        records.append({"first": group[0], "last": group[-1], "count": len(group),
                        "sha256": digest(raw), "module": prefix + name})
    files["Index.lua"] = table_bytes({"schema_version": "iris_layer3_product_index_v1", "product_id": product_id,
                                      "entry_count": len(keys), "chunks": records})
    for name, data, serializer in (("Tooltip", tooltip, lua_bytes), ("Recipe", variants, variants_bytes)):
        # Component envelope is checked by each stable facade before exposing
        # the existing public table shape.
        raw = serializer(data).decode("utf-8")
        start = raw.index("return ") + len("return ")
        files[name + ".lua"] = ("return {product_id=" + lua_string(product_id) + ",data=" + raw[start:].rstrip() + "}\n").encode("utf-8")
    descriptor = {"schema_version": SCHEMA, "product_id": product_id, "entry_count": len(menu),
                  "index_module": prefix + "Index", "tooltip_module": prefix + "Tooltip", "recipe_module": prefix + "Recipe",
                  "chunk_modules": [r["module"] for r in records]}
    files["Descriptor.lua"] = table_bytes(descriptor)
    manifest = {"schema_version": SCHEMA, "product_id": product_id, "identity": identity,
                "members": {k: digest(v) for k, v in sorted(files.items())},
                "menu": mapping, "tooltip": provenance, "summary": summary,
                "preserved_slots": preserved, "handoff": owner, "handoff_surface_drift": drift,
                "recipe_ids": {k: [v["id"] for v in r["variants"]] for k, r in variants.items()}}
    require(input_bindings(root) == before, "input drift during product invocation")
    require(not local(root, (DATA_ROOT / "IrisLayer3Product.lock").as_posix()).exists(), "product writer started during build")
    output.mkdir(parents=True)
    for name, raw in files.items():
        target = local(output, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    (output / "product_manifest.json").write_bytes(canonical(manifest))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_product(args.repository_root, args.output)
    print(json.dumps({"product_id": result["product_id"], "state": "candidate", "summary": result["summary"]}))


if __name__ == "__main__":
    main()
