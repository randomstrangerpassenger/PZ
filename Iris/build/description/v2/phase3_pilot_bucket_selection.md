# Phase 3 Pilot Bucket Selection

> 현재 `staging/reviews` 기준으로 파일럿은 high-signal 1개와 mixed 1개를 고른다.

---

## 1. Pilot A: `Consumable.3-C`

- 현재 Phase 2 닫힌 row 수: 27
- disposition 분포: `ACQ_HINT=27`
- 선택 이유:
  - 의료 소모품이라 획득 장소와 제작 방식이 개별 이해에 직접 연결된다.
  - bucket 크기가 작아 promote 기준을 빠르게 검증하기 좋다.
  - `Bandage`, `AlcoholWipes`, `DenimStrips`처럼 location/method specific 사례가 명확하다.

이 버킷은 promote threshold 점검용이다.

## 2. Pilot B: `Tool.1-L`

- 현재 Phase 2 닫힌 row 수: 45
- disposition 분포: `ACQ_HINT=40`, `ACQ_NULL=5`
- 선택 이유:
  - 가방/용기 계열이라 generic keep, specific promote, manual 경계가 실제로 섞여 있다.
  - `Doctor Bag`, `Briefcase` 같은 specific case와 `Pistol Case` 같은 standardization 불가 case가 공존한다.
  - manual 진입 조건과 notes 사용 규칙을 같이 검증할 수 있다.

이 버킷은 keep/manual/promote balance 점검용이다.

## 3. 샘플 크기

- 권장: Pilot A 전수 27건 + Pilot B 전수 45건
- 교차 검토: Pilot B에서 최소 10건 재판정

전수 기준으로 시작하면 bucket 내부 편차를 숨기지 않는다.
