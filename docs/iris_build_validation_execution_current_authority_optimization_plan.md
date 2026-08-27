# Iris 빌드·검증 실행 및 Current Authority 탐색 최적화 Implementation Plan

> 상태: review-ready operational correction draft — plan carrier·exact G5 chain·terminal environment·W0 admission 보정, 독립 계획 검토 PASS 전 구현 보류  
> 개정일: 2026-08-27  
> 기준 로드맵: `Iris 빌드·검증 실행 모델 및 Current Authority 탐색 구조 통합 최적화 Roadmap`  
> 검증 깊이: bounded — 중간 focused validation 3회 이하, 최종 full A/B 1회  
> 구현 예산: W0 + Wave 1~3 구현 및 focused checkpoint의 자동화 wall-clock 목표 90분 이내, 120분 초과 예상 또는 관측 시 중단·재구조화  
> terminal 예산: Wave 4 package + clean Run A/B + comparator는 구현 예산과 분리 측정·기록

이 계획은 개인 모딩 프로젝트에 맞는 비용으로 Iris의 offline build·validation 흐름을 더 단순하고 부드럽게 만드는 1차 최적화 계획이다. 분석 보고서를 늘리는 것이 아니라, 안전하게 확인된 중복 실행·중복 구현·분산된 command/readpoint를 실제로 줄이는 데 목적이 있다.

이 계획의 closeout은 Iris build·validation execution 및 current-authority 탐색 최적화에만 귀속된다. Wiki/Browser presentation 및 Lua UI 최적화의 완료를 주장하지 않는다.

---

## 1. Objective

다음을 실제 구현 결과로 달성한다.

1. current public build/validation 경계가 deterministic canonical result와 별도 volatile execution envelope를 사용한다.
2. thin `PhaseRunner`가 dependency ordering, run-local reuse, metric, issue/artifact association만 담당한다.
3. 동일 clean-checkout full gate 안의 current-output seed producer를 `6회 → 3회`로 줄인다.
4. 안전성과 효과가 확인된 repeated read, subprocess, digest/path/process helper 중복을 실제로 통합한다.
5. current owner와 predecessor tree 사이의 live source-authority 중복을 제거하고 current import/command owner를 단일화한다.
6. canonical CLI는 existing validation authority의 얇은 adapter로 수렴한다.
7. 사람과 AI가 `docs/IRIS_CURRENT.md`와 static route index에서 current authority, producer, validator, artifact, explicit receipt locator를 1~2 jump 안에 찾을 수 있게 한다.
8. 구현 종료 시 `unsupported_retention`, `remaining_eligible_optimization`, `unimplemented_optimization`, `unmeasured_defer`를 모두 `0`으로 닫는다.
9. 위 목표를 정규 테스트와 검증 절차의 순증가를 최소화하면서 달성한다.

이 계획에서 최적화는 runtime FPS나 wall-clock 성능 경쟁을 뜻하지 않는다. 실행 주체, command, authority hop, 중복 producer/read/subprocess, 실패 전달, AI 탐색 비용을 줄여 작업 흐름을 더 효율적이고 예측 가능하게 만드는 것을 뜻한다.

---

## 2. Scope

### 2.1 Product S0, plan carrier and implementation base

- product/code S0 commit: current local `main`의 `e6310737a99873e2c58f3f399de77ef97473f39f`
- product/code S0 tree: `fa58a95445a75308d06b24ac8515ea4d0789ca0f`
- 반드시 보존할 lightweighting implementation: `801f15f678fe9c5fd67be0f805f29ed3ba9db9b3`
- 반드시 보존할 lightweighting documentation closeout: `28f95b63df7ebe4d87e4071e018e1e240dfa938b`

이 계획 파일은 구현 착수 전에 **tracked documentation-only plan carrier**로 commit해야 한다. plan carrier의 sole parent는 product/code S0이며, 허용 diff는 이 계획 파일뿐이다. 실제 carrier commit/tree는 commit 후 W0 baseline에 기록한다. 구현 base는 product/code S0가 아니라 이 plan carrier이며, product/code S0 수치는 before 비교용으로 계속 고정한다.

구현은 plan carrier에서 분기한 clean worktree와 `codex/iris-build-validation-current-authority-optimization` branch에서만 수행한다. dirty main의 파일을 복사·병합하거나 absolute-path source로 import하지 않는다. plan carrier가 product/runtime/tooling/test mutation을 포함하거나 worktree가 clean하지 않으면 W0는 `BLOCKED`다. remote push는 착수 조건이 아니다.

current G5 compiler identity chain은 아래 **세 exact file만** 뜻한다.

| Role | Exact path | S0 Git blob | S0 raw SHA-256 |
|---|---|---|---|
| G5 successor 0013 | `Iris/validation/clean_checkout/evidence/g5_compiler_identity_successor_0013.json` | `21f5f8b8bd44db8fc6db723ca664f25b45bdf3b8` | `aa53450a706c1c6d67182355f3aec537c50586c96d53ed9a6af463fd51e7648d` |
| G5 successor 0014 | `Iris/validation/clean_checkout/evidence/g5_compiler_identity_successor_0014.json` | `66521e6b54b5c9b06f37d12ea1e26193493d80af` | `62a6150cb976075ae60f641c4e1d099588fd0bccea351878335977ea9caddf40` |
| G5 successor 0015 | `Iris/validation/clean_checkout/evidence/g5_compiler_identity_successor_0015.json` | `3e42f41433f4d34698e0fefe2f66e87102ee1506` | `04a7a5f6bd891c1e976a5c6d3faaa15456b06f859d63d361edda3c76c3b44e7f` |

이 세 파일은 append-only `0013 → 0014 → 0015` chain으로 보존한다. registry lifecycle `event-0013/0014/0015`, 다른 attempt/successor 번호, `frozen_predecessor_inputs/**/0013.bin`~`0015.bin`은 이 chain이 아니다. 향후 compiler identity 보정은 위 세 파일을 수정하지 않고 `g5_compiler_identity_successor_0016.json` 이상의 successor로만 추가한다.

current-route recurring execution denominator는 다음 read-only listing으로 고정한다.

```powershell
uv run python .\Iris\_docs\round3\round3_run_contract_tests.py --class current --list
```

| Denominator | S0 | Target | Hard cap |
|---|---:|---:|---:|
| Current-route regular pytest identity | **103** | ≤103 | 111 |
| canonical full gate의 required standalone validation | **4** | 4 | 4 |
| recurring execution unit | **107** | ≤107 | 115 |

`recurring execution unit`은 listing에 나타나는 regular current-route pytest identity와 canonical full gate가 각 required standalone validation을 정확히 한 번 실행하는 수의 합이다. parameterized named case, `subTest` constituent assertion, migration-only one-off script, external census script, reviewer-only check와 regular authority에 등록되지 않은 temporary validation은 identity 분모에 포함하지 않는다. 2026-08-27 read-only 재측정에서 listing은 exit `0`, 103행이었고 LF-normalized stdout SHA-256은 `3406301be19d3cf5c1491b450b90938cf68371d7284a4d8e7ce61bd7917b9b95`였다.

구현자는 W0 시작 시 위 exact command로 plan carrier commit/tree, product/code S0 ancestry, clean worktree, current authority manifest, 세 exact G5 file의 path/blob/SHA/schema/chain 관계, 세 denominator와 result digest를 다시 기록한다. G5 chain의 path·blob·SHA가 위 표와 다르거나 plan carrier가 product/code S0의 documentation-only child가 아니면 조용히 수치를 덮어쓰지 않고 `BLOCKED`로 닫는다. 계획 carrier와 implementation subject는 끝까지 별도 identity로 유지한다.

### 2.2 Measured source baseline

| Surface | Baseline |
|---|---:|
| current root `Iris/tooling/src/iris_tooling/build/**` | 34 Python files |
| predecessor root `Iris/build/description/v2/tools/build/**` | 264 Python files |
| current/predecessor same-basename intersections | 32 |
| non-implementation `__init__.py` intersection | 1 |
| concrete substantive same-name implementation pairs | **33** |
| known exact/diverged implementation pairs | 5 / 28 |
| same full-gate seed producer invocations | **6** |

pair denominator는 위 두 exact root에서 `*.py`를 재귀 열거해 root-relative path와 basename을 함께 기록한다. distinct basename intersection은 32지만 predecessor root에 같은 basename의 추가 concrete path가 2개 있으므로 concrete match는 34이고, `34 concrete matches - __init__.py 1 = 33 substantive implementation pairs`다. 현재 root를 `iris_tooling` 전체로 확장하지 않는다. 33은 same-name seed denominator이며, 이름이 다른 live duplicate는 별도 content/import/consumer census로 찾고 같은 disposition 규칙을 적용한다.

### 2.3 Included

- installed `iris_tooling`의 execution/result/phase/IO/digest/path/process core
- supported public `PhaseRunner` input/output, current build-domain public payload, validation adapter payload와 CLI machine-result projection
- failure/issue/artifact projection과 canonical/volatile result 분리
- current regular validation과 clean-checkout orchestration의 typed projection
- 동일 gate 내부 immutable seed 재사용
- repeated file load, redundant subprocess, same-semantics helper 통합
- 33 concrete same-name pair와 이름이 다른 live predecessor/current duplicate의 disposition 및 안전한 physical retirement
- current command surface와 Python/PowerShell/pytest 책임 정리
- `docs/IRIS_CURRENT.md`, `Iris/AGENTS.md`, static machine route index
- exact current allowlist와 historical opt-in search route
- existing external result root의 run-local immutable result/evidence와 그 compact locator metadata

### 2.4 Explicitly out of scope

- stateful cross-run receipt ledger, lock/CAS, mutable head, `latest_attempt`, `latest_applicable_pass`, pointer recovery, backup/restore protocol
- Wiki/Browser layout, scrolling, responsive UI, Lua runtime 변경과 manual in-game matrix
- fact, Evidence, Source, Outcome, classification 또는 semantic authority 변경
- runtime Python/JVM/Mixin 도입
- content-fingerprint incremental build
- 모든 대형 Python 파일의 전면 분해
- Iris 밖의 Pulse/Echo/Fuse/Nerve/Frame/Canvas/Cortex 정리
- `_docs` 전체 삭제 또는 historical receipt 재작성
- repository-wide `dict`/JSON 제거, 모든 private helper의 dataclass 전환, 모든 `print`의 event 전환, event bus/logging framework와 새로운 reporting authority
- historical payload migration과 별도 documentation census validator의 regular authority 등록
- release, Workshop, Publish, RTC, freeze readiness 승인
- 실제 telemetry 없는 PZ 성능 또는 실제 token 절감률 주장

Wiki/Browser 개선은 별도 1차 UI 최적화 문제로 다룬다. stateful receipt ledger는 current workflow에서 실제 필요성과 비용이 입증되기 전까지 도입하지 않는다.

---

## 3. Non-Goals

이 계획은 Iris 전체 제품 또는 UI 최적화 프로그램을 닫지 않는다. build·validation execution과 current-authority 탐색의 반복·중복·모호성을 줄이는 데 집중하며 다음을 목표로 삼지 않는다.

- runtime FPS·메모리·Lua presentation 성능 개선
- Wiki/Browser UX 또는 manual in-game acceptance 완료
- 모든 historical tooling/document를 current 구조로 migration
- 범용 workflow engine, event bus, stateful receipt database 설계
- 테스트 수 자체를 줄이기 위해 독립 failure/isolation semantics를 희생
- comparable telemetry 없이 wall-clock·token 개선률을 수치화

---

## 4. Assumptions

아래 ownership과 boundary는 구현 중에도 유지해야 하는 repository/authority assumptions이자 non-negotiable architecture decisions이다.

### 4.1 Ownership

```text
iris_tooling
  → typed execution primitives
  → canonical CLI projection

Iris/validation
  → validation membership
  → required contract
  → semantic verdict
  → clean-checkout applicability/evidence rules
```

canonical CLI의 `validate full`은 existing receipt-bound launcher를 호출하는 adapter다. membership, phase list, verdict 또는 applicability를 복제해 새 authority가 되어서는 안 된다.

### 4.2 Result boundary

- `PhaseInput[TDomain]` / `PhaseOutput[TDomain]` 또는 동등 typed contract: supported public phase I/O와 generic phase input/output 관계를 고정한다. domain payload의 field와 verdict는 build/validation domain owner가 소유한다.
- `CanonicalSemanticResult`: version/discriminator, terminal status, typed domain payload, ordered `Issue`, `ArtifactRef`와 deterministic identity만 포함하는 semantic comparator 대상이다.
- `ExecutionEnvelope`: run id, elapsed, timestamp, process/environment observation, path와 canonical result digest를 갖는 volatile artifact다.
- `Issue`: 최소 `code`, `message`, `phase`, `severity`, concrete failure identity를 보존한다.
- `ArtifactRef`: 최소 `role`, `locator`, digest identity를 보존하며 locator의 volatile path와 canonical content identity를 구분한다.
- CLI machine result: canonical result/envelope reference를 exit code와 stdout의 stable machine projection으로 내보낸다. human progress와 diagnostic/traceback은 machine result와 분리해 stderr에 둔다.
- `NOT_APPLICABLE`: evidence-bearing phase/probe 상태에서만 허용
- top-level validation status: `PASS | FAIL | BLOCKED`

legacy public dict/JSON consumer에는 명시적 encode/decode adapter를 둘 수 있으나 typed contract가 canonical owner다. unknown payload version 또는 discriminator는 generic `BLOCKED`나 빈 payload로 축약하지 않고 fail-loud한다. exception/traceback은 concrete failure identity를 가진 `Issue`로 투영한 뒤 exit code와 연결하며, 원인을 빈 문자열이나 generic `BLOCKED` orchestration failure로 삼키지 않는다.

volatile field를 serializer에서 임의로 삭제해 결정성을 만드는 방식은 금지한다. canonical과 volatile schema/artifact를 처음부터 분리한다. repository-wide dict 제거, 모든 내부 helper의 typed 전환, 전역 event/logging framework는 이 계약의 완료조건이 아니다.

### 4.3 Thin PhaseRunner

`PhaseRunner`는 다음만 소유한다.

- dependency ordering
- run-local immutable reuse
- phase metric
- issue/artifact association
- concrete failure identity 전달

generation lifecycle, semantic authority, current-generation pointer, cross-run cache, domain verdict는 소유하지 않는다.

### 4.4 Current readpoint

- human/AI canonical readpoint: `docs/IRIS_CURRENT.md`
- Iris-scoped agent bootstrap: `Iris/AGENTS.md`
- machine projection: `Iris/_docs/authority/iris_current_route_index.json`
- human command literal owner: `Iris/build/ENTRYPOINTS.md`

root `AGENTS.md`는 새로 만들지 않는다. `Iris/AGENTS.md`는 별도 authority가 아니라 `Philosophy.md`와 `docs/IRIS_CURRENT.md`로 보내는 짧은 bootstrap이다.

route index는 static navigation projection이다. authority reference, producer, validator, artifact, explicit receipt locator/query contract만 포함하며 mutable latest state나 독자적인 semantic content를 소유하지 않는다.

current-facing documentation census는 다음 surface로만 제한한다.

- `docs/IRIS_CURRENT.md`
- `Iris/AGENTS.md`
- `Iris/build/ENTRYPOINTS.md`
- current authority manifest와 current route index
- canonical launcher/current command를 직접 설명하는 문서
- default AI discovery에서 자동 노출되는 Iris 문서

각 문서는 `canonical_owner`, `link_only_projection`, `historical_only`, `retain_distinct` 중 하나로 disposition한다. `retain_distinct`에는 owner와 semantic difference가 모두 필요하다. `_docs` 전체, archived receipt, reproduction evidence, external reviewer raw, historical amendment 원문과 non-Iris 문서는 분모에서 제외한다. 단, `_docs/round3` 전체를 blanket exclusion하지 않고 exact current allowlist에 속하는 current-facing 문서는 분모에 포함한다.

### 4.5 Receipt handling

- 각 실행의 immutable result/receipt와 실패 evidence는 기존 external result root에 보존한다.
- W0는 result root에 대해 owner, allocator/launcher, 명시적으로 공급되는 locator/argument, repository descendant 아님, source checkout descendant 아님, exact commit, exact tree, attempt/result locator, tracked source mutation 금지를 compact metadata로 결속한다.
- current readpoint는 explicit terminal receipt locator와 조회 방법을 제공할 수 있다.
- receipt 탐색은 read-only/on-demand이며 validation의 선행조건이 아니다.
- mutable latest pointer, ledger writer, lock/CAS, sequence reconciliation을 이번 계획에서 만들지 않는다.
- missing/stale receipt는 해당 historical/navigation claim만 제한하며 semantic validation 결과를 재작성하지 않는다.

### 4.6 Compiler identity

current owner는 `Iris/tooling/src/iris_tooling/build/naturalization_compiler_identity.py`다. predecessor의 9-path identity는 current authority가 아니다.

execution core 변경이 current compiler production closure bytes를 실제로 바꾸는 경우에만 append-only `0016+` identity successor를 만든다. 변화가 없으면 compact `no_identity_change` evidence만 남긴다.

required closure는 first-party production reachability를 기준으로 module-level import와 정적으로 해석 가능한 lazy import를 추적한다. identity owner 자체를 반드시 포함한다. dependency 추가·제거 시 old/new ordered set, removed paths와 survivor ordinal mapping을 successor에 기록한다.

---

## 5. Repository Areas Affected

### Code

- `Iris/tooling/src/iris_tooling/__main__.py`
- `Iris/tooling/src/iris_tooling/build/**`
- `Iris/tooling/src/iris_tooling/domains/**`의 supported public build/validation/CLI adapters
- `Iris/tooling/tests/**`와 affected current-route test families
- `Iris/validation/clean_checkout/**`
- `Iris/build/description/v2/tools/build/**`의 current duplicate retirement 대상
- `Iris/build/description/v2/tests/**`의 affected guards/families

### Docs

- `docs/IRIS_CURRENT.md` — 신규 canonical human/AI readpoint
- `Iris/AGENTS.md` — 신규 Iris-scoped bootstrap
- `Iris/build/ENTRYPOINTS.md` — human command literal owner
- canonical launcher/current command를 직접 설명하거나 default AI discovery에 노출되는 Iris 문서
- 이 implementation plan과 compact closeout summary

### Config

- `Iris/tooling/pyproject.toml` — CLI/package surface가 변할 때만
- `Iris/validation/clean_checkout/contracts/*.json`의 affected result/orchestration contracts
- `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json` 및 append-only successor binding
- `Iris/_docs/authority/iris_current_route_index.json` — 신규 static navigation projection

### Generated Artifacts

- external W0 execution/document census와 self-check output
- external additive predecessor archive, all-entry hash manifest와 representative restore evidence
- external run-local immutable result/receipt/failure evidence
- tracked compact baseline, before/after counts, disposition summary와 stable external locator

stateful ledger, mutable latest/head와 backup/restore store는 affected surface에 포함하지 않는다.

---

## 6. Planned Changes

### 6.1 Optimization adoption threshold

후보가 아래 중 하나 이상을 만족하면 안전성 검토 후 구현 대상으로 채택한다.

- full gate 기준 subprocess 또는 producer invocation 1회 이상 감소
- 동일 immutable input의 repeated read 2회 이상 감소
- full gate 기준 read/write volume 64 KiB 이상 감소
- current authority hop, orchestration owner 또는 human command literal owner 1개 이상 감소
- current/predecessor live implementation copy 1개 이상 제거

어느 기준도 만족하지 않는 미세 변경은 측정과 안전성 근거가 있으면 `below_materiality_threshold`로 제외할 수 있다. 단순히 시간이 부족하다는 이유의 defer는 허용하지 않는다.

### 6.2 Terminal disposition

모든 W0 후보는 다음 중 하나의 stable disposition을 가진다.

- `adopt_and_implement`
- `merge_into_current_owner`
- `retire_predecessor_copy`
- `retain_distinct_semantics`
- `retain_isolation_boundary`
- `retain_protected_reproduction`
- `below_materiality_threshold`
- `out_of_scope_external`

각 retention에는 owner, distinct semantics 또는 isolation 이유, current consumer, 측정값이 필요하다. terminal closeout은 다음을 모두 `0`으로 요구한다.

```text
unsupported_retention
remaining_eligible_optimization
unimplemented_optimization
unmeasured_defer
undispositioned_candidate
```

### 6.3 Repository and validation growth ceilings

- Current-route regular pytest identity: `103 → ≤103`, hard cap `111`. 새 계약이 필요하면 먼저 같은 producer/oracle의 기존 identity를 병합해 순증가 `0`을 맞춘다.
- hard cap의 `+8`은 별도 fresh process, mutation workspace, 독립 failure boundary 또는 독립 oracle 때문에 기존 identity에 병합할 수 없는 경우에만 사용한다. 단순 가독성, 파일별 대칭성 또는 구현 편의는 근거가 아니다.
- standalone validation: `4 → 4`, 신규 금지
- 전체 recurring execution unit: `107 → ≤107`, hard cap `115`
- 새 test는 기존 family에 table-driven case 또는 named subtest로 우선 편입
- 같은 setup, producer와 oracle을 반복하는 기존 affected tests는 constituent assertion 이름을 보존한 채 한 family로 병합
- migration-only 검사 스크립트/fixture/result는 regular authority 등록 금지
- `docs/IRIS_CURRENT.md`: 최대 300 lines, 24 KiB
- static route index: 최대 64 KiB
- repository-local optimization overhead: S0 대비 최대 2 MiB
- raw W0 ledger, archive payload, 실행 receipt, reviewer raw output은 external custody에 두고 tracked tree에는 compact summary와 stable locator만 둔다.

상한을 넘기려면 계획을 멈추고 사용자 승인을 받아야 한다. 테스트나 문서가 구현 감소분을 상쇄하도록 무제한 추가하지 않는다.

---

### 6.4 Four-Wave Execution Strategy

네 implementation wave만 사용한다. wave마다 별도 대형 census, 전체 gate, 독립 reviewer를 반복하지 않는다.

### Change 0 — Wave 0: Read-only denominator and decision freeze

#### Work

1. plan carrier와 clean implementation worktree를 고정한다. carrier가 product/code S0의 documentation-only child인지, implementation branch가 carrier를 조상으로 갖는지, main의 dirty content가 worktree에 섞이지 않았는지 확인한다.
2. exact S0와 dirty scope를 고정한다. §2.1의 exact listing command, product S0 commit/tree, plan carrier commit/tree, current authority bytes와 normalized result digest를 같은 baseline row에 결속한다.
3. execution/reporting inventory는 다음 supported current public boundary로만 제한해 한 번 census한다.
   - supported public `PhaseRunner` input/output
   - current build-domain public payload
   - validation adapter payload
   - CLI machine-result projection
   - failure/`Issue`/`ArtifactRef` projection
4. optimization candidate는 다음만 한 번 census한다.
   - 두 live StageRunner consumer graph와 seed producer call graph
   - exact 두 source root의 33 concrete same-name pairs
   - 이름이 다른 duplicate implementation의 content/import/consumer 관계
   - same-semantics IO/digest/path/process helper
   - repeated file read와 redundant subprocess
   - current predecessor import/path/subprocess/embedded-command reference
5. current-facing documentation은 §4.4의 exact surface만 census하고 각 파일에 `canonical_owner`, `link_only_projection`, `historical_only`, `retain_distinct`를 부여한다.
6. before 수치로 human command literal owner 수, current authority explanation owner 수, authority→producer→validator→receipt 최대 hop, default AI current-context file 수와 tracked bytes를 기록한다.
7. 각 후보에 stable ID, before cost, safety boundary와 terminal disposition을 부여한다.
8. current naturalization compiler closure와 identity change 가능성을 분류한다. §2.1의 exact G5 chain 외 동일 번호 artifact를 chain input으로 사용하지 않는다.
9. external result/archive root의 compact custody metadata를 고정한다. 최소 항목은 owner, allocator/launcher, explicit locator/argument, repository/source-checkout 비하위 경로 증명, exact commit/tree, attempt/result locator와 tracked source mutation 금지다.
10. 기존 clean-checkout receipt 또는 launcher timing evidence가 exact command·subject·environment 관점에서 비교 가능하면 terminal 예상 시간의 근거로 기록하고, comparable evidence가 없으면 예상치를 확정 수치로 만들지 않는다.
11. W0 실제 경과시간과 Wave 1~3 selected candidate의 implementation/focused-validation 예상 비용을 한 번 산정한다. 이 값은 정밀 성능 예측이 아니라 전체 W0+Wave 1~3 구간이 120분 예산 안에서 bounded execution 가능한지 판정하는 admission input이다.

#### Storage

- raw census와 scripts: external temporary result root
- raw documentation census, archive payload와 reviewer raw: external custody
- tracked output: compact counts, hashes, selected candidate/disposition map, result/archive locator와 terminal summary만
- one-off census script를 `Iris/validation`이나 required manifest에 등록하지 않는다.

#### Gate

- read-only listing, census self-check, schema parse, digest와 baseline binding만 실행
- pytest execution, required standalone execution, package build, clean Run A/B와 full gate를 실행하지 않음
- S0 exact current authority binding이 lightweighting terminal과 일치하면 baseline full validation을 재실행하지 않고 기존 PASS를 baseline evidence로 재사용

#### Implementation admission gate

W0의 마지막 gate는 implementation 착수 여부만 판정한다.

```text
plan carrier valid
+ clean isolated worktree
+ exact G5 chain match
+ no unresolved custody/root ambiguity
+ elapsed W0 + projected Wave 1~3 implementation/focused-validation <= 120 minutes
→ ADMIT
```

120분을 초과할 것으로 예상되거나 candidate cost를 bounded하게 산정할 수 없으면 Wave 1을 시작하지 않는다. 먼저 candidate를 별도 successor로 분할하거나 materiality denominator를 owner review로 다시 고정하고 계획을 수정한다. 구현을 시작한 뒤 예산을 소진하고 `partial`로 끝내는 방식을 기본 경로로 사용하지 않는다. 이 admission 판정은 새 정규 validator나 full gate를 만들거나 실행하지 않는다.

### Change 1 — Wave 1: Combined execution-core optimization

기존 초안의 typed result, PhaseRunner, seed reuse, helper consolidation을 하나의 combined wave로 구현한다. 변경마다 테스트하지 않는다.

#### Work

1. supported public phase I/O에 generic input/output 관계가 드러나는 typed contract를 도입한다. 구체 build/validation payload는 각 domain owner에 둔다.
2. `CanonicalSemanticResult`, `ExecutionEnvelope`, `Issue`, `ArtifactRef`를 current tooling core에 도입하고 canonical/volatile field를 schema와 artifact 수준에서 분리한다.
3. public build/validation boundary를 typed result로 전환하되, 필요한 legacy dict/JSON consumer에는 explicit adapter를 제공한다.
4. CLI adapter는 existing machine-result/exit 의미를 보존하고 human progress/diagnostic/traceback을 stdout machine projection과 분리한다.
5. 두 live StageRunner를 thin `PhaseRunner` 또는 domain adapter로 수렴한다.
6. unknown version/discriminator와 exception을 concrete `Issue` 및 exit projection으로 fail-loud하게 전달한다.
7. clean-checkout seed를 staging에서 3 producer로 한 번 생성하고 completeness/digest 검증 후 immutable final seed로 publish한다.
8. pytest와 standalone consumer는 각자 case-local clone을 사용한다.
9. W0에서 materiality threshold를 넘긴 repeated read, digest/path/process/subprocess helper를 current owner에 병합한다.
10. compiler production closure bytes가 변했는지 검사하고 필요할 때만 §2.1과 같은 G5 namespace에 `g5_compiler_identity_successor_0016.json` 이상의 successor를 만든다.

#### Required preservation

- fresh-process와 A/B independence
- tamper/mutation case isolation
- raw, canonical JSON, LF-normalized text, ordered universe digest의 의미 분리
- traceback, concrete failure identity와 exit projection
- unknown typed payload의 fail-loud 처리와 legacy adapter semantic parity
- machine stdout과 human progress/diagnostic stderr의 분리
- validation membership과 semantic verdict ownership

#### Focused validation checkpoint 1

Wave 1 완료 뒤 다음 affected families를 한 번의 bounded batch로 실행한다.

1. execution contract matrix
2. PhaseRunner ordering/failure/reuse matrix
3. seed publish/share/isolation matrix
4. helper byte-parity/digest/path/process matrix

execution contract matrix에는 최소한 typed payload encode/decode, legacy adapter parity, unknown version failure, `Issue`/`ArtifactRef` roundtrip, exception→issue→exit, stdout/stderr split과 volatile exclusion named case를 포함한다. 새 case는 네 family 안에 parameterize/named subtest로 편입하며 regular pytest identity delta 목표는 `0`이다. 각 component 변경 직후의 개별 pytest 실행은 금지한다.

### Change 2 — Wave 2: Current/predecessor physical cutover

#### Work

1. 33 concrete same-name pair와 W0에서 확인한 이름이 다른 duplicate의 current consumer migration을 끝낸다.
2. predecessor-only reproduction/historical fixture가 있으면 neutral fixture identity와 explicit retention reason으로 분리한다.
3. 삭제 대상 exact bytes를 additive external archive에 create하고 archive manifest의 모든 entry에 대해 path/size/digest를 검증한다.
4. 실제 restore 대상은 정확히 한 개를 고른다. 선택 우선순위는 `(1) physical retirement 대상, (2) diverged pair, (3) archived bytes가 가장 큰 항목`이며, 결과적으로 삭제 대상 중 가장 큰 diverged pair를 대표로 복구한다. 우선순위에 해당하는 항목이 없을 때만 다음 조건으로 내려간다.
5. 대표 한 항목을 격리된 외부 restore root에 실제 복구하고 manifest digest와 byte identity를 다시 확인한다. 나머지는 manifest/hash verification으로 충분하며 반복 restore하지 않는다.
6. current import, dynamic import, path execution, subprocess literal, package shadowing reference를 0으로 만든다.
7. predecessor current-authority copy를 physical retirement한다.

#### Focused validation checkpoint 2

다음만 한 번 실행한다.

- archive create/verify/representative restore
- current import/package resolution guard
- predecessor static/dynamic/embedded reference guard
- affected current build entrypoint smoke matrix

full Run A/B와 repository-wide pytest는 실행하지 않는다.

### Change 3 — Wave 3: Canonical command and current readpoint

#### Work

1. `iris-tooling build|validate|inspect|install`을 기존 authority의 typed adapter로 정리한다.
2. PowerShell wrapper는 environment/launcher boundary만 남기고 phase membership과 verdict를 재구현하지 않게 한다.
3. human command literal을 `Iris/build/ENTRYPOINTS.md` 한 곳으로 수렴한다.
4. projection 문서는 command/authority 의미를 재서술하지 않고 canonical owner에 대한 link-only projection으로 만든다.
5. `docs/IRIS_CURRENT.md`에 current route와 role link만 compact하게 기록한다.
6. `Iris/AGENTS.md`에 `Philosophy.md → IRIS_CURRENT.md` 진입 링크를 둔다.
7. static route index에 authority/producer/validator/artifact/explicit receipt locator/query contract를 기록한다.
8. superseded command/amendment는 `historical_only` locator로 이동시키되 접근 경로를 끊지 않고, stale current authority 설명은 제거한다.
9. default search는 exact current allowlist를 유지한다. `_docs/round3` 전체를 blanket-hidden 처리하지 않으며, current allowlist 밖 historical path만 explicit opt-in route로 분리한다.
10. `retain_distinct` 문서는 owner와 semantic difference가 없는 한 canonical owner 또는 link-only/historical projection으로 수렴한다.
11. terminal compact summary에 human command literal owner count, authority→producer→validator→receipt 최대 hop, default current-context file count와 tracked bytes의 before/after를 기록한다. raw census는 external custody에 남기고 tracked tree에는 summary와 stable locator만 둔다.

Wave 3의 document/context terminal disposition은 다음 네 값이 모두 `0`이어야 한다.

```text
undispositioned_current_document_duplicate = 0
duplicate_human_command_literal = 0
stale_current_authority_description = 0
unsupported_document_retention = 0
```

#### Focused validation checkpoint 3

다음을 한 번의 batch로 실행한다.

- canonical CLI/legacy alias parity와 exit projection
- machine-result stdout / human progress·diagnostic stderr 분리
- validation-authority non-duplication contract
- route index schema, path existence와 hop count
- `IRIS_CURRENT.md`/`ENTRYPOINTS.md` literal ownership guard
- current-facing documentation stale/duplicate/disposition guard
- exact current allowlist/historical opt-in search guard
- installed wheel arbitrary-CWD smoke if CLI package bytes changed

문서 census는 위 batch의 named cases와 compact comparison으로 검증하며 새 standalone validator나 regular registration을 만들지 않는다. stateful receipt recovery, Lua syntax와 in-game UI test는 실행하지 않는다.

### Change 4 — Wave 4: Single terminal validation and closeout

#### Precondition

Wave 0 disposition과 Wave 1~3 implementation이 모두 닫힌 뒤에만 실행한다. terminal 전에 소스·contract를 계속 수정할 예정이면 full validation을 시작하지 않는다.

#### Terminal subject and environment-authority sequence

Wave 1~3의 source/test/contract 변경을 먼저 하나의 clean **package-source implementation commit**으로 고정한다. 그 commit과 tree에서만 wheel을 external wheel root에 생성한다.

```powershell
uv build --wheel --out-dir <external-wheel-root> .\Iris\tooling
```

새 external virtual environment를 만들고 위 exact wheel과 lock이 요구하는 package set을 설치한다. 기존 `responsibility_refactor_environment_current.json`이 가리키는 과거 `c2b9514f...` environment/wheel을 새 package subject의 terminal evidence로 재사용하지 않는다.

환경 receipt와 tracked authority successor는 target external environment의 Python으로 기존 writer를 정확히 한 번 실행해 만든다.

```powershell
$previousPythonNoUserSite = [Environment]::GetEnvironmentVariable('PYTHONNOUSERSITE', 'Process')
$previousPythonPath = [Environment]::GetEnvironmentVariable('PYTHONPATH', 'Process')
try {
  $env:PYTHONNOUSERSITE = '1'
  Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue

  <external-environment-root>\Scripts\python.exe -B -s `
    .\Iris\validation\clean_checkout\write_environment_receipt.py `
    --environment-root <external-environment-root> `
    --project .\Iris\tooling\pyproject.toml `
    --lock .\Iris\tooling\uv.lock `
    --wheel <external-wheel-root>\iris_tooling-0.1.0-py3-none-any.whl `
    --source-commit <package-source-implementation-commit> `
    --source-tree <package-source-implementation-tree> `
    --out <external-environment-receipt-root>\environment_receipt.json `
    --authority-record-out .\Iris\validation\clean_checkout\authority\responsibility_refactor_environment_build_validation_optimization_<short-commit>.json `
    --current-locator-out .\Iris\validation\clean_checkout\authority\responsibility_refactor_environment_current.json
  if ($LASTEXITCODE -ne 0) { throw 'environment receipt writer failed' }
}
finally {
  if ($null -eq $previousPythonNoUserSite) {
    Remove-Item Env:PYTHONNOUSERSITE -ErrorAction SilentlyContinue
  } else {
    $env:PYTHONNOUSERSITE = $previousPythonNoUserSite
  }
  if ($null -eq $previousPythonPath) {
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
  } else {
    $env:PYTHONPATH = $previousPythonPath
  }
}
```

writer는 package-source implementation commit에서 clean 상태로 시작해야 하며 receipt/manifest는 external에, versioned authority record와 current locator만 tracked output으로 만든다. 이 두 tracked file만 commit한 **machine-validation environment subject**를 생성한다. package source tree는 package-source implementation commit과 동일해야 하며 environment subject는 그 commit의 direct documentation/authority child여야 한다.

terminal identity 순서는 다음과 같다.

```text
package-source implementation commit/tree
→ exact external wheel
→ fresh external environment + immutable receipt
→ versioned environment authority record + current locator
→ machine-validation environment subject
→ receipt-bound Run A
→ receipt-bound Run B
→ deterministic comparator
→ independent review
→ optional documentation-only closeout carrier
```

Run A/B의 canonical launcher는 `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`, comparator는 `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`다. W0는 두 script의 S0 Git blob과 mandatory parameter contract를 기록하고 Wave 4는 변경된 exact subject의 blob을 다시 기록한다. 다른 ad hoc Python invocation을 canonical terminal로 대체하지 않는다.

Run A와 Run B는 같은 immutable environment receipt와 machine-validation subject를 사용하되 서로 다른 `WorkRoot`, `ResultRoot`, `OrchestrationReceipt`를 사용한다. comparator는 두 orchestration receipt와 별도 external `AttemptRoot`를 받는다. `ClaimId`, `Commit`, `EnvironmentReceipt`, execution context와 repository root는 세 invocation에서 일치해야 한다. 모든 work/result/attempt path는 repository와 source checkout 밖이어야 한다.

#### Machine terminal

machine-validation environment subject에서 정확히 한 번 다음 묶음을 실행한다.

1. exact package-source wheel/install/environment receipt verification
2. clean-checkout Run A
3. clean-checkout Run B
4. deterministic semantic comparator
5. tracked-tree/external mutation check

Run A/B는 기존 current canonical launcher와 required standalone 4개를 그대로 사용한다. 별도의 세 번째 full run, reordered full run, full tooling pytest 또는 historical replay를 추가하지 않는다.

#### Rerun rule

- environment/launcher 문제로 implementation이 실행되지 않았다면 원인을 고친 뒤 failed leg만 재실행할 수 있다.
- implementation source, schema, test contract, package wheel, environment authority record/locator 또는 canonical result가 수정되면 package-source/environment subject chain을 새 exact identity로 다시 만들고 final A/B/comparator 묶음을 한 번 다시 실행한다.
- docs-only carrier, unchanged subject, receipt formatting 변경 때문에 machine terminal을 재실행하지 않는다.
- 동일 실패를 이유 없이 반복 실행하지 않는다.

#### Independent review

독립 Reviewer는 최종 implementation terminal에 대해 한 번만 수행한다. per-wave reviewer는 두지 않는다. Reviewer는 모든 W0 candidate와 retention/defer/no-op을 검토하며 다음을 요구한다.

- actionable finding: 0
- unsupported claim: 0
- unsupported retention: 0
- unimplemented eligible optimization: 0
- product/runtime/Lua mutation: 0

Reviewer correction이 implementation을 바꾸면 affected focused batch와 terminal rerun rule을 적용한다. 문서 문구만 고친 경우 테스트를 다시 실행하지 않는다.

---

## 7. Validation Plan

### 7.1 Automated Validation and Maximum Planned Checkpoints

| Checkpoint | Scope | Full gate |
|---|---|---:|
| W0 | census self-check/schema parse | 0 |
| Wave 1 | execution/phase/seed/helper affected batch | 0 |
| Wave 2 | archive/reference/import/entrypoint affected batch | 0 |
| Wave 3 | CLI/readpoint/route affected batch | 0 |
| Wave 4 | package + clean Run A/B + comparator | **1 묶음** |

최대 중간 focused validation은 3회다. 구현자가 내부 변경 단위마다 A/B 또는 전체 pytest를 반복하는 것은 계획 위반이다.

### 7.2 Recurring Test Design

새로운 정규 검증이 필요하면 아래 8개 family 안에서 해결한다.

1. execution contract matrix
2. PhaseRunner matrix
3. seed sharing/isolation matrix
4. helper byte-parity matrix
5. CLI parity matrix
6. route index/readpoint matrix
7. predecessor reference guard
8. terminal integration contract

가능한 경우 새 pytest function을 만들지 않고 기존 identity에 parameterized named case를 추가한다. 같은 producer/setup/oracle을 공유하는 기존 affected identity도 이 wave에서 병합한다. 서로 다른 fresh process, mutation workspace 또는 독립 oracle이 필요한 경우에만 별도 identity를 허용한다.

### 7.3 Manual Validation

이 계획 범위에 mandatory manual validation은 없다. build/validation command와 current-authority navigation은 automated contract, path existence, exact allowlist와 machine terminal로 검증한다. Wiki/Browser/Lua presentation과 manual in-game UI matrix는 별도 UI 계획의 validation이며 이 closeout을 차단하지 않는다.

### 7.4 Validation Limits and Time/Usage Stop Rules

- W0 + Wave 1~3 implementation + focused checkpoint 자동화 wall-clock 목표: 90분 이내
- 이 구현 구간이 120분을 넘을 것으로 예상되거나 실제로 넘으면 현재 command를 계속 기다리거나 반복하지 않고 중단하고 wave/batch를 재구조화한다.
- 먼저 줄일 대상은 duplicate full run, per-component test, historical replay, raw tracked ledger, 동일 census 재실행, unchanged package 재검증과 per-wave reviewer다.
- semantic contract, seed isolation, compiler identity gate, archive 전체-entry verification과 대표 restore, predecessor reference guard, final A/B independence는 시간 절약을 이유로 제거하지 않는다.
- Wave 4 terminal budget은 구현 예산과 분리해 실제 package/Run A/Run B/comparator 시간을 각각 기록한다. historical timing은 exact command·subject·environment가 비교 가능한 경우에만 비교한다.
- timeout 또는 외부 환경 blocker로 terminal이 끝나지 않으면 반복 실행으로 예산을 소진하지 않고 `implemented_only` 또는 `blocked`로 닫는다.
- docs-only carrier 변경은 exact implementation subject를 바꾸지 않으므로 terminal 재실행 사유가 아니다.
- real blocker 또는 사용자 대기 시간은 자동화 wall-clock 예산에서 분리해 기록한다.

### 7.5 Claims Allowed

측정할 수 있는 다음 항목만 before/after로 주장한다.

- producer/subprocess/read invocation 수
- bytes read/written when instrumented
- execution/orchestration owner 수
- command literal owner 수
- current authority hop 수
- live duplicate implementation 수/bytes
- regular pytest/standalone/execution unit 수
- tracked context bytes와 추가 문서/검증 overhead

wall-clock 속도와 실제 GPT/Codex token 효율은 comparable telemetry가 없으면 주장하지 않는다.

---

### 7.6 Quantitative Completion Gates

| Metric | Baseline | Required terminal |
|---|---:|---:|
| same full-gate seed producer invocation | 6 | 3 |
| concrete same-name implementation pairs | 33 | 0 live authority duplicates |
| different-name live duplicates | W0 | 0 or supported distinct identity |
| predecessor current import/execution references | W0 | 0 |
| supported public execution boundary typed coverage | W0 | 100% |
| undispositioned candidates | W0 | 0 |
| unsupported retention | W0 | 0 |
| remaining eligible optimization | W0 | 0 |
| unimplemented optimization | W0 | 0 |
| unmeasured defer | W0 | 0 |
| human command literal owners | W0 exact count | 1 canonical owner |
| current authority explanation owners | W0 exact count | 1 canonical owner; others link-only/historical |
| undispositioned current document duplicate | W0 | 0 |
| duplicate human command literal | W0 | 0 |
| stale current authority description | W0 | 0 |
| unsupported document retention | W0 | 0 |
| default AI current-context file count | W0 | terminal exact count, no unsupported file |
| default AI current-context tracked bytes | W0 | terminal exact bytes, S0 이하 또는 supported increase |
| static machine route indexes | absent/partial | 1 |
| authority→producer→validator→receipt max hop | W0 exact count | ≤2 |
| Current-route regular pytest identity | **103** | 목표 ≤103; hard cap 111 |
| standalone validations | 4 | 4 |
| recurring execution units | **107** | 목표 ≤107; hard cap 115 |
| validation-caused tracked mutations | S0 | 0 |
| Lua/product runtime changes | S0 | 0 |

`complete`는 숫자를 억지로 맞추기 위해 독립적인 failure/isolation contract를 병합하거나 지울 권한을 주지 않는다. 보존이 필요하면 explicit distinct identity와 evidence를 남기되 unsupported retention은 0이어야 한다.

---

## 8. Risk Surface Touch

### Authority Surface

Current build/validation command projection, current source/import ownership, validation result contract와 static route index를 변경한다. semantic facts, validation membership, applicability, verdict owner와 current-generation pointer는 변경하지 않는다.

### Runtime Behavior Surface

PZ runtime과 Lua behavior는 건드리지 않는다. offline producer 수, phase orchestration, failure projection과 external evidence placement만 변경한다.

### Compatibility Surface

Supported current CLI와 legacy public dict/JSON adapter의 exit/result parity를 보존한다. predecessor current-authority import/path execution은 제거하지만 protected reproduction fixture는 explicit distinct identity로 보존한다. 보편적인 외부 모드 compatibility는 검증하거나 주장하지 않는다.

### Sealed Artifact Surface

§2.1의 세 exact G5 successor 0013·0014·0015는 immutable하게 유지한다. compiler production closure bytes가 바뀔 때만 exact G5 namespace에 0016+ successor를 추가한다. retirement bytes는 external additive archive에 봉인하고 모든 entry hash와 대표 restore를 검증한다.

### Public-Facing Output Surface

CLI machine stdout, human diagnostic stderr, `docs/IRIS_CURRENT.md`, `Iris/AGENTS.md`, `Iris/build/ENTRYPOINTS.md`와 static route index가 바뀐다. Wiki/Browser/Lua presentation은 바뀌지 않는다.

---

## 9. Risk Analysis

### Authority confusion

Risk: installed CLI가 validation membership/verdict를 복제해 새 authority가 될 수 있다.

Mitigation: CLI는 authority-owned launcher adapter만 사용하고 parity/non-duplication contract로 고정한다.

### God core

Risk: common execution core가 domain 판단과 lifecycle을 흡수할 수 있다.

Mitigation: immutable types, protocol, runner, serialization만 core에 두고 domain payload/verdict는 domain owner에 남긴다.

### False determinism

Risk: volatile observation이 canonical bytes에 섞일 수 있다.

Mitigation: canonical result와 execution envelope를 다른 type/schema/artifact로 만들고 comparator는 canonical digest만 비교한다.

### Reporting contract scope creep

Risk: typed public boundary 작업이 repository-wide payload migration, event bus 또는 새 reporting authority로 팽창할 수 있다.

Mitigation: W0 inventory와 Wave 1 completion을 supported public phase/build/validation/CLI/issue/artifact projection으로 제한하고 legacy adapter를 허용한다. unknown version과 exception failure identity만 fail-loud contract로 강제한다.

### Unsafe reuse

Risk: `6 → 3` seed sharing이 mutation isolation과 A/B independence를 약화할 수 있다.

Mitigation: staging completeness/digest 검사 후 immutable publish하고 consumer마다 case-local clone을 사용한다.

### Incorrect helper merge

Risk: newline, ordering, digest semantics, fresh-process boundary가 다른 helper를 이름만 보고 합칠 수 있다.

Mitigation: W0 semantic classification과 old/new byte parity를 통과한 material candidate만 병합한다.

### Predecessor deletion

Risk: hidden import/path execution 또는 reproduction consumer가 남을 수 있다.

Mitigation: static/dynamic/embedded reference guard, package resolution guard와 additive archive/representative restore를 삭제 전에 완료한다.

### Documentation denominator drift

Risk: `_docs` 전체를 중복으로 세거나 blanket-hidden 처리해 current evidence를 잃고, 반대로 historical 문서를 current owner로 오인할 수 있다.

Mitigation: §4.4 exact census surface와 4개 disposition을 사용하고 current allowlist만 default discovery에 남긴다. raw census는 external custody, tracked tree에는 compact before/after와 locator만 둔다.

### External evidence ambiguity

Risk: result/archive root가 checkout 내부이거나 allocator와 exact subject가 불명확해 validation이 source를 오염시키거나 evidence 귀속이 흔들릴 수 있다.

Mitigation: W0에서 owner, allocator, explicit locator, repository/source-checkout 비하위 경로, commit/tree와 attempt/result locator를 결속하고 tracked source mutation을 terminal에서 0으로 검증한다. mutable latest나 stateful ledger는 추가하지 않는다.

### Environment-authority subject drift

Risk: 과거 wheel/environment receipt를 새 tooling source에 재사용하거나 package-source commit, environment locator commit과 machine-validation commit을 하나의 모호한 subject로 기록할 수 있다.

Mitigation: Wave 4의 package-source → exact wheel → fresh environment receipt → versioned authority/current locator → machine-validation subject 순서를 지킨다. Run A/B/comparator는 같은 machine-validation subject와 environment receipt를 사용하고 서로 다른 external run roots를 사용한다.

### Test overgrowth

Risk: 최적화보다 검증기·raw census·문서가 더 커지고 실행 시간이 증가할 수 있다.

Mitigation: identity/bytes/time ceiling, table-driven family, 외부 raw evidence, 최종 full gate 1회 원칙을 적용한다.

---

## 10. Rollback Plan

1. Wave 1은 domain adapter 단위로 되돌릴 수 있어야 한다. actual compiler identity successor가 생긴 wave를 되돌릴 때는 기존 receipt를 수정하지 않고 rollback successor를 추가한다.
2. shared seed 전환 실패 시 이전 두 materialization call을 복구하되 실패한 staging/final identity를 재사용하지 않는다.
3. predecessor retirement는 verified archive의 explicit restore로 exact paths를 복구한 뒤 import/reference guard를 다시 실행한다.
4. CLI cutover는 확인된 compatibility consumer가 있을 때만 alias를 한 wave 복구한다. typed internal API는 유지한다.
5. environment authority correction을 되돌릴 때 기존 versioned record와 external receipt를 삭제하지 않는다. package-source commit에 맞는 새 rollback environment record/current locator successor를 만들고 새 machine-validation subject에서 terminal을 다시 수행한다.
6. append-only execution receipt와 failure evidence는 rollback 중에도 삭제하거나 덮어쓰지 않는다.
7. current-generation pointer, semantic payload와 Lua runtime은 이 계획의 rollback 대상이 아니다.

---

## 11. Governance Constraints

- `docs/Philosophy.md` 준수
- Iris PZ runtime 100% Lua 유지
- runtime/build-time separation 유지
- `offline generation → stateless validation → immutable install → pointer switch` 유지
- PhaseRunner, result schema, CLI와 route index는 semantic authority 또는 current pointer가 아님
- current source/import/command owner를 predecessor path로 우회하지 않음
- fresh-process, determinism A/B와 case-local mutation isolation 유지
- raw/canonical/LF-normalized/ordered-universe digest 의미 분리
- exact-subject PASS만 주장하고 predecessor PASS를 새 subject에 상속하지 않음
- §2.1의 exact G5 0013·0014·0015를 수정하지 않고 필요 시 같은 G5 namespace에 0016+ successor만 추가
- plan carrier, package-source implementation, machine-validation environment subject와 documentation-only closeout carrier의 identity를 혼합하지 않음
- one-off analysis/validator를 regular authority로 승격하지 않음
- current exact allowlist를 blanket historical exclusion으로 훼손하지 않음
- release/readiness/외부 모드 보편 compatibility를 이 계획의 완료 claim에 포함하지 않음

---

## 12. Expected Closeout State

Expected closeout name: `Iris build-validation execution/current-authority optimization: complete`

다음을 모두 만족할 때만 `complete`를 사용한다.

- Wave 0의 모든 후보가 terminal disposition됨
- tracked plan carrier가 product/code S0의 documentation-only child이고 implementation이 그 carrier의 clean isolated worktree에서 수행됨
- W0 implementation admission gate가 `ADMIT`이며 120분 초과 예측을 무시하고 Wave 1에 진입하지 않음
- materiality와 safety를 충족한 모든 eligible optimization이 실제 구현됨
- typed result, thin PhaseRunner와 canonical CLI가 기존 authority/failure 의미를 보존함
- seed producer가 `6 → 3`으로 감소하고 consumer isolation과 A/B independence가 유지됨
- live current/predecessor authority duplicate와 current predecessor reference가 0임
- current readpoint와 static route index가 1~2 jump navigation을 제공함
- current-facing document duplicate, duplicate human command literal, stale current authority description와 unsupported document retention이 모두 0임
- human command owner, authority explanation owner, max hop, default current-context file/bytes의 exact before/after가 compact summary에 기록됨
- external result/archive evidence가 explicit owner/allocator/locator와 exact commit/tree에 결속되고 tracked source mutation이 없음
- exact package-source wheel, fresh external environment receipt, versioned environment authority/current locator와 machine-validation subject가 Wave 4 순서대로 결속됨
- growth ceiling과 test/time budget을 준수함
- 최종 package + receipt-bound clean Run A/B + comparator가 exact machine-validation environment subject에서 exit 0임
- independent Reviewer actionable finding이 0임
- tracked/runtime/Lua forbidden mutation이 0임
- 실제로 측정하지 않은 wall-clock/token/runtime 개선을 주장하지 않음

구현이 끝났지만 final terminal 또는 Reviewer가 끝나지 않았으면 `implemented_only`, 일부 eligible implementation이 남으면 `partial`, 외부 선행조건으로 진행할 수 없으면 `blocked`다. 분석·inventory·문서만 완성한 상태를 `complete`로 닫을 수 없다.

closeout에는 다음 비주장 문구를 그대로 포함한다.

> 이 closeout은 Iris build·validation execution 및 current-authority 탐색 최적화에만 귀속된다.  
> Wiki/Browser presentation 및 Lua UI 최적화의 완료를 주장하지 않는다.

또한 runtime performance/FPS, 실제 token 절감, release·Workshop·Publish·RTC readiness, 외부 모드 보편 compatibility와 stateful cross-run receipt ledger의 완성을 주장하지 않는다.
