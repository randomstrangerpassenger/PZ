# Iris Layer 3 Body-Role Realignment Walkthrough

> Session date: 2026-08-21 KST  
> Status: staging closeout complete  
> Validated terminal subject: `1197ccc99085666d336e3ed493555e26810104e5`  
> Validated terminal tree: `da2bf2e5ec595b8de1ea41ee2fafb7e433c058db`  
> Closeout token: `layer3_role_realign_staging_complete`

## 1. Outcome

이번 작업은 Layer 3를 모든 item에 강제되는 상세 설명이 아니라 confirmed description material이 있을 때 제공하는 선택적 overview 계층으로 재정렬했다.

Current item과 existing Layer 3 body를 전수 분류하고, core description과 acquisition information을 source-bound fact 단위로 분리했다. Menu용 flat candidate와 Tooltip용 role-labeled input readiness를 만들었지만 current generation, runtime payload, package와 UI는 변경하지 않았다.

Exact tracked terminal subject는 mandatory full-repository Clean-Checkout Run A/B와 deterministic comparison을 통과했다. 따라서 staging 범위의 closeout token을 기록했다.

## 2. Implemented Route

구현 흐름은 다음과 같다.

`current exact facts + provenance mapping + optional one-off IPS Layer 3 axes -> disposition/readiness -> core/acquisition role material -> staging successor + Problem 5A handoff`

주요 구성은 다음과 같다.

- Hash-bound policy, mapping, defect/transformation, review-capacity와 tooling-disposition contract
- 모든 existing body에 대한 5-state disposition
- 모든 canonical FullType에 대한 독립 5-state readiness
- Rendered-string 의미 추론 없이 source slot, fact origin과 registered lineage만 사용하는 pure evaluator
- `core_description`과 `acquisition_information`의 물리적 분리 및 fact ID 보존
- `preserve_current_publicity` Menu four-case projection
- Tooltip UI가 아닌 role-labeled input readiness
- 서로 다른 isolated root를 사용하는 deterministic candidate replay A/B
- `insufficient_material`만 투영하는 exact Problem 5A handoff
- Staging subject만 읽는 read-only validator

보존된 Item-Page Information Sufficiency 결과는 one-off snapshot으로만 사용했다. Input identity가 current일 때 per-item Layer 3 axes를 readiness 보조 근거로 소비했으며 page disposition, Layer 4 axes와 gap inventory를 disposition/readiness/Problem 5A로 직접 변환하지 않았다.

## 3. Final Staging Result

### Body disposition

| Disposition | Count |
| --- | ---: |
| `keep` | 38 |
| `reduce` | 770 |
| `revise` | 1,262 |
| `hide` | 2 |
| `review_hold` | 12 |
| Total existing body | 2,084 |

### Description readiness

| Readiness | Count |
| --- | ---: |
| `description_ready` | 1,300 |
| `acquisition_only` | 770 |
| `omission_allowed` | 180 |
| `insufficient_material` | 2 |
| `review_required` | 33 |
| Total item | 2,285 |

Candidate replay A/B는 모두 다음 identity를 재현했다.

- Evidence status: `current_snapshot`
- Confirmed fact count: `5,197`
- Successor entries SHA-256: `17789343f34bfc013d71460118819369913f85a073f319e93335c614cacaa200`
- Problem 5A candidate: `Base.Bleach`, `Base.Rope`
- Required manual review: `33/33` complete
- Exact duplicate group representative review: `184/184` complete
- Source-bound acquisition: `1,050`
- Successor-projected acquisition: `1,050`
- Acquisition loss: `0`
- Blocking finding: `0`

## 4. Full-Repository Blocker Repairs

Staging 구현은 완료돼 있었지만 mandatory full-repository gate가 실제 repository integration 문제를 드러냈다. 수정 범위는 blocker를 직접 닫는 데 한정했다.

### Current-generation authority anchor

ARCHITECTURE와 ROADMAP의 current-generation authority anchor를 숫자 기반의 불안정한 위치 탐색에서 exact semantic anchor 탐색으로 바꿨다. 각 문서에서 anchor가 정확히 하나 존재하고 의도한 문맥으로 이동하는 regression을 추가했다.

### Closeout claim scan

Markdown inline identifier가 실제 completion claim으로 오인되던 false positive를 제거했다. Exact architecture definition과 routing/ownership 설명은 허용하되 실제 scope-exceeding claim은 계속 차단하도록 regression을 추가했다.

### Residual lifecycle recognition

Tracked historical overlay와 그 superseded validator row를 기존 lifecycle chronology대로 다시 인식하도록 residual validator를 복원하고 focused regression을 추가했다.

### Source disposition and adoption identity

Layer 3 focused test는 기존 dedicated route로 유지했다. 동시에 tracked Layer 4 interaction-presentation test를 `not_applicable_dedicated_route`로 명시해 full-gate source census를 완전하게 만들었다. Layer 4 제품 구현 파일은 수정하지 않았다. Full-gate contract의 새 blob identity는 기존 adoption binding에 갱신했다.

### Windows clean-checkout byte identity

Windows checkout에서 Layer 3 policy/replay 자료와 두 current-authority cutover JSON이 EOL 변환으로 시작부터 dirty가 되지 않도록 exact `.gitattributes` raw-byte 정책을 추가했다.

### Taxonomy identity

Anchor relocation regression 한 건이 current taxonomy identity set에 누락돼 canonical result가 실패한 것을 확인했다. 해당 test ID 한 row만 existing taxonomy authority와 protected chronology에 추가했다.

## 5. Validation Walkthrough

계획에 명시된 검증은 구현 변경을 마친 뒤 집중해서 실행했다.

### Focused and candidate validation

- Final focused test: `8 passed`
- Independent candidate replay A/B: both `candidate_complete`
- Read-only validator A/B: both `PASS`
- Candidate raw-byte comparison: exit `0`

Consumer-anchor, closeout-claim과 residual-lifecycle blocker의 focused regressions도 각각 exit `0`으로 확인했다. 이 일회성 focused 실행이나 외부 candidate root는 새 canonical validator 또는 validation authority가 아니다.

### Clean-Checkout Run A

Exact subject `1197ccc99085666d336e3ed493555e26810104e5`에 대한 fresh Run A 결과는 다음과 같다.

- Pytest: `433 passed, 2 deselected, 117 subtests passed`
- Standalone validation: `4/4 PASS`
- Canonical result: `PASS`
- Current taxonomy identity set equality: true
- Selected source set equality: true
- Source checkout clean before/after: true
- External execution mutation: `0`
- Cleanup: `PASS`

### Clean-Checkout Run B

Run A가 PASS한 뒤 별도의 fresh root에서 Run B를 실행했다.

- Pytest: `433 passed, 2 deselected, 117 subtests passed`
- Standalone validation: `4/4 PASS`
- Canonical result: `PASS`
- Current taxonomy identity set equality: true
- Selected source set equality: true
- Source checkout clean before/after: true
- External execution mutation: `0`
- Cleanup: `PASS`

### Deterministic comparison

Canonical comparator는 exit `0`으로 완료됐다.

- Canonical result raw bytes equal: true
- Run A/B canonical result SHA-256: `75775172c99a198f5df6a45dbee30a8836f03ded4fba4098686d2d8be7887333`
- Required execution unit count: `437`
- Test identity count: `433`
- Test inventory SHA-256: `c4b1679db1e37e56eb87e18e7f3847a8e65b6056f64e6f57bf8ca6f817b39772`

## 6. Failure-to-Fix Sequence

첫 full-gate 시도는 pytest `433`개와 standalone `4`개가 모두 통과했지만 execution checkout의 두 tracked JSON이 EOL 변환으로 시작부터 dirty여서 실패했다. 두 exact path의 raw-byte 보존 규칙을 추가해 이 문제를 닫았다.

그 다음 exact subject의 full-gate는 checkout cleanliness와 모든 test가 통과했지만 `current_taxonomy_identity_set_equal=false`로 실패했다. 원인은 새 anchor regression test ID 한 건의 taxonomy 누락이었다. Existing taxonomy에 그 row만 추가한 뒤 새 exact subject를 freeze하고 focused/candidate validation과 Run A/B를 다시 수행했다.

최종 subject에서는 두 조건이 모두 닫혔다. 실패 receipt는 PASS로 재해석하거나 predecessor PASS로 상속하지 않았다.

## 7. Closeout and Evidence Separation

Validated terminal subject는 `1197ccc99085666d336e3ed493555e26810104e5`다. Run A/B result identity는 이 commit에 역으로 넣지 않았다.

검증 뒤 다음 두 tracked artifact만 post-validation closeout으로 추가했다.

- `Iris/_docs/round3/layer3_body_role_realign/evidence_carriers/1197ccc99085666d336e3ed493555e26810104e5/clean_checkout_result_pointer.json`
- `Iris/_docs/round3/layer3_body_role_realign/17789343f34bfc013d71460118819369913f85a073f319e93335c614cacaa200/axis_qualified_closeout.json`

Result pointer는 external receipt의 path/hash를 가리키는 evidence-only carrier다. Axis-qualified closeout은 staging 완료 axis와 non-claim을 기록한다. 둘 다 validated terminal subject를 재정의하거나 current generation/runtime/package authority 또는 새 validation authority가 되지 않는다.

`DECISIONS.md`, `ROADMAP.md`, `ARCHITECTURE.md`도 같은 subject 분리, token 의미와 staging-only 경계를 반영하도록 정렬했다.

## 8. Commit Map

| Commit | Role |
| --- | --- |
| `3aeb33fb` | Consumer anchor, closeout scan과 residual lifecycle full-gate blockers 교정 |
| `508d2019` | Layer 4 dedicated test source disposition 명시 |
| `12139ad0` | Full-gate adoption blob binding 갱신 |
| `61db4d5f` | Layer 3 evidence bytes의 clean-checkout 보존 |
| `7dffa842` | Current-authority cutover report bytes의 clean-checkout 보존 |
| `1197ccc9` | Anchor regression taxonomy identity 결속 및 final validated subject freeze |
| `da81e29a` | Post-validation evidence carrier, closeout token과 walkthrough synchronization |
| `3a7828bb` | DECISIONS, ROADMAP과 ARCHITECTURE authority alignment |

모든 commit은 local `main`에 있고 원격 push는 수행하지 않았다.

## 9. Explicit Non-Claims

이번 closeout은 다음을 의미하지 않는다.

- Current Layer 3 generation installation
- Current runtime 또는 package projection update
- Menu public text replacement
- Tooltip UI, line allocation 또는 4-line layout completion
- Problem 5A enrichment 완료 또는 실행 승인
- Stateful Artifact Registry authority/lifecycle/receipt PASS
- Registry Runtime Compatibility PASS
- Publish PASS
- Release, Workshop 또는 deployment readiness

별도 current installation을 실행하려면 staging successor의 explicit upstream adoption, canonical seven-input complete-generation build/validate/install, runtime/package checks와 install subject의 fresh mandatory repository Run A/B가 필요하다.
