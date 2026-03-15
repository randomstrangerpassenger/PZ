"""
postproc_ko.py — 한국어 후처리 모듈 (v1)

v1 구현:
  - 이중 공백 제거
  - 연속 마침표 정리
  - 문장 끝 마침표 보장
  - 동일 종결 어미 3+ 연속 WARN

v2 인터페이스 (빈 구현):
  - 종성 판별
  - 조사 매핑

v1 조사 처리 계약:
  sentence_plan template에 {josa_xxx} 포함 금지.
  슬롯 참조는 {slot_name} 형태만 허용.
  postproc_ko의 {josa_xxx} 잔류 탐지는 비정상 데이터 유입 방어용.
"""

import re
from typing import Optional


# ---------------------------------------------------------------------------
# v1 후처리 함수
# ---------------------------------------------------------------------------

def remove_double_spaces(text: str) -> str:
    """연속된 공백을 단일 공백으로 축소."""
    return re.sub(r' {2,}', ' ', text)


def normalize_periods(text: str) -> str:
    """연속 마침표(.. 이상)를 단일 마침표로. 말줄임표(…)는 보존."""
    # 먼저 … (U+2026) 보존
    text = re.sub(r'\.{2,}', '.', text)
    return text


def ensure_trailing_period(text: str) -> str:
    """문장 끝에 마침표가 없으면 추가."""
    text = text.rstrip()
    if text and text[-1] not in '.!?':
        text += '.'
    return text


def clean_period_spacing(text: str) -> str:
    """마침표 뒤 공백 정리. ". " 패턴 통일."""
    # ". " 이 아닌 "." 뒤에 한글/영문이 바로 오면 ". "로 변환
    text = re.sub(r'\.(?=[가-힣A-Za-z])', '. ', text)
    # ". " 뒤의 추가 공백 제거
    text = re.sub(r'\. {2,}', '. ', text)
    return text


def postprocess_ko(text: str) -> str:
    """
    v1 한국어 후처리 파이프라인.
    순서: 이중공백 제거 → 마침표 정리 → 공백 정리 → 끝 마침표 보장.
    """
    if not text or not text.strip():
        return text

    text = text.strip()
    text = remove_double_spaces(text)
    text = normalize_periods(text)
    text = clean_period_spacing(text)
    text = ensure_trailing_period(text)
    return text


# ---------------------------------------------------------------------------
# 종결 어미 반복 탐지 (WARN)
# ---------------------------------------------------------------------------

_ENDING_PATTERNS = [
    r'할 수 있다',
    r'사용된다',
    r'쓰인다',
    r'필요하다',
    r'가능하다',
    r'된다',
]


def detect_ending_repetition(text: str, threshold: int = 3) -> list[str]:
    """
    동일 종결 어미가 threshold회 이상 반복되면 경고 목록 반환.
    반환: ["~할 수 있다 x3", ...] 형태의 경고 문자열 리스트.
    """
    warnings = []
    for pattern in _ENDING_PATTERNS:
        count = len(re.findall(pattern, text))
        if count >= threshold:
            warnings.append(f"'{pattern}' x{count}")
    return warnings


# ---------------------------------------------------------------------------
# {josa_xxx} 토큰 잔류 탐지
# ---------------------------------------------------------------------------

_JOSA_TOKEN_RE = re.compile(r'\{josa_[a-z_]+\}')


def detect_josa_tokens(text: str) -> list[str]:
    """
    비정상 {josa_xxx} 토큰 잔류 탐지.
    v1에서는 정상 경로에서 토큰이 생성되지 않으므로,
    이 함수가 결과를 반환하면 비정상 데이터 유입을 의미.
    """
    return _JOSA_TOKEN_RE.findall(text)


# ---------------------------------------------------------------------------
# v2 인터페이스 (빈 구현)
# ---------------------------------------------------------------------------

def has_jongseong(char: str) -> Optional[bool]:
    """
    한글 문자의 종성(받침) 존재 여부 판별.
    v2에서 구현 예정. v1에서는 None 반환.
    """
    # v2 구현 시: 유니코드 한글 음절 분해
    # code = ord(char)
    # if 0xAC00 <= code <= 0xD7A3:
    #     return (code - 0xAC00) % 28 != 0
    return None


def select_particle(preceding_char: str, particle_pair: tuple[str, str]) -> Optional[str]:
    """
    선행 문자의 종성에 따라 조사 선택.
    particle_pair: (종성 있을 때, 종성 없을 때) 예: ("은", "는")
    v2에서 구현 예정. v1에서는 None 반환.
    """
    return None
