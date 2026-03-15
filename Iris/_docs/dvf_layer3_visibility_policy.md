# DVF 3-3 표시 정책 (Layer 3 Visibility Policy)

**버전**: 1.0
**상태**: FINAL
**날짜**: 2026-03-15

---

## 목적

메뉴 설명란에서 3-3 개별 설명을 어떤 아이템에 표시하고, 어떤 아이템에 비표시하는지 확정한다.

---

## 표시 규칙

| Phase 3 결정 | dvf_3_3_rendered.json | IrisLayer3Data | getText() | 메뉴 표시 |
|---|---|---|---|---|
| APPROVE_SYNC (1089건) | entries에 포함 | 테이블에 포함 | text_ko 반환 | **표시** |
| HOLD | entries에 미포함 | 미포함 | nil 반환 | **비표시** |
| SILENT | entries에 미포함 | 미포함 | nil 반환 | **비표시** |
| 미등록 | entries에 미포함 | 미포함 | nil 반환 | **비표시** |

---

## 이번 배치 성격

- 원본 1050건: 전량 `DIRECT_ACQUISITION_READY` (acquisition 본문)
- CPR 39건: `IDENTITY_LINKED` (33건) + `USE_CONTEXT_LINKED` (6건) — 전부 APPROVE_SYNC
- compose 프로파일: `acq_location`/`acq_method` (원본) + `identity_acq`/`use_acq` (CPR)
- 전체 1089건 모두 acquisition 본문 성격

---

## 구현 매핑

`layer3_renderer.lua` (DVF 계약 §5.2):

```lua
entry = descriptions[fullType]
if entry and entry.text_ko then
    render(entry.text_ko)
end
-- 그 외: 아무것도 하지 않음
```

이 코드가 표시 정책을 자동으로 이행한다:
- `IrisLayer3Data`에 있으면 → text_ko 반환 → 표시
- 없으면 → nil → 비표시

---

## 금지 사항

- HOLD/SILENT 아이템의 text_ko를 다른 소스에서 fallback 생성하는 것 금지
- 비표시 상태를 에러 메시지나 플레이스홀더로 대체하는 것 금지
- 비표시는 "빈 칸"이며, 이는 의도된 상태
