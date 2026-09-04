# Implementation Plan — Iris DVF Layer 3 실제 의미 조사와 질문별 조사 결과 구축

- **문제 ID:** `DVF-L3-03`
- **작성일:** 2026-09-04
- **상태:** complete — 2026-09-04 off-live L3-03 구현·채택 완료 / A1·B1·C2 유지 / 최종 G1 exit 0
- **실행 결과:** [단일 closeout](iris_dvf_layer3_semantic_investigation_question_results_closeout.md). 이하 준비·검증 문구는 채택 전 계획이며 실제 실행과 실패 수정 이력은 closeout을 따른다.
- **양식:** `docs/PLAN_TEMPLATE.md`
- **입력:** 사용자 제공 「Iris DVF Layer 3 실제 의미 조사와 질문별 조사 결과 구축 종합 Roadmap」
- **검토 반영:** 사용자 제공 「Implementation Plan Review — 종합본」의 key identity 정정과 기술적 보완을 반영한다. FAIL/WARN severity 차이를 검토 합의로 바꾸지 않는다.
- **이번 수정 기준:** 사용자 요청에 따라 필수 입력 손상과 조사 근거 부족을 구분하고 B1의 사용자 관점 의미 기준을 보강한다. 종전 G0~G4와 독립 process A/B 의무는 이 계획의 단일 최종 G1으로 대체한다. 조사·admission의 깊이는 유지하되 중복 실행·증명 절차는 줄인다. 과거 로드맵의 실행 절차를 이번 수정과 함께 이중 적용하지 않는다.
- **코드 조사 기준:** HEAD `1eade326de0618d0146afefbb488073cc5841ae9`와 작성 시점 작업 트리. HEAD만으로 작업 트리 전체의 무결성을 주장하지 않는다.
- **선행 authority:** DVF-L3-01 successor semantic contract, DVF-L3-02 investigation authority

## 1. Objective

Exact case-sensitive FullType 2,105개를 대상으로 DVF-L3-02가 정의한 조사 질문을 실제 source 조사로 실행하고, 확인된 비획득 의미를 typed semantic facts와 provenance로 구축한다. 각 `(item_id, axis_id, scope_ref)`의 조사 결과를 fact와 별도로 기록하며 applicability / pending / gap을 실제 근거에 따라 갱신한다.

실행 결과는 successor resolver가 직접 소비할 수 있는 off-live semantic-result authority다. 하나의 item에 `0..N`개의 fact와 복수 context를 허용하며, 하나의 fact가 여러 질문에 답할 수 있게 한다. Fact 존재, 질문 전체의 해결, item 전체 조사 완료를 각각 구별한다.

이 문서는 실행 계획이다. 실제 semantic corpus 생성, authority 채택 또는 current product 전환을 수행했다는 기록이 아니다.

---

## 2. Scope

- 비획득 조사축 `operation`, `effects`, `role`, `conditions`의 실제 조사.
- 비획득 fact kind `use_context`, `context_role`, `direct_function`, `effect`, `state`, `condition`, `constraint`의 candidate 생성·admission·accepted corpus 구축.
- Raw source → derived observation → interpretation → semantic proposition → accepted fact lineage.
- Question-level result, 다대다 fact binding, scope coverage, negative evidence, unresolved / uninvestigated 이력.
- Native script, Static Recipe, Recipe group, dynamic cooking, fixing, world-work, 독립 Right-click, residual dynamic route 조사.
- 네 source anomaly의 개별 disposition과 추가 source의 exact identity 결속.
- 필요한 최소 question/scope revision, applicability 재계산, denominator carry-forward.
- 기존 resolver의 structured input 소비, final census와 successor readpoint 결속.

### Explicitly Out Of Scope

- Current facts/decisions, composer, generation, current pointer, Menu/Tooltip text, KO/EN, Lua runtime, package 및 product locator 변경.
- Acquisition fact 생산·해결은 DVF-L3-04, 표현·S2 구성·omission은 DVF-L3-05, runtime/product adoption은 DVF-L3-06 이후 책임이다.
- Layer 4 Recipe / Right-click / EvolvedRecipe ownership 변경, exact relation 목록의 Layer 3 복제.
- Pulse 또는 다른 모듈의 코드 변경, 전체 아키텍처·검증 체계 개편.
- 작업 시작 전부터 존재하는 문서 삭제를 이번 계획 작성 과정에서 복원·정리하는 작업.

---

## 3. Non-Goals

- 모든 item에 최소 fact 수, 대표 용도, 대표 역할 또는 설명 문장을 채우지 않는다.
- Profile, native Type, Recipe token, classification, predecessor prose를 semantic fact로 자동 승격하지 않는다.
- 추천·효율·우열·중요도·빈도·대표성 판단을 생산하지 않는다.
- Pending을 숫자상 0으로 만들기 위해 질문을 삭제하거나 source 부족을 N/A로 바꾸지 않는다.
- 전체 2,105 × 4축이 균일한 질문 격자라고 가정하지 않는다. 실제 질문 수는 scope와 contributor union에 의해 결정된다.
- 정확한 upstream PZ build, 전체 dynamic behavior coverage, 실제 게임 실행 결과, release readiness를 주장하지 않는다.
- L3-01/L3-02의 채택 자체를 재개방하거나 전체 profile taxonomy를 다시 설계하지 않는다.

---

## 4. Assumptions

### 4.1 Authority와 현재 작업 트리

`docs/Philosophy.md`의 근거 기반 정보·추측 금지·중립성·Layer 경계를 최상위 기준으로 삼는다. `docs/DECISIONS.md`의 DVF-L3-01/02 결정, `docs/ARCHITECTURE.md`의 Layer 3 successor/investigation 경계, `docs/ROADMAP.md`의 후속 책임 분리를 따른다.

`docs/EXECUTION_CONTRACT.md`의 claim/evidence 결속, validation ceiling, historical trace와 임시 실행물 수명 규칙을 적용한다. Heavy 분류를 이유로 무관한 전체 검증이나 저장소 전체 snapshot 절차를 추가하지 않는다.

작성 시 확인한 manifest identity는 다음과 같다.

| Readpoint | SHA-256 |
|---|---|
| `Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json` | `6735c3eadafaf4c4fd51ae56c8d0748d32903ee996d53ed43bca38822cf0932a` |
| `Iris/_docs/authority/dvf/layer3_investigation/manifest.json` | `47be8947a0b18745560b1e7e2463adbe86ab878e5e9fefd461f2a838c164290e` |

L3-02 manifest의 `status=adoption_subject`는 검증 subject 표기다. `DECISIONS.md`와 current route의 채택 상태를 무시하여 미채택으로 판정하지 않는다.

**복원 확인 (2026-09-04):** 사용자가 다음 계약 문서 두 개를 복원했다. 각 파일의 SHA-256이 해당 manifest의 member binding과 일치함을 확인했다.

- `docs/iris_dvf_layer3_multi_meaning_information_resolution_successor_contract.md`
- `docs/iris_dvf_layer3_multi_profile_investigation_completion_first_contact_contract.md`

두 manifest에 등록된 member 총 8개의 존재와 SHA-256 일치 검사도 당시 exit `0`으로 완료했다. 따라서 당시 계약 문서 누락 장애는 해소됐다. 이 기록은 이번 구현 subject의 검증 성공이 아니다. 실행 준비 시 필요한 binding 확인과 baseline 캡처는 한 번의 읽기·준비 작업으로 수행하고, 별도 선행 Gate나 기존 계약 재채택 절차를 만들지 않는다. 실제 결속·보호 상태 판정은 최종 G1에 합친다.

**검토 반영 시 재확인 evidence:** 2026-09-04, 작업 디렉터리 `C:/Users/MW/Downloads/coding/PZ`, HEAD `1eade326de0618d0146afefbb488073cc5841ae9`의 작업 트리에서 아래 PowerShell 명령을 실행했다. 검증 subject는 위 두 exact manifest와 각각에 기록된 member path/hash 총 8개다. 결과는 `Checked manifests=2; members=8`, 위 HEAD 출력, exit `0`이다. 다른 dirty 파일과 전체 저장소에 대한 검증 claim은 포함하지 않는다.

```powershell
$ErrorActionPreference = 'Stop'
$expectedManifests = @{
    'Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json' = '6735c3eadafaf4c4fd51ae56c8d0748d32903ee996d53ed43bca38822cf0932a'
    'Iris/_docs/authority/dvf/layer3_investigation/manifest.json' = '47be8947a0b18745560b1e7e2463adbe86ab878e5e9fefd461f2a838c164290e'
}
$memberCount = 0
foreach ($manifestPath in ($expectedManifests.Keys | Sort-Object)) {
    if ((Get-FileHash -LiteralPath $manifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne $expectedManifests[$manifestPath]) { throw "Manifest mismatch: $manifestPath" }
    $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    foreach ($member in $manifest.members) {
        if ((Get-FileHash -LiteralPath $member.path -Algorithm SHA256).Hash.ToLowerInvariant() -cne $member.sha256) { throw "Member mismatch: $($member.path)" }
        $memberCount++
    }
}
if ($memberCount -ne 8) { throw 'Unexpected member count' }
'Checked manifests=2; members=8'
git rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'HEAD lookup failed' }
```

### 4.2 코드와 저장 corpus에서 확인한 baseline

아래 수치는 저장된 `applications.jsonl`을 읽어 집계한 값이며 새 source 재생성·의미 검증 결과가 아니다.

| 항목 | 작성 시 확인값 | 실행 시 처리 |
|---|---:|---|
| Exact target | 2,105 | Facts/decisions/application 집합과 digest 재대조 |
| 전체 required key | 10,987 | Acquisition 포함 baseline |
| 비획득 required key | 8,882 | `operation` 3,578 + `effects` 582 + `role` 572 + `conditions` 4,150 |
| Acquisition required key | 2,105 | Item당 한 번, L3-03 결과 생산에서 제외 |
| Item investigation complete | 0 | L3-03만으로 complete 전환 금지 |
| Crafting pending | 1,779 | 해당 item/profile 집합 유지 |
| Cooking pending | 1,879 | Crafting과 겹칠 수 있음 |
| World-work pending | 2,085 | 다른 pending과 합산해 item 완료율로 사용 금지 |
| Native profile pending | 각 4 | combat / expenditure / ingestion / reading / storage / wearing |
| Source registry | 32 files | 28 script + 2 derived JSON + 2 Lua, exact bytes 기준 |

Target set digest는 L3-02 manifest의 `122ca07c483ff8e4af9ef83bfb8d28c950802a124aba1668c234bce3477b2fdb`를 기준으로 재계산한다.

**Pending denominator 주의:** `routes_for()`는 미확정 profile에 빈 `scope_refs`를 반환할 수 있고, `resolve_item()`은 관찰된 scope에만 required key를 생성한다. 따라서 8,882개 result ledger만 채워도 pending 조사가 끝나지 않는다. 별도의 item/profile pending ledger를 유지하고, scope 확정으로 생성되는 새 key를 revision별 universe에 추가해야 한다. 근거 있는 exclusion으로 key가 더 이상 요구되지 않아도 이전 key와 처분 이력을 삭제하지 않는다.

### 4.3 기존 구현의 재사용 범위와 결손

| 구현 지점 | 현재 동작 | L3-03에서 필요한 일 |
|---|---|---|
| `investigation.py::source_observations()` | Source hash 확인, item declaration/Type 대조, index가 제시한 Recipe token 재확인, moveable alias/tag 관찰 | Source 전체에서 역방향 탐색하여 index false negative 확인. 의미 해석·admission은 별도 구현 |
| `blocks()` | 주석 제거와 brace counting 기반 bounded reader | 문자열/중복 field/반복 clause/간접 group 등 parser capability를 명시하고 손실 없는 observation 보존 |
| `routes_for()` / `merge_routes()` | Applicability와 contributor union, conflict scope 보존 | 실제 조사 disposition을 입력으로 결속하되 기존 범위 계산 의미 보존 |
| `load_result_authorities()` | Explicit path/hash의 adopted payload, source/provenance 결속 확인 | 이 payload 형식을 우선 재사용하고 실제 corpus adapter·candidate 검증 경로 추가 |
| `terminal_result()` | Terminal 결과의 accepted fact·whole-scope coverage·context/qualifier 참조 검사 | 모든 accepted fact를 전수 검증하고 open result의 provenance/attempt도 별도 검사 |
| `resolve_item()` | Results/authorities를 인자로 받을 수 있음 | 실제 fact/result/applicability 입력을 함께 전달하는 offline 경로 연결 |
| `applications()` | `accepted_semantic_results == []`를 요구하며 결과를 공급하지 않음 | Baseline 재현용 경로를 보존하고 result-aware application을 구분 |
| `apply()` / CLI `investigate` | L3-02 고정 root의 evidence/application/manifest를 다시 씀 | L3-03 producer로 그대로 실행하면 안 됨. 별도 result authority의 candidate 출력·채택 경로 필요 |

`terminal_result()`의 open state는 `fact_refs`를 금지하고 조기에 반환한다. 반면 로드맵은 fact가 있어도 question scope가 미해결일 수 있어야 한다. 이 계획의 구현 설계는 별도 `fact_question_bindings`에 partial contribution을 두고, 기존 `result.fact_refs`는 terminal resolution용으로 유지하는 것으로 확정한다. 이는 이미 구현·채택된 field라는 뜻은 아니다. 신규 binding schema는 Change 2에서 계약화하고 검증한다. Binding은 resolver output에서도 추적 가능해야 하며 숨겨진 미소비 sidecar로 남기지 않는다. 기존 terminal/open 의미를 바꾸지 않는 최소 additive extension으로 구현한다.

### 4.4 A1·B1·C2 선택 기록과 단일 실행 기준

2026-09-04 사용자가 지정한 [질의 대상 작업](codex://threads/01a0620a-a4a0-75a0-ba48-d7199bb9485a)에 같은 질문을 전달하여 **A1 + B1 + C2** 답변을 받았다. 사용자의 질문·답변 회수 요청에 따라 이 답변을 본 계획의 단일 실행 기준으로 반영한다. 이는 이번 선택 기록이며, 과거에 상위 로드맵이 이미 세 값을 승인했다거나 검토안의 FAIL/WARN 차이가 해소되어 계획 전체가 PASS라는 뜻은 아니다. 잘못 지정했던 이전 작업의 답변은 근거로 사용하지 않는다.

| 결정 | 확정된 실행 기준 | 한계 |
|---|---|---|
| A1 | 명시·결속된 available-source 범위의 단순 `not_investigated = 0`. Pending 조사와 새로 확정되는 available key도 포함 | 실제 조사했으나 source/engine/dynamic dependency가 부족하면 evidence-bound `investigated_unresolved` 가능. 모든 질문 resolved를 요구하지 않음 |
| B1 | Stratified semantic audit + unique automatic mapping rule 전수 의미 검토 + 고위험 fact의 위험에 맞춘 추가 확인 | 모든 item의 수작업 재검토·외부 reviewer 승인·rule별 새 gate로 확대하지 않음. 표본 성공을 전수 의미 정확성으로 주장하지 않음 |
| C2 | 채택된 L3-02 정의를 참조하는 L3-03 별도 semantic-result authority. Facts/results와 derived application을 함께 결속 | 기존 L3-02 baseline application/writer를 덮어쓰지 않음. 질문/axis/scope/routing 정의 자체의 변경 때만 최소 L3-02 successor revision |

Available-source 분모를 수집 코드 미구현·조사 난도·미수행 때문에 사후 축소하지 않는다. 단순 source 열람이나 상태명 변경도 조사 완료가 아니다. 자료 밖 범위는 source dependency와 영향 item/profile/question을 명시하고 그 범위의 조사 완료를 주장하지 않는다.

B1은 각 고유 규칙의 전제·원본 소비 동작·의미 변환 범위·예외를 검토하고 실제 적용 사례를 층화해 확인한다. 동일 rule의 검토는 명시된 적용 범위에서 공유할 수 있다. Admission과 기존 최종 검증에 연결하며 사례/규칙마다 gate·proof tree·새 검사기를 추가하지 않는다.

의미 검토에서는 원본 호출·필드의 정확한 추출뿐 아니라 사용자가 이해할 기능·효과·활동으로 해석됐는지 확인한다. 서로 다른 용도를 지나치게 합치거나 exact Recipe/행동 목록으로 과도하게 쪼개지 않고, 진실 범위를 바꾸는 조건과 구현상 세부를 구별한다. 이 판단은 기존 B1의 내용 기준이며 별도 심사·Gate가 아니다. 문장 길이·용도 수·fact 수의 공통 하한은 만들지 않는다.

C2의 소비 readpoint는 definition revision → result authority → derived application 관계를 명시한다. Fact 추가, applicability 판정 갱신, 기존 정의 안의 구체 scope instance 추가는 L3-02 정의 개정 사유가 아니다. 새 source가 결과 근거면 result authority에 결속하고, 기존 정의에 결속된 source/규칙을 바꿔야 하면 그 정의 영향과 최소 revision 필요성을 따로 판정한다. 초기 baseline과 최신 결과를 같은 상태의 경쟁 authority로 두지 않는다.

### 4.5 Canonical key와 신규 vocabulary의 경계

Canonical identity는 전 과정에서 `question_key = (item_id, axis_id, scope_ref)`다. `registry_revision`과 `authority_id`는 정의와 결과가 어느 readpoint에 속하는지 검증하는 **별도 metadata**이며 네 번째 key component가 아니다. Contributor union·deduplication·question census는 이 3-tuple을 사용한다. Revision별 snapshot은 별도 record로 보존할 수 있지만 unchanged question을 새 question identity로 세지 않는다.

L3-02 human contract의 axis key 정의와 `investigation.py::resolve_item()`의 item 내부 `(axis_id, scope_ref)` union이 이 경계의 근거다. Scope의 의미가 달라져 새 질문이 되면 새 `scope_ref` 또는 명시적인 scope successor relation을 사용하고, metadata 검증은 구 revision 결과의 무검토 사용을 거부한다.

| Vocabulary | 현재 존재 여부 | L3-03 처리 |
|---|---|---|
| `resolved`, `evidence_backed_not_applicable`, `investigated_unresolved`, `not_investigated` | `investigation.py::STATES`와 L3-02 axis 계약에 존재 | 기존 상태와 terminal/open 의미 재사용 |
| `retained`, `changed`, `superseded`, `newly_required`, `no_longer_required` | 조사한 L3-02 계약/구현에 carry-forward enum으로 정의되지 않음 | 신규 L3-03 lineage relation vocabulary. Change 2/3에서 field·의미·검증을 명시하고 result state와 분리 |
| `fact_question_bindings` | 기존 result 소비 코드에 정식 partial-binding schema 없음 | 이번 계획의 신규 additive relation. Terminal `fact_refs`와 분리 |

신규 vocabulary는 closeout에서 즉석으로 도입하지 않는다. 구현 전 result/lineage 계약으로 정의하고, 실제 authority 채택 시 해당 추가 범위와 계약 readpoint를 결정 기록에 연결한다. 이 어휘를 기존 L3-02 token이라고 설명하지 않는다.

---

## 5. Repository Areas Affected

아래 경로는 **향후 실행 예상 범위**다. 이번 수정 대상은 이 계획서 하나다. `[신규 제안]`의 세부 파일명은 C2 구조와 기존 output policy에 맞춰 구현 시 확정한다.

### Code

- `Iris/tooling/src/iris_tooling/domains/layer3/investigation.py`: result consumption, applicability/result 결속의 최소 보완.
- `Iris/tooling/src/iris_tooling/domains/layer3/cli.py`: 명시적 off-live semantic-result 명령 추가. 기존 `investigate`와 composer dispatch 보존.
- `[신규 제안] Iris/tooling/src/iris_tooling/domains/layer3/semantic_results.py`: source observation/interpretation/admission/serialization의 offline owner. 커지면 동일 domain 내부에서 책임별 분리.
- `[신규 제안] Iris/build/description/v2/tests/test_layer3_semantic_results.py`: 단일 최종 G1 source. 전체 fact/result 무결성, 실제 소비, 변경된 공용 경계의 회귀와 보호 상태를 함께 검증한다. 하나의 public test identity와 내부 helper/subcase로 묶으며 사례 수를 제한하지 않는다.
- 기존 `test_layer3_investigation_contract.py`와 `test_layer3_successor_contract.py`는 보존한다. 전체 재실행을 이번 계획의 별도 의무로 두지 않고, 실제 수정하는 resolver/CLI와 상속 계약의 관련 불변식을 최종 G1에 포함한다. 정의 successor가 필요한 경우에만 그 변경에 직접 영향받는 기대값·참조의 최소 정정을 허용하며 predecessor 보존 요건을 약화시키지 않는다.

읽기 전용 참고: `Iris/tooling/src/iris_tooling/domains/layer4/evolved_recipe.py`, `Iris/tooling/src/iris_tooling/build/build_iris_fixing_index_data.py`. 이들의 public output이나 runtime writer를 L3-03 authority producer로 사용하지 않는다.

### Docs

- `docs/iris_dvf_layer3_semantic_investigation_question_results_plan.md`: 본 계획.
- `[신규 제안] docs/iris_dvf_layer3_semantic_investigation_question_results_contract.md`: A1·B1·C2, result/admission/source coverage 계약.
- `[신규 제안] docs/iris_dvf_layer3_semantic_investigation_question_results_closeout.md`: exact 실행 subject, 검증 결과, census, residual, claim ceiling.
- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`: 향후 실제 채택 시점에만 결과와 후속 책임 반영.

### Config

- `Iris/_docs/authority/dvf/layer3_investigation/contract.json`: 질문/axis/scope/routing 또는 그에 결속된 source/규칙의 정의 자체가 변경될 때만 최소 successor 관리. 새 result evidence는 L3-03 authority에 결속.
- `Iris/_docs/authority/iris_current_authority_manifest.json`, `Iris/_docs/authority/iris_current_route_index.json`: 검증된 L3-03 semantic-result readpoint만 연결. Product locator 보존.
- `Iris/validation/execution/required_validations.json`, `Iris/_docs/round3/round3_pytest_source_classification.json`: 신규 focused source 한 개와 필요한 경우 public test identity 한 건만 기존 소유권·분류 규칙에 맞춰 등록한다. 내부 subcase를 개별 required 항목으로 등록하지 않는다.
- 신규 permanent validator, 별도 검증 registry 또는 full gate 우회 runner는 만들지 않는다.

### Generated Artifacts

C2의 별도 authority root는 `Iris/_docs/authority/dvf/layer3_semantic_results/`로 계획한다. L3-02 baseline root는 보존하고 final result manifest가 해당 definition readpoint와 derived application을 결속한다.

- Final manifest: L3-01/L3-02 readpoint, target/key universe, sources, producer/rule identity, result members 결속.
- Accepted facts, provenance, question results, fact-question bindings, updated applicability/gap application.
- Source capability matrix, 네 anomaly disposition, source dependency/blocker, registry revision carry-forward.
- Final state/axis/scope/fact-kind/blocker census와 검증·review 범위 요약.
- Candidate/rejected/unresolved observation 및 audit 상세는 승인된 candidate/evidence output root에 둔다. 대량 중간자료를 current authority나 runtime tree에 무조건 편입하지 않는다.

위 목록은 필요한 정보의 역할이며 각 항목별 파일·manifest·디렉터리를 만들라는 요구가 아니다. Pending, capability, anomaly, carry-forward는 공통 record와 source/scope 참조를 공유할 수 있고 census는 그 결과에서 계산해 closeout에 요약할 수 있다. 전체 target/profile/source의 불필요한 직교 행렬을 물리적으로 만들지 않는다. 단, exact membership과 포함·제외 이유 및 이력은 재구성 가능해야 한다. 생산용 corpus와 최종 manifest 외에 별도 검증 authority·seal·receipt·gate별 evidence tree를 추가하지 않는다.

**Retention 경계:** Closeout 이후에도 final accepted facts/provenance/results/bindings, source identity와 locator의 재검증에 필요한 원본 또는 exact 재접근 carrier, rule/admission·semantic audit 기록, anomaly/negative/unresolved disposition, universe/carry-forward, final 검증 결과와 manifest는 보존한다. L3-04/05가 사용하는 unresolved candidate/attempt evidence도 downstream dependency가 해제되기 전에는 정리하지 않는다. 외부 evidence root를 사용하면 위치·hash·접근 방법을 final manifest/closeout에 남긴다.

Cache, 임시 observation export와 scratch helper는 retained evidence에서 재생성 가능하고 final provenance·audit·downstream 참조가 없음을 확인한 뒤 기존 output policy에 따라 정리할 수 있다. 실제 source/proposition을 유일하게 입증하는 자료를 intermediate로 분류하지 않는다. 보존/정리 판정은 Change 2에서 artifact class별로 정하고, closeout에서는 그 처분만 기록한다. 시작 baseline은 실행 중 필요한 최소 임시 기록으로 유지하고 G1의 판정 결과·보호 범위를 closeout에 남긴 뒤 제거할 수 있다. 이후 실행에 과거 baseline 재생성을 요구하지 않는다.

---

## 6. Planned Changes

아래 Change는 구현 책임의 분해이며 개별 승인·검증 Gate가 아니다. 정의와 실제 사례를 함께 다듬거나 관련 작업을 합쳐 수행할 수 있다. 각 **Validation** 문단은 최종 G1 또는 작성 중 B1 admission에 포함할 확인 내용을 뜻하며 중간 테스트 실행을 요구하지 않는다. 실제 source 조사·candidate 생성·내용 검토는 작업 자체로 수행하고, 자동 검증은 최종 subject가 준비된 뒤 한 번에 묶는다.

### Change 1 — Exact subject와 source coverage baseline 확정

**Purpose:** 로드맵 Phase 1. 생산 전에 target, 기존 key, pending universe, source 경계와 보호 대상을 고정한다.

**Files:** 두 기존 L3 manifest/member, `investigation.py`, `scripts/`, `lua/`, `Iris/input/`, 신규 baseline/capability 자료.

**Implementation Notes:**

1. 실행 HEAD·dirty 목록·manifest/member SHA-256을 기록한다. §4.1에서 복원·hash 일치를 확인한 두 계약 문서를 포함해 모든 member와 bound source bytes를 실행 subject 기준으로 다시 대조한다.
2. Exact target 2,105개와 8,882개 비획득 baseline key, 2,105 acquisition key, pending item/profile 집합을 각각 재계산한다.
3. 임시 baseline 한 개에 시작 HEAD·dirty와 명시적 보호 경로를 기록한다. 보호 대상은 기존 L3-01/02 manifest/member, current facts/decisions 및 그 입력 manifest·Tooltip owner input, 기존 `compose_layer3_body_profile.py`/`compose_layer3_item.py`, `IrisLayer3DataCurrent.lua`와 선택된 generation members, `layer3_renderer.lua`/`IrisItemDetailModelAssembler.lua`, current authority/route의 기존 product locator 부분이다. 추가 보호는 실제 writer 도달 경로에서 필요한 파일에 한정해 이유를 적는다. Package·전체 runtime/locale tree·외부 설치 경로의 별도 census는 만들지 않는다. Source identity는 생산용 source binding을 재사용한다. Touched/unexpected delta는 시작 dirty와 대조하며 보호 byte 판정과 쓰기 범위 제한의 증거 범위를 구분한다.
4. A~E route별 source 존재·binding 여부·extractor 능력·관찰 범위·semantic 해석 가능 범위·missing dependency·negative를 닫을 수 있는 범위를 기록한다.
5. 32개 bound 파일에 derived JSON 두 개도 포함됨을 명시한다. 파일 수를 raw semantic coverage로 읽지 않는다.
6. `available_source_scope`를 서술문만으로 두지 않고 canonical question key ↔ route ↔ bound source 및 pending item/profile ↔ potential route의 exact membership으로 식별한다. 공통 source/rule 참조와 계산 가능한 membership을 사용할 수 있으며 key마다 중복 source hash를 복사할 필요는 없다. Definition readpoint, source identity, scope revision, 포함·제외 이유와 최종 집계가 대조 가능해야 한다. 초기 목록은 조사에 따라 갱신하는 입력이며 별도 봉인 Gate가 아니다.
7. Partial route는 조사 가능한 구간과 missing source 경계를 분리한다. 추가 source 또는 새 scope로 집합이 변하면 이전 집합을 보존하고 추가/변경 범위와 질문 carry-forward를 기록한다. 조사 난도나 미수행을 이유로 available set을 사후 축소하지 않는다. 신규 available key도 최종 판정 A의 분모에 포함한다.

| Channel | 실제 repository 조사 시작점 | 조사상 제한 / 다음 단계 |
|---|---|---|
| A: native properties | `scripts/items*.txt`, clothing/기타 registry script, `lua/client/ISUI/ISInventoryPaneContextMenu.lua` | Type은 routing용. Property가 실제 소비되는 action/engine 경로까지 확인 |
| B: Static Recipe | `scripts/recipes.txt`, `scripts/recipes_radio.txt`, 기타 script의 recipe block; `Iris/input/recipes_index_full.json`은 검색 seed | 기존 reader는 index 후보에서 출발하므로 raw → index 역대조 필요. Input/keep/destroy/result와 clause를 손실 없이 관찰 |
| C: group / dynamic cooking | `scripts/evolvedrecipes.txt`, `lua/server/recipecode.lua`, `lua/client/TimedActions/ISAddItemInRecipe.lua` | BaseItem, group membership, indirect expansion, cooked 조건, `getItemsCanBeUse()` / `addItem()` 경계 조사 |
| D: fixing / world-work / Right-click | `scripts/fixing.txt`, `scripts/vehicles/vehiclesfixing.txt`, `lua/client/TimedActions/ISFixAction.lua`, `lua/client/Moveables/ISMoveableDefinitions.lua`, `ISMoveablesAction.lua`, inventory context menu | Require/Fixer 관계·target predicate·수선/건설/해체/설치 action 조사. FixingManager 내부 미확인은 별도 blocker |
| E: residual direct / dynamic | Inventory context menu에서 호출하는 action과 추가 item/tag predicate; `lua/client/TimedActions/ISEatFoodAction.lua` 등 | Native profile에 잡힌 item도 residual 조사에서 제외하지 않음. Callback/indirect call와 source 밖 engine 경계를 기록 |

위 경로 중 기존 registry 밖 파일은 **저장소에 존재하는 추가 결속 후보**다. 존재만으로 이미 adopted source라고 취급하지 않는다. Layer 4 코드의 `media/scripts/...` 설치 source 경로와 저장소의 `scripts/...` 경로도 이름만으로 동일 bytes라고 판단하지 않는다.

**Validation:** Target/key uniqueness·set digest·member/source hash 대조, pending 별도 accounting, current product baseline 완전성, source route별 available/partial/missing/conflict/unassessable 분류.

### Change 2 — Fact/result 모델과 authority 갱신 경로 확정

**Purpose:** Phase 2. 확정한 A1·B1·C2에 따라 semantic 사실과 조사 완료를 분리한 구현 계약을 구체화한다. 별도 계약 봉인 Gate 없이 실제 source 사례와 함께 다듬고 최종 G1의 subject로 확정한다.

**Files:** 신규 human/machine result contract, `semantic_results.py`, `investigation.py`, `cli.py`.

**Implementation Notes:**

- Fact는 `fact_id`, `item_id`, `fact_kind`, `status=accepted`, kind-specific `payload`, `provenance_refs`를 가진다. ID는 bundle global이며 재정렬·표현·timestamp·host에 의존하지 않는다. 같은 semantic fact는 deterministic rerun과 무관한 successor revision에서도 같은 `fact_id`를 유지한다. Semantic identity에는 item/kind/payload/context/dependency 의미를 반영하고, 관련 없는 registry/authority revision이나 provenance locator 변경만으로 ID를 재발급하지 않는다. 의미가 바뀐 fact는 explicit replacement/successor lineage로 구별한다. 구체 hash algorithm은 구현 계약에서 정한다.
- **NC1 — 구현 계약에서 확정할 항목:** `fact_id` 도출 방식이 `content-derived`인지 `assigned`인지 한 줄로 명시하고 하나의 방식을 선택한다. 이 계획에서는 도출 방식을 미리 선택하지 않으며 위 semantic identity 안정성 규칙은 유지한다. Payload 정정의 의미 변경 여부와 선택한 방식에 따른 ID 유지/교체 기준, 영향받는 `fact_question_bindings`·terminal `fact_refs`·context/dependency 참조의 무효화·재결속 및 replacement/successor lineage 절차를 함께 계약화한다. Content-derived에서 semantic content 정정으로 ID가 바뀌면 새 ID로 영향 참조를 재결속하고, assigned에서 ID가 유지되더라도 의미 변경을 조용히 덮어쓰거나 기존 terminal 판정을 무검토 승계하지 않는다. 이전 accepted 내용과 binding의 이력은 보존한다.
- `context_role.context_fact_ref`는 같은 item의 accepted `use_context`를 참조한다. `condition/constraint.applies_to_fact_refs`는 같은 item의 non-qualifier fact를 참조한다. 중첩 qualifier와 top-level 중복 표현을 금지한다.
- Provenance는 raw source identity/hash·locator, observation ID, interpretation/rule revision, semantic proposition을 연결한다. Index-level locator만으로 raw source lineage를 끝내지 않는다.
- Result의 실제 상태명은 기존 구현에 맞춰 `resolved`, `evidence_backed_not_applicable`, `investigated_unresolved`, `not_investigated`를 사용한다. 로드맵의 grounded non-applicable은 두 번째 상태에 대응한다.
- Result는 3-tuple `question_key`와 별도 `registry_revision`/`authority_id` metadata, 조사 attempt/evidence, scope coverage, state 전환 사유, blocker와 다음 source dependency를 기록한다. Pending applicability와 question result를 같은 enum/state로 합치지 않는다. §4.5의 기존 result token과 신규 lineage/binding token을 schema에서 구분한다.
- Partial fact contribution은 §4.3의 별도 binding으로 표현한다. Terminal 결과의 `fact_refs`는 whole-scope 증거와 함께만 허용한다. 하나의 fact를 질문 수만큼 복제하지 않는다.
- 미조사 result를 초기화하되 실제 조사 attempt 없이 일괄 unresolved로 바꾸지 않는다. Evidence-backed N/A는 semantic fact로 만들지 않는다.
- 현재 `load_result_authorities()`의 adopted JSON payload 형식(`authority_id`, `status`, `source_bindings`, `facts`, `provenance`, `results`)을 소비 경계로 우선 재사용한다. JSONL corpus를 나눌 경우 manifest-bound deterministic adapter가 이를 구성한다.
- Candidate validator와 adopted loader의 역할을 분리한다. 단지 loader를 통과시키려고 candidate에 `status=adopted`를 먼저 붙이지 않는다.

**Validation:** Invalid/duplicate ID, dangling provenance, cross-item context, qualifier-to-qualifier, invalid kind, partial fact → terminal 오승격, unbound open-result evidence, candidate/adopted 혼용을 거부하는 focused cases.

NC1의 도출 방식 확정 후 최종 G1의 fact ID 안정성 사례를 그 계약에 맞춘다. Unchanged semantic identity의 ID 유지와 semantic payload 정정 시 영향 binding/terminal 판정의 무효화·재결속을 각각 확인한다. Dangling 참조뿐 아니라 이전 의미에 대한 판정이 새 payload에 그대로 살아남는 경우도 거부한다. 별도 test source나 Gate를 추가하지 않는다.

### Change 3 — Question evolution과 denominator carry-forward 구축

**Purpose:** Phase 3. 새 의미와 늦게 확정되는 scope를 조사 누락 없이 반영한다.

**Files:** Investigation contract의 조건부 successor, 신규 universe/carry-forward ledger, result-aware application 코드.

**Implementation Notes:**

1. 발견을 existing question instance / scope extension / definition gap으로 구분한다.
2. Definition 변경 없이 처리할 수 있는 instance는 기존 key에 연결한다. 새로운 context는 기존 context에 합치지 않는다.
3. Extension/gap이면 먼저 기존 정의 안의 구체 instance 확장인지 정의 자체의 변경인지 구분한다. 전자는 L3-03 derived application과 universe revision으로 처리한다. 후자는 source finding → affected item/profile/scope → 최소 L3-02 definition successor → application 재계산 → 새 key universe → carry-forward → 신규 key 조사 순서를 지킨다. Universe revision과 definition revision을 동일시하지 않는다.
4. 이전 key를 `retained` / `changed` / `superseded` / `newly_required` / `no_longer_required` 관계로 보존한다. 이는 신규 lineage vocabulary이며 question/result state가 아니다. Before/after readpoint와 같은 3-tuple의 관계를 별도 record로 표현한다. Unchanged key는 `retained`이며 contributor union과 identity가 유지된다. Scope 의미가 바뀐 경우 새 `scope_ref` 또는 explicit scope successor relation을 요구하고, ID 문자열만 같다는 이유로 결과를 무검토 승계하지 않는다.
5. Confirmed key result, pending item/profile disposition, residual gap을 별도로 대조하여 universe 밖 조사 공백을 감추지 않는다.
6. Predecessor prose는 search seed로만 사용하고 source-confirmed candidate / expression-only / source-conflicting material로 처분한다.

**Validation:** Before/after 3-tuple key census, unrelated revision에서 unchanged key/contributor union/fact ID 보존, source finding 없는 revision 거부, 불필요한 definition revision 거부, unaffected application 불변성, split/merge 영향 범위, late-created key accounting. Revision을 네 번째 key component로 추가한 schema/adapter는 거부한다. 늦게 생성된 available-source key도 A1의 미조사 0 조건에 포함한다.

### Change 4 — A/B channel의 실제 의미 candidate 조사

**Purpose:** Phase 4. Confirmed applicability 질문과 현재 조사 가능한 원본에서 semantic proposition을 만든다.

**Files:** Native/Recipe raw source, 신규 observation/candidate producer와 rule registry, provenance 자료.

**Implementation Notes:**

- 질문 → raw observation → 소비 동작/조건 해석 → proposition → fact kind → candidate 순서를 지킨다.
- `Type=Food` 대신 `CantEat`, 상태 조건, context menu와 action의 실제 검사·호출을 함께 조사한다. `ISEatFoodAction:isValid()`의 보유/요구 item 조건처럼 관찰 가능한 전제와 engine 효과의 미확인 부분을 구분한다.
- `Base.Dogfood` / `Base.DogfoodOpen`은 closed/open 차이를 조사하는 사례다. 모든 Food에 같은 섭취·효과를 자동 적용하지 않는다.
- Recipe는 exact clause의 consume/keep/destroy와 변환 맥락을 확인한 뒤 broad context/local role로 해석한다. `keep` token만 보고 모든 경로에서 동일한 도구 역할을 부여하지 않는다.
- 기존 `fields=dict(...)`의 단일값 관찰에 의존해 중복 property를 소거하지 않는다. Repeated clause, module resolution, 대소문자, slash alternative와 result 참여의 parser 범위를 검증한다.
- `Base.Plank`, `Base.Hammer`, `Base.Apple` 등은 복수 역할/맥락 검토 seed이며 답을 미리 정하는 fixture가 아니다.
- Source가 부족하면 candidate/질문을 unresolved로 보존한다. 출력 분량을 맞추기 위한 fact는 생성하지 않는다.
- 소비 함수명·호출 성공·보유 item 검사 같은 구현 관찰을 그대로 사용자용 기능 사실로 바꾸지 않는다. 확인된 실제 기능·효과·활동과 진실 범위를 바꾸는 조건을 구분해 proposition으로 만들고, 원본 관찰의 나머지 세부는 provenance에 보존한다. 조건을 생략해도 된다는 뜻은 아니며 의미와 evidence의 해상도를 구별한다.

**Validation:** Mapping-rule premise와 source locator 대조, item/context 분리, 비어 있거나 근거 없는 payload 거부, raw/index 불일치, 두 context의 유사 fact를 과도하게 deduplicate하지 않는 사례. Semantic review는 B1의 unique rule 전수 검토와 층화 사례 감사를 따른다.

### Change 5 — C/D/E 확장 조사와 네 anomaly 처분

**Purpose:** Phase 5. 기존 extractor가 충분히 다루지 못한 경로를 조사하고 source 부족과 의미 부재를 구분한다.

**Files:** §6 Change 1의 C/D/E source와 추가 bound source, capability matrix, anomaly/attempt ledger.

**Implementation Notes:**

- C: Recipe group의 정의·membership·indirect expansion, definition-side BaseItem, EvolvedRecipe 참여·cooked/state 조건과 dynamic eligibility를 조사한다. Item-level EvolvedRecipe field나 Food Type 부재만으로 cooking을 닫지 않는다.
- D: Fixing Require/Fixer·skill/target/state 조건, moveable tool/tag, construction/maintenance/dismantle/install 경로를 조사한다. `build_iris_fixing_index_data.py::parse_fixers()`는 fixer FullType 집합만 남기므로 의미 authority로 충분하지 않다.
- E: Native/Recipe와 독립적으로 Right-click 및 residual item/tag/callback 경로를 조사한다. Recipe에서 찾았다는 이유로 Right-click 조사를 생략하지 않는다.
- `ISAddItemInRecipe`의 `getItemsCanBeUse()`·`addItem()`, context menu의 `FixingManager`처럼 engine으로 넘어가는 경계는 확인된 호출·조건과 미확인 내부 의미를 구분한다. 추가 source 확보 실패를 전역 negative로 해석하지 않는다.
- 추가 파일은 exact bytes, 출처/획득 경로, 기존 snapshot과의 관계, 조사에 사용한 locus를 결속한다. 정확한 upstream build가 불명확하면 그 상태를 유지한다.

| Anomaly | 기존 관찰 | 요구 disposition |
|---|---|---|
| `Base.Bag_PistolCase` | 대응 exact item declaration 부재 | 모델/손 모형·다른 FullType 후보와 구별, alias/renaming은 명시적 source 없으면 금지 |
| `Base.Lemongrass` | 대응 exact item declaration 부재 | Case variant나 관련 명칭은 검색 seed. Target identity 보존, source 미확보면 unresolved |
| `Base.NoiseMaker` | 대응 exact item declaration 부재 | DisplayName/model token을 declaration identity로 전용하지 않음 |
| `Base.ShotgunCase1` | `scripts/newBags.txt` L106 및 L239 중복 declaration | 양쪽 declaration 보존. Actual loader 증거 없이 first/last winner를 선택하지 않음 |

각 anomaly는 raw candidate 목록, 확인/미확인 source, 영향 profile/key, terminal 또는 unresolved 사유, 재조사 조건을 가진다. 네 건을 target에서 빼지 않는다.

**Validation:** Route coverage와 미확보 dependency 집합, indirect-call 한계, scoped negative의 bound universe, raw/derived lineage, 네 anomaly 개별 record, 조사 attempt와 state 일치. Available 범위의 단순 미수행은 허용하지 않는다. 자료 밖 범위는 dependency와 영향 집합을 별도 기록하며 실제 시도한 조사만 unresolved로 기록한다.

### Change 6 — Pending / coverage gap applicability 재평가

**Purpose:** Phase 6. 기존 1,779 / 1,879 / 2,085 pending 및 residual gap을 실제 조사 결과에 따라 처분한다.

**Files:** Pending disposition, result-aware applications, capability matrix, 조건부 registry revision.

**Implementation Notes:**

- 각 baseline pending item/profile에 source attempt와 applicable / scoped exclusion / pending-with-blocker / coverage-or-definition-gap disposition을 연결한다.
- Crafting은 direct/group participation·transformation·consumed/keep/require 관계, cooking은 Static Recipe/group/EvolvedRecipe/BaseItem/dynamic predicate, world-work는 tool/target/action chain을 조사한다.
- Native profile별 anomaly pending 각 4건도 포함한다. 세 대규모 pending만 처리하고 anomaly나 residual direct 질문을 빠뜨리지 않는다.
- 새 applicable scope가 생기면 필요한 key를 생성하고 실제 semantic 조사로 이어간다. Exclusion은 해당 channel/scope만 닫는다.
- `assessed_clear`는 evidence reference 존재만으로 충분하다고 간주하지 않는다. Gap 질문에 대응하는 route inventory·coverage·negative 근거를 검증한다.

**Validation:** Baseline pending의 전수 disposition join, overlap-preserving census, 새 key accounting, source 미확보 → N/A 전환 0, 분류용 Type negative → item-global negative 확장 0.

### Change 7 — Candidate admission과 accepted corpus 구축

**Purpose:** Phase 7. 확인된 proposition만 accepted fact로 채택하고 의존 관계를 보존한다.

**Files:** `semantic_results.py`, fact/provenance/rule/disposition corpus, focused tests.

**Implementation Notes:**

- Admission 조건: supporting source exists AND proposition supported AND valid kind AND correct scope AND valid dependencies.
- Accepted되지 않은 candidate는 rejected 또는 unresolved 이유와 재검토 조건을 기록한다. Review metadata를 semantic fact identity와 분리한다.
- Terminal result에 참조된 fact뿐 아니라 **전체 accepted corpus**를 검사한다. 현재 `terminal_result()`의 사용된 fact 검사만으로 전체 corpus 검증을 대신하지 않는다.
- 동일한 의미와 context/dependency를 가진 fact의 질문 기여는 binding으로 합치되, 다른 context의 비슷한 payload는 구분한다.
- Grounded N/A·unresolved는 positive fact로 materialize하지 않는다. 근거가 없으면 0 fact를 허용한다.

**Validation:** Duplicate ID, dangling provenance/dependency, unsupported accepted candidate, invalid payload/kind, global role collapse, qualifier 중복, negative→positive 변환 검사. B1의 unique automatic rule 전수 의미 검토와 위험에 맞춘 fact review를 수행하고 검토 적용 범위를 명시한다.

### Change 8 — Question-level closure와 후속 handoff 결속

**Purpose:** Phase 8. Facts·coverage·negative·unresolved를 exact question key에 결속한다.

**Files:** Question result corpus, fact-question bindings, final applicability/gap application, resolver adapter.

**Implementation Notes:**

- Resolved는 accepted references + whole-scope coverage justification이 함께 있어야 한다. 일부 fact만 확보한 질문은 partial binding과 unresolved result를 병존시킨다.
- Evidence-backed N/A는 exact scope의 exclusion predicate, provenance와 closure를 요구한다. 특정 index에서 미발견이라는 이유로 닫지 않는다.
- Unresolved는 수행한 조사와 source conflict/loader ambiguity/dynamic undercoverage 등을 구체적으로 기록한다. Uninvestigated와 혼용하지 않는다.
- Result와 binding은 canonical `question_key = (item_id, axis_id, scope_ref)`로 대조한다. 별도 `registry_revision`/`authority_id` metadata는 참조 readpoint와의 호환성·채택 상태 검증에만 사용한다. Wrong scope·cross-item·duplicate result·stale revision result는 fail-closed하며 unchanged key를 revision 때문에 새 질문으로 만들지 않는다.
- First-contact obligation과 관련 fact/dependency를 구조적으로 연결한다. 대표 fact 선택·전역 acquisition 문장·S2 composition은 수행하지 않는다.
- L3-04가 같은 item/3-tuple key와 별도 revision metadata로 acquisition을 결합할 수 있게 하고, L3-05에는 accepted facts, relation, 질문 상태와 불확실성을 함께 전달한다. L3-03 derived application은 비획득 result의 실제 resolver 소비만 증명하며 acquisition 공급·통합 구성·item 전체 완료를 만들지 않는다. Open 질문과 공존하는 accepted fact를 질문 미해결 때문에 삭제하지 않는다.

**Validation:** 모든 result→valid key, 모든 binding→accepted same-item fact, axis allowed kind, terminal coverage, scope negative 일치, acquisition 무단 해결 0, first-contact representative selection 0. Item completion 식은 기존 그대로 유지한다.

### Change 9 — Resolver 소비·검증·off-live successor 채택

**Purpose:** Phase 9. 실제 최종 corpus를 structured input으로 소비하고 exact readpoint와 census를 확정한다.

**Files:** Result adapter/CLI, final manifest 및 승인된 authority route, focused test/validation 등록, closeout.

**Implementation Notes:**

1. `load_result_authorities()`와 `resolve_item()`의 기존 boundary를 이용해 실제 fact/result와 updated routing/gap을 소비한다. Synthetic fixture만으로 소비 완료를 주장하지 않는다.
2. Predecessor prose, profile label, classification, Layer 4 rendered output, first ordinal, unresolved acquisition으로 의미를 보충하는 fallback이 없음을 확인한다.
3. Candidate 출력은 명시적 output root로 한정하고 기존 `investigate`의 고정 writer나 composer/product writer로 우회하지 않는다. CLI extension은 기존 command 동작 보존을 검증한다.
4. 최종 corpus는 한 벌만 준비한다. 전체 corpus의 실제 resolver 소비는 G1에서 한 번 수행하고 무결성·상태 집계·소비 검사가 그 결과를 공유한다. 재현성은 producer의 의미 변환·ID 도출·정규화 경로를 사용하는 작고 독립적인 사례의 재호출·입력 순서 변경으로 확인한다. Timestamp/host/review metadata는 semantic identity와 분리한다. 전체 corpus 독립 OS process A/B 생성, 별도 writable cache 두 벌, 전체 pipeline 반복을 의무화하지 않으며 full-process 재현성 성공도 주장하지 않는다.
5. 최종 corpus·manifest·최종 연결안·registry·문서 등 검사 대상 bytes를 준비한 뒤 G1을 실행한다. 준비된 연결안은 G1 전에는 채택 성공의 근거가 아니다. G1은 candidate 검증과 adopted 소비 경계를 구분하며 실제 candidate를 먼저 adopted로 가장해 통과시키지 않는다. 성공하면 같은 검증 subject를 채택하고 추가 post-adoption Gate를 만들지 않는다. 검사 대상 변경이나 실패 수정이 필요하면 관련 내용·binding을 갱신하고 같은 G1을 재실행한다. 성공 후에는 비member closeout의 결과 기록과 임시물 정리만으로 마무리하며 추가 confidence 실행은 하지 않는다.
6. Final census는 상태별·axis별·scope별·fact-kind별·blocker별로 작성한다. Baseline/revised denominator, available-source 범위, partial facts가 있는 unresolved 질문, pending profile, 미조사 residual을 구별한다.
7. Off-live semantic-result adoption만 current authority route에 반영한다. Current product를 전환하지 않는다.

**Validation:** 아래 §7의 단일 최종 G1에 명시적 보호 path/hash/membership·locator 불변성, 실제 resolver consumption, final manifest/member closure와 A1·B1 기준을 묶는다. 검증 실패 상태를 채택 완료로 기록하지 않는다.

---

## 7. Validation Plan

### Automated Validation

권위·사실 데이터를 변경하므로 disclosure/evidence/closeout의 **heavy** 기준은 유지한다. 다만 이 분류가 검증 횟수나 전수 의미 정확성 주장을 추가하지 않는다. 자동 검증은 **단일 최종 G1, 신규 focused source 한 개, public test identity 한 건, 정상 완료 시 pytest 실행 한 번**으로 합친다. 내부 helper/subcase의 수는 필요한 위험 범위에 맞추며 하나의 테스트라는 이유로 coverage를 삭제하지 않는다.

G1은 다음 내용을 같은 실행의 공통 입력·결과로 확인한다. 아래 항목은 별도 Gate나 순차 승인 지점이 아니다.

- **입력·보호 경계:** L3-01/02의 사용 계약과 source binding, exact target/key/pending 집합, 시작 baseline의 명시적 보호 파일과 기존 product locator 부분을 대조한다. 조건부 정의 successor는 이전 정의·baseline 보존과 정당한 영향 범위를 확인한다. 생성 도중 읽은 source를 최종 결과의 source binding으로 재사용하며 독립 census 파일을 중복 생성하지 않는다.
- **전체 결과 무결성:** terminal result가 참조하는 일부만이 아니라 전체 accepted facts/provenance/dependencies/results/partial bindings/applicability/gap을 검사한다. A1의 가용 범위·pending·새 key accounting, whole-scope terminal·scoped negative의 증거 연결, anomaly 및 carry-forward를 확인한다. B1의 의미 판단은 작성 중 검토 기록으로 수용하고 자동 검사는 해당 rule/result와의 결속 및 미처리 결함 여부를 확인한다.
- **실제 소비와 관련 회귀:** 최종 corpus 전체를 실제 adapter/resolver로 한 번 소비하고 필요한 집계와 비교가 그 결과를 공유한다. 공용 함수와 CLI의 기존 의미를 보존하는 사례를 같은 source에 둔다. Source에서 독립적으로 정한 기대값과 작은 사례의 재호출·입력 순서 변경으로 의미 변환·identity·결정성을 확인한다. 전체 생산 pipeline 재실행이나 별도 process A/B는 필수가 아니다.
- **최종 채택 대상:** corpus/member/source/result readpoint와 최종 연결안·registry가 같은 subject를 가리키며 C2 ownership과 보호 범위가 유지되는지 확인한다. 채택은 이 성공 결과에 한정한다. 단순 hash 일치를 내용 정확성으로 확대하지 않는다.

대표 회귀는 case-only identity, raw/index 누락·중복 원본, wrong item/axis/scope, 잘못된 provenance·terminal, partial facts와 open question 공존, context-local role·fact-local qualifier, 다대다 binding, late key·scope negative, 의미 정정에 따른 참조 재결속, acquisition 무단 해결 금지, CLI write boundary를 포괄한다. 서로 관련된 결함은 하나의 사례에서 함께 확인할 수 있다. 변경하지 않은 기존 테스트 두 파일의 전체 실행은 기본 의무가 아니며, 기존 guard를 우회하거나 약화시키지 않는다.

금지된 fallback은 실제 구조화 입력의 수용 경계에서 확인한다. 작은 격리 사례에 fact/result/provenance가 없거나 결속이 잘못됐을 때 prose·profile 표시 label·Layer 4 표시가 있어도 사실을 보충해 성공하지 않아야 한다. Canonical profile ID와 질문 정의는 합법적인 입력으로 유지한다. Predecessor prose를 검색 seed로 읽는 것과 의미 근거로 사용하는 것을 구분한다. 파일 read 전수 계측, 금지 입력 종류별 전체 corpus 교란 실행, 이를 위한 독립 harness는 요구하지 않는다. 어떤 assertion·stub·경계 검사가 적합한지는 실제 코드 구조에 맞춰 정하되 검증하지 않은 무접근 성질을 주장하지 않는다.

신규 제안 source의 public identity는 `test_layer3_semantic_results.Layer3SemanticResultsTest.test_semantic_results_contract`로 계획한다. 저장소 root, Python 3.12 이상, 기존 `iris_tooling`/pytest와 source policy 등록을 전제로 한 명령은 다음과 같다. 아직 구현·실행된 검사기가 아니다.

```powershell
uv run --project .\Iris\tooling --no-sync python -m pytest .\Iris\build\description\v2\tests\test_layer3_semantic_results.py -q -p no:cacheprovider --round3-contract=diagnostic --round3-additional-source=Iris/build/description/v2/tests/test_layer3_semantic_results.py
```

실제 corpus/definition readpoint와 시작 baseline을 넘기는 구체 인자 또는 환경 변수는 기존 input policy에 맞춰 구현 시 정하고, 최종 실행 기록에는 그 값까지 남긴다. 채택 검증은 지정된 실제 전체 corpus를 반드시 소비해야 하며 fixture-only 실행이나 입력 자동 fallback으로 대체하지 않는다. 시작 baseline 누락·손상 상태에서 이번 no-mutation 채택 PASS를 발급하지 않는다. 향후 통상 재사용 검사와 이번 채택 검사를 구별하여 통상 검사에 과거 임시 baseline을 요구하지 않는다. 사용한 환경 변수는 실행 후 이전 값으로 복원한다.

최종 subject·필요한 등록·문서가 준비되면 위 명령을 실행한다. 정상 성공 후 추가 confidence 실행은 없다. 실패 수정 또는 검사 대상 변경 시 같은 G1을 재실행할 수 있다. 기존 source 정책과 실제 적용되는 상위 계약의 별도 의무는 우회하지 않되, 과거 Gate 명칭·명령 예시·등록 목록만으로 전체 suite를 새 의무로 추가하지 않는다. 실제 충돌이 발견되면 정확한 규칙과 영향 범위를 확인해 이 계획을 정정하고 조용히 검증을 생략하거나 늘리지 않는다.

### 입력 손상과 조사 미해결의 구분

| 상황 | 처리 |
|---|---|
| 검증에 필수인 실행 도구, 선행 authority member, 채택 입력으로 지정한 source의 결손·hash 불일치 | 해당 입력에 의존한 판정·채택은 BLOCKED 또는 명시적 입력 오류. 무결성 확인 없이 다른 자료로 대체하지 않음 |
| 실제 조사 후 추가 원본·엔진 구현·동적 dependency를 확보하지 못하거나 의미를 확정하지 못함 | 영향받는 질문·scope에 실제 attempt와 부족 근거를 기록하고 `investigated_unresolved`로 보존. 다른 독립 조사까지 일괄 중단하지 않음 |
| 자료가 사용 가능하지만 수집 코드가 없거나 조사를 수행하지 않음 | `not_investigated` 유지. A1 완료 불가이며 이름만 unresolved로 바꾸지 않음 |

미확보 자료를 accepted fact의 provenance로 가장하거나 결속된 source 손상을 조사 한계로 숨기지 않는다. 반대로 결과를 아직 만들 수 없는 질문이 있다는 이유만으로 정당한 partial facts를 삭제하지 않는다.

Java/Gradle·JS/TS·Lua 구현 변경은 범위 밖이므로 해당 언어 검사, package 생성·검사와 PZ 실행은 기본 추가하지 않는다. 실제 변경 범위가 확대돼 언어별 필수 검증이 필요해지면 먼저 scope와 적용 규칙을 정정한다. Lua 원본을 읽는 것은 Lua 구현 변경이 아니다.

### Manual Validation

- **B1:** 음식·도구·무기·의류·multi-use·low-information과 A~E route를 층화해 감사한다. 구현 route에서 가능한 positive / grounded negative / unresolved 사례를 포함한다.
- **B1:** Unique automatic mapping rule의 전제·source 소비 동작·변환 범위·예외를 전수 의미 검토한다. Ambiguous source, multiple declaration, manual interpretation, dynamic predicate chain, multi-context role, condition/constraint fact는 위험에 맞춰 개별 review를 우선하고 미검토 범위를 명시한다. 모든 item 수작업 검토나 추가 외부 reviewer 승인을 요구하지 않는다.
- **사용자 관점 의미 기준:** 함수명·필드·호출 성공을 사용자용 기능과 혼동하지 않고, 실제 기능·효과·활동 및 그 진실 범위를 표현하는 proposition인지 확인한다. 너무 넓은 합성으로 독립 용도·역할을 잃지 않는지, 지나친 분해로 개별 Layer 4 관계 목록을 복제하지 않는지, 조건 생략으로 의미가 바뀌지 않는지 검토한다. 구현상 세부는 근거에 남길 수 있지만 모든 세부를 별도 설명 fact로 강제하지 않는다. 최소 fact/용도/문장 수는 없다.
- Rule 검토와 provenance/대표 route 표본은 candidate admission 중 함께 수행하고 같은 기록을 최종 G1·closeout에서 사용한다. 별도 사전·사후 내용 심사나 외부 reviewer 승인을 요구하지 않는다. 동일 rule의 검토 결과는 적용 범위를 명시해 공유하고 별도 rule별 Gate나 proof tree를 만들지 않는다. 표본 밖 accepted fact의 전수 의미 정확성을 주장하지 않는다.
- **공통:** 네 anomaly disposition, scoped negative의 실제 closure, partial fact가 있는 unresolved 질문, predicate에서 engine으로 넘어가는 경계를 검토한다. 구조 통과만으로 semantic correctness PASS를 붙이지 않는다.

### Validation Limits

- B1을 수행해도 exact upstream build correspondence, bound snapshot의 완전성, 모든 dynamic behavior, source 밖 engine semantics를 보증하지 않는다.
- Acquisition truth, KO/EN quality, Menu/Tooltip 표현·렌더링, Lua runtime 실행, package/install, PZ 실기동·멀티플레이·장시간 호환성 검증은 수행하지 않는다.
- Byte invariance 주장은 임시 baseline에 명시한 보호 경로와 기존 locator 부분에 한정한다. 전체 package/runtime/locale tree의 byte parity나 실게임 동작·release readiness를 주장하지 않는다. Runtime/package를 변경하지 않는 범위 규칙은 그대로 유지한다.
- 작은 사례의 결정성 검사는 full-process A/B, cross-process·다른 OS/engine/build 재현성 검증이 아니다. 실제 전체 corpus 소비 성공과 작은 사례 결정성의 증거 범위를 구분한다. Closeout은 `validated`, `out_of_scope`, `unvalidated_but_in_scope`를 구분한다.
- 계약 문서 복원 및 member hash 일치는 당시 관찰 기록이다. 현재 계획의 최종 G1은 아직 실행하지 않았으며 과거 PASS를 현 subject로 승계하지 않는다.
- 이번 수정은 계획 문서에 한정한다. 문서 정합성 확인을 구현 Gate의 실행·성공으로 표현하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

영향 있음. C2의 L3-03 별도 authority가 non-acquisition accepted semantic facts·question results·derived application을 소유한다. L3-02 정의 자체를 바꿀 필요가 있을 때만 최소 successor를 만든다. L3-01 의미 계약과 Layer 4 ownership은 보존한다.

### Runtime Behavior Surface

변경 없음. Python offline tooling에서 조사·생산·검증하며 PZ의 Iris는 100% Lua 원칙을 유지한다. Runtime writer 호출·설치는 범위 밖이다.

### Compatibility Surface

Structured result adapter와 선택적 CLI 확장의 offline compatibility에 영향이 있다. 기존 `investigate`, composer dispatch, result terminal semantics, exact FullType를 보존한다. Product compatibility 변경은 없다.

### Sealed Artifact Surface

영향 있음. Final facts/provenance/results/source/universe와 manifest가 새 exact subject다. Candidate와 adopted result를 구별하고 이전 readpoint/member lineage를 보존한다.

### Public-Facing Output Surface

변경 없음. Menu/Tooltip, locale 문자열, S2 selection·composition과 package는 기존 상태다. Semantic-result 채택을 사용자 화면 전환으로 설명하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- **높음 — applicability → fact 오승격:** Typed candidate/admission 경계와 semantic proposition review로 차단한다.
- **높음 — pending universe 누락:** 현재 required key만 처리하면 빈 scope의 pending이 사라진다. Item/profile ledger와 revision별 key carry-forward를 병행한다.
- **높음 — multi-context collapse:** Global role·대표 use와 context를 제외한 payload deduplication을 금지한다.
- **중간 — 중복 authority:** C2의 단일 소비 readpoint가 definition revision·별도 result authority·derived application을 명시하게 한다.
- **중간 — taxonomy 확장:** Instance/scope extension/definition gap을 구분하고 영향 범위가 입증될 때만 최소 revision한다.
- **높음 — revision의 key identity 혼입:** Canonical 3-tuple과 readpoint metadata를 분리하고 unchanged key/fact ID 유지 및 신규 carry-forward vocabulary 검증으로 차단한다.

### Runtime Risk

- **낮음 — 직접 runtime 변경:** 범위에 없으며 보호 baseline과 CLI write boundary로 검사한다.
- **중간 — 잘못된 CLI 호출:** 기존 `investigate`는 L3-02를 덮어쓰고 미인식 layer3 인자는 composer로 전달된다. 새 명령의 명시적 분기와 candidate output 강제로 우발적인 generation을 막는다.

### Compatibility Risk

- **높음 — source blind spot → negative:** Route capability, exact negative scope, 확보 실패 blocker를 함께 검증한다.
- **높음 — raw snapshot 혼합/loader 추정:** 추가 source를 별도로 결속하고 duplicate winner를 loader 증거 없이 정하지 않는다.
- **중간 — open state partial facts 손실:** Terminal `fact_refs`와 별도 contribution binding을 구분하고 실제 resolver output에서 소비를 확인한다.
- **중간 — Layer 4 output 오염:** Shared upstream source의 raw provenance만 사용한다. Fixer 집합·EvolvedRecipe public row·표시 문자열은 사실 authority가 아니다.

### Regression Risk

- **높음 — 실행 시 member 재누락 또는 drift:** 복원 확인 후에도 실행 subject의 member 존재와 hash를 fail-closed로 재확인한다.
- **높음 — 기존 L3-02 재현 검사 파괴:** 기존 baseline writer/검사를 유지한다. 실제 정의 successor가 필요한 경우에도 predecessor 재현과 lineage를 보존한다. `accepted_semantic_results == []` 검사를 무조건 삭제하지 않는다.
- **중간 — 검증 후 corpus 변형:** 검사 대상이 바뀌면 관련 binding과 기대값을 갱신한 뒤 같은 최종 G1을 재실행한다. 변경 없이 성공한 subject에 추가 confidence 검증을 붙이지 않는다.
- **중간 — fact 수/해결 수 완료 과장:** Item 완료식·acquisition 잔여·A1/B1 claim ceiling을 closeout에 함께 표시한다.

---

## 10. Rollback Plan

- Candidate 검증 실패 시 current readpoint를 바꾸지 않고 candidate/disposition만 수정한다. L3-01/L3-02와 current product를 유지한다.
- 특정 rule/source route의 systematic defect이면 해당 rule/source에서 파생된 fact, dependent fact, question binding/result를 추적하여 invalidation하고 affected key를 reopen한다. 관련 없는 route까지 무조건 폐기하지 않는다.
- Definition revision의 영향 범위가 불명확하면 기존 registry revision을 유지하고 새 발견을 definition gap으로 남긴다. 완료율을 맞추기 위한 rebaseline을 하지 않는다.
- 채택 후 문제는 이전 accepted readpoint로의 명시적 재지정 또는 correction successor로 처리한다. 이전 manifest/member bytes와 실패한 successor 이력을 삭제하지 않는다.
- 기존 dirty 문서 삭제를 포함한 사용자 변경을 rollback 대상으로 삼지 않는다.

다음은 adoption 중단 조건이다: target/key mismatch, source/provenance 손실, systematic inference, context collapse, unresolved→negative 전환, prose/profile fallback, 불명확한 denominator revision, C2 ownership 위반 또는 baseline 덮어쓰기, B1의 반복 mapping defect, A1 기준 미충족, current product delta, 필수 검증 BLOCKED/FAIL.

---

## 11. Governance Constraints

- `docs/Philosophy.md` 준수. 확인된 사실만 설명하고 근거가 부족하면 침묵한다. 권장·효율·우열 판단을 추가하지 않는다.
- Hub & Spoke/SPI 원칙, Pulse 역의존 금지, 모듈 간 직접 의존 금지를 보존한다. 본 작업은 Iris offline tooling 내부다.
- Runtime/build-time 분리와 Iris 100% Lua runtime을 유지한다.
- Existing authority ownership과 sealed lineage를 우회하지 않는다. 필요한 변경은 최소 additive successor로 기록한다.
- Case-sensitive identity, `0..N` facts, context-local role, fact-local qualifiers, semantic/provenance/investigation/expression/presentation 축 분리를 보존한다.
- Recipe와 Right-click은 독립·동등한 source 관점이다. Layer 3 broad meaning과 Layer 4 exact relations의 경계를 유지한다.
- Source/index 부재, profile exclusion, 0 fact, 조사 미수행, unresolved는 서로 대체할 수 없다.
- A1·B1·C2는 §4.4의 사용자 지정 작업 질의 답변에 따라 이번 계획에서 선택했다. 이를 과거 승인·계획 전체 PASS·구현/authority 채택 완료로 표현하지 않는다. 추가 외부 reviewer/승인 단계를 임의로 만들지 않는다.
- 임시 helper/baseline과 상세 candidate evidence를 새 permanent authority로 자동 승격하지 않는다. 기존 validation 등록·output policy에 맞춘다.
- 신규 carry-forward relation과 partial binding은 구현 계약에서 정의하고 authority 채택 시 변경 범위를 공개한다. Closeout만으로 새 token/field를 채택하지 않는다. 보존할 증거와 downstream dependency를 확인한 뒤에만 재생성 가능한 intermediate를 정리한다.
- 최종 G1은 정확한 명령의 exit `0`일 때만 해당 범위 PASS다. 필수 실행 도구·선행 authority·지정된 채택 source의 결손/손상은 해당 판정·채택을 막는다. 실제 조사에서 발견한 추가 근거 부족은 §7에 따라 질문별 unresolved로 남길 수 있으며 두 상황을 혼동하지 않는다. 과거 subject의 검증 결과를 현 subject의 통과로 승계하지 않는다.

---

## 12. Expected Closeout State

**실행 목표 상태:** `complete` — 단, DVF-L3-03의 off-live non-acquisition semantic-result 구축·검증·채택 범위에 한정한다. **현재 상태:** `planned`, 실제 corpus 생산·adoption 미실행. A1·B1·C2를 유지하고 단일 최종 G1으로 검증을 통합했다. 실행 준비는 별도 Gate가 아니며 최종 subject에 대한 G1은 아직 수행하지 않았다. 이 수정만으로 계획 전체 PASS를 주장하지 않는다.

Complete 조건은 다음과 같다.

1. Exact FullType 2,105개, original/revised key universe와 pending item/profile 이력이 보존된다.
2. 모든 accepted fact는 valid kind/payload/provenance와 source-supported admission을 갖고 context/qualifier 참조가 유효하다. 최소 fact 수는 요구하지 않는다.
3. 조사한 질문은 fact-backed resolution, grounded scoped N/A 또는 investigated unresolved로 식별되며 partial fact와 whole-question completion이 구별된다.
4. 네 anomaly와 A~E route의 조사 범위·source dependency·residual blocker가 명시된다.
5. Crafting 1,779 / cooking 1,879 / world-work 2,085 및 native anomaly pending, direct/dynamic gap이 개별 근거에 따라 처분된다. 겹치는 집합을 합산해 완료율을 만들지 않는다.
6. 실제 corpus를 successor resolver가 structured input으로 소비하며 predecessor prose/profile/Layer 4 fallback이 없다.
7. Final manifest/readpoint와 census가 동일 검증 subject에 결속되고 단일 최종 G1이 성공한다. Product 변경 금지는 유지하며 byte 보존 증거는 명시된 보호 경로·기존 locator 부분에 한정한다. 전체 runtime/package parity를 검사했다고 주장하지 않는다.
8. **A1:** 결속된 available-source key/route 집합과 pending 조사에서 새로 확정된 available key의 단순 미수행 `not_investigated`는 0이다. 실제 조사 후 부족한 source/engine/dynamic dependency로 닫히지 않은 질문은 evidence-bound unresolved로 남길 수 있다. 자료 밖 영향 범위는 별도 dependency로 기록하며 조사 완료를 주장하지 않는다.
9. **B1:** Unique rule 전수 의미 검토와 층화 content audit, 위험에 맞춘 추가 fact review를 충족하고 검토된 route/rule/fact 범위만 semantic validation claim을 한다. 구조 검사만으로 이 조건을 대체하지 않는다.
10. **C2:** L3-02 baseline writer/application을 보존하고 final readpoint에서 definition revision·별도 result authority·derived application 관계를 일관되게 소비한다. 기존 정의 안의 fact/applicability/구체 scope 추가만으로 L3-02 정의를 개정하지 않는다.

최종 G1이 실패하거나 필수 검증 입력·선행 authority를 읽을 수 없어 채택할 수 없으면 그 차단 원인과 실패 결과를 기록한다. Corpus 일부만 처리했거나 종료 기준에 못 미치면 `partial`, 구현했지만 최종 검증·채택이 없으면 `implemented_only`로 구분하고 적용되는 closeout 규칙에 따라 상태를 선택한다. A1/B1을 충족한 explicit unresolved 잔여는 source truth의 한계로서 complete와 양립할 수 있지만 available-source 범위의 단순 미조사 잔여는 complete와 양립하지 않는다. 추가 source를 확보하지 못한 질문이 있다는 사실만으로 전체 작업을 `blocked`로 바꾸지 않는다.

최종 closeout에는 exact command/exit code, subject/member identities, state·axis·scope·fact-kind census, carry-forward, review 범위, residual source/definition blocker, L3-04/L3-05 handoff와 **선택된 A1·B1·C2 및 그 근거·일자·provenance**를 함께 기록한다.

**NC2 — 선택 기록 보존:** 단일 closeout의 한 절에 §4.4의 선택일 `2026-09-04`, 사용자 요청과 답변 출처 `01a0620a-a4a0-75a0-ba48-d7199bb9485a`, A1·B1·C2의 내용·근거·한계 및 이번 검증 통합 요청을 요약한다. `codex://` 링크 접근 없이 이해 가능하게 하되 별도 trace 파일·승인·검증 Gate는 만들지 않는다. 이 기록은 과거 승인·계획 전체 PASS를 소급 선언하지 않으며 기존 선택을 다시 심사할 의무도 아니다.

완료 주장은 **확인된 비획득 의미와 질문별 결과를 source-bound 구조로 구축하고 남은 불확실성을 보존했다**는 범위다. Acquisition 해결, 2,105 item investigation complete, Layer 3 전체 완료, 표현·S2 완성, runtime/product 전환, PZ 동작 검증, package 또는 release readiness의 완료를 뜻하지 않는다.
