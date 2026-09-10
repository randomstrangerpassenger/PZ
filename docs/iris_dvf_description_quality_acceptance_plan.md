# Implementation Plan

DVF-COMPOSITION-3 — 전체 생성 문장의 의미·언어 품질 검수, 규칙 수정 및 B/C 인계

- 작성일: 2026-09-11
- 상태: complete — 일반 도구/재료 compact 잔여 결함까지 공통 규칙에서 교정하고 영향 29조합/31 items를 재독했다. 최종 focused 검사 exit 0. 생존 모드 공개 범위와 Q1~Q3 offline 품질/B·C 공통 인계의 정확한 범위는 [실행 기록](iris_dvf_description_quality_acceptance_closeout.md)을 따른다.
- 기반: 사용자 제공 「DVF-COMPOSITION-3 종합 Roadmap」(2026-09-10), `docs/PLAN_TEMPLATE.md`
- 개정 근거: 기존 종합 Review와 사용자의 후속 평가 반영 요청. 원문 검수와 수정 코드 기준선 확인을 분리하고, 기록 형식·자동 검사·Gate를 최소화했다. R-1은 입력/코드 차이의 확인 목적만 유지하며 원문 검수의 선행 Gate로 사용하지 않는다.
- 선행: DVF-COMPOSITION-1/2 complete. 후속: B(Tooltip S2), C(Menu expanded).
- 문제 정의: [description quality acceptance problem](iris_dvf_description_quality_acceptance_problem.md)

## 1. Objective

저장된 Problem 2 설명 corpus의 exact FullType 2,105개 × KO/EN × compact/expanded, 총 8,420개 state를 회계한다. 모든 present surface의 실제 의미·언어 품질과 item별 조합을 검토하고, 현재 composition/locale 책임에서 해결 가능한 결함을 공통 생성 규칙에 수정한다. 재생성 후 영향 범위를 다시 읽어 최종 subject에 coverage를 결속하고, B와 C에 같은 설명 corpus와 의미 연결을 인계한다.

종료점은 **offline description corpus의 품질 수락과 B/C 인계 준비**다. 저장 구조의 유효성, `present`, `failed=0`, 기존 Problem 2 테스트 성공은 전수 품질 수락을 대신하지 않는다.

Tooltip은 화면 기준 최대 4줄이며, 1행은 2계층 소분류, 2행은 DVF 설명, 3행은 획득 장소, 4행은 레시피·우클릭 행동·자유 조리 중 무작위 상호작용이다. Compact는 이 **두 번째 한 줄에 사용할 역할·기능 개요**다. 문제 3은 그 목적에 맞는 간결성과 의미 보존을 검수하고, 실제 폰트·폭·UI scale에서 한 줄에 들어가는지는 B에서 확인한다. 최대 4 logical slot으로 재해석하거나 별도 글자 수·문장 수·폰트 측정 Gate를 만들지 않는다.

## 2. Scope

- 현재 `Iris/build/description/composition/descriptions.json`의 KO/EN compact·expanded 원문, 상태, reason, segment 및 의미 연결.
- `blocks.json`과 대조한 role/function/target/result, qualifier application, negative, alternative, unresolved relation 및 acquisition/semantic 구분.
- Item별 네 surface를 함께 보는 검수 자료, expression-family 검토, 저빈도·unique 조합 검토, current-input absent 판정.
- Planner, family, lexicon, KO/EN realization 및 실제 조합 owner의 bounded correction과 재생성·delta·영향 범위 재검수.
- 실제 의미 구조 오류에 한한 Problem 1 최소 환류. 사실 근거 부족은 기존 semantic/audit owner의 evidence 확인과 limitation 기록으로 분리.
- Final identity, 전체 coverage, defect/absence disposition, B/C 소비 좌표와 제한의 공통 인계.

### Explicitly Out Of Scope

- r6 원본/adoption 및 L3-05/L3-06 authority 변경, product pointer, promotion, install/package.
- Current Tooltip/Menu, Lua runtime, S1/S3/S4, Alt 활성 조건, 최대 4줄 조립 정책 변경.
- B의 strict production admission/finalization, C의 UI 연결, PZ 폰트·폭·UI scale에서의 physical fit 측정.
- 전체 게임 사실 재조사, unresolved 전체 해소, Layer 4/profile taxonomy 재설계, 관련 없는 refactor.
- 별도 검수 웹 앱, 정규 validator taxonomy, quality-score authority, proof tree 또는 sealing lifecycle 신설.

## 3. Non-Goals

문장을 짧게 만들기 위해 대표 용도 하나만 선택하거나 `primary_use`를 복원하지 않는다. 중요도 추정·문자 수 절단·조건/부정/대안 삭제·역할 전환으로 가독성을 얻지 않는다. 공백 0개, 정해진 문장 수, 결함 개수 quota, 고정 polish 횟수를 목표로 삼지 않는다.

게임 내 설명을 사실보다 풍부하게 만드는 작업이 아니다. 아이템 이름이나 일반 지식에서 새 fact를 추론하거나 evidence gap을 자연스러운 문장으로 감추지 않는다. 실제 expanded 문장에 없는 정보를 audit/ref에 남았다는 이유로 공개 보존 완료로 계산하지 않는다.

## 4. Assumptions

### 확인한 repository 기준선

2026-09-11 checkout의 코드와 저장 파일을 확인했다. 아래 SHA-256은 계획 작성 시 실제 파일 bytes의 식별자이며, 실행 착수 때 다시 확인한다.

| 대상 | 현재 기준 |
| --- | --- |
| 의미 입력 | `Iris/build/description/composition/blocks.json` |
| 입력 SHA-256 | `b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796` |
| 설명 결과 | `Iris/build/description/composition/descriptions.json` |
| 결과 SHA-256 | `bef16e498e1d7ba007379310535be4d707b9877dce97e7ebc7109afd7e1364bf` |
| Schema | `iris-layer3-descriptions-v1`, version 1 |
| 선행 의미 구성 | 2,105 items, 29,202 facts, 10,304 blocks — Problem 1/2 closeout 기준 |
| 현재 저장 결과 summary | 8,420 states, 각 locale compact present 1,984 / absent 121, expanded present 2,043 / absent 62 |

두 locale 합계 present 8,054, absent 366이다. 저장 summary는 출현 state만 기록하므로 failed 키가 없음을 검수 도구에서 명시적 0으로 회계한다. 전체 키·대상 집합·reason 검증은 실행 Phase 1/2의 책임이다. 최종 분포를 이 숫자에 강제로 맞추지 않고 정상 수정으로 달라진 경우 전후 차이를 설명한다.

### 코드에서 확인한 책임과 실행 제약

| 코드/기록 | 확인 내용과 계획에 미치는 영향 |
| --- | --- |
| `description_composition_results.read_result(root, path=...)` | JSON을 읽고 `model.validate_result`를 호출한다. 입력 reader나 producer를 호출하지 않으므로 검수 착수 재생성이 불필요하다. |
| `description_composition_results.produce` | 저장 blocks를 읽고 입력 hash와 7개 composition 모듈 및 4개 참고 어휘 모듈의 hash를 기록한다. 수정 시 이 실제 소비 집합을 identity에 포함한다. |
| `description_composition_results._compact/_expanded/_clauses` | 저장뿐 아니라 그룹화·문장 합성·연결 생성도 소유한다. 모든 표현 결함을 families/locale 모듈에만 귀속하지 않는다. |
| `description_composition_planner.plan` | qualifier application이 같은 context/role을 결합하고 상세 배치와 조명 운영 상세를 결정한다. 문자열 길이나 FullType에 따른 의미 선택을 도입하지 않는다. |
| `description_composition_families.frames` | Payload와 실제 result 관계에 따른 조건부 합성 경로다. 미지원 추가 qualifier가 닫힌 규칙에 잘못 흡수되는지 검토한다. |
| `description_composition_ko/en.role/parallel/qualified` | 병렬 술어와 조건 접속을 실현한다. 공유 술어가 독립 조건을 전체 목록으로 확장하는지 실제 문장으로 확인한다. |
| `description_composition_lexicon` | `expression_rules`, `recovery_expression`, `recovery_sources`, `acquisition_expression`의 어휘를 참고한다. 공통 참고 모듈 변경은 과거 경로에도 영향을 줄 수 있으므로 우선 현 composition owner에서 수정한다. |
| `description_composition_model.validate_result` | 상태/text, segment/ref, qualifier application, detail link, summary의 구조를 검사한다. 실제 문장 의미·문법·자연스러움을 판정하지 않는다. |
| `tooltip_s2_supply.build` | `recovery.load_adopted`와 r6 `locales[loc]['s2']`를 소비한다. 새 `locales[loc]['compact']`의 직접 consumer가 아니다. 인계 준비와 B adapter 적용 완료를 구분한다. |
| `composition_results` / `recovery` | 현재 채택 입력 로드는 `load_adopted`를 사용하며 historical 재현은 분리되어 있다. 2026-09-09 exact-input 사고를 현재 정상 readback의 동일 실패로 단정하지 않는다. |

현재 B 상태는 `DECISIONS.md`의 더 구체적인 기록을 따른다: B 전체 partial, production 축 blocked, runtime unvalidated_but_in_scope, promotion deferred. 로드맵의 `implemented_only / PZ 대기`는 구현 축의 요약으로만 사용한다. C는 미완료이고 current 제품은 predecessor다. r6의 bounded unresolved 4,223개는 upstream 기록이며 새 corpus의 품질 결함 수가 아니다.

`docs/review/description/review-report.md`와 그 추출물은 **r6 대상 과거 검수**다. 위험 유형의 참고로 쓰되 새 Problem 2 corpus의 검수 coverage나 absence reason으로 승계하지 않는다.

기존 dirty 수정·삭제·untracked 파일이 다수 존재한다. 실행 전 현재 상태를 기록하고 이번 작업 변경만 구별한다. 독립 검토 자격이나 외부 도구 가용성은 가정하지 않는다.

## 5. Repository Areas Affected

### Code

주 수정 후보는 `Iris/tooling/src/iris_tooling/domains/layer3/`의 다음 파일이다. 실제 defect owner에 해당하는 파일만 수정한다.

- `description_composition_planner.py`, `description_composition_families.py`
- `description_composition_lexicon.py`, `description_composition_ko.py`, `description_composition_en.py`
- `description_composition_results.py`, `description_composition_model.py`
- 조건부 Problem 1 환류: `composition_rules.py`, `composition_model.py`, `composition_results.py`
- 회귀 검사: `Iris/build/description/v2/tests/test_layer3_description_composition.py`; Problem 1 변경 시 `test_layer3_composition.py`

`tooltip_s2_supply.py`, `product_projection.py`, `product_install.py`, runtime lookup/renderer와 Tooltip/Menu Lua는 소비 경계를 확인하는 참조 대상이다. 본 계획에서 수정하지 않는다.

### Docs

- 본 계획: `docs/iris_dvf_description_quality_acceptance_plan.md`
- 실행 결과 신규 기록: `docs/iris_dvf_description_quality_acceptance_closeout.md`
- 신규 검수 자료는 역할 중심의 짧은 경로 `docs/review/prose/`를 기본으로 하되 기존 자료와 충돌하면 역할에 맞는 짧은 경로를 선택한다. 과거 r6 검수 범위를 승계하지 않는다.
- 실제 규칙 계약이 달라질 때만 `docs/iris_dvf_description_composition_contract.md` 및 walkthrough의 관련 절 갱신.
- 종료 시 `docs/DECISIONS.md`, `docs/ROADMAP.md`에 실제 범위와 잔여 책임을 additive 기록. 본 계획에서 `docs/ARCHITECTURE.md` 본문은 실제 책임/흐름/소비 계약 변경이 있을 때만, 남은 exact-input 소비가 끝난 뒤 관련 절을 갱신한다. 이 조건을 §9와 §11에도 동일하게 적용한다.
- 기존 ARCHITECTURE의 model/results 요약에는 실제 results의 `_compact/_expanded/_clauses` 합성 책임이 충분히 드러나지 않는다. 이 기존 서술 차이는 closeout에 공개한다. 서술 차이의 발견이나 종료 사실 기록 자체를 architecture 변경으로 취급하지 않으며, 실제 책임/흐름/소비 계약 변경이 없으면 본 작업에서 ARCHITECTURE 본문을 편집하지 않는다.

### Config

기본 변경 없음. `Iris/validation/execution/required_validations.json`, `contracts/repository_test_gate.json`, `Iris/tooling/pyproject.toml`은 적용 계약 확인 대상으로만 사용한다. 검사를 통과시키기 위한 registry/계약 완화는 하지 않는다.

### Generated Artifacts

- 규칙 수정 후 `Iris/build/description/composition/descriptions.json` 재생성.
- 실제 Problem 1 수정이 있을 때만 `Iris/build/description/composition/blocks.json` 재생성.
- 비교용 생성 결과는 기존 writer의 경계에 맞춰 `Iris/build/description/composition/quality_review/` 아래 보존한다. `_path`는 composition 디렉터리 밖 저장과 blocks 덮어쓰기를 거부하므로 우회하지 않는다.
- 검수 기록에는 대상/읽은 범위/미검수, 원문 결함과 공통 규칙 수정·영향 결과, 최종 B/C 인계 정보를 남긴다. 이 정보를 기존 기록이나 소수 파일에 합칠 수 있으며 파일 수·형식·행별 hash를 강제하지 않는다. 별도 baseline/state/family/defect/delta/handoff 파일, manifest, seal, receipt, proof tree는 요구하지 않는다. 기록은 현재 작업의 보조 자료이며 새 validation authority가 아니다.

## 6. Planned Changes

아래 Phase는 작업 설명이며 각각의 승인·독립 Gate·별도 workspace가 아니다. 읽기·분류·수정·재검토는 필요한 범위에서 묶거나 앞당길 수 있다. 최종 수락은 §12의 세 결과를 함께 확인하는 한 번의 closeout으로 묶는다. 문서상 owner approval은 사용자의 사전 승인으로 충족된 것으로 처리하되 도구·플랫폼의 별도 권한 확인은 우회하지 않는다.

### Change 1 — 저장 corpus 기준선 고정 (Phase 1)

**Purpose:** 실제 검수 대상과 수정 전 원문을 재생성 없이 고정한다.

**Files:** 저장 descriptions/blocks, 기존 reader/model, 신규 검수 자료 디렉터리.

**Implementation Notes:**

1. Git 상태를 확인하고 실제 수정할 파일의 시작 bytes를 보존하여 기존 dirty 변경과 구별한다. 수정하지 않는 r6/adoption/current pointer/package의 별도 identity 목록이나 보존 증명은 만들지 않는다.
2. `read_result()`로 저장 descriptions를 읽고 corpus digest, schema/version 및 기존 input/producer identity를 재사용한다. 원문 언어 검수는 이 저장 결과를 대상으로 바로 시작할 수 있다. Plan hash와 다르면 현재 검수 대상을 기록하며 과거 수락을 승계하지 않는다.
3. 저장 input identity와 실제 blocks를 대조하여 의미 검수에 사용할 입력을 확인한다. 불일치 시 결속된 입력 또는 근거 있는 successor를 저장소 내에서 확보하고, 확보 전에는 해당 의미 대조·수락만 보류한다. 독립적인 원문 검수는 계속한다. 전체 item/state 회계는 Phase 2와 같은 읽기 결과를 공유한다.
4. 코드 수정·재생성 전에 실제 소비 producer 파일과 저장 identity의 차이, 사용할 현재 코드 상태 및 관련 기존 변경을 확인한다. 과거 코드가 없으면 그 한계와 재생성 후 확인할 영향 범위를 기록한다. 과거 Problem 1 producer 복원·hash 목록 신설·historical replay를 선행 과제로 만들지 않으며 현재 hash를 과거 생성 hash로 소급하지 않는다. 실제 Problem 1 수정 시에만 해당 코드와 입력까지 살핀다.
5. 과거 producer 정보 부재나 코드 hash 차이만으로 Phase 3을 막지 않는다. 재생성 결과를 현재 규칙의 수정 효과로 설명할 수 없는 경우 Phase 5에서 관련 결과를 재검토한다. 영향 범위를 좁힐 근거가 없을 때만 넓게 확인하며 과거 변경 이력의 완전한 복원을 요구하지 않는다.
6. 수정 전 원문을 비교할 수 있게 필요한 사본만 기존 출력 경계 안에 보존한다. 기존 경로 보호 기능을 사용하고 이를 위한 독립 사전 테스트를 추가하지 않는다. 최초 검수만을 이유로 producer/CLI/생성 테스트를 실행하거나 identity를 맞추기 위해 재생성·hash 치환하지 않는다.

**확인:** 검수할 저장 원문과 의미 입력, 재생성에 사용할 현재 코드 및 알려진 차이를 필요한 시점에 확인한다. Phase 2의 회계와 기록을 공유하며 별도 진입 승인·baseline PASS·고정 산출물을 요구하지 않는다. 입력을 확인하지 못한 의미 판정은 미확인으로 남기고 언어 검수와 구별한다.

### Change 2 — 검수 좌표·grouping 및 current absence (Phase 2)

**Purpose:** 모든 surface를 누락 없이 실제 검토에 연결한다.

**Files:** §5의 검수 자료 및 필요한 최소 read-only 추출 helper.

**Implementation Notes:**

- 한 item에 KO compact / EN compact / KO expanded / EN expanded 원문, state/reason, segment→block/branch/fact/relation refs, qualifier application, disposition, detail link 및 필요한 blocks를 함께 제시한다.
- 검수 키는 `(corpus digest, item_id, locale, surface)`다. 대상 원문과 검토 방식, 공통 검토의 재사용 근거, item 조합 확인, 결함 및 판정을 추적할 수 있게 한다. 필드 형식이나 surface별 hash는 강제하지 않으며 검토 방식과 품질 판정은 구별한다.
- 검토 방식은 개별 정독 / 공통 표현 검토+item 조합 확인 / absent reason 확인 / 미검수로 구분한다. 판정은 수락 / correction 필요 / 정상 부재 / upstream limitation / 미확인으로 구분한다. 미검수 행을 미리 수락 처리하지 않는다.
- Expression label 하나만으로 family를 정의하지 않는다. 실제 grammar/lexicon 경로, qualifier scope, branch 구조, 반복 skeleton을 함께 본다. Long list, 반복 clause, raw token, KO/EN outlier, mixed acquisition, low-frequency/unique shape는 읽기 순서 선별 신호다.
- 공유 기록에 재사용한 검토의 원문·locale grammar path와 equivalence 근거를 기록한다. Clause realization, qualifier attachment, coordination, target list, negative/alternative가 다른 경우 해당 차이가 기존 검토로 덮이는지 명시적으로 확인한다. 같은 family/skeleton이라는 이유로 자동 승계하지 않으며, 근거가 부족하면 별도 표현 검토를 한다. Item별 의미 결속 확인은 어느 경우에도 생략하지 않는다.
- 현재 blocks가 없는 62개는 양 locale·양 surface absent, acquisition-only 59개는 양 locale compact absent/expanded present인지 item별 대조한다. 과거 r6의 `scoped_not_applicable`/`upstream_gap` 분류를 복사하지 않는다.
- 설명되지 않는 absence·한 locale만의 누락·failed는 생성 결함 후보로 보낸다. 정상 absence에 언어 품질 PASS를 부여하지 않는다.

**Validation:** 전체 8,420개 키가 정확히 한 번 회계되고 triage 비선별 item도 남는다. 검수 범위와 absent 근거를 공유 기록에 남긴다. helper가 만든 목록만으로 실제 정독 완료를 주장하지 않는다.

### Change 3 — 전수 의미·언어·깊이 교차 검토 (Phase 3)

**Purpose:** 모든 present 원문에 표현 규칙 검토와 item 조합 검토를 모두 확보한다.

**Files:** 검수 자료, 저장 descriptions/blocks 및 필요한 기존 semantic/audit evidence.

**Implementation Notes:**

- 의미: role/function/target/result 방향, block_common/branch_local 조건, 부정·대안, 독립 branch, 미확정 관계, acquisition/semantic 구분을 실제 텍스트와 대조한다.
- Compact: 첫 이해를 위한 역할·기능 개요인지, 절차/수치/대상 나열이 개요를 압도하는지 확인한다. 화면 없이 확인 가능한 문장 결함을 B의 physical_fit 이슈로 넘기지 않는다.
- Expanded: 이동 detail의 실제 public sentence, 올바른 조건 결속, 불필요한 반복과 Layer 4 행동 목록 재복제를 확인한다. Detail link가 있다는 사실만으로 보존을 인정하지 않는다.
- KO: 조사·호응, 병렬 구조, 수식 범위, 모호한 생략, 명사화, 영어식 어순, 추상 상투구와 내부 용어를 확인한다.
- EN: 주어/술어, 관사/전치사, 수일치, coordination/qualifier scope, 직역투·명사화·모호한 동사·반복을 확인한다.
- KO/EN: 문장 수나 구조의 일치가 아니라 역할·대상·조건·결과·부정·대안·limitation 및 compact/expanded 배치의 의미 parity를 확인한다.
- Hammer 수리 대상/도구, Notebook 읽기/쓰기/잠금 조건, 연료/불쏘시개 점화 조건, CandleLit 점화 대상, 물 용기 독성, 창낚시/마모 미확정 관계를 회귀 sentinel로 포함한다. 이 대표군만으로 전수를 대체하지 않는다.
- 초반에 광범위한 structural defect가 확인되면 영향 family의 수락을 계속 쌓기 전에 Problem 1 bounded feedback 여부를 판단한다. 해당 집합은 Phase 4/5로 먼저 보내 수정·재투영 후 재개하고, 독립적인 나머지 검수는 계속한다. 이 조기 분기는 Phase 3 전체 종료를 기다릴 의무를 만들지 않으며, 사실 재판정까지 범위를 확대하는 근거도 아니다.

**Validation:** 각 present surface의 실제 읽기 근거와 item 조합 확인을 남긴다. 결함 기록에는 before 원문, 필요한 refs, 문제와 의미/언어 영향, 수정 owner·방향 및 영향 결과를 알아볼 수 있게 남긴다. 동일 결함군의 근거는 공유할 수 있다. Length 지표로 자동 수락하지 않는다.

### Change 4 — owner별 규칙 수정 (Phase 4)

**Purpose:** 발견 결함을 재생성 후에도 유지되는 수정으로 해결한다.

**Files:** §5의 실제 owner 모듈 및 관련 회귀 fixture.

| 결함 | 우선 수정 owner |
| --- | --- |
| Compact/expanded 의미 배치 | planner |
| 조건부 기능군 합성 | families |
| 공통 어휘·조건 표현 | lexicon |
| KO/EN 조사·어순·병렬·호응 | 해당 locale realization |
| 일반 문장 병합·분할, scope별 grouping | results의 `_compact`, `_expanded`, `_clauses` |
| State/ref/serializer 구조 불일치 | model/results |
| 잘못된 block/branch/qualifier/relation 의미 구조 | Problem 1의 composition owner |
| Fact 근거 부족 | 기존 semantic/audit evidence 확인 후 upstream limitation |
| PZ 실제 렌더링에서만 판정 가능 | B 후속 검증 |

**Implementation Notes:** output JSON 수기 수정이나 일반 FullType replacement를 사용하지 않는다. Lexicon/locale 계층에 의미 선택 책임을 숨기지 않는다. Correction 전에 예상 영향 rule/item/surface와 보존해야 할 조건을 기록한다. Problem 1 환류는 refs로 확인된 구조 오류만 최소 수정하고 blocks→descriptions까지 재투영한다.

관계·조건의 새 의미 재판정, source authority 변경, schema/read_result 소비 계약 변경이 필요하면 해당 변경을 자동 적용하지 않는다. 재현 사례와 B/C 영향, 필요한 후속 범위를 기록하고 그 변경에 의존하는 수락은 보류한다. 나머지 독립 검수는 계속한다.

**Validation:** 이 단계에서는 owner 귀속, code diff, 예상 영향 범위와 재검토 조건을 확인한다. 의미·조건·조합 회귀를 기존 검사로 확인할 수 없을 때만 최소 반례를 기존 focused test에 추가한다. 단순 어휘 교정이나 문체 조정마다 fixture를 만들거나 구현을 복제한 테스트를 추가하지 않는다. 원결함 제거와 의미/qualifier 보존, 양 locale의 실제 correction 성공은 Phase 5 재생성 원문에서 관찰한 증거로만 확정하고, automated test 결과는 §7 final 묶음에 귀속한다. 코드 수정만으로 correction 완료를 기록하지 않는다.

### Change 5 — 재생성·delta·영향 범위 재검토 (Phase 5)

**Purpose:** 수정이 해결한 범위와 새 회귀를 실제 결과에서 확인한다.

**Files:** 수정 모듈, comparison/final descriptions, delta 및 coverage evidence.

**Implementation Notes:**

1. 실제 rule/input 수정이 생긴 뒤에만 producer를 실행한다. 현재 `produce`는 전체 생성 API이므로 필요한 전체 deterministic 생성은 허용하되, 존재하지 않는 부분 생성 기능을 가정하지 않는다.
2. 비교에 필요한 수정 전후 결과를 사용해 text뿐 아니라 state/reason, segments, refs, qualifier application, detail link, input/producer identity를 비교한다.
3. Phase 1에서 기록한 사전 dirty/code 차이와 이번 correction의 예상 영향을 구분한다. 변경을 설명하는 데 필요한 수준에서 사전 변경과 이번 수정의 영향을 구분한다. 분리 근거가 부족하면 이번 correction만의 효과로 단정하지 않고 관련 결과를 재검토한다. 과거 이력의 완전한 분해나 candidate별 비교 행렬을 요구하지 않는다. Expected change와 unexpected change를 분리하고 예상 밖 delta를 모두 설명하거나 제거한다. 최종 state 분포 변화도 item별 이유에 결속한다.
4. Actual delta와 rule 영향 집합의 합집합을 재검토한다. Text가 같아도 의미 입력·refs·조건·공통 검토 근거가 달라졌으면 재사용하지 않는다. 전역 규칙이면 영향 범위도 전역일 수 있다.
5. 변경 surface는 이전 판정을 자동 승계하지 않는다. 무변경 surface만 text/state/ref/입력과 family 검토 유효성이 유지됨을 확인한 후 근거 ref로 재결속한다.
6. Correction reread에서 가독성을 높이는 과정에 근거 밖 해석·추천·효율 판단·우열 표현이 새로 들어가지 않았는지 양 locale에서 확인한다. 중립성 점검을 각 correction의 실제 after 원문과 coverage 기록에 결속한다.

**Validation:** 실제 변경 및 규칙 영향 surface의 원문과 필요한 KO/EN·compact/expanded 연결을 재검토한다. 무관한 표면의 재독은 반복하지 않는다. Detail/qualifier 보존과 예상 밖 변경을 같은 검수 기록에서 확인하며 별도 delta 파일을 강제하지 않는다. 반복은 실제 결함·새 변경 때문에 필요한 경우에 한한다.

### Change 6 — 최종 수락과 B/C 공통 인계 (Phase 6/7)

**Purpose:** 최종 bytes에 결속된 품질 수락을 기록하고 소비 변경에 필요한 좌표를 제공한다.

**Files:** final descriptions, 최종 검수 evidence, 신규 closeout, 필요한 governance 관련 절.

**Implementation Notes:**

- 최종 exact 2,105 items, 8,420 states, present coverage, absent reason, failed를 재회계한다. 검토 누락·해결 가능한 in-scope defect·설명되지 않은 delta가 있으면 complete로 닫지 않는다.
- Closeout 또는 공유 인계 기록에는 final 경로·bytes digest·schema/version·input/producer identity·의미 lineage, 전체 분포, 실제 검수 범위와 limitation을 함께 기록한다. 별도 seal이나 adoption으로 만들지 않는다.
- B 소비 좌표: `items[].locales[ko/en].compact`. C 소비 좌표: 같은 item/locale의 `expanded`. 공통 refs, qualifiers/relations/unresolved, `detail_links`, `qualifier_dispositions`, state/reason 해석을 함께 제공한다.
- 기존 B의 r6 `s2` supply와 새 `compact`/`segments` 구조 차이를 명시한다. 이 문서의 handoff는 B adapter·production admission 완료가 아니다. C도 같은 final identity를 사용하도록 후속 연결 요구를 남긴다.
- Closeout은 Problem 3가 새로 준비한 final corpus/coverage와 B의 기존 historical 공급 이력, 실행 시점 S2 candidate 상태, production/runtime 잔여를 별도 항목으로 기록한다. 현재 상태는 해당 B 기록에서 다시 확인하고 r6 기반 과거 구현 상태를 새 corpus candidate의 적용 상태로 승계하지 않는다.
- Schema/reader가 유지되는지 확인하고 변경이 필요했다면 영향과 미완료 consumer 의무를 공개한다. B/C가 각자 별도 문장 corpus를 생산하거나 runtime에서 의미를 재합성하지 않게 한다.
- Final 자동 검사와 실제 재독이 가리키는 결과의 digest가 일치한 뒤 종료 기록을 작성한다. 남은 exact-input 소비가 있으면 governance 문서 갱신을 선행하지 않는다.

**Validation:** §7의 final focused validation, final coverage reconciliation, B/C 공통 readback 좌표와 비전환 경계 확인. `DECISIONS`/`ROADMAP`의 완료 표시는 실제 검수 범위로 한정한다.

## 7. Validation Plan

### Automated Validation

전수 의미·언어 검수는 유지하되 자동 검사 범위는 실제 변경에 맞춰 최소화한다. 검증 강도 명칭을 추가 검사 근거로 사용하지 않는다. 현재 문제 정의의 마지막 묶음 검사 원칙을 채택한다. 중간 원문 읽기·재생성·delta 분석은 계속하되 코드 자동 테스트는 final candidate에서 묶는다. 실패 수정 또는 추가 변경으로 기존 검사 근거가 무효화된 경우에만 필요한 검사를 다시 실행한다.

실행 cwd는 `PZ` 루트, shell은 PowerShell이다. 실제 변경에 적용되는 required-validation 계약을 필요한 관련 절만 확인하고, 추가 의무가 있을 때 그 근거와 범위를 실행 기록에 남긴다. 필수 검사가 아래 final 묶음보다 넓거나 더 이른 시점을 요구하면 그 차이를 숨기거나 계획으로 면제하지 않는다. 기존 범위 안에서 수행 가능한 필수 검사는 반영하고, 범위 밖 변경·전환이나 확보할 수 없는 환경을 요구하면 해당 검증 축을 blocked, 전체 작업은 미충족 범위에 따라 partial/blocked로 남긴다. 필수 검증과 실행 범위를 조정하기 전에는 complete를 주장하지 않는다. 과거 명령 목록의 존재만으로 전체 suite를 의무화하지도 않는다.

Phase 1의 입력/코드 확인과 Phase 2/5의 읽기·집계·delta는 검수 작업이며 별도 자동 테스트 Gate가 아니다. 같은 읽기·생성 결과를 공유하고 helper를 검사하기 위한 별도 검사 체계를 만들지 않는다. 코드/생성 계약 변경이 없으면 검수 착수·closeout만을 위한 생성 테스트를 실행하지 않는다. 코드 변경이 있으면 아래 기존 focused 진입점으로 마지막 한 묶음을 수행한다. 아래는 기존 Problem 2에서 사용한 focused 진입점이며 **이번 계획 작성·개정에서는 실행하지 않았다**.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py -q
```

- 기존 테스트의 역할/조건/대안/미확정 fixture, 입력 순서 안정성, 전체 input 직접 대조, 양 locale refs, 실제 detail linkage, producer/input reader를 금지한 저장 readback을 유지한다.
- 기존 검사로 잡히지 않는 의미·조건·조합 회귀의 최소 반례만 같은 focused test에 통합한다. Coverage/delta helper는 일회성 보조 수단이며 별도 test suite나 validator를 만들지 않는다. 추출 누락·비교 오류가 실제 발견되면 원문과 대조해 고치되 validation-of-validation으로 확대하지 않는다.
- Problem 1 코드가 실제 변경되면 위 pytest 명령의 대상 목록에 `Iris/build/description/v2/tests/test_layer3_composition.py`를 함께 추가하여 묶는다. 변경이 없으면 Problem 1 전체 재수락을 요구하지 않는다.
- 일반 어휘·문법·문장 배치 수정만으로 전체 bytes determinism 검사를 추가하지 않는다. 순서·직렬화·비결정성에 영향을 주는 실제 변경 또는 관찰된 문제가 있을 때만 해당 위험에 맞는 최소 확인을 final 묶음에 포함한다. 기존 fixture와 생성 결과를 우선 공유하며 전체 동일 입력 재생성이 필요한 경우에만 비교용 생성을 추가한다. Fixture 순서 검사로 전체 bytes determinism을 주장하지 않는다.
- 새 Python helper의 실행은 `uv run --project .\Iris\tooling python <script>` 형식을 사용하고 실제 명령·cwd·exit·최종 subject를 기록한다. 아직 없는 helper를 이미 실행 가능한 기존 도구로 표시하지 않는다.
- Lua 변경은 기본 범위 밖이다. 별도 범위가 정해져 변경되는 경우 필수 명령은 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`이다. Java/JS 변경 없는 본 작업에 Gradle/Biome 검사를 추가하지 않는다.
- 테스트 실행 중 30~60초 간격으로 프로세스 상태·출력·진행 여부를 확인한다. 무한 반복·진행 정체·비정상 장기 실행 징후가 있으면 해당 프로세스를 중단하고 원인을 기록한다. 시간 초과를 PASS로 처리하거나 원인 확인 없이 자동 재시도하지 않는다.
- 저장소 전체 Run A/B + comparator, historical replay, 변경 없는 문제 1 재수락, 별도 seal/receipt/manifest/proof 검사는 추가하지 않는다. 같은 subject/input/producer/execution boundary의 검사는 기존 실행 결과를 공유하고 Gate마다 디렉터리나 중간 artifact tree를 만들지 않는다.
- FAIL-CLOSED: 관련 정확한 명령의 exit 0만 PASS로 기록한다. 필수 tooling 부재는 BLOCKED, 실행 안 한 검사는 미실행으로 남긴다. 과거 r6/Problem 2 exit 0은 final correction 증거로 승계하지 않는다.

### Manual Validation

- 모든 present surface의 실제 읽기 또는 검토된 표현+item 조합 확인. 양 locale와 양 깊이를 교차 대조한다.
- 모든 absent의 current-input reason 확인. 미검수/근거 부족/정상 부재/생성 결함을 구별한다.
- 변경 및 영향 집합의 실제 재독, 예상 밖 delta 해명, final coverage 결속을 확인한다.
- Independent review를 실제 수행하고 적용 독립성 조건을 만족한 경우에만 그 범위를 주장한다. 동일 계열 작성/파생 검토를 자동 독립 PASS로 계산하지 않는다.
- Correction 후 실제 원문에서 해석·추천·효율·우열 표현의 신규 삽입 여부를 확인하고 Phase 5 evidence에 남긴다.
- PZ runtime/UI 검증은 B/C 후속 범위로 명시한다. 화면 없이 판정 가능한 언어 문제는 본 검수에서 처리한다.

### Validation Limits

PZ font/viewport/UI scale fit, runtime adoption, 실제 B/C 통합, package/install, 멀티플레이·장기 세션·외부 모드 전수 호환성, 전체 Layer 3 fact 재조사를 수행하지 않는다. Offline compact 적합성은 실제 최대 네 줄 충족을 증명하지 않는다. RTC/Publish/freeze/release/Workshop/deployment readiness 및 미수행 독립 검토 PASS를 주장하지 않는다.

외부 reviewer가 필요하면 Codex Reviewer를 사용한다. 독립 reviewer에 의한 별도 acceptance는 본 계획에서 **out_of_scope**로 분류한다. 따라서 독립 검토 미수행만으로 본 계획의 offline 품질 complete를 partial로 낮추지는 않지만, 자체 전수 검수를 독립 검토로 표시하지 않는다. Phase 1에서 확인한 적용 계약이 이 subject에 독립 검토를 필수로 요구하면 해당 축은 **unvalidated_but_in_scope**이며, 이를 충족하기 전에는 전체 complete를 허용하지 않는다. 계획에서 필수 계약의 독립성 조건을 out_of_scope로 재분류하지 않는다.

## 8. Risk Surface Touch

### Authority Surface

**기존 기록에 조건부 영향 있음 / authority transition 없음.** Roadmap의 두 표현을 구분해서 채택한다. Problem 1 bounded correction과 종료 시 DECISIONS/ROADMAP 기록은 기존 권한 관련 기록에 접하지만 source/fact ownership과 L3-05/06, r6 adoption을 이전하지 않는다. Coverage와 defect ledger는 execution evidence다.

### Runtime Behavior Surface

없음. Current Tooltip/Menu, runtime Lua, package/pointer와 표시 정책은 본 문제의 변경 대상이 아니다.

### Compatibility Surface

기존 schema/read_result 유지가 기본이다. B의 r6 S2 공급과 새 compact 결과는 동일 형식이 아니므로 연결 변경은 B/C가 수행한다. 실제 schema/reader 변경 필요 시 자동 적용을 중단하고 영향과 후속 범위를 명시한다.

### Sealed Artifact Surface

기존 sealed/adopted artifact는 보존한다. 비교 candidate와 final 내부 handoff를 r6 adoption이나 current product identity로 승격하지 않는다.

### Public-Facing Output Surface

향후 표시할 offline public text candidate에 영향이 있다. 현재 사용자 화면은 이 계획 실행으로 전환되지 않는다.

## 9. Risk Analysis

### Architecture Risk

- Locale/lexicon이 semantic selection을 소유하거나 결과 저장 모듈의 실제 합성 책임을 놓칠 수 있다. §4/6 owner 기준으로 수정한다. ARCHITECTURE 본문은 §5의 단일 조건에 따라 실제 책임/흐름/소비 계약 변경이 있을 때만, 남은 exact-input 소비가 끝난 뒤 관련 절을 갱신한다. 기존 서술 차이만 있으면 closeout에 공개한다.
- Problem 1 환류가 사실 재판정으로 확대되면 필요한 upstream 작업을 분리한다. 완성된 의미 입력의 광범위 재설계를 본 품질 수정에 숨기지 않는다.

### Runtime Risk

- Offline 품질 complete를 B/C/current 완료로 오인할 수 있다. Final handoff에 현재 소비 경로와 adapter 미적용, physical_fit 미측정을 명시한다.
- 복잡한 compact 문장 결함을 화면 문제로 넘길 수 있다. 문장 자체의 반복·추상 표현·조건 혼란은 Problem 3에서 수습한다.

### Compatibility Risk

- 참고 어휘 모듈 수정이 r6 경로까지 번질 수 있다. 현 composition 모듈의 최소 수정부터 검토하고 shared source 변경 시 전체 영향 owner를 확인한다.
- 과거 exact-input 사고가 재현될 수 있다. 현재 정상 adopted 읽기와 historical 재생성을 구분하고 후자 필요 여부를 확인한 뒤 문서 변경 순서를 정한다. Hash 치환이나 검증 완화로 해결하지 않는다.

### Regression Risk

- 공통 family 수정이 다수 item의 조건/대상 결속을 바꾸거나 unique 조합만 깨뜨릴 수 있다. Actual delta와 rule 영향 집합을 모두 재검토한다.
- 동일 text도 다른 refs/조건에 결속될 수 있다. 문자열 동일성만으로 coverage를 승계하지 않는다.
- 자동 triage·ledger 완성을 실제 언어 수락으로 오인할 수 있다. 실제 읽기 근거와 미검수 disposition을 보존한다.
- 기존 dirty 작업이나 과거 r6 review를 덮어쓸 수 있다. 신규 검수 디렉터리와 시작 상태 대비 diff로 변경 범위를 관리한다.
- 저장 corpus와 현재 producer가 다르면 전수 검수 뒤 사전 dirty 영향 때문에 coverage가 대량 무효화될 수 있다. 원문 검수를 계속하면서 재생성 전에 현재 수정 코드와 입력 차이를 확인한다. Phase 5에서 실제 영향 결과를 검토하며 과거 Problem 1 module identity 부재는 이력 한계로 남긴다. 그 부재만으로 원문 검수를 차단하거나 과거 producer 복원을 요구하지 않는다.

## 10. Rollback Plan

실행 전 보존한 파일 bytes와 변경 목록을 기준으로 이번 작업에서 바꾼 rule 및 생성 결과만 되돌린다. 저장소 전체 reset/clean, 기존 dirty/untracked 삭제, r6 rollback은 사용하지 않는다.

검사 실패 candidate는 실패 원인·digest와 함께 비교 기록으로 남기고 final로 인계하지 않는다. Rules와 descriptions, 조건부 blocks를 서로 일치하는 상태로 복구한다. 생성 JSON을 수기로 고쳐 rollback 성공으로 만들지 않는다.

Governance 변경이 exact-input 소비를 깨뜨렸다면 이번 변경 직전의 정확한 bytes로 해당 변경만 복구하고 새 설명은 별도 closeout에 보존한다. 현재 dirty 문서를 HEAD 버전으로 덮어쓰지 않는다. 복구 후 필요한 정확한 readback 명령이 exit 0일 때만 소비 복구 성공을 기록한다. 이미 발표한 범위를 넘어서는 PASS는 만들지 않는다.

## 11. Governance Constraints

- `Philosophy.md`를 최상위 기준으로 유지한다. Iris는 확인 가능한 근거의 중립적 정보만 설명하며 해석·권장·효율/우열 평가와 상태 변경을 하지 않는다.
- PZ에서 실행되는 Iris는 100% Lua다. 본 작업의 Python은 offline tooling이며 runtime에 생성·재판정 책임을 넣지 않는다.
- Hub & Spoke/SPI 및 Pulse→submod 의존 금지, spoke 간 직접 의존 금지를 유지한다.
- 제작법과 우클릭 행동은 독립·동등 관점이다. Compact 합성으로 어느 한쪽을 하위 체계로 바꾸지 않는다.
- Tooltip Alt/최대 네 줄과 메뉴/툴팁의 동일 사실·다른 깊이 원칙을 유지한다. 실제 physical fit은 B 책임이다.
- 기존 authority ownership과 r6/PASS 이력을 보존한다. 선행 complete를 새로운 품질 판정으로 소급 확대하지 않는다.
- 문서 변경은 최소 additive 기록으로 한다. ARCHITECTURE 본문은 §5의 단일 조건에 따라 실제 책임/흐름/소비 계약 변경이 있을 때만, 남은 exact-input 소비가 끝난 뒤 관련 절을 갱신한다. 종료 사실이나 기존 서술 차이만 기록하는 경우에는 closeout에 공개하고 ARCHITECTURE 본문은 편집하지 않는다.
- 코드 자동 검사는 final 묶음을 기본으로 하고 필수 적용 계약을 우회하지 않는다. 실패·새 변경·새 증거로 정당화된 재검증만 추가한다.
- 새 quality authority/lifecycle을 만들지 않는다. 독립 검토가 없으면 그 제한을 공개한다.

## 12. Expected Closeout State

목표는 **complete — offline corpus quality acceptance 및 B/C common handoff 범위**다. 문제 정의의 Q1~Q3을 한 번의 최종 수락으로 확인한다. 아래 항목은 독립 Gate·별도 승인·산출물 요구가 아니며 같은 검수 기록과 적용되는 final 검사 결과를 공유한다.

| 결과 | 함께 확인할 내용 |
| --- | --- |
| Q1 전체 결과와 실제 검수 범위 | Exact 2,105 items·8,420 states의 최종 분포·변경 이유, 모든 present의 실제 원문 또는 공통 표현+item 조합 검토, 모든 absent의 current-input 근거. 미검수와 생성 결함을 정상 부재로 계산하지 않는다. |
| Q2 결함 수습과 의미·언어 품질 | Role/function/target/result/조건/부정/대안/미확정 관계 및 acquisition 구분, Tooltip 두 번째 한 줄용 compact 개요와 실제 expanded detail, KO/EN 자연스러움·간결성·의미 일치. 해결 가능한 결함을 공통 규칙에서 수정하고 영향 결과를 재검토했으며 in-scope known defect·미확인·미설명 변경이 남지 않는다. 실제 변경에 적용되는 최소 final 검사를 충족한다. |
| Q3 B/C 공통 인계와 한계 | 같은 final corpus의 경로·identity·schema·compact/expanded 소비 좌표와 refs/absence/limitation을 인계한다. r6/current/UI/package/pointer는 전환하지 않으며 physical fit·runtime 통합·release·전체 fact 조사·미수행 독립 검토는 완료로 주장하지 않는다. |

전수 검수나 수습이 덜 끝났으면 **partial**로 기록하고 미검수 키와 open defect를 남긴다. 도구/입력/계약 때문에 필수 검증을 못 하면 해당 축은 **blocked**로 기록한다. 코드 구현과 생성만 끝나도 언어 수락이 없으면 **implemented_only**이며 전체 complete가 아니다. Upstream limitation은 사실보다 강한 표현을 하지 않고 현 composition 결함과 분리해 보존할 때만 허용된다.

완료 시 허용 claim은 “최종 offline description corpus의 exact 2,105개 item·8,420개 state를 회계하고, 최종 corpus의 모든 present surface의 의미·언어·item 조합을 확인했으며, 현 책임의 결함을 공통 규칙에서 수정하고 영향 범위를 다시 검수하여 동일 corpus의 B/C 인계를 준비했다”까지다. Closeout에는 최종 present/absent/failed의 실제 개수를 함께 기재한다. Present 중 일부만 수락 대상으로 좁힌 denominator로 complete를 주장하지 않는다. B/C 제품 적용과 실제 PZ 검증은 별도 후속 작업으로 남는다.
