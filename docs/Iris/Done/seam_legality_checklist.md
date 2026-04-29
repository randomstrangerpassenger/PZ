# Seam Legality Checklist

> 상태: Draft v0.1  
> 기준일: 2026-04-20  
> 라운드: `Iris DVF 3-3 compose authority migration round` Phase B  
> canonical spec: `docs/Iris/Done/dvf_3_3_cross_layer_overlay_spec.md`

이 체크리스트는 `body_source_overlay` seam과 validator 경계가 합법적으로 닫혔는지 검토하기 위한 Phase B artifact다.

---

## 1. Schema / Ownership

- [ ] compose가 raw 1/2/4계층 source를 직접 읽지 않고 `body_source_overlay`만 읽는다.
- [ ] `facts / decisions / overlay / validator / runtime` owner가 문서상 분리돼 있다.
- [ ] overlay가 `compose_profile`, section policy, `quality_state`, `publish_state`를 쓰지 않는다.
- [ ] output 계약이 flat string으로 유지된다.
- [ ] Browser / Wiki / Lua bridge가 compose를 대신하지 않는다.

## 2. Decisions Overlay Relation

- [ ] `layer3_role_check`와 overlay의 무권한 관계가 명시돼 있다.
- [ ] `representative_slot`, `body_slot_hints`, `representative_slot_override`와 overlay의 precedence가 명시돼 있다.
- [ ] section policy / representative policy / legality는 `decisions > overlay`라는 점이 명시돼 있다.
- [ ] overlay hint와 decisions authority의 직접 충돌 시 판정이 정의돼 있다.

## 3. Validator Scope

- [ ] validator 역할이 drift-checker / legality-checker로 제한돼 있다.
- [ ] validator가 rendered 문장을 고치지 않는다고 명시돼 있다.
- [ ] validator가 `quality_state`와 `publish_state`를 기록하지 않는다고 명시돼 있다.
- [ ] `required / optional / required_any` legality만 검사한다고 명시돼 있다.
- [ ] `hard fail / warn / skip` matrix가 명시돼 있다.
- [ ] validator scope가 별도 신규 canonical 문서가 아니라 overlay spec appendix에 귀속돼 있다.

## 4. Drift / Legality

- [ ] overlay row count와 facts row count exact match 규칙이 있다.
- [ ] `item_id` set exact match 규칙이 있다.
- [ ] hint 타입이 `string | null`로 고정돼 있다.
- [ ] non-null hint의 source lineage 부재가 `hard fail`로 정의돼 있다.
- [ ] layer2 anchor export 부재가 explicit `skip`으로 정의돼 있다.
- [ ] representative lineage 존재 + registry/derivation 결과 누락이 `warn`으로 정의돼 있다.

## 5. Structural Signal Handling

- [ ] Phase C 실행 중 structural signal은 observer-only라고 명시돼 있다.
- [ ] structural signal이 Phase C exit blocker가 아니라고 명시돼 있다.
- [ ] semantic adjudication이 Phase D 책임이라고 명시돼 있다.
- [ ] `2026-04-05` next-build feedback 원칙과 정합하다고 명시돼 있다.

## 6. Forbidden Path Closure

- [ ] compose external repair 금지
- [ ] post-validator rewrite 금지
- [ ] runtime patch 금지
- [ ] style linter 승격 금지
- [ ] overlay builder writer 승격 금지
- [ ] validator writer 승격 금지
- [ ] raw layer direct read 금지
- [ ] same-build structural signal re-compose 금지
- [ ] external adapter preprocessor 금지

## 7. Exit Read

Phase B closeout은 아래 질문에 모두 `yes`일 때만 통과로 읽는다.

- [ ] Phase C 구현자가 `body writer가 먹는 입력`을 추측 없이 참조할 수 있는가
- [ ] same-build rewrite path가 문서상 완전히 닫혀 있는가
- [ ] `2026-04-06` single writer와 충돌하지 않는가
- [ ] current spec package가 새 canonical 문서를 무분별하게 늘리지 않는가
