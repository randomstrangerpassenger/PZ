"""DVF-L3-02 G1: one contract gate, no product writer or secondary runner."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, patch

from iris_tooling.domains.layer3 import investigation as inv


REPO = Path(__file__).resolve().parents[5]
AUTH = "Iris/_docs/authority/iris_current_authority_manifest.json"
ROUTE = "Iris/_docs/authority/iris_current_route_index.json"
REGISTRY = "Iris/validation/execution/required_validations.json"
POLICY = "Iris/_docs/round3/round3_pytest_source_classification.json"
ENTRY = "layer3_investigation_contract"


def adoption_baseline():
    mode = os.environ.get("IRIS_LAYER3_INVESTIGATION_MODE")
    inv.require(mode in {None, "adoption"}, "unknown investigation mode")
    if mode is None:
        return None
    raw = os.environ.get("IRIS_LAYER3_INVESTIGATION_BASELINE")
    inv.require(bool(raw), "adoption baseline missing")
    path = Path(raw)
    inv.require(path.is_absolute() and path.resolve().is_relative_to(REPO), "baseline must be local and absolute")
    try:
        baseline = inv.read_json(path)
        inv.require(re.fullmatch(r"[0-9a-f]{40}", baseline["execution_start_head"]) is not None,
                    "invalid execution start HEAD")
        inv.require(isinstance(baseline["dirty"], list) and bool(baseline["protected"])
                    and bool(baseline["generation_members"]) and set(baseline["configs"]) == {AUTH, ROUTE, REGISTRY, POLICY},
                    "incomplete baseline")
    except (KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        raise ValueError("damaged adoption baseline") from exc
    return baseline


def route(profile, state="confirmed_applicable", scope="activity:a"):
    return {"profile_id": profile, "state": state,
            "scope_refs": [scope] if state == "confirmed_applicable" else [],
            "evidence_refs": ["synthetic-observation"], "reason": "Independent bounded fixture observation"}


def terminal_fixture(kind="acquisition"):
    fact = {"fact_id": "f1", "item_id": "Base.Sample", "fact_kind": kind,
            "status": "accepted", "payload": {"scope": "synthetic closed source scope"}, "provenance_refs": ["p"]}
    result = {"item_id": "Base.Sample", "axis_id": "acquisition", "scope_ref": "item", "state": "resolved",
              "authority_ref": "external-fixture", "question_coverage": "whole_scope", "provenance_refs": ["p"], "fact_refs": ["f1"]}
    source = {"path": "synthetic-source.json", "sha256": "a" * 64}
    authority = {"authority_id": "external-fixture", "status": "adopted", "binding": {"path": "fixture.json", "sha256": "b" * 64},
                 "facts": [fact], "results": [result], "source_bindings": [source],
                 "provenance": {"p": {"source_sha256": source["sha256"], "locator": "closed fixture scope"}}}
    if kind == "acquisition_unobtainable":
        fact["negative_evidence_refs"] = ["n"]
        authority["negative_evidence"] = {"n": {"item_id": "Base.Sample", "closed_scope": True,
            "coverage_complete": True, "false_negative_limit": "excluded_within_bound_scope",
            "scope_description": "Entire fixture world source set, not a claim about PZ",
            "source_bindings": [source], "authority_ref": "external-fixture"}}
    return result, authority


class Layer3InvestigationContractTest(unittest.TestCase):
    def test_investigation_contract(self):
        baseline = adoption_baseline()
        contract = inv.read_json(REPO / inv.ROOT / "contract.json")
        inv.validate_contract(contract)
        inherited = inv.inherited_contract(REPO, contract["inherits"])
        manifest = inv.read_json(REPO / inv.ROOT / "manifest.json")
        self.assertEqual(manifest["schema_version"], "iris-layer3-investigation-manifest-v1")
        self.assertEqual(manifest["revision"], contract["revision"])
        self.assertEqual(manifest["inherits"], contract["inherits"])
        self.assertEqual(manifest["status"], "adoption_subject")
        self.assertEqual(manifest["adoption_requires"], inv.TEST_ID)
        expected_members = {inv.ROOT + "/" + name for name in ("contract.json", "evidence.jsonl", "applications.jsonl")} | {inv.HUMAN}
        self.assertEqual({m["path"] for m in manifest["members"]}, expected_members)
        self.assertEqual(len(manifest["members"]), 4)
        for member in manifest["members"]:
            self.assertEqual(inv.binding(REPO, member["path"]), member)
        self.assertEqual(manifest["target_sources"], [inv.binding(REPO, path) for path in inv.TARGET_PATHS])
        target = inv.targets(REPO)
        self.assertEqual(manifest["target_count"], len(target))
        self.assertEqual(manifest["target_set_sha256"], inv.set_digest(target))
        self.assertNotEqual(inv.set_digest(["Base.X"]), inv.set_digest(["base.X"]))
        for rows in ([{"item_id": ""}], [{"item_id": None}], [{"item_id": "A"}, {"item_id": "A"}]):
            with self.assertRaises(ValueError):
                inv.exact_rows(rows)
        self.assertEqual(set(inv.exact_rows([{"item_id": "Base.X"}, {"item_id": "base.X"}])), {"Base.X", "base.X"})
        with patch.object(inv, "read_rows", side_effect=[[{"item_id": "A"}], [{"item_id": "a"}]]):
            with self.assertRaises(ValueError):
                inv.targets(REPO)

        # One real source application/recalculation shared by all full-target checks.
        evidence = inv.read_rows(REPO / inv.ROOT / "evidence.jsonl")
        stored = inv.read_rows(REPO / inv.ROOT / "applications.jsonl")
        self.assertEqual(sorted(inv.exact_rows(evidence)), target)
        self.assertEqual(sorted(inv.exact_rows(stored)), target)
        fresh_evidence = inv.source_observations(REPO, contract, target)
        self.assertEqual(evidence, fresh_evidence)
        recalculated = inv.applications(contract, fresh_evidence, inherited)
        self.assertEqual(stored, recalculated)
        by_id = inv.exact_rows(stored)
        observed = inv.exact_rows(evidence)
        for row in stored:
            self.assertEqual(len(row["routing"]), len(contract["profiles"]))
            self.assertEqual(len([a for a in row["required_axes"] if a["axis_id"] == "acquisition"]), 1)
            self.assertEqual(row["item_investigation_state"], "incomplete")
            self.assertEqual(row["acquisition_state"], "not_investigated")
            self.assertTrue(row["blockers"])
            self.assertTrue(all(b.get("question") and b.get("missing") and b.get("next") for b in row["blockers"]))
        def confirmed(item):
            return {r["profile_id"] for r in by_id[item]["routing"] if r["state"] == "confirmed_applicable"}
        self.assertTrue({"ingestion", "cooking"} <= confirmed("Base.Apple"))
        self.assertTrue({"combat", "world_work"} <= confirmed("Base.Hammer"))
        self.assertIn("storage", confirmed("Base.Bag_Schoolbag"))
        self.assertIn("reading", confirmed("Base.Notebook"))
        self.assertIn("expenditure", confirmed("Base.Battery"))
        self.assertEqual(observed["Base.Dogfood"]["raw_item"]["fields"]["CantEat"], "TRUE")
        self.assertEqual({r["role"] for r in observed["Base.Plank"]["recipe_links"]}, {"input", "keep"})
        apple_first = {(a["axis_id"], a["scope_ref"]) for a in by_id["Base.Apple"]["first_contact"]}
        self.assertTrue({("effects", "activity:ingestion"), ("role", "activity:cooking")} <= apple_first)
        self.assertFalse(any(a["axis_id"] == "acquisition" for r in stored for a in r["first_contact"]))

        for change in ("duplicate", "axis", "first", "predicate"):
            invalid = deepcopy(contract)
            if change == "duplicate":
                invalid["profiles"].append(invalid["profiles"][0])
            elif change == "axis":
                invalid["profiles"][0]["required_axes"] = ["unknown"]
            elif change == "first":
                invalid["profiles"][0]["first_contact"][0]["detail_boundary"] = ""
            else:
                invalid["profiles"][0]["routing"]["kind"] = "category_guess"
            with self.subTest(schema=change), self.assertRaises(ValueError):
                inv.validate_contract(invalid)
        stale = deepcopy(evidence[:1])
        stale[0]["registry_revision"] = "old"
        with self.assertRaises(ValueError):
            inv.applications(contract, stale, inherited)
        wrong_binding = {**contract["inherits"], "sha256": "0" * 64}
        with self.assertRaises(ValueError):
            inv.inherited_contract(REPO, wrong_binding)
        with self.assertRaises(ValueError):
            inv.local_path(REPO, "../outside.json")

        # Small independently expected contexts, scope conflicts and sparse completion.
        small = deepcopy(contract)
        template = deepcopy(contract["profiles"][0])
        small["profiles"] = [{**deepcopy(template), "profile_id": p, "required_axes": ["operation"],
                              "first_contact": [template["first_contact"][0]]} for p in ("p", "q")]
        clear = {"state": "assessed_clear", "evidence_refs": ["synthetic-whole-scope-assessment"]}
        routes = [route("p"), route("q"), route("q", scope="activity:b")]
        resolve = lambda rs=routes, gap=clear, results=None, authorities=None: inv.resolve_item(
            "Base.Sample", small, rs, gap, inherited, results, authorities)
        result = resolve()
        keys = {(a["axis_id"], a["scope_ref"]): a for a in result["required_axes"]}
        self.assertEqual(set(keys), {("acquisition", "item"), ("operation", "activity:a"), ("operation", "activity:b")})
        self.assertEqual(keys[("operation", "activity:a")]["contributors"], ["p", "q"])
        self.assertEqual(result["scope_state"], "determined")
        self.assertEqual(result["item_investigation_state"], "incomplete")
        self.assertEqual(result, resolve())
        small["profiles"].reverse()
        self.assertEqual(result, resolve(list(reversed(routes))))
        self.assertEqual(len(result["first_contact"]), 2)  # no facts still retains obligations
        missing_route = resolve([route("p")])
        self.assertEqual(missing_route["pending_scope_refs"][0]["profile_id"], "q")
        conflict = resolve(routes + [route("q", "evidence_backed_not_applicable")])
        self.assertEqual(conflict["scope_state"], "undetermined")
        self.assertEqual(len(conflict["first_contact"]), 2)
        self.assertTrue(next(r for r in conflict["routing"] if r["profile_id"] == "q")["conflict"])
        excluded = resolve([route("p"), route("q", "evidence_backed_not_applicable")])
        self.assertEqual(excluded["pending_scope_refs"], [])
        self.assertEqual({c for a in excluded["required_axes"] for c in a["contributors"]}, {"global", "p"})
        invalid_route = route("p", "evidence_backed_not_applicable")
        invalid_route["evidence_refs"] = []
        with self.assertRaises(ValueError):
            resolve([invalid_route])
        gap = {"state": "not_investigated", "kind": "uninvestigated", "question": "Unassessed residual?", "missing": "scope review", "next": "review scope"}
        self.assertEqual(resolve(gap=gap)["scope_state"], "undetermined")
        prose = deepcopy(small)
        prose["prose"] = "Rich prose and many sentences" * 50
        self.assertEqual(inv.resolve_item("Base.Sample", prose, routes, clear, inherited), result)
        synthetic = deepcopy(observed["Base.Battery"])
        synthetic["raw_item"]["fields"]["Type"] = "Food"
        synthetic["type_agrees_with_extraction"] = False
        food_route = next(r for r in inv.routes_for(contract, synthetic) if r["profile_id"] == "ingestion")
        self.assertEqual(food_route["state"], "investigated_unresolved")
        for profile in ("crafting", "world_work", "cooking"):
            synthetic["recipe_links"], synthetic["moveable_tools"] = [], []
            synthetic["raw_item"]["fields"].pop("EvolvedRecipe", None)
            self.assertEqual(next(r for r in inv.routes_for(contract, synthetic) if r["profile_id"] == profile)["state"], "investigated_unresolved")

        # Accepted instance versus mere kind/producer declaration; negative authority.
        acquired, authority = terminal_fixture()
        authorities = {authority["authority_id"]: authority}
        acquisition_only = resolve(results=[acquired], authorities=authorities)
        self.assertEqual(acquisition_only["acquisition_state"], "resolved")
        self.assertEqual(acquisition_only["item_investigation_state"], "incomplete")
        sparse_results = [acquired]
        for scope in ("activity:a", "activity:b"):
            na = {"item_id": "Base.Sample", "axis_id": "operation", "scope_ref": scope,
                  "state": "evidence_backed_not_applicable", "authority_ref": authority["authority_id"],
                  "question_coverage": "whole_scope", "provenance_refs": ["p"],
                  "exclusion_predicate": "Entire synthetic scope has no direct function", "scope_complete": True}
            sparse_results.append(na)
            authority["results"].append(na)
        self.assertEqual(resolve(results=sparse_results, authorities=authorities)["item_investigation_state"], "complete")
        self.assertEqual(resolve(gap=gap, results=sparse_results, authorities=authorities)["item_investigation_state"], "incomplete")
        for mutation in ("missing_instance", "subject", "coverage", "unaccepted", "na", "scope", "provenance", "kind", "unbound"):
            bad_result, bad_authority = deepcopy(acquired), deepcopy(authority)
            if mutation == "missing_instance": bad_authority["facts"] = []
            elif mutation == "subject": bad_authority["facts"][0]["item_id"] = "base.Sample"
            elif mutation == "coverage": bad_result["question_coverage"] = "partial"
            elif mutation == "unaccepted": bad_authority["facts"][0]["status"] = "candidate"
            elif mutation == "na": bad_result["state"] = "evidence_backed_not_applicable"
            elif mutation == "scope": bad_result["scope_ref"] = "wrong-context"
            elif mutation == "provenance": bad_authority["provenance"] = {}
            elif mutation == "kind": bad_authority["facts"][0]["fact_kind"] = "effect"
            else: bad_authority.pop("binding")
            bad_authority["results"] = [bad_result]
            with self.subTest(terminal=mutation), self.assertRaises(ValueError):
                resolve(results=[bad_result], authorities={bad_authority["authority_id"]: bad_authority})
        neg, neg_authority = terminal_fixture("acquisition_unobtainable")
        negative_resolved = resolve(results=[neg], authorities={neg_authority["authority_id"]: neg_authority})
        self.assertEqual(negative_resolved["acquisition_state"], "resolved")
        self.assertEqual(len(neg_authority["facts"]), 1)  # negative is not a zero-fact result
        for field in ("closed_scope", "coverage_complete", "false_negative_limit", "source_bindings", "item_id", "authority_ref"):
            bad = deepcopy(neg_authority)
            bad["negative_evidence"]["n"].pop(field)
            with self.subTest(negative=field), self.assertRaises(ValueError):
                resolve(results=[neg], authorities={bad["authority_id"]: bad})
        for change in ("allowed", "binding", "resolved", "producer", "count_type"):
            bad = deepcopy(inherited)
            if change == "allowed": bad["semantic_node"]["allowed_fact_kinds"] = "acquisition"
            elif change == "binding": del bad["semantic_node"]["bindings"]["acquisition_unobtainable"]
            elif change == "resolved": bad["acquisition"]["resolved_requires"] = "any_hint"
            elif change == "producer": bad["semantic_node"]["bindings"]["acquisition_unobtainable"]["current_producer"] = "resolver"
            else: bad["semantic_node"]["bindings"]["acquisition_unobtainable"]["current_assignment_count"] = False
            with self.subTest(inherited=change), self.assertRaises(ValueError):
                inv.acquisition_rules(bad)
        with patch.object(inv, "bound_json", return_value=neg_authority), patch.object(inv, "sha", return_value="a" * 64):
            loaded = inv.load_result_authorities(REPO, [{"path": "fixture.json", "sha256": "b" * 64}])
            self.assertEqual(set(loaded), {"external-fixture"})
        with patch.object(inv, "bound_json", return_value=neg_authority), patch.object(inv, "sha", return_value="0" * 64):
            with self.assertRaises(ValueError):
                inv.load_result_authorities(REPO, [{"path": "fixture.json", "sha256": "b" * 64}])

        # Current links/required identity are additive; no product locator changes.
        navigation = inv.read_json(REPO / ROUTE)
        link = navigation[ENTRY]
        self.assertEqual(link["manifest_path"], inv.ROOT + "/manifest.json")
        self.assertEqual(link["manifest_sha256"], inv.sha(REPO / link["manifest_path"]))
        self.assertEqual(link["validation_identity"], inv.TEST_ID)
        self.assertEqual(link["state"], "adopted")
        self.assertEqual(link["product_migration_state"], "deferred")
        current = inv.read_json(REPO / AUTH)
        entries = [e for e in current["entries"] if e.get("path") == link["manifest_path"]]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["sha256"], link["manifest_sha256"])
        registry = inv.read_json(REPO / REGISTRY)
        tests = [r for r in registry["required_tests"] if r["test_id"] == inv.TEST_ID]
        self.assertEqual(len(tests), 1)
        self.assertIs(tests[0]["required"], True)
        self.assertEqual(tests[0]["source_file"], inv.TEST_SOURCE)
        policy = inv.read_json(REPO / POLICY)
        self.assertEqual(len([r for k in ("planned_sources", "reviewed_sources", "additional_sources") for r in policy.get(k, []) if r["source_file"] == inv.TEST_SOURCE]), 1)
        for doc in ("docs/DECISIONS.md", "docs/ARCHITECTURE.md", "docs/ROADMAP.md"):
            self.assertIn("layer3_investigation", (REPO / doc).read_text(encoding="utf-8"))
        attributes = (REPO / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn(inv.ROOT + "/** -text", attributes)
        self.assertIn(inv.HUMAN + " -text", attributes)

        if baseline is not None:
            self.assertEqual(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(), baseline["execution_start_head"])
            successor = inv.read_json(REPO / inv.SUCCESSOR)
            pointer_path = "Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua"
            pointer = (REPO / pointer_path).read_text(encoding="utf-8")
            generation = re.search(r'generation_id\s*=\s*"([^"]+)"', pointer)[1]
            generation_root = inv.local_path(REPO, "Iris/media/lua/client/Iris/Data/IrisLayer3Generations/" + generation)
            selected = {p.relative_to(REPO).as_posix() for p in generation_root.rglob("*") if p.is_file()}
            self.assertEqual(set(baseline["generation_members"]), selected)
            protected = {inv.SUCCESSOR, *[m["path"] for m in successor["members"]], *inv.TARGET_PATHS,
                         inv.DATA + "dvf_3_3_input_manifest.json", inv.DATA + "tooltip_t1_layer3_owner_input.json",
                         "Iris/tooling/src/iris_tooling/build/compose_layer3_body_profile.py",
                         "Iris/tooling/src/iris_tooling/build/compose_layer3_item.py", pointer_path,
                         "Iris/media/lua/client/Iris/Data/layer3_renderer.lua",
                         "Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua", *selected}
            self.assertEqual({p["path"] for p in baseline["protected"]}, protected)
            self.assertEqual(len(baseline["protected"]), len(protected))
            for ref in baseline["protected"]:
                self.assertEqual(inv.binding(REPO, ref["path"]), ref)
            stripped = deepcopy(navigation)
            stripped.pop(ENTRY)
            self.assertEqual(stripped, baseline["configs"][ROUTE])
            stripped = deepcopy(current)
            stripped["entries"] = [e for e in stripped["entries"] if e.get("path") != link["manifest_path"]]
            self.assertEqual(stripped, baseline["configs"][AUTH])
            stripped = deepcopy(registry)
            stripped["required_tests"] = [r for r in stripped["required_tests"] if r["test_id"] != inv.TEST_ID]
            self.assertEqual(stripped, baseline["configs"][REGISTRY])
            stripped = deepcopy(policy)
            stripped["planned_sources"] = [r for r in stripped["planned_sources"] if r["source_file"] != inv.TEST_SOURCE]
            stripped["source_set_binding"] = baseline["configs"][POLICY]["source_set_binding"]
            self.assertEqual(stripped, baseline["configs"][POLICY])
        with patch.dict(os.environ, {"IRIS_LAYER3_INVESTIGATION_MODE": "unknown"}):
            with self.assertRaises(ValueError): adoption_baseline()
        with patch.dict(os.environ, {"IRIS_LAYER3_INVESTIGATION_MODE": "adoption", "IRIS_LAYER3_INVESTIGATION_BASELINE": ""}):
            with self.assertRaises(ValueError): adoption_baseline()

        # Dispatch stubs prevent any real composer/publisher invocation in this gate.
        from iris_tooling.domains.layer3 import cli
        with patch.object(inv, "main", return_value=37) as investigation:
            self.assertEqual(cli.main(["investigate"]), 37)
            investigation.assert_called_once_with([])
        with self.assertRaises(SystemExit):
            inv.main(["--output", "forbidden-product-path"])
        module_names = {
            "iris_tooling.build.compose_layer3_text": ["main", "build_shared_successor"],
            "iris_tooling.build.build_layer3_english_localization": ["publish_tooltip_t1_owner_only"],
            "iris_tooling.domains.layer3.tooltip_t1_d3": ["main"],
            "iris_tooling.domains.tooltip_t1.d3_invariance": ["main"],
        }
        stubs = {}
        for name, functions in module_names.items():
            module = ModuleType(name)
            for function in functions:
                setattr(module, function, Mock(return_value=0))
            stubs[name] = module
        context = Mock(repository_root=REPO)
        with patch.dict(sys.modules, stubs), patch("iris_tooling.build.repository_context.require_repository_context", return_value=context):
            self.assertEqual(cli.main(["--legacy-argument"]), 0)
            stubs["iris_tooling.build.compose_layer3_text"].main.assert_called_once_with(["--legacy-argument"])
            for command, forwarded in (("prepare-tooltip-t1-d3", "prepare"), ("materialize-tooltip-t1-d3-registry", "materialize-registry"), ("bundle-tooltip-t1-d3", "bundle")):
                self.assertEqual(cli.main([command, "--arg"]), 0)
                stubs["iris_tooling.domains.layer3.tooltip_t1_d3"].main.assert_called_with([forwarded, "--arg"])
            for command, forwarded in (("validate-tooltip-t1-d3-absence", "absence"), ("compare-tooltip-t1-d3", "compare")):
                self.assertEqual(cli.main([command, "--arg"]), 0)
                stubs["iris_tooling.domains.tooltip_t1.d3_invariance"].main.assert_called_with([forwarded, "--arg"])
            self.assertEqual(cli.main(["publish-tooltip-t1-owner"]), 0)
            stubs["iris_tooling.build.build_layer3_english_localization"].publish_tooltip_t1_owner_only.assert_called_once_with(REPO)
            self.assertEqual(cli.main(["compose-successor", "--output", "unused-output"]), 0)
            stubs["iris_tooling.build.compose_layer3_text"].build_shared_successor.assert_called_once_with(REPO, Path("unused-output"))
