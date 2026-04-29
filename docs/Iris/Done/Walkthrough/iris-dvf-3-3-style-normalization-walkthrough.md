# Iris DVF 3-3 Style Normalization Walkthrough

_Last updated: 2026-04-05_

## 1. 목적

이 문서는 [iris-dvf-3-3-style-normalization-execution-plan.md](C:/Users/MW/Downloads/coding/PZ/docs/iris-dvf-3-3-style-normalization-execution-plan.md)가 이번 세션에서 실제로 어떻게 실행됐는지 한 번에 따라가기 위한 walkthrough다.

초점은 여섯 가지다.

- style normalization이 semantic 재판정이 아니라 post-compose surface layer로 어떻게 고정됐는가
- Phase 0 baseline scan부터 Phase 6 triage까지 실제로 어떤 수치와 artifact로 닫혔는가
- `G-01`, `F-01`이 어떤 근거로 활성화됐는가
- advisory lint가 어떻게 `active STYLE_WARN 0`까지 정리됐는가
- runtime authority, Lua bridge, manual in-game validation이 어떻게 closeout으로 이어졌는가
- 세션 말미에 드러난 `전지톱` 문구 이슈가 왜 style normalizer 문제가 아닌가

상위 기준은 다음 문서들이다.

- `docs/Philosophy.md`
- `docs/DECISIONS.md`
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/iris-dvf-3-3-style-normalization-execution-plan.md`

## 2. 시작점과 끝점

이번 작업은 second-pass closeout이 끝난 상태에서 시작했다.

시작 baseline:

- runtime rows: `2105`
- active / silent: `2084 / 21`
- path counts: `cluster_summary 1440 / identity_fallback 617 / role_fallback 48`
- runtime authority: `sprint7_overlay_preview.rendered.json`
- unresolved style layer: 없음

이번 세션의 끝점은 다음과 같다.

- `compose -> normalizer -> style linter -> rendered` 계층 구현 완료
- `G-01`, `F-01` 활성화 완료
- `L-01`, `L-02`, `L-04` advisory triage 완료
- current baseline 기준 `STYLE_WARN active hit 0`
- runtime authority/Lua bridge closeout 완료
- manual in-game validation pass 반영 완료
- style runtime status: `runtime_closed_pass`

즉, 이번 세션은 단순 초안 작성이 아니라 **style normalization execution, lint closure, runtime closeout, manual validation 반영까지 한 번에 닫은 세션**이었다.

## 3. 전체 흐름

실행 흐름은 크게 8단계였다.

1. execution plan을 실제 코드 구조와 reviewer feedback에 맞게 보정한다.
2. Phase 0에서 baseline scan과 family binding을 고정한다.
3. Phase 1에서 normalizer/linter 엔진과 rules skeleton을 구현한다.
4. Phase 3 dry run으로 postproc 흡수와 rule activation을 분리 검증한다.
5. Phase 2/6에서 lint hotspot을 줄이고 `ACCEPT / HOLD / exception` 판단으로 닫는다.
6. closeout packet과 sample review policy를 만들고 current baseline pass를 고정한다.
7. full runtime authority 기준으로 Lua bridge와 deployed runtime을 다시 검증한다.
8. manual in-game validation pass를 기록하고 이번 round를 종료한다.

아래부터는 이 8단계를 순서대로 본다.

## 4. Plan 보정: 모순 제거와 scope 고정

구현 전에 execution plan부터 실제 운영 가능한 형태로 다듬었다.

핵심 보정은 다음 네 가지였다.

- `byte-identical` gate를 두 단계로 분리
- family binding key를 `fact_origin + selected_cluster_contains`로 통일
- `manual_override_text_ko`는 `style rules skip + legacy postproc only`로 고정
- `STYLE_WARN 70%`를 hard gate가 아니라 pilot 목표치로 완화

이 보정의 의미는 단순하다.

- normalizer가 실제 문자열을 바꾸는데도 postproc-only와 byte-identical을 동시에 요구하는 모순을 제거했다.
- `tool 계열` 같은 새 semantic 축이 끼어들 여지를 없앴다.
- manual override surface를 사람이 통제하되 최소 postproc은 유지하게 했다.
- lint 운영 기준을 측정 가능한 형태로 바꿨다.

이 상태가 이후 구현의 헌법 역할을 했다.

## 5. Phase 0: Baseline Scan과 Rule Binding

baseline authority는 fixture가 아니라 full runtime snapshot으로 고정했다.

핵심 authority:

- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview.rendered.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview_facts.jsonl`

핵심 산출물:

- `Iris/build/description/v2/output/style_baseline_scan.json`
- `Iris/build/description/v2/staging/style/phase0_rule_binding/phase0_rule_binding.json`
- `Iris/build/description/v2/staging/style/phase0_rule_binding/phase0_rule_binding.md`

rule binding 결과는 다음처럼 닫혔다.

- `P-01 -> G-01 GLOBAL_CANDIDATE`
- `P-02A -> F-01 FAMILY_CANDIDATE`
- `P-04 -> LINT_ONLY`
- `P-05A -> LINT_ONLY`
- `P-06 -> LINT_ONLY`
- `P-02B / P-02C / P-03 / P-05B -> HOLD_ZERO_HIT`

current baseline scan에서 남아 있는 대표 pattern 수치는 다음과 같았다.

- `근접 전투`: `14`
- `~에서 발견된다`: `607`
- `동일 명사 반복 heuristic`: `166`

반대로 `겸용`, `함께 쓰는`, `함께 사용되는`, `주로 함께`, `~에 쓰이는 용도의`는 current rendered 기준 hit `0`이다. 이건 baseline scan이 무의미하다는 뜻이 아니라, **historical activation evidence가 이미 별도 artifact로 보존되고 current baseline에는 normalized surface가 반영된 상태**라는 뜻이다.

## 6. Phase 1~3: Engine 구현과 Dry Run 검증

핵심 구현 파일은 아래 경로에 추가되거나 갱신됐다.

- `Iris/build/description/v2/tools/style/normalizer.py`
- `Iris/build/description/v2/tools/style/linter.py`
- `Iris/build/description/v2/tools/style/baseline_scan.py`
- `Iris/build/description/v2/tools/style/phase0_rule_binding.py`
- `Iris/build/description/v2/tools/style/dry_run.py`
- `Iris/build/description/v2/tools/style/rules/global_rules.json`
- `Iris/build/description/v2/tools/style/rules/family_rules.json`
- `Iris/build/description/v2/tools/style/rules/lint_rules.json`
- `Iris/build/description/v2/tools/build/compose_layer3_text.py`
- `Iris/build/description/v2/run_interaction_cluster_pipeline.py`

여기서 중요한 것은 normalizer가 별도 장식층이 아니라 기존 compose 경로에 실제로 삽입됐다는 점이다.

- 기존: `compose -> postproc -> rendered`
- 현재: `compose -> normalizer(global/family/postproc) -> style linter -> rendered`

dry run은 두 단계로 닫았다.

### 6-1. postproc-only 흡수 검증

핵심 산출물:

- `Iris/build/description/v2/staging/style/phase3_dry_run/dry_run_summary.postproc_only.json`

결과:

- changed_count: `0`
- all_active_rows_byte_identical: `True`
- introduced hard fail / warn: `0 / 0`

즉, style rule을 전부 끈 상태에서는 새 normalizer가 기존 postproc-only 결과와 동일하게 동작한다.

### 6-2. historical rule activation 검증

핵심 산출물:

- `Iris/build/description/v2/staging/style/phase1_activation/phase1_activation_summary.json`
- `Iris/build/description/v2/staging/style/phase1_activation/phase1_activation_summary.md`
- `Iris/build/description/v2/staging/style/phase3_dry_run/dry_run_changed_review.g01_f01.md`

활성화 결과:

- activated rule ids: `G-01`, `F-01`
- changed_count: `18`
- applied_rule_counts: `G-01 18 / F-01 8`
- introduced hard fail / warn: `0 / 0`

의미는 명확하다.

- `G-01`은 global safe contraction으로 실제 변경 `18`건을 만들었다.
- `F-01`은 `identity_fallback + unknown` family phrase `8`건만 건드렸다.
- validation gate를 새로 깨지 않았다.

## 7. Phase 2~6: Advisory Lint를 실제로 닫는 과정

style lint는 처음부터 runtime gate가 아니라 advisory report였다. 하지만 advisory라고 해서 방치한 것은 아니다. 이번 세션의 중간 대부분은 `L-02`, `L-04`를 실제로 운영 가능한 수준까지 줄이는 작업이었다.

핵심 구현/분석 파일:

- `Iris/build/description/v2/tools/style/phase2_activation.py`
- `Iris/build/description/v2/tools/style/phase6_triage.py`
- `Iris/build/description/v2/tools/style/phase6_acquisition_phrase_breakdown.py`
- `Iris/build/description/v2/tools/style/style_lint_sample_review.py`
- `Iris/build/description/v2/tools/style/style_closeout_packet.py`

핵심 산출물:

- `Iris/build/description/v2/staging/style/phase2_activation/phase2_activation_summary.json`
- `Iris/build/description/v2/staging/style/phase6_triage/phase6_triage_summary.json`
- `Iris/build/description/v2/staging/style/phase6_triage/phase6_triage_summary.md`
- `Iris/build/description/v2/staging/style/closeout/style_closeout_packet.json`
- `Iris/build/description/v2/staging/style/closeout/style_closeout_packet.md`

정리 과정은 세 단계였다.

### 7-1. L-02 heuristic 보정

`L-02`는 처음에 문장 전체 repeated noun heuristic로 너무 넓게 잡혔다. 이를 문장 내 반복 기준으로 줄이고, acquisition-side exact phrase exception을 추가했다.

최종 상태:

- `matched_row_count: 0`
- `suppressed_row_count: 166`
- suppression reasons:
  - `accepted_seed_label_repeat_accessory: 68`
  - `accepted_seed_label_repeat_source_phrase: 98`

즉, 실제 awkward repeat를 잡는 용도는 유지하되, 의도된 acquisition phrase family는 예외로 명시했다.

### 7-2. L-04 discovery phrase 정리

`L-04`는 `~에서 발견된다`가 많다는 사실 자체보다, 어떤 형태가 어색한지를 분해하는 쪽으로 다뤘다. simple discovery shape 예외를 넣어 단일/쌍 source phrase를 suppress하고, multi-source discovery phrase만 dormant sensor로 남겼다.

최종 상태:

- `matched_row_count: 177`
- `matched_row_rate: 8.5%`
- threshold: `15%`
- `suppressed_row_count: 430`
- triggered: `False`

즉, `L-04`는 current baseline에서 더 이상 WARN을 발생시키지 않는다.

### 7-3. triage closure

최종 triage는 아래처럼 닫혔다.

- `L-01 = ACCEPT`
- `L-02 = ACCEPT`
- `L-04 = ACCEPT`

이 판단은 [phase6_triage_summary.md](C:/Users/MW/Downloads/coding/PZ/Iris/build/description/v2/staging/style/phase6_triage/phase6_triage_summary.md)에 그대로 남아 있다.

## 8. Current Baseline Closeout

lint와 dry run이 닫힌 뒤, closeout packet을 따로 만들었다.

핵심 산출물:

- `Iris/build/description/v2/staging/style/closeout/style_closeout_packet.json`
- `Iris/build/description/v2/staging/style/closeout/style_closeout_packet.md`

closeout packet의 핵심 수치는 다음과 같다.

- status: `closed_current_baseline_pass`
- active_rows: `2084`
- postproc_absorption_byte_identical: `True`
- historical_activation_changed_count: `18`
- historical_introduced_hard_fail_count: `0`
- historical_introduced_warn_count: `0`
- current_active_rules_idempotent: `True`
- current_style_warn_row_count: `0`
- lint_sample_review_selected_count: `0`

즉, current baseline 기준으로는 **style normalization layer가 더 이상 열려 있는 issue queue가 아니라 닫힌 운영 상태**로 들어갔다.

## 9. Runtime Authority Correction과 Static Runtime Closeout

이번 세션의 후반부에서 가장 중요한 기술적 정리는 `output/dvf_3_3_rendered.json`이 authority가 아니라는 점을 명시적으로 봉인한 것이다.

current workspace에는 두 rendered가 공존했다.

- fixture: `Iris/build/description/v2/output/dvf_3_3_rendered.json`
- authoritative full rendered: `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview.rendered.json`

fixture는 `6 rows`뿐이므로 runtime closeout authority가 될 수 없다. 그래서 full runtime authority를 sprint7 rendered로 고정하고, 그 기준으로 Lua bridge와 deployed runtime을 검증했다.

핵심 구현 파일:

- `Iris/build/description/v2/tools/style/style_runtime_closeout.py`

핵심 산출물:

- `Iris/build/description/v2/staging/style/runtime_closeout/style_runtime_closeout.json`
- `Iris/build/description/v2/staging/style/runtime_closeout/style_runtime_closeout_note.md`
- `Iris/build/description/v2/staging/style/runtime_closeout/style_runtime_lua_bridge_report.json`
- `Iris/build/description/v2/staging/style/runtime_closeout/style_runtime_report.json`
- `Iris/build/description/v2/staging/style/runtime_closeout/IrisLayer3Data.lua`

static runtime closeout 결과:

- authoritative entries: `2105`
- authoritative active rows: `2084`
- fixture entry count: `6`
- bridge source/runtime entry count: `2105 / 2105`
- runtime report status: `ready_for_in_game_validation`
- runtime report check count: `13`
- deployment action: `already_current`
- staged/deployed Lua hash: identical

이 단계의 의미는 단순하다.

- style normalization이 full runtime과 실제 Lua bridge를 깨지 않았다.
- deployed `IrisLayer3Data.lua`는 이미 staged full rendered와 같은 상태였다.
- 남은 것은 manual in-game validation뿐이었다.

## 10. Manual In-Game Validation과 Final Promotion

static runtime closeout 뒤에는 in-game 검증 가이드를 정리하고, user-confirmed pass를 closeout artifact에 반영했다.

reference pack:

- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/second_pass_in_game_validation_pack.md`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_in_game_validation_checklist.md`

manual validation 결과 산출물:

- `Iris/build/description/v2/staging/style/runtime_closeout/style_runtime_in_game_validation_result.json`
- `Iris/build/description/v2/staging/style/runtime_closeout/style_runtime_in_game_validation_result.md`

최종 상태:

- validation_date: `2026-04-04`
- status: `pass`
- reported_by: `user`
- basis: `all intended items displayed as expected in-game`
- surface_scope: `Iris context menu / Iris wiki panel / Iris browser`

이 결과를 반영해 runtime closeout도 최종적으로 승격됐다.

- 이전: `runtime_closed_except_in_game_validation`
- 최종: `runtime_closed_pass`

즉, 이번 세션에서 style normalization은 **current baseline closeout**만 닫은 것이 아니라 **runtime closeout과 manual validation까지 포함한 end-to-end pass**로 올라갔다.

## 11. 세션 말미 점검 메모: `전지톱`의 `맞춘다`

세션 마지막에는 `1-A 건설/제작`의 `전지톱` 문구가 왜 `자재를 가공하거나 맞출 때 쓴다`로 나오는지 점검했다.

핵심 확인 사항:

- `전기톱`은 `Base.Chainsaw`
- `전지톱`은 `Base.GardenSaw`
- `Base.GardenSaw`는 `Tool.1-A`
- 현재 selected cluster는 `construction_prep`

핵심 근거 경로:

- `lua/shared/Translate/KO/ItemName_KO.txt`
- `Iris/media/lua/client/Iris/Data/IrisData.lua`
- `Iris/build/description/v2/data/cluster_summary_templates.json`
- `Iris/build/description/v2/data/interaction_cluster_usecase_rules.json`
- `Iris/build/description/v2/staging/second_pass_backlog_132/sprint7_residual_closure/sprint7_overlay_preview_facts.jsonl`

판단은 다음과 같다.

- `맞춘다`는 style normalizer가 집어넣은 표현이 아니다.
- 이는 `construction_prep` 공용 template의 `자재를 가공하거나 맞출 때`라는 범용 문구에서 왔다.
- 따라서 이 이슈는 style normalization closeout의 잔여가 아니라, `construction_prep` compose template가 saw 계열에 너무 넓게 일반화된 문제다.
- 이 세션에서는 원인 확인까지만 했고, template wording 변경은 아직 하지 않았다.

즉, `전지톱` 문구 이슈는 runtime/style layer의 실패가 아니라 **compose template specificity 이슈**로 보는 것이 맞다.

## 12. 구현 entrypoint와 검증

이번 walkthrough를 코드 기준으로 따라가려면 아래 파일들이 핵심이다.

- `Iris/build/description/v2/tools/style/baseline_scan.py`
- `Iris/build/description/v2/tools/style/phase0_rule_binding.py`
- `Iris/build/description/v2/tools/style/normalizer.py`
- `Iris/build/description/v2/tools/style/linter.py`
- `Iris/build/description/v2/tools/style/dry_run.py`
- `Iris/build/description/v2/tools/style/phase2_activation.py`
- `Iris/build/description/v2/tools/style/phase6_triage.py`
- `Iris/build/description/v2/tools/style/style_closeout_packet.py`
- `Iris/build/description/v2/tools/style/style_runtime_closeout.py`

이번 세션의 대표 테스트 기준은 다음이었다.

- `Iris/build/description/v2/tests/test_style_normalizer.py`
- `Iris/build/description/v2/tests/test_style_baseline_scan.py`
- `Iris/build/description/v2/tests/test_style_linter.py`
- `Iris/build/description/v2/tests/test_style_phase6_triage.py`
- `Iris/build/description/v2/tests/test_style_phase6_acquisition_phrase_breakdown.py`
- `Iris/build/description/v2/tests/test_style_runtime_closeout.py`

static runtime closeout 시점에는 전체 test suite `167`건이 통과했다. 이후 final pass 반영은 artifact/doc update만 있었기 때문에 테스트를 다시 돌리지는 않았다.

## 13. 완료 판정

이번 walkthrough 기준 완료 판정은 다음처럼 읽는다.

- DVF 3-3 style normalization roadmap 범위는 완료
- `compose -> normalizer -> style linter -> rendered` 운영 경로도 완료
- current baseline lint closure도 완료
- Lua bridge/runtime closeout도 완료
- manual in-game validation pass 반영도 완료

반대로 별도 후속 과제로 남아 있는 것은 다음이다.

- future baseline drift가 생길 때의 rule/exception 재평가
- `construction_prep` 같은 compose template specificity 개선
- style normalization과 별개인 semantic/cluster expansion 후속 작업

즉, "이번 로드맵이 끝났다"와 "DVF/Iris 전체 후속 과제가 없다"는 같은 말이 아니다.
