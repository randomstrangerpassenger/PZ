# DVF description composition contract

문제 1의 `composition_results.read_result()`가 확인한 blocks를 소비하는 offline 표현 계약이다. 역사 r6는 보존한다. A의 `recovery_relations`가 기존 admitted observation에서 보완한 `use_relations`와 `source_traits`를 함께 소비한다. raw recipe나 기존 prose로부터 문장 조합기가 관계를 추론하지 않는다.

2026-09-11 용도 교정: 내부 accepted fact 보존과 공개 claim은 별개다. 아래 과거 세부 배치에서 전량 expanded 보존·관리 절차 출력을 요구하던 부분은 이 규칙으로 대체한다. `preserved_fact_refs`는 입력 사실 전체를 추적하고, `internal_uses`는 관리·처리 metadata·획득 분리 사유를 남긴다. 공개 `public_use` segment의 fact refs는 실제 용도·역할·결과 활용 claim만 가리킨다. 표현하지 않은 전체 실행 predicate를 그 문장의 qualifier refs에 붙이지 않는다. 미표현 근거를 무관한 문장 refs에 붙여 보존 검사를 통과시키지 않는다.

양말 등의 세척·패치 대상 관리, 조리자 기록, 세척 결과와 이동 중단은 DVF 용도가 아니다. 세척제의 몸/의류·장비 세척, 도구의 패치 기능, 변환 대상의 회수와 독립 제작 재료 용도는 유지한다. 획득은 의미 블록에 보존하고 기존 획득 공급으로 보내며 DVF 본문에는 넣지 않는다. 실제 독립 용도를 글자 수 때문에 숨기지 않는다.

개봉·손질·분해 관계는 exact 결과 정체성, 도구의 `any_of` 대안 집합/비소모, declared/무조건 callback/조건부 callback을 구별한다. 개봉 결과의 요리·파종 활용은 A가 이미 수락한 해당 결과 활용 fact가 있을 때만 연결한다. 결과의 다른 용도를 재귀적으로 복사하지 않는다. `Base.TinOpener`의 제품 명칭은 통조림 따개이며 기존 번역 깡통 따개와 동일한 아이템이다. 내용물 이름은 활성 EvolvedRecipeName의 공통 개념 어휘 또는 확인된 결과 표시명이며 FullType 접두사를 잘라 만들지 않는다. 미확정 어망 Result와 열쇠의 동적 일치/소모 구분은 유지한다.

## 입력과 내용 배치

`description_composition_planner.plan()`은 exact FullType별 branch의 사실과 정확한 qualifier application을 문장 단위로 옮긴다. context와 role은 같은 branch이며 조건 집합까지 같은 경우에만 한 주장으로 합친다. 조건이 다르면 context를 지시 대상으로만 이용하고 서로 다른 주장을 유지한다. 순서는 payload 기반의 표현 순서이며 중요도 순위가 아니다.

Compact는 기능/역할의 개요다. Expanded의 문장을 자르지 않고 같은 입력에서 따로 계획한다. 건축·목공·금속 가공처럼 활동을 알아볼 수 있는 이름과 실제 역할을 사용한다. 여러 제작 대상을 이름 없는 ‘해당 제작법’ 하나로 대체하지 않는다. 동일 역할의 여러 활동은 병렬화한다. 연료와 불쏘시개는 구분하고 점화 도구의 필요를 남긴다. 개별 화덕·공급 절차·소모 방식은 expanded에 둔다.

물품 자체의 세척·패치·이름 변경·수리 대상 역할, 적용한 붕대/부목 제거, 물의 세부 이동·잔량 합치기 및 기기의 보조 조작은 상세로 배치한다. 다른 물품의 패치에 쓰는 재료 기능은 이 유지관리 규칙으로 삭제하지 않는다. 키트·창·가구 부품처럼 구체적인 제작 결과와 수박 쪼개기라는 개별 가공 대상은 실제 expanded에 둔다. 다른 기능이 전혀 없는 제작 재료라면 모든 제작 역할을 compact에 남기며 대표 제작법 하나를 고르지 않는다. 이 배치는 다른 활동의 하위 의미라는 관계를 새로 선언하지 않는다.

효과/상태라는 종류만으로 compact에서 제외하지 않는다. 독서의 기술별 경험치 배율과 최대 배율, 물의 갈증 해소·오염수 음용 위험, 시비의 성장/부패 분기, 흡연가 여부에 따른 상반된 효과, 명시된 착용 위치는 compact에 남긴다. 음용의 중독/질병 수치 경계, 쪽수·진도 계산 간격, 조리자 metadata, 치료 계수·의료 경험치, 수량 계산, 조건부 치료 부작용과 장착 부품의 상태 변화는 상세다. 장비 세척의 결과는 입력의 명시적 result 관계가 있을 때 그 상세 기능과 묶는다. 정상 부재와 미구현 규칙 실패를 구분한다.

Compact의 기능 표현은 실제 수행 성공을 보장하지 않는다. 투척/근접 공격의 차량 밖 조건, 메모 편집의 필기구/잠금, 부목의 부위 제한처럼 표현의 의미를 바꾸는 제한은 짧은 어휘에도 남긴다. 상세의 exact qualifier 연결은 원래 적용 범위를 유지하며 개요를 근거로 확장하지 않는다. 장문/누락이 발견되면 공통 표현 규칙의 결함으로 수정한다.

## 대표 내용 배치

- 판자: 건축·금속 가공·목공의 재료 역할과 근접 공격, 부목 적용, 연료 역할을 compact에 남긴다. 수박 쪼개기의 도구 역할, 창·부목·덫·가구 부품·모닥불 키트 제작, 보존 도구 조건, 부목 계수/제거, 세척과 획득은 실제 expanded에 둔다. 재료 역할을 도구 역할로 바꾸거나 별도 제작 용도를 목공의 하위라고 선언하지 않는다.
- Notebook: 열람과 필기구/편집 잠금 조건이 있는 기록을 각각 짧게 표현한다. 페이지·제목 저장과 잠금 변경은 상세에서 서로 다른 조건으로 설명한다. 연료·불쏘시개 역할은 독립적으로 유지한다. 필기구 조건을 잠금 변경 전체에 붙이지 않는다.
- 의류: 명시된 착용 위치, 직물 회수 재료, 연료·불쏘시개 역할을 compact에서 구별한다. 세척의 피·때 제거/젖음, 패치 추가·제거, 획득은 상세다. 연료 경로별 의류 조건은 해당 상세에 붙이며 드럼에 모닥불의 필터를 확대하지 않는다.

예를 들어 판자의 compact는 “건축·금속 가공·목공에 쓰는 재료이며, 차량 밖 근접 공격, 머리·몸통 외 골절의 부목 적용에 쓰거나 연료로 소모할 수 있다.”이다. 재료/도구 활동과 용도 명사구를 같은 의미 단위에서 직접 조합한다. Hammer에도 같은 규칙을 적용하며 바리케이드 추가·철거의 목적은 개요에, 못·판자 반환 같은 절차는 상세에 둔다. 상세에서는 “가구 부품·부목 제작에 재료로 쓰인다. 이때 선택한 제조법의 재료·도구와 필요한 제작 지식을 갖춰야 한다.”와 같은 실제 문장을 읽는다.

Notebook의 compact는 “필기구 없이 메모를 읽을 수 있다. 쓰려면 필기구와 편집 권한이 있고 편집 잠금이 풀려 있어야 한다.”라는 기록 설명과 연료·불쏘시개 설명을 결합한다. 상세에서 잠금 변경의 즉시 적용/취소 비복원, 조작 접근에 필요한 필기구와 다른 사용자 소유 잠금 부재를 구별한다. 의류의 compact는 명시된 착용 위치와 직물 회수의 가위 조건을 유지하고, 상세의 실제 세척 문장은 피·때 제거와 젖음을 함께 설명한다.

연료와 불쏘시개를 함께 표현할 때는 “연료나 불쏘시개로 소모할 수 있으며 불쏘시개로 쓸 때는 점화 도구가 필요하다.” / “It can be consumed as fuel or as tinder with an igniter.”로 구성한다. 국소 조건이 다른 단위는 이 결합에서 제외하며 점화 도구 조건을 연료에 확대하지 않는다.

점화 기능은 공통 점화 목적 아래 실제 대상들을 합친다. 기능만으로 도구 역할을 추론하지 않으므로 휘발유 등도 포함하는 공통 문장은 “점화에 쓸 수 있다”로 쓴다. 대상마다 휘발유/불쏘시개를 되풀이하는 개요 대신, 대상별 수단·준비·소모 조건을 서로 분리된 expanded에 둔다. 이는 모든 대상에서 모든 점화 수단을 허용한다는 주장이 아니다. 같은 조건을 확인한 초 점화 도구 역할과 시신 점화 기능도 이 목적에 함께 표현한다.

물 용기는 보관·운반과 담긴 물의 사용 목적을 한 문장으로 구성한다. 작물 급수·차량 혈흔 세척·소화·갈증 해소 중 실제 입력에 있는 용도만 남기며, 오염수 음용의 중독 가능성은 별도로 표현한다. 작물의 파종/잔여 급수량, 소화 대상/소모량, 중독 수치 경계는 실제 상세에 둔다. 물 저장 시설 보충은 물 이동 절차로, 쌀·파스타 준비는 특정 제작 결과로 상세에 배치한다. 보관 기능이 없는 소화 도구에는 물 용기 개요를 적용하지 않는다. 예상하지 않은 추가 조건은 닫힌 개요 규칙에 흡수하지 않는다.

휴대 조명은 “손에 들거나 장착한 상태에서 휴대 조명을 조작할 수 있다.” / “It offers portable-light controls while held or attached.”로 실제 입력의 조작 기능을 표현한다. 실제 발광을 보장하지 않는다. 조명 자체의 점화·소화 제작법, 손에서 빼거나 버릴 때의 형태 변경은 상세이며, 다른 초에 불을 붙이는 도구 역할과 구별한다. 휴대 조명 조작 기능이 있는 물품의 활성화 토글·건전지 충전/삽입/제거는 그 조명의 운영 상세다. 전자 부품 회수의 직접 기능은 compact에 남기되 해당 조명 자체의 개별 분해 참여 역할은 상세로 둔다.

실제 최종 원문과 자체 검토 범위는 closeout 및 동일 `descriptions.json`을 사용한다. 고정 정답 문장이나 별도 승인 gate가 아니다. first-contact 조사 metadata는 사용하지 않는다.

## 문장 문법과 보존

KO는 받침에 따른 로/으로·이다/다와 공통 가능 서술어의 생략을, EN은 역할 명사의 관사와 병렬 동사구·주어 생략을 처리한다. 두 언어는 같은 의미 계획에서 독립 실현한다. 동일 문자열은 의미 동등성의 근거가 아니다. Expanded에서는 정확히 같은 qualifier 집합/역할에 대해서만 조건·역할 반복을 생략한다. 짧은 설명도 국소 조건을 가진 문장을 다른 조건의 문장과 기계적으로 병렬화하지 않는다.

`description_composition_families`는 입력의 실제 result edge를 확인한 뒤 독서–학습, 음용–갈증/독성, 시비–성장/부패, 흡연–특성별 효과를 조건부 문장으로 구성한다. 허용된 predicate 외 조건이 추가되면 닫힌 문장 규칙을 적용하지 않고 일반 조건 보존 경로로 돌아간다. 미확정 창낚시/마모는 이 경로로 합치지 않으며 “내구도가 감소할 수 있다”라는 독립 서술을 사용한다. 기존 어휘에 섞였던 창낚시의 마모 인과도 사용하지 않는다. 확인된 관계와 방향, 미확정 관계는 결과에 그대로 남긴다.

기존 `expression_rules`, `recovery_sources`, `recovery_expression`의 어휘 사전과 획득 표현 함수는 읽기 전용으로 참고한다. r6 완성 설명·first-contact inclusion·공백 수·producer는 사용하지 않는다. 기술적인 원본 predicate를 직접 사용자 문장으로 내보내지 않는다. 상세의 어휘 투영은 Layer 3 사용자 의미이며 레시피 원본의 모든 숫자/엔진 내부 절차를 번역하는 계약이 아니다. 정확한 실행 절차의 소유권은 Layer 4에 남으며 이번 문장의 상세 보존을 Layer 4 이관 완료로 확대하지 않는다.

## 결과와 reader

`Iris/build/description/composition/descriptions.json`의 schema는 `iris-layer3-descriptions-v1`이다. 각 item은 KO/EN × compact/expanded 상태를 제공한다.

- `present`: 정의된 내용을 실현했으며 원문이 있다.
- `absent`: 해당 표면의 채택된 내용이 없다.
- `failed`: 미구현/실현 실패 사유가 있다. 다른 locale·r6·빈 성공 문장으로 대체하지 않는다.

Segments에는 원문과 block/branch/fact/qualifier/relation refs, qualifier의 정확한 application을 둔다. 긴 qualifier 원문은 item의 `qualifiers`에 한 번 저장한다. 참조의 존재 자체는 문장에 조건 전체를 실현했다는 뜻이 아니다. Compact의 `qualifier_dispositions`가 `compact_core`(문장에 통합), `compact_summary`(짧게 실현), `expanded`(상세 배치), 실제 표현과 이유를 구분한다. 요약한 predicate의 실행 세부는 expanded에 남는다.

Compact의 `detail_links`는 같은 locale의 실제 expanded segment로 연결되며 expanded 실패 시 보존 완료로 표시하지 않는다. Item에는 관계와 방향 및 미확정 관계를 둔다. Input의 실제 hash와 generator/어휘 파일 hash는 식별 정보이며 봉인 authority가 아니다.

`description_composition_results.read_result(root)`는 저장된 JSON을 읽고 구조를 확인할 뿐 producer나 입력 reader를 호출하지 않는다. compact는 hard newline 없이, expanded는 scope별 문단으로 저장된다. 이는 실제 PZ 폰트/폭 적합성을 뜻하지 않는다. 최대 네 줄 요구를 유지하며 물리 표시 확인은 B의 후속 책임이다.

계획 §7의 집중 검사는 전체 결과 하나에서 입력 직접 대조·생성·저장·읽기를 공유한다. 자동 검사는 자연어 정확성 전체를 증명하지 않는다. 문제 3은 보존된 원문을 재생성 없이 검수한다.

## 2026-09-11 bounded expression correction

같은 exact qualifier application scope 안에서 명시적으로 검토한 predicate 쌍의 겹치는 표현을 합칠 수 있다. 현재 대상은 조리 자격/COOKING_ACTION, 독서 자격/READ_SELECTION, LOADING/AMMUNITION_LOADING_PATHS, PAINTING/PAINT_ACTIONS, MAKEUP_USE/MAKEUP_LIFECYCLE, 알약 소지/PILL_TAKING, CAMP_PLACEMENT/TENT_PLACEMENT다. 원래 qualifier refs와 applications는 그대로 남으며 문자열 일치만으로 predicate를 삭제하지 않는다. 각기 다른 적용 범위의 조건은 합치지 않는다.

Compact에서 명시한 미끼 조건은 core disposition으로 연결하고 낚시·독서·도색·화장의 공통 조건 요약은 검토된 predicate 쌍에 한해 한 번 표현한다. 독서 시작 값의 상한 효과는 입력에 있는 감정 속성만 같은 scope에서 병렬화한다. 창 제작 도구 마모의 실제 predicate가 제공하는 사용 맥락·보존 도구·1 감소를 실현하며 미확정 창낚시 마모와 합치지 않는다. 새 짧은 기능 frame도 허용 predicate 집합 밖 조건이 있으면 적용하지 않는다. 총기 조작의 빈 칸·용량과 같은 실행 상세는 같은 locale expanded에 남긴다.

이는 [Problem 3 partial 실행](iris_dvf_description_quality_acceptance_closeout.md)의 구현 계약이다. 전체 원문 품질 수락이나 accepted final corpus 인계 완료를 뜻하지 않는다.


## 2026-09-12 player-use successor (구현 중)

적용 계획은 `iris_dvf_player_use_description_transition_plan.md`이며 이 절은 이전 수락 subject를 수정하지 않는다. 새 producer는 모든 unit에 공통 공개 판단을 적용한다. 확인된 독립 활용은 길이나 primary-use 순위로 expanded에만 숨기지 않는다. 자기 관리·획득·내부 계산은 원래 facts/relations/qualifiers에 남지만 공개 문장에 자동 승격하지 않는다. 미구현 함수·조건은 failed이며 정상 absence가 아니다.

`public_plan`과 `internal_uses`는 composer의 선택 설명이다. 내부 처리한 qualifier의 `applies_to_fact_refs`는 원래 적용 대상에 한정하며 다른 공개 활용의 조건을 제거하지 않는다. 이는 기존 schema의 additive offline metadata이며 semantic fact authority나 validator를 신설하지 않는다.

공개 의미를 모두 실현한 닫힌 조건부 frame은 양 표면에서 재사용할 수 있다. 서로 다른 qualifier application을 문장의 모든 사실에 확장하지 않고 기존 개별 application 기록을 유지한다. Expanded로 조건 설명을 위임한 frame은 expanded에서 자체 위임을 충족한 것으로 재사용하지 않는다. 알려진 함수에 추가 조건이 붙으면 closed frame이 이를 삼키지 않고 해당 조건을 처리해야 한다.

기존 source adapter에서 admitted recipe와 실제 source module을 확인하여 제작 결과 이름을 연결한다. Callback은 명시적으로 검토한 결과 타입/수량 관계까지만 연결하며 실제 native 성공, 추가 회수품 또는 효과를 선언된 결과만으로 추정하지 않는다. 원래 r6/adoption과 semantic facts의 owner는 유지한다.

필요한 제한적 근거 보완은 기존 `recovery_sources` owner에서 수행한다. 현재 열린 우산의 선언과 실제 야외 채집 consumer로 보완한 facts는 `blocks.source.semantic_correction`에 source bindings·observations·provenance와 함께 보존한다. 기존 composition 모델이 같은 의미 identity 및 적용 범위를 검사하며 별도 검사기나 외부 semantic authority를 만들지 않는다. 원래 adopted payload는 그대로 보존하고 composition의 유효 입력에만 correction을 더한다. Composer는 원본 script/Lua 속성을 해석하지 않는다.

현재 구현 중이며 전수 의미 재판정·기존 최소 자동 검사·새 B/C 연결 전이다. 새 corpus/제품 수락은 기존 기록에서 승계하지 않는다.

### 명시적 용도 근거 보완의 최종 범위

2026-09-12 correction은 열린 우산 4종의 12 facts, 의약품 6종의 6 facts, 발전기의 2 facts로 한정한다. 의약품은 선언 Tooltip이 가리키는 vanilla Tooltip_EN의 명시적 목적과 기존 복용 consumer를 연결한다. 발전기는 Sandbox_EN의 야외 발전기 설명과 ISWorldObjectContextMenu의 실제 야외 주유기 조건을 연결한다. 공개 범위는 야외 사용 설정이 허용된 상태의 야외 주유기 급전이며 일반 실내·모든 가전·반경·native 계산으로 확대하지 않는다. 원래 29,202 facts(semantic 28,145 + acquisition 1,057)는 보존하며 유효 합계는 29,222다.

2026-09-12 실행 완료: 위 구현 중 표기는 당시 이력이다. 최종 descriptions `ffde6886d117482336159de49dd1ddc8ff075df2499217b09400542a895246b0`에 공통 규칙을 적용하고 전수 자체 검토 및 새 B/C 후보 검사를 마쳤다. 실제 PZ 미관찰로 implemented_only이며 상세 결과는 `iris_dvf_use_description_report.md`의 closeout에 있다.

## 2026-09-12 의미 판정 재개 — partial

후속 실제 원문 검토에서 공통 점화 frame의 내부 지원 문구, 도구 설명의 수행 요건 나열, 음식 미끼의 추상적 주어, 차량 부품 목적의 미확정 문제가 확인되었다. 위 ‘잔여 표현 결함 0 / 실제 PZ만 남음’ 판단을 철회한다. ledger의 읽기 이력과 자동 검사 결과는 보존하지만 의미 적합성 수락으로 사용하지 않는다. 기존 ffde6886... corpus와 run-7ztpp37i C ZIP은 당시 자동 검사 통과 후보이며 의미 품질 승인 후보가 아니다. 공통 규칙과 같은 의미/조합 범위를 교정하고 재판정할 때까지 partial이다.

## 2026-09-12 공통 목적군 교정 후 후보

재개 시 확인된 점화 주체·음식 미끼·복합 도구 목적군·중복 수행 요건을 공통 규칙으로 교정하고 실제 영향 범위를 재판정했다. 42개 차량 부품의 구체 기능 부족은 개별 purpose_unresolved로 기록한다. 포괄적인 결함 0 선언을 복원하거나 자동 검사 성공을 의미 품질 승인으로 사용하지 않는다. 누적 전수 자체 읽기/변경 범위 재판정의 상세와 한계는 `iris_dvf_use_description_report.md`의 최신 절 및 `review/uses/items.json`에 있다.

현재는 **implemented_only**: corpus `2301a4a4b8d24a28447ea53e3e47dd7143b362fb9e3b3b2531cf3152e4491e30`, B `.tmp/tooltip/run-cr4yy73j/s/.tmp/package/Iris.zip`, C `.tmp/menu/run-5b363prk/p/Iris.zip`(SHA256 `a55538e4cdaf47c771258a2c75d33dce0f93ba66cc524eb465873d1fa0086080`). 마지막 설명/B 묶음 exit 0(2 passed, 91.80s), 같은 B를 받은 C exit 0(1 passed, 72.08s). 실제 PZ는 미관찰이고 complete/독립 품질 승인/live 전환이 아니다. 과거 ffde 후보는 역사적 자동 검사 결과로만 남긴다.
