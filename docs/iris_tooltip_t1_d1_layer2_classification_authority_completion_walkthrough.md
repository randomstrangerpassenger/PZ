# Iris Tooltip T1-D1 Layer 2 Classification Authority Completion Walkthrough

> 작성일: 2026-08-29 KST
> 구현 계획: `docs/iris_tooltip_t1_d1_layer2_classification_authority_completion_plan.md`
> 병렬 실행 계약: `docs/iris_tooltip_t1_parallel_workstream_execution_contract.md`
> 공통 predecessor: `6b7118dc229bf8138302696e1aa5e5b7454589dc` / tree `4eae6fbdb3d0b2cb532f875b96137335a403f2fc`
> strict D1 implementation: `81eb49b062137d5ae8b93cd5bfeb17d08f3d3a56` / tree `064cb1bd8c7c4bb2056410addd2f9b50e9505ee4`
> optional Layer 2 successor: `8bbc40169e86bd2e818c440a823e497f852a1e69` / tree `e950a552797012e6e40523e75b93a1ed203e839b`
> 상태: D1 successor workstream complete; D2 partition ready; current adoption pending T1-D6; T2 blocked

## 1. 문서의 역할

이 문서는 현재 세션에서 수행한 Tooltip T1-D1 Layer 2 Classification 작업을 시간 순서와
책임 경계에 따라 설명하는 narrative walkthrough다. Strict D1 계획을 구현한 결과가 왜
처음에는 `partial`이었는지, product/contract owner의 successor amendment가 무엇을
바꾸었는지, 그리고 D6가 소비할 외부 bundle lineage를 어떻게 정정했는지를 한 흐름으로
읽을 수 있게 하는 것이 목적이다.

이 문서는 다음 역할을 갖지 않는다.

- Classification registry, Tooltip T1 decision contract, owner output 또는 external bundle을
  대체하지 않는다.
- canonical validator, 정규 검사기, 새 validation authority, seal, receipt 또는 manifest가
  아니다.
- display silence `874`에 새로운 item별 semantic 판정을 부여하지 않는다.
- D2 구현, D6 integration, global current adoption, canonical full gate/finalizer 또는
  production T2 handoff를 완료했다고 주장하지 않는다.
- runtime/release/deployment acceptance를 주장하지 않는다.

## 2. 시작점과 실행 경계

작업은 `docs/Philosophy.md`의 Iris 원칙을 기준으로 진행했다. Iris는 확인 가능한 근거에
기반한 정보를 Menu와 Tooltip에 서로 다른 깊이로 표시하며, 근거가 부족하면 추측해서
채우지 않는다. 이 작업에서도 FullType 이름, Layer 3/4 설명, presentation rank, source
iteration order 또는 raw fallback ID에서 Layer 2 semantic primary를 추론하지 않았다.

병렬 실행 공통 기준은 다음 exact subject였다.

```text
common predecessor commit = 6b7118dc229bf8138302696e1aa5e5b7454589dc
common predecessor tree   = 4eae6fbdb3d0b2cb532f875b96137335a403f2fc
predecessor closeout SHA  = 6e255227b0aa8381453a563e3ede9e96c59be82c9bb3a7cb6eba8f488039b4a3
support predicate         = current-owner-fulltype-union-v1
identity                  = case-sensitive exact FullType
```

Support hash는 공통 계약의 canonical rule, 즉 중복 제거한 exact FullType을 ordinal
ascending으로 정렬하고 각 UTF-8 value 뒤에 LF를 붙인 바이트의 SHA-256으로 계산했다.

```text
support count  = 2,280
support SHA-256 = 3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6
```

작업 범위는 Classification-owned registry/output와 T1 Layer 2 input/audit contract였다.
Menu/runtime/public source, global-current manifest/route, D2 consumer implementation과 T2
payload는 수정 범위가 아니었다. Owner approval이 필요한 gate는 세션 시작 프롬프트의
사전 승인과 후속 explicit amendment로 처리했고, 도구나 플랫폼의 별도 권한 요구는
우회하지 않았다.

## 3. Strict D1 구현

첫 구현 commit은 다음과 같다.

```text
commit = 81eb49b062137d5ae8b93cd5bfeb17d08f3d3a56
tree   = 064cb1bd8c7c4bb2056410addd2f9b50e9505ee4
title  = Implement Tooltip T1-D1 Layer 2 owner candidate
delta  = 21 files, +1,158 / -27
```

### 3.1 Classification owner 경로

Strict implementation은 다음 역할을 분리했다.

- `layer2_census.py`: support FullType과 membership/primary/fallback 상태 census
- `layer2_contract.py`: schema와 terminal vocabulary
- `layer2_materializer.py`: deterministic owner output candidate 생성
- `layer2_validator.py`: support completeness, identity, provenance와 surface 검증
- `classification_layer2_resolution_registry.json`: bounded Classification resolution input
- `classification_layer2_surface_catalog.json`: category/subcategory KO/EN surface authority
- `classification_layer2_owner_output.json`: T1과 D2가 읽을 canonical owner output
- Tooltip T1 contract/audit 변경: owner output relation을 읽되 runtime resolver나 raw tag
  inference를 복제하지 않음

Materializer와 validator는 exact FullType, category/primary identity, 별도 category/subcategory
surface, authority와 provenance를 함께 다뤘다. Menu output 자기대조를 consumer evidence로
간주하지 않았고, Menu correction은 D2 owner에게 남겼다.

### 3.2 Strict terminal 결과

원래 계획은 support `2,280` 모두를 `resolved` 또는 positive owner evidence가 있는
`owner_approved_absence`로 닫도록 요구했다. 실제 current Classification source에서 안전하게
확정할 수 있었던 행은 `1,406`이었다.

```text
resolved                              = 1,406
raw Misc.9-A fallback not admissible  =   408
no membership record                  =   201
multi-membership without primary      =   265
remaining strict Classification rows  =   874
```

Fallback `408`을 resolved classification으로 승격하지 않았고, membership이 없거나
admissible primary가 없는 `466`도 이름·Layer 3/4·표시 순서로 채우지 않았다. 또한 positive
owner evidence가 없었으므로 이들을 item별 `owner_approved_absence`로 발명하지 않았다.

따라서 strict plan의 all-row semantic-terminal success condition 아래에서는 유효한 `1,406`
resolved output을 보존하면서 Classification correction `874`가 남은 `partial`이 정직한
terminal 판정이었다. 다른 owner correction 분포는 바꾸지 않았고 T2는 계속 blocked였다.

## 4. 최초 bundle 위치 정정

첫 closeout 시도는 repository 내부인 `.git/codex-artifacts/**` 아래에 발행되었다. 이 위치는
공통 계약 §6의 `repository-external immutable empty root` 조건을 충족하지 않으므로
current/adopted evidence로 사용할 수 없었다.

Source, semantic registry와 correction 결과는 변경하지 않고 strict D1 bundle을 다음 외부
root에 다시 발행했다.

```text
C:\Users\MW\Downloads\coding\PZ-t1d1-external-81eb49b0
```

이 외부 bundle의 manifest SHA-256은
`e63fb1a9d954c64062908ffbb7e0c7244b9bdb46ed51facd0ab61013f071e4cb`다. 이후 owner
amendment가 만들어 낸 successor가 strict partial을 대체했으므로, 이 bundle은 현재 D6
active input이 아니라 intermediate semantic/implementation lineage evidence로만 남는다.
Repository 내부 최초 시도도 canonical/current evidence로 주장하지 않는다.

## 5. Owner-approved optional Layer 2 amendment

Product/contract owner는 strict 계획의 all-support-row semantic-terminal requirement를 다음
system-level decision으로 supersede했다.

```text
Tooltip Layer 2 S1 = optional navigation/display projection

display condition:
  current Classification authority가
  user-facing category + admissible primary subcategory를 함께 제공

otherwise:
  legitimate display silence
  S1 placeholder/empty line 없음
  S2-S4 compact
```

이 결정은 `874`개의 classification을 새로 발명한 것이 아니다. 다음 세 source state를
deterministic applicability rule로 display silence에 배치했다.

| Source state | Count | Disposition |
| --- | ---: | --- |
| raw `Misc.9-A` fallback | 408 | raw ID를 표시하거나 resolved로 승격하지 않고 S1 silence |
| membership 없음 | 201 | 이름·Layer 3/4 추론 없이 S1 silence |
| multi-membership, admissible primary 없음 | 265 | rank/source order 승격 없이 S1 silence |
| 합계 | 874 | non-correction display partition |

Item별 positive absence record `874`개는 만들지 않았다. 하나의 owner-approved system
contract disposition과 source-state 기반 applicability rule만 사용했다. Menu가 더 상세한
정보를 표시할 수 있다는 기존 원칙도 유지했다. `same-authority`는 같은 fact source를
사용한다는 뜻이며 두 surface의 coverage가 항상 같아야 한다는 뜻은 아니다.

## 6. D1 successor 결과

Optional Layer 2 amendment를 반영한 successor는 다음 exact subject다.

```text
commit = 8bbc40169e86bd2e818c440a823e497f852a1e69
tree   = e950a552797012e6e40523e75b93a1ed203e839b
title  = Adopt optional Tooltip Layer 2 applicability
delta from direct parent = 16 files, +295 / -102
```

Successor는 resolution contract, owner-output schema/data, Tooltip T1 input/decision contract,
Classification materializer/validator, T1 audit/contract와 기존 focused test parameter rows를
최소 변경했다. 새 test file이나 top-level test family는 만들지 않았다.

최종 exact partition은 다음과 같다.

| Partition | Count | Exact FullType SHA-256 |
| --- | ---: | --- |
| support | 2,280 | `3a6cc24b9ad64e06a0a6c0408821201e35bbd1d8558e6245809b5d3c34265ce6` |
| `layer2_applicable` | 1,406 | `c5a77d86eb875cecf03edf5ab67f29361f58947bd97493e522667b593130f264` |
| `layer2_display_silence` | 874 | `d13fa6ac9072a3ab2c61bc59990bfb948010ce8b2fc3211aa1ecb7b5c6c121de` |

`1,406 + 874 = 2,280`이며 두 하위 set은 exact partition이다. 기존 resolved `1,406`의
canonical row SHA-256은
`f36a6a6c72080bae8b28b9a1c419eff2ca2a15fc192be04edbfb5be40d31833f`로 direct parent와
byte/identity/surface가 동일하다.

```text
Classification correction before = 874
Classification correction after  = 0
display silence                    = 874 (separate non-correction partition)
semantic inference                 = false
per-FullType positive absence rows = 0
```

이 결과로 D1 successor의 workstream terminal은 `complete`가 되었다. 이 `complete`는
optional Layer 2 applicability 계약과 Classification correction bundle에만 적용된다.

## 7. D2 handoff와 남은 T2 blocker

D1은 D2가 소비할 다음 exact relation을 제공한다.

```text
layer2_applicable      = 1,406
layer2_display_silence =   874
partition_complete     = true
```

D2는 applicable row에만 S1을 표시하고 display-silence row는 placeholder 없이 N/A로
처리해야 한다. Menu consumer relation과 applicable/N/A parity는 D2가 소유한다. D1은 Menu
correction `2,280`을 산술 차감하거나 자동으로 닫지 않았다.

Successor re-audit의 actual other-owner correction 분포는 다음과 같다.

| Owner / reason | Count |
| --- | ---: |
| DVF owner / `DVF_OWNER_ROW_MISSING` | 175 |
| Iris presentation-contract owner / `SUPPORT_NORMALIZED_COLLISION` | 2 |
| Menu consumer owner / `PARITY_AUTHORITY_RELATION_MISSING` | 2,280 |
| QG/locale owner / `LOCALE_SELECTED_SURFACE_MISSING` | 888 |
| 합계 | 3,345 |

따라서 D2 semantic partition은 ready지만 전체 T2 상태는 다음과 같다.

```text
T2_FULL_DATA_PROGRESSION = BLOCKED_BY_UPSTREAM_CORRECTIONS
production_t2_handoff    = absent
```

## 8. D6 cumulative lineage 정정

첫 successor bundle은 direct parent D1 `81eb49b...`에서 final successor `8bbc401...`까지의
7-path successor-only delta를 가리켰다. D6가 그 bundle 하나만 적용하면 common T1-C
predecessor에서 strict D1 implementation까지의 변경을 잃을 수 있었다.

Source commit, semantic partition과 검증 결과는 바꾸지 않고 bundle metadata를 다시
발행했다. Final lineage는 다음과 같다.

```text
common T1-C predecessor
  6b7118dc229bf8138302696e1aa5e5b7454589dc
  tree 4eae6fbdb3d0b2cb532f875b96137335a403f2fc

direct parent D1
  81eb49b062137d5ae8b93cd5bfeb17d08f3d3a56
  tree 064cb1bd8c7c4bb2056410addd2f9b50e9505ee4

final D1 successor
  8bbc40169e86bd2e818c440a823e497f852a1e69
  tree e950a552797012e6e40523e75b93a1ed203e839b
```

D6 shared delta는 common predecessor에서 final successor까지의 cumulative delta다. 각
entry의 base blob은 T1-C, proposed blob은 final successor를 가리킨다. Corrected final
bundle 하나만 active D6 input이며 strict partial bundle과 non-cumulative successor bundle은
적용하지 않는다.

### 8.1 Final external bundle

```text
root:
C:\Users\MW\Downloads\coding\PZ-t1d1-successor-cumulative-8bbc4016

manifest:
d1_successor_cumulative_integration_manifest.json
SHA-256 ae91527431f5d34d0ca7c6fc6b86082b9c7e6f33b7ceabc39741ad2093641c3e

shared delta:
d1_successor_cumulative_shared_path_delta.json
SHA-256 5dcf432e36ae5ff2d2b8469faca0b983b37c96380985f46cd1af490c0e2cbed4

closeout:
t1d1_successor_cumulative_closeout.json
SHA-256 b1ac3157b04abada0bf153009022b7c4ee8118a160525fb129c5e2b8db27c7f3
```

Inactive lineage는 다음처럼 보존했다.

- strict partial external manifest SHA-256:
  `e63fb1a9d954c64062908ffbb7e0c7244b9bdb46ed51facd0ab61013f071e4cb`
- superseded non-cumulative successor manifest SHA-256:
  `99e5c3880a8b1493d8f743291061c38a4a7d744ede494fe9f22c986d6dd7e05d`

`remaining_entries`는 Classification correction remaining `0`을 명시한다. Display silence
`874`는 이 빈 correction set에 포함되지 않는 별도 partition이다.

## 9. 실행한 검증

계획과 공통 계약이 요구한 focused family를 successor 최종 단계에서 실행했다.

```powershell
uv run --project .\Iris\tooling python -B -m pytest `
  .\Iris\tooling\tests\test_classification_candidate_install.py `
  .\Iris\tooling\tests\test_tooltip_t1_contract.py `
  .\Iris\tooling\tests\test_tooltip_t1_projection.py `
  .\Iris\tooling\tests\test_tooltip_t1_audit.py -q
```

```text
result    = 74 passed
exit code = 0
```

주요 machine 결과는 다음과 같다.

| Check | Result |
| --- | --- |
| Candidate Run A | exit `0`, output SHA-256 `ade92e99d85da959374daa89ee3ed53d618e1c2e6e2030e25005de6250e09bae` |
| Candidate Run B | exit `0`, same output SHA-256 |
| Candidate byte comparator | equal, exit `0` |
| Classification validator | resolved `1,406`, silence `874`, corrections `0`, exit `0` |
| T1 re-audit | Classification blocker `0`, total other-owner correction `3,345`, exit `0` |
| Protected path comparator | mutation count `0`, exit `0` |
| Final cumulative base/proposed blob validation | exit `0` |
| Final bundle validator | exit `0` |

Output-location correction과 final cumulative rebundle에서는 source/semantic subject가 같았으므로
candidate A/B, focused family와 T1 re-audit을 confidence 목적으로 반복하지 않았다. Path/hash
binding에 필요한 bundle validation과 cumulative base/proposed blob validation만 최소
실행했다. 별도 ad hoc script나 결과를 canonical validator로 승격하지 않았다.

## 10. Protected boundary

Final successor bundle은 다음 protected class의 D1-induced delta가 `0`임을 기록한다.

- `IrisClassifications.lua`
- Browser category/variant/projection runtime source
- KO/EN runtime translation source
- `Iris/build/ENTRYPOINTS.md`
- global current authority manifest와 route index
- clean-checkout environment current record
- 당시 protected `DECISIONS.md`, `ROADMAP.md`, `ARCHITECTURE.md`

이후 사용자의 별도 요청으로 `DECISIONS.md`, `ROADMAP.md`, `ARCHITECTURE.md`에 현재 세션의
owner amendment, `1,406/874` partition, D2/D6 경계와 cumulative lineage를 문서화했다. 이
governance follow-up은 final source subject `8bbc401.../e950a552...`와 이미 발행된 external
bundle을 소급해 변경하거나 재결속하지 않는다. 본 walkthrough도 같은 docs-only follow-up
범위다.

## 11. 최종 claim ceiling

이번 세션에서 닫힌 범위는 다음과 같다.

- system-level optional Layer 2 applicability policy
- support `2,280`의 exact `1,406 applicable / 874 display silence` partition
- resolved `1,406` byte/identity/surface invariance
- no inference와 per-row absence expansion `0`
- Classification correction `874 → 0`
- D2 exact partition readiness
- actual other-owner correction distribution 보존
- protected runtime/public/global-current mutation `0`
- common predecessor에서 final successor까지의 corrected cumulative D6 bundle readiness

아직 닫히지 않은 범위는 다음과 같다.

- T1-D2 implementation과 Menu consumer relation/applicable-N/A parity closure
- T1-D6 integration과 global current adoption
- integrated canonical full gate Run A/B, comparator와 finalizer
- remaining DVF/Iris/Menu/QG correction closure
- production T2 handoff
- runtime visual fit, compatibility, freeze, Publish, release, Workshop와 deployment acceptance

최종 상태를 짧게 표현하면 다음과 같다.

```text
D1 successor workstream       = complete
D2 semantic partition         = ready
D6 cumulative bundle input    = ready
current_ecosystem_adoption     = pending_T1_D6
T2_FULL_DATA_PROGRESSION       = BLOCKED_BY_UPSTREAM_CORRECTIONS
production_t2_handoff          = absent
```

