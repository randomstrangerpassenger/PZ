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
import zipfile

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

MENU_SCHEMA = "iris-layer3-product-v2"
DESCRIPTION = {"path": "Iris/build/description/composition/descriptions.json",
               "sha256": "8e1eda45bb75482d69cb352a4676232b0824debc4c0be2a3d173d5c50b933c03"}
BLOCKS = {"path": "Iris/build/description/composition/blocks.json",
          "sha256": "860f6287c85b3eaf17de628b6b081eae5a4deb6b8bdac8280346454e27a27fb6"}
ACCEPTED_TOOLTIP = {"path": ".tmp/tooltip/preview/Iris.zip",
                    "sha256": "33b5927127442b16dca917c6f49f3e661743123c0cbd3d5890d47cb6fca96860"}
ACCEPTED_DESCRIPTION = {"path": "Iris/build/description/composition/descriptions.json",
                        "sha256": "ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0"}
# These shared components carry C's additive model/lookup path. All other
# retained accepted media are copied byte-for-byte, including Tooltip's closure.
MENU_RUNTIME = (
    "Data/IrisLayer3DataLookup.lua", "Data/layer3_renderer.lua",
    "UI/Detail/IrisItemDetailModelAssembler.lua", "UI/Wiki/IrisWikiSections.lua",
    "UI/Wiki/IrisWikiPanel.lua", "UI/Browser/IrisBrowserDetail.lua",
)


def menu_input_refs(description_ref=None, blocks_ref=None):
    """Resolve caller-owned candidate refs without changing current defaults."""
    require((description_ref is None) == (blocks_ref is None), "both Menu input refs are required")
    refs = (DESCRIPTION, BLOCKS) if description_ref is None else (description_ref, blocks_ref)
    result = []
    for ref, current in zip(refs, (DESCRIPTION, BLOCKS)):
        require(isinstance(ref, dict) and set(ref) == {"path", "sha256"}
                and ref["path"] == current["path"]
                and isinstance(ref["sha256"], str)
                and re.fullmatch(r"[0-9a-f]{64}", ref["sha256"]), "malformed Menu input ref")
        result.append(dict(ref))
    return tuple(result)

def read_menu_inputs(root, *, description_ref=None, blocks_ref=None):
    from . import description_composition_results, composition_results
    for ref in menu_input_refs(description_ref, blocks_ref):
        require(binding(root, ref["path"]) == ref, "canonical input drift: " + ref["path"])
    return description_composition_results.read_result(root), composition_results.read_result(root)


def accepted_tooltip(root, tooltip_ref=None, description_ref=None):
    tooltip_ref = tooltip_ref or ACCEPTED_TOOLTIP
    description_ref = description_ref or ACCEPTED_DESCRIPTION
    require(binding(root, tooltip_ref["path"]) == tooltip_ref, "accepted B ZIP drift")
    with zipfile.ZipFile(local(root, tooltip_ref["path"])) as archive:
        names = [n for n in archive.namelist() if not n.endswith("/")]
        require(len(names) == len(set(names)), "duplicate B member")
        for name in names:
            local(root, name)
        files = {name: archive.read(name) for name in names}
    prefix = DATA_ROOT.as_posix() + "/"
    owner = json.loads(files[prefix + "IrisTooltipOwner.json"])
    identity = json.loads(owner["identity_json"])
    require(owner["product_id"] == "ttp-" + digest(owner["identity_json"].encode())
            and identity["t1_input"]["description"] == description_ref, "B corpus/owner mismatch")
    require(set(owner["files"]) == {"IrisTooltipStaticData.lua", "IrisTooltipRecipeVariants.lua"}, "B member set")
    for name, sha in owner["files"].items():
        require(digest(files[prefix + name]) == sha == identity["files"][name], "B member mismatch")
    return files, owner


def expanded_projection(payload, blocks):
    """Separate only cuts that no source reference crosses.

    Shared references are a conservative continuity constraint, not a claim
    that sentences have identical meaning. Every segment stays intact and in
    source order. Unknown grouping remains continuous; nothing is collapsible.
    """
    source = {item["item_id"]: item for item in blocks["items"]}
    runtime, trace = {}, {}
    for item in payload["items"]:
        key = item["item_id"]
        require(key not in runtime and key in source, "Menu exact identity mismatch")
        structure = source[key]
        known = {"block_refs": set(), "branch_refs": set(), "fact_refs": set(),
                 "qualifier_refs": {q["qualifier_id"] for q in structure["qualifiers"]},
                 "relation_refs": set()}
        for block in structure["blocks"]:
            known["block_refs"].add(block["block_id"])
            known["relation_refs"].update(r["relation_id"] for r in block["relations"])
            for branch in block["branches"]:
                known["branch_refs"].add(branch["branch_id"])
                known["fact_refs"].update(f["fact_ref"] for f in branch["facts"])
        for qualifier in structure["qualifiers"]:
            known["fact_refs"].update(qualifier["fact_refs"])
        runtime[key], trace[key] = {}, {"source": deepcopy(item), "locales": {}}
        separate = set(structure["separate_block_refs"])
        for locale in LOCALES:
            row = item["locales"][locale]["expanded"]
            require(row["state"] in {"present", "absent"}, "failed expanded input")
            segments = row["segments"]
            references = []
            for segment in segments:
                for field, allowed in known.items():
                    require(set(segment[field]) <= allowed, "unresolved source reference: " + field)
                references.append({ref for field in known for ref in segment[field]})
            # A relation/qualifier can connect distinct facts even if a segment
            # does not repeat the relation ID. Keep its endpoints together too.
            spans = []
            for relation in item["relations"] + item["unresolved_relations"]:
                refs = set(relation.get("fact_refs", [])) | set(relation.get("branch_refs", []))
                positions = [i for i, values in enumerate(references) if values & refs]
                if positions:
                    spans.append((min(positions), max(positions)))
            cuts = [0]
            for position in range(1, len(segments)):
                left = set().union(*references[:position])
                right = set().union(*references[position:])
                left_blocks = {r for s in segments[:position] for r in s["block_refs"]}
                right_blocks = {r for s in segments[position:] for r in s["block_refs"]}
                if (not left & right and left_blocks | right_blocks <= separate
                        and not any(a < position <= b for a, b in spans)):
                    cuts.append(position)
            cuts.append(len(segments))
            if 'use_units' in row:
                # The composer owns independent purposes and their attached
                # conditions. Shared refs (including unresolved relations) do
                # not undo an explicitly authored use boundary.
                cuts = [0] + [unit['last_segment'] for unit in row['use_units']]
            units = []
            destinations = {}
            for start, end in zip(cuts, cuts[1:]):
                if start == end:
                    continue
                units.append({"first_segment": start + 1, "last_segment": end,
                              "text": " ".join(s["text"] for s in segments[start:end])})
                grouped = [s['target_groups'] for s in segments[start:end] if s.get('target_groups')]
                require(not grouped or (len(grouped) == 1 and end - start == 1), 'Grouped targets must own one independent use')
                if grouped:
                    units[-1]['target_groups'] = deepcopy(grouped[0])
                for position in range(start, end):
                    destinations[position] = len(units)
            runtime[key][locale] = {"schema_version": "iris_expanded_display_v1", "state": row["state"],
                                    "reason": row["reason"] or "", "text": row["text"],
                                    "blocks": [s["text"] for s in segments], "units": units}
            trace[key]["locales"][locale] = {
                "units": deepcopy(units),
                "detail_links": [{**deepcopy(link), "runtime_segment": link["segment"] + 1,
                                  "unit": destinations[link["segment"]]}
                                 for link in item["locales"][locale]["compact"].get("detail_links", [])]}
    require(set(runtime) == set(source), "Menu/source coverage mismatch")
    return runtime, trace


def build_menu_product(root: Path, output: Path, *, tooltip_ref=None, description_ref=None, blocks_ref=None):
    """Explicit canonical C candidate; does not invoke historical B writers."""
    root, output = root.resolve(), output.resolve()
    require(output.is_relative_to(root / ".tmp/menu"), "Menu candidate must stay in repository .tmp/menu")
    new_output(root, output)
    for name in ("IrisLayer3Product.lock", "IrisTooltip.lock"):
        require(not local(root, (DATA_ROOT / name).as_posix()).exists(), "product writer locked")
    description_ref, blocks_ref = menu_input_refs(description_ref, blocks_ref)
    payload, blocks = read_menu_inputs(root, description_ref=description_ref, blocks_ref=blocks_ref)
    tooltip_ref = tooltip_ref or ACCEPTED_TOOLTIP
    accepted, owner = accepted_tooltip(root, tooltip_ref, description_ref)
    menu, trace = expanded_projection(payload, blocks)
    owners = [description_ref, blocks_ref, tooltip_ref]
    # Bind exactly the source media/tools that staging reads, including files
    # shared with B. Accepted B bytes themselves come from the admitted ZIP.
    paths = [p.relative_to(root).as_posix() for p in local(root, "Iris/media").rglob("*") if p.is_file()
             and not any(x in p.parts for x in ("IrisLayer3Generations", "IrisLayer3DataChunks", GENERATIONS, "Layer3English"))]
    paths += [CODE + name + ".py" for name in ("product_projection", "product_install")]
    paths += ["Iris/tools/" + n for n in ("package_iris.ps1", "Layer3PackageProjection.psm1", "RuntimeLookupIndexIdentity.psm1")]
    producers = [binding(root, p) for p in sorted(set(paths))]
    replaced = {"Iris/media/lua/client/Iris/" + n for n in MENU_RUNTIME}
    replaced.update((DATA_ROOT / n).as_posix() for n in (POINTER, "IrisLayer3DataCurrent.lua",
                     "IrisLayer3DataChunkIndex.lua", "IrisLayer3DataChunks.lua", "IrisRuntimeLookupPackageIdentity.json"))
    preserved = {n: digest(raw) for n, raw in accepted.items() if n.startswith("Iris/media/") and n not in replaced
                 and not any(x in n.split("/") for x in ("IrisLayer3Generations", "IrisLayer3DataChunks", GENERATIONS, "Layer3English"))}
    changed = {n: {"before": digest(accepted[n]), "after": digest(local(root, n).read_bytes())}
               for n in sorted(replaced) if n in accepted and n.startswith("Iris/media/lua/client/Iris/")
               and n.removeprefix("Iris/media/lua/client/Iris/") in MENU_RUNTIME}
    identity = {"schema": MENU_SCHEMA, "description": description_ref, "blocks": blocks_ref,
                "tooltip_input": tooltip_ref,
                "tooltip_product_id": owner["product_id"], "owners": owners, "producer": producers,
                "b_preserved": preserved, "shared_changes": changed,
                "payload_sha256": digest(canonical(menu))}
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
    files["Descriptor.lua"] = table_bytes({"schema_version": MENU_SCHEMA, "product_id": product_id,
        "entry_count": len(keys), "index_module": prefix + "Index", "tooltip_product_id": owner["product_id"],
        "chunk_modules": [r["module"] for r in records]})
    manifest = {"schema_version": MENU_SCHEMA, "product_id": product_id, "identity": identity,
                "members": {n: digest(raw) for n, raw in sorted(files.items())}, "menu": trace,
                "b_preserved": preserved, "shared_changes": changed,
                "summary": payload["summary"]}
    for ref in owners + producers:
        require(binding(root, ref["path"]) == ref, "source drift during C generation")
    output.mkdir(parents=True)
    for name, raw in files.items():
        target = local(output, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    (output / "product_manifest.json").write_bytes(canonical(manifest))
    return manifest


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
    for name in ("IrisLayer3DataLookup.lua", "IrisLayer3ProductLookup.lua", "IrisLayer3LegacyLookup.lua", "IrisLayer3EnglishLookup.lua", "layer3_renderer.lua",
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
