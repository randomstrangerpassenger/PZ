# Right-click Evidence Resolution Rules v2

> **원칙**: 이 문서는 "분류 결과를 필드에 매핑"하는 규칙이 아니라,  
> **Evidence 후보를 병합 → 결정(STRONG/WEAK/NO/REVIEW) → 그 결과로 필드를 생성**하는 계약이다.

---

## 1. Purpose

이 문서는 v2 Evidence 파이프라인의 중간~최종 산출물을 만드는 **3가지 핵심 임무**를 계약으로 정의한다.

| 임무 | 입력 | 출력 |
|---|---|---|
| A — Candidate 병합 | `rightclick_source_index_v2.json`의 rule 적용 결과 | `evidence_candidates.json` |
| B — Decision 산출 | `evidence_candidates.json` | `evidence_decisions.json` |
| C — Field Registry 갱신 | `evidence_decisions.json` | `field_registry.json` + `review_queue.json` |

v1의 `capability_by_fulltype.json` 산출 구조를 폐기하고, 위 3단 파이프라인을 유일한 산출 경로로 고정한다.

---

## 2. Inputs

| 입력 | 설명 |
|---|---|
| `items_itemscript.json` | 전체 아이템 FullType + 정적 속성 |
| `rightclick_source_index_v2.json` | Extraction Rule 인덱스 (anchor/extract/prove/exclusions) |
| `rightclick_evidence_source_allowlist_v2.md` | A/B/C/D 근거 타입 허용 계약 |

---

## 3. Allowed / Forbidden Matching Sources

### 허용

| 유형 | 설명 | 예시 |
|---|---|---|
| **FullType 일치** | `Module.ItemType` 형식의 정확 일치 | `Base.Extinguisher`, `Base.PetrolCan` |
| **Type 일치** | ItemType 부분만 일치 (Module 무관) | `Extinguisher`, `Sandbag` |
| **Tag 일치** | scripts Tag 속성 | `Tags = Petrol`, `Tags = RemoveGlass` |
| **Property** | items_itemscript.json에서 정적으로 확인 가능한 속성만 | `IsWaterSource = true` (단, 정적 확인 불가 시 excluded_matchers로 격리) |
| **Category** | 스크립트 카테고리 | `Category = Food` |
| **DisplayCategory** | 스크립트 DisplayCategory | `DisplayCategory = WeaponPart` |

### 금지

| 유형 | 이유 |
|---|---|
| 이름 패턴 매칭 | `*Petrol*` 같은 글로브 패턴 금지 |
| 카테고리 추론 | 카테고리에서 의미 추론 금지 |
| 아이템 설명 기반 분류 | 설명문(description/meaning)은 데이터가 아님 |
| DisplayName 매칭 | 로케일 의존, 비결정적 |
| UI 문자열 | tooltip, 번역 문자열, menu_label 등 |
| 런타임 함수 결과 | `runtime_condition`/`excluded_matchers`에 격리된 동적 판단을 후보 추출에 사용 금지 |

> DisplayCategory ≠ DisplayName: DisplayCategory는 스크립트에 정의된 고정 분류값이며, 로케일 의존 표시 문자열이 아님.

---

## 4. 임무 A — Candidate 병합 규칙 (Accumulation)

여러 rule이 동일 FullType에 대해 proof/exclusion/anchors를 산출할 수 있다. 병합 규칙은 아래와 같이 강제한다.

### 병합 대상

동일 FullType끼리 merge한다.

### 병합 규칙

| 필드 | 병합 방식 |
|---|---|
| `anchors` | union (중복 제거) + `anchor.ref` 사전순 정렬. 대표 anchor 선정은 `rightclick_field_registry_v2.md` 4절 Anchor Cardinality 규칙 준수 |
| `prove.executing_tool` | true + false = **FAIL** (충돌). true + unknown = **true**. unknown + unknown = **unknown** |
| `prove.external_target` | 동일 규칙 |
| `prove.persistent_change` | 동일 규칙 |
| `exclusions.*` | 하나라도 true면 **true** (OR 병합). 우선순위 판정은 임무 B에서 처리 |
| `rule_ids` | 병합에 참여한 rule_id 목록 (추적용) |

### prove 충돌 = FAIL

동일 FullType에서 한 rule이 `prove.executing_tool=true`, 다른 rule이 `prove.executing_tool=false`를 산출하면 **즉시 FAIL**. 이는 `rightclick_fail_conditions_v2.md` 3-D (Cross-Phase Inconsistency)에 해당한다.

### 출력: `evidence_candidates.json`

```typescript
interface EvidenceCandidates {
  [fullType: string]: {
    anchors: Anchor[];          // union + ref 사전순 정렬
    prove: {
      executing_tool: boolean | "unknown";
      external_target: boolean | "unknown";
      persistent_change: boolean | "unknown";
    };
    exclusions: {
      recipe: boolean;
      consumption: boolean;
      equip: boolean;
      passive: boolean;
      auto: boolean;
      input_material: boolean;
      property_based: boolean;
    };
    rule_ids: string[];         // 병합에 참여한 rule 목록
  };
}
```

**정렬**: FullType 사전순. **중복 금지**: 동일 FullType 2회 이상 등장 시 FAIL.

---

## 5. 임무 B — Decision 규칙 (STRONG/WEAK/NO/REVIEW)

### Decision 우선순위 (강제 순서)

아래 순서대로 적용하며, **상위 단계에서 결정되면 하위 단계는 평가하지 않는다.**

| 순위 | 단계 | 조건 | 결과 |
|---|---|---|---|
| 1 | **FAIL 체크** | 금지 근거 사용 / 출력 계약 위반 / prove 충돌 | **FAIL** (파이프라인 중단) |
| 2 | **EXCLUSION 체크** | `exclusions` 중 결정적 제외 플래그가 true | **NO** |
| 3 | **PROPERTY_BASED 체크** | `exclusions.property_based=true` | **REVIEW** |
| 4 | **PROOF 체크** | `prove.*` 중 하나라도 `unknown` | **REVIEW** |
| 5 | **PASS 판정** | A(정적 소스) + B(외부 대상) + C(지속 변화) 모두 true + exclusions 모두 false | Evidence **통과** |
| 6 | **UNIQUENESS 체크** | 통과 후 유일성 판정 | **STRONG** 또는 **WEAK** |

### 순위 2 — EXCLUSION → NO 상세

아래 exclusion 플래그가 true이면 결정적으로 NO.

| Exclusion | 설명 |
|---|---|
| `recipe` | Recipe Track 해당 |
| `consumption` | 소비/소모 행위 |
| `equip` | 장착/착용 행위 |
| `passive` | 수동적 속성 |
| `auto` | 자동 발동 행위 |
| `input_material` | 입력 재료/부착물 패턴 |

> `property_based`는 여기에 포함하지 않는다. property_based는 순위 3에서 REVIEW로 격리한다 (자동 결론 금지 정책).

### 순위 3 — PROPERTY_BASED → REVIEW

`exclusions.property_based=true`인 경우, executing_tool 확정이 불가하므로 자동 결론을 금지하고 REVIEW로 격리한다.

### 순위 4 — PROOF UNKNOWN → REVIEW

`prove.executing_tool`, `prove.external_target`, `prove.persistent_change` 중 하나라도 `unknown`이면 REVIEW.

### 순위 6 — UNIQUENESS → STRONG/WEAK

Evidence 통과(순위 5) 이후에만 적용한다.

| 판정 | 조건 |
|---|---|
| **STRONG** | 해당 행동에 대한 유일성이 높음 (전용 FullType 의존) |
| **WEAK** | A/B/C/D 모두 충족(Evidence 통과). 단, 유일성이 약함 (대체 가능 아이템 다수) |

- 유일성 근거가 결정적으로 있으면 STRONG/WEAK 확정.
- 유일성이 불명확하면 **REVIEW**. WEAK를 디폴트로 사용하는 것은 금지 (추론에 해당).

### 출력: `evidence_decisions.json`

```typescript
interface EvidenceDecisions {
  [fullType: string]: {
    decision: "STRONG" | "WEAK" | "NO" | "REVIEW";
    proof: {
      A_static_source: boolean | "unknown";
      B_external_target: boolean | "unknown";
      C_persistent_change: boolean | "unknown";
    };
    exclusion_reason: string | null;    // NO인 경우 해당 exclusion 플래그
    review_reason: string | null;       // REVIEW인 경우 사유
    anchors: Anchor[];
    rule_ids: string[];
  };
}
```

> D(재현 가능성)는 아이템별 proof가 아니라 **파이프라인 전역 계약**이다. 7절 Determinism & Ordering Rules에서 런 단위로 검증하며, 아이템별 decision에는 포함하지 않는다.

**정렬**: FullType 사전순. **중복 금지**: 동일 FullType 2회 이상 등장 시 FAIL.

---

## 6. 임무 C — Field Registry 갱신

`evidence_decisions.json`을 입력으로 `field_registry.json`과 `review_queue.json`을 생성/갱신한다.

상세 규칙은 `rightclick_field_registry_v2.md`에서 정의한다. 이 문서에서는 연결 계약만 고정한다.

| Decision | Field Registry 처리 |
|---|---|
| **STRONG** | 필드 생성 대상. 해당 anchor 기반으로 필드에 등록 |
| **WEAK** | 필드 생성 대상. 근거 강도 표기 포함 |
| **NO** | 필드 생성 불가. `field_registry.json`에 등록 금지 |
| **REVIEW** | 필드 생성 불가. `review_queue.json`에 격리 |

### Cross-Phase 검증 (FAIL 조건)

| 위반 | 설명 |
|---|---|
| NO 항목 등록 | decisions에서 NO인데 field_registry에 등록됨 |
| REVIEW 누락 | decisions에서 REVIEW인데 review_queue에 없음 |
| Exclusion 무시 | candidates에서 exclusion=true인데 decisions가 STRONG/WEAK |
| Unknown 확정 | candidates에서 prove.*=unknown인데 decisions가 해당 기준 충족 처리 |

위반 시 `rightclick_fail_conditions_v2.md` 3-D에 의해 **FAIL**.

---

## 7. Determinism & Ordering Rules

### 결정성 (강제)

- 동일 입력(`items_itemscript.json` + `rightclick_source_index_v2.json`)으로 실행할 때마다 동일 출력이 보장되어야 한다.
- 비결정적 결과 = **FAIL** (`rightclick_fail_conditions_v2.md` 3-B).

### 정렬 규칙 (강제)

| 산출물 | 정렬 기준 |
|---|---|
| `evidence_candidates.json` | FullType 사전순 |
| `evidence_decisions.json` | FullType 사전순 |
| `field_registry.json` | Field ID 사전순 |
| `review_queue.json` | FullType 사전순 |

### 중복 규칙 (강제)

- 동일 FullType이 동일 산출물에 2회 이상 등장 시 FAIL.
- 동일 아이템이 `field_registry.json` 내 2개 이상 필드에 등록 시 FAIL.

### 금지 필드 (산출물 내 포함 불가)

- ❌ description (설명)
- ❌ meaning (의미)
- ❌ action_name (행동명)
- ❌ menu_label (메뉴명)

---

## 8. Examples

### STRONG

```
FullType: Base.Extinguisher
  prove: executing_tool=true, external_target=true, persistent_change=true
  exclusions: 전부 false
  → PASS (A/B/C 충족)
  → 유일성: Extinguisher 타입 전용 (대체 아이템 소수)
  → Decision: STRONG
```

### WEAK

```
FullType: Base.Tweezers
  prove: executing_tool=true, external_target=true, persistent_change=true
  exclusions: 전부 false
  → PASS (A/B/C 충족)
  → 유일성: SutureNeedleHolder도 동일 행동 가능 (대체 아이템 다수)
  → Decision: WEAK
```

### NO (Exclusion)

```
FullType: Base.CanOpener
  rule_canopener_recipe_exclusion에 의해 exclusions.recipe=true
  → 순위 2 EXCLUSION 체크에서 결정적 NO
  → Decision: NO, exclusion_reason: "recipe"
```

### REVIEW (Proof Unknown)

```
FullType: Base.PetrolCan
  prove: executing_tool=unknown, external_target=unknown, persistent_change=unknown
  exclusions.property_based=true
  → 순위 3 PROPERTY_BASED 체크에서 REVIEW
  → Decision: REVIEW, review_reason: "property_based exclusion + prove all unknown"
```

---

## 9. References

| 문서 | 역할 |
|---|---|
| `rightclick_field_registry_v2.md` | Field 생성/갱신/동결 계약 |
| `rightclick_source_index_v2.json` | Extraction Rule 인덱스 |
| `rightclick_evidence_source_allowlist_v2.md` | A/B/C/D 근거 타입 허용 계약 |
| `rightclick_fail_conditions_v2.md` | FAIL/REVIEW/NO 조건 정의 |

---

## 버전 정보

- **Version**: v2
- **Created**: 2026-02-08
- **Revised**: 2026-02-18
- **Status**: Active
- **Supersedes**: `rightclick_resolution_rules_v1.md`
