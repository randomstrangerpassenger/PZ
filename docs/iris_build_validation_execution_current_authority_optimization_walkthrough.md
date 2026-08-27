# Iris Build/Validation Execution and Current-Authority Optimization Walkthrough

> 작성일: 2026-08-27 KST
> 구현 계획: `docs/iris_build_validation_execution_current_authority_optimization_plan.md`
> Product S0: `e6310737a99873e2c58f3f399de77ef97473f39f`
> Documentation-only plan carrier: `e0d22781e0595abfd07da82150219d39969f6d4a`
> 최종 package-source subject: `c334ee97f0c01fb826309a6fb5388e99bde518d7`
> 최종 machine-validation subject: `7a6e8ef9e9c29d5986872b08bdbeded5f086b536`
> Reviewed closeout carrier: `b3045c82ea1b523fd27ecdf46528aaca61003ca4`
> 상태: implementation and machine validation complete; plan-process closeout complete by owner disposition

## 1. 문서의 역할

이 문서는 현재 세션에서 수행한 Iris build/validation 실행 구조와 current-authority
탐색 최적화를 구현 순서대로 설명하는 narrative walkthrough다. 계획의 요구사항이 실제
코드, authority, terminal subject와 Reviewer correction으로 어떻게 이어졌는지를 한
흐름으로 읽을 수 있게 하는 것이 목적이다.

이 Walkthrough는 다음 역할을 갖지 않는다.

- adopted plan, current authority manifest, G5 successor, environment authority 또는
  terminal receipt를 대체하지 않는다.
- canonical validator, 정규 검사기, 새 validation authority 또는 별도 seal이 아니다.
- 세션 중 사용한 read-only inspection이나 일회성 hash 계산을 정규 검증으로 승격하지
  않는다.
- closeout 상태를 재정의하지 않는다. 최종 결과의 authoritative summary는
  `docs/iris_build_validation_execution_current_authority_optimization_closeout.md`에 있다.
- runtime 성능, FPS, 실제 GPT/Codex token 절감률, release·Workshop·Publish·RTC
  readiness 또는 외부 모드 보편 compatibility를 주장하지 않는다.

## 2. 시작점과 작업 경계

작업은 `docs/Philosophy.md`의 Iris 역할을 유지하는 범위에서 진행했다. Iris는 근거 기반
정보를 읽기 전용으로 보여주는 spoke이며, 추천·우열 판단이나 게임 상태 변경을 소유하지
않는다. PZ에서 실행되는 Iris runtime은 100% Lua라는 경계도 유지했다.

이번 계획의 대상은 product 기능이나 UI가 아니라 다음 네 영역이었다.

1. build/validation 실행 결과와 오류 표현을 공통 typed boundary로 정리한다.
2. 중복 실행 orchestration과 seed producer를 줄인다.
3. package-owned current implementation과 description-tree predecessor copy를 분리한다.
4. 사람이 찾는 command/current readpoint와 machine route index를 한 current owner로
   수렴한다.

작업은 현재 repository와 계획이 명시한 external custody root
`C:/Users/MW/i/iris-build-validation-optimization-e0d22781` 안에서만 수행했다. Owner
approval gate는 세션 시작 프롬프트의 사전 승인으로 통과했지만, 도구·플랫폼의 별도
권한 요구는 우회하지 않았다.

테스트도 계획 경계를 유지했다. Wave별 focused checkpoint와 source/test/contract 변경
후 요구되는 replacement terminal만 실행했고, 추가 confidence만을 위한 full run,
historical replay 또는 full tooling pytest는 만들지 않았다.

## 3. W0에서 채택한 최적화 대상

W0 listing은 Round3 `current` route의 routing membership 103개를 가리켰다. 이는 canonical
full-gate pytest denominator 211개와 다른 분모다. Census와 실제 source/import,
command/document owner를 대조한 뒤 일곱 후보를 다음처럼 disposition했다.

| Candidate | 채택한 처리 | 최종 결과 |
| --- | --- | --- |
| Typed execution/result boundary | `adopt_and_implement` | 공통 phase I/O, canonical semantic result, volatile envelope, issue/artifact와 legacy adapter 도입 |
| 두 StageRunner | `merge_into_current_owner` | package-owned `PhaseRunner`로 수렴 |
| Current-output seed | `adopt_and_implement` | producer invocation `6 → 3` |
| 추가 helper 후보 | `below_materiality_threshold` | threshold 미달 helper authority를 새로 만들지 않음 |
| Same-name predecessor copy 33개 | `retire_predecessor_copy` | external archive 후 tracked predecessor source 물리 제거 |
| Command/readpoint fragmentation | `merge_into_current_owner` | command owner와 current explanation owner 각각 `4 → 1` |
| Historical/reproduction corpus | `retain_protected_reproduction` | current authority와 분리해 보존 |

이 disposition은 구현량을 늘리는 면허가 아니었다. 기존 owner로 합칠 수 없는 helper,
중복 proof artifact, validation-of-validation은 추가하지 않았다.

### 3.1 W0 admission evidence 상태

지정된 external custody root
`C:/Users/MW/i/iris-build-validation-optimization-e0d22781`와 그 `w0/`를 read-only로
조사했다. `w0_census.json`에는 candidate와 custody가 있지만, 구현 전 W0 elapsed,
Wave 1~3 projected time, total ≤120, 명시적 `ADMIT`, plan carrier/exact base binding을
함께 보존한 artifact는 없었다. 후속 timestamp는 bounded outcome을 보여줄 뿐 사전 결정을
재구성하지 않으며, 사후 admission artifact나 exemption을 만들지 않았다.

```text
W0_ADMISSION_EVIDENCE_MISSING

The implementation outcome completed within a bounded observed timeline,
but the plan-required pre-implementation elapsed/projected-time ADMIT
artifact was not preserved.

Observed timestamps are outcome evidence only and do not reconstruct
the missing pre-admission decision.
```

따라서 구현과 machine validation은 완료됐고 terminal 및 Reviewer는 PASS지만,
W0 pre-implementation admission은 unresolved다. Reviewer PASS는 이 누락을 대체하지
않으며 overall plan-process closeout은 complete by owner disposition이다.

## 4. 핵심 구현

주 구현 commit은 `31dc4c949db160bc3794cab38bedbef6af6349c0`이다. 이 commit은
53개 파일에 걸쳐 1,108줄을 추가하고 22,184줄을 제거했다. 큰 삭제량의 대부분은
`Iris/build/description/v2/tools/build`에 남아 있던 package source의 same-name
predecessor copy를 current tree에서 제거한 결과다.

### 4.1 Typed execution/result boundary

`Iris/tooling/src/iris_tooling/execution.py`에 다음 공통 계약을 도입했다.

- `PhaseInput` / `PhaseOutput`
- `CanonicalSemanticResult`
- `ExecutionEnvelope`
- `Issue` / `ArtifactRef`
- `MachineResult`
- `TerminalStatus`와 exit-code projection
- legacy dict/JSON encode/decode adapter

Canonical semantic result에는 stable 의미만 두고, run ID, elapsed time, process와
environment 같은 실행별 값은 envelope로 분리했다. Unknown schema/discriminator와
exception은 조용히 흡수하지 않고 concrete issue와 non-zero exit 의미로 투영한다.

이 core는 domain verdict나 validation membership을 소유하지 않는다. Build와 validation
각 domain이 payload와 판정을 계속 소유하고, execution core는 순서·재사용·오류·artifact
전달만 담당한다.

### 4.2 StageRunner 수렴

서로 따로 존재하던 두 StageRunner는 thin adapter가 공통 `PhaseRunner`를 사용하도록
바뀌었다. `PhaseRunner`는 다음 동작만 제공한다.

- dependency가 PASS한 phase만 실행
- run-local reuse key 처리
- phase elapsed time 기록
- exception을 BLOCKED issue로 변환
- 기존 simple `run(action, failed, abort_message)` 의미 보존

Right-click과 build domain의 실제 I/O, success 판정과 payload는 runner 밖에 남겼다.
따라서 중복 orchestration은 줄였지만 common core가 god object가 되지는 않았다.

### 4.3 Seed producer `6 → 3`

기존 full gate는 두 materialization 경로가 각각 세 producer를 호출해 같은 current-output
seed를 총 여섯 번 만들었다. 이를 다음 순서로 바꿨다.

```text
staging producer 3개
→ completeness/content identity 검사
→ immutable final seed publish
→ pytest/standalone case-local clone
```

Producer invocation은 3개로 줄었고, mutation/tamper case는 공유 final seed를 직접
수정하지 않고 각자 clone을 사용한다. Fresh-process와 A/B independence도 유지했다.

### 4.4 Predecessor copy 33개 retirement

분모는 임의로 31에서 33으로 확장한 것이 아니다.

```text
32 distinct basename intersections
- non-substantive __init__.py 1
= 31 substantive distinct basenames

31 substantive basenames
+ nested D16 one extra concrete predecessor copy for each of 2 basenames
= 33 concrete predecessor files
```

추가 concrete copy가 있는 basename은
`run_dvf_3_3_korean_prose_naturalization.py`와
`validate_dvf_3_3_korean_prose_naturalization.py`다. 이 nested D16 copy는 neutral
protected fixture가 아니다. Package-owned current source와 이름이 같은 33개 concrete
predecessor file을 실제 내용과 import/entrypoint consumer로 다시 판정했다. 5개는 exact
copy, 28개는 diverged copy였지만 모두 current authority를 package owner가 이미 대체하고
있었다. 결과는 substantive distinct basename identity의 live implementation intersection
`31 → 0`, concrete predecessor file `33 → 0`이다.

삭제 전에 external archive
`C:/Users/MW/i/iris-build-validation-optimization-e0d22781/archive/archive_manifest.json`에
33개 entry를 기록했다. 전체 path/size/SHA 검사가 PASS했고, 가장 큰 diverged entry인
`public_text_quality_acceptance.py`의 representative restore도 byte-identical PASS했다.

그 뒤 predecessor source를 tracked tree에서 제거했다. Historical/reproduction fixture와
서로 다른 identity를 가진 tool은 이 same-name denominator에 섞지 않았고, current import와
command authority만 0으로 만들었다.

### 4.5 Command와 current readpoint 수렴

사람이 복사하는 canonical command literal은 `Iris/build/ENTRYPOINTS.md` 한 곳으로
모았다. 다른 current-facing 문서는 command를 다시 설명하지 않고 link projection만
제공한다.

- `docs/IRIS_CURRENT.md`: compact current route와 role link
- `Iris/AGENTS.md`: `Philosophy.md → IRIS_CURRENT.md` bootstrap
- `Iris/_docs/authority/iris_current_route_index.json`: authority, producer, validator,
  artifact와 explicit receipt query route
- `Iris/_docs/authority/iris_current_authority_manifest.json`: current/historical exact
  classification

결과적으로 human command literal owner는 `4 → 1`, current authority explanation owner는
`4 → 1`, authority에서 receipt까지 최대 탐색 hop은 `4 → 1`이 됐다.

## 5. 첫 terminal과 Reviewer correction

초기 implementation 뒤 wheel, fresh external environment, versioned environment authority,
Run A/B와 comparator를 순서대로 결속했다. 이 과정에서 terminal 자체가 드러낸 문제는
해당 subject를 고친 뒤 계획의 rerun rule에 따라 새 exact chain으로 교체했다.

초기 execution correction에는 다음이 포함됐다.

- Windows full path budget을 넘은 work/result root를 짧은 external root로 변경
- working file CRLF와 Git blob LF의 raw identity 차이를 구분
- long result-root를 가정하던 여덟 case와 stale G5 aggregate oracle 교정

첫 Codex Reviewer는 다음 세 finding을 냈다.

1. Composite validation CLI가 predecessor receipt와 qualification identity 입력 네 개를
   launcher로 전달하지 않았다.
2. Authority manifest의 non-recursive glob이 nested D16 predecessor deletion을 덮지
   못했다.
3. Frozen `round3_active_core_closure.json`이 삭제된 predecessor path를 current라고
   주장했다.

`22e53eb2010e6909a49269df589186981585ef78`에서 이를 최소 수정했다.

- `iris-tooling validate`가 composite identity hash/path 네 인자를 조건부 require하고
  launcher로 전달하도록 보완
- standalone context에서는 composite 전용 입력을 reject
- unknown remainder도 fail-loud 처리
- nested D16 exact reproduction glob 추가
- frozen Round3 closure를 historical exact path로 명시

Affected CLI checkpoint는 기존 test family 안에서 4개 case로 PASS했고 새 standalone
validator는 만들지 않았다.

## 6. G5 0016과 0017 번호의 의미

이 세션에서 번호를 다룬 원칙은 append-only였다. 과거 번호를 다시 쓰거나 전체 chain을
재번호링하지 않았다.

### 6.1 왜 0016이 생겼는가

Main implementation에서 `public_text/cli.py` bytes가 execution-envelope adapter 통합으로
실제로 바뀌었다. 계획은 compiler production closure bytes가 바뀔 때만 0016 이상의
successor를 만들도록 요구한다. 따라서 0016은 실수 보정 번호가 아니라 그 시점의
19-path closure를 결속한 successor였다.

### 6.2 왜 0017이 필요했는가

두 번째 Reviewer는 0016 ordered set이 `public_text/cli.py`를 포함하면서도 그 파일이
module-level import하는 `iris_tooling/execution.py`를 포함하지 않는다고 지적했다. 계획
§4.6을 다시 대조하니 identity owner인
`naturalization_compiler_identity.py` 자체도 반드시 포함해야 했다.

따라서 `d103cf7815b98793b718361b65dbdac3e2aadfaa`에서 current ordered set에 두 파일을
추가했다.

```text
0016: 19 paths
0017: 21 paths
added: naturalization_compiler_identity.py, execution.py
removed: none
survivor mapping: old 0–6 → new 0–6, old 7–18 → new 9–20
```

0017은 기존 0013–0016을 수정하지 않고 새 current identity만 append했다. 최종 aggregate는
`61238620a841bc635169d5f254ceab9279f4b71d9231fdc2cd660c7b3afdb6ab`이며 0017 raw
SHA-256은 `8e5261338f7b4518b03b331df8da6ddabce15842b5188be995a39421c8c38e5f`다.

### 6.3 왜 0018은 만들지 않았는가

마지막 Reviewer는 full-gate `current_required_paths`에서 0016을 남기고 0017을 append해야
하는데, 0016 entry가 0017로 교체된 한 줄을 발견했다. `c334ee97f0c01fb826309a6fb5388e99bde518d7`은
0016을 누적 보존 목록에 복구했다.

이 수정은 compiler source, ordered set, constituent hash와 aggregate를 바꾸지 않았다.
따라서 새 compiler identity가 아니며 0018을 만들 이유도 없었다. 최종 목록은
`…0015, 0016, 0017`이고 0013–0017 파일은 append-only history로 유지된다.

## 7. Package와 machine-validation subject

계획은 source/test/contract가 바뀌면 package-source commit부터 새 exact terminal chain을
만들도록 요구했다. 이는 같은 subject를 confidence 확보 목적으로 반복한 것이 아니라,
검증 대상 identity가 달라졌기 때문에 replacement subject를 만든 것이다.

최종 chain은 다음과 같다.

```text
package source c334ee97 / tree d66ac0b0
→ wheel 8063f8a2…
→ fresh environment + receipt b452af78…
→ versioned environment authority + current locator
→ machine subject 7a6e8ef9 / tree 44ac4a75
→ Run A
→ Run B
→ deterministic comparator
→ read-only Codex Reviewer
→ docs-only closeout b3045c82
```

최종 wheel은
`C:/Users/MW/i/iris-build-validation-optimization-e0d22781/terminal/w7/wheel/iris_tooling-0.1.0-py3-none-any.whl`,
SHA-256은 `8063f8a20c1fc13fe5fb47f568ed80b1b086b272aafe38f764ddbe53d2483183`다.

Environment receipt는
`C:/Users/MW/i/iris-build-validation-optimization-e0d22781/terminal/w7/receipt/environment_receipt.json`,
SHA-256은 `b452af787e3afeabde15c689d508d55d9ba18e28cceb8e29428d286f9e442864`다.

Machine subject `7a6e8ef9…`는 package-source `c334ee97…`의 direct child이며, versioned
environment authority record와 current locator 두 파일만 변경한다. Docs-only closeout과
이 Walkthrough는 machine PASS subject를 다시 정의하지 않는다.

## 8. 최종 검증

최종 package/environment subject에서 계획이 요구한 affected G5 case와 terminal bundle을
실행했다.

| Validation | 결과 |
| --- | --- |
| Affected G5 focused case | `1 passed` |
| Round3 current-route routing identity | `103 → 103` |
| Run A | exit `0`, pytest `211`, standalone `4`, total `215` |
| Run B | exit `0`, pytest `211`, standalone `4`, total `215` |
| A/B canonical result | 동일 SHA-256 `ef6072fdcc1e3dcb71b1cdfacae656bf9d9e7dfd0da027114dd4d18e3833a2ac` |
| Deterministic comparator | exit `0`, status `succeeded` |
| Comparator fingerprint | `9e7bd8224a2ffe02ad49bfccd8950ec1e7f7715065b5bd303950127c125e3abc` |
| Tracked/external execution mutation | `0` |
| Run A/B external work root | 둘 다 empty after |

Run A orchestration은 `C:/Users/MW/i/ivo7-ra/orchestration.json`, Run B는
`C:/Users/MW/i/ivo7-rb/orchestration.json`, comparator receipt는
`C:/Users/MW/i/ivo7-cmp/compare_receipt.json`이다.

장기 실행 가능성이 있는 Run A/B는 약 30초 간격으로 process 상태를 확인했다. 각각
약 208초에 정상 종료했으며, 비정상 정체·무한 반복 신호는 없었다.

Canonical full gate의 recurring execution unit은 모든 pytest identity 211개와 required
standalone validation 4개의 합인 `211 + 4 = 215`다. Round3 103은 routing membership이므로
이 산식에 더하지 않는다. Parameterized named case, `subTest` assertion, migration-only
script, external census, Reviewer-only check, unregistered temporary validation도 분모에서
제외한다. Round3 routing identity와 canonical full-gate pytest identity 모두 delta는 0이며,
regular test 108개가 추가된 것이 아니다.

## 9. 최종 Codex Reviewer 결과

Reviewer는 마지막 correction을 읽기 전용으로 재검토했다. 테스트, build, formatter,
package manager, repository Python/PowerShell script와 file write는 허용하지 않았다.

최종 결과는 다음과 같다.

| Review axis | 결과 |
| --- | ---: |
| Actionable finding | `0` |
| Unsupported claim | `0` |
| Unsupported retention | `0` |
| Unimplemented eligible optimization | `0` |
| Product/runtime/Lua mutation | `0` |

Reviewer는 최종적으로 다음 관계를 확인했다.

- `c334ee97…`가 package-source subject다.
- `7a6e8ef9…`는 그 direct child이며 environment authority 두 파일만 바꾼다.
- Full gate는 G5 0016 다음 0017을 누적 보존한다.
- G5 0018은 없고 compiler ordered set과 aggregate는 마지막 contract correction에서
  바뀌지 않았다.

## 10. 최종 상태

구현의 정량 completion gate는 stated validation ceiling 안에서 닫혔다. W0 admission
evidence 누락은 unresolved 사실로 남지만 overall plan-process closeout은 complete by owner disposition이다.

- Same full-gate seed producer invocation: `6 → 3`
- Substantive distinct basename live implementation intersection: `31 → 0`
- Concrete predecessor file: `33 → 0` (`5 exact + 28 diverged`)
- Different-name exact duplicate: `0 → 0`
- Human command literal owner: `4 → 1`
- Current authority explanation owner: `4 → 1`
- Current authority maximum route hop: `4 → 1`
- Default current-context tracked bytes: `170,476 → 149,600`
- Current predecessor import/execution reference: `0`
- Unsupported retention / remaining optimization / unimplemented optimization /
  unmeasured defer / undispositioned candidate: 모두 `0`
- Product runtime/Lua mutation: `0`

Plan-process 상태를 분리하면 다음과 같다.

- Implementation: complete
- Package-bound machine terminal: PASS
- Independent Reviewer: PASS, actionable finding `0`
- Product/runtime/Lua mutation: `0`
- W0 pre-implementation admission: unresolved
- Overall plan-process: complete by owner disposition

### 10.1 Physical lightweighting

아래 수치는 product S0 `e6310737…`와 Walkthrough carrier `7f943745…`의 Git tree를 비교한
physical Git blob/context surface다.

| Scope | S0 | Final including Walkthrough | Delta |
| --- | ---: | ---: | ---: |
| Iris files | 1,753 | 1,731 | -22 |
| Iris Git blob bytes | 71,766,663 | 70,970,753 | -795,910 |
| Whole-repository files | 6,935 | 6,917 | -18 |
| Whole-repository Git blob bytes | 142,715,144 | 142,003,274 | -711,870 |

같은 구간의 source line delta는 `65 files changed, 3,259 insertions, 22,193 deletions`다.
이는 physical repository/context surface 감소이며 runtime 성능, wall-clock 개선 또는 token
절감률의 측정값이 아니다.

### 10.2 Commit timeline과 execution churn

| Milestone | Commit timestamp (KST) |
| --- | --- |
| Plan carrier | 2026-08-27 11:11:34 |
| Main implementation | 2026-08-27 11:42:50 |
| Reviewed closeout | 2026-08-27 13:13:59 |
| Walkthrough carrier | 2026-08-27 13:24:01 |

Commit timestamp 기준으로 plan→main은 약 31분, plan→reviewed closeout은 약 2시간 2분,
plan→Walkthrough는 약 2시간 12분이다. 이는 commit 시점 간 wall-clock일 뿐 active compute,
Codex의 정확한 작업 시간 또는 pre-implementation ADMIT evidence가 아니다.

최종 terminal chain은 `w7`이며, 변경된 source/test/contract subject마다 exact package와
environment subject를 새로 만들면서 versioned environment authority record 6개가 추가됐다.
Unchanged subject를 추가 confidence만을 위해 다시 실행하지는 않았다. 다만 다음 항목은
static preflight에서 더 일찍 잡을 수 있었던 avoidable churn이었다.

- composite CLI identity forwarding
- nested D16 reproduction glob
- stale frozen Round3 closure
- G5의 누락된 `execution.py`
- identity owner self-inclusion 누락
- cumulative required paths에서 0016 replacement

이 churn은 최종 correctness, Run A/B·comparator PASS 또는 Reviewer finding 0을 부정하지
않지만, process efficiency가 완벽했다고 주장할 근거도 아니다. 이번 documentation-only
correction에서는 테스트, package, writer, G5 validator 또는 Reviewer를 다시 실행하지 않았다.

최종 readpoint는 다음과 같다.

- Plan: `docs/iris_build_validation_execution_current_authority_optimization_plan.md`
- Closeout: `docs/iris_build_validation_execution_current_authority_optimization_closeout.md`
- Current navigation: `docs/IRIS_CURRENT.md`
- Human command owner: `Iris/build/ENTRYPOINTS.md`
- Static route index: `Iris/_docs/authority/iris_current_route_index.json`
- Current authority manifest: `Iris/_docs/authority/iris_current_authority_manifest.json`
- Environment locator:
  `Iris/validation/clean_checkout/authority/responsibility_refactor_environment_current.json`

## 11. Non-claims

이 세션은 Iris build/validation execution과 current-authority 탐색을 최적화했다. 다음
영역은 구현하거나 완료했다고 주장하지 않는다.

- Iris Wiki/Browser presentation 또는 Lua UI 최적화
- PZ runtime behavior, FPS, CPU, memory 또는 load-time 개선
- 실제 GPT/Codex token 절감률
- Release, freeze, RTC, Publish, Workshop 또는 deployment readiness
- 모든 외부 모드 조합의 compatibility
- Stateful cross-run receipt ledger
- Historical archive 전체를 current repository authority로 되돌리는 작업

External receipt와 archive는 계획에 따른 custody artifact다. 이 Walkthrough는 이를
복제하거나 새 seal/manifest/proof chain을 만들지 않으며, 후속 작업의 owner approval을
대신하지 않는다.
