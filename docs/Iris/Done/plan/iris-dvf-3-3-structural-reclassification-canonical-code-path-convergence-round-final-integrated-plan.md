# Iris DVF 3-3 Structural Reclassification Canonical Code-Path Convergence Round Final Integrated Plan

> 상태: Draft v0.3  
> 기준일: 2026-04-24  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/Iris/iris-dvf-3-3-phase-d-e-staged-rollout-override-round-plan.md`, `docs/Iris/iris-dvf-3-3-phase-d-e-staged-rollout-override-round-walkthrough.md`, `docs/Iris/iris-dvf-3-3-phase-d-observer-signal-preservation-patch-round-plan.md`, `docs/Iris/iris-dvf-3-3-phase-d-observer-signal-preservation-patch-round-walkthrough.md`, `docs/Iris/iris-dvf-3-3-entrypoint-drift-patch-authority-seal-round-plan.md`  
> authority input: `Iris DVF 3-3 Structural Reclassification Canonical Code-Path Convergence Round — 최종 통합 로드맵` (2026-04-24 user-provided roadmap)  
> 목적: observer lane 내부에서 legacy structural reclassification default code path를 2026-04-24 dual-axis canonical model로 수렴시키고, default artifact/summary/hash read point를 lossy single-slot 해석에서 canonical dual-axis 해석으로 교체하기 위한 execution-planning authority를 고정한다.  
> 실행 상태: planning authority only, revised after integrated review v0.1, v0.2. 이 문서는 branch choice, phase order, artifact topology, validation gate, top-doc reflection 범위를 봉인하지만, same-turn code mutation이나 top-doc patch를 선언하지 않는다.

> 이 문서는 additive observer lane 확장 계획이 아니다.  
> 이 문서는 existing observer default path를 canonical dual-axis read model로 교체·수렴시키는 계획이다.

---

## 0. Round Identity와 Opening Baseline

### 0-1. Round identity

| 항목 | 값 |
|---|---|
| round 이름 | `Iris DVF 3-3 Structural Reclassification Canonical Code-Path Convergence Round` |
| round 성격 | observer lane 내부 code-path convergence / replacement round |
| current problem statement | additive canonical lane는 닫혔지만, default structural reclassification path는 여전히 lossy single-slot 해석을 가진다 |
| 상위 authority | `compose_profiles_v2.json + body_plan` |
| authority rehearing | 없음 |
| writer/runtime authority migration | 본 round 범위 밖 |
| expected pass closeout state | `closed_with_canonical_code_path_convergence_applied` |
| alternate terminal state | `closed_with_distribution_handoff_to_next_round` pass closeout이 아니며, top-doc current-state reflection을 열지 않음 |

### 0-2. 한 문장 scope lock

> 이번 round는 `report_layer3_body_plan_structural_reclassification.py` 계열의 default observer read path를 2026-04-24 canonical dual-axis contract와 같은 해석으로 수렴시키는 것만 다룬다.

### 0-3. Upstream preconditions

아래 세 closeout은 adopted precondition이며 재심하지 않는다.

- `2026-04-22` staged/static closeout
- `2026-04-23` EDPAS direct default entrypoint authority seal
- `2026-04-24` additive signal preservation closeout

현재 round는 위 세 closeout을 reopen하지 않는다. 특히 `compose_profiles_v2.json + body_plan`, staged/workspace Lua parity hash, `ready_for_in_game_validation`, `quality_baseline_v4`, single-writer contract는 유지한 채 observer default read path만 convergence한다.

여기서 "재심하지 않음"의 의미는 해당 round들의 결정과 closeout legitimacy를 뒤집지 않는다는 뜻이다. 후속 round가 current default-path observer authority artifact를 supersede하는 것은 재심이 아니라 state progression으로 읽는다.

### 0-4. Current divergence read

현재 workspace 기준 observer lane은 두 경로로 갈라져 있다.

- legacy default observer artifact
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_structural_reclassification.2105.jsonl`
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_e_current_session/body_plan_structural_reclassification.2105.summary.json`
- additive canonical observer lane
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_signal_preservation_patch_round/body_plan_signal_preservation.2105.jsonl`
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_signal_preservation_patch_round/body_plan_signal_preservation.source_distribution.json`
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_signal_preservation_patch_round/body_plan_signal_preservation.section_distribution.json`
  - `Iris/build/description/v2/staging/compose_contract_migration/phase_d_signal_preservation_patch_round/body_plan_signal_preservation.crosswalk.json`

이번 round의 핵심 질문은 아래 한 문장으로 고정한다.

> default structural reclassification path가 더 이상 single-slot lossy observer view를 기본 해석으로 사용하지 않고, source axis와 section axis를 물리적으로 분리한 canonical dual-axis read를 default로 집행하는가?

### 0-5. Branch choice and disposition frame

Phase 0 첫 항목은 아래 세 branch를 명시적으로 기록해야 한다.

| Branch | 의미 | artifact disposition | 현재 계획에서의 위치 |
|---|---|---|---|
| `regenerate` | legacy artifact를 dual-axis canonical artifact로 교체 | `signal_preservation` current default-path wording superseded, legacy hash set historical trace 전환 | 기본안 / 권장 |
| `freeze-and-redirect` | legacy artifact를 유지하되 code path만 dual-axis로 전환 | artifact topology 유지, code path만 redirect | 대안 branch |
| `deprecate` | legacy artifact를 sunset하고 consumer를 `signal_preservation` artifact로 redirect | legacy sunset, additive artifact consumer redirect | 보류 branch |

본 문서는 `regenerate + supersession`을 기본 execution branch로 작성한다. 이는 아래를 뜻한다.

- current default-path authority artifact는 closeout 후 plain-name canonical `body_plan_structural_reclassification.2105.*` 세트로 이동한다.
- `body_plan_signal_preservation.*`는 `2026-04-24` additive lane의 adopted artifact이자 traceability baseline으로 남지만, current default-path authority wording은 이 round에 의해 superseded된다.
- 병렬 canonical 경로는 채택하지 않는다. 목적이 authority 추가가 아니라 authority convergence이기 때문이다.
- artifact 비생성 + helper rewire 경로는 기본안으로 채택하지 않는다. code와 artifact의 해석 분열을 남기기 때문이다.

Phase 0에서 다른 branch를 선택하면 Phase 4 artifact topology, Phase 5 hash gate, Phase 6 top-doc wording을 branch에 맞춰 다시 좁혀 써야 한다.

### 0-6. Tier classification

이 round는 `Tier 2`이며 `scope_policy_override_round`는 아니다.

이유는 아래처럼 고정한다.

- `regenerate` branch는 canonical observer artifact baseline hash를 새로 선언한다.
- 기존 `body_plan_structural_reclassification` `jsonl + summary` artifact 세트 hash는 historical trace로 밀린다.
- 이 행위는 단순 diagnostic lane 추가가 아니라 canonical read point 이관에 해당한다.
- `2026-04-22` / `2026-04-24` closeout의 artifact hash freeze는 각 round gate 기준이지 영구 seal이 아니다.
- 따라서 이번 round의 supersession은 기존 closeout을 invalidate하는 override가 아니라 후속 current-state 갱신으로 읽는다.
- Tier 2 round이므로 Phase 0 design adversarial review를 필수 산출물로 가진다.

### 0-7. Staging root

이번 round의 provenance/artifact root는 아래로 고정한다.

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/
```

권장 하위 디렉터리:

- `phase0_opening/`
- `phase1_snapshot/`
- `phase2_contract/`
- `phase3_patch/`
- `phase4_artifacts/`
- `phase5_validation/`
- `diagnostic/legacy_view/`
- `closeout/`

---

## 1. 전역 봉인선

### 1-1. Hard sealed invariants

| 항목 | 값 |
|---|---|
| `writer_role` | `observer_only` |
| staged/workspace Lua hash | `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062` |
| runtime status | `ready_for_in_game_validation` unchanged |
| baseline row count | `2105` |
| runtime state | `active 2084 / silent 21` |
| runtime path | `cluster_summary 2040 / identity_fallback 17 / role_fallback 48` |
| publish split | `internal_only 617 / exposed 1467` |
| quality split | `strong 1316 / adequate 0 / weak 768` |

### 1-2. Non-goals

아래 항목은 모든 phase에서 reopen 금지다.

- `quality_state`, `publish_state`, rendered text 변경
- Lua bridge / runtime consumer 변경
- `quality_baseline_v4 -> v5` cutover
- semantic carry 또는 weak family 정책 반영
- deployed closeout / `ready_for_release`
- manual in-game validation
- compose / quality / publish writer authority 이동
- same-build re-compose
- source expansion execution

### 1-3. Current code and reference surfaces

현재 convergence scope에서 읽는 대표 surface는 아래처럼 고정한다.

- default legacy target
  - `Iris/build/description/v2/tools/build/report_layer3_body_plan_structural_reclassification.py`
- canonical reference lane
  - `Iris/build/description/v2/tools/build/report_layer3_body_plan_signal_preservation.py`
  - `Iris/build/description/v2/tools/build/build_phase_d_signal_preservation_baseline.py`
  - `Iris/build/description/v2/tools/build/validate_phase_d_signal_preservation.py`
  - `Iris/build/description/v2/tools/build/build_signal_preservation_crosscheck.py`
  - `Iris/build/description/v2/tools/build/build_phase_d_signal_preservation_diagnostic_packet.py`

Phase 3 구현은 기존 legacy script를 직접 분해할 수도 있고, existing canonical helper를 재사용하도록 default entrypoint를 재배선할 수도 있다. 그러나 최종 closeout은 아래 두 조건을 동시에 만족해야 한다.

1. default execution path는 하나의 canonical dual-axis code path로 수렴한다.
2. single-slot legacy read는 explicit diagnostic/compat path로만 격리된다.

---

## 2. Phase 0 — Opening Seal + Branch Selection + Tier 2 Design Review

**목적:** round 전체의 branch, scope, tier, invariants를 먼저 봉인해 이후 phase의 산출물 의미를 흔들리지 않게 한다.

### 2-1. 필수 결정

- 세 branch를 모두 문서화한다.
- 현재 계획의 기본안인 `regenerate`를 선택하는지 여부를 명시한다.
- `signal_preservation` artifact disposition을 `superseded / parallel canonical / redirect-only` 중 무엇으로 읽는지 명시한다.
- 본 문서의 기본안인 `regenerate + supersession`을 채택하는지 여부를 명시한다.
- In-scope / Out-of-scope를 다시 적는다.
- hard sealed invariant와 non-writer boundary를 함께 적는다.
- Tier 2 판정을 명시하고 이유를 적는다.
- `scope_policy_override_round` 해당 없음과 그 이유를 적는다.
- Phase 5 exact-match gate용 `pre_approved_exception_table` 기본 상태를 `empty by default`가 아니라 `empty and non-operational for this round`로 선언한다.
- `pre_approved_exception_table.md`는 future round용 reserved structure일 뿐이며, 이번 round에서는 mismatch 완화 수단으로 사용할 수 없음을 명시한다.

### 2-2. 필수 산출물

- `scope_lock.md`
- `baseline_freeze.json`
- `non_writer_boundary.md`
- `tier_classification_memo.md`
- `structural_reclassification_code_path_convergence_tier2_design_adversarial_review.md`

### 2-3. Gate

- branch가 선택되고 기록된다.
- `signal_preservation` disposition이 명시되고, branch와 모순되지 않는다.
- `regenerate`를 선택하지 않는 경우, 이후 phase의 canonical artifact/hash wording을 재작성해야 함이 적힌다.
- `compose_profiles_v2.json + body_plan` authority non-rehearing이 명시된다.
- `scope_policy_override_round` 비해당 사유가 기록된다.
- staged/workspace Lua hash, runtime status, row count invariant가 baseline freeze에 기록된다.
- writer/runtime boundary가 `observer_only`로 다시 봉인된다.
- Tier 2 design adversarial review conclusion이 `pass` 또는 `pass_with_required_impl_guards`다.
- `pre_approved_exception_table.md`가 이번 round에서 append/update 금지라는 운영 규칙이 기록된다.

---

## 3. Phase 1 — Pre-Change Snapshot + Baseline Freeze

**목적:** 현재 legacy default read model의 문제를 코드와 artifact 양쪽에서 증거화하고, convergence 전 baseline을 동결한다.

### 3-1. 코드 스캔 목표

`report_layer3_body_plan_structural_reclassification.py`를 중심으로 아래 질문을 문서화한다.

- source-side family와 section-derived family가 어디에서 같은 슬롯에 쓰이는가
- `violation_flags`가 `violation_type`보다 먼저 읽히는 순서 버그가 있는가
- section-derived family가 old source family namespace로 재명명되어 같은 bucket에 들어가는가
- 현재 default summary가 overlap을 row-level이 아니라 summary-level에서만 추론하는가

### 3-2. Snapshot 목표

다음을 machine-readable snapshot으로 남긴다.

- current legacy observer artifact workspace path 확증
- current legacy `jsonl + summary` artifact 세트 hash
- current legacy row count / summary count
- current legacy lossy distribution
- current `body_plan_signal_preservation.2105.jsonl` 분포와의 delta
- current `body_plan_signal_preservation.2105.jsonl`의 row field naming verification
- current consumer list와 access pattern

### 3-3. Consumer scan 목표

legacy structural artifact 또는 summary를 읽는 downstream consumer를 전수 스캔한다.

Scan 대상 예시:

- build/validation scripts
- docs/walkthrough reference points
- any staging report generator that reads `body_plan_structural_reclassification.2105.*`
- any consumer that reads `*.summary.json`
- any consumer that depends on legacy summary key names, field meanings, bucket structure, or aggregate count shape
- any wrapper/default script that still treats single-slot summary as current authority

### 3-4. 필수 산출물

- `pre_change_snapshot.json`
- `legacy_read_model_scan.md`
- `entrypoint_surface_scan.json`
- `legacy_access_guard_plan.md`

### 3-5. Gate

- current legacy hash와 row count가 고정된다.
- current workspace path가 문서상 `phase_d_e_current_session/` 경로와 일치하는지 확증되거나 차이가 correction note로 기록된다.
- default path와 diagnostic path의 current call surface가 식별된다.
- lossy overwrite가 실제 code/model issue로 문서화된다.
- `2026-04-24` additive lane row field naming이 snapshot으로 확증되거나, 불일치 시 translation boundary가 blocking note로 기록된다.
- consumer scan이 완료되어 convergence 후 explicit legacy path가 필요한 위치가 분리된다.
- `*.summary.json` consumer의 path compatibility뿐 아니라 schema content compatibility도 스캔된다.

---

## 4. Phase 2 — Canonical Read Contract 문서화

**목적:** 코드를 먼저 고치지 않고, default path가 따라야 할 canonical read contract를 문서로 봉인한다.

Phase 2 pass 전에는 Phase 3 code patch를 시작할 수 없다.

### 4-1. Source Axis Contract

- `violation_type`는 explicit primary authority다.
- `violation_flags`는 2026-04-24에 승인된 closed allowlist fallback일 때만 source axis에 반영한다.
- 이번 round에서 fallback 범위를 넓히지 않는다.
- source axis는 upstream field 이름을 유지한다.
- fallback은 primary를 덮어쓰지 못한다.
- observer row output field 이름은 `source_signal_primary`, `source_signal_secondary`, `source_signal_origin`, `source_signal_present`로 고정한다.
- 이 field 이름은 `2026-04-24` `body_plan_signal_preservation.2105.jsonl` naming을 승계한 것으로 읽고, Phase 1 snapshot에서 exact field naming을 확증한다.

### 4-2. Section Axis Contract

- section axis는 `body_plan` section trace에서 재계산한다.
- namespace는 반드시 `SECTION_*`를 사용한다.
- source axis와 같은 row에 공존할 수 있지만 물리적으로 다른 슬롯이다.
- source axis를 절대 덮어쓰지 않는다.
- observer row output field 이름은 `section_signal_primary`, `section_signal_secondary`, `section_signal_origin`, `section_signal_present`로 고정한다.
- 이 field 이름은 `2026-04-24` additive lane naming을 승계한 것으로 읽고, Phase 1 snapshot에서 exact field naming을 확증한다.

### 4-3. Special Signal 처리 원칙

- `LAYER4_ABSORPTION`
  - source family 승격 금지
  - upstream probe 또는 `SECTION_LAYER4_ABSORPTION`로만 읽는다
- `IDENTITY_ONLY`, `ACQ_DOMINANT`
  - count target이 아니라 existence / no-overwrite target이다
- `ADEQUATE`
  - 이번 round의 preservation target이 아니다

### 4-4. Overlap State Contract

observer row overlap field 이름은 `signal_overlap_state`로 고정한다.
이 field 이름 역시 `2026-04-24` additive lane naming을 승계한 것으로 읽는다.

허용 overlap 값은 아래 네 개뿐이다.

| 상태 | 의미 |
|---|---|
| `source_only` | source 값만 존재 |
| `section_only` | section 값만 존재 |
| `coexist` | 양쪽 모두 존재 |
| `dual_none` | 양쪽 모두 없음 |

generic `none`은 overlap field 일반값으로 사용하지 않는다. remainder `none`은 `dual_none`에서만 읽는다.

### 4-5. Exact-match target and exception rule

이번 round는 2026-04-24 closeout target을 그대로 읽는다.

| 축 | 기준 |
|---|---|
| source total | `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481` |
| section total | `SECTION_FUNCTION_NARROW 1433 / none 672` |
| overlap | `source_only 67 / section_only 876 / coexist 557 / dual_none 605` |

운영 규칙은 아래처럼 고정한다.

- source / section / overlap은 기본적으로 exact match required다.
- 이번 round에서 `pre_approved_exception_table.md`는 structure reservation only다. entry 추가, 수정, soft-grant는 금지한다.
- mismatch 관측 후 same-session append로 pass를 만드는 self-service path는 금지한다.
- `reason-traced`만으로는 통과할 수 없다.
- 따라서 이번 round에서 mismatch는 `fail` 또는 separately defined `handoff closeout`다.

### 4-6. 필수 산출물

- `canonical_read_contract.md`
- `source_axis_contract.md`
- `section_axis_contract.md`
- `overlap_semantics.md`
- `pre_approved_exception_table.md`

### 4-7. Gate

- default path의 primary/fallback/namespace/overlap contract가 문서로 고정된다.
- `LAYER4_ABSORPTION`, `IDENTITY_ONLY`, `ACQ_DOMINANT`, `ADEQUATE`의 처리 원칙이 분리된다.
- preservation target과 hard invariant가 구분되어 적힌다.
- observer row output field naming과 upstream input field naming이 분리되어 적힌다.
- `pre_approved_exception_table.md`가 생성되고, 이번 round에서는 `empty and non-operational`임이 명시된다.
- Phase 3은 이 문서의 구현 단계로만 읽히고, contract 재논의 단계로 읽히지 않는다.

---

## 5. Phase 3 — Legacy Script 책임 분해 + Code Patch

**목적:** default observer code path를 dual-axis canonical contract에 맞춰 수렴시키고, legacy single-slot view를 explicit diagnostic path로 격리한다.

### 5-1. 내부 책임 분리

default canonical path는 최소 아래 네 책임으로 분해한다.

```text
read_source_signal()
derive_section_signal()
compute_overlap_state()
aggregate_dual_axis_distribution()
```

구현 방식은 아래 둘 중 하나를 허용한다.

- `report_layer3_body_plan_structural_reclassification.py`를 직접 분해해 canonical path로 만든다.
- existing canonical helper를 재사용하되, default entrypoint를 하나의 canonical code path로 재배선한다.

어떤 방식을 택하더라도 closeout 기준은 default path convergence다. additive helper 병존 자체가 목표가 아니다.
helper 재사용 경로를 택하더라도 output artifact는 `body_plan_signal_preservation.*`를 재사용하지 않고, Phase 4의 plain-name canonical artifact set으로 emit되어야 한다.

### 5-2. 금지 구조

- source family와 section family를 하나의 `family` 필드에 합치기
- `violation_flags`를 먼저 읽고 `violation_type`을 덮는 순서
- section-derived family를 old source family처럼 재명명해 같은 bucket에 넣기
- overlap을 summary 단계에서만 추론하고 row artifact에 남기지 않기

### 5-3. Legacy path isolation

legacy single-slot read는 삭제가 아니라 explicit-only 격리 대상으로 둔다.

- canonical path: default execution
- legacy path: `diagnostic_legacy_view` 또는 `compat_legacy` 같은 explicit flag/mode에서만 허용

구체 mode 이름은 Phase 1 surface scan에서 확정하되, 의미는 위 두 줄에서 바뀌지 않는다.

### 5-4. Observer-only guard

아래 중 최소 하나로 non-writer 경계를 code level에서 증명한다.

- assertion
- explicit `writer_role` tag
- focused test

증명 대상은 아래처럼 고정한다.

- compose에 write하지 않음
- quality/publish에 write하지 않음
- rendered text를 재생성하지 않음
- Lua/runtime artifact를 건드리지 않음

### 5-5. 필수 산출물

- refactored canonical default script path
- `legacy_mode_notes.md`
- `default_vs_legacy_read_matrix.md`

### 5-6. Gate

- default execution이 dual-axis row model과 separate distributions를 직접 생성한다.
- explicit legacy mode 없이는 single-slot summary가 생성되지 않는다.
- legacy compatibility path가 diagnostic root 밖의 canonical read point를 오염시키지 않는다.
- observer-only guard가 test 또는 code-level assertion으로 기록된다.

---

## 6. Phase 4 — Canonical Artifact Topology 재정렬

**목적:** `regenerate` branch 기준으로 default artifact topology를 dual-axis canonical set으로 교체하고, legacy single-slot 산출물을 diagnostic lane으로 이동시킨다.

### 6-1. Canonical output

default execution은 아래 canonical artifact set을 직접 생성해야 한다.

- `body_plan_structural_reclassification.2105.jsonl`
- `body_plan_structural_reclassification.2105.summary.json`
- `body_plan_structural_reclassification.source_distribution.json`
- `body_plan_structural_reclassification.section_distribution.json`
- `body_plan_structural_reclassification.overlap_distribution.json`
- `body_plan_structural_reclassification.crosswalk.json`
- `body_plan_structural_reclassification.artifact_validation_report.json`

이 세트는 더 이상 additive side lane이 아니라 default observer read point다. canonical 쪽이 plain basename을 차지하고, legacy 쪽이 `*_legacy_single_slot.*` suffix를 달고 빠지는 명명 규칙을 사용한다.

`body_plan_structural_reclassification.2105.summary.json`은 기존 `*.summary.json` consumer surface를 유지하는 stable aggregate summary다. 이 summary는 source/section/overlap/crosswalk self-summary와 artifact-level validation 요약을 제공하며, supplementary distribution artifacts에 대한 index 역할도 겸한다.

summary schema stability contract는 아래처럼 고정한다.

- plain-name `.summary.json`은 legacy consumer가 기대하는 stable top-level subset을 유지한다.
- old single-slot interpretation aggregate는 top-level canonical key가 아니라 `legacy_compat_summary` subsection으로만 제공한다.
- new dual-axis aggregate는 top-level canonical keys 또는 nested summary keys로 제공한다.
- distribution/crosswalk/artifact-validation pointer는 `linked_artifacts` object 아래에 둔다.
- 최소 pointer key는 `source_distribution`, `section_distribution`, `overlap_distribution`, `crosswalk`, `artifact_validation_report`다.
- optional `summary_schema_version`은 허용되지만, current consumer compatibility를 깨는 required migration signal로 사용하지 않는다.

`body_plan_structural_reclassification.artifact_validation_report.json`은 artifact-level self-validation이다. 이는 schema integrity, row count, summary/distribution internal consistency, summary pointer integrity를 확인하는 Phase 4 산출물이다.

### 6-2. Legacy output isolation

legacy single-slot output은 아래 diagnostic lane으로 분리한다.

```text
Iris/build/description/v2/staging/compose_contract_migration/phase_d_structural_reclassification_code_path_convergence_round/diagnostic/legacy_view/
```

권장 산출물:

- `body_plan_structural_reclassification_legacy_single_slot.2105.jsonl`
- `body_plan_structural_reclassification_legacy_single_slot.summary.json`

이 lane은 compatibility/diagnostic output일 뿐이며 release/current-state authority read point가 아니다.

### 6-3. 새 hash 선언

`regenerate` branch에서는 plain-name canonical artifact 세트 hash를 이 round의 새 baseline으로 선언한다.

문서 규칙:

- 기존 legacy structural reclassification `jsonl + summary` artifact 세트 hash는 historical trace로 전환한다.
- `body_plan_signal_preservation.*`는 `2026-04-24` additive lane의 adopted artifact로 유지되지만, current default-path authority wording은 superseded된다고 명시한다.
- DECISIONS.md 반영 시 `2026-04-24 additive lane canonical read point wording is superseded for current default-path authority by this convergence closeout` 문장이 포함되어야 한다.
- runtime/staged Lua hash는 여전히 unchanged invariant로 남는다.

### 6-4. Gate

- default canonical output 세트가 생성된다.
- canonical plain-name `.summary.json`이 생성되고 current consumer compatibility 역할이 정의된다.
- legacy single-slot output은 diagnostic lane에만 존재한다.
- `regenerate` branch 기준 새 observer artifact 세트 hash declaration 문안이 준비된다.
- old lossy artifact가 current default read point로 다시 사용되지 않도록 consumer path가 차단된다.

---

## 7. Phase 5 — Validation Gate

**목적:** canonical convergence가 artifact-level, code-path-level, non-writer-level로 모두 닫혔는지 검증한다.

### 7-1. 완료 조건

| 조건 | 내용 |
|---|---|
| 완료 조건 1 | row-level로 source-side family와 section-derived family가 물리적으로 다른 슬롯에 기록되고 overwrite가 `0`건이다 |
| 완료 조건 2 | source target `BODY_LACKS_ITEM_SPECIFIC_USE 617 / FUNCTION_NARROW 7 / none 1481`이 exact match다. mismatch는 pass가 아니라 separate handoff or fail 경로로만 처리된다 |
| 완료 조건 3 | section target `SECTION_FUNCTION_NARROW 1433 / none 672`이 exact match다. mismatch는 pass가 아니라 separate handoff or fail 경로로만 처리된다 |
| 완료 조건 4 | overlap distribution `source_only 67 / section_only 876 / coexist 557 / dual_none 605`가 exact match다. mismatch는 pass가 아니라 separate handoff or fail 경로로만 처리된다 |
| 완료 조건 5 | `IDENTITY_ONLY`, `ACQ_DOMINANT` replacement가 `0`이다 |
| 완료 조건 6 | staged/workspace Lua hash `0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062`와 `ready_for_in_game_validation` 상태가 unchanged다 |
| 완료 조건 7 | `quality_state`, `publish_state`, rendered text, `quality_baseline_v4`, `quality_publish_decision_preview` 어느 것도 write되지 않음을 code-level + artifact-level로 증명한다 |
| 완료 조건 8 | `entrypoint_surface_scan.json`에 기록된 build_script / cli_direct / test_harness / wrapper surface가 전부 canonical path로 resolve되고 implicit legacy fallback이 `0`건이다 |
| 완료 조건 9 | designated unit tests pass, direct default diagnostic run emits canonical dual-axis meta, design review guard violations가 `0`이다 |
| 완료 조건 10 | canonical plain-name `.summary.json`이 존재하고 Phase 1에서 식별한 `*.summary.json` consumer가 NotFound 없이 resolve되며 schema content compatibility failure가 `0`건이다 |

### 7-2. 필수 산출물

- `entrypoint_surface_guard_report.json`
- `convergence_validation_report.json`
- `convergence_crosscheck_report.json`
- `artifact_hash_guard_report.json`
- `diagnostic_packet.json`

### 7-3. Gate 해석 규칙

- `body_plan_structural_reclassification.artifact_validation_report.json`은 artifact-level self-validation이다.
- `convergence_validation_report.json`은 round-level convergence gate report다.
- source / section / overlap mismatch는 이번 round에서 pass로 승격할 수 없다.
- `pre_approved_exception_table.md`는 this-round mismatch 완화 authority가 아니다.
- source mismatch는 silent repair가 아니라 explicit failure reason 또는 separately defined handoff closeout reason으로 기록한다.
- section/overlap mismatch도 hard invariants가 유지될 때는 handoff closeout 후보가 될 수 있으나, pass closeout 근거는 아니다. `reason-traced` alone은 통과 근거가 아니다.
- runtime immutability 위반은 immediate blocker다.
- observer-only contract 위반은 immediate blocker다.
- `convergence_crosscheck_report.json`은 `2026-04-24`의 `signal_preservation_crosscheck_report.json`과 Phase 2 exact-match target을 reference baseline으로 사용한다.
- handoff closeout은 `closed_with_distribution_handoff_to_next_round`로 닫히며 `§9-1` pass closeout state와 구분된다.
- handoff closeout은 hard invariants, non-writer seal, entrypoint surface guard, artifact hash guard가 모두 pass했지만 exact-match target이 닫히지 않을 때만 허용된다.
- handoff closeout은 Phase 6 top-doc current-state reflection을 열지 않는다.

---

## 8. Phase 6 — 문서 반영

**목적:** convergence closeout이 top docs에 current state로 반영되도록 patch 범위를 봉인한다.

Top docs는 Phase 5 pass 이후에만 갱신한다.

### 8-1. `DECISIONS.md`

아래 내용을 신규 항목으로 기록한다.

- legacy structural reclassification default read는 이제 dual-axis canonical model을 따른다
- `violation_type` primary / `violation_flags` restricted fallback / `SECTION_*` section namespace를 current contract로 고정한다
- `2026-04-24` additive lane canonical read point wording은 current default-path authority에 대해 이 convergence closeout으로 superseded된다
- `body_plan_signal_preservation.*`는 `2026-04-24` additive verification lane / historical interim canonical trace로 남는다
- legacy single-slot read는 explicit diagnostic/compat only다
- plain-name `body_plan_structural_reclassification.2105.*`가 current default observer read point다
- 2026-04-24에 기록된 legacy `jsonl + summary` artifact 세트 hash는 historical trace로 전환한다
- 새 canonical baseline hash를 기록한다
- 이 round는 writer/runtime authority를 reopen하지 않는다

### 8-2. `ARCHITECTURE.md`

아래 내용을 current Iris addendum에 반영한다.

- `body_plan_structural_reclassification`의 current canonical read model을 dual-axis로 갱신
- `2026-04-24 §11-59` additive canonical model은 `2026-04-24` lane의 adopted traceability section으로 유지하되, current default-path authority wording은 superseded되었음을 명시
- observer patch applied but canonical code path divergence remains라는 상태를 닫고, current issue status를 convergence complete로 바꾼다

### 8-3. `ROADMAP.md`

아래 addendum 구조를 반영한다.

- Done: this round
- Doing: 없음
- Next: manual in-game validation QA round
- Hold: deployed closeout / `quality_baseline_v4 -> v5` / runtime-side rewrite / semantic carry / source expansion

### 8-4. Gate

- top-doc wording이 additive lane 추가가 아니라 canonical code-path convergence로 읽힌다.
- `2026-04-22`, `2026-04-23`, `2026-04-24` precondition closeout을 reopen하지 않는다는 문구가 유지된다.
- supersession이 rehearing이나 override round로 오독되지 않도록 wording이 고정된다.
- writer/runtime authority migration이 없었다는 boundary가 남는다.

---

## 9. Phase 7 — Closeout

**목적:** round의 허용 문장과 금지 문장을 명시하고 terminal state를 좁게 봉인한다.

### 9-1. Pass closeout state

```text
closed_with_canonical_code_path_convergence_applied
```

이 상태는 `§7-1` 완료 조건이 모두 참일 때만 사용한다.

### 9-1-b. Handoff closeout state

```text
closed_with_distribution_handoff_to_next_round
```

이 상태는 아래 조건을 모두 만족할 때만 사용한다.

- hard invariant pass
- non-writer seal pass
- entrypoint surface guard pass
- artifact hash guard pass
- source / section / overlap exact-match target 중 하나 이상 미달
- mismatch 원인이 implementation overwrite 또는 artifact mutation이 아님

이 상태는 convergence pass closeout이 아니며, Phase 6 top-doc current-state reflection을 열지 않는다.

### 9-2-a. Pass closeout에서만 허용

- legacy structural reclassification default code path convergence 완료
- canonical dual-axis read default화 완료
- source/section overwrite 제거 완료
- legacy single-slot view explicit diagnostic-only 격리 완료
- observer artifact baseline regenerate 완료

### 9-2-b. Handoff closeout에서만 허용

- non-writer seal 유지 확인됨
- legacy overwrite 제거 여부 확인됨 또는 부분 확인됨
- default path convergence implementation은 진행됐으나 exact-match distribution closeout은 다음 round로 handoff
- top-doc current-state reflection 미개방

### 9-2-c. 양쪽 모두에서 허용 불가

- deployed closeout
- release readiness
- semantic carry adoption
- `quality_baseline_v4 -> v5`
- runtime validation completion
- writer authority migration

### 9-3. Non-reopen clause

이번 round는 아래를 자동으로 reopen하지 않는다.

- `2026-04-22` staged/static closeout
- `2026-04-23` EDPAS direct default entrypoint authority seal
- `2026-04-24` additive signal preservation closeout

current default-path authority artifact가 superseded되는 것은 위 closeout들의 결정을 뒤집는 reopen이 아니라, 후속 current-state 갱신으로만 읽는다.

### 9-4. Closeout gate

closeout은 아래 문장이 참이 될 때만 허용한다.

> default structural reclassification path는 이제 2026-04-24 dual-axis canonical observer model과 같은 읽기 계약을 직접 집행하며, 기존 writer/runtime/Lua/quality/publish 봉인선은 그대로 유지된다.

---

## 10. 권장 실행 순서

```text
Phase 0  opening seal + branch selection (`regenerate` 기본안)
Phase 1  pre-change snapshot + consumer scan
Phase 2  canonical read contract 문서 고정
Phase 3  legacy script 책임 분해 + code patch
Phase 4  canonical artifact topology 재정렬 + 새 hash 선언
Phase 5  validation gate
Phase 6  top docs 반영
Phase 7  closeout memo + non-reopen clause 기록
```

운영 규칙은 아래처럼 고정한다.

- contract 문서가 먼저다.
- Phase 2 pass 전에는 Phase 3 code mutation에 들어가지 않는다.
- Phase 4 이후에는 legacy default read point를 다시 current authority로 읽지 않는다.
- Phase 5 pass 전에는 top docs를 current-state로 갱신하지 않는다.

---

## 11. 최종 round reading

이번 round의 최종 reading은 아래 두 문장으로 고정한다.

> 이 round는 observer lane additive 확장 round가 아니다.  
> 이 round는 legacy structural reclassification default code path를 canonical dual-axis read model로 교체·수렴시키는 round다.

또한 아래 문장도 함께 봉인한다.

> writer/runtime authority, staged/workspace Lua parity, `ready_for_in_game_validation`, `quality_baseline_v4`, manual QA pending 상태는 이번 round의 성공과 무관하게 그대로 유지된다.
