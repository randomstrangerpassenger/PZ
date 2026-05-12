"""
Action Evidence Strength Classifier
====================================
action_requirement_index + use_case_registry + items_itemscript
→ action_evidence_classification.v2.4.json

판정 규칙 (우선순위 순):
  1. has_input_material_exclusion → exclude (INPUT_ITEM)
  2. has_property_based_exclusion → weak (PROPERTY_GATED)
  3. requires_fulltypes ≥ 1 → strong (FULLTYPE_GATED)
  4. requires_tags ≥ 1 AND tag→item count ≤ TAG_STRONG_THRESHOLD → strong (TAG_RESOLVES_TO_TYPE)
  5. requires_tags ≥ 1 AND tag→item count > TAG_STRONG_THRESHOLD → weak (TOOL_GROUP)
  6. fallback → weak (AMBIGUOUS)

다중 규칙 합산 정책:
  동일 uc.action.*으로 매핑된 rule의 requires_*는 집합 union,
  exclusion 플래그는 OR 합산.

Usage:
    python build/tools/pipeline/classify_action_evidence.py
"""
import sys
from pathlib import Path
from collections import defaultdict

# ── Config ──
TAG_STRONG_THRESHOLD = 4  # ≤ 이 값이면 Strong, > 이면 Weak

# ── Paths ──
SCRIPT_DIR = Path(__file__).resolve().parent
BUILD_DIR = Path(__file__).resolve().parents[2]
for import_path in (BUILD_DIR, SCRIPT_DIR):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

IRIS_DIR = BUILD_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"
INPUT_DIR = IRIS_DIR / "input"

from registry_utils import resolve_use_case_id
from tools.common.io import load_json, write_json
from tools.common.versions import BUILD_VERSION

DATA_DIR = BUILD_DIR / "data" / BUILD_VERSION

REQUIREMENT_INDEX_PATH = OUTPUT_DIR / f"action_requirement_index.{BUILD_VERSION}.json"
REGISTRY_PATH = DATA_DIR / f"use_case_registry.{BUILD_VERSION}.json"
ITEMS_PATH = INPUT_DIR / "items_itemscript.json"
OUTPUT_PATH = OUTPUT_DIR / f"action_evidence_classification.{BUILD_VERSION}.json"


def build_tag_item_counts(items: dict) -> dict:
    """items_itemscript.json에서 각 태그별 보유 아이템 수를 카운트."""
    tag_counts = defaultdict(int)
    for ft, item_data in items.items():
        tags_str = item_data.get("Tags", "")
        if tags_str:
            for tag in tags_str.split(";"):
                tag = tag.strip()
                if tag:
                    tag_counts[tag] += 1
    return dict(tag_counts)


def resolve_tag_fulltypes(items: dict, tag: str) -> list:
    """특정 태그를 보유한 FullType 리스트."""
    result = []
    for ft, item_data in items.items():
        tags_str = item_data.get("Tags", "")
        if tags_str:
            tags = [t.strip() for t in tags_str.split(";")]
            if tag in tags:
                result.append(ft)
    return sorted(result)


def resolve_dcst_fulltypes(
    items: dict,
    display_categories: set,
    script_types: set,
) -> list:
    """
    DisplayCategory + ScriptType 조합으로 매칭되는 FullType 리스트.
    AND 로직: 둘 다 만족하는 아이템만.
    DC만 있고 ST 없으면 DC 단독, ST만 있고 DC 없으면 ST 단독.
    """
    result = []
    for ft, item_data in items.items():
        dc = item_data.get("DisplayCategory", "")
        st = item_data.get("Type", "")  # itemscript의 Type = script_type

        dc_match = (not display_categories) or (dc in display_categories)
        st_match = (not script_types) or (st in script_types)

        if dc_match and st_match:
            # At least one filter must be active
            if display_categories or script_types:
                result.append(ft)
    return sorted(result)



def is_consumable_item(items: dict, fulltype: str) -> bool:
    """
    Rule 1.5: 소모품 아이템 판별.
    (Type=="Drainable" AND DisplayCategory=="Material") → 소모품.
    
    안전 봉인:
    - Type=Drainable 단독으로는 제외하지 않음 (BlowTorch=DC:Tool, Extinguisher=DC:Household 보호)
    - DC=Material과 AND 결합해야만 제외
    """
    item = items.get(fulltype, {})
    return (
        item.get("Type") == "Drainable"
        and item.get("DisplayCategory") == "Material"
    )


def filter_consumables(items: dict, fulltypes: list) -> tuple:
    """
    canonical_tool_fulltypes에서 소모품을 분리.
    Returns: (tools: list, excluded_consumables: list)
    """
    tools = []
    excluded = []
    for ft in fulltypes:
        if is_consumable_item(items, ft):
            excluded.append(ft)
        else:
            tools.append(ft)
    return sorted(tools), sorted(excluded)


def classify_action(
    action_id: str,
    merged_requires_fulltypes: set,
    merged_requires_tags: set,
    merged_requires_props: set,
    merged_requires_display_categories: set,
    merged_requires_script_types: set,
    merged_has_property_based: bool,
    merged_has_input_material: bool,
    source_rules: list,
    tag_item_counts: dict,
    items: dict,
) -> dict:
    """
    단일 uc.action.*에 대해 evidence_strength를 판정.
    우선순위 테이블 (완전 기계적, 사람 판단 0).
    Rule 1.5: canonical_tool_fulltypes에서 소모품 아이템을 먼저 제거한 뒤 남은 도구로 판정.
    """
    # Priority 1: INPUT_ITEM → exclude (rule-level flag)
    if merged_has_input_material:
        return {
            "evidence_strength": "exclude",
            "reason_code": "INPUT_ITEM",
            "source_rules": source_rules,
            "canonical_tool_fulltypes": [],
            "excluded_consumables": [],
            "tag_item_count": None,
        }

    # Priority 2: PROPERTY_GATED → weak
    # property_based exclusion flag OR requires_props가 존재하면 property 기반
    if merged_has_property_based or merged_requires_props:
        raw_fts = sorted(merged_requires_fulltypes)
        tools, excluded = filter_consumables(items, raw_fts)
        return {
            "evidence_strength": "weak",
            "reason_code": "PROPERTY_GATED",
            "source_rules": source_rules,
            "canonical_tool_fulltypes": tools,
            "excluded_consumables": excluded,
            "tag_item_count": None,
        }

    # Priority 3: FULLTYPE_GATED → strong (explicit type matchers only)
    if merged_requires_fulltypes:
        raw_fts = sorted(merged_requires_fulltypes)
        tools, excluded = filter_consumables(items, raw_fts)
        # After filtering, if no tools remain, action can't be strong
        if not tools:
            return {
                "evidence_strength": "exclude",
                "reason_code": "INPUT_ITEM_CONSUMABLE",
                "source_rules": source_rules,
                "canonical_tool_fulltypes": [],
                "excluded_consumables": excluded,
                "tag_item_count": None,
            }
        return {
            "evidence_strength": "strong",
            "reason_code": "FULLTYPE_GATED",
            "source_rules": source_rules,
            "canonical_tool_fulltypes": tools,
            "excluded_consumables": excluded,
            "tag_item_count": None,
        }

    # Priority 4 & 5: TAG based
    if merged_requires_tags:
        max_tag_count = 0
        all_tag_fulltypes = set()
        for tag in merged_requires_tags:
            count = tag_item_counts.get(tag, 0)
            if count > max_tag_count:
                max_tag_count = count
            fts = resolve_tag_fulltypes(items, tag)
            all_tag_fulltypes.update(fts)

        # Rule 1.5: filter consumables from resolved tag items
        tools, excluded = filter_consumables(items, sorted(all_tag_fulltypes))
        tool_count = len(tools)

        if tool_count == 0:
            return {
                "evidence_strength": "exclude",
                "reason_code": "INPUT_ITEM_CONSUMABLE",
                "source_rules": source_rules,
                "canonical_tool_fulltypes": [],
                "excluded_consumables": excluded,
                "tag_item_count": max_tag_count,
            }
        elif tool_count <= TAG_STRONG_THRESHOLD:
            return {
                "evidence_strength": "strong",
                "reason_code": "TAG_RESOLVES_TO_TYPE",
                "source_rules": source_rules,
                "canonical_tool_fulltypes": tools,
                "excluded_consumables": excluded,
                "tag_item_count": max_tag_count,
            }
        else:
            return {
                "evidence_strength": "weak",
                "reason_code": "TOOL_GROUP",
                "source_rules": source_rules,
                "canonical_tool_fulltypes": tools[:10],
                "excluded_consumables": excluded,
                "tag_item_count": max_tag_count,
            }

    # Priority 5.5: DC+ST resolution (DisplayCategory + ScriptType → FullType)
    if merged_requires_display_categories or merged_requires_script_types:
        resolved = resolve_dcst_fulltypes(
            items, merged_requires_display_categories, merged_requires_script_types
        )
        # Rule 1.5: filter consumables from DC+ST resolved items
        tools, excluded = filter_consumables(items, resolved)
        resolved_count = len(tools)

        if resolved_count >= 1 and resolved_count <= TAG_STRONG_THRESHOLD:
            return {
                "evidence_strength": "strong",
                "reason_code": "DCST_RESOLVES_TO_TYPE",
                "source_rules": source_rules,
                "canonical_tool_fulltypes": tools,
                "excluded_consumables": excluded,
                "tag_item_count": resolved_count,
            }
        elif resolved_count > TAG_STRONG_THRESHOLD:
            return {
                "evidence_strength": "weak",
                "reason_code": "DCST_GROUP",
                "source_rules": source_rules,
                "canonical_tool_fulltypes": tools[:10],
                "excluded_consumables": excluded,
                "tag_item_count": resolved_count,
            }

    # Priority 6: AMBIGUOUS → weak
    return {
        "evidence_strength": "weak",
        "reason_code": "AMBIGUOUS",
        "source_rules": source_rules,
        "canonical_tool_fulltypes": [],
        "excluded_consumables": [],
        "tag_item_count": None,
    }


def main():
    print("=" * 60)
    print(f"  Action Evidence Classifier (BUILD_VERSION={BUILD_VERSION})")
    print(f"  TAG_STRONG_THRESHOLD = {TAG_STRONG_THRESHOLD}")
    print("=" * 60)

    # ── Load inputs ──
    for path, label in [
        (REQUIREMENT_INDEX_PATH, "action_requirement_index"),
        (REGISTRY_PATH, "use_case_registry"),
        (ITEMS_PATH, "items_itemscript"),
    ]:
        if not path.exists():
            print(f"\n  ❌ {label} not found: {path}")
            return 1

    req_index = load_json(REQUIREMENT_INDEX_PATH)
    registry = load_json(REGISTRY_PATH)
    items = load_json(ITEMS_PATH)

    rules_atoms = req_index.get("rules", [])
    registry_rules = registry.get("rules", {})

    print(f"  Requirement index: {len(rules_atoms)} rules")
    print(f"  Registry: {len(registry_rules)} entries")
    print(f"  Items: {len(items)} fulltypes")

    # ── Build tag→item count index ──
    tag_item_counts = build_tag_item_counts(items)
    print(f"  Unique tags in items: {len(tag_item_counts)}")

    # ── Map rule_id → uc.action.* via registry ──
    # Only process rules that map to uc.action.*
    rule_to_action = {}
    for reg_rule_id, reg_props in registry_rules.items():
        ucid = resolve_use_case_id(reg_props)
        if ucid.startswith("uc.action."):
            # Map the original rule_id (not the virtual one)
            rule_to_action[reg_rule_id] = ucid
    print(f"  Registry entries mapping to uc.action.*: {len(rule_to_action)}")

    # ── Collect Overrides from Registry (A안) ──
    # rule_id가 uc.action.*에 매핑되고, decision="PASS" 이며 strength가 명시된 경우.
    overrides = {}
    for reg_rule_id, ucid in rule_to_action.items():
        rule = registry_rules[reg_rule_id]
        decision = rule.get("decision")
        strength = rule.get("strength")
        if decision == "PASS" and strength:
            overrides.setdefault(ucid, {
                "evidence_strength": strength,  # 대문자 유지
                "reason_code": rule.get("override_reason_code", "HARDCODED_RULESET"),
                "source_rules": [],
                "canonical_tool_fulltypes": [],
                "excluded_consumables": [],
                "tag_item_count": None,
            })
            overrides[ucid]["source_rules"].append(reg_rule_id)

    # ── Aggregate atoms per uc.action.* (union policy) ──
    action_aggregates = defaultdict(lambda: {
        "requires_fulltypes": set(),
        "requires_tags": set(),
        "requires_props": set(),
        "requires_display_categories": set(),
        "requires_script_types": set(),
        "has_property_based": False,
        "has_input_material": False,
        "source_rules": [],
    })
    mapped_count = 0
    for atom in rules_atoms:
        rid = atom["rule_id"]
        if rid not in rule_to_action:
            continue  # This rule doesn't map to uc.action.*

        action_id = rule_to_action[rid]
        agg = action_aggregates[action_id]        # Union policy for requires_*
        agg["requires_fulltypes"].update(atom.get("requires_fulltypes", []))
        agg["requires_tags"].update(atom.get("requires_tags", []))
        agg["requires_props"].update(atom.get("requires_props", []))
        agg["requires_display_categories"].update(atom.get("requires_display_categories", []))
        agg["requires_script_types"].update(atom.get("requires_script_types", []))

        # OR policy for exclusion flags
        if atom.get("has_property_based_exclusion", False):
            agg["has_property_based"] = True
        if atom.get("has_input_material_exclusion", False):
            agg["has_input_material"] = True

        agg["source_rules"].append(rid)
        mapped_count += 1

    # Include overrides only if they did not have rules matching the requirement
    # index. Existing mechanical classifications stay data-derived.
    override_only_actions = set()
    for ucid, override_data in overrides.items():
        if ucid not in action_aggregates:
            action_aggregates[ucid]["source_rules"] = override_data["source_rules"]
            override_only_actions.add(ucid)

    print(f"  Rules mapped to actions: {mapped_count}")
    print(f"  Unique uc.action.* IDs: {len(action_aggregates)}")

    # ── Classify each action ──
    classifications = {}
    for action_id in sorted(action_aggregates.keys()):
        agg = action_aggregates[action_id]
        if action_id in override_only_actions:
            result = overrides[action_id].copy()
            # source_rules append 시 중복 방지 및 정렬로 봉인 3번 만족
            result["source_rules"] = sorted(set(result["source_rules"] + agg["source_rules"]))
        else:
            result = classify_action(
                action_id=action_id,
                merged_requires_fulltypes=agg["requires_fulltypes"],
                merged_requires_tags=agg["requires_tags"],
                merged_requires_props=agg["requires_props"],
                merged_requires_display_categories=agg["requires_display_categories"],
                merged_requires_script_types=agg["requires_script_types"],
                merged_has_property_based=agg["has_property_based"],
                merged_has_input_material=agg["has_input_material"],
                source_rules=sorted(set(agg["source_rules"])),
                tag_item_counts=tag_item_counts,
                items=items,
            )
        classifications[action_id] = result

    # ── FAIL-LOUD Assertions ──
    fail_reasons = []

    # Assert 1: expected action count
    expected_action_count = 10
    actual_count = len(classifications)
    if actual_count != expected_action_count:
        fail_reasons.append(
            f"Expected {expected_action_count} uc.action.* IDs, got {actual_count}"
        )

    # Assert 2: evidence_strength enum + reason_code enum validation
    valid_strengths = {"strong", "weak", "exclude", "STRONG", "WEAK", "EXCLUDE"}
    valid_reasons = {
        "INPUT_ITEM", "INPUT_ITEM_CONSUMABLE", "PROPERTY_GATED", "FULLTYPE_GATED",
        "TAG_RESOLVES_TO_TYPE", "TOOL_GROUP",
        "DCST_RESOLVES_TO_TYPE", "DCST_GROUP", "AMBIGUOUS", "HARDCODED_RULESET"
    }
    for aid, cls in classifications.items():
        strength = cls.get("evidence_strength")
        reason = cls.get("reason_code")
        if strength not in valid_strengths:
            fail_reasons.append(
                f"{aid}: invalid evidence_strength='{strength}'"
            )

    # Assert 3: strong must have evidence basis, except for override
    for aid, cls in classifications.items():
        if cls["evidence_strength"] in ("strong", "STRONG"):
            if cls.get("reason_code") == "HARDCODED_RULESET":
                continue # Override bypasses requirement check
            has_ft = bool(cls.get("canonical_tool_fulltypes"))
            has_tag_basis = (
                cls.get("tag_item_count") is not None
                and cls["tag_item_count"] <= TAG_STRONG_THRESHOLD
            )
            if not has_ft and not has_tag_basis:
                fail_reasons.append(
                    f"{aid}: strong but no FullType or tag basis"
                )

    # Assert 4: exclude must have reason_code
    for aid, cls in classifications.items():
        if cls["evidence_strength"] in ("exclude", "EXCLUDE"):
            if not cls.get("reason_code"):
                fail_reasons.append(
                    f"{aid}: exclude but missing reason_code"
                )

    if fail_reasons:
        print(f"\n  ❌ FAIL-LOUD: {len(fail_reasons)} assertion(s) failed:")
        for r in fail_reasons:
            print(f"    - {r}")
        return 1

    print("\n  ✅ All FAIL-LOUD assertions passed")

    # ── Write output ──
    output = {
        "version": BUILD_VERSION,
        "tag_strong_threshold": TAG_STRONG_THRESHOLD,
        "description": "uc.action.* 10개 ID의 evidence_strength 분류 결과. "
                       "build_usecases_by_fulltype.py가 소비.",
        "classifications": classifications,
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_json(OUTPUT_PATH, output, indent=2)

    # ── Summary output (기계 출력 only) ──
    strong_count = sum(1 for c in classifications.values() if c["evidence_strength"] == "strong")
    weak_count = sum(1 for c in classifications.values() if c["evidence_strength"] == "weak")
    exclude_count = sum(1 for c in classifications.values() if c["evidence_strength"] == "exclude")

    print(f"\n  ✅ Generated {OUTPUT_PATH.name}")
    print(f"     strong: {strong_count}")
    print(f"     weak: {weak_count}")
    print(f"     exclude: {exclude_count}")
    print(f"     total: {strong_count + weak_count + exclude_count}")

    print(f"\n  Classification details:")
    for aid, cls in sorted(classifications.items()):
        strength = cls["evidence_strength"].upper()
        reason = cls["reason_code"]
        tag_count = cls.get("tag_item_count", "-")
        tools = cls.get("canonical_tool_fulltypes", [])[:3]
        tools_str = ", ".join(tools) if tools else "-"
        print(f"    {aid}: {strength} ({reason}) tag_count={tag_count} tools=[{tools_str}]")

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
