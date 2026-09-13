# 문제 C — 검수된 DVF expanded의 Menu 구조화와 동일 제품 입력 연결

## 1. 문제명과 입력 기준

- 문제 ID: DVF-RECOVERY-C
- 입력 버전 / 기준일: v3 / 2026-09-11
- 대상: Iris Layer 3 expanded의 제품 투영·Lua 조회·Menu 상세 열람과 B 공통 입력 유지
- 기준 상태: 문제 1~3에서 공통 의미/문장 규칙과 corpus를 마련했고, B는 새 compact 공급·네 줄 Tooltip 후보 구현·통합·사용자 실제 PZ 확인으로 complete다. 새 expanded의 C 연결과 current 공동 활성화는 B 완료에 포함되지 않았다.

[B Walkthrough](iris_tooltip_supply_walkthrough.md)의 실제 결과와 사용자의 B 통과·추후 설명 교정 분리 지시를 반영한다. v2의 r6 입력, B/C 미착수, 과거 reader 실패를 현재 실행 전제로 삼지 않는다. Walkthrough는 이행 결과의 근거이며 새로운 Gate나 권한 요구가 아니다.

두 로드맵 작성자에게 같은 v3와 공통 문서를 제공한다. 이 문서는 필요한 배경·결과 기준을 자체 설명하고, 구체 UI·파일 수·실행 단계·검사 도구는 계획에서 실제 경로를 확인해 정한다.

## 2. 문제 정의

### 현재 상태와 기대 상태의 차이

B는 검수된 compact를 Tooltip에 연결했고 사용자가 실제 표시를 통과시켰다. 하지만 같은 corpus의 expanded를 의미 관계가 유지되는 Menu 상세 화면으로 전달하는 작업은 남아 있다. 기존 Menu가 새 자료를 이미 선택한다고 간주할 수 없다.

이전 제품 후보는 expanded에서 text만 추출해 줄바꿈으로 이어 붙이는 단일 본문 경로였다. 최신 checkout의 실제 소비 경로는 계획에서 확인해야 하지만, 단순 문자열 연결이나 내부 profile별 상투적 분류 설명으로는 복수 용도·조건·획득을 쉽게 구별하는 상세 열람을 보장하지 못한다.

C는 **B와 같은 검수 corpus의 expanded를 제품 자료부터 실제 Menu까지 연결하고, 서로 다른 용도와 그 조건·특성·획득 정보를 관계가 깨지지 않게 구별하여 읽을 수 있도록 하는 문제**다. S2를 길게 복사하거나 새로운 설명 조합기를 만드는 과제가 아니다.

### 영향과 필요성

사용자는 Tooltip에서 개요를 확인한 뒤 Menu에서 상세를 읽을 수 있어야 한다. Menu가 predecessor를 계속 표시하거나 새 expanded를 관계 없는 문장 목록으로 표시하면 두 표면의 정보가 어긋나거나 상세 접근이 어려워질 위험이 있다. B의 사용자 PZ 통과는 Menu 연결·열람의 성공 근거가 아니다.

## 3. 필요한 배경과 현재 상태

### 공통 입력

| 항목 | 기준과 의미 |
| --- | --- |
| 설명 corpus | Iris/build/description/composition/descriptions.json |
| SHA-256 | ba0fc047b3a613e7ef98d2d762cfbd10c1996a02ad4e6f96d1bffa61878262d0 |
| Schema / version | iris-layer3-descriptions-v1 / 1 |
| Reader | description_composition_results.read_result(root) |
| 의미 입력 | Iris/build/description/composition/blocks.json |
| 의미 입력 SHA-256 | b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796 |
| B 좌표 | items[].locales[ko/en].compact |
| C 좌표 | 같은 item/locale의 expanded — items[].locales[ko/en].expanded |
| 대상 | 2,105 items, KO/EN compact·expanded 8,420 states |

각 locale의 expanded는 present 2,043 / absent 62, compact는 present 1,984 / absent 121이다. 두 언어·두 깊이 합계는 present 8,054 / absent 366 / failed 0이다. 이는 저장 결과의 상태 분포이며 Menu 표시 완료 수가 아니다.

Blocks가 없는 62개 item은 두 깊이 모두 absent다. Acquisition-only 59개 item은 compact absent여도 expanded present다. 정상 부재를 새로운 문장으로 채우지 않고, 로드 실패·손상·locale 누락과 구별해야 한다. 옛 r6의 110 scoped/11 gap 분류나 조사 미해결 수를 현재 absence 사유로 복사하지 않는다.

### 설명 구조와 표시 책임

| 요소 | 의미와 C에 필요한 처리 |
| --- | --- |
| expanded.text / segments | 이미 생성·검수된 사용자 설명과 표현 단위. segment 하나가 UI 섹션 하나라는 뜻은 아니다. |
| block/branch/fact refs | 문장이 어떤 의미에 근거하는지 나타낸다. 내부 ID를 사용자 제목으로 표시하지 않는다. |
| qualifiers와 적용 관계 | 어느 사실·branch에 조건이 붙는지 구분한다. 조건을 다른 용도나 아이템 전체에 확대하지 않는다. |
| relations / unresolved_relations | 확인된 관계와 미확정 관계를 구분한다. UI 그룹화로 새 인과나 사용 불가 판정을 만들지 않는다. |
| compact.detail_links | 같은 locale의 expanded segment를 가리킨다. Tooltip에서 생략된 상세의 실제 도착점을 보존한다. 클릭형 링크 UI 자체를 강제하는 요구는 아니다. |
| qualifier_dispositions | compact 조건 배치의 추적 정보. 기존 reader가 허용하는 선택적 필드의 생략을 로드 오류로 만들지 않는다. |
| internal profile | 사실을 조사·정리하는 내부 구조다. 프로필 이름별 상투문이나 고정 UI 섹션으로 변환하지 않는다. |
| Layer 4 / QG | 레시피·우클릭 행동·자유 조리의 구체 상호작용과 목록을 소유한다. C는 기존 Menu 경로를 보존한다. |

현재 expanded에는 앞 문장을 이어받는 표현이 있다. 예를 들어 건축 조건을 먼저 설명한 뒤 “앞의 조건에서 건축 작업에 재료로 쓰인다”가 추가 조건을 설명하고, 화장 적용의 접근 조건 뒤 “같은 접근 조건에서 … 지울 수 있다”가 이어진다. 이 문장을 독립 카드로 떼거나 순서를 바꾸고 선행 문장을 접어 숨기면 원문을 보존해도 의미 전달에 실패한다. 연결된 문장을 함께 읽을 수 있어야 한다.

텍스트 참조만으로 모든 UI 그룹이 자동 결정된다고 가정하지 않는다. 필요한 연결 정보의 충분성은 미확인이다. 부족하면 실제 표시 관계를 위한 최소 metadata/제품 투영 수정으로 해결할 수 있지만 문장 키워드 추측이나 FullType별 수작업 분류로 대체하지 않는다.

### B가 완료한 것과 재사용 범위

B는 새 reader → supply v2 → candidate v2 → T2 static/interaction companion → Tooltip install/package → Lua 경로를 구현했다. S1은 소분류, S2는 compact 한 줄, S3는 획득 장소, S4는 레시피·우클릭·자유 조리 후보 하나다. Alt 및 한 역할당 한 화면 줄, 화면 최대 네 줄을 사용자가 확인하고 통과시켰다.

- 기존 strict T1의 S3/S4 두 L4 행과 달리, B 후보는 S3/S4 역할을 명시적으로 교체했다. 일반 strict/historical 경로는 유지한다.
- S3는 acquisition facts의 장소만 투영한다. 장소 없는 경로는 S3 absent라도 Menu에 획득 설명이 있을 수 있다. C는 B의 장소 행으로 expanded 획득 정보를 대체하지 않는다.
- S4는 기존 QG와 Menu의 EvolvedRecipe owner를 재사용한다. C는 Tooltip 무작위 한 후보만으로 Menu의 상호작용 목록을 대체하지 않는다.
- Tooltip 지원 2,280개 중 DVF 대상은 2,105개, 대상 밖 175개다. 이 수를 C의 지원 집합이나 모든 정보의 부재로 자동 승계하지 않는다. DVF 범위 밖이어도 기존 다른 계층 Menu 정보는 유지한다.
- B embedded 공급 subject는 추적용 자료이며 C의 새로운 의미 authority가 아니다. C는 공통 corpus/reader를 직접 재사용할 수 있다.
- 기존 reader의 정상 소비/historical 재현 분리는 재사용하며 r6 재검증·과거 producer 복원을 C 착수 조건으로 삼지 않는다.

사용자 확인 후보는 .tmp/tooltip/preview/Iris.zip, SHA-256 33b5927127442b16dca917c6f49f3e661743123c0cbd3d5890d47cb6fca96860, product ttp-5a90c7d3844be93670e1b0f6c9f30db41bc0d17a026caf6f70bb797789ebc163이다. 이는 B 보존·재사용 대상을 식별하는 값이지 C가 새 봉인 chain을 만들어야 한다는 뜻이 아니다. 실제 사용자 게임 버전·해상도·배율 수치는 보고되지 않았다.

## 4. 목표

- 새 expanded가 실제 Menu에서 선택·조회·표시된다.
- 사용자가 복수 용도, 각각의 조건·특성, 획득 설명을 구별해 읽을 수 있다.
- 모든 present의 사용자용 정보에 접근 가능하며 접힘·스크롤·탐색 때문에 조건이나 연결된 설명이 고립되지 않는다.
- KO/EN, 단일/복수 용도, acquisition-only, 정상 expanded 부재를 실제 내용에 맞게 처리한다.
- Tooltip의 개요·장소·상호작용과 같은 사실을 더 상세히 보여주고 기존 L2/L4 기능을 훼손하지 않는다.
- 필요한 제품 자료·Lua 조회·패키지까지 연결하고 실제 PZ Menu 열람을 확인한다.

고정 섹션 수, 카드/탭/접기 중 특정 위젯, 첫 화면 전체 펼침, 새 웹 앱을 요구하지 않는다. Menu에는 Tooltip의 최대 네 줄 제한을 적용하지 않는다. 원문 구분 없이 긴 본문 하나로 붙이는 방식만으로 목표를 달성했다고 판단하지 않는다.

## 5. 대상, 책임 경계 및 범위 밖

### 포함 대상

현재 expanded와 의미 연결의 Menu용 투영·직렬화·Lua lookup/renderer, 기존 Menu 상세 소비 경로, 필요한 설치/package/선택 연결과 실제 열람을 포함한다. 표시 그룹 metadata가 필요하면 기존 계약과 제품 경계를 최소 확장할 수 있다. 그룹 제목 등 일반 UI 문구의 현지화는 가능하지만 새로운 기능·추천·대표 역할을 덧붙이지 않는다.

기존 B 입력·Tooltip owner·package 연결을 재사용한다. C 설치가 옛 통합 L3 writer를 통해 Tooltip을 덮어쓰지 않게 하고, 같은 후보에서 Menu가 새 expanded를 소비하면서 수락된 Tooltip이 유지되는 결과를 준비한다. 공동 current 활성화에 필요한 연결과 복원 가능한 자료는 마련하되 사용자 설치/현재 선택 전환을 수행한 것으로 자동 간주하지 않는다.

### 별도 후속 표현 교정

사용자는 B 통과 후 설명을 더 교정할 필요가 있으며 구체 사항을 나중에 전달하겠다고 했다. C의 기본 입력은 지금 검수된 corpus다. 그 후속 교정이나 전체 문체 재검수를 C의 선행 조건으로 만들거나 자동 수행하지 않는다.

C가 새로 유발한 조건 단절·중복·누락은 C에서 해결한다. 안전한 표시 연결을 위해 source 표현 수정이 꼭 필요한 실제 결함은 공통 composition owner로 최소 환류하고 영향만 확인한다. UI가 임의 재요약·번역하거나 item별 대체문을 넣지 않는다. Corpus가 바뀌면 B/C 동일 입력을 유지하며 영향 없는 B 전체 수락을 반복하지 않는다.

### 범위 밖

A 및 문제 1~3 전수 재실행, 전체 미조사 사실 해소, 외부 모드 정규화 구현, B의 네 줄/Alt/S4 정책 재설계, QG 의미 재조사, 레시피·우클릭·자유 조리 목록 재구현, 다른 계층 전면 개편, 새로운 정보 표면, 공개 배포/release는 제외한다.

현재 선택 저장소 안에서 작업한다. 이 문제는 외부 게임 폴더 탐색·설치, 새 clone/worktree나 외부 검증 workspace를 요구하거나 승인하지 않는다. 실제 실행 접근 범위는 계획에서 구체화하며 사용할 수 없는 환경 때문에 독립 구현까지 중단하지 않는다.

## 6. 선행 조건과 의존 관계

문제 1~3의 공통 규칙·출력과 B의 실제 수락 결과를 출발점으로 사용한다. B를 다시 구현·전수 검증하거나 모든 future 문장 교정을 끝낼 때까지 기다릴 필요는 없다.

C의 입력 경로는 새 description reader다. r6 adoption이나 B 공급물 자체를 새 canonical authority로 승격하지 않는다. 정상 readback에서 입력 생산이나 과거 audit 재실행이 필요하다고 가정하지 않는다.

최종 C 후보는 같은 corpus를 사용하는 B와 호환되어야 한다. 이를 위해 필요한 공통 package/selector 수정은 C의 통합 범위다. C 후보의 실제 열람 수락과 사용자 current 공동 활성화·일반 strict production finalization·release는 구분한다. current 전환은 실제 계획/실행 범위를 명시한 경우에만 수행하며, 이를 C 착수 전의 별도 승인 반복으로 만들지 않는다.

## 7. 필수 불변식과 금지 사항

| 조건 | 적용 이유와 C에 미치는 영향 |
| --- | --- |
| 동일 corpus, 다른 깊이 | compact·expanded·S3 장소는 노출 범위가 다르다. 문장 수나 문자열 동일성을 강제하지 않고 의미 일치와 상세 접근을 유지한다. |
| 선행 조건과 후속 문장의 연결 | “앞의 조건”을 가리키는 대상이 실제 화면에서 명확해야 한다. 순서 변경·접힘·분리로 scope를 깨뜨리지 않는다. |
| 복수 용도·조건·대안 보존 | UI 편의로 대표 용도를 고르거나 조건/부정을 삭제하지 않는다. 독립 branch를 새 인과로 묶지 않는다. |
| 부재와 오류 구분 | compact/S3 부재로 expanded를 숨기지 않는다. 62개 expanded 부재는 L3만의 상태이며 기존 다른 계층까지 숨기지 않는다. |
| 내부 구조와 사용자 표시 구분 | profile·ref·client/native·audit를 설명 본문이나 제목에 그대로 노출하지 않는다. 상태/근거 추적과 공개 설명은 분리한다. |
| 실제 상세 보존 | refs나 숨겨진 데이터에만 남겨 놓고 보존했다고 하지 않는다. L4로 이동했다고 주장하려면 실제 접근 가능한 도착점이 있어야 한다. |
| 원문 생산 책임 | 일반 제목/배치는 Menu 책임, 의미·문장 수정은 공통 producer 책임이다. runtime 재조합·재번역·FullType 대체문은 금지한다. |
| B 수락 보존 | C의 설치/조회 경로가 Tooltip owner를 되돌리거나 S3/S4 역할을 바꾸지 않는다. 변경 영향이 있을 때만 해당 회귀를 확인한다. |
| 사용자 후속 교정 분리 | 치트 관련 공개 문구를 되살리지 않고, 예정된 설명 polish를 현재 C 전체 재교정으로 확대하지 않는다. |

## 8. 미확인 사항

| 질문 | 판단에 미치는 영향 | 단서/제약 |
| --- | --- | --- |
| 최신 Menu 상세와 lookup·제품 선택의 실제 연결은 무엇인가 | 재사용할 코드와 최소 교체 범위 | 새 C 연결은 B 완료 범위에 없었고 이전 단일 본문 경로 이력이 있다. |
| 현재 segments/refs만으로 선행 조건·그룹 관계를 충분히 전달할 수 있는가 | 최소 metadata/투영 수정 여부 | “앞의 조건에서” 등의 문장이 존재한다. 문자열 키워드만으로 추측하지 않는다. |
| 긴 KO/EN 상세를 어떤 배치로 구별해 읽을 수 있는가 | UI 구조와 탐색 설계 | 전체 정보 접근과 연결 보존은 필수, 위젯/섹션 수는 미정이다. |
| L3 상세와 기존 L4 목록이 실제로 어디서 중복되는가 | 필요한 표시 연결 범위 | 중복 위험만으로 사용자 조건을 삭제하지 않는다. |
| 기존 package/selector가 C와 수락된 B를 함께 소비할 수 있는가 | 최소 통합·복원 범위 | B는 독립 Tooltip owner와 같은 corpus 인계를 마련했다. |
| 실제 PZ 관찰 환경과 접근 수단은 무엇인가 | 사용자 관찰 또는 실행 범위 | B의 통과를 Menu 통과로 승계하지 않고 미제공 환경 값을 추정하지 않는다. |

조사 단계 수나 대안 비교표를 강제하지 않는다. 위 불확실성의 실제 영향에 맞게 로드맵과 계획을 구체화한다.

## 9. 완료 조건과 필요한 증거

| 결과 | 관찰 대상과 필요한 결과 | 한계 |
| --- | --- | --- |
| C1. 의미 보존과 끝까지 연결 | 새 corpus의 모든 대상 state와 필요한 원문/관계가 제품→Lua→Menu까지 전달된다. 순서 의존, 조건·대안·미확정 관계와 실제 상세 접근을 보존하고 정상 부재/오류를 구분한다. | data/ref equality만으로 화면의 의미 구별을 수락하지 않는다. |
| C2. 실제 Menu 열람 | KO/EN 실제 PZ에서 단일/복수 용도, 선행 조건 연결, 획득만 있는 경우, 긴 상세, expanded 부재 등 관련 위험을 확인한다. 구분·스크롤/접기·전체 접근에 알려진 결함이 없다. | 고정 표본 수는 요구하지 않는다. 실제 관찰 없으면 implemented_only다. |
| C3. 공통 제품과 인계 | 동일 corpus를 사용하는 B와 C 후보가 함께 작동하고 C 변경이 Tooltip·기존 L2/L4를 훼손하지 않는다. 필요한 최소 자동 검사를 충족하고 후보·입력·관찰 범위·current 잔여를 기존 기록에 남긴다. | 공동 활성화·strict finalization·release를 수행하지 않았다면 완료로 주장하지 않는다. |

세 결과는 별도 Gate 세 개가 아니며 같은 후보·읽기·검사 결과를 공유한다. 검사 수·fixture·명령은 계획에서 실제 변경에 맞춰 최소화하고 마지막에 묶는다. 실제 PZ 관찰은 자동 harness와 구분한다. 테스트는 상태를 주기적으로 확인하고 비정상 장기 실행이면 중단한다.

새 validator·품질 점수·proof/seal/receipt 체계, gate별 workspace, 중간 보조 검사기에 대한 검사, 근거 없는 full Run A/B+comparator, B/문제 1~3 전수 재수락은 요구하지 않는다. 실제 기존 계약의 필수 검증은 적용 범위를 확인하고 숨기거나 우회하지 않는다. 외부 reviewer가 필요하면 Codex Reviewer를 사용한다.

완료는 C 후보 구현·통합·실제 Menu 열람 범위다. 실제 표시가 없으면 implemented_only, 구현 자체가 남으면 partial, 필수 입력/도구에 막힌 범위는 blocked로 구분한다. 이미 가능한 구현과 후보 준비는 끝내며 실제 사용자 확인이 필요한 항목만 구체적으로 인계한다.

## 10. 입력 전달 전 확인

B가 완료한 새 입력·네 역할·실제 사용자 수락과 C의 미완료 Menu 연결을 구분했다. 현재 corpus의 분포와 relation/segment 의미, S2/S3 부재와 expanded 존재의 차이, 선행 문장 연결 위험을 본문에 설명했다. r6 상태/수치·과거 실패를 현재 의무로 복사하지 않았다.

추후 설명 교정, C 표시·통합, current 공동 활성화·배포의 범위를 분리했다. 공통 문서와 이 입력만으로 목표·경계·완료 기준을 이해할 수 있으며 UI 수단·단계·파일 수·검사 방식은 실제 필요에 맞춰 설계할 수 있다.
