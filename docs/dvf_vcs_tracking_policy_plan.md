# Implementation Plan

> 상태: planned / scope-lock candidate / WARN review revisions applied / follow-up refinements applied
> 작성일: 2026-06-15
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> Execution 기준: `docs/EXECUTION_CONTRACT.md`
> Template input: `docs/PLAN_TEMPLATE.md` / sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`
> Roadmap input: `C:/Users/MW/.codex/attachments/51ab9ee7-8037-4620-ad5b-5831413da7d0/pasted-text.txt` / sha256 `4709DBC57054B3738AFF613D2BB34BC5BD7D31A49DE29D2ACDA1FA776E571223` / unsealed AI-assisted roadmap reference, preserved only as drafting input
> Review input: `C:/Users/MW/.codex/attachments/ebcdcb9b-5ad3-40c4-bc4e-f5301738857b/pasted-text.txt` / sha256 `5A62E6693EDCF3DD31CE6962D87E3915CFF123088D7F6C58AE19EB3EBA11ED9C` / WARN final review reference

---

## 1. Objective

DVF 3-3 current regeneration authority와 VCS tracking 상태를 current authority model에 맞게 정렬한다.

이번 계획의 핵심 문제는 특정 파일 하나의 `.gitignore` 예외가 아니다. DVF 3-3 pipeline에서 source input / fixture / tool / generated output / runtime deployable payload / stale quarantine artifact가 서로 다른 지위를 갖는데, VCS tracking 정책이 그 차이를 충분히 표현하지 못하면 clean checkout, regeneration, package route, stale artifact guard가 서로 다른 방향을 가리킬 수 있다.

이번 계획의 목표는 다음 상태를 만드는 것이다.

* DVF artifact family를 role 기준으로 분류한다.
* current regeneration에 필요한 tool과 manifest가 `.gitignore`에 의해 숨겨지지 않게 한다.
* generated output, source input, fixture, staging evidence, historical reproduction, diagnostic advisory, runtime deployable payload, stale quarantine evidence의 tracking 기준을 분리한다.
* ignored-reproducible artifact는 tracked input + tracked tool + tracked manifest로 재생성 가능하고, trusted current artifact hash 또는 manifest expected hash와 일치한다는 target-fidelity evidence를 갖게 한다.
* stale / non-current artifact가 current-looking VCS surface에 tracked 상태로 남지 않게 한다.
* package / workspace route의 stale artifact fail-loud guard와 VCS tracking policy가 같은 방향을 가리키게 한다.
* tracked 상태가 current authority를 뜻한다거나 ignored 상태가 disposable을 뜻한다는 오독을 차단한다.
* current facts / decisions / rendered text / runtime chunk payload는 변경하지 않는다.

실제 특정 파일이 ignored, tracked, untracked, absent 중 어느 상태인지는 이 계획이 단정하지 않는다. Phase 1에서 `git ls-files`, `git check-ignore`, `git status --ignored`로 ground-truth를 먼저 측정한다.

---

## 2. Scope

이 계획의 intended modification scope는 다음으로 제한한다.

* DVF VCS tracking policy scope lock
* DVF 관련 path의 ground-truth VCS inventory
* artifact class taxonomy 작성
* tracking policy matrix 작성
* ignored-reproducible candidate의 reproduction closure / determinism / target-fidelity probe
* `.gitignore` 최소 realignment
* 필요한 경우 git index realignment
* current-looking stale artifact의 index / working tree / ignored-present / package reachability 판정
* current-looking stale artifact의 non-current evidence path relocation 또는 index removal
* VCS tracking fail-loud guard 추가
* package stale guard alignment check
* protected current payload no-mutation check
* documentation / ledger reflection packet / review handoff

Primary target family:

* DVF 3-3 regeneration tooling
* DVF 3-3 input manifest
* DVF 3-3 source input facts, decisions, rendered output
* DVF 3-3 fixture / non-authority facts, decisions, rendered output
* DVF 3-3 generated staging output
* DVF 3-3 runtime deployable chunk manifest and chunk files
* stale bridge / monolith / quarantine evidence family
* package and workspace-copy guard surfaces that can reintroduce stale payloads

Primary evidence root:

* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/`

### Explicitly Out Of Scope

* DVF vNext baseline cutover
* successor baseline identity sealing
* full 2105 source reconstruction
* canonical rendered output promotion
* live runtime chunk replacement
* Browser / Wiki / Tooltip behavior change
* package release readiness claim
* Workshop readiness claim
* manual in-game QA
* full historical artifact byte reproducibility resolution
* `tools/build` blanket promotion or blanket deletion
* broad `.gitignore` redesign outside this DVF policy scope
* generated output 전체 tracked 전환
* ignored output 전체 삭제
* Git LFS, artifact registry, external cache, CI artifact hosting introduction
* Stale DVF Bridge Artifact Disposition의 `review_pending` 상태 해소

---

## 3. Non-Goals

* 이 계획은 VCS tracking 지위를 authority 지위로 승격하지 않는다.
* `tracked`를 current authority의 동의어로 쓰지 않는다.
* `ignored`를 disposable의 동의어로 쓰지 않는다.
* `.gitignore` 수정만으로 clean checkout regeneration readiness를 주장하지 않는다.
* package guard pass를 release readiness로 읽지 않는다.
* runtime payload no-mutation을 full runtime equivalence로 읽지 않는다.
* stale quarantine artifact를 current fallback, package allowlist, runtime authority, source authority로 승격하지 않는다.
* historical / diagnostic reproduction route를 current cleanup 명목으로 삭제하지 않는다.
* exporter behavior redesign, compose contract reopen, runtime-side repair, semantic quality judgment를 열지 않는다.
* authority migration, numeric substitution, quality / publish / runtime vocabulary change를 수행하지 않는다.

---

## 4. Assumptions

* 최상위 기준은 `docs/Philosophy.md`다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`의 Iris DVF 3-3 current readpoint를 따른다.
* `docs/EXECUTION_CONTRACT.md`의 disclosure, evidence, closeout 규율을 따른다.
* current DVF 3-3 chain은 다음 순서로 읽는다.

```text
source / manifest
-> facts
-> decisions
-> compose profile + body_plan
-> rendered
-> Lua bridge
-> chunk manifest + chunk files
```

* current runtime deployable authority는 다음 chunk surface다.

```text
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua
Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/*.lua
```

* `IrisLayer3Data.lua` monolith는 current / staging / runtime / package authority가 아니다. 명시 historical / diagnostic side-output으로만 허용된다.
* stale `IrisDvfBridgeData.lua` 계열은 current bridge authority가 아니다.
* stale bridge 보존이 필요하면 current-looking runtime / package surface가 아니라 staging quarantine 또는 explicit historical / reproduction fixture path에서만 허용된다.
* Round 3는 `tools/build` 전체 삭제가 아니라 current / historical / diagnostic route 분리로 닫혔다.
* Stale DVF Bridge Artifact Disposition은 implemented / review_pending / not sealed PASS 상태로 읽고, 이 계획이 그 상태를 대신 PASS 처리하지 않는다.
* full historical artifact byte reproducibility는 unresolved 상태로 남는다.
* `.gitignore` realignment는 authority promotion / demotion이 아니라 VCS representation / governance surface 변경이다.
* repository layout은 execution 초기에 확인한다. 특히 root `docs/` path와 authority docs path가 실제 checkout layout과 일치하는지 측정 전제에 포함한다.
* execution 시 dirty working tree가 있을 수 있으므로 intended files만 stage / commit 대상으로 삼는다.

---

## 5. Repository Areas Affected

### Code

Expected or possible touch points:

* `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
* `Iris/build/description/v2/tools/build/*dvf*tracking*policy*.py`, if new guard tooling is needed
* `Iris/tools/package_iris.ps1`
* workspace-copy related scripts, only if inventory finds executable copy surfaces

### Tests

Expected or possible touch points:

* `Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py`
* existing package guard tests under `Iris/build/description/v2/tests/`
* existing Lua bridge export / package route guard tests, if the new policy is integrated there

### Docs

Directly touched by this plan:

* `docs/dvf_vcs_tracking_policy_plan.md`

Expected or possible execution outputs:

* `docs/dvf_vcs_tracking_policy.md`
* `docs/dvf_vcs_tracking_policy_closeout.md`
* `docs/dvf_vcs_tracking_policy_decisions_packet.md`
* `docs/dvf_vcs_tracking_policy_roadmap_packet.md`
* optional `docs/dvf_vcs_tracking_policy_architecture_packet.md`

Canon docs that are authority inputs and should remain read-only unless separately approved:

* `docs/Philosophy.md`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/EXECUTION_CONTRACT.md`
* `docs/PLAN_TEMPLATE.md`

### Config

Expected touch point:

* `.gitignore`

Possible VCS state touch points:

* `git rm --cached` for stale current-looking tracked artifact, only after classification
* `git add -f` or `.gitignore` negative pattern for current-critical tool / manifest, only after policy and closure verdict

### Generated Artifacts

All generated evidence for this round should stay under:

* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/`

Expected evidence artifacts:

* `scope_lock.md`
* `vcs_tracking_inventory.jsonl`
* `vcs_tracking_summary.md`
* `premise_verdict.json`
* `ignored_current_critical_index.md`
* `tracked_stale_current_looking_index.md`
* `artifact_taxonomy.md`
* `tracking_policy_matrix.json`
* `tracking_policy_disposition.md`
* `reproduction_closure_matrix.json`
* `reproduction_hash_record.json`
* `target_fidelity_report.json`
* `manifest_coverage_fidelity_report.json`
* `protected_surface_hashes.before.json`
* `protected_surface_hashes.after.json`
* `protected_surface_hash_diff.json`
* `protected_surface_no_mutation_verdict.json`
* `stale_current_looking_presence_report.json`
* `package_zip_forbidden_scan_report.json`
* `expected_predicate_validation_report.json`
* `round_evidence_tracking_disposition.json`
* `repo_layout_check.json`
* `path_form_normalization_report.json`
* `gitignore_audit_report.md`
* `git_tracking_verdict.json`
* `vcs_policy_validation_report.json`
* `package_alignment_report.json`
* `reconciliation_packet.md`
* `review_handoff.md`

---

## 6. Planned Changes

### Change 1 - Scope Lock and Ground-Truth VCS Inventory

Purpose:

이번 라운드가 만질 수 있는 surface와 만질 수 없는 surface를 잠그고, DVF 관련 path의 실제 VCS 상태를 측정한다.

Files:

* `.gitignore`, read-only in this phase
* DVF tool / data / output / runtime / stale artifact path candidates
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/*`

Implementation Notes:

* allowed mutation surface를 `.gitignore`, git index, evidence-surface relocation, governance docs로 제한한다.
* DVF 관련 path를 role 기준으로 inventory한다.
* 각 path의 상태를 `tracked`, `ignored`, `untracked-present`, `absent`, `ambiguous`로 기록한다.
* `export_dvf_3_3_lua_bridge.py`의 exact repo path를 확인하고 ignored 여부를 측정한다.
* current regeneration manifest, facts, decisions, rendered output, chunk output, stale bridge family의 tracking state를 측정한다.
* stale current-looking artifact 후보는 index status, working tree presence, ignored-present status, package / workspace-copy reachability를 분리해서 기록한다.
* stale referent가 모호한 경우 `ambiguous`로 남기고 mutation하지 않는다.
* inventory row는 최소 `path`, `role`, `current_authority`, `tracking_state`, `working_tree_state`, `ignored_state`, `package_reachability`, `expected_tracking_state`, `reason`, `disposition`, `measurement_command`, `measurement_result`, `expected_predicate`를 포함한다.
* Phase 1은 measurement-only다. 어떤 `.gitignore` 또는 index mutation도 수행하지 않는다.

Validation:

```powershell
git ls-files <target-path>
git check-ignore -v <target-path>
git status --ignored --short
Test-Path <target-path>
```

Expected deliverables:

* `scope_lock.md`
* `vcs_tracking_inventory.jsonl`
* `vcs_tracking_summary.md`
* `premise_verdict.json`
* `ignored_current_critical_index.md`
* `tracked_stale_current_looking_index.md`

---

### Change 2 - Artifact Taxonomy and Tracking Policy Definition

Purpose:

artifact class별 expected VCS state를 문서와 matrix로 봉인한다.

Files:

* `docs/dvf_vcs_tracking_policy.md`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/tracking_policy_matrix.json`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/tracking_policy_disposition.md`

Implementation Notes:

* `.gitignore` 수정 전에 tracking policy spec을 작성한다.
* taxonomy는 filename이 아니라 role 기준으로 정의한다.
* 최소 class는 다음을 포함한다.

```text
source_input
fixture_non_authority
regeneration-tooling
current_regeneration_manifest
generated-intermediate
runtime_deployable_authority
staging_evidence
historical_reproduction
diagnostic_advisory
stale / quarantine-evidence
forbidden_current_looking_stale
unknown_requires_review
```

* expected state vocabulary를 분리하고, `docs/dvf_vcs_tracking_policy.md`에 1-line 정의를 모아둔다.

```text
tracked
tracked_required
ignored-reproducible
reproduction-retained
quarantine-retained
forbidden-current-looking
selective-tracked-closeout-evidence
ignored-generated-evidence
reserved / hold
unknown_requires_review
```

* state vocabulary의 1-line 정의는 최소 다음 의미를 포함한다.

```text
tracked: normal git index tracking is allowed.
tracked_required: path must be tracked for current regeneration or retained contract completeness.
ignored-reproducible: path may be ignored only after closure, determinism, target-fidelity, and manifest coverage PASS.
reproduction-retained: path remains retained because reproducibility or route closure is not proven enough for ignore.
quarantine-retained: stale or non-current evidence retained outside runtime/package/current-looking surfaces.
forbidden-current-looking: path/state is forbidden on current-looking surfaces regardless of authority claim.
selective-tracked-closeout-evidence: selected round evidence may be tracked because review/closeout needs it.
ignored-generated-evidence: generated evidence may remain ignored when closeout does not require tracking it.
reserved / hold: no mutation until classification or policy decision is complete.
unknown_requires_review: classification is unresolved and must be reviewed before mutation.
```

* class와 state는 서로 다른 layer다. 예를 들어 `forbidden_current_looking_stale`은 artifact class이고, `forbidden-current-looking`은 해당 class 또는 path 상태에 적용될 수 있는 expected state다.
* declared class별 expected state를 모두 배정한다.

```text
source_input:
  expected: tracked 또는 tracked_required
  note: source input은 regeneration 또는 source authority readpoint의 입력 후보이며 fixture와 섞지 않는다

fixture_non_authority:
  expected: tracked 또는 reproduction-retained
  note: test fixture / non-authority sample이며 source input이나 full current authority로 오해되지 않게 문서화

regeneration-tooling:
  expected: tracked_required when current regeneration route가 소비함
  note: historical / diagnostic only tool이면 reproduction-retained 또는 reserved / hold 가능

current_regeneration_manifest:
  expected: tracked_required 또는 명시 reproduction-retained
  note: output 재생성 route fingerprint 보존

generated-intermediate:
  expected: ignored-reproducible only after closure + target-fidelity PASS, otherwise reproduction-retained 또는 tracked
  note: determinism만으로 ignored-reproducible 승격 금지

runtime_deployable_authority:
  expected: tracked 또는 별도 reproduction-retained verdict
  note: tracking status는 authority promotion / demotion이 아님

staging_evidence:
  expected: ignored-generated-evidence by default, selective-tracked-closeout-evidence when closeout / review가 필요함
  note: 이번 round staging evidence도 policy matrix row를 가져야 함

historical_reproduction:
  expected: reproduction-retained 또는 tracked
  note: Round 3 historical test-route 분류와 VCS tracking 분류는 별개임

diagnostic_advisory:
  expected: reserved / hold 또는 tracked only when diagnostic route consumes it
  note: Round 3 diagnostic route 분류와 VCS tracking 분류는 별개임

stale / quarantine-evidence:
  expected: quarantine-retained in non-current evidence path only
  note: package / runtime / workspace-copy allowlist가 아님

forbidden_current_looking_stale:
  expected: absent from current-looking path; not tracked, not untracked-present, not package-reachable
  note: ignored-present도 package / workspace-copy가 볼 수 있으면 forbidden

unknown_requires_review:
  expected: reserved / hold
  note: mutation 금지
```

* `docs/dvf_vcs_tracking_policy.md`는 `docs/Philosophy.md` → `docs/DECISIONS.md` → `docs/ARCHITECTURE.md` → `docs/ROADMAP.md` 아래의 subordinate policy 문서다.
* `docs/dvf_vcs_tracking_policy.md`는 artifact authority를 promote / demote하지 않는다.
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/*` 산출물 자체의 VCS 지위도 `tracking_policy_matrix.json`에 포함한다.
* `git add -f` 허용 후보는 `tracking_policy_matrix.json`에서 `tracked_required` verdict를 받은 current-critical tool / manifest로 제한한다.
* evidence packet은 실행 부담을 줄이기 위해 통합 가능하다. 단, 통합 packet은 각 expected predicate, source row, hash, and disposition을 잃지 않아야 한다.

Validation:

* policy class마다 Phase 1 inventory row가 연결된다.
* `.gitignore` 변경 후보와 tracked / untracked 후보가 policy row에서만 파생된다.
* docs에서 tracking 상태와 current authority를 동일시하거나 ignored 상태와 disposable 상태를 동일시하지 않는다.

---

### Change 3 - Reproduction Closure, Determinism, and Target-Fidelity Probe

Purpose:

`ignored-reproducible` 후보 artifact가 post-realignment proposed tracked set만으로 재생성 가능하고, 재생성 결과가 trusted current artifact hash 또는 manifest expected hash와 일치하는지 확인한다.

Files:

* DVF source input / fixture / manifest / generated-output candidates, read-only unless scratch output is generated
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/reproduction_closure_matrix.json`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/reproduction_hash_record.json`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/target_fidelity_report.json`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/manifest_coverage_fidelity_report.json`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/protected_surface_hashes.before.json`

Implementation Notes:

* closure 평가는 Phase 1 current checkout state가 아니라 taxonomy / policy에서 유도한 post-realignment proposed tracked set 기준으로 수행한다.
* Phase 1 measurement는 현재 상태와 proposed state의 delta를 식별하는 입력일 뿐이다.
* live output은 건드리지 않고 scratch / staging 영역에서만 재생성한다.
* 동일 입력으로 2회 재생성하고 hash-stable 여부를 기록한다.
* `ignored-reproducible` PASS 조건은 다음 모두를 만족해야 한다.

```text
two-run hash parity
AND (regenerated hash == trusted current artifact hash
     OR regenerated hash == manifest expected hash)
AND manifest coverage / fidelity check PASS
```

* trusted current artifact hash 또는 manifest expected hash가 없으면 해당 artifact는 ignored로 강등하지 않고 `tracked` 또는 `reproduction-retained`로 유지한다.
* regenerated output이 deterministic이더라도 target-fidelity가 맞지 않으면 `ignored-reproducible`이 될 수 없다.
* manifest coverage / fidelity check는 regenerated artifact가 manifest가 기대한 row / chunk / file / payload 범위를 빠짐없이 덮는지 확인한다.
* closure가 닫히지 않으면 pipeline을 고치지 않고 `reproduction-retained` 후보로 분류한다.
* determinism 문제가 발견되더라도 이 라운드를 pipeline refactor로 확장하지 않는다.
* protected current payload before hash를 먼저 캡처한다.

Validation:

* proposed tracked input completeness
* proposed tracked tool completeness
* proposed tracked manifest completeness
* two-run hash parity
* regenerated hash equals trusted current artifact hash or manifest expected hash
* manifest coverage / fidelity check PASS
* missing reference hash causes tracked or reproduction-retained disposition
* no live output mutation
* no runtime payload mutation

Expected deliverables:

* `reproduction_closure_matrix.json`
* `reproduction_hash_record.json`
* `target_fidelity_report.json`
* `manifest_coverage_fidelity_report.json`
* `protected_surface_hashes.before.json`
* preliminary no-mutation verdict

---

### Change 4 - `.gitignore` and VCS State Realignment

Purpose:

확정된 taxonomy / policy / closure verdict에 맞춰 실제 `.gitignore`와 tracked / untracked 상태를 정렬한다.

Files:

* `.gitignore`
* git index entries for current-critical tool / manifest / stale current-looking artifacts
* non-current evidence path, only if relocation is needed
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/gitignore_audit_report.md`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/git_tracking_verdict.json`

Implementation Notes:

* current regeneration tool이 ignored되지 않도록 `.gitignore` 예외 또는 allowlist를 추가한다.
* current regeneration manifest가 policy에 맞게 tracked 또는 reproduction-retained 상태가 되도록 한다.
* generated output ignore rule은 유지하되 current-critical tool / manifest를 잡아먹지 않도록 조정한다.
* stale current-looking artifact는 tracked 상태에서 제거하거나 non-current evidence path로 relocation한다.
* stale artifact를 단순 ignored 처리로 숨기지 않는다.
* stale current-looking path는 index status, working tree presence, ignored-present status, package reachability를 모두 분리 판정한다.
* stale current-looking path verdict는 다음으로 구조화한다.

```text
tracked: forbidden
untracked-present: forbidden unless explicit blocked/quarantine handling exists
ignored-present: forbidden if package/workspace-copy can see it
absent: pass
```

* quarantine artifact가 retained될 경우 non-current임을 path, manifest, docs에 명시한다.
* actual `.gitignore` rule text는 Phase 1 측정 결과와 기존 `.gitignore` 구조를 확인한 뒤 최소 수정으로 확정한다.
* `git add -f`는 current-critical tool / manifest에만 허용한다.
* `git add -f`는 해당 path가 `tracking_policy_matrix.json`에서 `tracked_required` verdict를 받은 경우에만 허용한다.
* package zip 내부 old filename, old path, exact payload hash, payload-shape fingerprint scan은 automated report로 남긴다.
* payload-shape fingerprint는 byte hash가 달라도 같은 stale payload shape를 잡기 위한 normalized structural signature다.
* stale bridge / monolith family의 payload-shape fingerprint는 최소 다음 요소를 포함한다.

```text
file family / format marker
top-level Lua return or module shape
known generated header or version marker when present
meta.stats total / active count when present
entry key set or chunk key range
entries_sha256 or equivalent normalized entry payload digest when present
chunk manifest module prefix / chunk count when relevant
```

* package zip scan은 zip 내부 path normalization 후 old path, old filename, exact hash, payload-shape fingerprint를 모두 검사한다.
* runtime chunk payload, facts, decisions, rendered output이 변경되면 rollback boundary violation으로 처리한다.

Validation:

```powershell
git ls-files Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py
git ls-files media/lua/shared/Iris/IrisDvfBridgeData.lua
git status --porcelain --ignored -- media/lua/shared/Iris/IrisDvfBridgeData.lua
Test-Path media/lua/shared/Iris/IrisDvfBridgeData.lua
```

`git check-ignore` and forbidden-match checks must be evaluated through expected predicate wrappers. Raw exit code is not a PASS verdict because an ignored path returns exit code 0.

Example current-critical unignore predicate:

```powershell
git check-ignore -q Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py
if ($LASTEXITCODE -eq 0) {
  throw "current regeneration tool is still ignored"
}
```

Additional checks:

* current regeneration tool not ignored
* current regeneration manifest tracked or explicitly retained
* generated output ignored as intended
* stale current-looking path absent from index and working tree, or explicitly blocked
* stale current-looking path not ignored-present in a package / workspace-copy reachable location
* package zip filename / path / hash / payload-shape forbidden scan report exists
* runtime chunks / facts / decisions / rendered content `changed_count == 0`
* package stale guard unchanged or strengthened

---

### Change 5 - Fail-Loud Guard and Test Integration

Purpose:

VCS tracking policy가 회귀하지 않도록 guard를 추가한다.

Files:

* `Iris/build/description/v2/tests/test_dvf_vcs_tracking_policy.py`
* optional guard tooling under `Iris/build/description/v2/tools/build/`
* `Iris/tools/package_iris.ps1`, only if package alignment requires guard hardening
* package guard tests, if integrated into existing test surface

Implementation Notes:

Guard categories:

```text
ignored_current_critical_guard
tracked_stale_current_looking_guard
unregistered_generated_tracked_guard
fixture_manifest_consistency_guard
package_forbidden_surface_alignment_guard
reproduction_closure_invariant_guard
target_fidelity_invariant_guard
stale_working_tree_presence_guard
round_evidence_tracking_disposition_guard
path_form_normalization_guard
```

* current-critical tool이 ignored되면 fail한다.
* current regeneration manifest가 policy 밖 상태이면 fail한다.
* stale current-looking artifact가 tracked, untracked-present, forbidden ignored-present, package-reachable, workspace-copy-reachable 상태이면 fail한다.
* generated output이 policy 없이 tracked되면 review fail로 잡는다.
* fixture로 tracked된 generated-looking file은 fixture manifest에 등록되어야만 허용한다.
* ignored-reproducible artifact는 closure + target-fidelity + manifest coverage / fidelity가 모두 PASS일 때만 허용한다.
* 이번 round staging evidence artifact는 `tracking_policy_matrix.json`의 evidence class와 실제 VCS state가 일치해야 한다.
* Round 3 current / historical / diagnostic route와 분리된 VCS-policy test route를 둔다.
* Round 3 import block과 충돌하지 않도록 guard는 파일 / index 지위를 검사하고 검사 대상 도구를 import하지 않는다.
* Python subprocess 기반 `git check-ignore`, `git ls-files`, `git status --ignored`, `Test-Path` equivalent 결과를 stable하게 파싱하되, raw exit code가 아니라 expected predicate로 PASS / FAIL을 판정한다.
* `rg` forbidden absence checks는 raw exit code가 아니라 forbidden match count가 0인지로 판정한다.
* package route와 stale bridge guard alignment를 확인한다.
* path-form normalization guard는 Windows separator, POSIX separator, zip-internal separator, CI checkout relative path, and case-insensitive Windows-like path를 최소 1개 이상 포함한다.

Validation:

* positive case: ignored current-critical tool -> fail
* positive case: stale current-looking path tracked -> fail
* positive case: stale current-looking path untracked-present -> fail unless explicit blocked/quarantine handling exists
* positive case: stale current-looking path ignored-present and package-reachable -> fail
* positive case: package zip contains old filename, old path, exact payload hash, or payload-shape fingerprint -> fail
* positive case: same payload-shape fingerprint under different filename -> fail
* positive case: unregistered generated output tracked -> fail
* positive case: deterministic regenerated output with mismatching target hash -> fail
* positive case: missing trusted reference hash for ignored-reproducible candidate -> fail into tracked / reproduction-retained disposition
* negative case: registered fixture path -> pass
* negative case: docs mention -> pass or diagnostic-only
* package forbidden surface alignment pass
* Windows / CI path-form normalization cases pass

---

### Change 6 - Documentation, Ledger Reflection, and Review Handoff

Purpose:

VCS tracking policy를 current docs와 review packet에 반영하고, closeout / ledger reflection의 입력을 준비한다.

Files:

* `docs/dvf_vcs_tracking_policy.md`
* `docs/dvf_vcs_tracking_policy_closeout.md`
* `docs/dvf_vcs_tracking_policy_decisions_packet.md`
* `docs/dvf_vcs_tracking_policy_roadmap_packet.md`
* optional `docs/dvf_vcs_tracking_policy_architecture_packet.md`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/reconciliation_packet.md`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/review_handoff.md`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/round_evidence_tracking_disposition.json`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/repo_layout_check.json`
* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/path_form_normalization_report.json`

Implementation Notes:

* `docs/dvf_vcs_tracking_policy.md`를 current policy surface로 둔다.
* `docs/dvf_vcs_tracking_policy.md`는 `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` 아래의 subordinate VCS policy surface로 둔다.
* `docs/dvf_vcs_tracking_policy.md`는 artifact authority를 promote / demote하지 않으며, authority와 tracking status가 직교한다는 점을 명시한다.
* `docs/dvf_vcs_tracking_policy.md`에는 state vocabulary 1-line definitions를 모아둔다.
* `docs/dvf_vcs_tracking_policy.md`에는 artifact class와 expected state layer가 다르다는 점을 명시한다.
* `docs/dvf_vcs_tracking_policy.md`에는 payload-shape fingerprint 구성 요소를 정의한다.
* closeout에는 source / rendered / runtime payload mutation이 없었음을 명시한다.
* closeout에는 root `docs/` path와 authority docs path가 실제 checkout layout과 일치하는지 확인한 `repo_layout_check.json` 결과를 반영한다.
* Round 3, Lua Bridge Export Contract, Stale Bridge Disposition과의 관계를 명시한다.
* before / after status, closure verdict, guard result, no-mutation verdict를 reconciliation packet으로 묶는다.
* 이번 round staging evidence artifacts의 tracking disposition을 closeout에 포함한다.
* evidence ceremony가 부담이 될 경우 closeout packet 일부를 통합할 수 있다. 단, 통합으로 인해 predicate result, hash, disposition, or review handoff trace가 사라지면 안 된다.
* `DECISIONS.md` 직접 mutation은 compact ledger packet이 review된 뒤 별도 승인 또는 seal step에서만 수행한다.
* `ROADMAP.md` 직접 mutation은 Doing / Done / Hold 관점의 update packet으로 먼저 준비한다.
* `ARCHITECTURE.md`는 VCS tracking과 authority orthogonality를 짧게 보강할 필요가 있을 때만 optional packet으로 둔다.
* independent review handoff를 남긴다.
* release readiness, package readiness, runtime rollout, successor cutover를 주장하지 않는다.

Validation:

* docs에서 tracking 상태와 current authority를 동일시하지 않는다.
* docs에서 ignored 상태와 disposable 상태를 동일시하지 않는다.
* stale quarantine artifact가 current fallback으로 오해되지 않는다.
* payload-shape fingerprint definition is present before closeout claim.
* repo layout check exists and matches the documented authority paths, or mismatch is recorded as blocked / hold.
* Windows / CI path-form normalization report exists if guard tooling is added.
* release / package readiness 비약이 없다.
* packet 내용이 실제 git / guard / no-mutation 결과와 일치한다.

---

## 7. Validation Plan

### Automated Validation

No validation may be claimed as passed unless the exact relevant validation wrapper or expected-predicate check exits with code 0. Raw discovery commands such as `git check-ignore` and `rg` absence probes are evidence inputs, not PASS verdicts by themselves.

Expected predicate rules:

* `git check-ignore` returns exit code 0 when a path is ignored. Current-critical unignore validation must assert `ignored == false`.
* `rg` returns non-zero when no match is found. Forbidden absence validation must assert forbidden match count is 0.
* `git ls-files` proves index state only. Stale current-looking disposition also requires working tree presence, ignored-present status, and package / workspace reachability predicates.
* package zip scans must assert old path, old filename, exact payload hash, and payload-shape fingerprint are absent.
* payload-shape fingerprint scans must use the definition recorded in `docs/dvf_vcs_tracking_policy.md` or the round policy matrix.

VCS inventory and ignore checks:

```powershell
git check-ignore -v Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py
git ls-files Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py
git ls-files media/lua/shared/Iris/IrisDvfBridgeData.lua
git status --porcelain --ignored -- media/lua/shared/Iris/IrisDvfBridgeData.lua
Test-Path media/lua/shared/Iris/IrisDvfBridgeData.lua
```

Current-critical unignore predicate example:

```powershell
git check-ignore -q Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py
if ($LASTEXITCODE -eq 0) {
  throw "current regeneration tool is still ignored"
}
exit 0
```

Forbidden absence predicate example:

```powershell
$matches = rg -n "IrisDvfBridgeData|IrisLayer3Data.lua" Iris/media media -g "*.lua"
if ($LASTEXITCODE -gt 1) {
  throw "rg forbidden absence probe failed"
}
if ($LASTEXITCODE -eq 0 -and $matches) {
  throw "forbidden current-looking stale surface found"
}
exit 0
```

Repository search / inventory:

```powershell
rg --files | rg "export_dvf_3_3_lua_bridge|dvf_3_3_input_manifest|dvf_3_3_facts|dvf_3_3_decisions|dvf_3_3_rendered|IrisLayer3Data|IrisDvfBridgeData"
rg -n "IrisDvfBridgeData|IrisLayer3Data.lua|IrisLayer3DataChunks|export_dvf_3_3_lua_bridge|dvf_3_3_input_manifest" Iris docs media .gitignore
```

Suggested focused guard route:

```powershell
python -B -m unittest discover -s Iris/build/description/v2/tests -p "test_dvf_vcs_tracking_policy.py"
```

Current route regression:

```powershell
python -B Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure
```

Historical / diagnostic route preservation, if touched:

```powershell
python -B Iris/_docs/round3/round3_run_contract_tests.py --class historical
python -B Iris/_docs/round3/round3_run_contract_tests.py --class diagnostic
```

Default pytest route, if shared build / test code changes:

```powershell
python -B -m pytest -q
```

Package route alignment:

```powershell
powershell -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 -Clean -Zip
```

Protected surface no-mutation:

* before / after SHA256 for current chunk manifest
* before / after SHA256 for current chunk files
* before / after SHA256 for current facts
* before / after SHA256 for current decisions
* before / after SHA256 for current rendered output
* before / after package-relevant stale forbidden surface scan

Phase 3 closure-specific validation:

* post-realignment proposed tracked input completeness
* post-realignment proposed tracked tool completeness
* post-realignment proposed tracked manifest completeness
* two-run hash parity
* regenerated hash equals trusted current artifact hash or manifest expected hash
* manifest coverage / fidelity check PASS
* no ignored-reproducible disposition when reference hash is missing
* no live output mutation
* no runtime payload mutation

Stale current-looking artifact presence validation:

* index tracked predicate
* working tree `Test-Path` predicate
* ignored-present predicate
* package / workspace-copy reachability predicate
* package zip filename / path / exact hash / payload-shape fingerprint absence report

Round evidence tracking validation:

* `Iris/build/description/v2/staging/dvf_vcs_tracking_policy/*` artifacts are classified in `tracking_policy_matrix.json`
* actual tracking state matches tracked closeout evidence, ignored generated evidence, or reproduction-retained evidence disposition

Repo layout validation:

* root `docs/` exists and contains `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `PLAN_TEMPLATE.md`, and `EXECUTION_CONTRACT.md`
* documented authority paths match current checkout layout
* mismatch is recorded as blocked / hold, not silently normalized

Path-form normalization validation:

* Windows separator candidate
* POSIX separator candidate
* zip-internal path candidate
* CI checkout relative path candidate
* case-insensitive Windows-like candidate
* at least one positive and one negative case for stale current-looking path normalization

### Manual Validation

* `git diff --stat` and `git diff` review for intended-file-only changes
* Phase 1 inventory row review
* taxonomy row to policy row traceability review
* `.gitignore` negative pattern order review
* current-critical tool / manifest unignore review
* stale current-looking artifact disposition review
* package zip forbidden scan report review for stale bridge / monolith / exact payload fingerprints
* payload-shape fingerprint definition review
* repo layout check review
* Windows / CI path-form normalization report review, if guard tooling is added
* closeout claim-boundary review
* independent review handoff packet review

### Validation Limits

This plan does not include:

* no full runtime equivalence validation
* no manual in-game QA
* no long-session runtime validation
* no multiplayer validation
* no Workshop deployment validation
* no B42 compatibility validation
* no external ecosystem compatibility sweep
* no full historical artifact byte reproducibility resolution
* no successor baseline correctness validation
* no vNext source-to-runtime parity validation
* no Browser / Wiki / Tooltip visual QA
* no package release readiness validation
* no Stale Bridge Disposition sealed PASS

---

## 8. Risk Surface Touch

### Authority Surface

Touched as VCS authority representation / governance surface only.

Runtime authority itself must not change. This plan may change how VCS tracking policy represents current regeneration, fixture, generated, runtime deployable, and stale artifact classes. It must not promote or demote DVF runtime authority.

### Runtime Behavior Surface

Intended none.

Runtime Lua behavior, Browser behavior, Tooltip behavior, Wiki behavior, source facts, decisions, rendered text, runtime chunk manifest, and runtime chunk files must remain unchanged.

### Compatibility Surface

Touched in clean checkout, package, and workspace-copy workflows.

Runtime external mod compatibility is not expected to change. However, current regeneration tool availability, ignored-generated-output handling, stale artifact package exclusion, and guard checks can affect developer workflows and package/workspace routes.

### Sealed Artifact Surface

Protected.

Current facts, decisions, rendered output, runtime chunk manifest, runtime chunk files, and prior sealed readpoints must not be rewritten by this plan. Any new evidence is additive under the round staging root.

### Public-Facing Output Surface

None.

No README marketing, Workshop text, release note, in-game UI, Browser, Tooltip, or Wiki-facing text changes are intended.

---

## 9. Risk Analysis

### Architecture Risk

* VCS tracking status may be mistaken for authority status.
* Generated output may be tracked broadly and make non-authority output look canonical.
* Current regeneration tooling may be treated as disposable output because it lives near generated artifacts.
* `.gitignore` policy may become a hidden authority model instead of a VCS representation rule.
* `docs/dvf_vcs_tracking_policy.md` may be overread as authority-promoting canon if subordinate precedence is not stated.
* source input and fixture / non-authority sample may be mixed if they remain one policy class.
* Ledger updates may become too long and violate compact ledger principles.

### Runtime Risk

* A stale current-looking artifact might be package-reachable even if it appears to be only repository residue.
* An index operation could accidentally untrack live runtime chunk payload.
* Reproduction closure probes could overwrite live output if staging-safe paths are not enforced.
* Determinism-only closure could reproduce a different target artifact consistently.
* Stale artifact relocation could be misread as runtime behavior cleanup.

### Compatibility Risk

* Clean checkout regeneration could fail if required tool / manifest remains ignored.
* Historical or diagnostic route could lose needed reproduction material if stale cleanup is too broad.
* Package route and VCS guard could disagree, causing false pass or false failure.
* Raw `git check-ignore` or `rg` exit-code semantics could invert expected PASS / FAIL if not wrapped by predicates.
* Guard tests that shell out to git may be brittle across Windows / CI path forms.

### Regression Risk

* `.gitignore` negative pattern order could fail silently.
* Directory ignore rules may override file-level unignore patterns.
* Generated outputs could accidentally become tracked.
* Stale artifacts could remain in working tree after index removal.
* Stale artifacts could remain ignored-present in a package-reachable location.
* No-mutation hash set could omit a protected payload.
* Package zip forbidden scan could miss hash-equivalent payload under a different filename.
* Payload-shape fingerprint could be interpreted inconsistently if not defined before closeout.
* Documentation may overclaim package readiness, release readiness, or sealed PASS.

---

## 10. Rollback Plan

Rollback units:

* `.gitignore` changes are reverted as a single patch or commit revert.
* tracked / untracked changes are reverted through explicit `git add`, `git rm --cached`, or commit revert for named paths only.
* stale artifact relocation is non-destructive by default and can be restored from the non-current evidence path if classification is revised.
* guard / test changes can be reverted independently from `.gitignore` if they prove unstable.
* documentation packets can be revised or discarded without mutating canon ledgers.

Rollback triggers:

* current regeneration tool remains ignored after realignment
* current regeneration manifest lacks tracked or explicit retained status
* generated output is broadly tracked outside policy
* stale current-looking artifact remains tracked or package-reachable without explicit blocked state
* stale current-looking artifact remains untracked-present or forbidden ignored-present without explicit blocked / quarantine handling
* reproduction closure, target-fidelity, or manifest coverage fails but artifact was already marked ignored-reproducible
* trusted current artifact hash or manifest expected hash is missing but artifact was marked ignored-reproducible
* raw `git check-ignore` or `rg` exit code is used as PASS verdict instead of expected predicate wrapper
* package guard and VCS policy disagree
* protected current chunks / facts / decisions / rendered output change unexpectedly
* current route regression fails due to this round
* closeout wording claims release readiness, runtime rollout, current baseline replacement, or Stale Bridge Disposition sealed PASS

Rollback must preserve these constraints:

* current chunk manifest + chunk files remain current runtime authority
* runtime payload no-mutation boundary is maintained
* stale current-looking artifact is not silently restored as current fallback
* authority promotion / demotion is not inferred from tracking rollback
* full historical artifact byte reproducibility remains unresolved unless separately proven

---

## 11. Governance Constraints

* `docs/Philosophy.md` compliance is mandatory.
* Hub & Spoke boundaries remain untouched.
* Iris runtime remains render-only and must not compose, repair, source-validate, or judge semantic quality.
* DVF runtime / build-time separation must remain intact.
* Current runtime deployable authority remains chunk manifest + chunk files.
* Current facts / decisions / rendered / live runtime chunk payload mutation is forbidden unless a separate approved scope opens it.
* VCS tracking status remains orthogonal to authority status.
* Tracking status must not be worded as a synonym for current authority.
* Ignored status must not be worded as a synonym for disposable output.
* `source_input` and `fixture_non_authority` must remain separate policy rows.
* State vocabulary definitions must be centralized in `docs/dvf_vcs_tracking_policy.md`.
* Artifact class and expected state layers must remain distinct.
* Payload-shape fingerprint must be defined before it supports package or closeout claims.
* `docs/dvf_vcs_tracking_policy.md` remains subordinate to `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`.
* `docs/dvf_vcs_tracking_policy.md` must not promote or demote artifact authority.
* `.gitignore` realignment must be derived from measured ground-truth and taxonomy, not premise.
* `ignored-reproducible` disposition requires closure, two-run determinism, target-fidelity, and manifest coverage / fidelity evidence.
* Missing trusted current artifact hash or manifest expected hash blocks ignored-reproducible disposition.
* Raw `git check-ignore` and `rg` exit codes must not be used as PASS verdicts without expected predicate wrappers.
* No blanket `tools/build` deletion or blanket promotion.
* No broad generated-output tracked conversion.
* No stale quarantine artifact current fallback.
* Stale current-looking artifacts must be absent from index, working tree, forbidden ignored-present states, and package / workspace reachable surfaces unless explicitly blocked or quarantined.
* Unknown or ambiguous artifact classification must close as blocked / hold, not resolved.
* Historical / diagnostic route preservation must not be broken by current cleanup.
* Package / workspace-copy guard must fail loud; it must not silently delete, hide, or promote stale payloads.
* `.gitignore` patch must be minimal and explain why each exception or ignore rule exists.
* `git add -f` is allowed only for current-critical tool / manifest paths with `tracked_required` verdict in `tracking_policy_matrix.json`.
* Generated staging evidence must remain non-current unless separately promoted through an approved authority path.
* This round's staging evidence artifacts must have their own tracking disposition row.
* Stale Bridge Disposition review_pending state is not resolved by this plan.
* Canon `DECISIONS.md`, `ARCHITECTURE.md`, and `ROADMAP.md` mutation requires separate approval or explicit execution scope.
* Release readiness, Workshop readiness, B42 readiness, deployment readiness, manual in-game validation, runtime rollout, package release, and public exposure are not implied.
* Dirty working tree safety applies: stage only files intentionally changed for this scope.

---

## 12. Expected Closeout State

Expected closeout target: `complete` if every required execution condition is satisfied within the stated validation ceiling.

`complete` requires:

* Phase 1 ground-truth status matrix exists.
* Premises are separated into confirmed / refuted / ambiguous.
* `export_dvf_3_3_lua_bridge.py` or its actual current regeneration tool path is classified as current regeneration tooling, historical, diagnostic, or reproduction-retained.
* current regeneration tooling is not hidden by `.gitignore`.
* current regeneration manifest is tracked or explicitly retained.
* source_input, fixture_non_authority, regeneration-tooling, current_regeneration_manifest, generated-intermediate, runtime_deployable_authority, staging_evidence, historical_reproduction, diagnostic_advisory, stale / quarantine-evidence, forbidden_current_looking_stale, unknown_requires_review each have expected VCS state or explicit reserved / hold disposition.
* `.gitignore` hides generated output without hiding current-critical tool / manifest.
* ignored-reproducible artifacts satisfy reproduction closure, two-run determinism, target-fidelity, and manifest coverage / fidelity invariants.
* ignored-reproducible artifacts have trusted current artifact hash or manifest expected hash references.
* current-looking VCS surface has no stale / non-current artifact tracked, untracked-present, forbidden ignored-present, package-reachable, or workspace-reachable without explicit blocked / quarantine handling.
* package zip forbidden scan reports old path, old filename, exact payload hash, and payload-shape fingerprint absence.
* payload-shape fingerprint has a recorded definition before closeout.
* stale bridge quarantine payload, if retained, is documented as non-current evidence only.
* round staging evidence artifacts have explicit tracking disposition.
* repo layout check confirms documented authority paths or records mismatch as blocked / hold.
* path-form normalization guard covers Windows / CI path cases when guard tooling is added.
* VCS guard route passes.
* package route continues to fail loud on stale bridge / monolith reintroduction.
* Round 3 current / historical / diagnostic route separation remains intact.
* protected current chunks / facts / decisions / rendered output no-mutation verdict is PASS.
* documentation does not equate tracking status with current authority.
* documentation does not equate ignored status with disposable output.
* closeout does not claim release readiness, package release readiness, runtime rollout, successor cutover, manual in-game QA, or Stale Bridge Disposition sealed PASS.
* DECISIONS / ROADMAP reflection is compact and evidence-bounded.
* review handoff packet exists.

Allowed complete variant:

* `already_consistent_no_realignment_required`: Phase 1 measurement refutes the ignored-current-critical and tracked-stale-current-looking premises, policy matrix and guard evidence prove the current state is already consistent, and no `.gitignore` / index mutation is required.

Allowed non-complete terminal states:

* `partial`: policy docs and inventory exist, but `.gitignore`, index, guard, or closure work is incomplete.
* `implemented_only`: realignment is implemented, but required validation or review did not run.
* `blocked`: measurement, classification, reproduction closure, package reachability, protected no-mutation, or guard stability prevents safe completion.

The closeout must explicitly state:

* VCS tracking policy was realigned only within the measured surface.
* current runtime authority is unchanged.
* protected current payload is unchanged.
* authority status and tracking status remain orthogonal.
* no release, deployment, Workshop, vNext cutover, or public-facing behavior claim is made.
