 # Prove Rule Proposals — Moveable/Furniture Anchor 기반 (v2 계약 준수)

## 전제 조건

- [anchor_catalog.md](file:///c:/Users/MW/Downloads/coding/PZ/Iris/anchor_catalog.md)의 **Anchor A** 기반
- v2 계약 문서: [rightclick_evidence_source_allowlist_v2.md](file:///c:/Users/MW/Downloads/coding/PZ/Iris/rightclick_evidence_source_allowlist_v2.md), [rightclick_source_index.json](file:///c:/Users/MW/Downloads/coding/PZ/Iris/rightclick_source_index.json) 준수
- `matcher_logic=AND` 지원: source_index 스키마 L28에 정의 확인 완료 (단, 본 Proposal 1은 matcher 1개이므로 미사용)

---

## Proposal 1: `rule_prove_moveable_place` (prove 전부 unknown → REVIEW)

### Anchor가 증명하는 것과 증명하지 않는 것

| 증명됨 | 증명되지 않음 |
|---|---|
| `instanceof(Moveable)` → `IGUI_PlaceObject` **메뉴가 생성됨** | 아이템이 행동의 **실행 주체**(executing_tool)인지 |
| 메뉴 존재 조건이 **item type predicate에 의해 게이팅됨** | 행동이 **외부 대상**에 영향을 주는지 (external_target) |
| | 행동이 **지속적 변화**를 일으키는지 (persistent_change) |

> [!IMPORTANT]
> Anchor A는 "메뉴 존재"를 증명하지, "executing_tool=true"를 증명하지 않는다.
> 실행 주체는 `ISMoveableCursor` / `ISMoveablesAction` 등 **커서/액션 객체**이며,
> 아이템은 "메뉴 생성 조건(재료/보유 조건)" 역할일 수 있다.
> 따라서 A/B/C 전부 **unknown**.

### 규칙 정의

```json
{
    "rule_id": "rule_prove_moveable_place",
    "source_type": "lua_predicate_on_inventory_item",
    "anchor": {
        "kind": "lua_function",
        "ref": "lua/client/Context/Inventory/InvContextMovable.lua::ISInventoryMenuElements.ContextMovable",
        "version": "b41"
    },
    "extract": {
        "matchers": [
            {
                "match_type": "script_type",
                "value": "Moveable"
            }
        ]
    },
    "prove": {
        "executing_tool": "unknown",
        "external_target": "unknown",
        "persistent_change": "unknown"
    },
    "notes": "Anchor A: InvContextMovable.lua L16 instanceof(Moveable) → IGUI_PlaceObject 메뉴 생성 확인. 메뉴 존재는 증명되나, executing_tool 정의(행동 실행 주체=아이템)와 매핑되지 않음. 실제 실행 주체는 ISMoveableCursor/ISMoveablesAction 커서·액션 객체. A/B/C 전부 unknown → REVIEW. prove-only rule이므로 exclusions 미지정. Proposal 2에서 lua_action_invocation 앵커 확보 시 A/B/C true로 승격 가능."
}
```

### Prove 판정 근거

| 기준 | 판정 | 근거 |
|---|---|---|
| **A (executing_tool)** | `unknown` | 앵커가 증명하는 건 "메뉴 생성 조건=Type 가드"이지, "아이템=실행 주체"가 아님 |
| **B (external_target)** | `unknown` | `lua_action_invocation` 앵커 미확보 |
| **C (persistent_change)** | `unknown` | 위와 동일 |

### matcher 범위 결정

| 항목 | 값 | 이유 |
|---|---|---|
| **앵커 guard** | `instanceof(Moveable)` | Type=Moveable 전체 |
| **rule matcher** | `script_type=Moveable` | **앵커가 보장하는 범위와 1:1 대응** |

- 기존 `rule_candidate_moveable_furniture`는 `script_type=Moveable AND display_category=Furniture`로 **정책상 좁힌 것**이었음
- 본 prove rule은 앵커 guard에 맞춰 `script_type=Moveable` 단일 조건으로 정렬
- DC=Furniture 제한이 필요한 경우, 별도 정책 레이어에서 처리 (prove rule 자체는 앵커에 충실)

### 예상 영향

| 항목 | 앵커 증명 범위 | 정책 제한 시 (참고) |
|---|---|---|
| 매칭 대상 | **Type=Moveable 전체** (136 + α) | DC=Furniture만이면 136 |
| Decision | **REVIEW** (A/B/C 전부 unknown) | 동일 |
| 기존 대비 변화 | `rule_candidate_moveable_furniture`(disabled)를 **활성 규칙으로 대체** | |

> [!NOTE]
> A/B/C 전부 unknown이므로 resolution은 **REVIEW**. 기존 candidate-only(disabled, prove 전부 unknown)와 결과 decision은 동일하지만,
> 차이점은: (1) 앵커가 명시됨, (2) disabled가 아닌 활성 규칙, (3) `source_type=lua_predicate_on_inventory_item` 근거가 문서화됨.
> 이 규칙은 "메뉴 존재 증거를 기록한 REVIEW" 상태이며, Proposal 2로 STRONG 승격할 **발판**.

---

## Proposal 2: Anchor D로 B/C 승격 (스캔 완료)

### 스캔 결과 — ISMoveablesAction:perform() L148-172

`ISMoveablesAction`은 `ISBaseTimedAction` 파생 클래스. `"place"` 모드에서 실행 체인:

```
perform() L160-162
  → placeMoveableViaCursor() L1535  (ISMoveableSpriteProps)
    → placeMoveable() L1542
      → placeMoveableInternal() L1636  ← IsoObject/IsoThumpable/etc 생성
      → inventory:Remove(item)         ← 인벤토리에서 아이템 제거
  → buildUtil.setHaveConstruction(square, true)  ← world 상태 플래그 변경
```

### B/C 증거 (확정)

| 기준 | 판정 | 코드 증거 |
|---|---|---|
| **B (external_target)** | **true** | `placeMoveableInternal(_square, item, spriteName)` → `IsoObject.new(getCell(), _square, spriteName)` 등. 월드 타일에 오브젝트 직접 생성 |
| **C (persistent_change)** | **true** | IsoObject가 world에 영구 추가 + `inventory:Remove(item)` + `buildUtil.setHaveConstruction(square, true)` |

### A 증거 (정책 결정 필요)

| 해석 | A 판정 | 근거 |
|---|---|---|
| "아이템 = 실행 도구" | **unknown** | Moveable 아이템은 "배치되는 대상(object)"이지 "실행하는 도구(tool)"가 아님. 실행 주체는 `self.character` |
| "아이템 = 행동 트리거 조건" | **true** | Anchor A에서 `instanceof(Moveable)` → 메뉴 생성. 아이템이 없으면 행동 자체가 발생하지 않음 |

> [!CAUTION]
> **A의 판정은 순수 코드 증거가 아닌 정책 선택**이다.
> Gate-0의 `executing_tool` 정의가 "도구로서의 아이템"이면 A=unknown → **WEAK** (B/C만 true).
> "행동 트리거 조건"까지 포함하면 A=true → **STRONG**.

### 규칙 정의 (A=unknown 보수적 버전)

```json
{
    "rule_id": "rule_prove_moveable_place_action",
    "source_type": "lua_action_invocation",
    "anchor": {
        "kind": "lua_function",
        "ref": "lua/client/Moveables/ISMoveablesAction.lua::ISMoveablesAction.perform",
        "version": "b41"
    },
    "extract": {
        "matchers": [
            {
                "match_type": "script_type",
                "value": "Moveable"
            }
        ]
    },
    "prove": {
        "executing_tool": "unknown",
        "external_target": true,
        "persistent_change": true
    },
    "notes": "Anchor D: ISMoveablesAction:perform() place 모드. placeMoveableViaCursor → placeMoveable → placeMoveableInternal에서 IsoObject를 world에 생성(B=true). inventory:Remove + buildUtil.setHaveConstruction으로 지속 변화(C=true). executing_tool은 정책 판단 보류 — 아이템은 '배치되는 오브젝트'이며, 실행 주체는 character. prove-only rule이므로 exclusions 미지정."
}
```

### 적용 시나리오

| A 판정 | 결과 Decision | 조건 |
|---|---|---|
| `unknown` (보수적) | **WEAK** | Proposal 1(A/B/C=unknown) + Proposal 2(A=unknown, B=true, C=true) 병합 |
| `true` (정책 결정) | **STRONG** | A를 "행동 트리거 조건" 해석으로 true 판정 시 |

### 예상 영향 (WEAK 기준)

| 항목 | 값 |
|---|---|
| 매칭 대상 | Type=Moveable 전체 (136 + α) |
| Decision | candidate-only REVIEW → **WEAK** |
| WEAK 변화 | 51 → **51 + 136 = 187** |

---

## Junk · VehicleMaintenance — 변동 없음

| Cluster | 스캔 결과 | 판정 |
|---|---|---|
| Normal+Junk (73) | 현 스캔 범위 내 앵커 0건 | **현 스캔 범위 내에서 앵커 미발견** |
| Normal+VM (89) | 현 스캔 범위 내 앵커 0건 | **현 스캔 범위 내에서 앵커 미발견** |

> [!NOTE]
> 다른 InvContext 모듈이나 이벤트 훅에서 처리될 가능성은 남아 있음.

