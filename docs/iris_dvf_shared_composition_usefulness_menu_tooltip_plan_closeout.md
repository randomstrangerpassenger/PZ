# Iris shared composition / Menu / Tooltip 실행 결과

상태: **partial — 구현, 계획상 필수 자동 검증, 패키지 생성 완료. 새 패키지의 영향 범위에 대한 실제 PZ 화면 재관찰은 남아 있다.** 사용자 프롬프트가 owner gate를 사전 승인했으므로 해당 gate는 진행했다. 이 문서는 이번 실행의 closeout이며 별도 validator나 새로운 acceptance authority가 아니다.

## 구현 결과

기존 installed Body Compiler의 shared composition 경로를 사용해 KO/EN Menu와 S2 Tooltip이 같은 bilingual core를 소비하도록 했다. 런타임에서 문장을 새로 조합하거나 항목 이름으로 기능을 추론하지 않는다. 기존 보존·hold·empty-core 판단도 유지했다.

사용자 게임 관찰에서 드러난 번역투를 반영해 두 언어를 각각 행동 중심 문장으로 다듬었다. 기술서 55개에는 source-bound 공통 획득 장소를 추가했다. 공개 문구는 KO `획득 방법: 학교에서 발견된다`, EN `Found in schools.`이며, 기존 독서 조건·적용 레벨·배율·페이지 설명 뒤의 별도 상세 문단으로 표시된다. `BookCarpentry1`과 `BookMetalWelding1`은 같은 구조를 사용한다.

도끼 설명에는 source가 제공하지 않는 효율·속도 수치를 만들지 않았고, Generator도 설치와 주변 기기 전력 공급 범위를 넘겨 쓰지 않았다. 수건 2개는 몸 건조와 표백제 혈흔 제거를 보존하며, 차량 부품은 후드·문·창문 등의 실제 역할을 구분한다. T2 fixed 데이터는 이전 승인 바이트와 동일했고 Recipe companion은 같은 fixed 데이터에서 349 FullTypes / 781 variants로 다시 생성되어 동일 바이트임을 확인했다.

## Menu와 Wiki 줄바꿈

긴 글이 고정 너비 Menu/Browser 상세 영역 밖으로 잘리는 결함을 수정했다. 새 `IrisTextLayout.lua`는 실제 `getTextManager():MeasureStringX`를 사용해 UTF-8 문장을 사용 가능한 너비에 맞춰 줄바꿈하고 기존 명시적 개행을 보존한다.

`IrisBrowserDetail.lua`는 줄바꿈 뒤 실제 줄 수로 본문 높이를 계산해 기존 스크롤 범위에 포함한다. `IrisWikiPanel.lua`도 현재 패널 너비에 맞춰 줄바꿈하며 패널 자체를 화면 경계 안에 배치한다. 따라서 긴 KO/EN 본문은 화면 밖으로 수평 잘림이 생기는 대신 여러 줄과 세로 스크롤로 읽을 수 있다.

Alt Tooltip은 사용자가 확인한 기존 Iris 박스 자동 크기 조정 경로를 그대로 유지했다. 이번 결함 수정에서는 Alt Tooltip에 별도 줄바꿈이나 padding 규칙을 추가하지 않았다.

## Identity와 전파

- 최종 Layer 3 generation: `dvf33-96b216c3a79fbbb6855f6aac3d49dbad5acbfc73c65c6a19fb3e580e7c9e448c`.
- generation descriptor SHA-256: `b35e9608c4f0370491f1fe3d171be96f90d9dc24fcf41b9f3f35d49b9e09fad9`.
- T1 검증 subject: commit `95f9c1e44cff4fcdd3d38def58febdc7838cffe1`, tree `393e14e7961b2621a0db326711c5c684e83fbc82`.
- T1 final closeout SHA-256: `0e4d523bd207139bc7e0b78a028f17fbdde45a62d39bf0451d9ece5b5b376451`.
- T2 검증 subject: commit `5812f8993977bcc173d58987053e446dbdfa0bab`, tree `60835a5c3ffb3f35656e9481de3af035dd8539c0`.
- T2 fixed Lua SHA-256: `f4a2ec3ba1f9b2e830c538374991d1a02c20b65e3bbb2876c3f5f7959018995f`.
- Recipe companion SHA-256: `b94301ecd933fd86e5e9f254611302ab42b5e5accbe587bb453d7e65e4f628d1`.
- T2 projection manifest SHA-256: `ab04f1951c71e9ef36d9029d6806a1d2231b8be1e7aba35ec18ff45127ca45ca`.
- T2 final closeout SHA-256: `a39f336b01a249cf93001cb4b82eceaffc116d8278082208b170c10abd9159e8`.

Universe 2,105, KO/EN public 각 2,099, S2 core 2,048, T1 support 2,280을 유지한다. Classification, D5, T1 binding은 새 generation-qualified locator와 exact identity로 다시 결박했다.

## 필수 검증

계획에 명시된 검사는 마지막 단계에 모아 실행했다. 아래 PASS는 각 명령의 실제 종료 코드 0에만 근거한다.

| 실행 | 결과 |
|---|---|
| 최종 T1 strict candidate, canonical A/B, comparator, finalizer | 모두 exit 0. A/B는 같은 subject에서 각각 213 tests, 118 subtests를 통과했고 final state는 complete |
| T2 독립 A/B 생성 | exit 0, 같은 subject에서 Lua/manifest bytes 동일 |
| T2 전용 focused 3파일 | exit 0, `18 passed in 13.26s` |
| installed `inspect current` | exit 0 |
| Lua syntax | exit 0, 252 files |
| 최종 canonical full gate | exit 0, 213 tests와 118 subtests 통과, subject `5812f899…` |
| package script | exit 0, current runtime payload applicability PASS |
| 실제 package Lua Menu/Tooltip consumer | exit 0, exact keys 2,280, legacy calls 0, KO/EN Menu 각 2,099 |

첫 T1 full은 acquisition 총계와 새 Layer 3 generation에 따른 runtime lookup package identity가 갱신되지 않아 5개가 실패했다. 고정 총계를 1,105로 수정하고 기존 parity module이 산출한 새 lookup digest를 기록한 뒤, 새 subject에서 A/B를 각각 다시 통과했다. 그 이전의 사전 조건 실패나 이 실패를 성공으로 소급하지 않았다.

추가 confidence만을 위한 full, 중복 gate, seal, receipt, manifest, census는 만들지 않았다. `.tmp/body`의 helper와 ad hoc 출력은 이번 작업의 일회성 보조 수단이며 canonical validator나 정책 authority가 아니다.

## 패키지

- 설치용 폴더: `C:/Users/MW/Downloads/coding/PZ/.tmp/pkg/final2/Iris`
- ZIP: `C:/Users/MW/Downloads/coding/PZ/.tmp/pkg/final2/Iris.zip`
- ZIP 크기: 676,501 bytes
- ZIP SHA-256: `b7883d6387587a9fffe72ff64b6eb681f5d6ecc4fac3defcf5237b50efe1f4a7`
- Package manifest: `C:/Users/MW/Downloads/coding/PZ/.tmp/pkg/final2/Iris.package_manifest.sha256.json`, 141 files

패키지는 current generation만 포함하며 predecessor generation을 설치물에 섞지 않는다. 사용자의 실제 Project Zomboid 설치 폴더에는 쓰지 않았다.

## 실제 PZ 관찰과 남은 항목

사용자는 이전 패키지에서 공통 동작, CannedPotato2, BathTowel/DishCloth, EngineDoor1, Axe, Generator, 레시피 전반, EN locale의 KO 부재가 정상임을 확인했다. 이번 새 패키지에서 다시 볼 범위는 결함 수정과 직접 겹치는 다음 항목으로 제한한다.

1. `BookCarpentry1`과 `BookMetalWelding1`의 KO/EN Menu 끝에 획득 장소가 각각 `획득 방법: 학교에서 발견된다` / `Found in schools.`로 표시되는지 확인한다.
2. 같은 두 기술서의 긴 본문이 Menu/Browser 상세 영역 너비에 맞춰 여러 줄로 표시되고, 아래 내용과 획득 장소까지 세로 스크롤로 읽을 수 있는지 확인한다.
3. `Base.Broom`의 KO/EN 긴 본문이 수평으로 화면 밖에 잘리지 않고 끝까지 읽히는지 확인한다.
4. 긴 문장을 화면 왼쪽과 오른쪽 가장자리에서 각각 열어 Wiki/Menu 패널이 화면 안에 머무는지 확인한다.
5. 짧은 설명 하나를 대조군으로 열어 불필요한 글자 단위 분리나 빈 줄 증가가 없는지 확인한다.

Alt Tooltip은 이번 수정 대상이 아니므로 새 줄바꿈 검증 항목으로 요구하지 않는다. 가짜 레시피의 실제 존재 여부는 이번 관찰만으로 판별하지 못했으며, 자동 검증 통과는 사람의 전체 레시피 내용 검토를 뜻하지 않는다. Build 42, 멀티플레이, 장시간 성능, 모든 해상도/UI scale, release/Workshop/deployment는 이번 범위가 아니다.
