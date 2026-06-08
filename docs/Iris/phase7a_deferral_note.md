# Phase 7a (Change 7a) — Deferral Note (excluded from execution)

> 2026-06-07 사용자 결정: **Phase 7a(selective sibling script consolidation)는 실행에서 제외**한다 (Phase 2와 동일 사유 + 더 위험).

## 사유

통합 후보 **43개 전부 gitignore된 frozen reproduction 스크립트**다 (실측: tracked 0/43):

| family | 개수 |
|---|---:|
| `build_source_coverage_*` | 16 |
| `build_post_cleanup_phase3_pkg3*` | 11 |
| `build_identity_fallback_batch*_authority_promotion` | 8 |
| `freeze_quality_baseline_v*` | 4 |
| `report_*_{draft,final}` | 4 |

이들은 staging 입력이 제거되어 **실행 불가**. 따라서 계획의 Phase 7a validation
("candidate별 Artifact SHA before/after 일치" + "batch별 test")을 수행할 수 없다.

**Phase 2보다 나쁨**: 7a는 import 한 줄 repoint가 아니라 **N개 스크립트를 1개 파라미터화 스크립트 +
config로 병합**하는 구조적 재작성이다. "설정 차이뿐"임을 diff로 확인해도, 병합이 출력을 바꾸지 않았음을
**실행으로 입증할 안전망이 없다**. 같은 검증불가 + 훨씬 큰 blast radius. 가치도 낮음(dead reproduction;
병합 시 per-round provenance 손실).

## Disposition

- Change 7a = **무기한 deferred**. staging 입력 복원 시에만 재검토.
- Active sequence는 7a를 건너뛰고 **Phase 7b(archive sweep — git mv 기반, 검증 가능)**로 진행.
