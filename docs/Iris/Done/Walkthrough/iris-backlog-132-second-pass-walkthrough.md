# Iris Backlog 132 Second-Pass Walkthrough

_Last updated: 2026-04-01_

## 1. 목적

이 문서는 `docs/iris-backlog-132-second-pass-execution-plan.md`가 이 세션에서 실제로 어떻게 실행됐는지 한 번에 따라가기 위한 walkthrough다.

초점은 여섯 가지다.

- second pass의 authority baseline이 어디서 고정됐는가
- `Phase 0`부터 `Sprint 7`까지 실제로 무엇이 구현됐는가
- package/theme cohort execution이 어떤 수치로 runtime에 반영됐는가
- final residual `34`가 왜 미완료 queue가 아니라 hold inventory인가
- 실제 runtime reflection과 closeout 문서화가 어디까지 끝났는가
- 지금 남은 일이 `인게임 연결`이 아니라 `manual in-game validation`인지

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/iris-post-cleanup-integrated-roadmap-walkthrough.md`
- `docs/iris-backlog-132-second-pass-execution-plan.md`

## 2. 시작점과 끝점

이번 작업은 post-cleanup integrated roadmap의 first operational pass가 끝난 상태에서 시작했다.

시작 baseline:

- runtime rows: `2105`
- active / silent: `2060 / 45`
- runtime paths: `cluster_summary 1342 / identity_fallback 685 / role_fallback 78 / direct_use 0`
- residual backlog authority: `132`

이번 세션의 끝점은 다음과 같다.

- Phase 0 infrastructure 완료
- Sprint 1~7 execution 완료
- second-pass runtime reflection 완료
- final residual closure 완료
- closeout 문서 갱신 완료
- manual in-game validation pack 작성 완료

최종 snapshot:

- runtime rows: `2105`
- active / silent: `2084 / 21`
- runtime paths: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
- final residual hold inventory: `34`

즉, 이번 세션은 residual backlog `132`를 열린 execution queue로 남겨둔 것이 아니라, **실제 runtime 반영과 hold closure까지 끝낸 second-pass execution session**이었다.

## 3. 전체 흐름

실행 흐름은 크게 9단계였다.

1. `Phase 0`에서 baseline, bucket authority, work queue를 동결한다.
2. `Sprint 1`에서 PKG-1 본체와 painting cross-domain exception을 먼저 처리한다.
3. `Sprint 2`에서 PKG-2 current scope를 cohort 단위로 나눠 순차 처리한다.
4. `Sprint 3`에서 PKG-4 handgun/explosive tail을 정리한다.
5. `Sprint 4`에서 PKG-3B~3D follow-on reuse를 처리한다.
6. `Sprint 5`에서 deferred multiuse tail을 정리하고 남는 것은 hold로 넘긴다.
7. `Sprint 6`에서 selective net-new를 실행한다.
8. `Sprint 7`에서 late candidates를 반영하고 final residual hold taxonomy를 닫는다.
9. closeout 단계에서 `DECISIONS.md`, `ROADMAP.md`, validation pack을 갱신한다.

아래부터는 이 9단계를 순서대로 본다.

## 4. Phase 0: Execution Infrastructure

`Phase 0`의 역할은 second pass 전체를 같은 baseline과 같은 lane 규칙 위에 고정하는 것이었다.

핵심 산출물:

- `Iris/build/description/v2/staging/second_pass_backlog_132/phase0_infrastructure/second_pass_baseline_snapshot.md`
- `Iris/build/description/v2/staging/second_pass_backlog_132/phase0_infrastructure/second_pass_package_queue.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/phase0_infrastructure/second_pass_bucket_authority.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/phase0_infrastructure/cluster_creation_protocol.md`
- `Iris/build/description/v2/staging/second_pass_backlog_132/phase0_infrastructure/existing_cluster_catalog_snapshot.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/phase0_infrastructure/second_pass_work_queue.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/phase0_infrastructure/lane_split_report.md`

이 단계에서 고정된 핵심 수치는 다음과 같다.

- residual axis split: `generated 96 / missing 36`
- candidate families: `identity_fallback_active 84 / role_fallback_active 12 / role_fallback_silent 36`
- lane split: `reuse_extension 72 / cluster_mismatch 41 / net_new 19`
- sprint current scope: `32 / 37 / 7 / 11 / 13 / 13 / 19`

의미는 단순하다.

- 이후 sprint는 모두 `132` authority backlog만 소비한다.
- `generated 먼저`, `reuse 먼저`, `candidate/runtime 분리`, `baseline-delta gate`라는 운영 원칙이 여기서부터 실제 산출물로 고정됐다.
- `Base.Paintbrush` 같은 recheck-only row도 이 시점에 queue상 `Sprint 7`로 명시됐다.

## 5. Sprint 1: PKG-1 + Painting Cross-Domain Exception

`Sprint 1`은 cheap/reuse-heavy lane을 먼저 쳐서 `cluster_summary` 비율을 빠르게 끌어올리는 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint1_pkg1/pkg1_second_pass_candidate_patch.jsonl`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint1_pkg1/pkg1_cluster_extension_notes.md`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint1_pkg1/pkg1_delta_validation_report.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint1_pkg1/sprint1_runtime_summary.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint1_pkg1/runtime_reflection/runtime_reflection_report.json`

실행 결과:

- row freeze: `32`
- promote: `24`
- hold: `8`
- promoted clusters:
  - `painting_decoration 15`
  - `construction_material_supply 6`
  - `electronics_assembly 3`
- overall residual: `132 -> 108`

runtime delta:

- active / silent: `2060 / 45 -> 2060 / 45`
- cluster_summary: `1342 -> 1366`
- identity_fallback: `685 -> 662`
- role_fallback: `78 -> 77`
- introduced hard fail / warn: `0 / 0`

즉, Sprint 1은 new active를 늘린 sprint라기보다 **generated fallback을 cluster_summary로 치환한 첫 대량 semantic conversion sprint**였다.

## 6. Sprint 2: PKG-2 Theme Cohort Split

`Sprint 2`는 가장 큰 residual package를 한 번에 밀지 않고 cohort로 분해해 처리한 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint2_pkg2_theme_split/pkg2_theme_split.json`
- `.../music_2a/pkg2_music_runtime_summary.json`
- `.../sports_2b/pkg2_sports_runtime_summary.json`
- `.../gardening_2c/pkg2_gardening_runtime_summary.json`
- `.../fishing_fitness_2d/pkg2_fishing_fitness_runtime_summary.json`

cohort 결과:

| Cohort | Promote | 주요 cluster |
|------|--------:|------|
| `2A music` | `14` | `music_instrument_play` |
| `2B sports` | `9` | `sports_play_equipment` |
| `2C gardening` | `8` | `gardening_tool_use` |
| `2D fishing + fitness` | `6` | `fishing_gear_use`, `strength_training_equipment` |
| `2E multiuse` | deferred `10` | Sprint 5로 이월 |

Sprint 2 cumulative 결과:

- current scope execution: `37`
- deferred: `10`
- overall residual: `108 -> 71`

runtime delta:

- active / silent: `2060 / 45 -> 2064 / 41`
- cluster_summary: `1366 -> 1403`
- identity_fallback: `662 -> 629`
- role_fallback: `77 -> 73`
- introduced hard fail / warn: `0 / 0`

핵심 해석은 이렇다.

- `music / sports / gardening`은 generated-heavy cluster replacement로 닫혔다.
- `fishing + fitness`는 일부 `missing -> active` 전환을 실제로 만들었다.
- `multiuse`는 억지 승격 대신 deferred/hold lane으로 밀어냈다.

## 7. Sprint 3: PKG-4 Handgun / Explosive Tail

`Sprint 3`은 generated-only에 가까운 cheap cohort를 먼저 치는 최적화 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint3_pkg4/cluster_handgun_firearm_v1.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint3_pkg4/pkg4_runtime_summary.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint3_pkg4/pkg4_explosive_tail_patch.json`

실행 결과:

- promote: `6`
- hold: `1`
- promoted target: `Pistol / Pistol2 / Pistol3 / Revolver / Revolver_Long / Revolver_Short`
- hold carry-forward: `Molotov`
- overall residual: `71 -> 65`

runtime delta:

- active / silent: `2064 / 41 -> 2064 / 41`
- cluster_summary: `1403 -> 1409`
- identity_fallback: `629 -> 623`
- role_fallback: `73 -> 73`
- introduced hard fail / warn: `0 / 0`

즉, Sprint 3은 low-row/high-payoff semantic cleanup이었다.

## 8. Sprint 4: PKG-3B~3D Follow-On Reuse

`Sprint 4`는 unclassified follow-on을 새 세계를 열지 않고 기존 family reuse로 닫는 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint4_followon_pkg3b_3d/pkg3_followon_reclass.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint4_followon_pkg3b_3d/pkg3_followon_patch_summary.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint4_followon_pkg3b_3d/pkg3_followon_runtime_summary.json`

실행 결과:

- promote: `8`
- hold: `4`
- promoted clusters:
  - `campfire_setup 4`
  - `vehicle_service_tool_use 4`
- overall residual: `65 -> 57`

runtime delta:

- active / silent: `2064 / 41 -> 2067 / 38`
- cluster_summary: `1409 -> 1417`
- identity_fallback: `623 -> 623`
- role_fallback: `73 -> 65`
- introduced hard fail / warn: `0 / 0`

이 단계의 의미는 PKG-3 follow-on을 더 이상 `unclassified blob`로 남기지 않았다는 데 있다.

## 9. Sprint 5: Deferred Tails

`Sprint 5`는 일부 row를 promote하기보다, 억지 cluster를 만들지 않고 hold taxonomy로 분리하는 데 더 큰 의미가 있었다.

핵심 산출물:

- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint5_deferred/pkg2_multiuse_disposition.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint5_deferred/pkg5_patch_summary.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint5_deferred/pkg5_runtime_summary.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint5_deferred/sprint5_delta_validation_report.json`

실행 결과:

- target row count: `13`
- promote: `3`
- hold: `10`
- promoted cluster: `fishing_gear_use 3`
- overall residual: `57 -> 54`

runtime delta:

- active / silent: `2067 / 38 -> 2070 / 35`
- cluster_summary: `1417 -> 1420`
- identity_fallback: `623 -> 623`
- role_fallback: `65 -> 62`
- introduced hard fail / warn: `0 / 0`

즉, Sprint 5의 성공은 많은 promote가 아니라 **multiuse tail을 무리 없이 hold/disposition으로 닫은 것**이다.

## 10. Sprint 6: Selective Net-New

`Sprint 6`은 net-new 중에서도 domain이 자명하고 missing->active 확장이 분명한 row만 선별 실행한 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint6_selective_netnew/pkg6_candidate_patch_summary.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint6_selective_netnew/pkg6_runtime_summary.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint6_selective_netnew/pkg5_small_netnew_clusters.json`

실행 결과:

- target row count: `13`
- promote: `12`
- hold: `1`
- proposed clusters:
  - `animal_trapping 6`
  - `fire_ignition_tool 3`
  - `improvised_radio_communication 3`
- overall residual: `54 -> 42`

runtime delta:

- active / silent: `2070 / 35 -> 2076 / 29`
- cluster_summary: `1420 -> 1432`
- identity_fallback: `623 -> 617`
- role_fallback: `62 -> 56`
- introduced hard fail / warn: `0 / 0`

이 sprint는 generated semantic conversion과 missing runtime expansion을 같이 만들었지만, 둘을 같은 성과 지표로 섞지 않고 그대로 artifact에 분리해서 남겼다.

## 11. Sprint 7: Late-Candidate Closure and Final Hold Inventory

`Sprint 7`은 남은 current-scope row를 late candidate로 정리하고, 나머지는 모두 hold taxonomy로 닫는 구조적 closure 단계였다.

핵심 산출물:

- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_candidate_patch_summary.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_runtime_summary.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/second_pass_final_residual_inventory.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/second_pass_closure_report.md`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/pkg6_tail_disposition.md`

late candidate 결과:

- row freeze: `11`
- promote: `8`
- explicit hold: `3`
- proposed clusters:
  - `crop_treatment_spray 3`
  - `photo_capture_device 3`
  - `soil_input_material 2`

최종 closure 결과:

- overall residual: `42 -> 34`
- final hold taxonomy:
  - `HOLD_CLUSTER_DESIGN_PENDING 18`
  - `HOLD_DOMAIN_UNCLEAR 13`
  - `HOLD_STRUCTURAL 3`

runtime delta:

- active / silent: `2076 / 29 -> 2084 / 21`
- cluster_summary: `1432 -> 1440`
- identity_fallback: `617 -> 617`
- role_fallback: `56 -> 48`
- introduced hard fail / warn: `0 / 0`

즉, Sprint 7은 `남은 게 조금 남았다`가 아니라, **남은 것을 final hold inventory로 바꿔 execution queue를 닫은 단계**였다.

## 12. 최종 수치 변화

start baseline과 final runtime을 비교하면 변화는 아래와 같다.

| Metric | Start | Final | Delta |
|------|------:|------:|------:|
| rows | `2105` | `2105` | `0` |
| active | `2060` | `2084` | `+24` |
| silent | `45` | `21` | `-24` |
| cluster_summary | `1342` | `1440` | `+98` |
| identity_fallback | `685` | `617` | `-68` |
| role_fallback | `78` | `48` | `-30` |
| residual backlog | `132` | `34` | `-98` |

핵심 해석은 다음과 같다.

- `98`행이 second pass에서 실제 promote 또는 late-candidate closure로 소거됐다.
- 그중 `24`행은 `silent -> active` 또는 equivalent runtime expansion을 만들었다.
- 나머지 큰 부분은 active 상태를 유지한 채 `identity_fallback / role_fallback -> cluster_summary`로 치환됐다.

## 13. Runtime Reflection과 Closeout 문서화

second pass는 staging 산출물만 만들고 끝난 것이 아니다. 실제 runtime reflection과 closeout 문서화까지 이어졌다.

runtime reflection:

- current runtime path: `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`
- final reflection artifact: `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/runtime_reflection/runtime_reflection_report.json`
- `DECISIONS.md`에는 second-pass build/runtime closure, new baseline, final residual `34`, 그리고 후속 manual validation closeout note가 기록됐다.
- `ROADMAP.md`에는 `5-xy. Iris DVF 3-3 second-pass execution closure addendum`가 추가됐다.

manual validation 준비:

- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/second_pass_in_game_validation_pack.md`

이 validation pack은 Priority A/B/C 샘플을 고정한다.

- Priority A: `Lighter`, `Makeshift Radio`, `Camera`, `Compost Bag`, `Gardening Spray Can (Full)`
- Priority B: `Barbell`, `Garden Fork`, `Fishing Rod`, `Pistol`, `Car Battery Charger`
- Priority C: `Camera Film`, `Watering Can (Full)`, `Paint Brush`, `Watering Can`

이후 브라우저/위키 표면 smoke check에서 사용자가 정상 동작을 확인했고, 현재 문서 상태는 **manual in-game validation `pass_with_note`** 로 정리됐다. 다만 exhaustive sample logging까지 끝낸 full `pass`는 별도 QA 성격으로 남긴다.

## 14. 구현 entrypoint

이번 세션에서 second pass를 실제로 밀어 올린 핵심 스크립트는 아래와 같다.

- `Iris/build/description/v2/tools/build/report_second_pass_phase0_infrastructure.py`
- `Iris/build/description/v2/tools/build/report_second_pass_sprint1_row_freeze.py`
- `Iris/build/description/v2/tools/build/report_second_pass_sprint1_candidate_patch.py`
- `Iris/build/description/v2/tools/build/build_second_pass_sprint1_runtime_integration.py`
- `Iris/build/description/v2/tools/build/apply_second_pass_sprint1_runtime_reflection.py`
- `Iris/build/description/v2/tools/build/report_second_pass_sprint2_theme_split.py`
- `Iris/build/description/v2/tools/build/build_second_pass_sprint2a_music.py`
- `Iris/build/description/v2/tools/build/build_second_pass_sprint2b_sports.py`
- `Iris/build/description/v2/tools/build/build_second_pass_sprint2c_gardening.py`
- `Iris/build/description/v2/tools/build/build_second_pass_sprint2d_fishing_fitness.py`
- `Iris/build/description/v2/tools/build/build_second_pass_sprint3_pkg4.py`
- `Iris/build/description/v2/tools/build/build_second_pass_sprint4_followon.py`
- `Iris/build/description/v2/tools/build/build_second_pass_sprint5_deferred.py`
- `Iris/build/description/v2/tools/build/build_second_pass_sprint6_selective_netnew.py`
- `Iris/build/description/v2/tools/build/build_second_pass_sprint7_closure.py`

즉, 이번 round는 수동 메모 정리가 아니라 **build script + staged artifact + runtime reflection** 으로 끝까지 밀어붙인 execution session이었다.

## 15. 완료 판정

이번 walkthrough 기준 완료 판정은 다음처럼 읽는다.

- `Backlog 132 second-pass execution plan` 범위는 build/runtime 기준으로 완료
- final reflected runtime도 완료
- final residual hold inventory closure도 완료
- `DECISIONS.md` / `ROADMAP.md` closeout도 완료
- manual in-game validation `pass_with_note` 기록까지 완료

반대로 아직 별도 후속 과제로 남아 있는 것은 다음이다.

- final residual `34` 전체 재오픈이 아니라 `future_promote_condition`이 성숙한 hold subset만 선별 reopen
- 필요 시 validation pack 기준 exhaustive sample logging을 수행해 full `pass`로 승격
- semantic quality UI exposure 같은 장기 과제

## 16. 한 줄 결론

이번 세션은 residual backlog `132`에 대한 second pass를  
`baseline freeze -> sprint execution -> runtime reflection -> final hold closure -> closeout documentation`  
까지 실제로 끝낸 세션이었다.  
현재 상태는 roadmap closed with `pass_with_note`이고, 이후 reopen은 hold subset future round로만 진행한다.
