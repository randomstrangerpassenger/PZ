# Right-click Evidence Pipeline - Fail Conditions v2

> **원칙**: Fail은 "결과가 마음에 안 듦"이 아니라, 파이프라인이 **결정적/재현 가능/금지 근거 미사용** 계약을 어겼을 때만 발생한다.  
> 애매함은 Fail이 아니라 REVIEW로 격리한다.

---

## 1. Scope / Purpose

이 문서는 v2 Evidence 파이프라인의 각 단계에서 발생하는 **Fail / REVIEW / NO** 조건을 정의한다.

v1의 "Capability ID ∉ allowlist → Fail" 전제를 폐기하고, 아래 파이프라인 단계별로 계약 위반만을 Fail로 정의한다.

```
Phase S: Source Index 규칙 로딩     (rightclick_source_index_v2.json)
Phase C: Candidate 생성             (evidence_candidates.json)
Phase D: Decision 산출              (evidence_decisions.json)
Phase F: Field Registry 생성        (field_registry.json)
```

### 상위 계약

| 문서 | 역할 |
|---|---|
| `rightclick_field_registry_v2.md` | Field 생성/갱신/동결 계약 |
| `rightclick_source_index_v2.json` | Extraction Rule 인덱스 |
| `rightclick_evidence_source_allowlist_v2.md` | A/B/C/D 근거 타입 허용 계약 |
| `rightclick_resolution_rules_v1.md` | 정렬/중복/출력 검증 로직 |

---

## 2. Severity Levels

| 등급 | 의미 | 파이프라인 영향 |
|---|---|---|
| **FAIL** | 계약 위반. 해당 단계 즉시 중단 | 산출물 생성 불가. 수동 검토 필수 |
| **REVIEW** | 판정 불확실. 자동 결론 불가 | 해당 항목만 격리. 나머지 파이프라인은 계속 진행 |
| **NO** | 제외 규칙에 의해 "Evidence 아님"이 결정적으로 증명됨 | 정상 산출. 필드 생성 대상에서 제외 |

---

## 3. FAIL Conditions

### 3-A. Forbidden Evidence Source 사용 (Critical)

**헌법/금지 위반. 최우선 Fail.**

다음 근거를 사용하여 candidate를 생성하거나 decision을 산출한 경우 즉시 Fail.

| 금지 근거 | 예시 |
|---|---|
| UI 문자열 | DisplayName, 번역 문자열, tooltip 텍스트 |
| 설명문 기반 | description, meaning, menu_label |
| 이름 패턴 매칭 | 아이템명/파일명의 문자열 패턴으로 도구/행동 추정 |
| 런타임 함수 결과를 후보 추출 기준으로 사용 | `runtime_condition`이나 `excluded_matchers`에 격리된 동적 판단을 matchers로 사용 |

**적용 Phase**: S, C, D, F 전체

```
로그: [FAIL:FORBIDDEN_SOURCE] Phase={phase}, rule_id='{rule_id}', forbidden_source='{source}'
```

---

### 3-B. Non-deterministic Pipeline (Critical)

**재현성 계약 위반. 동일 입력에 동일 출력이 보장되지 않으면 Fail.**

| 위반 유형 | 설명 |
|---|---|
| 전역 비결정 | 동일 입력(`items_itemscript.json` + `source_index`)으로 실행할 때마다 결과가 달라짐 |
| 정렬 불안정 | `evidence_decisions.json`이 FullType 사전순이 아니거나 `field_registry.json`이 Field ID 사전순이 아님 |
| 중복 처리 불안정 | 동일 FullType이 동일 단계에서 상충하는 결정을 받음 |

**적용 Phase**: C, D, F

```
로그: [FAIL:NON_DETERMINISTIC] Phase={phase}, input_hash='{hash}', detail='{detail}'
```

> **중요**: "특정 rule이 후보를 결정적으로 뽑지 못함"은 Fail이 아니라 **REVIEW**(4절 참조). 여기서의 Fail은 **파이프라인 전체의 재현성**이 깨진 경우만 해당.

---

### 3-C. Output Contract 위반 (Critical)

**산출물의 기계 계약 위반.**

| 위반 유형 | 설명 |
|---|---|
| 필수 필드 누락 | decision에 A/B/C/D proof 누락, REVIEW 항목에 `review_reason` 누락 등 |
| 스키마 불일치 | JSON 구조가 해당 Phase 산출물 스키마와 불일치 |
| 정렬 규칙 위반 | `evidence_decisions.json`: FullType 사전순 / `field_registry.json`: Field ID 사전순 |
| 중복 규칙 위반 | 동일 FullType이 `evidence_decisions.json`에 2회 이상 등장, 또는 동일 아이템이 `field_registry.json` 내 2개 이상 필드에 중복 등록 |
| Anchor 포맷 위반 | `anchor.ref`가 `source_index_v2.json` 스키마의 `ref_format_by_kind`에 정의된 강제 포맷과 불일치 |
| Field ID 파생 위반 | Field ID가 대표 Anchor에서 결정적으로 파생되지 않음 (`field_registry_v2.md` 4절 Naming 강제 규칙 위반) |

**적용 Phase**: C, D, F

```
로그: [FAIL:OUTPUT_CONTRACT] Phase={phase}, file='{output_file}', violation='{detail}'
```

> 정렬 및 중복 규칙의 상세 검증 로직은 `rightclick_resolution_rules_v1.md`에서 정의한다.

---

### 3-D. Cross-Phase Inconsistency (Critical)

**단계 간 계약 모순.**

| 위반 유형 | 설명 |
|---|---|
| Exclusion 무시 | candidates에서 `exclusions.*=true`인데 decisions가 STRONG/WEAK로 통과시킨 경우 |
| Unknown 근거 없는 확정 | candidates에서 `prove.*=unknown`인데 decisions가 해당 기준을 "충족"으로 처리한 경우 (근거 없이 확정) |
| REVIEW 누락 격리 | decisions에서 `REVIEW`인데 `review_queue.json`에 해당 항목이 없는 경우 |
| NO 항목 필드 등록 | decisions에서 `NO`인데 `field_registry.json`에 해당 아이템이 필드에 등록된 경우 |

**적용 Phase**: D → F 간 교차 검증

```
로그: [FAIL:CROSS_PHASE] from={source_phase}, to={target_phase}, fulltype='{fulltype}', detail='{detail}'
```

---

## 4. REVIEW Conditions

**판정 불확실. 자동 결론 불가. 해당 항목만 격리하고 파이프라인은 계속 진행.**

| 조건 | 해당 Phase | 설명 |
|---|---|---|
| Proof 일부 unknown | C → D | `prove.executing_tool`, `prove.external_target`, `prove.persistent_change` 중 하나 이상이 `unknown` |
| 후보 집합 비결정 | C | Rule의 `matchers`가 비어있거나 `extract_blocked_reason`이 존재 |
| property_based exclusion | C → D | `exclusions.property_based=true`로 자동 결론 불가 |
| Excluded matcher 해당 아이템 | C | `excluded_matchers`에 해당하는 아이템 (정적 결정 불가 property 등) |

**처리**: `review_queue.json`에 격리. `review_reason` 필수 기재.

```
로그: [REVIEW] Phase={phase}, rule_id='{rule_id}', fulltype='{fulltype}', reason='{reason}'
```

---

## 5. NO Conditions

**제외 규칙에 의해 "Evidence 아님"이 결정적으로 증명됨. 정상 산출.**

| Exclusion 플래그 | 설명 |
|---|---|
| `recipe` | Recipe Track 해당 (keep 도구 등) |
| `consumption` | 소비/소모 행위 |
| `equip` | 장착/착용 행위 |
| `passive` | 수동적 속성 (장착 시 효과 등) |
| `auto` | 자동 발동 행위 |
| `input_material` | 입력 재료/부착물 패턴 |

**처리**: `evidence_decisions.json`에 `decision: "NO"` + `exclusion_reason` 기재.

```
로그: [NO] fulltype='{fulltype}', exclusion='{exclusion_flag}', rule_id='{rule_id}'
```

---

## 6. Validation Checklist (Phase별)

### Phase S: Source Index 규칙 로딩

- [ ] 모든 rule의 `anchor`가 `ref_format_by_kind` 강제 포맷에 부합하는가?
- [ ] `matchers`의 `match_type`이 허용 목록(type/tag/property/category/display_category) 내인가?
- [ ] `match_type=property`인 matcher가 items_itemscript.json에서 정적으로 확인 가능한 키인가? (불가 시 `excluded_matchers`로 이동 필요)
- [ ] `runtime_condition`이 matchers와 분리되어 있는가?
- [ ] 금지 근거(UI 문자열/이름 패턴/설명문)가 matchers에 포함되어 있지 않은가?

### Phase C: Candidate 생성

- [ ] 각 candidate의 FullType이 `items_itemscript.json`에 실존하는가?
- [ ] candidate 생성에 `runtime_condition`이나 `excluded_matchers` 항목이 사용되지 않았는가?
- [ ] `matchers`가 비어있는 rule의 후보가 REVIEW로 격리되었는가?

### Phase D: Decision 산출

- [ ] 모든 decision에 A/B/C/D proof가 포함되어 있는가?
- [ ] `REVIEW` 판정에 `review_reason`이 포함되어 있는가?
- [ ] `exclusions.*=true`인 candidate가 STRONG/WEAK로 통과하지 않았는가?
- [ ] `prove.*=unknown`인 항목이 해당 기준 "충족"으로 확정되지 않았는가?
- [ ] FullType 사전순 정렬이 유지되는가?
- [ ] 동일 FullType 중복이 없는가?

### Phase F: Field Registry 생성

- [ ] STRONG/WEAK 판정만 필드에 등록되었는가?
- [ ] REVIEW 항목이 `review_queue.json`에 격리되었는가?
- [ ] NO 항목이 필드에 등록되지 않았는가?
- [ ] Field ID가 대표 Anchor에서 결정적으로 파생되었는가?
- [ ] Field ID 사전순 정렬이 유지되는가?
- [ ] 동일 아이템의 다중 필드 등록이 없는가?

---

## 7. Examples

### FAIL 예시: Forbidden Source

```
Phase C에서 아이템 "KitchenKnife"의 DisplayName("부엌칼")을 근거로
"절단 도구" candidate를 생성함.
→ [FAIL:FORBIDDEN_SOURCE] Phase=C, rule_id='manual', forbidden_source='DisplayName'
```

### FAIL 예시: Cross-Phase Inconsistency

```
Phase C에서 rule_worldobject_predicatepetrol의 prove.executing_tool=unknown인데,
Phase D에서 해당 아이템의 A(정적 소스) 기준을 "충족"으로 확정함.
→ [FAIL:CROSS_PHASE] from=C, to=D, fulltype='Base.PetrolCan', detail='prove.executing_tool=unknown but A marked as met'
```

### REVIEW 예시: Proof Unknown

```
Phase C에서 rule_worldobject_predicatepetrol의 prove 전항목이 unknown.
exclusions.property_based=true.
→ [REVIEW] Phase=C, rule_id='rule_worldobject_predicatepetrol', fulltype='Base.PetrolCan', reason='property_based exclusion + prove all unknown'
```

### NO 예시: Recipe Exclusion

```
Phase D에서 CanOpener 아이템이 rule_canopener_recipe_exclusion에 의해
exclusions.recipe=true로 증명됨.
→ [NO] fulltype='Base.CanOpener', exclusion='recipe', rule_id='rule_canopener_recipe_exclusion'
```

---

## Fail 처리 절차

```
1. Fail 감지
2. 로그 출력 (파일 + 콘솔) - 로그 포맷은 3절의 Phase별 템플릿 준수
3. 해당 Phase 즉시 중단 (후속 Phase 진행 금지)
4. 개발자에게 수동 검토 요청
```

> REVIEW는 Fail이 아님. REVIEW 항목은 격리 후 파이프라인을 계속 진행한다.

---

## 버전 정보

- **Version**: v2
- **Created**: 2026-02-08
- **Revised**: 2026-02-18
- **Status**: Active
- **Supersedes**: `rightclick_fail_conditions_v1.md`
