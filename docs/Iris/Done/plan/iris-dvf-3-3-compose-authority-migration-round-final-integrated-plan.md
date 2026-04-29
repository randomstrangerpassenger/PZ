# Iris DVF 3-3 Compose Authority Migration Round Final Integrated Plan

> 상태: Draft v0.2  
> 기준일: 2026-04-20  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/Iris/Done/dvf_3_3_compose_v2_spec.md`, `docs/Iris/Done/iris-dvf-3-3-compose-contract-migration-execution-plan.md`, `docs/Iris/Done/dvf_3_3_information_type_contract.md`, `docs/Iris/Done/dvf_3_3_cross_layer_overlay_spec.md`  
> authority input: `DVF 3-3 Compose Authority Migration Round — 최종 로드맵` (2026-04-20 user-provided roadmap)  
> 목적: `sentence_plan` runtime authority를 `body_plan`으로 교체하는 별도 authority migration round의 scope, phase order, sealed boundary, execution artifact, exit gate를 canonical plan으로 고정한다.  
> 실행 상태: planning authority only. 이 문서는 A/B/C 집행 요구와 exit gate를 고정하지만, 완료를 선언하지 않는다. 이후 실제 top docs patch, code mutation, runtime/publish mutation은 후속 execution step에서 생성된다.

> 이 문서는 "본문을 더 좋게 쓰는 계획"이 아니다.  
> 이 문서는 **`sentence_plan` compose authority를 `body_plan`으로 교체하는 실행 계획**이다.

---

## 0. Round Identity와 Opening Baseline

### 0-1. Round identity

| 항목 | 값 |
|---|---|
| round 이름 | `Iris DVF 3-3 compose authority migration round` |
| round 성격 | execution-planning authority round |
| 핵심 질문 | `sentence_plan` runtime authority를 `body_plan`으로 어떻게 교체할 것인가 |
| canonical output | top docs Phase A patch, Phase B seam closeout, Phase C compose migration artifact |
| non-output | structural violation accounting redesign, full-runtime regression gate, runtime Lua consumer 변경 |

### 0-2. 한 문장 scope lock

> 이번 round는 "문장을 더 잘 쓰게 만들자"가 아니라, `sentence_plan -> body_plan` authority migration을 문서와 구현 양쪽에서 닫는 계획만 다룬다.

### 0-3. Scope

| 포함 | 제외 |
|---|---|
| Phase A - canonical authority 재선언 | Phase D - structural violation 계상 재설계 |
| Phase B - overlay seam / validator closeout | Phase E-0 - 전수 regression gate |
| Phase C - compose 교체 + profile migration + pilot/golden/determinism | Phase E - full-runtime rollout |

### 0-4. Phase dependency

```text
A -> (B 설계 / C 설계 병렬 가능)
A -> B close -> C 집행
A + B -> C 집행
C close -> D
```

운영 규칙은 아래처럼 고정한다.

- A gate는 먼저 닫혀야 한다.
- B와 C의 설계는 A 이후 병렬 가능하다.
- C의 실제 집행은 B closeout 이후에만 허용한다.
- D/E-0/E는 이번 round의 완료 조건에 넣지 않는다.

### 0-5. Current canonical base

- `docs/Iris/Done/dvf_3_3_compose_v2_spec.md`
- `docs/Iris/Done/iris-dvf-3-3-compose-contract-migration-execution-plan.md`
- `docs/Iris/Done/dvf_3_3_information_type_contract.md`
- `docs/Iris/Done/dvf_3_3_cross_layer_overlay_spec.md`

### 0-6. Current opening read

현재 opening baseline은 아래처럼 읽는다.

- `2026-03-25` 결정으로 `sentence_plan` 블록 단위 조합은 v1 표준 메커니즘으로 봉인돼 있다.
- `2026-04-05` 결정으로 body-role closeout은 `decisions overlay + compose 내부 repair`로 닫혀 있다.
- `2026-04-06` 결정으로 compose 외부 repair 금지와 single-writer contract가 봉인됐다.
- `2026-04-07` in-game validation pass와 `2026-04-08` surface contract authority migration fresh rerun pass까지 포함해, current runtime/bridge seal은 `2026-04-06 ~ 2026-04-08`에 걸쳐 닫혀 있다.
- `quality/publish decision stage` single writer와 `publish_state` runtime visibility contract는 위 봉인선 위에서 유지된다.
- 따라서 이번 round는 body-role round 재오픈이 아니라, **별도 authority lane에서 compose authority를 상위 교체**하는 round로 읽어야 한다.

---

## 1. 전역 봉인선

### 1-1. Existing decision compatibility

- `2026-03-25` `sentence_plan` 표준 결정은 폐기가 아니라 **legacy authority baseline** 으로 보존한다.
- `2026-04-05` body-role closeout은 유지한다.
- `2026-04-06` compose 외부 repair 금지 / single writer 결정은 유지한다.
- `2026-04-08` surface contract authority migration과 `publish_state` visibility contract는 유지한다.
- `2026-04-19` SAPR weak-family carry matrix는 유지한다.

### 1-2. Non-goals

이번 round에서 열지 않는 항목은 아래처럼 고정한다.

- structural violation 계상 체계 변경
- `quality_state / publish_state` axis 변경
- full-runtime row-count regression gate
- quality ratio 기준 재설계
- weak/strong distribution drift 기준
- publish split drift 기준
- runtime Lua consumer 변경
- facts 슬롯 확장
- style gate 승격
- 새 한국어·josa 엔진 도입
- `active / silent` 외부 계약 변경

### 1-3. Global guardrail

- runtime Lua는 render-only다.
- Browser/Wiki/Lua bridge는 compose를 대신하지 않는다.
- compose 외부 repair, post-validator rewrite, runtime patch는 금지다.
- validator는 non-writer다.
- `quality/publish decision stage` single writer는 유지된다.

---

## 2. Phase A — Canonical Authority 재선언

**목적:** 문제 1을 `compose authority migration round`로 top docs에 못 박아 B/C가 참조할 기준선을 확정한다.

### 2-1. Required outputs

- `docs/DECISIONS.md` 신규 항목 최소 4건
  - `sentence_plan` 기반 legacy 3-profile(`interaction_tool / interaction_component / interaction_output`) 운용을 `body_plan` 기반 new 6-profile로 교체한다. 이는 compose authority의 상위 교체이며, `2026-03-25 sentence_plan` 결정은 legacy authority baseline으로 보존한다.
  - Phase C compatibility adapter는 compose-internal non-writer bridge로만 운용하며, native `body_plan` 전환 완료 전까지 유지한다.
  - Phase C 실행 중 관측되는 structural signal은 Phase D semantic redesign 이전까지 observer-only로 유지한다.
  - legacy `quality_flag` family(`function_narrow / identity_only / acq_dominant_reordered`)는 Phase D family redesign 이전까지 existing family frozen 상태로 유지한다.
  - Iris DVF 3-3에서 compose authority migration은 body-role closeout / surface contract migration과 **별도의 authority lane** 으로 운영하며, 향후 재개방은 명시적 `scope_policy_override_round`로만 연다.
- `docs/ARCHITECTURE.md` 갱신
  - Layer 3 production authority 설명을 legacy `sentence_plan` 중심에서 `body_plan` 중심으로 재서술
  - `identity_core / use_core / context_support / acquisition_support / limitation_tail / meta_tail` 6개 section 계약 명시
  - single-writer 원칙 유지 명시
  - Phase A의 1차 반영과 Phase C closeout 이후의 2차 갱신을 모두 명시
- `docs/ROADMAP.md` addendum 작성
  - `Iris DVF 3-3 compose authority migration round`
  - `Done / Doing / Next / Hold` 4섹션 구성
  - `A + B + C`를 current round scope로, `D / E-0 / E`를 후속 lane으로 분리 명시
  - 기존 `Iris DVF 3-3 body-role roadmap closure addendum` 위에 compose authority 교체 레이어로 올라간다고 명시
  - 두 addendum 사이에 아래 cross-reference 문구를 둔다.
    - `본 addendum은 body-role closure addendum을 재오픈하지 않는다. 같은 3-3 layer의 authority migration을 별도 lane에서 다룬다.`
  - Hold에는 최소 아래 항목 포함
    - Phase D structural violation
    - 전수 regression gate
    - runtime Lua consumer 변경

### 2-2. Required contact points that must be pinned in Phase A

Phase A exit 전 아래 네 접점은 "추후 결정" 없이 문서에 박혀 있어야 한다. 단, 요구 수준은 **Phase C 동안의 임시 소비 규칙 봉인** 까지이며, final semantic redesign을 Phase A에 끌어오지 않는다.

| 접점 | Phase C 기간 동안의 요구 명시 |
|---|---|
| `LAYER4_ABSORPTION` hard block | Phase C 동안 `hard block 유지 / suspend / read-only` 중 어느 path인지 명시. final semantic 재정의는 요구하지 않음 |
| `quality_flag` family | Phase C 동안 writer input 아님 / advisory-only / existing family frozen 중 무엇인지 명시. final family redesign은 요구하지 않음 |
| `quality_state / publish_state` post-compose decision stage | body_plan rendered가 current stage input shape와 호환되는지, Phase C 기간 소비 방식만 명시 |
| `C-5 compatibility adapter` | 아래 §2-3의 6개 adapter 계약을 그대로 봉인 |

### 2-3. C-5 compatibility adapter contract

- adapter는 **non-writer**다. legacy `sentence_plan` 필드를 새 `body_plan` section 자리에 배치만 하며, 문장을 생성하지 않는다.
- 비어 있는 section은 그대로 compose에 넘긴다. 빈 section의 emission 또는 omission은 compose가 `body_plan` 규칙으로 결정한다.
- adapter는 `compose_layer3_text.py` **내부**에 위치한다. compose 호출 이전 외부 preprocessor 구조는 허용하지 않는다.
- adapter는 Phase C에서 도입되고, 기존 DVF에 등록된 3계층 설명이 모두 native `body_plan` path로 이전될 때까지 유지된다. 즉 성격은 **한시적 반영구 변환기**다.
- Phase C 이후 새로 등록되는 3계층 설명은 처음부터 native `body_plan` path를 사용한다.
- Phase C exit에서 adapter 경유 row의 상한 임계값은 두지 않는다. adapter 경유 row count는 `Phase D 입력 inventory`로만 추적되며, 점진적 native path 이전의 진행 지표로 사용한다.

### 2-4. Phase A review rule

- `dvf_3_3_information_type_contract.md`의 current top-doc reflected meaning과 drift가 없어야 한다.
- "body-role round 재오픈"으로 읽힐 문구를 제거해야 한다.
- Phase A는 초안 존재가 아니라 **canonical closure state** 를 만드는 단계다.

### 2-5. Exit gate

- `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`의 해당 항목 실제 기록 완료
- `dvf_3_3_information_type_contract.md` reflected meaning과 drift 없음
- 네 접점 답변이 top docs에 명시됨
- 재오픈 오해를 유발하는 문구 제거 완료

---

## 3. Phase B — Overlay Seam / Validator Closeout

**목적:** `body_source_overlay` 입력 seam과 validator 경계를 닫아, Phase C 구현자가 추측 없이 참조할 수 있는 입력 계약을 완성한다.

### 3-1. Input artifact

- `docs/Iris/Done/dvf_3_3_cross_layer_overlay_spec.md`
- Phase A closure 결과

### 3-2. Required outputs

- `body_source_overlay` schema closeout
  - writer가 body composition에서 읽는 입력 필드 고정
  - `facts / decisions / overlay` 책임 분리 고정
  - 기존 decisions overlay와의 관계 명시
    - `layer3_role_check`
    - `representative_slot`
    - `body_slot_hints`
    - `representative_slot_override`
  - overlap 여부, 우선순위, drift 감지 규칙 명시
- validator 경계 고정
  - validator 역할 한정
    - drift-checker / legality-checker까지만 수행
    - rendered 문장을 고치지 않음
    - `required / optional / required_any` legality만 검사
    - overlay 누락 / 중복 / 충돌에 대한 `hard fail / warn / skip` 판정 명시
  - Phase C 실행 중 structural signal 처리
    - 관측되는 structural signal(`LAYER4_ABSORPTION` 의심 포함)은 **observer-only** 로 기록된다.
    - structural signal은 Phase C exit blocker가 아니다.
    - semantic 판정 결정은 모두 Phase D의 책임이다.
    - 위 원칙은 `2026-04-05` body-role structural lint의 `next-build feedback` 원칙과 정합해야 한다.
- rendered flat string 규약 재확인
  - output은 계속 flat string
  - runtime consumer는 staged authority만 소비
  - browser / wiki / Lua bridge가 compose를 대신하지 않음
- forbidden path 정리
  - compose 외부 repair 금지
  - post-validator rewrite 금지
  - runtime patch 금지
  - style linter 승격 금지
  - overlay builder writer 승격 금지

### 3-3. Deliverables

- canonical `dvf_3_3_cross_layer_overlay_spec.md` 반영본
- `dvf_3_3_cross_layer_overlay_spec.md` appendix로 귀속되는 validator scope closeout
- `forbidden_patterns.json`
- seam legality checklist

### 3-4. Review rule

- `2026-04-06` single-writer 결정과 정합해야 한다.
- same-build rewrite 경로가 문서상 완전히 닫혀야 한다.
- B 설계는 C 설계와 병렬 가능하지만, C 집행 승인 gate를 대신하지 않는다.

### 3-5. Exit gate

- C 구현자가 `body writer가 먹는 입력`을 추측 없이 참조 가능
- `facts / decisions / overlay / validator / runtime` 책임 충돌 없음
- same-build rewrite path 문서상 폐쇄
- `dvf_3_3_cross_layer_overlay_spec.md`가 Phase B 소속으로 명시됨

---

## 4. Phase C — Compose Authority 전환 실행

**목적:** `Iris/build/description/v2/tools/build/compose_layer3_text.py`의 runtime authority를 `sentence_plan`에서 `body_plan`으로 실제 교체한다.

### 4-1. Prerequisites

- Phase A closure 필수
- Phase B closure 필수

### 4-2. C-1. Legacy inventory freeze

- 현재 `compose_profiles.json`의 legacy 3-profile inventory 추출
  - `interaction_tool`
  - `interaction_component`
  - `interaction_output`
- profile별 `required / optional` slot 구조 정리
- `compose_layer3_text.py`의 `sentence_plan` 독해 방식 inventory화
- legacy rendered snapshot baseline 저장

### 4-3. C-2. 3-to-6 profile crosswalk 확정

| legacy | new | 비고 |
|---|---|---|
| `interaction_tool` | `tool_body` | legacy direct path |
| `interaction_component` | `material_body` | legacy direct path |
| `interaction_output` | `output_body` | legacy direct path |
| - | `container_body` | 신규 분기 |
| - | `wearable_body` | 신규 분기 |
| - | `consumable_body` | 신규 분기 |

required artifact는 아래처럼 고정한다.

- `profile_migration_table.json`
- `profile_migration_inventory.json`
- `manual_rebucket_candidates.json`
- `profile_precedence_rules.md`

특히 `container / wearable / consumable` 분기 규칙이 기존 decisions overlay와 충돌하지 않는지 adversarial review에서 명시 확인해야 한다.

### 4-4. C-3. New 6-profile concrete draft

각 profile마다 아래 항목을 고정한다.

- required section
- optional section
- disallowed section
- section ordering
- `required_any` legality
- canonical flat-string render order

핵심 규칙은 아래 한 줄로 고정한다.

> Phase C는 "문장 1/2/3 설계"가 아니라 **section emission 규칙 설계**다.

### 4-5. C-4. Body writer implementation

`compose_layer3_text.py`의 실제 구현 변경 범위는 아래처럼 고정한다.

- legacy `sentence_plan` reader 분리
- `body_plan` builder 추가
- section emission engine 추가
- flat-string renderer 추가
- optional emission rules 추가
- deterministic section ordering 보장
- compose 내부 repair만 허용
- writer는 하나뿐이며 validator/runtime는 writer가 아님

### 4-6. C-5. Compatibility adapter operation

Phase A §2-2의 네 번째 접점과 §2-3의 adapter 계약을 Phase C 구현에 그대로 적용한다.

- adapter는 `sentence_plan -> body_plan` **한시적 반영구 변환기** 이며 동시에 non-writer다. legacy 필드를 section 자리에 배치만 하고 문장을 생성하지 않는다.
- 빈 section은 그대로 compose에 넘기며, emission 또는 omission은 compose가 `body_plan` 규칙으로 결정한다.
- adapter 위치는 `compose_layer3_text.py` 내부로 고정한다. 외부 preprocessor path는 금지한다.
- 기존 등록 row는 모두 native `body_plan` path 전환 완료 시점까지 adapter를 경유할 수 있다.
- Phase C 이후 신규 등록 row는 처음부터 native `body_plan` path를 사용한다.
- adapter 경유 row count는 임계값 없이 추적만 하며, `Phase D 입력 inventory` 로 보존한다.

### 4-7. C-6. Pilot corpus / golden subset / determinism validation

pilot corpus 기준은 아래처럼 고정한다.

- 총량: `40~60`
- 6 profile 전부 포함
- legacy 3-profile에서 자연 전이되는 row 포함
- ambiguous / manual rebucket 사례 포함
- 경계 사례 포함
- 선정 방식은 `random / stratified / targeted` 중 실제 사용 방식과 분포 근거를 명시

golden subset seed 기준은 아래처럼 고정한다.

- profile별 최소 `5`개
- `strong / adequate / weak` 각각 포함
- `acquisition-heavy / identity-heavy / use-heavy / mixed body` 혼합
- 어느 사례가 경계인지 명시
- 이후 drift 감지 기준이 되는 seed artifact로 고정

determinism pass 기준은 아래처럼 고정한다.

- 동일 입력 2회 실행
- section order identical
- rendered identical
- hash identical
- 범위: pilot corpus 전체 + golden seed 전체

legacy diff review 기준은 아래처럼 고정한다.

- changed row inventory 생성
- intentional / accidental 분리
- `accidental changed = 0` 목표

### 4-8. C-7. Preview authority promotion

- staged rendered artifact 생성
- Lua bridge preview artifact 생성
- Browser/Wiki sample reflection 확인
- `deployed_matches_staged` preview comparison 수행

### 4-9. Phase C deliverables

| 분류 | artifact |
|---|---|
| 문서 | `profile_migration_spec.md`, `phase_c_exit_gate.md` |
| 데이터 | `profile_migration_table.json`, `profile_migration_inventory.json`, `manual_rebucket_candidates.json`, `golden_subset_seed.json`, `pilot_corpus_manifest.json` |
| 검증 | `compose_determinism_report.json`, `legacy_vs_bodyplan_diff_report.json` |
| 코드 | `compose_layer3_text.py` 개정, `compose_profiles_v2.json`, compose-internal adapter path, validator updates |

### 4-10. Exit gate

| 기준 | 수치 |
|---|---|
| pilot corpus pass | `40~60` |
| golden seed pass | 신규 profile별 최소 `5`개, `strong / adequate / weak` 포함 |
| determinism pass | pilot + golden 전체 2회 동일 출력 |
| migration table adversarial review | pass |
| `dvf_3_3_compose_v2_spec.md` adversarial review | pass |

### 4-11. Explicitly sealed out of Phase C gate

아래는 Phase C exit gate에 넣지 않는다.

- full-runtime row count 기반 regression gate
- adapter 경유 row count 상한 임계값
- quality ratio 기준
- weak/strong distribution drift 기준
- publish split drift 기준
- `unexpected delta = 0`
- `publish_state` 역행 없음

이 항목들은 각각 Phase D / E-0 / E로 이관한다. 단, adapter 경유 row count 상한 임계값은 Phase D로 이관되는 gate가 아니라, Phase D의 adapter 제거 조건 확정 작업으로 다른 형태로 대체된다.

---

## 5. Five-Cycle Operating Cadence

| 주기 | 작업 |
|---|---|
| 1주기 | A close / B close / legacy inventory freeze |
| 2주기 | 3-to-6 crosswalk artifact / new 6-profile concrete draft / manual rebucket inventory |
| 3주기 | compose writer 구현 / adapter 연결 / local pilot run |
| 4주기 | pilot corpus 검수 / golden subset 고정 / determinism pass / diff review |
| 5주기 | preview authority promotion / Lua + Browser smoke check / closeout docs 반영 |

이 cadence는 **권장 주기**이며 고정 일정이 아니다.

- A closeout review 재검토
- B seam 수정 요청
- pilot corpus 재선정

같은 피드백이 발생하면 cadence는 확장될 수 있다. 각 주기는 상한이 아니라 **기준**이다.

---

## 6. Sealed Decisions This Round Must Not Violate

| 날짜 | 결정 | 이번 round와의 관계 |
|---|---|---|
| 2026-03-25 | `sentence_plan` 블록 단위 조합은 v1 표준 메커니즘 | 폐기 아님. `body_plan`이 상위 authority로 교체 |
| 2026-04-05 | body-role 개편은 decisions overlay + compose 내부 repair로 닫힘 | 그 위에서의 authority 교체. 재오픈 아님 |
| 2026-04-06 | compose 외부 repair 금지 / single writer 계약 | writer 교체이지 writer 추가가 아님 |
| 2026-04-08 | layer boundary contract violation 분류 | Phase D에서 section 기준 재정의 대상 |
| 2026-04-19 | SAPR weak-family carry matrix | quality axis 변경 없음 |

---

## 7. Hold

이번 round에서 열지 않는 Hold는 아래처럼 고정한다.

- structural violation 계상 체계 변경 -> Phase D
- `quality_state / publish_state` axis 변경 -> `2026-04-06` 봉인 유지
- 전수 regression gate 집행 -> Phase E-0
- runtime Lua consumer 변경 -> Phase E
- facts 슬롯 확장 -> 기존 body-role hold 유지
- style gate 승격
- 새 한국어·josa 엔진
- `active / silent` 외부 계약 변경

---

## 8. Round Completion Criteria

§8의 10개 항목은 round completion criteria이며, §4-10 Phase C exit gate를 **포함한다**. `#1`, `#3`, `#10`은 Phase A/B closeout 관련 조건이고, `#4 ~ #9`는 Phase C exit과 정합한다. 단, `#9`의 legacy diff accidental change 판정은 Phase C exit 이후 최종 closeout 시점에 확정된다.

아래 10개가 모두 만족돼야 round close로 읽는다.

1. top docs가 이번 round를 **authority migration round** 로 일관되게 설명한다. 여기에는 Phase A의 1차 반영과 Phase C closeout 이후의 2차 architecture 갱신이 모두 포함된다.
2. A/B closeout 이후 `facts / overlay / validator / writer / runtime` 경계가 흔들리지 않는다.
3. A closeout 이후 네 접점(`LAYER4_ABSORPTION` / `quality_flag` / post-compose decision stage / `C-5 compatibility adapter`)의 Phase C 작동 방식이 문서에 박혀 있다.
4. legacy `3 -> 6` crosswalk가 artifact 수준으로 고정된다.
5. adapter 경유 row를 포함한 **모든 row가 `body_plan` section emission 규칙에 따라 조립**되며, `compose_layer3_text.py`의 주 권위가 `sentence_plan`이 아니라 `body_plan`이 된다.
6. pilot corpus `40~60`개 통과.
7. 신규 profile별 대표 아이템 최소 `5`개 확보, `strong / adequate / weak` 각각 포함.
8. 동일 입력 2회 compose 시 동일 section order / 동일 출력 보장.
9. legacy diff에서 accidental change가 허용 범위 밖으로 남지 않는다. 이 판정은 Phase C exit 이후 최종 closeout 시점에 확정된다.
10. structural violation / audit redesign은 이번 종료 조건이 아니라고 문서에 명시된다.

---

## 9. Next Round Candidates

이번 round 이후에만 열 수 있는 후보는 아래처럼 고정한다.

- Phase D
  - `body_plan` 기반 rendered 안정화 이후 structural violation 계상 체계 재설계
  - `LAYER4_ABSORPTION` section 기준 재정의
  - `IDENTITY_ONLY / BODY_LACKS_ITEM_SPECIFIC_USE / FUNCTION_NARROW / ACQ_DOMINANT`의 body_plan section 기준 재분류
  - adapter 경유 row의 native `body_plan` path로의 점진적 이전
  - adapter 제거 조건 확정
- Phase E-0
  - `unexpected delta = 0`
  - `publish_state` 역행 없음
  - full regression gate 재설계
- Phase E
  - 전수 row `body_plan` compose 적용
  - runtime Lua 재배포

---

## 10. Final Round Reading

이번 round의 최종 reading은 아래 두 문장으로 고정한다.

> 이 round는 body-role round 재오픈이 아니다.  
> 이 round는 `sentence_plan` authority를 `body_plan` authority로 교체하는 별도 compose migration round다.

또한 아래 문장도 함께 봉인한다.

> structural violation redesign, full regression gate, runtime Lua consumer 변경은 이번 round의 종료 조건에 포함되지 않는다.
