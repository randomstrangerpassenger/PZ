# Iris Tooltip S2 공급·소유권 구현 결과

2026-09-09. 실행 계획: [S2 공급·소유권 복구 계획](iris_dvf_tooltip_s2_supply_ownership_recovery_plan.md).

## 최종 수락 — 2026-09-11 사용자 PZ 확인 / B complete

사용자가 인계된 후보의 실제 게임 확인 항목을 “다 확인했고 통과야”라고 보고하고 “문제 B를 통과처리하자”고 명시했다. 기존 자동 공급·통합 검사와 사용자 실제 관찰을 근거로 B1~B3, 즉 **B 후보 구현·통합 및 실제 표시 범위를 complete**로 수락한다. 아래 implemented_only/PZ 대기는 확인 전 이력이다.

인계 대상은 .tmp/tooltip/preview/Iris.zip (SHA-256 33b5927127442b16dca917c6f49f3e661743123c0cbd3d5890d47cb6fca96860), product ttp-5a90c7d3844be93670e1b0f6c9f30db41bc0d17a026caf6f70bb797789ebc163, corpus ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0다. 근거는 사용자의 확인 보고이며 감독자가 직접 게임을 관찰한 것은 아니다. 별도 게임 버전·해상도·배율 수치는 제공되지 않았으므로 추정하지 않으며 모든 환경의 표시 보장으로 확대하지 않는다.

사용자는 향후 설명 교정이 더 필요해 보인다고 했으며 구체 사항은 나중에 전달하기로 했다. 이는 B 통과와 분리한 후속 표현 개선 과제다. 현재 문장 교정·재생성·추가 테스트 지시로 해석하지 않는다. 모든 설명의 향후 품질까지 완전하다고 수락한 것도 아니다.

이번에는 완료 상태와 기록만 갱신했다. C 구현, 저장소 current 공동 활성화, 일반 strict production finalization, 배포/release는 수행하거나 완료로 간주하지 않는다. 기존 실패·재실행 이력은 유지한다.

## 구현 당시 기록 — 2026-09-11 v3 / implemented_only

v3 계획의 코드·후보 통합과 자동 검증을 완료했다. **실제 PZ 관찰은 없으므로 B2 실제 표시 및 B 전체 complete는 아니다.** 아래 9월 9~10일 r6 결과·외부 실행 제안은 이력이며 새 입력의 성공 근거나 외부 접근 허가로 승계하지 않는다. 현재 Tooltip/Menu 데이터·current pointer는 전환하지 않았고 C와 공동 활성화, 일반 strict production finalization, release는 별도 범위다.

### 구현 결과

- B1: `description_composition_results.read_result`가 읽는 검수 corpus의 compact를 그대로 공급한다. `descriptions.json` SHA-256은 `ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0`, `blocks.json`은 `b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796`이다. 재생성/문장 수정은 없었다. 공급 schema v2는 present/absent/out_of_dvf_target을 구분하고 state/reason, segment refs, detail links, 존재하는 qualifier dispositions, expanded, qualifiers/relations/unresolved를 offline subject에 보존한다. 런타임으로는 표시와 선택에 필요한 자료만 보낸다.
- 실제 owner/admission 조정 결과 T=2,280, D=2,105, T∩D=2,105, T-D=175, D-T=0이다. 각 locale compact present 1,984, absent 121; 대상 밖 175개는 기존 owner absence로 확인했다. 예전 r6의 scoped/gap 상태로 재분류하거나 fallback하지 않는다. 저장소 밖 locator는 읽기 전에 거부한다.
- S1은 admitted classification 원문 그대로다. 기존 T1은 S3/S4 모두 L4였으므로 후보 v2에서 S3를 acquisition place, S4를 하나의 interaction으로 명시적으로 재매핑했다. 일반 strict/historical 매핑은 유지한다. S3는 기존 acquisition facts의 채집 zone 교집합·덫 zone·낚시 물가를 장소 행으로 표시한다(현재 1,016개). 장소 표현을 만들 수 없는 획득 경로는 S3 부재이며 expanded의 절차를 복사하거나 L4로 채우지 않는다.
- S4는 기존 QG owner의 유효 recipe/rightclick과 Menu가 소비하는 EvolvedRecipe owner를 한 목록으로 연결한다. 현재 후보 수는 레시피 781, 우클릭 86, 자유 조리 2,203이다. 각각 종류 label을 붙이고 한 번에 하나만 표시한다. 고정 종류 순환/가중치를 추가하지 않았다. 기존 승인된 레시피 이름 부재 예외만 유지하고 새 locale 누락·지원하지 않는 source·손상은 거부한다. 원래 이름의 `s2-candidate` CLI와 `IrisTooltipRecipeVariants.lua`를 호환 경로로 재사용하지만 그 이름으로 S3/S4 변경을 숨기지 않는다.
- renderer는 360px 제한과 다중 wrap을 제거했다. 게임 폰트의 원문 폭에 맞춰 패널을 넓히고 화면 안에서 옆/아래/위로 배치한다. 정상 글꼴, 원문 한 행당 한 화면 줄, Alt 및 opening 수명을 유지한다. 물리적으로 fit하지 않으면 `opening.displayStatus=fit_failed`와 원인/화면 정보를 남기고 로그로 알린다. **이 상태는 정상 부재나 표시 성공이 아니며 실제 관찰에서 나오면 해결해야 할 표시 결함이다.** 말줄임·clipping·글꼴 축소·일부 행 생략으로 통과시키지 않는다.

### 최종 자동 검증

첫 최종 묶음은 계획의 integration node와 실제 변경한 projection의 기존 `test_projection`이었다. 결과는 exit 1, 1 failed/1 passed(7.20초): integration에서 일부 정상 compact segment의 선택적 `qualifier_dispositions`를 필수로 요구한 adapter 결함이 발견됐다. 기존 corpus/reader 계약에 맞게 고쳤다. 같은 호출의 `test_projection` node는 통과했지만 그 호출 전체를 PASS로 기록하지 않는다.

수정 후 실패한 통합 범위만 아래 명령으로 재실행했다. **exit 0, 1 passed, 98.49초**였다. projection 코드는 이후 바뀌지 않아 통과한 node를 confidence 목적으로 반복하지 않았다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration --basetemp .\.tmp\tooltip\accept -q -s
```

같은 통합 실행에서 다음 실제 자식 명령이 모두 exit 0이었다. `$s`는 `.tmp/tooltip/accept/test_s2_supply_and_owner_integ0/s`다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
lua .\Iris\test\lua\tooltip_static_data_runtime_harness.lua $s supply .\.tmp\tooltip\accept\test_s2_supply_and_owner_integ0\expected.lua
powershell -NoProfile -ExecutionPolicy Bypass -File "$s/Iris/tools/package_iris.ps1" -OutputRoot "$s/.tmp/package" -Zip
```

같은 후보의 정확한 원문/locale/state/error, S1 보존과 S3/S4 owner 매핑, 세 종류 후보의 Lua 조회·단일 선택, opening/locale/Alt 수명, 네 화면 줄과 fit 실패, 설치/중단 복구/rollback/package member 일치를 검사했다. 자식 실행은 240초 timeout이며 실행 상태와 산출물 진행을 확인했다. 비정상 장기 실행이나 중단은 없었다. 최초 실패 수정 외 중간 테스트, full Run A/B/comparator, composition 재검증, 새 proof/validator/receipt 체계는 추가하지 않았다.

### 동일 후보와 C 인계

게임 관찰용 ZIP은 `.tmp/tooltip/preview/Iris.zip`이다. 위 통합 검사가 만든 `$s/.tmp/package/Iris.zip`을 그대로 복사했으며 기존 `.tmp/tooltip/package`의 r6 ZIP은 보존했다.

- ZIP: 1,039,213 bytes / SHA-256 `33b5927127442b16dca917c6f49f3e661743123c0cbd3d5890d47cb6fca96860`.
- Product: `ttp-5a90c7d3844be93670e1b0f6c9f30db41bc0d17a026caf6f70bb797789ebc163`.
- Supply: `7dbe477e0904fc1fa0df5786c7ebc5eb9976db691918f8b0987ab80e8bd6bbc1`.
- 원본 후보/설치/패키지: `.tmp/tooltip/accept/test_s2_supply_and_owner_integ0`의 기존 h/t/c/s 산출물. 시작 bytes는 `.tmp/tooltip/before`에 보존했다. source dirty 상태를 clean으로 바꾸거나 원본 commit/reset/clean하지 않았다.

C는 같은 `description_composition_results.read_result(root)`의 `items[].locales[ko/en].expanded`를 읽고 compact의 `detail_links[].segment`/fact refs, qualifiers·relations·unresolved를 함께 사용하면 된다. B embedded subject는 추적용 공급 자료이며 C의 새 의미 authority가 아니다. C가 같은 corpus를 소비할 준비가 되기 전 실제 사용자 current의 공동 활성화는 수행하지 않는다.

실제 확인은 이 ZIP 하나로 KO/EN에서 Alt 활성/해제, S2 한 화면 줄과 최대 네 화면 줄, S1/S3 역할, 레시피/우클릭/자유 조리 표시 및 읽는 동안의 선택 유지, 긴 복합 문장·짧은 문장·compact 부재·후보 부재·화면 가장자리의 잘림/겹침/가독성을 관찰해야 한다. 반복 개방 시 같은 후보가 나오는 것은 허용된다. 게임 버전·실제 해상도·UI 배율·폰트는 관찰 기록과 함께 남겨야 하며 현재는 미확보다. B41 QG 입력을 사용한 사실이나 가상 폰트 harness의 1920/900/640/300 폭 사례가 실제 PZ 지원 환경의 표시 완료를 뜻하지 않는다. 실게임 fit failure가 발견되면 renderer 또는 해당 표현 owner로 환류하고 두 소비자의 동일 corpus를 유지한다.

B3의 동일 입력/후보 인계는 준비됐고 B1 공급·owner 통합은 자동 확인됐다. B2는 자동 표시 계약만 확인했으며 실제 PZ 관찰 대기다. 최종 상태는 **implemented_only**다.

---

## 이전 상태 — 2026-09-10 r6 인게임 검증 대기

**B는 implemented_only이며 인게임 검증을 기다린다.** 아래 2026-09-09의 fixture/외부 환경 blocked 기록 이후, 사용자가 B 규모에 맞는 검증 경로 조정을 승인했다. 실제 S2 전용 후보 생산과 필요한 자동 검증·격리 설치·패키징을 완료했다. 계획 §12의 완료 조건은 바꾸지 않았으므로 PZ 결과 전에는 B complete가 아니다. current Tooltip/Menu는 predecessor, promotion은 deferred이며 C는 미완료다.

인게임 확인용 파일은 저장소 `.tmp/tooltip/package/Iris.zip`이다(1,020,172 bytes, SHA-256 `e5a48c6e635fba5cc99f207959d13c1f0492b1786d1871b867aedf148e086902`). 같은 폴더의 `Iris/`는 압축 전 패키지이며 나머지 두 JSON은 기존 package 도구의 출력이다. 검증된 패키지를 그대로 복사했으며 새 proof/receipt 파일은 추가하지 않았다. 원본의 Git 상태·current·게임 설치에는 손대지 않았다.

실제 product ID는 `ttp-0d11de526ddf333c7c7bf67016e9c0018cd89a1321647de756a33ae2bb37c03d`다. Static SHA-256 `6ecf00b21d9c077b697bb2a667aad5c75cc1dc1ce783bd7855ee30b7e8740ce0`, Recipe SHA-256 `f5504aa5a028d0ecb7da7c463511964df618b67ccc154062acb6a5f16113e529`. 공급 SHA-256은 `122e061d143a2a9f251fe99f4f21612095516c5c2bb884a94974e2cc40ca3a49`다. 출력 문장은 앞선 fixture와 같지만 이번 후보는 아래 실제 생산 경로와 최종 producer bytes에 귀속된다.

### 검증 경로의 적용 범위

`tooltip_t1/s2_candidate.py`는 새로운 validator가 아니라 기존 T1의 **S2-only candidate producer/admission**이다. hash-bound 채택 baseline을 읽고 그 S1/S3/S4 identity·surface·부재를 보존한다. baseline의 T2 projection과 현재 predecessor static table도 대조한다. S2는 정상 adopted reader/supplier와 기존 `_slot_supplied_s2`가 제공하고, 기존 `build_handoff_row`/`validate_handoff_row`/`validate_supply_rows`로 strict 행·locale·identity·support·정상 부재를 확인한다. T2는 기존 `project`/serializer, Recipe와 설치는 기존 Tooltip 소유 경로를 그대로 사용한다.

후보의 기존 `subject_binding.json`에는 실제 input/producer/runtime/package source SHA-256, 미커밋 여부를 숨기지 않은 Git 상태, 채택 baseline binding, durable S2 공급을 함께 기록한다. T2의 explicit `--s2-candidate --candidate-receipt-sha256`는 이 후보만 소비한다. receipt/member/source drift, 다른 슬롯 변경, 대상 밖 변경은 거부한다. 별도 clean checkout이나 원본 commit, 외부 출력 위치가 필요하지 않도록 이 후보 경로의 작업 위치는 `.tmp/tooltip` 하위로 제한했다. 원래 D6와 일반 T1/T2의 clean/external/finalization 요구는 그대로다.

이번 실행에서 D6 admission 또는 canonical receipt를 합성하지 않았고, 일반 T1/T2의 formal complete/adoption을 주장하지 않는다. 채택 baseline의 검증 결과를 S2 후보에 필요한 범위로 재사용하는 경로를 `s2_supply_contract.json`과 계획 §7에 명시한 것이다. 기존 전체 Run A/B+comparator는 D6 전체 재채택에 남고 B의 이 후보에는 적용하지 않는다. 아래 `C:/pzv`/36파일 overlay 준비안은 **이번 후보 경로에서는 사용하지 않는 이전 제안**이다.

### 실행 결과

아래 한 호출이 **exit 0, 8 passed in 149.58s**로 끝났다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_projection .\Iris\tooling\tests\test_tooltip_t2_cli.py::test_cli_finalization --basetemp .\.tmp\tooltip\accept -q -s
```

통합 node에서 기존 synthetic admission/final closeout과 수작업 T2 receipt를 제거하고 실제 T1 후보 두 생성과 실제 T2 `build(..., s2_candidate=True)` 두 생성을 호출했다. 공급·handoff·static·Recipe의 equality, S1/S3/S4와 T-D 보존, source/receipt 오염 거부, 설치·rollback·중단 복원, package member parity를 확인했다. 전체 2,280개의 공급 상태는 present 1,984 / scoped_non_applicable 110 / upstream_gap 11 / out_of_dvf_target 175, 최종 logical row 0~4 분포는 292/347/1410/171/60이다.

같은 후보로 Lua syntax, 실제 Tooltip Lua harness의 supply mode, 기존 `package_iris.ps1 -Zip`을 실행해 각각 exit 0이었다. 자식 명령 timeout은 240초이며 실행 중 진행 상황을 주기적으로 확인했다. 강제 중단·실패 재실행은 없었다. 함께 실행한 기존 projection/CLI finalization 검사도 성공했다. 이미 성공한 reader 및 다른 기존 focused node, A 장시간 검사, 전체 canonical Run A/B는 반복하지 않았다. 이 pytest는 기존 lifecycle 검사이며 정규 validation membership을 추가하지 않았다.

생산 입력/출력은 `.tmp/tooltip/accept/test_s2_supply_and_owner_integ0/`에 있다. h/i는 두 T1 후보, t/u는 두 T2 결과, c/d는 두 Tooltip 제품, s는 공유 격리 설치·패키지다. 최종 ZIP은 이 s에서 기존 패키저가 만든 실제 제품이며 가짜 admission을 사용하는 옛 fixture 제품이 아니다. 이 결과를 별도 환경 재현 또는 정식 current 채택 성공으로 확대하지 않는다.

### 사용자 인게임 확인과 C 인계

ZIP의 후보를 사용해 KO/EN에서 Alt OFF/ON, 아이템 전환·재개방, 긴 S2와 Recipe 선택을 확인한다. `Base.223Box`는 포장 개봉 설명, `Base.Plank`는 복합 용도와 긴 문장의 잘림/가독성을 보는 대표 사례다. 정상 S2 부재 및 대상 밖 아이템도 기존 슬롯을 유지하는지 확인한다. 게임 버전·locale·UI 배율과 실제 발견한 이상을 알려 주면 같은 후보의 PZ 결과로 기록한다. 고정 표본 수/전수 조합이나 별도 증명 자료는 요구하지 않는다.

C는 변경하지 않은 같은 r6 adoption/expression의 expanded와 shared reader를 사용한다. 새 Tooltip을 사용자 current로 전환하거나 옛 Menu와 모든 문장을 대응시키는 작업은 수행하지 않았다. 자동 결과가 성공했다는 이유로 PZ를 PASS로 기록하지 않는다.

최종 문서 갱신 후 `uv run --project .\Iris\tooling python -I -B -c ...recovery.load_adopted(Path.cwd(), ADOPTION)...`는 **exit 0**, `{"mode":"adopted","targets":2105}`였다. 변경 범위 `git diff --check`도 **exit 0**이다. 이후에는 이 결과 문장만 기록했으며 코드·제품을 변경하거나 성공한 검사를 반복하지 않았다.

## 2026-09-09 이전 단계 기록

**B 전체 상태는 partial이다.** 저장소 내 reader·supplier·T1/T2 opt-in·Tooltip 설치/패키징 코드를 구현하고 관련 fixture 검증을 완료했다. 실제 신규 strict production admission/finalization과 대표 PZ 관찰은 완료하지 못했다. Fixture에 synthetic admission/final closeout이 있으므로 이를 실제 채택된 Tooltip 후보 또는 B complete로 취급하지 않는다.

- `current Tooltip=predecessor`, `current Menu=predecessor`, `promotion=deferred`, `C=미완료`.
- 실제 production admission/finalization: `blocked`. 실제 PZ 및 production runtime ceiling: `unvalidated_but_in_scope`.
- 실제 사용자 설치·current locator·r6·L3-06 sealed evidence를 변경하지 않았다. 원본 작업 트리의 기존 수정·추가·삭제를 보존했고 commit/reset/worktree 생성은 하지 않았다. 테스트가 사용하는 저장소 내 synthetic Git fixture는 생산 subject가 아니다.
- 사용자 프롬프트의 owner 사전 승인을 적용했다. 추가 owner Gate, A 장시간 acceptance, 옛 Menu 전수 claim 조사, 새 canonical validator/receipt 체계는 만들지 않았다.

## 구현

`recovery.load_adopted`의 정상 경로는 고정 adoption/manifest/member bytes, 수락 subject, 상대 member 위치, 상태·FullType·KO/EN·표현/fact/dependency refs 및 B/C handoff를 검사한다. 현재 문서·생산 소스와의 비교 및 producer 재합성은 `load_candidate`와 `load_adopted(..., historical=True)`에 남겼다. 수락 기록의 절대 실행 위치는 역사로 보존하고 현재 checkout의 동일 repository-relative subject 소비를 허용한다. r6를 재생성하거나 승인 hash를 바꾸지 않았다.

`domains/layer3/tooltip_s2_supply.py`는 S2와 근거만 공급한다. 현재 owner 합집합을 sealed T1 handoff와 대조하고 Layer 2 validator, T1 contract validation 및 기존 Layer 3 absence validation을 사용한다. 실제 r6의 `scoped_not_applicable`을 `scoped_non_applicable`로 매핑한다. 계획의 예비 `no_first_contact` 설명을 이유로 immutable 자료를 편집하지 않았다.

T1 `--s2-supply`와 `--s2-supply-sha256`는 explicit opt-in이다. 최초 admission에서 원 입력 bytes와 현재 source를 대조한다. strict writer는 `subject_binding.json.s2_supply`에 exact canonical payload와 SHA-256을 함께 보존한다. T2는 이 durable 입력과 실제 S2 행의 expression identity/text/omission을 확인한다. 이미 수락된 handoff의 후속 소비는 현재 문서·producer를 다시 실행하지 않는다. 기존 generation 기반 D3 경로는 보존했다.

T2 build/finalize의 optional `--handoff-locator`는 finalized candidate를 current 변경 없이 읽기 위한 경계다. 외부 경로·strict handoff·Git subject·계약 bundle 검사는 그대로 적용된다. 새 공급 binding은 기존 projection manifest schema의 명시적 선택 필드이며, 기존 입력 형식은 계속 유효하다.

`domains/tooltip_static_data_projection/install.py`는 실제 T2 생성 결과에서 기존 `project_recipe_variants`와 serializer로 companion을 만든다. 두 직접 Lua table과 `IrisTooltipOwner.json`을 한 전환 단위로 취급한다. Menu current를 바꾸지 않는 격리 stage/install, source/producer drift 검사, writer lock, before bytes journal 및 rollback을 제공한다. 이 B 설치 API는 저장소 `.tmp` 내 격리 대상으로 제한되며 사용자 current 활성화는 C와의 공동 전환에 남긴다.

패키징은 Tooltip owner의 두 member hash·identity와 package parity를 검사한다. Unified predecessor가 입력인 경우 historical descriptor를 고치지 않고 그 facade hash에 연결된 Tooltip successor만 독립 owner로 허용한다. 기존 DVF `promote`는 Tooltip owner binding이 있는 current에 재진입해 덮어쓰지 못한다. Runtime의 Alt/선택/locale/wrap 정책은 바꾸지 않았다. 기존 runtime harness에 공급 후보의 exact expected rows를 사용하는 `supply` mode만 추가했다.

## 입력과 관찰 결과

실제 고정 adoption: `Iris/_docs/authority/dvf/layer3_expression/successors/r6/adoption.json`, SHA-256 `7dded22fad93b7eeff8debf56205cb9ee84220758d53ecb41396889fb49bd799`.

Manifest SHA-256 `69b5a1dab524f5d595b0739ee665238a11b971e30e6c56369afdf1a902107648`, descriptions SHA-256 `7aab01992fb4cd79ba5ca82d2d5627e55270356f0d25ea0cf249b16bd5da681d`. B/C는 같은 expression/audit member를 사용한다.

정상 loader/admission 읽기에서 T=2,280, D=2,105, T∩D=2,105, T-D=175, D-T=0을 확인했다. T는 output key로 정하지 않았다. Sealed T1 digest는 `3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6`이고 현재 owner predicate와 일치했다. 기존 owner absence와 T-D도 exact equality이며 missing/extra는 0이다.

| 공급 상태 | FullType 수 | 처리 |
|---|---:|---|
| present | 1,984 | KO/EN 승인 S2 그대로 |
| scoped_non_applicable | 110 | S2 omission |
| upstream_gap | 11 | S2 omission, residual 보존 |
| out_of_dvf_target | 175 | explicit owner absence에 따른 omission |

전체 fixture에서 S1/S3/S4 identity·문장과 T-D 전체 view equality, 실제 baseline static 및 Recipe companion 일치, Recipe 후보 identity와 새 base 연결을 확인했다. 0~4 logical rows의 before 분포는 206/455/1388/171/60, after는 292/347/1410/171/60이다. 분포는 quota가 아니다.

실제 공급 문장 예: `Base.223Box` KO는 “포장 개봉에서 재료로 쓰인다. 상자를 열어 탄약을 꺼낼 수 있다.”, EN은 “It serves as a material for package opening. The box can be opened to take out ammunition.”이다. `Base.Plank`에는 연료 대상, 제작 역할과 해당 제작법의 조건, 부목 등 여러 확인된 용도의 긴 S2가 그대로 남는다. 공급자가 줄이거나 내부 ref를 문장에 넣지 않는다. 실제 게임의 긴 문장 clipping/readability는 미관찰이다.

## 자동 검증과 한계

실행 형식은 모두 `uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml @bTestNodes --basetemp .\.tmp\tooltip\tests -q -s`였다. 첫 실행 이후 basetemp 상위 폴더를 준비했으며 반복 실행 전 정확한 저장소 내 경로를 확인했다.

1. 최초 묶음 **exit 1**: `22 passed, 15 errors in 0.61s`. `.tmp/tooltip` 상위 폴더가 없어 fixture setup 15개가 실행되지 않았다. 22개 개별 성공을 별도 Gate PASS나 후속 결과에 합산하지 않는다. 대상은 `test_tooltip_t1_contract.py::{test_adopted_reader_boundary,test_slot_layer2_layer3_input_contract}`, `test_tooltip_t1_audit.py::test_minimal_t2_handoff_mock_consumer`, `test_tooltip_t2_projection.py::{test_admission,test_projection,test_s2_supply_and_owner_integration}`, `test_tooltip_t2_cli.py::test_cli_finalization`, `test_tooltip_t2_serialization.py::test_serialization_guard`였다.
2. 미실행 fixture 관련 node만 재실행 **exit 0**, `15 passed in 96.33s`: reader boundary, T2 admission/projection, S2 owner integration, T2 CLI finalization. 미영향 22개는 숫자를 맞추기 위해 반복하지 않았다.
3. 마지막 installer writer lock 및 package producer source binding 보완 후 `test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration`만 재실행 **exit 0**, `1 passed in 74.62s`. 해당 변경이 영향을 주는 deterministic candidate identity, stage/install/rollback, source drift 경계, Lua 및 package를 같은 fixture에서 재확인했다.
4. Lock 도입에 맞춰 package reader가 첫 migration의 owner 파일 생성 전에도 `IrisTooltip.lock`을 발견하면 거부하도록 한 줄을 보완했다. 기존 파일의 `test_package_rejects_tooltip_writer_lock`만 `uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_package_rejects_tooltip_writer_lock -q`로 확인해 **exit 0**, `1 passed in 0.35s`였다. 30초 제한의 PowerShell 호출로 해당 거부 경계만 확인했고 공급·전체 fixture를 다시 생성하지 않았다.

최종 통합 node 내부의 실제 명령은 다음과 같고 각각 **exit 0**이다. 아래 `$s`는 `C:/Users/MW/Downloads/coding/PZ/.tmp/tooltip/tests/test_s2_supply_and_owner_integ0/s`이며 별도 gate별 workspace가 아니다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1 -Roots .tmp\tooltip\tests\test_s2_supply_and_owner_integ0\s\Iris\media\lua
lua .\Iris\test\lua\tooltip_static_data_runtime_harness.lua $s supply .\.tmp\tooltip\tests\test_s2_supply_and_owner_integ0\expected.lua
powershell -NoProfile -ExecutionPolicy Bypass -File "$s/Iris/tools/package_iris.ps1" -OutputRoot "$s/.tmp/package" -Zip
```

자식 명령은 240초 timeout이며 실행 중 상태를 확인했다. 비정상 장기 실행·강제 중단은 없었다. 기존 disposable wrapper는 외부 OS temp를 사용하므로 실행하지 않고 동일 package 명령·격리 설치·member readback과 Lua 검사를 통합 node에서 공유했다. Wrapper 자체 PASS라고 기록하지 않는다.

## Subject 및 current 보존

작업 subject는 dirty HEAD `a131b9027fd82097dfdc41924b7aca396a82eb07`, tree `b554fe02c38f2f23016e6a0fb417a35b75961eaf`이다. 착수 당시 이미 Layer 2, L3-06 product/install/package/runtime/harness 및 세 authority 문서 등에 수정이 있었고 다수 historical docs가 삭제되어 있었다. 본문은 그 기존 변경을 B의 새 구현으로 귀속하지 않는다.

최종 fixture의 supply SHA-256은 `a5b47a3d8543068b074196e0185b9e4c47c8fcc01b5e3299f83e7469415a0367`, product ID는 `ttp-fd1013c1b39960bdfc7811d42e7ecafe32dd1ee5576efc3ed19c81be434df2eb`이다. 이는 **test fixture identity**이며 adoption/current locator가 아니다. Static SHA-256 `6ecf00b21d9c077b697bb2a667aad5c75cc1dc1ce783bd7855ee30b7e8740ce0`, Recipe SHA-256 `f5504aa5a028d0ecb7da7c463511964df618b67ccc154062acb6a5f16113e529`. 최종 fixture는 기존 테스트 work root에만 남겼다.

변경하지 않은 실제 runtime 파일 SHA-256:

- `IrisTooltipStaticData.lua`: `f4a2ec3ba1f9b2e830c538374991d1a02c20b65e3bbb2876c3f5f7959018995f`.
- `IrisTooltipRecipeVariants.lua`: `b94301ecd933fd86e5e9f254611302ab42b5e5accbe587bb453d7e65e4f628d1`.
- `IrisLayer3DataCurrent.lua`: `347890b872dfdd075053cbddde49edfb69b8311934a1027daf3ffe5efbff6989`.

Machine-tested 변경 파일 16개의 sorted `repository-relative-path<TAB>raw-sha256<LF>` 결합 digest는 `4f7d69e108701698e7bef9190c9e85e52da491707e76cb58744200dff8f88577`이다. 대상: layer3의 `recovery.py`, `tooltip_s2_supply.py`, `product_install.py`; tooltip_t1의 `audit.py`, `cli.py`; tooltip_static_data_projection의 `contract.py`, `cli.py`, `install.py`; 세 package PowerShell 파일; Tooltip runtime harness; 변경된 두 test 파일; `s2_supply_contract.json`; `projection_manifest.schema.json`. 별도 identity manifest는 만들지 않았다. 이후 문서 delta는 이 결과 문서와 계획/DECISIONS/ARCHITECTURE/ROADMAP/문제 문서/walkthrough의 상태 동기화다.

최종 diff 확인은 새 reader block에 복사된 CRLF를 trailing whitespace로 지적해 exit 1이었다. 해당 새 block의 줄 끝만 LF로 통일한 뒤 동일 범위 `git diff --check`는 exit 0이다. 이는 Python 실행 내용이 같은 formatting delta이며 위 fixture의 raw producer identity를 새 bytes의 production identity로 승계하지 않는다. 제품 bytes는 그대로다. 이 formatting 이후 정상 adopted readback을 다시 확인하며 전체 fixture를 confidence 목적으로 반복하지 않는다.

위 snapshot 이후 최종 파일 delta의 SHA-256: reader의 LF 정리 후 `recovery.py`는 `f9fa5fa029e00a3d88cab6c33442949411a8beaf3c547bfe911ce79867635c2b`; package lock 거부 보완 후 `Layer3PackageProjection.psm1`은 `357d99fa61d649291bd8a7e6356fe61b37d33485829095670d6d53a49e6e175e`; 그 관련 assertion을 추가한 `test_tooltip_t2_projection.py`는 `ed1968dffeedf84546a1a38292de995e38f7f3441ee027ade979df82854c4b0e`다. Fixture artifact는 당시 producer bytes에 귀속되며 마지막 guard 변경을 포함한 새 production candidate라고 주장하지 않는다. 마지막 수정 파일·문서의 diff check도 exit 0이다.

## 남은 실행 경계와 C 인계

외부 경로 제한과 clean subject 부족은 서로 다른 blocker다.

- **경로**: T1 `run_candidate/_require_external` 및 T2 `external_path`는 신규 strict 산출물과 receipt에 repository-external 경로를 요구한다. 이번 사용자 프롬프트는 exact external required input이 명명되지 않은 저장소 밖 접근·변경을 금지한다. 임의 외부 경로를 만들거나 repository-local legacy locator를 새 생산 출력으로 재사용하지 않았다. 향후 필요한 역할은 strict T1 후보/final handoff, T2 생성/finalization 및 기존 실행 receipt의 허용된 외부 출력 위치다.
- **Subject**: T1 `validate_execution_subject`, T2 `machine_subject` 및 기존 canonical 계약은 clean subject를 요구한다. 현재 dirty 작업 트리를 사용자 승인 없이 commit/reset하거나 별도 execution worktree로 전환하지 않았다.
- **Canonical**: generic full 명령이 있다는 이유만으로 실행하지 않았다. 실제 production finalization에는 기존 T1 `_validate_gate_chain`의 same-subject full-gate receipt와 T2 completion의 canonical_full_gate 요구가 남는다. `repository_test_gate.json`은 Tooltip focused tests를 dedicated route로 구분하고, `required_validations.json`의 L3 product 항목도 보존했다. 이 요구를 삭제하거나 fixture 결과를 receipt로 꾸미지 않았다. 해당 실제 finalization/canonical 축은 미실행 `blocked`다.
- **PZ**: 허용된 경로 안에서 실제 게임 실행·관찰 환경을 확보하지 못했다. 게임 버전/배율/KO·EN 실제 관찰 값은 없으며 runtime harness를 PZ 관찰로 대신하지 않는다.

C는 같은 `recovery.load_adopted` 반환의 `payloads.expression.items[].locales[ko/en].expanded`와 audit를 사용하면 된다. B의 embedded handoff는 초기 공급의 durable 자료이며 C의 새 semantic authority가 아니다. C를 기다리는 추가 검사나 old Menu claim 전수 대응은 하지 않는다. 실제 공동 전환 시 같은 adoption/expression identity와 두 소비 결과를 확인해야 한다.

문서 갱신 후 첫 정상 adopted readback은 exit 0, `mode=adopted`, `targets=2105`, `B_C_same_expression=true`였다. 위 reader 줄 끝 정리 이후의 최종 정상 readback 결과도 아래에 기록한다. Production/current 미전환 범위는 그 readback 성공과 별개다.

최종 정상 `uv run --project .\Iris\tooling python -I -B -c ...recovery.load_adopted(...)`는 **exit 0**, `{"mode":"adopted","targets":2105,"B_C_same_expression":true}`였다. 같은 고정 adoption/hash를 사용했다. 이후 package의 in-progress 거부 보완은 reader/data를 변경하지 않으며 본 단락은 결과 기록 delta다. C가 정상 소비할 shared reader를 확보했지만 B의 실제 production/current/PZ 성공으로 확대하지 않는다.

## 외부 실행 전 준비안 — 미승인 제안

다음 내용은 실행 허가나 채택된 계약 변경이 아니다. `C:/pzv` 및 게임 설치 경로는 존재 확인도 하지 않았다. 원본 저장소 commit/reset/stash, 별도 checkout 생성, 환경 설치, 신규 strict 실행, 게임 실행은 하지 않았다. 사용자 owner 사전 승인은 유지하지만 명시된 filesystem 경계를 이 문서로 스스로 확장하지 않는다.

### 기존 두 실행 요구와 계획의 충돌

`Iris/_docs/authority/tooltip_t1/tooltip_t1_tool_disposition_contract.json`의 `post_gate_finalization.complete_requires_same_subject_run_a_run_b_and_comparator_exit_0`는 `true`다. `tooltip_t1/cli.py:103`부터의 finalizer 인자는 `--run-a-orchestration-receipt`, `--run-b-orchestration-receipt`, `--comparator-receipt`를 모두 필수로 받는다. `audit.py:605`의 `_validate_gate_chain`은 각 실행의 schema, 성공/exit 0, 동일 subject, 환경 configured/restored, 실제 result receipt hash 및 same-subject PASS를 검사한다. `audit.py:636`의 `finalize_closeout`은 이를 A와 B 각각에 적용하고, 같은 claim, comparator 성공, 두 실제 receipt chain의 정확한 연결, 두 `canonical_result` 파일 hash 일치까지 확인한다.

따라서 A는 첫 clean 실행의 전체 계약 성공을, B는 같은 subject의 별도 실행 성공을, comparator는 두 실행의 canonical 결과 재현성을 증명한다. A/B가 서로 다른 기능 coverage를 갖는다는 근거는 확인하지 않았지만, 두 번째 실행에는 반복 가능한 전체 실행 결과라는 별도 보장이 있다. 공급·static·Recipe 두 생성의 equality만으로 이 전체 결과 보장을 대체할 수 없다. 같은 receipt를 A/B에 복제해서도 안 된다.

계획 §7은 “기존 모듈 계약이 명시적으로 요구하는 독립 Gate까지 삭제하는 뜻은 아니다”라고 하면서, 같은 절에서 “full-suite 두 실행 ... 하지 않는다” 및 canonical “최종 exact subject에서 한 번 실행”을 명시한다. 현재 finalizer와 횟수 제한은 양립하지 않는다. **권고안은 계약을 그대로 두고 이 필수 T1 finalization에 한해 계획의 횟수 제한을 정정하는 것**이다. 다른 B 단계의 별도 A/B suite는 추가하지 않는다. 이는 아직 채택/실행된 정정이 아니다. canonical 1회 successor, 새 recorder/receipt 체계, 기존 요구 삭제는 구현하지 않았다. 환경 허용만으로 이 충돌이 자동 해결되지는 않는다.

### clean subject에 포함할 정확한 미커밋 overlay

별도 clone도 별도 checkout이며 준비 비용이 있다. 제안은 원본 HEAD의 Git 이력(기존 D6 ancestry 포함)을 보존한 `C:/pzv/s` checkout 하나에 아래 파일의 **현재 전체 bytes**만 overlay하고 그곳에서만 commit하는 것이다. 원본의 staged/unstaged 구분을 변경하지 않는다. 새 snapshot에는 아래 기존 기반 변경도 함께 포함하므로 B만 HEAD에 얹어 미커밋 의존성을 누락하지 않는다. 목록은 복사 허용 목록이며 전체 dirty tree 복사 지시가 아니다.

B 코드·검사·계약(공유 파일은 기존 변경도 포함):

```text
Iris/tooling/src/iris_tooling/domains/layer3/recovery.py
Iris/tooling/src/iris_tooling/domains/layer3/tooltip_s2_supply.py
Iris/tooling/src/iris_tooling/domains/layer3/product_install.py
Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py
Iris/tooling/src/iris_tooling/domains/tooltip_t1/cli.py
Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/contract.py
Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/cli.py
Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/install.py
Iris/tooling/tests/test_tooltip_t1_contract.py
Iris/tooling/tests/test_tooltip_t2_projection.py
Iris/test/lua/tooltip_static_data_runtime_harness.lua
Iris/tools/Layer3PackageProjection.psm1
Iris/tools/RuntimeLookupIndexIdentity.psm1
Iris/tools/package_iris.ps1
Iris/_docs/authority/tooltip_t1/s2_supply_contract.json
Iris/_docs/authority/tooltip_static_data_projection/projection_manifest.schema.json
```

필수 기존 기반: Layer 2 checkout identity·owner validation, L3 product/package 동작과 그 기존 validation membership을 함께 보존한다. 아래는 B가 새로 만든 변경이 아니다.

```text
Iris/build/classification/data/classification_layer2_resolution_registry.json
Iris/tooling/src/iris_tooling/domains/classification/layer2_contract.py
Iris/tooling/src/iris_tooling/domains/classification/layer2_materializer.py
Iris/tooling/src/iris_tooling/domains/classification/layer2_validator.py
Iris/tooling/tests/test_classification_layer2_input_identity.py
Iris/tooling/src/iris_tooling/domains/layer3/product_projection.py
Iris/build/description/v2/tests/test_layer3_product_integration.py
Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua
Iris/media/lua/client/Iris/Data/IrisLayer3EnglishLookup.lua
Iris/media/lua/client/Iris/Data/layer3_renderer.lua
Iris/_docs/round3/round3_pytest_source_classification.json
Iris/validation/execution/contracts/repository_test_gate.json
Iris/validation/execution/required_validations.json
```

작업 authority·상태 문서:

```text
docs/ARCHITECTURE.md
docs/DECISIONS.md
docs/ROADMAP.md
docs/iris_dvf_tooltip_s2_supply_ownership_recovery_plan.md
docs/iris_dvf_tooltip_ownership_recovery_problem.md
docs/iris_layer3_product_walkthrough.md
docs/iris_tooltip_supply_closeout.md
```

기존 r6 파일은 HEAD에 이미 tracked이므로 이력 복사에 포함한다. untracked r1~r5 복사, 모든 `.tmp` 복사, unrelated 연구 문서·walkthrough 수정, 기존 historical docs 삭제는 overlay에서 제외한다. 별도 snapshot의 HEAD 문서를 유지하는 것이며 원본 삭제를 복원하지 않는다. 복사 시 위 목록의 누락·bytes 차이와 예상 Git diff만 확인하고 별도 census/manifest를 만들지 않는다. 추가 의존성이 실제로 발견되면 원인과 exact 파일을 보고하며 허용 목록을 임의 확대하지 않는다.

### 요청할 외부 범위와 최소 실행 순서

제안 root `C:/pzv` 하나의 읽기/쓰기/실행과 그 안의 checkout 전용 commit을 요청한다. 하위 이름은 역할에 따른 짧은 경로이며 계약상 두 실행을 채택할 경우에만 실제 A/B 산출물을 구분한다.

| 경로 | 필요한 기존 역할 |
|---|---|
| `C:/pzv/s` | 정확한 overlay를 포함한 clean subject checkout; 자체 `.tmp/tooltip`은 공급·candidate·격리 설치·package 작업에 공유 |
| `C:/pzv/e` | 해당 subject wheel을 설치한 전용 Python 환경 |
| `C:/pzv/er` | 기존 environment recorder가 요구하는 manifest, receipt, SHA sidecar 세 파일 |
| `C:/pzv/iris_tooling-0.1.0-py3-none-any.whl` | 해당 source에서 빌드한 installed-package 입력 |
| `C:/pzv/w` | 기존 canonical launcher가 소유하는 실행 workspace; 내부 checkout/temp도 이 안에 유지 |
| `C:/pzv/r` | 기존 canonical 결과 보존. A/B 필요시 그 기존 결과만 짧은 a/b로 구분 |
| `C:/pzv/a.json`, `b.json`, `compare.json` | 기존 orchestration/comparator receipt 역할; 새 형식 아님 |
| `C:/pzv/h` | 공유 D2 입력과 실제 strict T1 생성 a/b 및 final f |
| `C:/pzv/t` | 실제 T2 생성 a/b 및 final f |
| `C:/pzv/pz` | 게임 관찰이 별도로 가능할 때만 사용하는 격리 cache/mod/save/log |

준비 비용은 checkout 복사, wheel 빌드, 전용 환경 설치·기존 environment 기록, clean snapshot commit이다. 기존 `current_environment.json`이 가리키는 `.tmp/z/e`, `.tmp/z/er2`, `.tmp/z/w`의 이전 source receipt를 새 subject 성공 근거로 재사용하지 않는다. 환경 도구가 별도 전역 cache/temp나 runtime 경로를 필요로 하면 이 승인 범위에 포함되지 않는다. cache/temp는 허용 root로 지정하고, 그 밖의 정확한 필수 runtime 접근은 확인된 필요 범위를 따로 제시해야 한다.

허용 및 위 계약 충돌 해소 이후의 명령 흐름은 다음과 같다. 지금 실행한 명령이 아니며 `<...>`는 실제 snapshot과 기존 도구 출력에서 얻을 값이다.

1. `git clone --no-local C:/Users/MW/Downloads/coding/PZ C:/pzv/s` 후 위 allowlist bytes를 복사하고, 그 checkout에서만 `codex/tooltip-supply` branch와 snapshot commit을 만든다. 원본 저장소는 read-only 입력이다.
2. snapshot wheel/전용 환경을 준비한 뒤 기존 `record_environment.py`의 `--environment-root`, `--project`, `--lock`, `--wheel`, `--source-commit`, `--source-tree`, `--out`, `--authority-record-out`, `--current-locator-out`을 사용한다. 필요한 authority/locator 변경은 복제 checkout에만 기록하고 commit한다. package source tree와 환경 기록의 subject 조건을 지킨다. 새 환경 기록 도구는 만들지 않는다.
3. 공급 CLI `python -m iris_tooling.domains.layer3.tooltip_s2_supply --repository-root C:/pzv/s --output C:/pzv/s/.tmp/tooltip/supply.json`을 사용한다. 기존 pinned legacy 입력은 원본 저장소의 명시된 `.tmp/z/v/f` locator/member를 읽는다. D2는 기존 `iris-tooling ... build tooltip-t1 d2-materialize --output-root C:/pzv/h/d2`로 한 번 materialize하여 두 T1 생성이 공유한다.
4. installed `iris-tooling --repository-root C:/pzv/s build tooltip-t1 --output-root <h/a 또는 h/b> --decision-contract-sha256 <실제 계약 hash> --verify-invariants --layer2-menu-relation <D2 산출물> --strict-production-handoff --s2-supply <supply.json> --s2-supply-sha256 <실제 hash>`로 실제 생산한다. canonical 실행은 기존 `validate full --commit <subject> --claim-id <claim> --environment-receipt <receipt> --work-root C:/pzv/w --result-root <r 하위 실행 결과> --orchestration-receipt <a.json 또는 b.json>` 경로를 사용한다. 두 실행이 채택된다면 기존 comparator로 실제 두 chain을 비교하고, T1 `finalize tooltip-t1`에 세 실제 receipt를 전달한다. 같은 work root의 재사용 가능 여부와 결과 보존은 기존 launcher 규칙을 따른다.
5. finalized T1 candidate locator를 명시한 T2 build 두 생성과 finalize를 수행한다. 같은 공급/handoff/static/Recipe 결과를 결정성·exact text·set/absence 검사에 공유한다. 기존 B installer API의 `.tmp` stage/install/rollback, Lua syntax/harness/package는 같은 최종 candidate에서 묶어 수행한다. canonical이 실제 포함해 성공한 검사는 다시 실행하지 않는다. 이전 fixture는 새 production subject receipt로 승계하지 않는다.

공급기의 마지막 후속 수정은 `current_support`의 “legacy handoff가 현재 checkout 내부여야 한다”는 추가 제한 하나를 제거한 것이다. 고정 locator가 원본 checkout의 입력을 가리킬 수 있도록 했고, `read_handoff`의 exact root/subject/member hash 검사는 유지했다. 신규 T1/T2 출력의 repository-external 요구는 그대로다. 이 변경 후 테스트를 반복하지 않았으며 다음 허용된 실제 후보의 최종 검사에 포함해야 한다. 앞서 기록한 fixture identity에는 이 후속 변경이 포함되지 않는다.

### PZ 접근과 관찰 한계

저장소의 `Iris/test/run_pz_core_refactor_harness.ps1`에 기록된 기본 실행 경로는 `G:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid/ProjectZomboid64.exe`다. 설치·버전·실행 가능 여부는 외부에서 확인하지 않았다. 필요한 허용 범위는 해당 게임 설치 root의 읽기/실행 및 `C:/pzv/pz` 쓰기이고, 기존 `C:/Users/MW/Zomboid`는 접근하지 않는다. 별도 cache를 지정한 게임 실행 인자는 `-cachedir=C:/pzv/pz -nosteam -nosound -novoip -debug`를 제안한다. 정확한 후보 package를 그 cache의 mods에 배치하고 새 설정/저장만 사용한다.

기존 core-refactor harness는 B의 PZ 검증기가 아니므로 실행하거나 PASS를 재사용하지 않는다. 실행 파일을 띄우는 권한과 KO/EN·Alt·긴 문장·배율·clipping을 화면에서 관찰하는 능력은 별개다. 현재 native UI 관찰 도구가 없으므로 사용자의 실제 관찰 또는 별도로 허용되고 사용 가능한 관찰 수단이 필요하다. 자동 검사만 완료하면 PZ는 여전히 `unvalidated_but_in_scope`로 남긴다. 이 준비 단계에서 가능한 일은 위 계약/소스 확인과 실행안 작성이며, 이미 완료된 fixture나 A 검사를 반복하지 않았다.
