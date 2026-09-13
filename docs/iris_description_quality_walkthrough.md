# Iris 설명 품질 개선 Walkthrough

현재 후속 교정 결과는 문서 끝의 **용도 중심 producer 교정** 절을 따른다. 아래 최초 corpus 수락은 그 당시 생성본의 이력이며 새 후보의 인게임 품질 수락으로 승계하지 않는다.

작성일: 2026-09-11

이번 세션에서는 [설명 품질 수락 계획](iris_dvf_description_quality_acceptance_plan.md)에 따라 의미 블록에서 생성하는 KO/EN compact·expanded 설명을 검수하고, 발견한 문제를 공통 합성 규칙에서 수정했다. 최종 결과는 **오프라인 corpus 자체 품질 수락과 동일 corpus의 B/C 인계 완료**다. 이후 사용자 요청으로 DECISIONS·ROADMAP·ARCHITECTURE의 현재 상태와 실제 합성 책임을 정리했다.

이 문서는 구현과 수정 과정의 안내다. 기존 [closeout](iris_dvf_description_quality_acceptance_closeout.md)과 [읽기 기록](review/prose/review.json)의 결과를 활용했으며, 문서 작성을 위해 테스트·생성·추가 검증을 실행하지 않았다.

## 1. 해결한 문제

기존 설명에는 같은 조건을 context와 material/tool 역할마다 반복하거나, compact에 대상·절차·세부 작업 목록을 길게 나열하는 문제가 있었다. 반대로 요약을 과도하게 하면 독립 기능이나 제한 조건을 잃을 수 있었다.

이번 수정은 compact에서 실제 용도를 이해하기 쉽게 묶고 expanded에서 그 용도가 성립하는 조건을 읽을 수 있게 배치하는 데 집중했다. 같은 의미를 합칠 때도 branch·scope·predicate와 원래 참조를 보존했다. 개별 아이템 이름에 따른 문장 교체나 생성 JSON의 직접 치환은 사용하지 않았다.

사용자의 추가 지시에 따라 공개 설명은 바닐라 생존 모드 범위로 정리했다. 공개 문구에서 요청된 예외 표현을 제거하되, 추적용 source predicate와 refs는 유지했다. 게임 실행이나 upstream 사실 재조사를 수행한 것으로 취급하지 않는다.

## 2. 구현 위치와 데이터 흐름

입력은 `Iris/build/description/composition/blocks.json`, 출력은 같은 폴더의 `descriptions.json`이다. 기존 schema와 읽기 계약을 유지했다.

```text
blocks.json
  → planner: 의미 단위의 개요/상세 배치
  → results: compact·expanded 문장 합성, 조건 연결, 상세 연결
      → families: 의미 조합별 공통 문장 틀
      → lexicon 및 언어 모듈: 어휘·조건 표현·문법
  → model 및 results.write_result: 상태·연결 계약과 저장
  → results.read_result: 결과 읽기와 B/C 인계
```

| 파일 | 이번 세션의 주요 변경 |
| --- | --- |
| [description_composition_planner.py](../Iris/tooling/src/iris_tooling/domains/layer3/description_composition_planner.py) | 개요와 상세의 배치를 조정했다. 다른 주용도가 있는 용기의 비우기 기능은 상세로 옮기고, 유일 기능이면 compact에 남겼다. |
| [description_composition_results.py](../Iris/tooling/src/iris_tooling/domains/layer3/description_composition_results.py) | `_compact`·`_expanded`·`_clauses`에서 실제 문장을 합성한다. context와 role의 공통 조건을 명시적으로 이어 주면서 각 segment의 원래 refs를 유지했다. 요리 바탕 재료의 표현도 자연스러운 기능 설명으로 바꿨다. |
| [description_composition_families.py](../Iris/tooling/src/iris_tooling/domains/layer3/description_composition_families.py) | 메모·점화·분장·포장·도구/재료 개요 등의 공통 문장 틀을 개선했다. 실제 입력에 있는 기능과 허용된 의미 조합만 묶도록 제한했다. |
| [description_composition_lexicon.py](../Iris/tooling/src/iris_tooling/domains/layer3/description_composition_lexicon.py) | KO/EN 어휘와 동일 scope의 조건 표현을 정리하고, 생존 모드 공개 설명 범위를 반영했다. |
| [기존 focused test](../Iris/build/description/v2/tests/test_layer3_description_composition.py) | scope 분리, 추가 predicate의 fallback, 독립 역할 보존, 조건 연결 등에 필요한 최소 반례를 보강했다. |

Problem 1의 사실 입력, 의미 blocks, 공유 r6 vocabulary를 변경하지 않았다. 새 런타임 경로나 모듈 간 의존성을 도입하지 않았다.

## 3. 대표적인 설명 변화

아래 결과는 최종 KO compact의 예다. EN에도 같은 의미 규칙을 적용했다.

| 대상 | 이전 문제 | 최종 표현 |
| --- | --- | --- |
| Hammer | 건축·금속 가공·삽 단조·목공과 세부 행동 조건을 개요에 길게 나열 | 일부 건축·제작·가구 이동 작업의 도구이며, 근접 공격, 판자 바리케이드 설치·철거에 쓸 수 있다. |
| Plank | 재료의 세부 작업 목록과 독립 기능을 읽기 어렵게 나열 | 일부 건축·제작 작업의 재료이며, 근접 공격, 부목 적용에 쓰거나 연료로 소모할 수 있다. |
| Notebook | 읽기·쓰기 권한, 필기구, 잠금, 점화 절차가 compact에 누적 | 메모를 읽고 적는 데 쓰거나 연료·불쏘시개로 소모할 수 있다. |
| MakeupFoundation | 적용 기능과 제거 기능, 접근 조건을 반복 | 분장을 하거나 등록된 착용 분장을 지우는 데 쓴다. |
| CandleLit | 점화 대상 목록과 추상적인 조명 제어 표현이 누적 | 불을 붙이는 데 쓰거나 현재 상태가 허용하면 휴대 조명으로 쓸 수 있다. |

이 요약은 조건이나 독립 기능을 삭제하는 규칙이 아니다. 근접 공격의 차량 제한, 부목의 신체 부위·조건, 메모의 접근 조건, 점화 대상과 수단은 expanded에 유지했다. 오염수 음용 위험처럼 개요에도 필요한 부정적 정보는 compact에 남겼다.

도구·재료의 상위 용도는 입력에 있는 건축·목공·단조 등의 허용된 조합으로만 만들고, 모든 제작을 지원한다는 뜻을 피하도록 “일부/certain”으로 한정했다. 가구 이동은 별도 용도로 유지했다. 바리케이드 설치·철거를 함께 표현하는 것은 두 기능이 모두 있을 때뿐이다. BallPeenHammer의 설치 전용 기능이나 Crowbar의 철거 전용 기능에 반대 기능을 추가하지 않았다.

expanded의 건축 조건은 같은 branch에서 context 조건을 먼저 설명하고 role을 “앞의 조건에서…”로 연결했다. 여러 role이 같은 조건을 공유할 때도 그 관계를 명시했다. 단순히 같은 문자열을 지우는 방식이 아니며, 각 segment의 qualifier application과 refs는 별도로 남긴다.

음식·용기에서는 “조리 재료 추가에 쓰는 바탕 재료”를 “재료를 더해 요리를 만들 수 있다”로 바꿨다. 물 보관과 요리 기능은 실제 역할에 따라 구분하며, 물을 담는다는 이유만으로 조리 가능성을 추정하지 않았다. 같은 scope의 음식 나누기 역할과 기능은 한 번만 표현했다.

## 4. 검수 중 발견한 문제와 재작업

Q1에서는 전체 item의 네 좌표(KO/EN × compact/expanded)를 읽기 대상으로 삼고 정상 부재를 별도 계산했다. 실제 읽기는 의미 조합과 item membership을 함께 확인했고, 이후 수정은 영향을 받은 조합을 다시 읽었다. 입력과 record가 바뀌지 않은 부분은 기존 읽기 결과를 공유했다.

최초 완료 판단은 감독 작업의 원문 지적에서 건축 조건 중복과 분장·compact 결함이 드러나 철회했다. 읽은 수량이나 테스트 성공을 근거로 결함 있는 문장을 수락하지 않고 공통 규칙을 수정했다. 이후 일반 도구·재료의 긴 작업 목록이 남아 있다는 지적도 반영했다. 마지막 role 개요 수정의 영향은 29개 조합·31개 item이며, compact 62개 surface가 바뀌었다. 이 마지막 수정에서는 expanded 원문과 참조를 유지했다.

검사 중에는 조건 없는 불쏘시개 fixture가 메모 요약에 잘못 흡수되는 문제가 실제로 실패했다. 정확한 predicate guard를 추가해 일반 보존 경로로 돌렸으며 기대값을 완화하지 않았다. 이전 저장 시도의 Windows `os.replace` 권한 오류는 실패로 기록하고 같은 명령의 재실행 결과와 구분했다.

사용자가 요청한 공개 문구 삭제는 10개 item의 expanded 20개 surface에 반영했다. 기존 확인 기록상 KO/EN 양 깊이의 공개 text에 해당 표현의 잔존은 0이다.

최종 결과는 지정된 감독 작업(`01a07ad6-0377-7d62-9c8d-bc833a049714`)에 보고했고, 감독은 최종 subject와 지적 항목의 수정 결과를 확인하여 오프라인 자체 품질 수락 및 B/C 인계 범위의 closeout을 수락했다. 이는 감독의 전체 corpus 독립 재검수가 아니다. 별도 외부 reviewer는 사용하지 않았다.

## 5. 최종 산출물과 기존 검사 결과

| 항목 | 최종 기록 |
| --- | --- |
| Corpus | `Iris/build/description/composition/descriptions.json` |
| Schema / version | `iris-layer3-descriptions-v1` / `1` |
| Corpus SHA-256 | `ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0` |
| 입력 SHA-256 | `b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796` |
| 전체 | 2,105 items / 8,420 states |
| 상태 | present 8,054 / absent 366 / failed 0 |
| 기존 baseline 대비 변경 | KO compact 996 / expanded 1,317; EN compact 996 / expanded 1,311 — 총 4,620 surface |

absent 366개는 빈 blocks 62개 item의 네 좌표 248개와 acquisition-only 59개 item의 compact 118개다. 현재 입력에 따른 정상 부재이며 설명 품질 PASS나 전체 게임 사실 조사 완료로 계산하지 않았다.

최종 구현 변경 뒤 실행한 기존 focused 검사는 다음과 같다. 실행 위치는 저장소 루트이며 PowerShell을 사용했다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py -q
```

**최종 결과: exit 0, `1 passed in 4.96s`.** 하나의 전체 입력 생산 결과로 구조·의미·refs·scope·detail linkage·저장 readback을 검사했다. 이 결과는 최종 구현의 기존 실행 기록이며, 이번 Walkthrough 작성 중 새로 실행한 결과가 아니다. 세션의 검사들은 10초 안에 종료하여 장기 실행 중단은 필요하지 않았다.

## 6. B/C 인계 범위

B는 `items[].locales[ko/en].compact`, C는 같은 item·locale의 `expanded`를 소비한다. 문장과 함께 state/reason, segment의 block·branch·fact·relation·qualifier refs, item의 qualifiers·relations·unresolved_relations, compact의 detail_links·qualifier_dispositions를 사용한다. failed를 absent로 바꾸거나 다른 locale 또는 r6 출력으로 대신하지 않는다.

B의 기존 `tooltip_s2_supply`는 r6 `s2`를 소비하므로 adapter와 production admission은 후속 B 작업이다. C의 실제 연결도 후속 작업이다. 이번 완료는 게임 내 툴팁·메뉴 연결, 실제 한 줄/네 줄 화면 fit, current 전환, 패키징·설치·배포 완료를 포함하지 않는다.

## 7. 문서 정리와 유지보수 경계

구현 closeout 이후 별도 사용자 요청으로 세 문서를 최종 상태에 맞췄다.

- [DECISIONS.md](DECISIONS.md): 최종 자체 품질 수락, 생존 모드 공개 설명 범위, 철회·보완 이력과 B/C 인계 경계를 정리했다.
- [ROADMAP.md](ROADMAP.md): Q1·Q2·Q3 완료와 후속 adapter·화면 연결 작업을 구분했다.
- [ARCHITECTURE.md](ARCHITECTURE.md): results 모듈이 실제 문장 합성과 조건 연결을 담당한다는 점 및 planner/families/lexicon/model의 책임과 소비 흐름을 명시했다.

기존 closeout의 “ARCHITECTURE 본문 유지” 설명은 구현 closeout 당시의 상태를 가리킨다. 이후 요청된 문서 정리에서는 실제 코드 책임에 맞춰 ARCHITECTURE도 갱신했다. 문서 정리는 corpus나 런타임 계약을 다시 변경하지 않았다.

`docs/review/prose/read_corpus.py`와 비교·읽기 기록은 이번 작업의 일회성 보조 자료다. canonical validator나 새 validation authority로 승격하지 않았다. 같은 입력·생산 경계의 기존 결과와 얕은 경로를 재사용했고 추가 seal·receipt·manifest·proof artifact나 gate는 만들지 않았다. 기존 dirty 작업을 reset하거나 commit하지 않았다.

## 8. 용도 중심 producer 교정 — 2026-09-11

[용도 조사 보고서](iris_dvf_use_description_report.md)에 기반해 A·1·2의 기존 경로와 3의 검사 기대를 직접 교정했다. 별도 문제·계획·Gate나 validator는 추가하지 않았다. r6와 기존 dirty/deleted/untracked 작업을 보존했으며 branch/worktree/clone·commit·push·외부 게임 폴더 접근은 수행하지 않았다.

### 공통 규칙과 결과

- A `recovery_relations.py`: admitted 함수의 observation에 연결된 recipe 입력/keep/Result를 구조화한다. 선언 결과·무조건 callback 추가·조건부 callback 결과를 구별한다. 기존 결과 요리/파종 fact가 있을 때만 결과 활용을 연결한다. `TinOpener`는 기존 깡통 따개와 같은 식별자를 유지하면서 제품 명칭을 통조림 따개로 전달한다. 이름은 결과 선언과 활성 음식 개념/locale 표시명에서 얻는다.
- 문제 1 `composition_results.py`, `composition_model.py`: 원래 29,202개 fact와 block/branch ID를 보존하고 `use_relations`, `source_traits`를 전달한다. 도구 대안은 any_of, 여러 도구 슬롯은 결합 관계다. 포장 결과 수량은 파종 소모량과 별개로 보존한다.
- 문제 2 `description_composition_uses.py`, planner/results: 관리 대상의 세척·패치·이름 변경, 세척 처리 결과·조리자 metadata를 공개 용도에서 제외한다. 세척제, 착용, 직물/로프 재료, 연료/불쏘시개, 점화, 조명, 변환 회수와 독립 제작 재료는 남긴다. 획득은 블록과 기존 S3 공급에 유지하며 DVF 본문과 분리한다. 새 frame이 용도를 출력한 뒤 나머지 상세를 compact로 다시 끌어올리던 fallback도 고쳤다.
- 내부 사실 전체는 `preserved_fact_refs`, 제외 사유는 `internal_uses`에 연결한다. 공개 `public_use` 문장은 실제 주장한 기능/역할 refs만 사용한다. 표현하지 않은 실행 predicate의 refs를 이 문장에 넣지 않는다. 기존 exact-scope 문장의 조건 검사와 모든 독립 기능/재료 역할의 expanded 보존 검사는 유지한다.
- B/C: 새 Tooltip ZIP을 명시적 입력으로 받아 동일 corpus의 메뉴 후보를 구성한다. 기존 B 승인 ZIP `.tmp/tooltip/preview/Iris.zip`과 이전 C 후보는 보존했다. 패키지 검사는 고정된 과거 corpus hash 대신 새 입력의 실제 identity와 Tooltip/Menu corpus 일치를 확인한다. 런타임 문장 수정이나 UI 폭 확대는 하지 않았다.

최종 변화는 KO compact 753개, EN compact 752개, expanded 각 1,645개다. Expanded 변화에는 기존 획득 본문 분리도 포함된다. 두 언어 각각 compact/expanded present 1,984개, absent 121개, failed 0개다. 기존 획득 전용 59개는 DVF 본문 부재가 되었지만 블록/획득 공급은 남는다.

A가 전달한 명명 관계는 79개다: 통조림 19, 농산물 자루 18, 전자제품 분해 12, 병 식품 9, 탄약 상자 8, 씨앗 봉지 7, 일반 상자 4, 달걀 포장 1, 개구리 1. 새 명명 frame은 이 중 확인한 65개 관계에 적용했다. 병 식품·일반 상자·달걀의 기존 callback 전용 표현은 유지하여 뚜껑 등 별도 결과를 잃지 않게 했다. 전체 적용 관계의 EN 요약과 대표 KO, 복합 역할을 읽었고 자동 검사는 2,105개 전 항목에서 독립 용도 보존을 비교했다. 세척 대상 함수는 778개, 패치 대상은 194개, 세척제 2개, 휴대 조명 5개에 존재한다.

| 대표 항목 | 교정 전 발췌 | 현재 KO 결과/의미 |
| --- | --- | --- |
| 양말 | 물로 피·때 세척, 완전히 젖음, 이동 중단, Cotton에 데님·가죽 가위 조건 | 연료·불쏘시개로 소모할 수 있다. 양말 자리에 착용한다. 찢어 직물을 회수하는 재료다. 시트 로프 제작에 쓰는 재료다. |
| 비누 | 몸 세척에 의류 결과·물 부족 처리까지 결합 | 몸과 의류·장비를 물로 씻을 때 쓰는 세척제다. |
| 옥수수 통조림 | 맞는 개봉 도구로 내용물을 꺼내는 통조림 | 통조림 따개로 개봉해 꺼낸 옥수수를 요리 재료로 쓸 수 있다. |
| .223 상자 | 탄약이 든 상자 | 도구 없이 개봉해 .223 탄약을 얻을 수 있다. |
| 당근 자루 | 농산물·신선도 설명 | 도구 없이 개봉해 꺼낸 당근을 요리 재료로 쓸 수 있다. |
| 당근 씨앗 봉지 | 이 작물의 낱알 씨앗 | 봉지를 열어 꺼낸 당근 씨앗을 파종하는 데 쓸 수 있다. Expanded의 봉지 선언 수량 50과 내부 파종 소모 12는 서로 다른 관계다. |
| 개구리 | 허용된 칼로 손질해 고기 | Compact는 개구리 고기를 명명한다. Expanded는 돌칼/사냥용 칼/부엌칼/마체테/중식도 대안과 도구 비소모를 보존한다. |
| 리모컨 | 전자 부품 회수, 추가 부품 비보장 | 수신기·전기 회로 부속 회수와 건전지 가능성을 구별한다. 타이머·원격 조작 부품 제작 재료는 별도 용도로 남는다. |

부서진 어망의 `Wire;3`를 철사 3개 확정 회수로 바꾸지 않았다. 열쇠의 동적 일치와 문 잠금 비소모/자물쇠 제거 소모도 유지했다. 라이터의 점화·휴대 조명, 손전등의 조명·분해 회수, TinnedBeans의 직접 제작 참여와 개봉 후 요리 재료 관계를 보존했다.

근거 정정 두 가지: `Make Pot of Soup`의 미개봉 CannedMushroomSoup 예시는 `scripts/recipes.txt:194`의 주석 구간에 있어 활성 제작법으로 추가하지 않았다. Onion은 실제 EvolvedRecipe 없이 `EvolvedRecipeName=Mushroom`만 남아 있으므로 양파 자루 결과를 버섯이라고 쓰지 않고 확인된 양파 표시명을 사용한다. 양파에 요리 재료 용도를 새로 전이하지 않는다. 보고서 조사 이력은 유지하고 첫 근거의 정정만 보고서에 표시했다.

### 실행한 기존 필수 검사

PowerShell, 저장소 root에서 실행했다. 최초 묶음은 문장 fixture 실패로 `1 failed, 2 passed`(102.93초), exit 1이었다. 공통 frame 이후 compact fallback이 상세를 재노출한 문제와 명명 guard를 고친 뒤 다음 묶음이 **3 passed in 101.84s, exit 0**이었다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py .\Iris\build\description\v2\tests\test_layer3_description_composition.py .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration --basetemp .\.tmp\tooltip\uses -q -s
```

B 통합 내부의 `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`, Tooltip runtime supply harness, 후보 `package_iris.ps1 -Zip`도 각각 exit 0이다. B 새 후보 ID는 `ttp-b21cade30605f97143149ea7d3e1c89b86415307b7f6537b46484e60039a8828`이다.

C 기존 검사 최초 실행은 고정된 판자 첫 단위 길이를 요구하던 Lua 기대에서 exit 1(38.45초)이었다. 전체 source 단위/범위 대조를 유지하고 위치 고정 기대만 제거했다. 같은 `.tmp/menu/run-w3ghss8_`의 제품/입력/단계를 재사용했으며 완료된 source/stage Lua syntax(exit 0, 388 files)는 반복하지 않았다. 실패했던 모델과 이어지는 기존 runtime/package 검사를 다음 명령으로 실행해 **1 passed in 52.57s, exit 0**을 얻었다.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
$env:IRIS_MENU_TOOLTIP_CANDIDATE='.tmp/tooltip/uses/Iris.zip'
$env:IRIS_MENU_RESUME_PACKAGE='C:/Users/MW/Downloads/coding/PZ/.tmp/menu/run-w3ghss8_'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_product_integration.py --basetemp .\.tmp\menu\uses -q -s
```

Browser/Wiki 4,210 locale 상태, B 2,280 지원 key, L4 모델, package admission, `package_iris.ps1 -PackageApplicability current_runtime_payload -Zip`, ZIP 내부 C pointer/model이 각각 exit 0이다. fit failure 로그는 의도된 작은 화면 fixture의 거부 검사이며 실제 PZ 화면 관찰이 아니다. 장기 실행은 도구 세션으로 상태를 확인했고 중단할 비정상 실행은 없었다. 저장소 전체 Run A/B/comparator와 Java/JS 검사는 실행하지 않았다.

### 검토 후보와 남은 범위

- 데이터: [blocks.json](../Iris/build/description/composition/blocks.json), [descriptions.json](../Iris/build/description/composition/descriptions.json).
- 교정 B 단독 후보: [Tooltip Iris.zip](../.tmp/tooltip/uses/Iris.zip).
- 사용자 검토용 동일 corpus B/C 통합 후보: [Iris.zip](../.tmp/menu/uses/Iris.zip). 기존 검사 산출물 `.tmp/menu/run-w3ghss8_/p/Iris.zip`을 그대로 복사했다. SHA-256 `6503a9466554596ab84ca346b641e0f9ac83ca749e7c838b03b03c4a03ecaeb2`, C ID `l3p-289febd9bb92e3b88ca86437084dd378ee68b9161799a5ae1a48eefceaa0c4d5`.

Producer 교정과 위 오프라인 공급/패키지 검사는 완료했다. 기존 B 사용자 인게임 통과 상태는 이전 승인 후보에 그대로 귀속한다. 새 후보의 실제 PZ 폰트·해상도·Alt 네 물리적 줄, KO/EN 메뉴 가독성과 상호작용은 사용자 검토 전이다. C는 implemented_only이며 실제 메뉴 품질 통과로 올리지 않는다. Native 결과 전달, 미확정 어망 결과, 미래 모드와 미확인 차량/가구/낚시 범위는 새로 확정하지 않았다. 추가 증명이나 자동 감독은 남은 작업이 아니다.
