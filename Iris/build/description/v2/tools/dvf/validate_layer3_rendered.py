"""
validate_layer3_rendered.py — D+E단계 산출물 검증

D단계 (본문 검증): active↔text_ko, silent↔null, max_length_chars, 금지 어휘
E단계 (계층 경계): v1에서는 4·5계층만 검증
+ decision override_mode ↔ rendered source 교차 검증
+ override 비율 KPI
"""

import re
from typing import Any

JOSA_TOKEN_RE = re.compile(r'\{josa_[a-z_]+\}')


def validate_rendered(
    rendered: dict,
    decisions_list: list[dict],
    profiles: dict,
    forbidden_patterns: dict,
    override_ratio_limit: float = 0.30,
) -> dict:
    """
    rendered 산출물 검증.
    반환: {"pass": bool, "errors": [...], "warnings": [...]}
    """
    errors = []
    warnings = []

    entries = rendered.get('entries', {})
    decisions_map = {d['item_id']: d for d in decisions_list}

    for item_id, entry in entries.items():
        prefix = f"[{item_id}]"
        text_ko = entry.get('text_ko')
        source = entry.get('source')

        # source enum
        if source not in ('composed', 'override', 'silent'):
            errors.append(f"{prefix} source 유효하지 않음: '{source}'")
            continue

        # decision ↔ source 교차 검증
        decision = decisions_map.get(item_id)
        if decision:
            d_state = decision['state']
            d_override = decision.get('override_mode', 'none')

            if d_state == 'silent' and source != 'silent':
                errors.append(f"{prefix} decision=silent인데 source='{source}'")
            elif d_state == 'active' and d_override == 'text_ko' and source != 'override':
                errors.append(f"{prefix} decision=active+override인데 source='{source}'")
            elif d_state == 'active' and d_override == 'none' and source != 'composed':
                errors.append(f"{prefix} decision=active+compose인데 source='{source}'")

        # active ↔ text_ko 정합성
        if source in ('composed', 'override'):
            if text_ko is None or not text_ko.strip():
                errors.append(f"{prefix} active인데 text_ko 비어있음")
        elif source == 'silent':
            if text_ko is not None:
                errors.append(f"{prefix} silent인데 text_ko 존재")

        # 본문 품질 검증 (active만)
        if text_ko and source in ('composed', 'override'):
            # max_length_chars
            profile_name = decision.get('compose_profile') if decision else None
            profile = profiles.get(profile_name, {}) if profile_name else {}
            max_chars = profile.get('max_length_chars', 220)
            if len(text_ko) > max_chars:
                errors.append(f"{prefix} 본문 길이 초과: {len(text_ko)} > {max_chars}")

            # 금지어 검사
            for pat in forbidden_patterns.get('hard_fail_patterns', []):
                if pat in text_ko:
                    errors.append(f"{prefix} 금지어 감지: '{pat}'")

            for pat in forbidden_patterns.get('inference_patterns', []):
                if pat in text_ko:
                    errors.append(f"{prefix} 추정 표현 감지: '{pat}'")

            # 계층 경계 (v1: 4·5계층만)
            layer_boundary = forbidden_patterns.get('layer_boundary_patterns', {})
            for pat in layer_boundary.get('layer4_intrusion', []):
                if pat in text_ko:
                    errors.append(f"{prefix} 4계층 정보 침범: '{pat}'")
            for pat in layer_boundary.get('layer5_internal', []):
                if re.search(pat, text_ko):
                    errors.append(f"{prefix} 5계층 내부 정보 노출: '{pat}'")

            # josa 토큰 잔류
            josa = JOSA_TOKEN_RE.findall(text_ko)
            if josa:
                errors.append(f"{prefix} josa 토큰 잔류: {josa}")

            # 번역투
            for pat in forbidden_patterns.get('translationese_patterns', []):
                if pat in text_ko:
                    warnings.append(f"{prefix} 번역투 의심: '{pat}'")

    # override 비율 KPI
    total = len(entries)
    if total > 0:
        override_count = sum(1 for e in entries.values() if e.get('source') == 'override')
        ratio = override_count / total
        if ratio > override_ratio_limit:
            errors.append(
                f"override 비율 초과: {ratio:.1%} > {override_ratio_limit:.0%} "
                f"({override_count}/{total})"
            )

    return {
        "pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
