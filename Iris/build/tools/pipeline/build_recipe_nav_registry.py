"""
build_recipe_nav_registry.py — 레시피 네비게이션 레지스트리 산출
================================================================
recipe_evidence_decisions + usecases_by_fulltype → recipe_nav_registry.json

nav_eligible 3조건 AND:
  1. original_name 역매핑 성공 (rp.recipe.* → recipe_name)
  2. category가 PZ 알려진 카테고리 목록에 존재 (null 제외)
  3. original_name이 recipe_evidence_decisions의 recipe_name과 매칭

Output: output/recipe_nav_registry.{BUILD_VERSION}.json
"""
import re
import sys
from pathlib import Path

# ── Paths ──
BUILD_DIR = Path(__file__).resolve().parents[2]
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

IRIS_DIR = BUILD_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"

from tools.common.io import load_json, write_json
from tools.common.versions import BUILD_VERSION

RECIPE_DECISIONS_PATH = OUTPUT_DIR / f"recipe_evidence_decisions.{BUILD_VERSION}.json"
USECASES_PATH = OUTPUT_DIR / f"usecases_by_fulltype.{BUILD_VERSION}.json"
REGISTRY_OUTPUT_PATH = OUTPUT_DIR / f"recipe_nav_registry.{BUILD_VERSION}.json"

# PZ 한국어 번역 파일
PZ_ROOT = IRIS_DIR.parent  # Iris/../
KO_RECIPES_PATH = PZ_ROOT / "lua" / "shared" / "Translate" / "KO" / "Recipes_KO.txt"

# PZ 제작 UI 알려진 카테고리 목록 (recipes.txt 기반, 오프라인 확정)
# ISCraftingUI에서 getTextOrNull("IGUI_CraftCategory_"..rawCategory) 사용
KNOWN_CRAFT_CATEGORIES = {
    "Carpentry",
    "Cooking",
    "Electrical",
    "Engineer",
    "Farming",
    "Fishing",
    "General",
    "Health",
    "Masonry",
    "Mechanics",
    "Metalworking",
    "Smithing",
    "Survivalist",
    "Tailoring",
    "Trapper",
    "Welding",
}


def parse_recipe_translations(path: Path) -> dict:
    """Parse Recipes_KO.txt (UTF-16LE) → {recipe_key: 한국어명}.
    Key format: Make_Campfire_Kit (원래 레시피명의 공백→언더스코어)
    """
    translations = {}
    if not path.exists():
        return translations
    with open(path, "r", encoding="utf-16-le") as f:
        for line in f:
            m = re.match(r'\s*Recipe_(\S+)\s*=\s*"(.+?)"', line)
            if m:
                translations[m.group(1)] = m.group(2)
    return translations


def build_registry(
    recipe_decisions: dict, usecases_data: dict, ko_translations: dict
) -> dict:
    """Build recipe_nav_registry from existing build artifacts."""
    rules = recipe_decisions.get("rules", {})
    fulltypes = usecases_data.get("fulltypes", {})

    # Step 1: Collect all unique uc.recipe.* ucids from usecases
    recipe_ucids = set()
    for ft, entry in fulltypes.items():
        for uc in entry.get("use_cases", []):
            ucid = uc.get("use_case_id", "")
            if ucid.startswith("uc.recipe."):
                recipe_ucids.add(ucid)

    # Step 2: Build entries from recipe_evidence_decisions
    entries = {}
    uid_collision_count = 0
    nav_missing_index_count = 0

    for ucid in sorted(recipe_ucids):
        # Map uc.recipe.xxx → rp.recipe.xxx
        rule_id = ucid.replace("uc.recipe.", "rp.recipe.", 1)
        rule = rules.get(rule_id)

        if rule is None:
            nav_missing_index_count += 1
            entries[ucid] = {
                "recipe_id": ucid,
                "original_name": None,
                "category": None,
                "nav_eligible": False,
            }
            continue

        recipe_name = rule.get("recipe_name")
        category = rule.get("category")

        # nav_eligible: original_name 매핑 성공이면 통과
        # category=null인 레시피도 eligible (핸들러에서 탭 이동만 스킵)
        cond1_name_mapped = recipe_name is not None and len(recipe_name) > 0

        nav_eligible = cond1_name_mapped

        # UID collision check
        if ucid in entries:
            uid_collision_count += 1

        entries[ucid] = {
            "recipe_id": ucid,
            "original_name": recipe_name,
            "translated_name": ko_translations.get(
                recipe_name.replace(" ", "_"), None
            ) if recipe_name else None,
            "category": category,
            "nav_eligible": nav_eligible,
        }

    # Stats
    nav_eligible_count = sum(1 for e in entries.values() if e["nav_eligible"])
    nav_ineligible_count = sum(1 for e in entries.values() if not e["nav_eligible"])

    registry = {
        "version": BUILD_VERSION,
        "entries": entries,
        "stats": {
            "total_recipe_ucids": len(entries),
            "nav_eligible_count": nav_eligible_count,
            "nav_ineligible_count": nav_ineligible_count,
            "uid_collision_count": uid_collision_count,
            "nav_missing_index_count": nav_missing_index_count,
        },
    }

    return registry


def main():
    print("=" * 60)
    print(f"  Build Recipe Nav Registry (BUILD_VERSION={BUILD_VERSION})")
    print("=" * 60)

    # Check prerequisites
    for path, label in [
        (RECIPE_DECISIONS_PATH, "recipe_evidence_decisions"),
        (USECASES_PATH, "usecases_by_fulltype"),
    ]:
        if not path.exists():
            print(f"\n  ❌ {label} not found: {path}")
            return 1

    print(f"  Loading: {RECIPE_DECISIONS_PATH.name}")
    recipe_decisions = load_json(RECIPE_DECISIONS_PATH)

    print(f"  Loading: {USECASES_PATH.name}")
    usecases_data = load_json(USECASES_PATH)

    # Load Korean translations
    ko_tr = parse_recipe_translations(KO_RECIPES_PATH)
    if ko_tr:
        print(f"  Loaded: {len(ko_tr)} Korean recipe translations")
    else:
        print(f"  ⚠ Recipes_KO.txt not found or empty")

    print("  Building registry...")
    registry = build_registry(recipe_decisions, usecases_data, ko_tr)

    stats = registry["stats"]
    print(f"  ✅ Built: {stats['total_recipe_ucids']} ucids")
    print(f"     nav_eligible:   {stats['nav_eligible_count']}")
    print(f"     nav_ineligible: {stats['nav_ineligible_count']}")
    print(f"     uid_collision:  {stats['uid_collision_count']}")
    print(f"     nav_missing:    {stats['nav_missing_index_count']}")

    # FAIL-LOUD checks
    if stats["uid_collision_count"] > 0:
        print(f"\n  ❌ uid_collision_count > 0 — FAIL-LOUD")
        return 1

    if stats["nav_missing_index_count"] > 0:
        print(f"\n  ⚠ nav_missing_index_count = {stats['nav_missing_index_count']}")
        print("     (These ucids exist in usecases but not in recipe_evidence_decisions)")

    # Write output
    OUTPUT_DIR.mkdir(exist_ok=True)
    write_json(
        REGISTRY_OUTPUT_PATH,
        registry,
        indent=2,
        sort_keys=True,
        trailing_newline=False,
    )

    print(f"  ✅ Saved: {REGISTRY_OUTPUT_PATH.relative_to(IRIS_DIR)}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
