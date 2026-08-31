# Iris shared composition / Menu / Tooltip 실행 결과

상태: **partial — 구현, 계획상 필수 자동 검증, 패키지 생성 완료. 새 패키지의 실제 PZ 화면 관찰은 남아 있다.** 사용자 프롬프트가 owner gate를 사전 승인했으므로 해당 gate는 진행했다. 이 문서는 이번 실행의 closeout일 뿐 별도 validator나 새로운 acceptance authority가 아니다.

## 구현 결과

기존 installed Body Compiler의 shared composition 경로를 사용해 KO/EN Menu와 S2 Tooltip이 같은 bilingual core를 소비하도록 했다. 런타임에서 문장을 새로 조합하거나 항목 이름으로 기능을 추론하지 않는다. 최종 입력은 2,105개 항목이며, shared 193개와 explicit 6개를 합친 199개의 설명을 실제로 바꿨다. 나머지 항목의 기존 보존·hold·empty-core 판단은 유지했다.

사용자 게임 관찰에서 드러난 번역투를 반영해 두 언어를 각각 행동 중심 문장으로 다듬었다. 최종 후보 두 독립 결과는 byte-identical이며 SHA-256은 `bf75cf0e397c0c338515ce1f7b61356547a099b16ea354ee73cdefb364f790a0`이다. 외부 Codex 검토에서 최종 후보에 추가 actionable 지시가 없음을 확인했다. 이는 문구 검토이며 사람의 게임 관찰을 대신하지 않는다.

대표 결과:

| 항목/계열 | KO | EN |
|---|---|---|
| Axe | 나무를 찍거나 자를 수 있다. | Use it to chop or cut trees. |
| BookCarpentry1 | 글을 읽을 수 있고 목공 레벨이 0~1이라면, 이 책을 읽어 목공 1~2레벨 구간의 경험치 획득 배율을 높일 수 있다. | If you can read and are at Carpentry level 0–1, this book boosts your XP multiplier for levels 1–2. |
| CannedPotato2 계열 | 통조림 따개로 열어 안에 든 감자를 꺼낼 수 있다. | Open it with a can opener to get the potatoes. |
| 휴대 보관 계열 | 물건을 넣어 보관하거나 운반할 수 있다. | Use it to store and carry items. |
| 연료 용기 계열 | 휘발유를 담아 운반하거나 차량에 주유할 수 있다. | Use it to carry gasoline or refuel a vehicle. |

기술서 55개는 현재 독서 가능 레벨과 XP 적용 레벨을 구분한다. 수건 2개는 몸 건조와 표백제 혈흔 제거를 보존한다. 착용 58개는 실제 BodyLocation을 자연스러운 의류/장신구 표현으로 옮긴다. 차량 부품 27개는 후드, 앞·뒷문, 양문형 뒷문, 트렁크 덮개, 창문과 유리를 구분한다. 탄띠, 빗자루, 대걸레, WoodenLance, Generator는 개별 조건과 동작을 유지한다. 도끼 설명에 source가 제공하지 않는 효율·속도 수치를 만들지 않았고, Generator도 설치와 주변 기기 전력 공급 범위를 넘겨 쓰지 않았다.

## 읽기 패널 줄바꿈

`IrisAltTooltip.lua`의 S2 읽기 패널만 수정했다. 실제 `MeasureStringX` 측정값을 계속 사용하면서 font height에 비례한 좌우/상하 padding과 measurement slack을 확보하고, 그 값을 빼서 wrap width를 계산한다. 기존 최대 너비 360, 화면 배치, Alt 동작, 네 logical row 정책은 유지했다. Menu 너비는 건드리지 않았다.

Lua runtime harness는 mock font height 17과 34에서 측정된 각 줄이 패널의 사용 가능 너비 안에 들어오는지 확인한다. 이는 회귀 검사이며 실제 PZ 글꼴 glyph, 해상도, UI scale의 화면 적합성을 증명하지 않는다.

## Identity와 전파

- 검토가 끝난 문구 subject: commit `17fb03a29e807b83d43843a31f2cc49b5f945d37`, tree `f1e4036a4485388ee2627fd64547a81573ad0660`.
- 채택 commit: `6102b8ffe25d49b7b28831feb32f76e96d27dd9f`.
- 새 generation: `dvf33-22756bdcfae37acb1ced4a49ffa6c26efe2015ea2370723c0ddadbd73a6a83d4`.
- generation descriptor SHA-256: `3c50517df1a524824c124f7757e148b919c1297bdc34ac78bc6fddd574c19aa3`.
- T1 final subject: commit `f4067cb73374094490dfd7f3c7983f1aba71c678`, tree `956281671dbb425e3615c3754842223e85869e59`.
- T1 final closeout SHA-256: `2c78ceaf7b68afad6237431497cc045ae89d304f25d22808578674f81e09559b`.
- T2 validated subject: commit `b738065558cd9da85274caef1b6234a02e29a54f`, tree `ae757ad15d82d7c82183f11634e73922a4bb67d9`.
- T2 fixed Lua SHA-256: `f4a2ec3ba1f9b2e830c538374991d1a02c20b65e3bbb2876c3f5f7959018995f`.
- Recipe companion SHA-256: `b94301ecd933fd86e5e9f254611302ab42b5e5accbe587bb453d7e65e4f628d1`.
- T2 projection manifest SHA-256: `5af8c09cd4b509495377cdd722b990887eb1d6b030349ec836cb17e98c9cbfb7`.
- T2 final closeout SHA-256: `9a69ab9de891faa280f2765959a3dc20e224394930b3a552c6baf045ca18798a`.

Universe 2,105, KO/EN public 각 2,099, S2 core 2,048, T1 support 2,280을 유지한다. 새 generation의 EN runtime은 2,099개이며 S2 owner는 2,048개다. Classification, D5, T1 binding은 새 generation-qualified locator와 exact identity로 다시 결박했다.

## 필수 검증

계획에 명시된 검사는 마지막 단계에 모아 실행했다. 아래 PASS는 각 명령의 실제 종료 코드 0에만 근거한다.

| 실행 | 결과 |
|---|---|
| 최종 T1 strict candidate, canonical A/B, comparator, finalizer | 모두 exit 0. A/B는 같은 subject에서 각각 213 tests, 118 subtests, standalone 4개를 통과했고 final state는 complete |
| T2 독립 A/B 생성 | exit 0, 최종 subject 결박과 Lua/manifest bytes 동일 |
| T2 전용 focused 3파일 | exit 0, `18 passed in 12.48s` |
| installed `inspect current` | exit 0 |
| Lua syntax | exit 0, 239 files |
| 최종 canonical full gate | `.tmp/og/run.json`, exit 0, subject `b7380655…` |
| package script | exit 0, current runtime payload applicability PASS |
| 실제 package Lua Menu/Tooltip consumer | exit 0. exact keys 2,280, legacy calls 0, KO/EN Menu 각 2,099, S2 2,048 missing/unverified/mismatch 0, L4 각 locale 530 missing 0 |

실패를 성공으로 소급하지 않았다. 첫 T1 full은 stale runtime lookup identity 때문에 4개가 실패했고, production parity module로 새 digest를 기록한 뒤 새 subject에서 A/B를 다시 통과했다. 최종 T2 full의 첫 두 launch는 테스트 전에 각각 PowerShell `Get-FileHash` autoload와 Windows 경로 길이 263 > 259로 중단됐다. system module path와 기존 방식의 짧은 `w8` work root를 사용해 검증 coverage를 줄이지 않고 같은 gate를 완료했다. Package consumer의 첫 호출도 허용된 replay scratch 경계에서 테스트 전에 거부됐으며 clone 내부의 새 scratch에서 같은 소비자를 정상 완료했다.

추가 confidence만을 위한 full, 중복 gate, seal, receipt, manifest, census를 만들지 않았다. `.tmp/body`의 helper와 ad hoc 출력은 이번 작업의 일회성 보조 수단이며 canonical validator나 정책 authority가 아니다.

## 패키지

- 설치용 폴더: `C:/Users/MW/Downloads/coding/PZ/.tmp/pkg/current/Iris`
- ZIP: `C:/Users/MW/Downloads/coding/PZ/.tmp/pkg/current/Iris.zip`
- ZIP 크기: 692,581 bytes
- ZIP SHA-256: `58099dd95551a6f7d44243d75e9b17196258b804e1425c7775e774701fc2ddd8`
- Package manifest: `C:/Users/MW/Downloads/coding/PZ/.tmp/pkg/current/Iris.package_manifest.sha256.json`, 140 files

패키지는 current generation만 포함하며 predecessor generation을 설치물에 섞지 않는다. 사용자의 실제 Project Zomboid 설치 폴더에는 쓰지 않았다.

## 실제 PZ 관찰과 남은 항목

사용자는 이전 패키지에서 공통 동작, CannedPotato2, BathTowel/DishCloth, EngineDoor1, Axe, Generator, 레시피 전반, EN locale의 KO 부재를 확인했다. 동시에 BookCarpentry1, 같은 구조의 BookMetalWelding1, Broom, 긴 EN 문장이 잘리고 양쪽 언어가 번역투로 느껴진다고 보고했다. 이 관찰을 근거로 현재 문구와 S2 wrap 계산을 수정했다.

현재 ZIP은 그 뒤에 만들어진 새 패키지이므로 이전 관찰을 승계해 실제 화면 PASS로 기록하지 않는다. 실제 게임에서 남은 확인은 다음과 같다.

1. 이전에 잘렸던 동일 해상도/UI scale에서 `BookCarpentry1` KO/EN 전체 문장이 보이는지 확인한다.
2. `BookMetalWelding1` EN과 `Broom` KO/EN에서 모든 줄이 보이고 문장이 자연스러운지 확인한다.
3. `Bag_BowlingBallBag` KO/EN이 물건 보관·운반 용도로 자연스럽게 읽히는지 확인한다.
4. 긴 문장을 화면 왼쪽과 오른쪽 가장자리에서 각각 열어 패널 배치와 wrap이 화면 밖으로 나가지 않는지 확인한다.
5. 대표 착용품 1개와 차량 부품 1개로 짧은 문장도 불필요하게 좁거나 어색하게 줄바꿈되지 않는지 확인한다.

가짜 레시피의 실제 존재 여부는 이번 게임 관찰로 판별하지 못했다. Recipe companion은 canonical source에서 349 FullTypes / 781 variants로 생성되고 자동 검증을 통과했지만, 이는 사람의 전체 레시피 내용 검토를 뜻하지 않는다. Build 42, 멀티플레이, 장시간 성능, 모든 해상도/UI scale, release/Workshop/deployment는 이번 범위가 아니다.
