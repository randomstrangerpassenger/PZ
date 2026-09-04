# Iris Layer 3 semantic results contract

Revision 1 · DVF-L3-03 · 2026-09-04

`Philosophy.md`와 L3-01/02의 결속된 계약을 상속한다. 이 계약은 offline source 조사, 비획득 의미 candidate admission, 질문 결과와 derived application을 정의한다. 제품의 facts/decisions, composer, generation, locale, Menu/Tooltip, runtime과 package는 이 authority의 출력이 아니다.

## Ownership와 채택

C2: L3-02 definition revision `1`과 기존 baseline writer/application을 보존한다. 별도 `Iris/_docs/authority/dvf/layer3_semantic_results/manifest.json`이 corpus, 정의 readpoint, producer, 이 계약, G1 source를 결속한다. `application_inputs`와 results/bindings는 derived application의 직렬화 입력이다. 실제 application은 `semantic_model.consume()` → `investigation.resolve_item()`으로 계산한다. 대용량 application 복제 파일은 만들지 않는다.

Corpus의 `status=candidate`는 생산 시 lifecycle이며 불변 bytes로 유지한다. G1은 명시적인 candidate 소비 mode로 검증한다. Current route의 adopted 연결과 같은 manifest hash를 기재한 `G1_EXIT_CODE=0` closeout이 함께 있어야 adopted loader가 채택된 논리 envelope를 제공한다. 이때 semantic corpus의 내용이나 hash를 바꾸지 않는다. Candidate를 검증 전에 adopted payload로 위장하지 않으며 일반 adopted loader는 이 근거가 없으면 거부한다. Closeout 문자열 검사는 로컬 채택 기록 결속이지 전자서명·보안 경계가 아니다.

## Identity와 정정 (NC1)

`fact_id` 방식은 **content-derived**다. UTF-8 canonical JSON (`ensure_ascii=False`, sorted keys, compact separators, NaN 금지)의 SHA-256에 `fact:`를 붙인다. 해시 입력은 `item_id`, `fact_kind`, `payload`, 존재하는 `context_fact_ref`와 정렬된 `applies_to_fact_refs`다. 따라서 context/dependency 의미가 identity에 포함된다. Timestamp, 호스트, source locator, review, authority/registry revision과 serialization order는 포함되지 않는다. Exact FullType에는 대소문자·공백·Unicode 정규화를 적용하지 않는다.

의미 없는 provenance locator 정정은 fact ID를 유지한다. Semantic payload 또는 관계 정정은 새 ID를 만들며 이전 내용을 조용히 덮어쓰지 않는다. 정정 successor는 이전 readpoint를 보존하고 이전→새 ID replacement와 영향 범위를 기록해야 한다. 이전 ID의 terminal `fact_refs`, partial bindings, context/dependency와 그에 의존하는 fact ID를 무효화하고 재조사·재admission·재결속한다. Payload만 바꾸고 ID/참조/기존 terminal을 승계하면 validator가 거부한다. 이번 최초 corpus에는 prior accepted semantic fact가 없어 replacement record는 없다. 새 의미의 source 근거를 기존 provenance의 문구 변경만으로 만들어서는 안 된다.

Question identity는 `(item_id, axis_id, scope_ref)` 3-tuple이다. `registry_revision`, `authority_ref`, before/after readpoint는 별도 metadata이며 네 번째 component가 아니다. Unchanged key의 contributor union은 유지한다. `retained`, `changed`, `superseded`, `newly_required`, `no_longer_required`는 L3-03의 lineage relation이며 result state가 아니다. Scope 의미가 달라지면 새 scope 또는 명시적 successor가 필요하다. 이번 revision은 raw group/result/repair/base 참여로 기존 scope instance를 추가한다. L3-02 정의를 개정하지 않는다. 이전 key를 삭제하지 않고 baseline/revised membership과 발생 근거를 universe에 보존한다.

## Facts, provenance와 결과

Accepted fact는 bundle-global ID, exact item, kind, `status=accepted`, kind별 payload, provenance refs와 rule admission을 가진다. Accepted는 candidate 내부의 admission 상태이며 authority adopted와 구별한다. Kind별 payload는 다음과 같다.

| Kind | Payload | 관계 |
|---|---|---|
| use_context | activity | 사용자가 이해할 넓은 활동 |
| context_role | role | 같은 item의 accepted use_context를 context_fact_ref로 참조 |
| direct_function | function | 근거가 있는 직접 기능 |
| effect | property, direction | 실제 소비 경로가 확인된 변화 |
| state | state, value | 근거가 있는 상태 |
| condition / constraint | predicate | 같은 item의 non-qualifier에 applies_to_fact_refs |

Nested qualifier·global role·대표 fact·acquisition fact는 이 producer가 만들지 않는다. Scope·진실을 바꾸는 조건은 관계로 보존한다. Native Type, 분류명, field 존재, recipe token, profile label, predecessor prose, Layer 4 표시·관계 수는 단독 admission 근거가 아니다. Scope별 최소 fact 수는 없다. 새로운 token은 corpus의 rule/admission과 원본 provenance가 그 정의·positive 적용 사례·예외·boundary 보존을 함께 소유한다.

Source의 exact path/hash와 raw locator → observation → rule/revision → semantic proposition → fact가 연결된다. 전체 accepted corpus를 검사한다. Index는 검색·역대조 seed이며 raw source를 대신하지 않는다. Source registry에 있는 두 derived JSON을 raw semantic coverage로 세지 않는다. 원본 snapshot과 추가 repository source의 관계는 exact bytes의 합집합이며 정확한 upstream build를 주장하지 않는다.

Result state는 L3-02의 `resolved`, `evidence_backed_not_applicable`, `investigated_unresolved`, `not_investigated`다. 모든 supplied result에는 exact key, compatible revision/authority, 실제 attempt refs와 provenance가 필요하다. Open state의 `fact_refs`는 비어 있어야 한다. `fact_question_bindings`는 `{question_key, fact_ref, authority_ref, registry_revision, contribution}`이며 partial/whole_scope를 구별한다. Partial fact는 open 질문과 공존하며 resolver output으로 소비된다. 하나의 fact는 여러 질문에 기여하고 질문 수 때문에 복제되지 않는다.

Resolved에는 같은 item·허용 kind의 fact refs와 whole-scope 근거가 필요하다. Scoped N/A는 exact key, explicit exclusion predicate, 닫힌 source 범위, scope completeness와 provenance를 요구한다. 현재 native CantEat 배제는 해당 형태의 native eating 채널에만 적용한다. 개봉·가공·다른 직접 행동이나 item-global 기능 부재를 뜻하지 않는다. N/A를 positive fact로 materialize하지 않는다.

Acquisition은 공급하지 않는다. Item 완료식, first-contact obligation과 profile contributor union은 L3-02 그대로다. Expression omission이나 acquisition 미해결로 accepted partial facts를 삭제하지 않는다.

## 조사 범위와 A1

각 target에는 A~E별 performed attempt가 있으며 exact question과 pending profile은 그 attempt를 참조한다. 공통 route source inventory는 한 벌만 보존한다. Native 선언/중복 field, raw Recipe input/keep/destroy/result 및 group 확장, EvolvedRecipe ingredient/base/result, fixing Require/Fixer, moveable tool, 선택 item predicate의 부분 평가와 독립 action literal 역탐색을 구별한다.

Script reader는 문자열·주석·brace, 반복 clause와 declaration을 보존한다. Group 해석은 straight-line tag/type union 및 실제 검토한 fabric/type/name predicate에 한정한다. Inventory loop의 `testItem`만 해당 selected item alias로 치환한다. 각 atom 평가를 전체 boolean branch truth로 오인하지 않는다. Other receiver, live getters, runtime object, action callback 및 engine 구현의 미확정 부분은 symbolic dependency로 남긴다. Lua를 실행하거나 engine을 복제하지 않는다.

`source_interpretations`는 raw recipe별 선언·참여·callback과 공통 consumer 해석, inventory caller→action별 조건·상태 변경·잔여를 연결한다. `callback_readings`의 명시적 검토 집합과 함수 정의 발견 집합은 별개다. 정의가 있어도 검토 집합에 없는 callback은 `defined_but_unreviewed_callbacks` 및 `not_investigated`로 남는다. Action도 명시적 의미 해석이 없으면 미조사다. 이 기록은 작성 중 B1 결과를 같은 corpus에 결속한 것이며 별도 validator나 전체 Lua UI 메서드 감사가 아니다.

Native/recipe 조사에는 raw↔index 역대조, 중복 선언·callback 충돌, recursive replacement의 cycle/누락, multistage construction의 previous-stage·재료·도구·skill 및 활성 construction branch가 포함된다. 우클릭의 generic equip/drop·debug editor·tooltip 생성은 실제 caller를 확인하고 intrinsic function 근거에서 제외한다. UI에서 실제 저장/변경하는 독서·노트·지도·알람·cosmetic 동작과 단순 표시를 혼동하지 않는다. Runtime event registry·receiver·engine의 부족은 구체 handoff에 남기며 정적 source 밖의 조사 완료를 주장하지 않는다.

A1은 결속된 available-source 조사 key와 pending 및 새 key의 단순 미수행 0을 요구한다. 실제 조사했으나 predicate/receiver/loader/source 의미가 확정되지 않은 경우는 performed evidence와 해당 dependency를 갖는 unresolved로 남길 수 있다. 코드 미구현·source 단순 열람을 이런 상태로 숨기면 안 된다. 이 계약은 정적 atom 조사와 전체 action 의미 해석을 동일시하지 않는다. 채택 전 감사에서 미수행으로 확인된 범위는 not_investigated로 환원하고 A1을 실패시킨다.

네 anomaly는 개별 raw 후보·near-name 검색·영향 attempt·재조사 조건을 보존한다. 비슷한 이름을 alias로 정하지 않고, 중복 원본의 loader winner를 선택하지 않는다. Native의 type 배제와 별개로 residual 직접 행동 질문은 남긴다. Pending 집합은 겹침을 유지하고 합산하여 item 완료율을 계산하지 않는다.

## B1과 검증 경계

B1은 unique automatic rule 전체의 precondition/소비 동작/의미 변환/예외 검토와 food/tool/weapon/clothing/multi-use/low-information 및 A~E 표본 감사를 요구한다. Review 기록은 corpus에서 rule/fact/attempt refs에 결속한다. 위험한 interpretation·조건·중복·multi-context는 개별 표본에서 확인한다. 표본 밖 전수 의미 정확성을 주장하지 않는다. 미해결 engine 효과·동적 분기·검토되지 않은 predicate chains는 그 한계를 남긴다.

G1의 public identity는 `test_layer3_semantic_results.Layer3SemanticResultsTest.test_semantic_results_contract` 한 개다. 실제 corpus 전체의 candidate adapter/resolver 소비를 한 번 실행하여 무결성과 집계를 공유한다. 작은 독립 사례에서 identity·reader·관계·결정성·negative·fallback·CLI 경계를 검사한다. Full-process A/B, 별도 validator, runtime/package 실행은 추가하지 않는다.

Adoption 검사는 `IRIS_LAYER3_SEMANTIC_MODE=adoption`, absolute repository-local `IRIS_LAYER3_SEMANTIC_BASELINE`, `IRIS_LAYER3_SEMANTIC_MANIFEST`를 명시한다. Missing/damaged baseline이나 bound input은 fail-closed다. 통상 contract 검사에는 과거 임시 baseline을 요구하지 않는다. 사용한 환경은 실행 후 복원한다. 보호 주장은 baseline의 명시적 33개 파일과 기존 config/product locator에만 한정한다.

Retain: final corpus/manifest, 원본 exact source locator, rule와 audit, anomaly/negative/unresolved attempt, universe/pending와 최종 실행 closeout. Scratch helper와 시작 baseline은 G1 결과/한계를 closeout에 옮긴 후 제거할 수 있으며 새로운 validation authority가 아니다. 후속 L3-04는 acquisition, L3-05는 표현·S2·omission, L3-06은 runtime/product adoption을 담당한다.
