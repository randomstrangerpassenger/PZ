"""
Registry Utilities — 공용 헬퍼
================================
use_case_registry의 rule_props에서 최종 use_case_id를 해석하는 단일 함수.

모든 파이프라인 스크립트는 이 모듈의 resolve_use_case_id()를 통해서만
use_case_id를 해석해야 함 (인라인 해석 금지).
"""


def resolve_use_case_id(rule_props: dict) -> str:
    """Registry rule의 최종 use_case_id를 해석.

    alias_of가 있으면 alias_of를 반환 (1단 해석, 체인 금지 정책).
    alias_of가 없으면 use_case_id를 반환.
    둘 다 없으면 빈 문자열 반환.
    """
    return rule_props.get("alias_of", rule_props.get("use_case_id", ""))
