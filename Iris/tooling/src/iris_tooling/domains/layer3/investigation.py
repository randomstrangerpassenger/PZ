"""Offline investigation scope; never a semantic fact producer or composer.

The bound registry owns questions. Source observations only route those questions.
Accepted terminal results are a separate, explicitly supplied authority input.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = "Iris/_docs/authority/dvf/layer3_investigation"
SUCCESSOR = "Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json"
HUMAN = "docs/iris_dvf_layer3_multi_profile_investigation_completion_first_contact_contract.md"
DATA = "Iris/build/description/v2/data/"
TARGET_PATHS = [DATA + "dvf_3_3_facts.jsonl", DATA + "dvf_3_3_decisions.jsonl"]
TEST_SOURCE = "Iris/build/description/v2/tests/test_layer3_investigation_contract.py"
TEST_ID = "test_layer3_investigation_contract.Layer3InvestigationContractTest.test_investigation_contract"
APPLICABILITY = {"confirmed_applicable", "evidence_backed_not_applicable",
                 "investigated_unresolved", "not_investigated"}
STATES = {"resolved", "evidence_backed_not_applicable", "investigated_unresolved", "not_investigated"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def local_path(root: Path, relative: str) -> Path:
    require(isinstance(relative, str) and bool(relative), "missing path")
    path = Path(relative)
    require(not path.is_absolute() and ".." not in path.parts and "\\" not in relative,
            "noncanonical repository path")
    resolved = (root / path).resolve()
    require(resolved.is_relative_to(root.resolve()), "path outside repository")
    return resolved


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(root: Path, path: str) -> dict:
    return {"path": path, "sha256": sha(local_path(root, path))}


def bound_json(root: Path, ref: dict) -> Any:
    path = local_path(root, ref["path"])
    require(sha(path) == ref["sha256"], f"source hash mismatch: {ref['path']}")
    return read_json(path)


def set_digest(values) -> str:
    return hashlib.sha256("".join(value + "\n" for value in sorted(values)).encode()).hexdigest()


def exact_rows(rows: list[dict]) -> dict[str, dict]:
    result = {}
    for row in rows:
        value = row.get("item_id")
        require(isinstance(value, str) and bool(value.strip()), "invalid exact FullType")
        require(value not in result, f"duplicate FullType: {value}")
        result[value] = row
    return result


def targets(root: Path) -> list[str]:
    left, right = [exact_rows(read_rows(local_path(root, path))) for path in TARGET_PATHS]
    require(left.keys() == right.keys(), "facts/decisions exact target mismatch")
    return sorted(left)


def inherited_contract(root: Path, ref: dict) -> dict:
    manifest = bound_json(root, ref)
    require(manifest["status"] == "adopted", "unadopted successor")
    contract = None
    for member in manifest["members"]:
        path = local_path(root, member["path"])
        require(sha(path) == member["sha256"], "successor member drift")
        if member["path"] == "Iris/_docs/authority/dvf/layer3_successor/contract.json":
            contract = read_json(path)
    require(contract is not None, "missing bound successor contract")
    acquisition_rules(contract)
    return contract


def acquisition_rules(inherited: dict) -> tuple[set[str], dict]:
    try:
        kinds = inherited["semantic_node"]["allowed_fact_kinds"]
        negative = inherited["semantic_node"]["bindings"]["acquisition_unobtainable"]
        resolved = inherited["acquisition"]["resolved_requires"]
    except (KeyError, TypeError) as exc:
        raise ValueError("missing inherited acquisition contract") from exc
    require(isinstance(kinds, list) and all(isinstance(k, str) for k in kinds)
            and {"acquisition", "acquisition_unobtainable"} <= set(kinds), "invalid allowed kinds")
    require(isinstance(negative, dict) and negative.get("required_field") == "negative_evidence_refs"
            and type(negative.get("minimum_targets")) is int and negative["minimum_targets"] >= 1
            and negative.get("current_producer") == "none"
            and type(negative.get("current_assignment_count")) is int
            and negative["current_assignment_count"] == 0, "unsupported negative binding")
    require(resolved == "one_or_more_acquisition_facts_or_one_admissible_acquisition_unobtainable_fact",
            "unsupported acquisition resolution contract")
    return set(kinds), negative


def validate_contract(contract: dict) -> None:
    require(contract.get("schema_version") == "iris-layer3-investigation-v1"
            and isinstance(contract.get("revision"), str) and bool(contract["revision"]), "unknown registry schema/revision")
    axes = {a["axis_id"]: a for a in contract["axes"]}
    profiles = {p["profile_id"]: p for p in contract["profiles"]}
    require(len(axes) == len(contract["axes"]) and "acquisition" in axes, "duplicate/missing axis")
    require(len(profiles) == len(contract["profiles"]) and bool(profiles), "duplicate/empty profiles")
    require(axes["acquisition"]["na_allowed"] is False and axes["acquisition"]["scope_unit"] == "item",
            "invalid global acquisition")
    require(set(axes["acquisition"]["allowed_result_kinds"]) == {"acquisition", "acquisition_unobtainable"},
            "acquisition must consume inherited result kinds")
    for axis in axes.values():
        require(all(axis.get(k) for k in ("question", "terminal_requirement", "next_investigation", "allowed_result_kinds"))
                and type(axis.get("na_allowed")) is bool and axis.get("scope_unit") in {"item", "context"}, "invalid axis")
    for profile in profiles.values():
        require(all(profile.get(k) for k in ("revision", "purpose", "question", "overlap", "examples", "next_investigation")),
                "empty profile content")
        required = profile["required_axes"]
        require(bool(required) and len(required) == len(set(required)) and set(required) <= axes.keys(), "unknown/duplicate profile axis")
        contacts = profile["first_contact"]
        require(len({c["axis_id"] for c in contacts}) == len(contacts), "duplicate first-contact axis")
        for contact in contacts:
            require(contact["axis_id"] in required and contact["required_question_ref"] == contact["axis_id"]
                    and all(contact.get(k) for k in ("user_question", "first_understanding_reason", "detail_boundary")), "invalid first-contact obligation")
        rule = profile["routing"]
        require(rule.get("kind") in {"all_targets", "native_type", "recipe_direct", "evolved_field", "moveable_definition"}
                and all(rule.get(k) for k in ("scope", "positive_reason", "open_reason")), "invalid routing rule")
        if rule["kind"] == "native_type":
            require(bool(rule.get("value")) and bool(rule.get("negative_reason")), "unjustified native exclusion")
    sources = [s["path"] for s in contract["sources"]]
    require(len(sources) == len(set(sources)) and set(contract["script_paths"]) <= set(sources), "invalid source registry")


def without_comments(text: str) -> str:
    # Preserve line offsets for source locators. This bounded reader does not execute scripts.
    return re.sub(r"/\*.*?\*/|//[^\n]*", lambda m: "\n" * m[0].count("\n"), text, flags=re.S)


def blocks(text: str, kind: str):
    clean = without_comments(text)
    modules = list(re.finditer(r"\bmodule\s+(\w+)\s*\{", clean))
    for match in re.finditer(r"\b" + kind + r"\s+([^{}\r\n]+?)\s*\{", clean):
        module = next((m[1] for m in reversed(modules) if m.start() < match.start()), None)
        if module is None:
            continue
        depth, end = 1, match.end()
        while end < len(clean) and depth:
            depth += (clean[end] == "{") - (clean[end] == "}")
            end += 1
        require(depth == 0, "unterminated source block")
        yield module, match[1].strip(), clean[match.end():end - 1], clean[:match.start()].count("\n") + 1


def source_observations(root: Path, contract: dict, item_ids: list[str]) -> list[dict]:
    """Apply declared predicates to bound source bytes once; no rendered inputs."""
    source_text = {}
    for ref in contract["sources"]:
        path = local_path(root, ref["path"])
        require(sha(path) == ref["sha256"], f"source drift: {ref['path']}")
        source_text[ref["path"]] = path.read_text(encoding="utf-8-sig")
    inventory = json.loads(source_text["Iris/input/items_itemscript.json"])
    recipe_index = json.loads(source_text["Iris/input/recipes_index_full.json"])["items"]
    raw_items, recipes = defaultdict(list), defaultdict(list)
    wanted = set(item_ids)
    for path in contract["script_paths"]:
        for module, name, body, line in blocks(source_text[path], "item"):
            item_id = module + "." + name
            if item_id in wanted:
                fields = dict(re.findall(r"(?m)^\s*(\w+)\s*=\s*([^,\r\n]*),?", body))
                raw_items[item_id].append({"path": path, "locator": f"L{line}:item:{item_id}",
                                           "fields": {k: v.strip() for k, v in fields.items()}})
        for module, name, body, line in blocks(source_text[path], "recipe"):
            recipes[(Path(path).name, name)].append((module, body, path, line))
    move_path = "lua/client/Moveables/ISMoveableDefinitions.lua"
    move = re.sub(r"--[^\n]*", "", source_text[move_path])
    aliases = dict(re.findall(r'\["([^"]+)"\]\s*=\s*"([^"]+)"', move.split("function ISMoveableDefinitions:getInstance")[0]))
    definitions = re.findall(r'moveableDefinitions\.addToolDefinition\(\s*"([^"]+)"\s*,\s*\{([^}]+)\}', move)
    require(bool(definitions) and bool(aliases), "unsupported moveable definitions")
    observations = []
    for item_id in item_ids:
        candidates = raw_items[item_id]
        extracted = inventory.get(item_id)
        raw = candidates[0] if len(candidates) == 1 else None
        agreed = bool(raw and extracted and extracted.get("FullType") == item_id
                      and raw["fields"].get("Type") == extracted.get("Type"))
        fields = raw["fields"] if raw else {}
        links, unverified = [], []
        for entry in recipe_index.get(item_id, []):
            verified = False
            for module, body, path, line in recipes[(entry["source"], entry["recipe"])]:
                for clause in body.split(","):
                    clause = clause.strip()
                    if not clause or ":" in clause:
                        continue
                    role = "keep" if clause.startswith("keep ") else "input"
                    tokens = re.sub(r"^(keep|destroy)\s+", "", clause).split("/")
                    ids = [token.split("=")[0].strip() for token in tokens]
                    ids = [token if "." in token else module + "." + token for token in ids]
                    if role == entry["role"] and item_id in ids:
                        links.append({"path": path, "locator": f"L{line}:recipe:{entry['recipe']}",
                                      "role": role, "observed": clause})
                        verified = True
            if not verified:
                unverified.append(entry)
        tools = []
        if raw:
            tags = fields.get("Tags", "").split(";")
            for name, values in definitions:
                for token in re.findall(r'"([^"]+)"', values):
                    if (token in aliases and aliases[token] in tags) or (token not in aliases and token == item_id):
                        tools.append({"definition": name, "token": token, "tag": aliases.get(token),
                                      "path": move_path, "locator": f"moveableDefinitions.addToolDefinition:{name}"})
        observations.append({"evidence_id": "item:" + item_id, "item_id": item_id,
                             "registry_revision": contract["revision"],
                             "snapshot": contract["snapshot"], "raw_item": raw,
                             "raw_item_candidates": [{"path": c["path"], "locator": c["locator"]} for c in candidates],
                             "raw_item_count": len(candidates), "type_agrees_with_extraction": agreed,
                             "extracted_type": extracted.get("Type") if extracted else None,
                             "recipe_links": sorted(links, key=lambda r: (r["path"], r["locator"], r["role"])),
                             "unverified_recipe_candidates": unverified, "moveable_tools": tools,
                             "accepted_semantic_results": [],
                             "gap": {"state": "investigated_unresolved", "kind": "evidence_gap",
                                     "question": "추가 직접 기능·활동·상태 조건이 현재 질문 범위 밖에 남아 있는가?",
                                     "missing": "Static Recipe 직접 token 및 native Type·EvolvedRecipe·moveable tool 정의만 확인; Lua 동적 predicate, Recipe group, fixing 의미와 전체 행동 coverage는 미확정.",
                                     "next": "DVF-L3-03에서 exact item의 Lua/script 행동과 group/tag 확장을 확인하고 기존 질문으로 표현되지 않는 경우에만 registry revision을 추가한다."}})
    return observations


def routes_for(contract: dict, observation: dict) -> list[dict]:
    routes = []
    raw = observation["raw_item"]
    fields = raw["fields"] if raw else {}
    for profile in contract["profiles"]:
        rule = profile["routing"]
        kind = rule["kind"]
        state, scopes = "investigated_unresolved", []
        reason = rule["open_reason"]
        if kind == "all_targets":
            state, scopes, reason = "confirmed_applicable", [rule["scope"]], rule["positive_reason"]
        elif kind == "native_type":
            if observation["type_agrees_with_extraction"]:
                state = "confirmed_applicable" if fields["Type"] == rule["value"] else "evidence_backed_not_applicable"
                scopes = [rule["scope"]] if state == "confirmed_applicable" else []
                reason = rule["positive_reason"] if scopes else rule["negative_reason"]
            else:
                reason = (f"{observation['item_id']}: raw declarations={observation['raw_item_count']}, "
                          f"extracted Type={observation['extracted_type']!r}; "
                          "단일 원본 FullType/Type과 추출의 일치를 확인하지 못했다. " + rule["open_reason"])
        elif kind == "recipe_direct":
            if observation["recipe_links"]:
                state, scopes, reason = "confirmed_applicable", [rule["scope"]], rule["positive_reason"]
        elif kind == "evolved_field":
            if fields.get("EvolvedRecipe"):
                state, scopes, reason = "confirmed_applicable", [rule["scope"]], rule["positive_reason"]
        elif kind == "moveable_definition":
            if observation["moveable_tools"]:
                state, scopes, reason = "confirmed_applicable", [rule["scope"]], rule["positive_reason"]
        else:
            raise ValueError(f"unknown routing predicate: {kind}")
        routes.append({"profile_id": profile["profile_id"], "state": state, "scope_refs": scopes,
                       "evidence_refs": [observation["evidence_id"]], "reason": reason})
    return sorted(routes, key=lambda r: r["profile_id"])


def merge_routes(contract: dict, routes: list[dict]) -> list[dict]:
    """Keep conflicts, missing decisions and all contributors; no priority winner."""
    known = {p["profile_id"] for p in contract["profiles"]}
    require(all(r["profile_id"] in known and r["state"] in APPLICABILITY for r in routes), "unknown route")
    merged = []
    for profile_id in sorted(known):
        rows = [r for r in routes if r["profile_id"] == profile_id]
        for row in rows:
            if row["state"] in {"confirmed_applicable", "evidence_backed_not_applicable"}:
                require(bool(row.get("evidence_refs")) and bool(row.get("reason")), "unsupported applicability")
            if row["state"] == "confirmed_applicable":
                require(bool(row.get("scope_refs")), "positive without scope")
        states = {r["state"] for r in rows}
        conflict = {"confirmed_applicable", "evidence_backed_not_applicable"} <= states
        state = ("investigated_unresolved" if conflict or "investigated_unresolved" in states
                 else "not_investigated" if not rows or "not_investigated" in states
                 else "confirmed_applicable" if "confirmed_applicable" in states
                 else "evidence_backed_not_applicable")
        merged.append({"profile_id": profile_id, "state": state, "conflict": conflict,
                       "scope_refs": sorted({s for r in rows for s in r["scope_refs"]}),
                       "evidence_refs": sorted({s for r in rows for s in r.get("evidence_refs", [])}),
                       "reasons": sorted({r["reason"] for r in rows}),
                       "observations": sorted(rows, key=lambda r: json.dumps(r, sort_keys=True))})
    return merged


def load_result_authorities(root: Path, refs: list[dict]) -> dict:
    """Only consume explicitly bound external results; never search or mint them."""
    authorities = {}
    for ref in refs:
        payload = bound_json(root, ref)
        require(payload.get("status") == "adopted" and payload.get("authority_id") not in authorities,
                "invalid result authority")
        source_bindings = payload.get("source_bindings", [])
        require(bool(source_bindings), "missing result source bindings")
        for source in source_bindings:
            require(sha(local_path(root, source["path"])) == source["sha256"], "result source drift")
        source_hashes = {source["sha256"] for source in source_bindings}
        require(all(p.get("source_sha256") in source_hashes and p.get("locator")
                    for p in payload.get("provenance", {}).values()), "unbound result provenance")
        for negative in payload.get("negative_evidence", {}).values():
            require(bool(negative.get("source_bindings")) and all(s in source_bindings for s in negative["source_bindings"]),
                    "unbound negative source scope")
        authorities[payload["authority_id"]] = {**payload, "binding": ref}
    return authorities


def terminal_result(item_id: str, axis: dict, result: dict, inherited: dict, authorities: dict) -> bool:
    state = result.get("state")
    require(state in STATES, "unknown axis state")
    if state in {"not_investigated", "investigated_unresolved"}:
        require(not result.get("fact_refs"), "open result contains terminal fact claim")
        return False
    require(state != "evidence_backed_not_applicable" or axis["na_allowed"], "N/A forbidden")
    authority = authorities.get(result.get("authority_ref"))
    require(isinstance(authority, dict) and authority.get("status") == "adopted"
            and bool(authority.get("binding", {}).get("sha256")), "unbound result authority")
    # An inline assertion cannot extend an adopted authority's accepted results.
    require(result in authority.get("results", []), "result not accepted by bound authority")
    require(result.get("item_id") == item_id and result.get("axis_id") == axis["axis_id"]
            and result.get("question_coverage") == "whole_scope" and bool(result.get("provenance_refs")),
            "terminal question/subject coverage missing")
    provenance = authority.get("provenance", {})
    require(all(ref in provenance and provenance[ref].get("source_sha256")
                and provenance[ref].get("locator") for ref in result["provenance_refs"]), "unbound provenance")
    if state == "evidence_backed_not_applicable":
        require(bool(result.get("exclusion_predicate")) and result.get("scope_complete") is True,
                "unsupported axis exclusion")
        return True
    kinds, negative = acquisition_rules(inherited)
    facts = authority.get("facts", [])
    by_id = {fact["fact_id"]: fact for fact in facts}
    require(len(by_id) == len(facts), "duplicate accepted fact ID")
    refs = result.get("fact_refs", [])
    require(bool(refs) and len(refs) == len(set(refs)), "missing/duplicate accepted result refs")
    for ref in refs:
        require(ref in by_id, "missing accepted fact instance")
        fact = by_id[ref]
        require(fact.get("status") == "accepted" and fact.get("item_id") == item_id
                and fact.get("fact_kind") in kinds and isinstance(fact.get("payload"), dict)
                and bool(fact["payload"]) and bool(fact.get("provenance_refs"))
                and all(p in provenance and provenance[p].get("source_sha256")
                        and provenance[p].get("locator") for p in fact["provenance_refs"]), "invalid accepted fact")
        require(fact["fact_kind"] in axis["allowed_result_kinds"], "wrong kind for question")
        if axis["axis_id"] == "acquisition":
            require(fact["fact_kind"] in {"acquisition", "acquisition_unobtainable"}, "non-acquisition terminal fact")
        if fact["fact_kind"] == "context_role":
            context = by_id.get(fact.get("context_fact_ref"), {})
            require(context.get("fact_kind") == "use_context" and context.get("item_id") == item_id
                    and context.get("status") == "accepted", "invalid context-local role")
        if fact["fact_kind"] in {"condition", "constraint"}:
            targets = fact.get("applies_to_fact_refs", [])
            require(bool(targets) and all(t in by_id and by_id[t].get("item_id") == item_id
                    and by_id[t].get("status") == "accepted"
                    and by_id[t].get("fact_kind") not in {"condition", "constraint"} for t in targets), "invalid fact-local qualifier")
        if fact["fact_kind"] == "acquisition_unobtainable":
            negatives = fact.get(negative["required_field"], [])
            require(len(set(negatives)) >= negative["minimum_targets"], "missing negative evidence")
            for neg_ref in negatives:
                evidence = authority.get("negative_evidence", {}).get(neg_ref, {})
                require(evidence.get("item_id") == item_id and evidence.get("closed_scope") is True
                        and evidence.get("coverage_complete") is True
                        and evidence.get("false_negative_limit") == "excluded_within_bound_scope"
                        and bool(evidence.get("source_bindings")) and bool(evidence.get("scope_description"))
                        and evidence.get("authority_ref") == authority.get("authority_id"),
                        "unsupported negative terminal claim")
    return True


def resolve_item(item_id: str, contract: dict, routes: list[dict], gap: dict,
                 inherited: dict, results: list[dict] | None = None, authorities: dict | None = None) -> dict:
    acquisition_rules(inherited)
    axes = {a["axis_id"]: a for a in contract["axes"]}
    profiles = {p["profile_id"]: p for p in contract["profiles"]}
    routing = merge_routes(contract, routes)
    pending, required, first = [], {("acquisition", "item"): {"global"}}, {}
    for route in routing:
        profile = profiles[route["profile_id"]]
        if route["state"] in {"investigated_unresolved", "not_investigated"}:
            pending.append({"profile_id": route["profile_id"], "question": profile["question"],
                            "possible_scope_refs": route["scope_refs"], "evidence_refs": route["evidence_refs"],
                            "reason": "; ".join(route["reasons"]) or "No routing observation supplied",
                            "next": profile["next_investigation"]})
        # Confirmed contexts remain visible even when another observation conflicts.
        for scope in route["scope_refs"]:
            for axis_id in profile["required_axes"]:
                key = (axis_id, "item" if axis_id == "acquisition" else scope)
                required.setdefault(key, set()).add(route["profile_id"])
            for contact in profile["first_contact"]:
                key = (contact["axis_id"], "item" if contact["axis_id"] == "acquisition" else scope)
                first.setdefault(key, set()).add(route["profile_id"])
    supplied = {}
    for result in results or []:
        key = (result["axis_id"], result["scope_ref"])
        require(key in required and key not in supplied, "unexpected/duplicate axis result")
        supplied[key] = result
    output_axes, blockers = [], []
    for (axis_id, scope), contributors in sorted(required.items()):
        result = supplied.get((axis_id, scope), {"state": "not_investigated"})
        terminal = terminal_result(item_id, axes[axis_id], result, inherited, authorities or {})
        output_axes.append({"item_id": item_id, "axis_id": axis_id, "scope_ref": scope,
                            "contributors": sorted(contributors), "state": result["state"],
                            "terminal": terminal, "result": result})
        if not terminal:
            blockers.append({"kind": "uninvestigated" if result["state"] == "not_investigated" else "evidence_gap",
                             "axis_id": axis_id, "scope_ref": scope, "question": axes[axis_id]["question"],
                             "missing": axes[axis_id]["terminal_requirement"], "next": axes[axis_id]["next_investigation"]})
    require(gap.get("state") in {"assessed_clear", "investigated_unresolved", "not_investigated"}, "unknown gap state")
    require(gap.get("state") != "assessed_clear" or bool(gap.get("evidence_refs")), "unsupported clear gap")
    if gap["state"] != "assessed_clear":
        require(all(gap.get(k) for k in ("kind", "question", "missing", "next")), "unspecified gap")
        blockers.append(gap)
    scope_state = "determined" if not pending and gap["state"] == "assessed_clear" else "undetermined"
    acquisition = next(a for a in output_axes if a["axis_id"] == "acquisition")
    complete = scope_state == "determined" and all(a["terminal"] for a in output_axes) and acquisition["state"] == "resolved"
    return {"item_id": item_id, "registry_revision": contract["revision"], "routing": routing,
            "pending_scope_refs": pending, "required_axes": output_axes,
            "first_contact": [{"axis_id": key[0], "scope_ref": key[1], "contributors": sorted(value),
                               "definition_refs": [f"{p}/first_contact/{key[0]}" for p in sorted(value)],
                               "expression_state": "deferred"} for key, value in sorted(first.items())],
            "scope_state": scope_state, "coverage_gap_state": gap["state"],
            "acquisition_state": acquisition["state"],
            "item_investigation_state": "complete" if complete else "incomplete", "blockers": blockers}


def applications(contract: dict, evidence: list[dict], inherited: dict) -> list[dict]:
    validate_contract(contract)
    exact_rows(evidence)
    require(all(row["registry_revision"] == contract["revision"] and row["snapshot"] == contract["snapshot"]
                and row["accepted_semantic_results"] == [] for row in evidence), "stale evidence or unbound semantic claims")
    return [resolve_item(row["item_id"], contract, routes_for(contract, row), row["gap"], inherited)
            for row in sorted(evidence, key=lambda r: r["item_id"])]


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_rows(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def apply(root: Path) -> dict:
    """The only writer: fixed investigation output paths, no runtime dispatch."""
    directory = local_path(root, ROOT)
    contract = read_json(directory / "contract.json")
    validate_contract(contract)
    inherited = inherited_contract(root, contract["inherits"])
    item_ids = targets(root)
    evidence = source_observations(root, contract, item_ids)
    rows = applications(contract, evidence, inherited)
    write_rows(directory / "evidence.jsonl", evidence)
    write_rows(directory / "applications.jsonl", rows)
    manifest = {"schema_version": "iris-layer3-investigation-manifest-v1", "revision": contract["revision"],
                "status": "adoption_subject", "adoption_requires": TEST_ID,
                "inherits": contract["inherits"], "target_sources": [binding(root, p) for p in TARGET_PATHS],
                "target_count": len(item_ids), "target_set_sha256": set_digest(item_ids),
                "members": [binding(root, p) for p in [ROOT + "/contract.json", ROOT + "/evidence.jsonl",
                                                       ROOT + "/applications.jsonl", HUMAN]],
                "product_migration_state": "deferred"}
    write_json(directory / "manifest.json", manifest)
    return {"target_count": len(rows), "complete_items": sum(r["item_investigation_state"] == "complete" for r in rows),
            "manifest": ROOT + "/manifest.json", "adoption": "requires final G1"}


def main(argv=None) -> int:
    import argparse
    from iris_tooling.build.repository_context import require_repository_context

    parser = argparse.ArgumentParser(prog="iris-tooling build layer3 investigate")
    parser.parse_args(argv)
    print(json.dumps(apply(require_repository_context().repository_root), ensure_ascii=False, sort_keys=True))
    return 0
