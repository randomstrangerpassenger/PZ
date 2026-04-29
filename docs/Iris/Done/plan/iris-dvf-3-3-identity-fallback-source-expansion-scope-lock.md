# Iris DVF 3-3 Identity Fallback Source Expansion Scope Lock

> 상태: Revised Draft v0.2  
> 기준일: 2026-04-14  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 동반 문서: `docs/iris-dvf-3-3-identity-fallback-source-expansion-execution-plan.md`  
> canonical input: `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/identity_fallback_source_expansion_backlog.json`  
> 목적: `identity_fallback 617` 후속 라운드가 compose 재설계, style 강화, state 의미 재정의로 번지지 않도록 범위를 먼저 봉인한다.

> 이 문서는 상위 문서의 하위 운영 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

---

## 0. 라운드 정체성

이번 라운드는 아래 한 줄로 닫는다.

> 닫힌 `facts -> decisions -> compose -> normalizer -> style linter -> rendered -> Lua bridge -> runtime` 파이프라인 위에서,  
> `identity_fallback 617`의 source evidence를 확보해 기존 facts 슬롯을 채우고  
> `identity_fallback -> cluster_summary` 중심의 경로 전환과 `internal_only -> exposed` 확대를 수행하는 **source expansion round** 다.

이 문장은 아래 넷을 동시에 뜻한다.

- 이번 라운드는 compose 재설계 라운드가 아니다.
- 이번 라운드는 style 개선 라운드가 아니다.
- 이번 라운드는 active/silent 의미 재정의 라운드가 아니다.
- 이번 라운드는 three-axis contract 구조 변경 라운드가 아니다.

`direct_use`는 금지 경로가 아니지만 기본 목표도 아니다.  
기본 승격 경로는 `cluster_summary`이며, `direct_use`는 새 슬롯 확장 없이 item-specific body가 명시적 source evidence로 바로 닫힐 때만 예외적으로 허용한다.  
current authoritative compose path 이름은 `cluster_summary / identity_fallback / role_fallback / direct_use`로만 읽는다.  
`special_context` 같은 비-canonical 명칭은 planning memo일 수는 있어도 authoritative lane은 아니다.

---

## 1. Baseline Snapshot

current round baseline은 아래처럼 고정한다.

| 항목 | 값 |
|---|---|
| total rows | 2105 |
| active | 2084 |
| silent | 21 |
| active origin | `cluster_summary 1440 / identity_fallback 617 / role_fallback 48` |
| publish split | `internal_only 617 / exposed 1467` |
| canonical input | `identity_fallback_source_expansion_backlog.json` |
| handoff alignment | `617 / 617 / 617` |
| bucket split | `bucket_1 11 / bucket_2 599 / bucket_3 7` |

supporting authority는 아래 artifact를 읽는다.

- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/identity_fallback_source_expansion_backlog.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/identity_fallback_policy_isolation_report.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_baseline_v4.json`
- `Iris/build/description/v2/staging/semantic_quality/phaseE_contract_migration/quality_publish_decision_preview_summary.json`

---

## 2. Hard No List

이번 라운드에서 열지 않는 항목은 아래처럼 고정한다.

- compose 외부 repair / same-build re-compose stage 재도입
- facts 슬롯 확장
- style linter의 publish gate 승격
- active/silent 재판정 및 `active` 의미 재정의
- `runtime_state / publish_state / quality_state` 축 구조 변경
- `FUNCTION_NARROW` blanket isolation 재개방
- `ACQ_DOMINANT` blanket isolation 재개방
- `bucket_3` 실행
- semantic weak candidate의 semantic axis 자동 반영
- 한국어 엔진 / runtime josa engine 도입
- 3-3 본문을 이유로 3-4 상세를 흡수하는 것

위 항목이 필요해지는 순간, 그 작업은 이번 라운드 scope 밖이다.

---

## 3. 운영 불변식

- canonical input은 항상 `identity_fallback_source_expansion_backlog.json` 하나로 읽는다.
- facts는 기존 슬롯 안에서만 채운다.
- source expansion은 upstream evidence/facts/decisions만 바꾸고 downstream pipeline 구조는 바꾸지 않는다.
- `publish_state` 승격은 source ownership이 강해진 뒤에만 검토한다.
- regression gate의 보호 대상은 round opening baseline `exposed 1467`에 이후 batch에서 정식 promote된 row를 합친 **current exposed surface 전체**다.
- `bucket_1`은 reuse-fast lane, `bucket_2`는 net-new cluster lane, `bucket_3`는 explicit hold lane으로 유지한다.
- `manual lane`은 evidence 부족을 뜻할 뿐, contract 예외를 뜻하지 않는다.
- `3-3`은 계속 item-centric body이며 `3-4` 상세를 대체하지 않는다.

---

## 4. 선행 라운드 닫힘 상태

이번 라운드는 아래 닫힌 상태를 재오픈하지 않는다.

- role_fallback hollow terminalized
- acquisition lexical standardization closed
- surface contract authority migration closed
- body-role round closed

즉 이번 라운드의 시작점은 `current phaseE handoff artifact` 위의 follow-up execution이지, 이전 라운드 재개방이 아니다.

---

## 5. 종료 문장

이번 라운드의 self-check는 아래 문장이 유지되는 상태다.

> 이건 `identity_fallback 617`의 source expansion round다.  
> compose/style/state 구조를 다시 여는 라운드가 아니다.
