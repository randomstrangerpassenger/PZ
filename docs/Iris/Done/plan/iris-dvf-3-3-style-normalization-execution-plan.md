# Iris DVF 3-3 Style Normalization Execution Plan

> 상태: Draft v0.1  
> 기준일: 2026-04-03  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 입력 기준: `DVF 3-3 Style Normalization 로드맵 — 최종 통합본 v1.0 FINAL (2026-04-03)`  
> 기준 코드 경로: `Iris/build/description/v2/`  
> 목적: DVF 3-3의 한국어 표면형을 결정론적 style normalization 레이어로 정리하되, `facts -> decisions -> compose -> rendered -> Lua bridge` 생산 계약과 `rendered ↔ Lua` 일치 계약을 깨지 않고 개선한다.

---

## 1. 실행 판정

- 이번 작업은 `facts`, `decisions`, `candidate_state`, `cluster`를 다시 여는 semantic 재판정 단계가 아니다.
- 본질은 **compose 이후 rendered 이전**에 결정론적 스타일 정규화 계층을 삽입하고, 그 뒤에 advisory-only style linter를 추가하는 **표면형 안정화 단계**다.
- 실행 순서는 아래처럼 고정한다.
  - `facts -> decisions -> compose -> normalizer -> style linter -> rendered -> Lua bridge -> runtime`
- 기존 `postproc_ko.py`가 맡고 있던 띄어쓰기/문장부호 정리는 별도 후처리 단계로 남기지 않고 **normalizer의 마지막 단계**로 흡수한다.
- style linter는 현재 validator나 baseline-delta gate를 대체하지 않는다. 역할은 **경고 리포트 생성**에 한정한다.

## 2. 불변 원칙

- normalizer는 evidence, cluster, fact_origin, approval, candidate_state를 재판정하지 않는다.
- normalizer는 정규 표현식 또는 리터럴 기반의 **결정론적 치환만** 수행한다.
- 형태소 분석, 의미 추론, 통계적 재해석, 자연어 모델 기반 교정은 도입하지 않는다.
- family 바인딩은 새 분류 축을 만들지 않고 **`fact_origin + selected_cluster_contains`** 로만 닫는다.
- style linter는 advisory-only다.
- style linter 경고는 baseline-delta gate에 합류하지 않는다.
- normalizer 결과는 `rendered.json`과 `IrisLayer3Data.lua`의 일치 계약을 깨면 안 된다.
- 3-3은 계속 **item-centric body**다.
- 표현 자연화를 이유로 3-3이 3-4의 상세 상호작용 목록을 흡수하면 안 된다.

## 3. 현재 코드 기준선

현재 워크스페이스에서 실제 변경 접점은 아래 다섯 곳이다.

- compose: `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- 기존 postproc: `Iris/build/description/v2/tools/postproc_ko.py`
- rendered validator: `Iris/build/description/v2/tools/build/validate_interaction_cluster_rendered.py`
- 파이프라인 엔트리: `Iris/build/description/v2/run_interaction_cluster_pipeline.py`
- Lua bridge export: `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`

현재 구조상 `compose_layer3_text.py`는 문장 조합 직후 `postprocess_ko()`를 직접 호출한다.  
따라서 이번 작업의 첫 구현 과제는 `compose`와 `normalizer`의 경계를 분리하고, 기존 `postproc_ko.py`를 normalizer 내부 마지막 단계로 이동시키는 것이다.

## 4. 기준선 및 authority

이번 문서의 runtime 기준선은 second-pass closeout 이후 current runtime snapshot을 따른다.

| 항목 | 값 |
|------|---:|
| total rows | 2105 |
| active | 2084 |
| silent | 21 |
| cluster_summary | 1440 |
| identity_fallback | 617 |
| role_fallback | 48 |

style normalization의 Phase 0 스캔 분모는 위 baseline 중 **active 2084 rows** 로 고정한다.

### authority artifact

- current baseline facts: `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview_facts.jsonl`
- current baseline rendered: `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview.rendered.json`
- current baseline runtime summary: `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_runtime_summary.json`
- compose fixture facts: `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
- compose fixture decisions: `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
- compose fixture profiles: `Iris/build/description/v2/data/compose_profiles.json`

Phase 0 스캔은 sprint7 closeout의 full rendered/facts를 authority로 삼되, compose fixture 경로는 테스트와 샘플 파이프라인용으로만 남긴다.
여기서 `selected_cluster_contains` 판정은 새 축이 아니라, 기존 `selected_cluster` 문자열에 대한 contains match로만 계산한다.

## 5. 산출물 구조

이번 실행안의 산출물 루트는 아래처럼 고정한다.

- 문서: `docs/iris-dvf-3-3-style-normalization-execution-plan.md`
- staging:
  - `Iris/build/description/v2/staging/style/phase0_baseline_scan/`
  - `Iris/build/description/v2/staging/style/phase0_rule_binding/`
  - `Iris/build/description/v2/staging/style/phase3_dry_run/`
- code:
  - `Iris/build/description/v2/tools/style/normalizer.py`
  - `Iris/build/description/v2/tools/style/linter.py`
  - `Iris/build/description/v2/tools/style/rules/global_rules.json`
  - `Iris/build/description/v2/tools/style/rules/family_rules.json`
  - `Iris/build/description/v2/tools/style/rules/lint_rules.json`
- output:
  - `Iris/build/description/v2/output/style_baseline_scan.json`
  - `Iris/build/description/v2/output/style_normalization_changes.jsonl`
  - `Iris/build/description/v2/output/style_lint_report.json`

현재 workspace에서는 `output/dvf_3_3_rendered.json`이 6-row fixture로 남아 있으므로, full runtime authority는 `staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview.rendered.json`으로 둔다. `media/lua/client/Iris/Data/IrisLayer3Data.lua`와의 계약 검증도 이 authoritative full rendered 기준으로 수행하고, style 산출물은 이를 보조하는 검증/추적 artifact로 둔다.

## 6. Work Breakdown

### Phase 0 — Baseline 수립 및 family 바인딩

#### 0-A. 빈도 스캔

- 목표: 현재 generated text에서 상투 표현과 반복 패턴의 분포를 계량화한다.
- 입력:
  - `staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview.rendered.json`
  - `staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview_facts.jsonl`
- 스캔 패턴:
  - `겸용`
  - `함께 쓰는`
  - `함께 사용되는`
  - `주로 함께`
  - `~에 쓰이는 용도의`
  - `근접 전투`
  - `~에서 발견된다`
  - `~에서 찾을 수 있다`
  - 동일 명사 2회 이상 반복
- 교차 집계 축:
  - `fact_origin`
  - `selected_cluster_contains`
- 산출물:
  - `style_baseline_scan.json`
- 완료 기준:
  - total active rows와 pattern hit count가 재현 가능하게 고정된다.
  - pattern별 sample item이 최소 5건 또는 전체 건수 전량으로 남는다.

#### 0-B. 전역/family/lint 바인딩

- 목표: 각 패턴을 global rule, family rule, lint-only 중 하나로 봉인한다.
- 판정 기준:
  - 분포가 균등하고 반례 0건이면 global
  - 특정 `fact_origin` 또는 cluster family에 집중되면 family
  - 분포는 넓지만 반례가 있으면 lint-only
- 바인딩 키:
  - `fact_origin + selected_cluster_contains`
- 산출물:
  - `phase0_rule_binding.md`
  - `phase0_rule_binding.json`
  - DECISIONS 반영 초안 메모
- gate:
  - 새 semantic 축을 만들지 않는다.
  - family rule이 사실상 domain reclassification으로 읽히면 실패다.

### Phase 1 — Normalizer 규칙 정의

#### 1-A. Global Rules

- 목표: 반례 0건인 안전 치환만 전역 규칙으로 승격한다.
- 초기 후보:
  - `G-01`: `겸용 -> 겸`
  - `G-02`: `함께 쓰는 -> 쓰는`
  - `G-03`: `함께 사용되는 -> 사용되는`
  - `G-04`: `주로 함께 -> 주로`
  - `G-05`: `~에 쓰이는 용도의 -> ~에 쓰이는`
- 산출물:
  - `tools/style/rules/global_rules.json`
- gate:
  - 반례가 1건이라도 확인되면 global에서 제거하거나 family로 격하한다.

#### 1-B. Family Rules

- 목표: 특정 fallback/family 문체의 과잉 표현만 scoped rule로 다룬다.
- Phase 0 현재 후보:
  - `F-01`: `fact_origin = identity_fallback`, `selected_cluster_contains = ["unknown"]` 조건에서 `근접 전투나 작업에 함께 쓰는 도구 -> 전투나 작업에 쓰는 도구`
- 주의:
  - `selected_cluster = null`은 binding/normalizer 매칭에서 `unknown` sentinel로 해석한다.
  - `근접 전투` 단독 토큰은 현재 baseline에서 `identity_fallback unknown`과 `melee_combat` 계열에 혼재하므로 standalone family rule로 승격하지 않는다.
- 산출물:
  - `tools/style/rules/family_rules.json`
- gate:
  - family scope가 넓어져 global substitute처럼 작동하면 실패다.

#### 1-C. Normalizer 엔진

- 목표: compose 산출 문자열을 deterministic하게 정규화하고 변경 로그를 남긴다.
- 실행 순서:
  1. global rules
  2. family rules
  3. legacy postproc 흡수
  4. change log 생성
- 필수 제약:
  - 규칙 순서 고정
  - 멱등성 보장
  - 모든 규칙은 `id`, `version`, `active` 플래그를 가진다
  - postproc 흡수 검증 단계에서는 모든 style rule을 `"active": false`로 내리고 legacy postproc만 실행할 수 있어야 한다
  - `manual_override_text_ko`는 style rule 적용을 건너뛰고 legacy postproc만 적용한다
  - manual override 문장은 작성자 책임 surface로 두되, 최소 띄어쓰기/문장부호 정리만 유지하고 필요 시 style linter에서만 advisory 경고를 허용한다
- 산출물:
  - `tools/style/normalizer.py`
  - `output/style_normalization_changes.jsonl`

### Phase 2 — Style Linter 규칙 정의

#### 2-A. Advisory 수준 고정

- `STYLE_WARN`: 수동 확인 권장
- `STYLE_NOTE`: 빈도 참고
- 둘 다 gate 영향 없음
- `STYLE_WARN 정밀도 70%`는 hard gate가 아니라, pilot labeled sample 기준의 초기 운영 목표치로 둔다
- 최종 임계값은 Phase 3 dry run 결과를 본 뒤 확정한다

#### 2-B. Lint Rules

- 목표: normalizer로 닫지 않을 패턴을 advisory report로 분리한다.
- Phase 2-B의 lint rule 초기 후보는 Phase 0-B에서 lint-only로 분류된 패턴을 기본 입력으로 삼고, Phase 0-A 스캔의 빈도 이상치에서 추가 후보를 보충한다.
- 초기 `STYLE_WARN` 후보:
  - `L-01`: `근접 전투나 작업`
  - `L-02`: 동일 명사 반복
  - `L-03`: `~에 쓰이는 용도의` 잔여 변형
  - `L-04`: `~에서 발견된다` 반복 과다
- 초기 `STYLE_NOTE` 후보:
  - `N-01`: `다양한 / 각종 / 여러 가지`
  - `N-02`: 80자 초과 문장
  - `N-03`: `~할 수 있다` 반복
- 산출물:
  - `tools/style/rules/lint_rules.json`
  - `tools/style/linter.py`
  - `output/style_lint_report.json`
- gate:
  - linter는 산출 문자열을 절대 수정하지 않는다.

### Phase 3 — Dry Run 및 검증

#### 3-A. Normalizer dry run

- 대상: active 2084 전수
- 검증:
  - idempotent
  - input/output row count 동일
  - 1단계: 모든 style rule을 `"active": false`로 둔 postproc 흡수 검증 모드에서 기존 postproc-only 결과와 byte-identical
  - 2단계: style rule 활성화 후에는 전체 byte-identical을 요구하지 않고, 변경 항목은 모두 규칙 적용 로그에 기록되며 미변경 항목만 byte-identical 유지
  - 변경 건 10% 또는 최소 30건 수동 샘플 검토
  - 샘플링 기준은 변경 폭이 큰 순서 우선 + `fact_origin`별 최소 5건 보장으로 고정한다
  - 의미 훼손 0

#### 3-B. Linter dry run

- 대상: normalizer 결과 전수
- 검증:
  - pilot labeled sample 기준 STYLE_WARN 정밀도 70%를 초기 운영 목표치로 추적
  - 실행 전후 rendered byte-identical

#### 3-C. Baseline-delta 검증

- 기준:
  - introduced hard fail = 0
  - introduced warn = 0
  - resolved fail/warn은 있으면 보너스
- 주의:
  - style lint report는 baseline-delta gate 집계에 합치지 않는다.

### Phase 4 — 구현 및 파이프라인 통합

#### 4-A. compose 경계 리팩터링

- 목표: 현재 `compose_layer3_text.py` 안에 섞여 있는 조합/후처리 책임을 분리한다.
- 작업:
  - raw compose 함수와 normalize 함수를 분리한다.
  - 기존 `postprocess_ko()` 직접 호출을 normalizer 호출로 치환한다.
  - `postproc_ko.py`는 deprecated shim 또는 helper 모듈로만 남긴다.
  - `manual_override_text_ko`는 style rules를 건너뛰고 legacy postproc only 경로로 고정한다.

#### 4-B. pipeline 삽입

- 목표: 엔트리 포인트에서 normalizer/linter를 공식 경로에 삽입한다.
- 대상:
  - `run_interaction_cluster_pipeline.py`
  - `compose_layer3_text.py`
  - 필요 시 validator 연동부
- 결과:
  - rendered는 normalized text를 authority로 갖는다.
  - Lua bridge는 변경 없이 normalized rendered만 소비한다.

#### 4-C. validator 공존

- 목표: 기존 validator와 style linter의 역할을 분리 유지한다.
- 원칙:
  - `validate_interaction_cluster_rendered.py`는 기존 hard fail/warn 의미 유지
  - style linter는 별도 report 출력
  - 두 리포트는 합산해 gate를 재정의하지 않는다.

### Phase 5 — 문서화 및 제도화

- `docs/DECISIONS.md`에 아래 5개 결정을 추가한다.
  - normalizer는 compose 뒤 rendered 앞에 위치한다
  - normalizer는 의미 재판정이 아니라 결정론적 치환만 수행한다
  - family scope는 `fact_origin + selected_cluster_contains` 조합으로 바인딩한다
  - style linter는 baseline-delta gate에 합류하지 않는다
  - normalizer가 legacy postproc을 흡수한다
- `docs/ARCHITECTURE.md`에는 normalizer/linter의 위치와 책임을 추가한다.
- `docs/ROADMAP.md`에는 이 작업을 style surface stabilization 성격의 next track으로 반영한다.

### Phase 6 — Linter 경고 소화 루프

- 각 `STYLE_WARN`에 대해 아래 중 하나를 선택한다.
  - `FIX_COMPOSE`
  - `ADD_RULE`
  - `ACCEPT`
  - `HOLD`
- 경고 소화는 facts/decisions 재판정 루트가 아니라 **표현층 후속 운영 루프**로만 다룬다.

## 7. 구현 순서

실제 작업 순서는 아래처럼 고정한다.

1. Phase 0 스캐너 작성
2. rule skeleton 작성
3. normalizer 엔진 작성
4. compose 리팩터링 seam 확보
5. linter 작성
6. dry run
7. pipeline 통합
8. 문서 반영

이 순서를 바꿔 `rule 없이 엔진부터 production 삽입`하거나, `dry run 없이 pipeline 통합`으로 가면 안 된다.

## 8. 테스트 및 gate

### 필수 테스트

- unit:
  - normalizer 규칙 적용
  - idempotency
  - family scope match
  - linter no-mutation
- integration:
  - compose -> normalizer -> rendered
  - rendered -> Lua bridge
  - baseline-delta 유지

### 필수 gate

- normalizer 2회 적용 결과 == 1회 적용 결과
- postproc 흡수 검증 모드에서는 기존 postproc-only 결과와 byte-identical
- style rule 활성화 후에는 전체 byte-identical을 요구하지 않고, 변경 항목 전부가 rule log에 기록되며 미변경 항목만 byte-identical 유지
- rendered row count 보존
- Lua bridge export 후 entry count 및 hash 계약 유지
- introduced hard fail 0
- introduced warn 0
- STYLE_WARN 정밀도 70%는 pilot labeled sample 기준 운영 목표치이며 shipping blocker로 쓰지 않는다

## 9. 리스크와 차단선

### 리스크

- family rule이 사실상 hidden semantic override로 미끄러질 수 있다.
- normalizer 도입 과정에서 `compose`와 `rendered`의 경계가 흐려질 수 있다.
- style linter를 기존 validator warning과 합쳐 읽으려는 운영 drift가 생길 수 있다.
- legacy postproc 흡수 과정에서 byte-identical 회귀가 깨질 수 있다.
- 규칙 적용 순서가 잘못되면 이중 치환이나 선행 치환으로 인한 후행 rule 미매칭이 발생할 수 있다.

### 차단선

- family rule은 반드시 Phase 0 scan evidence를 남긴다.
- 모든 규칙은 `id`, `version`, `active`를 가진 JSON 규칙 파일에만 등록한다.
- style lint report는 파일도, 요약도 validator report와 분리한다.
- postproc 흡수 완료 전까지는 deprecated shim을 남겨 회귀 비교 기준으로 사용한다.

## 10. 완료 기준

- `겸용`, `함께 쓰는` 계열 상투 표현이 generated text에서 유의미하게 감소한다.
- combat/tool family에서 `근접 전투` 같은 과잉 수식이 설명 가능한 범위로 줄어든다.
- item-centric body는 유지된다.
- 3-4 세부 상호작용 유입은 없다.
- acquisition 후행 배치는 유지된다.
- introduced hard fail = 0
- style warning은 advisory-only 수준으로 관리 가능하다.
- runtime surface에서 문체 개선이 확인된다.
- 정량 감소 기준은 Phase 0 baseline 완료 후 확정한다.

## 11. Hold

- compose profile 자체 재설계
- facts 재판정
- candidate_state 재오픈
- semantic quality UI exposure
- rendered ↔ Lua 계약 재정의
- 형태소 분석기 또는 NLP 엔진 도입
- forbidden_patterns와 style linter의 역할 통합
- style warning의 runtime gate 승격
- `generated::weak 133` / `missing::adequate 9` 정책 재논쟁

## 12. immediate next cut

지금 기준의 가장 안전한 첫 착수 묶음은 아래 세 가지다.

- Phase 0 baseline scanner 작성
- `tools/style/` rules skeleton 생성
- `compose_layer3_text.py`에서 `compose`와 `postprocess` 경계 분리

이 세 단계가 닫히기 전에는 rule 확장이나 linter 임계값 조정으로 가지 않는다.
