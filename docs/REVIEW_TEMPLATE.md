# REVIEW_TEMPLATE.md

## Review Basis

Review the roadmap or plan together with `Philosophy.md`, `EXECUTION_CONTRACT.md`, applicable sealed decisions, and task-relevant authority documents.

Apply each authority within its own declared scope and authority position. In particular, apply `EXECUTION_CONTRACT.md` as the shared authority for ecosystem-wide disclosure, evidence, and closeout obligations; do not treat it as a general implementation, testing, tooling, or execution-method policy.

Do not evaluate the target document as if it must restate every inherited requirement.

A requirement already guaranteed by an applicable authority remains binding even when it is not repeated in the roadmap or plan.

Do not treat an inherited requirement's omission as a defect unless:

* the target document conflicts with it
* the target document creates material ambiguity about its application
* its task-specific consequence must be explicit to define scope, sequencing, correctness, validation, or a claim

Do not request duplication merely to make the roadmap or plan self-contained.

Keep the review focused on new findings. Do not restate sound sections except where necessary to explain the verdict or a finding.

---

## 1. Verdict

PASS / WARN / FAIL

---

## 2. Executive Summary

Summarize the overall evaluation of the roadmap or plan.

Include:

* current execution readiness
* primary strengths
* primary risks
* whether execution should proceed

Keep this concise. Do not reproduce the target document section by section.

---

## 3. Critical Issues

List only issues that must be resolved before execution or PASS approval after applicable inherited authorities are taken into account.

The absence of text that merely duplicates an inherited requirement is not a Critical issue.

### Issue

Severity:

Impact:

Affected Scope:

Related Surface:

* Authority Surface
* Runtime Behavior Surface
* Compatibility Surface
* Sealed Artifact Surface
* Public-Facing Output Surface

Required Fix:

Blocking Reason:

---

(Repeat as needed)

---

## 4. Non-Critical Issues

List recommended improvements that are not blocking approval.

Examples:

* readability improvement
* task-specific validation strengthening
* implementation simplification
* documentation clarification
* current-scope maintainability concern

Do not use this section to request redundant restatement of inherited requirements.

---

## 5. Scope Review

### Scope Drift

Does the roadmap or plan expand beyond:

* approved roadmap
* approved architecture direction
* applicable module or ecosystem authority
* declared task-specific execution boundary
* approved implementation scope

Do not require an inherited boundary to be copied into the target document unless its task-specific consequence must be explicit.

### Missing Scope

Are there missing task-specific:

* implementation areas
* dependency considerations
* migration considerations
* validation considerations
* rollback or containment considerations

Do not count requirements already supplied by applicable inherited authorities as missing scope.

### Explicitly Out Of Scope Consistency

Does the declared out-of-scope boundary remain internally consistent with inherited authorities and the approved task scope?

---

## 6. Validation Review

Evaluate whether the task-specific validation in the roadmap or plan is sufficient to support its claims and gates.

Apply the evidence and validation-ceiling obligations inherited from `EXECUTION_CONTRACT.md`; do not require those obligations to be copied into the target document.

### Missing Validation

List task-specific validation required for a current claim or gate that is absent from the combined authority + roadmap/plan basis.

### Weak Validation

List task-specific validation that exists but is insufficient for the associated claim.

### Validation Ceiling Risk

Does the roadmap or plan risk making claims beyond validated scope?

Examples:

* runtime claims without runtime validation
* compatibility claims without compatibility testing
* behavior-preserving claims without equivalence evidence
* deployment claims without deployment validation
* release-readiness claims without end-to-end validation

### Validation Practicality

Is the proposed task-specific validation:

* realistically executable
* proportionate to risk surface
* appropriately scoped
* free from unnecessary ceremony

Do not invent additional validation solely to increase confidence when the governing authorities and task-specific claims do not require it.

---

## 7. Governance Review

Evaluate governance against the combined applicable authority set rather than requiring every governing rule to be restated in the target document.

### Philosophy.md Compliance

Any conflict with constitutional principles?

### Architecture Boundary

Any unauthorized architecture expansion, dependency violation, or ownership blur?

### Runtime / Build-Time Separation

Any task-specific change that improperly mixes responsibilities?

### FAIL-LOUD Preservation

Any task-specific change that introduces silent fallback or hidden degradation risk?

### Authority Ownership

Does the roadmap or plan bypass, weaken, or ambiguously change existing ownership boundaries?

### Contract Compliance

Within its declared scope, does the roadmap or plan conflict with `EXECUTION_CONTRACT.md` disclosure, evidence, or closeout obligations?

Also check for conflicts with:

* module authority documents
* approved constraints
* existing sealed decisions

Absence of duplicated inherited language is not non-compliance.

---

## 8. Risk Surface Review

Report only surfaces changed, exposed, or made uncertain by the roadmap or plan.

### Authority Surface

None / concerns

### Runtime Behavior Surface

None / concerns

### Compatibility Surface

None / concerns

### Sealed Artifact Surface

None / concerns

### Public-Facing Output Surface

None / concerns

---

## 9. Risk Review

List task-specific risks or inherited risks whose exposure is materially changed by this roadmap or plan.

### Regression Risk

*

### Compatibility Risk

*

### Operational Risk

*

### Validation Risk

*

### Governance Risk

*

Do not restate unchanged ecosystem-wide risks as findings.

---

## 10. Required Revisions

List only revisions actually required before PASS approval.

Each revision should:

* identify the affected section
* explain why the combined authority + roadmap/plan basis is insufficient or conflicting
* describe the minimum acceptable correction

Do not require the target document to copy text already guaranteed by an inherited authority.

---

## 11. Final Recommendation

State the final recommendation clearly.

Examples:

* PASS
* PASS with minor revisions
* WARN
* FAIL

If not PASS:

* explain why
* identify blocking conditions
* identify required next actions

---

## 12. Reviewer Notes

Optional reviewer observations.

Use this section only for:

* additional context
* future follow-up suggestions
* uncertainty disclosure
* review limitations

Do not introduce new governance policy, architecture direction, roadmap scope, or inherited-policy duplication in this section.
