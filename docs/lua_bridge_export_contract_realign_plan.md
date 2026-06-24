# Implementation Plan

> 상태: planned / scope-lock candidate / WARN review revisions applied / PASS minor revisions applied
> 작성일: 2026-06-15
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Roadmap input: `C:/Users/MW/.codex/attachments/f442a5fe-078e-44e3-a78c-3acb389b75fa/pasted-text.txt` / sha256 `8B578F9D0FD236F38B8E8DDBC4F4C638C34F288E2E772394DBDB164C4228F93` / unsealed AI-assisted roadmap reference, preserved only as drafting input
> Review input: `C:/Users/MW/.codex/attachments/45b680bf-38cc-4339-95db-156a285079fc/pasted-text.txt` / sha256 `6B3C4C1B65453B04D3E39C16D8835C2FE0AC6823121E536B736A0E84195E879D` / WARN review reference
> Review input rev.2: `C:/Users/MW/.codex/attachments/36a38a96-d3d7-4959-936d-c2cffd3bf3d8/pasted-text.txt` / sha256 `691E623D91F36533CCC9E36774E4B66B19FFB9FD2D844AA51CC1FB06478DCD01` / PASS with minor revisions reference

---

## 1. Objective

DVF 3-3 Lua bridge exporter의 default build-time contract를 monolith 중심에서 chunk manifest + chunk files 중심으로 재정렬한다.

현재 문제는 runtime 결함이 아니라 `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`의 default export contract drift다. runtime deployable authority는 이미 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` manifest와 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua` chunk files로 읽히지만, exporter default는 여전히 `IrisLayer3Data.lua` monolith를 먼저 생성하고 chunk export를 opt-in으로 둔다.

이번 계획의 목표는 다음 상태를 만드는 것이다.

* exporter default 실행은 chunk manifest + chunk files format을 생성한다.
* bare default invocation의 `bridge_context`, output root, protected-path rejection behavior를 먼저 pin한다.
* monolith `IrisLayer3Data.lua` 생성은 default/current route에서 제거한다.
* monolith 생성은 explicit `diagnostic` 또는 `historical` route에서만 허용한다.
* package와 workspace-copy 경로는 monolith deployable 재유입을 fail-loud로 차단한다.
* bridge report와 current test contract는 chunk manifest + chunk files를 primary bridge output으로 보고한다.
* runtime payload, facts, decisions, rendered content, quality/publish/runtime state는 변경하지 않는다.

판정 기준은 다음으로 고정한다.

* deployable runtime authority 자체는 변경하지 않는다.
* live frozen chunk payload를 교체하지 않는다.
* successor baseline identity를 봉인하지 않는다.
* build-time bridge export/report authority framing은 monolith 중심에서 chunk 중심으로 변경한다.
* default chunk output은 live deployable path 직접 생성이나 current authority promotion이 아니라, chunk format default + deployable landing guard + no auto-promotion으로 읽는다.
* approved cutover-class context는 이번 라운드에서 도입하거나 실행하지 않는다. live deployable chunk path write는 chunk든 monolith든 이번 라운드에서 항상 fail-loud 대상이다.

---

## 2. Scope

이 계획의 intended modification scope는 다음으로 제한한다.

* Lua bridge export surface inventory와 scope lock
* bare default invocation의 `bridge_context`와 default output root pin
* exporter mode/context contract 도입
* output format과 output location/context 분리
* default export format을 monolith에서 chunk manifest + chunk files로 전환
* live deployable chunk manifest + chunk dir write fail-loud guard 추가
* current/deployable context에서 monolith output 금지
* live monolith present/absent disposition branch 봉인
* diagnostic / historical monolith route 격리
* package preflight/postflight monolith guard 추가
* workspace-copy surface disposition 작성 및, executable surface가 있을 때만 source/destination monolith guard 추가
* chunk manifest/chunk file integrity, determinism, no-orphan validation
* bridge report primary fields를 chunk authority framing으로 전환
* current / historical / diagnostic test routes 분리
* sealed vNext Phase 5 invocation disposition을 frozen-historical 또는 additive supersession artifact로 기록
* roadmap input provenance를 versioned staging artifact로 보존
* protected surface no-mutation verdict와 closeout evidence packet 작성

### Explicitly Out Of Scope

* DVF 3-3 successor baseline cutover
* live 2105 chunk payload replacement
* source manifest reconstruction completion
* facts / decisions / rendered content rewrite
* current 6-entry fixture promotion
* canonical rendered promotion
* body-plan v2 redesign
* compose contract reopen
* consumer migration execution
* runtime Lua loader full redesign
* runtime JSON parser introduction
* Browser / Wiki / Tooltip behavior change
* quality_state / publish_state / runtime_state policy change
* `adopted / unadopted` vocabulary change
* legacy `active / silent` current vocabulary revival
* Layer4 / ACQ_DOMINANT / Acquisition Lexical / Structural Signal reopen
* release packaging completion claim
* Workshop / B42 / deployment readiness claim
* manual in-game QA completion claim
* monolith historical trace deletion
* chunk format / manifest schema / chunk count redesign
* verified current code defect를 근거로 manifest schema나 chunk count를 이 라운드 안에서 고치는 것. 그런 결함이 발견되면 STOP + 별도 승인 계획으로 라우팅한다.

---

## 3. Non-Goals

* DVF 3-3 본문 품질을 개선하지 않는다.
* semantic quality, publish policy, runtime state를 재판정하지 않는다.
* runtime에서 compose, repair, source validation, semantic quality judgment를 수행하게 만들지 않는다.
* package pass를 release readiness로 읽지 않는다.
* staging chunk output을 current deployable authority로 승격하지 않는다.
* old chunks와 successor chunks를 동시에 current로 두지 않는다.
* package-only monolith exclusion을 exporter default contract 해결로 과대 해석하지 않는다.
* historical / diagnostic monolith reproduction route를 파괴하지 않는다.
* full historical artifact byte reproducibility를 닫으려 하지 않는다.

---

## 4. Assumptions

* 최상위 헌법 기준은 `docs/Philosophy.md`다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 Iris DVF 3-3 current readpoint를 따른다.
* current deployable runtime authority는 `IrisLayer3DataChunks.lua` manifest와 `IrisLayer3DataChunks/*.lua` chunk files다.
* `IrisLayer3Data.lua` monolith는 current deployable authority가 아니며, 이번 라운드 이후 default/current export output도 아니다.
* `export_dvf_3_3_lua_bridge.py`는 rendered output을 Lua runtime 소비 표면으로 넘기는 build-time export 경로다.
* 현재 exporter는 default로 `--lua-output-path`를 live monolith path로 두고, `--chunk-output-dir`, `--chunk-manifest-path`, `--chunk-size`가 주어질 때 chunk export를 수행한다.
* 목표 default CLI contract는 다음으로 pin한다.
  * bare default invocation의 default `bridge_context`는 `staging`이다.
  * bare default invocation의 default input rendered path는 `Iris/build/description/v2/output/dvf_3_3_rendered.json`이다.
  * bare default invocation의 default output root는 `Iris/build/description/v2/staging/lua_bridge_export/default/`다.
  * default chunk manifest path는 `Iris/build/description/v2/staging/lua_bridge_export/default/IrisLayer3DataChunks.lua`다.
  * default chunk dir는 `Iris/build/description/v2/staging/lua_bridge_export/default/IrisLayer3DataChunks/`다.
  * default route는 live deployable path, package path, or current-looking path로 resolve되면 실행 전 fail-loud한다.
  * default invocation contract must record `default_input_rendered_path`, `input_scale`, and `input_authority_status`.
* path classification은 filename 또는 basename heuristic이 아니라 resolved absolute path comparison으로 수행한다.
* live deployable chunk manifest `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`와 live deployable chunk dir `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/`는 protected destination set에 포함한다.
* current checkout 기준 `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`는 absent다. 실행 Phase 0은 이 absence를 다시 증명해야 하며, present로 바뀐 경우 closeout branch가 달라진다.
* package script `Iris/tools/package_iris.ps1`는 현재 package output에서 `media/lua/client/Iris/Data/IrisLayer3Data.lua`를 제거하지만, source/current path monolith intrusion을 fail-loud로 막는 계약은 아직 아니다.
* workspace-copy 경로는 repo 조사 후 확정한다. 명시적 copy script가 없으면 실제 copy-like path와 package output path를 inventory하고 guard 적용 가능 범위를 분리한다.
* workspace-copy closeout은 Phase 0의 `workspace_copy_surface_disposition`에 종속된다. executable surface가 없으면 guard PASS를 주장하지 않고 `manual_only_no_executable_surface` 또는 `not_found_no_surface` limitation으로 닫는다. `unknown_blocked`이면 PASS closeout은 금지된다.
* vNext Phase 5 staging evidence는 current cutover가 아니며 직접 rewrite하지 않는다. 이 계획은 existing Phase 5 old invocation을 `frozen_historical_reference`로 읽고, 새 CLI shape가 필요하면 `vnext_phase5_additive_supersession.md`에 equivalent explicit non-current invocation을 기록한다. Old command를 as-is preserved로 주장하지 않는다.
* current facts / decisions / rendered / live runtime payload / packaged Lua / bridge-runtime payload는 protected no-mutation set에 포함한다.
* compatibility alias는 old option spelling을 chunk-default route에 매핑하는 alias만 허용한다. Monolith default semantics를 되살리는 alias는 금지한다.
* PowerShell package validation은 local execution environment에서 `powershell` 또는 Windows PowerShell이 resolve될 때만 PASS/FAIL을 주장한다. tool missing이면 validation blocked로 기록한다.
* dirty working tree에는 이 계획과 무관한 변경이 많으므로, 실행 시 intended files만 stage / commit 대상으로 삼는다.

---

## 5. Repository Areas Affected

### Code

* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/tools/package_iris.ps1`
* workspace-copy related scripts, if inventory finds them
* optional guard/validator tooling under `Iris/build/description/v2/tools/build/`, if exporter/package scripts cannot host the checks cleanly

### Tests

* `Iris/build/description/v2/tests/test_*.py` files that currently exercise `export_dvf_3_3_lua_bridge.py`
* new focused test file for Lua bridge export contract realignment, if clearer
* package/workspace-copy guard tests, if existing test structure supports them

### Docs

* `docs/lua_bridge_export_contract_realign_plan.md`
* `docs/lua_bridge_export_contract_realign_closeout.md` after execution
* `docs/lua_bridge_export_contract_realign_decisions_packet.md` as staging draft, if ledger reflection is needed
* `docs/lua_bridge_export_contract_realign_roadmap_packet.md` as staging draft, if roadmap reflection is needed

### Config

* None expected.
* Test discovery config must not be changed unless current route tests cannot be included through existing routes.

### Generated Artifacts

All generated evidence for this round should stay under:

* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/`

Expected evidence artifacts:

* `export_surface_inventory.json`
* `monolith_occurrence_disposition.jsonl`
* `live_monolith_disposition.json`
* `workspace_copy_surface_disposition.json`
* `protected_bridge_output_paths.json`
* `protected_surface_hashes.before.json`
* `bridge_export_mode_context_matrix.md`
* `default_invocation_contract.json`
* `roadmap_input_provenance.json`
* `vnext_phase5_invocation_disposition.md`
* `forbidden_claim_scan_policy.json`
* `bridge_export_report.json`
* `chunk_integrity_report.json`
* `chunk_determinism_report.json`
* `package_monolith_guard_report.json`
* `workspace_copy_monolith_guard_report.json`
* `protected_surface_hashes.after.json`
* `protected_surface_hash_diff.json`
* `no_mutation_verdict.json`
* `final_contract_report.json`
* `ledger_update_packet.md` if needed

---

## 6. Planned Changes

### Change 1 - Export Surface Inventory and Scope Lock

Purpose:

Lua bridge export, package, workspace-copy, tests, docs에서 monolith 또는 chunk output을 current-relevant surface로 다루는 모든 경로를 inventory하고 protected mutation boundary를 먼저 고정한다.

Files:

* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/tools/package_iris.ps1`
* `Iris/build/description/v2/tests/test_*.py`
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` read-only reference
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/*`

Implementation Notes:

* `export_lua_bridge()`, `write_chunked_lua_bridge()`, `write_chunked_lua_bridge_from_monolith()`, CLI args, default constants, report writer를 inventory한다.
* monolith `IrisLayer3Data.lua` occurrence를 `current-forbidden`, `diagnostic`, `historical`, `archive`, `docs-predecessor`, `runtime-log-evidence`, `unknown`으로 분류한다.
* package script의 copy, exclusion, clean behavior를 source/package/temp output별로 분류한다.
* live monolith disposition branch를 작성한다.
  * `live_monolith_absent`: Phase 0에서 absence를 증명하고 package preflight는 future intrusion만 fail-loud 처리한다. 이 branch는 `changed_count == 0` closeout이 가능하다.
  * `live_monolith_present`: closeout은 `partial` 또는 `blocked_live_monolith_present`로 닫는다. 별도 승인된 quarantine/removal action이 scope에 추가된 경우에만 `no unexpected mutation + approved forbidden monolith removal/quarantine` verdict로 재정의할 수 있다.
* workspace-copy surface disposition을 작성한다. 허용 상태는 `guarded_script_found`, `copy_like_package_path_guarded`, `manual_only_no_executable_surface`, `not_found_no_surface`, `unknown_blocked`다.
* workspace-copy path가 별도 script인지 manual validation path인지 확인한다. executable surface가 없으면 guard PASS가 아니라 disposition evidence와 validation limit로 기록한다.
* protected current bridge output set을 닫는다. 최소 포함 대상은 live chunk manifest, live chunk files, live monolith path, current rendered output, canonical facts/decisions, package output equivalent path다.
* live deployable chunk path는 manifest와 chunk directory 전체를 resolved absolute path로 보호한다. Chunk write와 monolith write 모두 approved cutover-class context 밖에서는 fail-loud 대상이다.
* Phase 0은 mutation 없이 inventory와 before hash만 남긴다.
* Roadmap input은 unsealed AI-assisted drafting reference로 provenance를 남기고, durable staging artifact `roadmap_input_provenance.json`에 hash/path/source-status를 기록한다.
* `default_invocation_contract.json`은 최소한 `bridge_context`, `default_input_rendered_path`, `default_output_root`, `default_chunk_manifest_path`, `default_chunk_dir`, `input_scale`, `input_authority_status`를 기록한다.
* `input_authority_status`는 `fixture_non_authority`, `full_authority_input`, `staging_candidate`, 또는 `unknown_blocked` 중 하나로 기록한다. `unknown_blocked`이면 default contract PASS closeout은 금지된다.
* `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/PLAN_TEMPLATE.md`, `docs/EXECUTION_CONTRACT.md` path resolve를 확인한다.

Validation:

* `rg` 기반 occurrence inventory가 exporter, package, tests, docs, runtime data, package output references를 포함한다.
* unresolved / unknown occurrence가 0이 되거나, unknown이 blocked row로 명시된다.
* protected path list가 live/runtime path와 staging path를 구분한다.
* live monolith branch is recorded as absent, present, or blocked.
* workspace-copy disposition is not `unknown_blocked` for PASS closeout.
* default invocation contract records context, input rendered path, input scale, input authority status, output root, manifest path, and chunk dir.
* default input authority status is not `unknown_blocked`.
* docs governance paths resolve.
* mutation performed false가 기록된다.

---

### Change 2 - Export Mode / Context Contract and Deployable-Landing Guard

Purpose:

default flip 전에 output format과 output context를 분리하고, monolith 또는 unlisted current-equivalent output이 deployable/current-looking path에 착지하지 못하게 한다.

Files:

* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* focused bridge export contract tests
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/bridge_export_mode_context_matrix.md`

Implementation Notes:

* bridge context를 명시한다: `staging`, `historical`, `diagnostic`. `current` 또는 `cutover` class context는 이번 라운드에서 실행 가능한 writer context로 도입하지 않는다.
* bare default invocation은 `bridge_context = staging`으로 pin한다.
* bare default output root는 `Iris/build/description/v2/staging/lua_bridge_export/default/`로 pin한다.
* output format을 명시한다: `chunk`, `monolith`.
* current/deployable-equivalent path에서는 monolith format과 chunk format 모두 hard fail한다.
* bare default invocation uses the pinned default staging output root and does not require caller-provided output path flags.
* explicit staging invocation requires caller-provided staging output root.
* historical / diagnostic context에서만 monolith output을 허용한다.
* monolith output path가 live runtime data path, package path, current-looking path로 resolve되면 hard fail한다.
* chunk manifest path 또는 chunk dir가 live deployable chunk path로 resolve되면 hard fail한다.
* guard classification은 `Path.resolve()` / absolute normalized path set comparison으로 수행한다. Filename, basename, suffix, or substring-only heuristic is not sufficient.
* direct function call도 CLI guard를 우회하지 못하게 shared guard를 writer boundary 안에 둔다.
* CLI help와 error message는 format/location/context를 구분해 설명한다.
* 기존 `--chunk-output-dir` / `--chunk-manifest-path` 옵션은 default chunk route와 호환되도록 alias 또는 explicit override로 정리한다.
* Allowed compatibility alias:
  * old chunk option spelling mapping to explicit staging chunk output.
  * explicit historical/diagnostic monolith mode for reproduction.
* Forbidden compatibility alias:
  * no-arg or default path alias that writes monolith.
  * alias that maps default chunk output to live runtime chunk paths.
  * alias that silently downgrades a protected-path failure to diagnostic output.

Validation:

* unsupported `--bridge-context current` is rejected, if provided.
* current/deployable-equivalent destination + monolith format is fail-loud.
* bare default invocation resolves to the pinned non-deployable staging output root.
* explicit staging invocation + live runtime path is fail-loud.
* staging/default chunk manifest or chunk dir resolving to live deployable path is fail-loud.
* historical / diagnostic context + explicit non-current monolith path pass.
* direct `export_lua_bridge()` call and CLI call pass through the same guard.
* rejected calls do not create monolith, manifest, chunk, report, or partial output in protected paths.

---

### Change 3 - Default Format Flip: Monolith to Chunk

Purpose:

Exporter default route가 chunk manifest + chunk files를 생성하도록 전환한다. 이 전환은 live deployable payload replacement나 current authority promotion을 의미하지 않는다.

Files:

* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* bridge export contract tests
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/chunk_integrity_report.json`
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/chunk_determinism_report.json`

Implementation Notes:

* default route에서 monolith write를 제거한다.
* default route는 pinned default output root 아래의 chunk manifest path와 chunk output dir을 resolved default로 갖는다.
* no-arg 또는 최소-arg CLI default invocation은 explicit staging command와 별도 validation case로 둔다.
* default route가 live path로 resolve되면 guard가 실행 전에 막아야 한다.
* manifest file과 chunk files는 하나의 authority unit으로 다룬다.
* chunk ordering, chunk naming, serialization order, newline/encoding policy를 deterministic하게 고정한다.
* Serialization policy is UTF-8 without BOM, LF newlines, sorted entry keys, deterministic chunk size, deterministic chunk filenames `ChunkNNN.lua`, and no environment-dependent absolute paths inside chunk content except in diagnostic reports.
* Bridge report records `input_scale` as `fixture`, `full`, or `unknown`. A 6-entry rendered input must be reported as `input_scale = fixture` and must not be described as authority-scale output.
* Bridge report records `input_authority_status` and must mark default 6-entry fixture input as `fixture_non_authority` when applicable.
* stale chunk cleanup은 protected/live path에서는 금지하고 staging/temp output에서만 허용한다.
* manifest references, orphan chunk, duplicate key, missing chunk, manifest mismatch를 hard fail한다.
* partial write 방지를 위해 temp directory staging 후 commit하거나 final guard pass 전에는 어떤 protected write도 하지 않는다.
* manifest schema or chunk count mismatch is a STOP condition for a separate approved plan, not an in-scope redesign escape hatch.

Validation:

* bare default invocation writes chunk manifest + chunk files under the pinned non-deployable default output root.
* explicit staging invocation writes chunk manifest + chunk files under its explicit non-current output root.
* default invocation does not write `IrisLayer3Data.lua`.
* default/current chunk output resolving to live deployable chunk manifest or chunk dir fails loud.
* same input produces same manifest hash.
* same input produces same per-chunk hashes.
* manifest references all chunks.
* no orphan chunks.
* duplicate key and missing chunk fixtures fail.
* protected-surface no-mutation verdict remains PASS.

---

### Change 4 - Monolith Diagnostic / Historical Quarantine

Purpose:

Monolith generation을 current/default export path에서 제거하되, 필요한 historical reproduction과 diagnostic inspection은 명시적 non-current route로 보존한다.

Files:

* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* bridge export contract tests
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/monolith_occurrence_disposition.jsonl`

Implementation Notes:

* monolith generation command는 explicit `--bridge-context diagnostic --format monolith` 또는 `--bridge-context historical --format monolith` 같은 non-current route로만 허용한다.
* monolith filename과 output root가 current runtime file처럼 보이지 않게 제한한다.
* live runtime data directory나 package workspace에 `IrisLayer3Data.lua`를 쓰는 경로는 hard fail한다.
* diagnostic report에는 `non_current = true`, `authority_kind = diagnostic_monolith` 같은 marker를 남긴다.
* historical reproduction test는 별도 historical route에서만 실행한다.
* monolith diagnostic output과 chunk authority report는 같은 primary report로 섞지 않는다.

Validation:

* diagnostic monolith explicit path pass.
* historical monolith explicit path pass.
* current monolith path hard fail.
* package/workspace monolith path hard fail.
* current tests do not assert monolith existence.
* historical tests do not mutate current runtime payload.

---

### Change 5 - Package / Workspace-Copy Fail-Loud Guard

Purpose:

Package와 workspace-copy 경로에서 monolith가 조용히 제외되거나 우연히 재유입되는 상태를 없애고, current/package/deployable surface에 monolith가 감지되면 fail-loud로 중단한다.

Files:

* `Iris/tools/package_iris.ps1`
* workspace-copy related scripts, if present
* package/workspace guard tests
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/package_monolith_guard_report.json`
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/workspace_copy_monolith_guard_report.json`

Implementation Notes:

* package preflight에 source runtime path monolith intrusion check를 추가한다.
* package postflight에 package output monolith absence check를 추가한다.
* existing behavior of deleting package output monolith is no longer enough for current/source intrusion; protected source monolith must fail loud.
* Clean mode는 temp/package staging stale monolith를 정리할 수 있지만 protected source monolith를 조용히 삭제하지 않는다.
* Phase 0의 `workspace_copy_surface_disposition`이 `guarded_script_found`이면 workspace-copy script source/destination monolith guard와 negative tests가 필수다.
* disposition이 `copy_like_package_path_guarded`이면 package/copy-like path guard와 package negative tests로 닫고, 별도 workspace-copy PASS를 주장하지 않는다.
* disposition이 `manual_only_no_executable_surface` 또는 `not_found_no_surface`이면 executable guard requirement는 면제되지만 validation limit에 명시한다.
* disposition이 `unknown_blocked`이면 PASS closeout은 금지된다.
* executable workspace-copy source/destination에 monolith가 있으면 fail-loud로 중단한다.
* diagnostic/historical directory의 monolith는 current/package guard가 오탐하지 않도록 allowed root를 분리한다.
* package expected file list는 chunk manifest + chunk files 기준으로 갱신한다.

Validation:

* source runtime path monolith exists -> package fail.
* package output monolith exists after copy -> package fail.
* workspace-copy source/destination monolith exists -> fail when executable workspace-copy surface exists.
* no executable workspace-copy surface -> disposition evidence exists and closeout records limitation.
* diagnostic/historical monolith under explicit non-current root is not over-blocked.
* package zip contains chunk manifest + chunks.
* package zip does not contain `IrisLayer3Data.lua`.
* Clean mode does not silently mutate protected source.

---

### Change 6 - Bridge Report / Test Contract Migration

Purpose:

Bridge export report와 test contract를 chunk authority framing 기준으로 갱신하고, current / historical / diagnostic routes를 분리한다.

Files:

* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* bridge export tests
* package/workspace guard tests
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/bridge_export_report.json`
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/final_contract_report.json`

Implementation Notes:

* bridge report primary fields는 chunk 기준으로 전환한다.
* required fields:
  * `authority_kind`
  * `bridge_context`
  * `format`
  * `input_rendered_path`
  * `output_manifest_path`
  * `output_chunk_dir`
  * `entry_count`
  * `adopted_count`
  * `unadopted_count`
  * `chunk_count`
  * `manifest_hash`
  * `chunk_hashes`
  * `monolith_generated`
  * `non_current`
  * `input_scale`
  * `input_authority_status`
* diagnostic monolith report는 별도 report 또는 clearly subordinate section으로 격리한다.
* current route tests는 default chunk export를 검증한다.
* historical route tests는 explicit historical monolith만 검증한다.
* diagnostic route tests는 explicit diagnostic monolith만 검증한다.
* old monolith default expectation을 가진 tests는 current route에서 제거하거나 historical route로 강등한다.
* report wording은 release, package readiness, quality exposure, publish readiness, runtime rollout, current baseline replacement, live chunk replacement claim으로 표류하지 않게 factual fields 중심으로 유지한다.
* forbidden claim scan policy는 다음 literal claim families를 최소 금지 목록으로 고정한다: `release readiness`, `package readiness`, `runtime rollout`, `current baseline replacement`, `live chunk replacement`, `Browser/Wiki/Tooltip behavior change`, `quality exposure`.

Validation:

* current route passes with default chunk export.
* current route fails if monolith is generated.
* diagnostic route passes only with explicit diagnostic mode.
* historical route passes only with explicit historical mode.
* report schema validation passes.
* report has no release/quality/publish readiness wording.
* report forbidden claim scan uses the fixed forbidden claim list and passes.
* no unexpected runtime payload mutation.

---

### Change 7 - Protected No-Mutation / Regression Verdict

Purpose:

이번 라운드가 exporter/tool/report/guard contract만 바꾸고 runtime payload, source facts/decisions, rendered content, packaged Lua, bridge/runtime payload를 변경하지 않았음을 증명한다.

Files:

* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/protected_surface_hashes.before.json`
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/protected_surface_hashes.after.json`
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/protected_surface_hash_diff.json`
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/no_mutation_verdict.json`

Implementation Notes:

* protected surface before/after hash diff를 작성한다.
* `live_monolith_absent` branch에서는 `changed_count == 0`이 no-mutation PASS 조건이다.
* `live_monolith_present` branch에서는 `changed_count == 0` complete closeout을 주장하지 않는다. 별도 승인된 quarantine/removal이 없으면 closeout은 `partial` 또는 `blocked_live_monolith_present`다.
* 별도 승인된 quarantine/removal이 수행되면 verdict는 `no unexpected mutation + approved forbidden monolith removal/quarantine`으로 재정의하고, 승인 근거와 changed path를 기록한다.
* current route regression, package guard, workspace guard, negative tests 결과를 final contract report로 묶는다.
* sealed vNext Phase 5 invocation compatibility는 `frozen_historical_reference`로 기록한다. Old invocation을 as-is preserved로 주장하지 않는다.
* 새 CLI shape로 Phase 5 재현 경로가 필요하면 `vnext_phase5_additive_supersession.md`에 explicit non-current invocation, input path, output path, expected report fields, and no-current-promotion wording을 기록한다.
* compatibility alias가 old monolith default semantics를 되살리면 fail이다.

Validation:

* live monolith absent branch: protected-surface hash diff `changed_count == 0`.
* live monolith present branch: PASS closeout blocked unless approved quarantine/removal verdict exists.
* current route regression PASS.
* negative-test suite PASS.
* package/workspace guard PASS.
* no runtime payload/source mutation.
* no current baseline replacement wording.
* vNext Phase 5 disposition is `frozen_historical_reference` or additive supersession is documented with concrete artifact path.

---

### Change 8 - Closeout / Ledger Reflection Packet

Purpose:

Claim boundary를 닫고, 후속 작업자가 exporter default를 chunk runtime/package authority format과 정렬된 build-time contract로만 읽도록 closeout과 optional ledger packet을 작성한다.

Files:

* `docs/lua_bridge_export_contract_realign_closeout.md`
* `docs/lua_bridge_export_contract_realign_decisions_packet.md` optional staging draft
* `docs/lua_bridge_export_contract_realign_roadmap_packet.md` optional staging draft
* `Iris/build/description/v2/staging/lua_bridge_export_contract_realign/ledger_update_packet.md` optional

Implementation Notes:

* closeout은 `Lua bridge export default contract realigned` 범위로만 작성한다.
* optional `decisions_packet` / `roadmap_packet`은 staging draft이며 canonical `docs/DECISIONS.md` 또는 `docs/ROADMAP.md` mutation이 아니다.
* canonical ledger 반영은 별도 사용자 승인 또는 single-writer seal 후에만 수행한다.
* success wording이 release readiness, runtime rollout, current baseline replacement로 확장되지 않게 제한한다.
* "monolith 제거"는 historical trace 삭제가 아니라 current/default/deployable quarantine으로 표현한다.

Validation:

* closeout has no release readiness wording.
* closeout has no runtime rollout wording.
* closeout has no current baseline replacement wording.
* closeout has no Browser / Wiki / Tooltip behavior change wording.
* docs / tests / reports use the same chunk authority framing language.
* canonical governance docs remain unchanged unless separately approved.

---

## 7. Validation Plan

### Automated Validation

No validation may be claimed as passed unless the exact relevant command exits with code 0.

Expected commands, subject to final test file names after implementation:

* `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_lua_bridge_export_contract_realign.py"`
* `python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_*.py"` if the current route requires full local discovery
* `python -B -m pytest -q`
* `python -B Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `python -B Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py --bridge-context staging --report-path Iris/build/description/v2/staging/lua_bridge_export_contract_realign/bridge_export_report.json --chunk-output-dir Iris/build/description/v2/staging/lua_bridge_export_contract_realign/IrisLayer3DataChunks --chunk-manifest-path Iris/build/description/v2/staging/lua_bridge_export_contract_realign/IrisLayer3DataChunks.lua`
* known-bad live chunk path probe wrapped by test or validator: `python -B Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py --bridge-context staging --chunk-manifest-path Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua --chunk-output-dir Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks`
* `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip`
* PowerShell precondition check: `Get-Command powershell`
* guard/validator known-bad fixture command if separate guard tooling is introduced
* independent before/after protected hash diff command

Raw known-bad probes are expected to return non-zero. They support PASS only when executed through a test/validator that exits 0 after observing the expected fail-loud rejection and unchanged protected surfaces.

Required validation matrix:

| Case | Expected |
| --- | --- |
| no-arg CLI default route | `bridge_context = staging`, default input rendered path, input scale/status, and pinned default output root are recorded |
| no-arg CLI default route | chunk manifest + chunk files generated under non-deployable default output root |
| no-arg CLI default route | no `IrisLayer3Data.lua` generated |
| no-arg CLI default route | protected live chunk manifest and chunk dir unchanged |
| explicit staging route | chunk manifest + chunk files generated under explicit non-current output root |
| direct exporter function default route | same guard and same output contract as CLI |
| unsupported `--bridge-context current` | FAIL-LOUD |
| current/deployable-equivalent destination + monolith format | FAIL-LOUD |
| live runtime monolith output path | FAIL-LOUD |
| default or explicit chunk manifest resolving to live deployable manifest | FAIL-LOUD |
| default or explicit chunk dir resolving to live deployable chunk dir | FAIL-LOUD |
| package path monolith output path | FAIL-LOUD |
| bare default staging route without caller output flags | PASS using pinned default root |
| explicit staging invocation + explicit staging chunk output | PASS |
| historical context + explicit historical monolith output | PASS |
| diagnostic context + explicit diagnostic monolith output | PASS |
| historical / diagnostic omitted output resolving to current path | FAIL-LOUD |
| manifest references missing chunk | FAIL |
| orphan chunk exists | FAIL |
| duplicate key across chunks | FAIL |
| same input repeated | same manifest hash and chunk hashes |
| chunk serialization policy | UTF-8 without BOM, LF newlines, sorted keys |
| fixture rendered input | report records `input_scale = fixture` |
| fixture rendered input | report records `input_authority_status = fixture_non_authority` |
| full rendered input if available | report records `input_scale = full` |
| default input authority status `unknown_blocked` | PASS closeout forbidden |
| live monolith absent branch | absence evidence exists and `changed_count == 0` remains required |
| live monolith present branch | PASS closeout blocked unless approved quarantine/removal verdict exists |
| source runtime monolith detected by package preflight | FAIL |
| package output monolith detected by postflight | FAIL |
| workspace-copy disposition `guarded_script_found` | executable guard and negative test required |
| workspace-copy disposition `copy_like_package_path_guarded` | package/copy-like guard evidence required |
| workspace-copy disposition `manual_only_no_executable_surface` | limitation recorded, no guard PASS claimed |
| workspace-copy disposition `not_found_no_surface` | limitation recorded, no guard PASS claimed |
| workspace-copy disposition `unknown_blocked` | PASS closeout forbidden |
| workspace-copy destination monolith detected | FAIL when executable workspace-copy surface exists |
| diagnostic/historical monolith in explicit non-current root | not over-blocked |
| protected live chunk payload after rejected calls | unchanged |
| live deployable chunk path after rejected calls | unchanged |
| vNext Phase 5 old invocation disposition | `frozen_historical_reference` or concrete additive supersession artifact exists |
| current route regression | PASS |
| report schema | PASS |
| report forbidden claim scan | PASS |

### Manual Validation

* Review `git diff --stat` and `git diff` for intended-file-only changes.
* Inspect exporter CLI help and error messages for format/location/context clarity.
* Inspect bridge report wording for release/quality/publish/runtime cutover overclaim.
* Inspect forbidden claim scan policy and confirm the fixed claim list is used.
* Confirm monolith historical/diagnostic route is preserved rather than deleted.
* Confirm live runtime chunk manifest and chunk files are not changed.
* Confirm facts, decisions, rendered output, Browser, Tooltip, Wiki behavior are not changed.
* Confirm live monolith branch and workspace-copy surface disposition are reflected in closeout.
* Confirm roadmap input is recorded as unsealed AI-assisted drafting reference and preserved in staging provenance artifact.
* Confirm `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/PLAN_TEMPLATE.md`, and `docs/EXECUTION_CONTRACT.md` resolve in the current checkout.
* Confirm optional governance packets are staging drafts only.

### Validation Limits

* no manual in-game QA
* no multiplayer validation
* no long-session runtime validation
* no runtime cutover validation
* no deployment validation
* no Workshop publication
* no release readiness validation
* no successor baseline cutover validation
* no successor-baseline parity validation
* no semantic quality validation
* no body text quality review
* no external ecosystem compatibility sweep
* no full historical byte reproducibility proof
* no executable workspace-copy guard PASS when Phase 0 disposition is manual-only or no-surface

---

## 8. Risk Surface Touch

### Authority Surface

Touched at build-time export/report framing only.

Deployable runtime authority remains the existing chunk manifest + chunk files. The exporter/report contract changes which artifact is treated as the default bridge export output. No new output is automatically promoted to current deployable authority.

Live deployable chunk manifest and chunk directory are protected destinations. Any exporter write to those paths is fail-loud unless a future separately approved cutover-class context exists.

### Runtime Behavior Surface

None intended.

Runtime Lua loader behavior, Browser, Wiki, Tooltip, chunk manifest, chunk files, facts, decisions, and rendered content must remain unchanged.

Default exporter output must resolve to non-deployable staging/output root. If it resolves to live runtime data paths, execution is blocked before write.

### Compatibility Surface

Touched.

Any workflow that relied on default exporter execution producing `IrisLayer3Data.lua` will break in current/default mode. This is intended for current route and must be replaced by explicit historical/diagnostic monolith mode if still needed.

vNext Phase 5 old invocation is treated as frozen historical reference. If executable compatibility is required, this round records a concrete additive supersession invocation rather than claiming old-command preservation.

### Sealed Artifact Surface

Protected.

Live runtime chunk manifest, live chunk files, live monolith path if present, current facts/decisions/rendered, package output, and bridge-runtime payload are no-mutation surfaces. New evidence artifacts are additive under the round staging root.

If live monolith is present at execution time, closeout cannot be `complete` under the default no-mutation branch without a separate approved quarantine/removal verdict.

### Public-Facing Output Surface

None.

No user-facing text, tooltip, wiki panel, browser behavior, README, Workshop text, release note, or package publication claim changes in this plan.

---

## 9. Risk Analysis

### Architecture Risk

* Default chunk output may be overread as live current authority generation.
* Default route pinning may be incomplete, causing explicit staging validation to pass while true no-arg default remains unsafe.
* A CLI-only guard would leave direct function writer bypass open.
* Format and location may be conflated, allowing staging output to look current.
* Report schema could continue to present monolith as primary bridge output.
* Optional compatibility alias could accidentally revive monolith default semantics.
* Unsealed roadmap input may be overread as canonical authority unless provenance is recorded.

### Runtime Risk

* Exporter default paths currently point at live Lua data paths; omitted explicit paths may write protected files if guard is incomplete.
* Chunk-to-live write is as risky as monolith-to-live write because it can overwrite the frozen deployable chunk authority.
* Stale chunk cleanup may delete live chunks if output dir classification is wrong.
* Manifest schema or chunk count redesign could indirectly change runtime loader expectations and must stop for separate approval.
* A hidden runtime consumer of monolith may be revealed by tests. That must be treated as current contract violation or compatibility investigation, not as reason to restore monolith default.

### Compatibility Risk

* Existing scripts/tests may expect default monolith generation.
* vNext Phase 5 invocation reproduction may rely on old CLI shape.
* Package script Clean behavior may be relied on to silently remove monolith from package output.
* Historical/diagnostic monolith route may be over-blocked if allowed roots are too narrow.
* Workspace-copy may be manual-only or absent, making unconditional guard PASS impossible.

### Regression Risk

* Chunk serialization hash may vary if key order, newline policy, or stale file cleanup is unstable.
* Path separator differences may make Windows-specific validation pass while POSIX-style test fixtures fail, or vice versa.
* Negative tests may assert the right failure but still leave partial output behind.
* Report field migration may break consumers that read old monolith fields.
* Broad `rg` occurrence cleanup may accidentally mutate docs/predecessor evidence rather than only current route expectations.
* Forbidden claim scan may be meaningless if the forbidden claim list is not fixed before execution.

---

## 10. Rollback Plan

Rollback must preserve live runtime payload and protected artifacts.

* Revert exporter default flip independently from package/workspace guard if possible.
* Revert default context/output root pinning only together with the corresponding tests; do not leave no-arg default pointing at live paths.
* Revert report schema migration separately if old report consumers are broken.
* Revert or quarantine new tests if the contract needs revision.
* Keep monolith explicit historical/diagnostic route available during rollback unless it is the source of failure.
* Do not roll back by restoring monolith as current/default deployable output.
* Do not write or restore live chunk manifest/chunk files without a separate approved runtime recovery step.
* If protected surface mutation is detected, stop immediately, identify changed protected files from hash diff, and restore only those named files through explicit user-approved recovery or VCS restore.
* Discard or ignore round staging artifacts if generated evidence is incomplete or invalid.

Rollback triggers:

* current route cannot produce chunk manifest + chunk files
* current/default route still writes monolith
* bare default invocation resolves to live runtime, package, or current-looking path
* unsupported `--bridge-context current` is accepted
* current/deployable-equivalent destination accepts monolith output
* chunk output to live deployable manifest or chunk dir is accepted outside a separately approved cutover-class context
* protected live chunk payload changes unexpectedly
* stale cleanup touches live/runtime chunk files
* package/workspace guard silently deletes protected source monolith instead of failing
* live monolith present branch is detected but closeout still attempts `changed_count == 0` complete
* workspace-copy surface remains `unknown_blocked` but closeout attempts PASS
* historical/diagnostic explicit monolith route is no longer usable
* report claims release readiness, runtime rollout, or current baseline replacement

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Iris runtime/build-time separation must remain intact.
* Runtime must remain render-only and must not compose, repair, source-validate, or judge semantic quality.
* Lua bridge exporter is build-time tooling, not runtime authority promotion.
* FAIL-LOUD must be preserved for current/deployable monolith output, live deployable chunk output, protected path landing, manifest/chunk mismatch, package intrusion, and executable workspace-copy intrusion.
* Bare default invocation must not write live runtime, package, or current-looking paths.
* Path classification must use resolved absolute protected destination comparison.
* Monolith and chunks must not both be deployable authority.
* Old chunks and successor chunks must not both be current authority.
* Existing live chunks remain current deployable authority until a separate approved single-authority cutover.
* Source facts, decisions, rendered content, runtime Lua, packaged Lua, bridge/runtime payload, `quality_state`, `publish_state`, and `runtime_state` must not be mutated by this round.
* Current runtime vocabulary remains `adopted / unadopted`.
* `adopted / unadopted` must not become quality, publish, deletion, or suppression vocabulary.
* Legacy `active / silent` remains historical / diagnostic / import alias vocabulary only.
* Browser / Wiki / Tooltip must not expose quality state as badge, sorting, filtering, hiding, recommendation, trust, or confidence display.
* vNext staging evidence remains non-current unless separately promoted by approved cutover.
* vNext Phase 5 old invocation is frozen historical reference unless a concrete additive supersession artifact is written.
* Manifest schema or chunk count redesign is out of scope and requires STOP + separate approval.
* Roadmap input remains unsealed AI-assisted reference unless separately promoted into repo canon.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` must not be mutated by this execution unless separately approved.
* Optional ledger/roadmap packets are staging drafts only.
* Release readiness, Workshop readiness, B42 readiness, manual in-game validation, runtime rollout, package deployment, and public exposure are not implied.
* Minimal diff preservation applies. Do not refactor unrelated DVF, compose, runtime, or package code while realigning this contract.
* Dirty working tree safety applies. Stage only files intentionally changed for this scope.

---

## 12. Expected Closeout State

Expected closeout target: `complete` as execution-complete-and-self-validated only.

Closeout may be marked `complete` only if:

* Phase 0 records default `bridge_context`, default input rendered path, input scale/status, default output root, default manifest path, and default chunk dir.
* default input authority status is not `unknown_blocked`.
* bare default invocation resolves to the pinned non-deployable output root.
* default exporter route generates chunk manifest + chunk files.
* default exporter route does not generate `IrisLayer3Data.lua`.
* default exporter route does not write live runtime, package, or current-looking paths.
* live deployable chunk manifest and chunk dir reject exporter writes fail-loud outside any future approved cutover-class context.
* unsupported `--bridge-context current` is rejected if provided.
* current/deployable-equivalent destination rejects monolith output fail-loud.
* direct function call and CLI call share the same bridge output guard.
* monolith generation is available only through explicit historical / diagnostic route.
* historical / diagnostic monolith output cannot target current/runtime/package-looking paths.
* live monolith disposition is `live_monolith_absent`, or an approved quarantine/removal verdict replaces the default no-mutation condition.
* package guard fails loud on monolith deployable intrusion.
* workspace-copy disposition is not `unknown_blocked`.
* executable workspace-copy surface, when present, fails loud on monolith deployable intrusion.
* package output contains chunk manifest + chunks and no `IrisLayer3Data.lua`.
* bridge report primary fields are chunk-oriented and include manifest/chunk hash evidence.
* bridge report records `input_scale` and `input_authority_status`.
* current route tests validate default chunk export.
* no-arg default invocation is validated separately from explicit staging invocation.
* chunk-to-live fail-loud validation passes through a test/validator wrapper.
* historical route tests validate explicit historical monolith only.
* diagnostic route tests validate explicit diagnostic monolith only.
* live monolith absent branch: protected surface hash diff reports `changed_count == 0`.
* approved quarantine/removal branch, if separately approved: no unexpected mutation verdict records only the approved monolith disposition change.
* facts, decisions, rendered content, live runtime payload, packaged Lua, and bridge/runtime payload remain unchanged.
* vNext Phase 5 invocation disposition is recorded as `frozen_historical_reference`, or concrete additive supersession is recorded.
* forbidden claim scan uses the fixed claim list and passes.
* roadmap input provenance is recorded as unsealed AI-assisted drafting reference.
* closeout does not claim release readiness, runtime cutover, current baseline replacement, Browser/Wiki/Tooltip behavior change, or manual in-game QA.

If Phase 0 records `manual_only_no_executable_surface` or `not_found_no_surface` for workspace-copy, `complete` may be used only with an explicit validation limit that no executable workspace-copy guard PASS is claimed.

If any required validation is blocked or intentionally skipped, closeout must be `partial` or `implemented_only`, with the blocked command and reason recorded explicitly.
