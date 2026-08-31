# Iris shared composition / Menu / Tooltip 실행 결과

상태: 최종 자동 검증·제품 통합 진행 중. 사용자 사전 승인으로 owner gate를 진행했으며, 실제 사람의 문장 검토와 PZ 관찰은 수행하지 않았다. 이 문서는 단일 실행 closeout이며 별도 validator나 acceptance authority가 아니다.

## 구현과 범위

`compose_layer3_shared.py`를 기존 installed Body Compiler에 추가했다. 기존 seven-input의 facts metadata, profile declaration, overlay binding으로 shared / explicit / retained 경로를 명시한다. `build layer3 compose-successor`는 채택 전 candidate를 만들고, 기존 generation builder는 이미 채택된 결과를 materialize한다. Runtime에서 문장을 조합하거나 의미를 추론하지 않는다.

새 Menu KO/EN과 S2 owner는 동일한 bilingual core를 소비한다. Compiler는 singleton core fact identity, source-slot hash, 조건·효과 parameter의 core 포함, locale placeholder 대응, optional block과 retention hash를 확인하며 오류 시 legacy 번역으로 fallback하지 않는다. Menu context/acquisition은 별도 보존한다. Single-core는 identity 제약이며 기본 용도 수를 하나로 제한하지 않는다.

최종 candidate는 `c8.json` / `c9.json`, SHA-256 `01d819386c310ac8bf0669c131f0be7e1a7d71b749177401d75cdd8bc43d579b`다. 두 결과는 독립 호출로 생성했다. Owner의 실행 프롬프트는 이번 source material·candidate adoption·필요한 기존 계약 갱신을 사전 승인했다. AI의 후보 검토를 human acceptance 또는 게임 관찰로 기록하지 않는다.

| 경로 | 항목 수 | 실제 변경 |
|---|---:|---|
| shared 기술서 | 55 | 기술·현재 독서 가능 레벨·XP 적용 레벨·독서 조건을 core에 표시. Menu에는 쪽수·10% 단위 진행 배율·최대 배율 |
| shared 수건 | 2 | 몸 건조와 표백제 혈흔 제거를 함께 core에 보존. 젖은 몸·잔여 사용량 조건 포함 |
| shared 착용 | 58 | source BodyLocation에 따른 착용 부위와 직접적인 의류/장신구 표현 |
| shared 휴대 보관 | 24 | source Container/Capacity 및 기존 운반 용도를 직접 표현 |
| shared 차량 부품 | 27 | 후드·앞문·뒷문·양문형 뒷문·트렁크 덮개·앞/뒤 창과 앞/뒤 유리를 구분. 탈착 표현만 공유 |
| shared 연료 용기 | 6 | exact Petrol tag와 기존 운반·주유 용도를 표현 |
| shared 통조림 | 12 | exact recipe input/result의 내용물과 CanOpener 조건 |
| shared 도끼 / 근접 공격 | 9 | 기존 벌목 4개와 타격·밀어내기 5개의 목적을 직접 표현 |
| explicit | 6 | 탄띠 2개, 빗자루, 대걸레, WoodenLance, Generator. 개별 조건과 복수 동작 보존 |
| 합계 변경 | **199** | shared 193 + explicit 6. Coverage 확대 수와 구분 |

Item별 exact 경로와 source binding은 기존 `dvf_3_3_overlay_support.jsonl#body_composition` 및 `dvf_3_3_facts.jsonl#slot_meta/body_material`에 있다. 이 필드는 생산 입력이며 별도의 검사 registry가 아니다. Source는 실제 repository item/recipe/Lua 선언과 기존 승인 semantic material에서 확인했다. 이름·classification·기존 rendered prose로 기능, 수치, 조건을 복원하지 않았다.

## 유지 판단

초기 authoring의 일괄 `already_adequate` 배정은 최종 근거로 채택하지 않았다. 기존 closeout의 1,529 revise / 12 reduce는 이전 작업의 교정 이력이다. 현재 primary/core/KO·EN과 해당 source 판단을 대조한 뒤, 남아 있던 번역투·개별 target 결손과 조건을 추가로 보완했다. 과거 숫자를 이번 변경 목표로 삼지 않았다.

| 최종 retention | 항목 수 | 이유 |
|---|---:|---|
| 현재 설명 유지 | 1,580 | 이미 기본 용도·효과와 필요한 제한을 직접 설명하는 승인 문장. 음식의 섭취/요리 역할, Battery의 전원 공급, 구체적인 제작·의료·도구 목적 등은 불필요하게 재작성하지 않음 |
| 실제 source gap | 1 | `Base.String`: Normal/Material/정체성 선언 외에 더 구체적인 기능을 승인할 direct action/exact recipe 관계가 없음. Twine/Wire 기능을 상속하지 않음 |
| 기존 source hold | 273 | 원래 exact membership과 각 항목의 sprite/legacy/조건/identity 등 미해결 근거 보존 |
| 기존 보호 | 12 | 기존 보호된 승인 core/detail 보존 |
| 나머지 explicit empty-core | 40 | 기능 추정이나 문구만으로 새 S2 eligibility를 만들지 않음 |
| 합계 | **1,906** | 변경 199 + 보존 1,906 = universe 2,105 |

Retained binding에는 해당 current primary hash, 기존 exact 항목 source 판단, reason ref를 남겼다. Retention은 새로운 source truth·semantic quality 승인도, 미작업을 숨기는 상태도 아니다. Empty-core 총 57개 중 17개는 기존 hold와 겹친다.

## 대표 표현

| 항목 | 이전 KO | 새 KO / EN core |
|---|---|---|
| BookCarpentry1 | 적용 수준에서 읽으면 목공 경험치 획득 배율을 높이는 기술서다. | 글을 읽을 수 있고 목공의 현재 레벨이 0~1일 때 읽으면, 목공 1~2레벨 구간의 경험치 획득 배율을 높일 수 있다. / When you can read and your current Carpentry level is 0–1, reading it can increase the XP multiplier for Carpentry levels 1–2. |
| BookCarpentry5 | 적용 수준 중심의 일반 설명 | 현재 레벨 8~9, XP 적용 9~10. 같은 표현의 item별 값이며 Menu 최대 배율은 16배 |
| Bag_BowlingBallBag | 보관 작업에서 소지품이나 내용물을 담아 휴대하거나 나눠 옮길 때 다룬다. | 물건을 담아 운반하는 휴대용 보관함이다. / A portable container used to store and carry items. |
| EngineDoor1 | 차량 정비 작업에서 차체 패널이나 유리를 떼어내거나 다시 끼울 때 다룬다. | 차량에서 떼어내거나 다시 끼울 수 있는 후드 부품이다. / A vehicle hood that can be removed and refitted. |
| CannedPotato2 | 개봉해 감자를 꺼낼 수 있는 통조림이다. | 통조림 따개로 통조림을 열면 감자를 꺼낼 수 있다. / Open the can with a can opener to obtain potatoes. |
| Broom | 재 제거와 표백제 혈흔 제거 목적, 파손 조건은 Menu context | 부러지지 않았다면 재를 치우거나 표백제와 함께 혈흔을 지울 수 있다. / If it is not broken, use it to clear ashes or remove blood stains with bleach. |
| Axe | 벌목 작업에서 나무를 찍거나 자를 때 쓴다. | 나무를 찍거나 자르는 데 쓴다. / Used to chop or cut trees. |

기술서·통조림·빗자루 등은 승인된 source에서 조건/값을 보완한 semantic clarification을 포함한다. 단순한 표현 정리와 이를 구분하며 scalar primary/source fact ID를 임의 재합성하지 않았다. 새로운 속도·효율·호환성·거리 수치를 추가하지 않았다.

## Identity와 전파

- 시작 HEAD: `e3bef7d656d89fb9a4417647db3a7cbb072ff953`.
- 시작 generation: `dvf33-103dd029d58267ffa696fcb9fa197d5564d14716f12f6ae3ee398b4fb3b41d83`.
- 최종 generation: `dvf33-028b1189a27295376ef37a5fe855f0886b15ae3d217486f9b5ace93cd3fc5a0c` (`g9` / `g10` 동일).
- 최종 T1 검증 대상: `ac270740` (기존 taxonomy에 새 compiler 테스트 2개 등록 후 subject).
- Universe 2,105, KO/EN public 각 2,099, silent 6, S2 core 2,048, explicit empty-core 57, outside-universe owner absence 175, support 2,280을 유지한다. Gained/lost core는 모두 빈 집합이다.
- S1 1,406 applicable / 874 display silence와 S3/S4 selection은 변경하지 않는다. Classification 및 D5의 generation-qualified locator/hash만 기존 의미와 exact identities를 유지하여 재결속했다.

G5는 실제 변경된 `compose_layer3_text.py`의 Git bytes/ancestry/last-writer를 기존 schema의 append-only successor 0018로 연결했다. Historical 0013–0017은 재작성하지 않았다. G5 naturalization의 실제 실행은 새 successor 함수를 호출하지 않아 그 ordered 21-path set은 그대로이며, shared producer module은 complete-generation implementation identity에 포함한다. 두 identity의 claim을 동일시하지 않는다.

## 검증과 실패 이력

최종 결과 표는 진행 중이며 exact exit 0 확인 후 확정한다. 적용되는 성공 경로는 T1 동일 subject full A/B + 기존 comparator, 그 뒤 finalized handoff를 채택한 최종 T2 subject full 1회다. T2 artifact A/B는 데이터 생성 비교이며 추가 full A/B가 아니다. 동일 subject/input/producer/execution boundary의 포함 검사는 재사용한다.

| 실행 | 현재 결과 |
|---|---|
| installed successor candidate / generation A/B 및 기존 installer | exit 0, 위 candidate/generation identity |
| 새 compiler focused 2개 | 초기 코드 subject에서 exit 0. 최종 full에 포함된 경우 별도 반복하지 않음 |
| final strict T1 candidate | `t1g`: 2,280행, correction 0, progression OPEN, candidate_present |
| T1 canonical A/B + comparator/finalizer | 진행 중 |
| T2 fixed/Recipe companion/finalizer | 대기 |
| 최종 Lua syntax / installed inspect / T2 full | 대기 |
| package / 실제 Lua Menu·Tooltip consumer | 대기 |

준비 실패 및 수정:

- 최초 launcher는 `Get-FileHash` autoload 실패로 테스트 진입 전 종료했다. 기존 테스트가 사용하는 system PowerShell module 경로를 적용했다.
- 긴 Windows checkout 경로는 263 > 259로 거절됐다. 저장소 내부의 짧은 work root로 조정했으며 coverage나 경로 guard를 삭제하지 않았다.
- G5의 이전 compiler identity guard는 actual successor 연결 전 실행을 거절했다. 기존 identity 계약을 유지했다.
- `afb5e321`의 full은 exit 1: 6 failed / 207 passed / 118 subtests passed. Legacy general-description fixture가 composed 대상을 검증하는 방식, package lookup digest, G5의 이전 expected digest를 원인별로 수정했다. 해당 실패를 최종 PASS로 상속하지 않는다.
- `32a00b8b` 실행은 추가 콘텐츠 검토가 도착하여 결과 파일 없이 중단했다. 최종 A/B로 계상하지 않는다.
- `88967a8a`의 pytest 213개/하위 118개 및 standalone 4개는 성공했으나, 추가 compiler 테스트 2개가 기존 taxonomy에 미등록되어 canonical 명령은 exit 1이었다. 기존 목록에 해당 2개만 등록하고 새 exact subject에서 필수 A/B를 실행한다. 이전 실패 결과를 수정하거나 PASS로 소급하지 않는다.

모든 임시 output/environment/integration은 선택한 저장소 내부에 두었다. 기존 도구의 external-root 조건은 격리 repository context에 대해 적용했다. 실제 PZ/사용자 설치 폴더는 열거나 수정하지 않았다. `.tmp/body`의 source authoring/rebind helper는 이번 작업의 일회성 보조 수단이며 canonical validator·정규 검사기·새 validation authority가 아니다. 기존 계약이 요구하는 기록 밖에 seal/receipt/manifest/census 체계를 추가하지 않는다.

## 검토와 관찰 한계

지정 보고 작업 `01a05297-eb3f-78d3-a5bd-fc44c02dac71`에 구현·실패·전체 대상 판단과 최종 후보를 보고했다. 해당 Codex 검토에서 vehicle target과 남은 표현을 보완했고, c8/c9에 추가 actionable 지시가 없음을 확인했다. 이는 AI 검토이며 human acceptance, 독립 생산 A/B 또는 PZ 관찰이 아니다.

실제 PZ의 Menu/S2/Alt/배치·Recipe 전환은 미관찰이다. 사용자 사전 승인과 실제 수행 사실을 구분하며 predecessor의 식품류 관찰을 이 successor에 승계하지 않는다. Runtime harness는 실제 게임의 글꼴·pixel wrapping·해상도/UI scale을 보증하지 않는다.

문제 2에 제공되는 결과는 기본 설명의 조건·효과와 Menu 상세의 명시적 분리, 같은 KO/EN semantic input, 기술서의 진행/최대 배율 detail이다. 신규 탐색·추천·상호작용 설명 체계나 모든 Menu 질문에 대한 답을 구현한 것은 아니다. Remaining hold/source gap, 임의 모드·Build 42·멀티·장시간·성능·전체 화면 환경·release/Workshop/deployment는 검증하지 않는다.

Rollback은 시작 HEAD의 input/candidate/KO pointer/EN/owner/fixed/companion을 함께 복원하는 단위다. Pointer만 되돌리고 EN·Tooltip을 successor로 남기지 않는다. Historical generation과 원본 승인 기록을 덮어쓰지 않는다.
