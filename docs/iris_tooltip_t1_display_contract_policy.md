# Iris Tooltip T1 표시 계약

> 상태: owner-ratified T1 contract / offline audit implementation adopted / T2 full-data progression expected blocked by upstream corrections
> 채택일: 2026-08-27
> 범위: Tooltip T1 offline projection/readiness contract only

Iris Tooltip T1은 Classification, DVF System, QG가 이미 소유한 사실의 의미를 바꾸지 않고 Tooltip용 구조화 입력 준비성을 판정한다. T1은 정적 Tooltip Lua payload를 만들거나 runtime renderer를 변경하지 않는다.

## 표시 계약

semantic slot은 다음 순서를 가진다.

```text
S1 = Layer 2 classification
S2 = Layer 3 core description
S3 = Layer 4 interaction #1
S4 = Layer 4 interaction #2
```

표시 가능한 행은 최대 네 개다. owner가 증명한 `legitimate_absence` 행과 system-level Layer 2 applicability contract가 판정한 `layer2_display_silence`는 placeholder 없이 표시에서 compact하지만 semantic slot ID와 S1→S4 상대 순서는 유지한다. 그 밖의 identity, authority 또는 locale surface 결손은 absence로 compact하지 않는다. logical row 수 `0~4`와 embedded newline 금지만 T2 hard gate이며 실제 pixel/font/UI-scale fit은 T3 범위다.

## 입력 경계

- Layer 2는 optional navigation/display projection이다. Classification owner가 제공한 resolved classification/category/admissible primary-subcategory identity와 KO/EN surface가 있을 때만 S1을 표시하며 raw tag scan, runtime resolver 복제와 `Misc.9-A` raw fallback 승격을 금지한다.
- T1-D1 successor candidate는 `Iris/build/classification/data/classification_layer2_owner_output.json`의 exact applicability partition을 소비한다. Existing resolved 1,406 rows는 그대로 표시하고, fallback/no-membership/multi-without-admissible-primary 874 rows는 semantic inference나 per-row absence record 없이 `layer2_display_silence`로 판정하여 S1을 생략한다. 이 candidate는 Menu evidence 또는 global current adoption을 발행하지 않는다.
- same-authority는 동일 fact source를 뜻하며 Menu와 Tooltip의 coverage 동일성을 뜻하지 않는다. Menu consumer relation과 applicable/N/A parity는 T1-D2 소유다.
- Layer 3는 owner-approved single `core_description` fact identity와 KO/EN single-line surface만 소비한다. rendered body 자르기, 요약, 재작성, 여러 core fact 합성과 acquisition paragraph 승격을 금지한다.
- T1-D3 successor proposal에서 Layer 3 explicit absence는 exact FullType, DVF owner decision, approved reason/scope/re-audit condition과 producer-independent technical·locale·quality·review defect exclusion evidence가 모두 결속된 경우에만 `legitimate_absence`로 소비한다. 단순 owner-row miss, search miss, locale 결손, review 상태 또는 producer self-report는 absence가 아니다. 이 proposal의 global current adoption은 T1-D6가 소유한다.
- Layer 4는 current owner data인 `Iris/build/description/v2/data/upstream_usecases_by_fulltype.json`의 public QG identity를 `semantic/public eligibility → stable order → exact identity dedupe → source equivalence → bounded selection → identity freeze` 순서로 선택한 뒤 locale/Menu readiness를 조회한다. `Iris/build/baseline/**` reproduction artifact는 semantic input으로 소비하지 않는다.

Layer 4 both-source row는 Recipe 하나와 Right-click 하나를 선택한다. single-source row는 neutral structural order로 최대 두 개를 선택한다. explicit order key가 없는 current subject에서는 versioned `source + NUL + interaction_id` UTF-8 bytes의 SHA-256을 presentation tie-break로 사용한다. 이 값은 중요도, 빈도, 대표성, 효율, 추천 또는 품질 순위가 아니다.

## Locale와 Menu parity

KO/EN은 동일한 selected identity와 order를 사용한다. locale surface나 independent Menu evidence가 없어도 차순위 candidate로 바꾸지 않는다. cross-locale raw fallback과 locale별 reselection을 금지한다.

Menu parity는 문자열 유사도가 아니라 identity relation이다. Layer 4는 owner input identity를 Browser가 소비하는 current runtime `UseCaseDescriptions/Chunk*.lua`의 `label_key` identity와 대조한다. independent consumer evidence가 있을 때만 `verified`를 주장한다. shared-authority relation은 성립하지만 independent observation이 없으면 `unverified_without_independent_consumer_evidence`로 남기며 T3 runtime-adoption parity claim은 보류한다. authority relation이 없거나 모순되면 T2-blocking correction이다.

## Current subject readiness disposition

W1-A census에 따라 current subject에는 다음 구조화 입력 gap이 있다.

- Layer 2: owner-issued resolved identity와 independent Menu consumer identity route 없음
- Layer 3: core source fact IDs와 rendered body는 있으나 single approved Tooltip fact identity/KO·EN surface 없음
- Layer 4: public identity는 있으나 selected identity의 explicit `display_by_locale` 없음
- Support: case-sensitive distinct identity인 `Base.LemonGrass`와 `Base.Lemongrass`는 normalized diagnostic collision을 이루지만 합치거나 denominator에서 제거하지 않는다. `tooltip_t1_d5_current_support_disposition.json`이 declared-target content fingerprint와 exact member-set guard에 대해 applicable할 때 raw observation은 유지하고 해당 pair의 unresolved `SUPPORT_NORMALIZED_COLLISION` correction row만 방출하지 않는다. disposition이 없거나 stale이면 기존 blocking correction을 그대로 방출한다.

T1은 이 gap을 추론으로 보완하지 않는다. owner-ratified support predicate는 current Layer 2, pointer-selected Layer 3, current Layer 4 owner FullType의 case-sensitive explicit union이다. readiness defect 때문에 이 frozen denominator에서 row를 제거하지 않는다.

따라서 T1 contract/audit axis와 T2 progression은 분리한다. whole-universe audit와 owner-attributed correction ledger가 완결되면 T1 contract/audit axis는 complete일 수 있지만, current T2 full-data progression은 owner correction이 반영되고 새 exact subject에서 재-audit되기 전까지 `BLOCKED_BY_UPSTREAM_CORRECTIONS`다. blocked 상태에서는 T2 handoff input/manifest를 생성하지 않는다.

candidate/pre-full-gate record는 task-specific axis를 `partial`, formal state를 `implemented_only`로 기록한다. candidate와 동일 subject의 canonical Run A/Run B 및 deterministic comparator receipt가 모두 exit `0`이고 path·hash·subject binding이 검증된 경우에만 좁은 post-gate finalizer가 두 값을 `complete`로 기록한다. 이 finalizer는 semantic pipeline이나 T2 progression을 변경하지 않는다.

## Machine authority와 명령

- 결정: `Iris/_docs/authority/tooltip_t1/tooltip_t1_decision_contract.json`
- slot/Layer 2–4/locale/handoff/reason 계약: 같은 `tooltip_t1` authority directory
- producer: installed `iris_tooling` package의 `tooltip_t1` domain
- command literal owner: `Iris/build/ENTRYPOINTS.md`
- audit result: repository-external immutable run root

one-off census, correction ledger, run receipt와 audit observation은 regular validation authority가 아니다. tracked fixture expectation은 audit observation에서 self-seed하지 않는다.

Tracked decision contract는 choice vocabulary와 owner-preapproved selected choice를 보존하는 ratification template다. Candidate는 clean exact subject에서 W1-A evidence를 먼저 hash-bind하고, 그 동일 subject/evidence hash를 인용하는 adoption receipt로 G1을 닫은 뒤에만 W1-B support freeze와 projection을 수행한다.

## T1-D4 isolated candidate amendment

T1-D4의 isolated integration candidate는 Layer 4 identity input을 locale authority로 확장하지 않는다. Recipe locale surface는 `Iris/_docs/authority/tooltip_t1/layer4_recipe_locale_input_contract.json`이 결속한 별도 QG owner output에서 selected identity freeze 뒤 exact identity로 조회한다. Right-click은 기존 translation route를 유지한다.

`Layer4Candidate`와 selector input에는 locale surface나 Menu readiness field가 존재하지 않는다. Locale-bearing `Slot` 같은 post-selection object는 selector input으로 사용할 수 없으며, identity input에 Recipe `display_by_locale`가 나타나면 missing-surface correction으로 흡수하지 않고 authority-ceiling 위반으로 fail-loud한다. KO/EN pair는 cross-locale fallback, locale별 reselection 또는 Recipe/Right-click substitution 없이 해결한다.

이 amendment는 D4 workstream의 shared-path proposal이다. Global current manifest, route, command owner와 governance status 채택은 T1-D6에 유보한다. Numeric character/byte/pixel bound를 새로 만들지 않으며 single logical line/NFC gate와 T3 actual-fit ceiling을 유지한다.

## Claim boundary

이 adoption은 offline T1 contract, deterministic identity selection, readiness attribution과 T2 boundary만 소유한다. static Tooltip Lua generation, runtime/Alt behavior, actual visual four-line fit, translation quality, upstream correction 완료, package/install, compatibility, freeze, Publish, release, Workshop 또는 deployment readiness를 주장하지 않는다.

## T2 Change 0: approved S1 title

Applicable S1 uses exactly `[{category_surface} - {primary_subcategory_surface}]` for each explicit KO/EN locale. Both labels come from the already approved D1 row. T1 hands off the completed string; T2 never rebuilds it. Classification identity, applicability/display silence, Menu relation and S2–S4 remain unchanged. Historical T1 handoffs remain immutable; the correction requires a same-subject successor lifecycle.
