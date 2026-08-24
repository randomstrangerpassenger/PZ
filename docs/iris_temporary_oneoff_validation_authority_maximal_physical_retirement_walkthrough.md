# Iris Temporary/One-Off Validation Authority Maximal Physical Retirement Walkthrough

> Session dates: 2026-08-23–2026-08-24 KST
> Current status: survivor correction terminal validation and S0→S1 full-range P8 review PASS; P10 withheld by dirty-main evidence-locator blocker
> S0 commit: `fd0504817af8c1031ac794391cf67d129c8db54c`
> S0 tree: `395ec36de921987299fa9a9d9bb46118b74160a5`
> Terminal S1 commit: `99585ff2a4738055d12aa2f7b42cf74d06f13860`
> Terminal S1 tree: `944f7e66692ab30453f3ddf39ce71f2461f2e43d`
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

### Exact closeout-carrier commit review result

- Command subject: exact commit `b0fe69b1406d4f8353a2278cff6cc9b71738f0b8`
- Command exit: `0`
- Actionable findings: `0`
- Critical/important/minor findings: `0/0/0`
- Final verdict: no actionable regression introduced by the reviewed commit

Reviewer는 S1이 추가·수정한 pending retirement closeout 문서와 evidence record가 syntactically valid하고, repository에서 직접 재확인할 수 있는 count/hash가 surrounding artifact와 일치한다고 판정했다.

이 PASS는 `b0fe69b1`이 부모 destructive commit에 추가한 closeout-carrier diff 검토 결과다. `4e527b84`의 destructive diff를 포함한 P8 final physical-retirement change-set PASS가 아니며, Product runtime, in-game QA, release, Workshop, Publish/RTC, B42 readiness, performance 또는 public-text quality에 대한 review PASS도 아니다.

## 8. Quantified Lightweighting

### Execution and taxonomy surface

| Metric | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Exact gate execution units | 437 | 225 | 212 (`48.513%`) |
| Pytest identity in exact gate | 433 | 221 | 212 (`48.961%`) |
| Standalone validation | 4 | 4 | 0 |
| Round 3 current taxonomy identity | 228 | 110 | 118 (`51.754%`) |

The exact gate comparison uses predecessor pytest `433` + standalone `4` and terminal pytest `221` + standalone `4`. Configured collection `231` and current runner `110` have different semantics and are not substituted for the comparator's required execution unit denominator.

### Repository surface

| Metric | S0 | S1 | Net change |
| --- | ---: | ---: | ---: |
| Tracked blob bytes | 801,868,754 | 793,650,844 | -8,217,910 (`-1.025%`) |
| Test/tooling LOC | 259,483 | 233,510 | -25,973 (`-10.010%`) |

Tracked byte 감소량은 약 `7.84 MiB`다. 새 retirement summary와 evidence가 repository에 포함된 뒤의 net result이므로 projection이나 deleted-source gross bytes가 아니다.

### Performance claim ceiling

Comparable S0/S1 wall-time, CPU와 memory benchmark는 수행되지 않았다. 따라서 gate unit이나 taxonomy가 약 절반으로 줄었다는 사실을 실제 실행시간이 같은 비율로 개선됐다는 주장으로 바꾸지 않는다.

## 9. Token-Efficiency Interpretation

이번 계획과 terminal closeout은 S0/S1의 prompt tokens, cached-input tokens, output tokens, tool-output tokens, cache hit 또는 context-compaction count를 수집하지 않았다. 실제 GPT/Codex token 개선률은 미측정이다.

다음 값은 workload별 static proxy로만 사용할 수 있다.

- Full-repository byte surface: `1.025%` 감소
- Test/tooling LOC surface: `10.010%` 감소
- Exact gate identity-heavy surface: `48.513%` 감소
- Current taxonomy identity-heavy surface: `51.754%` 감소

이 proxy는 동일 token budget에서 실제 처리량이 같은 비율로 증가했다는 증거가 아니다. Narrow product-code 작업은 제거된 테스트를 읽지 않으므로 token 변화가 거의 없을 수 있고, taxonomy/inventory/gate result를 모두 읽는 작업은 반복 identity text 감소의 영향을 더 크게 받을 수 있다. 반대로 retirement overlay를 통째로 읽는 authority-review workload는 compact product-code 작업보다 많은 context를 계속 요구한다.

정확한 token 효율을 주장하려면 같은 model, prompt, tool policy와 cache condition에서 S0/S1 input/cached-input/output/tool token을 별도로 측정해야 한다. 이번 세션은 그러한 benchmark를 실행하거나 새 token-validation authority를 만들지 않았다.

## 10. Top-Document Synchronization

Exact carrier-commit review 결과와 정량 해석을 반영하기 위해 다음 top-level 문서를 수정했다. 이후 survivor correction에서 이 표현을 full-range P8 pending으로 교정했고, correction terminal validation과 exact S0→S1 review PASS 뒤 최종 상태로 다시 동기화했다.

- `docs/DECISIONS.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`

세 문서는 다음 공통 상태를 기록한다.

- Physical implementation: PASS
- Exact-subject terminal validation: PASS
- Exact S0→S1 Codex Reviewer: PASS, exit `0`, actionable finding `0`; prior Medium finding `2`건 해소 확인
- Exact S1/tree: `99585ff2a4738055d12aa2f7b42cf74d06f13860` / `944f7e66692ab30453f3ddf39ce71f2461f2e43d`
- Structural efficiency metrics: recorded with separate denominators
- Runtime and GPT/Codex token efficiency: unmeasured
- Canonical post-validation carrier synchronization: complete; P10 token은 dirty-main evidence-locator blocker로 withheld

Architecture 문서는 predecessor `433 + 4` criterion과 successor adjudication 후 terminal `221 + 4` gate를 분리했다. 이는 과거 PASS를 rewrite하는 것이 아니라 registration membership을 survival authority로 삼지 않는 successor decision을 설명한다.

## 11. Current Repository State

Post-validation carrier update는 exact S1 이후의 product code, validator 또는 test를 수정하지 않았다. 변경 범위는 기존 closeout/summary JSON, 세 top-level 문서와 이 Walkthrough이며 exact S1을 재정의하지 않는다.

`Iris/_docs/round3/temporary_validation_physical_retirement/closeout.json`은 survivor correction terminal validation과 S0→S1 full-range review PASS를 기록한다. P10 token은 발행하지 않으며, dirty-main archive/restore locator 부재를 유일한 잔여 blocker로 유지한다.

사용자 지시에 따라 top-document 및 Walkthrough 작성 과정에서는 테스트를 실행하지 않았다. 별도 seal, receipt, manifest, census, proof artifact 또는 validation-of-validation도 만들지 않았다.

## 12. Final Claim Boundary

이번 작업으로 증명된 범위는 다음과 같다.

- Adjudicated temporary/one-off validation executable physical retirement
- Current product/validation-system survivor preservation
- Exact S1 terminal validation PASS
- Exact S0→S1 full-range Codex Reviewer PASS, actionable finding `0`
- Tracked repository bytes와 test/tooling LOC의 net 감소
- Gate/taxonomy execution surface의 구조적 감소

다음은 증명하거나 승인하지 않았다.

- Comparable wall-time, CPU 또는 memory improvement percentage
- Actual GPT/Codex token improvement percentage
- Iris product runtime correctness or performance
- Historical replay PASS after repository-local route retirement
- In-game QA, RTC, Publish, release, Workshop, deployment or B42 readiness
- Public-text quality acceptance

이 Walkthrough의 완료는 narrative 기록 완료만 뜻한다. Correction terminal validation과 full-range P8 review는 PASS했지만, canonical P10 token은 dirty-main evidence binding까지 충족된 뒤에만 발행할 수 있다.

## 13. Survivor Correction Addendum

외부 지적을 반영해 predecessor keep `328` identity / `71` family를 다시 열었다. 실제 source의 import, subprocess target, repository path literal과 lifecycle label을 확인했으며, 단순히 `staging`, `historical`, `legacy` 문자열이 있다는 이유로 현재 negative-boundary test를 제거하지 않았다.

추가 퇴역은 다음 `13` identity다.

- Predecessor regular survivor에서 full-source `6`: Layer 4 admission-round `4`, description phase acceptance `1`, RTC orchestration-context literal `1`.
- Predecessor regular survivor에서 mixed callable `6`: Browser phase acceptance, Detail phase acceptance, Legacy phase acceptance, IAR policy-closure projection, legacy-active/silent round producer, freshness-reseal cleanup helper 각각 `1`.
- Predecessor inventory 밖이지만 current required manifest의 historical-optional row로 남았던 IAR preserved-candidate replay callable `1`.

물리 변경은 test source `3`, 해당 Layer 4 round의 exclusive executable generator `1`, mixed source 내부 callable `7` 제거다. Non-executable historical round artifacts는 Git history/provenance carrier로 남기고 generator를 regular validator로 유지하지 않는다. Regular disposition은 product `224`, validation-system `92`, remove `283`, survivor 합계 `316`으로 교정했다. Outside-predecessor callable `1`은 이 599 regular denominator에 소급 산입하지 않고 별도 inventory correction으로 기록했다.

기존 dirty-main inventory 밖 validator-like ignored source는 더 넓은 파일명 기준으로 `32`개가 확인됐다. 이들은 taxonomy, required validation manifest, full-gate selection과 두 predecessor overlay 어디에도 없으므로 `not_regular_not_registered`로 분류했다. 기존 archive/restore hash 두 개의 discoverable locator가 없기 때문에 이 correction에서는 해당 local source를 삭제하지 않았고, 기존 `163`-path 안전 archive/restore claim도 independently reverified로 승격하지 않았다.

Correction의 one-off JSON mutation script는 실행 직후 삭제했다. 이 스크립트는 canonical validator, 정규 검사기 또는 새 validation authority가 아니다. Correction 과정에서는 중간 test/gate를 실행하지 않았다. 계획에 명시된 terminal validation은 correction implementation commit을 만든 뒤 마지막에 한 번만 실행한다.

## 14. Correction Terminal Validation and Review

최종 correction subject는 commit `99585ff2a4738055d12aa2f7b42cf74d06f13860`, tree `944f7e66692ab30453f3ddf39ce71f2461f2e43d`다. 이 subject에서 계획의 종단 배치를 실행한 결과는 다음과 같다.

- 수정 후 생존한 Python executable `12`개 `py_compile`: exit `0`
- Clean-checkout focused tests: `33 passed`
- Round 3 current contract runner: `110 tests`, exit `0`
- Configured current collection/denominator: `231 collected`, exit `0`
- Fresh clean-checkout Run A/B: 각각 exit `0`, source/external execution mutation `0`
- Deterministic comparator: exit `0`; pytest identity `221` + standalone `4` = required execution unit `225`
- A/B canonical result SHA-256: `a1ce7cd24073f1b2383e0cdd3b12c18871ebb9ed436c9b19486e6b88d5a72f66`
- Comparator receipt SHA-256: `9f89724e99df92d24c222f373323dffd96c4368be27ea909a4109d1c17c4cc8f`

첫 full-range Codex review는 active closure와 clean-checkout source-disposition contract에 남은 retired-source reference `2`건을 Medium finding으로 보고했다. Commit `99585ff2`에서 Layer 4 retired source의 current closure/seed reference와 RTC retired test의 dedicated-route/assertion reference를 제거했다. 수정 후 exact range `fd0504817af8c1031ac794391cf67d129c8db54c..99585ff2a4738055d12aa2f7b42cf74d06f13860`을 재검토한 Codex Reviewer의 최종 판정은 exit `0`, actionable finding `0`, PASS다.

Exact gate는 S0의 `437` unit에서 `225` unit으로 `212` (`48.513%`) 감소했고 current taxonomy는 `228`에서 `110`으로 `118` (`51.754%`) 감소했다. Tracked executable identity removal은 합계 `460`, full source/exclusive support deletion은 `96`이다. Exact S1 tracked blob은 S0 대비 `8,217,910` bytes (`1.025%`), test/tooling LOC는 `25,973` (`10.010%`) 감소했다. 이 값은 구조적 workload proxy이며 실제 token, wall-time, CPU 또는 memory 개선률이 아니다.

Post-validation 문서/JSON carrier는 위 S1을 재정의하지 않는다. P8은 충족됐지만 dirty-main archive manifest와 fresh-root restore receipt의 discoverable locator가 없으므로 해당 safety claim과 P10 completion token은 계속 blocked/withheld다.

## 15. Six-Family Canonical-Presence Successor Correction

마지막 correction은 이전 closeout의 “6 family/13 identity를 dirty-main local survivor로 보존”한 상태를 canonical tracked presence로 바꿨다. Exact implementation subject는 `052ef0e5c90282ef9afac830bb4491b36d4e92fc`, tree는 `9a952fab3442bea45cada05a4b660245f978a27e`다. Browser use-case, line-count CLI, object-access compatibility, session-cache, tag-precision, view-model contract source를 exact bytes로 추적하고, 각 source에 대한 exact `.gitignore` allow rule과 current taxonomy/required/full-gate binding만 추가했다. Product/runtime code는 변경하지 않았다.

Terminal batch 결과는 다음과 같다.

- promoted Python source `6`개 `py_compile`: exit `0`
- Clean-checkout focused tests: `47 passed`
- Round 3 current runner: `123 tests OK`
- Configured collection: `244 collected`
- Clean-checkout Run A/B: 각각 exit `0`, source/external mutation `0`
- Comparator: pytest identity `234` + standalone `4` = `238` unit, exit `0`
- A/B canonical result SHA-256: `2c364aeb7ee9b322060ba6080f780b85a0f7fc38e2f506cf047064b888687d61`
- Comparator receipt SHA-256: `a534f5da785864e2b40783a5ae0035f2d0121a6319535ee9f9d967ddf92e9d1e`
- Missing-source negative probe: expected tracked source `49`, observed `48`, exit `3` (의도한 fail-closed)
- 합성 retired target `262`에 대한 tracked clean/dirty-main residue: 각각 `0`

첫 successor full-range Reviewer는 implementation이 아니라 closeout/summary가 predecessor terminal `99585ff2`, taxonomy `110`, gate `225`를 계속 terminal 값으로 표시한 점을 Medium finding `1`건으로 지적했다. 이 section과 closeout carrier는 해당 stale reference를 S1의 `123/238` 수치와 정확한 canonical-presence 상태로 교정한다. Initial raw review는 보존하며, correction carrier를 exact endpoint로 다시 read-only review한다.

Canonical correction과 dirty-main safety completion은 별개다. Archive/restore hash의 discoverable locator가 없어 163-file binding은 검증되지 않았고, 두 hash는 `historical_unresolved_hash_reference`로만 남는다. 따라서 P10 completion token은 `null`이며, bounded search·negative probe·임시 스크립트는 canonical validator로 승격하지 않는다.
