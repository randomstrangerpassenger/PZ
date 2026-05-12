# ROADMAP_TEMPLATE.md

## 1. Problem Statement

Describe the core problem this roadmap is intended to solve.

Include:

* current limitation
* operational pain point
* architectural pressure
* workflow bottleneck
* validation or governance concern

---

## 2. Current State

Describe the current ecosystem or module state.

Include relevant:

* existing implementation state
* known limitations
* existing constraints
* sealed decisions
* active dependencies
* current validation confidence

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

Avoid implementation detail.

---

## 4. Constraints

List constraints that must remain preserved.

Examples:

* Philosophy.md compliance
* Hub & Spoke preservation
* SPI preservation
* runtime/build-time separation
* FAIL-LOUD preservation
* compatibility preservation
* authority ownership preservation
* Pulse must not depend on submods

---

## 5. Non-Goals

List work intentionally excluded from this roadmap.

Examples:

* unrelated refactor
* architecture redesign
* release strategy changes
* migration outside approved scope
* optimization outside target area

---

## 6. Proposed Approach

Describe the high-level strategy.

Focus on:

* direction
* sequencing
* decomposition
* risk reduction
* validation strategy

Avoid low-level implementation detail.

---

## 7. Authority / Surface Impact

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

---

## 9. Validation Expectations

### Expected Validation Depth

* lightweight
* standard
* heavy

### Expected Validation Areas

* runtime
* compatibility
* determinism
* migration
* regression
* public-facing behavior

### Known Validation Limits

List validation that is not expected during this roadmap.

Examples:

* no multiplayer validation
* no deployment validation
* no long-session runtime validation
* no external ecosystem compatibility sweep

---

## 10. Risk Assessment

### High Risk

*

### Medium Risk

*

### Low Risk

*

---

## 11. Rollback Strategy

Describe how roadmap execution can be reverted or contained if major regressions or invalid assumptions appear.

---

## 12. Success Criteria

Describe the conditions required for roadmap success.

Examples:

* determinism preserved
* no major regression
* validation completed
* runtime parity preserved
* compatibility maintained
* workflow simplification achieved

---

## 13. Expected Claim Boundary

This roadmap does NOT automatically imply:

* full runtime equivalence
* full compatibility preservation
* release readiness
* deployment readiness
* production validation
* architectural correctness

unless explicitly validated later.

Do not claim success beyond validated scope.
