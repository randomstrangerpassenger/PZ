# Phase 9b — Manual QA Checklist (Entry Gate Deliverable)

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 9b Manual QA Checklist Schema, §12.
> **이 문서는 Change 9b의 첫 코드 commit *이전*에 작성·commit되는 entry gate 산출물이다.**
> `baseline_capture_commit = a5054f3` (a5054f34501369f64eaaabbcc3eb89dfa35eefab) — 9b 코드 변경 전 HEAD.

## Surface 정의 (사용자 확정 2026-06-09)

user-facing surface는 2개 + Bootstrap:
- **Menu** (= 코드의 Browser + Wiki가 합쳐 보이는 "Iris 메뉴") — 9b 분할(`IrisWikiSections`, `IrisBrowserInteractionRenderer`)이 직접 그리는 핵심 surface.
- **Tooltip** ("Iris 툴팁") — IrisDesc Generator/Renderer가 그림(9a 완료, 9b 미변경). IrisMain 부팅만 간접 영향.
- **Bootstrap** — KO 부팅 console `[Iris] Bootstrap complete` (9a처럼 로그로 검증).

## QA Matrix

| surface | scenario (item + entry path) | baseline_screenshot | baseline_capture_commit | post_change_screenshot | post_change_commit | comparison_result | tester | verdict |
|---|---|---|---|---|---|---|---|---|
| **Menu** | item `탄산(음료수)`; Iris Browser → 소모품/음료 → 상세정보 | 사용자 제공 2026-06-09(세션). 내용 전사 ↓ | `a5054f3` | (pending) | (pending) | (pending) | 사용자 | (pending) |
| **Tooltip** | item `탄산` 툴팁 (Alt 확장) | (스크린샷 면제 — 9b가 툴팁 렌더 경로 미변경. "한국어 설명 표시" 육안) | `a5054f3` | (pending) | (pending) | (pending) | 사용자 | (pending) |
| **Bootstrap** | KO mode 진입 | console `[Iris] Bootstrap complete` (9a 시점 확인됨) | `a5054f3` | (pending) | (pending) | (pending) | 사용자/AI | (pending) |

## Menu baseline 전사 (탄산/음료수 상세정보 — 비교 기준 진리)

```
탄산 (음료수)
무게: 0.3 | 타입: Food | 데미지: 0.0~1.5 | 내구도: 10 | 갈증: -60 | 배고픔: -8

[소모품-식품]
이 아이템은 섭취하여 포만감이나 상태 수치에 영향을 주는 데 사용된다.
[소모품-음료]
이 아이템은 복용 시 갈증이나 상타 수치에 영향을 주는 데 사용된다.

음료수.
마시거나 나눠 마실 때 쓴다.

분류 ID: Consumable.3-A, Consumable.3-B
모듈: Base
```

레이아웃: 4열 (대분류 → 소분류 `3-A 식품(368)/3-B 음료(92)/3-C 의약품(28)/3-D 기호품(19)/3-E 약초(18)` → 아이템 목록 → 상세정보). 창 제목 `Iris Browser`.

> 분할 후 위 텍스트·레이아웃이 **byte/픽셀 동일(identical)** 이어야 PASS. 차이 발견 시 `regression` → revert(§10).

## baseline ↔ 진입 commit 순서 검증 (closeout 시 실행)

```powershell
git merge-base --is-ancestor a5054f3 $firstCodeCommit
$ancestorExit = $LASTEXITCODE   # 0 = ancestor
$sameSha = ((git rev-parse a5054f3) -eq (git rev-parse $firstCodeCommit))
# PASS 조건: $ancestorExit -eq 0 -and -not $sameSha
```

## Closeout 규칙

- 모든 행 `verdict = PASS` + `$ancestorExit -eq 0` + baseline≠첫코드 SHA → Change 9b `complete`.
- `regression`/`FAIL` 1건 → revert 또는 `implemented_only` (merge/behavior-preserving claim 불가).
- manual QA 미수행 → `implemented_only`.
