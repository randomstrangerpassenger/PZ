# Phase 9b — Runtime Renderer Responsibility Split

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 9b, §12.
> 실행일: 2026-06-07. 브랜치: `iris-refactoring-phase6`. baseline_capture_commit `a5054f3`.
> **Closeout State: `complete`** (사용자 Menu QA 전 행 PASS, 2026-06-09; `phase9b_manual_qa_checklist.md` 참조).

## 분할 내역 (facade + verbatim, public 인터페이스·caller 불변)

런타임 UI는 실행 불가(luac은 문법만, 로직 오류는 Menu QA가 잡음)이므로, **public 인터페이스를 그대로 두고
함수를 verbatim 이동, caller require 경로를 바꾸지 않는** facade 방식으로 분할했다.

### Browser (계획대로 2-way)
- **신규** `IrisBrowserInteractionCollector.lua` ← `collectRecipeInteractions` + `collectCapabilityInteractions` (interaction collection).
- `IrisBrowserInteractionRenderer.lua` = UI row rendering(`render`)만 유지, collection은 Collector에 위임. 미사용 `ProtectedCall` require 제거.
- caller `IrisBrowserDetail.lua` 불변(`.render` 그대로).

### Wiki (usecase line renderer 추출 — clean boundary 1개)
- **신규** `IrisWikiUseCaseLineRenderer.lua` ← `renderUseCaseLine`(순수 line→문자열 매퍼) + 자체 deps(`IrisUseCaseLabelMap` ensure, `getRuntimeLangKey`).
- `IrisWikiSections.lua`의 local `renderUseCaseLine`은 **위임 1줄**(`UseCaseLineRenderer.renderLine`)로 축소. `ensureUseCaseDeps`는 `IrisConfig`만 ensure(label map은 sub-module로 이관). caller(`IrisBrowser`, `IrisWikiPanel`)·`renderUseCaseSection` call site 불변.

### section renderer / property extractor 추가 분할 — 미실시 (의도)
계획의 IrisWikiSections "section renderer / property extractor" 추가 분할은 **하지 않았다**:
- 14개 section 메서드가 module-level 공유 deps(`ensureDeps`/`IrisAPI`, `ItemAccess`, `IrisConfig`, `getLabel`/`safeCall`)로 강결합.
- **"property extractor"와 "section renderer"는 사실상 같은 응집 코드**(각 section이 아이템 속성을 추출+포맷). 인위 분할은 가시 메뉴를 blind로 위험에 빠뜨릴 뿐 이득이 modest.
- 따라서 minimal-diff + "가시 UI를 blind로 깨지 않는다" 원칙상 **IrisWikiSections 본체는 보존**, clean boundary(usecase line)만 추출.

## IrisMain (별도 note 참조)
`runModuleSpec`(generic dispatch) + 선언형 `INIT_MODULES`로 **이미 helper 흡수 완료** → 변경 없음. `phase9b_irismain_absorption_note.md`.

## Validation (정적 — Menu QA 전)

| Item | 결과 | PASS |
|---|---|:---:|
| Lua syntax (`luac -p`) | 4/4 OK (Wiki/UseCaseLine/Browser/Collector) | ✅ |
| Pulse wrapper untouched | `git status`/`git diff` 빈 출력 + exit 0 | ✅ |
| Require enumeration | caller require 경로 불변(facade) — IrisWikiSections←IrisBrowser/IrisWikiPanel, InteractionRenderer←IrisBrowserDetail | ✅ |
| 9a re-check | Renderer.lua 게이팅 6 guards 유지; Iris/Data 미변경 | ✅ |
| **Menu QA (사용자)** | 재배포 → 메뉴 상세정보를 baseline(`a5054f3`, 탄산)과 비교 | ⏳ |
| **Bootstrap/Tooltip (사용자)** | KO 부팅 `[Iris] Bootstrap complete` + 툴팁 한국어 설명 표시 | ⏳ |

## 사용자 확인 요청 (closeout gate)
재배포 후 **Iris 메뉴에서 탄산(음료수) 상세정보가 baseline과 동일**한지(`phase9b_manual_qa_checklist.md`의 전사 텍스트·레이아웃), 그리고 부팅·툴팁을 확인해 주세요. 동일하면 9b `complete`, 차이(regression)면 revert(§10).

## 후속 메모
- `IrisWikiSections`의 local `getRuntimeLangKey`는 usecase line 이관 후 미사용(dead) — 별도 정리 후보(본 round 보존).
