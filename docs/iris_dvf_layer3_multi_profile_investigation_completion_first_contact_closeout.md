# DVF-L3-02 closeout

- 상태: **complete** — 조사 기준·전체 target 적용 및 잔여 추적·investigation authority 채택.
- 실행일: 2026-09-04.
- 계획: `docs/iris_dvf_layer3_multi_profile_investigation_completion_first_contact_plan.md`.
- 실행 시작 HEAD: `47a44ddae53124bffd09ebafaa4b2aea0f924d59`.
- 실행 시작 dirty: 위 계획 문서 한 건이 untracked였다. 기존 사용자 내용은 보존하고 구현 상태만 갱신했다.
- Owner approval: 이번 실행 프롬프트의 계획/문서 gate 사전 승인. 이 계획은 별도 외부 reviewer를 요구하지 않으며 외부 review PASS를 주장하지 않는다.

## 구현과 채택

`Iris/tooling/src/iris_tooling/domains/layer3/investigation.py`에 exact target 도출, 원본 source 적용, 복수 profile routing, scoped axis/contributor union, pending/gap/완료 계산과 accepted result 소비 경계를 구현했다. 기존 Layer 3 CLI에는 `investigate` 진입점만 추가했다. 실제 실행 명령은 다음과 같다.

```powershell
uv run --project .\Iris\tooling --no-sync python -m iris_tooling --repository-root . build layer3 investigate
```

Writer의 출력은 investigation root의 evidence/application/manifest로 고정되어 있다. 기존 composer·publisher 호출이나 임의 product output 옵션은 없다. Definition 작성과 실제 적용 과정에서 원본 moveable 호출 receiver를 교정했다. 초기 writer 호출의 repository-root 누락과 원본 호출 형식 불일치는 작성 중 교정했고, 두 실패 모두 application 작성 전에 중단됐다. 이는 테스트 실행이 아니다. Candidate를 다듬은 뒤 동일 root에 최종 application 한 벌을 작성했으며 A/B 산출물이나 preflight gate는 만들지 않았다.

채택 readpoint는 `Iris/_docs/authority/dvf/layer3_investigation/manifest.json`이다. 최종 subject manifest SHA-256은 `47be8947a0b18745560b1e7e2463adbe86ab878e5e9fefd461f2a838c164290e`다. Manifest는 contract/evidence/application/human contract 네 member와 상속 authority, target source identity를 결속한다. `status=adoption_subject`는 검증 대상의 고정 표시다. 최종 current route의 `state=adopted`와 이 closeout의 실제 G1 성공이 채택 결과를 설명하며 manifest가 검증 PASS를 스스로 발급하지 않는다.

Current authority manifest와 route index에 `layer3_investigation_contract` 연결 한 건을 추가했고 기존 readpoint/product locator는 보존했다. Required registry에는 focused test identity 한 건, 기존 source policy에는 해당 source와 현재 owner 승인 근거를 추가했다. Source policy의 tracked denominator는 50→51이며 기존 guard를 바꾸지 않았다. 새 test source는 `git add --intent-to-add`로 추적 목록에 등록했다. Commit은 만들지 않았고 기존 staged 내용도 없었다.

## 실제 적용과 내용 판단

Facts/decisions의 exact target은 각각 2,105개이며 duplicate/missing/extra 없이 일치한다. Set SHA-256은 `122ca07c483ff8e4af9ef83bfb8d28c950802a124aba1668c234bce3477b2fdb`다. Registry revision 1은 열 개 프로필과 다섯 조사 axis를 정의하고 32개 source 파일의 bytes를 결속한다. 프로필 수는 질문 차이의 결과이며 향후 quota가 아니다.

| 프로필 | 적용 확인 | 근거 있는 native 배제 | 적용 미정 |
|---|---:|---:|---:|
| direct | 2,105 | 0 | 0 |
| ingestion | 476 | 1,625 | 4 |
| combat | 161 | 1,940 | 4 |
| wearing | 548 | 1,553 | 4 |
| storage | 69 | 2,032 | 4 |
| reading | 106 | 1,995 | 4 |
| expenditure | 113 | 1,988 | 4 |
| crafting | 326 | 0 | 1,779 |
| cooking | 226 | 0 | 1,879 |
| world_work | 20 | 0 | 2,085 |

배제는 원본 item의 해당 native Type channel에 한정한다. Recipe/EvolvedRecipe/moveable predicate의 부재를 전역 미적용으로 확대하지 않았다. 다양한 적용 사례에서 다음을 확인했다.

- `Base.Apple`: ingestion effects와 cooking role은 서로 다른 첫 이해 질문이다. 섭취 효과만으로 조리 활용을 대신하지 않는다.
- `Base.Dogfood`: 원본 `CantEat=TRUE`가 있어 Type=Food만으로 즉시 섭취·허기 해소를 확정하면 안 된다. Operation/conditions 질문을 유지한다.
- `Base.Hammer`: native combat과 원본 moveable tag가 별도 context를 연다. Static Recipe group 후보는 원본 direct token 확인과 구별하여 crafting 적용을 억지로 확정하지 않았다.
- `Base.Plank`: 원본 Recipe input과 keep 관찰이 모두 있다. Combat과 crafting도 함께 적용되며 대표 역할을 고르지 않는다.
- `Base.Notebook`: reading 적용은 학습 효과를 보장하지 않는다. 낮은 정보량에 최소 fact·용도·문장 수를 요구하지 않는다.
- `Base.Battery`: expenditure와 crafting, direct 질문이 공존한다. Drainable 타입만으로 연료/전원이라는 actual fact를 생성하지 않는다.
- `Base.Bag_Schoolbag`와 `Base.Shirt_Denim`: 수납 기능과 착용 기능의 질문·상세 경계가 구별된다.

First-contact 정의는 축 ID만 나열하지 않고 사용자 질문, 첫 이해에서 필요한 이유와 상세 정보 경계를 포함한다. 사실이 미해결이어도 obligation을 남기며 global acquisition을 전역 Tooltip 문장으로 만들지 않는다. 많은 축을 대표 fact나 줄 수 제한으로 줄이지 않았다. 문장 품질이나 실게임 사용자 이해를 기계 검사로 증명했다고 주장하지 않는다.

## 잔여 상태

**Item complete는 0/2,105다.** 모든 item에 application은 있으나 accepted semantic/acquisition results를 이번 범위에서 공급하지 않았다. Acquisition과 실제 의미 axes는 not_investigated이며 scope/gap은 미해결로 남는다. 이것은 구현·전체 적용·채택 완료와 다른 상태다.

| 정확한 대상/범위 | 영향 질문·부족 근거 | 다음 판단 |
|---|---|---|
| `Base.Bag_PistolCase` | Extracted Container에 대응하는 단일 원본 item declaration을 찾지 못해 여섯 native profile 적용/배제 미정 | 해당 FullType의 upstream 원본과 추출 snapshot을 확인하고 native predicate 재평가 |
| `Base.Lemongrass` | Extracted Food에 대응하는 원본 declaration 부재; ingestion 등 native routing 미정 | 원본 source identity 확보 후 적용 재평가. 이름·기존 prose로 의미를 채우지 않음 |
| `Base.NoiseMaker` | Extracted Weapon에 대응하는 원본 declaration 부재 | 원본과 추출의 동일 subject 확인 후 combat 등 native 질문 재평가 |
| `Base.ShotgunCase1` | `scripts/newBags.txt` L106/L239의 두 원본 선언으로 단일 Type 근거를 확정하지 않음 | 중복 선언의 실제 해석/로드 범위를 확인. Evidence에 두 locator를 보존 |
| crafting 미정 1,779개 | Static index의 부재 또는 원본 direct token으로 검증하지 않은 group/동적 관계 | 각 application의 exact item과 `unverified_recipe_candidates`에서 원본 group·결과·동적 경로 조사 |
| cooking 미정 1,879개 | EvolvedRecipe field 부재가 모든 조리 경로의 부재를 뜻하지 않음 | 각 pending scope의 질문을 원본 조리/Recipe/Lua 경로에 적용 |
| world_work 미정 2,085개 | 확인한 addToolDefinition 밖의 월드 작업/수선·행동 경로 미확정 | 원본 fixing 및 독립 Right-click predicate·대상·조건 조사 |
| 전체 2,105개 | Direct residual 기능과 동적 behavior의 전체 coverage 미확정; accepted semantic/acquisition results 부재 | L3-03/04에서 exact source와 결과 authority를 구축. 기존 질문으로 설명되지 않을 때만 definition gap/question scope extension으로 revision |

총계 이외의 exact 대상·질문·missing/next는 `applications.jsonl`의 `pending_scope_refs`, `required_axes`, `blockers`와 해당 item의 evidence record에 있다. 현재 source coverage의 부족을 프로필 정의 결함으로 자동 분류하지 않고, 반대로 새 질문이 필요한 경우를 source 부족이라는 말로 닫지 않는다. Formal accepted authority 없이 negative acquisition instance를 만들지 않았다. 미래 negative 소비 사례는 합성 fixture이며 current producer none/assignment 0을 바꾸지 않는다.

## G1 실행 결과

실행 시작에 계획이 지정한 28개 보호 파일(상속 manifest·네 member, target/source/owner input, 기존 두 composer, runtime pointer와 선택된 generation members, renderer/assembler)의 path/hash 및 기존 config 보존 부분을 임시 baseline JSON 한 개로 캡처했다. 별도 package/runtime/translation tree census나 외부 경로 조사는 하지 않았다.

실제 두 실행 모두 다음 exact command와 adoption 환경을 사용했다.

```powershell
$env:IRIS_LAYER3_INVESTIGATION_MODE = 'adoption'
$env:IRIS_LAYER3_INVESTIGATION_BASELINE = 'C:\Users\MW\Downloads\coding\PZ\Iris\build\description\v2\staging\investigation\baseline.json'
uv run --project .\Iris\tooling --no-sync python -m pytest .\Iris\build\description\v2\tests\test_layer3_investigation_contract.py -q -p no:cacheprovider --round3-contract=diagnostic --round3-additional-source=Iris/build/description/v2/tests/test_layer3_investigation_contract.py
```

1. 첫 G1: exit `1`, `1 failed, 24 subtests passed in 1.29s`. 기존 authority entries 중 `path`가 없는 항목을 test가 허용하지 않아 `KeyError`로 중단됐다. `e.get("path")`로 기존 형식을 존중하도록 test만 교정했다. 이 실패를 PASS로 취급하지 않았다.
2. 최종 G1: **exit `0`, `1 passed, 24 subtests passed in 1.35s`**. Required source의 단일 test identity가 실제 collect/execute됐다. 전체 명령 wall time 약 2.3초로 정상 종료했으며 장기 실행·강제 중단은 없었다.

두 환경 변수는 각 실행의 `finally`에서 기존 process 환경 값으로 복원했다. 최종 성공 이후 contract/application/manifest/config/top docs/test/implementation을 변경하거나 추가 confidence 검증을 수행하지 않았다. 이 비member closeout과 계획의 완료 상태만 기록했다. 임시 작성 helper와 baseline은 작업 종료 시 제거했으며 authority·정규 validator·영구 proof artifact로 승격하지 않았다.

## 검증 범위와 한계

Validated: exact target/schema/source/registry/상속 binding, 실제 source predicate와 전체 application 한 번 재계산·대조, scope/contributor/conflict/pending 보존, first-contact 참조·obligation, acquisition-only와 sparse 완료·잘못된 terminal/negative 거부, bound result consumer, 작은 사례 결정성, final readpoint/required identity, 기존 config 보존 부분과 보호 파일 불변, 실제 product writer 없이 stub으로 확인한 기존 CLI dispatch.

작성 중 내용 검토: 질문 차이·overlap, native 배제 한계, 다양한 실제 item 사례, 구체 미해결 원인과 first-contact 상세 경계, diff의 계획 범위 및 기존 사용자 변경 보존을 확인했다. 새 validation framework나 외부 reviewer approval을 만들지 않았다.

Unvalidated/out of scope: 실제 semantic/acquisition 전수 정확성·완전성, 모든 item complete, source snapshot의 정확한 upstream build, KO/EN 자연성·S2 한 줄 적합성·Menu/Tooltip 의미 구현·실게임 이해도, full repository suite/current-required 전체/L3-01 전체 재실행/Lua syntax, package/install/PZ/compatibility·release readiness. Current corpus·runtime·product migration은 수행하지 않았다.
