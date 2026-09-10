# Implementation Plan — DVF-RECOVERY-B

검수된 DVF compact 공급과 실제 네 줄 Tooltip 복구

- 개정일: 2026-09-11 / v3
- 상태: complete — 2026-09-11 사용자 실제 PZ 확인 및 명시적 통과 지시로 B 후보 구현·통합·실제 표시 수락. C/current 공동 전환·일반 strict finalization·release 완료는 별개다.
- 형식: [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md)
- 현재 입력: [문제 3 최종 기록](iris_dvf_description_quality_acceptance_closeout.md)
- 기존 구현 이력: [Tooltip 공급 실행 기록](iris_tooltip_supply_closeout.md)
- 기존 [B 문제 정의](iris_dvf_tooltip_ownership_recovery_problem.md)는 r6 기준 v2다. 현 실행에는 사용자가 요청한 이 v3의 입력·범위·표시 기준을 적용한다. C 문제 정의의 r6 기준도 후속 개정 대상이며 이 계획에서 C 구현까지 수행하지 않는다.

이 개정은 기존 r6 고정 입력, wrap 정책 변경 제외, 화면 줄바꿈을 허용하는 logical-row 기준, 미채택 외부 checkout 실행안을 현재 실행 지시로 사용하지 않는다. 과거 성공·실패 기록은 그대로 보존한다.

## 1. Objective

문제 3에서 검수한 같은 설명 corpus의 compact를 기존 Tooltip owner의 Layer 3 입력으로 연결하고, 실제 게임 화면에서 다음 네 행의 역할과 최대 네 줄을 충족한다.

| 논리 역할 | 실제 표시 내용 |
| --- | --- |
| S1 | 2계층 소분류 |
| S2 | DVF compact 설명 |
| S3 | 획득 장소 |
| S4 | 레시피·우클릭 행동·자유 조리 중 해당 아이템에 유효한 무작위 상호작용 하나 |

Alt를 눌렀을 때만 표시한다. 최대 네 줄은 **화면에 그려지는 줄 수**다. S2는 한 줄을 사용하며, 어느 역할도 여러 줄로 늘어 다른 역할의 자리를 차지하지 않는다. 정상 부재 역할은 기존 생략 동작을 유지할 수 있으나 다른 계층으로 대체하거나 placeholder를 넣지 않는다. 생략으로 위치가 당겨져도 공급 데이터의 S1~S4 역할은 바뀌지 않는다.

DVF는 Layer 3 설명을 공급하고 Tooltip은 각 계층 입력의 조립·표시·선택·패키징을 책임진다. QG/Layer 4가 상호작용 내용을 소유한다. B는 C가 같은 corpus의 expanded와 관계를 소비할 수 있게 인계한다.

## 2. Scope

- 새 description reader에서 compact·state/reason·refs·상세 연결을 읽는 공급 adapter와 기존 T1/T2 연결.
- 실제 Tooltip 지원 집합과 DVF 입력 집합의 차이 처리. 기존 owner 검사를 재사용하고 과거 개수를 현재 권한으로 삼지 않는다.
- 기존 S2-only 후보/설치/패키징 경로 재사용과 필요한 최소 계약 확장.
- 실제 화면 네 줄을 위한 renderer의 폭·배치·줄바꿈 처리, S1/S3의 역할 보존.
- S4가 세 종류의 유효한 상호작용을 후보로 받아 하나를 선택하고 읽는 동안 안정적으로 표시하는 전체 연결.
- KO/EN 공급·오류/부재 구분·관련 회귀 및 같은 후보의 실제 PZ 관찰.
- 실제 표시로 드러난 설명 결함의 공통 composition owner 최소 환류와 영향 결과 확인.

### Explicitly Out Of Scope

A 및 문제 1~3의 전수 재조사·재수락, r6 원본 변경, C의 Menu 구현, 외부 모드 정규화 어댑터 구현, QG 사실 재조사, 지원 아이템 확대, 새로운 정보 표면, Workshop/release, 사용자 게임 폴더 자동 탐색·수정은 제외한다. 새 clone/worktree/외부 실행 workspace를 만들지 않는다.

## 3. Non-Goals

- 문자열만 S2에 들어가면 완료하는 작업이 아니다.
- 대표 용도 하나 선택, primary_use 복원, runtime 의미 재합성·재번역·요약, 말줄임·잘라내기로 네 줄을 맞추지 않는다.
- 작은 글꼴 강제, 화면 밖 확장, 긴 행 숨김, 매 프레임 상호작용 교체로 실패를 가리지 않는다.
- 정상 공백 0개, 고정 문장 수·글자 수, 모든 해상도/배율 지원을 목표로 삼지 않는다.
- 새 adoption/seal/receipt/manifest 체계, 보조 검사기의 canonical 승격, gate별 폴더를 만들지 않는다.

## 4. Assumptions

### 새 입력과 완료 범위

| 항목 | 기준 |
| --- | --- |
| 설명 경로 | Iris/build/description/composition/descriptions.json |
| 설명 SHA-256 | ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0 |
| Schema/version | iris-layer3-descriptions-v1 / 1 |
| 의미 입력 | Iris/build/description/composition/blocks.json |
| 입력 SHA-256 | b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796 |
| Reader | description_composition_results.read_result |
| 규모 | 2,105 items / 8,420 states; present 8,054 / absent 366 / failed 0 |
| 각 locale | compact present 1,984·absent 121, expanded present 2,043·absent 62 |
| B / C 좌표 | items[].locales[ko/en].compact / expanded |

이 값은 문제 3의 검수 대상이며 B의 제품 검증 결과가 아니다. 코드 정정으로 바뀌면 필요한 영향 검수를 거친 같은 successor를 B/C에 제공하고 기존 검수 완료 hash를 임의 치환하지 않는다. 착수 원문 확인만을 위한 재생성은 하지 않는다.

현재 compact 부재는 blocks 없는 62개와 acquisition-only 59개에 따른다. 이는 r6의 110 scoped/11 gap 분류와 다르며 옛 상태 매핑을 복사하지 않는다. 입력 없는 item을 사실 조사 완료로 간주하지 않는다. 실패·손상·미지원 schema는 정상 부재로 처리하지 않는다.

### 재사용할 구현과 확인된 차이

- 기존 정상 adopted reader와 historical replay 분리는 재사용할 성과이며 다시 구현하지 않는다. 새 corpus를 읽기 위해 r6 adoption chain을 경유하지 않는다.
- 현재 tooltip_s2_supply.build는 recovery.load_adopted와 r6 s2를 소비한다. 새 compact의 상태·segments·detail_links·qualifier_dispositions를 보존하는 adapter가 필요하다.
- 저장소 내부의 tooltip_t1/s2_candidate.py 경로는 기존 승인된 S2-only 후보 경로다. 일반 D6/T1/T2의 strict finalization과 구분한다.
- 현재 IrisAltTooltip.lua는 별도 패널 폭을 제한하고 wrapRow로 각 row를 여러 화면 줄에 그린다. 이는 확정된 네 줄 요구와 충돌하므로 보존 대상이 아니다.
- 기존 Recipe variant 연결이 우클릭 행동·자유 조리까지 충족한다는 근거는 아직 없다. 실제 L4 입력/선택 경로를 읽어 재사용과 필요한 변경을 결정한다.
- C와 제품 current 적용은 미완료다. 과거 후보의 implemented_only/PZ 대기 기록을 새 입력의 검증으로 승계하지 않는다.

### 실행 경계와 지원 표시 환경

현재 선택된 PZ 저장소 안에서 작업한다. 과거 closeout의 외부 경로 제안은 이 계획의 필수 입력이나 접근 승인으로 채택하지 않는다. locator가 밖을 가리키면 자동으로 따라가지 말고 저장소 내 유효한 입력으로 진행 가능한 범위를 구분한다.

실제 PZ 관찰은 사용자가 동일 후보를 실행해 제공한 결과 또는 별도로 허용된 실행 환경을 사용한다. native 관찰 수단·설치 경로·게임 버전을 추정하지 않는다. 지원할 게임 버전/해상도/배율/언어는 기존 지원 범위와 사용자 환경을 기준으로 기록하고, fit 실패를 피하기 위해 지원 범위를 임의 축소하지 않는다. 환경 미확보는 실제 표시 완료만 제한하며 독립 구현을 막지 않는다.

## 5. Repository Areas Affected

### Code

실제 변경 owner만 수정하며 목록 전체를 수정할 의무는 없다.

- Iris/tooling/src/iris_tooling/domains/layer3/tooltip_s2_supply.py
- 같은 layer3의 description_composition_results.py 및 model, planner, families, lexicon, ko/en 모듈: reader 참조와 실제 표현 결함에 한한 수정.
- Iris/tooling/src/iris_tooling/domains/tooltip_t1/의 s2_candidate.py, audit.py, models.py, contract.py, cli.py.
- Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/의 projection.py, recipe_variants.py, serialization.py, contract.py, cli.py, install.py.
- Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua 및 Iris/Data/IrisTooltipStaticDataLookup.lua, 해당 파일들이 실제 사용하는 L4 lookup/selector와 companion.
- 기존 Iris L4 owner 입력/소비 모듈은 S4의 종류·label·유효 후보 연결에 필요한 범위만 확인·수정한다. 조사 범위는 위 consumer에서 실제 참조하는 저장소 내 경로로 좁힌다.
- Iris/tools/Layer3PackageProjection.psm1, RuntimeLookupIndexIdentity.psm1, package_iris.ps1 및 layer3/product_install.py: 실제 membership/중복 writer 변경이 필요한 경우만.
- Iris/tooling/tests/test_tooltip_t2_projection.py, test_tooltip_t2_cli.py, 관련 기존 T1 검사 및 Iris/test/lua/tooltip_static_data_runtime_harness.lua.

### Docs

이 계획과 iris_tooltip_supply_closeout.md를 갱신한다. 실행 시 B 문제 정의의 입력/목표/상태도 이 계획과 맞추며, 실제 계약 변경과 완료 상태에 필요한 DECISIONS/ROADMAP/ARCHITECTURE 관련 절만 갱신한다. C 문제/계획 전체를 대신 작성하지 않는다. 표현 환류가 있으면 기존 composition 계약·품질 기록에 영향만 남긴다.

### Config

기존 s2_supply_contract.json, T1/T2 소비 schema와 실행 계약의 실제 관련 절만 확인한다. 새 입력 상태나 표시를 전달하는 최소 변경은 허용하나 무결성 검사를 약화하거나 검증 의무를 숨기지 않는다. 일반 strict finalization 요구를 수정해 후보를 production으로 가장하지 않는다.

### Generated Artifacts

기존 .tmp/tooltip 아래 공급·후보·설치·package 결과를 공유한다. 필요한 하위 이름은 역할에 따른 짧은 이름을 쓴다. 새 corpus는 표현 owner 수정 시에만 재생성한다. 과거 r6/sealed 자료는 보존하며 새 proof tree를 만들지 않는다.

## 6. Planned Changes

아래 Change는 독립 Gate·승인 단계가 아니다. 가능한 구현은 함께 진행하고 §12의 세 결과를 한 closeout에서 확인한다.

### Change 1 — 검수된 입력을 기존 공급 경로에 연결

**Purpose:** B/C 공통 corpus를 선택하고 옛 r6 전용 매핑을 교체한다.

**Files:** supplier, description reader/model, T1 adapter/계약.

**Implementation Notes:**
- 저장 결과를 reader로 읽어 명시된 입력을 확인한다. 기존 corpus metadata와 검수 기록을 사용하고 새 봉인 절차를 요구하지 않는다.
- Compact의 원문을 변경 없이 공급하고 상태/reason 및 의미 참조·상세 연결을 offline 경계에 보존한다. 런타임에는 표시·선택에 필요한 자료만 전달한다.
- T는 기존 owner/admission 지원 집합, D는 새 corpus 집합이다. 기존 검증을 재사용해 T∩D의 공급, T-D의 정당한 부재, D-T의 범위를 구분한다. 2,280/175 같은 과거 값이나 Lua 출력 key만으로 현재 권한을 확정하지 않는다.
- 새 absent reason을 손실 없이 표현한다. r6로 되돌리는 fallback, 다른 locale의 문장 대체, load failure 은폐는 금지한다.
- C에 동일 입력의 expanded와 관계를 읽을 좌표를 제공한다.

**Validation:** 기존 통합 검사에서 정확한 원문 공급·locale·상태·잘못된 입력 거부를 함께 확인한다. 착수 테스트나 별도 census Gate는 만들지 않는다.

### Change 2 — 네 역할과 S4 후보 선택을 연결

**Purpose:** 각 계층 입력이 자신의 표시 행과 후보를 소유한다.

**Files:** T1/T2 projection, L4 소비 연결, static lookup/selector.

**Implementation Notes:**
- S1은 소분류, S3은 획득 장소로 유지하고 새 DVF compact에 섞지 않는다.
- S4는 유효한 레시피·우클릭 행동·자유 조리 후보를 모두 포함할 수 있어야 한다. 하나의 레시피 전용 companion만으로 세 종류 지원을 완료했다고 주장하지 않는다.
- 정확한 L4 의미를 바꾸지 않고 표시용 후보 전달·label·선택만 수정한다. 종류를 고정 순환하거나 세 항목을 동시에 표시하지 않는다. 분포·가중치의 새 정책을 임의 추가하지 않는다.
- 기존 유효한 선택 수명을 재사용하며, 표시 중에는 선택을 유지하고 아이템/열기 단위의 기존 갱신 시점에 다시 선택한다. 매 프레임 재추첨하지 않는다.
- 후보가 없으면 S4 정상 부재다. 로드 오류나 지원하지 않는 종류를 후보 없음으로 숨기지 않는다.
- 기존 S2-only 계약이 S1/S3/S4 원문 불변을 요구하면 유효한 원문·의미 보존을 기본으로 한다. 실제 S4 연결/표시 correction은 필요한 필드와 영향만 명시적으로 확장하며 S2-only라는 이름으로 다른 변경을 숨기지 않는다.

**Validation:** 같은 통합/Lua harness에서 세 종류의 후보 연결, 한 개 선택, 수명 안정성과 부재를 확인한다. 난수 결과를 보기 위한 반복 게임 실행이나 통계 검사를 만들지 않는다.

### Change 3 — 실제 네 줄 표시와 폭 처리

**Purpose:** 모든 역할을 읽을 수 있는 화면 최대 네 줄 Tooltip을 만든다.

**Files:** IrisAltTooltip.lua 및 필요한 lookup, 표현 결함의 실제 producer.

**Implementation Notes:**
- 현재 wrapRow의 다중 화면 줄 누적을 수정한다. 실제 폰트 측정과 화면 경계 안에서 적절한 폭·배치를 선택하고 정상적인 읽기 크기를 유지한다. 360 폭 같은 현 구현 상수를 불변 계약으로 삼지 않는다.
- 줄 수만 4로 제한해 나머지를 버리거나 clipping, 말줄임, 폰트 축소로 해결하지 않는다. 원문 한 줄 표시가 불가능한 실제 사례는 fit 실패로 남긴다.
- 긴 DVF 문장 자체가 원인이면 composition의 공통 개요·어휘·배치 규칙에서 최소 수정하고 필요한 독립 용도/조건을 actual expanded에 보존한다. B에 아이템별 요약 DB를 만들지 않는다. 새 결과를 C에도 같은 입력으로 인계한다.
- S1/S3/S4의 문구 문제는 각 표시/생산 owner에서 해결하며 DVF에 다른 계층 문장을 생성시키지 않는다.
- 장문뿐 아니라 화면 가장자리·locale·정상 부재에서도 겹침과 역할 침범을 확인한다. 모든 가능한 화면 설정을 자동 지원한다고 주장하지 않는다.

**Validation:** 기존 harness의 다중 wrap 허용 기대를 네 줄·원문 보존·선택 행 기준으로 바꾸고 실제 PZ 관찰과 구분한다. 별도 폰트 측정 앱이나 새로운 품질 Gate는 만들지 않는다.

### Change 4 — 동일 후보의 설치·관찰·C 인계

**Purpose:** 데이터 파일 생성에서 끝내지 않고 최종 소비까지 확인한다.

**Files:** 기존 candidate/install/package 경로, runtime harness, closeout.

**Implementation Notes:**
- 저장소 내부 후보 경로를 우선 재사용한다. 같은 공급/static/L4 자료로 staging·package·조회 결과를 확인한다.
- 기존 후보가 runtime 변경을 결속하지 못하면 필요한 기존 source binding을 확장한다. 무관한 strict lifecycle 전체 재실행을 기본 경로로 바꾸지 않는다.
- 실제 관찰할 후보를 식별 가능하게 인계하고 KO/EN 네 줄, Alt, S4, 장문과 부재를 같은 후보에서 확인한다.
- C 완료를 B 구현의 착수 Gate로 두지 않는다. 실제 사용자 current의 공동 활성화는 C가 같은 corpus를 소비할 준비가 된 뒤 별도 실행 범위에서 한다. 후보 검증과 current 전환을 구별한다.
- 문서 갱신 때문에 소비가 깨지는 실제 결합만 바로잡으며 historical replay를 예방적으로 실행하지 않는다.

**Validation:** §7의 최종 묶음과 실제 PZ 관찰을 공유한다. 범위가 충족되면 추가 confidence 실행 없이 종료한다.

## 7. Validation Plan

### Automated Validation

실제 변경에 적용되는 기존 계약을 관련 절만 확인한다. 과거 명령·heavy 분류·새 문서 작성 자체는 검사 추가 근거가 아니다. 적용되는 필수 의무와 충돌하면 해당 범위와 근거를 공개하고 우회하지 않는다. 일반 production finalization이 미충족이면 후보 성공과 별도로 표시하며 전체 production 완료를 주장하지 않는다.

기본은 마지막에 아래 **기존 통합 node 한 묶음**이다. 이 node에 필요한 공급·S4·물리 줄 수의 최소 회귀 사례를 통합한다.

~~~powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration --basetemp .\.tmp\tooltip\accept -q -s
~~~

- 이 기존 경로가 실행하는 Lua syntax/harness/package 결과를 공유하고 같은 검사를 밖에서 반복하지 않는다. Lua 변경의 필수 명령은 아래이며 통합 실행에서 성공하면 충족된다.

~~~powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
~~~

- 통합 node가 직접 다루지 않는 projection/CLI finalization 코드를 실제 수정한 경우에만 기존 test_projection/test_cli_finalization 중 해당 node를 같은 pytest 호출에 추가한다.
- Composition 코드를 수정한 경우에만 기존 Iris/build/description/v2/tests/test_layer3_description_composition.py를 같은 마지막 묶음에 추가한다. 문제 1 코드는 본 계획의 일반 수정 대상이 아니다.
- 기존 통합 node에 필요한 후보 생성·equality 확인은 공유한다. 새 full Run A/B + comparator, 별도 결정성 suite, helper 검사 체계, 과거 A/문제 1~3 재수락을 추가하지 않는다.
- 원문 읽기·필요한 생성·차이 확인은 구현 중 수행할 수 있다. 자동 테스트는 마지막에 묶고 실패 수정이나 추가 변경으로 근거가 무효화된 경우만 필요한 범위를 재실행한다.
- 30~60초 간격으로 실행 상태·출력을 확인하고 무한 반복·진행 정체·비정상 장기 실행 시 해당 프로세스를 중단한다. 원인 확인 없는 자동 재시도나 성공 간주는 금지한다.
- 정확한 명령 exit 0만 PASS다. 필수 tooling 부재는 BLOCKED다. 별도 Java/JS 변경 없이 Gradle/Biome를 추가하지 않는다.
- 중복 helper·검증 결과 파일을 만들지 않고 같은 후보/검사 결과를 사용한다. 외부 reviewer가 필요하면 Codex Reviewer를 사용하며 독립 검토 자체를 기본 Gate로 추가하지 않는다.

### Manual Validation

동일한 실제 PZ 후보에서 아래 위험을 함께 관찰한다. 고정 아이템 수·스크린샷 수·반복 횟수는 요구하지 않는다.

- KO/EN에서 화면 최대 네 줄, S2 한 줄, 각 계층 역할, Alt 활성/해제.
- 긴 복합 용도, 일반 짧은 설명, compact 부재/다른 행 존재, S4 후보 부재.
- 레시피·우클릭 행동·자유 조리의 선택된 실제 표시와 읽는 동안의 안정성.
- 지원 화면 환경에서 화면 가장자리·폭·겹침·잘림·가독성.
- 필요한 상세가 C용 expanded에 실제 남고 원문 수정 시 두 소비자의 입력이 일치하는지.

실제 PZ 환경이 없으면 후보와 확인할 동작을 구체적으로 준비해 사용자 관찰을 요청한다. 가상 폰트 harness를 게임 관찰로 대체하지 않는다.

### Validation Limits

전체 모드 호환성, 모든 해상도·배율, 장기 세션·멀티플레이 전수, C Menu, current 공동 활성화, release는 이 후보 검증에 포함하지 않는다. 관찰하지 않은 환경은 한계로 명시한다.

## 8. Risk Surface Touch

### Authority Surface

새 corpus를 공급 입력으로 선택하며 필요한 기존 공급/후보 계약만 수정한다. Layer 2·L4/QG 의미 권한과 Tooltip 조립 책임은 유지한다.

### Runtime Behavior Surface

실제 폭·배치·wrap 및 필요한 S4 선택 연결이 변경된다. 기존 무제한 wrap의 동작 동일성을 성공 기준으로 삼지 않는다.

### Compatibility Surface

Lua lookup·companion·package의 필요한 schema 변경을 같은 후보에서 맞춘다. 다른 consumer를 무조건 변경하지 않는다.

### Sealed Artifact Surface

r6와 historical T1/T2/L3-06은 보존한다. 새 후보를 기존 sealed production으로 가장하지 않는다.

### Public-Facing Output Surface

새 compact와 실제 네 줄 표시, S4의 유효 후보가 달라질 수 있다. 내부 ref·reason·debug 정보를 본문으로 출력하지 않는다.

## 9. Risk Analysis

### Architecture Risk

DVF가 S1/S3/S4까지 생산하거나 runtime이 문장을 재작성할 위험은 adapter/Tooltip/L4 owner 분리로 막는다. 정규화된 모드 데이터도 같은 계약으로 소비하는 구조를 유지하되 모드 입력 구현을 확대하지 않는다.

### Runtime Risk

문장 공급 성공과 한 줄 fit은 다르다. 실제 폭에서 실패하면 공통 문장 또는 renderer 원인으로 처리하고 글자 절단·숨김으로 통과시키지 않는다. 후보 재추첨이 깜빡임을 만들지 않게 한다.

### Compatibility Risk

옛 S2-only 보존 기대와 필요한 S4/renderer correction이 충돌할 수 있다. 실제 수정 필드만 새 후보 계약에 반영하고 다른 계층의 사실·지원 집합은 바꾸지 않는다.

### Regression Risk

T-D 손실, absence 오분류, stale companion, locale mismatch, 다른 writer의 Tooltip 덮어쓰기, 기존 dirty 변경 손실을 기존 통합 경계에서 확인한다. 예전 실행 환경·개수·PASS를 새 결과로 복사하지 않는다.

## 10. Rollback Plan

실제 변경할 파일과 후보 설치 대상의 시작 bytes만 보존한다. 실패 후보는 current로 선택하지 않는다. 저장소 reset/clean이나 타 작업 변경 복원은 하지 않는다. 동시 변경이 있으면 대상 덮어쓰기를 멈추고 이번 변경만 구별한다.

실제 전환을 별도 범위에서 수행한 경우에만 static·companion·관련 selector를 일관된 이전 버전으로 복원한다. 새 compact가 없다는 이유로 런타임에서 옛 primary_use/r6 문장을 fallback하는 것은 rollback이 아니다. 표현 환류 시 producer와 corpus를 일치하는 상태로 유지한다.

## 11. Governance Constraints

- Philosophy의 근거·중립성·같은 사실의 다른 깊이, Alt와 화면 최대 네 줄을 준수한다.
- PZ runtime은 Lua이며 Hub & Spoke/SPI 경계를 유지한다.
- 계획상 owner approval은 사용자의 사전 승인으로 처리한다. 도구·플랫폼의 별도 보안/권한 요구는 우회하지 않는다.
- 저장소 밖 경로는 이 계획에 필수 입력으로 채택하지 않았다. 사용자의 기존 파일/게임 폴더를 탐색하거나 외부 workspace를 만들지 않는다.
- 문서·검증보다 구현과 실제 표시를 우선하며 필요한 결과가 충족되면 종료한다.
- 사용자가 확정한 생존 모드 공개 범위에 따라 치트 관련 문구를 다시 도입하지 않는다.
- 계획 작성 이후 2026-09-11 사용자가 구현을 명시적으로 지시했다. 구현·자동 검사·실제 관찰·current/release는 각각 실제 결과로 기록한다.

## 12. Expected Closeout State

목표는 **B 후보 구현·통합 및 실제 표시 complete**다. 다음 세 결과를 하나의 최종 수락으로 확인하며 별도 Gate/파일을 요구하지 않는다.

| 결과 | 완료 기준 |
| --- | --- |
| B1 공급·소유권 | 새 compact와 정확한 상태/참조가 기존 Tooltip 경로로 전달되고 지원 차집합·오류가 올바르게 처리된다. DVF/Tooltip/L4 책임이 유지된다. |
| B2 실제 표시 | 적용되는 최소 자동 검사와 실제 KO/EN PZ 관찰에서 최대 네 줄·S2 한 줄·Alt·세 종류 S4 후보 연결·선택 안정성·가독성을 확인한다. 알려진 overflow/문장 결함이 없다. |
| B3 인계·범위 | C가 같은 최종 corpus/reader/expanded 관계를 소비할 수 있고 후보·테스트·관찰 환경·남은 production/current/C 책임이 기존 closeout에 명확하다. |

코드·자동 검사만 끝나고 PZ 관찰이 없으면 implemented_only이며 실제 표시 완료는 아니다. 필수 구현이 남으면 partial, 입력/도구가 막은 의존 범위는 blocked로 구분한다. 독립 작업은 계속하며 미완료를 이유 없이 종료하지 않는다.

C 완료나 실제 current 공동 활성화를 B 후보 구현의 선행 조건으로 만들지 않는다. 반대로 후보 검증을 일반 strict production finalization·C·사용자 current·release 완료로 확대하지 않는다. 새 corpus로 통합된 준비 결과와 실제 사용 상태를 각각 보고한다.

## 13. 실행 기록 — 2026-09-11

사용자 구현 지시와 owner 사전 승인을 적용했다. 새 compact corpus 원문/상태/상세 연결, S3 획득 장소, S4 세 종류 중 한 후보, 한 행당 한 화면 줄 renderer, 기존 후보 install/package를 구현했다. 기존 strict T1의 S3/S4 두 L4 매핑을 후보에서 수정한 사실을 계약과 provenance에 명시했다. Corpus/composition 생산 코드는 변경하지 않았다.

최종 integration은 첫 선택적 segment 필드 처리 실패를 수정한 뒤 exact command exit 0(1 passed, 98.49초)이었고 Lua syntax/harness/package도 같은 실행에서 exit 0이었다. T2 projection의 기존 node는 최초 묶음에서 통과했으며 해당 묶음의 전체 exit 1과 분리해 기록했다. 추가 confidence 실행은 하지 않았다.

B1과 B3 후보 인계를 확인했고 B2는 자동 표시 계약만 확인했다. 실제 KO/EN PZ 버전/화면/배율 관찰이 없어 implemented_only다. 동일 ZIP은 `.tmp/tooltip/preview/Iris.zip`이며 product/input/명령/관찰 동작과 남은 current/C/production 경계는 [closeout](iris_tooltip_supply_closeout.md)의 최신 절을 따른다. r6와 이전 결과·외부 실행 제안은 보존하되 v3 실행 근거로 승계하지 않았다.
