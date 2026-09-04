# Iris Layer 3 investigation contract

Revision 1 · DVF-L3-02 · 2026-09-04

이 계약은 각 exact case-sensitive FullType의 조사 질문과 첫 접촉 정보 요구를 정의한다. 적용 결과는 `Iris/_docs/authority/dvf/layer3_investigation/manifest.json`이 결속하는 `contract.json`, `evidence.jsonl`, `applications.jsonl`과 이 문서다. 최종 채택은 계획의 adoption 모드 G1 성공에 종속되며, 실행 결과는 별도 단일 closeout에 기록한다. Manifest의 `adoption_subject`는 G1 전후에 bytes를 바꾸지 않는 검증 subject 표시이지 PASS를 자체 발급하는 필드가 아니다.

`layer3_successor/contract_manifest.json`의 bound bytes를 상속한다. 프로필은 질문 범위이며 fact producer·대표 의미 선택기가 아니다. 현재 제품의 단일 compose profile, prose, Menu/Tooltip, KO/EN, generation과 runtime은 이번 authority와 독립적이다.

## 질문을 구별하는 기준

| 프로필 | 실제 조사 질문과 admission | 첫 이해에 필요한 정보 | 상세로 남기는 정보 |
|---|---|---|---|
| direct | 모든 target: 다른 질문으로 포착되지 않은 직접 기능과 상태 변화가 있는가? | 어떤 직접 기능인지, 진실 범위를 바꾸는 전제. 재료 역할만 설명해서 놓칠 직접 동작을 확인한다. | exact 행동·대상·절차. 기능이 없으면 근거를 갖춘 N/A가 가능하며 최소 용도를 요구하지 않는다. |
| ingestion | 원본/추출 Type=Food 일치: 실제 섭취 가능성과 효과·조건은 무엇인가? | 섭취 가능한 형태인지, 실제 어떤 상태가 달라지는지, 상태가 기능을 바꾸는지. | 수치·영양값·분량·정확한 개봉 Recipe. 허기·갈증 해소를 전체 음식에 일반화하지 않는다. |
| combat | Type=Weapon 일치: 공격에 쓰는 방식과 성립 조건은? | 근접·발사 등 확인된 기능과 작동 전제. | 공격 수치·exact 장전/부착물 관계·우열 평가. |
| wearing | Type=Clothing 일치: 착용으로 제공되는 기능과 조건은? | 확인된 착용 기능, 상태/제약이 기능에 미치는 경계. | 부위별 수치·수선 절차. 타입만으로 보호 기능을 만들지 않는다. |
| storage | Type=Container 일치: 수납·운반 기능과 제한은? | 담는 기능과 착용 기능의 구별, 기능을 제한하는 전제. | 용량·감소율·슬롯별 표. 가방끼리 비교·추천하지 않는다. |
| reading | Type=Literature 일치: 읽기·기록·학습 중 실제 무엇을 하는가? | 기능과 확인된 변화, 읽기/학습 전제. 빈 노트와 학습 문헌을 동일한 효과로 설명하지 않는다. | 쪽 수·배율·단계별 수치와 exact 학습 Recipe. |
| expenditure | Type=Drainable 일치: 어떤 기능이 사용량을 소모하며 소진 시 무엇이 달라지는가? | 사용량과 실제 기능의 관계, 소진 상태의 제약. | 정확한 횟수·잔량·교체 관계. Drainable을 모두 연료·전원이라고 부르지 않는다. |
| crafting | 원본 static Recipe에서 exact input/keep token 확인: 변환 활동의 역할은? | 활동에 참여하는 역할과 넓은 역할의 진실 범위를 바꾸는 조건. | exact Recipe·결과·수량·관계별 요구. input/keep가 곧 accepted semantic role은 아니다. |
| cooking | 원본 nonempty EvolvedRecipe: 조리 활동에서 어떤 역할인가? | 섭취 효과와 별개인 조리 역할과 상태 전제. | exact EvolvedRecipe·투입량·결과 음식·조합. 음식 타입만으로 적용하지 않는다. |
| world_work | 원본 addToolDefinition의 exact item 또는 parseItemTypes alias/tag 일치: 월드 물체 작업에서 도구 역할은? | 제작 keep와 독립된 월드 작업 역할 및 전제. | exact 가구·우클릭 행동·결과·기술 수준·시간·확률. |

각 프로필의 machine 정의에는 stable ID/revision, 구체 질문, required axes, 각 first-contact 질문·선정 이유·상세 경계와 후속 조사 경로가 있다. 이 표의 순서는 우선순위가 아니다. Recipe와 Right-click은 동등한 독립 관찰 경로다. 이번 원본 확인 범위가 static Recipe 직접 token과 moveable 정의에 한정된다는 점은 두 경로의 의미적 우열을 뜻하지 않는다.

모든 Type별 배제는 **해당 원본 item declaration의 native channel만** 닫는다. 같은 기능을 구현하는 Lua 동작이나 다른 활동 역할까지 배제하지 않는다. 예를 들어 Type이 Food가 아니어도 직접 행동의 효과 질문이나 다른 활동 가능성은 direct와 gap assessment에 남는다. 원본이 여러 개이거나 추출 Type/FullType과 일치하지 않으면 native applicability도 미정이다. 파일 이름·DisplayCategory·Layer 2 label·검색 실패는 적용/배제 근거가 아니다.

## Source와 routing

Target은 current facts와 decisions의 item_id exact set 일치로만 도출한다. 공백 제거·대소문자 변경·Unicode 정규화는 하지 않는다. 중복·missing·extra는 오류다. 두 source의 path/hash와 정렬 후 identity당 LF인 set digest를 manifest에 결속한다. 기존 hints는 target identity 이외의 semantic 입력으로 소비하지 않는다.

`contract.json/sources`는 사용한 repository scripts, itemscript/recipe 추출 입력과 두 Lua source의 exact bytes를 결속한다. B41-labelled repository snapshot이며 정확한 upstream build는 확인하지 않았다. Hash는 source identity를 보장할 뿐 source의 의미·완전성을 증명하지 않는다. `ISInventoryPaneContextMenu`의 native 분기, Food/CantEat, 섭취 효과와 evolved 조리 조건은 질문을 구별하는 근거다. 원본을 실행하거나 엔진을 복제하지 않는다.

Item별 evidence record 하나에는 원본 path/block locator/field, 추출 Type 일치 여부, 원본에서 확인한 Recipe token·role, 확인되지 않은 index candidate, moveable definition/token/tag와 gap 판단을 담는다. 모든 application은 이 record와 공개 routing predicate를 참조한다. 개별 item/profile evidence 행렬이나 별도 target census는 없다.

Static Recipe는 원문 module로 수식한 direct token과 input/keep 역할만 positive admission한다. Recipe.GetItemTypes group, result 관계, 동적 확장, index 누락을 negative로 바꾸지 않는다. Moveable은 원본 parseItemTypes가 특정 item token을 tag로 치환하는 규칙까지 적용한다. 축약 `moveables_tooldefs`의 itemIds만 믿지 않는다. `fixing_fixers` 축약 목록과 rightclick rule index도 의미·완전성 authority로 사용하지 않는다. 그 경로의 부족분은 원인과 다음 조사를 식별한 gap으로 남는다.

Applicability는 `confirmed_applicable`, `evidence_backed_not_applicable`, `investigated_unresolved`, `not_investigated`다. 관찰 누락은 N/A가 아니다. Positive/negative가 충돌하면 양쪽 관찰·evidence와 positive context를 보존하고 pending으로 남긴다. Confidence, 수량, 순서로 승자를 선택하지 않는다. Source/hash 또는 registry revision 변경은 영향받는 프로필을 재평가한다. 안전한 subset을 증명할 수 없으면 그 프로필의 전체 target을 다시 적용한다.

## Axis와 완료

Axis key는 `(item_id, axis_id, scope_ref)`다. `scope_ref`는 조사 context이지 use_context fact가 아니다. 같은 key의 contributor는 union하고 다른 context는 합치지 않는다. Required axes는 item scope의 acquisition 한 건과 적용 프로필들의 operation/effects/role/conditions union이다. 미정 프로필의 질문·가능 context·원인·next는 `pending_scope_refs`에 남는다.

각 axis는 질문 전체를 닫는 accepted result와 evidence를 요구한다. 기능 한 개나 fact 한 개를 발견했다고 더 넓은 질문이 닫히지 않는다. 일반 axis의 evidence-backed N/A는 explicit exclusion predicate와 범위 완전성이 필요하다. Acquisition에는 N/A가 없다.

```text
item_complete = scope_determined
                AND every_required_axis_terminal_under_its_contract
                AND acquisition_state == resolved
```

`scope_state`, `coverage_gap_state`, `item_investigation_state`는 별도 계산값이다. Scope determined에는 registry 전체의 routing 설명, pending/conflict 부재, gap assessment clear가 필요하다. 근거로 배제된 native scope에 별도 심층조사 blocker를 만들지 않는다. 미평가 gap을 clear로 읽지 않는다. Prose·S2·locale·문장 수·fact 개수는 이 함수의 입력이 아니다. 최소 fact·용도·문장 수가 없으므로 정보가 희소한 item도 적절한 terminal results를 갖추면 완료될 수 있다.

현재 application은 semantic results를 제출하지 않는다. 원본에 profile predicate를 적용한 것과 actual semantic/acquisition 조사를 완료한 것을 구별한다. Acquisition과 실제 의미 axes는 not_investigated로 남는다. Scope/gap의 investigated_unresolved는 어느 자료가 어느 질문에 부족한지 기록한다. `definition_gap`, `question_scope_extension`, `evidence_gap`, `uninvestigated`, `application_error`를 구별하며 unresolved 비율에 실패 임계값을 두지 않는다.

## 획득 결과 소비 경계

Resolver는 bound successor JSON의 `/semantic_node/allowed_fact_kinds`, `/semantic_node/bindings/acquisition_unobtainable`, `/acquisition/resolved_requires`를 해석한다. Missing/type/value mismatch는 오류이며 fallback하지 않는다. Current producer `none`/assignment `0`은 허용 kind 선언과 accepted instance가 다르다는 의미다.

미래 결과를 소비할 때 별도 명시된 adopted authority의 path/hash, accepted result membership, exact FullType/fact ID/provenance, whole-scope question coverage가 필요하다. Acquisition은 accepted acquisition 또는 admissible acquisition_unobtainable fact가 필요하다. Negative에는 그 authority가 채택한 closed scope·coverage completeness·false-negative 제한·subject·source binding이 필요하다. Resolver는 부족한 authority를 생성하거나 비준하지 않는다. G1의 미래 negative fixture는 합성 소비 사례일 뿐 실제 fact 채택이 아니다.

Terminal로 주장한 결과가 요건을 만족하지 못하면 오류다. 조용히 unresolved로 내려 성공시키지 않는다. Unresolved acquisition은 다른 context의 accepted facts나 first-contact obligation을 삭제하지 않는다. Acquisition 한 건만 해결되어도 나머지 scope/axis가 열려 있으면 item은 incomplete다.

## First-contact 사용법과 사례 판단

Confirmed context의 first-contact axes를 contributor와 함께 합친다. Accepted facts가 없더라도 질문 의무는 유지하고 표현은 deferred로 전달한다. Pending scope가 있으면 확정 subset을 전체 scope인 것처럼 취급하지 않는다. Menu에 상세가 있다는 이유로 첫 이해에 필요한 의미를 생략하지 않는다.

`Base.Dogfood`의 Food와 CantEat는 섭취 가능성과 현재 형태를 별도로 조사해야 하는 사례다. `Base.Apple`의 섭취 effects와 EvolvedRecipe가 여는 조리 role은 서로 대체되지 않는다. 모든 음식에 두 효과나 조리 역할이 있다고 가정하지 않는다. `Base.Hammer`는 native Weapon과 moveable tag가 서로 다른 질문을 열며, Recipe group signal은 원문 direct token 확인과 구별한다. `Base.Plank`의 원문 Recipe input과 keep는 대표 role을 하나 고르는 근거가 아니다. `Base.Notebook`의 Literature는 학습 효과 보장이 아니며 낮은 정보량을 문장으로 채우지 않는다. `Base.Battery`의 Drainable은 잔량 질문을 열지만 실제 기능과 획득 경로를 대신하지 않는다.

실제 application에서는 위 source 관찰과 잠재 scope, 필요한 의미 조사와 구체 gap이 함께 보인다. 기준 자체에 새 질문이 필요하면 기존 질문 범위의 확장인지 새로운 실질적 질문인지 명시하고 revision을 변경한다. 현재의 open direct question은 미분류 label을 출력하는 fallback이 아니라 추가 기능을 빠뜨리지 않기 위한 조사 요구다.

Global acquisition은 전역 필수 조사 축이며 모든 item의 first-contact 문장이 아니다. 어떤 profile이 acquisition first-contact를 추가하려면 질문·선정 이유·상세 경계가 필요하다. Axis마다 한 문장·한 줄을 만들거나 많은 축을 대표 fact로 축약하지 않는다. Actual fact binding, KO/EN, S2 문장/줄 구성과 omission tracking은 DVF-L3-05가 맡는다.

## 실행과 검증 범위

`iris-tooling build layer3 investigate`는 고정 investigation root의 evidence/application/manifest만 작성한다. Output 경로 옵션이나 composer/publisher 호출이 없다. 정의/human contract 수정은 작성 작업이며 source와 revision이 맞는 최종 subject를 만든 뒤 계획 §7의 G1 한 건으로 검증한다. 통상 mode는 현재 계약·application·readpoint를 검사하며 이번 채택 no-mutation 증거를 대신하지 않는다. `adoption` mode는 시작 baseline을 요구하고 알 수 없는 mode·누락·손상은 fail-closed한다.

G1은 schema·routing·axis/first-contact/completion·acquisition 소비 사례, 전체 application 한 번 재계산, 최종 결속·보호 대상과 관련 CLI dispatch를 확인한다. 별도 focused preflight, A/B apply, full suite, Lua syntax, package/PZ, 반복 confidence run은 없다. 임시 작성 helper와 baseline은 새로운 validator나 authority member가 아니다. 기계 검사로 문장 품질·실게임 이해도나 source 전수 정확성을 입증했다고 주장하지 않는다.
