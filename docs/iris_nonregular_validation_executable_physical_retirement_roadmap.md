# ROADMAP — Iris 비정규 Validation Executable 물리 퇴역 및 증거 보존 경량화

> 상태: 실행 준비 로드맵 — 선행 분류 고정, 제거 중심
>
> 기준 documentation readpoint: `c798313f3740437d24a32532ce5db3a3c9465236`
>
> 선행 validated census subject: commit `18d0c2ff9de97a71ddf7aa6b03fb059ffbb35089`, tree `56250ea400511eaf84ff84ee19ee8550f89b8492`
>
> 이 로드맵은 완료된 `1,167` identity authority census를 다시 수행하지 않는다. 이미 non-current로 분류된 live executable을 최대한 물리 퇴역시키는 것이 유일한 중심 과제다.

---

## 1. Problem Statement

Iris의 validation authority census와 current baseline 복구는 완료됐다. Current regular composition은 pytest `433`과 standalone validation `4`, 합계 `437` required execution unit으로 재확정됐고 exact-subject Run A/B와 deterministic comparator도 통과했다.

그러나 분류 완료가 물리 정리 완료를 뜻하지는 않는다. 선행 readpoint에는 다음 비정규 executable이 여전히 live source 형태로 남아 있다.

| 대상 | Live source | Executable identity | Raw source bytes |
|---|---:|---:|---:|
| `reproduction_only` | `24` | `153` | `268,519` |
| `evidence_only` | `13` | `63` | `60,825` |
| 합계 | `37` | `216` | `329,344` |

또한 current contract와 같은 파일에 남은 live non-current callable이 `2`개 있다. 선행 작업이 실제로 제거한 대상은 current contract가 없던 TC8 identity `1`개뿐이며, baseline부터 documentation carrier까지 tracked tree는 약 `6.15 MiB` 증가했다.

문제는 더 이상 “무엇이 current인가”가 아니다. 문제는 이미 non-current로 확정된 executable을 다음 이유로 live repository에 계속 남겨 두고 있다는 점이다.

- historical 재현 가치와 live Python source 보존을 동일시한다.
- evidence provenance와 executable implementation 전체 보존을 동일시한다.
- mixed source의 current callable 때문에 같은 파일의 non-current callable도 함께 존속한다.
- 대형 census/evidence가 후속 정리의 근거라는 이유로 현재 물리 표현을 그대로 유지한다.
- cleanup을 위해 만든 checker·receipt·scratch artifact가 다시 새 잔존물이 될 수 있다.

이번 작업은 분류를 보완하는 작업이 아니다. 선행 분류를 immutable input으로 사용해 비정규 executable의 live 상태를 제거하고, 재현과 증거 의무는 더 작고 비실행적인 표현으로 이전하는 물리 퇴역 작업이다.

---

## 2. Current State

### 2-1. 고정된 선행 입력

- Authority census denominator: `1,167` executable identities
- Current pytest: `433`
- Standalone validation: `4`
- Required execution units: `437`
- Pure non-current live source: `37`
- Pure non-current executable identities: `216`
- Live mixed-source non-current callable: `2`
- Pure non-current raw source: `329,344 bytes`
- Classification/disposition undecided identity: `0`
- Current baseline and authority-reconfirmation result: predecessor exact subject에 귀속된 `PASS`

`Iris/_docs/round3/validation_contract_reconfirmation/`의 inventory, contract ledger, disposition ledger, support dependency inventory와 final composition은 이 로드맵의 predecessor input이다. 실행자는 이들 row의 authority role을 다시 판정하거나 새 `1,167`행 successor census를 만들지 않는다.

실행 시작 시 수행하는 확인은 재분류가 아니라 rebinding이다. 즉 대상 path가 현재 execution subject에 존재하는지, source hash와 identity mapping이 선행 입력과 일치하는지, 이미 삭제되거나 수정된 drift가 있는지만 compact delta로 기록한다.

### 2-2. 제거 대상의 의미

이 로드맵에서 `live executable`은 다음 중 하나에 해당하는 repository-resident source다.

- pytest 또는 별도 runner가 직접 수집·실행할 수 있다.
- Python/PowerShell/Lua entrypoint로 직접 호출할 수 있다.
- import, subprocess, path-based discovery 또는 manifest를 통해 실행 경로에 도달할 수 있다.
- mixed source 내부에서 callable로 남아 있다.

Content-addressed archive, compressed historical corpus, hash-bound external evidence 또는 실행 권한이 없는 compact receipt는 live executable로 세지 않는다. 다만 archive를 current gate가 자동 복원·실행한다면 그것은 사실상 live dependency이므로 제거 완료로 계산하지 않는다.

### 2-3. 현재 사용 가능한 보존 수단

Repository에는 이미 historical reproduction corpus와 repository-evidence lightweighting의 CAS/cold-archive·restore/verify 메커니즘이 존재한다. 이번 작업은 이를 재사용한다.

- 재현에 source bytes가 필요한 경우: exact bytes와 pinned input을 content-addressed historical bundle로 보존한다.
- 재현 실행이 필요한 경우: 명시적 historical command가 repository-external temporary root로 bundle을 복원해 실행한다.
- evidence만 필요한 경우: subject, source hash, input identity, verdict, 최소 failure meaning, provenance와 retrieval hash를 compact carrier에 둔다.
- 대형 raw result가 필요한 경우: existing durable external storage를 사용하고 repository에는 hash-bound pointer와 claim ceiling만 남긴다.

새 archive architecture, 새 taxonomy, 새 regular validator는 만들지 않는다.

### 2-4. 보호해야 하는 current surface

다음 current surface는 cleanup 대상이 아니다.

```text
current pytest          = 433
standalone validation   = 4
required execution unit = 437
```

Current contract identity, input partition, assertion/failure meaning, standalone CLI boundary, source-policy fail-closed semantics와 failure localization을 유지한다. 선행 PASS는 최종 cleanup subject로 상속하지 않으며 final exact subject에서 다시 검증한다.

---

## 3. Desired Outcome

### 3-1. Live executable surface의 최대 퇴역

목표 상태는 다음과 같다.

```text
pure non-current live source       37 -> 0
pure non-current executable ID    216 -> 0
mixed-source non-current callable   2 -> 0
evidence-only live executable      13 -> 0 files
reproduction-only live executable  24 -> 0 files
```

`reproduction_only`는 삭제 면제 분류가 아니다. 재현 의무는 archive-and-restore route로 이전하고 normal source tree의 executable은 제거한다. Exact source form이 반드시 repository에 live 상태로 있어야만 재현 가능한 예외가 발견되면 해당 항목은 삭제하지 않되, 이 로드맵의 target-wide closeout은 `complete`가 아니라 `partial` 또는 `blocked`로 제한한다.

### 3-2. 증거와 실행 가능성의 분리

완료 후 evidence 보존은 executable source가 아니라 다음 최소 정보로 충족한다.

- predecessor census identity와 source SHA-256
- exact validation subject/tree
- input 또는 fixture identity
- 당시 verdict와 최소 assertion/failure meaning
- provenance와 claim ceiling
- archive/retrieval key 및 archive SHA-256
- restore/verify receipt

Carrier는 current authority, required validation, regular gate 또는 새 executable이 아니다.

### 3-3. Current validation surface의 무손실 유지

Cleanup 뒤에도 pytest `433`, standalone `4`, required unit `437`의 exact identity set이 유지된다. 수치만 같은 다른 test로 바꾸는 것은 허용하지 않는다.

### 3-4. 실제 repository 경량화

다음 물리 지표가 모두 감소해야 한다.

- live executable file 수
- non-current executable identity 수
- test/tooling LOC
- target raw source bytes
- repository-wide tracked bytes

새 evidence와 pointer를 포함한 최종 tracked byte가 baseline보다 작아야 한다. 외부 archive로 이동한 bytes는 repository 감소량과 합산하지 않고 별도 storage domain으로 보고한다.

### 3-5. 잔존물 없는 종료

삭제된 source의 exclusive fixture/helper/config/manifest/discovery/entrypoint와 cleanup 전용 temporary tool을 함께 제거한다. Final subject에는 orphan reference, dead path, temporary checker, tracked scratch result가 없어야 한다.

---

## 4. Constraints

### 4-1. 선행 분류 고정

- `1,167` identity의 role/disposition을 재분류하지 않는다.
- 새로운 full census, duplicate contract ledger 또는 대형 successor inventory를 만들지 않는다.
- 실행 중 발견한 drift는 `added`, `missing`, `hash_changed`, `unchanged`의 compact rebinding delta로만 기록한다.
- Drift가 기존 role을 의심하게 만들면 임의 재판정하지 않고 해당 removal batch를 중단한다.

### 4-2. 제거 우선 정책

- `evidence_only` executable의 기본 처리는 compact evidence 전환 후 삭제다.
- `reproduction_only` executable의 기본 처리는 historical bundle 이전 및 external restore 검증 후 live source 삭제다.
- mixed source의 non-current callable은 current callable과 support를 보존한 채 제거한다.
- 보존 예외는 “historical로 분류됨”이 아니라 live executable 없이는 충족할 수 없는 기존 명시적 의무로만 허용한다.

### 4-3. Current contract 보호

- Current pytest `433`, standalone `4`, required execution unit `437`을 경량화 목표로 축소하지 않는다.
- Current source, shared support, input partition, failure branch와 fail-closed guard를 제거하거나 완화하지 않는다.
- 수집 실패를 피하려고 denominator guard, source-set pin 또는 missing-target failure를 느슨하게 만들지 않는다.

### 4-4. 원자적 removal batch

모든 `source + exclusive support + route/config references + evidence successor` 묶음은 하나의 원자적 batch다. 전체 `37`개를 하나의 거대 commit으로 묶지는 않으며, dependency closure가 독립적인 작은 batch로 나눈다.

각 batch는 다음 상태 중 하나만 허용한다.

- predecessor live source와 기존 reference가 모두 존재한다.
- successor evidence/archive, 삭제와 모든 reference 정리가 함께 존재한다.

Source만 먼저 삭제하거나 stale manifest를 후속 단계까지 남기는 중간 상태는 허용하지 않는다.

### 4-5. 기존 보존 인프라 재사용

- Historical corpus, CAS, cold archive와 repository-external evidence mechanism을 우선 사용한다.
- 새 database, registry, service 또는 validation-of-validation framework를 만들지 않는다.
- Archive restore는 repository-external temporary root만 대상으로 하며 source checkout을 변경하지 않는다.
- Absolute path, `..`, output escape, reparse-point escape를 허용하지 않는다.

### 4-6. Sealed evidence 경계

Predecessor verdict, sealed hash, historical meaning과 subject identity를 수정하지 않는다. Representation을 경량화할 때는 original bytes를 먼저 durable storage에 보존하고 retrieval/hash verification이 성공한 뒤 repository copy 또는 duplicate를 제거한다.

### 4-7. Temporary tooling 자기 퇴역

Cleanup을 위해 작성한 one-off scanner, conversion script, fixture, report generator와 scratch result는 regular route에 등록하지 않는다. Final measurement 전에 모두 제거하거나 repository-external execution workspace로 이동한다.

### 4-8. 비대상 surface

Iris runtime Lua, generated product payload, Layer 3/4 semantic output, Browser/Wiki/Tooltip, public text, public API, package payload와 external mod compatibility contract는 변경하지 않는다.

---

## 5. Non-Goals

- Current regular test의 병합·축소·재설계
- Scenario execution consolidation 또는 producer 공유 확대
- Test framework, assertion style 또는 execution order 변경
- Wall-time, CPU, memory 또는 runtime performance 최적화
- 새 validation taxonomy 또는 authority architecture 설계
- Historical 사실, sealed decision 또는 모든 historical route의 삭제
- 대상 `37 / 216 / 2` 밖 identity의 재분류
- 전체 `1,167` census 재생성
- DVF/QG/IAR 제품 architecture 변경 또는 재도입
- Iris runtime/UI/public text 변경
- RTC, Publish Boundary, package publication, release, Workshop, B42 또는 deployment readiness 판정

---

## 6. Proposed Approach

### 6-1. Removal-first 실행 흐름

```text
sealed census + exact target hashes
-> compact execution-time rebinding
-> dependency-closure removal batches
   -> evidence-only: compact -> verify -> delete
   -> reproduction-only: archive -> restore/replay -> delete
   -> mixed: preserve current -> remove non-current callable
-> exclusive support/reference sweep
-> large evidence duplicate compaction
-> temporary cleanup tooling removal
-> exact-subject Run A/B + comparator
-> bounded closeout
```

분류·contract extraction phase는 두지 않는다. 각 대상의 작업 항목은 선행 disposition에 의해 이미 정해지며, 실행자는 live retention 예외의 존재 여부만 확인한다.

### 6-2. Removal batch 구성

Batch key는 source 파일명이 아니라 dependency closure다. 한 batch에는 다음을 포함한다.

- 제거할 non-current executable identity
- 해당 identity의 source file 또는 mixed callable
- non-current-exclusive fixture/helper/data/config
- taxonomy/source-policy/discovery/manifest/entrypoint reference delta
- compact evidence 또는 reproduction archive successor
- before/after file, identity, LOC, byte measurement
- rollback anchor

Shared support가 여러 removal 대상에만 쓰인다면 마지막 consumer batch에서 제거한다. Current/product/tooling consumer가 하나라도 있으면 유지한다.

### 6-3. Evidence-only 처리

`13 files / 63 identities / 60,825 bytes`를 첫 removal wave로 처리한다.

1. 선행 ledger에서 각 identity의 source hash, subject, input, verdict, failure meaning과 provenance를 읽는다.
2. 이 정보를 source 구현을 복제하지 않는 compact carrier로 투영한다.
3. 필요한 raw bytes가 이미 sealed/durable artifact에 있으면 새 copy를 만들지 않고 reference만 둔다.
4. Retrieval/hash verification을 수행한다.
5. Live executable과 exclusive support를 삭제한다.
6. Current/required/standalone registration이 `0`임을 재확인한다.

Evidence-only source를 “혹시 나중에 쓸 수 있음”이라는 이유로 live 보존하지 않는다.

### 6-4. Reproduction-only 처리

`24 files / 153 identities / 268,519 bytes`를 두 번째 removal wave로 처리한다.

1. Exact source bytes, required fixture, pinned input과 expected failure meaning을 기존 historical corpus/CAS 형식으로 묶는다.
2. Archive manifest는 logical repository-relative path, content hash, subject, entrypoint와 input identity만 보유한다.
3. Historical reproduction command가 bundle을 repository-external temporary root에 복원하도록 기존 route를 조정한다.
4. 복원된 exact bytes와 archive manifest hash를 대조한다.
5. 적용 가능한 representative reproduction을 external root에서 실행해 route가 live source path에 의존하지 않음을 확인한다.
6. Live source와 non-current-exclusive support를 삭제한다.
7. Normal configured/current/full gate가 archive를 자동으로 복원하거나 실행하지 않음을 확인한다.

Repository-local executable 보존이 불가피하다는 주장은 다음을 모두 만족할 때만 예외 후보가 된다.

- 이미 존재하는 명시적 reproduction obligation
- 실제 consumer와 callable entrypoint
- exact pinned subject/input
- 구체적인 expected failure meaning
- archive-and-restore로는 보존할 수 없는 기술적 이유
- current/regular route와의 완전한 격리

예외가 승인돼 남으면 최대 제거 작업은 계속 진행하지만 target-wide `complete`는 금지한다.

### 6-5. Mixed source 처리

남아 있는 mixed-source non-current callable `2`개는 파일 전체가 아니라 callable/support 단위로 처리한다.

- current callable과 그 import/fixture/helper를 고정한다.
- non-current callable과 exclusive setup/data만 삭제한다.
- shared setup을 단순화를 이유로 재작성하지 않는다.
- current node ID, input partition, assertion/failure class와 failure localization을 before/after로 비교한다.
- source-policy mixed-item override가 더 이상 필요 없으면 같은 batch에서 제거한다.

### 6-6. Evidence footprint compaction

약 `6.15 MiB` 증가분을 이번 로드맵의 실제 cleanup 범위로 포함한다. 다만 “모두 삭제”가 아니라 consumer가 없는 duplicate physical representation을 제거한다.

- 기존 `1,167`행 census의 canonical copy는 하나만 남기거나 durable external bundle로 옮긴다.
- Repository에는 exact retrieval key, SHA-256, row count, schema identity, claim ceiling과 compact disposition delta만 남긴다.
- Current/historical runner가 물리 ledger를 직접 읽는다면 먼저 기존 resolver를 통해 동일 logical content를 공급한다.
- Immutable predecessor artifact를 in-place rewrite하지 않는다. 외부화가 허용되지 않는 sealed artifact는 유지하고 다른 duplicate만 제거한다.
- 새 tracked evidence 총량이 제거한 tracked bytes보다 작지 않으면 해당 compaction batch는 적용하지 않는다.

### 6-7. 최종 coherence와 closeout

모든 removal batch 후 actual source universe부터 entrypoint까지 다음 identity chain을 비교한다.

```text
actual live executable set
-> source classification / taxonomy
-> configured discovery
-> current / historical / diagnostic route
-> required manifest / standalone registry
-> canonical / full-repository entrypoint
```

Count equality가 아니라 exact source path, pytest node ID와 command ID set equality를 사용한다. Cleanup 전용 도구를 제거한 뒤 이 exact final subject로 canonical validation을 수행한다.

---

## 7. Authority / Surface Impact

### Authority Surface

영향 있음.

Non-current source membership, historical restore routing, source-policy/taxonomy row, discovery/manifest/entrypoint reference와 tracked source-set pin이 변경될 수 있다. Current/historical/diagnostic의 역할 정의와 current contract ownership은 변경하지 않는다.

### Runtime Behavior Surface

None.

Iris runtime Lua와 product behavior를 변경하지 않는다.

### Compatibility Surface

External/public compatibility surface는 None이다.

Internal historical reproduction command의 입력 위치가 live source path에서 archive restore root로 바뀔 수 있다. 기존 command ID, required arguments, exit semantics와 failure attribution은 유지한다.

### Sealed Artifact Surface

영향 가능.

Predecessor evidence의 의미와 hash는 불변으로 보존한다. Physical representation을 외부화하면 기존 durable storage의 retrieval key/hash와 in-repository pointer가 successor representation이 된다. 이 변경은 evidence storage의 전환이지 validation authority의 전환이 아니다.

### Public-Facing Output Surface

None.

---

## 8. Phases

### Phase 1 — Exact Target Lock and Physical Baseline

Goal:

선행 분류를 재수행하지 않고 `37 / 216 / 2` target을 execution subject에 결속하고 동일 측정법의 물리 baseline을 고정한다.

Primary Changes:

- Predecessor census/ledger/final composition의 path와 SHA-256 고정
- `37` source, `216` identity, mixed callable `2`의 existence/hash rebinding
- `437 + 216 + 2 + 512 = 1,167` arithmetic sanity check
- Source files, executable identities, raw bytes, test/tooling LOC와 repository tracked bytes 측정
- Python AST/import, subprocess literal, string-fragment path, PowerShell invocation, manifest와 ignored-tooling reference scan
- Dependency closure별 removal batch 순서 확정
- Compact rebinding delta 생성

Expected Risks:

- 오래된 path/hash를 현재 source로 오인
- rebinding을 새 분류/census로 비대화
- 동적 consumer 누락
- unrelated dirty-worktree delta를 baseline에 혼입

Expected Validation:

- Target source/identity mapping coverage `100%`
- 분류 row 수정 `0`
- Full successor census 생성 `0`
- Residual arithmetic mismatch `0`
- 모든 target이 정확히 하나의 removal batch에 배정됨
- Before measurement root/enumeration method 기록

Expected Deliverables:

- `target_rebinding_delta.jsonl`
- `physical_baseline.json`
- `removal_batch_manifest.json`
- `dynamic_consumer_scan.json`
- destructive change 이전 exact rollback anchor

---

### Phase 2 — Evidence-Only Executable Retirement

Goal:

Evidence-only `13 files / 63 identities`를 compact evidence로 대체하고 live executable을 전부 제거한다.

Primary Changes:

- Identity별 최소 evidence projection 생성
- 기존 sealed/durable evidence reference 재사용
- Hash-bound retrieval/verification 수행
- `13` live source와 exclusive fixture/helper 제거
- Source-policy/discovery/manifest의 stale reference를 batch별 원자적으로 제거

Expected Risks:

- Compact carrier가 source code 전체를 다시 복제함
- Evidence provenance 또는 failure meaning 손실
- Carrier가 regular validator로 등록됨
- Evidence 추가량이 삭제량을 상쇄함

Expected Validation:

- Evidence-only carrier에서 predecessor identity/hash/subject/input/verdict/provenance resolution `13/13`
- Retrieval/hash verification exit `0`
- Evidence-only live source `0`
- Evidence-only executable identity `0`
- Current/required/standalone registration `0`
- Batch별 tracked byte와 LOC delta가 양수 감소

Expected Deliverables:

- Compact evidence carrier set
- Evidence-only removal receipts
- Removed source/support list
- Phase 2 physical delta

---

### Phase 3 — Reproduction-Only Live Source Evacuation

Goal:

Reproduction-only `24 files / 153 identities`의 재현 가능성을 non-live bundle로 옮기고 normal repository source tree에서 전부 제거한다.

Primary Changes:

- Exact source/fixture/input을 existing historical corpus 또는 CAS에 content-addressed bundle로 저장
- Historical route를 external temporary restore 방식으로 결속
- Representative pinned reproductions restore/replay
- `24` live source와 non-current-exclusive support 제거
- Normal current/configured route의 archive 자동 실행 차단 확인

Expected Risks:

- Archive는 존재하지만 실제 복원이 불가능함
- Historical command가 여전히 deleted source path를 참조함
- Current gate가 archive payload를 암묵적으로 수집함
- 너무 큰 duplicate archive가 repository에 다시 들어옴

Expected Validation:

- Archive manifest path/hash/input coverage `24/24`
- Fresh external root restore verification exit `0`
- Applicable historical replay의 expected route/failure meaning 일치
- Live reproduction-only source `0`
- Live reproduction-only executable identity `0`
- Current/required discovery의 archive payload membership `0`
- Source checkout mutation `0`

Expected Deliverables:

- Content-addressed reproduction bundle/reference
- Restore/replay receipts
- Reproduction-only removal receipts
- Phase 3 physical delta

---

### Phase 4 — Mixed Callable and Exclusive Support Cleanup

Goal:

두 live mixed-source non-current callable을 제거하고 모든 surviving consumer 기준으로 orphan support를 정리한다.

Primary Changes:

- Current callable/node/support exact identity 고정
- Non-current callable `2`와 exclusive setup/data 제거
- 불필요해진 mixed-item override 제거
- 전체 target에 대한 fixture/helper/config consumer closure 재계산
- Last non-current consumer가 사라진 support 제거
- Stale import, node ID, string path, manifest와 entrypoint reference 제거

Expected Risks:

- Current/shared support 오삭제
- Node ID 또는 failure localization 변경
- Dynamic import/path consumer 누락
- Source와 policy가 다른 universe를 가리키는 중간 상태

Expected Validation:

- Mixed non-current callable `2 -> 0`
- Current callable exact identity와 failure semantics loss `0`
- Orphan fixture/helper/config/reference `0`
- Unclassified/conflicting source `0`
- Missing manifest target `0`
- Fail-closed guard weakening `0`

Expected Deliverables:

- Mixed-source before/after identity map
- Exclusive-support removal receipt
- Synchronized source/policy/discovery/manifest state
- Phase 4 physical delta

---

### Phase 5 — Census Evidence Compaction and Temporary Tool Self-Removal

Goal:

선행 auditability를 유지하면서 duplicate evidence footprint와 이번 execution의 temporary tooling을 제거한다.

Primary Changes:

- Census/ledger consumer와 duplicate copy 확인
- Existing CAS/cold archive로 이동 가능한 대형 payload 외부화
- Repository에는 compact hash-bound summary/delta만 유지
- Restoration/reconstruction verification
- One-off scanner/converter/validator, fixture와 tracked scratch result 제거
- Phase 1과 동일한 방법으로 최종 physical measurement

Expected Risks:

- Sealed predecessor artifact를 in-place 변경
- Pointer만 남고 durable bytes가 사라짐
- Temporary tool이 새 regular validation으로 잔존
- 외부 이동량을 repository 절감량과 중복 합산

Expected Validation:

- Predecessor semantic/hash mutation `0`
- Required retrieval/reconstruction exit `0`
- Duplicate full-census successor `0`
- Temporary executable/registration/residue `0`
- New tracked evidence bytes `<` removed tracked bytes
- Repository-wide tracked bytes와 test/tooling LOC net decrease `> 0`

Expected Deliverables:

- Evidence compaction receipt
- Durable retrieval pointers
- Temporary-tool removal receipt
- Final physical measurement

---

### Phase 6 — Final Exact-Subject Validation

Goal:

Cleanup과 temporary-tool removal이 모두 반영된 exact tracked subject에서 current validation과 historical/evidence reference integrity를 검증한다.

Primary Changes:

없음. Validation-only phase다.

Expected Risks:

- Predecessor PASS를 final subject에 잘못 상속
- Run A/B subject 또는 runner blob 불일치
- Cleanup-focused check만 통과하고 canonical gate 실패
- Validation 실행이 source checkout을 변경

Expected Validation:

- `uv run python -m pytest --collect-only --round3-contract all --round3-enforce-denominator -p no:cacheprovider`
- `uv run python Iris/_docs/round3/round3_run_contract_tests.py --class current`
- Changed Python source import/compile 및 affected focused tests
- Applicable historical restore/replay route
- `invoke_receipt_bound_full_gate.ps1`를 통한 independent external checkout Run A/B
- `invoke_deterministic_compare.ps1`를 통한 canonical raw-byte equality와 exact-subject binding
- Current pytest `433/433`, standalone `4/4`, required unit `437/437`
- Run A/B와 comparator exit `0`
- Source checkout tracked/untracked mutation `0`
- External execution cleanup `PASS`

필요한 `uv`, Python, PowerShell 또는 clean-checkout 환경이 없으면 이 phase는 `PASS`가 아니라 `BLOCKED`다.

Expected Deliverables:

- Exact validated subject commit/tree
- Repository-external Run A/B receipts
- Deterministic comparator receipt
- Final composition and route identity report

---

### Phase 7 — Independent Review and Bounded Closeout

Goal:

제거량, 보존된 evidence/reproduction, current contract 보존과 validation ceiling을 같은 exact subject에 결속한다.

Primary Changes:

- Independent reviewer가 deletion completeness, archive restoration, current/shared support 보존, guard non-weakening과 claim boundary 검토
- Removed/retained/blocked 수치와 physical delta 기록
- `validated`, `out_of_scope`, `unvalidated_but_in_scope` 분리
- Top-level readpoint supersession 여부 disclose
- Post-validation carrier는 exact validated subject의 hash-bound pointer만 추가

Expected Risks:

- 남은 non-current executable을 숨긴 채 `complete` 선언
- External archive 존재만으로 retrieval을 검증했다고 주장
- Post-validation carrier가 새 validation authority로 오해됨
- Runtime/release 성과로 claim 확대

Expected Validation:

- Independent reviewer P0/P1/P2/P3 `0`
- 모든 positive claim과 receipt의 1:1 binding
- Closeout pointer와 Run A/B/comparator exact subject 일치
- Post-validation carrier의 source/config/product delta `0`
- 공개되지 않은 owner action `0`

Expected Deliverables:

- Independent review
- Readpoint supersession disclosure
- Bounded closeout
- Compact final removal summary

---

## 9. Validation Expectations

### Expected Validation Depth

**heavy**

Runtime behavior는 변경하지 않지만 validation authority-adjacent source membership, historical execution path와 sealed-evidence representation을 변경하므로 exact-subject validation이 필요하다.

### Expected Validation Areas

- determinism
- migration
- regression
- internal historical reproduction compatibility
- evidence retrieval/reconstruction integrity

### Phase Gates

- Phase 1이 target/hash/dependency closure를 닫기 전 destructive deletion을 시작하지 않는다.
- 각 removal batch는 successor evidence/archive verification과 source/reference 삭제가 같은 transaction에 있어야 한다.
- Phase 2~4의 batch-focused validation이 실패하면 다음 batch로 진행하지 않는다.
- Phase 5에서 temporary tool이 남아 있으면 final subject를 만들지 않는다.
- Phase 6 Run A/B/comparator가 모두 exit `0`이 아니면 `complete`를 선언하지 않는다.

### Known Validation Limits

이 로드맵은 다음을 검증하지 않는다.

- PZ runtime, Browser/Wiki/Tooltip 동작
- Multiplayer 또는 long-session behavior
- FPS, frame time, CPU, memory 또는 test wall-time 개선
- External mod compatibility sweep
- RTC, Publish Boundary, package/release/Workshop/B42/deployment readiness
- Target 밖 identity의 분류 정확성
- 모든 historical scenario의 의미적 동등성

Applicable pinned reproduction의 restore/replay는 검증하지만, 모든 과거 환경을 완전 재현할 수 있다고 주장하지 않는다.

---

## 10. Risk Assessment

### High Risk

- **Current contract 또는 shared support 오삭제**: mixed callable과 support dependency closure를 exact identity로 고정하고 batch 후 current set equality를 검사한다.
- **Historical reproduction 파괴**: replacement-first 원칙으로 archive restore/replay가 성공하기 전 live source를 삭제하지 않는다.
- **Evidence 비가역성**: durable bytes, retrieval key와 SHA-256를 검증하고 predecessor evidence를 in-place rewrite하지 않는다.
- **Fail-closed 약화**: source universe 변화에 맞춘 membership delta만 허용하고 guard coverage/failure condition 완화는 rollback 사유로 둔다.
- **형식적 외부화**: repository 감소량과 external archive 증가량을 별도 domain으로 측정하며 retrieval이 없는 pointer-only cleanup을 금지한다.

### Medium Risk

- **동적 consumer 누락**: AST/import뿐 아니라 subprocess, 문자열 path fragment, PowerShell, manifest와 ignored tooling을 확인한다.
- **거대 archive 재생성**: 기존 CAS/cold archive를 재사용하고 repository-local duplicate bundle을 만들지 않는다.
- **Evidence carrier의 authority 재진입**: current/required/standalone registration과 automatic discovery membership을 모두 `0`으로 검증한다.
- **Temporary cleanup tooling 잔존**: final measurement 전에 self-removal phase를 두고 residue scan을 수행한다.
- **Unrelated worktree 변경 혼입**: isolated branch/disposable checkout과 exact path allowlist를 사용한다.

### Low Risk

- Markdown/documentation의 stale path
- Path separator, EOL 또는 line-count 계산 차이
- Closeout summary의 반올림 또는 storage-domain 표기 오류

---

## 11. Rollback Strategy

Rollback 단위는 파일 하나가 아니라 removal batch 전체다. 각 batch 전 다음 predecessor identity를 기록한다.

- source와 executable identity
- exclusive/shared support 판정
- taxonomy/source-policy/discovery/manifest/entrypoint reference
- evidence/archive target과 retrieval hash
- tracked bytes와 test/tooling LOC
- exact commit/tree rollback anchor

다음 조건에서는 해당 batch를 전부 되돌리고 후속 batch를 중단한다.

- Current pytest/standalone/required identity 감소 또는 의미 변경
- Shared/product/tooling consumer 발견
- Archive restore, hash verify 또는 applicable replay 실패
- Evidence provenance/failure meaning 손실
- Orphan/dangling reference 잔존
- Fail-closed guard 완화가 필요함
- Source/config/manifest가 하나의 final universe로 정렬되지 않음
- Batch의 새 tracked evidence가 제거 bytes 이상임
- Cleanup-attributable historical/current failure 또는 attribution unknown
- Source checkout mutation 또는 external cleanup 실패

Rollback은 isolated branch/disposable checkout에서 batch commit을 명시적으로 revert하거나 해당 batch patch만 역적용한다. 사용자 소유 worktree와 unrelated 변경에는 `git reset --hard` 또는 `git checkout --`를 사용하지 않는다. Archive에 이미 기록된 immutable predecessor bytes와 failed-attempt receipt는 rollback 때문에 삭제하지 않는다.

---

## 12. Success Criteria

### 12-1. Target 제거 완료

- Pure non-current live source: `37 -> 0`
- Pure non-current executable identity: `216 -> 0`
- Mixed-source live non-current callable: `2 -> 0`
- Target 미배정 removal batch: `0`
- Target 밖 identity 재분류: `0`
- 새 full `1,167`행 census: `0`

### 12-2. Reproduction 보존

- Reproduction-only live executable source: `0`
- `24/24` source에 archive manifest와 source hash 존재
- Required pinned input/fixture의 restore coverage `100%`
- Applicable historical replay exit/failure meaning 일치
- Current/required route의 archive payload 자동 실행 `0`

### 12-3. Evidence 보존

- Evidence-only live executable source: `0`
- `13/13` source가 compact carrier를 통해 predecessor identity/subject/input/verdict/provenance로 추적됨
- Hash-bound retrieval 또는 deterministic reconstruction 확인
- Evidence carrier의 current/required/standalone registration `0`

### 12-4. Dependency와 coherence

- Orphan fixture/helper/config/manifest/discovery/entrypoint reference `0`
- Deleted source/node/path dangling reference `0`
- Unclassified/conflicting source `0`
- Missing manifest target `0`
- Actual source, taxonomy/source-policy, discovery, route, manifest와 entrypoint exact set mismatch `0`
- Fail-closed guard semantic weakening `0`

### 12-5. Physical 경량화

- Removed source files `>= 37`
- Removed non-current executable identities `>= 218` (`216` pure + `2` mixed)
- Removed target raw source bytes `>= 329,344` plus mixed-callable/exclusive-support delta
- Repository-wide tracked bytes net decrease `> 0`
- Repository-wide test/tooling LOC net decrease `> 0`
- New tracked cleanup evidence `<` removed tracked footprint
- Temporary cleanup executable/fixture/result residue `0`

### 12-6. Current contract와 final gate

```text
current pytest                           = 433
standalone validation                    = 4
required execution units                 = 437
current product contract loss            = 0
current validation-system contract loss  = 0
```

- Exact final subject Run A exit `0`
- Exact final subject Run B exit `0`
- Deterministic comparator exit `0`
- Run A/B subject 및 relevant runner blob identity 일치
- Source checkout mutation `0`
- External execution cleanup `PASS`
- Independent reviewer P0/P1/P2/P3 `0`

### 12-7. Closeout 상태 규칙

- 위 성공 조건을 모두 만족하면 `complete`다.
- 일부 batch만 제거되고 live target이 남으면 `partial`이다.
- 구현은 끝났으나 Phase 6이 실행되지 않았으면 `implemented_only`다.
- Required tooling, durable archive custody, restore path 또는 필요한 authority가 없어 더 진행할 수 없으면 `blocked`다.
- Live retention 예외가 하나라도 남으면 제거량이 크더라도 target-wide `complete`를 금지한다.

---

## 13. Expected Claim Boundary

이 로드맵이 `complete`로 닫히면 다음만 주장할 수 있다.

> 선행 census에서 non-current로 확정된 Iris validation executable `37 files / 216 identities`와 mixed non-current callable `2`를 live repository surface에서 물리 퇴역시켰다. 필요한 historical reproduction과 evidence는 기존 durable archive/CAS 및 compact hash-bound carrier로 보존했고, current pytest `433`, standalone validation `4`, required execution unit `437`은 exact final subject의 Run A/B와 deterministic comparator에서 유지됐다. Repository tracked bytes와 test/tooling LOC는 측정된 범위에서 순감소했다.

이 claim은 다음으로 확대되지 않는다.

- Historical information 또는 모든 historical route를 삭제했다는 주장
- Target 밖 legacy/test/tooling debt를 모두 제거했다는 주장
- Current regular test suite를 축소하거나 최적화했다는 주장
- 모든 과거 환경의 완전 재현 주장
- Test wall-time, CPU, memory 또는 runtime 성능 개선 주장
- Iris runtime behavior, public text 또는 external compatibility 검증 주장
- RTC, Publish Boundary, package/release/Workshop/B42/deployment readiness 주장

Final gate 결과는 exact validated subject에만 귀속된다. Post-validation evidence carrier나 이후 repository state는 그 PASS를 자동 상속하지 않는다.
