# Iris Backlog 132 Second-Pass Execution Plan

> 상태: Revised Draft v0.3  
> 기준일: 2026-03-31  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 문서: `docs/iris-post-cleanup-status-model-runtime-adoption-backlog-expansion-execution-plan.md`, `docs/iris-post-cleanup-integrated-roadmap-walkthrough.md`  
> 기준 artifact: `Iris/build/description/v2/staging/post_cleanup_integrated_roadmap/phase3_runtime_integration/phase3_residual_backlog_aggregate.json`  
> 목적: first operational pass 이후 남은 residual backlog `132`를 package 단위 second pass로 처리하고, `identity_fallback / role_fallback` 의존을 줄이면서 `cluster_summary` 전환율을 production 방식으로 끌어올린다.

---

## 1. 실행 판정

- 이번 second pass는 새 semantic model을 설계하는 단계가 아니다.
- 본질은 residual `132`를 package 단위로 소거하면서 `fallback -> cluster_summary` 전환을 늘리는 **production expansion track**이다.
- 실행 골격은 **PKG 순차 집행**으로 고정한다.
- 단, 같은 도메인이 PKG 경계에 분산된 경우에 한해 **cross-PKG 합산**을 명시적 예외로 허용한다.
- 모든 sprint는 `validation -> runtime integration -> reflection -> in-game validation`까지 닫아야 완료로 본다.

## 2. 기준선과 authority 고정

현재 second pass의 authority baseline은 Phase 3 integrated runtime 종료 시점으로 고정한다.

### 2-1. runtime snapshot

| 지표 | 값 |
|------|---:|
| total rows | 2105 |
| active | 2060 |
| silent | 45 |
| cluster_summary | 1342 |
| identity_fallback | 685 |
| role_fallback | 78 |
| direct_use | 0 |

### 2-2. residual authority

| 항목 | 값 |
|------|---:|
| residual backlog | 132 |
| authority artifact | `phase3_residual_backlog_aggregate.json` |

### 2-3. residual package split

| package | original | residual |
|---------|---------:|---------:|
| PKG-1 | 49 | 29 |
| PKG-2 | 52 | 47 |
| PKG-3A~3J | 40 | 32 |
| PKG-4 | 17 | 7 |
| PKG-5 | 14 | 13 |
| PKG-6 | 6 | 4 |

### 2-3-b. PKG-3 sub-package carry-forward

| sub-pkg | original | first-pass promoted | residual | second-pass assignment | note |
|---------|---------:|--------------------:|---------:|------------------------|------|
| PKG-3A | 6 | 3 | 3 | Sprint 1 cross-PKG construction merge | construction tail only |
| PKG-3B | 5 | 1 | 4 | Sprint 4 follow-on | vehicle service reuse |
| PKG-3C | 6 | 2 | 4 | Sprint 4 follow-on | camping / fire setup reuse |
| PKG-3D | 4 | 1 | 3 | Sprint 4 follow-on, then Sprint 7 hold review | water / container tail |
| PKG-3E | 6 | 0 | 6 | Sprint 7 late candidate or hold | not pulled into Sprint 2 |
| PKG-3F | 4 | 0 | 4 | Sprint 7 execution candidate | photo capture |
| PKG-3G | 3 | 1 | 2 | Sprint 7 hold-first review | household access |
| PKG-3H | 3 | 0 | 3 | Sprint 5 deferred tail | fishing small gear |
| PKG-3I | 2 | 0 | 2 | Sprint 7 hold-first review | textile craft |
| PKG-3J | 1 | 0 | 1 | Sprint 7 recheck against painting family | painting finish tool |

### 2-4. 산출물 루트

second pass의 staging 루트는 아래처럼 고정한다.

- `Iris/build/description/v2/staging/second_pass_backlog_132/phase0_infrastructure/`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint1_pkg1/`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint2_pkg2_theme_split/`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint3_pkg4/`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint4_pkg3_followon/`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint5_deferred_tails/`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint6_pkg5/`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_pkg6_closure/`

candidate artifact와 official runtime artifact는 이 단계에서도 절대 섞지 않는다.

## 3. 불변 원칙

- package 단위로 움직인다. cross-PKG 합산은 명시적 예외로만 연다.
- `generated::weak`를 `missing::weak`보다 먼저 친다.
- `reuse extension`을 `net-new cluster`보다 먼저 친다.
- unclassified는 먼저 triage한 뒤 구현한다.
- 3-3은 계속 **item-centric body**다.
- 3-3은 representative work context만 요약하고, 3-4 상세를 끌어오지 않는다.
- 설명은 source 검증 뒤에만 온다. `source -> cluster/role -> rendered` 순서를 뒤집지 않는다.
- candidate와 adopted runtime은 분리 보관한다.
- 검증은 절대값 hard gate가 아니라 **baseline-delta gate**를 기본으로 쓴다.
- 억지 cluster를 만들지 않는다. 자연스러운 도메인 단위가 없으면 hold로 남긴다.

## 4. Phase 0 — Execution Infrastructure

### 4-1. 목표

- second pass 전체가 같은 기준선과 같은 cluster 생성 규칙을 보도록 잠근다.

### 4-2. 작업

- runtime baseline을 `2105 / 2060 / 45`로 동결한다.
- residual backlog authority를 `132`로 동결한다.
- current runtime의 cluster catalog snapshot을 고정한다.
- cluster creation protocol을 문서로 고정한다.
- `phase3_residual_backlog_aggregate.json`의 132건을 master list로 잠근다.
- 각 row에 대해 `runtime_axis_current`, `candidate_family`, `backlog_bucket`, `mapping_reason`, `source_package_id`, `primary_classification`, `proposed_cluster`, `proposed_role`, `proposed_primary_use`를 일관 조회 가능한 work queue를 만든다.
- row를 아래 3개 lane으로 분류한다.

| lane | 의미 |
|------|------|
| reuse_extension_lane | 기존 cluster wording 확장으로 흡수 가능 |
| cluster_mismatch_lane | 기존 cluster family는 있으나 split 필요 |
| net_new_cluster_lane | 완전 신규 cluster 필요 |

- lane 매핑 규칙은 아래처럼 고정한다.
  - `reuse_extension_candidate`이고 안전한 family 재사용 경로가 있으면 `reuse_extension_lane`
  - bucket명에 `mismatch`가 포함되거나, triage 후 existing family는 있으나 wording/role이 맞지 않으면 `cluster_mismatch_lane`
  - `net_new_cluster_candidate`이거나 triage 후 안전한 family가 없으면 `net_new_cluster_lane`
  - `classify_then_assess`는 임시 recommended track일 뿐이며, triage 완료 뒤 반드시 위 3개 lane 중 하나로 강제 매핑한다.
- lane 내부 우선순위는 항상 `generated first -> missing second`로 고정한다.

### 4-3. cluster 신설 규칙

- cluster_id는 소문자 snake_case로 통일한다.
- 허용 role 값은 `tool`, `material`, `output`, `item`만 유지한다.
- `wording floor`는 기존 runtime `cluster_summary`의 평균 길이와 문체를 baseline으로 삼는 최소 품질 기준이다.
- 금지 패턴은 `레시피 목록`, `재료 열거`, `조건 나열`, `행동명/메뉴명`, `파밍 안내문`이다.
- 신규 cluster는 `cluster_id 중복`, `wording 유사도`, `기존 catalog family 충돌`을 모두 확인한 뒤에만 승인한다.

### 4-4. 산출물

- `second_pass_baseline_snapshot.md`
- `second_pass_package_queue.json`
- `second_pass_bucket_authority.json`
- `cluster_creation_protocol.md`
- `existing_cluster_catalog_snapshot.json`
- `second_pass_work_queue.json`
- `lane_split_report.md`

### 4-5. gate

- 이후 어떤 sprint를 열어도 baseline 비교 기준이 동일하다.
- "원래 residual이었는가"와 "이번 sprint에서 생긴 drift인가"를 즉시 구분할 수 있다.
- cluster 신설 규칙이 문서화되어 있다.

## 5. Sprint 개요

| sprint | 대상 | 성격 | 예상 promote |
|--------|------|------|-------------:|
| 0 | baseline + infrastructure | 기준선 동결 | - |
| 1 | PKG-1 core + painting domain exception + PKG-3A construction merge | generated-heavy / reuse-heavy | 15~20 |
| 2 | PKG-2 music / sports / gardening | mixed reuse / split | 12~18 |
| 3 | PKG-4 | explosive reuse + handgun net-new | 5~7 |
| 4 | PKG-3B~3D follow-on | classify-then-reuse | 4~8 |
| 5 | PKG-2 multiuse tail + deferred tails | hold 분리 중심 | 2~5 |
| 6 | PKG-5 | selective net-new | 5~9 |
| 7 | PKG-6 + residual closure | tail 정산 + late-candidate execution + hold taxonomy | 12~15 |

PKG-3E~3J의 세부 배정은 Section 2-3-b를 authority로 읽는다.  
명시된 sprint에서 닫히지 않는 잔여는 Sprint 7에서 execute-or-hold taxonomy로 정산한다.

## 6. Sprint 1 — PKG-1 Core + Painting Domain Exception + PKG-3A Construction Merge

### 목표

- 가장 cheap한 generated-heavy / reuse-heavy lane부터 쳐서 `cluster_summary` 비율을 빠르게 올린다.
- planning range: `15~20`
- `painting`은 도메인상 별도 lane으로 취급하되, 현재 authority artifact에서는 `source_package_id = PKG-1`, `primary_classification = Resource.4-E`로 기록되어 있으므로 PKG 재배정이 아니라 **explicit cross-domain exception**으로만 다룬다.

### 중심 bucket

| bucket | rows | 유형 | provenance note |
|--------|----:|------|-----------------|
| painting_cluster_absent | 15 | generated | PKG-1 authority, painting-domain exception |
| construction_material_context_absent | 5 | generated | PKG-1 core |
| remote_controller_cluster_absent | 3 | generated | PKG-1 core |
| adhesive_context_spans_multiple_workflows | 2 | generated | PKG-1 core |
| timekeeping_variant_not_safely_reusable | 2 | generated | PKG-1 core |
| PKG-3A construction tail | 3 | generated | explicit cross-PKG merge |
| small tail | 2 | mixed | PKG-1 core |

### 구현 순서

1. `painting_decoration` cluster를 우선 설계한다.
2. construction material은 `construction_prep` 확장 가능성을 먼저 검토한다.
3. 필요 시 `construction_material_supply`를 신규로 설계하되 PKG-3A construction tail `3`건과 provenance를 유지한 채 합산한다.
4. remote controller는 electronics 계열 기존 cluster 재사용 범위를 먼저 확인한다.
5. adhesive / timekeeping은 억지 승격 없이 hold 후보를 따로 남긴다.

### 산출물

- `pkg1_second_pass_candidate_patch.jsonl`
- `pkg1_cluster_extension_notes.md`
- `pkg1_delta_validation_report.json`

### gate

- PKG-1 residual이 눈에 띄게 감소한다.
- `painting` 축이 전체 residual 1위에서 내려간다.
- introduced hard fail `0`을 유지한다.
- introduced warn은 `0` 또는 사유가 설명 가능한 소수 증가로 제한한다.

## 7. Sprint 2 — PKG-2 Theme Cohort Split

### 목표

- 가장 큰 residual package `47`을 theme cohort로 잘라 순차 처리한다.
- planning range: `12~18`

### cohort 구성

| cohort | bucket | rows | gen/miss | 순서 |
|--------|--------|----:|----------|------|
| 2A | music_instrument_cluster_absent | 14 | 13/1 | 1st |
| 2B | sports_tool_cluster_mismatch | 9 | 9/0 | 2nd |
| 2C | gardening_tool_cluster_absent | 8 | 8/0 | 3rd |
| 2D | fishing_tool_cluster_absent + fitness_equipment | 6 | mixed | 4th |
| 2E | multiuse_tool_cluster_absent | 10 | mixed | Sprint 5 이월 |

### cohort별 운영 방침

- `2A music`: `music_instrument_play` cluster를 `tool` role로 설계한다. 무기 겸용 분류는 건드리지 않는다.
- `2B sports`: 기존 ball-play 중심 sports cluster를 그대로 늘리지 않고 **split cluster**로 처리한다.
- `2C gardening`: PKG-2의 generated `8`건만 처리한다. PKG-3E missing `6`건은 이번 sprint로 끌어오지 않는다.
- `2D fishing + fitness`: fishing은 PKG-3H와 통합 여부를 이 sprint에서 결정한다.
- `2E multiuse`: 강제 cluster 생성을 금지하고 Sprint 5 또는 hold로 넘긴다.
- PKG-3E `Gardening Inputs And Irrigation`은 `generated-first`, `reuse-first`, `follow-on-after-triage` 원칙을 지키기 위해 Sprint 7 late candidate / hold lane으로 남긴다.

### 산출물

- `pkg2_theme_split.json`
- `pkg2_music_cluster_spec.md`
- `pkg2_sports_split_spec.md`
- `pkg2_gardening_cluster_spec.md`
- `pkg2_delta_validation_report.json`

### gate

- music / sports / gardening 중 최소 2개가 runtime 반영 단계까지 닫힌다.
- `multiuse_tool_cluster_absent`는 억지 감소가 아니라 이월 또는 hold로 명시 처리된다.

## 8. Sprint 3 — PKG-4 Explosive Reuse + Handgun Net-New

### 목표

- generated-only이고 도메인이 자명한 cohort를 `classify-then-reuse` follow-on보다 먼저 닫는다.
- planning range: `5~7`

### 구현 순서

1. explosive device tail은 기존 `explosive_devices` 또는 `explosive_assembly` family 안으로 흡수한다.
2. handgun `6`행은 `ranged_firearm_combat` 확장 여부를 먼저 검토한 뒤 별도 cluster 필요 시 `handgun_firearm`을 설계한다.
3. wording은 "한 손으로 사용하는 소형 화기" 수준에서 멈춘다. 무기 운용 상세는 쓰지 않는다.

### 산출물

- `pkg4_explosive_tail_patch.json`
- `cluster_handgun_firearm_v1.json`
- `pkg4_delta_validation_report.json`

### gate

- handgun backlog `6`행이 해소되거나, 최소한 승인 가능한 설계 spec이 고정된다.
- explosive tail은 기존 family 안으로 흡수된다.

## 9. Sprint 4 — PKG-3B~3D Follow-On

### 목표

- unclassified follow-on 중 already-triaged reuse lane을 안전하게 reverse-apply한다.
- planning range: `4~8`

### 대상

| sub-pkg | residual | 방향 |
|---------|---------:|------|
| 3B Vehicle Service Utility | 4 | `vehicle_running_gear`, `fuel_handling` reuse |
| 3C Camping And Fire Setup | 4 | `field_shelter_setup`, `weather_cover_use` wording broaden |
| 3D Water And Container Handling | 3 | filled-water variant 중심 최소 커버 |

### 운영 원칙

- 새 세계를 여는 sprint가 아니다.
- 먼저 `classify`, 그 다음 `reuse`.
- PKG-3A construction tail은 이미 Sprint 1에서 cross-PKG merge로 선처리했으므로 여기서 중복 배정하지 않는다.

### 산출물

- `pkg3_followon_reclass.json`
- `pkg3B_to_3D_candidate_patch.jsonl`
- `pkg3_delta_validation_report.json`

### gate

- PKG-3 follow-on이 더 이상 단일 unclassified blob로 남지 않는다.
- PKG-3E~3J carry-forward만 명시적 후반 잔여로 남는다.

## 10. Sprint 5 — Deferred Tails and Multiuse Disposition

### 목표

- Sprint 2에서 미룬 multiuse와 fishing/fitness tail을 억지 cluster 없이 정리한다.

### 핵심 판정

- `Crowbar`, `Broom`류는 `general_utility_tool` 가능성을 검토하되, 대표 맥락이 빈약하면 hold로 둔다.
- `CanoePadel`류는 `watercraft_paddling` 가능성을 검토하되, 도메인 응집이 약하면 hold로 둔다.
- fishing tail은 Sprint 2 판단을 이어받아 독립 cluster 또는 existing fishing family 편입 여부를 닫는다.

### 산출물

- `pkg2_multiuse_disposition.json`
- `sprint5_delta_validation_report.json`

### gate

- multiuse 잔여는 `promote` 또는 `hold reason`으로 전부 disposition된다.
- "전부를 하나의 cluster로 묶는다"는 경로는 열지 않는다.

## 11. Sprint 6 — PKG-5 Selective Net-New

### 목표

- net-new 비중이 높은 tail을 전수 실행하지 말고, 도메인이 자명하고 coverage 이득이 큰 것만 선별 실행한다.
- planning range: `5~9`

### cohort 우선순위

| cohort | rows | gen/miss | 방향 |
|--------|----:|----------|------|
| trap tools | 6 | 6/0 | 실행 |
| ignition / firestarter | 3 | 0/3 | 실행 |
| improvised radio | 3 | 0/3 | 실행 |
| full kettle reuse | 1 | mixed | hold 검토 |

### 산출물

- `pkg5_small_netnew_clusters.json`
- `pkg5_delta_validation_report.json`

### gate

- net-new cluster는 자명한 소규모 cohort만 연다.
- `1~2`건짜리 어색한 cluster는 hold로 넘긴다.

## 12. Sprint 7 — PKG-6 and Residual Closure

### 목표

- small tail과 hold taxonomy를 정리해 second pass를 구조적으로 닫는다.
- PKG-3E~3J carry-forward 중 earlier sprint에서 닫히지 않은 잔여를 execute-or-hold taxonomy로 정산한다.
- planning range: `12~15`
- 이 sprint의 기대치는 PKG-6 core 정산만이 아니라 `photo_capture 4`, `gardening_inputs_and_irrigation 6`, `painting_finish recheck 1` 같은 late candidate execution까지 포함한 값이다.

### 추가 선별 실행 후보

| 대상 | rows | gen/miss | 판정 |
|------|----:|----------|------|
| photo_capture | 4 | 0/4 | 실행 우선 |
| gardening_inputs_and_irrigation | 6 | 0/6 | late candidate, 아니면 hold |
| painting_finish_recheck | 1 | 1/0 | recheck-only, painting family 흡수 가능성 재판정 |

### 기본 hold taxonomy

| hold code | 정의 |
|-----------|------|
| HOLD_CLUSTER_DESIGN_PENDING | 설계 가능하지만 이번 round에서는 비효율 |
| HOLD_DOMAIN_UNCLEAR | 자연스러운 도메인 단위가 없어 강제 cluster 불가 |
| HOLD_STRUCTURAL | 기존 cluster에 안전하게 편입되지 않음 |

### 최종 산출물

- `pkg6_tail_disposition.md`
- `second_pass_final_residual_inventory.json`
- `second_pass_closure_report.md`

### closure 기준

- 모든 sprint gate가 통과한다.
- 남은 residual은 item별 hold 사유와 재개 조건을 가진다.
- final runtime snapshot과 delta가 기록된다.
- 후속 `DECISIONS.md` / `ROADMAP.md` 갱신 입력이 준비된다.

## 13. 공통 Sprint 절차

모든 sprint는 아래 10단계를 동일하게 따른다.

| step | 이름 | 설명 |
|------|------|------|
| 1 | Row Freeze | 이번 sprint 대상 row 잠금 |
| 2 | Source Audit | reuse / mismatch / net-new 재확인 |
| 3 | Cluster Spec | cluster_id, wording floor, role, exclusion 작성 |
| 4 | Facts Check | identity_hint, acquisition_hint 확인 및 보충 |
| 5 | Candidate Patch | proposed cluster/role/primary_use 생성 |
| 6 | Local Validation | baseline-delta 기준 검증 |
| 7 | Runtime Integration | 통과 candidate만 staged runtime 반영 |
| 8 | Reflection | staged와 deployed Lua 일치 확인 |
| 9 | In-Game Validation | 툴팁/패널 실제 노출 sampling 확인 |
| 10 | Residual Recount | residual 재계산 및 queue 재정렬 |

## 14. 검증 규칙

매 sprint 종료 시 아래 항목을 반드시 다시 센다.

- baseline-delta 판정은 `introduced hard fail 0`을 유지하고, `introduced warn`은 `0` 또는 사유가 설명 가능한 소수 증가만 허용한다.
- active / silent 총량
- `cluster_summary` 증가량
- `identity_fallback`, `role_fallback` 감소량
- sprint 대상 외 unexpected drift
- 3-3 문장의 item-centric 유지 여부
- 대상 외 row 본문 변경 여부
- row count `2105` 보존 여부

금지 사항은 아래처럼 고정한다.

- 문장이 좋아 보인다는 이유만으로 runtime 반영
- bucket 규모만 보고 억지 cluster 생성
- multiuse를 공통점이 없는데도 하나로 묶기
- 3-4 상세를 3-3 본문으로 가져오기
- package 순서를 무시하고 net-new부터 열기
- semantic 개선과 runtime 확장을 같은 성과로 합산하기

## 15. 운영 지표

second pass의 성공은 `max promote`가 아니라 **quality-preserving promote**로 판정한다.

아래 수치는 source audit와 split 결과를 거치기 전의 **현재 planning range**이며 closure gate가 아니다.  
특히 `new clusters` 수는 목표가 아니라 부산물이고, cross-sprint merge나 hold release 여부에 따라 sprint별 band와 기계적으로 일치하지 않을 수 있다.

### 기대 구간

| 지표 | 최종 예상 |
|------|----------:|
| promoted cumulative | 55~82 |
| residual | 50~77 |
| active | 약 2070~2078 |
| cluster_summary | 약 1397~1424 |
| identity_fallback | 약 615~640 |
| new clusters | 8~12 |

### 해석 규칙

- `generated -> cluster_summary`는 semantic 개선이다.
- `missing -> active`는 runtime coverage 확장이다.
- 두 성과는 같은 수치처럼 합산하지 않는다.

## 16. 즉시 착수 순서

실제 집행은 아래 순서로 시작한다.

1. Phase 0 baseline freeze와 cluster catalog snapshot을 먼저 만든다.
2. `phase3_residual_backlog_aggregate.json`에서 132 master list와 lane split work queue를 생성한다.
3. PKG-1 core 중 `painting` explicit domain exception과 `construction material` lane을 첫 sprint scope로 잠근다.
4. Sprint 1의 painting-domain exception provenance 규칙과 PKG-3A construction merge provenance 규칙을 동시에 문서화한다.
5. 첫 sprint부터 baseline-delta validation report 템플릿을 공용 형식으로 고정한다.

이 문서는 second pass를 설계 논쟁이 아니라 **반복 가능한 package execution 체계**로 밀어붙이기 위한 기준 문서다.
