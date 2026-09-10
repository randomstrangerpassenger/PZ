# DVF description quality acceptance — final

2026-09-11. **Complete — offline corpus quality acceptance 및 B/C common handoff 범위.** 최초 `10685bc0…` 완료 수락은 감독 원문 검토에서 실제 중복·compact 결함이 확인되어 철회하고 partial로 되돌렸다. 이후 공통 수정과 영향 조합 재독을 수행했다. 사용자의 추가 지시에 따라 **바닐라 생존 모드 설명에서 치트 모드 관련 공개 문구를 모두 제거했다.** 이전 전체 읽기 수나 테스트 성공만으로 최초 문장의 적합성을 방어하지 않는다.

## 최종 subject와 회계

| 항목 | 값 |
| --- | --- |
| Corpus | `Iris/build/description/composition/descriptions.json` |
| SHA-256 | `ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0` |
| Schema / version | `iris-layer3-descriptions-v1` / `1` |
| Input | `Iris/build/description/composition/blocks.json` |
| Input SHA-256 | `b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796` |
| Baseline SHA-256 | `bef16e498e1d7ba007379310535be4d707b9877dce97e7ebc7109afd7e1364bf` |
| 전체 | 2,105 items / 8,420 states |
| 분포 | present 8,054 / absent 366 / failed 0 |
| KO / EN 각각 | compact present 1,984 / absent 121; expanded present 2,043 / absent 62 |
| Baseline 대비 변경 | KO compact 996 / expanded 1,317; EN compact 996 / expanded 1,311 — 총 4,620 surface |
| 공개 문구 확인 | KO/EN 양 깊이 전체 text의 `치트` / `cheat` 잔존 0 |

Producer/input/source identity와 item별 disposition은 기존 corpus metadata 및 [검수 기록](review/prose/review.json)에 있다. Source predicate와 refs는 추적용 원형을 유지한다. 사용자 지시에 따라 치트 전용 예외를 공개 설명에서 표현하지 않는 것은 의도된 생존 모드 범위 결정이다. 입력 문자열까지 지워 출처를 재작성한 것이 아니다.

Q1: 빈 blocks 62개 item의 네 surface 248개와 acquisition-only 59개 item의 compact 118개가 정상 부재다. Current input의 blocks/class와 양 locale state/reason에 근거하며, 이를 사실 조사 완료나 언어 PASS로 계산하지 않았다. Present 8,054개는 자체 item 검수 수락이다.

## 실제 읽기와 교정

`88fbf9c…`에서 semantic/item 조합 673개 전체(2,105 items)의 실제 KO/EN 양 깊이와 branch·qualifier 적용·relation·unresolved를 읽었다. Acquisition은 공통 공개 표현 입력과 item membership을 포함한 81개 route 조합 전체(1,025 items, 1,057 route facts)를 읽었다. 이후 320개 조합/992개 item 및 18개 조합/29개 item의 교정 결과를 읽었으나, 최초 수락에는 아래 실제 결함을 놓친 판단 오류가 있었다.

감독 지적 이후 공통 수정 결과 68개 조합/109개 item, 추가 음식·용기 배치 수정 24개 조합/71개 item, 유일 기능 fallback 1개 item, 건축 조건 결합 2개 item을 재독했다. 사용자 지시로 치트 문구가 바뀐 10개 item 조합 전체와 여러 role을 가진 BlowTorch의 연속 설명도 읽었다. 실제 읽기 이력은 같은 검수 기록에 남겼다. 변경되지 않은 input과 record는 유효한 이전 읽기를 공유한다. 추출이나 동일 문자열만으로 새로운 scope를 수락하지 않는다.

Q2의 공통 수정 owner는 `description_composition_results.py`, `description_composition_families.py`, `description_composition_lexicon.py`, `description_composition_planner.py`다. 저장 JSON 직접 치환, FullType별 문장 대체, 새 사실·인과관계는 사용하지 않았다.

| 실제 before / 결함 | 공통 수정과 after / 영향 |
| --- | --- |
| Plank/Hammer에서 건축 context와 material/tool 설명이 전체 조건을 재출력 | 같은 branch의 context 조건을 먼저 설명하고 role 설명은 “앞의 조건에서…”로 이어 추가 조건만 표현한다. 여러 role의 조건 의미가 같으면 다음 role도 명시적으로 이어 받는다. 각 segment의 원래 refs와 qualifier application은 별도로 유지한다. Construction과 같은 구조의 FishingRodBreak에도 적용된다. |
| Plank 목공의 운전 금지 반복 | SAWN_WOOD와 WOOD_SHAPING의 같은 scope에서 각 재료·도구 대안을 구분한 뒤 “어느 작업도 운전 중에는 할 수 없다”로 한 번 설명한다. Log 등 같은 predicate 조합도 적용된다. |
| MakeupFoundation “적용할 수 있다 / 선택해 적용한다”, 제거 기능과 조건의 재반복 | Makeup 공통 기능 실현과 조건을 분리하고, 제거는 “같은 접근 조건에서 등록된 착용 분장도 지울 수 있다”로 잇는다. Compact는 “분장을 하거나 등록된 착용 분장을 지우는 데 쓴다.” Lipstick/Eyeshadow도 해당 부위에 맞춰 적용된다. 거울 면제는 소지/선택한 파운데이션으로 구체화하고 상세에 둔다. |
| Notebook compact의 읽기·쓰기 권한/필기구·잠금 및 점화 절차 누적 | 실제 조건을 가진 메모/연료/불쏘시개 기능만 요약한다. After: “메모를 읽고 적는 데 쓰거나 연료·불쏘시개로 소모할 수 있다.” Journal, Doodle, SheetPaper2에도 적용된다. 조건 없는 fixture는 일반 보존 경로를 쓴다. |
| CandleLit 점화 대상 7종과 추상적인 portable-light controls | 기능군으로 요약한다. After: “불을 붙이는 데 쓰거나 현재 상태가 허용하면 휴대 조명으로 쓸 수 있다.” 점화 대상·수단은 expanded에 남고, 조명의 실제 발광을 무조건 보장하지 않는다. Lighter, Matches, 휴대 조명 계열에도 적용된다. |
| WaterPot의 “조리 재료 추가에 쓰는 바탕 재료” | Base role을 “재료를 더해 요리를 만들 수 있다”로 표현한다. 물의 용도와 별도 요리 용도를 구분해 연결하고 오염수 음용 위험은 compact에 유지한다. 다른 식품·용기의 같은 role도 적용된다. 물 보관 기능만으로 조리 가능성을 추정하지 않는다. |
| 음식 나누기의 material/function 중복, 연료 용기의 주유 절차 나열 | 동일 scope의 food_portioning을 한 번 표현한다. 연료 용기는 “점화와 꺼진 발전기·차량의 급유에 쓰는 연료 용기다”로 요약한다. 용기 비우기는 다른 주용도가 있을 때 상세로 옮기되 유일 기능이면 compact에 남긴다. |
| 생존 모드 설명에 치트 전용 예외 표시 | 건축 공통 단독/결합 어휘에서 공개 예외 문구를 삭제했다. 10개 item의 expanded 20개 surface가 영향 범위이며, 일반 기술·도구·재료·배치와 정상 소모 조건은 유지한다. |

앞선 점화의 잘못된 도구 역할, 차량 부품, 배터리, 독서 감정 상한, 세척, 치료·파종, 포장 등의 유효한 공통 교정은 유지한다. 실제 result edge가 필요한 결합과 독립 효과 병렬화를 구분하며, upstream 미확정을 확정하지 않는다. 현재 범위의 발견된 결함은 수습했으며, 물리적 화면 fit은 측정하지 않았다.

## 마지막 검사

PowerShell, cwd `C:/Users/MW/Downloads/coding/PZ`:

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py -q
```

**최종 exit 0 — `1 passed in 4.96s`.** 이 마지막 변경 묶음은 한 번에 통과했다. 기존 한 검사에서 전체 입력 생산·의미/refs·scope·detail linkage·저장 readback을 공유한다. 마지막 저장본의 공개 문구 전체를 확인해 치트 관련 표현 잔존 0을 기록했다. 추가 검사기·gate는 만들지 않았다.

앞선 재작업 검사에서 조건 없는 불쏘시개 fixture를 메모에 흡수한 결함이 실패로 드러나 정확한 predicate guard를 추가했다. 검사 기대값은 완화하지 않았다. 다른 이전 시도에서는 저장 `os.replace`의 Windows `WinError 5`가 발생했고 같은 명령 재실행으로 성공했다. 이번 공개 어휘 생성도 첫 저장 교체에 실패한 뒤 생성 명령 재실행으로 성공했다. 실패를 PASS로 기록하지 않았으며 세부 이력은 기존 검수 기록에 있다. 검사들은 모두 10초 안에 종료해 장기 실행 중단이 필요하지 않았다.

## Q3 — 같은 최종 corpus 인계와 한계

B 좌표는 `items[].locales[ko/en].compact`, C 좌표는 같은 item/locale의 `expanded`다. Segments의 block/branch/fact/relation/qualifier refs, item의 qualifiers/relations/unresolved_relations, compact detail_links/qualifier_dispositions, state/reason을 함께 소비한다. Failed를 absence로 바꾸거나 다른 locale/r6로 대체하지 않는다. Schema/read_result 계약은 유지한다.

B의 기존 `tooltip_s2_supply`는 r6 `s2`를 소비하므로 adapter·production admission은 후속 B 책임이다. 이 인계를 B/C runtime 구현, r6/adoption/current Tooltip/Menu, package/install/pointer, 실제 네 줄 fit, release/Workshop 또는 전체 fact 조사 완료로 승계하지 않는다. 독립 reviewer는 사용하지 않았으며 자체 검수다.

Problem 1/blocks/shared r6 vocabulary를 수정하지 않았고 기존 dirty 작업을 reset/commit하지 않았다. 책임·흐름·소비 계약 이전이 없어 ARCHITECTURE 본문은 유지한다. Results 모듈의 실제 합성 책임에 대한 기존 요약의 서술 한계는 남아 있다. `read_corpus.py`와 읽기 기록은 일회성 작업 보조 자료이며 canonical validator나 새 validation authority가 아니다. 같은 얕은 비교 경로를 재사용했고 seal/receipt/manifest/proof tree를 추가하지 않았다.

## 일반 도구·재료 compact의 최종 교정

`ffbf506b…`에서도 일반 role/function 조합의 작업 목록이 길게 남아 있어 완료 수락을 보류하고 이 공통 규칙을 수정했다. `description_composition_families.py`의 role_overview는 입력에 실제 있는 건축/목공/금속·부품·삽 단조를 제한된 건축·제작 상위 용도로 묶는다. 가구 이동은 제작의 하위로 취급하지 않는다. 바리케이드 추가/철거가 모두 있을 때만 설치·철거로 묶고, 한쪽만 있는 물품에 반대 기능을 추가하지 않는다. 근접 공격의 차량 제한과 부목의 신체 부위·조건은 actual expanded에 유지한다. 모든 제작을 지원한다는 뜻을 피하려고 일부/certain 작업으로 한정했다.

Hammer의 기존 “건축·금속 가공·가구 이동·삽류 단조·목공…차량 밖…문·창문…”은 “일부 건축·제작·가구 이동 작업의 도구이며, 근접 공격, 판자 바리케이드 설치·철거에 쓸 수 있다.”로 바뀌었다. Plank는 “일부 건축·제작 작업의 재료이며, 근접 공격, 부목 적용에 쓰거나 연료로 소모할 수 있다.”로 바뀌었다. 무기·부목·연료와 도구/재료 역할을 삭제하거나 primary_use로 줄이지 않았다.

해당 공통 규칙의 실제 영향 29개 조합/31개 item을 KO/EN으로 재독했다. 변경은 compact 62개 surface이며 expanded 원문·참조는 모두 그대로다. 마지막 focused 검사는 한 번에 exit 0 (`1 passed in 4.96s`). 이 교정은 별도 gate나 전체 재검수를 만들지 않고 기존 읽기·입력·검사 진입점을 공유했다.
