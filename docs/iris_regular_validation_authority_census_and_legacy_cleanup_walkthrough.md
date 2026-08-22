# Iris Regular Validation Authority Census and Legacy Cleanup Walkthrough

> Session dates: 2026-08-22–2026-08-23 KST  
> Current status: authority census and validation baseline recovery complete; physical temporary/legacy cleanup pending  
> Baseline subject: `a570f34065fa96a459f946171330f080a8f1c8d1`  
> Validated subject: `18d0c2ff9de97a71ddf7aa6b03fb059ffbb35089`  
> Validated tree: `56250ea400511eaf84ff84ee19ee8550f89b8492`  
> PASS carrier: `6a4cf63c001ec708929e57da64347e3e7a040d91`  
> Documentation readpoint: `c798313f3740437d24a32532ce5db3a3c9465236`

## 1. Outcome

이번 세션은 Iris validation surface를 executable identity 단위로 조사하고 current regular authority, historical reproduction, diagnostic/evidence와 제거 후보를 분리했다. 동시에 required full gate를 막던 기존 DVF validation-system defect를 수정해 exact subject의 current pytest `433`, standalone validation `4`, Run A/B와 deterministic comparator를 PASS로 복구했다.

그러나 이 결과는 temporary·legacy executable source의 물리적 정리를 완료한 것이 아니다. 실제 삭제는 current contract가 없던 TC8 한 건뿐이고, regular contract가 없는 live source `37`개와 executable identity `216`개가 남아 있다. 따라서 기존 closeout의 `complete`는 채택된 authority-reconfirmation 계획 범위에만 유효하며, temporary-test cleanup Problem 1 전체 상태는 계속 진행 중이다.

이번 세션의 정확한 성과는 다음과 같다.

- 전체 validation authority census 완료
- Current/non-current role 분리 완료
- Current validation baseline 복구 및 exact-subject PASS 완료
- Temporary·legacy physical cleanup 입력 집합 확정
- Physical source cleanup과 repository lightweighting은 미완료

## 2. Adopted Plan and Scope Contraction

채택된 계획은 `docs/iris_regular_validation_authority_contract_reconfirmation_and_temporary_legacy_cleanup_plan.md`다.

계획의 1차 objective는 executable validation unit을 실제 observable contract 기준으로 조사하고 정규 validation authority를 재확정하는 것이었다. 이름이나 작성 시기만으로 legacy test를 삭제하지 않고 current contract, validation-system contract, historical reproduction과 evidence 역할을 먼저 분리하도록 했다.

이 접근은 안전한 census를 만들었지만 물리적 경량화 목표를 축소했다.

- Test count/LOC 감소는 명시적 목표에서 제외됐다.
- `reproduction_only`는 historical route에 보존할 수 있었다.
- `evidence_only`도 `physical_preservation=executable_source`로 남길 수 있었다.
- Current contract가 없다는 사실과 executable source를 계속 보존해야 한다는 판단을 별도 증명하지 않았다.

따라서 계획의 PASS는 authority mapping 완료를 뜻할 수 있었지만, 원래 문제의 핵심인 non-current executable source 제거를 보장하지 않았다.

## 3. Baseline and Census

Owner-selected tracked baseline은 commit `a570f34065fa96a459f946171330f080a8f1c8d1`, tree `2e2b4fa729b74c74d2ac1e64131d487074f81ac1`이다. Planning worktree를 암묵적 baseline으로 사용하지 않고 taxonomy, source classification, required manifest, clean-checkout runner와 owner-written authority identity를 exact baseline에 결속했다.

Executable identity `1,167`개를 inventory, contract와 disposition ledger의 같은 denominator로 기록했다.

| Disposition | Identity count |
| --- | ---: |
| `regular_product_contract` | 445 |
| `regular_validation_system_contract` | 154 |
| `reproduction_only` | 434 |
| `evidence_only` | 133 |
| `expired_or_duplicate_remove` | 1 |
| `migrate_then_remove` | 0 |
| `needs_decision` | 0 |
| Total | 1,167 |

Final authority composition은 다음과 같다.

- Tracked test source: `151`
- Required source: `66`
- Historical optional source: `62`
- Evidence-only executable source: `3`
- Current pytest identity: `433`
- Standalone validation: `4`
- Required execution unit: `437`
- Unclassified/conflicting source: `0/0`
- Missing manifest target: `0`

Inventory는 후속 physical cleanup의 입력으로 재사용한다. 같은 denominator를 다시 추출하거나 더 큰 validation-of-validation ledger를 만드는 것은 후속 범위가 아니다.

## 4. Implemented Census-Scope Changes

### Source-role reconciliation

다음 세 source를 기존 ambiguous obsolete/misrouted 표현에서 `evidence_only`로 재분류했다.

- `Iris/build/tests/test_description_generator.py`
- `Iris/build/tests/test_layer3_pipeline.py`
- `Iris/build/tests/test_wearable_6f.py`

세 source는 합계 `28` identity를 가진다. 이 변경은 regular membership 제거가 아니라 이미 non-regular였던 source의 역할을 명시한 것이다. Source bytes는 그대로 보존됐으므로 실행량이나 repository bytes 감소로 계산하지 않는다.

Full-repository source policy는 `evidence_only_sources`를 fail-closed 분류 대상으로 인식하고 executable-source preservation 형식을 확인하도록 정렬했다. Required-validation adoption binding도 변경된 full-gate contract blob에 맞췄다.

### Expired TC8 removal

`Iris/test/test_rightclick_pipeline.py::test_tc8_full_pipeline_snapshot`을 제거했다.

- Disposition: `expired_or_duplicate_remove`
- Current contract: absent
- Removed support: none
- Source file: retained because other current tests remain
- Source byte change: `11,452 -> 10,650` bytes
- Source line change: `321 -> 300`

이는 이번 세션에서 유일하게 물리 삭제된 executable identity다. 전체 inventory 기준 약 `0.086%`이며 current regular denominator에는 포함되지 않았으므로 current pytest 수는 줄지 않았다.

### Authority and runner alignment

Clean-checkout full gate와 관련 meta-validation이 evidence-only source classification, exact source disposition과 adoption blob identity를 같은 final composition으로 읽도록 정렬했다. Owner-written baseline-admission authority 두 파일은 수정하지 않았고 Iris runtime Lua, current generation, public text와 package payload 변경도 없었다.

## 5. Initial Blocked Closeout

Cleanup implementation subject의 required current gate는 다음 test에서 실패했다.

`Iris/build/description/v2/tests/test_dvf_3_3_closeout_reentry_guard_seal.py::DvfCloseoutReentryGuardSealTest::test_validator_requires_full_current_route_result_for_complete_contract`

관측 결과는 pytest `432 passed, 1 failed`, standalone `4/4 PASS`였다. 같은 failure가 baseline에서도 재현돼 cleanup-attributable regression은 아니었지만, required final full gate가 PASS하지 않았으므로 계획의 fail-closed 규칙에 따라 Run B와 comparator를 실행하지 않고 closeout을 `blocked`로 기록했다.

초기 disposition ledger는 이후 다음과 같이 보강됐다.

- `baseline_result=failing`
- `failure_attribution=validation_defect`
- `blocking=true`
- exact failing identity와 defect surface 기록

이 단계의 carrier commit은 `27e9638e7d7320318cfbd1e6e4264ad967e6ceab`이다. 당시 blocked 판정은 올바른 중간 판정이며 후속 PASS로 소급 삭제하지 않는다.

## 6. DVF Validation-System Blocker Resolution

### Root cause

DVF closeout/reentry guard는 `docs/ROADMAP.md`의 다음 형태를 current completion overclaim으로 오인했다.

`release/Workshop/deployment readiness는 별도 successor 범위다`

이 문장은 현재 범위의 완료를 release/deployment 완료로 확대하는 것이 아니라 반대로 별도 successor 범위를 명시한다. Product defect나 route fixture 결함이 아니라 top-document boundary classifier의 validation defect였다.

### Narrow fix

`is_top_doc_boundary_routing_definition()`에 다음 조건을 모두 만족하는 ROADMAP 문장만 boundary definition으로 인정하도록 했다.

- `별도 successor 범위`를 명시한다.
- `release`, `workshop` 또는 `deployment readiness`를 포함한다.
- Positive completion marker를 포함하지 않는다.

첫 review에서는 allowlist가 mixed assertion까지 허용할 수 있다는 P2 finding이 있었다. 예를 들어 같은 문장에 readiness 완료와 successor 범위가 함께 있으면 fail-closed해야 한다. Validated subject는 positive-completion-marker guard를 추가해 이 finding을 해소한 뒤 다시 review됐다.

Final fix commit은 `18d0c2ff9de97a71ddf7aa6b03fb059ffbb35089`이며 변경 surface는 `Iris/build/description/v2/tools/build/dvf_3_3_closeout_reentry_guard_seal_common.py` 한 파일, 17개 추가 line이다.

## 7. Validation Walkthrough

계획에서 요구한 검증은 final subject를 고정한 뒤 집중 실행했다. 이 과정의 임시 진단과 중간 candidate는 canonical validator 또는 새 validation authority로 채택하지 않았다.

### Focused validation

- Changed Python source compile/import: exit `0`
- Exact failing pytest identity: `1 passed`
- Codex Reviewer가 실행한 focused DVF test family: `9 tests`, `OK`

### Clean-Checkout Run A

- Root: `C:/Users/MW/ivrc/p8a`
- Claim ID: `iris-validation-contract-reconfirmation-successor-final`
- Subject: `18d0c2ff9de97a71ddf7aa6b03fb059ffbb35089`
- Tree: `56250ea400511eaf84ff84ee19ee8550f89b8492`
- Current pytest: `433 passed, 0 failed`
- Standalone: `4/4 PASS`
- Required execution unit: `437`
- Canonical result: `PASS`
- Source checkout mutation: `0`
- External cleanup: `PASS`
- Canonical result SHA-256: `ad98bbb6e1943a2ec2096b06f81ab445daabed30810077e968c6e3b9023cb74c`

### Clean-Checkout Run B

- Root: `C:/Users/MW/ivrc/p8b`
- Same claim ID, subject and tree as Run A
- Current pytest: `433 passed, 0 failed`
- Standalone: `4/4 PASS`
- Required execution unit: `437`
- Canonical result: `PASS`
- Source checkout mutation: `0`
- External cleanup: `PASS`
- Canonical result SHA-256: `ad98bbb6e1943a2ec2096b06f81ab445daabed30810077e968c6e3b9023cb74c`

### Deterministic comparison

- Root: `C:/Users/MW/ivrc/p8cmp`
- Comparator native exit code: `0`
- Run A/B canonical raw bytes equal: true
- Required execution unit count: `437`
- Test identity count: `433`
- Comparator receipt SHA-256: `3707d0ec20e10cc2d95b979e38c33585871a4f12948d98dcc82a73f9b0ce4336`

### Independent review

Codex Reviewer는 exact validated subject를 최종 재검토했다.

- P0: `0`
- P1: `0`
- P2: `0`
- P3: `0`
- Exit code: `0`
- Verdict: no actionable regression

Run A/B와 comparator의 large result는 repository 밖 durable root에 남기고 in-repository carrier에는 path와 SHA-256만 기록했다. 이전 p6/p7 intermediate runs는 identity/claim correction과 reviewer finding 이전 결과이므로 final evidence pointer에서 제외했다.

## 8. PASS Carrier and Ledger Reconciliation

Post-validation carrier commit `6a4cf63c001ec708929e57da64347e3e7a040d91`은 validated subject를 재정의하지 않고 다음만 기록했다.

- Baseline failure와 final PASS의 route attribution
- `validation_defect_resolved`, `blocking=false`
- Run A/B와 comparator의 external path/SHA-256
- Codex Reviewer의 final zero-finding result
- Top-level readpoint non-supersession disclosure
- Scoped closeout `state=complete`

Resolved disposition row는 baseline의 failing result를 보존하면서 final result를 `passing`으로 기록한다. Failure는 product defect가 아니라 명시적 successor-boundary 문장을 잘못 차단한 validation defect로 귀속된다.

Carrier의 `state=complete`는 다음 범위에만 유효하다.

- Regular validation authority-to-contract mapping
- Temporary/legacy role census
- Current gate baseline recovery
- Exact-subject deterministic PASS와 independent review

이는 temporary·legacy executable source의 물리 제거, repository byte/LOC lightweighting 또는 suite 성능 개선을 뜻하지 않는다.

## 9. Physical Cleanup Reassessment

PASS closeout 뒤 실제 source surface와 disposition ledger를 다시 대조한 결과, 원래 의도한 physical cleanup이 대부분 남아 있음을 확인했다.

### Pure non-current live source

| Role | Files | Identities | Raw bytes |
| --- | ---: | ---: | ---: |
| `reproduction_only` | 24 | 153 | 268,519 |
| `evidence_only` | 13 | 63 | 60,825 |
| Total | 37 | 216 | 329,344 |

이 37개 source는 현재 worktree에 실제로 존재하고 regular product/validation-system contract를 하나도 갖지 않는다.

### Mixed source

Ledger상 regular disposition과 non-current/expired disposition이 함께 있는 source는 3개다.

- `test_compose_entrypoint_guard_hardening.py`: live regular `6`, live non-current `1`
- `test_package_layer3_chunks_only_contract.py`: live regular `15`, live non-current `1`
- `test_rightclick_pipeline.py`: current tests는 유지되지만 non-current TC8은 이미 제거됨

따라서 후속 split 대상으로 실제 live non-current callable이 남은 mixed source는 2개다.

### Efficiency and repository size

- Current execution unit: `437 -> 437`, reduction `0%`
- Current pytest identity: `433 -> 433`
- Observed blocker result: `432 passed / 1 failed -> 433 passed / 0 failed`
- Comparable wall-time/CPU/memory benchmark: 없음
- Baseline에서 PASS carrier까지 tracked blob bytes: `+6,444,671` bytes, 약 `+6.15 MiB`
- Tracked files: `+19`
- Net text lines: `+5,372`

즉 correctness와 authority clarity는 개선됐지만 execution-count, storage와 LOC 경량화는 달성되지 않았다.

## 10. Corrected Completion Boundary

2026-08-23 top-level documents는 다음 상태로 정렬됐다.

- `DECISIONS.md`: census/baseline recovery와 physical cleanup을 별도 lifecycle로 판정
- `ARCHITECTURE.md`: authority role, execution registration과 physical durability를 서로 다른 축으로 정의
- `ROADMAP.md`: physical cleanup을 진행 중으로 두고 37 source/216 identity를 remaining scope로 기록

Documentation readpoint는 `c798313f3740437d24a32532ce5db3a3c9465236`이다.

Problem 1은 다음 조건 전에는 완료로 닫지 않는다.

- 37개 pure non-current source의 explicit retention obligation 재심사
- `evidence_only`의 compact sealed/external evidence 전환
- `reproduction_only`의 current-valid reproduction obligation 확인
- 두 live mixed source의 current/non-current contract 분리
- Actual removed files, identities와 bytes가 모두 양수
- Repository-wide tracked bytes와 test/tooling LOC 순감소
- Current pytest `433` + standalone `4` 보존
- Final exact-subject Run A/B와 comparator exit `0`

Historical taxonomy를 다시 인용하는 것만으로 executable source 보존을 정당화하지 않는다. 보존에는 현재도 유효한 explicit reproduction obligation, consumer, input과 failure meaning이 필요하다.

## 11. Commit Map

| Commit | Role |
| --- | --- |
| `a570f340` | Owner-selected tracked baseline |
| `2351de37` | 1,167-unit census, contract/disposition, source-role reconciliation와 TC8 cleanup |
| `4b808751` | Full-gate adoption binding reconciliation |
| `27e9638e` | Baseline-reproducible DVF validation defect를 기록한 blocked closeout carrier |
| `18d0c2ff` | DVF successor-boundary false-positive fix와 final validated subject |
| `6a4cf63c` | Run A/B, comparator와 reviewer에 결속된 scoped PASS carrier |
| `c798313f` | DECISIONS/ARCHITECTURE/ROADMAP의 corrected physical-cleanup boundary |

현재 작업 branch는 `codex/iris-validation-authority-successor`다. Remote push나 main merge는 이 walkthrough의 claim이 아니다.

## 12. Evidence Map

### In-repository

- Adopted plan: `docs/iris_regular_validation_authority_contract_reconfirmation_and_temporary_legacy_cleanup_plan.md`
- Census and ledgers: `Iris/_docs/round3/validation_contract_reconfirmation/`
- Final composition: `Iris/_docs/round3/validation_contract_reconfirmation/final_composition.json`
- Route attribution: `Iris/_docs/round3/validation_contract_reconfirmation/route_failure_attribution.json`
- Independent review: `Iris/_docs/round3/validation_contract_reconfirmation/independent_review.json`
- Scoped closeout: `Iris/_docs/round3/validation_contract_reconfirmation/closeout.json`

### Repository-external durable validation evidence

- Run A: `C:/Users/MW/ivrc/p8a`
- Run B: `C:/Users/MW/ivrc/p8b`
- Comparator: `C:/Users/MW/ivrc/p8cmp`
- Environment receipt: `C:/Users/MW/iccv/receipts/env-v1/environment_receipt.json`

The external roots are evidence for this exact validated subject only. They are not canonical validators, product authority or proof that the pending physical cleanup has completed.

## 13. Explicit Non-Claims

이번 세션은 다음을 완료하거나 증명하지 않는다.

- Temporary·legacy executable source physical cleanup completion
- Repository byte/LOC lightweighting
- Suite wall-time, CPU 또는 memory improvement
- Current test contract 축소
- All historical reproduction PASS
- Iris runtime Lua 또는 public behavior 변경
- PZ in-game QA
- RTC, Publish, release, Workshop, package 또는 deployment readiness
- External evidence나 ad hoc inspection의 새 validation authority 채택

따라서 이 walkthrough의 최종 상태 문구는 다음과 같다.

> Iris regular validation authority census and validation baseline recovery are complete. Temporary/legacy executable source cleanup and repository lightweighting remain pending successor work.
