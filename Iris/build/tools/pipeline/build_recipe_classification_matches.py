"""
Recipe Classification Matches — Static Artifact Generator
==========================================================
분류 파이프라인을 1회 실행하여 recipe-predicate 규칙 매칭을
정적 산출물로 고정한다.

출력: output/recipe_classification_matches.v2.4.json
용도: build_usecases_by_fulltype.py가 이 파일을 로드하여
      recipe 소스를 use_case 버킷에 병합.

이 스크립트는 산출물 고정 전용. use_case 통합기에서 직접 호출하지 않는다.
"""
import sys
from pathlib import Path

# ── Paths ──
SCRIPT_DIR = Path(__file__).resolve().parent
BUILD_DIR = Path(__file__).resolve().parents[2]
for import_path in (BUILD_DIR, SCRIPT_DIR):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

IRIS_DIR = BUILD_DIR.parent
INPUT_DIR = IRIS_DIR / "input"
OUTPUT_DIR = IRIS_DIR / "output"

from tools.common.io import load_json, write_json
from tools.common.versions import BUILD_VERSION

OUTPUT_PATH = OUTPUT_DIR / f"recipe_classification_matches.{BUILD_VERSION}.json"

# ── Recipe-predicate rule IDs ──
# phase2_rules/rules/*.py에서 recipe_matches()를 사용하는 규칙만.
# 이 목록은 계약: 여기에 없는 규칙은 recipe 매칭으로 인정하지 않는다.
RECIPE_RULE_IDS = frozenset([
    # Tool rules — keep/require 역할
    "Tool.1-A.carpentry",
    "Tool.1-A.welding",
    "Tool.1-A.smithing",
    "Tool.1-D.recipe",
    "Tool.1-E.recipe",
    "Tool.1-G.recipe",
    # Resource rules — input 역할
    "Resource.4-A.carpentry",
    "Resource.4-A.welding",
    "Resource.4-A.smithing",
    "Resource.4-B.cooking",
    "Resource.4-C.health",
    "Resource.4-E.electrical",
    "Resource.4-E.engineer",
])


def main():
    print("=" * 60)
    print(f"  Recipe Classification Matches (BUILD_VERSION={BUILD_VERSION})")
    print("=" * 60)

    print("  [1/3] Loading evidence...")
    from phase1_extraction.evidence_collector import collect_all_evidence
    evidence = collect_all_evidence(INPUT_DIR)
    print(f"         Items: {evidence.total_items}")

    # Phase 1.5: Blocklist filtering (mirrors main.py)
    print("  [1.5] Blocklist filtering...")
    items_path = INPUT_DIR / "items_itemscript.json"
    raw_items_data = load_json(items_path)
    from phase2_rules.blocklist import filter_blocklisted
    evidence, blocked_count, _ = filter_blocklisted(evidence, raw_items_data)
    print(f"         After blocklist: {evidence.total_items}")

    print("  [2/3] Executing classification rules...")
    from phase2_rules.rule_executor import execute_rules, get_all_rules
    from phase3_output.manual_overrides import get_manual_overrides

    rules = get_all_rules()
    manual_overrides = get_manual_overrides()
    result = execute_rules(evidence, rules, manual_overrides=manual_overrides)
    print(f"         Classified: {result.total_classified}")

    # ── Step 2: Extract recipe-predicate matches ──
    print("  [3/3] Extracting recipe-predicate matches...")
    matches = {}

    for ft in sorted(result.items.keys()):
        cr = result.items[ft]
        recipe_hits = sorted(
            rid for rid in cr.matched_rules if rid in RECIPE_RULE_IDS
        )
        if recipe_hits:
            matches[ft] = recipe_hits

    # ── Step 3: Write canonical output ──
    output = {
        "version": BUILD_VERSION,
        "recipe_rule_ids": sorted(RECIPE_RULE_IDS),
        "matches": matches,  # already sorted by key (sorted iteration above)
    }

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_json(OUTPUT_PATH, output, indent=2, trailing_newline=False)

    print(f"\n  ✅ Generated: {OUTPUT_PATH.name}")
    print(f"     Recipe rule IDs: {len(RECIPE_RULE_IDS)}")
    print(f"     Matched fulltypes: {len(matches)}")
    total_hits = sum(len(v) for v in matches.values())
    print(f"     Total (fulltype, rule_id) pairs: {total_hits}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
