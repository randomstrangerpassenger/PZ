# Iris DVF 3-3 Reopen Round Sizing Governance Closeout

> 상태: Final v1.0  
> 기준일: 2026-04-20  
> 상위 기준: `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> supporting review: `docs/Iris/iris-dvf-3-3-reopen-round-sizing-governance-consistency-review.md`  
> 목적: reopen round sizing governance amendment의 closeout 판정과 current-state reading을 문서로 봉인한다.

---

## 1. Closeout 판정

- `A complete`
  - amendment text adopted
  - 적용 범위는 future explicitly-opened `A-4-1 / cluster-budget reopen`으로 고정
  - lane ownership / subset-bounded sizing / reusable-first sequencing rule이 채택됨
  - existing decisions와 비충돌 확인 완료
- `B not opened`
  - `bucket_1 / bucket_2` execution plan은 이번 round에서 열지 않음
  - current terminal snapshot은 무변경
  - runtime / publish contract는 무변경

## 2. Current-State Reading

- current state는 여전히 `no_immediate_next_round_planned = true`로 읽는다.
- amendment 채택은 current reopen opening이나 carry-over queue 생성을 뜻하지 않는다.
- explicit future `A-4-1 / cluster-budget reopen`이 실제로 열릴 때만 이번 rule이 manifest sizing authority로 작동한다.

## 3. Reopen 허용 조건

- explicit `A-4-1 rework / cluster budget` reopen gate가 실제로 열린 경우
- future round owner가 first manifest를 작성하는 경우
- 위 시점에서 bounded subset, single-authority, reusable-first sequencing을 적용해야 하는 경우

## 4. Reopen 금지 해석

- amendment adoption 자체를 current reopen opening으로 읽는 것
- `future_new_source_discovery_hold`까지 이번 amendment의 적용 대상으로 확장하는 것
- current terminalized lane를 unfinished execution debt처럼 다시 읽는 것
- `30-cap` 재검토나 closure policy widening을 이번 amendment 안에서 같이 여는 것

## 5. Review Summary

- Good: scope lock, governance text, `DECISIONS.md` authority, consistency review가 같은 읽기 규칙 위에서 닫혔다.
- Critical: 없음.
- Important: 없음.
- Minor: 없음.
- PASS / FAIL: PASS.
