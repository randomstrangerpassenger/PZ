"""
Right-Click Capability Pipeline
===============================
B41 정적 스캔 기반 7개 Capability → capability_by_fulltype.json 산출

Usage:
    python pipeline.py                    # 프로덕션 모드 (Gate-2 통과 필수)
    python pipeline.py --skip-gate2       # 개발 모드 (dry_run, output 미생성)
"""

import json
import re
import logging
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Any, Optional, Tuple
from datetime import datetime

# ============================================================================
# Phase 0: 환경 고정
# ============================================================================

# 디렉토리 경로
SCRIPT_DIR = Path(__file__).parent.resolve()
IRIS_DIR = SCRIPT_DIR.parent.parent  # evidence/rightclick/ -> Iris/
INPUT_DIR = IRIS_DIR / "input"
OUTPUT_DIR = IRIS_DIR / "output"
LOGS_DIR = IRIS_DIR / "logs"
BASELINE_DIR = IRIS_DIR / "baseline"

# MEDIA_ROOT (B41 고정)
MEDIA_ROOT = Path(r"G:\Program Files (x86)\Steam\steamapps\common\ProjectZomboid\media")

# Capability Allowlist (7개, 고정)
CAPABILITY_ALLOWLIST = {
    "can_extinguish_fire",
    "can_add_generator_fuel",
    "can_scrap_moveables",
    "can_open_canned_food",
    "can_stitch_wound",
    "can_remove_embedded_object",
    "can_attach_weapon_mod",
}

# Evidence Type Allowlist
EVIDENCE_TYPE_ALLOWLIST = {
    "static_table",
    "explicit_predicate",
    "item_property",
    "item_tag",
    "item_type",
    "item_category",
    "item_display_category",
    "item_tag_or_type",
    "item_type_or_tag",
}

# Resolution Type → Index 매핑
RESOLUTION_TO_INDEX = {
    "type": "by_type",
    "tag": "by_tag",
    "property": "by_property_true",
    "category": "by_category",
    "display_category": "by_display_category",
}

# Property Predicate 매핑 테이블
PROPERTY_MAPPING = {
    "isWaterSource()": "CanStoreWater",
}

# 로거 설정
def setup_logger() -> logging.Logger:
    LOGS_DIR.mkdir(exist_ok=True)
    
    logger = logging.getLogger("rightclick_pipeline")
    logger.setLevel(logging.DEBUG)
    
    # 파일 핸들러
    fh = logging.FileHandler(
        LOGS_DIR / f"pipeline_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
        encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    
    # 콘솔 핸들러
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger


# ============================================================================
# Phase 1: 입력 로드 및 사전 검증
# ============================================================================

def load_items(logger: logging.Logger) -> Dict[str, Any]:
    """items_itemscript.json 로드"""
    path = INPUT_DIR / "items_itemscript.json"
    
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)
    
    if not isinstance(items, dict):
        raise ValueError("[FAIL] items_itemscript.json root is not dict")
    
    logger.info(f"[OK] Loaded items: {len(items)}")
    return items


def load_source_index(logger: logging.Logger) -> Dict[str, Any]:
    """rightclick_source_index.json 로드"""
    path = INPUT_DIR / "rightclick_source_index.json"
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if "meta" not in data or "version" not in data["meta"]:
        raise ValueError("[FAIL] source_index missing meta.version")
    
    if "capabilities" not in data:
        raise ValueError("[FAIL] source_index missing capabilities section")
    
    logger.info(f"[OK] Loaded capabilities: {len(data['capabilities'])}")
    return data


def parse_allowlist(logger: logging.Logger) -> Set[str]:
    """rightclick_capability_allowlist_v1.md에서 `can_xxx` 추출"""
    path = INPUT_DIR / "rightclick_capability_allowlist_v1.md"
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # `can_xxx` 패턴 추출
    pattern = r"`(can_[a-z_]+)`"
    matches = set(re.findall(pattern, content))
    
    if len(matches) == 0:
        raise ValueError("[FAIL] Allowlist parsed 0 capabilities")
    
    logger.info(f"[OK] Allowlist parsed: {len(matches)}")
    return matches


# ============================================================================
# Phase 2: Gate-1 - Allowlist/Evidence/Single-Source 검증
# ============================================================================

def gate1_validate(source_index: Dict, allowlist: Set[str], logger: logging.Logger) -> bool:
    """Gate-1: Allowlist, Evidence Type, Single-Source 검증"""
    capabilities = source_index["capabilities"]
    passed = True
    
    # 2-1. Allowlist 양방향 검증
    for cap_id in capabilities.keys():
        if cap_id not in allowlist:
            logger.error(f"[FAIL] Capability '{cap_id}' is not in allowlist")
            passed = False
    
    for cap_id in allowlist:
        if cap_id not in capabilities:
            logger.error(f"[FAIL] Allowlist capability '{cap_id}' missing from source_index")
            passed = False
    
    # 2-2. Evidence Type 검증
    for cap_id, cap_data in capabilities.items():
        ev_type = cap_data.get("evidence_type")
        if ev_type not in EVIDENCE_TYPE_ALLOWLIST:
            logger.error(f"[FAIL] Capability '{cap_id}' has invalid evidence_type: '{ev_type}'")
            passed = False
    
    # 2-3. Single-Source 검증
    for cap_id, cap_data in capabilities.items():
        if "primary_source" not in cap_data:
            logger.error(f"[FAIL] Capability '{cap_id}' has no primary_source")
            passed = False
        
        # sources 배열 체크 (있으면 > 1 검사)
        if "sources" in cap_data and len(cap_data["sources"]) > 1:
            logger.error(f"[FAIL] Capability '{cap_id}' has multiple sources: {len(cap_data['sources'])}")
            passed = False
    
    if passed:
        logger.info("[OK] Gate-1 passed: Allowlist, Evidence Type, Single-Source")
    
    return passed


# ============================================================================
# Phase 3: Gate-2 - Primary Source 파일 존재 검사
# ============================================================================

def gate2_validate(source_index: Dict, media_root: Path, logger: logging.Logger) -> bool:
    """Gate-2: Primary Source 파일 존재 검사"""
    capabilities = source_index["capabilities"]
    passed = True
    
    for cap_id, cap_data in capabilities.items():
        primary = cap_data.get("primary_source", {})
        file_path = primary.get("file", "")
        
        if not file_path:
            continue
        
        # 경로 결합
        full_path = media_root / file_path
        
        if not full_path.exists():
            logger.error(f"[FAIL] Source '{file_path}' for capability '{cap_id}' not found")
            passed = False
        else:
            logger.debug(f"[OK] Source verified: {file_path}")
    
    if passed:
        logger.info("[OK] Gate-2 passed: All source files exist")
    
    return passed


# ============================================================================
# Phase 4: 아이템 인덱스 구축
# ============================================================================

def build_indices(items: Dict[str, Any], logger: logging.Logger) -> Dict[str, Dict[str, Set[str]]]:
    """6종 역색인 구축"""
    indices = {
        "by_fulltype": {},
        "by_type": defaultdict(set),
        "by_tag": defaultdict(set),
        "by_property_true": defaultdict(set),
        "by_display_category": defaultdict(set),
        "by_category": defaultdict(set),
    }
    
    for fulltype, item_data in items.items():
        # by_fulltype
        indices["by_fulltype"][fulltype] = item_data
        
        # by_type (FullType suffix)
        if "." in fulltype:
            type_suffix = fulltype.split(".")[-1]
            indices["by_type"][type_suffix].add(fulltype)
        
        # by_tag
        tags = item_data.get("Tags", "")
        if tags:
            for tag in tags.split(";"):
                tag = tag.strip()
                if tag:
                    indices["by_tag"][tag].add(fulltype)
        
        # by_property_true (CanStoreWater 등)
        for prop_name in PROPERTY_MAPPING.values():
            if item_data.get(prop_name) == True or item_data.get(prop_name) == "true":
                indices["by_property_true"][prop_name].add(fulltype)
        
        # by_display_category
        display_cat = item_data.get("DisplayCategory", "")
        if display_cat:
            indices["by_display_category"][display_cat].add(fulltype)
        
        # by_category (단수 Category 필드)
        category = item_data.get("Category", "")
        if category:
            indices["by_category"][category].add(fulltype)
    
    logger.info(
        f"[OK] Index built: by_fulltype={len(indices['by_fulltype'])}, "
        f"by_type={len(indices['by_type'])}, by_tag={len(indices['by_tag'])}, "
        f"by_property_true={len(indices['by_property_true'])}, "
        f"by_display_category={len(indices['by_display_category'])}"
    )
    
    return indices


# ============================================================================
# Phase 5: Capability별 후보 FullType 집합 산출
# ============================================================================

def preprocess_lua(content: str) -> str:
    """Lua 주석 제거"""
    # 블록 주석 제거: --[[ ... --]]
    content = re.sub(r'--\[\[.*?--\]\]', '', content, flags=re.DOTALL)
    # 단일 라인 주석 제거
    content = re.sub(r'--(?!\[\[).*$', '', content, flags=re.MULTILINE)
    return content


def parse_scrap_moveables(media_root: Path, indices: Dict, logger: logging.Logger) -> Set[str]:
    """ISMoveableDefinitions.lua에서 도구 파싱 (can_scrap_moveables)"""
    lua_path = media_root / "lua" / "client" / "Moveables" / "ISMoveableDefinitions.lua"
    
    if not lua_path.exists():
        raise FileNotFoundError(f"[FAIL] ISMoveableDefinitions.lua not found at {lua_path}")
    
    with open(lua_path, "r", encoding="utf-8") as f:
        raw_content = f.read()
    
    # 주석 제거
    content = preprocess_lua(raw_content)
    
    # 라인별 분할 (원본 라인 번호 추적용)
    raw_lines = raw_content.split('\n')
    
    # 앵커 범위: load() 함수 (231-454)
    expected_range = (231, 454)
    
    tools = set()
    
    # addScrapDefinition 호출 패턴
    # addScrapDefinition("Material", output, "Base.Tool" or "Tag.XXX", ...)
    pattern = r'addScrapDefinition\s*\([^)]*\)'
    
    for match in re.finditer(pattern, content):
        # 호출 내용에서 도구 추출
        call = match.group(0)
        
        # "Base.XXX" 또는 "Tag.XXX" 추출
        ref_pattern = r'"(Base\.[^"]+|Tag\.[^"]+)"'
        refs = re.findall(ref_pattern, call)
        
        for ref in refs:
            if ref.startswith("Base."):
                tools.add(ref)
            elif ref.startswith("Tag."):
                tag_name = ref[4:]  # "Tag." 제거
                # by_tag 인덱스로 확장
                if tag_name in indices["by_tag"]:
                    tools.update(indices["by_tag"][tag_name])
    
    if len(tools) == 0:
        raise ValueError("[FAIL] can_scrap_moveables: 0 tools extracted (Fail-loud #6)")
    
    logger.info(f"[OK] can_scrap_moveables parsed: {len(tools)} tools")
    return tools


def resolve_criteria(criteria: Any, indices: Dict, logger: logging.Logger) -> Set[str]:
    """criteria를 기반으로 FullType 집합 산출"""
    results = set()
    
    # criteria 정규화
    if isinstance(criteria, list):
        items = criteria
    elif isinstance(criteria, dict):
        # dict인 경우 모든 value를 flatten
        items = []
        for v in criteria.values():
            if isinstance(v, list):
                items.extend(v)
    else:
        raise ValueError(f"[FAIL] Unsupported criteria type: {type(criteria)}")
    
    for item in items:
        res_type = item.get("type")
        value = item.get("value")
        
        if res_type == "type":
            # by_type 인덱스 사용
            if value in indices["by_type"]:
                results.update(indices["by_type"][value])
        
        elif res_type == "tag":
            # by_tag 인덱스 사용
            if value in indices["by_tag"]:
                results.update(indices["by_tag"][value])
        
        elif res_type == "property":
            # property predicate 매핑
            if value not in PROPERTY_MAPPING:
                raise ValueError(f"[FAIL] Unknown property predicate: {value} (Fail-loud #4)")
            prop_name = PROPERTY_MAPPING[value]
            if prop_name in indices["by_property_true"]:
                results.update(indices["by_property_true"][prop_name])
        
        elif res_type == "display_category":
            if value in indices["by_display_category"]:
                results.update(indices["by_display_category"][value])
        
        elif res_type == "category":
            if value in indices["by_category"]:
                results.update(indices["by_category"][value])
        
        else:
            raise ValueError(f"[FAIL] Unsupported resolution type: {res_type} (Fail-loud #4)")
    
    return results


def resolve_capabilities(
    source_index: Dict, 
    indices: Dict, 
    media_root: Path,
    items: Dict[str, Any],
    logger: logging.Logger
) -> Dict[str, Set[str]]:
    """7개 Capability별 후보 FullType 집합 산출"""
    capabilities = source_index["capabilities"]
    results = {}
    
    for cap_id, cap_data in capabilities.items():
        ev_type = cap_data.get("evidence_type")
        
        if ev_type == "static_table" and cap_id == "can_scrap_moveables":
            # 특수 처리: Lua 파싱
            results[cap_id] = parse_scrap_moveables(media_root, indices, logger)
        else:
            # criteria 기반 처리
            criteria = cap_data.get("criteria", [])
            results[cap_id] = resolve_criteria(criteria, indices, logger)
        
        # 결과 검증: items_itemscript.json에 존재하는지
        for fulltype in list(results[cap_id]):
            if fulltype not in items:
                logger.warning(f"[WARN] FullType '{fulltype}' not in items_itemscript.json")
                # Fail-loud #7은 제거하지 않고 경고만
        
        logger.info(f"[OK] Resolved: {cap_id} → {len(results[cap_id])} items")
    
    return results


# ============================================================================
# Phase 6: Invert - capability_by_fulltype 생성
# ============================================================================

def invert_to_fulltype(cap_results: Dict[str, Set[str]], logger: logging.Logger) -> Dict[str, List[str]]:
    """cap_id → Set[FullType] 를 FullType → List[cap_id] 로 역변환"""
    fulltype_caps = defaultdict(set)
    
    for cap_id, fulltypes in cap_results.items():
        for ft in fulltypes:
            fulltype_caps[ft].add(cap_id)
    
    # 정렬: FullType 키 알파벳순, capability 배열 알파벳순
    result = {}
    for ft in sorted(fulltype_caps.keys()):
        result[ft] = sorted(fulltype_caps[ft])
    
    logger.info(f"[OK] Inverted: {len(result)} unique FullTypes")
    return result


# ============================================================================
# Phase 7: Output Gate - 스키마/중복/Allowlist 검사
# ============================================================================

def output_gate_validate(output: Dict[str, List[str]], logger: logging.Logger) -> bool:
    """Output Gate: 스키마, 중복, Allowlist 검사"""
    passed = True
    
    for fulltype, caps in output.items():
        # 스키마 검증: key는 Module.ItemName 형식
        if "." not in fulltype:
            logger.error(f"[FAIL] Invalid FullType format: {fulltype}")
            passed = False
        
        # 빈 배열 금지
        if len(caps) == 0:
            logger.error(f"[FAIL] Empty capability array for {fulltype}")
            passed = False
        
        # 중복 검증
        if len(caps) != len(set(caps)):
            logger.error(f"[FAIL] Duplicate capability in {fulltype}")
            passed = False
        
        # Allowlist 검증
        for cap in caps:
            if cap not in CAPABILITY_ALLOWLIST:
                logger.error(f"[FAIL] Non-allowlist capability '{cap}' in {fulltype}")
                passed = False
    
    if passed:
        logger.info("[OK] Output Gate passed: Schema, Duplicates, Allowlist")
    
    return passed


# ============================================================================
# Phase 8: Atomic Write
# ============================================================================

def atomic_write(output: Dict[str, List[str]], logger: logging.Logger) -> None:
    """Atomic write: tmp → rename"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    tmp_path = OUTPUT_DIR / "capability_by_fulltype.tmp.json"
    final_path = OUTPUT_DIR / "capability_by_fulltype.json"
    
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Atomic rename
    tmp_path.replace(final_path)
    
    logger.info(f"[OK] Output written: capability_by_fulltype.json ({len(output)} FullTypes)")


def write_dry_run_result(output: Dict[str, List[str]], logger: logging.Logger) -> None:
    """Dry-run 결과를 logs/에 저장 (output/ 미사용)"""
    LOGS_DIR.mkdir(exist_ok=True)
    
    result_path = LOGS_DIR / f"dry_run_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    logger.info(f"[OK] Dry-run result written: {result_path.name} ({len(output)} FullTypes)")


# ============================================================================
# Main Pipeline
# ============================================================================

class RightClickCapabilityPipeline:
    def __init__(self, media_root: Path, skip_gate2: bool = False):
        self.media_root = media_root
        self.skip_gate2 = skip_gate2
        self.output_mode = "dry_run" if skip_gate2 else "production"
        self.logger = setup_logger()
    
    def run(self) -> bool:
        """전체 파이프라인 실행"""
        self.logger.info("=" * 60)
        self.logger.info("Right-Click Capability Pipeline Started")
        self.logger.info(f"Mode: {self.output_mode}")
        self.logger.info("=" * 60)
        
        try:
            # Phase 1: 입력 로드
            items = load_items(self.logger)
            source_index = load_source_index(self.logger)
            allowlist = parse_allowlist(self.logger)
            
            # Phase 2: Gate-1
            if not gate1_validate(source_index, allowlist, self.logger):
                self.logger.error("[FAIL] Pipeline aborted at Gate-1")
                return False
            
            # Phase 3: Gate-2
            if self.skip_gate2:
                self.logger.warning("[SKIP] Gate-2 skipped (--skip-gate2 mode)")
            else:
                if not gate2_validate(source_index, self.media_root, self.logger):
                    self.logger.error("[FAIL] Pipeline aborted at Gate-2")
                    return False
            
            # Phase 4: 인덱스 구축
            indices = build_indices(items, self.logger)
            
            # Phase 5: Capability 해결
            if self.skip_gate2:
                # dry_run 모드에서는 Lua 파싱 스킵 (파일 없을 수 있음)
                self.logger.warning("[SKIP] can_scrap_moveables Lua parsing skipped in dry_run mode")
                cap_results = {}
                for cap_id, cap_data in source_index["capabilities"].items():
                    if cap_id == "can_scrap_moveables":
                        # 더미 결과
                        cap_results[cap_id] = set()
                        self.logger.warning(f"[SKIP] {cap_id} → 0 items (dry_run)")
                    else:
                        criteria = cap_data.get("criteria", [])
                        cap_results[cap_id] = resolve_criteria(criteria, indices, self.logger)
                        self.logger.info(f"[OK] Resolved: {cap_id} → {len(cap_results[cap_id])} items")
            else:
                cap_results = resolve_capabilities(source_index, indices, self.media_root, items, self.logger)
            
            # Phase 6: Invert
            output = invert_to_fulltype(cap_results, self.logger)
            
            # Phase 7: Output Gate
            if not output_gate_validate(output, self.logger):
                self.logger.error("[FAIL] Pipeline aborted at Output Gate")
                return False
            
            # Phase 8: Write
            if self.output_mode == "dry_run":
                write_dry_run_result(output, self.logger)
            else:
                atomic_write(output, self.logger)
            
            self.logger.info("=" * 60)
            self.logger.info("Pipeline completed successfully")
            self.logger.info("=" * 60)
            return True
            
        except Exception as e:
            self.logger.error(f"[FAIL] Pipeline aborted: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Right-Click Capability Pipeline")
    parser.add_argument("--skip-gate2", action="store_true", help="Skip Gate-2 (dry_run mode)")
    parser.add_argument("--media-root", type=Path, default=MEDIA_ROOT, help="MEDIA_ROOT path")
    args = parser.parse_args()
    
    pipeline = RightClickCapabilityPipeline(
        media_root=args.media_root,
        skip_gate2=args.skip_gate2
    )
    
    success = pipeline.run()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
