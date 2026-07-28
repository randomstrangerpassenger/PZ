# Public Text Quality Freshness Policy

다음 constituent 중 하나가 바뀌면 prior foundation consumer 또는 official disposition은 stale이다.

- foundation contract bytes/hash
- policy bytes/hash
- evaluation-subject binding
- metric calculator/schema
- subject-applicable source/runtime bundle 또는 candidate handoff constituent
- applicable waiver set
- human-review selection/decision binding
- G0 materialized plan Git blob 또는 G1/G2/G3 prerequisite 고정 raw SHA,
  HEAD/working-byte identity, receipt/terminal binding
- G3 current facts/manifest Git blob·working-byte identity
- G3 adoption commit/tree identity

foundation contract 변경은 새 `foundation_contract_version`과 새 exact file hash를 요구한다. 기존 foundation hash를 소비한 naturalization corpus, candidate, review, handoff는 stale이며 earliest affected phase부터 재실행한다.

candidate 결과를 본 뒤 threshold, blocker mapping, denominator를 같은 foundation version에서 바꾸는 것은 금지한다.

G3 adoption 또는 current facts/manifest identity가 바뀌면 기존 G4 readiness를
재사용하지 않는다. 같은 policy semantics를 유지하더라도 새 foundation version과
새 exact readiness successor를 생성한다.
