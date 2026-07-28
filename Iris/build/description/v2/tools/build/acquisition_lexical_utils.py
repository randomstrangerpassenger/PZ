from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


SURFACE_PATTERN_VALUES = (
    "BARE_NOUN_CHAIN",
    "TRANSLATION_COMPOUND",
    "OVERLY_GENERIC",
    "GAME_INTERNAL_TERM",
    "JOSA_MISSING",
    "ACCEPTABLE",
)

DISPOSITION_VALUES = (
    "KEEP_AS_IS",
    "CANONICAL_LEXICON_REWRITE",
    "RAW_SOURCE_REPAIR",
    "STANDARDIZATION_IMPOSSIBLE_CANDIDATE",
)

MODE_VALUES = ("location", "method", "discovery", "mixed", "unknown")
BOOTSTRAP_STATUS_VALUES = ("mapped", "needs_manual_review", "unmapped")

METHOD_KEYWORDS = (
    "얻는다",
    "제작한다",
    "제작해",
    "제작으로",
    "조합해",
    "조합으로",
    "조리한다",
    "분해해",
    "분해로",
    "개조해",
    "주조해",
    "가공해",
    "수리한다",
    "손질해",
    "섞어",
    "으깨",
    "채워",
    "담아",
    "비워",
    "붙여",
    "잘라",
    "열어",
    "열거나",
    "찢어",
    "준비한다",
    "만든다",
    "만들어",
)

DISCOVERY_KEYWORDS = (
    "구할 수 있다",
    "찾을 수 있다",
    "채집으로 구할 수 있다",
)

LOCATION_KEYWORDS = ("발견된다",)

GENERIC_PHRASES = (
    "여러 장소",
    "여러 곳",
    "다양한 곳",
    "각종 장소",
    "어디서나",
)

SUSPICIOUS_TRANSLATION_PATTERNS = (
    "취급 선반",
    "선반 장소",
    "취급 선반 장소",
    "보관 선반",
    "작업 장소",
    "작업 구역",
    "판매 장소",
)

LOCATION_NOUN_HINTS = (
    "창고",
    "차고",
    "주방",
    "작업장",
    "보관 장소",
    "취급 장소",
    "진열대",
    "매장",
    "가정집",
    "시설",
    "차량",
    "상자",
    "선반",
    "작업대",
)

REPEATED_LOCATION_LABEL_HINTS = (
    "취급 장소",
    "보관 장소",
    "진열대",
    "상자",
    "선반",
    "차량",
    "매장",
)

ASCII_INTERNAL_TERM_RE = re.compile(r"(?:[A-Z][a-z0-9]+){2,}|[A-Za-z_]{4,}")
LEADING_CONNECTOR_RE = re.compile(r"^(?:또는|및)\s+")
SUFFIX_AREA_COMPONENT_RE = re.compile(r"[가-힣A-Za-z0-9]+(?: [가-힣A-Za-z0-9]+){0,7} (?:보관 장소|취급 장소)")

EXACT_AREA_COMPONENT_REWRITES: dict[str, tuple[str, ...]] = {
    "작업 차량": ("작업용 차량",),
    "작업 차량과 생존 차량": ("작업용 차량", "생존 차량"),
    "발전기실 또는 작업 차량": ("발전기실", "작업용 차량"),
    "주방과 조리 작업 장소": ("주방", "조리 공간"),
    "청소 작업 장소와 세탁 작업 장소": ("청소실", "세탁실"),
    "욕실과 배관 자재 장소": ("욕실", "배관 자재 코너"),
    "전자제품 매대와 전기공 작업 구역": ("전자제품 매대", "전기 설비 구역"),
    "조리 작업 장소": ("조리 공간",),
    "청소 작업 장소": ("청소실",),
    "세탁 작업 장소": ("세탁실",),
    "금속 작업 장소": ("금속 작업장",),
    "전기공 작업 구역": ("전기 설비 구역",),
    "공구 판매 장소": ("공구점",),
    "장신구 취급 장소": ("장신구 코너",),
    "장신구 보관 장소": ("장신구 코너",),
    "총기 취급 장소": ("총기 코너",),
    "시계 취급 장소": ("시계 코너",),
    "안경 취급 장소": ("안경 코너",),
    "원예 용품 취급 장소": ("원예 용품 코너",),
    "캠핑 장비 취급 장소": ("캠핑 장비 코너",),
    "낚시 장비 취급 장소": ("낚시 장비 코너",),
    "무전 장비 취급 장소": ("무전 장비 코너",),
    "야외 조리 장비 취급 장소": ("야외 조리 장비 코너",),
    "침구 취급 장소": ("침구 코너",),
    "학교와 체육관 보관 장소": ("학교 사물함", "체육관 사물함"),
    "군과 경찰 무기 보관 장소": ("군경 무기고",),
    "군과 경찰 총기 보관 장소": ("군경 총기 보관함",),
    "군과 경찰 보관 장소": ("군경 장비 보관함",),
    "군용과 소방 보관 장소": ("군용 보관함", "소방 보관함"),
    "군용 무기 보관 장소와 총기 보관 장소": ("군용 무기고", "총기 보관함"),
    "사냥 장비 보관 장소나 가정 총기 보관 장소": ("사냥 장비 코너", "가정용 총기 보관함"),
    "전자 공구 보관 장소나 전기 부품 보관 장소": ("전자 공구 코너", "전기 부품 코너"),
    "문구 보관 장소나 사무용품 보관 장소": ("문구 코너", "사무용품 코너"),
    "의상 보관 장소와 의류 보관 장소": ("의상 코너", "의류 코너"),
    "냉동 식품 보관 장소와 식기 보관 장소": ("냉동 식품 코너", "식기 코너"),
    "사물함과 의류 보관 장소": ("사물함", "의류 코너"),
    "의류 보관 장소와 병원 보관 장소": ("의류 코너", "병원 비품함"),
    "의류 보관 장소 또는 소방 보관 장소": ("의류 코너", "소방 장비 보관함"),
    "의류 보관 장소 또는 수영장 보관 장소": ("의류 코너", "수영장 사물함"),
    "의류 보관 장소 또는 학교와 체육관 보관 장소": ("의류 코너", "학교 사물함", "체육관 사물함"),
    "의류 보관 장소 또는 체육관 보관 장소": ("의류 코너", "체육관 사물함"),
    "차고 총기 보관 장소 또는 은닉 보관 장소": ("차고 총기 보관함", "은닉 보관함"),
    "공구점과 잡화 보관 장소": ("공구점", "잡화 코너"),
    "작업장과 공구 보관 장소": ("작업장", "공구 코너"),
    "작업장과 안전 장비 보관 장소": ("작업장", "안전 장비 코너"),
    "도축 작업 장소와 식기 보관 장소": ("도축 작업장", "식기 코너"),
    "제과 작업 장소와 식기 보관 장소": ("제과 작업장", "식기 코너"),
    "주방이나 전기 공구 보관 장소": ("주방", "전기 공구 코너"),
    "음향 기기 판매점이나 전자용품 보관 장소": ("음향 기기 판매점", "전자용품 코너"),
    "전자용품점이나 공구 보관 장소": ("전자용품점", "공구 코너"),
    "전자용품점이나 전기 부품 보관 장소": ("전자용품점", "전기 부품 코너"),
    "재봉 용품점이나 재봉 자재 보관 장소": ("재봉 용품점", "재봉 용품 코너"),
    "군용품점과 겨울 의류 보관 장소": ("군용품점", "겨울 의류 코너"),
    "군용품점과 캠핑 장비 보관 장소": ("군용품점", "캠핑 장비 코너"),
    "스포츠 장비 장소와 잡화 보관 장소": ("스포츠 장비 코너", "잡화 코너"),
    "스포츠 장비 장소와 코스튬 보관 장소": ("스포츠 장비 코너", "코스튬 코너"),
    "사무용품과 학용품 보관 장소": ("사무용품 코너", "학용품 코너"),
    "경찰과 경비 보관 장소": ("경찰 장비 보관함", "경비 장비 보관함"),
    "경찰과 교도관 보관 장소": ("경찰 장비 보관함", "교도관 장비 보관함"),
    "체육관과 경찰 보관 장소": ("체육관 사물함", "경찰 장비 보관함"),
    "학교 또는 학교 보관 장소": ("학교", "학교 사물함"),
    "체육관 또는 학교 보관 장소": ("체육관 사물함", "학교 사물함"),
}

STORAGE_STEM_EXACT_REWRITES: dict[str, str] = {
    "사진 자재": "사진 용품 코너",
    "재봉 자재": "재봉 용품 코너",
    "격식 의류": "정장 코너",
    "골프": "골프 용품 코너",
    "학교": "학교 사물함",
    "체육관": "체육관 사물함",
    "수영장": "수영장 사물함",
    "병원": "병원 비품함",
    "의료": "의료 비품함",
    "의료 물품": "의료 비품함",
    "소방": "소방 장비 보관함",
    "경찰": "경찰 장비 보관함",
    "교도관": "교도관 장비 보관함",
    "군용": "군용품 보관함",
    "군 의료": "군 의료 비품함",
    "군 항공": "군 항공 장비 보관함",
    "군용 장비": "군용 장비 보관함",
    "군용 전자": "군용 전자 장비 보관함",
    "보안 장비": "보안 장비 보관함",
    "차고 총기": "차고 총기 보관함",
    "가정 총기": "가정용 총기 보관함",
    "은닉": "은닉 보관함",
    "무장 은신처": "무장 은신처 보관함",
    "정비": "정비 장비 보관함",
    "볼링장": "볼링장 락커",
    "볼링장 신발": "볼링장 신발장",
    "연습실 의상": "연습실 의상 보관함",
    "스피포 상품": "스피포 상품 코너",
    "축제 물품": "축제 물품 코너",
    "의상": "의상 코너",
}

AREA_STEM_ALIAS: dict[str, str] = {
    "사진 자재": "사진 용품",
    "재봉 자재": "재봉 용품",
    "격식 의류": "정장",
    "골프": "골프 용품",
}

SALES_AREA_STEM_EXACT_REWRITES: dict[str, str] = {
    "공구": "공구점",
}

STORAGE_CONTAINER_HINTS = (
    "총기",
    "보안",
    "은닉",
    "경찰",
    "교도관",
    "소방",
    "군용",
    "군 ",
    "정비",
    "연료",
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False))
            handle.write("\n")


def has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def dedupe_preserve_order(values: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = normalize_text(value)
        if not normalized or normalized in seen:
            continue
        deduped.append(normalized)
        seen.add(normalized)
    return deduped


def strip_leading_connector(text: str) -> str:
    return normalize_text(LEADING_CONNECTOR_RE.sub("", normalize_text(text)))


def _extract_nested_area_components(text: str) -> list[str]:
    matches = [normalize_text(match.group(0)) for match in SUFFIX_AREA_COMPONENT_RE.finditer(text)]
    if len(matches) <= 1:
        return []
    return dedupe_preserve_order(matches)


def naturalize_storage_area_stem(stem: str) -> str:
    normalized_stem = normalize_text(stem)
    if normalized_stem in STORAGE_STEM_EXACT_REWRITES:
        return STORAGE_STEM_EXACT_REWRITES[normalized_stem]

    aliased_stem = AREA_STEM_ALIAS.get(normalized_stem, normalized_stem)
    if aliased_stem.endswith(("매장", "상점", "점", "판매점", "차량", "차고", "작업장", "시설", "사물함")):
        return aliased_stem
    if any(hint in aliased_stem for hint in STORAGE_CONTAINER_HINTS):
        return f"{aliased_stem} 보관함"
    return f"{aliased_stem} 코너"


def naturalize_access_area_stem(stem: str) -> str:
    normalized_stem = normalize_text(stem)
    aliased_stem = AREA_STEM_ALIAS.get(normalized_stem, normalized_stem)
    if aliased_stem.endswith(("매장", "상점", "점", "판매점", "차량", "차고", "작업장", "시설", "사물함")):
        return aliased_stem
    return f"{aliased_stem} 코너"


def naturalize_sales_area_stem(stem: str) -> str:
    normalized_stem = normalize_text(stem)
    if normalized_stem in SALES_AREA_STEM_EXACT_REWRITES:
        return SALES_AREA_STEM_EXACT_REWRITES[normalized_stem]

    aliased_stem = AREA_STEM_ALIAS.get(normalized_stem, normalized_stem)
    if aliased_stem.endswith(("매장", "상점", "점", "판매점", "판매대", "매대")):
        return aliased_stem
    return f"{aliased_stem} 코너"


def naturalize_area_place_stem(stem: str) -> str:
    normalized_stem = normalize_text(stem)
    aliased_stem = AREA_STEM_ALIAS.get(normalized_stem, normalized_stem)
    if aliased_stem.endswith(
        ("매장", "상점", "점", "판매점", "차량", "차고", "작업장", "시설", "사물함", "실", "구역", "공간")
    ):
        return aliased_stem
    return f"{aliased_stem} 코너"


def naturalize_acquisition_component(raw_text: str, component_type: str) -> list[str]:
    normalized = strip_leading_connector(raw_text)
    if not normalized:
        return []

    exact_rewrite = EXACT_AREA_COMPONENT_REWRITES.get(normalized)
    if exact_rewrite is not None:
        return list(exact_rewrite)

    nested_components = _extract_nested_area_components(normalized)
    if nested_components:
        naturalized_nested: list[str] = []
        for component in nested_components:
            nested_type = "access_area" if component.endswith("취급 장소") else "storage_area"
            naturalized_nested.extend(naturalize_acquisition_component(component, nested_type))
        return dedupe_preserve_order(naturalized_nested)

    if component_type == "storage_area" and normalized.endswith("보관 장소"):
        stem = normalized[: -len("보관 장소")].strip()
        return [naturalize_storage_area_stem(stem)]
    if component_type == "access_area" and normalized.endswith("취급 장소"):
        stem = normalized[: -len("취급 장소")].strip()
        return [naturalize_access_area_stem(stem)]
    if component_type == "sales_area" and normalized.endswith("판매 장소"):
        stem = normalized[: -len("판매 장소")].strip()
        return [naturalize_sales_area_stem(stem)]
    if component_type == "area_place" and normalized.endswith("장소"):
        stem = normalized[: -len("장소")].strip()
        return [naturalize_area_place_stem(stem)]
    if component_type == "work_area" and normalized.endswith("작업 장소"):
        stem = normalized[: -len("작업 장소")].strip()
        return [naturalize_area_place_stem(stem)]
    if component_type == "work_zone" and normalized.endswith("작업 구역"):
        stem = normalized[: -len("작업 구역")].strip()
        return [naturalize_area_place_stem(stem)]
    return [normalized]


def naturalize_acquisition_components(component_entries: list[dict[str, Any]]) -> list[str]:
    naturalized: list[str] = []
    for entry in component_entries:
        raw_text = str(entry.get("raw_text") or "").strip()
        component_type = str(entry.get("component_type") or "").strip()
        if not raw_text or not component_type:
            continue
        naturalized.extend(naturalize_acquisition_component(raw_text, component_type))
    return dedupe_preserve_order(naturalized)


def extract_acquisition_origins(facts_row: dict[str, Any]) -> list[str]:
    fact_origin = facts_row.get("fact_origin")
    if not isinstance(fact_origin, dict):
        return []
    acquisition_origin = fact_origin.get("acquisition_hint")
    if isinstance(acquisition_origin, list):
        return [str(entry) for entry in acquisition_origin if str(entry).strip()]
    if isinstance(acquisition_origin, str) and acquisition_origin.strip():
        return [acquisition_origin]
    return []


def infer_acquisition_mode(text: str) -> str:
    normalized = normalize_text(text)
    has_method = any(keyword in normalized for keyword in METHOD_KEYWORDS)
    has_discovery = any(keyword in normalized for keyword in DISCOVERY_KEYWORDS)
    has_location = any(keyword in normalized for keyword in LOCATION_KEYWORDS)

    signal_count = sum(1 for flag in (has_method, has_discovery, has_location) if flag)
    if signal_count > 1:
        return "mixed"
    if has_method:
        return "method"
    if has_discovery:
        return "discovery"
    if has_location:
        return "location"
    return "unknown"


def count_repeated_location_label_hints(text: str) -> int:
    normalized = normalize_text(text)
    return sum(normalized.count(hint) for hint in REPEATED_LOCATION_LABEL_HINTS)


def classify_acquisition_surface_pattern(text: str) -> str:
    normalized = normalize_text(text)
    if not normalized:
        return "ACCEPTABLE"

    if ASCII_INTERNAL_TERM_RE.search(normalized) and not any("가" <= char <= "힣" for char in normalized):
        return "GAME_INTERNAL_TERM"
    if any(pattern in normalized for pattern in GENERIC_PHRASES):
        return "OVERLY_GENERIC"
    if any(pattern in normalized for pattern in SUSPICIOUS_TRANSLATION_PATTERNS):
        return "TRANSLATION_COMPOUND"

    mode = infer_acquisition_mode(normalized)
    repeated_location_label_count = count_repeated_location_label_hints(normalized)
    if mode in {"location", "discovery", "mixed"} and repeated_location_label_count >= 2:
        return "TRANSLATION_COMPOUND"
    if mode == "unknown":
        if any(keyword in normalized for keyword in LOCATION_NOUN_HINTS):
            return "JOSA_MISSING"
        if len(normalized.split()) >= 2:
            return "BARE_NOUN_CHAIN"
    return "ACCEPTABLE"


def recommend_disposition(pattern_code: str) -> str:
    if pattern_code == "ACCEPTABLE":
        return "KEEP_AS_IS"
    if pattern_code in {"BARE_NOUN_CHAIN", "JOSA_MISSING"}:
        return "CANONICAL_LEXICON_REWRITE"
    if pattern_code in {"TRANSLATION_COMPOUND", "OVERLY_GENERIC"}:
        return "RAW_SOURCE_REPAIR"
    return "STANDARDIZATION_IMPOSSIBLE_CANDIDATE"


def determine_bootstrap_status(*, pattern_code: str, mode: str) -> str:
    if pattern_code == "ACCEPTABLE" and mode != "unknown":
        return "mapped"
    if pattern_code in {"BARE_NOUN_CHAIN", "JOSA_MISSING", "TRANSLATION_COMPOUND", "OVERLY_GENERIC"}:
        return "needs_manual_review"
    return "unmapped"


def infer_phrase_family(text: str) -> str:
    normalized = normalize_text(text)
    mode = infer_acquisition_mode(normalized)
    repeated_location_label_count = count_repeated_location_label_hints(normalized)

    if mode == "discovery" and repeated_location_label_count >= 2:
        return "seed_discovery_phrase_with_label_repeat"
    if mode == "discovery":
        return "seed_discovery_phrase"
    if repeated_location_label_count >= 2:
        return "seed_label_repeat"
    if mode == "location":
        return "seed_location_phrase"
    if mode == "method":
        return "seed_method_phrase"
    if mode == "mixed":
        return "seed_mixed_phrase"
    return "seed_other_phrase"


def build_provisional_canonical_key(*, text: str, mode: str) -> str | None:
    if mode == "unknown":
        return None
    digest = hashlib.sha1(normalize_text(text).encode("utf-8")).hexdigest()[:12]
    return f"legacy_{mode}_{digest}"
