# Phase 3 Pilot Scope Memo

## 고정 범위

- Pilot 입력은 `staging/reviews/*.acquisition.jsonl`의 닫힌 Phase 2 row만 사용한다.
- Pilot 판정 결과는 overlay와 pilot report로만 남기고 Phase 2 review row는 덮어쓰지 않는다.
- Pilot A는 `Consumable.3-C`, Pilot B는 `Tool.1-L` 전수 판정으로 고정한다.
- Pilot 단계의 `PROMOTE_ACTIVE`는 sync-ready 후보일 뿐 canon 반영 승인 상태가 아니다.

## 제외 범위

- 이번 배치에서 Phase 2 review 파일 내용 수정은 하지 않는다.
- 3-4 상호작용층 문장 설계나 canon sync queue 작성은 pilot 완료 전까지 포함하지 않는다.
- second-run comparison output과 scratch 산출물은 임시 생성물로 취급한다.

## 운영 메모

- Pilot overlay는 Phase 3 validator와 report builder가 직접 읽을 수 있는 JSONL 형태로 고정한다.
- Pilot summary/by_bucket/gaps는 pilot 이름이 붙은 별도 파일로 저장해 canonical full-overlay와 섞지 않는다.
- 후보 판정은 reviewer 감이 아니라 policy, reason/profile contract, validator gate로 닫는다.
