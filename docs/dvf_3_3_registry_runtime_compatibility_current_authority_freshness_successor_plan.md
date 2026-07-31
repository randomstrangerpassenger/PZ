# Implementation Plan

> 상태: owner-directed attribution-gated conditional plan / Change 1 discovery preserved / Changes 2–8 not applicable unless a canonical Iris RTC defect is independently reproduced without temporary orchestration
> 작성일: 2026-07-30
> 최종 개정일: 2026-08-01
> 대상 축: Iris Artifact Registry / Registry Runtime Compatibility
> Roadmap candidate: `iris_registry_runtime_compatibility_current_authority_freshness_successor_authority_reconstruction`
> Roadmap input: `C:/Users/MW/.codex/attachments/f741c537-ce33-47fc-af83-3111322439f1/pasted-text.txt`
> Roadmap input SHA-256: `de1168b6704c97056a5072b638b47e8fb490ddf6e528203b9b4d24fa925fab88`
> Prior review input: `C:/Users/MW/.codex/attachments/8623502f-2413-4fb6-af1f-2b14068ce897/pasted-text.txt`
> Prior review input SHA-256: `068121b5e194d40e87e4108b1096b5bb5cbbddf9ce346e0447b2896e24405a91`
> Second review input: `C:/Users/MW/.codex/attachments/ab8c0288-2e97-472a-8e7e-1ae3b74c8edb/pasted-text.txt`
> Second review input SHA-256: `2b335975f54c40660066760920709edb183bb28052a4e751ac9afd7fd68b7d14`
> Prior synthesis review input: `C:/Users/MW/.codex/attachments/6528d9ff-9a7e-4aea-b824-6fa16f0eaf21/pasted-text.txt`
> Prior synthesis review input SHA-256: `4c9b57c042ccbb058075e7664a42b5ed01d3c2c119c99b2145ffc7c6d707bba4`
> Latest synthesis review input: `C:/Users/MW/.codex/attachments/c4874484-2592-49d7-8150-d8b7ec989cb8/pasted-text.txt`
> Latest synthesis review input SHA-256: `dd8da21e153b1f21359f79ab8c54c63d3f400cfc4343f41bef8c76d3cb61465d`
> Latest inline review findings: `RTCF-I05`, `CLD-RTCS-N25`, `CLD-RTCS-N26`, `CLD-RTCS-N27`
> Current-lineage synthesis review input: `C:/Users/MW/.codex/attachments/f53a487d-b5ed-4a1f-a4dc-444c61c3bb07/pasted-text.txt`
> Current-lineage synthesis review input SHA-256: `2d641f2bbf8fba12cbe5622ab50a388bd1783bcf86c347f8d1c4dd95cef7fdc6`
> Current-lineage review target predecessor plan SHA-256: `17cef66daa4cce8d80b58c379fcb4e0725428908051f4563166cc48d97c3df68`
> Current-lineage review findings: `SYN-RTCS-C01`, `SYN-RTCS-C02`, `SYN-RTCS-C03`, `SYN-RTCS-I01`, `SYN-RTCS-N01`
> Near-convergence review input: `C:/Users/MW/.codex/attachments/f2fc8c08-b610-42f7-a2e9-53eb72d8d0a0/pasted-text.txt`
> Near-convergence review input SHA-256: `caa8017894c43535b0d3cb257348b4c1df5d166b0c05726e38d6546adee2ae6b`
> Near-convergence review target predecessor plan SHA-256: `2918ae21f87667c4a7932dcfe9d63c44d56688e61eab34cd77051c281033dc01`
> Near-convergence review findings: `SYN-RTCS-C01` (`CLD-RTCS-C19`), `SYN-RTCS-N01` (`CLD-RTCS-N29`)
> Latest non-blocking inline finding: `M-01` — plan-review severity taxonomy / `REVIEW_TEMPLATE.md` section mapping
> Template: `docs/PLAN_TEMPLATE.md`
> 조건부 historical 최대 claim: 아래 canonical defect attribution gate가 먼저 PASS한 미래 실행에서만, exact Registry current-authority reference set와 canonical runtime failure를 결속한 `Registry Runtime Compatibility PASS`를 고려할 수 있다. 현재 claim은 `not_applicable_unproven_iris_defect`다.

이 문서는 구현 결과나 PASS 증거가 아니다. 계획 작성 시점의 코드베이스 관찰값, 첨부 로드맵, staging, environment와 predecessor bundle은 current source authority를 선택하거나 Iris RTC 결함을 선언할 권한이 없다. 현재는 아래 attribution predicate를 만족하는 canonical failure가 없으므로 Change 2 이후 실행은 열리지 않는다. 뒤의 finalized G4/G5 handoff 기반 실행 설계는 predicate가 PASS한 미래 경우를 위한 historical design이며 현재 prerequisite가 아니다.

---

## 0. Current Executable Scope — Canonical Defect Attribution Gate

이 절은 이 문서에서 유일한 current executable synchronization authority다. 뒤의 finalized G4/G5 terminal prerequisite, RTC reservation/adoption, Changes 2~8, review/seal/terminal 조항은 설계 이력으로 보존하며 이 attribution gate가 PASS하기 전에는 실행하지 않는다.

동기화 기준점:

- commit: `7744df68fa7c0a66ccd9e760995c1b7071de8e08`
- tree: `5c6fd5d2df505c9ea217e6b913bfacf296e99a63`
- live required-validation manifest SHA-256: `2ccf98edfd087bb193387a77d0fec5bdb3a1efe9905d66fa9ac5ae74eec2c7d1`
- live current-route: `135/135 PASS`
- G6 Change 1 discovery: 보존
- current RTC disposition: `not_applicable_unproven_iris_defect`

세 계획이 동일하게 소비할 current compact projection은 다음과 같다.

```json
{"baseline_commit":"7744df68fa7c0a66ccd9e760995c1b7071de8e08","baseline_tree":"5c6fd5d2df505c9ea217e6b913bfacf296e99a63","contract_id":"iris_iar_scope_reduction_sync_v2","current_route":{"required_test_count":135,"result":"PASS"},"g4":{"attempt_specific_closure":"retired_historical","iar_core":"reusable_evaluator_only","live_gate_adoption":"not_required"},"g5":{"phase8_candidate":"preserved","terminal_finalize":"retired_not_required"},"g6":{"changes_2_8":"blocked_until_canonical_defect_attribution","current_disposition":"not_applicable_unproven_iris_defect"},"live_required_validation_manifest_sha256":"2ccf98edfd087bb193387a77d0fec5bdb3a1efe9905d66fa9ac5ae74eec2c7d1","owner_directive":"exclude_attempt_specific_closure_orchestration_from_iar_core","stable_session_names":["G1","G2","G3","G4","G5","G6"]}
```

```text
iar_scope_reduction_projection_sha256 = d2d1eec524bdbe8c29ce1a5552dd7cb1b33e8434d50bff4ce03df8c6e5b8dee7
```

### Change 1 disposition

- 기존 Change 1의 source reference-set 누락/불일치/모호성 `0/0/0` 관찰은 append-only discovery evidence로 보존한다.
- 당시 `blocked_pending_finalized_registry_handoff`는 G4/G5 attempt-specific terminal을 RTC prerequisite로 잘못 포함한 coordination 결과이며 current Iris RTC defect 증거가 아니다.
- `implementation_toolchain_freshness_failed` 또는 temporary script/staging/worktree의 실패만으로 Iris Registry Runtime Compatibility 부채를 선언하지 않는다.
- G4/G5 terminal 부재를 해결하기 위한 G6 실행은 폐기한다.

### Mandatory attribution predicate

Changes 2~8은 다음이 모두 독립적으로 참일 때만 열린다.

```text
canonical_iris_runner_failure_reproduced = true
clean_checkout_reproduced = true
temporary_orchestration_dependency = false
current_registry_to_runtime_identity_mismatch = true
runtime_or_package_effect_demonstrated = true
exact_failure_artifact_and_command_bound = true
```

하나라도 false, missing 또는 unknown이면:

```text
g6_execution_applicability = not_applicable
iris_rtc_debt_claimed = false
changes_2_through_8_authorized = false
runtime_lua_package_mutation_authorized = false
```

Attribution은 임시 script를 삭제·우회한 clean checkout에서 canonical Iris runner로 재현해야 한다. 저장소 안의 경로, tracked 상태, staging receipt 또는 검사기의 기대 freshness가 있다는 사실만으로 runtime defect가 되지 않는다. 실제 current Registry facts/manifest가 canonical rendered/bridge/runtime/package 결과와 불일치하거나 공식 실행이 실패하는 증거가 필요하다.

### Current exit

- 현재는 위 predicate를 만족하는 증거가 없으므로 G6에 실행할 다음 Change가 없다.
- 새로운 reservation, successor bundle, adoption, review, owner seal, terminal 또는 G1 pre-adoption round를 만들지 않는다.
- 향후 predicate가 PASS하면 그 exact defect attribution record를 새 실행 기준점으로 삼아 Change 2부터 진행할 수 있다. 기존 temporary-tooling failure를 재사용하지 않는다.
- predicate가 계속 성립하지 않으면 G6은 `not_applicable_non_authoritative_tooling_failure`로 종료하며 Iris current authority나 runtime을 변경하지 않는다.

### Stable session vocabulary

이 동기화 이후 세션 명칭은 `G1` Clean-Checkup, `G2` 음식 사실 의미, `G3`, `G4` 검사 시스템, `G5` 번역체 개선, `G6` RTC만 사용한다. 세션 이름은 defect authority를 만들지 않는다.

## Historical 0. Current-Lineage Synchronization Contract (Non-Executable Until Attribution PASS)

이 절은 독립적으로 작성된 문제 정의와 roadmap-derived implementation design을 현재 저장소 계보에 연결하는 coordination-only contract다. 문제의 원인, RTC 책임 경계와 success claim은 세션 이름에서 파생하지 않는다. 아래 세션 표기는 현재 작업의 재실행·중복 생성을 막기 위한 handoff vocabulary일 뿐이다. 이 절은 다른 절을 덮어쓰는 precedence authority가 아니며, 동일 계약은 아래 Assumptions, Planned Changes, Validation, Rollback과 Expected Closeout에 직접 일치시킨다.

동기화 기준점:

- current integration commit: `c0eb88a64a08c50fb3f581ee53a0502bd2445195`
- current integration tree: `0e19bac02886d67f5f8d08e60976d896f5bc2cbc`
- validated implementation subject commit: `1235e7bc497fea7f33774190a406534509838fa6`
- validated implementation subject tree: `b19ed0b21d0eafe19e719a16138437edf1dd2fd7`
- subject commit is an ancestor of the integration commit: `true`
- current facts SHA-256: `50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120`
- current input-manifest SHA-256: `090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7`
- live required-validation manifest observed working-byte SHA-256: `604275a6f8311df56c791c4c1d4492eb8e873410e03eeda41c4f761184cc819e`; execution entry rederives Git-blob, filtered-working and canonical identities rather than treating this planning observation as a seal

Changed-surface review disposition:

| Review applicability | Surfaces | Current disposition |
|---|---|---|
| prior structural finding closure remains applicable | discovery identity, denominator 3-way equality, census/freeze sequencing, clean-checkout structure, lane adjudication taxonomy, negative-fixture family | corrections are carried forward, but they do not approve the changed synchronization model |
| synchronized changed surfaces | source/rendered binding model, prerequisite class/order, reference-set composition, independent-review fulfillment, G1 pre-adoption ordering, pre-terminal default-consumer behavior, removed plan-precedence clause, current-lineage ancestry | bounded corrections are integrated into this frozen plan; no additional plan-review or governance-decision entry gate |
| eighth bounded correction | fixed pre-terminal default-consumer behavior and direct machine enforcement | plan text corrected; implementation validates the frozen constraint without a separate owner policy record |

The preceding review verdict is historical evidence rather than an execution prerequisite. Its technical corrections are incorporated into this frozen plan, and neither another exact-SHA plan review nor a separate governance owner decision is required to open Change 2. Implementation-complete review, pre-adoption G1 validation, per-result project-owner authorization, post-adoption closeout review and final owner seal remain mandatory at their defined result boundaries.

현재 source authority reference set 후보는 새 authority를 발급하지 않고 다음 tracked append-only chain을 함께 소비한다.

| Artifact | SHA-256 | Synchronized meaning |
|---|---|---|
| `Iris/build/description/v2/data/dvf_3_3_facts.jsonl` | `50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120` | current facts bytes |
| `Iris/build/description/v2/data/dvf_3_3_input_manifest.json` | `090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7` | current manifest, facts binding and declared row count |
| `Iris/build/description/v2/staging/dvf_3_3_food_semantic_registry_operational_cutover/attempts/attempt-0012/closeout/registry_correction_adoption_receipt.json` | `312c9b8744e1925b120129402b4ff6834d551960c284af8e91dbdbca091a56b0` | correction-0003 current adoption |
| `Iris/build/description/v2/staging/dvf_3_3_food_semantic_registry_operational_cutover/attempts/attempt-0012/closeout/terminal_correction_hash_seal.json` | `03dea1902f1d219b227b2b69cb88742f1005e3620cdcdee2b72ba811d1bd20fb` | adoption commit/tree and terminal binding |
| `Iris/build/description/v2/staging/dvf_3_3_food_semantic_registry_operational_cutover/attempts/attempt-0012/handoff/naturalization_current_input_handoff.json` | `bfa14583f524f99a75e88d4b6eaddfa146544cba9124cf09214a13a38c7d7750` | downstream current-input handoff |

Set membership은 owner-free mechanical rule `current_source_reference_set_composition_v1`으로만 파생한다.

1. `iris_current_authority_manifest.json`이 current/protected로 분류한 fixed path `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`의 exact bytes를 root로 연다.
2. input manifest의 `source_promotion`에서 `successor_facts_sha256 == facts.sha256`, exact `successor_id`와 `registry_cutover_attempt_id`를 함께 가진 current correction binding을 정확히 하나 선택한다. 이름·mtime·directory newest 정렬은 selector가 아니다.
3. 그 `registry_cutover_attempt_id`로 fixed cutover namespace의 adoption receipt와 terminal seal 경로를 구성하고, terminal seal이 직접 결속한 receipt/handoff path와 SHA-256만 따라간다.
4. receipt·terminal seal·handoff가 같은 facts/input-manifest SHA-256, successor ID와 attempt ID를 결속하는지 확인한다. Terminal seal과 handoff는 adoption commit `e56c2e0c94aed8f31a61cb27cd6e37f0037451c8`와 tree `c5123b318267f0d3f47933422b292aec864b481d`가 같아야 하며, terminal seal이 receipt/handoff path와 SHA-256을 직접 결속해야 한다.
5. exactly one closed chain의 member path/role/SHA-256와 derivation transcript를 `current_source_reference_set_manifest_v1.json`에 기록한다. 이 manifest는 derived receipt이지 source authority나 winner decision이 아니다.

Required field가 없으면 `blocked_reference_set_required_field_missing`, 둘 이상의 binding, 잘못된 path transition, cross-hash/identity divergence 또는 비-current lifecycle이면 `blocked_reference_set_composition_invalid`다. Change 1은 위 규칙으로 exact bytes, cross-hashes, lifecycle, commit/tree와 current-manifest declared denominator를 gap audit한다. Set가 완전하면 별도 `iris_registry_current_source_reference_and_denominator_seal_issuance` round를 만들지 않고, 불완전하면 RTC가 보충하거나 새 authority를 선택하지 않는다.

Rendered state는 다음 세 상태로 분리한다.

| State | Exact observation | Authority interpretation |
|---|---|---|
| existing rendered output path | `Iris/build/description/v2/output/dvf_3_3_rendered.json` exists and is tracked at the synchronized readpoint | protected retained non-writer surface, `authority_claim=false`; 최신 accepted candidate로 자동 해석하지 않음 |
| latest accepted candidate rendered | `attempt-0024-publish-remediation-a/phase4/candidate_rendered.json`, SHA-256 `ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437` | immutable non-current candidate |
| candidate handoff | `attempt-0024-publish-remediation-a/phase8/publish_acceptance_handoff_manifest.json`, SHA-256 `7fdbb224b3af4231a8bf3f2d37e448a8cdbfb4ed4d9871a83927b22cfdde25ec` | evaluation handoff only; G4 closure와 finalized Registry-facing packet 아님 |
| finalized Registry-facing rendered handoff packet | absent; G4 policy closure와 G5 terminal finalize 전에는 생성 불가 | RTC successor reservation을 막는 실제 upstream prerequisite |

Phase 8 handoff만으로 candidate를 current payload로 승격할 수 없고, RTC도 `output/dvf_3_3_rendered.json`을 authority로 승격하지 않는다. RTC execution entry에는 G4의 accepted disposition, live required-gate adoption과 terminal closure를 역인계 받아 G5가 봉인한 finalized Registry-facing handoff packet이 필요하다. 그 packet은 candidate rendered identity, source facts/input-manifest identity, G4 disposition/terminal identity와 G5 terminal identity를 함께 결속하되 `registry_current_adoption_claimed=false`를 유지한다.

현재 세션 handoff 상태:

| Session | Consumed state | This plan may do |
|---|---|---|
| G1 | current-route correction complete; live `135/135`, candidate projection `136/136`, clean-checkout `199/199` A/B PASS; successor 0008 evidence preserved | G4 재개 입력으로 사용하고, G3 adoption-ready candidate에 대해 live repoint 전 fresh G1 successor 재검증 |
| G2 | food semantic sealed-successor work complete | 재실행 금지 |
| G3 | correction-0003 current facts/manifest adoption complete; RTC freshness defect open | G4 closure와 finalized G5 Registry-facing handoff 뒤 이 계획으로 RTC successor 구현 |
| G4 | official attempt-0005 Phase 2~5 PASS, disposition `accepted`; existing Phase 6 failed evidence preserved, live adoption/Phase 7 not complete | G1 successor 0008을 소비해 Phase 6 correction/revalidation과 Phase 7 closure를 먼저 완료 |
| G5 | attempt-0024 Phase 8 immutable handoff complete; terminal finalize/Registry-facing packet 미완료 | G4 closure를 역인계 받아 terminal finalize와 Registry-facing packet을 봉인; candidate/trace/Phase 8 handoff는 수정·재실행 금지 |

Current synchronization evidence:

- G1 disposition ledger SHA-256: `6127556df93f919e51d9ee98cbb065d431ffabe0f19617d7a24ba159f5a80314`
- G1 gate manifest successor 0008 SHA-256: `b81878c89f9e1aa4dd9873bd1ec204632547938e33ce33567c09633f77de758f`
- G1 closeout successor 0008 SHA-256: `e6c4e877532ac196f4e8f84fcda7274251d26f1431e9a8c5b3192a9ca2e0cc1a`
- RTC open diagnostic: `implementation_toolchain_freshness_failed`
- RTC diagnostic SHA-256: `2eb285239433deda61baab508c2f9eb4a95bcd00100bd4cda8b7c41cea9c9969`
- G4 accepted disposition artifact SHA-256: `ad49f4bb0924d5f4528b61a4aed0e5338c505ee1b6be8f520abde963aa11b772`
- G4 preserved failed Phase 6 current-route result SHA-256: `f4306493bf346a076f8745bcb7422f58110a1c01845f7a3d44ddbe6cc91441cb`
- G4 required-gate candidate SHA-256: `3107201fd7e6da0c8a97a3c8d9ee8119d2d4d9768d0da3fcbcb306cc2447c75b`

`g1_pre_adoption`은 이 frozen plan의 실행 순서로 고정한다. 동기화된 실행 순서는 `G4 재개 → G5 terminal finalize/Registry-facing packet → G3 immutable candidate와 projected-live manifest freeze → G1 fresh A/B 재검증 → G3 live adoption/official route/closeout`이다. G2는 재실행하지 않는다. 이 순서는 G4의 required gate adoption을 RTC successor의 결과로 만들지 않으므로 순환 의존을 피하고, G1 미완료 candidate가 live default selection이 되는 adopted-but-unsealed 구간을 만들지 않는다. 별도 governance decision 없이 이 순서를 직접 구현한다.

Cross-session handoff gates:

1. G4는 exact integration commit `c0eb88a64a08c50fb3f581ee53a0502bd2445195`와 G1 successor 0008 hashes를 입력으로 소비한다. 기존 attempt-0005 Phase 0~5와 failed Phase 6 result를 수정하지 않고 additive correction/revalidation으로 Phase 6을 다시 판정한 뒤 Phase 7을 닫는다.
2. G4가 `accepted + live required gate adopted + policy closure complete`를 exact terminal hashes로 봉인하지 못하면 G5 terminal finalize와 G3 RTC execution은 금지한다.
3. G5는 기존 attempt-0024 candidate/trace/Phase 8 handoff를 재생성하지 않고 G4 terminal result만 역인계 받아 frozen terminal bundle과 `registry_handoff_receipt.json`을 만든다. Receipt는 `packet_status=complete`, `registry_handoff_eligibility_claimed=false`, `registry_current_adoption_claimed=false`를 유지한다.
4. G3는 G4/G5 closeout commits를 모두 포함하는 descendant commit에서 이 RTC 계획을 실행한다. Phase 0은 G5 receipt와 그 receipt가 결속한 terminal bundle/candidate를 직접 검증하며 Phase 8-only handoff로 대체하지 않는다.
5. G3는 immutable RTC candidate, exact projected post-adoption manifest, full command/test denominator와 adoption-ready commit/tree를 `g1_pre_adoption_handoff.json`에 봉인한다. G1은 live manifest를 바꾸지 않고 두 fresh checkout에서 그 projected manifest와 candidate를 explicit override로 소비해 full-repository Run A/B 및 새 append-only successor를 만든다. G1 결과가 PASS가 아니거나 미완료이면 `blocked_pending_full_repository_reverification`이며 live repoint, default consumption, official route와 closeout을 금지한다.
6. G3 adoption executor는 exact G1 PASS successor와 reviewed adoption-ready commit/tree를 결속한 descendant에서만 transaction을 acquire한다. G1 이후 repository-file toolchain, candidate, projected manifest, source/finalized-handoff binding 또는 reviewed diff가 바뀌면 PASS를 재사용하지 않고 새 freeze/G1/review를 요구한다. 기존 successor 0008은 입력 provenance일 뿐 새 결과를 대신하지 않는다.

검토·승인 계약은 cited source와 현재 운영 mechanism을 다음처럼 분리한다.

- `ARCHITECTURE.md` Registry Runtime Compatibility canonical closure는 independent review와 owner seal을 포함한 closeout packet이 terminal보다 먼저 commit될 것을 요구한다. `EXECUTION_CONTRACT.md` §6-1은 exact input/result claim-evidence binding을 요구한다. `DECISIONS.md`의 Completion Vocabulary External Gate Split은 self-generated PASS나 owner approval/seal이 independent review를 대체하지 못하며 reviewer identity/scope와 hash-sealed review artifact를 별도 축으로 보존할 것을 요구한다. 인용 원문은 “서로 다른 외부 인간 두 명” 또는 특정 credential ceremony를 요구하지 않는다.
- Fulfillment는 `fresh isolated Codex review session + separate per-result project-owner authorization/seal`이다. 이는 external-human 또는 organizational independence가 아니라 `procedural_session_independence` credit만 주장하며, owner authorization/seal은 review를 대체하지 않는다.
- Pre-adoption implementation review와 post-adoption closeout review는 이미 존재하는 두 review point를 유지하되 서로 다른 task/session ID여야 하고 구현 transcript/context를 상속하지 않는다. 각 reviewer는 roadmap/plan/implementation/adoption authorization authoring에 참여하지 않았고 owner role도 맡지 않아야 한다. 같은 `Codex Reviewer` role taxonomy/model family 사용은 허용하지만 `review_role_reused=true`, `review_session_reused=false`, `self_confirmation_relation=false`, independent-credit class와 limitation을 closeout packet에 공개한다.
- 각 attestation은 exact plan SHA-256, reviewed commit/tree, bundle/manifest/evidence-manifest SHA-256, review session/task ID, context-isolation receipt와 rerun result를 직접 결속한다. 이전 roadmap·plan review 참여자인 ChatGPT/Claude session은 implementation-complete 또는 terminal independent-review credit에 부적격하다.
- `g1_pre_adoption`과 `general_default_consumer_policy_before_terminal=fail_closed`는 이 plan의 고정된 implementation constraints다. 별도 owner policy input을 만들지 않으며 implementation schema, transaction guard와 negative fixtures가 이 두 값을 직접 강제한다.
- 별도 외부 reviewer stage, response-window reservation, SSHSIG ceremony나 24시간 credential deadline을 새로 만들지 않는다. Append-only lifecycle, exact hash binding, no predecessor fallback과 post-terminal contradictory-evidence fail-close 원칙은 유지한다.

---

## 1. Objective

현재 source authority와 현재 RTC implementation toolchain에 적용할 수 없는 predecessor bundle을 수정하거나 재사용하지 않고, synchronized current source reference set와 finalized Registry-facing rendered handoff packet을 소비하는 immutable content-addressed Registry Runtime Compatibility successor를 구축한다.

```text
Registry current source reference set ----------\
                                                  -> RTC reservation binds both exact hashes
Finalized Registry-facing rendered handoff ------/   -> Phase 0 mutual-coherence validation
-> authority reference resolved
-> execution checkout matches current authority
-> derivation chain coherent
-> declared / derived / observed denominator agreement
-> rendered derivation coherence
-> exact source/rendered/bridge/runtime/package identity
-> actual Lua reconstruction
-> Windows Route A/C lossless transport
-> isolated package projection
-> commit-bound current toolchain binding
-> RTC-bounded fresh-checkout reproduction
-> deterministic successor bundle
-> adoption-ready projected-live manifest
-> G1 pre-adoption full-repository fresh Run A/B PASS
-> reviewed/owner-authorized live required-validation exact consumption
-> isolated closeout review + owner exact-result seal
```

최종 성공 상태에서는 아래 일곱 결과를 같은 값으로 축약하지 않고 독립적으로 보고한다.

```text
current_authority_reference_resolved = true
execution_checkout_matches_current_authority = true
derivation_chain_coherent = true
stale_state_guard_status = PASS
current_registry_runtime_compatibility_status = PASS
selected_bundle_applicability_status = PASS
required_gate_consumption_status = PASS
```

현재 동기화 readpoint는 다음과 같다.

- inspected integration commit/tree: `c0eb88a64a08c50fb3f581ee53a0502bd2445195` / `0e19bac02886d67f5f8d08e60976d896f5bc2cbc`
- validated implementation subject commit/tree: `1235e7bc497fea7f33774190a406534509838fa6` / `b19ed0b21d0eafe19e719a16138437edf1dd2fd7`
- live selected RTC bundle: `46c87bfab662b09293adb6ba2b1028bdf6c0f20639c8e3fb8bd065895b5988b9`
- live RTC attempt: `attempt-0009`
- synchronized live required-validation manifest observed working-byte SHA-256: `604275a6f8311df56c791c4c1d4492eb8e873410e03eeda41c4f761184cc819e`
- predecessor bundle manifest SHA-256: `0e50d9d37d67da7534f637252366bc6ecba58d2b975960b6477c01ebb5a052a1`
- synchronized current facts raw SHA-256: `50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120`
- synchronized current input manifest raw SHA-256: `090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7`

초기 plan-authoring readpoint `33aad08676c96d5ae1ae7ff1c3fa509feff8bf08`에서 관찰한 facts `a765c50b...`와 manifest `8166257c...` 불일치는 historical planning observation으로만 보존한다. 현재 synchronized source bytes는 roadmap intake 후보와 일치하며 correction-0003 adoption chain이 이를 current로 결속한다.

RTC는 여전히 source 값을 자체 선택하지 않는다. 다만 별도 combined record의 부재만으로 새 upstream round를 강제하지 않고, Change 1이 current manifest + attempt-0012 adoption receipt + terminal seal + handoff로 구성된 synchronized reference set의 완전성을 먼저 검증한다. 완전하면 그 set를 그대로 소비하고, 불완전하면 exact missing fields만 반환한다.

Current rendered path는 synchronized readpoint에서 tracked 상태로 존재하지만 명시적 non-writer/non-authority surface이며 최신 accepted candidate와 동일한 authority라고 주장할 수 없다. 최신 candidate와 Phase 8 handoff는 아직 final Registry-facing packet이 아니다. 따라서 pre-entry discovery는 실행할 수 있지만, Publish policy closure와 naturalization terminal finalize가 끝나 finalized Registry-facing handoff packet이 봉인되기 전에는 successor attempt reservation, toolchain mutation, candidate construction과 RTC adoption을 금지한다. RTC reservation executor가 source reference set와 finalized handoff packet의 exact hashes를 각각 결속하고 Phase 0이 source facts/input identity와 packet-bound candidate derivation identity를 검증한다. `output/dvf_3_3_rendered.json`과의 equality는 요구하거나 주장하지 않는다.

---

## 2. Scope

이 계획의 범위는 다음과 같다.

- synchronized Registry current authority reference set를 read-only로 resolve하고 exact record identities, source identity, authority commit/tree, lifecycle와 current-manifest declared denominator를 소비
- attempt-independent append-only discovery observation으로 candidate inventory, missing fields, observed hashes, HEAD와 routing을 보존
- protected RTC inputs의 tracked/ignored/generated/external/unknown 상태와 one-checkout executability를 toolchain mutation 전에 확인
- `current_authority_reference_resolved`, `execution_checkout_matches_current_authority`, `derivation_chain_coherent`를 독립 판정
- current facts, decisions, overlay, input manifest, rendered output, runtime chunks와 isolated package projection 사이의 derivation coherence 확인
- reservation/freeze/adoption-ready/adopted commits가 predecessor roots, synchronized integration, current source adoption과 finalized G4/G5 terminal commits의 descendant인지 검증
- predecessor-bound 9개 경로와 실제 코드가 추가로 소비하는 direct/transitive toolchain 전체의 identity census
- Git identity, worktree bytes, normalized representation과 `.gitattributes` 영향을 분리한 freshness 판정
- validator short-circuit와 별개인 concurrent failure inventory 생성
- current manifest declared denominator, source-derived denominator와 observed exact surface count의 3-way equality를 위한 최소 RTC contract 정렬
- source → rendered → bridge → runtime → package exact key set과 per-key payload binding 재검증
- `Base.LemonGrass` / `Base.Lemongrass` collision member set과 sealed non-resolving disposition 재검증
- isolated bridge/chunk/package 생성, actual Lua merge, Windows Route A/C, negative fixture와 determinism 검증
- final freeze commit의 두 fresh checkout에서 tracked repository inputs와 finalized Registry-facing rendered handoff packet이 지정한 immutable candidate artifact만으로 candidate build와 positive validation을 재현하고 canonical parity 확인
- candidate seal 직전과 live repoint 직전 source/input/rendered/runtime binding의 concurrent drift 재확인
- frozen plan의 fixed `g1_pre_adoption` ordering과 `general_default_consumer_policy_before_terminal=fail_closed` machine enforcement
- exact adoption-ready commit/tree와 projected live manifest에 대한 G1 fresh full-repository Run A/B PASS를 live repoint 전에 봉인
- 새 immutable successor bundle, attempt evidence, predecessor-successor lineage, lifecycle event와 durable closeout packet 생성
- `Iris/_docs/round3/current_route_required_validations.json`의 additive successor adoption
- predecessor RTC-owned row preservation, current manifest recensus와 reviewed-base SHA의 optimistic concurrency/CAS adoption
- transaction-scoped official exporter/package route가 exact live successor를 선택하고 terminal 전 general default route는 fail closed하는지 확인
- terminal 전 claim-bearing official current-route result, 두 isolated Codex Reviewer PASS, 프로젝트 소유자 exact-result seal과 closeout hash binding
- 종료 시 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`를 문서별 update mode에 맞게 정렬하고 non-claim documentation regression 수행

### Explicitly Out Of Scope

- Registry Authority `attempt-0038-practical` 재실행, 수정 또는 재봉인
- RTC가 current facts/input-manifest reference 또는 declared denominator를 선택·발급·재봉인하는 것
- synchronized current source reference set가 충분한데도 중복 authority issuance round를 만드는 것
- latest candidate rendered를 `output/dvf_3_3_rendered.json`에 쓰거나 current rendered authority로 승격하는 작업
- DVF System / DVF Body Compiler 구현 또는 claim 변경
- Publish Boundary, public text acceptance 또는 semantic quality acceptance
- facts 의미, item spelling, item key, body text 또는 번역 수정
- live Lua bridge, live runtime chunks 또는 live package payload 재생성·교체
- runtime JSON parser 또는 runtime compatibility analyzer 도입
- PowerShell 5.1 raw `ConvertFrom-Json` object route 복구
- package ZIP publication, Workshop 업로드, release/deployment/B42 readiness
- 수동 인게임 QA, 멀티플레이 또는 외부 모드 전체 compatibility sweep
- plan-level review를 implementation/closeout independent-review credit으로 재사용하거나 새 reviewer layer를 추가하는 것
- terminal 전 general default consumer를 허용하는 alternate policy; 필요하면 별도 additive governance correction scope
- Pulse 의존 방향, Hub & Spoke, SPI 또는 current-route manifest ownership 변경
- unrelated refactor, test framework 재설계 또는 일반-purpose governance framework 추출

---

## 3. Non-Goals

- predecessor bundle의 source hash나 manifest만 바꾸어 current bundle처럼 만드는 것
- predecessor review, seal 또는 PASS report를 successor에 재사용하는 것
- case-variant key를 rename, merge, alias 또는 winner selection으로 해결하는 것
- count equality를 exact identity 또는 payload equivalence로 간주하는 것
- stale guard의 expected BLOCKED를 current RTC PASS로 해석하는 것
- candidate, staging path 또는 environment variable을 live default authority로 사용하는 것
- failing test 삭제, skip, expectation 완화 또는 failure code 치환으로 closure를 만드는 것
- isolated output이 live payload와 다를 때 수동 equivalence를 승인하는 것
- live mutation 후 복구한 상태를 no-mutation으로 기록하는 것
- RTC 범위 밖 full-repository clean-checkout closure 또는 cross-host/environment reproducibility를 이 계획이 소유하는 것
- Publish attempt-0005의 기존 Phase 0~5 evidence 또는 Naturalization attempt-0024의 frozen candidate/trace/Phase 0~8 evidence 수정·재실행

---

## 4. Assumptions

### Authority Assumptions

- `Philosophy.md`가 최상위 authority다.
- `DECISIONS.md`의 Registry Authority canonical closure와 Registry Runtime Compatibility contract를 유지한다.
- `ARCHITECTURE.md`의 compiler-viewer, offline production, runtime display-only 경계를 유지한다.
- `Iris/_docs/authority/iris_current_authority_manifest.json`은 current path classification/navigation authority지만 exact facts/input-manifest hash와 Registry lifecycle readpoint를 봉인하지 않으므로 단독 source currency reference가 아니다.
- `ROADMAP.md`, 첨부 로드맵과 planning checkout의 hash는 discovery 후보 또는 provenance이며 RTC가 current source를 선택하는 근거가 아니다.
- 실행 prerequisite인 synchronized current authority reference set는 exact artifact paths/record IDs와 SHA-256, facts/input-manifest SHA-256, constituent hashes/counts, adoption commit/tree, lifecycle/readpoint와 current-manifest declared denominator를 포함해야 한다.
- reference-set membership은 `current_source_reference_set_composition_v1`의 fixed manifest→current correction binding→attempt receipt→terminal seal→handoff cross-reference traversal에서만 파생한다. RTC/operator가 staging scan, newest-name/mtime 또는 ad hoc union으로 구성원을 선택할 수 없다.
- current input manifest는 source constituent를 설명하는 bound input이지만, RTC가 이를 current로 선언하거나 denominator seal을 발급하지 않는다.
- authority reference root absence는 `blocked_reference_absent`, required field absence는 `blocked_reference_set_required_field_missing`, multiple/ambiguous membership·invalid path/cross-hash·non-current lifecycle은 `blocked_reference_set_composition_invalid`로 보존하고 current source authority 경계로 routing한다. `blocked_current_authority_reference`는 이 named subcodes를 숨기지 않는 umbrella only다.
- source/rendered/runtime/package authority ownership은 이 계획으로 이동하지 않는다.

### Upstream Binding and Ordering Contract

결속 모델은 `rtc_reservation_current_source_and_finalized_rendered_handoff_binding_v2` 하나로 고정한다.

| Contract field | Declaring/binding scope | Required meaning |
|---|---|---|
| `registry_current_facts_sha256` / `registry_current_input_manifest_sha256` | synchronized current source reference set | current로 채택된 exact raw facts와 complete input-manifest bytes의 SHA-256 |
| `rendered_source_facts_sha256` / `rendered_source_input_manifest_sha256` | finalized Registry-facing rendered handoff packet | candidate artifact가 실제 소비한 exact raw facts와 complete input-manifest bytes의 SHA-256 |
| `rendered_artifact_identity` | finalized Registry-facing rendered handoff packet + naturalization derivation receipt | content-addressed candidate rendered bytes, `meta`, `entries_sha256`, Publish disposition/terminal과 naturalization terminal lineage |
| `rendered_handoff_binding_scope` | RTC reservation executor | `rtc_reservation`; source reference-set manifest SHA-256와 finalized handoff-packet SHA-256를 독립 fields로 결속 |
| `mutual_coherence_validator` | RTC Phase 0 | 두 authority declaration과 materialized bytes의 equality를 판정하며 불일치를 수정하지 않음 |

Inter-prerequisite ordering은 `source_current_then_publish_closure_then_finalized_rendered_handoff`다. Publish closure는 accepted Naturalization Phase 8 subject를 소비하고, Naturalization terminal finalize는 그 exact Publish closure를 역인계 받아 finalized Registry-facing handoff packet을 만든다. Source reference set는 이 handoff 때문에 재발급하거나 supersede하지 않는다. RTC reservation만 exact 두 artifact-set hashes와 consumed discovery manifest를 함께 결속한다.

Phase 0은 최소 다음을 독립 비교한다.

```text
Registry current facts identity
==
Finalized handoff packet source facts identity

Registry current input-manifest identity
==
Finalized handoff packet source input-manifest identity

Finalized handoff packet candidate identity
==
immutable candidate bytes / meta / entries_sha256
```

두 input-manifest identities는 각각 complete manifest raw bytes의 lowercase 64-hex SHA-256이고 constituent subset, 자유형 derivation description 또는 사람 assertion으로 대체할 수 없다. `rendered_source_derivation_basis` 대안 field와 `or` branch는 이 계획에 존재하지 않는다. 어느 required field가 absent/ambiguous이거나 equality가 false/unknown이면 `blocked_upstream_artifact_incoherent`로 terminal 처리하고 source reference set를 재작성하거나 receipt를 소급 수정하지 않는다.

Planning readpoint prerequisite dependency:

| Prerequisite | Current existence | Exact authority scope | Satisfaction path | Inter-prerequisite ordering / RTC binding | Separate scope required |
|---|---|---|---|---|---|
| Current source authority reference set | `present_candidate_set_pending_gap_audit` | `current_source_reference_set_composition_v1` over current manifest + attempt-0012 adoption chain | Change 1 mechanically derives membership and validates exact cross-hashes, lifecycle and current identity without issuing a duplicate authority | RTC reservation binds the derived reference-set manifest SHA-256 | no unless a required field is missing or composition is invalid |
| Current-manifest declared denominator | `present_pending_rederivation` | current input manifest | derive source denominator and compare declared/derived/observed values | part of source reference set | no |
| Authority commit/tree current readpoint | `present_in_attempt_0012_terminal_chain_pending_exact_validation` | attempt-0012 terminal seal and adoption lineage | Change 1 verifies exact commit/tree and ancestry | part of source reference set | no unless contradictory |
| Finalized Registry-facing rendered handoff packet | `absent_pending_publish_closure_and_naturalization_finalize` | Naturalization terminal handoff boundary consuming exact Publish closure | exact packet binds candidate derivation, source pair, Publish disposition/terminal, Naturalization terminal and `registry_current_adoption_claimed=false` | RTC reservation binds its exact packet SHA-256 after finalize | yes |
| Independent Codex reviews and project-owner result approvals | `not_started` | two isolated Codex review sessions + separate owner authorization/seal | exact implementation-complete/adoption-ready and post-adoption closeout bundles | pre-adoption G1/repoint and post-adoption terminal ordering as specified below | no external-person reservation or credential ceremony |

Change 1 gap audit와 finalized Registry-facing rendered handoff packet이 모두 준비되기 전 execution-entry state는 `blocked_pending_finalized_registry_handoff`다. Reference field가 없으면 `blocked_reference_set_required_field_missing`, cross-reference composition이 invalid하면 `blocked_reference_set_composition_invalid`로 세분화한다. Combined record가 없다는 이유만으로 별도 authority issuance를 자동 요구하지 않는다. 이 두 prerequisite와 eligible Change 1 discovery가 준비되면 추가 plan review나 별도 governance decision 없이 Change 2를 연다.

### Repository Assumptions

- physical worktree 이름과 절대경로는 authority identity가 아니다. Execution baseline은 exact commit/tree이며 새 repository copy나 persistent worktree를 만들지 않고 기존 clean worktree 또는 disposable checkout을 사용한다.
- predecessor durable bundle, attempt ledger, lifecycle ledger와 `attempt-0009/closeout`은 immutable historical evidence로 보존한다.
- live required-validation manifest는 historical required artifacts를 보존하는 additive container다. successor adoption 시 predecessor rows를 삭제하지 않는다.
- predecessor terminal의 `post_adoption_live_manifest_sha256` `2a0a46eb...`는 historical provenance일 뿐 future whole-manifest equality gate가 아니다. adoption은 predecessor RTC-owned rows/lifecycle references preservation과 pre-adoption review가 소비한 exact current manifest SHA의 CAS equality를 별도로 검사한다.
- current runtime authority는 `IrisLayer3DataChunks.lua`와 manifest가 열거한 chunk set이다. `Chunk001`~`Chunk011`이라는 현재 결과를 영구 상수로 사용하지 않는다.
- current code의 `toolchain_roots()`와 Python import inventory는 roadmap의 9개 seed path보다 넓다. successor toolchain identity는 9개 seed path와 발견된 모든 direct/transitive dependency를 모두 포함한다.
- repository-file toolchain identity는 exact freeze commit/tree/blob에 결속한다. Python/uv/package/PowerShell/Lua/OS 환경은 별도 execution receipt이며, lockfile 또는 별도 승인된 environment artifact가 없으면 sealed repository toolchain claim으로 확대하지 않는다.

### Historical Planning Observations and Current Revalidation Targets

- predecessor toolchain manifest는 28 rows를 봉인한다.
- initial `33aad086...` planning checkout에서 predecessor toolchain과 다른 것으로 관찰된 `.gitattributes` 결과는 historical observation이다. Current synchronized commit의 9 seed paths와 transitive dependencies를 Change 3a에서 전수 재측정한다.
- `validate_toolchain_freshness()`는 toolchain drift를 먼저 raise하므로 이후 source applicability, manifest applicability와 surface mismatch가 같은 실행에서 모두 열거되지 않는다.
- `validate_dvf_3_3_registry_runtime_compatibility.py`는 collision completeness에 `len(records) == 2105`와 `len(source) == 2105`를 사용한다.
- `run_dvf_3_3_registry_runtime_compatibility.py`와 `test_dvf_3_3_registry_runtime_compatibility_chunks.py`의 Lua reconstruction 기대값도 `2105`를 직접 사용한다.
- current RTC surface input은 facts/decisions/overlay를 직접 읽지만 `dvf_3_3_input_manifest.json`을 bound input으로 소비하지 않는다.
- `Iris/tools/package_iris.ps1`의 `-RegistryCompatibilityProbe`는 이미 존재하는 parameter이며 authentication이 아니다. Adoption transaction 구현이 내부 receipt parameter를 추가하면 별도 toolchain/API diff로 분류하되 기존 probe의 no-ZIP, fail-closed guard semantics를 약화하지 않는다.
- `validate_dvf_3_3_registry_runtime_compatibility.py`의 planning `HEAD` parser에는 `--bridge-preflight`, `--surface-validation`, `--contract-only`, `--required-gate`, `--require-implementation`만 있고 pre-entry observation mode는 존재하지 않는다. Change 1은 이 validator나 다른 RTC-bound repository-file toolchain을 수정하지 않는다.
- predecessor `attempt-0009/closeout/owner_canonical_seal_gate_report.json`은 historical seal로 보존하고 successor result에 재사용하지 않는다. Successor는 project-owner exact-result decision과 append-only machine lifecycle state를 별도 schema/version으로 결속하되 SSH credential 또는 별도 succession authority를 요구하지 않는다.
- synchronized commit `c0eb88a...`와 validated subject `1235e7bc...`의 ancestry는 확인됐지만 execution reservation, implementation freeze, adoption-ready와 final adopted commits에서 historical roots, synchronized integration, current source adoption, dynamic G4/G5 terminal commits 전체를 다시 확인한다.
- initial planning checkout에서 combined `current_authority_reference` field가 없었다는 사실은 historical observation이다. Current source reference set는 exact existing artifacts의 composition으로 검증하며 field-name 부재를 authority 부재로 해석하지 않는다.
- canonical top-document paths `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/EXECUTION_CONTRACT.md`는 planning checkout에서 모두 present/tracked로 확인됐다. competing top-document path를 만들지 않는다.

### Protected-Input and D-01 Feasibility Observation

Synchronized readpoint에 대한 `git ls-files` / `git check-ignore -v` 관찰:

| Required surface | State | Fresh-checkout disposition |
|---|---|---|
| facts / decisions / overlay / input manifest | `tracked` | available |
| runtime chunk manifest and `Chunk001`–`Chunk011` current manifest-derived set | `tracked` | available; final set is re-enumerated |
| `Iris/build/description/v2/output/dvf_3_3_rendered.json` | `exists + tracked`; explicit non-writer, `authority_claim=false`; latest candidate와 equality 미요구 | protected no-mutation surface; RTC input authority로 사용 금지 |
| live required-validation manifest and RTC durable bundle | `tracked` | available |
| attempt-local package projection | `generated by existing -RegistryCompatibilityProbe` | allowed output, not a pre-existing authority input |

The package guard currently hashes the rendered path directly, but that path is a protected non-authority surface and cannot stand in for the accepted candidate. Planning feasibility verdict is `blocked_pending_finalized_registry_handoff`; positive RTC validation is `not_run_due_unbound_finalized_rendered_handoff`. This does not weaken D-01. The minimum alignment must make the isolated RTC/package probe consume the tracked packet-bound candidate explicitly while preserving the unconditional package guard for default/live routes. Both final fresh checkouts must consume the same finalized handoff packet and its tracked candidate bytes; copying another workspace file, invoking an unapproved generator or using an environment fallback is forbidden.

이 관찰값은 toolchain alignment가 필요할 가능성을 높이지만, durable Phase 0과 Change 3a census가 끝나기 전 final change classification을 확정하지 않는다.

### Decision-Gate Assumptions

sealed principle, project-policy input, implementation choice와 prerequisite dependency를 분리한다. `sealed_constraint`는 아래 표에 exact governing source가 있는 principle에만 사용한다. Plan-invented schema/transaction/correction mechanism은 그 principle을 구현하더라도 스스로 sealed authority가 되지 않으며, 프로젝트 소유자가 원칙을 보존하는 다른 검증 가능한 mechanism을 승인하면 explicit plan revision과 toolchain freeze를 거쳐 조정할 수 있다.

| ID | Authority class | Governing source / basis | 채택 disposition | 실행 효과 |
|---|---|---|---|---|
| `D-01` | `prerequisite_dependency` | synchronized source reference set + finalized Registry-facing rendered handoff packet + this plan D-01 | RTC-bounded clean checkout hard gate | RTC reservation이 두 exact artifact-set hashes를 결속하고 source/rendered complete input-manifest raw SHA-256 exact equality를 통과한 뒤 final freeze commit의 primary/reproduction checkout은 tracked inputs와 same packet-bound candidate artifact만 소비한다. |
| `D-02` | `implementation_choice` | plan-invented sequencing | census-first sequencing | read-only census → drift classification → lane selection → selected lane의 최소 alignment → freeze commit/tree → fresh checkout → final identity capture → candidate generation 순서를 사용한다. |
| `D-03` | `implementation_choice` | plan-invented identity mechanism | Git authority identity | commit/tree/blob은 authority binding, raw bytes/normalized representation은 execution·diagnostic evidence로 분리한다. |
| `D-04a` | `sealed_constraint` | `ARCHITECTURE.md` Registry Runtime Compatibility canonical closure; `EXECUTION_CONTRACT.md` §6-1; `DECISIONS.md` Completion Vocabulary External Gate Split | independent-review/owner-seal separation, exact binding and terminal ordering principle | independent review는 owner approval/seal과 self-generated PASS로 대체할 수 없고, both exact-result records를 포함한 closeout packet commit 뒤에만 success terminal을 허용한다. |
| `D-04b` | `implementation_choice` | frozen plan + existing RTC independent-review precedent | isolated Codex review fulfillment, G1 pre-adoption ordering and fixed fail-closed behavior | 서로 다른 isolated Codex sessions가 pre/post result review를 수행하고 G1은 repoint 전에 실행한다. Pre-terminal general default policy는 exact literal `fail_closed`이며 별도 owner policy input 없이 implementation schema와 guards가 직접 강제한다. |
| `D-04c` | `implementation_choice` | existing single-writer/CAS/atomic-replace precedent | bounded machine adoption transaction | candidate → isolated pre-adoption review → G1 fresh A/B PASS → project-owner exact authorization → CAS/atomic replace → official route → isolated closeout review/owner seal 순서를 구현한다. D-04a를 보존하는 더 단순한 proven atomic mechanism을 우선한다. |
| `D-05a` | `sealed_constraint` | `DECISIONS.md` Registry Runtime Compatibility contract; `ARCHITECTURE.md` RTC canonical closure | exact collision non-resolution | no rename/no merge/no alias/no winner와 exact member/payload preservation은 project-policy input으로 변경할 수 없다. |
| `D-05b` | `project_policy_input` | sealed collision disposition artifact | disposition applicability / escalation | 프로젝트 소유자는 exact collision policy artifact의 current applicability와 escalation routing만 결정한다. |
| `D-06` | `sealed_constraint` | `DECISIONS.md` RTC contract current-default rule; `ARCHITECTURE.md` tracked live lifecycle resolution | no predecessor fallback | adoption/claim failure 시 superseded predecessor를 current PASS authority로 복귀시키지 않고 additive blocked/invalidation 상태를 기록한다. |
| `D-07a` | `sealed_constraint` | `ARCHITECTURE.md` append-only attempt/lifecycle + immutable bundle contract | immutable claim-bearing evidence | failed/terminal evidence, bundle와 lifecycle history를 삭제·덮어쓰기·replay하지 않는다. |
| `D-07b` | `implementation_choice` | `DECISIONS.md` Registry Authority bounded-correction precedent, not RTC sealed authority | bounded verifier correction mechanism | verifier-only duplicate metadata projection은 execution evidence 불변 조건에서 additive correction을 허용한다. Owner가 mechanism을 바꿔도 D-07a와 no replay를 보존해야 한다. |
| `D-08` | `implementation_choice` | plan-invented execution lifecycle | reservation-before-Phase-0 | pre-entry discovery 뒤 attempt를 reserve하고 Phase 0 verdict와 blocked terminal evidence를 attempt root에 durable하게 기록한다. |
| `D-09` | `implementation_choice` | current manifest declaration + this plan compatibility tripwire | denominator triple-check | current-manifest declared denominator, authority-derived denominator와 observed surface count의 3-way equality를 요구한다. |
| `D-10a` | `sealed_constraint` | `EXECUTION_CONTRACT.md` §6-1/§6-2 claim-evidence binding; `ARCHITECTURE.md` fail-closed consumer and append-only lifecycle principles | reachable fail-closed invalidation authority principle | post-terminal contradictory evidence가 생기면 current applicability를 내릴 검증 가능한 issuer 또는 mechanical blocked state가 반드시 존재해야 한다. |
| `D-10b` | `implementation_choice` | existing append-only correction/invalidation precedent | project-owner decision + mechanical invalidation policy | exact contradictory evidence가 발생하면 machine lifecycle validator가 current applicability를 fail closed로 내리고, 후속 correction/adoption은 프로젝트 소유자의 새 exact-result decision을 요구한다. |

`g1_pre_adoption`과 `general_default_consumer_policy_before_terminal=fail_closed`는 owner-selectable policy가 아니라 이 frozen plan의 direct constraints다. Reservation/adoption transaction schema와 default-consumer guards가 이를 구현하며 별도 governance input artifact를 소비하지 않는다. 프로젝트 소유자의 per-result authorization/seal은 exact candidate, adoption diff, official result와 closeout review에만 결속되고 independent review를 대체하지 않는다. Codex Reviewer는 구현자와 분리된 fresh isolated session에서 exact implementation-complete/adoption-ready 또는 post-adoption closeout bundle을 검토한다. Independence credit은 `procedural_session_independence`로 제한하고 external-human/organizational independence를 주장하지 않는다.

---

## 5. Repository Areas Affected

### Code

- `.gitattributes`
- `Iris/build/description/v2/tools/build/dvf_3_3_registry_runtime_compatibility.py`
- `Iris/build/description/v2/tools/build/run_dvf_3_3_registry_runtime_compatibility.py`
- `Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py`
- `Iris/build/description/v2/tools/build/dvf_3_3_registry_runtime_compatibility_closeout.py`
- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py`
- `Iris/build/description/v2/tools/build/export_registry_runtime_records.py`
- `Iris/_docs/round3/registry_runtime_compatibility/bootstrap/reserve_registry_runtime_compatibility_attempt.py`
- `Iris/tools/inspect_registry_runtime_compatibility.ps1`
- `Iris/tools/package_iris.ps1`
- `tools/check_lua_syntax.ps1`

수정 여부는 Change 3 lane disposition에 따른다. identity census에는 unchanged path도 포함한다.

### Tests

- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_contract.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_bridge.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_chunks.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_windows.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_package.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_fixtures.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_current.py`
- `Iris/build/description/v2/tests/test_dvf_3_3_registry_runtime_compatibility_closeout.py`
- `Iris/build/description/v2/tests/fixtures/registry_runtime_compatibility/roadmap_fixtures.json`
- `Iris/build/description/v2/tests/fixtures/registry_runtime_compatibility/lua_merge_harness.lua`
- `Iris/_docs/round3/registry_runtime_compatibility/bootstrap/test_reserve_registry_runtime_compatibility_attempt.py`

### Docs

- `docs/dvf_3_3_registry_runtime_compatibility_current_authority_freshness_successor_plan.md`
- `docs/DECISIONS.md` — terminal 뒤 successor decision을 append하고 predecessor decision을 보존
- `docs/ARCHITECTURE.md` — terminal 뒤 RTC axis의 canonical current readpoint를 successor로 교체하고 predecessor trace를 유지
- `docs/ROADMAP.md` — terminal 뒤 current summary를 갱신하고 historical provenance와 roadmap input SHA-256을 유지
- `docs/EXECUTION_CONTRACT.md` — verified tracked canonical execution contract; read-only compliance input
- 필요 시 별도 claim boundary / closeout 문서

위 네 canonical top-document paths는 planning checkout에서 직접 확인됐다. 같은 역할의 competing document를 새 path에 생성하지 않는다.

### Config

- current source authority reference set — read-only prerequisite; actual selected path/record ID와 SHA-256을 attempt evidence에 기록
- `Iris/_docs/authority/iris_current_authority_manifest.json` — read-only classification anchor, exact source currency reference로 대체 사용 금지
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json` — read-only protected input
- `Iris/_docs/round3/current_route_required_validations.json` — additive adoption surface
- `Iris/_docs/round3/round3_active_core_closure.json` — no-mutation verification input

### Generated Artifacts

Attempt-independent discovery observation root:

- `Iris/_docs/round3/registry_runtime_compatibility/authority_reference_discovery/<discovery-id>/`

각 discovery root는 immutable `discovery_identity_core_v1.json`, `discovery_observation.json`, candidate inventory, serialization/second-run receipts와 content manifest를 보존한다. 후속 reservation은 consumed discovery manifest SHA-256과 recomputed discovery ID를 결속한다. 이 evidence는 current authority, attempt terminal 또는 RTC PASS가 아니다.

Attempt-local evidence root:

- `Iris/build/description/v2/staging/dvf_3_3_registry_runtime_compatibility/attempts/<attempt-id>/`

successor round도 기존 RTC namespace와 reservation/closeout contract를 재사용한다. 별도 general-purpose ledger나 parallel attempt namespace를 만들지 않는다.

pre-entry discovery는 attempt를 열기 위한 prerequisite observation일 뿐 execution verdict를 내지 않는다. discovery 자체는 append-only durable record로 commit하고, reference가 resolve된 후에는 reservation을 먼저 commit한 다음 모든 Phase 0 verdict를 attempt-local evidence에 기록한다.

Durable canonical root:

- `Iris/_docs/round3/registry_runtime_compatibility/bundles/<successor-bundle-id>/`
- `Iris/_docs/round3/registry_runtime_compatibility/attempts/<attempt-id>/`
- `Iris/_docs/round3/registry_runtime_compatibility/bundle_lifecycle/`
- `Iris/_docs/round3/registry_runtime_compatibility/attempt_events.jsonl`
- `Iris/_docs/round3/registry_runtime_compatibility/bundle_lifecycle_events.jsonl`
- `Iris/_docs/round3/registry_runtime_compatibility/adoption_transactions/<attempt-id>/`
- `Iris/_docs/round3/registry_runtime_compatibility/adoption_transaction_events.jsonl`
- attempt-local `required_lineage_commit_set_v1.json`, `current_lineage_ancestry_report_v1.json`, `g1_pre_adoption_handoff.json`, adoption transaction contract, projected-live/scratch equivalence receipt, failure-injection receipt, isolated Codex Reviewer attestations and project-owner exact-result decision records

Protected no-mutation surface:

- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
- `Iris/build/description/v2/output/dvf_3_3_rendered.json`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
- manifest-derived runtime chunk set
- isolated package와 비교할 live package input surface

---

## 6. Planned Changes

### Change 1 — Durable Pre-Entry Authority Discovery and Clean-Checkout Feasibility Observation

Purpose:

RTC가 current source를 선택하지 않도록 synchronized current source reference set를 resolve하고, finalized Registry-facing rendered handoff prerequisite, protected-input state와 one-checkout feasibility를 attempt-independent durable observation으로 보존한다.

Files:

- `Iris/_docs/authority/iris_current_authority_manifest.json`
- synchronized current manifest와 attempt-0012 adoption receipt/terminal seal/handoff
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
- existing `git`, `rg`, `jq` and PowerShell read-only inspection command matrix — exact versions, executable hashes, argv and exit codes are observation provenance
- `Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py` — read-only parser/mode census only; no Change 1 mutation or nonexistent mode claim
- accepted candidate rendered와 immutable Phase 8 handoff — Publish/Naturalization 종결 전 non-current comparison evidence only
- `Iris/_docs/round3/registry_runtime_compatibility/authority_reference_discovery/<discovery-id>/`
- top-document current readpoints와 roadmap/review inputs

Implementation Notes:

- authority/source/protected surfaces는 read-only로 검사하고 attempt는 reserve하지 않는다. 유일한 write는 append-only discovery observation root와 그 commit이며 Phase 0 execution, current authority 또는 PASS/BLOCKED attempt verdict가 아니다.
- Change 1은 repository-file code/toolchain mutation `0`으로 실행한다. 현재 validator에 pre-entry observation mode가 없으므로 이를 추가하거나 호출하지 않는다. `git ls-files`, `git check-ignore -v`, `git cat-file`, `git grep`, `rg`, `Get-FileHash`와 exact `jq -S -c` canonicalizer의 declared command matrix로 관찰·직렬화하고 exact command/tool identity와 raw transcripts를 content manifest에 결속한다.
- pre-entry automation이 이후 필요하다고 판단되면 Change 1에 소급 추가하지 않는다. 해당 helper 또는 validator mode를 Change 3b의 `diagnostic_only_dependency` 또는 contract-affecting toolchain diff로 제안하고 census, lane adjudication, test와 freeze에 포함한 새 execution 계획으로만 도입한다.
- authority hierarchy에서 current manifest와 valid adoption lifecycle가 함께 current로 지정한 exact record set만 허용한다. Roadmap, planning checkout, environment, non-current candidate, predecessor bundle 또는 일반 classification manifest를 source selector로 사용하지 않는다.
- `current_source_reference_set_composition_v1`은 fixed current input-manifest path에서 exact hash-matching correction binding 하나를 찾고, 그 binding의 attempt ID로 fixed cutover receipt/terminal paths를 구성한 뒤 terminal seal이 직접 hash-bind한 handoff만 따라간다. Recursive staging scan, arbitrary record union, lexicographic/mtime “latest” 선택과 operator-provided member list를 금지한다.
- reference set는 최소 다음을 포함해야 한다:
  - authority artifact paths/record IDs와 각 record SHA-256
  - exact facts SHA-256과 exact input-manifest SHA-256
  - input-manifest constituent paths/hashes/counts
  - authority commit/tree와 lifecycle/readpoint
  - current-manifest declared denominator와 그 facts binding
- `discovery_observation.json`은 `observation_success`와 `entry_eligibility_status`를 분리한다. authority candidate가 없거나 여러 개여도 inventory/hashes/missing fields/scope routing/raw transcripts를 완전하게 기록하고 immutable commit하면 observation 자체는 성공할 수 있다.
- reference-set disposition은 `0 root/binding -> blocked_reference_absent`, `1 coherent closed chain -> eligible_subject_to_remaining_prerequisites`, `>1 current binding/chain or contradictory records -> blocked_reference_set_composition_invalid`로 고정한다. Required field가 없으면 `blocked_reference_set_required_field_missing`, lifecycle이 non-current면 `blocked_reference_set_composition_invalid`이며 dual-current를 임의로 해소하지 않는다.
- `entry_eligibility_status=eligible`은 exactly one coherent current source reference set, 완전한 declared-denominator/commit/tree binding, exactly one eligible finalized Registry-facing rendered handoff packet, protected-input `unknown=0`과 declared command-matrix completion을 모두 요구한다. 이와 별도로 `observation_success=true`는 execution entry나 RTC PASS가 아니다.
- finalized G5 receipt는 exact G4 terminal artifact path/SHA-256/commit/tree와 exact G5 terminal-finalize artifact path/SHA-256/commit/tree를 직접 결속해야 한다. Change 1은 값이 생기기 전에 hardcode하지 않고 finalized artifacts에서 추출해 historical roots, synchronized integration과 current source adoption을 합친 provisional `required_lineage_commit_set_v1` inventory를 만든다. G4/G5 fields가 없으면 entry eligibility는 false다.
- `discovery_observation.json`은 discovery ID, execution HEAD, observed facts/input/live-manifest hashes, 조사한 record-set paths/SHA-256, missing fields, protected-input tracked/ignored/generated/external/unknown classification, source-reference/finalized-rendered-handoff prerequisite states, `rendered_handoff_binding_scope=rtc_reservation`, observation verdict, entry-eligibility verdict와 separate-scope requirement를 기록한다.
- ID preimage schema는 `discovery_identity_core_v1` 하나로 고정한다. 이 core에는 schema version, inspected repository HEAD, repository-relative inspected candidate/source paths와 observed hashes, candidate missing-field/cardinality observations, protected-input state, Registry/DVF prerequisite observations, scope-routing inputs와 non-derived inspection-command provenance만 allowlist로 포함한다.
- `discovery_identity_core_v1`에는 `discovery_id`, discovery root/directory name, `content_manifest_sha256`, `identity_core_sha256`, `serialization_receipt_sha256`, `second_run_comparison_result`, full observation/content-manifest path, discovery ID가 포함된 모든 path/reference, timestamp, username, locale-dependent display text와 absolute path를 반드시 제외한다. Derived field가 중첩 object 또는 array에 나타나도 reject하며, unknown field를 core에 자동 포함하지 않는다.
- `discovery_id`는 canonicalizer-bound full SHA-256 identity다. `discovery_identity_core_v1`은 duplicate JSON key를 canonicalization 전에 reject한다. Exact `jq` executable SHA-256, raw version-output SHA-256, argv `["-S","-c"]`, `LC_ALL`, `LANG`, `TZ`와 UTF-8 encoding을 `canonicalizer_identity`에 기록한다. Identity bytes는 이 순서의 각 UTF-8 field를 `uint64_be(length) || field_bytes`로 이어 붙인다. Canonical core는 exact binary가 출력한 sorted-key compact UTF-8 bytes에서 terminal LF 하나만 제거하고 BOM을 금지한다. number representation과 Unicode escaping은 이 exact binary output에 결속되므로 canonicalizer identity가 달라지면 동일 logical observation도 의도적으로 다른 ID를 갖는다.
- full 64-hex `discovery_id`는 `SHA256(UTF8("iris-rtc-discovery-id-v1\n") || uint64_be(canonicalizer_identity_length) || canonicalizer_identity || uint64_be(canonical_core_length) || canonical_core)`로 계산한다. 동일 canonicalizer identity/core를 독립 두 번 직렬화했을 때 byte identity와 full ID가 같아야 하며, 동일 ID가 이미 있으면 byte-identical content만 재참조할 수 있고 수정/덮어쓰기는 금지한다.
- 계산 순서는 `(1) discovery_identity_core_v1 구성 -> (2) duplicate/derived-field rejection -> (3) exact jq canonicalization -> (4) canonical core bytes와 optional identity_core_sha256 계산 -> (5) discovery_id 계산 -> (6) <discovery-id>/ root 결정 -> (7) full discovery_observation.json에 discovery_id와 derived paths/receipts 추가 -> (8) core, full observation, inventories와 receipts를 content manifest로 봉인`으로 고정한다. ID 또는 root가 결정되기 전에 derived path/reference를 core에 투입하지 않는다.
- content manifest는 core, full observation, candidate inventory, serialization/second-run receipts와 planning provenance SHA-256을 봉인한다. `content_manifest_sha256`는 discovery ID의 결과가 아니라 별도 후행 seal이며 그 값만 바뀌어도 core/ID는 변하지 않는다. 동일 observation을 수정하지 않고 후속 discovery는 새 directory를 사용한다.
- arbitrary eligible commit의 clean projection에서 required RTC input availability와 positive validator entrypoint executability를 확인한다. Finalized Registry-facing rendered handoff packet이 없으면 `blocked_pending_finalized_registry_handoff / not_run_due_unbound_finalized_rendered_handoff`를 예상하며 이 결과를 success로 재분류하지 않는다.
- reference set와 finalized handoff packet이 모두 resolve되면 reservation pre-entry manifest가 exact reference-set manifest SHA-256, exact finalized-handoff packet SHA-256와 consumed discovery content-manifest SHA-256을 서로 다른 fields로 결속한다. 이 계획이나 operator가 input 값을 재작성하지 않는다.
- reference set 또는 finalized handoff packet이 absent면 discovery record를 commit하고 successor attempt를 열지 않는다. Publish policy closure와 naturalization terminal finalize가 끝난 뒤 새 discovery를 수행한다.

Validation:

- observation-level success:
  - candidate inventory completeness verified, all inspected hashes and raw command transcripts recorded
  - missing fields and exact authority-scope routing enumerated
  - protected-input state and one-checkout input/executability feasibility result durable
  - duplicate-key rejection, exact canonicalizer identity, UTF-8/no-BOM/LF/compact/sorted-key contract recorded
  - two independent canonicalization runs produce byte-identical core and identical full 64-hex `discovery_id`
  - validator reconstructs `discovery_identity_core_v1` from the full observation by the fixed allowlist, rejects every forbidden derived field, and recomputes the same ID
  - changing full-observation `discovery_id` produces recomputed-ID mismatch
  - changing only content-manifest hash or a discovery-ID-derived path leaves recomputed core ID unchanged
  - changing an observation fact changes discovery ID
  - injecting any forbidden derived field into the identity core produces BLOCKED
  - `observation_success=true` committed in an immutable content-addressed discovery root
- entry-eligibility result:
  - `0 / 1 coherent set / >1 or contradictory` reference-set cardinality produces `blocked_reference_absent` / eligible / `blocked_reference_set_composition_invalid`
  - exactly one synchronized current reference set with required fields, current lifecycle/readpoint and record SHA-256 values
  - manifest→current correction binding→attempt receipt→terminal seal→handoff traversal is unique and fully cross-hash-bound
  - missing required composition field produces `blocked_reference_set_required_field_missing`
  - ambiguous member, disallowed path transition or cross-hash/current-lifecycle divergence produces `blocked_reference_set_composition_invalid`
  - exactly one eligible finalized Registry-facing rendered handoff packet and every protected-input `unknown=0`
  - finalized G5 receipt exposes exact G4/G5 terminal commit/tree fields for dynamic lineage construction
  - current source precedes Publish policy closure and final rendered handoff; RTC reservation binds source/handoff without rewriting either
  - missing reference/adoption input routes to the exact upstream authority scope
- discovery content manifest is immutable and later reservation verifies/recomputes discovery core ID before source/handoff consumption
- Change 1 RTC-bound repository-file toolchain mutation `0`
- planning/roadmap/staging fallback count `0`

---

### Change 2 — Attempt Allocation and Durable Phase 0 Currency, Coherence and Lineage Gate

Purpose:

새 attempt를 append-only로 먼저 열고 current authority currency, derivation coherence, commit ancestry와 failure axes를 durable evidence로 판정한다.

Files:

- RTC bootstrap reservation executor와 ledgers
- new attempt root
- current source authority reference set
- facts/decisions/overlay/input manifest/rendered/runtime/package authority surfaces
- predecessor bundle/lifecycle/closeout
- `.gitattributes`

Implementation Notes:

- event ledger가 missing/empty인데 durable RTC attempts 또는 bundles가 존재하면 cold state로 간주하고 `blocked_ledger_cold_state`로 중단한다. 기존 evidence로 ID를 추측하거나 ledger를 재작성하지 않는다.
- open/nonterminal attempt count가 `0`인지 ledger replay로 확인한다. orphan reservation이 있으면 삭제·재사용하지 않고 original reservation/nonce와 evidence를 결속한 authorized additive blocked terminal로 먼저 reconciliation한 뒤 새 attempt를 연다.
- attempt allocation은 추가 plan-review artifact나 별도 governance owner-decision artifact를 요구하지 않는다. Frozen plan의 `g1_pre_adoption` ordering과 `general_default_consumer_policy_before_terminal=fail_closed`는 reservation/transaction schema의 direct constants이며 operator input이나 owner-selectable enum으로 받지 않는다.
- latest approved discovery content manifest가 `observation_success=true`, `entry_eligibility_status=eligible`이고 exact current source reference set, declared denominator, commit/tree current binding와 finalized Registry-facing rendered handoff packet을 모두 보유하는지 확인한다. Synchronized observation에서 finalized packet이 absent이므로 reservation은 blocked다.
- reservation intake는 content manifest를 신뢰해 ID를 복사하지 않는다. Full observation에서 fixed allowlist로 `discovery_identity_core_v1`을 재구성하고 forbidden derived fields `0`, duplicate keys `0`, recorded canonicalizer identity 일치와 recomputed full discovery ID/root-name equality를 먼저 검증한다. 하나라도 실패하면 `blocked_discovery_identity_reconstruction`으로 attempt를 열지 않는다.
- 새 attempt ID, output root와 nonce를 사용한다.
- reservation record는 `binding_model=rtc_reservation_current_source_and_finalized_rendered_handoff_binding_v2`, `rendered_handoff_binding_scope=rtc_reservation`, verified/recomputed discovery ID, discovery content-manifest SHA-256, source reference-set manifest SHA-256와 finalized Registry-facing rendered handoff-packet SHA-256을 독립 fields로 직접 결속한다. 또한 exact frozen plan SHA-256와 fixed literals `g1_ordering=g1_pre_adoption`, `general_default_consumer_policy_before_terminal=fail_closed`를 직접 결속한다.
- reservation commit 후 Phase 0은 `phase0_current_authority_gate_report.json` 또는 동등한 attempt-local record에 모든 관찰과 verdict를 즉시 기록한다.
- planning dirty worktree의 unrelated paths는 authority input에서 제외하고 preservation-only inventory로 기록한다.
- 다음 fields를 독립적으로 판정한다:
  - `current_authority_reference_resolved`
  - `execution_checkout_matches_current_authority`
  - `derivation_chain_coherent`
  - `source_currency = current | stale | undetermined`
  - `derivation_coherence = coherent | incoherent | unknown`
  - `commit_ancestry_verified`
- Phase 0은 reference set의 `registry_current_facts_sha256`와 finalized packet의 `rendered_source_facts_sha256`, reference set의 `registry_current_input_manifest_sha256`와 packet의 `rendered_source_input_manifest_sha256`, packet의 rendered artifact identity와 immutable candidate bytes/`meta`/`entries_sha256`를 각각 exact 비교한다. 두 input-manifest fields는 complete manifest raw bytes SHA-256여야 하며 constituent/basis 대체, 자유형 assertion 또는 alternate comparison branch를 허용하지 않는다.
- input manifest 내부 constituent hashes/counts, runtime manifest-derived chunks와 package projection을 이어서 직접 결속한다. materialize되지 않은 binding은 `unknown`으로 보존하며 success로 승격하지 않는다.
- `required_lineage_commit_set_v1`은 두 class를 분리한다.
  - `historical_roots`: predecessor RTC implementation `7d253c91b87abb7f1e044acf3953504180848682`, predecessor RTC integration `c6e2190e7b093b29bc5d615523ae29cf32560ff1`, Registry Authority closure `63357b7afb879f89c4f43df67ad0d39a060561fb`
  - `current_lineage`: synchronized integration `c0eb88a64a08c50fb3f581ee53a0502bd2445195`, current source adoption `e56c2e0c94aed8f31a61cb27cd6e37f0037451c8`, finalized G4 terminal closeout commit/tree, finalized G5 terminal-finalize/handoff commit/tree
- G4/G5 values는 G5 finalized receipt가 hash-bind한 terminal artifacts에서 동적으로 추출한다. Artifact path/SHA-256와 commit/tree가 missing, ambiguous 또는 서로 불일치하면 set을 만들지 않고 upstream/reference eligibility를 blocked로 유지한다.
- `current_lineage_ancestry_report_v1.json`은 각 required commit과 reservation execution commit에 대해 exact `git merge-base --is-ancestor <required_commit> <target_commit>` argv, exit code와 boolean을 기록한다. 하나라도 false/unknown이면 fixed code `blocked_current_lineage_ancestry_failed`로 candidate construction을 금지한다. 이 report와 commit-set manifest의 SHA-256은 reservation에 직접 결속한다.
- current required gate의 first failure와 별개로 source applicability, input-manifest applicability, validation contract, required-gate selection, lifecycle applicability, source currency와 derivation coherence를 모두 terminal disposition으로 열거한다.
- D-03 선택에 따라 commit/tree/blob identity를 authority basis로, raw checkout SHA-256·encoding·BOM·EOL·normalized hash를 execution evidence로 기록한다.
- resolved/matches/coherent/ancestry 중 하나라도 false 또는 unknown이면 candidate construction을 금지하고 observed hashes, reference, execution HEAD, verdict, evidence 목록과 routing scope를 결속한 blocked terminal attempt를 남긴다.

Validation:

- attempt reuse `0`
- open attempt `0` before reservation
- cold ledger/orphan reservation disposition present
- predecessor byte mutation `0`
- protected surface baseline captured
- every failure axis has a terminal disposition; `unknown` is retained with blocked routing
- resolved/matches/coherent/ancestry are independently reported
- reservation binds exact source-reference-set/finalized-rendered-handoff hashes under `rtc_reservation_current_source_and_finalized_rendered_handoff_binding_v2`
- reservation intake recomputes `discovery_identity_core_v1` ID and rejects derived-field/core cycles before attempt allocation
- no plan-review or separate governance-decision artifact is consumed before attempt allocation
- reservation binds fixed `g1_pre_adoption` and `general_default_consumer_policy_before_terminal=fail_closed` literals directly; they are not external inputs
- current source facts/input identity equals finalized-handoff-declared rendered source identity
- handoff artifact identity equals immutable candidate bytes/meta/entries hash
- missing/wrong Registry or DVF complete input-manifest SHA, constituent-only basis and free-form derivation basis each produce `blocked_upstream_artifact_incoherent`
- reservation execution commit descends from every historical/current member of `required_lineage_commit_set_v1`
- exact G4/G5 artifacts on a non-descendant branch and synchronized-integration non-descendant fixtures each produce `blocked_current_lineage_ancestry_failed`
- Phase 0 halt evidence durability and terminal ordering
- identity basis present; final toolchain freeze is intentionally not claimed yet

---

### Change 3 — Toolchain Census, Lane Adjudication, Minimum Alignment and Freeze

Purpose:

측정 도구를 바꾸기 전에 dependency universe와 drift를 read-only로 닫고 lane을 선택한 뒤, 선택된 lane에 필요한 최소 alignment만 수행하여 exact implementation freeze commit/tree와 primary fresh checkout을 만든다.

Files:

- RTC analyzer/runner/validator/closeout
- exporter/Windows wrapper/package script
- RTC focused tests and fixtures
- `.gitattributes`

Implementation Notes:

- Change 3a는 code mutation `0`인 census/classification 단계다. 각 path를 `unchanged`, `representation_only`, `non_contract_text`, `test_contract_change`, `validation_contract_change`, `implementation_semantic_change`, `unknown_or_mixed`로 분류하고 ambiguity를 억지로 0으로 바꾸지 않는다.
- Change 1의 direct inspection matrix는 repository-file toolchain이 아니라 version/hash/argv가 기록된 external diagnostic receipts다. pre-entry helper나 validator mode는 현재 존재하지 않고 이 계획도 Change 1에 추가하지 않는다. 이후 자동화 제안이 생기면 Change 3b에서 신규 file/dependency로 명시하고 lane, test, freeze commit에 포함하기 전에는 claim-bearing input으로 사용할 수 없다.
- 9개 roadmap seed path에서 시작해 static imports, dynamic import targets, subprocess targets, PowerShell-invoked scripts, data/fixture reads를 fixed point까지 추적한다. 각 dependency는 다음 terminal class 중 하나를 가져야 한다:
  - `repo_tracked_executable_dependency`
  - `dynamic_import_target`
  - `subprocess_target`
  - `external_executable_receipt`
  - `python_interpreter_or_package_environment`
  - `diagnostic_only_dependency`
  - `excluded_runtime_or_stdlib_dependency`
- 미분류 또는 `unknown_or_mixed` dependency는 evidence에 그대로 남기고 `blocked_toolchain_dependency_classification`으로 중단한다.
- `.gitattributes` change가 RTC-bound path bytes/checkout representation에 미치는 효과를 path별로 측정한다.
- Change 1의 one-checkout feasibility가 PASS가 아니거나 finalized handoff packet을 포함한 required input state가 `unknown`이면 Change 3b에 들어가지 않는다.
- lane adjudication은 다음 fixed input set과 exclusion relation을 사용하고 lane 선택 전에 contract code를 수정하지 않는다:

| Decision input | Required interpretation | Lane effect |
|---|---|---|
| path/dependency census | all terminal-classified, no unresolved executable edge | unresolved이면 all lanes blocked |
| current-manifest declared vs derived denominator | exact declaration present and equality possible | missing/mismatch면 `blocked_denominator_binding_required`; hardcoded authority dependency면 revalidation lane |
| input-manifest binding | current exact manifest already bound or contract change needed | binding-only이면 source-binding lane; schema/validator change면 revalidation lane |
| `.gitattributes` impact | no RTC byte/identity effect, representation-only, or contract-affecting | no effect/equivalent면 equivalent lane; contract effect면 revalidation; unknown이면 blocked |
| validation-contract drift | stale/current fields, hardcoded count, dependency coverage | any required contract change forces revalidation lane |
| implementation-semantic drift | measuring algorithm behavior changed or unchanged | semantic drift forces revalidation; unexplained drift blocks |
| source-only applicability drift | source changed while exact measuring contract remains applicable | source-binding lane eligible |
| collision/disposition drift | member/payload/policy artifact exact applicability | drift blocks RTC and routes D-05; no drift permits selected lane |

- exactly one of `lane_a_source_binding_successor`, `lane_b_current_toolchain_equivalent_successor`, `lane_c_current_toolchain_contract_revalidation` or a named blocked lane must result. Multiple eligible lanes or incomplete input is blocked.
- Change 3b는 selected lane이 요구하는 최소 alignment만 수행한다. 필요할 때만 hardcoded `2105` completeness/Lua expected count를 제거하고 authority-bound denominator fields, current input-manifest binding, separated stale/current result fields와 diagnostic concurrent inventory를 추가한다.
- successor contract에는 current source/finalized-handoff complete input-manifest SHA equality, project-owner exact-result seal, closeout/default-route mechanical invalidation과 their negative fixtures가 필요하다. Change 3a 시점에도 이 기능이 없다면 이는 `validation_contract_change`이며 `lane_c_current_toolchain_contract_revalidation`을 강제한다; equivalent/source-binding lane으로 축소할 수 없다.
- synchronized readpoint의 직접 관찰은 current RTC input-manifest bound input 부재와 exact current source/finalized-handoff complete-manifest equality gate 부재를 보여 주므로 `planning_readpoint_expected_lane=lane_c_current_toolchain_contract_revalidation`이다. 따라서 실질 adjudication 범위는 기본적으로 `lane_c eligibility vs named blocked lane`이며, Change 3a census가 이 관찰을 already-present dependency로 명시적으로 뒤집을 때만 lane_a/lane_b를 다시 고려한다. 세 lane 표는 그 반증 가능성을 보존하는 taxonomy이지 동등 확률의 자유 선택지가 아니다.
- input-manifest binding과 successor schema 변경이 선택 lane에 필요하지 않으면 수행하지 않고 disposition을 기록한다. historical v1 bundle validation은 current fallback 없이 유지한다.
- `.gitattributes` 수정이 필요하면 RTC-bound paths의 checkout/identity semantics만 좁게 다룬다. repository-wide `git add --renormalize .`는 금지하며 RTC 밖 renormalization이 필요하면 별도 scope로 중단한다.
- alignment diff와 tests를 commit하여 `implementation_freeze_commit`/tree를 만든다. uncommitted worktree hash는 authority toolchain이 아니라 execution receipt다. Phase 0의 exact `required_lineage_commit_set_v1` 각 commit에 대해 freeze commit ancestry를 다시 계산하고 같은 set digest를 가진 새 `current_lineage_ancestry_report_v1`을 봉인한다. false/unknown이면 `blocked_current_lineage_ancestry_failed`다.
- freeze commit에서 primary fresh checkout을 생성하고 tracked inputs와 exact finalized Registry-facing rendered handoff packet 및 packet-bound candidate만 존재하는지 확인한 뒤 final repository-file toolchain identity를 recapture한다.
- `canonical_execution_environment_identity`는 executable file identities/versions, Python package or lock-state digest, relevant OS/runtime/architecture/locale facts와 accepted Lua identity를 canonicalize한다. absolute checkout path, timestamp, run ID와 temp root는 제외한다.
- 각 `per_run_execution_receipt`는 canonical environment identity SHA-256, checkout path, timestamp, run ID, command/exit code와 raw executable paths를 포함한다. successor canonical content는 canonical environment identity를 결속하고 raw receipts는 evidence manifest로만 결속한다.
- primary/reproduction checkouts는 canonical environment identity가 같아야 한다. equality는 cross-host portability 또는 hermetic environment를 의미하지 않는다.
- Phase 0 verdict의 freeze handling을 다음처럼 고정한다:

| Verdict/evidence | Freeze commit handling |
|---|---|
| authority record identity | exact record/hash binding으로 계승 |
| declared denominator identity | exact current-manifest field/hash binding으로 계승 |
| source currency | freeze checkout에서 재측정·재도출 |
| derivation coherence | freeze checkout에서 재검증 |
| commit ancestry | freeze commit에서 재도출 |
| protected-surface baseline | freeze checkout에서 재측정 |
| D-01 input feasibility | finalized handoff packet과 packet-bound candidate를 포함한 fresh checkout에서 재실행 |

- 이후 toolchain byte, commit/tree 또는 declared dependency drift가 있으면 candidate를 만들지 않는다.

Validation:

- 9/9 seed paths terminal disposition
- discovered direct/transitive dependencies terminal disposition
- dependency classification fixed point reached
- unresolved dependency is retained and blocks rather than being forced to zero
- lane selected before alignment mutation
- lane input/exclusion matrix is fully enumerated and exactly one lane results
- selected-lane minimum diff only
- planning expected lane_c rationale recorded; adjudication resolves lane_c eligibility or a named blocked lane unless census evidence explicitly falsifies the planning observations
- hardcoded current denominator authority dependency `0` when alignment lane is selected
- old predecessor current fallback `0`
- stale fixture와 positive fixture 동시 유지
- freeze commit contains exact executed toolchain
- freeze commit descends from every dynamically finalized historical/current lineage member and binds the ancestry-report hash
- primary fresh checkout identity equals freeze commit/tree/blob manifest
- Phase 0 inherited/re-derived verdict table satisfied
- canonical environment identity equals across checkouts
- repository-file toolchain manifest, canonical environment identity and per-run receipts are separate

---

### Change 4 — Authority-Bound Compatibility Universe, Denominator and Collision Re-Derivation

Purpose:

current source authority reference set에서 exact key universe와 collision universe를 다시 계산하고 denominator의 independent drift tripwire를 닫는다.

Files:

- RTC analyzer and validator
- attempt-local source/surface/collision reports
- sealed collision disposition input

Implementation Notes:

- source는 authority reference가 지정한 exact facts/input manifest와 constituent files의 FullType join contract로 구성한다. 이 단계는 Phase 0에서 `registry_current_input_manifest_sha256 == rendered_source_input_manifest_sha256` exact raw-byte identity가 먼저 PASS한 경우에만 들어간다.
- `declared_denominator`는 exact current input manifest의 facts row count에서 읽고 RTC가 생성·수정하지 않는다. `derived_denominator`는 같은 manifest와 source join에서 파생한다. `observed_exact_key_count`는 source/rendered/bridge/runtime/package surface별로 독립 측정한다.
- 다음 3-way equality와 exact key-set equality를 모두 요구한다:

```text
declared_denominator
= derived_denominator
= observed_exact_key_count on every validated surface
```

- declaration 누락 또는 불일치는 predecessor `2105`로 대체하지 않고 `blocked_denominator_binding_required`로 current source authority 경계에 routing한다. `2105`는 predecessor historical comparison evidence일 뿐 current constant가 아니다.
- rendered, isolated bridge, reconstructed runtime와 isolated package surface의 exact decoded keys를 비교한다.
- source→rendered, rendered→bridge, bridge→runtime, runtime→package 각 edge에서 per-key canonical payload hash를 검증한다.
- `ascii_lower_v1` collision inventory를 current source에서 재생성한다.
- `Base.LemonGrass`와 `Base.Lemongrass`는 독립 exact entries로 유지한다.
- 기존 `reference + exception` disposition은 current member set, comparison key와 모든 edge payload binding이 동일할 때만 successor에 다시 결속한다.
- D-05 project-policy input은 current disposition artifact applicability와 escalation routing에만 적용한다. no rename/no merge/no alias/no winner selection은 fixed sealed constraint다.
- new collision, member drift 또는 payload divergence가 있으면 D-05에 따라 halt한다.
- final lane은 Change 3에서 선택된 lane과 관찰 결과가 일치해야 한다. 불일치는 사후 lane 재분류가 아니라 새 census/alignment attempt를 요구한다.
- final bound generation 전에 생긴 bridge/chunk/package intermediate는 `diagnostic_only_unbound`로 표시하고 candidate, PASS, review 또는 live adoption evidence에서 제외한다.

Validation:

- current-manifest declared/derived/observed denominator 3-way equality
- predecessor numeric equality is not authority reuse
- exact missing/additional key `0`
- per-key payload mismatch `0`
- exact duplicate `0`
- unauthorized collision `0`
- alias-emitted new key `0`
- no-live-mutation feasibility

---

### Change 5 — Immutable Successor Candidate and Lineage

Purpose:

final frozen toolchain과 current source-payload proof를 결속한 content-addressed successor candidate를 만든다.

Files:

- candidate root under attempt
- durable bundle schema inputs
- attempt and lifecycle ledgers

Implementation Notes:

- candidate seal 직전에 current source authority reference set, source/input constituent hashes, finalized handoff/candidate metadata, runtime manifest/chunks와 package input binding을 Phase 0 snapshot에 다시 비교한다.
- `protected_surface_no_mutation_status`와 `upstream_concurrent_drift_status`를 별도 fields로 기록한다. 이 round가 파일을 쓰지 않았다는 사실로 upstream drift absence를 추론하지 않는다.
- drift가 있으면 `blocked_upstream_concurrent_mutation`으로 중단하고 새 authority reference 또는 새 attempt 없이는 계속하지 않는다.
- bundle canonical content에는 authority record path/ID와 SHA-256, `registry_current_facts_sha256`, `registry_current_input_manifest_sha256`, `rendered_source_facts_sha256`, `rendered_source_input_manifest_sha256`, finalized handoff/candidate hashes, authority and execution commit/tree, exact `required_lineage_commit_set_v1` SHA-256, freeze-target `current_lineage_ancestry_report_v1` SHA-256, identity basis, repository-file toolchain manifest, denominator 3-way evidence, edge bindings, collision disposition, selected lane와 predecessor lineage를 포함한다. Current-source/finalized-handoff facts와 complete input-manifest hash pairs는 각각 exact equality여야 한다.
- bundle canonical content는 `canonical_execution_environment_identity` SHA-256을 결속한다. per-run receipts는 evidence manifest에 별도 hash-bind하며 repository-file toolchain identity나 cross-environment reproducibility claim으로 합치지 않는다.
- timestamps, absolute paths, username와 temp roots는 canonical bundle ID에서 제외하고 execution receipts에만 둔다.
- predecessor bundle ID, manifest hash, lifecycle state, predecessor terminal/integration commits, Registry Authority closure commit, synchronized integration commit, current source adoption commit, dynamically extracted G4/G5 terminal commits/trees와 skipped/unbound generation 여부를 lineage에 기록한다.
- predecessor bundle bytes와 event records를 수정하지 않는다.
- candidate state에서는 live manifest, default exporter와 default package route가 candidate를 소비하지 못하게 한다.
- candidate bundle ID를 canonical content에서 재계산해 일치시킨다.

Validation:

- schema and content-address verification
- predecessor mutation `0`
- lineage ambiguity `0`
- commit ancestry verified
- exact commit-set/ancestry-report hash binding verified; G4/G5 or synchronized integration non-descendant is BLOCKED
- volatile canonical field `0`
- candidate live consumption `0`
- final toolchain drift `0`
- source drift `0`
- protected no-mutation and concurrent drift independently reported

---

### Change 6 — Isolated End-to-End Compatibility Proof

Purpose:

live payload를 쓰지 않고 current source부터 package projection까지 실제 consumer transport를 검증한다.

Files:

- exporter
- runtime chunk validator
- Lua merge harness
- Windows record exporter/wrapper
- package script
- attempt-local isolated outputs

Implementation Notes:

```text
current rendered + candidate contract
-> bridge pre-materialization validation
-> isolated chunk export
-> cross-chunk validation
-> actual PUC Lua merge/reconstruction
-> isolated package projection
-> unconditional package guard
-> Windows Route A
-> Windows Route C JSONL records
-> live payload parity comparison
```

- 모든 writer에 explicit attempt-local output root를 전달한다.
- exporter와 package wrapper의 default live resolution은 이 단계에서 사용하지 않고 explicit candidate probe만 사용한다.
- candidate package projection은 기존 `Iris/tools/package_iris.ps1`의 `-RegistryCompatibilityProbe`를 사용하고 ZIP을 만들지 않는다. Change 8의 internal adoption-transaction receipt surface 외 새 public package mode를 추가하지 않으며 어떤 receipt도 guard bypass 권한을 갖지 않는다.
- actual Lua executable/version/path를 receipt에 기록하고 accepted version은 현재 contract의 Lua 5.1.x 또는 5.4.x로 제한한다.
- PUC Lua proof를 Kahlua/PZ runtime equivalence로 확대하지 않는다.
- Route A는 canonical Python analyzer algorithm proof, Route C는 exact identity별 UTF-8 JSONL transport conformance proof로 유지한다.

Validation:

- bridge preflight PASS
- isolated chunk generation and cross-chunk uniqueness PASS
- actual Lua merge/reconstructed exact universe PASS
- isolated package surface PASS
- Route A/C record and payload parity PASS
- Lua syntax PASS
- isolated/live canonical parity
- protected live payload changed count `0`

---

### Change 7 — Negative, Adversarial and Determinism Validation

Purpose:

stale evidence, toolchain drift, key loss, bundle misselection과 claim overreach를 fail-closed로 차단한다.

Files:

- RTC fixture manifest
- focused RTC tests
- attempt-local negative and determinism reports

Implementation Notes:

- roadmap의 최소 negative fixtures를 모두 구현·유지한다: stale facts, stale manifest, 각 bound path drift, missing path, untracked substitute, bundle tamper, predecessor selection, environment override, unauthorized collision, case merge, bridge/runtime/package/Windows loss, lifecycle ordering, claim overreach.
- negative test는 synthetic manifest/temp roots를 사용하며 live authority를 변경하지 않는다.
- positive current candidate assertion과 stale-state expected BLOCKED assertion을 별도 test/report로 둔다.
- primary fresh checkout에서 successor build/positive validation을 반복해 same-checkout determinism을 확인한다.
- 같은 final freeze commit에서 independent reproduction fresh checkout을 새로 만들고 tracked repository inputs와 exact same finalized handoff packet/packet-bound candidate artifact만으로 successor build와 positive validation을 다시 실행한다.
- primary/reproduction checkout의 canonical bundle ID, bundle manifest, equivalence matrix, collision evidence, Windows result와 claim-bearing validation inputs가 일치해야 한다. absolute path와 timestamps 같은 receipt-only fields는 canonical parity에서 제외한다.
- primary/reproduction checkout의 canonical environment identity는 같고 per-run path/time/run IDs는 달라도 된다.
- fresh checkout input 시점의 ignored/untracked dependency, unapproved generator output와 undeclared local input은 `0`이어야 한다. finalized handoff packet이 지정한 tracked candidate artifact는 explicit isolated input으로만 소비하고 generated outputs는 explicit isolated output root에만 쓴다.
- D-01 hard gate에 따라 clean-checkout result가 `failed` 또는 `not_run`이면 `registry_runtime_compatibility_canonical_complete`, live adoption과 RTC PASS를 금지하고 blocked terminal evidence를 남긴다.

Validation:

- all negative fixtures expected BLOCKED
- exact expected failure class/stage/code
- positive candidate PASS 유지
- same-checkout repeat parity
- primary/reproduction fresh-checkout canonical parity
- finalized handoff packet/candidate hash parity
- canonical environment identity parity with separate per-run receipts
- ignored/local undeclared dependency `0`
- tracked protected mutation `0`
- stale guard/current PASS confusion `0`

---

### Change 8 — Pre-Adoption Full-Repository Gate, Reviewed Live Adoption and Closeout

Purpose:

exact verified successor와 projected live manifest를 G1 fresh A/B로 먼저 검증한 뒤 live required-validation에 결속하고 review/seal/terminal ordering을 닫는다.

Files:

- durable successor bundle
- `g1_pre_adoption_handoff.json` and append-only G1 successor
- `current_route_required_validations.json`
- exporter/package default resolution
- project-owner exact-result seal schema/validator and machine lifecycle invalidation guard
- durable closeout packet
- attempt/lifecycle ledgers
- top-level docs

Implementation Notes:

- predecessor-era whole-manifest SHA equality를 adoption gate로 사용하지 않는다. `attempt-0009` bundle/evidence/lifecycle에서 predecessor RTC-owned required-artifact/test rows, selected bundle/manifest identity, lifecycle/closeout references와 default-resolution contract를 별도 preservation set으로 재구성한다.
- current live manifest를 whole-file SHA-256, all-row inventory, required-artifact/test/role denominators, unrelated additive rows, active RTC selector와 duplicate/conflicting selector counts로 recensus한다.
- exact candidate와 intended additive diff는 current recensus SHA-256을 `pre_adoption_reviewed_current_manifest_sha256`로 결속한다. Fresh isolated pre-adoption Codex review session은 implementation-complete bundle, candidate, predecessor preservation set, unrelated-row preservation, lifecycle event와 rollback behavior를 검토해 blocker `0`을 확인한다. 이 session은 implementation/plan authoring context를 상속하거나 참여하지 않고 exact review-input manifest와 context-isolation receipt를 attestation에 결속한다.
- 이 repository의 default exporter/package/current-route에 concurrent invocation 가능성이 있으므로 adoption executor는 existing single-writer/exclusive-lock precedent, reviewed-base CAS, same-filesystem temporary write, atomic replace와 manifest-last ordering을 사용한다. 별도 외부 계정, Windows 관리자 권한, OS 감사정책, reviewer availability lease 또는 credential ceremony를 요구하지 않는다.
- adoption rehearsal 전에 reviewed current-manifest bytes에 exact reviewed additive diff를 동일 serializer로 in-memory 적용해 `projected_post_adoption_live_manifest`를 만든다. Scratch manifest는 projected bytes와 byte-identical해야 하며 exact byte size, all-row count, required-artifact/test/role denominators, selector structure/counts, unrelated additive-row identity와 validation fan-out equality를 검사한다.
- same-filesystem scratch에서 atomic replace, rollback snapshot과 failure-injection을 검증한다. Rehearsal success는 live mutation 권한이 아니며 프로젝트 소유자의 exact adoption authorization이 별도로 필요하다.
- rehearsal, isolated pre-adoption review와 candidate evidence를 commit하여 `adoption_ready_commit`/tree를 고정한다. 이 commit은 exact `required_lineage_commit_set_v1` 전체의 descendant여야 하고 adoption-ready ancestry report를 새로 봉인한다.
- `g1_pre_adoption_handoff.json`은 adoption-ready commit/tree, immutable candidate bundle/manifest, projected post-adoption live manifest bytes/SHA-256, reviewed additive diff, current source/finalized handoff, required lineage set/report, full command/test denominator와 pre-adoption review attestation SHA-256을 직접 결속한다.
- G1은 live manifest/default selector를 바꾸지 않고 handoff가 지정한 adoption-ready commit을 primary/reproduction fresh checkout으로 열어 exact projected manifest와 candidate를 explicit validation input으로 소비한다. Run A/B, current-route full repository command matrix, test denominator와 canonical result가 모두 PASS인 새 append-only G1 successor만 허용한다.
- G1이 failed, incomplete, not-run, input/hash mismatch 또는 non-descendant이면 `blocked_pending_full_repository_reverification`다. Candidate는 immutable evidence로 남기지만 live repoint, transaction acquire, default selection, official route, owner repoint authorization과 terminal closeout을 금지한다.
- G1 PASS 뒤 repository-file toolchain, candidate, source/handoff binding, reviewed diff와 projected live manifest drift `0`을 재확인한다. 프로젝트 소유자의 repoint authorization은 exact G1 successor, adoption-ready commit/tree, candidate, reviewed base/diff와 transaction contract를 함께 승인해야 한다.
- durable transaction surface는 `adoption_transactions/<attempt-id>/`의 immutable acquire/success/invalidation records와 hash-chained `adoption_transaction_events.jsonl`이다.
- acquire record는 attempt/bundle/manifest identities, reviewed-current base SHA-256, pre-adoption Codex review SHA-256, G1 successor SHA-256, adoption-ready lineage report SHA-256, project-owner authorization SHA-256, one-time nonce hash, exact executor/toolchain identity, allowed command digests와 `acquired_at_utc`를 포함한다.
- acquire authority는 isolated Codex Reviewer PASS, G1 pre-adoption PASS와 project-owner authorization을 소비하는 RTC adoption executor에만 있다. Nonce/receipt 재사용은 금지한다.
- acquire 직전 reservation/transaction contract의 fixed `general_default_consumer_policy_before_terminal=fail_closed` literal과 실제 default-consumer guard behavior를 재검증한다. Missing/drift/alternate value면 transaction을 만들지 않고 `blocked_preterminal_default_guard_mismatch`다.
- exporter default resolver, current-route runner, validator와 `Iris/tools/package_iris.ps1`는 open or failed adoption transaction을 fail closed로 검사한다. `-RegistryCompatibilityProbe`는 compatibility/no-ZIP selector일 뿐 executor authentication이나 guard bypass가 아니다.
- live repoint 직전 observed current manifest SHA-256은 `pre_adoption_reviewed_current_manifest_sha256`와 같아야 한다. mismatch면 CAS conflict로 transaction을 invalidated 처리하고 새 recensus/review 없이 patch를 재계산하지 않는다.
- reviewed diff는 predecessor RTC rows removed/mutated/reclassified `0`, unrelated current rows changed `0`, exact successor rows only added, active successor selector `1`, duplicate/conflicting selector `0`을 요구한다.
- candidate validation, D-01 hard gate와 G1 pre-adoption full-repository gate가 닫힌 뒤 successor를 durable bundle로 promote하고 live selection을 exact bundle ID/manifest hash로 additive repoint한다.
- adoption은 additive다. historical predecessor artifact/test rows와 lifecycle events를 삭제하지 않는다.
- predecessor bundle에는 `superseded` lifecycle event를 append하되 byte identity를 유지한다.
- live repoint 직전에 current authority reference, source/input/rendered/runtime binding을 다시 측정한다. concurrent drift면 repoint하지 않는다.
- transaction-scoped post-adoption exporter/package official route가 live manifest의 exact successor만 선택하는지 검증하고, terminal 전 일반 no-arg/default invocation은 lifecycle guard로 fail closed하는지 함께 확인한다.
- current required gate는 actual current surface validation을 실행하며 stored predecessor PASS를 읽어 current PASS를 만들지 않는다.
- exact adopted successor를 소비하는 official current-route를 실행하고 `claim_bearing_official_current_route_result`와 SHA-256을 생성한다.
- repoint, official route, default package guard 또는 result persistence가 실패하면 transaction은 failed/invalidation event를 append하고 default consumers를 `no applicable current RTC selection`으로 fail closed한다.
- orphan reconciliation은 프로젝트 소유자의 새 one-time recovery authorization과 nonce를 가진 recovery executor만 수행한다. Acquire record를 삭제/수정하거나 adoption nonce를 재사용하지 않고 additive invalidation event를 append한 뒤 unsealed successor selector를 제거한다. Predecessor selector는 복귀시키지 않는다.
- machine route/package/result가 PASS면 transaction success event를 append하고 lock을 release한다. Terminal closeout 전 lifecycle은 `adopted_pending_closeout`이며 transaction-scoped official verification 외의 일반 default exporter/package consumer는 fail closed한다. General default consumption은 success terminal event 뒤에만 열린다.
- live repoint 뒤 bounded determinism을 다시 실행해 pre-adoption candidate, clean-checkout canonical result와 transaction-scoped post-adoption official-route result가 일치하는지 확인한다.
- exact adopted commit/tree가 `required_lineage_commit_set_v1` 전체의 descendant인지 다시 계산한다. Adopted-target ancestry report는 candidate가 결속한 same commit set digest를 사용하며 failure는 `blocked_current_lineage_ancestry_failed`와 additive transaction invalidation을 만든다.
- post-adoption closeout review는 exact adopted bundle, adoption diff, official current-route result, post-adoption bounded determinism, adopted-target ancestry report와 G1 pre-adoption successor를 대상으로 pre-adoption reviewer와 다른 fresh isolated Codex session이 수행한다. 동일 `Codex Reviewer` role/model family taxonomy를 써도 session/task/context는 재사용하지 않으며 closeout은 `review_role_reused=true`, `review_session_reused=false`, `self_confirmation_relation=false`, independent-credit limitation을 기록한다.
- project-owner seal은 exact adopted successor bundle ID/manifest SHA-256, adoption diff, official result와 closeout review SHA-256을 봉인한다. 사용자 지시를 기계적으로 재현할 수 있는 decision record와 hash binding이면 충분하며 SSH key, public credential, 별도 succession authority는 요구하지 않는다.
- Post-terminal contradictory evidence가 검증되면 lifecycle validator가 append-only `post_terminal_regression_failure` event를 기록하고 `current_claim_state=invalidated`, `current_selection_state=no_applicable_current_rtc_selection`으로 즉시 내린다. 이는 사람의 부재를 가장한 승인이 아니라 machine-observed contradiction에 대한 fail-close다. 후속 correction/adoption에는 프로젝트 소유자의 새 exact-result 승인이 필요하다.
- durable closeout packet을 commit한 뒤에만 success terminal event를 append한다.
- closeout validator도 reservation/transaction contract의 fixed `general_default_consumer_policy_before_terminal=fail_closed`와 실제 guard evidence를 §11/§12 constraint에 다시 대조한다. 이 check는 Change 2/acquire 검사 대체가 아니라 final consistency check이며 mismatch는 terminal을 금지한다.
- closeout packet과 terminal record는 claim-bearing official result SHA-256, both isolated Codex review SHA-256 values, G1 successor SHA-256, pre-terminal guard evidence SHA-256, project-owner seal SHA-256, adopted bundle/manifest hashes, current authority reference-set SHA-256, exact required lineage commit-set SHA-256와 adopted-target ancestry-report SHA-256을 직접 결속한다. Exact binding이 PASS하지 않으면 terminal event를 쓸 수 없다.
- terminal state는 기존 RTC lifecycle vocabulary인 `registry_runtime_compatibility_canonical_complete`만 사용한다.
- terminal 뒤 `DECISIONS.md`에는 successor decision을 append하고, `ARCHITECTURE.md`의 RTC canonical current readpoint를 교체하면서 predecessor trace를 보존하며, `ROADMAP.md` current summary를 갱신하면서 historical/attachment SHA-256 provenance를 유지한다.
- top-document 변경 후 official route 재실행은 `post_terminal_documentation_regression`인 non-claim evidence다. 이 결과는 terminal claim을 만들거나 소급 수정하는 데 사용하지 않는다.
- post-terminal regression 실패는 sealed evidence를 편집하지 않는다. Lifecycle validator가 exact failed regression receipt와 terminal/bundle/manifest hashes를 결속한 additive invalidation event를 append해 current applicability를 fail closed로 내린다. 어느 경로도 predecessor fallback을 허용하지 않는다.

Validation:

- no fresh plan-review or separate governance-decision prerequisite is consumed
- reservation, transaction acquire and closeout all enforce fixed `g1_pre_adoption` and `general_default_consumer_policy_before_terminal=fail_closed` constraints directly
- missing/drifted/alternate pre-terminal guard behavior produces `blocked_preterminal_default_guard_mismatch` before live mutation
- isolated pre-adoption Codex Reviewer verdict, session/context independence receipt and exact hash coverage
- adoption-ready commit/tree ancestry against every required historical/current lineage member
- G1 pre-adoption handoff exact projected-manifest/candidate/commit binding
- fresh full-repository clean-checkout Run A/B PASS and new append-only G1 successor before transaction acquire
- G1 failure/incomplete/not-run produces `blocked_pending_full_repository_reverification` with live mutation/default consumption `0`
- project-owner repoint authorization binding
- exclusive lock, reviewed-base CAS, atomic replace, manifest-last and rollback guards proven
- projected-live/scratch byte identity plus row/denominator/selector/unrelated-row/fan-out and same-filesystem write-path equivalence
- predecessor RTC preservation-set equality
- current manifest recensus and reviewed-base SHA binding
- pre-write optimistic CAS equality
- unrelated current row mutation `0`
- active RTC successor selector `1`; duplicate/conflicting selector `0`
- adoption transaction acquire/success/invalidation state-machine tests
- unauthorized/missing/replayed executor transaction receipt expected BLOCKED
- orphan transaction recovery and no-predecessor-fallback tests
- selected/adopted/reviewed/sealed bundle identity equality
- pre-terminal claim-bearing official current-route actual RTC PASS
- stale negative guard PASS
- transaction-scoped exporter/package official route selects the exact successor and post-terminal default selection matches it
- post-adoption bounded determinism PASS
- adopted commit/tree ancestry against the same required lineage commit-set
- predecessor fallback `0`
- distinct isolated post-adoption Codex Reviewer session/context and exact hash coverage
- closeout disclosure records role reuse, session non-reuse, no self-confirmation and `procedural_session_independence` ceiling
- project-owner seal exact successor/adoption/result/review coverage
- missing/wrong project-owner decision, bundle hash, adoption diff, result hash and replayed authorization expected BLOCKED
- post-terminal contradictory evidence produces mechanical invalidated/no-applicable-current state
- closeout-before-terminal ordering
- final protected surface mutation `0`
- final source drift `0`
- post-terminal documentation regression is explicitly non-claim
- authorized `post_terminal_regression_failure` event forces invalidated/no-applicable-current state

---

## 7. Validation Plan

### Automated Validation

Environment and exact executable identity를 receipt에 먼저 기록한 뒤 다음 validation families를 실행한다.

```powershell
uv run python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_dvf_3_3_registry_runtime_compatibility_*.py"
```

```powershell
uv run python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_registry_runtime_compatibility.py --required-gate --required-manifest Iris\_docs\round3\current_route_required_validations.json --out <attempt-output>
```

```powershell
uv run python -B Iris\_docs\round3\round3_run_contract_tests.py --class current --required-validations Iris\_docs\round3\current_route_required_validations.json --enforce-current-build-closure --out <attempt-output>
```

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Candidate package projection은 explicit attempt-local output root, explicit candidate contract와 `-RegistryCompatibilityProbe`를 사용하고 `-Zip`을 사용하지 않는다. G1 pre-adoption package 검증은 exact projected live manifest를 explicit override로 사용한다. Post-adoption package 검증은 transaction-scoped official route에서 live manifest resolution을 사용하되 publication artifact를 외부로 배포하지 않으며, 일반 default consumer는 terminal 전 fail closed다.

추가 automated checks:

- attempt-independent discovery observation schema/content-address/immutability
- canonicalizer-bound discovery identity fixtures cover duplicate-key rejection, exact jq binary/version/argv/locale identity, number/Unicode output, UTF-8/no-BOM/single-terminal-LF removal, two-run byte identity and canonicalizer-change ID separation
- `discovery_identity_core_v1` fixed allowlist/exclusion and reconstruction fixtures: changed ID mismatch; content-manifest/derived-path change stable; fact change changes ID; forbidden derived-field inclusion BLOCKED
- observation-level success and `entry_eligibility_status` are separate; `0 / 1 / >1` reference fixtures produce absent/eligible/ambiguous dispositions
- Change 1 declared external-command provenance and RTC-bound repository-file mutation `0`
- protected-input `git ls-files` / `git check-ignore` inventory and one-checkout feasibility
- `current_source_reference_set_composition_v1` schema/lifecycle/cross-reference validator
- wrong-member/ad hoc union/mtime-latest/path-transition/cross-hash fixtures produce `blocked_reference_set_composition_invalid`; required field removal produces `blocked_reference_set_required_field_missing`
- reservation schema enforces `rtc_reservation_current_source_and_finalized_rendered_handoff_binding_v2`, the exact source reference-set digest and finalized Registry-facing rendered handoff-packet SHA-256
- current source facts/input-manifest SHA-256 values match the finalized handoff packet by one exact algorithm; packet candidate identity equals immutable candidate bytes/meta/entries hash
- missing/wrong complete input-manifest hash, constituent-only substitution, free-form or `rendered_source_derivation_basis` alternative each produce `blocked_upstream_artifact_incoherent`
- execution checkout/reference exact source currency validator
- upstream derivation coherence validator
- `required_lineage_commit_set_v1` contains historical roots plus synchronized integration, current source adoption and dynamically extracted G4/G5 terminal commits/trees
- reservation, freeze, adoption-ready and adopted target ancestry reports run `git merge-base --is-ancestor` for every set member and bind the same set digest
- exact G4/G5 artifacts on a non-descendant branch and synchronized-integration non-descendant fixtures produce `blocked_current_lineage_ancestry_failed`
- concurrent failure inventory
- Git/blob/raw/normalized identity census와 `git check-attr`
- dependency fixed-point inventory and terminal classification
- decision-gate authority-class check: every `sealed_constraint` has cited governing source and no plan-invented transaction/schema/correction mechanism is classified as sealed
- planning lane expectation check: current observations imply lane_c; success may select lane_a/lane_b only with census evidence that explicitly falsifies those observations
- input-manifest constituent binding
- current-manifest declared/derived/observed denominator 3-way equality
- source/rendered/bridge/runtime/package exact-set and payload matrix
- collision and owner-disposition applicability
- actual Lua merge
- Windows A/C parity
- negative fixture matrix
- same-checkout repeat and independent fresh-checkout reproduction parity
- finalized handoff packet/candidate identity and canonical environment parity
- candidate-seal/live-repoint final source drift checks
- predecessor RTC row preservation, current manifest recensus and reviewed-base CAS comparison
- writer/concurrent-consumer inventory and every identified actor guard coverage
- projected-live/scratch byte identity plus row/denominator/byte-size/selector/unrelated-row/fan-out and same-filesystem write-path equivalence
- atomic adoption transaction authorization, reviewed-base CAS, executor, failure-injection, orphan recovery and replay negatives
- reservation/transaction schema fixes `g1_pre_adoption` and `general_default_consumer_policy_before_terminal=fail_closed`; operator-supplied or owner-supplied alternate values are rejected
- missing/drifted/alternate pre-terminal guard behavior produces `blocked_preterminal_default_guard_mismatch`
- pre/post Codex review session IDs differ, implementation context is not inherited, reviewer author/owner participation is false, exact review/implementation hashes match and independence credit is `procedural_session_independence`
- `g1_pre_adoption_handoff` binds adoption-ready commit/tree, projected live manifest, candidate, full denominator and ancestry report; fresh A/B successor PASS is required before transaction acquire
- failed/incomplete/not-run G1 fixture produces `blocked_pending_full_repository_reverification`, live manifest mutation `0` and general default consumption `0`
- terminal-before-general-default-use guard; pending-closeout default consumer fixture fails closed
- machine-observed/replayed `post_terminal_regression_failure` lifecycle event tests; a verified contradiction forces invalidated/no-applicable-current and predecessor fallback remains `0`
- project-owner exact-result seal requires exact successor, manifest, adoption diff, official result and Codex Reviewer attestation hashes; absent or mismatched coverage blocks closeout/terminal
- repository status and protected no-mutation snapshots
- claim vocabulary scan including this plan and all closeout/top-doc candidates
- lifecycle/closeout ordering validator

AGENTS.md 규칙에 따라 각 명령의 exit code가 `0`인 경우에만 해당 validation을 PASS로 기록한다. 도구가 없거나 command가 실행되지 않으면 `blocked` 또는 `not_run`이며 PASS가 아니다.

### Manual Validation

- fresh isolated Codex review session이 implementation-complete bundle과 pre-adoption candidate/diff/transaction을 검토하고 Critical/Important blocker `0`을 명시한다. 구현 session/context 상속이나 authoring 참여가 없어야 한다.
- G1은 exact adoption-ready commit/tree와 projected live manifest를 두 fresh checkout에서 검증하고 append-only successor PASS를 발급한다. 실패·미실행이면 live repoint를 검토하지 않는다.
- live adoption 뒤 별도의 fresh isolated Codex review session이 exact adopted successor, official result, post-adoption evidence와 closeout bundle에 대해 새 attestation을 발급한다. Role/model-family reuse는 disclose하되 session/task/context와 이전 attestation을 재사용하지 않는다.
- 프로젝트 소유자는 reviewed-base CAS, same-filesystem atomic replace, manifest-last ordering, rollback, failure-injection과 exact G1 successor를 확인하고 exact adoption 대상 hashes를 승인한다.
- 프로젝트 소유자는 exact adopted successor bundle ID/manifest, adoption diff, official result와 closeout review SHA-256을 결속한 별도 decision record를 발급한다.
- 프로젝트 소유자와 Codex Reviewer는 D-04a/D-07a/D-10a cited principles와 D-04b/D-04c/D-07b/D-10b mechanisms가 서로 다른 authority classes로 유지되는지 확인한다. Mechanism 변경은 principle 변경으로 오인하지 않되 explicit plan revision과 새 toolchain freeze 없이 바꾸지 않는다.
- operator가 `git diff --stat`, `git diff`와 protected-surface hash inventory로 unexpected mutation을 확인한다.
- operator가 `.gitattributes` diff가 RTC-bound scope 밖 renormalization을 만들지 않았는지 확인한다.
- top-doc update mode가 DECISIONS append / ARCHITECTURE current replacement plus predecessor trace / ROADMAP current summary plus historical provenance를 지키는지 검토한다.
- `docs/EXECUTION_CONTRACT.md`의 claim-evidence binding, validation ceiling, non-claims, historical trace와 `AGENTS.md`의 required document/validation rules 준수를 closeout checklist에 기록한다.

manual in-game 또는 UI 검증은 이 RTC 계획의 success gate가 아니다.

### Validation Limits

- no multiplayer validation
- no long-session gameplay validation
- no Kahlua/PZ runtime equivalence claim
- no deployment validation
- no Workshop upload
- no package publication authorization
- no external mod compatibility sweep
- no B42 validation
- no public text quality acceptance
- no semantic facts correctness or translation quality validation
- no future facts/toolchain applicability
- no full-repository or cross-host/environment reproducibility claim outside the RTC-bounded two-checkout gate
- no environment-independent claim beyond the exact canonical execution environment identity, per-run receipts and repository freeze
- no validated-route 밖의 플랫폼/consumer 보장

---

## 8. Risk Surface Touch

### Authority Surface

변경 있음. Registry Runtime Compatibility axis에 한정한다.

- current applicable RTC bundle
- predecessor-successor lineage
- RTC lifecycle state
- live required-validation의 selected RTC bundle binding
- stale/current applicability와 claim fields
- current source authority reference-set consumption and currency result
- current-manifest declared denominator consumption
- attempt-independent discovery observation and finalized Registry-facing rendered handoff dependency binding
- frozen-plan identity and fixed pre-terminal guard evidence
- project-owner exact-result seal and machine-observed post-terminal invalidation state

source, rendered, runtime chunk, package payload, Registry Authority, DVF Body Compiler와 Publish Boundary authority는 변경하지 않는다.

### Runtime Behavior Surface

변경 없음이 목표이며 hard validation 대상이다.

- Lua renderer behavior 변경 없음
- runtime data shape 변경 없음
- item key/text 변경 없음
- live chunk manifest/chunks 변경 없음

### Compatibility Surface

직접 영향 있음.

- input-manifest/source/rendered/bridge/runtime/package identity
- collision universe and disposition
- exporter/package bundle resolution
- bounded adoption-transaction enforcement and recovery
- Windows Route A/C
- stale source/toolchain rejection
- current positive required-gate consumption
- exact freeze-commit fresh-checkout reproduction
- source concurrent drift and commit ancestry

### Sealed Artifact Surface

새 discovery identity core/full observation, adoption transaction events, additive successor bundle, attempt evidence, lifecycle events, Codex Reviewer attestations, project-owner exact-result seal과 closeout packet이 추가된다. predecessor sealed artifacts는 수정하지 않는다.

### Public-Facing Output Surface

없음.

- Browser/Wiki/Tooltip text 변경 없음
- public quality badge/copy/sort/filter 변경 없음
- release note 또는 Workshop copy 변경 없음

---

## 9. Risk Analysis

### Architecture Risk

- RTC가 Registry Authority나 DVF Body Compiler의 source selection 책임을 흡수할 수 있다.
- input manifest binding 추가가 current-route manifest ownership 이전으로 오해될 수 있다.
- test/toolchain 확대가 Round 3 current core allowlist 우회로 변할 수 있다.
- current-manifest denominator 재사용이 RTC의 numeric authority 발급으로 오해될 수 있다.
- absent source reference/finalized Registry-facing handoff를 plan text만으로 충족했다고 오해할 수 있다.
- current source reference set나 Phase 8 handoff만으로 non-current candidate가 RTC input eligibility를 얻었다고 오인할 수 있다.
- plan-invented transaction 또는 decision schema가 cited sealed principle과 같은 별도 authority를 가진다고 오해할 수 있다.
- arbitrary record union이 mechanically derived current source reference set로 오인될 수 있다.
- Codex role 이름만으로 independent-review credit을 주장하거나 owner seal이 review를 대체할 수 있다.
- exact G4/G5 artifact가 존재한다는 사실만으로 non-descendant execution을 current lineage로 오인할 수 있다.
- implementation이 pre-terminal default-consumer behavior를 자유값으로 받으면 fixed fail-closed constraint를 재개방할 수 있다.

대응:

- RTC는 exact current source reference set와 current-manifest denominator를 읽는 read-only consumer로 유지하고 absence/mismatch를 자체 보정하지 않는다.
- fixed cross-reference traversal만 set membership을 파생하고 composition-invalid와 required-field-missing을 분리한다.
- current source reference set를 먼저 검증하고, Publish policy closure 뒤 naturalization terminal finalize가 exact source/candidate/Publish result를 결속한 finalized Registry-facing rendered handoff packet을 만든 뒤 RTC reservation이 두 exact identities를 결속한다.
- independent-review source clauses, `procedural_session_independence` ceiling, fresh non-author result-review sessions and separate per-result owner authorization/seal을 직접 결속한다.
- reservation/transaction schema와 default-consumer guards가 `general_default_consumer_policy_before_terminal=fail_closed`를 direct constant로 강제하고 다른 값은 `blocked_preterminal_default_guard_mismatch`로 차단한다.
- historical/current required commit set을 finalized G4/G5 artifacts에서 완성하고 reservation/freeze/adoption-ready/adopted targets마다 Git ancestry를 다시 검사한다.
- decision table에서 each sealed principle의 governing source와 plan-invented implementation rows를 분리하고, mechanism adjustment는 principle preservation + explicit plan revision/toolchain freeze로 허용한다.
- prerequisite table과 `blocked_pending_finalized_registry_handoff`를 유지하고 Change 1 observation 외 실행을 금지한다.
- standalone subprocess와 existing tooling allowlist 경계를 유지한다.
- claim scanner와 top-doc review에서 axis vocabulary를 강제한다.

### Runtime Risk

- isolated writer가 live bridge/chunk path로 fallback할 수 있다.
- Lua merge order 또는 chunk ordering이 key overwrite를 숨길 수 있다.
- package probe가 live package output을 덮어쓸 수 있다.

대응:

- explicit contained output root, before/after protected hashes, no-fallback validation을 사용한다.
- actual Lua reconstruction과 cross-chunk duplicate 검사를 함께 실행한다.
- candidate package에서 ZIP을 금지하고 live package path를 hard-forbidden으로 둔다.

### Compatibility Risk

- roadmap hash와 checkout hash 불일치를 잘못 해석해 stale upstream에 successor를 봉인할 수 있다.
- `.gitattributes` drift를 semantic change로 오판하거나 반대로 숨길 수 있다.
- hardcoded `2105` 제거 뒤 manifest와 observed universe가 함께 이동하여 drift tripwire를 잃을 수 있다.
- 기존 collision disposition을 current member set 검증 없이 승계할 수 있다.
- PowerShell object materialization이 case-variant key를 병합할 수 있다.
- modified worktree toolchain과 pinned freeze commit이 달라질 수 있다.
- same-worktree repeat만으로 undeclared/local environment dependency를 놓칠 수 있다.
- ignored/generated rendered output이 clean checkout에 조용히 복사될 수 있다.
- DVF receipt가 complete input-manifest raw SHA 대신 constituent subset이나 자유형 derivation basis를 제시해 다른 generation의 rendered artifact가 통과할 수 있다.

대응:

- Registry reference resolution, checkout currency, derivation coherence, commit ancestry와 final source drift를 독립 gate로 사용한다.
- current-manifest declared/derived/observed denominator 3-way equality를 요구한다.
- lane-first minimum alignment 후 commit-bound freeze와 두 fresh checkout reproduction을 요구한다.
- finalized Registry-facing rendered handoff packet이 결속한 tracked candidate artifact만 declared rendered input으로 허용하고 planning workspace/generated fallback과 Phase 8-only handoff 대체를 차단한다.
- Registry/DVF complete input-manifest raw SHA-256의 단일 exact equality만 허용하고 alternate derivation-basis branch를 금지한다.
- collision member/payload binding을 current data에서 재생성한다.
- Windows Route C는 object property가 아닌 UTF-8 JSONL records를 사용한다.

### Regression Risk

- successor v2 schema 지원이 predecessor historical validation을 깨뜨릴 수 있다.
- stale fixture가 current positive path에 맞춰 약화될 수 있다.
- exporter/package default selection이 candidate/environment fallback을 허용할 수 있다.
- live manifest additive update 중 historical required rows가 삭제될 수 있다.
- pre-adoption review 전에 live default가 바뀌거나 terminal 뒤 결과가 claim evidence로 혼입될 수 있다.
- predecessor-era whole-manifest hash를 current CAS base로 오용해 legitimate additive rows를 막을 수 있다.
- adoption transaction crash 또는 executor receipt replay가 live selection을 orphan 상태로 남길 수 있다.
- unclassified concurrent writer가 reviewed-base CAS와 manifest-last ordering을 우회할 수 있다.
- Codex Reviewer attestation이나 프로젝트 소유자 decision이 다른 bundle/result에 대한 것인데 재사용될 수 있다.
- pre/post review가 같은 session/context를 재사용해 self-confirmation이 될 수 있다.
- G1이 실패·지연됐는데 candidate가 live selector로 채택되거나 terminal 전 일반 default consumer가 이를 사용할 수 있다.
- post-terminal regression 실패가 기계적으로 lifecycle state를 내리지 못해 invalid claim이 current로 남을 수 있다.
- scratch rehearsal manifest가 projected live manifest보다 작거나 validation fan-out이 달라 실제 adoption failure surface를 축소할 수 있다.
- discovery ID preimage에 ID/root/manifest/receipt-derived fields가 포함돼 circular 또는 implementation-dependent root가 생길 수 있다.

대응:

- v1 historical and v2 successor fixtures를 분리한다.
- positive/negative assertions를 동시에 요구한다.
- manifest diff validator로 removed/modified predecessor rows `0`을 요구한다.
- predecessor preservation set, current recensus, reviewed-base SHA와 immediate CAS를 분리한다.
- default route는 exact live selection만 허용하고 explicit candidate probe만 별도로 둔다.
- pre-adoption review/authorization, bounded machine adoption transaction, pre-terminal claim-bearing official result와 post-terminal non-claim regression을 분리한다.
- writer/concurrent-consumer inventory, default-present exposure와 every-identified-actor fail-closed guard coverage를 pre-adoption evidence로 요구한다.
- scratch manifest는 reviewed diff를 적용한 projected post-adoption live manifest와 byte-identical해야 하고 구조/denominator/fan-out 및 same-filesystem write path equality를 별도 receipt로 봉인한다.
- Codex Reviewer attestation과 프로젝트 소유자 exact adoption authorization을 acquire 전에 결속하고, 다른 bundle/result에 대한 record 재사용을 거부한다.
- pre/post review session/task ID와 context-isolation receipt를 분리하고 role reuse/session non-reuse/independence ceiling을 closeout에 공개한다.
- exact adoption-ready commit/projected manifest에 대한 G1 fresh A/B PASS를 acquire 전 필수로 두고, 미완료면 `blocked_pending_full_repository_reverification`과 live mutation `0`을 요구한다.
- terminal 전 일반 default consumers는 fail closed하고 transaction-scoped official validation만 exact selector를 소비한다.
- verified post-terminal contradiction이 `post_terminal_regression_failure` event를 append하고 current claim을 `invalidated/no-applicable-current`로 내리도록 lifecycle validator와 default consumers에 강제한다.
- `discovery_identity_core_v1` fixed allowlist에서 all ID/root/content-manifest/receipt-derived fields를 제외하고 full observation projection으로 preimage/ID를 재검증한다.

---

## 10. Rollback Plan

Pre-entry discovery 실패:

- attempt를 열지 않고 Registry-owned reference absence/ambiguity/incomplete reason, candidate hashes, missing fields와 owner routing을 attempt-independent discovery observation root에 commit한다. 완전한 관찰은 `observation_success=true`일 수 있지만 `entry_eligibility_status`는 exact absent/ambiguous/ineligible disposition을 유지한다.
- RTC가 planning hash, roadmap hash, staging 또는 predecessor를 substitute authority로 선택하지 않는다.
- 기존 current source authority chain의 gap audit가 PASS하고 Publish policy closure를 역인계 받은 finalized Registry-facing rendered handoff packet이 존재할 때까지 execution entry는 `blocked_pending_finalized_registry_handoff`다.
- set member required field가 없으면 `blocked_reference_set_required_field_missing`, mechanical cross-reference chain이 ambiguous/divergent이면 `blocked_reference_set_composition_invalid`로 기록한다.
- current source reference set와 finalized handoff packet이 불일치하면 `blocked_upstream_artifact_incoherent`로 중단한다. RTC가 source reference를 supersede하거나 packet을 rewrite하지 않는다.

Reservation 이후 durable Phase 0부터 candidate seal 이전 실패:

- protected source/rendered/runtime/package를 변경하지 않는다.
- failed attempt evidence를 durable하게 보존하고 blocked terminal event로 open reservation을 닫는다.
- `unknown`을 임의로 0 또는 PASS로 재분류하지 않는다.
- orphan reservation은 삭제하거나 nonce를 재사용하지 않고 authorized additive reconciliation 후 새 attempt로 진행한다.

Candidate 생성 후 live adoption 이전 실패:

- candidate는 attempt-local failed/superseded evidence로 보존한다.
- live required-validation manifest는 변경하지 않는다.
- 새 실행은 새 attempt ID, root와 nonce를 사용한다.
- G1이 failed/incomplete/not-run이면 `blocked_pending_full_repository_reverification`을 append하고 live required-validation/default selector mutation `0`을 확인한다.
- writer/concurrent-consumer inventory가 불완전하거나 atomicity/CAS/failure-injection/isolated Codex review/G1/project-owner authorization gate가 false/unknown이면 transaction을 시작하지 않고 pre-adoption attempt evidence에 blocked disposition을 append한다.

Adoption 중 또는 직후 실패:

- transaction 시작 후 machine success 전 failure/crash는 open record를 삭제하지 않는다. normal consumers는 fail closed하며 project-owner-authorized recovery executor가 fresh recovery authorization/nonce로 additive invalidation event를 append한다.
- machine transaction success 뒤 closeout terminal 전에도 general default consumers는 fail closed한다. Closeout review/owner seal/terminal이 실패하면 unsealed successor를 externally usable state로 유지하지 않고 additive invalidation으로 `no_applicable_current_rtc_selection`을 만든다.
- recovery는 unsealed successor selector를 제거해 no-applicable-current-selection으로 내리고 transaction/lifecycle failure evidence를 commit한다.
- D-06에 따라 live RTC selection을 `blocked/no-applicable-current-bundle`로 내린다.
- predecessor bundle을 current PASS authority로 다시 선택하지 않는다.
- adoption 또는 recovery nonce/receipt를 재사용하지 않는다.
- source/rendered/Lua/runtime/package payload rollback은 수행하지 않는다. 이 계획은 해당 payload를 변경하지 않기 때문이다.

Terminal 이후 결함:

- sealed successor bundle, terminal report와 predecessor evidence를 수정하지 않는다.
- lifecycle validator가 exact failure/terminal/bundle hashes와 재현 가능한 contradiction evidence를 검증한다.
- contradiction이 확인되면 `post_terminal_regression_failure` event를 append하고 `current_claim_state=invalidated`, `current_selection_state=no_applicable_current_rtc_selection`으로 즉시 내린다.
- false/unknown이면 current PASS를 유지한 채 결함을 숨기지 않고 별도 blocked investigation evidence를 남긴다.
- default exporter/package/current-route는 invalidated lifecycle에서 fail closed하고 predecessor를 선택하지 않는다.
- verifier-only metadata 결함만 D-07b의 bounded same-attempt additive correction을 사용할 수 있다.
- execution rerun, protected mutation, receipt/nonce replay 또는 claim-bearing rewrite가 필요하면 새 successor/correction round를 연다.

Invalid rollback:

- predecessor rename 또는 manifest rewrite
- failed attempt/evidence 삭제
- owner seal/review 복사
- stale marker만 제거
- live mutation 후 복구를 no-mutation으로 계산
- predecessor PASS를 current PASS로 확대 선언

Failure routing:

| Failure class | Routing scope | RTC disposition |
|---|---|---|
| reference-set required field missing | current source authority boundary | `blocked_reference_set_required_field_missing`; RTC does not synthesize the field |
| reference-set membership/path/cross-hash composition invalid | current source authority boundary | `blocked_reference_set_composition_invalid`; no ad hoc winner or union |
| authority reference, source currency, authority lifecycle, denominator mismatch | current source authority scope | `blocked_current_authority_reference`, `blocked_denominator_reseal_required` 또는 exact equivalent |
| finalized Registry-facing rendered handoff absence, metadata/compose derivation mismatch | Publish→naturalization terminal handoff boundary | `blocked_pending_finalized_registry_handoff` 또는 exact mismatch; RTC does not regenerate |
| current-source identity vs finalized-handoff-declared source identity mismatch | source/rendered handoff boundary | `blocked_upstream_artifact_incoherent`; RTC does not choose a winner or cross-rewrite artifacts |
| live payload mismatch 또는 payload mutation 필요 | applicable upstream payload/cutover scope | `blocked_payload_mutation_required` |
| collision member/disposition drift | collision policy scope | `blocked_policy_change_required` |
| exporter/package/default-route defect | RTC/package implementation scope | successor attempt blocked; no guard bypass |
| adoption transaction orphan/replay | RTC adoption/recovery implementation scope | additive invalidation, remove unsealed successor selector, no predecessor fallback |
| fresh-checkout infrastructure/prerequisite defect | repository validation authority | D-01 `failed`/`not_run`; no adoption/PASS |
| G1 pre-adoption full-repository failed/incomplete/not-run | repository validation authority | `blocked_pending_full_repository_reverification`; no transaction acquire/live repoint/default use |
| any required historical/current commit is not an ancestor of reservation/freeze/adoption-ready/adopted target | RTC current-lineage scope | `blocked_current_lineage_ancestry_failed` |
| reservation/transaction pre-terminal default guard missing, drifted or non-`fail_closed` | RTC implementation boundary | `blocked_preterminal_default_guard_mismatch`; no live mutation |
| toolchain dependency ambiguity/alignment defect | RTC implementation scope | retain unknown classification and open a corrected freeze attempt |
| actor inventory, atomicity, CAS, failure-injection or review/approval precondition failure | RTC adoption scope | no repoint; append blocked pre-adoption evidence |
| project-owner exact-result seal absent/mismatch | RTC closeout scope | specific mismatch; no closeout/terminal |
| verified post-terminal regression failure | lifecycle validator | `post_terminal_regression_failure`; invalidated/no-applicable-current; no predecessor fallback |

---

## 11. Governance Constraints

- `Philosophy.md` compliance
- Iris runtime 100% Lua / offline compiler-viewer boundary
- Hub & Spoke and SPI preservation
- Pulse must not depend on Iris or another spoke
- Registry Runtime Compatibility must not reopen Registry Authority canonical closure
- RTC must consume, never select or issue, the exact current source authority reference set
- source reference-set membership is derived only by `current_source_reference_set_composition_v1`; arbitrary union/newest-record selection is forbidden
- current source authority must precede Publish policy closure and naturalization terminal finalize; a Phase 8-only handoff cannot substitute for the finalized Registry-facing rendered packet
- only the RTC reservation binds the exact source reference-set digest and finalized Registry-facing handoff-packet SHA-256; Phase 0 validates mutual coherence
- current source and finalized-handoff complete input-manifest raw SHA-256 values use one exact equality; constituent or free-form derivation-basis alternatives are forbidden
- successor execution remains blocked until the current source gap audit passes and the exact finalized Registry-facing rendered handoff packet exists
- no fresh plan-review or separate governance owner-decision artifact is an execution-entry prerequisite
- `g1_pre_adoption` and `general_default_consumer_policy_before_terminal=fail_closed` are frozen direct implementation constraints, not owner-selectable inputs
- missing, drifted or alternate pre-terminal default-consumer behavior blocks live mutation with `blocked_preterminal_default_guard_mismatch`
- DVF System / DVF Body Compiler / Registry / Publish Boundary claim separation
- source/rendered/runtime/package authority ownership preservation
- exact decoded code-point identity preservation
- `ascii_lower_v1` comparison identity preservation
- no Unicode normalization or Unicode casefold
- no source key rename, merge, alias resolution or winner selection
- current-manifest declared / derived / observed denominator 3-way equality; predecessor numeric readpoints are historical only
- append-only attempt and lifecycle ledgers
- write-once claim-bearing evidence
- no failed-attempt deletion, nonce replay or receipt reuse
- predecessor bundle byte identity preservation
- candidate/staging/environment selection cannot be live default authority
- ignored workspace rendered output cannot be copied into fresh-checkout authority inputs
- package guard remains unconditional
- `-RegistryCompatibilityProbe` remains an existing no-ZIP validation surface, is not executor authentication and does not weaken the package guard
- independent review and owner authorization/seal are separate axes; owner approval, owner seal and self-generated PASS cannot replace independent review
- Codex review credit is limited to fresh non-author isolated-session `procedural_session_independence`; pre/post session/task/context reuse is forbidden and role reuse/limitations are disclosed
- pre-adoption review, exact adoption-ready G1 fresh A/B successor and project-owner authorization all precede live repoint
- reservation, implementation freeze, adoption-ready and adopted commits descend from the same dynamically finalized historical/current `required_lineage_commit_set_v1`
- adoption transaction is machine-executed, bounded, append-only and recoverable only through a new exact project-owner authorization
- concurrency exposure is treated as present until a project-owner-approved exclusive-writer decision proves otherwise
- claim-bearing official current-route result precedes review/seal/closeout terminal
- general default exporter/package consumers remain fail closed until success terminal; transaction-scoped official validation is the only pre-terminal live consumer
- closeout packet commit precedes success terminal event
- project-owner exact-result seal must bind the adopted successor, manifest, adoption diff, official result and Codex Reviewer closeout attestation; absent or mismatched coverage forbids terminal completion
- verified post-terminal contradiction is non-claim evidence that mechanically appends `post_terminal_regression_failure` and blocks current applicability
- DECISIONS append / ARCHITECTURE current replacement plus predecessor trace / ROADMAP current summary plus historical provenance
- canonical top-document paths are the four verified tracked files under `docs/`; competing copies are forbidden
- `docs/EXECUTION_CONTRACT.md` claim/ceiling/non-claim discipline and `AGENTS.md` required validation discipline
- minimal diff and no unrelated refactor
- tracked status is not authority status; ignored status is not deletable status
- current-route manifest remains the `legacy_combined_governance_route` container and does not become DVF Body Compiler PASS authority
- `discovery_identity_core_v1` is a fixed observation/provenance allowlist and excludes every identity/root/manifest/receipt-derived field before hashing
- only cited top-document principles are `sealed_constraint`; transaction, correction and decision schemas remain implementation/project-policy mechanisms

---

## 12. Expected Closeout State

Target RTC lifecycle state: `registry_runtime_compatibility_canonical_complete`.

Synchronized entry state is `frozen_plan / blocked_pending_finalized_registry_handoff`; the target below is unreachable until Publish policy closure and naturalization terminal finalize produce the exact Registry-facing rendered handoff packet, Change 1 confirms no unresolved source-reference gap and a fresh eligible discovery observation exists.

이 axis-qualified state는 다음이 모두 충족될 때만 허용한다.

- current source authority reference set gap audit가 PASS하고 Publish policy closure를 역인계 받은 finalized Registry-facing rendered handoff packet이 존재함
- `current_source_reference_set_composition_v1` traversal이 exactly one closed chain을 만들고 composition/required-field blocker가 없음
- reservation/transaction contract가 frozen plan identity, `g1_pre_adoption`과 `general_default_consumer_policy_before_terminal=fail_closed`를 직접 결속하고 actual guard behavior가 일치함
- latest durable discovery observation이 `observation_success=true`, `entry_eligibility_status=eligible`이고 reservation이 its content-manifest SHA-256을 소비함
- `discovery_identity_core_v1`이 derived ID/root/content-manifest/receipt fields 없이 재구성되고 full observation/root의 recomputed ID와 일치함
- RTC reservation이 `rtc_reservation_current_source_and_finalized_rendered_handoff_binding_v2`로 exact source reference-set digest와 finalized Registry-facing handoff-packet SHA-256을 결속함
- Phase 0에서 current-source/finalized-handoff facts raw SHA-256와 complete input-manifest raw SHA-256가 각각 단일 exact equality를 만족하고 immutable candidate artifact identity가 packet과 일치함
- current source authority reference set의 exact identity/lifecycle/receipt chain이 resolved됨
- `execution_checkout_matches_current_authority=true`
- `derivation_chain_coherent=true`
- reservation, execution freeze, adoption-ready와 adopted commits가 historical roots, synchronized integration, current source adoption과 dynamically extracted G4/G5 terminals로 구성된 same `required_lineage_commit_set_v1` 전체의 descendant임
- roadmap/planning/checkout mismatch가 RTC의 자체 source 선택 없이 exact Registry reference로 해소됨
- D-01 fresh-checkout hard gate가 exact same finalized handoff packet과 packet-bound candidate를 소비해 PASS이고 `failed`/`not_run`이 아님
- current-manifest declared/derived/observed denominator가 3-way equality를 만족함
- selected lane의 최소 alignment가 freeze commit/tree에 포함되고 repository-file toolchain manifest, canonical environment identity와 per-run receipts가 분리됨
- planning observations가 실행 entry에서도 유지되므로 `lane_c_current_toolchain_contract_revalidation`이 선택되고, 달라졌다면 lane_a/lane_b를 허용한 exact census falsification evidence가 review됨
- exhaustive classified toolchain identity가 primary/reproduction fresh checkouts에서 일치하고 drift가 없음
- exact source/rendered/bridge/runtime/package key set과 per-key payload가 일치함
- unauthorized collision, duplicate, merge, loss가 `0`
- actual Lua reconstruction, isolated package, Windows Route A/C가 PASS
- positive current RTC validation과 stale negative guard가 각각 PASS
- deterministic successor bundle identity가 same-checkout 및 independent fresh-checkout에서 일치함
- candidate seal 직전과 live repoint 직전 source/input/rendered/runtime drift가 `0`
- predecessor RTC rows가 보존되고 current manifest recensus, reviewed-base SHA와 pre-write CAS가 일치함
- isolated Codex Reviewer pre-adoption attestation, G1 handoff/successor와 프로젝트 소유자 repoint authorization이 exact adoption-ready commit, candidate/projected manifest/adoption diff/transaction을 hash-bind함
- writer/concurrent-consumer inventory와 projected-live/scratch equivalence, atomicity/CAS/rollback/failure-injection PASS가 transaction 시작 전에 hash-bind됨
- exact successor가 transaction-scoped live required-validation/official exporter/package route에서 소비되고 terminal 전 general default consumers는 fail closed함
- predecessor fallback과 unexpected protected mutation이 `0`
- adoption transaction이 authorized machine success event로 닫히고 open/expired transaction이 없음
- pre-terminal claim-bearing official current-route result가 exact successor를 실제 소비함
- exact adoption-ready commit/tree와 projected live manifest에 대한 pre-adoption fresh full-repository clean-checkout Run A/B 및 새 append-only G1 successor가 transaction acquire 전에 PASS함
- exact adopted successor에 대한 distinct isolated Codex Reviewer closeout attestation, project-owner exact-result seal, durable closeout와 terminal ordering이 PASS
- top-document update mode와 post-terminal non-claim regression 결과가 additive trace로 보존됨

최대 허용 claim:

```text
Registry Runtime Compatibility PASS

applies to:
- exact execution facts SHA-256
- exact execution input manifest SHA-256
- exact current source authority reference-set digest
- exact finalized Registry-facing rendered handoff-packet SHA-256
- exact RTC reservation SHA-256 that binds the source reference set and finalized rendered handoff
- exact pinned repository commit/tree
- exact sealed successor repository-file toolchain manifest
- exact recorded canonical execution environment identity, with per-run receipts and without cross-environment authority claim
- exact immutable successor bundle
- exact pre-adoption full-repository clean-checkout G1 gate successor
- exact required-lineage commit-set and adopted-target ancestry report
- exact project-owner result seal and Codex Reviewer attestations
- validated bridge/runtime/package/Windows routes
```

이 claim은 Registry Authority PASS, DVF Body Compiler PASS, Publish Boundary PASS, package publication, release/Workshop/B42 readiness, deployment, manual QA, semantic facts correctness 또는 public text acceptance를 의미하지 않는다.

If unbound or skipped intermediate source generations exist, this `Registry Runtime Compatibility PASS` makes no claim about those intermediate generations.

Publish policy closure, finalized Registry-facing rendered handoff packet, source-reference composition/gap audit, cycle-free durable discovery identity, exact source/rendered input-manifest coherence, dynamic current-lineage ancestry, denominator equality, toolchain freeze, D-01 fresh-checkout gate, final source drift, manifest CAS, pre-adoption G1 full-repository gate, fixed pre-terminal default guard, atomic transaction, isolated Codex Reviewer attestations, project-owner exact-result seal 또는 adoption 중 하나라도 닫히지 않으면 execution closeout은 `blocked` 또는 `partial`이며 `Registry Runtime Compatibility PASS`와 `registry_runtime_compatibility_canonical_complete`를 출력하지 않는다.
