"""
validate_layer3_facts.py — A+B단계 검증

A단계 (구조 검증): 스키마, item_id 유일성, fact_origin/slot_meta 정합성
B단계 (슬롯 검증): 허용 슬롯 8개, 타입 string|null, 문자수, 금지어, josa 토큰, 4계층 침입
"""

import json
import re
from pathlib import Path
from typing import Any


ALLOWED_SLOTS = {
    'identity_hint', 'acquisition_hint', 'primary_use', 'secondary_use',
    'processing_hint', 'special_context', 'limitation_hint', 'notes',
}
GLOBAL_REQUIRED_SLOTS = {'identity_hint'}
SLOT_CHAR_WARN = 80
SLOT_CHAR_FAIL = 120
JOSA_TOKEN_RE = re.compile(r'\{josa_[a-z_]+\}')
NON_DECIMAL_PERIOD_RE = re.compile(r'(?<!\d)\.(?!\d)')


def _get_nonnull_slot_keys(entry: dict) -> set[str]:
    """non-null 슬롯 키 집합."""
    keys = set()
    for slot in ALLOWED_SLOTS:
        val = entry.get(slot)
        if val is not None:
            keys.add(slot)
    return keys


def validate_facts(
    facts_list: list[dict],
    forbidden_patterns: dict,
    decisions_list: list[dict] | None = None,
) -> dict:
    """
    facts 검증.
    반환: {"pass": bool, "errors": [...], "warnings": [...]}
    """
    errors = []
    warnings = []
    seen_ids = set()

    for idx, entry in enumerate(facts_list):
        item_id = entry.get('item_id', f'<unknown-{idx}>')
        prefix = f"[{item_id}]"

        # --- A단계: 구조 검증 ---

        # item_id 유일성
        if item_id in seen_ids:
            errors.append(f"{prefix} item_id 중복")
        seen_ids.add(item_id)

        # item_id 존재
        if not entry.get('item_id'):
            errors.append(f"{prefix} item_id 누락")
            continue

        # 허용되지 않은 필드
        known_fields = ALLOWED_SLOTS | {'item_id', 'slot_meta', 'fact_origin'}
        extra_fields = set(entry.keys()) - known_fields
        if extra_fields:
            errors.append(f"{prefix} 허용되지 않은 필드: {extra_fields}")

        # fact_origin 필수
        if 'fact_origin' not in entry:
            errors.append(f"{prefix} fact_origin 누락")

        # fact_origin 키 = non-null 슬롯 키
        nonnull_keys = _get_nonnull_slot_keys(entry)
        origin = entry.get('fact_origin', {})
        if origin:
            origin_keys = set(origin.keys())
            if origin_keys != nonnull_keys:
                missing = nonnull_keys - origin_keys
                extra = origin_keys - nonnull_keys
                if missing:
                    errors.append(f"{prefix} fact_origin에 누락된 키: {missing}")
                if extra:
                    errors.append(f"{prefix} fact_origin에 초과 키 (null 슬롯): {extra}")

        # slot_meta 키 ⊆ non-null 슬롯 키
        slot_meta = entry.get('slot_meta')
        if slot_meta:
            meta_keys = set(slot_meta.keys())
            extra_meta = meta_keys - nonnull_keys
            if extra_meta:
                errors.append(f"{prefix} slot_meta 키가 null 슬롯 참조: {extra_meta}")

        # --- B단계: 슬롯 검증 ---
        for slot_name in ALLOWED_SLOTS:
            val = entry.get(slot_name)
            if val is None:
                continue

            # 타입 체크
            if not isinstance(val, str):
                errors.append(f"{prefix}.{slot_name} 타입 오류: string이어야 함 (got {type(val).__name__})")
                continue

            # 슬롯 값 계약: 줄바꿈 금지
            if '\n' in val:
                errors.append(f"{prefix}.{slot_name} 줄바꿈 포함 (슬롯 값은 단일 절이어야 함)")

            # 슬롯 값 계약: 비소수점 마침표 금지 (template이 종결 마침표 부여)
            if NON_DECIMAL_PERIOD_RE.search(val):
                errors.append(f"{prefix}.{slot_name} 비소수점 마침표 감지 (슬롯 값에 문장 종결 마침표 금지)")

            # 문자수
            length = len(val)
            if length > SLOT_CHAR_FAIL:
                errors.append(f"{prefix}.{slot_name} 문자수 초과: {length} > {SLOT_CHAR_FAIL}")
            elif length > SLOT_CHAR_WARN:
                warnings.append(f"{prefix}.{slot_name} 문자수 경고: {length} > {SLOT_CHAR_WARN}")

            # 금지어 검사
            hard_fail = forbidden_patterns.get('hard_fail_patterns', [])
            for pattern in hard_fail:
                if pattern in val:
                    errors.append(f"{prefix}.{slot_name} 금지어 감지: '{pattern}'")

            inference = forbidden_patterns.get('inference_patterns', [])
            for pattern in inference:
                if pattern in val:
                    errors.append(f"{prefix}.{slot_name} 추정 표현 감지: '{pattern}'")

            # warning_patterns (4계층 침입)
            warn_pats = forbidden_patterns.get('warning_patterns', [])
            for pattern in warn_pats:
                if pattern in val:
                    errors.append(f"{prefix}.{slot_name} 4계층 정보 침범: '{pattern}'")

            # 5계층 내부 메타 노출
            layer5_pats = forbidden_patterns.get('layer_boundary_patterns', {}).get('layer5_internal', [])
            for pattern in layer5_pats:
                if re.search(pattern, val):
                    errors.append(f"{prefix}.{slot_name} 5계층 내부 정보 노출: '{pattern}'")

            # josa 토큰 잔류
            josa_matches = JOSA_TOKEN_RE.findall(val)
            if josa_matches:
                errors.append(f"{prefix}.{slot_name} josa 토큰 잔류: {josa_matches}")

    return {
        "pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
