# Phase 3 Reason / Profile Contract

> reason_code는 왜 그렇게 닫았는지를, compose_profile은 promote를 어떤 틀로 쓸지를 고정한다.

---

## 1. candidate_reason_code enum

### KEEP 계열

- `ACQ_NULL`
- `GENERIC_BUCKET_LEVEL`
- `DUPLICATES_SUBCATEGORY`
- `INTERACTION_LAYER_ONLY`
- `LOW_ITEM_SPECIFICITY`
- `PROSE_VALUE_INSUFFICIENT`

### PROMOTE 계열

- `LOCATION_SPECIFIC`
- `METHOD_SPECIFIC`
- `LOCATION_METHOD_SPECIFIC`
- `CONTEXT_SPECIFIC`
- `IDENTITY_LINKED`
- `USE_CONTEXT_LINKED`

### MANUAL 계열

- `LAYER_COLLISION`
- `SPECIFICITY_BORDERLINE`
- `COMPOSE_STYLE_RISK`
- `MULTI_CLAUSE_COLLAPSE`
- `RULE_GAP`

## 2. candidate_compose_profile enum

compose_profile은 `PROMOTE_ACTIVE`에만 채운다.

- `ACQ_ONLY_LOCATION`
- `ACQ_ONLY_METHOD`
- `ACQ_LOCATION_METHOD`
- `ACQ_CONTEXT_NOTE`
- `USE_PLUS_ACQ`
- `IDENTITY_PLUS_ACQ`

`KEEP_SILENT`와 `MANUAL_OVERRIDE_CANDIDATE`는 compose를 미리 닫지 않는다.

## 3. notes 사용 규칙

허용:

- `MANUAL_OVERRIDE_CANDIDATE`
- `COMPOSE_STYLE_RISK`
- `RULE_GAP`
- `LAYER_COLLISION`

금지:

- routine keep/promote 설명
- 감상문
- 재해석
- 추천성 언어

validator는 keep/promote의 notes 사용을 FAIL로 처리한다.
