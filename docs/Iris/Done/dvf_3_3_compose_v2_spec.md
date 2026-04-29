# DVF 3-3 Compose V2 Spec

> 상태: draft v0.1  
> 기준일: 2026-04-10  
> 상위 기준: `docs/dvf_3_3_information_type_contract.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`  
> 실행 계획: `docs/iris-dvf-3-3-compose-contract-migration-execution-plan.md`  
> 관련 구현: `Iris/build/description/v2/tools/build/compose_layer3_text.py`

---

## 1. 목적

이 문서는 현행 `sentence_plan` 기반 조합기를 Phase C의 `body_plan` 기반 compose 계약으로 교체하기 위한 기준선을 정의한다.

핵심 변화는 아래와 같다.

- block/slot 양적 상한을 본문 계약의 중심에서 제거한다.
- 3계층 본문을 정보 유형 section 조합으로 구성한다.
- 기존 `interaction_*` 3 profile을 신규 6 profile로 migration한다.

이 문서는 runtime render 구조를 바꾸지 않는다.  
shipping artifact는 계속 flat string이다.

---

## 2. 입력 계약

compose v2의 입력은 아래 네 artifact로 고정한다.

```text
facts
  + body_source_overlay
  + decisions
  + profiles
  -> body_plan
  -> rendered flat string
```

입력 ownership은 아래처럼 분리한다.

- `facts`
  - item canonical facts
- `body_source_overlay`
  - 1/2/4계층 raw source를 직접 노출하지 않는 합헌적 cross-layer hint
- `decisions`
  - single-writer compose authority
- `profiles`
  - profile별 section 규약

compose는 raw layer source를 직접 읽으면 안 된다.

---

## 3. `body_plan` 구조

compose v2는 아래 section 명칭만 사용한다.

- `identity_core`
- `use_core`
- `context_support`
- `acquisition_support`
- `limitation_tail`
- `meta_tail`

운영 규칙은 아래처럼 고정한다.

- section은 `0..N`개 emitted 가능하다.
- section 존재 여부는 `facts + overlay + decisions + profiles`로 결정론적으로 판정한다.
- 슬롯이 `0`개인 section은 emitted section으로 계산하지 않는다.
- 같은 profile + 같은 입력이면 section 순서는 항상 동일해야 한다.

`meta_tail`은 예비 section이다.

- 현재 Phase C 핵심 quality 판정에는 직접 포함하지 않는다.
- 향후 rendered 구조화 또는 trace annotation용 확장 여지를 남긴다.

---

## 4. 정보 유형과 section 대응

Phase A 정보 유형과 Phase C section 대응은 아래처럼 고정한다.

| 정보 유형 | section |
|---|---|
| `identity` | `identity_core` |
| `classification_context` | `context_support` |
| `primary_use` | `use_core` |
| `acquisition` | `acquisition_support` |
| `limitation_characteristic` | `limitation_tail` |

Phase C 이후 문서에서는 section 명칭을 우선 사용한다.

---

## 5. profile 계약

신규 compose profile은 아래 여섯 종류로 고정한다.

| 프로파일 | 대상 | 필수 section | 선택 section |
|---|---|---|---|
| `tool_body` | 도구형 | `identity_core`, `use_core` | `context_support`, `acquisition_support`, `limitation_tail` |
| `material_body` | 재료형 | `identity_core`, `context_support` | `use_core`, `acquisition_support`, `limitation_tail` |
| `consumable_body` | 소비형 | `identity_core`, `use_core`, `limitation_tail` | `context_support`, `acquisition_support` |
| `wearable_body` | 착용형 | `identity_core`, `limitation_tail` | `context_support`, `acquisition_support`, `use_core` |
| `container_body` | 용기형 | `identity_core`, `use_core` | `context_support`, `limitation_tail`, `acquisition_support` |
| `output_body` | 변환/출력형 | `identity_core`, `context_support` | `use_core`, `limitation_tail`, `acquisition_support` |

모든 profile은 최소한 아래 메타를 가져야 한다.

- section 우선순위 리스트
- adequate 최소선
- strong 최소선
- section별 허용 source
- acquisition 보호 규칙

---

## 6. `sentence_plan` 폐기 대상

아래 항목은 compose v2의 authoritative contract에서 제거한다.

- `4블록/4문장 상한`
- `블록당 슬롯 수 상한 3`
- `slot_sequence`
- `interaction_*` profile 전제의 고정 sentence block

즉, `compose_profiles.json`의 현행 `sentence_plan`은 Phase C 이후 compatibility 대상이지 최종 기준이 아니다.

---

## 7. profile migration 계약

### 7-1. legacy 3 profile -> new 6 profile 기본 매핑

| 기존 profile | 기본 target | 분기 성격 |
|---|---|---|
| `interaction_tool` | `tool_body` | container/wearable/consumable 예외 가능 |
| `interaction_component` | `material_body` | standalone tool 예외 가능 |
| `interaction_output` | `output_body` | consumable/wearable 예외 가능 |

### 7-2. 자동 분기 원칙

자동 분기 조건은 아래 원칙만 허용한다.

- `facts` 및 `decisions`의 canonical enum 조합만 사용한다.
- 자연어 해석 기반 조건은 허용하지 않는다.
- enum 조합으로 표현되지 않는 경우는 수동 재분류 inventory로 보낸다.

현재 Phase C planning artifact는 아래 입력만 사용한다.

- `facts.identity_hint`
- `decisions.selected_role`
- `decisions.compose_profile`

### 7-3. identity family target 규칙

identity family target은 아래 규칙 파일에서 결정한다.

- `Iris/build/description/v2/data/compose_profile_identity_hint_rules.json`

이 규칙 파일은 `identity_hint enum -> new profile` 매핑만 가진다.

현재 planning evidence에서 대표적으로 아래 계열이 이미 수록돼 있다.

- `가방 -> container_body`
- `의류 -> wearable_body`
- `식품 -> consumable_body`
- `재료 -> material_body`
- `근접 무기 -> tool_body`
- `폭발물 -> tool_body`
- `제작 무기 -> tool_body`

### 7-4. selected role target 규칙

selected role target은 legacy interaction-cluster role을 임시 canonical target으로 읽는다.

- `tool -> tool_body`
- `material -> material_body`
- `output -> output_body`

### 7-5. precedence 규칙

identity family target과 selected role target이 충돌하면 silent auto-resolution을 금지한다.  
명시적 precedence artifact가 필요하다.

현재 draft precedence rule은 아래 파일에 둔다.

- `Iris/build/description/v2/data/compose_profile_conflict_precedence_rules.json`

현재 초안은 아래처럼 읽는다.

- 기본 방향: `identity_family_target`
- 단, identity family 우선 적용 대상은
  - `consumable_body`
  - `wearable_body`
  - `container_body`
- 그 외 충돌은 `selected_role_precedence`로 정리한다.

즉, tool/material/output 계열은 아직 legacy role 신호를 더 보수적으로 존중한다.

---

## 8. migration planning artifact

Phase C planning evidence는 아래 artifact로 고정한다.

- inventory
  - `compose_profile_migration_inventory*.jsonl`
  - `compose_profile_migration_summary*.json`
- precedence draft
  - `compose_profile_precedence_draft*.resolved*.jsonl`
  - `compose_profile_precedence_draft*.summary*.json`
- resolution preview
  - `compose_profile_resolution_preview*.jsonl`
  - `compose_profile_resolution_preview*.summary*.json`
- body-plan v2 preview
  - `dvf_3_3_rendered_v2_preview*.json`
  - `dvf_3_3_rendered_v2_preview*.summary*.json`
- pilot corpus
  - `dvf_3_3_body_plan_v2_pilot_corpus*.jsonl`
  - `dvf_3_3_body_plan_v2_pilot_corpus*.summary*.json`
- blocker inventory
  - `dvf_3_3_body_plan_v2_blockers*.jsonl`
  - `dvf_3_3_body_plan_v2_blockers*.summary*.json`
- role-fallback hollow handoff
  - `role_fallback_hollow_source_expansion_backlog.json`
  - `role_fallback_hollow_source_expansion_backlog.md`
  - `role_fallback_hollow_followup_split.json`
  - `role_fallback_hollow_followup_split.md`
  - `role_fallback_hollow_reuse_candidate_facts.jsonl`
  - `role_fallback_hollow_policy_revisit_inventory.json`
  - `role_fallback_hollow_followup_execution_inputs.summary.json`
  - `role_fallback_hollow_c1b_reuse_package/*`
  - `role_fallback_hollow_policy_review/*`
  - `role_fallback_hollow_c1b_reuse_promotion_preview/*`
  - `role_fallback_hollow_residual_after_c1b_reuse.json`
  - `role_fallback_hollow_residual_after_c1b_reuse.md`
  - `role_fallback_hollow_net_new_package/*`
  - `role_fallback_hollow_net_new_work_packages.json`
  - `role_fallback_hollow_net_new_work_packages.md`
  - `role_fallback_hollow_net_new_work_packages/*`
  - `role_fallback_hollow_followup_runbook.json`
  - `role_fallback_hollow_followup_runbook.md`
  - `staging/source_coverage/block_c/role_fallback_hollow_seed_package_index.json`
  - `staging/source_coverage/block_c/c1f_tool_use_recovery_package/*`
  - `staging/source_coverage/block_c/c1g_material_context_recovery_package/*`
  - `staging/source_coverage/block_c/role_fallback_hollow_local_evidence_index.json`
  - `staging/source_coverage/block_c/role_fallback_hollow_manual_second_pass_upgrades.json`
  - `staging/source_coverage/block_c/role_fallback_hollow_source_authoring_queue.json`
  - `staging/source_coverage/block_c/role_fallback_hollow_targeted_authoring_pack.json`
  - `staging/source_coverage/block_c/role_fallback_hollow_targeted_authoring_drafts_index.json`
  - `staging/source_coverage/block_c/role_fallback_hollow_targeted_source_promotion_drafts_index.json`
  - `staging/source_coverage/block_c/role_fallback_hollow_manual_search_pack.json`
  - `staging/source_coverage/block_c/role_fallback_hollow_targeted_source_merge_previews_index.json`

artifact 책임은 아래처럼 나뉜다.

- inventory
  - 어떤 row가 어떤 canonical signal로 분류 가능한지 보여준다.
- precedence draft
  - identity family / selected role 충돌을 어떻게 해소할지 보여준다.
- resolution preview
  - full-runtime 기준에서 migration이 어디까지 deterministic하게 닫히는지 보여준다.
- body-plan v2 preview
  - resolved profile이 실제 emitted section과 flat string으로 어떻게 materialize되는지 보여준다.
- pilot corpus
  - Phase C adversarial review와 Phase E-0 shim 비교에 사용할 deterministic sample set을 고정한다.
- blocker inventory
  - Phase E-0 unexpected delta가 남았을 때 source 부재와 policy exclusion을 분리해 보여준다.
- role-fallback hollow handoff
  - final contract preview에 남은 `role_fallback` hollow lane을 후속 source expansion 입력으로 분리한다.
  - 후속 lane를 `existing cluster reuse / policy revisit / net-new source expansion`으로 재분류한다.

2026-04-10 full-runtime planning evidence 기준 현재 preview 상태:

- `row_count = 1050`
- `resolved_count = 1050`
- `unresolved_count = 0`

2026-04-11 body-plan v2 full-runtime preview 기준 현재 snapshot:

- `row_count = 1050`
- `silent_count = 75`
- coverage-only candidate:
  - `strong = 386`
  - `adequate = 130`
  - `weak = 459`
- audit-adjusted decision preview:
  - structural verdict:
    - `clean = 565`
    - `flag = 485`
  - violation flag:
    - `BODY_LOSES_ITEM_CENTRICITY = 37`
    - `SECTION_COVERAGE_DEFICIT = 459`
  - `quality_state`:
    - `strong = 360`
    - `adequate = 130`
    - `weak = 485`
  - `publish_state`:
    - `exposed = 490`
    - `internal_only = 485`
- missing required section snapshot:
  - `limitation_tail = 578`
  - `context_support = 11`
- pilot corpus:
  - `selected_count = 48`
- E-0 delta gate snapshot:
  - `expected_delta = 975`
  - `unexpected_delta = 0`
  - `publish_compatibility_shim_applied = 37`
  - `blocker_count = 0`
  - shim은 explained weak regression row에만 적용된다.
  - final contract preview의 authoring debt는 별도로 남아 있다.
    - `BODY_LOSES_ITEM_CENTRICITY = 37`
    - profile split:
      - `container_body = 20`
      - `material_body = 11`
      - `tool_body = 6`
    - handoff artifact:
      - `preview_role_fallback_active_count = 37`
      - `hard_fail = too_generic_use 37 / role_fallback_too_hollow 37`
      - `all_rows_e0_shimmed = true`
      - follow-up split:
        - `existing_cluster_reuse_candidate = 20`
        - `policy_revisit_candidate = 2`
        - `net_new_source_expansion_candidate = 15`
      - reusable cluster:
        - `container_storage = 20` via `C1-B`
      - execution inputs:
        - `reuse_candidate_facts = 20`
        - `policy_revisit_inventory = 2`
      - package-ready handoff:
        - `C1-B reuse package = 20`
        - `policy review lane = 2`
      - dry-run promotion preview:
        - `20/20 weak -> strong`
        - `20/20 internal_only -> exposed`
      - post-C1-B residual handoff:
        - `residual_after_c1b_reuse = 17`
        - `policy_revisit_candidate = 2`
        - `net_new_source_expansion_candidate = 15`
      - residual execution packages:
        - `net_new package = 15`
        - `policy review memo = 2`
      - net-new work package split:
        - `C1-F tool_use_recovery = 6`
        - `C1-G material_context_recovery = 9`
        - `primary_use_only = 6`
        - `primary_use_plus_context_support = 9`
      - follow-up runbook:
        - `step1 existing_cluster_reuse = 20`
        - `step2 policy_revisit = 2`
        - `step3 net_new_source_expansion = 15`
      - source-expansion seed packages:
        - `C1-F seed package = 6`
        - `C1-G seed package = 9`
        - `seed package index = 2`
      - local evidence sweep:
        - `C1-F ready_for_targeted_source_writeup = 1`
        - `C1-G ready_for_targeted_source_writeup = 6`
        - `manual_signal_interpretation = 8`
      - manual second-pass upgrades:
        - `upgraded_to_targeted = 5`
        - `remaining_manual = 3`
        - `C1-F upgrade = 4`
        - `C1-G upgrade = 1`
      - source authoring queue:
        - `targeted_source_writeup_now = 12`
        - `manual_repo_search_first = 3`
      - targeted authoring pack:
        - `targeted rows = 12`
        - `local_evidence = 7`
        - `manual_second_pass_upgrade = 5`
      - targeted authoring drafts:
        - `C1-F = 5`
        - `C1-G = 7`
      - source promotion drafts:
        - `promotion candidates = 12`
        - `source.raw draft-only`
      - manual search pack:
        - `manual_repo_search_first = 3`
        - `C1-F = 1`
        - `C1-G = 2`
      - manual residual blocker memo:
        - `parked_pending_new_source_discovery = 3`
        - `C1-F parked = 1`
        - `C1-G parked = 2`
      - source merge previews:
        - `aggregate pass = 12`
        - `C1-F pass = 5`
        - `C1-G pass = 7`
      - source authority candidates:
        - `row_count = 15`
        - `promotion_ready_authority_candidate = 12`
        - `parked_pending_new_source_discovery = 3`
      - source replacement candidates:
        - `row_count = 15`
        - `ready = 12`
        - `carry_forward_parked = 3`
      - source replacement delta review:
        - `semantic_upgrade = 12`
        - `parked_metadata_carry_forward = 3`
        - `direct_use_added = 12`
        - `special_context_added = 11`
      - source promotion manifest:
        - `apply_ready_replacement = 12`
        - `carry_forward_parked = 3`
      - source promotion applied:
        - `package_count = 2`
        - `ready_replacement_row_count = 12`
        - `carry_forward_parked_row_count = 3`
      - post-block-c apply status:
        - `block_c_source_promoted = 12`
        - `parked_pending_new_source_discovery = 3`
        - `policy_review_pending = 2`
        - `policy_default_maintain_exclusion = 2`
        - `policy_historical_precedent_attached = 2`
      - policy outcome projection:
        - `recommended_branch = maintain_exclusion_confirmed`
        - `default_confirmed -> remaining_unresolved = 3`
        - `override_reopen -> C1-G = 2`
      - policy default closeout:
        - `policy_review_closed_maintain_exclusion = 2`
        - `total_closed = 14`
        - `remaining_unresolved_tail = 3`
      - residual tail handoff:
        - `parked_pending_new_source_discovery = 3`
        - `C1-F = 1 / C1-G = 2`
        - `reopen_only_if_non_translation_item_specific_requirement_is_found`
      - residual tail source-discovery round:
        - `row_count = 3`
        - `package_count = 2`
        - `execution_order = C1-F 1 -> C1-G 2`
        - `runtime_frozen_until_reopen_gate_clears`
      - residual tail source-discovery status:
        - `executed_row_count = 3`
        - `reopen_ready_count = 0`
        - `remain_parked_count = 3`
        - `pending_execution_row_count = 0`
        - `C1-F executed_remain_parked = camping.SteelAndFlint`
        - `C1-G executed_remain_parked = Base.ConcretePowder, Base.Yarn`
      - residual tail round closeout:
        - `round_execution_complete = true`
        - `executed_package_count = 2`
        - `carry_forward_hold_count = 3`
        - `next_lane = future_new_source_discovery_hold`
      - terminal status:
        - `baseline_residual_after_c1b_row_count = 17`
        - `block_c_source_promoted = 12`
        - `policy_review_closed_maintain_exclusion = 2`
        - `carry_forward_hold = 3`
        - `active_unresolved_count = 0`
      - terminal handoff:
        - `baseline_followup_row_count = 37`
        - `existing_cluster_reuse_preview_backed = 20`
        - `block_c_source_promoted = 12`
        - `policy_review_closed_maintain_exclusion = 2`
        - `carry_forward_hold = 3`
        - `runtime_row_count = 2105`
      - post-apply ready preview:
        - `package_count = 2`
        - `ready_preview_rows = 12`
        - `parked_carry_forward_rows = 3`
        - `direct_use_preserved = 12`
        - `special_context_preserved = 11`
        - `unexpected_legacy_hard_fail = 0`
      - downstream runtime handoff:
        - `post_c replacement delta = role_fallback -12 / direct_use +12`
        - `integrated runtime path = cluster_summary 1275 / identity_fallback 718 / role_fallback 100 / direct_use 12`
        - `projection_comparison = match`
        - `replacement runtime apply = 12`

위 snapshot은 planning evidence와 downstream handoff status를 함께 적은 것이다.  
runtime authoritative state는 listed `post_c` / `source_coverage_runtime` artifact가 따로 맡는다.

---

## 9. section emission 원칙

section emission은 아래 원칙을 따른다.

- 필수 section이라도 source slot이 `0`개면 emitted 실패다.
- emitted 판단은 slot count가 아니라 slot 존재 여부로 본다.
- section은 profile 우선순위 순서대로 평가한다.
- 같은 입력이면 항상 같은 section 순서가 나온다.

이 원칙은 quality contract의 adequate/strong 최소선과 직접 연결된다.

---

## 10. connector 범위

Phase C에서 허용하는 connector 작업은 아래까지만이다.

- literal connector 확장
- section 전환 connector 추가

이번 라운드에서 하지 않는 것은 아래다.

- josa-aware grammar engine
- 확률적 connector 선택
- runtime connector 보정

---

## 11. flat string rendering 규칙

shipping artifact는 계속 flat string이다.

render 규칙은 아래처럼 고정한다.

- emitted section이 `2개 이상`이면 section 사이에 항상 `\n\n` 삽입
- emitted section이 `0개 또는 1개`이면 `\n\n` 미삽입
- 조건부 부분 삽입 금지

즉, 줄바꿈 여부도 compose 내부의 임의 판단이 아니라 deterministic render rule이어야 한다.

---

## 12. 비목표

이 문서는 아래를 하지 않는다.

- overlay schema 정의
- audit flag 정의
- quality_state 최종 기계 규칙 정의
- Lua consumer UI 구조 변경
