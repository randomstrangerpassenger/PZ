# Implementation Plan

> **Iris DVF 설명 실용성 교정 · Tooltip S2 전파 · Menu 정보 깊이 분리**  
> 작성일: 2026-08-31  
> 상태: `planned` — 코드 조사 기반 계획 작성 완료, 제품 교정·채택·실행 검증 미착수  
> 양식: [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md)  
> 입력: 사용자 제공 「ROADMAP — Iris DVF 설명 실용성 교정·Tooltip S2 전파·Menu 정보 깊이 분리」  
> 수정 근거: 사용자 제공 「Implementation Plan — Integrated Review」 반영 (2026-08-31)  
> 후속 수정: 사용자 요청에 따라 실행 가능한 Menu 결손 교정, 실용성 사례, 비대상 보존 예외를 반영하고 추가 테스트·Gate 및 중복 검증을 최소화 (2026-08-31)
> 조사 기준 HEAD: `54ab73dcec6160f6ee8d776096f6e013148588cb`  
> 성격: current authority와 runtime architecture를 유지하는 public-facing content correction successor

---

## 1. Objective

Iris의 current Layer 3 전체 exact FullType을 검토하여, 공개 설명이 승인된 근거 범위에서 “이 아이템을 게임에서 무엇에 쓰는가?”에 답하도록 필요한 항목만 교정한다. 승인된 core fact 교정은 Menu의 current Layer 3 generation뿐 아니라 Tooltip S2의 T1/T2 정적 projection과 실제 설치본의 Lua lookup까지 전파한다.

Tooltip은 기본 용도·효과를 빠르게 전달하고, Menu는 그 설명에서 이어지는 질문에 승인된 context, acquisition, Recipe / Right-click relation, requirement로 답한다. 추가 정보의 존재만으로 깊이를 인정하지 않는다. 예를 들어 조리 재료의 후속 질문에는 관련 레시피가 답해야 하며 획득처가 있다는 이유로 대신 충족시키지 않는다. 근거 없는 내용을 보충하거나 Menu detail gap을 Layer 3 문장으로 숨기지 않는다.

완료 여부는 변경 문장 수가 아니라 다음 세 축으로 따로 판단한다.

| 축 | 실행 목표 | 완료 근거 |
|---|---|---|
| A. Layer 3 설명 실용성 | 전체 current universe 감사 및 필요한 source-bound correction | exact item별 근거·disposition·readiness·old/new assertion |
| B. Tooltip 전파 | 승인된 S2 변경이 static payload와 runtime까지 도달 | T1/T2 successor, fixed/companion parity, 설치본 lookup |
| C. Menu 정보 깊이 | 후속 질문에 대응하는 detail 확인 및 이번 목적에 필요한 수정 가능한 결손 교정 | 실제 Menu consumer observation, 질문과 답의 연결, 미해결 gap 분리 |

---

## 2. Scope

- 실행 시점의 current subject, Layer 3 universe, Tooltip support, public/silent, S2 core/absence, Recipe companion의 독립 census.
- Layer 3 전체 항목의 의미·정보 실용성 감사. public body가 없는 항목도 검토하되 본문 생성을 강제하지 않는다.
- 승인된 source/fact를 바탕으로 surface-only correction, semantic/fact correction, hold/omission을 구분하고 exact target batch로 처리.
- `primary_use`, 허용된 추가 context, approved upstream candidate, source lineage 및 필요한 KO/EN projection의 일관된 채택.
- Layer 3 successor generation / EN companion, T1 owner output / strict handoff, T2 fixed static data 및 Recipe companion 재생성.
- current Menu consumer, Alt Tooltip, 격리 package/install candidate의 data reachability 및 대표 인게임 확인.
- 이번 Layer 3 감사에서 확인된 기본 쓰임과 연결된 후속 질문을 막는, 근거가 충분한 QG/Menu 결손의 최소 교정.
- changed / unchanged / hold / silence와 Tooltip propagation / Menu relation의 최종 exact accounting.

### Explicitly Out Of Scope

- unrelated refactor, taxonomy / classification 확대, evidence allowlist 완화, runtime architecture 재설계.
- S1~S4 의미, 0~4 logical-row 계약, exact lookup API, Recipe opening 선택 방식 변경.
- Layer 2 sealed display decision, 비대상 Layer 4 identity/order, 과거 collision disposition의 재판정.
- 현재 작업과 무관한 모듈·기존 untracked 파일의 수정·정리·삭제.
- Workshop 업로드, 공개 배포, 사용 중인 설치본 덮어쓰기, release 승격.

**확정된 실행 범위 `[MENU-GAP-SCOPE]=correction`:** 2026-08-31 사용자의 후속 요청은 직전 평가에서 제안한 수정 가능한 Menu 결손의 실제 교정을 이 계획에 반영하도록 지시했다. 원 로드맵에서 미결정이었던 선택은 이번 계획 수정에서 아래의 제한된 correction 범위로 해소한다. 동일한 scope 선택을 실행 중 다시 승인받는 별도 Gate를 만들지 않는다.

- 대상은 전체 Layer 3 감사에서 확인한 기본 쓰임의 후속 질문을 막는 결손이다. 기존 승인 QG fact의 Menu projection miss, 또는 허용된 source로 근거를 확보하여 기존 owner 경로로 고칠 수 있는 QG fact 결손을 포함한다.
- exact target, 질문, 근거, 기대되는 Menu 답, owner lineage를 같은 correction ledger에 기록하고 기존 채택 절차 안에서 처리한다. 이 scope 결정 자체가 아직 확인하지 않은 fact의 승인이나 제품 실행 완료를 뜻하지 않는다.
- unrelated QG 재설계·전면 보강은 하지 않는다. 다만 이번 목적에 해당하는 actionable gap을 작업량이나 일정 때문에 조사 전용으로 돌려 완료 처리하지 않는다.
- source 부족, 안전한 교정 불가, 실제 N/A는 근거와 함께 남긴다. 미관찰이나 승인 대기는 정당한 부재로 바꾸지 않는다. 범위 안의 unresolved actionable gap이 남으면 Menu-depth와 전체 목표는 미완료다.

`attribution-only` 또는 `undecided`는 이 계획의 실행 선택지가 아니다. 이후 사용자가 범위를 명시적으로 축소할 때만 그 변경과 미달성 제품 목표를 기록한다. 여기서는 계획만 수정하며 실제 제품 채택·설치·배포를 수행하지 않는다.

---

## 3. Non-Goals

- 모든 2,105개 문장 강제 변경, silent row의 일괄 공개, 단일 문체·어미로 통일.
- classification, 이름, 현실 상식, 유사 아이템, rendered prose에서 gameplay fact 추론.
- 새 semantic quality authority, replacement disposition/readiness, 종합 품질 점수 도입.
- Menu 전체 본문을 S2로 복사하거나 runtime summary / translation / semantic repair 추가.
- Layer 4 전체 rewrite, 모든 S3/S4 generic/repeated wording 제거, 모든 Menu gap 해결.
- 모든 item에 Recipe / Right-click detail이 존재한다고 가정하거나 새 interaction 생성.
- 새 locale, 전수 manual in-game QA, 외부 모드 전체 호환성 인증, 사용자 이해도 개선 연구.
- DVF freeze, 전체 RTC, Publish Boundary, release / Workshop readiness 판정.

---

## 4. Assumptions

### 4.1 Authority와 실행 경계

최상위 기준은 [Philosophy.md](Philosophy.md)다. [DECISIONS.md](DECISIONS.md)의 Iris body production, Menu/Tooltip, Layer 3–4 responsibility, locale, T1/T2/T3 결정을 [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md)의 current readpoint와 함께 따른다. [EXECUTION_CONTRACT.md](EXECUTION_CONTRACT.md) §6–7의 claim-evidence binding과 bounded closeout을 준수하되 그 문서를 새로운 scope의 승인 근거로 쓰지 않는다. 구체적인 command literal owner는 [Iris/build/ENTRYPOINTS.md](../Iris/build/ENTRYPOINTS.md)다.

이번 요청은 **계획 문서 수정**이다. 문서에 기재한 제품 변경, owner adoption, 외부 generation, package/install 및 인게임 검증을 수행했다는 뜻이 아니다. 후속 실행의 Menu correction 범위는 §2의 이번 사용자 요청에서 정하며, 이전 T3-D1의 특정 12개 correction 승인이나 historical external-root 승인을 새로운 전체 correction 권한으로 상속하지 않는다. 기존 계약이 요구하는 fact decision과 채택 경계는 유지하되 이미 유효한 승인·근거는 재사용하고 item별·Change별 추가 승인을 만들지 않는다.

### 4.2 실제 파일 관측과 predecessor 숫자의 차이

조사 시 `IrisLayer3DataCurrent.lua`가 선택한 generation은 다음과 같다.

```text
dvf33-05d76b51c5e1058be4d79afd8a43bc2f0ac8a11c136523166770f181eeaf82c1
```

| 모집단 / 관측값 | sealed readpoint / predecessor trace | 계획 작성 시 파일 관측 | 실행 시 처리 |
|---|---:|---:|---|
| Layer 3 exact universe | 2,105 | 2,105 | pointer-selected rendered entries를 재집계 |
| non-empty KO public body | 2,072 | **2,084** | actual Menu 소비 결과와 별도로 확인 |
| empty KO body | 33 | **21** | body 없음과 core fact 없음 구분 |
| EN chunk entry | — | 2,084 | KO/EN exact public-key set 비교 필요 |
| T1 owner core entries | 1,314 | 1,314 | single-core identity·surface·readiness 재검증 |
| Layer 3 empty-core | 791 | 791 | `core_source_fact_ids`가 없는 exact rows 직접 관측 |
| owner legitimate absence | 175 | 175 | `absence_entries` 직접 관측 |
| Tooltip fixed support rows | 2,280 | 2,280 | 양 locale 및 whole-support audit로 재확인 |
| Recipe companion FullType | 349 | 349 | 실제 companion key와 QG relation 비교 |
| concrete Recipe variants | 781 | 781 | variant identity/order/locale 재확인 |
| Layer 2 applicable / display silence | 1,406 / 874 | 이번 작성에서는 재검증하지 않음 | 기존 owner display 판정과 actual consumer relation 재관측 |

위 수치는 read-only 파일 집계이지 정식 canonical validation PASS가 아니다. `2,072/33`의 provenance는 단순 로드맵 참고 숫자가 아니라 `DECISIONS.md`의 「Iris DVF System — Layer 3 body production / optional role-material contract」에 기록된 2026-08-22 source-bound material correction의 sealed readpoint다. 이후 T3-D1 계획의 initial observation은 이를 `dvf33-028a3968…`에 연결한다. 현행 readpoint의 오래된 숫자를 강제하지도, observed `2,084/21`을 자동으로 승인 baseline으로 채택하지도 않는다. **sealed predecessor와 current observed 사이의 exact-set delta를 귀속한 뒤에만 mutation baseline을 확정한다.**

검토 반영 중 저장소의 세 rendered payload를 read-only로 대조했다. 아래 provenance와 hash는 계획의 조사 기록이며 실행 시 Change 1에서 exact subject에 다시 결속한다. 상대 경로 기준은 `Iris/media/lua/client/Iris/Data/IrisLayer3Generations/<generation_id>/`다.

| 역할 | generation_id | `dvf_3_3_rendered.json` SHA-256 |
|---|---|---|
| sealed readpoint에 연결되는 T3-D1 initial subject | `dvf33-028a396886eee3ed9bbb6f610c64c8e886ac3e3aab7b8c7381d5d4a48d7145e9` | `ab2f0b3f61731b6018e20c5d2138de09960b279f09609a2bfe416b60976f8fa9` |
| 기존 context 통합으로 12개 body 복구 | `dvf33-dfdef534a15eb3cae6b66ae4e7995ebf96a09b9b745082bab3ac2fcfbdd67486` | `18bf085aa28e3f3419c9de91bd5700ff51e0f1e7f8d3d8de52db92acac2a57e1` |
| 후속 Build 41 문구/fact 교정, current pointer subject | `dvf33-05d76b51c5e1058be4d79afd8a43bc2f0ac8a11c136523166770f181eeaf82c1` | `2ab795831d9526f9667bc908c3007f6ec5f6d3df5d5e5e554c1d45cc842fc753` |

연결 근거는 [T3-D1 계획의 initial observation 및 실행 기록](iris_tooltip_t3_d1_layer3_menu_tooltip_display_en_record_fact_relation_consistency_plan.md), `DECISIONS.md`의 「Iris Tooltip T3-D1 — existing context integration」 / 「Build 41 content correction」, current approved candidate의 `general_description_integration.entries`다. 12개 body 복구와 뒤이은 12개 문구/fact 교정은 서로 다른 전환으로 기록한다.

`028a3968… → 05d76b51…`에서 직접 추출한 empty → non-empty ordered exact set은 다음과 같으며 Change 3의 recent protected set과 정확히 일치했다.

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

Set hash는 case-sensitive 정렬 후 각 key 뒤에 LF 하나를 붙인 UTF-8 bytes의 SHA-256으로 계산한다. 빈 집합은 zero-byte input이다.

- empty → non-empty 및 protected set SHA-256: `aff222df71e1cdb6684ac9ee06cc19f4820ccc0d0f818a7961f7dba0200ded10`.
- non-empty → empty: `[]`, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- 세 payload의 universe는 동일한 exact 2,105개였다. initial → current의 changed entry는 위 12개이며 protected set 밖의 entry delta는 공집합이었다.
- initial → context integration에서 위 12개의 본문이 생겼고 role material 변화는 없었다. context integration → current는 public/silent membership 변화 없이 같은 12개의 본문 및 role material이 바뀌었다.

이 비교는 **저장된 Layer 3 entry의 baseline delta 귀속**에 한정한다. 독립 gameplay source 검증, 전체 historical seal 재검증, T1/T2/EN/package/runtime 전 구간 validation은 아니다. 실행 시 추가 delta, predecessor identity 불명확 또는 필요한 artifact 부재가 발견되면 Change 1을 완료로 간주하지 않는다. 각 모집단을 독립 추출한 후에만 교집합·차집합·분할 관계를 확인하며 숫자 차감으로 다른 모집단을 만들어내지 않는다.

`core fact 없음`, `public body 없음`, `Tooltip 미지원`, `approved legitimate absence`는 서로 다른 상태다. `public body`가 있다는 이유만으로 S2를 만들어서는 안 된다.

### 4.3 코드에서 확인한 실행상의 결합점

| 위치 / symbol | 현재 동작 | 계획에 반영할 사항 |
|---|---|---|
| `build/dvf_3_3_generation_contract.py::CANONICAL_INPUTS`, `build_dvf_3_3_complete_generation.py::build_complete_generation` | facts/decisions/profile 등 7개 canonical input에 approved `candidate_rendered.json`이 포함되며 generation builder가 그 candidate를 소비 | facts만 수정한 뒤 generation이 자동으로 의미를 고칠 것이라 가정하지 않음. 승인된 candidate와 binding도 함께 갱신 |
| `build/build_layer3_english_localization.py::primary_use_translations`, `special_context_translations` | distinct source 문자열의 정렬된 집합 SHA-256과 EN 목록 길이를 검사하고 대응시킴 | KO 교정 시 `PRIMARY_USE_SOURCE_SHA256` / `PRIMARY_USE_EN`, 필요 시 context 대응도 함께 검토. 해시만 바꾸어 stale EN을 통과시키지 않음 |
| 같은 파일의 `approved_general_descriptions`, `_current_projection` | latest integration metadata의 source hash/core/context ID 및 pointer-selected generation input을 검사 | 기존 12개 correction 보존, source/candidate 변화에 따른 binding 갱신과 semantic 변경을 구분 |
| 같은 파일의 `build_tooltip_t1_owner_entries` | 승인된 단일 `core_source_fact_ids`와 `primary_use` KO/EN만 S2 owner entry로 발행. multi-core는 오류 | rendered body 문장 분할·acquisition 승격으로 S2를 채우지 않음 |
| `domains/tooltip_t1/audit.py` | current source union으로 support를 구성하고 slot/readiness/absence 및 Menu parity를 검사 | current whole-support 재감사와 동일 subject handoff 필요. owner output 자기 비교를 Menu 검증으로 대체하지 않음 |
| `domains/tooltip_static_data_projection/recipe_variants.py::current_variants`, `project_recipe_variants` | repository의 fixed Lua를 읽고 QG selection/name/evidence와 대조하여 base+variant 배열 생성 | fixed successor를 격리 candidate checkout에 먼저 놓고 같은 입력에서 companion 생성. 외부 T2 root만 지정해 companion이 자동 갱신될 것이라 가정하지 않음 |
| `IrisTooltipStaticDataLookup.lua::open` | fixed 양 locale와 companion `base`를 비교하며 mismatch는 `nil` | fixed만 교체하면 수정 텍스트가 안 보일 수 있음. companion 전체 부재/로드 실패도 조용한 미표시 위험으로 검증 |
| `IrisAltTooltip.lua` | Alt lifecycle에서 정적 bilingual view 선택, 한 opening 동안 Recipe variant 유지 | 줄바꿈·옆 배치·opening behavior 보존. legacy summary를 경유하지 않음 |
| `layer3_renderer.lua` → `IrisItemDetailModelAssembler.lua::layer3Payload` → `IrisWikiSections` / `IrisBrowserDetail` | current locale의 precompiled Layer 3를 Menu에 전달. QG interactionState / connections는 별도 수집·표시 | 실제 표시된 본문 및 실제 열람 가능한 detail을 관찰해야 Menu relation을 주장할 수 있음 |

위 표의 Python `build/`, `domains/`는 `Iris/tooling/src/iris_tooling/` 아래 경로다. production owner는 installed `iris-tooling` package이며, 폐기된 build tool 복사본이나 historical replay route를 되살리지 않는다.

### 4.4 기존 조사 자료 및 환경

- 기존 untracked [DVF B41 1차 조사](dvf_b41_full_item_first_pass_2026-08-30/README.md)는 수정하지 않는다. 작성 시 그 `summary.json`이 기록한 8개 input hash는 현재 파일과 일치했다. source 전체·의미·인게임 검증이 완료됐다는 뜻은 아니다.
- 해당 자료의 문자열 패턴, 정적 필드, Lua hit, unresolved recipe token은 후속 조사 locator다. 감사 verdict나 approved fact로 자동 채택하지 않는다. 최신 correction과 충돌하는 조사 후보도 별도 exact target 판정이 필요하다.
- PowerShell을 사용한다. Python 실행은 `uv run python <script>` 계열을 사용하고, canonical 환경·installed wheel·외부 output root의 exact binding은 실행 시 확인한다.
- current route index의 과거 외부 final root, 기존 package/installed copy는 현재 source와 같다고 가정하지 않는다. 특히 source-only Recipe 후속·재명명 결과를 이전 T3 package 관찰로 인증하지 않는다.

### 4.5 Integrated Review 반영과 판정 경계

| 검토 쟁점 | 이번 계획 수정의 처리 |
|---|---|
| sealed/current delta exact attribution | **mutation 전 필수 조건으로 채택.** §4.2의 예비 대조와 Change 1의 실행 gate를 분리하고, 미귀속 delta가 있으면 adoption 금지 |
| actionable Menu gap correction의 mandatory 여부 | 초기 수정에서는 미결정으로 보존했으나, 이번 사용자 요청으로 §2의 관련 actionable gap correction을 실행 범위로 확정 |
| audit criterion | Change 2에 실용성·후속 질문 기준과 사례를 명시. pilot은 이를 실제 자료에 적용하는 작업이며 별도 승인 Gate가 아님 |
| S2 비교·transition·길이 | exact `(FullType, KO string, EN string)`와 presence 전이를 같은 diff에서 확인. 길이는 화면 표본 선정에만 사용하고 의무 통계는 제거 |
| test·Gate 최소화 | 신규 독립 테스트 파일·검증기·정식 Gate는 기본 0. 기존 필수 명령은 유지하고 반복 집계·별도 test denominator 검사·중복 실행을 제거 |
| public-text claim | task-scoped usefulness review와 propagation으로 제한. bare `Public Text Quality PASS` / `semantic-quality acceptance` 금지 |

이는 계획 수정의 처리 내역이며 이전 검토 결과를 새 independent PASS로 바꾸는 재검토 판정이 아니다. Menu 범위 변경은 검토자 선호가 아니라 이번 사용자의 명시적 후속 요청에 따른다.

### 4.6 최소 검증과 구현 유연성

- **신규 독립 테스트 파일·전용 검증기·정식 Gate는 기본 0개다.** 기존 테스트로 보호되지 않는 실제 오류 조건이 확인된 경우에만 기존 test family에 최소 사례를 추가한다. 그 방식으로도 검증할 수 없을 때만 추가 이유를 남기고 최소한으로 확장한다. 검증을 검증하는 새 도구·schema·승인 체계는 만들지 않는다.
- 아래 7개 Change는 작업 분해이며 7개의 승인·통과 Gate가 아니다. 조사·작성·교정은 근거가 준비된 batch부터 진행할 수 있고 batch 크기·도구·중간 실행 순서는 구현자가 정한다. baseline 확인, 사실 채택, strict handoff, 검증된 artifact 설치라는 기존 의존 순서는 지킨다.
- 시작 시 baseline census를 한 번 확보하고 감사·수정·최종 비교에 재사용한다. 같은 입력의 census A/B, 매 batch full gate, 단계별 독립 closeout은 요구하지 않는다. 입력이 바뀌면 영향받는 기록과 결과만 갱신하되 기존 계약이 전체 재실행을 요구하는 경우는 따른다.
- 필수 검증은 최종 채택 후보의 생성·전파 흐름에 묶어 **현재 계약이 요구하는 최소 실행 횟수**로 수행한다. T1/T2 finalizer, canonical Run A/B/comparator, required focused/inspect/syntax metadata는 생략하지 않는다. 동일 subject·입력·artifact·검사 범위에 대해 기존 경로가 허용하는 결과만 재사용하며, binding이 달라지면 재실행한다. 서로 다른 필수 subject를 한 번의 검사로 인증하지 않는다.
- canonical gate가 이미 포함한 harness·검사는 별도 반복하지 않는다. 기존 finalizer가 별도 focused 결과를 요구하거나 최종 artifact가 그 검사 범위 밖인 경우에만 필요한 호출을 추가한다. 시험 중 반복하는 targeted check는 오류 수정용이며 별도 의무 Gate로 누적하지 않는다.
- 전수 item 감사와 실제 변경 assertion의 근거 검토는 제품 작업으로 유지한다. 기록은 가능한 한 한 개의 item/correction ledger와 기존 실행 결과를 사용한다. 길이 통계·개별 test 수·보고서 파일 수를 새로운 합격 조건으로 만들지 않는다.
- 실용성 pilot과 대표 화면 확인은 같은 사례를 재사용한다. 최종 후보의 한 묶음 관찰로 여러 조건을 함께 확인하며, 수정이 없는데 같은 표본을 단계마다 다시 검사하지 않는다. 실제 관찰 없이 화면 동작 완료를 주장하지 않는다.

---

## 5. Repository Areas Affected

아래는 후속 **구현 시의 후보 범위**다. 이번 문서 작성에서 실제 생성하는 파일은 이 계획 문서 하나다. 코드 변경은 확인된 content propagation / consumer defect에 필요한 최소 범위로 제한한다.

이 절의 script/test 경로는 책임을 찾기 위한 source locator이며 실행 command literal이 아니다. 실행 전에 `ENTRYPOINTS.md`의 current command 및 실제 source 경로와 대조하고, stale하면 현재 owner 경로를 확인한 뒤 계획 locator를 수정한다. 오래된 경로로 실행하거나 compatibility wrapper를 새로 만들지 않는다.

### Code

- `Iris/tooling/src/iris_tooling/build/build_layer3_english_localization.py`: KO/EN source mapping과 기존 integration 검증을 보존한 bilingual correction.
- `Iris/tooling/src/iris_tooling/build/compose_layer3_text.py`, `compose_layer3_role_material.py`, `build_dvf_3_3_complete_generation.py`, `validate_dvf_3_3_complete_generation.py`, `install_dvf_3_3_complete_generation.py`: current production 경로 확인·재사용. 무조건 수정 대상이 아님.
- `Iris/tooling/src/iris_tooling/domains/layer3/cli.py`, `domains/tooltip_t1/`, `domains/tooltip_static_data_projection/`: current owner 발행·T1 audit·T2 serialization·Recipe companion 경로 재사용.
- `Iris/media/lua/client/Iris/Data/layer3_renderer.lua`, `IrisLayer3DataLookup.lua`, `IrisLayer3EnglishLookup.lua`, `IrisTooltipStaticDataLookup.lua`: 조회·locale·generation 경계 검증 대상.
- `Iris/media/lua/client/Iris/UI/Tooltip/IrisAltTooltip.lua`: Alt와 실제 표시 경로 검증 대상, 알고리즘 변경 기본 제외.
- `Iris/media/lua/client/Iris/UI/Detail/IrisItemDetailModelAssembler.lua`, `UI/Browser/IrisBrowserDetail.lua`, `IrisBrowserInteractionProjection.lua`, `IrisBrowserInteractionRenderer.lua`, `UI/Wiki/IrisWikiSections.lua`: Menu detail 추적. §2 범위의 승인된 projection miss에 한해 수정 후보.
- `Iris/tooling/tests/test_tooltip_t1_*.py`, `test_tooltip_t2_*.py`, `Iris/build/description/v2/tests/test_iris_browser_state_selection_search_acceptance.py`, 관련 기존 generation / locale / lookup tests: 보호 조건이 비어 있는 경우에만 기존 family 확장.

### Docs

- `docs/iris_dvf_description_usefulness_tooltip_s2_menu_depth_plan.md`: 본 계획.
- 실행 완료 후 같은 stem의 `_closeout.md`: 관측 subject, 결과 집합, unresolved gap, validation ceiling을 기록할 예정.
- `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`: 실제 adoption 이후 필요한 current successor readpoint만 additive 갱신. 계획 작성 시 완료 상태로 수정하지 않음.
- `Iris/build/ENTRYPOINTS.md`: 실제로 command interface가 달라질 때만 owner 문서에서 갱신. 이 계획에서 별도 명령 체계를 만들지 않음.

### Config

- `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`, `dvf_3_3_decisions.jsonl`, `dvf_3_3_input_manifest.json`: 승인된 exact correction 및 source lineage/binding.
- `Iris/build/description/v2/data/layer3_body_role_realign/approved_upstream/candidate_rendered.json`: approved semantic/body candidate.
- `Iris/build/description/v2/data/layer3_body_role_realign/disposition_readiness_contract.json` 등 current role-material 계약: 조회·준수 대상, vocabulary 변경 없음.
- `Iris/_docs/authority/tooltip_t1/`, `tooltip_t2/`, `iris_current_authority_manifest.json`, `iris_current_route_index.json`: 채택 시 관련 input/artifact binding successor만 갱신. sealed 선택·과거 receipt의 덮어쓰기 금지.
- `Iris/validation/execution/current_environment.json`, `required_validations.json`: 기존 validation authority 참조. PASS를 얻기 위한 denominator 축소나 gate membership 추가 없음.
- §2 범위의 승인된 QG owner input / locale projection 수정이 필요하면 exact target과 관련 파일을 같은 correction ledger에 명시한다.

### Generated Artifacts

- `Iris/media/lua/client/Iris/Data/IrisLayer3Generations/<successor-generation>/` 및 `IrisLayer3DataCurrent.lua`.
- `Iris/media/lua/client/Iris/Data/Layer3English/Index.lua`, `Chunk*.lua`.
- `Iris/build/description/v2/data/tooltip_t1_layer3_owner_input.json`.
- repository-external T1 candidate/final handoff, T2 Run A/B/final Lua·manifest·receipt.
- `Iris/media/lua/client/Iris/Data/IrisTooltipStaticData.lua`, `IrisTooltipRecipeVariants.lua`의 paired successor.
- 기존 package producer가 관리하는 `IrisRuntimeLookupPackageIdentity.json` 등 package identity, 격리 package/ZIP/install candidate.
- 실행별 외부 output root 아래 census / audit / correction / consumer relation / final accounting 자료. 진단 ledger는 product semantic input이나 새로운 persistent validation authority로 등록하지 않는다.

---

## 6. Planned Changes

### Change 1 — Exact Current Subject / Universe Census

**Purpose:** 로드맵 Phase 1. semantic mutation 없이 actual current subject와 독립 모집단을 고정한다.

**Files:** current pointer와 선택된 generation descriptor/rendered, canonical facts/decisions/candidate, EN chunks, T1 Layer 2/3/4 owner inputs, fixed/companion Lua, current route index, 기존 first-pass report.

**Implementation Notes:**

1. HEAD/tree, working-tree delta, canonical input hash, producer implementation/wheel, pointer generation, generated file hash를 기록한다. 기존 untracked 조사 자료는 별도 reference로 표시한다.
2. exact case-sensitive FullType으로 Layer 3와 Tooltip support의 union spine을 구성하고 각 source membership을 별도 필드로 둔다. DisplayName, lowercase, alias 또는 normalized key로 join하지 않는다.
3. item별 current body KO/EN, primary_use KO/EN, core/source/context/acquisition fact ID, owner provenance, disposition/readiness, S2 slot identity, fixed arrays, Recipe/Right-click candidate 및 companion relation을 연결한다.
4. runtime rendered entry에는 `role_material`, `source`, `text_ko`만 있는 현재 shape를 고려한다. disposition/readiness가 직접 없으면 owner contract/decision 경로를 추적하고, 찾지 못한 값은 미확인으로 남긴다. body 존재나 문자열을 보고 역산하지 않는다.
5. 각 집합의 ordered exact-key 목록·count·SHA-256을 같은 baseline 기록에 보관한다. 한 번 추출한 결과의 누락·중복·집합 관계를 확인하고 재사용한다. 별도 census Run A/B나 census 전용 validator는 만들지 않는다.
6. source, generated candidate, package, installed copy를 별도 subject로 구분한다. 과거 external handoff 접근 가능성과 current binding도 확인하되 stale 결과를 재사용하지 않는다.
7. §4.2의 sealed readpoint를 exact predecessor artifact/descriptor/기록에 연결하고 observed current와 비교한다. `empty → non-empty`, `non-empty → empty`, universe added/removed, 계속 public인 row의 content/role-material delta를 각각 exact set으로 추출한다. 각 ordered list와 SHA-256, before/after file hash를 남긴다. hash serialization은 §4.2를 사용한다.
8. empty → non-empty set을 recent protected 12건과 **집합 자체로** 비교하고 두 방향 차집합을 출력한다. 같지 않으면 12건 때문이라고 설명하지 않으며, 추가·소실·비대상 변화 각각에 기존 owner adoption/lineage를 연결한다. 정당한 추가 successor가 있으면 그 exact cause를 기록하되 숫자 맞추기로 delta를 지우지 않는다.
9. `unattributed_baseline_delta = 0`과 predecessor/current binding 확인이 끝난 뒤에만 observed set을 mutation baseline으로 채택한다. 미귀속 delta가 남거나 predecessor evidence를 읽을 수 없으면 mutation/adoption을 막고, 독립적인 read-only 조사만 계속할 수 있다.

**Validation:** duplicate exact identity 0, 소속별 missing row 0, sealed → observed exact transition과 recent protected set 비교 완료, 미귀속 baseline delta 0. public/silent 분할은 같은 Layer 3 집합 안에서만 확인한다. 이 단계의 product bytes 변경은 0이어야 한다. §4.2의 예비 대조는 입력 hash가 실행 시점에도 일치하면 같은 분석 자료로 재사용할 수 있지만 formal PASS를 상속하지 않는다. 달라진 입력만 다시 분석하며 별도 승인 Gate를 추가하지 않는다.

**Deliverables / Exit:** subject binding, sealed/current exact delta attribution과 hash, protected-set equality 또는 잔여 delta의 owner 귀속, independent universe sets, integrated census, Layer 3 ↔ S2 ↔ Menu baseline. 실행 시 숫자가 표와 달라지면 실제 값과 exact 원인을 기록한다. Change 4 mutation 진입의 선행 조건이다.

### Change 2 — Full Layer 3 Semantic Usefulness Audit

**Purpose:** 로드맵 Phase 2. current Layer 3 전수를 first-question usefulness 기준으로 review한다.

**Files:** Change 1 census, approved facts/source locators, 기존 first-pass `item_audit.jsonl` / `source_evidence.jsonl`, current Menu/QG inputs. 산출은 외부 audit ledger.

**Implementation Notes:**

**실용성 판정 기준:** 아래 기준은 이번 사용자 요청을 반영한 실행 기준이다. 첫 batch에서 실제 근거를 가진 서로 다른 family 사례에 적용하고 같은 audit/correction ledger에 이유를 남긴다. 별도의 criterion 승인 Gate나 전용 테스트는 만들지 않는다. 의미 범위나 기존 owner 권한을 바꾸는 새 판단이 필요할 때만 해당 제안의 기존 채택 경계에서 처리한다.

- S2만 읽고 아이템의 기본적인 목적·효과·활동 맥락을 이해할 수 있어야 한다. “작업에서 사용한다”를 “작업용 물건이다”로 바꾸는 정도로는 revise의 목적을 달성한 것으로 보지 않는다. 어미 교정이나 길이 감소 자체는 실용성 개선의 근거가 아니다.
- 전반적인 용도·효과만으로 충분하다. 개별 레시피 목록·재료 수량·기술·절차를 S2에 요구하지 않는다. 반대로 기본 용도를 이해하는 데 필요한, 근거 있는 효과까지 모두 Layer 4로 밀어내지 않는다.
- 대표 사례와 수정 항목의 관련 detail을 검토할 때 `툴팁에서 답하는 질문 → 남는 후속 질문 → Menu의 실제 답/위치`를 연결한다. 실제 후속 질문이 없는 item은 이유를 남기고 N/A로 처리할 수 있다. 새 데이터 schema가 아니라 기존 ledger의 설명 필드로 기록한다.
- 같은 문장이 Menu에 반복되는 것은 허용한다. 그러나 조리 가능성을 설명한 item에서 획득처만 더 보인다는 이유로 조리법 질문이 해결됐다고 판정하지 않는다. 각 applicable 질문에 답하는 detail이 있어야 한다.
- KO/EN은 같은 범위의 사실을 전달해야 한다. unsupported 기능 추가, 근거 없는 부정, 현실 용도의 게임 기능화는 허용하지 않는다.

아래는 **판정 예시이며 특정 아이템에 대한 신규 fact 승인이나 강제 문장 템플릿이 아니다.** 실제 적용 범위는 item별 근거로 결정한다.

| 경우 | 판정에 필요한 차이 | Menu 후속 질문과 답 |
|---|---|---|
| 음식/식재료 | “식사에 쓰는 음식이다”로만 바꾸면 부족. 실제 확인된 섭취 효과·조리 재료 여부를 전달하면 개선 후보이며 모든 음식에 같은 효과를 부여하지 않음 | “어떤 요리에 쓰는가?” → 연결된 실제 레시피·필요 재료/조건. 획득처로 대체 불가 |
| 도구 | “작업용 도구다”의 재진술로는 부족. 확인된 작업 종류와 도구 역할을 이해할 수 있으면 충분하며 세부 제작법까지 S2에 요구하지 않음 | “어느 작업/제작에 필요한가?” → 해당 interaction·requirement |
| 보관함 | “물건을 넣어 운반하는 보관함”처럼 기본 쓰임이 이미 명확하면 keep 가능. 숫자를 반드시 추가하거나 문장을 강제 변경하지 않음 | 관련 상세 질문이 있으면 실제 정보에 연결하고, 별도 detail이 적용되지 않으면 이유와 함께 N/A |
| 근거가 제한된 물건 | 현실 활동을 할 수 있다고 덧붙이지 않음. 안전한 정체성 설명을 유지하거나 기능 주장을 보류 | 존재하지 않는 interaction을 만들지 않음. 미관찰과 근거 확인 후의 N/A를 구분 |

이 기준을 실제 사례에 적용한 이유를 확인하면서 나머지 전수 감사와 교정을 진행할 수 있다. 기준 자체가 바뀌면 영향받는 exact set만 재검토한다.

1. 모든 exact item에 기본 쓰임 식별 가능성, 목적·효과의 구체성, assertion별 source 연결, 현실 기능 오인, Layer 4 흡수, S1/S3/S4 불필요 반복, KO/EN fact parity를 적용한다.
2. “작업에서 사용”, “준비 작업”, “작업 중 다룸” 등 scan과 같은 문구 grouping은 review 순서만 정한다. 항목별 supported fact가 같다는 증거 없이 일괄 rewrite하지 않는다.
3. 기존 `keep / reduce / revise / hide / review_hold`와 `description_ready / acquisition_only / omission_allowed / insufficient_material / review_required`를 독립 축으로 유지한다. public body가 없는 row에는 별도 `public_body_present=false`를 두며 새 `silent` disposition을 만들지 않는다.
4. 공개 body가 있는 항목의 revise/reduce/hide에는 item-specific 이유를 남긴다. silence를 용도 부재로 번역하거나 negative gameplay claim의 근거로 사용하지 않는다.
5. S3/S4 generic/repeated wording을 fixed dataset과 실제 Recipe variant 표시로 나누어 관측한다. fixed generic 문장이 있다고 실제 Alt도 generic이라고 단정하지 않는다.
6. Menu follow-up을 core/context, Recipe, Right-click, requirement, acquisition 등 실제 detail별로 조사하되 S2에서 이어지는 질문에 답하는지를 확인한다. unrelated detail의 존재로 verified 처리하지 않는다. 이번 목적에 필요한 approved QG fact의 projection miss와 approved source로 correction 가능한 QG fact 결손은 `actionable_gap`이다. source 부족·current authority로 안전한 correction 불가이면 `legitimate_unresolved`와 구체적 제약을, detail 자체가 적용되지 않으면 `not_applicable`과 이유를 기록한다. 미관찰은 `not_observed`이며 legitimate 상태로 추정하지 않는다.
7. `abstract_task_restatement` 등 문제 유형은 기존 ledger의 서술형 diagnostic reason으로 기록한다. 이번 작업에서 persistent classification field나 새 authority/schema를 도입하지 않으며, 그 설계를 감사의 선행 조건으로 만들지 않는다.

**Validation:** 위 기준의 전수 exact coverage, 누락/중복 0, item별 근거/이유 추적, 질문에 대응하는 Menu 답과 gap 원인/actionability 분리. 감사 자체는 product mutation을 하지 않으며, 확정된 target의 후속 correction 작업과 병행할 수 있다. 독립적인 사람 판단의 일치나 audit ledger의 별도 A/B 실행을 요구하지 않는다.

**Deliverables / Exit:** 위 기준을 적용한 사례와 full audit, proposed disposition/readiness, 질문-답 연결 및 actionable/legitimate/N/A/not-observed를 구분한 Menu depth baseline, S3/S4 limitation baseline. 같은 ledger에서 관리하며 미검토 항목을 keep으로 채워 완료 처리하지 않는다.

### Change 3 — Evidence Adjudication / Correction Design

**Purpose:** 로드맵 Phase 3. 문장 작성 전에 exact item별 말할 수 있는 사실과 mutation 경로를 결정한다.

**Files:** facts/decisions/source lineage, approved candidate와 role-material contracts, EN producer mapping, external correction ledger 및 target batches.

**Implementation Notes:**

1. current assertion을 분해하고 approved evidence와 대조하여 supported / unsupported / unresolved로 구분한다. 기존 승인 근거로 충분한 일반적 용도를 설명하는 데 모든 레시피·callback을 다시 추적하지 않는다. 새 assertion이나 확인된 충돌을 해결하는 데 필요한 범위에서만 해당 Build, 적용 조건·callback·동작 경로를 확인하고 기존 owner 절차를 따른다. QG presentation 자체를 Layer 3 evidence로 사용하지 않는다.
2. A `surface-only`: 같은 supported fact의 표현만 교정. B `semantic/fact correction`: assertion/범위가 바뀌므로 owner fact decision과 successor relation 필요. C `hold/omission`: approved material 부족으로 확대 보류. A/B/C는 실행 경로이며 semantic 상태 vocabulary가 아니다.
3. 모든 proposal에 exact FullType, source locator/hash, old/new assertion, old/new KO/EN S2, Menu core/context, fact identity/lineage 변화, expected body/S2/detail delta, owner decision ref를 남긴다. expected S2는 `(exact FullType, KO string, EN string)` tuple로 동결하고 absent는 양 locale `null`로 표시한다. fact ID/source lineage와 presence도 별도 필드로 결속한다. 변경된 FullType만 같아서는 expected surface 충족이 아니다.
4. 의미가 같은 surface-only 변경이라도 현행 source-value 기반 identity 계산이 ID 변경을 요구하면 기존 lineage 방식으로 기계적 successor를 기록한다. 의미 변화와 byte/ID 변화를 섞지 않는다.
5. Menu 추가 context는 같은 approved core fact에 연결하며 S2는 core description 하나로 제한한다. acquisition과 QG detail은 자기 owner·역할을 유지한다.
6. 첫 batch는 서로 다른 item family와 S2/Recipe/Right-click/무본문 structural case를 포함하도록 actual target에서 선정한다. 고정 batch 크기나 변경률 목표는 두지 않는다.
7. §4.2에 나열한 최근 승인 12개를 기본 보호 집합으로 둔다. 감사에서 재교정 필요성이 발견되어도 새 target·근거·owner decision 없이는 문구를 되돌리지 않는다.
8. §2 범위의 exact gap proposal을 작성한다. 기존 승인 QG fact의 projection miss, approved source로 correction 가능한 QG fact 부재, source 부족/안전한 correction 불가, detail N/A, S2 과장으로 구분한다. 마지막 경우는 Layer 3 correction으로 반환한다. 근거가 충분한 actionable gap을 기존 owner의 fact decision 대기라는 이유로 `legitimate_unresolved`로 재분류하지 않는다.
9. §2의 확정된 correction 범위 안에서 exact gap 집합, 수정할 부분, 기대되는 답과 owner lineage를 기존 batch proposal에 함께 기록한다. 동일 scope 선택이나 기준을 다시 승인받지 않는다. 기존 owner contract가 새로운 fact decision을 요구하면 해당 batch 채택에서 묶어 처리한다. unresolved actionable gap은 Menu-depth와 전체 completion을 막으며 단순 작업량/일정 사유로 범위 밖으로 이동시키지 않는다.

**Validation:** actual change의 unsupported assertion 0, Layer4 → Layer3 reverse inference 0, unsupported category propagation 0, KO/EN semantic mismatch 0. B의 owner decision이 없으면 그 target만 adoption gate를 닫는다.

**Deliverables / Exit:** frozen target/non-target sets, approved bilingual candidate, correction path/lineage ledger, hold/omission 목록, 관련 Menu gap correction proposal. 근거가 준비된 batch부터 후속 작업을 진행하며 새 독립 승인 Gate를 만들지 않는다.

### Change 4 — Layer 3 Adoption / Current Generation / Menu Consumer

**Purpose:** 로드맵 Phase 4. 승인된 correction을 canonical input, current generation과 Menu에 실제 반영한다.

**Files:** canonical facts/decisions/input manifest, approved candidate, EN producer, complete generation builder/validator/installer, pointer, EN chunks, T1 Layer 3 owner output, Menu consumer.

**Implementation Notes:**

1. 승인된 exact batch만 current owner 경로로 채택한다. facts 수정과 approved candidate 수정, provenance 보존, input hash / entries hash / general-description integration binding을 함께 처리한다.
   Change 1의 baseline 귀속과 해당 target의 근거·교정 판단을 먼저 완료한다. 별도 criterion 승인이나 전체 batch의 동시 완료를 기다리는 새 Gate는 만들지 않는다.
2. current generation builder는 approved candidate를 소비하므로 generation 실행 자체를 새로운 fact 검토나 semantic correction으로 간주하지 않는다. retired workflow를 복원하지 않고 current 도구가 맡지 않는 authoring 판단은 approved proposal에 남긴다.
3. EN의 distinct source 정렬 순서·문자열별 mapping을 old/new로 대조한다. source hash와 배열 길이 일치만으로 번역 의미를 검증했다고 하지 않는다. non-target 문구의 EN mapping 이동도 막는다.
4. 교정 중에는 필요한 candidate 생성·targeted 확인만 수행하고, 채택할 최종 묶음에서 기존 complete-generation 계약이 요구하는 Run A/B와 validator를 실행한다. 동일 input/implementation의 descriptor, index, chunks, rendered projection을 비교하며, 검증 가능한 동일 subject 결과를 별도 반복하지 않는다.
5. 검증된 successor를 격리 candidate checkout에 설치하고 pointer-selected input으로 EN companion과 `publish-tooltip-t1-owner`를 발행한다. KO/EN public exact set과 single-core owner relation을 대조한다.
6. actual Lua Menu consumer가 새 generation과 EN을 읽는지 확인한다. T2 successor가 준비되면 Change 6에서 final S2와 다시 비교하며 owner data 자기 비교로 끝내지 않는다.
7. §2의 범위에 해당하는 승인된 exact QG/Menu target을 실제 수정하고 QG lineage 및 projection 결과를 같은 ledger에 기록한다. target의 정당한 identity/selection/detail 변화는 expected delta에 포함한다. source 부족은 gap 유지, S2 과장은 Change 3으로 반환한다.

**Validation:** 실제 semantic/body delta가 승인된 target 및 expected effect와 일치, 비대상 Layer 3 semantic/text drift 0, 최신 12개 보존, 정당한 hidden/silent 결과 보존, KO/EN key·fact parity, A/B deterministic generation, actual Menu successor read. generation-wide pointer/hash 변경은 content drift와 구분한다.

**Deliverables / Exit:** adopted canonical input, successor Layer 3+EN, T1 owner output, current Menu observation, target/non-target comparison, gap correction 또는 attribution 결과. 후보만 수정되고 current generation이 stale하면 미완료다.

### Change 5 — T1 Reprojection / Paired Static Tooltip Regeneration

**Purpose:** 로드맵 Phase 5. Layer 3 교정을 T1 owner → strict handoff → fixed static → Recipe companion까지 전파한다.

**Files:** `domains/tooltip_t1/`, `domains/tooltip_static_data_projection/`, `tooltip_t1_layer3_owner_input.json`, current Layer 2/4 owner inputs, external T1/T2 artifacts, fixed/companion Lua.

**Implementation Notes:**

1. 새 Layer 3 owner input으로 T1 whole-support audit와 동일 subject의 필요한 consumer relation을 수행한다. T1은 사실 선택/요약 생성 권한이 없으며 기존 eligibility·absence 결정을 적용한다.
2. 기존 sealed S1 선택, D5 case collision disposition과 L4 선택 알고리즘을 보존한다. L4 identity/order 보존은 **비대상과 의도하지 않은 변화**에 적용한다. 승인된 exact QG correction target은 expected identity/selection/locale/detail delta를 동결하고 그 변화만 허용한다. 동일 선택 규칙 아래 target의 적격 후보가 바뀌어 생긴 예상 결과를 회귀로 오인하지 않는다. input binding은 필요한 successor로 갱신한다.
3. correction blocker가 0이고 progression이 OPEN인 strict handoff만 T2에 투입한다. candidate receipt나 과거 handoff를 strict successor 대신 사용하지 않는다. canonical Run A/B/comparator 증거를 기존 finalize 경로에 결속한다.
4. T2를 독립 empty Run A/B root에서 실행하여 Lua/manifest byte equality, exact coverage, KO/EN slot parity를 확인한 뒤 final static successor를 만든다.
5. **Recipe companion은 T2가 자동 생성하지 않는다.** 새 fixed Lua를 격리 candidate checkout의 정식 source path에 반영한 뒤 같은 checkout의 QG inputs로 `recipe_variants`를 생성한다. 이 CLI는 repository 내부 output을 요구한다. 외부 임의 output으로 우회하거나 live source에서 old fixed를 읽게 하지 않는다.
6. final fixed에 대응하는 companion을 생성하고 기존 projection test·runtime harness에서 모든 variant의 base/identity/locale 관계를 확인한다. 기존 필수 경로가 요구하지 않는 별도 companion Run A/B 및 전용 comparator를 추가하지 않는다. fixed와 companion은 검증된 한 세트로 채택한다.
7. 기존 missing-name exclusions `uc.recipe.empty_baking_tray`, `uc.recipe.hockeymasksmashbottle`, `uc.recipe.make_wooden_box_trap`와 `without_recipe` 동작을 보존한다. 새로운 이름/evidence mismatch는 fail-closed하고 조용히 exclusion을 늘리지 않는다.
8. approved S2 변경 set과 실제 S2 변경 set을 별도 계산하고 **모든 target의 `(exact FullType, KO string, EN string)` tuple이 frozen expected tuple과 정확히 같은지** 대조한다. serialized Lua는 기존 decoder로 읽고 공백·구두점·대소문자·Unicode normalization으로 차이를 지우지 않는다. fact ID/source relation도 별도로 비교한다. Menu context만 바뀐 항목은 S2 unchanged가 정상일 수 있다. slot ID로 비교하며 compact 배열의 두 번째 줄을 S2라고 가정하지 않는다.
9. 같은 before/after 비교에서 S2 presence 전이와 support added/removed를 함께 기록한다. 양 locale의 presence가 다르면 parity defect다. 이를 위한 독립 테스트·분할 검증기·보고서 파일은 만들지 않으며 기존 disposition/readiness를 바꾸지 않는다.
10. 같은 diff로 KO/EN의 긴 문장·길이 증가가 큰 사례를 찾아 실제 화면 표본에 재사용한다. code point 길이는 표본 선정 보조값일 뿐이다. p50/p95/빈도표/top-10 산출이나 길이 문턱을 의무로 두지 않고, 통계가 없다는 이유로 채택을 막거나 문장 의미를 삭제하지 않는다.

**Validation:** supported row 누락 0, 0~4 logical rows, KO/EN 동일 slot/identity/presence, 실제 S2 changed set = 승인된 expected S2 changed set **및 actual/expected bilingual tuple 정확히 일치**, unintended S1/L4 delta 0, 비대상/예상 밖 identity/order drift 0, fixed/companion base mismatch 0, 기존 계약이 요구하는 generation A/B 동일. 승인된 QG target과 합법적인 readiness/support 변화는 expected delta와 직접 비교한다. 나머지 진단 집계는 같은 diff 결과를 재사용한다.

**Deliverables / Exit:** successor strict T1 handoff, T2 final fixed Lua/manifest, matching Recipe companion, S2 presence와 승인된 QG delta를 포함한 tuple 기반 full-support diff. fixed만 갱신되거나 companion이 stale이면 adoption 불가. diff·표본 선정에 별도 Gate를 만들지 않는다.

### Change 6 — Package / Runtime Reachability / Surface Depth Validation

**Purpose:** 로드맵 Phase 6. 실제 current installed candidate가 새 내용을 소비하고 Menu가 같은 사실의 추가 detail로 이어지는지 확인한다.

**Files:** paired generated payload, 기존 runtime lookup/Alt/Menu code, package producer, external package/install candidate, 기존 T3 runtime harness.

**Implementation Notes:**

1. 승인된 Layer 3 generation+EN+fixed+companion과 기존 runtime을 하나의 package candidate로 만든다. 기존 package identity producer를 통해 manifest/hash를 갱신하고 source → package → extracted install bytes를 비교한다.
2. 격리된 설치 위치를 사용한다. package 생성은 공개 deployment가 아니며 기존 사용 설치본이나 save를 덮어쓰지 않는다.
3. actual Lua lookup에서 exact FullType, KO/EN, unsupported key/locale, empty arrays, companion/base, opening 선택 수명을 검증한다. missing dependency로 skip된 검증을 PASS로 보고하지 않는다.
4. 기존 Menu observation harness의 소비 text, active modules, absent-record reason을 사용한다. 필요 시 admitted T2 manifest와 동일 subject의 EN deterministic replay를 연결한다. owner input과 generated string의 단순 일치를 independent Menu 소비 증거로 사용하지 않는다.
5. item별 S2 claim과 남는 질문을 Menu의 실제 답/위치에 연결한다. 관련 Recipe/Right-click/requirement/context/acquisition 중 무엇이 그 질문에 답하는지를 대조한다. unrelated 정보가 더 있다는 이유로 `follow_up_verified`를 부여하지 않는다. `detail_gap`, `not_applicable`, `not_observed`와 gap별 원인·owner·해소 상태는 같은 ledger에 남긴다. 해결 하나로 item의 다른 actionable gap을 닫지 않는다.
6. 아래 matrix는 독립 테스트 목록이나 전 조합 실행 요구가 아니다. 실용성 pilot과 실제 변경 target 중 **한 사례로 여러 조건을 함께 확인하는 최소 묶음**을 고른다. 긴 KO/EN과 길이 증가 사례는 Change 5의 diff에서 선택한다. code point 길이는 pixel width/wrap의 대체물이 아니므로 최종 화면도 관찰한다. 구조가 없으면 N/A 이유를 남기고 샘플을 만들기 위해 fact를 추가하지 않는다.

| 대표 case | 확인할 내용 |
|---|---|
| S1 + S2 / no S1 + S2 | classification 유무와 무관한 core 설명, compact slot 순서 |
| S2 + Recipe / S2 + Right-click / 양쪽 모두 | 새 S2 보존, actual interaction identity/name, Menu 연결 |
| S2 only | 존재하지 않는 detail의 placeholder·추론 없음 |
| long KO / long EN | 같은 diff에서 고른 긴 문장 표본, 최대 4 logical rows, 원문 보존한 wrap, 화면 경계·옆 배치 |
| Menu context > Tooltip context | 같은 core fact와 실제 추가 context/detail |
| explicit silence / no-S2 / empty array | legitimate absence 보존, 미표시와 오류 원인 구분 |
| item·locale 전환 / Alt release·reopen | stale text 없음, opening 중 선택 유지, 재opening 동작 보존 |

7. 복수 major category의 correction을 포함한 위 최소 묶음으로 최종 후보의 실제 KO/EN 표시와 Tooltip 질문 → Menu 답을 한 번에 관찰한다. 관찰자·버전·설치 hash·item·locale·결과는 같은 기록에 남긴다. 실패 수정 시 영향받는 사례만 다시 확인하되 설치/input binding이 달라진 증거를 무효하게 재사용하지 않는다. 이전 T3 인게임 완료는 새 content 검증을 대신하지 않는다.

**Validation:** packaged/installed payload = approved generated payload, exact Lua syntax/lookup 성공, Alt OFF 무조회·vanilla render 보존·legacy semantic fallback 없음, Tooltip↔Menu contradiction 0, applicable detail relation 명시. representative 결과를 full-universe UX 보증으로 확대하지 않는다.

**Deliverables / Exit:** install identity, runtime reachability evidence, Menu consistency/depth report, S3/S4 limitation report, bounded representative observation. PZ 관찰이 없으면 그 축을 미완료로 남긴다.

### Change 7 — Final Accounting / Closeout

**Purpose:** 로드맵 Phase 7. correction·propagation·Menu relation 결과를 exact item 단위로 분리하여 닫는다.

**Files:** frozen baseline/targets, 각 producer 및 validator 결과, external final ledger, 예정 closeout 문서. 필요한 경우에만 current readpoint successor 추가.

**Implementation Notes:**

1. Layer 3 universe의 audit completion, 최종 disposition, readiness, public body presence를 각각 집계한다. 비대상/실제 변경/보류/omission을 추적한다.
2. Change 5의 같은 full-support diff에서 S2 changed/unchanged/absent, presence 전이, support added/removed 및 expected/actual `(FullType, KO, EN)` tuple/fact identity 비교를 재사용한다. 같은 집계를 다시 만드는 스크립트나 별도 길이 통계 Gate는 추가하지 않는다. Layer 3 수정률을 Tooltip 전파율로 대체하지 않는다.
3. Menu follow-up verified/detail gap/N/A/not observed를 별도 집계하고 unresolved actionable gap / legitimate unresolved의 exact gap set과 영향 FullType set을 각각 남긴다. 같은 item의 여러 gap을 누락하지 않는다. gap 없음·안전한 correction 불가·미관찰을 구분하고, unresolved actionable gap이 남으면 제품 Menu-depth 축을 incomplete로 기록한다.
4. 각 summary count에서 exact set으로 내려갈 수 있게 한다. 상호배타적 분할과 겹치는 진단 축을 표시하고 서로 더해 종합 점수를 만들지 않는다.
5. §2의 correction 범위, unresolved gap과 owner, 실제 검증 범위·명령·exit code·subject/artifact hash 및 미실행 항목을 기존 기록에서 참조한다. scope를 다시 선택하거나 단계마다 새 closeout을 발행하지 않는다.
6. source-bound correction, generation, T1, T2, runtime, Menu relation을 각각 판정한다. 실패·미실행 이력을 지우거나 다른 단계의 PASS를 전이하지 않는다.
7. 테스트를 바꿨다면 기존 diff와 실행 결과로 어떤 보호 조건을 보완했는지 짧게 기록한다. 별도 test file/function/parameter-case 전수 집계나 수량 비교 Gate는 요구하지 않는다. 테스트 수 증가를 coverage 향상으로 등치하지 않는다.

**Validation:** sealed/current baseline 귀속 및 Layer 3 final accounting 누락/미귀속 row 0, approved target·실제 delta/tuple 일치, intended body/S2의 current payload 존재, 질문별 Menu result와 actionable gap의 처리 상태 explicit, 모든 성공 주장이 실제 evidence 범위 안에 있음. 기존 결과를 결산하며 closeout 검증을 위한 새 검사나 Gate를 만들지 않는다.

**Deliverables / Exit:** final exact accounting, changed/unchanged/hold/omission, Tooltip propagation, 질문에 대응하는 Menu relation/gap, validation ceiling 및 최종 closeout 하나. unresolved actionable gap을 조사 완료로 바꾸어 제품 완료 숫자에 포함하지 않는다.

허용되는 요약 claim은 current exact row의 task-scoped usefulness review, source-bound correction propagation, 검증한 대표 Tooltip → Menu information flow까지다. 이 결과를 별도 authority의 bare `Public Text Quality PASS` 또는 `semantic-quality acceptance`로 명명하지 않는다.

---

## 7. Validation Plan

Public-facing content와 설치 산출물을 바꾸는 영향 수준은 유지하되, 검증은 **기존 필수 경로 + 그 경로가 다루지 못한 최소 targeted 확인 + 대표 실제 관찰**로 제한한다. §4.6을 적용하며 아래 표는 검사 목적의 묶음이지 새로운 5개 Gate가 아니다. 이번 계획 문서 수정에는 제품 build/runtime 검증을 실행하지 않는다.

### Automated Validation

| 묶음 | 반드시 확인할 것 | 최소 실행 방식 |
|---|---|---|
| Baseline와 content | exact 집합·baseline 귀속, 전수 감사, 변경 assertion의 근거·KO/EN 동등성, 비대상 보존 | baseline 한 번과 같은 audit/correction ledger를 재사용. 의미 검토를 문자열 테스트로 대체하지 않음 |
| Generation·T1·T2 | 승인된 input/candidate, strict handoff, exact S2 tuple/fact relation, 양 locale/slot·예상 QG delta | 현재 producer/validator/finalizer가 요구하는 최소 Run A/B·focused/inspect/receipt만 실행. 단계별 추가 suite 없음 |
| Canonical regression | 현행 required membership과 exact subject의 성공 결과 | 기존 launcher/comparator 사용. 동일 subject의 포함된 검사 결과를 finalizer에서 허용하는 범위로 재사용 |
| Companion·package·runtime | fixed/base 일치, 전체 variant 관계, generated→package→install identity, 실제 lookup/Alt 동작·Lua 문법 | 기존 projection/runtime harness와 syntax 재사용. canonical이 포함하지 않거나 artifact binding이 다른 부분만 추가 호출 |
| Menu의 답과 실제 화면 | S2의 질문에 대응하는 Menu 답, KO/EN 일관성, 긴 문장·opening·화면 배치 | 기존 Menu consumer 관측을 재사용하고 최소 대표 묶음으로 최종 게임 화면 확인. 미해결 actionable gap과 미관찰은 그대로 공개 |

Lua 필수 명령은 repository root에서 실행한다.

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

Python focused test, T1/T2 build/finalize, Menu harness, package 및 canonical gate의 명령과 파라미터는 [ENTRYPOINTS.md](../Iris/build/ENTRYPOINTS.md)의 current command를 사용하고 실제 실행 literal을 receipt/closeout에 기록한다. **실행 직전 문서·source locator·current command를 대조**하며 불일치는 먼저 해소한다. receipt launcher의 parameter/membership/verdict를 이 문서나 새 wrapper로 복제하지 않는다. Python 스크립트 호출은 `uv run python <script>` 원칙을 따른다. Java/Gradle·JS/TS 변경은 기본 범위가 아니며 해당 변경이 없으면 관련 검증은 N/A다.

각 command는 exact subject에서 exit `0`일 때만 PASS다. missing Lua/uv/wheel/environment/source evidence 등 필수 조건 부족은 해당 축의 **BLOCKED**이며 skip을 성공으로 바꾸지 않는다. canonical gate가 이미 실행한 동일 harness 결과는 재사용하고, 별도 focused 실행은 기존 finalizer의 요구 또는 uncovered scope에 한정한다. 새 독립 테스트 파일·검증기·정식 Gate는 기본 0이며, 필요한 경우에도 실제로 보호되지 않은 실패 조건을 기존 test family의 최소 사례로 보완한다. 단순 문서 수정, 문구마다의 snapshot test, 구현을 그대로 복제하는 테스트, 예전 Gate를 대체하는 우회 검증은 추가하지 않는다.

### Manual Validation

- Change 2의 기준을 서로 다른 family의 실제 사례에 적용하고 current Layer 3 전체 의미 감사와 actual changed assertions의 근거 검토를 수행한다. pilot에 별도 승인·검사 회차를 만들지 않으며 machine scan 완료와 의미 감사 완료를 구분한다.
- KO/EN이 같은 목적·효과·조건 범위를 말하는지 확인. word-for-word equality 또는 mapping hash를 의미 검증으로 간주하지 않는다.
- applicable Menu detail을 실제 열어 same-fact consistency와 해당 후속 질문에 대한 답을 확인한다. detail이 없으면 reason/owner를 남기고 수정 가능한 범위는 교정한다.
- Change 6 matrix는 최소 대표 묶음의 한 번의 관찰로 KO/EN, Alt lifecycle, long text, slot compaction, Recipe opening, Menu detail 전환을 함께 확인한다. 전수 수동 인게임 검사나 조건별 별도 세션은 요구하지 않는다.
- 이전 12개 approved corrections, legitimate silence, exact collision identities, 비대상 S1/L4 보존을 review한다.

### Validation Limits

- 모든 gameplay fact의 독립 원본 재검증이나 EN translation quality 독립 인증을 주장하지 않는다.
- 2,105 전수 인게임 QA, 실제 사용자 이해도 개선 측정, 모든 외부 모드 compatibility sweep은 수행하지 않는다.
- multiplayer, 장시간 세션·성능 보증, full RTC, DVF freeze, Publish Boundary, release/deployment 검증은 수행하지 않는다.
- Lua harness는 actual PZ/Kahlua UI 관찰을 대체하지 않으며 byte parity는 의미 정확성을 보장하지 않는다.
- 이 실행은 selected Layer 3 1,314행에 대한 sealed `unverified_without_independent_consumer_evidence` 상태의 전수 해소를 주장하지 않는다. 미관찰 행의 sealed unverified 상태는 그대로 남으며, representative Menu observation은 관찰한 exact subject/row에 한정된 증거이지 full Menu parity 종결이 아니다.
- Task-scoped usefulness review·correction propagation을 bare `Public Text Quality PASS` / `semantic-quality acceptance`로 확대하지 않는다. 그 별도 authority의 판정은 이번 범위가 아니다.
- **본 계획 작성·수정 시 수행한 것:** 문서·코드 조사, 제한된 current file census, 기존 report input hash 대조, 저장된 세 Layer 3 generation의 exact-set/content delta 대조. **수행하지 않은 것:** 제품 content 변경, formal validation suite, generation, package/install, PZ 관찰. 따라서 이 문서는 해당 검증의 PASS 기록이 아니다.

---

## 8. Risk Surface Touch

### Authority Surface

Affected. 승인된 Layer 3 content/semantic input과 successor binding이 바뀔 수 있다. facts owner, DVF production, QG 책임은 유지한다. §2 범위의 exact QG owner correction을 포함하며 audit ledger와 consumer diagnostic 자체는 fact authority가 아니다.

### Runtime Behavior Surface

Affected. 실제 Menu body와 Alt S2 text가 바뀐다. 기본 runtime algorithm은 유지하며 검증된 projection miss 외의 code 재설계는 하지 않는다.

### Compatibility Surface

No intended contract change. case-sensitive FullType, explicit KO/EN, static data shape, lookup API, 0~4 logical rows, Recipe opening lifecycle을 유지한다. hash/generation ID 변경은 필요할 수 있다.

### Sealed Artifact Surface

Affected through successors. Layer 3/EN, T1 handoff, T2/Recipe companion과 related binding을 mutually consistent successor로 만든다. historical record/receipt, unrelated sealed decision을 제자리 편집하지 않는다.

### Public-Facing Output Surface

Directly affected. KO/EN Layer 3와 Tooltip S2가 교정된다. 관련 QG/Menu correction은 §2 범위의 승인된 exact detail에 한정한다. 현재 턴은 계획 문서 수정만 수행하므로 public product output은 바뀌지 않는다.

---

## 9. Risk Analysis

### Architecture Risk

- Menu depth를 만들려고 QG use_case/requirement를 DVF에 흡수: source·Layer 3·QG·consumer를 구분하고 gap별 owner를 지정한다.
- audit/first-pass report를 새 facts authority로 승격: diagnostic reason은 승인 경로에 투입할 후보일 뿐 generation input이 아님을 유지한다.
- current authoring gap을 이유로 retired workflow 복원: approved candidate와 현행 installed producer 경로를 사용하고 도구 변경이 필요하면 별도 최소 scope로 명시한다.

### Runtime Risk

- fixed 새 버전 + stale companion에서 `Lookup.open`이 `nil`을 반환: paired adoption 및 실제 lookup을 필수 gate로 둔다.
- source와 설치본, KO generation과 EN companion 혼합: exact hash/binding 검증과 격리 candidate 설치로 차단한다.
- 길어진 문장이 읽기 폭·화면 경계를 넘음: 기존 wrap/placement를 보존하고 long KO/EN을 대표 관찰한다. 의미 축약 fallback으로 숨기지 않는다.

### Compatibility Risk

- normalized FullType join으로 `Base.LemonGrass` / `Base.Lemongrass` 같은 distinct key 병합: exact set 비교 및 기존 D5 결정 보존.
- locale별 다른 fact/variant selection: bilingual identity parity, 동일 opening selection, raw-text cross-locale fallback 금지.
- 새 recipe-name 누락을 조용히 제외: 기존 세 exclusions 외에는 generation 실패로 노출하고 owner 판단으로 돌린다.

### Regression Risk

- sealed/current count 차이를 곧바로 baseline에 흡수: Change 1에서 exact 양방향 delta·protected-set equality·잔여 owner 귀속을 확인하고 미귀속이 있으면 mutation을 막는다.
- 같은 wording/category의 bulk semantic propagation: batch 안에서도 exact item별 source trace가 있어야 한다.
- 최근 12개 correction이 predecessor로 회귀: 보호 집합과 per-item non-target byte/semantic comparison을 유지한다.
- EN 정렬 mapping 또는 candidate integration hash stale: distinct 문자열별 old/new correspondence와 generation binding을 함께 검증한다.
- context-only 수정이 S2 변경으로 잘못 집계되거나 generic fixed row가 actual Alt defect로 오분류: slot/fact identity와 runtime variant를 분리 관측한다.
- unresolved gap·미관찰·근거 부족을 keep/verified로 숨김: 독립 accounting 축과 validation ceiling을 유지한다.
- actionable gap을 조사만 하고 해결 처리: §2의 관련 correction 범위와 질문별 답을 대조하며, 미해결이면 제품 Menu-depth와 전체 목표를 미완료로 남긴다.
- 검증 부담 때문에 content 교정이 멈추거나 Gate가 늘어남: §4.6의 기본 신규 0, 기존 결과 재사용, 최종 후보 중심 최소 실행을 적용한다. 단 existing required validation의 생략이나 stale receipt 재사용은 허용하지 않는다.
- target FullType은 맞지만 S2 문구가 다른 경우: expected/actual KO/EN tuple과 fact identity를 직접 비교한다.

---

## 10. Rollback Plan

실행 시작 시 마지막으로 검증된 mutually consistent predecessor set과 target/non-target binding을 보존한다. batch 도중 unsupported assertion, KO/EN mismatch, non-target semantic drift, static nondeterminism, S2 contract violation, companion/base mismatch가 발견되면 해당 batch adoption을 중단한다.

Rollback 단위는 파일 하나가 아니라 다음의 결속된 content set이다.

```text
승인 input / candidate / source lineage / EN mapping
+ Layer 3 generation pointer 및 해당 payload
+ Layer3English index / chunks
+ T1 owner output / adopted handoff binding
+ IrisTooltipStaticData / IrisTooltipRecipeVariants
+ 관련 current route / package identity / 격리 설치 payload
```

관련 QG/Menu를 바꿨다면 해당 successor도 포함한다. 새로운 Layer 3와 이전 Tooltip, 이전 fixed와 새 companion을 혼합하여 rollback하지 않는다. generated text repair나 runtime fallback으로 mismatch를 감추지 않는다.

후속 pointer/binding을 검증된 predecessor로 복귀시키되 historical receipt는 보존하고 rollback 사실을 새 기록으로 남긴다. 기존 사용자 변경·untracked 조사 자료는 건드리지 않으며 wholesale reset/clean은 사용하지 않는다. 현재 계획 문서만 취소하는 경우에는 본 문서 추가만 되돌릴 수 있다.

---

## 11. Governance Constraints

- `Philosophy.md` 준수: Iris는 중립적 정보 제공자이며 추천·효율 평가·우열 비교·게임 상태 변경을 하지 않는다.
- runtime 100% Lua, offline production / runtime viewer 분리. Pulse의 Spoke 역의존 또는 Spoke 간 직접 의존을 추가하지 않는다.
- fact first, sentence second. 이름·classification·현실 지식·유사 문구·Menu/Layer 4 presentation을 facts evidence로 역사용하지 않는다.
- exact case-sensitive FullType과 source slot/provenance/registered lineage를 유지한다. count equality는 set equality가 아니다.
- sealed/current baseline의 미귀속 delta가 있으면 product mutation을 시작하지 않는다. current observation과 승인된 mutation baseline을 구분한다.
- disposition/readiness vocabulary를 바꾸지 않고 두 축을 혼합하지 않는다. silence는 용도 없음이 아니다.
- surface rewrite와 semantic/fact successor를 구분한다. 새 assertion은 owner decision 없이 current input에 채택하지 않는다.
- Tooltip S2는 승인된 core surface, Menu는 같은 fact의 추가 depth다. S1~S4 계약·Recipe/Right-click 동등성을 유지한다.
- 최신 승인 correction과 비대상 sealed decision은 보존한다. 승인된 추가 detail이 있는 gap을 숨기려고 정확한 S2를 약화하지 않는다.
- KO/EN fact parity와 precompiled locale projection을 유지한다. runtime translation/summary/semantic repair, cross-locale raw fallback은 추가하지 않는다.
- fixed/Recipe companion은 같은 입력 generation에서 생성·검증·채택한다. package·install은 이 세트를 유지한다.
- `[MENU-GAP-SCOPE]=correction`은 이번 사용자 요청으로 §2의 범위에 한해 확정했다. persistent audit defect class는 도입하지 않고 기존 ledger의 서술형 이유를 사용한다. 이미 승인된 범위를 다시 묻는 Gate를 만들지 않는다.
- actionable_gap / legitimate_unresolved와 S2 presence 등은 이번 실행의 진단 기록이다. 새로운 semantic state, 품질 점수 또는 persistent authority로 등록하지 않는다. Change 2 기준과 질문-답 연결을 적용하며 길이 통계·test 수량을 독립 채택 조건으로 만들지 않는다.
- durable module/test/generated asset은 current responsibility 이름을 쓴다. `TooltipStaticData` / `tooltip_static_data_projection` 등 current 명칭을 따르고 historical protocol/receipt 식별자는 보존한다.
- regular validation owner는 `Iris/validation`이며 command literal owner는 `Iris/build/ENTRYPOINTS.md`다. 새 gate/authority/denominator를 일회성 감사 편의로 만들지 않는다.
- source-only / generation / static staging / runtime observation / release를 독립 claim axis로 유지한다. 사용자 승인, 검증 receipt, independent evidence를 허위로 생성하거나 과거 결과를 새 subject에 소급 적용하지 않는다.

---

## 12. Expected Closeout State

후속 실행의 목표는 **DVF 설명의 실제 교정, 실제 Tooltip S2 전파, 그 설명에서 이어지는 Menu 답의 확보**다. §2의 관련 actionable gap correction을 포함한다. 다음은 최종 결과의 확인 항목이며 별도 Gate·승인 회차나 여섯 개의 새 테스트를 추가하라는 뜻이 아니다.

공통 완료 조건은 다음과 같다.

1. baseline의 exact delta가 귀속되고 전체 current Layer 3의 감사·disposition/readiness·source relation이 추적됨. 미검토 항목을 keep으로 채우지 않음.
2. Change 2의 실용성 기준에 맞는 교정이 실제 canonical input과 current Layer 3/EN에 채택됨. 문장 길이·어미만 바꾼 것을 정보 개선으로 세지 않고, latest approved/non-target content와 legitimate silence를 보존함.
3. expected S2 changed set **및 exact `(FullType, KO, EN)` tuple/fact relation**이 strict T1 → T2 fixed → matching Recipe companion → installed runtime까지 도달함. 같은 diff로 presence 전이를 확인하며 별도 길이·test denominator 보고를 완료 조건으로 두지 않음.
4. KO/EN 동일 fact, unintended S1/L4 delta 0, 승인된 QG target은 expected delta와 일치, Tooltip↔Menu contradiction 0임. 이번 범위의 applicable 후속 질문마다 실제 답 또는 근거 있는 N/A/한계가 연결되고 unresolved actionable gap이 없음.
5. 기존 required validation의 exact command exit `0`과 최소 대표 인게임 관찰의 실제 evidence를 확보함. 동일 subject의 적합한 결과를 재사용하고 검증 수를 늘리는 것을 완료 조건으로 삼지 않음.
6. 최종 closeout 하나에 changed/unchanged/hold/omission, Tooltip 전파, 질문별 Menu 답/한계, 미수행 범위와 validation ceiling을 기록함. 통계·문서 작성만으로 제품 결과를 대신하지 않음.

Terminal semantics는 다음과 같다.

| 결과 | 허용 closeout | 금지 claim |
|---|---|---|
| 공통 조건 충족, 범위 안의 unresolved actionable gap = 0 | stated validation ceiling 안에서의 `complete`. legitimate unresolved/N/A는 exact 근거·한계와 함께 남김 | 모든 game fact/모든 Menu gap을 해결했다는 확대 주장 |
| 범위 안의 unresolved actionable gap > 0 또는 실제 관찰 미완료 | 해당 축 incomplete 및 overall `partial`; 필수 외부 조건 때문에 진행할 수 없으면 해당 축 `blocked` | 조사만 끝내고 전체 `complete`, 미실행 화면 검증 성공 |
| 구현만 끝나고 필수 검증 미실시 | `implemented_only` | runtime 검증 완료, 제품 목표 달성 |

`actionable_gap`은 approved QG fact projection miss 또는 approved source로 correction 가능한 QG fact 결손이다. `legitimate_unresolved`는 source 부족이나 current authority로 안전한 correction 불가가 근거로 확인된 경우다. detail N/A는 별도로 표시하며, scope 승인 대기·작업량·미관찰은 legitimate 판정의 근거가 아니다. 한 item에 여러 gap이 있으면 모든 applicable actionable gap의 해소 상태를 확인한다.

이미 정해진 Menu 범위나 실용성 기준을 재승인받기 위해 실행을 멈추지 않는다. 새로운 fact decision 등 기존 계약이 요구하는 미해결 사항은 해당 target/batch의 채택 경계에서 다루고 가능한 다른 작업은 계속한다. item별 정당한 hold/omission과 실행 자체의 blocked는 별개다.

어느 closeout에서도 bare `Public Text Quality PASS` / `semantic-quality acceptance`, full RTC / DVF freeze / Publish Boundary / release-ready / Workshop-ready / deployed를 주장하지 않는다. 허용되는 표현은 exact row usefulness review, source-bound correction propagation, 실제 검증한 representative Tooltip → Menu flow에 한정한다. 현재 문서의 상태는 **사용자 후속 요청을 반영한 계획 수정, 제품 실행 미착수**이며 위 완료 조건을 달성했거나 검토 verdict가 PASS로 전환됐다는 선언이 아니다.
