"""Validate audit completeness and provenance, not the truth of game descriptions."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]


def jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


summary = json.loads((OUT / "summary.json").read_text(encoding="utf-8"))
rows = jsonl(OUT / "item_audit.jsonl")
items = {r["item_id"]: r for r in rows}
facts = {r["item_id"]: r for r in jsonl(ROOT / "Iris/build/description/v2/data/dvf_3_3_facts.jsonl")}
rendered = json.loads((ROOT / "Iris/media/lua/client/Iris/Data/IrisLayer3Generations" / summary["generation_id"] / "dvf_3_3_rendered.json").read_text(encoding="utf-8"))["entries"]
source_rows = jsonl(OUT / "source_files.jsonl")
evidence_rows = jsonl(OUT / "source_evidence.jsonl")
evidence = {r["id"]: r for r in evidence_rows}
assert len(items) == len(rows) == 2105
assert set(items) == set(facts) == set(rendered)
assert len(evidence) == len(evidence_rows) == summary["evidence_count"]
assert Counter(r["status"] for r in rows) == summary["status_counts"]
assert sum(summary["status_counts"].values()) == 2105
assert Counter(f for r in rows for f in r["review_flags"]) == summary["review_flag_counts"]
assert len(source_rows) == sum(summary["source_files"].values()) == 1041
assert len(jsonl(OUT / "unresolved_recipe_tokens.jsonl")) == summary["recipe_unresolved_token_count"]

line_counts = {}
for source in source_rows:
    path = ROOT / source["path"]
    assert path.is_file() and digest(path) == source["sha256"], source["path"]
    line_counts[source["path"]] = len(path.read_text(encoding="utf-8-sig", errors="replace").splitlines())
for path, expected in summary["input_hashes"].items():
    assert digest(ROOT / path) == expected, path

referenced = set()
for row in rows:
    ft = row["item_id"]
    assert row["current_text_ko"] == rendered[ft].get("text_ko"), ft
    assert row["current_primary_use"] == facts[ft].get("primary_use"), ft
    assert row["semantic_truth_verdict"] == "NOT_DETERMINED_BY_FIRST_PASS", ft
    assert row["runtime_reachability_verified"] is False, ft
    refs = row["source_evidence_ids"]
    assert len(refs) == len(set(refs)), ft
    for eid in refs:
        assert eid in evidence and ft in evidence[eid]["item_ids"], (ft, eid)
        referenced.add(eid)
    assert Counter(evidence[eid]["kind"] for eid in refs) == row["source_evidence_counts"], ft
    assert row["use_declaration_count"] == sum(evidence[eid]["proof_level"] == "script_declaration_only" and evidence[eid]["kind"] != "recipe_output" for eid in refs), ft
    if row["status"] == "STRUCTURED_DECLARATIONS_AVAILABLE":
        assert row["use_declaration_count"] > 0, ft
    if row["status"] == "STATIC_FIELDS_AVAILABLE":
        assert row["raw_action_or_effect_field_candidates"], ft
    for field, value in row["raw_detail_fields_missing_from_input"].items():
        assert field not in (row["current_itemscript_fields"] or {}), (ft, field)
        assert any(d["fields"].get(field) == value for d in row["raw_item_definitions"]), (ft, field)
    for d in row["raw_item_definitions"]:
        assert 1 <= d["line"] <= line_counts[d["source"]], ft
        line = (ROOT / d["source"]).read_text(encoding="utf-8-sig", errors="replace").splitlines()[d["line"] - 1]
        assert re.search(r"\bitem\s+" + re.escape(ft.split(".", 1)[1]) + r"\s*(?:\{|$)", line), (ft, line)

assert referenced == set(evidence)
for ev in evidence_rows:
    assert 1 <= ev["line"] <= line_counts[ev["source"]], ev["id"]
    assert ev["item_ids"] and set(ev["item_ids"]) <= set(items), ev["id"]
    assert all(ev["id"] in items[ft]["source_evidence_ids"] for ft in ev["item_ids"]), ev["id"]

# Independently anchored examples catch over-broad or lost relation extraction.
assert items["Base.Toolbox"]["raw_detail_fields"]["Capacity"] == "8"
assert items["Base.Toolbox"]["raw_detail_fields_missing_from_input"]["WeightReduction"] == "15"
assert "FruitSalad:8" in items["Base.Apple"]["raw_detail_fields"]["EvolvedRecipe"]
assert items["Base.Apple"]["raw_detail_fields"]["HungerChange"] == "-16"
assert any(evidence[e]["kind"] == "recipe_keep" and evidence[e].get("recipe") == "Build Spiked Baseball Bat" and "Base.BaseballBatNails" in evidence[e]["result_item_ids"] for e in items["Base.Hammer"]["source_evidence_ids"])
assert any(evidence[e]["kind"] == "fixing_material" and "Base.Axe" in evidence[e]["target_items"] for e in items["Base.Scotchtape"]["source_evidence_ids"])
assert any(evidence[e]["source"] == "lua/client/Vehicles/ISUI/ISVehiclePartMenu.lua" and evidence[e]["kind"] == "lua_item_locator" for e in items["Base.TirePump"]["source_evidence_ids"])
assert all(not items[ft]["raw_item_definitions"] for ft in ("Base.Lemongrass", "Base.NoiseMaker", "Base.Bag_PistolCase"))
assert items["Base.LemonGrass"]["raw_item_definitions"]

table_rows = [line for line in (OUT / "items.md").read_text(encoding="utf-8").splitlines() if re.match(r"\| \d+ \|", line)]
assert len(table_rows) == 2105
assert {line.split("|")[2].strip() for line in table_rows} == set(items)
assert all(len(re.split(r"(?<!\\)\|", line)) == 12 for line in table_rows)
group_text = (OUT / "primary_text_groups.md").read_text(encoding="utf-8")
group_ids = re.findall(r"`((?:Base|farming|camping|Radio)\.[^`]+)`", group_text)
assert len(group_ids) == len(set(group_ids)) == 2105 and set(group_ids) == set(items)

print(json.dumps({"audit_artifact_validation": "PASS", "items": len(items), "source_files_hash_verified": len(source_rows), "evidence_records_verified": len(evidence), "semantic_or_gameplay_validation": "NOT_PERFORMED", "product_data_modified_by_audit": False}, ensure_ascii=False, indent=2))
