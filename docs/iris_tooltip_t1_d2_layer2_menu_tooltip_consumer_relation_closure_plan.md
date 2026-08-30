# Iris Tooltip T1-D2 Layer 2 Menu / Tooltip Consumer Relation Closure Implementation Plan

> 상태: planned / implementation not started
> 작성일: 2026-08-29
> 기준 로드맵: `ROADMAP — Iris Tooltip T1-D2: Layer 2 Menu / Tooltip Consumer Relation Closure`
> 검증 깊이: focused — actual Lua consumer 전수 비교, bounded Browser correction, relation-driven T1 audit, minimal D6 bundle
> direct execution parent: commit `cb27591e3c6ef40a1b1f08a6e2ceee7047132cf8`, tree `b23103ace037aa62fc1e24d04901d534de5cc2e8`
> upstream input: validated T1-D1 Layer 2 partition and integrated T1-D3/D4/D5 state
> downstream consumer: T1-D6 global integration; actual PZ runtime verification remains T3-owned

이 계획은 Layer 2 분류를 새로 만들거나 Tooltip runtime을 구현하는 계획이 아니다. T1-D1이 확정한 Layer 2 결과와 실제 Iris Browser consumer가 같은 분류 identity를 사용하도록 결속하고, 그 관계를 기존 Tooltip T1 audit이 소비하게 만드는 작업이다.

핵심 결과는 다음 두 집합으로 제한한다.

```text
Layer 2 applicable       1,406 -> Menu/Tooltip relation verified
Layer 2 display silence    874 -> Tooltip S1 absent, parity not_applicable
support total            2,280
```

`874`의 Menu browsing membership은 삭제하거나 숨기지 않는다. 이 항목들은 Tooltip Layer 2를 표시하지 않는 항목일 뿐 Menu에서 사용할 수 없는 항목이 아니다.

---

## 1. Objective

T1-D1의 exact partition을 변경하지 않고 다음 관계를 확립한다.

```text
D1 Classification owner output
├─ applicable 1,406
│  ├─ exact FullType
│  ├─ category identity
│  ├─ primary subcategory identity
│  ├─ category/subcategory locale key and source
│  ├─ actual Iris Browser consumer tuple
│  └─ Tooltip S1 tuple
└─ display silence 874
   ├─ Tooltip S1 absent
   ├─ placeholder absent
   └─ Layer 2 Menu parity not_applicable
```

성공한 D2 candidate의 terminal distribution은 다음과 같다.

```text
verified            = exact D1 applicable set
not_applicable      = exact D1 display-silence set
correction_required = 0
```

`verified`는 D1 owner output을 Menu evidence로 자기대조해 만들지 않는다. 실제 Lua Browser projection이 산출한 consumer tuple과 D1 expected tuple을 exact FullType 기준으로 비교한다.

---

## 2. Inputs and Frozen Boundaries

### Exact execution subject

- commit `cb27591e3c6ef40a1b1f08a6e2ceee7047132cf8`
- tree `b23103ace037aa62fc1e24d04901d534de5cc2e8`
- D1, D3, D4, D5가 통합된 clean isolated subject

### D1 partition

```text
support count/hash:
2,280 / 3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6

layer2_applicable count/hash:
1,406 / c5a77d86eb875cecf03edf5ab67f29361f58947bd97493e522667b593130f264

layer2_display_silence count/hash:
874 / d13fa6ac9072a3ab2c61bc59990bfb948010ce8b2fc3211aa1ecb7b5c6c121de
```

Execution에서는 위 숫자를 출력에 강제로 맞추지 않는다. Direct parent의 D1 owner output에서 exact case-sensitive set을 다시 읽고 count/hash/disjoint union을 확인한다. 불일치하면 mutation 전에 중단한다.

### Protected state

- D1 semantic classification rows and display-silence partition
- D3 fact/legitimate-absence results
- D4 selected Recipe identity and locale results
- D5 exact case-sensitive FullType disposition
- Layer 3/4 parity distribution and all non-D2 correction rows
- global current manifest, route index, environment locator and canonical finalizer wiring

D2는 위 대상을 수정하지 않는다.

### Declared-byte admission rule

Git commit/tree는 source identity를 소유하지만, 기존 D1/D4 validator input은 일부 text 파일의 physical SHA-256을 혼합된 LF/CRLF bytes로 봉인하고 있다. 따라서 모든 파일을 LF 또는 CRLF 하나로 강제하지 않는다.

```text
declared SHA-256 == current working bytes
-> 그대로 사용

declared SHA-256 == same Git blob text의 LF 또는 CRLF serialization
-> 해당 파일의 line ending만 declared bytes로 materialize
-> normalized Git content delta 0 확인
-> 계속 진행

declared SHA-256가 current/LF/CRLF 어느 것과도 일치하지 않음
-> semantic/content mismatch로 blocked
```

이 materialization은 isolated execution checkout의 물리 표현 준비일 뿐 repository source, Git tree, registry hash 또는 semantic authority 변경이 아니다. D2 commit/shared delta에 포함하지 않으며, registry 값을 current checkout에 맞춰 다시 쓰지 않는다.

---

## 3. Scope

### Included

- exact parent and declared-byte-compatible subject admission
- D1 support/applicable/display-silence partition reconciliation
- actual Browser classification consumer route 확인
- actual Lua Browser projection의 applicable 1,406 tuple 전수 추출
- D1 expected tuple과 actual Lua consumer tuple의 exact comparison
- evidence가 확인한 explicit-primary navigation mismatch의 bounded correction
- applicable `verified`, display-silence `not_applicable` relation materialization
- existing Tooltip T1 audit의 unconditional Layer 2 correction을 relation-driven disposition으로 교체
- affected-range/non-target invariance 확인
- common execution contract가 요구하는 deterministic candidate A/B와 minimal D6 bundle

### Read-only non-consumer confirmation

현재 Browser Detail과 Wiki의 raw tags 또는 PZ engine category/subcategory는 D1 Layer 2 category/primary template consumer가 아니다. 구현자는 실제 direct caller를 한 번 확인하고 D2 denominator에서 제외한다.

이 확인을 위해 별도 route census 시스템, caller inventory, lifecycle artifact 또는 Detail/Wiki downstream 구현 과제를 만들지 않는다. Direct parent에서 별도의 D1 Layer 2 consumer가 실제로 발견된 경우에만 그 사실과 근거를 보고하고, D2 scope를 임의 확대하지 않은 채 `blocked` 또는 재계획 대상으로 남긴다.

### Explicitly out of scope

- D1 applicability, category, membership, primary 또는 locale 의미 재판정
- 새 분류 row, 번역 surface, placeholder 또는 positive semantic absence 생성
- `Misc.9-A`, DisplayName, FullType 이름 또는 rendered text 기반 추론
- display-silence `874`의 Menu membership 제거
- Detail/Wiki Layer 2 renderer 또는 template route 신설
- Menu layout, wording, 번역 문장 또는 public API shape 변경
- Layer 3/4 correction 또는 parity disposition 변경
- Tooltip static Lua emit, Alt Tooltip assembly 또는 runtime renderer 구현
- global current adoption, canonical full-gate/finalizer 또는 production T2 handoff
- actual PZ runtime/visual acceptance, release 또는 deployment 판정

---

## 4. Consumer Relation Rules

### Expected tuple

D1 owner output에서 다음 값만 읽는다.

```text
exact FullType
classification identity
category identity
primary subcategory identity
category label key and KO/EN source ref
subcategory label key and KO/EN source ref
classification authority/provenance ref
```

### Observed tuple

Observed side는 실제 repository Lua path가 산출한다.

```text
IrisClassifications.lua
-> StaticData.get("classifications")
-> IrisBrowserProjectionBuilder.build
-> Browser row
   - accepted memberships
   - primaryLocation.category/subcategory
   - primaryTag
-> IrisBrowserCategoryIndex
   - category label key
   - subcategory label key
```

Python은 Lua의 presentation rank, tie-break, override 또는 label-key 선택 알고리즘을 재구현하지 않는다. Python tooling은 다음 역할만 맡는다.

- D1 expected rows 읽기
- actual Lua output parsing
- exact-set join/comparison
- relation record 작성
- audit input과 invariant validation

### Full-set observation

Representative sample을 전체 relation의 근거로 사용하지 않는다. Existing Lua harness 또는 같은 production module-loading 경로를 최소 확장하여 actual Browser projection을 실행하고 applicable 1,406개 전부의 canonical tuple을 출력한다.

출력에는 timestamp, machine path, run ID 또는 elapsed time을 포함하지 않는다. FullType은 case-sensitive하게 유지하며 normalized identity join을 사용하지 않는다.

### Relation lifecycle

각 support FullType은 정확히 하나의 상태만 갖는다.

```text
applicable + exact relation match    -> verified
display-silence exact member         -> not_applicable
applicable + missing/mismatch route  -> correction_required
```

`not_applicable`은 `verified`로 계산하지 않는다. `correction_required`를 `unverified`로 완화하지 않는다.

---

## 5. Bounded Browser Correction

Current code에서 `primaryLocation`은 presentation rank를 사용하고 `primaryTag`는 `IrisPrimarySubcategory` override를 사용한다. Planning-time 비교에서는 applicable 1,406개 중 explicit primary가 있는 multi-membership 26개에서 두 선택이 달랐다.

실행에서는 26을 고정값으로 사용하지 않고 actual Lua full-set result로 exact mismatch set을 다시 구한다.

### Allowed correction

모든 mismatch가 다음 predicate를 만족할 때만 Browser projection을 수정한다.

```text
D1 explicit primary exists
AND explicit primary is a well-formed exact tag
AND explicit primary is an accepted current membership
AND primaryTag already selects that exact primary
AND primaryLocation differs only because presentation rank selected another membership
```

수정 규칙은 exact FullType 목록을 하드코딩하지 않는다.

```text
accepted explicit primary exists
-> primaryTag and primaryLocation use the same exact primary

no explicit primary exists
-> preserve existing presentation-rank behavior
```

### Fail-loud conditions

- explicit primary is malformed
- explicit primary is not an accepted membership
- navigation category mismatch exists
- label-key/source mismatch exists
- membership bucket is missing
- mismatch requires semantic classification or locale change

위 경우 fallback, raw tag inference 또는 partial relation 발행을 하지 않는다.

### Required invariants

- all existing membership buckets preserved
- display-silence Menu behavior delta `0`
- public Browser facade/result shape unchanged
- `CategoryPresentationOrder` remains presentation-only
- `Base.LemonGrass` and `Base.Lemongrass` remain distinct
- no normalized-key join

---

## 6. Planned Changes

### Change 1 — Admit the exact subject

- hash-bound input을 declared-byte-compatible하게 materialize한 isolated checkout 구성
- commit/tree exact match 확인
- D1 partition count/hash/disjoint union 확인
- current Tooltip T1 audit baseline 생성
- Layer 2 Menu correction exact set이 support exact set인지 확인
- D3/D4/D5와 non-D2 correction/parity baseline을 minimal hash/set metrics로 고정

Admission failure에서는 repository를 수정하지 않는다.

### Change 2 — Observe the actual Browser relation

- actual production Lua modules를 사용하는 existing harness path 확장
- Browser projection 전체를 한 번 build
- applicable 1,406개 actual tuple 전수 출력
- D1 expected와 exact comparison
- mismatch를 membership, navigation primary, display primary, label-key/source로 구분

별도 Python model, representative fidelity sample, Browser/Detail/Wiki census CLI를 만들지 않는다.

### Change 3 — Apply the minimum Browser alignment

Actual mismatch가 bounded predicate에 전부 해당할 때만 `IrisBrowserProjectionBuilder.lua`를 수정한다.

- accepted explicit primary를 `primaryTag`와 `primaryLocation`이 함께 사용
- explicit primary가 없는 row의 기존 behavior 유지
- invalid override fail-loud
- memberships, locale data and API shape unchanged

### Change 4 — Materialize the relation and update the audit

하나의 D2 relation materializer가 다음을 생성한다.

```text
verified exact set
not_applicable exact set
correction_required exact set
bounded mismatch/disposition metadata
actual Lua consumer source refs
D1 expected refs
```

Existing audit는 relation을 입력으로 받아 다음처럼 동작한다.

- applicable verified: `PARITY_AUTHORITY_RELATION_MISSING` 미발행
- display-silence: Layer 2 parity `not_applicable`
- applicable missing/mismatch: Menu consumer correction 발행
- Layer 3/4 parity logic unchanged
- `menu_owner_output_self_comparison=0`

새 evidence status enum이나 별도 semantic authority를 만들지 않는다.

### Change 5 — Run final minimal validation

구현 중간에는 계획에 없는 테스트를 실행하지 않는다. Admission에 필요한 read-only 검사 이후, 테스트와 materialization은 구현이 끝난 마지막 단계에 몰아서 실행한다.

Required final validation은 §8에 명시한 범위로 제한한다.

### Change 6 — Emit the minimal D6 bundle

Common execution contract가 요구하는 envelope를 하나의 integration manifest에 합친다.

```text
schema_version
workstream_id = T1-D2
terminal_state
direct_parent_commit/tree
final_subject_commit/tree
D1 support/applicable/silence identities
starting/remaining correction distribution
verified/not_applicable/correction exact-set identities
bounded Browser delta exact-set identity
owner/evidence refs
artifact hashes
shared_path_delta
protected/non-target invariance
validation receipts
claim ceiling
integration instructions
```

별도의 subject-admission report, contract-identity report, caller inventory, route census, observer sample, changed-file inventory 또는 validation-ceiling 파일을 만들지 않는다. 필요한 값은 relation output, run receipt 또는 integration manifest에 직접 포함한다.

---

## 7. Repository Areas Affected

### Expected code paths

- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/d2.py` — minimal expected/actual reconciliation and relation materializer
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/cli.py` — one D2 materializer route only
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py` — relation-driven Layer 2 parity
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py` — relation schema/contract validation
- conditional `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserProjectionBuilder.lua`
- `Iris/test/lua/fixtures/tags_public_surface_isolation_harness.lua` — full-set production projection mode and bounded override assertions

### Existing test files only

- `Iris/tooling/tests/test_tooltip_t1_contract.py`
- `Iris/tooling/tests/test_tooltip_t1_projection.py`
- `Iris/tooling/tests/test_tooltip_t1_audit.py`
- one existing Browser Lua harness pytest owner selected during implementation

No new test file or new top-level test function/family is allowed.

### Shared contract proposal

- conditional `Iris/_docs/authority/tooltip_t1/layer2_menu_consumer_relation.schema.json`
- `Iris/_docs/authority/tooltip_t1/layer2_tooltip_input_contract.json`
- `Iris/_docs/authority/tooltip_t1/tooltip_locale_menu_parity_contract.json`

기존 contract로 relation shape를 충분히 검증할 수 있으면 새 schema 파일을 만들지 않는다. 새 schema는 기존 contract로 정확히 표현할 수 없는 최소 row shape가 있을 때만 허용한다. Current route-index registration은 T1-D6 소유다.

### Must remain unchanged

- current authority manifest/route index/environment locator
- `Iris/build/ENTRYPOINTS.md`
- top-level `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`
- Layer 3/4 owner/runtime/static data
- D1 owner output and D5 exact identity disposition

---

## 8. Minimal Validation Budget

### Test identity budget

```text
new test files                  = 0
new top-level test functions   = 0
new standalone validator       = 0
new Tooltip parameter rows     <= 3
new Browser harness scenarios  <= 2
```

Tooltip parameter rows는 가능한 경우 하나의 existing table에서 다음 세 lifecycle만 다룬다.

1. applicable exact match -> `verified`
2. display silence -> `not_applicable`
3. applicable missing/mismatch -> `correction_required`

Browser harness scenarios는 다음 둘로 제한한다.

1. accepted explicit primary aligns `primaryTag` and `primaryLocation` while memberships remain unchanged
2. malformed/non-membership explicit primary fails loud

기존 D5 case-sensitive identity test가 이미 존재하므로 D2 전용 중복 test row를 추가하지 않는다.

### Required final test commands

#### Tooltip T1 focused suite

```powershell
uv run --project .\Iris\tooling python -B -m pytest `
  .\Iris\tooling\tests\test_tooltip_t1_contract.py `
  .\Iris\tooling\tests\test_tooltip_t1_projection.py `
  .\Iris\tooling\tests\test_tooltip_t1_audit.py `
  -q
```

#### Browser Lua harness owner

실제 production projection과 public navigation result를 정직하게 실행할 수 있는 기존 Browser pytest 파일 **하나만** 선택해 실행한다. 우선 기존 `test_iris_tags_public_surface_isolation.py` 안에 필요한 assertions를 통합한다.

그 파일로 `IrisBrowserQuery/getItemLocation` 소비 경로를 실행할 수 없다는 구체적 근거가 있을 때는 기존 `test_iris_browser_state_selection_search_acceptance.py`를 **대신** 선택한다. 두 Browser test 파일을 함께 실행하지 않는다. Detail ViewModel test와 unrelated Browser cache suite도 실행하지 않는다.

### Lua syntax

Lua source 또는 harness가 변경되므로 마지막에 한 번 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Missing required Lua tooling은 skipped PASS가 아니라 `blocked`다.

### Required non-pytest validation

- single D2 relation materializer Run A
- same exact candidate에서 separate empty root Run B
- canonical relation bytes/digest comparator
- candidate whole-T1 audit 한 번
- Layer 2 correction reconciliation and non-D2 invariant comparison
- minimal bundle hash/receipt validation
- `git diff --check`

Common execution contract가 materializer A/B를 요구하므로 두 번 실행한다. 그 외 confidence-only rerun, whole-repository canonical Run A/B, fresh environment authority, global comparator 또는 finalizer는 수행하지 않는다.

### Required machine invariants

```text
support                           = exact D1 frozen set
applicable                        = exact D1 applicable set
display silence                   = exact D1 silence set
applicable intersection silence   = 0
applicable union silence          = support
actual Lua applicable coverage    = applicable exact set
verified                          = applicable exact set
not_applicable                    = silence exact set
remaining Layer 2 correction      = 0
owner-output self-comparison      = 0
rendered-string inference         = 0
normalized-key join               = 0
display-silence Menu delta        = 0
D1/D3/D4/D5 protected delta       = 0
non-D2 correction/parity delta    = 0
D6-exclusive path delta           = 0
```

---

## 9. Generated Artifacts

모든 실행 산출물은 repository-external immutable empty root에 생성한다.

최소 산출물만 허용한다.

```text
run_a/
  layer2_menu_consumer_relation.jsonl
  run_receipt.json

run_b/
  layer2_menu_consumer_relation.jsonl
  run_receipt.json

t1d2_integration_manifest.json
t1d2_bundle_receipt.json
```

Mismatch/disposition, protected metrics, validation ceiling과 shared-path delta는 relation receipt 또는 integration manifest에 포함한다. 별도 proof 파일로 분할하지 않는다.

산출물은 semantic classification source, runtime payload, regular validator authority 또는 mutable current pointer가 아니다.

---

## 10. Terminal States

### Complete

```text
T1-D2 workstream                 = complete
Layer 2 verified                = exact applicable set
Layer 2 not_applicable          = exact display-silence set
Layer 2 correction_required     = 0
current ecosystem adoption      = pending_T1_D6
runtime verification            = pending_T3
production T2 handoff           = absent
```

Required validation이 모두 exit `0`이고 bundle이 hash-valid할 때만 `complete`다.

### Implemented only

Code/relation candidate는 존재하지만 §8 required final validation이 끝나지 않은 상태다.

### Partial

Evidence-bound bounded correction의 일부가 적용되지 않았거나 applicable relation 일부가 남은 상태다.

### Blocked

- declared-byte materialization 뒤에도 protected input hash가 current/LF/CRLF 어느 것과도 일치하지 않는 semantic/content mismatch
- D1 partition mismatch
- actual Browser relation을 full applicable set에서 추출할 수 없음
- mismatch가 bounded Browser correction predicate를 벗어남
- invalid explicit primary override
- required change가 classification/locale semantics 또는 public API를 변경함
- D1/D3/D4/D5 또는 non-D2 correction/parity delta 발생
- required tooling unavailable

---

## 11. Claim Ceiling

Successful D2가 주장하는 것은 다음뿐이다.

- exact D2 final subject에서 static Layer 2 Browser consumer relation이 완성됨
- applicable rows가 D1과 같은 category/primary/locale-source identity를 소비함
- display-silence rows가 placeholder 없이 Layer 2 `not_applicable`로 유지됨
- Layer 2 `PARITY_AUTHORITY_RELATION_MISSING=0`
- D1/D3/D4/D5와 non-D2 state가 보존됨

다음은 주장하지 않는다.

- actual PZ Menu/Tooltip runtime parity PASS
- Tooltip static Lua 또는 Alt Tooltip runtime completion
- T3 acceptance
- T1-D6 completion or global current adoption
- whole-T1 canonical finalizer completion
- `T2_FULL_DATA_PROGRESSION=OPEN`
- production T2 handoff
- release, freeze, Workshop or deployment readiness

---

## 12. Expected Closeout

Planning-time 예상 코드 형태가 exact subject에서도 확인되면 다음 결과가 기대된다.

```text
support                         2,280
verified                        1,406
not_applicable                    874
remaining Layer 2 correction        0
bounded Browser navigation delta   exact execution result
D1/D3/D4/D5 delta                  0
non-D2 correction/parity delta     0
```

Route C 예상치는 26이지만 이를 success condition으로 강제하지 않는다. Actual Lua full-set comparison이 산출한 exact set만 수정하고 기록한다.

T1-D2 bundle은 `cb27591e... -> D2 final subject` delta만 운반한다. T1-D6가 global current adoption과 canonical integrated validation을 한 번 수행한다.
