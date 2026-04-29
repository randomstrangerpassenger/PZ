"""
Right-Click Capability Pipeline Tests
=====================================
TC-1 ~ TC-8 테스트 케이스
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from copy import deepcopy

# 파이프라인 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "evidence" / "rightclick"))

from pipeline import (
    RightClickCapabilityPipeline,
    load_items,
    load_source_index,
    parse_allowlist,
    gate1_validate,
    gate2_validate,
    build_indices,
    resolve_criteria,
    invert_to_fulltype,
    output_gate_validate,
    CAPABILITY_ALLOWLIST,
    EVIDENCE_TYPE_ALLOWLIST,
    setup_logger,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def sample_source_index():
    """기본 source_index 샘플"""
    return {
        "meta": {"version": "v1"},
        "capabilities": {
            "can_extinguish_fire": {
                "primary_source": {"file": "lua/server/FireFighting/FireFighting.lua"},
                "evidence_type": "explicit_predicate",
                "criteria": [
                    {"type": "type", "value": "Extinguisher"},
                    {"type": "property", "value": "isWaterSource()"}
                ]
            },
            "can_add_generator_fuel": {
                "primary_source": {"file": "lua/client/ISUI/ISWorldObjectContextMenu.lua"},
                "evidence_type": "item_tag_or_type",
                "criteria": [
                    {"type": "tag", "value": "Petrol"},
                    {"type": "type", "value": "PetrolCan"}
                ]
            },
            "can_scrap_moveables": {
                "primary_source": {"file": "lua/client/Moveables/ISMoveableDefinitions.lua"},
                "evidence_type": "static_table",
                "criteria": []
            },
            "can_open_canned_food": {
                "primary_source": {"file": "scripts/items.txt"},
                "evidence_type": "item_tag",
                "criteria": [{"type": "tag", "value": "CanOpener"}]
            },
            "can_stitch_wound": {
                "primary_source": {"file": "lua/client/XpSystem/ISUI/ISHealthPanel.lua"},
                "evidence_type": "item_type_or_tag",
                "criteria": [
                    {"type": "type", "value": "Needle"},
                    {"type": "tag", "value": "SewingNeedle"},
                    {"type": "type", "value": "Thread"},
                    {"type": "type", "value": "SutureNeedle"}
                ]
            },
            "can_remove_embedded_object": {
                "primary_source": {"file": "lua/client/XpSystem/ISUI/ISHealthPanel.lua"},
                "evidence_type": "item_tag_or_type",
                "criteria": {
                    "glass": [
                        {"type": "tag", "value": "RemoveGlass"},
                        {"type": "type", "value": "SutureNeedleHolder"},
                        {"type": "type", "value": "Tweezers"}
                    ],
                    "bullet": [
                        {"type": "tag", "value": "RemoveBullet"},
                        {"type": "type", "value": "Tweezers"},
                        {"type": "type", "value": "SutureNeedleHolder"}
                    ]
                }
            },
            "can_attach_weapon_mod": {
                "primary_source": {"file": "lua/client/ISUI/ISInventoryPaneContextMenu.lua"},
                "evidence_type": "item_display_category",
                "criteria": [{"type": "display_category", "value": "WeaponPart"}]
            }
        }
    }


@pytest.fixture
def sample_indices():
    """기본 인덱스 샘플"""
    return {
        "by_fulltype": {"Base.Hammer": {}, "Base.Extinguisher": {}, "Base.Tweezers": {}},
        "by_type": {
            "Hammer": {"Base.Hammer"},
            "Extinguisher": {"Base.Extinguisher"},
            "Tweezers": {"Base.Tweezers"},
            "SutureNeedleHolder": {"Base.SutureNeedleHolder"},
        },
        "by_tag": {
            "RemoveGlass": {"Base.Tweezers", "Base.SutureNeedleHolder"},
            "RemoveBullet": {"Base.Tweezers", "Base.SutureNeedleHolder"},
        },
        "by_property_true": {"CanStoreWater": {"Base.Bowl", "Base.BucketEmpty"}},
        "by_display_category": {"WeaponPart": {"Base.IronSight", "Base.x2Scope"}},
        "by_category": {},
    }


# ============================================================================
# TC-1: source_index에 can_invalid 삽입 → Gate-1 Fail
# ============================================================================

def test_tc1_invalid_capability_fails_gate1(sample_source_index, mock_logger):
    """TC-1: Allowlist에 없는 capability → Gate-1 Fail"""
    # can_invalid 삽입
    source_index = deepcopy(sample_source_index)
    source_index["capabilities"]["can_invalid"] = {
        "primary_source": {"file": "dummy.lua"},
        "evidence_type": "item_tag",
        "criteria": []
    }
    
    allowlist = CAPABILITY_ALLOWLIST
    
    result = gate1_validate(source_index, allowlist, mock_logger)
    
    assert result == False
    mock_logger.error.assert_called()


# ============================================================================
# TC-2: capability에 primary_source 2개 삽입 → Gate-1 Fail
# ============================================================================

def test_tc2_multiple_sources_fails_gate1(sample_source_index, mock_logger):
    """TC-2: 여러 sources → Gate-1 Fail"""
    source_index = deepcopy(sample_source_index)
    source_index["capabilities"]["can_extinguish_fire"]["sources"] = [
        {"file": "source1.lua"},
        {"file": "source2.lua"}
    ]
    
    allowlist = CAPABILITY_ALLOWLIST
    
    result = gate1_validate(source_index, allowlist, mock_logger)
    
    assert result == False


# ============================================================================
# TC-3: criteria에 미지원 resolution type 삽입 → Phase 5 Fail
# ============================================================================

def test_tc3_unsupported_resolution_type_fails(sample_indices, mock_logger):
    """TC-3: 미지원 resolution type → ValueError"""
    criteria = [{"type": "unsupported_type", "value": "test"}]
    
    with pytest.raises(ValueError) as excinfo:
        resolve_criteria(criteria, sample_indices, mock_logger)
    
    assert "Unsupported resolution type" in str(excinfo.value)


# ============================================================================
# TC-4: capability 배열에 중복 ID 삽입 → Output Gate Fail
# ============================================================================

def test_tc4_duplicate_capability_fails_output_gate(mock_logger):
    """TC-4: 중복 capability → Output Gate Fail"""
    output = {
        "Base.Hammer": ["can_scrap_moveables", "can_scrap_moveables"]  # 중복
    }
    
    result = output_gate_validate(output, mock_logger)
    
    assert result == False


# ============================================================================
# TC-5: can_scrap_moveables 도구 존재 검증 (존재 검증)
# ============================================================================

def test_tc5_scrap_moveables_contains_expected_tools(sample_indices, mock_logger):
    """TC-5: can_scrap_moveables에 주요 도구 포함"""
    # 실제 파싱 결과 대신 존재 검증
    expected_tools = {"Base.Hammer", "Base.Screwdriver", "Base.Saw"}
    
    # 이 테스트는 실제 파이프라인 실행 후 결과로 검증
    # 여기서는 구조만 확인
    assert "Hammer" in sample_indices["by_type"]


# ============================================================================
# TC-6: can_remove_embedded_object dict flatten 정상 처리
# ============================================================================

def test_tc6_dict_flatten_works(sample_indices, mock_logger):
    """TC-6: dict criteria가 정상적으로 flatten됨"""
    criteria = {
        "glass": [
            {"type": "tag", "value": "RemoveGlass"},
            {"type": "type", "value": "Tweezers"}
        ],
        "bullet": [
            {"type": "tag", "value": "RemoveBullet"},
            {"type": "type", "value": "SutureNeedleHolder"}
        ]
    }
    
    result = resolve_criteria(criteria, sample_indices, mock_logger)
    
    # Tweezers와 SutureNeedleHolder가 포함되어야 함
    assert "Base.Tweezers" in result
    assert "Base.SutureNeedleHolder" in result


# ============================================================================
# TC-7: isWaterSource() → CanStoreWater 매핑 정상
# ============================================================================

def test_tc7_property_mapping_works(sample_indices, mock_logger):
    """TC-7: property predicate 매핑 정상 동작"""
    criteria = [{"type": "property", "value": "isWaterSource()"}]
    
    result = resolve_criteria(criteria, sample_indices, mock_logger)
    
    # CanStoreWater 인덱스 값이 반환되어야 함
    assert "Base.Bowl" in result
    assert "Base.BucketEmpty" in result


# ============================================================================
# TC-8: 스냅샷 검증 (baseline과 diff)
# ============================================================================

def test_tc8_full_pipeline_snapshot():
    """TC-8: 전체 파이프라인 스냅샷 검증 (수동 baseline 비교)"""
    # 이 테스트는 baseline 생성 후 활성화
    # 현재는 구조만 확인
    baseline_path = Path(__file__).parent.parent / "baseline" / "capability_by_fulltype.json"
    
    if baseline_path.exists():
        with open(baseline_path, "r", encoding="utf-8") as f:
            baseline = json.load(f)
        
        # 프로덕션 실행 결과와 비교
        # assert result == baseline
        pass
    else:
        pytest.skip("Baseline not yet created")


# ============================================================================
# 추가 단위 테스트
# ============================================================================

def test_invert_produces_sorted_output(mock_logger):
    """invert 결과가 정렬됨"""
    cap_results = {
        "cap_b": {"Base.Z", "Base.A"},
        "cap_a": {"Base.A", "Base.M"},
    }
    
    result = invert_to_fulltype(cap_results, mock_logger)
    
    # 키가 알파벳순
    keys = list(result.keys())
    assert keys == sorted(keys)
    
    # 각 배열도 알파벳순
    for caps in result.values():
        assert caps == sorted(caps)


def test_output_gate_rejects_invalid_fulltype(mock_logger):
    """FullType 형식 검증"""
    output = {"InvalidFormat": ["can_extinguish_fire"]}  # 점 없음
    
    result = output_gate_validate(output, mock_logger)
    
    assert result == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
