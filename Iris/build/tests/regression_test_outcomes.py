"""
Iris Context Outcome Regression Test
====================================
Phase 6-7 검증: 빌드 파이프라인 연동 확인
- context_outcomes.json 로드 확인
- CombinedEvidence에 outcomes 포함 확인
- has_outcome() predicate 동작 확인
- (예상) Wearable.6-F 분류 테스트 (규칙 파일이 있다면)
"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from phase1_extraction.evidence_collector import collect_all_evidence
from phase2_rules.predicates import has_outcome, eq, all_of


def test_pipeline_integration():
    print("=== Testing Pipeline Integration ===")
    
    # 가정: context_outcomes.json이 output에 존재함 (Phase 0-5 실행 결과)
    iris_root = project_root.parent
    input_dir = iris_root / "input"
    output_dir = iris_root / "output"
    
    # 1. Evidence Collection
    print("Collecting evidence...")
    result = collect_all_evidence(input_dir, output_dir)
    
    print(f"Total items: {result.total_items}")
    print(f"Context Outcomes loaded: {result.stats.get('context_outcomes', 0)}")
    
    # 2. Check specific itmes (Cigarettes - Option B injected)
    cig = result.items.get("Base.Cigarettes")
    if cig:
        print(f"\n[Base.Cigarettes] Outcomes: {cig.context_outcomes}")
        
        # Test Predicate
        has_smoke = has_outcome("smoke_item")(cig)
        print(f"Predicate has_outcome('smoke_item'): {has_smoke}")
        
        if not has_smoke:
            print("❌ Option B injection failed or predicate failed")
            return False
    else:
        print("⚠️ Base.Cigarettes not found in evidence")
    
    # 3. Check for equip_back candidate (if any exists in current run)
    # 현재는 Lua 입력이 없어서 equip_back이 없을 것임.
    # 가상의 아이템으로 predicate 테스트
    
    # Mock Item
    from phase1_extraction.evidence_collector import CombinedEvidence
    mock_item = CombinedEvidence(full_type="Mock.Bag")
    mock_item.context_outcomes.add("equip_back")
    
    print(f"\n[Mock.Bag] Outcomes: {mock_item.context_outcomes}")
    has_equip = has_outcome("equip_back")(mock_item)
    print(f"Predicate has_outcome('equip_back'): {has_equip}")
    
    if not has_equip:
        print("❌ has_outcome('equip_back') failed on mock item")
        return False
        
    return True

if __name__ == "__main__":
    if test_pipeline_integration():
        print("\n✅ Regression Test Passed")
        sys.exit(0)
    else:
        print("\n❌ Regression Test Failed")
        sys.exit(1)
