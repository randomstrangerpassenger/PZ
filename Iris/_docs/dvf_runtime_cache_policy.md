# DVF 런타임 캐시 정책 (Runtime Cache Policy)

**버전**: 1.0
**상태**: FINAL
**날짜**: 2026-03-15

---

## 목적

DVF 3-3 데이터의 런타임 로딩, 캐싱, fallback 동작을 확정한다.

---

## 로드 시점

- **Lazy load**: 최초 `Layer3Renderer.getText()` 호출 시 1회 로드
- `ensureData()` 함수가 `IrisLayer3Data` 전역 테이블을 읽어 `layer3Data` 로컬 변수에 캐시
- `dataLoaded` 플래그로 2회 이상 로드 방지

---

## 캐시 정책

| 항목 | 정책 |
|---|---|
| 최초 로드 | 게임 시작 후 최초 `getText()` 호출 시 |
| 캐시 방식 | 모듈 레벨 변수 (`layer3Data`) |
| 재로드 | 없음 (게임 세션 중 데이터 불변) |
| 메뉴 재진입 시 | 캐시 사용 (재조회 없음) |
| 메모리 해제 | 게임 종료 시 자동 |

---

## Fallback 정책

| 상황 | 동작 |
|---|---|
| `IrisLayer3Data` 정상 로드 | 로그: `[Layer3Renderer] Loaded: N entries` |
| `IrisLayer3Data` 없음 | 로그: `[Layer3Renderer] WARNING: IrisLayer3Data not available` + nil 반환 |
| 특정 fulltype 미존재 | nil 반환 (로그 없음 — 정상 동작) |
| pcall 실패 | nil 반환 + 1회 경고 로그 |

---

## 원칙

1. **silent failure 없음**: 데이터 부재 시 반드시 1회 WARNING 로그
2. **빈 칸 fallback**: 에러 UI가 아닌 nil 반환 (설명란에서 3-3 칸 자체가 미출력)
3. **중간 산출물 직접 참조 금지**: `layer3_renderer.lua`는 `IrisLayer3Data` 전역 테이블만 접근
4. **결정론적**: 동일 입력 → 동일 출력, 런타임 조건 분기 없음
