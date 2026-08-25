# Iris 책임 경계·빌드·런타임 구조 리팩터링 Plan Review (4차 / scope-reduced R1)

검토 대상: `docs/iris_responsibility_repository_build_validation_refactoring_plan.md` (1,001줄, 상태 `scope_reduced_pending_re_review`)
검토 기준일: 2026-08-25
기준 리비전: `main` / `d234723ae92ce83313da0ce83442389e6c4afac8`
검토 근거: `docs/Philosophy.md`, `docs/EXECUTION_CONTRACT.md` (v1.3), `docs/DECISIONS.md`, `Iris/validation/clean_checkout/contracts/full_repository_gate.json` (v8), `Iris/_docs/refactor/core_refactor/phase0_supported_api_manifest.json`, 검증 launcher/runner 실측

---

## 1. Verdict

**PASS**

---

## 2. Executive Summary

**현재 실행 준비 상태:** 실행 가능하다. 이번 개정은 3차 검토의 minor revision 4건을 모두 반영하면서 계획 범위를 R1으로 축소했다. 남은 지적은 2건이며 둘 다 편집 수준이다.

**축소의 성격.** 13개 Change가 10개로 줄었고, 제거된 것은 저장소 경량화(staging/evidence 외부화, CAS/cold archive, disposition enum, `SEALED_TRACKED_TRACE`, 500 MiB), IAR/vNext·predecessor의 물리 삭제, `output`/`media` 중복 제거, 범용 `PhaseRunner`/typed result/구조화 logging, validation runner·result plugin 통합, AI readpoint 최적화, Wiki layout/scroll 개선이다. 남은 것은 전역 패치 삭제, Python 패키지화, current 대형 모듈 분해, right-click v2.4 축소, Layer 3 package projection, Browser/Detail 책임 분리, supported compatibility 격리, closeout이다.

이 축소는 위험을 줄이는 방향이다. 이전 세 차례 검토에서 blocking을 만들었던 요인이 대부분 "**대량 물리 이동·삭제와 그에 따른 계약 재바인딩**"이었는데, 그 축이 통째로 빠졌다. §11은 이제 "historical, staging, evidence, frozen predecessor와 sealed artifact는 current gate 사용 여부와 무관하게 이 계획에서 이동·수정·삭제하지 않는다"는 단일 규칙으로 닫히고, §8 Sealed Artifact Surface는 **없음**이 됐다. 3차에서 지적한 `SEALED_TRACKED_TRACE` census 시드 문제(M-3)와 secondary archive 내구성(M-4)은 해당 작업 자체가 사라져 자연 소멸했다.

**정합성 실측.** 제거된 작업의 잔재 참조를 전수 스캔했고 결과는 깨끗하다.

| 검색어 | 잔존 |
| --- | ---: |
| `SEALED_TRACKED_TRACE`, `UNCLASSIFIED_BLOCKED`, `REPRODUCTION_REQUIRED`, `REGENERABLE`, `NO_OBLIGATION` | 0 |
| `CAS`, `cold-archive`, `migrate_repository_evidence`, `archive_locator`, `IrisArchives` | 0 |
| `500 MiB`, `구조화 로깅`, `typed payload` | 0 |
| `pytest_result_plugin`, `validation/common`, `Iris.validation.common` | 0 |
| `PhaseRunner`, `duplicate helper` | Out of Scope 항목에서만 1회씩 |
| `CURRENT_ROLLBACK_TARGET` | Layer 3 predecessor의 서술 라벨로 1회 |

Change 번호 재부여도 문서 전체에 반영됐다 — §7.4의 full-gate 지점이 "Change 3, 5, 6, 10"(이전 "4, 8, 9, 13"), §7.6이 "Change 10 terminal commit", §10 wave 표가 W0–W10으로 일관된다. Wiki layout/scroll은 §2 Out of Scope, §3 Non-Goals, Change 9 Validation, Manual Validation, §8, §12에서 모두 "기준선에서 변경되지 않음"으로 통일됐다.

**3차 minor revision 처리**

* **M-1(W8~W12 environment)** — §7.3에 wave→environment authority 표가 신설됐다. W0–W2는 predecessor `env-v1`, W3–W5는 package source/lock을 바꾼 wave마다 새 wheel/environment/record/locator, W6–W9는 blob이 동일할 때만 재사용하되 `record implementation commit이 wave subject의 조상 + src/iris_tooling tree·project/lock blob·installed manifest 일치`를 validator가 확인하고 불일치 시 stale reuse 금지, W10은 terminal 전용. 요청한 것보다 강하다.
* **M-2(§12 record binding 모호성)** — §7.6과 §12 양쪽에 "record의 implementation commit/tree는 authority-only subcommit의 부모 구현 subject이며 terminal subject의 조상이어야 하지 **terminal subject와 같을 필요는 없다**"가 명시됐다. blob binding과 commit ancestry가 분리 표기됐다.
* **M-3, M-4** — 해당 작업이 범위에서 제거되어 소멸.

**요청하지 않은 개선.** S0 baseline delta 처리가 `s0_baseline_adoption.json` canonical record로 형식화됐고(merge-base, changed-path inventory digest, owner adoption 전 implementation BLOCKED), terminal CLI probe가 argv/cwd/interpreter/stdout·stderr hash/exit code를 receipt로 남기도록 바뀌었다.

**주요 위험.** 없다. 남은 2건은 미수정 시 ⓐ 무의미하게 통과하는 검사 1줄(N-11)과 ⓑ §7.3 개발 확인 명령이 대상 디렉터리 부재로 실패하는 것(N-12)이며, 잘못된 삭제나 증거 없는 PASS 선언으로 이어지는 경로는 없다.

**실행 진행 여부:** 진행해도 된다. 두 항목은 W3 착수 전 한 줄씩 고치면 된다.

---

## 3. Critical Issues

없음.

---

## 4. Non-Critical Issues

**N-11 — 존재하지 않는 `core` 계층에 대한 검사가 Change 3 Validation에 남아 있음**

Change 3은 core 계층을 만들지 않기로 명시한다.

> Implementation Notes: 다음 의존 방향을 강제한다: `cli -> domain orchestration -> domain services`. **범용 core mechanics 계층은 이 계획에서 새로 만들지 않는다.**

Files 목록에도 `iris_tooling/core/`가 없다(`build/`, `domains/*`, `cli/`만 존재). 그런데 같은 Change의 Validation에는 이전 범위의 문장이 남아 있다.

> import graph 검사에서 **core**의 domain 역의존과 domain 간 내부 import가 0이다.

존재하지 않는 계층에 대한 검사이므로 공허하게 참이다. 위험하지는 않지만, 실행자에게는 "core를 만들어야 하나"라는 혼선을 준다. 더 아까운 점은 이 자리에 **실제로 유용한 검사**를 넣을 수 있다는 것이다.

권고: "import graph 검사에서 domain 간 내부 import가 0이고, `iris_tooling` 아래 새 범용 core 계층이 생성되지 않았다"로 바꾼다. 그러면 Implementation Notes의 규칙이 검증으로 결속된다.

참고로 Change 4의 "분해 후 생긴 공통 함수가 domain policy를 내포하면 `core`로 올리지 않고 해당 domain에 둔다"는 금지 문장이므로 그대로 두어도 모순이 아니다.

**N-12 — `Iris/tooling/tests/`를 어느 wave도 소유하지 않음**

`Iris/tooling/tests/`는 §5 Repository Areas Affected의 Code 목록에 있지만 **어떤 Change의 Files 목록에도 없다**. Change 3 Files는 `pyproject.toml`, `uv.lock`, `src/iris_tooling/*`, `cli/`, 검증 launcher/runner/test와 계약 파일만 나열한다.

그런데 §7.3의 개발 확인 명령은 그 디렉터리를 실행한다.

```powershell
uv run --project .\Iris\tooling --locked --no-editable python -B -m pytest .\Iris\tooling\tests
```

생성 주체가 지정되지 않으면 이 명령은 W3에서 대상 부재로 실패한다.

부수 효과가 하나 더 있다. `full_repository_gate.json`의 `source_disposition_policy`는 `unclassified_source_policy: fail`이므로, `Iris/tooling/tests/` 아래 새 test source가 gate selection 범위에 들어오는 순간 disposition 분류가 필요하다. Change 3은 "이동되는 source/test를 참조하는 `full_repository_gate.json`, taxonomy, required manifest, `pytest.ini`"를 Files에 포함하고 rebinding 규칙도 두었으므로 원칙은 이미 있다. 다만 **새로 생기는** test tree의 소유 wave와 disposition 분류를 명시해야 그 규칙이 적용된다.

권고: `Iris/tooling/tests/`를 Change 3 Files에 추가하고, Implementation Notes에 "새 package test source는 생성과 동시에 gate의 source disposition에 분류한다(current required / hermetic fixture / historical optional 중 택일)"를 한 줄 넣는다.

---

## 5. Scope Review

### Scope Drift

없음. 이번 개정은 순수 축소다. §2 Scope의 11개 항목, §2 Explicitly Out Of Scope에 신설된 7개 제외 항목, §12 ceiling의 `out_of_scope` 행, §12 말미의 "미실행이 closeout을 막지 않는다" 목록이 서로 정확히 대응한다. 제거된 작업이 "암묵적 후속"으로 흘러가지 않고 명시적으로 후속 경량화 범위로 지정됐다.

§1 Objective의 6개 결과 항목도 축소에 맞춰 재작성됐다 — 2번이 "historical payload의 물리적 이동·외부화·삭제는 수행하지 않는다", 4번이 "source predecessor는 이 계획에서 이동·수정·삭제하지 않는다", 6번이 "기존 테스트 family 병합이나 runner 공통화는 수행하지 않는다"로 바뀌었다.

### Missing Scope

task-specific 누락은 없다. N-12(`Iris/tooling/tests/` 소유 wave)는 기존 항목의 Files 등재 누락이지 새 scope가 아니다.

축소로 인해 의존이 끊긴 곳도 없다. 확인한 연결점은 다음과 같다.

* 이전 Change 9(validation runner 통합)가 소유하던 `pytest_result_plugin` 이동이 사라지면서 §12의 `Iris.validation.common.pytest_result_plugin` 요구도 함께 제거됐다. `result_plugin`은 §4.3에서 gate 계약의 필드로만 서술된다.
* `write_environment_receipt.py`가 `Iris/validation/common/`에서 `Iris/validation/clean_checkout/`로 옮겨졌고, "current environment authority resolution, schema/hash 검증, 결속과 stale-record rejection의 기존 owner는 `iris_clean_checkout_validation_common.py`에 유지한다. 다른 runner의 공통 인프라로 승격하지 않는다"가 덧붙었다. 공통화 제거와 일관된다.
* 이전 Change 3이 담당하던 staging fixture 이관이 사라졌지만, 애초에 이동하지 않으므로 rebinding 자체가 불필요하다. §7.4의 G4/G5 검사는 "historical/staging payload의 path와 raw bytes/hash가 기준선에서 변경되지 않았는지"로 전환됐다.

### Explicitly Out Of Scope Consistency

일관하다. `unvalidated_but_in_scope`는 여전히 한 줄(제3자 모드 조합에서의 patch 삭제 결과)이며 Out of Scope의 "모든 외부 모드와의 호환성 전수 조사"와 겹치지 않는다. 새로 제외된 7개 항목은 §12 ceiling의 `out_of_scope` 행에 그대로 반영됐다.

---

## 6. Validation Review

### Missing Validation

* 새 package test tree의 gate source disposition 분류 (N-12)

그 외 current claim/gate를 뒷받침하는 task-specific validation의 부재는 발견되지 않았다.

### Weak Validation

없음.

축소 후에도 핵심 검증은 유지되거나 강화됐다.

* Change 2의 non-interference probe(`tickTexture = nil`/invalid fixture)와 "이를 외부 compatibility 보존 증거로 해석하지 않는다"는 제한이 그대로다.
* Change 4·6이 "IAR/vNext와 frozen predecessor 파일의 tracked path, Git blob과 SHA-256이 기준선과 동일하다"를 Validation 항목으로 명시한다 — 삭제하지 않는다는 선언을 검사로 결속했다.
* §7.3의 wave environment 재사용에 negative fixture("package source 변경 후 stale wave authority를 current로 사용하는 negative fixture는 실패한다")가 붙었다.
* §7.6 terminal에 arbitrary-cwd installed CLI probe가 추가되고 stdout/stderr hash까지 receipt로 남는다.

### Validation Ceiling Risk

없음. §12의 3분류 표가 유지되고 `validated` 행이 축소 범위에 맞춰 재작성됐다("preserved historical/staging/frozen hashes"가 추가되고 archive 관련 항목이 제거됨). `release-ready`, `deployed`, multiplayer/dedicated-server, 전체 외부 모드 compatibility, PZ 기본 동작 equivalence를 명시적으로 비주장한다.

§12 말미의 "반대로 historical/predecessor 물리 삭제, archive, output/media 중복 제거, runner/helper/AI readpoint 최적화와 Wiki layout/scroll 개선의 미실행은 이 계획의 closeout을 막지 않는다"는 축소된 범위에서 `complete`가 무엇을 뜻하는지 정확히 한정한다.

### Validation Practicality

실행 가능하고 위험 표면에 비례한다. §7의 exact 명령은 3차 검토에서 스크립트 시그니처와 전수 대조했고, 이번 개정에서 바뀐 부분(§7.2 S0 adoption record, §7.3 wave 표, §7.6 CLI probe)은 기존 launcher 인자를 그대로 사용한다.

ceremony는 오히려 줄었다. archive verify/restore 블록 전체와 disposition 8~9등급 분류가 사라져 W3의 실행 부담이 크게 낮아졌다. 3차에서 언급했던 "전체 `REGENERABLE` 재생성 규모가 사전에 확정되지 않는다"는 실무 부담도 함께 소멸했다.

남은 실행 부담은 W3의 environment authority 절차(implementation subcommit → wheel build → create-new environment → immutable record → authority-only subcommit)가 W3–W5에서 최대 3회 반복될 수 있다는 점이다. 다만 W6–W9 재사용 규칙이 있어 총 횟수는 제한된다.

---

## 7. Governance Review

### Philosophy.md Compliance

충돌 없음. Change 2가 Philosophy `[4]`와 Iris 절의 충돌을 §4.5에서 successor decision 선행 채택으로 처리하는 구조가 유지된다. 무추론/침묵, Alt Tooltip 4줄, Recipe·Right-click 동등·독립, 100% Lua 런타임, Pulse 단일 의존이 §11에 유지된다.

축소로 §4.1에 한 줄이 추가됐다 — "두 경로의 기계적 인프라 공통화도 이 계획에서는 수행하지 않는다". Recipe/Right-click 독립성을 더 보수적으로 지키는 방향이다.

### Architecture Boundary

승인되지 않은 확장 없음. 오히려 좁아졌다 — 범용 core 계층을 만들지 않고 의존 방향을 `cli -> domain orchestration -> domain services` 3단으로 한정한다. N-11은 이 결정과 검사 문장 사이의 불일치다.

### Runtime / Build-Time Separation

부적절한 혼합 없음. Python은 배포 package에서 배제되고, Change 6이 package projection만 제한하며 source predecessor는 건드리지 않는다. `package_runtime_mirror` 재바인딩은 같은 commit에서 수행하고 "source file 삭제와 contract rebinding을 혼동하지 않는다"를 명시한다.

### FAIL-LOUD Preservation

silent fallback 도입 없음. required tool 부재 시 BLOCKED, nested result 재사용 6항목 일치, stale environment receipt 사용 BLOCKED, package extra generation 자동 무시 금지, right-click 구버전 옵션의 묵시적 fallback 금지, S0 adoption record 미채택 시 implementation wave BLOCKED가 모두 유지된다.

### Authority Ownership

ownership 우회·약화·모호화 없음. §11이 "current authority는 정확히 하나의 producer/entrypoint/owner를 가져야 한다. physical duplicate 제거는 후속 경량화 범위이며 이 계획은 current owner binding만 단일화한다"로 정확히 분리됐다 — 물리 중복을 남기면서도 authority 단일성은 확보한다는 뜻이 명시적이다.

3차에서 확인한 `phase0_ratification_attempt_0002.json` 9개 지점 census는 Change 3에 그대로 유지되고(W4 → W3으로 wave만 변경), historical allowlist 규칙도 유지된다.

### Contract Compliance

* §5 disclosure — §8이 surface별로 충족. Sealed Artifact Surface가 "없음"으로 바뀐 근거(이동·수정·삭제 안 함 + 기준선 hash 검사)도 함께 기재됐다.
* §6-1 claim-evidence binding — §7의 exact command와 §12 receipt 1:1 연결로 충족.
* §6-2 / §7-2 ceiling — §12 3분류 표로 충족.
* §7-1 state — 4개 state만 사용, 세부 원인은 blocking reason code. 충족.
* §7-4 taxonomy expansion — 이번 개정에서 disposition enum 자체가 사라져 해당 없음.
* §7-5 historical trace — 물리 상태를 건드리지 않으므로 자동 충족.
* §9-2 module policy 확장 금지 — `getLegacyIrisData`의 listed/unlisted 구분이 유지된다.

module authority 문서, 승인된 제약, sealed decision과의 충돌은 발견되지 않았다. 3차에서 지적한 `DECISIONS.md:2614`(round-scoped evidence tooling 조건부 no-auto-delete)는 이 계획이 evidence tooling을 물리 삭제하지 않으므로 더 이상 접점이 없다.

---

## 8. Risk Surface Review

### Authority Surface

**None** — current entrypoint/manifest/validation binding을 바꾸지만 계약 재바인딩이 같은 execution unit 규칙으로 묶여 있고, environment authority 단일 소유가 census와 wave 표로 확보됐다.

### Runtime Behavior Surface

**None** — Change 2의 삭제 결과가 decision 선행 + bounded probe + `blocked` 경로로 처리되고 §12 ceiling이 주장 범위를 제한한다. Wiki layout/scroll은 불변으로 고정됐다.

### Compatibility Surface

**None** — listed/unlisted 구분으로 supported set이 고정되고, 제거 대상은 비공개 중복 구현과 구버전 mode로 한정된다.

### Sealed Artifact Surface

**None** — historical/staging/evidence/frozen/sealed의 path·bytes를 이동·수정·삭제하지 않으며, terminal 검증이 기준선 hash 불변을 확인한다.

### Public-Facing Output Surface

**None** — 사실 값과 기존 layout/scroll을 유지하고 unit/visibility 정렬과 nil section 의미 오류만 수정한다.

---

## 9. Risk Review

### Regression Risk

* 신규 없음. 대량 물리 이동이 사라지면서 이전 세 차례 검토의 주된 회귀 경로가 함께 제거됐다.

### Compatibility Risk

* 신규 없음.

### Operational Risk

* `Iris/tooling/tests/` 생성 주체가 지정되지 않아 §7.3 개발 확인 명령이 W3에서 실패할 수 있다 (N-12).
* W3–W5에서 environment authority 절차가 최대 3회 반복될 수 있다. 절차 자체는 정당하나 실행 시간이 늘어난다.

### Validation Risk

* 신규 없음. N-11은 공허하게 통과하는 검사이므로 잘못된 PASS를 만들지 않는다.

### Governance Risk

* 신규 없음.

---

## 10. Required Revisions

**PASS 승인 전에 요구되는 revision은 없다.**

아래 2건은 W3 착수 전에 반영할 minor revision이며 PASS를 막지 않는다.

**M-5 — Change 3 Validation (N-11)**
"import graph 검사에서 core의 domain 역의존과 domain 간 내부 import가 0이다"를 "import graph 검사에서 domain 간 내부 import가 0이고 `iris_tooling` 아래 새 범용 core 계층이 생성되지 않았다"로 바꾼다.
*이유:* 현재 문장은 만들지 않기로 한 계층을 검사하므로 공허하게 참이며, 같은 자리에서 Implementation Notes의 실제 규칙을 결속할 수 있다.

**M-6 — Change 3 Files 및 Implementation Notes (N-12)**
`Iris/tooling/tests/`를 Change 3 Files에 추가하고, "새 package test source는 생성과 동시에 gate의 source disposition에 분류한다"를 Implementation Notes에 한 줄 넣는다.
*이유:* 현재 어느 wave도 이 디렉터리를 소유하지 않아 §7.3 명령이 실패하고, `unclassified_source_policy: fail`인 gate에 새 test source가 분류 없이 진입할 수 있다.

---

## 11. Final Recommendation

**PASS with minor revisions.**

계획은 실행 가능한 상태다. 이번 축소는 범위를 줄이면서 정합성을 잃지 않았다 — 제거된 작업의 잔재 참조가 0이고, Change 번호·wave 표·ceiling·Out of Scope·closeout 조건이 모두 새 범위로 일관되게 재작성됐다. 3차의 minor revision 4건 중 2건은 반영, 2건은 범위 축소로 소멸했으며, 요청하지 않은 개선(S0 adoption record, terminal CLI probe receipt)이 추가됐다.

남은 2건은 Change 3 안의 문장 하나와 Files 항목 하나다. 잘못된 삭제나 증거 없는 주장으로 이어지는 경로는 없다.

**Next actions**

1. M-5, M-6을 W3 착수 전에 반영한다. 각각 한 줄이다.
2. W0(§7.2 S0 baseline)부터 실행을 시작한다. S0가 exit `0`이 아니면 §4.4대로 blocker로 기록하고 원인을 별도 수정한 뒤 W1로 진행한다.
3. W0 HEAD가 `d234723a`와 다르면 §7.2 절차대로 `s0_baseline_adoption.json`에 delta를 기록하고 W1 owner adoption을 받은 뒤 implementation wave를 연다.

---

## 12. Reviewer Notes

**검토 방법과 한계**

* 정적 검사만 수행했다. §7의 어떤 명령도 실행하지 않았다 — full gate, standalone 4개, `uv sync`/`uv build`, `package_iris.ps1`, Lua syntax 전부 미실행이다. 이 PASS는 **문서로서의 계획**에 대한 판정이며 baseline이 green인지, S0가 exit `0`인지에 대해서는 아무것도 주장하지 않는다. 실행 결과에 대한 사전 승인이 아니다.
* 이번 회차 실측 대조: 제거된 작업 16개 키워드의 잔재 참조 전수 스캔, Change 번호 재부여의 문서 전역 일관성(§7.4·§7.6·§10), Wiki layout/scroll 관련 6개 지점의 일관성, `Iris/tooling/tests/`의 Files 등재 여부, `core` 참조 5개 지점의 문맥, §5 Code 목록과 각 Change Files의 대응.
* §4.2 baseline 표는 10개 행으로 축소됐다(저장소 byte 관련 5개 행 제거). 남은 행의 수치는 1차에서 전수 재측정해 일치를 확인했고 변경되지 않았다. 이번에 확인한 것은 Layer 3·fixed chunk 행의 의미 서술이 "보존"으로 유지된 점이다.
* §7의 exact command 인자 대조는 3차에서 수행했다(3개 PowerShell launcher의 mandatory 파라미터, standalone 4개 경로, 환경 receipt 실재). 이번 개정에서 해당 블록의 인자는 변경되지 않았고 §7.6의 CLI probe만 추가됐다.
* `docs/DECISIONS.md`는 전문이 아니라 보존/삭제/compatibility 관련 조항만 조회했다. 이 계획이 물리 삭제를 수행하지 않으므로 3차의 census 권고는 더 이상 적용되지 않는다.

**후속 참고**

* 이 계획은 이제 R1이며, 제거된 작업은 후속 라운드의 입력 상태로 남는다. 후속 경량화 라운드를 열 때 1~3차 검토에서 확인된 제약이 다시 적용된다는 점만 기록해 둔다 — `full_repository_gate.json`의 path-bearing 필드(taxonomy/additional source·node/standalone/source disposition/G4·G5/frozen bootstrap/package mirror/result plugin), `frozen_predecessor_inputs/`의 pinned SHA-256, `g4_required_paths` 30개 중 staging 11·`_docs/round3` 3, `DECISIONS.md:2627`의 sealed no-delete 4 family와 `2614`의 조건부 no-auto-delete, 그리고 이를 한정하는 `1875`/`1921.8`. R1이 이 자산들의 물리 상태를 바꾸지 않으므로 이 목록은 후속 라운드 시작 시점에도 그대로 유효하다.
* R1 종료 후 `tools/build`의 기존 physical 파일과 새 `iris_tooling` package가 공존한다. 계획은 이를 명시적으로 선택했고(current import graph는 새 package만 가리킴), 물리 존속 판정을 후속으로 미룬다. 후속 라운드의 첫 입력은 "current manifest가 가리키지 않는 physical file 집합"이 될 것이다.
