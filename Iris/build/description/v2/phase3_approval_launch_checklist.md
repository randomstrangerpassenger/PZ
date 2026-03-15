# Phase 3 Approval Launch Checklist

> approval backlog 처리 착수 전 반드시 확인해야 할 조건 5개.
> 전부 PASS해야 첫 번째 cluster review를 열 수 있다.

---

## Checklist

| # | 조건 | 검증 방법 | 결과 |
|---|---|---|---|
| 1 | candidate-state canonical SHA 불변 | `phase3_candidate_state_summary.json` SHA 대조: `409dff500686f4b7058484437c5c05d74640dc74c86a2d5cd87d32965621086a` | ☐ |
| 2 | `approval_state` 필드만 변경 대상 | `candidate_state`, `candidate_reason_code`, `candidate_compose_profile` 변경 금지 재확인 | ☐ |
| 3 | `phase3_notes` 읽기 전용 | 판정 근거 텍스트 덮어쓰기 금지. approval 메모는 `cluster_note` / `hold_note`만 사용 | ☐ |
| 4 | 메모 필드 분리 원칙 | `phase3_notes` ≠ approval 메모. 두 계층이 같은 필드를 쓰지 않음 | ☐ |
| 5 | hotspot cluster JSON 단일 소스 고정 | `staging/phase3/phase3_approval_hotspot_clusters.json`이 유일한 정의 소스임을 확인 | ☐ |

## Gate

- 5개 전부 ☑ → approval backlog 처리 시작 가능
- 1개라도 ☐ → 해당 조건 해소 후 재확인
