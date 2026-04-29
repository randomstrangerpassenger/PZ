# DVF 3-3 Cross-Layer Overlay Spec

> 상태: draft v0.2  
> 기준일: 2026-04-20  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`  
> 선행 기준: `docs/Iris/Done/dvf_3_3_information_type_contract.md`, `docs/Iris/Done/dvf_3_3_compose_v2_spec.md`  
> current round plan: `docs/Iris/iris-dvf-3-3-compose-authority-migration-round-final-integrated-plan.md`

---

## 1. 목적

이 문서는 `body_source_overlay`를 3계층 compose의 유일한 cross-layer 입력 seam으로 정의한다.

핵심은 아래 두 가지다.

- compose는 1/2/4계층 raw source를 직접 읽지 않는다.
- cross-layer 지원은 사전 생성된 overlay를 통해서만 들어온다.

즉, overlay는 source 재서술 계층이지 profile writer나 publish writer가 아니다.

2026-04-20 기준 current reading에서 이 문서는 **compose authority migration round의 Phase B canonical closeout spec** 이다.

- seam ownership
- decisions overlay 관계
- validator scope
- same-build rewrite closure

를 한 문서 안에서 닫는다.

---

## 2. ownership 경계

overlay는 **source restatement layer**다.

overlay가 가지는 책임:

- 1계층 정체성 힌트의 합헌적 restatement
- 2계층 anchor 힌트의 합헌적 restatement
- 4계층 대표 작업 맥락의 합헌적 restatement

overlay가 가지지 않는 책임:

- `compose_profile` 확정
- section 포함/제외 정책 결정
- quality_state 기록
- publish_state 기록
- budget 비율 계산
- structural signal의 semantic adjudication

같은 Phase B 경계에서 다른 owner는 아래처럼 고정한다.

- `facts`
  - item canonical fact와 slot-level source truth
- `decisions`
  - compose policy, role/representative 계열 authority, post-compose decision input
- `body_source_overlay`
  - cross-layer hint restatement만 담당
- validator
  - drift / legality checker
- runtime consumer
  - staged authority render-only consumer

따라서 아래 필드는 overlay에 두지 않는다.

- `body_scope_profile`
- `cross_layer_support_budget`

---

## 3. overlay 스키마

`body_source_overlay`는 row당 아래 필드만 가진다.

```text
item_id
layer1_identity_hint
layer2_anchor_hint
layer4_context_hint
```

필드 의미는 아래처럼 고정한다.

- `layer1_identity_hint`
  - 1계층 기초 정체성의 restatement hint
  - 예: `도구`, `의류`, `가방`
- `layer2_anchor_hint`
  - 2계층 주 소분류 anchor의 restatement hint
  - canonical anchor export가 없으면 `null`
- `layer4_context_hint`
  - 4계층 representative work context hint
  - 목록형 상세가 아니라 단일 context phrase

모든 hint는 `string | null`이다.

---

## 4. current builder 입력 artifact

2026-04-11 기준 current builder는 아래 artifact를 입력으로 읽는다.

### 필수 입력

- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
  - `layer1_identity_hint`의 current canonical seed
- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
  - item set alignment와 selected cluster fallback source
- `Iris/build/description/v2/staging/interaction_cluster/interaction_cluster_compose_input.jsonl`
  - `selected_cluster` current compose authority source
- `Iris/build/description/v2/data/interaction_clusters.json`
  - `selected_cluster -> label_ko` registry

### 선택 입력

- future layer2 anchor export artifact
  - 예: `primary_subcategory` export json/jsonl
  - 현재 build tree에는 canonical exported artifact가 없으므로 기본값은 미연결이다.

current implementation script:

- `Iris/build/description/v2/tools/build/build_layer3_body_source_overlay.py`

current validator:

- `Iris/build/description/v2/tools/build/validate_layer3_body_source_overlay.py`

---

## 5. current derivation rule

2026-04-11 기준 builder의 deterministic derivation rule은 아래처럼 고정한다.

### `layer1_identity_hint`

- source: `facts.identity_hint`
- rule:
  - non-empty string이면 그대로 채운다.
  - 비어 있으면 `null`

### `layer2_anchor_hint`

- source: optional future anchor export
- rule:
  - canonical anchor export가 제공되면 그 row의 anchor label을 채운다.
  - export가 없으면 전 row `null`

이 정책은 임시 추론이 아니라 명시적 보수 정책이다.  
current build tree에 2계층 anchor export artifact가 없으므로 억지 해석으로 메우지 않는다.

### `layer4_context_hint`

- source:
  - `interaction_cluster_compose_input.selected_cluster`
  - fallback: `decisions.selected_cluster`
  - fallback: `facts.slot_meta.interaction_cluster.selected_cluster`
- rule:
  - `selected_cluster`가 있으면 `interaction_clusters.json`의 `label_ko`를 채운다.
  - 없으면 `null`

예:

- `metalwork_welding -> 금속 접합 작업`
- `container_storage -> 보관 및 휴대 작업`

이 값은 recipe list나 action list가 아니라 representative work context phrase다.

---

## 6. decisions overlay 관계 / precedence / drift rule

`body_source_overlay`는 existing decisions overlay와 나란히 존재하지만, 같은 권한을 갖지 않는다.

### 6-1. relation

- `layer3_role_check`
  - overlap 없음
  - role legality / closure signal owner는 계속 decisions 쪽이다.
- `representative_slot`
  - representative selection authority는 계속 decisions 쪽이다.
  - `layer4_context_hint`는 그 결과를 돕는 support material일 뿐이다.
- `body_slot_hints`
  - section candidate 또는 repair hint authority는 계속 decisions 쪽이다.
  - overlay는 support phrase를 추가할 뿐 section policy를 정하지 않는다.
- `representative_slot_override`
  - override precedence는 decisions 쪽이 더 높다.
  - overlay는 override를 뒤집지 못한다.

### 6-2. precedence

- section policy / representative policy / legality는 `decisions > overlay` 순서다.
- overlay는 section material supplier이지 policy writer가 아니다.
- non-null overlay hint가 있어도 decisions가 해당 section을 금지하면 writer는 그 hint를 소비하지 않는다.

### 6-3. drift detection rule

- `item_id` alignment 불일치 -> `hard fail`
- non-null overlay hint에 supporting source lineage가 없음 -> `hard fail`
- canonical source lineage가 없어서 hint를 만들 수 없음
  - `layer2_anchor_hint` -> explicit `skip`
  - `layer4_context_hint` -> explicit `skip`
- representative lineage는 있으나 registry/derivation 결과가 빠짐 -> `warn`
- overlay hint가 decisions authority와 직접 충돌
  - 예: override/selected representative와 source lineage가 다른 context를 가리킴
  - 판정: `hard fail`

---

## 7. compose 소비 계약

compose v2는 아래 규칙을 따라야 한다.

- raw 1/2/4계층 source를 직접 읽지 않는다.
- `body_source_overlay`만 읽는다.
- hint가 `null`이면 해당 support section은 deterministic omission 후보가 된다.
- hint가 non-null이어도 body를 지배하면 안 된다.

즉, overlay는 section material의 공급원이지 section policy 자체는 아니다.

---

## 8. rendered flat string / runtime ownership 재확인

- output은 계속 flat string이다.
- `body_plan` section trace는 internal meta일 수 있지만 runtime consumer input이 아니다.
- `quality/publish decision stage`는 flat rendered string과 existing decision input shape를 계속 소비한다.
- Lua bridge / Browser / Wiki는 staged authority만 소비한다.
- browser / wiki / Lua bridge가 compose를 대신하면 안 된다.

---

## 9. validator scope appendix

이 섹션은 current Phase B round에서 별도 `validator_scope_spec.md`를 열지 않고, **이 문서의 appendix** 로 validator scope를 닫는다.

### 9-1. validator 역할 한정

- validator는 drift-checker / legality-checker까지만 수행한다.
- validator는 rendered 문장을 고치지 않는다.
- validator는 section policy를 대신 결정하지 않는다.
- validator는 `quality_state`나 `publish_state`를 기록하지 않는다.

### 9-2. legality scope

- `required / optional / required_any` legality만 검사한다.
- overlay row count = facts row count
- `item_id` set exact match
- hint 값은 `string | null`
- `layer4_context_hint`가 있으면 compose input row와 item alignment가 존재해야 한다.

### 9-3. hard fail / warn / skip matrix

- `hard fail`
  - row count mismatch
  - item set mismatch
  - non-null hint type mismatch
  - non-null hint의 source lineage 부재
  - overlay hint와 decisions authority의 직접 충돌
- `warn`
  - canonical representative lineage는 있으나 registry/derivation 결과가 비어 있음
  - derivable hint가 build quality 문제로 누락된 경우
- `skip`
  - canonical layer2 anchor export 부재
  - canonical representative lineage 자체가 부재

### 9-4. Phase C structural signal handling

- Phase C 실행 중 관측되는 structural signal(`LAYER4_ABSORPTION` 의심 포함)은 observer-only다.
- validator는 이 signal을 writer input으로 승격하지 않는다.
- structural signal은 Phase C exit blocker가 아니다.
- semantic adjudication은 Phase D owner가 맡는다.
- 이 원칙은 `2026-04-05` body-role structural lint의 next-build feedback 원칙과 정합해야 한다.

---

## 10. forbidden path reference

current forbidden path authority는 아래 artifact를 canonical reference로 사용한다.

- `docs/Iris/forbidden_patterns.json`
- `docs/Iris/seam_legality_checklist.md`

이 문서의 ownership/validator 규칙과 위 두 artifact는 같은 Phase B closeout package로 읽는다.

---

## 11. current implementation note

current implementation은 Phase B starter다.

- 2계층 anchor export가 아직 current build tree에 없으므로 `layer2_anchor_hint`는 기본적으로 `null`
- 4계층 representative context는 cluster label phrase로만 restatement
- current runtime compose path는 이 overlay를 아직 소비하지 않는다

즉, Phase B는 current runtime을 재개방하는 단계가 아니라, **new compose_v2 input seam을 미리 materialize하는 단계**다.

---

## 12. gate 기준

Phase B gate는 아래 조건이 닫혀야 통과로 본다.

- overlay builder가 raw layer source를 compose에 직접 넘기지 않음
- `body_source_overlay` schema가 문서와 validator에서 일치함
- existing decisions overlay와의 precedence / drift rule이 명시됨
- validator scope가 이 문서 appendix에 귀속됨
- forbidden path가 별도 artifact로 고정됨
- facts와 overlay item set drift가 없음
- 2계층 anchor 부재는 묵시 추론이 아니라 explicit `null` 정책으로 기록됨

---

## 13. 비목표

이 문서는 아래를 하지 않는다.

- quality_state 규칙 정의
- section ordering 정의
- profile migration 정의
- rendered string 포맷 정의
- structural signal semantic redesign 정의
