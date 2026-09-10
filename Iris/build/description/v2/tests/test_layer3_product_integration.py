"""One canonical product contract surface; no standalone validation authority."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

import pytest

from iris_tooling.domains.layer3 import expression_results as expression
from iris_tooling.domains.layer3 import product_projection as product
from iris_tooling.domains.layer3 import product_install as install

ROOT = Path(__file__).resolve().parents[5]


def command(argv, cwd):
    # Every potentially long child has an upper bound. The canonical launcher
    # captures this contract's single output stream and owns the result.
    result = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=240)
    if result.returncode != 0:
        pytest.fail("command exited %s: %r\n%s\n%s" % (
            result.returncode, argv, result.stdout[-12000:].decode("utf-8", errors="replace"),
            result.stderr[-12000:].decode("utf-8", errors="replace")), pytrace=False)
    return result.stdout


def test_product_contract(tmp_path, monkeypatch):
    # Share the canonical result boundary with a shallow product workspace.
    # Generation-qualified Lua paths must remain usable by Windows packaging.
    output = os.environ.get("IRIS_CLEAN_CHECKOUT_TEST_OUTPUT_ROOT")
    if output:
        tmp_path = Path(output) / "product"
        tmp_path.mkdir()
    payload = expression.load(ROOT, product.BINDING, mode="adopted")["payload"]
    before_pointer = (ROOT / product.DATA_ROOT / "IrisLayer3DataCurrent.lua").read_bytes()
    first, second = tmp_path / "a", tmp_path / "b"
    manifest = product.build_product(ROOT, first)
    other = product.build_product(ROOT, second)
    assert manifest == other and install.inventory(first) == install.inventory(second)
    shutil.rmtree(second)
    items = {row["item_id"]: row for row in payload["items"]}
    facts = {f["ref"]: f for f in payload["facts"]}
    assert len(items) == 2105 and len(facts) == 5290
    assert sum(f["fact_kind"] == "acquisition" for f in facts.values()) == 1057
    preserved, _, _, baseline, old_recipe, args = product.preserved_slots(ROOT, payload)
    expected_menu, expected_tooltip = {}, {}
    represented = set()
    present, empty = {loc: set() for loc in product.LOCALES}, {loc: set() for loc in product.LOCALES}
    for key, item in items.items():
        expected_menu[key] = {}
        for locale in product.LOCALES:
            authority = item["locales"][locale]
            assert manifest["menu"][key][locale] == authority
            blocks = [row["text"] for row in authority["expanded"]]
            expected_menu[key][locale] = {"blocks": blocks, "text": "\n".join(blocks)}
            refs = {ref for block in authority["expanded"] for ref in block["represented_fact_refs"]}
            assert refs == {ref for ref, fact in facts.items() if fact["item_id"] == key}
            represented.update((ref, locale) for ref in refs)
            if not blocks:
                empty[locale].add(key)
            if authority["s2"]["logical_rows"]:
                present[locale].add(key)
    assert len(represented) == 10580
    assert present["ko"] == present["en"] and len(present["ko"]) == 1280
    assert empty["ko"] == empty["en"] and len(empty["ko"]) == 552
    assert empty["ko"] <= set(items) - present["ko"] and len(set(items) - present["ko"]) == 825
    for row in preserved:
        key = row["full_type"]
        slots = {s["slot_id"]: s for s in row["slots"]}
        expected_tooltip[key] = {}
        for locale in product.LOCALES:
            values = {}
            for slot_id, slot in slots.items():
                values[slot_id] = slot["localized_surfaces"][locale]
            if key in present[locale]:
                values["S2"] = items[key]["locales"][locale]["s2"]["text"]
            expected_tooltip[key][locale] = [values[s] for s in sorted(values)]
            assert len(values) <= 4
        final_lines = manifest["tooltip"][key]["lines"]
        for slot in row["slots"]:
            line = next(line for line in final_lines if line["slot_id"] == slot["slot_id"])
            assert line["semantic_identity"] == slot["semantic_identity"]
            for locale in product.LOCALES:
                assert line["surface_sha256"][locale]["final_sha256"] == product.digest(slot["localized_surfaces"][locale].encode())
    assert len(set(expected_tooltip) - set(items)) == 175
    for key in set(expected_tooltip) - set(items):
        assert "S2" not in manifest["tooltip"][key]["present_slots"]
    expected_recipe = product.project_recipe_variants(expected_tooltip, *args)
    assert {k: [v["id"] for v in r["variants"]] for k, r in expected_recipe.items()} == manifest["recipe_ids"]
    for key, entry in expected_recipe.items():
        assert entry["base"] == expected_tooltip[key]
        assert [v["id"] for v in entry["variants"]] == [v["id"] for v in old_recipe[key]["variants"]]
    source = tmp_path / "source"
    install.stage(ROOT, first, source)
    sample = next(k for k, r in expected_recipe.items() if len(r["variants"]) > 1)
    fixture = tmp_path / "expected.lua"
    fixture.write_bytes(product.table_bytes({"menu": expected_menu, "tooltip": expected_tooltip,
                                             "recipe": expected_recipe, "recipe_sample": sample}))
    lua = shutil.which("lua")
    assert lua, "BLOCKED: Lua runtime unavailable"
    output = command([lua, str(ROOT / "Iris/test/lua/tooltip_static_data_runtime_harness.lua"), str(source), "product", str(fixture)], ROOT)
    assert b"IRIS_PRODUCT_CONSUMER_PASS" in output
    package = tmp_path / "package"
    command(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(source / "Iris/tools/package_iris.ps1"),
             "-OutputRoot", str(package), "-PackageApplicability", "current_runtime_payload", "-Zip"], ROOT)
    installed = tmp_path / "install"
    shutil.copytree(package / "Iris", installed / "Iris")
    assert install.inventory(source / "Iris/media") == install.inventory(package / "Iris/media") == install.inventory(installed / "Iris/media")
    with zipfile.ZipFile(package / "Iris.zip") as archive:
        assert {name: product.digest(archive.read(name)) for name in archive.namelist() if not name.endswith("/")} == {
            "Iris/" + name: sha for name, sha in install.inventory(package / "Iris").items()}
    # Malformed/stale candidate and path admission share this contract run.
    bad = tmp_path / "bad"
    shutil.copytree(first, bad)
    target = bad / "Index.lua"
    target.write_bytes(target.read_bytes() + b"--stale\n")
    with pytest.raises(ValueError, match="member mismatch"):
        install.admit(bad)
    with pytest.raises(ValueError):
        product.local(first, "../escape")
    shutil.rmtree(bad)
    # Simulated owner records are ONLY fault-injection fixtures, not PZ evidence.
    target_root = tmp_path / "target"
    shutil.copytree(source, target_root)
    data = target_root / product.DATA_ROOT
    (data / product.POINTER).unlink()
    (data / "IrisLayer3DataCurrent.lua").write_bytes(before_pointer)
    metadata = {name: product.canonical({"layer3_product": {"product_id": manifest["product_id"], "state": "adopted"}}) for name in (
        "Iris/_docs/authority/iris_current_route_index.json", "Iris/_docs/authority/iris_current_authority_manifest.json")}
    for name in metadata:
        destination = target_root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
    observed = {"state": "observed", "observer": "synthetic fault-injection fixture", "product_id": manifest["product_id"],
                "locales": ["ko", "en"], "cases": ["fixture"], "package_sha256": product.digest((package / "Iris.zip").read_bytes()),
                "runtime_inventory": install.inventory(source / "Iris/media")}
    options = dict(expected_pointer_sha256=product.digest(before_pointer), observation=observed,
                   package_path=package / "Iris.zip", game_closed=True, metadata=metadata)
    for index in (0, len(install.runtime_overlay(first)) + 6):
        journal = target_root / ".tmp" / str(index)
        before = install.inventory(target_root / "Iris")
        with pytest.raises(InterruptedError):
            install.promote(target_root, first, source, journal, interrupt_after=index, **options)
        assert install.inventory(target_root / "Iris") == before
        assert install.recover(target_root, journal) == "rolled_back"
    journal = target_root / ".tmp" / "interrupted"
    original_write = install.atomic_write
    def interrupted_write(path, raw):
        original_write(path, raw)
        if path.name == product.POINTER:
            raise KeyboardInterrupt("simulated process interruption after pointer switch")
    before = install.inventory(target_root / "Iris")
    with monkeypatch.context() as patch:
        patch.setattr(install, "atomic_write", interrupted_write)
        with pytest.raises(KeyboardInterrupt):
            install.promote(target_root, first, source, journal, **options)
    assert install.recover(target_root, journal) == "rolled_back"
    assert install.inventory(target_root / "Iris") == before
    journal = target_root / ".tmp" / "current"
    assert install.promote(target_root, first, source, journal, **options) == "complete"
    assert install.promote(target_root, first, source, journal, **options) == "no_op"
    assert (ROOT / product.DATA_ROOT / "IrisLayer3DataCurrent.lua").read_bytes() == before_pointer
