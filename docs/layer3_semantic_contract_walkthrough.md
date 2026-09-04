# Iris Layer 3 Semantic Contract Walkthrough

> 작성일: 2026-09-04
> 대상: 현재 세션의 DVF-L3-01 구현, 검토 정정 및 상위 문서 정리
> 상태: 계약 채택 완료 / 실제 corpus·runtime 전환은 후속 범위

## 1. 결과와 문서의 역할

Iris Layer 3가 아이템 하나를 대표 용도·대표 역할 하나로 축약하지 않고 복수의 의미 사실을 표현할 수 있도록 successor semantic contract를 구현하고 current semantic authority에 연결했다. 이번 작업은 계약과 그 채택 경로를 완성한 것이며, 기존 아이템 데이터를 새 모델로 이관하거나 게임 내 표시를 바꾼 작업은 아니다.

이 Walkthrough는 변경 내용을 이해하기 위한 설명 문서다. 새로운 validation authority, approval gate, seal 또는 완료 증거를 만들지 않으며, 기존 [계획](/C:/Users/MW/Downloads/coding/PZ/docs/iris_dvf_layer3_multi_meaning_information_resolution_successor_contract_plan.md), [human contract](/C:/Users/MW/Downloads/coding/PZ/docs/iris_dvf_layer3_multi_meaning_information_resolution_successor_contract.md), [closeout](/C:/Users/MW/Downloads/coding/PZ/docs/iris_dvf_layer3_multi_meaning_information_resolution_successor_contract_closeout.md)을 대체하지 않는다.

## 2. 의미 모델에서 달라진 점

- Exact case-sensitive `FullType` 하나에 `0..N`개의 typed fact를 허용하고 stable `fact_id`로 개별 사실을 식별한다. 직렬화 순서는 의미의 우선순위가 아니다.
- `use_context`는 복수로 존재할 수 있다. `context_role`은 아이템 전체의 대표 역할이 아니라 정확히 하나의 context에 속한다.
- `condition`과 `constraint`는 적용 대상 fact를 명시한다. 표현을 짧게 만든다는 이유로 사실의 참·거짓을 바꾸는 조건을 분리하거나 잃지 않는다.
- Semantic fact, provenance, investigation/coverage, approved expression, presentation을 독립 축으로 유지한다. 문장이 있다는 이유로 조사가 완료된 것으로 판정하거나 기존 출력에서 새 사실을 역으로 만들지 않는다.
- Context/role vocabulary는 확장 가능한 versioned vocabulary로 정의했다. 호환되는 token 추가와 의미 정의·경계 변경을 구분하며, 전체 vocabulary를 이번 단계에서 확정하지 않았다.

`identity_hint`, `primary_use`, `secondary_use`, `special_context`, selected role/profile 및 single core 등 predecessor 요소는 inventory에서 유지·대체·유예 경계를 명시했다. 기존 문장을 source 재확인 없이 successor typed fact로 자동 승격하지 않는다.

## 3. 계층과 표시 책임

| 구분 | 채택한 책임과 경계 |
| --- | --- |
| Layer 3 | Broad activity/context, context-local role, function/effect, state, condition/constraint, acquisition result |
| Layer 4 | Exact Recipe/Right-click/EvolvedRecipe identity와 relation-local target/result/requirement |
| Menu Layer 3 | Accepted facts와 resolved acquisition을 expanded detail로 보존 |
| Tooltip S2 | 같은 fact authority에서 first-contact 목적의 낮은 해상도로 투영하고 필요한 fact/dependency reference를 보존 |

Layer 3와 Layer 4는 같은 upstream source를 독립적으로 사용할 수 있지만 상대 계층의 rendered output을 fact source로 삼지 않는다. S2 역시 importance·frequency·efficiency·첫 ordinal 또는 profile label을 대표 fact 선택의 근거로 사용하지 않는다. Runtime에서 요약·축약·재선택·추론하는 경로를 추가하지 않았다.

기존 S1/S3/S4 ownership과 `0..4` logical-row 구조는 유지한다. 다만 구체적인 S2 fact 결합, 표현, 문장/줄 구성, omission tracking까지 predecessor 규칙으로 고정하지는 않았다.

## 4. 검토 후 정정한 두 경계

### Acquisition 축 완료와 item 전체 조사 완료

Acquisition은 모든 current Layer 3 대상의 필수 조사 축이며 `resolved`, `investigated_unresolved`, `not_investigated`를 구분한다. `resolved`는 acquisition 축 완료만 뜻한다. 다른 필수 조사 축의 완료까지 보장하지 않으므로 item 전체 investigation completion과 분리했다.

계약과 casebook의 acquisition-axis/item-level completion 표기를 맞추고 기존 focused test에도 이 구분을 반영했다. Item 전체 조사 완료 조건의 소유자는 DVF-L3-02다. 확인된 acquisition은 Menu에 보존하지만 모든 Tooltip S2에 반드시 문장으로 넣도록 요구하지 않는다.

### Profile과 실제 S2 구성의 재량

Profile은 investigation/composition/first-contact axis scope를 제공할 수 있다. 대표 fact·role 선택과 semantic priority 부여는 금지하지만, `sentence_count`와 `tooltip_s2_selection` 자체를 포괄적으로 금지하던 표현은 제거했다.

실제 S2 fact 조합·KO/EN 표현·문장/줄 구성·omission tracking은 DVF-L3-05에 남겼다. 이 정정은 대표 선택을 허용한 것이 아니라, 의미 우선순위 금지와 후속 표시 설계의 책임을 구별한 것이다.

## 5. 파일별 구현 구성

| 파일 또는 위치 | 이번 세션에서의 역할 |
| --- | --- |
| `docs/iris_dvf_layer3_multi_meaning_information_resolution_successor_contract.md` | 사람이 읽는 채택 계약 |
| `Iris/_docs/authority/dvf/layer3_successor/contract.json` | 의미 모델·축·참조·표시 경계의 기계 판독 계약 |
| 같은 디렉터리의 `casebook.json` | 허용 사례와 금지·경계 사례 |
| 같은 디렉터리의 `predecessor_inventory.json` | 기존 필드 disposition, baseline과 보호 대상 identity |
| 같은 디렉터리의 `contract_manifest.json` | 위 네 member를 하나의 계약 bundle로 결속 |
| `Iris/_docs/authority/iris_current_authority_manifest.json`, `iris_current_route_index.json` | 기존 current 경로에서 successor contract manifest를 연결 |
| `Iris/build/description/v2/tests/test_layer3_successor_contract.py` | 단일 focused G1 test 구현 |
| `Iris/validation/execution/required_validations.json` | G1의 required validation identity 한 건 등록 |
| `Iris/_docs/round3/round3_pytest_source_classification.json` | 기존 pytest discovery policy에 같은 test source 등록 |
| 기존 plan과 closeout | 실행 중 확인된 collection 전제, 최종 결과와 완료 주장 범위 기록 |

Current manifest identity는 기존 contract manifest와 closeout에서 관리한다. 이 설명 문서를 위해 별도 manifest나 digest를 만들지 않았다.

이후 상위 문서 세 개도 2026-09-04 기준으로 정리했다. [DECISIONS.md](/C:/Users/MW/Downloads/coding/PZ/docs/DECISIONS.md)는 채택 결정과 정정 사항, [ARCHITECTURE.md](/C:/Users/MW/Downloads/coding/PZ/docs/ARCHITECTURE.md)는 계약과 실제 제품 구현의 경계, [ROADMAP.md](/C:/Users/MW/Downloads/coding/PZ/docs/ROADMAP.md)는 DVF-L3-01 완료와 후속 문제 2~6을 구분한다.

## 6. 실제 실행한 검증

계획의 단일 focused G1을 사용했다. 최종 채택 명령은 다음과 같다.

```powershell
uv run --project .\Iris\tooling --no-sync pytest .\Iris\build\description\v2\tests\test_layer3_successor_contract.py -q --round3-contract=diagnostic --round3-additional-source=Iris/build/description/v2/tests/test_layer3_successor_contract.py
```

검토 정정 후 마지막 실행 결과는 **exit `0`, `1 passed` in `0.18s`**였다. Pytest cache 쓰기 권한 warning 한 건은 closeout에 기록했다. 장기 실행이나 무한 루프는 관찰되지 않았다.

최종 PASS까지의 수정 경로는 다음과 같다.

1. 새 test source 미분류로 collection 전에 실패했다. 기존 Round 3 source policy에 planned current source로 등록하고 계획의 수정 범위에도 반영했다.
2. 기본 current collection이 이 test에서 소비하지 않는 외부 output seed를 요구해 configure 단계에서 실패했다. 기존 diagnostic/additional-source collection 경로를 채택 명령에 명시했다. Source의 current 분류와 required validation identity는 유지했다.
3. Test 본문이 PowerShell 문화권 정렬과 명시된 ordinal 정렬의 digest 불일치를 검출했다. Ordinal 기준으로 inventory와 관련 manifest/readpoint를 정정했다.
4. G1이 `1 passed` in `0.15s`로 종료했고, 위 두 의미 경계의 검토 정정 후 같은 G1이 `1 passed` in `0.18s`로 다시 종료했다.

G1은 계약 구조·casebook·bundle 결속·기존 제품 보호 경계를 검사한다. 실제 corpus의 의미 조사 완료를 판정하는 범용 validator가 아니다. Full repository suite, current-required runner 전체, Lua syntax, package/install, 실제 PZ 관찰은 이 작업에서 실행하지 않았다. 별도의 independent-review gate도 신설하지 않았다.

위 PASS는 계약 구현과 검토 정정 시점의 실행 결과다. 이후 상위 문서 정리와 이 Walkthrough 작성에서는 테스트를 재실행하지 않았으며, 과거 PASS를 새 문서 수정 후의 재실행 결과로 표현하지 않는다.

사용자의 후속 Git 반영 요청에서는 현재 브랜치가 이미 `main`임을 확인했다. 새 test source의 추적 전환에 맞춰 기존 discovery binding을 tracked 50 / approved absent 0으로 갱신하고, `.gitattributes`에 contract bundle과 human contract의 exact byte 보존 규칙을 추가했다. 이 커밋 준비에서도 추가 테스트는 실행하지 않았다.

## 7. 보존한 제품과 후속 작업

기존 Layer 3 facts/decisions 각각 2,105건, Tooltip owner input의 fact 2,048건과 explicit absence 175건은 유지했다. G1은 계획에 지정된 facts/decisions, owner input, current pointer와 선택된 generation, 두 Lua consumer의 보호 identity를 확인했다. Corpus·생성물·runtime·package migration은 수행하지 않았다.

후속 책임은 다음과 같다.

- **DVF-L3-02:** Profile applicability, 조사 축, item-level investigation completion, first-contact axis.
- **DVF-L3-03/04:** 각각 semantic facts와 acquisition facts의 실제 조사·구축.
- **DVF-L3-05:** 두 facts 집합에 기반한 Menu/S2 구성, KO/EN 표현, 문장/줄 구성과 omission tracking.
- **DVF-L3-06:** Runtime 통합과 current adoption.

따라서 이번 세션은 **DVF-L3-01의 계약 채택 계획을 완료**했다. 문제 2~6은 미완료된 G1의 보충 검증이 아니라 별도 후속 구현이며, 게임 내 표시 개선 완료나 freeze/release readiness는 이번 완료 주장에 포함하지 않는다.
