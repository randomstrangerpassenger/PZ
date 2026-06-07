아래 최종 로드맵은 두 입력 로드맵의 항목을 ROADMAP\_TEMPLATE 구조에 맞춰 종합한 것입니다. 근거 문서: `ROADMAP\_IRIS\_REFACTOR.md`, `iris-codebase-refactoring-roadmap.md`, `ROADMAP\_TEMPLATE.md`   



\# Iris Codebase Refactoring Final Roadmap



> 상태: Draft

> 기준일: 2026-06-07

> 범위: Iris 모듈 및 Iris build/source/artifact/runtime cleanup 범위

> 종합 방식: 공통 항목은 병합, 한쪽에만 있는 항목은 단독 범위로 유지, 충돌 항목은 별도 판정 필요로 표시



\---



\## 1. Problem Statement



Iris는 이전 리팩토링을 통해 런타임 API, Browser, Layer 3 chunking, ProtectedCall, module bootstrap, 일부 build infra를 정리했으나, 후속 구조 압력이 남아 있다.



공통 문제 축:



\* `Iris/build/description/v2/tools/build/` 하위 build script군이 과도하게 커져 active source, reproduction evidence, one-shot script, legacy script의 경계가 불명확하다.

\* 공통 helper, path, JSON/JSONL I/O, hash/report writer, version/path 관리가 일부만 중앙화되어 있다.

\* generated runtime Lua, output JSON, staging evidence, package copy의 source/artifact/tracked 정책이 단순하지 않다.

\* runtime/build-time authority 분리, determinism, FAIL-LOUD validation, sealed artifact 보존을 유지한 상태로 정리가 필요하다.



로드맵 A에서 강조한 문제:



\* 282개 Python script, 24,672 LOC 누적.

\* `build\_identity\_fallback\_batch1\_clothing\_surface\_reuse.py`가 사실상 공용 모듈로 사용됨.

\* 254개 `ROOT` bootstrap, 97개 `sys.path.insert` 반복.

\* 5개 compose module의 import dance.

\* `staging/` 종료 라운드 누적.

\* Generator/Renderer debug noise와 IrisMain helper 잔존.



로드맵 B에서 강조한 문제:



\* description v2 build script는 269개로 측정됨.

\* `quality\_gates.py` 단일 파일 집중.

\* Recipe / Right-click evidence pipeline의 stage skeleton 중복.

\* version/path drift.

\* generated artifact / Git tracking policy 불명확.

\* runtime UI 표현 파일 책임 혼재.

\* test discovery와 validation command surface 정리 필요.



\---



\## 2. Current State



\### 공통 현재 상태



\* Iris는 Lua 기반 위키형 정보 모드이며, Python build pipeline은 offline authority/generation/validation을 담당한다.

\* Layer 3 runtime data는 chunk-only 구조로 전환되어 있고 generated Lua는 수동 편집 대상이 아니다.

\* build script inventory는 존재하지만 active, legacy, reproduction, artifact boundary가 충분히 명확하지 않다.

\* build/runtime 변경은 determinism, regression, compatibility, public-facing behavior claim boundary 안에서만 성공을 주장할 수 있다.



\### 로드맵 A 기준 상태



\* `Iris/build/description/v2/tools/build/`에 282개 Python script.

\* `Iris/build/description/v2/staging/`에 11개 top-level category.

\* `Iris/build/description/v2/tests/` 기준 380 tests OK baseline.

\* Pulse 의존성 없음, Iris standalone 유지.

\* chunking 전략과 no-op API 폐기 결정은 봉인 상태.

\* build tool determinism 검증은 phase별 golden SHA 비교에 의존.



\### 로드맵 B 기준 상태



\* `Iris/build/tools/common/`에는 `io.py`, `stage\_runner.py`, `versions.py`가 있으나 모든 script가 소비하지 않음.

\* `Iris/build/build\_import\_contract.md`는 direct script execution을 compatibility baseline으로 둔다.

\* `tools/build/\*.py`는 filename glob으로 archive/delete하지 않고 per-file disposition으로 다루도록 고정되어 있다.

\* Pulse namespace compatibility wrapper는 내부 require 조건만으로 삭제할 수 없다.

\* 현재 로드맵은 직접 코드 변경보다 후속 execution scope와 sequencing 정의에 가깝다.



\---



\## 3. Desired Outcome



\### 공통 목표



\* description v2 build script군이 family별 재현성 계약과 공통 helper 소비 경로를 가진 관리 가능한 build surface가 된다.

\* build/source/artifact/runtime boundary가 문서와 코드에서 일관되게 읽힌다.

\* generated runtime Lua와 output artifact는 generator-owned 상태를 유지한다.

\* runtime/build-time authority 분리, FAIL-LOUD validation, determinism gate가 유지된다.

\* validation command surface와 test discovery policy가 현재 import contract와 충돌하지 않는다.



\### 로드맵 A에서 채택 가능한 목표



\* build directory를 active tool과 archive 대상이 구분되는 구조로 정리한다.

\* 새 round 추가 시 batch1 script를 library처럼 import하지 않는다.

\* compose pipeline import path를 단일 계약으로 정리한다.

\* ROOT/sys.path bootstrap 반복을 줄인다.

\* `staging/`은 진행 중 작업 중심으로 정리한다.

\* Generator/Renderer debug noise를 줄이고 IrisMain helper를 spec-driven dispatch로 흡수한다.



\### 로드맵 B에서 채택 가능한 목표



\* `quality\_gates.py`를 gate별 책임과 reporting/CLI 책임으로 분리한다.

\* Recipe / Right-click evidence pipeline은 authority를 섞지 않고 execution skeleton만 공유한다.

\* version/path/output suffix/source path drift를 central manifest 또는 common helper로 줄인다.

\* generated artifact, output, staging evidence, package copy의 Git tracking policy를 명확히 한다.

\* runtime UI 표현 파일은 user-facing behavior를 바꾸지 않는 범위에서 책임을 작게 나눈다.



\---



\## 4. Constraints



\* Iris는 100% Lua 기반 위키형 정보 모드로 유지한다.

\* Iris는 해석, 권장, 비교를 하지 않는다.

\* runtime/build-time authority 분리를 유지한다.

\* FAIL-LOUD validation과 determinism gate를 약화하지 않는다.

\* generated Lua 또는 generated JSON을 손으로 쪼개거나 의미 수정하지 않는다.

\* sealed artifact와 current readpoint를 roadmap 자체로 mutation하지 않는다.

\* `facts → decisions → profiles → render` 흐름, SHA 무결성, `fact\_origin` 추적을 보존한다.

\* Recipe evidence와 Right-click evidence는 동급의 독립 2-track으로 유지한다.

\* public Lua API 또는 compatibility wrapper 제거는 deprecation/release decision 없이 진행하지 않는다.

\* Pulse 의존성 신설 또는 다른 Pulse module/Core 변경을 하지 않는다.

\* user-facing runtime behavior change는 manual in-game QA 없이 성공으로 주장하지 않는다.

\* direct script execution baseline은 별도 판정 전까지 깨지지 않는 계약으로 취급한다.



\---



\## 5. Non-Goals



\* Iris taxonomy, evidence rule, source authority, Layer 3 body policy 재설계.

\* Recipe / Right-click evidence 의미 체계 통합.

\* 새 capability, 새 Outcome, 새 Source 추가.

\* 설명 문장 rewrite, 추천/비교/해석 문장 추가.

\* Lua runtime UI 재설계.

\* chunking 분할 정책 변경.

\* Pulse, Echo, Fuse, Nerve, Frame, Cortex, Canvas 등 cross-module 구조 변경.

\* deployment, package publishing, Workshop readiness 선언.

\* release readiness, B42 readiness, production validation 선언.

\* runtime optimization 또는 gameplay behavior 변경.

\* external mod normalization contract 확장.

\* staging evidence 대량 삭제 또는 archive-by-glob 정리.

\* 새 테스트 인프라 도입.



\---



\## 6. Proposed Approach



\### 통합 시퀀싱



1\. \*\*Scope / Inventory / Artifact Boundary 정렬\*\*



&#x20;  \* active source, generated output, staging evidence, package copy, compatibility wrapper boundary를 재측정한다.

&#x20;  \* build script inventory를 active, legacy/archive, reproduction evidence, consolidation candidate 기준으로 정리한다.



2\. \*\*Description v2 Build Tool 공통화\*\*



&#x20;  \* family별 common I/O, JSON/JSONL, hash, markdown report helper를 정리한다.

&#x20;  \* batch1에 묶인 상수/유틸은 공용 module로 이동한다.

&#x20;  \* direct script execution baseline과 compose import contract 충돌은 별도 판정 대상으로 둔다.



3\. \*\*Build Import / Bootstrap / Compose Contract 정리\*\*



&#x20;  \* ROOT/sys.path bootstrap 반복을 줄인다.

&#x20;  \* compose module의 import dance를 제거하되, direct script execution 보존 여부 판정과 연결한다.



4\. \*\*Quality Gate / Evidence Pipeline / Version Path 정리\*\*



&#x20;  \* `quality\_gates.py`는 gate별 module과 reporting/CLI 책임으로 분리한다.

&#x20;  \* Recipe / Right-click pipeline은 execution skeleton만 공유하고 authority는 track별로 유지한다.

&#x20;  \* version/path/output suffix/source candidate는 central helper 또는 manifest로 정리한다.



5\. \*\*Artifact / Staging / Git Tracking Policy 정리\*\*



&#x20;  \* generated runtime Lua, `Iris/output`, staging evidence, package copy의 tracking policy를 명확히 한다.

&#x20;  \* staging archive sweep은 per-file/per-directory disposition을 따른다.



6\. \*\*Runtime Lua Responsibility Cleanup\*\*



&#x20;  \* Generator/Renderer debug line 축소, IrisMain helper 정리, runtime renderer responsibility split을 behavior-neutral 범위에서 수행한다.

&#x20;  \* Browser/Wiki/Tooltip 등 user-facing surface는 manual QA 전까지 behavior claim을 하지 않는다.



7\. \*\*Test Discovery / Validation Surface 정리\*\*



&#x20;  \* unittest/pytest/script-style check의 discovery boundary를 import contract와 맞춘다.

&#x20;  \* phase별 validation command matrix를 정리한다.



\---



\## 7. Authority / Surface Impact



\### Authority Surface



Planned as none.



\* build helper extraction, family consolidation, stage skeleton sharing은 authority ownership 이동이 아니다.

\* Recipe / Right-click evidence decision authority는 track별로 유지한다.

\* future execution이 authority-bearing artifact를 수정하면 별도 scope lock과 disclosure가 필요하다.



\### Runtime Behavior Surface



Potential impact 있음.



\* build-only phase는 output hash equivalence로 runtime behavior impact를 제한한다.

\* runtime Lua cleanup phase는 Generator/Renderer, IrisMain, Wiki/Browser renderer를 다룰 수 있으므로 syntax/require/manual QA boundary가 필요하다.

\* user-facing behavior change는 별도 QA 없이는 성공으로 주장하지 않는다.



\### Compatibility Surface



Concerns 있음.



\* direct script execution baseline.

\* public `IrisAPI`.

\* Pulse namespace compatibility wrapper.

\* compose module entrypoint.

\* compatibility wrapper 제거/변경은 deprecation decision 또는 compatibility window 없이는 진행하지 않는다.



\### Sealed Artifact Surface



Concerns 있음.



\* generated data, frozen SHA, current readpoint, staging evidence는 sealed 또는 evidence-adjacent surface다.

\* `IrisLayer3Data.lua`, Layer3 chunks, UseCaseDescriptions chunks, classification/index generated data는 SHA comparison 또는 approved diff 없이 mutation하지 않는다.

\* sealed evidence를 untracked/disposable로 오판하지 않는다.



\### Public-Facing Output Surface



기본 목표는 none.



\* Browser/Wiki/Tooltip 표시 문구나 구조를 바꾸는 execution은 public-facing output touch로 disclose한다.

\* 한국어 설명 문구 변경은 non-goal이다.



\---



\## 8. Phases



\### Phase 1 — Scope, Inventory, Artifact Boundary Seal



Goal:



\* active source, generated output, staging evidence, package copy, compatibility wrapper, build script disposition을 재측정한다.



Primary Changes:



\* `Iris/build/ENTRYPOINTS.md`, `Iris/build/build\_import\_contract.md`, `Iris/build/description/v2/tools/build/INVENTORY.md` current read를 맞춘다.

\* build script를 active / legacy\_archive / duplicate\_consolidation\_candidate / reproduction evidence 성격으로 분류한다.

\* tracked/untracked/ignored build scripts와 generated outputs를 분리한다.

\* batch1 import graph를 산출한다.

\* package copy와 runtime source copy의 Git 정책을 명시한다.



Expected Risks:



\* artifact를 source처럼 읽거나 source를 disposable artifact처럼 읽는 분류 오류.

\* active/legacy 기준 모호.

\* operator만 아는 보존 이유 누락.

\* 269개 vs 282개 script count 차이로 inventory 기준 혼선.



Expected Validation:



\* `git diff --stat`

\* `git ls-files` inventory

\* targeted existence/readpoint checks

\* INVENTORY.md 산출 후 검토 gate



Expected Deliverables:



\* updated inventory/readpoint note

\* phase-specific candidate list

\* batch1 import dependency graph

\* artifact/source classification table



\---



\### Phase 2 — Description v2 Build Common Helper Extraction



Goal:



\* description v2 build script군을 family별 helper 소비 구조로 정리하고, batch1 library import anti-pattern을 해소한다.



Primary Changes:



\* family별 common I/O, JSONL, hash, markdown report helper 후보를 정리한다.

\* `identity\_fallback`, `source\_coverage`, `interaction\_cluster`, `weak\_active\_cleanup`, acquisition 등 큰 family부터 helper adoption을 진행한다.

\* `build\_identity\_fallback\_batch1\_clothing\_surface\_reuse.py`에서 다른 batch가 import하는 상수/유틸을 common helper로 이동한다.

\* batch1은 다른 batch와 동등한 sibling script로 낮춘다.

\* artifact-path-only script는 reproduction contract를 먼저 남기고 추적/보존 여부를 결정한다.



Expected Risks:



\* batch1을 import하는 20+ 파일 전수 갱신 누락.

\* common constant/function 누락으로 build 실패.

\* direct script execution 깨짐.

\* staging artifact reproduction path 손상.

\* dual-import wrapper가 영구화될 위험.



Expected Validation:



\* family별 direct script smoke.

\* 모든 batch script smoke where available.

\* focused unittest where available.

\* before/after artifact hash 또는 approved diff.

\* `380 tests OK` baseline 유지.



Expected Deliverables:



\* common helper adoption batch.

\* family-level execution notes.

\* batch1 import migration note.

\* no-glob-delete confirmation.



\---



\### Phase 3 — Build Import Contract, Compose Contract, Root Bootstrap Cleanup



Goal:



\* compose module import dance와 ROOT/sys.path bootstrap 반복을 정리하되, direct script execution baseline 충돌을 명시적으로 판정한다.



Primary Changes:



\* `compose\_layer3\_\*.py`의 `try/except ImportError` import dance 제거 후보를 정리한다.

\* `tools/build/\_\_init\_\_.py` 또는 common path helper를 통해 `ROOT`, `DATA\_DIR`, `OUTPUT\_DIR`, `STAGING\_DIR` 같은 bootstrap source를 정리한다.

\* 254개 ROOT bootstrap, 97개 sys.path shim 반복 축소를 진행한다.

\* 호출자 import line을 contract에 맞게 갱신한다.



Expected Risks:



\* direct script execution baseline과 `python -m tools.build...` package entrypoint 통일이 충돌할 수 있음.

\* script 직실행 flow 실패.

\* import path 변경이 다른 build script에 전이.

\* package화로 인한 import cycle.



Expected Validation:



\* active pipeline direct execution.

\* compose standalone scenario regression where available.

\* build artifact SHA comparison.

\* `380 tests OK` 유지.

\* `except ImportError` occurrence check.



Expected Deliverables:



\* compose import contract note.

\* root bootstrap cleanup batch.

\* updated build import contract.

\* unresolved entrypoint decision record if conflict remains.



\---



\### Phase 4 — Quality Gates Module Split



Goal:



\* `Iris/build/quality\_gates.py`를 gate별 책임과 reporting/CLI 책임으로 분리한다.



Primary Changes:



\* Q1 PASS integrity, Q2 Strong integrity, Q3 anchor completeness, Q4 determinism, Q5 regression diff를 separate module로 이동한다.

\* build report JSON/Markdown generation을 reporting module로 이동한다.

\* existing `python -B Iris/build/quality\_gates.py` command surface를 유지한다.



Expected Risks:



\* gate output schema drift.

\* `--update-sha` guard behavior drift.

\* Q5 allowed-change semantics drift.

\* 기존 closeout에서 quality\_gates split이 완료됐다는 상태와 후속 split 필요 상태가 충돌할 수 있음.



Expected Validation:



\* `python -B Iris/build/quality\_gates.py`

\* `python -B Iris/build/quality\_gates.py --update-sha`는 별도 승인 scope에서만 실행.

\* report JSON/Markdown schema comparison.

\* determinism/regression gate comparison.



Expected Deliverables:



\* split gate modules.

\* compatibility CLI shim.

\* unchanged report semantics 또는 approved diff.

\* quality gate current-state readpoint note.



\---



\### Phase 5 — Evidence Pipeline Execution Skeleton Refactor



Goal:



\* Recipe / Right-click pipeline의 execution skeleton만 공통화하고 evidence decision authority는 분리 유지한다.



Primary Changes:



\* pipeline stage definition, artifact writer, deterministic save, stage logging을 common helper로 이동한다.

\* Recipe-specific parser/requirements logic은 recipe module에 남긴다.

\* Right-click-specific source index validation, candidate generation, proof merge, field registry logic은 right-click module에 남긴다.



Expected Risks:



\* 두 evidence track의 의미 체계가 섞이는 구조.

\* v2.2/v2.3/v2.4 mode handling drift.

\* generated output ordering drift.



Expected Validation:



\* `python -B Iris/build/recipe\_evidence\_pipeline.py`

\* `python -B Iris/build/rightclick\_evidence\_pipeline.py --v24`

\* cross-track regression fixture.

\* quality gate rerun.

\* output hash 또는 approved diff.



Expected Deliverables:



\* shared pipeline skeleton.

\* track-specific authority modules.

\* no cross-track semantic merge declaration.



\---



\### Phase 6 — Version and Path Manifest Hardening



Goal:



\* `v2.4`, `v2.5`, output suffix, data root, upstream source candidates, worktree-specific paths를 중앙화한다.



Primary Changes:



\* `Iris/build/tools/common/versions.py` 또는 manifest를 확장한다.

\* hard-coded `v2.4` path를 active pipeline에서 제거한다.

\* `.claude/worktrees/<name>` 같은 local worktree default candidate는 CLI option, environment override, explicit local manifest 중 하나로 이동한다.

\* historical oneshot script의 reproduction path는 필요 시 예외 문서화한다.



Expected Risks:



\* old artifact lookup 실패.

\* oneshot script의 historical reproduction path 손상.

\* local-only convenience path 제거로 workflow 불편.

\* active pipeline과 historical reproduction path 구분 실패.



Expected Validation:



\* active pipeline direct execution.

\* source sync script dry run.

\* path resolution unit tests 또는 focused script tests.

\* old artifact lookup check where applicable.



Expected Deliverables:



\* central version/path helper.

\* no implicit named-worktree dependency in active path.

\* documented exception for retained historical oneshots.



\---



\### Phase 7 — Selective Round Script Consolidation and Archive Sweep



Goal:



\* 명확히 같은 구조의 sibling script를 안전한 범위에서 통합하고, 끝난 staging/archive 대상은 per-disposition 기준으로 이관한다.



Primary Changes:



\* Phase 1 classification 결과 기반으로만 consolidation을 수행한다.

\* 후보:



&#x20; \* `build\_post\_cleanup\_phase3\_pkg3{a..j}`

&#x20; \* `build\_source\_coverage\_{b1..b4,c1a..c1e}`

&#x20; \* `build\_identity\_fallback\_batch{2..9}\_authority\_promotion`

&#x20; \* `freeze\_quality\_baseline\_v{1..4}`

&#x20; \* `report\_...\_{draft,final}`

\* batch별 설정은 JSON 등 data file로 외부화한다.

\* 종료된 staging directory는 `\_archive/staging/<original path>/`로 이동한다.

\* `\_archive/p0-2/Iris/Iris/...` 중첩 백업은 정리 대상 후보로 둔다.

\* archive/delete는 glob이 아니라 per-file/per-directory disposition으로만 처리한다.



Expected Risks:



\* 통합 후 output drift.

\* 동일해 보이는 batch 안에 숨은 branch logic 존재.

\* 진행 중 staging round를 archive로 오인.

\* build script가 staging path를 hard-code한 경우 깨짐.

\* sealed evidence를 disposable로 오판.



Expected Validation:



\* consolidation 전/후 artifact SHA comparison.

\* 관련 batch tests.

\* staging path reference grep.

\* 이동 후 grep 결과 확인.

\* `380 tests OK` 유지.

\* `git mv` 기반 이동 확인.



Expected Deliverables:



\* consolidated entrypoint scripts where approved.

\* batch config JSON where applicable.

\* archived original scripts.

\* `\_archive/staging/` tree.

\* staging/archive sweep note.



\---



\### Phase 8 — Generated Artifact and Git Tracking Policy Cleanup



Goal:



\* runtime generated Lua, `Iris/output`, staging evidence, package copy의 source/artifact/tracked 정책을 명확히 한다.



Primary Changes:



\* generated runtime Lua를 generator/source manifest와 연결한다.

\* `Iris/output` tracked files가 source-like baseline인지 generated artifact인지 분류한다.

\* `Iris/build/package`는 package output으로 유지하고 tracked source와 분리한다.

\* `.gitignore` allowlist는 round/evidence 기준으로 정리하되 existing sealed evidence를 손상하지 않는다.



Expected Risks:



\* sealed evidence를 untracked/disposable로 오판.

\* generated file manual-edit path를 열어버림.

\* package source와 runtime source 혼동.

\* archive sweep과 tracking policy cleanup이 서로 다른 disposition을 줄 수 있음.



Expected Validation:



\* `git ls-files` policy check.

\* generator output hash check where available.

\* package script dry-run 또는 file manifest inspection.

\* sealed artifact mutation 여부 확인.



Expected Deliverables:



\* tracking policy note.

\* artifact/source classification table.

\* updated ignore rules only if required.



\---



\### Phase 9 — Runtime Lua Residual and Responsibility Cleanup



Goal:



\* user-facing behavior를 바꾸지 않는 범위에서 남은 Lua runtime responsibility를 작게 나눈다.



Primary Changes:



\* `Generator.lua` / `Renderer.lua` debug line 축소 또는 trace mode 분리.

\* `IrisMain.lua`의 작은 helper를 INIT\_MODULES spec 또는 generic dispatch로 흡수하는 후보를 정리한다.

\* `IrisWikiSections.lua`를 section renderer / property extractor / usecase line renderer로 분리한다.

\* `IrisBrowserInteractionRenderer.lua`에서 interaction collection과 UI row rendering을 분리한다.

\* Pulse IrisDesc compatibility wrapper는 public/deprecation decision 이후에만 제거하거나 유지 정책을 문서화한다.

\* logger/info/warn/error 정책은 release/dev log boundary를 확인한 뒤 조정한다.

\* `\_dev/IrisTranslationDebug.lua`, `\_dev/media/`, debug text output은 미사용 검증 후 archive 또는 ignore 후보로 둔다.



Expected Risks:



\* Browser/Wiki/Tooltip rendering regression.

\* translation fallback drift.

\* compatibility wrapper removal regression.

\* debug line 축소로 진단 능력 저하.

\* IrisMain helper 통합으로 INIT\_MODULES spec 복잡도 증가.

\* `\_dev` file이 runtime에 포함되는지 검증 누락.



Expected Validation:



\* Lua syntax check.

\* runtime require smoke.

\* console boot sequence: `\[Iris] Bootstrap complete`.

\* KO mode boot playtest where required.

\* manual in-game QA for Browser/Wiki/Tooltip before behavior claim.

\* generated data SHA comparison.

\* `380 tests OK` 유지.



Expected Deliverables:



\* smaller runtime renderer modules.

\* reduced Generator/Renderer debug noise.

\* IrisMain helper disposition note or generic dispatch.

\* compatibility wrapper disposition note.

\* manual QA checklist update if UI surface changes.



\---



\### Phase 10 — Test Discovery and Validation Surface Normalization



Goal:



\* root build tests, description v2 tests, script-style checks의 discovery policy를 명확히 한다.



Primary Changes:



\* import-time `sys.exit()` style checks를 direct execution target으로 분리하거나 unittest-compatible 형태로 전환한다.

\* pytest/unittest discovery scope를 import contract와 일치시킨다.

\* validation command matrix를 phase별로 정리한다.



Expected Risks:



\* test discovery가 historical/script-style checks를 잘못 실행.

\* required validation command 증가로 operator burden 증가.

\* discovery behavior가 CI/release gate와 충돌.



Expected Validation:



\* `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test\_\*.py"`

\* focused root build tests.

\* pytest only if installed and configured for current scope.

\* validation matrix dry run.



Expected Deliverables:



\* validation matrix.

\* test discovery compatibility note.

\* converted tests where low-risk.



\---



\## 9. Validation Expectations



\### Expected Validation Depth



\* Phase 1: standard.

\* Phase 2, 3, 4, 5: heavy for build determinism, import contract, regression gate, evidence authority.

\* Phase 6, 7, 8: heavy where artifact movement, source/artifact classification, output hash, archive policy are touched.

\* Phase 9: heavy if user-facing runtime files change; otherwise syntax/require validation plus scoped smoke.

\* Phase 10: standard unless discovery behavior changes validation gates.



\### Expected Validation Areas



\* runtime.

\* compatibility.

\* determinism.

\* migration.

\* regression.

\* public-facing behavior.

\* source/artifact boundary.

\* evidence authority separation.



\### Known Validation Limits



\* No release readiness validation.

\* No Workshop deployment validation.

\* No B42 readiness validation.

\* No full external ecosystem compatibility sweep.

\* No long-session runtime validation.

\* No multiplayer validation.

\* No modpack compatibility validation.

\* No full runtime equivalence claim without manual in-game QA.

\* No sealed artifact mutation claim unless a phase explicitly performs and validates it.

\* No deployment/package publishing validation.

\* No build-time performance validation.



\---



\## 10. Risk Assessment



\### High Risk



\* `quality\_gates.py` split causing gate semantics or report schema drift.

\* Recipe / Right-click pipeline skeleton refactor accidentally merging evidence authority.

\* Runtime Lua UI split changing Browser/Wiki/Tooltip behavior without manual QA.

\* Generated artifact tracking policy change that loses sealed evidence or opens manual-edit paths.

\* batch1 import 해제 누락 또는 dual-import wrapper 영구화.

\* compose module import contract 변경이 direct script execution baseline과 충돌.

\* round script consolidation으로 output drift 발생.



\### Medium Risk



\* Description v2 build script common helper migration breaking direct script execution.

\* Version/path manifest migration breaking historical or local reproduction scripts.

\* Compatibility wrapper disposition affecting external require paths.

\* Test discovery normalization changing default executed tests.

\* staging directory archive 이동 중 진행 중 round 오인.

\* ROOT/sys.path bootstrap cleanup 중 import cycle 발생.

\* archive movement가 hard-coded staging path를 깨는 경우.



\### Low Risk



\* Inventory/readpoint documentation updates.

\* Helper extraction with no behavior/output change and focused validation.

\* Documentation-only tracking policy clarification.

\* Runtime file organization notes that do not touch Lua code.

\* ROOT bootstrap 단순화 중 output SHA 영향이 없는 경우.

\* `\_dev`, debug text output, nested archive 정리 중 runtime 미참조가 확인된 경우.



\---



\## 11. Rollback Strategy



\* 각 phase는 별도 batch 또는 독립 commit으로 구현한다.

\* build pipeline refactor는 focused validation 통과 전까지 compatibility entrypoint shim을 유지한다.

\* archive 이동은 `git mv`로 수행해 역방향 복귀 가능하게 한다.

\* generated artifact 변경은 before/after hash 또는 approved diff report를 보존한다.

\* sealed artifact SHA drift가 발견되면 해당 phase를 중단하고 rollback한다.

\* runtime Lua 변경은 이전 module layout과 require path 복원으로 되돌릴 수 있어야 한다.

\* compatibility wrapper removal은 deprecation window 또는 explicit release decision 전에는 실행하지 않는다.

\* tracking/ignore policy 변경은 inventory manifest를 기반으로 복구 가능하게 한다.

\* Phase 9 runtime 변경에서 Iris Lua error가 발생하면 해당 commit을 revert하고 runtime validation을 재수행한다.



\---



\## 12. Success Criteria



\* build/source/artifact/staging/package/runtime boundary가 inventory와 policy 문서에서 일관되게 읽힌다.

\* active build entrypoint는 documented direct script baseline 또는 별도 판정된 import contract를 통해 실행된다.

\* batch1이 common library 역할을 하지 않는다.

\* description v2 build script군은 family별 common helper 소비 경로를 갖는다.

\* quality gate behavior와 report schema는 unchanged 또는 approved diff 상태다.

\* Recipe / Right-click evidence outputs는 semantically independent 상태를 유지한다.

\* version/path constants는 active pipeline code에서 중앙적으로 읽힌다.

\* generated runtime Lua는 generator-owned 상태를 유지하고 manual-edit path가 열리지 않는다.

\* Git/source/artifact boundary가 pre-roadmap보다 명확하다.

\* staging은 active work와 archived evidence가 구분된다.

\* compose import dance와 ROOT/sys.path boilerplate는 판정된 contract 안에서 감소한다.

\* runtime cleanup이 수행된 경우 syntax/require/manual QA boundary를 통과한다.

\* `380 tests OK` baseline은 해당 범위에서 유지된다.

\* sealed generated data SHA는 변동 없음 또는 approved diff로만 변경된다.

\* test discovery policy는 `Iris/build/build\_import\_contract.md`와 충돌하지 않는다.



\---



\## 13. Expected Claim Boundary



This roadmap does NOT automatically imply:



\* full runtime equivalence.

\* full compatibility preservation.

\* release readiness.

\* deployment readiness.

\* production validation.

\* architectural correctness.

\* Layer 3 content correctness.

\* evidence/taxonomy correctness.

\* public-facing behavior validation.

\* Workshop readiness.

\* B42 readiness.

\* multiplayer readiness.

\* modpack compatibility.

\* long-session stability.

\* CI/CD readiness.

\* archive movement permanence.

\* all variant equivalence after script consolidation.

\* compatibility wrapper removal approval.



unless explicitly validated later.



Do not claim success beyond validated scope.



\---



\## 14. 충돌 / 별도 판정 필요



\### 14.1 Build script count



\* 로드맵 A: 282개 Python script.

\* 로드맵 B: 269개 build script.

\* 최종 판정 필요: Phase 1 inventory에서 기준 glob, tracked/untracked 포함 여부, ignored/local script 포함 여부를 재측정해야 한다.



\### 14.2 Direct script execution vs package entrypoint



\* 로드맵 A: compose module을 `python -m tools.build...` 또는 script direct execution 중 하나로 고정하는 선택지를 둔다.

\* 로드맵 B: direct script execution baseline을 compatibility contract로 보존한다.

\* 최종 판정 필요: compose import dance 제거 방식은 direct script execution baseline 보존 여부와 함께 결정해야 한다.



\### 14.3 Archive/delete 정책



\* 로드맵 A: 종료된 round/staging/script를 `\_archive/`로 이동하고 active/archive를 분리한다.

\* 로드맵 B: archive/delete는 glob이 아니라 per-file disposition이며 staging evidence 대량 삭제 또는 archive-by-glob 정리는 non-goal이다.

\* 최종 판정 필요: archive sweep은 per-file/per-directory disposition 기준으로만 실행할지, A의 top-level staging 축소 목표를 어느 범위까지 적용할지 결정해야 한다.



\### 14.4 `quality\_gates.py` split 상태



\* 로드맵 A: 이전 addendum에서 quality\_gates split이 닫힌 작업으로 언급된다.

\* 로드맵 B: `quality\_gates.py` split을 별도 Phase로 둔다.

\* 최종 판정 필요: 현재 readpoint에서 split이 실제 완료인지, 추가 split이 필요한지 확인해야 한다.



\### 14.5 Compatibility surface



\* 로드맵 A: compatibility surface를 None으로 둔다.

\* 로드맵 B: Pulse namespace compatibility wrapper, public `IrisAPI`, direct script execution contract를 compatibility surface로 둔다.

\* 최종 판정 필요: compatibility wrapper와 direct script execution을 roadmap surface로 명시할지 확정해야 한다.



\### 14.6 Runtime cleanup 범위



\* 로드맵 A: Generator/Renderer debug noise와 IrisMain helper 통합 중심.

\* 로드맵 B: IrisWikiSections, IrisBrowserInteractionRenderer, compatibility wrapper disposition 중심.

\* 최종 판정 필요: Phase 9 runtime cleanup에서 두 runtime cleanup 축을 모두 실행할지, 하나를 후속 phase로 보류할지 결정해야 한다.



