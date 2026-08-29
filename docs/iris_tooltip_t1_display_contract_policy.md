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

표시 가능한 행은 최대 네 개다. owner가 증명한 `legitimate_absence` 행은 표시에서 compact할 수 있지만 semantic slot ID와 S1→S4 상대 순서는 유지한다. identity, authority 또는 locale surface 결손은 absence로 compact하지 않는다. logical row 수 `0~4`와 embedded newline 금지만 T2 hard gate이며 실제 pixel/font/UI-scale fit은 T3 범위다.

## 입력 경계

- Layer 2는 Classification owner가 제공한 resolved classification/category/primary-subcategory identity와 KO/EN surface만 소비한다. raw tag scan, runtime resolver 복제와 `Misc.9-A` raw fallback 승격을 금지한다.
- Layer 3는 owner-approved single `core_description` fact identity와 KO/EN single-line surface만 소비한다. rendered body 자르기, 요약, 재작성, 여러 core fact 합성과 acquisition paragraph 승격을 금지한다.
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

## Claim boundary

이 adoption은 offline T1 contract, deterministic identity selection, readiness attribution과 T2 boundary만 소유한다. static Tooltip Lua generation, runtime/Alt behavior, actual visual four-line fit, translation quality, upstream correction 완료, package/install, compatibility, freeze, Publish, release, Workshop 또는 deployment readiness를 주장하지 않는다.
