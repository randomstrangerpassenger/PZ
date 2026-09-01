# Iris shared composition / Menu / Tooltip 실행 결과

상태: **complete — 구현, 계획상 필수 자동 검증, 패키지 생성과 사용자의 실제 PZ KO/EN 화면 재관찰을 완료했다.** 사용자 프롬프트가 계획상 owner gate를 사전 승인했으므로 해당 gate는 진행했다. 이 문서는 이번 실행의 closeout이며 별도 validator나 새로운 acceptance authority가 아니다.

## 구현 결과

기존 installed Body Compiler의 shared composition 경로를 유지하면서 기술서 55개의 Menu 상세 획득 장소를 보완했다. 55개는 같은 source slot 하나를 사용하며 다른 항목의 기능이나 획득 장소를 이름·분류·문장 패턴으로 추론하지 않았다.

- KO 최종 문구: `획득 방법: 학교, 서점, 도서관, 가정집 책장, 책 상자, 우체국과 우편 차량에서 발견된다.`
- EN 최종 문구: `Found in schools, bookstores, libraries, home bookshelves, book crates, post offices, and postal vehicles.`
- `Base.BookCarpentry1`과 `Base.BookMetalWelding1`을 포함한 55개 `Base.Book*`가 같은 구조와 전체 장소 범위를 사용한다.

기술서의 기존 독서 조건·적용 레벨·배율·페이지 설명은 유지했다. Tooltip S2의 승인 core, absence, hold, silent 판단도 바꾸지 않았으므로 T2 fixed Lua와 Recipe companion은 기존 승인 바이트를 유지한다. Alt Tooltip은 사용자가 확인한 Iris 박스 자동 크기 조정 경로를 그대로 사용하며 이번 변경 범위에 줄바꿈이나 padding 규칙을 추가하지 않았다.

## Browser와 Wiki 스크롤

Browser는 기존 구현대로 상세 본문을 너비에 맞춰 줄바꿈하고 계산된 본문 높이를 기존 Browser 스크롤 범위에 포함한다. 이번 후속 수정에서는 Browser 코드를 추가로 바꾸지 않았다.

Wiki는 제목과 닫기 버튼을 고정된 바깥 패널에 두고, 본문만 투명 child `ISPanel`로 분리했다. 본문 panel은 `setScrollChildren(true)`와 `addScrollBars()`를 사용하며, wrapped label마다 누적한 `yOffset`을 `setScrollHeight(math.max(content.height, yOffset + 10))`에 연결한다. 따라서 바깥 panel은 화면 안에 머물고 긴 본문만 세로로 스크롤된다.

자동검사는 실제 PZ의 mouse wheel/scrollbar hit testing, glyph, 해상도/UI scale을 보증하지 않는다.

## Identity와 전파

- 최종 Layer 3 generation: `dvf33-ed92fa5c9ed4a1ed367f5d79365d04e1996e36a05d76a33bd7b8dd2176e7f82f`.
- generation descriptor SHA-256: `36e3f3f589bd91678b87ea0cd1f33ad27d33fa9a17edfaff6fd0ece8b064eaf8`.
- 최초 구현 후보: commit `276d28134ddea0bab674cae3df639b34eebec99d`, tree `77d2a65cc45e56c0461e5504f800bbed3f7045e8`.
- 최종 T1 검증 subject: commit `87a44ba7ed0b85e2a96109ffdbd4bbe66a553e8e`, tree `3fbdcfdce4fe659f9bf41698a43e3f915951f704`.
- T1 final closeout SHA-256: `de4453813c6e5341582d763fb47b0b0363c7992a7b980c156b505cac4cacca99`.
- 최종 T2 검증 subject: commit `11039018314598c967337b89ad6b3becf5c6a6c6`, tree `5ac4605f30f95b5d0205400d1694508b72ecf997`.
- T2 fixed Lua SHA-256: `f4a2ec3ba1f9b2e830c538374991d1a02c20b65e3bbb2876c3f5f7959018995f`.
- Recipe companion SHA-256: `b94301ecd933fd86e5e9f254611302ab42b5e5accbe587bb453d7e65e4f628d1`.
- T2 projection manifest SHA-256: `fdf8a0ce245c1b34fc33898e06f89e7a2cfb6283408c1027b4fdf72ba69aae46`.
- T2 final closeout SHA-256: `300cb393fccfe6616eb4de300817a90b0f066f0d9886cc7515bf07c525c1a682`.

Universe 2,105, KO/EN public 각 2,099, S2 core 2,048, T1 support 2,280을 유지한다. Classification, D5, T1 binding은 새 generation-qualified locator와 exact identity에 결속했다.

## 필수 검증

계획과 Codex Reviewer가 승인한 최소 묶음만 마지막 단계에 실행했다. 아래 PASS는 각 명령의 실제 종료 코드 0에만 근거한다.

| 실행 | 결과 |
|---|---|
| strict T1 candidate | exit 0, correction 0, handoff 2,280, progression OPEN |
| T1 canonical full Run A | exit 0, `213 passed, 118 subtests passed in 181.10s` |
| T1 canonical full Run B | exit 0, `213 passed, 118 subtests passed in 177.91s` |
| T1 comparator / finalizer | 각각 exit 0, comparator succeeded, final state complete |
| T2 독립 A/B와 finalizer | 각각 exit 0, Lua/manifest byte-identical, final state complete |
| focused 3파일 | exit 0, `18 passed in 13.12s` |
| installed `inspect current` | exit 0 |
| Lua syntax | exit 0, 264 files |
| 최종 T2 canonical full | exit 0, `213 passed, 118 subtests passed in 181.52s` |
| package builder | exit 0, current runtime payload applicability PASS |
| 실제 package Lua Menu/Tooltip consumer | exit 0, exact keys 2,280, legacy calls 0, KO/EN Menu 각 2,099, S2 2,048 missing/unverified/mismatch 0, L4 각 locale 530 missing 0 |

첫 canonical 진입들은 테스트 수집 전에 기존 environment의 tooling source mismatch, receipt 뒤 `__pycache__` 변화, Windows work path 267 > 259 때문에 fail-closed로 중단됐다. exact wheel 환경을 기존 writer로 다시 결속하고 receipt 이후 Python을 `-B -s`로 고정했으며, 짧은 work root를 사용해 coverage를 줄이지 않았다. 이 준비 실패들은 PASS나 필수 실행 횟수로 세지 않았다.

포함된 테스트를 별도로 반복하지 않았고 기존 계약이 요구한 실행 receipt·manifest 외에 새 Gate, validator, proof, seal, receipt, manifest, census를 추가하지 않았다. `.tmp/body`와 그 밖의 ad hoc helper는 이번 작업의 일회성 보조 수단이며 canonical validator나 정책 authority가 아니다.

## 패키지

- 설치용 폴더: `C:/Users/MW/Downloads/coding/PZ/.tmp/z/p/Iris`
- ZIP: `C:/Users/MW/Downloads/coding/PZ/.tmp/z/p/Iris.zip`
- ZIP 크기: 694,217 bytes
- ZIP SHA-256: `5e0755067c0deac21412b935b1a0fab475d31331442bda30f42db1d3c3a5655d`
- Package manifest: `C:/Users/MW/Downloads/coding/PZ/.tmp/z/p/Iris.package_manifest.sha256.json`, 141 files, SHA-256 `3188c6ee5c88277f888a842440f5c712e822a120874efc07a72b8bd45b04a27c`

패키지는 current generation 하나만 포함하며 predecessor generation을 설치물에 섞지 않는다. 사용자의 실제 Project Zomboid 설치 폴더에는 쓰지 않았다.

## 실제 PZ 관찰 결과

사용자는 이전 패키지에서 공통 동작, CannedPotato2, BathTowel/DishCloth, EngineDoor1, Axe, Generator, 레시피 전반과 EN locale의 KO 부재를 확인했다. 이어 최종 패키지를 실제 PZ에서 재관찰해 KO와 EN 모두 글이 잘리지 않고 잘 보인다고 확인했다. 이 사용자 관찰로 이번 수정의 긴 공개 본문 표시와 두 locale의 화면 가독성 범위를 수용했다.

관찰 결과를 모든 항목·해상도·UI scale의 전수 인증으로 확대하지 않는다. Alt Tooltip은 이번 변경 범위 밖이다. 가짜 레시피의 실제 존재 여부, Build 42, 멀티플레이, 장시간 성능, 모든 해상도/UI scale, release/Workshop/deployment도 이번 범위가 아니다.
