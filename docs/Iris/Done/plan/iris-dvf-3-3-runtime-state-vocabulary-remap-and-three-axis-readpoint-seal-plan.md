# Iris DVF 3-3 Runtime-State Vocabulary Remap and Three-Axis Readpoint Seal Plan

> 상태: Draft v0.2-synthesis-review-applied  
> 기준일: 2026-04-26  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> authority input: `DVF 3-3 Runtime-State Vocabulary Remap and Three-Axis Readpoint Seal - Final Synthesized Roadmap` (2026-04-26 user-provided synthesis)  
> 목적: DVF 3-3 current readpoint의 `runtime_state` vocabulary를 `active/silent`에서 `adopted/unadopted`로 remap하고, runtime/quality/publish 3축의 current-state reading을 봉인하는 실행 계획을 고정한다.  
> 실행 상태: planning authority only. 이 문서는 round opening과 실행 순서를 고정하는 계획이며, 작성 시점에는 top docs, runtime artifact, JSON enum, Lua bridge, staged artifact를 변경하지 않는다.

---

## 0. Round Identity

### 0-1. 공식명

```text
DVF 3-3 Runtime-State Vocabulary Remap and Three-Axis Readpoint Seal
```

### 0-2. Round 성격

```text
runtime_state vocabulary remap
+ current-readpoint direct update
+ historical-body preservation
+ three-axis readpoint seal
```

이번 round는 current authoritative readpoint의 용어를 직접 갱신하되, historical sealed decision 본문은 원문 보존한다. Historical wording은 terminology migration note를 통해 canonical read만 갱신한다.

Note: 이전 synthesis의 `B-1'` 표기는 "current readpoint는 직접 갱신하고 historical sealed body는 보존한다"는 선택지를 뜻한다. 이 문서는 해당 의미를 위처럼 self-contained wording으로 풀어쓴다.

### 0-3. Opening Seal

Phase 0 manifest opening은 아래 문구를 그대로 사용한다.

```text
This round migrates the canonical runtime_state vocabulary from
active/silent to adopted/unadopted and seals three-axis current-state reading.

This is a terminology and readpoint remap.
It does not change runtime adoption counts, quality semantics,
publish visibility, UI exposure, Lua consumer behavior,
or historical decision meaning.
```

### 0-4. Staging Root

신규 산출물 root는 아래로 고정한다.

```text
Iris/build/description/v2/staging/compose_contract_migration/runtime_state_vocabulary_remap_round/
```

권장 하위 디렉터리:

- `phase0_scope_lock/`
- `phase1_audit/`
- `phase2_vocabulary_seal/`
- `phase3_drift_classification/`
- `phase4_mutation/`
- `phase5_review/`
- `phase6_closeout/`
- `phase7_walkthrough/`

---

## 1. Manifest Decisions

이 계획은 user-provided roadmap의 manifest 작성 전 결정점 두 개를 아래처럼 채택한다.

### 1-1. Canonical Seal Wording 위치

`DECISIONS.md`에는 Phase 4에서 아래 제목의 draft patch만 생성하고, Phase 6에서 Phase 5 PASS 이후 실제 authoritative 문서에 반영한다.

```text
## <closeout_date> - DVF 3-3 runtime_state vocabulary remapped to adopted/unadopted
```

`<closeout_date>`는 Phase 6 closeout 실행 시 실제 closeout 날짜로 치환한다. 이 placeholder는 planning artifact와 Phase 4 draft patch 안에서는 절대 특정 날짜로 선기입하지 않는다. DECISIONS 날짜는 authoritative ordering에 영향을 주므로 Phase 6 이전에는 authoritative 문서에 반영하지 않는다.

이 항목은 새 runtime behavior 결정이 아니라 `2026-04-07` DVF 3-3 three-axis 재봉인의 terminology/readpoint 갱신으로 읽는다. 과거 sealed decision 본문은 수정하지 않는다.

`ARCHITECTURE.md`에는 current canonical summary readpoint와 Iris DVF 3-3 current architecture section에 보강한다. 정확한 삽입 위치는 Phase 1 audit 후 current readpoint inventory가 확정하지만, 기본 위치는 다음이다.

- top current summary에 `runtime_state canonical values: adopted / unadopted` 추가
- Iris DVF 3-3 current section 중 `runtime/staged state`, `quality/publish split`, `adapter/native metadata migration closeout`을 읽는 current section 뒤에 three-axis read rule 추가
- historical narrative section의 본문은 보존하고 terminology migration note cross-reference만 추가

Historical narrative section cross-reference 형태는 section 첫머리 anchor 한 줄로 제한한다.

```text
Terminology note: 이 section의 runtime_state active/silent는
terminology migration note에 따라 adopted/unadopted로 읽는다.
본문은 historical trace로 보존한다.
```

본문 내 inline annotation, 각 occurrence 옆 주석, `active/silent` 직접 치환은 금지한다.

### 1-2. Phase 1 Audit Whitelist

기본 whitelist는 아래로 확정한다.

```text
docs/Philosophy.md
docs/DECISIONS.md
docs/ARCHITECTURE.md
docs/ROADMAP.md
docs/Iris/Done/quality_state_ownership_spec.md
docs/Iris/Done/publish_state_spec.md
docs/Iris/Done/lua_bridge_publish_state_contract.md
docs/Iris/Done/philosophy_constitutionality_check.md
docs/Iris/Done/semantic_quality_ui_exposure_agenda.md
Iris/build/description/v2/tools/build/**
Iris/build/description/v2/tests/**
Iris/build/description/v2/staging/**
Iris/media/lua/client/Iris/Data/**
runtime_state enum을 emit하거나 검증하는 JSON/JSONL/Lua/report fixture
```

Whitelist 조정 규칙:

- `runtime_state`, `active`, `silent`, `adopted`, `unadopted` 발견 위치가 whitelist 밖이면 Phase 1 inventory에 `scope_expansion_candidate`로 기록한다.
- runtime-facing artifact가 whitelist 밖에서 발견되면 Phase 1 종료 전 whitelist에 편입하거나 explicit exclusion reason을 남긴다.
- 신규 staging root `Iris/build/description/v2/staging/compose_contract_migration/runtime_state_vocabulary_remap_round/**`는 Phase 1 audit 대상에서 제외한다. Phase 4 mutation 이후 Phase 5 review 대상으로만 점검한다.
- `Pulse 생태계 각 모듈별 기능.txt`는 이 round의 authority source가 아니며, Iris runtime_state axis가 발견될 때만 audit 대상에 편입한다.

---

## 2. Baseline Invariants

Baseline은 input reference와 semantic invariant 두 층으로 분리한다. Hash는 Phase 1 `json_enum_update_scope` 결정에 따라 보존 gate 또는 expected terminology-only delta gate로 판정한다.

### 2-1. Input Baseline Invariants

아래 값은 round 시작 시점의 참조값이다. Delta handling은 `2-3. Hash Handling Rule`을 따른다.

```text
pre_round_staged_lua_hash: 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
pre_round_runtime_status: ready_for_in_game_validation
pre_round_active_count: 2084
pre_round_silent_count: 21
```

### 2-2. Semantic Invariants

아래 값과 의미는 Phase 0부터 Phase 6 closeout까지 절대 보존한다.

```text
row_count: unchanged
adopted_count == previous active_count == 2084
unadopted_count == previous silent_count == 21
quality distribution: strong 1316 / adequate 0 / weak 768 unchanged
publish surface split: internal_only 617 / exposed 1467 unchanged
runtime behavior: unchanged
UI exposure policy: unchanged
identity_fallback policy-isolation: unchanged
internal_only semantics: unchanged
Lua bridge availability semantics: unchanged
Browser/Wiki default exposure: unchanged
manual in-game validation status: unchanged
```

### 2-3. Hash Handling Rule

```text
json_enum_update_scope = docs_only 또는 json_enum_and_reports:
  staged Lua hash must remain unchanged
  hash preservation gate applies

json_enum_update_scope = json_enum_reports_and_runtime_facing_artifacts:
  staged Lua hash delta allowed only as expected terminology-only delta
  hash preservation gate becomes hash-delta classification gate
  old_hash and new_hash must both be recorded
  rendered text equality, Lua consumer parse, Browser/Wiki surface unchanged validation required
```

Mutation boundary에서 금지되는 것은 hash change 자체가 아니라 unexpected hash change, rendered text semantic change, row/count/quality/publish/runtime behavior change다.

---

## 3. Out of Scope

이번 round에서는 아래를 열지 않는다.

- `quality_state` / `publish_state` value 체계 변경
- `quality_exposed` 활성화
- semantic quality UI exposure 실행
- `runtime_state` axis 의미 재정의
- `runtime_state` reserved slot 추가
- single writer / bridge contract 변경
- `internal_only` row의 bridge 제거
- `identity_fallback 617` publish policy 변경
- historical sealed decision 본문 일괄 치환
- `not_emitted` 채택
- Korean lexical surface 수정
- Adapter / Native Body Plan migration active queue 재개방
- manual in-game validation pass 선언
- deployed closeout 또는 `ready_for_release` 선언

---

## 4. Phase Plan

| Phase | 초점 | 종료 조건 | 주요 산출물 |
|---|---|---|---|
| 0 | scope lock / baseline freeze | scope lock 작성, ROADMAP Doing 등록 | scope lock, baseline snapshot, invariants |
| 1 | mutation 없는 terminology audit | whitelist coverage, axis tag, JSON enum 범위 결정 | audit inventory, collision report, proxy risk report |
| 2 | vocabulary decision seal | adopted/unadopted와 legacy mapping 봉인 | vocabulary spec, legacy mapping |
| 3 | drift classification | 모든 audit case를 Type A-H로 분류 | drift matrix, current/historical inventory |
| 4 | mutation draft | current readpoint patch 초안, historical note 초안, top docs draft 생성 | canonical seal, top-doc patch drafts, report patch |
| 5 | adversarial review | validation gates PASS | review report, validation report |
| 6 | closeout | closeout state 봉인 | closeout md/json, top docs Done 전환 |
| 7 | walkthrough | traceability read point 작성 | walkthrough md |

---

## 5. Phase 0 - Scope Lock

### 목표

Round 성격, baseline, mutation boundary를 official opening으로 고정한다.

### 작업

- Round Definition을 Phase 0 opening artifact에 기록한다.
- Baseline invariants를 JSON과 Markdown 양쪽에 고정한다.
- Out-of-scope를 mutation boundary로 복제한다.
- `docs/ROADMAP.md` Doing에 이 round를 등록한다.
- 계획 문서 자체는 top docs를 변경하지 않는다. ROADMAP 등록은 Phase 0 실행 시에만 이루어진다.
- 아래 conclusion wording을 Phase 0 scope lock 또는 Phase 6 closeout에 포함한다.

```text
This round may mutate current terminology artifacts, schema/report labels,
and - only if Phase 1 explicitly selects the runtime-facing branch -
runtime-facing vocabulary labels.

Any runtime-facing hash delta must be classified as expected
terminology-only delta and must not be read as rendered text,
quality_state, publish_state, or runtime behavior change.

Historical sealed decision bodies remain immutable except for
external cross-reference anchor notes at section headers.
```

### 산출물

```text
runtime_state_vocabulary_remap_scope_lock.md
runtime_state_vocabulary_remap_baseline_snapshot.json
runtime_state_vocabulary_remap_invariants.md
```

### 종료 조건

- Scope lock 문서가 작성됐다.
- ROADMAP Doing에 이 round가 등록됐다.
- 아직 runtime-facing artifact, historical decision body, JSON enum은 변경하지 않았다.
- `legacy_alias_reader_required` decision이 Phase 1에서 확정될 필수 field로 봉인됐다.

---

## 6. Phase 1 - Audit

Phase 1은 mutation을 하지 않는다. 객관 기록과 범위 결정만 수행한다.

### 6-1. Keyword Set

```text
runtime axis:   active, silent, runtime_state, runtime-adopted
quality axis:   quality_state, quality-pass, semantic_quality, strong, adequate, weak, fail
publish axis:   publish_state, internal_only, exposed, quality_exposed
legacy:         no_ui_exposure
proxy risk:     fact_origin
collision:      adopted, unadopted
```

### 6-2. Axis Tags

| Tag | 의미 |
|---|---|
| `RUNTIME_AXIS_VALUE` | `runtime_state` enum value |
| `QUALITY_AXIS_VALUE` | `quality_state` value |
| `PUBLISH_AXIS_VALUE` | `publish_state` value |
| `EXECUTION_SCOPE` | execution queue/lane 의미 |
| `RENDERED_PREVIEW_SCOPE` | rendered preview scope 한정 표현 |
| `OPERATIONAL_PHRASE` | 운영 표현 |
| `PROVENANCE` | `fact_origin` 등 출처 표시 |
| `DEPRECATED` | `no_ui_exposure` 등 폐기 표현 |
| `AMBIGUOUS` | 의미 불명확 |

### 6-3. Proxy-Reading Risk Check

아래 위험을 별도 report로 분리한다.

- `active`가 quality-pass로 읽힐 위험
- `silent`가 quality fail로 읽힐 위험
- `internal_only`가 runtime availability 축으로 읽힐 위험
- `fact_origin`이 quality proxy로 읽힐 위험
- 동일 수치 `2084`, `617`, `768`이 서로 다른 axis 모집단으로 자동 동일화될 위험

`fact_origin` 검사는 current-state summary/report에서 `runtime_state`, `quality_state`, `publish_state`와 동시에 등장하는 지점으로 제한한다. 독립 provenance refactor는 out-of-scope다.

### 6-4. JSON Enum Inventory

`runtime_state`를 emit하거나 validate하는 모든 위치를 추출한다.

포함 범위:

- code emitter
- data artifact
- validator
- test fixture
- report fixture
- Lua bridge surface
- operator-facing report label

Phase 1 종료 시 아래 결정을 반드시 기록한다.

```json
{
  "json_enum_update_scope": "docs_only | json_enum_and_reports | json_enum_reports_and_runtime_facing_artifacts",
  "staged_lua_hash_delta_expected": "true | false",
  "staged_lua_hash_delta_reason": "none | terminology_only_runtime_state_label_delta",
  "manual_in_game_validation_recheck_required": "true | false",
  "legacy_alias_reader_required": "true | false",
  "legacy_alias_reader_scope": "reader_only | reader_and_writer_guard | not_required",
  "collision_status": "none | found",
  "collision_resolution_required": "true | false"
}
```

`docs_only` 또는 `json_enum_and_reports`인 경우 `staged_lua_hash_delta_expected`는 `false`여야 한다. `json_enum_reports_and_runtime_facing_artifacts`를 선택하는 경우에만 `staged_lua_hash_delta_expected = true`가 가능하며, hash delta는 terminology-only로 분류되어야 한다. `staged_lua_hash_delta_reason`은 delta가 없으면 `none`, delta가 있으면 `terminology_only_runtime_state_label_delta`만 허용한다.

`legacy_alias_reader_required`는 강제 cutover와 backward-compatible reader 중 어느 쪽을 택할지 봉인하는 architectural decision이다. `true`이면 reader-only 또는 reader-and-writer-guard scope를 명시하고, `false`이면 current writer/validator가 새 vocabulary만 emit/accept하는 cutover로 읽는다.

`legacy_alias_reader_required = false`:

```text
current pipeline reader/validator는 legacy active/silent를
current artifact input으로 accept하지 않는다.
historical documentation 참조는 terminology migration note로 커버된다.
historical artifact replay는 explicit legacy mode가 필요하거나
이번 라운드 scope 밖이다.
```

`legacy_alias_reader_required = true`:

```text
reader는 명시적으로 historical로 표시된 artifact에 한해
legacy active/silent를 accept한다.
writer는 여전히 adopted/unadopted만 emit한다.
```

### 6-5. Scope-to-Gate Matrix

| `json_enum_update_scope` | allowed mutations | hash rule | closeout branch |
|---|---|---|---|
| `docs_only` | planning/specification document wording only; generated report artifact not mutated | must remain unchanged | `closed_with_runtime_state_vocabulary_remap_and_three_axis_readpoint_seal` |
| `json_enum_and_reports` | JSON/schema/report writer and operator labels, no runtime-facing payload | must remain unchanged | `closed_with_runtime_state_vocabulary_remap_and_three_axis_readpoint_seal` |
| `json_enum_reports_and_runtime_facing_artifacts` | runtime-facing vocabulary label only, no semantic payload change | expected delta must be classified | in-game validation incomplete 시 `closed_static_ready_for_in_game_validation` |

Default expected closeout branch는 `docs_only` 기준의 `closed_with_runtime_state_vocabulary_remap_and_three_axis_readpoint_seal`이다. Phase 1이 runtime-facing branch를 선택하면 Phase 6 branch expectation을 즉시 갱신한다.

### 산출물

```text
three_axis_terminology_audit.json
runtime_state_active_silent_inventory.json
axis_external_active_inventory.json
new_vocabulary_collision_report.json
runtime_state_json_enum_inventory.json
proxy_reading_risk_report.md
```

### 종료 조건

- Whitelist 전체가 커버됐다.
- 모든 keyword occurrence에 axis tag가 있다.
- JSON enum 갱신 범위가 결정됐다.
- `legacy_alias_reader_required`와 scope가 결정됐다.
- `adopted` / `unadopted` collision 검사가 끝났다.
- `new_vocabulary_collision_report.json`이 Phase 3 Type H classification input으로 연결됐다.

---

## 7. Phase 2 - Vocabulary Decision Seal

### 채택값

```text
runtime_state.adopted
runtime_state.unadopted
```

### Legacy Mapping

```text
active  -> adopted
silent  -> unadopted
```

### `not_emitted` 보류

`not_emitted`는 `silent`를 "emission되지 않음"으로 좁혀 읽게 만들 수 있다. 이 round는 의미 재정의가 아니라 vocabulary remap이므로 보수적 부정형인 `unadopted`를 채택한다. `not_emitted`는 future round reserved item이다.

### Seal 문구

```text
The runtime_state vocabulary is migrated from active/silent to adopted/unadopted.
This is a terminology remap only.
No new runtime_state value is introduced.
No runtime_state reserved slot is introduced.
No runtime behavior, quality semantics, or publish visibility changes.
```

### 산출물

```text
runtime_state_vocabulary_spec.md
runtime_state_legacy_mapping.json
```

### 종료 조건

- Vocabulary와 legacy mapping이 sealed다.
- `not_emitted` 보류 사유가 문서화됐다.
- Reserved slot 추가 없음이 명시됐다.

---

## 8. Phase 3 - Drift Classification

Phase 1 audit 결과를 patch 가능한 drift matrix로 분류한다.

### 8-1. Drift Type Set

| Type | 정의 | Fix Direction |
|---|---|---|
| A | `active`가 quality proxy로 읽힐 위험 | current readpoint에 axis 분리 명시 |
| B | `active`가 axis 외 layer와 동음이의어 | ambiguous readpoint만 disambiguate |
| C | quality/publish axis 의미 누락 또는 과확장 | current readpoint cross-reference 추가 |
| D | deprecated wording이 still-living 문서에 남음 | historical trace 표시 |
| E | `fact_origin`이 quality proxy로 읽힘 | provenance-only 명시 |
| F | current readpoint의 `runtime_state` active/silent | adopted/unadopted 직접 갱신 |
| G | historical sealed decision 본문 active/silent | 본문 보존, migration note 적용 |
| H | adopted/unadopted 신규 collision | collision 위치 disambiguate |

### 8-2. Current vs Historical 기준

Current authoritative readpoint:

```text
ARCHITECTURE.md current section
ROADMAP.md Doing / Next / Hold
current canonical summary
current operating authority artifact 인용 부분
quality_state_ownership_spec.md / publish_state_spec.md 정의 부분
operator-facing report label
```

Historical:

```text
DECISIONS.md sealed decision 본문 전체
ARCHITECTURE.md historical narrative section
ROADMAP.md historical addendum
```

### 산출물

```text
drift_classification_matrix.json
current_readpoint_inventory.json
historical_inventory.json
type_h_collision_resolution_plan.json
```

`type_h_collision_resolution_plan.json`은 collision이 없으면 `not_required` 상태로 생성한다.
Phase 1 `new_vocabulary_collision_report.json`은 Type H의 직접 입력이다. Collision이 발견되면 Phase 3에서 반드시 Type H case로 승격하고 Phase 4 patch list에 포함한다.

### 종료 조건

- 모든 audit finding이 Type A-H 중 하나로 분류됐다.
- Type F와 Type G가 분리됐다.
- Type별 fix direction이 patch list 입력으로 사용할 수 있게 확정됐다.

---

## 9. Phase 4 - Mutation Draft

Phase 4는 current authoritative readpoint mutation patch와 top-doc sync patch를 draft 형태로만 생성한다. 이 Phase에서는 `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`에 authoritative 실반영을 하지 않는다. Historical sealed decision body는 직접 치환하지 않는다.

### 9-1. Canonical Seal 작성

`canonical_seal_draft.md`는 아래 항목을 모두 cover한다.

```text
1. runtime_state axis: adopted / unadopted
2. adopted는 runtime-adopted only, quality-pass 아님
3. quality_state current values: strong / adequate / weak
4. quality_state reserved inactive: fail
5. publish_state current values: internal_only / exposed
6. publish_state reserved inactive: quality_exposed
7. 각 axis의 single writer 위치
8. 각 axis의 consumer 위치
9. adopted != quality-pass != exposed
10. internal_only는 bridge availability 감소가 아니라 default visibility suppression
11. fact_origin은 provenance only, quality proxy 금지
12. axis 외 active 처리 결과
13. semantic UI exposure / quality_exposed deferred-out
14. runtime_state reserved slot 없음
15. JSON enum 갱신 범위
16. legacy alias reader decision
```

### 9-2. Terminology Migration Note

`terminology_migration_note.md`는 아래를 cover한다.

```text
Historical DVF 3-3 runtime_state references before this round
may use active / silent.
After this round, those terms are read as:
  active -> adopted
  silent -> unadopted

This normalization does not change:
  sealed decision meaning
  count
  date
  identifier
  runtime behavior
  publish visibility
  quality semantics

Axis-external historical active is not normalized by this note.
```

Historical narrative section의 cross-reference는 section 첫머리 anchor 한 줄만 허용한다. 본문 내 inline annotation, occurrence별 주석, `active/silent` 직접 치환은 금지한다.

### 9-3. Patch Justification Rule

모든 patch entry는 drift type에 대응하는 한 줄 justification을 가진다.

| Type | Justification example |
|---|---|
| A | `runtime active quality-proxy risk removed, axis separation clarified` |
| B | `axis-external active disambiguated, runtime axis unchanged` |
| C | `quality/publish axis cross-reference restored, no value change` |
| D | `deprecated wording retained as historical trace, current read clarified` |
| E | `fact_origin marked provenance-only, quality proxy forbidden` |
| F | `current readpoint vocabulary remap, meaning unchanged` |
| G | `historical body preserved, terminology migration note applies` |
| H | `new vocabulary collision disambiguated, runtime axis protected` |

### 9-4. Report / Operator Surface

권장 report shape:

```text
runtime_state:
  adopted:   2084
  unadopted: 21

quality_state:
  strong:   1316
  adequate: 0
  weak:     768

publish_state:
  internal_only: 617
  exposed:      1467
```

Operator read:

```text
adopted means runtime-adopted only.
adopted does not imply semantic quality pass.
quality_state is an offline semantic quality axis.
publish_state is the default Browser/Wiki visibility axis.
internal_only means preserved but not default-exposed.
```

### 9-5. Top Docs Patch Draft

Phase 4는 아래 내용을 draft patch로만 생성한다.

```text
DECISIONS_patch_draft.md
ARCHITECTURE_patch_draft.md
ROADMAP_patch_draft.md
top_docs_patch_draft_summary.md
```

Draft patch 안의 `<closeout_date>` placeholder는 그대로 유지한다. Phase 4 draft patch를 authoritative top docs에 적용하는 것은 금지한다.

`docs/DECISIONS.md`:

```text
## <closeout_date> - DVF 3-3 runtime_state vocabulary remapped to adopted/unadopted

Terminology migration note:
Historical DVF 3-3 runtime_state references before this round
may use active / silent.
After this round, those terms are read as:
  active -> adopted
  silent -> unadopted
This is terminology migration only.
Historical decision bodies are not rewritten.
```

`docs/ARCHITECTURE.md`:

```text
runtime_state canonical values: adopted / unadopted
legacy: active -> adopted, silent -> unadopted

adopted is not a quality proxy.
unadopted is not a publish_state.
internal_only is not runtime deletion.

Three current-state axes remain separate:
  runtime_state: adopted / unadopted
  quality_state current values: strong / adequate / weak
  quality_state reserved inactive: fail
  publish_state current values: internal_only / exposed
  publish_state reserved inactive: quality_exposed
```

`docs/ROADMAP.md`:

- Doing: three-axis model 현황 및 legacy interpretation 방침 등록
- Next: vocabulary remap artifact/report/operator validation closeout 등록
- Hold: adopted quality-pass proxy, unadopted publish_state read, historical 본문 일괄 치환, `quality_exposed` 활성화, reserved slot 추가 등록

위 ROADMAP 변경도 Phase 4에서는 draft-only다. Phase 6에서 Phase 5 PASS 이후 실제 문서에 적용한다.

### 9-6. Mutation Boundary

허용:

- current readpoint의 `active -> adopted`, `silent -> unadopted`
- current authoritative wording 갱신
- report/operator-facing label 갱신
- terminology migration note 추가
- drift wording 정정
- deprecated wording 옆 historical trace 표시
- canonical seal cross-reference 추가
- Phase 1 결정 범위에 한한 JSON enum 갱신
- Phase 1에서 runtime-facing artifact mutation으로 판정된 경우의 expected terminology-only hash delta

금지:

- row/count/quality/publish/runtime behavior 변경
- unexpected hash change
- rendered text semantic change
- 날짜 placeholder의 Phase 6 이전 선기입
- Phase 4에서 authoritative top docs에 draft patch 적용
- artifact identity 변경
- quality_state / publish_state value 변경
- semantic UI exposure / `quality_exposed` activation
- historical sealed decision 본문 active/silent 직접 치환
- terminalized lane reopen
- single writer / bridge contract 변경

### 산출물

```text
canonical_seal_draft.md
terminology_migration_note.md
drift_classification_patch_list.json
mutation_boundary_verification.md
quality_publish_runtime_report.patch
operator_summary_patch_report.md
historical_trace_preservation_report.md
DECISIONS_patch_draft.md
ARCHITECTURE_patch_draft.md
ROADMAP_patch_draft.md
top_docs_patch_draft_summary.md
runtime_state_enum_rename_patch.md
runtime_state_legacy_alias_reader_patch.md
runtime_state_writer_emit_report.json
runtime_state_validator_report.json
```

`runtime_state_enum_rename_patch.md`, `runtime_state_legacy_alias_reader_patch.md`, `runtime_state_writer_emit_report.json`, `runtime_state_validator_report.json`은 Phase 1 JSON enum decision에 따라 `not_required`가 될 수 있다. `runtime_state_legacy_alias_reader_patch.md`는 Phase 1 `legacy_alias_reader_required = true`일 때만 생성한다.

### 종료 조건

- Phase 3 drift matrix의 모든 case가 patched 또는 deferred다.
- Mutation boundary violation이 `0`이다.
- Historical sealed decision body direct rewrite가 `0`이다.
- Authoritative top docs direct apply가 `0`이다.

---

## 10. Phase 5 - Adversarial Review

Phase 4 결과를 validation gates로 검증한다. FAIL이면 Phase 4로 회귀한다.

### 10-1. Review Items

```text
1. canonical seal이 모든 drift type을 cover하는가
2. sealed decision 의미가 바뀌지 않았는가
3. terminalized lane을 reopen하지 않았는가
4. runtime invariant가 유지됐는가
5. canonical seal이 새 ambiguity를 만들지 않았는가
6. semantic UI exposure deferred-out과 일관적인가
7. vocabulary remap이 의미 변경을 동반하지 않았는가
8. Type G historical body가 모두 보존됐는가
9. terminology migration note가 historical runtime active/silent를 cover하는가
10. axis 외 active 처리가 원칙과 일관적인가
11. reserved slot 추가 없음이 명시됐는가
12. adopted/unadopted 신규 collision이 없는가
13. JSON enum 갱신 범위가 Phase 1 decision과 일관적인가
```

### 10-2. Validation Gates

| Gate | 조건 |
|---|---|
| A Vocabulary | changed current artifact/report의 `runtime_state` 값은 `adopted / unadopted`만 |
| B Legacy Mapping | historical `active/silent`는 mapping으로 읽히되 current writer는 emit하지 않음 |
| C Three-Axis Separation | runtime adoption, semantic quality, default visibility가 분리됨 |
| D Historical Preservation | historical sealed decision body 직접 치환 없음 |
| E Count Preservation | adopted/unadopted, quality split, publish split, row_count unchanged |
| F Runtime Surface | runtime-facing artifact 변경 시 rendered equality, Lua consumer parse, Browser/Wiki unchanged, hash delta classified |
| G No Scope Creep | `quality_exposed`, semantic UI exposure, reserved slot 추가 없음 |

Gate A는 scope-aware로 판정한다.

```text
변경된 current artifact/report에 한해 runtime_state 값은
adopted/unadopted만 허용한다.

docs_only / json_enum_and_reports scope에서 변경되지 않은
runtime-facing artifact에 legacy active/silent가 잔존하는 경우,
Phase 1에서 해당 위치를 out-of-mutation runtime payload로
명시 분류했고 terminology migration note가 적용됨을 확인하면 pass.

변경이 발생한 writer는 adopted/unadopted만 emit해야 한다.
```

### 산출물

```text
adversarial_review_report.md
three_axis_readpoint_seal_validation_report.json
```

### 종료 조건

PASS. FAIL이면 Phase 4 patch list를 수정하고 재심한다.

---

## 11. Phase 6 - Closeout

### 11-1. Closeout Branch

Default expected closeout branch는 `docs_only` 또는 `json_enum_and_reports` scope에서 `closed_with_runtime_state_vocabulary_remap_and_three_axis_readpoint_seal`이다. Phase 1이 `json_enum_reports_and_runtime_facing_artifacts`를 선택하고 in-game validation이 미완료이면 `closed_static_ready_for_in_game_validation`로 닫는다.

```text
runtime-facing artifact unchanged 또는 in-game validation complete:
  closed_with_runtime_state_vocabulary_remap_and_three_axis_readpoint_seal

runtime-facing artifact changed + in-game validation incomplete:
  closed_static_ready_for_in_game_validation
```

### 11-2. Closeout Wording

```text
This round remapped DVF 3-3 runtime_state vocabulary from
active/silent to adopted/unadopted
and sealed three-axis current-state reading.

Current authoritative readpoints now use adopted/unadopted.
Historical sealed decision bodies are preserved.
Legacy active/silent runtime_state references are interpreted
through the terminology migration note.

No counts, quality_state semantics, publish_state semantics,
runtime behavior, UI exposure policy, or identity_fallback treatment changed.
```

Phase 6은 `<closeout_date>` placeholder를 실제 closeout 날짜로 치환한다. 치환 대상은 Phase 4 draft patch의 `DECISIONS.md` 항목 제목과 closeout JSON 날짜 필드 전체다.

```text
DECISIONS.md closeout 항목의 <closeout_date>는
Phase 6 실행 시점의 실제 날짜로만 치환한다.
Phase 4 draft patch에는 placeholder가 그대로 유지된다.
```

Phase 5 PASS 이후에만 Phase 4 draft patch를 authoritative top docs에 적용한다. 이 시점에 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md` 실반영 report를 생성한다.

### 11-3. Closeout Required Fields

Closeout JSON은 아래 필드를 가진다.

```json
{
  "round_name": "DVF 3-3 Runtime-State Vocabulary Remap and Three-Axis Readpoint Seal",
  "closeout_date": "<closeout_date>",
  "closeout_state": "closed_with_runtime_state_vocabulary_remap_and_three_axis_readpoint_seal",
  "runtime_state_values": ["adopted", "unadopted"],
  "legacy_mapping": {
    "active": "adopted",
    "silent": "unadopted"
  },
  "reserved_slot_added": false,
  "semantic_ui_exposure_deferred": true,
  "quality_exposed_deferred": true,
  "json_enum_update_scope": "phase1_decision_value",
  "legacy_alias_reader_required": "phase1_decision_value",
  "legacy_alias_reader_scope": "phase1_decision_value",
  "axis_external_active_disambiguated_count": 0,
  "axis_external_active_preserved_count": 0,
  "deferred_case_count": 0,
  "historical_body_rewrite_count": 0,
  "pre_round_staged_lua_hash": "0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062",
  "post_round_staged_lua_hash": "unchanged | <new_hash>",
  "staged_lua_hash_delta_expected": "phase1_decision_value",
  "staged_lua_hash_delta_classification": "none | terminology_only_runtime_state_label_delta",
  "pre_round_runtime_status": "ready_for_in_game_validation",
  "post_round_runtime_status": "ready_for_in_game_validation"
}
```

### 산출물

```text
runtime_state_vocabulary_remap_closeout.md
runtime_state_vocabulary_remap_closeout.json
DECISIONS.md closeout 결정 항목
ARCHITECTURE.md 갱신 확정본
ROADMAP.md Done 전환
top_docs_patch_applied_report.md
```

---

## 12. Phase 7 - Walkthrough

Walkthrough는 새 authority나 gate source가 아니라 traceability read point다.

### 포함 내용

- 왜 `adopted/unadopted`인가
- 왜 `not_emitted`를 보류했는가
- 왜 historical sealed decision body를 보존했는가
- 어떤 current readpoint를 직접 수정했는가
- axis 외 `active`를 어떻게 audit하고 처리했는가
- 어떤 artifact/report/doc이 바뀌었는가
- 어떤 것은 바뀌지 않았는가
- JSON enum 갱신 범위 결정 과정
- 검증 결과 요약
- 후속 reserved 항목

### 산출물

```text
docs/Iris/iris-dvf-3-3-runtime-state-vocabulary-remap-and-readpoint-seal-walkthrough.md
```

---

## 13. Execution Order

```text
0. Scope lock / baseline invariants / ROADMAP Doing 등록
1. Audit / axis tag / collision 검사 / JSON enum 범위 결정
2. Vocabulary decision seal
3. Drift classification
4. Mutation draft / canonical seal / cross-reference / operator surface / top-doc patch draft
5. Adversarial review / validation gates
6. Closeout / top-doc patch apply
7. Walkthrough
```

---

## 14. Risk Register

| 위험 | 대응 |
|---|---|
| Phase 4 mutation boundary 모호성 | patch 단위 justification 필수 |
| historical 본문 직접 치환 위험 | Type G 재확인 후 migration note만 적용 |
| 새 vocabulary collision 위험 | Phase 1 collision report + Phase 5 Gate 12 |
| closeout이 새 behavior 결정으로 읽힐 위험 | `2026-04-07` three-axis 재봉인의 표기 갱신임을 명시 |
| JSON enum scope 결정 위험 | Phase 1 종료 시 hash/QA 영향까지 같이 결정 |
| audit 누락 위험 | whitelist 밖 occurrence를 scope expansion candidate로 기록 |
| axis 외 active 처리 결과 누락 | closeout에 disambiguated/preserved/deferred count 필수 기록 |

---

## 15. Non-Reopen Clause

이 plan은 아래를 자동으로 열지 않는다.

- Adapter / Native Body Plan active metadata migration
- Silent Metadata Intake / Cleanup Round
- Resolver Compatibility Mapping Cleanup Round
- manual in-game validation QA round
- semantic quality UI exposure round
- `quality_exposed` activation round
- runtime rebaseline
- deployed closeout
