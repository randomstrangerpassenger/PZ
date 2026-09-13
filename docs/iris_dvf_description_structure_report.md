# Iris DVF 설명 구조 전수 조사

## 개정 요약 — 결과 산정·후속 상세로의 범위 확장

2026-09-12 추가 요청에 따라 **축 4: 현재 아이템의 활용에서 불필요한 결과 산정·후속 처리 설명으로 확장되는가**를 조사했다. corpus 두 입력 해시는 최초 조사와 동일하다. 기존 자료의 548개 원문 묶음을 새 기준으로 모두 읽고 KO/EN compact/expanded 8,420좌표에 대응했다.

**축 4 결함은 고유 ID 277개, 판단 보류 사례를 가진 ID는 38개다. 기존 세 축의 결함 869개 중 239개와 겹치며, 새로 38개가 추가되어 네 축의 결함 합집합은 907개다.** 보류 ID 38개와 새 결함 ID 38개는 숫자만 같고 다른 집합이다. 상세 집계·사례·원인·경계 반례는 이 문서 마지막의 「추가 조사 — 축 4」에 기록했다.

기존 세 축의 항목별 상태·이유·findings는 변경하지 않았다. JSON의 `history[0].summary`는 최초 집계, `axis4_review`는 추가 조사, 최상위 `summary`는 네 축의 현재 합집합이다. 각 좌표의 `axes.axis4.cases`에는 현재 주체, 원래 활용, 뒤에 붙은 설명 대상, 필요성 판단 이유와 실제 segment 및 source refs가 있다.

아래 최초 조사 기록의 **869개·세 축·보류 41개**는 당시 범위의 결과로 보존한다. 이를 현재 네 축의 전체 집계로 읽지 않는다. 추가 조사에서도 구현·재생성·테스트·새 계획/Gate·후보 생성은 하지 않았다.

## 최초 조사 기록 — 기존 세 축

조사일: 2026-09-12. 이 문서는 현재 문면의 구조 조사 결과이며 구현안, 새 검증 기준, authority 또는 품질 수락 기록이 아니다.

현재 2,105개 exact ID의 KO/EN compact/expanded **8,420좌표를 대조했다. 세 축 중 하나 이상의 결함을 확인한 exact ID는 869개**다. 축별로 맥락 묶음·순서 810개, L3/L4 경계 47개, 대상·상태 연결 82개이며 중복이 있다. 이 수치는 현재 문면에 대한 판단이다. 실제 PZ 화면의 가독성이나 모든 native 용도의 완전성을 판정한 수치가 아니다.

## 범위와 읽기 근거

`Philosophy.md`를 먼저 읽고, `ARCHITECTURE.md`의 L3/L4 구분 및 기존 전환 계획·용도 조사 보고서의 최신 상태를 참조했다. L3는 아이템의 확인된 목적·맥락·기능·상태·제약을 설명하고, L4는 개별 Recipe/Right-click/EvolvedRecipe 관계와 요건을 다룬다는 경계를 적용했다. 기존 보고서의 전체 품질 수락 철회, implemented_only 상태, 차량 42개의 목적 근거 부족은 그대로 별도 사안으로 남긴다.

| 조사 입력 | SHA256 |
| --- | --- |
| `Iris/build/description/composition/descriptions.json` | `2301a4a4b8d24a28447ea53e3e47dd7143b362fb9e3b3b2531cf3152e4491e30` |
| `Iris/build/description/composition/blocks.json` | `0c806c345cbe512129c8a4af27ecd85a965607d8feeb8d14587335a0ab6ccb03` |

네 최종 문자열이 완전히 같은 548개 묶음을 만들어 모든 묶음의 KO/EN compact/expanded를 직접 읽었다. 묶음에는 단일 ID도 있으며, 빈 문면 124개는 한 묶음이다. 긴 출력에서 잘린 구간은 다시 읽었다. 이후 각 exact ID의 네 최종 문자열과 ordered segment가 읽은 묶음과 같은지 대조했다. 언어·표면·family 이름만 같다는 이유로 판정을 전이하지 않았다. 동일 원문 묶음 내 segment 경계 및 현재 투영 알고리즘의 Menu unit 범위 차이는 없었다.

현재 `docs/review/uses/items.json`과 `docs/iris_dvf_description_review.html`의 after 네 표면도 descriptions와 전 좌표에서 일치했다. 이는 읽기 대상의 동일성 확인이며 의미 적합성의 증명이 아니다. 각 ID의 기존 source traits/use relations/uncertainty를 함께 대응시켰고, 대상 전환 사례에서는 변환 관계와 원물의 직접 활용을 구별했다. 전체 native 구현의 사실 감사를 다시 수행하지 않았다.

기록은 [항목별 JSON](review/structure/items.json)에 있다. `items`에는 exact ID 2,105개 각각의 네 원문, 순서 있는 segment, 축별 상태·이유, 양 표면 대응 판정, Menu unit 범위, 기존 불확실성과 L4 청크의 레시피 이름 추출 결과를 담았다. `findings`는 사람이 읽어 기록한 판정과 영향 exact ID를 대응한다. 코드는 읽기 묶음 구성·추출·전사·집계에만 사용했다. 키워드, 문장 수, refs 수 또는 자동 분류를 의미 판정으로 삼지 않았다.

## 집계와 상태의 의미

각 표면은 present 1,981개, absent 124개다. present 좌표는 7,924개, absent 좌표는 496개다. absent는 구조를 평가할 문면이 없다는 뜻으로, 목적 누락 결함 또는 적합 판정에 포함하지 않는다.

| 직접 좌표의 결함 확인 | KO compact | KO expanded | EN compact | EN expanded |
| --- | ---: | ---: | ---: | ---: |
| 축 1: 맥락 묶음·반복·순서 | 20 | 780 | 20 | 780 |
| 축 2: L3/L4 경계 | 0 | 47 | 0 | 42 |
| 축 3: 대상·상태 연결 | 69 | 82 | 69 | 82 |

compact↔expanded 대응 순서 결함은 KO 263쌍, EN 263쌍이다. 이 판정은 개별 좌표의 결함 수에 임의로 두 번 넣지 않고 `cross_surface`에 별도 기록했다. 축 1의 exact ID 합집합 810개에는 이 대응 판정을 포함한다. compact에 결함이 없더라도 expanded 또는 대응 순서에는 결함이 있을 수 있다.

| exact ID별 확인된 축 조합 | 수 |
| --- | ---: |
| 축 1만 | 741 |
| 축 2만 | 10 |
| 축 3만 | 48 |
| 축 1+2 | 36 |
| 축 1+3 | 33 |
| 축 2+3 | 1 |
| 축 1+2+3 | 0 |
| 확인된 결함 없음 | 1,236 |

마지막 1,236개에는 absent 124개와 present 1,112개가 함께 있다. 이들은 전체 품질 수락 항목이라는 뜻이 아니다. 판단 보류는 exact ID 41개이며 다른 축의 확인된 결함과 겹칠 수 있다. expanded에서 축 1 보류는 언어별 14좌표, 축 2 보류는 언어별 27좌표다.

상태를 명시적으로 구분했다.

- `defect_found`: 읽은 문면에서 해당 구조 결함 확인.
- `not_found_in_review`: 문면을 읽었으며 해당 축 결함 미확인. 미독, 자동 적합 또는 전체 품질 수락이 아니다.
- `judgment_held`: 필요한 구체성이나 연결 근거를 확정할 수 없어 판단 보류.
- `not_applicable_absent`: 문면 부재로 구조 축 적용 불가.
- `not_observed`: 실제 PZ UI 미관찰. 모든 ID에 별도로 기록했다.

## 축 1 — 플레이어의 활용 맥락과 출력 경계

여기서 결함은 문장이나 segment가 많다는 사실이 아니다. 동일 맥락의 활용·조건이 흩어지거나, 그 사이에 다른 맥락이 들어가거나, compact에서 잡은 활용 순서가 expanded에서 무너지는 경우다. 서로 다른 활용의 문단 분리와 compact의 짧은 용도 나열은 허용했다.

**양말과 의류.** `Base.Socks_Ankle`은 expanded가 연료, 불쏘시개, 착용, 직물 회수, 시트 로프 제작의 다섯 segment 및 다섯 Menu unit으로 나뉜다. 연료·불쏘시개가 같은 점화 맥락인데 분리되고, compact의 착용→재료 활용→연료 흐름과도 다르다. 각 사실을 보존하더라도 플레이어가 읽는 활용 묶음은 별도로 설계되어야 한다. 의류 전체에 이름만으로 전이하지 않고 실제 네 문면과 착용 상세·변환·직물 회수 관계가 같은 항목에만 판정을 대응했다.

**드라이버.** `Base.Screwdriver`의 compact는 전자기기, 목공·가구/건축, 차량·무기, 창·근접 공격 순으로 묶는다. expanded는 창 부착부터 시작하고 전자기기 분해→조명 개조→건축물 해체→무기→차량→타이머·원격 부품→가구 이동·간이 무전기→목공→공격 순이다. 전자기기 제작이 분해에서 멀어지고, “가구 이동·간이 무전기 제작”은 서로 다른 맥락을 한 segment로 묶는다. 10개 segment가 10개 Menu unit이므로 참조 독립성만으로는 원하는 문단 구조가 나오지 않는다.

**치료와 수선.** `Base.Needle`은 의류 덧대기와 패치 제거 사이에 매트리스 제작이 끼고, expanded의 시술자 혈액공포증 상세는 마지막으로 밀린다. `Base.RippedSheets`는 화상 세척, 부목, 붕대와 치료 조건이 연료·건축·의류·제작 설명 사이에 분산된다. 이들은 compact에도 실제 순서 문제가 있어 표시했다. 반면 compact의 모든 segment를 독립 문단으로 세지는 않았다.

**음식과 용기.** `Base.CannedMilkOpen`의 조리→작물 치료제→음용, `Base.WildGarlic2`의 조리→찜질제→섭취는 음식 활용으로 돌아오는 순서다. `Base.Bowl`은 compact에서 음식 분배와 조리 용도 사이에 물 보관이 끼며, expanded에서도 조리 용도가 여러 기능별 문장으로 분산된다. 구체 대상·조건을 지우기보다 해당 활용 옆에 놓을 필요가 있다.

**상세가 목적보다 먼저 나오는 경우.** `Base.SharpedStone`은 “창 제작에 사용한 깎인 돌은 잃을 수 있다”로 시작한 뒤 “창 제작·목공에 쓰는 도구다”라고 목적을 소개한다. expanded에서는 창 제작 상세에서 마모·소실을 다시 설명한다. 내용의 진위를 바꾸지 않고 목적과 그에 붙는 손실 설명의 위치·중복을 다룰 사례다.

`Base.SpearCrafted`와 부착 창 13개의 내구도 감소 문장은 축 1을 보류했다. 현재 생성 코드가 미해결 연결을 독립 진술로 유지하고 있으므로, 낚시 설명 옆에 붙이면 자연스럽다는 이유로 낚시의 결과라고 확정할 수 없다.

## 축 2 — 용도 식별에 필요한 구체성과 L4 목록

**버전별 제작 목록.** 드라이버 expanded의 다음 부분은 타이머·원격 조작 부품이라는 목적 뒤에 개별 결과를 재현한다.

> 타이머·원격 조작 부품 제작에 도구로 쓰인다. 제작 대상: 원격제어 조정기 (V2)·원격제어 조정기 (V3)·폭탄 타이머 (수제작)·원격제어 조정기 (V1)·원격 폭탄 격발기 (수제작).

EN도 `V2 Remote Controller, V3 Remote Controller, Crafted Timer, V1 Remote Controller, and Crafted Trigger`를 나열한다. 원격 조작과 타이머의 기능 차이는 남길 가치가 있지만 같은 조정기의 버전별 결과가 독립 목적은 아니다. 일부 폭발·발화 장치 5개는 KO만 V1/V2/V3를 남기고 EN은 작동 방식으로 묶여 있어 언어별 결함 수가 5개 다르다.

**레시피 수량 재현.** `Base.Pillow`, `Base.Needle`, `Base.Thread`, `Base.Sheet`의 expanded는 매트리스 용도 뒤에 보존하는 바늘과 실 5, 시트 5개, 베개 5개를 반복한다. 매트리스라는 결과명은 활용 식별에 필요하지만, 다른 재료의 전체 수량과 보존 여부를 각 L3 아이템 설명에서 재현하는 것은 제작법 수준이다.

**목록 표지가 다른 사례.** `Base.TinOpener`는 “꺼낼 수 있는 내용물:”/“Contents include” 뒤에 16종을 나열한다. 통조림을 여는 도구라는 목적과 별개로 지원 통조림별 결과 목록을 펼친다. `제작 대상:`만 검색하는 방식으로는 놓칠 사례다. 이어지는 음식 준비 문장도 닫힌 통조림에 캔 따개가 필요하다는 같은 도구 맥락을 다시 소개한다.

다음은 같은 방식으로 삭제할 대상이 아니다.

- `Base.CannedCorn`의 꺼낸 **옥수수**는 변환 결과와 조리 대상을 식별한다. 캔 따개의 16종 지원 목록과 다르다.
- 탄환 거푸집의 정확한 탄종, 순수 분해 설명의 회수 부품, 씨앗 봉지의 종자 이름·내용량은 무엇을 얻거나 쓰는지 구별한다.
- 금속판 전환의 결과 크기·손실, 화염병과 연료 상태, 원격·타이머·센서의 작동 방식은 독립 기능 또는 중요한 결과 차이다.
- 칼의 손질 대상인 동물·생선·개구리·빵 등의 실제 범위를 지우고 “제작에 사용”으로 일반화하면 용도 정보가 손실된다.

손질에 허용되는 여러 도구, 소독 재료의 구체 결과, 약초 습포제 종류, 일부 음식 제작 결과, 통나무 묶기의 수량·반환 규칙은 목록과 유용한 구체성의 경계로 보류했다. 특히 묶기 재료의 저장 기록과 기록이 없을 때 반환물은 실제 회수 결과를 설명하므로 단순 수량 금지로 지울 수 없다.

### 현재 L4에서 실제로 공급되는 범위

L3/L4의 개념적 경계와 지금 L4에서 exact ID로 접근할 수 있는 범위는 구별해야 한다. 현재 `UseCaseDescriptions/Chunk*.lua`의 exact ID별 레시피 이름을 전량 추출했으며, 아래 대표 사례는 청크 내용과 UI 공급 경로를 읽었다. JSON의 나머지 inventory는 추출 목록이며 모든 항목의 UI 접근을 직접 확인했다는 뜻이 아니다.

| exact ID | 현재 L4 청크에서 확인한 공급 | 해석 |
| --- | --- | --- |
| `Base.Screwdriver` | `Chunk006.lua:776`, screw_disassembly 행동과 `Attach Screwdriver to Spear` | L3의 원격 조정기·타이머 제작 목록이 이 아이템의 레시피 목록에 모두 있지 않음 |
| `Base.TinOpener` | `Chunk007.lua:522`, open_can 행동; recipe 이름 없음 | 개봉 행동은 있으나 16개 내용물별 레시피가 모두 제공된다고 할 수 없음 |
| `Base.Remote` | `Chunk006.lua:18`, 원격 조정기 V1/V2/V3 | 버전별 제작법을 L4로 식별하는 실제 예 |
| `Base.Pillow` | `Chunk005.lua:1581`, `Make Mattress` | 매트리스 제작법 관계가 존재 |
| `Base.Bread` | `Chunk002.lua:389`, `Slice Bread` | 원물→조각 변환 관계가 존재 |
| `Base.CannedMilk` | `Chunk002.lua:1045`, `Open Condensed Milk` | 통조림 개봉 관계가 존재 |
| `Base.TinnedBeans` | `Chunk007.lua`의 exact ID 항목, `Make Bowl of Beans`, `Open Canned Beans` | 원 통조림의 직접 레시피와 개봉 관계를 함께 보존해야 함 |

`IrisBrowserInteractionCollector.lua:1`은 QG-only Layer 4 수집이며 legacy capability/recipe-index 합성을 하지 않는다. `IrisItemDetailModelAssembler.lua:202`의 UseCases interactionState와 `:237`의 recipe index 연결은 별도 공급이다. `IrisWikiSections.lua:400`의 recipe section은 연결 개수 표현이며 누락된 레시피 상세를 채우는 경로가 아니다. 전역 `upstream_recipe_nav_registry.json`에 레시피가 있다는 사실도 드라이버의 exact ID 접근을 증명하지 않는다.

따라서 L3 목록 재현은 확인했지만, 이를 줄인 뒤 동일 정보를 현재 L4에서 모두 찾을 수 있다는 수락은 하지 않는다. 이 접근성 공백을 구조 조사 결과에 남기며, 이번 작업에서 QG나 L4 공급을 수정하지 않았다.

## 축 3 — 원물·내용물·변환 결과의 연결

**연유 통조림의 실제 원문.** `Base.CannedMilk` KO compact:

> 통조림 따개로 개봉해 꺼낸 연유를 요리 재료로 쓸 수 있다. 먹을 수 있다.

expanded는 첫 문장 뒤에 “도구는 소모하지 않는다.”를 붙이고 다음 segment로 “먹을 수 있다.”를 둔다. EN expanded도 `It can be opened ... to obtain Evaporated Milk ... The tools are not consumed.` 다음에 `It can be eaten.`을 둔다. 꺼낸 내용물, 원 통조림, 방금 언급한 도구 사이에서 후속 활용의 대상이 명시되지 않는다. 이것은 문장의 사실 보존 여부와 별개인 대상 연결 결함이다.

개봉 관계와 원물에 붙은 native 섭취 사실은 따로 존재한다. 자연스러운 문장을 만들기 위해 임의로 개봉 필수 조건을 모든 섭취/레시피에 추가해서는 안 된다. 필요한 것은 확인된 사실의 주체와 상태를 명시적으로 연결하는 것이다. 병조림 일부, 달걀 포장과 분배 음식에서도 같은 문제를 원문별로 기록했다.

**옥수수 통조림에는 예시를 그대로 전이하지 않았다.** 현재 `Base.CannedCorn` compact는 “통조림 따개로 개봉해 꺼낸 옥수수를 요리 재료로 쓸 수 있다.”뿐이다. expanded는 도구 비소모 설명만 추가한다. 뒤따르는 “먹을 수 있다.”가 없고 현 source row에 같은 native 섭취가 공급되지 않으므로 연유의 결함을 이 ID에 복제하거나 먹기 문장을 추가할 근거가 없다.

**빵과 손질 음식.** `Base.Bread` 등은 변환 결과와 익힘/탄 상태를 먼저 제시한 뒤 생략 주어 또는 `It`으로 원물의 섭취·요리·미끼 활용을 잇는다. 원물에 귀속된 미끼의 익히지 않음 조건이 앞의 조리된 분할 결과에 걸리는 것으로 읽힐 수 있다. 손질 결과명, 원물의 직접 활용, 각 상태 조건의 적용 대상을 구별해야 한다.

**비음식 변환.** 빈 병은 깨진 병을 얻는 설명 뒤에 원래 병의 물·연료 보관 또는 화염병 재료 활용으로 돌아간다. 탄약은 분해해 얻은 화약 뒤에 원 탄약의 포장·장전이 이어진다. 리모컨·손전등·이어폰/헤드폰·시계 일부는 분해 부품 뒤에 원 기기의 활용으로 돌아간다. 순수 분해→회수만 있는 기기는 후속 전환이 없으므로 같은 결함을 일괄 적용하지 않았다.

부착 창 13개는 expanded에서 부착물과 반환한 제작 창을 말한 뒤 근접 공격·내구도 감소의 대상을 명시하지 않는다. 이 대상 혼선은 축 3으로 기록하지만, 내구도 감소가 낚시의 결과라는 해석은 보류한다. `Base.TinnedBeans`도 원 통조림의 직접 레시피와 개봉 결과 활용이 공존하므로 모든 용도를 개봉 뒤로 옮기는 교정은 정당화되지 않는다.

## 생성·투영·표시 단계의 책임

1. **원문 순서와 묶음 생성.** `description_composition_planner.py:35`는 block/branch/fact ID로 순회하고 `:76`은 canonical payload와 fact refs로 unit을 정렬한다. 이것은 안정적인 출력 순서지만 플레이어의 활용 맥락 순서를 보장하지 않는다. `description_composition_uses.py:315`의 의류 묶기는 compact에만 적용된다. `description_composition_results.py:57` 이후는 uses frame 뒤에 remaining을 붙이고 supporting detail만 있는 segment를 뒤로 보낸다. 조건·활동/role별 묶음과 이 후행 배치가 같은 맥락 분산에 기여한다.
2. **목록과 대상 연결 생성.** `description_composition_results.py:161` 이후는 결과명을 모아 `:171`에서 제작 대상 목록을 붙인다. `description_composition_uses.py:504` 이후는 개봉 도구의 내용물 목록을 만든다. 같은 파일의 변환 frame은 개봉 결과의 조리 활용을 연결하지만 별도 원물 섭취 사실까지 자동으로 같은 대상으로 연결하지 않는다. 따라서 문단 간격만 바꿔도 L4 열거·주체 혼선은 남는다. `description_composition_results.py:145`의 창 내구도 예외는 미해결 연결을 독립 진술로 보존하는 제약이다.
3. **최종 문자열의 경계.** `description_composition_results.py:409`는 compact segment를 공백으로, expanded segment를 줄바꿈으로 연결한다. compact 내부 segment 경계는 화면 문단 경계가 아니다. 이번 집계도 이 차이를 반영했다.
4. **Menu unit 투영.** `product_projection.py:118` 이후는 segment refs의 교집합, separate_block_refs 및 관계 span으로 연속 구간을 자른다. `:147`의 unit은 기존 segment를 줄바꿈으로 연결하며 의미상 재정렬·통합하지 않는다. 참조가 독립적이라는 사실과 독자가 다른 맥락으로 읽는다는 사실은 다르다. 반대로 같은 unit 안에도 여러 원문 줄바꿈이 남는다. 예를 들어 제작 창은 4개 segment가 1개 unit이다.
5. **조회와 모델.** `IrisLayer3DataLookup.lua:14` 이후 product 경로는 현재 pointer/index/chunk를 조회하고 text/blocks/units의 연속성을 확인한다. `layer3_renderer.lua:165`의 getDisplay는 locale payload의 text·units를 전달한다. `IrisItemDetailModelAssembler.lua:121` 이후는 이를 모델에 보관하며, 전체 display 문자열은 unit 사이를 두 줄바꿈으로 연결한다. `IrisWikiSections.lua:73`은 이미 만들어진 units를 순서대로 꺼낸다. 이 경로에는 플레이어 맥락을 재판정하는 기능이 없다.
6. **화면 간격과 자동 줄바꿈.** `IrisBrowserDetail.lua:290`은 첫 unit 뒤 unit마다 7 간격을 두고 Medium/18로 그린다. `IrisWikiPanel.lua:121`은 unit별 Small/22와 7 간격을 쓴다. `IrisTextLayout.lua:44` 이후는 명시적 줄바꿈을 보존한 다음 폭에 맞춰 줄을 감싼다. legacy 경로의 `IrisLayer3DisplayFormatter.lua:57`은 긴 원문 줄을 문장 쌍으로 나누기도 하지만, product units 경로에서는 그 formatter를 거치지 않는다.

이 코드 경로는 원문 segment, Menu unit, 자동 줄바꿈, unit 간 여백을 구별하는 근거다. 현재 corpus에서 추출한 unit 범위가 실제 사용 중인 게임 후보와 같다고 관찰한 것은 아니다. HTML after와 원문이 같다는 사실도 Browser/Wiki의 폰트·여백을 재현했다는 뜻이 아니다. “구분선이 안 보인다”, “네 물리적 줄에 들어간다”, “좁은 폭에서도 읽힌다”는 실제 화면 판정은 이번 조사에서 하지 않았다.

## 공통 교정 방향과 남는 한계

조사 결과가 가리키는 방향은 목적을 먼저 두고 그 목적의 대상·조건·결과를 인접하게 연결하는 것이다. compact에서 묶은 활용 순서를 expanded에서도 따라갈 수 있어야 한다. 발화 수단과 적용 장소, 치료 부위와 재료, 원물과 반환물 같은 차이는 남기면서 동일 맥락의 반복을 합칠 필요가 있다. 서로 다른 활용을 “도구”, “재료”라는 문법 역할이 같다는 이유로 묶어서는 안 된다.

L3에는 실제 목적 범위를 식별하는 결과명·대상·상태 차이를 남기고, 같은 목적 아래 개별 레시피 수량·버전·지원 항목을 펼치는 부분을 구별해야 한다. 이 구별은 키워드 삭제나 모든 고유명사 축약으로 대체할 수 없다. L4 접근성이 비어 있는 항목은 그 공백을 함께 고려해야 한다. 대상 연결은 원물의 직접 용도와 변환 결과 활용을 구분해 표현하되 근거 없는 선행 조건을 만들지 않아야 한다.

위 내용은 공통 방향이며 개별 최종 문구나 구현 단계·Gate를 새로 정한 것이 아니다. 실제 PZ 실행, KO/EN 폰트·해상도/UI scale, Tooltip 물리적 줄수, Browser/Wiki 좁은 폭·스크롤·Layer 4 접근은 미관찰이다. 기존 차량 42개 목적 근거 부족과 corpus의 전체 native 용도 완전성도 이번 세 축 판정으로 해소하지 않았다.

테스트, corpus 재생성, 새 후보 제작, QG/authority 수정, 배포, commit/push를 수행하지 않았다. 추출·전사 보조 Python 실행을 테스트 성공으로 보고하지 않는다. 기존 dirty/deleted/untracked 작업을 보존하고, 결과물은 이 보고서와 항목별 JSON으로 남겼다.

## 추가 조사 — 축 4

### 질문과 판정 범위

사용자의 추가 지적은 양말에서 천을 회수할 수 있다는 활용 이후, “회수되는 직물의 종류와 양은 옷의 구성·오염·재봉 상태에 따라 달라진다”는 설명이 붙는 경우였다. 이는 그 계산의 진위가 아니라 **현재 아이템의 용도를 이해하는 데 그 상세를 공개해야 하는가, 누구의 설명인가**라는 문제다.

현재 아이템 → 확인된 활용/획득 결과 → 부가 상세를 차례로 읽었다. 부가 상세가 다른 결과물의 속성·품질·수량 산정, 기술·오염·확률 요인, 일반 처리 규칙으로 넘어가면서 추가 용도 차이를 알려주지 않으면 결함으로 기록했다. 현재 아이템 자체의 사용 중 손실, 정확한 결과 정체성, 확정/조건부 반환의 구분, 재사용 도구와 소모 재료의 구분은 별도로 판단했다. 어떤 segment에 결함이 있다고 해서 그 segment의 모든 사실을 삭제 대상으로 삼는 것은 아니다.

기존 축 2와 축 4도 구별했다. 매트리스의 투입 수량·드라이버 버전 목록·캔 따개의 내용물 목록은 기존 L3/L4 경계 판정을 유지하되, 목록이라는 이유만으로 축 4 결함을 복제하지 않았다. 반대로 씨앗 포장의 “제작법이 정한 종류와 수량을 모아 포장”은 결과 이름의 문제가 아니라 활용 이후에 붙는 일반 처리 지침으로 새 축에서 확인했다. 입력 식재료의 사용 가능 조건과 결과 산정의 경계가 불명확한 경우는 보류했다.

### 동일성·전수 읽기·이력

조사 시작 시 descriptions SHA256 `2301a4a4b8d24a28447ea53e3e47dd7143b362fb9e3b3b2531cf3152e4491e30`, blocks SHA256 `0c806c345cbe512129c8a4af27ecd85a965607d8feeb8d14587335a0ab6ccb03`로 최초 기록과 같았다. 따라서 corpus 변경분은 없다.

기존 exact ID/동일 원문 관계를 재사용하고 548개 전체 묶음의 네 표면을 새 축으로 읽었다. 중복 segment는 이번 읽기에서 먼저 읽은 정확한 원문을 참조하되 각 묶음의 표면별 순서와 조합을 읽었다. 서로 다른 segment 원문은 1,542개였다. 출력이 잘린 G324–353은 별도로 다시 읽었다. 기존 JSON 각 ID의 text와 ordered segment를 현재 descriptions에 대응했으며 차이는 없었다. 이 작업은 세 사례만 확인한 표본 조사가 아니다.

항목 기록에는 최초 세 축의 판정과 기존 불확실성을 그대로 두고 각 좌표에 `axis4`를 추가했다. 새 finding 번호는 `STR4-001`부터 `STR4-020`까지이며 기존 `STR-*` 번호와 분리했다. 최초 두 산출물의 개정 전 해시와 최초 summary도 JSON history에 남겼다. 원문 자체·원천 사실·기존 authority를 고치거나 전체 native 사실 감사를 다시 수행하지 않았다.

### 새 축 집계와 중복

| 축 4 직접 좌표 상태 | KO compact | KO expanded | EN compact | EN expanded |
| --- | ---: | ---: | ---: | ---: |
| 결함 확인 | 2 | 277 | 2 | 277 |
| 판단 보류만 있음 | 1 | 36 | 1 | 36 |
| 읽었으나 새 축 결함 미확인 | 1,978 | 1,668 | 1,978 | 1,668 |
| absent — 적용 불가 | 124 | 124 | 124 | 124 |
| 합계 | 2,105 | 2,105 | 2,105 | 2,105 |

compact 결함 2개는 `Base.Wrench`의 회수량 확률 설명과 `Base.Needle`의 패치 반환 산정 설명이다. 나머지 확인된 축 4 결함은 expanded에만 있다. 축 4는 직접 문면의 범위 확장을 조사하므로 compact↔expanded 순서 결함 수를 별도로 추가하지 않았다.

축 4 판단 보류 사례가 있는 고유 ID는 38개다. 그중 `Base.Fork`, `Base.Spoon` 2개는 다른 segment에서 축 4 결함도 확인되어 expanded 좌표 대표 상태는 결함이며, 해당 `cases`에는 보류를 함께 남겼다. 그러므로 expanded의 보류만 있는 좌표는 36개다. 최초 세 축과 합친 보류 고유 ID는 73개이며 결함 합집합과 상호 배타적이지 않다.

| 축 4 결함 ID와 기존 축의 교집합 | 수 |
| --- | ---: |
| 기존 축 1과 겹침 | 219 |
| 기존 축 2와 겹침 | 21 |
| 기존 축 3과 겹침 | 19 |
| 기존 세 축 중 하나 이상과 겹침 | 239 |
| 기존 세 축 밖에서 새로 확인 | 38 |

교집합 세 행을 합하면 중복된다. 축 4 결함 277개를 배타적인 조합으로 나누면 다음과 같다.

| 확인된 축 조합 | 고유 ID 수 |
| --- | ---: |
| 축 4만 | 38 |
| 축 1+4 | 199 |
| 축 2+4 | 1 |
| 축 3+4 | 19 |
| 축 1+2+4 | 20 |

기존 축 1/2/3의 고유 수는 각각 810/47/82로 변하지 않았다. 현재 네 축 합집합은 **869 + 277 − 239 = 907개**다. 새 38개 exact ID 전체 목록은 JSON의 `axis4_review.summary.new_item_ids`에 있다. 총 2,105개 중 확인된 결함이 없는 1,198개에는 absent 124개가 포함되며, 전체 품질 수락을 의미하지 않는다.

### 실제 사례 — 무엇이 누구의 설명으로 넘어가는가

| 사례 / finding | 현재 아이템의 활용 | 뒤에 붙은 설명 대상 | 새 축 판단 |
| --- | --- | --- | --- |
| 양말·의류·가위, `STR4-013` — 195 ID | 현재 의류를 찢거나 가위로 직물을 회수 | 회수 직물 종류·양과 옷 구성·오염·재봉 상태의 산정 관계 | 결함. 천 회수, 가위 필요성, 조건부 실 회수와 계산 요인을 구별 |
| 전자기기·디지털 시계·드라이버, `STR4-011` — 19 ID | 분해해 전자 부품 회수 | 회수 부품을 결정하는 기기·기술 요인 | 결함. 구체 부품 이름은 유지 가능 |
| 판자·나뭇가지·창 제작 도구, `STR4-009` — 8 ID | 창 제작에 사용 | 완성된 창의 상태와 목공 기술·확률 | 결함. 현재 도구의 마모/소실과 결과 창 품질 계산을 구별 |
| 창에 부착되는 도구 `STR4-002` — 13 ID; 창·테이프 `STR4-014` — 2 ID | 제작한 창에 부착 | 결과 상태와 입력 창·부착 무기 상태 | 결함. 부착 활용 이후 결과물 상태의 결정 요인으로 확장 |
| 부착 창, `STR4-015` — 13 ID | 부착물 및 제작 창을 회수 | 반환 창 상태에 대한 입력 상태의 영향 | 결함. 파괴된 창 허용·함께 반환하는 창은 별도 유지 가능 |
| 렌치, `STR4-001` | 엔진에서 예비 부품 회수 | 회수량의 확률 변동 | 결함. 엔진 소진 결과까지 같은 이유로 제거하지 않음 |
| 바늘, `STR4-008` | 의류 패치 제거 | 반환 재료와 재봉 수준·확률 | 결함. 재료를 돌려받을 수도 있다는 조건부 회수는 보존 가능 |
| 수리 재료·수리 활용을 가진 물품, `STR4-003` — 20 ID | 호환 손상 물품의 수리에 사용 | 결과가 fixing rules에 따른다는 일반 결정 규칙 | 결함. 구체 활용 차이 없이 처리 체계의 설명으로 넘어감 |
| 톱·드라이버, `STR4-012` — 3 ID | 건축물 해체·재료 회수 | 회수량 변동 | 결함. 회수 자체와 일반 수량 변동을 구별 |
| 토치, `STR4-004` | 파손/소실 차량 분해 | 확률에 따른 회수 재료 변동 | 결함. 결과 산정의 사실성을 부정하지 않음 |
| 토치·용접 가면, `STR4-007` — 2 ID | 용접 작업에 사용 | 다른 투입물인 금속판 전환의 재료 손실 | 결함. 금속판 자신의 설명과 도구의 설명은 귀속이 다름 |
| 종자 7종, `STR4-010` | 현재 씨앗을 대응 봉투로 포장 | 레시피가 정한 종류·수량을 모으라는 일반 처리 지침 | 결함. 봉투 결과 이름과 실제 포장 내용량의 공개 필요성은 별개 |

표의 ID 수는 finding별 영향 범위이며 서로 겹치므로 합산하지 않는다.

양말 expanded의 실제 문제 절은 다음과 같다.

> 찢어 직물을 회수하는 재료다. 회수 재료와 양은 옷의 구성·오염·재봉 상태에 따라 달라진다.

> It is material for recovering fabric by ripping. Recovered material and amounts depend on garment construction, contamination and tailoring state.

첫 문장은 현재 양말의 활용이다. 두 번째 문장은 그 활용에서 생성되는 직물의 산정 요인을 설명한다. `착용 / 재료 활용 / 연료·불쏘시개` 같은 소제목을 붙여도 이 두 번째 문장의 공개 필요성은 달라지지 않는다. 소제목과 본문의 설명 범위는 별개이며, 이번 조사에서는 소제목 UI나 고정 taxonomy를 만들지 않았다.

전자기기에서도 “드라이버로 분해해 전자 부품을 회수”한 뒤 “회수 부품은 기기와 기술에 따라 달라진다”가 붙는다. 이는 리모컨의 “건전지도 나올 수 있다”와 다르다. 후자는 어떤 추가 결과가 확정이 아닌지를 구별한다. 전자는 결과 구성을 결정하는 일반 요인을 소개한다. 드라이버 문장의 “회수 대상: 전기 회로 부속”까지 일괄 삭제할 근거로 삼지 않았다.

용접 가면과 금속판의 차이도 귀속을 보여 준다. 금속판 자체를 다른 크기로 바꾸는 활용에서는 재료가 손실된다는 정보가 현재 아이템의 변환 비용을 식별한다. 가면을 용접에 쓴다는 설명에서 갑자기 큰/작은 금속판의 손실로 넘어가는 것은 다른 대상의 변환 상세다. 최초 조사에서 금속판 손실을 유지할 수 있다고 본 사실을 모든 도구의 동일 문장에도 공개해야 한다는 결론으로 전이하지 않았다.

### 필요한 상세의 경계와 보류

다음 정보는 새 축에서 일괄 금지하지 않았다.

- **결과 정체성:** 탄약 상자의 정확한 탄종, 분해해 얻는 센서·증폭기·전기 부품, 개구리를 손질해 얻는 고기, 통조림의 내용물은 무엇을 얻는지 설명한다.
- **조건부 결과와 비용:** 리모컨의 조건부 건전지 회수, 소모되지 않는 드라이버, 돌/날붙이의 마모·소실, 낚싯줄 파손 시 원 낚싯대·미끼 손실, 설치물 회수 중 파손은 활용을 선택할 때 중요한 차이다. 세부 산정 요인을 붙일 필요성과 별개다.
- **현재 포장 내용량:** 종자 봉투의 씨앗 50개는 이 포장을 열면 무엇이 얼마나 있는지 식별한다. “제작법이 정한 수량을 모아야 한다”는 일반 절차 문장과 다르다.
- **확인된 제한적 연결:** 꺼낸 옥수수를 조리 재료로 쓸 수 있다는 연결, 씨앗 봉지를 열어 해당 종자를 파종한다는 연결은 활용을 설명한다. 원물·결과물의 주체와 상태를 유지해야 하며, 사용자 예시를 근거 삼아 현재 corpus에 없는 섭취 사실을 자동 추가하지 않았다.
- **기능 결과의 중요한 차이:** 설치한 모닥불이 아직 불붙은 상태는 아님, 물을 담는 것이 정수는 아님, 지도에서 알려진 영역과 방문 기록은 다름, 책의 직접 경험치 배율 효과는 무관한 결과물 관리로의 이탈과 다르다. 시청·청취를 통한 조건부 학습 효과도 기기/매체 활용의 목적을 설명하므로 기술·조건 단어가 있다는 이유만으로 결함으로 세지 않았다.

보류 사례는 달걀곽의 신선도 비회복 1개, 통나무 묶음 3개와 통나무·로프류 3개, 채소 병조림 관련 보존 기간 15개, 오믈렛 입력 달걀의 신선도별 잔량 조건 6개, 어망의 정확한 확인 대기시간 1개, 타이어 장착 뒤 공기·상태 저하 9개로 총 38개다.

통나무를 풀면 저장된 결속 재료가 돌아오거나 기록이 없을 때 밧줄이 돌아오는 차이는 현재 회수 활용을 구별한다. 같은 문장에 묶기 수량·저장 기록 처리까지 포함되어 있어 필요한 반환 차이와 처리 상세를 분리하지 않고 전체를 결함으로 확정하지 않았다. 달걀 신선도/병조림 보존 기간도 결과물 속성이지만 잘못된 보존 기능을 기대하지 않게 하는 중요한 한계일 수 있어 보류했다. 입력 달걀의 잔량 요건은 결과 산정이 아니라 사용 가능 조건일 수도 있으므로 기존 레시피 상세 축과 구별했다.

타이어 9개는 설치 뒤 운영·관리로 넘어가는 설명과 중요한 사용 중 손실의 경계로 보류했다. 이것은 기존 차량 목적 근거 부족을 해결했다는 뜻이 아니다. 창의 “내구도가 감소할 수 있다”도 낚시 또는 공격 결과로 새로 귀속하지 않았다. 새로 확인한 것은 부착/회수 문장 안의 명시적인 결과 상태 산정이며, 기존 미해결 관계는 남는다.

### 공통 생성 원인과 책임 경로

다음 경로를 현재 저장소의 공통 생성 코드와 실제 segment/source refs에 대조했다. 원천 사실을 새로 조사하거나 정확한 근거의 삭제를 요구하는 결론은 아니다.

| 경로 | 확인한 자동 확장 |
| --- | --- |
| `Iris/tooling/src/iris_tooling/domains/layer3/description_composition_uses.py:825` | material 역할의 fabric recovery frame이 FabricType을 보고, expanded이면 `:832`에서 직물 종류·양 산정 문장을 붙인다. 현재 양말에 공개할 필요를 다시 판단하는 조건은 없다. |
| 같은 파일 `:493`, `:649` | 전자기기 분해 frame과 분해 도구 frame에서 expanded에 기기·기술별 회수 부품 변동을 붙인다. 전자 부품의 구체 결과명과 산정 설명이 같은 문면에 들어간다. |
| 같은 파일 `:275`, `:277` | frame에 허용하는 qualifier 집합에 직물 회수 및 창 부착의 source predicate를 포함한다. source scope 연결의 존재와 그 상세의 공개 필요성은 다른 판단이다. |
| 같은 파일 `:950`–`:968` | internal 또는 일부 무관한 금속판 전환을 거른 뒤 남은 qualifier는 지원되는 문구가 있으면 `supporting detail`로 보존한다. 금속판 결과가 관계에 존재하는지는 살피지만 현재 아이템이 금속판인지 용접 도구인지에 따른 서술 귀속까지 해결하지 않는다. |
| `description_composition_lexicon.py:360`–`:365` | 포장 종류·수량, 수리 결과 규칙, 직물 회수 산정, 패치 회수의 재봉·확률이 각각 public qualifier 문구에 함께 들어 있다. 가위 필요성/조건부 실 회수처럼 유지 가능한 부분과 산정 부분이 한 문자열에 결합된다. |
| 같은 lexicon `:473`, `:670`–`:673` | 창 회수·제작·부착과 엔진 회수의 공개 문구가 정확한 원천 계산을 요약해도 상태·수량 산정 요인 자체는 남긴다. 수식을 생략했다고 현재 아이템의 목적 설명 범위에 들어오는 것은 아니다. |
| `description_composition_results.py:57`, `:161` | frame과 remaining을 합치고, 남은 qualifier를 `qualifier_clauses`로 문구화해 핵심 절 뒤에 붙인다. supporting-only segment를 뒤로 옮기는 것은 위치 조정이며 붙은 상세의 필요성 판단을 대신하지 않는다. |

원천 `recovery_sources.py:1474`–`:1475`에는 직물의 덮는 부위·재봉·오염과 조건부 실 회수, `:1533`–`:1540`에는 창 결과 상태 산정, `:2352`에는 엔진 회수량 산정이 기록되어 있다. 이 근거는 사실 관계를 보존할 자료다. 그 모든 계산 요인을 L3에 요약해 공개해야 한다는 결론은 따르지 않는다. `description_composition_lexicon.py:410`은 등록된 공개 문구를 선택하며 자동 원천 문장 fallback을 하지 않으므로, 문제는 무분별한 raw source 유출만이 아니라 **이미 채택된 공통 공개 문구의 범위**에도 있다.

현재 UI는 투영된 원문과 unit을 받아 표시한다. 따라서 소제목·여백·unit 묶음을 바꾸는 것만으로 원문 내부의 결과 산정 문장은 없어지지 않는다. 이번 결과는 공통 frame과 qualifier의 공개 필요성·대상 귀속을 다룰 필요를 설명하며, FullType별 문구 패치나 원천 facts 삭제를 제안하지 않는다.

### 개정의 한계

새 축에서도 `not_found_in_review`는 실제 문면을 읽고 이 축 결함을 확인하지 못했다는 뜻이다. 최초 조사에서 미확인인 문장도 새 기준으로 읽었지만, 다른 축의 결론이나 원천 사실의 진위를 재수락하지 않았다. 실제 게임 실행·UI 관찰은 없고, 원본 전체 사실 감사·차량 목적 근거 해결·QG 수정·추가 후보·새 proof/validator는 수행하지 않았다. 추가 작업은 두 기존 산출물의 조사 기록 개정이며, 별도 계획·Gate·소제목 구현·다른 작업 지시·감독 자동화를 만들지 않았다.


## 2026-09-12 공통 생성 규칙 교정

이 절은 위의 조사 기록 이후 실제 생산 규칙을 고친 결과다. 위의 907개 발견과 보류는 당시 입력의 조사 기록으로 보존하며, 현재 산출물의 합격 수치로 재해석하지 않는다. 현재 상태는 **implemented_only**다. 최종 product 명령은 종료 코드 0이며, 실제 PZ 관측은 없다.

### 적용 범위와 생성 경계

전체 2,105개 아이템, KO/EN compact/expanded 8,420좌표에 같은 생성 경로를 적용했다. 각 언어·표면은 present 1,981개, absent 124개다. 차량 목적 근거가 불충분한 42개, 기존 미해결 관계와 exact ID L4 공급 공백은 해결했다고 판정하지 않는다.

- 합성기는 현재 아이템의 역할·활동·확인된 변환 관계로 독립 용도를 구성한다. 같은 source branch의 활동과 그 역할은 중복 설명하지 않으며, 같은 문법적 역할만으로 서로 다른 작업을 합치지 않는다.
- compact에 실제 서술한 목적 순서를 expanded가 공유한다. 전자기기 제작/분해와 조명 개조, 목공/건축/가구 작업, 차량/무기 부품 작업 등의 내부 순서와 음식/반죽/미끼, 미용 작업 순서를 맞췄다. 새로운 대분류나 아이템별 문구 패치는 만들지 않았다.
- expanded의 `use_units`가 항목 경계를 소유한다. 메뉴 두 표면은 해당 경계의 첫 줄에만 글머리표를 표시하고 줄바꿈된 문장에는 다시 붙이지 않는다. 문자열 안에는 글머리표를 저장하지 않으며 UI에서 마침표로 항목을 추측하지 않는다.
- tooltip은 별도 compact 공급 경로를 유지한다. expanded를 이어 붙이지 않으며 Alt의 최대 네 실제 줄과 L2/DVF compact/획득/무작위 L4 역할은 기존 계약으로 검사한다.
- 기존 A 관계 어댑터에 원본 표시명과 ClothingRecipesDefinitions의 재료 결과를 연결했다. 면·데님·가죽과 이름으로 지정된 천의 실제 결과명은 원본 정의와 기존 ItemName/DisplayName에서 읽는다. 오염된 결과 가능성은 기존 recipecode의 조건과 해당 결과 선언에 연결한다. 이 정보는 표현의 의미 입력이며, 기존 facts가 그대로라는 사실을 품질 보증으로 사용하지 않는다.

### 실제 문면 변화

| 사례 | Before에서 고친 문제 | 최종 After의 핵심 |
| --- | --- | --- |
| Base.Bowl | compact의 여러 조리 절차, 다른 투입물의 상태/도구 지침과 물의 일반 관리 지침 | compact 두 문장으로 요리·반죽 준비, 음식 분할 수용, 물 보관/운반을 요약. expanded는 네 용도 항목. |
| Base.Socks_Ankle | 직물 결과 산정 상세, 원물과 회수 재료의 주체 혼동 | compact는 천 조각이라는 상태 공통 재료명과 독립 가능한 사용을 두 문장으로 표현. expanded는 찢어진 천/찢어진 천(오염됨)을 명시하고 양말 자체의 로프 재료 용도를 구분. |
| 데님·가죽 의류 | 직물이라는 추상 결과와 깨끗한 결과 단정 위험 | compact는 데님 조각/가죽 조각, expanded는 실제 깨끗한/오염된 결과명을 사용. 가위 요건은 해당 찢기 용도에 유지. |
| Base.TinnedBeans | 도구 미소모 상세와 원물 요리의 추상 표현 | 개봉해 꺼낸 콩의 요리 재료 용도와 콩 통조림으로 그릇(콩)을 만드는 직접 용도를 구분. |
| Base.Bread | 원래 음식 자체라는 반복, 모호한 부정 범위 | 빵과 빵 조각의 주체를 구분. 미끼 조건은 ‘익히지 않고 다른 재료와 섞지 않은 상태’로 두 부정을 명확히 표현. |
| Base.Screwdriver | 전자기기 회수량·버전 목록·차량 작업 실패 상세 | 실제 목적별 11항목. 전자기기 제작/분해→조명→목공/가구/건축물 분해→차량/무기→창 부착→근접 공격. |
| Base.Nails / Base.Rope | 같은 건축 용도의 반복 | 같은 활동의 역할을 묶어 반복 제거. |
| Base.FishingRodBreak | 활동과 재료 역할을 별도 문장으로 두 번 설명 | 같은 source branch의 한 용도로 합성하고 원래의 수리 필요 조건 적용 범위는 보존. |

빵의 ‘맞는 손질 도구 / A suitable cutting tool’는 확인되지 않은 임의 도구를 추가한 표현이 아니다. 기존 admitted `food_portioning` 관계가 `any_of`로 지정하는 도구는 Base.BreadKnife, Base.ButterKnife, Base.FlintKnife, Base.HuntingKnife, Base.KitchenKnife, Base.Machete, Base.MeatCleaver다. 이 확인 범위를 L3에 일곱 이름으로 반복하지 않고 요약했으며, 아무 칼이나 허용한다거나 한 종류가 필수라는 주장으로 넓히지 않았다.

### 검토 방법과 남은 불확실성

초기 전체 문면의 713개 KO/EN 절 쌍과 변경 후 문면을 직접 읽었고, 현재 아이템 이름 차이는 실제 이름을 읽은 뒤 순서 대조에서만 치환해 532개 목적 순서 조합을 비교했다. 검토 중 원물/음식 쟁반의 주체 오류, 언어의 수 일치, 용접·목공·미용 순서, 음식 용도 사이의 미끼 삽입, 건축 중복을 찾아 공통 규칙에서 수정했다. 마지막 감독 피드백에 따른 의류 compact의 독립 용도 연결과 상태 공통 재료명, 미끼 부정 범위도 실제 생성 문면에서 확인했다. 동일 문면 묶음은 읽기를 돕기 위한 것이며 별도 authority나 자동 의미 품질 Gate가 아니다. 모든 아이템의 기존 source context, 불확실성, L4 기록은 `docs/review/structure/items.json`에서 그대로 볼 수 있다.

최종 입력과 네 표면의 실제 Before/After는 기존 `docs/iris_dvf_description_review.html`과 JSON의 `correction.after`에 있다. 새로운 HTML은 정적이며 각 아이템의 KO/EN compact와 생산 단위별 expanded를 모두 제공한다. 자동 계약 검증이 문면 품질이나 인게임 한 줄 가독성의 수락을 대신하지 않는다.

Base.Screwdriver의 L4에는 screw_disassembly와 Attach Screwdriver to Spear가 있지만 타이머/원격 부품 제작 전체 공급은 아직 없다. Base.TinOpener의 open_can은 실제 통조림 제작법 전체를 대신하지 않는다. Base.Pillow의 Make Mattress 항목 존재와도 구분한다. L3에서 상세를 덜었다고 이 exact ID L4 공백이 메워지지는 않는다. 위 조사에서 보류한 보존/신선도/반환/타이어와 미해결 창 마모 관계도 새 인과관계로 확정하지 않았다.

실제 PZ 실행, 설치, 폰트·창 폭·Alt 한 줄 가독성 관측은 수행하지 않았다. 저장소 외부 설치·배포·커밋·푸시는 하지 않는다.


### 최종 검증과 후보

최종 후보: `.tmp/menu/run-59pojnio/p/Iris.zip`  
product: `l3p-3664178e9cad7b58a342eb627abcc1098fcbc1786c596fe472527e882c9a3673`  
ZIP SHA-256: `df519ce8100d6177cd65078ad2bed789973e81a59410dbe17dbc32987b4eaf5c`  
descriptions SHA-256: `dac08223e284b66ee7aa0d6f41bcc05b84ef553beff4118a621ce15de920d080`  
blocks SHA-256: `8688d865d78bba75ee0fdf52d8336dc067f44043c334e6984b0f935021acd5c7`

최종 재개 명령은 아래와 같고 종료 코드 **0**, `1 passed in 41.99s`다.

```powershell
$env:IRIS_MENU_TOOLTIP_CANDIDATE='.tmp/tooltip/run-92z356al/s/.tmp/package/Iris.zip'
$env:IRIS_MENU_RESUME_PACKAGE='C:\Users\MW\Downloads\coding\PZ\.tmp\menu\run-59pojnio'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\structure-final-0912e -q -s --tb=short -x
```

| 실행 | 실제 결과 | 사용한 결과/수정 |
| --- | --- | --- |
| 합의한 block/description/S2/product 네 노드 묶음, basetemp structure-final-0912a | exit 1, 2 passed / 1 failed | block/description 노드는 성공 기록. S2 입력 SHA 불일치에서 중단. producer를 import한 뒤 수정한 임시 생성 명령의 순서 오류를 고쳤다. |
| description/S2/product, structure-final-0912b | exit 1, 1 failed | expanded 검사에 compact의 새 일반 재료명을 잘못 기대한 테스트를 수정. |
| description/S2/product, structure-final-0912c | exit 1, 2 passed / 1 failed | 최신 description와 S2 노드는 성공. 동일 후보의 Lua 검사에서 과거 Lipstick 한 항목 기대값이 실패. |
| product 재개, structure-final-0912d | exit 1, 1 failed | 후보 경로를 절대 Windows 경로로 전달해 기존 상대 경로 계약에서 거절. 저장소 상대 `/` 경로로 수정. |
| 동일 product 재개, structure-final-0912e | exit 0, 1 passed | 아래 실제 실행 검사 및 ZIP/복구 검사를 완료. |

실패한 묶음 전체를 PASS로 바꾸지 않았다. block 노드의 성공 기록은 같은 blocks SHA와 동일 생산 입력 경계에 대해 유지했고, 최신 description/S2의 성공 기록은 변경되지 않은 최종 설명 입력과 해당 B 후보에 대해 유지했다. 최종 기존 resume 경로는 동일 manifest의 owner/producer 바인딩을 확인하고 기존 두 빌드와 stage를 재사용한다. 이로써 이미 완료한 생성·동일 바이트 비교를 다시 수행하지 않았다. 전체 네 노드 명령이 한 번에 종료 코드 0이었다는 주장은 하지 않는다.

Lua 문법 검사는 실제 `powershell -NoProfile -ExecutionPolicy Bypass -Command "& .\tools\check_lua_syntax.ps1 -Roots @(\"Iris/media/lua\", \".tmp/menu/run-59pojnio/s/Iris/media/lua\")"`로 원본/후보 388개 파일을 검사해 exit 0이었다. 재개 시 해당 원본/후보 파일은 변하지 않아 이 결과를 재사용했다. 수정한 harness 자체는 다음 Lua 실행에서 읽고 실행했다.

최종 실행에서 Browser/Wiki 실제 소비 코드 4,210상태 검사, 툴팁 2,280 exact keys 및 legacy call 0 검사, L4 밀도 harness, 패키지 입장 거절 사례, 패키지 생성, ZIP 추출본 포인터 및 메뉴 검사 모두 종료 코드 0이었다. 툴팁 출력의 Fixture.Layout fit failure 네 줄은 작은/큰 화면의 거절 동작을 주입한 테스트이며 해당 harness는 exit 0으로 끝났다. 두 번의 빌드 바이트 일치, B payload 106개 보존, 중단/rollback/idempotence 및 원본 pointer 보존은 동일 product 계약 안에서 확인했다.

Lipstick 기대값을 1에서 2로 바꾼 의미 근거는 ‘입술에 호환 화장 적용’과 ‘등록된 착용 분장 제거’가 서로 다른 실행 목적이라는 점이다. 첫 항목은 적용의 자체 조건을, 둘째 항목은 제거의 접근 조건을 유지한다. 단순 출력 개수 맞추기가 아니다. 같은 기존 UI harness에서 두 소비자의 글머리표 수가 생산 항목 수와 같음을 확인해, 긴 문장이 줄바꿈되어도 글머리표가 다시 생기지 않도록 검사했다.

최종 JSON에는 모든 아이템의 `correction.after`, 검토 상태, 후보와 실제 검사 결과를 기록했다. HTML은 최신 692개 정확한 네 표면/단위 조합을 전체 2,105개 아이템별로 제공한다. 결과는 **implemented_only**이며 설치·실행을 통한 PZ 시각 수락은 남아 있다. 추가 confidence 검사, 전체 Run A/B, 별도 Gate/proof 산출물을 만들지 않았다.


## 2026-09-12 미용 문면 후속 교정

앞 절 후보의 구현 검사 결과는 보존한다. 이후 감독 검토에서 미용 설명의 내부 용어와 행동 지침이 남아 있음을 확인했으므로, 앞 절의 문면 교정 완료 판단을 이 범위에 그대로 적용하지 않는다. 이번 변경은 Base.Lipstick, Base.MakeupEyeshadow, Base.MakeupFoundation의 공통 문형에 한정한다. 이번 후속 교정은 **implemented_only**로 완료했다. 아래의 기존 세 노드 묶음은 종료 코드 0이다.

실제 생성 텍스트의 변경 대상은 세 아이템, KO/EN compact/expanded 12좌표다. Base.Mirror의 별도 문형과 나머지 아이템 텍스트는 변경하지 않았다. 거울 문면은 이번 검토 범위 밖이며 새 수락으로 해석하지 않는다.

| 아이템 | KO compact | KO expanded의 두 항목 |
| --- | --- | --- |
| Base.Lipstick | 입술 화장을 하거나 화장 메뉴에서 화장을 지우는 데 쓴다. | 입술 화장을 할 수 있다. / 화장 메뉴에서 선택한 화장을 지울 수 있다. |
| Base.MakeupEyeshadow | 눈 화장을 하거나 화장 메뉴에서 화장을 지우는 데 쓴다. | 눈 화장을 할 수 있다. / 화장 메뉴에서 선택한 화장을 지울 수 있다. |
| Base.MakeupFoundation | 화장을 하거나 화장 메뉴에서 화장을 지우는 데 쓴다. | 화장 무늬를 적용할 수 있다. / 화장 메뉴에서 선택한 화장을 지울 수 있다. |

| 아이템 | EN compact | EN expanded의 두 항목 |
| --- | --- | --- |
| Base.Lipstick | It can be used to apply lip makeup or remove makeup through the makeup menu. | It can be used to apply lip makeup. / It can remove makeup selected in the makeup menu. |
| Base.MakeupEyeshadow | It can be used to apply eye makeup or remove makeup through the makeup menu. | It can be used to apply eye makeup. / It can remove makeup selected in the makeup menu. |
| Base.MakeupFoundation | It can be used to apply makeup or remove makeup through the makeup menu. | It can be used to apply a makeup design. / It can remove makeup selected in the makeup menu. |

등록·호환·접근이라는 내부 표현, 거울의 층/거리/벽 차단과 차량/파운데이션 예외, 사용량 미소모, preview 복구 설명은 이 세 아이템의 공개 L3 문장에서 제거했다. 기존 MAKEUP_USE/MAKEUP_LIFECYCLE predicate와 그 적용 관계는 그대로 남는다. 화장 적용과 화장 메뉴에서 선택한 화장 제거라는 두 목적을 유지하며, 아무 착용물이나 모든 화장을 무조건 제거한다는 의미로 넓히지 않았다. 파운데이션에는 현실의 밑화장 효과를 덧붙이지 않았다.

합성기의 해당 공개 frame만 `public_use`로 표현하며 실행 조건을 전부 설명한 것으로 연결하지 않는다. 소스 block/fact/관계나 UI 경계는 바꾸지 않았다. 이전 ZIP `.tmp/menu/run-59pojnio/p/Iris.zip`은 보존하고, 기존 review JSON의 correction_history에 이전 후보/검사 결과, makeup_correction.before에 세 아이템의 직전 문구를 남겼다. HTML과 correction.after는 새 문구로 갱신했다.


### 미용 교정의 최종 검사 결과

이번 문구 변경으로 무효화된 기존 description/S2/product 세 노드만 실행했다. `IRIS_SHARED_MENU_VALIDATION=1`로 기존 묶음 안의 중복 Lua 검사를 공유하고, 이전 후보 resume나 후보 경로 환경변수 없이 새 후보를 만들었다. 다음 명령은 **exit 0, 3 passed in 145.91s**로 완료했으며 이번 묶음에 실패는 없었다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\makeup-final-0912a -q -s --tb=short -x
```

새 최종 후보는 `.tmp/menu/run-7y3whpg4/p/Iris.zip`이다.

- product: `l3p-ff9f13833897b9d82c21e9c4c9949e3072371aa5bd4bf799ab1d58461d37e2c6`
- ZIP SHA-256: `0436b75033fe6595b0ad2b539a73f61b8f96087f43eb28f89145aff583f4ae32`
- descriptions SHA-256: `798075477bf25ed2afd3a09883ff0beaa39744e946faa61591d2d493b4bf508c`
- blocks SHA-256: `8688d865d78bba75ee0fdf52d8336dc067f44043c334e6984b0f935021acd5c7` (이번 생산 입력/경계 변경 없음)

세 노드 안에서 새 후보의 두 빌드 바이트 일치, 원본/후보 Lua 388파일 문법 검사, Browser/Wiki 4,210상태와 글머리표/unit 경계, 툴팁 2,280 exact keys/legacy call 0, L4 harness, 패키지 입장 검사, ZIP 생성과 추출본 포인터/메뉴 검사, 중단·rollback·idempotence·원본 pointer 보존을 확인했다. Lua 문법·메뉴·툴팁·L4·패키지·ZIP 포인터의 실제 하위 명령도 각각 exit 0이었다. 툴팁 Fixture.Layout 네 fit failure 출력은 기존 거절 사례 테스트로 해당 명령은 exit 0이다. 기존 block 노드는 이번 범위에서 무효화되지 않아 반복하지 않았다.

앞 절의 이전 성공 후보와 실패/재사용 기록은 그대로 보존했다. 최신 Before/After는 `docs/iris_dvf_description_review.html`과 `docs/review/structure/items.json`의 correction.after이며, 세 화장품의 직전 Before는 makeup_correction.before에서 볼 수 있다. 추가 confidence 검사, 전면 재검토, 새 Gate는 수행하지 않았다. 실제 PZ 실행/설치/가독성은 여전히 미관측이며 결과는 **implemented_only**다.


## 2026-09-12 식품 미끼 문면 및 기존 후보 로딩 조사

사용자가 후보 폴더를 모드 폴더로 옮겨 설치했지만 통조림 설명이 그대로라고 보고했다. 미설치라고 추정하지 않는다. 기존 `.tmp/menu/run-7y3whpg4/p/Iris.zip`의 실제 Lua 테이블을 읽어 Base.CannedCorn/Base.CannedMilk/Base.TinnedBeans의 KO/EN compact와 expanded를 현재 descriptions 및 review correction.after와 대조했다. 세 항목 모두 일치했다. 이는 후보 데이터에 대한 확인이며 실제 PZ 적용 성공 판정은 아니다.

| 아이템 | 기존 후보의 KO compact 본문 |
| --- | --- |
| Base.CannedCorn | 통조림 따개로 개봉해 꺼낸 옥수수를 요리 재료로 쓸 수 있다. |
| Base.CannedMilk | 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 연유를 요리 재료로도 쓸 수 있다. |
| Base.TinnedBeans | 통조림 따개로 개봉해 꺼낸 콩을 요리 재료로 쓸 수 있다. 콩 통조림으로 그릇 (콩)을 만들 수 있다. |

**조사 중 표현 정정:** '이전 설명 데이터가 함께 있다'는 보고는 파일명/헤더를 보고 한 잘못된 분류이므로 철회한다. ZIP의 `Iris/media/lua/client/Iris/Data/UseCaseDescriptions/Chunk002.lua`에는 `[레시피] 옥수수 통조림 열기`, `[레시피] 연유 통조림 열기`가 있고, Chunk007.lua에는 `[레시피] 그릇에 콩 담기 `와 `[레시피] 콩 통조림 열기`가 있다. 이는 별도 L4 상호작용 목록으로 활성 소비되며 구버전 L3 본문이 아니다. L4의 lookup 장애 시 전체 facade fallback은 L4 데이터 내부에서만 작동한다.

실제 후보의 Alt 경로는 `IrisAltTooltip` → `IrisTooltipStaticDataLookup.open` → `IrisTooltipStaticData`/`IrisTooltipRecipeVariants`다. 구 UseCase 본문이나 L3로의 fallback은 없다. Browser는 `IrisBrowserDetail` → `IrisWikiSections.getLayer3Units` → DetailViewModel/Assembler → `layer3_renderer.getDisplay` → `IrisLayer3DataLookup.getLocale`로 이어진다. Wiki는 `IrisWikiPanel`에서 같은 getLayer3Units 이후 동일 경로를 쓴다. 메뉴 pointer는 `IrisLayer3DataCurrent` → `IrisLayer3ProductCurrent` → `l3p-ff9f13833897b9d82c21e9c4c9949e3072371aa5bd4bf799ab1d58461d37e2c6`의 Descriptor/Index/Chunks다. 통조림 최신 본문은 Chunk002(Corn/Milk) 및 Chunk009(Beans)에 있다. successor 오류는 fault/빈표시로 반환하며 이전 본문을 되살리지 않는다. legacy getEntry의 router 미로드 fallback이 존재하지만 product lookup 오류에는 isProduct로 차단되고, 후보의 compatibility facade 역시 동일 pointer를 참조한다. IrisTooltipSummary는 후보 내 다른 Lua에서 참조되지 않으며 현재 Alt 경로가 아니다.

ZIP 루트는 `Iris/mod.info`와 `Iris/media`이며 바로 옆 `.tmp/menu/run-7y3whpg4/p/Iris`의 파일 바이트도 ZIP과 일치했다. 이 Iris 폴더가 모드 루트이고 p 폴더 자체가 모드 루트는 아니다. 외부 설치 폴더는 조사하거나 수정하지 않았다. 코드에는 최초 require/lookup의 세션 유지가 있으나 캐시/중복 모드/실행 중 파일 교체를 실제 원인으로 확인한 것은 아니다. 기존 독립 Lua 검사는 실제 PZ 모드 선택·경로 우선순위·세션 캐시를 확인하지 못한다. 실제 통조림 ID/화면 문구/설치 mod.info 경로에 대한 사용자 응답 전에는 적용 실패 원인을 확정하지 않는다.

식품 교정은 공통 supply_trap_bait 공개 문형의 실제 소비 350개 아이템에 한정했다. KO/EN compact/expanded에서 '익히지 않고 다른 재료와 섞지 않은 상태'/ 'while uncooked and unmixed with other ingredients' 절차 문구를 제거하고 미끼 용도를 짧게 독립시켰다. Apple compact는 `먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.` / `It can be eaten or used as a cooking ingredient. It can also be used as trap bait.`이며 expanded는 먹기/조리 재료/미끼의 세 용도를 유지한다. Bread의 기존 주어 재지정은 유지한다. 소스 facts/eligibility/상태는 보존하며 미끼 용도를 삭제하거나 조리 결과에 새 용도를 전파하지 않는다. Egg의 오믈렛/포장 조건처럼 다른 공개 문형의 조건은 그대로다. 위 통조림 세 항목의 본문과 섭취 사실은 변경하지 않았다. 직전 후보와 검토 이력은 보존하고 food_bait_correction.before에 변경 아이템의 직전 문구를 기록했다.


### 식품 교정 최종 결과

기존 영향 범위 세 노드만 다음 명령으로 실행했고 **exit 0, 3 passed in 159.43s**였다. source block 생산자는 변경하지 않아 이전 성공 결과를 유지하고 반복하지 않았다. 전체 Run A/B나 추가 Gate/확신 검사는 수행하지 않았다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
Remove-Item Env:IRIS_MENU_RESUME_PACKAGE -ErrorAction SilentlyContinue
Remove-Item Env:IRIS_MENU_TOOLTIP_CANDIDATE -ErrorAction SilentlyContinue
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\food-bait-final-0912a -q -s --tb=short -x
```

- 새 후보 ZIP: `.tmp/menu/run-f58qne0f/p/Iris.zip`
- ZIP 옆 모드 루트: `.tmp/menu/run-f58qne0f/p/Iris` (`mod.info`와 `media`가 직접 들어 있는 폴더)
- product: `l3p-8b7c3f4d3facf6ba9846fb8716e1ecf7be0e116f97271bcd84c9ce84ef15f3e0`
- ZIP SHA-256: `79013c9aa998c57467773e0e85573469d0789b9604b0210562f18902481ed39b`
- descriptions SHA-256: `52df97180c22dbec6f8506004ca9d72d9ec2aeabf9d4571deef771c566a1fbe1`
- blocks SHA-256: `8688d865d78bba75ee0fdf52d8336dc067f44043c334e6984b0f935021acd5c7` (변경 없음)
- B tooltip product: `ttp-6503d93d2d92a9000fe9eb2f0d6691e6d6706676e385d44126ae3058a2fa3d79`

기존 세 노드 내부에서 두 빌드 바이트 일치, 원본/후보 Lua 388파일 문법, Browser/Wiki 4,210상태·unit 경계, 툴팁 2,280 exact keys 및 legacy_calls 0, L4 모델, 패키지 입장·ZIP 추출본 포인터, 중단·rollback·idempotence·원본 pointer 보존 하위 명령이 각각 exit 0이었다. Fixture.Layout 네 fit failure는 기존 의도된 거절 사례 출력이며 해당 명령은 exit 0이다. 검토 HTML과 JSON correction.after는 최신 문구로 갱신했으며 692개의 정확한 문면/단위 조합을 유지한다. 결과는 **implemented_only**다. 사용자 보고에 대한 실제 PZ 적용 문제는 별도 미확정이며 이 검사 통과로 부정하지 않는다.


## 2026-09-12 통조림 전체의 개봉 후 섭취 누락 교정

사용자가 실제로 본 당근 통조림 문구는 Base.CannedCarrots2의 최신 후보 문구와 일치했다. 그러므로 해당 사례는 설치 오류의 증거가 아니라 **최신 문구 자체에서 개봉 후 섭취가 누락된 사례**다. 이전 'Corn 등 섭취 근거 없음' 판정은 닫힌 원물의 섭취와 개봉 결과의 섭취를 혼동했으므로 명시적으로 철회한다. 닫힌 통조림 자체에 eat fact가 없어도 정확한 개봉 레시피의 결과가 먹을 수 있는 식품이면 '개봉해 내용물을 먹을 수 있다'는 관계 설명이 가능하다.

원인은 description_composition_uses의 개봉 frame이 현재 원물의 eat_food/consume_edible_food만 선택하고 결과의 섭취를 보지 않은 것이다. recovery_relations는 결과 ID를 알고도 요리 재료 용도만 전달했다. Base.CannedCarrots2의 결과 Base.CannedCarrotsOpen에는 채택된 native_eating/eat_food fact `121c651b…`가 있고, scripts/items_food.txt L130-L156의 Type=Food/EatType=can 및 ISInventoryPaneContextMenu/ISEatFoodAction이 provenance다. CannedMushroomSoupOpen에도 같은 native_eating 근거와 items_food.txt L186-L211 선언이 있다. 결과 이름 Mushroom Soup/버섯스프를 Mushroom/버섯으로 줄이지 않는다.

조사는 이름 검색으로 범위를 확정하지 않고 scripts 전체의 item 선언 CannedFood=TRUE, 병조림 OnCooked=CannedFood_OnCooked, 실제 개봉 레시피의 입력·결과·도구와 병 개봉 callback을 등록 아이템/관계에 대조했다. CannedFood 38개 모두 현재 등록되어 있으며 닫힌19개/개봉 결과19개다. 병조림9개도 포함해 조사 대상은 **47개**, 개봉 관계는 **28개(통조림19+병조림9)**다. 병조림의 정확한 원재료 결과9개도 연결해 확인했다. 이 구조 범위에서 개봉 frame에 진입하지 못한 통조림이나 미확정 개봉 관계는 발견되지 않았다. 빈 캔과 캔 모양 물통은 식품 통조림으로 추정해 포함하지 않는다.

실제 문면 수정은 **18개 ID, KO/EN compact/expanded 72좌표**다. 동일 누락이 없는29개는 개봉 상태19개, 병조림9개, 기존 내용물 섭취를 이미 표현한 CannedMilk1개다. 이번 개봉 후 섭취 누락 조사에서 보류는0개이며, 기존 전반적 원천 불확실성이나 다른 용도 정확성까지 수락한 뜻은 아니다.

A 관계 어댑터가 정확한 선언 결과의 소비 fact 및 적용 qualifier 전체를 result_consumption으로 보존한다. 새 원물 eat fact를 만들지 않으며 결과 소비 근거의 item ID를 결과와 검증하고 조건도 원래 결과와 정확히 대조한다. 전달은 unpack_canned_food의 단일 확정 결과 섭취에 한정한다. 해당19개 결과의 먹기17/마시기2와 소비 조건을 확인했고, 모두 기존 CONSUMING(인벤토리·동반물품·포만/칼로리 시작 조건) 범위다. 공개 개봉 문형은 이 알려진 실행 조건을 추상화하며 추가 조건이 있으면 자동 전달하지 않는다. 결과의 미끼·작물 치료·다른 레시피 용도는 전이하지 않는다. CannedMilk는 기존 원물 소비 표현을 우선해 중복하지 않는다. Dogfood에는 근거 없는 조리 용도를 추가하지 않고, Sardines/CornedBeef/Tuna의 도구 없는 개봉에는 따개를 강제하지 않는다.

아래는 이번 범위 전체의 상태/관계/수정 여부다. 닫힌 상태의 결과 섭취는 개봉 뒤 내용물을 주어로 하며, 개봉 상태의 자체 섭취와 구분한다.

| 등록 ID | 상태와 정확한 개봉 결과 | 이번 문면 |
| --- | --- | --- |
| Base.CannedBellPepper | 병조림 → Base.BellPepper | 동일 누락 없음 |
| Base.CannedBolognese | 닫힌 통조림 → Base.CannedBologneseOpen | 교정 |
| Base.CannedBologneseOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedBroccoli | 병조림 → Base.Broccoli | 동일 누락 없음 |
| Base.CannedCabbage | 병조림 → farming.Cabbage | 동일 누락 없음 |
| Base.CannedCarrots | 병조림 → Base.Carrots | 동일 누락 없음 |
| Base.CannedCarrots2 | 닫힌 통조림 → Base.CannedCarrotsOpen | 교정 |
| Base.CannedCarrotsOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedChili | 닫힌 통조림 → Base.CannedChiliOpen | 교정 |
| Base.CannedChiliOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedCorn | 닫힌 통조림 → Base.CannedCornOpen | 교정 |
| Base.CannedCornOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedCornedBeef | 닫힌 통조림 → Base.CannedCornedBeefOpen | 교정 |
| Base.CannedCornedBeefOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedEggplant | 병조림 → Base.Eggplant | 동일 누락 없음 |
| Base.CannedFruitBeverage | 닫힌 통조림 → Base.CannedFruitBeverageOpen | 교정 |
| Base.CannedFruitBeverageOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedFruitCocktail | 닫힌 통조림 → Base.CannedFruitCocktailOpen | 교정 |
| Base.CannedFruitCocktailOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedLeek | 병조림 → Base.Leek | 동일 누락 없음 |
| Base.CannedMilk | 닫힌 통조림 → Base.CannedMilkOpen | 동일 누락 없음 |
| Base.CannedMilkOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedMushroomSoup | 닫힌 통조림 → Base.CannedMushroomSoupOpen | 교정 |
| Base.CannedMushroomSoupOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedPeaches | 닫힌 통조림 → Base.CannedPeachesOpen | 교정 |
| Base.CannedPeachesOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedPeas | 닫힌 통조림 → Base.CannedPeasOpen | 교정 |
| Base.CannedPeasOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedPineapple | 닫힌 통조림 → Base.CannedPineappleOpen | 교정 |
| Base.CannedPineappleOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedPotato | 병조림 → farming.Potato | 동일 누락 없음 |
| Base.CannedPotato2 | 닫힌 통조림 → Base.CannedPotatoOpen | 교정 |
| Base.CannedPotatoOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedRedRadish | 병조림 → farming.RedRadish | 동일 누락 없음 |
| Base.CannedSardines | 닫힌 통조림 → Base.CannedSardinesOpen | 교정 |
| Base.CannedSardinesOpen | 개봉 상태 | 동일 누락 없음 |
| Base.CannedTomato | 병조림 → farming.Tomato | 동일 누락 없음 |
| Base.CannedTomato2 | 닫힌 통조림 → Base.CannedTomatoOpen | 교정 |
| Base.CannedTomatoOpen | 개봉 상태 | 동일 누락 없음 |
| Base.Dogfood | 닫힌 통조림 → Base.DogfoodOpen | 교정 |
| Base.DogfoodOpen | 개봉 상태 | 동일 누락 없음 |
| Base.OpenBeans | 개봉 상태 | 동일 누락 없음 |
| Base.TinnedBeans | 닫힌 통조림 → Base.OpenBeans | 교정 |
| Base.TinnedSoup | 닫힌 통조림 → Base.TinnedSoupOpen | 교정 |
| Base.TinnedSoupOpen | 개봉 상태 | 동일 누락 없음 |
| Base.TunaTin | 닫힌 통조림 → Base.TunaTinOpen | 교정 |
| Base.TunaTinOpen | 개봉 상태 | 동일 누락 없음 |

### 수정한 통조림의 실제 한국어 간단 설명

- **Base.CannedBolognese**
  - 직전: 통조림 따개로 개봉해 꺼낸 볼로냐 소스를 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 볼로냐 소스를 요리 재료로도 쓸 수 있다.
- **Base.CannedCarrots2**
  - 직전: 통조림 따개로 개봉해 꺼낸 당근을 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 당근을 요리 재료로도 쓸 수 있다.
- **Base.CannedChili**
  - 직전: 통조림 따개로 개봉해 꺼낸 칠리소스를 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 칠리소스를 요리 재료로도 쓸 수 있다.
- **Base.CannedCorn**
  - 직전: 통조림 따개로 개봉해 꺼낸 옥수수를 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 옥수수를 요리 재료로도 쓸 수 있다.
- **Base.CannedCornedBeef**
  - 직전: 개봉해 꺼낸 소고기를 요리 재료로 쓸 수 있다.
  - 교정: 개봉해 내용물을 먹을 수 있다. 꺼낸 소고기를 요리 재료로도 쓸 수 있다.
- **Base.CannedFruitBeverage**
  - 직전: 통조림 따개로 개봉해 꺼낸 과일 음료를 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 과일 음료를 요리 재료로도 쓸 수 있다.
- **Base.CannedFruitCocktail**
  - 직전: 통조림 따개로 개봉해 꺼낸 프루트 칵테일을 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 프루트 칵테일을 요리 재료로도 쓸 수 있다.
- **Base.CannedMushroomSoup**
  - 직전: 통조림 따개로 개봉해 꺼낸 버섯스프를 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 버섯스프를 요리 재료로도 쓸 수 있다.
- **Base.CannedPeaches**
  - 직전: 통조림 따개로 개봉해 꺼낸 복숭아를 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 복숭아를 요리 재료로도 쓸 수 있다.
- **Base.CannedPeas**
  - 직전: 통조림 따개로 개봉해 꺼낸 완두콩을 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 완두콩을 요리 재료로도 쓸 수 있다.
- **Base.CannedPineapple**
  - 직전: 통조림 따개로 개봉해 꺼낸 파인애플을 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 파인애플을 요리 재료로도 쓸 수 있다.
- **Base.CannedPotato2**
  - 직전: 통조림 따개로 개봉해 꺼낸 감자를 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 감자를 요리 재료로도 쓸 수 있다.
- **Base.CannedSardines**
  - 직전: 개봉해 꺼낸 정어리를 요리 재료로 쓸 수 있다.
  - 교정: 개봉해 내용물을 먹을 수 있다. 꺼낸 정어리를 요리 재료로도 쓸 수 있다.
- **Base.CannedTomato2**
  - 직전: 통조림 따개로 개봉해 꺼낸 토마토를 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 토마토를 요리 재료로도 쓸 수 있다.
- **Base.Dogfood**
  - 직전: 통조림 따개로 개봉해 개 사료를 얻을 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다.
- **Base.TinnedBeans**
  - 직전: 통조림 따개로 개봉해 꺼낸 콩을 요리 재료로 쓸 수 있다. 콩 통조림으로 그릇 (콩)을 만들 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 콩을 요리 재료로도 쓸 수 있다. 콩 통조림으로 그릇 (콩)을 만들 수 있다.
- **Base.TinnedSoup**
  - 직전: 통조림 따개로 개봉해 꺼낸 스프를 요리 재료로 쓸 수 있다.
  - 교정: 통조림 따개로 개봉해 내용물을 마실 수 있다. 꺼낸 스프를 요리 재료로도 쓸 수 있다.
- **Base.TunaTin**
  - 직전: 개봉해 꺼낸 참치를 요리 재료로 쓸 수 있다.
  - 교정: 개봉해 내용물을 먹을 수 있다. 꺼낸 참치를 요리 재료로도 쓸 수 있다.

KO/EN의 compact/expanded 전체 직전 문구는 기존 review JSON canned_consumption_correction.before에, 최신 문구는 각 item correction.after와 기존 HTML에 보존한다. 직전 식품 미끼 교정 후보도 보존한다. 현재 최종 영향4노드 검사 실행 중이며 이 절의 구현 완료 판정은 실제 종료 결과 뒤에 기록한다.

CannedMilk의 기존 consume_edible_food는 내용물 섭취를 표현하는 근거로 이미 쓰였고, 개봉 결과 CannedMilkOpen의 drink_food_contents는 실제 결과 상태의 마시기 근거다. 이번에는 기존 섭취 설명을 중복하거나 마시기 불가로 바꾸지 않고 유지했다. 두 fact를 동일 원물의 같은 동작으로 합치지 않으며, 어느 표현도 다른 소비 동작을 금지한다는 뜻은 아니다.


### 통조림 교정 최종 결과

blocks 관계 어댑터가 바뀌어 영향을 받는 기존 네 노드를 한 번의 마지막 묶음으로 실행했다. **exit 0, 4 passed in 173.79s**다. 이번 묶음에는 실패가 없었으며 추가 confidence 검사나 새 Gate는 수행하지 않았다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
Remove-Item Env:IRIS_MENU_RESUME_PACKAGE -ErrorAction SilentlyContinue
Remove-Item Env:IRIS_MENU_TOOLTIP_CANDIDATE -ErrorAction SilentlyContinue
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\canned-final-0912a -q -s --tb=short -x
```

- 최종 ZIP: `.tmp/menu/run-vq4__gyj/p/Iris.zip`
- ZIP 옆 모드 루트: `.tmp/menu/run-vq4__gyj/p/Iris` (`mod.info`와 `media`가 직접 들어 있음)
- product: `l3p-574a363f4367fcb20b6c3cd576f65097103676813ef9187df1862389f9dd3790`
- ZIP SHA-256: `a60a766c913ac6ce19b47dee70c7877f30520a8c52ad9ef9ff303c02399edb9e`
- descriptions SHA-256: `28885b0487d24bffb6825bb006e4a647fc9d1bf74113b7db1eda97c1c8d1fa04`
- blocks SHA-256: `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`
- tooltip product: `ttp-e6a8a8fa7d757460b04830919ccb9a9cd73f2a7afe57793d9b90e8de217ffadf`

기존 네 노드 내부에서 결과 소비의 정확한 대상/조건 변조 거절, 두 제품 빌드 바이트 일치, 원본/후보 Lua 388파일 문법, Browser/Wiki 4,210상태, 툴팁 2,280 exact keys/legacy_calls 0, L4 모델, 패키지 입장·ZIP 추출 포인터, 중단·rollback·idempotence·원본 pointer 보존을 확인했다. 하위 실행 명령 모두 exit 0이며 Fixture.Layout 네 fit failure는 기존 거절 사례다. 기존 JSON/HTML은 최신 KO/EN compact/expanded 문구로 갱신했고 이전 후보·직전 문구·검사 이력은 보존했다.

최종 상태는 **implemented_only**다. 사용자의 당근 사례는 최신 문구 자체의 누락으로 확인되어 수정했으며 설치 문제로 돌리지 않는다. 이번 결과는 통조림 개봉 후 섭취 전달 문제의 교정과 구현 검사 완료를 뜻하며 실제 PZ 시각 수락, 전체 용도 품질, 원천 불확실성의 전면 PASS를 뜻하지 않는다. 외부 설치 폴더 접근·재설치·커밋·배포는 수행하지 않았다.


## 2026-09-13 전체 문면 경계 조사 — 교정 전 보고

사용자는 집개/둥근머리 망치/전지톱의 예시를 넘어 전체 조사 후 교정을 지시했다. 따라서 앞서 편집한 단조/장치 목적 공통 규칙 두 곳은 부분 작업으로 남겨두고, 이 조사 중 새 descriptions 생성·테스트·패키징을 실행하지 않았다. 마지막 검증 후보 run-vq4__gyj 및 SHA 28885b…fa04 문면을 기준으로 조사했다. 아래 수치는 최종 생성 변화량이나 전체 품질 PASS가 아니다.

전체 2,105개, KO/EN compact/expanded 8,420좌표를 기존 corpus와 fact/role/qualifier/recipe-result 연결로 검토했다. 692개의 정확한 네 표면/단위 조합을 바탕으로 공개 activity 58개, 직접 기능223개, effect/state payload110개, 공개 qualifier179개를 의미별로 대조했다. 이름·중간점 존재·명사 나열 자체를 의미 결함 기준으로 삼지 않았다. 각 항목의 적용 집합과 공통 원인은 기존 review JSON boundary_investigation_20260913 및 item별 boundary_review_20260913에 기록했다. 원천 사실 전체 재감사는 수행하지 않았다.

**표시 제약 확정:** 사용자 인게임 관측에 따르면 중간점(U+00B7, `·`)이 표시되지 않는다. 에이전트 직접 게임 관측은 아니지만 사용자의 확정 관측으로 취급한다. 글머리표 등 다른 기호 미지원으로 확대하지 않는다. 중간점은744개 아이템에서 발견되며 KO compact611/expanded720, EN두표면0이다. 의미 교정과 별도로 남겨야 할 나열의 구분을 쉼표나 자연스러운 접속으로 표현할 필요가 있다.

| 축 | 고유 아이템 | 의미 판단 |
| --- | ---: | --- |
| A 동일 목적의 중복 분할 | 55 | 역할과 대상 연결로 같은 목적임을 확인한 묶음 |
| B 전역 목적명이 실제 범위보다 넓음 | 42 | 실제 admitted target 또는 기존 채택 recipe 관측과 비교 |
| C 레시피별 상세/요건 표현 정리 | 71 | 해당 문구 전체 삭제가 아니라 불필요한 상세를 목적·입력 정체성과 구분해 교정할 범위 |
| D 중간점 표시 영향 | 744 | 표시 영향이며 그 자체로 의미 결함이라는 뜻은 아님 |

A/B/C 의미 교정 합집합133개, 네 축 합집합770개다. 중복은 AB7/AC12/AD52/BC22/BD42/CD46이며 각 축 수를 단순 합산하지 않는다.

A의 공통 원인은 단조6(도구4/재료2), 반죽18(용기2는 이미 통합되어 반례로 제외), 붕대류 세척4, 물 옮기기24, 점화 도구3이다. 단조는 일반 금속단조와 삽/문부품 결과군이 별도 목적처럼 나오며, 반죽도 cookie/dough/batter를 같은 역할로 반복한다. 세척은 recipe 역할과 native 세척 기능이 같은 물품을 깨끗하게 하는 목적을 중복한다. 물 옮기기는 다른 용기/저장 시설 대상별로 같은 이송을 반복하고, 점화3은 지원 대상별 문장에서 점화 도구라는 설명을 반복한다. 역할/대상/조건 근거를 없애지 않고 공개 목적을 하나로 표현하는 방향이다.

B는 장치 제작28, 전자 부품 제작5, 붕대 재료 준비9, 쌀/파스타2, 손잡이의 삽류 명칭1의 중복 합집합42다. 장치 전역label은 모든 아이템에 폭발/발화/신호 전부를 붙인다. Saw/GardenSaw의 유일한 실제 결과는 PipeBomb이고, Amplifier는 NoiseTrap, Coldpack은 SmokeBomb이다. 전자부품에서는 AlarmClock2/Timer가 타이머만, Receiver/RadioReceiver가 원격 격발기만, Remote가 원격 조정기 버전군만 공급한다. Glue/ElectronicsScrap/Screwdriver는 전체 목적을 실제 지원하므로 같은 과장 판정에서 제외한다. 붕대 준비는 CottonBalls/각 붕대/오염 직물/물 냄비의 실제 결과가 서로 다른데 모두 붕대와 소독솜을 나열한다. Disinfectant/WhiskeyFull은 실제 양쪽을 지원하는 반례다. Rice/Pasta는 각각 자신의 요리만 만드는데 모두 쌀과 파스타 준비라고 한다. 두 물 냄비는 실제 양쪽을 지원한다. 마지막 네 항목군은 기존 채택 provenance의 recipe 관측도 대조했다.

C는 약초 찜질제/석고/산탄총 단축/작물 치료제/오트밀/오믈렛/달걀 포장/쌀과 파스타 준비/통나무 묶기/콩 준비/생선 및 개구리 손질/음식 나누기/화염병/붕대 세척의 공개 recipe 요건과 별도 `제작 대상:` 후행 문구9개에서 찾았다. 정확한 수량, 다른 투입물 목록, 버전별 요건과 fallback 반환 내역은 목적 본문과 분리한다. 단, 식품 자체의 유효 상태나 재료 손실처럼 용도를 구별하는 사실은 필요한 짧은 설명으로 남기며 내부 조건을 전부 삭제하지 않는다. C의71은 이러한 교정 대상 집합이지 qualifier 일괄 삭제 허가가 아니다.

대표 제안:

- Tongs: 금속/삽/문 부품 단조3항목 → `금속을 단조하는 데 쓰는 도구다.`
- Butter: 묽은 반죽/쿠키 반죽/반죽3항목 → `반죽 준비에 쓰는 재료다.` 영어에서는 실제 dough와 batter 범위를 잃지 않게 표현한다.
- BandageDirty: 붕대 준비와 세척2항목 → `물로 씻어 깨끗한 붕대로 바꿀 수 있다.` 원래 dirty 상태의 상처 감염 가능성은 유지한다.
- 물 용기: 다른 용기에 붓기/저장 시설에 붓기 → `다른 물 용기나 물 저장 시설에 물을 옮길 수 있다.`
- Saw/GardenSaw: 폭발, 발화, 신호 장치 전체 → `파이프 폭탄 제작에 쓰는 도구다.` 절단 역할은 근거 없이 발명하지 않는다.
- AlarmClock2: 타이머/원격 부품 전역label → `타이머 제작에 쓰는 재료다.`
- Rice: 쌀/파스타 준비 → `쌀 요리에 쓰는 재료다.`
- 씨앗: `씨앗 포장에 재료로 쓰인다. 제작 대상: …씨앗 봉투.` → `씨앗을 봉투로 포장할 수 있다.`

유지할 반례: 망치의 단조와 목공/가구 이동/공격은 실제 다른 목적이다. 단일 탄약 몰드의 탄종, 개봉 통조림의 정확한 내용물, 분해 결과의 수신기와 조건부 건전지, 소분 음식과 함께 돌아오는 원래 용기는 의미 있는 결과 정체성이다. 상처 감염/재료 손실/미완성 낚싯대/오염된 물/특정 장착 위치 등의 구별 조건도 단순 요건 키워드만으로 지우지 않는다. Bowl/MuffinTray의 반죽 용도는 이미 한 항목이다. 문자 그대로 동일한 expanded segment가 반복된 사례는 없었고, 이번 A는 의미상의 중복이다.

판단을 남겨둘 부분: 장치의 복수 결과군은 결과명 전체를 L3 목록으로 복사하는 전역 해결책을 쓰지 않는다. 같은 목적의 세분은 통합하고 실제 소음/연막/발화 등 다른 목적은 보존하는 짧은 표현을 정해야 한다. 제작 가능성이 장치의 실제 발화/피해/소음 동작까지 입증하는 것은 아니다. 입력 상태가 핵심인 손질 조건과 단순 다른 재료·도구 요건도 구별해야 한다. 불명확한 callback 결과를 새 목적에 자동 분류하지 않는다. 기존42개 차량 목적 불확실성과 exact ID L4 공급 공백은 이번 문면 교정으로 해소됐다고 주장하지 않는다.

현재 상태는 조사 보고/범위 확인 대기다. 추가 생성·최종 검사·후보 생성 없이 이 결과를 감독 세션에 먼저 보고한다. 승인된 전체 의미 교정을 적용한 뒤 남는 필요한 구분을 producer에서 수정하고, 마지막 영향 검사만 수행할 예정이다.


## 2026-09-13 전체 문면 경계 교정 — 최종 implemented_only

위 조사 후 감독 검토에 따라 공통 생성 규칙을 교정했다. 조사 A55/B42/C71/D744와 합집합770은 조사 집합이다. 최종 Before(28885b…fa04) → After(cb646b…f622)의 실제 문면/단위 변화는 **의미·구조141개 + 표시만625개 =766개**다. 표시만 변경은 네 표면의 단위 경계를 유지하면서 공개 문장의 U+00B7을 쉼표로 바꾼 경우로 구분했다. 자연스러운 접속 표현을 새로 쓴 경우는 표시만 집합에 넣지 않았다. 이 수치는 전체 원천 품질 PASS가 아니다.

같은 역할의 단조/반죽, 같은 결과의 세척, 물 옮기기, 점화 목적을 합쳤다. 실제 제조 결과의 공통 목적을 일반/특수 compact와 expanded가 공유하도록 연결했다. GardenSaw의 초기 compact에 전역 폭발/발화/신호 명칭이 남았던 결함은 최종 전에 수정했다. 중간 두 검사 실행은 감독 문면 지적을 반영하기 위해 중단(exit1)했으며 성공 근거로 사용하지 않는다.

compact에 제작 결과 전량을 압축 나열하던 초기 접근도 폐기했다. 기존 목적 관계를 이용하는 다목적 재료 요약은 DenimStrips/Plank/RippedSheets/Twine에 적용됐다. 다른 아이템에 연료나 응급처치 목적을 전이하지 않는다. 세부 제작물과 수박 쪼개기 같은 개별 활용은 expanded의 독립 용도와 참조에 보존한다. 새 소제목 분류, 길이 Gate, 글꼴 축소, 런타임 문장 재작성은 추가하지 않았다.

| 대상 | 최종 실제 문면 또는 보존 판단 |
| --- | --- |
| Tongs expanded | 금속을 단조하는 데 쓰는 도구다. |
| GardenSaw compact | 음식 손질, 목공 및 건축물 분해, 파이프 폭탄 제작, 덫 제작에 쓴다. |
| Remote expanded | TV 리모컨은 원격제어 조정기 제작에 재료로 쓰인다. 분해 결과의 수신기/조건부 건전지는 별도 보존. |
| Egg compact | 달걀곽에 포장할 수 있다. 먹거나 요리, 반죽 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다. |
| Plank compact KO | 목공과 건축의 재료로 쓰며 다른 물품을 만드는 데도 쓸 수 있다. 골절 고정이나 근접 공격에 쓰고, 연료로도 쓸 수 있다. |
| Plank compact EN | It supplies material for woodworking, construction, and crafting. It can also be used for splinting fractures and melee attacks, or as fuel. |
| RippedSheets compact KO | 응급처치, 의류 수선과 건축에 쓰며 제작 재료로도 쓸 수 있다. 연료나 불쏘시개로도 쓸 수 있다. |
| RippedSheets compact EN | It supplies material for first aid, clothing repairs, construction, and crafting. It can also be used as fuel or tinder. |
| OpenBeans | 이미 열린 원물의 용도에 섞인 닫힌 캔 따개 조건 제거. |
| 생선 자체7개 | 무게 >0.6 조건은 현재 아이템 손질 가능성을 구분하므로 유지. 도구에 붙던 해당 수치는 공개 상세에서 제거. |

달걀 포장의 expanded 상태 조건은 ‘익히지 않고 타지도 않은’으로 두 부정을 명시했다. 문과 창문, 머리와 몸통을 제외한 부위, 설치와 철거처럼 관계가 필요한 공통 템플릿은 접속 표현으로 고쳤다. 남은 공개 문장의 중간점은 producer에서만 처리했다. 실제 이름에 중간점이 들어간 사례는 없었으며 내부 source/refs/조건 토큰/L2/L4와 다른 기호는 이 교정 대상으로 삼지 않았다.

CannedCarrots2의 개봉 후 당근 섭취/요리, TinnedSoup의 개봉 후 마시기, 식품 미끼, Bread의 원물 주어, Hammer의 다른 용도, 탄약 몰드의 탄종, 의료·오염된 물의 유효한 expanded 조건은 보존했다. 기존 차량42개 불확실성과 exact ID L4 공급 공백은 그대로다.

최종 기존 최소3노드 검사는 `boundary-final-0913c`에서 **3 passed in 141.70s, exit0**이다. exact 명령/환경은 기존 `docs/review/structure/items.json`의 boundary_correction.validation에 기록했다. 설명의 사실/조건/참조 보존, S2 공급, 제품 두 빌드 바이트 일치, Lua 문법388파일, Browser/Wiki4210상태, 툴팁2280키/legacy0, 패키지 거부 fixture, ZIP 포인터, 복구/롤백/멱등성 검사가 포함됐다. Fixture.Layout의 네 fit failure 출력은 의도한 음성 fixture이며 해당 런타임 노드는 exit0이었다. 실제 PZ 글꼴 검사는 font stub 검사로 대체했다고 주장하지 않는다.

- descriptions SHA256: `cb646b6031c3670795b9d0f10969026531ba71ee9941a8ec52d1ebe6a125f622`
- blocks SHA256(변경 없음): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`
- product: `l3p-3eb7033153800db6ab44113a5f1d4c1e2eb7e5c34984849e293d6a715a91114d`
- ZIP: `.tmp/menu/run-bodrgea4/p/Iris.zip`
- ZIP SHA256: `f277173e09bba01e9500d4aa11b7f9d581591376667a5defb3bf4311c5471a06`
- 직접 mod root: `.tmp/menu/run-bodrgea4/p/Iris` (mod.info와 media 포함)

기존 JSON/HTML의 이번 Before는 조사 직전 28885b…fa04, After는 최종 cb646b…f622다. 원래 역사적 비교 자료는 JSON에 보존했다. 최종 상태는 **implemented_only**이며 인게임 수락, 설치/배포 또는 원천 사실 전체 해소를 선언하지 않는다.


## 2026-09-13 조리 재료와 반죽 준비의 포함관계 — implemented_only

사용자 지적에 따라 같은 원물의 같은 ingredient 역할에서 이미 조리 재료 목적이 채택됐으면 반죽 준비를 그 목적에 포함시켰다. 앞선 교정은 반죽3종→반죽1종에서 멈췄으며 조리→반죽 의미 포함관계를 놓쳤다. compact 미끼 공통 문장도 요리와 반죽을 병렬 나열했으므로 함께 수정했다. 새 분류나 증명 artifact 없이 기존 public_use frame의 참조 합집합과 placement_reason에 포함 이유를 보존했다.

전체 실제 소비 범위는 **21개/84좌표**이며 생성 결과의 변화량과 일치한다: Base.BakingSoda, Butter, CannedMilkOpen, Cheese, ChocolateChips, CocoaPowder, Cornflour, Egg, Flour, Lard, Margarine, Milk, OatsRaw, OilOlive, OilVegetable, Salt, Sugar, SugarBrown, SugarPacket, TomatoPaste, WildEggs. 이 목록은 전부 Base 모듈이다. 같은 역할/원물이며 구별되는 공개 상태조건이 없는 조리 및 반죽 ingredient만 합쳤다.

- Flour/Cornflour KO compact와 expanded: `요리 재료로 쓸 수 있다.`
- Flour/Cornflour EN compact와 expanded: `It can be used as a cooking ingredient.`
- Butter KO compact: `먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.` expanded는 먹기/요리 재료/미끼3항목이다.
- Butter EN compact: `It can be eaten or used as a cooking ingredient. It can also be used as trap bait.` expanded도 세 독립 용도를 보존한다.

조리 상위 목적이 없는 Yeast는 반죽 용도를 유지했다. Fork 같은 도구와 Bowl 같은 용기는 다른 역할이므로 이번 포함관계를 전이하지 않았다. Egg 포장/상태 조건, Sugar의 병조림과 보존조건, Milk/CannedMilkOpen 작물 치료제, 섭취/미끼와 원물-결과 관계를 유지했다. 반죽의 내부 사실/조건/참조는 삭제하지 않았다. 이전 boundary 후보 및 역사적 Before/After는 기존 JSON에 남아 있다.

최종 기존 최소3노드 명령은 `cooking-inclusion-final-0913a`에서 **3 passed in 177.62s, exit0**이다. 명령과 환경은 기존 JSON의 cooking_inclusion_correction.validation에 기록했다. 설명 보존/S2 공급/제품 검사 한 묶음만 실행했으며 Lua 문법388파일, Browser/Wiki4210상태(font stub), Tooltip2280키, ZIP 포인터, 복구/롤백/멱등성을 포함한다. 추가 confidence 검사나 전체 원천 재조사는 하지 않았다.

- Before descriptions: `cb646b6031c3670795b9d0f10969026531ba71ee9941a8ec52d1ebe6a125f622`
- After descriptions: `c3dfca3d4843d321899e624ba4150d994c3410a5bd289e1f289788819a45174e`
- blocks 변경 없음: `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`
- product: `l3p-c2a088b970e0c0925b8e569836300feafc2cabe8508db1cae3bffd07ff1c4f47`
- ZIP: `.tmp/menu/run-r46s_i87/p/Iris.zip`
- ZIP SHA256: `c57a4d742c42737a8a6862c903d459fc24c904d04a6a8c6048b3d843e75eb589`
- 직접 mod root: `.tmp/menu/run-r46s_i87/p/Iris`

HTML/JSON의 이번 비교는 cb646b…→c3dfca…이다. 최종 상태는 **implemented_only**, 실제 후보 PZ 관찰 전이다. 차량42개 불확실성 및 exact ID L4 공급 공백은 이번 교정으로 해소됐다고 주장하지 않는다.


## 2026-09-13 공통 공개 문장 경로 재적용

이번 시작 시점 `c3dfca3d4843d321899e624ba4150d994c3410a5bd289e1f289788819a45174e` 대비 **726개 아이템 / 2,429개 표면**이 바뀌었다. 이전 670개/40개/통조림/ingredient21개 등의 교정 건수와 합산하지 않는다. 전체 2,105개/8,420좌표와 각 표면 present1,981 / absent124를 유지한다.

2,105개 × KO/EN × compact/expanded의 실제 문면을 네 문자열 조합 679개와 공유 segment 사전으로 펼쳐 읽은 뒤, 후속 변경된 기술책/물/지면작업/역할 주어/의료/패치/조리 포함/순서 문면을 다시 읽었다. 문자열 중복은 읽기 분량만 줄였으며 서로 다른 관계의 의미 판정을 자동 공유하지 않았다. 지적 경로는 실제 payload, 적용 qualifier, role 및 result_consumption/recipe result 관계와 대조했다. 모든 관계의 원천 재조사나 독립 품질 승인은 수행하지 않았으며 refs 보존·건수·자동검사는 문장 품질의 증거로 대체하지 않는다.

- 특수 도구 요약과 context-role continuation에도 admitted target refinement를 전달한다. 몰드 탄종을 보존하고 다목적 단조 도구는 상위 목적을 유지한다.
- 탄띠는 실제 reload_speed_setting multiply_1_15와 산탄/비산탄 착용 범위를 효과 문장으로 표현한다. 장전 시간 감소를 추론하지 않는다.
- 개조부품 장착/제거와 탄창 삽입/탄약 채움/잔탄 회수를 보존하며 다른 도구의 비소모 설명을 제거한다.
- 붕대11개 감염 위험을 붕대 용도와 결합하고 화상6개 시술 강도/통증을 공개 목적에서 제외한다. 패치5개는 다른 투입물 요구와 잘못된 재료 역할을 제거한다.
- 같은 무조건 tool 역할의 음식 준비가 반죽 준비를 포함하는 4개와 Bowl container 목적을 검토해 포함 처리한다. 기존 ingredient21개와 별도 범위이며 서로 더해 변화량으로 쓰지 않는다.
- 변환 전후 주어, 낚싯줄 파손 후 실제 잔류물, 돌망치 건축 마모 범위, 물 사용 표적과 오염수 위험을 유지한다.
- 상위 compact material 문장을 작성한 순서의 fact traversal을 expanded에 전달한다. 전역 품목 우선순위나 Lua 문구 재작성을 추가하지 않는다.

CannedMilk는 원본 generic eat dispatch와 개봉 결과의 실제 `drink_food_contents`가 충돌할 때 확인된 result_consumption을 우선해 “통조림 따개로 개봉해 내용물을 마실 수 있다”로 표현한다. CannedMilkOpen의 실제 음용 용도 및 조리 용도와 일치한다. CannedFruitBeverageOpen은 admitted `eat_food`이므로 이름만으로 drink를 새로 만들지 않았다. 개봉 도구, 확인된 결과, 요리 포함, 원본/결과 구분과 기존 통조림 소비 교정은 유지했다.

RippedSheets expanded의 붕대 용도와 감염 위험은 한 use_unit이며 화상 강도/시술 통증이나 패치의 다른 재료 요구를 별도 용도로 출력하지 않는다. RollingPin compact는 “음식 준비에 쓰는 도구. 근접 공격에 쓸 수 있다.”이며 expanded는 두 독립 용도다. Plank compact의 승인된 상위 목적을 유지하고 expanded도 목공/건축부터 전개한다. 이 작업에서 Tooltip의 최대 네 줄이나 폰트/폭은 바꾸지 않았고 Lua에 문장 합성기를 추가하지 않았다.

새 descriptions SHA256은 `ff2e93b65270c8d226dfcce5e9148fe7f5c5d69927f721d87394fccb9089443b`, blocks는 변경 없이 `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`다. 기존 uses/structure JSON에 이전 locales/판정을 보존하고 현재 원문과 이번 기록을 추가했다. 이전 classification/axis 판단을 새 전체 품질 승인으로 자동 승계하지 않는다. `iris_dvf_descriptions.html`은 현재 8,420개 원문과 producer use_units로 갱신했고, `iris_dvf_description_review.html`에는 이번 시작 시점과 현재 네 표면을 비교할 수 있도록 기록했다.

문구를 고정한 뒤 아래 최소3노드를 한 묶음으로 실행했으며 **3 passed in 148.22s, exit 0**이다. 검사 중 producer를 바꾸지 않았고 추가 confidence 검사나 전체 Run A/B를 실행하지 않았다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

기존 제품 노드가 Lua 문법388파일, Browser/Wiki4,210상태(font stub), Tooltip2,280키, 공통 B/C stage와 ZIP 포인터, 복구/롤백/멱등성을 다뤘다. 명령 로그는 `.tmp/prose/final-tests.log`다.

- 공통 제품: `l3p-344df05eef9f14cb34a34e9bf46b28e3d83bd6b993c99abed2aec6ad16830660`
- ZIP: `.tmp/menu/run-6ipav47h/p/Iris.zip`
- ZIP SHA256: `129e30872e0a2326a17e4432a769eaf254315ff5f9d63a2c5bed5f8c71ea023c`
- 직접 mod root: `.tmp/menu/run-6ipav47h/p/Iris` (`mod.info`와 `media` 확인)
- S2 후보: `.tmp/tooltip/run-yftu78yd/s/.tmp/package/Iris.zip`

최종 상태는 **implemented_only**다. 전체 표현 결함0, 독립 품질 수락 또는 strict production 수락을 선언하지 않는다. absent124, 차량42개 구체 목적 미확정, unresolved 관계와 exact ID L4 공급 공백은 남긴다. 실제 PZ에서 KO/EN 폰트, Tooltip 네 물리줄/Alt/S1·S3·S4 공존, Browser/Wiki 좁은 폭·긴 설명·스크롤 끝·Layer4 접근은 미관찰이다. 저장소 밖 게임 설치나 current/live 전환, commit/push/배포는 하지 않았다.


## 사용자 후속 A~D 전체 조사 및 공통 교정 (2026-09-13)

상태: **implemented_only**. 실제 PZ 관찰·전체 품질 수락은 아니다.

기준 ff2e93 대비 기존 전체2105아이템/8420좌표 독해 기록과 679개 네문자열 조합 재독을 이어 A~D를 판단했다. 공통 수정 후 새로 나타난333개 localized segment를 읽고 그릇분배 continuation과 로프·찜질제의 최종5아이템 문면을 다시 읽었다. 원천 관계가 다른 항목은 같아 보이는 문구만으로 일괄 판정하지 않았다. 집계는 사람이 읽은 판정의 전사이며 자동 품질 증명·새 검증 권위가 아니다.

| 의미축 | 조사 아이템 | 조사 좌표 |
|---|---:|---:|
| A | 35 | 140 |
| B | 9 | 36 |
| C | 161 | 442 |
| D | 354 | 1280 |

중복 제외 조사547아이템/1850좌표. 조사 집계는 삭제목록이나 실제 변경수가 아니다.

배타적 교차집계(빈 축은 조사상 해당 없음):

{"items": {"": 1558, "D": 342, "C": 156, "A": 35, "B+D": 7, "B": 2, "C+D": 5}, "coordinates": {"": 6570, "D": 1232, "C": 422, "A": 140, "B+D": 28, "B": 8, "C+D": 20}}

실제 기준 대비 변경: 539아이템 / 1878좌표.

- A: 식품의 식사·조리 용도가 확인된 범위에서 개별 분할·그릇 분배 결과와 하위 팬 준비 절차를 공개 용도에서 제외했다. 결과 관계와 원천 사실은 유지한다.
- B: 선택적 식기와 차량 정비 열쇠 요건을 내부로 분류했다. 음식 준비 도구·창 부착·근접 공격, 맞는 문·차량 열쇠 사용은 공개 용도로 유지한다.
- C: 문해·현재 배율, 로프 수량·힘·회수 상태, 지도 편집 도구 조합, 일반 성공 비보장과 반복 실행 조건을 목적 문장에서 줄였다.
- D: 물 저장·급수·혈흔 세척·소화·음용, 도색·표식, 가구 이동·차량 수납·좌석·개폐, 매체·의료·설치 목적을 각각의 공통 함수와 역할 표현에서 간결하게 썼다.
- 수정 중 그릇 분배 직접 기능을 숨긴 뒤 재료 역할 문장이 남는 경로도 확인해 같은 의미 범위로 제외했다. 특정 FullType나 완성 문장 교체 규칙은 추가하지 않았다.
- 씨앗 봉투7의 실제 결과 수량50과 Wrench의 엔진 회수 한계·상태0 결과는 유지했다. 모든 숫자·변환·선택 기능·한계를 삭제하는 정책이 아니다.
- 로프2는 설치 후 상승·제거와 건축·통나무 묶기를 유지한다. 찜질제3은 다친 부위에 바르는 물품으로만 설명하며 새로운 치료 효과를 추정하지 않는다.

반례로 음식분할 도구13과 Bowl 용기 용도, 캔 개봉→소비·조리, 의류 회수·연료·시트 로프, 실제 탄약 호환 및 착용범위15% 효과, 낚싯줄 파손·미끼 소실, 봉합 보조 시간 단축·의료 감염/독성 위험을 유지했다.

- 124 absent 유지
- 차량42 구체 목적 미확정 유지
- Muffintray_Biscuit/Watermelon2 상위 식사·조리 근거 부재로 음식결과 숨김 일반화 보류
- 기술책 정확한 숫자 레벨 범위는 이번 admitted facts에 별도 확정되지 않아 일반 범위 문구 유지; 최대배율은 실제 state값 유지
- unresolved relations 및 L4 exact ID 공급 공백 유지
- 실제 PZ 폰트·툴팁4물리줄·Alt·메뉴 스크롤 미관찰
- 전체 표현 결함0·품질 수락 선언 아님

Descriptions SHA256: `cd695ac810d58443012686bd3bc029dbbd09468d2abbe49ccad1b944d2be9a25`

Blocks SHA256: `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

최종 검증과 신규 후보는 아래 완료 기록에 별도로 기재한다. 중단 실행은 F 출력 후 요약 전 종료됐으며 최종 PASS가 아니다. 기존 콩통조림 기대값 잔존을 코드에서 확인했으나 중단 로그만으로 실패 원인을 확정하지 않는다.


### 후속 최종 검증 및 후보

아래 정확한 명령은 종료 코드 **0**, **3 passed in 154.70s**로 완료됐다.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

실행 로그: `.tmp/prose/followup-tests.log`. 검증은 기존 세 노드 묶음이며 추가 Gate나 전면 원천 재조사가 아니다. Lua 구문388파일, Browser/Wiki4210상태(font stub), Tooltip2280키, 패키지 수용·ZIP pointer·rollback/idempotence를 기존 노드에서 확인했다. 실제 PZ 관찰은 하지 않았다.

- 최종 변경: 기준 ff2e93 대비 **539아이템 / 1878좌표**. 조사547/1850과 별개다.
- product: `l3p-debcf5c477a0761d435d2e3945f6bb79c6bd26b046f591a217327483d1c82624`
- ZIP: `.tmp/menu/run-20rthxop/p/Iris.zip`
- ZIP SHA256: `f7aef9da4c24dede3fe0b234d3220f8bacd895f956cdd8078c792652fc1ea948`
- direct mod root: `.tmp/menu/run-20rthxop/p/Iris` (`mod.info`, `media` 확인)
- 상태: **implemented_only**. 이전 후보 보존, 라이브 설치·커밋·푸시 없음.

최종 로프 문면: “설치해 위층으로 올라가는 데 쓸 수 있는 로프다. 설치한 로프를 제거할 수 있다.” / “It is rope that can be installed for climbing to an upper floor. The installed rope can be removed.” 건축·통나무 묶기도 유지했다.

최종 찜질제 문면: “다친 부위에 바르는 약초 찜질제다.” / “It is an herbal poultice for application to an injured body part.” 적용 가능 조건은 내부 사실로 유지하고 치료 효과를 발명하지 않았다.


## 개봉 식품 결과명 공통 교정 (2026-09-13)

상태: **implemented_only**.

기준 cd695ac 대비 해당 개봉 관계29개와 결과명·섭취·조리·도구를 읽고, 재생성된29아이템의 KO/EN compact/expanded116좌표 실제 문면을 읽었다. 전체 원천 재조사나 새 Gate는 수행하지 않았다.

- 공통 개봉·섭취 문장의 내용물/its contents를 실제 declared 개봉 결과의 KO/EN 표시명으로 바꿨다. 요리 용도에서도 같은 결과명을 반복한다.
- 캔19·병식품9·달걀곽1의 기존 공통 문형 소비범위29아이템/116좌표를 확인했다. 각 관계는 단일 확정 결과명을 가지며 식별 미확정은 없다.
- 먹기27·마시기2, 조리28·조리 없음1, 따개16·도구 관계 없음13의 기존 구분을 유지했다. 개사료 조리, 원물 미끼, 그릇 콩 제작을 추가하지 않았다.
- 버섯스프/Mushroom Soup, 스프/Vegetable Soup 등 언어별 원본 표시명을 유지하고 번역이나 아이템 ID로 이름을 추정·축약하지 않았다.

기준 cd695ac 대비 **29아이템/116좌표** 변경. 전체2105/8420과 각 표면 present1981/absent124 유지.

**Base.CannedCarrots2**

KO 전: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 당근을 요리 재료로도 쓸 수 있다.

KO 후: 통조림 따개로 개봉해 당근을 먹을 수 있다. 꺼낸 당근을 요리 재료로도 쓸 수 있다.

EN 전: It can be opened with a Can Opener to eat its contents. The extracted Carrots can also be used as a cooking ingredient.

EN 후: It can be opened with a Can Opener to eat the Carrots. The extracted Carrots can also be used as a cooking ingredient.

**Base.TinnedSoup**

KO 전: 통조림 따개로 개봉해 내용물을 마실 수 있다. 꺼낸 스프를 요리 재료로도 쓸 수 있다.

KO 후: 통조림 따개로 개봉해 스프를 마실 수 있다. 꺼낸 스프를 요리 재료로도 쓸 수 있다.

EN 전: It can be opened with a Can Opener to drink its contents. The extracted Vegetable Soup can also be used as a cooking ingredient.

EN 후: It can be opened with a Can Opener to drink the Vegetable Soup. The extracted Vegetable Soup can also be used as a cooking ingredient.

**Base.CannedMushroomSoup**

KO 전: 통조림 따개로 개봉해 내용물을 먹을 수 있다. 꺼낸 버섯스프를 요리 재료로도 쓸 수 있다.

KO 후: 통조림 따개로 개봉해 버섯스프를 먹을 수 있다. 꺼낸 버섯스프를 요리 재료로도 쓸 수 있다.

EN 전: It can be opened with a Can Opener to eat its contents. The extracted Mushroom Soup can also be used as a cooking ingredient.

EN 후: It can be opened with a Can Opener to eat the Mushroom Soup. The extracted Mushroom Soup can also be used as a cooking ingredient.

**Base.CannedSardines**

KO 전: 개봉해 내용물을 먹을 수 있다. 꺼낸 정어리를 요리 재료로도 쓸 수 있다.

KO 후: 개봉해 정어리를 먹을 수 있다. 꺼낸 정어리를 요리 재료로도 쓸 수 있다.

EN 전: It can be opened to eat its contents. The extracted Sardines can also be used as a cooking ingredient.

EN 후: It can be opened to eat the Sardines. The extracted Sardines can also be used as a cooking ingredient.

**Base.Dogfood**

KO 전: 통조림 따개로 개봉해 내용물을 먹을 수 있다.

KO 후: 통조림 따개로 개봉해 개 사료를 먹을 수 있다.

EN 전: It can be opened with a Can Opener to eat its contents.

EN 후: It can be opened with a Can Opener to eat the Dog Food.

Descriptions SHA256: `0b7d82d82209bf8b554eb186b6f057b3ed8e28be3d67d5531bcf05d52e0f1271`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

새로운 개봉·소비 관계나 요리 근거는 추가하지 않았다. 최종 검증과 후보는 아래 완료 기록에 기재한다.


### 개봉 결과명 교정 최종 검증 및 후보

문구 고정 뒤 기존 최소3노드 묶음 한 번 실행: **3 passed in 142.59s (0:02:22)**, 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/opened-tests.log`. Blocks 불변으로 별도 block 검사를 추가하지 않았다. 새 Gate·전면 원천 재조사·추가 confidence 검사는 없다.

- product: `l3p-6b6682f524a190f6dc8114141aa0450023e6fb66856b4d848e5675f9ae4ec3f6`
- ZIP: `.tmp/menu/run-1z4n2zmh/p/Iris.zip`
- SHA256: `06edab60f62cce11fd2f85ae3f23e5584826bad8f4045721bf6b7836c01fc1b6`
- direct mod root: `C:\Users\MW\Downloads\coding\PZ\.tmp\menu\run-1z4n2zmh\p\Iris`
- 상태: **implemented_only**. 실제 PZ 미관찰. 이전 run-20rthxop 후보 보존. 라이브 설치·커밋·푸시 없음.


## 파스타 조리재료 및 물 보관 문형 공통 교정 (2026-09-13)

상태: **implemented_only**.

현재 exact ID와 채택된 Pasta eat_food의 원천 관측·normalized fact·공개 문장을 대조하고 grain 역할4개 및 물 공통함수49아이템을 확인했다. 변경51아이템/204좌표의 실제 KO/EN 네문자열 조합17개를 읽었다. 전면 원천 재조사·새 Gate는 수행하지 않았다.

- Base.Pasta는 원물의 native_eating accepted eat_food가 채택→normalized→공개 양표면에 이미 있었다. 섭취 근거 누락이 아니라 grain_preparation 재료 문장의 분리·자기명 반복 문제다.
- Pasta/Rice ingredient2를 요리 재료 상위 표현으로 정리했다. WaterPot/WaterSaucepan의 같은 활동에 속한 용기 역할은 유지한다. 원물과 조리 결과의 섭취를 혼동하거나 새로운 fact를 추가하지 않았다.
- 물 용기49의 store_water/carry_water/receive_poured_water 공통 요약을 공급 경로에 종속되지 않는 보관·운반 목적으로 썼다. WATER_STORAGE는 실제 수원 채우기 근거이고 WATER_TRANSFER는 별도 용기간 이송이다.
- 물받기 관계를 삭제하지 않고 특정 공급 경로만 필수처럼 읽히는 문구를 고쳤다. 물 옮기기·시설 및 작물 급수·차량 혈흔·소화·음용·오염수 위험과 다른 독립 용도를 보존한다. 모든 수원·자동 급수·정수 효과를 주장하지 않는다.

기준 0b7d82 대비 **51아이템/204좌표** 변경: ingredient2+water49. 전체2105/8420과 각 표면 present1981/absent124 유지.

원천 관측: `scripts/items_food.txt L4808-L4824`의 원물 Pasta(Type Food, CantEat 없음), 메뉴의 isCantEat 조건과 ISEatFoodAction의 Eat 호출이 채택 fact `fact:ad362bed7f802a635e26d823b7bfa378413b4e61f0a3ef568e3c3e30bf35790c`에 연결돼 있다. 공개 먹기 문장은 수정 전에도 존재했다.

**Base.Pasta**

KO 전: 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 파스타 요리 준비에 쓰는 재료.

KO 후: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.

EN 전: It can be eaten. It can also be used as trap bait. An ingredient for preparing dishes with Pasta.

EN 후: It can be eaten or used as a cooking ingredient. It can also be used as trap bait.

**Base.Rice**

KO 전: 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 쌀 요리 준비에 쓰는 재료.

KO 후: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.

EN 전: It can be eaten. It can also be used as trap bait. An ingredient for preparing dishes with Rice.

EN 후: It can be eaten or used as a cooking ingredient. It can also be used as trap bait.

**Base.Teacup**

KO 전: 다른 용기의 물을 받아 보관, 운반할 수 있다.

KO 후: 물을 담아 보관하거나 운반할 수 있다.

EN 전: It can store and carry water received from other containers.

EN 후: It can hold water for storage or carrying.

**Base.MugWhite**

KO 전: 다른 용기의 물을 받아 보관, 운반할 수 있다.

KO 후: 물을 담아 보관하거나 운반할 수 있다.

EN 전: It can store and carry water received from other containers.

EN 후: It can hold water for storage or carrying.

**Base.WaterBottleFull**

KO 전: 다른 용기의 물을 받아 보관, 운반하고 다른 용기로 옮길 수 있다. 담긴 물은 저장 시설 급수, 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

KO 후: 물을 담아 보관하거나 운반할 수 있다. 다른 용기로 물을 옮길 수도 있다. 담긴 물은 저장 시설 급수, 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

EN 전: It can store and carry water received from other containers and transfer it to other containers. Its water can be used for refilling water storage, watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

EN 후: It can hold water for storage or carrying. It can also transfer water to other containers. Its water can be used for refilling water storage, watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

Descriptions SHA256: `e18e90dc3091504284b0dcefcb779e810f28991fb0f1c76e14dd2ef58b01d560`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

기존 후보 run-1z4n2zmh와 앞선 승인 교정은 보존한다. 최종 검증·후보는 아래 완료 기록에 기재한다.


### 파스타·물 보관 문형 교정 최종 검증 및 후보

문구 고정 뒤 기존 최소3노드 묶음 한 번 실행: **3 passed in 169.15s (0:02:49)**, 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/pasta-water-tests.log`. Blocks 불변으로 별도 block 검사를 추가하지 않았다. 새 Gate·전면 원천 재조사·추가 confidence 검사는 없다.

- product: `l3p-2a40ddc81a714c19299ae03fc2c5b7a7c083eaaaf55131cf61f2453dd5d1fb63`
- ZIP: `.tmp/menu/run-gannsp5q/p/Iris.zip`
- SHA256: `aa54b655bb0cb06eb9e1eab0b1f896e9ec0e3eee920c1388e63e7e0b4e32b684`
- direct mod root: `C:\Users\MW\Downloads\coding\PZ\.tmp\menu\run-gannsp5q\p\Iris`
- 상태: **implemented_only**. 실제 PZ 미관찰. 이전 run-1z4n2zmh 후보 보존. 라이브 설치·커밋·푸시 없음.


## 능력 중심 문형 및 도구 범위 조사 — 수정 전 (2026-09-13)

현재 655개 네문구 그룹과 2005개 고유 현지화 segment를 전부 읽고, 공통 문법·일반 및 특수 frame·compact 요약·expanded remaining·effect/state·qualifier·fallback 생성 경로를 대조했다. 읽기용 문형 색인은 수정 대상 후보의 좌표 전사이며 변경 수치나 통과 판정이 아니다.

기준: `e18e90dc3091504284b0dcefcb779e810f28991fb0f1c76e14dd2ef58b01d560`. 전체2105아이템/8420좌표.

- 문형: 1265아이템 / 4136좌표
- 문형만: 1245아이템 / 4056좌표
- 의미상세: 1아이템 / 2좌표
- 모호범위: 20아이템 / 80좌표
- 문형_의미상세: 1아이템 / 2좌표
- 문형_모호범위: 20아이템 / 80좌표
- 의미상세_모호범위: 1아이템 / 2좌표
- union: 1265아이템 / 4136좌표

문형만은 의미상세·모호범위를 제외한 좌표다. 축별 수는 중복을 포함한다. 문형 색인 수는 수정 전 후보 수이며 실제 변경 수는 재생성 후 별도로 기록한다.

- ko/en.role의 역할 명사형 및 passive 표현, results._compact_materials의 supplies/material 설명
- uses.frames의 도구 개요, 의복 위치, 의료/용기/필기구/점화/음식 등 독립 특수 문구
- families.FUNCTION_FRAMES/OVERVIEWS/frames/packaging_frames와 lexicon의 inherited direct function 및 qualifier fallback에 남은 역할형
- fabric_recovery의 FABRIC_ACTION을 tool/material에 공통 투영해 가위 자신의 필요 조건과 실 회수 결과가 재설명됨
- moving_furniture 활동명이 실제 PickUpTool/PlaceTool 검사와 결합되지 않아 이동/가구 작업으로 모호하게 요약됨
- 채택 r6 semantic: scripts/recipes.txt L3761–3819 Rip Clothing Denim/Leather, keep Scissors, Result DenimStrips/LeatherStrips; material 공통 결과/수량/실 qualifier는 내부에 유지
- 채택 ISMoveableDefinitions addToolDefinition + ISMoveableSpriteProps PickUpTool/PlaceTool, hasTool, canPickUp/canPlace 및 ISMoveablesAction. scrap은 별도 getScrapDefinition 분기라 moving_furniture에서 해체를 주장하지 않음
- 의복 material에는 데님/가죽 가위 조건과 실제 strips 결과를 유지한다. 가위 tool에만 관련 없는 조건/결과 상세를 제외한다.
- 가구 운반·모든 가구 지원·구체 가구 목록·해체는 추가하지 않는다. 별도 dismantle_built_object 기능은 기존 근거로 독립 보존한다.
- 장전15%의 탄종/착용 범위, 낚싯줄 파손의 실제 결과, 제작 마모, 엔진 상태>10→0, 시비4회 후 부패, 씨앗50개, 통조림 실제 결과명/섭취/요리 차이 등은 사실·조건을 가능성으로 약화하지 않는다.
- 타이어 중복처럼 보여도 설치/주행/공기·상태·손실 조건은 의미 구분이 있으므로 상세 삭제하지 않는다. 바늘 패치 회수 가능성과 의료 조건도 보존한다.
- 부서진 어망의 철사 회수량 미확정, 기존 음식 결과 보류2, 차량42 목적 미확정, absent124, unresolved 및 L4 공급 공백 유지.
- 이미 can/할 수 있다 중심인 통조림29와 Pasta/Rice 및 물49 등의 승인 교정은 의미를 유지한다. compact는 짧은 요약을 유지하되 명사 조각 종결을 능력 문장으로 바꾼다.

현재 단계는 조사 완료이며 producer·테스트·패키징 미실행. 실제 PZ 미관찰.


## 능력 중심 문형 공통 교정 — 구현 (2026-09-13)

상태: **implemented_only**.

수정 전 전체2105/8420 문구를 읽고 공통 생성 경로를 대조했다. 문형 색인1265/4136과 실제변경1302/4377을 분리한다. 최초 색인에 없던 보조도구/원격연결/일부 fallback 및 공통 문법의 파급은 실제 재생성 차이에 포함한다. 실제 대표13개의 KO/EN 네표면을 읽었고 재료 조사의 연결 오류와 가위 callback 목적 미적용, compact 길이를 발견해 교정했다. 키워드가 사라진 것만으로 전체 품질 PASS를 주장하지 않는다.

- 공통 role 문법, uses 특수 목적 및 compact 도구 개요, families 기능/학습/포장 fallback, results 재료 요약, lexicon 기능/qualifier를 능력 중심으로 작성했다. 출력 어미 일괄치환이나 FullType 문장 override는 없다.
- 가위 tool은 채택 FABRIC_ACTION+tool 역할로 데님/가죽 의류의 조각 회수 목적을 표현한다. callback 결과가 recipe_targets에 없는 경우도 이 닫힌 조건으로 처리한다. 실 회수와 가위 자기요건은 내부에 남고, 의복 material의 가위 조건 및 실제 strips 결과명은 유지한다.
- 가구20개: 개별선언 ID/Tag→parseItemTypes→공통 addToolDefinition; 같은 등록표를 PickUpTool/PlaceTool 양쪽 hasTool 검사에서 사용한다. 한쪽만 허용하는 도구 등록은 없다. 일부 가구의 집기/설치로 제한하며, 별도 scrap 및 운반 기능은 추론하지 않는다.
- compact의 재료·도구 묶음은 짧게 유지하고 expanded는 독립 목적을 나눈다. 창 부착물 회수/산탄총 총신 단축은 가공대상이라는 역할 설명을 해당 작업의 능력 문장으로 작성하고 기존 후속 조건·결과를 보존한다.
- 장전15%의 착용/탄종 범위, 장비 슬롯 제공, 낚싯줄 파손 결과, 창 제작 마모, 엔진>10→0, 씨앗50, 시비4회 후 부패, 항생제 좀비화불가 등은 확정값/조건/위험을 임의 가능성으로 약화하지 않는다.
- 통조림 실제 결과명·섭취와 요리 구분, Pasta/Rice 먹기·미끼·요리, 물49 보관/운반과 공급경로 구분, 낮은 음식결과 생략, 선택적 식기 내부화, 짧은 물기닦기, 가운데점 제거 등 앞선 승인 교정을 보존한다.

Descriptions SHA256: `1abe69a28130420aae4bd9da3f602202305fa950711c235db2139994bb6d263a`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.Scissors — 실제 생성 문구**

KO compact: 데님이나 가죽 의류의 조각 회수, 일부 가구 집기와 설치, 머리와 수염 손질에 사용할 수 있다. 제작한 창에 부착하거나 근접 공격에 사용할 수도 있다.

KO expanded: 데님이나 가죽 의류를 잘라 조각을 회수할 수 있다. / 일부 가구를 집어 들거나 설치하는 데 사용할 수 있다. / 머리를 손질할 수 있다. / 수염을 다듬거나 면도할 수 있다. / 제작한 창에 부착해 쓸 수 있다. / 근접 공격에 사용할 수 있다.

EN compact: It can be used for recovering strips from denim or leather clothing; picking up or placing certain furniture; hair and beard grooming. It can also be attached to a crafted spear or be used for melee attacks.

EN expanded: It can be used to cut denim or leather clothing into strips. / It can be used to pick up or place certain furniture. / It can be used to groom hair. / It can be used to trim or shave a beard. / It can be attached to a crafted spear. / It can be used for melee attacks.

**Base.Hammer — 실제 생성 문구**

KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 일부 가구 집기와 설치, 수박 쪼개기, 문과 창문의 판자 바리케이드 설치와 철거에 사용할 수 있다. 근접 공격에 사용할 수도 있다.

KO expanded: 금속을 단조하는 데 사용할 수 있다. / 목공 작업에 사용할 수 있다. / 건축 작업에 사용할 수 있다. / 일부 가구를 집어 들거나 설치하는 데 사용할 수 있다. / 문과 창문의 판자 바리케이드를 설치하거나 철거할 수 있다. / 수박 쪼개기에 사용할 수 있다. / 근접 공격에 사용할 수 있다.

EN compact: It can be used for metal forging. It can be used for woodworking and construction; picking up or placing certain furniture; breaking a watermelon; installing or removing plank barricades on doors and windows. It can also be used for melee attacks.

EN expanded: It can be used for metal forging. / It can be used for woodworking. / It can be used for construction. / It can be used to pick up or place certain furniture. / It can be used to install or remove plank barricades on doors and windows. / It can be used for breaking a watermelon. / It can be used for melee attacks.

**Base.DenimStrips — 실제 생성 문구**

KO compact: 응급처치와 의류 수선에 쓰거나 제작 재료로 사용할 수 있다.

KO expanded: 세척이 필요한 화상을 씻는 붕대 재료로 사용할 수 있다. / 상처에 붕대를 대는 재료로 사용할 수 있다. 재료가 감염되어 있으면 상처를 감염시킬 수 있다. / 부목 제작에 재료로 사용할 수 있다. / 의류의 구멍을 덧대거나 패딩을 추가할 수 있다. / 화염 장치 제작에 재료로 사용할 수 있다. / 석제 도구 제작에 재료로 사용할 수 있다.

EN compact: It can be used as material for first aid, clothing repairs, and crafting.

EN expanded: It can be used as bandaging material for cleaning burns that need washing. / It can be used as material for bandaging wounds. Infected material can infect the wound. / It can be used as a material for splint crafting. / It can be used to patch garment holes or add padding. / It can be used as a material for making incendiary devices. / It can be used as a material for stone-tool crafting.

**Base.Pills — 실제 생성 문구**

KO compact: 통증 완화를 위해 복용할 수 있다.

KO expanded: 통증 완화를 위해 복용할 수 있다.

EN compact: It can be taken for pain relief.

EN expanded: It can be taken for pain relief.

**Base.Socks_Ankle — 실제 생성 문구**

KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 양말을 시트 로프 제작 재료나 연료, 불쏘시개로도 쓸 수 있다.

KO expanded: 양말 자리에 착용할 수 있다. / 찢어서 찢어진 천 또는 찢어진 천 (오염됨)을 얻을 수 있다. / 양말을 시트 로프 제작 재료로 쓸 수 있다. / 모닥불, 비프로판 바비큐, 벽난로의 연료로 소모할 수 있다. / 모닥불, 비프로판 바비큐, 벽난로, 통나무가 든 드럼의 불쏘시개로 소모할 수 있다.

EN compact: It can be worn or ripped to obtain cloth scraps, used directly to make sheet rope, or used as fuel and tinder.

EN expanded: It can be worn in the socks equipment slot. / It can be ripped to obtain Ripped Sheets or Dirty Rag. / The Socks can be used as material for making sheet rope. / It can be consumed as fuel for campfires and non-propane barbecues and fireplaces. / It can be consumed as tinder for campfires, non-propane barbecues and fireplaces, and drums containing logs.

**Base.BookCarpentry1 — 실제 생성 문구**

KO compact: 책의 기술 범위에 맞는 독자의 목공 경험치 배율을 높일 수 있다. 완독 시 최대 3배다. 연료나 불쏘시개로 쓸 수 있다.

KO expanded: 책의 기술 범위에 맞는 독자의 목공 경험치 배율을 높일 수 있다. 완독 시 최대 3배다. / 모닥불, 비프로판 바비큐, 벽난로의 연료로 소모할 수 있다. / 모닥불, 비프로판 바비큐, 벽난로, 통나무가 든 드럼의 불쏘시개로 소모할 수 있다.

EN compact: It can raise carpentry XP multipliers within its supported skill range. Full reading reaches up to 3×. It can be used as fuel or tinder.

EN expanded: It can raise the carpentry XP multiplier for readers within its supported skill range. Full reading reaches up to 3×. / It can be consumed as fuel for campfires and non-propane barbecues and fireplaces. / It can be consumed as tinder for campfires, non-propane barbecues and fireplaces, and drums containing logs.

**Base.SpearScissors — 실제 생성 문구**

KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창의 부착물을 회수할 수 있다. 창 (가위)는 근접 공격에 쓸 수 있다.

KO expanded: 물가에서 미끼 없이 창낚시에 쓸 수 있다. / 창의 부착물을 회수할 수 있다. 이때 파괴된 창에서도 부착물과 제작한 창을 회수할 수 있다. / 창 (가위)는 근접 공격에 사용할 수 있다.

EN compact: Spear With Scissors can be used for spear fishing at water without bait. Its spear attachment can be recovered. Spear With Scissors can be used for melee attacks.

EN expanded: Spear With Scissors can be used for spear fishing at water without bait. / Its spear attachment can be recovered. The attachment and a crafted spear can be recovered even from a destroyed spear. / Spear With Scissors can be used for melee attacks.

**Base.CannedCorn — 실제 생성 문구**

KO compact: 통조림 따개로 개봉해 옥수수를 먹을 수 있다. 꺼낸 옥수수를 요리 재료로도 쓸 수 있다.

KO expanded: 통조림 따개로 개봉해 옥수수를 먹을 수 있다. / 꺼낸 옥수수를 요리 재료로도 쓸 수 있다.

EN compact: It can be opened with a Can Opener to eat the Corn. The extracted Corn can also be used as a cooking ingredient.

EN expanded: It can be opened with a Can Opener to eat the Corn. / The extracted Corn can also be used as a cooking ingredient.

**Base.Pasta — 실제 생성 문구**

KO compact: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.

KO expanded: 먹을 수 있다. / 덫의 미끼로 쓸 수 있다. / 요리 재료로 쓸 수 있다.

EN compact: It can be eaten or used as a cooking ingredient. It can also be used as trap bait.

EN expanded: It can be eaten. / It can be used as trap bait. / It can be used as a cooking ingredient.

이전 run-gannsp5q와 모든 이전 후보·교정 기록을 보존한다. 마지막 최소 검사·후보는 아래 완료 기록에 기재한다. 실제 PZ 미관찰.


검사 전 영향 문면 확인: 전체 4377 변경 좌표의 before/after 고유수정조각296개 및 주변문구를 읽고, 최초색인밖100아이템/241좌표의 전체문구를 읽었다. 신규37아이템+기존63아이템의 추가표면. Bowl의 divide 의미 약화를 발견해 검사 전 복원했다. 마지막 원문은 위 최종 SHA에 해당하며 대표13만으로 전수 품질 수락을 주장하지 않는다.


### 능력 중심 문형 공통 교정 최종 검증 및 후보

문구 고정 뒤 기존 최소3노드 묶음 한 번 실행: **3 passed in 139.11s (0:02:19)**, 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/capability-tests.log`. Blocks 불변으로 별도 block 검사를 추가하지 않았다. 새 Gate·전면 원천 재조사·추가 confidence 검사는 없다.

- product: `l3p-066eb82436c04a645a94850605501323831b69e779db260ec09e2c376d315485`
- ZIP: `.tmp/menu/run-yp219v2y/p/Iris.zip`
- SHA256: `70fe2da4beb47f981d9c18c202fcb2517c8c777371a41c1c553580258702be96`
- direct mod root: `C:\Users\MW\Downloads\coding\PZ\.tmp\menu\run-yp219v2y\p\Iris`
- 상태: **implemented_only**. 실제 PZ 미관찰. 이전 run-gannsp5q 후보 보존. 라이브 설치·커밋·푸시 없음.


## 무기 용도 문형 공통 교정 — 구현 (2026-09-13)

상태: **implemented_only**.

수정 전 melee_attack 공개 참조로114아이템/456좌표를 확인했다. 실제 변경도 정확히114/456이며 전체 변경의17고유차이와 주변문구를 읽었다. 일반형, 도구 복합형, 창부착형, 재료 복합형 및 실제 이름 주어형을 확인했다.

- admitted melee_attack의 공개 용도를 무기로 쓸 수 있다 / It can be used as a weapon으로 표현한다. 일반 expanded/compact, 도구와 창부착의 복합compact, 재료와 골절고정의 복합compact에 공통 적용했다.
- 새로운 무기 역할이나 총기 기능을 추가하지 않았다. 114아이템의 원본 fact, qualifier, 독립 용도와 부착 관계를 보존했다. 복합 문장의 조사만 해당 의미 경로에서 작성하며 완성 문구 전역 치환은 없다.
- 기준1abe69와 이전 run-yp219v2y 후보 및 기존 교정 기록은 보존한다. 가운데점 제거, 가위/가구 범위와 수치·상태·실제 결과명·섭취/조리 구분도 유지한다.

Descriptions SHA256: `cc25b4596aa5d3d3ec0fd43a00da80ba9390ed3c31285a117465a6c7edad982c`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.BadmintonRacket — 실제 생성 문구**

KO compact: 무기로 쓸 수 있다.

KO expanded: 무기로 쓸 수 있다.

EN compact: It can be used as a weapon.

EN expanded: It can be used as a weapon.

**Base.Scissors — 실제 생성 문구**

KO compact: 데님이나 가죽 의류의 조각 회수, 일부 가구 집기와 설치, 머리와 수염 손질에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

KO expanded: 데님이나 가죽 의류를 잘라 조각을 회수할 수 있다. / 일부 가구를 집어 들거나 설치하는 데 사용할 수 있다. / 머리를 손질할 수 있다. / 수염을 다듬거나 면도할 수 있다. / 제작한 창에 부착해 쓸 수 있다. / 무기로 쓸 수 있다.

EN compact: It can be used for recovering strips from denim or leather clothing; picking up or placing certain furniture; hair and beard grooming. It can also be attached to a crafted spear or be used as a weapon.

EN expanded: It can be used to cut denim or leather clothing into strips. / It can be used to pick up or place certain furniture. / It can be used to groom hair. / It can be used to trim or shave a beard. / It can be attached to a crafted spear. / It can be used as a weapon.

**Base.Hammer — 실제 생성 문구**

KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 일부 가구 집기와 설치, 수박 쪼개기, 문과 창문의 판자 바리케이드 설치와 철거에 사용할 수 있다. 무기로도 쓸 수 있다.

KO expanded: 금속을 단조하는 데 사용할 수 있다. / 목공 작업에 사용할 수 있다. / 건축 작업에 사용할 수 있다. / 일부 가구를 집어 들거나 설치하는 데 사용할 수 있다. / 문과 창문의 판자 바리케이드를 설치하거나 철거할 수 있다. / 수박 쪼개기에 사용할 수 있다. / 무기로 쓸 수 있다.

EN compact: It can be used for metal forging. It can be used for woodworking and construction; picking up or placing certain furniture; breaking a watermelon; installing or removing plank barricades on doors and windows. It can also be used as a weapon.

EN expanded: It can be used for metal forging. / It can be used for woodworking. / It can be used for construction. / It can be used to pick up or place certain furniture. / It can be used to install or remove plank barricades on doors and windows. / It can be used for breaking a watermelon. / It can be used as a weapon.

**Base.Plank — 실제 생성 문구**

KO compact: 목공과 건축이나 다른 물품을 만드는 재료로 사용할 수 있다. 골절 고정에 쓸 수 있다. 무기로도 쓸 수 있다. 연료로도 쓸 수 있다.

KO expanded: 목공 작업에 재료로 사용할 수 있다. / 건축 작업에 재료로 사용할 수 있다. / 모닥불 키트 제작에 재료로 사용할 수 있다. / 가구 부품 제작에 재료로 사용할 수 있다. / 톱 제작 재료로 사용할 수 있다. / 창 제작에 재료로 사용할 수 있다. / 머리와 몸통을 제외한 부위의 골절에 부목을 대는 데 쓸 수 있다. / 부목 제작에 재료로 사용할 수 있다. / 덫 제작에 재료로 사용할 수 있다. / 수박 쪼개기에 사용할 수 있다. / 무기로 쓸 수 있다. / 모닥불, 비프로판 바비큐, 벽난로의 연료로 소모할 수 있다.

EN compact: It can be used as material for woodworking, construction, and crafting. It can also be used for splinting fractures. It can also be used as a weapon. It can also be used as fuel.

EN expanded: It can be used as a material for woodworking. / It can be used as a material for construction. / It can be used as a material for campfire-kit crafting. / It can be used as a material for furniture-part crafting. / It can be used as material for making Saw. / It can be used as a material for spear crafting. / It can help splint fractures outside the head and torso. / It can be used as a material for splint crafting. / It can be used as a material for trap crafting. / It can be used for breaking a watermelon. / It can be used as a weapon. / It can be consumed as fuel for campfires and non-propane barbecues and fireplaces.

**Base.SpearScissors — 실제 생성 문구**

KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창의 부착물을 회수할 수 있다. 창 (가위)는 무기로 쓸 수 있다.

KO expanded: 물가에서 미끼 없이 창낚시에 쓸 수 있다. / 창의 부착물을 회수할 수 있다. 이때 파괴된 창에서도 부착물과 제작한 창을 회수할 수 있다. / 창 (가위)는 무기로 쓸 수 있다.

EN compact: Spear With Scissors can be used for spear fishing at water without bait. Its spear attachment can be recovered. Spear With Scissors can be used as a weapon.

EN expanded: Spear With Scissors can be used for spear fishing at water without bait. / Its spear attachment can be recovered. The attachment and a crafted spear can be recovered even from a destroyed spear. / Spear With Scissors can be used as a weapon.

이전 run-yp219v2y와 모든 이전 후보·교정 기록을 보존한다. 마지막 최소 검사·후보는 아래 완료 기록에 기재한다. 실제 PZ 미관찰.


### 무기 용도 문형 공통 교정 최종 검증 및 후보

문구 고정 뒤 기존 최소3노드 묶음 한 번 실행: **3 passed in 143.71s (0:02:23)**, 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/weapon-tests.log`. Blocks 불변으로 별도 block 검사를 추가하지 않았다. 새 Gate·전면 원천 재조사·추가 confidence 검사는 없다.

- product: `l3p-db1faa84039f1840c907f006be53e2ff9322befa8f6da4ca68f389597a6a8755`
- ZIP: `.tmp/menu/run-6bt0yuh8/p/Iris.zip`
- SHA256: `21bed8da7bda2b0c0cfd5e92b3e6719735f7ba283fedd90b47c98d0ea9719b4a`
- direct mod root: `C:\Users\MW\Downloads\coding\PZ\.tmp\menu\run-6bt0yuh8\p\Iris`
- 상태: **implemented_only**. 실제 PZ 미관찰. 이전 run-yp219v2y 후보 보존. 라이브 설치·커밋·푸시 없음.


## 2026-09-13 기존 공통 규칙 적용 누락 교정

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

기준 cc25b459의 전체 2,105개 활동·기능·역할을 순회해 같은 합성 경로를 조사했다. 변경 전후의 KO/EN 고유 segment 715그룹과 후속 delta 140그룹을 읽고, 주요 복합 아이템의 네 전체 문면을 대조했다. 동일 문장에 들어가는 기존 원물 이름은 변수로 묶어 읽었다. 이는 기존 입력에 대한 공통 의미/문면 교정이며 원천 사실 전수 재감사, EN 독립 품질 수락 또는 인게임 수락이 아니다.

실제 문면 변경: **735아이템 / 2466좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 사용자 확정 지시를 기존 공통 uses/families/lexicon/results 경로에 적용했다. FullType 완성 문장 override나 생성 JSON 수동 패치, 런타임 의미 재작성기는 없다.
- 라디오12종과 TV3종은 주파수/채널 선택 대신 방송 청취/시청을 설명한다. 전원과 내용에 따른 효과 조건은 보존한다.
- 붕대 준비11종의 역할을 대조했다. 붕대 자체의 소독, 솜의 소독솜 제작, 소독 공급물과 물 용기, 이미 있는 세척 경로를 구별한다. 물 용기에 솜 소독이나 끓는 온도 보장을 발명하지 않는다. 생선7종은 손질 대상과 무게>0.6 조건을 보존하고 작은 동물5종은 고기 획득으로 표현한다. 수박 대상과 도구9종을 구별하며, Plank compact에 빠졌던 수박 쪼개기도 복원한다.
- 전자 제작의 여러 결과/버전은 전자 부품 등 확인된 목적군으로 묶는다. 단일 결과가 용도를 식별하는 경우와 원격제어 조정기만 만드는 경우의 이름은 보존한다. 달걀은 달걀곽 포장 용도를 직접 표현한다.
- 목공/건축의 같은 재료 역할과 분리 context를 함께 묶고, compact의 제작 및 호환 물품 수리 범위를 공유한다. 포장, 로프 고정, 손질 대상, 연료, 무기 등 독립 활용은 따로 남긴다. Shovel 계열은 밭 작업과 무덤 파기/메우기, 재 청소, 담기로 묶고 수확 제외를 보존한다.
- 조리 용기의 쌀/파스타/반죽 준비를 조리 활용 안에서 묶고, 반죽에 넣는 재료와 만드는 도구/용기 역할은 구별한다. 물 보관/운반 문장은 그대로 두며 다른 용기/저장 시설로 옮기는 공급 경로만 함께 표현한다.
- 낚싯대 파손 후 제작품/완제품별 남는 물품 산정은 삭제했다. 파손과 미끼 손실은 보존한다. 창 마모 인과관계, 통나무 반환, 신선도/보존, 타이어 등 기존 보류를 일괄 삭제하거나 새 관계로 확정하지 않았다.
- 의복의 슬롯식 표현과 착용 형태 변경, 기술서의 경험치 배율 문형, 지면 재료 깔기, 약초 찜질제의 도구/재료 문형을 고쳤다. 천/의복의 시트 로프 제작은 찢기 전 원물을 주어로 명시한다.
- 차량 좌석/연료탱크12종은 설치 대상이라는 공통 역할만 호환 차량에 장착할 수 있다로 표현한다. 구체 차량 기능42종의 미확정 범위를 해소했다고 주장하지 않는다.
- 통조림 실제 내용물과 개봉 도구/음용/식용/조리 구분, Pasta/Rice 식용/요리/미끼, 물 보관/운반, 가위 데님/가죽 및 가구 집기/설치, 무기 문형과 S3 획득/Acquisition 변경을 보존한다.
- 각 locale/surface present1981, absent124 유지. absent는 품질 수락 수가 아니다.
- 차량42 구체 목적, 기존 unresolved/보류 및 exact ID L4 공급 공백 유지.
- 실제 PZ의 KO/EN 글꼴, Tooltip 네 물리줄과 S1/S3/S4, Browser/Wiki 스크롤/메뉴 표시는 미관찰.
- 저장소 밖 설치, live/current 전환, commit/push, 전체 Run A/B, 새 validation authority는 수행하지 않는다.

Descriptions SHA256: `8ea9a317292ae25ce5ee0221c0fb5b8074707705950b492ee9b7694b34b0c1e1`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Radio.RadioBlack**

Before KO compact: 밸류테크 라디오는 전원이 공급되면 방송 주파수 선택에 쓸 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After KO compact: 밸류테크 라디오는 전원이 공급되면 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After EN compact: With power, ValuTech Radio can be used for listening to radio broadcasts. Depending on the content, it can affect stats, XP or recipe knowledge. It can be dismantled with a screwdriver to recover electronic parts.

**Base.Bandage**

Before KO compact: 화상 세척 재료로 쓸 수 있다. 상처에 붕대를 대는 재료로 사용할 수 있다. 재료가 감염되어 있으면 상처를 감염시킬 수 있다. 붕대 재료 소독에 재료로 사용할 수 있다.

After KO compact: 화상 세척에 쓸 수 있다. 상처에 붕대를 대는 재료로 사용할 수 있다. 재료가 감염되어 있으면 상처를 감염시킬 수 있다. 소독해 상처에 댈 수 있다.

After EN compact: It can be used for cleaning burns. It can be used as material for bandaging wounds. Infected material can infect the wound. It can be disinfected for bandaging wounds.

**Base.Splint**

Before KO compact: 부목 재료로 쓸 수 있다.

After KO compact: 골절 고정에 쓸 수 있다.

After EN compact: It can be used for splinting fractures.

**Base.Screwdriver**

Before KO compact: 간이 무전기 제작, 전자기기 분해 및 조명 개조, 목공 및 건축물 분해, 원격제어 조정기, 폭탄 타이머 (수제작), 원격 폭탄 격발기 (수제작) 제작, 일부 가구 집기와 설치, 차량, 무기 부품 장착, 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 일부 가구 집기와 설치, 차량, 무기 부품 장착, 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can be used for making and dismantling electronic devices, plus lamp conversion to battery power; woodworking, plus structure disassembly; picking up or placing certain furniture; fitting and removing vehicle and weapon parts. It can also be attached to a crafted spear or be used as a weapon.

**Base.Nails**

Before KO compact: 호환되는 손상 물품의 수리 재료로 사용할 수 있다. 모아서 상자로 포장할 수 있다. 위층 창문 등에 탈출용 로프를 고정할 수 있다. 목공에 재료로 사용할 수 있다. 건축 작업에 재료로 사용할 수 있다. 문과 창문에 판자 바리케이드를 설치할 수 있다. 낚시 장비 제작, 가구 부품 제작, 덫 제작에 재료로 사용할 수 있다.

After KO compact: 목공, 건축, 물품 제작, 호환 물품 수리의 재료로 쓸 수 있다. 모아서 상자로 포장할 수 있다. 위층 창문 등에 탈출용 로프를 고정할 수 있다.

After EN compact: It can be used as material for woodworking, construction, crafting, and repairing compatible items. It can be collected and packed into a box. It can be used to anchor an escape rope at an upper-floor window or similar attachment.

**Base.WaterPot**

Before KO compact: 물을 담아 보관하거나 운반할 수 있다. 다른 용기로 물을 옮길 수도 있다. 담긴 물은 저장 시설 급수, 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다. 재료를 더해 요리를 만들 수도 있다 (오염수 음용은 중독 위험). 붕대 재료 소독에 재료로 사용할 수 있다. 쌀, 파스타 준비에 용기로 사용할 수 있다.

After KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 담아 보관하거나 운반할 수 있다. 다른 용기나 저장 시설로 물을 옮길 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After EN compact: It can be used to disinfect bandaging. It can hold ingredients for cooking. It can hold water for storage or carrying. It can transfer water to other containers or storage fixtures. Its water can be used for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

**Base.Sheet**

Before KO compact: 찢어서 찢어진 천 또는 찢어진 천 (오염됨)을 얻을 수 있다. 천을 시트 로프 제작 재료로 쓸 수 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 설치 후 열고 닫거나 떼어낼 수 있다. 모닥불 키트 제작, 매트리스 제작에 재료로 사용할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 찢어서 찢어진 천 또는 찢어진 천 (오염됨)을 얻을 수 있다. 찢기 전 천을 시트 로프 제작 재료로 쓸 수 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 설치 후 열고 닫거나 떼어낼 수 있다. 모닥불 키트 제작, 매트리스 제작에 재료로 사용할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be ripped to obtain Ripped Sheets or Dirty Rag. The intact Sheet can be used as material for making sheet rope. It can be installed as a curtain on an eligible window or door without one; the installed curtain can be opened, closed or removed. It can be used as a material for campfire-kit crafting and mattress crafting. It can be used as fuel or tinder.

**Base.Bass**

Before KO compact: 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 생선 손질에 재료로 사용할 수 있다.

After KO compact: 먹을 수 있다. 덫의 미끼로도 쓸 수 있다. 생선을 손질해 살을 얻을 수 있다.

After EN compact: It can be eaten. It can also be used as trap bait. It can be filleted.

**Base.CraftedFishingRod**

Before KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 낚싯대가 부러지거나 막대로 바뀌며 미끼를 잃는다. 무기로 쓸 수 있다.

After KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 낚싯대가 부러지거나 막대로 바뀌며 미끼를 잃는다. 무기로 쓸 수 있다.

After EN compact: It can be used for rod fishing at water with matching bait. A broken line changes the rod into a broken rod or stick and loses the bait. It can be used as a weapon.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-bcwd4x0i/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 공통 규칙 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 131.14s (0:02:11)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/common-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-f2wnvz9w/p/Iris.zip`
- SHA256: `c9f8a5615caebf392d66c99fc6c9e98ca5e844820e7fbfa9a1953d40b40be011`
- product: `l3p-a420c7486a7a6dcba1e2ada08e8c09d7b5a25eb65b85046f3b600c0f488171f6`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-bcwd4x0i 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 후속 문형 및 입력 역할 경계 교정

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

직전 8ea9a317 결과를 기준으로 후속 교정의 KO/EN 고유 변경 segment 94그룹을 모두 읽었다. 역할별 내부/공개 경계를 대조했으며 자동 검사와 문면 검토, 실제 게임 수락을 구별한다.

실제 문면 변경: **84아이템 / 234좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- Socks/Shoes는 발에 신기, 장갑은 손에 끼기, 목걸이/스카프/벨트/안경은 같은 공통 착용 경로의 신체 부위와 동사로 표현한다.
- 붕대는 상처에 감는 활용 안에 소독 대안을 합쳤다. 감염된 붕대의 상처 감염 조건은 보존하고 화상 세척은 독립 활용으로 유지한다.
- Sheet compact는 천 조각 회수와 찢기 전 원물의 시트 로프 제작을 대안으로 연결한다. expanded의 정확한 회수 결과는 보존한다. 같은 재료의 제작 활용을 compact에서 묶으며 설치한 커튼의 후속 조작은 내부에 둔다.
- 차량과 무기 부품의 장착과 제거는 명시적 접속사로 구별한다.
- 음식 분할/수박 쪼개기의 ingredient/material 입력 역할은 원물의 단순 가공 상세로 내부에 둔다. 이번 추가 대상은 Base.Watermelon과 Base.Muffintray_Biscuit이며 기존 미끼 용도를 유지한다. 식용/조리 용도를 추가하지 않는다.
- 실제 가공 도구 역할, 천 회수, 통조림 내용물 개봉 활용은 보존한다. Plank는 확인된 수박 쪼개기 도구 활용 그대로 두며 일반 음식 손질로 확대하지 않는다.
- 기존 공통 producer만 변경했다. FullType 완성 문장 override, 생성 JSON 수동 패치 또는 새 검증 권한을 도입하지 않았다.
- 각 locale/surface present1981, absent124 유지.
- 차량42 구체 목적, 기존 unresolved/보류 및 exact ID L4 공급 공백 유지.
- EN 독립 품질 수락 및 실제 PZ 글꼴/물리줄/메뉴 관찰은 수행하지 않았다.
- 기존 수정과 검사/후보 기록을 보존한다. 외부 설치, commit/push, 전체 Run A/B 또는 추가 confidence 실행 없음.

Descriptions SHA256: `1014c47c8596aa483ded11ca67440ad8c195fb04e00cf413c07c8fafa9fba36a`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.Socks_Ankle**

Before KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 양말을 시트 로프 제작 재료나 연료, 불쏘시개로도 쓸 수 있다.

After KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 양말을 시트 로프 제작 재료나 연료, 불쏘시개로도 쓸 수 있다.

After EN compact: It can be worn or ripped to obtain cloth scraps, used directly to make sheet rope, or used as fuel and tinder.

**Base.Bandage**

Before KO compact: 화상 세척에 쓸 수 있다. 상처에 붕대를 대는 재료로 사용할 수 있다. 재료가 감염되어 있으면 상처를 감염시킬 수 있다. 소독해 상처에 댈 수 있다.

After KO compact: 화상 세척에 쓸 수 있다. 상처에 감을 수 있다. 소독해서 쓸 수도 있다. 감염된 붕대를 쓰면 상처를 감염시킬 수 있다.

After EN compact: It can be used for cleaning burns. It can be wrapped around wounds. It can also be disinfected before use. An infected bandage can infect the wound.

**Base.Screwdriver**

Before KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 일부 가구 집기와 설치, 차량, 무기 부품 장착, 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 일부 가구 집기와 설치, 차량과 무기의 부품 장착과 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can be used for making and dismantling electronic devices, plus lamp conversion to battery power; woodworking, plus structure disassembly; picking up or placing certain furniture; fitting and removing parts on vehicles and weapons. It can also be attached to a crafted spear or be used as a weapon.

**Base.Sheet**

Before KO compact: 찢어서 찢어진 천 또는 찢어진 천 (오염됨)을 얻을 수 있다. 찢기 전 천을 시트 로프 제작 재료로 쓸 수 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 설치 후 열고 닫거나 떼어낼 수 있다. 모닥불 키트 제작, 매트리스 제작에 재료로 사용할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻거나, 찢기 전 천을 시트 로프 재료로 쓸 수 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be used as material for crafting. It can be ripped for cloth scraps or used intact to make sheet rope. It can be installed as a curtain on an eligible window or door without one. It can be used as fuel or tinder.

**Base.Watermelon**

Before KO compact: 수박은 깨뜨려 박살난 수박을 얻을 수 있다. 나누어 수박 조각을 얻을 수 있다. 수박은 덫의 미끼로 쓸 수 있다.

After KO compact: 덫의 미끼로 쓸 수 있다.

After EN compact: It can be used as trap bait.

**Base.Muffintray_Biscuit**

Before KO compact: 나누어 비스킷을 얻을 수 있다. 익었거나 탄 트레이에서 꺼낸다. 나누기 전 음식은 덫의 미끼로 쓸 수 있다.

After KO compact: 덫의 미끼로 쓸 수 있다.

After EN compact: It can be used as trap bait.

**Base.Plank**

Before KO compact: 목공과 건축이나 다른 물품을 만드는 재료로 사용할 수 있다. 골절 고정이나 수박 쪼개기에 쓸 수 있다. 무기로도 쓸 수 있다. 연료로도 쓸 수 있다.

After KO compact: 목공과 건축이나 다른 물품을 만드는 재료로 사용할 수 있다. 골절 고정이나 수박 쪼개기에 쓸 수 있다. 무기로도 쓸 수 있다. 연료로도 쓸 수 있다.

After EN compact: It can be used as material for woodworking, construction, and crafting. It can also be used for splinting fractures and breaking a watermelon. It can also be used as a weapon. It can also be used as fuel.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-f2wnvz9w/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 후속 문형 및 역할 경계 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 133.73s (0:02:13)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/refine-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-eek7qzgg/p/Iris.zip`
- SHA256: `01ca01730f67e2de24c101def308ce643f07c3828f035ef6283a16ba32543e73`
- product: `l3p-505c60d31143b06b96c05ee070f7971c33dd985492d86bcf868ad9d172a0d5cf`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-f2wnvz9w 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 전체 자기 이름 반복 공통 문형 교정

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

직전 1014c47c 결과를 기준으로 전체 이름 일치 98문형과 최종 잔여 44문형을 읽고, 변경 Before/After의 고유 segment 135그룹을 전부 대조했다. 긴 양말·티셔츠·Sheet·전자기기·창의 네 전체 문면을 읽었다. 문자열 일치 수는 검토 후보이며 오류 또는 품질 수락 수가 아니다.

실제 문면 변경: **279아이템 / 1012좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 전체 2,105개 아이템의 KO/EN compact/expanded 8,420좌표를 조사했다. 자기 이름 문자열이 있는 282개/98문형을 대조하고 display_names/subject_names를 사용하는 공통 producer 경로를 조사했다.
- 의류 compact에서 자기 이름을 생략하고 천 회수와 찢지 않은 상태의 로프 제작을 별개 대안으로 표현한다. expanded에서도 찢지 않은 원물 상태를 유지하고 자기 이름 대신 EN It을 사용한다. KO 이 아이템/이것/그것으로 대체하지 않는다.
- 분해/변형이 있는 아이템에 display name을 일괄 덧붙이던 공통 처리를 제거했다. 전자기기/탄약은 분해 전, 병은 깨기 전, 부착물 창은 분리 전 상태 관계로 표현한다. 결과물의 활용으로 읽히지 않도록 상태는 보존한다.
- 같은 기준으로 지도/거울/통나무/그릇/설치 자물쇠/로프와 낚싯대 파손/돌 도구 마모·손실/붕대 감염/골절 고정의 자기 이름 반복을 교정했다. 조건·결과·독립 활용의 사실 결속은 유지한다.
- 통조림 실제 내용물, 소독솜/개구리 고기/찢어진 천/제작 타이머 등의 결과, 드라이버·가위·통조림 따개, 호환 장착 위치, 운동명, 호박 조각 작업명은 보존했다. 최종 문자열 일치 51개/44문형은 이런 대상·결과·역할 및 부분 문자열 일치이며 일괄 삭제하지 않았다.
- 동일 공통 경로로 생성 JSON을 재생산했다. FullType 문장 override, 생성 JSON 수동 패치, 새 validator/authority/전체 Run A/B는 없다.
- 각 locale/surface present1981, absent124 유지.
- 가위 moving_furniture의 실제 가구 매핑 근거는 미확인 상태다. 기존 문장을 확정 수락하지 않으며 이번 자기 이름 교정에서 기능/가구명을 추가하지 않았다.
- 차량42 구체 목적, 기존 unresolved/보류 및 exact ID L4 공급 공백 유지.
- EN 독립 품질 수락과 실제 PZ 관찰은 수행하지 않았다. 기존 후보/검사 기록 보존. 외부 설치, commit/push 없음.

Descriptions SHA256: `3d25f5f28d98fa48d2676bb91ccf96c055c3a6d0959804b095b0a90ffdf77b94`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.Socks_Long**

Before KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 긴 양말을 시트 로프 제작 재료나 연료, 불쏘시개로도 쓸 수 있다.

After KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After EN compact: It can be worn or ripped to obtain cloth scraps, used intact to make sheet rope, or used as fuel and tinder.

**Base.Tshirt_DefaultTEXTURE_TINT**

Before KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 티셔츠를 시트 로프 제작 재료나 연료, 불쏘시개로도 쓸 수 있다.

After KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After EN compact: It can be worn or ripped to obtain cloth scraps, used intact to make sheet rope, or used as fuel and tinder.

**Base.Sheet**

Before KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻거나, 찢기 전 천을 시트 로프 재료로 쓸 수 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be used as material for crafting. It can be ripped for cloth scraps or used intact to make sheet rope. It can be installed as a curtain on an eligible window or door without one. It can be used as fuel or tinder.

**Radio.RadioRed**

Before KO compact: 프리미엄 테크 라디오는 전원이 공급되면 기록 매체를 재생하거나 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After KO compact: 분해하지 않고 전원이 공급되면 기록 매체를 재생하거나 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After EN compact: While intact and powered, it can be used for playing recorded media and listening to radio broadcasts. Depending on the content, it can affect stats, XP or recipe knowledge. It can be dismantled with a screwdriver to recover electronic parts.

**Base.BeerEmpty**

Before KO compact: 깨뜨려 깨진 병을 얻을 수 있다. 맥주 병 (비어있음)은 물을 담아 보관하거나 운반할 수 있다. 맥주 병 (비어있음)은 화염병 제작에 재료로 사용할 수 있다.

After KO compact: 깨뜨려 깨진 병을 얻을 수 있다. 깨지 않은 상태로 물을 담아 보관하거나 운반할 수 있다. 깨지 않은 상태로 화염병 제작에 재료로 사용할 수 있다.

After EN compact: It can be broken to obtain Smashed Bottle. While unbroken, it can hold water for storage or carrying. While unbroken, it can be used as a material for making Molotov Cocktail.

**Base.SpearBreadKnife**

Before KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창의 부착물을 회수할 수 있다. 창 (빵칼)은 무기로 쓸 수 있다.

After KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창의 부착물을 회수할 수 있다. 부착물을 분리하지 않고 무기로 쓸 수 있다.

After EN compact: With its attachment still fitted, it can be used for spear fishing at water without bait. Its spear attachment can be recovered. With its attachment still fitted, it can be used as a weapon.

**Base.CannedMilk**

Before KO compact: 통조림 따개로 개봉해 연유를 마실 수 있다. 꺼낸 연유를 요리 재료로도 쓸 수 있다.

After KO compact: 통조림 따개로 개봉해 연유를 마실 수 있다. 꺼낸 연유를 요리 재료로도 쓸 수 있다.

After EN compact: It can be opened with a Can Opener to drink the Evaporated Milk. The extracted Evaporated Milk can also be used as a cooking ingredient.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-eek7qzgg/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 전체 자기 이름 반복 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 138.96s (0:02:18)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/self-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-5debqnfk/p/Iris.zip`
- SHA256: `3a9a31a04d59217e0e16d7d46e93c130bc77f5fb7db75136b55a9c96272db2e5`
- product: `l3p-f3aa38ae0288fa1cacfc0173cb3bd3ac01d8193ef8e08572059ae07944519d23`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-eek7qzgg 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 독립 활용 문형의 불필요 상태절 제거

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

직전 3d25f5f2 결과 대비 변경 문면 72개 고유 segment 그룹을 모두 읽었다. Socks_Long/BeerEmpty/SpearBreadKnife/Radio.RadioRed의 KO/EN compact/expanded 전체 문면과 독립 활용 배치를 대조했다.

실제 문면 변경: **221아이템 / 884좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 최신 사용자 지시: 용도끼리는 독립적으로 서술한다. 앞 설명과 이어질 것을 가정해 찢지 않고/깨지 않고 같은 상태절을 넣지 않는다. 이 지시는 앞선 자기 이름 교정 기록의 상태절 유지 설명을 대체한다. 이전 기록/후보 자체는 보존한다.
- self-name 후처리의 분해하지 않고/깨지 않은 상태로/부착물을 분리하지 않고 및 EN While intact/unbroken/attachment still fitted 접두어를 제거했다. 라디오 전원 등 실제 조건은 유지한다.
- 의류와 Sheet의 찢지 않고/used intact도 제거했다. 천 회수와 시트 로프 제작은 각각 현재 아이템의 독립 활용이다. KO/EN compact/expanded에 같은 기준을 적용했다.
- 병/탄약/부착물 창/전자기기의 독립 활용 단위를 회수·변형 단위 앞에 배치한다. 각 단위의 사실·조건·후속 결과 문장은 함께 보존하고 이름이나 상태 조건을 추가하지 않는다.
- 이번 self-name 변경에서 생긴 접두어와 관계 합성만 교정했다. FullType 문장 override, 생성 JSON 수동 패치, 새 광범위 감사/validator/authority/전체 Run A/B 없음.
- 각 locale/surface present1981, absent124 유지.
- 통조림 내용물·회수 결과·도구/대상 이름과 기존 실제 조건 보존.
- 가위 실제 가구 매핑 미확인, 차량42/기존 unresolved/보류/L4공급 공백 유지.
- EN 독립 품질 수락 및 실제 게임 관찰 없음. 외부 설치/commit/push 없음.

Descriptions SHA256: `e611c74cd18ed03d2ed8469d0b3dfb9897436d1e2f1209131bbd16fd0024eaff`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.Socks_Long**

Before KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After EN compact: It can be worn or ripped to obtain cloth scraps, used to make sheet rope, or used as fuel and tinder.

**Base.Tshirt_DefaultTEXTURE_TINT**

Before KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After KO compact: 착용하거나 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 연료나 불쏘시개로도 쓸 수 있다.

After EN compact: It can be worn or ripped to obtain cloth scraps, used to make sheet rope, or used as fuel and tinder.

**Base.Sheet**

Before KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 찢지 않고 시트 로프 제작에 쓸 수도 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be used as material for crafting. It can be ripped for cloth scraps or used to make sheet rope. It can be installed as a curtain on an eligible window or door without one. It can be used as fuel or tinder.

**Radio.RadioRed**

Before KO compact: 분해하지 않고 전원이 공급되면 기록 매체를 재생하거나 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After KO compact: 전원이 공급되면 기록 매체를 재생하거나 라디오 방송을 청취할 수 있다. 내용에 따라 능력치, 경험치, 제작법 학습 효과를 얻을 수 있다. 드라이버로 분해해 전자 부품을 회수하는 데 쓸 수 있다.

After EN compact: With power, it can be used for playing recorded media and listening to radio broadcasts. Depending on the content, it can affect stats, XP or recipe knowledge. It can be dismantled with a screwdriver to recover electronic parts.

**Base.BeerEmpty**

Before KO compact: 깨뜨려 깨진 병을 얻을 수 있다. 깨지 않은 상태로 물을 담아 보관하거나 운반할 수 있다. 깨지 않은 상태로 화염병 제작에 재료로 사용할 수 있다.

After KO compact: 물을 담아 보관하거나 운반할 수 있다. 화염병 제작에 재료로 사용할 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.

After EN compact: It can hold water for storage or carrying. It can be used as a material for making Molotov Cocktail. It can be broken to obtain Smashed Bottle.

**Base.SpearBreadKnife**

Before KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창의 부착물을 회수할 수 있다. 부착물을 분리하지 않고 무기로 쓸 수 있다.

After KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 무기로 쓸 수 있다. 창의 부착물을 회수할 수 있다.

After EN compact: It can be used for spear fishing at water without bait. It can be used as a weapon. Its spear attachment can be recovered.

**Base.CannedMilk**

Before KO compact: 통조림 따개로 개봉해 연유를 마실 수 있다. 꺼낸 연유를 요리 재료로도 쓸 수 있다.

After KO compact: 통조림 따개로 개봉해 연유를 마실 수 있다. 꺼낸 연유를 요리 재료로도 쓸 수 있다.

After EN compact: It can be opened with a Can Opener to drink the Evaporated Milk. The extracted Evaporated Milk can also be used as a cooking ingredient.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-5debqnfk/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 독립 활용 상태절 제거 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 132.15s (0:02:12)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/prefix-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-ms8p4gav/p/Iris.zip`
- SHA256: `63c125cc59db971f31928ce3f04ff3a4972378225978d9465b0430d713590e56`
- product: `l3p-c22fc3c5694e25ee5091ebd8243873f33294f9af352494163ace07204d16f8b8`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-5debqnfk 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 발견사항 16개 공통 경로 교정 및 근거 보류

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

전체 2,105개 입력을 위16개 발견사항의 공통 activity/function/role 경로에 대조했다. 각 범위와 변경/유지 항목을 기존 검수 자료에 기록하고, 실제 원문 및 조건·결과를 읽어 처리 여부를 판단했다. 변경 문면뿐 아니라 유지된 조리 재료·도구 부착물·독서/기술서·물 용기·금속 재료·착용 형태도 대조했다. 같은 기술서의 기술명·배율 등 반복 변수는 공통 문형으로 검토했다. 문면 읽기와 생성/자동 검사 성공은 전체 아이템의 모든 규칙 품질 수락을 뜻하지 않는다.

실제 문면 변경: **215아이템 / 811좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 1. 교정 — 낚싯대4의 compact 후속 변형 결과를 제거하고 파손·미끼 손실을 expanded와 일치시켰다. 줄 끊김 조건 유지.
- 2. 교정/해당 없음 — 조리 하위 활동29의 입력 역할을 대조했다. BakingTray/MuffinTray는 반죽을 담아 요리를 만드는 용도, Yeast는 반죽 제작 재료로 설명한다. 나머지는 이미 요리 재료/음식 준비로 묶이거나 독립 포장·미끼 활용이어서 불완전 문장이 없다.
- 3. 교정 — 관련24개 중 창 자체와 부착물, 장치 개조 대상과 부착 부품, 소모 재료, 도구를 구별했다. Add 계열 채택 recipe의 두 번째 입력이 작동 부품임을 사용했다. 기존 attachment 역할7개 등은 현재 문형을 유지하며 재료로 바꾸지 않았다.
- 4. 공개 경계 교정/장식 근거 보류 — Pumpkin의 pumpkin_carving material은 단순 원물 가공으로 내부화했다. 먹기·조리·미끼는 유지. 칼의 실제 조각 도구 활용6개는 보존했다. HalloweenPumpkin이라는 결과 이름으로 장식 기능을 발명하지 않았다.
- 5. 교정 — 소화28개를 바닥이나 몸에 붙은 불을 끌 수 있다로 표현했다. EN은 ground or characters를 유지하여 플레이어만으로 좁히지 않았다.
- 6. 교정 — 분무액 준비4개 중 물을 담는 분무기는 혼합 용기, 우유류·담배는 투입 재료로 구별했다. scripts/farming.txt의 두 제조법 입력·결과와 기존 store_water/소비 기능을 대조했다.
- 7. 교정 — 열쇠7개의 잠금/시동/최초 문 열기 경보 제한을 플레이어 동사로 표현했다. 처음 열기와 이미 울리는 경보를 끄지 못함, 맞는 열쇠 제한은 유지했다. 정비 열쇠 요구는 계속 내부다.
- 8. 교정 — 관련16개 모두 현재 원문을 대조했다. 자물쇠 설치 가능 대상/문 제외, 커튼 없는 창문·문, 매체 재생, 헤드폰 연결과 TV 제외, 원격 장치 연결 관계로 설명했다. 실제 가구명/기기명을 새로 지정하지 않았다.
- 9. 교정 — 벨트/홀스터3개를 물품을 걸거나 넣어 휴대하는 목적으로 표현했다. ISHotbarAttachDefinition.lua의 도구·무전기/홀스터 연결과 items_weapons.txt의 AttachmentType=Holster를 확인했다. 모든 물품 부착을 주장하지 않는다.
- 10. 문면 교정/학습 기능 근거 보류 — 독서102개를 분류했다. mood cap의 악화 방지 문형을 교정했으며 감소·치료로 바꾸지 않았다. 기술서의 조건·배율은 유지한다. CookingMag 등의 현재 L3 입력에는 제작법 학습 사실이 없어 읽을 수 있다를 남겼다. 소스의 recipe 학습/L4 공급과 L3 채택 공백은 기능이 없다는 판정도, 교정 완료 판정도 아니다.
- 11. 교정 — Battery1의 중복 대상은 호환 조명·휴대/건전지 기기로 묶고 남은 충전량으로 작동시키는 용도로 표현했다. 신규 기기 종류나 충전량 보장은 추가하지 않았다.
- 12. 교정/기존 보류 유지 — 현재 장착·탱크·문·좌석·타이어 경로42개를 대조했다. 좌석·탱크·문의 장착과 실제 사용을 묶고 타이어 손실 중복을 제거했다. 탱크 상태70·엔진 정지·타이어 손실 조건은 보존했다. 이 범위42는 과거 미확정 차량42를 해소했다는 뜻이 아니며 새로운 구체 기능/매핑을 추가하지 않았다.
- 13. 공통 묶음 교정/독립 목적 유지 — 목공·건축·용접, 음식 손질 도구, 재료 제작 목적, 의류 패치, 물 보관·운반·이동, 연료 이동, 밭/무덤 작업을 동일 역할/활용별로 묶었다. 명시된 긴 사례 모두 양표면을 대조했다. Log의 묶음·숯·수박 도구·연료, TreeBranch/WoodenStick의 골절·제작·점화·연료 등 독립 활용은 길이만을 이유로 삭제하지 않았다. primary_use/글자수 정책/expanded에만 이전 없음.
- 14. 교정/해당 없음 — BlowTorch/WeldingMask는 용접에 쓰는 역할로, BrokenFishingNet는 철사 회수로 표현했다. GardenFork 등의 동사와 수확 제외, 화장/제거, 수면 보조약 문형을 교정했다. SharpedStone의 실제 소모 가능성은 창 제작과 함께 유지했다. 금속판의 크기 전환 손실·기존 마모 보류 및 이미 간결한 진통/공포 약품 문형은 보존했다.
- 15. 교정/해당 없음 — 착용 형태·텐트 관련80개를 대조했다. 형태 변경은 착용과 함께 연료 앞에 배치했고 텐트 설치와 휴식/수면은 같은 활용으로 묶었다. 이미 올바른 순서인 장신구·모자 등의61개는 그대로다.
- 16. 공개 확정 보류 — moving_furniture20개 모두 내부에 근거를 보존하고 공개 확정을 제거했다. 등록표는 도구 종류만 제공하고 ISMoveableSpriteProps.lua는 실제 PickUpTool/PlaceTool 값을 읽는다. 현재 허용 저장소에서 구체 sprite 매핑을 찾지 못했다. 20개 모두 실제 불가능하다는 뜻이 아니며 가위만의 오류나 두 동작 모두의 존재를 추정하지 않는다. News_EN의 Shovel 언급은 채택된 구체 매핑을 대신하지 않는다.
- 상태 implemented_only. 각 locale/surface present1981, absent124 유지.
- 가구20 실제 매핑, L3 잡지 학습 사실 공백, 기존 차량 구체 목적/미해결 관계/L4 exact-ID 공급 공백은 보류다.
- 실제 게임 관찰과 EN 독립 품질 수락 없음. 사용자에게 문장 검수 의무를 넘기지 않는다.
- 기존 dirty/후보/기록 보존. FullType 완성 문장 override, 생성 JSON 수동 수정, 새 검증 authority/ledger/전체 Run A/B, 외부 접근/설치/commit/push 없음.

범위별 해당/변경/유지(항목 간 중복 포함):

- 1 scope 4 changed 4 unchanged 0
- 2 scope 29 changed 5 unchanged 24
- 3 scope 24 changed 17 unchanged 7
- 4 scope 7 changed 5 unchanged 2
- 5 scope 28 changed 28 unchanged 0
- 6 scope 4 changed 4 unchanged 0
- 7 scope 7 changed 7 unchanged 0
- 8 scope 16 changed 16 unchanged 0
- 9 scope 3 changed 3 unchanged 0
- 10 scope 102 changed 12 unchanged 90
- 11 scope 1 changed 1 unchanged 0
- 12 scope 42 changed 42 unchanged 0
- 13 scope 96 changed 66 unchanged 30
- 14 scope 30 changed 26 unchanged 4
- 15 scope 80 changed 19 unchanged 61
- 16 scope 20 changed 20 unchanged 0

Descriptions SHA256: `524f74b79d6d5d2b258b7f29435e34e16d901456bac98f2661a92f98819a172f`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.CraftedFishingRod**

Before KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 부러지거나 막대로 바뀌며 미끼를 잃는다. 무기로 쓸 수 있다.

After KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 파손되고 미끼를 잃는다. 무기로 쓸 수 있다.

After EN compact: It can be used for rod fishing at water with matching bait. If the line breaks, it breaks and the bait is lost. It can be used as a weapon.

**Base.BakingTray**

Before KO compact: 반죽을 담아 만들 수 있다.

After KO compact: 반죽을 담아 요리를 만드는 데 쓸 수 있다.

After EN compact: It can hold dough for preparing food.

**Base.MuffinTray**

Before KO compact: 반죽을 담아 만들 수 있다.

After KO compact: 반죽을 담아 요리를 만드는 데 쓸 수 있다.

After EN compact: It can hold dough or batter for preparing food.

**Base.Yeast**

Before KO compact: 반죽에 넣을 수 있다.

After KO compact: 반죽을 만드는 재료로 쓸 수 있다.

After EN compact: It can be used as an ingredient for preparing dough and batter.

**Base.SpearCrafted**

Before KO compact: 물가에서 미끼 없이 창낚시에 쓸 수 있다. 창 부착물 장착에 재료로 사용할 수 있다. 무기로 쓸 수 있다.

After KO compact: 부착물을 달아 쓸 수 있다. 무기로 쓸 수 있다. 물가에서 미끼 없이 창낚시에 쓸 수 있다.

After EN compact: It can be fitted with an attachment. It can be used as a weapon. It can be used for spear fishing at water without bait.

**Base.Aerosolbomb**

Before KO compact: 장치 작동 부품 장착에 재료로 사용할 수 있다. 투척 공격에 쓸 수 있다.

After KO compact: 작동 부품을 달아 개조할 수 있다. 투척 공격에 쓸 수 있다.

After EN compact: It can be modified by fitting triggering components. It can be used for throwing attacks.

**Base.Pumpkin**

Before KO compact: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다. 호박 조각에 재료로 사용할 수 있다.

After KO compact: 먹거나 요리 재료로 쓸 수 있다. 덫의 미끼로도 쓸 수 있다.

After EN compact: It can be eaten or used as a cooking ingredient. It can also be used as trap bait.

**Base.WaterPot**

Before KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 담아 보관하거나 운반할 수 있다. 다른 용기나 저장 시설로 물을 옮길 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 보관, 운반하거나 다른 용기나 물 저장 시설로 옮길 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After EN compact: It can be used to disinfect bandaging. It can hold ingredients for cooking. It can store and carry water or transfer it to other containers or water storage fixtures. Its water can be used for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

**farming.GardeningSprayEmpty**

Before KO compact: 물을 담아 보관하거나 운반할 수 있다. 작물 치료제 준비에 재료로 사용할 수 있다.

After KO compact: 작물 치료용 분무액을 만드는 용기로 쓸 수 있다. 물을 담아 보관하거나 운반할 수 있다.

After EN compact: It can hold the mixture when making crop-treatment spray. It can hold water for storage or carrying.

**Base.CarKey**

Before KO compact: 맞는 차량의 첫 문 개방 경보를 피하지만 이미 울리는 경보는 끄지 않는다. 맞는 문의 잠금을 조작할 수 있다. 맞는 구조물 자물쇠를 제거할 수 있으며 이때 소모된다. 맞는 차량의 시동이나 점화장치를 조작할 수 있다.

After KO compact: 열쇠가 맞는 차량의 문을 처음 열 때 경보가 울리지 않게 한다. 이미 울리는 경보는 끄지 못한다. 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있으며 이때 소모된다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다.

After EN compact: It prevents the alarm from being triggered when first opening the matching vehicle. It cannot silence an alarm already ringing. It can lock or unlock a door with a matching lock. It can remove a matching structure padlock and is consumed in the process. It can be used to start the matching vehicle.

**Base.Sheet**

Before KO compact: 물품 제작의 재료로 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 커튼이 없는 대응 창문이나 문에 커튼으로 설치할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 물품 제작에 재료로 쓸 수 있다. 찢어서 천 조각을 얻을 수 있다. 시트 로프 제작에 쓸 수도 있다. 커튼이 없는 창문이나 문에 커튼으로 달아 쓸 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be used as material for crafting. It can be ripped for cloth scraps or used to make sheet rope. It can be used as a curtain on an eligible window or door without one. It can be used as fuel or tinder.

**Base.Belt2**

Before KO compact: 허리에 착용할 수 있다. 착용하면 맞는 유형의 물품을 부착하는 좌우 벨트 슬롯을 제공한다. 불쏘시개로 소모할 수 있다.

After KO compact: 허리에 착용할 수 있다. 착용하면 허리 양쪽에 도구나 무전기를 걸어 휴대할 수 있다. 불쏘시개로 소모할 수 있다.

After EN compact: It can be worn at the waist. When worn, it can carry compatible tools or walkie-talkies on either side of the waist. It can be consumed as tinder.

**Base.Book**

Before KO compact: 독서할 수 있으며, 읽는 동안 지루함, 스트레스, 불행이 독서 시작 때보다 더 심해지지 않게 한다. 모닥불 키트 제작에 재료로 사용할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 독서 중 지루함, 스트레스, 불행이 더 심해지는 것을 막을 수 있다. 모닥불 키트 제작에 재료로 사용할 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: Reading can keep boredom, stress, and unhappiness from worsening beyond their starting levels. It can be used as a material for campfire-kit crafting. It can be used as fuel or tinder.

**Base.CookingMag1**

Before KO compact: 읽을 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 읽을 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be read. It can be used as fuel or tinder.

**Base.Battery**

Before KO compact: 남은 충전량을 호환되는 건전지형 조명, 기둥 조명, 휴대 기기, 배터리형 기기의 전원으로 공급할 수 있다.

After KO compact: 남은 충전량으로 호환되는 조명과 휴대 기기 등을 작동시킬 수 있다.

After EN compact: Its remaining charge can power compatible lights and portable or other battery-powered devices.

**Base.SmallGasTank1**

Before KO compact: 호환 차량에 장착할 수 있다. 차량에 장착해 연료를 보관한다. 엔진을 멈추면 맞는 용기로 연료를 넣거나 뺄 수 있고 작동 중에는 엔진에 공급한다. 탱크 상태가 70 미만이면 추가로 연료를 잃을 수 있다.

After KO compact: 호환 차량에 장착해 연료를 보관하고 엔진에 공급할 수 있다. 엔진을 끄면 맞는 용기로 연료를 넣거나 뺄 수 있다. 탱크 상태가 70 미만이면 연료가 추가로 줄 수 있다.

After EN compact: It can be installed in a compatible vehicle to store fuel and supply the engine. With the engine stopped, fuel can be added or siphoned with a compatible container. Tank condition below 70 can cause additional fuel loss.

**Base.Screwdriver**

Before KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 일부 가구 집기와 설치, 차량과 무기의 부품 장착과 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 차량과 무기의 부품 장착과 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can be used for making and dismantling electronic devices, plus lamp conversion to battery power; woodworking, plus structure disassembly; fitting and removing parts on vehicles and weapons. It can also be attached to a crafted spear or be used as a weapon.

**Base.BlowTorch**

Before KO compact: 금속 용접, 건축, 금속 바리케이드 설치와 철거, 불타거나 파손된 차량 분해에 사용할 수 있다.

After KO compact: 금속 용접, 건축, 금속 바리케이드 설치와 철거, 불타거나 파손된 차량 분해에 사용할 수 있다.

After EN compact: It can be used for metal welding and construction, installing or removing metal barricades, and dismantling burnt or smashed vehicles.

**camping.CampingTentKit**

Before KO compact: 설치한 텐트에서 쉬거나 잘 수 있다. 텐트를 설치할 수 있다.

After KO compact: 텐트를 설치해 쉬거나 잘 수 있다.

After EN compact: It can be pitched as a tent for resting or sleeping.

**Base.Scissors**

Before KO compact: 데님이나 가죽 의류의 조각 회수, 일부 가구 집기와 설치, 머리와 수염 손질에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 데님이나 가죽 의류의 조각 회수, 머리와 수염 손질에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can be used for recovering strips from denim or leather clothing; hair and beard grooming. It can also be attached to a crafted spear or be used as a weapon.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-ms8p4gav/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 발견사항 16개 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 130.95s (0:02:10)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/findings-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-wi1iy1oy/p/Iris.zip`
- SHA256: `aae12ee19a9bcd1c0561affdbb1aa4d5e170a779fbe7efd57287aa1ff4eba513`
- product: `l3p-fc115dbf6ef0bc0dd8ad409ca944c0cc5fed222dac957f823ac750b4e075f7eb`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-ms8p4gav 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 발견사항 잔여 교정과 부분해결 판정

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

이번 잔여 공통 경로의 실제 전후 문면을 대조했다. 낚싯대4, 창 도구6의 조건 결속과 원문/제품 use unit 투영, 조종기3, 열쇠7, 이중 홀스터1, 물 용기24의 영향을 확인했다. KO/EN 양표면 45아이템/112좌표 변경은 변경 범위이며 전체 품질 수락이 아니다.

실제 문면 변경: **45아이템 / 112좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- a / 지적9 해결 — 이중 홀스터의 양쪽에 홀스터에 중복을 허리 양쪽 홀스터에 맞는 총기를 넣어 휴대로 교정했다.
- b / 지적8 해결 — link_remote_device와 send_remote_trigger를 가진 조종기3개에서 함께 소지한 호환 장치 연결과 범위 내 원격 작동을 한 활용으로 합성했다. 연결만 가능한 장치는 이 경로로 합치지 않았다.
- c / 지적1·14·15 해결 — 낚싯대4의 낚시/줄 파손·미끼 손실, SharpedStone의 창 제작/소모, 칼5개의 창 제작/내구도 감소를 같은 활용 본문에 묶었다. 기존 continues_use가 원문·제품 투영에서는 줄바꿈으로 남던 차이를 바로잡았다. 독립 활용에는 줄바꿈을 유지하며 근거 없는 낚시 마모 연결은 추가하지 않았다.
- d / 지적7 해결 — 열쇠7개의 compact에서 문 잠금과 해제/구조물 자물쇠 제거/차량 시동을 나열하고 대상 일치를 한 번 명시한다. 경보 절차를 선두에서 빼고 첫 개방/이미 울리는 경보 제한을 요약했다. expanded는 차량 활용과 첫 개방 경보 제한을 같은 단위로, 문 잠금과 구조물 자물쇠 제거는 독립 단위로 유지한다. 자물쇠 제거 시 소모도 유지한다.
- d / 지적13 부분해결 — 물 용기24개의 compact 보관·운반·이동 문형을 줄였다. WaterPot에는 붕대 소독, 요리, 물 보관·운반·이동, 작물 급수·차량 혈흔 세척·소화·음용과 오염수 위험이 여전히 남는다. 이는 독립 활용과 의미를 바꾸는 제한이라 삭제하지 않았다. 기존 Screwdriver/Hammer/Shovel/Needle/WhiskeyEmpty/RippedSheetsDirty/Log/TreeBranch/WoodenStick의 앞선 공통 묶음 개선은 유지하지만 긴 목록 문제 전체가 해결됐다고 하지 않는다. WaterPot의 실제 남은 원문을 아래에 기록한다.
- 기존16개 판정 정정 — 1/2/3/5/6/7/8/9/11/14/15는 지적한 문면·구조 교정 범위에서 해결. 4는 원물 가공 경계 해결/장식 기능 근거 보류. 10은 감정 상한 문면 해결/잡지 학습 기능 근거 보류. 12는 근거 있는 부품 설명 개선/기존 미확정 차량 관계 보류. 13은 부분해결. 16은 구체 PickUpTool/PlaceTool 매핑 근거 보류. 모든16개 완료라는 앞선 총괄 표현을 대체한다.
- implemented_only. 실제 게임 미관찰, EN 독립 품질 승인 없음.
- 가구 매핑/잡지 학습/기존 차량·L4 공급 근거 공백 보류 유지.
- 독립 활용 삭제, FullType 완성 문장 override, 생성 JSON 수동 수정, 새 검증 체계나 전체 confidence 검사 없음. 기존 산출물 일치 검사는 같은 활용의 문장 결속을 반영하도록 갱신했다.

Descriptions SHA256: `6aa09cf681b5616da9812b3b6bdf457b7695b758ada771571c74b4bfa2801c70`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.HolsterDouble**

Before KO compact: 허리에 착용할 수 있다. 착용하면 양쪽에 홀스터에 맞는 총기를 넣어 휴대할 수 있다. 불쏘시개로 소모할 수 있다.

After KO compact: 허리에 착용할 수 있다. 허리 양쪽 홀스터에 맞는 총기를 넣어 휴대할 수 있다. 불쏘시개로 소모할 수 있다.

After EN compact: It can be worn at the waist. It can carry compatible firearms in holsters on both sides of the waist. It can be consumed as tinder.

**Base.RemoteCraftedV1**

Before KO compact: 조종 범위 안의 연결된 장치를 원격으로 작동시킬 수 있다. 함께 가지고 있는 호환 장치를 연결해 원격으로 작동시키도록 설정할 수 있다.

After KO compact: 함께 소지한 호환 장치를 연결해 조종 범위 안에서 원격으로 작동시킬 수 있다.

After EN compact: It can be linked to a compatible device carried together and remotely activate that device within range.

**Base.SharpedStone**

Before KO compact: 창 제작에 사용할 수 있다. 창을 만들 때 소모될 수 있다. 석제 도구 제작에 재료로 사용할 수 있다. 목공에 사용할 수 있다.

After KO compact: 창 제작에 사용할 수 있다. 창을 만들 때 소모될 수 있다. 석제 도구 제작에 재료로 사용할 수 있다. 목공에 사용할 수 있다.

After EN compact: It can be used for spear crafting. It may be consumed when used to craft a spear. It can be used as a material for stone-tool crafting. It can be used for woodworking.

**Base.FishingRod**

Before KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 파손되고 미끼를 잃는다. 무기로 쓸 수 있다.

After KO compact: 물가에서 맞는 미끼와 함께 낚시할 수 있다. 낚싯줄이 끊어지면 파손되고 미끼를 잃는다. 무기로 쓸 수 있다.

After EN compact: It can be used for rod fishing at water with matching bait. If the line breaks, it breaks and the bait is lost. It can be used as a weapon.

**Base.HuntingKnife**

Before KO compact: 음식 손질, 목공, 낚시 장비, 창 제작, 호박 조각, 덤불, 덩굴 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 음식 손질, 목공, 낚시 장비, 창 제작, 호박 조각, 덤불, 덩굴 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can be used for food preparation; woodworking; fishing-gear and spear crafting; pumpkin carving; removing bushes and vines. It can also be attached to a crafted spear or be used as a weapon.

**Base.CarKey**

Before KO compact: 열쇠가 맞는 차량의 문을 처음 열 때 경보가 울리지 않게 한다. 이미 울리는 경보는 끄지 못한다. 열쇠가 맞는 문을 잠그거나 열 수 있다. 맞는 구조물 자물쇠를 제거할 수 있으며 이때 소모된다. 열쇠가 맞는 차량의 시동을 거는 데 쓸 수 있다.

After KO compact: 문 잠금과 해제, 구조물 자물쇠 제거, 차량 시동에 쓸 수 있으며 대상과 열쇠가 맞아야 한다. 자물쇠 제거 시 소모된다. 차량 첫 개방 경보를 막지만 이미 울리는 경보는 끄지 못한다.

After EN compact: It can be used for locking and unlocking doors, removing structure padlocks, and starting vehicles, with a matching key required for each target. Removing a padlock consumes the key. It prevents the first-entry vehicle alarm but cannot silence an active alarm.

**Base.WaterPot**

Before KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 보관, 운반하거나 다른 용기나 물 저장 시설로 옮길 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 보관, 운반하고 용기나 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After EN compact: It can be used to disinfect bandaging. It can hold ingredients for cooking. It can store, carry and pour water into containers or storage fixtures. Its water can be used for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-wi1iy1oy/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 발견사항 잔여 교정 최종 검사와 새 후보

실패한 제품 검사와 필수 S2 의존 검사 재실행: **2 passed in 122.38s (0:02:02)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

최초 최소3노드 실행은 1 failed, 2 passed in 80.32s / exit 1이었다. 제품 검사 기대값이 같은 활용의 문장을 줄바꿈으로 연결하도록 남아 있어 실패했고 공백 연결로 수정했다. 단독 제품 재실행은 S2 공유 입력이 없어 B corpus/owner mismatch로 exit 1, 1 failed in 2.80s였다. 이어 필수 S2와 제품2노드를 함께 실행했지만 Lua 로더의 기존 줄바꿈 결속 검사에서 1 failed, 1 passed in 91.00s / exit 1이었다. 로그는 `.tmp/prose/residual-dependent-tests.log`에 보존했다. IrisLayer3DataLookup.lua의 기존 일치 검사도 같은 활용 내부는 공백, 활용 사이는 줄바꿈으로 대조하도록 맞췄다. 문장 재작성이나 새 검증 체계를 런타임에 추가한 것이 아니다. 아래는 해당 수정 후 필수2노드 최종 재실행 결과다. 최초 설명 조합 노드는 성공했지만 최초 묶음 전체를 PASS로 표시하지 않는다. 로그: `.tmp/prose/residual-tests.log`, `.tmp/prose/residual-product-tests.log`.

로그: `.tmp/prose/residual-dependent-final-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-fbgcwee9/p/Iris.zip`
- SHA256: `03aa80beabb1591c6f9dfe2aa60dc73796b7513eb738ef6a88afa6062c119f1f`
- product: `l3p-97a61bb9b62fcf86dfbb010a4c21884777b1acc55d7ea6059a4be2cf4985946e`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-wi1iy1oy 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 긴 목록·중복 서술 교정 완료

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

앞서 부분해결로 남긴 지적13의 명시 사례와 공통 생산 경로를 교정하고 실제 KO/EN compact/expanded 전후 문면을 대조했다. 같은 대상·역할의 반복은 합성하고 서로 다른 활용은 독립 문장으로 유지했다. 변경 수는 적용 범위이며 전체 게임 기능의 품질 수락 수가 아니다.

실제 문면 변경: **420아이템 / 837좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 지적13 긴 목록·중복 문장 교정 완료 — 전회 부분해결로 남긴 실제 문면을 공통 activity/function/role 경로에서 마무리했다. 아이템 용도 수 자체를 줄이는 목표로 바꾸지 않았으며 독립 활용을 삭제하지 않았다.
- WaterPot/물 용기 — compact는 조리·붕대 소독의 동일 용기 역할, 물 보관·운반·옮겨 붓기, 담긴 물의 급수·세척·소화·음용으로 구분한다. expanded에서는 각각의 독립 활용과 실제 조건을 유지한다. WaterMug 계열의 오염수 위험을 조리 뒤에서 음용 바로 뒤로 옮겨 잘못된 조건 연결도 제거했다.
- Screwdriver — 전자 부품·무전기 제작과 전자기기 분해·회수 및 조명 건전지 개조를 전자 작업 문장으로 묶었다. 목공·건축물 분해와 부품 탈부착, 창 부착·무기는 별도 문장으로 구분했다. 호환 무기 부착물과 차량 부품을 구별한다.
- Hammer/Shovel — Hammer의 건축·바리케이드 작업에 수박 손질을 끼워 넣던 목록을 분리했다. Shovel은 무덤·밭 조성과 재 청소·토사 담기 작업을 별도 문장으로 나눴다. 수확 제외, 무기 활용 등 실제 용도와 제한을 유지한다.
- Needle — 의류 덧대기·패딩·패치 제거 및 재료 회수 가능성을 같은 활용으로 묶었다. 깊은 상처 봉합의 붕대·유리 제한과 매트리스 제작은 각각 독립적으로 유지하며 문형을 간결하게 했다.
- WhiskeyEmpty/연료 용기 — 주유기 전력과 차량 엔진 정지 조건을 보존하며 급유·연료 이동의 반복 표현을 줄였다. 물 보관·운반, 화염병 재료, 깨진 병 회수는 각각 별도 활용이다.
- RippedSheetsDirty/재료 공통 경로 — 제작 결과마다 반복하던 제작 서술을 하나로 묶고 결과 이름을 보존했다. compact의 장치 제작/기타 제작도 하나의 제작 목적 안에서 설명한다. 상처 감염 위험과 천 세척은 유지한다.
- 연료·불쏘시개 — expanded에서 같은 시설을 두 번 열거하던 문장을 공유 대상과 한쪽 용도에만 해당하는 대상으로 합성했다. 통나무가 든 드럼에는 불쏘시개 용도만 적용해 연료 기능으로 넓히지 않는다.
- Log/TreeBranch/WoodenStick — Log의 목공·건축 및 숯 제작 재료 문형을 정리했다. 마찰 점화의 시설 목록은 compact에서 점화 목적과 방법으로 요약하고 expanded에서 시설별 대상 및 지구력·파손 조건을 보존한다. 골절 고정, 제작 재료, 연료, 묶기와 수박 손질 같은 독립 활용은 유지한다.
- 문면 교정은 완료했다. 이전 사실 근거 보류(가구의 구체 매핑, 잡지 학습 사실 채택, 기존 차량/L4 공급 공백)를 설명이 길다는 이유의 미완료와 섞지 않는다. 이를 새 기능이 확인되었다는 뜻으로 변경하지 않는다.
- 현재 문장 교정 범위 완료. 제품 상태 implemented_only, 실제 게임 미관찰.
- FullType 완성 문장 override, 생성 JSON 수동 수정, 글자 수 강제 절단, 독립 활용 삭제 없음.
- 기존 근거 보류는 별개 사실 공백으로 유지. 이전 기록과 후보 보존. 새 검증 체계/외부 접근/설치/commit/push 없음.

Descriptions SHA256: `f84b25cfc3dbfc947a3cd03e0ad5c66526328f97a5a345717d805ee75683eb78`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.WaterPot**

Before KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 보관, 운반하고 용기나 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After KO compact: 조리와 붕대 소독에 쓸 수 있다. 물을 보관, 운반하거나 용기, 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After EN compact: It can be used for cooking and disinfecting bandaging. It can store, carry and pour water into containers or storage fixtures; its water serves for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

**Base.WaterMug**

Before KO compact: 물을 보관, 운반하고 용기나 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다. 재료를 더해 요리를 만들 수도 있다 (오염수 음용은 중독 위험).

After KO compact: 물을 보관, 운반하거나 용기, 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험). 재료를 더해 요리를 만들 수도 있다.

After EN compact: It can store, carry and pour water into containers or storage fixtures; its water serves for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning. Ingredients can also be added to prepare food.

**Base.Screwdriver**

Before KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 차량과 무기의 부품 장착과 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 전자 부품, 무전기 제작과 전자기기 분해에 쓸 수 있다. 조명을 건전지용으로 개조할 수 있다. 목공, 건축물 분해, 차량 부품과 호환 무기 부착물의 탈부착에 쓸 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can make electronic components and radios or dismantle electronic devices. It can convert lamps to battery power. It can be used for woodworking, structure disassembly; fitting and removing vehicle parts and compatible weapon attachments. It can also be attached to a crafted spear or be used as a weapon.

**Base.Hammer**

Before KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 수박 쪼개기, 문과 창문의 판자 바리케이드 설치와 철거에 사용할 수 있다. 무기로도 쓸 수 있다.

After KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 문과 창문의 판자 바리케이드 설치와 철거에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다.

After EN compact: It can be used for metal forging. It can be used for woodworking and construction; installing or removing plank barricades on doors and windows. It can be used to break a watermelon. It can also be used as a weapon.

**Base.Shovel**

Before KO compact: 무덤 파기와 메우기, 밭 만들기와 정리(수확 제외), 재 청소, 흙이나 모래, 자갈 담기 작업에 쓸 수 있다. 무기로 쓸 수 있다.

After KO compact: 무덤 파기와 메우기, 밭 만들기와 정리(수확 제외)에 쓸 수 있다. 재 청소, 흙이나 모래, 자갈 담기에 쓸 수 있다. 무기로 쓸 수 있다.

After EN compact: It can be used for digging and filling graves and preparing and clearing planting beds without harvesting. It can be used for ash cleanup and bagging dirt, sand or gravel. It can be used as a weapon.

**Base.Needle**

Before KO compact: 의류의 구멍을 덧대거나 패딩을 붙이고, 패치를 뗄 수 있다. 뗀 패치 재료를 돌려받을 수도 있다. 붕대가 감기지 않고 유리가 없는 깊은 상처를 봉합하는 데 사용할 수 있다. 매트리스 제작에 사용할 수 있다.

After KO compact: 의류의 구멍을 덧대거나 패딩을 붙이고 패치를 제거할 수 있다. 제거 시 재료가 회수될 수 있다. 붕대를 감지 않았고 유리가 없는 깊은 상처를 봉합할 수 있다. 매트리스 제작에 사용할 수 있다.

After EN compact: It can mend garment holes, add padding and remove patches, with a chance to recover the removed material. It can stitch a deep wound that is unbandaged and free of glass. It can be used for mattress crafting.

**Base.WhiskeyEmpty**

Before KO compact: 전원이 공급되는 주유기에서 연료를 받거나 엔진이 꺼진 차량과 연료를 주고받을 수 있다. 물을 담아 보관하거나 운반할 수 있다. 화염병 제작에 재료로 사용할 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.

After KO compact: 전원이 있는 주유기에서 급유받거나 시동이 꺼진 차량과 연료를 주고받을 수 있다. 물을 보관하거나 운반할 수 있다. 화염병 제작에 재료로 사용할 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.

After EN compact: It can receive fuel from a powered pump or exchange fuel with a vehicle whose engine is off. It can hold water for storage or carrying. It can be used as a material for making Molotov Cocktail. It can be broken to obtain Smashed Bottle.

**Base.RippedSheetsDirty**

Before KO compact: 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축, 장치 제작, 그 밖의 물품 제작에 재료로 쓸 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축, 장치 등 물품 제작에 재료로 쓸 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be wrapped around wounds. If infected, it can infect the wound. It can be washed with water into clean bandaging material. It can be used as material for construction and crafting devices and other items. It can be used as fuel or tinder.

**Base.Log**

Before KO compact: 목공, 건축, 물품 제작에 재료로 쓸 수 있다. 모아서 묶을 수 있다. 빈 금속 드럼에서 숯을 만드는 재료로 사용할 수 있다. 수박 쪼개기에 사용할 수 있다. 연료로 소모할 수 있다.

After KO compact: 목공과 건축, 물품 제작에 재료로 쓸 수 있다. 모아서 묶을 수 있다. 빈 금속 드럼의 숯 제작 재료로 쓸 수 있다. 수박 쪼개기에 사용할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used as material for woodworking and construction and crafting. It can be bundled with other logs. It can be made into charcoal in an empty metal drum. It can be used for breaking a watermelon. It can be consumed as fuel.

**Base.TreeBranch**

Before KO compact: 골절 고정에 쓸 수 있다. 목공, 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 모닥불, 비프로판 바비큐, 벽난로, 통나무 드럼의 점화를 시도할 수 있다. 연료로 소모할 수 있다.

After KO compact: 골절 고정에 쓸 수 있다. 목공, 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 불 피우기를 시도할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used for splinting fractures. It can be used as material for woodworking and crafting. It can be used to attempt lighting fires by wood friction. It can be consumed as fuel.

**Base.WoodenStick**

Before KO compact: 골절 고정에 쓸 수 있다. 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 모닥불, 비프로판 바비큐, 벽난로, 통나무 드럼의 점화를 시도할 수 있다. 연료로 소모할 수 있다.

After KO compact: 골절 고정에 쓸 수 있다. 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 불 피우기를 시도할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used for splinting fractures. It can be used as material for crafting. It can be used to attempt lighting fires by wood friction. It can be consumed as fuel.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-fbgcwee9/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 긴 목록·중복 서술 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 146.16s (0:02:26)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/complete-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-fffuyq8m/p/Iris.zip`
- SHA256: `01a2a68b4ca4f0bf0858321c85eeda877710dd9071a0e9f2ec7b797f60cb225d`
- product: `l3p-36d19f03c0b17a9cf8c726e23172275b9a66306b65d79c678dec65c42291dcef`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-fbgcwee9 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.


## 2026-09-13 긴 목록·중복 서술 교정 완료

상태: **implemented_only**. 최종 자동 검사는 아래에 별도 기록한다.

앞서 부분해결로 남긴 지적13의 명시 사례와 공통 생산 경로를 교정하고 실제 KO/EN compact/expanded 전후 문면을 대조했다. 같은 대상·역할의 반복은 합성하고 서로 다른 활용은 독립 문장으로 유지했다. 변경 수는 적용 범위이며 전체 게임 기능의 품질 수락 수가 아니다.

실제 문면 변경: **401아이템 / 818좌표**. 변경 분모는 2,105아이템 / 8,420좌표다.

- 지적13 긴 목록·중복 문장 교정 완료 — 전회 부분해결로 남긴 실제 문면을 공통 activity/function/role 경로에서 마무리했다. 아이템 용도 수 자체를 줄이는 목표로 바꾸지 않았으며 독립 활용을 삭제하지 않았다.
- WaterPot/물 용기 — compact는 조리·붕대 소독의 동일 용기 역할, 물 보관·운반·옮겨 붓기, 담긴 물의 급수·세척·소화·음용으로 구분한다. expanded에서는 각각의 독립 활용과 실제 조건을 유지한다. WaterMug 계열의 오염수 위험을 조리 뒤에서 음용 바로 뒤로 옮겨 잘못된 조건 연결도 제거했다.
- Screwdriver — 전자 부품·무전기 제작과 전자기기 분해·회수 및 조명 건전지 개조를 전자 작업 문장으로 묶었다. 목공·건축물 분해와 부품 탈부착, 창 부착·무기는 별도 문장으로 구분했다. 호환 무기 부착물과 차량 부품을 구별한다.
- Hammer/Shovel — Hammer의 건축·바리케이드 작업에 수박 손질을 끼워 넣던 목록을 분리했다. Shovel은 무덤·밭 조성과 재 청소·토사 담기 작업을 별도 문장으로 나눴다. 수확 제외, 무기 활용 등 실제 용도와 제한을 유지한다.
- Needle — 의류 덧대기·패딩·패치 제거 및 재료 회수 가능성을 같은 활용으로 묶었다. 깊은 상처 봉합의 붕대·유리 제한과 매트리스 제작은 각각 독립적으로 유지하며 문형을 간결하게 했다.
- WhiskeyEmpty/연료 용기 — 주유기 전력과 차량 엔진 정지 조건을 보존하며 급유·연료 이동의 반복 표현을 줄였다. 물 보관·운반, 화염병 재료, 깨진 병 회수는 각각 별도 활용이다.
- RippedSheetsDirty/재료 공통 경로 — 제작 결과마다 반복하던 제작 서술을 하나로 묶고 결과 이름을 보존했다. compact의 장치 제작/기타 제작도 하나의 제작 목적 안에서 설명한다. 상처 감염 위험과 천 세척은 유지한다.
- 연료·불쏘시개 — expanded에서 같은 시설을 두 번 열거하던 문장을 공유 대상과 한쪽 용도에만 해당하는 대상으로 합성했다. 통나무가 든 드럼에는 불쏘시개 용도만 적용해 연료 기능으로 넓히지 않는다.
- Log/TreeBranch/WoodenStick — Log의 목공·건축 및 숯 제작 재료 문형을 정리했다. 마찰 점화의 시설 목록은 compact에서 점화 목적과 방법으로 요약하고 expanded에서 시설별 대상 및 지구력·파손 조건을 보존한다. 골절 고정, 제작 재료, 연료, 묶기와 수박 손질 같은 독립 활용은 유지한다.
- 문면 교정은 완료했다. 이전 사실 근거 보류(가구의 구체 매핑, 잡지 학습 사실 채택, 기존 차량/L4 공급 공백)를 설명이 길다는 이유의 미완료와 섞지 않는다. 이를 새 기능이 확인되었다는 뜻으로 변경하지 않는다.
- 현재 문장 교정 범위 완료. 제품 상태 implemented_only, 실제 게임 미관찰.
- FullType 완성 문장 override, 생성 JSON 수동 수정, 글자 수 강제 절단, 독립 활용 삭제 없음.
- 기존 근거 보류는 별개 사실 공백으로 유지. 이전 기록과 후보 보존. 새 검증 체계/외부 접근/설치/commit/push 없음.

Descriptions SHA256: `e8d6c3a2320f63b9ab75b9aeac3edc0977ebada5c9a698982b3e12b666aa859b`

Blocks SHA256(불변): `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`

**Base.WaterPot**

Before KO compact: 붕대 소독에 쓸 수 있다. 재료를 담아 요리할 수 있다. 물을 보관, 운반하고 용기나 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After KO compact: 조리와 붕대 소독에 쓸 수 있다. 물을 보관, 운반하거나 용기, 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험).

After EN compact: It can be used for cooking and disinfecting bandaging. It can store, carry and pour water into containers or storage fixtures; its water serves for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning.

**Base.WaterMug**

Before KO compact: 물을 보관, 운반하고 용기나 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다. 재료를 더해 요리를 만들 수도 있다 (오염수 음용은 중독 위험).

After KO compact: 물을 보관, 운반하거나 용기, 저장 시설에 부을 수 있다. 담긴 물은 작물 급수, 차량 혈흔 세척, 소화, 음용에 쓸 수 있다 (오염수 음용은 중독 위험). 재료를 더해 요리를 만들 수도 있다.

After EN compact: It can store, carry and pour water into containers or storage fixtures; its water serves for watering crops, washing vehicle bloodstains, extinguishing fires, and drinking; drinking tainted water risks poisoning. Ingredients can also be added to prepare food.

**Base.Screwdriver**

Before KO compact: 전자기기 제작과 분해 및 조명 개조, 목공 및 건축물 분해, 차량과 무기의 부품 장착과 제거에 사용할 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After KO compact: 전자 부품, 무전기 제작과 전자기기 분해에 쓸 수 있다. 조명을 건전지용으로 개조할 수 있다. 목공, 건축물 분해, 차량 부품과 호환 무기 부착물의 탈부착에 쓸 수 있다. 제작한 창에 부착하거나 무기로 쓸 수도 있다.

After EN compact: It can make electronic components and radios or dismantle electronic devices. It can convert lamps to battery power. It can be used for woodworking, structure disassembly; fitting and removing vehicle parts and compatible weapon attachments. It can also be attached to a crafted spear or be used as a weapon.

**Base.Hammer**

Before KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 수박 쪼개기, 문과 창문의 판자 바리케이드 설치와 철거에 사용할 수 있다. 무기로도 쓸 수 있다.

After KO compact: 금속을 단조하는 데 사용할 수 있다. 목공, 건축, 문과 창문의 판자 바리케이드 설치와 철거에 쓸 수 있다. 수박을 쪼개는 데 쓸 수 있다. 무기로도 쓸 수 있다.

After EN compact: It can be used for metal forging. It can be used for woodworking and construction; installing or removing plank barricades on doors and windows. It can be used to break a watermelon. It can also be used as a weapon.

**Base.Shovel**

Before KO compact: 무덤 파기와 메우기, 밭 만들기와 정리(수확 제외), 재 청소, 흙이나 모래, 자갈 담기 작업에 쓸 수 있다. 무기로 쓸 수 있다.

After KO compact: 무덤 파기와 메우기, 밭 만들기와 정리(수확 제외)에 쓸 수 있다. 재 청소, 흙이나 모래, 자갈 담기에 쓸 수 있다. 무기로 쓸 수 있다.

After EN compact: It can be used for digging and filling graves and preparing and clearing planting beds without harvesting. It can be used for ash cleanup and bagging dirt, sand or gravel. It can be used as a weapon.

**Base.Needle**

Before KO compact: 의류의 구멍을 덧대거나 패딩을 붙이고, 패치를 뗄 수 있다. 뗀 패치 재료를 돌려받을 수도 있다. 붕대가 감기지 않고 유리가 없는 깊은 상처를 봉합하는 데 사용할 수 있다. 매트리스 제작에 사용할 수 있다.

After KO compact: 의류의 구멍을 덧대거나 패딩을 붙이고 패치를 제거할 수 있다. 제거 시 재료가 회수될 수 있다. 붕대를 감지 않았고 유리가 없는 깊은 상처를 봉합할 수 있다. 매트리스 제작에 사용할 수 있다.

After EN compact: It can mend garment holes, add padding and remove patches, with a chance to recover the removed material. It can stitch a deep wound that is unbandaged and free of glass. It can be used for mattress crafting.

**Base.WhiskeyEmpty**

Before KO compact: 전원이 공급되는 주유기에서 연료를 받거나 엔진이 꺼진 차량과 연료를 주고받을 수 있다. 물을 담아 보관하거나 운반할 수 있다. 화염병 제작에 재료로 사용할 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.

After KO compact: 전원이 있는 주유기에서 급유받거나 시동이 꺼진 차량과 연료를 주고받을 수 있다. 물을 담아 보관하거나 운반할 수 있다. 화염병 제작에 재료로 사용할 수 있다. 깨뜨려 깨진 병을 얻을 수 있다.

After EN compact: It can receive fuel from a powered pump or exchange fuel with a vehicle whose engine is off. It can hold water for storage or carrying. It can be used as a material for making Molotov Cocktail. It can be broken to obtain Smashed Bottle.

**Base.RippedSheetsDirty**

Before KO compact: 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축, 장치 제작, 그 밖의 물품 제작에 재료로 쓸 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After KO compact: 상처에 감을 수 있다. 감염된 상태로 쓰면 상처를 감염시킬 수 있다. 물로 씻어 깨끗한 붕대 재료로 바꿀 수 있다. 건축, 장치 등 물품 제작에 재료로 쓸 수 있다. 연료나 불쏘시개로 쓸 수 있다.

After EN compact: It can be wrapped around wounds. If infected, it can infect the wound. It can be washed with water into clean bandaging material. It can be used as material for construction and crafting devices and other items. It can be used as fuel or tinder.

**Base.Log**

Before KO compact: 목공, 건축, 물품 제작에 재료로 쓸 수 있다. 모아서 묶을 수 있다. 빈 금속 드럼에서 숯을 만드는 재료로 사용할 수 있다. 수박 쪼개기에 사용할 수 있다. 연료로 소모할 수 있다.

After KO compact: 목공과 건축, 물품 제작에 재료로 쓸 수 있다. 모아서 묶을 수 있다. 빈 금속 드럼의 숯 제작 재료로 쓸 수 있다. 수박 쪼개기에 사용할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used as material for woodworking and construction and crafting. It can be bundled with other logs. It can be made into charcoal in an empty metal drum. It can be used for breaking a watermelon. It can be consumed as fuel.

**Base.TreeBranch**

Before KO compact: 골절 고정에 쓸 수 있다. 목공, 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 모닥불, 비프로판 바비큐, 벽난로, 통나무 드럼의 점화를 시도할 수 있다. 연료로 소모할 수 있다.

After KO compact: 골절 고정에 쓸 수 있다. 목공, 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 불 피우기를 시도할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used for splinting fractures. It can be used as material for woodworking and crafting. It can be used to attempt lighting fires by wood friction. It can be consumed as fuel.

**Base.WoodenStick**

Before KO compact: 골절 고정에 쓸 수 있다. 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 모닥불, 비프로판 바비큐, 벽난로, 통나무 드럼의 점화를 시도할 수 있다. 연료로 소모할 수 있다.

After KO compact: 골절 고정에 쓸 수 있다. 물품 제작에 재료로 쓸 수 있다. 나무 마찰로 불 피우기를 시도할 수 있다. 연료로 소모할 수 있다.

After EN compact: It can be used for splinting fractures. It can be used as material for crafting. It can be used to attempt lighting fires by wood friction. It can be consumed as fuel.

전체 Before/After는 기존 `iris_dvf_description_review.html`, 전체 최신 문장은 `iris_dvf_descriptions.html`에 갱신했다. 이전 `.tmp/menu/run-fbgcwee9/p/Iris.zip`은 보존하며 최신 후보라고 재사용하지 않는다.


### 긴 목록·중복 서술 교정 최종 검사와 새 후보

기존 최소 3노드 묶음: **3 passed in 146.16s (0:02:26)**, 정확한 명령 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

로그: `.tmp/prose/complete-tests.log`. Blocks/상류 생산자는 바꾸지 않아 별도 block 검사를 추가하지 않았다. Lua syntax와 런타임/메뉴/package 검사는 공통 product node의 같은 stage/ZIP 결과를 공유했다. 새 Gate, 전체 Run A/B, 추가 confidence 실행은 없다.

- 새 ZIP: `.tmp/menu/run-fffuyq8m/p/Iris.zip`
- SHA256: `01a2a68b4ca4f0bf0858321c85eeda877710dd9071a0e9f2ec7b797f60cb225d`
- product: `l3p-36d19f03c0b17a9cf8c726e23172275b9a66306b65d79c678dec65c42291dcef`

최신 compact(S2)와 expanded(Menu)의 source 결속을 기존 제품 경로에서 검증했다. S3 획득/Acquisition 문형을 보존한 실제 ZIP의 static row를 읽었으며 Base.CannedMilk에는 S3가 없다. 이전 run-fbgcwee9 후보는 보존한다. **implemented_only**, 실제 게임 미관찰. 설치/commit/push 없음.
