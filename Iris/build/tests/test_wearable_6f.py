"""
Wearable.6-F Rule Test
======================
has_outcome("equip_back") 규칙 테스트
"""
import sys
from pathlib import Path

# 프로젝트 루트 설정
build_root = Path(__file__).resolve().parents[1]
project_root = build_root.parent
sys.path.insert(0, str(build_root))
sys.path.insert(0, str(project_root))

from build.phase1_extraction.evidence_collector import CombinedEvidence
from build.phase2_rules.predicates import has_outcome


def test_wearable_6f():
    """Wearable.6-F 규칙 테스트"""
    print("=" * 60)
    print("Wearable.6-F Rule Test: has_outcome('equip_back')")
    print("=" * 60)
    
    # 테스트 케이스
    test_cases = [
        # (full_type, context_outcomes, expected_match)
        ("Base.Bag_ALICEpack", {"equip_back"}, True),
        ("Base.Bag_BigHikingBag", {"equip_back"}, True),
        ("Base.Bag_Schoolbag", {"equip_back"}, True),
        ("Base.Torch", {"toggle_activate"}, False),
        ("Base.Cigarettes", {"smoke_item"}, False),
        ("Base.BucketEmpty", {"fill_container", "empty_container"}, False),
        ("Base.Hammer", set(), False),  # 빈 outcomes
    ]
    
    passed = 0
    failed = 0
    
    for full_type, outcomes, expected in test_cases:
        # CombinedEvidence 생성
        evidence = CombinedEvidence(
            full_type=full_type,
            context_outcomes=outcomes
        )
        
        # predicate 실행
        matched = has_outcome("equip_back")(evidence)
        
        # 결과 확인
        status = "✅ PASS" if matched == expected else "❌ FAIL"
        if matched == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"  {status} {full_type}: outcomes={outcomes}, matched={matched}, expected={expected}")
    
    print()
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == "__main__":
    success = test_wearable_6f()
    sys.exit(0 if success else 1)
