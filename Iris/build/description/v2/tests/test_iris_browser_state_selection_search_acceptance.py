from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import shutil
import subprocess
import unittest
from contextlib import redirect_stdout
from dataclasses import dataclass, replace
from io import StringIO
from pathlib import Path
from unittest.mock import patch

REPO = next(parent for parent in Path(__file__).resolve().parents if (parent / ".git").exists())


PAYLOAD = REPO / "Iris/media/lua/client/Iris/Data/IrisTooltipStaticData.lua"
EXPECTED_SHA256 = "1efc19e01132767f97111048eba2e027916b69ef07304f19c3152144a7817647"
DATA_ROOT = REPO / "Iris/media/lua/client/Iris/Data"
V2_DATA = REPO / "Iris/build/description/v2/data"


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AssertionError(f"duplicate exact key: {key}")
        result[key] = value
    return result


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def menu_subject() -> dict:
    """Bind this observation to current repository inputs, never Tooltip IDs."""
    pointer = DATA_ROOT / "IrisLayer3DataCurrent.lua"
    matches = re.findall(r'generation_id\s*=\s*"(dvf33-[0-9a-f]{64})"', pointer.read_text(encoding="utf-8"))
    assert len(matches) == 1, "invalid Menu generation pointer"
    generation = matches[0]
    root = DATA_ROOT / "IrisLayer3Generations" / generation
    descriptor = _json(root / "generation_descriptor.json")
    assert descriptor["generation_id"] == generation
    paths = {pointer, root / "generation_descriptor.json", V2_DATA / "dvf_3_3_input_manifest.json"}
    for row in descriptor["canonical_inputs"]:
        path = (REPO / row["path"]).resolve()
        assert path.is_relative_to(REPO.resolve()), "Menu input escapes repository"
        assert _sha(path) == row["raw_byte_sha256"], "stale Menu generation input"
        paths.add(path)
    for row in descriptor["outputs"]:
        # The installer moves runtime/ paths into the generation's module root.
        relative = row["path"].removeprefix("runtime/")
        relative = relative.removeprefix(f"IrisLayer3Generations/{generation}/")
        if relative == "IrisLayer3DataCurrent.lua":
            continue
        path = (root / relative).resolve()
        assert path.is_relative_to(root.resolve()), "Menu output escapes generation"
        assert _sha(path) == row["raw_byte_sha256"], "stale Menu generation output"
        paths.add(path)
    source = _json(V2_DATA / "dvf_3_3_input_manifest.json")["facts"]
    assert source["role"] == "current_source_authority"
    assert source["path"] == "Iris/build/description/v2/data/dvf_3_3_facts.jsonl"
    assert source["sha256"] == _sha(REPO / source["path"]), "unbound approved facts"
    rendered = _json(root / "dvf_3_3_rendered.json")["entries"]
    approved = _json(V2_DATA / "layer3_body_role_realign/approved_upstream/candidate_rendered.json")
    assert rendered == approved["entries"], "current Menu differs from approved candidate"
    paths.update((DATA_ROOT / "Layer3English").glob("*.lua"))
    for relative in (
        "Iris/tooling/src/iris_tooling/build/build_layer3_english_localization.py",
        "Iris/tooling/src/iris_tooling/build/dvf_3_3_generation_contract.py",
        "Iris/tooling/src/iris_tooling/build/repository_context.py",
        "Iris/build/description/v2/tools/build/layer3_body_role_realign.py",
        "Iris/build/description/v2/data/layer3_body_role_realign/fact_kind_mapping_contract.json",
        "Iris/build/description/v2/data/layer3_body_role_realign/policy_ratification_contract.json",
        "Iris/test/lua/tooltip_static_data_runtime_harness.lua",
        "Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py",
        "Iris/media/lua/client/Iris/Data/IrisLayer3DataChunkIndex.lua",
        "Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua",
        "Iris/media/lua/client/Iris/Data/IrisLayer3EnglishLookup.lua",
        "Iris/media/lua/client/Iris/Data/layer3_renderer.lua",
        "Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailViewModel.lua",
        "Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua",
        "Iris/media/lua/client/Iris/IrisTranslationLoader.lua",
        "Iris/media/lua/client/Iris/Util/IrisTranslationResolver.lua",
    ):
        paths.add(REPO / relative)
    bindings = {}
    for path in paths:
        path = path.resolve()
        assert path.is_relative_to(REPO.resolve()), "Menu binding escapes repository"
        bindings[path.relative_to(REPO.resolve()).as_posix()] = _sha(path)
    corrections = {row["item_id"]: row.get("slot_meta", {}).get("usefulness_correction")
                   for row in (json.loads(line) for line in (V2_DATA / "dvf_3_3_facts.jsonl").read_text(encoding="utf-8").splitlines())
                   if row.get("slot_meta", {}).get("usefulness_correction")}
    return {"generation": generation, "bindings": bindings, "entries": rendered,
            "usefulness_corrections": corrections,
            "adoption": approved.get("meta", {}).get("general_description_integration", {})}


def predecessor_selected(selected: dict, corrections: dict) -> tuple[dict, dict]:
    """Reverse only source-bound adopted changes, retaining the original ledger guard."""
    previous = dict(selected)
    transitions = {}
    for key, correction in corrections.items():
        expected = correction["expected_s2"]
        assert selected.get(key) == expected["id"], "initial selected ledger membership or adopted fact changed"
        old_ids = correction["predecessor_core_source_fact_ids"]
        assert len(old_ids) <= 1, "ambiguous predecessor core"
        if old_ids:
            previous[key] = old_ids[0]
        else:
            previous.pop(key)
        transitions[key] = {"before": old_ids[0] if old_ids else None, "after": selected[key]}
    return previous, transitions


@dataclass(frozen=True)
class MenuEvidence:
    """Ephemeral test input from reconstruction; not a certificate or registry."""
    generation: str
    bindings: dict[str, str]
    records: dict[str, tuple[str, str, str]]  # module, source-bound core ID, text SHA
    method: str = "current_deterministic_derivability"


def reconstruct_menu_evidence(replay_root: Path, subject: dict) -> MenuEvidence:
    """One isolated run of the existing EN producer/serializer, no live writes.

    Calling this requires the execution prompt to allow the plan's external
    output exception. The caller must not use this as historical-run provenance.
    """
    # Successor execution root approved for the usefulness plan; no live install.
    allowed = Path("C:/Users/MW/PZ-U").resolve()
    replay_root = replay_root.resolve()
    assert replay_root != allowed and replay_root.is_relative_to(allowed), "replay outside plan root"
    assert not replay_root.exists(), "replay requires a new unused leaf"
    sys.path.insert(0, str(REPO / "Iris/tooling/src"))
    try:
        from iris_tooling.build.repository_context import configure_repository
        configure_repository(REPO)
        from iris_tooling.build import build_layer3_english_localization as producer
        assert Path(producer.__file__).resolve() == (REPO / "Iris/tooling/src/iris_tooling/build/build_layer3_english_localization.py").resolve()
        entries, generation, _ = producer.build_english_entries(REPO)
        assert generation == subject["generation"]
        producer._write_runtime(entries, replay_root)
    finally:
        sys.path.pop(0)
    actual = DATA_ROOT / "Layer3English"
    generated = {path.name: path.read_bytes() for path in replay_root.glob("*.lua")}
    live = {path.name: path.read_bytes() for path in actual.glob("*.lua")}
    assert generated == live, "EN reconstruction differs from current Index/chunks"
    index = re.findall(r'\{ first = "([^"]+)", last = "([^"]+)", module = "([^"]+)" \}',
                       (replay_root / "Index.lua").read_text(encoding="utf-8"))
    assert index, "EN reconstruction index missing"
    facts = _unique_object((row["item_id"], row) for row in (
        json.loads(line, object_pairs_hook=_unique_object)
        for line in (V2_DATA / "dvf_3_3_facts.jsonl").read_text(encoding="utf-8").splitlines() if line))
    decisions = _unique_object((row["item_id"], row) for row in (
        json.loads(line, object_pairs_hook=_unique_object)
        for line in (V2_DATA / "dvf_3_3_decisions.jsonl").read_text(encoding="utf-8").splitlines() if line))
    mapping = _json(V2_DATA / "layer3_body_role_realign/fact_kind_mapping_contract.json")
    records = {}
    for key, text in entries.items():
        core = subject["entries"][key]["role_material"]["core_source_fact_ids"]
        if not core:
            continue  # Acquisition/identity-only public bodies are outside S2.
        fact = facts[key]
        origins = fact.get("fact_origin", {}).get("primary_use", [])
        assert len(core) == len(origins) == 1 and fact.get("primary_use"), "ambiguous Menu primary-use relation"
        origin = origins[0]
        lineage = None
        if origin == "cluster_summary":
            decision = decisions.get(key, {})
            assert (decision.get("facts_ref") == key and decision.get("state") == "adopted"
                    and decision.get("cluster_used") is True and decision.get("use_source") == "cluster_summary"), "unapproved Menu cluster lineage"
            lineage = "layer3_approval_bound"
        rules = [row for row in mapping["scalar_mappings"]
                 if (row["source_slot"], row["fact_origin"], row.get("lineage_state")) == ("primary_use", origin, lineage)]
        assert len(rules) == 1 and rules[0]["description_eligible"] and rules[0]["outcome"] == "eligible_kind"
        # Read-only check of scalar_fact_id's existing source identity convention.
        # Never derive this identity from Tooltip, EN prose, or an observed count.
        scalar = {"item_id": key, "source_slot": "primary_use", "fact_origin": origin,
                  "source_value_hash": hashlib.sha256(fact["primary_use"].encode("utf-8")).hexdigest()}
        identity = "l3rf-" + hashlib.sha256(json.dumps(scalar, ensure_ascii=False, sort_keys=True,
                                                       separators=(",", ":")).encode("utf-8")).hexdigest()
        assert core == [identity], "Menu core does not bind producer primary-use input"
        modules = [module for first, last, module in index if first <= key <= last]
        assert len(modules) == 1, "ambiguous EN output module"
        records[key] = (modules[0], identity, hashlib.sha256(text.encode("utf-8")).hexdigest())
    assert menu_subject() == subject, "Menu changed during reconstruction"
    return MenuEvidence(generation, subject["bindings"], records)


def load_menu_baseline(root: Path) -> dict:
    root = root.resolve()
    allowed = Path("C:/Users/MW/Downloads/coding/PZ2/t3d1").resolve()
    assert root.is_relative_to(allowed) and root != allowed, "baseline outside plan root"
    reports = [line.split("\t", 1)[1] for line in (root / "menu-before.txt").read_text(encoding="utf-8").splitlines()
               if line.startswith("MENU_RELATION_REPORT\t")]
    assert len(reports) == 1, "initial relation report missing or ambiguous"
    before = json.loads(reports[0], object_pairs_hook=_unique_object)
    prefix = "Iris/media/lua/client/Iris/Data/Layer3English/"
    expected = {Path(path).name: sha for path, sha in before["subject_bindings"].items() if path.startswith(prefix)}
    actual = {path.name: _sha(path) for path in (root / "en-before").glob("*.lua")}
    assert actual == expected and actual, "baseline EN snapshot is not the initial bound output"
    generation = before["generation"]
    assert re.fullmatch(r"dvf33-[0-9a-f]{64}", generation), "invalid baseline generation"
    rendered = DATA_ROOT / "IrisLayer3Generations" / generation / "dvf_3_3_rendered.json"
    assert _sha(rendered) == before["subject_bindings"][rendered.relative_to(REPO).as_posix()]
    before["entries"] = _json(rendered)["entries"]
    before["owner"] = _json(root / "owner-before.json")
    assert _sha(root / "owner-before.json") == "8b58fc7e39fc0d139750eed5a031cecb615a1cdc8ef38a0f2a31c1aeedab4771"
    initial_manifest = Path("C:/Users/MW/Downloads/coding/PZ2/t2-final/tooltip_t2_projection_manifest.json")
    assert _sha(initial_manifest) == "2b4bee6ce9a262e727b57d7c254e7c2f2211780100cf1c222468a93419ef3efe"
    before["t2"] = _json(initial_manifest)
    original = subprocess.run(["git", "show", "b9d7ae289b226082c191b1f6a23e6b363c6d99a6:Iris/build/description/v2/data/dvf_3_3_facts.jsonl"], cwd=REPO, capture_output=True, check=True).stdout
    assert hashlib.sha256(original).hexdigest() == "e784cf76d2f7d51273eda44906c202c0548f0043027f60cf1af817336c03a6e9"
    before["facts"] = {row["item_id"]: row for row in map(json.loads, original.decode("utf-8").splitlines())}
    return before


def compare_menu_preservation(output: str, before: dict, subject: dict, final_manifest: dict) -> None:
    """The plan's exact per-record C delta, not a new validation authority."""
    candidate = _json(V2_DATA / "layer3_body_role_realign/approved_upstream/candidate_rendered.json")
    adoption = candidate["meta"]["general_description_integration"]
    targets = set(adoption["entries"])
    assert targets == set(before["missing_observations"]["KO"]) == set(before["missing_observations"]["EN"])
    assert len(targets) == 12
    assert before["entries"].keys() == subject["entries"].keys()
    changed = set()
    for key, old in before["entries"].items():
        new = subject["entries"][key]
        if old != new:
            changed.add(key)
            assert key in targets
            old_material, new_material = old["role_material"], new["role_material"]
            row = adoption["entries"][key]
            assert old_material["core_source_fact_ids"] == [row.get("predecessor_primary_use_fact_id", row["primary_use_fact_id"])]
            assert new_material["core_source_fact_ids"] == [row["primary_use_fact_id"]]
            assert {k: v for k, v in old_material.items() if k != "core_source_fact_ids"} == {
                k: v for k, v in new_material.items() if k != "core_source_fact_ids"}, "acquisition material changed"
            assert {k: v for k, v in old.items() if k not in {"text_ko", "source", "role_material"}} == {
                k: v for k, v in new.items() if k not in {"text_ko", "source", "role_material"}}, "unrelated Menu material changed"
            assert old["text_ko"] is None and new["text_ko"], "unexpected Menu visibility transition"
    assert changed == targets, "Menu changed set differs from adopted exact targets"
    facts = {row["item_id"]: row for row in map(json.loads, (V2_DATA / "dvf_3_3_facts.jsonl").read_text(encoding="utf-8").splitlines())}
    assert facts.keys() == before["facts"].keys()
    for key, old in before["facts"].items():
        omitted = {"primary_use", "special_context"} if key in targets else set()
        assert {k: v for k, v in old.items() if k not in omitted} == {
            k: v for k, v in facts[key].items() if k not in omitted}, "unrelated source fact changed"
    assert final_manifest["fulltypes"].keys() == before["t2"]["fulltypes"].keys()
    assert final_manifest["line_distribution"] == before["t2"]["line_distribution"]
    for key, old in before["t2"]["fulltypes"].items():
        new = final_manifest["fulltypes"][key]
        assert {k: v for k, v in old.items() if k != "lines"} == {k: v for k, v in new.items() if k != "lines"}, "T2 row/slot layout changed"
        assert len(old["lines"]) == len(new["lines"])
        for old_line, new_line in zip(old["lines"], new["lines"], strict=True):
            if key in targets and old_line["slot_id"] == "S2":
                row = adoption["entries"][key]
                assert old_line["semantic_identity"] == row["predecessor_primary_use_fact_id"]
                assert new_line["semantic_identity"] == row["primary_use_fact_id"]
                assert {k: v for k, v in old_line.items() if k not in {"semantic_identity", "surface_sha256"}} == {
                    k: v for k, v in new_line.items() if k not in {"semantic_identity", "surface_sha256"}}
                for locale, text in row["localized_general_description"].items():
                    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
                    assert new_line["surface_sha256"][locale] == {"source_sha256": digest, "final_sha256": digest}
            else:
                assert new_line == old_line, "unrelated T2 S1/S2/S3/S4 changed"
    observed = {"KO": {}, "EN": {}}
    old_en = {}
    routing_changes = 0
    for line in output.splitlines():
        fields = line.split("\t")
        if fields[0] == "MENU_L3":
            _, locale, key, module, raw = fields
            assert key not in observed[locale]
            observed[locale][key] = bytes.fromhex(raw).decode("utf-8")
        elif fields[0] == "MENU_BASELINE_EN":
            _, key, raw = fields
            assert key not in old_en
            old_en[key] = bytes.fromhex(raw).decode("utf-8")
    expected_ko = {key: row["text_ko"] for key, row in subject["entries"].items() if row.get("text_ko")}
    assert observed["KO"] == expected_ko, "actual KO Menu differs from final input"
    assert observed["EN"].keys() == old_en.keys() | targets and not old_en.keys() & targets
    assert all(observed["EN"][key] == text for key, text in old_en.items()), "non-target EN text changed"
    for key, row in adoption["entries"].items():
        for locale in ("KO", "EN"):
            assert observed[locale][key].split("\n\n", 1)[0] == row["localized_general_description"][locale.lower()], "adopted detail duplicated or replaced"
    owner = _json(V2_DATA / "tooltip_t1_layer3_owner_input.json")
    assert owner["generation_id"] == subject["generation"]
    assert before["owner"]["absence_entries"] == owner["absence_entries"] and len(owner["absence_entries"]) == 175
    assert before["owner"]["entries"].keys() == owner["entries"].keys()
    for key, old in before["owner"]["entries"].items():
        new = owner["entries"][key]
        omitted = {"authority_ref"}
        if key in targets and adoption["decision"] == "user_adopted_build41_description_correction":
            row = adoption["entries"][key]
            assert old["fact_id"] == row["predecessor_primary_use_fact_id"]
            assert new["fact_id"] == row["primary_use_fact_id"] and new["source_fact_ids"] == [row["primary_use_fact_id"]]
            assert new["localized_surfaces"] == row["localized_general_description"]
            omitted |= {"fact_id", "source_fact_ids", "localized_surfaces"}
        assert {k: v for k, v in old.items() if k not in omitted} == {
            k: v for k, v in new.items() if k not in omitted}, "unrelated Tooltip semantic or surface changed"
    # Chunk boundary changes are physical routing changes, never text changes.
    for path, sha in before["subject_bindings"].items():
        if path.startswith("Iris/media/lua/client/Iris/Data/Layer3English/") and _sha(REPO / path) != sha:
            routing_changes += 1
    print("MENU_PRESERVATION\t" + json.dumps({
        "changed_exact_set": sorted(targets), "unchanged_selected_count": 1302,
        "unchanged_existing_en_records": len(old_en), "public_records": len(expected_ko),
        "non_target_role_material_and_tooltip_surfaces_unchanged": True,
        "target_core_and_s2_correction_count": len(targets) if adoption["decision"] == "user_adopted_build41_description_correction" else 0,
        "t2_row_count_transitions": {key: {"before": before["t2"]["fulltypes"][key]["line_count"], "after": final_manifest["fulltypes"][key]["line_count"]} for key in sorted(targets)},
        "line_distribution": final_manifest["line_distribution"],
        "support_count": len(final_manifest["fulltypes"]),
        "unrelated_source_facts_preserved": len(facts) - len(targets),
        "absence_entries_unchanged": 175, "changed_en_files": routing_changes,
        "content_adoption": adoption["decision"], "independent_game_source_verification": "not_performed",
    }, sort_keys=True))


def run_harness(mode: str = "full", baseline_en_root: Path | None = None) -> str:
    if mode not in {"full", "replacement", "smoke", "menu"}:
        raise ValueError("expected full, replacement, smoke, or menu")
    lua = shutil.which("lua")
    if lua is None:
        raise RuntimeError("BLOCKED: standalone Lua is required")
    if hashlib.sha256(PAYLOAD.read_bytes()).hexdigest() != EXPECTED_SHA256:
        raise AssertionError("T2 product bytes differ from admitted payload")
    completed = subprocess.run(
        [lua, str(REPO / "Iris/test/lua/tooltip_static_data_runtime_harness.lua"), str(REPO), mode]
        + ([str(baseline_en_root)] if baseline_en_root else []),
        cwd=REPO, text=True, encoding="utf-8", capture_output=True, timeout=60,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stdout + completed.stderr)
    if f"IRIS_TOOLTIP_T3_PASS mode={mode}" not in completed.stdout:
        raise AssertionError("missing harness completion marker")
    return completed.stdout


def menu_relations(output: str, manifest_path: Path, *,
                   en_identity_evidence: MenuEvidence | None = None) -> None:
    """Compare actual consumer observations with the admitted offline input.

    EN source observation is not an independent fact identity certificate.
    No production IDs, text parsing, or new authority mapping are introduced.
    Only a current producer/input/output-bound reconstruction can supply EN
    relations. Bare Tooltip/module tuples are insufficient. No authority-backed
    non-required scope is introduced: Branch C restores the 12 Menu bodies
    while retaining the initial selected universe in both locales.
    """
    manifest = _json(manifest_path)
    subject = menu_subject()
    l3 = {"KO": {}, "EN": {}}
    absent = {"KO": {}, "EN": {}}
    l4 = {"KO": {}, "EN": {}}
    for line in output.splitlines():
        fields = line.split("\t")
        if fields[0] == "MENU_L3":
            assert len(fields) == 5, "stale Menu observation without payload identity"
            _, locale, key, module, encoded = fields
            assert key not in l3[locale] and key not in absent[locale], "duplicate Menu observation"
            text = bytes.fromhex(encoded).decode("utf-8")
            assert text, "empty public Menu observation"
            l3[locale][key] = (module, hashlib.sha256(text.encode("utf-8")).hexdigest())
        elif fields[0] == "MENU_L3_ABSENT":
            _, locale, key, reason = fields
            assert key not in l3[locale] and key not in absent[locale], "duplicate Menu observation"
            absent[locale][key] = reason
        elif fields[0] == "MENU_L4":
            _, locale, key, identity, source = fields
            l4[locale].setdefault(key, set()).add((identity, source))
    selected = {k: next(row["semantic_identity"] for row in v["lines"] if row["slot_id"] == "S2")
                for k, v in manifest["fulltypes"].items() if "S2" in v["present_slots"]}
    initial_selected, transitions = predecessor_selected(selected, subject.get("usefulness_corrections", {}))
    adoption = subject.get("adoption", {})
    if adoption.get("decision") == "user_adopted_build41_description_correction":
        for key, row in adoption["entries"].items():
            if "predecessor_primary_use_fact_id" not in row:
                continue  # New Menu context keeps the core bound by usefulness_corrections.
            assert selected.get(key) == row["primary_use_fact_id"], "stale T2 fact after content correction"
            initial_selected[key] = row["predecessor_primary_use_fact_id"]
            transitions[key] = {"before": initial_selected[key], "after": selected[key]}
    assert len(initial_selected) == 1314, "initial selected ledger membership changed"
    expected_pairs = hashlib.sha256(json.dumps(sorted(initial_selected.items()), ensure_ascii=True,
                                              separators=(",", ":")).encode()).hexdigest()
    assert expected_pairs == "c5db8a28892229df25f9b65b22e045515b3ac1fcc0d476bb8a1231131832cd28", "initial selected ledger identity changed"
    failures = []
    for locale in ("KO", "EN"):
        if l3[locale].keys() | absent[locale].keys() != manifest["fulltypes"].keys():
            failures.append((locale, "observation universe mismatch",
                             sorted((l3[locale].keys() | absent[locale].keys()) ^ manifest["fulltypes"].keys())))
        missing = sorted(selected.keys() - l3[locale].keys())
        print(f"Menu L3 {locale}: selected source observations={len(selected)-len(missing)}, missing={len(missing)}")
        if missing:
            failures.append((locale, "L3 source missing", missing))
    ko_verified = set()
    for key, fact_id in selected.items():
        if key not in l3["KO"]:
            continue
        module, text_sha = l3["KO"][key]
        entry = subject["entries"].get(key, {})
        module_prefix = f'Iris/Data/IrisLayer3Generations/{subject["generation"]}/Chunks/'
        if (module.startswith(module_prefix)
                and entry.get("role_material", {}).get("core_source_fact_ids") == [fact_id]
                and text_sha == hashlib.sha256((entry.get("text_ko") or "").encode("utf-8")).hexdigest()):
            ko_verified.add(key)
        else:
            failures.append(("KO", "L3 identity mismatch", key))
    print(f"Menu L3 KO: observed record -> existing generation fact mapping matched={len(ko_verified)}/{len(selected)}")
    trace = en_identity_evidence
    valid_trace = (isinstance(trace, MenuEvidence)
                   and trace.method == "current_deterministic_derivability"
                   and trace.generation == subject["generation"]
                   and bool(trace.bindings) and trace.bindings == subject["bindings"])
    en_evidence = trace.records if valid_trace else {}
    if trace is not None and not valid_trace:
        failures.append(("EN", "L3 evidence binding mismatch", "producer/input/output/generation"))
    en_unverified = []
    en_mismatched = []
    en_verified = set()
    for key, fact_id in selected.items():
        relation = en_evidence.get(key)
        if relation is None:
            en_unverified.append(key)
        elif key not in l3["EN"] or relation != (l3["EN"][key][0], fact_id, l3["EN"][key][1]):
            en_mismatched.append(key)
        elif key in l3["EN"]:
            en_verified.add(key)
    print(f"Menu L3 EN: independent identity matched={len(en_verified)}, "
          f"unverified={len(en_unverified)}, mismatch={len(en_mismatched)}")
    if en_unverified:
        failures.append(("EN", "L3 identity unverified", sorted(en_unverified)))
    if en_mismatched:
        failures.append(("EN", "L3 identity mismatch", sorted(en_mismatched)))
    # Branch C leaves final requirements equal to the initial ledger.
    resolved = ko_verified & en_verified
    unresolved = selected.keys() - resolved
    report = {
        "initial_selected_pair_sha256": expected_pairs,
        "final_selected_pair_sha256": hashlib.sha256(json.dumps(sorted(selected.items()), ensure_ascii=True, separators=(",", ":")).encode()).hexdigest(),
        "final_required_scope": "initial_fulltypes_and_adopted_new_core_facts" if transitions else "initial_selected_unchanged",
        "fact_identity_transitions": transitions,
        "generation": subject["generation"],
        "evidence_method": trace.method if valid_trace else "missing",
        "subject_bindings": subject["bindings"],
        "verified_records": {key: {"KO": l3["KO"][key], "EN": l3["EN"][key], "fact": selected[key]}
                             for key in sorted(resolved)},
        "resolved_exact_set": sorted((key, initial_selected[key]) for key in resolved if key in initial_selected),
        "retained_exact_set": [],
        "unresolved_exact_set": sorted((key, initial_selected[key]) for key in unresolved if key in initial_selected),
        "newly_selected_resolved_exact_set": sorted((key, selected[key]) for key in resolved if key not in initial_selected),
        "newly_selected_unresolved_exact_set": sorted((key, selected[key]) for key in unresolved if key not in initial_selected),
        "missing_observations": {locale: {key: absent[locale].get(key, "observation_missing")
                                         for key in sorted(selected.keys() - l3[locale].keys())}
                                 for locale in ("KO", "EN")},
        "sealed_authority_rewritten": False,
    }
    assert resolved.isdisjoint(unresolved) and resolved | unresolved == selected.keys()
    print(f"Inherited Menu evidence: resolved={len(resolved)}, retained=0, unresolved={len(unresolved)}")
    print("MENU_RELATION_REPORT\t" + json.dumps(report, ensure_ascii=True, sort_keys=True))
    for locale in ("KO", "EN"):
        compared = 0
        missing_l4 = []
        for key, record in manifest["fulltypes"].items():
            for row in record["lines"]:
                if row["slot_id"] not in {"S3", "S4"}:
                    continue
                identity = row["semantic_identity"]
                source = "recipe" if identity.startswith("uc.recipe.") else "rightclick"
                if (identity, source) in l4[locale].get(key, set()):
                    compared += 1
                else:
                    missing_l4.append((key, identity, source))
        print(f"Menu L4 {locale}: selected identity/source subset matched={compared}, missing={len(missing_l4)}")
        if missing_l4:
            failures.append((locale, "L4 source missing", missing_l4))
    if failures:
        print(json.dumps(failures, ensure_ascii=True))
        raise AssertionError("Menu relation incomplete; required scope is unchanged")



class BrowserStateSelectionSearchAcceptanceTest(unittest.TestCase):
    def test_actual_standalone_lua_state_and_cache_contracts(self) -> None:
        for locale, expected_sha in (
            ("KO", "0ea2f9f5747a5845347ccdbb02e48948f3b3b6218d971800dd8d77afe4f2c5de"),
            ("EN", "98066208a95aad2113326d4f7b7d022ee3658e31f721802af9d43ab38c1de488"),
        ):
            corpus = REPO / f"lua/shared/Translate/{locale}/ItemName_{locale}.txt"
            self.assertEqual(expected_sha, _sha(corpus), f"{locale} search corpus changed")
        lua = shutil.which("lua")
        self.assertIsNotNone(lua, "required standalone Lua executable is unavailable")
        completed = subprocess.run(
            [lua, str(REPO / "Iris/test/lua/browser_state_acceptance_harness.lua"), str(REPO)],
            cwd=REPO,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            timeout=60,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("IRIS_BROWSER_STANDALONE_PASS", completed.stdout)
        self.assertIn("normalized_getter_calls=6", completed.stdout)
        self.assertIn("optional_load_calls=2", completed.stdout)
        self.assertIn("folded_cache_entries=1", completed.stdout)
        self.assertIn("get_all_items_calls=1", completed.stdout)
        self.assertIn("recovery_get_all_items_calls=2", completed.stdout)
        self.assertIn("prefix_reuse_count=1", completed.stdout)
        self.assertIn("tooltip_static_lookups=2", completed.stdout)
        self.assertIn("SEARCH_CORPUS locale=KO raw=2017 exact=2007 queries=1661 violations=0", completed.stdout)
        self.assertIn("SEARCH_CORPUS locale=EN raw=1974 exact=1974 queries=1615 violations=0", completed.stdout)
        self.assertIn("SEARCH_CONTRACT quality=passed identity=passed transitions=passed controller=passed", completed.stdout)
        print("\n".join(line for line in completed.stdout.splitlines() if line.startswith("SEARCH_")))
        runtime = run_harness()
        self.assertIn("exact_keys=2280", runtime)
        self.assertIn("legacy_calls=0", runtime)

    def test_browserdata_compatibility_and_logging_source_guards(self) -> None:
        browser_root = REPO / "Iris/media/lua/client/Iris/UI/Browser"
        data_path = browser_root / "IrisBrowserData.lua"
        data_text = data_path.read_text(encoding="utf-8")
        self.assertEqual(1, data_text.count("IrisBrowserData._built ="))
        self.assertIn("function IrisBrowserData.getBuildState()", data_text)
        self.assertIn("function IrisBrowserData.isReady()", data_text)
        self.assertIn("function IrisBrowserData.ensureReady()", data_text)
        self.assertIn("function IrisBrowserData.getInstrumentation()", data_text)
        self.assertIn("IrisBrowserLifecycle", data_text)
        self.assertIn("IrisBrowserMetrics", data_text)

        projection = (browser_root / "IrisBrowserProjectionBuilder.lua").read_text(encoding="utf-8")
        lifecycle = (browser_root / "IrisBrowserLifecycle.lua").read_text(encoding="utf-8")
        metrics = (browser_root / "IrisBrowserMetrics.lua").read_text(encoding="utf-8")
        self.assertIn("function IrisBrowserProjectionBuilder.build", projection)
        self.assertIn("function IrisBrowserLifecycle.create", lifecycle)
        self.assertIn("function IrisBrowserMetrics.create", metrics)
        self.assertNotIn("function IrisBrowserData.ensureReady", lifecycle)

        main = (REPO / "Iris/media/lua/client/Iris/IrisMain.lua").read_text(encoding="utf-8")
        self.assertIn('ready = "BrowserData demand-build boundary ready"', main)
        self.assertNotIn("invoke = buildBrowserData", main)
        self.assertNotIn("local function buildBrowserData", main)

        forbidden = []
        for path in browser_root.glob("*.lua"):
            if path == data_path:
                continue
            text = path.read_text(encoding="utf-8")
            if "IrisBrowserData._built" in text or "BrowserData._built" in text:
                forbidden.append(path.name)
        self.assertEqual([], forbidden)

        controller = (browser_root / "IrisBrowserListController.lua").read_text(encoding="utf-8")
        self.assertIn("resolveSelectedPayload", controller)
        self.assertNotIn("for k, v in pairs(item)", controller)
        self.assertNotIn("for k, v in pairs(itemData)", controller)

        query = (browser_root / "IrisBrowserQuery.lua").read_text(encoding="utf-8")
        self.assertIn("searchSnapshot", query)
        self.assertIn("rowsByFullType", query)
        self.assertIn("prefixReuseCount", query)
        self.assertIn("copyRows", query)
        self.assertNotIn("table.sort(result", query)
        classification = (browser_root / "IrisBrowserClassificationIndex.lua").read_text(encoding="utf-8")
        self.assertIn("function IrisBrowserClassificationIndex.addTag", classification)
        self.assertNotIn("function IrisBrowserClassificationIndex.addItem", classification)
        static_data = (REPO / "Iris/media/lua/client/Iris/API/StaticData.lua").read_text(encoding="utf-8")
        self.assertIn("function StaticData.getFailureReason(key)", static_data)
        self.assertIn("function StaticData.reset(key)", static_data)

        # Isolate the relation verdict from Lua/runtime execution. All source,
        # KO identity, and L4 comparisons succeed in this common fixture; only
        # the explicitly supplied EN evidence varies. Nothing is written.
        owner = json.loads((REPO / "Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json").read_text(encoding="utf-8"))
        selected = {key: row["fact_id"] for key, row in owner["entries"].items()}
        corrections = {row["item_id"]: row["slot_meta"]["usefulness_correction"]
                       for row in (json.loads(line) for line in (V2_DATA / "dvf_3_3_facts.jsonl").read_text(encoding="utf-8").splitlines())
                       if row.get("slot_meta", {}).get("usefulness_correction")}
        selected, _ = predecessor_selected(selected, corrections)
        adopted = _json(V2_DATA / "layer3_body_role_realign/approved_upstream/candidate_rendered.json")["meta"]["general_description_integration"]
        for key, row in adopted["entries"].items():
            if "predecessor_primary_use_fact_id" in row:
                selected[key] = row["predecessor_primary_use_fact_id"]
        fixture_manifest = {"fulltypes": {key: {
            "present_slots": ["S2", "S3"],
            "lines": [{"slot_id": "S2", "semantic_identity": fact_id},
                      {"slot_id": "S3", "semantic_identity": "uc.recipe.fixture"}],
        } for key, fact_id in selected.items()}}
        fixture_generation = {"entries": {key: {
            "role_material": {"core_source_fact_ids": [fact_id]},
            "text_ko": "fixture KO body",
        } for key, fact_id in selected.items()}}
        manifest_path = REPO / "Iris/test/lua/tooltip-t3-menu-fixture.json"
        ko_module = "Iris/Data/IrisLayer3Generations/fixture/Chunks/Chunk001"
        en_module = "Iris/Data/Layer3English/Chunk001"
        fixture_subject = {"generation": "fixture", "entries": fixture_generation["entries"],
                           "bindings": {"producer": "p", "input": "i", "output": "o", "pointer": "g"}}
        en_text = "fixture EN body"
        en_sha = hashlib.sha256(en_text.encode()).hexdigest()
        observations = "\n".join(line for key in selected for line in (
            f"MENU_L3\tKO\t{key}\t{ko_module}\t{'fixture KO body'.encode().hex()}",
            f"MENU_L3\tEN\t{key}\t{en_module}\t{en_text.encode().hex()}",
            f"MENU_L4\tKO\t{key}\tuc.recipe.fixture\trecipe",
            f"MENU_L4\tEN\t{key}\tuc.recipe.fixture\trecipe",
        ))
        def fixture_read(path: Path, *args, **kwargs) -> str:
            return json.dumps(fixture_manifest if path == manifest_path else fixture_generation)

        complete_evidence = MenuEvidence("fixture", fixture_subject["bindings"],
                                         {key: (en_module, fact_id, en_sha) for key, fact_id in selected.items()})
        first = next(iter(selected))
        cases = [(None, "L3 identity unverified"),
                 ({key: (en_module, fact) for key, fact in selected.items()}, "L3 evidence binding mismatch"),
                 (replace(complete_evidence, generation="stale"), "L3 evidence binding mismatch"),
                 (replace(complete_evidence, method="tooltip_self_attestation"), "L3 evidence binding mismatch"),
                 (complete_evidence, None)]
        for binding in fixture_subject["bindings"]:
            cases.append((replace(complete_evidence, bindings={**complete_evidence.bindings, binding: "wrong"}),
                          "L3 evidence binding mismatch"))
        for relation in ((en_module, "wrong-fact", en_sha),
                         ("Iris/Data/Layer3English/Chunk999", selected[first], en_sha),
                         (en_module, selected[first], "wrong-text")):
            cases.append((replace(complete_evidence, records={**complete_evidence.records, first: relation}),
                          "L3 identity mismatch"))
        for evidence, failure_kind in cases:
            captured = StringIO()
            with patch.object(Path, "read_text", fixture_read), patch(__name__ + ".menu_subject", return_value=fixture_subject), redirect_stdout(captured):
                if failure_kind:
                    with self.assertRaisesRegex(AssertionError, "Menu relation incomplete"):
                        menu_relations(observations, manifest_path, en_identity_evidence=evidence)
                else:
                    menu_relations(observations, manifest_path, en_identity_evidence=evidence)
            self.assertNotIn("L3 source missing", captured.getvalue())
            self.assertNotIn("L4 source missing", captured.getvalue())
            if failure_kind:
                self.assertIn(failure_kind, captured.getvalue())
            self.assertIn("missing=0", captured.getvalue())
            report = json.loads(next(line.split("\t", 1)[1] for line in captured.getvalue().splitlines()
                                     if line.startswith("MENU_RELATION_REPORT\t")))
            groups = [set(map(tuple, report[name])) for name in
                      ("resolved_exact_set", "retained_exact_set", "unresolved_exact_set")]
            self.assertEqual(set(selected.items()), set.union(*groups))
            self.assertFalse(groups[0] & groups[2])
            self.assertFalse(groups[1])

        # Missing public records cannot become retained merely by saying silence.
        missing = "\n".join(line for line in observations.splitlines()
                            if not line.startswith((f"MENU_L3\tKO\t{first}\t", f"MENU_L3\tEN\t{first}\t")))
        missing += f"\nMENU_L3_ABSENT\tKO\t{first}\tno_public_body\nMENU_L3_ABSENT\tEN\t{first}\tno_public_body"
        for observed, failure_kind in ((missing, "Menu relation incomplete"),
                                       (observations + "\n" + observations.splitlines()[0], "duplicate Menu observation")):
            with patch.object(Path, "read_text", fixture_read), patch(__name__ + ".menu_subject", return_value=fixture_subject), redirect_stdout(StringIO()):
                with self.assertRaisesRegex(AssertionError, failure_kind):
                    menu_relations(observed, manifest_path, en_identity_evidence=complete_evidence)
        removed = {"fulltypes": {key: row for key, row in fixture_manifest["fulltypes"].items() if key != first}}
        duplicated = '{"fulltypes":{"duplicate":{},"duplicate":{}}}'
        for raw, failure_kind in ((json.dumps(removed), "initial selected ledger membership"),
                                  (duplicated, "duplicate exact key")):
            with patch.object(Path, "read_text", return_value=raw), patch(__name__ + ".menu_subject", return_value=fixture_subject):
                with self.assertRaisesRegex(AssertionError, failure_kind):
                    menu_relations(observations, manifest_path, en_identity_evidence=complete_evidence)

        # Exercise the adopted-input boundary in this existing family. The
        # actual EN producer/serializer run remains the separate final replay.
        from iris_tooling.build import build_layer3_english_localization as producer
        candidate_path = V2_DATA / "layer3_body_role_realign/approved_upstream/candidate_rendered.json"
        candidate = _json(candidate_path)
        facts = {row["item_id"]: row for row in (
            json.loads(line) for line in (V2_DATA / "dvf_3_3_facts.jsonl").read_text(encoding="utf-8").splitlines() if line)}
        from iris_tooling.build.compose_layer3_shared import approved_compositions
        composed = approved_compositions(REPO, candidate["entries"])
        material = producer.approved_general_descriptions(REPO, facts, candidate["entries"], composed)
        self.assertEqual(set(candidate["meta"]["general_description_integration"]["entries"]) - set(composed), set(material))
        target = next(iter(material))
        original_read = Path.read_text
        for field, replacement, failure in (
            ("context_source_sha256", "wrong", "SOURCE_MISMATCH"),
            ("context_fact_id", "wrong", "CONTEXT_ID_MISMATCH"),
            ("primary_use_fact_id", "wrong", "CORE_MISMATCH"),
            ("localized_general_description", {"ko": "wrong", "en": material[target]["en"]}, "LOCALE_MISMATCH"),
        ):
            mutated = json.loads(json.dumps(candidate))
            mutated["meta"]["general_description_integration"]["entries"][target][field] = replacement
            def read_candidate(path, *args, **kwargs):
                return json.dumps(mutated) if path.resolve() == candidate_path.resolve() else original_read(path, *args, **kwargs)
            with patch.object(Path, "read_text", read_candidate), self.assertRaisesRegex(RuntimeError, failure):
                producer.approved_general_descriptions(REPO, facts, candidate["entries"], composed)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in {"full", "replacement", "smoke", "menu"}:
        parser = argparse.ArgumentParser()
        parser.add_argument("mode", choices=("full", "replacement", "smoke", "menu"))
        parser.add_argument("manifest", type=Path, nargs="?")
        parser.add_argument("--en-replay-root", type=Path)
        parser.add_argument("--baseline-root", type=Path)
        args = parser.parse_args()
        if args.en_replay_root and not args.manifest:
            parser.error("EN reconstruction requires an explicit admitted T2 manifest")
        if args.baseline_root and (not args.manifest or not args.en_replay_root):
            parser.error("final preservation requires the admitted manifest and EN reconstruction")
        subject, evidence = None, None
        if args.manifest:
            if args.mode not in {"menu", "full"}:
                parser.error("Menu relation requires menu or full mode")
            route = _json(REPO / "Iris/_docs/authority/iris_current_route_index.json")["tooltip_t2_static_staging"]
            admitted = Path(route["final_root"]) / "tooltip_t2_projection_manifest.json"
            assert args.manifest.resolve() == admitted.resolve(), "manifest is not the current admitted T2 input"
            assert _sha(args.manifest) == route["artifact_sha256"][admitted.name], "T2 manifest binding mismatch"
            assert _sha(PAYLOAD) == route["artifact_sha256"][PAYLOAD.name], "T2 product binding mismatch"
            subject = menu_subject()
            if args.en_replay_root:
                evidence = reconstruct_menu_evidence(args.en_replay_root, subject)
        baseline = load_menu_baseline(args.baseline_root) if args.baseline_root else None
        output = run_harness(args.mode, args.baseline_root / "en-before" if args.baseline_root else None)
        visible = [line for line in output.splitlines()
                   if not line.startswith(("MENU_L3\t", "MENU_L3_ABSENT\t", "MENU_L4\t", "MENU_BASELINE_EN\t"))]
        if args.mode == "menu":
            visible = [line for line in visible if not line.startswith("IRIS_TOOLTIP_T3_PASS")]
            visible.append("Menu source observation finished; no relation PASS is implied.")
        print("\n".join(visible))
        if args.manifest:
            assert menu_subject() == subject, "Menu changed during consumer observation"
            assert _sha(args.manifest) == route["artifact_sha256"][admitted.name]
            assert _sha(PAYLOAD) == route["artifact_sha256"][PAYLOAD.name]
            if baseline:
                compare_menu_preservation(output, baseline, subject, _json(args.manifest))
            menu_relations(output, args.manifest, en_identity_evidence=evidence)
            print("Menu relation PASS: all required source and identity evidence matched.")
    else:
        unittest.main()
