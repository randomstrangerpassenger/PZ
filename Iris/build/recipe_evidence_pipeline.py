"""
Recipe Evidence Pipeline v2.4
==============================
R1: Recipe Index 생성          → recipe_index.v2.4.json
R2: recipes_by_fulltype 생성   → recipes_by_fulltype.v2.4.json
R3: Recipe Evidence Decisions  → recipe_evidence_decisions.v2.4.json
R4: Recipe Review Queue        → recipe_review_queue.v2.4.json
R5: Dynamic Expr Catalog       → dynamic_expr_catalog.v2.4.json

입력: recipes_index_full.json, items_itemscript.json
설계: RightClick evidence pipeline과 대칭적 rule_id 중심 구조.
      source_type="recipe_evidence" (classification_recipe 폐기).

Usage:
    python build/recipe_evidence_pipeline.py
"""
import json
import hashlib
import re
import sys
from pathlib import Path
from collections import defaultdict, OrderedDict

# ── Paths ──
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

IRIS_DIR = SCRIPT_DIR.parent
INPUT_DIR = IRIS_DIR / "input"
OUTPUT_DIR = IRIS_DIR / "output"

from tools.common.io import load_json
from tools.common.stage_runner import StageRunner
from tools.common.evidence_skeleton import pipeline_banner, require_inputs
from tools.common.versions import BUILD_VERSION, REQUIRE_FIELDS_VERSION, versioned_name

RECIPES_PATH = INPUT_DIR / "recipes_index_full.json"
ITEMS_PATH = INPUT_DIR / "items_itemscript.json"

RECIPE_INDEX_PATH = OUTPUT_DIR / f"recipe_index.{BUILD_VERSION}.json"
RECIPES_BY_FT_PATH = OUTPUT_DIR / f"recipes_by_fulltype.{BUILD_VERSION}.json"
DECISIONS_PATH = OUTPUT_DIR / f"recipe_evidence_decisions.{BUILD_VERSION}.json"
REVIEW_QUEUE_PATH = OUTPUT_DIR / f"recipe_review_queue.{BUILD_VERSION}.json"
DYNAMIC_CATALOG_PATH = OUTPUT_DIR / f"dynamic_expr_catalog.{BUILD_VERSION}.json"

# ── REVIEW reason enum ──
REASON_UNRESOLVED_TOKEN = "unresolved_token"
REASON_PARSER_UNSUPPORTED = "parser_unsupported"
REASON_UNKNOWN_FULLTYPE_REF = "unknown_fulltype_ref"
REASON_UNKNOWN_TAG_REF = "unknown_tag_ref"
REASON_DYNAMIC_RECIPE_EXPR = "dynamic_recipe_expr"
REASON_DYNAMIC_EXPR_TAG_MATCH_EMPTY = "dynamic_recipe_expr.tag_match_empty"
REASON_DYNAMIC_EXPR_GROUP_DEF_DYNAMIC = "dynamic_recipe_expr.group_def_dynamic"
REASON_MISSING_OUTPUT = "missing_output"

VALID_REVIEW_REASONS = frozenset([
    REASON_UNRESOLVED_TOKEN,
    REASON_PARSER_UNSUPPORTED,
    REASON_UNKNOWN_FULLTYPE_REF,
    REASON_UNKNOWN_TAG_REF,
    REASON_DYNAMIC_RECIPE_EXPR,
    REASON_DYNAMIC_EXPR_TAG_MATCH_EMPTY,
    REASON_DYNAMIC_EXPR_GROUP_DEF_DYNAMIC,
    REASON_MISSING_OUTPUT,
])

# ── group_def_dynamic 정책 동결 ──
# PERMANENT_REVIEW: 정적 해석 불가로 영구 REVIEW 고정, 해결 시도하지 않음
# ALLOW_STATIC_SNAPSHOT: 재구성 가능한 테이블만 스냅샷 경로로 이동 (미래 확장용)
GROUP_DEF_DYNAMIC_POLICY = "PERMANENT_REVIEW"

# 5건 각각의 의존성 정보 (정적 스캔으로 확인 완료)
UNRESOLVED_GROUP_DEPS: dict[str, dict] = {
    "CraftSheetRope": {
        "depends_on": ["FabricType", "ClothingRecipesDefinitions"],
        "rationale": "depends_on_unreconstructable_runtime_table",
        "source_ref": "recipecode.lua::Recipe.GetItemTypes.CraftSheetRope",
    },
    "RipClothing_Cotton": {
        "depends_on": ["FabricType", "ClothingRecipesDefinitions"],
        "rationale": "depends_on_unreconstructable_runtime_table",
        "source_ref": "recipecode.lua::Recipe.GetItemTypes.RipClothing_Cotton",
    },
    "RipClothing_Denim": {
        "depends_on": ["FabricType", "ClothingRecipesDefinitions"],
        "rationale": "depends_on_unreconstructable_runtime_table",
        "source_ref": "recipecode.lua::Recipe.GetItemTypes.RipClothing_Denim",
    },
    "RipClothing_Leather": {
        "depends_on": ["FabricType", "ClothingRecipesDefinitions"],
        "rationale": "depends_on_unreconstructable_runtime_table",
        "source_ref": "recipecode.lua::Recipe.GetItemTypes.RipClothing_Leather",
    },
    "RipSheets": {
        "depends_on": ["FabricType", "ClothingRecipesDefinitions"],
        "rationale": "depends_on_unreconstructable_runtime_table",
        "source_ref": "recipecode.lua::Recipe.GetItemTypes.RipSheets",
    },
}

DYNAMIC_GROUP_POLICY_PATH = OUTPUT_DIR / f"dynamic_group_policy.{BUILD_VERSION}.json"
REQUIREMENTS_BY_FT_PATH = OUTPUT_DIR / f"requirements_by_fulltype.{BUILD_VERSION}.json"

# ── Require channel (v2.5) ──
REQUIRE_ATOM_KINDS = frozenset(["perk", "near_item", "flag"])
REQUIRE_FIELDS_PATH = OUTPUT_DIR / versioned_name("recipe_require_fields", REQUIRE_FIELDS_VERSION)

# ── PASS-eligible roles (행동 증거) ──
# keep/require는 조건/도구이지 행동 참여가 아님 → NO
PASS_ROLES = frozenset(["input"])
# Note: "output" would also be PASS, but recipes_index_full.json에는 output 역할 없음.
# 향후 output이 추가되면 여기에 포함.


# ══════════════════════════════════════════════════════════════════════════
#  TAG INDEX & GROUP RESOLUTION
# ══════════════════════════════════════════════════════════════════════════

# tag_index canonical 규칙: strip, drop_empty, case_preserve, sort_unique
TAG_INDEX_CANONICAL = "strip, drop_empty, case_preserve, sort_unique"

# ── Round 2: Lua-sourced alias 매핑 ──
# recipecode.lua에서 getItemsTag("다른태그")로 호출하는 그룹
# group_name -> 실제 tag_index에서 조회할 alias tag
LUA_TAG_ALIAS: dict[str, str] = {
    "CraftLogStack": "Rope",
    "Rice": "RiceRecipe",
    "DismantleCamera": "Camera",
}

# ── Round 2: Static filter 평가기 ──
# recipecode.lua에서 정적 필드 조건으로 필터링하는 그룹
# Canonical: type_eq=exact match(대소문자 구분),
#            name_contains=in 연산자(대소문자 구분, trim 없음, fulltype의 Base. 이후 = name)
LUA_STATIC_FILTERS: dict[str, dict] = {
    "DismantleDigitalWatch": {
        "type_eq": "AlarmClockClothing",
        "name_contains": "Digital",
    },
}


def build_tag_index(items_data: dict) -> dict[str, list[str]]:
    """
    items_itemscript.json → {tag_name: sorted([fulltype, ...])}

    Canonical 규칙:
    - Tags 필드를 ';'으로 split
    - 각 태그를 strip(), 빈 문자열 drop
    - 대소문자 원문 유지 (case_preserve)
    - fulltype 목록은 sort + unique
    """
    tag_to_fts: dict[str, set[str]] = {}

    for fulltype, item in items_data.items():
        tags_str = item.get("Tags", "")
        if not tags_str:
            continue
        for tag in tags_str.split(";"):
            tag = tag.strip()
            if not tag:
                continue
            tag_to_fts.setdefault(tag, set()).add(fulltype)

    # sort unique
    return {tag: sorted(fts) for tag, fts in sorted(tag_to_fts.items())}


def _evaluate_static_filter(
    filter_def: dict, items_data: dict
) -> list[str]:
    """
    Static filter 정의를 items_itemscript.json에 대해 평가.
    지원 조건: type_eq (exact), name_contains (substring of fulltype suffix).
    반환: sorted fulltype 리스트
    """
    type_eq = filter_def.get("type_eq")
    name_contains = filter_def.get("name_contains")

    matched = []
    for fulltype, item in items_data.items():
        # type_eq: exact match (case-sensitive)
        if type_eq and item.get("Type", "") != type_eq:
            continue
        # name_contains: substring of fulltype suffix (after "Base.")
        if name_contains:
            # Extract name from fulltype: "Base.WristWatch_Left_DigitalBlack" -> "WristWatch_Left_DigitalBlack"
            name_part = fulltype.split(".", 1)[1] if "." in fulltype else fulltype
            if name_contains not in name_part:
                continue
        matched.append(fulltype)

    return sorted(matched)


def resolve_get_item_types_groups(
    group_names: list[str],
    tag_index: dict[str, list[str]],
    items_data: dict,
) -> tuple[dict[str, dict], list[str]]:
    """
    GetItemTypes 그룹을 3단계로 해석.

    1단계: 그룹명이 tag_index에 직접 존재 (tag_match)
    2단계: LUA_TAG_ALIAS에서 alias tag로 tag_index 재조회 (lua_tag_alias)
    3단계: LUA_STATIC_FILTERS로 items_data 필드 필터링 (static_filter)

    해석된 그룹은 evidence decision을 생성하지 않고,
    단지 dynamic_recipe_expr REVIEW 항목에서 제외(resolved)된다.

    Returns: (resolved_groups, unresolved_group_names)
      resolved_groups: {group: {"method": str, "fulltypes": [str], ...}}
      unresolved_group_names: [str]
    """
    resolved_groups: dict[str, dict] = {}
    unresolved_groups: list[str] = []

    for group_name in sorted(group_names):
        # Stage 1: Direct tag match
        if group_name in tag_index:
            resolved_groups[group_name] = {
                "method": "tag_match",
                "fulltypes": tag_index[group_name],
            }
            continue

        # Stage 2: Lua tag alias
        if group_name in LUA_TAG_ALIAS:
            alias_tag = LUA_TAG_ALIAS[group_name]
            if alias_tag not in tag_index:
                raise ValueError(
                    f"FAIL-LOUD: LUA_TAG_ALIAS['{group_name}'] = '{alias_tag}' "
                    f"not found in tag_index. Data inconsistency."
                )
            resolved_groups[group_name] = {
                "method": "lua_tag_alias",
                "alias_tag": alias_tag,
                "fulltypes": tag_index[alias_tag],
            }
            continue

        # Stage 3: Static filter
        if group_name in LUA_STATIC_FILTERS:
            filter_def = LUA_STATIC_FILTERS[group_name]
            matched = _evaluate_static_filter(filter_def, items_data)
            resolved_groups[group_name] = {
                "method": "static_filter",
                "filter": filter_def,
                "fulltypes": matched,
            }
            continue

        # Unresolved
        unresolved_groups.append(group_name)

    return resolved_groups, unresolved_groups


def build_dynamic_expr_catalog(
    resolved_groups: dict[str, dict],
    unresolved_groups: list[str],
) -> dict:
    """
    해석 결과를 정적 산출물로 기록.
    감사 추적 + 해석 근거 보존 목적.
    """
    groups = {}

    for group_name in sorted(resolved_groups.keys()):
        info = resolved_groups[group_name]
        entry = {
            "status": "resolved",
            "method": info["method"],
            "matched_fulltypes": info["fulltypes"],
        }
        if "alias_tag" in info:
            entry["alias_tag"] = info["alias_tag"]
        if "filter" in info:
            entry["filter"] = info["filter"]
        groups[group_name] = entry

    for group_name in sorted(unresolved_groups):
        entry = {
            "status": "unresolved",
            "reason": "group_def_dynamic",
            "policy": GROUP_DEF_DYNAMIC_POLICY,
        }
        # 의존성 정보가 등록되어 있으면 주입
        if group_name in UNRESOLVED_GROUP_DEPS:
            deps = UNRESOLVED_GROUP_DEPS[group_name]
            entry["depends_on"] = deps["depends_on"]
            entry["rationale"] = deps["rationale"]
            entry["source_ref"] = deps["source_ref"]
        groups[group_name] = entry

    return {
        "version": BUILD_VERSION,
        "group_def_dynamic_policy": GROUP_DEF_DYNAMIC_POLICY,
        "total_groups": len(groups),
        "resolved_count": len(resolved_groups),
        "unresolved_count": len(unresolved_groups),
        "tag_index_canonical": TAG_INDEX_CANONICAL,
        "groups": groups,
    }


# ══════════════════════════════════════════════════════════════════════════
#  UTILITY
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
    Returns: { recipe_name: final_recipe_id }
    충돌은 허용되며 규칙에 따라 결정적으로 분리된다.
    """
    name_to_id = {}

    for slug, names in slug_to_names.items():
        if len(names) == 1:
            name_to_id[names[0]] = slug
        else:
            # 충돌: 각 name에 sha1 4자 접미어 추가
            for name in sorted(names):
                h = hashlib.sha1(name.encode("utf-8")).hexdigest()[:4]
                name_to_id[name] = f"{slug}_{h}"

    return name_to_id


def canonical_sha256(data) -> str:
    """Canonical JSON SHA256 (sort_keys, compact separators, utf-8)."""
    canonical = json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


# ══════════════════════════════════════════════════════════════════════════
#  R1: Recipe Index
# ══════════════════════════════════════════════════════════════════════════

def phase_r1_recipe_index(recipes_data: dict) -> dict:
    """
    recipes_index_full.json → recipe_index.v2.4.json
    recipe_name 기준으로 역변환.

    출력: {
        "version": BUILD_VERSION,
        "recipes": {
            "<recipe_id>": {
                "recipe_name": "...",
                "recipe_id": "...",
                "category": "...",
                "source": "...",
                "inputs": ["Base.Plank", ...],
                "keeps": ["Base.Axe", ...]
            }
        },
        "slug_collisions": [...]
    }
    """
    items = recipes_data.get("items", {})

    # Step 1: Collect all (recipe_name, category, source) → roles/fulltypes
    # Use (recipe_name, source) as compound key for uniqueness
    recipe_map = {}  # (recipe_name, source) → { category, inputs, keeps }

    for fulltype, relations in items.items():
        # Skip meta-reference keys
        if fulltype.startswith("[") and fulltype.endswith("]"):
            continue

        for rel in relations:
            rname = rel.get("recipe", "")
            role = rel.get("role", "")
            category = rel.get("category")
            source = rel.get("source", "")

            if not rname:
                continue

            key = (rname, source)
            if key not in recipe_map:
                recipe_map[key] = {
                    "recipe_name": rname,
                    "category": category,
                    "source": source,
                    "inputs": set(),
                    "keeps": set(),
                }

            entry = recipe_map[key]
            # Update category if not set yet
            if entry["category"] is None and category is not None:
                entry["category"] = category

            if role == "input":
                entry["inputs"].add(fulltype)
            elif role == "keep":
                entry["keeps"].add(fulltype)

    # Step 2: Generate slugs and resolve collisions
    slug_to_names = defaultdict(list)
    for (rname, source) in recipe_map.keys():
        # Unique key for collision: recipe_name + source
        unique_name = f"{rname}|{source}"
        slug = slugify(rname)
        slug_to_names[slug].append(unique_name)

    name_to_id = resolve_slug_collisions(slug_to_names)

    # Step 3: Build recipe index
    recipes = {}
    collisions = []

    for (rname, source), entry in sorted(recipe_map.items()):
        unique_name = f"{rname}|{source}"
        recipe_id = name_to_id[unique_name]

        recipes[recipe_id] = {
            "recipe_id": recipe_id,
            "recipe_name": rname,
            "category": entry["category"],
            "source": source,
            "inputs": sorted(entry["inputs"]),
            "keeps": sorted(entry["keeps"]),
        }

    # Track collisions for audit
    for slug, names in slug_to_names.items():
        if len(names) > 1:
            collisions.append({
                "slug": slug,
                "names": sorted(names),
                "resolved_ids": sorted(name_to_id[n] for n in names),
            })

    output = {
        "version": BUILD_VERSION,
        "recipe_count": len(recipes),
        "recipes": recipes,
        "slug_collisions": collisions,
    }

    return output


# ══════════════════════════════════════════════════════════════════════════
#  R2: recipes_by_fulltype
# ══════════════════════════════════════════════════════════════════════════

def phase_r2_recipes_by_fulltype(recipe_index: dict) -> dict:
    """
    recipe_index → recipes_by_fulltype
    { fulltype: { as_input: [recipe_id...], as_keep: [...] } }
    """
    by_ft = defaultdict(lambda: {"as_input": set(), "as_keep": set()})

    for recipe_id, recipe in recipe_index["recipes"].items():
        for ft in recipe["inputs"]:
            by_ft[ft]["as_input"].add(recipe_id)
        for ft in recipe["keeps"]:
            by_ft[ft]["as_keep"].add(recipe_id)

    # Convert to sorted lists for determinism
    result = {}
    for ft in sorted(by_ft.keys()):
        entry = by_ft[ft]
        result[ft] = {
            "as_input": sorted(entry["as_input"]),
            "as_keep": sorted(entry["as_keep"]),
        }

    return {
        "version": BUILD_VERSION,
        "fulltype_count": len(result),
        "fulltypes": result,
    }


# ══════════════════════════════════════════════════════════════════════════
#  R3: Recipe Evidence Decisions
# ══════════════════════════════════════════════════════════════════════════

def phase_r3_decisions(
    recipe_index: dict,
    recipes_by_ft: dict,
    valid_fulltypes: set,
    unresolved_groups: list[str],
) -> dict:
    """
    recipe_index + recipes_by_fulltype + valid fulltypes → decisions

    rule_id 중심 구조 (RightClick pipeline과 대칭):
    - rules: { rp.recipe.<id>: { decision, matched_fulltypes, matched_keep_fulltypes, ... } }
    - by_fulltype: { ft: { rule_ids: [{rule_id, role}, ...] } }

    결정 규칙:
    - input에 등장하는 fulltype → PASS (행동의 실제 참여), role="consume"
    - keep에 등장하는 fulltype (PASS 레시피) → PASS, role="keep"
    - unknown fulltype → REVIEW
    """
    rules = {}
    review_items = []  # for R4
    keep_unresolved = []  # 함수 선두, 루프 밖 초기화
    recipe_keep_link_count = 0

    for recipe_id, recipe in sorted(recipe_index["recipes"].items()):
        rule_id = f"rp.recipe.{recipe_id}"

        # Collect matched_fulltypes (input only = PASS evidence)
        matched_fulltypes = []
        matched_keep_fulltypes = []
        review_reasons_for_rule = []

        for ft in recipe["inputs"]:
            if ft not in valid_fulltypes:
                review_reasons_for_rule.append({
                    "fulltype": ft,
                    "reason": REASON_UNKNOWN_FULLTYPE_REF,
                })
            else:
                matched_fulltypes.append(ft)

        for ft in recipe["keeps"]:
            if ft in valid_fulltypes:
                matched_keep_fulltypes.append(ft)
            else:
                keep_unresolved.append(ft)

        # Check if recipe has no inputs (only keeps) — still a valid recipe but NO evidence
        if not recipe["inputs"] and not recipe["keeps"]:
            review_reasons_for_rule.append({
                "fulltype": None,
                "reason": REASON_MISSING_OUTPUT,
            })

        # Determine rule-level decision
        if review_reasons_for_rule:
            decision = "REVIEW"
        elif matched_fulltypes:
            decision = "PASS"
        else:
            # Recipe exists but no matched fulltypes (empty inputs, only keeps)
            decision = "NO"

        rules[rule_id] = {
            "decision": decision,
            "recipe_id": recipe_id,
            "recipe_name": recipe["recipe_name"],
            "category": recipe["category"],
            "source": recipe["source"],
            "matched_fulltypes": sorted(matched_fulltypes),
            "matched_keep_fulltypes": sorted(matched_keep_fulltypes),
        }

        # Collect review items for R4
        for rr in review_reasons_for_rule:
            review_items.append({
                "rule_id": rule_id,
                "recipe_id": recipe_id,
                "recipe_name": recipe["recipe_name"],
                "fulltype": rr["fulltype"],
                "reason": rr["reason"],
            })

    # Build by_fulltype — rule_ids: [{rule_id, role}] (C1 확정 스키마)
    by_fulltype = defaultdict(list)  # ft → [{rule_id, role}]

    for rule_id, rule in rules.items():
        if rule["decision"] != "PASS":
            continue
        for ft in rule["matched_fulltypes"]:
            by_fulltype[ft].append({"rule_id": rule_id, "role": "consume"})
        for ft in rule.get("matched_keep_fulltypes", []):
            by_fulltype[ft].append({"rule_id": rule_id, "role": "keep"})
            recipe_keep_link_count += 1

    # Sort for determinism — (role, rule_id) 순
    by_fulltype_sorted = {}
    for ft in sorted(by_fulltype.keys()):
        by_fulltype_sorted[ft] = {
            "rule_ids": sorted(
                by_fulltype[ft],
                key=lambda e: (e["role"], e["rule_id"]),
            ),
        }

    # Handle dynamic_recipe_expr: only unresolved groups remain as REVIEW.
    # Resolved groups are excluded entirely — they don't generate evidence decisions,
    # they are simply removed from the dynamic_recipe_expr REVIEW list.
    for group_name in sorted(unresolved_groups):
        review_items.append({
            "rule_id": None,
            "recipe_id": None,
            "recipe_name": None,
            "fulltype": None,
            "reason": REASON_DYNAMIC_EXPR_GROUP_DEF_DYNAMIC,
            "detail": f"Recipe.GetItemTypes.{group_name}",
        })

    decisions = {
        "version": BUILD_VERSION,
        "rules": rules,
        "by_fulltype": by_fulltype_sorted,
        "stats": {
            "total_rules": len(rules),
            "pass_rules": sum(1 for r in rules.values() if r["decision"] == "PASS"),
            "no_rules": sum(1 for r in rules.values() if r["decision"] == "NO"),
            "review_rules": sum(1 for r in rules.values() if r["decision"] == "REVIEW"),
            "pass_fulltypes": len(by_fulltype_sorted),
            "keep_unresolved_count": len(keep_unresolved),
            "recipe_keep_link_count": recipe_keep_link_count,
        },
    }

    return decisions, review_items


# ══════════════════════════════════════════════════════════════════════════
#  RQ: Requirements by FullType
# ══════════════════════════════════════════════════════════════════════════

def phase_rq_requirements_by_fulltype(
    recipe_index: dict,
    recipes_by_ft: dict,
    valid_fulltypes: set,
    require_fields_data: dict | None = None,
) -> dict:
    """
    requirements_by_fulltype 산출물 생성 (v2.5).

    requirements 채널 (keep, 기존 유지):
      fulltype이 as_input에 참여하는 레시피의 keeps를 수집.
      자격: fulltype이 레시피의 input에 등장해야 해당 레시피의 keep이 연결됨.

    require 채널 (신규, output 기준):
      recipe_require_fields에서 output_fulltype 기준으로 require atom 수집.
      require가 없는 fulltype에는 require 키 생략 (빈 배열 금지, R4).

    diagnostics.unparsed_require: kind allowlist 밖 atom 기록 (파이프라인 단계).
    """
    ft_reqs: dict[str, list[dict]] = {}
    ft_require: dict[str, list[dict]] = {}  # require 채널
    debug_recipe_names: dict[str, str] = {}
    violations = []
    unparsed_require = []  # pipeline-stage diagnostics

    fulltypes_data = recipes_by_ft.get("fulltypes", {})
    recipes = recipe_index.get("recipes", {})

    # ── requirements 채널 (keep, 기존 로직 변경 없음) ──
    for ft, ft_entry in fulltypes_data.items():
        as_input_ids = ft_entry.get("as_input", [])
        if not as_input_ids:
            continue

        reqs = []
        for recipe_id in as_input_ids:
            recipe = recipes.get(recipe_id)
            if not recipe:
                continue
            keeps = recipe.get("keeps", [])
            if not keeps:
                continue

            rule_id = f"rp.recipe.{recipe_id}"
            if rule_id not in debug_recipe_names:
                debug_recipe_names[rule_id] = recipe.get("recipe_name", recipe_id)

            for keep_ft in keeps:
                if keep_ft not in valid_fulltypes:
                    violations.append(
                        f"requirement_key '{keep_ft}' not in items_itemscript "
                        f"(recipe={recipe_id}, fulltype={ft})"
                    )
                    continue

                reqs.append({
                    "recipe_id": rule_id,
                    "role": "keep",
                    "requirement_key": keep_ft,
                    "surface": "recipe_ui",
                })

        if reqs:
            reqs.sort(key=lambda r: (r["role"], r["requirement_key"], r["recipe_id"]))
            ft_reqs[ft] = reqs

    # FAIL-LOUD
    if violations:
        raise ValueError(
            f"FAIL-LOUD: {len(violations)} invalid requirement_key(s) detected:\n"
            + "\n".join(f"  - {v}" for v in violations[:20])
        )

    # ── require 채널 (output + keep 기준, v2.5) ──
    if require_fields_data:
        rf_recipes = require_fields_data.get("recipes", {})
        for rf_id, rf_entry in rf_recipes.items():
            output_ft = rf_entry.get("output_fulltype")
            if not output_ft:
                continue  # no output → skip (already in parser diagnostics)
            if output_ft not in valid_fulltypes:
                continue  # invalid fulltype → skip (parser diagnostics captures)

            rf_requires = rf_entry.get("requires", [])
            if not rf_requires:
                continue

            rule_id = f"rp.recipe.{rf_id}"
            source = rf_entry.get("source", {})

            # keep fulltypes: 동일 레시피의 keeps에 등장하는 valid fulltype
            recipe = recipes.get(rf_id, {})
            keep_fts = [ft for ft in recipe.get("keeps", []) if ft in valid_fulltypes]

            for atom in rf_requires:
                kind = atom.get("kind", "")
                if kind not in REQUIRE_ATOM_KINDS:
                    unparsed_require.append({
                        "recipe_id": rule_id,
                        "reason": "kind_not_in_allowlist",
                        "kind": kind,
                        "raw": atom,
                    })
                    continue

                req_entry = {
                    "recipe_id": rule_id,
                    "kind": kind,
                    "key": atom["key"],
                    "via": "recipe_field",
                    "source": source,
                }
                if kind == "perk":
                    req_entry["op"] = atom.get("op", ">=")
                    req_entry["value"] = atom.get("value", 0)

                ft_require.setdefault(output_ft, []).append(req_entry)

                # keep fulltypes에도 동일 atoms 연결 (via="recipe_keep")
                for kft in keep_fts:
                    keep_entry = {**req_entry, "via": "recipe_keep"}
                    ft_require.setdefault(kft, []).append(keep_entry)

        # Deterministic sort for require entries
        for ft in ft_require:
            ft_require[ft].sort(
                key=lambda r: (r["kind"], r["key"], r.get("op", ""), r.get("value", 0), r["recipe_id"])
            )

    # ── Assemble output ──
    all_fts = sorted(set(ft_reqs.keys()) | set(ft_require.keys()))
    sorted_fulltypes = {}
    for ft in all_fts:
        entry = {}
        if ft in ft_reqs:
            entry["requirements"] = ft_reqs[ft]
        if ft in ft_require:
            entry["require"] = ft_require[ft]  # R4: only if non-empty
        sorted_fulltypes[ft] = entry

    requirements_count = sum(len(e.get("requirements", [])) for e in sorted_fulltypes.values())
    require_count = sum(len(e.get("require", [])) for e in sorted_fulltypes.values())
    require_ft_count = sum(1 for e in sorted_fulltypes.values() if "require" in e)

    return {
        "version": BUILD_VERSION,
        "fulltype_count": len(sorted_fulltypes),
        "requirements_entry_count": requirements_count,
        "require_entry_count": require_count,
        "require_fulltype_count": require_ft_count,
        "fulltypes": sorted_fulltypes,
        "diagnostics": {
            "unparsed_require": unparsed_require,
        },
        "_debug": {
            "recipe_names": dict(sorted(debug_recipe_names.items())),
        },
    }


# ══════════════════════════════════════════════════════════════════════════
#  R4: Recipe Review Queue
# ══════════════════════════════════════════════════════════════════════════

def phase_r4_review_queue(review_items: list) -> dict:
    """
    review_items → recipe_review_queue.v2.4.json

    각 항목은 기계적 사유(열거형 reason)를 기록.
    """
    # Validate all reasons are in the enum
    for item in review_items:
        reason = item.get("reason", "")
        if reason not in VALID_REVIEW_REASONS:
            raise ValueError(
                f"Invalid review reason '{reason}' — "
                f"must be one of {sorted(VALID_REVIEW_REASONS)}"
            )

    # Sort deterministically
    sorted_items = sorted(
        review_items,
        key=lambda x: (
            x.get("reason", ""),
            x.get("rule_id") or "",
            x.get("fulltype") or "",
        ),
    )

    return {
        "version": BUILD_VERSION,
        "total": len(sorted_items),
        "by_reason": {
            reason: sum(1 for i in sorted_items if i["reason"] == reason)
            for reason in sorted(VALID_REVIEW_REASONS)
            if any(i["reason"] == reason for i in sorted_items)
        },
        "items": sorted_items,
    }


# ══════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════

def main():
    pipeline_banner(f"Recipe Evidence Pipeline (BUILD_VERSION={BUILD_VERSION})", 60)
    runner = StageRunner()

    # ── Check prerequisites ──
    if not require_inputs([
        (RECIPES_PATH, "recipes_index_full"),
        (ITEMS_PATH, "items_itemscript"),
    ]):
        return 1

    # ── Load inputs ──
    print("\n  [Load] Loading inputs...")
    recipes_data = load_json(RECIPES_PATH)
    items_data = load_json(ITEMS_PATH)

    valid_fulltypes = set(items_data.keys())
    all_group_names = sorted(
        recipes_data.get("get_item_types_groups", {}).keys()
    )

    # Input SHA for build_report tracing
    input_sha = canonical_sha256(recipes_data)
    print(f"         recipes_index_full.json SHA: {input_sha[:24]}...")
    print(f"         items_itemscript.json items: {len(valid_fulltypes)}")
    print(f"         dynamic groups: {len(all_group_names)}")

    # ── R0: Tag Index & Group Resolution ──
    runner.announce("R0", "Resolving GetItemTypes groups via tag index")
    tag_index = build_tag_index(items_data)
    print(f"       tag index: {len(tag_index)} unique tags")

    resolved_groups, unresolved_groups = resolve_get_item_types_groups(
        all_group_names, tag_index, items_data
    )
    print(f"       resolved: {len(resolved_groups)} groups")
    print(f"       unresolved: {len(unresolved_groups)} groups")
    if unresolved_groups:
        for g in unresolved_groups:
            print(f"         ⚠️ {g}: no tag match")

    # ── R1: Recipe Index (UNCHANGED — recipe structure not modified) ──
    runner.announce("R1", "Building recipe index")
    recipe_index = phase_r1_recipe_index(recipes_data)
    runner.save_json(RECIPE_INDEX_PATH, recipe_index)
    print(f"       ✅ {RECIPE_INDEX_PATH.name}: {recipe_index['recipe_count']} recipes")
    if recipe_index["slug_collisions"]:
        print(f"       ⚠️ Slug collisions resolved: {len(recipe_index['slug_collisions'])}")
        for c in recipe_index["slug_collisions"]:
            print(f"         {c['slug']} → {c['resolved_ids']}")

    # ── R2: recipes_by_fulltype ──
    runner.announce("R2", "Building recipes_by_fulltype")
    recipes_by_ft = phase_r2_recipes_by_fulltype(recipe_index)
    runner.save_json(RECIPES_BY_FT_PATH, recipes_by_ft)
    print(f"       ✅ {RECIPES_BY_FT_PATH.name}: {recipes_by_ft['fulltype_count']} fulltypes")

    # ── R3: Decisions (only unresolved groups go to REVIEW) ──
    runner.announce("R3", "Building recipe evidence decisions")
    decisions, review_items = phase_r3_decisions(
        recipe_index, recipes_by_ft, valid_fulltypes, unresolved_groups
    )
    runner.save_json(DECISIONS_PATH, decisions)
    stats = decisions["stats"]
    print(f"       ✅ {DECISIONS_PATH.name}")
    print(f"         rules: {stats['total_rules']} "
          f"(PASS={stats['pass_rules']}, NO={stats['no_rules']}, "
          f"REVIEW={stats['review_rules']})")
    print(f"         PASS fulltypes: {stats['pass_fulltypes']}")

    # ── RQ: Requirements by FullType ──
    runner.announce("RQ", "Building requirements_by_fulltype")
    # Load require fields (v2.5) if available
    require_fields_data = None
    if REQUIRE_FIELDS_PATH.exists():
        require_fields_data = load_json(REQUIRE_FIELDS_PATH)
        print(f"       require_fields: {REQUIRE_FIELDS_PATH.name} loaded "
              f"({require_fields_data.get('parsed_require_count', 0)} recipes with requires)")
    else:
        print(f"       ⚠️ require_fields not found: {REQUIRE_FIELDS_PATH.name} (require channel disabled)")

    requirements = phase_rq_requirements_by_fulltype(
        recipe_index, recipes_by_ft, valid_fulltypes, require_fields_data
    )
    runner.save_json(REQUIREMENTS_BY_FT_PATH, requirements)
    print(f"       ✅ {REQUIREMENTS_BY_FT_PATH.name}")
    print(f"         fulltypes={requirements['fulltype_count']}, "
          f"keep_entries={requirements['requirements_entry_count']}, "
          f"require_entries={requirements['require_entry_count']} "
          f"(require_fts={requirements['require_fulltype_count']})")
    diag = requirements.get("diagnostics", {})
    if diag.get("unparsed_require"):
        print(f"         unparsed_require: {len(diag['unparsed_require'])}")
    # ── R4: Review Queue ──
    runner.announce("R4", "Building recipe review queue")
    review_queue = phase_r4_review_queue(review_items)
    runner.save_json(REVIEW_QUEUE_PATH, review_queue)
    print(f"       ✅ {REVIEW_QUEUE_PATH.name}: {review_queue['total']} items")
    if review_queue["by_reason"]:
        for reason, count in review_queue["by_reason"].items():
            print(f"         {reason}: {count}")

    # ── R5: Dynamic Expr Catalog ──
    runner.announce("R5", "Building dynamic expr catalog")
    catalog = build_dynamic_expr_catalog(resolved_groups, unresolved_groups)
    runner.save_json(DYNAMIC_CATALOG_PATH, catalog)
    print(f"       ✅ {DYNAMIC_CATALOG_PATH.name}")
    print(f"         total={catalog['total_groups']}, "
          f"resolved={catalog['resolved_count']}, "
          f"unresolved={catalog['unresolved_count']}")

    # ── R6: Dynamic Group Policy (정책 증거 봉인) ──
    runner.announce("R6", "Building dynamic group policy document")
    policy_groups = {}
    for group_name in sorted(unresolved_groups):
        deps = UNRESOLVED_GROUP_DEPS.get(group_name, {})
        policy_groups[group_name] = {
            "status": "permanent_review",
            "reason": deps.get("rationale", "depends_on_unreconstructable_runtime_table"),
            "depends_on": deps.get("depends_on", []),
            "source_ref": deps.get("source_ref", f"recipecode.lua::Recipe.GetItemTypes.{group_name}"),
        }
    policy_doc = {
        "version": BUILD_VERSION,
        "policy": GROUP_DEF_DYNAMIC_POLICY,
        "policy_description": (
            "group_def_dynamic은 정적 해석 불가로 영구 REVIEW 고정. "
            "FabricType 필드 부재 + ClothingRecipesDefinitions 런타임 테이블 의존으로 "
            "정적 재구성 불가 판정. 해결 시도하지 않음."
        ),
        "frozen_count": len(policy_groups),
        "groups": policy_groups,
    }
    runner.save_json(DYNAMIC_GROUP_POLICY_PATH, policy_doc)
    print(f"       ✅ {DYNAMIC_GROUP_POLICY_PATH.name}")
    print(f"         policy={GROUP_DEF_DYNAMIC_POLICY}, frozen_count={len(policy_groups)}")

    # ── Summary ──
    print(f"\n{'=' * 60}")
    print(f"  ✅ Recipe Evidence Pipeline complete")
    print(f"     Input SHA: {input_sha[:24]}...")
    print(f"     Outputs:")
    print(f"       {RECIPE_INDEX_PATH.name}")
    print(f"       {RECIPES_BY_FT_PATH.name}")
    print(f"       {DECISIONS_PATH.name}")
    print(f"       {REVIEW_QUEUE_PATH.name}")
    print(f"       {DYNAMIC_CATALOG_PATH.name}")
    print(f"       {DYNAMIC_GROUP_POLICY_PATH.name}")
    print(f"       {REQUIREMENTS_BY_FT_PATH.name}")
    print(f"{'=' * 60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
