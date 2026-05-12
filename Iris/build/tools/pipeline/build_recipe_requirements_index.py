"""
build_recipe_requirements_index.py — 레시피 요구사항 인덱스 산출
================================================================
requirements_by_fulltype + usecases_by_fulltype + recipe_require_fields
  → recipe_requirements_index.json

교차 fulltype 피벗:
  requirements_by_fulltype의 require atoms는 "이 fulltype을 생산하는 레시피의 요구사항".
  usecases의 lines는 "이 아이템을 소비하는 레시피".
  모든 fulltype의 require atoms를 recipe_id 기준으로 피벗하면,
  소비 측 lines에서 참조하는 recipe의 실제 요구사항을 조회할 수 있다.

rp→uc 변환 2단계:
  1. rp.recipe.xxx → uc.recipe.xxx 직접 변환
  2. 실패 시 SHA suffix(_[0-9a-f]{4}$) 제거 → base slug로 재시도
  base slug도 없으면 dangling → stats 격리

kind allowlist: {"perk", "near_item", "flag"} — 위반 시 FAIL-LOUD
정렬: entries 키 알파벳순, requirements 배열 (kind, display) 튜플순

Output: output/recipe_requirements_index.{BUILD_VERSION}.json
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
from tools.common.versions import BUILD_VERSION, REQUIRE_FIELDS_VERSION, versioned_name

REQUIREMENTS_PATH = OUTPUT_DIR / f"requirements_by_fulltype.{BUILD_VERSION}.json"
USECASES_PATH = OUTPUT_DIR / f"usecases_by_fulltype.{BUILD_VERSION}.json"
REQUIRE_FIELDS_PATH = OUTPUT_DIR / versioned_name("recipe_require_fields", REQUIRE_FIELDS_VERSION)
INDEX_OUTPUT_PATH = OUTPUT_DIR / f"recipe_requirements_index.{BUILD_VERSION}.json"

# ── Constants ──
# SUPPORTED_KINDS: 이 목록 밖의 kind가 나타나면 빌드 FAIL-LOUD (I2)
SUPPORTED_KINDS = {"perk", "near_item", "flag"}
KIND_ALLOWLIST = SUPPORTED_KINDS  # 하위 호환 별칭
RE_SHA_SUFFIX = re.compile(r"_[0-9a-f]{4}$")

# ── Korean translations (display용) ──
PERK_NAME_KO = {
    "Blacksmith": "대장장이",
    "Electricity": "전기공학",
    "MetalWelding": "금속용접",
    "Trapping": "함정",
    "Woodwork": "목공",
}
NEAR_ITEM_KO = {
    "Anvil": "모루",
}
FLAG_DISPLAY_KO = {
    "NeedToBeLearn": "미습득",  # 런타임에서 충족 시 "습득"으로 교체
}


def build_check(kind: str, atom: dict, recipe_name: str | None) -> dict:
    """atom에 대한 check 필드 생성. 실패 시 ValueError (빌드 FAIL-LOUD).

    check 스키마:
      perk:      { type, perk_id, level }
      near_item: { type, near_token }       ← C2 1단계: fulltype 미해소, 토큰만 저장
      flag:      { type, flag_id, recipe_name }   ← recipe_name = ScriptManager OriginalName

    M1 설계 의도: near_item은 check 필드가 존재하나 런타임 핸들러가 nil 반환 → 회색 고정.
    2단계 커밋에서 near_token→fulltype 해소 + 핸들러 활성화 시 자연스럽게 색상 점등.
    """
    if kind not in SUPPORTED_KINDS:
        raise ValueError(f"Unsupported requirement kind: {kind!r}")

    if kind == "perk":
        return {
            "type": "perk",
            "perk_id": atom["key"],
            "level": atom.get("value", 0),
        }
    elif kind == "near_item":
        # C2: 1단계 — 원본 토큰만 저장, fulltype 해소는 별도 커밋
        return {"type": "near_item", "near_token": atom["key"]}
    elif kind == "flag":
        # recipe_name 계약: ScriptManager OriginalName과 1:1 대응
        if not recipe_name:
            raise ValueError(
                f"flag check requires recipe_name but got None "
                f"(recipe_id slug not found in recipe_require_fields)"
            )
        return {
            "type": "flag",
            "flag_id": atom["key"],
            "recipe_name": recipe_name,
        }
    # SUPPORTED_KINDS 가드가 위에서 걸러주므로 여기 도달 불가
    raise ValueError(f"Unreachable: kind={kind!r}")


def build_index(
    requirements_data: dict, usecases_data: dict,
    require_fields_data: dict,
) -> dict:
    """Build recipe_requirements_index from existing build artifacts."""
    # Step 1: 모든 uc.recipe.* ucid 수집
    uc_recipe_ids = set()
    for ft, entry in usecases_data.get("fulltypes", {}).items():
        for uc in entry.get("use_cases", []):
            ucid = uc.get("use_case_id", "")
            if ucid.startswith("uc.recipe."):
                uc_recipe_ids.add(ucid)

    # Build recipe_id slug → OriginalName lookup
    # recipe_require_fields의 recipe_name이 ScriptManager OriginalName
    slug_to_name = {}
    for slug, rdata in require_fields_data.get("recipes", {}).items():
        slug_to_name[slug] = rdata.get("recipe_name", "")

    # Step 2: 전체 fulltype 순회 → recipe_id 기준 피벗
    # require atoms를 rp.recipe.xxx 단위로 수집 (fulltype 간 중복 제거)
    rp_to_atoms = {}  # {rp.recipe.xxx: [atoms]}
    rp_seen = {}      # {rp.recipe.xxx: set of (kind, display)} — 중복 방지
    kind_violations = []
    check_build_errors = []

    for ft, fdata in requirements_data.get("fulltypes", {}).items():
        for atom in fdata.get("require", []):
            rid = atom.get("recipe_id", "")
            if not rid.startswith("rp.recipe."):
                continue

            kind = atom.get("kind", "")
            if kind not in KIND_ALLOWLIST:
                kind_violations.append(f"{rid}: kind={kind!r}")
                continue

            # display 렌더 (한국어)
            if kind == "perk":
                op = atom.get("op", ">=")
                value = atom.get("value", 0)
                key = atom.get("key", "")
                key_ko = PERK_NAME_KO.get(key, key)
                display = f"{key_ko} {op} {value}"
            elif kind == "near_item":
                raw_key = atom.get('key', '')
                display = NEAR_ITEM_KO.get(raw_key, f"Near: {raw_key}")
            elif kind == "flag":
                raw_key = atom.get("key", "")
                display = FLAG_DISPLAY_KO.get(raw_key, raw_key)
            else:
                display = f"UNKNOWN:{kind}:{atom.get('key', '')}"

            # check 필드 생성 (C1: FAIL-LOUD — 모든 atom에 check 필수)
            rid_slug = rid.replace("rp.recipe.", "", 1)
            recipe_name = slug_to_name.get(rid_slug)
            try:
                check = build_check(kind, atom, recipe_name)
            except ValueError as e:
                check_build_errors.append(f"{rid}: {e}")
                continue

            if rid not in rp_to_atoms:
                rp_to_atoms[rid] = []
                rp_seen[rid] = set()

            dedup_key = (kind, display)
            if dedup_key in rp_seen[rid]:
                continue  # 같은 레시피의 동일 atom — fulltype 간 중복 스킵
            rp_seen[rid].add(dedup_key)
            rp_to_atoms[rid].append({"kind": kind, "display": display, "check": check})

    # FAIL-LOUD: kind allowlist 위반
    if kind_violations:
        print(f"\n  ❌ FAIL-LOUD: {len(kind_violations)} kind allowlist violations")
        for v in kind_violations[:10]:
            print(f"    {v}")
        return None

    # FAIL-LOUD: check 빌드 실패 (C1)
    if check_build_errors:
        print(f"\n  ❌ FAIL-LOUD: {len(check_build_errors)} check build errors")
        for e in check_build_errors[:10]:
            print(f"    {e}")
        return None

    # Step 3: rp→uc 변환 (2단계 fallback)
    entries = {}
    base_slug_fallback_count = 0
    dangling_count = 0
    dangling_non_suffixed_count = 0
    atoms_total = 0
    atoms_with_check = 0
    atoms_without_check = 0

    for rp_id, atoms in rp_to_atoms.items():
        # 1차: 직접 변환
        uc_id = rp_id.replace("rp.recipe.", "uc.recipe.", 1)

        if uc_id not in uc_recipe_ids:
            # 2차: SHA suffix 제거 → base slug fallback
            slug_part = uc_id.replace("uc.recipe.", "", 1)
            m = RE_SHA_SUFFIX.search(slug_part)
            if m:
                base_slug = "uc.recipe." + slug_part[:m.start()]
                if base_slug in uc_recipe_ids:
                    uc_id = base_slug
                    base_slug_fallback_count += 1
                else:
                    # (A) dangling — base slug도 없음
                    dangling_count += 1
                    continue
            else:
                # non-suffixed 불일치 (예: remove_battery)
                dangling_non_suffixed_count += 1
                continue

        # 정렬: (kind, display) 튜플순
        sorted_atoms = sorted(atoms, key=lambda a: (a["kind"], a["display"]))
        entries[uc_id] = sorted_atoms
        atoms_total += len(sorted_atoms)
        for a in sorted_atoms:
            if "check" in a:
                atoms_with_check += 1
            else:
                atoms_without_check += 1

    # Step 4: 요구사항 없는 ucid → 빈 배열
    for ucid in uc_recipe_ids:
        if ucid not in entries:
            entries[ucid] = []

    # Stats
    with_requirements = sum(1 for v in entries.values() if len(v) > 0)
    without_requirements = sum(1 for v in entries.values() if len(v) == 0)

    # UID collision check
    uid_collision_count = 0  # entries는 dict이므로 자동 0

    # req_missing_index_count: usecases에 있는 ucid가 entries에 없는 건수
    req_missing_index_count = sum(1 for uid in uc_recipe_ids if uid not in entries)

    index = {
        "version": BUILD_VERSION,
        "entries": dict(sorted(entries.items())),  # 알파벳순 정렬
        "stats": {
            "total_ucids": len(entries),
            "with_requirements": with_requirements,
            "without_requirements": without_requirements,
            "atoms_total": atoms_total,
            "atoms_with_check": atoms_with_check,
            "atoms_without_check": atoms_without_check,
            "req_missing_index_count": req_missing_index_count,
            "req_uid_collision_count": uid_collision_count,
            "req_dangling_count": dangling_count,
            "req_dangling_non_suffixed_count": dangling_non_suffixed_count,
            "req_base_slug_fallback_count": base_slug_fallback_count,
        },
    }

    return index


def main():
    print("=" * 60)
    print(f"  Build Recipe Requirements Index (BUILD_VERSION={BUILD_VERSION})")
    print("=" * 60)

    # Check prerequisites
    for path, label in [
        (REQUIREMENTS_PATH, "requirements_by_fulltype"),
        (USECASES_PATH, "usecases_by_fulltype"),
        (REQUIRE_FIELDS_PATH, "recipe_require_fields"),
    ]:
        if not path.exists():
            print(f"\n  ❌ {label} not found: {path}")
            return 1

    print(f"  Loading: {REQUIREMENTS_PATH.name}")
    requirements_data = load_json(REQUIREMENTS_PATH)

    print(f"  Loading: {USECASES_PATH.name}")
    usecases_data = load_json(USECASES_PATH)

    print(f"  Loading: {REQUIRE_FIELDS_PATH.name}")
    require_fields_data = load_json(REQUIRE_FIELDS_PATH)

    print("  Building index (cross-fulltype pivot)...")
    index = build_index(requirements_data, usecases_data, require_fields_data)
    if index is None:
        return 1

    stats = index["stats"]
    print(f"  ✅ Built: {stats['total_ucids']} ucids")
    print(f"     with_requirements:    {stats['with_requirements']}")
    print(f"     without_requirements: {stats['without_requirements']}")
    print(f"     atoms_total:          {stats['atoms_total']}")
    print(f"     atoms_with_check:     {stats['atoms_with_check']}")
    print(f"     atoms_without_check:  {stats['atoms_without_check']}")
    print(f"     base_slug_fallback:   {stats['req_base_slug_fallback_count']}")
    print(f"     dangling:             {stats['req_dangling_count']}")
    print(f"     dangling_non_suffix:  {stats['req_dangling_non_suffixed_count']}")
    print(f"     missing_index:        {stats['req_missing_index_count']}")
    print(f"     uid_collision:        {stats['req_uid_collision_count']}")

    # FAIL-LOUD checks
    if stats["req_missing_index_count"] > 0:
        print(f"\n  ❌ req_missing_index_count > 0 — FAIL-LOUD")
        return 1
    if stats["req_uid_collision_count"] > 0:
        print(f"\n  ❌ req_uid_collision_count > 0 — FAIL-LOUD")
        return 1

    # Write output
    OUTPUT_DIR.mkdir(exist_ok=True)
    write_json(INDEX_OUTPUT_PATH, index, indent=2, trailing_newline=False)

    print(f"  ✅ Saved: {INDEX_OUTPUT_PATH.relative_to(IRIS_DIR)}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
