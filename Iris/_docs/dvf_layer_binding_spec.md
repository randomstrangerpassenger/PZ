# DVF 설명란 레이어 바인딩 명세 (Layer Binding Spec)

**버전**: 1.0
**상태**: FINAL
**날짜**: 2026-03-15

---

## 목적

Iris 메뉴 설명란의 5계층이 각자의 칸에만 연결되는 규칙을 확정한다.

---

## 5계층 바인딩 매핑

| 헌법 계층 | 코드 위치 | 데이터 소스 | 성격 |
|---|---|---|---|
| 3-1 기초 설명 | `IrisWikiSections.renderCoreInfoSection()` | 아이템 Java 메서드 (getWeight, getType, getMinDamage 등) | 수치/속성 |
| 3-2 주 소분류 설명 | `IrisWikiSections.renderUseCaseSection()` | `IrisUseCaseDescriptions.lua` | 행위 중심 UseCase |
| 3-3 개별 설명 | `Layer3Renderer.getText()` via `getAllSections():296-310` | `IrisLayer3Data.lua` | 개별 acquisition 본문 |
| 3-4 상호작용 | `IrisWikiSections.renderConnectionSection()` | IrisAPI (Recipe/Moveables/Fixing) | 연결 정보 |
| 3-5 내부 정보 | `IrisWikiSections.renderMetaInfoSection()` | IrisAPI 분류ID, 아이템 메서드(모듈) | 분류/모듈 메타 |

---

## 경계 규칙

### 물리적 경계
- 각 계층은 `IrisWikiSections.lua` 내 독립 함수로 구현됨
- `getAllSections()`가 순차적으로 호출하되, 각 함수는 자기 데이터 소스만 접근
- 3-3 (`Layer3Renderer`)은 `IrisLayer3Data`만 참조, 다른 데이터 모듈 미접근

### 의미적 경계
- **3-3이 3-4를 대체하면 안 됨**: 3-3은 acquisition 본문(어디서/어떻게 얻는가), 3-4는 상호작용 연결(Recipe/Moveables/Fixing). 성격이 다름.
- **3-5 내부 정보가 3-3 본문으로 새면 안 됨**: 분류ID(Tool.1-A 등), 모듈명(Base, Hydrocraft 등)은 3-5 영역. 3-3 본문에 이런 식별자가 나오면 T-Gate T3(내부키노출)에서 차단됨.
- **3-3이 3-2를 반복하면 안 됨**: UseCase Block의 행위 설명을 3-3에서 다시 말하면 의미적 중복. T-Gate T4(유사도 WARN)에서 감지.

### HOLD/SILENT 처리
- KEEP_HOLD 아이템 → `IrisLayer3Data`에 미포함 → `getText()` = nil → 3-3 칸 비표시
- KEEP_SILENT 아이템 → `IrisLayer3Data`에 미포함 → `getText()` = nil → 3-3 칸 비표시
- 다른 계층(3-1, 3-2, 3-4, 3-5)은 HOLD/SILENT와 무관하게 정상 작동

---

## 참조

- `Iris/media/lua/client/Iris/UI/Wiki/IrisWikiSections.lua` — 5계층 렌더링 구현
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua` — 3계층 전용 렌더러
- `Iris/_docs/description_validation_contract.md` — DVF 계약 (4원칙, T-Gate)
