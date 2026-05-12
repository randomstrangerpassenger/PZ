"""
FAIL-LOUD 시뮬레이션 테스트

새 use_case_id가 파이프라인에 추가됐을 때
label_map에 누락되면 정말 실패하는지 검증.
"""
import sys
from pathlib import Path

BUILD_DIR = Path(__file__).resolve().parents[1]
IRIS_DIR = BUILD_DIR.parent
sys.path.insert(0, str(BUILD_DIR))

from convert_labelmap_to_lua import coverage_check, extract_use_case_ids, load_json


def main():
    labelmap = load_json(BUILD_DIR / "data" / "v2.4" / "usecase_label_map.json")
    label_keys = set(labelmap["labels"].keys())
    usecases = load_json(IRIS_DIR / "output" / "usecases_by_fulltype.v2.4.json")
    actual_ids = {
        use_case_id
        for use_case_id in extract_use_case_ids(usecases)
        if not use_case_id.startswith("uc.recipe.")
    }

    all_pass = True

    # Test 1: 현재 상태 - 정상 통과
    missing = coverage_check(actual_ids, label_keys)
    ok = len(missing) == 0
    print(f"[Test 1] 현재 상태 (정상): missing={len(missing)}  => {'PASS' if ok else 'FAIL'}")
    if not ok:
        all_pass = False

    # Test 2: 새 use_case_id 2개 추가 시뮬레이션
    fake_new_ids = actual_ids | {"uc.new_feature.test_action", "uc.craft.new_tool"}
    missing2 = coverage_check(fake_new_ids, label_keys)
    ok2 = len(missing2) == 2
    print(f"\n[Test 2] 새 ID 2개 추가 시뮬레이션: missing={len(missing2)}")
    for m in missing2:
        print(f"    - {m}")
    print(f"  => {'PASS (FAIL-LOUD 정상 작동)' if ok2 else 'FAIL'}")
    if not ok2:
        all_pass = False

    # Test 3: label_map에서 기존 ID 1개 제거
    reduced_keys = label_keys - {"uc.action.open_can"}
    missing3 = coverage_check(actual_ids, reduced_keys)
    ok3 = len(missing3) == 1 and "uc.action.open_can" in missing3
    print(f"\n[Test 3] label_map에서 uc.action.open_can 제거: missing={len(missing3)}")
    for m in missing3:
        print(f"    - {m}")
    print(f"  => {'PASS (FAIL-LOUD 정상 작동)' if ok3 else 'FAIL'}")
    if not ok3:
        all_pass = False

    # Test 4: label_map에 미사용 extra 포함 - 통과해야 함
    extra_keys = label_keys | {"uc.future.placeholder"}
    missing4 = coverage_check(actual_ids, extra_keys)
    ok4 = len(missing4) == 0
    print(f"\n[Test 4] label_map에 미사용 extra 포함: missing={len(missing4)}")
    print(f"  => {'PASS (extra는 경고만, 실패 아님)' if ok4 else 'FAIL'}")
    if not ok4:
        all_pass = False

    print("\n" + "=" * 50)
    if all_pass:
        print("FINAL: ALL 4 TESTS PASSED")
    else:
        print("FINAL: SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
