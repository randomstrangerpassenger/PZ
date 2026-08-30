# Iris Tooltip T1-D6 통합 current 채택·최종 재감사·strict production T2 handoff 개방 계획

## 문서 상태

- 상태: 실행 전 개정 계획
- 작업 성격: T1-D1~D5 결과의 최종 통합, whole-universe 재감사, T2 handoff 개방
- 실행 기준 direct parent:
  - commit: `76fe186d44815c9fa061d496ce88224e2ddce082`
  - tree: `f6532a6fca016feee503ca5c154d90607741f5ee`
- 검증 깊이: focused validation + 기존 canonical full gate
- 테스트 원칙: 새 테스트 체계를 만들지 않고 기존 테스트와 gate를 최소 횟수로 사용

---

## 1. 목적

T1-D1~D5에서 각 owner correction은 이미 해결되었고, T1-D2의 isolated candidate에서는 whole-T1 correction이 `0`이며 progression이 `OPEN`인 것이 확인되었다.

T1-D6의 목적은 이 결과들을 다시 설계하거나 재구현하는 것이 아니다. 하나의 exact machine subject에서 다음을 수행하는 최종 통합 단계다.

1. 이미 main에 통합된 D1~D5 결과와 D2 결과의 계보 및 필수 입력을 확인한다.
2. 2,280개 exact FullType 전체를 동일 subject에서 다시 감사한다.
3. T2-blocking correction이 정확히 `0`인지 확인한다.
4. blocker가 `0`일 때만 strict T2 handoff input과 manifest를 생성한다.
5. fresh installed environment와 기존 canonical Run A/Run B/comparator를 통과한다.
6. 기존 post-gate finalizer가 성공한 뒤에만 formal closeout과 current 채택을 완료한다.

성공 상태는 다음과 같다.

```text
upstream_blocker_count = 0
contract_blocker_count = 0
T2_FULL_DATA_PROGRESSION = OPEN
production_t2_handoff = present
contract_and_audit_axis = complete
formal_closeout_state = complete
```

---

## 2. 동결 입력

### 2.1 실행 기준 subject

실행은 반드시 다음 exact direct parent에서 만든 clean isolated worktree에서 시작한다.

```text
commit = 76fe186d44815c9fa061d496ce88224e2ddce082
tree   = f6532a6fca016feee503ca5c154d90607741f5ee
```

선택된 일반 작업 트리에 남아 있는 사용자 문서 변경은 입력으로 소비하거나 수정하지 않는다.

### 2.2 D2 구현 기준

```text
D2 implementation commit = 0e959b3bd7055d58f319fa9d69a5b110bf48b8b7
D2 implementation tree   = 5dbc1a830e5a911eece943102c6078102c3d9611
D2 bundle manifest SHA-256 = 25cc173f9b47effb23b0c4823cc33be82b012ba8e9f6c1281172bdf50e62b39d
```

D2 docs-only successor는 D2 구현 결과를 대체하지 않는다. D6는 구현 subject의 계보와 현재 main에 포함된 결과를 확인한 뒤, D6 exact subject에서 relation을 새로 materialize한다.

### 2.3 동결 집합

```text
support_count = 2,280
support_sha256 = 3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6

layer2_applicable_count = 1,406
layer2_applicable_sha256 = c5a77d86eb875cecf03edf5ab67f29361f58947bd97493e522667b593130f264

layer2_display_silence_count = 874
layer2_display_silence_sha256 = d13fa6ac9072a3ab2c61bc59990bfb948010ce8b2fc3211aa1ecb7b5c6c121de
```

직렬화 규칙은 exact case-sensitive FullType을 ordinal ascending으로 정렬하고 각 UTF-8 값 뒤에 LF를 붙이는 기존 규칙을 사용한다. JSON 배열이나 다른 직렬화를 같은 집합의 canonical hash로 사용하지 않는다.

### 2.4 workstream 결과 취급

- D1~D5의 결과는 이미 main에 통합되어 있다.
- D6는 과거 workstream patch를 다시 적용하지 않는다.
- 외부 bundle은 계보와 결과 확인을 위한 입력 증거일 뿐, 새 semantic authority가 아니다.
- bundle이 접근 가능한 경우 manifest, receipt, subject, support binding만 한 번 확인한다.
- 임시 경로의 과거 bundle이 사라졌더라도 구현 계보와 D6 subject에서의 fresh materialization으로 필수 사실을 재현할 수 있으면 그것만으로 D6를 차단하지 않는다.
- 접근할 수 없는 과거 artifact를 보존했다고 주장하지 않는다.

---

## 3. 범위

### 3.1 포함 범위

- clean isolated admission
- D1~D5 및 D2 구현 계보 확인
- current authority manifest와 route의 필요한 통합
- D2 Menu/Tooltip consumer relation의 same-subject 재생성
- 2,280개 whole-universe T1 재감사
- 단일 `t2_blocking=true` correction 집합에 기반한 progression 판정
- blocker `0`일 때 strict T2 handoff 생성
- fresh wheel build와 fresh environment install
- installed CLI를 통한 candidate 재생성 및 검증
- 동일 exact subject의 canonical Run A/Run B
- deterministic comparator
- 기존 post-gate finalizer를 이용한 formal closeout
- final production handoff와 current route의 readback
- 필수 생태계 문서 갱신

### 3.2 범위 밖

- Classification, DVF, QG/locale, Menu relation의 재설계
- owner가 발행하지 않은 의미의 보정 또는 추론
- Tooltip 정적 Lua 생성
- `IrisAltTooltip` 런타임 구현
- PZ 실제 실행 및 시각 검증
- T2 generator 구현
- T3 runtime parity 검증
- release 또는 deployment readiness
- 새로운 범용 workflow·승인·봉인 플랫폼
- 별도의 D6 전용 lifecycle 체계
- 추가 reviewer 체계나 review artifact

---

## 4. 실행 원칙

### 4.1 기존 T1 lifecycle 재사용

D6는 이미 구현된 T1 candidate와 finalizer의 상태 모델을 그대로 사용한다.

Candidate 단계:

```text
contract_and_audit_axis = partial
formal_closeout_state = implemented_only
```

Canonical gate와 finalizer 성공 후:

```text
contract_and_audit_axis = complete
formal_closeout_state = complete
```

Candidate receipt 안에서 `T2_FULL_DATA_PROGRESSION = OPEN`이 계산될 수 있지만, 이것은 그 candidate subject의 감사 결과다. current ecosystem의 formal 완료나 production 채택을 뜻하지 않는다.

새 progression 이름이나 별도의 채택 lifecycle 상태를 만들지 않는다.

### 4.2 기존 finalizer 재사용

현재 `tooltip_t1`의 candidate closeout과 post-gate finalizer를 재사용한다.

필요한 기능이 부족한 경우 기존 finalizer에 다음 확인만 최소 추가한다.

- candidate blocker count가 `0`인지
- candidate handoff input 및 manifest hash가 일치하는지
- candidate와 Run A/Run B/comparator의 subject가 동일한지
- Run A/Run B가 exit `0`/PASS인지
- comparator가 exit `0`이고 canonical result가 동일한지

별도의 D6 finalizer, 별도의 eligibility 판정기, 별도의 adoption 명령은 만들지 않는다.

### 4.3 owner approval 처리

계획 또는 기존 authority가 요구하는 작업 owner approval은 사용자의 실행 프롬프트에 포함된 사전 승인으로 충족한다.

별도 승인 증빙 파일이나 승인 receipt를 생성하지 않는다. 플랫폼 자체가 요구하는 보안·권한 확인은 이 규칙의 대상이 아니다.

### 4.4 하나의 machine subject

다음 결과는 모두 하나의 exact machine subject에 결속되어야 한다.

- fresh D2 relation
- whole-T1 correction ledger
- progression 판정
- candidate T2 handoff
- candidate run receipt
- installed CLI 결과
- canonical Run A/Run B
- comparator
- finalizer closeout

최종 문서나 current route 기록만을 위한 additive successor commit이 필요한 경우, 이 successor는 검증된 machine subject와 final artifact hash를 가리켜야 한다. successor 자체를 새로운 machine validation subject로 재해석하거나 기존 결과를 재결속하지 않는다.

### 4.5 strict absence/presence

- blocker가 하나라도 남으면 production handoff 파일은 `0`개여야 한다.
- blocker가 `0`일 때만 handoff input과 manifest를 생성한다.
- candidate output은 repository 밖의 새 empty root에 생성한다.
- final production output도 repository 밖의 새 empty root에 생성한다.
- 기존 final root를 덮어쓰지 않는다.

---

## 5. 데이터 및 감사 불변식

### 5.1 support

- exact FullType 기준 2,280개여야 한다.
- case-sensitive identity를 보존한다.
- `Base.LemonGrass`와 `Base.Lemongrass`를 서로 다른 exact identity로 유지한다.
- normalized collision 관측 사실을 삭제하지 않는다.
- 해당 collision을 T2 blocker로 다시 만들지 않는다.

### 5.2 Layer 2

- applicable 1,406개는 D1 owner output과 D2 actual Menu consumer relation이 exact identity로 일치해야 한다.
- display-silence 874개는 `not_applicable`이어야 한다.
- display-silence를 correction이나 추론된 분류로 되돌리지 않는다.
- Menu 문자열에서 identity를 역추론하지 않는다.
- Tooltip projection이 자기 fact ID를 Menu evidence로 기입하지 않는다.

### 5.3 Layer 3

- 기존 DVF fact 1,314개를 유지한다.
- D3의 legitimate absence 175개를 유지한다.
- 나머지 non-applicable 범위를 기존 계약대로 유지한다.
- 독립 Menu consumer evidence가 없는 selected Layer 3 행은 `unverified_without_independent_consumer_evidence`로 보존한다.
- 이 unverified 범위를 `verified`로 승격하지 않는다.
- 계약상 T3 재검증 대상인 unverified 상태를 T2 blocker로 다시 분류하지 않는다.

### 5.4 Layer 4

- deterministic identity-first selection 결과를 유지한다.
- Recipe와 right-click source를 독립·동등 source로 유지한다.
- locale readiness 때문에 identity를 재선택하지 않는다.
- fallback, source substitution, locale-dependent reselection을 금지한다.
- D4에서 완성한 Recipe KO/EN surface를 exact selected identity에만 연결한다.

### 5.5 correction과 progression

다음 값들은 정확히 동일한 `t2_blocking=true` filtered correction 집합에서 계산해야 한다.

- correction ledger의 blocker count
- owner별 blocker count
- reason별 blocker count
- `upstream_blocker_count`
- `contract_blocker_count`
- `T2_FULL_DATA_PROGRESSION`
- handoff 생성 가능 여부

Unknown owner/reason, unclassified readiness, raw inference, fallback, source mutation, duplicate exact FullType은 모두 `0`이어야 한다.

---

## 6. strict T2 handoff 계약

### 6.1 기존 row schema 유지

기존 `tooltip_t2_handoff.schema.json`과 기존 `build_handoff_row` 경로를 우선 재사용한다.

Handoff row에 감사용 metadata나 새 lifecycle 필드를 추가하지 않는다. T2가 소비하는 확정 입력만 포함한다.

각 row의 `subject_binding_ref`가 `subject_binding.json`을 가리키므로 candidate와 final output root에는 반드시 이 파일이 실제로 존재해야 한다.

### 6.2 행 구성

각 exact FullType은 기존 contract가 허용하는 다음 정보만 전달한다.

- exact FullType
- Layer 2 applicable인 경우 승인된 category/subcategory identity와 KO/EN surface
- Layer 3 fact가 있는 경우 승인된 fact identity와 KO/EN surface
- Layer 3 legitimate absence인 경우 승인된 absence disposition
- Layer 4 selected identity와 승인된 KO/EN surface
- source identity와 순서 정보
- exact machine subject binding reference

새 문장, 요약, 추천, 중요도, 빈도, 효율, 우선순위를 생성하지 않는다.

### 6.3 manifest 최소 필드

기존 contract만으로 manifest 검증이 불가능한 경우에만 handoff manifest schema를 하나 추가하거나 기존 schema를 최소 확장한다.

필수 정보는 다음으로 제한한다.

```text
schema_version
subject.commit
subject.tree
support_count
support_sha256
handoff_row_count
handoff_fulltype_sha256
handoff_input_sha256
authority_contract_bundle_sha256
candidate_run_receipt_sha256
```

Canonical Run A/Run B/comparator receipt는 final closeout에서 결속한다. 이를 handoff manifest에 중복 기록하기 위해 candidate manifest를 다시 쓰지 않는다.

### 6.4 candidate와 final bytes

- candidate `subject_binding.json`과 final `subject_binding.json`은 byte-identical이어야 한다.
- candidate `t2_handoff_input.jsonl`과 final input은 byte-identical이어야 한다.
- candidate manifest와 final manifest는 동일 machine claim을 나타내며 byte-identical하게 유지한다.
- final gate 결과는 별도 final closeout에 기록한다.

---

## 7. 구현 단계

### Change 0 — clean admission과 계보 확인

1. exact direct parent에서 isolated worktree를 만든다.
2. commit/tree와 working tree clean 상태를 확인한다.
3. D1~D5 및 D2 implementation commit이 ancestry에 포함되는지 확인한다.
4. 접근 가능한 active integration bundle은 각 bundle당 한 번만 다음을 확인한다.
   - manifest/receipt hash
   - common predecessor 또는 implementation subject
   - support count/hash
   - protected/global-current mutation claim
5. 과거 patch를 다시 적용하지 않는다.
6. admission 결과는 candidate run receipt에 기록하고 별도 admission proof bundle을 만들지 않는다.

Admission이 실패하면 repository를 수정하지 않고 정확한 불일치를 보고한다.

### Change 1 — current contract/route의 최소 통합

1. D1~D5와 D2 결과가 현재 authority manifest 및 route에서 같은 contract bundle로 해석되는지 확인한다.
2. 누락된 현재 경로가 있을 때만 기존 manifest/route를 additive하게 갱신한다.
3. 기존 P-1~P-12 decision identity를 유지한다.
4. workstream-specific historical binding은 역사적 증거로 남기되 current claim과 혼동하지 않는다.
5. 새 semantic authority나 D6 전용 정책 namespace를 만들지 않는다.

### Change 2 — same-subject D2 relation 재생성

1. D6 exact subject에서 기존 D2 materializer route를 실행한다.
2. actual Browser consumer tuple과 D1 expected tuple을 exact FullType으로 join한다.
3. 다음 결과를 요구한다.

```text
support = 2,280
verified = 1,406
not_applicable = 874
correction_required = 0
owner_output_self_comparison = 0
```

4. bounded Browser delta는 D2에서 승인된 범위와 일치해야 한다.
5. 불일치 시 fresh 결과를 우선하며 correction을 숨기지 않는다.

### Change 3 — whole-universe 재감사

1. 동일 subject에서 Tooltip T1 audit을 실행한다.
2. support 2,280개 전부에 Layer 2/3/4 상태를 부여한다.
3. correction ledger와 owner/reason 집계를 생성한다.
4. Layer 3 unverified와 T2 blocker를 분리한다.
5. D1~D5에서 닫힌 correction이 재발하지 않았는지 확인한다.
6. blocker가 남으면 다음 상태로 종료한다.

```text
T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS
production_t2_handoff = absent
contract_and_audit_axis = partial
formal_closeout_state = implemented_only
```

이 경우 handoff input/manifest/subject binding을 생성하지 않는다.

### Change 4 — candidate strict handoff 생성

Blocker가 정확히 `0`일 때만 다음을 수행한다.

1. 기존 row builder로 2,280개의 handoff row를 생성한다.
2. 빈 slot은 압축하되 slot 순서와 source identity를 변경하지 않는다.
3. FullType exact set이 support universe와 동일한지 확인한다.
4. duplicate/missing/extra FullType이 모두 `0`인지 확인한다.
5. 새 empty candidate root에 다음을 쓴다.

```text
subject_binding.json
t2_handoff_input.jsonl
t2_handoff_manifest.json
run_receipt.json
```

6. candidate closeout은 기존 상태를 유지한다.

```text
contract_and_audit_axis = partial
formal_closeout_state = implemented_only
T2_FULL_DATA_PROGRESSION = OPEN
```

Candidate에서 formal complete 또는 current production adoption을 주장하지 않는다.

### Change 5 — exact implementation subject 확정

1. 코드·contract·route 변경을 하나의 clean implementation subject로 확정한다.
2. candidate를 그 exact subject에서 다시 생성한다.
3. subject binding, audit, handoff, receipt가 모두 동일 commit/tree를 가리키는지 확인한다.
4. 문서-only 변경은 machine subject 확정 전에 불필요하게 섞지 않는다.

### Change 6 — fresh wheel과 installed environment

1. exact implementation subject에서 fresh wheel을 한 번 build한다.
2. 새 empty environment에 한 번 install한다.
3. installed `iris-tooling inspect current`를 실행한다.
4. installed CLI로 same-subject D2 relation과 Tooltip T1 candidate를 생성·검증한다.
5. 기존 environment authority 계약이 요구하는 receipt와 current locator만 갱신한다.
6. 별도의 D6 environment authority 체계를 만들지 않는다.

### Change 7 — canonical Run A/Run B/comparator

1. 동일 exact implementation subject에서 기존 canonical full gate Run A를 실행한다.
2. 같은 subject와 별도 empty output root에서 Run B를 실행한다.
3. 두 실행 모두 exit `0`/PASS여야 한다.
4. 기존 deterministic comparator를 실행한다.
5. comparator exit `0`과 canonical result equality를 요구한다.
6. 실패한 receipt를 성공으로 재해석하거나 덮어쓰지 않는다.

### Change 8 — post-gate finalizer와 final production root

기존 finalizer를 사용해 다음을 확인한다.

- candidate artifact 및 receipt hash
- blocker `0`
- candidate progression `OPEN`
- handoff input/manifest/subject binding의 strict consistency
- exact subject equality
- Run A/Run B exit `0`/PASS
- comparator exit `0`과 canonical equality

모든 조건이 충족되면 새 empty final root에 다음 네 파일을 기록한다.

```text
subject_binding.json
t2_handoff_input.jsonl
t2_handoff_manifest.json
axis_separated_final_closeout_record.json
```

Final closeout은 다음을 기록한다.

```text
contract_and_audit_axis = complete
formal_closeout_state = complete
T2_FULL_DATA_PROGRESSION = OPEN
production_t2_handoff = present
```

Finalizer 실패 시 final production root를 current로 채택하지 않는다.

### Change 9 — current 채택과 문서 갱신

1. finalizer 성공 후에만 기존 current authority manifest와 route가 검증된 machine subject 및 final root를 가리키게 한다.
2. `ENTRYPOINTS.md`에는 기존 CLI의 실제 경로만 기록한다.
3. `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`에는 T1-D6 최종 결과와 validation ceiling을 additive하게 기록한다.
4. 문서/current-route carrier commit이 필요한 경우 machine subject와 final artifact hash를 명시한다.
5. carrier commit은 handoff row나 audit 결과를 다시 생성하지 않는다.
6. current readback을 한 번 수행해 route, subject, hashes, final state를 확인한다.

---

## 8. 예상 변경 경로

실제 결손이 있을 때만 수정한다. 아래 목록 전체를 반드시 변경해야 한다는 뜻은 아니다.

### 8.1 Tooltip T1 tooling

```text
Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py
Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py
Iris/tooling/src/iris_tooling/domains/tooltip_t1/cli.py
Iris/tooling/src/iris_tooling/domains/tooltip_t1/models.py
```

- 기존 candidate/finalizer로 요구사항을 충족하면 변경하지 않는다.
- 새 모듈은 기존 파일에 기능을 넣을 경우 책임이 명확히 훼손될 때만 하나까지 허용한다.
- 동일 검증을 수행하는 독립 validator를 추가하지 않는다.

### 8.2 Authority/contract

```text
Iris/_docs/authority/tooltip_t1/tooltip_t2_handoff.schema.json
Iris/_docs/authority/tooltip_t1/<handoff manifest schema if strictly required>
Iris/_docs/authority/iris_current_authority_manifest.json
Iris/_docs/authority/iris_current_route_index.json
```

- row schema는 기존 것을 우선 유지한다.
- manifest schema가 이미 존재하면 새 파일을 만들지 않는다.
- authority bundle은 필요한 변경 후 한 번만 rebind한다.

### 8.3 Tests

```text
Iris/tooling/tests/test_tooltip_t1_contract.py
Iris/tooling/tests/test_tooltip_t1_projection.py
Iris/tooling/tests/test_tooltip_t1_audit.py
```

새 테스트 파일과 새 top-level test function은 만들지 않는다.

### 8.4 문서

```text
Iris/build/ENTRYPOINTS.md
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
docs/iris_tooltip_t1_d6_integrated_current_adoption_final_reaudit_strict_production_t2_handoff_opening_plan.md
```

### 8.5 보호 경로

D6에서 다음 runtime 경로는 읽기 전용이다.

```text
Iris/media/lua/**
```

Unexpected mutation이 있으면 원인을 해결하기 전에는 closeout하지 않는다.

---

## 9. 최소 artifact 집합

### 9.1 Candidate

기존 materializer가 생성하는 audit/ledger를 중복 복제하지 않는다. Candidate root의 필수 결과는 다음뿐이다.

```text
subject_binding.json
t2_handoff_input.jsonl
t2_handoff_manifest.json
run_receipt.json
```

Correction ledger가 기존 run receipt 또는 기존 candidate artifact에 이미 포함되면 별도 census/proof 파일을 추가하지 않는다.

### 9.2 Canonical validation

기존 gate가 요구하는 다음 receipt만 보존한다.

```text
Run A orchestration/result receipt
Run B orchestration/result receipt
deterministic comparator receipt
```

### 9.3 Final production

```text
subject_binding.json
t2_handoff_input.jsonl
t2_handoff_manifest.json
axis_separated_final_closeout_record.json
```

### 9.4 만들지 않는 artifact

- 별도 admission inventory
- 별도 lifecycle contract
- 별도 eligibility receipt
- 별도 adoption receipt
- 별도 승인 증빙 파일
- 중복 correction census
- 중복 protected-path proof bundle
- validation-of-validation report
- 임시 스크립트를 canonical validator로 승격한 artifact

---

## 10. 테스트 및 검증 계획

### 10.1 테스트 추가 예산

```text
new test files = 0
new top-level test functions = 0
new parameterized rows across the three focused files <= 4
new standalone validator = 0
```

기존 parameterized family에 필요한 경우에만 다음 의미를 합계 최대 4행으로 통합한다.

1. exact subject 또는 no-reapply binding 불일치 거부
2. blocker `> 0`이면 handoff strict absence
3. blocker `= 0`이면 2,280-row handoff 생성
4. handoff exact-set/subject/hash 불일치 거부

기존 행이 이미 같은 불변식을 검증하면 새 행을 추가하지 않는다.

### 10.2 필수 focused test

구현이 끝나고 clean exact subject가 확정된 뒤, 다음 명령을 한 번 실행한다.

```powershell
uv run --project .\Iris\tooling python -B -m pytest `
  .\Iris\tooling\tests\test_tooltip_t1_contract.py `
  .\Iris\tooling\tests\test_tooltip_t1_projection.py `
  .\Iris\tooling\tests\test_tooltip_t1_audit.py `
  -q
```

- 중간 개발 단계에서 같은 suite를 반복 실행하지 않는다.
- exact-subject clean guard 때문에 commit 전 실패할 것이 명백한 시점에는 실행하지 않는다.
- 실패 후 코드를 수정했다면 필요한 실패 범위만 재확인하고, 최종 clean subject에서 focused command를 다시 한 번 통과시킨다.

### 10.3 필수 실행 검증

Focused test와 별개로 실제 success condition에 필요한 다음 검증은 수행한다.

1. fresh wheel build: 1회
2. fresh environment install: 1회
3. installed `inspect current`: 1회
4. installed CLI의 fresh D2 relation + whole-T1 audit/handoff: 1회
5. canonical Run A: 1회
6. canonical Run B: 1회
7. deterministic comparator: 1회
8. post-gate finalizer: 1회
9. final current readback: 1회
10. `git diff --check`: 최종 변경 기준 1회

Run A/Run B는 determinism 요구 때문에 줄일 수 없다. 이 둘이 repository 전체 gate를 이미 포함한다면 같은 목적의 추가 full suite를 실행하지 않는다.

### 10.4 조건부 검증

- Lua syntax 검사는 Lua 파일이 실제로 변경된 경우에만 실행한다.
- Browser owner harness는 Browser Lua 또는 그 harness가 실제로 변경된 경우에만 실행한다.
- D6 계획상 Lua runtime은 read-only이므로 정상적인 실행에서는 둘 다 생략한다.
- 문서만 수정한 후에는 코드 test를 다시 실행하지 않는다.

### 10.5 금지 사항

- 계획에 없는 전체 test suite 추가 실행
- 같은 focused suite의 confidence 목적 반복
- 대규모 negative test matrix
- 새 test file 또는 새 top-level test function
- 테스트를 위한 production API 확장
- 임시 검사 스크립트의 canonical 채택
- gate 결과를 다시 검증하는 별도 validator

장기 실행 중에는 상태를 주기적으로 확인한다. 무한 루프나 비정상 장기 실행 징후가 있으면 중단하고 원인을 조사한다.

---

## 11. 완료 불변식

### 11.1 Subject와 support

```text
all machine artifacts share one commit/tree
support_count = 2,280
support_sha256 = 3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6
duplicate_fulltype = 0
missing_fulltype = 0
extra_fulltype = 0
```

### 11.2 Layer 2 relation

```text
verified = 1,406
not_applicable = 874
correction_required = 0
owner_output_self_comparison = 0
```

### 11.3 Correction

```text
t2_blocking_correction_total = 0
upstream_blocker_count = 0
contract_blocker_count = 0
owner_blocker_sum = 0
unknown_owner = 0
unknown_reason = 0
raw_inference = 0
fallback = 0
source_mutation = 0
locale_dependent_reselection = 0
```

### 11.4 Handoff

```text
handoff_row_count = 2,280
handoff_exact_fulltype_set = support_exact_fulltype_set
subject_binding file present = true
candidate/final subject binding bytes equal = true
candidate/final input bytes equal = true
candidate/final manifest bytes equal = true
```

### 11.5 Lifecycle

Candidate:

```text
contract_and_audit_axis = partial
formal_closeout_state = implemented_only
T2_FULL_DATA_PROGRESSION = OPEN
```

Final:

```text
contract_and_audit_axis = complete
formal_closeout_state = complete
T2_FULL_DATA_PROGRESSION = OPEN
production_t2_handoff = present
```

---

## 12. 실패 및 종료 상태

### 12.1 Admission 실패

- repository mutation 없음
- handoff 없음
- 불일치한 subject, ancestry 또는 required input을 보고

### 12.2 Blocker 잔존

```text
contract_and_audit_axis = partial
formal_closeout_state = implemented_only
T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS
production_t2_handoff = absent
```

Owner별 correction을 정확히 보고하고 T2 handoff를 만들지 않는다.

### 12.3 Candidate 성공, canonical 미완료

```text
contract_and_audit_axis = partial
formal_closeout_state = implemented_only
T2_FULL_DATA_PROGRESSION = OPEN on candidate subject only
production_t2_handoff = absent from current
```

Candidate artifact는 보존할 수 있지만 current production으로 채택하지 않는다.

### 12.4 Canonical 또는 finalizer 실패

- 성공 closeout을 쓰지 않는다.
- current route를 production handoff로 전환하지 않는다.
- 실패 receipt를 덮어쓰지 않는다.
- 실패 원인에 필요한 범위만 수정한 뒤 동일 success path를 재실행한다.

### 12.5 Complete

Complete는 blocker `0`, strict handoff, installed validation, Run A/Run B, comparator, finalizer, final readback이 모두 성공한 경우에만 선언한다.

---

## 13. Validation ceiling

최종 closeout은 다음 세 범주를 기존 형식으로 기록한다.

### validated

- exact machine subject binding
- 2,280 support universe
- D2 Layer 2 consumer relation
- Layer 2/3/4 Tooltip T1 readiness contract
- T2-blocking correction `0`
- strict 2,280-row handoff
- fresh wheel/installed CLI
- canonical Run A/Run B/comparator
- finalizer와 current readback

### unvalidated_but_in_scope

성공적인 T1-D6 closeout에서는 비어 있어야 한다. 필수 검증이 남아 있으면 complete를 주장하지 않는다.

### out_of_scope

- Tooltip static Lua generation
- `IrisAltTooltip` runtime behavior
- PZ 실제 화면과 Alt 입력
- 최종 runtime Menu/Tooltip parity
- T2/T3 구현
- release/deployment readiness

---

## 14. Rollback 원칙

- D1~D5 owner 결과를 되돌리지 않는다.
- Candidate 또는 gate 실패 시 current production route를 변경하지 않는다.
- Final production root는 create-new 방식으로 만들고 기존 성공 root를 덮어쓰지 않는다.
- 문서/current carrier 오류는 machine artifact를 재생성하지 않고 reference만 바로잡는다.
- machine input, code, contract 또는 authority bundle이 바뀐 경우에만 machine subject를 새로 만들고 필요한 validation path를 다시 실행한다.

---

## 15. 최종 보고 형식

최종 보고는 중복 proof 목록을 늘리지 않고 다음만 명확히 제시한다.

1. exact machine commit/tree
2. support count/hash
3. Layer 2 relation 분포
4. correction 및 owner blocker 합계
5. handoff row count와 input/manifest hash
6. focused test 결과
7. wheel/install/installed CLI 결과
8. Run A/Run B/comparator/finalizer exit 상태
9. final root와 closeout hash
10. current readback 결과
11. validation ceiling과 non-claims

---

## 16. 최종 완료 판정

다음 조건을 모두 만족하면 T1-D6를 완료한다.

- D1~D5와 D2 결과가 하나의 exact subject에 포함되어 있다.
- support universe는 exact 2,280개다.
- T2-blocking correction과 owner blocker 합계가 모두 `0`이다.
- strict T2 handoff는 exact 2,280행이며 `subject_binding.json`을 포함한다.
- candidate는 formal complete를 주장하지 않는다.
- fresh installed validation이 exit `0`이다.
- canonical Run A/Run B와 comparator가 모두 exit `0`이다.
- 기존 post-gate finalizer가 exit `0`이다.
- final production root의 네 필수 파일이 존재하고 서로 일관된다.
- current readback이 검증된 machine subject와 final hashes를 반환한다.
- 최종 closeout은 `complete / complete / OPEN / present`를 기록한다.

이 완료는 Tooltip T1 upstream input과 T2 handoff 경계의 완료만 뜻한다. Tooltip static Lua, runtime, 시각 검증, T2/T3 구현 및 release readiness를 포함하지 않는다.
