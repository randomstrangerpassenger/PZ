# Iris Track Boundaries v2

> **원칙**: 이 문서는 전체 아이템 스캔에서 **무엇을 Gate-0(우클릭 Evidence)로 보내고, 무엇을 제외(NO)하고, 무엇을 격리(REVIEW)할지**를 결정적으로 고정하는 **라우팅 계약**이다.  
> 트랙 분류는 정적 근거 + exclusion 플래그로만 결정한다. 의미/추측에 의한 라우팅은 금지.

---

## 1. Purpose

이 문서의 역할은 3가지로 한정된다.

1. **트랙(Track) 목록을 정의 기반으로 고정**: 트랙은 기능 이름이 아니라 제외 규칙(exclusion)으로만 나뉜다
2. **제외(NO)와 격리(REVIEW)의 경계를 명확히 고정**: 결정적 제외 vs 자동 결론 금지를 라우팅 규칙으로 구분
3. **라우팅 근거를 허용 목록에 묶기**: 경계 판정은 `rightclick_evidence_source_allowlist_v2.md`에서 허용한 근거 타입으로만 수행

이 문서는 다음을 하지 **않는다**:
- Evidence 판정(STRONG/WEAK) 산출 (→ `rightclick_resolution_rules_v2.md`)
- Field 생성/갱신 (→ `rightclick_field_registry_v2.md`)
- FAIL 조건 정의 (→ `rightclick_fail_conditions_v2.md`)

---

## 2. Track Definitions

| Track | 목적 | 라우팅 조건 |
|---|---|---|
| **Gate-0 RightClick Evidence Track** | STRONG/WEAK/NO/REVIEW 산출 대상 | 아래 제외/격리 조건에 해당하지 않는 모든 후보 |
| **Recipe Track** | 레시피 기반 요구/도구/재료. Gate-0에서 제외 | `exclusions.recipe=true` |
| **Excluded Track** | 정의상 Gate-0 대상이 아닌 항목 | `exclusions.consumption/equip/passive/auto/input_material=true` |
| **REVIEW Queue** | 자동 결론 금지. 수동 검토 대기 | `exclusions.property_based=true` 또는 `prove.*`에 unknown 존재 |

- 트랙은 **정의(exclusion 플래그)로만** 나뉜다.
- "유용해 보인다", "의료/수리 행동이다" 같은 의미 사유로 트랙을 넘나드는 것은 금지.

---

## 3. Inputs

| 입력 | 설명 |
|---|---|
| `evidence_candidates.json` | FullType별 병합된 후보 (prove/exclusions/anchors) |
| `rightclick_evidence_source_allowlist_v2.md` | 라우팅 판정에 허용된 근거 타입 |

라우팅은 **Candidate 병합 직후, Decision 산출 직전**에 수행한다.

```
source_index → evidence_candidates.json → [라우팅(본 문서)] → evidence_decisions.json
```

---

## 4. Routing Rules

### 라우팅 테이블 (강제 우선순위)

아래 순서대로 적용하며, **상위 조건에서 라우팅이 결정되면 하위 조건은 평가하지 않는다.**

| 순위 | 조건 | Route | Decision Flag | 비고 |
|---|---|---|---|---|
| 1 | 금지 근거 사용 흔적 감지 | — | **FAIL** | `rightclick_fail_conditions_v2.md` 3-A. 신호 위치: candidate 생성 과정에서 `forbidden_source_detected=true` 플래그가 설정된 경우 작동 |
| 2 | `exclusions.recipe=true` | Recipe Track | **NO** | recipe 관련 산출물로만 이동 |
| 3 | `exclusions.consumption=true` | Excluded Track | **NO** | Eat/Drink/Read 계열 |
| 4 | `exclusions.equip=true` | Excluded Track | **NO** | Equip/Unequip 행위 |
| 5 | `exclusions.passive=true` | Excluded Track | **NO** | 수동적 속성 (장착 시 효과 등) |
| 6 | `exclusions.auto=true` | Excluded Track | **NO** | 자동 발동 행위 |
| 7 | `exclusions.input_material=true` | Excluded Track | **NO** | 입력 재료/부착물 패턴 |
| 8 | `exclusions.property_based=true` | REVIEW Queue | **REVIEW** | 자동 결론 금지 (정책) |
| 9 | `prove.*` 중 하나라도 `unknown` | REVIEW Queue | **REVIEW** | 추론 금지 |
| 10 | 위 조건에 해당 없음 | Gate-0 Evidence Track | (다음 단계로) | `evidence_decisions.json` 산출 진행 |

### 라우팅 근거 제약

모든 라우팅 판정은 `rightclick_evidence_source_allowlist_v2.md`에서 허용한 근거 타입으로만 수행해야 한다.

| 판정 대상 | 허용 근거 |
|---|---|
| recipe 여부 | `recipe_tool_requirement` (결정적 근거만) |
| consumption/equip | itemscript 필드 (정적) |
| passive/auto | 정적 이벤트 훅/자동 tick 정의 (결정적 근거만) |
| input_material | `itemscript_display_category` 등 |
| property_based | `property_based_container_logic` |

UI 문자열/메뉴 텍스트로 "이건 우클릭이겠지" 같은 판정은 금지 (→ FAIL).

---

## 5. Conflict Rules

하나의 FullType에 여러 exclusion 플래그가 동시에 true인 경우, **4절 라우팅 테이블의 순위가 우선순위를 결정한다.**

| 충돌 예시 | 적용 |
|---|---|
| `recipe=true` + `consumption=true` | 순위 2(recipe) 우선 → Recipe Track, NO |
| `recipe=true` + `property_based=true` | 순위 2(recipe) 우선 → Recipe Track, NO |
| `input_material=true` + `property_based=true` | 순위 7(input_material) 우선 → Excluded Track, NO |
| `property_based=true` + prove에 unknown | 순위 8(property_based) 우선 → REVIEW Queue |

원칙: **결정적 제외(NO)가 격리(REVIEW)보다 항상 우선한다.** REVIEW는 "판정 불가"일 때만 적용된다.

---

## 6. Outputs

| 산출물 | Track | 설명 |
|---|---|---|
| Gate-0로 진행 | Gate-0 Evidence Track | `evidence_decisions.json` 산출 대상 (STRONG/WEAK 판정) |
| `evidence_decisions.json`에 NO 기록 | Recipe Track / Excluded Track | `decision: "NO"` + `exclusion_reason` |
| `review_queue.json`에 격리 | REVIEW Queue | `decision: "REVIEW"` + `review_reason` |

> Recipe Track과 Excluded Track의 NO 항목은 `evidence_decisions.json`에 함께 기록되며, `exclusion_reason`으로 구분한다. 별도 파일 분리는 선택 사항이다.

---

## 7. Forbidden Routing Patterns

### 금지 1: 의미 기반 트랙 분류

```
❌ "이 아이템은 의료 도구이므로 Gate-0로 보낸다"
❌ "이 아이템은 수리 도구이므로 Excluded Track으로 보낸다"
→ FAIL: 의미/카테고리 추론에 의한 라우팅
```

### 금지 2: Track 간 데이터 참조

```
❌ Recipe Track의 결과를 Gate-0 Evidence 판정에 사용
❌ Gate-0 Evidence 판정 결과를 Recipe Track에 피드백
→ FAIL: Track 간 교차 참조
```

### 금지 3: 런타임 기반 라우팅

```
❌ 게임 실행 중 관측한 우클릭 메뉴 출현 여부로 트랙 결정
❌ 프로파일링 데이터로 "이 아이템은 자주 우클릭되므로 Gate-0"
→ FAIL: 런타임/관측 기반 라우팅
```

---

## 8. Cross-Document Links

| 문서 | 책임 분리 |
|---|---|
| `rightclick_fail_conditions_v2.md` | 금지 근거 사용 / 비결정성 / 출력 계약 위반 / Cross-Phase 모순 시 FAIL |
| `rightclick_resolution_rules_v2.md` | Gate-0로 라우팅된 후보의 Decision 산출 (STRONG/WEAK/NO/REVIEW) + Candidate 병합 |
| `rightclick_field_registry_v2.md` | Decision 결과로 Field 생성/갱신/동결 |
| `rightclick_evidence_source_allowlist_v2.md` | 라우팅 판정에 허용된 근거 타입 정의 |
| `rightclick_source_index_v2.json` | Extraction Rule 인덱스 (anchor/extract/prove/exclusions) |

---

## 버전 정보

- **Version**: v2
- **Created**: 2026-02-08
- **Revised**: 2026-02-18
- **Status**: Active
- **Supersedes**: `rightclick_track_boundaries_v1.md`
