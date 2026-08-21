# ROADMAP_TEMPLATE.md

## Template Use Rule

This template assumes the author has already read `Philosophy.md`, `EXECUTION_CONTRACT.md`, and the task-relevant ecosystem authority documents.

Apply `EXECUTION_CONTRACT.md` only within its declared scope and authority position: ecosystem-wide disclosure, evidence, and closeout obligations.

Do not restate inherited requirements that are already binding through applicable authorities.

Include an inherited requirement only when:

* its task-specific consequence must be made explicit
* it is necessary to define scope, sequencing, correctness, validation, or a claim boundary

An inherited requirement remains binding even when it is not repeated in this roadmap.

---

## 1. Problem Statement

Describe the core problem this roadmap is intended to solve.

Include relevant:

* current limitation
* operational pain point
* architectural pressure
* workflow bottleneck
* task-specific validation or governance concern

Do not use this section to restate inherited requirements.

---

## 2. Current State

Describe the current ecosystem or module state relevant to the problem.

Include relevant:

* existing implementation state
* known limitations
* task-relevant constraints
* sealed decisions
* active dependencies
* current validation confidence

Reference inherited authority by document or decision when useful; do not reproduce it unless its task-specific effect matters here.

---

## 3. Desired Outcome

Describe the intended end state after the roadmap is completed.

Focus on:

* expected capability improvement
* workflow improvement
* stability improvement
* governance improvement
* validation improvement
* architectural clarity

Avoid implementation detail and generic compliance statements.

---

## 4. Constraints

List only constraints that are specific to this roadmap, or inherited constraints whose concrete effect on this task must be explicit.

Do not duplicate requirements already guaranteed by applicable authority documents, including `EXECUTION_CONTRACT.md` within its declared scope.

Examples:

* a named authority must remain the sole owner of a specific surface
* migration must not begin before a task-specific gate is satisfied
* a compatibility surface affected by this roadmap must remain unchanged
* a sealed artifact or decision relevant to this task must not be modified
* a task-specific boundary inherited from an applicable authority materially constrains execution

---

## 5. Non-Goals

List work intentionally excluded from this roadmap.

Examples:

* unrelated refactor
* architecture redesign outside the approved direction
* release strategy changes
* migration outside approved scope
* optimization outside the target area

Do not repeat exclusions that already apply through inherited authority unless they materially define this roadmap's boundary.

---

## 6. Proposed Approach

Describe the high-level strategy.

Focus on:

* direction
* sequencing
* decomposition
* risk reduction
* task-specific validation strategy

Avoid low-level implementation detail and inherited requirements that do not need task-specific restatement.

---

## 7. Authority / Surface Impact

Describe only surfaces materially affected by this roadmap.

### Authority Surface

None / describe

### Runtime Behavior Surface

None / describe

### Compatibility Surface

None / describe

### Sealed Artifact Surface

None / describe

### Public-Facing Output Surface

None / describe

---

## 8. Phases

### Phase 1 — <name>

Goal:

Primary Changes:

Expected Risks:

Expected Validation:

Expected Deliverables:

---

### Phase 2 — <name>

Goal:

Primary Changes:

Expected Risks:

Expected Validation:

Expected Deliverables:

---

(Repeat as needed)

For `Expected Validation`, name validation specific to the phase or necessary to support a task-specific claim or gate.

Do not restate inherited evidence or closeout obligations merely to make the roadmap self-contained.

---

## 9. Validation Expectations

Describe the validation needed to support this roadmap's task-specific claims and gates.

Apply inherited evidence and validation-ceiling obligations from `EXECUTION_CONTRACT.md` without reproducing them unless their task-specific consequence must be explicit.

If the roadmap requires a validation checkpoint at a specific phase boundary, state it explicitly here or in the relevant phase.

### Expected Validation Depth

* lightweight
* standard
* heavy

### Expected Validation Areas

Select only applicable areas:

* runtime
* compatibility
* determinism
* migration
* regression
* public-facing behavior

### Known Validation Limits

List task-specific validation that is intentionally not expected and that materially limits what may be claimed.

Do not add generic non-claims merely as boilerplate.

---

## 10. Risk Assessment

List risks created or materially changed by this roadmap.

Do not repeat generic ecosystem risks that are unchanged by the task.

### High Risk

*

### Medium Risk

*

### Low Risk

*

---

## 11. Rollback Strategy

Describe the task-specific rollback, containment, or stop condition needed if major regressions or invalid assumptions appear.

If applicable inherited authority already defines everything needed and this roadmap adds nothing task-specific, state that no additional task-specific rollback rule is required rather than reproducing the inherited requirement.

---

## 12. Success Criteria

Describe concrete conditions required for roadmap success.

Success criteria should be task-specific, observable, and supportable by the planned validation.

Examples:

* the intended authority transition is completed without mixed ownership
* the target workflow no longer requires the identified redundant step
* the affected runtime behavior matches the explicitly defined expected state
* the task-specific compatibility boundary remains satisfied
* the required validation gates pass

Do not use generic compliance with inherited requirements as a substitute for task-specific success criteria.

---

## 13. Expected Claim Boundary

State only claim boundaries that are specific to this roadmap and materially follow from its validation limits.

Apply the claim-evidence and validation-ceiling obligations inherited from `EXECUTION_CONTRACT.md` without restating generic contract language.

Do not repeat generic disclaimers merely as boilerplate.

Each positive claim must remain within the evidence planned by this roadmap.
