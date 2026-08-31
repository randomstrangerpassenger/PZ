# 게임·모드의 설명 및 정보 제공 시스템 추가 조사

조사일: 2026-08-31

이 문서는 추가 사례와 근거를 모은 조사 기록이다. DVF 적용안, 권장 구조, 우선순위, 구현 계획, 테스트 또는 Gate를 제안하지 않는다. 아이템 설명과 직접 관련된 사례뿐 아니라 능력 설명, 도감, 제작 관계 탐색, 번역 기반 시설, 외부 데이터·계산 도구를 포함한다. 따라서 아래 40개 항목을 모두 ‘아이템 설명 자동 생성기’로 해석하면 안 된다.

이전에 다룬 Patchouli, Factorio의 Factoriopedia 및 LocalisedString, Stardew Valley의 Lookup Anything, JEI, Cataclysm: DDA, The Binding of Isaac의 External Item Descriptions, Slay the Spire의 BaseMod, Guild Wars 2의 skill facts는 추가 사례 수에 포함하지 않았다. 같은 프로젝트의 여러 파일은 하나로 묶었고, Create의 Ponder와 이를 작성하는 PonderJS도 한 항목으로 묶었다.

## 조사 범위와 근거 구분

확인한 사항은 설명의 원천, 공통 문구와 개별 값의 연결, 조건·상태별 표시, 번역, 예외 처리, 짧은 정보와 상세 정보의 관계이다. 검색 결과는 후보 탐색에 사용했고, 기술적 설명은 프로젝트가 공개한 문서·소스·작성자 자료를 근거로 기록했다.

| 표시 | 확인 수준 | 해석 범위 |
|---|---|---|
| S | 관련 소스 또는 실제 정의 파일을 읽음 | 명시한 함수·데이터 경로의 동작을 확인했다. 전체 실행 경로를 검증했다는 뜻은 아니다. |
| D | 공식 API, 프로젝트 개발 문서, 작성자 가이드·변경 기록을 읽음 | 문서에 명시된 기능을 확인했다. 현재 배포판 전체와의 일치는 별도 확인이 필요하다. |
| I | 작성자의 소개·README에 명시된 기능을 확인 | 기능의 존재에 관한 자료이며 내부 구현의 증거로 사용하지 않는다. |
| 보류 | 원문 접근 실패 또는 관련 구현 근거 부족 | 확인된 구조로 분류하지 않으며 40개 항목에 포함하지 않는다. |

게임을 실행하거나 모드를 설치해 화면을 재현하지 않았다. `master`, `main`, `HEAD`, `dev` 링크는 이동하는 브랜치다. 버전이 지정된 자료와 과거 개발 기록은 각 항목에 표시했다. 소스가 공개되어 있다는 사실과 자유롭게 재사용할 수 있다는 사실도 구분한다. 원문 코드의 재배포나 라이선스 검토는 이번 조사에 포함하지 않았다.

## 전체 색인

| 번호 | 게임·프로젝트 | 조사한 방식 | 근거 |
|---|---|---|---|
| 01 | Unciv | 읽을 수 있는 효과 문법, 형식화된 매개변수, 조건 | D |
| 02 | Freeciv | 작성한 도움말과 규칙 기반 목록·표의 혼합 | S |
| 03 | The Battle for Wesnoth | 능력 설명, 비활성 설명, 도감용 주석 분리 | D |
| 04 | OpenRA | 조건과 관찰자 관계에 따른 설명 표시 | D |
| 05 | Angband | 확인된 속성의 설명 블록과 표시 모드 | S |
| 06 | Dungeon Crawl Stone Soup | 속성 목록에 따른 축약 표기, 미확인 정보 제한 | S |
| 07 | Shattered Pixel Dungeon | 아이템 계열의 공통 처리와 식별 상태별 설명 | S |
| 08 | Mindustry | 목적 설명·상세 설명·통계의 별도 필드 | S |
| 09 | Veloren | 모듈형 아이템을 완성된 번역 메시지에 매핑 | D·과거 개발 기록 |
| 10 | Endless Sky | 작성한 설명 문단의 조건부 표시 | D |
| 11 | Tales of Maj'Eyal / T-Engine | 요구 조건 및 전체 설명 생성 API | D·구버전 |
| 12 | 0 A.D. | 실제 능력 필드별 툴팁 함수와 번역 형식 | S |
| 13 | OpenMW | 주문 효과 레코드를 구조화된 표시 데이터로 전달 | S |
| 14 | Widelands | 작성한 용도와 생산·소비 관계로 구성한 도감 | S |
| 15 | FreeOrion | 효과 그룹의 설명 키와 수치 출처 라벨 | D·S |
| 16 | OpenTTD / NewGRF | 구매 화면 추가 설명 콜백과 매개변수 | D |
| 17 | Divinity: Original Sin 2 | 설명 자리표시자와 게임 통계의 연결 | D |
| 18 | Path of Exile / RePoE | 추출한 통계 ID·값을 문구 규칙에 대응 | S |
| 19 | Warframe / WFCD warframe-items | 여러 출처를 수집·가공한 아이템 데이터 배포 | S·D |
| 20 | Destiny / Bungie Manifest | 언어별 정적 정의와 실시간 데이터의 ID 연결 | D |
| 21 | Don't Starve Together / Insight | 컴포넌트별 설명기, 플레이어 상태, 대체 설명 | S |
| 22 | Create / Ponder·PonderJS | 아이템과 연결된 수동 작성 시연 장면 | D |
| 23 | Minecraft / The One Probe | 정보 제공자 API와 일반·확장·디버그 모드 | S |
| 24 | Terraria / tModLoader | 공통 번역 템플릿, 상속, 동작 값과 설명 값 공유 | D |
| 25 | Tinkers' Construct | 효과 단위 공통 설명과 도구·레벨별 재정의 | S |
| 26 | Enchantment Descriptions | 효과 ID 기반 번역 키와 리소스 팩 수정 | D |
| 27 | Jade | 서버 상태 제공과 클라이언트 툴팁 작성 분리 | D·S |
| 28 | Luanti | 짧은 설명 필드와 매개변수형 클라이언트 번역 | D |
| 29 | Item Descriptions / Cassian | 개별 설명 우선, 태그 기반 공통 설명, 집필 지침 | S·D |
| 30 | Modded Minecraft Wiki | 게임 데이터와 문서 결합, 획득·사용 레시피 표시 | D |
| 31 | Risk of Rain 2 / Moffein ItemStats | 기존 상세 설명을 툴팁·획득 알림에 재사용 | S |
| 32 | Risk of Rain 2 / ontrigger ItemStatsMod | 중첩 효과 설명과 외부 등록 API | D |
| 33 | World of Warcraft / All The Things | 수집 정보 데이터베이스와 툴팁·별도 창 | I |
| 34 | FTB Quests | 게임 내 집필과 언어별 본문 저장 | D |
| 35 | Dwarf Fortress / DFHack | 기본 아이템 이름에 인스턴스 상태를 주석으로 추가 | S |
| 36 | Stardew Valley / Content Patcher | 조건별 번역 키, 명시적 인수, 대체 키 순서 | D |
| 37 | EMI | 레시피 관계·트리, 기본 경로, 트리 제외 조건 | D |
| 38 | Vintage Story | 공통 아이템 설명 함수와 실제 속성·상태 조회 | S·D |
| 39 | Pokémon Showdown | 정적 기술 설명과 전투 상황별 계산 정보 결합 | S |
| 40 | Path of Building Community | 외부 계산을 통한 장비 변경 효과와 미지원 표시 | S |

## 사례 기록

### 01. Unciv — 설명처럼 읽히는 효과 문법

객체에 여러 `Uniques`를 부여하고, 정해진 문장 형식의 매개변수에 수치·자원·대상 등을 넣는다. 매개변수에는 형식이 있으며 조건을 덧붙이는 문법도 있다. 개발 문서는 폐기된 형식을 새 형식으로 바꾸는 기능을 설명한다. 이는 자유롭게 쓴 문장을 게임이 이해한다는 의미가 아니라, 게임이 인식하는 제한된 효과 문법이다. [개발자 문서: Uniques](https://yairm210.github.io/Unciv/Developers/Uniques/)

복잡한 필터는 표시 문구를 읽기 어렵게 만들 수 있다. 매개변수 문서는 이러한 경우 고유 효과를 숨기고 `Comment []`로 더 읽기 좋은 설명을 제공하는 방법도 안내한다. 실행 가능한 형식만으로 모든 설명의 가독성을 해결한다고 주장하지 않는다. [Unique parameters](https://yairm210.github.io/Unciv/Modders/Unique-parameters/)

### 02. Freeciv — 편집한 설명과 규칙 데이터로 만든 도움말

`helpdata.txt`는 작성자가 넣는 문단 배열 외에 유닛·기술·지형 등 규칙 항목으로 목록을 만드는 `generate`, 생성된 표를 삽입하는 `$` 항목을 지원한다. 문단을 나눈 이유에는 번역 편의도 명시되어 있다. 텍스트를 작성하는 부분과 게임 규칙에 맞춰 생성되는 부분이 함께 존재한다. [도움말 정의 파일](https://github.com/freeciv/freeciv/blob/main/data/helpdata.txt)

같은 파일은 규칙 변경에 도움말이 적응하려 하지만 모든 변경을 포괄하지는 못한다고 설명한다. 이 사례를 ‘규칙을 바꾸면 모든 설명도 자동으로 정확해진다’는 근거로 사용할 수는 없다.

### 03. The Battle for Wesnoth — 능력의 표시 문구와 도움말 문구

능력 정의에는 이름과 설명뿐 아니라 비활성 상태의 이름·설명, 유닛 도움말에 들어가는 `special_note` 등이 있다. 특정 표시 상황에 사용할 문구를 명시적으로 구분한다. 필드별 도입 버전은 문서의 버전 표시에 따른다. [AbilitiesWML](https://wiki.wesnoth.org/AbilitiesWML)

같은 문서는 실제 효과 없이 능력처럼 표시하는 `dummy`도 정의한다. 따라서 능력 설명 필드가 존재한다는 사실만으로 그 문구의 효과가 실행된다고 보장되지는 않는다. 이번에는 이러한 정의 구조를 확인했으며 모든 기본 능력의 구현과 설명을 대조하지는 않았다.

### 04. OpenRA — 조건과 관계에 따른 설명 표시

릴리스용 trait 문서에서 `TooltipDescription`은 `Description`, `RequiresCondition`, `ValidRelationships`를 갖는다. 일반 `Tooltip` 역시 이름과 소유자 표시 등 별도 역할을 가진다. 설명의 내용뿐 아니라 활성 조건과 관찰자 관계를 표시 설정으로 다룬다. [릴리스 trait 문서](https://docs.openra.net/en/release/traits/#tooltipdescription)

확인한 것은 표시 trait의 계약이다. 전투·생산 등의 행동 trait를 모두 읽어 목적 문장을 자동 작성한다는 구현은 이 문서에서 확인되지 않았다.

### 05. Angband — 알려진 속성만 설명 블록으로 조립

`object_info_out`은 확인된 속성과 원소 정보를 준비한 후 저주, 능력치, 저항, 빛, 발동 효과 등 해당하는 설명을 순서대로 붙인다. 아이템 종류를 모르면 제한된 안내를 반환하는 경로가 있다. `OINFO_TERSE`, `OINFO_SUBJ` 등 모드에 따른 분기도 존재한다. [obj-info.c](https://github.com/angband/angband/blob/master/src/obj-info.c)

조사한 것은 이 함수와 주변 표시 분기다. 일부 정보는 플레이어에게 알려진 범위를 기준으로 하며, 모든 숨은 속성을 처음부터 표시하는 구조가 아니다. 게임 실행으로 각 조합을 확인하지는 않았다.

### 06. Dungeon Crawl Stone Soup — 속성에서 축약 표기를 생성

`_randart_propnames`는 식별 여부를 확인하고, 유물 속성·브랜드 등의 데이터를 일정한 순서로 축약 표기에 반영한다. 소스에서 미식별 정보를 제한하는 조건을 확인했다. [describe.cc](https://github.com/crawl/crawl/blob/master/crawl-ref/source/describe.cc)

공식 저장소의 매뉴얼도 유물의 속성을 축약해 표기하고 조사 화면에서 설명하는 방식을 안내한다. 이번에 직접 추적한 범위는 주로 속성 축약과 식별 조건이며, 모든 장문 설명의 생성 경로는 아니다. [게임 매뉴얼](https://github.com/crawl/crawl/blob/master/crawl-ref/docs/crawl_manual.rst)

### 07. Shattered Pixel Dungeon — 계열 공통 처리와 식별 상태

`Potion` 클래스는 식별 여부에 따라 이름과 설명을 선택한다. 알려진 물약은 정상 설명을 사용하고, 모르는 물약은 공통 미확인 설명을 사용한다. 개별 아이템 문구는 메시지 리소스에 존재한다. 계열 클래스가 상태별 표시를 맡고 실제 문장은 번역 데이터에 두는 사례다. [Potion.java](https://github.com/00-Evan/shattered-pixel-dungeon/blob/master/core/src/main/java/com/shatteredpixel/shatteredpixeldungeon/items/potions/Potion.java), [아이템 메시지](https://github.com/00-Evan/shattered-pixel-dungeon/blob/master/core/src/main/assets/messages/items/items.properties)

물약 경로를 확인한 결과다. 모든 장비·효과의 설명이 동일한 방식으로 생성된다고 확장해서 판단하지 않았다.

### 08. Mindustry — 목적·상세·통계를 별도로 보관

`UnlockableContent`는 `description`, `details`, `stats`를 별도로 가진다. 잠금 상태에서 상세 정보를 숨기는 설정과 연구 화면의 짧은 설명 관련 설정도 존재한다. `ContentInfoDialog`는 목적 설명을 표시하고 통계를 범주별로 구성한다. [콘텐츠 정의](https://github.com/Anuken/Mindustry/blob/master/core/src/mindustry/ctype/UnlockableContent.java), [정보 창](https://github.com/Anuken/Mindustry/blob/master/core/src/mindustry/ui/dialogs/ContentInfoDialog.java)

짧은 문장과 깊은 정보를 담을 자리가 분리되어 있다는 점을 확인했다. `description`이 통계로부터 자동 생성된다는 뜻은 아니며, 모든 콘텐츠가 상세 필드를 채웠는지는 조사하지 않았다.

### 09. Veloren — 모듈형 이름도 완성된 메시지로 매핑

2024년 1월 개발 기록은 `ItemKey`를 번역 메시지 식별자에 연결하는 `ItemL10n`을 설명한다. 모듈형 무기에서도 문자열 조각을 결합하기보다 메시지 매핑을 사용하며, 일부 조합은 같은 식별자를 공유하도록 정리했다. [개발 기록 225](https://veloren.net/blog/devblog-225/)

이는 당시 변경 사항에 관한 근거다. 같은 글의 문법적 성별 관련 논의까지 모두 구현된 기능으로 취급하지 않았고, 현재 모든 아이템의 번역 경로를 추적하지도 않았다. 특히 이 사례의 직접 대상은 아이템 명명·번역이며 용도 문장 생성 전체가 아니다.

### 10. Endless Sky — 설명 문단별 표시 조건

장비인 outfit의 `description`을 여러 번 정의해 문단을 만들 수 있다. 문서는 0.10.13부터 `to display` 하위 조건으로 설명 일부의 표시 여부를 결정할 수 있다고 명시한다. 조건의 참·거짓과 작성한 문장을 연결하는 방식이다. [CreatingOutfits](https://github.com/endless-sky/endless-sky/wiki/CreatingOutfits)

이 기능은 장비 수치로 용도를 자동 추론하는 기능이 아니다. 어떤 설명을 쓸지와 어떤 조건에서 보여줄지는 콘텐츠 작성자가 정한다.

### 11. Tales of Maj'Eyal / T-Engine — 전체 설명을 만드는 API

공개 API에는 요구 조건을 여러 줄 설명으로 만드는 `getTalentReqDesc`, 전체 능력 설명을 제공하는 `getTalentFullDescription`이 있다. 후자는 전력 사용 등의 내용을 추가하도록 재정의할 수 있다는 설명이 붙는다. [ActorTalents API 1.4.8](https://te4.org/docs/t-engine4/1.4.8/classes/engine.generator.interface.ActorTalents.html)

확인 자료는 1.4.8 문서다. 현재 모든 능력이 동작 계산 함수와 설명 계산 함수를 공유한다는 주장은 이 자료만으로 하지 않는다. 아이템 계열 템플릿보다는 능력 설명 확장 API에 관한 사례다.

### 12. 0 A.D. — 능력별 함수가 만드는 툴팁

`getAttackTooltip`은 공격 능력이 없으면 빈 결과를 반환하고, 공격 종류와 효과 정보를 읽어 표시한다. `attackEffectsDetails`는 피해·점령·상태 효과 등 해당하는 항목을 조합하며, 빈 항목을 걸러낸다. 공격 표시에는 이름 있는 번역 자리표시자도 사용한다. [tooltips.js](https://github.com/0ad/0ad/blob/master/binaries/data/mods/public/gui/common/tooltips.js)

모든 능력을 무조건 나열하지는 않는다. 조사한 공격 경로에는 `Slaughter`를 건너뛰는 선택도 있다. 따라서 표시 문구는 실제 데이터에 연결되지만, 어떤 사실을 보여줄지는 별도 표시 정책에 따른다.

### 13. OpenMW — 효과 레코드를 표시용 구조로 전달

주문 툴팁 경로는 게임 저장소에서 주문을 찾고, 효과 ID·능력치 대상·지속 시간·최소/최대 크기·범위·영역 등을 효과 표시 데이터로 옮긴다. 이후 효과 목록 위젯으로 전달한다. [tooltips.cpp](https://github.com/OpenMW/openmw/blob/master/apps/openmw/mwgui/tooltips.cpp)

이 경로는 이미 정의된 주문 효과를 읽는다. 이번에는 그 연결을 확인했으며, 각 효과를 최종 자연어 문장으로 바꾸는 모든 위젯·번역 경로까지 추적하지는 않았다. OpenMW 구현에 관한 근거이지 원작의 내부 구현을 확인한 것은 아니다.

### 14. Widelands — 작성한 용도와 생성한 생산·소비 관계

물품 도감의 일반 설명은 `helptexts["purpose"]`를 사용한다. 이어 물품의 생산 건물과 소비 건물·작업자 관계를 조회해 목록과 링크를 만든다. 도감의 반환 본문은 일반 설명, 생산자 설명, 소비자 설명을 합친다. [ware_help.lua](https://github.com/widelands/widelands/blob/master/data/tribes/scripting/help/ware_help.lua)

용도 문장 자체는 작성된 도움말이고, 상세 관계는 게임 정의를 조회한 결과다. 문장과 관계 목록이 서로 다른 작성 경로를 갖는 점을 확인했으며, 해당 물품의 모든 비생산 행동까지 도감에 포함된다고 보지는 않는다.

### 15. FreeOrion — 효과 그룹 설명과 수치의 출처 라벨

FOCS 문서는 `EffectsGroup`의 실행 대상·활성 조건과 별도로 `DESCRIPTION`, `ACCOUNTINGLABEL`을 설명한다. 설명 키는 번역 문자열을 참조하고, 출처 라벨은 수치 합계에서 효과 그룹의 기여를 표시하는 데 사용된다. 문서는 설명 추가의 적용 대상을 작성 당시 specials와 species로 제한해 설명한다. [FOCS Scripting Details](https://freeorion.org/index.php/FOCS_Scripting_Details)

소스에서도 효과 그룹에 설명과 출처 라벨을 저장하는 구성을 확인했다. 다만 현재 모든 효과 트리를 자동으로 장문으로 바꾸는 함수는 이번 조사에서 확인하지 못했다. [Effects.cpp](https://github.com/freeorion/freeorion/blob/master/universe/Effects.cpp)

### 16. OpenTTD / NewGRF — 구매 화면의 추가 설명 콜백

콜백 23은 차량 구매 화면의 기본 정보 아래에 텍스트를 덧붙인다. 문서에는 반환할 텍스트 ID, 텍스트를 표시하지 않는 반환값, 매개변수용 텍스트 스택, 줄바꿈 동작이 설명되어 있다. 레지스터 및 반환값의 세부 범위는 버전에 따라 다르다. [NewGRF 콜백 명세](https://newgrf-specs.tt-wiki.net/wiki/Callbacks#Additional_text_in_purchase_screen_(23))

기본 통계 표시 외에 제작자가 추가 정보를 제공하는 확장 지점이다. 이 콜백이 차량의 실제 기능을 해석해 문장을 자동 작성한다는 의미는 아니다.

### 17. Divinity: Original Sin 2 — 설명 인수와 게임 통계

공식 스킬 작성 문서는 `Description`의 `[1]`, `[2]` 같은 자리를 `StatsDescriptionParams`의 순서와 연결한다. 예시는 피해와 사거리 값을 설명에 넣는다. `StatsDescription`은 주 설명 아래에 표시할 추가 설명을 별도로 정의한다. [Larian: Skill creation](https://docs.larian.game/Skill_creation)

효과 문장을 작성하되 그 일부를 통계 매개변수와 연결하는 방식이다. 문장 전체가 스킬 코드로부터 생성되는 것은 아니다. 이 문서를 Baldur's Gate 3의 현행 툴킷 명세로 대신 사용하지 않았다.

### 18. Path of Exile / RePoE — 통계 값과 표시 규칙의 추출

RePoE는 게임 GGPK 데이터를 PyPoE로 처리해 JSON으로 제공하는 프로젝트다. `stat_translations`는 통계 ID와 값에서 게임 표시 문구로 가는 정보를 담는다. 실제 데이터에서 조건 범위, 수치 형식, 값 처리기, 문구가 함께 저장된 구조를 확인했다. [RePoE 프로젝트](https://github.com/brather1ng/RePoE), [실제 monster 번역 규칙](https://github.com/brather1ng/RePoE/blob/master/RePoE/data/stat_translations/monster.json)

이 사례는 자유로운 용도 추론이 아니라 게임이 사용하는 수치·표현 규칙을 추출한 것이다. 조사한 저장소 데이터가 현재 게임 버전의 모든 통계를 빠짐없이 반영한다고 검증하지 않았다. 게임이 직접 만든 공식 API와도 구분한다.

### 19. Warframe / WFCD warframe-items — 출처가 여럿인 통합 데이터

README는 아이템 데이터를 자동 수집·컴파일해 JSON으로 제공하는 구조와 번역 데이터의 중앙 보관 또는 아이템별 첨부 옵션을 설명한다. 빌드 코드에는 데이터 수집과 가공 단계가 분리되어 있다. [프로젝트 문서](https://github.com/WFCD/warframe-items)

실제 수집 코드에는 게임 콘텐츠 서버 외에 위키에서 정보를 읽는 scraper들도 있다. 그러므로 이 패키지의 모든 필드가 게임 파일에서 직접 나온다고 말할 수 없다. 이번에는 수집 구조를 확인했으며 개별 필드의 출처와 충돌 해결 규칙을 전수 추적하지 않았다. [scraper.ts](https://github.com/WFCD/warframe-items/blob/master/build/scraper.ts)

### 20. Destiny / Bungie Manifest — 정적 정의와 인스턴스 데이터 연결

Bungie의 문서는 언어별 JSON 또는 SQLite 정적 정의를 배포하고, 게임 데이터에 있는 hash로 사람이 읽는 문자열·아이콘 등의 정의를 찾는 방법을 설명한다. 아이템 정의와 실제 소지 상태 등을 ID로 연결할 수 있는 기반이다. [Bungie Manifest 문서](https://github.com/Bungie-net/api/wiki/Obtaining-Destiny-Definitions-%22The-Manifest%22)

확인한 것은 공식 정의 데이터의 전달·조회 계약이다. 짧은 설명과 상세 설명이 어떤 편집 과정으로 작성되는지, 게임의 모든 효과를 설명 문자열에서 복원할 수 있는지는 확인하지 않았다. 설명 생성법보다 소비자가 원천 데이터를 공유하는 방식에 관한 사례다.

### 21. Don't Starve Together / Insight — 컴포넌트별 설명과 문맥

`edible` 설명기는 섭취 가능 여부와 먹는 주체를 확인하고, 음식의 허기·정신력·체력 값을 조회한다. 음식 기억, 흡수율 등 조건을 반영하는 경로와 짧은/긴 형식이 있다. `weapon` 설명기에는 설명 우선순위, 대체 설명, 캐릭터·아이템별 예외 처리가 보인다. [edible.lua](https://github.com/penguin0616/Insight/blob/master/scripts/descriptors/edible.lua), [weapon.lua](https://github.com/penguin0616/Insight/blob/master/scripts/descriptors/weapon.lua)

기존 게임 함수를 부르는 부분과 별도 계산·예외 처리 부분이 함께 있다. 따라서 ‘항상 같은 동작 함수의 결과를 그대로 보여준다’고 일반화할 수 없다. 조사한 공개 저장소의 라이선스는 별도 조건이 있는 shared source이므로 자유 재사용 코드로 취급하지 않는다. [프로젝트·라이선스 안내](https://github.com/penguin0616/Insight)

### 22. Create / Ponder·PonderJS — 설명을 시연 장면으로 작성

Ponder는 게임 안에서 기계 작동을 설명하는 상호작용형 가이드를 만드는 라이브러리다. PonderJS 작성 문서는 아이템 ID에 장면을 연결하고, 구조물과 장면 동작을 작성하는 방법을 제공한다. [Ponder](https://github.com/Creators-of-Create/Ponder), [PonderJS 작성 가이드](https://github.com/AlmostReliable/ponderjs/wiki/1.-Getting-Started)

텍스트를 더 길게 만드는 방식 외에 공간적 작동 과정을 보여주는 사례다. 장면은 작성자가 구성하며, 임의의 아이템 행동을 분석해서 자동 시연을 생성한다는 기능은 확인되지 않았다. 라이브러리와 작성 도구를 별개 사례로 중복 계산하지 않았다.

### 23. The One Probe — 정보 제공자가 표시 모드를 받음

`IProbeInfoProvider`는 플레이어·월드·대상 등의 문맥을 받아 정보를 추가하는 API다. `ProbeMode`에는 일반, 확장, 디버그 모드가 있으며, 확장 모드는 웅크리기, 디버그는 크리에이티브 관련 용도로 설명된다. [정보 제공자 API, 1.20 브랜치](https://github.com/McJtyMods/TheOneProbe/blob/1.20/src/main/java/mcjty/theoneprobe/api/IProbeInfoProvider.java), [ProbeMode](https://github.com/McJtyMods/TheOneProbe/blob/1.20/src/main/java/mcjty/theoneprobe/api/ProbeMode.java)

정보를 얼마나 표시할지 제공자에게 전달하는 구조다. 각 모드에서 같은 정보가 반드시 확장되도록 강제하는지, 외부 모드의 문구가 정확한지는 이 인터페이스만으로 보장되지 않는다.

### 24. tModLoader — 공통 문장과 실제 값의 연결을 문서화

공식 번역 가이드는 같은 툴팁을 여러 아이템이 공유하도록 번역 키를 등록하거나 공통 클래스로 상속하는 예시를 제공한다. 아이템 동작에 쓰는 `MaxMinionIncrease` 값을 `WithFormatArgs`의 설명 인수로도 사용하는 예시가 있어 수치 변경 시 문구의 숫자도 함께 바뀌도록 한다. [tModLoader Localization](https://github.com/tModLoader/tModLoader/wiki/Localization)

문서는 고정 매개변수와 상황에 따라 변하는 매개변수도 구분해 후자는 `ModifyTooltips` 등에서 처리하도록 설명한다. 문서화된 구현 방법을 확인한 것이며, 모든 Terraria 모드가 이를 따른다는 조사 결과는 아니다.

### 25. Tinkers' Construct — 효과 단위 공통 설명과 재정의

1.20.1 브랜치의 `Modifier`는 효과 번역 키에 `.flavor`, `.description`을 붙여 기본 설명 목록을 만들고 보관한다. 레벨을 받는 설명 함수와 실제 도구·효과 항목을 받는 설명 함수가 있어 필요한 구현이 재정의할 수 있다. 별도로 일반 툴팁과 고급 표시 상황을 구분하는 `shouldDisplay`가 있다. [Modifier.java](https://github.com/SlimeKnights/TinkersConstruct/blob/1.20.1/src/main/java/slimeknights/tconstruct/library/modifiers/Modifier.java)

같은 효과가 붙은 도구들이 공통 설명을 참조할 수 있는 구조다. 효과 동작 코드를 자동으로 요약하는 생성기는 아니며, 레벨별 세부 내용도 재정의하지 않으면 공통 설명으로 돌아간다.

### 26. Enchantment Descriptions — 효과 ID에 대응하는 편집 가능한 문구

1.20.1용 작성자 문서는 인챈트 ID에서 `enchantment.{namespace}.{path}.desc` 번역 키를 찾는 규칙을 설명한다. 모드나 리소스 팩에서 코드를 수정하지 않고 설명을 추가·교체할 수 있다. 기존 설명을 교체할 때 언어 파일 namespace와 로드 순서를 주의하라는 안내도 있다. [Enchantment Descriptions 문서](https://docs.darkhax.net/1.20.1/enchantment-descriptions/)

설명을 책이나 인챈트 화면에만 표시하거나 키를 눌렀을 때 표시하는 설정도 문서화되어 있다. 실제 효과의 의미는 작성한 문구가 담당하며, 설명 키 규칙 자체가 문장의 사실성을 검사하지는 않는다.

### 27. Jade — 서버 사실과 클라이언트 표시의 분리

1.19 플러그인 가이드는 화로 상태를 서버 데이터 제공자가 읽어 전달하고, 클라이언트 컴포넌트 제공자가 이를 툴팁으로 구성하는 예시를 설명한다. 정보 수집과 표시를 분리하는 확장 API다. [플러그인 작성 가이드](https://jademc.readthedocs.io/en/1.x/plugins19/getting-started/)

현재 저장소의 `FurnaceProvider`도 확인했으나 네트워크 직렬화 API 등은 구버전 문서와 다르다. 이 둘을 같은 버전의 복사 가능한 코드로 취급하지 않았다. 어떤 정보를 전달하는지는 제공자 구현에 달려 있다. [FurnaceProvider.java](https://github.com/Snownee/Jade/blob/HEAD/src/main/java/snownee/jade/addon/vanilla/FurnaceProvider.java)

### 28. Luanti — 아이템 설명 필드와 클라이언트 번역

아이템 정의에는 `description`과 `short_description`이 구분되어 있다. 번역 API는 서버에서 번역 가능한 메시지를 만들고 클라이언트의 언어로 표시할 수 있도록 하며, 인수와 복수형을 다룬다. [정의 테이블](https://api.luanti.org/definition-tables/), [번역 API](https://api.luanti.org/translations/)

이는 텍스트 보관·표시 기반 시설이다. 설명용 인수만 준비하면 한국어 문법이나 아이템 용도가 자동으로 결정된다는 의미는 아니다. 원문 인수의 순서·반복 등에 문법 제약도 있으므로 임의의 문자열 조립과 동일하지 않다.

### 29. Item Descriptions / Cassian — 개별 문구와 공통 태그의 결합

`findLoreKey`는 변형·사용자 지정 정보와 개별 아이템 설명 키를 확인하고, 해당 설명을 찾지 못하면 태그 기반 공통 설명을 조회한다. 키 입력이나 항상 표시 설정에 따른 표시 경로도 있다. [설명 선택 코드](https://github.com/cassiancc/Item-Descriptions/blob/HEAD/src/main/java/cc/cassian/item_descriptions/client/descriptions/ItemDescriptions.java)

작성 지침은 짧은 소개, 첫 독자를 고려한 문장, 핵심 용도에 필요하지 않은 레시피 뷰어·WAILA 정보의 중복 회피를 다룬다. 예외적으로 더 긴 설명도 허용한다. 이는 프로젝트의 편집 지침이지 게임 데이터에서 자동 도출되는 규칙은 아니다. [Writing Descriptions](https://github.com/cassiancc/Item-Descriptions/blob/HEAD/docs/Writing-Descriptions.mdx)

### 30. Modded Minecraft Wiki — 데이터와 문서의 역할 구분

문서용 게임 데이터에는 이름 번역, 태그, 레시피 등이 들어가며, 문서 페이지는 아이템 ID를 기준으로 이러한 데이터를 이용한다. `PrefabObtaining`과 `PrefabUsage`는 각각 획득 경로와 해당 아이템을 쓰는 레시피를 표시하는 구성 요소다. [게임 데이터 구조](https://docs.moddedmc.wiki/docs/folder_structure/game_data), [상호작용 구성 요소](https://docs.moddedmc.wiki/docs/components/interactive)

교차 모드 태그나 사용자 정의 레시피도 자료를 제공해야 한다. 게임 데이터가 있다는 사실만으로 모든 행동이나 설명이 자동 수록되는 구조는 아니다. 웹 위키 사례이며, 자체적으로 인게임 툴팁을 변경하는 모드로 분류하지 않는다.

### 31. Risk of Rain 2 / Moffein ItemStats — 기존 상세 문구의 표시 위치 변경

아이템·장비 아이콘 등의 툴팁에서 `descriptionToken`을 언어 시스템으로 해석해 사용하고, 유효한 상세 토큰이 없으면 `pickupToken`으로 돌아가는 경로를 확인했다. 작성자도 중첩 수치를 계산하는 옛 ItemStatsMod와 구분한다. [ItemStatsPlugin.cs](https://github.com/Moffein/ItemStats/blob/HEAD/ItemStats/ItemStatsPlugin.cs), [작성자 배포 페이지](https://thunderstore.io/c/riskofrain2/p/Moffein/ItemStats/)

새 설명을 생성하지 않고 이미 있는 상세 설명의 소비 위치를 넓히는 사례다. 표시된 문장의 정확성은 기존 게임·모드 설명 토큰의 내용에 의존한다.

### 32. Risk of Rain 2 / ontrigger ItemStatsMod — 중첩 효과 등록 API

프로젝트 문서는 아이템 툴팁에서 현재 중첩 보너스를 보여주는 기능을 설명한다. 외부 아이템은 `ItemStatDef`를 만들고 `AddCustomItemStatDef`로 등록하며, 추가 보정은 `AbstractStatModifier`와 등록 API로 확장하도록 안내한다. [프로젝트 및 API 안내](https://github.com/ontrigger/ItemStatsMod)

README의 표기는 2.2.1이다. 현재 게임 호환성을 검증하지 않았고 모든 아이템 계산식도 대조하지 않았다. 앞 항목과 이름은 유사하지만 상세 문구 재사용과 중첩 효과 처리라는 조사 대상이 달라 분리했다. BetterUI·LookingGlass까지 같은 기능의 별개 확정 사례로 추가 집계하지는 않았다.

### 33. World of Warcraft / All The Things — 수집 지식의 별도 데이터베이스

작성자 README는 데이터베이스 모듈, 추가 툴팁 정보, 수집 창과 지역별 미니 목록을 설명한다. 퀘스트·상인·희귀 몬스터·던전 등 여러 경로의 정보를 수집 맥락으로 보여주는 프로젝트다. [All The Things](https://github.com/ATTWoWAddon/AllTheThings)

이번에는 소개에 명시된 기능을 확인한 수준이다. 아이템 노드의 내부 스키마, 출처 합성 순서, 설명 문장 생성 함수를 추적하지 않았다. 따라서 데이터베이스 기반 정보 확장의 사례로만 기록한다.

### 34. FTB Quests — 게임 내 편집과 언어별 텍스트 저장

변경 기록에는 편집 언어를 선택하고, 게임 내에서 수정한 문구를 해당 언어 파일에 저장하며, 현재 언어의 번역이 없는 텍스트를 편집 모드에서 강조하는 기능이 설명되어 있다. 퀘스트 내용과 번역 작업을 연결하는 집필 기능이다. [공식 변경 기록](https://github.com/FTBTeam/FTB-Quests/blob/main/CHANGELOG.md)

이 자료는 문서·퀘스트를 유지하는 방식에 관한 것이다. 게임 규칙으로 퀘스트 설명을 자동 작성하거나, 해당 퀘스트가 설명하는 아이템 기능을 검증하는 시스템으로 해석하지 않는다. 변경 기록의 버전별 내용은 현행 API 계약과 구분한다.

### 35. Dwarf Fortress / DFHack — 인스턴스 상태를 추가한 읽기용 이름

`Items::getDescription`은 게임의 기본 아이템 설명을 호출한 뒤 품질·마모 등의 표기를 덧붙일 수 있다. `getReadableDescription`은 포함된 유닛이 있으면 그 이름과 적대 여부를 추가하는 경로가 있다. [Items.cpp](https://github.com/DFHack/dfhack/blob/develop/library/modules/Items.cpp)

아이템의 공통 정체성과 개별 인스턴스의 상태를 나누어 표시하는 인접 사례다. 여기서 함수명이 description이라는 이유로 장문의 용도 설명 생성기로 분류하지 않았다. 주로 사람이 읽는 이름·주석에 관한 코드다.

### 36. Content Patcher — 조건별 번역 키와 명시적 인수

작성자 문서는 번역 키에 매개변수를 넘기고, 현재 언어에 없으면 기본 번역으로 돌아가며, `defaultKeys`로 여러 후보 키를 순서대로 조회하는 방법을 설명한다. 관계·상황별 키에서 공통 키로 돌아가는 예시도 있다. [번역 작성 가이드](https://github.com/Pathoschild/StardewMods/blob/develop/ContentPatcher/docs/author-guide/translations.md)

번역 파일 내부가 Content Patcher의 모든 동적 토큰을 저절로 해석하지는 않는다. 필요한 값을 호출할 때 명시적으로 전달해야 한다. 이 사례는 Stardew Valley 콘텐츠 패치 기반 시설이며, Lookup Anything의 내부 설명 생성법에 관한 추가 주장으로 사용하지 않았다.

### 37. EMI — 레시피를 탐색 가능한 관계로 표현

작성 가이드는 아이템·유체 등을 공통 자원 표현으로 다루고, 레시피의 입력·출력·수량·잔여물을 정확히 제공하도록 설명한다. 레시피 트리의 자동 전개를 위해 기본 경로 메타데이터를 제공할 수 있으며, 출력이 일정하지 않은 레시피는 `supportsRecipeTree`로 제외한다. [Getting Started Guide](https://github.com/emilyploszaj/emi/wiki/Getting-Started-Guide)

기존 레시피 객체가 없는 양조·양동이 채우기 등의 관계도 별도 ID로 등록할 수 있다. 이는 등록된 관계의 상세 탐색에 관한 기능이며, 모든 우클릭 행동을 자동 발견한다고 보장하는 것은 아니다.

### 38. Vintage Story — 공통 함수가 실제 아이템 상태를 조회

공식 API는 인벤토리에서 아이템을 가리킬 때 `GetHeldItemInfo`가 표시 문구를 작성한다고 명시한다. 공통 구현은 내구도, 채굴 속도, 보관 슬롯·내용물, 부패 상태, 영양 정보를 조회하고 해당하는 번역 형식에 값을 넣는다. 음식에는 섭취 시 포만감·체력 정보가 들어가며 부패 보정도 반영한다. [CollectibleObject API](https://apidocs.vintagestory.at/api/Vintagestory.API.Common.CollectibleObject.html), [Collectible.cs](https://github.com/anegostudios/vsapi/blob/master/Common/Collectible/Collectible.cs)

고정 설명을 얻는 함수와 수치·상태 정보의 추가가 함께 존재한다. 이번에 확인한 것은 공통 구현이다. 모든 하위 아이템 클래스와 모든 모드의 재정의까지 동일한 정확성을 갖는지 검증하지 않았다.

### 39. Pokémon Showdown — 정적 문장과 전투 문맥 계산의 결합

`showMoveTooltip`은 기술의 `desc` 또는 `shortDesc`와 함께 위력·명중률 등을 표시한다. 위력 계산은 상대와 전투 문맥을 받을 수 있고, 상대별 값이 다르면 구분해 보여주는 경로가 있다. 모드에 따른 짧은 설명 선택과 우선도·대상 관련 추가 안내도 존재한다. [battle-tooltips.ts](https://github.com/smogon/pokemon-showdown-client/blob/master/play.pokemonshowdown.com/src/battle-tooltips.ts)

작성한 기술 문장과 상황별 계산이 공존한다. Pokémon Showdown 클라이언트의 구현을 확인한 것이며, 원작 게임의 툴팁 구현이나 모든 기술 계산의 정확성을 검증한 것은 아니다.

### 40. Path of Building Community — 외부 모델로 변경 효과 계산

`AddModComparisonTooltip`은 변경 전·후 아이템을 구성하고 계산기를 각각 호출한 결과를 비교 문구로 전달한다. 소스에는 해석하지 못한 효과에 미지원 표시를 붙이는 경로도 있다. [ItemsTab.lua](https://github.com/PathOfBuildingCommunity/PathOfBuilding/blob/dev/src/Classes/ItemsTab.lua)

이는 게임 바깥의 빌드 계산 도구다. 실제 게임 인스턴스의 실행 결과를 직접 읽는 것이 아니라 자체 계산 모델을 사용한다. 단순 용도 설명과 다른 범주의 사례로 수록했으며, 계산·비교 기능을 Iris에 도입하자는 제안은 포함하지 않는다.

## 근거 부족 또는 접근 제한으로 보류한 후보

아래는 검색 도중 발견했으나 이번 조사에서 필요한 원문 또는 구현을 충분히 확인하지 못한 대상이다. 설명 방식에 관한 확정 근거로 사용하지 않고, 추가 사례 수에도 포함하지 않았다.

| 후보 | 확인 한계 |
|---|---|
| Skyrim Creation Kit의 Magic Effect 설명 | 검색에서 효과 설명과 수치 자리표시자 관련 자료를 찾았으나 [문서 원문](https://ck.uesp.net/wiki/Magic_Effect) 접근이 거부되었다. 검색 요약만으로 구현 확정하지 않았다. |
| Dota 2 Workshop Tools의 능력 설명 | 자리표시자 관련 커뮤니티 논의는 발견했으나 [Valve 도구 문서](https://developer.valvesoftware.com/wiki/Dota_2_Workshop_Tools/Localizing)에서 해당 계약을 확인하지 못했다. |
| Luanti의 doc_items / Wuzzy 문서 모드팩 | 자동 문서화 기능을 설명하는 소개는 발견했지만 [원본 저장소](https://www.repo.or.cz/minetest_doc_modpack.git) 접근이 시간 초과되어 생성 규칙을 검증하지 못했다. Luanti 엔진 API 항목과 합쳐 추정하지 않았다. |
| Crusader Kings III의 중첩 툴팁 | 관련 개발 일지의 원문 접근 제한과 이전 주소 문제로 내부 설명 구성까지 확인하지 못했다. |
| Baldur's Gate 3의 DescriptionParams 계열 | 검색한 자료에서 이번 질문에 필요한 공식 툴킷 연결 계약을 충분히 확인하지 못했다. Divinity 문서를 대체 근거로 사용하지 않았다. |
| RimWorld의 정보 카드·StatDrawEntry | 공개된 제3자 자료와 원작의 직접적인 구현 근거를 구분할 필요가 있어 확정 사례에 넣지 않았다. |
| Mekanism·PneumaticCraft의 속성 설명 확장 | 특정 기능에 관한 검색 단서는 있었으나 관련 소스와 실제 표시 경로의 연결을 충분히 추적하지 못했다. |
| Risk of Rain 2의 BetterUI·LookingGlass | 작성자 자료와 기존 ItemStatsMod 계열의 관계는 탐색했으나 독립적인 설명 구조까지 추가 확인하지 못해 중복 집계하지 않았다. |
| WTHIT | 정보 제공자 계열의 후보로 확인했으나 Jade·The One Probe와 구분되는 내부 설명 방식은 추가로 확인하지 않았다. |

## 이 기록으로 확인하지 않은 사항

- 어떤 방식이 자연스러운 한국어 용도 설명을 가장 잘 만드는지는 비교 실험하지 않았다.
- 각 프로젝트가 해당 구조를 선택한 역사적 이유는 작성자가 명시한 경우 외에는 추정하지 않았다.
- 데이터와 설명이 연결된다는 사실만으로 모든 문장의 사실성·완전성·최신성이 보장된다고 판단하지 않았다.
- 설명의 편집 구조, 표시 위치, 상태 계산, 상세 관계 탐색은 서로 다른 조사 대상이다. 한 기능의 존재를 다른 기능의 증거로 대체하지 않았다.
- DVF의 2,105개 아이템에 각 방식을 적용했을 때의 결과, 코드 변경량, 이전 비용은 이번 조사 범위가 아니다.

조사 산출물은 이 기록뿐이다. DVF 데이터, 조합기, 툴팁, Iris 메뉴와 프로젝트의 결정·아키텍처·로드맵 문서는 이 조사 작업에서 수정하지 않았다.
