# Pipeline Execution Order Check

> 상태: draft v0.1  
> 기준일: 2026-04-08  
> 목적: `surface contract authority migration` round에서 실제 코드 기준 실행 순서를 문서로 고정한다.

---

## 확인 결과

현행 코드 기준으로 `body-role overlay`는 별도 seam으로 존재한다.

- 근거:
  - [`compose_layer3_text.py`](C:/Users/MW/Downloads/coding/PZ/Iris/build/description/v2/tools/build/compose_layer3_text.py)는 `layer3_role_check_overlay.jsonl`을 별도 입력으로 읽는다.
  - overlay 필드(`layer3_role_check`, `representative_slot`, `representative_slot_override`)는 compose 내부에서 소비된다.

따라서 current execution order는 아래처럼 읽는다.

```text
facts
  -> decisions
  -> body-role overlay seam
  -> compose(internal repair + diagnostic quality_flag capture)
  -> normalizer
  -> advisory sensor branch
  -> structural audit
  -> quality/publish decision stage
  -> Lua bridge
  -> runtime consumer
```

## `rendered.json` 파일명에 대한 주석

current build는 compose 결과 candidate artifact의 파일명을 역사적으로 `*.rendered.json`으로 유지하고 있다.  
하지만 `surface contract authority migration` round에서 structural audit가 읽는 것은 **final publish decision 이후 산출물**이 아니라, **decision stage 이전의 pre-render contract candidate** 다.

즉:

- 파일명: `rendered.json`
- 구조적 위치: `quality/publish decision stage` 이전 candidate input

이 문서는 둘을 혼동하지 않기 위해 `pre-render contract candidate`라는 용어를 쓴다.

## 결론

- `body-role overlay`는 decisions 내부 암묵 로직이 아니라 별도 seam으로 취급한다.
- structural audit는 publish writer가 아니다.
- final authority는 계속 `quality/publish decision stage` 하나뿐이다.
