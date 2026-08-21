# Iris Layer 4 adaptive presentation and locale projection Walkthrough

Date: 2026-08-21

Current state: implementation complete / integrated into `main` / owner in-game acceptance complete

## 1. 범위와 시작 상태

이번 세션은 기존 Layer 4 `partial` 실행의 다음 적용 가능한 지점에서 adaptive interaction presentation을 완료하고, 실제 PZ에서 owner가 확인한 결함을 current runtime에 반영하는 작업이었다.

핵심 범위는 다음과 같았다.

- status-bearing Layer 4 interaction projection을 Iris Browser의 adaptive presentation으로 연결
- 단일·소규모·고밀도 항목의 표시 밀도 차등화
- 고밀도 항목의 compact/full 전환과 검색
- Recipe 제작 UI 이동과 item/locale별 UI state ownership
- QG-only 3개 관계의 public 표시
- KO/EN 전환 시 Layer 2–3 정보 보존
- 기존 context menu/Wiki/Alt Tooltip과 화면 layout의 회귀 방지

Layer 4 구현은 처음에 `codex/iris-layer4-adaptive` branch에 있었기 때문에, main 기반의 첫 owner 테스트는 변경이 적용되지 않은 버전을 대상으로 했을 가능성이 있었다. Owner의 요청에 따라 해당 구현을 `e7508c0c`에서 `main`에 병합한 뒤 실제 수용 테스트를 다시 진행했다.

## 2. Layer 4 current runtime

Layer 4는 `UseCases._getDescriptionState(fullType)`에서 `available`, `verified_empty`, `fault`를 구분한 상태를 Detail ViewModel의 `interactionState`로 전달한다. Browser는 legacy capability/Recipe fallback을 별도의 presentation source로 재조합하지 않고 이 상태-bearing projection을 표시한다.

현재 presentation 동작은 다음과 같다.

- 1개 row는 바로 펼쳐 표시한다.
- 2–8개 row는 전체를 표시한다.
- 9개 이상은 compact view로 시작하며 full view와 literal search를 제공한다.
- Recipe와 Right-click은 독립된 동등 Source로 유지한다.
- Recipe row는 stable recipe identity를 사용해 제작 UI로 이동한다.
- 검색·compact/full 상태는 Browser generation, locale, FullType owner에 결속된다.
- item 또는 locale이 바뀌면 이전 화면의 query와 fold state를 재사용하지 않는다.

새로 public 표시되는 QG-only 관계는 다음 세 개다.

- `Base.BallPeenHammer / uc.action.construction`
- `Base.GardenSaw / uc.action.wood_cutting`
- `Base.HammerStone / uc.action.construction`

대표 density anchor는 `Base.223BulletsMold`의 단일 Recipe row와 `Base.Tongs`의 고밀도 Recipe row다. `223 Bullets Mold`는 즉시 열린 단일 항목과 requirement를, `Tongs`는 compact/full/search 동작을 확인하는 데 사용됐다.

## 3. Owner 인게임 확인의 진행

첫 확인에서는 Iris Browser 자체와 Tongs, Recipe UI 이동 등은 정상으로 보였지만 `223 Bullets Mold`와 일부 전환 상태가 실패로 보고됐다. 이후 현재 변경이 main에 병합되지 않았다는 점을 확인했고, `e7508c0c` 병합 뒤 동일 범위를 다시 확인했다.

재확인 결과 `223 Bullets Mold`, Tongs, Recipe UI 이동과 item 전환 상태는 정상으로 판정됐다. item 전환 상태는 처음에는 실패로 기록됐지만 owner가 다시 확인했을 때 이전 item의 상태가 남지 않았다.

QG-only 항목 중 Ball Peen Hammer와 Garden Saw는 즉시 확인됐고, Stone Hammer는 처음에는 기대한 우클릭 행동이 보이지 않는다고 보고됐다. 후속 수정과 재확인 뒤 owner가 Stone Hammer의 우클릭 행동도 정상 표시된다고 최종 확인했다.

Assistant가 시도한 PZ harness 실행은 timeout 뒤 유효한 결과를 만들지 못했으며 PASS로 사용하지 않았다. 이후 실제 인게임 확인은 owner에게 맡겼고 PZ를 다시 자동 실행하지 않았다.

## 4. KO/EN Layer 2–3 결함과 수정

Owner 테스트에서 KO 화면은 정상인 반면 EN으로 바꾸면 Layer 2와 Layer 3의 글자가 깨져 보이는 결함이 발견됐다. Layer 1, 4, 5는 정상 표시됐다.

처음에는 EN에서 KO-only Layer 2–3을 숨기는 변경이 `1524d72a`에 들어갔다. 이 방식은 지원 locale에서 이미 알려진 정보를 감추므로 Iris Philosophy의 정보 비은폐 원칙에 맞지 않았다. Owner의 지적에 따라 해당 동작을 폐기하고 번역된 EN payload를 제공하는 방식으로 교체했다. `1524d72a`는 current 결정이나 최종 동작이 아니며 `de146b73`에 의해 superseded됐다.

최종 구현은 다음과 같다.

- Layer 2는 `Templates.lua`와 동일한 50개 classification ID를 가진 `TemplatesEn.lua`를 제공한다.
- `Generator.lua`, `Description.lua`, Detail ViewModel과 Browser detail path가 locale을 전달해 같은 분류 의미의 KO/EN 문장을 선택한다.
- Layer 3는 current facts에 결속된 2,084개 EN companion payload를 제공한다.
- EN payload는 `IrisLayer3EnglishLookup.lua`가 `Layer3English/Index.lua`를 통해 11개 lazy chunk 중 필요한 chunk만 읽는다.
- `layer3_renderer.lua`는 요청 locale의 precompiled payload를 선택한다.
- KO raw text를 EN 화면에 그대로 노출하거나, 번역 문제를 이유로 알려진 Layer 2–3 정보를 숨기는 cross-locale fallback은 사용하지 않는다.

Layer 3 EN payload는 current facts의 locale projection이다. KO body, fact/provenance, disposition/readiness 또는 Layer 4 authority를 바꾸지 않으며 PZ runtime에서 새로운 사실을 추론하거나 문장을 다시 생성하지 않는다. Python localization builder는 offline producer일 뿐 Iris의 새 runtime authority나 canonical validator가 아니다.

## 5. 최종 owner acceptance

| 확인 항목 | 최종 결과 | 비고 |
|---|---|---|
| PZ 부팅 | 정상 | Owner 확인 |
| Iris Browser | 정상 | Owner 확인 |
| 223 Bullets Mold | 정상 | 단일 row/requirement 표시 |
| Tongs compact/full/search | 정상 | 고밀도 표시 동작 |
| Recipe 제작 UI 이동 | 정상 | Owner 확인 |
| item 전환 상태 | 정상 | 이전 item 상태가 남지 않음 |
| Ball Peen Hammer QG-only | 정상 | Owner 확인 |
| Garden Saw QG-only | 정상 | Owner 확인 |
| Stone Hammer QG-only | 정상 | 우클릭 행동 표시 최종 확인 |
| 기존 context menu/Wiki/Alt Tooltip | 정상 | fallback 분기 발생 여부 자체는 구별 불가 |
| 화면 겹침/잘림 | 없음 | Owner 확인 |
| KO/EN Layer 2–3 | 정상 | EN 번역 적용 뒤 owner 확인 |

기존 context menu/Wiki/Alt Tooltip이 정상이라는 결과를 내부 fallback branch 자체의 수동 PASS로 확대하지 않는다. Owner가 확인한 것은 공개 surface의 정상 동작이다.

## 6. 변경 readpoint와 필요한 검사

Current 코드 readpoint는 다음과 같다.

- `e7508c0c` — Layer 4 adaptive presentation을 `main`에 통합
- `1524d72a` — 폐기된 EN Layer 2–3 hide 방식
- `de146b73` — Layer 2–3 EN locale projection으로 hide 방식을 대체

Locale 수정 뒤 task-focused suite는 `9 passed, 5 deselected`, repository Lua syntax command는 `Lua syntax validation OK: 145 files`로 exit `0`이었다. Layer 2 KO/EN template ID는 50개로 일치하고 Layer 3 EN runtime payload는 current body denominator 2,084개를 포함한다.

이번 작업을 위해 별도의 seal, receipt, manifest, census 또는 validation-of-validation artifact를 추가하지 않았다. Localization builder와 일회성 검사는 이 작업의 보조 수단이며 기존 계획이나 authority가 채택하지 않는 한 정규 검사기나 후속 validation authority가 아니다.

## 7. 완료 경계

Layer 4 adaptive interaction presentation, 세 QG-only 관계, item/locale state ownership, Recipe navigation과 KO/EN Layer 2–3 표시에는 남은 구현 또는 인게임 수용 gate가 없다.

이번 완료는 다음을 주장하지 않는다.

- Layer 3 fact authority 또는 source semantics 변경
- 새로운 사실 추론, 추천 또는 정보 생성 권한
- 기존 surface fallback branch의 직접적인 인게임 관찰
- RTC, Publish, push, release/Workshop 또는 deployment readiness

현재 `main`의 제품 동작은 `de146b73`까지이며, 세션의 의사결정·아키텍처·로드맵 정합화는 `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`에 함께 반영됐다.
