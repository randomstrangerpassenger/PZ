# Phase 3 Candidate State Walkthrough

이 문서는 현재 시점 기준으로 Phase 3 candidate-state 작업 전체를 한 번에 읽을 수 있도록 정리한 final walkthrough다.

목표는 처음부터 같았다.

- Phase 2 acquisition review를 immutable input으로 고정한다.
- Phase 3 판단은 별도 overlay로 분리한다.
- reviewer 감이 아니라 policy, schema, validator, report, sync queue가 결정을 지배하게 만든다.

---

## 1. 현재 상태 한 줄 요약

지금 상태는 “pilot-proven 규약을 closed review universe 전체에 확장해 candidate_state rollout evaluation까지 닫았고, approval backlog만 남은 상태”다.

즉 `evaluation complete`는 `YES`, `sync-ready complete`는 `NO`다.

---

## 2. 현재 기준 핵심 산출물

### 운영 / 상태 문서

- `phase3_kickoff_checklist.md`
- `phase3_pilot_scope_memo.md`
- `phase3_path_traceability.md`
- `phase3_rollout_wave_plan.md`
- `phase3_rollout_seed_policy.md`
- `phase3_cumulative_report_policy.md`
- `phase3_wave1_acceptance.md`
- `phase3_wave2_acceptance.md`
- `phase3_wave3_acceptance.md`
- `phase3_wave4_acceptance.md`
- `phase3_policy_patch_candidate.md`
- `phase3_hold_review_backlog.md`
- `phase3_evaluation_complete.md`

### 계약 문서

- `phase3_scope_contract.md`
- `phase3_candidate_state_policy.md`
- `phase3_reason_profile_contract.md`
- `phase3_gate_spec.md`
- `phase3_pilot_bucket_selection.md`
- `phase3_reviewer_decision_sheet.md`
- `phase3_sync_approval_policy.md`
- `phase3_manual_cluster_analysis.md`
- `phase3_rollout_readiness.md`

### 스키마

- `schemas/phase3_schema.json`
- `schemas/phase3_summary_schema.json`
- `schemas/phase3_by_bucket_schema.json`
- `schemas/phase3_gaps_schema.json`
- `schemas/phase3_sync_queue_schema.json`

### 빌드 / 검증 코드

- `tools/build/phase3_candidate_state_lib.py`
- `tools/build/validate_phase3_candidate_state.py`
- `tools/build/report_phase3_candidate_state.py`
- `tools/build/export_phase3_pilot_input.py`
- `tools/build/build_phase3_rollout_seed.py`
- `tools/build/build_phase3_sync_queue.py`
- `tools/build/build_phase3_hold_queue.py`

### 테스트

- `tests/test_acquisition_coverage.py`
- `tests/test_phase3_candidate_state.py`
- `tests/test_phase3_hold_queue.py`
- `tests/test_phase3_pilot_input.py`
- `tests/test_phase3_rollout_seed.py`
- `tests/test_phase3_sync_queue.py`

### canonical / cumulative 산출물

- `staging/phase3/candidate_state_phase3.review.jsonl`
- `staging/phase3/phase3_candidate_state_summary.json`
- `staging/phase3/phase3_candidate_state_by_bucket.json`
- `staging/phase3/phase3_candidate_state_gaps.json`
- `staging/phase3/phase3_sync_queue.jsonl`
- `staging/phase3/phase3_hold_queue_cumulative.jsonl`
- `staging/phase3/phase3_hold_reason_summary.json`
- `staging/phase3/phase3_rollout_universe_manifest.json`

---

## 3. 변하지 않은 핵심 설계 결정

### 3-1. Phase 2는 입력, Phase 3는 overlay

기존 `staging/reviews/*.acquisition.jsonl`는 계속 Phase 2 진실 소스다.

Phase 3는 여기서 아래 필드만 snapshot으로 읽는다.

- `coverage_disposition`
- `acquisition_hint`
- `acquisition_null_reason`

판단 결과는 Phase 2 파일에 다시 쓰지 않는다.
pilot 단계 산출물은 아래 파일들에 남아 있고, current canonical은 별도 full overlay로 닫혀 있다.

- `staging/phase3/pilotA_candidate_state.review.jsonl`
- `staging/phase3/pilotB_candidate_state.review.jsonl`
- `staging/phase3/pilotA_second_run.review.jsonl`
- `staging/phase3/pilotB_second_run.review.jsonl`

현재 canonical full overlay 파일은 `staging/phase3/candidate_state_phase3.review.jsonl`다.

### 3-2. candidate_state는 staging 판단

`KEEP_SILENT`, `PROMOTE_ACTIVE`, `MANUAL_OVERRIDE_CANDIDATE`는 compose 확정이나 canon sync 확정이 아니다.

- `KEEP_SILENT`: 3-3을 깨울 자격이 없음
- `PROMOTE_ACTIVE`: 3-3 본문 가치가 있어 활성화 가능
- `MANUAL_OVERRIDE_CANDIDATE`: 구조 충돌 또는 rule gap으로 자동 판정 보류

### 3-3. approval_state는 별도 상태

sync approval queue를 추가하면서 `candidate_state`와 `approval_state`를 분리했다.

- candidate-state: staging 평가
- approval-state: canon sync 승인 판단

이 분리는 `phase3_sync_approval_policy.md`와 `phase3_sync_queue_schema.json`으로 닫았다.

---

## 4. validator가 실제로 강제하는 것

`validate_phase3_candidate_state.py`는 아래를 FAIL로 본다.

- invalid state / reason / profile enum
- state-reason-profile 조합 오류
- `PROMOTE_ACTIVE`인데 compose_profile 누락
- `KEEP_SILENT` 또는 `PROMOTE_ACTIVE`인데 notes 사용
- `MANUAL_OVERRIDE_CANDIDATE`인데 notes 누락
- phase2 snapshot mismatch
- `SYSTEM_EXCLUDED` 또는 `UNREVIEWED` row 혼입
- Phase 2 review row candidate 필드 오염
- summary / by_bucket / gaps 재계산 불일치
- compare overlay 기준 determinism mismatch

WARN은 과도한 manual 비율, reason 편중, 특정 버킷 manual 집중을 올리도록 했다.

---

## 5. 추적성 상태

초기에는 이 경로가 `build/` 아래라 `.gitignore` 때문에 git status에 보이지 않았다.

현재는 루트 `.gitignore`를 조정해서 아래 자산이 git 추적 대상으로 보이게 만들었다.

- Phase 3 문서
- Phase 3 스키마
- Phase 3 도구 / 테스트
- Phase 2 review input
- Phase 3 pilot artifact

generated temporary와 scratch는 계속 분리했다.

이 규약은 `phase3_path_traceability.md`에 정리해 두었다.

---

## 6. Pilot A 실행 결과

### 대상

- bucket: `Consumable.3-C`
- row count: `27`
- disposition: `ACQ_HINT=27`
- snapshot sha256: `687a8a7bb2b19e89cf5944b80f180652a115cd8c6142b0b6ae3e9416982f2560`

### 입력 산출물

- `staging/phase3/pilotA_input_manifest.json`
- `staging/phase3/pilotA_phase2_snapshot.jsonl`
- `staging/phase3/pilotA_phase2_snapshot_hash.txt`

### overlay 결과

- `PROMOTE_ACTIVE=23`
- `KEEP_SILENT=4`
- `MANUAL_OVERRIDE_CANDIDATE=0`

reason/profile breakdown:

- `LOCATION_SPECIFIC=16`
- `METHOD_SPECIFIC=7`
- `INTERACTION_LAYER_ONLY=4`
- `ACQ_ONLY_LOCATION=16`
- `ACQ_ONLY_METHOD=7`

dirty / after-use row 4건만 `INTERACTION_LAYER_ONLY`로 keep 처리했고, 나머지는 location 또는 method specific promote로 닫았다.

### report 산출물

- `staging/phase3/phase3_candidate_state_summary_pilotA.json`
- `staging/phase3/phase3_candidate_state_by_bucket_pilotA.json`
- `staging/phase3/phase3_candidate_state_gaps_pilotA.json`

determinism sha:

- `3a1ad712455fecc9e27fcd9862283012dc621c94e425c7bad1e6d4c5f7925cab`

---

## 7. Pilot B 실행 결과

### 대상

- bucket: `Tool.1-L`
- row count: `45`
- disposition: `ACQ_HINT=40`, `ACQ_NULL=5`
- snapshot sha256: `162d1dd53306bdeec140a6e2b48b78afaa3775dd03b132fbb3c4d4f5d4c3394b`

### 입력 산출물

- `staging/phase3/pilotB_input_manifest.json`
- `staging/phase3/pilotB_phase2_snapshot.jsonl`
- `staging/phase3/pilotB_phase2_snapshot_hash.txt`

### overlay 결과

- `PROMOTE_ACTIVE=29`
- `KEEP_SILENT=13`
- `MANUAL_OVERRIDE_CANDIDATE=3`

reason/profile breakdown:

- `ACQ_NULL=5`
- `DUPLICATES_SUBCATEGORY=5`
- `GENERIC_BUCKET_LEVEL=3`
- `LOCATION_SPECIFIC=22`
- `USE_CONTEXT_LINKED=5`
- `IDENTITY_LINKED=2`
- `LAYER_COLLISION=3`
- `ACQ_ONLY_LOCATION=22`
- `USE_PLUS_ACQ=5`
- `IDENTITY_PLUS_ACQ=2`

manual 3건은 모두 `채집으로 구할 수 있다` 계열 row였고, 3-4 상호작용층과 겹치는 `LAYER_COLLISION`으로 닫았다.

### report 산출물

- `staging/phase3/phase3_candidate_state_summary_pilotB.json`
- `staging/phase3/phase3_candidate_state_by_bucket_pilotB.json`
- `staging/phase3/phase3_candidate_state_gaps_pilotB.json`

determinism sha:

- `abcb95ef43404ccf9050cced9d31ae10763fde138ec52bdade63318a56090d08`

---

## 8. Pilot 비교 결과

pilot 비교는 `staging/phase3/phase3_pilot_compare_report.json`에 정리했다.

핵심 해석은 아래다.

- Pilot A는 promote-heavy ACQ_HINT bucket으로 동작했다.
- Pilot B는 mixed bucket이라 keep / promote / manual 경계가 실제로 드러났다.
- 두 pilot 모두 `LOCATION_SPECIFIC + ACQ_ONLY_LOCATION`이 dominant promote 경로로 유지됐다.
- Pilot B에서만 `ACQ_NULL`, `DUPLICATES_SUBCATEGORY`, `GENERIC_BUCKET_LEVEL`, `USE_CONTEXT_LINKED`, `IDENTITY_LINKED`, `LAYER_COLLISION`이 추가로 나타났다.

즉 reason/profile 체계가 bucket이 바뀌어도 reviewer 감으로 흔들리지 않고 구조적으로 버텼다.

---

## 9. 실데이터 2-run determinism 결과

second-run overlay를 실제로 다시 만들고 compare-overlay를 돌렸다.

생성 파일:

- `staging/phase3/pilotA_second_run.review.jsonl`
- `staging/phase3/pilotB_second_run.review.jsonl`
- `staging/phase3/phase3_determinism_report.json`

결과:

- Pilot A compare-overlay PASS
- Pilot B compare-overlay PASS
- mismatch count `0`
- summary SHA / breakdown 동일

즉 “같은 입력, 같은 reviewer rule, 같은 기록 방식이면 같은 산출이 나온다”는 최소 조건은 실데이터에서 확인했다.

---

## 10. manual cluster 분석 결과

manual 분석은 `phase3_manual_cluster_analysis.md`에 정리했다.

현재 결과는 아래다.

- Pilot A manual rate: `0 / 27 = 0.0000`
- Pilot B manual rate: `3 / 45 = 0.0667`
- combined manual rate: `3 / 72 = 0.0417`

manual reason top N:

- `LAYER_COLLISION=3`

판정:

- manual 원인은 reviewer 불안이 아니라 구조적 layer collision이다.
- notes 패턴은 안정적이다.
- 현 시점에서는 policy patch / reason-profile patch를 새로 열 필요가 없다.

---

## 11. sync approval queue 초기 구조

sync queue는 `build_phase3_sync_queue.py`로 생성했고, 계약은 `phase3_sync_approval_policy.md`와 `schemas/phase3_sync_queue_schema.json`으로 닫았다.

pilot 기준 최초 queue 산출물:

- `staging/phase3/phase3_sync_queue_pilot.jsonl`

queue 집계:

- total rows: `55`
- `APPROVE_SYNC=45`
- `HOLD=10`
- `REJECT=0`

approval reason breakdown:

- `DIRECT_ACQUISITION_READY=45`
- `CONTEXTUAL_PROMOTE_REVIEW=7`
- `MANUAL_REVIEW_REQUIRED=3`

이 단계로 `candidate_state`와 `approval_state`를 분리 저장하는 기본 구조가 완성됐다.

현재 full rollout 기준 누적 queue 상태는 아래 section 19에서 다시 정리한다.

---

## 12. 테스트 / 검증 상태

현재 기본 테스트 묶음은 아래 파일들로 구성된다.

- `test_acquisition_coverage.py`
- `test_phase3_candidate_state.py`
- `test_phase3_hold_queue.py`
- `test_phase3_pilot_input.py`
- `test_phase3_rollout_seed.py`
- `test_phase3_sync_queue.py`

실행 결과:

- `python -B -m unittest discover -s Iris\build\description\v2\tests -p "test_*.py"`
- `Ran 17 tests`
- `OK`

validator는 pilot overlay, wave rollout overlay, cumulative regenerate, sync queue, HOLD queue 범위에서 모두 PASS했다.

---

## 13. 로드맵 기준 완료 상태

로드맵 기준으로 현재 상태는 아래다.

1. rollout universe manifest 고정: 완료
2. wave plan 작성: 완료
3. bucket 입력 snapshot 고정: 완료
4. bucket별 overlay 작성: 완료
5. validator 실행: 완료
6. cumulative report 생성: 완료
7. cumulative sync queue 갱신: 완료
8. wave acceptance / drift check: 완료
9. HOLD queue 누적 추적: 완료
10. wave 1~4 rollout 반복: 완료
11. canonical full overlay 생성: 완료
12. evaluation complete / sync-ready complete 판정: 부분 완료

12번의 세부 판정은 아래처럼 닫혔다.

- evaluation complete: `YES`
- sync-ready complete: `NO`

---

## 14. 현재 남은 것

남은 일은 rollout이 아니라 approval backlog 정리다.

현재 후속 운영 대상은 아래다.

1. `HOLD=197` row를 approval queue에서 처리한다.
2. `MANUAL_REVIEW_REQUIRED=158` backlog를 cluster 단위로 정리한다.
3. `CONTEXTUAL_PROMOTE_REVIEW=39` row를 approval notes와 함께 검토한다.
4. backlog가 해소되면 `sync-ready complete: YES` 판정을 다시 낸다.

한 줄로 요약하면, 지금은 “candidate_state rollout은 끝났고, approval_state backlog만 남은 상태”다.

---

## 15. full rollout 결과

이 walkthrough는 pilot / readiness 문서에서 시작했지만, 현재는 full rollout closeout까지 포함하는 최종 문서다.

그 뒤 실제 rollout은 같은 계약을 유지한 채 wave 단위로 확장됐다.

고정 원칙은 끝까지 바뀌지 않았다.

- Phase 2 input은 immutable
- Phase 3 candidate_state는 canonical overlay 하나로 누적
- approval_state는 sync queue / HOLD queue로 분리
- validator / cumulative report / queue rebuild를 bucket 단위로 반복

즉 readiness 이후는 “새 규칙 탐색”이 아니라 pilot-proven 규약을 closed review universe 전체에 적용하는 단계였다.

---

## 16. wave rollout 결과

wave별 처리 결과는 아래다.

- wave1: `5 buckets / 56 rows`
- wave2: `5 buckets / 197 rows`
- wave3: `4 buckets / 319 rows`
- wave4: `32 buckets / 1507 rows`

최종적으로 reviewable closed universe 전체가 canonical에 반영됐다.

- canonical bucket coverage: `46 / 46`
- canonical overlay rows: `2079`
- pending canonical rollout bucket count: `0`

canonical 단일 기준 파일은 아래다.

- `staging/phase3/candidate_state_phase3.review.jsonl`

---

## 17. cumulative candidate-state 결과

full rollout 종료 시점의 canonical 집계는 아래다.

- `PROMOTE_ACTIVE=1089`
- `KEEP_SILENT=832`
- `MANUAL_OVERRIDE_CANDIDATE=158`
- manual rate: `0.076`
- determinism sha: `11764818309519feeb9da4c0dfe16205e390e815c99af36713ad0675664c653e`

reason code breakdown은 아래처럼 닫혔다.

- `LOCATION_SPECIFIC=762`
- `METHOD_SPECIFIC=288`
- `INTERACTION_LAYER_ONLY=304`
- `GENERIC_BUCKET_LEVEL=467`
- `LAYER_COLLISION=158`
- `IDENTITY_LINKED=33`
- `USE_CONTEXT_LINKED=6`
- `ACQ_NULL=42`
- `DUPLICATES_SUBCATEGORY=19`

즉 bulk rollout에서도 pilot 때 확인한 구조가 유지됐고, manual은 새로운 random cluster가 아니라 주로 known `LAYER_COLLISION`으로 수렴했다.

---

## 18. wave 3 stop rule과 처리 방식

wave3에서는 mechanical acceptance 자체는 PASS였지만 stop rule이 한 번 발동했다.

원인은 `Wearable.6-G`의 pure-foraging accessory subset `33`행이 기존 known `LAYER_COLLISION` cluster로 한꺼번에 유입됐기 때문이다.

여기서 선택한 운영 해법은 `NO_RULE_CHANGE_BATCH_REVIEW`였다.

뜻은 아래와 같다.

- candidate_state rule은 바꾸지 않는다.
- pure-foraging collision row는 계속 `MANUAL_OVERRIDE_CANDIDATE`로 둔다.
- approval_state에서 known batch backlog로 따로 관리한다.
- stop rule은 “규칙 패치”가 아니라 “운영 분리 필요” 신호로 해석한다.

그래서 `KEEP_SILENT` 의미를 오염시키는 예외 규칙은 열지 않았고, collision 의미는 보존한 채 rollout을 계속 마쳤다.

---

## 19. sync queue / HOLD queue 최종 상태

candidate_state rollout이 끝난 뒤 approval queue 상태는 아래다.

- sync queue rows: `1247`
- `APPROVE_SYNC=1050`
- `HOLD=197`

approval reason breakdown:

- `MANUAL_REVIEW_REQUIRED=158`
- `CONTEXTUAL_PROMOTE_REVIEW=39`

HOLD queue는 두 층으로 관리한다.

- known batch review hold: `33`
- general hold: `164`

이 단계에서 중요한 건 candidate_state와 approval_state를 섞지 않았다는 점이다.

- candidate_state는 canonical 결과로 고정
- approval_state만 backlog로 남김

---

## 20. 최종 gate 판정

로드맵의 12번 closeout 기준으로 최종 판정은 아래다.

- evaluation complete: `YES`
- sync-ready complete: `NO`

evaluation complete가 `YES`인 이유:

- reviewable closed universe coverage `2079 / 2079`
- canonical bucket coverage `46 / 46`
- invalid combo `0`
- snapshot mismatch `0`
- cumulative summary / by_bucket / gaps regenerate PASS
- cumulative sync queue build PASS
- cumulative HOLD queue build PASS

sync-ready complete가 `NO`인 이유:

- approval backlog `197` rows가 아직 남아 있기 때문이다.

즉 Phase 3 candidate-state rollout은 종료됐지만, approval backlog 운영은 후속 작업으로 남아 있다.

---

## 21. 최종 검증 상태

최종 closeout 시점의 검증 상태는 아래다.

- canonical JSON audit PASS
- cumulative regenerate PASS
- sync queue / HOLD queue consistency PASS
- wrapped unittest runner 기준 `17 tests` PASS

이 상태에서 canonical overlay는 “전 universe에 대한 closed baseline”으로 간주한다.

이후 재검수나 policy patch가 필요하면, Phase 2 input을 바꾸는 게 아니라 canonical overlay / report / sync / HOLD artifact를 다시 생성하는 방식으로 다룬다.
