# Phase 9b — Pulse Compatibility Wrapper Disposition

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 9b, §8 Compatibility Surface, conflict 14.5.
> 상세 인벤토리: `docs/Iris/phase1_pulse_wrapper_usage_inventory.md`.

## Disposition: 보존 (제거하지 않음)

Pulse namespace compat wrapper 6개 —
`Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/{Generator,Logger,Ordering,Renderer,TagParser,Templates}.lua` —
는 본 Change 9b에서 **제거/변경하지 않는다**(conflict 14.5 resolved: compat surface; governance §11).

| 항목 | 값 |
|---|---|
| 성격 | thin 리다이렉트 shim (`return require("Iris/Logic/IrisDesc/<M>")`) |
| 내부 require 참조 | 0건 (외부 소비자 후방호환용) |
| sealed 보호 | DVF 3.3 protected-surface 해시 집합 등재 |
| disposition | **keep** (제거는 deprecation/release decision 별도) |
| 본 round 변경 | 없음 — `git status`/`git diff --name-only HEAD` 빈 출력 + exit 0 으로 검증 |

## 검증 (Change 9b)
- Pulse wrapper untouched: `git status --short -- Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/` = 빈 stdout (exit 0); `git diff --name-only HEAD -- ...` = 빈 stdout (exit 0). → 6개 전부 미변경 ✅.
- 9b의 다른 변경(Browser/Wiki split)은 canonical `Iris/Logic/IrisDesc/*` 및 `Iris/UI/*`만 건드리며 Pulse 네임스페이스는 무관.
