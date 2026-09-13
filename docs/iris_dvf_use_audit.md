# Iris DVF 전체 용도 설명 조사

2026-09-11 · 현재 checkout의 descriptions.json과 blocks.json 전수 조사. 판정 자료 기록 시각은 09:20 UTC(18:20 KST)다. 구현·corpus 재생성·테스트·commit·push는 수행하지 않았다.

## 전체 결과와 집계 정의

**전체 2,105개 중 한국어 결함 고유 아이템은 1,599개(75.96%)다.** 한국어 compact/expanded를 함께 보면 **행동·관리 중심 1,027개**, **용도와 불필요한 행동 설명 혼재 572개**다. 결함을 확인하지 않은 아이템은 385개, 설명 부재는 121개다. 부재를 적절 또는 결함으로 산입하지 않았다.

질문의 “얼마나 많은 아이템이 용도 중심이 아니라 행동·관리 절차 중심인가”를 엄격한 **행동·관리 중심** 범주로 읽으면 **1,027개(48.79%)**다. 불필요한 절차가 **혼재한 설명까지 포함하면 1,599개(75.96%)**다. 변경된 문장 수나 과거 교정 수치는 이 집계에 사용하지 않았다.

| 한국어 아이템 판정 | 고유 아이템 수 | 전체 대비 |
|---|---:|---:|
| 적절: 두 표면에서 이번 기준의 결함을 확인하지 않음 | 385 | 18.29% |
| 용도와 불필요한 행동 설명 혼재 | 572 | 27.17% |
| 행동·관리 중심 | 1,027 | 48.79% |
| 설명 부재 | 121 | 5.75% |
| 판단 보류 | 0 | 0.00% |
| 전체 | **2,105** | **100.00%** |

표면의 **서술 성격**과 **결함 유무**는 별개다. `use`는 활용을 서술하는 문장이 중심이라는 뜻이지 자동 적절 판정이 아니다. 짧은 용도 문장이라도 결과가 추상적이거나 독립 용도가 빠지면 결함이다. 한국어 compact의 `use` 1,003개 중 76개가 이러한 다른 결함을 가진다.

| 한국어 표면 | 용도 중심 서술 use | 혼재 mixed | 행동·관리 중심 action | 부재 absent | 보류 | 결함 표면 | 결함 미확인 표면 |
|---|---:|---:|---:|---:|---:|---:|---:|
| compact | 1,003 | 719 | 262 | 121 | 0 | **1,057** | 927 |
| expanded | 385 | 572 | 1,027 | 121 | 0 | **1,599** | 385 |

한국어 결함 표면은 **2,656건**이다. 동일 아이템의 두 표면을 중복 계산한 수이며 고유 아이템 수와 다르다. compact 결함 아이템 1,057개는 모두 expanded에도 결함이 있고, expanded에만 결함이 있는 아이템은 542개다.

### 영어와 양언어 합집합

**영어 결함 고유 아이템도 1,599개**, **KO 또는 EN에 결함이 있는 합집합도 1,599개**다. KO만 또는 EN만 결함인 아이템은 각각 0개다. 영어 원문도 별도로 읽고 판정했으며, 이번 의미 기준에서는 최종 아이템·표면 집계가 같았다.

| 영어 표면/아이템 | 용도 중심 서술 | 혼재 | 행동·관리 중심 | 부재 | 보류 | 결함 |
|---|---:|---:|---:|---:|---:|---:|
| compact | 1,003 | 719 | 262 | 121 | 0 | 1,057 |
| expanded | 385 | 572 | 1,027 | 121 | 0 | 1,599 |
| 아이템: 두 표면 통합 | 385 | 572 | 1,027 | 121 | 0 | **1,599** |

EN 결함 표면은 2,656건, 양언어 네 표면 전체의 결함 표면은 **5,312건**이다. 전체 **8,420개 표면 상태** 중 실제 텍스트가 있는 표면 7,936개와 부재 484개를 모두 대조했다.

## 플레이어 관점의 기준

최종 질문은 **“플레이어가 이 설명을 읽고 이 아이템으로 무엇을 할 수 있는지 이해하는가?”**다. 내부 tool·material·transformation_target 역할의 정확성만으로 적절 판정하지 않았다. 기준은 [Philosophy.md](Philosophy.md)의 근거 기반 게임 내 위키, 확인된 사실, 같은 사실의 다른 깊이 원칙과 이번 사용자의 명시적 전수 조사·플레이어 관점 지시다.

- **용도 중심 서술:** 플레이어가 얻는 기능·결과·내용물·제작 목적을 이해할 수 있다. 대상·재질·동적 일치·실제 도구 대안 등 의미상 필요한 한정은 허용한다.
- **혼재:** 활용이 중심으로 남지만 소지·이동 중단·선택·취소·관리·실행당 소비·내부 처리 설명이 불필요하게 붙는다.
- **행동·관리 중심:** 활용보다 설치·탈거·보충·상태 조회·실행 조건·상태 계산을 따라 읽게 한다. 목적 문장 하나가 있어도 본문이 조작 설명이면 이 범주다.
- **부재:** 해당 공개 표면에 설명이 없다. defect는 null이며 적절이나 결함으로 간주하지 않는다.
- **보류:** 읽었으나 실제 의미의 불확실성 때문에 판정을 결정할 수 없는 경우다. 이번 최종 자료에는 이 상태가 없다. 미독 항목을 보류로 채우지 않았다.

아이템 수준 서술 성격은 **행동·관리 중심 > 혼재 > 용도 중심 서술 > 부재** 순서로 두 표면을 통합한다. 어느 한 표면에 확인된 결함이 있으면 해당 locale의 아이템 결함은 참이다. 두 표면 모두 부재이면 null이다. 유형은 복수로 기록하되 한 유형은 한 표면에서 한 번만 센다. locale 아이템 유형 수는 두 표면 유형의 합집합이다.

“재료다”, “할 수 있다”, 대상 역할 또는 문장 길이는 단독 판정 기준이 아니다. 시트 로프 제작 재료라는 목적은 활용을 알려 주지만 “그 제작법에 허용되는 직물을 제공한다”를 expanded에서 반복하는 것은 추가 활용 정보가 아니다. 재사용 도구라는 의미는 보존했고, 실행당 사용량이나 취소 후 상태는 별도로 판단했다. compact를 줄이기 위해 독립 용도를 지우는 것도 결함이며 메뉴를 생략된 절차의 수납처로 간주하지 않았다.

## 입력 식별과 실제 조사 범위

| 입력 | 바이트 | 파일 수정 시각 UTC | SHA-256 |
|---|---:|---|---|
| Iris/build/description/composition/descriptions.json | 57,263,509 | 2026-09-11 08:20:22.5172328 | 1DF567F8442BA93B76B4390FB8962D5FF98D7489223BE2A5EA2A7EDB0E424478 |
| Iris/build/description/composition/blocks.json | 27,717,160 | 2026-09-11 08:20:17.8792214 | 048D16806C5DC47254E47B35BBAFFA62C7F2C7DE0447CE92F88DCD701583ED52 |

`descriptions.json.input.sha256`도 위 blocks 해시와 일치한다. 초기 식별, 전체 읽기를 마친 시점, 판정 자료 출력 시점에서 동일 입력을 확인했다. 서로 다른 입력 시점의 결과를 섞지 않았다.

큰 JSON을 파싱해 공개문을 작은 묶음으로 읽었다. 각 언어의 서로 다른 compact 전문은 474종, expanded 전문은 614종이었다. 중복 문장은 1,000개의 KO/EN 문장 쌍으로 읽고, 전체 아이템을 실제 compact/expanded 조합과 blocks의 기능·역할·결과·착용 위치·재질로 대조했다. 표시 조합 637개에 속하는 모든 아이템 ID를 확인했다. 대표 family 몇 개를 읽고 나머지를 자동 통과시키지 않았다.

KO와 EN의 segment 수와 분할이 다른 곳도 확인했다. 무기 부품의 EN compact에 추가되는 독립 탈거 문장과 라디오/TV의 EN에서 결합되는 회수·설치 문장을 별도로 읽었다. 분할 차이 자체를 누락이나 결함으로 보지 않았다. 공백·개행 차이를 제외한 전문과 segments의 연결 내용은 일치하며, 항목 자료에는 개행을 포함한 원문을 보존했다.

대소문자를 포함한 **2,105개의 exact item ID**를 구분했다. `Base.LemonGrass`는 식용·요리용 설명이 있고 `Base.Lemongrass`는 설명이 없으므로 별도로 대조했다.

생성 경로와 기존 [대표 사례 보고서](iris_dvf_use_description_report.md), [품질 walkthrough §8](iris_description_quality_walkthrough.md)을 필요한 범위에서 참조했다. 게임 원본 전체 재조사, 게임 설치 경로·저장소 밖 사용자 파일 접근, 실제 UI 검증은 하지 않았다. 보조 처리는 추출·판정 기록·집계용이며 canonical validator가 아니다. 의미 판정은 읽은 원문과 실제 역할 조합에 대한 편집 판단이다.

## 유형별 중복 집계

각 행의 아이템 수는 해당 유형이 한 번 이상 있는 고유 아이템 수다. compact/expanded는 해당 표면에서 그 유형이 발견된 건수다. 행간 중복이 있으므로 합산해 결함 아이템 수로 쓰면 안 된다.

| 유형 | KO compact | KO expanded | KO 아이템 | EN compact | EN expanded | EN 아이템 |
|---|---:|---:|---:|---:|---:|---:|
| 불필요한 실행 절차·조건 procedure | 834 | 1,575 | 1,575 | 834 | 1,575 | 1,575 |
| 자체 관리를 용도로 제시 maintenance | 348 | 574 | 580 | 348 | 574 | 580 |
| 과도한 추상화 abstraction | 108 | 404 | 497 | 108 | 404 | 497 |
| 플레이어 활용 정보 부족 insufficient_use | 241 | 229 | 241 | 241 | 229 | 241 |
| 같은 용도·조건의 반복 repetition | 4 | 166 | 166 | 4 | 166 | 166 |
| compact 정보 밀도 density | 137 | 0 | 137 | 137 | 0 | 137 |
| 내부·구현 관점 노출 implementation | 7 | 31 | 32 | 7 | 31 | 32 |
| 확인된 독립 용도 누락 omission | 17 | 0 | 17 | 17 | 0 | 17 |
| 역할 오귀속·혼동 role | 1 | 4 | 4 | 1 | 4 | 4 |
| 적용 범위 불일치 scope | 1 | 0 | 1 | 1 | 0 | 1 |

omission은 동일 입력의 blocks와 expanded에서 확인되지만 compact에 드러나지 않는 독립 용도다. insufficient_use는 공개문으로 사용 목적·효과를 이해하기 어렵다는 판정이다. 미서술 구체적 효과가 상류 근거에 존재한다고 확정하는 분류가 아니다.

## 남아 있는 공통 경로와 실제 판정

### 명시적 용도 프레임 밖의 기존 expanded 경로

[description_composition_uses.py](../Iris/tooling/src/iris_tooling/domains/layer3/description_composition_uses.py)의 internal_reason()은 세척 대상·의류 패치 대상·이름 변경과 일부 결과를 제외한다. frames()에는 세척제, 착용, 연료·불쏘시개, 개봉 결과, 점화 등의 명시적 표현이 있다. 반면 [description_composition_results.py](../Iris/tooling/src/iris_tooling/domains/layer3/description_composition_results.py)의 _expanded()는 이 경로가 처리하지 않은 unit을 _expanded_remaining()에 보내고 qualifier를 grammar.qualified()로 공개한다.

이에 따라 현재 의류의 옛 세척·패치 설명은 사라졌어도 총기·물 용기·음식·차량 부품·독서·화장에는 실행 조건 나열이 남는다.

| 아이템 | 현재 원문에서 확인한 내용 | 판정 요점 |
|---|---|---|
| Base.Socks_Ankle / Base.Socks_Long | 착용, 연료·불쏘시개, 직물 회수, 시트 로프 제작. expanded에 허용된 직물을 제공한다는 문장 | compact 적절, expanded는 가벼운 절차 혼재. 과거 물10단위·젖음·이동 중단을 현존 결함으로 세지 않음 |
| Base.223Bullets | 장전 뒤에 주 손·소지·달리면 중단·장전된 탄이 남는 설명 | expanded 행동 중심. 분해는 가공 대상이라는 추상 표현도 남음 |
| Base.Apple | 요리 재료·식용·덫 미끼. expanded에는 음식과 재료의 인벤토리 이전·잔류·이동 중단 | 식재료 역할이 맞다는 이유로 통과하지 않고 실행 설명의 비중을 판정 |
| Base.WaterBottleFull | 음용·급수·소화와 함께 갈증0.1/0, 독20, 질병0.3, 취소 후 잔량, 버리기 | compact는 복수 용도 보존. expanded는 행동·관리 중심 |
| Base.Battery | 조명·기둥 조명·휴대 기기·기기의 빈 칸별 삽입 설명 | 전원 용도는 적절하나 expanded에서 같은 공급 용도의 절차 반복 |
| Base.ModernBrake1 등 | 설치·탈거·도구·실패·타이어 선행 제거·주행 마모 | 장착 가능성만으로 플레이어가 얻는 기능이 충분히 드러나지 않음. 절차 중심과 정보 부족 병기 |
| Base.Notebook | compact는 읽기·쓰기. expanded는 소유 잠금·확인 버튼·취소와 저장 상태 | compact 적절, expanded는 편집·관리 절차 중심 |
| Base.Lipstick | 입술 화장과 거울의 층·장애물·차량/파운데이션 예외·Apply·미리보기 취소 | 실제 화장 용도는 있으나 expanded가 UI 조작 설명 중심 |

### 관리를 상세로 보내는 선택

[description_composition_planner.py](../Iris/tooling/src/iris_tooling/domains/layer3/description_composition_planner.py)의 DETAIL_FUNCTIONS에는 잔량 통합, 적용된 붕대·부목 제거, 전지 삽입·제거, 기기 조작창, 라디오 프리셋 편집 등이 남아 있다. 코드 주석도 관리와 적용된 치료의 제거를 상세 설명에 둔다고 명시한다. 이번 기준에서는 상세라는 사실만으로 공개 용도가 되지 않는다.

처리 대상 전체를 제외하지는 않았다. Base.Remote의 “분해해 수신기·전기 회로 부속을 얻으며 건전지도 나올 수 있다”는 실제 활용이다. 같은 리모컨의 제작 재료 용도도 별도로 인식했다. Base.TirePump의 타이어 공기 공급은 실제 도구 용도이며 타이어 자신의 관리 설명과 구분했다.

### 역할·일반 작업명으로 끝나는 설명

Base.CandyPackage의 “포장 개봉에 쓰는 재료”, Base.NailsBox 등의 “내용물을 꺼낼 수 있는 포장 재료”는 실제 내용물을 충분히 밝히지 않는다. 반면 Base.CannedCorn의 명명된 개봉 결과와 요리 재료 활용, 농산물 자루의 명명된 결과는 플레이어에게 무엇을 얻는지 알려 준다.

Base.Antibiotics와 다섯 Base.Pills 계열은 복용 가능성과 실행 조건을 말하지만 효과를 설명하지 않는다. 읽은 blocks도 복용 기능 중심이므로 효과를 추측해서 채우지 않았다. 기술 잡지와 일부 설치물도 이름에서 효과를 추정하지 않고 공개 정보 부족과 근거 한계를 구분했다.

총기 부품은 부착·탈거만 있고 개별 부품의 기능 차이가 설명되지 않는다. Base.HandTorch, Base.Torch, Base.Rubberducky2의 expanded에는 전력을 받는 기기를 설명하면서 그 기기를 다른 빈 기기에 넣는 듯한 조건 연결이 있다. Base.Generator에는 자기 급유·수리를 공급 측 능력처럼 읽게 하는 문장이 있다. 역할 혼동으로 별도 기록했다.

### 새 프레임의 내부 용어와 compact 누락

씨앗 봉지의 “선언된 내용물 수량은 50개”, 점화의 “실제 점화는 해당 대상의 지원 상태에 달려 있다”는 내부 데이터·구현 시점을 공개문에 드러낸다. 내용물 수량과 지원 범위의 근거를 보존하는 것과 그 언어를 본문에 출력하는 것은 분리했다.

열쇠의 맞는 차량·문·자물쇠라는 동적 조건, Base.Frog의 실제 복수 칼, 확정 회수와 조건부 회수는 필요한 한정으로 인정했다. 조건절이 있다는 이유만으로 결함 처리하지 않았다.

compact에서는 Base.Aluminum의 모자 제작, Base.Paperclip의 낚시 장비 제작, Base.Stake의 텐트 키트 제작 등 독립 용도가 드러나지 않는다. PRODUCT_CONTEXTS와 compact의 역할·일반 제작 요약 경로는 이 expanded와의 차이에 대응한다. 독립 용도를 짧게 만들기 위해 없애는 것도 결함이다.

## 항목별 자료와 남은 불확실성

전체 자료는 [review/uses/items.json](review/uses/items.json)이다. items 배열의 exact item_id에서 locales.ko/en.compact/expanded를 조회하면 다음을 대조할 수 있다.

- 입력의 존재 상태, 이번 분류, 결함 boolean/null, 복수 결함 유형.
- 개행을 포함한 실제 전문 text와 구체적 판정 이유.
- 해당 segment의 0부터 시작하는 위치·원문 발췌·block 참조를 가진 findings.
- 해당 아이템의 기능·역할·결과·상태 근거와 fact 참조, 구조화된 개봉·처리 관계.
- locale별 아이템 분류·결함 여부와 개별 uncertainty.

**미독 0, 판정 보류 0이다.** 다만 개별 근거상 유보는 242개에 남겼다. 241개는 공개문의 활용 정보 부족을 확인했지만 미서술 효과·기능 차이의 정확한 내용을 이번 입력에서 새로 확정하지 않은 항목이다. 나머지 1개는 Base.BrokenFishingNet으로, 철사 회수 용도는 인정하되 Wire;3의 확정 회수량은 새로 단정하지 않았다. 미독이나 집계 미완을 뜻하지 않는다.

385개의 결함 미확인 역시 게임에 존재하는 모든 용도의 완전성이나 실제 화면 합격을 보장하지 않는다. 이번 입력과 기준에서 실제로 읽은 설명에 결함을 확인하지 않았다는 범위의 결론이다. 원본에 없는 용도 발굴, 게임 전체 원본 조사, 실제 글꼴에서의 compact 물리적 적합성은 조사하지 않았다.

기존 dirty/deleted/untracked 변경을 보존했다. 산출물은 이 보고서와 항목별 자료이며 구현 교정·새 계획/Gate·채택 상태 변경·감독 자동화를 만들지 않았다. 입력 전문과 저장된 전문의 일치, ID 개수, 집계 합계를 읽기·집계 작업으로 대조했으며 테스트 실행이나 품질 PASS 주장은 하지 않았다.



## 2026-09-12 successor 구현 중 기록

이 절은 위 2026-09-11 전수 조사와 구별한다. 현재 상태는 **partial — 공통 규칙 교정 및 KO/EN 원문 검토 중**이다. 위 조사 수치·`items.json`의 기존 `reviewed` 판정은 이전 입력에만 적용하며 새 corpus에 승계하지 않는다. 현재 canonical 위치의 JSON은 구현 중 초안이고 B/C의 이전 accepted binding은 아직 변경하지 않았다. 생성 성공을 의미 수락 또는 자동 검사 PASS로 취급하지 않는다.

공통 public plan은 accepted 함수·활동·참여 역할·효과를 분류하고 미구현 입력은 failed로 처리한다. 자체 관리와 내부 기록은 refs를 보존하면서 공개 대상에서 제외한다. 공개 qualifier는 적용 대상별로 판단하며, 일반 소지·이동·취소·제작 수량과 같은 절차를 짧게 바꿨다는 이유로 공개하지 않는다. qualifier 내부 처리 기록은 원래 fact의 application 범위를 가진 검토 보조 정보이며 새로운 semantic authority가 아니다.

원래 작업 bytes는 `docs/review/uses/before.zip`에 보관했다. 기존 2,105 FullType의 순서·대소문자와 8,420 좌표를 유지한다. 현재 생성 초안은 네 표면 각각 present 1,980 / absent 125이며 생성 실패는 없었다. 이후 교정에 따라 바뀔 수 있고 전수 품질 판정은 아직 끝나지 않았다. 최종 자동 검사는 아직 실행하지 않았고 새 B/C ZIP도 만들지 않았다.

### 새 부재의 근거와 범위

이전 121개에서 추가된 3개는 네 표면에 동일하게 적용되어 12좌표가 늘었다. 모두 선언과 저장된 admitted facts를 대조했다.

- `Base.BucketConcreteFull`: `scripts/items.txt`의 drainable 선언, 빈 양동이/물 교체 속성은 있으나 accepted 공개 construction use가 없다. 남은 dump_contents/consolidate는 자기 관리다. 콘크리트라는 이름으로 건축 효능을 추가하지 않는다. 조사한 repository source에서 해당 아이템의 적극적 건축 사용을 확인하지 못했으며 전역적으로 사용할 수 없다는 주장은 아니다.
- `Base.Cornmeal`: 같은 script의 drainable 선언이며 Food 타입 또는 EvolvedRecipe 재료 사실이 없다. 남은 consolidation은 자기 관리다. 음식 카테고리 이름만으로 섭취·요리 능력을 만들지 않는다.
- `Base.Rubberducky2`: `scripts/newitems.txt` 선언, `scripts/recipes.txt`의 건전지 넣기/빼기 및 `lua/server/recipecode.lua`의 충전량 이전은 확인했다. 배터리 관리만으로 빛·소리·장난감 기능을 주장하지 않는다. 공개 효능의 근거 부족이며 구현되지 않은 출력 규칙을 부재로 숨긴 경우와 구별한다.

### 공개 표현 결함과 근거 부족의 분리

알약의 중복 복용 문구는 교정했으나 약효 공급은 별개다. 기존 `recovery_sources.py`의 pill owner와 `semantic_results.py`는 native `BodyDamage.JustTookPill` 효과를 이름이나 수치 부호로 추정하지 않는다. 차량 브레이크·서스펜션 등의 장착/탈거/마모 근거도 제동·승차감 등 native 성능 사실을 대신하지 않는다. Moveable 배치, 접힌 우산의 형태 변경, 발전기 조작 역시 그 자체로 가전 기능·방수·전력 효과의 증거가 아니다. 이 범위의 실제 evidence gap과 아직 남은 표현 결함을 별도로 재판정한다.

열린 우산 4종은 잠정 부재를 해소했다. `recovery_sources.supplement_player_uses`가 admitted declaration의 `ProtectFromRainWhenEquipped=TRUE`, `lua/shared/Foraging/forageSystem.lua:getWeatherPenalty`, `lua/client/Foraging/ISSearchManager.lua:updateModifiers`의 호출을 연결한다. 같은 source hash/span의 중복 locator·줄바꿈 표현은 동일 선언으로 다루되 상충 선언/속성은 거부한다. 일반적인 손에 든 비 보호와 야외 채집의 강수 불이익 감소를 서로 구분하는 12개 fact를 기존 block 입력의 inline correction으로 공급한다. 완전 방수·달리기 효과·다른 날씨의 개선은 주장하지 않는다. 원래 r6/adoption은 변경하지 않았다.

`Base.Generator`는 신규 잠정 evidence gap이다. 자기 연결·가동·급유·수리를 독립 용도로 수락하지 않는다. 같은 발전기를 대상으로 하는 관리와 전자 스크랩/연료가 다른 발전기에 제공하는 수리·급유 용도는 공통 판정에서 구분했다. 좁은 근거 추적에서 `ISPlugGenerator.lua:perform`의 연결 setter와 `ISActivateGenerator.lua:perform`의 가동 setter, `ISWorldObjectContextMenu.lua`의 주유기 전력/외부 발전기 옵션 및 스토브·건조기 `isPowered` 소비, `ISGeneratorInfoWindow.lua:getRichText`의 공급 대상 getter를 확인했다. 접근 가능한 Lua에는 가동한 발전기에서 square/container의 전력 상태로 이어지는 공급 구현을 찾지 못했으며 해당 native 구현 파일도 repository 경로 검색에서 발견되지 않았다. 최소 잔여는 이 공급 연결의 직접 근거 또는 기존 owner에서 허용할 별도 명시적 기능 근거다. 독성·공급 범위·연료 효율의 완전 증명을 전력 공급 설명의 조건으로 추가하지 않는다. 이 기록은 정당한 공개 부재의 최종 수락이 아니다.

현재 확인한 잔여에는 일부 건축 조건 반복, 역할명만으로 추상적인 제작 용도, 치료 결과의 중복/내부 수치 문구, KO/EN 전체 미검토 조합이 있다. accepted 식품 callback 중 결과 타입/개수를 바꾸지 않는 것으로 직접 확인한 경우만 기존 source adapter의 제작 대상 관계에 연결한다. 추가 결과물·효과·양을 이름으로 보충하지 않는다.

### 계속된 공통 교정

씨앗 봉투의 관계 수락에서 고랑별 소비량 qualifier가 빠져 작물명·개봉 결과가 generic 문구로 밀리는 결함을 교정했다. 이 qualifier는 관계를 인정하는 닫힌 집합에 포함하지만 원문 소비량을 공개할 의무로 연결하지 않는다. 봉지의 내용물 수량과 파종 행동의 실행당 소비량은 구별하며 후자는 내부 근거에만 남긴다. 자동으로 붙이던 도구 부재 설명도 두 언어에서 제거했다. 실제 필수 도구는 계속 명시한다.

추가 공통 교정은 탄약 분해/병 깨기의 구체적 회수 결과, 그릇의 분배 용도 중복 통합, 오트밀 재료 조건의 대상 명시, 농작물 살포제의 효능 중심 표현, 의료 공포 조건의 실제 시술 범위 분리다. 문장 조합의 근거 허용과 qualifier 원문 공개는 별도 판단이다. 이 과정의 인메모리 원문 추출은 편집 보조이며 검사기나 새 authority가 아니다. 아직 최종 전수 수락·B/C 재결속·자동 검사를 완료하지 않았다.

복용 dispatch(`take_pills`, `take_food_medicine`) 자체는 약의 목적·효과를 설명하는 독립 활용으로 공개하지 않도록 공통 판정을 수정했다. 약효 이름 추정을 금지하는 기존 `pill_controls`/`food_callbacks` owner 범위와, 해당 선언·소비 호출만 확인된 근거를 따른다. 원본 fact와 조건은 내부에 남으며 별도로 확인된 제작 역할이나 효과가 있으면 그 활용은 계속 공개한다. 따라서 이는 모든 의약품을 숨기는 FullType 규칙이 아니다. 최종 생성 후 정확한 영향 품목·부재 변화와 전수 판정을 기록해야 한다.

## 2026-09-12 전환 corpus 자체 검토 완료

이 절은 위 조사/구현 중 상태 이후의 현재 기록이다. `docs/review/uses/items.json`은 현재 descriptions `fc8c11d0e4e375fdf3449e7ae9141779bcf00023ba2537751579cf243b8ebb05`, blocks `0c806c345cbe512129c8a4af27ecd85a965607d8feeb8d14587335a0ab6ccb03`에 대한 누적 원문·근거 대조를 기록한다. 2,105개·8,420좌표 전수 자체 검토를 마쳤으며 미독 0, 확인된 미해결 표현 결함 0이다. 외부 Reviewer의 독립 판정은 아니다. 전체 native 효과나 게임의 모든 용도를 확정한 것은 아니며 항목별 upstream evidence gap은 별도로 남겼다.

네 표면 각각 present 1,981 / absent 124다. 원래 121 부재와 비교해 BucketConcreteFull, Cornmeal, Rubberducky2의 3개가 늘었다. 자체 관리만 남은 이 품목은 공개 목적의 근거 부족으로 기록하며 부재 증가를 품질 개선 실적으로 계산하지 않는다. 약품 6종과 발전기의 중간 부재는 최종 상태가 아니다. 약품은 실제 선언 Tooltip의 명시적 약효, 발전기는 야외 주유기 급전 설명과 메뉴 조건을 기존 owner에서 보완했다. 열린 우산 4종을 포함한 보완은 20 facts이며 원래 semantic 28,145 + acquisition 1,057에 더해 총 29,222 facts를 보존한다.

공통 public plan은 독립 활용을 compact와 expanded 모두에 남기고 자체 관리/실행 bookkeeping을 내부 처리한다. 재료·결과·도구 대안은 실제 관계의 범위로 묶고 고랑당 씨앗 소비량 및 자동 ‘도구 없이’ 문장은 공개하지 않는다. 검토 보조 코드는 기존 자료를 전사·집계한 일회성 수단이며 canonical validator가 아니다. 전환 직전 dirty bytes는 `docs/review/uses/before.zip`, 전체 원문 비교는 `docs/iris_dvf_description_review.html`에 있다.

이 시점의 자동 검사/B·C 후보 생성 결과는 아래 후속 closeout에 기록한다. 실제 PZ 표시는 미관찰이며 수락하지 않는다.

## 2026-09-12 player-use 전환 closeout — implemented_only

계획 `iris_dvf_player_use_description_transition_plan.md`의 공통 용도 표현·제한적 기존 owner 보완·전수 자체 원문 검토·새 B→C 후보 연결을 구현했다. 실제 PZ 관찰은 **unvalidated_but_in_scope**다. 사용자 사전 owner approval은 적용했으나 이전 후보의 실제 표시 수락을 새 ZIP에 승계하지 않았다. live/current 활성화, 게임 설치, commit/push/release는 하지 않았다.

최종 descriptions SHA256은 `ffde6886d117482336159de49dd1ddc8ff075df2499217b09400542a895246b0`, blocks는 `0c806c345cbe512129c8a4af27ecd85a965607d8feeb8d14587335a0ab6ccb03`다. 직전 `fc8c11...` 원문에서 봉합의 ‘붕대가 감기지 않은’ 조건 누락을 복구했다. 영향을 받은 Needle/SutureNeedle/Thread 3개·12좌표를 다시 읽고 항목 기록과 HTML에 반영했다. 총 2,105개·8,420좌표, 각 surface present 1,981 / absent 124, 미독 0·확인된 잔여 표현 결함 0이라는 자체 판정이다. 근거 부족과 native 효과 완전성의 한계는 개별 uncertainty에 남겼다.

### 기존 검사 실행 결과

모든 명령은 repository 루트 PowerShell에서 실행했다. 아래 첫 묶음의 전체 종료 상태는 실패이며 성공으로 바꾸어 기록하지 않는다. 변경 없는 블록 node의 성공 결과는 계획 §7에 따라 공유하고, 설명 수정의 영향을 받은 설명/B만 다시 실행했다. 별도 validation-of-validation이나 추가 confidence 검사는 실행하지 않았다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration --basetemp .\.tmp\v -q -s --tb=short
# exit 1: 1 failed, 2 passed in 121.45s. 블록/B node 성공, 설명 node 봉합 조건 누락 실패.

uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\w -q --tb=short
# exit 0: 1 passed in 6.57s.

uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\tooling\tests\test_tooltip_t2_projection.py::test_s2_supply_and_owner_integration --basetemp .\.tmp\x -q -s --tb=short
# exit 0: 1 passed in 102.42s.

$env:IRIS_MENU_TOOLTIP_CANDIDATE = '.tmp/tooltip/run-frlycdx2/s/.tmp/package/Iris.zip'
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_product_integration.py::test_product_contract --basetemp .\.tmp\y -q -s --tb=short
# exit 0: 1 passed in 79.60s.
```

B 자식의 repository Lua syntax, supply runtime, package 명령은 각각 exit 0이었다. C 자식의 source/stage Lua syntax(388 files), Browser/Wiki expanded 모델(4,210 locale 상태), Tooltip runtime(2,280 keys), Layer 4 모델, package admission fault, package 및 actual ZIP pointer 명령도 각각 exit 0이었다. 검사에서 출력된 Fixture.Layout fit failure는 의도된 화면 용량 실패 fixture이며 실제 PZ fit 관찰이 아니다. C node 안에서 두 build 일치, 원문/refs/scope/order/detail links, B 106개 retained member bytes, 중단·rollback·idempotence·source pointer 보존을 검사했다. 실행 중 상태/진행을 확인했으며 비정상 장기 실행이나 강제 중단은 없었다. Python 생성 중 잘못된 write_result 인자 호출은 실패로 끝났고 정상 호출로 생성했으며 테스트 성공으로 집계하지 않는다.

### 최종 후보와 인계

- 새 B: `.tmp/tooltip/run-frlycdx2/s/.tmp/package/Iris.zip`
  - SHA256 `b6af414a583f75573e5eac308f655564aa3e0348266ad4d9a2474222396dddaa`
  - owner `ttp-d01c54c44ceac5664796b746038c8127dc678f8345ea5e04c5a6204b0369d6e8`
  - supply `ada0ac7184397440565bfc22bb5bd652f1275365804e0b75134f4e357347a488`
- 새 공통 C: `.tmp/menu/run-7ztpp37i/p/Iris.zip`
  - SHA256 `db2174e72e5acc50db8651c538343e6adc432950015d04d44b4da5c7145a9796`
  - product `l3p-7514d54f6f3d27e727a3b78b14f38e9f9c7d74d49a185c938b709c5f2d53d414`

C는 위 새 B ZIP을 명시적 tooltip_ref로 받아 동일 corpus와 독립 owner를 결속했다. 소스의 과거 ACCEPTED_TOOLTIP/ACCEPTED_DESCRIPTION 상수는 historical 수락값이며 이 successor 후보의 기본값으로 재해석하지 않는다. 재생성 시 `build_menu_product(root, output, tooltip_ref=binding(root, 새_B_경로))` 또는 위 기존 통합 node의 명시적 환경 입력을 사용한다. 첫 B `run-b7nrzztu`는 봉합 교정 전 후보이므로 최종 인계 대상이 아니다.

실제 PZ에서 확인할 남은 범위는 계획 Change 7의 같은 C ZIP에 대한 KO/EN 긴 compact·복수 활용·부재·Alt 및 S1/S3/S4 공존, Browser/Wiki 긴 expanded·좁은 폭·스크롤 끝·Layer 4 접근이다. PZ 버전/해상도/UI scale/관찰자는 unknown / not reported이며 표시 수락을 주장하지 않는다. 추가 proof artifact나 검사기 신설 없이 implemented_only로 closeout한다.

## 2026-09-12 의미 판정 재개 — partial

후속 실제 원문 검토에서 공통 점화 frame의 내부 지원 문구, 도구 설명의 수행 요건 나열, 음식 미끼의 추상적 주어, 차량 부품 목적의 미확정 문제가 확인되었다. 위 ‘잔여 표현 결함 0 / 실제 PZ만 남음’ 판단을 철회한다. ledger의 읽기 이력과 자동 검사 결과는 보존하지만 의미 적합성 수락으로 사용하지 않는다. 기존 ffde6886... corpus와 run-7ztpp37i C ZIP은 당시 자동 검사 통과 후보이며 의미 품질 승인 후보가 아니다. 공통 규칙과 같은 의미/조합 범위를 교정하고 재판정할 때까지 partial이다.

## 2026-09-12 공통 목적군 교정 후 후보

재개 시 확인된 점화 주체·음식 미끼·복합 도구 목적군·중복 수행 요건을 공통 규칙으로 교정하고 실제 영향 범위를 재판정했다. 42개 차량 부품의 구체 기능 부족은 개별 purpose_unresolved로 기록한다. 포괄적인 결함 0 선언을 복원하거나 자동 검사 성공을 의미 품질 승인으로 사용하지 않는다. 누적 전수 자체 읽기/변경 범위 재판정의 상세와 한계는 `iris_dvf_use_description_report.md`의 최신 절 및 `review/uses/items.json`에 있다.

현재는 **implemented_only**: corpus `2301a4a4b8d24a28447ea53e3e47dd7143b362fb9e3b3b2531cf3152e4491e30`, B `.tmp/tooltip/run-cr4yy73j/s/.tmp/package/Iris.zip`, C `.tmp/menu/run-5b363prk/p/Iris.zip`(SHA256 `a55538e4cdaf47c771258a2c75d33dce0f93ba66cc524eb465873d1fa0086080`). 마지막 설명/B 묶음 exit 0(2 passed, 91.80s), 같은 B를 받은 C exit 0(1 passed, 72.08s). 실제 PZ는 미관찰이고 complete/독립 품질 승인/live 전환이 아니다. 과거 ffde 후보는 역사적 자동 검사 결과로만 남긴다.
