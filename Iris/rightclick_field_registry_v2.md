# Right-click Field Registry v2

> **원칙**: 필드는 Evidence 결과로만 생성/갱신된다. 수동 고정 목록은 존재하지 않는다.  
> Iris는 "의미 시스템"이 아닌 "결정적 Evidence 시스템"

---

## 1. Purpose

이 문서는 우클릭 행동 증거 시스템에서 **Field(필드)**가 어떻게 생성·갱신·동결되는지를 정의하는 **Registry 계약**이다.

v1의 "고정 Allowlist(7개 can_*)"를 폐기하고, 아래 파이프라인을 유일한 필드 산출 경로로 고정한다.

```
items_itemscript.json + 정적 우클릭 소스/인덱스
        ↓  Phase 0
  evidence_decisions.json   (FullType → STRONG/WEAK/NO/REVIEW + 근거 + 제외 사유)
        ↓  Phase 1  (REVIEW 항목은 field_registry에 포함하지 않고 별도 격리)
  field_registry.json       (필드 목록 + 각 필드가 커버하는 Evidence 아이템 집합)
        ↓  Phase 2 (선택)
  동결 스냅샷 태깅
```

---

## 2. Definitions

### Evidence

아이템이 특정 우클릭 행동을 수행할 수 있다는 **정적 근거**.  
판정 기준 A/B/C/D의 충족 여부로 `STRONG / WEAK / NO / REVIEW`를 결정한다.

#### 판정 등급

| 등급 | 의미 |
|---|---|
| `STRONG` | A/B/C/D 모두 충족 + 해당 행동에 대한 유일성이 높음 (전용 FullType 의존) |
| `WEAK` | A/B/C/D 모두 충족 (Evidence 통과). 단, 유일성이 약함 (대체 가능 아이템 다수) |
| `NO` | A/B/C/D 중 하나 이상 미충족 또는 Exclusion 체크 해당. 필드 생성 불가 |
| `REVIEW` | 판정 불확실. 필드 생성하지 않고 격리 큐에 보관 |

#### A/B/C/D 체크리스트 요약

> 정식 정의는 상위 계약 문서 `rightclick_evidence_source_allowlist_v2.md`(A/B/C/D 근거 타입 허용 계약)에서 관리한다.  
> 아래는 본 Registry 계약의 실행을 위한 최소 요약이다. **구현 시 반드시 상위 문서를 참조할 것.**

| 기준 | 체크 항목 |
|---|---|
| **A — 정적 소스 존재** | 해당 우클릭 행동이 정적 소스(Lua 파일/테이블/함수)에서 식별 가능한가? |
| **B — 외부 대상에 대한 아이템 연결** | 특정 아이템(FullType)이 해당 행동의 **외부 대상**(플레이어 신체/환경 오브젝트/다른 아이템 등)에 대해 정적으로 연결되는가? |
| **C — 지속적 변화 유발** | 해당 행동이 대상에게 **되돌리기 어려운 상태 변화**(수치 변경/상태 전이/구조 변경 등)를 일으키는가? |

| 별도 체크 | 체크 항목 |
|---|---|
| **Exclusion — 제외 규칙** | Recipe / Consumption / Equip / Passive / Auto에 해당하는가? 해당 시 판정 대상에서 제외 |

| 재현성 | 체크 항목 |
|---|---|
| **D — 재현 가능** | 동일 입력으로 동일 판정 결과가 재현되는가? |

### Field

동일한 우클릭 행동 Evidence 성격을 공유하는 아이템 집합을 표현하는 **ID**.

- 필드의 정체성은 **정적 근거(Anchor)**로만 식별된다.
- 의미·설명문·카테고리명으로 필드를 정의하는 것은 금지한다.

### Anchor (근거)

필드를 식별하는 정적 출처. 코드 경로 / 함수 / 테이블 / 정적 predicate 등이 해당한다.

- 같은 Anchor → 같은 필드
- Anchor가 변경되면 필드도 버전 갱신 대상이 된다.

#### Anchor 최소 구성요건 (필수)

모든 Anchor는 아래 3개 속성을 반드시 포함해야 한다.

| 속성 | 설명 | 예시 |
|---|---|---|
| `anchor.kind` | Anchor의 유형 | `lua_function` / `lua_table` / `predicate` / `file_span` |
| `anchor.ref` | 정규화된 식별자 (파일+심볼 또는 테이블 키) | `ISInventoryTransferAction.lua::performAction` / `SuburbsDistributions.BagTable` |
| `anchor.version` | Anchor가 참조하는 소스의 버전 태그 | `b42.1` / `commit:abc1234` |

#### Anchor 동일성 규칙

- 두 Anchor의 동일성은 **`kind` + `ref`** 조합으로만 판정한다.
- `version`이 다르더라도 `kind` + `ref`가 같으면 동일 Anchor로 취급한다 (버전 갱신).
- `kind` 또는 `ref`가 하나라도 다르면 별개의 Anchor이다.

---

## 3. Pipeline Phases

### Phase 0: Evidence Decisions 생성

- **입력**: `items_itemscript.json` + 정적 우클릭 소스/인덱스
- **출력**: `evidence_decisions.json`
  - 각 FullType에 대해 `STRONG / WEAK / NO / REVIEW` 판정
  - 판정 근거 (A/B/C/D 충족 여부)
  - 제외 사유 (해당 시)
  - `REVIEW` 항목은 `review_reason` 필드를 필수로 포함
- 제외 규칙: Recipe / Consumption / Equip / Passive / Auto에 해당하면 제외

### Phase 1: Field Registry 생성/갱신

- **입력**: `evidence_decisions.json`
- **출력**: `field_registry.json` + `review_queue.json`
  - `field_registry.json`: 필드 목록 + 각 필드가 커버하는 Evidence 아이템 집합
  - `review_queue.json`: `REVIEW` 판정 항목의 격리 목록 (FullType + review_reason)
- `STRONG` / `WEAK` 판정만 필드 생성 대상이 된다. `REVIEW`는 `review_queue.json`으로 격리하며 필드에 포함하지 않는다.
- Evidence 결과를 입력으로 하여 필드를 산출한다.
- "필드가 필요해 보이니 만들자"는 금지. "Evidence 결과로 생성된다"만 허용.

### Phase 2: 동결/버전 태깅 (선택)

- 배포/릴리즈 시점에만 `field_registry.json`을 **동결 스냅샷**으로 태그한다.
- 동결 이후에도 다음 Evidence 파이프라인 실행 시 리뉴얼 가능.

---

## 4. Field ID Rules

### Naming (강제)

- 의미 단어 기반 ID 금지 (예: ~~`medical_tools`~~, ~~`repair_actions`~~)
- Field ID는 **Anchor에서 결정적으로 파생**되어야 한다 (수동 명명 금지).
- 형식: `rc.<anchor.kind>.<anchor.ref의 정규화 slug>`
  - slug 생성 규칙: `anchor.ref`에서 파일 확장자 제거 → 구분자를 `_`로 치환 → 소문자 변환
  - 예: Anchor `{kind: "lua_function", ref: "ISInventoryTransferAction::performAction"}` → Field ID: `rc.lua_function.isinventorytransferaction_performaction`
- `action_key`를 사용할 경우, 해당 키 역시 **정적 근거(Anchor.ref)로부터만** 파생되어야 한다.

### Stability

- 필드 동일성 판단 기준은 **Anchor 동일성**이다 (의미 동일성이 아님).
- 같은 코드 경로/정의에 의해 발생하는 행동이면 같은 필드.
- Anchor가 바뀌면 필드가 바뀌어도 정상이다 (버전 갱신).

### Anchor Cardinality (강제)

- 필드당 Anchor는 **N개 가능**하다 (동일 행동이 여러 파일/함수에서 정의되는 현실 케이스 대응).
- 단, Field ID는 **대표 Anchor 1개**에서 결정적으로 파생한다.
- 대표 Anchor 선정 규칙: 해당 필드에 속한 Anchor 중 `anchor.ref`의 **사전순 최소값**을 대표로 삼는다.
- 대표 Anchor가 변경되면 (예: 사전순 최소 Anchor가 제거됨) Field ID도 갱신 대상이 된다.

### Merge / Split

- 두 필드의 Anchor가 동일 출처로 수렴하면 → Merge 가능
- 하나의 필드 Anchor가 분리되면 → Split 가능
- 판단 기준은 항상 Anchor이며, 의미적 유사성은 근거가 될 수 없다.

---

## 5. Creation Rules

필드는 아래 조건을 **모두** 만족할 때만 생성 가능하다.

| 조건 | 설명 |
|---|---|
| Evidence 존재 | 해당 필드에 속할 Evidence 아이템이 **최소 1개 이상** 존재 |
| 정적 재현성 | 집합을 만드는 근거가 **정적이고 재현 가능** |
| 제외 규칙 통과 | Recipe / Consumption / Equip / Passive / Auto 제외 규칙에 걸리지 않음 |
| 애매함 격리 | 판정이 애매하면 필드 생성이 아닌 **REVIEW로 격리** |

---

## 6. Validation Rules (Fail-loud)

v1의 "∉ allowlist → Fail"을 폐기하고, 아래 **계약 위반**을 Fail 조건으로 정의한다.

| 위반 유형 | 설명 |
|---|---|
| 금지 근거 사용 | UI 문자열 / 이름 패턴 / 설명문 기반으로 필드를 생성·판정한 경우 |
| 비결정적 분류 | 동일 입력에 대해 결과가 흔들리는 경우 |
| 수동 추가 | 필드가 근거 없이 수동으로 추가된 경우 |
| 출력 포맷 위반 | JSON 스키마가 7절 Outputs에 정의된 구조와 불일치하는 경우 |
| 정렬 규칙 위반 | `evidence_decisions.json`은 FullType 사전순, `field_registry.json`은 Field ID 사전순으로 정렬되지 않은 경우 |
| 중복 규칙 위반 | 동일 FullType이 `evidence_decisions.json`에 2회 이상 등장하거나, 동일 아이템이 `field_registry.json` 내 2개 이상의 필드에 중복 등록된 경우 |

> 정렬 및 중복 규칙의 상세 검증 로직은 `rightclick_resolution_rules_v1.md`에서 정의한다. 본 문서는 위반 시 Fail 판정을 내리는 계약만 고정한다.

### 금지 필드 (필드 내 포함 불가 속성)

- ❌ description (설명)
- ❌ meaning (의미)
- ❌ action_name (행동명)
- ❌ menu_label (메뉴명)

---

## 7. Outputs

| 산출물 | Phase | 형식 |
|---|---|---|
| `evidence_decisions.json` | Phase 0 | FullType별 STRONG/WEAK/NO/REVIEW + 근거 + 제외 사유 |
| `field_registry.json` | Phase 1 | 필드 목록 + 각 필드의 Evidence 아이템 집합 |
| `review_queue.json` | Phase 1 | REVIEW 판정 항목 격리 목록 (FullType + review_reason) |
| 동결 스냅샷 | Phase 2 | `field_registry.json`의 버전 태그된 사본 |

---

## 8. References

| 문서 | 역할 |
|---|---|
| `rightclick_evidence_source_allowlist_v2.md` | A/B/C/D 근거 타입 허용 계약 |
| `rightclick_resolution_rules_v1.md` | 정렬/중복/출력 검증 로직의 상세 정의 |

---

## 버전 정보

- **Version**: v2
- **Created**: 2026-02-08
- **Revised**: 2026-02-18
- **Status**: Active
- **Supersedes**: `rightclick_capability_allowlistv1.md`
