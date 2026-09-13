# DVF-RECOVERY-C 실행 결과

- 날짜: 2026-09-11
- 상태: **implemented_only** — C 구현·B/C 통합·필수 자동 검사 완료, 실제 PZ 관찰 미실시.
- 실행 기준: [채택 계획](iris_dvf_expanded_menu_structuring_common_candidate_recovery_plan.md), Philosophy.md.
- owner approval은 사용자 프롬프트의 사전 승인으로 처리했다. 별도 reviewer/추가 seal/검증 authority는 만들지 않았다.

## 후보 인계

| 항목 | 값 |
|---|---|
| 최종 ZIP | `.tmp/menu/run-jd06pdcs/p/Iris.zip` |
| ZIP SHA-256 | `61c3ccb9ae753d23bfa78d743e0f673e7c22372390e08ce870064458dd12d78a` |
| C product | `l3p-9fc31259642b5eaceb55bd10b87e3d57e739295551f2d8a7d362315be080468f` |
| product / stage / ZIP readback | 같은 실행 폴더의 `a/`, `s/`, `z/` |
| descriptions SHA | `ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0` |
| blocks SHA | `b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796` |
| accepted B | `.tmp/tooltip/preview/Iris.zip`, SHA `33b5927127442b16dca917c6f49f3e661743123c0cbd3d5890d47cb6fca96860` |
| B product | `ttp-5a90c7d3844be93670e1b0f6c9f30db41bc0d17a026caf6f70bb797789ebc163` |
| 보존한 source DataCurrent SHA | `347890b872dfdd075053cbddde49edfb69b8311934a1027daf3ffe5efbff6989` |

최종 후보는 위 ZIP 하나다. 앞선 `.tmp/menu/run-7jm1d937/p/Iris.zip`은 문자열 API의 unsupported locale 보완 전 이력이며 인계 후보가 아니다. B ZIP과 source current, r6/adoption, canonical corpus는 수정하지 않았다. 기존 사용자의 dirty/deleted/untracked 문서도 정리·복원하지 않았다.

## 구현

`build_menu_product()`는 기존 reader로 canonical expanded/blocks를 읽는다. Historical `build_product()`의 expression 및 Tooltip 재생성 경로와 명시적으로 구분한다. C product schema는 v2이며 이전 공개 문자열/full-table facade를 유지한다. 후보 내부 ProductCurrent → Descriptor → compatibility DataCurrent → Index → chunks → lookup이 C ID를 선택한다.

4,210 expanded states(2,105 × KO/EN), present 4,086 / absent 124를 보존한다. locale별 acquisition-only 59개는 compact 부재와 무관하게 표시한다. locale별 expanded absent 62개와 175개 B-only support는 다른 분모다. 잘못된 payload는 fault이고 정상 absent로 합산하지 않는다.

표시 단위는 원문 segment의 연속 구간이다. block/branch/fact/qualifier/relation 연결이 가로지르는 경계는 분리하지 않으며, source `separate_block_refs` 안에서 참조가 걸치지 않는 경계만 간격으로 구별한다. 동일 branch를 의미 동일성으로 재분류하지 않는다. 문장을 합성·절단·복제하지 않고 segment 순서와 qualifier scope를 그대로 보존한다. `Base.Plank` 선행/후속 조건 및 `Base.Lipstick` 공통 접근 조건은 같은 연속 단위로 표시한다. 접기·대표 용도·임의 제목·runtime 요약은 추가하지 않았다. grouping이 불명확하면 연속 표시로 남긴다.

전체 item 원문과 refs/relations/unresolved/detail links는 기존 product manifest의 offline trace에 보존한다. Lua는 text/state/reason/units와 1-based segment 범위를 받는다. 0-based compact link는 offline trace에 runtime segment와 unit destination을 함께 기록한다. 공통 composition owner는 읽기만 했으며 원문·metadata를 재생성하지 않았다.

`getDisplay()` → Detail assembler → `getLayer3Units()`를 Browser Detail과 WikiPanel이 공통 사용한다. C에서는 기존 문장부호 formatter를 grouping에 사용하지 않는다. 두 consumer의 기존 폰트 wrapping·label 위치·content height·scroll 계산을 재사용한다. Browser item/locale 변경은 scroll을 초기화한다. 기존 readonly 모델과 L2/L4 병합 경계를 유지한다. KO/EN 외 locale, 손상 pointer/index/member/descriptor는 다른 locale·predecessor·stale global로 대체하지 않는다.

## B 보존과 설치 경계

accepted B ZIP과 변경 전 source의 retained runtime 차이는 Tooltip 세 artifact뿐이었다. C stage는 다음을 수락 ZIP에서 raw bytes로 복사한다.

- `IrisTooltipStaticData.lua`, `IrisTooltipRecipeVariants.lua`, `IrisTooltipOwner.json`.
- C가 교체하는 legacy generation/facade 및 의도적 공유 변경을 제외한, 변경 없는 retained media 전체. 최종 보존 대상은 **106개 파일**이다. Tooltip runtime과 그 retained require closure도 이 집합에 포함한다.

의도적 공유 변경은 아래 여섯 파일이다. 실제 before/after SHA는 최종 `a/product_manifest.json`의 identity/shared_changes에 있다. 이 파일들은 byte-preservation 성공에 포함하지 않았다.

| 파일 (client/Iris 기준) | 변경과 B 영향 |
|---|---|
| `Data/IrisLayer3DataLookup.lua` | 구조·state validation, product 실패 시 predecessor 거부. Tooltip static 선택 정책은 유지 |
| `Data/layer3_renderer.lua` | additive display API, C의 unsupported locale 거부. Tooltip 본문 producer는 아님 |
| `UI/Detail/IrisItemDetailModelAssembler.lua` | readonly units/state/product identity 전달 |
| `UI/Wiki/IrisWikiSections.lua` | 공통 units API, 기존 문자열 section 유지 |
| `UI/Wiki/IrisWikiPanel.lua` | units 순서대로 wrapping/높이 계산 |
| `UI/Browser/IrisBrowserDetail.lua` | 동일 units와 간격, item/locale scroll reset |

stage overlay 완료 후와 actual final ZIP에서 106개 파일을 accepted B raw bytes와 비교했다. 동일 corpus SHA 및 owner/product binding도 패키저가 검사한다. B 고유 세 artifact의 hash를 갱신하여 불일치를 숨기지 않았다. 정상 복사 경계에 별도 EOL 조사표를 만들지 않았다.

기존 package_iris/Layer3PackageProjection/RuntimeLookupIndexIdentity 경로를 사용했다. RuntimeLookupIndexIdentity 자체는 수정하지 않았다. C v2 descriptor는 B 독립 소유권과 보존 member 집합을 결속한다. 기존 hash/lock/source-drift 보호를 유지한다. `restore_candidate()`는 `.tmp/menu` 후보 안에서 기존 journal/recover를 사용하며 live `promote()`의 Tooltip owner guard는 유지한다.

## 자동 검증

마지막 실행은 다음 **전체 node, exit 0, `1 passed in 100.05s`**다. 최종 candidate는 위 `l3p-9fc312…`이며 이 실행 안에서 모든 아래 자식 명령도 exit 0이었다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\menu\accept3 -q -s --tb=short
```

아래 `$run`은 저장소 루트의 `.tmp/menu/run-jd06pdcs` 절대 경로다. 명령은 부모 node의 실제 checkpoint에서 호출됐으며 같은 stage/ZIP을 공유했다.

| Checkpoint | 결과 |
|---|---|
| input / conservation | 두 SHA/reader, 2,105 exact IDs, 4,210 states, ordered segment 전수 대응, refs 해소·scope·unresolved 원본 보존, link destination, optional dispositions 생략 허용 |
| 결정성 | `a/`와 `b/` 두 생성의 product manifest/member bytes 동일. 전체 checkout 재현성 주장이 아님 |
| stage-b-identity | 106개 accepted B byte identity 및 동일 corpus owner |
| lua-syntax | `powershell -NoProfile -ExecutionPolicy Bypass -Command '& .\tools\check_lua_syntax.ps1 -Roots @("Iris/media/lua", ".tmp/menu/run-jd06pdcs/s/Iris/media/lua")'`; **388 files, exit 0** |
| lua-model | `lua Iris/test/lua/detail_view_model_locale_harness.lua $run/s expanded $run/menu.lua`; actual C payload 전수 모델, readonly units, absent/fault, stable full-table facade, 두 실제 consumer의 표본 label/scroll, locale/item/reopen, invalid locale/index/payload/descriptor/predecessor 반례. **exit 0** |
| b-runtime | `lua Iris/test/lua/tooltip_static_data_runtime_harness.lua $run/s supply $run/tooltip.lua`; **2,280 exact IDs, S1~S4·Alt/opening·fit-failure 반례, exit 0**. 로그의 Fixture.Layout fit failure는 의도한 반례 |
| l4-model | `lua Iris/test/lua/browser_interaction_density_acceptance_harness.lua $run/s`; 기존 Recipe/Right-click/EvolvedRecipe density/접근 fixture. **exit 0** |
| package-admission | 같은 stage에서 Tooltip bytes/owner 오염, stale EN, 두 writer lock을 각각 거부하고 원본 복원. 기존 package Get-FileHash 함수를 재사용하는 부모 내 PowerShell 호출, **exit 0** |
| package | `powershell -NoProfile -ExecutionPolicy Bypass -File $run/s/Iris/tools/package_iris.ps1 -OutputRoot $run/p -PackageApplicability current_runtime_payload -Zip`; **exit 0** |
| zip-c-pointer | ZIP member 전수 parity와 B 원본 byte 비교 후 `z/`에 풀어 fresh Lua로 위 expanded harness 호출. **4,210 states, 두 consumer, C product ID 일치, exit 0** |
| recovery | candidate member drift, traversal/source overlap, source drift, writer lock, live promote owner guard 거부. 후보 transaction 예외 및 process interruption 복원, recover/idempotence, source pointer 보존. 부모 node 안에서 성공 |

과정 중 실패와 수정:

1. 최초 `--basetemp .tmp/menu/accept` 실행은 `.tmp/menu` 상위 폴더 부재로 setup exit 1. 폴더를 만든 뒤 진행했다.
2. 첫 후보의 Lua/B/L4까지 exit 0이었으나 package-admission의 PowerShell `Get-FileHash` autoload가 uv의 reduced PSModulePath에서 실패했다. 기존 패키저의 동일 함수 정의를 재사용하여 해결했고 `IRIS_MENU_RESUME_PACKAGE`로 그 exact 후보의 후반을 이어서 exit 0을 확보했다. 이 환경변수는 명시적 실행 재개만을 위한 것이며 PASS receipt/새 authority가 아니다.
3. C 문자열 API에 남아 있던 unsupported locale → KO 선택을 제거하고 반례를 추가했다. B 보존 descriptor 집합의 누락도 authenticated identity 집합과 대조하도록 했다. 그 source 변경으로 새 candidate를 생성해 위 마지막 전체 node를 exit 0으로 마쳤다. 옛 후보 결과를 최종 후보 성공으로 합산하지 않는다.

30초 단위 상태 확인과 자식 실행 상한을 적용했다. 비정상 장기 실행/강제 중단은 없었다. Java/Gradle·JS/TS는 변경하지 않아 실행하지 않았다. composition owner도 변경하지 않아 문제 1~3 재수락 검사를 추가하지 않았다. B producer/선택 정책은 변경하지 않았고 C 묶음의 accepted-byte 및 기존 supply runtime 검사로 필요한 보호를 확인하여 별도 B 전체 통합을 중복 실행하지 않았다.

기존 required node membership는 유지했다. historical expression의 5,290 facts·1,280 S2·552 expanded empty 및 flattened block 기대는 canonical 4,210 state/ordered units/원본 trace conservation으로 교체했다. B 보존은 재생성된 historical slot equality 대신 accepted B raw bytes와 기존 supply runtime 반례로 확인한다. FullType/locale/member integrity/stable facade/path boundary/source pointer 및 recovery/idempotence 보호는 같은 node 안에 유지했다. 격리 historical promote 성공을 C live promotion으로 확대하지 않고 후보 repair/recover와 기존 owner guard 거부로 확인한다.

current required locator는 `Iris/validation/execution/required_validations.json`이다. `_docs/round3/current_route_required_validations.json`은 historical, `validation/current_route/required_validations.json`은 중간 naming locator다. 과거 기록/schema는 소급 수정하지 않았다.

## 실제 PZ 관찰 및 상태 축

| 축 | 상태/경계 |
|---|---|
| C implementation / B-C integration / 자동 검증 | **validated** — 위 exact candidate에 한정 |
| Actual PZ Menu, KO/EN Browser/Wiki, 같은 후보 B 공존 | **unvalidated_but_in_scope** — 미관찰. 관찰자·게임 버전·해상도·UI scale·실제 폰트는 미제공 |
| 전수 인간 품질 검수·2,105개 전수 게임 열람, 모든 환경·멀티/장시간/모드 호환 | **out_of_scope** |
| 신규 unresolved 의미 해결·후속 prose polish | **out_of_scope** |
| Current 공동 activation / strict production finalization / release·deployment | **out_of_scope, 미수행** |
| 전체 Clean-Checkout A/B 재현성 | **out_of_scope** — product 두 생성 결정성과 구분 |
| C closeout | **implemented_only** |

Lua 모델의 engine/API/font/widget fixture와 actual payload readback을 구분한다. 원문 conservation과 label bounds는 실제 폰트 가독성이나 게임 화면의 성공 증거가 아니다. B의 과거 실제 PZ 수락을 C 관찰로 승계하지 않는다. 저장소 밖 게임 폴더를 탐색하거나 자동 설치하지 않았다.

동일 최종 ZIP으로 남은 관찰:

- KO/EN 각각 Browser Detail과 우클릭 Wiki에서 단일/복수 용도, multi-branch/qualifier가 많은 설명, `Base.Plank`·`Base.Lipstick` 선행 의존 확인.
- acquisition-only(`Base.Baseball` 등), expanded absent(`Base.BackgammonBoard` 등)에서 L3와 L2/L4의 독립 접근 확인.
- 긴 설명·좁은 폭·section 경계·스크롤 끝 및 L4가 많은 항목의 Recipe/Right-click/EvolvedRecipe 접근 확인.
- item/locale 재구성, 닫기/재열기의 stale text/state와 같은 후보 B Alt/opening/S1~S4 확인.

관찰 결과는 위 ZIP SHA, 관찰자, locale, 위험 유형과 defect/수정·재관찰 범위에 결속한다. blocking defect가 있으면 corrected candidate를 다시 확인한다. 이 관찰이 닫히기 전에는 complete로 바꾸지 않는다. current 전환은 별도 인계이며 본 작업의 남은 자동 검증 gate가 아니다.


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

## 2026-09-13 Alt Tooltip S3 획득 라벨 후속

상태: **implemented_only**, 실제 PZ 미관찰.

`Iris/tooling/src/iris_tooling/domains/tooltip_t1/s2_candidate.py:77`의 `acquisition_places()`에서 foraging/foraging_crop_seed 장소 표시 접두만 KO `채집: ` → `획득: `, EN `Foraging: ` → `Acquisition: `으로 변경했다. 별도 번역 키는 없으며, 생성된 StaticData/RecipeVariants를 Lookup.open이 공급하고 AltTooltip.drawText가 완성 줄 그대로 렌더한다. 취득 근거/장소, 덫/낚시 활동 이름, 다른 본문/기술명, L4 선택과 줄 구조는 보존했다.

기존 두 통합 검사만 수정 후 한 번 실행: **2 passed in 134.21s (0:02:14)**, 종료 코드 **0**.

```powershell
$env:IRIS_SHARED_MENU_VALIDATION='1'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\common -q -s --tb=short
```

검사 로그: `.tmp/prose/acquisition-label-tests.log`. 이 실행은 정규 Tooltip owner 및 누적 Menu product/package 생성, Lua 구문·런타임 fixture와 ZIP readback을 포함한다. 설명 코퍼스는 재생성하지 않았고 description composition 검사는 재실행하지 않았다. 그 검사 결과는 직전 weapon 기록에 속한다.

패키지 읽기 비교 결과 StaticData 1007개, RecipeVariants 1625개의 KO 접두 및 대응 EN 접두만 바뀌었다. 두 파일 모두 이전 바이트에 해당 접두 변경만 적용한 결과와 정확히 일치한다. expanded 11 chunks는 product ID 변경을 제외한 내용이 같다. Description SHA256 `cc25b4596aa5d3d3ec0fd43a00da80ba9390ed3c31285a117465a6c7edad982c`, blocks SHA256 `9d68e982cd508b3a4beafc9d1a8892668c9470d4581f7db0d1761e602926e161`, S2 supply `10d85c0948c442898e8f07c13b75223dec77fc3a5440531d0eca5d2a6a81170f`는 직전과 동일하다. 비교 로그: `.tmp/prose/acquisition-label-readback.log` (단발 패키지 읽기, 새 validator 아님).

- product: `l3p-2fd5e624d199d690997c25c978bca435e7b59936e70999d52516a7b9d044c6bb`
- ZIP: `.tmp/menu/run-bcwd4x0i/p/Iris.zip`
- ZIP SHA256: `60ca0eee037aa93dba08259212bb8e0fa28b9c97528e88c0ff878471c16fb316`
- direct mod root: `C:\Users\MW\Downloads\coding\PZ\.tmp\menu\run-bcwd4x0i\p\Iris`
- 직전 run-6bt0yuh8 ZIP SHA256 `21bed8da7bda2b0c0cfd5e92b3e6719735f7ba283fedd90b47c98d0ea9719b4a` 그대로 보존.

참고: 현재 패키지의 Base.CannedMilk 행에는 S3 장소 줄이 없다. 사용자가 본 개별 연유 항목의 정체·근거는 이번 라벨 변경 범위에서 재조사하지 않았다. 라이브 설치/커밋/푸시 없음.
