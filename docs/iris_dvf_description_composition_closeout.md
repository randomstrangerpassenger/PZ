# DVF description composition closeout

2026-09-10. 문제 2의 offline 공통 문장 조합기와 문제 3 검수용 전체 결과를 구현했다. [계획](iris_dvf_description_composition_plan.md) §7의 집중 검사 및 대표 원문 자체 검토를 완료했다. 전체 언어 품질 수락, 제품 current 전환, 실제 PZ 표시 검증까지 완료한 것은 아니다.

## 구현과 인계

`Iris/tooling/src/iris_tooling/domains/layer3/description_composition_*.py`에 의미 계획, 공통 기능별 문장 구성, 어휘, KO/EN 실현, 결과 모델 및 저장/읽기를 추가했다. Compact와 expanded를 동일 의미 입력에서 각각 구성하며 기존 r6 완성 문장을 입력으로 사용하지 않는다. 구체적인 내용 배치와 조건 범위는 [표현 계약](iris_dvf_description_composition_contract.md)에 기록했다.

입력은 기존 reader가 읽은 `Iris/build/description/composition/blocks.json`이다. 실제 SHA-256은 `b0b1f8b402c74c48efa0d3ef5bb9413709e38e4582cdbffe8ea74749304d5796`이며 계획의 입력과 일치한다. 2,105개 아이템, 29,202개 fact, 10,304개 block을 소비했다.

검사한 결과를 그대로 `Iris/build/description/composition/descriptions.json`에 보존했다. Schema는 `iris-layer3-descriptions-v1`이다. `description_composition_results.read_result(root)`는 저장된 원문·상태·의미 연결을 읽으며 입력 reader나 producer를 호출하지 않는다. 생성기와 참고 어휘의 식별 정보는 같은 결과에 있고 별도 봉인 파일은 없다.

| 언어 | 표면 | present | absent | failed |
| --- | --- | ---: | ---: | ---: |
| KO | compact | 1,984 | 121 | 0 |
| EN | compact | 1,984 | 121 | 0 |
| KO | expanded | 2,043 | 62 | 0 |
| EN | expanded | 2,043 | 62 | 0 |

총 8,420개 표면 상태다. 채택된 내용이 없는 62개와 획득 내용만 있는 59개를 구분한다. 후자의 획득 문장은 expanded에 있으므로 compact 부재는 121개다. 과거 설명의 공백 여부를 부재 기준으로 사용하지 않았다. `present`는 전체 자연어 품질 수락을 뜻하지 않는다.

## 실행한 검사

계획 §7의 다음 명령만 테스트 진입점으로 사용했다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_description_composition.py -q
```

최종 실행은 **exit 0, `1 passed in 4.53s`**다. 초기 fixture 수정과 실제 원문에서 발견한 공통 규칙 수정 후 같은 명령을 재실행했다. 각 실행은 전체 결과 하나의 생성·입력 직접 대조·저장·읽기를 공유한다. 최종 명령은 약 5.2초 안에 완료되어 장기 실행이나 중단이 발생하지 않았다. 계획 밖 중간 테스트 및 Lua/Java/JS·제품 전체 suite는 실행하지 않았다.

검사는 역할/조건 범위, 병렬화, 입력 순서 안정성, 대안·결과·미확정 관계, 미지원 조건의 실패와 닫힌 문장 규칙의 일반 경로 복귀를 작은 fixture에서 확인한다. 전체 결과에서 exact 대상과 네 표면, fact/qualifier의 정확한 적용 연결, 관계와 방향, 같은 언어의 실제 expanded 연결을 입력에 직접 대조한다. 저장 후 읽기에서는 생성과 입력 읽기를 금지한 상태로 원문·상태·연결의 동일성을 확인한다. 이 검사를 새로운 validation authority로 승격하지 않았다.

## 실제 원문 검토와 수정

동일 결과에서 KO/EN compact/expanded를 읽고 공통 규칙을 수정했다. 다음은 검토 범위와 주요 관찰이다.

- Plank/Hammer: 역할 문장과 기능 문장의 반복 나열을 활동별 재료/도구 역할과 용도 명사구로 조합했다. 개별 제작 결과와 실행 절차는 상세에 두고, Hammer의 수리 대상 역할을 수리 도구로 바꾸지 않았다.
- Notebook: 열람, 기록 저장, 잠금 변경의 서로 다른 조건을 보존했다. 편집 잠금 해제 조건을 잠금 변경 자체에 확대하지 않았다. 연료와 불쏘시개를 결합할 때 점화 도구가 연료에도 필요한 것처럼 읽히던 영어를 수정하고 Notebook·의류·기술서의 최종 원문을 다시 읽었다.
- 의류/Molotov: 의류 세척의 피·때 제거와 젖음은 명시적 결과 관계로 묶었다. Molotov는 입력의 차량 밖 투척 공격을 표현하고 별도 화염 효과를 발명하지 않았다.
- Candle/CandleLit: 점화·소화와 연소 상태를 구별하고 바닥 배치와 용기 이동의 획득 대안을 유지했다.
- 창낚시: 미확정 14건의 마모와 낚시를 독립 서술했다. 어휘에 섞여 있던 근거 없는 마모 인과를 제거했다.
- 기술서/Fertilizer/Cigarettes/WaterPot/Bellows: 기술별 배율과 최대값, 성장과 과다 시비 부패, 흡연가 여부의 상반된 효과, 음용 독성 조건, 화로의 열과 지구력 소모를 해당 조건 아래에 남겼다. 효과 전체를 일괄 상세 배치하지 않았다.
- 차량 부품·지면 작업·총기 기능: 설치할 빈 자리와 제거할 장착 부품, 연료 탱크/좌석의 비움 조건, 엔진 상태, 작업별 국소 조건을 구별했다. 공통 작업 표현에서 서로 다른 조건이 전체 목록에 걸리지 않도록 했다.

최종 Plank compact:

> 건축·금속 가공·목공에 쓰는 재료이며, 차량 밖 근접 공격, 머리·몸통 외 골절의 부목 적용에 쓰거나 연료로 소모할 수 있다.

> It serves as a material for construction, metalworking, and woodworking, can be used for melee attacks outside a vehicle and splinting fractures outside the head and torso, and can be consumed as fuel.

그 expanded에는 “가구 부품·부목 제작에 재료로 쓰인다. 이때 선택한 제조법의 재료·도구와 필요한 제작 지식을 갖춰야 한다.” / “It serves as a material for furniture-part and splint crafting. The selected recipe requires its materials, tools and any required recipe knowledge.”처럼 상세 용도를 실제 문장으로 남겼다. 참조만 보존한 것이 아니다.

최종 Notebook compact:

> 필기구 없이 메모를 읽을 수 있다. 쓰려면 필기구와 편집 권한이 있고 편집 잠금이 풀려 있어야 한다. 연료나 불쏘시개로 소모할 수 있으며 불쏘시개로 쓸 때는 점화 도구가 필요하다.

> Notes can be read without a writing implement. Writing requires an implement, editing access and an unlocked note. It can be consumed as fuel or as tinder with an igniter.

잠금 변경 expanded는 즉시 적용/쪽 편집 취소로 복원되지 않음과 조작 접근 조건을 별도로 설명한다. 원문 전체 및 exact 의미 연결은 같은 결과 파일에서 재생성 없이 검수한다. 위 사례는 고정 정답 문장이나 새 승인 gate가 아니다.

## 한계와 종료 범위

최초 완료 보고 뒤 감독 검토에서 CandleLit의 대상/수단별 점화 반복과 WaterPot의 실행·수치 설명 누적이 남아 있다는 지적을 받았다. 이를 실제 화면 측정의 문제로만 남긴 완료 판단을 정정하고 공통 내용 배치 규칙을 수정했다. 점화 도구 9개와 물 용기 49개에 적용했으며, CandleLit/Lighter/Matches와 WaterPot/WaterSaucepan/WaterBottleFull/BucketWaterFull의 최종 KO/EN을 다시 읽었다. 특정 FullType 대체 문장은 추가하지 않았다.

점화 개요는 하나의 도구 목적과 실제 대상들로 조합한다. 휘발유/불쏘시개별 대상, 화로와 드럼의 차이, 소모 여부는 실제 expanded에서 확인했다. CandleLit의 첫 문장은 “바비큐·모닥불·통나무 드럼·벽난로·연료가 있는 화로·시신·초의 점화에 쓰는 도구다.” / “It is a tool for lighting barbecues, campfires, drums containing logs, fireplaces, fueled furnaces, corpses, and candles.”이다. 최종 compact의 다음 문장은 “손에 들거나 장착한 상태에서 휴대 조명을 조작할 수 있다.” / “It offers portable-light controls while held or attached.”이다.

후속 감독 검토의 조명 자체 상태 전환 지적도 반영했다. 점화·소화 제작법과 손에서 빼거나 버릴 때의 형태 변경을 공통 운영 상세로 배치하고, 휴대 조명 조작 기능이 있는 물품의 활성화 토글 및 건전지 삽입/제거·충전 절차도 상세에 뒀다. Candle/CandleLit/Lighter/Torch/HandTorch의 영향을 받은 KO/EN 원문을 읽었다. Torch/HandTorch compact에는 휴대 조명 조작과 전자 부품 회수 기능이 남고, 건전지별 조건은 실제 expanded에서 확인했다. 초의 발광은 현재 상태에 달려 있다는 상세를 유지하며 항상 빛난다는 기능을 새로 주장하지 않았다. 테스트는 같은 전체 결과에서 조명 운영 fact가 compact에 중복 누적되지 않으며 expanded에 보존되는지도 확인한다.

최종 WaterPot compact:

> 물을 보관·운반하며, 담긴 물은 작물 급수·차량 혈흔 세척·소화·갈증 해소에 쓸 수 있다. 오염된 물을 마시면 중독될 수 있다. 조리 재료 추가에 쓰는 바탕 재료다.

> It can store and carry water for crop watering, washing vehicle bloodstains, fire extinguishing, and quenching thirst. Drinking tainted water can cause poisoning. It is a preparation base for adding cooking ingredients.

중독 20/질병 0.3 경계, 쌀·파스타 준비, 물 저장 시설 보충은 참조에만 숨기지 않고 expanded 원문에서 확인했다. 최종 집중 검사는 같은 전체 결과에서 점화 목적의 반복 제거와 수단 분기를 개요에 잘못 확대하지 않음, 중독 상세의 실제 문장 보존도 확인한다. 상태 분포는 위 표와 동일하다. 이 수정까지 포함한 결과를 문제 3에 인계한다.

실제 PZ 폰트·폭·viewport에서 측정하지 않았다. `physical_fit`은 미측정으로 기록했고 logical slot 수나 임의 글자 수로 최대 네 줄 충족을 주장하지 않는다. CandleLit·물 용기·다기능 도구처럼 용도가 많은 설명의 실제 화면 적합성은 기존 B 책임에서 확인한다. 문제 3에는 전체 원문 품질 검수가 남아 있다.

입력 blocks, r6 producer/adoption/current route, Lua·UI·adapter·package는 이번 작업에서 변경하지 않았다. 기존 dirty 변경은 보존했다. 문서상 owner approval은 사용자의 사전 승인으로 충족했으며 별도 reviewer gate나 증명 artifact를 추가하지 않았다. 필수 성공 조건이 충족되어 추가 confidence 검사 없이 이 범위로 종료한다.
