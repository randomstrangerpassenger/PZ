# Iris Regular Validation Boundary Consolidation Walkthrough

이 문서는 구현 결과를 빠르게 따라가기 위한 비권위 narrative다. Canonical runner·validator·closure를 대체하지 않는다.

## 결과

Exact S0는 `64754c38147233c4f5e04a7469b45163c2c55ebe` / tree `92810ce35f021bd3dfa65ceafb782a32c2b86258`, machine-validation terminal은 `b7c4fa54acd43b0d64b51089ed34357c18a6c469` / tree `d6a6a8feef9724482ca3e2004161a66bd6633f92`다.

| Universe | S0 | Final | 감소 |
| --- | ---: | ---: | ---: |
| Pytest identity | 234 | 192 | 42 (17.9%) |
| Standalone | 4 | 4 | 0 |
| Total execution | 238 | 196 | 42 (17.6%) |
| Taxonomy | 123 | 102 | 21 (17.1%) |
| Required manifest | 70 | 61 | 9 (12.9%) |

## 무엇을 바꿨나

초기 wave의 public-text, particle, Layer 4 consolidation에 이어 독립 review가 찾은 11개 잔존 후보를 모두 처리했다. VCS path, compose legacy label, current-authority acceptance, Korean naturalization, legacy synthetic guard, package lookup/output-root, protected snapshot, Round 3 missing-artifact와 Lua bridge rejection을 named table 또는 same-input family로 묶었다. 중복 package/VCS authority는 더 강한 기존 check로 이관했다.

Predecessor assertion은 삭제하지 않고 named check로 옮겼다. Writable negative case는 row마다 fresh clone/reset을 사용하고 Round 3의 shared `runner.REPO`는 `finally`에서 복원한다. Round 3는 최종적으로 pytest identity `5 -> 4`, runner import `5 -> 1`이다. Product/runtime/public-output 파일은 바꾸지 않았다.

## 검증과 review

- Focused: `83 passed`, `73 subtests passed`.
- Round 3: 역순으로 같은 module object에서 2회, 총 `8 tests` PASS.
- Clean-checkout Run A/B: 각각 pytest `192` + standalone `4`, canonical SHA-256 `651167c7bd01cd12287351c4533b58e90fe978ba265c23ac7bcb44ee7161faee`.
- Deterministic comparator: `succeeded`, exit `0`.
- Codex Reviewer: P0–P3, actionable, unsupported keep, unimplemented non-keep, remaining eligible candidate 모두 `0`.

## Evidence readpoints

- Compact map: `Iris/_docs/refactor/regular_validation_boundary_consolidation/implementation_map.json`
- Item closure: `C:\Users\MW\iccv\regular-consolidation-closeout-correction\closure\item-level-closure-v5.json`, SHA-256 `26135c9a629f066961ba84efa4835331dc35c965a6cd1eea43911d5526e68528`
- Final implementation review: `C:\Users\MW\iccv\regular-consolidation-closeout-correction\review\implementation-final\implementation_review_receipt.json`, SHA-256 `1232069d1af948b4fbb316869a9cfba91bb300f1c7c5d1d7625c4f1422c13029`
- Comparator: `C:\Users\MW\iccv\regular-consolidation-closeout-correction\validation\compare2\compare_receipt.json`, SHA-256 `1c1c973f5c1c6de3e77a28a34211a702b698555420aca2e411aedf10eccd36c6`

Validation/tooling closure는 S0 대비 `15,151` bytes 줄었다. 최종 documentation 증가와 context proxy는 compact map의 carrier 측정을 따른다. 이는 repository-side byte proxy이며 wall-clock 또는 실제 tokenizer/Codex token 절감률이 아니다. 세션의 임시 inspection 명령도 새 validation authority가 아니다.
