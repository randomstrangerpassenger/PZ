# DVF 3-3 Body Role Closeout

이 문서는 `Philosophy.md`, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`의 하위 운영 문서다. 상위 문서와 충돌 시 상위 문서가 우선한다.

## closeout 문구

- 3-3은 authoritative wiki body다.
- 3-3은 1·2·4 정보를 일부 포함할 수 있다.
- 단, 3-4 상세를 통째로 흡수하면 안 된다.
- compose는 repair를 수행한다.
- linter/gate는 veto와 피드백을 수행한다.
- Phase 4 feedback은 매 빌드 fresh recompute가 원칙이며 누적 상태로 재사용하지 않는다.
- `quality_flag`는 rendered 진단 메타데이터일 뿐 상태 축이 아니다.
- 신규 상태 축을 만들지 않고 기존 semantic axis 위에서 품질 추적을 수행한다.

## 현재 closeout 해석

current round에서 body-role 경로는 다음처럼 읽는다.

- Phase 2/3은 실제 수정 경로다.
- Phase 4/6은 현재 빌드를 소급 수정하지 않는 진단·피드백 경로다.
- semantic weak 후보 목록은 자동 재분류가 아니라 후속 `DECISIONS.md` 입력이다.
- full rendered authority는 `sprint7_overlay_preview.rendered.json`이다.
- fixture `output/dvf_3_3_rendered.json`은 runtime authority가 아니다.
- manual in-game validation은 `pass`로 기록됐다.
- current round는 build/runtime/in-game까지 포함한 closeout으로 읽는다.

## reopen 조건

다음이 생기면 body-role closeout은 재개방될 수 있다.

- `LAYER4_ABSORPTION` introduced hard fail 발생
- full preview regression에서 rejected row 발생
- source expansion 이후 `IDENTITY_ONLY`/`FUNCTION_NARROW` 분포가 의미 있게 변한 경우
- manual override lane에서 deterministic repair 실패가 반복되는 경우
