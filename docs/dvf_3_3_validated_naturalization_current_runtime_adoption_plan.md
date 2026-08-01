# Implementation Plan

> 계획명: Iris DVF 3-3 — 검증된 한국어 자연화 문안의 Current Rendered·Lua Runtime·Package 일관 채택
>
> 상태: current G1·G4·G5 completion synchronization integrated / fresh plan review required / Phase 0 blocked pending fresh review / Changes 2~11 blocked / live mutation blocked
>
> 기준 로드맵: 사용자 제공 `Iris DVF 3-3 — 검증된 한국어 자연화 문안의 Current Rendered·Lua Runtime·Package 일관 채택 종합 로드맵`
>
> 로드맵 입력: `C:\Users\MW\.codex\attachments\2e0cccdd-e682-4d69-a5d1-bb7af94c700a\pasted-text.txt`, SHA-256 `C9F40C318738287952B7471B4C9F1AD2831FDEF9042C138BADA6E7B4C9C4F953`
>
> 계획 검토 피드백: `C:\Users\MW\.codex\attachments\f2e04250-0946-4147-92b4-283409af66b4\pasted-text.txt`, SHA-256 `734AB25AED1811CDAEBE3D60D1C5360A5C4AC820BB29062721B19BB10E369909`
>
> 검토 반영: `WARN / Critical 0 confirmed / Important 7 / Minor 5`의 Revision 1~7과 Minor 1~5를 반영한다. 수정본에 대한 fresh plan review에서 Critical/Important `0`과 Phase 0 eligibility가 확인되기 전에는 Phase 0도 실행하지 않는다.
>
> Cycle 2 계획 검토 피드백: `C:\Users\MW\.codex\attachments\e13d927a-c1ad-4a87-8ab1-7a0cee2481fb\pasted-text.txt`, SHA-256 `ADD57F9FD6C2F37D10C2683E39B412D0030958E52174891009ABEDE736DED922`
>
> Cycle 2 검토 반영: `WARN / Critical 1 / Important 3 / Minor 5`의 Revision 1~5를 반영한다. 이 수정은 plan-level finding 해소 시도이며 fresh review credit을 스스로 만들지 않는다.
>
> Cycle 3 계획 검토 피드백: `C:\Users\MW\.codex\attachments\ffa99925-d813-430d-8a3a-9b4147fe9b37\pasted-text.txt`, SHA-256 `24078054E84043F6F42E862850E1C83AF77002E6FCCCCE47C0E290FF640EBB0F`
>
> Cycle 3 검토 반영: `WARN / Critical 0 / Important 3 / Minor 4`를 반영하되, 사용자 정정에 따라 G6/RTC live-certification 설계를 제거한다. 현재 G6은 `not_applicable_temporary_tooling_trigger`이며 actual canonical runtime/package mismatch가 독립 재현되기 전에는 기술 부채나 G4/G5 blocker가 아니다.
>
> Cycle 4 계획 검토 피드백: `C:\Users\MW\.codex\attachments\95ce76a4-7a1a-4eda-afa0-d29fb5271e8c\pasted-text.txt`, SHA-256 `3E7491F20857093F8869D2B39B66C71D2A2D734642E7AE0118EDE6246B6138E4`
>
> Cycle 4 검토 반영: sealed compatibility-claim prohibition의 additive supersession, official package/current-route exact-command pre-cutover proof, canonical roadmap C-ID 지위, durable embedded generation identity, existing reviewer-eligibility contract, 독립 failure axes와 post-cutover disposition을 보강한다. 이는 G6을 현재 기술 부채로 재분류하지 않는다.
>
> 역사적 계획 작성 기준점: repository HEAD `dd4b8ac37d2b974717364c79aa04afe2fe445f58`
>
> 현재 동기화 최소 실행 ancestry: G1 `c3e2cac1b2c6a6e9f237d5766f2620f92794b8fb`, G4 `9c4b19cbaee5b2f2efb400ba7cb37411be831f48`, G5 `14d240a1c4f22800a7576ab6e52c5019402b5a1a`
>
> 주의: 이 문서의 hash, count, 파일 목록은 동기화 시점의 관찰값이며 실행 권한이나 봉인된 baseline이 아니다. Phase 0에서 위 세 commit을 모두 포함하는 clean execution readpoint와 Git/working identity를 다시 측정하고, 충돌 시 자동 rebaseline하지 않는다.

## 0. Current Executable Synchronization Contract

이 절은 이 계획의 current execution input과 교차 계획 경계를 고정한다. 뒤의 Cycle 1~4 검토 설계는 보존하지만 이 절과 충돌하는 planning-time observation, attempt-specific Publish terminal prerequisite, candidate-anchor 부재 예상과 G6 선행 실행 문구는 historical/non-executable이다.

### Synchronized completed inputs

| Surface | Current exact input | Runtime-adoption interpretation |
|---|---|---|
| G1 clean-checkout | successor `0011`, commit `c3e2cac1b2c6a6e9f237d5766f2620f92794b8fb`, tree `26bd957bbd756e16076d088211ae1291ef37eb94`, Run A/B `206/206 PASS`, canonical SHA-256 `5aacb50791ec629e67c722faf22ed00cee75984de4dbf9f1cbfcf873cebba55b` | reusable IAR integration의 clean-checkout 검증 완료; 이 계획 구현 뒤 새 persistent test/dependency가 생긴 경우에만 final exact subject를 재검증한다. |
| G4 검사 시스템 | commit `9c4b19cbaee5b2f2efb400ba7cb37411be831f48`, tree `de330c7b1c2ed360b0b571c66b86eed622604c40`, current-route `142/142 PASS` | reusable IAR evaluator와 generic current-route integration은 완료된 입력이며 다시 구현하지 않는다. |
| G5 번역체 개선 | commit `14d240a1c4f22800a7576ab6e52c5019402b5a1a`, tree `3b869bd801f4d0fb89de0979e21bc8da3df61b77`, completion claim `naturalization_implementation_and_quality_assessment_complete` | candidate/compiler/detector/human-review를 재실행하지 않고 exact candidate와 assessment를 채택 입력으로 소비한다. |
| G6 RTC | `not_applicable_temporary_tooling_trigger` | 선행 prerequisite가 아니다. 이 계획의 canonical runtime/package path에서 실제 payload mismatch가 독립 재현될 때만 별도 후속 eligibility가 열린다. |

현재 exact cross-plan inputs는 다음과 같다.

```text
candidate payload:
Iris/build/description/v2/staging/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/attempt-0024-publish-remediation-a/phase4/candidate_rendered.json
SHA-256: ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437

candidate manifest:
Iris/build/description/v2/staging/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/attempt-0024-publish-remediation-a/phase4/candidate_manifest.json
SHA-256: 474cd41a439964768541738daf43af30bdee5f7eaf0deee352a44d45c880b18d

IAR assessment result:
Iris/_docs/round3/iar_public_text_assessment/subjects/dvf_3_3_korean_naturalization_candidate/ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437/assessment_result.json
raw SHA-256: 4a5cb7a8a7abf77c66c79a6a6376cafbf0eb4592f19ab94c28f6f5dab4fb5137
deterministic result hash: 861ca998dfff5a7e976d0298ba4e8c164797f6a44abf9c7f168e996d05169199
result: 12 metrics / findings 0 / PASS

G5 consumption record:
Iris/_docs/round3/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/g5_current_iar_assessment_consumption_record.json
raw SHA-256: 0d11c4ca829361e9bc772bdab58e44f73eed540a498d551907168ca8cef30c7c

G4 current-route manifest:
Iris/_docs/round3/current_route_required_validations.json
raw SHA-256: 58f7427cccca4ab181caf5d9bf1031d32b3b2a924858588ce5e5082f9fb6592f
result: 142/142 PASS
```

### Current authority and rerun boundary

- G2/G3는 재실행하지 않는다. current facts `50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120`과 current input manifest `090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7`를 read-only source pair로 소비한다.
- G4의 reusable evaluator와 G5의 naturalization completion은 이 계획의 upstream prerequisite를 이미 만족한다. attempt-specific Publish Phase 6/7, freeze, owner seal, terminal DAG 또는 세션 전용 handoff를 다시 요구하지 않는다.
- G5 Phase 8 artifact는 immutable candidate provenance로 보존할 수 있지만, current admission의 완료 증거는 위 generic IAR assessment와 G5 consumption record다.
- 이 계획은 current rendered, Lua runtime bundle, generation descriptor와 isolated package projection만 소유한다. facts, compiler, candidate, IAR policy/metric/result와 current-route manifest는 mutation하지 않는다.
- project owner는 사용자 한 명이다. 별도 가상 subsystem owner를 만들지 않으며, implementation-time owner artifact는 destructive live cutover에 대해 기존 execution contract가 명시적으로 요구하는 exact authorization으로만 제한한다.

### Fixed synchronization decisions

- C-03: `publish_terminal_not_required_current_scope`. Generic IAR PASS와 G5 consumption record가 candidate admission의 public-text 품질 입력이다.
- C-05: current rendered는 source authority가 아니라 Registry-owned derived current projection이다.
- C-06: `not_applicable_temporary_tooling_trigger`; actual canonical mismatch가 독립 재현되기 전 G6 실행 금지.
- C-08: rendered, Lua manifest, ordered chunks와 generation descriptor를 하나의 rollback 가능한 generation transaction으로 취급한다.
- C-09: Alt tooltip은 별도 surface로 유지하며 이 계획의 기본 transaction에서 제외한다.
- C-10: canonical completion token은 `validated_naturalization_current_runtime_adoption_complete`다.
- C-11: G4 attempt-specific review/seal ceremony는 retired historical이다. 이 계획 자체의 fresh plan review와, existing execution contract가 live cutover에 요구하는 implementation/result review만 적용한다.
- C-13: repository-wide gate는 exact current execution contract 또는 live required-validation manifest가 이 adoption implementation을 mandatory denominator로 포함할 때만 적용한다.

### Machine-policy and RTC boundary

- `stale_requires_successor_rtc`, `live_bridge_runtime_package_publication_allowed=false` 또는 동등 marker의 존재만으로 G6 기술 부채를 선언하지 않는다. Phase 0은 marker의 exact applicability predicate가 current facts/generation에 실제로 적용되는지 검사한다.
- 적용되지 않는 historical marker는 non-applicable evidence로 보존한다. 적용되는 machine guard는 문서-only supersession으로 우회하지 않는다.
- applicable machine guard가 exact generation의 canonical preflight 또는 cutover를 거부하면 `blocked_current_machine_policy`로 중단한다. 이는 payload mismatch나 G6 trigger가 아니다. 해당 machine policy를 바꾸려면 이 계획의 exact write surface에 추가하는 별도 명시적 계획 개정이 필요하다.
- canonical Lua reconstruction, consumer load, package/live parity 또는 post-cutover current-route에서 동일 payload mismatch가 독립 재현될 때만 `rtc_product_mismatch_reproduced=true`와 G6 후속 eligibility를 기록한다.

### Synchronization precedence

역사적 `dd4b8ac…` planning observation은 provenance로만 남는다. 현재 구현은 위 G1·G4·G5 commit을 모두 ancestor로 가진 clean descendant에서 시작한다. 현재 요청 경로의 plan blob은 아직 tracked execution baseline이 아니므로 fresh plan review PASS 후 exact plan blob을 clean descendant에 materialize하기 전 Phase 0와 live mutation을 실행하지 않는다.

## 1. Objective

검증·봉인된 DVF 3-3 한국어 자연화 candidate를 source authority로 승격하지 않은 채, 판정된 current rendered projection과 실제 Lua runtime bundle에 하나의 generation으로 채택하고, 공식 격리 package projection이 동일 payload를 포함함을 검증한다.

목표 상태는 다음 체인으로 정의한다.

```text
exact immutable naturalization candidate
+ exact current source provenance
+ prepared Registry writer / lock / generation schema
-> off-live rendered + Lua generation
-> candidate-scoped canonical Lua/runtime/package preflight
-> exact-generation mirror apply/rollback proof
-> manifest-last live cutover
-> isolated official package projection
-> fresh current-route validation
-> representative in-game consumer observation
-> conditional G6 handoff only if an actual mismatch is independently reproduced
```

성공 시 주장 가능한 최대 범위는 C-10에서 봉인한 terminal token과 다음 사실 문장으로 제한한다.

```text
하나의 exact validated naturalization candidate가 판정된 current rendered 경로와
current Lua runtime bundle에 채택됐고, isolated official package projection에서
동일 payload가 검증됐으며, 대표 consumer/display 경로에서 관측됐다.
```

`DVF PASS`, `Registry Authority PASS`, `Publish Boundary PASS`, release/Workshop/B42 readiness, 2,084개 전수 인게임 human review는 이 계획의 결과로 주장하지 않는다.

---

## 2. Scope

### In Scope

- candidate, assessment, Publish evidence, current facts/manifest, current rendered, runtime manifest/chunks, required-validation manifest의 path·hash·Git identity·referent를 읽기 전용으로 재조사한다.
- 로드맵의 C-01a~C-13을 machine-readable adjudication ledger에 명시적으로 판정한다.
- candidate/current source binding과 admission prerequisite를 검증한다.
- current rendered의 역할을 source authority가 아닌 chain-bound/disposable projection 중 정확한 계약으로 고정한다.
- 새 candidate가 기존 RTC 인증에 포함되지 않는다는 사실을 기록하되 이를 현재 제품 결함이나 선행 G6 기술 부채로 승격하지 않는다.
- 기존 `export_dvf_3_3_lua_bridge.py`의 보호 경로 write refusal를 보존하면서, off-live materialization과 Registry-owned cutover를 분리한다.
- `2105 / 2084 / 21` key/state/public-text shape, exact case-sensitive key, forbidden metadata, unadopted no-text 계약을 전수 검증한다.
- rendered, 실행 시 계산된 ordered chunk set, runtime manifest, exact `current_generation_descriptor.json`을 한 generation으로 묶어 교체한다.
- generation 단위 snapshot, mirror apply/rollback, failure injection, live rollback verification을 구현한다.
- `Iris/tools/package_iris.ps1`의 official isolated package 경로에서 live runtime과 package runtime의 byte parity를 검증한다.
- `Iris/Data/IrisLayer3DataChunks` consumer module path와 기존 Browser 상세 설명 경로를 유지한다.
- 대표 인게임 smoke와 claim-bounded closeout을 수행한다.

### Explicitly Out Of Scope

- facts, decisions, overlay, classification, evidence allowlist의 의미 수정
- candidate 문안 재작성, 자연화 compiler 품질 개선, candidate mutation
- source authority나 Publish Boundary authority의 재설계
- Lua runtime에서 문안 생성·의미 판정·quality 판정 수행
- Iris 외 Pulse 생태계 모듈 변경 또는 spoke 간 직접 의존 추가
- legacy monolith `IrisLayer3Data.lua` 또는 stale `IrisDvfBridgeData.lua` 복원
- package를 source/current authority로 승격
- release archive publication, Workshop 업로드, B42 호환성 선언
- multiplayer, server-side, 장시간 안정성, 외부 모드 전체 compatibility 검증
- unrelated refactor와 top-document의 기존 사용자 변경 정리

---

## 3. Non-Goals

- count 일치만으로 candidate identity나 provenance를 대체하지 않는다.
- candidate acceptance를 current adoption, runtime compatibility, package publication과 같은 claim으로 합치지 않는다.
- predecessor RTC PASS나 superseded bundle을 새 candidate 검증 증거로 재사용하지 않는다. 동시에 그 비포괄성을 실제 RTC 제품 결함으로 표현하지 않는다.
- package를 먼저 만든 뒤 package payload를 live source로 역수입하지 않는다.
- 일부 파일 복사 성공을 generation cutover 성공으로 기록하지 않는다.
- PowerShell `ConvertFrom-Json` object round-trip을 case-sensitive key 보존 경로로 사용하지 않는다.
- raw metadata, assessment, trace, detector, review, disposition 필드를 Lua runtime에 투영하지 않는다.
- 자동화가 owner 판단, independent review, owner seal을 대신 만들지 않는다.

---

## 4. Assumptions

### Exact Immutable Candidate Anchor

기준 로드맵이 지정한 adoption input은 아래 하나로 고정한다. Phase 0에는 sibling attempt 선택, alternate candidate 탐색, hash-based substitution, rebaseline 권한이 없다.

```text
candidate payload path:
Iris/build/description/v2/staging/dvf_3_3_korean_prose_naturalization_public_text_rewrite_closure/attempt-0024-publish-remediation-a/phase4/candidate_rendered.json

candidate payload SHA-256:
ec2a6370a694c9a322e29653765d3d17fab26a208414d7539aaaf8d3fe547437

candidate manifest SHA-256:
474cd41a439964768541738daf43af30bdee5f7eaf0deee352a44d45c880b18d

assessment raw SHA-256:
4a5cb7a8a7abf77c66c79a6a6376cafbf0eb4592f19ab94c28f6f5dab4fb5137

deterministic result hash:
861ca998dfff5a7e976d0298ba4e8c164797f6a44abf9c7f168e996d05169199

compiler aggregate:
2dcff095b1cc34c8fb6d3ad735ac8f9d0ca2affe259f6bb97870b19e7235cc7f

expected shape:
entries=2105, adopted/public=2084, unadopted=21

assessment result:
12 metrics / findings 0 / PASS
```

compiler aggregate의 64자 literal은 repository의 G5 preservation binding, G5 binding, compiler identity, Phase 8 closeout 및 validator 상수에 동일하게 기록된 authoritative value다. repository에서 새 aggregate를 재계산해 anchor를 교체한 것이 아니다. 모든 SHA-256 literal은 Phase 0에서 `^[0-9a-f]{64}$` 형식을 먼저 검증하며 실패하면 `blocked_invalid_anchor_literal`로 종료한다.

candidate manifest와 assessment의 exact path는 위 Current Executable Synchronization Contract에 고정돼 있다. 동기화 시점에는 두 파일과 G5 consumption record가 모두 존재하고 선언 SHA-256과 일치했다. Phase 0은 이 관찰을 무조건 신뢰하지 않고 Git blob/working identity와 referent를 재검증하며, exact anchor가 사라졌거나 bytes가 달라진 경우에만 `blocked_candidate_anchor_unavailable`로 조사 완료한다. sibling attempt 탐색이나 alternate artifact substitution은 금지한다.

### Planning-Time Repository Observations

- current facts는 `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`이며 계획 시점 SHA-256은 `50c5d4901220d7eb43d14d2f8bc35f3e65f983a4326035a4477d7f6319e39120`이다.
- current input manifest는 `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`이며 계획 시점 SHA-256은 `090381a652da540c6e72300624728aba48f6392e41fb50e8eec973efd320b9b7`이다.
- current rendered는 `Iris/build/description/v2/output/dvf_3_3_rendered.json`이며 계획 시점 SHA-256은 `4ebdb0b6c381fb07d8a61517133c7f61483d979563fc9c0e6ebbb8f2359fa50d`이다.
- live Lua manifest는 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`이며 동기화 시점 raw working SHA-256은 `714050b6618c10e23fb15e31ec258fa3dec7652f00422093567a4c09af095f75`, LF-canonical SHA-256은 `fa9f74938023cc81a08e12bc271a22f65befb5df36c0a18e85550882c82f6e2c`이다.
- `714050b6…`과 `fa9f7493…`은 서로 다른 payload가 아니라 같은 tracked text의 raw working-byte domain과 LF-canonical domain이다. Phase 0 drift report는 raw Git blob, filtered working, raw working과 LF-canonical identity를 이름 있는 별도 필드로 기록하며 서로 다른 identity domain을 payload drift로 오판하지 않는다. 줄바꿈 이외의 byte/content mismatch만 실제 drift 후보가 된다.
- live runtime은 `IrisLayer3DataChunks.lua`와 `IrisLayer3DataChunks/Chunk001.lua`~`Chunk011.lua`로 구성되며 manifest 주석은 `2105` entries, `11 x <= 200`을 기록한다.
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`는 먼저 `Iris/Data/IrisLayer3DataChunks`를 require하고 `IrisLayer3Data` global을 보존한다. Browser 상세 표면은 `IrisBrowserDetail.lua`에서 `IrisAPI.Description.getDescription`을 사용한다.
- Alt tooltip은 `IrisTooltipSummary.lua`에서 별도 `IrisUseCaseDescriptions` surface를 읽는다. 따라서 C-09 전에는 Layer 3 본문 adoption scope로 자동 포함하지 않는다.
- `export_dvf_3_3_lua_bridge.py`의 default output은 staging이며 current/package-looking manifest 및 protected chunk 경로 직접 쓰기를 거부한다. 이 guard는 제거하지 않는다.
- `package_iris.ps1`은 `media/`를 격리 package root로 복사한 뒤 rendered/runtime/package surface를 RTC validator에 제출하고 monolith와 stale bridge를 금지한다.
- `current_route_required_validations.json`은 live required-validation container이지 DVF 전체 authority가 아니다.
- `docs/EXECUTION_CONTRACT.md`는 heavy/authority/public-output 실행 계약이다. current synchronized worktree의 관찰 SHA-256은 `dc5e9b34be950da09ce8101c5de8b21485f30ae8920769acfec8b49fc6e9fd76`이며 Phase 0에서 exact Git blob/hash, applicable clauses, conflict count를 다시 기록한다.
- 계획 작성 시점 worktree에는 `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/ROADMAP.md`의 기존 사용자 변경과 별도 untracked 경로가 있다. 이 계획은 이를 수정·정리·포함하지 않는다.

### RTC / G6 Status Boundary

이 계획은 RTC의 현재 상태를 다음처럼 고정한다.

```text
현재 확인된 RTC 제품 결함:
없음

G6 current disposition:
not_applicable_temporary_tooling_trigger

기존 RTC 인증이 새 naturalization candidate를 포괄함:
아님

새 candidate의 canonical Lua/runtime/package 검증 필요:
맞음

G6을 현재 기술 부채 해결 계획으로 선행 실행:
필요 없음
```

과거 오류는 임시 validation/closure tooling에서 발생했고 실제 Lua/runtime/package 결함은 재현되지 않았다. G6 Change 1의 중단도 runtime defect 발견이 아니라 당시 G4/G5 one-use terminal 자료 부재 때문이었다. 따라서 `stale_requires_successor_rtc` 같은 기존 marker는 이 계획에서 “새 candidate가 아직 그 인증 범위에 들지 않는다”는 freshness 상태로만 읽으며 `runtime_defect_confirmed`, `technical_debt_open`, G4/G5 blocker로 해석하지 않는다.

이 계획은 G6 RTC lifecycle, bundle adoption, required-validation live reference를 생성·활성화·수정하지 않는다. 인게임 연결 후 canonical Lua reconstruction, runtime consumer load, package/live parity, current-route 검사를 수행하고 동일 mismatch가 canonical path에서 독립적으로 재현될 때만 `rtc_product_mismatch_reproduced=true`를 기록한다. 그때에만 별도 owner-approved 후속 계획에서 G6의 필요한 부분을 현재 generation identity에 동기화할 수 있다. environment/tooling-only failure 또는 one-use evidence 부재는 이 trigger를 만족하지 않는다.

다만 defect 존재 여부와 machine-policy applicability는 별개다. `docs/DECISIONS.md`의 Food Semantic G3 readpoint와 live `Iris/_docs/round3/current_route_required_validations.json`에는 historical `stale_requires_successor_rtc` 및 publication guard가 남아 있다. Phase 0은 current facts/generation에 대한 exact applicability predicate와 실제 canonical command 동작을 재현한다. non-applicable historical marker는 보존하되 blocker로 승격하지 않는다. applicable machine guard는 `docs/DECISIONS.md` 문구만으로 우회하지 않고 `blocked_current_machine_policy`로 종료한다. 이를 변경하려면 exact machine-policy path/field/test를 이 계획의 write surface에 추가하는 명시적 계획 개정이 먼저 필요하며, 그 개정 자체는 RTC 제품 결함 인정이나 G6 closure가 아니다.

### Phase 0 Entry Preconditions

1. `docs/Philosophy.md`가 최상위 권위이며 Iris는 100% Lua runtime과 오프라인 정적 생산 책임 분리를 유지한다.
2. 수정본에 대한 fresh plan review가 `Open Critical=0`, `Open Important=0`, `phase0_eligible=true`를 기록해야 한다.
3. 실행 base는 이 plan blob과 G1 `c3e2cac1…`, G4 `9c4b19cb…`, G5 `14d240a1…`을 모두 포함한 clean descendant commit이어야 한다. 현재 dirty planning worktree를 implementation baseline으로 자동 채택하지 않는다.
4. declared candidate payload path가 존재하고 payload hash literal이 형식상 유효해야 한다. payload bytes/hash 일치는 Phase 0가 조사한다.
5. 모든 declared anchor literal이 `^[0-9a-f]{64}$` 형식이어야 한다. manifest/assessment referent의 존재와 일치는 Phase 0 조사 대상이지 entry prerequisite가 아니다.
6. read-only census tooling과 protected pre-census가 사용 가능해야 한다.
7. fresh review artifact는 Phase 0 진입 허용 여부만 판정한다. reviewer independence를 이 계획이 새로 발명하지 않으며 Phase 0가 existing contract의 exact eligibility clause를 찾아 path/hash로 기록한다.

### Phase 0 Completion and Phase 1 Entry

Phase 0의 정상 terminal outcome은 둘이다.

```text
phase0_complete_eligible_for_phase1
phase0_complete_blocked
```

`blocked_candidate_anchor_unavailable`, `blocked_invalid_anchor_literal`, `blocked_source_role_conflict`, `blocked_source_pair_incoherent`는 Phase 0 실행 실패가 아니라 downstream blocker를 성공적으로 확인한 `phase0_complete_blocked` reason이다.

Phase 0 exit는 C-01a~C-01c를 실제 판정하고 C-02~C-13은 허용 vocabulary와 routing 규칙만 검증한다. Phase 1 진입에는 exact candidate referents PASS, C-01a~C-01c `resolved_pass`, C-02 binding obtainable, applicable owner records available, required axes의 `resolved_blocked`/`deferred_with_owner` `0`이 필요하다. 이후 각 Change는 자신이 소비하는 C-ID를 entry gate에서 실제 PASS로 요구한다.

계획 시점 count/hash가 달라지면 drift report를 만들고 identity·write surface·denominator·claim에 영향을 주는 drift는 owner 재승인을 요구한다.

### Required Adjudications

| ID | 판정 질문 | 기본 fail-closed 처리 |
|---|---|---|
| C-01a | current facts exact identity와 sealed lifecycle role은 무엇인가 | `role_conflict`/`unknown`이면 Phase 1 진입 금지 및 owner 회부 |
| C-01b | current input manifest exact identity와 sealed lifecycle role은 무엇인가 | `role_conflict`/`unknown`이면 Phase 1 진입 금지 및 owner 회부 |
| C-01c | facts와 input manifest가 동일 sealed generation pair인가 | `pair_incoherent`/`pair_unknown`이면 Phase 1 진입 금지 및 owner 회부 |
| C-02 | candidate가 exact current input generation을 소비했는가 | unbound/mismatch면 adoption 금지 |
| C-03 | assessment만으로 충분한가, Publish terminal evidence가 필요한가 | 동기화 결정 `publish_terminal_not_required_current_scope`; exact IAR PASS와 G5 consumption record 불일치 시 adoption 금지 |
| C-04 | immutable candidate direct projection인가 deterministic regeneration인가 | candidate mutation 가능성이 있으면 금지 |
| C-05 | current rendered의 정확한 authority vocabulary/role은 무엇인가 | 동기화 결정 `registry_owned_derived_current_projection`; source authority 승격 금지 |
| C-06 | 새 candidate의 runtime 검증 상태와 G6 trigger disposition은 무엇인가 | 기본값 `not_applicable_temporary_tooling_trigger`; actual canonical mismatch 독립 재현 전 G6/RTC debt closure 금지 |
| C-07a | single live writer identity와 exact target allowlist는 무엇인가 | 명시적 authorization 없으면 live write 금지 |
| C-07b | generation descriptor의 exact live path와 owner는 무엇인가 | exact path/owner 없으면 live write 금지 |
| C-07c | closed protected output set의 additive expansion이 필요한가 | 필요하면 explicit additive authorization 전 live write 금지 |
| C-07d | 신규 tooling의 allowlist/core cap 영향은 무엇인가 | 충돌 또는 미판정이면 implementation 금지 |
| C-07e | `Iris/_docs/round3/current_route_required_validations.json`과 RTC lifecycle/bundle namespace의 disposition은 무엇인가 | read-only/protected/no-writer로 고정; mutation 발견 시 adoption FAIL |
| C-08 | rendered/runtime을 한 transaction으로 묶을 것인가 | mixed generation 가능 경계 금지 |
| C-09 | Alt tooltip이 동일 generation scope인가 | 판정 전 별도 surface 유지 |
| C-10 | canonical terminal claim token은 무엇인가 | 동기화 결정 `validated_naturalization_current_runtime_adoption_complete`; 더 넓은 claim 금지 |
| C-11 | 이 adoption/current-route에 existing contract가 요구하는 review/seal이 있는가 | fresh plan review와 실제 applicable implementation/result review만 소비; G4/G6 attempt-specific terminal ceremony를 자동 흡수하지 않음 |
| C-12 | predecessor snapshot residue를 rollback에 사용할 수 있는가 | freshness 미확인 snapshot 재사용 금지 |
| C-13 | `EXECUTION_CONTRACT.md` 또는 live required-validation manifest가 이 exact adoption에 specific repository-wide command를 mandatory로 선언하는가 | 그 경우에만 applicable; 별도 Clean-Checkout closure/owner 선호 자동 흡수 금지 |

Canonical roadmap source는 `C:\Users\MW\.codex\attachments\2e0cccdd-e682-4d69-a5d1-bb7af94c700a\pasted-text.txt`, SHA-256 `C9F40C318738287952B7471B4C9F1AD2831FDEF9042C138BADA6E7B4C9C4F953`다. 원문의 conflict-preserved C-03, C-05, C-08, C-10은 이번 cross-plan synchronization에서 위 current executable scopes와 사용자의 직접 동기화 지시를 근거로 fixed synchronization decision이 됐다. Phase 0은 그 결정과 exact input identity를 검증하지만 별도 subsystem owner나 attempt-specific owner record를 새로 만들지 않는다. C-01a~C-02, C-04, C-06~C-07, C-11~C-13의 사실 판정은 여전히 실제 repository evidence와 applicable contract를 소비한다.

공통 adjudication 상태는 `resolved_pass`, `resolved_blocked`, `not_applicable`, `deferred_with_owner`로 제한한다. 동기화로 고정된 C-03, C-05, C-08, C-09, C-10은 exact plan blob과 current input이 일치하면 `resolved_pass` 또는 `not_applicable`로 materialize한다. 나머지 C-01a~C-08의 `deferred_with_owner`는 모든 dependent implementation을 차단한다. C-11~C-13의 `deferred_with_owner`는 독립적인 선행 작업만 허용하고 해당 surface 및 terminal closeout을 차단한다.

이 계획은 C-01a~C-01c 실패를 고칠 권한이 없다. sealed role reclassification, facts 수정, input manifest 재생성 또는 pair rebinding은 out of scope다.

Generation descriptor의 proposed exact live path는 다음 Registry-owned sidecar로 고정한다.

```text
Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json
```

C-07b는 이 path의 owner를 `Iris Artifact Registry`로 고정한다. C-07c가 이 path를 기존 closed protected output set 밖으로 판정하면 explicit additive authorization 전에는 생성하거나 쓰지 않는다. authorization이 거부되면 alternate path를 자동 선택하지 않고 `resolved_blocked`로 종료한다. `current_route_required_validations.json`과 RTC lifecycle/bundle namespace는 이 계획의 write allowlist에 포함하지 않는다.

---

## 5. Repository Areas Affected

아래는 예상 surface다. Phase 0 census와 C-07 writer authorization이 exact write allowlist를 확정하며, 목록 밖 변경은 fail-closed한다.

### Code

- `Iris/build/description/v2/tools/build/export_dvf_3_3_lua_bridge.py` — 기존 off-live exporter; protected write guard 보존
- `Iris/build/description/v2/tools/build/validate_dvf_3_3_registry_runtime_compatibility.py` — mutation 없는 candidate-scoped canonical surface probe로만 재사용 가능; RTC closure/adoption claim 금지
- `Iris/build/description/v2/tools/build/` 아래 신규 adoption orchestrator, validator, transaction/rollback helper 및 test
- `Iris/tools/package_iris.ps1` — official isolated package projection; 계약이 이미 충분하면 수정하지 않고 소비

### Docs

- `docs/dvf_3_3_validated_naturalization_current_runtime_adoption_plan.md`
- C-01a~C-13 판정에 필요한 신규 scope-lock/authority decision/claim-boundary 문서
- final adoption 사실과 claim boundary를 additive sync할 `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`; machine-policy denial을 문서만으로 supersede하는 용도로 사용 금지

### Config / Authority Manifests

- `Iris/_docs/round3/current_route_required_validations.json` — read-only current-route input; 이 계획의 write target 아님
- `Iris/_docs/round3/registry_authority_required_gate_contract.json`
- `Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json` — C-07c additive authorization 전 write 금지
- 신규 adoption attempt root 아래 writer authorization, transaction policy, generation schema, adjudication ledger

### Generated Artifacts

- `Iris/build/description/v2/output/dvf_3_3_rendered.json`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk*.lua`
- `Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json`
- 격리 package output의 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
- 격리 package output의 `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk*.lua`
- attempt-local receipts, rollback snapshot, journal, machine reports, closeout packet

### Protected but Normally Unmodified

- immutable naturalization candidate와 assessment/evidence
- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_input_manifest.json`
- `Iris/build/description/v2/data/dvf_3_3_decisions.jsonl`
- `Iris/build/description/v2/data/dvf_3_3_overlay_support.jsonl`
- `Iris/_docs/round3/current_route_required_validations.json`
- `Iris/_docs/round3/registry_runtime_compatibility/` 전체 bundle/lifecycle/attempt evidence
- unrelated Lua/UI/package files

---

## 6. Planned Changes

### Change 1 — Phase 0 scope lock and read-only premise census

Purpose:

실행 base, repository identity, candidate/current identities, protected surfaces, writer/guard 상태, tooltip, rollback residue를 mutation 없이 확정한다.

Files:

- census 실행 전에 materialize하는 신규 attempt-local census runner/schema/test
- tooling materialization 완료 뒤 시작하는 read-only census의 신규 attempt-local report
- 신규 `adoption_adjudication_ledger.json`
- 신규 `protected_surface_census.json`
- 신규 `premise_identity_report.json`

Implementation Notes:

- Git HEAD/tree/status, path type, file size, SHA-256, Git blob/untracked state, encoding/EOL을 기록한다.
- 모든 declared SHA-256 anchor literal에 `^[0-9a-f]{64}$`를 적용하고 prefix·추정·재계산 대체를 금지한다.
- candidate와 관련 manifest의 referent를 재귀적으로 검증하되 historical artifact를 current로 승격하지 않는다.
- 세 current facts 후보 충돌, current rendered 역할, closed protected output set, tooling allowlist/core cap, tooltip surface, predecessor snapshot residue를 실제 repository에서 판정한다.
- G6 `not_applicable_temporary_tooling_trigger`, temporary tooling failure provenance, actual runtime defect reproduction `0`, 새 candidate의 기존 인증 비포괄성을 서로 분리해 기록한다.
- `docs/ROADMAP.md`, `docs/DECISIONS.md`, live required-validation manifest의 exact prohibition source path/hash/field와 current-facts applicability predicate를 기록하고 `applicable=true|false`를 근거와 함께 판정한다. `true`인 machine guard는 문서-only supersession으로 우회하지 않고 모든 live-dependent change를 `blocked_current_machine_policy`로 닫는다.
- official package command는 `Iris/tools/package_iris.ps1`의 실제 parameter contract에서, official current-route command는 `Iris/_docs/round3/round3_run_contract_tests.py --class current --enforce-current-build-closure --out <receipt>`에서 exact argv를 추출한다. live manifest의 required artifact/test 전체 denominator와 SHA-256을 함께 봉인하고 임의 axis subset을 정의하지 않는다.
- review eligibility는 existing contract의 exact path/hash/clause, `independence_required`, `owner_seal_required`, reviewer identity/role, plan co-drafter 여부, credited review 여부를 기록한다. applicable contract가 independence를 요구할 때만 eligible reviewer의 fresh review를 요구한다. 요구하지 않거나 독립 review가 수행되지 않으면 waiver/PASS로 바꾸지 않고 closeout known limit로 남긴다.
- live marker `stale_requires_successor_rtc`와 `successor_registry_runtime_compatibility_closure=false`는 freshness/non-coverage observation으로 기록하고 technical-debt 또는 G4/G5 blocker로 승격하지 않는다.
- exporter output에 `bridge_context=staging`, attempt path/output root/identifier 같은 build-context marker가 존재하는지 조사한다. 없으면 `not_applicable`, 있으면 live projection 제거 gate를 연다.
- runtime manifest의 raw Git blob, filtered working, raw working과 LF-canonical identity를 별도 필드로 기록하고, 동기화 관찰값 `714050b6…` raw / `fa9f7493…` LF-canonical의 domain relation을 검증한다. identity-domain 혼동을 payload drift로 세지 않는다.
- PowerShell은 파일 hash/경로 검사에만 사용하고 JSON key projection은 Python의 pair-preserving parser로 수행한다.
- runner/schema/test 자체의 신규 materialization은 read-only census window 밖의 implementation mutation으로 별도 기록한다. `read_only_mutation_count=0`의 분모는 census 시작 시 봉인한 current rendered, live runtime manifest/chunks, current source inputs, required-validation/RTC namespace, immutable candidate/evidence와 top documents인 protected/live surface로 한정하며 attempt-local report/receipt write는 제외한다.
- census read window의 실행 전·후 protected/live surface hash census가 같아야 한다.

Validation:

- census read window protected/live surface mutation count `0`; attempt-local tooling/report writes는 별도 implementation inventory와 exact hash로 기록
- anchor literal format PASS 또는 `phase0_complete_blocked/blocked_invalid_anchor_literal`
- exact referent PASS 또는 `phase0_complete_blocked/blocked_candidate_anchor_unavailable`
- duplicate/case-collision-preserving census PASS
- C-01a~C-13 각각 허용 vocabulary 사용 PASS
- C-01a~C-01c 실제 판정 완료; blocked 결과는 reason과 함께 `phase0_complete_blocked`
- C-02~C-13은 vocabulary/routing validity만 Phase 0에서 강제하고 실제 PASS를 선행 요구하지 않음
- sealed prohibition applicability와 official terminal command/full denominator가 exact bytes로 확인됨
- machine-policy guard가 non-applicable이거나 exact canonical route에서 허용됨; applicable denial이면 `blocked_current_machine_policy`로 정상 차단됨
- `phase0_complete_eligible_for_phase1` 또는 `phase0_complete_blocked` 중 정확히 하나
- execution contract exact readpoint/applicable clause/conflict count 기록 PASS

---

### Change 2 — Phase 1 candidate admission and authority adjudication

Purpose:

candidate가 현재 source generation과 결속되며 adoption에 필요한 acceptance evidence를 갖췄는지 판정한다.

Entry Preconditions:

- `phase0_complete_eligible_for_phase1`
- exact payload/manifest/assessment referents PASS
- C-01a~C-01c `resolved_pass`
- C-02 binding obtainable
- synchronized C-03/C-05 fixed decisions와 exact plan blob identity PASS
- dependent axes에 `resolved_blocked`/`deferred_with_owner` `0`

Files:

- 신규 `candidate_admission_report.json`
- 신규 `candidate_source_binding_report.json`
- 신규 `authority_role_decision.json`
- 신규 `adoption_method_decision.json`

Implementation Notes:

- candidate content hash, candidate manifest hash, assessment target identity, source input identities를 exact 비교한다.
- C-04는 direct projection과 regeneration 중 하나만 선택한다. regeneration을 선택하면 regenerated text가 immutable candidate의 public payload와 byte/decoded-text contract상 동일해야 하며 다르면 FAIL한다.
- C-05는 current rendered를 source authority로 선언할 수 없다. 허용되는 역할은 판정된 generation-bound projection/consumer-facing build artifact 범위다.
- C-03은 generic IAR assessment raw/deterministic identity와 G5 consumption record가 모두 exact candidate를 결속하는지 검증한다. attempt-specific Publish terminal, owner seal 또는 terminal DAG는 admission 입력이 아니다.

Validation:

- candidate mutation `0`
- candidate/current input binding PASS
- assessment/candidate referent PASS
- admission prerequisite PASS
- authority vocabulary/claim-boundary scan PASS

---

### Change 3 — Phase 2 writer, lock, generation schema, and runtime-check contract preparation

Purpose:

아직 존재하지 않는 next generation에 PASS를 부여하지 않고 materialization writer·lock·schema와 candidate-scoped canonical runtime/package 검사 계약만 준비한다.

Files:

- 신규 writer authorization, exact target allowlist, lock/transaction/generation schema
- Lua reconstruction/runtime/package probe의 exact-generation input contract와 test
- `C-07a`~`C-07d` 및 `C-13` 판정 record

Implementation Notes:

- 이 단계의 최대 상태는 `runtime_check_contract_prepared`이며 RTC/G6 closure나 제품 결함을 주장하지 않는다.
- `package_iris.ps1`, exporter, Lua reconstruction과 current-route consumer가 나중에 소비할 exact input/output·failure taxonomy를 준비한다.
- C-06은 `not_applicable_temporary_tooling_trigger`를 current default로 유지하고 actual canonical mismatch 재현 조건만 고정한다.
- 기존 exporter의 protected current/package write refusal를 보존한다.
- C-07a는 신규 Registry-owned adoption writer 하나만 exact protected paths에 쓸 수 있게 하고 validator와 package script에는 live mutation 권한을 주지 않는다.
- C-07b는 `Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json`과 `Iris Artifact Registry` ownership을 확인한다.
- C-07c는 기존 closed protected set 밖 write이면 explicit additive authorization을 요구한다.
- C-07d는 신규 orchestrator/validator/helper의 tooling allowlist와 core cap 영향을 고정한다.

Validation:

- `runtime_check_contract_prepared=true`
- `g6_current_disposition=not_applicable_temporary_tooling_trigger`
- `rtc_product_defect_confirmed=false`
- writer count `1`
- unauthorized protected writer `0`
- generation descriptor destination ambiguity `0`
- allowlist/core cap conflict `0`

---

### Change 4 — Phase 3 off-live rendered and Lua generation materialization

Purpose:

immutable candidate를 current source contract에 맞는 rendered projection과 deterministic Lua runtime bundle로 attempt-local staging에 완성한다.

Files:

- attempt-local `next_generation/dvf_3_3_rendered.json`
- attempt-local `next_generation/IrisLayer3DataChunks.lua`
- attempt-local `next_generation/IrisLayer3DataChunks/Chunk*.lua`
- attempt-local `next_generation/materialized_generation_descriptor.json`, key-membership, payload-field, chunk reports

Implementation Notes:

- output은 live/package-looking 경로가 아닌 attempt-local staging에 만든다.
- `materialized_generation_descriptor.json`은 attempt-local trace이며 candidate identity, coherent source-pair identity, rendered identity, runtime manifest identity와 ordered chunk path/hash만 포함한다. RTC/G6 bundle, lifecycle, live binding, adoption receipt는 hash domain에 포함하지 않는다. live descriptor는 이 임시 파일의 hash만 가리키지 않고 동일한 full identity fields와 transaction ID를 직접 embed한다. staging cleanup 뒤에도 durable current descriptor 하나만으로 source/candidate/rendered/runtime/chunk identity를 재개방할 수 있어야 한다.
- source의 exact case-sensitive key/state와 candidate의 public text를 결합하기 전에 `candidate_key_set == current_source_key_set`을 검증한다.
- key 비교는 decoded Unicode code-point exact이며 casefold와 Unicode normalization을 사용하지 않는다. case-variant key는 독립 원소다.
- public-text parity denominator는 candidate/source key set의 합집합이다. count는 보조 shape 지표일 뿐 membership evidence가 아니다.
- adopted row에만 candidate public text를 투영한다. 모든 unadopted row의 `text_ko`는 absent 또는 explicit nil이어야 하고 빈 문자열은 FAIL이다.
- 모든 current-like JSON/Lua/reconstructed row에서 `publish_state`는 absent여야 한다. `publish_state`는 forbidden metadata exact field다.
- assessment, trace, review, detector, quality/disposition metadata를 runtime에 투영하지 않는다.
- `export_dvf_3_3_lua_bridge.py --bridge-context staging --format chunk --output-root <attempt-local>` 계약을 사용한다.
- actual Lua reconstruction으로 manifest module order, key/state/text, duplicate/overwrite/orphan을 검사한다.
- applicable canonical compatibility probe가 Windows Route C를 요구하면 `4 surfaces × 2105 = 8420` exact record projection을 소비한다. 이는 G6 closure나 제품 결함 claim이 아니다.
- Phase 0에서 staging/build marker가 존재한다고 판정되면 live projection 전에 제거하고, 없으면 이 gate를 `not_applicable`로 닫는다.
- materialization 완료 시 in-game sample item list와 각 expected text hash를 봉인하며 관측 결과를 보고 교체하지 않는다.

Validation:

- `candidate_only_count=0`, `source_only_count=0`
- candidate/source bidirectional key-set equality PASS
- union-denominator candidate/rendered public-text equality PASS
- key count `2105`, adopted/public `2084`, unadopted `21` 또는 승인된 실행-time shape
- JSON/Lua/reconstruction 전 surface에서 unadopted `text_ko` absent-or-nil, empty string `0`
- JSON/Lua/reconstruction 전 current-like row의 `publish_state` `0`
- forbidden metadata `0`, duplicate/cross-chunk overwrite `0`, orphan chunk `0`
- live-projection staging/build-context marker `0`, attempt-local path/identifier exposure `0` when applicable
- repeated run normalized content identity PASS
- sample manifest path/hash binding PASS
- materialized descriptor canonical schema/hash PASS; RTC/G6 field `0`

---

### Change 5 — Phase 4 candidate-scoped canonical Lua/runtime/package preflight

Purpose:

Change 4의 exact bytes가 canonical Lua reconstruction과 runtime/package surface contract를 만족하는지 mutation 없이 검사한다. 이는 RTC 기술 부채 해결, G6 실행, durable RTC certification 또는 live lifecycle adoption이 아니다.

Files:

- attempt-local exact-generation surface input manifest
- Lua reconstruction, consumer-load, package probe와 field/key parity receipts
- environment/tooling failure classification report

Implementation Notes:

- Change 3의 prepared check contract를 exact rendered hash, runtime manifest hash, ordered chunk path/hash, source pair identity, candidate anchor와 materialized generation descriptor hash에 결속한다.
- predecessor RTC PASS를 새 candidate의 PASS로 재사용하지 않는다.
- 기존 RTC bundle/lifecycle/current required-validation reference를 생성·수정·adopt하지 않는다.
- mismatch는 `candidate_preflight_mismatch`로 기록하며 이 단계만으로 `rtc_product_mismatch_reproduced=true`나 G6 debt를 만들지 않는다.
- applicable Route C는 exact case-sensitive record projection denominator 전체를 소비한다.
- disposable off-live generation을 입력으로 official package exact argv와 official current-route exact argv를 **live mutation 전에 실제 실행**한다. 두 command 모두 guard bypass/manifest rewrite/required-test omission `0`, exit code `0`, full required denominator 충족을 증명해야 한다.
- 두 official command에는 임의 input override를 추가하지 않는다. 대신 G1/G4/G5와 이 계획 implementation commit을 포함하는 exact clean detached checkout을 attempt-local external mirror root에 만든다. Change 4가 승인한 rendered/runtime manifest/ordered chunks만 그 mirror의 canonical relative live paths에 Registry transaction helper로 설치하고, mirror-local generation descriptor가 동일 embedded generation identity를 가리키게 한 뒤 기존 `Iris/tools/package_iris.ps1`와 `Iris/_docs/round3/round3_run_contract_tests.py`를 mirror 내부의 원래 argv/cwd 계약 그대로 실행한다. 원본 repository live tree는 실행 전·후 protected hash census equality로 불변을 증명한다.
- isolated mirror receipt는 mirror base commit/tree, clean-checkout creation argv, mirror root identity, installed Change 4 path/hash set, original repository pre/post census, official executable Git blob/SHA-256, exact argv/cwd, live-manifest denominator와 결과를 함께 결속한다. mirror의 predecessor live bytes가 남았거나 Change 4 exact path-set 밖 tracked/untracked mutation이 있으면 preflight FAIL이다. mirror 결과는 disposable evidence이며 current authority나 package authority가 아니다.
- isolated candidate mode가 package script상 허용되더라도 current-route full denominator를 대체하지 않는다. exact official route가 stale RTC policy 때문에 exit `0`에 도달할 수 없거나 disposable input을 공식적으로 받을 수 없으면 우회하지 않고 `blocked_official_terminal_route_noncoverage`로 종료한다. 이 상태는 RTC 제품 결함이나 G6 trigger가 아니다.
- pre-cutover receipt는 exact executable/interpreter identity, argv, cwd, input generation identity, live-manifest hash, required artifact/test IDs와 counts, exit code, stdout/stderr hashes, `guard_bypass=false`, `denominator_reduced=false`를 기록한다.

Validation:

- materialized generation identity/referent PASS
- Lua reconstruction, consumer-load probe, key/state/text/field parity PASS
- isolated package probe parity PASS
- predecessor RTC certification reuse `0`
- RTC/G6 lifecycle mutation `0`
- environment/tooling-only failure의 product defect 승격 `0`
- official package/current-route exact command exit `0`; required denominator 누락 `0`; bypass `0`

---

### Change 6 — Phase 5 exact-generation mirror transaction and rollback proof

Purpose:

exact materialized generation과 candidate-scoped preflight PASS를 입력으로 live cutover 전에 apply/rollback 완전성과 실패 복구를 증명한다.

Files:

- 신규 adoption transaction helper/validator/test
- attempt-local mirror root, fresh snapshot manifest, journal, failure-injection receipts

Implementation Notes:

- exact preimage에는 rendered, runtime manifest, chunk directory 전체, `current_generation_descriptor.json`, applicable tooltip surface만 포함한다. RTC lifecycle과 `current_route_required_validations.json`은 read-only protected surface다.
- snapshot manifest를 hash-bound하고 C-12에서 stale인 residue를 사용하지 않는다.
- exact Change 4 bytes와 Change 5 canonical preflight PASS만 mirror input으로 허용한다.
- runtime generation과 descriptor만 하나의 live transaction/snapshot/rollback unit으로 취급한다.
- manifest-last를 지킨다.
- failure injection은 rendered install 전/후, chunk swap 중, runtime manifest 전/후, descriptor install 실패를 포함한다.
- 각 실패 뒤 exact preimage equality를 검증한다.

Validation:

- mirror apply PASS
- 각 failure point rollback exact equality PASS
- orphan/new path `0`, partial rollback path `0`
- journal/receipt referential integrity PASS
- package output rollback authority `0`
- mutable live surface인 rendered/runtime/descriptor exact predecessor equality PASS
- RTC lifecycle/required-validation manifest mutation `0`

---

### Change 7 — Phase 6 live current generation cutover

Purpose:

검증된 exact generation을 single Registry writer transaction으로 current rendered/runtime/descriptor에 채택한다.

Files:

- `Iris/build/description/v2/output/dvf_3_3_rendered.json`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/Chunk*.lua`
- `Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json`
- cutover journal/receipt/snapshot

Implementation Notes:

- entry preconditions는 C-01a~C-08 `resolved_pass/not_applicable`, exact anchor admission, writer authorization, Change 4 materialization, Change 5 canonical preflight PASS, Change 6 rollback proof PASS다.
- exclusive lock 후 exact preimage를 재확인하고 drift가 있으면 쓰지 않는다.
- C-08 결정과 무관하게 intermediate state를 current-valid/package-eligible로 기록하지 않는다.
- chunks를 완전히 배치하고 stale chunks를 제거한 뒤 runtime manifest를 교체하고 exact generation descriptor를 설치한다.
- live `current_generation_descriptor.json`은 materialized descriptor hash와 사전 할당된 adoption transaction ID를 기록하되 임시 path를 durable referent로 요구하지 않는다. candidate/source-pair/rendered/runtime-manifest/ordered-chunk path+hash identity 전체를 직접 embed한다. RTC/G6 identity를 포함하지 않으며 자기 자신의 full-file hash를 참조하지 않는다.
- C-07b exact descriptor path만 writer가 쓸 수 있다. protected set 밖이면 C-07c additive authorization이 선행돼야 한다.
- runtime install/post-apply validation 실패 시 runtime generation과 descriptor를 predecessor로 자동 rollback하고 terminal credit `0`으로 한다.

Validation:

- installed bytes = approved exact-generation bytes
- rendered/chunks/manifest/descriptor generation identity PASS
- current descriptor의 `materialized_generation_descriptor_sha256` = approved materialized descriptor SHA-256
- `embedded_generation_identity_complete=true`, `durable_generation_identity_reopenable=true`, missing embedded identity field `0`
- descriptor self-reference count `0`, RTC/G6 field count `0`
- mixed generation `0`, stale/orphan chunk `0`
- candidate/source key membership과 unadopted field contract 재검증 PASS
- protected upstream/unrelated mutation `0`
- RTC bundle/lifecycle/`current_route_required_validations.json` mutation `0`
- rollback snapshot verify-only PASS

---

### Change 8 — Phase 7 official package projection

Purpose:

Change 5에서 disposable input으로 pre-proved한 동일 official package command를 live input으로 다시 실행해 package가 live runtime의 disposable projection이며 동일 payload를 포함하는지 검증한다. Change 5 PASS는 이 단계의 PASS를 대체하지 않는다.

Files:

- `Iris/tools/package_iris.ps1` 소비
- attempt-local isolated package root, package manifest, compatibility probe receipt

Implementation Notes:

- Change 5의 disposable official-route proof가 PASS한 동일 command/mode를 live cutover 뒤 재실행한다.
- `package_iris.ps1`의 monolith/stale bridge 금지와 surface validation을 유지한다. 기존 RTC required-gate가 새 candidate를 포괄하지 않는 사실은 non-coverage로 기록하고, package payload의 canonical parity는 별도 검사한다.
- existing isolated candidate-probe mode는 Change 5 보조 진단으로만 사용할 수 있고 terminal official package PASS를 대체하지 않는다. pre-proved official mode가 live에서 exit `0`이 아니면 guard를 우회하지 않고 package를 폐기하고 live generation을 rollback한다.
- package runtime manifest와 모든 chunk relative path/bytes를 live와 비교한다.
- package mismatch는 live를 재정의하지 않는다. package를 폐기하고 terminal eligibility를 false로 만든 뒤 Change 7의 exact preimage로 live generation 전체를 rollback한다.

Validation:

- package/live manifest byte equality PASS
- package/live chunk path-set·byte equality PASS
- missing/extra runtime file `0`
- monolith/stale bridge `0`
- package authority claim `0`
- G6/RTC lifecycle mutation `0`
- package tooling/policy non-coverage와 product payload mismatch의 classification PASS

---

### Change 9 — Phase 8 fresh full-denominator current-route and regression validation

Purpose:

실제 current files를 입력으로 모든 applicable required validation을 새로 실행한다.

Files:

- `Iris/_docs/round3/current_route_required_validations.json`이 지시하는 exact tests/artifacts
- 신규 adoption current-route receipt와 regression report

Implementation Notes:

- staging/candidate가 아니라 live current facts/rendered/runtime/package identities를 사용한다.
- current-route에서 canonical Lua/runtime/package mismatch를 독립 재현할 수 있는 별도 result를 기록한다. 기존 RTC non-coverage나 tooling-only failure는 mismatch로 세지 않는다.
- actual Lua reconstruction, consumer module load, case-variant fixture, field-level payload contract, stale bridge/monolith absence를 포함한다.
- validator 전후 live hash census로 validation tool mutation `0`을 증명한다.
- C-13은 `EXECUTION_CONTRACT.md` 또는 live required-validation manifest가 이 exact adoption에 specific command를 mandatory로 선언한 경우에만 `resolved_pass/applicable`이다. 그때 exact command를 실행한다. 별도 Clean-Checkout 상태나 owner 선호는 자동 포함하지 않으며 ambiguous/deferred이면 terminal closeout을 막는다.

Validation:

- Phase 0에서 봉인하고 Change 5에서 pre-proved한 동일 official current-route command가 full required denominator로 exit `0`; axis subset이나 `non-RTC axes PASS`는 terminal PASS 대체 불가
- canonical mismatch reproduced count와 failure family 분류 완료
- actual mismatch가 없으면 `rtc_product_mismatch_reproduced=false`, `g6_triggered=false`
- actual mismatch가 독립 재현된 경우에만 `rtc_product_mismatch_reproduced=true`와 별도 G6 handoff eligibility 기록; 이 계획 안에서 G6 실행 금지
- execution-time full denominator consumption PASS
- `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` exit `0`
- protected upstream/unrelated Lua/package mutation `0`
- environment/tool failure와 product failure 분류 완료

---

### Change 10 — Phase 9 representative in-game consumer/display smoke

Purpose:

Change 4에서 사전 봉인한 표본으로 실제 consumer가 새 generation을 표시하는지 확인한다.

Files:

- attempt-local in-game checklist, observation log, screenshot/reference manifest
- C-09가 tooltip scope를 채택한 경우 tooltip parity/4-line report

Implementation Notes:

- Browser 경로는 `IrisBrowserDetail.lua -> IrisAPI.Description -> layer3_renderer.lua -> Iris/Data/IrisLayer3DataChunks`로 관찰한다.
- 사전 봉인 표본은 adopted naturalized, unchanged control, unadopted, case-variant collision pair를 포함한다.
- 관측 실패/성공을 보고 표본을 교체하지 않는다.
- C-09가 in-scope일 때만 tooltip generation/4-line contract를 검증한다.
- C-09가 out-of-scope이면 body/tooltip generation independence를 closeout known limits에 기록하고 tooltip parity claim을 금지한다.
- machine denominator를 sample 수로 축소하지 않는다.

Validation:

- pre-bound sample identity/hash PASS
- representative adopted text와 unchanged control PASS
- unadopted body exposure `0`
- raw metadata/placeholder exposure `0`
- existing consumer path unchanged
- applicable tooltip contract PASS

---

### Change 11 — Phase 10 documentation and claim-bounded closeout

Purpose:

판정, generation identity, validation 결과, 남은 한계를 additive 기록으로 닫는다.

Files:

- `validated_naturalization_current_runtime_adoption_closeout.md`
- `current_generation_ledger_packet.md`
- `top_doc_sync_report.json`
- `claim_boundary_validation_report.json`
- `final_adoption_verdict.json`
- `rtc_g6_trigger_disposition.json`
- machine-policy applicability와 실제 canonical command 결과를 보존하고, 성공한 adoption 사실만 `DECISIONS.md`/`ARCHITECTURE.md`/`ROADMAP.md`에 필요한 범위로 additive sync한다. applicable denial은 문서 supersession으로 바꾸지 않고 `blocked_current_machine_policy`로 기록한다.

Implementation Notes:

- C-10의 synchronized terminal token `validated_naturalization_current_runtime_adoption_complete` 하나만 canonical로 사용한다.
- C-11이 확인한 existing contract가 요구할 때만 해당 eligibility를 만족하는 implementation/result review 또는 live-cutover authorization을 수행한다. G4/G6 attempt-specific owner seal을 재사용하거나 새로 요구하지 않는다. 요구되지 않거나 수행되지 않은 review는 `independent_review_status=not_required|not_performed`, 근거 contract path/hash, known limit를 명시하며 PASS credit을 만들지 않는다.
- C-13이 ambiguous/deferred이면 terminal closeout을 차단한다.
- `rtc_g6_trigger_disposition.json`은 current RTC product defect `none`, prior trigger `temporary_tooling`, existing certification coverage `does_not_cover_candidate`, canonical post-link mismatch reproduction 결과, G6 trigger boolean을 서로 다른 필드로 기록한다.
- predecessor/successor precedence, referent existence/hash, protected historical rewrite `0`을 검증한다.
- C-09 out-of-scope이면 body/tooltip independence와 tooltip parity non-claim을 known limits에 남긴다.

Validation:

- top-doc terminology consistency PASS
- claim-boundary scan PASS
- release/Workshop/B42 overclaim `0`
- package/current rendered/source authority 혼동 `0`
- applicable existing review/seal PASS

---

## 7. Validation Plan

### Automated Validation

- Python unit tests: 신규 orchestrator, identity parser, projection, chunk reconstruction, transaction/rollback, claim scan
- exact path/hash/Git blob/referent validation
- exact candidate payload/manifest/assessment/determinism/compiler/shape anchor validation; sibling selection `0`
- observed facts/manifest identity ↔ sealed lifecycle role 및 generation pair coherence
- candidate/current source provenance binding
- candidate/current source bidirectional key-set equality와 union-denominator parity
- full-set key/state/text shape (`2105 / 2084 / 21`, 실행 시 재확정); count는 membership evidence가 아님
- exact case-sensitive key와 collision preservation
- JSON/Lua/reconstruction의 unadopted `text_ko` absent-or-nil, empty string FAIL, current-like `publish_state` absent
- forbidden metadata와 unadopted text leakage 검사
- Lua manifest/chunk completeness, duplicate/cross-chunk overwrite, orphan 검사
- actual Lua reconstruction과 rendered parity
- candidate-scoped canonical Lua/runtime/package preflight와 post-link mismatch reproduction check
- 모든 receipt가 Validation Limits의 normative independent-field schema(`coverage_status`, `tooling_status`, `payload_status`, `independent_reproduction_status`, `g6_trigger`)를 사용하며 field 간 동시 상태를 보존
- live-installed staging/build-context marker와 attempt-local path/identifier exposure `0`
- RTC lifecycle/bundle/`current_route_required_validations.json` before/after mutation `0`
- materialized descriptor → current descriptor non-circular hash edge와 self-reference `0`
- mirror transaction failure injection과 exact rollback equality
- isolated package/live byte parity
- fresh current-route required validations
- C-13의 두 허용 contract 중 하나가 exact adoption/specific command를 mandatory로 선언해 applicable로 판정된 경우에만 repository-wide gate
- execution contract exact readpoint/applicable clauses/conflict count
- Lua syntax: `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
- top-document/claim-boundary scan

모든 명령은 attempt receipt에 exact argv, cwd, interpreter/tool version, exit code, stdout/stderr hash를 기록한다. 관련 명령이 exit code `0`으로 끝나지 않으면 PASS로 기록하지 않는다.

### Manual Validation

- fresh plan review에서 synchronized candidate/adoption authority decisions 확인
- rendered text와 Lua reconstruction의 대표 항목 spot check
- Iris Browser 상세 설명의 대표 adopted/unchanged/unadopted/case-variant in-game smoke
- C-09 적용 시 Alt tooltip 4줄 및 generation parity 확인
- C-11이 확인한 existing contract가 요구할 때만 implementation/result review 또는 exact live-cutover authorization

### Validation Limits

모든 validation receipt는 서로 독립인 다음 축을 사용한다. 한 축의 값으로 다른 축을 추론하지 않는다.

```text
coverage_status = covered | not_covered | unknown
tooling_status = pass | blocked_policy | failed_tooling | failed_environment | not_run
payload_status = pass | mismatch | not_evaluated
independent_reproduction_status = pass | fail | not_evaluated
g6_trigger = true only when payload_status=mismatch and independent_reproduction_status=pass
```

`not_covered`, `blocked_policy`, `failed_tooling`, `failed_environment`은 payload mismatch가 아니며 payload 검사가 실행되지 않았으면 반드시 `not_evaluated`다. 반대로 canonical payload mismatch도 independent reproduction이 없으면 G6 trigger가 아니다.

Post-cutover terminal-required validation 실패는 live generation을 애매한 current 상태로 남기지 않는다. cutover identity/parity 실패, package payload mismatch, full-denominator current-route product mismatch, in-game displayed-text/consumer mismatch는 terminal claim과 downstream eligibility를 false로 만들고 exact preimage로 자동 rollback한다. package 산출물은 폐기한다. package/current-route/in-game의 environment/tooling-only 실패도 제품 결함으로 주장하지 않지만 terminal validation이 미완료이므로 package를 폐기하고 live generation을 rollback한 뒤 `blocked_environment_or_tooling`으로 닫는다. rollback 자체는 defect 판정이 아니라 fail-closed current-state 복구다. rollback 검증 실패는 `blocked_rollback_integrity`로 수동 복구에 이관한다.

- 2,084개 public text 전체 인게임 human review 없음
- multiplayer/server-side validation 없음
- 장시간 runtime 안정성 및 성능/메모리 측정 없음
- 외부 모드 전체 compatibility sweep 없음
- Workshop 설치/업데이트 및 release publication 없음
- B42 전체 compatibility 검증 없음
- power-loss atomicity 또는 intermediate-reader visibility zero 증명 없음
- 독립 제3자 clean-checkout 재현은 별도 gate가 요구하지 않는 한 없음
- 다른 Iris 기능 전체 manual QA 없음
- 이 계획 안에서 G6 RTC 기술 부채 closure, bundle/lifecycle adoption, required-validation RTC reference mutation 없음
- existing contract가 independent review를 요구하지 않으면 independent review 없이 종료될 수 있으며, 요구 여부·미수행 사실·review credit `0`을 closeout known limit로 기록

---

## 8. Risk Surface Touch

### Authority Surface

높음. immutable candidate, current source provenance, current rendered 역할, Registry-owned writer, exact generation descriptor와 terminal claim을 건드린다. RTC required-gate/lifecycle은 read-only이며 수정하지 않는다.

### Runtime Behavior Surface

높음. 실제 게임이 require하는 `IrisLayer3DataChunks.lua`와 chunk payload를 교체한다. module path와 renderer logic은 유지한다.

### Compatibility Surface

높음. case-sensitive key, collision preservation, chunk ordering, existing consumer load, Windows lossless route, package guard가 모두 적용된다.

### Sealed Artifact Surface

높음. candidate와 predecessor evidence는 read-only로 소비하고 새 adoption generation/closeout evidence만 추가한다. RTC/G6 evidence는 새로 봉인하거나 수정하지 않으며 historical artifact rewrite는 금지한다.

### Public-Facing Output Surface

높음. 2,084개 adopted item의 한국어 Layer 3 본문이 current Browser 표면에 바뀐다. 21개 unadopted item에는 본문이 생기지 않아야 한다.

---

## 9. Risk Analysis

### Architecture Risk

- current rendered를 source authority로 잘못 승격할 위험
- candidate admission, Registry adoption, candidate runtime verification, RTC debt, Publish acceptance, package projection claim을 합칠 위험
- validator/exporter/package script에 live writer 권한을 분산할 위험
- Tooltip의 별도 data surface를 Layer 3 본문과 무근거로 결합할 위험

Mitigation: C-01a~C-13 adjudication, authority-role decision, single-writer allowlist, source/runtime/package claim scan을 hard gate로 둔다.

### Runtime Risk

- rendered, chunks, manifest 중 일부만 교체되어 mixed generation이 되는 위험
- stale/orphan chunk가 manifest 밖에 남는 위험
- unadopted item의 `text_ko`가 absent/explicit nil이 아니거나 빈 문자열로 존재하는 위험
- candidate metadata가 Lua에 섞이는 위험
- manifest-last 이전의 중간 상태를 consumer가 읽는 위험

Mitigation: off-live complete materialization, exclusive lock, exact preimage, directory-level swap, manifest-last, post-apply reconstruction, failure 시 자동 generation rollback을 사용한다.

### Compatibility Risk

- PowerShell JSON object 변환에서 대소문자 key가 붕괴하는 위험
- 기존 RTC non-coverage를 실제 제품 결함 또는 G6 blocker로 오분류할 위험
- tooling/one-use evidence failure를 canonical Lua/runtime/package mismatch로 오분류할 위험
- legacy monolith/bridge가 다시 포함되는 위험

Mitigation: pair-preserving Python route, candidate-scoped pre/post-link canonical checks, package/live byte comparison, failure-family 분리, forbidden path scan을 사용한다. G6 trigger는 actual canonical mismatch의 독립 재현에만 열린다.

### Regression Risk

- 기존 Browser consumer module path가 바뀌는 위험
- unrelated Lua/UI/package 파일이 transaction에 포함되는 위험
- validation tool이 live surface를 수정하는 위험
- dirty worktree의 사용자 변경이 execution baseline/closeout에 섞이는 위험

Mitigation: exact write allowlist, before/after protected census, clean tracked execution base, current-route consumer load test, unrelated diff count `0`을 요구한다.

---

## 10. Rollback Plan

Rollback 단위는 개별 파일이 아니라 직전 live generation 전체다.

포함 surface:

- current rendered
- runtime manifest
- runtime chunk directory 전체
- `Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json`
- C-09에서 동일 generation으로 판정된 경우 tooltip surface
- 관련 tracked state

Package output은 authority가 아니므로 rollback하지 않고 폐기 후 재생성한다.

실행 순서:

1. live apply 직전 path/type/size/SHA-256/Git blob/EOL을 가진 fresh preimage와 hash-bound snapshot manifest를 만든다.
2. exclusive lock 후 preimage drift를 다시 확인한다.
3. §7 Validation Limits의 post-cutover rollback disposition을 normative trigger source로 사용한다. write error, partial swap, manifest failure, runtime mismatch, orphan, metadata leakage, unadopted text exposure, generation mismatch뿐 아니라 cutover identity/parity failure, package payload mismatch, official package command failure, full-denominator current-route product mismatch, current-route environment/tooling failure, in-game displayed-text mismatch, in-game consumer-path mismatch, in-game environment/tooling failure가 발생하면 자동 rollback한다.
4. exact generation descriptor, runtime manifest, runtime chunks, rendered를 승인된 복구 순서로 되돌리고 새 orphan path를 제거한다.
5. exact preimage recensus와 actual Lua reconstruction을 실행한다.
6. 모든 preimage hash equality와 new path `0`이 성립해야 rollback PASS다.
7. rollback verification이 PASS하지 않으면 `blocked_rollback_integrity`로 닫고 자동 재시도·부분 current 유지·terminal claim을 금지한 채 수동 복구에 이관한다. environment/tooling-only 원인의 rollback은 제품 결함 판정이 아니라 fail-closed state 복구다.

Rollback 검증 실패 시 다음 상태로 fail-closed한다.

```text
adoption_complete=false
current_generation_valid=false
mixed_authority_recovery_required=true
package_projection_allowed=false
in_game_validation_allowed=false
terminal_claim_allowed=false
```

failed attempt receipt와 journal은 보존하고 one-use authorization/attempt identity를 재사용하지 않는다.

---

## 11. Governance Constraints

- `Philosophy.md` 준수: Iris는 Iris 내부 100% Lua runtime과 오프라인 정적 생산 경계를 유지하며 Pulse나 다른 spoke에 역의존하지 않는다.
- source/classification/description/runtime 책임 분리를 유지한다. runtime은 봉인된 정보를 표시할 뿐 새 의미나 quality를 판정하지 않는다.
- current rendered와 package는 source authority가 아니다.
- immutable candidate와 protected historical evidence를 rewrite하지 않는다.
- additive amendment와 minimal diff를 우선한다.
- Registry-owned single writer만 current rendered/runtime과 exact generation descriptor path를 변경한다.
- generation descriptor path가 closed protected output set 밖이면 explicit additive authorization 없이는 생성·수정하지 않는다.
- exporter의 protected path refusal와 package의 RTC guard를 우회하지 않는다.
- exact case-sensitive key와 collision preservation을 유지한다.
- `IrisLayer3Data.lua` monolith와 `IrisDvfBridgeData.lua` stale bridge를 되살리지 않는다.
- predecessor RTC PASS, stale snapshot, superseded evidence를 current credit으로 재사용하지 않는다.
- G6은 `not_applicable_temporary_tooling_trigger`로 유지하며 실제 canonical mismatch가 독립 재현되기 전에는 기술 부채 계획, prerequisite 또는 G4/G5 blocker로 실행하지 않는다.
- RTC lifecycle/bundle/`current_route_required_validations.json`은 read-only protected surface로 유지한다.
- package는 live payload의 disposable isolated projection이다.
- human/owner/independent review authority를 자동화가 대리하지 않는다.
- product failure와 environment/tool failure를 구분하되 environment failure를 PASS나 waiver로 바꾸지 않는다.
- top-doc update는 최종 판정 사실만 additive 반영하며 현재의 unrelated 사용자 변경을 덮어쓰지 않는다.
- release, Workshop, B42, deployment readiness를 이 계획의 terminal claim에 포함하지 않는다.

---

## 12. Expected Closeout State

Expected closeout target: `complete`, 단 아래 단계적 상태를 엄격히 구분한다.

```text
planning_state=revision_complete_fresh_review_required
phase0_entry=blocked_pending_fresh_plan_review
changes_2_through_11=blocked
live_mutation=blocked
terminal_closeout=blocked_pending_applicable_C09_through_C13
```

동기화 시점에는 declared candidate payload, candidate manifest, IAR assessment와 G5 consumption record가 모두 존재하고 exact SHA-256과 일치했다. 따라서 fresh plan review PASS 뒤의 현재 예상 조사 결과는 다음과 같다.

```text
current_expected_investigative_outcome=phase0_complete_eligible_for_phase1
current_expected_reason=exact_candidate_and_assessment_referents_observed
target_closeout=complete_only_if_phase0_reverification_and_all_later_gates_pass
```

이것은 PASS 선취득이 아니다. fresh plan review가 PASS하면 Phase 0는 read-only 조사를 실행하고, 그 시점의 Git/working identity가 위 관찰과 다르거나 exact referent가 사라졌으면 `phase0_complete_blocked`로 종료한다.

실행 후 `complete`가 되려면 다음이 모두 필요하다.

- fresh plan review에서 Critical/Important `0`과 Phase 0 eligibility 확인
- C-01a~C-13의 적용 가능한 판정이 `resolved_pass` 또는 `not_applicable`로 닫힘
- candidate/current provenance와 admission PASS
- exact candidate anchor 전부 PASS 및 sibling/rebaseline `0`
- current facts/manifest sealed-role match와 pair coherence PASS
- candidate/source bidirectional key-set equality PASS
- immutable candidate mutation `0`
- candidate-scoped canonical runtime/package preflight와 single-writer authorization PASS
- exact generation descriptor path/owner/protected-set authorization PASS
- mirror apply/rollback 및 failure injection PASS
- rendered/runtime generation alignment PASS
- live cutover와 fresh full-denominator official current-route exit `0`
- official package/live payload parity PASS
- representative consumer/display smoke PASS
- C-10 terminal token 확정
- C-11이 이 adoption/current-route에 실제 applicable하다고 확인한 review/seal 완료
- actual canonical mismatch 독립 재현이 없으면 `g6_triggered=false`; 있으면 별도 후속 handoff만 생성하고 이 계획의 G6 실행 `0`
- C-13 terminal denominator 판정 완료
- claim-boundary scan PASS

하나라도 충족되지 않으면 `partial`을 성공의 다른 이름으로 사용하지 않는다. live mutation 전 전제 실패는 `blocked`, live apply/validation 실패는 rollback 완료 후 `implemented_only` 또는 `blocked` 중 실제 상태로 기록하며 terminal adoption claim은 만들지 않는다.
