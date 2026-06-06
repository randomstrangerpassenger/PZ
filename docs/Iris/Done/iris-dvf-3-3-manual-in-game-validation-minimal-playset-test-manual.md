# Iris DVF 3-3 Manual In-Game Validation Minimal Playset Test Manual

작성일: 2026-05-24

상위 계획:

```text
docs/Iris/iris-dvf-3-3-manual-in-game-validation-qa-round-plan.md
```

증거 기록 대상:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/
```

## 목적

이 문서는 MIGV-QA Phase 4-6을 사람이 인게임에서 실행하기 위한 최소 플레이세트 절차다.

이 문서로 할 수 있는 것:

* Phase 4 인게임 환경 기록.
* Phase 5 Browser / Wiki-detail / default bounded baseline 표면 확인.
* Phase 6 publish visibility 양방향 확인.
* Phase 9 evidence packet에 넣을 콘솔, 스크린샷, 구조화 관찰 기록 확보.

이 문서로 주장하면 안 되는 것:

* release readiness.
* Workshop readiness.
* tooltip / Alt validation.
* B42 validation.
* 2105-row exhaustive QA.
* deployed closeout.

## 실행 전 상태

시작 전 다음 상태여야 한다.

```text
Phase 1 identity pre-gate = pass
Phase 2 sample/source axis matrix = prepared and finalized
Phase 3 static validation = pass
Phase 4-6 = not_run
```

현재 최소 플레이세트는 아래 matrix artifact를 기준으로 한다.

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase2_harness/manual_in_game_validation_sample_matrix.json
```

주의:

* matrix artifact 자체를 수정하지 않는다.
* runtime Lua, source decisions, rendered text, publish authority, quality state를 수정하지 않는다.
* 이 검증은 관찰과 기록만 수행한다.

## 증거 파일 위치

실행자가 Phase 4-6을 완료한 뒤 아래 파일을 채울 수 있어야 한다.

```text
phase4_environment/manual_in_game_validation_environment.md
phase4_environment/enabled_mods_minimal.md
phase4_environment/enabled_mods_modded.md
phase5_surface/browser_surface_result.json
phase5_surface/wiki_detail_result.json
phase5_surface/default_surface_result.json
phase5_surface/surface_display_result.json
phase6_publish/publish_visibility_two_sided_result.json
phase9_evidence/manual_in_game_validation_results.json
phase9_evidence/manual_in_game_validation_console_log_summary.md
phase9_evidence/manual_in_game_validation_screenshots_index.md
phase9_evidence/manual_in_game_validation_walkthrough.md
```

스크린샷 또는 영상은 Phase 9 evidence 아래 별도 폴더에 모아도 된다.

권장 위치:

```text
Iris/build/description/v2/staging/manual_in_game_validation/migv_qa/phase9_evidence/screenshots/
```

## 최소 샘플 세트

Phase 4-6 차단 해소에 필요한 최소 샘플은 다음 6개다.

| 한국어 인게임 이름 | identity_key | 목적 | 기대 관찰 |
|---|---|---|
| `.223 탄약 상자` | `Base.223Box` | exposed control, cluster_summary, acquisition support, non-empty text control | Browser/Wiki에서 사용자 표면 노출 가능. 설명 본문이 정상 표시되어야 한다. |
| `앞치마` | `Base.Apron_Black` | internal_only, identity_fallback | Iris Browser 아이템 엔트리 노출은 허용된다. `internal_only`는 Layer 3 본문/상태 품질 표식이며 raw internal token이나 깨진 placeholder가 사용자 표면에 보이면 안 된다. |
| `빗자루` | `Base.Broom` | missing publish_state, nil text_ko, unadopted finding row | Iris Browser 아이템 엔트리 노출은 허용된다. generated/tag 기반 설명은 허용되지만 raw nil, table 주소, raw state token, 깨진 placeholder가 보이면 안 된다. |
| `철조망` | `Base.BarbedWire` | direct_use, special_context support | Browser/Wiki 선택과 본문 표시가 정상이어야 한다. |
| `서류 가방` | `Base.Briefcase` | role_fallback | Browser/Wiki 선택과 본문 표시가 정상이어야 한다. |
| `스크류드라이버` | `Base.Screwdriver` | long text shape | 긴 본문이 잘리거나 stale text를 만들지 않아야 한다. |

추가 확인 샘플:

* current matrix를 그대로 hard-gate 입력으로 사용할 경우 `chunk_boundary` 행도 모두 실행한다.
* 시간 단축이 필요한 1차 수동 QA에서는 위 6개를 먼저 실행하고, 누락된 matrix 행은 `not_run`으로 남긴다.
* Branch A closeout을 주장하려면 실제 selected sample마다 sample/surface/result 증거가 있어야 한다.

## Phase 4 - 환경 기록

### 4.1 콘솔 기준점 확보

Windows 기본 위치:

```text
C:\Users\MW\Zomboid\console.txt
```

다른 위치를 쓰는 경우 실제 경로를 기록한다.

시작 전 기록:

* `Console.txt` 경로.
* 시작 전 파일 수정 시각.
* 시작 전 파일 크기.
* 검증 시작 시각.
* 스크린샷 또는 영상 저장 위치.

실행 후 기록:

* 종료 후 파일 수정 시각.
* 종료 후 파일 크기.
* 관찰 시간대 안의 Iris-attributable error 수.
* non-Iris 또는 다른 모드 error 수와 분류.

### 4.2 Minimal environment

목표는 vanilla-adjacent run이다.

설정:

* Project Zomboid 버전과 B41/B42 여부를 기록한다.
* Iris mod install/build path를 기록한다.
* 활성 모드는 Iris와 Iris 실행에 필요한 최소 의존성만 둔다.
* 언어/locale 설정을 기록한다. Korean text 확인이면 Korean locale을 우선 사용한다.
* 새 테스트 save 또는 기존 테스트 save 이름을 기록한다.
* 테스트 캐릭터와 인벤토리 준비 방식을 기록한다.

통과 조건:

```text
minimal_environment_recorded = true
console_capture_ready = true
visual_evidence_capture_ready = true
test_save_entered = true
Iris_UI_entered = true
```

### 4.3 Modded environment

목표는 사용자의 실제 모드 조합에서 compatibility 관찰을 분리하는 것이다.

설정:

* 사용자의 일반 모드셋 + Iris를 활성화한다.
* 전체 enabled mod list를 기록한다.
* minimal run과 같은 게임 버전, locale, 테스트 save 조건을 최대한 유지한다.
* 오류가 있으면 minimal 환경에서 재현되는지 여부를 따로 기록한다.

분류 규칙:

* minimal에서도 재현되고 Iris 호출 경로에 묶이면 Iris blocker다.
* modded에서만 발생하고 Iris 표면 통과와 직접 관련이 없으면 compatibility observation이다.
* 원인을 모르면 `unclassified`로 두고 pass를 주장하지 않는다.

## Phase 5 - 표면 검증

Phase 5는 minimal environment에서 먼저 실행한다. modded environment에서는 대표 샘플만 반복한다.

각 샘플마다 기록할 공통 필드:

```text
identity_key:
environment: minimal | modded
surface: Browser | Wiki/detail | default bounded baseline
steps:
observed_result:
expected_result:
pass_fail:
console_window:
evidence_file:
```

### 5.1 Browser surface

각 샘플에서 다음을 수행한다.

1. 인게임에서 Iris Browser를 연다.
2. category browse 또는 search로 샘플 identity를 찾는다.
3. item select를 수행한다.
4. 다른 샘플을 선택한 뒤 원래 샘플로 reselect한다.
5. Browser를 닫고 다시 열어 같은 샘플을 다시 확인한다.
6. 스크린샷 또는 구조화 관찰 기록을 남긴다.
7. 같은 시간대의 `Console.txt` 오류를 확인한다.

통과 조건:

```text
browser_surface = pass
stale_selection_artifact_count = 0
layer_boundary_confusion_count = 0
nil_placeholder_raw_token_exposure = 0
iris_attributable_console_error_count = 0
```

즉시 실패 조건:

* 이전 샘플의 본문이 남는다.
* Layer 3 body text가 Layer 1/2/4/5와 섞인다.
* `publish_state`, `runtime_state`, `source`, `nil`, `table: 0x`, placeholder token이 사용자 표면에 보인다.
* minimal environment에서 Iris-attributable runtime error가 발생한다.

### 5.2 Wiki/detail surface

각 exposed 또는 표시 가능한 샘플에서 다음을 수행한다.

1. Browser에서 샘플을 선택한다.
2. Wiki/detail 패널로 진입한다.
3. `대분류 - 소분류 - 아이템 목록 - 아이템 설명` 4단계 계층을 확인한다.
4. item description이 DVF 3-3 body_plan 출력으로 보이는지 확인한다.
5. detail을 닫고 다시 열어 stale content가 없는지 확인한다.
6. 스크린샷 또는 구조화 관찰 기록을 남긴다.
7. 같은 시간대의 `Console.txt` 오류를 확인한다.

통과 조건:

```text
wiki_detail_surface = pass
four_level_hierarchy = pass
stale_selection_artifact_count = 0
layer_boundary_confusion_count = 0
nil_placeholder_raw_token_exposure = 0
iris_attributable_console_error_count = 0
```

주의:

* `앞치마` (`Base.Apron_Black`)는 internal_only 샘플이지만 Iris Browser 아이템 엔트리 노출은 실패가 아니다. raw `publish_state`, `internal_only`, `source`, debug/internal token, 깨진 placeholder가 사용자 표면에 보이는지를 본다.
* `빗자루` (`Base.Broom`)는 finding row다. Browser에 엔트리와 generated/tag 기반 설명이 보일 수 있으며, raw nil/table/placeholder/state token이 없는지를 본다.

### 5.3 Default bounded baseline

default bounded baseline은 세 번째 Iris 본문 표면을 새로 만드는 검증이 아니다.

허용 범위:

```text
Iris-disabled vanilla behavior preservation
right-click entrypoint baseline leading to the Browser/Wiki path
```

Minimal run에서 수행:

1. Iris enabled 상태에서 아이템 right-click 또는 현재 사용자 진입 경로를 확인한다.
2. 진입 경로가 Browser/Wiki path로 이어지는지 확인한다.
3. Browser/Wiki와 별개인 새 body display surface가 생기지 않았는지 확인한다.
4. 같은 항목을 여러 번 open/close하여 context menu와 item selection regression이 없는지 확인한다.

Iris-disabled control run에서 수행:

1. Iris를 비활성화하고 같은 테스트 save 또는 동등한 테스트 save에 진입한다.
2. vanilla item right-click / inventory interaction이 유지되는지 확인한다.
3. Iris UI가 나타나지 않는지 확인한다.
4. 이 control run은 Browser/Wiki pass로 계산하지 않고 default baseline evidence로만 기록한다.

통과 조건:

```text
default_bounded_baseline_definition_documented = true
default_bounded_baseline_within_philosophy_two_surface_model = true
default_bounded_baseline = pass
vanilla_behavior_preserved = true
context_menu_regression_count = 0
item_selection_regression_count = 0
known_conflict_marker_recurrence = 0
iris_attributable_console_error_count = 0
```

## Phase 6 - publish visibility two-sided check

Minimal environment에서 반드시 수행한다. Modded environment에서는 대표 세트로 반복한다.

### 6.1 Exposed sample

샘플:

```text
.223 탄약 상자
identity_key: Base.223Box
```

수행:

1. Browser에서 검색 또는 category browse로 찾는다.
2. Wiki/detail로 연다.
3. 설명 본문이 사용자 표면에 정상 표시되는지 확인한다.
4. raw state token이 보이지 않는지 확인한다.

통과 조건:

```text
exposed_display_sample_pass = true
```

### 6.2 Internal-only sample

샘플:

```text
앞치마
identity_key: Base.Apron_Black
```

수행:

1. 기본 사용자 Browser 검색에서 아이템 엔트리가 표시되는지 확인한다.
2. 설명란에 raw `publish_state`, `internal_only`, `runtime_state`, `source`, debug/internal token, table 주소, 깨진 placeholder가 보이는지 확인한다.
3. 기본 Wiki/detail 사용자 경로에서 열리는지는 전체 Phase 4-6 완료를 주장할 때만 별도로 확인한다.
4. debug/internal path가 있다면 기본 사용자 표면과 별도로 기록한다.

통과 조건:

```text
internal_only_item_entry_visible_allowed = true
internal_only_raw_state_token_exposure_count = 0
internal_only_broken_placeholder_count = 0
```

실패 조건:

* 사용자 표면에 raw `internal_only`, raw `publish_state`, raw `source`, debug/internal token, table 주소, 깨진 placeholder가 보인다.
* internal/debug 관찰을 default user-facing Browser 관찰과 섞어 pass로 처리한다.

### 6.3 Missing publish_state / nil text finding sample

샘플:

```text
빗자루
identity_key: Base.Broom
```

수행:

1. Browser 검색 결과를 확인한다.
2. Browser에 표시된다면 아이템 엔트리와 설명란이 안전하게 표시되는지 확인한다.
3. generated/tag 기반 설명은 허용한다.
4. raw nil, table 주소, placeholder, raw state token이 없는지 확인한다.
5. Wiki/detail 진입 가능 여부는 전체 Phase 4-6 완료를 주장할 때만 별도로 확인한다.
6. 이 샘플을 cleanup 대상이 아니라 finding-aware QA sample로 분류한다.

통과 조건:

```text
missing_publish_state_finding_rows_classified = true
missing_publish_state_item_entry_visible_allowed = true
nil_text_ko_broken_placeholder_count = 0
unadopted_broken_exposure_count = 0
raw_state_token_exposure_count = 0
```

### 6.4 Browser/Wiki consistency

수행:

1. `.223 탄약 상자` (`Base.223Box`), `앞치마` (`Base.Apron_Black`), `빗자루` (`Base.Broom`)의 Browser 관찰 결과를 기록한다.
2. 같은 샘플의 Wiki/detail 관찰 결과를 기록한다.
3. Browser와 Wiki/detail의 visibility 판정이 충돌하지 않는지 확인한다.

통과 조건:

```text
browser_wiki_visibility_consistent = true
```

## Modded environment 반복 범위

Modded run에서는 전체 6개 샘플을 반복하는 것이 가장 좋다.

시간이 부족하면 최소 대표 세트는 다음 3개다.

| 한국어 인게임 이름 | identity_key | 목적 |
|---|---|
| `.223 탄약 상자` | `Base.223Box` | exposed 정상 노출 |
| `앞치마` | `Base.Apron_Black` | internal_only 상태의 raw token / placeholder 누출 방지 |
| `빗자루` | `Base.Broom` | missing publish_state / nil text 상태의 raw nil / placeholder 누출 방지 |

Modded run 통과 기록은 release readiness가 아니다. 이 기록은 compatibility observation과 Iris blocker 분리를 위한 보조 증거다.

## 스크린샷 최소 목록

최소 evidence packet에는 아래 스크린샷 또는 동등한 구조화 visual note가 필요하다.
권장 파일명은 한국어 인게임 이름을 사용하고, identity key는 screenshots index 또는 observation note에 별도 기록한다.

```text
p4_minimal_enabled_mods.png
p4_minimal_console_window_before_after.png
p5_browser_.223탄약상자_minimal.png
p5_wiki_.223탄약상자_minimal.png
p5_browser_reselect_스크류드라이버_minimal.png
p5_default_right_click_entrypoint_minimal.png
p5_default_iris_disabled_vanilla_control.png
p6_internal_only_앞치마_visible_safe_minimal.png
p6_missing_publish_빗자루_visible_safe_minimal.png
p4_modded_enabled_mods.png
p5_modded_representative_.223탄약상자.png
p6_modded_representative_visibility.png
```

스크린샷이 불가능하면 다음 필드를 갖는 구조화 관찰 기록을 남긴다.

```text
observer:
observed_at:
environment:
sample:
surface:
exact_steps:
visible_text_summary:
raw_token_exposure:
stale_content_observed:
console_error_window:
result:
```

## 콘솔 오류 판정

Iris-attributable error로 보는 경우:

* stack trace 또는 log prefix가 Iris 파일/함수/모듈을 직접 가리킨다.
* minimal environment에서 Iris UI 조작 직후 재현된다.
* 같은 조작을 반복하면 같은 오류가 재현된다.

Compatibility observation으로 보는 경우:

* modded environment에서만 발생한다.
* stack trace가 다른 모드 파일/함수를 직접 가리킨다.
* minimal environment의 같은 조작에서는 재현되지 않는다.

Blocked로 두는 경우:

* attribution이 불명확하다.
* console window를 잃어버렸다.
* 스크린샷/구조화 기록과 console timestamp를 연결할 수 없다.

## Hard fail 목록

아래 중 하나라도 있으면 Phase 4-6 pass를 주장하지 않는다.

* minimal environment에 진입하지 못했다.
* Iris Browser에 진입하지 못했다.
* exposed sample `.223 탄약 상자` (`Base.223Box`)가 기본 사용자 표면에서 정상 확인되지 않는다.
* internal_only sample `앞치마` (`Base.Apron_Black`)가 raw `internal_only`, raw `publish_state`, debug/internal token, table 주소, 깨진 placeholder를 사용자 표면에 노출한다.
* `빗자루` (`Base.Broom`)가 raw nil, table address, placeholder, raw state token을 노출한다.
* Browser selection/reselection 후 stale body text가 남는다.
* Browser/Wiki 외의 새 기본 body display surface가 생긴다.
* minimal environment에서 Iris-attributable console/runtime error가 발생한다.
* Phase 4-6 수행 중 canonical runtime/source artifact가 변경된다.

## 완료 판정

현재 최소 Browser 플레이테스트 pass를 주장하려면 아래가 모두 참이어야 한다.

```text
environment_manifest_present = true
project_default_playtest_baseline_recorded = true
console_capture_ready = true
visual_evidence_capture_ready = true
browser_surface = pass
exposed_display_sample_pass = true
internal_only_item_entry_visible_allowed = true
internal_only_raw_state_token_exposure_count = 0
missing_publish_state_finding_rows_classified = true
missing_publish_state_item_entry_visible_allowed = true
nil_text_ko_broken_placeholder_count = 0
unadopted_broken_exposure_count = 0
raw_state_token_exposure_count = 0
iris_browser_lua_stack_trace_count = 0
```

전체 Phase 4-6 완료 또는 deployed closeout을 주장하려면 아래가 추가로 필요하다.

```text
minimal_or_project_default_environment_recorded = true
modded_environment_recorded_if_claimed = true
wiki_detail_surface = pass
default_bounded_baseline = pass
browser_wiki_visibility_consistent = true
```

최소 Browser pass 완료 후에도 다음은 별도 Phase 7-12에서 다시 확인해야 한다.

* runtime baseline preservation.
* negative invariant.
* evidence packet completeness.
* hard gate report.
* closeout classification.
