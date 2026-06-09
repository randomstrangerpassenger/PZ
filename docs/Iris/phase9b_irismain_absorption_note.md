# Phase 9b — IrisMain INIT_MODULES Helper Absorption (이미 완료)

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 9b.

## 결론: IrisMain은 변경 불필요 (이미 흡수 형태)

계획의 9b는 "IrisMain INIT_MODULES helper 흡수 (INIT_MODULES spec 또는 generic dispatch로 작은 helper 흡수)"를
요구하나, `Iris/media/lua/client/Iris/IrisMain.lua`는 **이미 그 형태**다:

- **선언형 `INIT_MODULES`** 테이블(Step 2a~5f): 각 모듈 init을 `{ step, label, load, ready/onLoaded/invoke, protectedCall, ... }` spec으로 선언.
- **generic dispatch `runModuleSpec(spec)`**: load → onLoaded → ready → invoke(protectedCall) 를 일괄 처리. 작은 per-module helper(`hookTooltip`, `installBulletReloadCompat`, `buildBrowserData`, `initMapIcon` 등)는 spec의 `invoke` 콜백으로 흡수되어 있다.
- `Iris.initialize()`는 `for _, spec in ipairs(INIT_MODULES) do runModuleSpec(spec) end` 로 순회.

즉 "작은 helper들이 generic dispatch + 선언 spec으로 흡수"라는 목표가 **이미 구현**되어 있어 추가 변경이 없다.
(가장 위험한 bootstrap/dispatch 모듈을 건드리지 않으므로 9b 위험도 ↓.)

## Validation
- IrisMain.lua **미변경** → syntax/require/boot 영향 없음(9a 시점 `[Iris] Bootstrap complete` 확인됨).
- §12 9b의 "IrisMain syntax/require smoke"는 미변경으로 자동 충족(사용자 boot 재확인 권장).
