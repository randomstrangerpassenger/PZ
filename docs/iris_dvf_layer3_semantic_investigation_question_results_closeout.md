# DVF-L3-03 semantic results closeout

상태: **complete — off-live DVF-L3-03 채택 완료**. 날짜: 2026-09-04. Item 전체 조사·acquisition·runtime/product 완료를 뜻하지 않는다.

## 선택·범위 (NC2)

2026-09-04 사용자 지정 질의 작업 `01a0620a-a4a0-75a0-ba48-d7199bb9485a`의 답변을 반영한 계획을 구현했다. A1은 결속된 available-source key/route 및 pending/new key의 단순 미조사 0, B1은 unique automatic rule 전수 의미 검토와 층화 표본 감사, C2는 L3-02 정의/baseline을 보존하는 별도 result authority다. 실제 source/engine/runtime dependency 때문에 unresolved인 질문은 남길 수 있고 전수 item 의미 정확성·모든 질문 해결을 뜻하지 않는다. 이번 프롬프트는 문서상 owner gate를 사전 승인했고, 검증을 단일 최종 G1에 통합하며 불필요한 추가 봉인·proof artifact를 금지했다. 과거 승인을 소급하거나 새 approval gate를 만들지 않았다.

## 구현과 소유권

`Iris/tooling/src/iris_tooling/domains/layer3/`의 source reader, 명시적 interpretation, semantic producer/model과 additive CLI/resolver를 구현했다. Raw/index 역대조, group 확장, evolved cooking, fixing, construction, inventory action 및 네 anomaly를 조사한다. Callback 정의 발견과 명시적으로 검토된 callback 집합은 분리한다. Fact ID는 semantic content와 context/dependency 기반이며 partial binding은 open question과 공존한다. Derived application 입력은 corpus에 보존하고 실제 resolver로 계산한다. 별도 application 복제나 validator/proof tree를 만들지 않았다.

음용은 갈증 감소와 조건부 tainted-water poison 증가를, skill book은 읽기 진척에 따른 조건부 XP multiplier 증가를 보존한다. Container 보관, 착용, note 기록, bandaging, hair dye, pills 복용, fabric recovery, portable-device battery supply, woodworking, repair, moving, construction을 해당 source 조건에 한정해 admission했다. Native field·recipe 참여만으로 모든 효과나 용도를 확정하지 않는다.

## 최종 subject

- Manifest: `Iris/_docs/authority/dvf/layer3_semantic_results/manifest.json`
- SHA-256: `a3416672aa47fe4c6c84d9b8e9912377adda6e20e9eb679bf2d229cb9d3456bd`
- L3-01 predecessor: `6735c3eadafaf4c4fd51ae56c8d0748d32903ee996d53ed43bca38822cf0932a`.
- L3-02 definition revision 1: `47be8947a0b18745560b1e7e2463adbe86ab878e5e9fefd461f2a838c164290e`.
- Exact target: 2,105; set SHA-256 `122ca07c483ff8e4af9ef83bfb8d28c950802a124aba1668c234bce3477b2fdb`.
- Source bindings: 216개. Exact 목록/hash, 원본 locator, observation/provenance는 corpus에 있다. upstream build 일치나 repository 밖 source 완전성은 주장하지 않는다.

| Member | SHA-256 |
|---|---|
| `Iris/_docs/authority/dvf/layer3_semantic_results/corpus.json` | `fd0e44622c7a931a8a982b757641958772b0979b518907c96b03beb1b63ddb36` |
| `docs/iris_dvf_layer3_semantic_investigation_question_results_contract.md` | `dc0fe78ac3deeb02ca9183d186e12d8a60d140a8d26c14dc1f83ba267cf222af` |
| `Iris/build/description/v2/tests/test_layer3_semantic_results.py` | `89200882a40a1b5367f763ea9f29876e7cca2eee87c15330f1b79c712a11bd19` |
| `Iris/tooling/src/iris_tooling/domains/layer3/semantic_results.py` | `3ca43a7fc0411632ba24d66a17484f239402a09bd3c047298f54277d6e11c13b` |
| `Iris/tooling/src/iris_tooling/domains/layer3/semantic_model.py` | `a7a9b031a37034429f9dbfc7e3b50f1a441fd177e6077dbc397ddfcac47220e8` |
| `Iris/tooling/src/iris_tooling/domains/layer3/source_reader.py` | `d7f5929e8cc317295ab506bbea9724d67a639db67b78730f97f4a7d6dbe8b7c5` |
| `Iris/tooling/src/iris_tooling/domains/layer3/interpretations.py` | `38f4cb87d5a1d3c10939737d780dc07fc0b2dc568ac0d28d5d34269b089e9716` |
| `Iris/tooling/src/iris_tooling/domains/layer3/investigation.py` | `84d03ae23b7293548bde672d8f55c6117920da8e86ac9e9b2e03ae3cdbe3e30f` |
| `Iris/tooling/src/iris_tooling/domains/layer3/cli.py` | `2010b23b348a19d1b055c1e9a79543d9c70544cbc16b1d80ba85936cd300a7fd` |

## 생산 집계와 잔여

아래는 같은 manifest의 생산 집계이며 성공한 G1의 실제 전체 resolver 소비 결과와 일치했다. 질문 수와 item 완료율을 혼동하지 않는다.

| 항목 | 수 |
|---|---|
| Original non-acquisition keys | 8882 |
| Current non-acquisition keys | 9982 |
| Accepted facts | 4233 |
| Partial fact가 기여하는 질문 | 3498 |
| Item complete | 0 / 2,105 |
| Acquisition not_investigated | 2,105 |

### 질문 상태

| 분류 | 수 |
|---|---|
| `investigated_unresolved` | 9900 |
| `evidence_backed_not_applicable` | 82 |

### Axis

| 분류 | 수 |
|---|---|
| `conditions` | 4700 |
| `operation` | 3578 |
| `role` | 1122 |
| `effects` | 582 |

### Scope

| 분류 | 수 |
|---|---|
| `activity:crafting` | 1396 |
| `item:direct` | 4210 |
| `activity:cooking` | 572 |
| `activity:ingestion` | 1428 |
| `activity:combat` | 322 |
| `activity:expenditure` | 226 |
| `activity:wearing` | 1096 |
| `activity:world_work` | 276 |
| `activity:storage` | 138 |
| `activity:reading` | 318 |

### Fact kind

| 분류 | 수 |
|---|---|
| `effect` | 110 |
| `direct_function` | 1141 |
| `condition` | 1850 |
| `context_role` | 566 |
| `use_context` | 562 |
| `constraint` | 4 |

### Carry-forward

| 분류 | 수 |
|---|---|
| `retained` | 8882 |
| `newly_required` | 1100 |

### Pending 처분

| 분류 | 수 |
|---|---|
| `pending_with_blocker` | 5217 |
| `applicable` | 550 |

### Pending profile (중복 item 허용)

| 분류 | 수 |
|---|---|
| `cooking` | 1879 |
| `world_work` | 2085 |
| `crafting` | 1779 |
| `combat` | 4 |
| `expenditure` | 4 |
| `ingestion` | 4 |
| `reading` | 4 |
| `storage` | 4 |
| `wearing` | 4 |

### 질문별 residual blocker

| 분류 | 수 |
|---|---|
| `RecipeManager_and_opaque_callbacks` | 1396 |
| `runtime_predicate_and_indirect_dispatch` | 4210 |
| `EvolvedRecipe_runtime_eligibility` | 572 |
| `IsoGameCharacter.Eat_and_OnEat_dispatch` | 1322 |
| `HandWeapon_attack_reload_and_character_state` | 284 |
| `DrainableComboItem.Use_and_device_specific_consumers` | 224 |
| `Clothing_protection_insulation_and_body_state` | 1080 |
| `loader_or_declaration_identity` | 80 |
| `FixingManager_stage_engine_and_world_object_state` | 276 |
| `ItemContainer_capacity_and_transfer_state` | 138 |
| `ISReadABook_SkillBook_and_ReadLiterature` | 318 |

Available-source membership은 exact target × A~E의 10,525 attempt와 각 question/universe/pending의 attempt refs로 계산한다. Route별 source_capability observation refs가 source path/hash를 연결한다. 기존 key는 모두 retained, 추가 key는 source finding과 contributor를 가진 newly_required다. Profile pending은 5,767 pair를 보존하며 550개 applicable, 5,217개 pending_with_blocker다. 합산한 pair 수를 item 완료율로 쓰지 않는다.

`Base.Bag_PistolCase`, `Base.Lemongrass`, `Base.NoiseMaker`는 exact raw declaration이 없고 near-name/literal 검색으로 alias를 확정할 수 없어 unresolved다. `Base.ShotgunCase1`은 두 raw declaration을 모두 보존하며 loader winner가 없어 unresolved다. 해당 native pending과 direct/gap은 유지한다. 유사 model/display 이름이나 case-fold 검색은 identity 변경 근거가 아니다.

## B1 내용 감사

Unique rule의 전제·소비 동작·변환·예외를 검토했다. 공통 recipe callback 해석은 food, predicates, devices, materials, experience, shotgun의 명시적 callback 집합을 소유한다. Inventory action 해석은 해당 menu caller edge를 대상으로 하며 UI 클래스 전체 메서드나 runtime event registry를 감사한 것으로 확대하지 않는다.

표본은 Apple, Dogfood/Opened form, BucketWaterFull, BookTrapping1, Hammer, Plank, Woodglue, Shirt_Denim, Notebook, DishCloth, Battery, Bandage, HairDyeBlue, Pills, Bag_Schoolbag, Shotgun이다. Food/tool/weapon/clothing/multi-use/low-information 및 A~E, positive/scoped-negative/unresolved를 포함한다. Tainted-water 임계, 읽기 multiplier, stage/branch construction, fabric recovery, multi-context role와 qualifier binding을 검토했다. Rule/fact/attempt refs와 검토 한계는 corpus의 review에 보존한다. 모든 item의 수작업 의미 정확성을 주장하지 않는다.

## 최종 G1

첫 G1: exit `1`, `1 failed in 2.65s`. Subject `0925016a702f781d3dc6328d7b5be8f999d1ba669008dbc3ac83d53660151f79`에서 테스트의 recipe 순회 변수가 manifest binding을 덮어써 `AttributeError`가 발생했다. 첫 item의 소비에서 중단되어 전체 소비를 완료하지 못했다. 변수명을 수정하고 같은 corpus를 재생산하지 않은 채 테스트 member와 manifest 연결만 갱신했다. 실패를 PASS로 취급하지 않았다. 같은 G1을 재실행했고 최종 subject `a3416672aa47fe4c6c84d9b8e9912377adda6e20e9eb679bf2d229cb9d3456bd`에서 **exit 0, `1 passed, 19 subtests passed in 3.40s`**로 통과했다. 정상 완료한 전체 corpus 소비는 이 실행 한 번이며 성공 뒤 추가 confidence 실행은 하지 않았다.

`G1_EXIT_CODE=0`. 이 성공 subject에 한정해 current route를 `adopted`로 전환했다. Corpus와 manifest member bytes는 G1 이후 변경하지 않았다.

작업 위치: `C:/Users/MW/Downloads/coding/PZ`.
환경: `IRIS_LAYER3_SEMANTIC_MODE=adoption`, `IRIS_LAYER3_SEMANTIC_BASELINE=C:/Users/MW/Downloads/coding/PZ/.tmp/semantic/baseline.json`, `IRIS_LAYER3_SEMANTIC_MANIFEST=Iris/_docs/authority/dvf/layer3_semantic_results/manifest.json`. 실행 후 기존 값으로 복원했다.

```powershell
uv run --project .\Iris\tooling --no-sync python -m pytest .\Iris\build\description\v2\tests\test_layer3_semantic_results.py -q -p no:cacheprovider --round3-contract=diagnostic --round3-additional-source=Iris/build/description/v2/tests/test_layer3_semantic_results.py
```

실제 전체 corpus를 한 번 소비해 입력·accepted fact/provenance·question/partial binding·carry-forward·pending·source/member·명시적 보호 경계를 함께 검사한다. 작은 독립 fixture는 case identity, stale binding/정정, context/qualifier, terminal/negative, acquisition 무단 해결, 함수 발견≠의미 검토, CLI/fallback과 결정성을 검사한다. 중간 테스트·기존 전체 suite·runtime/package 테스트는 실행하지 않는다.

생산 준비 중 apostrophe lexer 처리를 수정했고, 등록 helper의 taxonomy 포함 누락을 수정했다. 이는 corpus/등록 생산 실패이며 G1 PASS로 표현하지 않는다. 일회성 helper는 정규 validator나 새 validation authority가 아니다.

## 한계와 후속

- `validated`: 위 exact G1의 exit 0. 전체 structured corpus 소비, A1 accounting, B1 기록 결속과 미처리 결함 없음, typed facts/provenance/relations, target/key/pending 보존, source/member/readpoint 및 명시적 33개 보호 파일·기존 config/product locator. B1의 내용 판단은 기록한 unique rule/표본 범위이며 자동 구조 검사가 전수 의미 정확성을 증명한 것은 아니다.
- `out_of_scope`: acquisition truth, KO/EN 표현·S2·Menu/Tooltip, Lua/Java/JS runtime 변경·검사, package/install, PZ 실행·멀티플레이·장시간 호환성, release readiness.
- `unvalidated_but_in_scope`: 표본 밖 전수 의미 정확성, source snapshot/upstream build 완전성, 동적 registry/receiver와 engine 효과. 결속 source에서 수행한 해석과 추가 source가 필요한 잔여를 구분한다.
- Byte 보존은 시작 baseline의 명시적 33개 파일·14 selected generation member와 기존 config/product locator 부분에 한정한다. 전체 runtime/package tree parity나 다른 checkout/OS의 bytes를 검증하지 않는다.
- L3-04: acquisition은 별도 authority로 병행한다. L3-03 adopted를 acquisition 전체 작업의 선행 gate로 추가하지 않는다. L3-05: partial facts·조건·open question·first-contact를 구조화 입력으로 받고 대표 의미/전역 문장 수를 강제하지 않는다. L3-06: runtime/product adoption은 deferred다.
- 사용자 기존 문서 삭제와 다른 작업 변경은 rollback하지 않는다. 최종 corpus/member 및 단일 closeout을 보존했다. `.tmp/semantic/assemble.py`, `baseline.json`, `g1.txt` 삭제와 빈 임시 폴더 정리를 시도했으나 플랫폼 자동 승인 검토가 명령을 `blocked by policy`로 거부했다. 명령은 실행되지 않았고 별도 상세 사유는 제공되지 않았다. 보안·권한 확인을 우회하지 않아 세 파일을 남겼다. 이들은 일회성 작성 helper·시작 baseline·실행 로그이며 canonical validator나 새 validation authority가 아니다. 정리 보류는 검증된 corpus 채택을 바꾸지 않는다.
