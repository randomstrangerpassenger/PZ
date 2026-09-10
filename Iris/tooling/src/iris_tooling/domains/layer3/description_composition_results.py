"""Produce once, persist, and read descriptions without invoking a producer."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from . import composition_results as inputs
from . import description_composition_model as model
from . import description_composition_planner as planner
from . import description_composition_lexicon as lex
from . import description_composition_ko as ko
from . import description_composition_en as en
from . import description_composition_families as families

DEFAULT_OUTPUT = "Iris/build/description/composition/descriptions.json"
CODE = "Iris/tooling/src/iris_tooling/domains/layer3/"


def _links(units, plan):
    result = {name: sorted({v for u in units for v in u[name]})
              for name in ("block_refs", "branch_refs", "fact_refs", "qualifier_refs", "relation_refs")}
    result["qualifier_applications"] = [{"qualifier_id": q,
        "applies_to_fact_refs": plan["qualifiers"][q]["applies_to_fact_refs"]} for q in result["qualifier_refs"]]
    result["fact_refs"] = sorted(set(result["fact_refs"]) | {
        ref for q in result["qualifier_refs"] for ref in plan["qualifiers"][q]["fact_refs"]})
    return result


def _role(unit):
    contexts = [f["payload"]["activity"] for f in unit["facts"] if f["fact_kind"] == "use_context"]
    roles = sorted(f["payload"]["role"] for f in unit["facts"] if f["fact_kind"] == "context_role")
    if not contexts and unit.get("context"):
        contexts = [unit["context"]["activity"]]
    return contexts, roles


def _core(unit, locale, compact=False):
    grammar = ko if locale == "ko" else en
    contexts, roles = _role(unit)
    if contexts:
        names = [lex.context(c, locale, compact) for c in contexts]
        if roles:
            return grammar.role(names, roles)
        return names[0] + "에 쓸 수 있다" if locale == "ko" else "It can be used for " + names[0]
    if len(unit["facts"]) != 1:
        raise ValueError("unsupported unbound branch")
    return lex.core(unit["facts"][0], locale, compact)


def _expanded(plan, locale):
    grammar = ko if locale == "ko" else en
    groups = defaultdict(list)
    for unit in plan["units"]:
        contexts, roles = _role(unit)
        # Exact qualifier identity and class delimit the scope of sharing.
        family = ("role", tuple(roles)) if contexts and roles else ("clauses",)
        candle_activity = {"light_candle": "candle_lighting", "extinguish_candle": "candle_extinguishing"}.get(
            unit["facts"][0]["payload"].get("function"))
        if candle_activity:
            family = ("candle", candle_activity)
        elif roles == ["transformation_target"] and contexts in (["candle_lighting"], ["candle_extinguishing"]):
            family = ("candle", contexts[0])
        if unit["facts"][0]["fact_kind"] == "acquisition":
            family = ("route", tuple(unit["fact_refs"]))
        groups[(tuple(unit["qualifier_refs"]), family)].append(unit)
    segments = []
    for (qrefs, family), units in groups.items():
        if family[0] == "candle" and len(units) > 1:
            clauses = [lex.pair(("초에 불을 붙일 수 있다", "The candle can be lit") if family[1] == "candle_lighting"
                               else ("켜진 초를 끄는 제작법에 쓸 수 있다", "It can be supplied to the lit-candle extinguishing recipe"), locale)]
        elif family[0] == "role":
            activities = [lex.context(c, locale) for u in units for c in _role(u)[0]]
            # Equal activity names only coalesce with equal role AND scope.
            clauses = [grammar.role(list(dict.fromkeys(activities)), list(family[1]))]
        else:
            clauses = _clauses(units, plan, locale)
        # The unresolved wear statement is independently worded with its
        # possibility qualifier; do not restate it as a fishing consequence.
        independent_wear = (len(units) == 1 and units[0]["facts"][0]["payload"] ==
                            {"property": "item_condition", "direction": "decrease"}
                            and any(plan["qualifiers"][q]["payload"]["predicate"] == lex.source.SPEAR_FISHING_WEAR for q in qrefs))
        if independent_wear:
            clauses = [lex.qualifier(plan["qualifiers"][q], locale) for q in qrefs]
            conditions = []
        else:
            conditions = [lex.qualifier(plan["qualifiers"][q], locale) for q in qrefs]
        text = grammar.qualified(clauses, conditions)
        if family[0] == "route":
            text = ("획득 경로: " if locale == "ko" else "Acquisition route: ") + text
        segments.append({"text": text, **_links(units, plan), "expression": "exact_scope"})
    return segments


def _clauses(units, plan, locale):
    functions = {f["payload"].get("function") for u in units for f in u["facts"]}
    properties = {f["payload"].get("property") for u in units for f in u["facts"]}
    fact_refs = {r for u in units for r in u["fact_refs"]}
    result_refs = {r for relation in plan["relations"] if relation["kind"] == "result"
                   for r in relation.get("fact_refs", [])}
    if functions == {"use_furnace_bellows", None} and properties == {"forge_temperature", None} and fact_refs <= result_refs:
        return [lex.pair(("풀무로 화로의 열을 높일 수 있다", "Bellows can raise furnace heat"), locale)]
    # This coalescing is licensed by the actual function/result relations and
    # the grouping's exact common qualifier scope, not by surface strings.
    if functions == {"wash_carried_equipment", None} and fact_refs <= result_refs:
        removed = []
        if "item_surface_blood" in properties:
            removed.append("피" if locale == "ko" else "blood")
        if "clothing_surface_dirt" in properties:
            removed.append("옷의 때" if locale == "ko" else "clothing dirt")
        covered = {"item_surface_blood", "clothing_surface_dirt", "clothing_wetness", None}
        if removed and properties <= covered:
            text = ("물로 " + "와 ".join(removed) + "를 씻어낼 수 있다" if locale == "ko"
                    else "Washing with water removes " + en.join(removed))
            if "clothing_wetness" in properties:
                text += (". 세척한 옷은 완전히 젖는다" if locale == "ko" else ". Washed clothing becomes fully wet")
            return [text]
    return [_core(u, locale) for u in sorted(units, key=lambda u:
        ({"direct_function": 0, "use_context": 1, "context_role": 1, "effect": 2, "state": 3}.get(u["facts"][0]["fact_kind"], 4), u["fact_refs"]))]


FUEL_FUNCTIONS = {"supply_campfire_fuel", "supply_hearth_fuel", "supply_furnace_fuel"}
TINDER_FUNCTIONS = {"provide_campfire_tinder", "provide_hearth_tinder", "provide_industrial_tinder"}


def _compact(plan, locale):
    grammar = ko if locale == "ko" else en
    frames, used = families.frames(plan, locale, _links)
    groups = defaultdict(list)
    decisions = {}
    role_contexts = {c for u in plan["units"] if not u["detail_reason"] and not (set(u["fact_refs"]) & used) and _role(u)[1]
                     for c in _role(u)[0]}
    covered_contexts = []
    for u in plan["units"]:
        if u["detail_reason"] or set(u["fact_refs"]) & used:
            continue
        contexts, roles = _role(u)
        fn = u["facts"][0]["payload"].get("function")
        conditions = []
        for qref in u["qualifier_refs"]:
            wording, reason = lex.compact_qualifier(plan["qualifiers"][qref], locale, u)
            inline = lex.INLINE_CONDITIONS.get((plan["qualifiers"][qref]["payload"]["predicate"], fn))
            if fn in lex.CONTROL_NOUNS and lex.CONTROL_NOUNS[fn][0] == "firearm" and wording is None:
                inline = lex.CONTROL_NOUNS[fn][1]
            decisions[(tuple(u["fact_refs"]), qref)] = {"qualifier_ref": qref,
                "applies_to_fact_refs": u["fact_refs"], "placement": "compact_summary" if wording else "expanded",
                "text": wording, "reason": reason}
            if inline:
                decisions[(tuple(u["fact_refs"]), qref)].update(
                    placement="compact_core", text=lex.pair(inline, locale),
                    reason="condition integrated into the capability; remaining execution detail is expanded")
                wording = None
            if wording:
                conditions.append(qref)
        if contexts and not roles and all(c in role_contexts for c in contexts):
            covered_contexts.append(u)
            continue
        if contexts and roles:
            key = ("role", tuple(roles), tuple(conditions))
        elif fn in FUEL_FUNCTIONS:
            key = ("fuel", tuple(conditions))
        elif fn in TINDER_FUNCTIONS:
            key = ("tinder", tuple(conditions))
        elif fn in lex.CONTROL_NOUNS:
            key = ("control", lex.CONTROL_NOUNS[fn][0], tuple(conditions))
        else:
            key = ("function", tuple(u["qualifier_refs"]))
        groups[key].append(u)
    for u in covered_contexts:
        target = next(members for key, members in groups.items() if key[0] == "role"
                      and any(set(_role(u)[0]) & set(_role(m)[0]) for m in members))
        target.append(u)
    if ("fuel", ()) in groups and ("tinder", ()) in groups:
        groups[("consumption",)] = groups.pop(("fuel", ())) + groups.pop(("tinder", ()))
    segments = list(frames)
    for key, units in groups.items():
        if key[0] == "role":
            activities = list(dict.fromkeys(lex.context(c, locale, True) for u in units for c in _role(u)[0]))
            text = grammar.role(activities, list(key[1]), compact=True) + "."
            reason = "existential activity/role overview; exact recipe targets and eligibility in expanded"
        elif key[0] == "consumption":
            text = lex.pair(("연료나 불쏘시개로 소모할 수 있으며 불쏘시개로 쓸 때는 점화 도구가 필요하다",
                             "It can be consumed as fuel or as tinder with an igniter"), locale) + "."
            reason = "distinct consumptive roles; the igniter requirement attaches only to tinder"
        elif key[0] in {"fuel", "tinder"}:
            text = lex.pair(("연료로 소모할 수 있다", "It can be consumed as fuel")
                            if key[0] == "fuel" else
                            ("점화 도구와 함께 불쏘시개로 소모할 수 있다", "It can be consumed as tinder with an igniter"), locale) + "."
            reason = "fuel/tinder role overview; distinct targets and local supply conditions in expanded"
        elif key[0] == "control":
            nouns = [lex.pair(lex.CONTROL_NOUNS[u["facts"][0]["payload"]["function"]][1], locale) for u in units]
            if locale == "ko":
                text = "·".join(nouns) + (" 기능을 지원한다." if key[1] in {"device", "firearm"} else "에 쓸 수 있다.")
            else:
                text = ("It supports " if key[1] in {"device", "firearm"} else "It can be used for ") + en.join(nouns) + "."
            reason = "parallel named operations share their subject; actual operations and conditions stay individually linked"
        else:
            text = grammar.parallel([_core(u, locale, True) for u in units])
            reason = "function capability; local execution and outcomes remain in expanded"
        conditions = []
        dispositions = []
        emitted = set()
        for u in units:
            for qref in u["qualifier_refs"]:
                decision = decisions[(tuple(u["fact_refs"]), qref)]
                dispositions.append(decision)
                if decision["placement"] == "compact_summary" and qref not in emitted:
                    conditions.append(decision["text"])
                    emitted.add(qref)
        if conditions:
            text = grammar.qualified([text.removesuffix(".")], conditions)
        segments.append({"text": text, **_links(units, plan), "expression": "capability_overview",
                         "placement_reason": reason, "qualifier_dispositions": dispositions})
    # If the input has only maintenance/effects, it is still describable. Do not
    # promote an arbitrary representative: keep all of its independent meanings.
    if not segments:
        remaining = [u for u in plan["units"] if u["facts"][0]["fact_kind"] != "acquisition"]
        for u in remaining:
            conditions = [lex.qualifier(plan["qualifiers"][q], locale) for q in u["qualifier_refs"]]
            segments.append({"text": grammar.qualified([_core(u, locale)], conditions),
                             **_links([u], plan), "expression": "exact_scope",
                             "placement_reason": "all available semantic content; no main function anchor"})
    # Coordinate grammatical peers after placement. Sharing a modal does not
    # remove any member's locally worded condition or its exact source links.
    coordinated = defaultdict(list)
    for segment in segments:
        clause = segment["text"].removesuffix(".")
        key = ("single", len(coordinated))
        patterns = ("할 수 있다", "쓸 수 있다", "쓰인다") if locale == "ko" else (
            "It can be used for ", "It can be used to ", "It can ")
        scoped = segment["expression"] == "conditional_frame" or any(
            d["placement"].startswith("compact") for d in segment.get("qualifier_dispositions", []))
        if "." not in clause and not scoped:
            for pattern in patterns:
                if clause.endswith(pattern) if locale == "ko" else clause.startswith(pattern):
                    key = ("parallel", pattern)
                    break
        coordinated[key].append(segment)
    output = []
    for members in coordinated.values():
        if len(members) == 1:
            output.append(members[0])
            continue
        combined = {name: sorted({ref for s in members for ref in s[name]}) for name in
                    ("block_refs", "branch_refs", "fact_refs", "qualifier_refs", "relation_refs")}
        combined.update(
            text=grammar.parallel([s["text"].removesuffix(".") for s in members]),
            expression="capability_overview",
            placement_reason="parallel capabilities retain each local modifier; exact detail in expanded",
            qualifier_applications=[{"qualifier_id": q, "applies_to_fact_refs": plan["qualifiers"][q]["applies_to_fact_refs"]}
                                    for q in combined["qualifier_refs"]])
        combined["qualifier_dispositions"] = [d for s in members for d in s.get("qualifier_dispositions", [])]
        output.append(combined)
    return output


def compose_item(item):
    plan = planner.plan(item)
    output = {"item_id": item["item_id"], "relations": plan["relations"],
              "unresolved_relations": plan["unresolved_relations"],
              "qualifiers": [plan["qualifiers"][q] for q in sorted(plan["qualifiers"])], "locales": {}}
    for locale in model.LOCALES:
        surfaces = {}
        for surface, realize in (("expanded", _expanded), ("compact", _compact)):
            reason = None
            try:
                segments = realize(plan, locale)
                state = "present" if segments else "absent"
                if not segments:
                    reason = "no accepted semantic content" if surface == "compact" else "no accepted content"
            except (KeyError, ValueError, TypeError) as exc:
                segments, state = [], "failed"
                reason = "composition rule failure: " + str(exc)
            surfaces[surface] = {"item_id": item["item_id"], "locale": locale, "surface": surface,
                                 "state": state, "reason": reason, "segments": segments,
                                 "text": (" " if surface == "compact" else "\n").join(s["text"] for s in segments)}
        compact, expanded = surfaces["compact"], surfaces["expanded"]
        compact["detail_links"] = []
        if expanded["state"] == "present":
            compact["detail_links"] = [
                {"segment": n, "fact_refs": s["fact_refs"],
                 "reason": "full local meaning, qualifier scope, outcomes and acquisition routes"}
                for n, s in enumerate(expanded["segments"])]
        elif compact["state"] == "present":
            compact.update(state="failed", text="", segments=[],
                           reason="expanded meaning unavailable; cannot preserve compact detail placement")
        output["locales"][locale] = surfaces
    return output


def compose(source, identity, producer):
    result = {"schema": model.SCHEMA, "version": model.VERSION, "input": identity,
              "producer": producer, "physical_fit": "unmeasured; B must check PZ font and viewport",
              "items": [compose_item(item) for item in source["items"]]}
    counts = Counter(f"{loc}/{surface}/{row['state']}" for item in result["items"]
                     for loc, surfaces in item["locales"].items() for surface, row in surfaces.items())
    result["summary"] = {"targets": len(result["items"]), "surfaces": sum(counts.values()),
                         "states": dict(sorted(counts.items()))}
    return model.validate_result(result)


def produce(root: Path):
    root = Path(root).resolve()
    source = inputs.read_result(root)
    identity = {"path": inputs.DEFAULT_OUTPUT,
                "sha256": hashlib.sha256((root / inputs.DEFAULT_OUTPUT).read_bytes()).hexdigest(),
                "schema": source["schema"], "source": source["source"], "summary": source["summary"]}
    # Identify the actual vocabulary and grammar consumed; no copies or seals.
    names = ["description_composition_" + suffix + ".py" for suffix in
             ("model", "planner", "lexicon", "ko", "en", "families", "results")]
    names += ["expression_rules.py", "recovery_expression.py", "recovery_sources.py", "acquisition_expression.py"]
    producer = {"version": model.VERSION, "files": {
        CODE + name: hashlib.sha256((root / CODE / name).read_bytes()).hexdigest() for name in names}}
    return source, compose(source, identity, producer)


def _path(root, path):
    root = Path(root).resolve()
    target = (root / path).resolve()
    model.require(target.is_relative_to(root / "Iris/build/description/composition"),
                  "description path escapes its output directory")
    model.require(target != root / inputs.DEFAULT_OUTPUT, "cannot overwrite semantic input")
    return target


def write_result(root, result, path=DEFAULT_OUTPUT):
    target = _path(root, path)
    model.validate_result(result)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".json.tmp")
    temporary.write_bytes(model.canonical(result))
    temporary.replace(target)
    return target


def read_result(root, path=DEFAULT_OUTPUT):
    return model.validate_result(json.loads(_path(root, path).read_text(encoding="utf-8")))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--root", type=Path, default=Path.cwd())
    args = cli.parse_args()
    _, result = produce(args.root)
    print(write_result(args.root, result))
    print(json.dumps(result["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
