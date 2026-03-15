# DVF 런타임 입력 계약 (Runtime Input Contract)

**버전**: 1.0
**상태**: FINAL
**날짜**: 2026-03-15

---

## 목적

Iris 메뉴 런타임이 어떤 파일을 읽고, 어떤 파일을 읽지 않는지를 확정한다.

---

## 정규 런타임 입력 경로

```
dvf_3_3_rendered.json (빌드 산출물)
  → convert_layer3_to_lua.py (빌드 시 변환)
  → IrisLayer3Data.lua (런타임 소비자 입력)
  → layer3_renderer.lua.ensureData()
  → Layer3Renderer.getText(fullType)
```

**Canonical Runtime Source**: `Iris/media/lua/client/Iris/Data/IrisLayer3Data.lua`

---

## 런타임이 읽어야 할 것

| 파일 | 역할 | 비고 |
|---|---|---|
| `IrisLayer3Data.lua` | 3계층 개별 설명 텍스트 | 빌드 시 `dvf_3_3_rendered.json`에서 변환 |

---

## 런타임이 읽지 말아야 할 것

| 파일 | 이유 |
|---|---|
| `dvf_3_3_rendered.json` | 빌드 산출물 원본. Lua 변환물만 소비. |
| `dvf_3_3_decisions.jsonl` | 오프라인 파이프라인 중간 산출물 |
| `dvf_3_3_facts.jsonl` | 오프라인 파이프라인 중간 산출물 |
| `phase3_sync_queue.jsonl` | Phase 3 스테이징 파일 |
| `candidate_state_phase3.review.jsonl` | Phase 3 리뷰 파일 |
| `dvf_3_3_validation_report.json` | 검증 리포트 (런타임 불필요) |
| `dvf_3_3_summary.json` | 빌드 요약 (런타임 불필요) |

---

## layer3_by_fulltype.json의 위상

`Iris/output/layer3_by_fulltype.json`은 T-Gate 파이프라인(경로 A)의 산출물이다.

- **현재 상태**: Phase 3 compose 경로(경로 B)가 실제 데이터 소스이므로, 이 파일은 compatibility/debug artifact로 동기화한다.
- **canonical runtime source가 아님**: 런타임 정규 경로는 `IrisLayer3Data.lua`
- 이 파일을 런타임이 직접 읽어서는 안 된다.

---

## 원칙

1. **런타임은 최종 Lua 변환물만 소비한다.**
2. **중간 파일 직접 참조는 금지한다.**
3. **빌드 시점과 런타임 시점의 관심사를 분리한다.**
