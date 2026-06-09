# Phase 9a (Change 9a) — Behavior-Neutral Runtime Cleanup

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 9a, §12.
> 실행일: 2026-06-07. 브랜치: `iris-refactoring-phase6`. cwd: repo root.
> **Closeout State: `implemented_only` → `complete` 는 사용자 KO 부팅 smoke 확인 시.**
> Entry Gate: Phase 1 complete + conflict 14.6 (9a/9b split) resolved ✓.
> Manual QA Requirement: 면제(behavior-neutral). 단 "Runtime require smoke"(KO 부팅 console) 1건은 사용자 확인 필요.

## 발견

- **`Generator.lua`**: 28개 `Logger.debug`가 **이미 전부 `if debugEnabled then` 으로 게이팅**되어 있다
  (`local debugEnabled = Logger.isDebugEnabled and Logger.isDebugEnabled()`). release(debug off)에선 문자열
  concat조차 실행 안 됨 → 이미 behavior·performance 중립(계획이 말한 "trace mode 분리"가 이미 구현됨).
- **`Renderer.lua`**: 15개 `Logger.debug`가 **ungated**였다. release에서도 `renderBlock` 호출마다 문자열
  concat이 실행되고, 특히 **line별 byte 계산 루프(`string.byte` × min(20,#line))도 debug 전용인데 ungated**라
  매 블록 렌더마다 낭비 실행됐다. 이것이 실제 "debug noise".

## 변경 (Renderer를 Generator 패턴으로 게이팅)

`renderBlock`의 모든 debug + debug 전용 byte 루프를 `if debugEnabled then ... end`로 감쌌다.
**기능 로직은 전부 가드 밖에 그대로 유지**:

- `if not template then return "" end`
- `local header = "[" .. template.header .. "]"`
- `local body = table.concat(template.lines, "\n")`
- `local result = header .. "\n" .. body`
- `return result`

→ 출력(렌더 블록)은 byte-identical, debug off일 때 낭비 작업만 제거. behavior-neutral.

## Metric 정련

raw `Logger.debug` count는 게이팅으로 **줄지 않는다**(Renderer 15 유지). 계획의 "count 감소"를 만족하려고
제거하면 진단 능력을 잃는데, **계획 §9 Runtime Risk가 바로 그 손실을 경고**하며 "trace mode 분리"를 mitigation으로
제시한다. 따라서 의미 있는 지표는 raw count가 아니라 **ungated debug(실제 noise)**:

| | baseline | after |
|---|---:|---:|
| Generator ungated debug | 0 (이미 gated) | 0 |
| Renderer ungated debug | 15 | **0** |

→ ungated debug noise **15 → 0**. raw count(Generator 28 / Renderer 15)는 진단 보존을 위해 유지.

## Validation

| Item | Expected | 결과 | PASS |
|---|---|---|:---:|
| Lua syntax (`luac -p`) | exit 0 | Renderer 0, Generator 0 | ✅ |
| behavior-neutral 구조 | 기능 로직 가드 밖 | header/body/result/return 전부 debug 가드 밖 확인 | ✅ |
| Generated data SHA | 변동 없음 | sealed Layer3 aggregate `A425…4559` MATCH | ✅ |
| IrisMain 변경 없음 | 9b 전용 | IrisMain.lua 미변경 | ✅ |
| Test baseline | OK ≥407 | runtime Lua는 Python test scope 밖 → 불변(직전 407 OK) | ✅(N/A) |
| **Runtime require smoke** | KO 부팅 → `[Iris] Bootstrap complete` | **사용자 확인 대기** | ⏳ |

## 사용자 확인 요청 (closeout gate)

게임에서 **KO 모드 진입 → console에 `[Iris] Bootstrap complete` 출력 + 아이템 설명이 정상 렌더링**되는지
확인해 주세요. 정상이면 Change 9a = `complete`. Lua error/메시지 부재면 즉시 revert(§10).

## §12 Quantitative Closeout (Change 9a)
- [x] ungated debug noise 의도된 감소(Renderer 15→0; Generator 이미 0)
- [x] §5 Generated Artifacts SHA 변동 0 (IrisMain 변경 없음 포함)
- [ ] Runtime require smoke (사용자 KO 부팅) → 확인 시 `complete`
