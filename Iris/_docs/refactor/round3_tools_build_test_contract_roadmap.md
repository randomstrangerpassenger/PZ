# Round 3 Roadmap — tools/build Script & Test Contract Disentanglement

Date: 2026-06-11

Template: `docs/ROADMAP_TEMPLATE.md`

Scope root: `Iris/build/description/v2/tools/build/*.py` and
`Iris/build/description/v2/tests/test_*.py`

Governing inventories (readpoints, do not duplicate their authority here):

- `Iris/build/description/v2/tools/build/INVENTORY.md`
- `Iris/_docs/refactor/phase1_active_manifest.md`
- `Iris/build/build_import_contract.md`

Sealed prior decisions inherited by this roadmap:

- conflict 14.1: canonical directory count is **281** `.py` (excl `__pycache__`).
- conflict 14.2: import form resolved = **package form** for the compose core;
  direct-execution remains the baseline for non-migrated reproduction scripts.
- conflict 14.3: **per-file / per-directory disposition only**; filename-glob
  archive/delete is forbidden.

---

## 1. Problem Statement

`Iris/build/description/v2/tools/build/` holds **281** Python scripts but only
**12** are git-tracked core. The other **269** are gitignored "reproduction"
scripts. The naive cleanup instinct — "keep the 12, drop the rest" — collides
with a second fact: the **test corpus imports the reproduction scripts
heavily**, so they are load-bearing under `unittest`/`pytest` discovery even
though they are invisible to a plain tracked-file `rg`.

Concrete pain points:

- **Invisible coupling.** The reproduction scripts are gitignored, so they do
  not appear in tracked-file searches, but they *are* on disk and *are*
  collected by test discovery. "It looks deletable" and "the test suite imports
  it" are both true at once.
- **Discovery has no boundary.** `python -B -m unittest discover -s
  Iris/build/description/v2/tests` runs **everything on disk** (a historical
  closeout record shows `380 tests / OK`; Phase 1 must remeasure the live
  baseline), with no separation between *current contract* tests and
  *historical reproduction* tests.
- **Unprovable core.** Nobody can currently answer "how many scripts does the
  current build/test contract actually require?" with evidence. The boundary
  between current build core, historical reproduction script, and one-shot
  generator is not visible from code structure alone.
- **Disposition is blocked.** Because the required set is unproven, conflict
  14.3 (correctly) forbids any archive/delete. The directory stays at 281 files
  indefinitely with no path to shrink it safely.

---

## 2. Current State

### Measured inventory (re-measured 2026-06-11; methodology in Phase 1)

| Metric | Value | Source |
|---|---:|---|
| `.py` in scope dir (excl `__pycache__`) | 281 | INVENTORY 2026-06-07, re-confirmed |
| git-tracked core | 12 | `git ls-files` |
| gitignored reproduction | 269 | derived |
| `build_*.py` | 177 | INVENTORY |
| `report_*.py` | 57 | INVENTORY |
| other `*.py` | 47 | derived |
| `test_*.py` on disk under `description/v2/tests` | 190 | `find` |
| git-tracked tests | 6 | `git ls-files` |
| gitignored tests | 184 | derived |
| distinct `tools.build.<module>` targets referenced | 199 | `rg --no-ignore -o` |
| test files importing `tools.build.*` | 160 | `rg --no-ignore -l` (tests) |
| build-dir files importing `tools.build.*` | 134 | `rg --no-ignore -l` (tools/build) |

> The user-cited figures (≈191 import sites / ≈178 unique modules) are an earlier
> measurement window and are the same order of magnitude. Phase 1 re-locks the
> canonical figures; this roadmap does not treat any pre-lock number as binding.

### The 12 tracked core

- Index generators: `build_iris_recipe_index_data.py`,
  `build_iris_moveables_index_data.py`, `build_iris_fixing_index_data.py`
- Guard / recovery rounds:
  `build_legacy_active_silent_current_surface_guard_round.py`,
  `build_static_report_label_cleanup_referent_recovery_round.py`
- Compose core (7): `compose_layer3_text.py` + `compose_layer3_{blocks, io,
  identity, body_profile, item, render}.py`

### The 6 tracked tests — the latent contract seed (key finding)

| Tracked test | Imports `tools.build.*` |
|---|---|
| `test_build_iris_index_data.py` | the 3 index generators only |
| `test_compose_layer3_text_v2.py` | `compose_layer3_text`, `compose_layer3_body_profile` |
| `test_current_authority_source_path_guard.py` | `compose_layer3_text` |
| `test_layer4_absorption_current_surface_guard.py` | none |
| `test_layer4_trace_edge_authority_admission_round.py` | none |
| `test_legacy_active_silent_current_surface_guard.py` | none |

**The tracked tests import only tracked-core modules (or nothing).** A *current
contract boundary already exists implicitly in the tracked set* — it is simply
not declared or enforced. The 184 gitignored tests are what reach into the 269
reproduction scripts and the 199 reproduction-module targets.

### Import hubs (most-imported reproduction/core modules)

`compose_layer3_text` (71), `validate_interaction_cluster_rendered` (57),
`report_weak_active_cleanup_w2_existing_cluster_absorption` (46),
`export_dvf_3_3_lua_bridge` (32), `validate_interaction_cluster_phase_d_runtime`
(30), `build_interaction_cluster_compose_input` (25). The reproduction set is a
**dense peer-import graph**, not loose scratch files (INVENTORY classification).

### Discovery infrastructure

- `pytest.ini` exists at repo root. The only collection-limiting `conftest.py`
  is `Iris/build/tests/conftest.py` (root build tests).
- `Iris/build/description/v2/tests/` has **no** collection guard → discovery
  collects all 190 on-disk test files, including the 184 gitignored ones.
- `python -B -m unittest discover -s Iris/build/description/v2/tests -p
  "test_*.py"` is the historical recorded validation command (`380 tests / OK`);
  this is not a live canonical baseline until Phase 1 remeasures it.

### Existing classification (do not re-derive)

INVENTORY already assigns all in-scope files `reproduce-required`, lists a
Family Inventory (acquisition, identity_fallback 40, interaction_cluster 29,
role_fallback_hollow 35, post_cleanup 27, …), Import Hubs, and 36
Artifact-Path-Only scripts. INVENTORY also flags **Phase 7a consolidation
candidates** (sibling `batch{2..9}`, `b1..b4/c1a..c1e`, `phase3_pkg3{a..j}`,
`freeze_quality_baseline_v{1..4}`, `report_*_{draft,final}`). This roadmap
only records disposition/archive/keep-historical boundaries for those families;
content consolidation, merge, and dedup remain a Phase 7a follow-up, not this
roadmap's execution scope.

---

## 3. Desired Outcome

- A **declared, enforced boundary** between *active build core* and *historical
  reproduction scripts/tests*, visible at a glance in `tools/build`.
- **Default test discovery runs only current-contract tests.** Historical
  reproduction tests run only via an explicit, separate path.
- An **evidence-proven minimal script closure**: the exact set of scripts the
  current build/test contract requires, computed from import-closure, not
  intuition.
- A **proven disposition** for every out-of-closure reproduction script
  (keep-as-historical / archive / manifest-only / delete), each with a recorded
  rationale — so the directory can finally shrink without violating 14.3.
- A **guardrail** that fails loud if a current-contract test later imports a
  historical reproduction module (prevents boundary erosion).

---

## 4. Constraints

- **conflict 14.3 preserved**: no filename-glob archive/delete. Every
  disposition is per-file/per-directory with recorded evidence.
- **conflict 14.2 preserved**: compose core stays package-form
  (`python -m tools.build.compose_layer3_text`); non-migrated reproduction
  scripts keep their direct-execution bootstrap.
- **FAIL-LOUD preserved**: guard/recovery rounds and surface guards must keep
  failing loudly; discovery routing must not silently drop tests.
- **Generated-artifact parity preserved**: the runtime Lua outputs
  (`IrisRecipeIndexData.lua`, `IrisMoveablesIndexData.lua`,
  `IrisFixingIndexData.lua`, Layer3 chunks) must remain byte-identical. This is
  a build-tooling reorg, not an output change.
- **No-`__init__.py` namespace behavior preserved** (two distinct `tools` trees:
  `Iris/build/tools` and `Iris/build/description/v2/tools`).
- **Reproducibility preserved**: a reproduction script that any retained test or
  documented runbook needs must remain runnable; archive ≠ break.
- **Working-tree reality**: the tree already carries many M/D/untracked files;
  the large Git-surface phase (Phase 5) must be a dedicated change, not mixed
  with unrelated edits (per INVENTORY guidance).

---

## 5. Non-Goals

- Rewriting, merging, or refactoring the *internals* of reproduction scripts
  (family consolidation/dedup is Phase 7a follow-up, not this roadmap).
- Changing runtime Lua behavior or any public-facing description output.
- Migrating every reproduction script to package-form import (14.2 keeps direct
  execution for the non-core set).
- Resolving the broader Iris refactor backlog outside `tools/build` + its tests.
- Converting root `Iris/build/tests` script-style tests (owned by the import
  contract / Phase 10, separate track).
- Multiplayer, deployment, or long-session runtime validation.

---

## 6. Proposed Approach

Sequence chosen for **risk reduction first**: every destructive step is preceded
by a non-destructive proof step, so deletion is always evidence-backed.

1. **Phase 1 — Measure & lock** — re-derive canonical counts and define the
   classification rule before touching anything.
2. **Phase 2 — Classify tests by contract and status** — assign every test a
   `contract_class` (`current`, `historical`, `diagnostic`) and a `state` (`ok`,
   `non_collectable`, `non_passing`, `stale`). Pure analysis, no moves.
3. **Phase 3 — Route discovery** — make default discovery current-only;
   historical reproduction reachable via an explicit opt-in command or recorded
   frozen/non-executable status. Assert the test-case identities and result
   counts reconcile.
4. **Phase 4 — Prove the active core closure** — compute the import closure of
   current-contract tests and the description/v2 `tools/build` core-12 readpoint
   from INVENTORY/phase1_active_manifest, then combine it with
   doc/runbook/artifact-reference and artifact-regeneration signals. This is the
   evidence input to "how many scripts does the contract require"; import closure
   alone is not sufficient for archive/delete.
5. **Phase 5 — Execute disposition** — per-file decision and application
   (keep-historical / archive / manifest-only / delete) for out-of-closure
   scripts. This is the large dedicated Git change.
6. **Phase 6 — Lock the boundary** — structural separation + a guard test +
   inventory/contract doc updates so the boundary cannot silently erode.

Classification rule (the spine of the whole roadmap):

> Import closure is an initial classification signal, not a sufficient rule. A
> test gets a `contract_class` first, then a `state`. A test is a
> **current-contract candidate** when its transitive import closure touches only
> tracked-core modules (or no `tools.build` module), then passes manual audit for
> assertion intent. A test is a **historical-reproduction candidate** when its
> closure touches at least one gitignored reproduction module, unless assertion
> intent/audit evidence makes it diagnostic. `historical` means a test validates
> the reproduction contract for a prior round or sealed readpoint; `diagnostic`
> means a one-off advisory/non-contract test that does not claim a reproduction
> guarantee. Collectability/pass-state produces `state`: `ok` satisfies the
> assigned contract's pass/skip rule; `non_collectable` fails discovery/import/load
> before a runnable identity; `non_passing` collects but fails/errors/times out or
> has an unapproved skip; `stale` is superseded, duplicate, or points at a retired
> readpoint. State never moves a current test out of the current gate. `current +
> non_passing` fails the current gate, `current + non_collectable` blocks it, and
> `current + stale` requires explicit blocked-current handling or owner-approved
> subtraction.
> A script is **active/current-retained** when import closure, root entrypoint,
> dynamic/path execution, doc/runbook reference, artifact reference, or committed
> artifact-regeneration evidence requires it; otherwise it is only a disposition
> candidate after manual audit.

---

## 7. Authority / Surface Impact

### Authority Surface
None. No authority ownership (compose authority, surface guards) changes; guard
tests are reclassified by location, not by what they assert.

### Runtime Behavior Surface
None. Build-time tooling only. Runtime Lua is untouched.

### Compatibility Surface
Build-command compatibility: the documented `unittest`/`pytest` commands change
*scope* (current-only by default). The historical command form is preserved as
an explicit opt-in. The import contract doc must be amended to describe both.

### Sealed Artifact Surface
The reproduction scripts' `staging/`, `output/`, and runtime-export artifacts
are sealed reproduction outputs. Disposition must preserve the ability to
regenerate any artifact a retained test or runbook depends on.

### Public-Facing Output Surface
None. Generated description Lua and index data must remain byte-identical when
disposition touches generator or committed-artifact dependencies (verified in
Phase 5 validation).

---

## 8. Phases

### Phase 1 — Measurement freeze & classification rule

Goal: Produce a single machine-generated manifest that re-locks every count and
encodes the current/historical classification rule, so all later phases cite one
source of truth.

Primary Changes:
- A read-only analysis script kept outside `tools/build`, under a `_round3/` or
  `Iris/_docs/round3/` analysis dir, that emits `round3_contract_manifest.json`:
  per-script {tracked?, family, imported-by count, in-tracked-test-closure?,
  in-historical-test-closure?, artifact-path-only?, dynamic-import-signal?}.
- A short doc pinning canonical figures and reconciling them against the
  user-cited ≈191/≈178 window.

Expected Risks: dynamic imports (`importlib`, `__import__`, `subprocess`
`python …`) escaping static analysis → false "unreferenced". Mitigation:
explicitly grep dynamic-import + subprocess patterns and fold hits into the
manifest as `dynamic-import-signal`.

Expected Validation: lightweight. Manifest totals must reconcile to 281 / 12 /
269 and 190 / 6 / 184.

Expected Deliverables: `round3_contract_manifest.json`,
`round3_measurement_lock.md`.

---

### Phase 2 — Test taxonomy split (analysis only)

Goal: Assign all 190 tests a two-axis taxonomy (`contract_class` plus `state`)
with no file moves and no discovery change yet.

Primary Changes:
- Apply the classification rule from Phase 1. Seed `contract_class=current` with
  the 6 tracked tests (proven to import only tracked core) and grow it only with
  tests whose closure stays inside tracked core and whose manual audit confirms
  current contract intent. `contract_class=historical` validates a prior-round or
  sealed-readpoint reproduction contract; `contract_class=diagnostic` is
  advisory/non-contract and does not carry a reproduction guarantee. Then assign
  `state=ok/non_collectable/non_passing/stale`.
- Emit `round3_test_taxonomy.json` (test → contract_class → state → reason).
- Manually audit the boundary tests (the 0-import guard tests and any test whose
  closure is borderline) — guard tests with no `tools.build` import are
  current-contract by intent, confirm against what they assert.

Expected Risks: a test that *looks* historical but encodes a current guarantee
(or vice versa) → misclassification. Mitigation: human review of every test that
flips class vs its filename signal (29 `current/contract/smoke/gate`-named, 2
`repro/historical`-named today).

Expected Validation: standard. `sum(contract_class x state) == total discovered
test identities`; current-contract includes the 6 tracked tests or explains any
exception. `current + non_passing/non_collectable` fails or blocks the current
gate instead of being routed away.

Expected Deliverables: `round3_test_taxonomy.json`, taxonomy section appended to
the lock doc.

---

### Phase 3 — Discovery routing

Goal: Default discovery runs current-contract only; historical reproduction runs
on an explicit, separate path. Directly satisfies the "discovery runs current
tests only by default, or historical path is separated" success criterion.

Primary Changes (pick the lowest-risk mechanism that remains
`unittest`-compatible):
- Preferred: use a unittest-compatible path, pattern, wrapper, or manifest runner
  so the default run is current-only. Keep a documented historical command or a
  recorded frozen/non-executable status. Pytest configuration is not the default
  mechanism and requires separate dependency proof and parity review.
- Record the historical route's observed status (pass/fail/blocked/non-collectable
  or frozen-candidate) in this phase. Long-term preservation policy is decided in
  Phase 6 closeout after that observation exists.
- Update `Iris/build/build_import_contract.md` "Pytest discovery contract" to
  describe the two scopes.

Expected Risks: silently dropping tests (masking real loss) when narrowing
scope. Mitigation: reconciliation by collected test-case identity plus
tests-run/errors/failures/skips, not by file count. The historical path's
pass/fail/blocked/non-collectable status is recorded; green is not assumed.

Expected Validation: heavy on identity/result reconciliation. Run the sealed
current-default command and the sealed historical command if D3 keeps historical
execution. Compare them to the Phase 1 legacy full-discovery identity/result
baseline, including explicit exclusions for diagnostic/stale/non-collectable
buckets.

Expected Deliverables: unittest-compatible discovery route or wrapper, updated
import-contract section, `round3_discovery_reconciliation.md` with identity and
result-count reconciliation. Pytest config is only a separately approved
compatibility note, not the default deliverable.

---

### Phase 4 — Active core closure proof

Goal: Compute and record the provable minimal script set the current contract
requires — the evidence answer to "how many of the 281 are actually needed."

Primary Changes:
- From Phase 1 data, compute the transitive import closure of
  (current-contract tests ∪ the description/v2 `tools/build` core-12 readpoint
  from INVENTORY/phase1_active_manifest). Emit
  `round3_active_core_closure.json` (the active set) and its complement
  `round3_disposition_candidates.json`.
- Cross-check: every tracked-core module must be in the closure; the 3 index
  generators + compose 7 must be present.

Expected Risks: closure under-counts because of dynamic/`subprocess` reuse, or
over-counts because a test transitively imports a hub that pulls in many leaves.
Mitigation: fold Phase 1 `dynamic-import-signal`, path-execution,
doc/runbook/artifact-reference, and artifact-regeneration signals into the
manifest; annotate each candidate with why it is outside the retained set.

Expected Validation: standard. Re-run current-contract discovery using *only*
the closure set present (temporarily hide candidates in a scratch worktree) to
prove the current contract still passes without the candidates.

Expected Deliverables: `round3_active_core_closure.json`,
`round3_artifact_dependency_manifest.json`,
`round3_artifact_dependency_method.md`, `round3_disposition_candidates.json`,
closure summary in the lock doc.

---

### Phase 5 — Disposition execution (large dedicated Git change)

Goal: Apply a recorded per-file disposition to every out-of-closure candidate.
This is the change INVENTORY says must be dedicated and not mixed with other
work.

Primary Changes (per-file, evidence-tagged; choose one per script):
- **keep-historical**: outside active closure but inside historical-test closure
  → retain, relocate under a historical tree, optionally promote from gitignored
  to tracked-as-historical so the reproduction suite is reproducible from a
  clean checkout.
- **manifest-only**: artifact-path-only with no test/runbook consumer → record
  provenance in a manifest, then archive the script body.
- **archive**: outside both closures and with no import, artifact dependency,
  doc/runbook/artifact-reference, dynamic/path-execution, or unresolved signal
  → `git mv` to an archive
  location (reversible).
- **delete**: only after an archive interval and explicit user sign-off; never
  in the same step as archive.

Expected Risks: HIGH — breaking reproducibility of a historical artifact, or
review noise from a 200+ file move colliding with the already-dirty working
tree. Mitigation: tag/branch before the move; archive-before-delete; do it on a
clean-ish tree; per-file evidence row required before each move.

Expected Validation: heavy. After moves: current-default discovery green;
historical command/status follows D3; a spot-sample of relocated reproduction
scripts reruns only when D3 requires executable historical preservation;
generated runtime Lua diff is empty when disposition touches generator or
committed-artifact dependencies.

Expected Deliverables: `round3_disposition_log.md` (one row per file: path →
action → evidence), the executed moves, updated `.gitignore` for any
track/relocate.

---

### Phase 6 — Boundary lock & doc reconciliation

Goal: Make the boundary self-defending and update the governing inventories so
future readers see current vs historical immediately.

Primary Changes:
- Add a **guard test** (current-contract class) that scans current-contract
  tests and **fails loud** if any imports a historical/out-of-closure module —
  prevents silent boundary erosion.
- Update `INVENTORY.md`, `phase1_active_manifest.md`, and
  `build_import_contract.md` with the new boundary, the closure size, and the
  two-scope discovery contract. Record a conflict-style resolution note for the
  current/historical split.
- Add a `tools/build/README` or manifest pointer so `tools/build` visibly
  distinguishes active core from historical at a glance.
- Apply the historical preservation policy decision to the Phase 3 historical
  route observation: pass-required, explicit fail/block allowed, or frozen
  non-executable.

Expected Risks: doc drift if the guard test and inventory disagree. Mitigation:
the guard test reads the manifest from Phase 1 as its source of truth.

Expected Validation: standard. Guard test fails on an injected violation and
passes on the real tree.

Expected Deliverables: guard test, updated INVENTORY/manifest/import-contract,
`tools/build` README/pointer.

---

## 9. Validation Expectations

### Expected Validation Depth
Standard overall, **heavy** on test-case identity/result reconciliation (Phases
3-5) and on generated-artifact byte-parity in the disposition phase (Phase 5).

### Expected Validation Areas
- determinism (generated Lua + JSON artifacts byte-identical)
- regression (current-contract discovery green throughout)
- migration (historical-path pass/fail/blocked/non-collectable status is
  recorded; relocated scripts still regenerate only when D3 requires executable
  historical preservation)
- compatibility (documented commands still work under the new scopes)

### Known Validation Limits
- no multiplayer validation
- no deployment / packaging validation
- no long-session runtime validation
- no claim that all 184 historical tests are green on every phase unless the
  sealed historical command was actually run and passed
- static+dynamic import analysis proves *referenced*, not *semantically alive*;
  "delete-safe" is bounded by that analysis plus the archive interval

---

## 10. Risk Assessment

### High Risk
- Archiving/deleting a script some historical test, artifact dependency,
  dynamic/path execution path, or undocumented runbook needs (reproducibility
  loss). → closure/reference/dependency proof + archive-before-delete + per-file
  evidence.
- Phase 5 large move colliding with the already-dirty working tree (lost edits,
  unreviewable diff). → dedicated change on a clean tree, tag before move.

### Medium Risk
- Dynamic / `subprocess` imports escaping static closure → false candidates.
  → dynamic-import-signal sweep folded into the manifest.
- Discovery narrowing silently dropping tests → reconciliation against the live
  Phase 1 collected test-case identity/result baseline. Historical green is not
  assumed.

### Low Risk
- Naming/relocation churn for clearly-historical files.
- Doc reconciliation drift → guard test reads the manifest as source of truth.

---

## 11. Rollback Strategy

- Phases 1-4 are **additive** (manifests, taxonomy, discovery config, closure
  JSON). Roll back by reverting the docs/config; no script content is lost.
- Phase 3 discovery routing is config-only; revert restores full-scope
  discovery.
- Phase 5 uses **archive (`git mv`) before delete**, with a tag/branch captured
  immediately before the move; any over-eager archive is restored via
  `git mv` back or `git revert`. Deletion is a separate, later, signed-off step.
- A scratch worktree is used for the "hide candidates and re-run" proofs so the
  main tree is never left in a half-moved state.

---

## 12. Success Criteria

- Active build core vs historical reproduction boundary is **declared and
  visible** in `tools/build` (Desired Outcome §3, user success criterion 1, 4).
- Default `unittest`/`pytest` discovery runs **current-contract only**;
  historical reproduction runs via a separate explicit path (user criterion 2).
- The required-script count is **closure-proven**, not intuited; the
  disposition-candidate set is enumerated with per-file evidence (user
  criterion 3).
- Every disposition (keep-historical/archive/manifest-only/delete) carries a
  recorded rationale; conflict 14.3 never violated.
- The `contract_class x state` taxonomy matrix reconciles to the locked
  test-case identity/result baseline; generated runtime Lua/JSON artifacts are
  byte-identical when disposition touches generator or committed artifact
  dependencies.
- No import-closure-positive, artifact-dependency-positive,
  doc/runbook/artifact-reference-positive, dynamic/path-execution-positive, or
  unresolved script is archived/deleted.
- A guard test prevents future current→historical import bleed.

---

## 13. Expected Claim Boundary

This roadmap does NOT automatically imply:

- full runtime equivalence (only build-time tooling + generated-artifact parity
  is validated)
- that archived/deleted scripts are provably *dead* beyond static+dynamic import
  analysis and the archive interval
- release, deployment, or packaging readiness
- resolution of the Phase 7a family-consolidation backlog (separate roadmap)
- production validation

Do not claim success beyond validated scope. Each phase claims only its own
recorded evidence (manifest totals, reconciliation counts, byte-diff results).
