# EXECUTION_CONTRACT.md

> 상태: v1.3  
> 기준일: 2026-05-11  
> 발효일: 2026-05-11 이후 시작되는 execution에 적용된다.  
> 상위 기준: `Philosophy.md` → `DECISIONS.md` → `ARCHITECTURE.md` → `ROADMAP.md` → 모듈 authority 문서 → approved plan  
> 목적: Pulse 생태계 전체에서 execution이 따라야 할 disclosure 의무, evidence 요구, closeout 규율을 정의한다.

---

## 운영 원칙

- 이 문서는 **execution obligations 문서**다. governance specification이 아니다.
- 새 architecture, module policy, roadmap scope를 생성하지 않는다.
- 상위 문서와 충돌하면 상위 문서가 우선한다.
- 모듈 특화 정책은 모듈 authority 문서가 보유한다. 이 문서는 참조하되 흡수하지 않는다.
- 이 문서는 "execution이 어떻게 작업하는가"가 아니라, **무엇을 숨겨선 안 되는가**와 **무엇을 증거 없이 주장해선 안 되는가**를 정의한다.

---

## 1. Purpose, Scope, Non-Goals

### 1-1. Purpose

이 문서는 Pulse 생태계 전체에서 execution이 따라야 할 세 가지를 정의한다.

- **Disclosure 의무** — 무엇을 숨기면 안 되는가
- **Evidence 요구** — 무엇을 증거 없이 주장하면 안 되는가
- **Closeout 규율** — 작업을 닫을 때 어떻게 정직성을 유지하는가

### 1-2. Scope

- 적용 대상: Pulse, Echo, Fuse, Nerve, Iris, Frame, Cortex, Canvas, 그리고 이 생태계 내에서 수행되는 모든 internal execution.
- 적용 강도: §3 risk surface trigger와 §4 execution weight에 따라 달라진다. Surface를 만지지 않는 작업은 이 문서의 추가 의무를 지지 않는다.
- 적용 단위: round, phase, PR, closeout 등 execution이 식별 가능한 단위. 단위 정의 자체는 모듈 authority 문서 또는 approved plan이 정한다.
- **발효일 이전의 sealed decision 및 closeout naming은 retroactive로 reclassify되지 않으며, 모듈 authority 차원의 historical naming으로 보존된다.**

### 1-3. Non-Goals

이 문서가 정의하지 않는 것:

- 작업 방식 — refactor 방식, migration 단계, implementation 기법, 도구 선택, 코드 스타일.
- 모듈 정책 — 모듈별 허용 범위, 금지 범위, 디자인 방향, 정책 enum.
- 새 architecture rule, governance spec, ceremony framework, 평가 기준.
- 모듈별 검증 시나리오, 모듈별 success metric, 모듈별 sealing criteria.
- "deployment"의 의미 정의 — deployment의 의미는 모듈 authority 문서 또는 approved plan이 정의하며, 이 문서는 그 정의를 우회하는 증거 없는 주장만 금지한다.

이 항목들은 각각 모듈 authority 문서, approved plan, `ARCHITECTURE.md`, `ROADMAP.md`, `DECISIONS.md`가 정한다.

---

## 2. Authority Hierarchy

### 2-1. Reference Documents

- `Philosophy.md` — 유일한 헌법.
- `DECISIONS.md` — sealed decisions의 기록.
- `ARCHITECTURE.md` — 구조 지도 / 역할 경계 / 의존 방향.
- `ROADMAP.md` — 현재 상태와 다음 게이트.
- 모듈 authority 문서 — 각 모듈의 정책 / 운영 규약 / 검증 절차.
- Approved plan — 작업별 세부 제한, scope lock, PASS review condition, 단계 절차. 모듈 authority 문서보다 세밀하게 적용되며, 해당 plan의 scope 안에서 최종 실행 기준이 된다.
- 이 문서 (`EXECUTION_CONTRACT.md`) — 생태계 공통 disclosure / evidence / closeout 의무.

### 2-2. 충돌 시 우선순위

1. `Philosophy.md`
2. `DECISIONS.md`
3. `ARCHITECTURE.md`
4. `ROADMAP.md`
5. 모듈 authority 문서
6. Approved plan
7. 이 문서 (`EXECUTION_CONTRACT.md`)

### 2-3. 이 문서의 위치

- 이 문서는 상위 문서를 흡수하거나 재정의하지 않는다.
- 상위 문서의 내용을 복제하지 않으며, 참조만 한다.
- 상위 문서의 변경은 이 문서를 자동 편집하지 않는다. 단, 이 문서의 해석은 항상 최신 상위 authority read에 종속된다.
- 이 문서의 변경은 상위 문서를 변경하지 않는다.

---

## 3. Risk Surface Triggers

execution weight와 disclosure 의무를 판단하기 위한 공통 trigger surface는 다음과 같다. 이 목록은 governance taxonomy가 아니라 execution reporting을 위한 최소 판정 기준이다.

### 3-1. Authority Surface

- 모듈 authority 문서 또는 approved plan이 권위 / ownership / writer responsibility로 봉인한 field, stage, decision.
- `DECISIONS.md`에 sealed로 기록된 결정.

### 3-2. Runtime Behavior Surface

- 사용자에게 노출되는 런타임 동작.
- 모듈이 게임에 적용하는 개입 / 가드 / 안정화 / 표시 로직.
- 모듈의 기본값 (default ON/OFF, default policy).

### 3-3. Compatibility Surface

- 외부 모드와의 호환 경계.
- API surface, SPI 계약.
- 입출력 포맷 (JSON / SQLite / ZIP / 모듈별 외부 공유 포맷).

### 3-4. Sealed Artifact Surface

- closeout snapshot으로 봉인된 산출물 (sealed hash, sealed staged artifact 등).
- `DECISIONS.md` / `ROADMAP.md` / `ARCHITECTURE.md`에 기록된 sealed state.
- baseline freeze artifact.

### 3-5. Public-Facing Output Surface

- 사용자 의미, 공개 주장, 사용법, compatibility, safety, release 상태를 바꾸는 public-facing output.
- 대상: 게임 내 텍스트 / README의 기능·사용법·주의사항 / 공개 채널의 릴리스·호환성 메시지 / 모듈이 외부에 노출하는 UI 동작.
- 단순 오타 수정, 서식 변경, 의미 변화 없는 문구 정리는 이 surface에 해당하지 않는다.

### 3-6. Validation Limit (별도 분류 — §6-2 ceiling disclosure의 대상)

- §3-1~§3-5와 달리 "만지는 대상"이 아니라 execution이 가진 **검증 경계 자체**다.
- §4 weight scaling의 trigger가 아니라, §6-2 ceiling disclosure의 직접 대상이다.

---

## 4. Execution Weight Scaling

### 4-1. Light — Baseline

- §3-1~§3-5의 어느 surface도 만지지 않는 작업.
- 예: 모듈 내부 비공개 helper 변경, 주석 정리, 테스트 추가, 외부에 노출되지 않는 내부 리팩토링.
- 이 문서가 **추가로** 요구하는 disclosure / evidence / closeout 의무: 없음.
- 단, governing plan, PR rule, module authority 문서가 요구하는 기존 의무는 그대로 적용된다.

### 4-2. Medium — Disclosure-Required / Claim-Evidence Bound

- §3-2 Runtime Behavior 또는 §3-3 Compatibility 중 하나 이상을 만지지만, §3-1 / §3-4 / §3-5는 만지지 않는 작업.
- 이 문서가 기본으로 요구하는 의무: §5 disclosure 충족.
- 단, 해당 작업이 success, safety, runtime behavior preservation, compatibility preservation, validation pass를 주장하는 경우 §6 evidence requirement가 적용된다.

### 4-3. Heavy — Validation-Required

- §3-1 Authority Surface, §3-4 Sealed Artifact Surface, §3-5 Public-Facing Output Surface 중 하나라도 만지는 작업.
- 이 문서가 요구하는 의무: §5 disclosure + §6 evidence + §7 closeout discipline.

### 4-4. Scaling 원칙

- ceremony는 task의 존재가 아니라 **만진 surface가 결정**한다.
- Light에서 Medium / Heavy로의 격상은 작업별 risk surface 검토를 통해서만 일어난다.
- **이 문서만을 근거로** Light 작업에 추가 ceremony를 부과하지 않는다. governing plan, module authority 문서, PR rule이 별도로 요구하는 절차는 그대로 적용된다.

---

## 5. Disclosure Obligations

§3의 surface를 만진 모든 execution은 다음을 disclose한다. Disclosure는 PR / closeout / round artifact 중 한 곳에 명시적으로 기록되어야 하며, 위치는 모듈 authority 문서 또는 approved plan이 정한다.

### 5-1. Touched Authority Surfaces

- 어떤 권위 field / stage / sealed decision을 만졌는가.
- 만진 결과 ownership 또는 writer responsibility가 바뀌었는가.
- 만진 결과 권위 경계가 흐려졌는가.

### 5-2. Behavior-Affecting Changes

- 사용자가 런타임에서 볼 수 있는 동작이 어떻게 바뀌는가.
- 기본값이 바뀌었는가.
- 모듈의 개입 / 가드 / 안정화 로직이 바뀌었는가.

### 5-3. Compatibility-Affecting Changes

- 외부 모드와의 호환 경계가 바뀌었는가.
- API / SPI / 포맷이 바뀌었는가.
- 외부에 노출되던 surface가 제거되거나 의미가 바뀌었는가.

### 5-4. Public-Facing Output Changes

- §3-5에 해당하는 public-facing output이 바뀌었는가.
- 사용자 의미, 공개 주장, 사용법, compatibility, safety, release 상태에 영향을 주는 변경인가.

### 5-5. Sealed-Artifact Changes

- 봉인 산출물이 바뀌었는가.
- 바뀌었다면 어떤 reopen gate / governance documentation을 통과했는가.
- superseded된 봉인 산출물은 historical trace로 보존됐는가 (§7-5).

### 5-6. Module Policy Touchpoints

- 만진 surface가 모듈 authority 문서 또는 approved plan의 정책 영역에 해당하는가.
- 해당하면 해당 문서의 어느 항목에 비추어 disclosure하는가.
- 모듈 정책 위반이 있다면 명시적으로 disclose하고 해당 authority의 승인을 거친다.
- 이 문서는 모듈 정책 자체를 강제하지 않는다. disclosure 의무만 정의한다.

---

## 6. Evidence Requirements

§3의 surface를 만진 execution이 무언가를 주장(claim)하려면 다음을 만족한다.

### 6-1. Claim-Evidence Binding

- 모든 success claim은 그것을 뒷받침하는 검증 결과와 1:1로 연결된다.
- 검증 결과는 artifact / test result / validation report / in-game check / 봉인된 측정값 같은 식별 가능한 형태여야 한다.
- "통과했다"는 진술은 **어떤 검증이 어떤 입력에서 어떤 결과를 냈는가**가 명시되어야 한다.

### 6-2. Validation Ceiling Disclosure

§3 surface를 만지는 execution 또는 formal success claim을 하는 closeout은 자신이 수행한 검증의 한계를 다음 세 가지로 분리하여 기록한다.

| 구분 | 의미 |
|---|---|
| `validated` | 검증된 것 |
| `out_of_scope` | 검증되지 않았으나 이번 작업의 영향 밖에 있는 것 |
| `unvalidated_but_in_scope` | 검증되지 않았으나 이번 작업의 영향 안에 있는 것 |

`unvalidated_but_in_scope`이 비어 있지 않다면, 그 영역에 대한 success claim은 허용되지 않는다.

### 6-3. 증거 없는 주장 금지

**Formal closeout success claim**에서 다음 표현은 §6-1을 만족하지 않으면 사용할 수 없다. 일반 작업 대화나 진행 중 보고에는 적용되지 않는다. 각 그룹은 해당 언어에서 자주 쓰이는 formal claim 표현을 등재한 것이며, 두 그룹 사이의 1:1 번역 대응은 의도하지 않는다.

- 한국어: "통과", "성공", "안전", "검증됨", "완료"
- 영어: `release-ready`, `behavior-preserving`, `deployed`, `validated`, `complete`

추가 제한:

- runtime validation 없이 runtime success를 주장할 수 없다.
- deployment 없이 deployed completion을 주장할 수 없다.
- equivalence check 없이 behavior preservation을 주장할 수 없다 (unvalidated intent로는 표현 가능).

§6-3이 금지하는 `complete`는 §6-1을 만족하지 않은 채 쓰이는 naked formal claim이다. §7-1의 `complete` closeout state는 §7-2 ceiling 명시와 결합된 정의된 상태이며, 두 맥락은 구분된다.

증거가 없거나 ceiling 안에 남은 영역에 대해서는 §7-1의 정직한 closeout state를 사용한다.

---

## 7. Closeout Discipline

§4-3 Validation-Required execution이 closeout을 선언할 때 다음을 따른다.

### 7-1. Allowed Closeout States

| State | 의미 |
|---|---|
| `complete` | governing plan의 완료 조건이 stated validation ceiling 내에서 충족됨. **모든 `complete` 선언은 §7-2 validation ceiling 명시와 결합된 형태로만 의미를 가진다.** `complete` 명칭 단독 사용은 검증 여부를 보증하지 않는다. |
| `partial` | 계획된 scope의 일부만 완료됨 |
| `implemented_only` | 구현 완료, 요구 검증 미실시 |
| `blocked` | 외부 조건(missing authority, evidence, dependency, conflict, validation path)으로 진전 불가 |

봉인이 완료되지 않은 경우 위 state 중 적합한 것을 선택하고, §7-3 Non-Claims에 "sealed closeout 아님"을 명시한다. 별도 state를 도입하지 않는다.

모듈 authority 문서 또는 approved plan이 추가 state를 정의할 수 있다. 단, 추가 state는 위 4개 state 중 하나로 환원 가능해야 하며, §6-2 ceiling 명시 의무와 §6-3 증거 없는 주장 금지를 우회하지 않아야 한다.

### 7-2. Validation Ceiling 명시

- §4-3 Heavy execution의 모든 closeout은 §6-2의 ceiling을 명시한다.
- 검증되지 않은 surface는 명시적으로 `unvalidated`로 기록한다.
- **validation ceiling을 명시하지 않은 closeout은 `complete`로 닫을 수 없다.** 기록 누락은 "전부 검증됨"으로 간주하지 않는다.

### 7-3. Non-Claims 명시

closeout이 무엇을 선언하지 않는지를 명시한다.

> 예: "이 closeout은 deployed closeout이 아니다."  
> 예: "이 closeout은 manual in-game validation pass를 선언하지 않는다."  
> 예: "이 closeout은 `release-ready`를 선언하지 않는다."  
> 예: "이 closeout은 sealed closeout이 아니다."

closeout이 `DECISIONS.md` / `ROADMAP.md` / `ARCHITECTURE.md`의 sealed 상태를 자동으로 갱신하지 않는다. sealed 상태 갱신이 필요한 경우 명시적으로 disclose하고, 갱신은 해당 문서의 절차를 따른다.

### 7-4. Taxonomy Expansion 금지

closeout artifact에서 다음을 도입하지 않는다:

- 새 state enum
- 새 phase name (이미 정의된 round / phase의 새 인스턴스는 허용)
- 새 contract field
- 새 surface classification
- 새 quality / publish / runtime axis

새 분류가 필요하면 별도 design decision으로 분리하고, `DECISIONS.md` / `ARCHITECTURE.md` / 모듈 authority 문서를 통해 닫는다.

### 7-5. Historical Trace 보존

- closeout이 이전 상태를 superseded할 때, 이전 상태를 삭제하지 않고 historical trace로 남긴다.
- 봉인된 hash / artifact / decision은 superseded 표시와 함께 보존된다.

---

## 8. Non-Compliant Execution

다음 중 하나라도 해당하는 execution은 non-compliant이며 `complete`로 닫을 수 없다. 각 항목의 출처 섹션은 괄호로 표기한다.

- §6-1을 만족하지 않은 채 success를 주장함 (§6-1)
- 만진 authority / behavior / compatibility / public-output / sealed-artifact surface를 숨김 (§5)
- execution을 통해 architecture, module policy, roadmap scope를 확장함 (§1-3, §9-2)
- 이 문서를 design authority로 취급함 (§1-3, §9-1)
- 모듈 특화 정책을 ecosystem-wide 정책으로 전환함 (§9-5)
- runtime validation 없이 runtime success를 주장함 (§6-3)
- deployment 없이 deployed completion을 주장함 (§6-3)
- equivalence evidence 없이 behavior preservation을 주장함 (§6-3)
- blocked / partial / `implemented_only` 결과를 `complete`로 보고함 (§7-1)
- scope expansion을 disclose 없이 수행함 (§5)
- public-facing output 변경을 선언 없이 수행함 (§5-4)
- sealed artifact 변경을 traceable disclosure 없이 수행함 (§5-5)
- §7-2 validation ceiling을 명시하지 않은 채 `complete`를 선언함 (§7-2)
- closeout artifact에서 새 state / phase / contract field / surface classification을 도입함 (§7-4)

non-compliant execution의 closeout은 `blocked`, `partial`, `implemented_only`, 또는 다른 evidence-bounded state를 사용한다.

§9-4의 ceremony 부과 제한은 이 섹션의 self-check에도 적용된다. §4-1 Light / §4-2 Medium execution은 별도의 §8 checklist 작성 의무를 지지 않는다. 단, §8의 non-compliance 기준 자체를 우회할 수는 없다.

---

## 9. Self-Restraint Boundaries

이 문서가 governance spec으로 비대화되지 않기 위한 자기 제한.

### 9-1. 흡수 / 재정의 금지

이 문서는 `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, 모듈 authority 문서, approved plan의 어떤 내용도 복제 / 흡수 / 재정의하지 않는다.

### 9-2. 새 정책 생성 금지

이 문서는 새 architecture rule, 새 module policy, 새 roadmap scope를 만들지 않는다. disclosure / evidence / closeout 규칙만 정의한다.

### 9-3. 작업 방식 강제 금지

refactor 방식, migration 단계, implementation 기법, 도구 선택, 코드 스타일은 이 문서가 제약하지 않는다. unnecessary restriction의 판정 기준은 §3(risk surface trigger)과 §5(disclosure) 두 축이다.

### 9-4. Ceremony 부과 제한

**이 문서만을 근거로** §3의 surface를 만지지 않는 작업에 추가 ceremony를 부과하지 않는다. §4-1 Baseline을 §4-2 / §4-3으로 자동 격상시키는 일반 규칙을 만들지 않는다. governing plan, module authority 문서, PR rule이 별도로 요구하는 절차는 이 제한의 영향을 받지 않는다.

### 9-5. 모듈 정책 흡수 금지

모듈별 허용 범위 / 금지 범위 / 디자인 방향 / 정책 enum은 모듈 authority 문서 또는 approved plan이 정한다. 이 문서는 모듈 정책을 강제하지 않고, execution이 모듈 정책을 disclose할 의무만 정의한다(§5-6).

### 9-6. 이 문서의 변경 절차

이 문서의 변경은 원칙적으로 감축, 정정, 명확화에 한정한다. 새 surface trigger, 새 disclosure 항목, 새 closeout state 추가는 기존 문서로 처리할 수 없는 반복적 execution ambiguity가 있을 때만 허용하며, §9-1~§9-5를 위반하지 않아야 한다.

비대화 신호 — 특정 모듈 patrol, 새 architecture rule, 새 ceremony framework, 모듈별 검증 시나리오 흡수 — 가 감지되면 해당 부분을 적절한 상위 문서로 이관한다.
