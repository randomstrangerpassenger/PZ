# DVF Semantic Boundary Validation Report (Step 9)

**Version:** 1.0
**Date:** 2026-03-15
**Scope:** dvf_3_3_rendered.json semantic boundary check + layer independence audit
**Rendered JSON:** v2.0, 1089 entries (all APPROVE_SYNC — original 1050 + CPR 39, 0 silent, 0 override)

---

## 1. Semantic Content Audit (10+ Representative Items)

### Audit Criteria

For each item, verify:
- (A) text_ko is acquisition-oriented (acq_location or acq_method)
- (B) No internal info leaks (classification IDs like `Tool.1-A`, module names like `Base.` as standalone, tag identifiers)
- (C) Neutral tone: no recommendations, comparisons, or evaluations

### Sampled Items

| # | fullType | text_ko (decoded) | (A) Acq? | (B) Leak? | (C) Tone? |
|---|---|---|---|---|---|
| 1 | Base.223BulletsMold | 탄약. 모루 근처에서 철괴와 망치, 집게로 제작한다. | acq_method | CLEAN | Neutral |
| 2 | Base.AlcoholBandage | 의료 용품. 붕대를 소독하거나 끓여서 만든다. | acq_method | CLEAN | Neutral |
| 3 | Base.Aluminum | 재료. 주방이나 전기 공구 보관 장소에서 발견된다. | acq_location | CLEAN | Neutral |
| 4 | Base.Antibiotics | 의약품. 가정집이나 의료 시설에서 발견된다. | acq_location | CLEAN | Neutral |
| 5 | Base.AssaultRifle | 근접 무기. 군용 무기 보관 장소와 총기 보관 장소, 특수 총기 진열대에서 발견된다. | acq_location | CLEAN | Neutral |
| 6 | Base.BlowTorch | 소모성 도구. 철물점이나 금속 작업장에서 발견된다. | acq_location | CLEAN | Neutral |
| 7 | Base.Boilersuit_Prisoner | 의류. 교도소 수감자 구역에서 발견된다. | acq_location | CLEAN | Neutral |
| 8 | Base.CraftedFishingRod | 낚싯대. 나무막대와 낚싯줄, 종이클립이나 못으로 제작한다. | acq_method | CLEAN | Neutral |
| 9 | Base.Crowbar | 무기 겸용 도구. 작업 차량과 차고, 공구 상자와 공구점에서 발견된다. | acq_location | CLEAN | Neutral |
| 10 | Base.Lighter | 조명 기구. 차량과 책상, 담배 판매대와 주거지 주방에서 발견된다. | acq_location | CLEAN | Neutral |
| 11 | Base.ConcretePowder | 재료. 공사 자재 보관 장소와 작업장에서 발견된다. | acq_location | CLEAN | Neutral |
| 12 | Base.DenimStrips | 재료. 데님 의류를 찢어 얻는다. | acq_method | CLEAN | Neutral |
| 13 | Base.Dogfood | 식품. 가정집이나 애완용품 판매점에서 발견된다. | acq_location | CLEAN | Neutral |
| 14 | Base.TriggerCrafted | 전자 기기. 수신기와 전자 부품으로 만든다. | acq_method | CLEAN | Neutral |
| 15 | farming.HandShovel | 원예 도구. 차고와 농업 물품 상자, 원예 상점과 공구점에서 발견된다. | acq_location | CLEAN | Neutral |

### Semantic Audit Result: PASS (15/15)

All sampled items follow the pattern: `[category label]. [acquisition sentence].`
- acq_location items describe where the item is found (locations, containers, vehicles)
- acq_method items describe how the item is crafted or obtained (materials, process)
- No item describes what the item does, how to use it, or interaction behavior

---

## 2. Internal Information Leak Scan

### Methodology

Automated regex scans on `dvf_3_3_rendered.json` (full file, 1089 entries):

| Pattern | Target | Matches |
|---|---|---|
| `Tool\.\d`, `uc\.`, `module\.` in text_ko | Classification IDs, internal namespaces | **0** |
| `Base\.[A-Z]` inside text_ko values | Module prefix leak as standalone identifier | **0** |
| Korean evaluative terms (추천/비교/평가/좋다/낫다/최고/우수) | Recommendation/comparison language | **0** |

### Manual Spot-Check

Reviewed 15 text_ko values across the full sample set. None contain:
- Classification system identifiers (e.g., `Tool.1-A`, `Weapon.2-B`)
- Module prefixes used as identifiers (e.g., `Base.` or `farming.` appearing in description text)
- Tag system identifiers or internal pipeline markers
- Source attribution strings (e.g., `composed`, `override`)

Note: The key names in the JSON use `Base.xxx` and `farming.xxx` format (as expected for fullType lookup keys), but these module prefixes do NOT appear inside any `text_ko` value. The grep scan for `Base.` inside text_ko content returned 0 matches.

### Leak Scan Result: PASS

---

## 3. Tone Verification

### Criteria

Text must NOT contain:
- Recommendations ("use this for...", "good for...")
- Comparisons ("better than...", "similar to...")
- Evaluations ("effective", "powerful", "best")

### Findings

All 15 sampled items and the automated scan of evaluative Korean terms confirm:
- Every text_ko uses declarative factual statements only
- Sentence pattern is consistently: `[발견된다/만든다/얻는다/제작한다]` (is found / is made / is obtained / is crafted)
- No subjective qualifiers, no comparative language, no recommendations

### Tone Result: PASS

---

## 4. Layer Independence Audit

### Objective

Verify that Layer 3 rendering in `IrisWikiSections.lua` is independent from Connection section (lines 216-250) and Meta section (lines 415-468), with no data source cross-contamination.

### Architecture Analysis

**File:** `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua` (606 lines)

#### Layer 3 Block (lines 296-310)

- **Data source:** `layer3_renderer.lua` -> `IrisLayer3Data` (global Lua table)
- **Input:** `item:getFullType()` -> string lookup in IrisLayer3Data table
- **Output:** Plain text string or nil
- **Dependencies:** Only `layer3_renderer` module (pcall-guarded)
- **Writes to shared state:** NONE (result inserted into local `sections` array only if non-nil)

#### Connection Section (lines 216-250)

- **Data source:** `IrisAPI.getRecipeConnectionsForItem`, `IrisAPI.getMoveablesInfoForItem`, `IrisAPI.getFixingInfoForItem`
- **Input:** `item` object passed to IrisAPI methods
- **Output:** Formatted string with recipe count, furniture registration, fixer status
- **Reads from Layer 3:** NO — uses only IrisAPI methods that query recipe/moveables/fixing systems
- **Cross-contamination:** NONE

#### Meta Section (lines 415-468)

- **Data source:** `IrisAPI.getTagsForItem`, `item:getModule():getName()`
- **Input:** `item` object
- **Output:** Formatted string with classification ID tags and module name
- **Reads from Layer 3:** NO — uses IrisAPI for tags and item object for module name
- **Cross-contamination:** NONE

#### UseCase Section (lines 561-604)

- **Data source:** `IrisAPI.getUseCaseLines(fullType)`, `IrisUseCaseLabelMap`
- **Reads from Layer 3:** NO — uses its own data pipeline (use-case lines, label maps)
- **Cross-contamination:** NONE

### Data Flow Diagram

```
IrisLayer3Data (global) --> layer3_renderer.getText() --> [Layer 3 text or nil]
                                                              |
IrisAPI (recipe/moveables) --> renderConnectionSection()      |  (no connection)
                                                              |
IrisAPI (tags) + item.getModule() --> renderMetaInfoSection() |  (no connection)
                                                              |
IrisAPI (use-case lines) --> renderUseCaseSection()           |  (no connection)
```

Each section reads from independent data sources. The `getAllSections` function assembles results into a flat array but sections do not read from or write to each other's data sources.

### Layer Independence Result: PASS

---

## 5. Rendered JSON Metadata Verification

| Field | Value | Status |
|---|---|---|
| version | 2.0 | OK |
| total entries | 1089 | OK (original 1050 + CPR 39) |
| active_composed | 1089 | OK (all entries are composed) |
| active_override | 0 | OK (no manual overrides) |
| silent | 0 | OK (all items have text) |
| override_ratio | 0.0 | OK |
| source field (all entries) | "composed" | OK (consistent) |

---

## Final Summary

| Check | Items Tested | Result |
|---|---|---|
| Acquisition-oriented content | 15 items | **PASS** |
| No classification ID leaks | 1089 items (automated) | **PASS** |
| No module name leaks in text | 1089 items (automated) | **PASS** |
| No evaluative/comparative tone | 1089 items (automated) + 15 manual | **PASS** |
| Layer 3 independence from Connection | Code audit | **PASS** |
| Layer 3 independence from Meta | Code audit | **PASS** |
| Layer 3 independence from UseCase | Code audit | **PASS** |
| No cross-contamination between layers | Architecture review | **PASS** |
| **Overall Step 9 Validation** | | **PASS** |
