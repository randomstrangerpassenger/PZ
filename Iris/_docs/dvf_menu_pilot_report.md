# DVF Menu Pilot Report

**Version:** 1.0
**Date:** 2026-03-15
**Scope:** Layer 3 Individual Item Description — Menu Integration Pilot
**Data Source:** `dvf_3_3_rendered.json` v2.0 (1089 entries, APPROVE_SYNC only — original 1050 + CPR 39)
**Runtime Source:** `IrisLayer3Data.lua` (1089 entries, auto-generated)

---

## Pilot A: APPROVE_SYNC Acquisition Text Verification

### Objective

Confirm that `text_ko` values in `IrisLayer3Data.lua` are:
1. Present and non-empty
2. Acquisition-oriented (where found / how obtained), NOT use/interaction descriptions
3. Free of internal key leaks (`Base.`, `uc.`, `module.`, classification IDs)

### Sample Items (5 representative categories)

#### 1. Ammo — `Base.223Clip`

- **text_ko present:** YES (non-empty)
- **Content (decoded):** "탄약. 총기 취급 장소와 경찰 시설에서 발견된다."
- **Translation:** "Ammo. Found at firearms handling locations and police facilities."
- **Acquisition-oriented:** YES — describes where the item is found (acq_location)
- **Internal key leaks:** NONE
- **Verdict:** PASS

#### 2. Tool — `Base.Axe`

- **text_ko present:** YES (non-empty)
- **Content (decoded):** "무기 겸용 도구. 작업 차량과 차고, 목공 공구 상자와 공구점에서 발견된다."
- **Translation:** "Weapon/tool dual-use. Found in work vehicles, garages, woodworking toolboxes, and hardware stores."
- **Acquisition-oriented:** YES — describes discovery locations (acq_location)
- **Internal key leaks:** NONE
- **Verdict:** PASS

#### 3. Medical Consumable — `Base.AlcoholWipes`

- **text_ko present:** YES (non-empty)
- **Content (decoded):** "의료 소모품. 의료 시설이나 구급 차량에서 발견된다."
- **Translation:** "Medical consumable. Found in medical facilities or ambulances."
- **Acquisition-oriented:** YES — describes discovery locations (acq_location)
- **Internal key leaks:** NONE
- **Verdict:** PASS

#### 4. Explosive (Crafted) — `Base.Aerosolbomb`

- **text_ko present:** YES (non-empty)
- **Content (decoded):** "폭발물. 헤어스프레이와 불꽃놀이 재료를 조합해 만든다."
- **Translation:** "Explosive. Made by combining hairspray and firework materials."
- **Acquisition-oriented:** YES — describes how the item is obtained via crafting (acq_method)
- **Internal key leaks:** NONE
- **Verdict:** PASS

#### 5. Farming Module — `farming.HandShovel`

- **text_ko present:** YES (non-empty)
- **Content (decoded):** "원예 도구. 차고와 농업 물품 상자, 원예 상점과 공구점에서 발견된다."
- **Translation:** "Gardening tool. Found in garages, farming supply boxes, garden shops, and hardware stores."
- **Acquisition-oriented:** YES — describes discovery locations (acq_location)
- **Internal key leaks:** NONE
- **Verdict:** PASS

### Pilot A Summary

| Check | Result |
|---|---|
| text_ko present & non-empty (all 5) | PASS |
| Acquisition-oriented content (all 5) | PASS |
| No use/interaction descriptions | PASS |
| No internal key leaks | PASS |
| **Overall Pilot A** | **PASS** |

---

## Pilot B: HOLD/SILENT Non-Display Verification

### Objective

Confirm that items NOT present in `IrisLayer3Data` produce no output (nil/silent behavior), and that other wiki sections do not depend on Layer 3 data.

### B.1: Renderer nil-Path Analysis

**File:** `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`

The `Layer3Renderer.getText(fullType)` function (lines 52-73) follows this logic:

1. `ensureData()` loads `IrisLayer3Data` global table once (lines 28-46)
2. If `layer3Data` is nil or `fullType` is nil, returns `nil` immediately (lines 55-57)
3. Looks up `layer3Data[fullType]` via pcall (lines 59-65)
4. If entry is nil or `entry.text_ko` is nil, returns `nil` (line 64)
5. If pcall fails, returns `nil` silently (lines 71-72)

**Missing fullType path:** When a fullType key does not exist in `IrisLayer3Data`, `layer3Data[fullType]` evaluates to `nil`, causing the inner function to return `nil`. The pcall succeeds with `result = nil`, which is returned at line 68.

**Verdict:** PASS — missing items correctly produce `nil` with no fallback text, no error, and no alternative display.

### B.2: Section Independence Check

**File:** `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua`

The `getAllSections(item)` function (lines 286-325) assembles sections sequentially:

1. `renderBasicInfoSection` (line 290) — reads item weight/type/module via `safeCall`. No Layer 3 dependency.
2. `renderTagsSection` (line 293) — reads tags from `IrisAPI.getTagsForItem`. No Layer 3 dependency.
3. **Layer 3 block** (lines 296-310) — standalone pcall-guarded block that:
   - Loads `layer3_renderer` via pcall (line 298)
   - Gets fullType from item (lines 301-305)
   - Calls `Layer3Renderer.getText(fullType)` (line 307)
   - Inserts result only if non-nil (line 308)
   - If renderer fails to load, `Layer3Renderer` stays nil and entire block is skipped
4. `renderFoodSection` (line 312) — reads hunger/thirst/stress. No Layer 3 dependency.
5. `renderWeaponSection` (line 315) — reads damage/range/durability. No Layer 3 dependency.
6. `renderConnectionSection` (line 318) — reads recipe/moveables/fixing from IrisAPI. No Layer 3 dependency.
7. `renderMiscSection` (line 321) — reads capacity/light/waterproof. No Layer 3 dependency.

**v1.1 sections:**
- `renderCoreInfoSection` (lines 345-395) — reads weight, type, damage, durability, thirst, hunger from item object methods. No reference to Layer 3 data, IrisLayer3Data, or layer3_renderer.
- `renderRecipeInfoSection` (lines 399-413) — reads recipe count from IrisAPI. No Layer 3 dependency.
- `renderMetaInfoSection` (lines 415-468) — reads tags and module name from IrisAPI and item. No Layer 3 dependency.
- `renderUseCaseSection` (lines 561-604) — reads use-case lines from IrisAPI. Uses `IrisUseCaseLabelMap`, not Layer 3 data.

**Verdict:** PASS — Layer 3 rendering is fully independent. No other section reads from `IrisLayer3Data` or `layer3_renderer`. The Layer 3 block is self-contained with its own pcall guard and nil-check gate.

### Pilot B Summary

| Check | Result |
|---|---|
| getText() returns nil for missing items | PASS |
| No fallback text for missing entries | PASS |
| pcall failure returns nil silently | PASS |
| renderCoreInfoSection independent of L3 | PASS |
| renderConnectionSection independent of L3 | PASS |
| renderMetaInfoSection independent of L3 | PASS |
| renderUseCaseSection independent of L3 | PASS |
| **Overall Pilot B** | **PASS** |

---

## Final Verdict

| Pilot | Status |
|---|---|
| Pilot A (APPROVE_SYNC acquisition text) | **PASS** |
| Pilot B (HOLD/SILENT non-display) | **PASS** |
| **Menu Pilot Overall** | **PASS** |
