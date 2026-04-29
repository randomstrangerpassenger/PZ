# Layer3 Structural Audit Spec

> 상태: draft v0.1  
> 기준일: 2026-04-08  
> 구현 기준: [`layer3_structural_audit.py`](C:/Users/MW/Downloads/coding/PZ/Iris/build/description/v2/tools/build/layer3_structural_audit.py)

---

## 목적

`layer3_structural_audit.py`는 style advisory와 별도인 **surface contract signal generator** 다.

- writer가 아니다.
- `quality_state`를 직접 기록하지 않는다.
- `publish_state`를 직접 기록하지 않는다.

## 입력

- `decisions.jsonl`
- `layer3_active_quality_audit.jsonl`
- facts의 `primary_use`
- compose candidate entry의 `quality_flag`

## 출력

`surface_contract_signal.jsonl` row 필드:

- `item_id`
- `structural_verdict`
  - `clean | flag | hard_fail`
- `violation_type`
  - current implementation:
    - `LAYER4_ABSORPTION`
    - `BODY_LACKS_ITEM_SPECIFIC_USE`
    - `IDENTITY_ONLY`
    - `FUNCTION_NARROW`
    - `ACQ_DOMINANT`
    - `none`
- `recommended_tier`
  - `advisory_only`
  - `publish_isolation_candidate`
  - `hard_block_candidate`
- `evidence`

## 현재 구현 규칙

- explicit `LAYER4_ABSORPTION`
  - `hard_fail + hard_block_candidate`
- explicit `BODY_LACKS_ITEM_SPECIFIC_USE`
  - `flag + publish_isolation_candidate`
- `IDENTITY_ONLY` role 또는 `quality_flag == identity_only`
  - `primary_use`가 있으면 `BODY_LACKS_ITEM_SPECIFIC_USE`
  - 없으면 `IDENTITY_ONLY`
- `semantic_quality_decision == function_narrow_default_weak`
  - `FUNCTION_NARROW`
- residual `ACQ_DOMINANT`
  - `ACQ_DOMINANT`

## consumer 규칙

- downstream `quality/publish decision stage`만 이 신호를 읽는다.
- `recommended_tier`는 recommendation이다.
- final 처분은 decision stage가 닫는다.
- `structural_flag`는 decision preview/report meta일 뿐, runtime axis가 아니다.
