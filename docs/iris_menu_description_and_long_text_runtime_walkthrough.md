# Iris Menu Description and Long-Text Runtime Walkthrough

> 작성일: 2026-09-01 KST
> 구현 계획: `docs/iris_dvf_shared_composition_usefulness_menu_tooltip_plan.md`
> 실행 결과: `docs/iris_dvf_shared_composition_usefulness_menu_tooltip_plan_closeout.md`
> shared composition 도입: `bc1fb0fb4c217f290327d5ebd899f51e0f49576e`
> current consumer 정렬: `32a00b8bf0f8aae3f53ee8c52365f92774f6b66d`
> 기술서·장문 표시 후속: `09d6973c1b52272661e9564d1e7d083160e2b937`, `9abef076d9a5f46bb21b5455a5e083330d04ff13`
> 최종 T1/T2 subject: `87a44ba7ed0b85e2a96109ffdbd4bbe66a553e8e`, `11039018314598c967337b89ad6b3becf5c6a6c6`
> 작성 기준 canonical-doc carrier: `1c2bcc8493061f54019d7794cdfd6874ea1f510d`
> 상태: 구현·필수 자동 검증·패키지 생성·사용자의 실제 PZ KO/EN 재관찰 완료

## 1. 문서의 역할

이 문서는 현재 세션에서 수행한 Iris Layer 3 shared composition, Menu/Tooltip 전파,
기술서 획득 정보 보완과 긴 본문 표시 수정을 하나의 구현 흐름으로 설명하는 narrative
walkthrough다. 계획의 초기 목표가 실제 게임 관찰과 사용자 피드백을 거치며 어떻게
구체적인 source correction과 UI 책임 분리로 이어졌는지를 읽을 수 있게 하는 것이
목적이다.

이 문서는 다음 역할을 갖지 않는다.

- 채택 계획, `DECISIONS.md`, generation descriptor, T1/T2 authority 또는 closeout을
  대체하지 않는다.
- canonical validator, 정규 검사기, 새 validation authority, seal, receipt, manifest 또는
  별도 acceptance gate가 아니다.
- 세션 중 사용한 ad hoc 조사나 임시 helper를 Iris의 상설 검사 경로로 승격하지 않는다.
- 사용자 관찰을 모든 아이템·해상도·UI scale·외부 모드 compatibility의 전수 검증으로
  확대하지 않는다.
- freeze, RTC, Publish, release, Workshop 또는 deployment readiness를 선언하지 않는다.

정확한 실행 결과와 package identity의 authoritative summary는
`docs/iris_dvf_shared_composition_usefulness_menu_tooltip_plan_closeout.md`에 있다.

## 2. 시작점과 작업 경계

작업은 `docs/Philosophy.md`의 다음 Iris 원칙을 유지하는 범위에서 진행했다.

1. Iris는 확인된 사실을 이해하기 쉽게 보여주되 추천·효율 평가·우열 판단을 하지 않는다.
2. 근거가 충분하지 않으면 이름, classification 또는 현실의 일반 용도에서 기능을
   추론하지 않는다.
3. Menu와 Alt Tooltip은 같은 사실을 서로 다른 깊이로 표시한다.
4. PZ runtime은 100% Lua이며, 문장 조합·번역·사실 판정은 offline producer에서 끝낸다.

초기 목표는 기존 DVF Body Compiler 안에서 source-bound semantic material과 문장 표현을
분리하는 것이었다. 같은 의미 구조를 공유하는 아이템은 공통 표현을 사용하되 item별
대상·효과·조건·예외를 보존하고, 공유가 부적합하면 explicit body 또는 기존 승인 surface
retention으로 남기는 구조다.

작업 범위는 다음 production chain까지였다.

```text
source-bound fact / profile / item binding
→ adopted KO/EN candidate
→ immutable Layer 3 generation
→ Menu Layer 3 body
→ approved core projection
→ strict T1
→ T2 fixed data + matching Recipe companion
→ installable Iris package
```

Classification과 Tooltip S1, Layer 4 Recipe/Right-click 의미, Alt 활성화와 최대 4 logical-row
계약, 게임 상태 변경, 외부 모드 adapter와 release 작업은 범위 밖으로 유지했다. 계획상
owner approval이 필요한 gate는 사용자의 세션 시작 프롬프트가 사전 승인한 것으로
처리했으며 도구·플랫폼의 별도 권한 요구는 우회하지 않았다.

## 3. Source-bound shared composition 도입

첫 구현은 별도 description engine을 만들지 않고 installed `iris_tooling`의 기존 Body
Compiler 책임을 확장했다. 주요 연결점은 다음과 같다.

- `Iris/tooling/src/iris_tooling/build/compose_layer3_shared.py`가 shared expression과 item별
  binding을 조합한다.
- `compose_profiles_v2.json`은 공통 표현 구조를 선언하고, `dvf_3_3_facts.jsonl`은 exact
  FullType의 source material과 조건·효과 값을 소유한다.
- `candidate_rendered.json`은 검토·채택된 KO/EN public body이며 complete-generation
  producer가 읽는 실제 입력이다.
- generation contract는 새 composition implementation을 identity에 포함한다.
- EN Menu와 Tooltip S2 owner projection은 같은 승인 semantic material을 소비한다.

공통화는 문장이 비슷하다는 이유로 적용하지 않았다. Exact source slot, target, effect,
condition과 item binding이 같은지를 먼저 확인했다. 기존 prose를 파싱해 새 fact를 만들거나,
FullType 이름과 classification으로 기능을 채우는 경로도 추가하지 않았다.

최종 disposition은 다음과 같다.

| 경로 | 수량 | 의미 |
| --- | ---: | --- |
| shared | 193 | 같은 source-bound 의미 구조와 공통 표현을 사용 |
| explicit | 6 | 개선은 필요하지만 shared 구조에 넣지 않고 item별 body 사용 |
| retained | 1,906 | 기존 승인 문구·보호·근거 부족 등의 항목별 이유로 유지 |
| 전체 | 2,105 | exact DVF FullType universe |

Universe 2,105, KO/EN public body 각 2,099, silent 6, S2 core 2,048, empty-core 57과
explicit owner absence 175는 유지했다. Shared 193개와 explicit 6개는 표현·조건 개선이며
coverage 확대로 계상하지 않았다. Single-core identity도 기본 용도나 효과가 반드시 하나라는
뜻으로 사용하지 않았다.

## 4. 첫 current consumer 전파

Shared composition candidate를 채택한 뒤 current consumer를 새 generation에 맞췄다.
Menu는 complete Layer 3 body를 읽고, Tooltip S2는 같은 승인 body의 core만 strict T1/T2
경로로 전달한다. Menu의 acquisition이나 `special_context` 전체를 Tooltip에 복사하거나
runtime에서 4줄로 요약하지 않았다.

이 단계에서 다음 invariant를 유지했다.

- KO/EN public exact set은 각각 2,099개로 동일하다.
- Tooltip S2 core는 2,048개다.
- Tooltip support는 2,280 exact FullType이다.
- Recipe companion은 349 FullTypes / 781 variants다.
- protection, source hold, silent와 owner absence를 새 shared rule로 재판정하지 않는다.

초기 package는 shared/explicit 결과가 generation, EN, T1/T2와 runtime consumer까지
연결되는 것을 확인하는 전달물이었다. 이 시점의 자동 검증은 source identity와 데이터
관계를 확인했지만 실제 PZ에서의 glyph, 화면 폭, scroll hit testing이나 문장 자연스러움을
대신하지 않았다.

## 5. 실제 PZ 관찰에서 드러난 문제

사용자가 첫 전달물을 실제 게임에서 확인하면서 자동 검증이 닫지 못한 presentation과
내용 문제를 구체화했다.

| 관찰 대상 | 사용자 관찰 | 이번 세션의 disposition |
| --- | --- | --- |
| 목공 기술서 | 본문이 잘리고 획득 장소가 없음 | 기술서 source 범위를 다시 확인하고 획득 정보와 장문 표시를 수정 |
| 금속가공 01권 | 목공 기술서와 같은 구조 | 같은 source slot을 쓰는 55개 기술서 전체로 exact 범위를 결속 |
| 빗자루 | 명시된 내용은 있으나 장문이 잘림 | semantic fact를 임의 변경하지 않고 Menu/Wiki 장문 presentation에서 해결 |
| 감자 통조림 | 정상 | 변경하지 않음 |
| `Base.BathTowel` / `Base.DishCloth` | 둘 다 확인 | 기존 결과 유지 |
| 볼링공 가방 | 문장은 자연스러우나 별도 수정안은 미확정 | 근거 없는 의미 변경을 하지 않음 |
| `EngineDoor1` | 후드 부품이라는 설명 확인 | 기존 source-bound 설명 유지 |
| 도끼 | 효율·속도 수치가 없음 | 이번 source/contract에 승인된 수치를 이름으로 추가하지 않음 |
| 발전기 | 주변 기기에 전력을 공급한다는 설명 | 상세 수치를 추론하지 않고 기존 core 유지 |
| EN locale | KO 노출은 없지만 문장이 길고 직역처럼 보임 | runtime 번역을 만들지 않고, 이번 후속은 긴 본문 가독성과 source-bound 기술서 문구에 한정 |
| Recipe 전반 | 대체로 정상, 가짜 Recipe 존재 여부는 확인 불가 | 미확인 사항을 PASS나 결함으로 단정하지 않음 |

이 피드백은 “모든 문장을 짧게 바꾼다”는 요구로 처리하지 않았다. 내용 누락과 화면 표시를
분리했고, source로 닫을 수 있는 기술서 획득 장소는 semantic input을 보완했다. 글이 긴
문제는 Menu 내부 view의 layout/scroll 책임에서 해결했다.

## 6. 기술서 55권의 획득 장소 보완

`Base.BookCarpentry1`과 `Base.BookMetalWelding1`이 같은 구조라는 관찰을 시작점으로 삼되,
이름 유사성만으로 전체 기술서를 묶지 않았다. Build 41의 item literature 선언과
`ProceduralDistributions.lua`, `VehicleDistributions.lua`의 실제 배치를 확인해 active
skill book 55개의 공통 장소 집합을 source slot 하나에 결속했다.

최종 public text는 다음과 같다.

```text
KO: 획득 방법: 학교, 서점, 도서관, 가정집 책장, 책 상자, 우체국과 우편 차량에서 발견된다.
EN: Found in schools, bookstores, libraries, home bookshelves, book crates, post offices, and postal vehicles.
```

기존 기술서의 독서 가능 조건, 적용 레벨, 경험치 배율과 페이지 설명은 유지했다. 획득
장소는 core description과 분리된 Menu detail이므로 다음 항목도 그대로다.

- S2 core count와 승인 core text
- T2 fixed Lua bytes
- Recipe companion bytes
- absence, hold, silent와 protection 판정
- Alt Tooltip의 0~4 logical-row 계약

이 공통 장소 집합은 55개 exact `Base.Book*` binding에만 적용한다. 다른 책, 잡지나 아이템의
획득처를 이름·classification·문장 패턴으로 일반화하는 새 규칙은 만들지 않았다.

## 7. 긴 본문 표시 책임 정리

### 7.1 Browser

`IrisTextLayout`은 PZ engine font measurement와 현재 사용 가능한 폭을 사용해 physical
line을 계산한다. `IrisBrowserDetail`은 줄바꿈된 각 행의 실제 높이를 누적해 기존
`detailContentHeight`에 반영하고, 기존 mouse-wheel scroll 범위가 그 높이를 사용한다.

```text
public body
→ IrisTextLayout.wrapLines(width, font)
→ wrapped ISLabel rows
→ accumulated detailContentHeight
→ existing Browser scroll range
```

Browser에는 별도 두 번째 scrollbar나 장문 전용 surface를 만들지 않았다. 기존 detail
scroll owner가 계산된 본문 높이를 정확히 소비하도록 유지했다.

### 7.2 Wiki

Wiki는 바깥 panel 전체를 본문 높이만큼 키우는 대신 고정 chrome과 scroll content를
분리했다.

```text
outer ISPanel: screen-bounded frame + title + close button
└─ transparent child ISPanel: wrapped section labels + scroll children + scrollbar
```

Child panel은 `setScrollChildren(true)`와 `addScrollBars()`를 사용한다. Tags, Layer 3,
literature, use case, connection과 fields section의 wrapped label을 추가할 때마다 `yOffset`을
누적하고, 마지막에 다음 값으로 scroll range를 결정한다.

```lua
content:setScrollHeight(math.max(content.height, yOffset + 10))
```

따라서 제목과 닫기 버튼은 화면 안에 고정되고 긴 본문만 세로로 이동한다.

### 7.3 Alt Tooltip

사용자는 Iris Tooltip 박스가 글 길이에 맞춰 자체 크기를 조정하고 실제 KO/EN 표시도
잘리지 않는다고 확인했다. 최종 범위에서는 Tooltip에 별도의 강제 줄바꿈·padding 규칙을
추가하지 않고 기존 자동 크기·화면 배치와 4 logical-row 계약을 유지했다. Menu/Wiki의
장문 문제를 이유로 Tooltip semantic surface나 vanilla tooltip 크기를 변경하지 않았다.

## 8. Successor adoption과 exact identity

기술서 전체 장소 범위를 adopted candidate에 반영한 뒤 immutable generation, EN, T1/T2와
package를 순서대로 갱신했다.

| 단계 | exact identity / 결과 |
| --- | --- |
| 전체 장소 candidate 채택 | commit `912b2d32946249071d08ea53a954cfeb53360d54` |
| Layer 3 generation 설치 | commit `276d28134ddea0bab674cae3df639b34eebec99d` |
| 최종 generation | `dvf33-ed92fa5c9ed4a1ed367f5d79365d04e1996e36a05d76a33bd7b8dd2176e7f82f` |
| generation descriptor SHA-256 | `36e3f3f589bd91678b87ea0cd1f33ad27d33fa9a17edfaff6fd0ece8b064eaf8` |
| T1 final subject / tree | `87a44ba7ed0b85e2a96109ffdbd4bbe66a553e8e` / `3fbdcfdce4fe659f9bf41698a43e3f915951f704` |
| T2 final subject / tree | `11039018314598c967337b89ad6b3becf5c6a6c6` / `5ac4605f30f95b5d0205400d1694508b72ecf997` |
| T2 fixed Lua SHA-256 | `f4a2ec3ba1f9b2e830c538374991d1a02c20b65e3bbb2876c3f5f7959018995f` |
| Recipe companion SHA-256 | `b94301ecd933fd86e5e9f254611302ab42b5e5accbe587bb453d7e65e4f628d1` |

T1 final root는 `.tmp/z/v/f`, T2 final root는 `.tmp/z/v/2f`다. 이 경로는 같은
subject/input/producer/execution boundary의 검사 결과를 묶으면서 Windows path 길이를
피하기 위한 짧은 repository-local staging이다. 경로 이름 자체를 새 authority로 사용하지
않는다.

## 9. 필수 자동 검증과 실행 중 정정

계획과 Reviewer가 요구한 최소 검증은 구현과 adoption이 끝난 뒤 모아서 실행했다. 새
독립 Gate나 validation-of-validation을 추가하지 않았다.

| 실행 | 최종 결과 |
| --- | --- |
| strict T1 candidate | correction 0, handoff 2,280, progression OPEN |
| T1 canonical full Run A/B | 각각 exit 0, `213 passed, 118 subtests passed` |
| T1 comparator / finalizer | 각각 exit 0, final complete |
| T2 독립 A/B / finalizer | 각각 exit 0, Lua/manifest byte-identical, final complete |
| focused 3파일 | exit 0, `18 passed` |
| installed `inspect current` | exit 0 |
| Lua syntax | exit 0, 264 files |
| 최종 T2 canonical full | exit 0, `213 passed, 118 subtests passed` |
| package builder / package consumer | 각각 exit 0 |

최초 canonical 진입 일부는 PASS 전에 fail-closed로 중단됐다. 원인은 기존 environment의
tooling source mismatch, receipt 뒤 생성된 `__pycache__`, Windows work path 267 > 259였다.
Source나 검증 coverage를 줄이지 않고 exact wheel environment를 기존 writer로 다시
결속하고, receipt 이후 Python을 `-B -s`로 실행했으며, 짧은 work root를 사용했다. 이 준비
실패는 PASS나 필수 실행 횟수로 세지 않았다.

`.tmp/body`와 ad hoc helper는 이 작업에서만 사용한 보조 수단이다. 이를 canonical
validator, 정규 검사기, 새 validation authority나 후속 정책 입력으로 승격하지 않았다.

## 10. 설치 package

최종 전달물은 current generation 하나와 그에 맞는 KO/EN Menu payload, T2 fixed data와
Recipe companion을 포함한다.

| 산출물 | 값 |
| --- | --- |
| 설치용 폴더 | `C:/Users/MW/Downloads/coding/PZ/.tmp/z/p/Iris` |
| ZIP | `C:/Users/MW/Downloads/coding/PZ/.tmp/z/p/Iris.zip` |
| ZIP 크기 | 694,217 bytes |
| ZIP SHA-256 | `5e0755067c0deac21412b935b1a0fab475d31331442bda30f42db1d3c3a5655d` |
| package manifest | 141 files, SHA-256 `3188c6ee5c88277f888a842440f5c712e822a120874efc07a72b8bd45b04a27c` |

Predecessor generation이나 stale fixed/companion을 package fallback으로 섞지 않았다.
작업 과정에서 사용자의 실제 Project Zomboid 설치 폴더에 직접 쓰지도 않았다.

## 11. 실제 PZ 재관찰과 claim ceiling

사용자는 최종 package를 실제 PZ에서 다시 확인해 KO와 EN 모두 글이 잘리지 않고 잘
보인다고 보고했다. 이 관찰로 이번 후속의 긴 공개 본문 표시와 두 locale의 화면 가독성
범위를 수용했다. 기술서에는 전체 획득 장소가 표시되고, Tooltip은 기존 자동 크기 경로로
정상 표시되는 상태다.

다음 항목은 이 관찰로 인증하지 않았다.

- 2,105개 전체 문장의 의미·자연스러움 전수 승인
- 모든 해상도와 UI scale의 mouse wheel, scrollbar, glyph fit
- 가짜 Recipe의 존재 여부
- Build 42, 멀티플레이, 장시간 성능과 외부 모드 조합
- freeze, RTC, Publish, release, Workshop와 deployment readiness

사용자가 앞서 확인한 감자 통조림, 수건/행주, 차량 후드 부품, 발전기, 도끼, 빗자루와
Recipe 관찰은 item별 피드백으로 보존한다. 그 관찰에서 직접 확인하지 않은 수치·효과나
기능을 새 사실로 역추론하지 않는다.

## 12. Canonical 문서 동기화와 현재 readpoint

실제 PZ 재관찰 뒤 `DECISIONS.md`, `ROADMAP.md`, `ARCHITECTURE.md`를 commit
`1c2bcc8493061f54019d7794cdfd6874ea1f510d`에서 동기화했다.

- `DECISIONS.md`는 기술서 55권의 source-bound 획득 장소, Tooltip S2 비변경,
  Browser/Wiki 장문 표시 책임과 관찰 한계를 current decision에 반영한다.
- `ROADMAP.md`는 shared composition과 기술서·장문 표시 후속을 Done으로 기록한다.
- `ARCHITECTURE.md`는 최종 generation, T1/T2/package 경로, `IrisTextLayout`, Browser
  scroll과 Wiki child scroll 구조를 current runtime architecture로 설명한다.

구현 결과를 확인할 때는 다음 순서로 읽는다.

```text
Philosophy.md
→ DECISIONS.md / ARCHITECTURE.md / ROADMAP.md
→ iris_dvf_shared_composition_usefulness_menu_tooltip_plan.md
→ iris_dvf_shared_composition_usefulness_menu_tooltip_plan_closeout.md
→ 이 Walkthrough
```

계획은 요구사항과 success condition, closeout은 exact 실행 결과와 package identity,
Walkthrough는 구현과 사용자 피드백이 이어진 과정을 설명한다. 서로의 역할을 대체하지
않는다.
