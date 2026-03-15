"""
validate_layer3_decisions.py — 입력 정합성 검증

decisions validator는 입력 정합성만 검사. rendered 존재 여부는 보지 않는다.
  - state↔필드 정합성
  - reason_code enum
  - override 계약 (text_ko 필수)
  - facts ↔ decisions 양방향 교차 검증
"""

ACTIVE_REASON_CODES = {
    'HAS_ITEM_SPECIFIC_PRACTICAL_INFO',
    'HAS_NON_TRIVIAL_ACQUISITION_CONTEXT',
    'HAS_SPECIAL_PROCESSING_CONTEXT',
}

SILENT_REASON_CODES = {
    'L1_L2_ALREADY_SUFFICIENT',
    'NO_ITEM_SPECIFIC_LAYER3_PAYLOAD',
    'DATA_INSUFFICIENT',
    'INTENTIONAL_OMIT',
}

ALL_REASON_CODES = ACTIVE_REASON_CODES | SILENT_REASON_CODES

VALID_PROFILES = {
    'medical_consumable', 'herb_food_remedy', 'tool_interaction',
    'storage_container', 'fuel_container', 'misc_generic',
    'acq_location', 'acq_method', 'identity_acq', 'use_acq',
}

GLOBAL_REQUIRED_SLOTS = {'identity_hint'}


def validate_decisions(
    decisions_list: list[dict],
    facts_list: list[dict],
    profiles: dict,
) -> dict:
    """
    decisions 검증.
    반환: {"pass": bool, "errors": [...], "warnings": [...]}
    """
    errors = []
    warnings = []
    seen_ids = set()

    facts_ids = {f['item_id'] for f in facts_list}
    decision_ids = set()

    for idx, d in enumerate(decisions_list):
        item_id = d.get('item_id', f'<unknown-{idx}>')
        prefix = f"[{item_id}]"

        # item_id 유일성
        if item_id in seen_ids:
            errors.append(f"{prefix} item_id 중복")
        seen_ids.add(item_id)
        decision_ids.add(item_id)

        state = d.get('state')
        reason_code = d.get('reason_code')
        override_mode = d.get('override_mode', 'none')

        # state 유효성
        if state not in ('active', 'silent'):
            errors.append(f"{prefix} state 유효하지 않음: '{state}'")
            continue

        # reason_code enum
        if reason_code not in ALL_REASON_CODES:
            errors.append(f"{prefix} reason_code 유효하지 않음: '{reason_code}'")

        # state ↔ reason_code 정합성
        if state == 'active' and reason_code not in ACTIVE_REASON_CODES:
            errors.append(f"{prefix} active인데 silent reason_code: '{reason_code}'")
        if state == 'silent' and reason_code not in SILENT_REASON_CODES:
            errors.append(f"{prefix} silent인데 active reason_code: '{reason_code}'")

        if state == 'active':
            # compose_profile 필수
            profile = d.get('compose_profile')
            if not profile:
                errors.append(f"{prefix} active인데 compose_profile 누락")
            elif profile not in profiles:
                errors.append(f"{prefix} 알 수 없는 compose_profile: '{profile}'")

            # facts_ref 필수
            facts_ref = d.get('facts_ref')
            if not facts_ref:
                errors.append(f"{prefix} active인데 facts_ref 누락")
            elif facts_ref not in facts_ids:
                errors.append(f"{prefix} facts_ref가 facts에 없음: '{facts_ref}'")

            # 전역 필수 슬롯 검증 (facts에서)
            facts_entry = next((f for f in facts_list if f['item_id'] == item_id), None)
            if facts_entry:
                for slot in GLOBAL_REQUIRED_SLOTS:
                    val = facts_entry.get(slot)
                    if val is None or (isinstance(val, str) and not val.strip()):
                        errors.append(f"{prefix} 전역 필수 슬롯 '{slot}' 누락/비어있음")

                # required_any 검증
                if profile and profile in profiles:
                    req_any = profiles[profile].get('required_any', [])
                    if req_any:
                        has_any = any(
                            facts_entry.get(s) is not None and str(facts_entry.get(s, '')).strip()
                            for s in req_any
                        )
                        if not has_any:
                            errors.append(f"{prefix} required_any 슬롯 전부 null: {req_any}")

            # override 계약
            if override_mode == 'text_ko':
                if not d.get('manual_override_text_ko'):
                    errors.append(f"{prefix} override인데 manual_override_text_ko 누락")
            elif override_mode == 'none':
                if d.get('manual_override_text_ko') is not None:
                    errors.append(f"{prefix} override_mode=none인데 override_text 존재")
            elif override_mode != 'none' and override_mode != 'text_ko':
                errors.append(f"{prefix} override_mode 유효하지 않음: '{override_mode}'")

        elif state == 'silent':
            # silent 제약
            if d.get('compose_profile') is not None:
                errors.append(f"{prefix} silent인데 compose_profile 존재")
            if override_mode != 'none':
                errors.append(f"{prefix} silent인데 override_mode != none")
            if d.get('manual_override_text_ko') is not None:
                errors.append(f"{prefix} silent인데 override_text 존재")

            # silent + facts 존재 → WARN
            if item_id in facts_ids:
                warnings.append(f"{prefix} silent인데 facts에 데이터가 존재함")

        # --- acquisition_null_reason 교차 검증 (state 무관, facts 존재 시만) ---
        acq_null_reason = d.get('acquisition_null_reason')
        valid_acq_reasons = {'STANDARDIZATION_IMPOSSIBLE', 'UBIQUITOUS_ITEM'}

        # enum 유효성
        if acq_null_reason is not None and acq_null_reason not in valid_acq_reasons:
            errors.append(f"{prefix} acquisition_null_reason 유효하지 않음: '{acq_null_reason}'")

        facts_entry_for_acq = next((f for f in facts_list if f['item_id'] == item_id), None)
        if facts_entry_for_acq is not None:
            acq_hint = facts_entry_for_acq.get('acquisition_hint')
            if acq_hint is None:
                # acquisition_hint가 null → reason 필수
                if acq_null_reason is None:
                    errors.append(f"{prefix} acquisition_hint=null인데 acquisition_null_reason 누락")
            else:
                # acquisition_hint가 non-null → reason은 null이어야 함
                if acq_null_reason is not None:
                    errors.append(f"{prefix} acquisition_hint 존재인데 acquisition_null_reason이 non-null: '{acq_null_reason}'")

    # 양방향 교차 검증
    # 정방향: decisions(active)에 있는데 facts에 없음
    for d in decisions_list:
        if d['state'] == 'active':
            facts_ref = d.get('facts_ref')
            if facts_ref and facts_ref not in facts_ids:
                pass  # 이미 위에서 검사

    # 역방향: facts에 있는데 decisions에 없음
    for fid in facts_ids:
        if fid not in decision_ids:
            errors.append(f"[{fid}] facts에 있는데 decisions에 없음")

    return {
        "pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
