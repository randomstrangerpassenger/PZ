"""Product admission, isolated runtime staging and recoverable promotion.

Only the common pointer supplies runtime visibility. Initial facade migration
and non-runtime locators require a game-closed guarded file transaction.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import zipfile

from .product_projection import (
    BINDING, DATA_ROOT, GENERATIONS, POINTER, SCHEMA, canonical, digest, local,
    require, table_bytes, new_output,
    MENU_SCHEMA, DESCRIPTION, BLOCKS, accepted_tooltip, menu_input_refs,
)

COMPAT = '''-- Derived compatibility view; the common pointer is the only switch.
local pointer = require("Iris/Data/IrisLayer3ProductCurrent")
assert(type(pointer) == "table" and pointer.schema_version == "iris_layer3_product_pointer_v1")
local id = pointer.product_id
assert(type(id) == "string" and #id == 68 and id:match("^l3p%%-[0-9a-f]+$"))
local prefix = "Iris/Data/IrisLayer3ProductGenerations/" .. id .. "/"
assert(pointer.descriptor_module == prefix .. "Descriptor")
local descriptor = require(pointer.descriptor_module)
assert(descriptor.schema_version == "iris-layer3-product-v1" and descriptor.product_id == id)
assert(descriptor.index_module == prefix .. "Index" and descriptor.tooltip_module == prefix .. "Tooltip" and descriptor.recipe_module == prefix .. "Recipe")
assert(type(descriptor.chunk_modules) == "table" and #descriptor.chunk_modules == 11)
for ordinal, name in ipairs(descriptor.chunk_modules) do
    assert(name == prefix .. string.format("Chunks/Chunk%%03d", ordinal))
end
return {
    schema_version = "iris_layer3_product_compat_v1", product_id = id, generation_id = id,
    index_module = descriptor.index_module, chunk_modules = descriptor.chunk_modules,
    tooltip_module = descriptor.tooltip_module, recipe_module = descriptor.recipe_module,
}
'''.replace("%%", "%")


def facades(product_id, schema=SCHEMA):
    pointer = ('return {\n    schema_version = "iris_layer3_product_pointer_v1",\n    product_id = "' + product_id +
               '",\n    descriptor_module = "Iris/Data/' + GENERATIONS + '/' + product_id + '/Descriptor",\n}\n').encode()
    result = {POINTER: pointer, "IrisLayer3DataCurrent.lua": COMPAT.encode(),
              "IrisLayer3DataChunkIndex.lua": b'local current = require("Iris/Data/IrisLayer3DataCurrent")\nreturn require(current.index_module)\n',
              "IrisLayer3DataChunks.lua": b'''-- Complete compatibility table for this product only.
local current = require("Iris/Data/IrisLayer3DataCurrent")
local lookup = require("Iris/Data/IrisLayer3DataLookup")
local result = {}
for _, module in ipairs(current.chunk_modules) do
    for key, _ in pairs(require(module)) do
        local entry, reason = lookup.get(key)
        assert(entry and not reason and entry.product_id == current.product_id)
        result[key] = entry
    end
end
IrisLayer3Data = result
return result
'''}
    if schema == MENU_SCHEMA:
        compat = COMPAT.replace('descriptor.schema_version == "iris-layer3-product-v1"',
                                'descriptor.schema_version == "iris-layer3-product-v2"')
        compat = compat.replace(' and descriptor.tooltip_module == prefix .. "Tooltip" and descriptor.recipe_module == prefix .. "Recipe"', '')
        compat = compat.replace('schema_version = "iris_layer3_product_compat_v1",',
                                'schema_version = "iris_layer3_product_compat_v1", display_schema = "iris_expanded_display_v1",')
        result["IrisLayer3DataCurrent.lua"] = compat.encode()
        return result
    for file, member in (("IrisTooltipStaticData.lua", "tooltip"), ("IrisTooltipRecipeVariants.lua", "recipe")):
        result[file] = ('''local current = require("Iris/Data/IrisLayer3DataCurrent")
local component = require(current.%s_module)
assert(type(component) == "table" and component.product_id == current.product_id)
assert(type(component.data) == "table" and getmetatable(component.data) == nil)
return component.data
''' % member).encode()
    return result


def admit(candidate: Path, *, description_ref=None, blocks_ref=None):
    description_ref, blocks_ref = menu_input_refs(description_ref, blocks_ref)
    candidate = candidate.resolve()
    raw = local(candidate, "product_manifest.json").read_bytes()
    manifest = json.loads(raw)
    require(canonical(manifest) == raw, "noncanonical product manifest")
    product_id = manifest["product_id"]
    is_menu = manifest["schema_version"] == MENU_SCHEMA
    require(manifest["schema_version"] in {SCHEMA, MENU_SCHEMA} and re.fullmatch(r"l3p-[0-9a-f]{64}", product_id)
            and (manifest["identity"].get("description") == description_ref and manifest["identity"].get("blocks") == blocks_ref
                 if is_menu else manifest["identity"].get("expression") == BINDING)
            and product_id == "l3p-" + digest(canonical(manifest["identity"])), "product identity mismatch")
    expected = {"Index.lua", "Tooltip.lua", "Recipe.lua", "Descriptor.lua",
                *("Chunks/Chunk%03d.lua" % n for n in range(1, 12))}
    if is_menu:
        expected -= {"Tooltip.lua", "Recipe.lua"}
        require(manifest["b_preserved"] == manifest["identity"]["b_preserved"]
                and manifest["shared_changes"] == manifest["identity"]["shared_changes"], "B preservation binding mismatch")
    require(set(manifest["members"]) == expected, "missing/unknown product member")
    actual = {p.relative_to(candidate).as_posix() for p in candidate.rglob("*") if p.is_file()}
    require(actual == expected | {"product_manifest.json"}, "candidate inventory mismatch")
    for name, sha in manifest["members"].items():
        require(re.fullmatch("[0-9a-f]{64}", sha) and digest(local(candidate, name).read_bytes()) == sha,
                "product member mismatch: " + name)
    return manifest


def inventory(root):
    return {p.relative_to(root).as_posix(): digest(local(root, p.relative_to(root).as_posix()).read_bytes())
            for p in sorted(root.rglob("*")) if p.is_file()}


def runtime_overlay(candidate, *, description_ref=None, blocks_ref=None):
    manifest = admit(candidate, description_ref=description_ref, blocks_ref=blocks_ref)
    product_id = manifest["product_id"]
    prefix = GENERATIONS + "/" + product_id + "/"
    files = {prefix + name: local(candidate, name).read_bytes() for name in manifest["members"]}
    # Packaging descriptor contains binding and member hashes, never Menu
    # fact/dependency maps. Lua only reads Descriptor.lua.
    schema = manifest["schema_version"]
    descriptor = {"schema_version": schema, "product_id": product_id,
                  "identity": manifest["identity"], "members": manifest["members"],
                  "menu_keys": sorted(manifest["menu"]),
                  "facades": {name: digest(raw) for name, raw in facades(product_id, schema).items()}}
    if schema == MENU_SCHEMA:
        descriptor["b_preserved"] = manifest["b_preserved"]
        descriptor["identity_json"] = canonical(manifest["identity"]).decode("utf-8")
    files[prefix + "product_descriptor.json"] = canonical(descriptor)
    files.update(facades(product_id, schema))
    return files


def stage(root, candidate, output, *, description_ref=None, blocks_ref=None, tooltip_ref=None):
    """A new isolated source tree, suitable for its own package_iris.ps1."""
    root, output = root.resolve(), output.resolve()
    new_output(root, output)
    manifest = admit(candidate, description_ref=description_ref, blocks_ref=blocks_ref)
    for name in ("IrisLayer3Product.lock", "IrisTooltip.lock"):
        require(not local(root, (DATA_ROOT / name).as_posix()).exists(), "product writer locked")
    if manifest["schema_version"] == MENU_SCHEMA:
        require(output.is_relative_to(root / ".tmp/menu"), "Menu stage must stay in repository .tmp/menu")
        if tooltip_ref is not None:
            require(manifest['identity'].get('tooltip_input') == tooltip_ref, 'B candidate binding mismatch')
        accepted, _ = accepted_tooltip(root, manifest['identity'].get('tooltip_input'), manifest['identity']['description'])
    # Reject source drift since the single product invocation; staging cannot
    # silently substitute a newer runtime or owner for the observed candidate.
    for ref in manifest["identity"]["owners"] + manifest["identity"]["producer"]:
        require(digest(local(root, ref["path"]).read_bytes()) == ref["sha256"], "candidate/source drift: " + ref["path"])
    excluded = {"IrisLayer3Generations", "IrisLayer3DataChunks", GENERATIONS, "Layer3English"}
    source_media = local(root, "Iris/media")
    output_media = output / "Iris/media"
    for path in source_media.rglob("*"):
        relative = path.relative_to(source_media)
        if path.is_file() and not any(part in excluded for part in relative.parts):
            source = local(root, path.relative_to(root).as_posix())
            target = output_media / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
    for name in ("mod.info", "poster.png"):
        source = local(root, "Iris/" + name)
        if source.exists():
            shutil.copyfile(source, output / "Iris" / name)
    for name in ("package_iris.ps1", "Layer3PackageProjection.psm1", "RuntimeLookupIndexIdentity.psm1"):
        target = output / "Iris/tools" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(local(root, "Iris/tools/" + name), target)
    data_root = output / DATA_ROOT
    if manifest["schema_version"] == MENU_SCHEMA:
        for name, sha in manifest["b_preserved"].items():
            require(name in accepted and digest(accepted[name]) == sha, "B admission mismatch")
            target = local(output, name)
            # Unclassified source drift cannot be hidden by overlaying B bytes.
            if target.exists() and name not in {(DATA_ROOT / n).as_posix() for n in
                    ("IrisTooltipStaticData.lua", "IrisTooltipRecipeVariants.lua", "IrisTooltipOwner.json")}:
                require(target.read_bytes() == accepted[name], "unclassified B runtime drift: " + name)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(accepted[name])
    for name, raw in runtime_overlay(candidate, description_ref=description_ref, blocks_ref=blocks_ref).items():
        target = local(data_root, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    identity_rows = ["product\t" + manifest["product_id"]]
    for name in ("UseCaseDescriptions/ChunkIndex.lua", "UseCaseDescriptions/LineCountIndex.lua"):
        raw = local(data_root, name).read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        identity_rows.append(name + "\t" + digest(raw))
    identity_rows.extend(name + "\t" + sha for name, sha in sorted(manifest["members"].items()))
    lookup = {"schema_version": "iris-runtime-product-lookup-identity-v1", "generation_id": manifest["product_id"],
              "source_digest": digest(("\n".join(identity_rows) + "\n").encode()),
              "layer3_entry_count": 2105, "usecase_entry_count": 1631, "line_count_entry_count": 1631}
    (data_root / "IrisRuntimeLookupPackageIdentity.json").write_bytes(canonical(lookup))
    if manifest["schema_version"] == MENU_SCHEMA:
        for name, sha in manifest["b_preserved"].items():
            require(local(output, name).read_bytes() == accepted[name], "stage B byte mismatch: " + name)
    return manifest["product_id"]


def restore_candidate(root, candidate, source, journal, *, interrupt_after=None, description_ref=None, blocks_ref=None, tooltip_ref=None):
    """Recover a candidate overlay in place; never authorize live promotion.

    Uses the existing journal/lock protocol for interrupted candidate repair.
    The exact B owner stays present throughout; promote's owner guard remains.
    """
    root, source, journal = root.resolve(), source.resolve(), journal.resolve()
    require(source.is_relative_to(root / ".tmp/menu") and journal.is_relative_to(source / ".tmp"),
            "candidate recovery must remain inside Menu stage")
    manifest = admit(candidate, description_ref=description_ref, blocks_ref=blocks_ref)
    require(manifest["schema_version"] == MENU_SCHEMA, "candidate schema required")
    if tooltip_ref is not None:
        require(manifest['identity'].get('tooltip_input') == tooltip_ref, 'B candidate binding mismatch')
    accepted, _ = accepted_tooltip(root, tooltip_ref, description_ref)
    files = {(DATA_ROOT / n).as_posix(): raw for n, raw in runtime_overlay(candidate, description_ref=description_ref, blocks_ref=blocks_ref).items()}
    files.update({n: accepted[n] for n in manifest["b_preserved"]})
    lock = local(source, (DATA_ROOT / "IrisLayer3Product.lock").as_posix())
    require(not lock.exists(), "product writer locked")
    require(not journal.exists(), "journal already used")
    if all(local(source, n).exists() and local(source, n).read_bytes() == raw for n, raw in files.items()):
        return "no_op"
    journal.mkdir(parents=True)
    with lock.open("xb") as stream:
        stream.write(canonical({"product_id": manifest["product_id"], "journal": str(journal)}))
    members = []
    for i, (name, raw) in enumerate(sorted(files.items())):
        target = local(source, name)
        before = target.read_bytes() if target.exists() else None
        if before is not None:
            backup = journal / "b" / str(i)
            backup.parent.mkdir(exist_ok=True)
            backup.write_bytes(before)
        members.append({"path": name, "before": digest(before) if before is not None else None, "after": digest(raw)})
    state = {"state": "prepared", "repository": str(source), "product_id": manifest["product_id"], "members": members}
    atomic_write(journal / "transaction.json", canonical(state))
    try:
        for i, member in enumerate(members):
            target = local(source, member["path"])
            require((digest(target.read_bytes()) if target.exists() else None) == member["before"], "concurrent candidate writer")
            atomic_write(target, files[member["path"]])
            if i == interrupt_after:
                raise InterruptedError("candidate repair interrupted")
        state["state"] = "complete"
        atomic_write(journal / "transaction.json", canonical(state))
        lock.unlink()
        return "complete"
    except Exception:
        recover(source, journal)
        raise


def atomic_write(path, raw):
    staged = path.with_name(path.name + ".stage")
    require(not staged.exists(), "unfinished staged write: " + str(staged))
    path.parent.mkdir(parents=True, exist_ok=True)
    with staged.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(staged, path)


def recover(root, journal):
    """Restore all transaction members after interruption, including pointer."""
    state = json.loads(local(journal, "transaction.json").read_bytes())
    require(state["repository"] == str(root.resolve()), "rollback repository mismatch")
    require(state["state"] in {"prepared", "writing", "complete", "rolled_back"}, "unknown journal state")
    if state["state"] in {"complete", "rolled_back"}:
        return state["state"]
    lock = local(root, (DATA_ROOT / "IrisLayer3Product.lock").as_posix())
    require(json.loads(lock.read_bytes()) == {"product_id": state["product_id"], "journal": str(journal.resolve())}, "rollback writer lock mismatch")
    for index, member in reversed(list(enumerate(state["members"]))):
        path = local(root, member["path"])
        staged = path.with_name(path.name + ".stage")
        if staged.exists():
            staged.unlink()
        if member["before"] is None:
            if path.exists():
                require(digest(path.read_bytes()) == member["after"], "rollback unexpected concurrent writer")
                path.unlink()
        else:
            raw = local(journal, "b/" + str(index)).read_bytes()
            require(digest(raw) == member["before"], "rollback backup mismatch")
            if path.exists():
                require(digest(path.read_bytes()) in {member["before"], member["after"]}, "rollback concurrent writer")
            atomic_write(path, raw)
    state["state"] = "rolled_back"
    atomic_write(journal / "transaction.json", canonical(state))
    lock.unlink()
    return "rolled_back"


def promote(root, candidate, source, journal, *, expected_pointer_sha256, observation,
            package_path, game_closed, metadata=None, interrupt_after=None):
    """Promote exact observed bytes. No builder or packager runs here.

    metadata maps repository-relative current route/authority locators to final
    bytes. Their expected before hashes belong to the admitted owner snapshot.
    A hard interruption leaves the writer lock and journal for recover().
    """
    root, journal = root.resolve(), journal.resolve()
    require(not local(root, (DATA_ROOT / 'IrisTooltipOwner.json').as_posix()).exists(),
            'Tooltip successor owns current files; historical unified promotion forbidden')
    require(journal.is_relative_to(root / ".tmp"), "journal must remain in repository .tmp")
    local(root, journal.relative_to(root).as_posix())
    manifest = admit(candidate)
    product_id = manifest["product_id"]
    require(game_closed is True, "game-closed installation required")
    require(observation.get("state") == "observed" and observation.get("observer")
            and observation.get("product_id") == product_id and observation.get("locales") == ["ko", "en"]
            and observation.get("package_sha256") == digest(package_path.read_bytes())
            and observation.get("runtime_inventory") == inventory(source / "Iris/media")
            and observation.get("cases"), "exact owner PZ observation required")
    with zipfile.ZipFile(package_path) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        require(len(names) == len(set(names)), "duplicate package member")
        expected = {"Iris/" + name: sha for name, sha in inventory(source / "Iris").items()
                    if name == "mod.info" or name == "poster.png" or name.startswith("media/")}
        require({name: digest(archive.read(name)) for name in names} == expected, "observed package/source parity mismatch")
    files = {(DATA_ROOT / name).as_posix(): raw for name, raw in runtime_overlay(candidate).items()}
    require(all(local(source, name).read_bytes() == raw for name, raw in files.items()), "observed source differs from candidate")
    lookup_path = (DATA_ROOT / "IrisRuntimeLookupPackageIdentity.json").as_posix()
    files[lookup_path] = local(source, lookup_path).read_bytes()
    for ref in manifest["identity"]["producer"]:
        if ref["path"].startswith("Iris/media/"):
            raw = local(source, ref["path"]).read_bytes()
            require(digest(raw) == ref["sha256"], "observed runtime source drift")
            files[ref["path"]] = raw
    allowed = {"Iris/_docs/authority/iris_current_route_index.json", "Iris/_docs/authority/iris_current_authority_manifest.json"}
    require(set(metadata or {}) == allowed, "both current route/authority locators required")
    for raw in metadata.values():
        value = json.loads(raw)
        require(value.get("layer3_product", {}).get("product_id") == product_id
                and value["layer3_product"].get("state") == "adopted", "promotion locator product mismatch")
    files.update(metadata or {})
    pointer = (DATA_ROOT / POINTER).as_posix()
    legacy = (DATA_ROOT / "IrisLayer3DataCurrent.lua").as_posix()
    current = local(root, pointer if local(root, pointer).exists() else legacy)
    lock = local(root, (DATA_ROOT / "IrisLayer3Product.lock").as_posix())
    require(not lock.exists(), "product writer locked; recover the recorded journal first")
    if current.read_bytes() == files[pointer]:
        require(all(local(root, name).read_bytes() == raw for name, raw in files.items()), "mixed current product")
        return "no_op"
    require(digest(current.read_bytes()) == expected_pointer_sha256, "expected predecessor mismatch")
    owners = {ref["path"]: ref["sha256"] for ref in manifest["identity"]["owners"]}
    require(all(digest(local(root, name).read_bytes()) == owners[name] for name in allowed), "current locator predecessor mismatch")
    journal.mkdir(parents=True, exist_ok=True)
    require(not (journal / "transaction.json").exists(), "transaction journal already used")
    with lock.open("xb") as stream:
        stream.write(canonical({"product_id": product_id, "journal": str(journal)}))
    names = sorted(set(files) - {pointer}) + [pointer]
    members = []
    try:
        require(digest(current.read_bytes()) == expected_pointer_sha256, "predecessor changed while acquiring lock")
        for index, name in enumerate(names):
            path = local(root, name)
            before = path.read_bytes() if path.exists() else None
            if before is not None:
                backup = journal / "b" / str(index)
                backup.parent.mkdir(exist_ok=True)
                backup.write_bytes(before)
            members.append({"path": name, "before": digest(before) if before is not None else None, "after": digest(files[name])})
        state = {"state": "prepared", "repository": str(root), "product_id": product_id, "members": members}
        atomic_write(journal / "transaction.json", canonical(state))
    except Exception:
        # No product member has been written before the journal is durable.
        lock.unlink()
        raise
    try:
        for index, member in enumerate(members):
            path = local(root, member["path"])
            actual = digest(path.read_bytes()) if path.exists() else None
            require(actual == member["before"], "concurrent product writer")
            atomic_write(path, files[member["path"]])
            if interrupt_after == index:
                raise InterruptedError("product transaction interrupted")
        require(all(local(root, name).read_bytes() == raw for name, raw in files.items()), "post-switch parity mismatch")
        state["state"] = "complete"
        atomic_write(journal / "transaction.json", canonical(state))
        lock.unlink()
        return "complete"
    except Exception:
        recover(root, journal)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--source-output", type=Path, required=True)
    args = parser.parse_args()
    print(stage(args.repository_root, args.candidate, args.source_output))


if __name__ == "__main__":
    main()
