from __future__ import annotations

import re
from typing import Any

try:
    from .compose_layer3_blocks import has_text
except ImportError:
    from compose_layer3_blocks import has_text


def ensure_sentence(text: str) -> str:
    normalized = text.strip()
    if not normalized:
        return normalized
    if normalized[-1] in {".", "!", "?"}:
        return normalized
    return f"{normalized}."


def has_final_consonant(text: str) -> bool:
    if not text:
        return False
    char = text[-1]
    code = ord(char)
    if not (0xAC00 <= code <= 0xD7A3):
        return False
    return ((code - 0xAC00) % 28) != 0


def append_copula(noun: str) -> str:
    normalized = noun.strip()
    if not normalized:
        return normalized
    if normalized.endswith(("다", "이다")):
        return normalized
    if has_final_consonant(normalized):
        return f"{normalized}이다"
    return f"{normalized}다"


def render_identity_core_text(identity_hint: str) -> str:
    normalized = identity_hint.strip().rstrip(".!?")
    return ensure_sentence(append_copula(normalized))


def normalize_for_contains(text: str) -> str:
    return text.replace(" ", "").strip()


def context_core(context_hint: str) -> str:
    normalized = context_hint.strip()
    if normalized.endswith(" 작업"):
        return normalized[:-3].strip()
    return normalized


def derive_context_from_primary_use(primary_use: Any) -> str | None:
    if not has_text(primary_use):
        return None
    normalized = str(primary_use).strip()
    patterns = (
        r"^(.+?)에 쓰는 .+$",
        r"^(.+?)에 함께 쓰는 .+$",
        r"^(.+?)에 들어가는 .+$",
    )
    for pattern in patterns:
        match = re.match(pattern, normalized)
        if match:
            context = match.group(1).strip()
            if context:
                return context
    return None


def primary_use_covers_context(*, primary_use: Any, context_hint: Any) -> bool:
    if not has_text(primary_use) or not has_text(context_hint):
        return False
    haystack = normalize_for_contains(str(primary_use))
    needles = {
        normalize_for_contains(str(context_hint)),
        normalize_for_contains(context_core(str(context_hint))),
    }
    return any(needle and needle in haystack for needle in needles)
