"""
Recipe Require Fields Parser v2.5
=================================
scripts/recipes.txt, farming.txt → recipe_require_fields.v2.5.json

recipes.txt/farming.txt/camping.txt에서 require-eligible 필드 추출:
  - SkillRequired → perk atom
  - NearItem → near_item atom
  - NeedToBeLearn → flag atom
  - Result → output_fulltype

봉인 규칙:
  R1: module 미확정 → diagnostics, output_fulltype 생성 금지
  R2: Result 파싱 실패 → diagnostics.unparsed_result, silently drop 금지
  R3: recipe_id는 slugify + resolve_slug_collisions로 직접 결정
"""
import re
import hashlib
import sys
from pathlib import Path
from collections import defaultdict

# ── Paths ──
BUILD_DIR = Path(__file__).resolve().parents[2]
if str(BUILD_DIR) not in sys.path:
    sys.path.insert(0, str(BUILD_DIR))

IRIS_DIR = BUILD_DIR.parent
SCRIPTS_DIR = IRIS_DIR.parent / "scripts"
OUTPUT_DIR = IRIS_DIR / "output"

from tools.common.io import write_json
from tools.common.versions import REQUIRE_FIELDS_VERSION, versioned_name

BUILD_VERSION = REQUIRE_FIELDS_VERSION


# ── Recipe source files (순서 고정 = 결정성) ──
RECIPE_SOURCE_FILES = [
    "recipes.txt",
    "farming.txt",
    "camping.txt",
]


# ══════════════════════════════════════════════════════════════════════════
#  UTILITY (recipe_evidence_pipeline.py에서 재사용하는 규칙 복제)
# ══════════════════════════════════════════════════════════════════════════

def slugify(name: str) -> str:
    """
    Recipe name → deterministic slug.
    'Make Campfire Kit' → 'make_campfire_kit'
    """
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    return s


def resolve_slug_collisions(slug_to_names: dict[str, list[str]]) -> dict[str, str]:
    """
    충돌하는 recipe_name들을 _<sha1_4자> 접미어로 결정적 분리.
    Returns: { unique_key: final_recipe_id }
    """
    name_to_id = {}
    for slug, names in slug_to_names.items():
        if len(names) == 1:
            name_to_id[names[0]] = slug
        else:
            for name in sorted(names):
                h = hashlib.sha1(name.encode("utf-8")).hexdigest()[:4]
                name_to_id[name] = f"{slug}_{h}"
    return name_to_id


# ══════════════════════════════════════════════════════════════════════════
#  PARSER
# ══════════════════════════════════════════════════════════════════════════

# ── Regex patterns (정규화 고정) ──
RE_MODULE = re.compile(r"^\s*module\s+(\w+)")
RE_RECIPE_START = re.compile(r"^\s*recipe\s+(.+)")
RE_RESULT = re.compile(r"^\s*Result\s*:\s*(\w+)(?:\s*=\s*(\d+))?\s*,?\s*$")
RE_SKILL = re.compile(r"^\s*SkillRequired\s*:\s*(.+?)\s*,?\s*$")
RE_NEAR_ITEM = re.compile(r"^\s*NearItem\s*:\s*(\w+)\s*,?\s*$")
RE_NEED_LEARN = re.compile(r"^\s*NeedToBeLearn\s*:\s*true\s*,?\s*$")
RE_BLOCK_OPEN = re.compile(r"\{")
RE_BLOCK_CLOSE = re.compile(r"\}")
RE_COMMENT_START = re.compile(r"/\*")
RE_COMMENT_END = re.compile(r"\*/")
RE_LINE_COMMENT = re.compile(r"^\s*//")

# ── SkillRequired value parser ──
# Patterns: "Blacksmith=2" or "Woodwork=1;Trapping=2;" (semicolon-separated)
RE_SKILL_PAIR = re.compile(r"(\w+)\s*=\s*(\d+)")


def parse_skill_required(raw: str) -> tuple[list[dict], list[str]]:
    """
    SkillRequired value → list of perk atoms.
    Returns: (atoms, errors)
    """
    atoms = []
    errors = []
    pairs = RE_SKILL_PAIR.findall(raw)
    if not pairs:
        errors.append(f"no skill pairs found in: {raw!r}")
        return atoms, errors

    for skill_name, level_str in pairs:
        try:
            level = int(level_str)
        except ValueError:
            errors.append(f"non-integer level: {skill_name}={level_str!r}")
            continue
        atoms.append({
            "kind": "perk",
            "key": skill_name,
            "op": ">=",
            "value": level,
        })
    return atoms, errors


def parse_recipe_file(filepath: Path) -> dict:
    """
    단일 레시피 파일 파싱.

    Returns: {
        "module": str or None,
        "recipes": [ { recipe_name, line_start, result, result_count, requires, ... } ],
        "diagnostics": { unparsed_result, multi_result, unparsable_skill, module_unresolved }
    }
    """
    lines = filepath.read_text("utf-8").splitlines()
    filename = filepath.name

    current_module = None
    recipes = []
    diagnostics = {
        "unparsed_result": [],
        "multi_result": [],
        "unparsable_skill": [],
        "module_unresolved": [],
    }

    # ── State machine ──
    in_comment = False
    in_recipe = False
    brace_depth = 0
    recipe_name = ""
    recipe_line_start = 0
    recipe_results = []     # (short_name, count)
    recipe_requires = []
    recipe_errors = []

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()

        # ── Block comment tracking ──
        if in_comment:
            if RE_COMMENT_END.search(line):
                in_comment = False
            continue

        if RE_COMMENT_START.search(line) and not RE_COMMENT_END.search(line):
            in_comment = True
            continue

        # Skip single-line comments
        if RE_LINE_COMMENT.match(stripped):
            continue

        # Handle inline /* ... */ comments (single line)
        if RE_COMMENT_START.search(line) and RE_COMMENT_END.search(line):
            # Remove the comment portion for processing
            line = re.sub(r"/\*.*?\*/", "", line)
            stripped = line.strip()

        # ── Module declaration ──
        m = RE_MODULE.match(stripped)
        if m:
            current_module = m.group(1)
            continue

        # ── Recipe start ──
        m = RE_RECIPE_START.match(stripped)
        if m and not in_recipe:
            recipe_name = m.group(1).strip()
            # Remove trailing { if on same line
            if recipe_name.endswith("{"):
                recipe_name = recipe_name[:-1].strip()
            recipe_line_start = line_num
            recipe_results = []
            recipe_requires = []
            recipe_errors = []
            # Don't set in_recipe yet — wait for opening brace
            # But if brace is on same line:
            if "{" in line:
                in_recipe = True
                brace_depth = 1
            continue

        # ── Detect opening brace (recipe block start on next line) ──
        if recipe_name and not in_recipe and "{" in line:
            in_recipe = True
            brace_depth = 1
            continue

        if not in_recipe:
            continue

        # ── Track brace depth ──
        open_count = line.count("{")
        close_count = line.count("}")
        brace_depth += open_count - close_count

        # ── Parse fields inside recipe block ──
        # Result
        m = RE_RESULT.match(stripped)
        if m:
            short_name = m.group(1)
            count = int(m.group(2)) if m.group(2) else 1
            recipe_results.append((short_name, count))

        # SkillRequired
        m = RE_SKILL.match(stripped)
        if m:
            raw_skill = m.group(1)
            atoms, errors = parse_skill_required(raw_skill)
            recipe_requires.extend(atoms)
            for err in errors:
                diagnostics["unparsable_skill"].append({
                    "file": filename,
                    "line": line_num,
                    "recipe_name": recipe_name,
                    "error": err,
                })

        # NearItem
        m = RE_NEAR_ITEM.match(stripped)
        if m:
            recipe_requires.append({
                "kind": "near_item",
                "key": m.group(1),
            })

        # NeedToBeLearn
        m = RE_NEED_LEARN.match(stripped)
        if m:
            recipe_requires.append({
                "kind": "flag",
                "key": "NeedToBeLearn",
            })

        # ── Recipe block end ──
        if brace_depth <= 0:
            in_recipe = False

            # ── Process collected data ──
            # R1: module 미확정 → diagnostics, output_fulltype 생성 금지
            if current_module is None:
                diagnostics["module_unresolved"].append({
                    "file": filename,
                    "line": recipe_line_start,
                    "recipe_name": recipe_name,
                    "reason": "no_module_declaration",
                })
                recipe_name = ""
                continue

            # R2: Result 파싱
            output_fulltype = None
            if len(recipe_results) == 0:
                diagnostics["unparsed_result"].append({
                    "file": filename,
                    "line": recipe_line_start,
                    "recipe_name": recipe_name,
                    "reason": "no_result_line",
                })
            elif len(recipe_results) > 1:
                # multi_result 격리: 첫 번째만 사용하되 진단 기록
                diagnostics["multi_result"].append({
                    "file": filename,
                    "line": recipe_line_start,
                    "recipe_name": recipe_name,
                    "results": [f"{n}={c}" for n, c in recipe_results],
                })
                # multi_result는 PASS에 넣지 않음 → output_fulltype = None
            else:
                short_name = recipe_results[0][0]
                output_fulltype = f"{current_module}.{short_name}"

            # Only record recipes that have require-eligible fields OR output
            if recipe_requires or output_fulltype:
                recipes.append({
                    "recipe_name": recipe_name,
                    "file": filename,
                    "line_start": recipe_line_start,
                    "output_fulltype": output_fulltype,
                    "requires": recipe_requires,
                })

            # Reset
            recipe_name = ""

    return {
        "module": current_module,
        "recipes": recipes,
        "diagnostics": diagnostics,
    }


# ══════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print(f"  Recipe Require Fields Parser (BUILD_VERSION={BUILD_VERSION})")
    print("=" * 60)

    # ── Parse all source files ──
    all_recipes = []          # list of raw recipe dicts
    all_diagnostics = {
        "unparsed_result": [],
        "multi_result": [],
        "unparsable_skill": [],
        "module_unresolved": [],
    }

    for fname in RECIPE_SOURCE_FILES:
        path = SCRIPTS_DIR / fname
        if not path.exists():
            print(f"\n  ⚠️ Source file not found: {path}")
            continue

        print(f"\n  Parsing {fname}...")
        result = parse_recipe_file(path)
        print(f"    module: {result['module']}")
        print(f"    recipes found: {len(result['recipes'])}")

        all_recipes.extend(result["recipes"])
        for key in all_diagnostics:
            all_diagnostics[key].extend(result["diagnostics"][key])

    print(f"\n  Total raw recipes: {len(all_recipes)}")

    # ── Filter: only recipes with require-eligible fields ──
    # (recipes without requires AND without output are already filtered in parser)
    require_recipes = [r for r in all_recipes if r["requires"]]
    print(f"  Recipes with require fields: {len(require_recipes)}")

    # ── R3: Generate recipe_id using slugify + collision resolution ──
    slug_to_names = defaultdict(list)
    for r in all_recipes:
        unique_key = f"{r['recipe_name']}|{r['file']}"
        slug = slugify(r["recipe_name"])
        slug_to_names[slug].append(unique_key)

    name_to_id = resolve_slug_collisions(slug_to_names)

    # ── Build output ──
    recipes_output = {}
    for r in all_recipes:
        unique_key = f"{r['recipe_name']}|{r['file']}"
        recipe_id = name_to_id[unique_key]

        entry = {
            "recipe_id": recipe_id,
            "recipe_name": r["recipe_name"],
            "output_fulltype": r["output_fulltype"],
            "source": {
                "file": r["file"],
                "line_start": r["line_start"],
            },
        }

        # Only include requires if non-empty (R4 compliance)
        if r["requires"]:
            # Deterministic sort: kind → key → op → value
            sorted_requires = sorted(
                r["requires"],
                key=lambda a: (a["kind"], a["key"], a.get("op", ""), a.get("value", 0))
            )
            entry["requires"] = sorted_requires

        recipes_output[recipe_id] = entry

    # Sort by recipe_id for determinism
    sorted_recipes = dict(sorted(recipes_output.items()))

    # ── Count atoms by kind ──
    atom_counts = defaultdict(int)
    recipes_with_requires = 0
    for entry in sorted_recipes.values():
        reqs = entry.get("requires", [])
        if reqs:
            recipes_with_requires += 1
        for atom in reqs:
            atom_counts[atom["kind"]] += 1

    # ── Sort diagnostics for determinism ──
    for key in all_diagnostics:
        all_diagnostics[key].sort(
            key=lambda d: (d.get("file", ""), d.get("line", 0), d.get("recipe_name", ""))
        )

    # ── Assemble final output ──
    output = {
        "version": BUILD_VERSION,
        "recipe_count": len(sorted_recipes),
        "parsed_require_count": recipes_with_requires,
        "atom_counts": dict(sorted(atom_counts.items())),
        "recipes": sorted_recipes,
        "diagnostics": all_diagnostics,
    }

    # ── Save ──
    out_path = OUTPUT_DIR / versioned_name("recipe_require_fields", BUILD_VERSION)
    write_json(out_path, output, indent=2, trailing_newline=False)

    print(f"\n  Output: {out_path.name}")
    print(f"    recipe_count:         {output['recipe_count']}")
    print(f"    parsed_require_count: {output['parsed_require_count']}")
    print(f"    atom_counts:          {dict(atom_counts)}")
    print(f"    diagnostics:")
    for key, items in all_diagnostics.items():
        print(f"      {key}: {len(items)}")

    # ══════════════════════════════════════════════════════════════════
    #  Self-validation asserts
    # ══════════════════════════════════════════════════════════════════
    print(f"\n{'=' * 60}")
    print("  Self-validation")
    print("=" * 60)

    errors = []

    # 1. recipe_count > 0
    if output["recipe_count"] == 0:
        errors.append("recipe_count is 0")

    # 2. parsed_require_count > 0
    if output["parsed_require_count"] == 0:
        errors.append("parsed_require_count is 0 (no require fields extracted)")

    # 3. All atom kinds must be in allowlist
    ALLOWED_KINDS = {"perk", "near_item", "flag"}
    for rid, entry in sorted_recipes.items():
        for atom in entry.get("requires", []):
            if atom["kind"] not in ALLOWED_KINDS:
                errors.append(f"{rid}: kind={atom['kind']} not in allowlist")

    # 4. perk atoms: op must be >=, value must be int, key non-empty
    for rid, entry in sorted_recipes.items():
        for atom in entry.get("requires", []):
            if atom["kind"] == "perk":
                if atom.get("op") != ">=":
                    errors.append(f"{rid}: perk op={atom.get('op')!r} (expected >=)")
                if not isinstance(atom.get("value"), int):
                    errors.append(f"{rid}: perk value={atom.get('value')!r} not int")
                if not atom.get("key"):
                    errors.append(f"{rid}: perk key is empty")

    # 5. output_fulltype format: <Module>.<Name> (dot required)
    for rid, entry in sorted_recipes.items():
        ft = entry.get("output_fulltype")
        if ft and "." not in ft:
            errors.append(f"{rid}: output_fulltype={ft!r} missing dot")

    # 6. Each atom kind has > 0 entries
    for kind in ["perk", "near_item", "flag"]:
        if atom_counts.get(kind, 0) == 0:
            errors.append(f"atom kind '{kind}' has 0 entries")

    if errors:
        print(f"\n  ❌ FAIL: {len(errors)} validation errors:")
        for e in errors[:20]:
            print(f"    - {e}")
        return 1
    else:
        print(f"\n  ✅ All validations passed")
        print(f"    - recipe_count: {output['recipe_count']}")
        print(f"    - parsed_require_count: {output['parsed_require_count']}")
        print(f"    - atom kinds all populated: {dict(atom_counts)}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
