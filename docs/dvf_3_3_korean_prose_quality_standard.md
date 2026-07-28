# DVF 3-3 Korean Prose Quality Standard

이 문서는 DVF 3-3 candidate 문장의 realization 및 raw 측정 기준을 정의한다. 공개 품질의 blocker/advisory/human-only 분류, threshold, waiver, item disposition과 aggregate disposition은 Publish Boundary가 소유한다.

## 역할 경계

- source proposition은 approved facts/decisions/source-supported field에서만 나온다.
- profile과 `body_plan`은 structural role, requirement, ordering만 제공한다.
- current surface snapshot은 회귀 비교 자료이며 semantic authority나 정답 corpus가 아니다.
- candidate는 staging 전용이며 current rendered, Lua, runtime chunk, package를 수정하지 않는다.

## 결함 분류

- identity noun의 불필요한 반복
- use/context proposition의 중복 실현
- `작업`, `맥락`, `용도` 같은 assembler 추상어 노출
- acquisition subtype 평탄화
- section별 paragraph 파편화
- required shape를 채우기 위한 filler
- 넓은 category만 말하는 첫 문장
- 반복 sentence skeleton 집중
- 수동·번역투 표현
- source가 지지하지 않는 사실·추천·비교·절차 추론

## 기계 측정과 사람 검토

raw detector는 전체 candidate denominator에서 hit/no-hit을 기록할 뿐 disposition을 만들지 않는다. 사람 검토는 foundation이 봉인한 exact-hash deterministic strata sample 안에서 readability, naturalness, semantic fidelity, public suitability를 각각 판정한다. 표본 검토를 corpus 전체 human-only blocker 0으로 확대하지 않는다.

## Compiler-invalid 조건

빈 adopted body, 미등록 transformation, source proposition 없는 clause, item-specific patch/override/branch, 제한을 넘는 장문은 compiler contract failure다. 이는 Publish disposition과 별개다.
