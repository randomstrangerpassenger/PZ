# Implementation Plan

> 상태: planned / scope-lock candidate / WARN review revisions applied / PASS minor revisions applied
> 작성일: 2026-06-15
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Roadmap input: `C:/Users/MW/.codex/attachments/9d9cdfbd-a8ec-4fb7-956a-ca632c00cede/pasted-text.txt` / sha256 `36AEF42BED87BA4E5C290CBFDB8F41AF1C94F13DD084D7B6C217EF595A575DED` / unsealed AI-assisted roadmap reference, preserved only as drafting input
> Review input: `C:/Users/MW/.codex/attachments/ffd5dd12-66c5-4bd0-af21-ca914711f1d4/pasted-text.txt` / sha256 `E6C7D994A73E8397AE64EE58AF1EDE3466E37C3DA124DBDB58218BDE275B6AF0` / WARN final review reference
> Review input rev.2: `C:/Users/MW/.codex/attachments/61af8c14-7a72-423b-a8c2-5e40b0af7056/pasted-text.txt` / sha256 `E65171B9666E1814D07DCAB4A9663189428CF43A02856E2C52E944EEB89B8592` / PASS with minor revisions reference
> Initial checkout observation: `media/lua/shared/Iris/IrisDvfBridgeData.lua` is tracked / sha256 `C5EC93914F4A13C227BF1B3958908B860AF768113700CECB4C4496B46AD411AA` / 45 lines / 6-entry legacy-looking payload. `Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua` was not present in the initial probe.

---

## 1. Objective

`media/lua/shared/Iris/IrisDvfBridgeData.lua` 계열 current-looking DVF bridge artifact를 current DVF bridge authority로 오독되지 않도록 명시 분류하고 처분한다.

이 파일은 current-looking naming과 generated bridge header를 가진 artifact다. 실제 runtime/package/workspace-copy reachability는 아직 결론이 아니며, Phase 1-2 audit에서 root `media/`와 `Iris/media/`의 관계를 분리해 증명한다.

이번 계획의 목표는 다음 상태를 만드는 것이다.

* 대상 artifact와 duplicate / same-payload / package-output copy를 inventory한다.
* 대상 artifact를 `historical / reproduction / stale / blocked / current_candidate_requires_reconciliation` 중 하나로 evidence 기반 분류한다.
* `current`는 이번 라운드의 terminal disposition이 아니다. current consumer가 발견되면 artifact mutation 없이 별도 authority reconciliation으로 격상한다.
* current가 아닌 경우 current-looking runtime / package / workspace-copy surface에서 제거한다. 여기서 `removed`는 기본적으로 current-looking path 밖 quarantine/relocation을 뜻하며, hard delete는 별도 승인 gated step이다.
* 보존이 필요하면 파일명, 위치, manifest, header가 non-current historical 또는 reproduction fixture임을 명확히 드러내게 한다.
* current-looking old path, old filename, exact hash, payload-shape fingerprint, 6-entry legacy bridge payload가 runtime / package / workspace-copy route로 재유입되면 fail-loud 처리한다.
* current DVF bridge authority는 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`와 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`로 유지한다.
* current facts / decisions / rendered / live runtime chunks / quality state / publish state / runtime state는 변경하지 않는다.

이번 계획은 artifact disposition round다. DVF vNext generation, current runtime cutover, description quality improvement, release readiness를 열지 않는다.

---

## 2. Scope

이 계획의 intended modification scope는 다음으로 제한한다.

* exact target path와 alternate target path의 scope lock
* `IrisDvfBridgeData.lua` filename / token / payload inventory
* SHA256, line count, entry count, header, top-level export 방식 기록
* root `media/` path와 Iris module source root `Iris/media/` path의 package/runtime 의미 분리
* direct consumer, dynamic consumer candidate, global lookup, docs/test/tool references audit
* package script and package output inclusion audit
* root `media/` reachability와 package zip inclusion 결과를 closeout에서 분리 보고
* workspace-copy or copy-like route inventory
* classification adjudication
* stale artifact quarantine/relocation by default, or hard delete only after separate explicit approval
* forbidden path / filename / payload-shape / package-content / workspace-copy guard hardening
* path normalization rule for Windows path, POSIX path, zip internal path, and case-insensitive comparisons
* package output equivalence report after guard changes
* current chunk authority no-mutation seal
* `docs/EXECUTION_CONTRACT.md` pre-execution check
* post-implementation independent review gate before closeout PASS/seal
* final closeout and ledger update packet draft

### Explicitly Out Of Scope

* DVF 3-3 vNext cutover
* successor baseline identity sealing
* current runtime chunk replacement
* current rendered output promotion
* facts / decisions / rendered source authority restoration
* Lua bridge exporter default contract redesign
* monolith bridge export reintroduction
* 6-entry fixture promotion to current bridge sample
* repo-wide stale artifact sweep outside the named bridge artifact family
* source expansion / IrisData work
* Browser / Wiki / Tooltip behavior change
* public-facing text change
* semantic quality / publish_state / runtime_state policy change
* release / Workshop / deployment readiness declaration
* PZ long-session in-game QA
* multiplayer validation
* external ecosystem compatibility sweep

---

## 3. Non-Goals

* 이 계획은 `IrisDvfBridgeData.lua`를 current compatibility fallback으로 되살리지 않는다.
* hidden consumer가 발견되어도 silent shim으로 덮지 않는다.
* old path를 조용히 복구하거나 package에 계속 포함시키지 않는다.
* current chunk payload, chunk manifest, facts, decisions, rendered output을 재생성하지 않는다.
* package gate pass를 release readiness나 package-wide deployability로 읽지 않는다.
* historical / reproduction 보존을 current authority preservation으로 표현하지 않는다.
* root `media/` artifact 제거를 전체 runtime equivalence 증명으로 확대하지 않는다.
* stale artifact 하나의 처분을 DVF stale artifact 전체 정리로 확대하지 않는다.

---

## 4. Assumptions

* 최상위 헌법 기준은 `docs/Philosophy.md`다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 Iris DVF 3-3 current readpoint를 따른다.
* current deployable runtime authority는 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua` manifest와 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua` chunk files다.
* `IrisLayer3Data.lua` monolith와 6-entry legacy bridge payload는 current full runtime authority가 아니다.
* initial checkout 기준 tracked target은 `media/lua/shared/Iris/IrisDvfBridgeData.lua`다.
* initial checkout 기준 `Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua`는 존재하지 않았다. 실행 Phase 0은 이 observation을 다시 검증해야 한다.
* target file은 6-entry legacy-looking payload, `interaction-cluster-rendered-v0`, generated timestamp `2026-03-27T06:02:39.464418+00:00`를 포함한다.
* target payload fingerprint seed는 exact file SHA256 `C5EC93914F4A13C227BF1B3958908B860AF768113700CECB4C4496B46AD411AA`, `interaction-cluster-rendered-v0`, `meta.stats.total = 6`, `meta.stats.active_composed = 6`, known 6-entry key set, and `entries_sha256`이다. Phase 1 must recapture these values before using them as guard inputs.
* current package script `Iris/tools/package_iris.ps1`는 `Iris/`를 source root로 보고 `Iris/media`를 copy한다. root `media/`가 package input인지 여부는 별도 audit로 봉인해야 한다.
* current package script는 `media\lua\client\Iris\Data\IrisLayer3Data.lua` monolith를 forbidden file로 처리하지만, `IrisDvfBridgeData.lua` root/shared artifact guard는 아직 이 계획 기준에서 봉인되지 않았다.
* "direct consumer 없음"은 아직 결론이 아니다. `require`, `safeRequire`, `dofile`, `loadfile`, string-built require, global table lookup, package inclusion, tool/test fixture reference를 audit해야 한다.
* current-looking path에 artifact가 남아 있으면 filename/header 때문에 current bridge authority로 오독될 수 있다.
* historical 또는 reproduction 보존이 필요하면 current runtime/package path 밖에서만 허용한다.
* `removed`는 이 계획에서 기본적으로 "old current-looking path에서 제거되고 quarantine 또는 explicit fixture path로 relocation됨"을 뜻한다. Hard delete는 separate approval gate가 있을 때만 허용한다.
* default quarantine target is `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/quarantine/IrisDvfBridgeData.legacy_6_entry.lua`. Historical/reproduction preservation may instead use an explicit fixture path recorded in the matching manifest.
* Quarantine artifact retention policy: the quarantine artifact is staging-only generated evidence, not tracked source authority, not package/runtime material, and not a cleanable cache during the round. It must be retained through post-implementation independent review and closeout. If later cleanup removes it, the closeout must already preserve its hash, payload profile, provenance, and disposition record.
* Guard and scan path comparison must normalize Windows separators, POSIX separators, zip internal paths, relative path aliases, resolved absolute paths where applicable, and case-insensitive filesystem comparisons.
* `docs/EXECUTION_CONTRACT.md` exists in the current checkout and must be checked before execution for disclosure, evidence, and closeout obligations.
* Plan approval and closeout/seal are separate. The plan may be execution-ready, but closeout PASS/seal requires post-implementation independent review. If that review is not performed, closeout must remain `review_pending` or `seal_pending`.
* Initial checkout check found `tools/check_lua_syntax.ps1`. Execution must verify the path again before claiming Lua syntax validation; if missing, Lua syntax validation is blocked or the exact command must be adjusted and reported.
* dirty working tree에는 이 계획과 무관한 변경이 많으므로, 실행 시 intended files만 stage / commit 대상으로 삼는다.

---

## 5. Repository Areas Affected

### Code

Expected or possible touch points:

* `Iris/tools/package_iris.ps1`
* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`, read-only unless guard/report integration is needed
* optional new guard or validator under `Iris/build/description/v2/tools/build/`
* optional workspace-copy related script, only if inventory finds one

### Tests

Expected or possible touch points:

* `Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py`
* `Iris/build/description/v2/tests/test_lua_bridge_export_contract_realign.py`
* new focused test file for stale bridge artifact disposition guard, if clearer

### Docs

* `docs/stale_dvf_bridge_artifact_disposition_plan.md`
* `docs/stale_dvf_bridge_artifact_disposition_closeout.md` after execution
* `docs/stale_dvf_bridge_artifact_disposition_decisions_packet.md` as staging draft, if ledger reflection is needed
* `docs/stale_dvf_bridge_artifact_disposition_roadmap_packet.md` as staging draft, if roadmap reflection is needed

### Config

* None expected.
* Test discovery config must not be changed unless new focused tests cannot be included through existing routes.

### Generated Artifacts

All generated evidence for this round should stay under:

* `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/`

Expected evidence artifacts:

* `scope_lock_report.json`
* `artifact_inventory.json`
* `artifact_payload_profile.json`
* `payload_fingerprint_guard_policy.json`
* `duplicate_payload_inventory.jsonl`
* `consumer_audit_report.json`
* `dynamic_consumer_candidate_report.json`
* `package_inclusion_report.json`
* `path_normalization_matrix.json`
* `package_output_equivalence_report.json`
* `workspace_copy_surface_disposition.json`
* `guard_coverage_gap_report.json`
* `classification_verdict.json`
* `disposition_matrix.json`
* `historical_fixture_manifest.json`, if preserved as historical
* `reproduction_fixture_manifest.json`, if preserved as reproduction
* `mutation_report.json`
* `quarantine_retention_policy.json`, if stale quarantine/relocation is used
* `forbidden_surface_guard_report.json`
* `package_forbidden_file_scan_report.json`
* `protected_surface_hashes.before.json`
* `protected_surface_hashes.after.json`
* `protected_surface_hash_diff.json`
* `no_mutation_verdict.json`
* `final_disposition_contract_report.json`
* `ledger_update_packet.md`, required if artifact relocation, hard delete, package guard addition, workspace-copy guard addition, or authority-boundary wording change occurs; optional otherwise
* `independent_review_gate.md`

---

## 6. Planned Changes

### Change 1 - Scope Lock and Artifact Inventory

Purpose:

대상 artifact의 exact path, alternate path, duplicates, payload profile, current authority baseline을 mutation 없이 고정한다.

Files:

* `media/lua/shared/Iris/IrisDvfBridgeData.lua`
* `Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua`, expected absent but must be checked
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua`
* `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/*`

Implementation Notes:

* `git ls-files`, `rg --files`, exact path checks로 tracked status와 alternate path status를 기록한다.
* target file의 SHA256, byte count, line count, entry count, header/comment, generated timestamp, `meta.stats`, top-level return shape를 기록한다.
* same filename, exact SHA256, same `entries_sha256`, same `interaction-cluster-rendered-v0` + 6-entry stats shape, same 6-entry key set, same generated header를 repository-wide로 검색한다.
* payload-level guard seed를 `payload_fingerprint_guard_policy.json`에 기록한다. Minimum guard inputs are exact SHA256, `entries_sha256` when present, version marker, stats total/active count, and known key set.
* root `media/` artifact와 `Iris/media/` artifact를 분리한다. 이 둘을 같은 runtime/package surface로 단정하지 않는다.
* root `media/`와 `Iris/media/`의 relationship은 classification input이다. Root artifact package exclusion, package inclusion, dev-runtime reachability를 각각 별도 field로 기록한다.
* current chunk manifest/chunk files, current facts/decisions/rendered, package output equivalent path를 protected surface before hash 대상으로 기록한다.
* path normalization matrix를 작성한다. 최소 대상은 Windows `\`, POSIX `/`, zip internal `/`, relative aliases, resolved absolute paths, case-insensitive compare variants다.
* initial observation은 evidence seed일 뿐 closeout verdict가 아니다.

Validation:

* `rg --files | rg "IrisDvfBridgeData|IrisLayer3Data\.lua|IrisLayer3DataChunks\.lua"`
* `git ls-files -- media/lua/shared/Iris/IrisDvfBridgeData.lua Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua`
* raw SHA256 and line-count capture
* payload-shape fingerprint capture
* path normalization matrix capture
* protected runtime chunk baseline hash capture

---

### Change 2 - Consumer, Package, and Reachability Audit

Purpose:

대상 artifact가 runtime, package, test, tool, docs, dynamic load 후보 중 어디에서 소비되거나 포함되는지 분류한다.

Files:

* `media/lua/shared/Iris/IrisDvfBridgeData.lua`
* `Iris/tools/package_iris.ps1`
* `Iris/build/description/v2/tools/build/*.py`
* `Iris/build/description/v2/tests/*.py`
* docs and Iris docs references, read-only unless closeout packet needs updates

Implementation Notes:

* content token search와 filename search를 분리한다.
* search token은 최소 `IrisDvfBridgeData`, `DvfBridge`, `IrisDvf`, `media/lua/shared/Iris`, `interaction-cluster-rendered-v0`, six known item ids를 포함한다.
* Lua dynamic load 후보는 `require`, `safeRequire`, `dofile`, `loadfile`, `package.path`, global lookup, string concat require로 나누어 기록한다.
* string-built require 후보는 최소 `Iris`, `Dvf`, `Bridge`, `Data`, `shared`, item-id token 조합을 포함해 검색하고, static certainty가 없으면 `dynamic_candidate_unresolved`로 남긴다.
* reference classification은 다음 중 하나로 둔다.
  * `current_runtime_consumer`
  * `current_package_inclusion`
  * `current_tool_consumer`
  * `test_reproduction_consumer`
  * `historical_reference`
  * `diagnostic_reference`
  * `doc_reference`
  * `false_positive`
  * `none`
* package script가 root `media/`를 포함하지 않는 것으로 보이더라도 package output and zip content scan으로 증명한다.
* package zip scan은 old path/filename 부재뿐 아니라 normalized internal zip path, exact payload hash, payload-shape fingerprint absence를 확인한다.
* package guard 변경이 있으면 package output equivalence report를 작성한다. Equivalence means intended package roots and expected current chunk payload remain present, while forbidden stale bridge path/filename/payload are absent. It is not a full package behavior equivalence claim.
* workspace-copy surface가 없으면 `not_found_no_surface` 또는 `manual_only_no_executable_surface`로 닫고, guard PASS를 주장하지 않는다.
* consumer가 발견되면 current shim을 넣지 않고 classification escalation 후보로 기록한다.

Validation:

* repository-wide token search
* Lua load-pattern search
* package script path trace
* package output and zip content scan with normalized internal paths
* package output equivalence report, if package guard changes
* current route regression before mutation, if mutation is likely

---

### Change 3 - Classification Adjudication and Current-Consumer Escalation

Purpose:

Phase 1/2 evidence를 기준으로 target artifact를 `historical / reproduction / stale / blocked / current_candidate_requires_reconciliation` 중 하나로 판정한다. `current` is not a terminal disposition in this round.

Files:

* `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/classification_verdict.json`
* `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/disposition_matrix.json`
* optional fixture manifest, only if preserved

Implementation Notes:

* `current` terminal classification is precluded. This artifact may not be sealed as current bridge authority by this plan.
* confirmed current runtime consumer, current package consumer, or current tool consumer 발견 시 verdict는 `blocked_current_consumer_found`로 닫는다.
* current-like consumer candidate, ambiguous authority conflict, unresolved dynamic consumer candidate, or evidence that could imply current reachability but is not confirmed closes as `current_candidate_requires_reconciliation`.
* current-candidate verdict는 artifact mutation, old path restoration, shim, fallback, compatibility alias를 금지한다.
* current-candidate verdict는 별도 approved `DVF Bridge Authority Reconciliation` scope를 요구한다.
* `historical` 판정 허용 조건:
  * 과거 bridge format 보존의 문서적 가치가 있다.
  * closeout/provenance trace로 참조된다.
  * current path 밖으로 이동할 수 있다.
  * 이름과 manifest가 non-current historical fixture임을 명시한다.
* `reproduction` 판정 허용 조건:
  * 테스트나 재현 라운드가 해당 6-entry payload를 deterministic fixture로 소비한다.
  * tests/tools가 explicit fixture path만 참조한다.
  * current path 밖으로 이동할 수 있다.
* `stale` 판정 허용 조건:
  * current consumer가 없다.
  * historical/reproduction 보존 필요가 없다.
  * package/runtime/current-looking path에서는 오독 위험만 만든다.
* `blocked` 판정 허용 조건:
  * consumer, provenance, package inclusion, reachability evidence가 단일 classification을 지지하지 못한다.
* classification verdict must separately record root `media/` reachability, `Iris/media/` reachability, package inclusion, zip inclusion, and workspace-copy reachability. None of these fields may be inferred from another.

Validation:

* classification verdict가 Phase 1/2 evidence artifact를 참조해야 한다.
* stale 판정은 consumer absence, package absence, preservation value absence를 모두 기록해야 한다.
* historical/reproduction 판정은 explicit fixture manifest path를 동반해야 한다.
* `current_candidate_requires_reconciliation`, `blocked_current_consumer_found`, or blocked verdict는 mutation 금지 상태로 closeout해야 한다.

---

### Change 4 - Artifact Quarantine, Fixture Relocation, or Approved Hard Delete

Purpose:

classification 결과에 따라 대상 artifact를 current-looking path에서 제거하고 current path 밖으로 격리한다. In this plan, removal means removal from the old current-looking path, not hard delete by default.

Files:

* `media/lua/shared/Iris/IrisDvfBridgeData.lua`
* `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/quarantine/IrisDvfBridgeData.legacy_6_entry.lua`, default quarantine target for stale non-fixture preservation
* historical/reproduction fixture path, if selected
* fixture manifest, if selected
* `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/mutation_report.json`

Implementation Notes:

* stale이면 current-looking path에서 제거한다. 기본 처분은 default quarantine target으로 relocation하고, old path absence를 guard로 봉인하는 것이다.
* hard delete is not the default stale disposition. Hard delete is allowed only if a separate explicit approval is recorded after classification proves stale + no preservation value + no reproduction value.
* quarantine artifact는 package/runtime/current surface allowlist가 아니다. It is staging-only generated evidence and must be excluded from package and workspace-copy outputs.
* quarantine artifact is retained through post-implementation independent review and closeout. It is not a cache that may be cleaned during the round. Later cleanup is allowed only after closeout preserves hash, payload profile, provenance, and disposition.
* historical이면 current path 밖 fixture로 이동하고 filename에 `legacy`, `historical`, `6_entry`, or equivalent non-current signal을 포함한다.
* reproduction이면 current path 밖 fixture로 이동하고 tests/tools가 explicit fixture path를 참조하게 한다.
* blocked이면 artifact mutation을 수행하지 않는다.
* header/comment 교정은 historical/reproduction/quarantine target에만 적용한다. Old current-looking path의 content rewrite로 문제를 해결하지 않는다.
* header/comment를 수정해야 할 경우 additive provenance note 또는 supersession note로만 처리한다.
* root `media/` path가 package source가 아니더라도 current-looking authority 오독 surface이면 처분 대상이다. Runtime/package reachability claim은 Phase 1-2 evidence에 종속된다.
* old path 복구나 compatibility shim 추가는 이 change의 허용 행동이 아니다.

Validation:

* git diff review
* old path absence or explicit blocked/current-candidate reason
* quarantine target path, retention policy, and package exclusion check, if stale relocation is used
* fixture manifest consistency, if preserved
* package output forbidden file absence
* current runtime chunk no-mutation check
* current route regression after mutation

---

### Change 5 - Fail-Loud Guard Hardening

Purpose:

같은 stale/current-looking bridge artifact 또는 같은 6-entry legacy bridge payload가 current runtime, package, workspace-copy surface에 재유입되지 않도록 막는다.

Files:

* `Iris/tools/package_iris.ps1`
* package guard tests
* optional new stale bridge guard tool
* optional workspace-copy guard surface, if inventory finds an executable surface

Implementation Notes:

* 필수 forbidden path 후보:
  * `media/lua/shared/Iris/IrisDvfBridgeData.lua`
  * `Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua`
  * package output equivalent path for `media/lua/shared/Iris/IrisDvfBridgeData.lua`
* 필수 forbidden filename 후보:
  * `IrisDvfBridgeData.lua` in runtime/package current surfaces
* 필수 payload-level forbidden 후보:
  * exact SHA256 `C5EC93914F4A13C227BF1B3958908B860AF768113700CECB4C4496B46AD411AA`, after Phase 1 recapture
  * `interaction-cluster-rendered-v0` + `meta.stats.total = 6` + `meta.stats.active_composed = 6`
  * known 6-entry key set: `Base.CanOpener`, `Base.ElectronicsScrap`, `Base.GunpowderCan`, `Base.ModKit`, `Base.Tongs`, `Base.WeldingTorch`
  * `entries_sha256` when present in a candidate payload
* Allowlist 밖 current runtime/package/workspace-copy surface에서 payload fingerprint가 감지되면 filename이 달라도 hard fail한다.
* token guard는 docs/historical references와 fixture allowlist를 false-positive로 막지 않아야 한다.
* historical/reproduction/quarantine fixture path는 explicit allowlist가 있을 때만 pass한다. Quarantine allowlist는 package/runtime allowlist가 아니다.
* package forbidden 판단의 single writer는 `Iris/tools/package_iris.ps1`다. Optional guard/validator tools may produce evidence and self-tests, but must not define a conflicting package policy.
* package script는 stale bridge source, output inclusion, or payload fingerprint inclusion을 hard fail해야 한다.
* workspace-copy surface가 없으면 executable guard pass를 주장하지 않고 limitation으로 기록한다.
* guard 일반화 범위는 named stale bridge artifact family로 제한한다. repo-wide stale artifact sweep으로 확장하지 않는다.
* Guard comparison must use the path normalization matrix: Windows path, POSIX path, zip internal path, relative alias, resolved absolute path where applicable, and case-insensitive match on Windows-like surfaces.

Validation:

* positive case: old path present -> fail
* positive case: package output contains old filename -> fail
* positive case: package/runtime/workspace-copy candidate contains exact hash or payload-shape fingerprint under a different filename -> fail
* negative case: docs mention -> pass or diagnostic-only
* negative case: explicit historical/reproduction/quarantine fixture allowlist -> pass outside package/runtime current surface
* path normalization positive/negative cases for Windows, POSIX, zip internal, relative alias, and case-insensitive variants
* default package route pass
* current route regression pass

---

### Change 6 - Regression, No-Mutation Seal, and Closeout

Purpose:

처분과 guard가 current DVF authority와 package route를 깨지 않았음을 검증하고 closeout한다.

Files:

* `docs/stale_dvf_bridge_artifact_disposition_closeout.md`
* optional `docs/stale_dvf_bridge_artifact_disposition_decisions_packet.md`
* optional `docs/stale_dvf_bridge_artifact_disposition_roadmap_packet.md`
* `Iris/build/description/v2/staging/stale_dvf_bridge_artifact_disposition/*`

Implementation Notes:

* final report는 classification verdict, disposition action, guard coverage, validation outcome, no-mutation boundary, claim boundary를 포함한다.
* closeout은 release readiness, deployment readiness, Workshop readiness, runtime equivalence를 주장하지 않는다.
* ledger update packet is required when artifact relocation, artifact hard delete, package guard addition, workspace-copy guard addition, or authority-boundary wording changes occur. It remains a staging draft unless canon docs mutation is separately approved.
* canon docs mutation은 별도 승인 또는 explicit execution scope가 있을 때만 수행한다.
* post-implementation independent review gate must be recorded before closeout PASS/seal. Plan approval alone does not satisfy this gate. If not performed, closeout state remains `review_pending` or `seal_pending`.
* protected current payload 변경이 있으면 closeout은 fail 또는 blocked로 닫는다.

Validation:

* final direct/dynamic consumer audit
* package script pass and package zip scan
* current route regression
* protected chunk no-mutation verdict
* facts/decisions/rendered no-mutation verdict
* guard positive/negative behavior report
* package output equivalence report if package guard changes
* post-implementation independent review gate report before closeout PASS/seal
* final contract report review

---

## 7. Validation Plan

### Automated Validation

Exact command choice may be adjusted only when the local tool is missing. A validation claim is allowed only when the exact relevant command exits with code 0.

* Execution contract check:
  * `Get-Content docs\EXECUTION_CONTRACT.md`
  * Execution closeout must explicitly map disclosure, evidence, and closeout obligations that apply to this round.
* Inventory:
  * `rg --files | rg "IrisDvfBridgeData|IrisLayer3Data\.lua|IrisLayer3DataChunks\.lua"`
  * `rg -n "IrisDvfBridgeData|DvfBridge|IrisDvf|interaction-cluster-rendered-v0" .`
  * `git ls-files -- media/lua/shared/Iris/IrisDvfBridgeData.lua Iris/media/lua/shared/Iris/IrisDvfBridgeData.lua`
* Payload fingerprint scan:
  * exact SHA256 scan for `C5EC93914F4A13C227BF1B3958908B860AF768113700CECB4C4496B46AD411AA`, where byte-level candidate paths exist
  * token/shape scan for `interaction-cluster-rendered-v0`, 6-entry stats, known key set, and `entries_sha256`
* Path normalization validation:
  * Windows separator path candidate
  * POSIX separator path candidate
  * zip internal path candidate
  * relative alias candidate
  * resolved absolute path candidate
  * case-insensitive candidate on Windows-like surfaces
* Consumer / dynamic candidate search:
  * `rg -n "require|safeRequire|dofile|loadfile|package\.path|IrisDvfBridgeData|DvfBridge" Iris media docs -g "*.lua" -g "*.py" -g "*.ps1" -g "*.md"`
* Package gate:
  * `powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip`
* Package output equivalence, if package guard changes:
  * old path, old filename, exact payload hash, and payload-shape fingerprint are absent from package root and zip
  * intended package roots and current chunk manifest/chunk files remain present
  * this is package artifact equivalence only, not full runtime equivalence
* Current route regression baseline:
  * `uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --enforce-current-build-closure`
  * Expected baseline: exit code 0 and no protected current payload mutation. Test count drift must be reported rather than silently normalized.
* Focused current bridge/export tests, if relevant:
  * `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_lua_bridge_export_contract_realign.py"`
* Package guard tests, if added:
  * `uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_package_layer3_chunks_only_contract.py"`
* Default pytest route, if this execution changes shared Iris build/test code:
  * `uv run python -B -m pytest -q`
* Lua syntax, if Lua files are moved/edited rather than deleted:
  * `Test-Path .\tools\check_lua_syntax.ps1`
  * `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
  * If the script path is missing, report Lua syntax validation as blocked or record the exact adjusted command that replaces it.
* Protected surface no-mutation check:
  * before/after SHA256 report for current chunks, current facts, current decisions, current rendered output, and package-relevant Lua runtime files
* Independent review gate before PASS/seal:
  * review packet must include final diff, classification verdict, guard policy, package equivalence report if applicable, and no-mutation verdict

### Manual Validation

* git diff review scoped to intended files only
* classification verdict review against Phase 1/2 evidence
* root `media/` reachability and `Iris/media/` package source relation reviewed as separate closeout fields
* package zip content inspection for old path, old filename, exact payload hash, and payload-shape fingerprint absence
* closeout claim-boundary review

### Validation Limits

This plan does not include:

* no multiplayer validation
* no long-session runtime validation
* no full manual in-game QA
* no external mod compatibility sweep
* no vNext successor baseline validation
* no rendered-runtime full equivalence validation
* no release readiness validation
* no Workshop readiness validation
* no package readiness beyond this stale bridge artifact guard

---

## 8. Risk Surface Touch

### Authority Surface

Touched as boundary reinforcement only.

The planned change may remove or relocate a current-looking stale bridge artifact, but it must not change current DVF bridge authority. The authority statement remains:

* current runtime bridge authority is `IrisLayer3DataChunks.lua` + `IrisLayer3DataChunks/*.lua`
* `IrisDvfBridgeData.lua` 6-entry legacy payload is not current bridge authority in this round
* any current-consumer discovery is a blocked/escalation condition, not preservation approval

### Runtime Behavior Surface

Intended none.

Risk exists because the stale artifact is under a `media/lua/shared` shape. Execution must prove whether root `media/` is runtime/package reachable in this repository layout. If a current runtime consumer is found, this plan stops before silent mutation.

### Compatibility Surface

Low to medium.

If no current consumer exists, compatibility impact should be low. Hidden dynamic consumers, external scripts, or copy routes would raise the risk and must be handled by classification escalation, not by restoring the stale file as a shim.

### Sealed Artifact Surface

Protected.

Current chunks, facts, decisions, rendered output, and package deployable payload must be no-mutation surfaces for this plan. Historical/reproduction preservation can create new fixture artifacts only outside current runtime/package path.

### Public-Facing Output Surface

None.

Browser, Wiki, Tooltip, Korean text content, quality exposure, public copy, and release messaging are outside this plan.

---

## 9. Risk Analysis

### Architecture Risk

* Treating a root `media/` cleanup as an Iris runtime authority change.
* Reintroducing monolith or legacy bridge fallback logic while trying to preserve compatibility.
* Expanding a named stale artifact disposition round into repo-wide stale artifact cleanup.
* Mutating canon ledgers directly when a staging ledger packet is enough.

### Runtime Risk

* `media/lua/shared` location could be runtime-loadable in some packaging or dev launch path.
* A hidden dynamic `require` / `loadfile` / global lookup could consume the artifact.
* Removing the file before reachability audit could hide a real consumer.
* Guard false negatives could allow the stale artifact back into package output.

### Compatibility Risk

* Test/tool/doc references may be misclassified as runtime consumers.
* External local workflows may expect the root `media/` file even if package does not.
* Historical or reproduction value may be missed if the file is deleted without fixture classification.
* A false-positive guard may block legitimate historical fixture or docs references.

### Regression Risk

* Package script guard changes may fail on path separator or case differences.
* Package zip scan may miss nested or alternate root paths.
* Guard tests may pass only on one shell path style.
* No-mutation hash capture may omit a protected current payload file.

---

## 10. Rollback Plan

Rollback must not silently restore `IrisDvfBridgeData.lua` to a current-looking runtime/package path as a compatibility shim.

Allowed rollback:

* discard staged changes before commit
* revert artifact removal or relocation diff
* revert guard diff
* revert package script guard diff
* revert fixture manifest diff
* revert closeout / ledger packet draft diff

Conditional rollback:

* If a current runtime consumer is discovered after removal, restore by opening a separate `DVF Bridge Authority Reconciliation` scope. Do not silently put the stale artifact back in current path.
* If historical preservation need is discovered after removal, restore to a historical fixture path with manifest, not to the old current-looking path.
* If reproduction need is discovered, restore to an explicit reproduction fixture path and update tests/tools to point there.
* If package guard false positives block legitimate docs or fixture references, narrow the guard with explicit allowlist and rerun positive/negative tests.

Rollback does not change these decisions:

* current chunk manifest + chunk files remain current runtime authority
* 6-entry legacy bridge payload is not automatically current bridge authority
* stale/current-looking bridge artifacts must not silently enter package/runtime paths

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance.
* `docs/EXECUTION_CONTRACT.md` disclosure / evidence / closeout obligations must be checked before execution and reflected in closeout.
* Hub & Spoke boundaries remain untouched.
* Iris remains offline evidence / outcome / rendered artifact consumer at runtime; runtime does not re-compose or rejudge semantic meaning.
* Current DVF runtime/build-time separation remains preserved.
* Current deployable runtime authority remains chunk manifest + chunk files.
* Current facts / decisions / rendered / live runtime chunk payload mutation is forbidden unless a separate approved scope opens it.
* `IrisDvfBridgeData.lua` must not be restored as current fallback.
* Consumer discovery must fail-loud and escalate, not silently shim.
* `current` is not a terminal disposition in this round. Current-consumer discovery closes as blocked/escalation pending separate approved reconciliation.
* Classification uncertainty must close as `blocked / classification-undetermined`, not as resolved.
* Historical/reproduction preservation must live outside current runtime/package path.
* Stale disposition defaults to quarantine/relocation outside current-looking path. Hard delete requires separate explicit approval after stale + no preservation value + no reproduction value are proven.
* Package/workspace-copy guard must fail-loud, not silently delete or ignore.
* Payload-level forbidden guard is required for exact hash and payload-shape fingerprint, not only path/filename.
* Header/comment edits must be additive provenance or supersession notes only.
* No release readiness, Workshop readiness, B42 readiness, deployment readiness, or full runtime equivalence claim.
* Closeout PASS/seal requires post-implementation independent review of final diff, classification verdict, guard behavior, package evidence, and no-mutation verdict. Plan approval alone does not satisfy this gate. Without it, closeout remains review/seal pending.
* Dirty working tree safety: stage only files intentionally changed by this execution.

---

## 12. Expected Closeout State

Expected closeout target: `complete` if one of the following terminal states is reached and validated:

* `complete_stale_quarantined_or_relocated`: artifact classified stale, old current-looking path removed, artifact moved to default quarantine target or explicit non-current location, guard hardened, package/current no-mutation checks pass.
* `complete_stale_hard_deleted_after_approval`: artifact classified stale, no preservation value and no reproduction value proven, separate hard-delete approval recorded, old current-looking path removed, guard hardened, package/current no-mutation checks pass.
* `complete_historical_preserved`: artifact classified historical, moved to explicit non-current historical fixture path with manifest, old path blocked, validation passes.
* `complete_reproduction_preserved`: artifact classified reproduction, moved to explicit non-current reproduction fixture path with manifest, tests/tools migrated to explicit path, old path blocked, validation passes.
* `complete_absent_or_nonpackage_surface_sealed`: exact Iris runtime path absent and root artifact disposition is sealed with root reachability evidence, package no-inclusion evidence, payload fingerprint guard evidence, and no current-authority claim.

Allowed non-complete terminal states:

* `blocked_classification_undetermined`: evidence is insufficient to choose historical / reproduction / stale / current-candidate escalation.
* `blocked_current_consumer_found`: a confirmed current runtime, package, or tool consumer is discovered and a separate authority reconciliation plan is required.
* `current_candidate_requires_reconciliation`: a current-like consumer candidate, ambiguous authority conflict, unresolved dynamic consumer candidate, or unconfirmed reachability signal is discovered; mutation, shim, fallback, and old path restoration are forbidden until separate approved reconciliation.
* `blocked_package_reachability_unresolved`: package/workspace-copy reachability cannot be proven.
* `partial_guard_only`: artifact mutation is not approved, but guard and evidence packet are completed.
* `review_pending` or `seal_pending`: implementation evidence exists, but required post-implementation independent review has not been completed.

The closeout must explicitly state:

* `IrisDvfBridgeData.lua` is not current DVF bridge authority in this round.
* current chunk runtime authority is unchanged.
* protected current payload is unchanged.
* no release, deployment, Workshop, vNext cutover, or public-facing behavior claim is made.
