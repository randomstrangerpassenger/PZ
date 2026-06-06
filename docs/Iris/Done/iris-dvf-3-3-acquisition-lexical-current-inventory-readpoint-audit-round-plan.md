# Iris DVF 3-3 Acquisition Lexical Current Inventory / Readpoint Audit Round Plan

> 상태: Draft v0.4-taxonomy-glossary-review-response
> 기준일: 2026-06-05
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
> authority input: `ROADMAP - Iris DVF 3-3 Acquisition Lexical Current Inventory / Readpoint Audit Round` (user-provided pasted roadmap)
> review input: `REVIEW - Iris DVF 3-3 Acquisition Lexical Current Inventory / Readpoint Audit Round Plan` (user-provided pasted review). v0.2 resolves Critical C1/C2 by adding writer-path / import-graph closure completeness gates and narrowing Branch C to tooling/code-surface authority absence without denying sealed data authority. v0.2 also addresses R3-R8 by clarifying audit-root/protected-hash separation, current default compose path consumption, suppress sense disambiguation, branch precedence, closed expansion wording, and raw/logical count invariants.
> v0.3 review input: `REVIEW - Iris DVF 3-3 Acquisition Lexical Current Inventory / Readpoint Audit Round Plan v0.2` (user-provided pasted review). v0.3 adopts the required Branch C/D precedence correction by making Branch D outrank Branch C, fixes the Branch C closeout template wording, and repeats bounded discovery completeness in closeout claim boundary.
> v0.4 feedback input: user-provided taxonomy clarity note. v0.4 adds a glossary requirement distinguishing authority classification `current_validator_or_gate_utility` from suppress disposition `current_validator_surface` / `current_gate_surface`.
> 계획 형식: `docs/PLAN_TEMPLATE.md`; path verified; sha256 `38D70D4D624733DB4D24F047E0B737A47C75522A967C84F06FE5AABC5EBD9BA1`; line_count `109`
> 실행 상태: planning authority only. This document does not execute inventory, mutate source facts, source decisions, rendered text, runtime Lua, packaged Lua, bridge payload, state axes, public-facing behavior, suppress retirement, rollout, or release readiness.

---

## 1. Objective

이번 execution plan의 목적은 current checkout 기준 Iris DVF 3-3 `acquisition lexical` 관련 surface를 전수 inventory하고, 각 surface의 authority class와 `suppress` dependency disposition을 봉인하는 readpoint audit round를 실행 가능한 형태로 정리하는 것이다. 여기서 `전수 inventory` claim은 vocabulary/root search만으로 주장하지 않고, known acquisition lexical anchors에서 출발한 writer-path / import-graph closure pass가 `writer_path_reachable_but_unindexed_count == 0`을 만족할 때만 허용한다.

이 round가 답해야 하는 질문은 다음으로 제한한다.

```text
current checkout 기준 acquisition lexical 관련 surface는 무엇인가?
known acquisition lexical anchors에서 reachable한 writer-path / import-graph surface가 inventory universe에 모두 포함되었는가?
각 surface는 current authority input, validator/gate utility, staging-only, diagnostic/report-only,
test fixture, historical artifact, stale predecessor plan, closed expansion candidate 중 어디에 속하는가?
`suppress` 잔존 surface는 current gate/validator인지, diagnostic/report/test/historical/stale plan인지?
```

이번 round의 최대 claim은 다음이다.

```text
current checkout 기준 acquisition lexical 관련 surface를 전수 inventory하고,
writer-path / import-graph closure에서 reachable-but-unindexed surface가 없음을 확인했으며,
각 surface의 authority class와 suppress dependency disposition을 봉인했다.
```

이번 round는 acquisition lexical 기능 개선, suppress retirement, contract expansion, runtime rollout, release readiness를 주장하지 않는다.
또한 sealed `facts.acquisition_hint` data authority나 current default compose consumption을 부정하지 않는다.

---

## 2. Scope

This is a governance and readpoint-audit planning round for Iris DVF 3-3 acquisition lexical surfaces. Execution under this plan may create round-local inventory, classification, disposition, hash, staging report, and closeout artifacts.

In scope:

* Opening contract / scope lock.
* Surface universe, search corpus, vocabulary lock.
* Writer-path / import-graph closure completeness pass.
* Raw occurrence inventory.
* Logical surface grouping.
* Per-surface evidence collection.
* Authority classification.
* Current default compose path consumption validation.
* Ambiguity / blocked residue handling.
* `suppress` sense disambiguation.
* `suppress` dependency disposition.
* Out-of-scope / existing-closure expansion candidate record.
* Protected surface non-mutation / hash delta verification.
* Staging report / hard gate.
* Closeout / readpoint seal.

### Explicitly Out Of Scope

* Acquisition lexical sentence edits.
* Acquisition lexical validator rewrite.
* Acquisition lexical utility rewrite.
* `suppress` retirement execution.
* `suppress` removal patch.
* Source facts patch.
* Source decisions patch.
* Rendered text regeneration.
* Runtime Lua regeneration.
* Packaged Lua mutation.
* Runtime consumer repair.
* Style linter hard gate promotion.
* Korean josa processor introduction.
* Phrasebook introduction.
* Array acquisition input contract introduction.
* Acquisition contract expansion.
* Candidate state, active/silent, adopted/unadopted reclassification.
* `publish_state`, `quality_state`, or `runtime_state` mutation.
* Manual in-game validation.
* Deployment validation.
* Release or Workshop readiness declaration.
* Stale plan physical deletion.
* Historical artifact physical deletion.
* Dead surface removal.
* Coverage, quality, or completion remeasurement.
* Sealed `facts.acquisition_hint` authority denial.
* Current default compose consumption denial.

---

## 3. Non-Goals

This plan does not attempt to:

* Improve acquisition lexical wording.
* Retire or remove `suppress`.
* Expand the acquisition lexical contract.
* Reopen `josa_adaptive`, `phrasebook`, array acquisition, or runtime-side repair.
* Turn style lint into a hard gate.
* Treat historical or staging artifacts as current function evidence.
* Treat stale predecessor plans as current execution openings.
* Deny sealed acquisition data authority or current compose consumption.
* Measure acquisition lexical quality, coverage, or completion.
* Validate runtime behavior.
* Validate multiplayer behavior.
* Validate external mod ecosystem compatibility.
* Declare release readiness, Workshop readiness, or deployed closeout.

---

## 4. Assumptions

* `docs/Philosophy.md` is the top authority for Pulse ecosystem governance.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md` are the current ecosystem state references for this plan.
* `docs/PLAN_TEMPLATE.md` is the required implementation plan form for this repository context.
* Acquisition lexical is a build-time authority branch, not a runtime Korean language repair system.
* The current production structure remains `facts -> decisions -> compose -> normalizer -> style linter -> rendered -> Lua bridge`.
* Current default compose authority is read as the `compose_profiles_v2 + body_plan` path. Legacy-only `sentence_plan` or predecessor-only consumption does not by itself make a surface current authority.
* Sealed acquisition data authority such as `facts.acquisition_hint`, and current compose consumption of that data authority, remain preserved unless a separate successor/correction round says otherwise.
* Style linter remains advisory-only.
* Runtime consumer does not repair acquisition text.
* Facts null reason plus canonical trace principles remain preserved.
* `josa_adaptive`, `phrasebook`, array acquisition, and runtime-side repair are out of scope for this round. If a prior sealed closure exists for a candidate, this round records that existing closure; if no prior sealed basis exists, this round records only `out_of_scope_for_this_round` and does not create permanent design closure.
* `suppress` retirement is not executed in this round. At most, this round may identify a follow-up candidate queue.
* Prior staging artifacts and closeout evidence are provenance unless current checkout evidence proves a current authority role.

---

## 5. Repository Areas Affected

### Code

* None expected for production code.
* If execution requires helper scripts, they must be round-local or explicitly reviewed before introduction. They must not alter current production source, rendered output, runtime Lua, or packaged Lua surfaces.

### Docs

* `docs/Iris/iris-dvf-3-3-acquisition-lexical-current-inventory-readpoint-audit-round-plan.md`
* Optional execution closeout after hard gates pass:
  * `docs/Iris/iris-dvf-3-3-acquisition-lexical-current-inventory-readpoint-audit-round-closeout.md`
* Optional additive canon readpoint after staging report / review / hard gate:
  * `docs/DECISIONS.md`
  * `docs/ARCHITECTURE.md`
  * `docs/ROADMAP.md`

### Config

* None expected.

### Generated Artifacts

Round-local artifacts should be placed under a dedicated staging/report root such as:

* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/round_opening_contract.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/forbidden_mutation_surface.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/authority_read_order.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/validation_ceiling.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_surface_universe.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_search_vocabulary.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_corpus_manifest.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_exclusion_manifest.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_writer_path_closure.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_import_graph_closure.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/writer_path_reachable_unindexed_report.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/current_default_path_consumption_report.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_raw_occurrence_index.jsonl`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/raw_occurrence_summary.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/suppress_raw_occurrence_index.jsonl`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_logical_surface_inventory.jsonl`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/surface_grouping_summary.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/raw_to_surface_map.jsonl`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_surface_evidence_index.jsonl`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/surface_evidence_summary.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_authority_matrix.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_classification_summary.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/writer_reach_surface_index.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/forbidden_writer_reach_report.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/unclassified_blocked_surface_index.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/blocked_surface_unblock_conditions.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/suppress_dependency_disposition.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/suppress_dependency_disposition.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/suppress_followup_candidate_queue.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/out_of_scope_closed_expansion_candidates.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/closed_expansion_surface_summary.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/protected_surface_hash_before.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/protected_surface_hash_after.json`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/non_mutation_delta_report.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_staging_classification_report.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/classification_hard_gate_result.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/surface_count_axis_disambiguation.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/acquisition_lexical_readpoint_audit_closeout.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/followup_round_queue.md`
* `Iris/build/description/v2/staging/acquisition_lexical_current_inventory_readpoint_audit_round/claim_boundary.md`

The staging/report root above is an audit-artifact root, not a protected source/rendered/runtime/package surface. Protected non-mutation hashes must be file-manifest based and must exclude the round-local audit root itself. The audit root must also be excluded from any build/package derivation check and must not be placed under `Iris/build/package/`, `Iris/media/lua/`, or packaged-runtime output roots.

---

## 6. Planned Changes

### Change 1 - Opening Contract / Scope Lock

Purpose:

Lock this as a non-mutation current readpoint audit round before any inventory work begins.

Files:

* `round_opening_contract.md`
* `forbidden_mutation_surface.md`
* `authority_read_order.md`
* `validation_ceiling.md`

Implementation Notes:

* Record round title: `Acquisition Lexical Current Inventory / Readpoint Audit Round`.
* Record authority read order: `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`, approved roadmap / plan.
* Define validation ceiling: `static_inventory_and_governance_readpoint_only`.
* Split mutable audit artifacts from immutable protected surfaces.
* Forbidden mutation surfaces must include facts, decisions, rendered text, runtime Lua, packaged Lua, Lua bridge payload, `quality_state`, `publish_state`, and `runtime_state`.
* Confirm `suppress` retirement, runtime repair, and acquisition contract expansion are out of scope.
* Confirm the round-local audit root is excluded from protected hash manifests and build/package derivation checks.
* Include a taxonomy glossary line: authority classification `current_validator_or_gate_utility` is a non-writer validator/gate utility class for the main surface matrix; suppress disposition `current_validator_surface` / `current_gate_surface` is a separate suppress-only disposition axis.

Validation:

* Opening checklist includes non-mutation declaration.
* Immutable protected surface list is explicit.
* Audit-root/protected-hash separation is explicit.
* Taxonomy glossary distinguishes authority classification classes from suppress disposition labels.
* Canon addendum is not written before staging report, hard gate, and review.
* Optional canon addendum is not required for round success.

---

### Change 2 - Surface Universe / Search Corpus / Vocabulary Lock

Purpose:

Define the universe and repeatable search inputs before collecting occurrences.

Files:

* `acquisition_lexical_surface_universe.json`
* `acquisition_lexical_search_vocabulary.json`
* `acquisition_lexical_corpus_manifest.json`
* `acquisition_lexical_exclusion_manifest.json`
* `acquisition_lexical_writer_path_closure.json`
* `acquisition_lexical_import_graph_closure.json`
* `writer_path_reachable_unindexed_report.md`
* `current_default_path_consumption_report.md`

Implementation Notes:

* Lock search vocabulary, including:
  * `acquisition`
  * `acquire`
  * `acquisition_hint`
  * `acquisition_lexical`
  * `lexical`
  * `canonical_trace`
  * `null_reason`
  * `suppress`
  * `suppressed`
  * `suppression`
  * `validator`
  * `promotion`
  * `staging`
  * `runtime reflection`
  * `josa_adaptive`
  * `phrasebook`
  * `array acquisition`
  * `보관 장소`
  * `취급 장소`
  * `작업 장소`
  * `작업 구역`
  * `판매 장소`
  * `작업 차량`
* Define inventory roots for source data, build scripts, validators, utilities, docs, tests, reports, staging artifacts, closeout artifacts, and plans.
* Define excluded or separately-classified roots for archives, generated duplicates, obsolete draft plans, and review artifacts.
* Run a writer-path / import-graph closure pass from known acquisition lexical anchors into reachable current writer, validator, promotion, and compose surfaces.
* The exhaustive inventory claim is allowed only if closure pass confirms every reachable surface is present in the universe.
* Record `writer_path_reachable_but_unindexed_count`; any positive count blocks Branch A and prevents sealed exhaustive claim.
* Record current-default-path consumption against `compose_profiles_v2 + body_plan`; legacy-only `sentence_plan` or predecessor-only consumption must be separated.

Validation:

* Search vocabulary manifest exists and is parseable.
* Corpus manifest exists and is parseable.
* Exclusion manifest records reasons.
* Search universe is reproducible by grep/rg anchors.
* `writer_path_reachable_but_unindexed_count == 0` is required for Branch A exhaustive seal.
* Current default path consumption report exists and separates current-default from legacy-only consumption.

---

### Change 3 - Raw Occurrence Inventory / Logical Surface Grouping

Purpose:

Collect raw occurrences, then group them into logical surfaces that can be classified by authority.

Files:

* `acquisition_lexical_raw_occurrence_index.jsonl`
* `raw_occurrence_summary.json`
* `suppress_raw_occurrence_index.jsonl`
* `acquisition_lexical_logical_surface_inventory.jsonl`
* `surface_grouping_summary.json`
* `raw_to_surface_map.jsonl`

Implementation Notes:

* Record raw occurrence rows with path, line, matched term, local context, and preliminary surface kind.
* Preliminary surface kinds may include schema, utility, validator, build tool, staging artifact, report, test, doc, plan, closeout artifact, and generated artifact.
* Add a `suppress` flag for all suppress-related rows.
* Group repeated occurrences inside one file into a logical surface where appropriate.
* Raw-to-surface mapping cardinality must be explicit. Default cardinality is many raw occurrences to one logical surface; split or many-to-many mapping is allowed only when the mapping file records the reason.
* Each logical surface should include `surface_id`, `path`, `surface_kind`, `matched_terms`, `raw_occurrence_count`, `generated`, `current_consumer`, `writer_reach`, `runtime_reach`, `publish_reach`, `test_only`, `historical_or_provenance`, and `requires_classification`.

Validation:

* JSONL parse passes.
* `logical_surface_count` is recorded.
* `sum(per-surface raw_occurrence_count) == raw_occurrence_total`.
* Mapping cardinality and duplicate counting rules are recorded.
* Every raw occurrence maps to at least one logical surface.
* Unmapped occurrence count is `0`.

---

### Change 4 - Evidence Collection / Authority Classification

Purpose:

Classify every logical surface into exactly one authority class using explicit evidence.

Files:

* `acquisition_lexical_surface_evidence_index.jsonl`
* `surface_evidence_summary.json`
* `acquisition_lexical_authority_matrix.md`
* `acquisition_lexical_classification_summary.json`
* `writer_reach_surface_index.json`
* `forbidden_writer_reach_report.md`
* `unclassified_blocked_surface_index.md`
* `blocked_surface_unblock_conditions.md`

Implementation Notes:

* Evidence should cover current pipeline call, import/execution path, writer reach, staging-only status, diagnostic/report-only status, test-only status, historical/provenance status, suppress relation, sealed decision relation, and current default path consumption.
* `current_authority_input` includes current data authority inputs, including sealed `facts.acquisition_hint`, when they are directly consumed by the current default compose path. This inclusion is classification evidence, not a claim that data content is changed.
* For tooling/code-surface branch decisions, data authority must be separately acknowledged so that Branch C cannot be read as denying sealed data authority.
* Current default compose authority is `compose_profiles_v2 + body_plan`. Legacy-only `sentence_plan`, predecessor-only plan artifacts, and diagnostic adapter paths must not be classified as current authority inputs unless current-default consumption is also proven.
* Classify each logical surface into exactly one of:
  * `current_authority_input`
  * `current_validator_or_gate_utility`
  * `staging_only_build_tool`
  * `diagnostic_or_report_only_tool`
  * `test_fixture`
  * `historical_artifact`
  * `stale_predecessor_plan`
  * `out_of_scope_closed_expansion_candidate`
  * `UNCLASSIFIED_BLOCKED`
* `current_authority_input` requires current-default writer/compose/validator/promotion path consumption, current contract input status, non-historical/non-staging provenance, and writer path reach.
* `current_validator_or_gate_utility` may fail-loud or validate the contract but must not be treated as an authority input.
* The authority matrix must include a glossary note that `current_validator_or_gate_utility` is distinct from suppress disposition labels `current_validator_surface` and `current_gate_surface`. The former classifies non-writer validator/gate utilities in the main authority taxonomy; the latter classify suppress-related surfaces only.
* `out_of_scope_closed_expansion_candidate` is a round-local classification for this audit. It records either prior sealed closure provenance or this-round out-of-scope status; it does not create a new permanent design closure by itself.
* `UNCLASSIFIED_BLOCKED` is used only when single-class evidence is insufficient.

Validation:

* Every logical surface has exactly one class.
* `classified_count + UNCLASSIFIED_BLOCKED_count == logical_surface_count`.
* Branch A closeout is forbidden unless `UNCLASSIFIED_BLOCKED_count = 0`.
* Authority class counts are recorded.
* Writer reach surfaces are listed.
* Forbidden writer reach count is recorded.
* Current default path consumption is verified for all surfaces classified as `current_authority_input`.
* Legacy-only surfaces are classified as non-current, diagnostic, historical, or stale predecessor as evidence supports.
* Mutation candidate count is `0`.
* Class mutual exclusivity is checked.

---

### Change 5 - Suppress Sense Disambiguation / Disposition / Closed Expansion Record

Purpose:

Separate `suppress` sense and dependency disposition from actual `suppress` retirement, and prevent out-of-scope expansion candidates from reopening during the audit.

Files:

* `suppress_dependency_disposition.json`
* `suppress_dependency_disposition.md`
* `suppress_followup_candidate_queue.md`
* `out_of_scope_closed_expansion_candidates.md`
* `closed_expansion_surface_summary.json`

Implementation Notes:

* Before disposition, split suppress occurrences by sense:
  * `publish_visibility_suppression`
  * `acquisition_lexical_plan_suppress_dependency`
  * `other_or_ambiguous_suppress_usage`
* Live publish visibility suppression must not be collapsed into stale acquisition lexical suppress plan evidence.
* Stale acquisition lexical suppress plan dependency must not be treated as a current gate unless current-default gate/validator reach is proven.
* Classify suppress surfaces into exactly one of:
  * `current_gate_surface`
  * `current_validator_surface`
  * `diagnostic_only`
  * `report_only`
  * `test_fixture`
  * `historical_artifact`
  * `stale_predecessor_plan`
  * `out_of_scope_for_this_round`
* If suppress reaches a current gate/validator, record a follow-up candidate only. Do not remove or retire it in this round.
* Record this-round out-of-scope or existing closure status for expansion candidates:
  * `josa_adaptive`
  * `phrasebook`
  * array acquisition
  * runtime-side repair
  * style linter hard gate promotion
  * acquisition contract expansion
  * runtime Korean language system
  * compose external repair/rewrite
* If a candidate has prior sealed closure, cite it as existing closure/provenance. If it lacks prior sealed closure evidence, record only `out_of_scope_for_this_round`; do not create a new permanent closure in this audit round.
* Out-of-scope expansion candidates must not be written as an automatic todo list.

Validation:

* Suppress sense split exists before suppress disposition.
* Live publish visibility suppression and stale acquisition lexical suppress dependency are counted separately.
* Every suppress surface has a disposition.
* `current_gate_surface_count`, `current_validator_surface_count`, and `stale_predecessor_plan_count` are recorded.
* Suppress-related mutation count is `0`.
* Runtime repair opening count is `0`.
* Contract expansion opening count is `0`.
* Out-of-scope candidates are not auto-queued.
* No new permanent design closure is claimed without prior sealed closure basis.

---

### Change 6 - Non-Mutation Verification / Staging Gate / Closeout Seal

Purpose:

Prove the round stayed within readpoint-audit scope, then select the evidence-matched closeout branch.

Files:

* `protected_surface_hash_before.json`
* `protected_surface_hash_after.json`
* `non_mutation_delta_report.md`
* `acquisition_lexical_staging_classification_report.md`
* `classification_hard_gate_result.md`
* `surface_count_axis_disambiguation.md`
* `acquisition_lexical_readpoint_audit_closeout.md`
* `followup_round_queue.md`
* `claim_boundary.md`
* Optional: `canon_readpoint_addendum.md`

Implementation Notes:

* Capture before/after hashes for protected surfaces, including facts source, decisions source, rendered output, runtime Lua, Lua bridge, packaged runtime payload, and state-axis files.
* Generate a staging report with universe count, classified count, blocked count, suppress disposition counts, writer reach, runtime reach, publish reach, and single-writer status.
* Keep surface count, quality count, coverage count, and completion count separate.
* A `follow-up blocker` means an unresolved evidence gap, unclassified surface, protected mutation, closure incompleteness, or claim conflict that prevents a branch from being evidence-bound. A separately recorded follow-up candidate is not a blocker unless the branch definition says it is.
* Choose exactly one closeout branch:
  * Branch A: `closed_with_acquisition_lexical_current_readpoint_inventory_sealed`
  * Branch B: `blocked_unknown_or_unclassified_surface`
  * Branch C: `closed_with_no_current_acquisition_lexical_tooling_code_surface_authority_found`
  * Branch D: `closed_with_followup_suppress_disposition_required`
* Branch precedence is:
  * Branch B first, if any unclassified surface, positive reachable-but-unindexed closure residue, protected mutation, or evidence gap blocks a complete branch.
  * Branch D second, if current gate/validator suppress reach exists and requires a separate suppress disposition follow-up, while no Branch B blocker remains.
  * Branch C third, if all surfaces are classified and no current acquisition lexical tooling/code-surface authority is found, while no Branch B or Branch D condition applies. Branch C does not deny sealed `facts.acquisition_hint` data authority, current compose consumption, or existing validators/gates; those must be listed separately.
  * Branch A last, if all surfaces are classified, closure completeness passes, suppress disposition is complete, protected mutation is `0`, and no follow-up blocker remains.
* Branch C is not allowed when `current_gate_surface_count > 0` or `current_validator_surface_count > 0` in suppress disposition. Those cases must choose Branch D unless Branch B applies.
* If non-suppress `current_validator_or_gate_utility` exists but no current tooling/code-surface authority input exists, Branch C remains available only when the closeout explicitly lists those validators/gates and preserves sealed data authority.
* Branch C closeout must include this fixed claim boundary text: `This branch means no current acquisition lexical tooling/code-surface authority input was found. It does not deny sealed data authority, current default compose consumption, or separately classified validator/gate utilities.`
* Closeout claim boundary must repeat that discovery completeness is claimed only relative to declared acquisition lexical anchors, writer-path/import-graph closure pass, and indexed corpus boundaries.
* If top-doc addendum is needed, write it only after staging report, hard gate, and review. It must be additive and claim-bounded.
* Optional canon addendum is not required for round success.

Validation:

* Protected source hash delta is `0`.
* Rendered/runtime/package hash delta is `0`.
* Facts/decisions mutation count is `0`.
* Runtime mutation count is `0`.
* `universe_count == classified_count + UNCLASSIFIED_BLOCKED_count`.
* Every surface has exactly one class.
* Grep/rg anchors are reproducible.
* `writer_path_reachable_but_unindexed_count == 0` is required for Branch A.
* Branch C scope validation confirms sealed `facts.acquisition_hint` data authority and current compose consumption are not denied.
* Suppress sense disambiguation is complete before suppress branch selection.
* Single-writer violation count is `0`.
* No-inheritance violation count is `0`.
* Closeout branch matches evidence counts.
* Release/deployment/runtime validation is not claimed.

---

## 7. Validation Plan

### Automated Validation

Execution must record the exact commands and exit codes used. Suggested validation areas:

* `rg` or equivalent search replay for vocabulary anchors.
* Writer-path / import-graph closure replay from known acquisition lexical anchors.
* Current-default-path consumption validation for `compose_profiles_v2 + body_plan`.
* JSON / JSONL parse validation for all inventory, grouping, evidence, classification, suppress disposition, and summary artifacts.
* Count invariant checks:
  * `sum(per-surface raw_occurrence_count) == raw_occurrence_total`
  * `unmapped_occurrence_count == 0`
  * `writer_path_reachable_but_unindexed_count == 0` for Branch A
  * `classified_count + UNCLASSIFIED_BLOCKED_count == logical_surface_count`
  * every logical surface has exactly one class
  * every raw-to-surface mapping has explicit cardinality
  * every suppress occurrence has a sense assignment
  * every suppress surface has exactly one disposition
* Mutual exclusivity checks for authority classes.
* Single-writer preservation checks.
* No-inheritance checks for staging/historical/provenance artifacts.
* Protected surface before/after hash comparison.
* Audit-root exclusion check confirming the round-local audit root is outside protected hash manifests and build/package derivation.
* Branch C scope check confirming it does not deny sealed `facts.acquisition_hint` data authority or current compose consumption.
* `git diff --stat` and `git diff` review to confirm only allowed plan/audit artifacts changed.
* If Lua files are touched accidentally or by approved separate work, run `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`; this plan expects no Lua touch.
* If Python helper scripts are introduced, run the exact relevant Python parse/test commands and record exit code `0`; otherwise report script validation as not applicable.
* Any helper script used to generate inventory/classification artifacts must be replayable and must report deterministic output, or explicitly explain non-deterministic fields.

### Manual Validation

* Review `acquisition_lexical_authority_matrix.md` for class evidence quality.
* Review `suppress_dependency_disposition.md` for removal-free disposition language.
* Review suppress sense split to ensure live publish visibility suppression is not collapsed into stale acquisition lexical plan dependency.
* Review `out_of_scope_closed_expansion_candidates.md` to ensure closed candidates are not framed as same-round todos.
* Review candidate wording to ensure prior sealed closure is distinguished from `out_of_scope_for_this_round`.
* Review `surface_count_axis_disambiguation.md` to ensure surface counts are not confused with quality, coverage, or completion counts.
* Review `claim_boundary.md` to ensure no runtime rollout, public exposure, release readiness, or suppress retirement claim is implied.
* Review closeout branch decision tree and confirm exactly one branch is selected.

### Validation Limits

This execution will not perform:

* Runtime behavior validation.
* Multiplayer validation.
* Deployment validation.
* Long-session runtime validation.
* Manual in-game validation.
* External ecosystem compatibility sweep.
* Rendered text rebaseline.
* Lua package rollout.
* Release readiness validation.
* Workshop readiness validation.
* Acquisition lexical quality improvement validation.
* Suppress retirement execution validation.
* Dead-surface removal validation.
* Coverage, quality, or completion remeasurement.
* Discovery completeness beyond the bounded writer-path / import-graph closure inputs. If closure inputs are later found incomplete, the closeout must be superseded by a successor inventory round rather than silently upgraded.

---

## 8. Risk Surface Touch

### Authority Surface

Additive readpoint authority only. Existing current authority inputs, validators, writer paths, and sealed artifacts are classified but not changed. Sealed data authority such as `facts.acquisition_hint` and current default compose consumption remain preserved; Branch C is limited to tooling/code-surface authority absence.

### Runtime Behavior Surface

None. Runtime consumer, Browser, Wiki, Tooltip, Lua payload, and packaged Lua chunks are not changed.

### Compatibility Surface

No direct compatibility mutation. The readpoint may reduce future compatibility risk by preventing stale plans, staging artifacts, or runtime-side repair candidates from being mistaken for current openings.

### Sealed Artifact Surface

Existing sealed artifacts are not modified. They may be classified as historical artifact, provenance artifact, diagnostic/report-only artifact, or stale predecessor plan.
Existing closure records for expansion candidates may be cited, but this round does not create new permanent design closures for candidates that lack prior sealed basis.

### Public-Facing Output Surface

None. User-facing sentences, tooltip output, browser display, wiki display, and rendered runtime text are not changed.

---

## 9. Risk Analysis

### Architecture Risk

* Historical or staging artifact could be promoted accidentally to current authority input.
* Validator/gate utility could be confused with writer authority input.
* Sealed acquisition data authority could be denied accidentally by an overbroad Branch C claim.
* Legacy-only `sentence_plan` consumption could be misread as current default authority.
* Closed expansion candidates could be reopened under lexical cleanup language.
* This-round out-of-scope candidates could be overstated as newly permanent design closures.
* Stale predecessor plans could be interpreted as current execution openings.

### Runtime Risk

* Runtime risk should remain none if protected mutation gates hold.
* Runtime risk appears only if rendered text, runtime Lua, Lua bridge, or packaged payload changes despite the non-mutation scope.

### Compatibility Risk

* Compatibility risk is low if the round remains readpoint-only.
* Compatibility risk rises if runtime-side repair, josa processing, phrasebook, or contract expansion is introduced without a separate design round.

### Regression Risk

* Surface universe may be incomplete if the vocabulary is too narrow.
* Writer-path / import-graph closure inputs may be incomplete if known anchors are incomplete.
* Search vocabulary may over-capture unrelated lexical tools if too broad.
* Raw occurrence count may be confused with logical surface count.
* Test expected strings may be misread as current contract evidence.
* Diagnostic/report outputs may be misread as publish candidates.
* Live publish visibility suppression may be confused with stale acquisition lexical suppress-plan dependency.
* `UNCLASSIFIED_BLOCKED` residue may be hidden by speculative classification.
* Closeout claims may exceed the readpoint seal boundary.

---

## 10. Rollback Plan

Because this is a non-mutation / additive readpoint round, rollback is mostly artifact and claim correction.

* If protected source, facts, decisions, rendered, runtime, bridge, package, or state surfaces change, revert those changes immediately.
* If a `suppress` retirement patch is included, remove it and mark the round failed or out-of-scope.
* If validator or utility rewrite is included, remove it unless a separate approved implementation round exists.
* If stale plans or historical artifacts are physically deleted, restore them.
* If audit artifacts are created under runtime package roots, move them to the round-local staging/report root or remove them.
* If audit artifacts are included in protected hash manifests or build/package derivation, exclude the audit root and rerun non-mutation verification before closeout.
* If closeout implies release readiness, runtime validation, public exposure, or deployment, correct the claim boundary.
* If Branch C wording denies sealed `facts.acquisition_hint` data authority, current compose consumption, or existing validators/gates, correct Branch C wording before closeout.
* If `UNCLASSIFIED_BLOCKED` residue exists but the closeout chooses Branch A, change the closeout to Branch B or rerun classification after obtaining evidence.
* If `writer_path_reachable_but_unindexed_count > 0` but Branch A is selected, change the closeout to Branch B or extend the universe and rerun closure validation.
* If top-doc addendum overclaims, correct with an additive successor/supersession instead of rewriting predecessor evidence silently.
* If classification is later found wrong, preserve the existing readpoint as historical predecessor and open a successor inventory/classification round.

---

## 11. Governance Constraints

Must preserve:

* `docs/Philosophy.md` compliance.
* Hub & Spoke / SPI boundary preservation.
* Iris evidence-bound / structure-only principles.
* Build-time / runtime separation.
* FAIL-LOUD preservation.
* Compatibility preservation.
* Authority ownership preservation.
* Current authority and historical/provenance surface separation.
* Sealed acquisition data authority preservation, including `facts.acquisition_hint` and current default compose consumption.
* Current default compose path basis: `compose_profiles_v2 + body_plan`; legacy-only consumption is not enough for current authority classification.
* No-inheritance principle: prior staging artifacts and closeout evidence must not be inherited directly as current function evidence.
* Style linter advisory-only status.
* Runtime consumer repair prohibition.
* Facts-only or decisions-only acquisition reopening prohibition.
* Stale predecessor plan promotion prohibition.
* `suppress` retirement prohibition in this round.
* Suppress sense separation before disposition; live publish visibility suppression must not be collapsed into stale acquisition lexical plan suppress dependency.
* Acquisition lexical contract expansion prohibition.
* `josa_adaptive`, `phrasebook`, array acquisition, and runtime-side repair reopening prohibition.
* Existing closure record and this-round out-of-scope status must be distinguished; no new permanent design closure without prior sealed basis.
* Facts, decisions, rendered, runtime Lua, Lua bridge, packaged runtime, `quality_state`, `publish_state`, and `runtime_state` non-mutation.
* Release readiness, Workshop readiness, and deployed closeout non-claim.
* Additive-only canon readpoint behavior after staging-first / hard gate / review.

---

## 12. Expected Closeout State

Expected closeout target is `complete` only if the evidence supports Branch A, Branch C, or Branch D:

```text
closed_with_acquisition_lexical_current_readpoint_inventory_sealed
closed_with_no_current_acquisition_lexical_tooling_code_surface_authority_found
closed_with_followup_suppress_disposition_required
```

Branch selection must follow this precedence:

```text
B(blocked) > D(suppress current gate/validator follow-up required) > C(no current tooling/code-surface authority) > A(full sealed readpoint)
```

Branch A is allowed only when:

* Every logical surface is classified.
* `UNCLASSIFIED_BLOCKED_count = 0`.
* `writer_path_reachable_but_unindexed_count = 0`.
* Current default path consumption has been validated against `compose_profiles_v2 + body_plan`.
* Suppress disposition is complete.
* Suppress sense disambiguation is complete.
* Protected mutation count is `0`.
* No follow-up blocker remains.

Branch C is allowed when acquisition lexical related surfaces exist, but no current acquisition lexical tooling/code-surface authority input is found. If any `current_authority_input` rows exist, they must be limited to preserved data authority such as sealed `facts.acquisition_hint` and must not be tooling/code-surface authority. All other surfaces must be classified as historical, staging, diagnostic/report-only, test, stale plan, validator/gate utility, or out-of-scope existing closure/candidate surfaces.

Branch C is not allowed when `current_gate_surface_count > 0` or `current_validator_surface_count > 0` in suppress disposition. Those cases must close through Branch D unless Branch B applies.

Branch C must explicitly state that:

```text
This branch means no current acquisition lexical tooling/code-surface authority input was found.
It does not deny sealed data authority, current default compose consumption,
or separately classified validator/gate utilities.
```

* It does not deny sealed `facts.acquisition_hint` data authority.
* It does not deny current default compose consumption of preserved data authority.
* It does not deny existing current validator/gate utilities if they are classified separately.
* It is not a claim that acquisition lexical has no current data authority.

All complete closeout branches must state that discovery completeness is claimed only relative to the declared acquisition lexical anchors, writer-path/import-graph closure pass, and indexed corpus boundaries.

Branch D is allowed when suppress reaches a current gate or validator and follow-up suppress disposition is required, while this round still performs no suppress retirement.

Expected closeout target is `blocked` if Branch B applies:

```text
blocked_unknown_or_unclassified_surface
```

Branch B applies when inventory exists but one or more surfaces cannot be assigned a single authority class with available evidence. In that case, the closeout must carry `UNCLASSIFIED_BLOCKED` residue, missing evidence, unblock conditions, and follow-up round requirements.

Branch B also applies when:

* `writer_path_reachable_but_unindexed_count > 0`.
* Branch C would deny sealed acquisition data authority or current compose consumption.
* Audit-root/protected-hash separation cannot be proven.
* Protected mutation count is non-zero.
* Suppress sense cannot be separated enough to choose a branch.

The closeout must not claim:

* Acquisition lexical function improvement.
* Suppress retirement.
* Acquisition lexical contract expansion.
* Validator rewrite.
* Utility rewrite.
* Rendered text improvement.
* Runtime Lua regeneration.
* Deployed runtime equivalence.
* Manual in-game validation pass.
* Full compatibility preservation.
* Release readiness.
* Workshop readiness.
* Production validation.
* Dead/historical surface removal.
* Coverage, quality, or completion measurement.
* Candidate state, active/silent, or adopted/unadopted reclassification.
