"""
compose_layer3_text.py — 3계층 조합기 본체

sentence_plan 블록 단위 조합:
1. sentence_plan 블록 순회
2. 블록 내 non-null 슬롯 수집 → partial 키 알고리즘
3. template_full / template_partial[key] 선택 → {slot_name} 치환
4. required 블록 전 슬롯 null → HARD FAIL
5. optional 블록 전 슬롯 null → 블록 생략
6. 블록 간 연결: 공백 1개 (template이 마침표로 끝남)
7. postproc_ko 후처리
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from postproc_ko import postprocess_ko


# ---------------------------------------------------------------------------
# 데이터 로더
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> list[dict]:
    """JSONL 파일 로드. 빈 줄 무시."""
    entries = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def load_json(path: Path) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def file_sha256(path: Path) -> str:
    """파일 전체 SHA-256."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# 슬롯 허용 목록
# ---------------------------------------------------------------------------

ALLOWED_SLOTS = [
    'identity_hint', 'acquisition_hint', 'primary_use', 'secondary_use',
    'processing_hint', 'special_context', 'limitation_hint', 'notes',
]


# ---------------------------------------------------------------------------
# Partial 키 구성 알고리즘
# ---------------------------------------------------------------------------

def build_partial_key(non_null_slot_names: list[str]) -> str:
    """
    non-null 슬롯 이름 목록에서 partial 키 생성.
    1개: '{name}_only'
    2개+: '{a}+{b}+...'
    """
    if len(non_null_slot_names) == 1:
        return f"{non_null_slot_names[0]}_only"
    return "+".join(non_null_slot_names)


# ---------------------------------------------------------------------------
# 단일 블록 렌더링
# ---------------------------------------------------------------------------

def render_block(block: dict, facts: dict) -> str | None:
    """
    sentence_plan 블록 1개를 렌더링.
    반환: 렌더링된 문자열 또는 None (생략).
    예외: required 블록의 전 슬롯이 null이면 ValueError.
    """
    slots = block['slots']
    required = block['required']

    # facts에서 해당 슬롯 값 수집
    non_null = []
    for slot_name in slots:
        val = facts.get(slot_name)
        if val is not None and str(val).strip():
            non_null.append(slot_name)

    # 전 슬롯 null
    if not non_null:
        if required:
            raise ValueError(
                f"Required block slots {slots} are all null for item '{facts.get('item_id', '?')}'"
            )
        return None  # optional 블록 생략

    # 단일 슬롯 블록 (template 사용)
    if len(slots) == 1:
        template = block['template']
        return template.replace(f"{{{slots[0]}}}", str(facts[slots[0]]))

    # 다중 슬롯 블록
    if len(non_null) == len(slots):
        # 전 슬롯 non-null → template_full
        template = block['template_full']
    else:
        # 부분 null → template_partial
        key = build_partial_key(non_null)
        partial_map = block.get('template_partial', {})
        if key not in partial_map:
            raise ValueError(
                f"Missing partial template key '{key}' for block slots {slots} "
                f"(item '{facts.get('item_id', '?')}')"
            )
        template = partial_map[key]

    # {slot_name} 치환
    result = template
    for slot_name in slots:
        val = facts.get(slot_name)
        if val is not None:
            result = result.replace(f"{{{slot_name}}}", str(val))

    return result


# ---------------------------------------------------------------------------
# 아이템 1개 조합
# ---------------------------------------------------------------------------

def compose_item(
    facts: dict,
    decision: dict,
    profiles: dict,
) -> dict:
    """
    단일 아이템의 3계층 텍스트 조합.
    반환: {"text_ko": str|None, "source": "composed"|"override"|"silent"}
    """
    state = decision['state']

    # silent
    if state == 'silent':
        return {"text_ko": None, "source": "silent"}

    # override
    override_mode = decision.get('override_mode', 'none')
    if override_mode == 'text_ko':
        text = decision['manual_override_text_ko']
        return {"text_ko": postprocess_ko(text), "source": "override"}

    # compose
    profile_name = decision['compose_profile']
    if profile_name not in profiles:
        raise ValueError(
            f"Unknown profile '{profile_name}' for item '{facts.get('item_id', '?')}'"
        )

    profile = profiles[profile_name]
    sentence_plan = profile['sentence_plan']

    # 블록별 렌더링
    rendered_blocks = []
    for block in sentence_plan:
        rendered = render_block(block, facts)
        if rendered is not None:
            rendered_blocks.append(rendered)

    if not rendered_blocks:
        raise ValueError(
            f"No blocks rendered for active item '{facts.get('item_id', '?')}'"
        )

    # 블록 간 공백 1개로 연결
    text = " ".join(rendered_blocks)

    # postproc_ko 후처리
    text = postprocess_ko(text)

    return {"text_ko": text, "source": "composed"}


# ---------------------------------------------------------------------------
# 전체 조합
# ---------------------------------------------------------------------------

def compose_all(
    facts_list: list[dict],
    decisions_list: list[dict],
    profiles: dict,
) -> dict[str, dict]:
    """
    전체 아이템 조합. facts와 decisions를 item_id로 조인.
    반환: {item_id: {"text_ko": ..., "source": ...}}
    """
    facts_map = {f['item_id']: f for f in facts_list}
    decisions_map = {d['item_id']: d for d in decisions_list}

    entries = {}
    for item_id, decision in decisions_map.items():
        facts = facts_map.get(item_id, {})
        facts['item_id'] = item_id  # ensure item_id present
        entry = compose_item(facts, decision, profiles)
        entries[item_id] = entry

    return entries


# ---------------------------------------------------------------------------
# 빌드 산출물 생성
# ---------------------------------------------------------------------------

def build_rendered(
    facts_path: Path,
    decisions_path: Path,
    profiles_path: Path,
    output_path: Path,
) -> dict:
    """
    전체 파이프라인 조합 실행.
    layer3_rendered.json 저장 후 결과 반환.
    """
    facts_list = load_jsonl(facts_path)
    decisions_list = load_jsonl(decisions_path)
    profiles = load_json(profiles_path)

    entries = compose_all(facts_list, decisions_list, profiles)

    # 통계
    total = len(entries)
    composed_count = sum(1 for e in entries.values() if e['source'] == 'composed')
    override_count = sum(1 for e in entries.values() if e['source'] == 'override')
    silent_count = sum(1 for e in entries.values() if e['source'] == 'silent')
    override_ratio = override_count / total if total > 0 else 0.0

    rendered = {
        "meta": {
            "version": "2.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "facts_sha256": file_sha256(facts_path),
            "profiles_sha256": file_sha256(profiles_path),
            "stats": {
                "total": total,
                "active_composed": composed_count,
                "active_override": override_count,
                "silent": silent_count,
                "override_ratio": round(override_ratio, 4),
            },
        },
        "entries": entries,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(rendered, f, ensure_ascii=False, indent=2)

    return rendered


def entries_sha256(entries: dict) -> str:
    """entries 블록의 결정론적 SHA-256. meta 제외."""
    canonical = json.dumps(entries, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
