# Implementation Plan — Iris 비정규 Validation Executable 물리 퇴역

> 계획 상태: 실행 준비
>
> Roadmap input: `docs/iris_nonregular_validation_executable_physical_retirement_roadmap.md` 및 사용자 제공 종합 Roadmap
>
> Authority census validated subject: commit `18d0c2ff9de97a71ddf7aa6b03fb059ffbb35089`, tree `56250ea400511eaf84ff84ee19ee8550f89b8492`
>
> Documentation readpoint: `c798313f3740437d24a32532ce5db3a3c9465236`
>
> 계획 원칙: 선행 분류를 다시 수행하지 않고, 이미 non-current로 확정된 executable을 live repository surface에서 최대한 제거한다.

---

## 1. Objective

선행 `1,167` identity census에서 이미 non-current로 분류된 Iris validation executable을 실제 source tree에서 물리 퇴역시킨다.

목표치는 다음과 같다.

```text
pure non-current live source        37 -> 0
pure non-current executable ID     216 -> 0
mixed-source non-current callable    2 -> 0
reproduction-only live source       24 -> 0
evidence-only live source           13 -> 0
current pytest                     433 -> 433
standalone validation                4 -> 4
required execution unit            437 -> 437
```

`reproduction_only`는 live source 보존 면제가 아니다. 필요한 source/input bytes는 existing repository-evidence cold archive/CAS mechanism으로 이전하고 명시적 historical route에서만 repository-external temporary root로 복원한다. `evidence_only`는 executable implementation 대신 predecessor identity, source hash, subject, input, verdict, 최소 failure meaning과 provenance를 가진 compact carrier로 대체한다.

Cleanup 완료는 파일 삭제 수만으로 판정하지 않는다. 37개 pure source와 두 mixed callable의 제거, exclusive support/reference 정리, current exact identity set 보존, repository-wide tracked byte 및 test/tooling LOC 순감소, exact-subject Run A/B와 deterministic comparator PASS를 모두 요구한다.

---

## 2. Scope

이 계획은 다음 변경을 포함한다.

- 선행 census의 `37 files / 216 identities / 329,344 bytes`와 mixed callable `2`를 execution-time subject에 hash-rebind한다.
- Evidence-only `13 files / 63 identities / 60,825 bytes`를 하나의 compact, non-executable retirement carrier와 기존 durable evidence reference로 대체한 뒤 삭제한다.
- Reproduction-only `24 files / 153 identities / 268,519 bytes`와 필요한 exact input/support를 deterministic external cold archive로 보존하고 restore/replay를 검증한 뒤 live source를 삭제한다.
- `test_compose_entrypoint_guard_hardening.py`와 `test_package_layer3_chunks_only_contract.py`에서 non-current callable만 제거한다.
- 마지막 surviving consumer가 사라진 fixture, helper, config, import, path literal, discovery row, taxonomy/source-policy row, manifest와 entrypoint reference를 함께 제거한다.
- `round3_run_contract_tests.py`가 repository-local 6.93MB historical ZIP을 직접 pin하는 구조를 existing resolver/cold-archive restore 경계로 이전한다.
- `validation_contract_reconfirmation`의 대형 census/ledger와 중복 evidence를 existing cold store로 옮기고, repository에는 exact hash, row count, schema, retrieval identity와 claim ceiling만 남긴다.
- Cleanup 전용 scanner/converter/report generator는 repository-external workspace에서 실행하고 final subject에 남기지 않는다.

### Explicitly Out Of Scope

- Current regular pytest 또는 standalone validation의 병합, 축소, 대체
- `1,167` identity의 role/disposition 재분류 또는 full census 재생성
- Target `37 / 216 / 2` 밖 legacy test의 opportunistic 삭제
- Test execution order, framework, assertion style, producer sharing 또는 wall-time 최적화
- Iris runtime Lua, Layer 3/4 data, Browser/Wiki/Tooltip, public text 또는 package payload 변경
- DVF/QG/IAR architecture 변경 또는 historical 의미 재작성
- RTC, Publish Boundary, release, Workshop, B42 또는 deployment readiness 판정
- Git history rewrite 또는 unreachable object pruning

---

## 3. Non-Goals

- Current coverage를 더 적은 test로 다시 설계하지 않는다.
- Historical taxonomy를 폐기하거나 모든 과거 scenario의 실행 가능성을 보장하지 않는다.
- Evidence carrier를 새 regular validator, required execution unit 또는 validation authority로 승격하지 않는다.
- 기존 sealed verdict, source hash, subject identity 또는 failure meaning을 in-place 수정하지 않는다.
- Repository byte 감소를 external archive byte와 합산하지 않는다.
- Comparable benchmark 없이 test wall-time, CPU, memory 또는 Iris runtime 성능 개선을 주장하지 않는다.
- 다른 진행 중인 Iris product/runtime 변경을 이 cleanup에 포함하지 않는다.

---

## 4. Assumptions

- Canonical predecessor input은 `Iris/_docs/round3/validation_contract_reconfirmation/`의 validated `1,167`-row inventory/contract/disposition ledger다. 계획 실행자는 분류 row를 새로 만들지 않고 path/hash/identity를 현재 subject에 다시 결속하는 compact delta만 만든다.
- 실행 시작점은 validated successor의 내용이 통합된 clean isolated worktree다. 현재 사용자 worktree의 unrelated 변경 또는 삭제를 cleanup baseline에 섞지 않는다.
- `Iris/_docs/refactor/repository_evidence_lightweighting/owner_policy_approval.json`의 승인 범위는 plan-enumerated payload, existing external cold-store backend, verified restore, consumer migration과 zero dangling reference를 전제로 physical cleanup을 허용한다.
- `Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json`과 `Iris/validation/residual_refactor/migrate_repository_evidence.py`의 `cold-archive`, `cold-verify`, `cold-restore`, `cold-dispose` 경계를 재사용한다.
- 현재 `historical_reproduction_corpus.zip`은 약 `6,934,423` bytes이고 runner가 직접 pin한다. 24개 target 중 현 manifest에 path가 있는 것은 6개뿐이며 exact current source hash 일치는 0개이므로, 기존 ZIP의 존재만으로 24개 source retirement proof를 대신하지 않는다.
- Evidence compaction은 이번 실행의 mandatory scope로 채택한다. Sealed predecessor bytes를 변경하지 않고 external durable copy와 restore proof가 있는 duplicate physical representation만 제거한다.
- Destructive 변경은 전체를 하나의 거대 transaction으로 묶지 않는다. Dependency closure별 작은 batch를 사용하되, 각 batch 안의 `successor evidence/archive + source deletion + exclusive support deletion + policy/reference update`는 원자적으로 적용한다.
- 고정 evidence 비율은 두지 않는다. 각 batch와 전체 실행 모두 `new tracked cleanup evidence bytes < removed tracked bytes`를 만족해야 한다.
- Existing approval 범위를 벗어난 storage path, unavailable external custody 또는 검증 불가능한 restore가 발견되면 해당 batch만 fail-closed하며 다른 독립 batch의 최대 제거는 계속한다. Live target이 하나라도 남으면 전체 closeout은 `complete`가 아니다.

---

## 5. Repository Areas Affected

### Code

- Evidence-only source 13개: Appendix A의 목록
- Reproduction-only source 24개: Appendix B의 목록
- `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py`
- `Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py`
- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/_docs/round3/build_historical_reproduction_corpus.py`
- `Iris/validation/residual_refactor/migrate_repository_evidence.py` — existing command로 요구사항을 충족하지 못하는 최소 resolver/receipt 보강만 허용
- `Iris/validation/residual_refactor/repository_evidence_codec.py` — existing representation contract 보강이 필요한 경우에만 변경
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`
- Target의 마지막 consumer 제거로 exclusive가 된 `Iris/build/description/v2/tests/fixtures/`, build helper 또는 historical-only support — Phase 1 consumer closure에서 확정한 exact path만 해당

### Docs

- `docs/ARCHITECTURE.md` — live source가 0이 된 최종 architecture state만 additive update
- `docs/DECISIONS.md` — measured removal과 bounded closeout만 append
- `docs/ROADMAP.md` — physical cleanup 항목의 final state만 갱신
- 기존 historical plan/walkthrough의 path mention은 과거 사실로 보존하며 일괄 rewrite하지 않는다.

### Config

- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/round3_pytest_source_classification.json`
- `Iris/_docs/round3/round3_full_discovery_denominator.json`
- `Iris/_docs/round3/current_route_required_validations.json` — exact current identity가 변하지 않았음을 re-pin할 필요가 있을 때만 변경
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- `Iris/validation/clean_checkout/contracts/canonical_gate.json` — referenced hash/manifest identity가 실제로 변경될 때만 변경
- `pytest.ini` — stale source path가 있을 때만 제거하며 discovery breadth는 완화하지 않음
- `.gitignore` / `.gitattributes` — retired archive/source의 active exception이 실제로 orphan이 된 경우에만 정리

### Generated Artifacts

- Repository-external deterministic historical archive와 archive manifest
- Repository-external archive verify/restore/replay receipts
- `Iris/_docs/round3/nonregular_validation_physical_retirement/retirement_manifest.json` — 37 source와 두 mixed callable의 compact delta, source hash, identity count, successor reference, physical delta
- `Iris/_docs/round3/nonregular_validation_physical_retirement/closeout.json` — exact terminal subject와 bounded final result
- `Iris/_docs/round3/validation_contract_reconfirmation/`의 대형 ledger를 대체하는 compact hash-bound pointer/summary
- Run A/B, comparator 및 independent review 결과는 repository-external result root에 보존하고 in-repo closeout에는 hash-bound pointer만 둔다.

---

## 6. Planned Changes

### Change 1 — Exact target lock와 dependency-closure batch manifest

Purpose:

분류를 반복하지 않고 validated predecessor의 `37 / 216 / 2`를 execution subject에 결속하며 삭제 batch의 안전 경계를 확정한다.

Files:

- `Iris/_docs/round3/validation_contract_reconfirmation/validation_unit_inventory.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/contract_ledger.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/disposition_ledger.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/support_dependency_inventory.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/final_composition.json`
- Appendix A/B의 37개 source와 두 mixed source
- `Iris/_docs/round3/nonregular_validation_physical_retirement/retirement_manifest.json`

Implementation Notes:

- Predecessor ledger의 source path, SHA-256, identity count와 disposition을 읽어 `unchanged`, `missing`, `hash_changed`, `already_retired`만 기록한다. Role/disposition 필드를 다시 산출하지 않는다.
- `437 + 216 + 2 + 512 = 1,167` 산술 sanity check만 수행하며 residual `512`를 조사 대상으로 확장하지 않는다.
- 동일 root와 enumeration method로 target file count, raw bytes, LOC, 전체 tracked bytes를 기록한다. Git object database, ignored worktree와 external archive는 별도 storage domain으로 둔다.
- Python imports/AST, subprocess arguments, PowerShell invocation, manifest, exact path literal, filename fragment, ignored tooling과 config를 검사한다.
- Consumer closure 기준으로 batch를 구성한다. 최소 family는 `pre-refactor/phase5 evidence`, `old monolithic build evidence`, `food-semantic/Korean-prose reproduction`, `public-text/terminal/adoption reproduction`, `remaining Layer 3 reproduction`, `mixed callable`, `large evidence/corpus`다.
- Current/product/tooling consumer가 하나라도 있는 support는 유지한다. Non-current target만 소비하는 support는 마지막 consumer batch에 넣는다.
- Existing tracked source를 삭제하기 전 exact rollback anchor를 batch별로 고정한다.

Validation:

- 37 source와 216 identity mapping coverage `100%`
- Mixed target `2/2`
- Target의 batch 중복/미배정 `0`
- Predecessor role/disposition mutation `0`
- New full-census row `0`
- Baseline measurement method와 storage domain 누락 `0`

---

### Change 2 — Historical reproduction route를 external restore 경계로 이전

Purpose:

Reproduction 의무를 live source 및 repository-local 6.93MB ZIP과 분리하고, 24개 source를 삭제할 수 있는 restore path를 먼저 완성한다.

Files:

- `Iris/_docs/round3/round3_run_contract_tests.py`
- `Iris/_docs/round3/build_historical_reproduction_corpus.py`
- `Iris/_docs/refactor/core_refactor/historical_reproduction_corpus.json`
- `Iris/_docs/refactor/core_refactor/historical_reproduction_corpus.zip`
- `Iris/_docs/refactor/core_refactor/phase1_validation_asset_manifest.json`
- `Iris/validation/residual_refactor/migrate_repository_evidence.py`
- `Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json` — 정책 완화가 아니라 current schema가 새 bounded reference를 표현하지 못할 때만 additive change

Implementation Notes:

- Appendix B 24개 source의 exact raw bytes, required fixture/input/support와 expected failure meaning을 deterministic archive selection manifest에 포함한다.
- 기존 cold archive profile의 ordinal member order, fixed timestamp, SHA-256, containment, reparse-point 방어와 create-new 규칙을 그대로 사용한다.
- `round3_run_contract_tests.py --class current`는 archive resolver를 호출하지 않는다. `historical|diagnostic|all`만 explicit archive/reference input을 요구하고 repository-external temporary overlay에 restore한다.
- Runner의 current executable identity, argument/exit semantics, current selection과 failure attribution은 유지한다. Historical route는 missing archive, hash mismatch, path escape, duplicate member 또는 incomplete support에서 fail-loud한다.
- Repository-local corpus manifest/ZIP을 current runner 필수 파일에서 제거하기 전에 external archive의 verify와 fresh-root restore를 완료한다.
- Existing 2,409-row archive가 보존해야 할 별도 historical route를 포함하면 그것을 먼저 external cold store로 이전한다. 24-source successor만 만들면서 다른 historical route를 암묵적으로 버리지 않는다.
- In-repo successor는 external machine absolute path를 기록하지 않고 store identifier, archive SHA-256, row/member-set hash, producer identity, retrieval contract와 claim ceiling만 보유한다.

Validation:

- Appendix B source bytes archive coverage `24/24`
- Required input/support closure coverage `100%`
- Deterministic archive Run A/B hash equality
- `cold-verify`와 fresh external root `cold-restore` exit `0`
- Applicable representative replay의 expected route/failure meaning 일치
- Current/default route의 external archive access `0`
- Restore target escape, duplicate member와 tamper negative fixture가 fail-loud
- Source checkout mutation `0`

---

### Change 3 — Evidence-only executable 13개 전량 삭제

Purpose:

Executable provenance로만 남아 있는 13개 source를 compact non-executable evidence로 대체하고 live source와 exclusive support를 제거한다.

Files:

- Appendix A의 13개 source
- `Iris/_docs/round3/nonregular_validation_physical_retirement/retirement_manifest.json`
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/round3_pytest_source_classification.json`
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- Change 1에서 확인된 evidence-only exclusive fixture/helper/reference

Implementation Notes:

- Compact carrier는 source별 predecessor path/hash, identity count, predecessor ledger hash/range, validation subject, input identity, verdict, 최소 assertion/failure meaning, provenance, successor reference와 claim ceiling만 기록한다.
- 63개 full contract row를 새 carrier에 복사하지 않는다. 원본 ledger의 durable hash-bound reference를 사용한다.
- `test_description_generator.py`, `test_layer3_pipeline.py`, `test_wearable_6f.py`는 제거된/ignored implementation을 import하는 retired route이므로 source bytes가 아니라 provenance만 보존한다.
- Pre-refactor characterization, Phase 5 structural contract, legacy-axis census와 public-text fixture/metric source도 current source로 이동시키거나 regular test로 승격하지 않고 삭제한다.
- Active source policy에서 retired path를 제거한다. Historical documents와 sealed evidence에 포함된 과거 path mention은 dangling executable reference로 세지 않으며 수정하지 않는다.
- New tracked carrier가 해당 batch removed bytes보다 크거나 executable로 수집되면 batch를 적용하지 않는다.

Validation:

- Evidence-only live source `13 -> 0`
- Evidence-only executable identity `63 -> 0`
- 13개 source의 predecessor identity/hash/subject/input/verdict/provenance resolution `13/13`
- Current/required/standalone registration `0`
- Deleted path의 active import/discovery/manifest reference `0`
- Batch tracked bytes 및 test/tooling LOC net decrease `> 0`

---

### Change 4 — Reproduction-only executable 24개 전량 삭제

Purpose:

Change 2에서 검증한 external archive/restore route를 근거로 reproduction-only live source 24개를 normal source tree에서 제거한다.

Files:

- Appendix B의 24개 source
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/round3_pytest_source_classification.json`
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- Change 1에서 확인된 reproduction-only exclusive fixture/helper/config/reference
- `Iris/_docs/round3/nonregular_validation_physical_retirement/retirement_manifest.json`

Implementation Notes:

- Source deletion은 archive verify/restore receipt, route migration과 active policy/reference delta를 같은 batch에 포함한다.
- Korean-prose, food-semantic, public-text, terminal-disposition, live-migration/adoption처럼 support overlap이 큰 family는 shared build module을 삭제하지 않는다. Current/product/tooling consumer가 0인 support만 마지막 family batch에서 제거한다.
- Historical taxonomy row는 live source registration으로 남기지 않는다. 필요한 identity는 external archive manifest의 predecessor identity로만 남긴다.
- Normal configured pytest, current route와 full gate가 external archive를 자동 복원하거나 archived Python을 수집하지 못하게 한다.
- Archive-only executable은 live source count에 포함하지 않지만, restore/replay command는 regular/current authority로 등록하지 않는다.
- Live executable retention 예외를 기본값으로 허용하지 않는다. Verified archive로 표현할 수 없는 기술적 blocker가 발생하면 해당 source를 숨겨서 완료 처리하지 않고 final state를 `partial` 또는 `blocked`로 제한한다.

Validation:

- Reproduction-only live source `24 -> 0`
- Reproduction-only executable identity `153 -> 0`
- External archive/member/source hash coverage `24/24`
- Historical restore/replay exit `0` 또는 expected historical failure meaning 일치
- Current/required discovery의 archive member `0`
- Deleted path의 active import, manifest, command와 string-fragment reference `0`
- Source checkout mutation `0`

---

### Change 5 — Mixed callable, exclusive support와 source-universe coherence 정리

Purpose:

두 mixed source에서 non-current callable만 제거하고 actual source, taxonomy, discovery, manifest와 entrypoint를 동일한 final universe로 맞춘다.

Files:

- `Iris/build/description/v2/tests/test_compose_entrypoint_guard_hardening.py`
- `Iris/build/description/v2/tests/test_package_layer3_chunks_only_contract.py`
- `Iris/_docs/round3/round3_test_taxonomy.json`
- `Iris/_docs/round3/round3_pytest_source_classification.json`
- `Iris/_docs/round3/round3_full_discovery_denominator.json`
- `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
- `Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py`
- `Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py`
- `pytest.ini` 및 Change 1에서 확인된 orphan support/reference

Implementation Notes:

- 제거 callable은 다음 두 개로 고정한다.
  - `ComposeEntrypointGuardHardeningTest.test_legacy_profile_explicit_historical_output_passes`
  - `PackageLayer3ChunksOnlyContractTest.test_workspace_copy_flow_excludes_layer3_monolith`
- 첫 source의 current callable 6개와 둘째 source의 current callable 15개를 before/after exact node ID로 비교한다.
- Shared class setup, constants와 imports는 current callable이 사용하면 유지한다. 두 callable 전용 setup/data만 제거한다.
- 더 이상 필요 없는 mixed `item_overrides`를 제거한다. Default current classification, current assertion/failure class와 failure localization은 유지한다.
- 37개 source 삭제 후 fixture/helper/config consumer closure를 다시 계산하고 surviving consumer 0인 support를 제거한다.
- Final chain을 exact set으로 비교한다.

```text
actual live executable source/node set
-> source classification / taxonomy
-> configured discovery
-> current / historical / diagnostic route
-> required manifest / standalone registry
-> canonical / full-repository entrypoint
```

Validation:

- Mixed non-current callable `2 -> 0`
- Mixed source current callable identity loss `0`
- Current callable assertion/failure meaning 및 localization 변화 `0`
- Orphan fixture/helper/config/import/path/reference `0`
- Unclassified/conflicting source `0`
- Missing manifest target `0`
- Fail-closed guard weakening `0`

---

### Change 6 — 대형 census/corpus evidence 경량화와 temporary tooling 자기 퇴역

Purpose:

선행 auditability를 유지하면서 약 6.15MiB 증가분의 duplicate physical representation과 cleanup 전용 executable을 제거한다.

Files:

- `Iris/_docs/round3/validation_contract_reconfirmation/validation_unit_inventory.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/contract_ledger.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/disposition_ledger.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/support_dependency_inventory.jsonl`
- `Iris/_docs/round3/validation_contract_reconfirmation/final_composition.json`
- `Iris/_docs/round3/validation_contract_reconfirmation/closeout.json`
- `Iris/_docs/refactor/core_refactor/historical_reproduction_corpus.json`
- `Iris/_docs/refactor/core_refactor/historical_reproduction_corpus.zip`
- `Iris/_docs/refactor/repository_evidence_lightweighting/`의 existing CAS/cold-archive receipts와 compact successor
- Change 1~5에서 사용한 one-off checker/report output

Implementation Notes:

- Current executable consumer가 없는 1,167-row raw ledgers는 external cold archive로 이동하고 repository에는 canonical summary, raw SHA-256, row count, schema version, store identifier, retrieval/restore contract와 claim ceiling을 둔다.
- `final_composition.json`, validated closeout와 independent review처럼 사람이 읽는 compact authority summary는 유지한다.
- Existing immutable evidence를 rewrite하지 않는다. External archive promotion과 restore가 성공한 뒤 duplicate repository copy만 제거한다.
- `historical_reproduction_corpus.zip`의 runner 소비가 Change 2에서 이전됐고 모든 historical member가 durable store에 존재할 때 6.93MB ZIP과 0.91MB manifest를 퇴역시킨다.
- Cleanup scanner/converter가 필요하면 repository-external temporary workspace에서 실행한다. 일반화된 새로운 validation framework를 추가하지 않는다.
- Final measurement 전에 tracked scratch report, temporary fixture, generated script, `__pycache__`, pytest cache와 ad hoc result를 제거한다.

Validation:

- Externalized artifact raw SHA-256/row/member count equality
- Fresh external root restore/reconstruction exit `0`
- Required consumer migration coverage `100%`
- Dangling reference 및 orphan retained object `0`
- Predecessor semantic/hash mutation `0`
- Duplicate full-census successor `0`
- Temporary executable/registration/tracked result residue `0`
- New tracked cleanup evidence `<` removed tracked evidence
- Repository-wide tracked bytes 및 test/tooling LOC net decrease `> 0`

---

### Change 7 — Exact-subject validation, independent review와 bounded closeout

Purpose:

모든 deletion과 temporary-tool removal이 끝난 exact final subject에서 current contract 보존과 physical cleanup 완료를 검증한다.

Files:

- `Iris/_docs/round3/nonregular_validation_physical_retirement/retirement_manifest.json`
- `Iris/_docs/round3/nonregular_validation_physical_retirement/closeout.json`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- `docs/ROADMAP.md`

Implementation Notes:

- Validation 전 terminal implementation commit/tree를 고정한다. Run A/B와 comparator receipt는 이 subject와 relevant runner/config blob을 exact binding한다.
- Post-validation closeout carrier는 validated subject를 재정의하지 않는다. Product/config/source delta 없이 result pointer만 추가한다.
- Closeout은 removed/retained/blocked source, identity, raw bytes, LOC, tracked bytes와 storage-domain별 archive size를 분리해 기록한다.
- Independent review는 current/shared support 오삭제, archive restoration, active dangling reference, source-policy guard 완화와 claim overreach를 확인한다.
- 하나라도 live target이 남거나 Run A/B/comparator가 exit `0`이 아니면 `complete`를 금지한다.

Validation:

- Appendix A/B source absence `37/37`
- Mixed callable absence `2/2`
- Current pytest exact identity `433/433`
- Standalone validation `4/4`
- Required execution unit `437/437`
- Exact final subject Run A/B와 comparator exit `0`
- Source checkout mutation `0`, external cleanup `PASS`
- Independent reviewer P0/P1/P2/P3 `0`
- Final tracked bytes와 test/tooling LOC net decrease `> 0`

---

## 7. Validation Plan

### Automated Validation

- Python syntax/import validation:

```powershell
uv run python -m py_compile Iris/_docs/round3/round3_run_contract_tests.py Iris/_docs/round3/build_historical_reproduction_corpus.py Iris/validation/clean_checkout/run_iris_clean_checkout_validation.py Iris/validation/residual_refactor/migrate_repository_evidence.py
```

- Final configured/current collection and denominator guard:

```powershell
uv run python -m pytest --collect-only --round3-contract all --round3-enforce-denominator -p no:cacheprovider
```

- Current route:

```powershell
uv run python Iris/_docs/round3/round3_run_contract_tests.py --class current
```

- Focused source-policy/clean-checkout tests:

```powershell
uv run python -m pytest Iris/validation/clean_checkout/tests/test_iris_clean_checkout_validation.py -p no:cacheprovider
```

- Historical route는 Change 2에서 확정한 explicit external archive/reference argument로 실행한다. Archive verify, restore와 applicable representative replay가 모두 exit `0`이어야 한다.
- `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`로 independent external checkout Run A/B를 canonical contract arguments와 함께 실행한다.
- `Iris/validation/clean_checkout/invoke_deterministic_compare.ps1`로 Run A/B canonical result raw-byte equality, exact subject, runner/config blob과 `437` required unit을 비교한다.
- Static consumer/reference scan은 active code/config/manifest에서 deleted 37 paths와 두 node IDs가 0인지 검사한다. Historical docs, sealed predecessor evidence와 external archive manifest는 별도 allowlisted provenance reference로 분리한다.
- 동일 enumeration으로 before/after tracked file bytes, target raw bytes, Python test/tooling LOC와 external archive bytes를 측정한다.
- `git diff --check`를 실행한다.
- Java/Gradle, JS/TS와 Lua source는 변경하지 않으므로 `./gradlew test`, `pnpm biome check .`, Lua syntax sweep은 이 계획의 relevant command가 아니다. 해당 surface가 실제 diff에 들어오면 즉시 scope violation으로 중단하거나 해당 exact validation을 추가한다.

### Manual Validation

- `retirement_manifest.json`의 37 source와 두 mixed callable을 predecessor ledger row와 source-by-source 대조한다.
- Mixed source current tests의 before/after node ID, setup usage, assertion과 failure message를 검토한다.
- External archive manifest가 machine-specific absolute path 없이 exact retrieval identity와 hash를 제공하는지 검토한다.
- Restore output이 repository-external root에만 생성되고 source checkout, runtime Lua 또는 product data를 변경하지 않는지 확인한다.
- Final diff에서 Iris runtime Lua, generated product payload, public text와 package files 변경이 0인지 확인한다.
- Independent reviewer가 deletion completeness, current/shared support 보존, guard non-weakening과 bounded claim을 검토한다.

### Validation Limits

- PZ in-game Browser/Wiki/Tooltip QA를 수행하지 않는다.
- Multiplayer, long-session 또는 external mod compatibility sweep을 수행하지 않는다.
- Test wall-time, FPS, CPU 또는 memory benchmark를 수행하지 않는다.
- 모든 historical scenario의 replay를 요구하지 않는다. 24개 source의 exact restore coverage와 dependency family별 applicable representative replay를 요구한다.
- RTC, Publish Boundary, package publication, Workshop, release, B42 또는 deployment validation을 수행하지 않는다.
- Target 밖 `512` residual identity의 role 정확성을 재검증하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

영향 있음. Non-current source membership, historical restore routing, source-policy/taxonomy rows, discovery/manifest reference와 census physical representation이 변경된다. Current product/validation-system contract ownership과 `433 + 4` identity는 변경하지 않는다.

### Runtime Behavior Surface

None. Iris runtime Lua와 product behavior는 변경하지 않는다.

### Compatibility Surface

External/public compatibility surface는 None이다. Internal historical runner는 repository-local ZIP 대신 explicit external archive/reference를 사용하게 되지만 current/default command behavior는 유지한다.

### Sealed Artifact Surface

영향 있음. Sealed predecessor 의미와 hash는 불변이다. Physical ledger/corpus를 external cold store로 옮길 때 successor pointer와 restore receipt가 추가되며, original bytes의 verified durable copy 전에는 삭제하지 않는다.

### Public-Facing Output Surface

None. Browser, Wiki, Alt Tooltip, public text와 package output은 변경하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- Historical runner가 current source tree와 archive source를 동시에 읽으면 authority 경계가 다시 섞일 수 있다. Current route의 archive access를 0으로 고정하고 historical overlay를 external temporary root에만 둔다.
- 기존 6.93MB corpus에는 2,409개 member가 있으므로 target 24개만 보존하고 기존 다른 historical member를 유실할 위험이 있다. 전체 consumer/member census와 external archive migration을 ZIP 삭제보다 먼저 수행한다.
- 새 compact carrier가 duplicate `1,167` census가 될 위험이 있다. Source-level 37-row delta와 predecessor ledger hash/reference만 허용한다.

### Runtime Risk

- Product runtime risk는 낮다. Runtime/product file delta가 하나라도 생기면 scope violation으로 처리한다.
- Historical restore의 path traversal, reparse point 또는 overwrite 위험은 existing containment/create-new guard와 negative fixture로 차단한다.

### Compatibility Risk

- Repository-local historical ZIP을 기대하는 내부 개발 command는 explicit archive/reference 입력으로 migration해야 한다.
- External store가 없는 환경에서는 historical route가 fail-loud할 수 있다. Current route는 영향을 받지 않으며 missing custody를 PASS로 변환하지 않는다.
- Windows PowerShell/Python path normalization 차이로 hash/member ordering이 달라질 수 있다. POSIX logical path와 ordinal ordering을 고정한다.

### Regression Risk

- Mixed source의 shared setup 또는 support를 삭제해 current 21개 callable이 깨질 수 있다. Before/after exact node set과 support usage를 비교한다.
- Active config에서 deleted path가 남아 full gate가 fail하거나, 반대로 source-policy guard를 느슨하게 만들어 통과할 위험이 있다. Actual source set에서 entrypoint까지 exact set equality를 요구한다.
- Historical documents와 sealed evidence의 path mention을 무차별 삭제하면 provenance가 손상될 수 있다. Active executable reference와 historical textual reference를 분리한다.
- Cleanup evidence가 source 삭제 효과를 상쇄할 수 있다. Batch별 및 전체 tracked-byte hard gate를 적용한다.

---

## 10. Rollback Plan

Rollback 단위는 dependency-closure batch다. 각 batch 전 source/hash/identity, shared/exclusive support 판정, active config/reference, archive successor, byte/LOC measurement와 exact commit/tree anchor를 기록한다.

다음 조건이면 해당 batch 전체를 명시적으로 revert하고 후속 dependent batch를 중단한다.

- Current pytest/standalone/required identity 감소 또는 의미 변경
- Current/product/tooling consumer가 남은 support 발견
- Archive verify/restore/replay 실패 또는 external custody 불명
- Evidence provenance, subject 또는 failure meaning 손실
- Dangling active reference 또는 orphan retained object 잔존
- Source-policy/denominator/fail-closed guard 완화 필요
- New tracked evidence가 removed tracked bytes 이상
- Source checkout mutation 또는 external cleanup 실패

Rollback은 isolated branch에서 batch commit을 revert하거나 batch patch를 역적용한다. 사용자 작업이 있는 worktree에 `git reset --hard` 또는 `git checkout --`를 사용하지 않는다. External immutable archive와 failed-attempt receipt는 rollback으로 삭제하지 않는다. Archived bytes는 source tree rollback과 독립적으로 보존한다.

---

## 11. Governance Constraints

- `docs/Philosophy.md`의 Iris 역할, 근거 원칙, 중립성, UI surface와 100% Lua runtime 경계를 보존한다.
- Pulse와 다른 spoke module에 새 의존성을 추가하지 않는다.
- Current pytest `433`, standalone `4`, required execution unit `437`을 cleanup 성과를 위해 축소하지 않는다.
- Existing `1,167` census를 immutable predecessor input으로 사용하고 재분류/duplicate ledger를 만들지 않는다.
- Historical/evidence 가치와 live executable 보존을 동일시하지 않는다.
- Source deletion과 evidence/archive successor, exclusive support 및 active config/reference delta는 batch 원자성을 갖는다.
- Current/shared support와 fail-closed guard를 완화하거나 우회하지 않는다.
- Existing repository-evidence owner approval, output policy, CAS/cold-store containment와 deletion contract를 준수한다.
- Sealed artifact는 in-place rewrite하지 않는다.
- Cleanup-only helper를 regular validator, taxonomy class, required gate 또는 장기 tooling으로 채택하지 않는다.
- Runtime/build-time separation을 유지하고 Iris product/runtime에 Python을 추가하지 않는다.
- Unrelated dirty-worktree 변경을 보존하며 cleanup diff에 혼입하지 않는다.
- Exact relevant command가 exit `0`이 아니면 PASS를 주장하지 않는다. Required tooling 부재는 `BLOCKED`다.

---

## 12. Expected Closeout State

Expected closeout target: `complete`

`complete`는 다음을 모두 의미한다.

- Pure non-current source `37 -> 0`
- Pure non-current identity `216 -> 0`
- Mixed non-current callable `2 -> 0`
- Removed target raw source bytes `>= 329,344` plus mixed/exclusive-support delta
- Repository-wide tracked bytes와 test/tooling LOC net decrease `> 0`
- Evidence/reproduction successor의 verify/restore가 exit `0`
- Current exact identity `433`, standalone `4`, required unit `437` 보존
- Final exact subject Run A/B, comparator와 independent review PASS
- Temporary executable 및 tracked scratch residue `0`

Archive custody, restore 또는 current/shared support 때문에 일부 target이 남으면 closeout은 `partial` 또는 `blocked`다. 구현만 끝나고 exact-subject Run A/B/comparator를 수행하지 못하면 `implemented_only`다. 제거량이 크더라도 live target이 하나라도 남으면 target-wide `complete`를 선언하지 않는다.

---

## Appendix A — Evidence-only source 13개

| # | Source | Identities | Raw bytes |
|---:|---|---:|---:|
| 1 | `Iris/build/description/v2/tests/test_dvf_3_3_legacy_combined_route_axis_inventory.py` | 6 | 6,481 |
| 2 | `Iris/build/description/v2/tests/test_dvf_3_3_required_artifact_surface_preflight_census.py` | 4 | 8,145 |
| 3 | `Iris/build/description/v2/tests/test_iris_pre_refactor_browser_characterization.py` | 1 | 1,650 |
| 4 | `Iris/build/description/v2/tests/test_iris_pre_refactor_description_characterization.py` | 1 | 1,174 |
| 5 | `Iris/build/description/v2/tests/test_iris_pre_refactor_detail_characterization.py` | 1 | 1,546 |
| 6 | `Iris/build/description/v2/tests/test_layer3_current_authority_reconstruction.py` | 2 | 2,228 |
| 7 | `Iris/build/description/v2/tests/test_phase5_array_util_contract.py` | 4 | 3,178 |
| 8 | `Iris/build/description/v2/tests/test_phase5_iris_main_function_specs_contract.py` | 4 | 2,704 |
| 9 | `Iris/build/description/v2/tests/test_public_text_quality_acceptance_fixtures.py` | 4 | 2,840 |
| 10 | `Iris/build/description/v2/tests/test_public_text_quality_metric_contract.py` | 8 | 5,825 |
| 11 | `Iris/build/tests/test_description_generator.py` | 5 | 10,955 |
| 12 | `Iris/build/tests/test_layer3_pipeline.py` | 22 | 12,068 |
| 13 | `Iris/build/tests/test_wearable_6f.py` | 1 | 2,031 |
| **합계** |  | **63** | **60,825** |

---

## Appendix B — Reproduction-only source 24개

| # | Source | Identities | Raw bytes |
|---:|---|---:|---:|
| 1 | `Iris/build/description/v2/tests/test_body_plan_phase_d_e.py` | 4 | 14,506 |
| 2 | `Iris/build/description/v2/tests/test_build_acquisition_sprint7_authority_promotion.py` | 1 | 15,058 |
| 3 | `Iris/build/description/v2/tests/test_build_body_role_lexical_cleanup_authority.py` | 1 | 12,720 |
| 4 | `Iris/build/description/v2/tests/test_dvf_3_3_core_registry_boundary_claim_contract_closure.py` | 6 | 6,845 |
| 5 | `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_closeout.py` | 6 | 7,710 |
| 6 | `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_curation_writer.py` | 5 | 9,964 |
| 7 | `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_handoff.py` | 4 | 7,587 |
| 8 | `Iris/build/description/v2/tests/test_dvf_3_3_food_semantic_kernel.py` | 2 | 8,202 |
| 9 | `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_acceptance_gate.py` | 7 | 6,209 |
| 10 | `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_candidate_route.py` | 2 | 7,630 |
| 11 | `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_compiler.py` | 16 | 17,637 |
| 12 | `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_policy.py` | 5 | 3,333 |
| 13 | `Iris/build/description/v2/tests/test_dvf_3_3_korean_prose_semantic_preservation.py` | 3 | 2,809 |
| 14 | `Iris/build/description/v2/tests/test_dvf_3_3_required_artifact_disposition_seal.py` | 8 | 14,804 |
| 15 | `Iris/build/description/v2/tests/test_interaction_cluster_phase_d_runtime.py` | 4 | 14,984 |
| 16 | `Iris/build/description/v2/tests/test_layer3_data_chunking_contract.py` | 5 | 10,822 |
| 17 | `Iris/build/description/v2/tests/test_live_consumer_migration_execution.py` | 7 | 11,863 |
| 18 | `Iris/build/description/v2/tests/test_naturalization_compiler_identity.py` | 3 | 6,441 |
| 19 | `Iris/build/description/v2/tests/test_post_cleanup_phase2_runtime_adoption.py` | 1 | 17,081 |
| 20 | `Iris/build/description/v2/tests/test_public_text_constituent_identity.py` | 20 | 23,928 |
| 21 | `Iris/build/description/v2/tests/test_public_text_quality_acceptance_policy.py` | 9 | 9,371 |
| 22 | `Iris/build/description/v2/tests/test_public_text_quality_acceptance.py` | 6 | 7,719 |
| 23 | `Iris/build/description/v2/tests/test_terminal_disposition_adjudication.py` | 12 | 12,008 |
| 24 | `Iris/build/description/v2/tests/test_validated_naturalization_runtime_adoption.py` | 16 | 19,288 |
| **합계** |  | **153** | **268,519** |

