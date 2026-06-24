# Implementation Plan

> 상태: planned / scope-lock candidate
> 작성일: 2026-06-13
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> 입력 로드맵: `Compose Entrypoint Guard Hardening`
> 검토 반영: `Compose Entrypoint Guard Hardening Plan` FAIL review C1-C3 / R1-R10
> Cycle 2 검토 반영: WARN W1 / optional M1, N1-N3

---

## 1. Objective

DVF 3-3 compose 경로의 current rendered output write boundary를 CLI entrypoint가 아니라 `build_rendered()` write boundary까지 내린다.

완료 목표는 `python -m tools.build.compose_layer3_text` CLI 호출과 `build_rendered()` programmatic direct call이 동일한 guard를 통과하게 만드는 것이다. legacy profile 또는 legacy-shaped input이 current-looking output path, 특히 `Iris/build/description/v2/output/dvf_3_3_rendered.json`, 을 덮는 경로는 fail-loud로 차단한다.

이 계획은 guard hardening 계획이며, vNext cutover, runtime chunk 교체, Lua bridge export 변경, Browser / Tooltip / Wiki behavior 변경을 수행하지 않는다.

---

## 2. Scope

이 계획의 intended modification scope는 다음으로 제한한다.

* `compose_layer3_text.py`의 current / historical / diagnostic write contract 명시화
* `build_rendered()` 직접 호출에 대한 shared write-boundary guard 적용
* current output path 및 current-equivalent alias / normalized path 보호
* `compose_protected_output_paths.json`을 this-round CLOSED / exhaustive protected current-output set으로 봉인
* protected set에 포함되는 모든 current-equivalent write의 structural no-partial-write / atomicity 보장
* legacy profile의 current output write 금지
* historical / diagnostic route의 explicit non-current output path 보존
* `compose_context`를 `current | staging | historical | diagnostic` 중 하나로 명시
* `compose_context × resolved output-path-class` 판정 matrix를 닫고, explicit non-current path + missing context를 fail-loud 처리
* 기존 staging / historical / diagnostic caller를 새 `compose_context` 계약으로 migration
* v2 current profile을 positive discriminator로 판정하고 ambiguous / partial / unknown profile은 current output에서 fail-loud 처리
* rejected call의 no-mutation / no-partial-write 검증
* guard 또는 validator / wrapper 도구가 추가될 경우 negative self-test와 halt semantics 검증
* closeout claim을 guard hardening 범위로 제한하는 staging draft 문서 packet 작성

### Explicitly Out Of Scope

* vNext baseline cutover
* 2105 successor baseline identity 봉인
* source manifest 재생성
* facts / decisions / rendered full regeneration
* Lua bridge export 변경
* runtime chunk replacement
* `IrisLayer3Data.lua` 또는 chunk payload 변경
* current 6-entry fixture authority 승격
* legacy historical reproduction route 삭제
* diagnostic route 삭제
* compose profile 전면 재설계
* `body_plan` 재설계
* selected_role / resolver / Silent 21 / Layer4 / ACQ_DOMINANT / Acquisition Lexical 재오픈
* public-facing UI 변경
* packaging / release / Workshop readiness 검증
* manual in-game QA
* 전체 architecture redesign

---

## 3. Non-Goals

* current rendered text의 내용 품질을 개선하지 않는다.
* semantic quality 판단, recommendation, 비교, 추천 문구를 추가하지 않는다.
* runtime Lua에서 compose / repair / source validation을 수행하게 만들지 않는다.
* historical byte reproducibility unresolved surface를 해결하지 않는다.
* vNext staging evidence를 current authority로 승격하지 않는다.
* current output no-mutation을 release readiness나 package readiness로 확대 해석하지 않는다.

---

## 4. Assumptions

* 최상위 헌법 기준은 `docs/Philosophy.md`다.
* Iris는 runtime에서 의미를 재판정하지 않고, offline build artifact를 소비한다.
* current `Iris/build/description/v2/output/dvf_3_3_rendered.json`은 full runtime authority가 아니라 current 6-entry fixture / non-authority로 읽지만, current-looking protected output path로 보호한다.
* existing runtime chunks는 후속 cutover 전 deployable runtime authority이며, 이번 계획에서 변경하지 않는다.
* Round 3 current contract route는 `python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`다.
* default pytest route는 `python -B -m pytest -q`로 읽는다.
* historical / diagnostic route는 삭제하지 않고 explicit non-current output path에서 유지한다.
* compose_context is required for every direct function call write. Direct call + missing `compose_context` fails loud with `context required`, even if the resolved output path is current-equivalent.
* CLI default may assign `compose_context = current` before the shared guard only through the CLI context construction path.
* compose_context is required for every explicit non-current write. An explicit non-current output path without `compose_context` fails loud with `context required`.
* Identified staging, historical, and diagnostic callers must be migrated to pass the explicit `compose_context`; this is a full caller inventory and migration task, not a narrow test fixture update.
* `compose_protected_output_paths.json`은 이번 라운드의 closed authoritative protected current-output set이다. 이 set에 없는 current-equivalent write target은 fail-loud reject 대상이다.
* `compose_protected_output_paths.json` records the closed known protected set, while the runtime classifier must also reject any newly observed current-equivalent target not listed in the manifest.
* no-mutation verdict는 rejected / forbidden calls와 protected runtime surfaces에 적용한다. Guard를 통과한 accepted current/default write는 current fixture output을 갱신할 수 있지만, full runtime authority promotion을 의미하지 않는다.
* accepted current write tests는 기본적으로 temporary current-equivalent fixture path를 사용한다. 실제 current fixture write route를 검증해야 할 때만 real protected current output을 쓰고, before / after hash를 반드시 비교한다.
* shared guard inside `build_rendered()` is the authority boundary. External guard / validator tools are supplementary evidence only and cannot replace the function-level write guard.
* 현재 working tree에는 이 계획과 무관한 변경이 많으므로, 실행 시 intended files만 stage / commit 대상으로 삼는다.

---

## 5. Repository Areas Affected

### Code

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tools/build/compose_layer3_io.py` optional only if Option B staged-temp + atomic-rename implementation is selected
* `Iris/build/description/v2/tools/build/guard_compose_entrypoint_output_paths.py` if separate guard tool이 필요할 경우
* `Iris/build/description/v2/tools/build/validate_compose_entrypoint_guard.py` if separate validator가 필요할 경우

### Tests

* `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`
* `Iris/build/description/v2/tests/test_current_authority_source_path_guard.py`
* `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py` if a new focused test file is clearer
* `Iris/_docs/round3/round3_run_contract_tests.py` only if new current-route tests must be classified into the round3 contract runner

### Docs

* `docs/compose_entrypoint_guard_hardening_plan.md`
* `docs/compose_entrypoint_guard_hardening_closeout.md` after execution
* `docs/compose_entrypoint_guard_hardening_decisions_packet.md` as STAGING DRAFT after execution
* `docs/compose_entrypoint_guard_hardening_roadmap_packet.md` as STAGING DRAFT after execution

### Config

* None expected.
* `pytest.ini` must not be changed unless test discovery cannot include the new focused tests through existing routes.

### Generated Artifacts

* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_entrypoint_guard_call_surface_inventory.md`
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_write_path_matrix.md`
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_protected_output_paths.json` as CLOSED / exhaustive protected current-output set
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_pre_change_hash_snapshot.json`
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_guard_tool_selftest_report.json`
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_entrypoint_guard_regression_report.json`
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_entrypoint_guard_no_mutation_verdict.json`

---

## 6. Planned Changes

### Change 1 - Scope Lock and Call-Surface Inventory

Purpose:

`build_rendered()`와 current rendered write path에 도달하는 모든 호출 표면을 식별하고, protected path 및 allowed / forbidden matrix를 먼저 고정한다.

Files:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`
* `Iris/build/description/v2/tests/test_current_authority_source_path_guard.py`
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/*`

Implementation Notes:

* direct `build_rendered()` 호출처를 inventory한다.
* existing staging / historical / diagnostic callers를 inventory하고, 새 `compose_context` 계약으로 migration해야 할 caller 목록을 작성한다.
* CLI entrypoint에서만 수행되는 guard와 function-level에서 수행되는 guard를 분리해 기록한다.
* current output path alias, relative path, Windows separator, resolved path를 protected path classifier 후보에 포함한다.
* `compose_protected_output_paths.json`은 후보 목록이 아니라 this-round closed authoritative protected current-output set으로 작성한다.
* closed protected set은 최소한 current rendered output, paired style log, requeue candidates, temp output naming pattern, current-equivalent aliases, normalized / relative / Windows separator equivalent paths를 포함한다.
* closed protected set에 열거되지 않은 current-equivalent write target은 fail-loud reject한다.
* vNext staging explicit output path는 current authority가 아니라 staging context로 분리한다.
* pre-change protected surface hash snapshot은 protected set 전체를 대상으로 확보한다.

Validation:

* call-surface inventory가 `build_rendered()` direct call, CLI default, diagnostic resolver, vNext staging explicit call을 모두 포함해야 한다.
* inventory가 staging / historical / diagnostic caller의 migration 대상 여부를 포함해야 하며, 단순 테스트 fixture 수정으로 축소되면 안 된다.
* protected path matrix는 current / staging / historical / diagnostic을 구분해야 한다.
* inventory closeout 전 unlisted current-equivalent write target을 fail-loud로 취급하는 rule을 확인해야 한다.

---

### Change 2 - Current / Historical / Diagnostic Write Contract Specification

Purpose:

current/default write와 historical/diagnostic write의 허용 조건을 코드 계약과 문서 계약으로 분리한다.

Files:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py`
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_write_path_matrix.md`

Implementation Notes:

* current/default write는 `compose_context = current`, v2 profile, `body_plan`, current input contract, current write intent가 모두 있어야 허용한다.
* v2 profile은 "legacy가 아님"이 아니라 positive allowlist로 판정한다.
* `profile_class = v2_current`는 v2 schema marker, body_plan binding, current input contract marker, required current profile fields가 모두 있을 때만 부여한다.
* partial / unknown / ambiguous profile은 current output에서 fail-loud reject한다.
* legacy sentence_plan-only profile은 current/default output path에 쓸 수 없다.
* historical / diagnostic write는 explicit `compose_context`와 explicit non-current output path를 요구한다.
* staging write는 explicit `compose_context = staging`, explicit non-current output path, sealed staging root, non-current path classification, no current-equivalent alias 조건을 모두 만족해야 한다.
* explicit non-current output path with missing `compose_context` is not inferred from path location; it fails loud with `context required`.
* mode 없음 또는 default 해석은 current guard를 적용한다.
* legacy auto-detection fallback은 금지한다.

Declared `compose_context × resolved output-path-class` verdict matrix:

| Declared `compose_context` | Resolved output-path-class | Verdict |
| --- | --- | --- |
| missing / null | current-equivalent | FAIL-LOUD: `context required`; CLI default is excluded because CLI must assign `compose_context = current` before shared guard |
| missing / null | staging / historical / diagnostic / other non-current | FAIL-LOUD: `context required` |
| `current` | current-equivalent | PASS only when v2 current profile, current input contract, and current write intent pass |
| `current` | staging / historical / diagnostic / other non-current | FAIL-LOUD: current context cannot write non-current output |
| `staging` | sealed staging non-current | PASS only when explicit output path and no current-equivalent alias pass |
| `staging` | current-equivalent | FAIL-LOUD |
| `staging` | historical / diagnostic / other non-current | FAIL-LOUD unless the path is inside the sealed staging root |
| `historical` | explicit historical non-current | PASS when historical contract passes |
| `historical` | current-equivalent | FAIL-LOUD |
| `historical` | staging / diagnostic / other non-current | FAIL-LOUD unless explicitly allowed by the historical output classifier |
| `diagnostic` | explicit diagnostic non-current | PASS when diagnostic contract passes |
| `diagnostic` | current-equivalent | FAIL-LOUD |
| `diagnostic` | staging / historical / other non-current | FAIL-LOUD unless explicitly allowed by the diagnostic output classifier |

Validation:

* current v2 profile + current input + current output은 pass해야 한다.
* legacy profile + current output은 CLI와 direct call 모두 fail해야 한다.
* partial / unknown / ambiguous profile + current output은 fail해야 한다.
* legacy profile + explicit historical / diagnostic non-current output은 pass해야 한다.
* staging context missing but staging root path present case는 fail해야 한다.
* explicit non-current path + missing `compose_context`는 `context required`로 fail-loud해야 한다.

---

### Change 3 - Shared Guard Extraction and `build_rendered()` Boundary Enforcement

Purpose:

CLI guard와 direct function guard를 같은 shared guard로 통합하고, `build_rendered()` 내부 write boundary에서 반드시 실행되게 한다.

Files:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py`

Implementation Notes:

* shared guard inside `build_rendered()` is the authority boundary.
* shared guard는 compose context, write intent, output path classification, profile schema classification, input contract classification, current write permission verdict를 함께 판단한다.
* external guard / validator tools are supplementary evidence only and cannot replace this function-level guard.
* render 전 early guard를 두되, 실제 file write 직전 final guard를 반드시 둔다.
* guard fail은 fallback 없이 `ComposeEntrypointGuardError` 같은 전용 guard exception으로 fail-loud 처리하는 것을 우선한다. 최소 payload는 output path class, profile class, compose context, write intent, rejection reason이다.
* protected set을 건드리는 모든 write는 다음 둘 중 하나로 구조적으로 보호한다.
  * Option A: final guard pass 전에는 protected output, side output, temp output, style log, requeue artifact를 생성하지 않는다.
  * Option B: 모든 write를 temp path에 staging하고, final guard pass 후에만 atomic commit / rename한다.
* Atomicity guarantee through Option A or Option B is mandatory. `compose_layer3_io.py` is optional only if Option B staged-temp + atomic-rename implementation is selected.
* guard fail 이후 rendered output, style log, requeue candidates, temp output 같은 current-equivalent side output을 생성하거나 부분 변경하지 않는다.
* CLI는 argument parsing과 context construction만 담당하고, 허용 / 거부 판정은 shared guard로 위임한다.

Validation:

* direct `build_rendered()` current pass test
* direct `build_rendered()` legacy + current output reject test
* CLI default current pass test
* CLI legacy + current output reject test
* rejected call no-write assertion
* rejected call no-partial-write assertion
* mid-pipeline guard fail leaves zero partial bytes across the full protected set

---

### Change 4 - Path Normalization and Protected Surface Coverage

Purpose:

relative path, alias, Windows separator, resolved path 차이로 current output protection을 우회하지 못하게 한다.

Files:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py`
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_protected_output_paths.json`

Implementation Notes:

* `Path.resolve()` 기반 classifier를 사용하되, missing parent 또는 non-existent output file을 다루는 경우도 테스트한다.
* symlink / junction policy는 resolved target 기준으로 판정한다. protected set 안으로 resolve되는 경로는 protected로 취급하고, classification failure는 fail-loud로 처리한다.
* protected set은 minimum list가 아니라 CLOSED / exhaustive set이다.
* closed set에는 rendered output, paired style log, requeue candidates, temp naming pattern, current-equivalent aliases가 포함되어야 한다.
* current write가 reject될 때 protected set 전체가 no-mutation 대상이다.
* staging output은 특정 `phase4` hardcoding이 아니라 sealed staging root 기준으로 정의한다.
* staging pass 조건은 `compose_context = staging`, explicit output path, sealed staging root, non-current path classification, no current-equivalent alias, no default/current path resolution이다.
* direct call에서 `output_path`가 생략되거나 default current path로 resolve되더라도 missing `compose_context`는 `context required`로 fail-loud reject한다.
* `compose_context = current` 자동 assignment는 CLI default context construction에서만 허용한다.

Validation:

* canonical protected path reject
* relative protected path reject
* Windows separator protected path reject
* normalized alias protected path reject
* explicit staging output pass only when all staging context conditions pass
* staging context missing but staging root path present reject
* staging context present but current-equivalent path target reject
* non-existent parent path classification test
* symlink / junction alias into protected set reject
* if symlink / junction creation is unavailable in the local or CI environment, run classifier-policy tests with resolved-path fixtures and report the environment limitation instead of claiming OS-level alias validation

---

### Change 5 - Guard Tool Self-Test and Halt Semantics

Purpose:

guard / wrapper / validator 도구를 새로 만들 경우, supplementary evidence로만 사용한다. 이 도구들은 `build_rendered()` 내부 shared guard를 대체할 수 없다.

Files:

* `Iris/build/description/v2/tools/build/guard_compose_entrypoint_output_paths.py` if needed
* `Iris/build/description/v2/tools/build/validate_compose_entrypoint_guard.py` if needed
* `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py`
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/compose_guard_halt_semantics.md`

Implementation Notes:

* protected output path를 가진 known-bad input은 non-zero / fail을 반환해야 한다.
* guard fail 후 후속 generation command는 실행되지 않아야 한다.
* warning-only guard는 protected write prevention claim의 근거로 사용하지 않는다.
* self-test는 static string뿐 아니라 normalized path case를 포함한다.
* external tool pass는 function-level guard pass를 의미하지 않는다. closeout은 두 표면을 별도로 기록한다.

Validation:

* protected current output path negative self-test: FAIL / non-zero
* alias / relative / Windows separator negative self-test
* halt-on-nonzero test
* guard fail 이후 generation command non-execution assertion
* external tool result cannot bypass `build_rendered()` shared guard assertion

---

### Change 6 - Legacy / Historical / Diagnostic Path Isolation

Purpose:

legacy compose route를 삭제하지 않고 explicit historical / diagnostic non-current path에 격리한다.

Files:

* `Iris/build/description/v2/tools/build/compose_layer3_text.py`
* `Iris/build/description/v2/tests/test_compose_layer3_text_v2.py`
* `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py`

Implementation Notes:

* historical / diagnostic output root allowlist 또는 classifier를 명시한다.
* identified staging / historical / diagnostic callers must be migrated to pass explicit `compose_context`.
* caller migration은 테스트 몇 개를 새 계약에 맞추는 작업이 아니라, `build_rendered()` 및 CLI/wrapper/tooling 호출 표면을 전수 확인하고 production/staging/historical/diagnostic caller를 새 계약으로 갱신하는 작업이다.
* legacy profile은 historical / diagnostic lane에서만 허용한다.
* historical / diagnostic mode라도 path 생략이 current output으로 resolve되면 hard fail한다.
* historical reproduction tests가 default current path에 의존하고 있다면 explicit non-current fixture path로 갱신한다.
* vNext staging caller가 explicit phase path에만 의존하고 있다면 `compose_context = staging`을 넘기도록 갱신한다.
* migration 후에도 legitimate staging / diagnostic non-current writes가 over-block되지 않아야 한다.

Validation:

* historical route explicit output pass
* diagnostic route explicit output pass
* existing staging caller after `compose_context` migration pass
* existing historical caller after `compose_context` migration pass
* existing diagnostic caller after `compose_context` migration pass
* all identified staging / historical / diagnostic callers are accounted for in the migration inventory
* historical route default/current output reject
* diagnostic route default/current output reject
* missing `compose_context` + explicit non-current path reject
* historical preservation policy 유지 확인

---

### Change 7 - Regression, No-Mutation Evidence, and Closeout Packet

Purpose:

current route는 계속 통과하고, direct caller 우회는 닫혔으며, protected current output은 변경되지 않았음을 evidence로 남긴다.

Files:

* `Iris/_docs/round3/round3_run_contract_tests.py` if current-route classification update is needed
* `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/*`
* `docs/compose_entrypoint_guard_hardening_closeout.md`
* `docs/compose_entrypoint_guard_hardening_decisions_packet.md`
* `docs/compose_entrypoint_guard_hardening_roadmap_packet.md`

Implementation Notes:

* protected surface hash snapshot before / after를 비교한다.
* no-mutation claim은 self-report만으로 하지 않고 protected set 전체에 대한 external hash diff로 확인한다.
* no-mutation verdict applies to rejected / forbidden calls and protected runtime surfaces.
* accepted current/default writes may update the current fixture output only when they pass the shared current write guard.
* accepted current/default writes do not imply full runtime authority promotion.
* closeout은 guard hardening claim만 포함한다.
* `decisions_packet`과 `roadmap_packet`은 STAGING DRAFT artifacts only다. 이 packet들은 canonical `docs/DECISIONS.md` 또는 `docs/ROADMAP.md`를 수정하지 않는다.
* canonical promotion은 별도 post-execution adversarial review와 사용자 single-writer seal 이후에만 가능하다.
* runtime / chunk / Lua bridge / UI / release readiness claim은 명시적으로 배제한다.

Validation:

* current route 44 tests pass
* default pytest route pass
* new direct caller guard tests pass
* legacy / historical / diagnostic expected pass/fail matrix pass
* protected set hash unchanged on rejected / forbidden calls
* rejected calls create no current partial output across the full protected set
* closeout `complete` means execution-complete-and-self-validated only

---

## 7. Validation Plan

### Automated Validation

Exact commands must be recorded in closeout, and no validation may be claimed as passed unless the relevant command exits with code 0.

* `python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure`
* `python -B Iris/_docs/round3/round3_run_contract_tests.py --class historical`
* `python -B Iris/_docs/round3/round3_run_contract_tests.py --class diagnostic`
* `python -B -m pytest -q`
* `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_compose_layer3_text_v2.py"`
* `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_current_authority_source_path_guard.py"`
* `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_compose_entrypoint_guard_hardening.py"` if the new focused test file is added
* guard tool negative self-test command if a separate guard tool is introduced
* validator known-bad fixture test command if a separate validator is introduced
* independent before / after hash diff for the entire closed protected set

Windows path variants may be recorded as secondary notation, but closeout pass/fail evidence uses the repo-relative commands above.

No-mutation rule:

* Rejected / forbidden calls must leave the entire closed protected set unchanged and must create no partial current-equivalent output.
* Accepted current/default writes may update current fixture output only after shared guard pass.
* Accepted current/default writes do not imply full runtime authority promotion.
* Real protected current output must be hash-checked before and after all rejected-call tests.

Required validation matrix:

| Case | Expected |
| --- | --- |
| CLI default + v2 profile + current input + current output | PASS |
| direct `build_rendered()` + v2 profile + current input + current output | PASS |
| direct `build_rendered()` + current-equivalent output + missing `compose_context` | FAIL-LOUD: `context required` |
| CLI default with omitted output path after CLI assigns `compose_context = current` | PASS when current guard passes |
| CLI default + legacy profile + current output | FAIL |
| direct `build_rendered()` + legacy profile + current output | FAIL |
| direct `build_rendered()` + partial profile + current output | FAIL |
| direct `build_rendered()` + unknown profile + current output | FAIL |
| direct `build_rendered()` + ambiguous profile + current output | FAIL |
| CLI historical / diagnostic + legacy profile + explicit non-current output | PASS |
| direct `build_rendered()` + legacy profile + explicit non-current intent + explicit non-current output | PASS |
| historical / diagnostic path omission resolving to current output | FAIL |
| explicit non-current path + missing `compose_context` | FAIL-LOUD: `context required` |
| missing `compose_context` + explicit non-current path silently falls into current lane | FAIL |
| protected output alias / relative / Windows-normalized current path | FAIL |
| unlisted current-equivalent write target under output root unknown sibling | FAIL |
| unlisted current-equivalent write target with rendered basename variant | FAIL |
| unlisted current-equivalent write target with temp naming pattern variant | FAIL |
| staging context missing but staging root path present | FAIL |
| staging context present but current-equivalent path target | FAIL |
| existing staging caller after `compose_context` migration | PASS |
| existing historical caller after `compose_context` migration | PASS |
| existing diagnostic caller after `compose_context` migration | PASS |
| identified staging / historical / diagnostic caller omitted from migration inventory | FAIL |
| legitimate staging / diagnostic write over-block | FAIL-LOUD and rollback trigger |
| known current v2 positive discriminator | PASS |
| legacy / sentence_plan-only / unknown profile discriminator on current path | FAIL |
| guard fail after pre-flight | no downstream generation |
| mid-pipeline guard fail | zero partial bytes across full protected set |
| rejected call leaves full protected set unchanged | PASS |
| rejected call creates no partial current output across full protected set | PASS |
| current route regression | PASS |
| default pytest route | PASS |
| known-bad validator fixture, if validator exists | FAIL |
| dry-run before / after independent hash diff, if dry-run exists | unchanged |

### Manual Validation

* Review `git diff --stat` and `git diff` for intended-file-only changes.
* Inspect generated closeout packet and staging draft governance packets for claim inflation.
* Confirm `decisions_packet` and `roadmap_packet` are staging drafts only and do not modify canonical `docs/DECISIONS.md` or `docs/ROADMAP.md`.
* Confirm runtime Lua, Lua bridge, chunk manifest, chunk files, Browser / Tooltip / Wiki behavior are not changed.
* Confirm historical / diagnostic routes are preserved rather than deleted.

### Validation Limits

* no in-game manual QA
* no multiplayer validation
* no runtime chunk equivalence validation
* no Lua bridge export validation beyond no-mutation
* no package validation unless separately approved
* no Workshop readiness validation
* no B42 readiness validation
* no successor baseline validation
* no source-to-runtime full regeneration validation
* no public-facing UI validation
* no semantic quality validation
* no full historical artifact byte reproducibility closure
* no vNext cutover evidence production

---

## 8. Risk Surface Touch

### Authority Surface

Touched.

The enforcement point for current rendered output writes moves from CLI-only guard toward shared function-level write-boundary guard. This changes who may write current-looking output paths, not the source / facts / decisions / rendered content authority itself.

The shared guard inside `build_rendered()` is the authority boundary. External guard tools are supplementary evidence only. `decisions_packet` and `roadmap_packet` are staging draft artifacts and do not promote canonical `DECISIONS.md` / `ROADMAP.md`.

### Runtime Behavior Surface

None expected.

Runtime Lua, Browser, Tooltip, Wiki, Lua bridge, chunk manifest, and chunk payload must not change.

### Compatibility Surface

Limited internal compatibility impact.

Any internal script or test that directly calls `build_rendered()` with legacy profile and current-looking output path must fail after this change. Explicit historical / diagnostic non-current output use must remain supported.

### Sealed Artifact Surface

Concern unless protected set and atomicity requirements pass.

Sealed runtime artifacts are protected. Current-equivalent build outputs are guarded by the closed protected set. New staging evidence artifacts may be generated under `Iris/build/description/v2/staging/compose_entrypoint_guard_hardening/`.

### Public-Facing Output Surface

None.

User-facing text, tooltip, wiki panel, browser behavior, runtime chunk payload, and published package content do not change.

---

## 9. Risk Analysis

### Architecture Risk

* A guard placed only in CLI keeps direct caller bypass open.
* A guard placed too high can mix current, staging, historical, and diagnostic responsibilities.
* A separate guard tool that only reports without halting can create false confidence.
* Canonical governance packet promotion would violate single-writer authority if it happens without separate user seal.

### Runtime Risk

* Low, because runtime Lua and chunks are out of scope.
* Any accidental write to runtime chunk files is a hard scope violation.

### Compatibility Risk

* Existing internal direct callers may rely on permissive `build_rendered()` writes.
* Historical / diagnostic tests may rely on default output path convenience.
* vNext staging explicit output may be over-blocked if staging context is not classified separately.
* Existing staging calls may rely on phase-specific assumptions instead of explicit `compose_context`.
* Legitimate vNext staging / diagnostic non-current writes may be over-blocked if migration is incomplete.

### Regression Risk

* Current route 44 tests could fail if current v2 profile is misclassified as legacy.
* Ambiguous / partial / unknown profiles could be misclassified as current if positive discriminator is incomplete.
* Path classifier could miss alias / normalized path cases.
* Guard fail could occur after partial style log or rendered output writes if final guard and atomic write order are not handled carefully.
* CLI and direct function calls could produce inconsistent error semantics if they do not share the same guard.
* Full protected set no-mutation could be under-validated if side outputs or temp naming patterns are omitted.

---

## 10. Rollback Plan

Rollback should be narrow and preserve protected artifacts.

* Revert shared guard implementation.
* Revert `build_rendered()` guard insertion.
* Revert CLI behavior changes that depend on the new shared guard.
* Revert or quarantine new direct caller guard tests.
* Revert historical / diagnostic fixture path updates only if they were introduced for this round.
* Remove or disconnect new guard / validator / wrapper tools if they cause false pass or false fail behavior.
* Do not roll back by replacing current output, runtime Lua, Lua bridge, chunk manifest, or chunk files.
* After rollback, verify full protected set hash against pre-change snapshot.

Rollback is required if any of the following occurs:

* current route 44 tests fail because current v2 path is blocked
* explicit historical / diagnostic non-current output is blocked
* legitimate vNext staging / diagnostic non-current write is over-blocked after migration
* legacy profile detection misclassifies current v2 profile
* ambiguous / partial / unknown profile is accepted on current output
* rejected call leaves partial current output anywhere in the full protected set
* protected set hash changes unexpectedly during rejected / forbidden calls
* guard fail does not halt downstream generation where halt is claimed
* validator / dry-run self-test passes known-bad cases
* staging draft packet is promoted into canonical `DECISIONS.md` / `ROADMAP.md` without separate user seal

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Pulse / Iris module boundaries must remain intact.
* Iris runtime/build-time separation must remain intact.
* Runtime Lua must not perform compose, repair, source validation, or semantic quality judgment.
* Current route and historical / diagnostic route separation must remain intact.
* Legacy historical reproduction route must not be deleted.
* Guard failure must be fail-loud, not fallback or silent downgrade.
* `active / silent` must not be revived as current writer vocabulary.
* `adopted / unadopted` must not be expanded into quality-pass, publish_state, deletion, or suppression semantics.
* Staging output and current output must not be confused.
* Current 6-entry fixture must not be promoted to full runtime authority.
* Existing runtime chunks must not change.
* vNext staging evidence must not be promoted to current authority.
* `decisions_packet` and `roadmap_packet` must remain STAGING DRAFT artifacts unless the user separately approves canonical promotion.
* Canonical promotion requires separate post-execution adversarial review and user single-writer seal.
* `complete` means guard-hardening execution completed and self-validated only.
* `complete` does not mean canonical promotion, adversarial-review PASS, vNext cutover, release readiness, or runtime authority replacement.
* Browser / Wiki / Tooltip behavior must not change.
* Package readiness, release readiness, Workshop readiness, B42 readiness, and manual in-game QA pass must not be claimed.
* Minimal diff preservation applies: do not refactor unrelated compose modules while hardening this guard.
* Dirty working tree safety applies: stage only files intentionally changed for this scope.

---

## 12. Expected Closeout State

Expected closeout target: `complete` as execution-complete-and-self-validated only

Closeout may be marked complete only if:

* CLI and direct `build_rendered()` calls share the same current write guard.
* `compose_protected_output_paths.json` is closed / exhaustive for this round.
* unlisted current-equivalent write targets fail-loud.
* legacy profile writes to current output path fail-loud.
* partial / unknown / ambiguous profiles fail-loud on current output.
* explicit historical / diagnostic non-current output remains supported.
* the declared `compose_context × resolved output-path-class` matrix is implemented and validated.
* explicit non-current output path without `compose_context` fails loud with `context required`.
* direct call with current-equivalent output and missing `compose_context` fails loud with `context required`.
* identified staging / historical / diagnostic callers are fully inventoried and migrated to explicit `compose_context`; this closeout cannot be satisfied by updating only selected tests.
* staging writes require explicit staging context, sealed staging root, explicit non-current output path, and no current-equivalent alias.
* protected path alias / normalization cases are covered.
* rejected / forbidden calls leave the full protected set unchanged and create no partial current-equivalent output.
* protected writes are structurally atomic: every protected write occurs only after final guard pass, or is staged to temp and atomically committed after final guard pass.
* current route regression passes.
* direct caller guard tests pass.
* guard / validator / dry-run self-tests pass when those tools are introduced.
* external guard tools remain supplementary and do not replace `build_rendered()` shared guard.
* runtime Lua, Lua bridge, chunk manifest, chunk payload, Browser / Tooltip / Wiki behavior remain unchanged.
* closeout claim is limited to compose entrypoint guard hardening.
* decisions / roadmap packets are staging drafts only and do not modify canonical governance docs.
* canonical promotion is left to separate post-execution adversarial review and user seal.

If any required validation is blocked or intentionally skipped, closeout must be `partial` or `implemented_only`, with the blocked command and reason recorded explicitly.
