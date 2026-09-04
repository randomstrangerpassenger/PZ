# Implementation Plan

> 문제 ID: `DVF-L3-02`  
> 제목: Iris Layer 3 복수 프로필·조사 완결성·first-contact 정보 기준 확립  
> 작성일 / 수정일: 2026-09-04  
> 상태: `complete` — 조사 기준·전체 2,105 target 적용·investigation authority 채택 완료; adoption G1 exit `0`, 상세 결과와 한계는 단일 closeout 참조
> 양식: `docs/PLAN_TEMPLATE.md`  
> 입력: 사용자 제공 종합 Roadmap 및 계획 검토 사항. 이번 수정은 first-contact 내용 기준 보강, 근거 있는 scope routing, 검증·Gate 최소화 요청을 반영한다.  
> 상위 기준: `docs/Philosophy.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/EXECUTION_CONTRACT.md`  
> 상속 계약: `Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json`  
> 계획 조사 HEAD: `47a44ddae53124bffd09ebafaa4b2aea0f924d59` — 실행 시작 상태와 동일하다고 가정하지 않는다.  
> 실행 무게: `Heavy` — disclosure·evidence·closeout 의무. 전체 검사·반복 실행·별도 승인 Gate의 자동 근거가 아니다.  
> 필수 검증: §7의 단일 최종 G1. 이전 계획의 별도 A/B 출력, 채택 전후 check, 외부 증거 workspace 의무는 이번 수정으로 대체한다.  
> 계획 수정은 구현 검증 PASS나 실행·채택 승인을 뜻하지 않는다.

---

## 1. Objective

각 exact case-sensitive `FullType`에 대해 적용 가능한 복수 프로필, 필요한 조사 질문, 조사 상태, item-level 완료 조건과 first-contact 정보 축을 근거에 따라 설명하고 계산할 수 있는 오프라인 기준과 실제 전체 대상 application을 구축한다.

목표는 상태표를 채우는 것만이 아니다. 조사자가 무엇을 확인해야 하는지 알 수 있고, 설명 구성자가 first-contact 정보 선택 기준을 처음부터 다시 만들어야 하지 않는 결과를 제공한다.

- 프로필은 조사·구성·first-contact 범위를 제공하지만 actual semantic fact나 대표 의미를 생성하지 않는다.
- 조사 대상에 필요한 질문을 보존하되, 모든 아이템에 모든 프로필의 개별 심층조사를 요구하지 않는다.
- first-contact 축마다 사용자 질문, 첫 이해에 필요한 이유와 상세 정보와의 경계를 설명한다.
- 획득 축은 모든 대상의 필수 조사 축이다. 획득 해결만으로 item 전체 조사를 완료하지 않는다.
- 실제 사실·KO/EN 문장·runtime 전환은 완료 주장에 포함하지 않는다.

`complete`는 조사 기준과 전체 대상의 근거 있는 적용·잔여 추적이 성립한 상태다. 모든 item complete 또는 unresolved 0을 뜻하지 않는다.

---

## 2. Scope

- Current facts/decisions에서 exact target set과 source identity를 확인한다.
- 복수 프로필의 admission, applicability, scope routing 및 근거 규칙을 정의한다.
- 조사 axis와 context-preserving union, item completion을 정의·구현한다.
- 프로필별 first-contact의 내용 기준과 contributor 관계를 정의한다.
- 전체 target에 실제 기준을 적용하고 scope gap·미조사·미해결을 식별한다.
- 기존 Layer 3 Python 도메인에 필요한 resolver와 하나의 focused test source를 추가한다.
- 기존 successor bundle 밖에 최소 investigation authority를 추가하고 current readpoint와 문서를 정렬한다.

### Explicitly Out Of Scope

- 기존 `layer3_successor` bundle과 human semantic contract의 수정.
- Current facts/decisions, 기존 composer·precedence, rendered corpus의 변경.
- 실제 semantic/acquisition fact 전수 구축 및 negative-result 생산 authority 신설.
- KO/EN 문장, Menu/Tooltip 출력, Lua runtime, current generation/pointer, 패키지 변경.
- Layer 2 taxonomy 및 Tooltip `0..4` logical-row 소유권 변경.
- 무관한 historical cleanup, 별도 validator framework, proof package, approval ceremony.

---

## 3. Non-Goals

- `primary_use`, selected role/profile 또는 single-core를 다른 이름으로 복원하지 않는다.
- 프로필·사실·문장 수나 분류 계층 깊이를 목표값으로 고정하지 않는다.
- Profile overlap을 priority로 하나만 선택해 해소하지 않는다.
- 기존 prose, 분류 label, 화면 출력 또는 source 부재에서 actual fact를 생성하지 않는다.
- 모든 registry profile을 개별 심층조사해야만 scope를 닫을 수 있다는 규칙을 기본값으로 강제하지 않는다.
- 잠재적 적용 가능성을 무시하거나, 근거 없는 routing으로 미해결을 없애지 않는다.
- First-contact를 전역 필수 fact 목록이나 완성 문장으로 고정하지 않는다.
- 이 계획의 검증을 corpus 정확성·runtime·release readiness의 범용 증거로 사용하지 않는다.

---

## 4. Assumptions

### 4.1 확인된 baseline과 상속 계약

계획 조사 당시 확인한 값이며 실행 시 재확인한다. Count를 writer 상수로 사용하지 않는다.

| 대상 | 관찰 값·규칙 | 적용 의미 |
|---|---|---|
| facts/decisions | 각각 2,105 rows/unique IDs; duplicate 0; exact set 동일 | 두 source에서 target을 도출한다 |
| exact set SHA-256 | `122ca07c483ff8e4af9ef83bfb8d28c950802a124aba1668c234bce3477b2fdb` | ordinal case-sensitive 정렬, UTF-8, identity당 LF |
| 상속 manifest SHA-256 | `6735c3eadafaf4c4fd51ae56c8d0748d32903ee996d53ed43bca38822cf0932a` | 실행 시작 시 current readpoint와 대조한다 |
| 상속 `contract.json` SHA-256 | `bb8201549218b08452fd603ff13727599c1021f98882de1d7dae9f3545e9890e` | exact bound bytes에서 계약을 읽는다 |
| source `item_id` | exact case-sensitive FullType | strip/lower/casefold/Unicode normalization 금지 |
| 별도 분모 | adopted 2,099/6, S2 2,048/57, owner absence 175 | target universe나 조사 완료 수로 대체하지 않는다 |

상속 계약의 핵심은 다음과 같다.

- Item별 `0..N` typed facts, context-local role 및 fact-local condition/constraint.
- Fact, provenance, investigation, expression, presentation의 독립성.
- Global acquisition은 `resolved / investigated_unresolved / not_investigated`이며 N/A 불가.
- Acquisition `resolved`에는 하나 이상의 accepted `acquisition` 또는 admissible `acquisition_unobtainable` fact가 필요하다. 획득 축 완료는 item 전체 완료의 충분조건이 아니다.
- `acquisition_unobtainable`은 허용 kind지만 current producer `none`, assignment `0`이다. 별도 정식 negative-evidence authority 없이 새 instance를 만들 수 없다.
- Menu와 S2는 같은 accepted facts를 다른 깊이로 소비한다. Importance·frequency·efficiency·ordinal·profile label에 의한 대표 의미 선별은 금지한다.

### 4.2 기존 코드와 입력의 역할

| 파일·구조 | 확인된 역할 | 이번 처리 |
|---|---|---|
| `build/compose_layer3_body_profile.py`의 `resolve_body_profile()` | 기존 단일 body profile 선택 | 복수 investigation resolver로 재사용하지 않음 |
| 같은 파일의 coverage quality | emitted/required section 기반 품질값 | 조사 완료와 연결하지 않음 |
| `build/compose_layer3_item.py` | 기존 prose·compose profile 소비 | 보호 대상 |
| `domains/layer3/cli.py` | 기존 Layer 3 명령 dispatch | 필요한 조사 application 진입점만 추가 |
| `domains/layer3/tooltip_t1_d3.py` | 175 owner-absence subset 처리 | target selection·고정 count 복사 금지 |
| `tests/conftest.py` 및 source classification | 미분류 test source를 fail-closed로 거부 | 기존 등록 방식 사용, guard 우회 금지 |

위 상대 경로의 Python 구현 root는 `Iris/tooling/src/iris_tooling/`, test root는 `Iris/build/description/v2/`다.

Applicability 입력 후보와 소비 조건:

| `Iris/input/` 입력 | 역할·조건 |
|---|---|
| `items_itemscript.json` | FullType별 field 추출. Exact field·관찰값과 upstream snapshot/추출 범위를 결속 |
| `recipes_index_full.json` | Static recipes 추출 인덱스. 원본 Recipe/field까지 추적하며 static-only 부재를 전역 부재로 확대하지 않음 |
| `rightclick_source_index.v2.4.json` | 탐색 rule/anchor 인덱스. 연결한 Lua/script와 exact item predicate를 확인 |
| `fixing_fixers.json` | 축약 목록. 원문·추출 provenance 없으면 candidate signal로만 사용 |
| `moveables_tooldefs.json` | itemIds/tags/defs 추출. 실제 definition과 태그 해석·source scope를 확인 |

경로 존재나 source-family 이름만으로 current admissibility·완전성을 부여하지 않는다. 기존 Layer 4 owner/rendered row·관계 수·최종 표시 문자열은 evidence 입력에서 제외한다. Recipe와 Right-click은 동등한 독립 관찰 경로다.

### 4.3 미정 사항과 실행 중 설계 여지

- 프로필 목록·수·계층 깊이·질문 묶음은 실제 source와 사용자 질문 차이에 따라 정한다.
- `FullType × profile` 전체를 물리적으로 펼친 행렬은 필수 산출물이 아니다. Explicit application과 근거 있는 공통 routing을 함께 사용해도 된다.
- 조사 모델 후보를 실제로 서로 다른 성격의 아이템에 적용한 후 scope 규칙을 확정한다. 형식적 상태 계산만으로 모델의 사용 가능성을 판단하지 않는다.
- 미해결 비율에 임의 임계값을 두지 않는다. 기준 결함, source 부족, 실제 미조사를 구별한다.
- 임시 작업은 저장소 내 비권위 staging 또는 정상적인 temporary directory에서 수행할 수 있다. 별도 외부 workspace나 task 전용 절대 경로는 요구하지 않는다.
- source/readpoint가 바뀌었으면 기존 candidate에 조용히 섞지 않고 변경 범위와 새 binding을 확인한다.
- Target 또는 상속 authority가 확인되지 않으면 채택을 중단한다. 개별 source 부족은 해당 상태를 열어 둔 채 다른 작업을 진행할 수 있다.

---

## 5. Repository Areas Affected

### Code

- `Iris/tooling/src/iris_tooling/domains/layer3/investigation.py` [신규] — profile/axis/evidence 모델, routing, union, completion과 application 계산.
- `Iris/tooling/src/iris_tooling/domains/layer3/cli.py` — 전체 application 생성에 필요한 최소 진입점. 기존 dispatch 보존.
- `Iris/build/description/v2/tests/test_layer3_investigation_contract.py` [신규] — 단일 G1 source. 기존 helper를 재사용할 수 있으나 별도 validator family를 만들지 않음.

기존 `test_layer3_successor_contract.py`는 수정하지 않는다. 이번 G1은 상속 bundle/hash와 사용 계약을 확인하며, 같은 검증을 위해 기존 test 전체를 별도로 재실행할 의무를 추가하지 않는다.

### Docs

- 본 계획.
- `docs/iris_dvf_layer3_multi_profile_investigation_completion_first_contact_contract.md` [신규] — human investigation contract.
- `docs/iris_dvf_layer3_multi_profile_investigation_completion_first_contact_closeout.md` [신규] — 단일 실행 결과·잔여 상태·검증 한계 기록.
- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` — 채택 결과와 product migration 미수행 경계.

### Config

- `Iris/_docs/authority/iris_current_authority_manifest.json`, `iris_current_route_index.json` — investigation readpoint 한 건.
- `Iris/validation/execution/required_validations.json` — focused test identity 한 건.
- `Iris/_docs/round3/round3_pytest_source_classification.json` — 새 test 및 실제 tracked/planned source binding.
- `.gitattributes` — 신규 채택 bundle/human contract에 필요한 경로만 byte 보존 규칙 추가. 기존 파일 재정규화 금지.

### Generated Artifacts

신규 authority root는 `Iris/_docs/authority/dvf/layer3_investigation/`다. 초기 산출물은 다음 네 machine file과 human contract로 제한한다.

| 파일 | 내용 |
|---|---|
| `contract.json` | Schema, profile/axis definitions, routing·evidence·completion·first-contact 규칙. Profile/axis별 별도 파일을 기본 요구하지 않음 |
| `evidence.jsonl` | Exact item 또는 명시적인 공통 member set에 결속된 applicability/routing 관찰과 근거. Actual semantic corpus가 아님 |
| `applications.jsonl` | Target당 한 record. 적용 프로필, routing refs, 잠재 scope, required axes, first-contact, 계산 상태와 구체 blocker |
| `manifest.json` | 상속/target source identity, target count/set digest, definition revision, 네 member(human contract 포함)의 path/hash와 채택 상태 |

Exact membership은 target source와 applications에서 대조한다. 별도 `target_universe.json`과 `reconciliation.json`을 기본 생성하지 않는다. 상태 집계와 잔여 요약은 application에서 계산하고 closeout에 기록한다.

실행 시작 보호 fingerprint는 §7을 위해 임시 JSON 한 개로 보관한다. 이는 일회성 test input이며 authority member, 정규 report, 새 validator 또는 semantic identity가 아니다. 별도 before/after/report 세트·A/B artifact tree·receipt·attestation을 만들지 않는다.

---

## 6. Planned Changes

### Change 1 — Exact target와 bounded baseline 확인

Purpose: 조사 대상과 변경하지 않을 기존 상태를 분명히 한다.

Files: target sources, current readpoints, 상속 bundle 읽기; `investigation.py`, 신규 manifest의 target binding.

Implementation Notes:

1. 실행 시작 HEAD와 dirty state를 확인한다. 기존 사용자 변경은 보존한다.
2. Facts/decisions에서 nonempty string `item_id`, duplicate, exact set equality를 확인한다. 불일치를 union/intersection으로 숨기지 않는다.
3. Ordinal case-sensitive target digest와 source hashes를 결속한다. 같은 count도 같은 membership이 아니다.
4. §7의 명시적 보호 파일과 pointer-selected generation만 초기 fingerprint로 기록한다. 패키지 탐색이나 runtime 전체 census를 하지 않는다.
5. Current manifest/index와 허용 config는 변경 예정이므로 byte 불변 대상과 구분한다. 기존 readpoint·product locator와 무관한 entries는 유지한다.

Validation: target identity와 bounded 보호 상태는 최종 G1에서 확인한다. 별도 preflight Gate를 만들지 않는다.

### Change 2 — 프로필·조사 질문·근거 있는 scope routing 구축

Purpose: 무엇을 조사해야 하는지 정하되, 단순 전수 행렬이나 대표 프로필로 문제를 바꾸지 않는다.

Files: 신규 contract, evidence, investigation 구현 및 human contract.

Implementation Notes:

1. 프로필에는 stable ID/revision, 목적, 실제 사용자·조사 질문, 적용 근거, required axes, first-contact axes, 중첩 관계와 사례를 둔다. 조사 질문·적용 방법·정보 요구의 실질적 차이가 없는 label 분화는 합친다.
2. Applicability는 `confirmed_applicable / evidence_backed_not_applicable / investigated_unresolved / not_investigated`를 구별한다. Positive는 actual fact의 resolved를 뜻하지 않는다.
3. Evidence는 exact 대상, source identity/hash/locator, build/snapshot, predicate, 관찰값과 판정 이유를 연결한다. 공통 source나 routing rule은 정확한 member set에 결속해 재사용할 수 있다.
4. 모든 프로필을 고려했음을 보장하되, 개별 심층조사가 필요한 범위와 근거로 배제된 범위를 구별한다. Scope routing은 공개된 predicate와 근거로 프로필의 후보 범위를 결정한다. 단순 name/category 추측이나 검색 실패로 제외하지 않는다.
5. 원본에서 의미와 적용 범위가 확인된 type/태그/구조적 field는 routing 근거가 될 수 있다. 이때 원본 판정 근거가 authority이며 Layer 2 label이나 해당 field만으로 새로운 기능·효과를 생성하는 것은 아니다.
6. 미적용에는 해당 배제 predicate를 정당화하는 source 범위·완전성·한계를 확인한다. 필요 범위를 넘는 전역 획득 불가 증명까지 요구하지 않는다. 배제를 입증하지 못한 잠재 scope는 unresolved/not investigated로 남긴다.
7. 공통 rule로 배제된 적용 상태는 명시적 rule/member binding으로 설명 가능해야 한다. Record 생략을 암묵적 N/A로 해석하지 않는다. Rule 누락·미일치·알 수 없는 token은 error 또는 명시적인 미정 scope로 처리하고 구별한다.
8. Positive/negative 충돌은 두 근거를 보존하고 unresolved로 둔다. Confidence score·자료 수·priority로 승자를 고르지 않는다.
9. 새 프로필·predicate·source 변경 시 영향받는 범위를 재평가한다. 안전한 subset이 확인되지 않으면 관련 profile의 전체 target을 다시 평가한다. 관련 없는 프로필까지 무조건 개별 재조사하지 않는다.

Validation: 공통 routing과 개별 적용이 같은 의미를 주는 경우, 배제 불가한 잠재 scope, 다중 프로필, 잘못된 배제 및 충돌 사례를 G1에 포함한다.

### Change 3 — Axis union·완료 판정과 희소 정보 구분

Purpose: 필요한 조사 범위의 상태로 완료를 계산한다.

Files: 신규 contract, investigation 구현, applications 및 human contract.

Implementation Notes:

- Axis에는 조사 질문, scope 단위, 허용 evidence/result, terminal 조건과 N/A 허용 여부를 정의한다. Axis 하나가 `0..N` facts에 연결될 수 있으며 fact kind와 동일한 개념이 아니다.
- Canonical key는 `(FullType, axis_id, scope_ref)`다. 아직 semantic fact가 없는 조사 context에도 stable scope ID를 사용할 수 있지만 그것이 `use_context` fact를 생성하지는 않는다.
- 같은 key의 contributor는 합집합으로 보존한다. Context가 다른 같은 axis는 합치지 않는다.
- Required axes는 global acquisition 한 건과 confirmed profiles의 scoped required axes 합집합이다. Applicability가 미정인 잠재 질문은 `pending_scope_refs`로 보존한다.
- Acquisition은 item scope에서 정확히 하나이며 N/A를 허용하지 않는다. 일반 axis는 계약에 따라 evidence-backed N/A를 허용할 수 있다.
- `scope_state`, `coverage_gap_state`, `item_investigation_state`를 분리한다. Scope determined에는 registry 검토 범위의 적용·배제가 설명되고, 적용 가능성이 남은 pending scope/conflict가 없으며, gap assessment에서 미해결 범위가 없어야 한다.
- 근거로 배제된 scope에는 개별 심층조사 미수행을 이유로 별도 blocker를 만들지 않는다. 반대로 routing이 설명하지 못한 영역을 배제된 것으로 간주하지 않는다.

```text
item_complete
  = scope_determined
    AND every_required_axis_terminal_under_its_contract
    AND acquisition_state == resolved
```

- Completion은 수기 boolean이 아니라 계산값이다. 원인과 관련 profile/axis/evidence를 추적한다.
- Resolved는 질문 범위에 맞는 terminal evidence/result를 요구한다. 임의 fact 한 건 발견으로 질문 전체를 닫지 않는다.
- Acquisition에는 상속 계약이 요구하는 accepted result refs를 확인한다. Exact FullType/fact ID와 결과 authority/provenance를 결속하며 기존 hint나 allowed kind 정의를 accepted instance로 취급하지 않는다.
- Negative acquisition은 별도 정식 negative-evidence authority와 accepted instance가 있어야 소비할 수 있다. 해당 authority의 닫힌 범위·completeness·false-negative 제한·subject 결속이 terminal claim을 지지해야 한다. 조사 resolver가 이를 자체 보충·비준하거나 source-specific producer를 새로 구현하지 않는다.
- 정식 결과가 없으면 조사 여부에 따라 unresolved/not investigated를 유지한다. 요건 미충족 resolved/negative claim은 오류로 거부하며 조용히 downgrade하고 PASS하지 않는다.
- 상속된 current producer `none`/assignment `0`을 변경하지 않는다. 미래 admissible result의 합성 fixture는 실제 negative fact 채택을 뜻하지 않는다.
- Prose·S2·번역 존재, 문장 길이와 fact 개수는 완료 함수의 입력이 아니다. 계수를 표시한다면 accepted distinct fact ID 기준이고 미확인은 unknown이다. Negative acquisition 하나는 acquisition fact 한 건이며 total 0으로 계산하지 않는다.
- 프로필 적용을 조사했다고 actual semantic/acquisition axes를 일괄 resolved로 만들지 않는다.

Validation: acquisition-only, 잠재 적용 미해결, 미평가 gap, 근거로 배제된 scope, low-information, 조건 미충족 terminal claim을 기존 G1 사례 안에서 확인한다.

### Change 4 — First-contact의 내용 기준과 실제 사용 가능성 확립

Purpose: 단순 axis list 전달을 넘어 왜 그 정보가 첫 이해에 필요한지 설명한다.

Files: 신규 contract의 profile/axis definitions, human contract, investigation 구현 및 applications.

Implementation Notes:

1. First-contact axis마다 답할 사용자 질문, 첫 이해에 필요한 이유, 관련 required question과 상세 정보로 남길 부분의 경계를 기록한다. 새 질문이면 axis catalogue에도 정의한다.
2. 축을 포함·제외하는 근거는 importance 순위가 아니라 질문과 정보 해상도의 차이로 설명한다. 설명 작성자가 이 기준을 다시 처음부터 결정해야 하는 상태로 넘기지 않는다.
3. Confirmed profiles의 first-contact를 scoped axis 단위로 합치고 contributor/context를 보존한다. Pending applicability는 확정 subset과 전체 scope 미정 상태를 함께 전달한다.
4. Actual fact가 없다고 obligation을 삭제하지 않는다. 그 경우 문장을 만들지 말고 해당 입력·조사 미해결 상태를 전달한다.
5. Global acquisition을 모든 item의 first-contact 문장으로 복사하지 않는다. 특정 profile의 first-contact에 acquisition이 필요하다면 같은 질문·해상도 근거를 요구한다.
6. 여러 axes를 한 문장으로 표현할 수 있으므로 axis별 문장·줄을 강제하지 않는다. 반대로 정보 축이 많다는 이유로 여기서 삭제하거나 대표 fact를 선택하지 않는다.
7. 아래 차이가 실제 registry/적용 사례에서 드러나는지 작성 중 확인하고 기준을 조정한다. 개수별 표본 quota나 별도 review Gate는 두지 않는다.
   - 서로 다른 성격의 아이템에서 조사 질문·첫 접촉 요구가 실질적으로 다른가.
   - 복수 맥락·역할을 합쳤을 때 한쪽 질문이 누락되지 않는가.
   - 정보가 적은 아이템에서 최소 용도·문장 수를 요구하지 않는가.
   - 풍부한 prose가 있어도 미조사 axis가 남으면 incomplete인가.
   - 미해결 이유가 단순 `자료 부족`을 넘어 부족한 질문·근거를 지목하는가.
8. 음식 관련 기준을 사용한다면 섭취 효과와 조리 활용을 구별할 수 있어야 한다. 실제 확인된 효과·맥락만 설명에 연결될 수 있고 모든 음식이 허기·갈증 해소와 조리 활용을 가진다고 가정하지 않는다. 이는 문형·전역 필수 axis가 아니라 의미 누락·과잉 일반화를 확인하는 사례다.
9. First-contact obligation은 해당 범위에 유효한 accepted facts가 있을 때 답해야 할 의미 요구다. Menu에 상세가 있다는 이유로 첫 이해 요구를 무시할 수 없다. Actual fact binding·KO/EN 표현·문장/줄 구성·omission 추적은 이번 구현에서 확정하지 않는다.

Validation: axis refs의 정합성뿐 아니라 사용자 질문·선정 근거·상세 경계가 존재하고 사례가 그 기준을 실질적으로 설명하는지 G1과 작성 중 내용 검토에서 확인한다. 기계 검사만으로 문장 품질이나 사용자 이해를 입증했다고 주장하지 않는다.

### Change 5 — 전체 적용·잔여 정리와 최종 채택

Purpose: 기준을 실제 target에 적용하고 하나의 최종 검증으로 결과를 채택한다.

Files: 신규 authority files, 조사 CLI, 기존 current route/config, canonical docs와 closeout.

Implementation Notes:

1. 정의 작성과 실제 사례 적용을 함께 진행해 registry·routing·first-contact 내용을 다듬는다. 전체 sweep 전 별도의 focused test 통과 단계나 registry 봉인 절차를 만들지 않는다.
2. 확정할 candidate revision에서 사용 가능한 source predicates와 routing을 전체 target에 실제 적용한다. 형식적 미조사 초기화만으로 완료하지 않는다.
3. Target당 한 application record를 작성한다. 공통 routing은 refs로 공유할 수 있지만 어떤 프로필이 적용·배제·미정인지 해석 가능해야 한다.
4. Explicit rows와 routing을 해석한 target coverage를 대조한다. 모든 item/profile 조합의 개별 evidence row나 물리적 행렬을 요구하지 않는다.
5. Gap은 기준 부족, 기존 질문 범위 보완, 증거 부족, 미조사, 적용 오류 등을 구별한다. Exact 대상·영향 질문·부족 근거·다음 판단을 식별한다. Unresolved 비율만으로 실패시키지 않는다.
6. 실제 semantic result가 없는 axes는 정직하게 열어 둔다. 작업 complete와 item complete를 별도로 보고한다.
7. 하나의 application 결과를 만들고 manifest에 정의·evidence·application·human contract를 결속한다. Target/registry/source가 다른 결과를 혼합하지 않는다.
8. Current route에 `layer3_investigation_contract` entry 한 건을 준비하고 기존 readpoint/product locator를 보존한다. Registry에는 새 focused test identity 한 건만 등록한다.
9. Contract·application·config·top docs를 포함하는 최종 subject를 준비한 뒤 §7 G1을 실행한다. Working-tree 채택 준비와 채택 성공 주장을 구분하며 G1 전에는 complete를 선언하거나 외부 배포하지 않는다.
10. 실패하면 원인을 교정하고 변경된 subject에 같은 G1을 재실행한다. 기존 current를 잘못 대체한 상태는 복구한다. 성공 후에는 검증 대상 member를 다시 바꾸지 않고 비member closeout에 실제 결과와 한계를 기록한다.

Validation: 최종 G1만 required Gate로 사용한다. 별도 A/B apply, pre/post check 또는 추가 confidence run은 수행하지 않는다.

---

## 7. Validation Plan

### Automated Validation

필수 Gate는 **G1 하나**다. 모든 구현·실제 적용·최종 route 준비가 끝난 subject에서 신규 test source 한 개를 실행한다. Required identity는 `test_layer3_investigation_contract.Layer3InvestigationContractTest.test_investigation_contract` 한 건으로 묶는다. 내부 helper와 subcase로 아래 범위를 확인하며 필요한 사례 수를 줄이거나 사례마다 required identity·runner를 추가하지 않는다.

실행 시작 보호 fingerprint를 담은 임시 JSON 경로를 다음 환경 변수로 제공한다. File은 read-only 상태 수집 결과이며 별도 validator·report authority가 아니다. 형식은 `execution_start_head`, 기존 dirty 정보, exact 보호 path/hash 목록과 선택된 generation member 목록에 필요한 최소 정보로 한다. Current route/config의 변경 전 값 중 보존할 부분도 포함할 수 있다. 이 입력은 writer가 사후 상태로 대체하지 않으며 `adoption` 모드에서 누락·손상되면 G1은 fail-closed한다.

```powershell
$env:IRIS_LAYER3_INVESTIGATION_MODE = 'adoption'
$env:IRIS_LAYER3_INVESTIGATION_BASELINE = '<실행 시작에 확보한 임시 baseline JSON의 절대 경로>'
uv run --project .\Iris\tooling --no-sync python -m pytest .\Iris\build\description\v2\tests\test_layer3_investigation_contract.py -q -p no:cacheprovider --round3-contract=diagnostic --round3-additional-source=Iris/build/description/v2/tests/test_layer3_investigation_contract.py
```

보호 비교는 이 실행에서 제품을 바꾸지 않았다는 근거다. Baseline은 investigation authority의 member가 아니며 장래의 정당한 제품 migration을 영구 금지하는 새 의미 계약으로 승격하지 않는다. `MODE`를 지정하지 않은 통상적인 required-test 재사용에서는 현재 계약·application·readpoint를 검사하고 과거 임시 baseline을 요구하지 않는다. 그 결과는 이번 실행의 no-mutation/adoption G1 PASS를 뜻하지 않는다. 이번 채택 성공은 위 `adoption` 모드의 exact command 결과로만 주장하며 알 수 없는 mode는 오류로 거부한다. 실행 종료 후 두 환경 변수는 이전 상태로 복원한다.

필수 보호 대상은 다음으로 한정한다.

- 기존 `layer3_successor` manifest와 네 member.
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`, `dvf_3_3_facts.jsonl`, `dvf_3_3_decisions.jsonl`, `tooltip_t1_layer3_owner_input.json`.
- 기존 `Iris/tooling/src/iris_tooling/build/compose_layer3_body_profile.py`, `compose_layer3_item.py`.
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua`와 그 pointer가 선택한 generation members.
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`, `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua`.
- 기존 current readpoint·product locators의 보존 부분. Current config의 계획된 additive 변경은 byte 불변 대상에서 제외한다.

패키지 tree, 저장소 전체 runtime/번역 tree, 임의 외부 파일은 탐색·캡처하지 않는다. 계획 밖 파일 변경은 diff 범위 확인으로 발견하며 정당한 범위 확장 없이 유지하지 않는다.

G1의 검사 범위:

| 영역 | 필요한 확인 |
|---|---|
| Target·schema·상속 | Exact source set, duplicate/missing/extra, case-sensitive identity, source/registry binding, 상속 manifest/member hashes |
| Applicability·routing | 근거 있는 적용·배제, 공통 member binding, 미정 범위·충돌 보존, 누락을 암묵적 N/A로 처리하지 않음 |
| Axis·completion | Context/contributor 보존, global acquisition 한 번, 근거로 배제된 범위와 실제 pending scope 구별, acquisition-only·low-information·invalid terminal 사례 |
| Acquisition 소비 경계 | Bound contract의 allowed kind/binding/resolved 요구를 실제 해석. Producer none/assignment 0과 accepted instance 부재 구별. Admissible 외부 결과의 결속과 unsupported negative 거부 |
| First-contact | 질문·필요 이유·상세 경계와 참조, 복수 맥락 union, fact 미해결 시 obligation 유지, 대표 선택·전역 acquisition 문장화 금지 |
| 결정성 | 작은 사례의 동일 계산 반복과 profile/contributor 입력 순서 변경에서 의미 결과 일치. 별도 전체 A/B output은 만들지 않음 |
| 실제 적용 결과 | 전체 applications를 한 번 재계산·대조하고 exact target coverage, routing 해석, 저장된 completion과 잔여 상태의 정합성 확인 |
| 최종 연결·보호 | Final manifest members와 current link/validation identity, 기존 readpoint와 명시적 보호 대상 불변, 기존 CLI dispatch의 관련 동작 보존 |

상속 JSON의 `/semantic_node/allowed_fact_kinds`, `/semantic_node/bindings/acquisition_unobtainable`, `/acquisition/resolved_requires`를 bound bytes에서 해석한다. Missing/type/value mismatch를 fallback으로 숨기지 않는다. 동일 검사를 별도 Gate나 pointer별 테스트 파일로 나누지 않는다.

Source binding 검증과 작은 synthetic negative cases는 필요하지만 source-specific negative producer 전체를 구현하지 않는다. 실제 source 의미·완전성을 hash 일치만으로 증명했다고 주장하지 않는다.

G1 PASS는 exact command exit `0`이고 해당 source가 실제 collect·execute됐을 때만 가능하다. `0 collected`, import failure, deselection 또는 필요한 tooling 부재를 성공으로 처리하지 않는다. 실패 교정 후 같은 Gate 재실행은 허용하며, 성공 이후 추가 confidence만을 위한 반복 실행은 요구하지 않는다.

### Manual Validation

작성 중 다음 내용 판단을 수행하고 결과를 contract의 설명·사례와 단일 closeout에 남긴다. 이는 별도 reviewer, approval, pre-sweep Gate나 독립 evidence package가 아니다.

- 프로필 질문의 실질적인 차이, overlap·routing 근거와 배제 한계.
- 실제 적용 사례에서 다양한 아이템 성격, 복수 의미, 희소 정보, 미해결 원인이 구별되는지.
- First-contact 선정 근거가 단순 우선순위나 label 반복이 아닌지, 상세 정보와 구별되는지.
- 전체 적용에서 기준 자체의 결함을 source 부족이라는 이유로 숨기지 않았는지.
- Diff가 허용 범위에 있고 기존 사용자 변경과 product를 보존했는지.

### Validation Limits

- 실제 semantic/acquisition 전수 정확성·완전성, 모든 item complete를 증명하지 않는다.
- 최종 KO/EN 자연성·Tooltip 한 줄 적합성·실게임 이해도·runtime/package/compatibility를 검증하지 않는다.
- Full repository suite, current-required runner 전체, clean-checkout gate, 기존 L3-01 test 전체 재실행, Lua syntax, package/install, 실제 PZ 검사를 추가하지 않는다.
- 별도 `capture-protection` product CLI, `check` subcommand, 전체 A/B 실행, 채택 전후 이중 검증, 외부 전용 workspace, before/after/report 세트, 검증 결과의 재검증을 요구하지 않는다.
- Runtime/generator/package 등 계획 밖 구현 변경이 필요하면 먼저 범위와 위험을 재판정하고 해당 변경에 필요한 검증만 계획에 추가한다.
- 임시 baseline 경로·내용과 실행 결과는 investigation manifest/semantic identity에 포함하지 않는다. 단일 closeout은 검사 범위·시작 기준·실제 결과·한계를 기록하면 된다. 임시 파일의 영구 봉인·해시 보관은 요구하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

변경 있음. Profile/axis/routing/completion/first-contact 기준과 실제 application authority를 추가한다. 의미 fact producer나 새로운 전역 validation policy는 만들지 않는다.

### Runtime Behavior Surface

직접 변경 없음. Python 조사 명령만 추가한다. 기존 CLI dispatch를 잘못 연결해 composer·publisher를 실행하는 간접 회귀는 G1의 관련 검사와 diff로 확인한다.

### Compatibility Surface

외부 API/SPI/package 변경 없음. 신규 내부 schema와 source/registry binding을 명시하며 알 수 없는 상태를 자동 성공·미적용으로 해석하지 않는다.

### Sealed Artifact Surface

기존 successor bundle은 불변이다. 신규 investigation bundle과 current readpoint, test source/required identity, 필요한 `.gitattributes` 경로만 추가한다. 기존 historical snapshot을 재작성하지 않는다. Definition/application의 정식 변경에는 명시적 revision과 영향 범위 재평가를 사용하지만, 작은 변경마다 새 proof tree나 approval ceremony를 요구하지 않는다.

### Public-Facing Output Surface

없음. Menu·Tooltip·KO/EN 제품 설명은 바뀌지 않는다. Canonical docs는 investigation 기준의 완료와 실제 제품 전환 미수행을 구분한다.

---

## 9. Risk Analysis

### Architecture Risk

- 기존 단일 compose profile 재사용으로 대표 의미가 복원될 수 있다. Investigation 책임과 기존 composer를 분리한다.
- Routing이 누락을 숨기는 shortcut이 될 수 있다. Exact predicate/member binding, 미배제 범위와 gap을 보존한다.
- 모든 프로필의 개별 심층조사를 강제하면 적용되지 않는다는 증명에 작업이 치우칠 수 있다. 근거 있는 공통 배제와 잠재 scope를 구별한다.
- 구조적으로 완전하지만 내용이 빈약한 registry가 채택될 수 있다. First-contact 질문·선정 이유·상세 경계와 실제 적용 사용 가능성을 완료 조건에 둔다.

### Runtime Risk

- 직접 runtime 변경은 없다. 명령 dispatch·잘못된 output target이 기존 product를 변경할 위험은 bounded baseline과 최종 G1으로 확인한다.
- First-contact 정보가 많다는 문제를 upstream 질문 삭제로 해결하지 않는다. 실제 표현상의 제약은 미확정으로 남긴다.

### Compatibility Risk

- Extraction의 부재를 전역 negative로 확대할 수 있다. Source의 적용 범위·완전성·한계를 기준으로 배제를 정당화한다.
- Source·profile revision 변화 후 stale application을 소비할 수 있다. 결속을 확인하고 관련 범위를 재평가한다.
- Schema 설계를 너무 빨리 고정할 수 있다. 실제 사례 적용과 기준 수정을 함께 진행한 후 초기 revision을 채택한다.

### Regression Risk

- Count equality를 exact set equality로 오판정하지 않는다.
- Context/contributor dedup 손실과 scope 미정의 complete 승격을 작은 판정 사례와 전체 재계산에서 확인한다.
- Validator·writer의 같은 오류가 통과할 수 있다. 핵심 boundary cases에는 독립적으로 정한 기대 결과를 사용하되 새로운 검증 framework는 만들지 않는다.
- Unresolved 허용이 형식적 완료에 악용될 수 있다. 실제 source 적용, 기준 결함과 source 부족 구분, 구체 blocker를 요구하되 미해결 비율만으로 실패시키지 않는다.

---

## 10. Rollback Plan

- G1 이전에는 채택 준비 상태다. 실패한 신규 readpoint를 current 성공 상태로 남기거나 외부 배포하지 않는다.
- 자신의 신규 entry·등록·문서 변경만 실행 시작 상태와 비교해 복구한다. 기존 dirty 변경과 successor bundle/product를 reset하지 않는다.
- Scope 모델 결함이면 영향받은 정의·application을 교정하고 같은 G1을 다시 실행한다. 미해결을 억지로 지워 통과시키지 않는다.
- 보호 대상의 예상 밖 변경은 원인을 확인하고 자신의 변경만 복구한다. Baseline을 사후 상태로 다시 캡처해 차이를 숨기지 않는다.
- 채택 후 의미 변경은 기존 결과의 변경 이유와 revision·영향 범위를 명시해 current readpoint를 갱신한다. 단순 관측·문서 보완을 자동으로 새 Gate 제도로 확대하지 않는다.

---

## 11. Governance Constraints

- Iris의 근거 기반·비추천·근거 부족 시 침묵·읽기 전용 원칙을 유지한다.
- Layer 1~5와 Recipe/Right-click의 독립성을 유지하며 다른 Layer의 출력에서 사실을 만들지 않는다.
- Exact identity, no-primary, context-local/fact-local 관계와 독립 상태 축을 재정의하지 않는다.
- Heavy는 disclosure·evidence·closeout 의무이며 추가 반복 검사나 승인식의 자동 근거가 아니다.
- 기존 source policy와 required validation guard를 끄거나 과거 승인을 새 승인으로 재사용하지 않는다. 실제 세션의 승인 범위만 기록한다.
- 미확인을 0·N/A·완료로 바꾸지 않는다. 계획 작성이나 application 생성만으로 adoption 성공을 선언하지 않는다.
- 새 산출물·테스트·검사 단계는 위 범위로 제한한다. 단순 confidence 확대를 위한 별도 seal/receipt/manifest/census/proof artifact를 추가하지 않는다.

---

## 12. Expected Closeout State

목표는 `complete`이며 적용 범위는 **조사 기준 + 실제 전체 target 적용·잔여 추적 + investigation authority 채택**이다.

다음 결과가 필요하다.

1. 프로필이 무엇을 조사하고 왜 구별되는지 설명하며 대표 의미를 선택하지 않는다.
2. 전체 target에 application이 있고 적용·배제·미정 범위가 explicit evidence 또는 근거 있는 routing으로 설명된다.
3. 개별 심층조사가 필요 없는 범위와 적용 가능성이 남은 미해결 범위를 구별한다.
4. Scoped axes와 contributor가 보존되고 item completion은 필요한 조사 범위·axis terminal·acquisition의 함수로 계산된다.
5. Acquisition-only·prose 존재·fact 개수로 전체 완료를 판정하지 않는다. Unsupported negative terminal claim은 거부한다.
6. First-contact 축의 사용자 질문·선정 이유·상세 경계가 실질적으로 정의돼 있다. 설명 구성자가 기준을 처음부터 재설계할 필요가 없어야 한다.
7. 서로 다른 성격·다중 의미·희소 정보·미해결의 실제 적용 사례에서 기준의 사용 가능성이 드러난다. 임의의 profile 수·sample quota·unresolved 0 조건은 없다.
8. 잔여는 단순 총계가 아니라 정확한 대상·영향 질문·부족 근거·다음 판단으로 설명된다. 기준 결함과 source 부족을 구별한다.
9. 최종 G1 exact command가 exit `0`이며 actual application·final route·상속/보호 경계를 확인했다.
10. 단일 closeout에 시작 기준, 실제 명령·결과, 내용 검토의 결론, 잔여와 validated/unvalidated/out-of-scope 범위를 기록한다.

`partial`은 기준 또는 전체 적용의 일부만 완료된 상태, `implemented_only`는 구현했지만 G1·채택 결속이 완료되지 않은 상태다. 필수 authority/tooling 부재는 해당 범위의 blocker이며 개별 item unresolved와 구별한다.

허용되는 완료 주장:

> 각 아이템에 필요한 조사 질문과 첫 접촉 정보 기준을 근거에 따라 정의하고, 적용·배제·미해결을 구분하며, 전체 대상을 실제로 추적할 수 있는 기준과 application을 확립했다.

실제 semantic/acquisition 전수 조사 완료, 모든 item complete, KO/EN·S2 문장 완성, runtime/current product migration, package/PZ 검증과 release readiness는 주장하지 않는다.
