# Implementation Plan — Iris Tooltip T3-D1 Menu·Tooltip Layer 3 표시 조건 및 EN 소비 Record Fact 연결 정합성

> 실행 상태(2026-08-30): **T3-D1 complete**. 사용자 지정 12개 Build 41 정정을 Menu·EN·owner·T1·T2·product까지 전파했다. 필수 canonical A/B·comparator와 최종 actual Menu relation 모두 PASS이며 initial 1,314 pair는 resolved 1,314 / retained 0 / unresolved 0이다. 상세 current binding과 검증은 문서 끝의 최종 closeout을 따른다. 과거 실패·superseded 결과는 보존하고 전체 T3는 partial, runtime_adopted=false다.

> 원 계획 작성 시점의 상태: 실행 전 계획. 2026-08-30 코드·계약·산출물의 읽기 전용 조사에 기반한다. 당시 작성·개정은 본 문서에 한정하며, display disposition 확정·producer 수정·generation 전환·T3-D1 완료를 의미하지 않았다.
>
> 양식: `docs/PLAN_TEMPLATE.md`의 12개 절과 각 Change의 Purpose / Files / Implementation Notes / Validation 구조.
>
> 입력: 사용자 제공 「Iris Tooltip T3-D1 — Menu·Tooltip Layer 3 표시 조건 및 EN 소비 Record Fact 연결 정합성 통합 ROADMAP」. 두 원안이 합의하지 않은 validation depth, Branch C locale precondition, 별도 owner ratification gate는 §4.4에 미결정으로 보존한다.
>
> 개정: 2026-08-30 Integrated Review 반영. R-1의 Branch A Philosophy depth-ordering 대조와 R-2의 inherited evidence-gap exact-set disposition을 계획의 명시적 검증·완료 조건으로 채택했다. 네 가지 비차단 보완과 provenance wording도 반영했다. 이는 검토 간 severity/verdict 충돌의 소급 판정이나 새 review PASS, 실제 Branch 승인 또는 execution completion 선언이 아니다.
>
> 실행 보완: 외부 입력/작업 경계를 §4.5에 한정하고, 최종 required set을 original T3 acceptance에 인계하는 절차를 Change 8에 명시했다. 검증은 §7의 세 논리 그룹에 통합하여 최종 단계에 수행하며, 재사용 가능한 기존 관측·동일 subject의 결과와 중복되는 실행을 요구하지 않는다. 기존 authority의 필수 gate는 유지한다.
>
> 상위 상태: T1 display contract / upstream readiness 및 T2 static staging 완료. T3는 working implementation `partial`이며, 이 계획은 T3에서 드러난 Layer 3 relation 두 축만 다루는 bounded successor다.

## 1. Objective

기존 authority와 production path 안에서 다음 두 문제를 해결하고 원래 T3의 package / install / actual PZ / visual integration validation으로 돌아갈 수 있는 근거를 만든다.

1. **P1 — 표시 조건:** Tooltip S2 selected 1,314개 중 Menu KO/EN이 침묵하는 exact 12개에 대해, 기존 silence decision의 실제 surface scope를 확인하고 legitimate difference / Tooltip eligibility defect / Menu omission defect / authority insufficient로 disposition한다.
2. **P2 — EN fact 연결:** 최종 disposition상 Menu EN record가 필요한 모든 항목에서 실제 소비 record를 producer output, approved input, exact Layer 3 fact identity까지 연결한다.

```text
exact current subject / initial relation universe
→ 12-item silence authority scope
→ P1 display disposition
→ 필요한 최소 upstream correction
→ final-required Menu KO/EN consumer record ↔ approved fact
→ affected artifact propagation / non-target preservation
→ scoped validation / T3-D1 closeout
→ original T3 integration validation 재개
```

P1이 final expected Menu visibility를 결정하므로 P2의 필수 record 범위 확정에 선행한다. EN evidence 조사는 먼저 할 수 있지만 missing row를 성공으로 분류하는 판정은 P1보다 앞서 수행하지 않는다. 두 문제를 `1,314 + 12 = 1,326`개의 독립 결함으로 합산하지 않는다.

---

## 2. Scope

- exact current T1/T2/T3 입력, Menu generation/pointer, KO/EN actual consumer readpoint와 초기 relation universe 결속.
- 12개가 current silent 33에 포함되는지 exact FullType / fact pair로 확인.
- body disposition, role-material readiness, Tooltip eligibility, locale visibility의 기존 authority lineage 비교.
- Branch A 최종 표시 상태와 Philosophy의 Menu depth-ordering·same-fact·silence 원칙 대조.
- authority가 요구하는 경우에만 Tooltip upstream eligibility 또는 Menu production의 최소 수정.
- actual EN record → producer/output → approved input → fact identity의 existing evidence 조사, 필요시 격리된 deterministic reconstruction 또는 기존 경로의 최소 evidence 보완.
- 기존 Menu 관측 harness와 relation comparator의 bounded 보완. observation, provenance 검증, Tooltip comparison의 책임을 분리한다.
- 실제 영향에 따른 Menu generation / owner projection / T1 / T2 / T3 product copy successor 전파.
- 초기 정상 1,302개, support 2,280개, scope 밖 Layer 2/4 및 Layer 3 data의 보존 확인.
- 필요한 검증, validation ceiling, T3-D1 결과와 original T3 잔여 범위 기록.
- inherited `unverified_without_independent_consumer_evidence`의 resolved / retained / unresolved exact-set 처분과 authority 문서의 후속 갱신 경계 기록.

### Explicitly Out Of Scope

- Alt reader, wrapping / geometry / cache / locale lifecycle 재설계.
- Classification / Layer 2, Layer 4 semantic identity·selection, Recipe / Right-click 로직 수정.
- 신규 Layer 3 fact, 신규 KO description·EN translation, 기존 public 문장의 요약·재작성.
- `special_context` 필드의 시스템 전체 폐기, schema/key/전체 reader 제거 및 과거 source trace 삭제. 아래 승인된 일반 설명 통합은 기존 fragment·번역·registered frame의 조립까지만 허용하며 새 사실·임의 번역·자유로운 prose 작성은 계속 금지한다.
- approved absence 175건과 empty-core 791건의 재판정.
- 전체 Layer 3 truth audit, public-text quality 재심사, translation quality 인증.
- package 생성·사용자 설치·actual PZ·Alt press/release·font/UI-scale·visual fit 검증 실행.
- RTC certification, DVF freeze, Publish / release / Workshop / deployment.
- 새 Registry, Tooltip 전용 provenance framework, 상시 validator/schema/regular test membership 추가.
- 다른 Spoke, Pulse platform, JVM/Java/Mixin runtime 변경.

현재 존재하는 사용자 변경과 T3 작업을 정리하거나 덮어쓰지 않는다. 이번 문서 작성에서는 위 조건부 구현도 실행하지 않는다.

---

## 3. Non-Goals

Menu와 Tooltip의 coverage를 무조건 같게 만드는 작업이 아니다. `Philosophy.md`의 “Iris 메뉴는 Iris 툴팁보다 상세한 정보를 제공한다”, same-fact/non-contradiction, 근거 부족 시 침묵 원칙을 함께 적용하여 현재 차이가 허용되는지를 근거로 설명하는 작업이다. depth-ordering을 이유로 Branch A를 미리 배제하거나, coverage 차이가 가능하다는 이유로 그 대조를 생략하지 않는다.

`silent` token, non-empty `primary_use`, 현재 producer 동작, Tooltip 문자열 중 어느 하나도 public visibility permission으로 승격하지 않는다. Tooltip fact/output은 최종 비교 대상이며 Menu independent evidence의 출처가 아니다. EN runtime chunk에 `fact_id`를 추가하거나, 번역문을 해석하여 identity를 역산하는 것을 기본 해법으로 삼지 않는다.

T3-D1 완료는 전체 T3 완료나 runtime adoption이 아니다. build-side consumer 관측을 실제 PZ 검증으로, current deterministic derivability를 과거 original-run provenance로, key-set 일치를 번역 품질로 확대하지 않는다.

---

## 4. Assumptions

### 4.1 Authority와 조사 subject

- 헌법은 `docs/Philosophy.md`다. “Iris 메뉴는 Iris 툴팁보다 상세한 정보를 제공한다”는 depth-ordering, 근거 부족 시 침묵, Menu/Tooltip same-fact·non-contradiction, Alt 전용 최대 4줄, runtime 100% Lua와 게임 상태 비변경을 함께 유지한다. sealed decision과 충돌하면 상위 Philosophy를 우선한다.
- `docs/DECISIONS.md`의 Menu/Tooltip presentation, Layer 3 optional role-material, Layer 2–3 locale, stateless generation, T1/T2, clean-checkout 및 evidence integrity 결정을 따른다.
- `docs/ARCHITECTURE.md`의 producer / owner / runtime / validation 책임 분리와 `docs/ROADMAP.md` Iris의 T3 `partial` 상태를 따른다.
- `docs/EXECUTION_CONTRACT.md`는 disclosure / claim-evidence binding / ceiling / closeout 규율이다. 새 visibility policy의 출처로 사용하지 않는다.
- human command literal owner는 `Iris/build/ENTRYPOINTS.md`, current locator는 `Iris/_docs/authority/iris_current_route_index.json`이다. 과거 문서나 source filename만 보고 retired route를 재활성화하지 않는다.
- 조사 시 HEAD는 `b9d7ae289b226082c191b1f6a23e6b363c6d99a6`, HEAD tree는 `c5d1d1c4ed9d4142e1cdb7dfdc854255c19ecb0b`다. **dirty working tree이므로 이 commit/tree가 조사한 전체 파일 내용의 identity는 아니다.** 실행 시 relevant source/data hashes, tracked/untracked 상태와 exact validation subject를 별도 결속한다.
- 시작부터 `.gitattributes`, T3 reader/Alt·translation·harness·test·entrypoint와 문서 변경, `b/`, `g/`, `i/` 하위 기존 test checkout 상태가 있었다. 이는 본 계획 작성의 변경이 아니다.

### 4.2 읽기 전용으로 확인한 현재 입력

| 항목 | 현재 readpoint / 관측 |
|---|---|
| T1 successor | `60796744ffb889477161d243a1443c9de57d49b0`; final root `C:/Users/MW/Downloads/coding/PZ-t2/t1-final` |
| T2 machine subject | `d64692ac26cdc21e4c7f558a0fe93278f64b16d1`; tree `850e0af81af9b9fda8ee7df26847f88a4b32b142` |
| T2 final root | `C:/Users/MW/Downloads/coding/PZ2/t2-final` |
| T1/T2 artifact binding | route에 등재된 T1 4개 및 T2 3개 파일이 존재하고 각 SHA-256과 일치 |
| T2 product copy | `Iris/media/lua/client/Iris/Data/IrisTooltipT2Data.lua` SHA-256 `4d9d109eaaf0f61e638ebf94cee33c8c306e88f322143c74c8eecdb8131646fd`; final T2와 일치 |
| Menu current generation | `dvf33-028a396886eee3ed9bbb6f610c64c8e886ac3e3aab7b8c7381d5d4a48d7145e9` |
| support / initial selected | T2 manifest FullType 2,280 / S2 exact FullType·fact pair 1,314 |
| T2 sealed result trace | 0/1/2/3/4줄 분포 `367 / 825 / 895 / 137 / 56`; 개정 시 current T2 manifest의 line 수를 읽기 전용 재집계하여 확인. Branch B에서는 successor 분포와 exact row-count delta를 별도 기록 |
| initial selected pair hash | sorted pairs를 ASCII JSON compact로 직렬화한 SHA-256 `c5db8a28892229df25f9b65b22e045515b3ac1fcc0d476bb8a1231131832cd28`; 기존 comparator와 같은 방식 |
| body universe / public / silent | pointer-selected rendered 2,105 / non-empty `text_ko` 2,072 / silent 33 |
| selected ∩ silent | 아래 exact 12개. 각각 single core ID가 T2 S2 identity와 일치하고 `primary_use`가 존재하며 current `fact_origin.primary_use`는 `direct_use` |
| inherited Menu observation | T3 실행 기록에서 selected 중 KO/EN 각 1,302개 관측, 12개 침묵. 이번 문서 작성 중 실제 consumer harness는 재실행하지 않음 |
| inherited evidence-gap status | T1 selected 1,314개는 `unverified_without_independent_consumer_evidence`; `docs/DECISIONS.md`의 T1 boundary와 `docs/ARCHITECTURE.md`의 independent consumer evidence 규정. T3-D1 final report에서 §6 Change 6의 exact-set 처분으로 연결 |
| formal state | current route T2 `state=complete`, `runtime_adopted=false`; T3 working implementation `partial` |

```text
Base.BarbedWire
Base.CarBatteryCharger
Base.Hinge
Base.Jack
Base.LeatherStrips
Base.LugWrench
Base.Paintbrush
Base.Pipe
Base.Scotchtape
Base.ScrapMetal
Base.TirePump
Base.Toolbox
```

위 12개는 모두 현재 rendered에서 `source=layer3_role_realign_silent_v1`, `text_ko` 없음, core fact 있음으로 확인됐다. 이 관측은 silence authority의 scope 판정이 아니다. `direct_use`도 visibility 결론을 대신하지 않는다.

175 approved absence는 owner-output `absence_entries`의 별도 domain이고, 791 empty-core는 current generation의 role-material domain이다. 1,314 selected relation ledger를 이들 수치와 합산하거나, 이후 S2 생략을 이유로 초기 ledger에서 12개를 삭제하지 않는다.

### 4.3 코드에서 확인한 판단·증거 경계

| 경계 | 실제 코드와 의미 | 계획에 미치는 영향 |
|---|---|---|
| Menu body production | `Iris/build/description/v2/tools/build/layer3_body_role_realign.py`의 `compose_role_material`, `classify_disposition`, `build_successor_rendered`: readiness에 따라 `menu_text_ko`를 비우고 silent source를 기록하지만 `core_source_fact_ids`는 유지할 수 있음 | token보다 readiness / disposition / ratification lineage를 조사 |
| Menu EN production | `Iris/tooling/src/iris_tooling/build/build_layer3_english_localization.py`의 `build_english_entries`: `text_ko` 없는 row 제외. facts의 `primary_use`, context, acquisition을 기존 번역 경로로 조합 | EN record 범위는 Menu public visibility 뒤에 결정됨 |
| Tooltip owner projection | 같은 파일의 `build_tooltip_t1_owner_entries`: single core ID와 non-empty `primary_use`로 `tooltip_eligibility=eligible`, KO/EN primary-use surface 생성. `text_ko` predicate 없음 | 현재 P1이 생기는 구체적 upstream 분기. 정당성은 기존 authority로 별도 판정 |
| T1 S2 admission | `Iris/tooling/src/iris_tooling/domains/tooltip_t1/audit.py`의 `run_candidate`: single core / owner-approved / eligible / locale surface를 검사. core가 있는데 fact가 eligible이 아니면 correction | Branch B에서 flag만 바꾸거나 owner row만 삭제하면 정상 생략이 되지 않음 |
| Menu KO consumer | `IrisLayer3DataCurrent.lua → IrisLayer3DataChunkIndex.lua → IrisLayer3DataLookup.get → layer3_renderer.getText → IrisItemDetailModelAssembler.layer3Payload` | current pointer가 선택한 실제 record와 generation fact mapping을 함께 관측 |
| Menu EN consumer | `layer3_renderer.getText`가 먼저 KO public body와 `internal_only` 여부를 확인한 뒤 `IrisLayer3EnglishLookup.get → Layer3English/Index.lua → Chunk*.lua[FullType]` 소비 | EN key 존재만으로 실제 소비 또는 공개를 증명할 수 없음 |
| EN output shape | `_write_runtime`은 sorted FullType을 200개 단위 chunk로 직렬화. Index는 first/last/module, payload는 FullType→string이며 fact ID 없음 | output bytes와 producer/input을 build-side evidence로 연결 |
| generation evidence | `_current_projection`이 pointer/descriptor와 facts·approved candidate raw identity를 대조. current descriptor는 KO generation 산출물을 기록하며 EN chunk는 포함하지 않음 | KO descriptor만으로 EN provenance 완료 선언 금지 |
| T3 observation | `Iris/test/lua/tooltip_t3_runtime_harness.lua`는 실제 ViewModel/lookup을 호출하고 KO record 참조와 EN chunk read를 관측 | 테스트 stub 환경의 consumer 실행 evidence이며 actual PZ evidence는 아님 |
| 현재 relation comparator | `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py::menu_relations`: 1,314/pair hash 고정, 모든 selected의 Menu presence 요구, EN `(module, fact)` tuple 입력 비교 | authority-backed silence와 successor denominator를 구분할 bounded 보완 필요 |
| 현재 EN evidence caller | 같은 파일의 CLI 경로가 `en_identity_evidence={}` 전달. fixture의 complete tuple map은 판정 회귀용 synthetic data | 빈 값을 Tooltip ID로 채우지 말고 actual producer/input 증거를 먼저 확립 |
| T3 payload admission | 같은 wrapper의 `EXPECTED_SHA256`이 현 T2 bytes를 고정. `IrisTooltipT2Lookup.lua`는 exact key / explicit locale / atomic 0~4 rows만 소비 | T2 successor이면 payload와 admission hash를 함께 전환. runtime에 12-item 분기 금지 |

`docs/DECISIONS.md`가 가리키는 `docs/iris_layer3_body_role_realignment_policy.md`는 최초 조사 시 current checkout에 없었다. Change 2 초입에서 존재 여부와 repository 내부 archive / exact Git history를 통한 복원 가능성을 조기 확인한다. 외부 archive가 필요하면 §4.5의 입력 경계를 적용하며 사용자 디렉터리를 탐색하지 않는다. 존재하는 `disposition_readiness_contract.json`, `policy_ratification_contract.json`, proposal/current-install trace와 후속 decision이 필요한 scope를 충분히 입증하는지도 함께 확인한다. 복원 실패 자체만으로 모든 branch를 막지는 않지만, 대체 existing authority로도 A/B scope를 확정할 수 없으면 영향 row는 Branch D다. 누락 문서를 새로 써서 과거 authority로 취급하지 않으며, snapshot evidence 회수를 위해 퇴역 producer를 current gate로 부활시키지 않는다.

Branch C의 named precedent는 `docs/DECISIONS.md` 「Iris DVF System — Layer 3 body production / optional role-material contract」의 2026-08-22 `Base.Bleach` / `Base.Rope` correction이다. 당시 직접 source evidence에 따라 `identity_fallback → direct_use`와 silent → public role material 전환이 이뤄졌다. 조사 시 target 12개에도 `direct_use`가 있지만, 이 값만으로 같은 처분이나 과거 승인을 상속하지 않는다. 해당 선례의 source·approval·candidate·locale·non-target 보존 기준을 비교 자료로만 사용한다.

### 4.4 통합 로드맵의 미결정 항목

| 항목 | 원안의 차이 | 실행 전 처리 경계 |
|---|---|---|
| Validation depth | 전체 `heavy` 대 A/D `standard`, B/C `heavy` | 현재 적용 authority와 실제 touched surface를 대조해 기록. `EXECUTION_CONTRACT.md`의 weight와 로드맵 depth token을 동일 enum으로 취급하지 않음. §7에서 실제 branch와 claim에 필요한 성질만 기존 family에 통합하며 명칭 때문에 전체 suite를 추가하지 않음 |
| Branch C locale precondition | approved KO/EN surface 모두 필요 대 approved KO material + EN owner disposition | Branch C mutation 전에 기존 승인 material과 locale contract를 근거로 확정. 새 번역·KO→EN fallback·EN 미해결 상태의 complete는 어느 해석에서도 금지 |
| 별도 owner ratification gate | 기존 authority 준수 대 branch/common-rule/silence-scope에 별도 receipt 의무 | 기존 승인이 exact scope를 이미 덮는지 먼저 확인. 이 계획으로 별도 mandatory ceremony를 발명하거나 기존 owner boundary를 면제하지 않음 |

미결정 항목은 해당 branch와 완료 판정을 제약하며, read-only census / source 조사 / 기존 EN evidence 수집까지 막는 blanket gate가 아니다. 자료로 해소할 수 없으면 실제 선택에 필요한 구체적 차이와 근거를 정리해 남긴다. 계획 작성 요청 자체를 owner의 display-policy 승인으로 읽지 않는다.

Branch C에서 approved KO만 있고 **허용된 existing producer로 소비할 approved EN material도 없어 새 번역이 필요한 경우**, 해당 Branch C는 T3-D1 안에서 실행·채택할 수 없으며 blocked / unresolved로 남긴다. 이는 위 두 locale precondition 중 하나를 포괄적으로 선택한 것이 아니라 신규 번역 금지의 공통 귀결이다. EN runtime record가 아직 없다는 사실과 approved EN material 자체가 없다는 사실을 구별한다. 기존 material/path가 충분하면 그 binding과 §4.4의 적용 해석을 먼저 확인한다.

reviewer-model gate나 별도 round/seal governance는 T3-D1 기술 완료 조건으로 추가하지 않는다. 기존 repository review / owner / machine axis 분리는 그대로 준수한다.

### 4.5 외부 입력과 작업 경계

외부 경로는 다음으로 한정한다. 이 절은 필요한 경로를 지정하는 것이며, 계획서 개정 요청 자체로 외부 파일 접근·생성·수정을 실행하거나 더 엄격한 실행 프롬프트를 무효화하지 않는다.

| 경로 | 허용 목적과 경계 |
|---|---|
| `C:/Users/MW/Downloads/coding/PZ-t2/t1-final` | current route가 지정한 기존 T1 파일의 읽기 전용 입력. 덮어쓰기·삭제 금지 |
| `C:/Users/MW/Downloads/coding/PZ2/t2-final` | current route가 지정한 기존 T2 파일의 읽기 전용 입력. 덮어쓰기·삭제 금지 |
| `C:/Users/MW/Downloads/coding/PZ2/t3d1` | 이 작업의 전용 외부 작업/output root. 필요할 때만 그 하위의 새 attempt 디렉터리에 EN reconstruction, 기존 gate가 요구하는 clean worktree·wheel/environment·result, 조건부 T1/T2 successor 및 기존 형식의 최종 결과를 생성. 모든 용도별 디렉터리나 산출물을 미리 만들 의무는 없음 |

실행 프롬프트가 repository 밖의 **명시된 입력 읽기만** 허용한다면, 위 output root 지정만으로 외부 쓰기가 허용되지 않는다. 그 경우 실제 실행 지시에는 다음 한정 예외를 함께 채택해야 한다. 채택되지 않았으면 외부 쓰기가 필요한 단계만 차단 사유를 알리고, in-scope 읽기 조사까지 불필요하게 멈추지는 않는다.

> Execution boundary exception for this plan: In addition to the named read-only external inputs, allow read/create/write only within `C:/Users/MW/Downloads/coding/PZ2/t3d1` for the plan-required isolated reconstruction, existing validation environment/work/results, and conditional successor outputs. Preserve pre-existing inputs and attempt results; do not inspect or modify other external paths, game installations, or user files. Do not bypass tool or platform permission checks.

실행 시 root와 새 child의 resolved absolute path를 확인하고 기존 내용은 덮어쓰지 않는다. `_write_runtime`처럼 내부에서 디렉터리를 교체하는 호출은 위 root 아래의 **새 전용 빈 leaf**만 대상으로 하며 root 자체나 기존 attempt를 넘기지 않는다. 기존 gate의 cleanup 역시 확인된 disposable leaf와 그 owner 절차에 한정한다. 경로 길이·도구 제약이 생기면 허용 root 안에서 짧은 child 이름을 사용하고, 임의의 다른 외부 root로 우회하지 않는다.

current locator가 위 읽기 전용 입력 밖을 가리키거나 누락된 policy/environment evidence의 외부 원본이 꼭 필요한 경우, 정확한 필요한 경로와 목적을 먼저 제시하여 입력 범위를 확인한다. locator 문자열을 읽었다는 이유로 외부 탐색 권한을 확장하지 않는다. output 경계 확인을 위해 별도 approval receipt, path registry 또는 proof artifact를 만들지 않는다.

---

## 5. Repository Areas Affected

아래는 **향후 실행 시 읽기 또는 조건부 수정 후보**다. 전부 수정하라는 목록이 아니며, 이번 작성의 실제 write set은 본 문서 하나다.

### Code

- `Iris/tooling/src/iris_tooling/build/build_layer3_english_localization.py`: 공통 owner/EN producer, 기존 deterministic serializer, 필요한 provenance 보완.
- `Iris/build/description/v2/tools/build/layer3_body_role_realign.py`: silence/body/role 생산 술어와 historical lineage 조사. 수정 시 installed package의 실제 source ownership부터 확인.
- `Iris/tooling/src/iris_tooling/build/compose_layer3_role_material.py`, `dvf_3_3_generation_contract.py`, `build_dvf_3_3_complete_generation.py`: Branch C에서만 기존 generation 경로 사용.
- `Iris/tooling/src/iris_tooling/domains/tooltip_t1/contract.py`, `audit.py`: Branch B에서 fact 보존과 approved display omission을 구분하는 bounded input/consumer 보완.
- `Iris/tooling/src/iris_tooling/domains/tooltip_t2/`: 조건부 successor 재생성. T2 semantic 재판정 또는 기본 알고리즘 변경은 의도하지 않음.
- `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py`, `Iris/test/lua/tooltip_t3_runtime_harness.lua`: actual consumer observation / report / evidence admission 보완.
- `Iris/tooling/tests/test_tooltip_t1_contract.py`, `test_tooltip_t1_audit.py`, `test_tooltip_t1_projection.py`, `test_tooltip_t2_projection.py`: 실제 영향이 있을 때 기존 family 안에 회귀 사례 추가.
- `Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua`, `IrisLayer3EnglishLookup.lua`, `layer3_renderer.lua`, `IrisTooltipT2Lookup.lua` 및 `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua`, `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`: consumer readpoint / 비변경 보호 대상. runtime eligibility workaround 대상이 아님.

### Docs

- 신규: `docs/iris_tooltip_t3_d1_layer3_menu_tooltip_display_en_record_fact_relation_consistency_plan.md`.
- 실행 결과가 생긴 경우 기존 `docs/iris_tooltip_t3_static_data_alt_runtime_integration_plan.md`에 Change 8의 final-required scope와 T3-D1 handoff를 반영한다. 특히 A/B로 record 의무가 달라지면 original T3의 acceptance/readpoint도 같은 scope를 사용하도록 additive 갱신한다. `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`는 실제 claim 변경 범위에서만 동기화.
- authority 해석/계약의 approved successor가 필요한 경우만 `docs/DECISIONS.md`, `docs/iris_tooltip_t1_display_contract_policy.md`의 additive 기록 검토.
- command가 실제 변경된 경우만 `Iris/build/ENTRYPOINTS.md` 갱신. 본 계획은 별도의 command authority가 아님.

### Config

- `Iris/_docs/authority/tooltip_t1/layer3_tooltip_input_contract.json`, `tooltip_locale_menu_parity_contract.json`, 관련 decision/input binding: Branch B 또는 승인된 relation interpretation 변경에만 영향.
- `Iris/build/description/v2/data/layer3_body_role_realign/`의 기존 mapping / readiness / ratification / approved-upstream 입력: P1 조사 대상. authorized correction에 필요한 최소 범위만 successor 처리.
- `Iris/_docs/authority/iris_current_route_index.json`: 최종 current artifact locator가 실제 변경된 경우에만 갱신. T3-D1만으로 `runtime_adopted=true` 전환 금지.
- `Iris/validation/clean_checkout/authority/`와 `Iris/_docs/round3/current_route_required_validations.json`: 기존 exact-subject gate의 environment / applicability authority. T3-D1 편의를 위한 membership 축소·면제 금지.

### Generated Artifacts

- `Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json`: 조건부 owner projection successor.
- `Iris/build/description/v2/data/layer3_body_role_realign/approved_upstream/candidate_rendered.json`: Branch C에서만 승인된 input successor.
- `Iris/media/lua/client/Iris/Data/IrisLayer3Generations/<generation>/`와 `IrisLayer3DataCurrent.lua`: Branch C current generation 경로. predecessor module set을 in-place rewrite하지 않음.
- `Iris/media/lua/client/Iris/Data/Layer3English/Index.lua`, `Chunk*.lua`: EN output이 실제 바뀔 때만 기존 producer로 갱신.
- §4.5의 전용 외부 root 하위 T1 handoff / T2 staging / final roots와 `Iris/media/lua/client/Iris/Data/IrisTooltipT2Data.lua`: S2 변경 시에만 successor와 byte-preserving product copy.
- baseline/disposition, EN evidence, propagation delta, final relation·inherited status 처분은 기존 report/closeout에 합쳐 기록하고 기존 관측이 충분하면 참조로 재사용한다. 실제로 필요한 외부 output만 §4.5 안에 생성한다. 항목마다 별도 census/proof 파일, 새 mutable latest pointer / 영구 parallel registry를 만들지 않음.

---

## 6. Planned Changes

### Change 1 — Exact current baseline과 relation universe 고정 (Phase 0)

**Purpose:** historical 수치나 문서 carrier를 actual current subject로 오인하지 않도록 초기 입력과 target을 결속한다.

**Files:** current route, T1/T2 external manifests/receipts, Tooltip product copy, Menu pointer/descriptor/rendered/index/chunks, owner input, 기존 T3 harness/comparator.

**Implementation Notes:**

1. dirty/untracked 상태와 relevant physical hashes를 보존하고 source subject, machine subject, product copy, evidence carrier를 분리한다. gate가 필요하면 기존 clean-checkout 절차의 exact tracked subject를 사용한다.
2. current route에서 T1/T2 locator를 읽고 외부 파일 존재·hash·subject·line provenance를 확인한다. §4.2의 해시는 planning snapshot이지 미래 input 고정 승인값이 아니다.
3. 초기 ledger의 key를 case-sensitive `(FullType, fact identity)`로 둔다. initial selected, Menu KO/EN observed, missing, current body/silent, approved absence, empty-core를 별도 domain으로 기록한다. T1에서 넘겨받은 `unverified_without_independent_consumer_evidence`의 exact initial set과 authority/subject ref도 동결하여 final status disposition의 denominator로 사용한다.
4. 기존 T3의 raw consumer 관측이 relevant source/data/lookup/harness/config identity와 결속되어 있고 필요한 per-row 정보를 포함하면 baseline으로 재사용한다. count나 요약 보고만으로 actual observation을 대신하지 않는다. 자료가 없거나 관련 identity가 달라졌을 때만 기존 Lua Menu 경로로 bounded baseline 관측을 한 번 수행한다. 필요한 정보는 KO/EN actual lookup / ViewModel availability / active index·module / exact key / payload identity와 lookup miss·미호출·load failure의 구분이다. baseline 확보만을 위해 Alt/runtime full suite를 재실행하지 않는다.
5. 12개에는 core ID, T1/T2 S2, `text_ko`, `primary_use`와 provenance, role/disposition, silent membership을 같이 기록한다. KO/EN complement가 같은 exact set인지 확인한다.
6. 현재 1,314/1,302/12와 다르면 delta를 설명하고 새 exact baseline을 결속한다. 동일 count만으로 기존 identity set을 상속하지 않는다.

**Validation:** duplicate pair 0, normalized-key join 0, selected/silent intersection exactness, current payload binding, KO observed fact mismatch 여부를 확인한다. identity를 확정할 수 없으면 영향 branch 진행을 멈추고 원인을 남긴다. EN observation만으로 provenance verified를 발행하지 않는다.

---

### Change 2 — Silence lineage와 surface-scope disposition (Phase 1)

**Purpose:** producer의 현재 결과와 기존 authority가 요구한 결과를 구분하고 P1의 branch를 정한다.

**Files:** `docs/DECISIONS.md`의 Layer 3/locale/T1 결정, role-realign contracts/proposal/approved candidate, current-install trace, exact historical evidence, owner producer, `layer3_renderer.lua`, T1 S2 audit.

**Implementation Notes:**

1. **Missing-policy early checkpoint:** `docs/iris_layer3_body_role_realignment_policy.md`의 현재 존재와 exact archive/history 회수 가능성, 회수 자료의 identity/freshness를 먼저 확인한다. 회수 불가이면 기존 ratified contracts와 successor decisions로 필요한 surface scope를 입증할 수 있는지 기록한다. 모두 부족하면 영향 row를 즉시 D로 남기고, 그 row의 mutation 설계나 adoption을 앞서 진행하지 않는다. 다른 row 및 EN public-record evidence 조사는 계속할 수 있다.
2. 각 target의 original decision → ratified contract → material readiness → body disposition → approved candidate → generation installation → later successor를 추적한다.
3. Menu body silence인지, Tooltip을 포함한 Layer 3 public disclosure silence인지, locale에 공통인지를 명시한다. `text_ko` omission과 core IDs / `primary_use` 유지의 의도를 각각 확인한다.
4. 현재 producer predicate 세 가지(Menu body, EN emission, Tooltip S2)를 existing approved rule과 대조한다. missing human policy link 또는 stale snapshot을 임의 정책으로 보충하지 않는다. C 후보는 §4.3의 `Base.Bleach` / `Base.Rope` 선례와 실제 source/approval/material 경계를 비교하되 target별 독립 근거를 요구한다.
5. **Branch A Philosophy 대조:** Menu-specific silence permission 확인과 별개로, 최종 Menu-silent / Tooltip-present 상태를 “Iris 메뉴는 Iris 툴팁보다 상세한 정보를 제공한다”, same-fact/non-contradiction, 근거 부족 시 침묵의 세 원칙과 함께 대조한다. disposition record에 exact target, 실제 비교한 Menu/Tooltip 정보 범위, Philosophy 및 existing authority의 인용 위치/identity, 허용 근거와 대조 결론 또는 충돌·미결정 이유를 남긴다. Menu의 무관한 다른 정보가 많다는 일반론이나 coverage-difference 원칙만으로 대조를 대신하지 않는다. sealed decision과 Philosophy가 충돌하면 Philosophy를 우선하며, 상위 원칙과의 정합성을 입증하지 못한 A 후보는 A로 닫지 않는다. 이 확인 자체가 B/C를 자동 선택하지는 않는다.
6. 동일 rule과 Philosophy 대조가 exact 12개 모두에 적용된다는 근거가 있을 때만 공통 disposition한다. 원인이 다르면 subgroup으로 분리하고 각각 authority ref를 남긴다.

| Branch | 필요한 근거 | 결과 |
|---|---|---|
| A — legitimate surface difference | Menu-specific silence와 Tooltip S2 공개를 실제로 허용하는 existing authority 및 최종 상태의 Philosophy depth-ordering 정합성 | 근거와 대조 결론을 기록한 뒤 Menu silent / S2 present 유지; relation evidence만 보완 |
| B — Tooltip eligibility defect | 기존 public silence scope에 Tooltip S2도 포함 | upstream에서 S2 emission 생략; fact identity 자체는 보존 |
| C — Menu omission defect | 기존 authority가 Menu public display를 요구하며 허용된 existing material이 존재 | §4.4 locale precondition 해소 뒤 Menu producer/generation 최소 수정 |
| D — authority insufficient | scope 또는 exact authority binding이 부족/충돌 | 해당 row mutation 없음; unresolved와 필요한 authority/evidence 기록 |

**Validation:** `silent` 이름, general coverage difference, `primary_use` 존재, Tooltip 문장 존재만으로 branch를 선택한 사례 0. missing-policy checkpoint 결과와 모든 target의 scope·owner·successor 여부·근거 또는 unresolved 이유가 있어야 한다. Branch A는 Philosophy depth-ordering 대조 결과와 인용 위치가 없거나 정합성이 미해결이면 채택하지 않는다. 별도 ratification 의무는 §4.4의 미결정을 숨기지 않고 적용 authority에 따라 처리한다.

---

### Change 3 — 선택된 branch의 최소 upstream correction (Phase 2)

**Purpose:** P1 disposition만 반영하고 authority·runtime 역할을 넓히지 않는다.

**Files:** Branch A/D는 evidence/comparator만; B는 owner producer·Layer 3 input contract·T1 audit와 관련 focused family; C는 approved candidate·기존 generation/EN producer와 pointer 경로.

**Implementation Notes:**

- **A:** Change 2의 authority와 Philosophy 대조가 닫힌 경우에만 적용하고 product bytes를 바꾸지 않는다. comparator가 approved Menu silence를 source missing으로 오판하는 부분만 해당 authority scope에 맞춘다. legitimate silence를 `verified record`로 세지 않는다.
- **B:** `fact exists`와 `S2 emitted`를 구분하는 approved display disposition을 기존 owner/input 경로에 반영한다. 현재 T1은 core ID가 있는 row의 `tooltip_eligibility != eligible`을 correction으로 처리하므로 flag 변경만으로 끝내지 않는다. exact fact를 유지한 채 authority-backed display omission을 소비하도록 필요한 계약과 audit를 함께 보완하고 malformed/missing/locale defect는 계속 correction으로 남긴다. 현재 absence는 generation row와 충돌하므로 12개를 175 `absence_entries`에 넣거나 core ID를 삭제하여 absence를 위조하지 않는다. 새 field/reason이 꼭 필요하면 owner 계약의 최소 승인 successor로만 도입한다.
- **C:** 이미 승인된 Menu public material과 locale surface/producer path만 사용한다. Tooltip owner 문자열을 Menu의 source authority로 복사하지 않는다. approved KO가 있어도 approved EN material이 없어 신규 번역이 필요한 target은 §4.4에 따라 이 범위에서 C를 실행·채택하지 않고 blocked / unresolved로 남긴다. EN record 미생성만으로 material 부재를 단정하지 않는다. `primary_use`에서 새 Menu prose를 만드는 것도 금지한다. §4.3의 `Base.Bleach` / `Base.Rope` 선례는 evidence 기준의 참고이며 이번 target의 신규 fact 작성이나 자동 public 전환을 허용하지 않는다. 허용된 material이 있는 경우 facts/readiness/approved candidate의 실제 결함 경계만 고친 뒤 existing complete-generation·locale projection 경로를 사용한다.
- **C 한정 개정(사용자 최종 편집 지시, 2026-08-30):** 이번 exact 12개는 `primary_use`를 의미의 중심으로 유지하고, 채택된 `special_context`의 대상·상황·작업 디테일을 자연스럽게 녹여 KO·EN 일반 Menu 설명을 다듬는다. 이는 두 원문의 기계적 연결이나 context로 기본 용도를 덮어쓰는 작업이 아니다. 기본 의미와 세부 정보는 모두 보존하되 중복 표현은 정리하는 bounded 문장 편집을 허용한다. 위 재작성/primary-use 기반 prose 금지 및 item-wide review hold에 대한 이번 target 범위 한정 successor이며 새 용도·기능·게임 사실·추천·평가는 추가하지 않는다. 기존 양언어 문구를 바탕으로 같은 통합 의미를 편집하고, 원본 field/provenance/실패 이력을 보존한다. 별도 source 검증 미완료 때문에 채택된 내용을 다시 보류하거나 같은 콘텐츠 승인을 재요청하지 않는다. 사용자 콘텐츠 채택/편집을 independent game-source 검증으로 기록하지 않는다. 통합 문장 뒤에 context를 재첨부하지 않으며 S2의 core·문장은 그대로다. 다른 데이터의 검증 원칙이나 `special_context` 전역 schema는 변경하지 않는다.
- **D:** current behavior를 유지하며 P2에서 독립적으로 조사 가능한 기존 public record는 계속 조사한다. D row를 denominator에서 제거하지 않는다.
- 모든 branch에서 `if FullType in special12` 또는 `if MenuHasNoText then hideTooltip` 같은 runtime 예외는 만들지 않는다. T2 Lua도 손으로 patch하지 않는다.

**Validation:** target actual delta가 disposition과 일치하고 신규 user-facing 문장 0, runtime eligibility 예외 0, fact identity 훼손 0이어야 한다. B의 정상 omission / malformed correction 구분, C의 approved material·KO/EN boundary, 기존 정상 1,302개 보존을 검증한다. authority 또는 필요한 locale material이 부족하면 해당 mutation을 채택하지 않는다.

---

### Change 4 — Actual Menu EN record와 approved fact의 독립 연결 (Phase 3)

**Purpose:** EN observation과 provenance 사이의 끊긴 link를 기존 생산 경로에서 닫는다.

**Files:** `build_layer3_english_localization.py`, current facts / approved candidate / descriptor, EN Index/chunks, 기존 generation/producer evidence, T3 Menu observation 및 `menu_relations`.

**Implementation Notes:**

1. **Actual record:** final-required EN 각 row에서 exact FullType, active index entry, selected module/chunk, lookup key, actual payload identity와 consumer path를 확보한다. index 범위만 겹치거나 inactive chunk에 존재하는 것은 consumption evidence가 아니다.
2. **Existing direct evidence 우선:** generation/input manifest, producer implementation 또는 installed wheel identity, run receipt, output identity와 source/fact binding을 조사한다. current KO descriptor는 EN output을 열거하지 않으므로 그 파일 하나를 EN receipt로 취급하지 않는다.
3. **Deterministic reconstruction:** direct evidence가 부족한 경우에만 exact approved facts/candidate, source-bound role IDs, 기존 번역 material과 exact producer/serializer를 §4.5의 격리 output에서 실행해 actual Index/chunk bytes와 대조한다. 가능한 한 P1 correction 뒤 final input으로 한 번 수행한다. 동일 producer/input/output 결속의 성공한 replay는 재사용하며, 별도 existing determinism 의무가 없다면 replay 자체의 A/B·comparator를 추가하지 않는다. producer의 `_current_projection` identity 검사를 우회하지 않는다. `_write_runtime`은 output directory를 삭제 후 생성하므로 live `Layer3English`에 replay하지 않고 검증한 새 전용 빈 leaf만 사용한다. `main()`은 locale와 Tooltip owner output을 함께 쓰므로 read-only evidence 조사 목적으로 live checkout에서 호출하지 않는다.
4. **Fact binding:** producer가 실제 사용한 item/field (`primary_use` 등)를 approved source-bound role fact까지 연결하고 current generation의 core fact와 대조한다. Menu body의 context/acquisition 추가 깊이는 별도 보존한다. hash 일치만으로 입력의 승인 여부를 증명하지 않는다.
5. **최소 augmentation:** 앞 경로로도 부족한 link만 existing producer/output evidence 또는 test-local admission 경로에 추가한다. 필요한 내용은 input identity, producer identity, locale, FullType, output record/module identity와 source fact relation이다. runtime payload shape 변경이나 새 provenance registry를 기본값으로 만들지 않는다.
6. **Comparator 연결:** independently validated Menu trace에서만 현재 `en_identity_evidence`에 필요한 relation을 얻는다. tuple만 받아 provenance 검증을 끝냈다고 하지 않는다. 현 CLI의 빈 evidence를 실제 증거 경로에 연결하고, 증거가 없으면 명시적으로 missing을 유지한다. Tooltip manifest는 이 단계 뒤 exact fact comparison에만 사용한다.
7. historical original-run provenance와 current deterministic derivability 중 어떤 방법을 사용했는지 row 또는 bundle evidence에 적는다. 재현을 과거 receipt 발급으로 표현하지 않는다.

**Validation:** positive chain 전체가 닫혀야 sufficient relation이다. same FullType/string, key-set 일치, Tooltip ID 자기 참조, 잘못된 fact·producer input·output hash·generation·module, stale chunk, missing evidence는 모두 verified가 아니어야 한다. synthetic fixture의 positive case를 actual EN evidence로 제출하지 않는다.

---

### Change 5 — 실제 영향에 따른 successor 전파 (Phase 4)

**Purpose:** 변경되지 않은 T1/T2를 재생성하지 않으면서 current artifact와 evidence의 세대를 일치시킨다.

**Files:** 변경 branch의 owner output/contracts, external T1/T2 roots, Menu generation/pointer/EN output, product Tooltip Lua, T3 wrapper admission, current route.

**Implementation Notes:**

| 실제 변경 | 필요한 전파 | 보존 |
|---|---|---|
| A 또는 evidence-only | relation/evidence successor만 | Menu / owner / T1 / T2 / product bytes |
| EN provenance metadata-only | producer/input/output evidence 또는 validator의 bounded 보완 | EN bytes가 같으면 Menu payload와 T1/T2 재생성 없음 |
| B: S2 selection/visibility 변경 | approved owner/input → strict T1 successor → deterministic T2 successor → byte-preserving T3 product copy → admission hash/locator | support 2,280, S1/S3/S4 identity·text·selection, target 외 S2 |
| C: Menu만 변경, S2 unchanged | approved candidate → Menu generation successor → EN output → current pointer 및 final relation binding | T1/T2 content가 동일하면 재생성 없음 |
| B/C 조합 또는 추가 S2 영향 | 실제 dependency delta에 해당하는 경로만 실행 | unrelated producer/output/contract |

Menu generation만 바뀌어도 current generation을 참조하는 owner `authority_ref`와 관련 contract binding의 stale 여부를 확인한다. 필요한 metadata rebind와 semantic/static content 변경을 구분한다. **T1/T2 unchanged는 파일 hash와 selected/surface 비교에 근거하여 주장**하며, old handoff를 새 generation의 production receipt라고 표현하지 않는다. final Menu provenance를 final current generation에 별도 결속할 수 없으면 unchanged 주장을 근거로 gap을 덮지 않는다.

T2 successor가 생기면 기존 final root를 덮어쓰지 않는다. 현 wrapper의 `EXPECTED_SHA256`, hard-coded selected count/pair hash 및 in-memory fixture assumption도 admitted successor와 initial baseline의 역할을 구분하여 갱신한다. 고정 검사를 삭제하거나 observed success rows에서 expected set을 역산하여 통과시키지 않는다.

Branch B의 S2 omission은 T2의 sealed result trace도 바꾼다. predecessor의 0/1/2/3/4줄 분포 `367 / 825 / 895 / 137 / 56`을 보존하고, successor manifest에서 다시 계산한 분포, exact affected FullType별 before/after row count·slot vector·S2 fact/disposition, predecessor/successor manifest identity를 additive trace로 남긴다. mixed branch에서는 실제 B subset만 사용하며 “12개가 줄었음”이라는 산술만으로 successor 분포를 추정하지 않는다. unchanged T2 branch는 분포와 exact per-item rows 모두 unchanged임을 확인한다.

**Validation:** expected/actual changed set 일치, unrelated output delta 0, selected facts·slot provenance 보존, old T2 product copy와 stale Menu pointer/evidence 혼용 0. B에서 S2가 생략되면 row compaction은 바뀔 수 있으나 S1/S3/S4 내용과 identity는 바뀌지 않아야 한다. 각 B row의 줄 수는 정확히 1 감소하고 그 전이의 집계가 successor 0~4줄 분포와 일치하며 합계 support 2,280을 보존해야 한다. chunk boundary 이동으로 정상 row의 module path가 달라지면 semantic/text invariance와 physical routing delta를 구분해 기록한다.

---

### Change 6 — Whole relation re-audit와 non-target preservation (Phase 5)

**Purpose:** 초기 전체 universe를 보존한 상태에서 최종 expected/actual 결과를 판정한다.

**Files:** baseline/disposition/EN trace, final Menu/Tooltip 산출물, 기존 Lua Menu harness와 Python comparator.

**Implementation Notes:**

- ledger는 initial selected 1,314개를 유지한다. final S2 selected set, Menu KO required set, Menu EN required set, legitimate silence set은 disposition으로부터 각각 도출한다.
- 각 row에 initial fact, final S2 visibility/fact, Menu KO/EN expected/actual visibility, actual record relation, authority ref와 evidence method를 기록한다.
- A라면 초기 12개는 approved silence와 S2 present의 relation으로 남고, B라면 core fact 보존과 S2 omission을 함께 남긴다. C라면 복구된 KO/EN record 모두 필수 관계에 포함한다. mixed branch이면 exact subgroup별로 적용한다.
- report에서는 `verified record`, `legitimate silence`, `not applicable`, `evidence missing`, `identity mismatch`, `unresolved`의 의미를 구별한다. 이는 report-level 설명이며 ecosystem-wide enum/schema 확장이 아니다.
- legitimate silence 또는 not applicable은 final authority로만 부여한다. locale missing, load failure, unknown scope, failed observation은 대체 사유가 아니다.
- 초기 정상 1,302개는 Menu KO/EN text·fact·locale selection과 Tooltip S2 identity/surface의 preservation target이다. 추가 public body와 silent 33의 나머지, absence 175, empty-core 791도 범위 밖 delta가 없는지 확인한다.
- support exact FullType, Classification, Layer 4 selected identity/source 및 Recipe/Right-click distribution을 보존한다. 대소문자가 다른 `Base.LemonGrass` / `Base.Lemongrass`를 합치지 않는다.
- final consumer observation, relation 비교, non-target preservation과 inherited status reconciliation은 같은 final input을 소비하는 기존 wrapper의 한 실행에 묶는다. Phase 5와 Phase 6의 이름이 다르다는 이유로 동일 관측을 두 번 수행하지 않는다. baseline 관측은 final 관련 source/data/consumer identity까지 동일하고 필요한 trace가 완전한 경우에만 final 비교 입력으로 재사용한다.

**Inherited evidence-gap status disposition:** T1에서 넘겨받은 `unverified_without_independent_consumer_evidence`의 exact initial set을 아래 세 집합으로 빠짐없이 대조한다. 별도 registry/schema가 아니라 같은 final relation report의 status 처분 항목으로 기록한다.

| report 집합 | 의미와 필요한 근거 | 완료 판정 |
|---|---|---|
| `resolved exact set` | 해당 pair의 final-required Menu KO/EN actual record와 independent producer/input/fact relation이 닫혀, 이번 evidence로 inherited gap을 해소한 집합 | 각 pair를 supporting record/evidence와 연결. historical T1 판정을 소급 PASS로 바꾸지는 않음 |
| `retained exact set` | final authority가 legitimate silence / not applicable을 입증하여 record verification 의무가 없지만, 실제 Menu record의 independent evidence가 생긴 것은 아니므로 inherited unverified 표시를 verified로 승격하지 않는 집합 | scope disposition은 닫혔고 record verification claim은 하지 않음을 명시. authority ref·최종 비필수 사유·관측 결과가 필요 |
| `unresolved exact set` | final-required record evidence 부족, mismatch, authority/Philosophy scope 미해결 또는 status 처분 자체 미확정인 집합 | T3-D1 complete 불가. 부족한 link와 후속 담당 범위를 남김 |

집합 key는 initial `(exact FullType, exact fact identity)`다. 세 집합은 서로 겹치지 않고 합집합이 초기 1,314 pair 전체와 일치해야 한다. count뿐 아니라 exact member 목록과 subject-bound identity를 남긴다. 각 pair에서 final visibility / required 여부 / relation result / status 처분의 대응을 확인하며, 이 구분을 새로운 ecosystem-wide status enum으로 만들지 않는다. 미해결 때문에 기술적으로 원래 token이 남는 row는 보고서의 `retained`가 아니라 `unresolved`에 둔다.

`retained`는 missing evidence를 우회하는 경로가 아니다. record verification을 요구하는 pair는 retained에 넣을 수 없고, public record가 양 locale에서 필요하면 양쪽이 닫혀야 resolved다. A/B에서 Menu silence가 정당화된 row는 relation scope가 닫혀도 “independent Menu record verified”로 세지 않는다. 따라서 complete 시에도 resolved가 초기 1,314 전체가 아닐 수 있지만, 그 차이는 exact retained set의 authority-backed 비필수 scope로 모두 설명되어야 한다. 현재 ledger를 바꾸지 않은 채 legitimate silence를 단순 unresolved 해소로 합산하지 않는다.

**Validation:** final-required 관계에 missing/mismatch/unresolved가 하나라도 남으면 complete 금지. inherited status의 세 exact set이 누락·중복 없이 initial ledger와 reconciliation되어야 하고, required pair의 retained 편입은 0이어야 한다. initial ledger의 missing/extra pair 0, final expected/actual visibility mismatch 0, target 외 semantic/text delta 0을 요구한다. 1,302 count만 유지된 것을 set/identity 보존으로 보고하지 않는다.

---

### Change 7 — Focused validation과 조건부 canonical gate (Phase 6)

**Purpose:** 실제 변경 범위의 계약과 evidence admission을 검증하고 ceiling을 명시한다.

**Files:** 기존 T3 wrapper/harness, 영향 있는 T1/T2/Layer 3 test family, `Iris/build/ENTRYPOINTS.md`, current validation binding과 receipt-bound full-gate owner.

**Implementation Notes:** §7의 branch matrix와 최소 실행 규칙을 적용한다. 새 test file / top-level test function / regular gate 추가는 기본 0개다. 실제 변경된 판정 경계만 기존 parameterized fixture에 통합한다. 단순 implementation mirror나 고정 target count만 확인하는 test로 authority/provenance 검증을 대체하지 않는다. 기존 구조에서 필요한 성질을 검증할 수 없는 경우에만 이유를 설명하고 가장 작은 기존 harness 보완을 사용하며, 숫자를 맞추려고 필요한 검증을 생략하지 않는다.

source correction이 끝난 exact subject에 필요한 최종 검증을 수행한다. unchanged 입력에 대한 duplicate generation/run은 피하되 existing T1/T2 finalizer와 canonical owner가 요구하는 Run A/B 및 comparator를 단일 임의 실행으로 축소하지 않는다.

**Validation:** 적용 대상으로 확정된 정확한 command의 exit `0`만 PASS. dependency·Lua·환경·receipt 부족은 BLOCKED이며 skip을 PASS로 쓰지 않는다. command, subject/input binding, exit code, evidence locator, 미검증 영역을 함께 기록한다.

---

### Change 8 — T3-D1 closeout과 original T3 handoff (Phase 7)

**Purpose:** 닫힌 Layer 3 관계와 아직 남은 integration 검증을 분리한다.

**Files:** 본 계획의 후속 실행 기록, 기존 T3 계획, 필요시 current route / ROADMAP / ARCHITECTURE의 bounded successor 기록.

**Implementation Notes:** closeout에 initial selected set/12 target, authority disposition/branch와 Branch A Philosophy 대조, KO/EN final relation, provenance method, actual changed set, 1,302 preservation, final Menu pointer/generation, T1/T2 유지 또는 successor, T3 input binding, validation ceiling, original T3 remaining scope를 포함한다. Branch B이면 T2 predecessor/successor의 0~4줄 분포와 exact row-count transition도 연결한다.

`unverified_without_independent_consumer_evidence`에 대해서는 Change 6의 **resolved exact set / retained exact set / unresolved exact set**, initial set과의 reconciliation 및 각 집합의 evidence/authority ref를 closeout에 반드시 포함한다. final-required relation closure와 initial 1,314 전체 independent record verification을 같은 주장으로 쓰지 않는다. retained가 있다면 무엇이 유지되고 왜 record verification 의무가 없는지 exact scope로 인계한다.

**Original T3 acceptance 동기화는 handoff의 일부다.** 기존 T3 계획에 다음을 additive successor 항목으로 반영한다. 초기 1,314 pair와 당시 실패/미검증 결과는 역사적 baseline으로 유지하고, final S2 selected set, Menu KO/EN required set, authority-backed silence/non-required set 및 resolved/retained/unresolved 처분을 기존 final relation 결과에 연결한다. exact input/subject, Menu readpoint, T1/T2 유지 또는 successor locator, EN evidence method와 comparator의 expected scope를 함께 명시한다. 같은 목록을 새 파일에 중복 발행할 필요는 없다.

A/B 또는 mixed disposition으로 필수 record 범위가 바뀌면 original T3의 “초기 1,314 모두 KO/EN record 필수” 가정을 그 승인된 final scope로 갱신해야 한다. final scope가 그대로라면 기존 의무 유지라고 명시한다. 관측에 성공한 행으로 expected set을 축소하거나 required gap을 retained로 바꾸지 않는다. 이 동기화가 빠져 original T3와 D1의 acceptance가 모순된 상태에서는 handoff-ready를 주장하지 않는다. 이는 D1 안의 bounded 인계 작업이며 별도 T3-D2 문제나 새 승인·봉인 체계를 만들 사유가 아니다.

이 closeout은 이번 successor evidence의 처분 기록이며, `docs/DECISIONS.md` / `docs/ARCHITECTURE.md`의 sealed T1 기록이나 원래 handoff를 자동 갱신하지 않는다. 실제 authority 문서의 current-status 갱신이 필요하면 변경 필요 여부·대상·exact successor scope를 disclose하고 기존 절차에 따라 별도 additive amendment로 처리한다. historical unverified 판정은 당시 상태로 보존한다. EN method가 current deterministic derivability이면 closeout과 T3 handoff에서도 같은 wording을 유지하며 historical original-run provenance로 강화하지 않는다.

T2 unchanged이면 기존 final bundle을, changed이면 검증된 successor만 T3 static input으로 전달한다. Menu가 바뀌면 final current pointer와 relation readpoint를 같이 전달한다. T3의 `partial` 및 `runtime_adopted=false`를 T3-D1 closeout만으로 변경하지 않는다.

**Validation:** §12의 성공 조건과 각 claim의 evidence를 대조한다. inherited status exact-set 처분 누락, required unresolved 또는 Branch A Philosophy 대조 미해결이면 complete로 닫지 않는다. sealed record의 자동 rewrite와 provenance wording 확대가 없는지 확인한다. 실패/blocked predecessor를 지우거나 새 attempt의 PASS로 바꿔 쓰지 않는다. code 구현만 끝났거나 관계 증거가 미완료이면 그에 맞는 상태로 종료한다.

---

## 7. Validation Plan

### Automated Validation

검증 성질은 아래 **세 논리 그룹**으로 묶는다. 그룹은 test file/function 또는 별도 command 수를 뜻하지 않는다. 기존 wrapper·parameterized family에서 함께 확인하고 새 test file / top-level function은 기본 0개로 유지한다. 전체 exact-set 비교는 유지하되 FullType마다 별도 test나 proof를 만들지 않는다.

| 그룹 | 같은 실행/fixture에 통합할 성질 |
|---|---|
| 표시 처분·범위 | 실제 채택한 display rule, initial ledger와 final-required scope 구분, inherited resolved/retained/unresolved의 exact-set reconciliation. Branch A의 Philosophy 판단은 Manual Validation에서 한 번 수행 |
| EN 증거·소비 관계 | actual KO/EN consumer, EN output→producer→approved input→fact binding, positive chain과 변경된 admission의 실패 경계. baseline/final 자료가 재사용 조건을 충족하면 중복 관측 없음 |
| 변경 전파·보존 | 초기 정상 1,302개와 scope 밖 identity/text 보존, 실제 변경 branch의 successor·product/pointer binding 및 stale-copy 배제. 동일 final relation 실행과 산출물 비교에 결합 |

**최소 실행 규칙:**

1. admission·필수 입력 확인과 branch를 결정하는 읽기 조사는 먼저 하되, 계획에 없는 중간 회귀 테스트는 하지 않는다. 구현·필요한 producer 수정이 끝난 뒤 영향 있는 기존 focused 사례와 final relation을 마지막 검증 구간에 모은다. producer/build 실행은 필요한 산출물 생산이며 confidence만을 위한 반복 실행은 하지 않는다.
2. 기본 실행은 final Menu relation 1회와 실제 변경된 기존 fixture 사례 1회다. 같은 기존 command가 둘을 포함하면 1회로 합친다. Phase 5의 성공한 final relation을 Phase 6에서 반복하지 않는다. command 개수를 맞추기 위한 새 wrapper는 만들지 않는다.
3. baseline raw observation과 EN direct/replay evidence는 해당 source/input/output/consumer/config identity 및 필요한 trace가 일치할 때 재사용한다. upstream 또는 consumer가 달라졌으면 영향 있는 관측만 갱신한다. 구현 수정 전의 PASS나 요약 count를 새 exact subject의 검증으로 재사용하지 않는다.
4. 실제 수정·채택한 branch와 공통 admission 경계만 기존 parameter table에 추가한다. 미선택 branch를 시험하기 위한 별도 구현·generation·가상 successor는 만들지 않는다. 수동 authority 판단을 “설명 문자열이 존재함” 같은 test로 중복 인증하지 않는다.
5. 기존 canonical gate가 **동일 exact subject에서 동일 fixture/성질을 실제 실행하고 결과를 확인할 수 있으면**, 별도 standalone 실행과 중복하지 않는다. 포함되지 않은 actual Menu relation이나 branch 검증은 수행한다. gate는 한 번의 최종 검증 구간에 모으되, T1→T2 successor의 기존 선후 의무가 있으면 그 순서를 따른다. 필수 Run A/B·comparator·finalizer를 없애거나 새 subject에 predecessor PASS를 상속하지 않는다.
6. 실패 후에는 원인을 고친 뒤 영향 command만 재실행한다. 새 subject 때문에 기존 authority가 다시 요구하는 gate는 예외다. 동일 성공 입력을 confidence 목적으로 반복하거나 새 seal/receipt/manifest/census/proof를 추가하지 않는다. command·subject·exit·재사용 근거는 기존 실행 기록에 합쳐 적는다.
7. 실행 중 상태는 최대 60초 간격으로 확인하고 기존 timeout을 유지한다. 출력·진행 정체, 무한 반복 또는 비정상 장기 실행이면 중단하여 실패/차단으로 기록한다. 원인 수정 없이 자동 재시도하지 않는다.

| 조건 | 수행 범위 | PASS 해석 한계 |
|---|---|---|
| 완료를 주장하는 branch | 세 그룹 중 해당 claim에 필요한 성질을 기존 final relation/fixture에 통합 | authority 부족 row는 unresolved로 남김; required gap의 retained 처리 금지 |
| A, evidence-only | 재사용 가능한 baseline/evidence를 우선하고 final relation 비교; A의 Philosophy 대조; unchanged byte/hash 확인 | output generation·T1/T2 재생성 불필요; missing comparison은 A closure 아님 |
| D | 확보된 자료와 부족한 authority를 기존 보고서에 명시. 독립적으로 수정 완료한 부분에만 해당 검증 적용 | D를 확인하려고 전체 suite/producer를 실행할 의무 없음; required D가 남으면 complete 불가 |
| B | 영향 T1 contract/audit focused, strict handoff, T2 deterministic Run A/B/finalization, row-count distribution successor trace, product admission, Lua syntax | T1/T2 성공을 actual PZ 성공으로 확대 금지 |
| C | approved input binding, relevant generation determinism, KO/EN projection·pointer 일치, Lua syntax, final consumer observation | Menu 복구를 번역 품질 또는 package acceptance로 확대 금지 |
| deterministic EN replay | direct evidence가 부족한 경우 final producer/input으로 1회 reconstruction 후 actual Index/chunk/record bytes 대조. 기존 별도 determinism 의무가 있으면 준수 | current derivability이며 historical receipt가 아님 |
| execution-relevant source/protected result 변경 | current authority에 따른 corrected exact-subject canonical full gate | focused PASS나 predecessor PASS로 대체 불가 |

기존 T3 wrapper의 `menu` 모드를 D1의 기본 관측 경로로 사용한다. 다음은 기존 mode의 호출 형태이며 **이 호출만으로 final relation PASS를 주장하지 않는다.**

```powershell
uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py menu
```

최종 실행은 explicit admitted T2 manifest를 같은 wrapper의 입력으로 제공하고 Change 4/6의 **독립 검증된 actual EN evidence**까지 연결한 Menu relation 호출로 한 번 수행한다. 현재 caller의 빈 `en_identity_evidence={}`를 그대로 사용하거나 관측-only 성공을 relation 성공으로 세지 않는다. 필요한 evidence admission 연결을 구현한 뒤 정확한 최종 command/input을 기존 실행 기록에 남기며, human command가 바뀌면 `Iris/build/ENTRYPOINTS.md`도 필요한 범위만 갱신한다.

`full`은 Alt reader/lifecycle 등 그 검증 범위에 실제 영향이 있거나 기존 authority가 명시적으로 요구할 때만 실행한다. D1의 provenance/comparator 보완만으로 `full`을 추가하지 않는다. B의 product/admission 변경도 기존 좁은 payload 검사로 검증 가능한 범위는 그 경로를 사용하며, 본래 T3의 최종 runtime 검증 의무는 T3에 보존한다. `replacement`는 이번에 legacy 삭제/adapter 변경을 하지 않으므로 실행하지 않는다. 서로 다른 mode를 전부 한 번씩 돌리는 것을 기본 절차로 삼지 않는다.

Lua source 또는 generated Lua가 변경되는 branch에서는 repository 지정 명령을 수행한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

T1/T2 focused 및 build/finalize command는 `Iris/build/ENTRYPOINTS.md`의 해당 section을 사용한다. 실행 Python은 `uv run python ...` 또는 그 문서의 `uv run --project ... python ...` 경로를 사용한다. Java/Gradle·JS/TS 변경이 없는 본 scope에 `gradlew test` / `pnpm biome check .`를 무관하게 추가하지 않는다.

**Canonical 적용 판정:** 통합 로드맵은 source mutation 후 canonical gate를 별도 채택 항목으로 남겼다. 그러나 현재 `docs/DECISIONS.md`의 clean-checkout 계약은 execution-relevant source 또는 protected result correction 시 corrected exact subject 재검증을 요구한다. 따라서 이 계획은 해당 surface를 실제 수정하는 branch에 기존 gate 의무를 적용한다. 이는 로드맵의 optional 항목을 근거 없이 의무화한 것이 아니라 current repository authority 적용이다. evidence-only의 결과 기록과 docs-only 작성만으로 새 source-validation subject 또는 불필요한 full-gate 의무를 만들지 않는다.

gate membership, environment, work/result root, receipt, Run A/B와 deterministic comparison은 `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1` 및 `invoke_deterministic_compare.ps1`가 소유한다. human invocation은 ENTRYPOINTS의 `iris-tooling ... validate full ...`을 따르고 필요한 external 작업/output은 §4.5에 한정한다. T1/T2 finalizer의 이미 존재하는 canonical evidence 요구도 생략하지 않는다. 새 gate wrapper나 T3-D1 전용 exemption을 만들지 않는다.

**최소 회귀 사례:** 아래 성질 중 실제 수정한 판정 경계만 기존 positive/negative table에 통합한다. 기존 동일 사례가 있으면 재사용하며 field별 test function, 전체 조합의 Cartesian product 또는 사용하지 않는 branch별 suite는 추가하지 않는다.

- 공통 relation/admission: 독립 actual trace의 성공 사례와 evidence 없음·자기대조·잘못된 fact 또는 binding의 실패 사례. input/output/module/generation처럼 서로 다른 검증 경계를 수정했다면 해당 실패 변형을 같은 table에 넣고, 한 종류의 실패만으로 모든 경계가 검증됐다고 주장하지 않는다.
- scope/status 판정: authority 없는 silence나 required missing을 성공 처리하지 않으며, initial ledger 누락·중복과 required pair의 retained 편입을 거부한다. 실제 legitimate silence는 record verified가 아니다. Branch A의 Philosophy 대조와 C의 승인 material 존재 판정은 Manual Validation에서 확인하고 별도 문서-existence test를 만들지 않는다.
- 실제 B/C 전파: B를 채택하면 approved omission과 malformed correction 구분, exact row-count/slot 전이 및 stale product를 확인한다. C를 채택하면 approved KO/EN input과 generation/pointer/evidence binding을 확인한다. 변경되지 않은 쪽의 producer를 시험용으로 재생성하지 않는다. non-target 보존은 동일 final 비교에 묶는다.

### Manual Validation

- missing-policy early checkpoint, authority scope, common-rule 적용과 subgroup 분리, 기존 owner 승인 범위, Branch C의 approved locale material을 문서·코드·record로 대조한다. `Base.Bleach` / `Base.Rope` 선례를 target의 자동 승인으로 사용하지 않았는지 확인한다.
- Branch A 최종 상태를 Philosophy의 depth-ordering·same-fact·silence 원칙과 명시적으로 대조하고, 비교한 정보 범위·authority 인용 위치·결론을 검토한다. 단순 token/문자열 test는 이 판단을 대신하지 않는다.
- exact 12개 before/after와 초기 정상 1,302개 preservation report를 검토한다. 문자열 자체를 fact join authority로 쓰지 않는다.
- inherited `unverified_without_independent_consumer_evidence`의 resolved / retained / unresolved exact set과 initial ledger의 일치, final required relation과의 대응, sealed authority 문서 변경 여부·별도 절차를 검토한다.
- EN trace가 Tooltip 자기 증거가 아닌지, replay evidence를 historical provenance로 과장하지 않았는지 확인한다.
- final pointer/manifest/product copy와 report가 같은 subject를 가리키는지 확인하고 original T3로 넘길 locator를 정리한다.

위 검토는 기존 disposition/final report에 한 번 합쳐 기록한다. 동일 common rule이 12개 모두에 적용되면 exact 적용 범위를 하나로 확인하며, 서로 다른 subgroup에만 추가 판단을 남긴다. 항목별 승인 문서·수동 검토 receipt나 반복 review round를 만들지 않는다. original T3 acceptance가 Change 8의 final-required scope를 실제로 채택했는지도 이 인계 검토에 포함한다.

이번 T3-D1에서는 실제 PZ, package/install, Alt interaction, clipping/wrapping 등의 manual validation을 수행하지 않는다.

### Validation Limits

closeout에서 `validated`, `out_of_scope`, `unvalidated_but_in_scope`를 분리한다.

- `validated`: 실제 수행하여 성공한 exact relation / authority-backed disposition 및 Branch A Philosophy 대조 / inherited status exact-set reconciliation / producer-output binding / preservation / 적용된 focused·canonical 결과만 포함. retained legitimate silence를 actual verified record에 포함하지 않음.
- `out_of_scope`: T3-D1의 정의된 완료 범위 밖인 package/install, actual loaded module/PZ, Alt·visual·font/UI-scale, multiplayer/soak/external-mod sweep, translation quality, full truth audit, RTC/DVF freeze/Publish/release.
- `unvalidated_but_in_scope`: required relation, source mutation 후 적용되는 gate, branch에 필요한 determinism·propagation 등 이 계획의 의무 중 미실행·실패·blocked인 항목. 비어 있지 않으면 해당 success claim을 하지 않으며 required closure를 complete로 닫지 않는다.

게임 내 visibility 영향은 의도된 동작 변경으로 disclose하되 여기서는 실제 게임에서 성공했다고 주장하지 않는다. original T3에서는 package/install/actual PZ/visual이 여전히 **in-scope 미검증**이다. T3-D1의 범위 제한으로 original T3 의무를 삭제하지 않는다.

이번 **계획서 작성의 검증**은 template 구조, 코드·계약·artifact readpoint 확인, 경로 및 diff 검토에 한정된다. runtime suite, producer replay, Lua syntax, canonical full gate를 실행한 것으로 기록하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

조건부로 중요하다. 기존 silence/public scope를 읽고, B에서는 Tooltip display eligibility/omission 계약, C에서는 approved Menu production input을 만질 수 있다. producer/validator가 owner policy를 발명하지 않는다. 별도 ratification의 mandatory 여부는 §4.4에 남긴다.

### Runtime Behavior Surface

A/D는 현재 visibility 유지. B는 승인된 target의 S2 생략, C는 승인된 Menu KO/EN body 복구가 가능하다. runtime은 완성된 정적 output만 읽고 eligibility를 재판정하지 않는다. Alt behavior/layout는 보호 대상이다.

### Compatibility Surface

의도한 public API/SPI 변경 없음. exact FullType, Lua facade, explicit KO/EN, 2,280 support-key와 T2 0~4 rows shape를 유지한다. external mod / JVM 의존을 추가하지 않는다.

### Sealed Artifact Surface

branch에 따라 owner/contract, Menu generation, T1/T2 bundle과 product copy가 successor로 바뀔 수 있다. predecessor sealed hash·receipt·실패 기록은 보존하고 current locator만 필요한 범위에서 변경한다.

T1 inherited unverified status의 이번 evidence에 대한 exact-set 처분과 T2 row-distribution successor trace를 명시한다. final relation report가 sealed authority 문서의 기록을 자동 수정하거나 historical unverified 결과를 소급 해소하지 않는다.

### Public-Facing Output Surface

B/C에서는 표시 여부가 바뀔 수 있으므로 영향을 명시한다. 신규 문장·번역은 0이어야 한다. A의 evidence-only 변경을 public behavior correction이라고 보고하지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- `primary_use`나 silent token을 public authority로 오인할 위험: decision / surface scope / exact lineage를 분리해 확인한다.
- Menu-specific permission만으로 Branch A를 허용할 위험: 최종 상태의 Philosophy depth-ordering 대조를 함께 기록하고 상위 원칙 충돌을 unresolved로 남긴다.
- EN provenance가 새 framework로 커질 위험: existing producer/receipt/replay를 우선하고 부족한 link만 보완한다.
- historical source path나 missing policy를 current authority로 오인할 위험: archive/history는 identity-bound evidence로만 읽고 installed owner와 current route를 확인한다.
- 승인된 fact가 있는 B row를 semantic absence로 바꿀 위험: fact identity와 display omission을 분리하고 175/791 domain을 보호한다.

### Runtime Risk

- upstream 수정 대신 Tooltip 예외로 숨길 위험: reader/Alt logic을 scope 밖 보호 경로로 둔다.
- live EN replay가 현재 chunk를 지울 위험: `_write_runtime`의 삭제 동작을 고려하여 검증된 external empty root에서만 재현한다.
- successor 이후 old payload/cache/locator 혼용 위험: final product hashes와 fresh-process consumer evidence를 결속한다. 실제 PZ cache/loaded module 검증은 T3에 남긴다.

### Compatibility Risk

- FullType 정규화로 별도 아이템을 병합할 위험: ordinal case-sensitive identity만 join에 사용한다.
- EN-only stale record 또는 KO fallback이 결함을 숨길 위험: actual renderer 경로 및 active index를 관측하고 locale fallback 0을 보존한다.
- chunk 재분할을 semantic change로 오해하거나 반대로 누락할 위험: module routing delta와 per-record text/fact preservation을 별도 기록한다.

### Regression Risk

- 12개 수정이 정상 1,302개와 scope 밖 Layer 3/Layer 4로 확산할 위험: initial exact sets 기준 comparator를 유지한다.
- comparator의 1,314/hash 하드코딩을 제거하며 denominator가 축소될 위험: initial ledger와 final selected/required sets를 별도 binding한다.
- final-required closure가 inherited 1,314 전체 verified로 오독될 위험: resolved / retained / unresolved exact sets와 그 근거를 인계하고 sealed 기록의 자동 갱신을 금지한다.
- D1이 승인된 final scope로 닫혔는데 original T3가 여전히 초기 1,314 전부의 record를 요구하는 위험: 기존 T3 계획의 acceptance/readpoint에 동일 successor scope를 additive 반영한 뒤 handoff한다. 실패 기록은 유지하고 새로운 denominator를 관측 성공 행에서 역산하지 않는다.
- synthetic positive fixture가 actual EN evidence로 승격될 위험: fixture result와 current producer/input/output trace를 분리한다.
- S2 변경 후 T2 Lua·admission hash·T1 metadata가 불일치할 위험: successor 전체 dependency를 검증한다.
- S2 생략 뒤 predecessor의 0~4줄 분포를 current 결과로 유지할 위험: exact per-item row transition과 successor 분포를 함께 재집계한다.
- 불필요한 반복 실행 / 테스트 파일 증가 위험: 기존 family와 owner command를 사용하고 affected branch만 실행한다.

---

## 10. Rollback Plan

1. authority scope를 정하지 못하면 해당 target의 current behavior를 유지하고 unresolved / blocked로 남긴다. 문서만 바꾸어 승인된 silence로 만들지 않는다.
2. B의 T1/T2 successor가 실패하면 candidate를 current T3 input으로 채택하지 않고 기존 bundle/product/admission을 유지한다. old T2를 수동 patch하지 않는다.
3. C의 generation/locale 검증이 실패하면 pointer 전환을 하지 않는다. 채택 후 회귀가 드러나면 승인된 복구 절차로 predecessor pointer와 그에 맞는 EN companion·binding을 함께 복구한다. Tooltip text를 Menu fallback으로 사용하지 않는다.
4. EN evidence가 부족하면 actual record는 보존하되 verified로 승격하지 않는다. missing/mismatch와 실패 원본을 유지한다.
5. expected/actual delta가 다르면 downstream adoption을 중지하고 이번 변경의 영향 파일만 복구한 뒤 affected validation을 수행한다. 시작부터 있던 사용자 변경을 복구 대상으로 포함하지 않는다.
6. 결과/receipt/attempt는 append-only successor로 보존한다. recursive cleanup, 전체 reset, old failure 덮어쓰기 또는 current generation의 in-place rewrite로 되돌리지 않는다.

---

## 11. Governance Constraints

- `Philosophy.md`의 정보·중립성·근거·침묵 원칙, “Iris 메뉴는 Iris 툴팁보다 상세한 정보를 제공한다”는 depth-ordering, Menu/Tooltip 두 표면, same-fact/non-contradiction, Alt 최대 4줄, 100% Lua를 함께 준수한다. Branch A도 이 원칙과 명시적으로 대조하며, sealed decision과 충돌하면 Philosophy를 우선한다.
- runtime/build-time 책임을 분리하고 Hub & Spoke·SPI 경계를 보존한다. Pulse가 Iris에 의존하거나 Spoke 간 직접 의존을 추가하지 않는다.
- exact authority와 prior authorization의 적용 범위를 확인한다. 이미 적용되는 승인은 불필요하게 재요청하지 않지만 historical owner approval을 다른 subject의 신규 policy 승인으로 재사용하지 않는다.
- additive amendment와 최소 diff를 우선한다. sealed predecessor·rejected candidate·FAIL/BLOCKED를 삭제하거나 성공으로 재작성하지 않는다.
- inherited `unverified_without_independent_consumer_evidence`의 exact-set 사후 처분은 필수 closeout disclosure다. 이는 `DECISIONS.md` / `ARCHITECTURE.md` sealed record의 자동 rewrite가 아니며, 실제 authority 문서 갱신은 exact successor scope를 disclose하고 기존 절차로 별도 처리한다.
- machine validation, independent consumer evidence, independent review, owner adoption/seal과 publication을 별도 axis로 둔다. Tooltip owner가 Menu consumer evidence를 스스로 발급하지 않는다.
- 로드맵의 세 미결정 사항은 계획만으로 승인하지 않는다. 보류된 reviewer-model gate나 별도 seal governance를 필수 조건으로 추가하지 않는다.
- public/authority/contract 변경은 필요한 최소 범위만 승인된 existing owner path에서 수행한다. Hash equality, fixture PASS, current producer behavior는 mutation authority가 아니다.
- required validation의 scope/membership를 편의를 위해 줄이지 않는다. tool/dependency 없음은 BLOCKED이며 exact command exit `0` 없는 PASS를 기록하지 않는다.
- 본 문서는 T3-D1 실행 계획이지 새 semantic authority / Registry / canonical validator / execution receipt가 아니다.

---

## 12. Expected Closeout State

목표는 stated ceiling 안에서 **`Iris Tooltip T3-D1 — Layer 3 Menu/Tooltip relation consistency complete`**다. 다음 조건이 모두 충족되어야 한다.

1. initial selected universe와 exact 12 target이 current subject와 결속되어 있다.
2. target별 existing silence/display scope와 A/B/C disposition이 근거로 확정되고 required D/unresolved가 남지 않는다. Branch A는 최종 상태와 Philosophy depth-ordering·same-fact·silence 원칙의 대조 결과 및 authority 인용 위치가 명시되고 정합성이 입증되어야 한다.
3. 필요한 B/C correction은 upstream의 허용된 existing material/path에서 완료됐으며 fact identity 훼손·새 user-facing text·runtime 예외가 없다.
   - 사용자 지정 bounded KO/EN 편집의 before/after와 기본 의미·채택된 디테일의 보존 및 단일 소비를 기록한다. 새 output 문장은 허용된 편집 결과이며 새로운 게임 사실의 추가/검증과 구별한다. 콘텐츠 채택을 재심사하지 않는다. `special_context` 전역 폐기는 success condition이 아니다.
4. final-required Menu KO record가 approved fact에, EN record가 actual consumer → output → producer → approved input → fact에 연결된다. Tooltip identity는 독립 연결 후 비교한다.
5. legitimate silence / verified record / not applicable / evidence missing / mismatch / unresolved가 구별되고, success rows만 남기는 denominator 축소가 없다.
6. 초기 정상 1,302개 및 support·Layer 2/4·absence 175·empty-core 791 등 scope 밖 data가 보존된다.
7. T1/T2 unchanged 주장은 실제 content/hash에 근거하고, S2 변경 시 validated T1/T2 successor 및 T3 product admission이 일치한다. Branch B의 predecessor/successor 0~4줄 분포와 exact row-count transition은 additive trace로 남는다.
8. Menu 변경 시 final pointer, EN output, producer/input binding과 relation evidence가 동일 current state를 가리킨다.
9. 적용된 필수 validation이 exact command exit `0`으로 완료되고 required `unvalidated_but_in_scope`가 없다.
10. closeout이 final locator·evidence method·changed set·validation ceiling과 original T3 remaining scope를 명시한다. 기존 T3 계획의 acceptance/readpoint가 같은 final S2 selected / Menu KO·EN required / authority-backed non-required scope를 채택하며, 초기 1,314 baseline과 당시 실패 기록은 보존한다. scope가 달라졌는데 원래 T3의 비교 의무가 갱신되지 않은 상태는 handoff-ready가 아니다.
11. inherited `unverified_without_independent_consumer_evidence`의 **resolved exact set / retained exact set / unresolved exact set**이 initial 1,314 pair를 누락·중복 없이 설명한다. retained는 authority-backed 비필수 scope에만 한정되고, unresolved는 0이어야 한다. resolved/retained를 합쳐 모든 pair의 independent Menu record가 verified라고 주장하지 않는다.
12. status 처분 자체가 `docs/DECISIONS.md` / `docs/ARCHITECTURE.md`의 sealed 기록을 자동 갱신하지 않음을 명시한다. 실제 authority 문서 변경이 필요하면 그 대상과 exact successor scope를 disclose하여 별도 절차로 처리하고 historical status를 보존한다.

required relation 또는 authority가 남으면 `partial` 또는 `blocked`, 구현만 끝나고 요구 검증이 남으면 `implemented_only`를 사용한다. 문서 작성 당시에는 branch와 EN evidence가 아직 해결되지 않았으므로 **이 문서 자체는 T3-D1 complete를 선언하지 않는다.**

원래 T3에 남기는 범위는 package identity, installation identity, actual loaded module, actual PZ load, Alt press/release, 대표 0~4 rows, KO/EN in-game behavior, wrapping/spacing/clipping/visual layout, failure isolation과 최종 T3 closeout이다. T3-D1을 닫은 뒤에도 이 검증이 끝나기 전 T3는 `partial`이다.

이 계획의 closeout은 전체 T3 완료, full Menu coverage equality, package/install/PZ/visual validation, translation quality, Layer 3 truth audit, RTC certification, DVF freeze, Publish PASS, release/Workshop readiness 또는 deployed를 뜻하지 않는다.

---

## 실행 기록 — 2026-08-30 / partial

### 범위와 현재 입력

실행 요청의 owner approval 사전 승인은 적용했다. 별도 승인 receipt나 reviewer gate를 만들지 않았다. 다만 실행 요청은 repository 밖의 **계획에 명명된 필수 입력 읽기**만 허용했고 §4.5의 external output exception은 채택하지 않았다. 따라서 `PZ-t2/t1-final`과 `PZ2/t2-final`의 명명된 파일만 읽었으며 `PZ2/t3d1`을 생성·열람·사용하지 않았다. owner gate 사전 승인을 더 구체적인 파일 접근 제한의 해제로 해석하지 않았다.

작업 시작 시 있던 dirty/untracked T3 구현, `.gitattributes`, 문서 및 `b/`, `g/`, `i/` 상태를 보존했다. 이번 write set은 기존 Python wrapper, 기존 Lua harness, `Iris/build/ENTRYPOINTS.md`, 이 계획과 original T3 계획의 실행 인계 기록 다섯 파일이다. product Lua, Menu generation/pointer/EN payload, producer, owner contract/output, current route, `DECISIONS.md`, `ARCHITECTURE.md`, `ROADMAP.md`는 이번 작업에서 수정하지 않았다. commit/push하지 않았다.

Current route에 열거된 T1 네 파일과 T2 세 파일의 실제 SHA-256은 §4.2 및 route의 값과 일치했다. T2 manifest `2b4bee6ce9a262e727b57d7c254e7c2f2211780100cf1c222468a93419ef3efe`, product `4d9d109eaaf0f61e638ebf94cee33c8c306e88f322143c74c8eecdb8131646fd`를 explicit admission으로 사용했다. 초기 S2 pair set은 1,314 / `c5db8a28892229df25f9b65b22e045515b3ac1fcc0d476bb8a1231131832cd28`이며 case normalization이나 observed-success 기반 축소는 없다. support 2,280, 분포 `367 / 825 / 895 / 137 / 56`과 current Menu generation은 §4.2 그대로다.

### Missing-policy checkpoint와 12개 disposition

현재 `docs/iris_layer3_body_role_realignment_policy.md`는 없으나 저장소 Git의 `6ce9197131e3be8fca3d05ea0ec6cbcb2a04d6f6`에서 읽을 수 있었다. 해당 문서 blob은 `c55505ccde6a19632d6b848860c8acb031975234`이며 삭제 이력은 `f9e44e98b6ffd502410cce726ceab209c42c9873`이다. 과거 문서를 current 파일로 복원하거나 퇴역 producer/gate를 재활성화하지 않았다.

회수 정책의 denominator/readiness 단락, source-mapping 단락, Menu projection / “Tooltip work stops at role-labeled input readiness” 단락과 현재 `DECISIONS.md`의 「Layer 3 body production / optional role-material contract」를 대조했다. 실제 common rule은 다음과 같다.

- 12개 모두 approved facts에 `primary_use`의 `direct_use` provenance가 있다. `L3R-MAP-005`가 해당 역할 fact를 허용하며 generation과 S2에 같은 single core ID가 남는다.
- 12개 모두 non-empty `special_context`가 있지만 해당 field의 `fact_origin`은 없다. 기존 `L3R-MAP-008`은 이 조합을 `review_required`로 처리한다. `classify_readiness`와 `classify_disposition`은 review를 우선하고, `compose_role_material`은 이 readiness의 Menu body를 비우면서 core ID를 유지한다. 이는 모든 12개에 같은 원인이 적용된다는 코드·입력 대조이며 새 source truth 판정이 아니다.
- current approved candidate도 target `text_ko=null`, `source=layer3_role_realign_silent_v1`이다. EN producer는 이 public-body predicate 때문에 record를 생성하지 않는다. Tooltip producer는 primary-use/single-core predicate를 사용한다. `silent` token만으로 scope를 판단한 것이 아니다.
- ratification contract SHA `888f47cda897e21aa901ab1066872ee176a95782a06a4de54e6ab33342d3c7f2`, mapping SHA `e7c6fbdcee6a36aa0db0b12ab0763c1f35aada3287c642d9d0001687adcc62ed`, readiness SHA `1a504a6028c0323841f2ab22afcd48f569d15dd3d7a13dc086252833c617f7d5`를 읽었다. 과거 installation authorization은 predecessor candidate binding이며 current target의 새 표시 승인이 아니다. current facts/approved candidate는 selected generation descriptor에 별도로 결속된다.

**12개 전부 Branch D.** Branch A는 Menu-specific review hold만으로 `Philosophy.md` Iris 규정의 depth-ordering·same-fact·silence 대조를 닫을 수 없다. 비교한 범위는 해당 exact primary-use fact의 Menu body 부재와 Tooltip S2 존재이며, Menu의 무관한 정보량으로 정당화하지 않았다. Branch B는 기존 review hold가 Tooltip S2의 독립 primary-use 공개까지 금지한다는 exact scope가 확보되지 않았다. Branch C는 현재 승인된 KO Menu body가 없고, `primary_use`로 새 본문을 만들어 채우는 것은 §6 Change 3에서 금지한다. 기존 EN 번역 material이 있다는 사실만으로 이 KO/public-display 공백을 해결하지 않는다. `Base.Bleach` / `Base.Rope`의 source correction 승인을 target에 재사용하지 않았다.

| exact FullType | 보존한 core / S2 fact ID | before → after |
|---|---|---|
| Base.BarbedWire | `l3rf-23ebe0b0e37e666d73bd3d4c7c39db19764e3d9218ff254efc312b692032166f` | KO/EN silent, S2 present → 동일 / D |
| Base.CarBatteryCharger | `l3rf-d96036d60fdf9fff996e60aa3810f153a4b57624f9b07a251ff2dc9e482cab1f` | 동일 / D |
| Base.Hinge | `l3rf-5357dd90c73271ed68c161d43e668c2afe93343917b7503738f90f53b9976843` | 동일 / D |
| Base.Jack | `l3rf-81908325ab9b3b0ee939faa950d0116b376640e7a8db1e5ab10224983a7ac415` | 동일 / D |
| Base.LeatherStrips | `l3rf-9c07bb06e567d42b66599c865a5bda832833e09658d4282c7d458d1f6216bf67` | 동일 / D |
| Base.LugWrench | `l3rf-9d36735e92ee216eda82ff1ee7af9fb3d134ba1364c6e83ce6bcc38fcbfebab8` | 동일 / D |
| Base.Paintbrush | `l3rf-f7c2069cbd638de68d39081a3424878e52e38e7f6bf60381076b703c208369b7` | 동일 / D |
| Base.Pipe | `l3rf-044bd4c14dd86854f41b2a042d8c8db3a553505a4fe08ea1c2afa216d0428dea` | 동일 / D |
| Base.Scotchtape | `l3rf-a83c96bc0ba76961c86d11fa76c60b3659733bd9b6378048b1cf41699b7ab841` | 동일 / D |
| Base.ScrapMetal | `l3rf-cddf9936926b95b139927e941aceaf1b7b10f76db4db76ee982bac9ebfefdac3` | 동일 / D |
| Base.TirePump | `l3rf-585b48d6a45b316d7ff14e58dbd1c3ad35c889d5c71a3d5f07a8b3a726291778` | 동일 / D |
| Base.Toolbox | `l3rf-6169a21157a026d0110033bc64cbb795b4109baf3872a11f8f19510257059cb2` | 동일 / D |

이 결과에 필요한 추가 판단은 위 review hold의 **surface scope 또는 기존 승인 Menu material의 exact 근거**다. 일반 owner 서명 재요청이나 새로운 승인 ceremony가 필요한 것이 아니다. §4.4의 B/C mutation·별도 ratification 세부는 해당 branch가 채택되지 않았으므로 해결된 것으로 쓰지 않는다. 변경은 test-local evidence 경계이며 runtime/public/owner authority 변경은 없다. Execution Contract weight는 Light에 해당하지만 이 계획과 기존 source-validation authority의 의무는 유지한다.

### 구현과 evidence ceiling

기존 Lua harness의 `menu`는 KO/EN actual ViewModel에서 소비된 원문 bytes를 hex로 기록하고 active index/module과 연결한다. record 부재는 `no_public_body`, `internal_only`, lookup 미호출·miss·load failure 등으로 분리한다. Python comparator는 중복/오래된 관측, initial ledger 누락·중복, 잘못된 generation/module/text/fact, producer/input/output binding 및 Tooltip tuple 자기 증거를 거부한다. authority-backed non-required set을 새로 발급하지 않는다.

`--en-replay-root` 연결은 기존 `build_english_entries` / `_current_projection` / `_write_runtime`을 사용하고, 허용된 외부 root의 새 leaf에서만 재현하도록 구현했다. producer·approved input·pointer·전체 EN Index/chunk bytes를 결속하고, Tooltip과 비교하기 전에 기존 scalar fact identity convention과 approved mapping/cluster lineage를 대조한다. 이 test-local identity 대조는 fact/validation authority가 아니다. live `main()` 호출이나 Tooltip owner output 복사는 없고 production code도 바꾸지 않았다. 이 경로의 **실제 producer/serializer 실행은 BLOCKED/미검증**이며 synthetic positive fixture를 actual EN evidence로 제출하지 않는다.

현재 한 번의 Menu 실행은 시작/종료 source·input·generation·output binding이 같은지 확인하고 initial selected의 KO 1,302개를 current generation의 exact fact와 text에 연결했다. EN 1,302개는 actual consumption만 관측했으며 independent provenance verified는 0이다. KO·EN complement는 위 exact 12개로 일치했고 각 사유는 `no_public_body`였다. 전체 public Menu는 KO/EN 각각 2,072, selected L4 subset은 locale별 530개 모두 관측됐다. 이 부분 결과를 aggregate command PASS라고 쓰지 않는다.

T1/T2 재생성, S2 row transition, Menu generation 전환은 없다. product/hash와 selected pair set은 그대로이며 source/generation/output의 새 mutation도 없다. 따라서 target 외 1,302개를 포함한 data bytes에 이번 구현의 변경은 없다. owner fact 1,314 / absence 175 / empty-core 791 / silent 33 domain은 분리해 유지했다. 기존 raw consumer baseline이 없어 이를 과거 실행의 동일 원문 증명으로 과장하지 않았고, 별도 non-target proof artifact도 만들지 않았다.

### 최종 검증 구간

Python invocation에는 `PYTHONDONTWRITEBYTECODE=1`, `UV_OFFLINE=1`을 적용했다. 모두 즉시 완료해 진행 중단이나 재시도가 없었다. 실행 중인 장기 command는 남아 있지 않다.

| exact command | 실제 결과 |
|---|---|
| `uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py BrowserStateSelectionSearchAcceptanceTest.test_browserdata_compatibility_and_logging_source_guards` | exit 0; 기존 test method 1개. positive/negative evidence 및 scope/ledger 사례 통합. 새 test file/top-level test function 0 |
| `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` | exit 0; 129 files. 기본 roots의 product Lua 구문 검사이며 harness 자체의 실행/파싱은 다음 command에 포함 |
| `uv run python .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py menu C:/Users/MW/Downloads/coding/PZ2/t2-final/tooltip_t2_projection_manifest.json` | **exit 1**; aggregate relation incomplete. KO/EN source missing 12, KO fact/text matched 1,302, EN unverified 1,314, L4 locale별 matched 530 / missing 0 |

정확한 final wrapper SHA는 `eeb55f80636a129efca90ba1a44f12c8241c5ee48e084e684095e8e34f41aa98`, harness SHA는 `c03dca0819afd743564afef3789eccb8536dad835025afbb484e620aea89abf2`다. Menu descriptor SHA는 `bc479e1e49fc3661e2c4e1bbbe489171170f0ced8142546988bf357e61e1902d`, facts SHA는 `e784cf76d2f7d51273eda44906c202c0548f0043027f60cf1af817336c03a6e9`, approved candidate SHA는 `fe6d24a1cac362076db6c3ce895df02eb1ec407bab080aee437df88fc153b5c6`다. 이것은 dirty working-tree의 물리적 실행 identity이며 HEAD commit 전체 검증을 뜻하지 않는다.

Canonical full gate는 source mutation 때문에 여전히 필수지만 **미실행/BLOCKED**다. 현재 environment locator가 참조하는 기존 환경은 §4.5의 허용된 read-only input 밖이다. 그 외부 파일을 읽거나 predecessor 환경/receipt를 새 subject에 재결속하지 않았다. §4.5 output exception이 허용돼도 새 subject의 기존 owner 절차로 환경·work/result를 준비해야 하며 focused PASS로 대신할 수 없다. T1/T2 build/finalize, full/replacement/smoke, 별도 pytest suite, PZ/package/install 및 confidence 목적 재실행은 하지 않았다.

### Inherited status와 original T3 인계

같은 final relation 실행의 `MENU_RELATION_REPORT` stdout에는 initial 1,314 pair의 exact member 목록과 source binding, locale별 missing 사유, 다음 disjoint partition을 출력했다. 별도 report/receipt/manifest 파일이나 registry는 생성하지 않았다.

- `resolved_exact_set = []`.
- `retained_exact_set = []`.
- `unresolved_exact_set = initial_selected_exact_set` 전체. 이 집합의 authoritative member locator는 위 SHA로 결속된 T2 manifest의 `fulltypes`에서 S2 `semantic_identity`와 exact FullType을 취한 1,314 pair이며 pair SHA도 위 값과 동일하다. count 차감으로 구성하지 않았다. 위 12개는 authority와 actual body가 미해결이고, 나머지 exact 1,302개도 EN 독립 producer evidence가 없어 unresolved다.

현재 final S2 selected / Menu KO required / Menu EN required는 모두 **initial 1,314 그대로**, authority-backed silence/non-required는 **공집합**이다. original T3 acceptance에도 이 범위 유지와 이번 `partial` 결과를 additive 인계했다. Branch D를 legitimate silence로 승격하거나 required gap을 retained로 우회하지 않았다. `DECISIONS.md` / `ARCHITECTURE.md`의 historical sealed T1 unverified 기록은 자동 갱신하지 않으며 이번에는 해당 문서 amendment도 없다.

- `validated`: exit 0인 기존 focused fixture와 지정 Lua syntax만 PASS. current binding 및 actual Menu/L4 부분 관측은 위 exit 1 실행의 부분 evidence로 한정한다.
- `unvalidated_but_in_scope`: 12개 final display authority/Philosophy closure, 실제 independent EN reconstruction/producer admission 및 final required relation closure, corrected exact-subject canonical gate. 필요한 경우 후속 B/C propagation도 해당 branch 채택 전에는 완료가 아니다.
- `out_of_scope`: 이 D1에서의 package/install/actual loaded module/PZ/Alt·visual/font/UI-scale, multiplayer/soak/external-mod, translation quality/full truth audit, RTC/DVF freeze/Publish/release. 이 중 original T3의 package/install/PZ/Alt/visual 등은 그 계획에서 여전히 **in-scope 미검증**이다.

결론은 **partial**, reconstruction 연결 코드는 **implemented_only**다. D1 complete 또는 handoff-ready를 선언하지 않는다. 사용자에게 필요한 후속 입력은 §4.5의 한정 external output exception 허용 여부와 12개 review hold의 surface scope/승인 material 근거다. 기존 owner 승인 자체는 이미 받은 것으로 유지한다.

### 동일 작업 재개 — 외부 경계 승인 반영

위 기록 뒤 원 세션 `01a026db-1b3f-7001-9a68-08700f242f40`에서 사용자의 명시적 §4.5 external output exception 승인이 전달됐다. `C:/Users/MW/Downloads/coding/PZ2/t3d1` 내부만 read/create/write할 수 있고, 기존 외부 T1/T2 입력은 계속 read-only다. 따라서 **외부 작업 root 미허용이라는 blocker는 해소**됐으며, 과거 실패나 미실행을 PASS로 고치지 않고 같은 D1에서 이어간다.

Resolved containment와 새 leaf를 확인하고 `a1` attempt를 생성했다. `a1/s`는 `codex/iris-tooltip-t3d1` clean worktree, `a1/python`과 `a1/e`는 전용 interpreter/venv, `a1/cache`와 `a1/tmp`는 tool 작업 경로다. `uv sync --project .\Iris\tooling --frozen --no-install-project`로 lockfile 의존성을 준비했으며 이는 테스트나 gate PASS가 아니다. 기존 attempt/output 삭제·덮어쓰기는 없다.

추가로 위 Git commit의 `docs/새 폴더/iris_layer3_body_role_realignment_menu_tooltip_core_description_readiness_plan.md`를 읽었다. 이 문서의 Minimum Mapping Proposal과 Change 4 validation은 `special_context × origin_missing` 및 `review_hold`의 public successor installation 제외를 명시한다. 따라서 approved `primary_use` fact와 item-level body hold는 구별되지만, 현재 hold를 field-only로 좁히는 처분을 기존 코드의 단순 버그 수정으로 선언할 수는 없다.

원 세션에 한 가지 최소 C 제안을 전달했다: **12개의 승인된 primary-use fragment와 기존 source-bound public acquisition만 기존 registered frame/producer로 Menu KO·EN에 표시하고, 미확인 special_context는 공개하지 않는다.** 이는 source truth나 번역을 추가하지 않으나 review hold의 적용 범위 및 Change 3의 primary-use 기반 새 Menu prose 금지에 대한 한정 채택 결정이 필요하다. Tooltip 문자열을 source authority로 복사하지 않는다. 현재 EN producer의 unconditional context emission도 이 처분과 일치시켜야 한다. 제안만으로 candidate/pointer/producer를 변경하지 않았고 B/C를 이미 채택한 것으로 기록하지 않는다.

최종 P1 input이 확정되기 전에는 같은 실패 relation을 반복하거나, 다시 해야 할 EN replay/subject gate를 미리 실행하지 않는다. 이미 수행한 첫 fixture/Lua/관계 관측은 보존한다. 이것은 T3-D2나 별도 프로젝트의 시작이 아니며 원래 D1의 미완료 상태다.

외부 예외 승인 후 첫 Menu command의 이미 확보한 stdout/exit를 `C:/Users/MW/Downloads/coding/PZ2/t3d1/a1/menu-before.txt`에 그대로 보존했다. 이 파일에 exact 1,314-pair report와 binding이 있으며 새 관측이나 추가 검사 결과가 아니다. Original T3 계획의 「T3-D1 실행 인계」가 같은 required scope와 미완료 상태를 참조한다. 이 시점에는 P1의 위 한정 C 채택 결정을 원 세션에 요청해 둔 상태이며, 표시/producer mutation과 final replay/gate는 아직 실행하지 않았다.

### 사용자 방향 채택 — 일반 설명 통합

이후 원 세션에서 이번 D1은 일반 설명 통합까지 진행하고 `special_context` 전역 폐기는 제외하라는 사용자 지시가 전달됐다. 위 Change 3과 완료 조건을 이 지시에 맞게 한정 개정했다. 이전의 모든 context 무조건 제외 제안과 구별하며, exact 12개의 기본 설명/부연 설명을 대조한 뒤 중복은 기본 설명으로 충족하고 근거 없는 추가 주장만 보류한다. 기존 승인 source fragment·번역을 재사용하는 C 조립과 필드별 공개 보류는 허용하지만 추가 source truth나 임의 authoring을 승인한 것은 아니다. 이전 D/unresolved 기록은 당시 판단으로 보존한다.

**이어진 사용자 정정이 위 조건을 supersede한다.** 사용자 원문은 “special_context 내용을 일괄적으로 일반 용도에 포함시키는거야. 근거가 확인된 내용만 일반 설명으로 옮기는게 아니라”다. 이번 12개 기존 문구 전체를 일반 설명 입력으로 채택하며, 근거 확인분만 통합/나머지 공개 보류라는 직전 조건은 철회됐다. 따라서 C를 실행하고 문구 전체를 보존한다. 새 사실·번역 추가, source 검증을 수행했다는 주장, origin/history 소급 수정, 전역 필드 폐기는 하지 않는다. 이 변경은 동일 D1의 사용자 지정 범위 정정이며 추가 콘텐츠 승인 gate를 요구하지 않는다.

**최종 편집 방식 정정:** 사용자는 “일반 용도의 내용을 바탕으로 두되 디테일한 부분은 special_context를 사용해서 다듬는 것”이라고 명시했다. 문자열 전부 보존/기계적 조립이라는 해석은 철회하고, 기본 의미와 채택된 디테일을 보존하는 bounded KO/EN 편집을 수행한다. 직전 단순 조립 `a1/menu-a`는 설치하지 않은 superseded candidate로 보존한다. 원본 두 field는 수정하지 않으며 통합 문장은 기존 approved candidate의 KO body와 같은 input의 EN material로 채택한다. 이 최신 지시는 사용자 승인 콘텐츠의 편집 방식이며 게임 source 검증 claim은 아니다.

### C 구현 및 최종 relation — 2026-08-30

최신 사용자 편집 지시를 적용한 exact 12개는 모두 C다. 기존 표의 12개 `KO/EN silent → public body`, single core/S2 ID와 Tooltip surface는 불변이다. Before material은 원본 `dvf_3_3_facts.jsonl`의 `primary_use`/`special_context`에 그대로 남고, after KO/EN 문장은 기존 `approved_upstream/candidate_rendered.json`의 `meta.general_description_integration.entries`에 source hash·원래 origin과 함께 둔다. 기본 용도를 중심으로 사용 맥락·대상·정비 단계의 디테일만 편집했고 별도의 게임 기능이나 권장 사용을 추가하지 않았다. 이 메타데이터는 generation-bound 입력 material이며 새 registry/validator가 아니다. EN producer는 채택된 일반 문장을 한 번 소비하고 context를 다시 붙이지 않는다. Tooltip producer는 기존 primary-use surface를 유지한다.

기존 installed builder/installer로 `dvf33-dfdef534a15eb3cae6b66ae4e7995ebf96a09b9b745082bab3ac2fcfbdd67486`을 생성·설치했다. 출력은 `a1/menu-final-a`이며 이전 `a1/menu-a`와 초기 generation은 보존했다. 최초 builder invocation은 repository context env 누락으로 import 단계 exit 1이었고 output을 쓰지 않았다. `IRIS_REPOSITORY_ROOT`를 명시한 실행은 exit 0이었다. 설치 입력 `a1/r2-decision.json`은 기존 R2 selection B를 유지하면서 현행 installed-package 경로와 변경되지 않은 implementation subject `b9d7ae28`에 재결속한 필수 owner 입력이다. 새로운 seal이나 runtime 승인으로 사용하지 않는다. Installer의 기존 mandatory validation을 통과했고 predecessor pointer에서 한 번 전환했다.

실제 production `build_layer3_english_localization`은 EN 2,084개와 owner 1,314개를 출력했다. Tooltip owner 변경은 generation/authority reference와 파생 hash이며 기존 contract의 current owner canonical SHA만 `4edf43068cebdb49932c82d29342db1c467c64ad62d3ad6420051ecc4a0d290e`로 재결속했다. T1/T2 sealed handoff와 product는 재생성·덮어쓰기하지 않는다. 이것은 새 Menu generation을 과거 T1/T2 receipt로 인증한다는 뜻이 아니다. Byte-bound D1 producer/consumer 및 EN output에 한정한 `.gitattributes`를 추가해 Windows checkout 변환으로 실제 관측 identity가 달라지지 않게 했다.

최종 command는 전용 installed environment에서 `uv run --no-project --python C:/Users/MW/Downloads/coding/PZ2/t3d1/a1/e/Scripts/python.exe python -B .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py menu C:/Users/MW/Downloads/coding/PZ2/t2-final/tooltip_t2_projection_manifest.json --en-replay-root C:/Users/MW/Downloads/coding/PZ2/t3d1/a1/en-final-1 --baseline-root C:/Users/MW/Downloads/coding/PZ2/t3d1/a1`이며 **exit 0**이다. 원문 stdout은 `a1/menu-final-1.txt`다. 동일 실행에서 existing EN producer/serializer를 새 leaf에 1회 재현해 live Index/chunk 전 bytes와 대조한 후 actual consumer record와 source-bound primary-use fact를 독립적으로 연결했다. Method는 `current_deterministic_derivability`; historical original-run provenance나 source truth/번역 품질 검증이 아니다.

그 실행의 `MENU_PRESERVATION`은 changed exact set=위 12개, 기존 EN 2,072개 원문 불변, 전체 KO role material/비대상 body 불변, 기존 selected 1,302개 불변, owner absence 175개 및 Tooltip surface 불변을 확인했다. EN 12개 파일의 변화는 record 삽입·chunk routing 변화이며 비대상 원문 변화가 아니다. Actual KO/EN public 2,084개 중 required 1,314개 전부 관측되고 locale별 fact/record mismatch·missing=0이다. S2 selected/KO required/EN required는 initial 1,314 그대로, authority-backed non-required는 공집합이다. `MENU_RELATION_REPORT`의 resolved exact set은 initial 1,314 pair 전체, retained/unresolved는 공집합이며 pair SHA는 초기 `c5db8a28…`와 동일하다. L4 selected identity/source subset은 locale별 530개 모두 일치했다. 지정 Lua syntax command도 **exit 0, 141 files**다.

이 시점에는 actual relation은 PASS이고 corrected-subject canonical Run A/B/comparator만 남았다. 해당 gate의 기존 complete-generation test가 final 입력의 A/B byte equality·path independence를 포함하므로 동일 성질의 별도 generation 반복을 추가하지 않는다. Fixture/회귀 사례도 기존 family 안에서 gate가 실행하며 중복 standalone test를 추가하지 않는다. 최종 gate 결과 전까지 D1 전체 complete를 선언하지 않는다. 과거 FAIL/BLOCKED와 sealed T1 unverified 이력은 그대로 보존한다.

### Canonical gate 실행 경계

필수 source gate용 clean implementation `88e47a6fa83a60dc6d2a67f2a2cad7d06202c7f7`에 기존 writer가 생성한 환경 binding만 추가한 machine subject는 `fb3d8391773fb35f5440824bd42b64ea620e16ea` / tree `0494082f19612de9d57dc2c02ff20ab462e5116b`다. Main checkout은 commit/reset하지 않았으며 시작 시 사용자 변경과 범위 밖 nested workspace 상태를 보존했다. Installed wheel은 `a1/wheel2`, dedicated environment는 `a1/e`, 기존 writer의 immutable receipt는 `a1/er/environment_receipt.json` (SHA `df4181cada590ee53ae2da6cd51df8661a94d80fbbcca13b1f7d59fe2312d5e5`)다. 이들은 기존 canonical owner가 요구하는 입력이며 별도 D1 봉인 체계를 만들지 않았다.

`a1/e/Scripts/iris-tooling.exe --repository-root <a1/s> validate full --commit fb3d8391773fb35f5440824bd42b64ea620e16ea --claim-id iris-tooltip-t3-d1 --environment-receipt <a1/er/environment_receipt.json> --work-root <a1/w1> --result-root <a1/r1> --orchestration-receipt <a1/o1.json>`은 **exit 1**, PowerShell `Get-FileHash` module resolution preflight 실패였다. 프로세스의 `PSModulePath`를 Windows 시스템 모듈 경로로 한정해 같은 subject를 `w2/r2/o2.json`으로 실행한 두 번째 command도 **exit 1**(inner exit 2)이었다. 원인은 테스트 이전의 기존 Windows 경로 안전 검사: longest tracked path 221자 + execution checkout root로 267 > 259였다. `o2.json`, `full-gate.stdout.bin`, `full-gate.stderr.bin`을 보존했다. 실제 pytest/generation determinism/Run B/comparator는 아직 실행하지 않았다.

허용 root는 37자여서 가장 짧은 `<root>/a/x/<221자 path>`도 **263 > 259**다. 단순히 child 이름을 줄여 해결할 수 없으므로 더 짧은 `C:/PZ-D1` 전용 gate work/result root의 한정 예외를 원 세션에 요청했다. 이 경로에는 승인 전 접근하지 않으며 gate 제한·membership을 바꾸거나 alias로 우회하지 않는다. 현재 D1 status는 **implemented_only / required canonical gate BLOCKED**다. Actual relation의 resolved 1,314 / retained 0 / unresolved 0과 gate의 미검증은 별도 axis로 유지한다. 최종 권한 확인은 콘텐츠/owner 승인 재요청이 아니라 실행 프롬프트가 제한한 새 외부 파일 경계에만 해당한다.

### 최신 Build 41 정정 및 짧은 gate 경로 승인

원 세션에서 사용자의 12개 Build 41 수정안이 전달됐다. 이는 직전 primary-use 보존 방침보다 우선하며 source/owner/S2까지 충돌 문구를 정정하고 KO/EN 및 필요한 T1/T2 successor로 전파하라는 지시다. `special_context` 시스템의 전역 폐기는 여전히 제외한다. 이 정정 때문에 `a1`의 relation PASS는 그때 입력의 성공으로만 유지되고 최종 결과는 아니며, 위 S2 불변/새 fact 0 조건은 이번 exact 12개 정정에 한해 superseded다. §5의 기존 affected files와 current facts/input manifest, 기존 T1 decision contract의 hash binding에 필요한 최소 수정을 적용한다. 새 검증 정책이나 source audit는 만들지 않는다.

사용자는 이어서 **`C:/PZ-D1` 내부에만 gate work/result·필수 임시 출력의 읽기·생성·쓰기를 추가 허용**했다. 따라서 §4.5의 이 목적에 한한 짧은 외부 root exception을 채택하며 source/env/successor 출력은 기존 `PZ2/t3d1`을 유지한다. Path/membership guard를 우회하지 않고 새 gate leaf를 사용한다.

현재 정정 source의 facts SHA는 `f29a29560a65e0c7651fc038adeafcd1d6cea1214341a396c8ad6874ac208c5c`, candidate SHA는 `fe69ffc02ce4c105086f4a9cb5394391ef27f5e48138f36a806b5fdddff4e13a`다. 정정은 기존 `primary_use`와 `special_context`의 12개 값에 한정하며 나머지 row/field는 보존한다. Source hash guard에 맞춰 기존 EN translation table을 재정렬·갱신했다. Generation `dvf33-05d76b51c5e1058be4d79afd8a43bc2f0ac8a11c136523166770f181eeaf82c1`을 `a2/menu`에서 생산·설치했고 KO/EN public은 각각 2,084개다. Tooltip owner는 새 12개 core ID/문장을 사용하며 이제 T1/T2 successor를 전파한다. 사용자 원문을 그대로 KO 일반 문장으로 사용하고 획득 문단은 유지했다. EN은 정확히 같은 의미의 한 문장이다. 판정 아이콘·해설·링크는 public 출력에 넣지 않았다.

최신 정정본의 T1 단계 subject는 `d874b2ce37f080a1ab0f3001a881e59e892e68ae` / tree `58316235e48c075e9cf68a0852c4ce2141827178`이다. `a2/d2b` actual relation은 verified 1,406 / not-applicable 874 / mismatch 0, `a2/t1c3` strict candidate는 correction 0 / OPEN / handoff 2,280이다. Earlier d2 admission은 stale Layer2 pointer로 실패했고, t1 candidate는 raw decision hash 대신 canonical hash를 전달한 invocation 실패 및 D5 generation binding stale blocker 2를 거쳤다. 각 결과/empty attempt를 보존하고 실제 참조만 정정했으며 validation code를 약화하지 않았다.

새 environment는 `a2/e`, installed wheel은 `a2/wheel`, 기존 owner receipt는 `a2/er/environment_receipt.json` (SHA `84f8abeb4e2e6fa250f95a119bfbb1b36d96d55966fbb9f193c92c6eebd523b4`)다. 승인된 `C:/PZ-D1` 생성은 OS `Access denied`로 실패했다. Canonical gate는 테스트 시작 전 중단됐고 primary receipt도 쓸 수 없어 launcher의 structured stderr만 남았다. 관리자/ACL/경로 alias 우회는 하지 않았다.

T1 dedicated focused command의 첫 실행은 95 passed / exit 0이나 실패한 TEMP/TMP 설정 때문에 경계 준수 미확인으로 보존한다. 그 위치는 추가 탐색·정리하지 않았다. 사용 가능한 기존 `a1/tmp`를 TEMP/TMP/TMPDIR로 지정하고 `--basetemp C:/Users/MW/Downloads/coding/PZ2/t3d1/a2/pt1`을 명시한 동일 3-file dedicated command는 95 passed / exit 0이며 stdout은 `a2/t1-focused2.txt`다. T1 lifecycle tests는 canonical regular membership 밖이므로 필요한 이 실행 뒤 별도 confidence 반복은 하지 않는다. 남은 순서는 실제 writable gate root의 T1 canonical A/B/comparator 및 finalization, T2 successor·product·해당 필수 검증, 최신 final Menu relation이다. 최신 correction의 actual relation PASS나 D1 complete는 아직 선언하지 않는다.

후속 승인된 `C:/Users/MW/PZ-D1`에서 짧은 gate leaf `1/a`, result `1/ra`, orchestration `1/oa`, temp `1/t`를 사용했다. 생성·쓰기와 기존 path guard를 통과했으며 위 T1 subject의 canonical Run A는 약 3분의 pytest 실행 뒤 **exit 1: 206 passed / 5 failed / 109 subtests passed**, standalone 4개는 exit 0이었다. 실패 attempt의 기존 owner 출력은 `1/oa/receipt.json`, `1/ra/canonical_full_result.json`, `1/ra/full_pytest.stdout.txt`에 보존한다. 실행 checkout은 기존 gate가 정리했고 source checkout은 clean이다. Run B/comparator는 실패 상태에서 실행하지 않았다.

실패 원인은 새 public body를 얻은 BarbedWire를 기존 lazy lookup harness가 계속 silent fixture로 사용한 것 1개와 이전 generation의 runtime lookup package identity로 인한 package fixture 실패 4개다. 사용자는 후속 "그렇게 해"로 `Iris/test/lua/lazy_lookup_acceptance_harness.lua`, `Iris/media/lua/client/Iris/Data/IrisRuntimeLookupPackageIdentity.json`, `Iris/tools/RuntimeLookupIndexIdentity.psm1`의 한정 읽기·최소 수정 범위를 승인했다. 현재도 silent인 `Base.Broom`으로 동일 침묵 guard fixture를 교체하고, 기존 `Assert-RuntimeLookupPackageParity -SkipManifestCheck` 계산 함수로 current generation의 파생 identity를 `lookup-ea4d67f0fdae3a6f`로 갱신했다. 계산 모듈 자체는 수정하지 않았다. 검증 기준 완화, 새 검사기·증명 산출물 추가, 실제 사용자 package/install 검증은 하지 않는다. T1 finalization과 이후 T2 전파는 필수 gate 재실행 결과까지 미완료로 유지한다.

### 최종 closeout — 2026-08-30 / T3-D1 complete

최종 처분은 사용자 콘텐츠 정정에 따른 exact 12개의 C 복구와 필요한 S2 successor 전파다. 같은 정정 fact를 Menu 일반 설명과 Tooltip S2에 사용하고 Menu의 기존 acquisition 문단을 보존하여 same-fact/non-contradiction 및 depth ordering을 충족한다. 새 의미를 runtime assembler에서 만들거나 누락을 non-required로 바꾸지 않았다. `special_context`는 기존 schema에 남되 채택 문장을 두 번 출력하지 않는다. 다른 item·field 및 L2/L4 의미를 바꾸지 않았다. 이전 origin category와 사용자 제공 참고 링크를 독립 source 검증으로 주장하지 않는다.

최종 current generation은 위 `dvf33-05d76b51…`이다. T1은 `b67907dc09b508d538fd12efa2c697a0388d8647` / tree `353a887cf45d4604b88137ced6408dff3712a2cd`의 `a2/t1c4`를 최종화했다. Canonical `C:/Users/MW/PZ-D1/2/oa/receipt.json`, `2/ob/receipt.json`, `2/c/compare_receipt.json` 모두 exit 0 / PASS이며 A/B canonical bytes가 같다. T1 final root는 `C:/Users/MW/Downloads/coding/PZ2/t3d1/a2/t1-final`, closeout SHA는 `8b18aadfa572c27c849b8ab1a0d60e8452e237140d123001ba0ddc94adb5237b`다. Correction 0 / OPEN / strict handoff 2,280을 유지한다.

T1 실제 채택 후 생산한 `a2/t2p` bytes를 제품에 복사하고 기존 wrapper의 admission hash를 갱신했다. Final T2 implementation은 `a3ec5293b1306f0ba74eda2af5dc8730cdd98ff6` / tree `d54f24c36594e5b3ad7f7dca1f563ab22a1204a1`이다. 그 subject의 `a2/t2a`, `a2/t2b`는 Lua/manifest bytes가 동일했고 기존 finalizer가 다시 current T1 binding과 함께 확인했다. Final root `a2/t2-final`의 static state는 complete이며 Lua SHA `d9c88a437c60b49a631e214b577ab8e78a087435101e69d76c8b86e0c65aa10a`, manifest SHA `545bbcb54b0b15aae8b641c646a93d6aeea1b179d907f0b093902ad0c7568d7d`, closeout SHA `7290f8df8983d01027f1aea97d8cba857851209f08e6f2bd86eb036873fb1590`다. Current route는 실제 finalizer 출력이 생긴 뒤에만 새 경로/hash를 채택했다. Historical T1/T2 final roots는 덮어쓰지 않았다.

필수 검증 결과는 다음과 같다. 정확한 gate argv는 기존 orchestration receipts, T2 completion의 command/exit/subject/artifact binding은 기존 `tooltip_t2_closeout.json`에 있다. 별도 proof/manifest/validator를 추가하지 않았다.

| 실행 | 결과 |
|---|---|
| T1 dedicated 3-file pytest, 위 `a2/t1-focused2.txt` | exit 0, 95 passed; 이후 T1 코드·정책 선택 변경 없음 |
| T1 canonical Run A/B 및 comparator, `PZ-D1/2` | 모두 exit 0; 각 211 passed, 109 subtests; standalone 각 4 PASS |
| T2 dedicated 3-file pytest, installed `a2/e` Python과 `--basetemp .../a2/pt2` | exit 0, 18 passed |
| installed `iris-tooling --repository-root <a1/s> inspect current` | exit 0; finalization 전 당시 채택 route 조회 |
| `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` | exit 0, 153 files |
| T2 canonical Run A/B 및 comparator, `PZ-D1/3` | 모두 exit 0; 각 211 passed, 109 subtests; standalone 각 4 PASS |
| 아래 final Menu command | exit 0, relation PASS |

```powershell
uv run --no-project --python C:/Users/MW/Downloads/coding/PZ2/t3d1/a2/e/Scripts/python.exe python -B .\Iris\build\description\v2\tests\test_iris_browser_state_selection_search_acceptance.py menu C:/Users/MW/Downloads/coding/PZ2/t3d1/a2/t2-final/tooltip_t2_projection_manifest.json --en-replay-root C:/Users/MW/Downloads/coding/PZ2/t3d1/a2/en-final --baseline-root C:/Users/MW/Downloads/coding/PZ2/t3d1/a1
```

이 한 실행의 stdout `a2/menu-final.txt`에 actual observation·preservation·inherited status를 함께 기록했다. EN은 current producer/input으로 한 번 재현한 Index/chunk bytes와 actual consumer를 연결한 `current_deterministic_derivability`다. Historical original-run provenance나 번역 품질 인증은 아니다. KO/EN public 2,084개, required fact/record 각 1,314개 모두 일치하고 missing/mismatch/unverified는 0이다. Initial ledger SHA `c5db8a28…`를 유지하며 12개 before/after fact-ID를 명시했고 final selected pair SHA는 `eeb88db8e8ddd96c008ef16f7508e9d31b2cdcaae23caaedf4f093b30de8522a`다. Resolved exact set은 initial 1,314 pair 전체, retained/unresolved는 공집합이다. Required FullType은 줄지 않았다.

같은 실행에서 기존 selected 1,302개, 기존 EN 2,072개 원문, 비대상 source facts 2,093개, acquisition, owner absence 175개와 비대상 S2/S1/S3/S4를 보존했다. L4 selected identity/source는 locale별 530개 모두 actual subset에 일치했다. Support는 2,280, 0/1/2/3/4줄 분포는 `367/825/895/137/56`이며 12개 각 항목의 KO/EN 줄 수·slot vector도 이전과 같다. 최대 4 logical rows를 유지한다.

필수 success condition 충족으로 검증을 종료한다. Main checkout은 commit/reset하지 않고 사용자 선행 변경과 범위 밖 nested workspace를 보존했다. 위 machine subjects는 isolated worktree의 검증 대상이며 이후 route/doc carrier를 그 PASS subject로 소급하지 않는다. 환경은 기존 writer의 `a2/er/environment_receipt.json`을 사용했고 새 봉인 체계는 없다. 과거 FAIL/BLOCKED·superseded relation·sealed T1 unverified 이력은 그대로 보존한다. 원 T3에 current artifacts와 final-required scope를 인계하며 전체 T3는 **partial**, `runtime_adopted=false`다. Package/install/actual loaded module/PZ/Alt/visual/failure-isolation은 원 T3의 미검증 범위로 남고 이 D1 완료를 release 또는 runtime adoption으로 읽지 않는다.
