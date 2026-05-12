"""
Action Requirement Index Builder
================================
rightclick_source_index.v2.4.json의 활성 rule에서
메뉴 생성 조건의 원자(Atom)를 추출하여
action_requirement_index.v2.4.json을 생성.

입력: input/rightclick_source_index.v2.4.json
출력: output/action_requirement_index.v2.4.json

Usage:
    python build/tools/pipeline/build_action_requirement_index.py
"""
import sys
from pathlib import Path

# ── Paths ──
SCRIPT_DIR = Path(__file__).resolve().parent
BUILD_DIR = Path(__file__).resolve().parents[2]
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

IRIS_DIR = BUILD_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"

from tools.common.io import load_json, write_json
from tools.common.versions import BUILD_VERSION

SOURCE_INDEX_PATH = IRIS_DIR / "input" / f"rightclick_source_index.{BUILD_VERSION}.json"
OUTPUT_PATH = OUTPUT_DIR / f"action_requirement_index.{BUILD_VERSION}.json"


def normalize_fulltype(value: str) -> str:
    """
    FullType 정규화 봉인 규칙:
    - value에 '.'이 포함 → 그대로 FullType 취급 (예: Base.TinOpener)
    - '.'이 없으면 → Base. prefix 부여 (예: Needle → Base.Needle)
    """
    if "." in value:
        return value
    return f"Base.{value}"


def extract_rule_atoms(rule: dict) -> dict:
    """단일 rule에서 메뉴 생성 조건 원자를 추출."""
    rule_id = rule["rule_id"]
    extract = rule.get("extract", {})
    matchers = extract.get("matchers", [])
    matcher_logic = extract.get("matcher_logic", "OR")
    exclusions = rule.get("exclusions", {})

    requires_fulltypes = []
    requires_tags = []
    requires_props = []
    requires_display_categories = []
    requires_script_types = []

    for m in matchers:
        mt = m.get("match_type", "")
        val = m.get("value", "")

        if mt == "type":
            requires_fulltypes.append(normalize_fulltype(val))
        elif mt == "tag":
            requires_tags.append(val)
        elif mt == "property":
            requires_props.append(val)
        elif mt == "display_category":
            requires_display_categories.append(val)
        elif mt == "script_type":
            requires_script_types.append(val)

    # Exclusion 플래그
    has_property_based = exclusions.get("property_based", False) is True
    has_input_material = exclusions.get("input_material", False) is True

    # Source anchor ref (첫 번째 anchor의 ref)
    anchor_ref = ""
    if "anchors" in rule:
        anchors = rule["anchors"]
        if anchors:
            anchor_ref = anchors[0].get("ref", "")
    elif "anchor" in rule:
        anchor_ref = rule["anchor"].get("ref", "")

    return {
        "rule_id": rule_id,
        "requires_fulltypes": sorted(set(requires_fulltypes)),
        "requires_tags": sorted(set(requires_tags)),
        "requires_props": sorted(set(requires_props)),
        "requires_display_categories": sorted(set(requires_display_categories)),
        "requires_script_types": sorted(set(requires_script_types)),
        "matcher_logic": matcher_logic,
        "has_property_based_exclusion": has_property_based,
        "has_input_material_exclusion": has_input_material,
        "matchers_raw": matchers,
        "source_anchor_ref": anchor_ref,
    }


def main():
    print("=" * 60)
    print(f"  Action Requirement Index Builder (BUILD_VERSION={BUILD_VERSION})")
    print("=" * 60)

    # ── Load source index ──
    if not SOURCE_INDEX_PATH.exists():
        print(f"\n  ❌ Source index not found: {SOURCE_INDEX_PATH}")
        return 1

    source_index = load_json(SOURCE_INDEX_PATH)

    rules = source_index.get("rules", [])
    print(f"  Total rules in source index: {len(rules)}")

    # ── Extract atoms from active rules only ──
    atoms = []
    skipped_disabled = 0
    for rule in rules:
        if rule.get("disabled", False):
            skipped_disabled += 1
            continue
        atom = extract_rule_atoms(rule)
        atoms.append(atom)

    print(f"  Active rules processed: {len(atoms)}")
    print(f"  Disabled rules skipped: {skipped_disabled}")

    # ── FAIL-LOUD: at least 1 active rule ──
    if not atoms:
        print("\n  ❌ FAIL-LOUD: No active rules found in source index")
        return 1

    # ── Write output ──
    output = {
        "version": BUILD_VERSION,
        "description": "rightclick_source_index에서 추출한 메뉴 생성 조건 원자 (Atom). "
                       "classify_action_evidence.py의 입력으로 사용.",
        "rules": atoms,
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_json(OUTPUT_PATH, output, indent=2)

    # ── Summary ──
    ft_rules = sum(1 for a in atoms if a["requires_fulltypes"])
    tag_rules = sum(1 for a in atoms if a["requires_tags"])
    prop_rules = sum(1 for a in atoms if a["requires_props"])
    pb_rules = sum(1 for a in atoms if a["has_property_based_exclusion"])
    im_rules = sum(1 for a in atoms if a["has_input_material_exclusion"])

    print(f"\n  ✅ Generated {OUTPUT_PATH.name}")
    print(f"     Rules with requires_fulltypes: {ft_rules}")
    print(f"     Rules with requires_tags: {tag_rules}")
    print(f"     Rules with requires_props: {prop_rules}")
    print(f"     Rules with property_based exclusion: {pb_rules}")
    print(f"     Rules with input_material exclusion: {im_rules}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
