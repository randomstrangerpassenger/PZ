# Implementation Plan — Iris 책임 분리 리팩토링

- 작성일: 2026-09-15
- 수정일: 2026-09-15 (사용자 요청: 리팩토링 범위 유지, 검증 중복 최소화와 변경별 차단 격리)
- 상태: **planned — 범위 유지 및 최소 검증 실행 정책 반영**
- 입력: 사용자 제공 「Iris 리팩토링 제안 종합안 — ChatGPT × Claude」
- 양식: [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md)
- 설계 기준: [Philosophy.md](Philosophy.md), [ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md), [ROADMAP.md](ROADMAP.md)
- 실행·증거 기준: [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md)
- 최초 수정 입력: 「Iris 책임 분리 리팩토링 계획 — 종합 Implementation Plan Review」. 당시 대상 SHA-256: `8d60e62ddd026545f828ec66de8753b0f7cbf100c9c065e379c3e600ffd06cac`.
- 이번 수정 입력: 「Iris 책임 분리 리팩토링 계획 개정본 — 종합 Plan Review」. 대상 SHA-256: `bb947c5862b0c8bd2b153f3edb4f3acbba7b3f07767781e41655a6a5b5204c40`.
- 조사 checkout: `C:\Users\MW\Downloads\coding\PZ`, `main`, HEAD `aeabeda257209fd2bb7eb9172a4c9960ff7d1f9f`

이 문서는 리팩토링 실행 계획이다. 이전 검토의 대응과 K-1/K-2 관찰은 당시 기록으로 유지한다. 이번 개정은 사용자의 요청에 따라 폭넓은 리팩토링 대상을 유지하면서 중복 검사·후보 생산·Gate를 줄인다. 별도 plan review 회차나 승인을 새 착수 조건으로 두지 않는다. 구현·후보 생산·설치·pytest 본문·full gate·PZ는 이번 문서 수정에서 실행하지 않았다. 이하 과거 검토 대응표는 추적 기록이며, 현재 실행 횟수와 적용 범위는 §7의 최소 검증 실행 정책을 따른다.

---

## 1. Objective

Iris의 현재 사실·설명·검증 결과와 공개 Lua 호환성을 유지하면서, 변경할 때 함께 이해해야 하는 코드의 범위를 줄인다.

핵심 목표는 다음 세 가지다.

1. Layer 3 설명 조합을 공통 조립 흐름과 기능군별 표현 규칙으로 분리한다.
2. Layer 3 근거 수집, 과거 설명의 주장 추출, 질문별 판정을 각각 기능군 단위로 분리한다.
3. 저장소 검증 실행기를 조사·계약 확인·작업공간·실행 및 결과 수집 책임으로 분리한다.

공통 유틸, 빌드 진입점, Lua 화면 코드와 역사 자료 정리는 이 세 목표를 지원하는 별도 변경 단위로 진행한다. 파일 수나 줄 수 감소 자체를 완료 기준으로 삼지 않는다.

---

## 2. Scope

### 채택 범위와 순서

| 순서 | 변경 | 범위 | 착수 조건 |
|---|---|---|---|
| 1 | Change 1 | subject/스냅샷 격리, B→C 입력 전달 코드와 fixture, 비교 기준 확보 | §7의 준비·별도 제품 코드 변경 검증을 완성 |
| 2 | Change 2 | 검증 실행기의 내부 책임 분리 | 실제 full gate는 현재 classification 문제로 BLOCKED; 이를 해소하지 않고 완료 처리하지 않음 |
| 3 | Change 3 | 같은 계약의 hash/JSON/path/Lua escaping 공통화 | producer 변경이면 Change 4–5와 같은 격리/후보 조건 적용 |
| 4 | Change 4 | lexicon 결합 축소와 `frames()` 기능군 분리 | before/after 및 B/C 후보 binding 준비 |
| 5 | Change 5 | recovery 기능군 분리 | 사실·근거·질문 판정 비교 준비 |
| 6 | Change 6–7 | 설치 공통화 실익 판정, 허용된 Menu Lua 국소 정리 | Change 6은 조건부, B guard 파일 변경은 보류 |
| 7 | Change 8–9 | 빌드 의존·CLI·경로 및 테스트 배치 정리 | 활성 참조와 test ID 매핑 확보 |
| 8 | Change 10–12 | 큰 legacy 코드, 보관 구조, 이름·주석 정리 | 현재 참조와 복원 계약 확인 |

**첫 핵심 구현 대상은 검증 실행기의 내부 책임 분리를 기본값으로 하되 고정 선행 조건으로 삼지 않는다.** 이는 3,373줄 실행기의 결합을 줄이는 독립적인 선택이다. §7 A/B/D/E/F/G는 이 runner를 직접 통과하지 않으므로 Change 2가 막혀도 다른 변경을 진행한다. 실행자는 실제 의존성에 따라 독립 Change의 순서를 바꾸거나 관련 추출을 묶을 수 있다. Change 번호는 추적 단위이며 별도 PR·승인·Gate·전체 재생성 횟수가 아니다. PowerShell 동작 변경과 테스트 이동은 runner 추출 diff와 구분한다.

현재 HEAD의 classification 누락에 대해서는 **canonical full-gate 검증을 원인 명시 BLOCKED로 남기는 경로를 선택한다.** 이 계획에서 임시 분류를 추가하거나 conftest를 비활성화해 canonical PASS를 만들지 않는다. 독립적인 조사·집중 검사·코드 분리는 진행할 수 있지만, 실제 runner 종단 검증이 끝나기 전 Change 2는 미완료로 남긴다. 독립 Change는 각 검증을 충족하면 개별 complete로 닫고, 전체는 항목별 상태를 집계한다. 기존 classification owner 절차에서 문제가 해소되면 해당 새 subject와 유효한 환경으로 다시 실행한다.

Layer 3 착수 조건은 별도 worktree를 기다리는 것이 아니라 실제 선택 subject의 코드·입력·산출물 대응과 후보 검증 경로 확보다. 재조사한 핵심 producer 7개와 composition 산출물 2개는 main과 교정 worktree의 raw hash가 같았다. 이후 다른 내용 변경이 확인되는 경우에만 기준 포함 여부를 다시 판단한다. 이 조건은 Layer 3 producer closure를 변경하는 Change 3/8/12에도 적용한다.

### 원 종합안과 Change의 대응

| 원 제안 | 수정 계획 | 처분 |
|---|---|---|
| repository runner 분리, Python/PowerShell 책임 | Change 2, §7 C | 채택; 실제 runner 검사와 fake launcher fixture 구분 |
| hash/JSON/path 및 Lua escaping | Change 3 | 동일 계약만 채택; raw-bound 파일 속성도 확인 |
| frames/family 분리, lexicon/recovery 결합 축소 | Change 4 | 채택; 격리된 before/after 전수 비교 |
| recovery source/migration/adjudication | Change 5, §7 B | 채택; 비-editable 설치와 두 신규 후보 필요 |
| installer atomic write | Change 6 | 실익 판정 후 adopt/no-op; 현재는 추출을 필수화하지 않음 |
| Browser Detail / DataLookup | Change 7 | 허용된 `MENU_RUNTIME` 파일과 신규 내부 모듈에 한해 채택 |
| Wiki 표시 규칙 | Change 7 | WikiSections 안의 중복 정리만 채택; 기존 Presentation/profile 수정은 보류 |
| interaction state/widget slot | Change 7 | B guard에 걸리는 파일의 수정은 보류 |
| 계측 중복·이름·주석 | Change 7/12 | ModelAssembler의 호환 가능한 정리만 검토; guarded tooltip/fact reader 수정은 보류 |
| build 세대/의존 방향/CLI/local path | Change 8 | 활성 참조를 확인한 범위 채택; PZ2 경로 fixture 포함 |
| 테스트 배치/framework/validation anchor | Change 9 | 보호 범위 유지 조건으로 채택; 일괄 pytest 변환 제외 |
| 13,219줄 파일/완료 round script | Change 10 | current contract별 존속 판정 후 분리/보관; membership만으로 존속 승인하지 않음 |
| successor 중복 저장 | Change 11 | 현재 r1–r5 저장소 정리는 no-op; 실익이 있는 tracked 항목만 별도 조건부 판정 |
| version/round 파일명 | Change 12 | 책임 정리 이후 조건부 |
| canonical/newline 정책, `.gitattributes` 축소 | 범위 밖 | 기존 bytes 유지; 새 raw-bound 파일의 속성 추가는 허용 |
| Lua 평면 API wrapper | 유지 | 공개 호환 facade로 보존 |

### 이전 종합 검토 지적의 반영 위치

| 검토 ID | 수정 내용 | 주요 위치 |
|---|---|---|
| Critical 1 / F-01 / C-2 | A의 고정 writer를 disposable subject에 격리, Origin hash 보존·전수 비교·생성물 병합 정책 | Change 1/3/4, §5, §7 A, §10 |
| Critical 2 / F-03 / C-3 | non-editable 설치, before/after 신규 Recovery 후보·환경 변수·payload 비교·수명 | Change 1/5, §7 B, §12 |
| Critical 3 / F-02 | `.tmp` basetemp, 단일 pytest B→C 실행, 명시적 candidate refs의 producer/installer 전달 | Change 1, §7 E |
| Critical 4 / C-1 | B guard 파일 변경 보류, 허용 Menu 목록·retained bytes 확인, product contract 포함 | Change 7, §7 E/F, Manual Validation |
| W-01 | fake launcher와 실제 runner 종단 실행 구분 | Change 2, §7 C |
| N-01 | 신규 raw-bound 파일에 `-text` 적용·checkout hash 확인 | §5 Config, Change 3 |
| N-02 | 동일성이 확인된 핵심 파일에 대해 worktree 대기 전제 삭제 | §2/4 |
| N-03 | Change 3에도 producer closure 격리 조건 적용 | Change 1/3, §7 |
| N-04 | membership과 survival authority 구분 | §4, Change 10 |
| N-05 | untracked r1–r5 저장소 정리는 no-op, 실익 기반 처분 | Change 11 |
| N-06 | Python→Lua 실제 실행 명령과 도구 전제 | §7 F |
| N-07 | PZ2/t3d1·t2-final의 boundary/binding fixture 조사 포함 | Change 8 |
| N-08 | 원 종합안→Change 대응표 추가 | 이 절 |
| N-09 | runner 우선순위 근거 정정, 실제 source-census 전후 JSON 비교 | §2, §7 C |
| N-10 | atomic write 공통화는 실익 확인 후 adopt/no-op | Change 6 |

이 표는 수정 추적표이며 각 이슈의 검토 PASS 판정이나 구현 검증 결과가 아니다.

### 이번 개정본 검토의 판정 및 반영 위치

ID가 겹치는 N 항목은 이 표와 앞의 **이전 검토** 표를 구분해 읽는다.

| 이번 검토 ID | 확인/처분 | 주요 위치 |
|---|---|---|
| K-1 | source의 `supply.build(root)`가 `description bytes changed`로 거부됨을 재현. 실행 차단 원인으로 채택 | §4, Change 1, §7 E의 직접 supply와 중첩 `s2_candidate.build` 모두 명시적 ref 전달 |
| K-2 | 기존 F collection exit 3, conftest 없는 집중 경로 exit 0을 확인. canonical 경로 차단으로 채택 | §4, Change 2, §7 C/F, §12 |
| N-01 | Wiki는 기존 Presentation/profile을 수정 없이 재사용하는 것으로 정렬 | §4 |
| N-02 | subject 상대 cache를 공용 절대 `UV_CACHE_DIR`로 대체; cache/network 전제 명시 | §7 공통 준비 |
| N-03 | Origin 두 JSON의 실제 byte snapshot 생성·복사 전후 hash 확인 | §7 공통 준비 |
| N-04 | A 이전 default Menu input 검사 node/options 명시 | §7 공통 준비 |
| N-05 | expected-ref 전달은 fixture 외 B/Menu producer 코드 변경. Change 1에 귀속하고 별도 전후 검증 | Change 1, §5/7 E |
| N-06 | 신규 Lua module을 v1/v2 producer·legacy package support 목록에 반영할 책임 명시 | Change 7 |
| N-07 | browser current-required 파일을 F 집중 검사에 포함 | §7 F |

K-1/K-2를 채택한 근거는 검토자 수나 전체 WARN/FAIL 중 선택이 아니라 아래 §4의 재현 결과다. full gate 전체의 첫 실패 위치까지 재현한 것은 아니며, 동일한 classification 입력을 사용하는 canonical 경로의 준비 상태와 F collection 실패를 구분해 기록한다.

### Explicitly Out Of Scope

- 설명의 의미·문체 교정, 새 사실 추가, 미확정 사실의 확정, 바닐라 생존 범위 변경.
- canonical JSON, newline, Unicode 또는 Lua escaping의 **기존 의미 변경**과 이를 위한 `.gitattributes` 정규화.
- 기존 authority/adoption/봉인 파일 덮어쓰기, current 포인터 전환, strict finalization, 배포·게시.
- Lua API 제거나 deprecation 결정, legacy generation 지원 중단.
- accepted Tooltip B guard 대상 파일 변경, B 재수락을 필요로 하는 Lua 하위 변경, `MENU_RUNTIME` 허용 집합 확장.
- Iris 전체 재설계, JVM 런타임 도입, Pulse 또는 다른 spoke의 기능 변경.
- 테스트의 검증 대상·실패 기준 완화, 검증 수를 줄이기 위한 required 항목 삭제.

---

## 3. Non-Goals

- 런타임 성능 개선이나 저장 공간 절감률을 보장하지 않는다. 이득은 실제 변경 뒤 측정한다.
- 모든 `canonical()`·`lua_quote()`·경로 함수를 하나의 동작으로 통일하지 않는다.
- `v1`, `v2`, `round`, 날짜가 이름에 있다는 이유로 코드를 폐기하지 않는다.
- 새 검증 authority, 승인 lifecycle, 범용 규칙 엔진 또는 동적 플러그인 등록 체계를 만들지 않는다.
- 자동 검사 성공을 설명 품질 승인이나 실제 PZ 표시 검증으로 확대하지 않는다.

---

## 4. Assumptions

### 현재 코드에서 확인한 기준

아래 줄 수와 상태는 조사 시점의 checkout 관찰이다. 다른 worktree나 후속 교정 결과로 자동 승계하지 않는다.

| 영역 | 실제 확인 사항 | 계획에 반영할 판단 |
|---|---|---|
| 설명 조합 | `description_composition_uses.py` 2,823줄. `frames()`가 423행에서 시작하고 다음 최상위 함수 `prepare()`는 2,596행에서 시작한다. `output`, `used`, `material_frames`, `select`, `emit`을 공유한다. | 기능군 분리 시 실행 순서·중복 소비·공유 조립 상태를 명시적으로 보존 |
| 기존 분리 구조 | `description_composition_families.py` 917줄, planner/model/KO/EN 모듈과 `prepare`·`arrange`·`finish_units`가 이미 존재한다. | 기존 분리점을 사용하고 두 번째 planner나 표현 엔진을 만들지 않음 |
| lexicon | `description_composition_lexicon.py`가 `recovery_expression`, `recovery_sources`, `expression_rules`, `acquisition_expression`을 import한다. | 실제 사용하는 어휘·predicate 정의를 분리하되 판정 책임은 이동시키지 않음 |
| recovery | `recovery_sources.py` 5,289줄, `recovery_migration.py` 3,569줄, `recovery_adjudication.py` 2,281줄. 주요 함수는 `extend`, `adjudicate`, `reassess`다. | 파일 전체 재작성보다 공통 인덱스와 기능군별 단계 분리 |
| 검증 실행기 | `Iris/validation/execution/run_repository_tests.py` 3,373줄. `build_source_census`, `run_gate`, `run_full_repository_gate`와 계약 검사·자료 복원까지 포함한다. | 기존 실행기 진입점 뒤에서 책임을 분리 |
| 활성 v2 경로 | `RepositoryContext.create()`가 `Iris/build/description/v2`를 요구한다. `run_required_contract_tests.py`는 v2 테스트 및 `tools.build` import 허용 집합을 사용한다. | `iris_tooling` 이외 경로를 일괄 legacy 처리할 수 없음 |
| 13,219줄 파일 | `Iris/build/description/v2/tools/build/dvf_3_3_registry_authority_canonical_closure.py`. 같은 이름의 테스트가 현재 `required_validations.json`에 다수 등록되어 있다. | 참조 조사 신호일 뿐 존속 authority는 아님. exact current contract/반복 실행 의무를 먼저 판정 |
| JSON | `public_text/emission.py`와 `dvf_3_3_generation_contract.py`에는 compact JSON + LF 계약이 있다. `content_addressed_archive.py`의 canonical JSON은 indent 2 + LF다. | 동일 계약끼리만 공통화하고 서로 다른 직렬화 profile 유지 |
| Lua 문자열 출력 | recipe index의 `lua_quote`는 역슬래시·따옴표·LF·CR을 처리한다. fixing index의 함수는 역슬래시·따옴표만 처리한다. | 함수 이름이 같아도 대체 가능하다고 판단하지 않음 |
| Lua 조회 | `IrisLayer3DataLookup.lua` 한 파일이 product와 legacy 조회를 선택한다. 현재 `IrisLayer3DataCurrent.lua`는 `iris_layer3_generation_pointer_v1`을 가리킨다. | product 코드가 존재한다는 이유로 현재 runtime 전환을 가정하지 않음 |
| Wiki | `IrisItemDetailPresentation`에 unit profile과 visible row가 이미 있다. `IrisWikiSections`에는 무게·음식 속성 조립 중복이 남는다. | Presentation/profile은 수정 없이 재사용하고 WikiSections/Panel 내부 조립만 정리 |
| 보관 | `Iris/validation/artifacts/content_addressed_archive.py`와 archive/prune 도구가 이미 있다. r6 대용량 4개 JSON에는 LFS 속성이 있다. | 새 보관 방식 신설보다 기존 복원·manifest 구조의 적용 가능성 조사 |
| 산출물 writer | A의 `test_layer3_composition_contract`는 `write_result(..., replace=True)`, 설명 테스트는 `write_result(ROOT, result)`를 실행한다. | A를 기준 checkout에서 직접 실행하지 않음 |
| Recovery 설치 | `installed_identity()`는 해당 subject의 `Iris/tooling/.venv/Lib/site-packages`와 `-I -B`를 요구한다. | subject마다 non-editable 설치, `--no-sync` 실행 및 설치/source hash 확인 |
| B→C 인계 | B 테스트는 repository `.tmp` 아래 tmp_path를 요구하며 `IRIS_SHARED_MENU_VALIDATION`이 있어야 ZIP 경로를 환경에 남긴다. | 전용 basetemp, 동일 pytest 프로세스, 정확한 path/hash 전달 |
| B runtime guard | Menu stage는 `MENU_RUNTIME` 및 명시적 data 예외 밖의 retained B media drift를 거부한다. | Change 7 허용 목록을 좁히고 guard 비교와 product contract 유지 |
| B supply 기본값 | `tooltip_s2_supply.DESCRIPTION.sha256`은 `8510f3003f7150ad034d83ef1496a2540b3fc5ac62acecb622d7c3bce7ba6ed3`이고 실제 corpus는 `8e1eda45…`다. `supply.build(root, description_ref=None)`의 default가 현재 파일을 거부한다. | stale default를 자동 갱신하지 않고 후보 경로만 A의 명시적 ref를 전달 |
| B 중첩 호출 | `test_s2_supply_and_owner_integration`의 두 직접 supply 호출뿐 아니라 `s2_candidate.build(root, output)` 내부에도 인자 없는 `supply.build(root)`가 있다. | 직접 호출과 두 handoff build 모두 같은 ref를 전달; 중첩 호출 누락 금지 |
| B baseline locator | `tooltip_s2_supply.current_support()`는 route index의 `tooltip_t1_production_handoff.final_root`를 읽고 subject 안의 경로인지 검사한다. 현재 값은 `C:/Users/MW/Downloads/coding/PZ/.tmp/z/v/f`다. | 단순 복사로 격리 입력 준비를 완료하지 않음; 기존 계약에 맞는 subject-local locator/동일 handoff 입력을 확보하지 못하면 B/E는 입력 BLOCKED |
| Round 3 분류 | `Iris/build/description/v2/tests/conftest.py::pytest_configure`가 전체 controlled source inventory를 먼저 검사한다. 아래 5개가 미분류다. | F는 명시적 focused 경로로 변경. canonical full gate의 분류 정책은 그대로 두고 BLOCKED 기록 |
| 절대 경로 | `Iris/build/tools/oneshots`의 개인 경로와 `Iris/test/run_pz_core_refactor_harness.ps1`의 PZ/사용자 옵션 기본 경로를 확인했다. | 활성 실행 설정과 과거 일회성 경로를 구분하고 Windows 경로 거부 조건을 검사하는 테스트 문자열은 유지 |

### 작업 상태와 설명 기준

- 현재 checkout에는 `docs/ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md`의 기존 수정과 여러 untracked 자료가 있다. 작성 전부터 존재한 변경을 리팩토링 결과로 포함하지 않는다.
- `codex/iris-dvf-purpose-correction-20260915`와 main의 HEAD는 같은 `aeabeda2…`다. 재조사한 `description_composition_uses/results`, `recovery_sources/migration/adjudication`, `product_projection/install`, `blocks.json`, `descriptions.json`의 raw hash도 모두 같았다. 앞선 1,732개 status 항목을 미병합 의미 변경의 증거로 사용하지 않는다. 이 비교는 worktree 전체의 동일성 보증은 아니다.
- 실제 `Iris/build/description/composition/descriptions.json` SHA-256은 `8e1eda45bb75482d69cb352a4676232b0824debc4c0be2a3d173d5c50b933c03`이었다. 저장된 summary는 2,105 items / 8,420 states, 각 locale/surface마다 present 1,976 / absent 129이며 failed 항목은 없다. 이것은 읽은 파일의 상태이지 새 검증 PASS가 아니다.
- 위 값은 [2026-09-15 교정 기록](iris_dvf_correction_2026-09-15.md)과 대응한다. `ROADMAP.md`의 이전 `2301a4a4…` 후보 기록을 현재 파일의 해시로 사용하지 않는다. 실제 착수 때 파일과 reader를 다시 확인한다.
- `recovery.load_adopted(..., historical=False)`의 immutable 소비와 `historical=True`의 과거 producer 재현은 구분되어 있다. 소스 재배치로 현재 소비를 과거 재현에 다시 결합하지 않는다.
- Windows PowerShell을 실행 환경으로 사용한다. `uv`, Python 프로젝트 환경, Lua/luac 및 필요한 PZ 실행 환경은 해당 검증 직전에 확인한다. 도구 존재만으로 검증 완료를 주장하지 않는다.

### 이번 수정에서 확인한 실행 전 실패

- K-1: 현재 checkout의 `Iris/tooling/src`를 명시적으로 import한 읽기 전용 probe에서 `tooltip_s2_supply.build(root)`가 `TooltipContractError: description bytes changed`를 반환했다. source 해시/현재 corpus 불일치 검사에서 끝났으며 supply/candidate 산출물을 생성하지 않았다. 이는 설치본·전체 B/E 검증이 아니다.
- K-2: 개정 전 F의 5개 테스트 파일을 `python -B -m pytest -p no:cacheprovider --collect-only -q ...`로 수집했을 때 exit `3`과 `Round 3 source classification is incomplete`를 확인했다. 누락 집합은 `test_layer3_composition.py`, `test_layer3_description_composition.py`, `test_layer3_dvf_purpose_review.py`, `test_layer3_recovery.py`, `test_layer3_rule_generalization.py`다.
- 같은 집중 검사에 `--noconftest -c Iris/tooling/pyproject.toml`을 적용하고 browser current-required 파일도 포함한 6개 파일은 **collection exit `0`, 12 tests collected**였다. pytest 본문·Lua harness는 실행하지 않았다. `-p no:cacheprovider`와 `-B`로 읽기 전용 확인의 cache/bytecode 출력을 막았다.
- `execution/contracts/repository_test_gate.json`의 `--round3-contract current` 및 실제 runner의 command 구성은 같은 conftest를 사용하는 canonical 경로다. 이번에 full gate를 실행한 것은 아니므로 그 전체 실행의 exit나 첫 실패를 단정하지 않는다. 분류 누락을 도구 부재로 잘못 기록하지 않는다.
- 재현 명령·stdout/stderr 요약은 임시 `iris-plan-review-c37b5c8bec334a478a3158dbc92e3f56/findings.json`에 남겼다. 이 관찰을 미래 subject의 PASS로 승계하지 않는다.

---

## 5. Repository Areas Affected

경로는 저장소 루트 기준이다. 아래는 계획 실행 시의 영향 영역이며 이번 문서 작성에서 이 파일들을 수정한다는 뜻이 아니다.

### Code

- `Iris/tooling/src/iris_tooling/domains/layer3/`: `description_composition_*`, `recovery*`, `product_projection.py`, `product_install.py`.
- Change 1의 제품 코드 입력 전달: 위 `product_projection.py`/`product_install.py`와 `Iris/tooling/src/iris_tooling/domains/tooltip_t1/s2_candidate.py`. `layer3/tooltip_s2_supply.py`의 기존 `description_ref` API를 재사용하며 stale default 상수는 유지한다.
- `Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/`: `install.py`, serialization/manifest 소비 코드.
- `Iris/tooling/src/iris_tooling/build/`: `repository_context.py`, index producer, composition 진입점 및 실제 활성 build 모듈.
- `Iris/tooling/src/iris_tooling/__main__.py`, 각 `domains/*/cli.py`.
- `Iris/validation/execution/`, `source_analysis/`, `artifacts/`, `test_coverage/`의 관련 실행 코드와 테스트.
- `Iris/build/description/v2/tools/build/`, `Iris/build/tools/common/`, `Iris/build/tools/oneshots/`의 조사 후 확정된 대상.
- Lua 수정은 Change 7의 허용 목록 및 신규 내부 모듈에 한정한다. 나머지 Browser/Detail/Tooltip 파일은 호환 검사 입력이다.
- `Iris/tools/package_iris.ps1`의 해당 support 목록과 product producer inventory: 신규 Lua 의존 모듈의 결속·포함·검증에 필요한 변경만 수행한다.
- `Iris/test/lua/`, `Iris/_dev/`의 해당 harness, `Iris/test/run_pz_core_refactor_harness.ps1`.
- 제안 신규 경로: `iris_tooling/common/` 및 Layer 3 기능군별 내부 모듈. 이름은 책임 확정 후 결정한다.
- 검증 fixture 보완: 기존 A/B/E 테스트의 subject/import 확인, 후보 binding 전달, 전후 payload 비교. §7의 임시 실행 보조물은 작성 예정이며 현재 정규 validator/등록 항목이 아니다.

### Docs

- `docs/iris_refactoring_implementation_plan.md`: 이 계획과 단계별 진행/보류 상태.
- 구현 완료 시 실제 경계 변화만 `docs/ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md`에 반영한다. 기존 수정·역사적 실행 기록과 충돌 여부를 먼저 확인한다.
- 관련 기존 설명 composition/recovery 문서는 소비 계약을 확인하는 참고 자료다. 과거 바이트 결속 문서를 경로 정리 목적으로 일괄 수정하지 않는다.

### Config

- `Iris/tooling/pyproject.toml`, 루트 `pytest.ini`: discovery·실행 방식 변경이 실제 필요할 때만 수정.
- `Iris/validation/execution/required_validations.json`, `current_environment.json`과 `_docs/round3`의 taxonomy/closure: 현재 locator 변경에 필요한 기존 갱신 경로 사용. 과거 identity를 소급 수정하지 않음.
- `.gitattributes`: 기존 속성은 유지한다. `core.autocrlf=true`이므로 새 `iris_tooling/common/` 등 raw-bound 파일이 기존 `-text` 범위를 벗어나면 해당 파일/책임 경로에 `-text`를 추가한다. `git check-attr text eol filter -- <path>`와 새 checkout의 raw hash로 확인한다. 기존 파일의 개행 정규화는 하지 않는다.

### Generated Artifacts

- `Iris/build/description/composition/blocks.json`, `descriptions.json`: 기준 checkout에서는 원 bytes를 유지한다. A가 쓰는 고정 경로는 disposable before/after subject 안에서만 후보 출력으로 사용한다. 코드 병합에는 이 생성 diff를 포함하지 않는다. 이후 정식 산출물 갱신은 기존 owner 절차로 별도 수행한다.
- `Iris/_docs/authority/dvf/layer3_expression/successors/`: 의미/근거 비교 입력 및 역사 보관 판단 대상. r6의 채택 결과와 원 bytes 보존.
- `Iris/media/lua/client/Iris/Data/`: 기존 pointer·generation·tooltip bytes는 기준점. 새 제품 검증은 격리된 후보에서 수행.
- `.tmp/tooltip`, `.tmp/menu` 또는 기존 실행 계약이 정한 외부 workspace: 비교·설치 복구·package 검사 출력. 실행 경로마다 다른 출력 경계 계약을 그대로 적용.

---

## 6. Planned Changes

### Change 1 — 비교 기준과 착수 경계 확보

**Purpose:** 의미 교정·구조 변경·과거 자료 재현을 구분할 수 있는 실행 기준을 만든다.

**Files:** 현재 Layer 3 producer/reader, `tooltip_t1/s2_candidate.py`, `layer3/product_projection.py`/`product_install.py`, composition 산출물, `required_validations.json`, `pytest.ini`, `git status` 및 worktree 상태, 기존 회귀 fixture.

**Implementation Notes:**

1. 기준 checkout `Origin`, 별도 `Before`/`After` disposable subject와 증거 출력 `Evidence`를 구분한다. 각 subject의 정확한 commit·source hash·필수 untracked 입력을 명시한다. 기존 source와 생성물 snapshot은 Origin에서 읽기만 한다.
2. 두 subject에 같은 바닐라/authority 입력과 필요한 로컬 B ZIP을 raw hash 확인 후 제공한다. Origin의 `.venv`를 복사하거나 Origin에 재설치하지 않는다. §7 공통 준비에 따라 각 subject를 non-editable 설치한다.
3. Origin의 `blocks.json`, `descriptions.json`, r6, pointer, accepted 상수와 관련 입력 hash를 먼저 저장한다. 두 composition JSON은 §7의 byte copy로 `$Evidence/origin-composition`에 실제 snapshot도 만든다. A writer는 두 subject의 고정 경로에만 쓰며 검증 성공/실패 후 모두 Origin의 hash를 다시 확인한다.
4. before 생성 결과를 기존 저장 결과와 먼저 비교한다. 이후 after를 before와 비교한다. 기존 저장 결과를 현재 producer가 재현하지 못하면 그 차이를 숨기지 않고 기준 적합성을 다시 판단한다.
5. Recovery는 같은 입력에서 before/after **신규 candidate**를 각각 생산·검사하고 payload를 비교한다. r6는 immutable 입력이며 refactored producer의 before/after 후보를 대신하지 않는다.
6. E 실행에 필요한 입력 전달과 후보 fixture를 먼저 보완한다. B의 두 직접 `supply.build`에는 기존 `description_ref` 인자를 사용한다. `s2_candidate.build(root, output, *, description_ref=None)`에는 같은 ref를 내부 supply에 전달하는 경로를 추가하고 두 handoff 생성 호출에도 적용한다. C producer와 installer까지 A의 `description`/`blocks` 기대 binding을 전달한다. 이는 **Change 1의 제품 코드 변경**이며 테스트만 수정한 것으로 기록하지 않는다. 기존 current/accepted 상수 변경이나 manifest 자기 검증으로 대체하지 않는다.
7. installed module/source hash, 테스트 ROOT/REPO, 후보 전달/비교를 위한 최소 보조물을 기존 테스트에 붙인다. 새 정규 validation authority를 만들지 않는다. 아직 작성되지 않은 보조물은 §7에 명시하며 구현·검증 전 해당 실행 단계를 준비 완료로 표시하지 않는다.
8. 입력 전달 변경의 검증 경계를 별도로 남긴다. 원본 commit과 **입력 전달만 보완한 commit**을 각각 격리 subject에서 설치해 default 거부 동작, 기존에 지원하는 명시적 supply 입력·순수 projection의 동일 입력 결과, 잘못된 ref 거부를 비교한다. 현재 원본은 K-1 때문에 E를 성공시킬 수 없으므로 원본→보완본 전체 E 성공 동등성을 주장하지 않는다. 보완본에서 신규 B→C 전체 연결을 검증한 뒤 해당 commit과 fixture를 구조 리팩토링의 `Before`로 고정한다. `After`는 그 기준에 책임 분리만 추가하고 같은 fixture로 검증한다. 최초 입력 전달 변경의 diff·identity·거부 조건 검증은 별도 기록으로 계속 보존한다.

입력 전달 보완본의 최초 검증은 그 subject만으로 공통 준비→A 생성→Origin snapshot과의 payload 비교→그 결과의 ref를 사용하는 E 순서로 수행한다. 이때 아직 없는 구조 변경 After와의 비교를 선행 조건으로 두지 않는다. 이후 Before를 고정하고 아래 §7의 Before→After 절차를 적용한다. 두 경계 모두 실제 producer commit/source에 종속된 identity 차이만 별도로 확인하며 payload 차이를 허용하지 않는다.

**Validation:** baseline reader, subject/import 대응, 설치 형태, 후보 writer 격리, before/after 비교 및 E 전달 fixture를 확인한다. 입력 전달 변경 자체의 전후 검증과 이후 구조 리팩토링 전후 검증을 구분한다. 변경된 B/Menu producer·installer도 non-editable 설치 및 source identity 검사를 통과해야 한다. Layer 3 producer closure를 건드리는 Change 3/4/5/8/12는 이 조건이 필요하다. 순수 runner 등 독립 변경은 같은 이유로 자동 보류하지 않는다.

### Change 2 — repository runner 내부 분리

**Purpose:** 검증의 의미를 보존하면서 실행 흐름을 읽고 수정하기 쉽게 만든다.

**Files:** `Iris/validation/execution/run_repository_tests.py`, `checkout_environment.py`, `pytest_outcome_recorder.py`, `execution/tests/test_repository_test_execution.py`, 필요 시 `source_analysis/` 내부 모듈.

**Implementation Notes:**

- 기존 `source-census`, `gate`, `full-gate` CLI 및 함수 표면을 adapter로 유지한다.
- 테스트·import·required dependency 조사는 source analysis 책임으로, evidence/compiler identity와 current capsule 검사는 계약 확인 책임으로 분리한다.
- frozen fixture·runtime mirror·current output seed·disposable checkout 구성은 workspace 책임으로 분리한다.
- subprocess·pytest 결과·stdout/stderr·status 수집과 최종 보고를 실행 책임으로 분리한다.
- 기존 함수 import 및 monkeypatch 사용도 조사한다. 내부 함수 이름만 유지하고 patch 대상이 분리 코드에 전달되지 않는 회귀를 피한다.
- 첫 변경에서는 `invoke_repository_tests.ps1`의 환경 적용·복원·receipt 기록을 유지한다. Python 중심화는 중복된 순수 판단 로직부터 옮기며 PowerShell의 Windows 환경 책임을 남긴다.
- 종료 코드, 외부 workspace 제약, clean subject, source census, required evidence, 실패 우선순위와 결과 schema를 보존한다. 현재의 예외 exit 2 / 결과 실패 exit 1 / 성공 exit 0을 임의 통일하지 않는다.

**Validation:** execution 테스트의 성공/실패 fixture, 환경 일부 적용 실패·복원 실패·native 실패 우선순위, 바이트가 다른 결과 거부, repository 오염 검사를 사용한다. fake runner를 생성하는 launcher fixture의 성공은 환경 wrapper 검증으로 한정한다. §7 C에서 실제 before/after runner로 source-census JSON을 비교하고, 추출한 workspace/실행/수집 경로를 통과하는 실제 runner 실행을 별도로 수행한다.

**현재 차단 조건:** `Iris/build/description/v2/tests/conftest.py`의 미분류 5개 source 때문에 canonical full-gate는 준비 상태를 **BLOCKED — 기존 Round 3 classification 누락**으로 기록한다. classification을 임시 수정하거나 canonical 실행에 `--noconftest`를 넣지 않는다. source-census·독립 fixture 결과와 이 차단은 별도로 보고한다. 기존 owner 절차에서 해소한 유효한 subject로 최종 full gate가 끝나기 전에는 Change 2만 미완료로 남긴다. 독립 변경은 계속 진행하고 개별 완료를 인정한다. 전후 동일 실패는 실패 보존 관찰이며 성공 동등성의 대체물이 아니다.

### Change 3 — 같은 계약의 공통 유틸 추출

**Purpose:** 중복 구현을 줄이되 직렬화와 파일 안전성의 의미를 유지한다.

**Files:** `public_text/emission.py`, `build/dvf_3_3_generation_contract.py`, index producer의 `lua_quote`, `layer3/*`의 canonical/digest, `Iris/build/tools/common/io.py`, 제안 `iris_tooling/common/`.

**Implementation Notes:**

- 먼저 hash 대상이 raw bytes인지, LF 정규화인지, 특정 필드의 의미 projection인지 나눈다. `raw_sha256`, `eol_lf_sha256`, `category_locale_sha256`는 서로 대체하지 않는다.
- JSON의 key 순서, separators, indent, trailing LF, ensure_ascii, 반환 타입을 비교해 동일한 계약끼리 추출한다. 서로 다른 계약에는 명시적인 별도 함수/profile을 둔다.
- Lua escaping은 recipe/fixing/moveables 등 호출자별 입력 범위와 출력 bytes를 확인한다. 제어 문자, 역슬래시, 따옴표, 한글·영문, 빈 문자열을 포함한 기존 계약을 유지한다.
- 경로는 repository 내부 product, 외부 validation workspace, archive logical path의 제약을 분리한다. 하나의 느슨한 `resolve()` helper로 바꾸지 않는다.
- 공통 모듈은 표준 라이브러리와 순수 입력에만 의존한다. domain/build/validation owner나 repository 초기화에 역의존하지 않는다.
- 기존 함수는 필요한 호환 기간 동안 얇은 wrapper로 남긴다. 새 helper가 producer identity 목록에서 빠지지 않게 실제 입력 목록을 함께 갱신한다.
- Layer 3 producer 파일을 변경하는 경우에는 Change 4–5와 동일하게 §7의 non-editable 설치, A 격리, 후보 비교와 필요 시 E binding을 사용한다. common 경로의 신규 raw-bound 파일은 `.gitattributes` 적용과 checkout 간 raw hash를 먼저 확인한다.

**Validation:** 같은 입력의 bytes/hash 및 잘못된 path 거부가 동일해야 한다. 기존 generation/serialization/archive 관련 테스트를 재사용하고, 확인된 계약 차이에만 fixture를 보완한다. 개행 정규화나 hash 정책 변경은 이 단계에 포함하지 않는다.

### Change 4 — lexicon 결합 축소와 설명 frame 기능군 분리

**Purpose:** 한 기능의 표현을 고칠 때 거대한 `frames()` 전체를 수정하지 않도록 한다.

**Files:** `description_composition_uses.py`, `description_composition_families.py`, `description_composition_lexicon.py`, planner/model/results, `recovery_expression.py`, `recovery_sources.py`의 공유 정의.

**Implementation Notes:**

1. lexicon이 실제 소비하는 문구 사전·predicate 상수·body label 등을 독립 정의로 추출한다. recovery 구현과 표현 구현이 함께 소비하도록 하고, 같은 값을 양쪽에 복제하지 않는다. 정의 파일에 source 읽기·fact 생성·판정 side effect를 넣지 않는다.
2. `frames(plan, locale, links, compact)` 진입점을 유지하고, `units`, `used`, `output`, `material_frames`, `links`, locale/surface를 갖는 명시적 내부 조립 상태를 도입한다. 이는 함수 호출별 상태이며 module singleton이 아니다.
3. `select`·`emit`·허용 predicate·근거 연결·중복 소비는 공통 흐름으로 남긴다. 기능군 handler는 선택한 사실로 어떤 문장을 만들지 담당한다.
4. 점화/연료/물, 음식/조리/포장, 의료/착용, 도구/건축/재료, 차량/장치/매체 등 기존 분기 묶음부터 순차 추출한다. 단순한 primary family 하나로 분류하지 않는다. 한 아이템의 독립 용도가 여러 handler를 통과할 수 있어야 한다.
5. 기존 handler 호출 순서와 `used` 갱신 시점, material frame 병합, `PURPOSE_NEIGHBORS`, `prepare`→frame→`arrange`/`finish_units`의 관계를 유지한다. 파일명 정렬이나 set 순회로 순서를 결정하지 않는다.
6. compact와 expanded의 독립 구성, KO/EN의 동일 의미 선택, qualifier 범위와 target group/detail 연결을 보존한다. expanded 절단이나 FullType별 대체 문장으로 parity를 맞추지 않는다.
7. `description_composition_results.produce()`가 파일 이름 목록으로 producer hash를 묶으므로, 모든 새 정의/handler를 실제 producer 목록에 반영한다. 과거 hash를 새 코드의 hash인 것처럼 재사용하지 않는다.

**Validation:** 전체 8,420 좌표의 문장·세그먼트·순서·상태·근거·상세 연결이 기준과 같아야 한다. 다중 용도 도구, 점화/연료, 조건부 물 사용, 음식 재료, 차량 부품, 미확정 제련 범위 등 기존 위험 사례와 일반화/목적 회귀 테스트를 실행한다. producer metadata 차이는 7절의 별도 규칙으로 검토한다.

### Change 5 — recovery 단계별 기능군 분리

**Purpose:** 원본 근거 수집과 과거 문장 해석, 질문 판정의 경계를 유지한 채 각각의 복잡도를 낮춘다.

**Files:** `recovery.py`, `recovery_sources.py`, `recovery_migration.py`, `recovery_adjudication.py`, `recovery_relations.py`, 관련 source reader/model, 기존 `test_layer3_recovery.py`.

**Implementation Notes:**

- `recovery.py`는 입력 묶음·후보 조립·reader/handoff의 책임을 유지한다.
- `recovery_sources.extend()`는 공통 원본 읽기·declaration/recipe 인덱스·builder를 준비하고 기능군별 근거 추출을 호출한다. 기존 `recover_participation`, `baking_roles`, `welding_roles`, `spear_roles`, `supplement_*` 경계를 먼저 활용한다.
- migration의 `extract`/`interpret`와 `adjudicate`를 분리한다. 과거 설명에서 추출한 주장을 새 사실 근거로 승격하지 않는다.
- adjudication의 `reassess`와 `reconcile_direct_claims`는 공통 question/result 조립과 기능군 판정을 분리한다. attributed 처리, 미확정·실패·잔여 상태의 우선순위를 보존한다.
- 사실/evidence 생성 순서, 정렬, ID 계산, provenance ref, observation binding, qualifier application을 유지한다. 기능군별 새 ID 규칙을 만들지 않는다.
- description handler와 recovery handler를 하나의 범용 registry로 합치지 않는다. 각각 표현 책임과 근거/판정 책임을 갖는다.
- 기존 adopted r6는 immutable 입력으로 남는다. 현재 immutable 소비와 historical replay, candidate 검사 경로를 유지하고 새 후보만 실제 producer identity를 가진다.

**Validation:** §7 B의 before/after 신규 candidate에 각각 contract test를 적용한 뒤 semantic/acquisition/expression/audit payload를 비교한다. contract PASS와 두 후보의 동등성은 별개의 결과다. 새 helper까지 설치/source identity와 producer 입력 목록에 포함한다. 사실·근거·question 판정·잔여 사유에 차이가 생기면 구조 변경을 멈추고 별도 의미 교정으로 분류한다.

### Change 6 — installer 공통화 실익 판정 및 조건부 추출

**Purpose:** 중복된 atomic write 구현을 줄이고 두 설치 경로의 복구 책임을 명확하게 유지한다.

**Files:** `layer3/product_install.py`, `tooltip_static_data_projection/install.py`, 필요한 공통 파일 I/O 모듈, product/tooltip 설치 회귀 테스트.

**Implementation Notes:**

- 현재 두 `atomic_write`는 각각 약 8–9줄이고 `.stage`·독점 생성·flush/fsync·replace는 같지만 parent 생성과 오류 메시지가 다르다. 중복량 대비 lock/journal/중단 회귀 부담을 먼저 평가한다. 지금은 추출 자체를 필수 완료 조건으로 두지 않는다.
- 이번 범위에서 향후 변경 비용이 실제 줄어드는 근거가 없으면 **no-op — 두 구현 유지**로 처리한다. 같은 I/O 계약을 여러 활성 소비자가 공유하는 등 실익이 확인될 때만 아래 추출을 채택하고 §7 E의 복구 검증을 수행한다.
- 임시 파일 생성·byte write·flush/fsync·동일 파일시스템 내 replace 등 실제로 동일한 부분만 추출한다.
- 임시 파일 suffix와 cleanup 방식도 기존 recovery가 소비하므로 명시적으로 전달한다. helper가 자체 lock/journal 정책을 갖지 않게 한다.
- Menu의 product pointer·facade·generation journal과 Tooltip의 static data/recipe variant 묶음은 각각 기존 owner에 남긴다.
- lock 획득, concurrent writer 거부, `before`/`after` hash, 중단 시 남길 journal, recover 순서와 예외 종류를 보존한다.

**Validation:** 쓰기 전/도중/replace 후 중단, 이미 존재하는 lock, 다른 writer의 변경, backup 손상, `KeyboardInterrupt`를 기존 fixture로 검사한다. 실패 뒤 원래 bytes로 복구되는지 확인하며 실제 current 설치는 수행하지 않는다.

### Change 7 — B guard를 보존하는 Menu Lua 국소 책임 정리

**Purpose:** 현재 UI와 API 동작을 유지하면서 반복되는 조립과 lifecycle 처리를 줄인다.

**Files:** `IrisLayer3DataLookup.lua`, `IrisBrowserDetail.lua`, `IrisWikiSections.lua`, 필요한 `IrisWikiPanel.lua`/`IrisItemDetailModelAssembler.lua`, B ZIP에 없는 신규 내부 모듈. Lua 파일은 `Iris/media/lua/client/Iris/` 아래에 둔다. 의존 모듈을 결속하는 `layer3/product_projection.py`와 `Iris/tools/package_iris.ps1`의 해당 목록도 영향 범위다.

**Implementation Notes:**

현재 `product_projection.MENU_RUNTIME`은 다음 6개다: `Data/IrisLayer3DataLookup.lua`, `Data/layer3_renderer.lua`, `UI/Detail/IrisItemDetailModelAssembler.lua`, `UI/Wiki/IrisWikiSections.lua`, `UI/Wiki/IrisWikiPanel.lua`, `UI/Browser/IrisBrowserDetail.lua`. 이는 허용 가능한 변경 집합이며 모두 수정하라는 뜻은 아니다. 이번 계획에서 이 집합을 확장하지 않는다.

**선택한 경로는 guarded 파일 변경 제외 및 해당 하위 변경 보류다.** 아래 7개를 포함해 accepted B ZIP의 나머지 retained media는 원 bytes를 유지한다: `IrisBrowserInteractionRenderer.lua`, `IrisBrowserInteractionState.lua`, `IrisItemDetailPresentation.lua`, `IrisWikiUnitProfiles.lua`, `IrisItemFactReader.lua`, `IrisAltTooltip.lua`, `IrisTooltipSummary.lua`.

| 하위 변경 | 이번 처분 | 보존 조건 |
|---|---|---|
| Browser Detail | 허용 파일에서 콘텐츠·child 위치/스크롤·entry 위치 갱신을 내부 모듈로 분리 | `install`과 Renderer가 호출하는 메서드, Lua/Java children·scroll·focus |
| 검색 위젯 slot 공통화 | Renderer 수정을 요구하는 부분 보류 | Detail 쪽 정리는 기존 Renderer API로 가능할 때만 수행 |
| 상태 초기화 | `IrisBrowserInteractionState` 변경 보류 | 일반/Evolved 저장소와 query reset은 그대로 |
| DataLookup | 허용 router에서 product/legacy 내부 구현 분리 | pointer·세션 캐시·형식·reason·호환 전체 적재 |
| Wiki 표시 | WikiSections/Panel 안의 중복 조립만 정리 | 기존 Presentation/profile을 수정 없이 사용; 그 제약으로 불가능한 공통화는 보류 |
| 계측 | ModelAssembler 내부의 주석/중복만 실익 검토 | 기존 필드와 counter 의미 유지; guarded tooltip/fact reader 계측 추출은 보류 |

새 모듈은 기존 B ZIP에 같은 경로가 없는지 확인하고 source/package에 포함한다. guarded 파일을 새 B 후보에 넣어 차이를 숨기는 방식은 허용하지 않는다. Origin의 accepted B ZIP과 비교한 retained media hash도 별도로 확인한다.

**신규 모듈의 producer/package 책임:**

- Menu v2 `build_menu_product()`는 `Iris/media`의 파일을 동적으로 producer에 수집한다. 새 Lua 파일이 제외 디렉터리에 있지 않고 실제 producer 목록·stage·ZIP에 들어갔는지 확인한다. 동적 수집이 package 포함까지 보장한다고 가정하지 않는다.
- Product v1 `build_product()`는 `IrisLayer3DataLookup.lua` 등 Data/UI producer를 명시적 목록으로 결속한다. 분리 후 이 경로가 요구하는 새 모듈을 해당 목록에 추가한다. 기존 목록에 없는 파일을 해시 검증 없이 require하게 두지 않는다.
- legacy package의 `Iris/tools/package_iris.ps1::$supportRelativePaths`는 DataLookup 등 지원 파일을 열거하고 `support_files` hash/존재 검사를 만든다. DataLookup에서 분리한 새 의존 파일을 해당 support 목록과 package 검사에 반영한다. 다른 디렉터리의 신규 의존성도 실제 소비 목록을 조사해 빠짐없이 결속한다.
- 이 갱신은 활성 producer/package 코드에 적용한다. 기존 generation descriptor·adopted 산출물을 소급 수정하거나 `MENU_RUNTIME`을 확장하지 않는다. source→producer inventory→stage→ZIP의 path/hash 대응과 새 모듈 누락·변조 거부를 검사하고, staged/ZIP 경로의 실제 Lua `require`로 의존성 완결성을 확인한다.

- Product v1/v2와 legacy generation의 반환 shape, `get`/`getLocale` 지원 차이 및 reason을 임의 통일하지 않는다. product 손상·unsupported locale을 legacy/다른 locale로 대체하지 않는다.
- `IrisAPI.lua`는 주석과 실제 위임 구조에서 공개 호환 facade임이 확인된다. 평면 wrapper를 유지한다.
- `staticCacheHits`/`staticCacheMisses`는 `IrisItemDetailModelAssembler`에서 실제 증가 조건을 확인한 뒤 이름·주석을 정리한다. 기존 harness/외부 진단 소비 가능성이 남아 있으면 필드 이름을 유지하고 의미를 설명한다.

**Validation:** §7 F의 실제 Python→Lua harness 명령과 §7 E의 `test_layer3_product_integration.py::test_product_contract`를 포함한다. retained B media의 전후 raw hash, stage의 drift guard와 새 모듈 포함을 확인한다. 실제 PZ에서는 변경한 Menu의 스크롤·재오픈·locale/item·검색·IME를 관찰한다. Tooltip/일반·Evolved 상태는 unchanged contract 회귀 범위이며 그 구현을 변경했다고 보고하지 않는다. 보류 항목의 재개는 별도 B owner/재수락 조건 판단 이후이며 이번 완료 조건에 숨기지 않는다.

### Change 8 — 빌드 의존 방향, CLI, 환경 경로 정리

**Purpose:** 실제 producer 책임에 맞는 의존 방향과 이동 가능한 실행 환경을 만든다.

**Files:** `build/repository_context.py`, `__main__.py`, `domains/*/cli.py`, `domains/public_text/naturalization_*`, 활성 build producer, `Iris/build/tools/oneshots/`, PZ harness.

**Implementation Notes:**

- repository context의 위치는 공통 기반으로 옮기되 명시적 `--repository-root`/환경 입력·중복 설정 거부·v2 입력 존재 확인을 유지한다. 경로 이동을 이유로 입력 검사를 없애지 않는다.
- `domains/public_text`의 build composition import 등 실제 역방향 의존을 domain 구현과 build adapter로 분리한다. 기존 build 경로는 필요한 호환 wrapper로 유지한다.
- `__main__._domain_main`을 고정된 target→lazy import 등록표로 정리한다. `tooltip-t2`, legacy command token, remainder 전달, parser error/exit, `validate full` 위임 동작을 유지한다.
- 개인 경로는 활성 스크립트에서만 명시적 인자 또는 기존 environment locator로 대체한다. PZ executable/options 경로는 실행 시 지정하도록 한다. 필수 경로가 없으면 명확하게 실패한다.
- 과거 oneshot은 참조와 필요성을 먼저 판정한다. 보관할 파일을 경로 정리 목적으로 수정해 역사 bytes를 바꾸지 않는다.
- `test_iris_browser_state_selection_search_acceptance.py`의 `C:/Users/MW/Downloads/coding/PZ2/t3d1` 및 `PZ2/t2-final/tooltip_t2_projection_manifest.json`도 조사한다. 전자는 baseline 경계 검사이고 후자는 최초 manifest binding이므로 단순 문자열 치환을 하지 않는다. 활성 의무이면 동등한 명시적 fixture root/identity로 이전하고, historical 의무이면 근거와 처분을 기록한다.

**Validation:** 기존 CLI/repository context 테스트와 실제 사용 command의 도움말·인자 전달을 검사한다. 다른 경로 및 공백·한글 경로에서 실행하고, package 설치 가능성과 root import가 기존과 같아야 한다.

### Change 9 — 테스트 배치와 framework 정리

**Purpose:** 테스트 위치를 책임에 맞게 정리하면서 기존 보호 범위를 유지한다.

**Files:** `Iris/tooling/tests`, `Iris/build/description/v2/tests`, `Iris/test`, `Iris/validation/*/tests`, `pytest.ini`, `pyproject.toml`, required/taxonomy/closure의 current locator, `test_coverage` 도구.

**Implementation Notes:**

- tooling domain 테스트는 `Iris/tooling/tests`, 검증 실행기 테스트는 `Iris/validation/*/tests`, Lua harness는 `Iris/test/lua`를 목표 위치로 한다. 모든 테스트를 한 폴더로 옮기지 않는다.
- `run_required_contract_tests.py`가 unittest class/test ID를 직접 소비하므로 pytest 일괄 변환을 선행하지 않는다. 기존 unittest를 pytest에서 실행할 수 있는 범위부터 활용한다.
- 이동 시 old path/node ID→new path/node ID를 대응시키고 수집 목록·필수 목록·fixtures·동적 import·source closure를 함께 갱신한다. 파일명만 바꾸고 검증 대상이 줄어드는 것을 허용하지 않는다.
- 단순 줄 수/함수 존재를 검사하는 validation anchor는 실제 보호하던 동작을 확인한 뒤 동등한 보호로 교체한다. 새 테스트를 추가하고 기존 검사를 제거하는 경우 누락이 없는지 기존 test coverage 비교를 사용한다.

**Validation:** 수집 개수뿐 아니라 test ID별 보호 대상·skip/제외·실패 주입 결과를 비교한다. migration fixture가 기준이면 그 매핑도 검증한다. required runner에서 같은 범위가 실행되는 것을 확인하기 전 구 경로를 제거하지 않는다.

### Change 10 — 활성 legacy 코드와 완료 라운드 분리

**Purpose:** 큰 과거 경로의 실제 활성 책임을 남기고 명백한 역사 코드를 실행 경로 밖으로 정리한다.

**Files:** `Iris/build/description/v2/tools/build/dvf_3_3_registry_authority_canonical_closure.py`, 관련 run/validate script, 기존 dependency inventory·source census·closure.

**Implementation Notes:**

- 정적 import 외에 문자열 module name, `spec_from_file_location`, `runpy`, subprocess argv, manifest/schema의 경로, package script와 current test를 포함해 소비자를 추적한다.
- 13,219줄 파일의 required membership은 참조 조사 입력이다. `DECISIONS.md`의 regular validation 경계에 따라 exact current product/recurring validation contract, 반복 실행 의무, lifecycle 독립성, 비중복성을 확인해 함수/검사별 존속을 판정한다. membership·census·taxonomy만으로 활성 코드의 존속을 승인하지 않는다.
- 존속할 current 책임이 확인되면 entry/preflight·contract 검증·산출물 구성의 실제 호출 묶음을 분리하고 필요한 adapter를 유지한다. lifecycle-only/one-off 책임은 독립적으로 퇴역/보관할 수 있다. 판정 전에는 조사 편의를 위한 삭제·이동을 하지 않는다.
- 일부 함수만 historical이면 파일 전체를 이동하지 않는다. 현재 실행에 필요한 코드·입력을 먼저 독립시킨 뒤 나머지 보관 가능성을 판정한다.
- 완료 round script는 현재 소비 참조가 없고 명시적 복원으로 역사 재현이 가능한 경우에만 기존 보관 도구로 처리한다. Git에 있다는 이유만으로 필요한 원본을 삭제하지 않는다.

**Validation:** archive 없이 유지 대상 current contract의 실행·검증이 성립해야 한다. 기존 membership 변경이 필요하면 위 근거에 따른 명시적 disposition과 해당 current 검사로 확인한다. 역사 증거의 보존은 모든 과거 executable replay의 존속을 뜻하지 않는다. 복원이 필요한 자료는 기존 복원 계약을 따르고 동적 참조가 불명확한 항목은 보류한다.

### Change 11 — successor 산출물의 보관 구조 검토와 적용

**Purpose:** 중복 저장을 줄일 수 있는 역사 자료를 식별하되 현재 읽기와 증거 추적을 보존한다.

**Files:** `Iris/_docs/authority/dvf/layer3_expression/successors/`, `Iris/validation/artifacts/content_addressed_archive.py`, lifecycle/archive manifest 및 기존 테스트.

**Implementation Notes:**

- 재조사한 r1–r5에는 `git ls-files` 결과가 없었다. 따라서 **이 로컬 사본을 대상으로 한 저장소 중복 제거는 현재 no-op**이다. untracked 자료를 새 tracked archive로 만들거나 로컬 파일을 삭제하는 작업을 자동 추가하지 않는다.
- 다른 tracked 대상이 확인되면 Git/LFS 전송·실제 디스크 절감, current 소비 비용, 복원 비용을 비교해 `adopt`/`defer`/`no-op`을 선택한다. 이는 항목별 처분이며 새 closeout 상태나 authority 분류가 아니다. 실익이 없는 변경은 수행하지 않는다.
- current-required, adopted input, rejected/intermediate candidate, historical replay 자료를 실제 소비 관계로 나눈다. r1–r6를 같은 상태로 취급하지 않는다.
- 현재 r6 채택 소비와 LFS로 관리되는 raw JSON은 그대로 읽을 수 있어야 한다. LFS pointer text를 실제 payload로 해싱하거나 archive하지 않도록 실내용 bytes를 확인한다.
- 이미 있는 content-addressed archive의 manifest·SHA-256·복원 기능을 사용한다. 같은 raw bytes는 공유할 수 있지만 원래 논리 경로·개별 provenance·실패 이력은 모두 남긴다.
- live 참조 부재와 복원 검사가 확인된 역사 항목만 보관 대상으로 확정한다. 현재 reader에 숨은 archive fallback을 추가하지 않는다.
- 이 작업 때문에 authority의 상태나 승인 결과를 재작성하지 않는다. 저장 형식 변경이 기존 owner/봉인 계약 변경을 요구하면 이 계획의 실제 이동 대상에서 분리해 후속 판단으로 남긴다.

**Validation:** archive 생성→검증→독립 경로 복원 뒤 대상별 raw hash와 논리 경로가 일치해야 한다. 손상 object·누락 object·경로 탈출을 거부하고 current-required 자료는 archive 없이 읽혀야 한다.

### Change 12 — 최종 이름·주석·참조 정리

**Purpose:** 책임 분리가 끝난 구조를 이름과 문서에 정확히 반영한다.

**Files:** 앞 단계에서 분리한 활성 모듈, Lua 계측 주석·validation anchor, current locator와 관련 문서.

**Implementation Notes:**

- 날짜/round/version이 구현 책임을 가리는 활성 source만 재명명한다. schema version, CLI token, generation ID, historical manifest 경로는 바꾸지 않는다.
- 이름 변경을 대규모 이동과 함께 하지 않는다. old→new 참조를 확인하고 필요한 wrapper의 이유와 제거 조건을 설명한다.
- `.gitattributes` 정규화·Lua API deprecation은 계속 범위 밖이다.
- 완료 기록에 구현·자동 검증·PZ 관찰·보류 항목을 구분하고 실제 변화만 ecosystem 문서에 반영한다.

**Validation:** 동적 경로를 포함한 참조 검사와 영향받는 기존 테스트를 수행한다. 주석/이름만 바뀐 파일 때문에 producer identity가 변하는지도 확인한다.

---

## 7. Validation Plan

### Automated Validation

#### 최소 검증 실행 정책 — 현재 실행 범위와 횟수

사용자 요청에 따라 리팩토링 대상은 유지하고 **신규 정규 Gate·validator·승인 단계는 0개**로 둔다. 아래 A–H는 매 Change마다 모두 실행하는 체크리스트가 아니라 변경 영향에 따라 선택하는 기존 검증 경로다. 각 Change의 Validation 문장은 보호할 동작을 정의하며 별도 테스트 호출을 추가하라는 뜻이 아니다. 실행 횟수는 이 절을 우선 적용하고, 개별 제품 계약 안의 결정성·실패 주입 검사는 유지한다.

- **관련 변경을 묶어 검증한다.** Change 3/4/5/8/12 중 같은 producer를 건드리는 변경은 최종 묶음으로 A/B를 실행한다. 함수·파일·커밋마다 전체 corpus와 후보를 재생성하지 않는다. 중간에는 변경 동작을 직접 확인하는 기존 node만 사용한다.
- **Before는 한 번 확보하고 재사용한다.** 동일 코드·입력·환경·검사 범위에 결속된 기존 결과가 있으면 새 Before 실행을 생략한다. 결과가 없거나 대응을 확인할 수 없을 때만 한 번 생산한다. r6 입력 자체를 새 producer 검증 결과로 대체하지 않는다. After는 해당 묶음의 최종 코드에서 한 번 실행한다.
- **통합 검사가 포함한 검사는 다시 실행하지 않는다.** 같은 최종 subject에서 E 또는 C가 실제 실행한 node/harness·문법·package 검사는 A/D/F/G의 중복 호출을 대체할 수 있다. 단순히 상위 명령 이름이 같다는 이유로 포함을 추정하지 않고 실행 목록과 결과로 확인한다. 서로 다른 입력·legacy/product 경로의 검사는 동일 검사로 취급하지 않는다.
- **추가 테스트는 기존 검사에 없는 변경 위험에만 쓴다.** 파일 수·함수명·줄 수·추출 구조를 따라가는 테스트, 별도 승인/봉인 테스트는 추가하지 않는다. 입력 전달의 잘못된 ref 거부 등 필요한 사례는 기존 fixture에 추가한다. 임시 비교/subject 확인 보조물은 기존 테스트나 한 개의 임시 도구로 합쳐도 된다.
- **재실행은 원인이 있을 때만 한다.** 관련 source·입력·환경 변경, 실패 수정, 이전 실행에 누락된 보호 범위가 있을 때 영향받은 검사만 재실행한다. 주석·문서 변경만으로 전부 다시 실행하지 않는다. 단, raw-bound producer identity가 실제 바뀌면 그 binding을 소비하는 검사는 갱신한다.
- **차단은 해당 변경과 실제 의존 변경에 한정한다.** classification/full-gate 차단은 Change 2의 미완료로 남기며 독립 Change의 구현·검증·완료를 막지 않는다. 전체 보고는 완료 항목과 미완료 항목을 함께 요약한다. 모든 필수 변경이 끝나기 전 전체 complete를 주장하지 않는 원칙은 유지한다.

| 검증 경로 | 선택 조건 | 기본 실행 횟수 / 재사용 |
|---|---|---|
| A — composition 전수 비교 | 설명 또는 그 입력을 생산하는 코드 변경 | 관련 변경을 묶어 Before 최대 1회 + 최종 After 1회. 기존 동일 Before가 있으면 After만 실행 |
| B — Recovery 후보·계약·비교 | Recovery producer 변경 | Before 최대 1후보 + 최종 After 1후보. 각 후보의 기존 계약 검사와 비교를 같은 실행 흐름에서 처리 |
| C — runner | runner/계약/작업공간/결과 수집 변경 | 영향받은 execution node와 census 비교. 실제 full-gate는 최종 변경 runner에서 1회; 기존 실패가 확인된 Before full-gate는 반복하지 않음 |
| D — CLI/context/serialization | 해당 계약의 구현 변경 | 영향받는 기존 node만 최종 1회. 상위 검사에 실제 포함된 node는 별도 실행 0회 |
| E — B→C 제품 통합 | 입력 전달, 제품 투영·설치 또는 제품 Lua 변경 | Change 1 보완본의 성공 결과를 Before로 재사용하고 관련 변경을 모아 최종 After 1회. 그 사이 별도 Before E 반복 0회 |
| F — Lua | Lua 실행 코드 또는 생성 Lua 변경 | 정확한 문법 명령과 영향받은 harness를 최종 묶음에서 1회. E가 같은 경로에서 수행한 검사는 중복 제외 |
| G — 이동/보관 | 실제 테스트 이동 또는 archive 구현/자료 이동 채택 | 영향받은 실행·보호 범위 또는 대상 archive 복원 1회. no-op/defer이면 0회 |
| H — 문서/diff | 모든 변경 | 최종 diff·Origin 보존 확인 1회. 각 writer 종료 시 보호 확인은 기존 fixture에 포함 |

위 횟수는 성공한 실행의 기본값이며 실패를 숨기는 상한선이 아니다. 신규 전체 성능 기준선 측정, 별도 benchmark 회차, 전수 수동 원문 재검토는 이 리팩토링의 필수 조건이 아니다. 설명의 전수 기계 비교와 변경 동작의 기존 회귀 검사는 유지한다. §7의 명령은 선택할 node를 보여주는 실행 예시이며, 별도 제품 계약이 필수로 요구하는 node를 제외하지 않는 범위에서 중복 node를 줄이거나 한 호출로 묶을 수 있다.

#### 비교 수준

| 대상 | 유지해야 할 것 | 허용되는 차이 |
|---|---|---|
| 기존 authority·채택/봉인·기준 산출물 | 원래 raw bytes/hash와 소유권 | 없음 |
| 동일 producer·동일 입력의 재실행 | 결정적 출력 bytes와 hash | 없음 |
| 새 producer로 만든 구조 변경 후보 | 사실/근거/판정, 문장·순서·상태·qualifier·detail links | 실제 변경된 producer 경로/hash 및 이에 종속된 후보 identity만 명시적으로 허용 |
| validation | test membership·실패 기준·status/exit·출력 경계 | 실행 경로/새 attempt 등 계약상 가변 필드와 명시적으로 바뀐 구현 identity |
| Lua runtime | 공개 반환 계약·조회/실패 동작·표시 문자열·상태 전이 | 내부 module 경로와 책임 배치 |

소스 파일을 분리하면 `descriptions.json`의 `producer.files`가 달라지므로 **파일 전체가 옛 hash와 같아야 한다는 조건은 부정확하다.** 기존 파일은 그대로 보존하고, 새 후보의 의미/표현 부분을 전수 비교한 뒤 producer metadata의 정확한 차이를 따로 확인한다. 임의의 필드를 통째로 제외하지 않으며 새 helper/handler의 누락도 거부한다. 이에 종속되는 product ID는 새 후보로 검증하고 과거 acceptance를 승계하지 않는다.

#### 공통 실행 준비 — Origin을 writer로 사용하지 않음

아래는 **향후 실행 절차**다. 이번 계획 수정에서는 실행 환경 설치·후보 생산·pytest 본문을 실행하지 않는다. 경로 변수는 실행 시 확정한 절대 경로이며, 서로 겹치지 않는 짧은 Windows 경로를 선택한다.

| 변수/위치 | 역할 |
|---|---|
| `$Origin` | 사용자 기준 checkout. 코드·입력·기존 산출물을 읽고 전후 hash만 확인 |
| `$Before` | Change 1의 입력 전달 보완을 별도로 검증한 commit과 명시적 입력을 담은 구조 리팩토링 기준 subject |
| `$After` | 확정된 리팩토링 commit과 같은 의미 입력을 담은 disposable Git subject |
| `$Evidence` | Before/After subject 밖의 baseline snapshot·diff 출력. 이번 실행은 Origin 내부 `.tmp/e` 사용 |
| `$UvCache` | subject와 겹치지 않는 공용 절대 cache 경로. 이번 실행은 Origin 내부 `.tmp/uv-cache` 사용 |
| `$Subject` | 현재 실행할 Before 또는 After. 테스트의 ROOT/REPO와 설치본이 모두 이 경로에 대응 |
| `$SubjectLabel` | 현재 subject의 `before` 또는 `after`; 입력 ref/로그 파일 이름을 구분 |
| `$Subject/.tmp/semantic/rf/candidate` | 각 Recovery producer가 새로 만드는 후보. 두 subject에서 상대 경로를 같게 유지 |
| `$Subject/.tmp/rf-a`, `.tmp/rf-e` | 각 검사 전용 basetemp. 재사용하지 않는 빈 경로 |

1. `Before`/`After`는 정확한 commit과 명시적인 입력 inventory로 구성한다. working tree의 모든 untracked 파일을 자동 복사하지 않는다. raw-bound/LFS payload, 고정 readpoint, 필요한 B ZIP 및 역사 계약은 같은 logical path와 기대 hash로 제공한다. 누락되면 입력 BLOCKED로 기록한다.

   특히 B의 `current_support()`가 읽는 route index의 `final_root`는 현재 Origin의 절대 경로다. 복사한 handoff bytes의 동일성 외에 locator가 선택 Subject 내부를 가리키며 기존 reader/owner 계약을 충족하는지도 먼저 확인한다. 기존 subject 준비 절차가 허용하는 locator 구성·검증을 사용하고 그 차이를 입력 inventory에 기록한다. 적법한 subject-local locator를 확보하지 못하면 **B/E 입력 BLOCKED**로 남긴다. Origin의 authority index를 수정하거나 경계 검사를 끄고 다른 checkout을 읽는 방식으로 통과시키지 않는다.

2. Origin의 보호 파일 hash를 `$Evidence/origin-before.json`에 저장하고 종료 시 성공/실패와 무관하게 비교한다. 대상은 composition 두 파일, r6/adoption·필수 authority 입력, current pointer/data, accepted 상수를 가진 source 및 사전에 확정한 보호 목록이다. `git diff`만으로 untracked 또는 ignored 입력 보존을 대신하지 않는다.
3. A 실행 전에 아래 snapshot을 한 번 생성한다. `$Evidence`는 Before/After subject 밖이어야 하며 `origin-composition`은 존재하면 거부한다. 이번 사용자 execution boundary에 따라 Origin 밖에는 생성하지 않는다. 두 파일의 **복사 전 원본 집합→복사 후 원본 집합→복사본 집합** hash가 모두 같아야 한다. 원본이 변하거나 복사가 실패하면 부분 snapshot은 비교 기준으로 사용하지 않고 새 Evidence에서 다시 준비한다. 기록한 같은 파일의 시작 hash와도 대조한다.

```powershell
$CompositionRelative = 'Iris\build\description\composition'
$CompositionNames = @('blocks.json', 'descriptions.json')
$Snapshot = Join-Path $Evidence 'origin-composition'
if (Test-Path -LiteralPath $Snapshot) { throw 'Origin snapshot already exists' }
$CompositionBefore = @{}
foreach ($Name in $CompositionNames) {
    $SourcePath = Join-Path (Join-Path $Origin $CompositionRelative) $Name
    $CompositionBefore[$Name] = (Get-FileHash -LiteralPath $SourcePath -Algorithm SHA256 -ErrorAction Stop).Hash
}
New-Item -ItemType Directory -Path $Snapshot -ErrorAction Stop | Out-Null
foreach ($Name in $CompositionNames) {
    $SourcePath = Join-Path (Join-Path $Origin $CompositionRelative) $Name
    Copy-Item -LiteralPath $SourcePath -Destination (Join-Path $Snapshot $Name) -ErrorAction Stop
}
foreach ($Name in $CompositionNames) {
    $SourcePath = Join-Path (Join-Path $Origin $CompositionRelative) $Name
    $SourceAfter = (Get-FileHash -LiteralPath $SourcePath -Algorithm SHA256 -ErrorAction Stop).Hash
    $CopiedHash = (Get-FileHash -LiteralPath (Join-Path $Snapshot $Name) -Algorithm SHA256 -ErrorAction Stop).Hash
    if ($CompositionBefore[$Name] -ne $SourceAfter -or $SourceAfter -ne $CopiedHash) {
        throw "Origin snapshot bytes changed: $Name"
    }
}
```

4. A 전용 검사는 Before/After 안의 추적 `blocks.json`/`descriptions.json`을 다시 쓴다. 이 subject 내부의 writer 동작은 허용하지만 생성 diff는 코드 병합에서 제외한다. Origin의 기존 두 파일은 이전 producer의 결과로 유지한다. 신규 producer 결과를 그 producer의 current 결과로 채택/갱신하는 작업은 별도 owner 절차다.
5. 저장소 `uv.toml`의 `.tmp/uv-cache`는 subject마다 상대 경로여서 새 subject에 cache가 없을 수 있다. 기존 `UV_CACHE_DIR`의 존재 여부/값을 저장하고, 실행 세션 동안 `$env:UV_CACHE_DIR = $UvCache`로 공용 절대 경로를 지정한다. 두 subject의 lockfile과 Python 버전을 확인하며 cache만 공유하고 `.venv`는 각각 설치한다. online이면 lockfile에 필요한 다운로드 접근성을, offline이면 Python·의존 package·build dependency가 공용 cache에 모두 있는지 확인한다. offline 실행은 보존한 환경 아래 `UV_OFFLINE=1`을 사용한다. 필요한 cache가 없거나 잠긴 의존성을 가져올 수 없으면 **BLOCKED — 설치 입력/네트워크**로 기록한다. 잠금 해제·Origin venv 차용으로 대체하지 않는다. `UV_CACHE_DIR`/`UV_OFFLINE`도 `finally`에서 원래 상태로 복원한다.
6. 두 subject마다 다음 설치를 수행한다. `uv run`이 다시 editable 설치로 바꾸지 않도록 이후 모든 Python 호출에 `--no-sync`를 사용한다. 최종 비교에 사용할 source 묶음이 확정되면 해당 subject를 다시 설치하고 identity를 확인한다. 중간 편집마다 설치·전체 검증을 반복하지 않으며, 설치본 검사를 실행할 때에는 반드시 그 source와 일치해야 한다.

```powershell
Set-Location -LiteralPath $Subject
$env:UV_CACHE_DIR = $UvCache
uv sync --project .\Iris\tooling --locked --no-editable --reinstall-package iris-tooling
if ($LASTEXITCODE -ne 0) { throw 'Subject installation failed' }
```

7. 기존 `recovery.installed_identity(root)`에 Subject의 `Path`를 전달하고, 모든 실행 대상 `iris_tooling` module의 `__file__`이 해당 subject의 `Iris/tooling/.venv/Lib/site-packages` 아래이며 source 대응 파일과 raw hash가 같은지 확인한다. `recovery`의 기존 일부 파일 검사만으로 새 helper의 설치 상태를 추정하지 않는다. 외부 editable 경로와 다른 subject의 import를 거부한다. 사전 확인 외에 실행 중 실제 import된 module도 종료 시 대조한다.
8. 테스트 파일은 해당 subject의 절대 경로/동일 cwd에서 수집한다. collection 시 A의 ROOT/REPO와 B의 REPO, E의 ROOT/repository가 모두 Subject인지 확인한다. `-I -B`와 설치/source 확인 결과를 기록한다. test root만 격리하고 producer는 Origin에서 import하는 실행은 거부한다.
9. 위 설치/import 확인이 끝난 뒤, **A가 쓰기 전** 각 subject에서 다음 default Menu readpoint node를 실행한다. 실패하면 기존 input 불일치를 기록하고 기대 상수를 바꾸지 않는다. 이 노드는 C의 현재 `DESCRIPTION/BLOCKS` binding 검사다. K-1의 stale **B supply default**와 다른 경로이므로 한쪽 결과로 다른 쪽 성공을 추정하지 않는다.

```powershell
Set-Location -LiteralPath $Subject
uv run --project .\Iris\tooling --no-sync python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_current_menu_input_binding -q
if ($LASTEXITCODE -ne 0) { throw 'Default Menu input binding failed before A' }
```

**Change 1에서 작성할 최소 실행 보조물:** `$Evidence/check_refactor_subject.py`는 설치/source/ROOT 대응과 보호 파일 보존을 확인한다. `$Evidence/compare_refactor_outputs.py`는 아래 A/B의 명시된 필드 정책으로 전후 JSON을 비교한다. 기존 pytest fixture와 함께 쓰며, 정규 required registry에 추가하지 않는다. 두 파일은 아직 존재한다고 가정하지 않는다. 작성·검토 및 의도적 차이 fixture 확인 후에만 아래 명령을 사용할 수 있다. 새 formal seal/승인 상태를 만들지 않고 로그와 차이 목록만 남긴다.

`--noconftest`를 사용하는 A/B/E/F의 fixture는 선택된 테스트 모듈에 정의하거나 그 모듈에서 명시적으로 import한다. 자동 탐색되는 `conftest.py`에만 넣지 않는다. 이는 열거된 node의 집중 검사이며 canonical Round 3 분류 준수/PASS를 대신하지 않는다. B가 기록한 후보 path/hash/owner는 같은 프로세스에서 C가 읽는 명시적 공유 기록으로 전달하고, 기존 ZIP 경로 환경 hook만으로 hash 인계까지 완료됐다고 가정하지 않는다.

모든 native command 직후 실제 exit code를 확인하고, 실패 시 다음 producer/consumer로 진행하지 않는다. wrapper의 마지막 성공 명령이 앞선 실패를 가리지 않게 한다. pytest collection 성공은 본문 실행 성공으로 기록하지 않는다.

**A. 격리된 composition 생산과 전수 비교 — producer closure 변경**

아래 명령은 관련 producer 변경을 묶은 최종 비교에 사용한다. 재사용 가능한 Before 결과가 없을 때만 Before에서 한 번 실행하고 최종 After에서 한 번 실행한다. 두 테스트가 고정 출력 경로를 다시 쓴다는 점을 이용하되 그 경로는 disposable subject 내부다.

```powershell
Set-Location -LiteralPath $Subject
uv run --project .\Iris\tooling --no-sync python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\build\description\v2\tests\test_layer3_rule_generalization.py .\Iris\build\description\v2\tests\test_layer3_dvf_purpose_review.py --basetemp .\.tmp\rf-a -q
```

- Origin snapshot→Before 재생성 결과, Before→After 재생성 결과를 구분해 비교한다. 출력은 각 subject의 `Iris/build/description/composition/{blocks,descriptions}.json`이며 비교 과정은 읽기 전용이다.
- `blocks`는 item/target 집합, block/branch/relation ID·순서·내용, fact/provenance 참조, qualifier/application, unresolved·summary를 비교한다. `descriptions`는 전체 8,420 좌표의 state/reason, text, segment/use unit 순서·내용, target group, fact/block/branch/relation/qualifier refs, detail links, unresolved 및 summary를 비교한다.
- `producer.files`와 실제로 그 변경에 종속된 input path/hash만 별도 allowlist로 비교한다. source correction이나 판정 내용을 담는 subtree를 통째로 제외하지 않는다. 허용된 metadata 차이도 before/after 값과 실제 source hash를 검증한다.
- 같아야 할 payload에 차이가 있거나 새 helper가 producer 목록에서 빠지면 실패다. 이 비교는 문체/사실을 새로 승인하는 작업이 아니다.
- 비교를 마친 각 subject의 두 파일 hash를 `$Evidence/before-menu-inputs.json`과 `after-menu-inputs.json`에 `description`/`blocks`의 기존 `{path, sha256}` binding 형태로 저장한다. 파일은 E의 test-only 입력이며 새 authority manifest가 아니다. 해당 subject의 E 도중 이 두 파일은 쓰지 않는다.

```powershell
uv run --project "$After\Iris\tooling" --no-sync python -I -B "$Evidence\compare_refactor_outputs.py" --mode composition --baseline "$Evidence\origin-composition" --before "$Before\Iris\build\description\composition" --after "$After\Iris\build\description\composition" --output "$Evidence\composition-diff.json"
```

위 보조물은 구현 시 실제 metadata allowlist와 실패 예제를 먼저 확인한다. 테스트 PASS, baseline 재현, after 동등성 및 Origin hash 보존은 각각 별도 결과로 기록한다.

**B. Recovery 비-editable 설치 → before/after 후보 생산 → contract → 동등성**

재사용 가능한 Before 후보·계약 결과가 없을 때만 Before를 생산한다. 최종 After와 실제 실행할 subject에서 공통 준비를 완료하고 아래를 **해당 subject에서 순차 실행**하며 같은 상대 candidate 경로를 사용한다. 존재하는 candidate를 덮어쓰거나 r6를 환경 변수로 지정하지 않는다.

```powershell
Set-Location -LiteralPath $Subject
uv run --project .\Iris\tooling --no-sync python -I -B -m iris_tooling.domains.layer3.recovery --repository-root $Subject --output .tmp/semantic/rf/candidate
if ($LASTEXITCODE -ne 0) { throw 'Recovery candidate generation failed' }
$env:IRIS_LAYER3_RECOVERY_CANDIDATE = Join-Path $Subject '.tmp\semantic\rf\candidate'
uv run --project .\Iris\tooling --no-sync python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_recovery.py --basetemp .\.tmp\rf-b -q
if ($LASTEXITCODE -ne 0) { throw 'Recovery candidate contract failed' }
```

후보의 `manifest.json`, member path/hash, 생성 명령 stdout, 설치 identity를 같은 실행 기록에 연결한다. 후보 출력 위치를 잘못 지정한 실행은 실패로 처리한다. 실행 전에 기존 `IRIS_LAYER3_RECOVERY_CANDIDATE` 값을 저장하고 종료 후 복원한다.

| 후보 파일 | 전후 비교할 내용 | 제한적으로 허용할 차이 |
|---|---|---|
| `semantic.json` | fact ID/payload/순서, target 및 question key, state/판정/coverage/blocker, observations/provenance, bindings와 qualifier 범위 | 실제 producer ref의 명시적 path/hash 변화만; 사실·근거 내용 차이는 불허 |
| `acquisition.json` | facts·provenance·results·traces와 기존 `acquisition_content()` 결과 | `semantic_readpoint`, 검증된 dependency-only `binding_change`, self authority ref. 정규화 전 원 binding/hash를 먼저 확인 |
| `descriptions.json` | KO/EN text·표현/compact/expanded 순서·refs·fact_expressions·누락 사유·상태·적용 범위 | `inputs.semantic/acquisition`의 검증된 새 member hash/path. 임의 input subtree 제외 금지 |
| `audit.json` | recovered_facts, corrections, question_reassessment, inventory, applications, expression_projection, remaining_work, counts/completion | 실제 producer/test 경로 hash와 그에 따른 dependency binding만 개별 승인 목록으로 비교 |
| `manifest.json` | schema/status/completion, definition/successor, member 집합과 실제 파일 hash | 검증된 candidate member hash, 계획된 test/source binding 차이 |

candidate는 비교하려고 adoption하지 않는다. `partial`이 생성되거나 contract가 실패하면 원 결과를 보존하고 실패를 기록한다. 두 후보가 똑같이 실패했다는 이유로 변경 완료를 선언하지 않는다.

```powershell
uv run --project "$After\Iris\tooling" --no-sync python -I -B "$Evidence\compare_refactor_outputs.py" --mode recovery --before "$Before\.tmp\semantic\rf\candidate" --after "$After\.tmp\semantic\rf\candidate" --output "$Evidence\recovery-diff.json"
```

**자원/수명:** 조사한 r6 주요 JSON 4개는 합계 약 0.81 GB다. 신규 후보가 비슷한 크기라면 두 후보만 약 1.63 GB이며 subject 입력·설치·파싱 메모리·B/C package 공간은 추가로 든다. before 생산 후 실제 최대 크기/시간을 기록해 after 실행 여유를 확인한다. 서로 다른 후보 생산은 순차 실행하고, 메모리 부족을 피하도록 비교는 파일별로 처리한다. 후보·manifest·로그·diff를 후속 판단이 끝날 때까지 보존한 뒤 필요한 증거만 남기고 재생성 가능한 임시 subject/venv/후보는 기존 수명 정책에 따라 정리한다. 자원 부족은 BLOCKED이며 기존 r6 검사로 대체하지 않는다.

**C. runner — wrapper fixture와 실제 구현 검증 분리**

```powershell
Set-Location -LiteralPath $Subject
uv run --project .\Iris\tooling --no-sync python -B -m pytest .\Iris\validation\execution\tests -q
```

이 묶음의 fake launcher fixture는 인자 전달·환경 적용/복원·receipt·native 실패 우선순위를 검증한다. 그것만으로 분리한 실제 runner가 검증되었다고 기록하지 않는다.

실제 before/after `run_repository_tests.py`의 동일 입력 정책 census를 비교한다. 유효한 기존 Before census는 재사용하고 없는 경우에만 생산한다. 최종 full-gate가 같은 subject/정책의 census를 실제 제공하면 After census의 별도 실행은 생략한다. `$SubjectCommit`은 그 subject의 고정 commit이고 `$CensusOutput`은 Subject와 겹치지 않는 신규 외부 경로다.

```powershell
uv run --project .\Iris\tooling --no-sync python -B .\Iris\validation\execution\run_repository_tests.py source-census --repo $Subject --commit $SubjectCommit --output-root $CensusOutput --full-repository
```

- 전후 JSON에서 required test/source ID, classification·역할·제외 사유, dependency edge, 실행 대상 집합을 비교한다. 의도한 source 분리와 test ID 이동만 명시적인 대응표로 설명하고 나머지 차이는 실패로 처리한다. commit·구현 hash·실행 경로 같은 가변 필드도 기록한다.
- 분리한 실제 contract/workspace/실행/결과 수집 경로는 기존 `gate`/`full-gate` 중 해당 경로를 통과하는 실행으로 확인한다. 이번 Change 2는 `run_full_repository_gate` 내부도 분리하므로 최종에는 실제 `invoke_repository_tests.ps1`→실제 `full-gate` 실행이 필요하다. `--collect-only`와 fake body는 대체 증거가 아니다.
- **현재 선택은 BLOCKED 유지다.** `Iris/build/description/v2/tests/conftest.py::pytest_configure`는 선택 node와 무관하게 전체 inventory를 먼저 검사한다. §4의 미분류 5개와 `execution/contracts/repository_test_gate.json`의 `--round3-contract current` 연결을 사전 상태에 기록한다. canonical contract/분류 파일을 임시로 보정하거나 아래 full gate에 `--noconftest`를 적용하지 않는다. F의 focused collection 성공을 이 단계에 사용하지 않는다.
- 기존 classification owner 절차에서 누락이 해소되면 새 기준 commit/source와 관련 입력을 기록하고 before/after census·runner 비교 기준을 다시 맞춘다. 그 후 아래 명령은 해당 commit의 유효한 environment receipt와 외부 work/result root, orchestration receipt를 사용한다. 필요한 환경·evidence 부재도 별도 BLOCKED 원인이다. 실제 성공 전에는 runner 동작 보존 및 Change 2 완료를 주장하지 않는다. 다른 Change의 완료는 해당 검증 결과로 독립 판정한다. 전후 동일 실패도 성공으로 취급하지 않는다. 다른 Change마다 이 full gate를 반복 요구하지 않는다.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\validation\execution\invoke_repository_tests.ps1 -RepositoryRoot $Subject -Commit $SubjectCommit -ClaimId $ClaimId -EnvironmentReceipt $EnvironmentReceipt -WorkRoot $GateWorkRoot -ResultRoot $GateResultRoot -OrchestrationReceipt $OrchestrationReceipt
```

**D. CLI·context·serialization — Change 3/8**

```powershell
Set-Location -LiteralPath $Subject
uv run --project .\Iris\tooling --no-sync python -B -m pytest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_cli.py .\Iris\tooling\tests\test_repository_context.py .\Iris\tooling\tests\test_tooltip_t2_serialization.py -q
```

변경된 hash/escaping 계약과 실제 index producer의 비교를 추가한다. 이 명령만으로 모든 helper 호출자의 parity를 주장하지 않는다.

**E. 하나의 pytest 프로세스로 새 B 후보를 C/installer에 전달**

E는 A 비교와 입력 ref 파일 확정 뒤 수행한다. Change 1 보완본에서 이미 성공한 동일 Before E 결과는 재사용하고, 제품에 영향을 주는 관련 변경을 묶어 **최종 After에서 한 번 실행**한다. 해당 Before 성공 결과가 없거나 입력/구현 대응이 달라졌을 때만 Before E를 확보한다. 여기서 Before는 Change 1의 입력 전달 보완을 별도로 검증한 기준 commit이다. K-1이 있는 원본의 E 성공을 비교 기준으로 꾸미지 않는다. Lua-only 변경으로 새 A 생산이 필요하지 않다면 각 ref 파일에 보존된 canonical corpus의 확인된 binding을 기록한다. 현재 실행할 `$Subject`와 `$SubjectLabel` (`before`/`after`)을 맞춰 지정한다.

**Change 1에서 먼저 구현할 제품 코드 입력 전달 및 candidate fixture 경계:**

1. 기존 C 테스트의 `IRIS_MENU_TOOLTIP_CANDIDATE` 분기와 B의 `IRIS_SHARED_MENU_VALIDATION` hook을 사용한다. test-only `IRIS_REFACTOR_MENU_INPUTS`는 A에서 확인한 description/blocks 기대 binding 파일을 지정한다. 이 입력은 fixture 안에서 raw hash와 Subject 경계를 검사한 뒤 고정한다.
2. **B의 모든 supply 호출에 먼저 전달한다.** `tooltip_s2_supply.build(root, description_ref=None)`는 이미 명시적 ref를 지원한다. `test_s2_supply_and_owner_integration`의 두 직접 호출을 `supply.build(repository, description_ref=expected_description)`로 바꾼다. `tooltip_t1/s2_candidate.py`에는 `build(root, output, *, description_ref=None)`를 추가해 내부 `supply.build(root, description_ref=description_ref)`로 전달한다. 테스트의 첫 handoff와 결정성 비교용 두 번째 `s2_candidate.build` 모두 같은 `expected_description`을 받는다. 직접 호출만 바꾸고 중첩 경로를 남기지 않는다.
3. B의 default 처분은 **기존 거부 유지**다. `DESCRIPTION.sha256=8510f300…`과 현재 corpus `8e1eda45…`의 불일치를 기록하고, 인자 없는 경로가 `description bytes changed`로 거부되는 상태를 자동 보정하지 않는다. candidate fixture가 선언된 실행에서 기대 ref가 없으면 실패하며 default로 돌아가지 않는다. 기본 입력 갱신·current adoption은 별도 owner 작업이다.
4. 현재 C의 `read_menu_inputs()`와 `build_menu_product()`는 전역 `DESCRIPTION/BLOCKS`를 읽고 `product_install`은 두 값을 import해 복사한다. **기존 소스 상수 또는 `ACCEPTED_*`를 새 값으로 덮어쓰지 않는다.** 기존 함수에 내부용 명시적 expected input 인자를 전달할 수 있는 최소 경로를 추가한다. 인자를 생략한 default/current/CLI 경로는 기존 상수와 동일한 검사를 유지한다.
5. C는 `read_menu_inputs`→`build_menu_product(tooltip_ref=...)`에서 같은 description/blocks refs를 사용한다. installer는 `admit`→`runtime_overlay`→`stage`→`restore_candidate`의 내부 호출에도 같은 expected refs를 전달한다. manifest가 주장한 hash를 그대로 expected로 삼지 않고 A fixture가 사전에 고정한 값을 사용한다. `promote`/live 경로는 기존 current binding을 유지한다.
6. B handoff의 embedded supply `payload.binding.expression`, `s2_candidate.admit()`의 `AcceptedInput.binding.description`, T2 owner의 `t1_input.description`이 모두 A의 `expected_description`과 같아야 한다. `admit`의 receipt/member/source/working-subject 검사는 유지하고 fixture가 별도 기대 ref와의 동일성을 확인한다. B가 생산한 정확한 ZIP의 상대 path·raw SHA-256·owner product ID·이 description ref를 공유 기록에 남긴다. C node는 이 값을 읽고 ZIP bytes와 owner를 재확인한다. 기존 C 테스트가 `ACCEPTED_TOOLTIP/ACCEPTED_DESCRIPTION`을 monkeypatch하는 부분은 명시적 인자 소비로 바꾼다.
7. default current-input 검사와 candidate 검사를 구분한다. malformed/missing 후보 binding, 잘못된 description/blocks/B ZIP, 다른 subject, member/source drift를 거부하는 기존 검사와 거부 조건 fixture를 유지한다. canonical input 검사를 제거하거나 모든 후보를 수용하는 mode를 만들지 않는다.
8. 변경된 `s2_candidate`, Menu producer/installer 및 새 helper를 해당 subject에 non-editable로 재설치하고 실제 import/source hash와 producer inventory를 검사한다. 입력 전달 변경의 default 보존·명시적 입력·거부 조건 검증을 원본→보완본 경계에 기록하고, 그 이후 같은 fixture의 Before→After E로 구조 변경을 비교한다. fixture와 제품 코드 전달 경로가 완성되지 않으면 E를 실행 준비 완료로 표시하지 않는다.

실행 전에 `IRIS_MENU_TOOLTIP_CANDIDATE`와 `IRIS_MENU_RESUME_PACKAGE`가 이전 실행 값을 갖지 않도록 제거하고, 기존 환경 값은 종료 후 복원한다. 다음 **단일 호출**에서 B node가 먼저 실행되고 C node가 그 성공 후 실행되도록 node 순서를 고정한다. `-x`로 B 실패 시 C 진행을 막고 병렬 pytest/xdist를 사용하지 않는다.

```powershell
Set-Location -LiteralPath $Subject
$env:IRIS_SHARED_MENU_VALIDATION = '1'
$env:IRIS_REFACTOR_MENU_INPUTS = Join-Path $Evidence "$SubjectLabel-menu-inputs.json"
uv run --project .\Iris\tooling --no-sync python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\rf-e -x -q -s
if ($LASTEXITCODE -ne 0) { throw 'Shared B to C candidate validation failed' }
```

- B가 같은 Python 프로세스의 `os.environ['IRIS_MENU_TOOLTIP_CANDIDATE']`에 기록한 ZIP만 C가 사용한다. hook 값이 없으면 fixture가 실패해야 하며 기존 accepted ZIP으로 돌아가지 않는다. 별도 프로세스로 나누는 대안은 이번 계획에서 사용하지 않는다.
- A ref→B embedded supply→AcceptedInput→T2 owner→정확한 B ZIP→C manifest의 description/blocks/tooltip_input 및 tooltip_product_id→installer expected refs→stage/ZIP descriptor가 정확히 이어져야 한다. B package를 새로 골라 재사용하거나 A 후 corpus를 재생성하지 않는다. Before/After의 payload·표시 결과는 비교하되 각 subject의 실제 source와 그에 종속된 candidate identity 차이는 명시적으로 기록한다.
- `IRIS_SHARED_MENU_VALIDATION=1`일 때 B가 생략하는 syntax/runtime 검사는 동일 C stage의 `test_product_contract`가 실제로 수행해야 한다. C 실패 시 B 생략 검사를 PASS로 기록하지 않는다.
- Origin의 accepted B ZIP에 대한 retained media guard 비교도 유지한다. 새 B 후보가 guarded Lua 변경을 포함해 drift를 숨기지 못하도록 Change 7의 허용 목록 밖 raw hash를 따로 확인한다.
- Product contract의 두 product 결정성, source/member drift 거부, lock/interrupt/recover, package readback을 유지한다. `.tmp/menu`/`.tmp/tooltip` 전용 경계는 그대로이며 full gate의 외부 workspace 규칙과 혼합하지 않는다.

**F. Lua 실제 실행 경로 — 허용된 Change 7 및 Lua 생성 변경**

`lua`, `luac`, `powershell`의 실행 파일 경로/버전을 해당 검사 전에 확인한다. 없으면 해당 검사는 BLOCKED다. 아래는 subject의 default/legacy 경로를 위한 후보 목록이고, E의 product stage harness는 새 product 경로를 확인한다. **열거된 6개 파일 중 실제 변경을 보호하는 node만 `--noconftest -c`로 선택**한다. 여섯 파일 전부를 매번 실행할 의무는 없다. 이 실행은 canonical full gate나 classification 정책 검증으로 보고하지 않는다.

```powershell
Set-Location -LiteralPath $Subject
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
if ($LASTEXITCODE -ne 0) { throw 'Lua syntax validation failed' }
uv run --project .\Iris\tooling --no-sync python -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_iris_detail_view_model_acceptance.py .\Iris\build\description\v2\tests\test_iris_browser_single_pass_cache_contract.py .\Iris\build\description\v2\tests\test_layer3_lazy_lookup_contract.py .\Iris\build\description\v2\tests\test_iris_legacy_surface_acceptance.py .\Iris\build\description\v2\tests\test_iris_viewmodel_allocation_contract.py .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py -q
if ($LASTEXITCODE -ne 0) { throw 'Focused Lua harness validation failed' }
```

| Python 실행 대상 | 실제 Lua harness |
|---|---|
| `test_iris_detail_view_model_acceptance.py` | `detail_view_model_locale_harness.lua`, `detail_fact_reader_harness.lua` |
| `test_iris_browser_single_pass_cache_contract.py` | `browser_state_acceptance_harness.lua` |
| `test_iris_browser_state_selection_search_acceptance.py` | `browser_state_acceptance_harness.lua`, `run_harness()` 및 BrowserData 호환/logging source guard |
| `test_layer3_lazy_lookup_contract.py` | `lazy_lookup_acceptance_harness.lua`의 `layer3` mode |
| `test_iris_legacy_surface_acceptance.py` | `legacy_surface_adapter_harness.lua` |
| `test_iris_viewmodel_allocation_contract.py` | `runtime_optimization_metrics_harness.lua`의 `viewmodel` mode |
| E의 `test_product_contract` | 동일 stage의 detail `expanded`, tooltip `supply`, browser interaction density 및 ZIP 재조회 |

실제 변경에 해당하는 node만 선택하되 Change 7에는 E의 `test_product_contract`가 포함된다. 문자열 anchor가 추출 때문에 바뀌면 보호하던 동작을 동등한 검사로 옮기고 기존 검사를 조용히 삭제하지 않는다. Lua 문법/harness로 PZ IME 또는 accepted B의 새 수락을 주장하지 않는다.

Browser 상태·선택·검색 동작에 영향을 주면 current-required 파일의 두 test method를 포함한다. 이 method 경로는 Change 8에서 별도 조사할 standalone CLI의 PZ2 baseline 옵션 실행과 구분한다. 이전 확인의 12-node collection 성공만으로 이 본문·Lua 실행의 PASS를 주장하지 않는다.

**G. 실제 보관/테스트 이동을 채택한 경우에만 실행**

```powershell
Set-Location -LiteralPath $Subject
uv run --project .\Iris\tooling --no-sync python -B -m pytest .\Iris\validation\artifacts\tests\test_content_addressed_archive.py -q
```

실제 이동 항목에 대해서 기존 inventory·test ID migration·replacement coverage·current runner를 사용한다. Change 11의 r1–r5 no-op을 이유로 새 archive 생산/복원 전체 검사를 실행하지 않는다.

**H. 문서·보존·diff 확인**

계획의 12개 절, 기존 경로·검증 node와 옵션, 새로 구현해야 할 보조물의 구분을 확인한다. 모든 후보 실행 뒤 Origin 보호 hash와 status를 비교하고, 병합 diff에 후보 생성물이나 accepted 상수 변경이 없는지 확인한다. 현재 문서 수정에서는 구조/경로/공백·PowerShell 명령 문법과 §4의 제한된 읽기 전용 실패 재현을 확인한다. Java/JS 변경이 향후 별도 범위로 생기면 `.\gradlew test` / `pnpm biome check .`를 적용하며 이 계획의 Python 도구는 `uv run ... python <script>`로 실행한다.

### Manual Validation

- 전수 기계 비교에서 문장·의미 연결 차이가 0이면 별도 전수/대표 원문 수동 검토를 완료 조건으로 추가하지 않는다. 차이가 있거나 비교 도구가 다루지 못한 출력이 있을 때만 해당 내용을 직접 확인한다. 의미 교정은 별도 작업으로 분리한다.
- 실제 UI 동작 경로를 변경하면 최종 Lua 변경을 묶어 같은 게임 버전·언어·해상도/배율에서 한 번 회귀 관찰한다. 각 추출 단계마다 PZ를 반복하지 않는다. 변경 경로에 해당하는 항목만 선택한다. Browser 스크롤 끝/중간, 화면 크기 변경, 아이템 전환, 검색 중 재렌더, 창 닫기·재열기, KO IME 조합과 focus를 포함한다.
- 허용된 Detail 변경이 기존 recipe/rightclick과 Freeform Cooking의 펼침/검색 상태를 깨뜨리지 않는지 확인한다. 보류한 state/Renderer 구현을 검증 완료로 보고하지 않는다.
- unchanged B의 Alt Tooltip 표시는 Menu 통합에 실제 영향이 있거나 자동 검사가 확인하지 못한 연결이 있을 때만 관찰한다. 변경하지 않은 Tooltip 전수 수동 QA는 추가하지 않는다. 기존 B owner 수락을 새 B 후보에 자동 승계하지 않는다.
- 실제 PZ를 확보하지 못하면 해당 UI 변경은 `implemented_only`, PZ 확인은 `unvalidated_but_in_scope`로 남긴다.

### Validation Limits

- exact relevant command가 exit `0`일 때만 해당 검사를 PASS로 기록한다. 필수 도구/입력/환경 부재는 BLOCKED이며 skip이나 미실행을 PASS로 바꾸지 않는다.
- 기존 테스트가 현재 출력을 보존하는지 검증하는 것이며 현재 설명의 모든 의미·품질을 새로 승인하는 작업이 아니다.
- 외부 모드 전수 호환성, B42 대응, 멀티플레이·장시간 세션, 공개 배포는 검증 범위 밖이다.
- 소스 검색만으로 동적 참조 부재를 증명하지 않는다. 확인이 부족한 archive/이동은 보류한다.
- full repository gate·재봉인·과거 전체 재생성을 모든 변경에 일괄 요구하지 않는다. 기존 계약과 실제 영향 범위에 따라 필요한 검증만 수행한다.
- A/B/E의 설치·후보 fixture 및 비교 보조물이 아직 구현되지 않았거나 실제 비교가 끝나지 않았다면 실행 준비/동등성 검증을 완료로 기록하지 않는다. 이 계획 수정은 required test 본문의 실행 가능성 검증을 대신하지 않는다.
- 현재 확인된 B default의 stale binding 거부와 canonical full-gate의 classification 차단을 기존 실패로 남긴다. 명시적 후보 경로의 향후 성공이나 focused collection exit `0`으로 이 상태를 덮지 않는다. classification owner 해소 및 실제 runner 종단 검증 전에는 Change 2는 미완료다. 이 차단을 독립 변경의 착수·검증·개별 완료 조건으로 전파하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

recovery의 fact/evidence/question 판정과 producer 입력 목록을 건드린다. 기존 의미 소유권은 유지하고 변경 전후 판정 차이 0을 요구한다. required 목록/locator 이동은 기존 갱신 경로에서 수행한다.

### Runtime Behavior Surface

허용된 Browser Detail lifecycle, product/legacy lookup, Wiki 조립을 건드린다. 상태 저장소·guarded Renderer/Presentation/Tooltip 파일 수정은 보류한다. 새 Lua 모듈도 require 순서·전역 노출·cache lifetime을 바꿀 수 있으므로 동작 검증과 B retained bytes 확인이 필요하다.

### Compatibility Surface

Lua 공개 API·전체 데이터 facade, Python import/CLI, unittest test ID, dynamic build path, Windows 환경 처리를 건드릴 수 있다. 기존 adapter와 진단 schema를 보존한다.

### Sealed Artifact Surface

`.gitattributes`의 raw-bound 범위, r6 LFS payload, producer/hash 목록과 artifact manifest, accepted B ZIP이 관련된다. Origin 기준 bytes와 accepted 상수를 유지하고 신규 후보 identity는 별도 기대값으로 검증한다. candidate 인자 전달이 default current/live guard를 바꾸지 않게 한다.

### Public-Facing Output Surface

설명과 Wiki 문자열, 순서, 조건·부재 표시가 관련된다. 구조 변경의 목표는 표시 결과 보존이며 제품 의미를 수정하는 핑계로 사용하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- 공통 helper가 domain owner를 import하면 새 순환 의존이 생긴다. 공통 기반은 순수 기능만 갖고 domain/build는 얇은 진입점으로 연결한다.
- 기능군을 하나의 배타적 category로 만들면 독립 용도가 사라질 수 있다. 복수 handler 적용과 기존 선택/소비 규칙을 유지한다.
- 기존 authority 책임까지 분리 모듈에 옮기지 않는다. 정보 근거와 표현 책임은 별개다.

### Runtime Risk

- entry 재생성 또는 child 순회 변경으로 IME focus·스크롤 위치가 깨질 수 있다. 실제 PZ 관찰을 해당 단계 완료 조건에 둔다.
- lookup 분리로 eager load나 숨은 fallback이 생길 수 있다. 선택된 generation/product만 가시적이어야 한다.
- atomic helper 변경이 복구용 임시 파일 이름·fsync·replace 순서를 깨뜨릴 수 있다. 실패 주입과 원 bytes 복원을 검사한다.
- guarded Lua 파일을 바꾸면 `unclassified B runtime drift`가 발생할 수 있다. 이번 범위에서는 해당 파일을 보류하며, 새 B 후보 생산으로 guard를 우회하지 않는다.
- 새 Lua 모듈이 source에서는 동작해도 v1 producer 또는 package support 목록에서 빠지면 배포 후보의 `require`가 깨지거나 미결속 코드가 실행될 수 있다. 관련 목록의 path/hash와 staged/ZIP 실제 조회를 함께 검사한다.

### Compatibility Risk

- CLI/함수명이 유지되어도 import/monkeypatch/dynamic loader 위치가 바뀌면 소비자가 깨질 수 있다. 호출 관계와 테스트의 patch 대상을 함께 확인한다.
- 보관소 이동은 source closure·manifest·test ID를 끊을 수 있다. 현재 참조가 남은 파일은 유지한다.
- 진단 필드와 평면 Lua API는 외부 소비자가 확인되지 않았다는 이유로 제거하지 않는다.

### Regression Risk

- `used`·material grouping·정렬 변경은 전체 설명에 파급된다. 대표 사례 외에 전수 좌표 비교를 수행한다.
- 코드 분리는 producer hash를 바꾼다. 기존 산출물 raw 보존과 새 후보의 논리 결과 동일성을 분리해 판정한다.
- 테스트 이동으로 discovery만 줄어들어도 녹색 결과가 나올 수 있다. 수집 test ID·required 집합과 보호 조건을 비교한다.
- test ROOT와 실제 import subject가 다르거나 editable 설치가 다시 들어오면 옛 producer를 검사할 수 있다. `--no-sync`·module/source hash·test root를 확인한다.
- B/C를 별도 프로세스로 실행하거나 stale 환경을 남기면 다른 후보를 검사할 수 있다. 단일 프로세스·명시적 입력 refs·사전 환경 제거/종료 후 복원을 적용한다.
- 직접 supply만 보완하고 `s2_candidate.build`의 중첩 호출을 남기면 K-1이 다시 발생한다. 네 supply 생산 경로의 같은 ref 사용과 AcceptedInput→owner→C 연결을 확인한다. 이 입력 전달 변경을 Change 1의 별도 제품 코드 diff로 검증해 구조 변경의 비교 기준에 숨기지 않는다.
- 집중 pytest가 성공해도 canonical collection이 분류 누락으로 막힐 수 있다. focused 검사와 full gate의 상태·명령·원인을 분리하고 동일 실패를 전체 동등성 성공으로 처리하지 않는다.
- subject별 상대 cache를 사용하면 설치가 네트워크 상태에 좌우될 수 있다. 공용 절대 cache와 잠긴 의존성 공급 전제를 기록하며 설치 실패를 오래된 환경으로 우회하지 않는다.
- Recovery 두 후보의 메모리/디스크 비용으로 비교가 끝나지 않을 수 있다. 실제 용량을 확인하고 완료 전 동등성 claim을 하지 않는다.

---

## 10. Rollback Plan

1. Change 단위로 분리해 반영하고 Origin 보호 hash 및 before/after 코드·산출물 identity와 필요한 비교 결과를 보존한다. 사용자의 기존 미커밋 수정은 별개로 유지한다.
2. 비교 실패 시 해당 분리 변경만 되돌린다. old facade/adapter와 기준 산출물이 남아 있어 이전 구현으로 복귀할 수 있어야 한다.
3. 새 producer의 실패 후보는 current로 설치하지 않는다. A/B/E writer는 disposable subject에만 허용한다. Origin의 기준 `blocks.json`, `descriptions.json`, r6와 pointer는 그대로 유지하며 코드 병합에 subject의 생성물 diff를 포함하지 않는다. 보존 hash가 달라지면 즉시 실패로 기록하고 원 bytes 및 변경 주체를 확인한다. 성공한 실행 뒤 조용히 되돌려 보존했다고 주장하지 않는다.
4. 설치 fixture 중단은 해당 owner의 journal/lock recovery로 복구한다. lock 파일만 삭제해 성공 상태로 만들지 않는다.
5. archive 이동은 검증된 archive에서 원래 논리 경로와 raw bytes로 복원한다. 복원 검사가 끝나기 전 원본 제거를 수행하지 않는다.
6. 전체 workspace를 대상으로 `reset --hard`·`clean`·재귀 삭제하지 않는다. Windows 파일 이동/정리는 절대 경로와 작업 대상 경계를 확인한 뒤 해당 변경 범위에만 수행한다.
7. B/C/Recovery 환경 변수, `UV_CACHE_DIR`/`UV_OFFLINE`의 원래 존재 여부·값과 cwd를 `finally`에서 복원한다. 임시 candidate/venv는 후속 비교에 필요한 증거를 보존한 뒤 수명을 종료한다. Origin의 `.venv` 또는 기존 accepted ZIP, 재사용하는 공용 uv cache를 subject 정리 대상으로 삼지 않는다.

---

## 11. Governance Constraints

- `Philosophy.md`를 최상위 기준으로 유지한다. PZ에서 Iris는 100% Lua이며 Python은 오프라인 도구다.
- Hub & Spoke와 SPI 경계를 보존한다. Pulse가 Iris에 의존하거나 Iris가 다른 spoke를 직접 의존하게 하지 않는다.
- 사실에 근거한 중립적 설명, 근거 부족 시 침묵, 메뉴/Alt Tooltip 두 표면, 최대 네 줄을 유지한다.
- recipe와 rightclick은 독립적이고 동등한 쓰임 관점이다. 정리 과정에서 어느 하나를 종속시키지 않는다.
- 아이템·행동·게임 상태를 변경하는 기능을 추가하지 않는다.
- 과거 authority/승인/실패 기록과 원 bytes를 보존한다. 새 구현을 과거 결과로 검증했다고 기록하지 않는다.
- 현재 실행과 historical replay를 분리하고, 기존 소비 경로에 archive·legacy·다른 locale의 숨은 대체를 추가하지 않는다.
- 새 정책·검증 lifecycle 없이 기존 계약·reader·테스트를 재사용한다. 결속된 문서 변경도 단순 산문 변경으로 가정하지 않는다.
- canonical full gate의 미분류 source를 임시 taxonomy/closure 수정으로 통과시키지 않는다. 기존 owner 절차로 해소하고 새 subject의 실제 검증을 수행한다. 집중 검사의 `--noconftest`는 분류 정책을 충족했다는 증거가 아니다.
- 종합안의 미결정 사항은 이 계획의 채택/조건부/제외 판단으로 드러낸다. 정보가 부족한 항목을 이미 제거 가능한 것으로 기록하지 않는다.

---

## 12. Expected Closeout State

### 계획 수정의 완료 상태 — 구현 착수 전 기록

**complete — 사용자 요청을 반영한 계획 수정 범위.** 리팩토링 범위와 기존 검토 기록을 유지하고 최소 검증 실행 정책·변경별 차단 격리를 반영했다. 아래 collection/실패 관찰은 이전 개정의 기록이다. K-1의 default supply 거부와 K-2의 기존 F collection exit `3`을 확인했고, 수정한 F 목록은 collection exit `0`/12 nodes까지 확인했다. 리팩토링 구현 상태는 `planned`이며 이번 문서 수정으로 구현 검증 PASS를 주장하지 않으며 추가 계획 검토를 필수 Gate로 만들지 않는다. 설치·후보·pytest 본문·full gate·실제 PZ를 실행했다고 주장하지 않는다.

### 향후 구현의 목표 상태

각 채택 변경의 목표는 **complete**이며 아래에서 그 변경에 적용되는 조건만 충족한다. 검사 실행과 재사용은 §7 최소 검증 정책을 따른다. 조건부 no-op/defer와 독립 변경의 blocked를 구분하며, 한 항목의 차단으로 완료된 다른 항목을 다시 열지 않는다.

- 설명/recovery/runner의 책임 분리가 구현되고 기존 진입점·의미 소유권이 유지된다.
- 사실·판정·표현·근거 연결의 전후 차이가 0이며 실제 producer identity 차이는 정확히 기록된다.
- A의 Origin byte snapshot·전후 hash 보존, before 재현 및 after 전수 비교가 충족된다. Recovery는 정확한 non-editable before/after producer의 후보 contract와 payload 비교를 충족한다. 동일 Before의 기존 생산·검증 결과는 재사용하며 각 Change마다 두 후보를 새로 생산하지 않는다.
- Change 1의 B/Menu 입력 전달 코드는 원본→보완본 경계에서 별도 검증되며, 이 기준 commit 이후 구조 리팩토링의 before/after 검증과 구분된다. K-1 때문에 불가능한 원본 E의 성공 동등성을 주장하지 않는다.
- E의 직접/중첩 supply, AcceptedInput, B ZIP path/hash/owner/corpus와 C producer·installer·stage/ZIP binding이 각 subject의 A ref로 이어지고, accepted 상수/default guard는 유지된다. candidate PASS를 current/default readpoint PASS로 보고하지 않는다. 기존 B default 실패의 owner 판단은 별도로 남긴다.
- 변경된 실행 경로의 필수 검증이 exit `0`이고, 테스트 이동 시 보호 범위가 유지된다.
- Change 2는 fake launcher fixture 외에 실제 source-census 비교와 변경한 실제 runner 종단 검증을 완료한다. 현재는 **BLOCKED — 기존 Round 3 source classification 누락**이며, owner 해소 후 유효한 최종 subject에서 실제 full gate가 성공해야 Change 2를 complete로 닫을 수 있다. 이와 독립인 Change의 완료는 유지한다. 환경·evidence 부재는 별도 차단 사유로 기록한다.
- 채택한 Menu Lua 변경은 신규 모듈의 v1/v2 producer·package support 결속, retained B guard·product contract와 실제 PZ 회귀 관찰까지 완료된다. 미관찰이면 `implemented_only`로 남긴다. guarded state/Renderer/Tooltip 하위 변경은 이번 구현 목표에서 제외된 보류 항목이다.
- 기존 authority·기준 산출물·현재 포인터와 사용자 작업이 보존된다.
- Change 6/11 등 조건부 항목은 실제 실익에 따라 adopt/defer/no-op과 근거를 기록한다. no-op 판정 완료를 코드 추출/보관 수행으로 표시하지 않는다. 필수 채택 변경이 남아 있으면 부분 완료이며, 원 제안 중 명시적으로 보류한 항목을 숨겨 전체 제안 구현 완료를 주장하지 않는다.

최종 보고에는 Change별 상태, 실제 변경 파일, 실행한 명령과 exit code, 출력 parity, PZ 관찰 범위, 보류 사유를 남긴다. 필수 변경이 미완료면 전체 리팩토링은 `partial`이며, 기존 classification 또는 필수 입력·환경 때문에 더 진행할 수 없는 해당 검증은 `blocked`다. 계획 작성의 complete를 구현·품질 승인·current 전환·배포 완료로 확대하지 않는다.

### 2026-09-15 구현 실행

**전체 상태: partial.** 아래는 실제 구현·실행 기록이며 위 계획 작성 완료와 구분한다. 사용자 프롬프트의 owner approval을 적용했다. 새 validation authority나 seal을 만들지 않았고 current/adoption/release는 전환하지 않았다.

#### 작업 경계와 입력

- Origin은 `C:/Users/MW/Downloads/coding/PZ`다. 외부 디렉터리의 목적은 원본 쓰기 방지와 subject 혼용 방지이므로, 이번 execution boundary에서는 같은 저장소 안의 `.tmp/s/b`와 `.tmp/s/a`를 독립 Git subject로 사용했다. 비교 출력은 두 subject 밖인 `.tmp/e`, 공용 cache는 `.tmp/uv-cache`다. 검사별 checkout을 추가하지 않았다.
- 원본 commit은 `aeabeda257209fd2bb7eb9172a4c9960ff7d1f9f`, Change 1 보완 Before는 `92cd64f7819da4e9d34f7628592f7197f091daba`다. A/B/E 구조 변경 후보는 `cd1fd7f9c18ef6b664a5f0df8ea16c199a9960c7`이다. 이후 같은 After subject에서 naturalization 및 PZ 인자 처리 변경을 `8f882b7167f814328005ca244b0677f4f9f26b26`으로 검사했다. 이 마지막 변경은 A/B/E가 결속한 producer/input을 바꾸지 않아 해당 결과를 재사용했다. Origin에는 commit/stage를 하지 않았다.
- 각 subject에 잠긴 의존성으로 `uv sync --project <subject>/Iris/tooling --locked --no-editable --reinstall-package iris-tooling`을 실행했다. r6 실제 JSON, accepted B ZIP, 기존 handoff를 같은 logical path에 제공했다. subject route index의 `tooltip_t1_production_handoff.final_root`만 해당 subject 안의 handoff로 설정했다. Origin index는 보존했다.
- Recovery가 요구하지만 HEAD에서 삭제된 human input 5개는 저장소 Git 이력에서 manifest의 기대 SHA-256과 일치하는 bytes를 찾아 subject에만 제공했다: `iris_dvf_layer3_multi_meaning_information_resolution_successor_contract.md`, `iris_dvf_layer3_multi_profile_investigation_completion_first_contact_contract.md`, `iris_dvf_layer3_semantic_investigation_question_results_contract.md`, `iris_layer3_acquisition_contract.md`, `iris_layer3_expression_contract.md`(모두 `docs/`). 이를 current 문서 복원이나 새 authority 채택으로 처리하지 않았다.
- `lua/client/ISUI/ISLiteratureUI.lua`는 checkout의 개행 변환이 provenance에 영향을 줘 Origin의 정확한 bytes를 두 subject에 제공했다. 이 입력을 바로잡기 전 Before A 비교 실패와 이후 재실행을 구분한다.
- `.tmp/code`의 실행·비교 스크립트는 이번 작업의 일회성 보조물이다. 정규 validator나 후속 승인 기준으로 채택하지 않는다. 실행 환경 변수는 종료 시 복원한다.

#### Change별 처분

| Change | 상태와 실제 내용 |
|---|---|
| 1 | complete — B 직접/중첩 supply에 description ref 전달. Menu producer 및 admit/runtime_overlay/stage/restore에 명시적 description/blocks ref 전달. 같은 프로세스의 B ZIP·owner·corpus binding을 C에서 확인. accepted 상수와 current/live 기본 거부 유지 |
| 2 | implemented / blocked — runner를 `repository_contracts`, `repository_sources`, `checkout_workspace`, `process_results`로 분리하고 기존 진입점·patch 위치 유지. execution 48개 통과. 실제 census의 기존 classification 차단 때문에 canonical full-gate 완료는 아님 |
| 3 | complete — `common/serialization.py`의 compact/pretty JSON 및 raw SHA-256, `common/repository_context.py`로 동일 계약만 공유. build context는 같은 상태를 재수출. Recipe의 CR/LF escaping과 fixing/moveables의 quote/backslash escaping은 서로 달라 유지. `build/tools/common/io.py`의 기본 key order·출력 옵션과 외부 workspace guard도 별도 기존 계약 유지 |
| 4 | complete — crafting/cooking/media/medical/supplies frame handler와 명시적 assembly state 분리. lexicon은 source producer 대신 vocabulary/phrase view를 소비. description 전수 내용 차이 0 |
| 5 | complete — vocabulary, phrase views, source index, crafting roles, claims, direct/activity question review를 분리. producer 입력 목록 갱신. Before/After 기존 후보 계약과 전수 payload 비교 완료 |
| 6 | no-op — 짧은 atomic write 구현의 부모 디렉터리 처리·오류 메시지·journal/lock owner가 달라 공통화 실익 없음. 기존 실패/복구 책임 유지 |
| 7 | implemented_only — product/legacy lookup factory, Detail child/scroll lifecycle helper, Wiki 공통 identity field 조립 분리. 신규 Lua 3개 producer/package 결속. guarded B 파일 7개 보존. 실제 PZ는 unvalidated_but_in_scope |
| 8 | implemented — 고정 lazy CLI registry, common context, 명시적 PZ executable/options 인자. naturalization composition 구현을 `domains/public_text/composition`으로 이전하고 build adapter 및 compiler/generation producer 목록 유지. 자동 검증의 잔여 상태는 아래 기록 참조 |
| 9 | defer — unittest ID와 기존 test 경로 유지. required runner의 같은 보호 범위 실행을 확인하기 전에 구 경로를 제거하지 않는 조건을 적용. classification이 막힌 상태에서 relocation/교체 coverage를 완료로 선언하지 않음 |
| 10 | defer — 큰 registry closure 파일은 current frozen-fixture materialization·preimport 검사와 과거 preflight/nonce/failure-record 실행을 함께 포함한다. `repository_test_gate.json`, dependency inventory, run/validate entry 및 기존 current-route fixture 소비가 남아 있어 파일 전체 보관은 불가. membership을 존속 승인으로 삼지 않았으며, 함수별 current obligation 해소와 canonical 실행이 남아 있음 |
| 11 | no-op — r1–r5는 untracked. 새 archive 생성이나 로컬 사본 삭제 없음. r6 bytes 보존 |
| 12 | complete — 구현 경계·기존 adapter·미검증 범위와 아래 결과를 문서에 반영. 의미·schema·CLI token·historical manifest 경로를 개명하지 않음 |

PZ2의 `t3d1`/`t2-final` 경로는 Browser 테스트의 standalone historical baseline 보존 옵션에 속한다. current-required 두 method 실행에 필요한 입력으로 확대하거나 임의의 새 identity로 치환하지 않았다. 실제 PZ executable/options는 제공받지 않았으므로 검색·추측 실행하지 않았다.

#### 실제 검증 결과

명령의 공통 prefix는 `uv run --project <subject>/Iris/tooling --no-sync python`이다. A/B/E는 `-I -B -m pytest --noconftest -c <subject>/Iris/tooling/pyproject.toml`, D/F는 같은 pytest 설정에서 `-B`를 사용했다. 모든 basetemp는 subject의 `.tmp` 아래이며, B/C 공유 ref 및 candidate 환경 값은 실행 전 지정하고 종료 후 복원했다. 아래에 기록한 실패를 PASS로 합산하지 않는다.

| 검사 | 실행 대상·결과 |
|---|---|
| Change 1 원본→보완본 | default B supply는 두 설치본에서 동일한 `description bytes changed` 거부. explicit projection hash `2997509a96702e03021df1fdf75fc44f080cce7ba5a6d2729ceed247d4babea1` 동일. malformed/partial/wrong Menu refs는 기존 current-input node로 확인 |
| A | `test_layer3_composition::test_layer3_composition_contract`, `test_layer3_description_composition::test_layer3_description_composition`, `test_layer3_rule_generalization.py`, `test_layer3_dvf_purpose_review.py`: Before 19 passed/exit 0(41.68s), After 19 passed/exit 0(45.49s). Recovery 인자 수정 후 영향받는 description node만 1 passed/exit 0(11.01s) 재실행 |
| A 비교 | Before 두 JSON은 Origin snapshot과 raw-equal. After 전수 payload는 동일. 실제 source hash로 확인한 `semantic_correction.producer_sha256`, description의 input hash/producer files만 달라짐 |
| B 생산 | 양쪽 `python -I -B -m iris_tooling.domains.layer3.recovery --repository-root <subject> --output .tmp/semantic/rf/candidate` exit 0, completion complete, source-confirmed facts 24,342. 최초 After의 누락 `payload` 인자로 인한 NameError는 인자 전달을 수정한 뒤 재실행 |
| B 계약 | `test_layer3_recovery.py`, 정확한 `IRIS_LAYER3_RECOVERY_CANDIDATE` 사용. Before 1 passed/exit 0(1509.54s), After 1 passed/exit 0(1807.50s). 실행 중 CPU·메모리를 주기적으로 확인했다. After의 600초 faulthandler 출력은 반복 음성 조건 검증의 현재 stack 진단이며 실행 제한/실패가 아님 |
| B 비교 | semantic/acquisition/descriptions raw-equal. audit은 변경 producer 5개·신규 8개의 확인된 입력 path/hash를 제외하고 전수 동일. manifest 차이는 해당 audit SHA-256뿐. `.tmp/e/recovery-diff.json` |
| C | `python -B -m pytest Iris/validation/execution/tests -q`: 48 passed/exit 0(139.09s). 실제 `run_repository_tests.py source-census --repo <subject> --commit <commit> --output-root <Origin>/.tmp/e/cb 또는 ca --full-repository`는 Before/After 모두 exit 2: `docs/review/prose/before/test_layer3_description_composition.py` 미분류. full gate 미실행/blocked |
| D | `test_cli.py test_repository_context.py test_tooltip_t2_serialization.py`: 12 passed, 1 failed/exit 1. 기존 current route가 없는 `docs/iris_tooltip_t1_display_contract_policy.md`를 가리킴. `test_compose_layer3_text_v2.py`, `test_compose_layer3_text_overlay.py`, `test_compose_entrypoint_guard_hardening.py`, `test_naturalization_compiler_identity.py`: Before/최종 After 각각 32 passed, 15 subtests passed/exit 0(1.07s/0.97s). 테스트의 기존 external output locator는 subject 밖이면서 Origin 안인 `.tmp/e/d`를 사용 |
| D byte/path 비교 | 최종 설치본으로 compact/pretty/raw-hash, path escape 거부, 세 index producer의 Lua quoting·실제 render 출력 전후 동일(exit 0). 공백·한글 경로의 명시적 context, 내부 output root 거부, installed CLI help도 Before/After exit 0. 인자 없는 PZ executable은 `powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File Iris/test/run_pz_core_refactor_harness.ps1 -OutputPath .tmp/pz/result.json -HarnessModule unused`에서 예상대로 즉시 exit 1; 게임 실행 없음 |
| E | `test_s2_supply_and_owner_integration` 다음 `test_product_contract`를 단일 프로세스로 실행. Before 2 passed/exit 0(103.77s), 최종 After 2 passed/exit 0(114.38s). source/member drift, lock/interrupt/recovery, stage/ZIP 실제 조회 포함. 이전 After snapshot의 성공을 최종 후보 대신 사용하지 않음 |
| F | 계획의 6개 Lua 연계 파일에서 11 passed/1 failed 후, 빠졌던 `IRIS_REPOSITORY_ROOT`를 해당 subject로 지정해 실패한 Browser source guard만 재실행: 1 passed/exit 0. 12개 모두 확인. E syntax 396 files/exit 0, expanded 4,210 states와 B runtime/ZIP harness exit 0 |
| 신규 Lua 결속 | 최종 E의 동일 product/ZIP을 재사용해 신규 3개 source의 manifest hash·ZIP bytes 일치 및 기존 stage의 누락/변조 거부를 확인(exit 0). 별도 gate tree나 validator를 만들지 않음 |
| H | Origin blocks/descriptions는 시작 snapshot hash와 동일. r6 6개 root file은 Before 입력과 동일. accepted B ZIP 및 guarded Lua 7개 bytes 보존. pointer/authority 변경 없음 |

최종 E product는 `l3p-93b16406f1af32f8a2a94ef289a8121a02aa90ab8724922f372c089a4379db43`, ZIP은 After subject의 `.tmp/menu/run-a9o6zu_p/p/Iris.zip`, SHA-256 `075f63f4ebe70f9ab17145ab8a2cba1981cf943ddcb50d425924d87c009dc39a`다. Before/After `menu.lua`/`tooltip.lua`의 전체 표시 fixture도 정확한 C product ID 외 동일하다. 이 후보는 실제 PZ 수락 또는 current 채택을 의미하지 않는다.

`git diff --check`는 exit 2다. Raw-bound product test의 CRLF 변경 행, Wiki의 공백 행, Recovery source 끝의 빈 줄을 보고했다. 이를 PASS로 기록하지 않는다. 전수 payload와 source binding을 확인한 뒤 형식만 일괄 바꾸어 producer identity를 다시 만드는 작업은 수행하지 않았다.

### 2026-09-16 비 PZ 잔여 해소

사용자는 실제 PZ 관찰을 직접 맡고 나머지를 해소하도록 지시했다. 이후 raw-byte 동일성과 해시값 동일성 검증은 과검증이므로 하지 말라고 명시했다. 이 지시는 이 작업의 전후 동일성·봉인 완료 조건보다 우선한다. 관련 재생산·재실행·추가 증명은 중단한다. 기존 제품의 입력 거부 로직을 제거하거나 새로운 validation authority를 만들지는 않는다. 이 절이 앞선 partial 기록의 현재 처분을 갱신한다.

#### 구현 및 처분

- 설명 frame, Recovery, runner, 공통 serialization/context, naturalization adapter, Menu Lua의 책임 분리를 구현했다. 명시적 B→Menu 후보 입력을 같은 실행 경계에 전달한다.
- 조합/설명/purpose/Recovery/rule-generalization 5개 소스는 기존 전용 A/B 경로로 분류했다. Prose review의 before 테스트 사본은 반복 실행 의무가 없는 evidence-only로 분류했다. 기존 기능 테스트를 삭제하지 않았다.
- Active Tooltip validator가 요구하는 `docs/iris_tooltip_t1_display_contract_policy.md`를 복원했다. 대체 정책 경로를 도입하지 않았다.
- Disposable checkout에 필요한 기존 B ZIP과 명시적 Menu 후보 입력을 전달하도록 bootstrap을 보완했다. Origin의 accepted/current 포인터와 composition JSON은 유지한다.
- Change 9는 no-op이다. 기존 책임별 테스트 위치, unittest ID와 runner를 유지한다.
- Change 10은 archive다. 독립 current 실행 의무가 없는 registry closure 본체와 run/validate 진입점 3개를 `Iris/_archive/registry.zip`에 보관했다. Current fixture materializer와 역사 기록은 유지한다. 기존 archive 도구의 create/restore는 exit 0이었다.
- 마지막 전체 실행에서 드러난 두 fixture 불일치를 수정했다. Package support 기대 목록에 `IrisLayer3ProductLookup.lua`, `IrisLayer3LegacyLookup.lua`를 추가했고, `test_current_menu_input_binding`도 product 검사와 같은 명시적 후보 입력을 받도록 했다.

#### 실행 결과와 한계

- 설명 및 CLI/context/serialization 묶음: 32 passed, exit 0.
- 정책 복원 후 B→Menu 및 CLI 묶음: 3 passed, exit 0. Lua syntax 396개 파일, Browser/Wiki 4,210 states, B runtime, stage/ZIP 및 lock/interrupt/recovery를 포함한다.
- Recovery 계약: Before 1 passed, After 1 passed, 각각 exit 0. Naturalization: 양쪽 32 passed 및 15 subtests. Runner 전용 검사: 48 passed. 자세한 기존 실행 기록은 앞 절에 남긴다.
- Archive 검사: 8 passed, 1 skipped, exit 0. Windows symlink 생성 불가로 생긴 skip은 실행 성공으로 간주하지 않는다.
- 최종 After canonical 전체 실행은 **215 passed / 3 failed, exit 1**이다. 두 실패는 위의 package support 목록과 Menu 후보 입력 fixture 문제로 수정했다. 나머지는 G5의 고정 경로 수·해시 기대값과 subject 전환의 불일치다. 이 동일성 검사는 사용자의 최신 지시에 따라 이번 작업의 완료 조건에서 제외하며 추가 봉인이나 재실행으로 해소하지 않는다.
- 마지막 두 fixture 수정 뒤에는 추가 테스트를 실행하지 않았다. 따라서 canonical 전체 PASS나 수정 후 테스트 PASS를 주장하지 않는다. 기존 검사 본문의 해시 확인을 제거하여 통과시키지도 않았다.
- Windows 경로 길이를 위해 저장소 안의 짧은 공유 work root `.w`를 사용했다. 검토용 LFS 객체 부재로 실패한 checkout은 보존했다. 재귀 삭제는 자동 승인 검토가 정책상 거부했으며 `.tmp/e/fb/checkout`으로 비파괴 이동했다.

#### 사용자 PZ 관찰 인계

자동 기능 검사를 통과한 Menu 후보 ZIP은 `.tmp/s/a/.tmp/menu/run-jpbm0mhq/p/Iris.zip`이다. 실제 PZ에서 Browser/Wiki 표시, 툴팁 및 게임 내 상호작용 관찰은 사용자 담당이다. 실제 PZ는 `unvalidated_but_in_scope`이며 live/accepted 전환이나 배포를 하지 않았다. 구현과 위 처분은 완료했으며, 자동 전체 검사의 실패 이력과 마지막 fixture 수정의 미실행 상태는 위와 같이 남긴다. 추가 동일성 증명 없이 이 작업을 closeout한다.

#### 후속: 실패 3건 재검사 완료

사용자가 위 세 실패를 PASS시키도록 명시적으로 요청하여, 해당 노드만 같은 After 작업 사본 `.tmp/s/a`에서 함께 재실행했다. 앞 절의 수정 후 미실행 상태와 G5 완료 조건 제외 처분은 이 후속 결과로 갱신한다.

- Package support 기대 목록에 분리된 ProductLookup/LegacyLookup 모듈을 반영했다.
- Menu 입력 연결 검사가 기존 `IRIS_REFACTOR_MENU_INPUTS` 후보를 받도록 수정했다.
- G5 테스트가 과거 successor의 파일 수와 current 해시를 고정하지 않고 기존 현재 계약과 transition의 목록을 기대값으로 참조하도록 수정했다. 역사 attestation 기대값과 변조 거부 검사는 유지했다. 새 transition이나 봉인 자료는 만들지 않았다.

실행 위치: `.tmp/s/a`. 기존 설치 환경과 `.tmp/e/a-menu-inputs.json`을 재사용하고 TEMP/TMP는 Origin 저장소 안의 `.tmp/e/tmp`로 지정했다.

```powershell
uv run --project Iris/tooling --no-sync python -B -m pytest --noconftest -c Iris/tooling/pyproject.toml Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py::PackageLayer3ChunksOnlyContractTest::test_current_runtime_payload_package_does_not_require_rtc_bundle Iris/build/description/v2/tests/test_layer3_product_integration.py::test_current_menu_input_binding Iris/validation/execution/tests/test_repository_test_execution.py::test_g5_current_capsule_separates_historical_raw_and_current_claim -q
```

결과: **3 passed, exit 0, 61.89초**. 실행 중 상태를 확인했고 정상 종료했다. 전체 suite는 재실행하지 않았으므로 앞선 전체 실행의 실패 이력은 그대로 남긴다. 이번 세 실패의 재검사 결과는 모두 PASS이며 실제 PZ 관찰은 여전히 사용자 담당이다.

#### PZ 관찰 후: 저장소 실행의 Layer3 설명 누락 대응

사용자가 ZIP이 아닌 저장소 Iris 폴더 실행에서 3계층 설명이 사라졌다고 보고했다. 저장소는 legacy generation pointer를 사용하며 optional ProductCurrent 파일이 없다. DataLookup은 optional require의 보호 호출 성공 여부만으로 product가 존재한다고 판단하여, 로더가 없는 모듈에 nil을 반환하면 legacy 데이터를 product fault 경로로 잘못 보내는 결함이 있었다.

`IrisLayer3DataLookup.lua`가 require 반환값도 확인하도록 수정했다. nil은 product 존재로 취급하지 않으며, 실제 product pointer가 있는 경우의 기존 거부 조건은 유지한다. 기존 `lazy_lookup_acceptance_harness.lua`에 optional 모듈의 nil 반환 조건을 반영했다. 실제 사용자 증상의 원인 확정과 복구 확인은 PZ 재시작 후 관찰이 필요하다.

검증: `uv run --project Iris/tooling --no-sync python -B -m pytest --noconftest -c Iris/tooling/pyproject.toml Iris/build/description/v2/tests/test_layer3_lazy_lookup_contract.py -q` → 1 passed, exit 0, 0.32초. 기존 `tools/check_lua_syntax.ps1`에 변경된 Lua 두 파일을 Roots 배열로 전달 → 2 files OK, exit 0. 최초 문법 검사 호출은 배열 인자 전달 오류로 exit 1이었으며 올바른 배열로 다시 실행했다. 추가 동일성 검사나 패키지 재생산은 하지 않았다.

#### 최종 사용자 확인 및 closeout

사용자가 설명 누락 수정 후 “인게임 검증도 통과했어”라고 확인했다. 확인 대상은 사용자가 실행한 저장소 Iris 폴더이며, 위 PZ 관찰 대기 상태와 설명 복구 미확인 상태를 사용자 관찰 PASS로 갱신한다. 이 확인을 별도 ZIP의 실행 결과나 전체 자동 suite 재실행 결과로 확대하지 않는다.

채택한 리팩토링 범위의 구현, 실패 세 노드 수정·재검사, 저장소 실행의 설명 누락 수정 및 사용자 인게임 확인을 완료했다. 추가 검사·동일성 증명·봉인 자료 없이 closeout한다.
