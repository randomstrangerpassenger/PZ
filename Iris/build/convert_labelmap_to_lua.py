#!/usr/bin/env python3
"""
convert_labelmap_to_lua.py

JSON 라벨맵 → IrisUseCaseLabelMap.lua 변환.

규칙:
  1. usecase_label_map.json 읽기
  2. usecases_by_fulltype.v2.4.json에서 실제 use_case_id 집합 추출
  3. 커버리지 FAIL-LOUD: 실제 use_case_id ⊆ JSON 키 아니면 exit(1)
  4. plain UTF-8 그대로 Lua에 출력 (바이트 이스케이프 금지)
  5. UTF-8 round-trip 검증
  6. SURFACE/STRENGTH/UNIQUENESS도 plain UTF-8로 통일

auto-only 계약: 단순 치환만, 조건분기/추론 금지.
"""

import re
import sys
from pathlib import Path

# ─── 경로 설정 ───────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from tools.common.versions import BUILD_VERSION

DATA_DIR = SCRIPT_DIR / "data" / BUILD_VERSION
LABELMAP_JSON = DATA_DIR / "usecase_label_map.json"
USECASES_JSON = SCRIPT_DIR.parent / "output" / f"usecases_by_fulltype.{BUILD_VERSION}.json"
OUTPUT_LUA = SCRIPT_DIR.parent / "media" / "lua" / "client" / "Iris" / "Data" / "IrisUseCaseLabelMap.lua"

from tools.common.io import load_json


def extract_use_case_ids(usecases_data: dict) -> set[str]:
    """usecases_by_fulltype.v2.4.json에서 모든 use_case_id 추출."""
    ids = set()
    fulltypes = usecases_data.get("fulltypes", {})
    for ft_data in fulltypes.values():
        for uc in ft_data.get("use_cases", []):
            ucid = uc.get("use_case_id")
            if ucid:
                ids.add(ucid)
    return ids


def coverage_check(actual_ids: set[str], label_keys: set[str]) -> list[str]:
    """커버리지 FAIL-LOUD: actual ⊆ label_keys 검사.
    
    Returns:
        누락된 ID 리스트 (비어있으면 통과)
    """
    missing = actual_ids - label_keys
    return sorted(missing)


def lua_string(s: str) -> str:
    """Python 문자열을 Lua 문자열 리터럴로. plain UTF-8, 이스케이프 최소."""
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def generate_lua(labelmap: dict) -> str:
    """라벨맵 데이터 → Lua 소스코드 생성."""
    labels = labelmap["labels"]
    surface = labelmap["surface_labels"]
    strength = labelmap["strength_labels"]
    uniqueness = labelmap["uniqueness_labels"]

    lines = []
    lines.append("-- Iris UseCase Label Map (i18n)")
    lines.append("-- 런타임에서 label_key → 표시 문자열 단순 치환용")
    lines.append("-- 자동 생성: convert_labelmap_to_lua.py")
    lines.append("-- 조건분기/추론 금지: 키→문자열 lookup만 수행")
    lines.append("")
    lines.append("local IrisUseCaseLabelMap = {}")
    lines.append("")

    # ── KO labels ──
    lines.append("-- use_case_id → 표시 문자열 (KO)")
    lines.append("IrisUseCaseLabelMap.KO = {")
    for ucid in sorted(labels.keys()):
        ko = labels[ucid]["KO"]
        lines.append(f'    [{lua_string(ucid)}] = {lua_string(ko)},')
    lines.append("}")
    lines.append("")

    # ── EN labels ──
    lines.append("-- use_case_id → 표시 문자열 (EN)")
    lines.append("IrisUseCaseLabelMap.EN = {")
    for ucid in sorted(labels.keys()):
        en = labels[ucid]["EN"]
        lines.append(f'    [{lua_string(ucid)}] = {lua_string(en)},')
    lines.append("}")
    lines.append("")

    # ── SURFACE ──
    lines.append("-- surface 키 → 표시 문자열")
    lines.append("IrisUseCaseLabelMap.SURFACE_KO = {")
    for key in sorted(surface.keys()):
        lines.append(f'    {key} = {lua_string(surface[key]["KO"])},')
    lines.append("}")
    lines.append("")
    lines.append("IrisUseCaseLabelMap.SURFACE_EN = {")
    for key in sorted(surface.keys()):
        lines.append(f'    {key} = {lua_string(surface[key]["EN"])},')
    lines.append("}")
    lines.append("")

    # ── STRENGTH ──
    lines.append("-- strength 키 → 표시 문자열")
    lines.append("IrisUseCaseLabelMap.STRENGTH_KO = {")
    for key in sorted(strength.keys()):
        lines.append(f'    {key} = {lua_string(strength[key]["KO"])},')
    lines.append("}")
    lines.append("")
    lines.append("IrisUseCaseLabelMap.STRENGTH_EN = {")
    for key in sorted(strength.keys()):
        lines.append(f'    {key} = {lua_string(strength[key]["EN"])},')
    lines.append("}")
    lines.append("")

    # ── UNIQUENESS ──
    lines.append("-- uniqueness 키 → 표시 문자열")
    lines.append("IrisUseCaseLabelMap.UNIQUENESS_KO = {")
    for key in sorted(uniqueness.keys()):
        lines.append(f'    {key} = {lua_string(uniqueness[key]["KO"])},')
    lines.append("}")
    lines.append("")
    lines.append("IrisUseCaseLabelMap.UNIQUENESS_EN = {")
    for key in sorted(uniqueness.keys()):
        lines.append(f'    {key} = {lua_string(uniqueness[key]["EN"])},')
    lines.append("}")
    lines.append("")
    lines.append("return IrisUseCaseLabelMap")
    lines.append("")

    return "\n".join(lines)


def round_trip_verify(lua_path: Path, labelmap: dict) -> list[str]:
    """UTF-8 round-trip 검증: Lua 파일에서 테이블별 문자열 추출 → 원본과 비교.
    
    Returns:
        오류 메시지 리스트 (비어있으면 통과)
    """
    errors = []
    content = lua_path.read_text(encoding="utf-8")

    # 테이블별로 파싱 — IrisUseCaseLabelMap.XXX = { ... } 블록 추출
    table_pattern = re.compile(
        r'IrisUseCaseLabelMap\.(\w+)\s*=\s*\{([^}]*)\}', re.DOTALL
    )
    # 각 블록 내 key=value 추출
    entry_pattern = re.compile(
        r'(?:\["([^"]+)"\]|(\w+))\s*=\s*"((?:[^"\\]|\\.)*)"'
    )

    tables: dict[str, dict[str, str]] = {}
    for tm in table_pattern.finditer(content):
        table_name = tm.group(1)  # KO, EN, SURFACE_KO, ...
        block = tm.group(2)
        entries = {}
        for em in entry_pattern.finditer(block):
            key = em.group(1) or em.group(2)
            value = em.group(3).replace('\\"', '"').replace("\\\\", "\\")
            entries[key] = value
        tables[table_name] = entries

    # ── use_case_id 라벨 검증 ──
    labels = labelmap["labels"]
    for table_key, lang in [("KO", "KO"), ("EN", "EN")]:
        tbl = tables.get(table_key, {})
        for ucid, lang_map in labels.items():
            expected = lang_map[lang]
            actual = tbl.get(ucid)
            if actual is None:
                errors.append(f"  Missing in {table_key}: {ucid}")
            elif actual != expected:
                errors.append(
                    f"  Round-trip mismatch: {ucid}({lang}) "
                    f"expected={expected!r} actual={actual!r}"
                )

    # ── surface/strength/uniqueness 검증 ──
    section_table_map = [
        ("surface_labels", [("SURFACE_KO", "KO"), ("SURFACE_EN", "EN")]),
        ("strength_labels", [("STRENGTH_KO", "KO"), ("STRENGTH_EN", "EN")]),
        ("uniqueness_labels", [("UNIQUENESS_KO", "KO"), ("UNIQUENESS_EN", "EN")]),
    ]
    for section_name, pairs in section_table_map:
        section_data = labelmap[section_name]
        for table_key, lang in pairs:
            tbl = tables.get(table_key, {})
            if not tbl:
                errors.append(f"  Table {table_key} not found in output")
                continue
            for key, lang_map in section_data.items():
                expected = lang_map[lang]
                actual = tbl.get(key)
                if actual is None:
                    errors.append(f"  Missing in {table_key}: {key}")
                elif actual != expected:
                    errors.append(
                        f"  Round-trip mismatch: {key}({table_key}) "
                        f"expected={expected!r} actual={actual!r}"
                    )

    # ── 엔트리 개수 검증 ──
    ko_tbl = tables.get("KO", {})
    en_tbl = tables.get("EN", {})
    expected_count = len(labels)
    if len(ko_tbl) != expected_count:
        errors.append(f"  KO entry count: expected={expected_count}, actual={len(ko_tbl)}")
    if len(en_tbl) != expected_count:
        errors.append(f"  EN entry count: expected={expected_count}, actual={len(en_tbl)}")

    return errors


def main():
    print("=" * 60)
    print("convert_labelmap_to_lua.py")
    print("=" * 60)

    # ── Step 1: JSON 로드 ──
    print("\n[1/5] Loading JSON files...")
    if not LABELMAP_JSON.exists():
        print(f"  FAIL: {LABELMAP_JSON} not found")
        sys.exit(1)
    labelmap = load_json(LABELMAP_JSON)
    label_keys = set(labelmap["labels"].keys())
    print(f"  Label map: {len(label_keys)} entries")

    # ── Step 2: 실제 use_case_id 추출 ──
    print("\n[2/5] Extracting use_case_ids from usecases_by_fulltype...")
    if not USECASES_JSON.exists():
        print(f"  FAIL: {USECASES_JSON} not found")
        sys.exit(1)
    usecases = load_json(USECASES_JSON)
    actual_ids = extract_use_case_ids(usecases)
    print(f"  Actual use_case_ids: {len(actual_ids)}")

    # ── Step 3: 커버리지 FAIL-LOUD ──
    print("\n[3/5] Coverage check (FAIL-LOUD)...")
    missing = coverage_check(actual_ids, label_keys)
    if missing:
        print(f"  FAIL: {len(missing)} use_case_id(s) missing from label map:")
        for m in missing:
            print(f"    - {m}")
        print("\n  Coverage FAILED. Add missing IDs to usecase_label_map.json.")
        sys.exit(1)
    print(f"  PASS: all {len(actual_ids)} actual IDs covered")

    # 라벨맵에만 있고 실제로 사용되지 않는 ID (경고만)
    extra = label_keys - actual_ids
    if extra:
        print(f"  INFO: {len(extra)} extra label(s) not in current usecases:")
        for e in sorted(extra):
            print(f"    - {e}")

    # ── Step 4: Lua 생성 + 쓰기 ──
    print(f"\n[4/5] Generating Lua file...")
    lua_content = generate_lua(labelmap)
    OUTPUT_LUA.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_LUA.write_text(lua_content, encoding="utf-8")
    print(f"  Written: {OUTPUT_LUA}")
    print(f"  Size: {len(lua_content)} bytes")

    # ── Step 5: UTF-8 round-trip 검증 ──
    print(f"\n[5/5] UTF-8 round-trip verification...")
    errors = round_trip_verify(OUTPUT_LUA, labelmap)
    if errors:
        print(f"  FAIL: {len(errors)} round-trip error(s):")
        for e in errors:
            print(e)
        sys.exit(1)
    print("  PASS: round-trip OK")

    print("\n" + "=" * 60)
    print("SUCCESS: IrisUseCaseLabelMap.lua generated")
    print("=" * 60)


if __name__ == "__main__":
    main()
