# Iris Current / Historical Physical Separation 및 Repository Lightweighting Implementation Plan

상태: `revised_for_post_hardening_execution / execution_ready_after_hardening_integration / S0_exact_main_commit_pending`

코드베이스 조사 readpoint: drafting predecessor `main` / `0311718b2334fc3b45908b2f0d2117c7dc57569a`; 실행 S0는 public-text hardening documentation carrier `0329c04a505f4297ab8fdec86e4cb9521506d74d`를 포함한 post-integration `main`의 exact commit/tree로 고정한다.

작성 기준일: 2026-08-26

상위 근거: `docs/Philosophy.md`, `docs/EXECUTION_CONTRACT.md`, `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/PLAN_TEMPLATE.md`, 사용자 제공 `Iris Current / Historical Physical Separation 및 Repository Lightweighting Roadmap` 및 최신 `Plan — 종합 검토안`

주의: 조사 시점 working tree에는 이 계획과 무관한 `docs/ARCHITECTURE.md`, `docs/DECISIONS.md` 수정 및 `.codex-worktrees/` 변경이 존재한다. 이 계획은 해당 변경을 baseline authority로 채택하거나 수정·정리하지 않는다. 실행 전 public-text hardening을 `main`에 통합하고 새 exact commit/tree를 S0로 채택해야 한다. hardening branch에서 확인된 current locator는 `responsibility_refactor_environment_terminal_v15.json`이며 해당 external root와 immutable receipt가 존재한다. S0에서 이 binding이 유효하면 Change 0E는 `not_required(existing_environment_validated)`로 닫고 새 environment authority를 만들지 않는다. 이후 W0는 tracked 구현을 검증하는 exact clean Git worktree와 ignored/untracked/filesystem-only payload를 실제로 보유한 local custody checkout을 별도 subject로 측정한다. W0에서 genuine identity conflict, unresolved current consumer 또는 baseline gate failure가 발견되지 않으면 미리 채택된 disposition rule에 따라 Change 1B를 봉인하고 같은 실행에서 Change 2 이후로 진행한다.

## 1. Objective

Iris repository의 물리 역할을 다음 네 경계로 분리한다.

1. repository-local **current authority**: current source, runtime data, installed offline tooling, current contracts/manifests, current-required compact evidence와 최소 재현 fixture
2. repository-external **historical/reproduction archive**: historical staging, superseded attempt payload, historical evidence CAS, raw ledger, 과거 validation/playtest 결과와 predecessor evidence
3. repository-external 또는 재생성 가능한 **generated result**: build/run output, package, report, diagnostics와 temporary result
4. repository-local이 아닌 **local cache/residue**: `.venv`, `__pycache__`, `.pyc`, `.tmp_tests`, pytest/cache/log와 분석 도구 cache

목표는 source line 수를 임의로 줄이는 것이 아니라, current execution이 historical payload의 repository-local 존재 또는 external archive restore에 의존하지 않는 구조를 만드는 것이다. 완료 시 current clean checkout은 compact current evidence만으로 fail-closed full gate와 package projection을 수행하고, historical payload는 repository 밖에서 hash/inventory/restore 계약으로만 복구한다.

이 계획은 다음 개념적 흐름을 강제한다. 실제 실행 권위는 아래 번호가 붙은 Change와 progression rule이며, 이 요약 흐름이 Change 번호의 선후관계를 재정의하지 않는다.

```text
S0: public-text hardening을 포함한 exact post-integration main commit/tree 채택
-> Change 0E: S0의 committed external environment가 실제로 invalid일 때만 environment-only authority reseal
-> Checkpoint A: clean locator subject에서 baseline full gate Run A/B/comparator PASS
-> Change 1A: W0 dual-subject census + normalization/broader-closure + pre-adopted disposition 검증
-> Change 1B: deterministic authority/sequencing amendment commit
-> Change 2: tracked residue와 non-Git custody cleanup 분리
-> Change 3: runtime/generated authority 단일화
-> Change 4: old tooling predecessor current binding 제거
-> Change 5: bounded current evidence capsule + current binding 전환
-> Change 6: historical docs/generated output current surface 분리
-> Change 7A: deterministic archive implementation/authority 확정
-> Checkpoint B: Changes 3–7A successor tree의 exact full gate Run A/B/comparator PASS
-> Change 7B: Layer 3 포함 historical archive 생성·검증·복원·증빙
-> Checkpoint C: disposable synthetic candidate에서 기존 canonical full gate Run A/B/comparator PASS
-> Change 8: repository-local historical payload 삭제
-> Change 9: ignore/search policy 단순화
-> Change 10 / Checkpoint D: exact clean-checkout terminal validation + final census + independent review
```

완료 판정은 예상 용량 목표가 아니라 exact terminal subject의 current closure, archive 복구 가능성, full-gate 결과와 final census를 기준으로 한다.

---

## 2. Scope

이 계획은 다음 범위를 포함한다.

* `Iris/build/description/v2/staging/`의 current-required payload와 historical/reproduction payload 분리
* `Iris/build/description/v2/evidence/`의 repository-local CAS/reference를 current route에서 분리하고 historical store로 외부화
* `Iris/_docs/`의 broad current glob을 exact current allowlist로 교체하고 historical/raw evidence를 외부화
* `Iris/output/`과 `Iris/build/description/v2/output/`의 current seed, runtime source, generated result, stale duplicate를 consumer별로 재분류
* `IrisClassifications.lua`, `IrisContextOutcomes.lua`, `IrisData.lua`의 generator/output/runtime authority 관계 정리
* `Iris/build/description/v2/tools/build/` predecessor의 current consumer를 `Iris/tooling/src/iris_tooling/` successor로 재결속하고 zero-consumer predecessor를 제거
* inactive Layer 3 generation 3개와 legacy fixed chunk 11개의 source rollback hold를 명시적으로 supersede한 뒤 물리 제거
* Iris-owned `.venv`, `__pycache__`, `.pyc`, `.tmp`, `.tmp_tests`, `.dvf_tmp`, cache, log와 W0/1B-approved root exact 검증 residue 제거
* repository root `.tmp/` 중 local custody subject에서 Iris가 소유한 exact generated/cache selection만 별도 소유권 확인 후 제거
* full gate가 disposable execution-checkout local path로 선언한 repository-root `.dvf_tmp/`의 source/custody residue를 W0 subject별로 판정하고 terminal clean source에서 exact absence 검증
* `.gitignore`와 `.rgignore`를 directory-role 중심으로 단순화하고 ignored current dependency를 0으로 만들기
* archive locator, SHA-256, compact inventory, explicit restore/verify 계약과 closeout census 작성
* current full-repository gate, installed tooling, Lua syntax, package parity와 clean-checkout validation 재봉인

### Explicitly Out Of Scope

* `.git` history rewrite, `git filter-repo`, release tag 또는 과거 commit 변경
* `Pulse_All_Source.txt`와 같이 Iris가 소유하지 않는 다른 모듈의 local/generated payload 정리
* `.codex-worktrees/`의 merge, archive 또는 삭제. 조사 시점 tracked locator 4개에는 사용자 변경이 있고 physical worktree에도 main보다 앞선 작업이 있을 수 있다.
* Echo, Fuse, Nerve, Pulse, Frame, Cortex, Canvas source와 authority 변경
* Iris public fact, 분류, 한국어/영어 문구, Layer 3 의미 또는 Layer 4 상호작용 내용 재설계
* `public_text_quality_acceptance.py`와 `run_dvf_3_3_korean_prose_naturalization.py`의 추가 책임 분해. 이 계획에서는 physical placement와 dependency만 다룬다.
* repository 전체 documentation 정보구조 재설계 또는 `docs/새 폴더/` 정리
* release, RTC, Publish, Workshop 또는 deployment 승인
* 모든 외부 모드 조합의 compatibility sweep
* repository-wide owner가 필요한 `graphify-out/`와 `console_log.txt` 정리. 두 surface는 Iris closeout 뒤 별도 계획/승인으로 다루며 Iris 완료 조건이나 감축량에 포함하지 않는다.
* `.codex-worktrees/`, 다른 module의 cache, unrelated repository-root `.pytest_cache`/`__pycache__`/`.pyc` 정리. 단, W0가 exact Iris-owned tracked row로 채택한 root `.tmp`/`.pyc`는 Change 2A 범위가 된다.

---

## 3. Non-Goals

* physical byte 감소를 위해 current product/runtime source를 압축하거나 난독화하지 않는다.
* current test identity나 fail-closed branch를 용량 감소 수단으로 삭제하지 않는다.
* full repository gate direct binding과 broader manifest/gate closure를 하나의 denominator로 합치지 않는다.
* historical evidence의 존재를 current source authority로 승격하지 않는다.
* external archive를 current build, current gate 또는 package command의 fallback dependency로 만들지 않는다.
* generated output을 rollback 전략이라는 이유로 repository에 중복 보존하지 않는다.
* tracked historical payload 삭제를 local cache 정리와 같은 low-risk 작업으로 취급하지 않는다.
* source predecessor 전체 크기를 현재 확인된 zero-consumer subset과 동일시하지 않는다.
* 예상치 `Iris tracked 약 75 MB`, `physical 약 50~80 MiB`를 hard PASS threshold로 사용하지 않는다.
* repository byte 감소를 runtime 성능, FPS, memory 또는 실제 GPT/Codex token 절감률로 환산하지 않는다.
* clean worktree 또는 sparse/locally-deleted working tree에 어떤 파일이 없다는 사실을 local custody deletion이나 exact Git-object absence 증거로 사용하지 않는다.
* 서로 다른 checkout/root의 physical delta를 빼거나 합쳐 repository 감축량으로 주장하지 않는다.

---

## 4. Assumptions

### 4.1 Constitutional and authority assumptions

* `docs/Philosophy.md`가 최상위 권위다. Iris는 근거 기반 정보를 읽기 전용으로 표시하며 게임 상태를 변경하지 않고, PZ runtime은 100% Lua를 유지한다.
* `docs/DECISIONS.md`의 current IAR 판정은 Stateful Artifact Registry product architecture의 `FULL_RETIREMENT`와 Layer 1–5 active product consumer 0을 뜻한다. 재사용 가능한 public-text assessment producer와 repository validation evidence는 별도 current/historical 역할을 가질 수 있다.
* `docs/ARCHITECTURE.md`의 installed `iris_tooling` ownership, pointer-selected Layer 3 package projection, stable Lua facade와 clean-checkout receipt 경계를 유지한다.
* 기존 W1 decision은 inactive Layer 3 source와 historical/staging/evidence payload의 physical hold를 보존한다. 따라서 실제 destructive wave 전에 repository-local hold를 external immutable preservation으로 supersede하는 owner decision을 `docs/DECISIONS.md`에 먼저 채택해야 한다.
* sealed artifact를 외부화할 때 bytes와 historical trace를 보존하되, repository-local path의 존재를 계속 보존하는 것으로 해석하지 않는다. 이 해석은 Change 1의 명시적 successor decision 없이는 적용하지 않는다.

### 4.2 Inspected repository baseline

다음 값은 2026-08-26 working-tree read-only census다. tracked 값은 `git ls-files -- Iris`, ignored 값은 `git ls-files --others --ignored --exclude-standard -- Iris`, untracked 값은 `git ls-files --others --exclude-standard -- Iris`, physical 값은 실제 파일 길이 합계다. 이 checkout은 `core.autocrlf=true`, `core.eol` unset이다.

| Surface | Physical | Tracked | Ignored | Untracked / FS-only | 계획상 의미 |
| --- | ---: | ---: | ---: | ---: | --- |
| `Iris/` 전체 | 8,265 files / 868.92 MiB | 5,467 / 648.09 MiB | 2,797 / 220.83 MiB | 0 / 1 | W0/W10 동일 방식 재측정 |
| `description/v2/staging` | 4,645 / 558.76 MiB | 3,402 / 377.61 MiB | 1,243 / 181.16 MiB | 0 / 0 | 가장 큰 historical/reproduction 분리 대상 |
| `description/v2/evidence` | 240 / 177.74 MiB | 240 / 177.74 MiB | 0 | 0 / 0 | 238 CAS objects + 2 references |
| `Iris/_docs` | 739 / 42.85 MiB | 737 / 42.80 MiB | 2 / 0.05 MiB | 0 / 0 | broad current authority rule 제거 후 분리 |
| `description/v2/output` | 31 / 20.98 MiB | 7 / 9.21 MiB | 24 / 11.78 MiB | 0 / 0 | current consumer와 regenerated output 구분 |
| `Iris/output` | 47 / 5.62 MiB | 47 / 5.62 MiB | 0 | 0 / 0 | current seed/fixture와 disposable output 구분 |
| old `tools/build` | 737 / 16.53 MiB | 267 / 6.49 MiB | 470 / 10.04 MiB | 0 / 0 | current reference 0 후 tracked/ignored disposition 분리 |
| `Iris/tooling` successor | 646 / 8.68 MiB | 56 / 0.85 MiB | 590 / 7.83 MiB | 0 / 0 | ignored 대부분 local environment/cache; terminal env는 repository 밖에 생성 |
| `description/v2/tests/.tmp` | 6 physical | 0 | 5 | 0 / 1 | FS-only row는 nested `.git` marker; Change 2B owner decision 필요 |
| `description/v2/frozen_predecessor_inputs` | 35 / 1,632,848 B | 35 / 1,632,848 B | 0 | 0 / 0 | current full gate가 내부 current-route manifest digest를 고정하므로 보호 대상 |
| `description/v2/owner_inputs` | 37 / 2,661,731 B | 37 / 2,661,731 B | 0 | 0 / 0 | current round 문서 참조가 있어 blanket archive 금지; W0 row별 처분 필요 |
| `description/v2/reviewer_inputs` | 10 / 26,675 B | 10 / 26,675 B | 0 | 0 / 0 | historical archive 또는 retained exception을 W0가 row별 선언 |
| `Iris/build/tests` | 8 / 32,832 B | 6 tracked | 2 ignored | 0 / 0 | executable test와 local residue가 공존; Change 4 gate surface 및 residue census 대상 |
| `description/v2/data` | 45 / 8,090,444 B | 45 / 8,090,444 B | 0 | 0 / 0 | authority manifest glob 및 full-gate exact paths가 있는 current data surface; 보호 집합 |
| Layer 3 generations | 56 / 9.23 MiB | 56 / 9.23 MiB | 0 | 0 / 0 | current 1개 1,954,408 bytes 유지 |
| Layer 3 fixed chunks | 11 / 0.92 MiB | 11 / 0.92 MiB | 0 | 0 / 0 | inactive predecessor 제거 후보 |
| `Iris/test` | 36 physical | 31 tracked | 5 | 0 / 0 | top-level current test owner; W0 closure에 포함 |
| `Iris/evidence` | 16 physical | 15 tracked | 1 | 0 / 0 | top-level evidence owner; archive 대상 CAS와 혼동 금지 |
| `Iris/input` | 8 physical | 8 tracked | 0 | 0 / 0 | legacy/current input 여부를 `main.py` 결정에 결속 |
| `Iris/_dev` | 8 physical | 8 tracked | 0 | 0 / 0 | package/runtime overlay consumer 확인 |
| `Iris/_archive` | empty directory | 0 | 0 | 0 / 0 | Change 2B에서 empty/non-reparse 확인 후 제거; Change 9에서 obsolete rule 제거 |

Repository-root adjacent 관측값은 `.tmp/` 1,463 files / 83,020,784 bytes(tracked 18, ignored 1,444), `graphify-out/` tracked 1,754 files / 23,518,192 bytes, `console_log.txt` tracked 842,314 bytes, `Pulse_All_Source.txt` ignored 102,806,164 bytes, `.codex-worktrees/` 약 1.63 GB다. 이 계획은 `.tmp/` 중 Iris 소유 exact selection만 local custody cleanup 후보로 삼는다. `graphify-out/`, `console_log.txt`, `Pulse_All_Source.txt`, `.codex-worktrees/`는 모두 이 계획의 destructive scope 밖이다.

사용자 제공 roadmap의 `113 vs 196`, staging `18 vs 124`, `_docs` `6 vs 43`은 서로 다른 denominator다. 위 physical/tracked census와도 서로 대체하지 않는다. W0는 다음 집합을 별도로 재산출한다.

* full repository gate direct path binding
* current authority manifest path/glob expansion
* required validation/artifact binding
* active Python/Lua/PowerShell dynamic consumer closure
* clean-checkout seed/bootstrap closure
* filesystem-only/reparse-point closure와 local custody path containment

### 4.3 Code-informed findings

* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`에는 staging direct-bound path가 18개, 합계 18,829,290 bytes(17.96 MiB) 있다. 이 가운데 G4/G5가 raw content를 읽는 path와 existence/hash/identity만 소비하는 path를 구분하지 않고 전부 복사하면 capsule 자체가 새 대형 payload가 된다. `g5_required_evidence.evidence_bindings`, `handoff_path_bearing_constituents`, `g4_required_paths` 및 excluded historical test path의 operation class를 먼저 산출한다.
* 같은 contract는 `test_iar_public_text_assessment.py`의 direct dependency로 old `run_iar_public_text_assessment.py`와 `validate_iar_public_text_assessment.py`를 명시한다. 반면 실제 assessment 구현은 이미 `Iris/tooling/src/iris_tooling/build/iar_public_text_assessment.py`에 있다.
* `Iris/tooling/src/iris_tooling/build/dvf_3_3_generation_contract.py`의 `GENERATOR_IMPLEMENTATION_FILES`는 successor package 안에 있으면서도 old `tools/build` 7개 경로를 identity input으로 사용한다. old tree removal 전에 이 current binding을 package 경로로 재결속해야 한다.
* `Iris/build/main.py`는 tracked current manifest entrypoint지만 clean checkout에서 import하는 `phase0_validation`과 `phase1_extraction`이 missing이고, `phase2_rules`, `phase3_output`, `phase4_tests`는 local custody checkout의 ignored-only 파일이다. 따라서 clean checkout에서 실행 가능한 current entrypoint가 아니다. 동시에 output의 75,143-byte stale full-table `IrisData.lua`를 371-byte runtime thin adapter에 배포할 수 있어 그대로 보존하거나 실행해서도 안 된다. `iris_tooling classification`은 Fixing/Moveables/Recipe index만 생성하므로 이 entrypoint의 동등 successor로 간주하지 않는다.
* `Iris/output/IrisClassifications.lua`와 runtime `IrisClassifications.lua`는 현재 SHA-256과 111,083 bytes가 동일하다. `Iris/output/context_outcomes.lua`와 runtime `IrisContextOutcomes.lua`도 8,688 bytes로 동일하다. 동일본이라는 사실은 두 위치가 모두 authority라는 뜻이 아니며 generator result와 installed runtime source 관계를 명시해야 한다.
* current Layer 3 pointer는 `dvf33-028a3968...7145e9`를 선택한다. 이 generation은 14 files / 1,954,408 bytes이고, 다른 세 generation은 각각 1.95~2.89 MB의 inactive predecessor다.
* `Iris/tools/package_iris.ps1`은 이미 pointer-selected generation만 package에 투영하고 inactive generation/fixed chunk를 제외한다. source cleanup은 package logic 재설계가 아니라 source predecessor hold 해제와 negative guard 갱신이다.
* `Iris/validation/clean_checkout/evidence/`는 23 files / 약 0.178 MiB의 compact current validation evidence 선례를 제공한다. 별도의 repository-wide capsule framework를 만들지 않고 이 owner 경계 아래 versioned current-required capsule을 둔다.
* `repository_evidence_lightweighting_output_policy.json`은 deterministic ZIP deflate level 9, canonical member metadata, external opaque locator와 restore-before-delete를 요구한다. `migrate_repository_evidence.py`의 cold archive writer는 level 9를 구현하지만 ignored source disposal에 한정되고, `execute_artifact_lifecycle.py`는 tracked delete ancestry/check를 구현하지만 ZIP level 6과 machine-specific absolute receipt path를 사용한다. 둘 중 하나를 그대로 재사용하지 않고 정책에 맞는 shared deterministic archive successor를 먼저 만든다.
* `.gitignore`는 1,280 lines, Iris rule 1,224개, Iris negation 1,097개다. 현재 tree는 broad ignore 후 개별 artifact를 다시 허용하는 구조이므로 physical separation이 끝난 뒤에만 단순화한다.
* `Iris/build/description/v2/tools/`는 physical 774 / tracked 275 / ignored 499 files이며 `tools/build/`만 조사해서는 consumer/helper/fixture를 누락한다. `Iris/build/description/v2/tests/.tmp/`에는 local residue가 있고 top-level `Iris/test/`에는 current adaptive-interaction/Layer 4 projection tests가 있다.
* tracked byte materialization은 `.gitattributes`와 Git config에 영향을 받는다. 조사 checkout은 `core.autocrlf=true`, `core.eol` unset이고, historical payload 일부만 `-text`/`text eol=lf`가 고정되어 있으며 attempt-0024 direct-bound rows와 planned capsule destination은 explicit normalization이 없다. 따라서 tracked identity는 worktree SHA가 아니라 Git blob bytes/ID를 authority로 사용해야 한다.
* `Iris/` physical 8,265와 tracked+ignored 8,264의 차이 1개는 untracked file이 아니라 `Iris/build/description/v2/tests/.tmp/uv-cache/sdists-v9/.git` filesystem-only VCS marker다. enumeration 또는 cleanup이 이 marker를 조용히 건너뛰면 census는 실패다.
* `Iris/build/description/v2/frozen_predecessor_inputs/`는 legacy처럼 보이는 이름과 달리 `full_repository_gate.json`이 `dvf_3_3_registry_authority_canonical_closure/current_route/manifest.json`을 `b77720204c6e12f46c122d52c5602eefda311a6f5379b055aee0b843f822dfa2`로 고정하고 `hermetic_test_fixture`로 분류한다. 이 subtree는 historical 후보가 아니라 current-required gate fixture이며 Change 7/8 archive/delete selection에서 제외한다.
* `Iris/build/description/v2/owner_inputs/` 일부는 현재 round 문서에서 참조된다. `owner_inputs/`와 `reviewer_inputs/`는 이름만으로 일괄 분류하지 않고 W0 operational-consumer closure에 따라 각 row를 `historical_archive` 또는 versioned `retained_exception`으로 닫는다.
* `Iris/build/tests/`와 `Iris/build/description/v2/data/`는 기존 범위에서 빠져 있던 별도 subtree다. 전자는 current gate/test surface와 ignored residue를 함께 가지며, 후자는 authority manifest의 `data/**` glob과 full gate의 IAR/Korean-prose exact paths에 결속된 current data surface다. W0는 둘의 별도 denominator와 exact protected closure를 산출한다.
* drafting predecessor `0311718b`의 committed environment locator는 부재한 `terminal_v4` root를 가리켰다. 그러나 public-text hardening carrier `0329c04a`의 current locator는 `responsibility_refactor_environment_terminal_v15.json`을 가리키며 2026-08-26 확인 시 external root와 immutable receipt가 모두 존재한다. 실행 S0는 hardening 통합 뒤 locator/record/receipt/root와 package-source tree를 다시 검증한다. 모두 유효하면 Change 0E는 `not_required(existing_environment_validated)`이며, invalid할 때만 `environment_authority_unavailable`과 implementation regression을 분리한 conditional reseal을 수행한다.
* Windows PowerShell 5.1.26100.9168의 .NET Framework `System.IO.Path`에는 `GetRelativePath`가 없다. terminal residue normalizer는 `GetFullPath` 후 separator-bound subject-root prefix를 `OrdinalIgnoreCase`로 검증·제거하는 구현을 사용하며, prefix mismatch/rooted/`..` 결과를 계속 fail-closed한다.

### 4.4 Adopted plan decisions

이 plan이 승인될 경우 다음 구현 결정을 사용한다.

1. **Commit ordering**: current evidence raw bytes 추가와 G4/G5/manifest rebinding은 같은 commit에 둔다. predecessor staging 삭제는 archive manifest·verify·restore evidence가 먼저 commit된 뒤 별도 후속 commit에서 수행한다. 따라서 어떤 commit도 missing current dependency 상태가 되지 않는다.
2. **Current evidence capsule**: `Iris/validation/clean_checkout/evidence/current_required_v1/`을 current clean-checkout owner가 소유한다. 18개 direct-bound 입력 각각을 `content_read`, `hash_only`, `existence_only`, `path_embedded`로 분류하고, raw verification claim을 current gate가 계속 소유하는 row만 raw bytes를 보존한다. 나머지는 versioned successor contract의 canonical digest/size/approved summary와 logical source identity로 결속한다. **2,359,296 bytes(2.25 MiB)는 default hard ceiling이다.** W0가 증명한 최소 raw current bytes가 이를 넘으면 자동 exception이나 retained keep으로 흡수하지 않고 `blocked(reason=current_capsule_hard_ceiling_requires_owner_scope_expansion)`로 닫는다. budget을 맞추기 위해 raw-evidence claim을 암묵적으로 약화하지 않는다.
3. **Historical restore boundary**: current gate/build/package는 external archive를 자동 복원하지 않는다. restore는 별도 명시적 historical/reproduction command에서만 수행한다.
4. **Archive locator**: repository에는 machine-specific absolute path가 아니라 opaque `store_identifier`, archive SHA-256, archive bytes, member inventory digest, restore/verify command contract만 남긴다.
5. **Root classification adopted disposition**: `Iris/build/main.py`는 clean checkout에서 required phase module이 존재하지 않고 current supported entrypoint로 실행될 수 없는 broken legacy entrypoint이므로 **C — current authority에서 폐기**를 채택한다. W0는 이 전제를 fresh consumer census로 검증하며 operational current consumer가 새로 발견되면만 `blocked(reason=unexpected_current_main_consumer)`로 중단한다. 새 동등 successor를 구현하거나 missing phase module을 tracked current로 복구하지 않는다. 필요한 classification/context-outcome producer는 각 existing supported owner/CLI로 보존하며 `iris_tooling classification`을 `main.py` 전체의 동등 successor라고 오기하지 않는다. `IrisData.lua` stale full-table deploy는 제거한다.
6. **Evidence authority transition**: predecessor `raw_repository_evidence_v1`과 successor `current_capsule_attestation_v2`는 같은 claim이 아니다. repository-local historical raw availability claim은 Change 1B의 deterministic adoption record로 supersede하고, current gate는 capsule attestation/migration receipt를, historical archive verifier는 raw recovery/identity를 소유한다. `behavior/evidence-preserving parity`가 아니라 approved authority transition으로 기록한다.
7. **Layer 3 rollback**: inactive generation/fixed chunk는 Git history만으로 보존하지 않는다. Change 7에서 mandatory external archive의 exact logical paths, hashes, restore parity를 먼저 증명하고 증빙 commit을 만든 뒤에만 Change 8에서 제거한다. current route는 current pointer-selected generation 하나만 repository source로 요구한다.
8. **Archive profile**: existing policy의 deterministic ZIP, deflate level 9, canonical metadata/order는 필수다. successor profile은 ZIP 내부의 unique `objects/<sha256>` bodies와 logical path-to-object manifest를 사용하는 `content_addressed_zip_v2`로 이 plan에서 채택한다. Change 1B는 W0 exact selection과 이 profile의 적용 대상을 봉인하며 profile 자체를 다시 선택하지 않는다. restore는 원래 logical path tree를 정확히 재구성하고 duplicate logical path, hash mismatch/missing object를 fail-closed한다.
9. **Repository-local successor overhead ceiling**: 이 plan 도입 이후 repository에 새로 남는 current metadata, validation code, compact evidence와 closeout docs의 합계는 `max(2 MiB, tracked removal bytes의 0.5%)`를 넘을 수 없다. `successor_overhead_bytes`는 S0 대비 새 tracked file bytes와 retained tracked file의 양수 byte delta 합계로 계산한다. current capsule raw member bytes, external archive/object/inventory/receipt, 삭제 또는 축소된 file의 음수 delta는 이 수치와 상계하거나 중복 합산하지 않고 별도 domain으로 보고한다. W0/W10 item-level 원문, 일회성 probe script/result와 allocation ledger는 repository-external로 유지한다. ceiling 초과는 자동 exception이 아니라 `blocked(reason=repository_local_successor_overhead_ceiling_exceeded)`다.
10. **Byte identity**: tracked row의 authority bytes는 exact commit의 Git blob bytes(`git cat-file blob`)이고, ignored/untracked/filesystem-only custody row만 filesystem bytes다. worktree bytes는 physical census 관측값일 뿐 tracked raw identity가 아니다. repository-local capsule raw destination은 `.gitattributes`에서 `-text`로 고정하고, external ZIP writer는 authoritative input bytes를 text transformation 없이 object member로 기록한다.

### 4.5 Execution assumptions

* tracked implementation subject는 user dirty state가 없는 dedicated clean Git worktree다. tracked edits, clean validation, commit ancestry와 package source identity는 이 root에서만 판단한다.
* local physical custody subject는 ignored/untracked/filesystem-only payload가 실제로 존재하는 원 checkout이다. W0 non-Git inventory, archive source read, literal non-Git deletion과 W10 custody census는 이 동일 root identity에서만 수행한다. 이 root의 tracked rows는 충돌/identity 관측용이며 tracked removal delta로 세지 않는다.
* 두 subject는 canonical resolved root, volume/file-system identity(가능한 범위), HEAD, creation time, custody owner와 manifest SHA-256로 결속한다. clean worktree absence를 local deletion으로 세거나 두 root 사이 byte delta를 계산하지 않는다.
* subject manifest는 `core.autocrlf`, `core.eol`, `.gitattributes` Git blob ID/SHA-256, Git version, PowerShell version과 W0 inventory producer command/script SHA-256를 기록한다. tracked blob/materialization rule이 재실행 사이 바뀌면 W0 census는 완료로 기록하지 않고 explicit blocker를 낸다.
* plan의 PowerShell validation/closeout 예제는 Windows PowerShell 5.1과 PowerShell 7 공통 API만 사용한다. .NET Core-only API가 필요하면 해당 command를 PowerShell 7 전용으로 선언하고 exact carve-out을 별도 채택하기 전에는 사용하지 않는다.
* destructive wave는 exact selection manifest를 먼저 생성하고, glob 또는 directory name만으로 삭제 대상을 결정하지 않는다.
* tracked source는 Git rollback을 사용할 수 있지만 ignored/untracked reproduction payload는 Git에 없으므로 archive 또는 explicit disposable 판정 없이 삭제하지 않는다.
* Change 0E admission 또는 existing terminal-v15 validation 뒤 W0 current full gate가 baseline에서 실패해도 complete census 자체를 실패로 위장하지 않는다. gate launch 전 environment 불능은 `environment_authority_unavailable`, valid environment에서 실행된 gate의 non-zero는 implementation baseline failure로 분리한다. 후자는 explicit blocker로 기록하고 별도 remediation 전 implementation progression을 `blocked`로 둔다. baseline이 PASS하고 W0의 pre-adopted rule 검증에서 genuine blocker가 0이면 추가 owner round-trip 없이 Change 1B와 후속 implementation을 계속한다.
* external store가 create-new, immutable, owner-controlled, repository-disjoint 조건을 만족하지 않으면 historical deletion wave는 `blocked`다.
* local cleanup은 target의 resolved path가 recorded custody root 아래인지 확인하고, junction/symlink/reparse ancestor 또는 path escape가 있으면 삭제하지 않는다.
* enumeration, hashing 또는 path normalization에서 access-denied/long-path/invalid-name 오류가 하나라도 발생하면 해당 subtree를 0건으로 처리하지 않고 `enumeration_error` blocker로 기록한다. nested `.git`/`.hg`/`.svn` marker는 명시적 disposable owner decision 없이 archive/delete traversal 대상이 될 수 없다.

---

## 5. Repository Areas Affected

### Code

* `Iris/build/main.py`
* `Iris/build/phase2_rules/`, `Iris/build/phase3_output/`, `Iris/build/phase4_tests/` — 조사 checkout의 ignored-only legacy source; current tracked code로 간주하지 않음
* `Iris/build/tools/pipeline/context_outcomes_main.py`
* `Iris/build/tools/common/io.py`
* `Iris/build/description/v2/tools/build/`
* `Iris/build/description/v2/tools/`의 build 밖 helper/fixture/module
* `Iris/build/description/v2/tests/`
* `Iris/build/tests/`
* `Iris/build/description/v2/tests/.tmp/`, `Iris/build/description/v2/tests/.tmp_tests/`
* `Iris/build/description/v2/frozen_predecessor_inputs/`
* `Iris/build/description/v2/owner_inputs/`, `Iris/build/description/v2/reviewer_inputs/`
* `Iris/build/description/v2/data/`
* `Iris/test/`
* `Iris/evidence/`
* `Iris/input/`
* `Iris/_dev/`
* `Iris/tooling/src/iris_tooling/`
* `Iris/tooling/tests/`
* `Iris/validation/clean_checkout/`
* `Iris/validation/residual_refactor/migrate_repository_evidence.py`
* `Iris/validation/residual_refactor/execute_artifact_lifecycle.py`
* `Iris/validation/residual_refactor/report_artifact_lifecycle.py`
* `Iris/tools/package_iris.ps1`
* `Iris/media/lua/client/Iris/Data/`

### Docs

* `Iris/build/ENTRYPOINTS.md`
* `Iris/build/build_import_contract.md`
* `Iris/build/description/v2/tools/build/INVENTORY.md`
* `Iris/_docs/authority/iris_current_authority_manifest.json`
* `Iris/_docs/authority/iris_authority_classification.md`
* `Iris/_docs/` current allowlist와 historical archive selection
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `docs/iris_current_historical_physical_separation_and_repository_lightweighting_plan.md`

### Config

* `.gitignore`
* `.rgignore`
* `.gitattributes`
* `pytest.ini`
* `Iris/tooling/pyproject.toml`
* `Iris/tooling/uv.lock`
* `Iris/build/current_build_manifest.json`
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
* `Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json`
* `Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json`
* `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json`
* `Iris/tooling/src/iris_tooling/build/dvf_3_3_generation_contract.py`
* current evidence/archive manifest schema와 source disposition policy

### Generated Artifacts

* `Iris/build/description/v2/staging/`
* `Iris/build/description/v2/evidence/`
* `Iris/build/description/v2/output/`
* `Iris/output/`
* `Iris/build/package/`
* `Iris/media/lua/client/Iris/Data/IrisLayer3Generations/`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/`
* external work/result/package/archive/restore roots
* repository root `.tmp/` 중 owner-approved Iris selection
* `Iris/_archive/` obsolete ignore-rule surface(archive output 위치로 사용하지 않음)

---

## 6. Planned Changes

### Change 0E — conditional pre-W0 external environment authority admission

Purpose:

Change 1A의 repository-read-only 계약을 보존하면서 baseline full gate가 읽을 수 있는 실제 external environment를 확인한다. committed locator가 결속한 environment root가 없거나 validation에 실패할 때만 실행하는 environment-only authority wave다. Drafting predecessor의 terminal-v4 root는 부재했지만 post-hardening terminal-v15 root/receipt는 존재하므로, 실행 S0에서 terminal-v15 binding이 유효하면 이 Change는 `not_required(existing_environment_validated)`로 닫는다.

Files:

* `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json`
* 신규 versioned `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_iris_lightweighting_admission_v*.json`
* external allocator ledger/receipts, wheel, uv cache/environment, immutable environment receipt
* `Iris/validation/clean_checkout/write_environment_receipt.py` — 실행만 하며 이 wave에서 source 수정 금지

Implementation Notes:

* committed locator/record/receipt/root를 read-only admission probe로 먼저 확인한다. root가 존재하고 interpreter/package/content manifest가 모두 유효하면 Change 0E를 `not_required(existing_environment_validated)`로 기록하고 repository write 없이 Change 1A로 진행한다. locator, record, receipt 또는 environment root가 missing/invalid이면 ordinary gate FAIL로 기록하지 않고 Change 0E를 실행한다.
* Public-text hardening carrier의 current locator는 `terminal_v15`를 가리키며 조사 시점 external environment root와 receipt가 존재한다. S0에서 interpreter/package/content manifest와 package-source tree까지 유효하면 Change 0E는 `not_required(existing_environment_validated)`로 닫는다. terminal-v15가 통합 과정에서 유실·변조·불능이 된 경우에만 이 environment-only wave를 실행한다.
* Change 0E가 필요해도 범위는 이 plan에서 이미 승인한 environment-only 두-file authority diff다. source/lock mismatch가 발견되면 이 wave에서 확대 수정하지 않고 별도 remediation blocker로 올린다.
* owner-approved exact diff는 신규 immutable authority record와 current locator 두 파일뿐이다. `Iris/tooling` source/lock, gate contract, product/runtime/source, W0 classification 또는 cleanup을 변경하지 않는다. source/lock mismatch가 발견되면 이 wave에서 고치지 않고 별도 remediation blocker로 올린다.
* exact clean source commit/tree를 먼저 고정하고 §7.3의 wave-specific `checkpoint` allocation에서 `uv_environment`, `uv_cache`, `package_result`, `test_output` roots를 사용해 wheel/environment/tests/CLI를 생성·검증한다. `write_environment_receipt.py`의 required authority record/locator outputs는 이 wave가 소유한다.
* environment receipt의 implementation/source binding은 authority record/locator를 추가하기 직전 clean source commit이다. writer output만 authority-only **Commit 0E**로 채택하고, 새 clean worktree에서 locator hash, record hash, external root와 receipt content manifest를 다시 검증한다.
* Change 0E가 `not_required`이면 S0를 그대로 Checkpoint A target으로 사용한다. Reseal을 수행한 경우 authority-only Commit 0E의 새 process가 committed locator를 읽기만 하며, 이 validation 중 `write_environment_receipt.py`, environment 생성 또는 repository write를 다시 수행하지 않는다. Checkpoint A PASS 뒤 exact target을 Change 1A clean subject로 사용한다.

Validation:

* preflight outcome이 `existing_environment_validated` 또는 exact `environment_authority_unavailable` 중 하나이며 implementation gate FAIL과 혼합되지 않음
* external environment root/interpreter/package/content manifest/receipt hash validation PASS
* Commit 0E diff가 신규 versioned authority record와 current locator 밖을 변경한 사례 `0`
* authority-only commit의 parent 대비 `Iris/tooling` project/lock/package-source tree identity 불변
* §7.3 allocator의 used/unused root lifecycle receipt와 Checkpoint A canonical Run A/B/comparator exit `0`
* S0 또는 Commit 0E clean post-status 및 Change 1A baseline이 읽을 valid committed locator 존재

---

### Change 1 — W0 read-only 조사와 deterministic authority amendment

Purpose:

삭제 전에 current source/data/evidence와 historical/reproduction/generated/disposable 역할을 exact path 단위로 고정한다. Read-only evidence 생성과 authority-writing amendment를 별도 execution unit으로 분리하되, 이 plan이 미리 채택한 disposition rule과 hard ceilings를 W0 결과에 기계적으로 적용한다. Genuine blocker나 scope expansion이 없으면 별도 owner 질문·계획 재작성·중간 rereview 없이 후속 실행을 연다.

Relevant inputs / potential Change 1B files:

* `Iris/_docs/authority/iris_current_authority_manifest.json`
* `Iris/build/current_build_manifest.json`
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
* `Iris/validation/residual_refactor/report_artifact_lifecycle.py`
* `Iris/build/ENTRYPOINTS.md`
* `Iris/build/description/v2/tools/` 전체
* `Iris/build/description/v2/tests/.tmp/`, `Iris/build/description/v2/tests/.tmp_tests/`
* `Iris/build/description/v2/frozen_predecessor_inputs/`, `owner_inputs/`, `reviewer_inputs/`
* `Iris/build/description/v2/data/`, `Iris/build/tests/`
* `Iris/test/`, `Iris/evidence/`, `Iris/input/`, `Iris/_dev/`, `Iris/_archive/`
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`
* `.gitattributes`
* external W0 inventory root, producer manifest와 deterministic adoption record

#### Change 1A — W0 read-only census 및 decision packet

Inputs/Outputs:

* read-only inputs: clean implementation subject, local custody subject, current manifests/contracts/config and `.gitattributes`
* external create-new outputs: dual-subject census, broader staging disposition table, evidence claim matrix, `main.py=C`/archive/capsule/Layer 3 disposition-verification packet, producer manifest, W0 baseline Run A/B/orchestration/comparator and allocation-usage receipts
* repository writes: none

Implementation Notes:

* clean Git worktree에는 tracked Git blob identity와 별도 worktree materialization census를, local custody checkout에는 ignored/untracked/filesystem-only/reparse/VCS-marker census를 산출한다. tracked raw SHA는 `git cat-file blob <blob-id>` bytes에서 계산하고 custody-only SHA만 filesystem bytes에서 계산한다.
* 두 subject manifest는 서로 다른 `subject_id`, canonical root/volume identity, HEAD/tree, `core.autocrlf`, `core.eol`, `.gitattributes` blob ID/SHA-256, producer command/script SHA-256, Git/PowerShell version을 가진다. W0 external evidence는 create-new root에 기록하며 producer identity가 없는 ad-hoc output은 채택하지 않는다.
* `git ls-files`, non-ignored untracked, ignored, PowerShell physical enumeration을 별도 집합으로 저장한다. union/intersection과 bytes를 domain별로 기록하고 overlap을 합산하지 않는다. physical enumeration의 1-row remainder인 `Iris/build/description/v2/tests/.tmp/uv-cache/sdists-v9/.git`을 `filesystem_only_vcs_marker`로 명시한다.
* full gate의 `execution_workspace.disposable_bootstrap_local_paths`에 선언된 repository-root `.dvf_tmp/`를 두 subject에서 exact path로 조사한다. clean source에는 terminal absence contract를 적용하고, custody에 존재하면 tracked/ignored/untracked/filesystem-only role과 owner decision 없이 자동 삭제하지 않는다.
* `frozen_predecessor_inputs/`, `owner_inputs/`, `reviewer_inputs/`, `build/tests/`, `description/v2/data/` 각각에 독립 physical/tracked/ignored/current-consumer denominator를 산출한다. `frozen_predecessor_inputs/dvf_3_3_registry_authority_canonical_closure/current_route/manifest.json`의 gate-pinned digest와 이를 읽는 contract row를 `current_contract` 또는 `current_required_evidence` 보호 집합에 포함한다.
* full gate direct binding, authority-manifest expansion, required validation/artifact, Python import, subprocess/CLI argv, dynamic `Path` construction, manifest/JSON path, current test consumer, clean-checkout bootstrap과 historical string-only reference를 각각 독립 집합으로 산출한다.
* 모든 staging operational row에 `move_to_current_owner`, `raw_capsule`, `digest_capsule`, `historical_archive`, `retained_exception`, `unresolved_blocker` 중 정확히 하나를 부여하는 **broader staging closure disposition table**을 만든다. direct-bound 18 rows는 이 전체 table의 subset이다. Current operational consumer가 있으면 최소 current owner/capsule로 이관하고, current consumer 0이면서 historical value가 있으면 archive 후 remove, 재생성/cache이면 remove가 default다. `retained_exception`은 exact current consumer와 유지 필요 bytes가 증명된 row만 허용하며 unsupported keep, remaining eligible removal과 unimplemented removal은 각각 0이어야 한다.
* `Iris/**`와 owner가 미리 승인한 repository-root exact rows를 `current_source`, `current_runtime`, `current_tooling`, `current_contract`, `current_required_evidence`, `historical_reproduction`, `generated_disposable`, `local_cache`, `unresolved` 중 기존 의미로 환원 가능한 역할에 매핑한다. `_docs`는 `.md`뿐 아니라 JSON/JSONL 및 모든 broad authority rule을 exact protected allowlist 후보로 좁힌다.
* `owner_inputs/`와 `reviewer_inputs/` 각 row는 operational consumer evidence와 함께 `historical_archive` 또는 versioned `retained_exception` 중 하나를 가져야 한다. current consumer가 있는 row를 단지 디렉터리명 때문에 archive로 분류하면 W0 validator가 실패한다.
* `Iris/build/main.py` verification packet은 exact facts인 missing `phase0_validation`, `phase1_extraction`, `phase2_rules`, `phase3_output`, `phase4_tests`와 operational current consumer 0을 다시 확인한다. Adopted C disposition에 따라 legacy entrypoint를 current authority에서 제거하고 existing supported classification/context-output producer만 보존한다. 예상 밖 current consumer가 발견되면만 blocker로 올린다.
* direct 18 rows에는 operation class와 predecessor/successor claim matrix를 만든다. Current raw capsule hard ceiling은 2,359,296 bytes다. Raw claim 유지에 필요한 최소 bytes가 이를 넘으면 W0 실패로 숨기거나 자동 exception으로 보존하지 않고 exact ceiling blocker를 낸다.
* archive packet은 existing deterministic ZIP profile과 proposed `content_addressed_zip_v2`, Layer 3 mandatory preservation, logical restore parity 및 policy-supersession 필요 여부를 비교한다.
* 이 unit에서는 current evidence 복사, governance/manifest/gate 수정, tracked/non-Git cleanup을 수행하지 않는다. Checkpoint A PASS, current closure의 missing/unclassified 0, `main.py=C` verification, unsupported keep/remaining eligible/unimplemented removal 0, ceiling 준수와 genuine blocker 0이면 같은 실행에서 Change 1B로 진행한다. Scope expansion이나 위 조건의 실패가 있을 때만 중단한다.
* dual-subject conflict는 숨기지 않는다. custody HEAD가 clean subject의 W0 target commit과 다르거나, custody dirty tracked path가 protected/current/archive/delete selection과 교차하거나, 같은 tracked path의 Git blob이 target commit과 다르거나, recorded canonical root/volume binding이 재실행 사이 바뀌면 해당 row와 모든 dependent Change를 `blocked(reason=dual_subject_identity_conflict)`로 둔다.
* baseline full gate는 Change 0E에서 유효화된 committed locator/environment를 **읽기만** 하며 §7.3의 reseal branch, `write_environment_receipt.py` 또는 authority record/locator output을 호출하지 않는다. gate work/result/orchestration/compare output은 repository-disjoint W0 allocations에만 쓴다.

Validation:

* environment admission preflight가 먼저 PASS해야 한다. locator/root/receipt 불능은 `environment_authority_unavailable` blocker이고 baseline implementation FAIL로 세지 않는다. admission PASS 뒤 실행한 baseline full gate Run A/B/comparator의 실제 exit/status/failure meaning을 그대로 기록한다. 이때의 baseline failure는 W0 census 실패로 바꾸지 않지만 explicit implementation blocker가 된다.
* W0 progression success는 `complete census + deterministic manifest parity + current closure missing/unclassified 0 + unsupported keep/remaining eligible/unimplemented removal 0 + explicit blocker 0`이다. Census 자체는 blocker를 기록하고 완료할 수 있지만 blocker가 있으면 Change 1B 이후 implementation progression은 열리지 않는다.
* clean/custody subject identity, normalization state, tracked/ignored/untracked/filesystem-only domain count, producer identity와 manifest digest 존재
* clean/custody `core.autocrlf`/`core.eol`과 `.gitattributes` blob state mismatch가 있으면 explicit normalization blocker로 기록하고 tracked worktree-byte parity, capsule/archive progression을 금지
* broader staging operational closure의 모든 row가 disposition을 정확히 하나 가지며 누락/중복 `0`; `unresolved_blocker > 0`이면 Change 7/8은 닫힘
* main import-root exact list, 18-row operation/claim classification, Layer 3/archive profile decision inputs의 source evidence 존재
* enumeration/hash/long-path/access 오류가 조용히 누락된 사례 `0`

#### Change 1B — deterministic authority amendment

Files:

* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`
* compact versioned disposition-adoption record
* declaration-only current authority/build/gate contract version rows required by adopted decisions
* external subject-scoped residue selection/exception manifest digests와 compact repository locator/summary

Implementation Notes:

* W0 packet hash에 결속해 pre-adopted `main.py=C`, broader staging row별 deterministic disposition, raw/digest claim supersession, capsule hard ceiling, `content_addressed_zip_v2`, tracked `.tmp` 18 rows와 root tracked `.pyc` disposition, empty `_archive`, Layer 3 hold release 조건을 봉인한다.
* owner는 `frozen_predecessor_inputs/`를 current-required gate fixture로 보호하고, `owner_inputs/` 및 `reviewer_inputs/`의 각 row를 `historical_archive` 또는 versioned `retained_exception`으로 확정하며, `build/tests/`와 `description/v2/data/`의 current consumer/protection disposition을 채택한다.
* Change 2 selection과 retained exception은 repository-external `subject_scoped_residue_manifest_v1` one-off format을 공통으로 사용한다. `subject_id`, subject-root binding과 `file_exact|directory_exact|directory_subtree` semantics는 Commit 1B의 compact adoption record에 고정하되, 이 format이나 validator를 repository-regular validation authority/schema로 등록하지 않는다.
* Wave allocation identity는 §7.3의 fixed checkpoint mapping과 external allocation receipt가 소유한다. 일회성 lightweighting execution을 위해 새 repository-regular execution schema를 만들지 않는다.
* `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, compact disposition-adoption record와 필요한 declaration-only authority/manifest version을 **Commit 1B**에 반영한다. 이 plan을 실행 중 자기수정하지 않으며 current dependency path 삭제/rebind나 payload 이동은 후속 Change에서만 수행한다.
* W0 packet의 subject/producer/manifest digests, decision row IDs와 amendment의 선택이 전수 대응되어야 한다. sealed predecessor record를 rewrite하지 않고 successor decision을 append한다.
* Checkpoint A baseline full gate가 PASS인 경우에만 Change 1B가 정상 progression amendment를 봉인할 수 있다. Baseline full gate가 FAIL이면 W0는 census와 failure packet까지만 완료하고 이 plan은 Change 2 앞에서 닫힌다. 별도 remediation으로 canonical full gate PASS를 얻은 뒤 새 S0/W0 packet으로 다시 시작한다. Change 1B 자체는 declaration-only 범위를 넘어 failing implementation이나 gate 기대값을 수정하지 않는다.
* Change 1B는 다음 실행-chain 계약을 함께 고정한다: baseline-failure 별도 remediation, current successor binding Checkpoint B, ordinary canonical gate를 사용하는 external synthetic candidate Checkpoint C, archive implementation/restore, subject-aware residue selection과 PowerShell 5.1-compatible normalization, 새로 census된 subtree의 row별 disposition, Change 번호의 순서 권위, package source 변경 시 environment reseal, Change 0E/1A write ownership, allocator root/profile/ledger binding, 모든 Git identity query의 explicit `-C <subject-root>`.
* Change 1B는 declaration-only authority amendment다. Diff와 compact adoption record를 focused review하고 바로 Change 2로 진행한다. W0가 이 plan의 pre-adopted rules로 처리할 수 없는 genuine scope expansion을 발견한 경우에만 `blocked(reason=W0_scope_expansion_requires_plan_revision)`로 닫고 별도 plan review를 요구한다.

Validation:

* W0 packet digest/row exact-set과 deterministic adoption record/amendment의 one-to-one consistency
* 선택되지 않은 `main.py` branch, undecided broader staging row, archive profile 또는 capsule budget row `0`
* Commit 1B diff가 approved governance/declaration files 밖을 변경한 사례 `0`
* baseline full gate Run A/B/comparator PASS. FAIL이면 위 별도 remediation plan의 owner approval, independent review, implementation commit, PASS evidence와 새 W0/1B hash가 모두 없으면 Change 2 progression 금지
* Pre-adopted execution-chain checklist 누락 `0`; terminal independent reviewer가 각 항목을 exact section/file/command에 역추적 가능
* Genuine blocker와 scope expansion `0`이면 Change 2 progression은 open

---

### Change 2 — tracked residue removal과 non-Git custody cleanup 분리

Purpose:

W0/Change 1B가 disposable로 승인한 residue를 Git-tracked와 custody-only domain으로 분리해 각 소유 subject에서 제거한다.

Candidate files, finalized by Change 1B:

* `Iris/tooling/.venv/`
* Iris 아래 `__pycache__/`, `*.pyc`, `.tmp/`, `.tmp_tests/`, `.dvf_tmp/`, pytest/cache/log residue
* repository root `.tmp/` tracked 18 rows 및 non-Git rows 중 W0/1B가 Iris-owned `generated_disposable`로 채택한 exact rows
* repository root `.dvf_tmp/`가 subject에 존재할 경우 gate-declared ephemeral residue exact row
* root tracked `__pycache__/conftest.cpython-314-pytest-9.0.3.pyc` — owner가 Iris/repository validation residue로 채택한 경우에만 2A
* empty `Iris/_archive/` directory — 2B

#### Change 2A — tracked generated/cache removal

Files:

* W0/1B-approved repository root `.tmp/` tracked exact rows
* repository root `.dvf_tmp/`가 tracked로 존재하는 경우 W0/1B-approved exact rows
* W0/1B-approved tracked Iris cache/residue rows
* owner-approved root tracked `__pycache__/conftest.cpython-314-pytest-9.0.3.pyc`, otherwise out-of-scope exception
* tracked removal receipt/guard
* repository-external `subject_scoped_residue_manifest_v1` Change 2A selection manifest와 digest
* external one-off residue selection validator/negative probes와 compact tracked removal summary; 정규 validation authority로 등록하지 않음

Implementation Notes:

* clean implementation subject에서만 수행한다. selection은 W0/1B가 `tracked + generated_disposable/local_cache + consumer 0 + Git revert sufficient`로 승인한 exact rows다. recovery/historical/unique source는 Change 7 archive 및 Change 8 tracked removal로 넘긴다.
* root `.tmp` tracked 18 rows와 root tracked `.pyc`를 row별 판정한다. approved rows는 **Commit 2A**의 Git-authored deletion으로 제거하고 custody checkout의 tracked files는 변경하지 않는다.
* selection에는 Git blob ID/SHA-256, consumer proof, owner decision row와 rollback commit을 기록한다. tracked가 아닌 row가 들어오면 fail-closed한다.
* `.gitignore`/`.gitattributes`는 이 unit에서 수정하지 않는다.

Validation:

* `git ls-files --error-unmatch`로 모든 2A row가 tracked임을 확인하고 exact blob identity parity
* selection schema에서 `subject_id=clean_implementation`, subject-root binding digest, normalized relative path와 file/directory semantics 일치; absolute/path-escape/wrong-subject fixture fail-closed
* Commit 2A diff가 approved delete rows와 receipt/guard update 밖을 변경한 사례 `0`
* current consumer reference `0`, source checkout clean, affected focused validation과 exact diff guard exit `0`; canonical full gate는 Checkpoint B에서 successor-binding 변경과 함께 실행
* custody checkout tracked-path absence를 2A acceptance 또는 byte delta로 사용하지 않음

#### Change 2B — non-Git custody cleanup

Files:

* `Iris/tooling/.venv/` 및 W0/1B-approved Iris ignored/untracked cache exact rows
* `Iris/build/description/v2/tests/.tmp/`, `.tmp_tests/` approved non-Git rows
* root `.tmp/` approved ignored/untracked/filesystem-only exact rows
* repository root `.dvf_tmp/` approved ignored/untracked/filesystem-only exact row
* empty `Iris/_archive/`
* external custody cleanup selection/receipt
* repository-external `subject_scoped_residue_manifest_v1` Change 2B selection/retained-exception manifests와 digests

Implementation Notes:

* recorded local custody root에서 ignored/untracked/filesystem-only rows만 literal deletion한다. 각 row는 path, role, size/filesystem SHA, ignore state, resolved target, reparse/VCS-marker ancestry를 가진다. tracked row가 하나라도 selection에 들어오면 전체 action을 중단한다.
* `Iris/build/description/v2/tests/.tmp/`의 ignored rows와 filesystem-only nested `.git` marker는 자동 cache로 보지 않는다. W0 exact selection이 enclosing uv-cache를 consumer 0의 disposable residue로 증명한 경우에만 marker 포함 exact tree removal을 허용한다.
* `Iris/_archive/`는 empty, non-reparse, nested-entry 0을 재확인한 뒤 empty directory만 제거한다. archive output을 이 경로에 생성하지 않는다.
* old tooling ignored Python, `Iris/test`, `Iris/evidence`, `Iris/input`, `Iris/_dev`의 ignored rows는 자동 cache로 간주하지 않는다. `graphify-out`, `console_log.txt`, `Pulse_All_Source.txt`, `.codex-worktrees`, other module/cache는 제외한다.
* enumeration과 삭제는 literal resolved paths, long-path-aware API와 `-ErrorAction Stop`을 사용한다. error/partial traversal은 성공 0건으로 기록하지 않는다.

Validation:

* 모든 2B row가 `git ls-files --error-unmatch`에는 실패하고 ignored/untracked/filesystem-only 중 정확히 하나임을 확인
* exact path/size/hash selection manifest, containment, junction/symlink/reparse, nested VCS, directory-swap와 long-path/error negative tests
* selection schema에서 `subject_id=local_custody`; same-relative-path cross-subject collision, `file_exact`/`directory_subtree` mismatch와 stale root binding fixture fail-closed
* 동일 custody root의 제거 후 literal absence와 domain별 bytes; clean subject absence와 합산하지 않음
* cleanup 전후 scope-limited focused command exit/status/failure meaning 동일
* `git check-ignore --no-index -v -- <path>` expected role과 일치

---

### Change 3 — Lua runtime authority와 generated output/deploy 관계 단일화

Purpose:

runtime current source를 stale 또는 duplicate generated output이 덮어쓸 수 없게 하고, output은 explicit external result 또는 install candidate로만 취급한다.

Files:

* `Iris/build/main.py`
* W0 owner decision이 복구/이관 대상으로 확정한 exact phase module 또는 successor
* `Iris/build/tools/pipeline/context_outcomes_main.py`
* `Iris/build/tools/common/io.py`
* `Iris/output/IrisData.lua`
* `Iris/output/IrisClassifications.lua`
* `Iris/output/context_outcomes.lua`
* `Iris/media/lua/client/Iris/Data/IrisData.lua`
* `Iris/media/lua/client/Iris/Data/IrisClassifications.lua`
* `Iris/media/lua/client/Iris/Data/IrisContextOutcomes.lua`
* 관련 tests, current build manifest와 entrypoint docs
* A branch가 package successor를 택할 경우 `Iris/tooling/pyproject.toml`, `Iris/tooling/uv.lock`, package source 및 current environment authority/locator

Implementation Notes:

* `IrisData.lua` runtime current authority는 371-byte thin adapter로 고정한다. old full-table output 생성·append·deploy 경로를 제거한다.
* 이 Change는 pre-adopted **C disposition**만 구현한다. Current manifests/tests/docs에서 broken legacy `main.py` entrypoint를 제거하고 필요한 classification/context-outcome outputs의 existing supported producer를 각각 명시한다. 새 동등 successor 구현(A)과 결손 phase module 복구(B)는 이 lightweighting scope에서 금지한다.
* 어떤 branch에서도 `IrisData.lua`는 output/install list에 포함하지 않는다. repository-local mutable output root는 default 또는 fallback이 될 수 없다.
* classification/context outcome output은 external candidate를 먼저 생성·검증한 뒤 explicit install action만 current runtime target을 갱신한다. install은 expected target, hash, source role과 allowed filename을 fail-closed 검증한다.
* runtime source와 output copy가 byte-identical하더라도 repository-local output copy를 authority로 취급하지 않는다. 필요한 deterministic baseline은 Change 6의 compact seed/fixture로 이동한다.
* root classification entrypoint를 successor로 교체하는 W0 판정이 나오면 구현과 manifest/gate/test rebinding을 같은 commit에 넣고 `main.py`는 historical predecessor로 disposition한다.
* A branch가 `iris_tooling` source를 바꾸면 Change 4와 동일한 implementation commit -> external environment receipt -> authority-only locator commit 순서를 적용한다.

Validation:

* stale 75,143-byte `IrisData.lua`에서 371-byte adapter로의 overwrite negative test
* `IrisClassifications.lua`와 `IrisContextOutcomes.lua` external candidate/runtime install parity
* allowed target 밖 write, missing external root, corrupt candidate, wrong hash가 fail-closed
* `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1` exit `0`
* runtime/package manifest에 thin adapter와 current runtime copies가 정확히 한 번 포함됨
* `main.py=C` disposition의 exact CLI/input/output/consumer acceptance, operational current consumer `0`, A/B branch 구현이나 결손 phase module이 current manifest에 남지 않음
* runtime Lua/install target 또는 package bytes가 바뀌면 §7 Manual Validation 완료 전 closeout ceiling은 `implemented_only`

---

### Change 4 — W3 predecessor current binding 제거 및 consumer closure

Purpose:

installed `iris_tooling` successor가 이미 소유하는 기능의 current dependency를 old `Iris/build/description/v2/tools/`에서 제거하고, zero-consumer predecessor를 Change 7 archive/Change 8 removal 대상으로 확정한다. 이 Change 자체에서는 predecessor source를 물리 제거하지 않는다.

Files:

* `Iris/tooling/src/iris_tooling/build/`
* `Iris/tooling/src/iris_tooling/domains/`
* `Iris/tooling/tests/`
* `Iris/tooling/pyproject.toml`
* `Iris/tooling/uv.lock`
* `pytest.ini`
* `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/build/description/v2/tests/test_iar_public_text_assessment.py`
* `Iris/build/description/v2/tests/fixtures/`
* `Iris/build/tests/`
* `Iris/build/description/v2/frozen_predecessor_inputs/`
* `Iris/build/description/v2/data/`
* `Iris/test/test_adaptive_interaction_presentation.py`
* `Iris/test/test_layer4_runtime_projection.py`
* `Iris/tooling/src/iris_tooling/build/dvf_3_3_generation_contract.py`
* `Iris/build/description/v2/tools/build/`
* `Iris/build/description/v2/tools/`의 build 밖 current helper/fixture
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
* `Iris/validation/residual_refactor/run_python_import_matrix.py`
* `Iris/validation/residual_refactor/report_artifact_lifecycle.py`
* current manifests/import contracts/inventory docs

Implementation Notes:

* reusable `iar_public_text_assessment.py`는 유지한다. old runner/validator의 CLI semantics가 current test에 필요하면 package-owned CLI module/subcommand로 이관하고 test는 installed package 또는 public Python API만 소비하게 한다.
* full gate의 IAR `explicit_direct_dependencies`를 package successor와 contract/fixture로 재결속한다. old wrapper path 제거와 binding update는 같은 commit에 둔다.
* `GENERATOR_IMPLEMENTATION_FILES`를 current package source로 바꾸고 historical predecessor identity는 append-only transition evidence로만 남긴다.
* old tree 안의 hermetic candidate test fixture는 `Iris/build/description/v2/tests/fixtures/`로 이동하고 test binding을 같은 commit에서 갱신한다.
* residual validation/import-matrix 도구가 old path를 current import 대상으로 검사하는 경우 successor 검사를 추가한 뒤 old current route를 제거한다. frozen predecessor payload 안의 문자열과 sealed historical ledgers는 operational consumer로 세지 않는다.
* W0 재측정은 `tools/build/`뿐 아니라 `Iris/build/description/v2/tools/` 전체를 대상으로 한다. 조사값 physical 774 / tracked 275 / ignored 499를 denominator로 삼고 operational consumer/fixture/helper를 exact path로 분류한다.
* tracked zero-consumer predecessor도 Change 7 archive selection에 넣어 external preservation을 완료한 뒤 Change 8에서 제거한다. ignored unique reproduction source 역시 Change 7 archive selection에 넣고, cache/byte-identical duplicate만 Change 2B non-Git disposable로 삭제한다.
* terminal acceptance는 old directory 전체 삭제가 아니라 `current operational consumer = 0`, `retained exact exception = explicitly listed`다. exception이 남으면 directory whole-tree removal을 주장하지 않는다.
* `frozen_predecessor_inputs/dvf_3_3_registry_authority_canonical_closure/current_route/manifest.json`과 W0가 current-required로 확정한 `description/v2/data/` rows는 predecessor-removal closure에서 제외하고 gate-protected exact set으로 검증한다. `Iris/build/tests/`의 tracked tests가 old path를 소비하면 같은 wave에서 successor로 재결속하며 ignored residue는 Change 2B selection으로만 다룬다.
* package source tree가 바뀌므로 Change 4 implementation commit 뒤 §7.3의 external wheel/environment/receipt를 새로 만들고, immutable authority record와 stable locator는 별도 authority-only commit으로 갱신한 뒤 full gate를 수행한다. 과거 W3 receipt를 source hash 불일치 상태로 재사용하지 않는다.

Validation:

* installed package tests와 arbitrary-cwd CLI probe exit `0`
* current Python import, subprocess argv, manifest, gate, dynamic Path/string consumer의 old tree reference `0`
* historical/frozen string reference와 operational reference를 분리한 report
* IAR PASS/FAIL exit semantics, no-write validator와 deterministic replay parity
* current generation implementation identity/hash transition validation
* Change 4 affected package/import/IAR/generation validation exit `0`; exact canonical Run A/B/comparator는 Change 7A 완료 뒤 Checkpoint B에서 한 번 실행
* top-level adaptive-interaction와 Layer 4 runtime projection tests exit `0`

---

### Change 5 — bounded current evidence capsule 생성과 G4/G5 rebinding

Purpose:

historical staging을 제거하기 전에 current gate가 실제 내용을 읽어야 하는 최소 bytes만 current owner 경계로 옮기고, hash/existence/path identity 소비는 digest contract로 바꿔 새 대형 복제를 만들지 않는다.

Files:

* `Iris/validation/clean_checkout/evidence/current_required_v1/` — 신규
* current evidence manifest/schema/validator — 신규 또는 확장
* `Iris/validation/clean_checkout/contracts/full_repository_gate.json`
* `Iris/_docs/authority/iris_current_authority_manifest.json`
* `.gitattributes`
* versioned evidence claim matrix와 migration transition receipt/schema
* broader staging closure disposition manifest
* capsule-specific compact validator/tests와 existing full-gate binding update; canonical launcher/comparator execution mode는 변경하지 않음
* attempt-0024 handoff/assessment current binding consumers

Implementation Notes:

* 기준 denominator는 full gate JSON 안의 staging direct-bound 18 files / 18,829,290 bytes다. top four는 7,971,479 / 6,843,637 / 1,969,097 / 1,905,371 bytes다. Current capsule hard ceiling은 2,359,296 bytes(2.25 MiB)다. W0가 증명한 최소 raw current bytes가 이를 넘으면 자동 exception을 만들지 않고 scope-expansion blocker로 닫는다.
* operation class만으로 raw/digest를 결정하지 않는다. row별 **claim owner와 failure requirement**를 먼저 정한다. raw repository-local availability/hash recomputation을 current gate가 계속 주장하면 `raw_capsule`, 해당 claim을 supersede하면 `digest_capsule`, source/data owner가 current authority면 `move_to_current_owner`다.
* predecessor/successor claim matrix는 최소 다음 전이를 명시한다.

| Disposition | Superseded predecessor claim | Successor current-gate claim | Raw historical owner |
| --- | --- | --- | --- |
| `raw_capsule` | old staging logical-path availability | capsule raw member availability + raw hash recomputation | current capsule 및 historical archive |
| `digest_capsule` | repository-local historical raw availability | versioned digest/summary attestation + migration receipt integrity | external archive verifier only |
| `move_to_current_owner` | staging path ownership | exact current owner raw/schema contract | current source/data/evidence owner |
| `historical_archive` | current-route applicability | no current claim; historical-only disposition receipt | external archive verifier only |

* `digest_capsule`은 predecessor와 동일 failure meaning/parity를 주장하지 않는다. `raw_repository_evidence_v1` availability claim을 supersede하고 `current_capsule_attestation_v2`를 채택한 authority transition이다. raw missing/corruption/restoration은 archive verifier가, digest/summary/receipt missing·tamper는 current gate가 실패시킨다.
* 각 row는 `operation_class`, predecessor/successor claim ID, `role`, `source_logical_path`, tracked Git blob ID/raw SHA 또는 custody filesystem SHA, optional `capsule_path`, source/retained size, consuming field/function과 owner-decision row를 기록한다.
* broader staging closure table의 `move_to_current_owner`, `raw_capsule`, `digest_capsule` 전체를 이 Change에서 처리한다. direct 18 밖 operational row를 남긴 채 direct-bound closure만 PASS로 기록하지 않는다. `historical_archive`는 Change 7, `retained_exception`은 exact current manifest, `unresolved_blocker`는 progression block으로 연결한다.
* current source/tooling/data와 excluded historical test source는 capsule에 중복하지 않는다. current test가 필요하면 supported test owner로 이관하고, historical string-only exclusion이면 digest row만 둔다.
* tracked raw member는 source worktree bytes를 복사하지 않고 exact source Git blob bytes에서 materialize한다. `.gitattributes`에 `Iris/validation/clean_checkout/evidence/current_required_v1/** -text`를 추가하고 source blob, destination blob/worktree raw identity를 모두 검증한다.
* raw/digest rows, G4/G5 bindings, broader manifest, claim contract, transition receipt, current manifest와 validator update는 **Commit 5A 하나**에 둔다. 이 commit에서는 old staging bytes를 삭제하지 않는다. transition receipt는 source blob/filesystem identity→capsule identity를 결속하고 Change 7B가 archive object/restore identity를 append-only successor로 완성한다.
* capsule validator는 missing, hash mismatch, duplicate logical role, unregistered raw file, path escape, adopted budget/exception 위반과 external archive locator의 current-route 유입을 fail-closed한다.
* 이번 삭제를 위해 canonical launcher/comparator/Python runner-validator/common/plugin/schema에 새로운 `pre_delete_independence_probe` mode나 cleanup 전용 CLI field를 추가하지 않는다. Change 8의 disposable synthetic candidate는 기존 ordinary canonical full gate를 그대로 실행하며 base/candidate/delete/parity identity와 claim ceiling은 repository-external compact receipt가 소유한다.
* Change 5 acceptance는 old staging bytes가 아직 물리적으로 존재하더라도 operational current binding이 0이고 current capsule/owner rebinding이 existing canonical full gate contract에서 유효한 상태다. Exact synthetic candidate 생성과 staging absence를 전제로 한 ordinary Run A/B/comparator는 Checkpoint C가 소유한다.

Validation:

* 18-row operation classification exact coverage, duplicate/unclassified `0`
* broader staging closure의 operational row exact coverage와 disposition successor existence; `unresolved_blocker 0`
* capsule raw exact-set/Git-blob hash/size, digest/summary/transition-receipt identity와 adopted budget/exception parity
* claim matrix에서 predecessor raw availability와 successor attestation을 같은 parity claim으로 표시한 row `0`
* raw capsule missing/corruption, digest/summary/receipt tamper, `hash_only` source mutation during migration 각각의 owner-specific expected failure
* `move_to_current_owner` row의 successor owner 파일 누락, owner mismatch, source/successor digest mismatch를 각각 fail-closed하는 fixture
* full gate에서 historical staging operational binding `0`; historical sealed string reference는 별도 report로만 허용
* canonical validation source에 cleanup 전용 execution mode/CLI/schema가 추가된 사례 `0`
* Change 5 capsule/rebinding focused validation이 PASS해야 Change 6으로 진행하며 exact full gate는 Change 7A 뒤 Checkpoint B에서 실행

---

### Change 6 — historical `_docs`와 generated output의 current surface 분리

Purpose:

current claim이 실제 요구하는 documents/fixtures만 exact allowlist로 유지하고 raw historical evidence와 regenerated output을 archive/disposable candidate로 확정한다. 이 Change는 current binding을 바꾸지만 historical payload를 아직 삭제하지 않는다.

Files:

* `Iris/_docs/`
* `Iris/output/`
* `Iris/build/description/v2/output/`
* `Iris/build/baseline/`
* `Iris/build/description/v2/tests/fixtures/`
* `Iris/_docs/round3/round3_test_taxonomy.json`
* `Iris/_docs/round3/validated_naturalization_current_runtime_adoption/current_generation_descriptor.json`
* current authority/build manifests
* full gate `execution_workspace.standalone_output_projection`

Implementation Notes:

* `Iris/_docs/*.md = current` 같은 broad glob을 모두 제거한다. active authority, round3 taxonomy/routing, current generation descriptor, product/data contracts와 gate-bound compact evidence를 exact protected allowlist로 등록한다. broad JSON/JSONL glob도 동일하게 금지한다.
* lifecycle manifest, contract/disposition ledger, historical validation/playtest/debug log, superseded attempt evidence는 Change 7 archive selection으로 보낸다. top-level governance와 현재 product/data contract를 archive하지 않는다.
* `Iris/output`을 현재 producer의 mutable workspace로 사용하지 않는다. standalone command나 tests가 요구하는 exact seed subset은 `Iris/build/baseline/` 또는 test fixture owner 아래로 raw-byte identity를 유지해 이동하고 full gate seed binding을 **Commit 6A**에서 함께 갱신한다.
* `description/v2/output/dvf_3_3_rendered.json`의 current consumer를 current generation approved/rendered input 또는 explicit external result로 재결속한다. 다른 output은 deterministic regeneration과 consumer 0이 증명된 뒤 Change 8 delete selection에 넣는다.
* output file을 runtime source와 동일하다는 이유만으로 current evidence capsule에 넣지 않는다.
* 대형 item-level inventory는 repository에 복제하지 않고 Change 7 external archive inventory + compact digest로 남긴다.

Validation:

* protected `_docs`/JSON allowlist exact-set과 current doc/reference consumer missing `0`
* standalone seed exact-set과 hash parity, full gate execution workspace parity
* current producer의 repository-local mutable output fallback `0`
* deterministic regeneration Run A/Run B output digest equality
* `_docs` exact allowlist 밖 operational current binding `0`
* Change 6 affected allowlist/seed/output focused validation과 exact binding/reference guard exit `0`; canonical full gate는 Change 7A 뒤 Checkpoint B에서 한 번 실행

---

### Change 7 — deterministic archive successor 및 mandatory preservation

Purpose:

historical/reproduction payload와 inactive Layer 3 rollback payload를 policy-conformant external archive에 먼저 보존하고, exact logical restore를 검증한 durable evidence commit을 만든다. 이 Change에서는 repository-local source를 삭제하지 않는다.

Files:

* `Iris/validation/clean_checkout/contracts/repository_evidence_lightweighting_output_policy.json`
* `Iris/validation/clean_checkout/contracts/repository_runtime_lightweighting_output_policy.json`
* `Iris/validation/residual_refactor/migrate_repository_evidence.py`
* `Iris/validation/residual_refactor/execute_artifact_lifecycle.py`
* shared deterministic content-addressed archive helper/tests — 신규 또는 기존 module successor
* `.gitattributes`
* `Iris/build/description/v2/staging/`
* `Iris/build/description/v2/evidence/`
* W0가 `historical_archive`로 확정한 `Iris/build/description/v2/owner_inputs/` 및 `reviewer_inputs/` exact rows
* Change 6 historical `_docs`/output selection
* Change 4 tracked/ignored unique predecessor selection
* inactive Layer 3 generation 3개와 legacy fixed chunk 11개
* compact archive locator/inventory/verify/restore receipts

Implementation Notes:

* **Commit 7A — archive implementation/authority**: 이 plan이 채택한 `content_addressed_zip_v2` policy, deterministic writer/verifier/restore와 tests를 먼저 commit한다. 현 policy와 implementation의 ZIP compression level 및 receipt locator 불일치를 이 commit에서 교정하고 canonical member metadata/order를 포함한 새 profile을 봉인한다. deterministic ZIP, deflate level 9, canonical member metadata/order는 필수이며 선택적 표현을 사용하지 않는다. repository-stable receipt에는 absolute path를 쓰지 않는다.
* ZIP 내부는 `objects/<sha256>` unique raw body와 canonical logical path-to-object manifest로 구성해 byte-identical staging/CAS payload를 한 번만 저장한다. tracked body는 exact Git blob bytes, custody-only body는 filesystem bytes다. manifest는 source role/domain, logical path, object hash, size, mode와 source subject를 담으며 restore는 원래 logical path tree를 재구성한다.
* archive selection은 current capsule/source/data/contract/current Layer 3 generation과 gate-bound `frozen_predecessor_inputs/dvf_3_3_registry_authority_canonical_closure/current_route/manifest.json` closure를 포함할 수 없다. historical staging, 238 CAS objects + 2 refs, W0-selected historical `owner_inputs/`/`reviewer_inputs/`, historical `_docs`/output, unique predecessor, inactive Layer 3 53 files / 8,696,093 bytes를 role별 exact rows로 고정한다.
* local custody payload는 recorded custody root에서 읽고 tracked payload는 clean implementation subject의 commit identity와 결속한다. 동일 logical row의 두 subject bytes가 다르면 archive를 만들지 않고 conflict로 중단한다.
* archive 생성 후 exact logical set, unique object set, canonical order/metadata, archive SHA-256/size를 verify하고 fresh empty external restore root에 복원한다. restored logical path tree와 authoritative source bytes를 전수 비교한다. tracked restore parity는 Git blob bytes, custody restore parity는 filesystem bytes 기준이다.
* **Commit 7B — archive evidence**: opaque `store_identifier`, archive/profile/content/inventory digests, logical/unique-object counts와 bytes, restore receipt, W0/Change 1B의 plan-adopted selection 및 Change 5 transition receipt의 archive-object successor를 commit한다. Commit 7B가 Change 8 deletion commit의 ancestor여야 한다. Current-route independence는 Checkpoint B에서 이미 검증하며 evidence-only 7B에 full gate를 반복하지 않는다.
* current command와 fresh-process locator resolver는 archive가 없어도 성공한다. historical restore만 explicit opaque locator resolver를 사용하며 repository에 machine-specific path를 기록하지 않는다.

Validation:

* Commit 7A archive writer/verifier/restore focused tests와 policy/static current-route independence validation exit `0`; package source/lock/tree 변경분에 필요한 environment reseal을 마친 뒤 Changes 3–7A combined subject에서 Checkpoint B를 정확히 한 번 실행
* archive create/verify/restore exact commands 모두 exit `0`
* logical path count, unique object count, deduplicated/source/archive bytes, per-object와 per-restored-file hash parity
* path traversal, absolute path, `..`, duplicate logical path, missing object, hash mismatch, reparse/symlink ancestor와 non-empty restore root negative tests
* `historical_archive` row를 current gate/manifest/operational consumer가 계속 참조하는 fixture, gate-bound frozen fixture가 archive selection에 들어간 fixture, owner/reviewer input disposition 누락 fixture는 모두 fail-closed
* fresh process가 committed stable locator와 explicit external mapping만으로 verify/restore command를 resolve
* inactive Layer 3 53-file archive exact-set 및 logical restore parity
* Commit 7B archive evidence ancestry와 W0/Change 1B adopted selection 검증; 아직 repository-local source absence는 주장하지 않음
* Commit 7B exact archive-evidence diff/ancestry, compact locator validation과 current-route archive independence focused check exit `0`; evidence-only carrier에 별도 canonical Run A/B를 반복하지 않음

---

### Change 8 — repository-local historical payload 및 inactive Layer 3 physical removal

Purpose:

Change 5/6에서 current binding이 제거되고 Change 7에서 mandatory preservation이 검증된 exact payload만 repository-local에서 제거한다.

Files:

Removal candidates:

* `Iris/build/description/v2/staging/`
* `Iris/build/description/v2/evidence/`
* archived `Iris/build/description/v2/owner_inputs/` 및 `reviewer_inputs/` exact rows
* archived historical `_docs`/output selection
* archived old tooling/predecessor selection
* `Iris/media/lua/client/Iris/Data/IrisLayer3Generations/`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks/`

Protected/updated current files, not wholesale removal targets:

* `Iris/media/lua/client/Iris/Data/IrisLayer3DataCurrent.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunks.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataChunkIndex.lua`
* `Iris/media/lua/client/Iris/Data/IrisLayer3DataLookup.lua`
* `Iris/media/lua/client/Iris/Data/Layer3English/`
* `Iris/build/description/v2/frozen_predecessor_inputs/`와 W0-protected `description/v2/data/` rows
* `Iris/tools/package_iris.ps1`
* delete selection/receipt와 current manifests/guards
* external hash-bound synthetic candidate generation receipt와 one-off validator; repository regular schema/validator로 등록하지 않음

Implementation Notes:

* delete gate는 Commit 7B ancestry, W0/Change 1B adopted exact selection, fresh reference census, source/custody manifest identity와 archive restore PASS를 다시 확인한다. 하나라도 달라지면 아무것도 삭제하지 않는다.
* tracked deletion 전에 disposable clone에서 Commit 7B canonical precursor를 base로 exact tracked delete manifest만 적용한 **synthetic candidate commit/tree**를 만든다. candidate diff의 path/status가 proposed tracked deletion exact set과 같고, non-removal current blob IDs가 Commit 7B와 동일해야 한다.
* Candidate generator는 compact receipt를 external result root에 기록한다. Receipt는 `base_commit/tree`, `candidate_root/commit/tree`, `delete_manifest_path/sha256`, `non_removal_blob_parity_receipt_path/sha256`, producer identity를 필수로 가진다. One-off wrapper는 hash-verified receipt에서 candidate/delete/parity paths를 배정하며 shell 추측값이나 ad-hoc path를 허용하지 않는다. 이 receipt/schema/validator는 current regular validation authority로 승격하지 않는다.
* Synthetic clean checkout은 **기존 ordinary canonical full gate** Run A/B/comparator를 수행한다. 별도 cleanup execution mode, claim ID 또는 launcher field를 추가하지 않는다. External receipt가 base/candidate/tree/delete-manifest, old staging Git-object absence와 non-removal blob parity를 별도로 결속한다. Sparse checkout, unstaged deletion 또는 base commit의 Git history blob 접근은 absence proof가 아니다.
* Synthetic result의 사용 범위는 pre-delete independence evidence뿐이다. 실제 main implementation/deletion 완료 또는 release claim으로 사용할 수 없고 synthetic commit을 merge/rebase하지 않는다. External archive mapping 없이 current route가 성공해야 한다.
* **Commit 8A — tracked removal**: exact tracked rows와 current manifest/guard의 same-wave update만 포함한다. staging/CAS/history directory 자체가 아니라 selection manifest row를 literal path로 제거한다.
* **Custody action 8B — ignored/untracked/filesystem-only removal**: 동일 W0 custody root의 archived exact rows만 literal deletion한다. resolved containment/reparse 검사를 다시 수행하고 W10 custody receipt를 남긴다. 이 action의 absence를 clean worktree에서 추론하지 않는다.
* current pointer-selected `dvf33-028a3968...7145e9` 14 files / 1,954,408 bytes, stable facade/pointer/lookup, current generation descriptor/chunks와 `Layer3English`는 유지한다. archived inactive generation/fixed 53 files만 제거한다.
* `PROTECTED_CURRENT_PATHS`와 source census guard를 entire generation root 보존이 아니라 pointer-selected exact closure로 바꾼다. current runtime/package는 archive locator를 읽지 않는다.
* Change 8은 exact delete/manifest/guard diff만 가질 수 있다. `dvf_3_3_generation_contract.py`, `iris_tooling` package source/lock 또는 다른 package-owned source 수정이 필요하다고 드러나면 삭제에 섞거나 추가 중간 full-gate wave를 만들지 않고 `blocked(reason=unexpected_predelete_source_change_requires_plan_revision)`로 닫는다.
* deletion 후 durable **Commit 8C — removal receipt**에는 tracked commit, custody subject, exact removed logical rows, pre-delete hashes, post-delete literal absence와 non-overlapping bytes를 기록한다.

Validation:

* clean tracked implementation subject의 tracked selected path absence와 local custody subject의 ignored/untracked/filesystem-only selected path absence; subject/domain별 removed files/bytes 별도 산출
* current source/data/capsule/contract가 delete manifest에 포함된 사례 `0`
* synthetic candidate diff exact-set, non-removal current Git blob parity, tracked staging Git-object absence와 claim ceiling 검증
* external candidate receipt의 producer/base/candidate/delete/parity digest 검증 및 derived path의 receipt exact equality
* Checkpoint C ordinary canonical Run A/B/comparator exit `0`; working-tree-only absence나 새 regular probe mode를 사용한 사례 `0`
* dangling operational current reference와 CAS ref/object mismatch `0`
* source generation count `1`, inactive generation `0`, fixed chunk file `0`; package generation count `1`
* package content repeatability와 PowerShell 5.1/7 ordinal identity parity
* Lua syntax 및 focused generation/install/runtime compatibility tests exit `0`
* 실제 Commit 8A/8C에서 archive를 mount/resolve하지 않은 affected focused/package/Lua validation과 exact diff guard exit `0`; canonical Run A/B/comparator는 Change 9까지 반영한 terminal Checkpoint D에서 실행

---

### Change 9 — ignore/search/byte-normalization policy 단순화

Purpose:

physical separation 후 file-by-file negation allowlist를 제거하고 current source는 tracked, generated/cache는 ignored/external이라는 directory-role 규칙으로 정리한다.

Files:

* `.gitignore`
* `.rgignore`
* `.gitattributes`
* current manifest/ignore consistency validator
* `Iris/_archive/` obsolete rule set

Implementation Notes:

* staging/CAS/old tooling path가 repository에서 제거되기 전에는 대규모 ignore rewrite를 하지 않는다.
* `Iris/tooling/src`, current tests, current contracts/data/runtime는 broad ignore 아래 exact file negation으로 숨기지 않고 tracked-by-default 구조로 바꾼다.
* external output/work/archive는 repository path가 아니므로 per-file negation을 만들지 않는다. local `.venv`, cache, package/result는 directory-level ignore를 사용한다.
* `.rgignore`는 repository에 남은 historical/raw subtree만 제외하며, 삭제된 staging 경로에 대한 obsolete rule은 제거한다.
* empty `Iris/_archive/`, deleted staging/CAS/output/old tooling path의 obsolete ignore/negation을 제거한다. 존재하는 current path를 살리는 exact negation은 protected allowlist와 일치하는 경우에만 유지한다.
* deleted historical path의 obsolete `.gitattributes` rules를 제거하되 current capsule raw members/archive object schema/current source의 adopted normalization rules는 유지한다. capsule raw member pattern은 `-text`, canonical JSON/JSONL authority records는 adopted `text eol=lf` 또는 `-text` 중 하나로 명시한다.
* ignore line 수 자체를 success gate로 삼지 않지만, 현재 1,097 Iris negation의 실질적 감소와 current file visibility를 측정한다.
* ignore 판정 검증은 tracked path에도 rule match를 관측할 수 있도록 `git check-ignore --no-index -v -- <path>`를 사용한다. 일반 `git check-ignore` 결과만으로 tracked current visibility를 판정하지 않는다.

Validation:

* clean checkout current manifest path 존재성 및 `git check-ignore --no-index -v` 분류에서 current ignore rule match `0`
* generated/cache sample은 ignored, source/tooling/runtime/contract sample은 not ignored
* tracked file set과 current manifest closure 일치
* tracked current/capsule sample의 `git check-attr -a`, Git blob SHA와 checkout materialization contract parity; `core.autocrlf` 변화에도 authority blob identity 불변
* ordinary `rg` current search에서 externalized historical payload가 나타나지 않음
* Change 9 current visibility/attribute/package focused validation exit `0`; exact full gate Run A/B/comparator는 Change 10 terminal Checkpoint D에서 한 번 실행

---

### Change 10 — terminal clean-checkout validation, measurement 및 closeout

Purpose:

모든 destructive/authority change 이후 current behavior/contract, archive integrity와 실제 repository 감축량을 exact terminal subject에 결속한다.

Files:

* terminal environment authority/locator
* `Iris/tooling/pyproject.toml`, `Iris/tooling/uv.lock`, `pytest.ini`, `.gitattributes`
* `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json`
* immutable environment authority record와 external wheel/environment receipt
* external Run A/Run B/comparator/package/archive receipts
* compact closeout/census/archive locator record
* repository-external Change 2A/2B selection manifest와 retained-residue-exception manifest의 stable digests/compact summary
* `docs/DECISIONS.md`
* `docs/ARCHITECTURE.md`
* `docs/ROADMAP.md`

Implementation Notes:

* terminal implementation commit을 clean clone으로 checkout하고 committed environment를 preflight한다. external root/content manifest가 유효하고 terminal commit의 project/lock/package-source identity가 record와 같으면 existing locator를 읽기만 한다. identity가 바뀌었거나 environment가 부재/invalid일 때만 Change 10 environment sub-unit이 repository-disjoint allocator roots에서 새 immutable wheel/environment receipt를 만든다. repository-local `.venv`, uv/cache/build output은 허용하지 않는다.
* environment reseal이 필요한 wave는 **implementation commit -> external wheel/environment 생성 -> receipt 작성 -> immutable authority record commit -> stable locator만 갱신하는 authority-only commit -> 가장 가까운 다음 Checkpoint의 full gate** 순서를 사용한다. locator commit에는 package source/lock 변경을 섞지 않으며 reseal 자체만으로 별도 canonical Run A/B를 추가하지 않는다.
* full gate는 새 PowerShell process에서 committed stable locator를 다시 읽어 external receipt/wheel/environment를 해석해야 한다. 현재 shell의 임시 변수나 이전 process state만으로 성공하면 실패다.
* exact full gate Run A/Run B, deterministic comparator, standalone commands, installed tooling tests/CLI, Lua syntax와 current package를 수행한다.
* archive store가 연결된 explicit restore 검증과 archive가 없는 current route 검증을 둘 다 수행한다.
* W0와 동일한 dual-subject census를 W10에 반복한다. tracked implementation subject는 같은 lineage의 terminal clean commit과 비교하고 local custody subject는 동일 canonical custody root와 비교한다. removed bytes를 tracked, ignored, untracked, filesystem-only, generated, archive source, unique archive object, capsule domains별로 기록하고 겹쳐 합산하지 않는다.
* W10은 `frozen_predecessor_inputs/dvf_3_3_registry_authority_canonical_closure/current_route/manifest.json`의 gate-pinned digest와 current consumer가 유지됨을 확인한다. `owner_inputs/`와 `reviewer_inputs/`의 W0 exact row set은 archive evidence 또는 retained-exception manifest 중 정확히 하나에 존재해야 하고, `build/tests/` 및 `description/v2/data/` current-required rows는 protected closure와 일치해야 한다.
* W10은 current capsule이 hard ceiling 2,359,296 bytes 이하인지 다시 확인한다. repository-local successor overhead는 `max(2 MiB, tracked physical-removal source bytes의 0.5%)` 이하여야 하며, current capsule raw bytes와 archive source/unique/compressed bytes는 이 overhead에 중복 합산하지 않고 각각 별도 보고한다.
* final closeout은 validated/out_of_scope/unvalidated_but_in_scope ceiling, non-claims, retained exceptions와 unresolved inventory를 기록한다. `unsupported_keep`, `remaining_eligible_removal`, `unimplemented_removal`은 모두 0이어야 한다.
* governance docs는 terminal result를 기록할 뿐 과거 sealed record를 rewrite하지 않는다.

Validation:

* §7의 모든 automated validation exit `0`
* final current closure missing/ambiguous/unclassified/dangling `0`
* terminal source checkout post-status clean
* tracked clean subject와 local custody subject 각각의 file/byte census, archive logical/unique/compressed bytes와 current capsule retained bytes 산출
* current capsule `<= 2,359,296 bytes`; repository-local successor overhead `<= max(2 MiB, tracked physical-removal source bytes의 0.5%)`
* `unsupported_keep=0`, `remaining_eligible_removal=0`, `unimplemented_removal=0`
* frozen gate fixture missing/hash drift `0`; owner/reviewer input disposition 누락·중복 `0`; `build/tests/`와 `description/v2/data/` current-required protection mismatch `0`
* clean implementation subject의 `Iris/` residue, 2A approved root exact rows와 local custody subject의 2B approved non-Git residue exact `0`; out-of-scope repository/cache는 별도 exception inventory
* residue normalizer/matcher의 Windows PowerShell 5.1 및 PowerShell 7 parity: in-root normalization, case-insensitive root match, sibling-prefix escape, `..`, rooted result, file/subtree exception fixtures
* independent diff review에서 actionable finding `0`일 때만 `complete` closeout 후보

---

## 7. Validation Plan

### Automated Validation

#### 7.1 General execution rules

* 모든 명령은 PowerShell에서 실행하고 native command마다 `$LASTEXITCODE -eq 0`을 확인한다.
* Python/uv, Git, PowerShell 또는 Lua checker가 없으면 PASS가 아니라 `blocked`다.
* work/result/package/archive/restore root는 repository와 disjoint한 create-new allocator-owned leaf를 사용한다. 기존 leaf를 자동 삭제하거나 재사용하지 않으며 allocator ledger 밖의 병렬 leaf를 만들지 않는다.
* baseline과 terminal current authority는 `Iris/validation/clean_checkout/invoke_receipt_bound_full_gate.ps1`이 읽는 exact `full_repository_gate.json`이다.
* test count는 관측값이며 고정 목표가 아니다. selection identity, dependency closure, failure meaning과 canonical result가 authority다.
* clean Git worktree와 local custody checkout을 명령 시작 시 `Resolve-Path`, `git -C <subject-root> rev-parse --show-toplevel`, `git -C <subject-root> rev-parse HEAD`로 재검증한다. physical cleanup 명령은 clean worktree에서 실행하지 않고, tracked edits/commits는 custody checkout에서 실행하지 않는다. cwd-dependent bare Git 호출은 금지한다.
* terminal residue 검사는 clean/custody subject 각각의 `Iris/`, Change 2A/2B가 승인한 root exact rows와 full-gate contract-derived clean-subject `.dvf_tmp/` exact row로 한정한다. `.codex-worktrees`, other modules, unrelated root `.pytest_cache`/`__pycache__`/`.pyc`를 recurse하지 않는다. 그 밖의 repo-root row는 W0 manifest에 등재된 literal path만 검사한다.

#### 7.2 Current gate and determinism

Canonical full gate Run A/B/comparator는 변경 commit마다 반복하지 않고 다음 네 checkpoint에서만 수행한다.

| Checkpoint | Exact subject | Purpose |
| --- | --- | --- |
| A — baseline | hardening을 포함한 S0 또는 conditional Change 0E authority commit | clean current baseline과 W0 progression admission |
| B — successor binding | Changes 3–7A의 current owner/capsule/output/tooling/archive implementation이 함께 반영된 commit | historical payload 없이도 current authority가 독립적으로 작동하고 archive tooling이 current route를 오염시키지 않음을 증명 |
| C — pre-delete candidate | Checkpoint B/7B를 base로 exact delete manifest만 적용한 disposable synthetic commit | 삭제된 tree에서 existing canonical gate가 그대로 PASS함을 사전 증명 |
| D — terminal | 실제 removal, ignore/attribute 정리와 terminal authority가 반영된 implementation commit | 최종 current closure와 deterministic result 봉인 |

각 checkpoint는 다음을 수행한다.

1. receipt-bound full gate Run A
2. 독립 work/result root의 Run B
3. `invoke_deterministic_compare.ps1`
4. source/external mutation audit
5. required standalone 4개 direct command identity 확인

Run A/B가 각각 exit `0`, comparator canonical result equality, missing/unmapped/ambiguous `0`, source mutation `0`일 때만 해당 checkpoint를 PASS로 기록한다. Checkpoint C는 candidate commit에 기존 ordinary canonical claim/command를 그대로 실행하되 external candidate receipt가 그 결과의 사용 범위를 pre-delete evidence로 제한한다.

그 밖의 Change/commit은 affected focused tests, exact diff/reference guard, package/Lua/archive-specific validation과 mutation audit만 수행한다. Evidence-only, locator-only, removal-receipt-only, documentation-only carrier에는 full gate를 다시 실행하거나 PASS를 상속하지 않는다. Package source/lock/tree가 바뀌어 environment reseal이 필요한 경우에도 새 authority locator를 만든 뒤 가장 가까운 다음 checkpoint에서 한 번만 canonical Run A/B를 수행한다.

Change 2 progression에는 **Checkpoint A baseline PASS**가 절대 전제다. Baseline FAIL은 W0 census 완료만 허용하고 cleanup/rebind/archive implementation은 허용하지 않는다. 별도 remediation이 PASS를 복구한 뒤 새 S0/W0로 다시 시작한다.

Change 2A와 2B는 cleanup 전후 동일 scope-limited focused command의 exit/status/failure meaning과 clean subject Git tree/diff identity를 확인한다. 2B에서 tracked/config delta가 생기면 fail-closed한다. Change 2A만으로 별도 canonical Run A/B를 반복하지 않는다.

§7.3에서 checkpoint별 Run A/Run B allocation receipt를 만든 뒤 exact Run A/B/comparator는 다음 command shape를 사용한다. `$runAAllocation`과 `$runBAllocation`은 allocator receipt를 hash-verify해 읽은 객체이며, work/result/orchestration/compare path를 임의의 병렬 leaf로 만들지 않는다. Allocator가 만든 root는 호출 직전 empty여야 하고 orchestration receipt file만 absent여야 한다.

```powershell
$commit = (& git -C $cleanSubjectRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'cannot resolve exact gate commit' }
$locatorPath = Join-Path $cleanSubjectRoot 'Iris\validation\clean_checkout\authority\responsibility_refactor_environment_current.json'
$locator = Get-Content -LiteralPath $locatorPath -Raw | ConvertFrom-Json
$recordPath = Join-Path $cleanSubjectRoot ([string]$locator.record_path)
if ((Get-FileHash -LiteralPath $recordPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne [string]$locator.record_sha256) {
    throw 'environment authority record hash mismatch'
}
$record = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
$environmentReceipt = [string]$record.environment_contract.immutable_environment_receipt_path
$environmentRoot = [string]$record.environment_contract.external_environment_root
if (-not (Test-Path -LiteralPath $environmentReceipt -PathType Leaf) -or -not (Test-Path -LiteralPath $environmentRoot -PathType Container)) {
    throw 'environment_authority_unavailable: committed receipt or environment root is absent'
}
if ((Get-FileHash -LiteralPath $environmentReceipt -Algorithm SHA256).Hash.ToLowerInvariant() -ne
    [string]$record.environment_contract.immutable_environment_receipt_sha256) {
    throw 'environment_authority_unavailable: immutable environment receipt hash mismatch'
}
$workA = [IO.Path]::GetFullPath([string]$runAAllocation.roots.work)
$resultA = [IO.Path]::GetFullPath([string]$runAAllocation.roots.result)
$workB = [IO.Path]::GetFullPath([string]$runBAllocation.roots.work)
$resultB = [IO.Path]::GetFullPath([string]$runBAllocation.roots.result)
$receiptA = Join-Path ([string]$runAAllocation.roots.orchestration_result) 'run-a-orchestration.json'
$receiptB = Join-Path ([string]$runBAllocation.roots.orchestration_result) 'run-b-orchestration.json'
$compareRoot = [IO.Path]::GetFullPath([string]$runAAllocation.roots.compare_result)

powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1 `
    -RepositoryRoot $cleanSubjectRoot -Commit $commit -ClaimId 'iris-lightweighting-current' `
    -EnvironmentReceipt $environmentReceipt `
    -WorkRoot $workA -ResultRoot $resultA `
    -OrchestrationReceipt $receiptA
if ($LASTEXITCODE -ne 0) { throw 'full gate Run A failed' }

powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_receipt_bound_full_gate.ps1 `
    -RepositoryRoot $cleanSubjectRoot -Commit $commit -ClaimId 'iris-lightweighting-current' `
    -EnvironmentReceipt $environmentReceipt `
    -WorkRoot $workB -ResultRoot $resultB `
    -OrchestrationReceipt $receiptB
if ($LASTEXITCODE -ne 0) { throw 'full gate Run B failed' }

powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\validation\clean_checkout\invoke_deterministic_compare.ps1 `
    -RepositoryRoot $cleanSubjectRoot -Commit $commit -ClaimId 'iris-lightweighting-current' `
    -EnvironmentReceipt $environmentReceipt `
    -RunAOrchestrationReceipt $receiptA -RunBOrchestrationReceipt $receiptB `
    -AttemptRoot $compareRoot
if ($LASTEXITCODE -ne 0) { throw 'full gate deterministic comparison failed' }
```

Checkpoint C는 canonical validation system을 변경하지 않는다. One-off wrapper가 external synthetic-generation receipt와 child manifest hashes를 검증한 뒤 candidate root/commit을 대상으로 기존 ordinary gate command shape를 그대로 사용한다.

```powershell
$syntheticReceiptPath = (Resolve-Path -LiteralPath $SyntheticGenerationReceipt).Path
if ((Get-FileHash -LiteralPath $syntheticReceiptPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $SyntheticGenerationReceiptSha256) {
    throw 'synthetic generation receipt hash mismatch'
}
$synthetic = Get-Content -LiteralPath $syntheticReceiptPath -Raw | ConvertFrom-Json
$candidateRoot = (Resolve-Path -LiteralPath ([string]$synthetic.candidate_root)).Path
$candidateCommit = (& git -C $candidateRoot rev-parse HEAD).Trim()
$candidateTree = (& git -C $candidateRoot rev-parse 'HEAD^{tree}').Trim()
if ($LASTEXITCODE -ne 0 -or $candidateCommit -ne [string]$synthetic.candidate_commit -or
    $candidateTree -ne [string]$synthetic.candidate_tree) {
    throw 'synthetic candidate identity mismatch'
}
$ancestry = ((& git -C $candidateRoot rev-list --parents -n 1 $candidateCommit).Trim() -split '\s+')
if ($LASTEXITCODE -ne 0 -or $ancestry.Count -ne 2 -or $ancestry[1] -ne [string]$synthetic.base_commit) {
    throw 'synthetic candidate must have the approved base as its sole parent'
}
if ((& git -C $candidateRoot status --porcelain=v1 --untracked-files=all).Count -ne 0) {
    throw 'synthetic candidate checkout must be clean'
}
foreach ($binding in @(
    @{ Path = [string]$synthetic.delete_manifest_path; Sha = [string]$synthetic.delete_manifest_sha256 },
    @{ Path = [string]$synthetic.non_removal_blob_parity_receipt_path; Sha = [string]$synthetic.non_removal_blob_parity_receipt_sha256 }
)) {
    if ((Get-FileHash -LiteralPath $binding.Path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $binding.Sha) {
        throw 'synthetic child receipt hash mismatch'
    }
}

$runAAllocation = New-IrisWaveAllocation -RunLabel 'candidate-run-a' `
    -ClaimId 'iris-lightweighting-current' -AttemptId ('checkpoint-c-' + $candidateCommit.Substring(0, 12)) `
    -AllocationProfile checkpoint
$runBAllocation = New-IrisWaveAllocation -RunLabel 'candidate-run-b' `
    -ClaimId 'iris-lightweighting-current' -AttemptId ('checkpoint-c-' + $candidateCommit.Substring(0, 12)) `
    -AllocationProfile checkpoint
$cleanSubjectRoot = $candidateRoot
$commit = $candidateCommit
# Continue with the unchanged ordinary Run A/B/comparator command shape above.
```

External synthetic receipt는 base/candidate/delete/parity identity를 기록하고 성공한 candidate result의 사용 범위를 pre-delete evidence로만 제한한다. 이를 current gate schema, regular validation taxonomy 또는 영구 execution mode에 추가하지 않는다.

#### 7.3 Wave allocations and installed Python tooling

`$recordedCustodySubjectRoot`는 현재 shell에서 추측한 path가 아니라 hash-verified custody subject manifest에서 읽은 canonical root다. 기존 `allocate_repository_runtime_lightweighting_roots.ps1`을 모든 external work/result/package/test/environment allocation의 유일한 allocator로 사용한다. separator-aware 양방향 repository disjointness, reparse-ancestor, prior-ledger reuse와 create-new/empty 조건을 통과하지 못하면 별도 leaf를 손으로 만들지 않는다. `git rev-parse`가 성공하기 전에 commit을 allocation attempt ID에 삽입하지 않는다.

Allocation identity는 이 plan의 fixed checkpoint table과 repository-external hash-verified execution manifest가 `$allocationClaimId`, `$allocationAttemptId`, `$allocationProfileA`, `$allocationProfileB`로 전달한다. 일회성 lightweighting allocation을 위해 repository-regular execution schema를 추가하지 않는다. Wrapper는 아래 mapping과 다른 free-form 값, 중간 checkpoint의 `terminal` profile, terminal checkpoint의 `checkpoint` profile을 거부한다.

| Execution unit | `ClaimId` / `AttemptId` | Allocation profile |
| --- | --- | --- |
| Change 0E environment build | `iris-lightweighting-environment-admission` / `change-0e-env-<commit12>` | environment allocation 1개: `checkpoint` |
| Checkpoint A baseline | `iris-lightweighting-current` / `checkpoint-a-<commit12>` | Run A/B 각각 `checkpoint` |
| Change 1A inventory / Change 7 archive / Change 10 terminal inventory | `iris-lightweighting-<wave-purpose>` / `<wave-purpose>-<commit12>` | purpose별 1개: `physical-capacity` |
| Checkpoint B successor binding | `iris-lightweighting-current` / `checkpoint-b-<commit12>` | Run A/B 각각 `checkpoint` |
| Checkpoint C synthetic candidate | `iris-lightweighting-current` / `checkpoint-c-<candidate12>` | candidate Run A/B 각각 `checkpoint` |
| Checkpoint D terminal | `iris-lightweighting-terminal` / `checkpoint-d-<commit12>` | A=`terminal-run-a`, B=`terminal-run-b` |

Checkpoint profile이 만든 root 중 사용하지 않는 axis가 있으면 allocation-usage receipt에 `unused`, empty verification, cleanup eligibility를 기록한다. terminal-run-b의 built-in `lifecycle_disposition`도 같은 receipt에 결속한다. Allocator ledger에 없는 병렬 `$runRoot\full-gate`, `$runRoot\package`, `$runRoot\pre-delete-independence-probe` leaf는 만들지 않는다.

```powershell
$cleanSubjectRoot = (Resolve-Path -LiteralPath '.').Path
$custodySubjectRoot = (Resolve-Path -LiteralPath $recordedCustodySubjectRoot).Path
$targetCommit = (& git -C $cleanSubjectRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'cannot resolve target commit before external allocation' }
$commit = $targetCommit
if ([string]::IsNullOrWhiteSpace($env:IRIS_EXTERNAL_VALIDATION_ROOT)) {
    throw 'IRIS_EXTERNAL_VALIDATION_ROOT is required'
}
$externalBase = [IO.Path]::GetFullPath($env:IRIS_EXTERNAL_VALIDATION_ROOT)
$allocationLedger = Join-Path $externalBase 'iris-lightweighting-allocation-ledger.jsonl'
$protectedRootsJson = ConvertTo-Json -Compress @($cleanSubjectRoot, $custodySubjectRoot)

function New-IrisWaveAllocation(
    [string]$RunLabel,
    [string]$ClaimId,
    [string]$AttemptId,
    [ValidateSet('physical-capacity', 'checkpoint', 'terminal-run-a', 'terminal-run-b')][string]$AllocationProfile
) {
    if ([string]::IsNullOrWhiteSpace($ClaimId) -or [string]::IsNullOrWhiteSpace($AttemptId)) {
        throw 'wave-specific ClaimId and AttemptId are required'
    }
    $allocationReceipt = Join-Path $externalBase ('allocation-' + $RunLabel + '-' + [Guid]::NewGuid().ToString('N') + '.json')
    $allocatorOutput = @(powershell -NoProfile -ExecutionPolicy Bypass `
        -File (Join-Path $cleanSubjectRoot 'Iris\validation\clean_checkout\allocate_repository_runtime_lightweighting_roots.ps1') `
        -ProtectedRepositoryRootsJson $protectedRootsJson `
        -ClaimId $ClaimId `
        -AttemptId ($AttemptId + '-' + $RunLabel) `
        -AllocationProfile $AllocationProfile `
        -ExternalParent $externalBase `
        -AllocationLedger $allocationLedger `
        -Out $allocationReceipt)
    if ($LASTEXITCODE -ne 0) { throw "external root allocation failed: $RunLabel" }
    $allocation = Get-Content -LiteralPath $allocationReceipt -Raw | ConvertFrom-Json
    if ([string]$allocation.status -ne 'PASS' -or [string]$allocation.claim_id -ne $ClaimId -or
        [string]$allocation.attempt_id -ne ($AttemptId + '-' + $RunLabel) -or
        [string]$allocation.allocation_profile -ne $AllocationProfile) {
        throw "external allocation identity mismatch: $RunLabel"
    }
    $allocation | Add-Member -NotePropertyName allocation_receipt_path -NotePropertyValue $allocationReceipt
    $allocation | Add-Member -NotePropertyName allocation_receipt_sha256 `
        -NotePropertyValue (Get-FileHash -LiteralPath $allocationReceipt -Algorithm SHA256).Hash.ToLowerInvariant()
    return $allocation
}

# Run these two calls only for a canonical gate after any authority-only locator commit.
# An environment-reseal sub-unit skips them and uses the dedicated allocation below.
$runAAllocation = New-IrisWaveAllocation -RunLabel 'run-a' -ClaimId $allocationClaimId `
    -AttemptId $allocationAttemptId -AllocationProfile $allocationProfileA
$runBAllocation = New-IrisWaveAllocation -RunLabel 'run-b' -ClaimId $allocationClaimId `
    -AttemptId $allocationAttemptId -AllocationProfile $allocationProfileB
```

environment 생성은 allocation과 별개로 **조건부 owner branch**다.

* `reuse_committed_environment`: committed locator/record/receipt/root가 존재하고 receipt content manifest가 유효하며 exact target commit의 `pyproject.toml`, `uv.lock`, package source tree가 record binding과 일치하면 새 environment를 만들지 않는다. ordinary Change 1A/1B/2/5/6/7/8/9 gate는 이 branch에서 locator를 읽기만 한다.
* `reseal_environment`: Change 0E이거나, Change 3/4/7A/10 등에서 `pyproject.toml`, `uv.lock` 또는 installed `iris_tooling` package source tree identity가 바뀐 경우에만 실행한다. implementation commit -> dedicated environment allocation -> wheel/environment/receipt -> authority-only locator commit -> 가장 가까운 다음 Checkpoint의 새 clean checkout full gate 순서를 사용한다.
* locator가 유효하지 않은데 source/lock/package tree도 바뀐 일반 wave는 즉석 reseal하지 않는다. 그 wave의 declared environment sub-unit으로 돌아가거나 `blocked(environment_authority_unavailable)`를 기록한다.

reseal owner는 별도 `checkpoint` environment allocation의 `uv_environment`, `uv_cache`, `package_result`, `test_output` roots를 직접 사용한다. 아래 `$environmentAllocationClaimId`, `$environmentAllocationAttemptId`, `$environmentAuthorityWaveId`는 Change 0E 또는 package-source-changing wave manifest의 required values다.

```powershell
$environmentAllocation = New-IrisWaveAllocation -RunLabel 'environment' `
    -ClaimId $environmentAllocationClaimId -AttemptId $environmentAllocationAttemptId `
    -AllocationProfile checkpoint
$env:UV_PROJECT_ENVIRONMENT = [IO.Path]::GetFullPath([string]$environmentAllocation.roots.uv_environment)
$env:UV_CACHE_DIR = [IO.Path]::GetFullPath([string]$environmentAllocation.roots.uv_cache)
$env:PYTHONNOUSERSITE = '1'
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue

$wheelRoot = [IO.Path]::GetFullPath([string]$environmentAllocation.roots.package_result)
$testOutputRoot = [IO.Path]::GetFullPath([string]$environmentAllocation.roots.test_output)
$toolingProject = Join-Path $cleanSubjectRoot 'Iris\tooling'
uv build --project $toolingProject --wheel --out-dir $wheelRoot
if ($LASTEXITCODE -ne 0) { throw 'iris_tooling wheel build failed' }
$wheel = @(Get-ChildItem -LiteralPath $wheelRoot -Filter '*.whl' -File)
if ($wheel.Count -ne 1) { throw 'expected exactly one iris_tooling wheel' }

uv sync --project $toolingProject --locked --no-editable
if ($LASTEXITCODE -ne 0) { throw 'iris_tooling external locked install failed' }
uv pip install --python (Join-Path $env:UV_PROJECT_ENVIRONMENT 'Scripts\python.exe') --reinstall $wheel[0].FullName
if ($LASTEXITCODE -ne 0) { throw 'exact wheel install failed' }
uv run --project $toolingProject --no-sync python -B -m pytest (Join-Path $toolingProject 'tests') `
    --junitxml (Join-Path $testOutputRoot 'iris-tooling-tests.xml')
if ($LASTEXITCODE -ne 0) { throw 'iris_tooling tests failed' }
uv run --project $toolingProject --no-sync python -B -m iris_tooling --help
if ($LASTEXITCODE -ne 0) { throw 'iris_tooling CLI probe failed' }

$sourceCommit = (& git -C $cleanSubjectRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'cannot resolve implementation commit' }
$sourceTree = (& git -C $cleanSubjectRoot rev-parse 'HEAD^{tree}').Trim()
if ($LASTEXITCODE -ne 0) { throw 'cannot resolve implementation tree' }
$receiptPath = Join-Path $testOutputRoot 'environment_receipt.json'
$safeEnvironmentWaveId = $environmentAuthorityWaveId -replace '[^A-Za-z0-9_-]', '_'
$authorityRecord = Join-Path $cleanSubjectRoot ('Iris\validation\clean_checkout\authority\responsibility_refactor_environment_iris_lightweighting_' + $safeEnvironmentWaveId + '.json')
$currentLocator = Join-Path $cleanSubjectRoot 'Iris\validation\clean_checkout\authority\responsibility_refactor_environment_current.json'
$externalPython = Join-Path $env:UV_PROJECT_ENVIRONMENT 'Scripts\python.exe'

& $externalPython -B (Join-Path $cleanSubjectRoot 'Iris\validation\clean_checkout\write_environment_receipt.py') `
    --environment-root $env:UV_PROJECT_ENVIRONMENT `
    --project (Join-Path $toolingProject 'pyproject.toml') `
    --lock (Join-Path $toolingProject 'uv.lock') `
    --wheel $wheel[0].FullName `
    --source-commit $sourceCommit `
    --source-tree $sourceTree `
    --out $receiptPath `
    --authority-record-out $authorityRecord `
    --current-locator-out $currentLocator
if ($LASTEXITCODE -ne 0) { throw 'environment authority writer failed' }
```

위 command는 reseal owner unit에서만 실행한다. 생성된 versioned authority record와 locator만 authority-only commit으로 채택한다. 이후 가장 가까운 다음 Checkpoint에서 새 process와 새 clean checkout이 §7.3 allocator로 gate Run A/B roots를 배정하고 §7.2 full gate를 실행한다. 동일 versioned authority filename을 덮어쓰지 않는다. Change 1A와 reuse branch는 이 writer block을 절대로 호출하지 않는다.

Change 4에서는 IAR runner/validator successor, generation identity, arbitrary-cwd import와 explicit repository context를 focused tests로 추가한다. terminal에서 `uv run`은 모두 `--no-sync`를 사용해 검증 중 repository 또는 environment를 암묵적으로 바꾸지 않는다.

#### 7.4 Lua and package

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
if ($LASTEXITCODE -ne 0) { throw 'Lua syntax validation failed' }

$packageRoot = [IO.Path]::GetFullPath([string]$runAAllocation.roots.package_result)
if (@(Get-ChildItem -LiteralPath $packageRoot -Force -ErrorAction Stop).Count -ne 0) {
    throw 'allocator-owned package root must be empty before packaging'
}
powershell -NoProfile -ExecutionPolicy Bypass -File .\Iris\tools\package_iris.ps1 `
    -OutputRoot $packageRoot `
    -Clean `
    -Zip `
    -PackageApplicability current_runtime_payload
if ($LASTEXITCODE -ne 0) { throw 'Iris package projection failed' }
```

Terminal package는 위 exact external `-OutputRoot` command로만 생성한다. package manifest는 current generation 정확히 1개, stable facade/pointer/descriptor/chunks, thin `IrisData` adapter, Python/old generations/fixed chunks 0을 증명해야 한다.

#### 7.5 Archive and restore

Change 7 archive wave는 `physical-capacity` allocation을 별도로 만들고 `archive_store`, `restore_result`, `inventory_result`, `promotion_result`를 archive create/restore/inventory/promotion command에 직접 전달한다. Change 10 terminal inventory는 새 `physical-capacity` allocation의 `terminal_inventory_result`를 사용한다. path를 `$runRoot` 아래에서 다시 조합하지 않는다.

```powershell
$archiveAllocation = New-IrisWaveAllocation -RunLabel 'archive' `
    -ClaimId $archiveAllocationClaimId -AttemptId $archiveAllocationAttemptId `
    -AllocationProfile physical-capacity
$archiveStore = [IO.Path]::GetFullPath([string]$archiveAllocation.roots.archive_store)
$restoreRoot = [IO.Path]::GetFullPath([string]$archiveAllocation.roots.restore_result)
$archiveInventoryRoot = [IO.Path]::GetFullPath([string]$archiveAllocation.roots.inventory_result)
$archivePromotionRoot = [IO.Path]::GetFullPath([string]$archiveAllocation.roots.promotion_result)
```

* exact selection dry-run과 current-path exclusion
* deterministic content-addressed archive create와 logical-path-to-object manifest
* archive hash/logical member/unique object/canonical metadata verify와 deduplication ratio
* tracked source는 Git blob bytes, custody-only source는 filesystem bytes로 archive identity 계산
* fresh empty external root에 original logical path tree restore + per-file/per-object authoritative hash verify
* durable compact evidence promotion
* archive-evidence ancestry/owner-approval delete prerequisite
* clean tracked subject와 local custody subject의 tracked/ignored/untracked/filesystem-only physical deletion 분리
* same-subject post-delete literal absence/reference audit
* committed locator를 새 process에서 resolve하는 verify/restore probe
* nested `.git`/`.hg`/`.svn`, long-path enumeration error와 partial traversal negative probe

정책과 implementation이 현재 불일치하는 ZIP level/receipt locator는 **Change 7A**에서 교정하고 그 implementation/authority commit의 canonical full gate가 PASS한 뒤에만 archive create/verify/restore를 수행한다. archive PASS와 Commit 7B evidence ancestry가 모두 성립하기 전에는 Change 8을 시작하지 않는다. Change 8은 archive implementation 교정의 owner가 아니다.

#### 7.6 Boundary and negative validation

* current capsule file 누락/변조
* capsule digest row 누락/operation class 위조/budget 초과
* `move_to_current_owner` successor path/owner/digest 누락 또는 mismatch
* `historical_archive` row가 current gate/manifest/operational consumer에 다시 결속되는 경우
* synthetic candidate commit/tree의 old staging Git-object 부재, base/candidate non-removal blob mismatch와 working-tree-only absence 거부
* external archive 부재
* stale full-table `IrisData.lua` install 시도
* inactive Layer 3 generation 또는 fixed chunk package 주입
* old `tools/build` import/command/path consumer 주입
* broad ignore로 current file 은닉
* `main.py` decision과 다른 branch 재유입 또는 clean-checkout 결손 import 재유입
* archive path traversal, duplicate logical member, duplicate/missing object, hash collision/mismatch, reparse ancestor와 non-empty restore root
* nested VCS marker, long-path/access-denied enumeration을 silent skip하는 시도
* clean worktree absence를 custody deletion receipt로 제출하거나 서로 다른 root delta를 비교하는 시도

각 negative case는 expected failure domain/code 또는 non-zero exit를 확인한다. archive 부재는 historical restore에는 실패해야 하지만 current full gate에는 영향을 주지 않아야 한다. digest successor는 predecessor raw-path failure parity가 아니라 versioned claim-transition matrix에 정의한 successor failure domain을 검증한다.

#### 7.7 Final census

W0/W10에 subject별 동일한 방식으로 다음을 기록한다.

* clean implementation subject의 Iris tracked/physical files와 bytes, commit/tree/status
* 동일 local custody subject의 Iris tracked-observation/ignored/untracked/filesystem-only/reparse files와 bytes. tracked-observation은 두 subject의 충돌 탐지에만 쓰고 removal delta에는 포함하지 않음
* staging, CAS, `_docs`, output, old tooling, Layer 3 predecessor surface
* `Iris/test`, `Iris/evidence`, `Iris/input`, `Iris/_dev`, `Iris/_archive`, `Iris/build/tests`, description tests `.tmp/.tmp_tests/.dvf_tmp`, `tools/` 전체
* `description/v2/frozen_predecessor_inputs`, `owner_inputs`, `reviewer_inputs`, `data`의 subject/domain별 exact rows와 bytes
* repository root `.tmp` 중 approved Iris-owned selection 및 full-gate contract-derived clean-subject `.dvf_tmp` exact row; `graphify-out`와 `console_log.txt`는 out-of-scope 관측값으로만 고정
* current capsule raw files/bytes와 digest-only rows/source bytes
* external archive logical files/source bytes, unique objects/bytes, compressed bytes
* `.gitignore` total/Iris/negation rule count와 `.gitattributes` blob/normalization rule count

중복 domain의 감소량을 하나의 총합으로 더하지 않는다. byte/file 감소와 current closure PASS를 함께 보고하되 runtime/token 개선률은 별도 측정 없이는 주장하지 않는다.

Terminal residue는 plan-owned surface만 검사한다. terminal wrapper는 `CleanSubjectRoot`, `CustodySubjectRoot`, `W10SubjectManifest`/`W10SubjectManifestSha256`, `Change2ASelectionManifest`/digest, `Change2BSelectionManifest`/digest, `RetainedResidueExceptionManifest`/digest를 required CLI inputs로 받는다. 아래 `$cleanSubjectRootBindingSha256`과 `$custodySubjectRootBindingSha256`는 hash-verified W10 subject manifest의 exact subject rows에서 배정하며 shell에서 계산하거나 추측하지 않는다. selection/exception 변수도 각 hash-verified manifest의 `rows`에서만 배정한다.

`$change2ASelection`, `$change2BSelection`, `$retainedResidueExceptions`는 repository-external `subject_scoped_residue_manifest_v1` one-off format으로 검증한 manifest rows다. 이 명칭은 실행 중 외부 파일의 형식 버전일 뿐 repository-regular schema나 validation authority가 아니다. 각 row는 `subject_id`, `subject_root_binding_sha256`, `normalized_repository_relative_path`, `exception_kind(file_exact|directory_exact|directory_subtree)`, decision row/reason을 가진다. selection과 exception이 동일 path semantics를 사용하도록 field 이름을 공통 유지한다. durable row에는 absolute path를 넣지 않으며, runtime의 `$cleanSubjectRoot`와 `$custodySubjectRoot`는 hash-verified W0/W10 subject binding으로만 해석한다. `file_exact`/`directory_exact`는 entry kind와 정규화 상대경로가 모두 완전 일치해야 하고, `directory_subtree`는 해당 directory 자체 또는 `/` boundary 뒤 descendant에만 일치한다. 서로 다른 subject ID나 binding digest, `..`, rooted path, separator가 정규화되지 않은 row는 fail-closed한다.

`.codex-worktrees`, other modules와 unrelated root cache는 enumerate하지 않는다. 검사 이름에는 `.venv`, `__pycache__`, `.tmp`, `.tmp_tests`, `.dvf_tmp`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `uv-cache`와 `*.pyc`를 포함한다. enumeration 오류는 residue 0이 아니라 `blocked`다.

```powershell
$cleanSubjectRoot = (Resolve-Path -LiteralPath $CleanSubjectRoot).Path
$custodySubjectRoot = (Resolve-Path -LiteralPath $CustodySubjectRoot).Path
$w10SubjectManifestPath = (Resolve-Path -LiteralPath $W10SubjectManifest).Path
if ((Get-FileHash -LiteralPath $w10SubjectManifestPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $W10SubjectManifestSha256) {
    throw 'W10 subject manifest hash mismatch'
}
$w10SubjectManifestPayload = Get-Content -LiteralPath $w10SubjectManifestPath -Raw | ConvertFrom-Json
$cleanSubjectRows = @($w10SubjectManifestPayload.subjects | Where-Object { [string]$_.subject_id -eq 'clean_implementation' })
$custodySubjectRows = @($w10SubjectManifestPayload.subjects | Where-Object { [string]$_.subject_id -eq 'local_custody' })
if ($cleanSubjectRows.Count -ne 1 -or $custodySubjectRows.Count -ne 1) {
    throw 'W10 subject manifest must bind each terminal subject exactly once'
}
if (-not [IO.Path]::GetFullPath([string]$cleanSubjectRows[0].canonical_root).TrimEnd([char[]]@('\', '/')).Equals(
        $cleanSubjectRoot.TrimEnd([char[]]@('\', '/')), [StringComparison]::OrdinalIgnoreCase) -or
    -not [IO.Path]::GetFullPath([string]$custodySubjectRows[0].canonical_root).TrimEnd([char[]]@('\', '/')).Equals(
        $custodySubjectRoot.TrimEnd([char[]]@('\', '/')), [StringComparison]::OrdinalIgnoreCase)) {
    throw 'W10 subject manifest canonical root mismatch'
}
$cleanSubjectRootBindingSha256 = [string]$cleanSubjectRows[0].subject_root_binding_sha256
$custodySubjectRootBindingSha256 = [string]$custodySubjectRows[0].subject_root_binding_sha256

function Read-VerifiedManifestRows([string]$Path, [string]$ExpectedSha256, [string]$Label) {
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    if ((Get-FileHash -LiteralPath $resolved -Algorithm SHA256).Hash.ToLowerInvariant() -ne $ExpectedSha256) {
        throw "$Label manifest hash mismatch"
    }
    $payload = Get-Content -LiteralPath $resolved -Raw | ConvertFrom-Json
    if ([string]$payload.schema_version -ne 'subject_scoped_residue_manifest_v1') {
        throw "$Label manifest schema mismatch"
    }
    return @($payload.rows)
}

$change2ASelection = @(Read-VerifiedManifestRows -Path $Change2ASelectionManifest `
    -ExpectedSha256 $Change2ASelectionManifestSha256 -Label 'Change 2A selection')
$change2BSelection = @(Read-VerifiedManifestRows -Path $Change2BSelectionManifest `
    -ExpectedSha256 $Change2BSelectionManifestSha256 -Label 'Change 2B selection')
$retainedResidueExceptions = @(Read-VerifiedManifestRows -Path $RetainedResidueExceptionManifest `
    -ExpectedSha256 $RetainedResidueExceptionManifestSha256 -Label 'retained residue exception')

$subjectRoots = @{
    clean_implementation = $cleanSubjectRoot
    local_custody = $custodySubjectRoot
}
$subjectRootBindingDigests = @{
    clean_implementation = $cleanSubjectRootBindingSha256
    local_custody = $custodySubjectRootBindingSha256
}

function ConvertTo-NormalizedSubjectRelativePath([string]$SubjectRoot, [string]$FullName) {
    $root = [IO.Path]::GetFullPath($SubjectRoot).TrimEnd([char[]]@('\', '/'))
    $full = [IO.Path]::GetFullPath($FullName)
    $prefix = $root + [IO.Path]::DirectorySeparatorChar
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "residue path escaped subject root: $FullName"
    }
    $relative = $full.Substring($prefix.Length).Replace([char]'\', [char]'/')
    if ([string]::IsNullOrWhiteSpace($relative) -or [IO.Path]::IsPathRooted($relative) -or
        $relative -eq '..' -or $relative.StartsWith('../', [StringComparison]::Ordinal) -or
        $relative -match '(^|/)\.\.(/|$)') {
        throw "invalid normalized residue path: $relative"
    }
    return $relative
}

function Assert-ManifestRow(
    [object]$Row,
    [hashtable]$SubjectRoots,
    [hashtable]$SubjectRootBindingDigests
) {
    $subjectId = [string]$Row.subject_id
    if (-not $SubjectRoots.ContainsKey($subjectId)) { throw "unknown residue subject: $subjectId" }
    if ([string]$Row.subject_root_binding_sha256 -ne [string]$SubjectRootBindingDigests[$subjectId]) {
        throw "residue subject binding mismatch: $subjectId"
    }
    $path = [string]$Row.normalized_repository_relative_path
    if ([string]::IsNullOrWhiteSpace($path) -or [IO.Path]::IsPathRooted($path) -or $path.Contains('\') -or $path -match '(^|/)\.\.(/|$)') {
        throw "invalid normalized residue path: $path"
    }
    if ([string]$Row.exception_kind -notin @('file_exact', 'directory_exact', 'directory_subtree')) {
        throw "invalid residue exception kind: $($Row.exception_kind)"
    }
}

function Test-ManifestRowMatch(
    [object]$Item,
    [object]$Row,
    [hashtable]$SubjectRoots,
    [hashtable]$SubjectRootBindingDigests
) {
    Assert-ManifestRow -Row $Row -SubjectRoots $SubjectRoots -SubjectRootBindingDigests $SubjectRootBindingDigests
    if ([string]$Item.SubjectId -ne [string]$Row.subject_id) { return $false }
    $actual = [string]$Item.RelativePath
    $expected = ([string]$Row.normalized_repository_relative_path).TrimEnd('/')
    if ([string]$Row.exception_kind -eq 'file_exact') {
        return [string]$Item.EntryKind -eq 'file' -and $actual.Equals($expected, [StringComparison]::OrdinalIgnoreCase)
    }
    if ([string]$Row.exception_kind -eq 'directory_exact') {
        return [string]$Item.EntryKind -eq 'directory' -and $actual.Equals($expected, [StringComparison]::OrdinalIgnoreCase)
    }
    return $actual.Equals($expected, [StringComparison]::OrdinalIgnoreCase) -or
        $actual.StartsWith($expected + '/', [StringComparison]::OrdinalIgnoreCase)
}

function Get-IrisResidue([string]$SubjectId, [string]$SubjectRoot) {
    $irisRoot = Join-Path $SubjectRoot 'Iris'
    try {
        $entries = @(
            Get-ChildItem -LiteralPath $irisRoot -Force -Recurse -ErrorAction Stop |
                Where-Object {
                    ($_.PSIsContainer -and $_.Name -in @('.venv', '__pycache__', '.tmp', '.tmp_tests', '.dvf_tmp', '.pytest_cache', '.ruff_cache', '.mypy_cache', 'uv-cache')) -or
                    (-not $_.PSIsContainer -and $_.Extension -eq '.pyc')
                }
        )
        return @($entries | ForEach-Object {
            [pscustomobject]@{
                SubjectId = $SubjectId
                RelativePath = ConvertTo-NormalizedSubjectRelativePath -SubjectRoot $SubjectRoot -FullName $_.FullName
                EntryKind = if ($_.PSIsContainer) { 'directory' } else { 'file' }
            }
        })
    }
    catch {
        throw "Iris residue enumeration failed for subject $SubjectId :: $($_.Exception.Message)"
    }
}

$allResidue = @(
    Get-IrisResidue -SubjectId 'clean_implementation' -SubjectRoot $cleanSubjectRoot
    Get-IrisResidue -SubjectId 'local_custody' -SubjectRoot $custodySubjectRoot
)
$unexceptedResidue = @($allResidue | Where-Object {
    $item = $_
    -not @($retainedResidueExceptions | Where-Object {
        Test-ManifestRowMatch -Item $item -Row $_ -SubjectRoots $subjectRoots `
            -SubjectRootBindingDigests $subjectRootBindingDigests
    }).Count
})

$contractDerivedRootResidueRows = @(
    [pscustomobject]@{
        subject_id = 'clean_implementation'
        subject_root_binding_sha256 = $cleanSubjectRootBindingSha256
        normalized_repository_relative_path = '.dvf_tmp'
        exception_kind = 'directory_exact'
        decision_row = 'full_repository_gate.execution_workspace.disposable_bootstrap_local_paths'
        reason = 'source checkout must not retain disposable execution-checkout state'
    }
)
$approvedRows = @($change2ASelection) + @($change2BSelection) + $contractDerivedRootResidueRows
$remainingApprovedRows = @($approvedRows | Where-Object {
    Assert-ManifestRow -Row $_ -SubjectRoots $subjectRoots -SubjectRootBindingDigests $subjectRootBindingDigests
    $root = [string]$subjectRoots[[string]$_.subject_id]
    $relative = ([string]$_.normalized_repository_relative_path).Replace([char]'/', [IO.Path]::DirectorySeparatorChar)
    Test-Path -LiteralPath (Join-Path $root $relative)
})
if ($unexceptedResidue.Count -ne 0 -or $remainingApprovedRows.Count -ne 0) {
    throw 'scope-limited terminal residue is not zero'
}
```

### Manual Validation

* supported Project Zomboid + Pulse/Iris 환경에서 boot/save load와 Lua error 부재 확인
* Iris Browser category/search/selection, Detail, Wiki, Alt Tooltip 표시 확인
* Alt Tooltip 최대 4줄, Browser/Wiki와 사실 일치, 추천/효율 판단 부재 확인
* KO/EN 전환과 current Layer 3 body 표시 확인
* classification/context outcome 재생성 후 explicit install이 의도한 current file만 바꾸는지 diff 검토
* external archive locator를 사용한 operator restore 절차가 문서만으로 재현 가능한지 확인

Change 3이 runtime install target, runtime Lua bytes 또는 package runtime projection을 바꾸면 위 supported PZ boot/UI/manual checks는 `complete`의 필수 조건이다. bytes와 package manifest가 predecessor current와 완전히 동일하고 install route가 production data를 바꾸지 않은 경우라도 manual validation을 생략하면 runtime preservation은 `unvalidated_but_in_scope`로 남기고 전체 closeout은 최대 `implemented_only`다.

### Validation Limits

* 모든 외부 모드 조합, 특히 기존 CheatMenuRebirth 관측 문제의 재검증은 수행하지 않는다.
* 장시간 multiplayer, 성능/FPS/heap/IO benchmark는 수행하지 않는다.
* Git history 크기와 clone-time 개선은 측정하지 않는다.
* RTC, Publish, release, Workshop upload와 deployment validation은 수행하지 않는다.
* 삭제하지 않은 다른 branch/worktree의 current/historical closure는 검증하지 않는다.
* 실제 GPT/Codex tokenizer, cache hit, prompt selection과 token telemetry를 측정하지 않는다.

---

## 8. Risk Surface Touch

### Authority Surface

영향 있음. current evidence location, current authority/build manifests, G4/G5/full gate binding, old tooling disposition, generated/runtime ownership과 Layer 3 predecessor hold를 변경한다. Change 1B의 deterministic adoption record와 실제 binding을 바꾸는 wave의 same-commit update가 필요하다.

### Runtime Behavior Surface

public runtime behavior 변경은 목표가 아니다. 다만 classification/context outcome install 경로와 stale `IrisData.lua` overwrite route를 변경하므로 generated/runtime transition은 runtime-affecting surface로 취급한다. Runtime Lua content parity 또는 manual validation 없이 behavior preservation을 주장하지 않는다.

### Compatibility Surface

영향 제한. supported `IrisData` thin adapter, Browser/Wiki/Tooltip facade, Layer 3 stable pointer/facade와 package format은 보존한다. old internal tooling path와 historical reproduction command는 public compatibility surface가 아니지만 current test/automation consumer는 successor로 이관한다.

### Sealed Artifact Surface

영향 큼. sealed/historical evidence를 repository 밖으로 이동하고 archive locator/hash/inventory/restore evidence로 바꾼다. content/history rewrite는 하지 않으며 archive 검증·restore·ancestry 없이 physical deletion을 허용하지 않는다.

### Public-Facing Output Surface

직접 변경 목표 없음. Iris가 표시하는 사실/문구/추천 금지 원칙과 Tooltip 최대 4줄은 유지한다. build/generated placement 변경이 public output bytes를 바꾸면 별도 scope expansion과 validation이 필요하다.

---

## 9. Risk Analysis

### Architecture Risk

* full gate direct binding만 current closure 전체로 오인해 broader manifest/dynamic consumer를 누락할 위험
* `Iris/_docs`의 broad Markdown/JSON/JSONL/other-type authority rule을 좁히면서 실제 current domain contract를 historical로 오분류할 위험
* current capsule이 source/data를 복제해 새로운 이중 authority가 될 위험
* external archive locator가 current route dependency로 다시 유입될 위험
* existing DECISIONS의 physical hold를 successor adoption 없이 위반할 위험
* clean Git worktree와 local custody checkout을 혼동해 ignored/untracked payload를 archive하지 않았는데 제거됐다고 오판할 위험
* 18개 staging path를 모두 raw-copy해 17.96 MiB capsule을 새 영구 historical payload로 만들 위험
* content-addressed archive object와 logical path manifest가 어긋나 restore tree가 원래 경로를 재현하지 못할 위험
* tracked Git blob identity와 `core.autocrlf`가 materialize한 worktree bytes를 섞어 false conflict/parity를 만들 위험
* direct 18 rows만 이관하고 broader staging operational closure의 다른 current row를 historical tree에 남길 위험
* W0 read-only packet과 deterministic adoption record 사이 row/digest 불일치가 생길 위험
* baseline gate failure를 이 lightweighting Change에 몰래 섞어 progression deadlock 또는 authority-scope 확대를 만드는 위험
* 삭제 전 일회성 검증을 canonical launcher/comparator/Python/schema의 새 정규 mode로 편입해 temporary validator가 validation authority로 영구화될 위험
* gate-pinned frozen fixture를 이름만 보고 historical archive/delete 대상으로 오분류하는 위험

### Runtime Risk

* old `main.py`가 stale full-table `IrisData.lua`로 thin adapter를 덮어쓰는 위험
* broken `main.py`를 이름이 유사한 `iris_tooling classification`으로 잘못 대체해 output contract를 잃는 위험
* ignored-only `phase4_tests`를 missing 또는 다른 module name으로 오분류해 B branch 복구 범위와 blocker를 잘못 정하는 위험
* current Layer 3 generation 대신 inactive predecessor를 제거/유지 대상으로 혼동하는 위험
* generated classification/context output의 explicit install 분리 과정에서 runtime target 또는 require shape가 바뀌는 위험
* package에는 current generation만 남지만 source lookup/index가 fixed predecessor를 여전히 참조하는 위험

### Compatibility Risk

* internal old CLI를 사용하는 repository automation을 consumer census에서 누락할 위험
* supported `IrisData` global/table identity를 stale output과 함께 제거할 위험
* external historical reproduction 사용자가 old logical path를 기대하지만 restore command가 동일 path tree를 재구성하지 못할 위험
* PowerShell 5.1/7 ZIP 또는 ordering 차이로 archive/package identity가 달라질 위험

### Regression Risk

* G4/G5 rebind 전에 old staging을 삭제해 full gate가 깨지는 위험
* CAS references를 남긴 채 objects만 제거해 dangling reference가 생기는 위험
* tracked archive evidence가 physical deletion commit의 ancestor가 아니어서 rollback/restore provenance가 끊기는 위험
* `.gitignore` 단순화로 current file이 숨거나 generated/cache가 다시 tracked되는 위험
* root `.tmp` 또는 ignored predecessor를 local disposable로 오인해 Git에 없는 유일 reproduction source를 잃는 위험
* package/lock wave와 locator update를 한 commit에 섞어 environment receipt의 implementation identity를 순환 참조하게 만들 위험
* tracked `.tmp`를 custody checkout에서 삭제하거나 non-Git row를 clean implementation commit 대상으로 넣는 위험
* sparse/local deletion을 exact candidate Git-object absence로 오인하는 위험
* digest attestation을 predecessor raw-evidence availability와 같은 failure parity로 과장하는 위험
* repository-wide residue scan이 out-of-scope worktree/module cache 때문에 closeout을 구조적으로 막는 위험
* subject-relative retained exception을 absolute path 또는 다른 subject의 same-relative path와 비교해 정상 closeout이 항상 실패하거나 과도하게 예외 처리되는 위험

---

## 10. Rollback Plan

* 각 Change는 독립 commit으로 수행한다. 실패 시 해당 wave의 source/config change를 normal Git revert로 되돌린다. unrelated user changes에 `reset --hard` 또는 blanket checkout을 사용하지 않는다.
* Change 0E 실패 시 authority-only Commit 0E를 normal revert하고 이전 locator를 복원한다. 이전 external root가 현재 부재하므로 그 상태에서 W0 baseline PASS를 주장하지 않으며 `blocked(environment_authority_unavailable)`로 돌아간다. 새 external environment/allocator roots는 receipt와 lifecycle disposition에 따라 별도 정리하고 repository rollback과 혼합하지 않는다.
* Change 1B deterministic adoption record가 W0 packet과 불일치하면 Commit 1B만 revert하며 external W0 packet은 immutable evidence로 보존한다. W0 read-only subject에 write를 역적용하지 않는다.
* Change 2A는 Git revert로 tracked exact rows를 복원한다. Change 2B는 local-cache row는 재생성 가능성을 사용하고, 잘못 분류된 unique non-Git row는 삭제 전 mandatory archive/backup이 없었다면 복구 가능하다고 주장하지 않는다.
* Change 5 capsule rebinding 실패 시 Commit 5A의 gate/manifest/digest rows/raw capsule 추가를 함께 revert한다. old staging은 이 시점까지 남아 있으므로 broken intermediate 없이 predecessor binding으로 돌아갈 수 있다.
* Change 7A archive implementation 실패 시 normal revert하고 payload는 건드리지 않는다. Change 7B evidence가 없거나 검증되지 않으면 Change 8 delete gate가 열리지 않는다.
* Change 8 physical deletion rollback은 verified mandatory external archive의 explicit restore command로 exact logical paths를 create-new external recovery root에 복구하고 hash를 확인한 뒤, tracked subset은 새 Git-authored commit으로, ignored/untracked/filesystem-only subset은 recorded custody root containment 검사를 거쳐 명시적 operator action으로 복원한다.
* pre-delete synthetic candidate commit/tree는 evidence-only disposable subject이며 rollback/merge 대상이 아니다. 실제 tracked removal rollback은 Commit 8A revert로만 수행한다.
* Layer 3 predecessor는 Change 7 mandatory archive 또는 recorded predecessor Git commit/tree의 이중 증거에서 복원한다. current pointer를 inactive generation으로 자동 되돌리지 않는다.
* generated output은 deterministic producer로 external root에 재생성한다. repository-local duplicate를 계속 보존하는 방식을 rollback으로 사용하지 않는다.
* `.gitignore` rollback은 physical payload를 자동 복원하지 않는다. current tracked set과 ignore policy를 별도 commit으로 되돌린다.
* external archive가 손상·분실되었거나 locator를 해석할 수 없으면 historical deletion wave는 실행하지 않으며 closeout은 `blocked` 또는 `partial`이다.

---

## 11. Governance Constraints

* `docs/Philosophy.md`의 Iris 경계, 근거 원칙, 중립성, 읽기 전용 동작, 100% Lua runtime과 Pulse 외 spoke 의존 금지를 보존한다.
* authority hierarchy는 `Philosophy -> DECISIONS -> ARCHITECTURE -> ROADMAP -> module authority -> approved plan` 순서를 따른다.
* existing sealed decision/receipt를 rewrite하지 않고 successor record를 append한다.
* current evidence location 변경, gate binding 변경과 successor bytes 추가는 같은 execution unit에서 수행한다.
* successor binding 유효화 전 predecessor path를 삭제하지 않는다.
* current authority/current-required evidence를 historical archive selection에 포함하지 않는다.
* current route는 historical external archive를 암묵적으로 restore하지 않는다.
* Recipe와 Right-click은 독립되고 동등한 사실 surface로 유지한다.
* supported runtime facade, `IrisData` thin adapter, current Layer 3 pointer/facade/lookup, `Layer3English`와 current generation을 보존한다.
* source/data/runtime 의미 변경이 발견되면 physical cleanup에 숨기지 않고 별도 scope expansion과 validation을 요구한다.
* clean checkout에 없는 ignored dependency를 current로 유지하지 않는다.
* destructive selection은 exact manifest/hash/consumer proof를 사용하고 filename glob 또는 크기만으로 판정하지 않는다.
* Change 1A W0 packet과 Change 1B deterministic adoption record가 exact row/digest로 결속되기 전에는 destructive/local cleanup을 실행하지 않는다. W0가 이 plan의 pre-adopted 범위를 벗어나는 genuine scope expansion을 발견한 경우에만 별도 plan revision/review를 요구한다.
* post-hardening S0의 terminal-v15 committed locator/root/receipt를 먼저 검증한다. 유효하면 Change 0E는 `not_required`; 부재·불일치이면 conditional Change 0E와 그 post-commit Checkpoint A PASS 전에는 Change 1A progression을 열지 않는다. Change 1A 자체는 environment/authority를 쓰지 않는다.
* canonical baseline full gate가 FAIL이면 Change 2 이후를 열지 않는다. remediation은 이 plan의 implementation Change로 우회하지 않고 별도 owner-approved plan과 독립 검토로만 수행한다.
* inactive Layer 3 source는 mandatory archive evidence/restore/ancestry가 먼저 성립해야 하며 Git history-only 보존으로 삭제를 승인하지 않는다.
* clean implementation subject와 local custody subject의 root identity 및 census를 섞지 않는다.
* archive는 unique object body와 logical path inventory를 모두 보존하고 restore path parity를 검증한다.
* tracked evidence/source identity는 Git blob bytes를, custody-only identity는 filesystem bytes를 authority로 사용하며 `.gitattributes`/Git config state를 subject manifest에 결속한다.
* predecessor raw-evidence claim과 successor capsule-attestation claim을 같은 parity로 표현하지 않고 versioned authority supersession으로 기록한다.
* synthetic candidate result는 external pre-delete evidence일 뿐 canonical implementation PASS로 승격하지 않는다. 이를 위한 새 repository-regular execution mode/schema/validator를 만들지 않는다.
* `.git` history와 unrelated worktree/user changes를 수정하지 않는다.
* validation ceiling과 non-claims 없이 `complete`, behavior-preserving, release-ready 또는 deployed를 선언하지 않는다.

---

## 12. Expected Closeout State

Expected closeout target: public-text hardening을 포함한 exact S0에서 terminal-v15 environment authority를 재사용하고, 그것이 유효하지 않을 때만 Change 0E로 복구한다. Checkpoint A와 W0 progression 조건을 통과하면 사전 확정된 disposition을 Change 1B에 deterministic하게 봉인하고, genuine blocker 없이 Changes 2–10을 연속 수행하여 `complete`로 닫는다.

`complete`는 다음 조건이 모두 충족될 때만 사용한다.

1. current source/data/tooling/contracts/evidence closure의 missing, ambiguous, unclassified와 ignored dependency가 0이다.
2. `main.py=C`가 broken legacy entrypoint retirement로 고정되고 missing phase module 복원이나 새 대체 CLI 도입이 없으며, 다른 branch가 current authority에 남지 않는다.
3. direct-bound 18 rows를 포함한 broader staging operational closure 전체가 `move_to_current_owner`, `raw_capsule`, `digest_capsule`, `historical_archive`, approved `retained_exception`으로 닫히고 `unresolved_blocker`가 0이다.
4. predecessor raw-evidence availability와 successor capsule-attestation/archive-raw claim이 versioned matrix/transition receipt로 분리되고, adopted capsule budget/exception을 충족한다.
5. current full gate는 external archive 없이 canonical clean checkout의 Checkpoints A/B/D에서 Run A/Run B/comparator를 통과하고, Checkpoint C synthetic candidate는 새 정규 mode 없이 동일 ordinary canonical gate를 통과한다.
6. historical staging/CAS/selected `_docs`/output, old tooling unique predecessor와 inactive Layer 3 deterministic ZIP archive의 logical/unique-object/hash/restore 검증이 성립한다.
7. archive evidence가 physical deletion보다 선행하고 deletion 후 dangling current reference가 0이다.
8. old `tools/` 전체의 current operational consumer가 0이고 retained exception이 있다면 exact list와 이유가 남는다.
9. current Layer 3 generation 하나, stable facade/pointer/lookup와 `Layer3English`가 유지되고 inactive generation/fixed chunks가 mandatory archive 후 제거된다.
10. stale output `IrisData.lua`가 thin adapter를 덮어쓰는 경로가 0이다.
11. generated output/current runtime authority와 external work/result/package/environment/cache root가 명확히 분리된다.
12. `.gitignore`/`.rgignore`/`.gitattributes` 정리 후 current tracked surface와 byte-normalization contract가 clean checkout에서 보이고 obsolete `_archive`/deleted-path rule이 0이다.
13. Lua syntax, installed tooling, package, terminal exact full gate와 Change 3에 필요한 manual runtime validation이 stated ceiling 안에서 완료된다.
14. W0/W10 clean implementation subject 및 동일 local custody subject의 census와 non-overlapping delta가 기록된다.
15. repository-external `subject_scoped_residue_manifest_v1` one-off format의 subject binding 및 file/directory-subtree semantics로 plan-owned `Iris/`와 Change 2A/2B approved root exact rows의 terminal residue가 0이며 out-of-scope cache는 exception inventory로 분리된다. 이 format/validator가 repository-regular authority로 등록된 사례는 0이다.
16. gate-pinned frozen fixture는 protected exact digest로 남고, W0의 `owner_inputs/`/`reviewer_inputs/` row는 archive 또는 retained exception 중 정확히 하나로 닫히며, `build/tests/`/`description/v2/data/` current closure가 보존된다.
17. Checkpoint C의 external synthetic receipt와 ordinary canonical Run A/B/comparator 결과가 exact candidate/base/delete identity에 결속되고, probe-only implementation/schema가 regular authority에 추가되거나 결과가 canonical implementation PASS로 승격된 사례가 0이다.
18. Change 2 진입 전에 terminal-v15 environment admission 또는 conditional Change 0E, Checkpoint A PASS, W0 progression 조건과 exact W0-to-Change-1B row/digest binding이 모두 존재한다.
19. current capsule은 2,359,296 bytes 이하이고 repository-local successor overhead는 `max(2 MiB, tracked physical-removal source bytes의 0.5%)` 이하이다.
20. terminal disposition에서 `unsupported_keep=0`, `remaining_eligible_removal=0`, `unimplemented_removal=0`이다.

다음 중 하나라도 남으면 expected closeout을 낮춘다.

* W0가 pre-adopted scope 밖의 genuine expansion을 발견: `blocked(reason=W0_scope_expansion_requires_plan_revision)`
* committed locator/receipt/environment root가 유효하지 않고 conditional Change 0E도 미완료: `blocked(reason=environment_authority_unavailable)`
* current binding 미해결, capsule/overhead ceiling 초과, archive store/restore 불가 또는 eligible removal 잔존: `blocked`와 exact reason
* 구현 일부와 검증 일부만 완료: `partial`
* 구현은 끝났으나 required terminal/restore/manual validation 미실시: `implemented_only`

최종 closeout은 Git history lightweighting, universal external-mod compatibility, release/RTC/Publish/Workshop/deployment readiness, runtime performance 향상 또는 실제 token 절감률을 선언하지 않는다.
