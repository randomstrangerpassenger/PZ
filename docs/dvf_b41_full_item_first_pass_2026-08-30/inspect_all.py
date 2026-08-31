"""Read-only, exact-FullType evidence census; not a semantic validator or producer.

Run: uv run --no-project python -B docs/dvf_b41_full_item_first_pass_2026-08-30/inspect_all.py
Only writes reports next to this script. Never installs or changes product data.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DATA = ROOT / "Iris/build/description/v2/data"
RUNTIME = ROOT / "Iris/media/lua/client/Iris/Data"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def comment_mask(text, lua=False):
    """Preserve offsets/newlines and strings, remove C/script or Lua comments."""
    chars = list(text)
    i = 0
    while i < len(text):
        if text[i] in "\"'":
            quote = text[i]
            i += 1
            while i < len(text):
                if text[i] == "\\":
                    i += 2
                elif text[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
            continue
        start = i
        if not lua and text.startswith("/*", i):
            depth = 1
            i += 2
            while i < len(text) and depth:
                if text.startswith("/*", i):
                    depth += 1
                    i += 2
                elif text.startswith("*/", i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
        elif lua and text.startswith("--", i):
            long = re.match(r"--\[(=*)\[", text[i:])
            if long:
                close = "]" + long[1] + "]"
                end = text.find(close, i + len(long[0]))
                i = len(text) if end < 0 else end + len(close)
            else:
                end = text.find("\n", i)
                i = len(text) if end < 0 else end
        elif not lua and text.startswith("//", i):
            end = text.find("\n", i)
            i = len(text) if end < 0 else end
        else:
            i += 1
            continue
        for pos in range(start, i):
            if chars[pos] not in "\r\n":
                chars[pos] = " "
    return "".join(chars)


def brace_pairs(text):
    pairs, stack = {}, []
    tokens = re.finditer(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}]', text)
    for match in tokens:
        token = match[0]
        if token == "{":
            stack.append(match.start())
        elif token == "}" and stack:
            pairs[stack.pop()] = match.start()
    return pairs, stack


def fields(body):
    return {m[1]: m[2].strip() for m in re.finditer(r"^\s*([A-Za-z][\w.]*)\s*[:=]\s*([^\r\n]*?)\s*,?\s*$", body, re.M)}


def line_at(text, pos):
    return text.count("\n", 0, pos) + 1


def write_jsonl(name, rows):
    (OUT / name).write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def md(value):
    return str(value or "—").replace("|", "\\|").replace("\n", "<br>")


facts_list = [json.loads(l) for l in (DATA / "dvf_3_3_facts.jsonl").read_text(encoding="utf-8").splitlines() if l]
facts = {x["item_id"]: x for x in facts_list}
assert len(facts_list) == len(facts) == 2105, "Denominator or duplicate identity changed"
items_input = read_json(ROOT / "Iris/input/items_itemscript.json")
recipe_input = read_json(ROOT / "Iris/input/recipes_index_full.json")
usecases = read_json(DATA / "upstream_usecases_by_fulltype.json")["fulltypes"]
owner = read_json(DATA / "tooltip_t1_layer3_owner_input.json")
pointer = (RUNTIME / "IrisLayer3DataCurrent.lua").read_text(encoding="utf-8")
generation = re.search(r'generation_id = "([^"]+)"', pointer)[1]
rendered_path = RUNTIME / "IrisLayer3Generations" / generation / "dvf_3_3_rendered.json"
rendered = read_json(rendered_path)["entries"]
assert set(rendered) == set(facts), "Rendered/fact exact identity mismatch"
snapshot_paths = [DATA / "dvf_3_3_facts.jsonl", DATA / "dvf_3_3_decisions.jsonl", DATA / "tooltip_t1_layer3_owner_input.json", DATA / "upstream_usecases_by_fulltype.json", ROOT / "Iris/input/items_itemscript.json", ROOT / "Iris/input/recipes_index_full.json", RUNTIME / "IrisLayer3DataCurrent.lua", rendered_path]
initial_hashes = {str(p.relative_to(ROOT)): digest(p) for p in snapshot_paths}

scripts, blocks, parser_notes = {}, [], []
module_imports = defaultdict(set)
raw_items = defaultdict(list)
block_pattern = re.compile(r"\b(module|item|recipe|evolvedrecipe|fixing|multistagebuild|part|table|template|vehicle)\s+([^{}\r\n]+?)\s*\{", re.I)
for path in sorted((ROOT / "scripts").rglob("*.txt")):
    original = path.read_text(encoding="utf-8-sig", errors="replace")
    text = comment_mask(original)
    pairs, unmatched = brace_pairs(text)
    rel = path.relative_to(ROOT).as_posix()
    scripts[rel] = {"text": text, "original": original, "sha256": digest(path)}
    if unmatched:
        parser_notes.append({"source": rel, "kind": "unmatched_open_braces", "count": len(unmatched)})
    modules = []
    for m in block_pattern.finditer(text):
        start = m.end() - 1
        if start not in pairs:
            parser_notes.append({"source": rel, "line": line_at(text, m.start()), "kind": "unmatched_block", "header": m[0]})
            continue
        kind, name = m[1].lower(), m[2].strip()
        module = next((a[2] for a in reversed(modules) if a[0] < start < a[1]), None)
        if kind == "module":
            modules.append((start, pairs[start], name))
            for imp in re.finditer(r"\bimports\s*\{([^{}]*)\}", text[start + 1:pairs[start]]):
                module_imports[name].update(re.findall(r"\b[A-Za-z_]\w*\b", imp[1]))
            continue
        block = {"kind": kind, "name": name, "module": module, "path": rel, "line": line_at(text, m.start()), "start": start, "end": pairs[start], "body": text[start + 1:pairs[start]]}
        block["fields"] = fields(block["body"])
        blocks.append(block)
        if kind == "item" and module:
            raw_items[module + "." + name].append(block)

all_ids = set(raw_items) | set(items_input)
short_to_ids, tag_to_ids = defaultdict(set), defaultdict(set)
for ft in all_ids:
    short_to_ids[ft.split(".", 1)[-1]].add(ft)
    for b in raw_items.get(ft, []):
        for tag in b["fields"].get("Tags", "").split(";"):
            if tag.strip():
                tag_to_ids[tag.strip()].add(ft)


def resolve_token(token, module="Base"):
    token = token.strip()
    if token in all_ids:
        return [token]
    if "." not in token and module + "." + token in all_ids:
        return [module + "." + token]
    if "." not in token:
        imported = [m + "." + token for m in module_imports.get(module, ()) if m + "." + token in all_ids]
        if len(imported) == 1:
            return imported
    return []


groups = {}
recipe_lua_path = ROOT / "lua/server/recipecode.lua"
recipe_lua = comment_mask(recipe_lua_path.read_text(encoding="utf-8-sig"), lua=True)
for m in re.finditer(r"function Recipe\.GetItemTypes\.(\w+)\(scriptItems\)(.*?)\nend", recipe_lua, re.S):
    body = m[2]
    tags = re.findall(r'getItemsTag\("([^"]+)"\)', body)
    extras = re.findall(r'addExistingItemType\(scriptItems,\s*"([^"]+)"\)', body)
    remainder = re.sub(r'scriptItems:addAll\(getScriptManager\(\):getItemsTag\("[^"]+"\)\)', "", body)
    remainder = re.sub(r'addExistingItemType\(scriptItems,\s*"[^"]+"\)', "", remainder)
    if not remainder.strip() and (tags or extras):
        resolved = set().union(*(tag_to_ids[t] for t in tags))
        for token in extras:
            resolved.update(short_to_ids.get(token, set()))
        groups[m[1]] = {"ids": sorted(resolved), "tags": tags, "extra_types": extras, "source": "lua/server/recipecode.lua", "line": line_at(recipe_lua, m.start())}

evidence, per_item = [], defaultdict(list)


def add_evidence(kind, source, line, targets, payload):
    exact_targets = sorted(set(targets) & set(facts))
    if not exact_targets:
        return
    record = {"kind": kind, "source": source, "line": line, "item_ids": exact_targets, **payload}
    eid = "ev-" + hashlib.sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]
    record["id"] = eid
    if eid in evidence_ids:
        return
    evidence_ids.add(eid)
    evidence.append(record)
    for ft in exact_targets:
        per_item[ft].append(record)


evidence_ids = set()
unresolved_recipe_tokens = []
for b in blocks:
    f = b["fields"]
    if b["kind"] == "recipe":
        result = f.get("Result", "")
        result_token = result.split("=", 1)[0].strip()
        result_ids = resolve_token(result_token, b["module"] or "Base")
        conditions = {k: v for k, v in f.items() if k in {"Time", "SkillRequired", "NeedToBeLearn", "NearItem", "OnTest", "OnCanPerform", "OnCreate", "OnGiveXP", "CanBeDoneFromFloor", "AllowFrozenItem", "Category"}}
        common = {"recipe": b["name"], "result_declaration": result, "result_item_ids": result_ids, "conditions_and_callbacks": conditions, "runtime_availability": "not_verified", "proof_level": "script_declaration_only"}
        add_evidence("recipe_output", b["path"], b["line"], result_ids, common)
        for offset, line in enumerate(b["body"].splitlines()):
            val = line.strip().rstrip(",").strip()
            if not val or re.match(r"^[A-Za-z]\w*\s*:", val) or "{" in val or "}" in val:
                continue
            role = "input"
            for prefix in ("keep ", "destroy "):
                if val.startswith(prefix):
                    role = prefix.strip()
                    val = val[len(prefix):].strip()
            for alternative in val.split("/"):
                token = re.split(r"[=;]", alternative, maxsplit=1)[0].strip()
                g = re.fullmatch(r"\[Recipe\.GetItemTypes\.(\w+)\]", token)
                resolution = None
                if g and g[1] in groups:
                    ids = groups[g[1]]["ids"]
                    resolution = groups[g[1]]
                else:
                    ids = resolve_token(token, b["module"] or "Base")
                if not ids:
                    unresolved_recipe_tokens.append({"source": b["path"], "line": b["line"] + offset + 1, "recipe": b["name"], "token": token})
                    continue
                add_evidence("recipe_" + role, b["path"], b["line"], ids, {**common, "ingredient_expression": val, "matched_alternative": alternative, "group_resolution": resolution})
    elif b["kind"] == "fixing":
        target_tokens = [x.strip() for x in f.get("Require", "").split(";")]
        target_ids = [ft for t in target_tokens for ft in resolve_token(t, b["module"] or "Base")]
        for m in re.finditer(r"^\s*Fixer\s*:\s*([^\r\n,]+)", b["body"], re.M):
            expression = m[1].strip()
            token = expression.split(";", 1)[0].split("=", 1)[0].strip()
            fixer_ids = resolve_token(token, b["module"] or "Base")
            payload = {"fixing_name": b["name"], "target_items": target_ids, "fixer_items": fixer_ids, "fixer_expression": expression, "proof_level": "script_declaration_only", "effect_amount": "not_verified"}
            add_evidence("fixing_material", b["path"], b["line"], fixer_ids, payload)
            add_evidence("fixing_target", b["path"], b["line"], target_ids, payload)
    elif b["kind"] == "multistagebuild":
        for field, role in (("ItemsRequired", "material"), ("ItemsToKeep", "tool")):
            for token in f.get(field, "").split(";"):
                ids = resolve_token(token.split("=", 1)[0], b["module"] or "Base")
                add_evidence("multistage_" + role, b["path"], b["line"], ids, {"stage": b["name"], "declared_fields": f, "proof_level": "script_declaration_only", "runtime_availability": "not_verified"})
    elif b["kind"] == "part" and "/vehicles/" in b["path"]:
        for token in f.get("itemType", "").split(";"):
            add_evidence("vehicle_part_type", b["path"], b["line"], resolve_token(token), {"part": b["name"], "proof_level": "script_declaration_only", "template_vehicle_binding": "not_fully_resolved"})
        for operation in ("install", "uninstall"):
            for t in blocks:
                if t["path"] != b["path"] or t["kind"] != "table" or t["name"] != operation or not (b["start"] < t["start"] < t["end"] < b["end"]):
                    continue
                for m in re.finditer(r"\btype\s*=\s*([\w.]+)", t["body"]):
                    add_evidence("vehicle_" + operation + "_requirement", t["path"], t["line"], resolve_token(m[1]), {"part": b["name"], "operation": operation, "declaration": t["body"].strip(), "proof_level": "script_declaration_only", "template_vehicle_binding": "not_fully_resolved"})

lua_sources = {}
for path in sorted((ROOT / "lua").rglob("*.lua")):
    rel = path.relative_to(ROOT).as_posix()
    text = comment_mask(path.read_text(encoding="utf-8-sig", errors="replace"), lua=True)
    lua_sources[rel] = {"sha256": digest(path)}
    # A lexical locator is never treated as proof of an executable behavior.
    function = None
    for number, line in enumerate(text.splitlines(), 1):
        m = re.match(r"\s*(?:(?:local\s+)?function\s+([\w.:]+)|([\w.:]+)\s*=\s*function\b)", line)
        if m:
            function = m[1] or m[2]
        is_loot = any(x in rel for x in ("Distributions", "forageDefinitions", "Suburbs", "/Translate/"))
        for match in re.finditer(r'(["\'])(.*?)(?<!\\)\1', line):
            token = match[2]
            ids = [token] if token in all_ids else sorted(short_to_ids.get(token, set()))
            tag_match = re.search(r'(?:hasTag|getItemsTag|containsTag\w*|getFirstTag\w*|getAllTag\w*)\s*\([^\n]*$', line[:match.start()])
            if tag_match and token in tag_to_ids:
                add_evidence("lua_tag_locator", rel, number, tag_to_ids[token], {"tag": token, "nearest_preceding_function": function, "code": line.strip(), "proof_level": "lexical_candidate_not_behavior_proof"})
            if token.startswith("need:"):
                ids = resolve_token(token[5:])
                kind = "lua_build_material_declaration"
            elif is_loot:
                kind = "lua_loot_locator"
            else:
                kind = "lua_item_locator"
            add_evidence(kind, rel, number, ids, {"matched_literal": token, "identity_resolution": "exact_fulltype" if token in all_ids or token.startswith("need:") else "short_type_candidate", "nearest_preceding_function": function, "code": line.strip(), "proof_level": "lexical_candidate_not_behavior_proof"})

USEFUL_FIELDS = set("HungerChange ThirstChange UnhappyChange BoredomChange StressChange FatigueChange EnduranceChange Alcoholic PoisonPower PoisonDetectionLevel BandagePower AlcoholPower ReduceInfectionPower Capacity WeightReduction MaxDamage MinDamage MaxRange MinRange TreeDamage DoorDamage WeaponPart ClipSize AmmoType ReloadTime AimingTime MinAngle HitChance DamageModifier CanStoreWater ReplaceOnUse ReplaceOnUseOn ReplaceOnDeplete UseDelta FuelType FuelRatio LightStrength LightDistance TorchCone CanBeActivated BatteryPowered TaughtRecipes SkillTrained LvlSkillTrained NumLevelsTrained NumberOfPages CanBeWrite EvolvedRecipe FoodType DaysFresh DaysTotallyRotten Calories Proteins Lipids Carbohydrates BiteDefense ScratchDefense BulletDefense Insulation WindResistance WaterResistance RunSpeedModifier BodyLocation BloodLocation WorldObjectSprite VehicleType MechanicsItem ItemCapacity MaxCapacity ConditionMax MetalValue CanBandage Medical CanBeEquipped CanBeAttached CanBePlaced".split())
HINT_ONLY_FIELDS = set("BodyLocation BloodLocation WorldObjectSprite MechanicsItem MetalValue ConditionMax FoodType Medical VehicleType CanBeEquipped CanBeAttached CanBePlaced".split())
USEFUL_FIELDS.update("TeachedRecipes OnEat OnCooked OnCreate BadCold BadInMicrowave GoodHot CantBeFrozen CantEat CannedFood DangerousUncooked IsCookable MinutesToBurn MinutesToCook RemoveNegativeEffectOnCooked RemoveUnhappinessWhenCooked ReplaceOnCooked ReplaceOnRotten Spice Poison UseForPoison FluReduction PainReduction ReduceFoodSickness CanBarricade CanBeRemote CanBeReused CriticalChance CritDmgMultiplier critDmgMultiplier BaseSpeed CombatSpeedModifier EnduranceMod EquippedNoSprint ExplosionPower ExplosionRange ExplosionTimer FirePower FireRange FishingLure HairDye HerbalistType IsWaterSource ItemWhenDry Wet WetCooldown KeepOnDeplete MakeUpType MaxAmmo MaxHitCount NoiseDuration NoiseRange OnlyAcceptCategory PageToWrite Padlock DigitalPadlock ProtectFromRainWhenEquipped RainFactor RemoteController RemoteRange ReplaceTypes RequireInHandOrInventory RequiresEquippedBothHands SensorRange SmokeRange StompPower Trap TriggerExplosionTimer triggerExplosionTimer TwoHandWeapon UseEndurance UseSelf UseWhileEquipped UseWhileUnequipped UseWorldItem WeightEmpty MountOn PartType WeightModifier MaxRangeModifier MinRangeModifier AimingTimeModifier HitChanceModifier ReloadTimeModifier RecoilDelayModifier AngleModifier EngineLoudness SuspensionCompression SuspensionDamping WheelFriction brakeForce ConditionAffectsCapacity ConditionLowerOffroad ConditionLowerStandard ConditionLowerChanceOneIn CanHaveHoles ChanceToFall NeckProtectionModifier RemoveOnBroken TransmitRange MicRange MinChannel MaxChannel TwoWay NoTransmit UsesBattery IsPortable IsTelevision AcceptMediaType MediaCategory AlarmSound SoundRadius ClothingItemExtra ClothingItemExtraOption OtherHandRequire OtherHandUse MagazineType FireMode FireModePossibilities RecoilDelay AimingMod AimingPerkCritModifier AimingPerkHitChanceModifier AimingPerkMinAngleModifier AimingPerkRangeModifier MinimumSwingTime SwingTime MaxRange MinRange HitChance ToHitModifier JamGunChance PiercingBullets ProjectileCount AlwaysKnockdown KnockBackOnNoDeath KnockdownMod PushBackMod DisappearOnUse".split())
REAL_WORLD_PATTERNS = ["연주", "이를 닦", "반려견", "개가 씹", "몸에 향", "머리를 빗", "사진이나 그림을 넣", "몸단장 상태를 비춰", "놀이 규칙", "가볍게 즐", "훈련이나 레저", "기분을 달랠", "구역 표시를 정리", "먹거나 나눠 먹", "다시 쓰거나 처리"]
groups_primary = defaultdict(list)
for ft, fact in facts.items():
    groups_primary[fact.get("primary_use")].append(ft)
ordered_groups = sorted(groups_primary.items(), key=lambda x: (-len(x[1]), x[0] or ""))
group_ids = {text: f"text-{i:03}" for i, (text, _) in enumerate(ordered_groups, 1)}
audit_rows = []
for ft in sorted(facts):
    fact, public = facts[ft], rendered[ft]
    definitions = raw_items.get(ft, [])
    unique_field_sets = {json.dumps(b["fields"], sort_keys=True) for b in definitions}
    combined = definitions[0]["fields"] if len(unique_field_sets) == 1 else {}
    useful = {k: v for k, v in combined.items() if k in USEFUL_FIELDS}
    actionable_fields = {k: v for k, v in useful.items() if k not in HINT_ONLY_FIELDS}
    lost = {k: v for k, v in useful.items() if k not in items_input.get(ft, {})}
    evs = per_item.get(ft, [])
    by_kind = Counter(e["kind"] for e in evs)
    structured = [e for e in evs if e["proof_level"] == "script_declaration_only"]
    use_declarations = [e for e in structured if e["kind"] != "recipe_output"]
    lua_action = [e for e in evs if e["kind"] in {"lua_item_locator", "lua_tag_locator", "lua_build_material_declaration"}]
    primary = fact.get("primary_use") or ""
    text = public.get("text_ko") or ""
    primary_is_public = bool(primary) and primary.rstrip(".。 ") in text
    flags = []
    if not definitions:
        flags.append("RAW_ITEM_DEFINITION_NOT_LOCATED")
    if len(unique_field_sets) > 1:
        flags.append("MULTIPLE_RAW_ITEM_DEFINITIONS_REQUIRE_LOAD_ORDER_REVIEW")
    if any(str(v).lower() == "true" for k, v in combined.items() if k.lower() == "obsolete"):
        flags.append("RAW_ITEM_MARKED_OBSOLETE_REQUIRES_AVAILABILITY_REVIEW")
    if lost:
        flags.append("RAW_DETAIL_FIELDS_ABSENT_FROM_ITEMSCRIPT_INPUT")
    if any(w in primary for w in REAL_WORLD_PATTERNS):
        flags.append("REAL_WORLD_OR_ADDED_EFFECT_WORDING_REQUIRES_GAME_PROOF")
    if "작업" in primary or "용도에 맞게" in primary:
        flags.append("ABSTRACT_WORKFLOW_TEXT_REQUIRES_ITEM_SPECIFIC_REWRITE")
    if any(w in primary for w in ("보호", "복구", "치료", "기분", "비를 막", "온도를 높", "전기를 공급")):
        flags.append("EFFECT_OR_OUTCOME_CLAIM_REQUIRES_MECHANISM_TRACE")
    if any(w in primary for w in ("없는", "쓸 수 없는", "용도가 없")):
        flags.append("NEGATIVE_CLAIM_REQUIRES_CLOSED_SCOPE_EVIDENCE")
    if not text:
        flags.append("CURRENT_PUBLIC_BODY_EMPTY")
    elif primary and not primary_is_public:
        flags.append("FACT_PRIMARY_NOT_VERBATIM_PRESENT_IN_PUBLIC_BODY")
    if not primary and text:
        flags.append("NO_PRIMARY_USE_IN_FACT_ROW")
    existing_positive = [x for x in usecases.get(ft, {}).get("use_cases", []) if x.get("line_kind") == "evidence"]
    # This classification concerns data availability, not the truth of prose.
    if len(unique_field_sets) > 1 or not definitions:
        status = "IDENTITY_RECONCILIATION_REQUIRED"
    elif use_declarations:
        status = "STRUCTURED_DECLARATIONS_AVAILABLE"
    elif actionable_fields:
        status = "STATIC_FIELDS_AVAILABLE"
    elif lua_action:
        status = "LUA_TRACE_REQUIRED"
    else:
        status = "IDENTITY_OR_CLASSIFICATION_ONLY"
    next_steps = []
    if use_declarations:
        next_steps.append("제작·수리·부품·건축 선언의 대상/역할/결과/조건을 보존해 추출")
    if lost:
        next_steps.append("기존 입력에 빠진 원본 속성을 허용된 설명 입력 경로로 보강")
    if lua_action:
        next_steps.append("Lua 후보의 호출·조건·상태 변경 및 비활성 분기 여부를 추적")
    if not next_steps:
        next_steps.append("태그·동적 선택·엔진 경로를 추가 확인하고 미확인 용도는 생성하지 않음")
    if "REAL_WORLD_OR_ADDED_EFFECT_WORDING_REQUIRES_GAME_PROOF" in flags:
        next_steps.append("현실 활동 또는 추가 효과 표현을 게임 근거와 대조; 이름만으로 유지 금지")
    audit_rows.append({
        "item_id": ft, "scope": "full_2105_first_pass_evidence_inventory", "status": status,
        "current_primary_use": fact.get("primary_use"), "current_text_ko": public.get("text_ko"),
        "primary_text_group": group_ids[fact.get("primary_use")], "primary_verbatim_in_public_body": primary_is_public,
        "current_origins": fact.get("fact_origin"), "current_cluster": fact.get("slot_meta", {}).get("interaction_cluster"),
        "tooltip_s2_selected": ft in owner["entries"],
        "raw_item_definitions": [{"source": b["path"], "line": b["line"], "fields": b["fields"]} for b in definitions],
        "current_itemscript_fields": items_input.get(ft), "raw_detail_fields": useful, "raw_detail_fields_missing_from_input": lost,
        "raw_action_or_effect_field_candidates": actionable_fields,
        "use_declaration_count": len(use_declarations), "recipe_output_declaration_count": by_kind["recipe_output"],
        "existing_recipe_relations": recipe_input.get("items", {}).get(ft, []),
        "existing_usecases": usecases.get(ft, {}).get("use_cases", []), "existing_positive_usecase_count": len(existing_positive),
        "food_semantic_assertions": fact.get("food_semantic_assertions", []),
        "source_evidence_counts": dict(sorted(by_kind.items())), "source_evidence_ids": [e["id"] for e in evs],
        "review_flags": flags, "next_steps": next_steps,
        "semantic_truth_verdict": "NOT_DETERMINED_BY_FIRST_PASS", "runtime_reachability_verified": False,
        "acquisition_claims_audited": False, "new_authority_created": False,
    })

assert len(audit_rows) == 2105 and {r["item_id"] for r in audit_rows} == set(facts)
assert all(r["status"] and r["next_steps"] for r in audit_rows)
assert all(digest(ROOT / rel) == value for rel, value in initial_hashes.items()), "Inputs changed during audit"
status_counts = Counter(r["status"] for r in audit_rows)
flag_counts = Counter(f for r in audit_rows for f in r["review_flags"])
summary = {
    "scope": "all 2105 DVF exact FullTypes; first-pass evidence availability and granularity only",
    "generation_id": generation, "item_count": len(audit_rows), "unique_nonempty_primary_texts": len(groups_primary) - (None in groups_primary),
    "primary_text_groups_including_empty": len(groups_primary), "status_counts": dict(status_counts), "review_flag_counts": dict(flag_counts),
    "priority": ["IDENTITY_RECONCILIATION_REQUIRED", "STRUCTURED_DECLARATIONS_AVAILABLE", "STATIC_FIELDS_AVAILABLE", "LUA_TRACE_REQUIRED", "IDENTITY_OR_CLASSIFICATION_ONLY"],
    "nonexclusive_availability_counts": {
        "raw_definition_found": sum(bool(r["raw_item_definitions"]) for r in audit_rows),
        "use_declarations": sum(bool(r["use_declaration_count"]) for r in audit_rows),
        "recipe_output_declarations": sum(bool(r["recipe_output_declaration_count"]) for r in audit_rows),
        "static_action_or_effect_field_candidates": sum(bool(r["raw_action_or_effect_field_candidates"]) for r in audit_rows),
        "nonloot_lua_candidates": sum(any(r["source_evidence_counts"].get(k, 0) for k in ("lua_item_locator", "lua_tag_locator", "lua_build_material_declaration")) for r in audit_rows),
    },
    "public_primary_real_world_review_count": sum(r["primary_verbatim_in_public_body"] and "REAL_WORLD_OR_ADDED_EFFECT_WORDING_REQUIRES_GAME_PROOF" in r["review_flags"] for r in audit_rows),
    "source_files": {"scripts": len(scripts), "lua": len(lua_sources)}, "raw_item_ids": len(raw_items),
    "script_block_counts": dict(Counter(b["kind"] for b in blocks)), "static_recipe_groups_resolved": len(groups),
    "evidence_count": len(evidence), "evidence_kind_counts": dict(Counter(e["kind"] for e in evidence)),
    "recipe_unresolved_token_count": len(unresolved_recipe_tokens), "parser_notes": parser_notes,
    "input_hashes": initial_hashes, "product_files_modified": False,
    "limitations": [
        "No PZ execution or per-item gameplay acceptance was performed.",
        "This is a bounded lexical/declaration inventory, not a complete parser or engine analysis. Generic type behavior, complex recipe groups, dynamic selectors, moveable sprite properties and Java-only effects may be absent from the candidate counts.",
        "Script declarations preserve fields, but availability, callbacks, load order and engine semantics remain unverified.",
        "Lua hits are lexical locators, not proof of action or effect; function names are nearest preceding declarations, not a full AST scope.",
        "Short type names are candidates; exact FullTypes are never case-normalized or merged.",
        "Only simple unconditional tag/addExistingItemType recipe groups are expanded; unresolved expressions are retained.",
        "Recipe outputs are recorded as acquisition declarations and do not alone qualify as use evidence; classification-only fields are not promoted to action/effect candidates.",
        "Raw static fields may require enum/unit/state semantics before public wording; their presence is not a correctness verdict.",
        "Reality/effect wording flags are review triggers, not confirmed errors; lack of a hit is not proof of no use.",
        "Acquisition/location text is retained for context but not audited by this purpose/effect first pass.",
        "Current classification evidence allowlists and adoption contracts remain unchanged; report findings are not production authority.",
    ],
}
write_jsonl("item_audit.jsonl", audit_rows)
write_jsonl("source_evidence.jsonl", sorted(evidence, key=lambda e: (e["source"], e["line"], e["kind"], e["id"])))
write_jsonl("unresolved_recipe_tokens.jsonl", unresolved_recipe_tokens)
write_jsonl("source_files.jsonl", [{"path": p, "sha256": s["sha256"]} for p, s in sorted({**scripts, **lua_sources}.items())])
(OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

labels = {
    "STRUCTURED_DECLARATIONS_AVAILABLE": "구체적 선언 있음·실행 조건 확인 필요",
    "STATIC_FIELDS_AVAILABLE": "정적 속성 있음·효과 의미 확인 필요",
    "LUA_TRACE_REQUIRED": "Lua 후보 있음·행동 추적 필요",
    "IDENTITY_OR_CLASSIFICATION_ONLY": "이번 스캔에서는 정체성/분류 수준",
    "IDENTITY_RECONCILIATION_REQUIRED": "원본 항목 식별 확인 필요",
}
header = ["# DVF B41 전체 2,105개 1차 근거 점검", "", "전체 exact FullType을 전수 대조한 정보 보존/추출 가능성 점검이다. 설명의 사실성 전수 검증 완료나 인게임 동작 보장을 뜻하지 않는다. 파일에 없다는 이유로 게임 용도가 없다고 판정하지 않는다.", "", f"현재 generation: `{generation}`", "", "제품 파일 변경: 없음. 획득처 설명은 이번 용도/효과 점검 범위 밖이다.", "", "## 전체 분포", "", "| 구분 | 항목 수 |", "|---|---:|"]
header += [f"| {labels[k]} | {v} |" for k, v in status_counts.items()]
header += ["", "이 분포는 다음 단계의 조사 경로를 정하는 분류다. 첫 행부터 순서대로 우선 적용하므로 범주는 서로 배타적이며 합계는 2,105다. 어떤 범주도 해당 아이템의 현재 설명이 정확하다는 뜻이 아니다.", "", "## 산출물", "", "- `items.md`: 2,105개 전 항목의 설명·조사 분류·원본 첫 위치·검토 표시.", "- `item_audit.jsonl`: 항목별 전체 원본 필드·기존 추출물·근거 ID·누락 필드·다음 확인 작업.", "- `source_evidence.jsonl`: 근거 ID에 대응하는 제작법·수리·차량·Lua 후보 원문과 위치.", "- `primary_text_groups.md`: 175개 비어 있지 않은 원문 및 빈 값 그룹의 전체 아이템 목록. 문장별 검토 단위.", "- `unresolved_recipe_tokens.jsonl`: 해석하지 못한 제작법 토큰. 임의로 보완하지 않음.", "- `source_files.jsonl`, `summary.json`: 읽은 원본/입력 해시, 집계와 한계.", "", "## 판정 한계", "", "이 결과는 의미 검증기가 아니다. Lua의 문자열 일치는 위치를 찾는 보조 정보이며 실행 가능성을 보장하지 않는다. 제작 선언도 비활성 콘텐츠·콜백·기술/지식 조건·템플릿 연결을 추가 확인해야 한다. 실제 효과가 Java 엔진에 있는 경우 Lua에서 호출 사실만 확인될 수 있다. 현실 활동 표현 표시 역시 확정 오류 판정이 아니다.", "", "## 재현", "", "```powershell", "uv run --no-project python -B docs/dvf_b41_full_item_first_pass_2026-08-30/inspect_all.py", "```", ""]
(OUT / "README.md").write_text("\n".join(header), encoding="utf-8")
readme = (OUT / "README.md").read_text(encoding="utf-8")
readme = readme.replace("첫 행부터 순서대로 우선 적용하므로", "식별 확인 → 용도 선언 → 정적 속성 → Lua 후보 → 분류 수준 순으로 우선 적용하므로")
readme += "\n## 분류 기준의 범위\n\n제작법 결과물로만 등장하는 경우는 사용 근거로 세지 않는다. `MetalValue`, `MechanicsItem`, 착용 부위 등 분류/간접 속성만으로 구체적인 행동이나 효과가 있다고 판정하지 않는다. 정적 속성 범주는 수치·변환·콜백 등의 원본 후보 필드가 있다는 뜻이며, 그 의미와 게임 내 활성 여부는 별도 검증 대상이다.\n\n복잡한 의류 찢기 등 동적 Recipe.GetItemTypes 함수, 공통 아이템 타입 동작, moveable 스프라이트 속성, Java 엔진 내부는 완전히 해석하지 않았다. 따라서 분류 수준으로 남은 항목도 실제 용도가 없다는 뜻이 아니다. 미해결 레시피 토큰 42건에는 `Water` 28건 및 동적 그룹 등이 포함된다.\n\n`findings.md`에는 확인된 문제와 다음 단계가, `validate_report.py`에는 2,105개 누락/중복·근거 참조·원본 해시 검사가 있다. 검증 명령은 `uv run --no-project python -B docs/dvf_b41_full_item_first_pass_2026-08-30/validate_report.py`다.\n"
(OUT / "README.md").write_text(readme, encoding="utf-8")
lines = ["# 전체 2,105개 항목", "", "상세 근거는 같은 폴더의 item_audit.jsonl 및 source_evidence.jsonl에 있다. 아래 수는 의미가 검증된 용도 수가 아니라 선언/후보 위치 수다. 모든 행의 사실성 최종 판정은 미결정이다. 용도 선언 수에서는 제작법 결과물 기록을 제외한다.", "", "| # | FullType | 현재 공개 설명 | 1차 조사 경로 | 원본 아이템 | 용도 선언 수 | Lua 후보 수 | S2 | 원본 상세 필드 누락 | 검토 표시 |", "|---:|---|---|---|---|---:|---:|---|---|---|"]
for i, row in enumerate(audit_rows, 1):
    src = row["raw_item_definitions"]
    link = f"[{src[0]['source']}:{src[0]['line']}]({(ROOT / src[0]['source']).as_posix()}:{src[0]['line']})" if src else "미확인"
    evs = per_item[row["item_id"]]
    lines.append(f"| {i} | {row['item_id']} | {md(row['current_text_ko'])} | {labels[row['status']]} | {link} | {row['use_declaration_count']} | {sum(e['kind'] in {'lua_item_locator','lua_tag_locator','lua_build_material_declaration'} for e in evs)} | {'선택' if row['tooltip_s2_selected'] else '미선택'} | {md(', '.join(row['raw_detail_fields_missing_from_input']))} | {md(', '.join(row['review_flags']))} |")
(OUT / "items.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
lines = ["# 현재 primary_use 전체 문장 그룹", "", "동일 문장도 아이템별 근거가 다르므로 같은 판정을 자동 부여하지 않는다. 전체 175개 비어 있지 않은 문장과 빈 값 그룹을 포함한다. 현실 활동/효과 표시는 확정 오류가 아니라 대조할 주장이다.", ""]
for text, ids in ordered_groups:
    group_rows = [r for r in audit_rows if r["item_id"] in ids]
    lines += [f"## {group_ids[text]} · {len(ids)}개", "", text or "(primary_use 없음)", "", "검토 표시: " + md(", ".join(sorted({f for r in group_rows for f in r["review_flags"]}))), "", "항목: " + ", ".join(f"`{ft}`" for ft in sorted(ids)), ""]
(OUT / "primary_text_groups.md").write_text("\n".join(lines), encoding="utf-8")
print(json.dumps({k: summary[k] for k in ("item_count", "status_counts", "review_flag_counts", "evidence_count", "recipe_unresolved_token_count", "parser_notes")}, ensure_ascii=False, indent=2))
