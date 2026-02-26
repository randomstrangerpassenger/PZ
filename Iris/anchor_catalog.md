# Anchor Catalog — Moveable/Furniture Right-Click Evidence

## 개요

Moveable/Furniture 136개 아이템이 **인벤토리 우클릭 메뉴에 의해 생성되는 행동이 있는지**를
정적으로 증명할 수 있는 anchor 목록.

---

## Anchor A: `InvContextMovable.lua` — IGUI_PlaceObject

| 필드 | 값 |
|---|---|
| **source_type** | `lua_predicate_on_inventory_item` |
| **file** | [InvContextMovable.lua](file:///c:/Users/MW/Downloads/coding/PZ/lua/client/Context/Inventory/InvContextMovable.lua) |
| **span** | L16–L28 |
| **kind** | `type_guard` |
| **guard** | `instanceof(_item, "Moveable")` |
| **menu_item** | `IGUI_PlaceObject` ("오브젝트 놓기") |
| **action** | `ISMoveableCursor` → mode `"place"` |

### 핵심 로직

```lua
if instanceof(_item, "Moveable") then          -- L16: Type guard
    if _player:getPrimaryHandItem() ~= _item    -- L21: 손에 없을 때만
    and _player:getSecondaryHandItem() ~= _item then
        if instanceof(_item, "Radio") and _item:getWorldStaticItem() then
            return                               -- L24-26: Radio+WSI 제외
        end
        context:addOption(getText("IGUI_PlaceObject"), ...)  -- L28: 메뉴 추가
    end
end
```

### 증명력

- **모든 `Moveable` 타입 아이템**은 인벤토리 우클릭 시 "오브젝트 놓기" 메뉴를 받음
- Guard 조건: `instanceof(item, "Moveable")` → **Type=Moveable 이면 참**
- 유일한 제외: `Radio` + `WorldStaticItem` 조합 (Furniture 136에 해당 없음)

> [!IMPORTANT]
> 이 앵커는 **Type=Moveable인 모든 아이템**에 대해 "인벤토리 우클릭 → PlaceObject 메뉴" 존재를 **정적으로 증명**한다.
> `DisplayCategory=Furniture`는 여기서 분기 조건이 아니며, `Type=Moveable`이 유일한 guard다.

---

## Anchor B: `ISContextDisassemble.lua` — ContextMenu_Disassemble

| 필드 | 값 |
|---|---|
| **source_type** | `world_context_menu` |
| **file** | [ISContextDisassemble.lua](file:///c:/Users/MW/Downloads/coding/PZ/lua/client/Context/World/ISContextDisassemble.lua) |
| **span** | L14–L54 |
| **kind** | `world_object_menu` |
| **guard** | `ISMoveableSpriteProps.fromObject(object)` + `canScrapObject()` |
| **menu_item** | `ContextMenu_Disassemble` ("해체") |

### 핵심 로직

```lua
for _,object in ipairs(_data.objects) do
    local moveProps = ISMoveableSpriteProps.fromObject(object)  -- L25
    if moveProps then
        local resultScrap = moveProps:canScrapObject(_data.player)  -- L32
        if resultScrap.craftValid then
            -- validObjList에 추가 → L44에서 Disassemble 메뉴 생성
        end
    end
end
```

### 증명력

- 월드에 배치된 Moveable 오브젝트를 우클릭하면 해체 메뉴 표시
- **인벤토리 우클릭이 아닌 월드 우클릭**이므로 현재 파이프라인 스코프 외
- 참고 앵커로만 기록 (향후 확장 시 사용 가능)

---

## Anchor C: `ISInventoryPaneContextMenu.lua` — doPlace3DItemOption

| 필드 | 값 |
|---|---|
| **source_type** | `inventory_context_menu` |
| **file** | [ISInventoryPaneContextMenu.lua](file:///c:/Users/MW/Downloads/coding/PZ/lua/client/ISUI/ISInventoryPaneContextMenu.lua#L3707-L3748) |
| **span** | L3707–L3748 |
| **kind** | `property_check` |
| **guard** | `item:getWorldStaticItem()` OR `instanceof(item, "HandWeapon")` OR `instanceof(item, "Clothing")` |
| **menu_item** | `ContextMenu_PlaceItemOnGround` ("아이템을 바닥에 놓기") |

### 핵심 로직

```lua
for _,item in ipairs(items) do
    if not item:getWorldStaticItem()
       and not instanceof(item, "HandWeapon")
       and not instanceof(item, "Clothing") then
        all3D = false  -- L3713-3714: 3D 배치 불가
    end
end
if all3D then
    context:addOption(getText("ContextMenu_PlaceItemOnGround"), ...)  -- L3729
end
```

### 증명력

- `getWorldStaticItem()` 프로퍼티가 있으면 "바닥에 놓기" 메뉴 표시
- **이것은 Moveable 타입 체크가 아닌 프로퍼티 체크**
- Moveable+Furniture 아이템 중 `WorldStaticItem` 프로퍼티가 있는 것만 해당
- `items_itemscript.json`에서 `WorldStaticItem` 필드 추출이 필요하지만, 현재 미포함

---

## Anchor D: `ISMoveablesAction.lua` — perform() "place" 모드

| 필드 | 값 |
|---|---|
| **source_type** | `lua_action_invocation` |
| **file** | [ISMoveablesAction.lua](file:///c:/Users/MW/Downloads/coding/PZ/lua/client/Moveables/ISMoveablesAction.lua#L148-L172) |
| **span** | L148–L172 (perform), L1535–L1619 (placeMoveable chain) |
| **kind** | `lua_function` |
| **guard** | `self.moveProps.isMoveable and self.mode == "place"` |
| **action** | `placeMoveableViaCursor → placeMoveable → placeMoveableInternal` |

### 핵심 로직 — perform() L156-162

```lua
if self.moveProps and self.moveProps.isMoveable and self.mode and self.mode ~= "scrap" then
    if self.mode == "place" then
        self.moveProps:placeMoveableViaCursor( self.character, self.square, ... )  -- L161
        buildUtil.setHaveConstruction(self.square, true)                          -- L162
    end
end
```

### 실행 체인

```
perform() L160-162
  → placeMoveableViaCursor() L1535  (ISMoveableSpriteProps)
    → placeMoveable() L1542
      → placeMoveableInternal() L1636  ← world object 생성
        → IsoObject.new(getCell(), _square, spriteName)  또는
        → IsoThumpable.new / IsoDoor.new / IsoWindow.new 등
      → inventory:Remove(item)  ← 인벤토리에서 아이템 제거
```

### 증명력

| 기준 | 판정 | 증거 |
|---|---|---|
| **A (executing_tool)** | **판정 보류** | 아이템은 "배치되는 오브젝트"이지 "실행 도구"가 아님. `character`가 실행 주체. Gate-0 A 정의("실행 주체=아이템")와 매핑이 **모호** |
| **B (external_target)** | **true** | `placeMoveableInternal(_square, item, spriteName)` → world tile(`IsoGridSquare`)에 IsoObject 생성 |
| **C (persistent_change)** | **true** | IsoObject 생성(world 영구 변경) + `inventory:Remove(item)` + `buildUtil.setHaveConstruction(square, true)` |

> [!WARNING]
> A(executing_tool) 판정은 Gate-0의 "executing_tool" 정의에 따라 달라짐.
> "아이템이 행동의 실행 주체 도구"라면 A=unknown (배치 행위 주체는 character).
> "아이템이 행동을 트리거하는 조건"이라면 Anchor A에서 이미 메뉴 존재 증명됨.
> **이 판단은 정책 결정 사항**이며, 앵커 자체는 양쪽 판단의 근거를 모두 제공.

---

## Negative Anchor (증명 부재 확인)

### ISInventoryPaneContextMenu.lua — Moveable/Furniture 전수 검색

| 키워드 | 검색 결과 |
|---|---|
| `Moveable` | **0건** |
| `Furniture` | **0건** |
| `ISMoveable` | **0건** |
| `pickup` | **0건** |
| `moveable` (case-insensitive) | **0건** |
| `IsoThumpable` | **0건** |
| `IsoObject` | **0건** |
| `WorldStaticItem` | **0건** (함수명에만 등재, 키워드 매칭 없음) |

### ISWorldObjectContextMenu.lua — 동일

| 키워드 | 검색 결과 |
|---|---|
| `moveable` | **0건** |
| `furniture` | **0건** |
| `pickup` | **0건** |

> [!NOTE]
> `ISInventoryPaneContextMenu.lua`와 `ISWorldObjectContextMenu.lua` 본체에는 Moveable/Furniture를 직접 분기 처리하는 코드가 **전혀 없다**.
> Moveable 아이템의 인벤토리 우클릭은 **별도 모듈** `InvContextMovable.lua`에서 처리된다.

---

## 앵커 요약

| ID | 파일 | Guard | 증명 대상 | 현재 활용 가능 |
|---|---|---|---|---|
| **A** | InvContextMovable.lua | `instanceof(Moveable)` | 메뉴 존재 (PlaceObject) — A/B/C 직접 증명 아님 | ✅ (prove-only REVIEW) |
| **B** | ISContextDisassemble.lua | ISMoveableSpriteProps | 월드 우클릭 Disassemble (현 스코프 외) | ⬜ |
| **C** | ISInventoryPaneContextMenu.lua | getWorldStaticItem() | PlaceItemOnGround (WSI 미추출) | ⬜ |
| **D** | ISMoveablesAction.lua | isMoveable + mode="place" | **B=true, C=true** (A는 정책 판단 필요) | ✅ (A+D 조합 시) |
