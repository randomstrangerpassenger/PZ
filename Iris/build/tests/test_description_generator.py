"""
DescriptionGenerator 자동 검증 스크립트
=======================================
로드맵 §7: 샘플 고정 금지 — 데이터에서 자동으로 케이스 추출.

Case 1: surface="both"인 fulltype → 라인에 "우클릭+레시피" 존재
Case 2: surface="recipe_ui" only인 fulltype → "레시피" 존재
Case 3: display_strength=null 항목 포함 → strength 슬롯 비어있음
Case 4: REVIEW 포함 fulltype → debug_lines에만 존재
Case 5: 결정성 — 2회 실행 SHA 비교
"""
import json
import hashlib
import subprocess
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parents[1]
IRIS_DIR = BUILD_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"
GENERATOR = BUILD_DIR / "description_generator.py"

USECASES_PATH = OUTPUT_DIR / "usecases_by_fulltype.v2.4.json"
DESC_PATH = OUTPUT_DIR / "descriptions_by_fulltype.v2.4.json"

ok_all = True


def sha_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_fulltype_with_surface(usecases: dict, target_surface: str) -> str | None:
    """데이터에서 target_surface를 가진 첫 번째 fulltype 자동 선택."""
    for ft in sorted(usecases.keys()):
        for uc in usecases[ft].get("use_cases", []):
            if uc.get("surface") == target_surface:
                return ft
    return None


def find_fulltype_with_null_strength(usecases: dict) -> str | None:
    """display_strength=null 항목이 포함된 첫 번째 fulltype 자동 선택."""
    for ft in sorted(usecases.keys()):
        for uc in usecases[ft].get("use_cases", []):
            if uc.get("display_strength") is None:
                return ft
    return None


def find_fulltype_with_review_only(usecases: dict) -> str | None:
    """REVIEW decision만 있고 PASS가 없는 use_case를 가진 fulltype 자동 선택."""
    for ft in sorted(usecases.keys()):
        for uc in usecases[ft].get("use_cases", []):
            has_pass = any(s.get("decision") == "PASS" for s in uc.get("evidence_sources", []))
            has_review = any(s.get("decision") == "REVIEW" for s in uc.get("evidence_sources", []))
            if has_review and not has_pass:
                return ft
    return None


# ══════════════════════════════════════════════════════════════════════════
#  Load data
# ══════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("  DescriptionGenerator Verification")
print("=" * 60)

if not USECASES_PATH.exists():
    print(f"\n❌ usecases not found: {USECASES_PATH}")
    sys.exit(1)
if not DESC_PATH.exists():
    print(f"\n❌ descriptions not found: {DESC_PATH}")
    sys.exit(1)

usecases_data = json.loads(USECASES_PATH.read_text("utf-8"))
usecases = usecases_data.get("fulltypes", {})

desc_data = json.loads(DESC_PATH.read_text("utf-8"))
desc_fts = desc_data.get("fulltypes", {})


# ══════════════════════════════════════════════════════════════════════════
#  Case 1: surface="both" → "우클릭+레시피"
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Case 1: surface=both ===")
ft_both = find_fulltype_with_surface(usecases, "both")
if ft_both is None:
    print("  ⏭ SKIP: no surface=both in source data (0 items — correct)")
else:
    desc_block = desc_fts.get(ft_both, {}).get("use_case_block", {})
    all_lines = desc_block.get("lines", []) + desc_block.get("debug_lines", [])
    has_both_label = any("우클릭+레시피" in l for l in all_lines)
    if has_both_label:
        print(f"  ✅ PASS: {ft_both} has '우클릭+레시피' in lines")
    else:
        print(f"  ❌ FAIL: {ft_both} missing '우클릭+레시피'")
        ok_all = False


# ══════════════════════════════════════════════════════════════════════════
#  Case 2: surface="recipe_ui" only → "레시피"
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Case 2: surface=recipe_ui ===")
ft_recipe = find_fulltype_with_surface(usecases, "recipe_ui")
if ft_recipe is None:
    print("  ❌ FAIL: no surface=recipe_ui found in source data")
    ok_all = False
else:
    desc_block = desc_fts.get(ft_recipe, {}).get("use_case_block", {})
    all_lines = desc_block.get("lines", []) + desc_block.get("debug_lines", [])
    has_recipe_label = any("(레시피)" in l for l in all_lines)
    if has_recipe_label:
        print(f"  ✅ PASS: {ft_recipe} has '(레시피)' in lines")
    else:
        print(f"  ❌ FAIL: {ft_recipe} missing '(레시피)' in {all_lines}")
        ok_all = False


# ══════════════════════════════════════════════════════════════════════════
#  Case 3: display_strength=null → strength 슬롯 없음
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Case 3: display_strength=null ===")
ft_null_str = find_fulltype_with_null_strength(usecases)
if ft_null_str is None:
    print("  ❌ FAIL: no null strength found in source data")
    ok_all = False
else:
    desc_block = desc_fts.get(ft_null_str, {}).get("use_case_block", {})
    all_lines = desc_block.get("lines", []) + desc_block.get("debug_lines", [])
    # null strength → 라인에 [강]도 [약]도 없어야 함 (해당 use_case 라인에서)
    # Find the specific use_case with null strength
    target_ucid = None
    for uc in usecases[ft_null_str].get("use_cases", []):
        if uc.get("display_strength") is None:
            target_ucid = uc["use_case_id"]
            break
    target_line = [l for l in all_lines if target_ucid in l]
    if target_line:
        has_strength_tag = "[강]" in target_line[0] or "[약]" in target_line[0]
        if not has_strength_tag:
            print(f"  ✅ PASS: {ft_null_str}/{target_ucid} has no strength tag")
        else:
            print(f"  ❌ FAIL: {ft_null_str}/{target_ucid} has strength tag in: {target_line[0]}")
            ok_all = False
    else:
        print(f"  ❌ FAIL: {ft_null_str}/{target_ucid} line not found")
        ok_all = False


# ══════════════════════════════════════════════════════════════════════════
#  Case 4: REVIEW-only → debug_lines에만 존재
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Case 4: REVIEW-only → debug_lines ===")
ft_review = find_fulltype_with_review_only(usecases)
if ft_review is None:
    print("  ⏭ SKIP: no REVIEW-only use_case found in source data")
else:
    desc_block = desc_fts.get(ft_review, {}).get("use_case_block", {})
    main_lines = desc_block.get("lines", [])
    debug_lines_list = desc_block.get("debug_lines", [])

    # Find the REVIEW-only use_case_id
    review_ucid = None
    for uc in usecases[ft_review].get("use_cases", []):
        has_pass = any(s.get("decision") == "PASS" for s in uc.get("evidence_sources", []))
        has_review = any(s.get("decision") == "REVIEW" for s in uc.get("evidence_sources", []))
        if has_review and not has_pass:
            review_ucid = uc["use_case_id"]
            break

    if review_ucid:
        in_main = any(review_ucid in l for l in main_lines)
        in_debug = any(review_ucid in l for l in debug_lines_list)

        if not in_main and in_debug:
            print(f"  ✅ PASS: {ft_review}/{review_ucid} is in debug_lines only")
        elif in_main:
            print(f"  ❌ FAIL: {ft_review}/{review_ucid} leaked into main lines")
            ok_all = False
        else:
            print(f"  ❌ FAIL: {ft_review}/{review_ucid} not found in any lines")
            ok_all = False
    else:
        print(f"  ⏭ SKIP: could not identify REVIEW-only ucid for {ft_review}")


# ══════════════════════════════════════════════════════════════════════════
#  Case 5: Determinism — 2회 실행 SHA 비교
# ══════════════════════════════════════════════════════════════════════════
print("\n=== Case 5: Determinism (2-run SHA match) ===")

# Run 1
subprocess.run([sys.executable, str(GENERATOR)], capture_output=True, cwd=str(IRIS_DIR))
sha1 = sha_of_file(DESC_PATH)

# Run 2
subprocess.run([sys.executable, str(GENERATOR)], capture_output=True, cwd=str(IRIS_DIR))
sha2 = sha_of_file(DESC_PATH)

if sha1 == sha2:
    print(f"  ✅ PASS: SHA match ({sha1[:24]}...)")
else:
    print(f"  ❌ FAIL: SHA mismatch")
    print(f"    Run 1: {sha1[:24]}...")
    print(f"    Run 2: {sha2[:24]}...")
    ok_all = False


# ══════════════════════════════════════════════════════════════════════════
#  Summary
# ══════════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 60}")
print(f"  FINAL: {'ALL PASSED' if ok_all else 'FAILURES DETECTED'}")
print(f"{'=' * 60}")

sys.exit(0 if ok_all else 1)
