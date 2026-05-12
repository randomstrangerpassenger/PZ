"""
test_require_render.py — Require 렌더 자동 검증
=================================================
3가지 케이스를 자동으로 검증:
1. requirements(keep)만 있는 FT
2. require만 있는 FT
3. 둘 다 있는 FT

FAIL-LOUD: UNKNOWN_REQUIRE_ATOM 검출 시 실패.
"""
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

IRIS_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"
LUA_PATH = (
    IRIS_DIR / "media" / "lua" / "client" / "Iris" / "Data"
    / "IrisUseCaseDescriptions.lua"
)
LUA_CHUNK_DIR = LUA_PATH.parent / "UseCaseDescriptions"
LUA_REQUIREMENTS_LOOKUP_PATH = LUA_CHUNK_DIR / "RequirementsLookup.lua"

from tools.common.io import load_json


def main():
    print("=" * 60)
    print("  Test: Require Render Verification")
    print("=" * 60)

    # ── Load descriptions ──
    desc_path = OUTPUT_DIR / "descriptions_by_fulltype.v2.4.json"
    desc = load_json(desc_path)
    fts = desc.get("fulltypes", {})

    # ── Test 1: requirements-only FT ──
    # Base.Margarine: has requirements_block but no require_block
    ft1 = "Base.Margarine"
    assert ft1 in fts, f"FAIL: {ft1} not in descriptions"
    assert "requirements_block" in fts[ft1], f"FAIL: {ft1} missing requirements_block"
    assert "require_block" not in fts[ft1], f"FAIL: {ft1} should NOT have require_block"
    print(f"  ✅ Case 1: {ft1} — requirements only ✓")

    # ── Test 2: require-only FT ──
    # Base.MortarPestle: has require_block but no requirements_block
    ft2 = "Base.MortarPestle"
    assert ft2 in fts, f"FAIL: {ft2} not in descriptions"
    assert "require_block" in fts[ft2], f"FAIL: {ft2} missing require_block"
    assert "requirements_block" not in fts[ft2], f"FAIL: {ft2} should NOT have requirements_block"
    rq2 = fts[ft2]["require_block"]
    assert rq2["title_key"] == "require", f"FAIL: {ft2} require_block title_key != 'require'"
    assert any("Woodwork >= 2" in l for l in rq2["lines"]), \
        f"FAIL: {ft2} require_block missing 'Woodwork >= 2'"
    print(f"  ✅ Case 2: {ft2} — require only ✓")

    # ── Test 3: both requirements + require ──
    # Base.MetalBar: has both
    ft3 = "Base.MetalBar"
    assert ft3 in fts, f"FAIL: {ft3} not in descriptions"
    assert "requirements_block" in fts[ft3], f"FAIL: {ft3} missing requirements_block"
    assert "require_block" in fts[ft3], f"FAIL: {ft3} missing require_block"
    req3 = fts[ft3]["requirements_block"]
    rq3 = fts[ft3]["require_block"]
    assert req3["title_key"] == "requirements", f"FAIL: {ft3} requirements_block title mismatch"
    assert rq3["title_key"] == "require", f"FAIL: {ft3} require_block title mismatch"
    # Check keep has correct keep keys
    assert any("Base.BallPeenHammer" in l for l in req3["lines"]), \
        f"FAIL: {ft3} requirements_block missing BallPeenHammer"
    # Check require has perk + flag
    assert any("MetalWelding >= 2" in l for l in rq3["lines"]), \
        f"FAIL: {ft3} require_block missing 'MetalWelding >= 2'"
    assert any("NeedToBeLearn" in l for l in rq3["lines"]), \
        f"FAIL: {ft3} require_block missing NeedToBeLearn"
    print(f"  ✅ Case 3: {ft3} — both blocks ✓")

    # ── Test 4: near_item template ──
    # Base.Nails: has Near: Anvil
    ft4 = "Base.Nails"
    assert ft4 in fts, f"FAIL: {ft4} not in descriptions"
    rq4 = fts[ft4].get("require_block", {})
    assert any("Near: Anvil" in l for l in rq4.get("lines", [])), \
        f"FAIL: {ft4} require_block missing 'Near: Anvil'"
    print(f"  ✅ Case 4: {ft4} — near_item template ✓")

    # ── Test 5: No UNKNOWN_REQUIRE_ATOM in any FT ──
    unknown_count = 0
    for ft, data in fts.items():
        rq = data.get("require_block", {})
        for line in rq.get("lines", []) + rq.get("debug_lines", []):
            if "UNKNOWN_REQUIRE_ATOM" in line:
                unknown_count += 1
                print(f"  ❌ UNKNOWN_REQUIRE_ATOM: {ft}: {line}")
    assert unknown_count == 0, f"FAIL: {unknown_count} UNKNOWN_REQUIRE_ATOM found"
    print(f"  ✅ Case 5: No UNKNOWN_REQUIRE_ATOM ✓")

    # ── Test 6: Lua output structural check ──
    facade_text = LUA_PATH.read_text("utf-8")
    lua_parts = [facade_text]
    if LUA_CHUNK_DIR.exists():
        lua_parts.extend(
            chunk.read_text("utf-8")
            for chunk in sorted(LUA_CHUNK_DIR.glob("Chunk*.lua"))
        )
    if LUA_REQUIREMENTS_LOOKUP_PATH.exists():
        lua_parts.append(LUA_REQUIREMENTS_LOOKUP_PATH.read_text("utf-8"))
    lua_content = "\n".join(lua_parts)
    require_blocks = lua_content.count("    require = {")
    require_debug_blocks = lua_content.count("    require_debug = {")
    assert require_blocks == require_debug_blocks, \
        f"FAIL: require={require_blocks} != require_debug={require_debug_blocks}"
    assert require_blocks > 0, "FAIL: No require blocks in Lua output"
    print(f"  ✅ Case 6: Lua output has {require_blocks} require blocks ✓")

    # ── Test 7: require:[] prohibition ──
    # No fulltype should have an empty require_block
    empty_rq = [ft for ft, data in fts.items()
                if "require_block" in data and not data["require_block"].get("lines")]
    assert len(empty_rq) == 0, f"FAIL: {len(empty_rq)} fulltypes with empty require_block lines"
    print(f"  ✅ Case 7: No empty require_block ✓")

    # ── Test 8: check 필드 — atoms_with_check == atoms_total (C1 FAIL-LOUD 후조건) ──
    req_idx_path = OUTPUT_DIR / "recipe_requirements_index.v2.4.json"
    if req_idx_path.exists():
        req_idx = load_json(req_idx_path)
        rq_stats = req_idx.get("stats", {})
        at = rq_stats.get("atoms_total", 0)
        awc = rq_stats.get("atoms_with_check", 0)
        awoc = rq_stats.get("atoms_without_check", 0)
        assert awc == at, f"FAIL: atoms_with_check({awc}) != atoms_total({at})"
        assert awoc == 0, f"FAIL: atoms_without_check={awoc} (must be 0)"
        print(f"  ✅ Case 8: atoms_with_check={awc} == atoms_total={at}, without=0 ✓")
    else:
        print(f"  ⚠️  Case 8: SKIPPED — {req_idx_path.name} not found")

    # ── Test 9: check 스키마 유효성 ──
    if req_idx_path.exists():
        valid_types = {"perk", "near_item", "flag"}
        schema_errors = []
        for ucid, atoms in req_idx.get("entries", {}).items():
            for atom in atoms:
                if "check" not in atom:
                    schema_errors.append(f"{ucid}: missing check (C1 violation)")
                    continue
                ck = atom["check"]
                if "type" not in ck:
                    schema_errors.append(f"{ucid}: check missing type")
                elif ck["type"] not in valid_types:
                    schema_errors.append(f"{ucid}: unknown check.type={ck['type']!r}")
                elif ck["type"] == "near_item" and "near_token" not in ck:
                    schema_errors.append(f"{ucid}: near_item missing near_token")
                elif ck["type"] == "perk" and ("perk_id" not in ck or "level" not in ck):
                    schema_errors.append(f"{ucid}: perk missing perk_id/level")
                elif ck["type"] == "flag" and ("flag_id" not in ck or "recipe_name" not in ck):
                    schema_errors.append(f"{ucid}: flag missing flag_id/recipe_name")
        for e in schema_errors[:5]:
            print(f"  ❌ {e}")
        assert len(schema_errors) == 0, f"FAIL: {len(schema_errors)} check schema errors"
        print(f"  ✅ Case 9: All check schemas valid ✓")
    else:
        print(f"  ⚠️  Case 9: SKIPPED — {req_idx_path.name} not found")

    # ── Test 10: Lua에 check 필드 존재 확인 ──
    check_count = lua_content.count("check = {")
    assert check_count > 0, "FAIL: No check fields in Lua output"
    print(f"  ✅ Case 10: Lua output has {check_count} check fields ✓")

    # ── Test 11: Recipe requirements lookup is split out of the facade ──
    assert LUA_REQUIREMENTS_LOOKUP_PATH.exists(), \
        f"FAIL: {LUA_REQUIREMENTS_LOOKUP_PATH.name} not found"
    lookup_text = LUA_REQUIREMENTS_LOOKUP_PATH.read_text("utf-8")
    assert 'require("Iris/Data/UseCaseDescriptions/RequirementsLookup")' in facade_text, \
        "FAIL: facade does not require RequirementsLookup"
    assert "local IrisRecipeRequirementsLookup = {}" not in facade_text, \
        "FAIL: facade still contains inline requirements lookup"
    assert "return IrisRecipeRequirementsLookup" in lookup_text, \
        "FAIL: RequirementsLookup does not return lookup table"
    print("  ✅ Case 11: Requirements lookup split from facade ✓")

    print()
    print("=" * 60)
    print("  FINAL RESULT: ALL PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
