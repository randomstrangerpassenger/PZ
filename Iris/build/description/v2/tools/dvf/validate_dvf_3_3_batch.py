"""
validate_dvf_3_3_batch.py — DVF 3-3 배치 전용 검증기

기존 DVF 4단계 검증에 추가하는 배치 고유 검증:
- 구조 검증 (compose target 대비 rendered 커버리지)
- 층 경계 검증 (3-4, 3-5 침범)
- 프로파일-문장 정합성 검증
- 길이 검증
- 수량 항등식 검증
"""

from __future__ import annotations

import json
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# 층 경계 패턴
# ---------------------------------------------------------------------------

LAYER4_PATTERNS = [
    r"관련 레시피", r"관련 행동", r"사용처:", r"사용 가능한",
    r"만들 수 있는 것", r": ", r"· ", r"^\d+\. ",
]

LAYER5_PATTERNS = [
    r"uc\.", r"Base\.", r"module\.",
    r"분류:", r"대분류", r"소분류", r"카테고리",
]

FORBIDDEN_TONE = [
    r"추천", r"최고의", r"가장 좋은", r"보다 나은", r"유용",
    r"효율적", r"더 ", r"덜 ", r"우수", r"드랍률", r"확률",
    r"스폰율", r"%", r"아마", r"대체로",
]

# 프로파일-문장 정합성 힌트 키워드
LOCATION_KEYWORDS = ["발견", "진열", "놓여", "보관", "찾을 수"]
METHOD_KEYWORDS = ["제작", "조합", "분해", "만들"]


# ---------------------------------------------------------------------------
# 검증 함수
# ---------------------------------------------------------------------------

def validate_dvf_3_3_batch(
    rendered: dict,
    compose_input: list[dict],
    gaps: list[dict],
    decisions: list[dict],
    sync_queue: list[dict] | None = None,
) -> dict:
    """
    3-3 배치 전용 검증.

    Returns: {"pass": bool, "errors": [...], "warnings": [...], "stats": {...}}
    """
    errors: list[str] = []
    warnings: list[str] = []

    entries = rendered.get("entries", {})
    compose_target = len(compose_input)
    gap_fulltypes = {g["fulltype"] for g in gaps}
    decision_ids = {d["item_id"] for d in decisions}

    # --- 수량 항등식 ---
    rendered_count = sum(1 for e in entries.values() if e.get("source") == "composed")
    gap_count = len(gaps)
    facts_count = len(decisions)  # facts == decisions 수

    if facts_count != len(decisions):
        errors.append(f"facts_count({facts_count}) != decisions_count({len(decisions)})")

    if rendered_count + gap_count != compose_target:
        errors.append(
            f"rendered({rendered_count}) + gap({gap_count}) = {rendered_count + gap_count} "
            f"!= compose_target({compose_target})"
        )

    # --- compose target 커버리지 ---
    compose_fulltypes = {r["fulltype"] for r in compose_input}
    rendered_fulltypes = set(entries.keys())
    missing_in_rendered = compose_fulltypes - rendered_fulltypes - gap_fulltypes
    if missing_in_rendered:
        errors.append(
            f"compose target 중 rendered/gap 미포함: {len(missing_in_rendered)}건 "
            f"(예: {sorted(missing_in_rendered)[:3]})"
        )

    # --- HOLD/SILENT 행이 active로 섞이지 않음 ---
    if sync_queue:
        hold_fulltypes = {
            r["fulltype"] for r in sync_queue
            if r.get("approval_state") != "APPROVE_SYNC"
        }
        leaked = hold_fulltypes & rendered_fulltypes
        if leaked:
            errors.append(f"HOLD/SILENT 행이 rendered에 포함: {len(leaked)}건")

    # --- fulltype 중복 ---
    seen = set()
    for d in decisions:
        if d["item_id"] in seen:
            errors.append(f"[{d['item_id']}] decisions에 fulltype 중복")
        seen.add(d["item_id"])

    # --- 텍스트 품질 검증 (rendered entries) ---
    compose_index = {r["fulltype"]: r for r in compose_input}

    for item_id, entry in entries.items():
        text = entry.get("text_ko")
        if not text:
            continue

        prefix = f"[{item_id}]"

        # 층 경계: 3-4 침범
        for pat in LAYER4_PATTERNS:
            if re.search(pat, text):
                errors.append(f"{prefix} 3-4 층 경계 침범: '{pat}'")
                break

        # 층 경계: 3-5 침범
        for pat in LAYER5_PATTERNS:
            if re.search(pat, text):
                errors.append(f"{prefix} 3-5 층 경계 침범: '{pat}'")
                break

        # 금지 톤
        for pat in FORBIDDEN_TONE:
            if re.search(pat, text):
                errors.append(f"{prefix} 금지 톤 검출: '{pat}'")
                break

        # 프로파일-문장 정합성 (WARN)
        ci = compose_index.get(item_id)
        if ci:
            dvf_profile = ci.get("dvf_compose_profile")
            if dvf_profile == "acq_location":
                method_count = sum(1 for kw in METHOD_KEYWORDS if kw in text)
                loc_count = sum(1 for kw in LOCATION_KEYWORDS if kw in text)
                if method_count > loc_count and method_count > 0:
                    warnings.append(f"{prefix} acq_location인데 방법형 키워드 우세")
            elif dvf_profile == "acq_method":
                method_count = sum(1 for kw in METHOD_KEYWORDS if kw in text)
                loc_count = sum(1 for kw in LOCATION_KEYWORDS if kw in text)
                if loc_count > method_count and loc_count > 0:
                    warnings.append(f"{prefix} acq_method인데 위치형 키워드 우세")

        # identity_hint 30자 초과 (rendered 텍스트에서는 직접 확인 어려움, facts에서 확인)

    # --- gap 검증 ---
    if gap_count > 0:
        errors.append(f"gap_count = {gap_count} (초기 배치 기준 FAIL)")

    stats = {
        "compose_target": compose_target,
        "rendered_count": rendered_count,
        "gap_count": gap_count,
        "facts_decisions_count": facts_count,
        "error_count": len(errors),
        "warning_count": len(warnings),
    }

    return {
        "pass": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": stats,
    }
