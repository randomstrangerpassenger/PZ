# Implementation Plan

> **제목:** Iris DVF Layer 3 획득 정보의 근거 확보와 독립된 조사 결과 구축  
> **문제 ID:** `DVF-L3-04`  
> **작성일:** 2026-09-04  
> **개정:** 2026-09-04, 사용자 제공 Implementation Plan Review 종합본의 R1~R4 및 NC-01~05 반영  
> **추가 개정:** 추가 검토 NC-05~07 반영; Q/F와 P4의 L3-04 작업 한정 경계 명시  
> **현재 개정:** 획득 사실과 조사 상태의 독립성·resolved 판정 사례 명확화; 공통 조사 증거 재사용; 최종 G1 하나로 검증 통합 및 반복 실행 축소  
> **상태:** 계획 초안 — 코드·current authority 채택을 실행한 문서가 아님  
> **입력:** 사용자 제공 「Iris DVF Layer 3 획득 정보의 근거 확보와 독립된 조사 결과 구축 Roadmap」  
> **양식:** [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md)  
> **기준:** [Philosophy.md](Philosophy.md), [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md), current [DECISIONS.md](DECISIONS.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md), DVF-L3-01/02/03 adopted readpoint

---

## 1. Objective

Exact case-sensitive FullType `2,105`개에 대한 item-global acquisition 질문 `(item_id, acquisition, item)`을 조사하고, current source와 provenance에 결속된 **독립 L3-04 acquisition result authority**를 구축한다. 확인된 획득 사실은 `0..N`으로 보존하며, 조사 상태·사실 존재·획득 축 해결·item 전체 조사 완료를 분리한다.

기존 `investigation.resolve_item()`이 L3-02 정의, L3-03 비획득 결과, L3-04 획득 결과를 함께 소비하게 한다. L3-05에는 raw source를 재조사하지 않고 표현 단계로 넘길 수 있는 structured facts, conditions, provenance, question results, limitations와 adopted readpoint를 제공한다.

완료 범위는 off-live 조사·결과 authority·structured consumption이다. 이 수정본은 **`complete`의 필요조건을 acquisition `not_investigated=0 / 2,105`로 고정**한다. `investigated_unresolved>0`은 허용하지만, 필요한 실제 조사를 수행하지 못한 질문을 unresolved로 바꿔 완료하지 않는다. §4의 조사 coverage admission을 함께 충족해야 하며 상태 집계만으로 전수 조사를 증명하지 않는다. 이 문서 수정은 과거 sealed decision의 재해석이나 L3-04 구현·채택 성공 선언이 아니다.

---

## 2. Scope

- Repository에 존재하는 acquisition source family의 identity, observation 가능 범위, 적용 조건, interpretation 가능 범위와 한계 조사.
- Exact `2,105` acquisition question universe 및 실제 수행 기록에 대응하는 result state 생산.
- Source-bound acquisition fact, fact-local condition/constraint, multi-source provenance, 복수 획득 경로 보존.
- Predecessor acquisition material 전수 census와 source rebinding 여부에 따른 disposition.
- Closed-negative 근거가 성립할 때만 `acquisition_unobtainable` 생산. 정당화되지 않으면 negative `0` 허용.
- L3-03과 별도 corpus/manifest/readpoint, candidate/adopted loader 및 기존 resolver를 사용하는 결합 consumer 추가.
- Task-specific 검증, additive authority 등록, 실제 subject에 결속된 closeout와 L3-05 handoff.

### Explicitly Out Of Scope

- L3-01/02/03 adopted manifest/member, L3-02 definition revision 및 baseline의 덮어쓰기.
- L3-03 비획득 fact 재조사, unresolved 전수 해결, profile taxonomy 재설계.
- Current product corpus, composer, KO/EN public text, Menu/Tooltip, Tooltip static projection, Lua runtime 변경.
- Generation/current pointer, package/install, release/Workshop/deployment 전환.
- Layer 4 개별 Recipe/Right-click relation 및 전체 제작 절차의 Layer 3 복제.
- 기존 문서 삭제 복원, unrelated cleanup, 검증 체계 재설계.

P3의 definition gap은 기존 정의 보존을 기본으로 별도 문제로 분리한다. 정의 확장은 Iris 프로젝트 owner의 명시적 scope/contract 결정과 별도 revision·영향 판정 없이는 수행하지 않으며, 이 계획의 자동 확장 권한으로 해석하지 않는다.

---

## 3. Non-Goals

- 모든 획득 질문을 `resolved`로 만들거나 resolved 비율을 품질 목표로 삼지 않는다.
- Source miss, 빈 positive fact 집합, 미확인 declaration을 획득 불가로 해석하지 않는다.
- 한 경로 발견만으로 나머지 applicable source 조사를 종료하거나 대표 경로를 선택하지 않는다.
- 기존 문장을 재사용하는 것으로 successor truth를 확보하지 않는다.
- 전체 PZ acquisition universe, engine/runtime 경로 또는 외부 모드의 완전성을 증명하지 않는다.
- 획득 축 해결을 item 전체 조사 완료, Menu 상세 완성, Tooltip S2 완성으로 확대하지 않는다.
- 획득 확률·효율·추천 장소·아이템 우열을 생산하지 않는다. Raw weight/roll 값을 실제 출현 확률로 바꾸지 않는다.
- L3-03 미해결, 과거 audit 재현, 임시 파일 정리를 조사 시작의 새 gate로 만들지 않는다.

---

## 4. Assumptions

### 확인한 repository 상태

아래는 2026-09-04 working tree의 코드·JSON 열람 및 읽기 전용 집계 결과다. 과거 G1 성공은 기존 closeout의 기록이며, 이번 계획 작성에서 재실행한 결과가 아니다.

| 항목 | 확인 결과 | 근거 |
|---|---|---|
| Exact target | `2,105`, set SHA-256 `122ca07c483ff8e4af9ef83bfb8d28c950802a124aba1668c234bce3477b2fdb` | `layer3_investigation/manifest.json`, `investigation.targets()` |
| L3-02 정의 | revision `1`, acquisition scope `item`, N/A 금지 | `layer3_investigation/contract.json` |
| L3-03 결과 | source binding `216`, fact `4,233`, non-acquisition question `9,982` | `layer3_semantic_results/corpus.json` 직접 집계 |
| L3-03 질문 상태 | unresolved `9,900`, scoped N/A `82` | 동일 corpus 직접 집계 |
| 다른 분모 | partial fact 기여 question `3,498`, pending item/profile pair `5,767` | L3-03 manifest/closeout; pending 길이 직접 확인 |
| 현재 획득/완료 | acquisition `not_investigated=2,105`, item complete `0` | L3-03 manifest/closeout 및 획득 결과를 공급하지 않는 producer/model |
| Predecessor 후보 | 비어 있지 않은 `acquisition_hint` `1,105`행, Book 계열 `body_material.source_slots.acquisition_hint` `55`행 | `dvf_3_3_facts.jsonl` 직접 집계 |
| 채택 경로 | L3-01/02/03 모두 route에 `adopted`; L3-04 entry 없음 | `Iris/_docs/authority/iris_current_route_index.json` |

`216`, `4,233`, `9,982`, `5,767`은 acquisition source 전수 또는 acquisition 진행률 분모가 아니다. Hint 보유 exact item 집합을 H, Book acquisition source-slot 보유 exact item 집합을 B라 하면, 수정 시 직접 집계한 결과는 `|H|=1,105`, `|B|=55`, `|H∩B|=55`, `|H−B|=1,050`, `|B−H|=0`, `|H∪B|=1,105`다. 즉 **B는 H의 부분집합**이다. 이는 item 집합 관계이며 서로 다른 material record 55개를 삭제하거나 두 수를 더해 item 수로 사용하는 근거가 아니다. §6 Change 3에서 material-kind별 분모와 exact item 합집합을 따로 관리한다.

### 코드가 제공하는 접점과 제약

| 기존 접점 | 실제 동작 | 계획에 반영할 사항 |
|---|---|---|
| `investigation.targets()` | facts/decisions의 exact ID 집합 일치 확인 | 별도 이름 정규화 target 생성 금지 |
| `investigation.resolve_item()` | global acquisition을 한 번 생성하고 복수 authority/result/contribution 입력 수용 | 새 조사 엔진 대신 기존 함수 재사용 |
| `investigation.terminal_result()` | open state의 terminal `fact_refs` 금지, resolved fact/provenance와 negative evidence 검사 | partial fact는 별도 `fact_question_bindings`에 보존 |
| `investigation.load_result_authorities()` | L3-03 manifest의 특수 경로 및 generic adopted payload 로딩 | 새 manifest를 기존 함수가 자동 인식한다고 가정하지 않음 |
| `semantic_model.validate_payload()` | non-acquisition kind만 허용하고 acquisition universe 명시 배제 | 획득 corpus를 L3-03 validator에 밀어 넣지 않음 |
| `semantic_model.consume()` | 한 payload/authority를 resolve_item에 전달 | 결합 orchestration을 별도 모듈에 추가 |
| `semantic_model.fact_identity()` | item/kind/payload/dependency 기반 ID, locator·review metadata 제외 | 동일 identity 규율 재사용; provenance 다중성 별도 보존 |
| `semantic_results.load_manifest()` | member/source hash, definition, adopted route와 exact 성공 closeout 확인 | 기존 L3-03 loader를 그대로 사용하여 readpoint 검증 |
| `layer3/cli.py` | 알려지지 않은 argument는 composer로 fallback | 획득 명령이 기존 fallback에 도달하지 않게 별도 entrypoint 사용 |

중요한 구현 제약: L3-03 manifest는 corpus뿐 아니라 `investigation.py`, `semantic_model.py`, `source_reader.py`, `interpretations.py`, `semantic_results.py`, `cli.py`와 focused test까지 member hash로 결속한다. 해당 파일을 수정하면 `load_manifest()`의 `semantic member drift` 검사가 실패한다. 따라서 **기존 파일을 import하는 새 모듈**을 기본 구현으로 삼는다. 기존 CLI에 subcommand를 추가하는 작은 변경도 자동 허용하지 않는다.

Known uncertainty 네 항목은 target에 유지한다: `Base.Bag_PistolCase`, `Base.Lemongrass`, `Base.NoiseMaker`, `Base.ShotgunCase1`. 앞의 세 항목의 exact declaration 부재와 마지막 항목의 duplicate declaration/loader winner 미확정은 L3-03의 기록이다. 새로운 acquisition evidence와 재대조하되 alias 치환·임의 winner·자동 negative를 적용하지 않는다.

### 완료 조건·상태 규칙과 판정 책임 — R1/R2/R4

여기서 **owner는 작업을 요청한 사용자인 Iris 프로젝트 owner**다. 별도의 외부 reviewer를 필수 owner로 신설하지 않는다. Execution actor는 근거 수집·정해진 규칙의 적용·검증·판정안 작성을 담당하며, 완료 의미 완화·정의 확장·채택 후 복구 정책을 독자적으로 선택할 권한을 갖지 않는다. 기존 세션에서 명시된 owner 승인은 그 범위 안에서 유효하며 같은 승인을 반복해서 요구하지 않는다.

| 기존 ID / 현재 성격 | 수정본의 규칙 | 책임 주체와 lifecycle point |
|---|---|---|
| P1 → 고정 완료 조건 | `complete`이면 `not_investigated=0 / 2,105`. 미수행을 남기는 complete 선택지 제거; unresolved 잔존 허용 | 계획 규칙의 owner는 사용자. Execution actor와 focused test는 Phase 4 종료·최종 closeout에서 이 조건을 평가하며 완화 선택을 하지 않음 |
| P2 → unobservable-source disposition rule | 필요한 실제 조사를 못 했으면 not_investigated 및 complete 불가. 조사를 수행했으나 승인 가능한 positive/negative 답변을 확보하지 못하면 unresolved. 확정 경로와 무관한 추가 경로의 불확실성만으로 resolved를 막지 않음 | Execution actor가 아래 coverage admission·해결 판정표에 따라 item별 적용. 새로운 의미/예외만 owner에게 구체적 사례로 제시 |
| P3 → 조건부 definition owner 결정 | Current revision 1과 baseline 보존. Gap 영향 결과를 보류하고 별도 contract 문제로 분리 | Gap 발생 시 execution actor가 영향·대안을 정리. Owner가 정의 확장/범위 변경 여부를 결정해야 그 변경을 시작할 수 있음. 영향 없는 조사는 진행 가능 |
| P4 → 계획에 포함된 복구 정책 | §10의 결함 route 철회·새 correction subject 검증·sealed history 보존을 기본 복구안으로 고정 | 후속 실행 승인에 이 복구안과 위임 범위를 함께 포함할 수 있으며 이미 승인된 범위는 재승인하지 않음. 기본안 밖 조치가 필요한 경우에만 추가 결정 |

**검토안 간 차이의 처리:** 종합본 C1은 과거 P1의 성격에 관해 결론을 내리지 않았다. 이 수정본은 이를 과거 authority에서 이미 결정된 사실이라고 소급 주장하지 않고, 수정 계획의 완료 조건으로 명시한다. P1/P2를 실행 중 A/B 선택으로 남기지 않으면서 owner와 실행자의 책임을 구별한다. C2에 대해서는 R2의 item×family coverage admission을 구체적인 증거 요건으로 추가한다. 이는 두 검토가 원래 동의했다거나 수정본이 독립 review PASS를 받았다는 뜻이 아니다.

**진행 가능 범위:** 이 요청은 계획 수정이다. 후속 구현이 허용되면 source census·observation·predecessor inventory 및 아래 규칙에 따른 조사/후보 생산은 진행할 수 있다. Coverage가 불충분하면 Phase 4 전수 조사 종료와 complete를 선언할 수 없다. P3 gap에 필요한 owner 결정 없이 정의를 확장할 수 없고, P4 복구 정책과 필요한 실행/adoption 권한이 없으면 current adoption은 진행하지 않는다. 완성된 증거·영향·대안을 먼저 마련하며 불필요한 중간 승인 절차를 만들지 않는다.

### 획득 사실·조사 상태·해결 판정의 관계

- 이 후속 계획이 선택하는 의미는 **불확실한 상태 자체로 fact를 생성하지 않되, 독립된 증거로 확정한 개별 획득 사실과 조사 상태는 분리한다**는 것이다. Partial은 질문에 대한 기여 범위를 뜻하며, 추측이 섞인 사실을 accepted로 낮춰 승인하는 등급이 아니다. 해당 경로의 진실성에 필요한 조건까지 확인한 사실만 accepted가 된다.
- 기존 `docs/iris_dvf_layer3_multi_meaning_information_resolution_successor_contract.md` §7에는 open state가 “acquisition fact를 만들지 않으며”라고 되어 있다. Machine contract의 `unknown_state_creates_semantic_fact=false`와 기존 resolver의 partial contribution 수용만으로 이 문구의 해석이 자동 확정된다고 주장하지 않는다. 신규 L3-04 human contract에 원문과 이 후속 명확화의 차이·적용 범위를 함께 기록하여 **open state 자체의 fact 생성 금지와 별도 증거 기반 fact 보존 허용**을 명시한다. 이번 계획 수정은 그 계약의 실제 채택이나 과거 sealed 의미의 소급 변경이 아니다.
- 이 명확화는 L3-04의 독립 결과에만 적용하며 기존 sealed member를 수정하지 않는 additive 방식을 사용한다. 실제 적용에 기존 sealed 계약/revision 변경이 필요하다고 확인되면 P3로 해당 충돌·최소 변경 범위만 분리한다. 테스트 통과나 임의 재해시로 의미 결정을 대신하지 않으며 영향 없는 조사는 계속한다.
- `whole_scope`는 아래 조사 수행 조건과 기존 획득 질문의 답변 충족 조건을 함께 충족한다는 뜻이다. 알려지지 않은 모든 게임 경로의 전수 확정이나 모든 family에서 positive를 얻었다는 뜻이 아니다. 결과에는 조사 범위, 승인한 답변의 근거, 미확인 추가 경로와 해당 사실 자체를 위협하는 한계를 구별하여 기록한다.

| 실제 상황 | 개별 사실과 획득 질문의 처리 |
|---|---|
| 필수 family 조사가 하나라도 미수행 | `not_investigated`; 이미 독립적으로 확정한 사실은 별도 partial binding으로 보존하되 전수 조사 완료나 resolved로 승격하지 않음 |
| 필수 조사를 모두 수행했고, 조건까지 확인한 획득 경로가 하나 이상 있음 | `resolved`; 확인한 모든 경로를 보존. 무관한 추가 경로의 존재 여부·엔진 한계는 limitation으로 남기며 이것만으로 해결을 막지 않음 |
| 특정 상점 선반의 생성 연결은 확정됐으나 다른 동적 생성 경로는 해석 불가 | 위 resolved 사례에 해당. 확정된 상점 경로를 지우거나 모든 획득 경로가 밝혀졌다고 확대하지 않음 |
| 이름/분포 token은 발견했으나 그 경로의 실제 생성 연결 또는 필수 조건이 미확정 | 그 경로는 observation/lead로 유지. 필수 조사를 실제 수행했고 다른 확정 경로나 정당한 negative도 없으면 `investigated_unresolved` |
| 필수 조사를 모두 수행했으나 positive도 정당한 negative도 없음 | `investigated_unresolved`; 검색 miss는 획득 불가가 아님 |
| Item-global 질문을 지지하는 정당한 closed-negative가 있고 positive 모순이 없음 | 기존 negative admission과 필수 조사 수행 조건을 충족할 때만 `resolved` |

대상 identity나 필수 조건의 모순이 특정 경로의 진실성을 무너뜨리면 그 경로의 fact admission을 보류한다. 다른 독립적으로 확정된 경로가 있으면 별도로 판정한다. Fact와 open state의 독립성을 이유로 위 resolved 조건을 충족한 질문을 임의로 unresolved에 고정하지도 않는다. 획득 축의 resolved는 item 전체 완료를 뜻하지 않는다.

### Investigation coverage admission — 상태 label보다 먼저 검사

- Phase 1의 여섯 acquisition source family를 **전체 target 공통 조사 family 집합 F**의 출발점으로 삼는다. Phase 1 종료 시 exact family ID, family별 bound source member 집합, 관찰 방법과 필요 consumer 연결, known gap을 inventory revision/hash에 결속한다. Item 이름·분류·검색 miss로 family를 사후 제외하지 않는다.
- Required coverage 좌변은 `Q = exact_target_set × F`다. 최종 census에 추가 family/source가 발견되면 그 revision과 영향 pair를 기록하고 재조사한다. 이미 수행한 pair가 빠지도록 F를 축소하거나 결과에 맞춰 분모를 재작성하지 않는다. F의 closure는 이 작업의 bounded 조사 범위이며 게임 전체 source completeness가 아니다.
- Q/F는 이 작업의 실제 전수 조사를 증명하기 위한 **L3-04 한정 bounded execution inventory**다. 기존 authority가 요구하는 의미 taxonomy 또는 다른 Iris 작업의 공통 조사 의무로 승격하지 않는다.
- 공통 source 해석·consumer 연결·일괄 탐색 결과는 한 번 조사하여 여러 item/family pair가 참조할 수 있다. Q는 개별 추적 의무이지 동일 파일의 2,105회 재열람이나 증거 본문의 중복 저장 의무가 아니다. 공유 evidence에는 실제 입력 identity·탐색 범위·방법·해석 규칙을, pair에는 exact item의 발견/부재·예외·조건 연결을 남긴다. 증거 참조를 재사용하되 item별 검사를 수행하지 않은 공통 label로 대체하지 않는다.
- 각 `(item_id, family_id)`에는 outcome과 실제 수행한 attempt의 참조를 기록한다. Phase 2 result contract는 outcome 허용값을 **`found`, `not_found`, `access_failure`, `interpretation_unresolved`, `not_attempted` 다섯 값으로 닫는다.** 이는 family 조사 결과이며 acquisition question state나 새 N/A axis가 아니다. 여러 attempt/outcome을 보존할 수 있지만 최종 coverage disposition은 pair당 하나로 정리한다.

| Coverage outcome | 조사 충족/미충족 대응 | 필수 근거와 제한 |
|---|---|---|
| `found` | 필요한 실제 조사 evidence가 모두 확인되면 충족 | 발견 사실만으로 family 전체 조사 완료를 뜻하지 않음; 필수 source-member 범위·consumer 추적까지 검사 |
| `not_found` | 필요한 실제 조사 evidence가 모두 확인되면 충족 | Bound 범위를 실제 조사한 miss; negative fact 또는 game-wide absence가 아님 |
| `interpretation_unresolved` | 필요한 실제 조사 evidence가 모두 확인되면 충족 | 관찰·가능한 해석/consumer 추적은 수행했으나 의미·engine 경계가 남음. 이 family outcome 하나로 item의 resolved 여부를 결정하지 않고 위 판정표를 적용 |
| `access_failure` | 미충족 | 실패 대상과 실제 접근 시도 기록; 필수 관찰을 대신하지 못함 |
| `not_attempted` | 미충족 | 미수행 사유 기록; 존재하지 않는 attempt/provenance 생성 금지 |

- 앞의 세 값도 필수 evidence가 부족하면 admission을 거부한다. Unknown outcome, 충족/미충족 대응이 없는 outcome 또는 대응표와 다른 판정을 V2가 거부한다. 어휘를 추가해야 하면 Phase 2 result contract의 명시적 개정으로 대응 분류·evidence 요건·검사를 함께 정의하며, 개정 전 값은 허용하지 않는다.
- Attempt는 source path/hash 또는 접근 실패 대상 identity, 조사한 locator/query와 방법, 관찰 범위, finding, 필요한 consumer/조건 추적 여부, 남은 dependency를 포함한다. Family에 여러 필수 source member가 있으면 그 적용 범위와 수행/미수행도 대조한다. 임의 한 파일의 token 검색이나 이름만 채운 공통 record로 family 전체를 조사했다고 처리하지 않는다.
- `found`/`not_found`는 정해진 관찰 범위를 실제 검사했다는 근거가 있어야 한다. `not_found`는 그 bound source 범위의 검색 결과이며 negative fact가 아니다. `interpretation_unresolved`는 필요한 관찰 및 가능한 해석·consumer 추적을 수행했지만 의미/engine 경계가 남았다는 근거가 있어야 한다.
- `access_failure`는 접근을 시도했다는 증거일 뿐 조사 완료 증거가 아니다. 필수 관찰을 못 했다면 해당 pair는 미수행으로 남는다. 다른 source로 같은 필요 관찰 범위를 충족했다면 동등 범위와 evidence를 명시하고, 최종 pair outcome은 그 실제 조사 결과에 따라 앞의 세 충족 가능 값 중 하나로 기록한다. 이전 접근 실패 attempt는 보존하되 `access_failure` 자체를 충족으로 분류하지 않는다.
- Item에 `resolved` 또는 `investigated_unresolved`를 부여하려면 그 item의 **모든 required family pair가 존재하고, 필요한 실제 조사 수행이 evidence로 확인**되어야 한다. 그 다음에 fact/whole-scope/negative 요건으로 resolved 여부를 판정한다. 하나라도 실제 미수행이면 item acquisition은 `not_investigated`이며 이미 확보한 partial facts는 별도 binding으로 보존한다.
- V2는 좌변 Q와 결과 pair의 exact equality, source member coverage, attempt/evidence binding, outcome의 admission, question state와의 대응을 검사한다. `not_investigated=0` count만으로 이를 대신하지 않는다. Corpus validator의 이 조건을 통과하기 전에는 resolver 입력을 accepted/adopted 조사 결과로 사용하지 않는다.

### Required-validation 등록 표면의 근거 — R3

신규 required identity를 등록할 current surface는 **`Iris/validation/execution/required_validations.json`**이다. 이는 실행 코드만 보고 상위 결정을 덮어쓴 선택이 아니다. 다음 superseding decision과 current readpoint가 일치한다.

| 근거 위치 | 확인한 역할 |
|---|---|
| `docs/DECISIONS.md`, 「Iris current naming — responsibility-based source locator successor」, 2026-08-30 (수정 시 L2436~2448) | 첫 naming 결정은 `_docs/round3/current_route_required_validations.json`을 historical baseline으로 두고 `validation/current_route/`로 이동. 같은 절의 **2026-08-30 사용자 정정 반영**은 그 중간 경로도 predecessor로 두고 `validation/execution/required_validations.json`을 현재 필수 목록으로 명시 |
| `Iris/_docs/authority/iris_current_authority_manifest.json`, `entries`의 해당 exact path records | execution registry는 `current`; `_docs/round3/current_route_required_validations.json`은 `historical` 및 original bytes 보존 |
| `Iris/_docs/authority/iris_current_route_index.json`, `routes.validator` | execution registry를 현재 validation readpoint로 연결 |
| `Iris/validation/execution/run_required_contract_tests.py`, `DEFAULT_REQUIRED_VALIDATIONS`; `run_repository_tests.py`, `REQUIRED_MANIFEST_PATH` | 두 current consumer 모두 execution registry를 읽음 |

검토안이 지적한 DECISIONS의 이전 `current_route_required_validations.json` 기술(L1616/L1621/L1836/L1939)은 위 후속 naming/정정 전 locator의 기록으로 읽는다. 과거 내용을 삭제하거나 historical registry에도 신규 identity를 이중 등록하지 않는다. 삭제 상태인 naming closeout의 복원은 이 판정의 전제조건이 아니다. 현존 DECISIONS의 exact 후속 기록·machine authority·실제 reader로 확인했다.

수정 시 열람한 evidence identity(SHA-256)는 다음과 같다. 이는 근거 snapshot 식별이며 새 봉인/영구 validation gate가 아니다. 실행 시에는 current 의미와 등록 경로가 여전히 일치하는지 관련 부분을 재확인한다.

| 근거 파일 | SHA-256 |
|---|---|
| `docs/DECISIONS.md` | `d089ce109873b9accfa9c266ae7a63e5b8953ea8e9235030f97c152cecc4644f` |
| `Iris/_docs/authority/iris_current_authority_manifest.json` | `bb45d258d930b7cba4eeb67a23bf9706895b5e7e81eed4f22d7c39e23960b4b3` |
| `Iris/_docs/authority/iris_current_route_index.json` | `757f72bcc8ad4d6f9a71b91f085315b82c7656947ed8fba4624a09a23729c092` |
| `Iris/validation/execution/run_required_contract_tests.py` | `097933ea8ae8f387168558b7de09774be042d4fe1a52d2750e3890f9624cad04` |

### Source-classification 등록 표면의 근거 — 추가 NC-07

`Iris/_docs/round3/round3_pytest_source_classification.json`은 **현재 pytest discovery가 소비하는 source 분류 policy**다. 신규 L3-04 test source는 이 policy에 분류하고, required test identity는 위 execution registry에 별도로 등록한다. Source 분류만으로 required-current test membership이 생기지 않는다.

| 확인 대상 | 수정 시 확인 결과 |
|---|---|
| `docs/DECISIONS.md`, 같은 naming successor 절의 2026-08-30 결정(수정 시 L2440) | Required registry의 이전을 명시하면서 taxonomy/closure/**source-policy의 역사적 경로와 schema version은 유지**한다고 기록. 뒤의 설정 이동 정정을 모든 `_docs/round3/` 파일의 일괄 historical 전환으로 해석하지 않음 |
| `Iris/_docs/authority/iris_current_authority_manifest.json` | 이 source-policy 파일의 exact `current`/`historical` entry는 없음. 이전 required registry와 closure의 historical entry가 이 파일의 분류를 대신하지 않음. 개별 current entry가 있다고 주장하지 않음 |
| `Iris/_docs/authority/iris_current_route_index.json` | Source-policy의 직접 entry는 없음. `routes.validator`는 current 실행 경로를 가리키고 `historical_opt_in.blanket_round3_exclusion=false`; 경로 prefix만으로 historical 판정하지 않음. 이 값만으로 개별 파일의 current 지위를 확정하지도 않음 |
| `Iris/build/description/v2/tests/conftest.py` | `SOURCE_POLICY_PATH`가 이 파일을 지정. `_source_policy_payload()`가 실제 파일을 읽고 schema와 owner approval을 검사하며 `_source_policy()`가 분류를 소비. 일반 pytest discovery policy와 exact required-test authority를 명시적으로 분리 |
| Source-policy 본문 | `schema_version=round3-pytest-source-classification-v1`; `policy`는 general pytest source discovery만 담당하며 exact current authority를 확장하지 않는다고 명시 |

따라서 이 경로는 유지된 source-policy 경로와 실제 reader에 근거한 **활성 discovery 설정의 등록 위치**로 사용한다. R3의 required registry와 같은 독립 current-authority entry가 있다는 주장은 하지 않는다. 기존 owner approval metadata는 과거 범위의 기록이며 신규 L3-04 등록에 대한 권한은 해당 실행에서 실제 주어진 권한에 결속한다.

등록 직전에 위 결정·manifest/route·reader와 source-policy 역할을 관련 범위에서 재확인하고 결과를 기록한다. Reader 경로 변경이나 authority 충돌이 발견되면 과거 위치에 임의 등록하지 않고 해당 registration만 보류하여 실제 소비 경로와 상위 결정을 대조한다. 이를 source 조사 전체의 새 prerequisite gate로 만들지 않는다.

| 추가 근거 파일 | SHA-256 |
|---|---|
| `Iris/_docs/round3/round3_pytest_source_classification.json` | `8ff7469c815c143691660300ce466e89a2a8f61963db07df6f18e442251823eb` |
| `Iris/build/description/v2/tests/conftest.py` | `c7de667f202e8740d087cb6434b57c5b593b5a69d0525fd8dc5df6f4be62737a` |

### 환경과 기준선

- PZ 내 Iris 실행은 100% Lua로 유지한다. Python은 이미 존재하는 `Iris/tooling` 오프라인 작업에만 사용한다.
- `Iris/tooling/pyproject.toml`은 Python `>=3.12`, dev pytest `9.0.3`을 명시한다. 실행은 PowerShell과 `uv run ... python`을 사용한다.
- Repository `scripts/`, `lua/`는 조사 가능한 로컬 source snapshot이다. 파일 존재·hash만으로 설치된 게임 build/version, loader applicability 또는 전체 source completeness를 보증하지 않는다.
- 작성 시작 시 다수 기존 `docs/*.md`가 삭제 상태였다. 이를 되돌리지 않는다. 실행 기준선은 HEAD뿐 아니라 실제 working tree와 보호 경로 집합으로 기록하며, 이미 없는 historical 문서를 복원하는 작업을 L3-04 gate로 추가하지 않는다.

---

## 5. Repository Areas Affected

아래 신규 경로는 **제안 경로**다. 이번 문서 작성에서는 계획서 한 파일만 추가한다. 실행 시 신규 파일 수는 논리 책임에 맞춰 최소화하되 확정 경로를 contract와 manifest에 기록한다.

### Code

- 신규 `Iris/tooling/src/iris_tooling/domains/layer3/acquisition_sources.py`: acquisition source 관찰 및 명시적 interpretation.
- 신규 `Iris/tooling/src/iris_tooling/domains/layer3/acquisition_results.py`: fact/result 모델, 전수 producer, authority loader, 독립 모듈 entrypoint.
- 신규 `Iris/tooling/src/iris_tooling/domains/layer3/acquisition_consumption.py`: L3-03/L3-04 독립 입력 검증 후 기존 `resolve_item()` 호출.
- 신규 `Iris/build/description/v2/tests/test_layer3_acquisition_results.py`: L3-04 focused contract/consumption test.
- 읽기 전용 재사용: `investigation.py`, `semantic_model.py`, `semantic_results.py`, `source_reader.py`.
- 원본 조사 입력: repository `scripts/`, `lua/`; product predecessor facts/decisions와 current product locator가 가리키는 구조화 corpus.

### Docs

- 현재 작성: `docs/iris_dvf_layer3_acquisition_evidence_independent_results_plan.md`.
- 실행 시 신규: `docs/iris_dvf_layer3_acquisition_evidence_independent_results_contract.md`.
- 실행 시 신규: `docs/iris_dvf_layer3_acquisition_evidence_independent_results_closeout.md`.
- 실제 채택 후 관련 섹션만 additive 갱신: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`.

### Config

- `Iris/_docs/authority/iris_current_route_index.json`: 독립 `layer3_acquisition_results` entry 제안. 기존 entry/product locator 보존.
- `Iris/_docs/authority/iris_current_authority_manifest.json`: 신규 readpoint의 authority 분류·보호 정책 등록.
- `Iris/validation/execution/required_validations.json`: 신규 required test identity 등록.
- `Iris/_docs/round3/round3_pytest_source_classification.json`: §4 추가 NC-07의 유지된 source-policy 경로·실제 pytest reader 근거와 등록 직전 재확인에 따라 신규 test source 분류 등록. Required membership은 execution registry와 별도로 결속.
- Historical `Iris/_docs/round3/current_route_required_validations.json`은 current registry가 아니므로 수정하지 않는다. Current/historical 판정은 §4 R3의 exact naming successor 결정·readpoint·consumer에 결속한다.

### Generated Artifacts

- 신규 후보 작업 위치: repository 내부 `.tmp/acquisition/<attempt>/`.
- 신규 authority 위치: `Iris/_docs/authority/dvf/layer3_acquisition_results/manifest.json`, `corpus.json` 제안.
- Corpus 안에 source inventory/observations/interpretations, facts/provenance, results/attempts/limitations, predecessor disposition, 필요한 negative evidence를 논리적으로 보존한다. 파일 분할 자체를 gate로 만들지 않는다.
- 결합 application은 원칙적으로 입력 readpoint에서 계산한다. 진단용 출력이 있어도 별도 truth authority나 item completion writer로 만들지 않는다.
- 기존 generation, rendered output, Lua chunk, tooltip projection, package 산출물은 생성·교체하지 않는다.

---

## 6. Planned Changes

### Change 1 — Phase 1: Acquisition Source Domain Census

**Purpose:** 어떤 source가 어떤 acquisition claim까지 뒷받침하는지 먼저 확정한다.

**Files:** 신규 `acquisition_sources.py`, acquisition candidate inventory; 아래 원본은 읽기 전용.

**Implementation Notes:**

| 조사 family | 확인한 입력 위치 | 조사해야 할 의미 연결 및 한계 |
|---|---|---|
| Loot/container/procedural | `lua/server/Items/ProceduralDistributions.lua`, `Distributions.lua`, `SuburbsDistributions.lua` | exact item token → distribution → room/container 참조; rolls/weight/force 조건, loader 적용 경로 |
| Vehicle loot | `lua/server/Vehicles/VehicleDistributions.lua`, 관련 vehicle script | distribution 별칭·차량 선택·container 연결 및 조건; 이름만으로 실제 차량 의미 확정 금지 |
| Foraging | `lua/shared/Foraging/forageDefinitions.lua`, `forageSystem.lua`, `lua/server/Foraging/forageServer.lua`, client Foraging 코드 | item 생성 연결, zone/season/skill 조건, 동적 등록·runtime 상태 의존 |
| Fishing/trapping | `lua/shared/Fishing/fishing_properties.lua`, client Fishing timed actions, `lua/server/Traps/trappingCommands.lua` | 정의와 실제 결과 생성 consumer 연결; 추가 참조 source는 census에서 확장 |
| Stash 및 기타 동적 생성 | `lua/shared/StashDescriptions/`, 원본에서 추적되는 생성 caller | 조건부 경로와 engine boundary; debug/test 생성은 일반 획득 경로와 구분 |
| 제작·분해·변환 | `scripts/*.txt`, 원본 Recipe callback, item 변환/소모/결과 생성 consumer | exact 결과 identity와 조건; L4 index는 discovery lead, 출력 문자열·relation count는 근거 아님 |

- 각 family에 path/hash, 확인 가능한 version/build 근거, access/observation 상태, applicability, evidence capability, known gap, interpretation 필요성, closed-negative 가능 여부를 기록한다.
- §4의 공통 family 집합 F와 `Q=2,105 targets × F`를 명시적 조사 obligation으로 생산한다. Family별 source members와 필요한 관찰/consumer 추적 범위를 정하고, required pair 누락 또는 결과에 맞춘 family 제외를 허용하지 않는다. Source inventory revision은 이후 pair별 outcome과 state admission의 입력이다.
- L3-03의 `216` binding은 발견용 참고다. Acquisition에 실제 필요한 source만 applicability를 재확인하고 새 authority에 직접 결속한다.
- `BookTrapping1`은 `ProceduralDistributions.lua`의 `BookstoreBooks` 등 여러 목록에서 발견되고, `Distributions.lua`는 `bookstore.shelves.procList`에서 해당 목록을 참조한다. 이 연결은 조사 출발점이지 지역 전체에서의 확정 출현·확률 보증이 아니다.
- Unqualified `BookTrapping1` token을 `Base.BookTrapping1`로 바꾸는 데도 원본 namespace/lookup 규칙의 근거가 필요하다. 무조건 `Base.`를 붙이거나 case-fold join하지 않는다.
- 임의 Lua 실행으로 source의 side effect를 재현하지 않는다. 정적으로 이해 가능한 선언/참조만 해석하고 opaque callback, table mutation, loader order는 limitation으로 남긴다.

**Validation:** source별 관찰 범위·한계·claim capability와 F/source-member obligation이 빠짐없이 존재하고, 경로·hash가 재현 가능해야 한다. Q는 target×F에서 독립적으로 계산되어야 한다. Snapshot 조사 범위와 전체 게임 universe를 구별한다. 파일 접근 가능성을 전수 의미 조사 완료로 계산하지 않는다.

---

### Change 2 — Phase 2: Source Interpretation / Provenance and Result Contract

**Purpose:** 관찰·의미 판정·fact·조사 상태의 연결을 기존 L3-01/02 계약 안에서 실현한다.

**Files:** 신규 `acquisition_sources.py`, `acquisition_results.py`, L3-04 human contract와 candidate corpus.

**Implementation Notes:**

1. `investigation.targets()`와 L3-02 readpoint로 exact universe를 결정한다. 각 target에 acquisition key 하나만 만들고 expected set와 exact equality를 확인한다.
2. Observation은 item, source identity/hash, locator, source role, raw token/value, source-local meaning, acquisition meaning, condition/constraint, limitation과 interpretation rule을 연결한다. Source가 없는 의미부터 생성하고 provenance를 사후 부착하지 않는다.
3. Accepted `acquisition` fact의 payload에는 확인된 경로와 그 경로의 진실성에 필요한 조건을 보존한다. Raw token만 있는 observation은 조사 단서에 남기고 의미가 확인되기 전 accepted fact로 승격하지 않는다.
4. Acquisition 질문의 `allowed_result_kinds`는 `acquisition`, `acquisition_unobtainable`이다. 조건을 acquisition payload에 fact-local로 담는 방식을 우선 검토한다. 별도 condition/constraint node가 필요하면 L3-01 binding을 지키고, 이를 acquisition terminal fact나 L3-03 question result로 잘못 등록하지 않는다. 조건의 소유/소비를 기존 계약 안에서 표현할 수 없으면 P3 gap으로 분리한다.
5. Fact ID는 semantic content 기반으로 계산한다. Locator·timestamp·registry metadata는 제외하고 의미가 같은 fact의 복수 provenance는 합집합으로 보존한다. 조건/경로가 다르면 별개 의미로 보존하며 동일한 문자열이라는 이유만으로 합치지 않는다.
6. 결과에는 exact question key, `registry_revision`, authority ref, state, 실제 attempt refs, provenance 또는 미수행 사유, limitation/dependency를 결속한다. 미수행을 정당화하려고 가짜 observation/provenance를 만들지 않는다.
7. `resolved`는 §4 판정표에 따라 기존 `one_or_more_acquisition_facts_or_one_admissible_acquisition_unobtainable_fact`와 whole-scope result 조건을 충족한다. 모든 필수 조사를 실제 수행한 뒤 조건까지 확정한 경로가 있으면 무관한 추가 경로의 불확실성만으로 해결을 막지 않는다. Token 발견이나 해당 경로의 필수 조건 미확인은 확정 사실이 아니다. 답변 충족과 조사 coverage의 근거를 별도 기록하며 game-wide completeness를 요구하거나 주장하지 않는다.
8. §4의 후속 의미 명확화에 따라 독립적으로 확정한 fact는 open question 때문에 버리지 않는다. Open result의 `fact_refs=[]`를 유지하고 `fact_question_bindings`로 부분 기여를 전달하되, resolved 판정표를 만족한 질문까지 open으로 고정하지 않는다. 기존 `terminal_result()`는 open result의 authority/limitation 전체를 검사하지 않으므로 신규 acquisition validator가 **open result까지 전수 검사**한다.
9. `resolved`와 `investigated_unresolved`의 공통 선행 admission으로 §4의 item×family coverage를 구현한다. Phase 2 result contract에 다섯 outcome의 닫힌 허용 집합과 충족/미충족 대응표, evidence 요건을 함께 고정한다. Unknown/미분류 outcome을 거부하며 partial fact나 attempt 개수만으로 실제 조사 수행 여부를 판정하지 않는다.
10. **NC-01 개발 점검:** 결합 가능성이 불확실하면 작은 synthetic fixture로 기존 `resolve_item()`의 두 authority·partial binding·mode 조합을 조기에 확인할 수 있다. 코드 열람으로 충분히 확인된 부분의 별도 선행 실행은 의무가 아니다. 필요한 사례는 최종 G1에 재사용하며 Phase별 테스트·승인 gate를 신설하지 않는다. 실제 불가능성이 발견되면 기존 stop condition에 따라 영향과 대안을 기록한다.

**Validation:** duplicate/missing/unexpected question `0`, case/alias join 오류 `0`; fact-provenance-question referential integrity, content ID, qualifier 관계, raw-token-only admission 거부, partial/whole-scope 및 coverage admission 구분. Synthetic combined-call 관찰은 full-corpus/adopted 성공을 뜻하지 않는다. New kind/scope가 필요하면 result 편법 대신 P3 처리.

---

### Change 3 — Phase 3: Predecessor Acquisition Material Disposition

**Purpose:** 기존 제품의 acquisition 문장을 successor 근거로 자동 상속하지 않게 한다.

**Files:** 읽기 전용 `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`, `dvf_3_3_decisions.jsonl`, current product structured corpus; 신규 disposition records.

**Implementation Notes:**

- **NC-02 census universe:** 아래 네 material-kind의 입력 파일/readpoint hash와 selector를 census manifest에 고정하고, 실제 추출 목록과 대조한다. 전수 disposition claim은 이 명시적 집합 M에 한정하며 repository의 모든 historical acquisition 자료를 조사했다는 뜻이 아니다.

| Material kind | 포함할 위치/값 | 집계 단위 |
|---|---|---|
| Hint | `dvf_3_3_facts.jsonl`의 non-empty `acquisition_hint`와 대응 `fact_origin` | exact item별 field record |
| Source-slot material | 동일 facts의 `slot_meta` 안 acquisition slot/binding 및 그 근거 refs. `body_material.source_slots.acquisition_hint` 포함 | item + exact metadata locator; Book 55개로 selector를 제한하지 않음 |
| Predecessor absence claim | `dvf_3_3_decisions.jsonl`의 non-empty `acquisition_null_reason` | item별 field record; successor negative가 아님 |
| Current product acquisition material | 실행 시 current product locator가 지시한 corpus의 명시적 acquisition typed material/role refs 및 **모든 locale의 acquisition 표현 span**. `role_material.acquisition_source_fact_ids`, `menu_public_acquisition_fact_ids`, `body_composition.menu.ko`/`.en`, `text_ko`와 실제 존재하는 EN/기타 locale 표현 surface를 포함하며 locale 목록·locator를 census 입력에 명시 | item + JSON locator + locale/claim span; 빈 ref 배열도 관찰해 표현 누락을 탐지 |

- Current `Base.BookTrapping1`에는 acquisition role-ref 배열이 비어 있어도 `body_composition.menu`와 `text_ko`에 획득 문장이 있다. 따라서 non-empty fact refs만으로 product material을 열거하지 않는다. Structured ref와 source-slot, 실제 표현을 대조해 acquisition material의 누락을 확인한다. Selector로 분류되지 않는 acquisition 구조/표현이 발견되면 census 범위 누락으로 보고 selector와 M을 명시적으로 갱신하기 전 전수 disposition을 선언하지 않는다.
- Material identity는 `(input path/hash, exact item_id, material kind, locator/claim span)`으로 추적한다. Product에 같은 문장이 여러 표면/locale로 존재해도 각각의 occurrence를 보존하고 동일 predecessor claim과 연결한다. 신규 successor truth를 문장 문자열에서 추론하지 않는다.
- 추가 NC-06: `DECISIONS.md`의 「Iris Layer 3 — source-bound shared composition」 결정은 기술서 55개의 KO 장소 집합과 이에 대응하는 EN 장소 집합을 함께 기록한다. KO와 EN의 실제 acquisition span 및 claim 대응을 census에 포함하고 locale 간 장소/조건 불일치를 disposition에 남긴다. Locale inventory는 selector가 만든 M과 별도로 current product의 실제 locale surface에서 확인하여, KO-only selector로 M을 재생성한 것만으로 전수성을 선언하지 않는다. 표현이 누락되었으면 누락으로 기록하고 이 단계에서 번역·문장 교정은 하지 않는다.
- **NC-03 집합 집계:** §4의 H/B 관계를 재계산하고 H/B/M별 material count, unique item count, 교집합·차집합을 구분한다. 현재 `B⊆H`, 교집합 `55`, H-only `1,050`, B-only `0`이다. Item은 합집합으로, disposition은 material identity 집합 M으로 집계하여 중복 합산·누락을 막는다.
- `Base.BookTrapping1`의 `slot_meta.body_material.source_refs`에는 procedural 및 vehicle distribution 경로/hash가 있으나, 이는 current source rebinding의 출발점이다. 그 안의 문장·포괄 locator만으로 모든 장소/조건을 승인하지 않는다.
- 모든 material을 `rebound`, `lead-only`, `unverified`, `rejected` 의미 중 하나로 처분한다. 실제 enum은 신규 result contract에서 확정한다.
- Rebound는 source 대조를 마친 **candidate 자격**이다. Successor admission·question resolution과 동일한 상태가 아니다.
- 한 predecessor 문장에 여러 장소가 있으면 claim별로 분해해 일부만 재확인되었는지 보존한다. Book family 전체에 한 건의 근거를 무검증 전파하지 않는다.
- 과거 `build_acquisition_sprint7_authority_promotion.py` 등은 rendered/bridge/runtime promotion을 포함하므로 이 실행의 producer로 호출하지 않는다. 기존 코드/출력은 discovery 참고로만 읽는다.

**Validation:** 고정 input/selector에서 재구성한 M과 census record 집합 exact equality, missing/unexpected/duplicate material `0`; 실제 locale inventory와 KO/EN acquisition span 포함 여부·claim 불일치 disposition 대조; H/B 교집합·차집합 및 item/material 분모 일치; M의 미판정 `0`; rebound claim 전수 current source binding; predecessor 문장만을 provenance로 한 successor fact `0`; product body 변경 `0`. Census 내부 disposition count만 검사해 census 또는 EN surface 누락을 숨기지 않는다.

---

### Change 4 — Phase 4: Full Target Acquisition Investigation

**Purpose:** 2,105개 질문의 실제 수행 범위와 결과를 기록한다.

**Files:** 신규 producer, corpus의 attempts/results/facts/provenance/limitations.

**Implementation Notes:**

- Target마다 Phase 1에서 고정한 공통 family 집합 F를 조사한다. Q의 각 pair에 method, source-member/locator 범위, 참조 observation, finding, 접근 실패, 필요한 consumer 추적, coverage, remaining dependency와 outcome을 남긴다. 일괄 파서도 exact item별 탐색 범위와 결과가 추적 가능해야 한다.
- Positive fact `0..N`을 수집하고 첫 경로 이후에도 예정된 다른 source를 조사한다. 서로 다른 경로·조건·source의 증거를 보존한다.
- 네 known identity uncertainty도 같은 question universe 안에서 조사한다. 다른 source에 exact acquisition evidence가 있으면 개별 검토하되 declaration ambiguity를 지우지 않는다.
- 이미 존재하는 L3-03 partial fact와 first-contact obligation은 acquisition state와 독립적으로 계속 소비한다.
- 먼저 item의 모든 required family pair에 대해 §4 admission을 검사한다. 필요한 조사·관찰이 하나라도 미수행이면 acquisition은 `not_investigated`다. Family 전부를 수행한 후에만 evidence 수준에 따라 `resolved` 또는 `investigated_unresolved`로 분류한다.
- Phase 4의 전수 조사 종료 및 L3-04 complete는 **`not_investigated=0 / 2,105`와 Q의 실제 조사 coverage 충족을 모두 요구**한다. 실제 조사를 수행했으나 결론을 닫지 못한 unresolved는 허용한다. 접근 실패나 미수행을 unresolved로 치환해 종료하지 않는다.
- 필요한 실제 조사를 수행할 수 없다면 수행한 결과와 partial facts를 보존하고 남은 질문을 미수행으로 기록한다. 종료해야 할 경우 `partial` 또는 진전 불가능한 의존이 있으면 `blocked` 등 실제 non-complete 상태를 사용한다.

**Validation:** state 없는 question `0`; Q와 family outcome의 exact equality; 필수 source 관찰 누락 또는 access-failure-only pair의 investigated admission 거부; unresolved마다 수행 evidence와 limitation/dependency 존재; known uncertainty 누락 `0`; distinct path/provenance 손실 `0`; `not_investigated=0` 고정 종료 조건 검사.

---

### Change 5 — Phase 5: Negative Evidence and Edge-Case Adjudication

**Purpose:** positive-empty, source miss, identity ambiguity와 formal unobtainability를 구별한다.

**Files:** 신규 acquisition validator, 필요한 경우 negative evidence records, unresolved/identity disposition.

**Implementation Notes:**

- Negative candidate마다 explicit scope, source coverage identity, completeness 근거, dynamic/engine 누락 가능성, false-negative limitation, positive contradiction 유무를 판정한다.
- 기존 `terminal_result()` 요구값인 `closed_scope=true`, `coverage_complete=true`, `false_negative_limit=excluded_within_bound_scope`, source bindings, scope description, authority ref와 fact의 `negative_evidence_refs`를 충족한다. Boolean을 채우는 것으로 증거를 대신하지 않는다.
- Single container/distribution 내 부재를 item-global `(item_id, acquisition, item)`의 획득 불가로 확대하지 않는다. Bound scope가 실제 negative claim을 충분히 지지하는지 별도 검사한다.
- Positive path와 충돌하는 item-global negative는 admission하지 않는다. Duplication/loader uncertainty는 arbitrary winner 또는 negative로 닫지 않는다.
- 정당한 negative producer가 성립하지 않으면 fact assignment `0`으로 종료 가능하다. L3-01의 기존 `current_producer=none` 기록을 덮어쓰지 않는다.

**Validation:** negative가 있으면 전수 evidence/closed-scope/contradiction 검증. Source miss→negative, identity ambiguity→negative를 거부하는 fixture. Negative `0`도 허용하는 검사.

---

### Change 6 — Phase 6: Independent Authority and Structured Consumption

**Purpose:** 봉인된 L3-03을 보존하며 획득 결과를 기존 resolver에 결합한다.

**Files:** 신규 `acquisition_results.py`, `acquisition_consumption.py`, acquisition manifest/corpus; §5 current registration 파일.

**Implementation Notes:**

1. 새 manifest는 L3-01 identity, L3-02 definition/application readpoint, target set, acquisition source/interpretation, corpus, producer, human contract, required test identity를 결속한다. L3-03은 결합 소비의 별도 bound input이며 acquisition 결과 저장소가 아니다.
2. Candidate 출력은 repository 내부 허용된 새 디렉터리로 제한하고 비어 있지 않은 authority 덮어쓰기·경로 탈출을 거부한다. 검증 전 current로 연결하지 않는다.
3. L3-03 `load_manifest()`와 `validate_payload()`를 그대로 호출한다. Acquisition은 신규 loader/validator로 source·manifest·전체 결과를 확인한다. Generic adopted payload의 status만 믿거나 memory의 임의 dict로 adopted 권한을 만들지 않는다.
4. 결합 consumer는 L3-03 corpus의 `application_inputs`에 있는 routes/gap을 사용한다. L3-02 baseline으로 되돌려 L3-03이 추가한 `1,100` non-acquisition key를 잃지 않는다.
5. 두 결과 집합을 exact item/question key로 결합한다. Authority ID 충돌, 중복 question, cross-item fact, stale revision, L3-04의 non-acquisition overwrite는 실패로 처리한다. 동일 semantic fact ID가 겹치면 content 일치 여부를 확인하고 provenance/authority 경계를 유지하며 last-wins로 덮어쓰지 않는다.
6. 기존 `resolve_item()`에 results, authorities, fact_question_bindings를 전달한다. Item complete 값을 직접 기록하지 않고 기존 식 `scope_determined AND every_required_axis_terminal AND acquisition_state == resolved`로만 계산한다.
7. `result_mode`는 호출 전체에 적용된다. Preview는 두 입력을 검증된 candidate 관점으로 소비하고, adopted 소비는 두 readpoint가 모두 실제 adopted인지 확인한다. Preview를 위해 기존 L3-03 route나 저장 corpus 상태를 바꾸지 않는다.
8. 최종 authority에서 acquisition row 또는 required family pair 누락은 신규 validator가 거부한다. 결과 label과 Q의 조사 evidence가 일치하는지도 검사한다. 기존 resolver의 일반적인 missing→`not_investigated` fallback을 2,105행 완전성 또는 실제 조사 증거로 사용하지 않는다.
9. 기존 `cli.py`가 sealed member이므로 새 모듈의 `python -m ...acquisition_results` entrypoint를 제안한다. 명시적 repository root와 acquisition output만 받게 하고 composer fallback과 분리한다. `build layer3 acquisition-results`는 현재 존재하는 명령으로 문서화하지 않는다.
10. 기존 loader/resolver를 수정해야만 구현할 수 있다면 해당 변경을 별도 contract/architecture 문제로 분리한다. L3-03 manifest hash 재작성·검사 제거·monkeypatch로 우회하지 않는다.
11. Exact candidate 검증 성공, 고정 완료 조건/coverage 충족, 필요한 owner 실행 권한과 P4 복구 정책 확인 후 새 current route와 authority/required-test 등록을 연결한다. 등록은 §4 R3의 current execution registry에만 추가하며 required identity의 실제 consumer membership을 검사한다. 기존 entry는 의미상 동등하게 보존한다. Corpus는 immutable candidate bytes로 두고 채택 상태는 route/성공 closeout이 소유하는 기존 패턴을 따른다.
12. L3-05 handoff는 두 manifest identity, L3-02 revision, structured API, fact-local conditions, partial/open states, provenance, limitations를 전달한다. Public prose와 projection은 생성하지 않는다.

**Validation:** L3-03 standalone/combined non-acquisition facts/results/partial bindings/first-contact/pending/gap equivalence; authority 순서 교환 결과 동일; acquired axis 반영; completion 공식 보존; candidate/adopted route와 exact hash 일치; L3-01/02/03 member drift `0`.

---

### Change 7 — Phase 7: Single G1 Validation and Closeout

**Purpose:** 실제 산출물과 소비 결과에 한정해 L3-04 달성 상태를 기록한다.

**Files:** 신규 focused test, L3-04 closeout, current registration 및 관련 상위 문서 섹션.

**Implementation Notes:**

- §7의 V1~V11은 검증 범위의 추적 ID이며 독립 test/Gate 목록이 아니다. **신규 required test identity 1개, 최종 acceptance Gate G1 1개**로 묶는다. 앞선 Change의 Validation 항목은 G1에 합류할 불변식이며 Phase별 통과 증명이나 명령 실행을 추가 요구하지 않는다. 내부 함수·fixture·subtest 분할 및 실행 순서는 구현에 맡긴다.
- 후보 생산/검증/채택에서 동일 corpus identity를 추적한다. 최종 성공 subject 이후 semantic bytes가 바뀌면 이전 결과를 재사용하지 않는다.
- 최종 candidate focused 검사 후 채택을 연결하고, 실제 adopted readpoint가 exact verified subject를 읽으며 combined consumption이 성공하는지 제한적으로 확인한다. 이는 G1의 연결 확인 부분이며 별도 G2·required identity·추가 승인 절차가 아니다. Candidate와 adopted는 lifecycle이 달라 호출이 나뉠 수 있지만 이를 이유로 전체 focused suite나 corpus 생산을 두 번 요구하지 않는다. 연결 확인 전에는 최종 adopted complete를 선언하지 않는다.
- Closeout에 고정 완료 조건과 unobservable-source 규칙의 적용 결과, Q/F/inventory revision 및 family별 수행·미수행 집계, P3 발생/처리와 P4 owner 결정·위임 근거, 상태 분포, positive/negative 수, unresolved·미수행 잔여, M의 material-kind별 disposition, source limitation, touched surfaces, 명령·exit code·subject hash를 기록한다.
- Required identity가 current execution registry와 실제 reader에 연결되며 historical registry가 불변임을 기록한다. 검토 지적의 수정 위치와 근거는 아래 대응표로 추적하고, 계획 수정 완료를 독립 review PASS로 보고하지 않는다.
- `validated / out_of_scope / unvalidated_but_in_scope`를 구별한다. 검증 실패 이력과 기각 candidate를 삭제하거나 PASS로 재작성하지 않는다.
- 실제 채택이 완료된 경우에만 DECISIONS/ARCHITECTURE/ROADMAP을 갱신한다. L3-05 expression, L3-06 runtime/product adoption은 별도 후속 책임으로 명시한다.

**Validation:** exact adopted route/readpoint, 성공 subject, consumed input/output identity와 closeout claim 일치. Scope 안의 검증 잔여가 있으면 해당 성공 주장을 제외하고 적절한 closeout 상태 사용.

| 검토 항목 | 수정 위치/처리 |
|---|---|
| R1 / NC-05 | §1/§4/Change 4/§7/§12: 미수행 잔존 complete 선택지 제거, P2를 상태 규칙으로 정리 |
| R2 | §4 coverage admission, Change 1/2/4, V2: target×F의 독립 좌변과 수행 evidence가 상태 부여 조건 |
| R3 | §4 exact naming 정정/route/reader 근거, Config/Change 6/V10: execution registry 유지 및 실제 membership 검사 |
| R4 | §4 owner/실행자 구분·lifecycle·진행 범위, Change 6, §10/§11/§12: 정책 자기 결정 방지 |
| NC-01 | Change 2: 결합 가능성의 조기 확인 취지 유지. 현재 개정에서는 별도 선행 실행을 선택화하고 필요한 fixture를 G1에 재사용 |
| NC-02/03 | §4 H/B 집합 관계, Change 3/V6: material kind 집합 M, selector와 occurrence identity, 분모별 집계 |
| NC-04 | §7 Manual Validation: family/상태/복수 경로/identity anomaly의 위험과 선정 근거 유지. 현재 개정에서는 조합별 별도 표본 대신 조사 기록·중첩 사례 재사용 |
| 추가 NC-05 | §4/Change 2/V2: 다섯 coverage outcome 어휘와 충족/미충족 대응을 닫고 unknown/미분류 값 거부 |
| 추가 NC-06 | Change 3/V6: 모든 locale의 acquisition span, KO/EN claim 대응 및 독립 locale inventory 대조 |
| 추가 NC-07 | §4/Config/V10: source-policy의 manifest/route 직접 entry 부재와 실제 reader·유지 결정 구분, 등록 직전 확인 |
| 추가 검토 4.1/4.2 | §4/§11: Q/F는 bounded execution inventory, P4는 L3-04 한정 조건이며 공통 taxonomy/gate로 승격 금지 |
| 현재 개정 — 의미 정합성 | §4/Change 2: 초기 human contract 문구와의 차이를 공개하고 신규 후속 계약에 명확화; 확정 경로와 추가 경로 불확실성의 판정표 적용 |
| 현재 개정 — 최소 검증 | Change 2/7 및 §7: 조기 점검 선택화, G1·required identity 각 1개, 전체 후보 이중 생산 기본 의무 제거, 공유 증거·중첩 표본 재사용 |

---

## 7. Validation Plan

### Automated Validation

신규 Authority/Sealed Artifact Surface를 추가하는 **heavy** 실행으로 검증한다. 이는 전체 repository suite나 추가 ceremony를 자동 요구한다는 뜻이 아니다.

**최소 실행 원칙:** 신규 required test identity는 아래 1개, 최종 Gate는 G1 하나다. V1~V11과 각 Change의 Validation은 이 Gate 안의 검사 책임이며 별도 테스트 파일·명령·승인·보고서를 요구하지 않는다. 기본 흐름은 후보 1회 생산 → 최종 focused 명령 1회 → 채택 후 제한된 실제 readpoint/consumption 확인이다. 마지막 확인은 같은 검증 구현을 재사용하는 G1의 연결 확인 부분이다. 실패, 검증 subject 변경 또는 구체적인 미검증 영향이 없는 한 전체 생산/검사를 반복하지 않는다. 조사 및 수동 의미 검토 자체는 생략하지 않으며 그 기록을 G1에서 재사용한다.

| 로드맵 검사 | 실제 검사 내용 |
|---|---|
| V1 Universe | exact target/question 각 `2,105`, duplicate/missing/unexpected `0`, case/alias/cross-item 오류 거부 |
| V2 State | 독립 계산한 Q=target×F와 pair 결과 exact equality; 닫힌 다섯 outcome의 evidence admission; source-member·관찰·method/finding/limitation binding; pair 미수행 시 resolved/unresolved 거부; §4 판정표와 전수 state 일치 및 complete의 `not_investigated=0`. 확정 경로와 무관한 추가 경로 한계를 구별하고, token-only/필수 조건 미확정을 accepted fact로 승격하지 않음 |
| V3 Fact/provenance | source/member hash, locator, raw observation→interpretation→fact, condition, question binding, semantic ID 및 정정 시 재결속 |
| V4 Multiplicity | 복수 path/조건/동일 의미의 multi-source provenance 보존; source·serialization 순서를 바꿔도 대표 선택 없음 |
| V5 Negative | source miss/partial closure/positive contradiction 거부; 정당한 closed-negative 검사; count `0` 허용 |
| V6 Predecessor | 고정 input/selector에서 재구성한 material 집합 M과 census exact equality; 실제 locale inventory에서 KO/EN을 포함한 모든 acquisition span 포함 여부·claim 불일치 disposition 대조; kind별 disposition·H/B 교집합/차집합·item/material 분모 대조; 빈 role refs의 실제 표현 누락 탐지; rebound 재결속 및 순환 근거 거부 |
| V7 L3-03 preservation | standalone과 combined의 비획득 projection 동등성; `4,233` facts/`9,982` results/partial bindings의 identity 보존 |
| V8 Completion | acquisition resolved만으로 item complete가 되지 않음; 독립적으로 확정한 fact가 open state 때문에 소실되지 않으며 binding 존재만으로 resolved를 만들지 않음; §4 해결 요건 충족 시 임의 unresolved 고정 금지; scope/pending/gap 보존 |
| V9 Determinism | 실제 corpus의 canonical identity·중복·provenance 보존을 검사하고, 동일 production 경로를 사용하는 최소 fixture에서 입력 순서·metadata를 바꿔 ID/의미 집합 불변을 V3/V4와 함께 확인. 전체 corpus의 독립 이중 생산은 기본 의무가 아니며 fixture로 다루지 못하는 순서 의존·재현성 결함의 구체적 위험이 발견된 범위에만 추가 |
| V10 Compatibility | 신규 combined consumer와 shared registration의 기존 entry 보존; §4 R3의 current registry/실제 reader 경로 및 새 required identity membership 일치, historical registry 불변; 추가 NC-07의 source-policy 경로/역할/실제 reader 대조와 신규 source 분류 반영; 공통 파일 변경 필요 시 별도 영향 판정 |
| V11 Protected surfaces | 실행 전 열거한 L3-01/02/03 sealed member와 이번 writer/consumer가 영향을 줄 수 있는 product/source·composer·KO/EN·Menu/Tooltip·Lua·generation/pointer·package/install 경로의 identity/diff 비교. 영향 밖 설치 트리 전수 census나 runtime parity 검사는 요구하지 않으며 보호 주장은 실제 비교한 경로로 제한 |

신규 test identity 제안:

```text
test_layer3_acquisition_results.Layer3AcquisitionResultsTest.test_acquisition_results_contract
```

구현 후 repository root에서 사용할 **제안 명령**이다. 현재 신규 모듈/test는 아직 없으며 실행 가능한 기존 명령이라고 주장하지 않는다. 옵션과 등록 identity는 구현에서 확정한 뒤 최종 명령을 closeout에 그대로 기록한다.

```powershell
# 신규 모듈 CLI 구현 후: acquisition 후보 생산
uv run --project .\Iris\tooling --no-sync python -m iris_tooling.domains.layer3.acquisition_results --repository-root . --output .tmp/acquisition/candidate-001

# 신규 test source/identity 등록 후: focused contract 및 실제 corpus 검증
uv run --project .\Iris\tooling --no-sync python -m pytest .\Iris\build\description\v2\tests\test_layer3_acquisition_results.py -q -p no:cacheprovider --round3-contract=diagnostic --round3-additional-source=Iris/build/description/v2/tests/test_layer3_acquisition_results.py
```

- Focused test는 명시적 manifest 입력과 candidate/adopted 소비 모드를 지원하도록 구현한다. 최종 검증에 사용한 환경값·입력 경로·검증 모드·exit code를 기록한다.
- 실제 adopted readpoint 소비 확인은 검증한 manifest/corpus/member identity, route·성공 subject 연결, 실제 adopted loader와 combined consumer의 입력·결과를 확인한다. 기존 loader의 필수 내부 검사는 그대로 실행하지만 수동 source 조사·fixture suite·후보 생산은 반복하지 않는다. 같은 test의 제한된 모드 또는 동일 검사를 호출하는 보조 entrypoint 중 구현에 맞게 선택하고 명령·exit code를 기록한다. 검증 없는 status 전환은 허용하지 않는다.
- Required identity는 `Iris/validation/execution/required_validations.json`과 현재 source-classification 방식으로 등록한다. 새 validator taxonomy나 영구 proof tree를 만들지 않는다.
- Fixture는 공통 최소 입력과 table-driven 변형을 재사용한다. Coverage 누락/얕은 조사/접근 실패/분모 축소/잘못된 outcome 거부, source miss와 negative 구별, §4의 확정 경로 대 미확정 필수 조건, 복수 경로·조건·authority 결합을 함께 다룬다. 같은 validator 분기·불변식을 이미 입증한 사례를 명칭별로 중복 추가하지 않는다. Fixture/test/subtest 수 자체는 고정하지 않으며 실제 corpus의 전수 구조·상태 검사를 작은 표본으로 대체하지 않는다.
- Exact 관련 명령이 exit `0`인 경우에만 PASS다. Python/uv/pytest 또는 필요한 source/authority가 없으면 BLOCKED이며, 과거 결과나 다른 명령 성공으로 대체하지 않는다.
- Python만 변경하는 본 계획에서 Java/JS/Lua 검증을 기본 실행하지 않는다. 승인된 scope 변화로 해당 코드가 바뀌면 각각 `.\gradlew test`, `pnpm biome check .`, `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`의 정확한 관련 명령과 적용 범위를 재확정한다.
- 검증 확대·재실행은 발견한 실패 또는 실제 영향에 한정한다. 충분한 근거 확보 후 confidence 목적의 반복 실행은 추가하지 않는다.

### Manual Validation

- Source interpretation rule마다 전제, raw token 의미, 실제 consumer 연결, 조건, 예외, 닫히지 않은 engine/loader 경계를 실제 조사 중 검토하고 그 기록을 최종 검증에 재사용한다. 조사 후 동일 원본을 다시 읽는 독립 audit를 의무화하지 않는다.
- `Base.BookTrapping1`과 나머지 skill book의 개별 source 결속, loot/vehicle/foraging/recipe·transform의 실제 발견 표본, 복수 경로, positive-empty 및 네 identity anomaly를 검토한다.
- **NC-04 표본 선정:** 실제 해석 규칙과 서로 다른 실패 위험을 기준으로 겹치는 최소 사례를 선택한다. Family별 의미 연결, 복수 경로/조건, positive-empty, predecessor disposition 및 네 identity anomaly를 조사 기록과 함께 대조하되 family×outcome의 모든 조합마다 별도 수동 표본을 강제하지 않는다. 같은 사례가 여러 위험을 다루면 재사용하고, 실제 사례가 없는 항목은 `0`과 이유를 기록한다. 전수 source 조사와 M disposition 의무는 유지하며 표본은 rule 적용의 질적 확인에만 사용한다.
- Closeout에는 표본 exact item/claim ID, family/outcome/disposition 층, 선정 이유, raw locator, 검토 finding과 남은 한계를 기록한다. 표본 수나 resolved 비율을 성공 목표로 만들지 않고 새 독립 audit ceremony를 추가하지 않는다. 표본 결과를 전수 item 의미 정확성으로 확대하지 않는다.
- 가족 이름·분류명으로 item별 근거를 대체하지 않았는지, 내부 token을 장소명으로 과해석하지 않았는지 검토한다.
- L3-05가 confirmed facts와 open questions를 함께 읽을 수 있고 raw source 재조사 없이 truth-changing condition을 보존하는지 G1의 API/구조화 출력 확인을 재사용한다. 별도 수동 API 검증 실행은 추가하지 않는다.
- In-game/runtime/UI 수동 검증은 이번 범위에 포함하지 않는다.

### Validation Limits

- 구조·참조·해시·결정성 검증은 모든 acquisition fact의 전수 수작업 의미 정확성 감사가 아니다.
- 전체 후보를 독립적으로 두 번 생산하지 않은 경우 결정성 주장은 실제 corpus identity 검사와 production 경로 fixture에서 확인한 불변성에 한정한다. 전체 corpus 재생산 동등성을 검증했다고 확대하지 않는다.
- Repository snapshot 밖 source, 실제 설치 게임 build 일치, 전체 runtime dispatch/conditional spawn, external mod semantics는 검증하지 않는다.
- KO/EN prose 품질, Menu/Tooltip 표시, multiplayer/long-session, package/install/deployment/release readiness는 검증하지 않는다.
- 보호 주장은 실제 열거하고 비교한 경로와 입력 identity 범위에 한정한다. 전체 runtime 행동 동등성을 파일 hash만으로 주장하지 않는다.
- 이번 **계획 작성**에서는 코드/readpoint/자료 집계를 읽기 전용으로 확인했다. 신규 구현·G1·runtime 검증은 수행하지 않았다.

---

## 8. Risk Surface Touch

### Authority Surface

**변경 있음 — additive.** L3-04가 acquisition fact/provenance/result/limitation 및 정당화된 negative evidence를 소유한다. L3-02 definition, L3-03 비획득 결과, L3-05 expression, L3-06 product/runtime의 owner는 유지한다.

### Runtime Behavior Surface

**None.** 오프라인 tooling과 structured consumer만 추가한다. 게임 실행 코드는 변경하지 않는다.

### Compatibility Surface

**변경 있음.** 새 structured acquisition input/loader/combined consumer와 shared registration을 추가한다. 기존 resolver signature와 sealed implementation은 유지하고 기존 소비 결과와의 동등성을 검사한다.

### Sealed Artifact Surface

**변경 있음 — 신규 acquisition subject만.** L3-01/02/03 manifest/member와 product generation을 보존한다. 공통 Python/CLI 파일도 L3-03 member라는 점을 보호 목록에 포함한다.

### Public-Facing Output Surface

**None.** Predecessor public acquisition text와 KO/EN Menu/Tooltip 출력은 유지한다. 개발 문서의 L3-04 상태 설명을 runtime/public 기능 완료로 확대하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- **높음:** acquisition corpus를 L3-03 validator/manifest에 통합하거나 sealed common code를 수정하면 ownership 또는 hash binding이 깨진다. 독립 loader/validator와 기존 resolver 호출로 분리한다.
- **높음:** source-local 부재를 item-global negative로 확대하거나 namespace를 추측하면 정보 원칙을 위반한다. Exact identity·closed scope·interpretation lineage를 admission 조건으로 둔다.
- **중간:** condition 표현을 위해 L3-02 axis/kind를 편법 확장할 수 있다. 기존 payload/binding 내 표현 가능성을 먼저 확인하고 P3에 따른 gap 처리로 넘긴다.

### Runtime Risk

- 직접 runtime 변경은 없다. 다만 legacy acquisition promotion이나 unknown CLI fallback을 호출하면 composer/bridge 경로에 진입할 수 있다. 신규 entrypoint와 출력 allowlist로 차단한다.
- Candidate/adopted 혼동은 후속 L3-05가 미검증 사실을 소비하게 할 수 있다. Route·manifest·성공 subject 검증을 loader 책임으로 둔다.

### Compatibility Risk

- **높음:** L3-02 baseline routes를 사용하면 L3-03의 newly required 질문과 partial bindings를 잃는다. L3-03 `application_inputs`와 standalone/combined equivalence로 방지한다.
- **중간:** `result_mode` 혼합, authority ID 충돌, merge order 우선순위로 기존 결과가 덮일 수 있다. 명시적 모드와 exact key 충돌 검사로 실패 처리한다.

### Regression Risk

- **높음:** item complete 직접 저장, binding만으로 resolved 승격, unresolved→N/A 또는 확정 경로가 있어도 무관한 한계 때문에 unresolved로 고정하는 처리는 완료 의미를 왜곡한다. §4 판정표와 실제 `resolve_item()`을 G1에서 함께 검사한다.
- **높음:** 전수 state count를 맞추기 위해 얕은 attempt/접근 실패만으로 investigated label을 부여할 수 있다. Q와 source-member coverage를 독립 재구성하고 실제 수행 admission을 검사한다.
- **높음:** Book 55개만 disposition하고 hint 1,105개 또는 구조화 product material을 놓칠 수 있다. 자료 종류별 census와 coverage를 분리한다.
- **중간:** working tree의 기존 문서 삭제를 이번 변경으로 오인해 복원·정리할 수 있다. 실행 전 변경 상태를 별도 기록하고 task diff만 검토한다.

---

## 10. Rollback Plan

1. **채택 전 실패:** 새 candidate를 current에 연결하지 않는다. 실패 이유·candidate identity·필요 evidence를 보존하고 L3-01/02/03 및 product route를 유지한다.
2. **Combined consumer/registration 실패:** 해당 신규 interface/entry 변경만 분리 철회한다. 기존 entries를 baseline과 대조하여 복구하고 L3-04 corpus는 non-current candidate/history로 보존한다. Repository 전체 reset 또는 기존 사용자 변경 덮어쓰기를 하지 않는다.
3. **채택 후 결함:** §4 P4의 기본안은 결함 L3-04 route를 이전의 유효한 검증된 L3-04 readpoint 또는 최초 채택 전 부재 상태로 철회하고, 새 correction subject를 생산·영향 검증한 뒤 재채택하는 방식이다. 이 계획의 후속 실행 승인에 복구안·위임 범위를 함께 결속하며 같은 정책을 채택 직전에 재승인받지 않는다. 기존 sealed bytes/history를 보존하고 predecessor 문장을 successor truth로 연결하지 않는다. 기본안 밖 변경·권한 확대가 필요할 때만 영향과 대안을 제시해 추가 결정을 받는다. 이번 문서 수정만으로 구현/adoption/복구 실행 권한이 주어졌다고 주장하지 않는다.
4. **Shared sealed 파일 변경 필요:** 본 계획의 기본 구현 범위를 중단하고 별도 contract/architecture 문제로 기록한다. 검사 삭제나 기존 manifest 재해시를 복구책으로 사용하지 않는다.
5. **보존:** 실패/기각 기록과 adopted history를 삭제하지 않는다. 재생성 가능한 임시 파일 정리는 필요한 evidence와 후속 입력을 보존한 뒤 별도 수행 가능하며 adoption gate가 아니다.

---

## 11. Governance Constraints

- `Philosophy.md`의 근거 기반 정보, 근거 부족 시 침묵, 추천·우열 금지, 게임 상태 비변경, Menu/Tooltip 두 표면 및 Tooltip Alt/최대 4줄 원칙을 유지한다.
- Pulse Hub & Spoke/SPI와 모듈 경계를 유지한다. 신규 오프라인 로직을 Pulse 또는 다른 spoke의 역할로 이동하지 않는다.
- Runtime/build-time을 분리하고 Iris runtime 100% Lua를 유지한다.
- 현재 owner와 sealed member를 우회하지 않는다. 기존 contract의 호환 가능한 vocabulary admission과 question/definition revision을 혼동하지 않는다.
- New L3-04 authority·registration·closeout는 additive 변경으로 기록한다. L3-02 baseline, L3-03 facts/results를 새 결과 저장소로 재사용하지 않는다.
- P1/P2는 수정 계획의 고정 완료 조건/상태 규칙으로 적용하고 execution actor가 완화하지 않는다. P3의 정의 변경과 P4의 복구 정책은 사용자 owner가 필요한 lifecycle point에서 결정하며 이미 주어진 권한은 반복 확인하지 않는다. 실제 결정·위임·영향 범위를 실행 기록에 남긴다.
- Q/F 및 coverage outcome은 이번 L3-04의 bounded 조사·증거 관리에만 사용하며 새로운 의미 taxonomy로 굳히지 않는다. P4 owner decision도 이 계획에 한정된 adoption 조건이며 다른 Iris 작업이나 생태계 전체에 자동 적용하는 governance gate로 승격하지 않는다.
- Required-validation current/historical 지위는 §4의 superseding decision과 실제 readpoint에 따른다. 과거 문구를 지우거나 두 registry를 이중 current writer로 만들지 않는다.
- 종합 review의 의견 차이 및 이전 FAIL 이력을 수정본의 PASS로 재작성하지 않는다. Claude 검토에만 있던 `independent_review_gate=BLOCKED`를 새 프로젝트 공통 gate로 도입하지 않는다.
- 이번 계획 작성 요청은 구현·authority adoption 실행 기록이 아니다. 문서만으로 current state 또는 sealed decision을 갱신하지 않는다.
- 실패/미수행/blocked를 unresolved 또는 PASS로 위장하지 않는다. 완료 수치와 state는 실제 evidence를 따른다.
- Protected authority 변경, exact identity 손실, provenance 없는 해석 확대, 근거 없는 negative, resolver 우회 또는 runtime/product mutation이 필요해지면 해당 문제를 L3-04 안에서 추정으로 덮지 않는다.
- `EXECUTION_CONTRACT.md`의 touched-surface disclosure, claim-evidence binding, validation ceiling과 historical trace 보존을 적용한다. 과거 audit·clean checkout·full suite를 자동 재도입하지 않는다.

---

## 12. Expected Closeout State

**목표:** 고정 완료 조건·coverage admission, 필요한 owner 결정/권한, 실제 구현·검증·채택을 충족하면 `complete — off-live acquisition authority and structured consumption`.

| 완료 조건 | 요구 결과 |
|---|---|
| Exact universe | target/question 각 `2,105`, duplicate/missing/unexpected `0` |
| Truthful state | Q의 모든 required pair 및 source-member 범위에 실제 조사 evidence 존재; state와 admission 일치; acquisition `not_investigated=0 / 2,105`; 조사 후 unresolved 잔존 허용 |
| Fact integrity | accepted positive 전수 exact item/source/locator/interpretation/condition/provenance/question 결속 |
| Multiplicity | 확인된 복수 path와 multi-source provenance 보존 |
| Unresolved/negative | 한계·dependency 보존; 모든 negative에 closed-scope evidence; negative `0` 허용 |
| Predecessor/identity | input/selector로 닫힌 집합 M 전수 disposition, kind별 record/item 분모 및 H/B 관계 일치; rebinding 없는 승격 `0`; 네 uncertainty 누락·alias 치환 `0` |
| Independent authority | 신규 L3-04 adopted readpoint; L3-01/02/03 member 불변 |
| Structured consumption | adopted L3-03/L3-04 함께 소비, non-acquisition 동등성, 기존 completion 공식 유지 |
| Protected surfaces | 명시적으로 비교한 product/runtime/public/generation/package 경로 불변 |
| Owner/registration | 실제 P3 충돌 발생 시 해당 최소 범위의 정의 결정; 실행 승인에 P4 정책·위임 범위 결속 및 중복 승인 없음; current execution registry와 reader의 신규 required identity 1개 일치, historical registry 보존 |
| Handoff/claim | L3-05 structured input과 exact validation subject, ceiling, 잔여·non-claims 기록 |

`not_investigated>0`이거나 Q의 실제 조사 admission을 충족하지 못하면 `complete`로 닫지 않는다. 일부 범위만 달성하면 `partial`, 구현은 되었으나 필요한 검증이 없으면 `implemented_only`, evidence/authority/tooling/definition 또는 필요한 owner 결정 의존으로 진전할 수 없으면 `blocked`로 기록한다. 모든 state를 unresolved로 바꾸는 것으로 미수행을 제거하지 않는다. 계획 수정 완료 자체는 L3-04 실행 closeout 또는 독립 review PASS가 아니다.

완료해도 다음은 주장하지 않는다: 모든 acquisition resolved, 게임 전체 획득 방법의 완전성, source 밖 engine/runtime 전수 확인, 모든 fact의 전수 수작업 정확성, 모든 item의 investigation complete, KO/EN·Menu·Tooltip S2 완성, runtime/current generation/package 전환, freeze/RTC/Publish/release/deployment readiness.

L3-04의 최종 주장은 **근거에 결속된 독립 acquisition 조사 결과 authority와 기존 resolver를 통한 structured consumption 구축**까지다. 표현 및 Menu/Tooltip composition은 DVF-L3-05, current runtime/product adoption은 DVF-L3-06에 남긴다.
