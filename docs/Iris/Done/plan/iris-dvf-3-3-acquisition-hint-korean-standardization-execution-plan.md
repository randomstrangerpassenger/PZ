# Iris DVF 3-3 Acquisition Hint Korean Standardization Execution Plan

> 상태: Draft v0.1  
> 기준일: 2026-04-08  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 동반 문서: `docs/iris-dvf-3-3-acquisition-hint-scope-lock.md`  
> 입력 기준: `Iris DVF 3-3 — acquisition_hint 한국어 표준화 통합 로드맵` (2026-04-08)  
> 기준 코드 경로: `Iris/build/description/v2/`  
> 목적: `acquisition_hint`를 핵심 축으로 유지한 채, raw 번역투 phrase를 직접 노출하지 않도록 v1용 한국어 입력 표준화 계층과 validator lexical contract를 구축한다.

> 이 문서는 상위 문서의 하위 운영 계획 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

---

## 0. 실행 판정

이번 라운드는 한국어 엔진 개발이 아니다.  
이번 라운드는 style linter 승격도 아니다.  
이번 라운드는 `candidate_state`, active/silent, body-role authority를 다시 여는 round도 아니다.

이번 라운드의 정체성은 아래 한 줄로 고정한다.

> `acquisition_hint`를 핵심 축으로 올린 뒤에도 버틸 수 있도록,  
> raw source literal을 직접 쓰지 않는 **한국어 입력 표준화 계층**을 먼저 세우고,  
> 그 계층으로 닫히지 않는 잔여분만 최소 범위의 구조적 예외로 봉인한다.

이번 문서의 실행 원칙은 다음 셋이다.

- A축: canonical lexicon + normalization layer
- B축: Phase 5 이후에만 열 수 있는 acquisition 전용 conditional micro-josa shim
- S축: suppress 경로 식별과 제거를 별도 작업으로 분리

핵심은 항상 A축 우선이다. B축은 잔여분이 충분히 클 때만 열고, S축은 A/B의 부산물이 아니라 독립 migration으로 다룬다.

---

## 1. 현재 출발점

current authority는 이미 다음을 봉인하고 있다.

- `acquisition_hint`는 `identity_hint`, `primary_use`와 동급의 Layer 3 핵심 축이다.
- `facts.acquisition_hint`는 current v1에서 단일 완성형 string만 허용한다.
- `facts.acquisition_hint = null`이면 `decisions.acquisition_null_reason`이 필요하다.
- 허용 null reason enum은 `UBIQUITOUS_ITEM`, `STANDARDIZATION_IMPOSSIBLE` 둘뿐이다.
- acquisition 블록은 limitation / processing보다 앞에 오되, 3-3은 계속 4블록/4문장 기준을 유지한다.

동시에 current baseline은 아래 현실도 같이 보여준다.

- acquisition coverage closeout 자체는 이미 완료됐다.
  - `closed = 2285 / 2285`
  - `ACQ_HINT = 2037`
  - `ACQ_NULL = 42`
  - `SYSTEM_EXCLUDED = 206`
- 그러나 current style zero-hit는 lexical closure가 아니라 suppress 의존 결과다.
  - acquisition phrase family full snapshot: `214`
  - 분해: `seed_label_repeat 1 / seed_discovery_phrase 177 / seed_discovery_phrase_with_label_repeat 36`
  - `seed_label_repeat 1` family는 exact exception으로 이미 suppress-closed 상태다.
  - 따라서 current active residual backlog는 `213` family이며, discovery-driven family 축으로 남아 있다.

즉 이번 라운드의 직접 과제는 acquisition coverage를 다시 여는 것이 아니라, **current acquisition surface가 suppress 없이도 자연형으로 닫히는 입력 계약**을 만드는 것이다.

---

## 2. Scope Lock Summary

세부 범위 봉인은 동반 문서 `docs/iris-dvf-3-3-acquisition-hint-scope-lock.md`를 authority로 삼는다.  
이 실행 계획에서 다시 강조하는 핵심 금지선은 아래와 같다.

- `josa_adaptive`, `phrasebook_ko.json`, `ko_particles.json`은 열지 않는다.
- `acquisition_hint` 배열화는 열지 않는다.
- acquisition 기반 active/silent 자동 재판정은 열지 않는다.
- `identity_hint`, `primary_use`를 같은 수준의 lexical naturalization 대상으로 확장하지 않는다.
- sentence_plan의 4블록 상한을 바꾸지 않는다.
- style linter를 gate로 승격하지 않는다.
- compose 외부 repair/rewrite 단계는 재도입하지 않는다.

이번 문서에서 허용하는 예외는 하나뿐이다.

- Phase 5 이후 `COUNT / GOLDEN_FAIL / PROFILE_CONCENTRATION` 조건이 충족될 때만 acquisition 슬롯 한정 micro-josa shim을 검토한다.

---

## 3. Current Authority Baseline

이번 실행안의 authority input/output baseline은 아래처럼 고정한다.

- facts authority
  - `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
- decisions authority
  - `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
- compose profile authority
  - `Iris/build/description/v2/data/compose_profiles.json`
- compose entry
  - `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- style branch
  - `Iris/build/description/v2/tools/style/normalizer.py`
  - `Iris/build/description/v2/tools/style/linter.py`
- runtime authority rendered
  - `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview.rendered.json`

이번 라운드는 facts/decisions/schema/runtime 계약을 갈아엎지 않는다.  
바꾸는 것은 `facts.acquisition_hint`에 들어가는 **입력의 출처와 표준화 방식**이다.

---

## 4. Work Breakdown

### Phase 0. Scope Lock and Authority Freeze

#### 목적

이번 라운드를 `한국어 입력 표준화 계층 구축`으로 먼저 봉인하고, 이후 phase에서 범위가 밀리지 않게 한다.

#### 작업

- scope lock companion 문서 작성 및 동결
- current suppress baseline을 lexical closure로 오인하지 않는 판정 문구 명시
- acquisition lexical round의 write scope를 facts / decisions / validator / compose profile / acquisition staging으로 한정
- self-check 문구 고정
  - 이번 라운드를 한 문장으로 설명했을 때 `한국어 엔진 개발`, `style gate 승격`, `active/silent 재판정`이 등장하면 실패

#### 산출물

- `docs/iris-dvf-3-3-acquisition-hint-korean-standardization-execution-plan.md`
- `docs/iris-dvf-3-3-acquisition-hint-scope-lock.md`

#### Gate

- 다음 라운드 착수 전 self-check가 통과한다.

---

### Phase 1. Audit

#### 목적

감이 아니라 전수 실측으로 acquisition surface의 실태를 phrase family 단위까지 닫는다.

#### 1-A. 비자연 패턴 분류

전체 acquisition_hint를 아래 6개 패턴으로 1차 필터링한다.

| 코드 | 정의 |
|---|---|
| `BARE_NOUN_CHAIN` | 조사 없는 명사 나열 |
| `TRANSLATION_COMPOUND` | 번역투 복합명사 |
| `OVERLY_GENERIC` | 지나치게 포괄적 표현 |
| `GAME_INTERNAL_TERM` | 게임 내부 용어 직노출 |
| `JOSA_MISSING` | 자연형 후보이나 조사 누락 |
| `ACCEPTABLE` | current v1 계약상 자연형 |

규칙 기반 1차 필터 후 경계 사례는 수동 검토한다.

#### 1-B. phrase family breakdown 확장

기존 acquisition phrase family breakdown을 아래 축으로 다시 닫는다.

- `seed_label_repeat`
- `seed_discovery_phrase`
- `seed_discovery_phrase_with_label_repeat`

핵심은 개별 문장 문제가 아니라 **입력 계약 family 문제**를 분리하는 것이다.

#### 1-C. disposition 예비 분류

각 phrase를 아래 4등급으로 분류한다.

1. 유지 가능
2. canonical lexicon 치환 가능
3. raw source 수정 필요
4. `STANDARDIZATION_IMPOSSIBLE` 후보

#### 1-D. suppress 경로 선식별

아래 경로를 병렬 inventory로 수집한다.

- compose 내부 acquisition skip 조건
- decisions overlay의 acquisition 예외 처리
- normalizer의 acquisition 특수 규칙
- `manual_override_text_ko` 계열 우회 흔적
- exact phrase exception / simple discovery shape exception 의존 항목

#### 권장 staging 경로

- `Iris/build/description/v2/staging/acquisition/phase1_audit/`

#### 산출물

- `acq_surface_audit_report.json`
- `acquisition_phrase_inventory.json`
- `acquisition_phrase_family_breakdown_v2.json`
- `acquisition_phrase_disposition.review.jsonl`
- `acq_suppress_inventory.json`

#### Gate

- acquisition_hint 전수 분모의 disposition이 모두 분류된다.
- 비자연 패턴이 6개 이하로 수렴한다.
- suppress 때문에 조용한 phrase와 실제 표준화 완료 phrase가 분리된다.
- suppress 경로 inventory가 누락 없이 수집된다.

---

### Phase 7-A. Compose Profile and Sentence Plan Read-Only Audit

#### 목적

실제 profile 수정 전에 acquisition이 body를 지배하는 위험 패턴을 read-only로 먼저 식별한다.

#### 작업

- `required_any`와 sentence_plan 재검토
- `use_acq`, `acq_location`, `acq_method`, `identity_acq` 계열 분포 점검
- `medical_consumable` 4블록 리스크 사전 식별
- acquisition이 item-centric body를 무너뜨리는 profile/plan scope 확정

#### 산출물

- `dvf_acquisition_profile_matrix.md`
- `sentence_plan_acquisition_review.json`

#### Gate

- 어떤 profile/sentence plan이 실제 수정 대상인지 read-only 기준으로 잠긴다.

---

### Bootstrap Phase. Legacy Canonical Backfill

#### 목적

existing `ACQ_HINT = 2037` rows를 새 canonical 체계로 이행할 bootstrap inventory를 먼저 만든다.

#### 실행 순서

1. 기존 `2037` ACQ_HINT rows 전량에 provisional canonical_key 매핑 시도
2. 매핑 성공 항목은 slot_meta backfill 후보로 적재
3. 매핑 실패 항목은 legacy unmapped inventory로 분리
4. bootstrap 결과를 Phase 2 lexicon 설계 입력으로 넘긴다

#### 운영 원칙

- 이 phase는 bootstrap inventory 작성 단계다.
- `staging/gate`를 우회한 direct write는 금지한다.
- gate 통과 전 facts/decisions canon promotion은 허용하지 않는다.

#### 권장 staging 경로

- `Iris/build/description/v2/staging/acquisition/bootstrap/`

#### 산출물

- `legacy_acquisition_canonical_bootstrap.jsonl`
- `legacy_acquisition_slot_meta_backfill.review.jsonl`
- `legacy_acquisition_manual_review_inventory.json`
- `legacy_acquisition_unmapped_inventory.json`
- `legacy_acquisition_bootstrap_report.json`

#### Gate

- 기존 `2037` rows가 `mapped / needs_manual / unmapped`로 빠짐없이 분해된다.
- Phase 4 validator 활성화 전에 legacy backfill inventory가 준비된다.

---

### Phase 2. Canonical Lexicon and Normalization Design

#### 목적

raw acquisition phrase를 그대로 facts에 넣지 않고, `raw source -> canonical acquisition class -> canonical Korean slot text` 구조를 세운다.

#### 2-A. canonical acquisition lexicon 구축

`normalized_text_ko`는 반드시 **조사까지 끝난 완성형 절/명사구**여야 한다.  
current v1 compose는 조사를 만지지 않기 때문이다.

이 artifact 명칭은 `phrasebook`이 아니라 `lexicon`으로 고정한다.  
hold 영역인 `phrasebook_ko.json`과의 scope drift를 막기 위함이다.

필수 필드는 아래처럼 고정한다.

- `canonical_key`
- `allowed_mode`
- `normalized_text_ko`
- `deprecated_aliases`
- `blocked_raw_patterns`
- `notes`

#### 2-B. normalization schema 설계

최소 구조는 아래처럼 고정한다.

- `mode`
  - `location / method / discovery / mixed`
- `canonical_key`
- `normalized_text_ko`
- `source_origin`
- `confidence`
- `disposition`

`facts.acquisition_hint`에는 raw source literal을 직접 쓰지 않는다.  
raw trace와 canonical key는 `slot_meta.acquisition_hint` 쪽에 남긴다.

#### 2-C. 패턴별 정화 전략 배정

Phase 1 audit과 bootstrap 결과를 기준으로 각 pattern에 아래 셋 중 하나를 배정한다.

- 자동 변환 가능
- 반자동 후보 제시 + 수동 승인
- 수동 전용

자동 변환 규칙은 `acq_surface_rewrite_rules.json`으로 관리한다.

#### 2-D. 산출물 소유권 테이블

Phase 2 설계 시점에 주요 artifact의 생산자 / 소비자 / 갱신 주체를 같이 고정한다.

| 산출물 | 생산자 | 소비자 | 갱신 주체 |
|---|---|---|---|
| `acquisition_lexicon_v1.json` | Phase 2 lexical design | normalizer, Phase 3 gate, Phase 4 validator | lexical design round only |
| `canonical_acquisition_map.json` | bootstrap + Phase 2 design | Phase 3 execution, canonical alignment pre-check | bootstrap/Phase 2 owner only |
| `acquisition_phrase_blocklist.json` | Phase 2 lexical design | normalizer, Phase 3 gate, Phase 4 validator | lexical design / suppress retirement only |
| `forbidden_patterns.json` acquisition section | Phase 4 validator contract | Phase 4 validator, QA reports | validator contract owner only |
| `acquisition_hint_normalization_schema.json` | Phase 2 schema design | normalizer, Phase 3 gate | schema owner only |

#### 2-E. facts ↔ decisions 분리 규약 확정

이번 phase에서 다시 못 박아야 하는 것은 다음이다.

- `facts.acquisition_hint = null`이면 `decisions.acquisition_null_reason` 필수
- 허용 enum은 `UBIQUITOUS_ITEM`, `STANDARDIZATION_IMPOSSIBLE` 둘만 유지
- suppress로 숨기던 표준화 불가 항목은 `STANDARDIZATION_IMPOSSIBLE`로 명시 전환
- `획득 정보 없음`과 `phrase는 있으나 표준화 불가`를 분리 기록

#### 2-F. staging-first 운영 확인

current acquisition coverage closeout의 staging-first 구조를 그대로 재사용한다.

- `master`
- `review`
- `gate`
- `canon promotion`

문구는 아래처럼 통일한다.

> `staging/gate`를 우회한 direct write 금지.  
> gate 통과 후 `staging -> canon promotion`만 허용.

#### 권장 경로

- acquisition normalization package root
  - `Iris/build/description/v2/acquisition/`
- design staging root
  - `Iris/build/description/v2/staging/acquisition/phase2_design/`

#### 산출물

- `acquisition_lexicon_v1.json`
- `acquisition_phrase_aliases.json`
- `acquisition_phrase_blocklist.json`
- `canonical_acquisition_map.json`
- `acquisition_hint_normalization_schema.json`
- `normalize_acquisition_hint.py`
- `acq_surface_rewrite_rules.json`
- `acq_surface_design.md`
- `acquisition_null_reason_cases.json`
- `standardization_impossible_samples.json`
- `acquisition_artifact_ownership_table.md`

#### Gate

- 모든 비자연 패턴에 명시적 정화 경로가 배정된다.
- dry run 기준 자동 변환 오탐 `0`을 목표로 규칙이 잠긴다.
- acquisition slot 공급원이 raw literal이 아니라 canonical lexicon으로 바뀔 준비가 된다.
- 주요 산출물의 생산자 / 소비자 / 갱신 주체 경계가 명문화된다.

---

### Phase 7-B. Compose Profile and Sentence Plan Revision

#### 목적

Phase 7-A audit 결과를 기준으로 실제 `compose_profiles.json` 수정과 sentence plan 조정을 Phase 5 이전에 완료한다.

#### 작업

- `compose_profiles.json` revision
- `medical_consumable` 4블록 재조정 반영
- acquisition 블록이 body를 지배하지 않도록 profile별 제한 반영

#### 산출물

- 갱신된 `compose_profiles.json`
- `phase7b_profile_revision_report.json`

#### Gate

- Phase 5 rebuild 전에 profile이 고정된다.
- rebuild에서 검증해야 할 compose profile delta가 더 이상 움직이지 않는다.

---

### Phase 3. Execution

#### 목적

설계된 규칙을 staging review에 반영하고, gate를 통과한 결과만 `staging -> canon promotion`으로 반영한다.

#### Phase 3 write scope

- facts
  - acquisition_hint 정화
  - canonical slot text 반영
  - slot_meta.acquisition_hint canonical trace 반영
- decisions
  - acquisition_hint가 null로 변경된 항목에 한해 `acquisition_null_reason` 추가 또는 갱신
  - `STANDARDIZATION_IMPOSSIBLE` disposition 확정 항목의 decisions 반영

`STANDARDIZATION_IMPOSSIBLE` disposition 확정과 decisions 수정은 같은 Phase 3 staging 경로에서 처리한다.  
Phase 8은 suppress residual migration만 담당하며, Phase 3에서 이미 확정된 항목을 중복 처리하지 않는다.

#### 실행 순서

1. 자동 변환 batch
2. 반자동 후보 batch
3. 수동 전용 batch
4. canonical alignment pre-check
5. gate 검증
6. `staging -> canon promotion`
7. 결정론 해시 재계산

#### batch 분기 기준

| 비자연 항목 수 | 처리 방향 |
|---|---|
| `<= 50` | 수동 정화 중심 |
| `50 ~ 200` | 자동 + 반자동 혼합 |
| `> 200` | 자동 변환 규칙 투자 우선 |

#### canonical alignment pre-check

Phase 3 gate에는 아래 사전 검문을 반드시 포함한다.

- 모든 non-null `facts.acquisition_hint` 값은 canonical_key를 가진다.
- `slot_meta.acquisition_hint.canonical_key`와 facts 값의 정합성이 맞는다.
- `canonical_acquisition_map.json`에 없는 text는 gate에서 차단된다.

이 pre-check는 Phase 4 validator의 pre-implementation 역할을 하며, Phase 4는 이를 코드 계약으로 공식화하는 단계다.

#### canon promotion 대상

current repo 기준 canon promotion target은 아래 경로로 본다.

- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`

#### staging 경로

- `Iris/build/description/v2/staging/acquisition/phase3_execution/`

#### 산출물

- 갱신된 `dvf_3_3_facts.jsonl`
- 갱신된 `dvf_3_3_decisions.jsonl`
- `acq_canonical_alignment_precheck.json`
- `acq_surface_execution_report.json`
- before/after diff archive

#### Gate

- 비자연 판정 항목 정화율 `>= 95%`
- 자동 변환 오탐 `0`
- v1 슬롯 계약 위반 `0`
- canonical alignment pre-check 실패 `0`
- decisions null_reason drift `0`
- 결정론 해시 재계산 정상

---

### Phase 4. Validator Lexical Contract Extension

#### 목적

부자연 acquisition phrase를 style 경고가 아니라 **입력 계약 위반**으로 분리 검문한다.

#### 최소 검문 항목

| 규칙 | 처리 |
|---|---|
| canonical key 없는 acquisition text 금지 | HARD FAIL |
| blocklist raw phrase 포함 금지 | HARD FAIL |
| `facts.acquisition_hint == null -> decisions.acquisition_null_reason` 필수 | HARD FAIL |
| `slot_meta`와 `facts.acquisition_hint` canonical alignment 불일치 | HARD FAIL |
| silent item facts 부재 skip | current 규칙 유지 |
| acquisition slot 내부 비소수점 마침표 `0` | HARD FAIL |
| `forbidden_patterns.json` acquisition section match | HARD FAIL |

#### 구현 대상

- Phase 3 canonical alignment pre-check의 validator 승격
- existing cross-file validator patch
- acquisition lexicon validator 추가
- forbidden pattern acquisition section 연결

#### 권장 경로

- `Iris/build/description/v2/tools/build/validate_layer3_decisions.py`
- `Iris/build/description/v2/tools/build/validate_acquisition_lexicon_contract.py`
- `Iris/build/description/v2/tools/style/rules/forbidden_patterns.json`
- `Iris/build/description/v2/staging/acquisition/phase4_validation/`

#### 산출물

- `validate_layer3_decisions.py` acquisition rule patch
- `validate_acquisition_lexicon_contract.py`
- `forbidden_patterns.json` acquisition section
- `acquisition_lexical_validation_report.json`

#### Gate

- acquisition 오류가 `style lint`, `입력 계약 실패`, `표준화 불가 판정` 세 경로로 분리된다.
- validator를 켰을 때 legacy bootstrap 누락으로 인한 대량 false hard fail이 없다.

---

### Phase 5. Rebuild and Regression

#### 목적

Phase 7-B까지 고정된 profile과 정화된 facts/decisions를 기준으로 full pipeline을 다시 빌드하고, acquisition 이외의 비예상 변화를 차단한다.

#### 실행

1. `facts -> decisions -> compose -> normalizer -> rendered` 재빌드
2. 기존 rendered 대비 diff 분석
3. validator 전량 재실행
4. golden subset 검증
5. in-game manual validation

#### 변경 허용 범위

- 허용
  - acquisition_hint가 정화된 항목의 acquisition block 변화
- 비허용
  - identity / primary_use block 변화
  - unrelated item rendered 변화

#### staging 경로

- `Iris/build/description/v2/staging/acquisition/phase5_rebuild/`

#### 산출물

- `acq_surface_rebuild_report.json`
- 갱신된 rendered authority artifact
- 결정론 해시 갱신

#### Gate

- introduced hard fail `0`
- 비예상 변경 `0`
- golden subset pass
- in-game validation pass

---

### Phase 6. Conditional Micro-Josa Shim

> 이 phase는 조건부다.

#### 개방 조건

Phase 5 완료 후 residual josa mismatch를 측정한다.  
아래 조건 코드 세 개를 같이 평가한다.

| 조건 코드 | 내용 |
|---|---|
| `COUNT` | 잔여 불일치 `> 30`건 |
| `GOLDEN_FAIL` | golden subset의 acquisition block에서 조사 불일치 발생 |
| `PROFILE_CONCENTRATION` | 동일 canonical family에서 5건 이상 집중되거나 상위 노출 profile에서 반복 발생 |

개방 판정 규칙은 아래처럼 잠근다.

- 세 조건이 모두 미충족이면 B축 전체 스킵
- `COUNT`만 충족하고 `GOLDEN_FAIL`, `PROFILE_CONCENTRATION`이 모두 미충족이면 facts 추가 정화를 먼저 시도하고 B축 진입을 보류
- `GOLDEN_FAIL` 또는 `PROFILE_CONCENTRATION`이 충족되면 residual count가 작아도 B축 진입을 검토

#### 개방 시 원칙

- acquisition_hint 슬롯에만 적용
- 허용 조사 pair는 최대 `은/는`, `이/가`, `을/를`, `에서`, `으로/로`
- 종성 판별은 결정론적 함수 1개로만 처리
- `phrasebook_ko.json`, `ko_particles.json`은 건드리지 않음
- v2 `josa_adaptive`와 독립된 self-contained 예외로 봉인
- 호출 관계는 compose acquisition block path에 직접 삽입한다.
  - `normalize_acquisition_hint.py`는 `micro_josa.py`를 호출하지 않는다.

#### 구현 후보

- `Iris/build/description/v2/acquisition/micro_josa.py`

#### 산출물

- `acq_josa_mismatch_audit.json`
- `acq_micro_josa_design.md`
- `micro_josa.py`
- `acq_micro_josa_validation_report.json`
- `docs/DECISIONS.md` micro-josa 봉인 항목

#### Gate

- 단위 테스트 100% pass
- introduced hard fail `0`
- non-acquisition block 변화 `0`
- `DECISIONS.md` 봉인 완료

---

### Phase 7. Split Note

이 phase는 고정된 실행 순서상 두 조각으로 분리해 앞단으로 이동했다.

- `Phase 7-A`
  - profile / sentence_plan read-only audit
- `Phase 7-B`
  - actual `compose_profiles.json` revision

따라서 current round에서 profile 관련 실제 수정은 **Phase 5 rebuild 이전**에 모두 닫혀 있어야 한다.

단, Bootstrap / Phase 2 결과가 `Phase 7-A`의 결론을 실제로 뒤집는 경우에만 `Phase 7-A` one-shot rerun을 허용한다.

---

### Phase 8. Suppress Retirement

> 실행 시점은 Phase 5 이후다.

#### 목적

지금의 suppress 기반 zero-hit 운영을 canonical normalization 또는 null reason 기반 운영으로 교체한다.

#### 작업

- exact acquisition phrase exception 순차 제거
- simple discovery shape exception을 canonical normalization으로 대체
- 제거 불가능한 suppress는 잔류 사유를 기록하고 후속 과제로 이관
- suppress residual 중 Phase 3에서 아직 disposition 확정되지 않은 항목만 null_reason migration 대상으로 검토

남기는 예외는 아래 둘뿐이다.

- migration safety pin
- `STANDARDIZATION_IMPOSSIBLE` 전환 대기

#### staging 경로

- `Iris/build/description/v2/staging/acquisition/phase8_suppress_retirement/`

#### 산출물

- `acquisition_exception_retirement_plan.md`
- `suppressed_phrase_residuals.json`
- `exception_to_null_reason_migration.json`
- suppress retirement diff

#### Gate

- acquisition phrase 문제가 suppress 0-hit가 아니라 normalization 또는 null reason으로 닫힌다.
- Phase 3에서 이미 확정된 `STANDARDIZATION_IMPOSSIBLE` 항목과 중복 처리되지 않는다.

---

### Phase 9. Coverage and QA

#### 목적

실데이터 기준으로 acquisition null이 전부 구조적으로 설명되는지 검증한다.

#### 집계 항목

1. `normalized_success`
2. `UBIQUITOUS_ITEM`
3. `STANDARDIZATION_IMPOSSIBLE`
4. `residual_manual_review`

#### 작업

- warning false positive 비율 실데이터 점검
- 전 아이템 분모 기준 acquisition coverage 재집계
- null reason 분포 점검
- residual manual review 잔량 측정
- same family residual closure 점검

#### staging 경로

- `Iris/build/description/v2/staging/acquisition/phase9_coverage_qa/`

#### 산출물

- `acquisition_coverage_report.json`
- `acquisition_null_reason_distribution.json`
- `acquisition_false_positive_review.md`

#### Gate

- acquisition null 100%가 `UBIQUITOUS_ITEM` 또는 `STANDARDIZATION_IMPOSSIBLE`로 설명된다.
- 동일 phrase family 반복 잔여분은 전부 disposition이 부여되어 있다.

---

## 5. 실행 순서

phase number보다 실행 순서 authority가 우선한다.

```text
Phase 0      scope lock / authority freeze
    ->
Phase 1      audit
    ->
Phase 7-A    profile / sentence_plan read-only audit
    ->
Bootstrap    legacy canonical backfill
    ->
Phase 2      canonical lexicon + normalization design
    ->
Phase 7-B    profile / sentence_plan revision
    ->
Phase 3      execution
    ->
Phase 4      validator lexical contract
    ->
Phase 5      rebuild + regression
    ->
Phase 6      conditional residual josa audit
        -> skip
        -> or micro-josa implementation
    ->
Phase 8      suppress retirement
    ->
Phase 9      coverage / QA
```

병렬 허용은 아래 둘로 제한한다.

- Phase 1 audit와 suppress inventory 수집
- Phase 5 이후 Phase 8 suppress retirement 설계와 Phase 9 QA 설계의 read-only 준비

그 외 단계는 authority drift를 막기 위해 직렬로 유지한다.

---

## 6. 우선 수정 경로

| 우선순위 | 파일/경로 | 목적 |
|---|---|---|
| P0 | `docs/iris-dvf-3-3-acquisition-hint-korean-standardization-execution-plan.md` | execution authority |
| P0 | `docs/iris-dvf-3-3-acquisition-hint-scope-lock.md` | 범위 봉인 |
| P1 | `Iris/build/description/v2/staging/acquisition/bootstrap/` | legacy bootstrap authority |
| P1 | `Iris/build/description/v2/acquisition/` | canonical lexicon / schema / rewrite rules / normalization entry |
| P1 | `Iris/build/description/v2/staging/acquisition/phase1_audit/` | audit authority |
| P1 | `Iris/build/description/v2/tools/build/validate_layer3_decisions.py` | null reason / cross-file lexical contract |
| P1 | `Iris/build/description/v2/tools/build/compose_layer3_text.py` | acquisition slot consumption and micro-josa insertion seam |
| P1 | `Iris/build/description/v2/data/compose_profiles.json` | profile / sentence_plan 조정 |
| P2 | `Iris/build/description/v2/tools/style/rules/forbidden_patterns.json` | acquisition forbidden pattern 연결 |
| P2 | `Iris/build/description/v2/staging/acquisition/phase5_rebuild/` | rebuild / regression pack |

---

## 7. 금지 목록

이번 라운드 전 phase 공통 금지선은 아래처럼 고정한다.

- acquisition surface 문제를 이유로 facts/evidence/cluster를 의미론적으로 재판정하는 것
- style linter를 baseline-delta gate 또는 publish gate로 승격하는 것
- compose 외부 repair/rewrite stage를 재도입하는 것
- `acquisition_hint`를 배열이나 multi-slot 구조로 확장하는 것
- `identity_hint`, `primary_use`까지 동일한 lexical naturalization round로 끌고 가는 것
- `candidate_state`, active/silent, publish_state를 acquisition lexical round에 묶는 것
- `phrasebook_ko.json`, `ko_particles.json`, `josa_adaptive`를 선행 도입하는 것
- suppress removal을 style zero-hit 유지용 cosmetic 작업으로 읽는 것

---

## 8. 최종 성공 기준

1. `facts.acquisition_hint`는 raw 번역투 literal을 직접 받지 않는다.
2. canonical lexicon을 거치지 않은 acquisition text는 validator에서 HARD FAIL이다.
3. `facts.acquisition_hint = null`이면 `decisions.acquisition_null_reason`이 구조적으로 남는다.
4. 비자연 판정 항목 정화율은 `>= 95%`다.
5. golden subset 내 critical residual은 `0`이다.
6. 동일 phrase family 반복 잔여분은 전부 disposition이 부여되어 있다.
7. suppress exception은 크게 줄고, 예외 대신 normalization 또는 null reason으로 닫힌다.
8. compose는 계속 literal 조합기다.
9. style linter는 끝까지 advisory-only다.
10. introduced hard fail `0`, golden subset pass, in-game validation pass를 유지한다.
11. acquisition null 100%가 구조적으로 설명 가능하다.
12. active/silent 재판정은 별도 단계로 분리된 채 유지된다.

---

## 9. 한 줄 요약

이번 라운드는 acquisition을 위한 새 한국어 엔진을 만드는 일이 아니라, **legacy bootstrap과 canonical lexicon, 입력 표준화 계층, canonical alignment gate를 통해 `acquisition_hint`를 raw 번역투와 suppress 의존 운영에서 분리하는 실행 계획**이다.
