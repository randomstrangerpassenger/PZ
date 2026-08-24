# Iris Temporary/One-Off Validation Authority Maximal Physical Retirement Walkthrough

> Session dates: 2026-08-23–2026-08-24 KST  
> Current status: physical implementation, exact-subject terminal validation and P8 Codex Reviewer PASS; canonical P10 closeout carrier synchronization pending  
> S0 commit: `fd0504817af8c1031ac794391cf67d129c8db54c`  
> S0 tree: `395ec36de921987299fa9a9d9bb46118b74160a5`  
> Terminal S1 commit: `b0fe69b1406d4f8353a2278cff6cc9b71738f0b8`  
> Terminal S1 tree: `2e7f2c8e1693586284d5aedb3f8cc05cce29f12e`  
> Existing post-validation carrier: `8b9f779970c44d87914a9082a0c2da9a8efbd86e`

## 1. Document Role

이 문서는 selected repository root의 owner-supplied input `docs/iris_temporary_oneoff_validation_authority_maximal_physical_retirement_plan.md`에 따라 수행된 physical-retirement 작업과 2026-08-24 세션의 independent review, 정량 해석 및 top-document synchronization을 설명하는 narrative walkthrough다. Adopted plan 원본은 이 clean successor worktree의 tracked file이 아니며, 이 문서는 그 원본을 복제하거나 대체하지 않는다.

이 Walkthrough는 다음 역할을 갖지 않는다.

- Canonical validator 또는 새 validation authority가 아니다.
- S0, S1, predecessor ledger, terminal receipt 또는 `closeout.json`을 대체하지 않는다.
- 현재 세션의 ad hoc 조회나 계산을 새로운 gate로 승격하지 않는다.
- P10 completion token을 발행하지 않는다.
- Runtime, release, Workshop, Publish/RTC, B42 또는 public-text quality를 승인하지 않는다.

## 2. Starting Point

Predecessor authority-reconfirmation 세션은 executable validation identity `1,167`개를 분류하고 current exact gate pytest `433` + standalone `4` = `437` unit을 복구했다. 그러나 그 closeout은 authority census와 baseline recovery의 완료였으며 temporary·legacy executable source의 실제 물리 제거를 완료하지 않았다.

이번 작업의 S0는 commit `fd0504817af8c1031ac794391cf67d129c8db54c`, tree `395ec36de921987299fa9a9d9bb46118b74160a5`다. S0의 regular membership이나 historical/diagnostic registration은 그 자체로 영구 보존 권한이 아니며, 각 identity가 현재 product contract 또는 validation-system contract를 독립적으로 갖는지 다시 심사해야 했다.

작업은 다음 boundary를 유지했다.

- Product runtime Lua, product data, public text와 package payload는 변경하지 않는다.
- Current contract가 있는 validation source를 temporary naming이나 age만으로 삭제하지 않는다.
- Historical denominator, sealed predecessor receipt와 Git history를 소급 rewrite하지 않는다.
- Tracked repository, dirty-main ignored/untracked files와 external archive를 서로 다른 metric domain으로 유지한다.
- Temporary helper와 ad hoc 검사 결과를 canonical validation authority로 승격하지 않는다.

## 3. Authority and Commit Ordering

Destructive work보다 authority가 먼저 존재하도록 commit ordering을 고정했다.

| Role | Commit | Meaning |
| --- | --- | --- |
| S0 | `fd0504817af8c1031ac794391cf67d129c8db54c` | Measurement and authority-census baseline |
| Corrective survival authority | `9739b389f0076903a3494f3d78edc3193fded458` | Registration-only survival을 부정하고 independent obligation을 요구 |
| Survival adjudication | `462806ca` | Regular/non-current identity disposition 반영 |
| Physical-domain authority | `145b1dd2e21afa957be3ffe87ab8ea3bde069ce0` | Tracked, dirty-main과 archive domain 및 destructive boundary 고정 |
| First destructive commit | `4e527b845d2cb6e05a6694e425e607fc95b42ead` | Adjudicated executable source와 exclusive support 제거 |
| Terminal S1 | `b0fe69b1406d4f8353a2278cff6cc9b71738f0b8` | Retirement summary와 implemented-only closeout을 처음 포함한 exact subject |
| Existing carrier | `8b9f779970c44d87914a9082a0c2da9a8efbd86e` | S1 terminal validation PASS와 당시 Reviewer platform block 기록 |

Authority-only readpoint `145b1dd2...`는 first destructive commit `4e527b84...`보다 앞선다. Post-validation carrier와 현재 문서 수정은 exact S1을 재정의하지 않는다.

## 4. Survival Adjudication

### Regular universe

S0 regular identity `599`개를 registration 밖의 independent contract basis로 심사했다.

| Disposition | Identity count |
| --- | ---: |
| `keep_regular_product_contract` | 234 |
| `keep_regular_validation_system_contract` | 94 |
| `remove_regularized_temporary` | 271 |
| `migrate_then_remove` | 0 |
| `blocked_needs_owner_authority` | 0 |
| `registration_only_survivor` | 0 |
| Total | 599 |

보존된 regular identity는 `328`, 퇴역 판정된 lifecycle-bound identity는 `271`이다.

### Non-current universe

Non-current identity `568`개도 repository-local historical/diagnostic registration을 보존 근거로 사용하지 않고 current consumer 여부를 확인했다.

| Disposition | Identity count |
| --- | ---: |
| Promoted current product contract | 39 |
| Remove regularized temporary | 529 |
| Unresolved | 0 |
| Total | 568 |

Full-gate conflict identity `56`개는 current `39` 보존, non-current `17` 퇴역으로 닫혔다.

Authority universe에서 퇴역 판정된 `271 + 529 = 800` identity는 physical file/callable count와 같은 분모가 아니다. Authority disposition, tracked executable identity와 dirty-main identity는 아래처럼 분리해서 읽는다.

## 5. Physical Retirement

### Tracked transaction

Tracked tree에서는 다음 실행 자산을 제거했다.

- Regularized-temporary source family: `48`
- Regularized-temporary identity: `268`
- Pure non-current source: `34`
- Pure non-current identity: `177`
- Surviving mixed source에서 제거한 callable: `2`
- Full source 및 exclusive support deletion: `92 files`
- Tracked executable identity removed: `268 + 177 + 2 = 447`
- Active target residue: `0`
- Unfinished migration: `0`

`4e527b84...`의 실제 file status는 deletion `92`, modification `12`, addition `3`이다. `round3_run_contract_tests.py`는 살아남았고 `current` selector, current build closure, required-validation projection과 fail-closed 결과 attribution을 유지했다. Repository-local `historical`, `diagnostic`, `all` selector와 historical corpus materialization path는 종료했다.

### Dirty-main ignored/untracked transaction

Dirty-main 영역은 tracked transaction과 합산하지 않았다. Exact archive verify와 fresh-root restore 뒤 다음 범위만 제거했다.

- Removed files: `163`
- Removed identities: `335`
- Removed raw bytes: `901,270`
- Already absent files, not counted: `14`
- Already absent identities, not counted: `17`
- Preserved current product source families: `6`
- Preserved current product identities: `13`
- Survivor hash mismatch: `0`
- Active target residue: `0`

Tracked `92/447`과 dirty-main `163/335`는 서로 다른 physical domain이므로 하나의 canonical 총계로 합산하지 않는다. External archive bytes도 tracked repository 감소량에 포함하지 않는다.

## 6. Exact S1 and Terminal Validation

Terminal subject는 retirement summary와 initial closeout을 처음 함께 포함한 commit `b0fe69b1406d4f8353a2278cff6cc9b71738f0b8`, tree `2e7f2c8e1693586284d5aedb3f8cc05cce29f12e`다.

Existing post-validation carrier가 기록한 exact-subject 결과는 다음과 같다.

- Python syntax: exit `0`
- Focused clean-checkout tests: `33 passed`
- Current runner: `118 tests`, `OK`, exit `0`
- Configured collection: `243 collected`, exit `0`
- Clean-Checkout Run A: PASS, native exit `0`
- Clean-Checkout Run B: PASS, native exit `0`
- Deterministic comparator: PASS, exit `0`
- Terminal pytest identity: `230`
- Standalone validation: `4`
- Required execution unit: `234`
- Canonical result SHA-256: `1baca45cd773df9ddeca0bc8c125c766a97eb462751e4246ff6ba6ef4cc07964`
- Guard negative probe: expected non-zero exit observed
- Mixed-contract negative probes: PASS
- Tracked/dirty target residue: `0/0`
- Source checkout mutation: `0`
- External execution mutation: `0`

Run A/B와 comparator 결과는 S1에 결속된다. Post-validation documentation이나 carrier update는 이 subject를 새 subject로 바꾸지 않는다.

## 7. Codex Reviewer Walkthrough

### Earlier carrier state

Existing carrier `8b9f7799...`를 작성할 당시 P8 Codex Reviewer는 platform usage limit으로 최종 결과 회수가 불가능했다. 따라서 terminal validation은 PASS였지만 independent review는 `BLOCKED_EXTERNAL_PLATFORM_USAGE_LIMIT`, completion token은 withheld 상태로 기록됐다.

### 2026-08-24 review attempts

이번 세션은 exact S1만 대상으로 `codex review --commit b0fe69b1406d4f8353a2278cff6cc9b71738f0b8`을 실행했다.

첫 실행은 CLI model-cache compatibility warning이 대량 출력되어 최종 Reviewer 메시지가 output limit에서 잘렸다. 같은 exact subject를 경고 억제 상태로 다시 실행했고 Reviewer는 Philosophy, S1 diff, predecessor destructive commit, JSON, metric 및 selector 상태를 조사했다.

Reviewer가 current runner를 실행하던 중 사용자가 일시 중단을 요청했다. 중단 신호가 도착하기 직전에 runner는 `118 tests`, `OK`, `54.371s`로 끝났지만 Reviewer final verdict는 생성되지 않았다. 이 실행은 기존 current runner 결과와 일치하는 incidental observation일 뿐 새 canonical validator, receipt 또는 benchmark로 채택하지 않는다.

중단된 Reviewer session은 rollout을 보존하지 않아 resume할 수 없었다. 따라서 같은 exact S1에 새 Reviewer를 시작했다. 두 번째 완료 run에서는 테스트를 추가 실행하지 않았고 repository-local diff, JSON syntax, count/hash와 authority consistency만 확인했다.

### Final independent-review result

- Command subject: exact commit `b0fe69b1406d4f8353a2278cff6cc9b71738f0b8`
- Command exit: `0`
- Actionable findings: `0`
- Critical/important/minor findings: `0/0/0`
- Final verdict: no actionable regression introduced by the reviewed commit

Reviewer는 S1이 추가·수정한 pending retirement closeout 문서와 evidence record가 syntactically valid하고, repository에서 직접 재확인할 수 있는 count/hash가 surrounding artifact와 일치한다고 판정했다.

이 PASS는 exact S1 검토 결과다. Product runtime, in-game QA, release, Workshop, Publish/RTC, B42 readiness, performance 또는 public-text quality에 대한 review PASS가 아니다.

## 8. Quantified Lightweighting

### Execution and taxonomy surface

| Metric | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Exact gate execution units | 437 | 234 | 203 (`46.453%`) |
| Pytest identity in exact gate | 433 | 230 | 203 (`46.882%`) |
| Standalone validation | 4 | 4 | 0 |
| Round 3 current taxonomy identity | 228 | 118 | 110 (`48.246%`) |

The exact gate comparison uses predecessor pytest `433` + standalone `4` and terminal pytest `230` + standalone `4`. Configured collection `243` and current runner `118` have different semantics and are not substituted for the comparator's required execution unit denominator.

### Repository surface

| Metric | S0 | S1 | Net change |
| --- | ---: | ---: | ---: |
| Tracked blob bytes | 801,868,754 | 793,640,069 | -8,228,685 (`-1.026%`) |
| Test/tooling LOC | 259,483 | 235,409 | -24,074 (`-9.278%`) |

Tracked byte 감소량은 약 `7.85 MiB`다. 새 retirement summary와 evidence가 repository에 포함된 뒤의 net result이므로 projection이나 deleted-source gross bytes가 아니다.

### Performance claim ceiling

Comparable S0/S1 wall-time, CPU와 memory benchmark는 수행되지 않았다. 따라서 gate unit이나 taxonomy가 약 절반으로 줄었다는 사실을 실제 실행시간이 같은 비율로 개선됐다는 주장으로 바꾸지 않는다.

## 9. Token-Efficiency Interpretation

이번 계획과 terminal closeout은 S0/S1의 prompt tokens, cached-input tokens, output tokens, tool-output tokens, cache hit 또는 context-compaction count를 수집하지 않았다. 실제 GPT/Codex token 개선률은 미측정이다.

다음 값은 workload별 static proxy로만 사용할 수 있다.

- Full-repository byte surface: `1.026%` 감소
- Test/tooling LOC surface: `9.278%` 감소
- Exact gate identity-heavy surface: `46.453%` 감소
- Current taxonomy identity-heavy surface: `48.246%` 감소

이 proxy는 동일 token budget에서 실제 처리량이 같은 비율로 증가했다는 증거가 아니다. Narrow product-code 작업은 제거된 테스트를 읽지 않으므로 token 변화가 거의 없을 수 있고, taxonomy/inventory/gate result를 모두 읽는 작업은 반복 identity text 감소의 영향을 더 크게 받을 수 있다. 반대로 retirement overlay를 통째로 읽는 authority-review workload는 compact product-code 작업보다 많은 context를 계속 요구한다.

정확한 token 효율을 주장하려면 같은 model, prompt, tool policy와 cache condition에서 S0/S1 input/cached-input/output/tool token을 별도로 측정해야 한다. 이번 세션은 그러한 benchmark를 실행하거나 새 token-validation authority를 만들지 않았다.

## 10. Top-Document Synchronization

Reviewer PASS와 정량 해석을 반영하기 위해 다음 top-level 문서를 수정했다.

- `docs/DECISIONS.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`

세 문서는 다음 공통 상태를 기록한다.

- Physical implementation: PASS
- Exact-subject terminal validation: PASS
- P8 Codex Reviewer: PASS, exit `0`, actionable finding `0`
- Exact S1/tree: unchanged
- Structural efficiency metrics: recorded with separate denominators
- Runtime and GPT/Codex token efficiency: unmeasured
- Canonical P10 closeout carrier synchronization: pending

Architecture 문서는 predecessor `433 + 4` criterion과 successor adjudication 후 terminal `230 + 4` gate를 분리했다. 이는 과거 PASS를 rewrite하는 것이 아니라 registration membership을 survival authority로 삼지 않는 successor decision을 설명한다.

## 11. Current Repository State

이번 documentation update는 product code, validator, test, JSON closeout carrier를 수정하지 않았다. 현재 작업으로 변경된 파일은 세 top-level 문서와 이 Walkthrough다.

`Iris/_docs/round3/temporary_validation_physical_retirement/closeout.json`은 아직 earlier Reviewer platform-blocked state를 기록한다. 따라서 이 Walkthrough와 top-document update는 P10 token이 이미 발행됐다고 주장하지 않는다. 남은 canonical record step은 existing closeout carrier가 Reviewer PASS를 반영하도록 동기화하는 것이다.

사용자 지시에 따라 top-document 및 Walkthrough 작성 과정에서는 테스트를 실행하지 않았다. 별도 seal, receipt, manifest, census, proof artifact 또는 validation-of-validation도 만들지 않았다.

## 12. Final Claim Boundary

이번 작업으로 증명된 범위는 다음과 같다.

- Adjudicated temporary/one-off validation executable physical retirement
- Current product/validation-system survivor preservation
- Exact S1 terminal validation PASS
- Codex Reviewer zero-finding PASS
- Tracked repository bytes와 test/tooling LOC의 net 감소
- Gate/taxonomy execution surface의 구조적 감소

다음은 증명하거나 승인하지 않았다.

- Comparable wall-time, CPU 또는 memory improvement percentage
- Actual GPT/Codex token improvement percentage
- Iris product runtime correctness or performance
- Historical replay PASS after repository-local route retirement
- In-game QA, RTC, Publish, release, Workshop, deployment or B42 readiness
- Public-text quality acceptance

이 Walkthrough의 완료는 narrative 기록 완료만 뜻한다. Canonical completion state와 P10 token은 existing closeout authority가 Reviewer PASS를 반영한 뒤에만 변경할 수 있다.
