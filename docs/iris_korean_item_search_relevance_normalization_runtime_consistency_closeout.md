# Iris 아이템 검색 구현 결과

> 이번 후속 수정 상태: 완료 — package/4의 붙여넣기 후 분류 자동 선택, 검색어 삭제 후 초기 화면 복귀, 검색 중 분류 직접 탐색에 대해 사용자가 “잘 나와”라고 확인했다. 사용자 관찰로 확인한 이 범위에서 closeout하며 원계획 전체 환경·성능 검증 완료로 확대하지 않는다. 아래 package/1·2·3 및 최초 구현 기록은 predecessor 이력이다. 일반 기능 수정에 보편적 Clean-Checkout A/B를 자동 부과하지 않는 현행 DECISIONS를 적용한다.

## 검색어 삭제 시 초기 화면 복귀 — 최종 요청 반영

- global 검색어를 지우거나 공백만 남기면 대분류 목록만 유지하고 대분류·소분류 선택, 하위 목록, detail·variants 및 하위 검색 필터를 비운다. 앞선 package/3의 선택 분류 유지 동작을 이 사용자 요청으로 대체했다. 붙여넣기·직접 입력의 분류 자동 선택은 유지한다.
- 분류를 직접 클릭해 global 검색을 종료할 때는 클릭한 분류로 이동한다. 소분류 callback의 category를 clear 전에 보존하고, clear 후 해당 목록과 선택을 다시 연결한다. 아이템 직접 열기의 분류 선택도 동일한 선택 함수를 사용한다. 뒤늦은 clear callback이 이전 탐색을 되살리지 않는다.
- 마지막 검사: 기존 Browser focused 명령 exit 0, 5.347초; Lua syntax 명령 exit 0, 179 files. 새 요청의 clear·필터 초기화·지연 callback·분류 직접 이동을 기존 harness의 같은 통합 사례로 검사했다. 앞선 package/3 검사 이후의 재실행은 추가 confidence 확보가 아닌 사용자 요청으로 달라진 코드에 대한 최종 검사다.
- 최종 패키지: `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot .\.tmp\package\4 -Zip -PackageApplicability current_runtime_payload` exit 0. 설치 폴더는 `.tmp/package/4/Iris`, ZIP은 `.tmp/package/4/Iris.zip`이다. 기존 package 자체 검사를 재사용했고 별도 검증 artifact나 외부 설치본을 만들지 않았다.
- 사용자 PZ 확인: 위 package/4에 대해 안내한 세 항목(정확한 이름 붙여넣기와 분류 이동, 전체 검색어 삭제와 초기화, 검색 중 분류 직접 클릭)이 정상이라는 응답을 받았다. 에이전트가 직접 실행한 관찰로 표현하지 않으며, 한글 조합 확정 지연 해소·모든 환경·성능 확인으로 확대하지 않는다. 확인 기록만 갱신하고 추가 테스트나 재패키징은 하지 않았다.

## 붙여넣기 대상 분류 자동 선택 — package/3 이력

- 사용자 후속 요청: 붙여넣기 후 유지되는 분류 목록에서 대상 아이템의 대분류·소분류도 자동 선택한다. 붙여넣기 전용 키 이벤트를 추가하지 않고 같은 global 입력 반영 경로에 적용하므로 직접 입력에도 동일하게 동작한다.
- 대상 결정: 명시적 FullType exact → 표시 이름 exact → 기존 공백 정규화 이름 exact 순서로 탐색 위치를 결정한다. 해당 exact 집합이 같은 기존 `primaryLocation`을 가리킬 때만 선택한다. 동명·공백 제거·ID 대소문자 충돌로 위치가 다르거나 부분 일치/무결과만 있으면 이전 선택을 유지한다. 검색 결과의 이름 우선 순위, distinct FullType 및 global/local 범위는 변경하지 않는다.
- 구현: Query의 방금 완료된 검색 후보·document·snapshot을 재사용하며 검색/정렬/document 생성을 반복하지 않는다. Data의 내부 adapter는 query·generation·locale이 맞지 않으면 위치를 반환하지 않는다. Controller는 분류와 소분류의 선택·스크롤만 맞추고 검색어·전체 결과·detail 선택은 그대로 둔다. 이전 소분류 필터가 목표를 가리면 그 필터를 비우며, 늦은 callback도 선택 표시를 유지한다. clear 이후에는 자동 선택된 분류에서 browse를 이어간다.
- 마지막 검증 묶음: 아래 기존 Browser focused 명령 1회 exit 0, 5.608초. 같은 harness 안에서 분류 간 이동, 같은 분류 내 소분류 이동, exact 이름/ID, 동명·정규화·case collision, 부분/무결과 선택 유지, global 결과 보존, 필터 해제, clear, stale owner를 검사했다. 기존 KO/EN sweep과 Tooltip 회귀도 같은 실행을 재사용했다. 사용자 지정 Lua syntax 명령은 exit 0, 179 files. 중간 테스트·새 runner·별도 검증 artifact는 만들지 않았다.
- 패키징: `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot .\.tmp\package\3 -Zip -PackageApplicability current_runtime_payload` exit 0. 기존 package 자체 검사를 거쳐 `.tmp/package/3/Iris`와 `.tmp/package/3/Iris.zip`을 생성했다. 앞선 패키지는 덮어쓰지 않았다. 외부 설치 경로에 접근하거나 실제 PZ를 실행하지 않았다.
- 실제 확인이 남은 범위: 새 패키지에서 정확한 아이템 이름을 붙여넣었을 때 분류 두 단계가 선택되는지. 사용자가 설명한 마지막 한글 음절의 조합 확정 지연은 별도 엔진 입력 경계이며 이번 분류 이동 수정으로 해결했다고 주장하지 않는다.

## PZ 입력·탐색 피드백 후속

- 사용자 관찰: 첫 `망치` 입력은 `망`에 해당하는 넓은 결과가 남고 공백/방향키 등 후속 입력에서 정상화됐다. 붙여넣기도 결과 반영이 누락됐다. 전체 검색 중 대분류·소분류가 사라져 분류 탐색을 사용할 수 없었다. 목록 내 검색, 기존 ID 조회, 재열기·언어 변경은 정상이라고 확인했다.
- 수정: PZ `ISCraftingCategoryUI`의 기존 방식처럼 `getInternalText()`의 edit buffer를 읽고 panel update에서 마지막 적용 문자열과 비교한다. callback보다 늦은 edit/누락된 paste callback은 다음 update에서 반영한다. 동일 입력은 재검색하거나 선택을 지우지 않는다. 게임 전역 입력 함수를 교체하지 않는다.
- 탐색: global 결과는 item list만 교체한다. 대분류·현재 소분류를 유지하고 해당 항목을 누르면 global query를 비운 뒤 browse로 돌아간다. clear는 유효한 기존 분류 선택을 복원하며, 선택이 없으면 하위 목록·detail을 비운다. SetText의 동기/지연 중복 callback이 복원된 탐색을 다시 지우지 않도록 처리한다.
- 동명 항목: 전체 검색의 대형 망치 두 줄은 distinct FullType 유지 동작이다. 별도의 variants row를 global에 추가하지 않았다. 기존 local folding 및 detail의 `Variants (n)`은 유지한다.
- 검사: 기존 Browser focused method 1회 exit 0, 6.313초. KO/EN exact sweep과 기존 회귀를 재사용하며 early callback, stale getText, 무callback paste, 중복 callback, 분류/소분류 직접 복귀를 같은 harness에 포함했다. 사용자 지정 Lua syntax는 exit 0, 179 files. 실제 Kahlua/IME가 해결됐다는 증거로 확대하지 않는다.
- 수정본 전달: `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot .\.tmp\package\2 -Zip -PackageApplicability current_runtime_payload` exit 0. 설치 폴더는 `.tmp/package/2/Iris`, ZIP은 `.tmp/package/2/Iris.zip`이다. 기존 package 검사 및 manifest 기반 검색 파일 6개의 source/package 일치를 확인했다. package/1은 덮어쓰지 않았다. 수정본에서 재확인할 인게임 범위는 첫 한글 입력·붙여넣기·분류 탐색 복귀이며, 이미 정상으로 관찰한 범위를 별도 전수 재검사 의무로 늘리지 않는다.

> 후속 패키징 완료: 사용자 요청으로 저장소 내부 `.tmp/package/1/Iris`와 `.tmp/package/1/Iris.zip`을 생성했다. 아래 최초 실행의 package BLOCKED 기록은 이 후속 결과로 해소됐다. 기존 package script가 `.tmp/package/`의 격리 출력만 추가 허용하도록 수정했으며 source/상위 경로 겹침 및 reparse 거부는 유지했다. `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -OutputRoot .\.tmp\package\1 -Zip -PackageApplicability current_runtime_payload`는 exit 0으로 끝났고 기존 payload/package 검사를 통과했다. 기존 package manifest를 사용해 검색 변경 파일 6개의 포함과 source/package byte 일치도 확인했다. 새 검증 authority나 별도 proof artifact는 만들지 않았다. 실제 설치·PZ 관찰은 수행하지 않았다.

> 상태: `implemented_only` — source 구현·focused acceptance·Lua syntax 완료. 전체 계획 complete 아님.
> 날짜: 2026-08-31
> 계획: `iris_korean_item_search_relevance_normalization_runtime_consistency_plan.md`

## 구현 subject와 범위

기준 HEAD는 `f8da88748b09c67f0adb89daa6b28f543500bc48`이다. 결과는 이 HEAD 위의 작업 트리 변경이며 새 commit, 설치본, current package 또는 release를 발행하지 않았다. 기존 사용자 변경인 `docs/PROBLEM_TEMPLATE.md`, `docs/iris_menu_display_interaction_stability_problem.md`는 수정하지 않았다. 계획의 owner approval은 이번 사용자 프롬프트로 사전 승인됐다.

`IrisBrowserSearch`가 순수 Lua lexical 비교를 소유한다. ProjectionBuilder의 초기 생성과 Query의 locale 교체가 같은 document 함수를 사용한다. exact FullType 및 item 객체 identity는 그대로 유지하고, 비교용 소문자·공백 제거 값을 identity key로 사용하지 않는다. Search에 전역 cache나 generation owner를 추가하지 않았다.

| 항목 | 채택한 동작 |
|---|---|
| 이름 관련성 | ASCII case를 무시한 원본 표시 이름 exact → U+0020 제거 후 이름 exact → 이름 literal/공백 제거 부분 일치 → global ID-only 일치 |
| 같은 tier | 원본 displayName → case-sensitive exact FullType. local의 isPrimary는 metadata로만 보존 |
| 공백 | 양쪽 표시 이름과 query의 U+0020을 비교용으로 제거. 한국어뿐 아니라 다른 표시 이름에도 동일 적용. 숫자·기호는 유지 |
| global ID | 앞뒤 U+0020만 정리하고 내부 공백·숫자·구두점은 literal 유지. 명시적 FullType도 별도 최상위 예외 없이 이름 우선 순서 적용 |
| global/local | global은 active item snapshot 전체·display/ID. local은 현재 category/subcategory의 기존 folded 대표 row·display-only. variants/대표 FullType/grouping 유지 |
| empty | global API는 빈 결과와 prefix 폐기, UI는 선택 없는 browse로 복귀하며 item/subcategory/detail 비움. local은 원래 primary 우선 browse 순서 복원 |
| prefix | 같은 snapshot에서 compact-name와 ID 양쪽의 prefix 단조성이 성립할 때만 재사용. 후보는 기본 이름 순서로 유지하며 새 query로 tier 재계산 |
| UI owner | panel update에서 generation/loader locale의 scalar만 비교하고 변경 시에만 목록 재조회. 동일 query의 locale/rebuild 전환, reset, reopen 연결 |
| 선택 | 실제 PZ raw event payload와 기존 wrapped payload를 모두 exact identity로 해석. 검색/clear 후 이전 index·variants·detail을 유지하지 않음 |

초성(`ㅁㅊ`), 어순 변경(`망치 대형`), KO에서 EN 표시 이름 alias(`Club Hammer`), Unicode canonical equivalence, typo/fuzzy는 미채택이다. 이 입력들의 미해소를 전체 한국어 입력 문제 해결로 표현하지 않는다. 새 안내 UI, local ID 확대, semantic ranking은 도입하지 않았다.

TranslationLoader/Resolver는 수정하지 않았다. 기존 loader `init()`의 normalized locale 변경을 소비한다. loader에 전달되지 않은 실제 게임 언어 변경이나 IME composing을 처리했다고 주장하지 않는다.

## 입력과 기대값

구현 전 repository 번역을 read-only로 집계했다. 같은 exact FullType 중복은 마지막 항목을 사용하고 값이 충돌하면 harness에서 실패한다. case-sensitive identity를 유지한다.

| locale | 원본 줄 | deduplicated exact FullType | unique DisplayName/query | SHA-256 |
|---|---:|---:|---:|---|
| KO | 2,017 | 2,007 | 1,661 | `0ea2f9f5747a5845347ccdbb02e48948f3b3b6218d971800dd8d77afe4f2c5de` |
| EN | 1,974 | 1,974 | 1,615 | `98066208a95aad2113326d4f7b7d022ee3658e31f721802af9d43ab38c1de488` |

KO의 10개 중복 key는 같은 값이고 EN 중복은 0이다. 각 locale의 전체 exact-name sweep은 기존 Browser harness 한 실행에 포함한다. 실제 active `getAllItems()` 분모는 미측정이며 번역 모집단으로 대체하지 않는다.

KO 파일은 BOM이 있는 UTF-16BE이고 EN은 ASCII/UTF-8 호환 입력이다. 기존 harness 안의 test-only reader가 KO의 BMP 문자를 UTF-8로 읽는다. 이는 고정 corpus 입력 처리이며 Iris runtime normalizer, PZ translation parser, 새로운 validator가 아니다.

필수 target은 `Base.Hammer`의 `망치`/`  망치  `, `Base.Sledgehammer`·`Base.Sledgehammer2`의 `대형 망치`/`대형  망치`/`대형망치`다. 별도 구성 사례로 공백 제거 collision, 이름/ID collision, `Base.LemonGrass`·`Base.Lemongrass`, secondary exact와 primary partial, local 동명 variant를 검사한다. `형`·`해머` 부분 검색, `A-1 (B)` literal, `A1B`·`대형 망치 없음` 무결과가 품질 기대값이다. 기대값은 production comparator에서 생성하지 않는다.

Before 표시는 조사한 predecessor의 literal filter와 원본 이름/FullType 정렬을 같은 corpus에 적용한 source-derived model이다. predecessor runtime 실행이나 실제 PZ baseline 관찰이 아니다. 최종 harness의 `SEARCH_CASE` 출력에서 같은 query/target의 결과 수·순위를 비교한다.

| KO query / target | Before 결과 수·target 순위 | After 결과 수·target 순위 | 판정 |
|---|---|---|---|
| `망치` / Base.Hammer | 6 / 6 | 6 / 1 | exact 우선순위 해소, membership 유지 |
| `  망치  ` / Base.Hammer | 0 / 없음 | 6 / 1 | 앞뒤 공백 해소 |
| `대형 망치` / Base.Sledgehammer | 2 / 1 | 2 / 1 | 기존 조회 유지; Sledgehammer2도 유지 |
| `대형  망치` / Base.Sledgehammer | 0 / 없음 | 2 / 1 | 연속 공백 해소 |
| `대형망치` / Base.Sledgehammer | 0 / 없음 | 2 / 1 | 띄어쓰기 차이 해소 |
| `Hammer` / Base.Hammer | 6 / 5 | 6 / 5 | global ID 조회 유지 |
| `망치 대형` / Base.Sledgehammer | 0 / 없음 | 0 / 없음 | 어순 변경 미채택·미해소 |
| `ㅁㅊ` / Base.Hammer | 0 / 없음 | 0 / 없음 | 초성 미채택·미해소 |
| `Club Hammer` / Base.ClubHammer | 0 / 없음 | 0 / 없음 | KO EN alias 미채택·미해소 |
| U+0020 세 개 | 0 / 해당 없음 | 0 / 해당 없음 | API 빈 결과; controller는 browse 복귀 검사 통과 |

최종 실제 Lua production 경로에서 KO 1,661 / EN 1,615 query를 실행했고 exact group 누락·순위 위반은 각각 0이었다. 품질 구성 사례와 callback/owner/identity 검사는 같은 실행에서 통과했다. production 검색의 입력 source는 계속 `getAllItems()`이며 위 번역 파일은 test corpus로만 사용한다.

## 검증과 남은 범위

최종 실행 결과는 아래에 기록한다. 구현 중 중간 테스트, 새 test file/top-level test, 새 runner/registration, proof artifact는 만들지 않았다. 기존 Python 두 wrapper에 60초 subprocess 제한을 적용했으며 중복 harness 실행을 별도 증거로 세지 않는다.

| 범위 | 상태 | 근거/한계 |
|---|---|---|
| 기존 Browser focused acceptance | PASS / exit 0 | 기존 method 1개, 4.523초. KO/EN sweep·필수 공백·부분 검색·identity/copy·atomic replacement·controller/owner 전환과 기존 Tooltip runtime 회귀 |
| 필수 Lua syntax | PASS / exit 0 | 사용자 지정 root script, runtime 179 files. package coverage나 Kahlua 검증이 아님 |
| mandatory Clean-Checkout A/B + comparator | BLOCKED | 계획은 저장소 외 dedicated environment/work/result를 요구하지만 이번 실행 경계에 구체적으로 허용된 외부 경로가 없음. 저장소 내부로 우회하지 않았고 current environment receipt 외부 경로도 열지 않음 |
| 후보 package 생성/검증 | BLOCKED | 현행 package entrypoint는 repository-external output을 요구. 새 외부 출력 루트·기존 설치본 접근이 허용되지 않음 |
| 실제 PZ 입력·선택·상태·사용성 | unvalidated_but_in_scope | 허용된 설치/실행 경로와 동일 candidate package가 없어 미관찰. PZ build, active count, mod/번역 환경, IME callback, latency 모두 미측정 |

실행 subject는 위 기준 HEAD에 이 작업의 source/test delta를 적용한 작업 트리다. 문서 최종 기록은 검사 후 갱신했으며 runtime source는 syntax 성공 이후 변경하지 않았다. Browser harness만 corpus reader를 교정하고 같은 focused 명령으로 다시 실행했다. 정식 command owner는 `Iris/build/ENTRYPOINTS.md`이며 아래는 이번 실행 로그다.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.tmp/uv'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
uv run --no-project --no-config --offline --no-python-downloads --python python python -B .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py BrowserStateSelectionSearchAcceptanceTest.test_actual_standalone_lua_state_and_cache_contracts
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

최종 검증 묶음의 첫 focused 실행과 원인 진단 출력 보강 후 실행은 각각 exit 1이었다. KO UTF-16BE를 줄 단위 일반 텍스트로 읽어 `0/0/0`으로 집계한 test reader 결함이며, 기대 분모/원본/hash를 바꾸지 않고 reader만 교정했다. 이어 같은 focused 실행이 exit 0으로 끝났다. 이 실패 이력을 PASS로 덮어쓰지 않는다. 모든 실행은 수 초 안에 끝났고 60초 timeout·강제 중단은 발생하지 않았다. 검증 출력·receipt용 새 디렉터리는 만들지 않았으며 `.tmp/uv`는 도구 cache일 뿐 검증 authority가 아니다.

`required_validations.json`의 기존 Browser acceptance와 single-pass membership은 유지했다. source closure는 Python current-route dependency를 소유하며 이번에는 Python module/import graph·registry membership·semantic payload authority를 변경하지 않는다. 향후 full gate는 이 구현의 최종 exact tracked subject를 대상으로 새 결과를 얻어야 하며 이전 PASS를 상속하지 않는다.

Classification, DVF/Layer3 pointer·generation·KO/EN body, QG/UseCase, Tooltip fixed/Recipe payload를 수정하거나 producer를 재실행하지 않았다. 전체 non-search regression과 package 비간섭의 machine PASS는 full gate/package가 남아 있어 주장하지 않는다. 외부 Reviewer는 사용하지 않았으며 independent review PASS를 주장하지 않는다.

필수 full gate, package, 실제 PZ 검증이 남았으므로 계획 전체 상태는 `implemented_only`다. owner 사전 승인은 관찰 결과를 대신하지 않는다. 추가 confidence 확보용 검증이나 봉인 작업을 만들지 않고 이 제한을 유지한다.
