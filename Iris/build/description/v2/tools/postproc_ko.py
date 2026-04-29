"""
postproc_ko.py — 한국어 후처리 모듈 (v1)
"""

from __future__ import annotations

import re
from typing import Optional


def remove_double_spaces(text: str) -> str:
    return re.sub(r" {2,}", " ", text)


def normalize_periods(text: str) -> str:
    return re.sub(r"\.{2,}", ".", text)


def ensure_trailing_period(text: str) -> str:
    text = text.rstrip()
    if text and text[-1] not in ".!?":
        text += "."
    return text


def clean_period_spacing(text: str) -> str:
    text = re.sub(r"\.(?=[가-힣A-Za-z])", ". ", text)
    text = re.sub(r"\. {2,}", ". ", text)
    return text


def postprocess_ko(text: str) -> str:
    if not text or not text.strip():
        return text
    text = text.strip()
    text = remove_double_spaces(text)
    text = normalize_periods(text)
    text = clean_period_spacing(text)
    return ensure_trailing_period(text)


_ENDING_PATTERNS = [
    r"할 수 있다",
    r"사용된다",
    r"쓰인다",
    r"필요하다",
    r"가능하다",
    r"된다",
]


def detect_ending_repetition(text: str, threshold: int = 3) -> list[str]:
    warnings = []
    for pattern in _ENDING_PATTERNS:
        count = len(re.findall(pattern, text))
        if count >= threshold:
            warnings.append(f"{pattern} x{count}")
    return warnings


_JOSA_TOKEN_RE = re.compile(r"\{josa_[a-z_]+\}")


def detect_josa_tokens(text: str) -> list[str]:
    return _JOSA_TOKEN_RE.findall(text)


def has_jongseong(char: str) -> Optional[bool]:
    return None


def select_particle(preceding_char: str, particle_pair: tuple[str, str]) -> Optional[str]:
    return None
