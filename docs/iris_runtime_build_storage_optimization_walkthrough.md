# Iris runtime/build/storage 경량화 Walkthrough

> 작성일: 2026-09-16
>
> 상태: **complete**
>
> 구현 계획: [iris_lightweighting_implementation_plan.md](iris_lightweighting_implementation_plan.md)
>
> 실행 결과: [iris_runtime_build_storage_optimization_closeout.md](iris_runtime_build_storage_optimization_closeout.md)

## 1. 무엇을 완료했는가

이번 작업은 Iris의 공개 정보나 사실을 줄이는 경량화가 아니라, 같은 의미를 더 적은 중복 자료와 더 좁은 UI 갱신으로 전달하도록 내부 표현을 바꾸는 작업이었다.

완료한 범위는 다음과 같다.

- EvolvedRecipe Lua lookup에서 반복 condition 및 bilingual 문구 table을 공유한다.
- Tooltip RecipeVariants가 StaticData base와 같은 행을 복제하지 않고 참조한다.
- Recovery producer가 전체 입력을 복사하거나 provenance를 반복 탐색하지 않는다.
- Browser Detail에서 Layer 3, interaction, variant 변경 시 해당 section만 다시 만든다.
- 보관 후보는 실제 CAS create/verify/restore 표본으로 판단하고, 실익이 없는 자료 이동은 하지 않는다.
- 확인된 tooling cache만 ignore·삭제하고 사용자 자료와 기존 authority는 보존한다.
- 관련 자동 계약과 사용자의 실제 PZ 검증을 통과했다.

이번 완료는 `iris-runtime-build-storage-optimization-2026-09-16` subject에 한정된다. 기존 repository-lightweighting terminal subject, r6 adoption, current product pointer, 공개 release를 대체하지 않는다.

## 2. 변경 전 비용과 경계

### EvolvedRecipe

`IrisEvolvedRecipeLookup.lua`에는 2,203개 relation이 있었다. 각 relation은 자신의 condition 배열과 target/action/display bilingual table을 각각 보유했다. 의미가 같은 관계에서도 같은 table literal이 반복됐다.

- Lua 크기: 1,742,824 bytes
- 반복 value table: relation당 condition 1개와 locale table 3개, 합계 8,812개
- relation record와 canonical ordering 자체는 필요한 정보이므로 제거 대상이 아니었다.

### Tooltip

`IrisTooltipStaticData.lua`와 `IrisTooltipRecipeVariants.lua`는 기존 두 파일 설치 단위였다. Variants는 349개 FullType의 base KO/EN 배열을 StaticData와 다시 저장했고, 각 variant가 base와 같은 행도 문자열로 반복했다.

- StaticData: 1,116,186 bytes
- RecipeVariants: 768,344 bytes
- 합계: 1,884,530 bytes

단순히 `entry.base`를 제거하면 StaticData와 Variants가 서로 다른 세대일 때의 stale-pair 거부가 약해진다. 따라서 중복 제거와 설치 안전성을 함께 유지해야 했다.

### Recovery

Recovery expression 생산은 정규화된 전체 입력을 deepcopy한 뒤 일부 facts와 applications를 제거했다. 사용 중인 provenance를 남기는 과정도 각 provenance마다 모든 fact를 다시 탐색했다. Acquisition successor 역시 payload 전체를 복사한 뒤 authority reference가 있는 일부 행만 바꿨다.

### Browser Detail

Layer 3 target group, interaction 검색·펼침, recipe/evolved variant를 바꾸면 `showDetail(..., true)`로 상세 화면 전체를 다시 만들었다. 그 결과 정적 model과 무관한 child까지 교체되고, 검색 entry의 focus·IME와 scroll 상태를 다시 맞춰야 했다.

### 저장 자료

현재 tree에는 LFS-backed 또는 untracked 대형 자료가 있었지만, 크기만으로 삭제하거나 archive로 이동할 수는 없었다. reader·복원 계약과 exact duplicate 실익을 먼저 확인해야 했다. 기존 repository-lightweighting의 과거 삭제·보관 권한도 이번 파일에 재사용할 수 없었다.

## 3. 최종 구조

### 3.1 EvolvedRecipe shared-value pool

Producer인 `Iris/tooling/src/iris_tooling/domains/layer4/evolved_recipe.py`의 `render_runtime()`이 exact value를 먼저 수집한다.

```text
owner relations
  → exact condition tuple 집합
  → exact (EN, KO) locale pair 집합
  → stable sort
  → sharedConditions / sharedLocales
  → relation record의 numeric reference
```

정렬된 value 집합으로 pool index를 만들기 때문에 입력 순서에 우연히 의존하지 않는다. Relation은 기존 `relation_id`, source/target, role, action key, canonical ordinal과 count를 계속 보유한다. 바뀐 것은 반복 table의 물리 표현뿐이다.

생성 결과는 다음과 같다.

| 지표 | 변경 전 | 변경 후 |
| --- | ---: | ---: |
| Lua bytes | 1,742,824 | 899,122 |
| condition/locale value table | 8,812 | 172 |
| relation record | 2,203 | 2,203 |

공유 table은 runtime 내부 read-only 자료다. Browser UI가 relation condition을 소유·변경할 가능성은 `IrisBrowserInteractionProjection.lua`에서 새 배열로 복사해 차단했다. Scalar display 문자열은 projection row가 별도로 소유한다.

따라서 최종 경계는 다음과 같다.

```text
generated shared relation value
  → lookup의 read-only relation
  → Browser projection이 UI-owned row 생성
  → UI state 변경
```

한 FullType의 UI 변경이 같은 table을 공유하는 다른 FullType이나 이후 조회를 오염시키지 않는다.

### 3.2 Tooltip StaticData와 RecipeVariants 공유

`recipe_variants.py`는 생성된 Variants module에서 StaticData를 한 번 require하고 FullType별 base reference를 잡는다.

```text
IrisTooltipStaticData
  → bases[FullType]
  → RecipeVariants entry.base
  → base와 같은 최종 행은 baseRow(FullType, locale, index)
  → 다른 행만 literal로 저장
```

Runtime은 prefix와 delta로 문장을 다시 합성하지 않는다. Producer가 여전히 각 variant의 완성된 KO/EN 배열을 확정하고, generated Lua는 그 최종 배열의 일부 원소를 기존 base row로 채울 뿐이다. Tooltip의 최대 네 행, 행 순서, recipe/rightclick/evolved_recipe 선택 의미는 바뀌지 않는다.

`baseRow()`는 다른 FullType의 StaticData가 누락됐을 때 module 전체가 load 단계에서 죽지 않도록 nil-safe다. 누락되거나 잘못 결속된 entry를 실제로 열면 기존 lookup 검사가 해당 entry를 fail-closed로 거부한다.

#### stale-pair 보호

중복 base literal을 제거해도 두 파일의 일치 검사는 유지해야 한다. Producer는 각 base의 정확한 KO/EN UTF-8 bytes와 행 수로 compact identity를 만든다. Runtime lookup은 다음을 함께 확인한다.

1. `entry.base`가 현재 StaticData의 exact FullType table과 같은 reference인가.
2. `base_identity`가 현재 bilingual base를 다시 계산한 값과 같은가.
3. variants와 최종 KO/EN 배열이 기존 shape·행 수·kind 계약을 만족하는가.

이 identity는 보안 서명이나 새 authority가 아니라 runtime stale-pair guard다. 기존 Tooltip owner, install, rollback, package의 두 파일 단위는 확장하지 않았다.

| 지표 | 변경 전 | 변경 후 |
| --- | ---: | ---: |
| RecipeVariants | 768,344 bytes | 398,532 bytes |
| StaticData + RecipeVariants | 1,884,530 bytes | 1,514,718 bytes |
| Variants 내부 duplicated base table | 349 | 0 |

### 3.3 Recovery의 선택적 복사

`recovery_expression.py`는 더 이상 전체 `inputs`를 deepcopy한 뒤 제거하지 않는다.

```text
normalized facts
  → note island 제외 fact view
  → 남은 fact의 provenance_ref를 한 번 set으로 수집
  → 해당 provenance만 선택
  → 실제로 아래에서 수정하는 applications branch만 deepcopy
```

Fact payload는 현재 flat payload 계약에 맞춰 얕은 dict copy를 사용한다. 같은 qualified provenance를 여러 fact가 참조하면 첫 복사본을 재사용하고, 다른 내용이 같은 identity로 들어오면 거부한다.

`recovery.py`의 acquisition successor도 전체 acquisition을 복사하지 않는다. 최상위 read-only 값은 공유하고, 새 authority reference가 필요한 `results`와 `fact_question_bindings` 행만 새 dict로 만든다. `acquisition_content()`의 dependency-only 의미 비교는 그대로 유지한다.

두 파일의 `deepcopy` call site는 20개에서 16개로 줄었다. 중요한 직접 변화는 숫자 자체보다 full-input/acquisition copy와 provenance의 반복 reverse scan을 없앤 것이다. 별도 before timing이나 peak-memory 기준선은 만들지 않았으므로 시간·메모리 개선률은 주장하지 않는다.

### 3.4 Browser section 단위 갱신

`IrisDetailChildren.lua`가 다음 정보를 소유한다.

- 현재 Detail panel child snapshot
- section별 child 목록
- section order와 start/end Y
- child별 scroll 적용 전 base Y
- 제거된 section 뒤의 section 위치 이동

`IrisBrowserDetail.lua`는 상세 화면을 다음 section으로 나눈다.

```text
1 identity
2 layer3
3 literature
4 interaction
5 variants
6 meta
```

초기 진입이나 item·locale·Browser generation·detail width 변화는 기존처럼 full rebuild다. 반면 다음 동작은 section refresh를 사용한다.

| 사용자 동작 | 다시 만드는 section |
| --- | --- |
| Layer 3 target group 펼침/접힘 | `layer3` |
| interaction density, fixed recipe, evolved recipe, requirements 펼침/접힘 | `interaction` |
| interaction freeform 검색 변경 | `interaction` |
| recipe variant 펼침/접힘 | `variants` |

Section 갱신은 이전 child만 제거하고 새 section 높이와의 차이만 뒤 section의 base Y와 전체 content height에 반영한다. 기존 scroll은 새 최대 범위 안에서 clamp한 뒤 재적용한다.

Interaction 검색 entry는 Browser가 소유하는 기존 객체를 다시 붙이므로 focus·caret·IME 상태를 유지한다. Static detail model과 identity/literature/meta child는 interaction 입력 때문에 다시 생성되지 않는다. Dynamic recipe requirements는 interaction section을 다시 그릴 때 현재 player/inventory 상태를 읽는다.

## 4. 저장·정리 판단

### CAS 표본

두 untracked acquisition payload를 기존 CAS create/verify/restore 경로에 넣었다.

- logical source: 112,336,280 bytes
- unique object: 112,336,280 bytes / 2 objects
- exact duplicate 제거: 0 bytes
- compressed archive: 17,557,685 bytes
- restore logical-tree parity: true

압축은 효과가 있었지만 원본을 함께 유지한 표본이므로 repository 절감량은 0이다. 또한 해당 표본을 active reader가 archive 위치에서 소비하도록 이전하는 계약을 확정하지 않았다. 따라서 실제 자료 이동·원본 삭제는 하지 않았다.

### Repository cleanup

역할이 확인된 `Iris/tooling/.tmp/uv-cache/`만 `.gitignore`에 추가하고 최종 10,392,380-byte cache를 제거했다. 실행 중 만든 Recovery candidate, B/Menu product, pytest, CAS sample 경로도 작업 완료 후 제거했다.

다음은 보존했다.

- 기존 r1–r6 및 LFS-backed 자료
- quality-review와 generation descriptor
- current/adopted authority와 historical lightweighting 기록
- 이번 작업 전에 있던 사용자 변경과 unrelated `.tmp` 자료

Effective attributes가 이미 필요한 LFS/text 경계를 제공해 `.gitattributes`는 no-op으로 닫았다. 최근 내부 리팩토링 뒤 별도 추출 가치가 있는 중복 본체도 확인되지 않아 structural deduplication은 no-op이다.

Tooltip chunking은 dedup 뒤에도 검토했지만 보류했다. 추가 index/chunk member, require I/O, install/package allowlist, rollback failure point를 정당화할 측정된 post-dedup 이득이 없었다. Chunking 보류는 base/row 공유 완료를 막지 않는다.

## 5. 검증 흐름과 수정된 실패

계획에 명시된 영향 node만 마지막 검증 묶음에서 실행했다. Repository full gate와 관련 없는 Java/Gradle, JS/TS, 전체 archive suite는 실행하지 않았다.

### 최종 성공 결과

| 범위 | 결과 |
| --- | --- |
| EvolvedRecipe, Tooltip serialization/projection, Browser focused nodes | 14 passed in 10.65s, exit 0 |
| non-editable Recovery candidate contract | 1 passed in 1082.57s, exit 0 |
| 같은 프로세스 B→Menu/install/package | 2 passed in 134.92s, exit 0 |
| repository Lua syntax | 269 files, exit 0 |
| repository + product stage Lua syntax | 396 files, exit 0 |

Focused 묶음은 generated EvolvedRecipe Lua의 shared identity와 재조회, UI projection mutation isolation, Tooltip base binding·reader order, Browser state/search/cache와 section 교체를 확인했다.

Recovery는 non-editable installed package와 새 candidate를 사용했다. Candidate는 `complete`, source-confirmed facts는 24,342개였으며 전용 계약 통과 뒤 disposable output을 제거했다.

B→Menu 통합은 같은 Python process에서 B ZIP을 Menu가 직접 받도록 했다. 두 deterministic product build, retained B bytes, stage와 ZIP 실제 Lua lookup, Tooltip/Browser harness, package member, source/member drift 거부, lock/interruption/rollback/recovery를 기존 계약 그대로 실행했다.

### 실패와 수정

최초 실패를 최종 PASS로 숨기지 않았다.

1. EvolvedRecipe aliasing fixture의 Python f-string brace가 Lua 배열 한 겹을 잃었다. Fixture 표기만 수정했다.
2. non-editable package에서 Browser source-guard가 명시적 repository context 없이 import됐다. 실행 환경에 실제 repository root를 제공했다.
3. interaction harness가 production owner에 없는 Apple→Soup 관계를 가정했다. 실제 owner에서 exact Bread relation을 공유하는 Acorn/Banana pair로 교체했다.
4. 실패 뒤 다른 transient B ZIP으로 기존 Menu workspace를 resume하자 exact ZIP path binding이 달라 거부됐다. 이 거부는 정상 계약이었다. 최종 B→Menu는 fresh single-process subject로 실행해 통과했다.

새 validator, seal, receipt, validation-of-validation은 만들지 않았다. 일회성 menu input과 candidate workspace는 기존 계약 실행을 위한 임시 입력일 뿐 authority로 남기지 않았다.

## 6. 실제 PZ 확인

자동 검사 완료 뒤 저장소의 최종 `Iris` 폴더를 대상으로 실제 PZ 검증 항목을 인계했다. 확인 범위는 다음이었다.

- KO/EN Alt Tooltip 표시와 해제
- opening 동안 선택 유지와 item 전환
- 최대 네 행, 화면 가장자리 fit과 가독성
- recipe/rightclick/evolved_recipe 표시
- Menu와 Tooltip 공존
- Browser Layer 3/interaction/variant 부분 갱신
- 한국어 IME와 검색 focus/caret 유지
- 긴 상세 화면의 scroll 유지
- inventory/skill 변화 뒤 dynamic requirement 갱신
- Iris 관련 Lua error·stack traceback·load/identity failure 부재

사용자가 이 인게임 검증의 통과를 보고했다. 이에 따라 자동 검사까지만 끝난 `implemented_only` 상태를 **complete**로 갱신했다.

게임 빌드, 해상도, UI 배율, font 설정과 외부 모드 구성은 별도로 제공되지 않았다. 따라서 이번 수락을 모든 화면·모드 조합의 성능 또는 호환성 보장으로 확대하지 않는다.

## 7. 최종 상태와 비주장

완료된 것은 다음이다.

- 동일 의미를 보존한 runtime data 중복 축소
- Recovery의 불필요한 복사·탐색 축소
- Browser의 무관한 section 재생성 축소
- 확인된 cache 정리와 저장 후보 처분
- 관련 자동 계약과 실제 PZ 기능 관찰

완료로 주장하지 않는 것은 다음이다.

- Kahlua heap·cold/warm load·latency·FPS의 정량 개선
- 전체 external-mod compatibility
- B42 포팅
- current authority/adopted product pointer 전환
- strict production finalization, release 또는 Workshop readiness
- 기존 historical lightweighting terminal subject의 재수락

문제가 다시 확인되면 관찰된 원인의 producer/runtime/section 경계만 재개한다. 이번 PASS를 이유로 전체 corpus 재생산, 추가 proof tree, full gate 또는 새 validation authority를 자동 요구하지 않는다.

## 8. 주요 변경 파일

| 책임 | 파일 |
| --- | --- |
| EvolvedRecipe pool producer | `Iris/tooling/src/iris_tooling/domains/layer4/evolved_recipe.py` |
| EvolvedRecipe generated lookup | `Iris/media/lua/client/Iris/Data/IrisEvolvedRecipeLookup.lua` |
| Tooltip variant producer | `Iris/tooling/src/iris_tooling/domains/tooltip_static_data_projection/recipe_variants.py` |
| Tooltip generated variants | `Iris/media/lua/client/Iris/Data/IrisTooltipRecipeVariants.lua` |
| Tooltip runtime stale-pair guard | `Iris/media/lua/client/Iris/Data/IrisTooltipStaticDataLookup.lua` |
| Recovery orchestration/copy boundary | `Iris/tooling/src/iris_tooling/domains/layer3/recovery.py` |
| Recovery expression projection | `Iris/tooling/src/iris_tooling/domains/layer3/recovery_expression.py` |
| Browser section orchestration | `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserDetail.lua` |
| Browser child/scroll ownership | `Iris/media/lua/client/Iris/UI/Browser/IrisDetailChildren.lua` |
| Browser interaction isolation/render | `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionProjection.lua`, `Iris/media/lua/client/Iris/UI/Browser/IrisBrowserInteractionRenderer.lua` |
| Cache ignore | `.gitignore` |

변경된 assertion은 기존 EvolvedRecipe·Tooltip·Browser Python/Lua harness에 추가했다. 테스트 위치와 기존 ID는 유지했다.

## 9. Rollback 관점

Rollback은 이번에 바뀐 producer, generated Lua, lookup, Browser/Recovery source, 관련 assertion, `.gitignore` 규칙과 이 문서들을 하나의 변경 집합으로 되돌리는 것이다.

- EvolvedRecipe producer와 generated lookup은 함께 복구한다.
- Tooltip producer, Variants와 StaticData lookup은 함께 복구해 서로 다른 stale-pair 계약을 섞지 않는다.
- Browser는 section refresh 연결을 제거하고 기존 full rebuild 호출로 복구할 수 있다.
- Recovery는 전체-copy predecessor로 돌아가도 adopted r6와 baseline을 수정하지 않는다.
- historical authority, 기존 사용자 자료와 이번 작업 전 dirty 변경은 rollback 대상이 아니다.

Disposable candidate와 test workspace는 이미 제거됐으므로 별도 수명 관리나 후속 봉인은 없다.
