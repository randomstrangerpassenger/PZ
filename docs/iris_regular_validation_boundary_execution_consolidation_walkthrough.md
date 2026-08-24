# Iris Regular Validation Boundary Execution Consolidation Walkthrough

> Session dates: 2026-08-24–2026-08-25 KST  
> Current status: **complete**  
> Adopted plan: `docs/iris_regular_validation_boundary_execution_consolidation_plan.md`  
> S0: `64754c38147233c4f5e04a7469b45163c2c55ebe` / tree `92810ce35f021bd3dfa65ceafb782a32c2b86258`  
> S_terminal: `4f80540f13f64b36929fece13e2ca46978df101f` / tree `266eb7fdee96d4749fa816346abd862d648d3423`  
> S_carrier: `3a6564e3af87f834ad7f9de224b25fd5fed9280b` / tree `92332ec4c9206e7717b97aba3eaa52e5424451df`  
> Post-closeout top-document readpoint: `0d1ee465b1c7b8cca40f4196b50b32664bd9b1ac`

## 1. Document Role

이 문서는 regular validation boundary의 execution consolidation을 실제로 구현한 과정, second exhaustive sweep, exact-subject validation, independent review와 closeout을 설명하는 narrative walkthrough다.

이 Walkthrough는 다음 역할을 갖지 않는다.

- Canonical validator, test runner 또는 새 validation authority가 아니다.
- S0/S_terminal canonical result, deterministic comparator receipt, item-level closure 또는 compact implementation map을 대체하지 않는다.
- 세션에서 사용한 ad hoc 조회·계산 command를 후속 검사기로 승격하지 않는다.
- Machine PASS를 carrier나 이 문서에 상속시키지 않는다. PASS는 exact `S_terminal`에만 귀속한다.
- Wall-clock 속도, 실제 tokenizer/Codex token 사용량, PZ in-game behavior, RTC/Publish 또는 deployment를 승인하지 않는다.

## 2. Starting Point and Correction

선행 physical-retirement closeout이 확정한 current boundary는 pytest identity `234`, standalone validation `4`, 전체 execution unit `238`, taxonomy `123`, required manifest `70`이었다. 이들은 서로 다른 universe이며 하나의 count로 합치거나 대체하지 않았다.

초기 implementation wave는 public-text, particle adjustment, Round 3 applicability, Layer 4 synthetic family를 consolidation했다. 다만 owner review가 두 가지 한계를 지적했다.

1. Round 3는 pytest identity `5 -> 1`이 아니라 identity `5 -> 5`, runner import `5 -> 1`이었다.
2. 네 family의 유효성만으로는 maximal consolidation을 주장할 수 없었다. Same-input, named-check absorption, table-driven, pipeline, shared-core, duplicate authority, wrapper, traversal/assertion/comparison, parse/load/materialization, registration, pytest/standalone 중복 전체를 다시 봐야 했다.

이 지적을 closeout 문구만 바꾸는 대신 second exhaustive sweep와 추가 구현으로 해소했다.

## 3. Exact Baseline and Commit Ordering

계획은 commit `48cb970e`에 채택했다. Full-gate의 이미 retired된 docs path 참조를 별도 correction commit `64754c38`에서 제거한 뒤, 해당 exact clean subject를 S0로 선택했다.

S0 canonical full gate는 PASS했고 다음을 고정했다.

| Universe | S0 count |
| --- | ---: |
| Pytest identity | 234 |
| Standalone execution | 4 |
| Total regular execution unit | 238 |
| Taxonomy entry | 123 |
| Required-manifest obligation | 70 |
| Tracked validation source | 72 |
| Required validation source | 38 |

S0 canonical result는 `C:\Users\MW\iccv\rr1\canonical_full_result.json`, SHA-256 `f7ff1095d21d3942e2377441b059b371cbf3d95493c1089c2035b6a902634bd7`에 결속했다.

## 4. Implemented Consolidation

최종 구현은 check을 삭제하는 방식이 아니라, 중복 preparation/producer/materialization을 공유하고 predecessor contract를 named check로 이관하는 방식을 사용했다.

| Family | Identity/result disposition | Shared operation |
| --- | --- | --- |
| Particle adjustment | 11 predecessor test -> 1 table-driven test | Case table and named subtests |
| Public-text review negatives | 6 -> 1 | Strict JSON fixture/result load |
| Public-text protected snapshot | 2 -> 1 | Shared snapshot preparation |
| Layer 4 synthetic surface | 4 -> 1 | One table-driven identity, case-local trees |
| Current-authority source path | 2 -> 1 | Named invalid-input cases |
| Package forbidden surface | 2 -> 1 | Package script read `2 -> 1` |
| DVF runtime compatibility | 2 -> 1 | Generation/runtime report `2 -> 1` |
| DVF complete-generation success | 2 -> 1 | Input copy and initial generation `2 -> 1` |
| DVF complete-generation failure | Identity 1 -> 1 | Immutable failure seed `6 -> 1` |
| Legacy current-surface guard | Two pairs `2 -> 1` each | Per-case writable workspace |
| DVF generation install | Identity `3 -> 3` | Class-owned immutable seed `7 -> 1` |
| Round 3 applicability | Identity `5 -> 5` | Runner import `5 -> 1` |

Public-text strict JSON load의 actual execution-semantic count는 `26 -> 2`로 감소했다. Identity를 유지한 Round 3와 install lifecycle은 계약 단위를 합치지 않고 expensive preparation만 공유한 family다.

## 5. Failure Localization and Isolation

Shared producer를 도입하면 후속 assertion이 연쇄 실패하거나 mutable state가 sibling에 누출될 수 있다. 이를 막기 위해 다음 규칙을 적용했다.

- Shared preparation/producer 실패는 독립 named check로 FAIL한다.
- Producer result가 없으면 dependent check는 가짜 assertion failure 대신 `blocked_by:<producer>` skip을 보고한다.
- Complete-generation negative case는 하나의 immutable repository/generation seed를 만든 뒤 case별 writable clone을 사용한다.
- Generation-install family도 class-level immutable repository/candidate seed를 사용하지만 각 positive/negative/guard case는 별도 short-root clone을 받는다.
- Layer 4와 legacy synthetic guard는 case별 workspace를 초기화해 mutation residue를 공유하지 않는다.
- Round 3 check가 변경하는 `runner.REPO`는 항상 복원하며 reverse order와 same-process repetition으로 확인했다.

Merged predecessor-detectable failure population `35/35`를 replay해 constituent detection과 localization을 `100%` 유지했다.

## 6. Second Exhaustive Sweep and Closure

Second sweep는 shared producer만 재검토하지 않고 계획이 요구한 모든 consolidation axis를 대상으로 했다.

- `same_input_merge`
- `absorb_as_named_check`
- `table_driven_conversion`
- `pipeline_merge`
- `shared_core_replacement`
- `duplicate_authority_removal`
- One-use wrapper
- Repeated traversal/assertion/comparison
- Repeated parse/load/materialization
- Duplicate registration/authority
- Pytest/standalone duplicate execution path

External item-level closure는 predecessor execution `238`, taxonomy `123`, manifest `70` row 전체에 explicit successor와 disposition을 부여한다. Terminal canonical set과 비교한 결과는 다음과 같다.

| Set | S0 | S_terminal | Bidirectional delta |
| --- | ---: | ---: | ---: |
| Execution | 238 | 213 | 0 |
| Taxonomy | 123 | 115 | 0 |
| Required manifest | 70 | 67 | 0 |

Unmapped row, unsupported keep, 미구현 non-keep disposition과 remaining eligible consolidation candidate는 모두 `0`이다.

## 7. Terminal Validation

테스트는 구조 변경이 끝난 exact `S_terminal`에 몰아서 실행했다. Carrier와 후속 narrative docs에는 terminal machine PASS를 재귀속시키지 않았고 추가 test를 실행하지 않았다.

| Validation | Result |
| --- | --- |
| Focused family selection | `67 passed`, `58 subtests passed` |
| Round 3 reverse order | `5 passed` |
| Round 3 same-process repeat | `10 passed` |
| Clean-checkout Run A | PASS, pytest `209` + standalone `4` |
| Clean-checkout Run B | PASS, pytest `209` + standalone `4` |
| Deterministic comparator | `succeeded`, exit `0` |
| Exact execution/taxonomy/manifest closure | All bidirectional deltas `0` |

Run A/B canonical result SHA-256은 모두 `0d5b5ab8dd60862d8df15bd831a33e0066dc44a88884d9ad82365a27dfb73bf1`이다. Comparator receipt SHA-256은 `f226ba0b20eb9d28cb11e7022949a280618a4ff4f3dab389232da8e31649af6e`이다.

Runner, common gate logic, full-gate definition, result/comparator schema와 denominator enforcement blob은 S0 대비 변경되지 않았다. 따라서 계획의 missing-source, denominator-mismatch, comparator-tamper negative probe는 `gate machinery unchanged` 조건에 따라 면제했다.

## 8. Independent Review

Codex Reviewer는 exact S0→S_terminal delta와 item-level closure를 read-only로 검토했다. 모든 keep disposition, failure localization, writable-clone isolation, Round 3 state restoration, taxonomy/manifest mapping과 residual repeated-operation group을 전수 검토한 결과는 다음과 같다.

- P0/P1/P2/P3: `0/0/0/0`
- Actionable finding: `0`
- Remaining eligible candidate: `0`

이후 exact `S_terminal`을 sole parent로 갖는 documentation/evidence-only `S_carrier`를 만들었다. Carrier reviewer도 parent count `1`, forbidden implementation/gate delta `0`, evidence locator/hash와 exact-subject language를 확인했고 actionable finding `0`으로 승인했다.

## 9. Quantified Efficiency

### Execution structure

- Pytest identity: `234 -> 209`, `-25` (`-10.7%`)
- Total execution unit: `238 -> 213`, `-25` (`-10.5%`)
- Taxonomy: `123 -> 115`, `-8` (`-6.5%`)
- Required manifest: `70 -> 67`, `-3` (`-4.3%`)

Identity 감소는 assertion 제거와 같지 않다. Named constituent check는 계속 실행되므로 wall-clock 시간이 같은 비율로 감소했다고 해석하지 않는다.

### Static operation surface

| Axis | Before | After |
| --- | ---: | ---: |
| Setup | 8/5 | 11/8 |
| Repository scan | 27/22 | 22/17 |
| Manifest parse | 82/79 | 82/79 |
| Source load | 152/149 | 151/148 |
| Artifact generation | 128/124 | 125/121 |
| Producer invocation | 65/58 | 62/55 |
| Subprocess | 50/49 | 50/49 |
| Workspace/materialization | 117/113 | 121/117 |

Setup과 workspace/materialization 증가는 negative/lifecycle case의 writable isolation을 유지하기 위한 safety cost다. 이 증가를 숨기거나 다른 감소 축으로 대체하지 않았다.

### Physical and context proxy

| Universe | S0 | S_terminal | Delta |
| --- | ---: | ---: | ---: |
| Tracked source LOC | 15,289 | 15,254 | -35 |
| Tracked source bytes | 597,477 | 599,090 | +1,613 |
| Required source LOC | 10,124 | 10,089 | -35 |
| Required source bytes | 390,694 | 392,307 | +1,613 |
| Validation/tooling closure bytes | 1,921,053 | 1,917,107 | -3,946 |

Exact `S_carrier 3a6564e3` completion measurement에서 added analysis/documentation은 `3,574` bytes이며 context-budget proxy는 `3,574 - 3,946 = -372` bytes다. 이는 repository-side physical proxy일 뿐 실제 token 절감량이 아니다. 통제된 before/after wall-clock과 tokenizer/Codex token 계측은 수행하지 않았다.

## 10. Commit Walkthrough

| Commit | Role |
| --- | --- |
| `48cb970e` | Consolidation plan adoption |
| `64754c38` | Pre-existing full-gate path correction and exact S0 |
| `b7cf3a0f` | Initial regular validation consolidation wave |
| `27d06949` | Boundary consolidation and authority reconciliation |
| `6893a9cc` | Residual lifecycle consolidation from second sweep |
| `fb813c0f` | Immutable negative-seed sharing |
| `beeb21ce` | Short isolated install clone paths |
| `4f80540f` | Final install lifecycle seed sharing; exact S_terminal |
| `3a6564e3` | Documentation/evidence-only closeout carrier |
| `0d1ee465` | DECISIONS/ARCHITECTURE/ROADMAP narrative synchronization |

Implementation commit들은 local `main`의 직계 이력에 있다. 별도 merge commit은 필요하지 않았으며 remote push는 이 작업 범위에서 수행하지 않았다.

## 11. Evidence Map

### In repository

- Plan: `docs/iris_regular_validation_boundary_execution_consolidation_plan.md`
- Compact closeout map: `Iris/_docs/refactor/regular_validation_boundary_consolidation/implementation_map.json`
- Taxonomy: `Iris/_docs/round3/round3_test_taxonomy.json`
- Required manifest: `Iris/_docs/round3/current_route_required_validations.json`
- Top-level readpoints: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`

### Repository-external plan-required evidence

- Item-level closure: `C:\Users\MW\iccv\regular-consolidation-terminal\item-level-closure-v4.json`
  - SHA-256: `7a843c5ff96c0456b3f5bd2781812ae4fafc9bedf6b1195110cad850bfaaa25d`
- Terminal Run A result: `C:\Users\MW\iccv\rrt6a\canonical_full_result.json`
  - SHA-256: `0d5b5ab8dd60862d8df15bd831a33e0066dc44a88884d9ad82365a27dfb73bf1`
- Deterministic comparator: `C:\Users\MW\iccv\regular-consolidation-terminal-4f80540f\compare\compare_receipt.json`
  - SHA-256: `f226ba0b20eb9d28cb11e7022949a280618a4ff4f3dab389232da8e31649af6e`
- Final measurement: `C:\Users\MW\iccv\regular-consolidation-terminal\final-measurement.json`
  - SHA-256: `05cb87aecb73ff01d7353e993c0dcc8566564ab81b3813da08c599dbdf4e490c`

이 external record들은 계획이 요구한 result/closure/measurement이며 새 validator, policy, seal 또는 execution authority가 아니다.

## 12. Current Repository State and Final Boundary

세션의 implementation, terminal, carrier와 top-document synchronization은 local `main`에 commit되었다. 작업 전부터 존재한 사용자 소유 `.codex-worktrees/iris-validation-retirement-p10-successor` dirty state는 읽기 외 변경·stage·commit하지 않았다.

최종 claim boundary는 다음과 같다.

- Regular validation execution consolidation: **complete**
- Exact terminal machine validation: **PASS at S_terminal only**
- Non-author terminal/carrier review: **actionable finding 0**
- Remaining eligible consolidation candidate: **0**
- Product/runtime/public-output mutation: **0**
- Wall-clock speedup claim: **not measured**
- Actual token-efficiency claim: **not measured**
- RTC/Publish/release/Workshop/deployment claim: **out of scope**

이후 새 product contract, runtime behavior 또는 validation authority가 바뀌면 이 closeout의 PASS를 승계하지 말고 새 exact subject에서 해당 범위를 다시 검증해야 한다.
