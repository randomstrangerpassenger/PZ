# DVF 3-3 Body Role Execution Plan

> 상태: draft v0.3  
> 기준일: 2026-04-05  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`

> 이 문서는 상위 문서의 하위 운영 계획 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

---

## 0. 목적

이 문서는 2026-04-05 body-role roadmap과 최종 검토 피드백을 반영해, 현재 DVF 3-3 경로에 맞는 실행 순서를 다시 고정한다.

이번 수정의 핵심은 다섯 가지다.

- facts 슬롯 확장을 하지 않는다.
- repair 규칙은 compose 외부 단계가 아니라 compose 내부 분기로 흡수한다.
- Phase 번호 체계를 0~9로 단일화한다.
- `surface_active / runtime_only` 같은 신규 상태 축을 만들지 않는다.
- 구조 패턴 경고는 새 축이 아니라 기존 semantic axis와 `layer3_role_check`에 연결한다.

---

## 1. 고정 제약

### 1-1. facts는 현행 유지

다음 facts 슬롯 추가는 하지 않는다.

- `representative_use`
- `secondary_use`
- `distinctive_mechanic`

본문 배치 판단은 facts가 아니라 decisions overlay에서 처리한다.

### 1-2. compose 외부 repair 단계 금지

별도 `layer3_body_repair.py` 같은 독립 단계는 두지 않는다. repair 규칙은 `compose_layer3_text.py` 내부 조합 흐름의 일부로만 존재한다.

### 1-3. 신규 상태 축 금지

다음 신규 상태 축은 만들지 않는다.

- `surface_quality`
- `surface_active`
- `runtime_only`

품질 강등이 필요하면 기존 2-stage status model의 semantic axis와 연결한다.

### 1-4. `quality_flag`는 진단 메타데이터로만 제한

`quality_flag`는 rendered 산출물의 진단 메타데이터로만 사용한다.

- runtime 소비자와 Lua bridge 계약으로 승격하지 않는다.
- 상태 축으로 사용하지 않는다.
- Phase 7 회귀 검증과 Phase 4 피드백 연결에만 사용한다.
- 허용값은 다음 셋으로 고정한다.
  - `function_narrow`
  - `identity_only`
  - `acq_dominant_reordered`

### 1-5. Phase 번호만 사용

본문 실행 순서와 산출물 설명은 `Phase 0 ~ Phase 9`만 사용한다. 묶음 실행은 참고 섹션에서만 다룬다.

---

## 2. 현재 기준선

### 2-1. 현재 입력/출력 경로

- facts: `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
- decisions: `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
- compose entrypoint: `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- style normalizer: `Iris/build/description/v2/tools/style/normalizer.py`
- style linter: `Iris/build/description/v2/tools/style/linter.py`
- Lua bridge: `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
- runtime consumer: `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`

### 2-2. full-rendered 기준선과 fixture 구분

- full-rendered 기준선: `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview.rendered.json`
- fixture output: `Iris/build/description/v2/output/dvf_3_3_rendered.json`

SHA-256 비교와 baseline-delta 검증은 full-rendered 기준선으로 수행한다. `output/dvf_3_3_rendered.json`은 fixture로만 유지한다.

### 2-3. 현재 확인된 구조 갭

- decisions에는 `layer3_role_check`가 없다.
- compose는 아직 `primary_use` 중심 단일 경로다.
- structural pattern과 semantic axis가 아직 연결돼 있지 않다.
- style linter는 현재 advisory-only이며 body-role 전용 구조 패턴 세트가 없다.

---

## 3. 수정된 Phase 계획

## Phase 0. 기준선 재봉인

### 목적

3-3의 역할을 상위 문서에 종속된 execution policy로 다시 문서화한다.

### 산출물

- `docs/dvf_3_3_body_role_policy.md`
- `docs/3_3_vs_3_4_boundary_examples.md`

### 문구 규칙

두 문서 모두 서두에 다음 문장을 명시한다.

> 이 문서는 `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`의 하위 운영 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

### 기존 문서 처리

- `Iris/build/description/v2/dvf_3_3_text_policy.md`는 runtime text policy/reference 문서로 남기고, 새 policy 문서를 참조하도록 정리한다.
- `Iris/build/description/v2/3_3_vs_4_boundary_examples.md`는 reference note를 남기거나 새 예시 문서로 연결한다.

### 게이트

- 문서 2종 완료
- 상위 문서 우선 문구 삽입 완료

## Phase 1. 현행 산출물 진단

### 목적

현재 3-3 본문이 어떤 실패 형태로 분포하는지 read-only로 수치화한다.

### 진단 필드

- `body_role_class`
- `fact_origin_summary`
- `dominant_slot`

`body_role_class`의 허용값은 다음과 같다.

- `item_centric`
- `function_locked`
- `identity_echo`
- `acquisition_led`
- `representative_distorted`
- `fallback_survivor`

### 구현

- 스크립트: `Iris/build/description/v2/tools/build/report_layer3_body_adequacy_audit.py`
- 출력:
  - `Iris/build/description/v2/staging/body_role/phase1/layer3_body_adequacy_audit.jsonl`
  - `Iris/build/description/v2/staging/body_role/phase1/layer3_body_adequacy_summary.json`
  - `Iris/build/description/v2/staging/body_role/phase1/layer3_body_adequacy_summary.md`

### 입력

- facts: `identity_hint`, `primary_use`, `acquisition_hint`, `fact_origin`, `slot_meta.interaction_cluster`
- decisions: `use_source`, `selected_cluster`, `selected_role`, `merge_case`, `cluster_used`
- full-rendered 기준선 sample

### 규칙

- facts/decisions/rendered를 수정하지 않는다.
- read-only audit만 수행한다.

### 게이트

- class 분포 수치 확정
- 수동 샘플 검수 packet 생성

## Phase 5. identity_fallback expansion plan

### 실행 시점

Phase 1 기준선 고정 직후 병렬 착수한다. 구현 순서는 Phase 1 다음이지만, read-only 분석이므로 Phase 2를 막지 않는다.

### 목적

`identity_fallback 617`의 후속 확장 대상을 bucket별로 정리한다.

### Bucket

- `bucket_1_existing_cluster_reusable`
- `bucket_2_net_new_cluster_required`
- `bucket_3_out_of_dvf_scope_group_c`

### 산출물

- `Iris/build/description/v2/staging/body_role/phase1_parallel/identity_fallback_expansion_plan.json`

### 규칙

- facts 입력 확장 계획만 만든다.
- 현재 runtime/state를 바꾸지 않는다.

## Phase 2. decisions overlay 추가

### 목적

compose에 전달하기 전에 body-role 판정과 배치 힌트를 decisions 쪽에 추가한다.

### 추가 필드

- `layer3_role_check`
- `representative_slot`
- `body_slot_hints`
- `representative_slot_override` (선택)

### `layer3_role_check` 허용값

- `ADEQUATE`
- `FUNCTION_NARROW`
- `IDENTITY_ONLY`
- `ACQ_DOMINANT`

### overlay 스키마

| 필드 | 형식 | nullable | 허용값/규칙 |
|---|---|---|---|
| `layer3_role_check` | enum | no | `ADEQUATE`, `FUNCTION_NARROW`, `IDENTITY_ONLY`, `ACQ_DOMINANT` |
| `representative_slot` | enum | yes | `primary_use`, `identity_hint` |
| `body_slot_hints.secondary_use_present` | boolean | no | 고정 key |
| `body_slot_hints.distinctive_mechanic_present` | boolean | no | 고정 key |
| `body_slot_hints.acquisition_should_trail` | boolean | no | 고정 key |
| `body_slot_hints.item_specific_cue_required` | boolean | no | 고정 key |
| `representative_slot_override` | boolean | no | boolean only |

### 필드 의미

- `representative_slot`: 현재 facts 슬롯 중 무엇을 대표 기능으로 전면에 둘지 나타내는 derived field
- `body_slot_hints`: secondary/distinctive/acquisition reorder 힌트를 담는 decisions-side derived field
- `representative_slot_override`: `representative_distorted` 계열에서 대표 슬롯을 강제로 재선택했음을 나타내는 optional derived flag

### Phase 1 -> Phase 2 매핑표

| Phase 1 `body_role_class` | Phase 2 `layer3_role_check` | 비고 |
|---|---|---|
| `item_centric` | `ADEQUATE` | — |
| `function_locked` | `FUNCTION_NARROW` | — |
| `identity_echo` | `IDENTITY_ONLY` | — |
| `acquisition_led` | `ACQ_DOMINANT` | — |
| `representative_distorted` | `FUNCTION_NARROW` | 필요 시 `representative_slot_override: true` 부여 |
| `fallback_survivor` | `IDENTITY_ONLY` | identity/role fallback만 생존 |

### 구현

- overlay builder: `Iris/build/description/v2/tools/build/build_layer3_role_check_overlay.py`
- validator: `Iris/build/description/v2/tools/build/validate_layer3_role_check.py`

### 규칙

- facts 슬롯은 추가하지 않는다.
- 현재 decisions를 덮어쓰는 대신 overlay 또는 enriched artifact로 먼저 구현한다.

### 게이트

- Phase 1 수동 진단과 기계 판정 일치율 80% 이상

## Phase 3. compose 내부 분기와 repair 규칙 흡수

### 목적

`layer3_role_check`를 compose의 중심 입력으로 사용하고, repair 규칙을 compose 내부에 흡수한다.

### 구현 위치

- 핵심 파일: `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- profile 조정: `Iris/build/description/v2/data/compose_profiles.json`

### compose 내부 실행 순서

1. `layer3_role_check` 읽기
2. role_check에 따른 `sentence_plan` 선택
3. 선택된 `sentence_plan`으로 본문 조합
4. 같은 함수 내부에서 repair 규칙 적용
5. `quality_flag` 태깅

### repair 규칙

| 규칙 이름 | 조건 | 행동 |
|---|---|---|
| 대표성 복구 규칙 | `representative_slot`보다 `distinctive_mechanic` 또는 `secondary_use` 성격의 힌트가 문장 선두에 배치된 경우 | `representative_slot` 내용을 주절로 이동하고 나머지를 후행절로 재배치 |
| 특수 기능 후경화 규칙 | `distinctive_mechanic` 성격의 힌트가 `representative_slot` 앞에 오는 경우 | 순서를 역전한다 |
| 일반론 탈출 규칙 | 완성 문장이 item-specific cue 없이 분류 레이블 수준으로만 끝나는 경우 | `representative_slot` 또는 `body_slot_hints`에서 item-specific 내용을 강제 삽입한다 |
| 파밍 안내 후행화 규칙 | `acquisition_hint`가 첫 번째 절에 배치된 경우 | `acquisition_hint`를 마지막 절로 재배치한다 |

### 결정 필드 사용 원칙

- 대표 기능 판단은 `representative_slot`을 사용한다.
- secondary/distinctive 여부는 `body_slot_hints`를 사용한다.
- 새로운 facts를 만들지 않는다.
- `quality_flag`는 rendered 진단 메타데이터로만 남기고 runtime 계약에는 올리지 않는다.

### 게이트

- introduced hard fail 0
- compose 외부 단계 추가 없음

## Phase 4. structural pattern 추가

### 목적

compose 이후 구조 위반을 감지하고, 다음 빌드용 피드백 신호를 만든다.

### 패턴 세트

- `LAYER4_ABSORPTION`
- `SINGLE_FUNCTION_LOCK`
- `REPRESENTATIVE_USE_MISSING`
- `BODY_LACKS_ITEM_SPECIFIC_USE`
- `ACQUISITION_LEADS_BODY`

### 패턴 의미

- `LAYER4_ABSORPTION`: 3-4 상세 흡수
- `SINGLE_FUNCTION_LOCK`: 복수 용도 아이템이 단일 기능에 잠김
- `REPRESENTATIVE_USE_MISSING`: 대표 기능 문장이 부재
- `BODY_LACKS_ITEM_SPECIFIC_USE`: 2계층 정보는 있으나 item-specific use가 부재
- `ACQUISITION_LEADS_BODY`: acquisition이 본문 선두를 점거

### 구현

- lint rule source: `Iris/build/description/v2/tools/style/rules/structural_rules.json`
- linter 확장: `Iris/build/description/v2/tools/style/linter.py`
- phase output:
  - `Iris/build/description/v2/staging/body_role/phase4/body_role_lint_report.json`
  - `Iris/build/description/v2/staging/body_role/phase4/role_check_feedback.jsonl`

### 현재 빌드에 대한 규칙

Phase 4의 구조 패턴 탐지 결과는 현재 빌드 산출물을 변경하지 않는다. 탐지 결과는 `body_role_lint_report.json`에 기록되며, 다음 빌드에서 overlay builder가 이 결과를 입력으로 사용해 `layer3_role_check`를 재판정하는 피드백 신호로만 작동한다.

### feedback 수명 규칙

Phase 4 feedback 산출물은 매 빌드 fresh recompute가 원칙이며, 이전 빌드 feedback을 누적 상태로 재사용하지 않는다.

### 처리 등급

- `LAYER4_ABSORPTION` -> hard block
- `SINGLE_FUNCTION_LOCK` -> 다음 빌드 `layer3_role_check` 재판정 후보 `FUNCTION_NARROW`
- `REPRESENTATIVE_USE_MISSING` -> 다음 빌드 `layer3_role_check` 재판정 후보 `IDENTITY_ONLY`
- `BODY_LACKS_ITEM_SPECIFIC_USE` -> 다음 빌드 `layer3_role_check` 재판정 후보 `IDENTITY_ONLY`
- `ACQUISITION_LEADS_BODY` -> `ACQ_DOMINANT` 추적 및 repair 회귀 센서

### 게이트

- `LAYER4_ABSORPTION` introduced hard fail 0

## Phase 6. semantic axis 연결과 검증 준비

### 목적

Phase 4의 구조 패턴 결과를 신규 상태 축 없이 기존 semantic axis에 연결하고, Phase 7 검증 입력을 고정한다.

### 규칙

- `SINGLE_FUNCTION_LOCK` 감지 row -> 다음 빌드 `FUNCTION_NARROW` 재판정 후보 -> semantic weak 후보 목록에 기록
- `REPRESENTATIVE_USE_MISSING` 감지 row -> 다음 빌드 `IDENTITY_ONLY` 재판정 후보 -> semantic weak 후보 목록에 기록
- `BODY_LACKS_ITEM_SPECIFIC_USE` 감지 row -> 다음 빌드 `IDENTITY_ONLY` 재판정 후보 -> semantic weak 후보 목록에 기록

### 판정 주체

Phase 6의 산출물은 semantic weak 후보 목록이다. 이 목록의 row를 실제로 semantic::weak로 재분류하는 것은 별도 `DECISIONS.md` 항목을 거친 후에만 반영한다. Phase 6 자체에서 semantic axis를 자동 갱신하지 않는다.

### 현재 빌드에 대한 규칙

Phase 2/3이 실제 수정 경로다. Phase 4/6은 후속 튜닝용 진단·피드백 경로이며, 현재 빌드 산출물을 소급 수정하지 않는다.

### semantic axis 반영 규칙

Phase 6의 후보 목록은 다음 round의 결정 입력일 뿐이다. semantic axis의 실제 값은 별도 결정 없이 자동 갱신하지 않는다.

### 비목표

- `surface_quality` 필드 추가
- `surface_active/runtime_only` 축 추가
- active/silent 외부 계약 변경

### 산출물

- `Iris/build/description/v2/staging/body_role/phase6/semantic_axis_linkage_report.json`
- `Iris/build/description/v2/staging/body_role/phase6/semantic_axis_linkage_report.md`

### 게이트

- 구조 패턴과 semantic axis 연결 규칙 문서화 완료
- 신규 상태 축 추가 없음 확인

## Phase 7. 회귀 검증과 baseline 재측정

### 목적

개선과 회귀를 구분 가능한 검증 규칙으로 다시 측정한다.

### 검증 규칙

- golden subset SHA-256 고정
- golden subset 외의 `ADEQUATE` row는 `meaning-preserving approved diff`로 검증
- introduced hard fail 0
- introduced `LAYER4_ABSORPTION` 0
- `item_centric` 비율 감소 없음

### golden subset

전수 검토가 끝난 exemplar row만 포함한다. 초기 권장 크기는 100 row 내외다.

golden subset은 다음 lane을 강제 포함한다.

- `multiuse tool`
- `weapon/tool hybrid`
- `distinctive mechanic item`
- `identity/role fallback row`

나머지 표본은 `item_centric` 확인 완료 row로 채운다.

### approved diff 기준

허용:

- 문장 순서 조정
- identity/use 비중 재조정
- acquisition 후행화
- representative focus 복구

거부:

- 새 사실 추가
- 기존 사실 삭제
- 3-4 상세 유입

### 산출물

- `Iris/build/description/v2/staging/body_role/phase7/body_role_regression_report.json`
- `Iris/build/description/v2/staging/body_role/phase7/body_role_regression_report.md`

### `quality_flag` 매핑표

| 조건 | `quality_flag` |
|---|---|
| `layer3_role_check = ADEQUATE` | 없음 |
| `layer3_role_check = FUNCTION_NARROW` and compose 완료 | `function_narrow` |
| `layer3_role_check = IDENTITY_ONLY` | `identity_only` |
| `layer3_role_check = ACQ_DOMINANT` and acquisition reorder 적용 | `acq_dominant_reordered` |

## Phase 8. override 기준 재정의와 회귀 테스트

### 목적

자동 규칙으로 대표성 선택이 계속 왜곡되는 row를 위한 manual override 기준을 body-role 기준으로 다시 작성한다.

### 산출물

- `Iris/build/description/v2/dvf_3_3_body_regression_pack.json`
- `Iris/build/description/v2/manual_override_body_policy.md`

### 회귀 lane

- `multiuse tool`
- `weapon/tool hybrid`
- `distinctive mechanic item`
- `acquisition-heavy item`
- `identity/role fallback row`
- `cluster_summary dominant row`

### 표본 기준

`cluster_summary dominant row` lane의 회귀 표본은 Phase 1 진단에서 `function_locked`로 분류된 row 중 도메인별 상위 N건으로 뽑는다. 전수 포함하지 않는다. 도메인 분포는 Phase 1 산출물의 `body_role_class` 분포를 기준으로 결정한다.

## Phase 9. 문서 closeout

### 목적

다음 세션에서 3-3 역할 논쟁이 재발하지 않도록 문구를 닫는다.

### closeout 문구

- 3-3은 authoritative wiki body로 읽힌다.
- 3-3은 1·2·4 정보를 일부 포함할 수 있다.
- 단, 3-4 상세 흡수는 금지다.
- compose는 repair를 수행한다.
- linter/gate는 veto와 피드백을 수행한다.
- 신규 상태 축 없이 기존 semantic axis 위에서 품질 추적을 수행한다.

### 산출물

- `docs/dvf_3_3_body_closeout.md`

---

## 4. 실행 순서

기본 순서는 다음과 같다.

`Phase 0 -> Phase 1 -> Phase 2 -> Phase 3 -> Phase 4 -> Phase 6 -> Phase 7 -> Phase 8 -> Phase 9`

병렬 허용은 다음 한정으로 둔다.

- `Phase 5`는 `Phase 1` 직후 병렬 시작 가능

그 외에는 직렬로 유지한다.

---

## 5. 파일 수정 우선순위

| 우선순위 | 파일/경로 | 이유 |
|---|---|---|
| P0 | `docs/dvf_3_3_body_role_policy.md` | Phase 0 문서 재봉인 |
| P0 | `docs/3_3_vs_3_4_boundary_examples.md` | Phase 0 예시 문서 |
| P1 | `Iris/build/description/v2/tools/build/report_layer3_body_adequacy_audit.py` | Phase 1 read-only audit |
| P1 | `Iris/build/description/v2/tools/build/build_layer3_role_check_overlay.py` | Phase 2 overlay |
| P1 | `Iris/build/description/v2/tools/build/validate_layer3_role_check.py` | Phase 2 validator |
| P1 | `Iris/build/description/v2/tools/build/compose_layer3_text.py` | Phase 3 내부 분기/repair |
| P1 | `Iris/build/description/v2/data/compose_profiles.json` | sentence_plan 조정 |
| P2 | `Iris/build/description/v2/tools/style/linter.py` | Phase 4 structural pattern |
| P2 | `Iris/build/description/v2/tools/style/rules/structural_rules.json` | structural rule source |
| P2 | `Iris/build/description/v2/tests/*` | 회귀 방어 |

---

## 6. 권장 검증 루틴

### unit / script

- `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"`

### body-role 전용

1. Phase 1 audit 생성
2. Phase 2 overlay 생성 + validator 실행
3. Phase 3 compose rebuild
4. Phase 4 structural lint 실행
5. Phase 6 semantic axis linkage report 생성
6. Phase 7 golden subset / approved diff 검증
7. Lua bridge export

### runtime smoke

- browser
- wiki panel
- context menu

현재 라운드는 UI 노출 정책 변경이 아니므로 exhaustive QA보다 기존 surface 회귀 없음 확인이 우선이다.

---

## 7. 리스크와 방어선

- 리스크: facts를 슬쩍 확장하면 `facts 재판정 없음` 원칙이 깨진다.
  - 방어: 새 배치 정보는 모두 decisions overlay에 둔다.
- 리스크: compose 외부 repair 단계가 다시 생기면 본문 생성 책임이 이중화된다.
  - 방어: repair 규칙은 `compose_layer3_text.py` 내부에만 둔다.
- 리스크: 구조 패턴을 새 상태 축으로 연결하면 기존 2-stage model과 모순이 생긴다.
  - 방어: semantic axis 연결만 허용하고 신규 상태 축은 금지한다.
- 리스크: `BODY_LACKS_ITEM_SPECIFIC_USE` 대신 2계층 echo 자체를 금지로 읽으면 3계층 헌법과 충돌한다.
  - 방어: 금지 대상은 2계층 정보 포함이 아니라 item-specific use 부재로 정의한다.
- 리스크: full-rendered 기준선 대신 fixture를 검증 기준으로 오인할 수 있다.
  - 방어: Phase 7 검증은 full-rendered 기준선만 사용한다고 명시한다.

---

## 8. 완료 정의

다음이 모두 만족되면 이 계획은 완료다.

- facts 슬롯 확장 없이 `layer3_role_check`와 decisions overlay가 구축된다.
- repair 규칙이 compose 내부 분기로 흡수된다.
- structural pattern이 `LAYER4_ABSORPTION` hard block과 semantic axis 연결용 피드백을 동시에 제공한다.
- golden subset과 approved diff 기준으로 회귀 검증이 닫힌다.
- `identity_fallback 617` 확장 계획이 read-only 산출물로 정리된다.
