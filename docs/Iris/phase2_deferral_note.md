# Phase 2 (Change 2) — Deferral Note (excluded from execution)

> 2026-06-07 사용자 결정: **Phase 2(Change 2, batch1 helper 추출)는 앞으로 실행/결정 흐름에서 완전히 제외**한다. 다음 단계 후보로 제시하지 않는다.

## 사유

Change 2 대상(`build_identity_fallback_batch1_clothing_surface_reuse` + 약 20개 caller)은 gitignore된
**frozen reproduction 스크립트**이며, staging 입력이 제거되어 **실행 불가능**하다(입력 7개 중 5개 부재,
OUTPUT_DIR 없음, 저장소 어디에도 사본 없음 — 세션 분석 결과). 따라서 계획의 Phase 2 validation
(family direct script smoke + artifact SHA)을 수행할 수 없고, 어떤 리팩토링도 런타임 검증 불가한
"맹목 변경"이 되어 closeout이 `implemented_only`에 머문다.

## Disposition

- Change 2 = **무기한 deferred**, active sequence에서 제외.
- 입력(reproducibility contract)이 복원되면 그때 재검토 가능.
- batch1의 **공유 경로 상수**(category ①)는 Change 6(path manifest)에서 별도로 다룬다.
- batch1의 **helper 함수** anti-pattern은 스크립트가 frozen인 동안 dormant로 유지.

## Active 실행 순서 (Phase 2 제외)

완료: Phase 1, 3, 4 · 다음: **5 → 6 → 7a → 7b → 8 → 9a → 9b(사용자 in-game QA) → 10**.
(conflict 게이트 6/6 resolved.)
