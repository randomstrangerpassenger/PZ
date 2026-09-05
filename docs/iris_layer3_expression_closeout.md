# Iris Layer 3 expression closeout

## 현재 결과 — 사용자-facing 해상도 교정본

2026-09-05, **complete / adopted (off-live)**.
선행 결과의 구조적 fact 보존만으로 사용자 설명 해상도까지 완료됐다고 판단한 것이
잘못이었다. 보고 세션의 실제 문장 검토를 받아 동일 작업에서 S2와 acquisition을
교정했다. 선행 `0abd0d…`의 PASS를 현재 후보에 승계하지 않았다.

현재 binding:

- Manifest SHA-256: `cff8acd83715e70c6e7b82553d47e538c7f75131437491d7cf6781875f5435be`
  (`Iris/_docs/authority/dvf/layer3_expression/manifest.json`).
- Descriptions SHA-256: `df194f2c79dffd5bdf38bf5db2a3b0606ca157b8da292e32cb2d3d5842b50ef5`.
- Review SHA-256: `5bcd38efddab97670de2ac3ed1dc0a4e99de6300a679110bf8ef8ed8ae2caf6c`.
- `adoption.json`의 `superseded_result`가 선행 hash, 당시 Gate 결과와 교정 사유를
  보존한다. 새 manifest의 `supersedes`도 같은 선행 subject를 가리킨다.

`description_projection.py`가 compact first-contact를 독립 합성한다. Expanded를
잘라 붙이거나 글자 수 제한·primary 선택·runtime 재요약을 사용하지 않는다.
S2의 일반 실행 조건은 `detail_qualifier_refs`와 expanded에 남기며, 실제로 발화하지
않은 qualifier를 represented라고 세지 않는다. 기능·효과·활동·역할 contributor는
모두 표현하고 오염수·학습 수준·호환 장치·필기구처럼 첫 이해에 필요한 범위를
짧게 유지한다. Acquisition은 장소·방법·의미 있는 이용 조건과 복수 경로를 설명하며
selection weight, raw random 수식, callback/registration, marker/destination/전달
처리 흔적은 원래 payload/provenance에만 보존한다.

실제 S2:

| Item | KO |
|---|---|
| Apple | 먹을 수 있으며, 음식 준비와 조리의 재료로 사용할 수 있다. |
| Hammer | 건축 작업·가구 이동·목공 작업에 도구로 쓰이며, 물품 수리의 대상이기도 하다. |
| WaterBottleFull | 마셔 갈증을 줄일 수 있으며, 오염된 물은 중독 수치를 높일 수 있다. |

Hammer의 accepted role은 `repair_target`이므로 수리 재료·도구로 바꾸지 않았다.
Generator expanded는 기존의 연결 해제된 월드 발전기 회수와 상태/연료 보존을
설명한다. Worm은 채집, 밭갈기, 흙 퍼 담기의 세 경로를 유지한다.

최종 단일 Gate 안에서 기록한 S2 문자 길이(비어 있지 않은 1,280개/locale,
nearest-rank percentile; 이 수치는 quota나 pass threshold가 아니다):

| Locale | p50 | p95 | max |
|---|---:|---:|---:|
| KO | 12 | 39 | 44 |
| EN | 27 | 83 | 104 |

Exact target 2,105, facts 5,290, fact-locale pair 10,580, expanded acquisition
1,057/locale, upstream gap obligation 6,402를 유지한다. Current product/runtime,
L3-01~04/shared code, registry와 lock은 변경하지 않았다.

### 교정 실행과 검증 귀속

교정 콘텐츠를 읽기 위한 installed package 준비 및 최종 문법 수정을 반영한
재설치에서 기존 offline `uv sync --locked --no-editable --reinstall-package iris-tooling`
명령을 사용했고 모두 exit `0`이었다. 교정 후보 생성은 콘텐츠 검토용 한 번과 최종
생성으로 나뉜다. 최종 생성의 첫 write는 `OSError [Errno 22]`로 exit `1`이었고,
같은 repository-local 파일에 재시도하여 exit `0`으로 끝났다. 원인은 확정하지
않았으며 범위를 넓히거나 별도 검사기를 만들지 않았다. 이들은 acceptance Gate가 아니다.

유일한 Gate source와 실행 명령은 그대로다. 실제 문장 fixture, qualifier detail
partition, acquisition 내부 정보 금지 assertion과 superseded receipt 복원을 같은
source에서 교체·보강했다. 수정 후 최종 후보에 **한 번** 실행했다.

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) 'Iris/tooling/.tmp/uv-cache'
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
uv run --project .\Iris\tooling --no-sync python -I -B -m pytest -q -s --noconftest --import-mode=importlib -c .\Iris\tooling\pyproject.toml --basetemp .\.tmp\expression .\Iris\build\description\v2\tests\test_layer3_expression_results.py
```

**현재 후보 G1_EXIT_CODE=0 — `1 passed in 14.17s`.**
약 10초 시점에 입력/installed identity 로드 상태를 확인하고 후속 poll로 정상
종료를 확인했다. 별도 Gate나 공용 suite, validation-of-validation은 실행하지 않았다.

```powershell
uv run --project .\Iris\tooling --no-sync python -I -B -m iris_tooling.domains.layer3.expression_results adopt --repository-root . --candidate-sha256 cff8acd83715e70c6e7b82553d47e538c7f75131437491d7cf6781875f5435be --gate-exit-code 0 --authorization 'Owner authorized L3-05 implementation and adoption; reporting session requested user-facing resolution correction, superseding subject 0abd0d3837321558252970a1ef007ac57d8f5b149c28d1532b24d44e74d673ff. This adoption belongs only to the corrected candidate and its successful focused gate.'
```

**현재 후보 adoption/readback exit `0`.** 같은 상태 전이에서 adopted loader를
읽었으며, 실패하면 완료 상태가 아닌 superseded receipt를 복원하도록 했다.
통과 후 추가 confidence 검사 없이 문서 갱신과 지정 세션 보고로 종료한다.

### 현재 validation ceiling

- **validated:** installed identity/adopted input/member binding, 2,105/5,290/10,580/1,057
  completeness, expanded fact equality, 모든 compact 비조건 contributor와 의미 있는
  qualifier, 일반 실행 qualifier의 명시적 detail disposition, 실제 문장 fixture,
  acquisition 내부 정보 미노출, profile/residual/omission/upstream reconciliation,
  결정성, malformed consumer 거부, 실패 시 superseded receipt 복원, 현재 exact
  subject의 adopted readback, 기존 보호 bytes/registry/config 보존.
- **out_of_scope:** 실제 PZ·Menu rendering·Tooltip wrapping/Alt·S1/S3/S4 및 최종
  4줄·runtime/package/release, upstream 재조사, item별 문체 취향의 전수 보증,
  전체 repository suite와 외부 모드 compatibility sweep.
- **unvalidated_but_in_scope:** 없음. 완료 주장은 위 사용자-facing proposition과
  off-live contract 범위이며 실제 제품 노출 완료가 아니다. L3-06에 compact 재요약이나
  truncation 책임을 넘기지 않는다.

## 선행 결과 이력 — 현재 채택이 아님

2026-09-05 최초 결과 — **superseded**. 아래 `0abd0d…`의 구조적 Gate PASS는 그 exact
subject의 과거 기록이다. 보고 세션이 실제 S2의 과도한 실행 전제와 Menu acquisition의
내부 정보 노출을 지적하여 사용자-facing 해상도 교정을 재개했다. 이 PASS를 수정본에
승계하지 않으며, 수정본 완료 기록은 이 문서에 별도로 귀속한다.

사용자가 지정한 `iris_dvf_layer3_fact_bound_expression_menu_tooltip_resolution_plan.md`를
구현했다. 실행 프롬프트의 owner approval·표현·채택 사전 승인을 사용했다. 별도
승인 gate나 외부 reviewer는 추가하지 않았다. 기존 사용자 문서 삭제는 보존했다.

## 결과와 binding

| 항목 | 결과 |
|---|---|
| Exact FullType | 2,105 |
| Qualified accepted facts | 5,290 = 비획득 4,233 + 획득 1,057 |
| 승인된 fact-locale 표현 대응 | 10,580 |
| Expanded represented set | KO/EN 각각 accepted fact set과 exact equality |
| Acquisition expanded 표현 | KO/EN 각각 1,057 facts, 경로/성립 조건 보존 |
| Compact S2 | 0..1 logical row, accepted first-contact contributor 보존 |
| Contributor 없는 upstream first-contact obligation | 6,402, expression 실패와 구별 |
| Item investigation complete | 0, upstream 상태 유지 |
| Focused acceptance | `1 passed in 16.91s`, exit `0`, 실행 1회 |
| Adoption/readback | 같은 adoption 명령 안에서 성공, exit `0` |

- Manifest: `Iris/_docs/authority/dvf/layer3_expression/manifest.json`
  — SHA-256 `0abd0d3837321558252970a1ef007ac57d8f5b149c28d1532b24d44e74d673ff`.
- Descriptions: `Iris/_docs/authority/dvf/layer3_expression/descriptions.json`
  — SHA-256 `07d889ad52c1cbc20c5c98f82514af5aaa1bfec9954898b7d766284b467f1533`.
- Review: `Iris/_docs/authority/dvf/layer3_expression/review.json`
  — SHA-256 `da47d3f5044800938ca8e7afeb434bc13e60af82f0c3d09fd2370a0ac67e2ded`.
- Lifecycle receipt: `Iris/_docs/authority/dvf/layer3_expression/adoption.json`.

계획에 명시된 네 L3-01~04 manifest hash를 그대로 고정했다. 기존 loader의 member
binding과 실제 combined consumption이 성공했다. 새 authority는 공용 current
route/authority manifest/validation registry에 등록하지 않는다.

## 구현과 콘텐츠 검토

신규 모듈은 `expression_results.py`, `expression_rules.py`,
`acquisition_expression.py`이며 installed `iris_tooling`이 실행 owner다.
고정 final root 외 제품 경로에 쓰는 기능은 없다. 독립 소비 계약은
[iris_layer3_expression_contract.md](iris_layer3_expression_contract.md)에 기록했다.

모든 adopted profile이 동시에 기여한다. 음식 상태, 착용 위치, 저장/이동 조건,
독서/학습의 다른 조건, 제작·조리·월드 작업의 context-local role을 구별한다.
같은 조건의 역할 문장이 이미 설명하는 활동만 중복 mention을 줄이며 역할이나
사실은 삭제하지 않는다. Residual 사실은 expanded에 남긴다.

KO/EN의 기능 10개, 효과 payload 15개, 활동 7개, 역할 6개, predicate 21개와
채집/씨앗/낚시/덫/시작 지급/조건부 회수 14개 경로 branch를 accepted semantics에
대조했다. Rule 밖 freeform fallback은 없다. 실제 생성 문장의 Apple, Battery,
Hammer, Notebook, BookFirstAid3, WaterBottleFull, Generator를 읽고 조사·중복·조건
범위를 수정한 뒤 최종 candidate를 생성했다.

- Apple의 섭취와 조리 역할을 함께 표현하되 accepted fact가 없는 허기 감소는
  생성하지 않았다. 물의 갈증 감소와 오염수 중독은 실제 조건을 각각 보존했다.
- Worm의 채집·밭갈기·땅 퍼 담기 경로를 각각 유지했다.
- Generator는 기존 월드 발전기, 연결 해제, 접근 가능, 중단 없는 회수와 상태/연료
  전달 조건을 보존했다. 제작이나 상시 획득 가능으로 바꾸지 않았다.
- L3-04에 이미 결속된 `checkTime` 관찰에 대조하여 덫의 시작=종료 시간은 시간대
  제한 없음으로 표현했다. 새 source 조사나 upstream fact 수정은 하지 않았다.
- 건축의 경로별 조건을 전체 경로에 동시에 필요한 조건으로 확대하지 않았다.
- Acquisition dependency metadata는 실제 표현한 개별 condition path를 가리킨다.
  내부 생성 계수·식별용 이름·크기/무게 계산을 모두 문장으로 옮겼다고 주장하지
  않으며 원래 fact payload에는 그대로 보존했다. 획득 성립 조건을 생략하거나
  선택 가중치를 확률로 환산하지 않는다.

## 실제 실행

환경 준비에서 `UV_CACHE_DIR=Iris/tooling/.tmp/uv-cache`, 빌드의 `TEMP`/`TMP`는
`Iris/tooling/.tmp`로 지정했다. `pyproject.toml`과 `uv.lock`을 변경하지 않았다.

1. `uv sync --project .\Iris\tooling --locked --no-editable --reinstall-package iris-tooling --offline`
   — exit `1`: 저장소 내부 cache에 고정 `hatchling==1.27.0`이 없었다. Acceptance 실행이 아니다.
2. 위 명령에서 `--offline`을 제거하여 고정 build dependency를 받은 재설치
   — exit `0`.
3. 첫 설명 생성 후 실제 콘텐츠 수정 사항을 installed package에 반영하기 위해
   동일 offline 재설치 — exit `0`. 이 추가 준비는 발견한 콘텐츠 수정에 따른 것이며
   추가 검증이나 dependency/lock 변경이 아니다.

Candidate 생성 명령은 다음과 같으며 최초 생성 및 콘텐츠 수정 후 최종 생성 모두
exit `0`이다. 생성된 문장을 읽는 콘텐츠 작업은 acceptance Gate로 계산하지 않는다.

```powershell
uv run --project .\Iris\tooling --no-sync python -I -B -m iris_tooling.domains.layer3.expression_results prepare --repository-root .
```

유일한 automated acceptance 명령:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'
uv run --project .\Iris\tooling --no-sync python -I -B -m pytest -q -s --noconftest --import-mode=importlib -c .\Iris\tooling\pyproject.toml --basetemp .\.tmp\expression .\Iris\build\description\v2\tests\test_layer3_expression_results.py
```

`G1_EXIT_CODE=0`, `1 passed in 16.91s`.
실행 중 약 10초 시점의 입력 로드 상태를 확인하고 다음 poll에서 정상 종료를
확인했다. 무한루프·장기 실행으로 중단한 작업은 없다. 결정성의 두 번째 생성,
negative fixture, preserved bytes는 모두 이 단일 focused source 안에서 검사했다.

공용 conftest는 정규 source 등록과 repository-external output을 요구한다.
이번 계획은 해당 registry 변경과 외부 workspace를 범위 밖으로 정했으므로
`--noconftest`와 명시적 installed import/config/basetemp를 사용했다. Validation
coverage를 제거하지 않았다. 테스트 scratch는 `.tmp/expression` 하나를 공유했다.

```powershell
uv run --project .\Iris\tooling --no-sync python -I -B -m iris_tooling.domains.layer3.expression_results adopt --repository-root . --candidate-sha256 0abd0d3837321558252970a1ef007ac57d8f5b149c28d1532b24d44e74d673ff --gate-exit-code 0 --authorization '2026-09-05 owner implementation request explicitly preauthorizes plan/document owner approval, expression approval and authority adoption; runtime/product migration excluded.'
```

Exit `0`. Exact candidate bytes를 final 위치에 유지하고 같은 명령에서 adopted
loader readback을 수행했다. 이후 별도 readback/final-binding Gate나 추가 confidence
검사는 실행하지 않았다. L3-04/shared loader는 수정하지 않았으므로 기존 suite를
다시 실행하지 않았다.

## Surface와 validation ceiling

Authority/compatibility/public-output surface는 신규 **off-live consumer contract**에
한정된다. 기존 L3-01~04 sealed member, 보호 대상 330개, current config/route/registry,
`pyproject.toml`/`uv.lock` 보존은 단일 Gate에서 확인했다. Runtime behavior 변경은
없으며 현재 사용자에게 표시되는 Menu/Tooltip 문장을 바꾸지 않았다.

- **validated:** installed module identity와 source-root bootstrap 부재; adopted
  input/member binding; exact target/fact/locale/acquisition completeness;
  context/qualifier closure와 실제 predicate 문장; 복수 profile와 residual;
  S2/expanded/omission/upstream reconciliation; 결정성; malformed ref/member/input,
  stale review/locale fallback/무근거 문장 거부; 실패한 adoption의 receipt 회수;
  exact candidate adoption 및 adopted loader readback; 위 보호 bytes 보존.
- **out_of_scope:** PZ 실행, Menu rendering, Tooltip physical wrapping과 Alt,
  S1/S3/S4 및 최종 4줄, Lua/package/install/Workshop/release, 미해결 upstream 재조사,
  source corpus 전수 재인증, 모든 item의 번역 취향 보증, 전체 repository suite와
  외부 모드 compatibility sweep.
- **unvalidated_but_in_scope:** 없음. 위 선언은 rule/contract와 명시된 검증 범위에
  한정되며 제품 노출이나 모든 개별 문장의 문체 전수 보증을 의미하지 않는다.

이 closeout은 runtime/product 전환, deployment, release readiness를 선언하지 않는다.
L3-06은 adopted description readpoint를 재조사·재번역·대표 선택 없이 소비해 실제
제품과 통합한다. `.tmp/expression`과 package 준비 cache는 실행 보조 자료이며
Iris의 canonical validator, 정규 검사기, 새로운 validation authority가 아니다.
