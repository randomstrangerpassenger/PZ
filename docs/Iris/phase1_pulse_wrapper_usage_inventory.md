# Phase 1 — Pulse Compatibility Wrapper Usage Inventory

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §6 Change 1 / Change 9b, §8 Compatibility Surface.
> 측정일: 2026-06-07 (repo root cwd).
> 대상: `Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/{Generator,Logger,Ordering,Renderer,TagParser,Templates}.lua` (6개).
> 관련 conflict: 14.5 (compatibility surface). downstream blocking: Phase 9b.

## 요약

6개 Pulse wrapper는 전부 **단일 라인 리다이렉트 shim**이다. 내부 Iris Lua 코드에서 Pulse 네임스페이스를
명시적으로 `require`하는 곳은 **0건**이며, 존재 목적은 외부 소비자(과거 `Pulse/Iris/Logic/IrisDesc/*`
경로를 require하던 코드)를 위한 후방 호환 네임스페이스다. 모두 git-tracked·clean 상태이며 sealed
protected-surface 해시 집합에 포함되어 있다. **본 계획에서 제거/변경 금지**(governance §11, 계획 §2/§8);
Change 9b는 disposition note만 작성한다.

## Wrapper 내용 (전수 확인)

| Wrapper (`Pulse/Iris/Logic/IrisDesc/`) | 파일 내용 | 리다이렉트 대상 | 대상 존재 | 대상 tracked |
|---|---|---|:---:|:---:|
| `Generator.lua` | `return require("Iris/Logic/IrisDesc/Generator")` | `Iris/Logic/IrisDesc/Generator.lua` | ✅ | ✅ |
| `Logger.lua` | `return require("Iris/Logic/IrisDesc/Logger")` | `Iris/Logic/IrisDesc/Logger.lua` | ✅ | ✅ |
| `Ordering.lua` | `return require("Iris/Logic/IrisDesc/Ordering")` | `Iris/Logic/IrisDesc/Ordering.lua` | ✅ | ✅ |
| `Renderer.lua` | `return require("Iris/Logic/IrisDesc/Renderer")` | `Iris/Logic/IrisDesc/Renderer.lua` | ✅ | ✅ |
| `TagParser.lua` | `return require("Iris/Logic/IrisDesc/TagParser")` | `Iris/Logic/IrisDesc/TagParser.lua` | ✅ | ✅ |
| `Templates.lua` | `return require("Iris/Logic/IrisDesc/Templates")` | `Iris/Logic/IrisDesc/Templates.lua` | ✅ | ✅ |

현재 디렉토리는 정확히 위 6개 파일만 보유한다(과거 `console_log.txt`에 보이던 `TestHarness.lua`는 현재 부재
— 6-wrapper scope 밖, disposition 대상 아님).

## Tracked / Ignore 상태

| 항목 | 결과 | 근거 명령 |
|---|---|---|
| git-tracked | **6/6 tracked** | `git ls-files -- 'Iris/media/lua/client/Pulse/Iris/Logic/IrisDesc/*.lua'` → 6 |
| gitignore 적용 | **미적용** | `git check-ignore -v <Generator.lua>` → `$LASTEXITCODE = 1` (not ignored) |
| working tree 변경 | **없음(clean)** | `git status --short -- <dir>` → stdout 빈 출력 |
| HEAD 대비 변경 | **없음(clean)** | `git diff --name-only HEAD -- <dir>` → stdout 빈 출력 |

> Change 9b "Pulse wrapper untouched" 검증의 baseline은 **현재 두 명령 모두 stdout 빈 출력 + `$LASTEXITCODE -eq 0`**
> (= clean)이다. tracked 파일이므로 `git diff --name-only HEAD`(tracked 수정 감지)와 `git status --short`
> (staged/working/untracked 감지) 두 safety net이 모두 유효하다(계획 §6 Change 9b Implementation Notes 역할 분담).

## 참조처 (repo-wide grep: `Pulse[./\\]Iris[./\\]Logic[./\\]IrisDesc`)

| 참조 유형 | 위치 | 의미 |
|---|---|---|
| 내부 명시적 `require` | **0건** (Iris/media/lua 코드 내) | Iris 런타임 코드는 canonical `Iris/Logic/IrisDesc/*`만 require. Pulse 경로 직접 require 없음 |
| 런타임 auto-load | `console_log.txt` (boot 로그) | PZ가 media/lua 트리를 boot 시 자동 로드 → wrapper가 canonical로 리다이렉트. 명시적 require 아님 |
| governing docs | `docs/ROADMAP.md:494`, `docs/ARCHITECTURE.md:348` | "`Iris/Logic/IrisDesc/*`가 current namespace, `Pulse/Iris/Logic/IrisDesc/*`는 compatibility wrapper" 공식 명시 |
| sealed 보호 해시 | `docs/Iris/Done/iris-dvf-3-3-...protected-surface-hashes.{before,after}.json` | 6개 wrapper가 protected-surface 해시 집합에 등재(이전 DVF 3.3 round seal) |
| 계획/리뷰 docs | `docs/Iris/Iris_Refactoring_Plan*.md`, `*_Review*.md` | 본 refactoring 계획 자체의 참조 |

## conflict 14.5 / Change 9b 함의

- 6개 wrapper는 compatibility surface로 **확정**(governance §11 + ARCHITECTURE.md/ROADMAP.md 명시 인용). conflict 14.5는 `resolved`로 닫을 수 있다(roadmap B 채택: Pulse wrapper = compat surface).
- 제거/변경은 deprecation/release decision 전까지 금지. Change 9b는 `phase9b_compat_wrapper_disposition_note.md`에 disposition만 기록.
- sealed protected-surface 해시에 포함되므로, 어떤 phase에서든 이 6개 파일의 SHA drift는 §10 Rollback의 sealed artifact 절차 대상이다.
