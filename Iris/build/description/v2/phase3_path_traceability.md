# Phase 3 Path And Traceability Contract

> 목적은 `build/` 아래에 놓인 Phase 3 자산을 git에서 다시 보이게 만들고, tracked source와 generated artifact를 섞지 않는 것이다.

## 1. 원칙

- `staging/reviews/*.acquisition.jsonl`는 immutable Phase 2 입력으로 추적한다.
- Phase 3 판단은 `staging/phase3/` 아래 overlay와 pilot report로만 기록한다.
- 사람이 유지하는 규약/스키마/도구/테스트는 tracked source로 둔다.
- 재생성 가능한 집계, 비교 출력, scratch는 generated temporary로 남기고 기본 추적 대상에서 제외한다.

## 2. Tracked Source

- 계약 문서: `phase3_*.md`, `acquisition_policy.md`
- 스키마: `schemas/phase3_*.json`
- 도구: `tools/build/generate_acquisition_master.py`, `tools/build/export_phase3_pilot_input.py`, `tools/build/phase3_candidate_state_lib.py`, `tools/build/validate_acquisition_coverage.py`, `tools/build/report_acquisition_coverage.py`, `tools/build/validate_phase3_candidate_state.py`, `tools/build/report_phase3_candidate_state.py`
- 테스트: `tests/test_phase3_*.py`

`generate_acquisition_master.py`는 Phase 3 validator/lib가 직접 import하므로 Phase 3 재현성의 일부로 같이 추적한다.

## 3. Review Artifact

- Phase 2 immutable input: `staging/reviews/*.acquisition.jsonl`
- Phase 3 pilot input: `staging/phase3/pilot*_input_manifest.json`, `staging/phase3/pilot*_phase2_snapshot.jsonl`, `staging/phase3/pilot*_phase2_snapshot_hash.txt`
- Phase 3 pilot overlay: `staging/phase3/pilot*_candidate_state.review.jsonl`
- Phase 3 pilot report: `staging/phase3/phase3_candidate_state_{summary,by_bucket,gaps}_pilot*.json`
- Canonical full overlay를 만들 때만 `staging/phase3/candidate_state_phase3.review.jsonl`와 기본 report 파일명을 사용한다.

## 4. Generated Temporary

- `staging/acquisition_master.jsonl`
- `staging/acquisition_master_manifest.json`
- `staging/acquisition_coverage_summary.json`
- `staging/acquisition_coverage_by_bucket.json`
- `staging/acquisition_coverage_gaps.json`
- `staging/phase3/tmp/`
- `staging/phase3/scratch/`
- second-run comparison overlay와 ad-hoc diff output
- `__pycache__/`, `*.pyc`

## 5. Git Rule

- 루트 `.gitignore`는 `build/`를 기본 차단하되, `Iris/build/description/v2` 아래의 tracked source와 review artifact만 예외로 연다.
- generated temporary는 같은 경로 아래에 있더라도 계속 ignore 상태를 유지한다.
- gate는 `git status --short`에서 핵심 Phase 3 문서, 도구, 테스트, pilot artifact가 보이는지로 확인한다.

## 6. Naming

- Pilot 이름은 `pilotA`, `pilotB`처럼 고정된 접두어를 쓴다.
- snapshot hash는 pilot 단위 snapshot row를 `fulltype` 기준 정렬한 뒤 SHA-256으로 계산한다.
- pilot report는 suffix를 붙여 canonical full-overlay report와 충돌하지 않게 저장한다.
