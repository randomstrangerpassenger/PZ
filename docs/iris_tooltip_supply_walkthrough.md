# Iris Tooltip 공급·표시 Walkthrough

작성일: 2026-09-11  
상태: **B 후보 구현·통합·실제 표시 complete — 사용자 PZ 확인 및 명시적 수락**

이 문서는 현재 세션에서 수행한 새 DVF compact 공급, Tooltip 역할 복구, 후보 패키징, 검증 및 문서 정리를 설명한다. 실행 기준은 [v3 구현 계획](iris_dvf_tooltip_s2_supply_ownership_recovery_plan.md)이며, 정확한 실행 결과와 최종 수락 기록은 [closeout](iris_tooltip_supply_closeout.md)을 따른다. 새로운 검증 계약이나 authority를 정의하지 않는다.

## 1. 출발점과 해결한 문제

착수 시 저장소에는 이전 B 구현과 다른 작업의 수정·삭제·미추적 파일이 함께 있었다. 기존 변경을 보존하고 계획에 필요한 코드와 문서만 수정했다. 저장소 밖 파일을 탐색하거나 외부 checkout을 만들지 않았으며 원본 commit/reset/clean도 하지 않았다.

기존 후보·설치 경로는 재사용할 수 있었지만 다음 차이가 있었다.

| 영역 | 착수 시 동작 | 이번 구현 |
| --- | --- | --- |
| S2 공급 | r6 adoption의 `s2` 소비 | 검수된 description corpus의 `compact` 원문 소비 |
| 부재 상태 | r6의 scoped/gap 분류 | 새 corpus의 `absent` 및 원래 reason 보존 |
| S3/S4 | strict T1에서 두 행 모두 L4 상호작용 | 후보에서 S3 획득 장소, S4 유효 상호작용 하나로 재매핑 |
| S4 변형 | 레시피 중심 companion | 레시피·우클릭·자유 조리를 하나의 선택 목록으로 연결 |
| 화면 표시 | 최대 360px 패널 안에서 한 행을 여러 줄로 wrap | 원문 측정 폭에 맞춘 패널, 한 역할당 한 화면 줄 |

따라서 S2 문자열만 교체하거나 기존 S1/S3/S4 equality를 그대로 적용해서는 v3를 충족할 수 없었다. 후보에서 바뀌는 역할을 명시하고, 일반 strict/historical 경로의 기존 의미와 구분했다.

## 2. 새 설명 입력과 공급

입력은 이미 검수된 `Iris/build/description/composition/descriptions.json`이다. SHA-256은 `ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0`이며, 의미 입력 `blocks.json`의 SHA-256은 `b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796`이다. 이번 세션에서는 corpus를 재생성하거나 composition 문장을 수정하지 않았다.

`tooltip_s2_supply.py`는 `description_composition_results.read_result`로 저장 결과를 읽고 입력 identity를 확인한다. Compact의 text, state/reason, segments와 의미 참조, detail links, 존재하는 qualifier dispositions를 원형으로 전달한다. Expanded와 qualifiers/relations/unresolved도 offline subject에 보존한다. Runtime은 이 자료에서 완성된 표시·선택 데이터만 받으며 문장을 다시 조합하거나 번역하지 않는다.

Supply schema v2의 상태는 `present`, `absent`, `out_of_dvf_target`이다. 로드 실패·손상·미지원 schema를 정상 부재로 바꾸거나 r6/다른 locale로 대체하지 않는다. 저장소 밖을 가리키는 admitted locator는 읽기 전에 거부한다.

지원 집합 T는 기존 owner/admission으로 확인하고 D는 새 corpus에서 구했다. 과거 개수나 Lua key만으로 권한을 정하지 않았다.

| 항목 | 이번 결과 |
| --- | ---: |
| Tooltip 지원 T | 2,280 |
| DVF 대상 D 및 T∩D | 2,105 |
| T-D / D-T | 175 / 0 |
| 각 locale compact present / absent | 1,984 / 121 |

대상 밖 175개는 기존 owner의 정당한 부재로 확인했다. 새 compact 부재 121개를 옛 r6 scoped/gap 분류로 다시 해석하지 않았다.

## 3. 네 역할의 조립과 소유권

```text
description corpus → read_result → tooltip_s2_supply v2
                                      ↓
admitted classification/support → s2_candidate v2 ← acquisition facts / QG owners
                                      ↓
                         T2 static + interaction companion
                                      ↓
                         Tooltip install/package → Lua runtime
```

S1은 admitted classification 원문과 identity를 보존한다. S2는 같은 item/locale의 compact 원문이다. DVF가 S1이나 상호작용 문장을 새로 생산하지 않는다.

S3는 `s2_candidate.acquisition_places`에서 기존 acquisition facts의 장소 정보를 투영한다. 채집은 item/category의 유효 zone 교집합, 덫은 유효 zone, 낚시는 물가를 사용한다. 이번 후보의 장소 행은 1,016개다. 장소 표현을 만들 수 없는 경로는 S3 부재로 두며 expanded의 전체 획득 절차나 다른 L4 항목을 복사하지 않는다.

S4는 `recipe_variants.interaction_candidates`가 기존 QG usecase·recipe navigation·우클릭 번역과 Menu가 사용하는 EvolvedRecipe owner를 읽어 만든다. 각 owner의 유효성·의미 판단을 유지하고 표시용 종류 label을 붙인다.

| 종류 | 후보 수 | 표시 label |
| --- | ---: | --- |
| 레시피 | 781 | `[레시피]` / `[Recipe]` |
| 우클릭 | 86 | `[우클릭]` / `[Right-click]` |
| 자유 조리 | 2,203 | `[자유 조리]` / `[Freeform Cooking]` |

이 수치는 후보 수이며 아이템 수나 선택 확률을 뜻하지 않는다. 종류별 고정 순환이나 가중치는 추가하지 않았다. 기존 승인된 레시피 이름 부재 예외는 유지하고, 새로운 locale 누락·손상·미지원 source를 후보 없음으로 숨기지 않는다.

`project_interaction_variants`는 명시적인 slot identity로 S4만 교체하고 앞의 행을 보존한다. 후보 admission은 S1 보존과 새 S3/S4 owner 매핑의 정확한 결과를 확인한다. 다른 슬롯 변경을 무조건 허용하거나 이전 두 L4 행과의 equality를 강제하지 않는다.

기존 `s2-candidate` CLI와 `IrisTooltipRecipeVariants.lua` 이름은 호환을 위해 재사용했다. 이름과 달리 실제 후보는 S3/S4 변경을 포함하며 supply/candidate v2, 공급 계약과 T2 provenance에 이를 명시했다. 일반 strict T1/T2의 historical 매핑과 finalization 요구는 유지했다.

## 4. 실제 화면 줄 수와 선택 수명

`IrisAltTooltip.lua`에서 `wrapRow`와 360px 상한을 제거했다. 게임의 정상 폰트로 각 원문의 폭을 측정하고, 가장 긴 행이 들어갈 패널 폭을 선택한다. 패널은 화면 안에서 vanilla Tooltip과 겹치지 않는 옆·아래·위 위치에 배치한다.

한 역할은 한 화면 줄이며 정상 부재 행은 생략할 수 있다. 최대 네 줄을 맞추기 위해 문장 일부를 버리거나 말줄임·clipping·폰트 축소·runtime 요약을 사용하지 않는다.

화면 용량이나 배치 공간이 부족하면 opening에 `displayStatus=fit_failed`와 원인을 남기고 로그로 알린다. 이 경우 사용자에게 Tooltip이 나타나지 않을 수 있으므로 **정상 부재나 성공한 표시로 수락하지 않는다.** 추후 실제 환경에서 발생하면 renderer 또는 해당 표현 owner의 결함으로 다뤄야 한다.

선택은 기존 opening 단위를 유지한다. 여러 후보 중 하나를 고른 뒤 읽는 동안 같은 bilingual view를 사용한다. Locale 변경은 같은 identity의 언어만 바꾸며 매 프레임 재추첨하지 않는다. Alt 해제, 숨김, item 변경 등 기존 갱신 시점에 선택을 해제한다. 다시 열 때 같은 후보가 연속으로 나올 수 있다.

## 5. 변경 파일의 역할

아래는 이번 구현에서 수정한 주요 owner 파일이다. 이 세션 전에 존재하던 다른 변경 전체를 이번 작업의 성과로 귀속하지 않는다.

| 파일 | 변경 역할 |
| --- | --- |
| `Iris/tooling/src/iris_tooling/domains/layer3/tooltip_s2_supply.py` | 새 corpus reader와 상태·참조 공급 |
| `Iris/tooling/src/iris_tooling/domains/tooltip_t1/s2_candidate.py` | 네 역할 조립, acquisition place, 후보 source binding/admission |
| `Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/recipe_variants.py` | 세 종류 후보와 S4 단일 표시 companion |
| 같은 domain의 `projection.py`, `install.py` | 후보 역할 provenance 및 동일 static/companion 설치·패키징 연결 |
| `Iris/media/lua/client/Iris/Data/IrisTooltipStaticDataLookup.lua` | 후보 종류 확인과 lookup 실패 구분 |
| `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua` | 실제 한 행 한 줄 배치와 fit 실패 기록 |
| `Iris/_docs/authority/tooltip_t1/s2_supply_contract.json` | 새 입력·상태와 후보 역할 범위 명시 |
| `Iris/_docs/authority/tooltip_static_data_projection/projection_manifest.schema.json` | 후보 acquisition/interaction 역할 표현 |
| `Iris/tooling/tests/test_tooltip_t2_projection.py` | 기존 통합 node에 원문·상태·역할·후보 회귀 반영 |
| `Iris/test/lua/tooltip_static_data_runtime_harness.lua` | 세 종류 조회·선택, 물리 줄 수·배치·fit 실패 기대 반영 |

계획·B 문제 정의·closeout을 갱신했고, 이후 사용자 요청으로 `DECISIONS.md`, `ROADMAP.md`, `ARCHITECTURE.md`를 B complete 상태에 맞췄다. 이전 partial/implemented_only는 당시 이력으로 구분하고 새 corpus 소비 구조 및 남은 책임을 반영했다.

## 6. 검증과 실패 수정

자동 테스트는 구현 마지막에 계획의 기존 node로 묶었다. T2 projection도 수정했으므로 첫 호출에는 `test_s2_supply_and_owner_integration`과 기존 `test_projection`을 포함했다.

첫 결과는 **exit 1, 1 failed/1 passed, 7.20초**였다. 일부 정상 segment는 선택적 `qualifier_dispositions`를 생략하지만 adapter가 필수로 요구한 것이 원인이었다. 기존 corpus/reader 계약에 맞게 생략을 허용하고, 필드가 있으면 보존·형식을 확인하도록 수정했다. Corpus를 바꾸거나 검사를 무시해서 통과시키지 않았다. `test_projection` node는 이 호출에서 통과했지만 호출 전체를 PASS로 기록하지 않는다.

실패한 통합 범위만 다음 명령으로 재실행했다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration --basetemp .\.tmp\tooltip\accept -q -s
```

결과는 **exit 0, 1 passed, 98.49초**였다. 이후 projection 코드는 바뀌지 않았으므로 통과한 node를 추가 confidence 목적으로 반복하지 않았다.

같은 통합 실행에서 Lua syntax 명령 `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`, 실제 runtime harness의 supply mode, 격리 후보의 `package_iris.ps1 -Zip`도 각각 exit 0이었다. 원문·locale·상태·손상 거부, owner 역할, 세 종류 후보, opening/Alt 수명, 네 줄 배치, fit 실패, 설치/중단 복구/rollback 및 package member 일치를 확인했다. 정확한 자식 인자는 기존 closeout에 보존했다.

자식 명령에는 240초 timeout을 두고 실행 상태·출력·산출물 진행을 확인했다. 비정상 장기 실행이나 강제 중단은 없었다. 별도 full Run A/B/comparator, composition 재검증, 외부 reviewer, 새 validator·seal·proof 체계는 추가하지 않았다. 문서 갱신과 사용자 수락 때문에 검사를 재실행하지도 않았다.

## 7. 동일 후보 인계와 사용자 수락

통합 실행의 패키지를 `.tmp/tooltip/preview/Iris.zip`으로 복사해 인계했다. 원본 후보·설치·패키지는 `.tmp/tooltip/accept/test_s2_supply_and_owner_integ0`에 있으며, 기존 `.tmp/tooltip/package`의 r6 ZIP은 보존했다.

| 식별 항목 | 값 |
| --- | --- |
| ZIP 크기 | 1,039,213 bytes |
| ZIP SHA-256 | `33b5927127442b16dca917c6f49f3e661743123c0cbd3d5890d47cb6fca96860` |
| Product ID | `ttp-5a90c7d3844be93670e1b0f6c9f30db41bc0d17a026caf6f70bb797789ebc163` |

코드·자동 검사·후보 준비만 끝났을 때는 implemented_only로 보고했다. 이후 사용자가 실제 확인 항목을 모두 통과했다고 보고하고 B 통과를 명시했다. 이 보고에 따라 **B1 공급·소유권, B2 실제 표시, B3 인계·범위를 complete**로 수락했다. 감독 작업에 결과를 보고했으며 최종 수락은 기존 closeout에 반영됐다.

실제 PZ 확인은 사용자 보고에 근거하며 에이전트가 직접 화면을 관찰한 것은 아니다. 게임 버전·해상도·UI 배율의 상세 수치는 제공되지 않았으므로 추정하지 않는다. 가상 폰트 harness를 게임 관찰로 대체하거나 모든 표시 환경을 보장했다고 기록하지 않는다.

## 8. C 인계와 남은 후속 작업

C는 같은 `description_composition_results.read_result(root)`의 `items[].locales[ko/en].expanded`를 소비하면 된다. Compact의 `detail_links[].segment`는 같은 locale의 expanded segment를 가리키며 fact refs, qualifiers, relations와 unresolved를 함께 유지한다. B의 embedded 공급 subject는 C의 새로운 의미 authority가 아니다.

사용자는 설명을 추후 다시 교정할 필요가 있어 보인다고 했고 구체 사항은 나중에 전달하기로 했다. 이는 B 완료와 분리한 후속 표현 개선 과제다. 현재의 추가 문장 수정·재생성 지시나 모든 설명의 영구적 품질 수락으로 해석하지 않는다.

C 구현, C 준비 이후의 current 공동 활성화, 일반 strict production finalization, release는 이번 완료 범위에 포함하지 않는다. 추후 실제 overflow·누락·가독성·S4 문제가 보고되면 해당 원인으로 재개한다. 이 Walkthrough 작성 자체는 추가 검증·설치·배포를 수행하거나 승인하지 않는다.

## 관련 문서

- [구현 계획](iris_dvf_tooltip_s2_supply_ownership_recovery_plan.md)
- [B 문제 정의](iris_dvf_tooltip_ownership_recovery_problem.md)
- [실행 결과와 최종 수락](iris_tooltip_supply_closeout.md)
- [DECISIONS](DECISIONS.md)
- [ROADMAP](ROADMAP.md)
- [ARCHITECTURE](ARCHITECTURE.md)
