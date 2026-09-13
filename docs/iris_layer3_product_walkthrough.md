# Iris Layer 3 제품 생성·소비 Walkthrough

> 날짜: 2026-09-07  
> 상태: **complete**  
> 범위: DVF-L3-06 — 채택된 Layer 3 설명의 Menu·Alt Tooltip 제품 통합

## 1. 구현 결과

채택된 Layer 3 설명을 Iris 메뉴의 KO/EN 상세 본문과 Alt Tooltip의 S2에 연결했다. Menu, Tooltip base, Recipe companion을 하나의 immutable product로 생성하고, Lua 조회·표시 코드와 패키징·설치 경로가 같은 product를 소비하도록 구현했다.

설명의 사실 선택·표현은 기존 authority가 담당한다. 이번 제품 계층은 완성된 표현을 연결하고 보존한다. Iris runtime은 Lua로 유지하며, 표시 중 사실을 추론하거나 번역·요약하지 않는다.

| 구성 | 최종 통합 범위 |
|---|---|
| Menu | Exact FullType 2,105개, KO/EN expanded block과 본문 |
| 설명 사실 | 5,290개 facts, 10,580개 fact-locale 대응 |
| 획득 정보 | 1,057개 acquisition facts를 상세 본문에 보존 |
| Alt Tooltip | Support 2,280개, S2 교체와 기존 S1/S3/S4 보존 |
| Recipe companion | 349개 item, 781개 표시 variant |
| 생성 Lua | Menu chunk 11개와 Index·Descriptor·Tooltip·Recipe 4개 |

## 2. 입력에서 화면까지

```text
채택된 layer3_expression + 기존 Tooltip/Recipe owner 입력
                         |
                 product_projection
                         |
          하나의 product ID와 product_manifest.json
                         |
       Menu KO/EN chunks + Tooltip base + Recipe companion
                         |
                product_install.stage
                         |
          Lua facade / lookup / renderer + package
                         |
            Menu 상세 본문 / Alt Tooltip 표시
```

설명 입력은 `Iris/_docs/authority/dvf/layer3_expression/manifest.json`이다. 이번 결과가 사용한 SHA-256은 `cff8acd83715e70c6e7b82553d47e538c7f75131437491d7cf6781875f5435be`다.

`product_projection.build_product()`는 adopted loader로 입력을 읽고 다음 순서로 제품을 만든다.

1. 기존 owner 입력과 보호할 제품 입력의 identity를 수집한다.
2. Menu의 locale별 expanded block·순서·원문·fact/dependency reference를 보존한다. 본문은 block text를 줄바꿈으로 연결한다.
3. Tooltip의 구조화된 slot에서 S2를 교체하고 S1/S3/S4를 유지한다.
4. 완성된 Tooltip base를 입력으로 Recipe companion을 생성한다. 기존 Recipe 선택 대상과 variant identity를 보존한다.
5. 입력 owner, producer bytes, schema/contract와 논리 payload digest로 product ID를 계산한다.
6. Product ID가 결속된 Lua member와 각 member의 hash를 담은 manifest를 기록한다. 생성 전후 입력 drift도 확인한다.

FullType은 정렬하여 최대 200개씩 chunk에 넣는다. Index는 각 chunk의 FullType 범위·개수·hash·module을 제공하고, Descriptor는 같은 product에 속한 Index·Tooltip·Recipe·chunk module을 연결한다.

## 3. 코드별 책임

아래 경로는 저장소 루트 기준이다.

| 코드 | 책임 |
|---|---|
| `Iris/tooling/src/iris_tooling/domains/layer3/product_projection.py` | Adopted expression admission, Menu/Tooltip/Recipe 투영, product identity와 immutable payload 생성 |
| `Iris/tooling/src/iris_tooling/domains/layer3/product_install.py` | Candidate admission, 격리 source staging, facade 연결, guarded promotion과 복구 |
| `Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua` | Product Index·chunk를 통한 Layer 3 조회 |
| `Iris/media/lua/client/Iris/Data/IrisLayer3EnglishLookup.lua` | 같은 product의 EN payload 조회 |
| `Iris/media/lua/client/Iris/Data/layer3_renderer.lua` | Product 본문을 기존 Menu 소비 경로에 연결 |
| `Iris/tools/Layer3PackageProjection.psm1` | Product descriptor와 package member 구성 확인 |
| `Iris/tools/RuntimeLookupIndexIdentity.psm1` | Runtime lookup identity와 source/package 대응 확인 |
| `Iris/tools/package_iris.ps1` | 선택된 generation·facade를 package와 ZIP에 반영 |

기존 public lookup과 Menu/Alt 진입점을 유지했다. Product component를 읽을 수 없거나 identity가 맞지 않으면 이전 본문이나 stale global을 섞어 표시하지 않는다. 빈 상세 본문과 없는 S2 slot도 입력 상태대로 처리한다.

Tooltip의 최대 4개 logical slot과 화면 줄바꿈 처리를 구분한다. Recipe는 생성된 variant 중 하나를 opening 때 선택하고 열린 동안 유지한다. Locale 변경은 같은 Recipe identity의 언어별 배열을 사용하며, Alt 해제·item 전환 등 기존 opening 종료 동작을 보존한다.

## 4. 설치·패키징과 전환 구현

`product_install.admit()`는 candidate의 manifest와 member bytes를 확인한다. `stage()`는 격리된 source에 product payload와 안정된 facade를 연결하여 패키징 가능한 입력을 만든다.

패키징은 선택된 product의 descriptor와 정확한 member 집합을 기준으로 동작한다. Source, package, install과 실제 ZIP 사이의 payload 및 lookup 대응을 확인하고, 선택되지 않은 generation이나 legacy payload를 함께 넣지 않는다.

`promote()`는 준비된 source bytes를 소비하며 내부에서 다시 build하거나 package하지 않는다. Expected predecessor와 입력 identity를 확인하고, writer lock과 transaction journal을 사용해 전환한다. Product pointer를 마지막에 기록하며 실패하면 `recover()`가 이전 파일과 pointer를 복구한다. 이미 같은 제품이 설치된 경우의 no-op도 구현했다.

전환·복구 경로의 구현과 전달 product는 구분해서 읽는다. 세션 종료 시 저장소의 `IrisLayer3DataCurrent.lua`는 `dvf33-ed92fa5c9ed4a1ed367f5d79365d04e1996e36a05d76a33bd7b8dd2176e7f82f`를 가리켰고, `IrisLayer3ProductCurrent.lua`는 없었다. 아래 산출물은 별도로 완성한 product의 전달 위치다.

## 5. 통합 과정에서 해결한 문제

- **Windows 경로 길이:** 동일 contract의 실행 결과 아래에 `product/a`, `source`, `package`, `install` 등 짧고 얕은 경로를 사용했다. 검사마다 별도 작업 공간을 늘리지 않고 공통 생성 결과를 공유했다.
- **Checkout EOL과 raw identity:** 기존 입력에 결속된 raw bytes가 checkout 변환으로 달라지지 않도록 `.gitattributes`를 필요한 경로에 한정해 보완했다. 입력 hash나 의미 기준을 임의로 바꾸지 않았다.
- **정규 검사 등록:** 제품 통합 test를 기존 repository gate에 등록했다. 기존 dedicated contract에 속한 검사와 normal pytest 수집의 경계를 정리했다.
- **PowerShell collection 형태:** Runtime lookup identity에서 pipeline 반환값을 명시적인 ordinal HashSet으로 구성해 집합 비교가 올바른 형식으로 실행되도록 수정했다.
- **Module import:** 중첩 module import의 `-Force`로 호출자에게 필요한 export가 사라지는 문제를 수정했다.
- **공통 package 검사 호출:** Predecessor와 product 경로가 공통 lookup 검사 진입점을 사용하도록 정리했다.

선행 Layer 2 input identity 조정 결과를 제품 통합의 prerequisite로 소비했다. 해당 선행 작업의 완료와 이번 제품 검증 결과는 별도의 결과로 유지한다.

## 6. 완료된 검증

최종 검증은 기존 canonical repository gate에서 실행했다. 실행 중 프로세스와 진행 상태를 주기적으로 확인했으며, 최종 실행은 정상 종료했다.

| 항목 | 실행 결과 |
|---|---|
| Machine subject | `3fa4f42642a32d40bdc6690c686e493ad40376e4` |
| Canonical launcher / native process | Exit `0` |
| Repository test 결과 | **214 passed, 118 subtests passed**, 232.08초 |
| 최종 package Lua syntax | Exit `0`, **125 files** |

제품 통합 검사의 정규 source는 `Iris/build/description/v2/tests/test_layer3_product_integration.py`다. 같은 contract 안에서 결정적 생성, 전체 Menu/Tooltip/Recipe 집합·본문·slot 보존, source/package/install/ZIP 대응, 잘못된 입력 거부와 전환·복구·no-op를 확인했다.

`Iris/test/lua/tooltip_static_data_runtime_harness.lua`의 product 경로는 실제 Lua lookup→renderer→FactReader→Detail/formatter 소비를 실행했다. 전체 target 조회, KO/EN, Tooltip과 Recipe variant, Alt opening 수명 및 stale 데이터 처리를 포함했다. 전환 중단과 복구는 합성 fixture에서 검증했다.

검사 등록은 `Iris/validation/execution/required_validations.json`, `contracts/repository_test_gate.json`과 기존 pytest source classification에 반영했다. 별도의 임시 검사기를 정규 authority로 추가하지 않았다. 이 Walkthrough 작성에서는 테스트를 재실행하지 않았다.

## 7. 전달 산출물

아래는 이번 세션에서 완성·전달한 산출물의 기록이다.

| 산출물 | 경로 |
|---|---|
| Candidate | `C:/Users/MW/Downloads/coding/iv/r5/test-output/product/a` |
| Canonical source/package/install | `C:/Users/MW/Downloads/coding/iv/r5/test-output/product/` 아래 `source`, `package`, `install` |
| 전달 ZIP | `C:/Users/MW/Downloads/coding/iris-validation/playtest/Iris.zip` |
| 전달 설치 폴더 | `C:/Users/MW/Downloads/coding/iris-validation/playtest/Iris` |
| Canonical 결과 | `C:/Users/MW/Downloads/coding/iv/r5/canonical_full_result.json` |

- Product ID: `l3p-4e05fc9f92da124221e3ba17469cb9562fd0f895a5fa871969101ce049818124`
- Product manifest SHA-256: `7bd4aca557be8eb0c355a1d3c7a41ee5669d8f41b69498c4cc6d6e72fc2e84d7`
- ZIP SHA-256: `53305465044e577376674db7af5c0b224d5d2101bdcdf2625b4713a4b2a4de9f`

최종 검증 뒤 같은 ZIP과 설치본을 재빌드 없이 전달했다. 이후 다른 입력이나 코드로 만든 결과에는 새 product identity가 부여된다.

## 8. 문서 반영

- [DECISIONS.md](DECISIONS.md): DVF-L3-06을 **complete**로 기록하고 제품 생성·소비 책임과 최종 검증 결과를 반영했다.
- [ARCHITECTURE.md](ARCHITECTURE.md): 단일 product 생성, Lua 조회·표시, package/install과 전환·복구 구조를 설명했다.
- [ROADMAP.md](ROADMAP.md): 제품 통합을 Done으로 옮기고 완료 체크를 반영했다.

후속 작업은 이 제품 생성·소비 경로와 기존 의미·표현 owner의 책임을 기준으로 진행한다. 이 문서는 구현을 따라가기 위한 설명이며 새로운 검증 gate나 validation authority를 정의하지 않는다.

## Tooltip owner successor 구현 (2026-09-09)

위 L3-06 unified product 결과는 historical 범위로 유지한다. B에서는 DVF를 승인 S2 공급자로 제한하고 기존 Tooltip T1/T2·Recipe projection과 Tooltip 전용 install/package binding을 연결했다. 활성화된 Tooltip owner가 있을 때 historical unified installer가 current Tooltip을 덮어쓰는 재진입은 차단한다. 이 구현은 현재 격리 fixture에서만 검증됐고 실제 current를 전환하지 않았다. 실제 strict admission/finalization과 PZ가 남은 partial 상태 및 동일 r6를 받을 C의 인계는 [Tooltip 공급 결과](iris_tooltip_supply_closeout.md)를 따른다.

2026-09-10 후속: 위 fixture 단계 이후 실제 `tooltip_t1/s2_candidate.py` → T2 `--s2-candidate` → Tooltip Recipe/install/package 경로를 실행했다. 후보는 기존 채택 baseline에서 S2만 교체하고 미커밋 소스의 실제 bytes를 결속한다. 통합 검사 exit 0, 8 passed로 인게임용 패키지를 준비했으며 상태는 implemented_only/PZ 대기다. 원래 L3-06/D6 완료 기록이나 current는 변경하지 않았다.

## 2026-09-11 — canonical expanded Menu 후보 경로

위 DVF-L3-06 기록은 historical unified product다. C 후보는 `product_projection.build_menu_product()`가 `description_composition_results.read_result()`와 `composition_results.read_result()`를 통해 고정 descriptions/blocks를 읽는다. 기존 `build_product()`의 expression/B writer를 새 corpus용으로 재해석하지 않는다.

C 내부 schema는 `iris-layer3-product-v2`, 표시 payload는 `iris_expanded_display_v1`이다. 후보의 ProductCurrent → Descriptor → DataCurrent compatibility → Index → chunks가 같은 product ID를 선택한다. source current는 전환하지 않는다. Tooltip은 동일 description SHA를 가진 수락 ZIP의 독립 owner와 Lua bytes를 사용한다.

표시 단위는 source segment를 자르거나 복제하지 않는 연속 구간이다. block/branch/fact/qualifier/relation 참조가 경계를 가로지르면 구간을 분리하지 않는다. `separate_block_refs` 안에서 참조가 걸치지 않는 경계만 간격으로 구별한다. shared refs는 의미 동일성의 판정이 아니라 보수적인 연속 표시 제약이다. 원문은 각 segment 그대로 유지하고, 불명확한 관계에 새 제목·접기를 부여하지 않는다. `Base.Plank`의 선행 조건과 후속 설명, `Base.Lipstick`의 공통 접근 조건은 연속 단위로 유지한다. composition owner/corpus는 변경하지 않았다.

전체 source item과 refs·qualifier scope·relations·unresolved·compact detail links는 기존 product manifest의 offline trace에 보존한다. Lua에는 text, state/reason, ordered units와 1-based first/last segment만 보낸다. offline link의 0-based segment와 runtime destination을 명시적으로 대응한다. C는 compact 부재로 expanded를 숨기지 않는다.

`layer3_renderer.getDisplay()` → Detail assembler → `IrisWikiSections.getLayer3Units()`를 Browser Detail과 WikiPanel이 공통 소비한다. 기존 문자열 API와 full-table `IrisLayer3DataChunks`/`IrisLayer3Data` facade는 유지한다. normal absent와 payload fault를 모델에서 구분하며, product 실패 때 다른 locale·generation·stale global로 돌아가지 않는다. 줄바꿈과 높이는 기존 TextLayout과 두 consumer가 계산한다. Browser의 item/locale 변경은 scroll을 초기화한다.

B 세 artifact와 변경 없는 retained media는 stage와 actual ZIP에서 accepted bytes와 비교한다. C가 변경하는 공유 파일은 `MENU_RUNTIME`의 여섯 파일이며 product identity의 `shared_changes`에 before/after hash를 기록한다. product descriptor의 C/B corpus binding과 패키저의 owner/hash/lock 검사를 유지한다. 후보 복원은 기존 recover journal을 사용하는 `restore_candidate()`로 한정하고 live `promote()`의 Tooltip owner guard는 유지한다.

현재 required node는 `Iris/validation/execution/required_validations.json`의 `test_layer3_product_integration.test_product_contract`다. historical `_docs/round3/current_route_required_validations.json` → 중간 `validation/current_route/required_validations.json` → 현재 `validation/execution/required_validations.json` 순서의 locator 변경이며 membership를 새로 추가하거나 축소하지 않는다. 실제 후보 identity·자동 검사·PZ 관찰 상태는 [C 실행 결과](iris_dvf_expanded_menu_structuring_common_candidate_recovery_closeout.md)를 따른다.

## 2026-09-12 player-use successor — implemented_only

공통 공개 용도 계획, 기존 source owner의 제한적 보완, 2,105개 KO/EN compact/expanded 전수 자체 검토와 동일 corpus 새 B→C 후보 연결을 완료했다. 설명은 각 표면 1,981 present / 124 absent이며 근거 부족은 별도 기록했다. 기존 블록 검사 결과와 수정 후 설명/B/C 자동 검사를 사용했다. 실제 PZ 표시 관찰은 unvalidated_but_in_scope이며 live/current·release는 전환하지 않았다. 최종 공통 후보는 `.tmp/menu/run-7ztpp37i/p/Iris.zip` (SHA256 `db2174e72e5acc50db8651c538343e6adc432950015d04d44b4da5c7145a9796`)이다. 정확한 명령/실패·수정/입력·B owner와 남은 관찰 범위는 [전환 결과](iris_dvf_use_description_report.md)의 마지막 closeout을 따른다. 과거 수락 기록은 역사적 subject로 유지한다.

## 2026-09-12 의미 판정 재개 — partial

후속 실제 원문 검토에서 공통 점화 frame의 내부 지원 문구, 도구 설명의 수행 요건 나열, 음식 미끼의 추상적 주어, 차량 부품 목적의 미확정 문제가 확인되었다. 위 ‘잔여 표현 결함 0 / 실제 PZ만 남음’ 판단을 철회한다. ledger의 읽기 이력과 자동 검사 결과는 보존하지만 의미 적합성 수락으로 사용하지 않는다. 기존 ffde6886... corpus와 run-7ztpp37i C ZIP은 당시 자동 검사 통과 후보이며 의미 품질 승인 후보가 아니다. 공통 규칙과 같은 의미/조합 범위를 교정하고 재판정할 때까지 partial이다.

## 2026-09-12 공통 목적군 교정 후 후보

재개 시 확인된 점화 주체·음식 미끼·복합 도구 목적군·중복 수행 요건을 공통 규칙으로 교정하고 실제 영향 범위를 재판정했다. 42개 차량 부품의 구체 기능 부족은 개별 purpose_unresolved로 기록한다. 포괄적인 결함 0 선언을 복원하거나 자동 검사 성공을 의미 품질 승인으로 사용하지 않는다. 누적 전수 자체 읽기/변경 범위 재판정의 상세와 한계는 `iris_dvf_use_description_report.md`의 최신 절 및 `review/uses/items.json`에 있다.

현재는 **implemented_only**: corpus `2301a4a4b8d24a28447ea53e3e47dd7143b362fb9e3b3b2531cf3152e4491e30`, B `.tmp/tooltip/run-cr4yy73j/s/.tmp/package/Iris.zip`, C `.tmp/menu/run-5b363prk/p/Iris.zip`(SHA256 `a55538e4cdaf47c771258a2c75d33dce0f93ba66cc524eb465873d1fa0086080`). 마지막 설명/B 묶음 exit 0(2 passed, 91.80s), 같은 B를 받은 C exit 0(1 passed, 72.08s). 실제 PZ는 미관찰이고 complete/독립 품질 승인/live 전환이 아니다. 과거 ffde 후보는 역사적 자동 검사 결과로만 남긴다.
