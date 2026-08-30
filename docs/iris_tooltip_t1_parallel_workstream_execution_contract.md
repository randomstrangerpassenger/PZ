# Iris Tooltip T1-D Parallel Workstream Execution Contract

> 상태: planned / four-workstream synchronization authority
> 적용 대상: T1-D1, T1-D3, T1-D4, T1-D5
> 통합 소비자: T1-D6
> 작성일: 2026-08-29

이 문서는 T1-D1, T1-D3, T1-D4, T1-D5가 같은 출발점과 통합 형식을 사용하면서 서로 기다리지 않고 병렬 실행되기 위한 최소 공통 계약이다. 각 작업의 semantic owner 판단과 domain-specific validation은 각 계획이 소유한다. 이 문서는 그 판단을 합치거나 대신하지 않는다.

각 계획의 문구가 이 계약의 predecessor, 병렬 실행, current adoption, 공통 파일 소유권, bundle envelope 또는 테스트 예산과 충돌하면 이 계약이 우선한다.

## 1. 실행 순서

```text
T1-D1 ──> T1-D2 ──┐
T1-D3 ─────────────┤
T1-D4 ─────────────┤──> T1-D6
T1-D5 ─────────────┘
```

- T1-D1, T1-D3, T1-D4, T1-D5는 동시에 시작할 수 있다.
- T1-D2는 validated T1-D1 correction bundle을 입력으로 시작한다.
- T1-D6는 T1-D2, T1-D3, T1-D4, T1-D5 bundle이 모두 terminal state를 발행한 뒤 시작한다.
- 한 작업선의 진행 중 상태를 다른 작업선이 current authority로 소비하지 않는다.

## 2. 공통 predecessor

네 작업선의 공통 semantic predecessor는 검증 완료된 Tooltip T1-C corrective subject다.

```text
commit: 6b7118dc229bf8138302696e1aa5e5b7454589dc
tree: 4eae6fbdb3d0b2cb532f875b96137335a403f2fc
iris_tooling package tree: d1d0c098fb6f06222194e7e032af80932780b275
final closeout SHA-256: 6e255227b0aa8381453a563e3ede9e96c59be82c9bb3a7cb6eba8f488039b4a3
```

각 작업은 별도 clean worktree 또는 동등하게 격리된 clean synthetic subject에서 시작한다. Planning HEAD, dirty working tree, 문서 작성 시점의 관측 commit은 실행 predecessor가 아니다.

Predecessor commit을 직접 사용할 수 없는 경우에는 다음 전부를 포함하는 exact path/blob equivalence manifest가 필요하다.

- `Iris/_docs/authority/tooltip_t1/**`
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/**`
- T1 focused test three-file set과 fixture contract
- T1-C owner inputs
- T1-C final environment authority locator/record content
- `Iris/build/ENTRYPOINTS.md`의 relevant command owner

Ancestry 또는 위 equivalence를 증명하지 못하면 해당 작업은 mutation 전에 `blocked`다.

## 3. 공통 support freeze

모든 작업은 같은 current T1 support predicate를 사용한다.

```text
predicate: current-owner-fulltype-union-v1
identity: case-sensitive exact FullType
```

각 작업은 mutation 전에 동일 predecessor에서 다음을 독립적으로 재도출한다.

- ordered exact FullType set
- support count
- canonical ordered-set SHA-256
- owner-universe membership relation
- starting correction ledger owner/reason/count distribution

`canonical ordered-set SHA-256`의 입력 바이트는 다음 하나로 고정한다.

```text
values = case-sensitive exact FullType의 중복 제거 집합
order = exact FullType의 ordinal ascending order
bytes = 각 value의 UTF-8 bytes 뒤에 LF(0x0A)를 붙여 순서대로 연결
final LF = present
BOM = absent
JSON encoding = 사용하지 않음
digest = SHA-256(bytes)
```

즉, 구현상 동등 표현은 `sha256(b"".join(value.encode("utf-8") + b"\n" for value in sorted(set(values))))`이다. Count와 exact set이 같더라도 JSON array, length prefix, platform newline 또는 final-LF 없는 직렬화의 hash는 공통 support hash로 인정하지 않는다.

Planning baseline은 support `2,280`, T2-blocking correction `5,625`지만 상수 expectation으로 사용하지 않는다. 네 작업의 frozen support hash가 서로 다르면 숫자를 맞추거나 한 작업의 산출물을 복사하지 않는다. 해당 작업은 `integration_impact.support_freeze_mismatch=true`를 기록하고 fail-closed한다.

## 4. Workstream semantic ownership

| Workstream | Exclusive semantic responsibility | Direct successor |
| --- | --- | --- |
| T1-D1 | Layer 2 Classification identity, membership, primary subcategory, KO/EN surface, authority/provenance와 positive absence | T1-D2 |
| T1-D3 | Frozen `DVF_OWNER_ROW_MISSING` target의 approved Layer 3 fact 또는 legitimate absence disposition | T1-D6 |
| T1-D4 | Frozen selected Recipe identity의 QG-approved KO/EN interaction surface | T1-D6 |
| T1-D5 | Declared exact FullType pair의 presentation-owner support disposition과 exact-key preservation | T1-D6 |

각 작업은 자기 owner correction만 해결한다. 다른 owner correction은 actual re-audit delta로 관찰하고 자동 수정, 산술 차감, owner 이동 또는 replacement blocker로 바꾸지 않는다.

T1-D1은 Menu consumer relation을 닫거나 Menu runtime/public source를 변경하지 않는다. T1-D2가 D1 bundle을 소비해 Menu/Tooltip Layer 2 authority relation을 별도로 다룬다.

## 5. Repository mutation ownership

### 5.1 Workstream-exclusive paths

각 작업은 자신의 owner registry, schema, materializer/validator module, external candidate와 workstream-specific authority record를 소유할 수 있다.

### 5.2 Shared integration surfaces

다음 경로는 여러 작업이 isolated candidate에서 변경 제안을 만들 수 있지만 어느 작업도 그 변경을 global current adoption으로 주장하지 않는다.

```text
Iris/tooling/src/iris_tooling/domains/tooltip_t1/{audit,contract,models,projection}.py
Iris/tooling/tests/test_tooltip_t1_{contract,projection,audit}.py
Iris/tooling/tests/fixtures/tooltip_t1/contract_expectations.json
Iris/_docs/authority/tooltip_t1/**
docs/iris_tooltip_t1_display_contract_policy.md
```

Shared-path 변경은 bundle의 `shared_path_delta`에 path, base blob, proposed blob 또는 patch hash, workstream reason과 merge invariant를 기록한다. T1-D6가 모든 shared delta를 하나의 integration subject에서 병합하고 전체 T1 재감사를 수행한다.

### 5.3 T1-D6-exclusive current adoption paths

다음 경로의 cross-stage/global current adoption은 T1-D6만 수행한다.

```text
Iris/_docs/authority/iris_current_authority_manifest.json
Iris/_docs/authority/iris_current_route_index.json
Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json
Iris/build/ENTRYPOINTS.md
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
```

T1-D1, T1-D3, T1-D4, T1-D5는 위 파일을 read-only integration input으로 취급한다. 필요한 successor 문구나 route delta는 bundle에 proposal로 기록할 수 있지만 current pointer, current route, ecosystem status 또는 formal product claim을 직접 갱신하지 않는다.

## 6. Workstream bundle envelope

각 작업은 repository-external immutable empty root에 다음 공통 envelope를 가진 correction bundle을 생성한다.

```text
schema_version
workstream_id
terminal_state
predecessor_commit
predecessor_tree
predecessor_closeout_sha256
workstream_subject_commit
workstream_subject_tree
support_predicate
frozen_support_count
frozen_support_sha256
starting_correction_distribution
target_owner
target_reason_codes
target_exact_set_sha256
resolved_entries
remaining_entries
owner_authority_refs
evidence_refs
artifact_hashes
shared_path_delta
protected_path_hashes
integration_impact
acceptance_condition
re_audit_condition
validation_receipts
claim_ceiling
integration_instructions
```

`integration_impact`는 최소 다음 boolean과 affected exact set을 제공한다.

```text
support_set_changed
shared_contract_change_required
other_owner_delta_detected
predecessor_mismatch
common_path_conflict_detected
full_reaudit_required
```

다른 작업에 영향을 발견해도 그 작업의 bundle이나 owner source를 수정하지 않는다. 영향을 기록하고 T1-D6가 통합 시 disposition한다.

## 7. Workstream terminal vocabulary

각 작업은 다음 범위에서만 terminal state를 발행한다.

```text
workstream_correction_bundle = complete | partial | blocked | implemented_only
current_ecosystem_adoption = pending_T1_D6
T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS
production_t2_handoff = absent
```

Domain 계획이 더 좁은 terminal vocabulary를 요구하면 그 좁은 집합을 사용할 수 있다. 어느 작업도 독자적으로 전체 T1 formal closeout, global current authority adoption, T2 `OPEN` 또는 production handoff를 주장하지 않는다.

## 8. Minimal test budget

테스트의 목표는 필요한 불변식을 검증하는 것이며 작업명별 test identity를 늘리는 것이 아니다.

기본 예산은 다음과 같다.

```text
new test files = 0
new top-level test functions/families = 0
new standalone validation framework = 0
```

검증 case는 우선순위대로 다음 위치에 통합한다.

1. 기존 Tooltip T1 contract/projection/audit parameter table과 fixture row
2. 기존 `test_classification_candidate_install.py` parameterization
3. generation-bearing D3에서만 기존 DVF complete-generation/install test parameterization
4. existing candidate/audit receipts의 machine metrics와 exact ledger comparison

기존 family로 필수 code path를 정직하게 실행할 수 없다는 구체적 근거가 있을 때만 예외를 허용한다.

- 새 test file은 만들지 않는다.
- 기존 test file 안에 parameterized function 최대 1개를 추가할 수 있다.
- 예외 사유, 대체를 검토한 기존 family, 추가된 function count와 제거 조건을 bundle에 기록한다.
- 단순히 workstream 이름을 분리하거나 fixture readability를 높이기 위한 예외는 허용하지 않는다.

각 계획의 과거 문구가 `test_tooltip_t1_d3.py`, `test_tooltip_t1_d4.py`, `test_classification_layer2.py` 또는 다른 workstream 전용 test file을 요구하면 그 요구는 폐기된다.

## 9. Validation ownership

### 9.1 Each parallel workstream

각 작업이 반드시 수행하는 검증은 다음으로 제한한다.

- common predecessor/support freeze validation
- owner schema, evidence와 semantic binding validation
- 기존 focused parameterized tests
- domain candidate materialization twice when it has a materializer
- candidate byte/digest determinism
- protected-path and non-target invariance
- affected-range audit and correction reconciliation
- immutable bundle hash/receipt validation
- `git diff --check`

작업이 current ecosystem을 채택하지 않으므로 workstream마다 fresh current environment authority를 발행하거나 canonical repository full-gate Run A/B, global comparator와 Tooltip T1 post-gate finalizer를 반복하지 않는다.

### 9.2 T1-D6

T1-D6가 다음 formal validation을 한 번 수행한다.

- all bundle schema/hash/predecessor/support compatibility validation
- shared-path delta merge and conflict attribution
- fresh integrated wheel/environment authority
- integrated whole-universe T1 audit
- canonical clean-checkout Run A
- canonical clean-checkout Run B
- repository-owned deterministic comparator
- post-gate finalizer
- blocker `0`일 때만 strict production T2 handoff generation

Applicable current authority가 특정 workstream의 generation/install 경로에 별도 필수 검증을 이미 요구하는 경우 그 executed-path validation은 해당 workstream이 수행한다. 이는 global full-gate 반복을 허가하지 않는다.

## 10. Integration acceptance

T1-D6는 다음 조건을 만족하지 않는 bundle을 current integration에 사용하지 않는다.

- common predecessor inclusion/equivalence valid
- common support freeze compatible or explicitly re-audited
- owner approval/evidence valid
- no semantic inference/fallback/reselection
- target correction reconciliation exact
- other-owner delta fully attributed
- protected shared/current paths not independently adopted
- focused test budget respected or exception justified
- bundle bytes and receipts hash-valid

Support set 변경, shared schema conflict 또는 cross-owner semantic dependency가 발견되면 T1-D6는 affected bundle을 새 integration subject에서 재감사하거나 해당 workstream을 재실행 대상으로 돌린다. 숫자 보정이나 silent row dropping으로 통합하지 않는다.
