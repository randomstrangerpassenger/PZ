\# REVIEW\_TEMPLATE.md



\## 1. Verdict



PASS / WARN / FAIL



\---



\## 2. Executive Summary



Summarize the overall evaluation of the plan.



Include:



\* current execution readiness

\* primary strengths

\* primary risks

\* whether execution should proceed



\---



\## 3. Critical Issues



List issues that must be resolved before execution or PASS approval.



\### Issue



Severity:



Impact:



Affected Scope:



Related Surface:



\* Authority Surface

\* Runtime Behavior Surface

\* Compatibility Surface

\* Sealed Artifact Surface

\* Public-Facing Output Surface



Required Fix:



Blocking Reason:



\---



(Repeat as needed)



\---



\## 4. Non-Critical Issues



List recommended improvements that are not blocking approval.



Examples:



\* readability improvement

\* validation strengthening

\* implementation simplification

\* documentation clarification

\* future maintainability concern



\---



\## 5. Scope Review



\### Scope Drift



Does the plan expand beyond:



\* approved roadmap

\* approved architecture direction

\* declared execution boundary

\* approved implementation scope



\### Missing Scope



Are there missing:



\* implementation areas

\* dependency considerations

\* migration considerations

\* validation considerations

\* rollback considerations



\### Explicitly Out Of Scope Consistency



Does the declared out-of-scope boundary remain internally consistent?



\---



\## 6. Validation Review



\### Missing Validation



List validation that is entirely absent.



\### Weak Validation



List validation that exists but is insufficient for the associated claim.



\### Validation Ceiling Risk



Does the plan risk making claims beyond validated scope?



Examples:



\* runtime claims without runtime validation

\* compatibility claims without compatibility testing

\* behavior-preserving claims without equivalence evidence

\* deployment claims without deployment validation

\* release-readiness claims without end-to-end validation



\### Validation Practicality



Is the proposed validation:



\* realistically executable

\* proportionate to risk surface

\* appropriately scoped

\* free from unnecessary ceremony



\---



\## 7. Governance Review



\### Philosophy.md Compliance



Any conflict with constitutional principles?



\### Architecture Boundary



Any unauthorized architecture expansion, dependency violation, or ownership blur?



\### Runtime / Build-Time Separation



Any mixing of responsibilities?



\### FAIL-LOUD Preservation



Any silent fallback or hidden degradation risk?



\### Authority Ownership



Does the plan bypass or weaken existing ownership boundaries?



\### Contract Compliance



Does the plan conflict with:



\* EXECUTION\_CONTRACT.md

\* module authority documents

\* approved constraints

\* existing sealed decisions



\---



\## 8. Risk Surface Review



\### Authority Surface



None / concerns



\### Runtime Behavior Surface



None / concerns



\### Compatibility Surface



None / concerns



\### Sealed Artifact Surface



None / concerns



\### Public-Facing Output Surface



None / concerns



\---



\## 9. Risk Review



\### Regression Risk



\*



\### Compatibility Risk



\*



\### Operational Risk



\*



\### Validation Risk



\*



\### Governance Risk



\*



\---



\## 10. Required Revisions



List revisions required before PASS approval.



Each revision should:



\* identify the affected section

\* explain why revision is required

\* describe the minimum acceptable correction



\---



\## 11. Final Recommendation



State the final recommendation clearly.



Examples:



\* PASS

\* PASS with minor revisions

\* WARN

\* FAIL



If not PASS:



\* explain why

\* identify blocking conditions

\* identify required next actions



\---



\## 12. Reviewer Notes



Optional reviewer observations.



Use this section only for:



\* additional context

\* future follow-up suggestions

\* uncertainty disclosure

\* review limitations



Do not introduce new governance policy, architecture direction, or roadmap scope in this section.



