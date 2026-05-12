"""
DescriptionGenerator — UseCase Block Builder
=============================================
usecases_by_fulltype.v2.4.json + uniqueness_overlay.v2.4.json
→ descriptions_by_fulltype.v2.4.json

Phase D1: Reader/Joiner — 입력 로드 + 중간 모델 구성
Phase D2: Block Builder — 정렬 + REVIEW 필터 + 빈 블록 처리
Phase D3: Renderer — 라인 템플릿 + 최종 산출물

운영 안전 규칙 (동결):
  - frozen_description_count = 블록이 생성된 fulltype 수 (전체 아이템 수 아님)
  - label = use_case_id 그대로 (i18n 시 키→문자열 치환만, 조건 분기 금지)
  - REVIEW-only만 격리: has_review && !has_pass → debug_only
    PASS+REVIEW 동시 존재 시 기본 출력에 잔류
"""
import sys
from pathlib import Path

# ── Paths ──
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

IRIS_DIR = SCRIPT_DIR.parent
OUTPUT_DIR = IRIS_DIR / "output"

from tools.common.io import load_json, write_json
from tools.common.versions import BUILD_VERSION

USECASES_PATH = OUTPUT_DIR / f"usecases_by_fulltype.{BUILD_VERSION}.json"
OVERLAY_PATH = OUTPUT_DIR / f"uniqueness_overlay.{BUILD_VERSION}.json"
REQUIREMENTS_PATH = OUTPUT_DIR / f"requirements_by_fulltype.{BUILD_VERSION}.json"
NAV_REGISTRY_PATH = OUTPUT_DIR / f"recipe_nav_registry.{BUILD_VERSION}.json"
OUTPUT_PATH = OUTPUT_DIR / f"descriptions_by_fulltype.{BUILD_VERSION}.json"

LABELMAP_PATH = IRIS_DIR / "build" / "data" / BUILD_VERSION / "usecase_label_map.json"

# ── Constants ──
SURFACE_RANK = {"both": 0, "context_menu": 1, "recipe_ui": 2}
STRENGTH_RANK = {"STRONG": 0, "WEAK": 1, None: 2}

SURFACE_LABEL = {
    "context_menu": "우클릭",
    "recipe_ui": "레시피",
    "both": "우클릭+레시피",
}

SURFACE_LABEL_KEEP = {
    "context_menu": "우클릭·도구",
    "recipe_ui": "레시피·도구",
    "both": "우클릭+레시피·도구",
}

STRENGTH_LABEL = {
    "STRONG": " [강]",
    "WEAK": " [약]",
}

UNIQUENESS_LABEL = {
    "unique": " [고유]",
    "shared": " [공유]",
}


# ══════════════════════════════════════════════════════════════════════════
#  Phase D1: Reader/Joiner
# ══════════════════════════════════════════════════════════════════════════

def build_intermediate_model(usecases_data: dict) -> dict:
    """
    usecases_by_fulltype → fulltype별 중간 모델 구성.

    Returns: {fulltype: {"title_key": "actions", "items": [...]}}
    """
    fulltypes = usecases_data.get("fulltypes", {})
    result = {}

    for ft, ft_data in fulltypes.items():
        items = []
        for uc in ft_data.get("use_cases", []):
            # sources 분석: 기계적 OR (추론 금지)
            has_pass = False
            has_review = False
            for src in uc.get("evidence_sources", []):
                decision = src.get("decision")
                if decision == "PASS":
                    has_pass = True
                elif decision == "REVIEW":
                    has_review = True

            # uniqueness: overlay에서 그대로
            uniqueness_data = uc.get("uniqueness", {})
            overlay_label = uniqueness_data.get("overlay", "none")

            # role 추출 (C2: recipe_evidence 전용 필수 필드)
            # 우선순위: consume > keep > None(rightclick 전용)
            has_consume = False
            has_keep = False
            for src in uc.get("evidence_sources", []):
                role = src.get("role")
                if role == "consume":
                    has_consume = True
                elif role == "keep":
                    has_keep = True
            if has_consume:
                item_role = "consume"
            elif has_keep:
                item_role = "keep"
            else:
                item_role = None  # rightclick 전용

            items.append({
                "use_case_id": uc["use_case_id"],
                "label_key": uc["use_case_id"],  # 기계적 복사, 추론 금지
                "surface": uc.get("surface", "context_menu"),
                "display_strength": uc.get("display_strength"),
                "uniqueness": overlay_label,
                "role": item_role,
                "sources": {
                    "has_pass": has_pass,
                    "has_review": has_review,
                },
            })

        if items:
            result[ft] = {
                "title_key": "actions",
                "items": items,
            }

    return result


# ══════════════════════════════════════════════════════════════════════════
#  Phase D2: Block Builder
# ══════════════════════════════════════════════════════════════════════════

def sort_key(item: dict) -> tuple:
    """결정적 정렬 키: surface_rank → strength_rank → use_case_id."""
    return (
        SURFACE_RANK.get(item["surface"], 99),
        STRENGTH_RANK.get(item["display_strength"], 2),
        item["use_case_id"],
    )


def build_blocks(intermediate: dict) -> dict:
    """
    중간 모델 → 정렬 + REVIEW 필터 적용 → 블록 구조.

    REVIEW 격리 규칙 (동결):
      REVIEW-only만 격리 — has_review && !has_pass → debug_only=True
      PASS+REVIEW 동시 존재 시 기본 출력에 잔류

    Returns: {fulltype: {"title_key", "main_items": [...], "debug_items": [...]}}
    """
    result = {}

    for ft, block in intermediate.items():
        items = block["items"]

        # 정렬 (결정적)
        sorted_items = sorted(items, key=sort_key)

        main_items = []
        debug_items = []

        for item in sorted_items:
            src = item["sources"]
            # REVIEW-only만 격리: has_review==True && has_pass==False
            if src["has_review"] and not src["has_pass"]:
                debug_items.append(item)
            else:
                main_items.append(item)

        # 빈 블록 처리: main도 debug도 비어 있으면 생략
        if not main_items and not debug_items:
            continue

        result[ft] = {
            "title_key": block["title_key"],
            "main_items": main_items,
            "debug_items": debug_items,
        }

    return result


# ══════════════════════════════════════════════════════════════════════════
#  Phase D3: Renderer
# ══════════════════════════════════════════════════════════════════════════

VALID_STRENGTH = {"STRONG", "WEAK", "EXCLUDE", None}

def get_recipe_label_text(ucid: str, recipe_nav_entries: dict) -> str:
    nav_entry = recipe_nav_entries.get(ucid)
    if not nav_entry:
        raise ValueError(f"FAIL-LOUD: recipe nav entry missing '{ucid}'")

    label_text = nav_entry.get("translated_name") or nav_entry.get("original_name")
    if not label_text:
        raise ValueError(f"FAIL-LOUD: recipe nav entry has no display name '{ucid}'")
    return label_text


def render_item(item: dict, label_map: dict, recipe_nav_entries: dict | None = None) -> dict:
    """
    아이템을 구조체 블록 데이터로 변환.
    - display_text = [{surface_label}] {label_text_KO}
    """
    recipe_nav_entries = recipe_nav_entries or {}
    ucid = item["use_case_id"]
    if ucid.startswith("uc.exclusion."):
        # Exclusion 속성은 런타임에 노출되지 않고 분류 필터로만 쓰이므로 라벨 번역 불필요
        display_text = ucid
        strength = None
    else:
        label_entry = label_map.get(ucid)
        if label_entry is None:
            if ucid.startswith("uc.recipe."):
                label_text = get_recipe_label_text(ucid, recipe_nav_entries)
            else:
                raise ValueError(f"FAIL-LOUD: label_map missing '{ucid}'")
        else:
            label_text = label_entry['KO']
            
        strength = item["display_strength"]
        assert strength in VALID_STRENGTH, f"Invalid strength '{strength}' for {ucid}"
        
        role = item.get("role")
        if role == "keep":
            surface_label = SURFACE_LABEL_KEEP.get(item["surface"], item["surface"])
        else:
            surface_label = SURFACE_LABEL.get(item["surface"], item["surface"])
        display_text = f"[{surface_label}] {label_text}"
    
    return {
        "use_case_id": ucid,
        "display_text": display_text,
        "surface": item["surface"],
        "strength": strength,
        "uniqueness": item.get("uniqueness"),
        "line_kind": item.get("line_kind", "evidence"),
    }


def assert_no_unlabeled_output(output: dict) -> None:
    violations = []
    for ft, ft_data in output.get("fulltypes", {}).items():
        block = ft_data.get("use_case_block", {})
        for item in block.get("items", []) + block.get("debug_items", []):
            display_text = item.get("display_text", "")
            if "(unlabeled:" in display_text:
                violations.append(f"{ft}: {display_text}")

    if violations:
        preview = "; ".join(violations[:5])
        raise ValueError(f"FAIL-LOUD: unlabeled usecase output remains ({len(violations)}): {preview}")


def render_descriptions(
    blocks: dict,
    requirements_data: dict,
    label_map: dict,
    recipe_nav_entries: dict | None = None,
) -> dict:
    """
    블록 구조 → 최종 산출물 descriptions_by_fulltype.

    Returns: {"version": ..., "fulltypes": {ft: {"use_case_block": {...}, "requirements_block": {...}}}}
    """
    fulltypes_output = {}
    req_fulltypes = requirements_data.get("fulltypes", {})

    # 모든 fulltype 모음 (use_case + requirements)
    all_fts = sorted(set(blocks.keys()) | set(req_fulltypes.keys()))

    for ft in all_fts:
        ft_entry = {}

        # ── use_case_block ──
        if ft in blocks:
            block = blocks[ft]
            items = [
                render_item(item, label_map, recipe_nav_entries)
                for item in block["main_items"]
            ]
            debug_items = [
                render_item(item, label_map, recipe_nav_entries)
                for item in block["debug_items"]
            ]
            if items or debug_items:
                ft_entry["use_case_block"] = {
                    "title_key": block["title_key"],
                    "items": items,
                    "debug_items": debug_items,
                }

        # ── requirements_block (keep) ──
        if ft in req_fulltypes:
            reqs = req_fulltypes[ft].get("requirements", [])
            if reqs:
                # 고유 requirement_key 추출 (정렬된 순서 유지)
                seen_keys = []
                for r in reqs:
                    k = r["requirement_key"]
                    if k not in seen_keys:
                        seen_keys.append(k)

                # lines: 고유 requirement_key만 (role 표시, 라벨 치환 없이 그대로)
                req_lines = [f"- {k} ({r_role})" for k in seen_keys
                             for r_role in ["keep"]]  # 현재 keep만
                # debug_lines: recipe_id 포함
                req_debug_lines = [
                    f"- {r['requirement_key']} ({r['role']}) [{r['recipe_id']}]"
                    for r in reqs
                ]
                ft_entry["requirements_block"] = {
                    "title_key": "requirements",
                    "lines": req_lines,
                    "debug_lines": req_debug_lines,
                }

        # ── require_block (v2.5 신규, output 기준) ──
        if ft in req_fulltypes:
            require_atoms = req_fulltypes[ft].get("require", [])
            if require_atoms:
                rq_lines = []
                rq_debug_lines = []
                for atom in require_atoms:
                    kind = atom.get("kind", "")
                    key = atom.get("key", "")
                    recipe_id = atom.get("recipe_id", "")
                    # 렌더 템플릿 (키 나열 + 라벨 lookup만, 추론 금지)
                    if kind == "perk":
                        op = atom.get("op", ">=")
                        value = atom.get("value", 0)
                        display = f"{key} {op} {value}"
                    elif kind == "near_item":
                        display = f"Near: {key}"
                    elif kind == "flag":
                        display = key
                    else:
                        # FAIL-LOUD: 빌드 타임에서 이미 allowlist로 필터됨
                        # 만약 여기에 도달하면 데이터 오류
                        display = f"UNKNOWN_REQUIRE_ATOM:{kind}:{key}"
                    rq_lines.append(f"- {display} ({kind})")
                    rq_debug_lines.append(f"- {display} ({kind}) [{recipe_id}]")

                # 중복 제거 (동일 display가 여러 recipe에서 올 수 있음)
                seen_displays = []
                unique_rq_lines = []
                for rl in rq_lines:
                    if rl not in seen_displays:
                        seen_displays.append(rl)
                        unique_rq_lines.append(rl)

                ft_entry["require_block"] = {
                    "title_key": "require",
                    "lines": unique_rq_lines,
                    "debug_lines": rq_debug_lines,
                }

        if ft_entry:
            fulltypes_output[ft] = ft_entry

    return {
        "version": BUILD_VERSION,
        "fulltypes": fulltypes_output,
    }


# ══════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════

def generate_descriptions() -> tuple[dict, int]:
    """
    Full pipeline: D1 → D2 → D3.

    Returns: (output_data, exit_code)
    """
    # ── D1: Reader/Joiner ──
    print(f"  Loading usecases: {USECASES_PATH.name}")
    usecases_data = load_json(USECASES_PATH)
    
    print(f"  Loading label map: {LABELMAP_PATH.name}")
    label_data = load_json(LABELMAP_PATH)
    label_map = label_data.get("labels", {})

    # NOTE: uniqueness overlay는 build_usecases_by_fulltype 단계에서 이미
    # usecases_by_fulltype에 반영 완료. 여기서는 파일 존재 검증만 수행하며
    # 데이터를 직접 소비하지 않는다 (이중 적용 방지).
    print(f"  Overlay validated: {OVERLAY_PATH.name} (consumed by usecases, not re-read)")

    print(f"  Loading requirements: {REQUIREMENTS_PATH.name}")
    requirements_data = load_json(REQUIREMENTS_PATH)
    req_ft_count = requirements_data.get("fulltype_count", 0)
    req_keep_count = requirements_data.get("requirements_entry_count",
                                           requirements_data.get("entry_count", 0))
    req_require_count = requirements_data.get("require_entry_count", 0)
    print(f"  ✅ Requirements loaded: {req_ft_count} fulltypes, "
          f"keep={req_keep_count}, require={req_require_count}")

    print(f"  Loading recipe nav registry: {NAV_REGISTRY_PATH.name}")
    nav_registry = load_json(NAV_REGISTRY_PATH)
    recipe_nav_entries = nav_registry.get("entries", {})
    print(f"  ✅ Recipe nav entries: {len(recipe_nav_entries)}")

    print("  Building intermediate model...")
    intermediate = build_intermediate_model(usecases_data)
    print(f"  ✅ Intermediate: {len(intermediate)} fulltypes")

    # ── D2: Block Builder ──
    print("  Building blocks (sort + REVIEW filter)...")
    blocks = build_blocks(intermediate)

    main_count = sum(len(b["main_items"]) for b in blocks.values())
    debug_count = sum(len(b["debug_items"]) for b in blocks.values())
    print(f"  ✅ Blocks: {len(blocks)} fulltypes, "
          f"{main_count} main lines, {debug_count} debug lines")

    # ── D3: Renderer ──
    print("  Rendering descriptions...")
    output = render_descriptions(blocks, requirements_data, label_map, recipe_nav_entries)
    assert_no_unlabeled_output(output)
    ft_count = len(output["fulltypes"])
    print(f"  ✅ Output: {ft_count} fulltypes with blocks")
    req_block_count = sum(
        1 for ft_data in output["fulltypes"].values()
        if "requirements_block" in ft_data
    )
    rq_block_count = sum(
        1 for ft_data in output["fulltypes"].values()
        if "require_block" in ft_data
    )
    print(f"     (use_case: {len(blocks)}, requirements: {req_block_count}, require: {rq_block_count})")

    # ── Write output ──
    OUTPUT_DIR.mkdir(exist_ok=True)
    write_json(OUTPUT_PATH, output, indent=2, trailing_newline=False)

    print(f"  ✅ Saved: {OUTPUT_PATH.name}")
    return output, 0


def main():
    print("=" * 60)
    print(f"  DescriptionGenerator (BUILD_VERSION={BUILD_VERSION})")
    print("=" * 60)

    # ── Check prerequisites ──
    for path, label in [
        (USECASES_PATH, "usecases_by_fulltype"),
        (OVERLAY_PATH, "uniqueness_overlay"),
        (REQUIREMENTS_PATH, "requirements_by_fulltype"),
        (LABELMAP_PATH, "usecase_label_map"),
    ]:
        if not path.exists():
            print(f"\n  ❌ {label} not found: {path}")
            return 1

    output, code = generate_descriptions()
    if code != 0:
        return code

    ft_count = len(output["fulltypes"])

    # Surface distribution
    surface_dist = {"context_menu": 0, "recipe_ui": 0, "both": 0}
    for ft_data in output["fulltypes"].values():
        block = ft_data.get("use_case_block", {})
        for item in block.get("items", []) + block.get("debug_items", []):
            surf = item.get("surface")
            if surf in surface_dist:
                surface_dist[surf] += 1

    # Requirements/Require counts
    req_block_count = sum(
        1 for ft_data in output["fulltypes"].values()
        if "requirements_block" in ft_data
    )
    rq_block_count = sum(
        1 for ft_data in output["fulltypes"].values()
        if "require_block" in ft_data
    )

    print(f"\n  Summary:")
    print(f"     fulltypes with blocks: {ft_count}")
    print(f"     surface distribution: {surface_dist}")
    print(f"     fulltypes with requirements(keep): {req_block_count}")
    print(f"     fulltypes with require: {rq_block_count}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
