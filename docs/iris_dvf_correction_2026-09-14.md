# DVF 목적 중심 설명 교정 결과

이 문서는 1차 교정 시점의 기록이다. 재검수 지적을 반영한 **최신 결과·해시·검증은 [추가 교정 보고서](iris_dvf_followup_2026-09-14.md)**에 있다. 아래 1차 수치와 예시는 당시 상태이며, 연결된 전체 HTML·누적 scopes/fulltext는 최신본으로 갱신했다.

2026-09-14. 기존 전수 평가에서 제기한 A–G 범위를 생성 규칙과 근거 관계에서 교정하고, 전체 설명을 다시 생성했다. 정규화 어댑터는 추가하지 않았다.

## 산출물과 검토 범위

- 기준: `iris_dvf_current_full_review_2026-09-14.md`의 원본 설명. 원본 작업 디렉터리 `C:/Users/MW/Downloads/coding/PZ`는 읽기 전용으로 사용했다.
- 작업 기준 커밋: `549f01f1f08a74acb51b38282a144915584b0bbc`.
- 원본 descriptions SHA-256: `c9e1d15da5fe6179567d60b4e8f622ce11ac6a30ce26f5a48a47839715c7b8e1`.
- 최종 descriptions SHA-256: `625020e7e68ed9fcc7cd9c31fab3c529c2b72b53bd7e83a1ddc298b3ec819332`.
- 최종 blocks SHA-256: `294b16ea0afcdd82652ea19ced1319bda1facd15335f1cf8ac84cccbfec52f3c`.
- 2,105 ID, KO/EN × Compact/Expanded 8,420좌표. 797 ID의 2,270좌표 문면 변경.
- 최종 동일 문면 묶음 501개 중 변경된 183개 묶음의 양 언어·양 깊이를 검토했다. 재검수에서 발견한 빵칼 대상명 중복과 탄약 명사 중복도 고친 뒤 재생성했다. 기존 전수 평가의 미변경 문면과 조사 후 유지한 범위는 아래 판정을 적용했다. 동일 문면은 동일 근거를 보증하지 않는다.
- 설명 있음 1,976 ID, absent 129 ID가 그대로 유지된다. 새 absent, failed, 설명 속 가운데점은 없다. 기존 preserved_fact_refs는 모두 보존되며 Expanded에서 빠진 참조는 내부 용도에 남는다.

전문과 범위: [변경 문면 전문](iris_dvf_correction_2026-09-14_fulltext.txt), [전후 좌표·ID·문면 묶음](iris_dvf_correction_2026-09-14_scopes.json). [전체 현재 설명](iris_dvf_descriptions.html)은 8,420좌표, [전후 비교](iris_dvf_description_review.html)는 변경 2,270좌표를 담는다. 두 HTML의 해시와 각 좌표의 문장·접힌 대상 항목을 최종 JSON과 대조했다.

## A–G 처리

| 범위 | 교정 및 유지 판단 |
| --- | --- |
| A: 제작 분류와 목적 | 야구 방망이는 일반 목공 재료 대신 못 박은 야구 방망이로 개조하는 관계를 표현한다. 고정 결과를 유지하는 SpikedBat/UpgradeSpear 콜백을 확인하고, 현재 투입 역할과 결과 무기 분류를 사용했다. 천막 재료는 텐트 제작 목적을 표현한다. 폭넓은 재료의 유효한 상위 분류는 유지했다. |
| B: 미끼 350 ID | 삽입 메뉴에서 동물 수용까지 전체 ID 전달 경로, Animals 등록, 양수 baits 항목, 변환 레시피의 별도 결과 ID를 확인했다. 직접 수용 24 ID만 공개 미끼 목적을 유지하고 326 ID의 삽입 사실은 내부에 보존했다. 조사 집합을 곧바로 삭제 목록으로 사용하지 않았다. 미끼 제외로 용도가 사라질 뻔한 수박과 비스킷 틀은 확인된 손질·꺼내기 목적을 별도로 살렸다. |
| C: Compact 깊이 | 동일 천 의류 176 ID는 착용·직물 재활용·연료 개요로 묶었다. 후드 조절은 남기고 Expanded의 천 회수·시트 로프·가위 등은 보존했다. 가위와 시트의 재료 활용, 렌치의 정비 활용도 개요로 묶되 회수 사실이 있을 때만 회수 목적을 포함한다. 더러운 천의 세척과 붕대 활용은 의미가 있으므로 무조건 축약하지 않았다. |
| D: Expanded 대상 | 장치 부품은 확인된 폭발·소이·연막·소음 장치 범주를 제공한다. 제작한 창은 확인된 부착물 예를 제공한다. 톱·도끼 등은 실제 음식 손질 대상, 빵칼은 빵·케이크·파이를 제시한다. 정비 잡지 3종은 스크립트의 Standard/Commercial/Performance 표시명과 Basic/Intermediate/Advanced 학습 관계를 확인했으며 기존 문구를 유지한다. |
| E: 조작과 용도 | 알람 영어는 원하는 시각에 울리거나 끄는 목적 문형으로 고쳤다. 가구 이동 반복 102 ID와 설치된 차량 문·창문 조작은 내부 관리로 분류하되 교체·설치·재료 회수는 보존했다. 차량 메뉴가 EngineDoor/TrunkDoor도 포함하고 실제 잠금 가능 여부를 검사하므로 후드라는 이름만으로 잠금 사실을 부정하지 않는다. VHS·붕대의 문맥상 유용한 효과는 유지했다. |
| F: 영어 및 반복 | 개봉 영어 26 ID는 내용물을 먹거나 마시는 목적, 씨앗은 꺼내 심는 목적을 표현한다. 결과 명사의 관사·복수·불가산 처리를 개선했다. 우산은 비 보호와 빗속 탐색 페널티 완화를 자연스럽게 표현한다. 수리 동사 반복을 묶고 기기의 CD/VHS 호환 범위를 구별했다. |
| G: 추가 근거 | 양방향 무전기 9 ID는 실제 캐릭터 발화 송신 경로가 확인되어 공개 목적을 추가했다. Expanded에 전원·마이크·주파수·범위 조건을 둔다. 알람 계열 16 ID 중 Classic 8 ID는 네이티브 isDigital 조건에 맞춰 알람 조작을 내부로 전환한다. 금속 드럼 불쏘시개 354 ID는 의류·문학 category를 받는 실제 조건이 확인되어 보존한다. absent 129 ID는 그대로이며 전부 결함이라는 판정은 하지 않는다. |

대표 결과:

- 야구 방망이: “못 박은 야구 방망이 형태로 개조할 수 있다.”
- 일반 천 의류 Compact: “착용할 수 있다. 직물 재료로 재활용할 수 있다. 연료나 불쏘시개로도 쓸 수 있다.”
- 빵칼 Expanded: “빵, 케이크, 파이를 나누는 데 쓸 수 있다.” / “It can be used for cutting up bread, cake, and pie.”
- 수박: “자르거나 쪼개어 조각으로 나눌 수 있다.” / “It can be sliced or smashed into pieces.”

## 근거와 구현 경계

`Iris/build/description/source_support/b41_dvf_purpose_review.json`에 설치된 B41과 일치하는 Lua 소비자 8개, 네이티브 클래스 2개의 해시 및 판독 내용을 기록했다. `purpose_evidence.py`는 이 스냅샷과 Lua 해시를 검사하고 관계 근거를 기존 생성 흐름에 연결한다. 레시피 관측문의 CRLF/LF 차이를 처리하여 이미 승인된 관계를 놓치지 않게 했다. 다른 피연산자가 해석되지 않았다는 이유로 현재 아이템의 확정 역할과 결과까지 버리지 않되 미해석 피연산자는 별도로 보존하고 수량·완전한 레시피를 주장하지 않는다.

무전은 UpdateScripts의 발화 수집, 전원·TwoWay·마이크 검사, 휴대 장비 검사, SendTransmission, 수신 주파수·거리 검사, AddDeviceText까지 확인했다. VOIP 전달이나 모든 실행 상태의 성공을 증명한 것은 아니다. Classic 조건은 표시명 추정이 아니라 AlarmClockClothing 생성자의 fullType.contains("Classic")와 isDigital 반환값에 근거한다. 네이티브 파일은 검토 시점 해시에 묶인 정적 판독이며 실행 시 설치 게임을 다시 검사하는 기능은 아니다.

미끼는 현재 로컬 B41 등록과 소비 경로에 한정한다. 외부 모드가 추가할 Animals/baits 등록은 이 정적 자료에 포함되지 않으므로 모드 전체의 기능 부재를 단정하지 않는다. 드럼은 일반 불 피우기 메뉴의 직물 제한을 잘못 옮겨 적용하지 않았으며 장신구도 category 조건을 통과한다.

## 검증

아래 관련 명령은 모두 종료 코드 0으로 완료했다.

```powershell
uv run --project ./Iris/tooling python -I -B -m pytest --noconftest -c ./Iris/tooling/pyproject.toml ./Iris/build/description/v2/tests/test_layer3_composition.py::test_layer3_composition_contract ./Iris/build/description/v2/tests/test_layer3_description_composition.py::test_layer3_description_composition ./Iris/build/description/v2/tests/test_layer3_rule_generalization.py ./Iris/build/description/v2/tests/test_layer3_dvf_purpose_review.py --basetemp ./.tmp/dvf/final -q -s --tb=short
# 11 passed in 35.58s. blocks/descriptions 전체 재생성 포함.

uv run --project ./Iris/tooling python -I -B -m pytest --noconftest -c ./Iris/tooling/pyproject.toml ./Iris/build/description/v2/tests/test_layer3_product_integration.py::test_current_menu_input_binding -q --tb=short
# 1 passed in 2.60s. 최종 descriptions/blocks 해시 바인딩 갱신 후 실행.

powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
# Lua syntax validation OK: 266 files
```

보조 전수 비교와 HTML 내용 대조도 종료 코드 0. Python 변경 범위의 `git diff --check`도 종료 코드 0이다. 초기 실행의 acquisition 해시 실패는 체크아웃 개행 차이를 원본 바이트와 맞춰 해결했다. 이후 기존 문장 기대값 실패는 의도한 공개 용도 변경에 맞춰 갱신했으며 최종 전체 관련 검사에서 통과했다.

이 결과는 생성 규칙·전체 composition 산출물·현재 메뉴 입력 바인딩의 교정이다. 기존 런타임 current pointer나 게임 설치 산출물을 교체한 배포가 아니다. 실제 게임 화면의 줄 수·폰트·물리적 맞춤은 측정하지 않았다. 모든 아이템의 모든 실행 경로를 다시 증명하는 전수 기능 감사도 아니다. 현재 평가에서 지정한 관계 조사와 문면 교정은 완료했다.
