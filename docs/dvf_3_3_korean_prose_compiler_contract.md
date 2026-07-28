# DVF 3-3 Korean Prose Compiler Contract

DVF Korean prose compiler는 approved source proposition과 body-plan requirement를 분리해 읽고, deterministic discourse/realization을 수행하는 staging-only compiler다.

```text
approved source fields -> source proposition inventory
profile/body_plan -> structural requirement inventory
both inventories + realization policy -> clause trace + candidate body
```

각 proposition은 exact item ID, role, source path/field/value hash, origin, modality, qualifier, condition, semantic key와 emission eligibility를 가진다. 각 clause는 proposition IDs, relation, ordering/merge/suppression reason, paragraph ID, realization rule과 transformation IDs를 가진다.

candidate에서 `required=true`인 structural role의 상태는 `emitted_direct`, `satisfied_by_verified_fusion`, `satisfied_by_verified_suppression`, `missing` 중 하나다. optional 또는 emission-ineligible role만 `not_required`를 쓸 수 있다. fusion/suppression은 typed equivalence proof 없이 PASS가 될 수 없다.

Profile의 `required_sections`와 candidate의 source-bound applicability는 별도 필드로 보존한다. Profile-required role에 approved source proposition이 없고 approved derivation도 없으면 `profile_required=true`, `required=false`, `optional=true`, `candidate_applicability=owner_approved_source_absence_exclusion`으로 분류한다. 이 분류는 `body_plan_applicability_approval.json`의 exact hash와 `source_bound_profile_role_applicability_v1`에 결속하며 source proposition을 만들거나 current profile/source authority를 수정하지 않는다. Approved primary-use proposition에서 context가 파생되는 경우에는 `required=true`를 유지하고 typed fusion proof를 요구한다. 따라서 ledger에서 `required=true`인 row에 `not_required`를 사용하는 금지는 그대로 유지된다.

Candidate API는 다음을 모두 요구한다.

- `compose_context=staging`
- exact policy hash
- Phase 2 source proposition inventory
- Phase 2 body-plan requirement inventory
- attempt-local rendered/trace/evidence paths

Default composer는 candidate policy나 candidate output을 읽지 않는다. Candidate path는 current rendered, Lua bridge, runtime chunks와 package path를 거부한다.

`DVF Body Compiler PASS`의 네 구성요소는 determinism, body-plan application, rendered shape, source-provenance preservation이며 서로 대체하지 않는다. Publish acceptance, Registry authority/runtime compatibility, current adoption과 release authorization은 이 contract의 claim이 아니다.
