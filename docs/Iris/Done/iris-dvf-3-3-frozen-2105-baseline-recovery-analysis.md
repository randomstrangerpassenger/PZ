# Iris DVF 3-3 Frozen 2105 Baseline Recovery Analysis

> 상태: Analysis artifact  
> 기준일: 2026-05-13  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 관련 round: `resolver_compatibility_mapping_cleanup_round`  
> machine summary: `Iris/build/description/v2/staging/compose_contract_migration/resolver_compatibility_mapping_cleanup_round/phase1_baseline/frozen_2105_baseline_recovery_assessment.json`

---

## 1. Objective

이 분석의 목적은 resolver compatibility mapping cleanup을 안전하게 검증할 수 있는 frozen `2105` 기준면을 현재 checkout에서 다시 세울 수 있는지 판정하는 것이다.

분석 대상은 cleanup 문제 자체가 아니라, cleanup 전후 `rendered delta = 0`, Lua hash unchanged, resolver default reach `0`, `selected_role` bridge 영향도를 governance evidence로 측정할 수 있는 byte-level authority baseline의 복원 가능성이다.

---

## 2. Verdict

현재 checkout만으로는 frozen `2105` baseline을 세울 수 없다.

결론은 `blocked_missing_byte_level_frozen_2105_baseline`이다.

문서 readpoint는 historical authority로 유효하지만 byte-level baseline 대체물로는 불충분하다. cleanup 검증에는 실제 row artifact, summary, staged Lua, readiness queue, metadata migration dry-run/post-apply/closeout report가 필요하다.

---

## 3. Six-Point Assessment

### 3-1. Baseline authority artifact

판정: 문서값만으로는 부족하고 byte-level artifact가 필요하다.

유효한 문서 readpoint:

* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/Iris/Done/Walkthrough/iris-dvf-3-3-adapter-native-body-plan-metadata-migration-round-walkthrough.md`

하지만 이 문서들은 counts와 lifecycle을 복원할 뿐, cleanup 전후 delta를 계산할 row bytes와 hash authority를 제공하지 않는다.

필요하지만 현재 checkout에서 없는 핵심 artifact:

* `phase_d_e_current_session/dvf_3_3_rendered_v2_preview.2105.json`
* `phase_d_e_current_session/dvf_3_3_rendered_v2_preview.2105.summary.json`
* `body_plan_v2_lua_bridge_report.2105.json`
* readiness queue `2006 / 78 / 21`
* metadata migration Phase 5 dry-run report
* metadata migration Phase 7 post-apply report
* metadata migration Phase 9 closeout

### 3-2. 2105 source reconstruction input

판정: 필요한 입력이 일부만 남아 있고, post-migration baseline 재구성에는 부족하다.

현재 있는 것:

* pre-migration facts: `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/dvf_3_3_facts.integrated.jsonl`
* pre-migration decisions: `Iris/build/description/v2/staging/interaction_cluster/source_coverage_runtime/dvf_3_3_decisions.integrated.jsonl`
* `Iris/build/description/v2/data/compose_profiles_v2.json`
* identity/precedence rule files

하지만 해당 2105 source candidate는 active/silent split이 `2030 / 75`이고, `2105` decision row 전부가 legacy `interaction_*` labels를 가진 pre-migration input이다. cleanup baseline target인 post-migration `active 2084 / silent 21`, active native profile `2084` 상태가 아니다.

현재 없는 핵심:

* `2105` row `body_source_overlay`
* post-migration decisions baseline
* metadata migration artifact tree

현재 checkout의 `layer3_body_source_overlay.jsonl`은 `6` rows뿐이며 hash는 `B9AF509335D46982E795AECED76D6133F1309CE45FFAF1E66D0B3B113AC02EB1`이다.

### 3-3. body_plan v2 preview regeneration

판정: 현재 입력으로는 재생성 불가하다.

목표 count:

```text
total = 2105
active = 2084
silent = 21
resolution distribution = 720 / 46 / 136 / 288 / 894
```

현재 probe failure:

```text
ValueError: Missing body_source_overlay row for active item 'Base.223Box'
```

원인은 default `body_source_overlay`가 `6` rows뿐이라 2105 active set을 커버하지 못하기 때문이다.

### 3-4. Metadata migration post-state restoration

판정: 현재 checkout에서 복원 불가하다.

목표 상태:

```text
active_old_profile_count = 0
active_native_profile_count = 2084
silent_old_profile_count = 21
legacy_fallback_target_count = 0
canonical_row_legacy_field_residue_count = 0
```

필요하지만 없는 artifact:

* readiness queue `execution_queue_non_fallback_active.2006.jsonl`
* readiness queue `execution_queue_fallback_dependent_active.78.jsonl`
* `silent_metadata_inventory.21.jsonl`
* `legacy_field_namespace_contract.json`
* Phase 5 dry-run verification report
* Phase 7 post-apply verification report
* Phase 9 closeout pass JSON

따라서 docs에 적힌 migration result를 기준값으로 읽을 수는 있어도, cleanup 검증용 byte-level baseline으로 사용할 수는 없다.

### 3-5. Rendered / Lua / runtime invariant baseline

판정: invariant 기준면을 byte-level로 세울 수 없다.

목표 invariant:

```text
rendered delta = 0
Lua hash = 0390272b93a933d7e53bba996b322ffbdd9fc905585bec03fc78d338f469f062
runtime state = ready_for_in_game_validation
bridge split = internal_only 617 / exposed 1467
```

현재 문제:

* checkout의 `full_runtime/IrisLayer3Data.body_plan_v2.staged.lua` hash는 `9412BCD2316C02F357D1196F6B80EE0FCAEDC0F7B06C962240C16B3276F85277`이다.
* archive Lua candidate hash는 `52C848E81105E62AD815B22C50D7D338C2A086F9A743213B3FBF55E0ACEA081E`로 sealed hash와 다르다.
* source coverage backup Lua hash는 `A108F3E5BEE473D00F4CB7DC63BADE3374670A21BC0D9B4049EDB4CA179D3162`로 sealed hash와 다르다.
* live workspace path `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`는 현재 없다.

따라서 Lua/runtime invariant는 문서값으로만 참조 가능하고 byte-level guard로는 사용할 수 없다.

### 3-6. selected_role bridge and resolver mapping impact

판정: frozen baseline 위에서 측정할 수 없으므로 governance evidence로 사용할 수 없다.

목표:

```text
selected_role_precedence = 288
selected_role_target = 894
default path legacy fallback reach = 0
cleanup rendered delta = 0
```

현재 가능한 것은 6-row sample 진단뿐이다. 해당 sample의 `selected_role_precedence` / `selected_role_target` count는 cleanup authority evidence가 아니다.

현재 diagnostic report는 default resolver static path에 `LEGACY_PROFILE_FALLBACK` call edge가 남아 있음을 기록하지만, 이 영향도를 cleanup 기준으로 확정하려면 frozen `2105` post-migration baseline의 dynamic measurement가 필요하다.

---

## 4. Do Not Use As Baseline

다음은 frozen cleanup baseline으로 사용하면 안 된다.

* 문서 count summary만으로 구성한 synthetic baseline
* 현재 `6` row data sample
* pre-migration `interaction_cluster/source_coverage_runtime` 2105 source pair
* archive `p0-2` Lua artifact
* source coverage runtime backup Lua
* later distribution/handoff summaries

---

## 5. Required Recovery Path

Preferred path:

1. 다른 worktree 또는 backup에서 누락된 byte-level staging tree를 복원한다.
2. 최소 복원 대상은 `phase_d_e_current_session`, `adapter_native_body_plan_readiness_round`, `adapter_native_body_plan_metadata_migration_round`이다.
3. 복원 후 hash/count를 문서 readpoint와 대조하고 frozen baseline seal을 다시 생성한다.

Fallback path:

1. 별도 baseline reconstruction round를 연다.
2. full `2105` `body_source_overlay`를 복구하거나 재생성한다.
3. body_plan v2 preview를 `2105 / 2084 / 21` 목표로 재생성한다.
4. readiness queue `2006 / 78 / 21`을 재생성한다.
5. metadata migration dry-run과 post-apply verification을 다시 수행한다.
6. rendered delta `0`, sealed Lua hash, runtime state, bridge split을 byte-level로 다시 봉인한다.

---

## 6. Cleanup Gate

Resolver compatibility mapping cleanup은 frozen `2105` byte-level baseline이 복원 또는 재생성되어 seal되기 전에는 Phase 1 blocked 상태를 넘어가면 안 된다.

이 상태에서 resolver guard patch, namespace amendment, selected_role 영향도 판정, rendered/Lua delta 검증을 진행하면 cleanup evidence가 아니라 sample 또는 추정 기반 변경이 된다.

