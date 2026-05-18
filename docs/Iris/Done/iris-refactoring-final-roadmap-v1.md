# Iris Refactoring Final Roadmap v1.4

> 상태: Implemented and closeout-recorded  
> 기준일: 2026-05-04  
> 완료일: 2026-05-08  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 입력 기준: ChatGPT Codex 제안 + Claude Code 제안 통합안 + 2차/3차/4차/5차 검토안 종합 반영  
> 목적: Iris 리팩토링을 `빌드 잔재 정리 -> 런타임 경량화 -> 책임 분리 -> 소형 정리` 순서로 실행하기 위한 current planning document를 고정한다.
> Closeout: `Iris/_docs/refactor/iris_refactoring_final_roadmap_closeout.md`

이 문서는 Iris 리팩토링의 실행 순서와 게이트를 정리한다.  
수치가 붙은 항목은 제안 입력 기준의 측정값으로 채택하되, 실제 변경 직전에는 각 phase의 재측정 게이트를 통과해야 한다.

v1.1의 핵심 수정은 Phase 1을 **파일명 glob 기반 archive/delete가 아니라 active manifest 기반 판정**으로 바꾼 것이다.  
검토안에서 확인된 active helper, path-execution test 참조, phase 디렉토리 잔존 파일 가능성을 모두 실행 게이트로 승격한다.

v1.2의 핵심 수정은 공통 모듈 위치, schema/docs 계약, ProtectedCall call-site migration, phase disposition 판정 규칙, Phase 4 대형 변경 batch 분리를 명문화한 것이다.

v1.3의 핵심 수정은 `IrisProtectedCall.lua` B안을 Phase 2에서 제거하고 Phase 4 런타임 책임 분리 항목으로 이동한 것, 그리고 `Iris/build/tools/common` 도입 전에 Python import/실행 계약을 먼저 고정하도록 한 것이다.

v1.4의 핵심 수정은 Phase 4 대형 런타임 변경의 pairwise batch 분리, release/dev log 변경 batch 분리, import 계약 산출물 위치, pytest와 import 계약의 의존성을 명문화한 것이다.

---

## 1. 종합 원칙

- Iris는 계속 **100% Lua 기반 위키형 정보 모드**로 유지한다.
- Iris의 설명/브라우저/툴팁 표면은 해석, 권장, 비교를 하지 않는다.
- Recipe evidence와 Right-click evidence는 동급의 독립 2트랙으로 유지한다.
- Layer 3 문장은 build-time authority에서 생산된 문장을 기본 단위로 소비한다.
- 런타임 리팩토링은 in-game manual QA 기준이 문서화된 뒤에만 시작한다.
- 대형 정리는 먼저 노이즈와 dead code를 줄인 뒤, active 파일 수와 active entrypoint를 재측정하고 진행한다.
- generated artifact 자체를 손으로 쪼개는 것이 아니라, 가능한 한 생성기와 build pipeline의 책임 경계에서 수정한다.

## 2. 실행 순서 판정

두 제안의 공통 방향은 아래 순서로 읽는다.

1. **빌드 잔재 정리**
   - 런타임 동작을 바꾸지 않는 정리.
   - 탐색 노이즈와 과거 phase 잔여물을 제거한다.
2. **Dead Code 제거**
   - require/import 재확인 뒤, 런타임 참조가 없는 껍데기 코드를 삭제한다.
3. **빌드 파이프라인 구조화**
   - Phase 1 이후 active 파일 수를 다시 재고, 실제 빌드 계약에 남은 중복만 중앙화한다.
4. **Lua 런타임 책임 분리**
   - API, Browser, translation, Layer 3 data loading 같은 user-facing runtime 경계를 분리한다.
5. **소형 정리**
   - 런타임 QA와 충돌하지 않는 작은 정리는 병행하되, Phase 4 변경과 섞어 원인 추적을 어렵게 만들지 않는다.

## 3. Phase 1 - 빌드 잔재 정리

> 리스크: 낮음  
> 런타임 영향: 없음  
> QA: git diff와 파일 이동 확인 중심

### 1-1. one-shot 스크립트 아카이빙 `[LARGE]`

- 후보 universe: `build_*.py` 178개 + `report_*.py` 55개, 총 233개
- 중요 수정: 이 수치는 archive 후보 universe일 뿐이며, glob 자체가 archive 기준이 아니다.
- 알려진 active 위험:
  - `Iris/build/tools/pipeline/` 아래 `build_*.py` helper가 같은 glob에 포함된다.
  - `Iris/build/tools/pipeline/build_usecases_by_fulltype.py`는 `Iris/build/tests/test_recipe_evidence.py`에서 경로로 직접 참조된다.
  - import 검색만으로는 `subprocess` / direct path execution / test fixture 참조를 잡지 못한다.
- 기준: `ENTRYPOINTS.md` + tests + direct path execution + pipeline keep-list에 걸리지 않는 one-shot 스크립트
- 조치: `Iris/build/tools/oneshots/_archive/` 또는 현재 one-shot archive 정책에 맞는 하위 디렉토리로 이동
- 기대 효과: build tree 탐색 노이즈 대폭 감소
- 게이트:
  - 이동 전 active manifest를 먼저 작성한다.
  - active manifest는 `ENTRYPOINTS.md`, `tests`, `tools/pipeline`, direct path execution reference, 문서화된 command를 모두 포함한다.
  - `rg "import .*<script_name>|from .* import"`는 보조 확인으로만 사용한다.
  - pipeline keep-list에 오른 파일은 파일명이 `build_*.py`여도 archive하지 않는다.
  - archive 후 active manifest의 모든 command와 test path가 존재하는지 확인한다.

### 1-2. phase 디렉토리 사실 검증 및 relocated 판정 `[VERIFY-FIRST]`

- 대상: `phase0_validation/` ~ `phase4_tests/` 계열 디렉토리
- 중요 수정: 이 항목은 더 이상 "빈 디렉토리 삭제"가 아니다.
- 검토 입력: 해당 계열 디렉토리에 `.py` 파일이 남아 있을 수 있음이 보고됐다.
- 조치:
  - 현재 트리에서 각 phase 디렉토리의 존재 여부, 파일 수, `.py` 목록을 inventory한다.
  - `main.py`, `ENTRYPOINTS.md`, tests, direct path execution, docs link와의 의존 그래프를 확인한다.
  - relocated가 실제로 끝난 파일은 `tools/pipeline/`, `tests/`, `tools/oneshots/` 중 맞는 위치로 이동하거나 archive한다.
  - active 역할이 확인된 파일은 삭제하지 않고 active manifest에 올린다.
- 게이트:
  - "디렉토리가 비어 있다"는 전제를 사용하지 않는다.
  - 각 파일별 disposition(`active`, `relocated_duplicate`, `oneshot_archive`, `delete_candidate`)을 먼저 기록한다.
  - disposition 결정 규칙:
    - `main.py`, `ENTRYPOINTS.md`, tests, 활성 파이프라인이 import 또는 path 참조하면 `active`
    - `tools/pipeline/` 또는 `tests/`에 동명/동기능 파일이 있고 phase 위치본은 미참조면 `relocated_duplicate`
    - sprint/phase 명을 단 one-shot 패턴이고 active manifest에 없으면 `oneshot_archive`
    - 위 셋에 모두 해당하지 않으면 `delete_candidate`
  - `delete_candidate`는 단독 결정하지 않고 별도 review로 닫는다.
  - delete는 해당 disposition이 모두 닫힌 뒤에만 수행한다.

### 1-3. 루트 중간 산출물 이동 `[LARGE]`

- 대상: `context_outcomes.json`, `diagnostics.json`, `extraction_stats.json`, `iris-*-evidence-table.md` 9개 외 약 13개 파일
- 조치:
  - runtime/output 성격: `Iris/output/`
  - source/input 성격: `Iris/input/`
  - evidence/reference 성격: `Iris/evidence/` 또는 현재 evidence archive 정책 위치
- 게이트:
  - active script의 hard-coded path 확인
  - 이동 후 build/report command가 동일 산출물을 찾는지 확인
  - `iris-input-schema-v0.2-final.meta.json`, `_docs/`, `docs/Iris/Done/plan/` 같은 schema/meta/docs reference를 함께 확인
  - 문서/메타 계약이 현재 루트 파일명을 canonical로 참조하는 경우, reference 갱신 또는 legacy 위치 유지 결정을 먼저 기록
  - 코드가 깨지지 않아도 schema/meta/docs reference가 stale이면 Phase 1 완료로 보지 않는다.

### 1-4. `_archive/p0-2/` 압축 또는 제외 `[SMALL]`

- 대상: 중첩된 구식 런타임 사본
- 조치: zip 압축 후 git 제외 또는 삭제 후보로 분리
- 게이트:
  - 현재 runtime 경로와 이름이 겹치는 파일이 active require 대상이 아닌지 확인
  - 삭제 대신 압축을 택할 경우 `.gitignore` 반영 여부 확인

### 1-5. `_docs/refactor/` 완료 단계 분리 `[SMALL]`

- 대상: 완료된 P0~P7 단계 문서
- 조치: `Iris/_docs/refactor/_done/`으로 이동
- 게이트:
  - 현재 진행 중인 refactor 문서와 완료 문서가 섞이지 않게 상태 표기 확인

## 4. Phase 2 - Dead Code 제거

> 리스크: 낮음~중간  
> 런타임 영향: require 경로 삭제 가능성 있음  
> QA: require/load smoke 수준

### 2-1. Pulse IrisDesc wrapper release decision `[LARGE]`

- 대상: `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/`
- 제안 근거: 7개 파일이 passthrough 성격이며 require 없음으로 보고됨
- 조치:
  - `rg "Pulse/Iris/Logic/IrisDesc|IrisDesc"`로 내부 require를 재확인한다.
  - 내부 require 부재는 삭제의 필요조건일 뿐 충분조건이 아니다.
  - 공개 API였는지, 이전 공개 패키지에 포함됐는지, 외부 require 경로로 안내된 적이 있는지 확인한다.
  - 이번 릴리스에서 바로 제거할지, deprecate wrapper만 유지할지, 다음 릴리스에서 제거할지 release decision을 먼저 기록한다.
  - 제거가 허용된 경우에만 디렉토리를 삭제한다.
  - `Pulse/` 트리 자체가 빈 껍데기가 되는지 별도 확인
- 종료 조건:
  - `internal_unused = true`
  - `public_api = false` 또는 `deprecation_plan_exists = true`
  - 위 두 조건이 모두 충족된 뒤에만 `package_removal_allowed = true`로 마킹한다.
  - 디렉토리 삭제는 `package_removal_allowed = true` 이후에만 수행한다.

### 2-2. `Templates.lua` Logger/debug 경계 재측정 `[SMALL]`

- 대상: `Iris/media/lua/client/Iris/Logic/IrisDesc/Templates.lua`
- 중요 수정:
  - `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/Templates.lua`는 1줄 wrapper이므로 이 항목의 실제 대상이 아니다.
  - Pulse wrapper 삭제 여부와 별개로 Iris 실파일의 Logger/debug 사용 여부를 다시 측정한다.
- 조치:
  - Logger 호출이 실제로 없으면 import 제거
  - Logger 호출이 남아 있으면 release/dev log 정책에 맞춰 dev flag 뒤로 격리
- 게이트:
  - 파일 단독 require smoke
  - release mode에서 불필요한 debug log가 나오지 않는지 확인

### 2-3. `IrisProtectedCall.lua` 미사용 별칭 제거 후보 `[SMALL]`

- 대상: `engine()`, `ui()`, `data()`, `compat()` 별칭
- 현재 판정: 모두 `call()` 위임이면 실질 경계가 없음
- 현재 사용 상태:
  - 런타임 call site 대부분은 `ProtectedCall.call(...)`을 직접 사용한다.
  - `engine()`, `ui()`, `data()`, `compat()` 별칭에 정책을 추가해도 call site migration이 없으면 실제 런타임 경계에 적용되지 않는다.
- Phase 2 허용 범위:
  - A안만 허용한다.
  - A안은 미사용 별칭 제거 또는 no-op 별칭 유지 결정을 뜻하며, call-site migration을 포함하지 않는다.
- Phase 2 금지:
  - `engine/ui/data/compat`에 서로 다른 정책을 부여하는 것
  - `ProtectedCall.call(...)` call site를 wrapper별로 옮기는 것
  - release/dev log 동작을 바꾸는 것
- B안 처리:
  - B안은 런타임 동작 변경이므로 Phase 2에서 실행하지 않는다.
  - B안이 필요하면 Phase 4-8 `ProtectedCall boundary policy and call-site migration`으로 별도 scope lock을 연다.

## 5. Phase 3 - 빌드 파이프라인 구조화

> 리스크: 중간  
> 런타임 영향: 산출물 변경 가능  
> QA: 기존 build/test + 산출물 diff 검토

### 3-0. Phase 1 후 active scope 재측정 `[REQUIRED]`

- 목적: one-shot archive 이후 실제 active pipeline 파일 수를 다시 고정한다.
- 산출물:
  - active entrypoint 목록
  - active helper 목록
  - archived script 수
  - remaining duplicated JSON I/O 수
- 종료 조건: Phase 3의 각 작업이 재측정된 active 파일만 대상으로 삼는다.

### 3-1. JSON I/O 헬퍼 중앙화 `[MEDIUM]`

- 기준 모듈:
  - active build 전체 공통화 기준은 `Iris/build/tools/common/io.py` 같은 중립 위치에 새로 둔다.
  - `Iris/build/description/v2/tools/build/compose_layer3_io.py`는 description v2 전용 facade 또는 re-export로 유지할 수 있다.
- 중요 수정: "약 167개"는 JSON I/O 함수 정의 수로 보지 않는다.
- 현재 판정:
  - JSON I/O helper **정의 파일 수**와 `load_json(...)` 등 **호출처 수**를 분리해서 재측정해야 한다.
  - 검토안 기준으로 정의 수는 소수 파일이며, 실제 작업량은 active 호출처를 표준 helper로 위임시키는 범위에 가깝다.
- 계층 규칙:
  - `Iris/build/tools/pipeline/*` 같은 일반 build pipeline이 `description/v2/tools/build/*`에 의존하면 계층이 역전된다.
  - 공통 helper는 description v2보다 상위 또는 중립 build tools 위치에 둔다.
  - description v2 모듈은 필요하면 중립 common helper를 import해서 자기 계층에 맞는 이름으로 재수출한다.
- import/실행 계약 선행:
  - 현재 `Iris/build/__init__.py`와 `Iris/build/tools/__init__.py`가 없고, pipeline 스크립트는 standalone 실행과 로컬 sibling import가 섞여 있다.
  - common helper를 만들기 전에 아래 실행 형태 중 무엇을 보장할지 먼저 결정한다.
  - `python -B Iris/build/tools/pipeline/<script>.py`
  - `python -B -m Iris.build.tools.pipeline.<script>`
  - tests에서의 direct import 또는 path execution
  - package marker(`__init__.py`) 추가 여부
  - script-local `sys.path` bootstrap 허용 여부
- 조치:
  - Phase 1 이후 active 파일만 다시 측정
  - `def load_json`, `def load_jsonl`, `def save_json`, `def load_jsonl_map`, `write_jsonl` 같은 정의를 먼저 inventory한다.
  - 호출처 수는 별도 통계로 남기되, 호출처 수를 중복 정의 수처럼 해석하지 않는다.
  - active hub 파일부터 순차 교체
  - archive 대상 파일은 수정하지 않는다.
- 게이트:
  - common helper 도입 전 import/실행 계약 문서를 먼저 작성한다.
  - 결정 산출물은 `Iris/build/ENTRYPOINTS.md` 갱신 또는 `Iris/build/build_import_contract.md` 신설 중 하나로 봉인한다.
  - active manifest의 모든 command가 선택한 import 계약 아래에서 실행되는지 확인한다.
  - standalone script 실행과 test path execution이 깨지면 common helper 도입 실패로 본다.
  - read/write encoding, newline, stable sort 동작이 기존과 동일한지 fixture로 확인

### 3-2. recipe/rightclick evidence pipeline 공통 베이스 추출 `[LARGE]`

- 대상:
  - `Iris/build/recipe_evidence_pipeline.py`
  - `Iris/build/rightclick_evidence_pipeline.py`
- 조치:
  - R1~R5 / RC1~RC5 골격을 공통 stage runner로 추출
  - recipe/right-click 차이는 config와 classifier hook으로 주입
- 금지:
  - Recipe와 Right-click evidence를 같은 의미 체계로 합치지 않는다.
  - 공통화는 실행 골격에 한정하고, evidence track의 동급 독립성은 유지한다.
- 게이트:
  - stage runner 추출과 동시에 cross-track 무회귀 fixture를 추가한다.
  - Recipe 쪽 stage 변경이 Right-click 판정 결과를 바꾸거나, Right-click 쪽 stage 변경이 Recipe 판정 결과를 바꾸면 fail로 본다.
  - 공통 stage runner는 scheduling/logging/artifact IO 골격만 공유하고, 분류/판정 authority는 track별로 유지한다.

### 3-3. `quality_gates.py` Q5 분할 `[LARGE]`

- 대상: Q5 diff 수집 / 비교 / 리포팅
- 조치:
  - `collect`
  - `compare`
  - `report`
  3개 서브 게이트로 분할
- 게이트:
  - 기존 Q1~Q5 command surface 유지
  - Q5 결과 파일명과 fail 조건 유지

### 3-4. `compose_layer3_text.py` 모듈 분할 `[MEDIUM]`

- 대상: 847줄, 27개 함수, 외부 진입점 `build_rendered()`
- 현재 구조:
  - `compose_layer3_text.py`는 이미 `compose_layer3_blocks.py`와 `compose_layer3_io.py`를 import하는 public hub 구조다.
- 선행 결정:
  - 기존 `blocks/io` 경계를 유지하면서 내부만 더 나눌지, `identity/body_profile/item_v2/render` 경계로 재배치할지 먼저 결정한다.
  - 같은 책임을 `blocks/io`와 신규 모듈에 중복 배치하지 않는다.
- 조치:
  - `identity`
  - `body_profile`
  - `item_v2`
  - `render`
  4개 서브모듈로 분리
- 게이트:
  - `build_rendered()` public entrypoint 유지
  - rendered output byte-for-byte 또는 approved diff 기준 통과

### 3-5. 버전 상수 단일 manifest화 `[MEDIUM]`

- 대상: `v2.4` / `v2.5`, `BUILD_VERSION`, output suffix, quality gate label
- 조치 후보:
  - `Iris/build/description/v2/build_manifest.json`
  - 또는 Python-only 소비라면 `config.py`
- 채택 기준:
  - Lua/runtime 산출물까지 버전 정보를 소비하면 JSON manifest 우선
  - build Python 내부에서만 필요하면 `config.py` 우선
- 목적: 릴리스 suffix drift와 gate label drift 방지

### 3-6. pytest 인프라 구축 `[MEDIUM]`

- 제안 입력: 177개 `test_*.py` 중 52개가 sprint/phase 네이밍
- 조치:
  - active vs archived test 분류
  - `pytest.ini` 추가
  - active test discovery 범위 고정
  - CI 연결은 별도 phase로 분리 가능
- 게이트:
  - unittest 기반 기존 테스트가 있다면 즉시 폐기하지 않고 compatibility path 유지
  - `pytest.ini`와 test discovery는 3-1의 import/실행 계약과 호환되어야 한다.
  - dotted module import를 지원하지 않기로 결정했다면 pytest 설정도 path execution 중심으로 둔다.
  - dotted module import를 지원하기로 결정했다면 package marker와 module path를 테스트에서도 동일하게 검증한다.

## 6. Phase 4 - Lua 런타임 책임 분리

> 리스크: 높음  
> 런타임 영향: 있음  
> QA: manual in-game validation 필수

### 4-0. Manual QA 기준 문서화 `[REQUIRED]`

Phase 4 시작 전 아래 QA를 먼저 문서화한다.

- 게임 부팅 및 Iris boot 로그
- Alt tooltip 표시/비표시
- 우클릭 "Iris 메뉴에서 더보기" 진입
- Browser open/search/category/list/detail flow
- recipe requirement / right-click capability 표시
- Layer 3 description block 표시
- KO/EN fallback
- 오류 발생 시 release/dev log 차이
- Phase 4-2 / 4-4 변경이 예정된 외부 모드 입력 계약과 충돌하지 않는지 확인

### 4-1. `IrisLayer3Data.lua` 청킹 검토 `[LARGE]`

- 대상: `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`
- 제안 입력: 약 10,515줄, 약 1MB 단일 generated file
- 조치:
  - 생성기 `export_dvf_3_3_lua_bridge.py` 수준에서 chunk 출력 옵션 추가
  - chunk manifest 추가
  - Layer 3 lazy load 정책 검토
- 금지:
  - generated Lua 파일을 손으로 분할하지 않는다.
  - 문장 내용 rewrite와 data loading refactor를 한 phase에 섞지 않는다.

### 4-2. `IrisAPI.lua` 책임 분리 `[LARGE]`

- 대상: `Iris/media/lua/client/Iris/IrisAPI.lua`
- 사전 산출물:
  - `ARCHITECTURE.md`의 `Core(분류) / Description(표현) / Browser(탐색)` 3계층과 아래 4모듈 후보의 매핑 표를 먼저 작성한다.
  - `Tags`, `Index`, `Description`, `UseCases`가 각각 어느 계층의 facade인지 명시한다.
  - 매핑이 모호하면 4분할 축을 재설계한다.
- 조치:
  - `IrisAPI.Tags`
  - `IrisAPI.Index`
  - `IrisAPI.Description`
  - `IrisAPI.UseCases`
  로 책임을 분리
- 함께 처리:
  - `getDescriptionBlocks()` 디버그 로그를 dev flag 뒤로 격리
  - `ensureData()` 반복 패턴을 테이블 드리븐화
- 호환성:
  - 구형 `IrisDescGenerator` / Layer3 / UseCase 공존 경로는 compatibility window를 명시한다.
  - public Lua API surface나 예정된 외부 모드 입력 계약과 충돌하는 변경은 deprecation plan 없이 진행하지 않는다.

### 4-3. `IrisBrowserData.lua` 관심사 분리 `[MEDIUM]`

- 대상: `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserData.lua`
- 조치:
  - `CategoryIndex`
  - `VariantIndex`
  - `BrowserQuery`
  - `BrowserFilters`
  로 분리
- 함께 처리:
  - `CATEGORY_ORDER`와 `CATEGORY_KEYS` 중복 테이블 통합
- 게이트:
  - category/list/detail 결과가 기존과 동일한지 fixture 또는 manual QA로 확인

### 4-4. 번역 소스 단일화 `[MEDIUM]`

- 대상:
  - `Iris/media/lua/client/Iris/IrisTranslationLoader.lua`
  - `media/lua/shared/translate/*.txt`
- 문제: inline KO/EN 테이블과 txt 번역 소스 공존으로 key drift 가능
- 조치 후보:
  - txt를 canonical source로 두고 Lua를 생성
  - Lua를 canonical source로 두고 txt를 생성
- 채택 기준:
  - PZ 네이티브 translation flow와 맞추려면 txt canonical 우선
  - runtime fallback 커스터마이징이 더 중요하면 Lua canonical 검토
- 함께 처리:
  - UI 하드코딩 문자열 조사
  - 외부 모드가 추가 번역 key를 주입하거나 참조할 예정인 경우, canonical source 결정이 해당 입력 계약을 막지 않는지 확인

### 4-5. Browser 공통 베이스 추출 `[MEDIUM]`

- 대상:
  - `IrisBrowserListController.lua`
  - `IrisBrowserDetail.lua`
  - `IrisBrowserInteractionRenderer.lua`
  - `IrisBrowser.lua`
- 조치:
  - `ensureDeps()` / `getData()` 반복 패턴 공통화
  - `openSearch` / `openForItem`의 `panelW` / `panelH` 계산 중복 정리
- 게이트:
  - layout change는 별도 승인 diff로 분리

### 4-6. `IrisWikiSections.lua` fallback 중복 제거 `[MEDIUM]`

- 대상: `tr()` / `getLabel()` fallback chain
- 조치: 공통 fallback 함수로 통합
- 게이트: KO/EN fallback manual 확인

### 4-7. Layer 3 presentation formatting 경계 명문화 `[MEDIUM]`

- 목적: 이미 결정된 Layer 3 **render-time only** formatting 정책을 spec과 renderer gate로 명문화한다.
- 현재 결정:
  - `rendered.json` 원문 유지
  - `IrisLayer3Data.lua` 원문 유지
  - 줄바꿈과 폭 대응은 Browser / Wiki 같은 UI 소비자에서만 처리
- 조치:
  - spec 문서에 render-time only presentation formatting 정의
  - renderer gate 추가
- 허용:
  - UI 소비자에서의 줄바꿈
  - UI 소비자에서의 block spacing
  - UI 폭에 따른 wrapping
- 게이트:
  - `rendered.json` / `IrisLayer3Data.lua` data contract hash는 formatting 작업으로 바뀌지 않는다.
  - UI formatter 존재와 panel 개행 렌더만 별도 회귀로 관리한다.
- 금지:
  - 문장 삭제
  - 필터링
  - 의미 단위 재정렬
  - 조건부 요약
  - 추천/비교 문장 삽입

### 4-8. ProtectedCall boundary policy and call-site migration `[MEDIUM]`

- 성격: Phase 2의 dead-code cleanup이 아니라 런타임 책임 분리 작업이다.
- 대상:
  - `Iris/media/lua/client/Iris/Util/IrisProtectedCall.lua`
  - `ProtectedCall.call(...)`을 직접 쓰는 runtime call site
- 목적:
  - `engine()`, `ui()`, `data()`, `compat()`에 실제 경계별 에러 분류, 로그 정책, fallback 차이를 줄지 결정한다.
  - 정책을 부여한다면 call site를 해당 boundary wrapper로 이동시킨다.
- 사전 산출물:
  - `engine/ui/data/compat` call-site migration 범위표
  - 각 call site가 어느 boundary wrapper로 이동하는지의 판정 기준
  - wrapper별 failure mode와 release/dev log 정책
  - migration 전후 manual in-game QA checklist
- 게이트:
  - Phase 4 manual QA 문서가 생기기 전에는 실행하지 않는다.
  - wrapper 정책만 추가하고 call site를 그대로 두는 변경은 금지한다.
  - call-site migration과 로그 정책 변경은 같은 batch 안에서 검증한다.
  - `IrisAPI.lua` 책임 분리와 같은 batch에 섞지 않는다.

## 7. Phase 5 - 소형 정리

> 리스크: 낮음~중간  
> 실행 방식: Phase 4와 병행 가능하되, 동일 파일을 동시에 건드리지 않는다.

| # | 항목 | 크기 | 게이트 |
|---|------|------|--------|
| 5-1 | `IrisDesc/Generator.lua` 디버그 로그 40+줄을 dev flag 뒤로 격리 | SMALL | release log 무음 확인 |
| 5-2 | `arrayContains()` 등 유틸 중복을 `Iris/Util/Array.lua`로 추출 | SMALL | require path 확인 |
| 5-3 | `TestHarness.lua`를 dev 전용 폴더로 이동하고 `IrisMain.lua`의 `safeRequire("Iris/Logic/IrisDesc/TestHarness")` 경로/분기를 dev flag 뒤로 함께 격리 | SMALL | production load 차단 확인 |
| 5-4 | `Ordering.lua` `toArray()` 2회 중복 호출 제거 | SMALL | ordering output 동일 |
| 5-5 | `IrisMain.lua` `INIT_MODULES` string dispatch를 함수 포인터로 전환 | SMALL | boot order 동일 |
| 5-6 | `IrisDesc/Logger.lua` safeRequire 14줄을 직접 require로 단순화 | SMALL | missing dependency failure mode 확인 |
| 5-7 | `IrisConfig.lua` 매직 넘버 상수화 | SMALL | config default 동일 |
| 5-8 | `IrisBrowserDetail.lua` 3단 fallback 검증 후 단일화 | SMALL | detail fallback manual QA |
| 5-9 | 모듈 부트스트랩 보일러플레이트 통합 | SMALL | require/load smoke |

## 8. 모델별 채택 판정

| 항목 | Codex | Claude Code | 판정 |
|------|-------|-------------|------|
| 빌드 잔재 아카이빙 | 방향 제안 | 233개 수치 제시 | Claude Code 수치를 계획 기준으로 채택하되 실행 전 재측정 |
| phase 디렉토리 삭제 | 미언급 | 빈 디렉토리 삭제 제안 | 검토안 반영: 삭제가 아니라 verify-first disposition으로 변경 |
| 루트 산출물 이동 | 방향 제안 | 구체 대상 제시 | 코드 path뿐 아니라 schema/meta/docs 계약 확인 후 이동 |
| Pulse IrisDesc 삭제 | 호환 기간 주의 | dead code 확인 | 삭제 후보로 채택, 공개 경로 호환성 확인 후 실행 |
| JSON I/O 중앙화 | 방향 + 계층 위치 보강 | 167개 파일 수치 제시 | 167은 정의 수로 채택하지 않음. 정의 수/호출처 수 분리 재측정 + 중립 common 위치로 변경 |
| 버전 상수 manifest화 | 구체 제안 | 미언급 | 채택 |
| Layer 3 formatting 경계 | 구체 제안 | 미언급 | 이미 결정된 render-time only 정책의 명문화 작업으로 채택 |
| IrisAPI 책임 분리 | 4분할 제안 | 로그 정리 언급 | 3계층 ↔ 4모듈 매핑 표를 사전 산출물로 추가 |
| ProtectedCall 정리/강화 | 에러 분류 + call-site migration 지적 | 별칭 삭제 제안 | Phase 2는 A안만 허용. B안은 Phase 4-8 runtime migration으로 이동 |
| pytest 인프라 | 미언급 | 구체 제안 | 채택 |

## 9. 실행 게이트 요약

### Phase 1 진입 조건

- 현재 작업트리의 기존 변경과 충돌하지 않는 이동/삭제 범위 확인
- 본문에 적힌 모든 수치를 진입 직전 inventory 명령으로 재확인
- active manifest 작성
  - `ENTRYPOINTS.md`
  - tests
  - direct path execution
  - `tools/pipeline` keep-list
  - docs command reference
- phase 디렉토리 계열은 존재 여부 / 파일 수 / import graph / `main.py` 의존 확인 전 삭제 금지

### Phase 2 진입 조건

- require/import 재확인
- public API였는지 확인
- compatibility path가 필요하면 deprecation plan 작성
- 공개 패키지에서 제거 가능한지 release decision 기록
- `IrisProtectedCall.lua`는 Phase 2에서 A안만 실행 가능
- B안이 필요하면 Phase 2 scope에서 제외하고 Phase 4-8 scope lock으로 이동

### Phase 3 진입 조건

- Phase 1 이후 active build 파일 수 재측정
- 기존 산출물 기준 diff gate 결정
- 공통 build helper는 description v2 내부가 아니라 중립 build tools 계층에 둘지 먼저 결정
- `Iris/build/tools/common` 도입 전 Python import/실행 계약을 먼저 문서화
- standalone script 실행, `python -m` 실행, tests path execution 중 어떤 형태를 지원할지 결정

### Phase 4 진입 조건

- manual in-game QA checklist 문서화
- runtime smoke 기준 고정
- generated data와 runtime loader의 책임 경계 확정
- Phase 4 runtime-triggering 항목인 4-1(`IrisLayer3Data.lua` 청킹), 4-2(`IrisAPI.lua` 책임 분리), 4-8(ProtectedCall B안)은 모두 서로 다른 batch/commit으로 분리
- 4-1, 4-2, 4-8 중 둘 이상을 같은 변경 묶음에서 동시에 진행하지 않는다.
- 4-8 ProtectedCall B안은 manual QA 문서화 이후에만 실행한다.

### Phase 5 진입 조건

- 동일 파일을 Phase 4 대형 변경과 동시에 수정하지 않도록 batch 분리
- release/dev log 정책을 건드리는 Phase 5 항목은 4-8 ProtectedCall batch와 분리
- 특히 5-1(`Generator.lua` debug log dev flag 격리)은 4-8과 같은 batch/commit에 넣지 않는다.

## 10. Hold

- Phase 1 없이 바로 JSON I/O 167개 파일을 일괄 수정하는 접근
- JSON I/O 호출처 수를 helper 정의 중복 수로 해석하는 접근
- 일반 build pipeline이 `description/v2/tools/build/compose_layer3_io.py` 같은 description 전용 모듈에 의존하게 만드는 접근
- Python import/실행 계약 없이 `Iris/build/tools/common` helper를 먼저 추가하는 접근
- 파일명 glob만으로 `build_*.py` / `report_*.py`를 archive하는 접근
- phase 디렉토리를 inventory 없이 빈 디렉토리로 가정하고 삭제하는 접근
- 루트 산출물 이동 시 schema/meta/docs reference를 갱신하지 않고 코드 경로만 맞추는 접근
- generated `IrisLayer3Data.lua`를 수동 편집으로 청킹하는 접근
- Recipe / Right-click evidence의 의미 체계를 공통화하는 접근
- Layer 3 문장을 runtime renderer에서 필터/요약/재작성하는 접근
- manual in-game QA 없이 `IrisAPI.lua` / Browser / translation runtime 경계를 대규모로 바꾸는 접근
- Phase 2에서 ProtectedCall B안, 즉 boundary policy 부여나 call-site migration을 실행하는 접근
- `IrisProtectedCall.lua`에 경계별 정책만 추가하고 call site를 `engine/ui/data/compat` wrapper로 옮기지 않는 접근
- Phase 4의 4-1, 4-2, 4-8 중 둘 이상을 같은 batch/commit에 섞는 접근
- 4-8 ProtectedCall release/dev log 정책 변경과 5-1 Generator debug log 격리를 같은 batch/commit에 섞는 접근
- archive 대상 one-shot 스크립트를 active pipeline cleanup과 함께 리팩토링하는 접근
- compatibility alias 삭제와 user-facing API surface 변경을 같은 커밋에 섞는 접근
- release log 정리와 dev diagnostic 강화 기준을 구분하지 않는 접근
- 본 리팩토링 후 발견되는 설명 왜곡을 곧바로 리팩토링 책임으로 귀속시키는 접근
  - DECISIONS 2026-03-23 기준, 설명 왜곡의 1차 책임 위치는 태그 생성 단계(Core / Rule / predicate 계층)다.

## 11. 다음 작업

1. Phase 1 실행 전 inventory command로 실제 대상 수를 재측정한다.
2. `Iris/build/ENTRYPOINTS.md`, tests, direct path execution, `tools/pipeline` keep-list를 묶어 active manifest를 만든다.
3. phase 디렉토리 계열은 삭제가 아니라 파일별 disposition inventory로 먼저 닫는다.
4. one-shot archive / phase disposition / root artifact move를 하나의 cleanup batch로 묶되, runtime Lua 파일은 건드리지 않는다.
5. root artifact move 후보는 schema/meta/docs reference까지 포함해 legacy 위치 유지 여부를 먼저 결정한다.
6. Phase 1 종료 후 Phase 3의 active pipeline scope를 새로 계산한다.
7. JSON I/O common helper 위치는 description v2 내부가 아니라 중립 build tools 계층으로 먼저 설계한다.
8. `Iris/build/tools/common` 도입 전 standalone/script/module/test import 계약을 먼저 문서화한다.
9. import 계약은 `Iris/build/ENTRYPOINTS.md` 갱신 또는 `Iris/build/build_import_contract.md` 신설로 봉인한다.
10. Phase 2에서 `IrisProtectedCall.lua`를 다룰 경우 미사용 별칭 제거 여부만 결정한다.
11. ProtectedCall boundary policy와 call-site migration은 Phase 4-8로 넘긴다.
12. Phase 4는 별도 QA 문서와 API 계층 매핑표가 생기기 전까지 planning 상태로 유지한다.
13. Phase 4 실행 시 4-1, 4-2, 4-8은 pairwise separate batch로만 연다.

## 12. Implementation Closeout

This planning roadmap has been implemented through Phase 5-9 and closed at the
documented static-test and console-validation level.

- Closeout record: `Iris/_docs/refactor/iris_refactoring_final_roadmap_closeout.md`
- Latest full test run: `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"` = `376 tests / OK`
- Latest runtime smoke: Phase 5-9 KO console validation with
  `Iris/Util/IrisModuleBootstrap.lua` loaded and Iris error patterns at 0.
