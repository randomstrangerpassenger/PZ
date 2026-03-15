"""
run_dvf_layer3.py — 통합 DVF 검증 진입점

4단계 순차 실행:
[1/4] 입력 검증 — facts/decisions 스키마 + 교차 + 금지어
[2/4] 조합 실행 — (run_pipeline에서 수행, DVF는 검증만)
[3/4] rendered 검증 — 구조/경계/길이/금지어/override비율
[4/4] 결정론 검증 — entries SHA-256 비교

DVF는 3계층 본문 전용 엔진이다. 툴팁은 후속 별도 시스템으로 분리됨.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'build'))

from validate_layer3_facts import validate_facts
from validate_layer3_decisions import validate_decisions
from validate_layer3_rendered import validate_rendered


def run_dvf(
    facts_list: list[dict],
    decisions_list: list[dict],
    profiles: dict,
    forbidden_patterns: dict,
    rendered: dict,
    compose_fn=None,
) -> dict:
    """
    DVF 통합 검증.

    Args:
        compose_fn: 결정론 검증용 조합 함수 (재실행).
                    None이면 결정론 검증 건너뜀.

    반환: {"pass": bool, "stages": {1..4: result}, "errors": [...], "warnings": [...]}
    """
    all_errors = []
    all_warnings = []
    stages = {}

    # [1/4] 입력 검증
    r1_facts = validate_facts(facts_list, forbidden_patterns, decisions_list)
    r1_decisions = validate_decisions(decisions_list, facts_list, profiles)

    stage1 = {
        "pass": r1_facts["pass"] and r1_decisions["pass"],
        "errors": r1_facts["errors"] + r1_decisions["errors"],
        "warnings": r1_facts["warnings"] + r1_decisions["warnings"],
    }
    stages["1_input"] = stage1
    all_errors.extend(stage1["errors"])
    all_warnings.extend(stage1["warnings"])

    if not stage1["pass"]:
        return _final(False, stages, all_errors, all_warnings)

    # [3/4] rendered 검증
    r3 = validate_rendered(rendered, decisions_list, profiles, forbidden_patterns)
    stages["3_rendered"] = r3
    all_errors.extend(r3["errors"])
    all_warnings.extend(r3["warnings"])

    if not r3["pass"]:
        return _final(False, stages, all_errors, all_warnings)

    # [4/4] 결정론성 검증
    if compose_fn:
        r4 = _verify_determinism(
            facts_list, decisions_list, profiles, rendered, compose_fn
        )
        stages["4_determinism"] = r4
        all_errors.extend(r4["errors"])
        all_warnings.extend(r4["warnings"])

        if not r4["pass"]:
            return _final(False, stages, all_errors, all_warnings)
    else:
        stages["4_determinism"] = {
            "pass": True, "errors": [],
            "warnings": ["결정론 검증 건너뜀 (compose_fn 미제공)"],
        }

    return _final(True, stages, all_errors, all_warnings)


def _verify_determinism(
    facts_list, decisions_list, profiles, rendered, compose_fn
) -> dict:
    """동일 입력 재실행 → entries SHA-256 비교."""
    from compose_layer3_text import entries_sha256

    errors = []

    original_hash = entries_sha256(rendered.get('entries', {}))
    re_entries = compose_fn(facts_list, decisions_list, profiles)
    re_hash = entries_sha256(re_entries)

    if original_hash != re_hash:
        errors.append(
            f"결정론성 실패: 원본 SHA={original_hash[:16]}... "
            f"재실행 SHA={re_hash[:16]}..."
        )

    return {"pass": len(errors) == 0, "errors": errors, "warnings": []}


def _final(passed, stages, errors, warnings):
    return {"pass": passed, "stages": stages, "errors": errors, "warnings": warnings}
