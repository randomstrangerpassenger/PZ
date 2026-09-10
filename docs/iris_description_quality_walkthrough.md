# Iris 설명 품질 개선 Walkthrough

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
