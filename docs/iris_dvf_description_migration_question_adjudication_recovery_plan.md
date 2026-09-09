# Implementation Plan — DVF-RECOVERY-A

- 문제: 기존 설명 의미 이관 누락과 질문별 판정 복구
- 작성일: 2026-09-07
- 상태: `planned` — 계획 작성 완료와 recovery 구현·채택 완료를 구분한다.
- 개정: v2 — 사용자 첨부 「DVF-RECOVERY-A Implementation Plan Review」의 비충돌 필수 수정 1·2 및 중요/권고 사항을 반영했다. 검토의 FAIL 이력은 보존하며 본 개정 자체를 재검토 PASS로 간주하지 않는다. L3-02 범위 충돌은 아래 별도 판정 기록을 따른다.
- 추가 개정: v3 — 후속 검토 I-1~I-4와 M-1을 반영해 검증 등록 선례, 정의 ownership, 비의미 clause 반례, import-time I/O 확인을 보강했다. M-2의 상류 모듈 변경 시 재검증 의무는 closeout 기록 항목으로 유지한다.
- 추가 개정: v4 / 2026-09-08 — 사용자 요청에 따라 실제 복구 미완료와 근거 한계를 구분하는 완료 조건, 기본 재사용 방식이 막혔을 때의 최소 구현 변경 경로, 단일 통합 acceptance 중심의 검증 최소화를 반영했다. v4 개정 자체는 구현·검증 PASS가 아니다.
- 입력: 사용자 첨부 「DVF-RECOVERY-A — 기존 설명 의미 이관 누락과 질문 판정 복구 Roadmap」, [문제 A](iris_dvf_description_migration_recovery_problem.md)
- 양식: [PLAN_TEMPLATE.md](PLAN_TEMPLATE.md). 절 번호와 하위 항목을 유지하고 내용을 실제 저장소에 맞춰 구체화했다.
- 최상위 authority: [Philosophy.md](Philosophy.md). 현재 결정·구조·진행 상태는 [DECISIONS.md](DECISIONS.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md)를 따른다.

## 1. Objective

동일한 exact case-sensitive FullType 2,105개에서 predecessor가 제공하던 개별 의미와 successor의 사실·표현 관계를 전수 대조한다. 근거가 확인된 의미는 기존 다중 typed-fact 계약으로 복구하고, 잘못되거나 책임이 다른 의미는 정정·축소·이동·제거 사유를 남긴다. 조사 후에도 확인되지 않은 의미는 unresolved로 공개한다.

기준 비획득 질문 `(item_id, axis_id, scope_ref)` 9,982개 전부의 귀속과 잔여 범위를 재평가하고, revised semantic/acquisition 결과를 2,105 application 및 KO/EN expanded·compact successor까지 연결한다. 근거로 입증된 정의 결함에는 bounded L3-02 successor를 허용하되 기준 질문 전체의 lineage와 잔여 의무를 보존한다. 정의 수정도 동일 정의 내 누락 인스턴스 복구도 없으면 같은 9,982 key를 재파생한다. Source-bound 참여 인스턴스 복구 시 baseline 9,982 key와 전수 attribution·잔여 의무를 보존하고 추가 질문을 포함한 successor N을 별도 집계한다. 기존 L3-01~06의 sealed subject와 historical completion은 유지한다.

완료 단위는 근거 있는 의미의 실제 복구·정정, 질문별 판정 복구와 이를 표현까지 연결한 successor chain이다. Accounting은 이 결과를 확인하는 수단이며 기록 작성만으로 복구를 대신하지 않는다. 설명 공백 0, unresolved 0, 모든 아이템의 investigation complete는 목표가 아니다. A 범위에서 현재 자료로 진행 가능한 것으로 확인된 해석·판정·이관·표현 작업을 미수행으로 남긴 채 complete를 선언하지 않는다.

## 2. Scope

- 동일 대상의 predecessor structured input, KO/EN 설명, 현재 L3-02/03/04/05 readpoint identity 확인.
- blank 전환뿐 아니라 non-empty 설명 내부의 기능·효과·활동·역할·조건·획득 의미 차이 조사.
- source-bound fact recovery/correction, question-local 판정 생산, fact identity와 dependent reference 재결속.
- result/producer 수정만으로 해결할 수 없다고 입증된 exact L3-02 definition defect의 bounded successor correction 및 전 chain의 definition 호환성 결속.
- semantic successor, 필요 시 acquisition correction, 결합 application, expression successor, migration/residual 기록.
- 검증된 동일 expression subject를 B/C에 전달하는 adoption·handoff 설계.

### Explicitly Out Of Scope

- B의 Tooltip 생산·Recipe companion·current 소유권 복구 및 C의 Menu 구조·가독성 구현.
- 현재 Lua, runtime generation pointer, package/install, 사용자 설치본 변경.
- L3-01 계약 개정, 복구와 무관한 L3-02 taxonomy/profile 전면 개편, Layer 4 corpus 재구축, 외부 모드 전수 조사.
- 기존 작업 파일 복원·삭제, unrelated refactor, 영구 validator/framework/governance 계층 신설.

## 3. Non-Goals

- `primary_use`나 대표 역할 선정으로 회귀하지 않는다.
- 기존 문장 그대로 유지, 모든 item 최소 문장 보장, unresolved 수를 낮추기 위한 판정 완화를 하지 않는다.
- 전체 engine 구현·동적 행동을 무제한 해명하지 않는다.
- 권장·효율·우열 평가, 게임 상태 변경, runtime predecessor fallback을 도입하지 않는다.
- A 완료를 replacement product 보존, PZ runtime 검증, B/C 완료, freeze/RTC/Publish/release readiness로 확장하지 않는다.

## 4. Assumptions

### 저장소 확인 결과와 실행 전제

2026-09-07 working tree를 읽어 확인한 내용이다. 아래 수치는 기존 manifest/문제 문서의 관측치이며 이번 계획 작성에서 재실행한 검증 PASS가 아니다.

| 확인 대상 | 코드·자료에서 확인한 사실 | 실행 계획에 미치는 영향 |
|---|---|---|
| 비획득 판정 | `semantic_results.py:503~523`은 scope를 A~E route에 매핑하고 `attempt['dependency']`를 기본 blocker로 복사한다. `CantEat` native ingestion의 operation/effects만 whole-scope N/A 예외가 있다. | route 관측은 유지하되 질문 결과를 별도 evidence/residual 평가로 생산한다. |
| 부분 사실 | 같은 파일의 fact-question binding은 기본 `contribution='partial'`이다. | 사실 존재나 blocker 제거만으로 terminal을 만들지 않는다. |
| 노트류 | `semantic_results.py:453` 부근은 `record_written_notes`와 편집 constraint를 생성한다. 원본 `ISInventoryPaneContextMenu.lua:760` 부근에는 필기구·타 사용자 lock에 따른 읽기/쓰기 분기가 있고, `onWriteSomething`은 `seePage(1)`을 창에 전달한다. `ISUIWriteJournal.lua` 생성자는 custom page를 읽는다. | 독립 열람 의미와 편집 조건을 조사할 근거가 있다. 읽기·효과·조건 12문항 전부 해결은 아직 입증되지 않았다. |
| 결합 소비 | `acquisition_consumption.load()`는 L3-04 manifest의 `semantic_readpoint`를 따라 L3-03을 읽는다. `consume_payloads()`는 candidate끼리만 허용한다. | 기존 L3-04에 새 L3-03을 단순 교체할 수 없다. 사실 재사용과 readpoint 재결속을 분리한다. |
| 표현 생산 | `expression_results.py`는 `ROOT`, `INPUTS`, baseline `DENOMINATORS`를 고정하고 adopted input만 정규화한다. `prepare()`는 이미 adopted인 출력 덮어쓰기를 거부한다. | 새 candidate chain과 별도 successor 경로가 필요하다. 새 fact 수를 기존 5,290에 맞춰서는 안 된다. |
| sealed 범위 | L3-03 manifest는 producer/model/source reader/resolver/test/human contract를, L3-05 manifest는 expression 코드/test/human contract를 member hash로 결속한다. | 기존 모듈·테스트를 직접 수정하면 역사적 loader가 drift로 거부할 수 있다. 변경 전 transitive member census가 필요하다. |
| 제품 기준 | `IrisLayer3DataCurrent.lua`는 `dvf33-ed92fa5c9ed4a1ed367f5d79365d04e1996e36a05d76a33bd7b8dd2176e7f82f`를 가리킨다. | repository current와 새 expression, delivered product, 사용자 설치 상태를 동일시하지 않는다. |
| 현재 작업 상태 | Iris 코드와 공통 문서에 기존 수정이 있고, 여러 historical contract/closeout 문서가 working tree에서 삭제된 상태다. 그중 일부는 manifest가 여전히 참조한다. | 계획은 새 문서만 추가한다. 실행 시 누락·drift는 별도 baseline blocker로 기록하며 자동 복원하거나 과거 hash를 바꾸지 않는다. |

기준 수치는 target 2,105, 비획득 8,882+1,100=9,982, unresolved 9,900/N/A 82, semantic facts 4,233이다. 획득은 질문 2,105, resolved 1,025/unresolved 1,080, facts 1,057이며 결합 facts 5,290, KO/EN fact-locale pairs 10,580이다. predecessor blank 6, successor expanded blank 552, compact blank 825와 item complete 0은 exact baseline에서 재확인한다. `552-6=546`을 손실 item 집합으로 사용하지 않는다.

### 로드맵의 별도 판정 사항에 대한 계획상 제안

다음은 이 계획의 실행 경계를 위한 제안이며 이미 채택된 ecosystem 결정으로 기록하지 않는다. 후속 실행에서 다른 선택이 확정되면 영향 범위와 입력 binding부터 갱신한다.

| 미결정 사항 | 계획상 선택 | 근거·한계 |
|---|---|---|
| recovery ledger authority | candidate/closeout에 결속된 내부 audit artifact로 둔다. 사실·질문 truth는 L3-03/04가 소유한다. | 기존 owner를 중복하는 semantic authority를 만들 필요가 없다. 기록의 작성자와 hash는 명시한다. |
| L3-02 definition correction | 사용자 지정 세션의 판정에 따라 Option A: revision 1이 기본이며 입증된 exact definition defect에 한해 A 안의 bounded successor correction을 허용한다. | historical revision 1은 불변이다. 변경 admission·lineage·분모 분리·잔여 보존·전 chain definition 호환성 조건을 아래와 P4~P6에 적용한다. |
| B/C handoff 시점 | source 조사·구조 작업은 독립 진행 가능하다. 소비용 handoff는 검증된 coherent chain 단위로 허용한다. | A 전량 종결을 B/C 착수 조건으로 삼지 않는다. 증분도 full target/question 재파생과 단일 subject 검증을 거친다. |
| integrated product evidence | A 완료는 offline successor expression까지로 한정한다. | 실제 replacement product의 보존 주장은 B/C 통합 입력에서 별도 증명해야 한다. |
| 한쪽 안의 확장 항목 | provenance strength, owner 판단 대기, 질문 귀속 불가를 audit 필드로 채택한다. baseline 후보의 종류도 구분한다. | 새로운 fact/status taxonomy로 승격하지 않는다. owner-adopted prose만으로 source-confirmed fact를 만들지 않는다. 새 영구 검증 계층도 만들지 않는다. |

### L3-02 범위 판정 기록

사용자는 검토 간 충돌을 [지정 세션](codex://threads/01a07ad6-0377-7d62-9c8d-bc833a049714)에 질문하고 그 답을 따르도록 요청했다. 해당 세션의 회신은 **Option A**다. 기존 문제 A가 질문 정의·판정·사실 결속을 포함하므로 실제 정의 결함을 별도 문제로 무조건 미루면 복구 범위를 축소한다는 이유다. 이 회신은 조건부 범위 판정이며 구현·검증·채택 완료나 배포 승인이 아니다.

admission에는 exact 영향 질문, 원래 정의, source/consumer 기능 경로, 기존 정의로 정당한 답을 처리할 수 없는 이유를 요구한다. route blocker 전파 오류는 result producer에서 고치며, 자료 부재·engine 미확인을 definition defect로 바꾸지 않는다. 노트류 12문항은 결함/해결로 선판정하지 않는다. 복구에 필요한 영향 profile/axis/scope만 수정하며 최소 필요 변경이 bounded 범위를 벗어나면 별도 확장 제안과 A의 미완료 범위를 기록한다.

### Expression reusable boundary 확인과 채택 경로

검토 후 `expression_results.py:80~321`, `expression_rules.py`, `description_projection.py`를 읽어 다음 경계를 확인했다. 이는 코드 경계 확인이며 successor 실행 검증은 아니다. 표의 재사용 선택은 우선 경로이며, 아래 v4의 최소 대체 변경 조건이 구현 선택에 우선한다.

| 경계 | 실제 결속 | 선택 |
|---|---|---|
| 모듈 import 시점 동작 | 확인한 `expression_results.py`의 ROOT/INPUTS/DENOMINATORS는 literal 상수이며 그 평가 자체가 predecessor 파일을 읽지는 않는다. `description_projection.py`는 import 시 `rules.PREDICATES`로 QUALIFIERS를 구성한다. 다만 expression 모듈은 combined/investigation 등도 import하므로 직접 상수 검사만으로 transitive import의 무 I/O를 증명할 수 없다. | P1에서 package 초기화와 transitive imports를 포함해 authority/source/product 데이터에 대한 import-time I/O를 검사한다. 실행 시 관측은 아직 하지 않았으며 아래 기본 재사용 경로는 이 검사 통과를 전제로 한다. |
| `read_inputs()`, `read_review()`, `prepare()`, `load()`, `adopt()` | 기존 ROOT/INPUTS/receipt와 adopted lifecycle에 결속 | successor에서 호출하지 않는다. 신규 입력 검증·review binding·writer/loader가 책임진다. |
| `normalize()` | 관계 정규화는 독립적이나 mode/status가 adopted여야 한다. | candidate status를 속여 호출하지 않는다. 신규 adapter가 동일 qualified-ref·dependency·application 불변식을 검사하여 입력 모델을 만든다. |
| `produce(inputs, review)` | 본문은 I/O 없는 합성이고 denominator는 실제 facts에서 계산한다. 다만 반환값 `inputs`는 전역 INPUTS를 복사한다. | 기존 지원 payload에는 읽기 전용으로 재사용한다. 반환된 body를 내부 중간값으로만 취급하고, 기존 `inputs` 메타데이터를 외부에 저장하기 전에 신규 envelope를 실제 verified successor bindings로 구성한다. |
| `expression()`, `_profiles()`, `_selection()`, `_expand_qualifiers()`, `_coalesce_contexts()`, `_blocks()` | 입력 관계와 기존 semantic/qualifier grammar를 소비한다. | 지원 domain에서는 재사용한다. private helper도 exact module hash와 interface 회귀 검사로 결속한다. |
| `expression_rules.core/qualified()`, `description_projection.compose()` | FUNCTIONS/PREDICATES/CONTEXTS/QUALIFIERS 등 closed domain이며 알 수 없는 payload는 `expression_gap`으로 거부한다. | 신규 의미에는 아래 isolated composition의 bounded 규칙만 추가할 수 있다. 기존 모듈 global/dictionary monkeypatch는 금지한다. |

**우선 경로는 신규 adapter/envelope + 기존 pure composition 재사용**이다. 이는 구현 선택이며 A 완료의 고정 조건이 아니다. Fake adopted status, 전역 상수 monkeypatch, source 재작성·동적 실행을 통한 검증 우회는 금지한다. 역사적 subject의 불변성과 현재 구현의 영구 수정 금지는 구별한다. 필요한 최소 parameterization·공통 함수 분리·successor 구현 변경은 아래의 대체 경로 판단에 따라 허용한다.

새 payload가 기존 사전 밖인 경우에는 **bounded isolated successor composition**을 사용한다. 신규 dispatch에서 해당 payload의 KO/EN expanded·compact·qualifier 규칙을 명시하고 기존 지원 domain은 기존 함수로 처리한다. 분리 단위는 fact 하나가 아니라 context/qualifier/first-contact contributor 관계가 닫힌 집합이다. 집합을 나눌 때 dependency를 끊거나 compact 의미 합성을 잃으면 분리하지 않는다. 기존 body 알고리즘 전체를 복사하지 않고, 새 branch와 호출·병합 및 reference 검증만 신규 모듈이 소유한다. exact 지원 predicate와 rule domain은 review에 결속한다.

우선 경로가 성립하지 않으면 실제 결합 지점, 필요한 최소 변경, 역사적 subject의 보존 및 loader 호환성을 확인하고 대체 구현을 선택한다. 검증된 archive/checkout 또는 기존에 지원되는 버전별 source 보존을 활용할 수 있으나, historical hash를 현재 코드에 맞춰 바꾸거나 과거 PASS를 재사용해서는 안 된다. 새 successor가 변경된 구현에 정확히 결속되고 영향 consumer가 검증되는 조건에서 최소 수정·재구성을 허용한다. 대체 경로와 실제 보호 대상의 변경은 이 계획/closeout에 기록하며 별도 승인·Gate를 기본 신설하지 않는다. 기존 계약의 명시적 추가 절차가 실제 적용되면 그 절차는 따른다.

선호한 adapter 방식이 실패했다는 이유만으로 A를 blocked로 끝내지 않는다. 필요한 최소 대체 경로도 실제 계약·권한·필수 자료 제약 때문에 진행할 수 없으면 `blocked`, 허용된 구현이 미완료이면 `partial`이다. 어느 경우에도 A5 미충족 subject의 소비용 adoption/B·C handoff는 금지한다. 조사 자료 공유는 가능하지만 소비 가능한 expression으로 표시하지 않는다. 이 경로는 A의 복구에 필요한 변경만 허용하며 장기 병렬 authority나 시스템 전체 복제를 정당화하지 않는다.

Import 시점의 숨은 predecessor 의존 여부는 선택한 재사용 경로의 사전 조사로 확인한다. 관련 위험이 있으면 단일 통합 acceptance 안에서 fresh process와 데이터 접근 제한을 이용한 사례로 확인하며, 별도 import Gate나 범용 I/O 감시 framework는 만들지 않는다. 코드 로딩·명시적 member 검증과 숨은 authority/source/product 접근을 구별한다. 숨은 의존 발견 시 최소 제거·명시적 입력화 등 위 대체 경로를 검토한다. 실제 predecessor 파일 삭제·이동이나 loader 검증 우회는 하지 않는다. 재사용하지 않는 경로의 import fixture까지 의무적으로 구현하지 않는다.

## 5. Repository Areas Affected

아래 기존 파일은 조사·재사용 지점이다. hash-bound 파일은 자동 변경 대상으로 간주하지 않으며, 필요한 변경은 §4의 역사 보존·successor 결속 조건을 따른다. `(신규 제안)` 경로는 아직 구현되지 않았다.

### Code

- `Iris/tooling/src/iris_tooling/domains/layer3/semantic_results.py`, `semantic_model.py`, `source_reader.py`, `interpretations.py`: source 관측, fact identity/검사, 기존 판정 참조.
- 같은 디렉터리의 `investigation.py`: `resolve_item()` 및 completion/first-contact 의미 재사용.
- `acquisition_results.py`, `acquisition_sources.py`, `acquisition_consumption.py`: 획득 owner와 결합 제약 확인.
- `expression_results.py`, `expression_rules.py`, `acquisition_expression.py`, `description_projection.py`: 표현 규칙·qualifier·정상 생략 재사용.
- `(신규 제안)` 같은 디렉터리의 `recovery.py`: bounded successor 생산·소비 진입점. 복구 전용 규칙이 커지면 같은 도메인 안에만 분리한다.
- `(신규 제안)` 같은 디렉터리의 `recovery_expression.py`: 우선 candidate adapter, successor envelope/loader와 필요한 expression dispatch. §4 검토 결과 더 작은 기존 구현 변경이 적절하면 파일 분리 방식도 조정할 수 있다.
- `(신규 제안)` `Iris/build/description/v2/tests/test_layer3_recovery.py`: 이번 correction의 focused acceptance와 반례 검사.
- `scripts/`, `lua/`: 실제 게임 선언·consumer를 읽는 원본 입력. 수정하지 않는다.

### Docs

- 본 계획 문서.
- `(신규 제안)` `docs/iris_dvf_description_migration_question_adjudication_recovery_closeout.md`: exact subject, 검증 명령/exit, 미해결, handoff ceiling.
- 채택 시 `docs/DECISIONS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`에 successor 결과를 추가한다. historical completion을 재작성하지 않는다.

### Config

- 기존 `Iris/_docs/authority/iris_current_route_index.json`, `iris_current_authority_manifest.json`: 현재 경로와 구독자를 조사한다. 검증 전 변경하지 않는다.
- successor readpoint 등록이 기존 제품 소비를 암묵적으로 전환한다면 별도 명시 경로를 사용한다. runtime current pointer를 건드리지 않는다.
- `Iris/tooling/pyproject.toml`, `uv.lock`, `Iris/validation/execution/`은 원칙적으로 불변이다. 새 정규 gate 등록을 전제하지 않는다.

### Generated Artifacts

- 읽기 전용 predecessor 후보: `Iris/build/description/v2/data/dvf_3_3_facts.jsonl`, `dvf_3_3_decisions.jsonl`, `dvf_3_3_input_manifest.json`, `frozen_predecessor_inputs/`와 current Lua generation.
- 읽기 전용 authority: `Iris/_docs/authority/dvf/layer3_successor/`, `layer3_investigation/`, `layer3_semantic_results/`, `layer3_acquisition_results/`, `layer3_expression/`.
- `(신규 제안)` `Iris/_docs/authority/dvf/layer3_semantic_results/recovery_a/<subject>/`, 필요 시 acquisition의 대응 하위 경로, expression의 대응 하위 경로: immutable successor subject. 기존 root manifest는 보존한다.
- definition defect가 admission을 통과하면 기존 `layer3_investigation/` 소유권 아래의 additive successor definition/readpoint도 대상이다. 기존 manifest/lifecycle 형식을 우선 재사용하며 새 형식·gate·증거 디렉터리 자체를 별도 요구하지 않는다.
- `(신규 제안)` repository-local `.tmp/semantic/recovery-a/<run>/`: 입력 binding, claim inventory, question reassessment, candidate 검증 자료. 최종 audit은 successor member 또는 closeout binding으로 보존하며 임시 경로 자체를 authority로 삼지 않는다.

## 6. Planned Changes

### Change 1 — P1: Exact baseline과 sealed dependency 고정

**Purpose:** 서로 다른 generation과 working tree 상태가 섞이지 않는 재현 가능한 입력을 만든다.

**Files:** 위 predecessor 입력, L3-01~05 manifest와 transitive members, runtime pointer, current route, 신규 recovery 진입점/입력 binding.

**Implementation Notes:**

- FullType는 대소문자 그대로 join한다. target 2,105개에 missing/extra/duplicate를 검사한다.
- predecessor structured facts/decisions와 실제 KO/EN generation의 관계를 입증한다. 저장소 current, delivered candidate, 사용자 설치본을 별도 baseline 후보로 기록한다. 설치 증거가 없으면 unknown으로 둔다.
- manifest/member/source/producer 경로·SHA, target set digest, git 상태, source snapshot을 기록한다. blank 6/552의 exact subject를 찾지 못하면 입력 미확정으로 남긴다.
- 모든 transitive sealed code/doc/test 목록을 만든다. 누락된 member는 경로·기대 hash·소비 실패 지점을 기록하고 historical bytes를 대체하지 않는다. 검증된 archive/checkout이 필요하다면 별도 입력 위치에서 identity를 확인한다.

**Validation:** exact target set equality, locale/structured subject 일치와 manifest member closure는 입력 수용 검사로 수행하고 최종 통합 acceptance에서 같은 결과를 재사용한다. 별도 P1 Gate/receipt는 만들지 않는다. 필요한 member의 누락·drift는 검증된 archive/checkout 등 허용된 입력 확보 경로로 해결한다. 필수 baseline을 확보하지 못하면 source-confirmed 이관/보존 주장과 verified chain adoption은 blocked다. 구현 경로의 불일치는 baseline identity 실패와 구별해 §4의 대체 경로를 검토한다. P1에서 모든 후속 표현 branch의 구현 가능성 입증을 요구하여 독립적인 원본 조사를 막지 않는다.

baseline 미확정 중 허용하는 P2 작업은 identity가 확인된 단일 predecessor 자료의 claim 후보/locator 관측까지다. 서로 다른 subject의 blank 전환, semantic delta, preserved/recovered 판정과 A1 전수 완료는 금지한다. 검증된 입력으로 다시 결속하기 전까지 해당 자료에 provisional 표시를 유지한다.

### Change 2 — P2: Predecessor claim inventory와 의미 차이

**Purpose:** 문장 유무가 아닌 의미 단위로 전체 이관 상태를 관측한다.

**Files:** predecessor facts/decisions/KO·EN output, current semantic/acquisition/expression corpus, recovery inventory/diff.

**Implementation Notes:**

- structured field에서 claim을 우선 추출하되 문장 안의 복수 기능·조건·획득 의미를 분해한다. KO/EN rendered description을 독립 감사하여 structured 추출 누락도 찾는다.
- 추출 claim 목록을 자기 자신과 대조하는 검사를 피한다. 원본 rendered prose의 locale별 span/clause index를 별도로 만들고 각 영역을 `claim_ids`, 이유가 있는 비의미적 연결 표현, `unsegmented` 중 하나로 연결한다. `unsegmented`가 남으면 A1 미충족이며, 모르는 의미를 연결 표현으로 숨기지 않는다.
- 비의미 clause row에는 exact locale/span/text binding, `classification_rule_ref`, 해당 rule의 적용 근거와 검토 기록을 요구한다. rule은 연결·문법 역할과 독립적인 기능/조건/획득 등 명제를 담지 않는 이유를 설명해야 한다. 단순히 이해하지 못했다거나 “연결 표현”이라는 generic reason은 거부한다. 판정하기 어려운 clause는 `unsegmented`로 유지하고 A1 미충족을 드러낸다.
- item row 2,105개를 반드시 남기고 claim이 없는 item도 명시한다. claim ID는 predecessor subject/item/locator/meaning을 재현 가능하게 결속한다.
- claim row는 `item_id`, `predecessor_claim_id`, `predecessor_field_or_surface`, `predecessor_text_ref`, `predecessor_source_leads`, `candidate_successor_fact_refs`, `verified_source_refs`, `migration_disposition`, `reason`, `remaining_uncertainty`를 포함한다.
- 관측 단계의 미판정과 bounded 조사 후 unresolved를 구분한다. 문자열 유사도는 검토 후보 생성에만 사용하고 preserved 판정은 payload·조건·범위로 한다.
- blank→blank/non-empty, non-empty→blank/non-empty의 전환 집합과, 문장이 남은 item 내부 delta를 별도 산출한다.

**Validation:** 모든 predecessor claim이 item과 원래 표면에 결속되고, 동일 입력의 inventory가 결정적이다. 원본 KO/EN clause index의 누락·미분해 영역 0을 독립 확인하고 모든 non-semantic row의 rule 참조·exact span 적용 근거와 검토 기록을 확인한다. 의미 있는 기능/조건 clause를 비의미로 잘못 분류하거나 generic reason으로 대체한 fixture는 실패해야 한다. prose-only claim의 자동 accepted fact 승격은 0이어야 한다.

### Change 3 — P3: 근거 기반 의미 복구·정정·책임 분류

**Purpose:** 각 claim에 근거와 disposition을 부여한다.

**Files:** 원본 `scripts/`, `lua/`, source/provenance 해석, recovery rules 및 migration audit.

**Implementation Notes:**

- `claim → current source/provenance → typed fact → result → expression`으로 추적한다. source 위치뿐 아니라 실제 consumer, 조건, 범위, snapshot hash를 결속한다.
- disposition은 already represented, recovered, corrected/narrowed, responsibility relocation/removal, unresolved로 기록한다. 각 항목에 reason을 요구하며 corrected/removed는 무엇이 왜 달라졌는지 남긴다.
- provenance 진단은 `source_binding/strength`, `owner_adoption_evidence`, `review_state`, `owner_presence_evidence`를 독립 축으로 기록한다. source-bound/weak provenance, owner-adopted, review-hold, explicit owner absence를 하나의 `provenance_state` enum으로 합치지 않는다. 확인 불가 owner-adopted 내용은 owner 판단 대기로 남기며 참이라고 가정하지 않는다.
- question attribution은 exact key·귀속 근거를 기록한다. 귀속 불가는 별도 audit 결과이며 조용히 버리거나 새 질문을 임의 생성하지 않는다.
- 획득은 L3-04로 보낸다. Recipe·우클릭·EvolvedRecipe의 구체적 관계는 Layer 4 책임으로 식별하되 실제 목적지 보존을 확인하지 못하면 relocation 완료를 주장하지 않는다.
- 의미가 바뀌는 fact는 새 ID를 만들고 qualifier/context/dependent refs를 갱신한다. provenance 위치만 바뀌는 경우 semantic identity의 기존 규칙을 따른다.
- 조사 중 현재 자료에서 추가로 확인 가능한 구체적 consumer·조건·의미가 발견되면 A 범위의 복구 작업으로 이어간다. 임의 시간/표본/단계 한도에 도달했다는 이유만으로 그 작업을 근거 부족 unresolved로 종결하지 않는다. 실제 자료·해석 한계와 아직 수행하지 않은 해석/구현을 구별하며 후자는 완료 조건을 막는다. 무제한 엔진 탐색이나 전 세계 자료 부재 증명은 요구하지 않는다.

**Validation:** recovered/corrected fact의 source chain, 사실별 조건, 이전 ID→새 ID mapping, correction reason을 검사한다. unresolved에는 조사한 범위·필요 자료·남은 불확실성이 있어야 한다.

### Change 4 — P4: Question-local 판정 복구

**Purpose:** 실제 답한 범위와 잔여 범위에 필요한 dependency로 질문을 판정한다.

**Files:** 신규 recovery 판정 구현, 기존 semantic model/interpretations/resolver 참조, question reassessment audit, focused tests.

**Implementation Notes:**

- 순서는 `exact scope → accepted/partial/direct evidence → answered scope → remaining scope → effective blockers → 기존 result semantics`다.
- route attempts는 조사 이력으로 유지한다. 해당 route의 모든 dependency를 각 질문에 복사하지 않는다. effective blocker 제거도 whole-scope closure 증거를 대신하지 않는다.
- reassessment row에 exact key, previous result/blockers, accepted/partial fact refs, direct evidence refs, answered/remaining scope, effective blocker refs, successor result, change reason을 남긴다.
- 결과 변경 여부와 무관하게 **9,982 row 전부**에 `attribution_status`, 질문/잔여 범위와 evidence의 관계, `attribution_rule_ref`, 실제 적용 입력 refs를 요구한다. 성공한 귀속은 각 `effective_blocker_ref`가 어떤 remaining scope에 왜 필요한지 연결한다. terminal의 빈 blocker는 whole-scope 해소/배제 증거로 설명한다. unresolved에서 귀속을 확정할 수 없으면 `attribution_failure`와 조사 시도·사유·남은 범위·필요 자료를 명시하고 terminal을 금지한다. 이는 audit 값이며 result status taxonomy를 대체하지 않는다.
- 같은 결과가 유지된 unresolved row도 위 조건을 만족해야 한다. 여러 row가 같은 rule/blocker를 공유하는 것은 허용하지만 각 exact question의 predicate 적용·residual 결속 근거가 있어야 한다. question-local 근거 없는 route-wide 일괄 복사, 누락 attribution, 단순 generic failure 문구는 validation failure다.
- 기준 9,982 전체 key와 이전 8,882/추가 1,100 관계를 보존한다. 정의 변경과 누락 인스턴스 추가가 모두 없으면 동일 key set을 재파생한다. 기존 정의의 source-bound 참여 추출 누락을 복구하는 경우 baseline key 삭제·이름 변경·정의 재해석 없이 새 instance key를 추가할 수 있다. §4 admission을 통과한 정의 변경이 있으면 원래 key별 유지/정정/분할/병합/제외와 successor key·잔여 의무 mapping을 만든다. revision은 metadata/readpoint로 결속하며 key에 임의의 네 번째 성분을 추가하지 않는다.
- 기준 `9,982 = unresolved 9,900 + scoped N/A 82`는 역사적 집계다. successor question 분모 N과 상태 수는 별도 보고하고 증감을 lineage로 설명한다. 정의 재분류와 실제 evidence 확보에 의한 해결을 구분하며 새 분모로 과거 완료율을 개선하지 않는다.
- 범위를 좁히거나 이동할 때 원래 미확인 의미는 기존/successor 질문 또는 명시적인 residual investigation obligation에 남긴다. item/context에 적용되지 않는다는 결론도 scoped evidence가 필요하다. residual이 current application/completion에서 보이지 않게 사라지는 변경은 거부한다.
- 상태 변경, migration 연결, 새 interpretation, N/A 변화와 모든 definition delta/lineage는 집중 검토한다.
- Notebook/Journal/Doodle/SheetPaper2의 `activity:reading` operation/effects/conditions 12문항을 고정 regression set으로 둔다. 필기구 없는 열람과 편집 제한을 구별한다. 공통 source predicate로 처리하고 item-name 특별 terminal 규칙은 만들지 않는다.
- exact 선언 부재·중복 선언, engine handoff, dynamic registration, runtime-state 의존 반례를 남긴다. `Base.Bag_PistolCase`, `Base.Lemongrass`, `Base.NoiseMaker`, `Base.ShotgunCase1`은 현재 anomaly 목록이며 구체적 부재/중복 유형은 실제 source로 확인한다.
- partial→terminal에는 residual 해소 증거를, terminal→unresolved에는 회귀 사유를 요구한다. scoped N/A는 부재 일반화가 아닌 명시적 배제 증거를 요구한다.

**Validation:** baseline 9,982 key와 reassessment attribution row의 1:1 equality 및 위 귀속 조건을 통합 acceptance의 전수 순회에서 확인한다. baseline에서 `attributed + explicit attribution_failure = 9,982`, missing attribution = 0이어야 하며 failure row도 질문별 조사·사유 검사를 통과해야 한다. definition successor 또는 동일 정의 내 instance 추가가 있으면 successor N개 question에도 동일하게 전수 attribution을 요구한다. mapping만 있고 원래 질문의 attribution/residual 판정이 없으면 실패다. failure 수 감소는 목표가 아니며 changed-question 검사는 전수 attribution을 대체하지 않는다. 추가로 affected-definition-only delta, retained/changed/new scope accounting, lineage 완전성, silent key deletion 0, residual 소거 0, denominator 조작 0, partial/terminal 및 scoped N/A 불변식을 같은 실행에서 검사한다.

#### P4 보충 판정 — 동일 정의 내 누락 참여 인스턴스 복구 (2026-09-08)

[지정 세션](codex://threads/01a07ad6-0377-7d62-9c8d-bc833a049714)의 판정에 따라 `Salt;1`, `[Recipe.GetItemTypes.BakingFat];15` 같은 직접/group 참여 clause의 추출 누락은 실제 definition defect로 입증되지 않는 한 기존 revision 아래 producer에서 복구한다. 역사적 parser/hash는 수정하지 않는다.

- baseline 9,982 key의 attribution·잔여 의무는 전부 유지한다. 새 key는 baseline 부재, exact item/recipe/clause/group, 기존 profile/axis/scope, 이전 누락 이유와 관련 pending/gap을 연결한다. 같은 세 요소 key로 모이는 여러 recipe의 contributor/evidence는 합치고 질문을 중복 생성하지 않는다.
- 단순 token 인식은 참여 조사 admission이다. 세미콜론 수치를 `=` 수치와 동일하게 해석하지 않는다. 원문·수치·group/callback·조건을 보존하고 미확인 소비량·효과·유효성은 구체적 residual로 유지한다. 참여 복구만으로 role/conditions를 resolved로 만들지 않는다.
- 같은 historical parser가 누락한 `Plank = 3`, `TentPeg = 4`처럼 공백을 포함한 `=` operand도 이 참여 복구에 포함한다. 이미 인식된 공백 없는 `=`는 중복 admission하지 않고, 원문 구분자·공백·수치를 유지한다. 기존 통합 acceptance의 동일 인메모리 문법 사례에 함께 포함하며 별도 검사나 gate를 추가하지 않는다.
- 같은 정의의 참여 복구에는 명시적인 module `imports`로 연결되는 무수식 아이템 이름도 포함한다. 현재 모듈의 선언이 없고 명시적 import 대상에서 유일한 선언을 찾은 경우에만 추가하며, 로컬 선언·모호한 선언·충돌한 import 헤더·이미 한정된 이름에는 fallback하지 않는다. 이전 파서의 행과 원문 operand를 보존하고 헤더 관찰을 연결한다. 수량·런타임 선택·결과 전달을 이 admission으로 해결하지 않으며 동일 통합 acceptance의 인메모리 사례를 사용한다.
- 특정 사례 이름만 예외 처리하지 않고 모든 영향 exact 대상의 direct/group token에 같은 규칙을 적용한다. 기존 cooking 사실로 crafting 질문을 대신하지 않는다. instance 추가와 기존 질문의 evidence resolution, definition delta를 별도로 집계한다.
- 동일 정의의 group 참여 복구에는 과거 whole-declaration `unique_properties`가 중복 필드 때문에 버린 선언도 포함한다. 정확한 단일 선언의 안정된 Tags 또는 명시된 short-type group 조건만 사용하고, 과거의 해당 recipe/clause/member 행이 실제로 없는 경우에 추가한다. 같은 값의 반복과 관련 없는 충돌은 원문 그대로 남기며 membership 필드의 충돌이나 다중 선언을 승자 선택으로 해결하지 않는다. `Base.WeldingMask`의 반복된 `BloodLocation = Head`와 안정된 `Tags = WeldingMask`가 확인된 사례다. 기존 profile/axis/scope·historical reader를 유지하고 중복 속성·group·선언 및 이전 누락에 결속한다.
- 기존 통합 acceptance에서 direct/group 세미콜론 사례, 기존 `=` 처리 보존, 미지원 문법 거부, baseline 보존·근거 있는 신규 key·중복 병합을 공유 사례로 확인한다. 새 gate/validator/proof tree는 만들지 않고 미완성 후보의 acceptance 반복을 하지 않는다.

같은 원칙은 route D에 원문 `need:Base.…` 관측이 있으나 historical construction-material 고정 목록 때문에 `world_work`가 열리지 않은 경우에도 적용한다. 실제 활성 메뉴 factory, 생성 클래스의 `buildUtil.consumeMaterial`, exact 재료·수량을 대조한 참여에만 기존 role/conditions instance를 추가한다. 이전 route/pending/gap과 원문 관측을 보존하고 여러 factory는 동일 key에 합친다. 함수 이름이나 비활성 정의만으로 추가하지 않는다. 이 복구는 정의 revision 변경이 아니며 기존 통합 acceptance의 instance lineage 사례를 공유한다.

route D의 기존 `ISBuildMenu` 전용 탐색이 놓친 활성 `ISBlacksmithMenu` 금속 용접 경로도 실제 학습군·메뉴 수치·`need:`/`use:`·장비·생성 소비를 대조해 같은 방식으로 병합한다. 이미 있는 world-work 질문에는 관측과 참여 의무를 강화하고, 없는 질문에만 인스턴스를 추가한다. 비활성 화로·모루·드럼 건축 분기나 물품 이름만으로 용접 역할을 열지 않는다.

#### P4 scope clarification — 일반 인벤토리 관리 (2026-09-08)

같은 지정 세션의 후속 판정에 따라 일반 물품의 hotbar 부착·제거·빠른 꺼내기도 이 관리 제외 범위에 포함한다. 실제 static AttachmentType·slot 매칭 조사와 제외 사유는 기존 audit에 남긴다. AttachmentsProvided로 슬롯을 제공·증가시키는 기능, 특정 물품의 기능·상태·사용 조건을 바꾸는 특수 의미, predecessor의 개별 부착 호환성 주장은 별도로 조사·보존한다. 실제 목적지 보존 없이 relocation을 주장하지 않으며 이 제외만으로 direct 전체를 N/A/resolved로 만들지 않는다. 새 definition revision이나 gate는 추가하지 않는다.

[지정 세션](codex://threads/01a07ad6-0377-7d62-9c8d-bc833a049714)의 판정에 따라 모든 아이템에 공통인 즐겨찾기 표시, 일반 이동/버리기, 단순 손에 들기는 item-specific Layer 3 직접 기능의 필수 fact나 residual로 각각 추가하지 않는다. 기존 게임 UI의 일반 관리 책임과 구분하며 Iris Layer 4에 구현·보존되어 있다고 주장하지 않는다. Predecessor에 해당 의미가 있으면 실제 source에 따른 일반 관리 분류/제거 사유를 남긴다. 손에 들었을 때 특정 기능이 가능하거나 이동·버리기가 특정 상태·내용물·형태를 바꾸는 등 item/property/context별 특수 의미는 별도로 조사·보존한다. 이 구분은 새 definition revision이나 gate가 아니며 direct 전체의 N/A/해결 근거도 아니다.

Predecessor claim/conservation 비교가 끝났어도 question-local attribution을 대신하지 않는다. 각 direct operation/conditions의 답한 범위·미확인 명제·필수 dependency를 별도로 평가한다. 현재 runtime 상태 값이 미확정이라는 이유만으로 설명 가능한 조건부 기능을 막지 않으며, 모든 질문에 같은 predicate/native/extension 목록을 residual로 붙이지 않는다. 비교만 완료되면 그 범위만 기록하고 미수행 질문 재평가 의무는 유지한다.

### Change 5 — P5: Immutable semantic/acquisition successor chain

**Purpose:** 기존 sealed writer/loader를 깨뜨리지 않고 corrected subject를 생성·검증한다.

**Files:** recovery 진입점, successor manifest/corpus, 기존 semantic/acquisition loaders의 읽기 전용 재사용 경계.

**Implementation Notes:**

- 우선 successor 경로에서 source reading/fact validation 등 재사용 가능한 동작을 호출한다. 기존 producer 수정이 필요한 경우 §4에 따라 최소 변경·역사적 subject 보존·실제 consumer 결속을 함께 다룬다. 대규모 복제나 범용 framework 신설은 피한다.
- candidate output은 repository-local empty directory에 한정하고 overwrite를 거부한다. historical hash를 현재 코드에 맞춰 재작성하지 않는다.
- L3-04 결함이 있으면 해당 route의 correction successor를 만든다. 결함이 없으면 기존 acquisition facts/results/source evidence를 보존한다.
- 후자의 경우에도 현재 L3-04 manifest가 이전 semantic readpoint를 결속하므로, 새 combination binding에서 unchanged acquisition subject와 새 semantic subject를 명시한다. 기존 `load()`에 새 semantic을 몰래 주입하지 않는다. 기존 contract가 이 결합을 표현하지 못하면 사실 변경 없는 binding-only successor를 만들고 그 이유를 기록한다.
- binding-only artifact 자체에 `content_delta: none`, `dependency_binding_delta: yes`, predecessor acquisition binding, 이전/새 semantic binding, facts/results/source evidence의 동일성 digest를 기록한다. 내용이 달라지면 binding-only로 분류하지 않는다.
- candidate/adopted lifecycle은 명시적으로 검증한다. adopted 자료를 candidate로 재사용할 때 원래 verified binding을 유지하며 임의 status 변경으로 loader를 우회하지 않는다.
- definition successor가 있으면 definition readpoint/revision을 L3-03/04 result와 fact/condition reference, application/resolver, expression 입력에 명시 결속한다. revision 1 결과를 새 정의의 결과로 묵시 소비하지 않는다. 영향 없는 기록도 의미·scope 호환성 검사 후 재사용한다. hard-coded root를 가진 loader를 속이지 않고 실제 definition을 검증한다. adapter로 호환성을 구현할 수 없으면 §4의 최소 대체 변경을 검토하며, 실제 제약과 구현 미완료를 구별한다.
- L3-05는 §4에 따라 선택한 경로를 사용한다. 우선 candidate adapter가 관계를 검증하고 재사용 합성 body를 실제 input/review/rule hash와 동적 denominator를 가진 successor envelope로 감싼다. 대체 구현도 같은 사실·조건·입력 결속을 충족해야 한다. 고정된 predecessor metadata를 가진 중간값을 저장·배포하지 않는다. body의 재생성 비교는 통합 acceptance의 결정성 검사와 공유하고, 실제 loader는 필요한 입력/member/관계 검증을 수행한다. 기존 `validate_payload()`의 고정 envelope 비교를 우회 수단으로 사용하지 않는다.
- 선택한 경계가 실제 installed package에서 동작하고 역사적 입력 및 successor module binding이 맞는지 통합 acceptance에서 확인한다. 지원 domain의 재사용 parity와 새 branch의 독립적인 기대 사실/qualifier 집합을 같은 candidate로 검사한다. 별도 P5 Gate 또는 P7 진입용 중복 실행을 만들지 않는다.

**Validation:** 새 chain의 독립 load, member/source hash closure, cross-authority fact collision 거부, qualified reference 일치, stale/mixed subject 거부, protected historical bytes 불변.

### Change 6 — P6: Combined application과 잔여 상태 재계산

**Purpose:** 추가 사실과 admitted definition correction의 영향을 명시적으로 결속된 정의에서 계산한다.

**Files:** `investigation.resolve_item()` 읽기 전용 재사용, successor combination consumer, application/residual report.

**Implementation Notes:**

- L3-02 revision 1 또는 admission을 통과한 successor definition + successor L3-03 + unchanged/revised L3-04의 exact binding으로 2,105 application을 계산한다. `resolve_item()`의 explicit contract 입력을 우선 재사용하고, 현재 경로를 직접 읽는 상위 loader와 분리한다.
- required axis result, partial contribution, acquisition state, item completion, pending/gap, first-contact obligation/contributor를 함께 재파생한다.
- `scope_determined AND every_required_axis_terminal AND acquisition_state == resolved`를 보존한다. 설명 존재나 획득 resolved 하나로 item complete를 만들지 않는다.
- 정의 변경으로 옮긴 잔여 의무도 pending/gap/required-axis 표현에 결속해 item complete를 막을 수 있어야 한다. audit에만 잔여를 숨기거나 정의 축소만으로 item을 complete 처리하지 않는다. 기존 모델/adapter로 표현할 수 없으면 §4에 따라 최소 successor 변경을 검토한다. 잔여 의무 보존이 구현되지 않은 subject는 A3 미충족이다.
- 수정된 input마다 full application을 다시 계산한다. 증분 handoff도 동일 full universe를 기준으로 한다.

**Validation:** result/fact/contributor 무결성, unresolved/pending 재현성, acquisition과 item completion의 분리, unsupported first-contact 의무 보존.

### Change 7 — P7: KO/EN expanded·compact 재생성과 의미 보존 accounting

**Purpose:** 복구한 사실이 표현에서 다시 빠지지 않도록 추적한다.

**Files:** successor expression producer/manifest/descriptions/review, 기존 expression rules·projection 참조, conservation report.

**Implementation Notes:**

- revised qualified fact set과 application에서 KO/EN expanded를 생성한다. context·condition·acquisition reference를 보존하고 locale 간 같은 사실 집합을 표현한다.
- compact는 accepted first-contact contributor와 첫 이해의 범위를 바꾸는 qualifier에서 생성한다. expanded 자르기, 대표 fact 선택, predecessor fallback을 사용하지 않는다.
- claim→disposition→fact→expanded→compact(if applicable)를 연결한다. 정상 상세 생략, first-contact 비대상, upstream unresolved, 표현 실패를 구별한다.
- claim별 최종 conservation row는 migration disposition, successor fact outcome/refs, KO·EN expanded outcome/refs, KO·EN compact outcome/omission reason, residual과 `conservation_status`를 합성한다. preserved/recovered/corrected claim은 살아 있는 fact와 양 locale expanded 표현이 있어야 `conserved`다. compact 비대상/정상 상세 생략은 독립 reason과 fact refs가 있을 때만 허용한다. relocated/removed는 근거·확인된 목적지 또는 제거 사유로, unresolved는 bounded 조사 잔여로 종결한다. fact만 recovered인데 expression이 없으면 `expression_failure`이며 A5 실패다.
- 기존 6,402 unmet obligation과 blank 수는 비교 지표다. revised input에서 다시 계산하고 baseline 수를 합격 상수로 유지하지 않는다.
- 표현 rule/review domain도 revised payload에 결속한다. accepted fact에 지원 표현이 없으면 **해당 exact expression candidate 전체의 P7 validation failure**로 처리한다. artifact에 실패 fact/locale/rule을 진단 기록할 수 있으나 `completion=complete`, adoption, 소비용 handoff는 금지한다. 해당 fact를 accepted set에서 빼거나 upstream unresolved/normal omission으로 재분류하지 않는다.
- 지원 표현이 아직 미구현인 경우 A closeout은 `partial`이다. 우선 경로의 한계는 §4의 최소 변경으로 해결하고 실제 계약·필수 input/tooling 제약이 있을 때 `blocked`로 기록한다. 수정된 candidate를 통합 검증한 뒤에만 A5를 다시 판정한다. KO/EN parity 실패를 한 locale 억제·양쪽 문장 삭제로 숫자만 맞춰 해소하지 않는다.

**Validation:** fact-locale binding completeness, KO/EN semantic parity, expanded fact/dependency coverage, compact omission 근거, acquisition 표현 무결성, 동일 입력의 byte/semantic determinism과 claim별 최종 conservation relation을 검사한다. unsupported-expression/locale 누락은 candidate failure이며 부분 소비 허용으로 완화하지 않는다.

### Change 8 — P8: Adoption·B/C handoff·closeout

**Purpose:** 검증한 exact recovery subject와 주장 한계를 후속 작업에 전달한다.

**Files:** successor adoption record/readpoint, final audit, closeout, 필요한 공통 문서의 additive 기록.

**Implementation Notes:**

- candidate chain 전체에 대해 exact command/exit, subject SHA, input/member bindings를 고정하고 채택 후 같은 subject를 readback한다. 검증 실패 시 route를 변경하지 않는다.
- 기존 product가 암묵적으로 새 expression을 읽지 않도록 readpoint 구독자를 확인한다. semantic→acquisition→expression 중간 상태를 외부에 current로 노출하지 않는다.
- 기존 route/index/receipt mechanism이 지원하는 최소 전환을 우선 사용한다. 별도 transaction/governance framework는 만들지 않는다. 기존 방식으로 coherent 전환을 보장할 수 없으면 최소 보완을 검토한다. coherent 전환이 미구현인 동안 소비용 채택은 보류하고, 실제 제약에 따른 blocked와 구현 미완료 partial을 구별한다.
- B에는 compact S2, represented fact/dependency refs, expression identity, upstream gaps를 전달한다. C에는 expanded KO/EN, context/condition/acquisition refs, dispositions, residual을 전달한다.
- 두 작업이 같은 exact expression subject를 식별하게 한다. 증분 handoff는 포함한 correction과 남은 queue를 명시하며 A 전체 완료로 표시하지 않는다.
- 증분 허용은 그 exact subject 자체가 P5~P7 전수 검증에 통과한 경우에만 적용한다. expression producer 경로 부재·unsupported accepted fact·locale parity failure·bound-member drift가 있는 subject에는 적용하지 않는다. 실패 subject의 source/audit 공유와 B/C가 소비 가능한 expression handoff를 구분한다.
- 실제 replacement product integrated input evidence는 후속 B/C의 보존 주장 조건으로 전달한다. historical L3-06 complete는 유지한다.

**Validation:** exact adopted readback, coherent dependency chain, B/C identity 일치, historical trace 보존, closeout의 결과와 claim ceiling 일치.

## 7. Validation Plan

### Automated Validation

이번 요청은 문서 작성이므로 아래는 후속 구현 시 실행할 계획이다. 현재 실행 성공을 뜻하지 않는다.

**검증 최소화 원칙:** 이번 A가 새로 추가하는 acceptance Gate는 하나다. 단일 focused test source·단일 명시 명령으로 실제 full candidate를 만들고, 질문/사실/표현의 전체 연결과 오류 거부를 함께 검사한다. P1~P8의 `Validation`은 이 통합 검증의 확인 항목 또는 정상 producer/loader의 입력 수용 검사이며 별도 Gate·validator·receipt를 뜻하지 않는다. exact input/member 결속, 전수 의미 accounting, 질문별 판정, 실제 표현 결과의 필수 범위는 축소하지 않는다.

- pytest test 함수·fixture·subtest 개수는 고정하지 않는다. 한 함수로 억지 합치거나 항목마다 별도 검사 파일을 만들지 않고, 결과를 설명할 수 있는 최소 구조를 구현자가 선택한다.
- 정상 생성의 assertion과 loader 검증을 재사용하고 같은 조건의 별도 검사기를 만들지 않는다. 입력 파싱·후보 생성·전수 순회를 가능한 한 공유한다. 결정성은 필요한 한 쌍의 생성 비교를 같은 실행 안에서 수행하며 단계별로 반복하지 않는다.
- 아래 오류 목록은 보장해야 할 거부 동작이다. 각 항목에 별도 fixture/Gate를 요구하지 않는다. 같은 실패 원인을 검증하는 사례는 묶거나 매개변수화한다. 단, 다른 의미 오류를 막는 독립적인 근거가 없는 경우 이름만 묶어 생략하지 않는다.
- 의미 검토는 생산 규칙 검토와 전수 적용/차이 검토에 통합한다. 별도 수동 승인 Gate나 검토 전용 증거 체계를 만들지 않는다. 채택 후 readback은 실제 채택 작업의 좁은 결과 확인으로 수행하며 전체 suite를 다시 돌리지 않는다.
- 초기 실패, 입력·구현·규칙 변경 또는 새 결함으로 재검증이 필요한 경우에만 다시 실행한다. 동일 subject가 통과한 뒤 confidence 목적의 재실행·단계별 중복 검증·성공을 재증명하는 검증은 추가하지 않는다.
- 기존 계약이 실제 변경에 요구하는 검증은 유지한다. 추가 실행이 필요하면 적용 조건·현재 변경과의 관계·기존 통합 검증으로 충족할 수 없는 부분을 구체적으로 기록한다. 과거 명령 목록이나 Heavy 분류만으로 Gate 수를 늘리지 않는다.

- 기존 focused tests `test_layer3_semantic_results.py`, `test_layer3_acquisition_results.py`, `test_layer3_expression_results.py`, `test_layer3_investigation_contract.py`는 계약과 반례 설계의 참조다. sealed test의 기대 수치를 바꾸거나 기존 PASS를 successor에 승계하지 않는다.
- 신규 focused source 하나에서 baseline identity, 독립 clause coverage, 전수 accounting/key set 및 **상태 변화와 독립된 baseline 9,982 attribution rows와 successor N rows**, source/fact/reference, representative/counterexample, combined completion, locale parity, claim별 최종 conservation, determinism, protected surface를 검증한다. 정의 수정과 누락 인스턴스 추가가 모두 없으면 N=9,982다. 의미 검토 기록을 검사하는 테스트가 source 전수 의미 정확성을 대신하지는 않는다.
- admitted definition correction에는 영향 범위 밖 delta, lineage 없는 key 삭제, residual 소거, revision 1 결과의 새 정의 묵시 재사용, 분모 변경을 evidence resolution으로 집계하는 negative fixture를 추가한다. definition→result→application→expression exact binding과 잔여 의무의 completion 차단을 검사한다.
- negative cases: case-normalized join, stale member, 누락 source, duplicate key, missing disposition, 미분해 prose clause, **근거 없는 비의미 clause 분류**, clause classification rule 누락·generic reason, prose-only fact, **missing question attribution**, 질문 근거 없는 route blocker 일괄 복사, 근거 없는 generic attribution failure, residual이 남은 terminal, broken correction reference, mixed candidate/adopted, expression fact 누락, 한 locale 억제, predecessor INPUTS가 남은 successor envelope, current pointer 변경을 거부한다. 특히 상태가 계속 unresolved인 fixture에서 attribution만 누락/변조해도 실패해야 한다. Clause fixture도 원래 기능/조건을 담은 span을 비의미 연결 표현으로 바꿔 미분해 수만 0으로 만드는 변조를 거부해야 한다.
- 선택한 expression 재사용/대체 경로의 검사는 기존 지원 의미의 보존, 새 payload의 qualifier/context 연결, 실제 module/input envelope 결속을 통합 확인한다. Import-time 데이터 의존 반례는 그 위험이 있는 실제 경로에 한정하며 별도 도구를 만들지 않는다. 기존 함수와의 equality만으로 새 branch의 의미 정확성을 증명하지 않는다.
- tooling은 설치된 패키지를 사용한다. 기존 expression gate가 요구하는 isolated Python과 bytecode 비생성을 유지하며 `PYTHONPATH` source-root 우회는 사용하지 않는다.

**등록 모델:** 기존 L3-05 `test_layer3_expression_results.py`의 독립 off-live acceptance 선례를 따른다. 해당 파일은 스스로 정규 registry entry가 아니라고 명시하며 `--noconftest`/tooling config로 실행한다. Recovery도 단일 focused test identity를 successor manifest/receipt에 결속하고 `Iris/validation/execution/`의 정규 registry에는 추가하지 않는다. B/C에는 이 gate가 자동 정규 회귀 실행 대상이 아님을 전달한다. 소비자는 exact input binding을 검증하며 recovery producer/input/rule 변경 시 이 focused gate를 명시 재실행한다. 기존 정규 검증의 보호 범위가 자동 확장되었다고 주장하지 않는다.

이 선택은 L3-05의 예외를 chain 전체에 자동 상속한 것이 아니다. L3-02의 required test 등록, L3-03의 required identity/current-route 연결, L3-04의 execution registry/source policy 등록 선례를 함께 검토했으며, 정의·semantic·acquisition successor에는 predecessor보다 자동 회귀 실행 범위가 얇아지는 tradeoff가 있다. 이번 A에서는 2026-08-31 작업별 조건부 검증 결정에 따라 전 chain을 결속한 독립 focused acceptance를 선택하고, 신규 정규 entry는 만들지 않되 기존 등록/검사를 제거하지 않는다. 해당 focused gate를 생산자·definition/input·rule 변경 시 명시 재실행하고, P8 closeout에는 surface별 predecessor 등록 여부, successor의 미등록 결정, 자동 실행되지 않는 보호 범위 및 재실행 책임을 기록한다. 기존 정규 gate나 채택 계약이 실제 successor에 요구하는 조건이 발견되면 이를 이 문장의 예외로 우회하지 않고 채택 전 계획과 필요한 등록 범위를 정정한다.

후속 focused source 구현 및 installed package identity 확인 후, 저장소 루트 PowerShell에서 사용할 검증 명령은 다음과 같다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_recovery.py -q
```

새 source는 기존 default `testpaths` 바깥에 있으므로 명시 경로로 실행한다. candidate fixture가 환경변수·인자를 요구하게 되면 실제 명령을 closeout에 빠짐없이 기록한다. 구현된 패키지와 installed bytes의 일치를 먼저 확인한다. 정확한 명령이 exit `0`일 때만 PASS이며, uv/Python/pytest/필수 원본 또는 bound member 부재는 BLOCKED다.

A는 Lua를 수정하지 않는다. 승인된 후속 범위가 Lua 변경을 포함하게 되면 별도로 저장소 루트에서 `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`을 실행하고 exit `0`을 요구한다. Java/JS 변경이 없는 이 문서·Python 계획에 Gradle/Biome 성공을 근거로 끌어오지 않는다.

### Manual Validation

아래 의미 검토는 생산·통합 검증에 포함하며 별도 Gate가 아니다.

- 모든 migration claim의 disposition과 근거 또는 조사 후 uncertainty를 확인한다. 수작업/규칙 기반 검토의 구분과 적용 domain을 기록한다.
- changed question, partial→terminal, terminal→unresolved, N/A 변화, 새 source interpretation은 전부 근거를 검토한다. unchanged 영역도 모든 row의 attribution rule 적용·evidence/residual 결속을 검사한다. 공유 rule의 내용 검토와 개별 row의 적용 검사를 구분하며, representative 표본이나 상태 equality로 전수 attribution 검사를 대체하지 않는다.
- 노트류 원본의 열람/편집/lock/page 조건, 비공백 설명 내부 의미 손실, 획득 qualifier, KO/EN 설명 의미를 대조한다.
- B/C handoff 파일을 읽어 동일 expression hash와 residual 목록을 가리키는지 확인한다.

### Validation Limits

- 이번 문서 작성에서는 recovery 코드를 구현하거나 위 테스트를 실행하지 않는다.
- 후속 A 검증도 PZ UI/Alt 동작, multiplayer, 장시간 실행, package/install, Workshop, 외부 모드 호환 전수를 검증하지 않는다.
- 기존 문서 삭제·hash drift가 해결되지 않으면 adopted chain 검증 가능성을 주장하지 않는다. 이를 recovery 판정 결함과 별개로 보고한다.
- integrated replacement product를 검사하지 않은 상태에서 predecessor information의 제품상 완전 보존을 주장하지 않는다.

## 8. Risk Surface Touch

### Authority Surface

High. L3-03/필요 시 L3-04/L3-05 successor와 채택 readpoint, evidence admission을 통과한 bounded L3-02 successor definition이 대상이다. L3-01 및 historical L3-02 revision 1은 불변이며 ledger는 audit 관계만 소유한다.

정의 successor의 profile taxonomy·first-contact axis 및 definition writer responsibility는 **DVF-L3-02 authority lineage에 그대로 남는다**. DVF-RECOVERY-A는 그 lineage 안에서 admitted correction을 수행하는 실행 주체이며 별도 owner/co-writer가 되지 않는다. 소유권 이전은 없고, successor 구현 진입점이 달라져도 독립적인 정의 작성 권한을 만들지 않는다. [EXECUTION_CONTRACT.md §5-1](EXECUTION_CONTRACT.md#5-1-touched-authority-surfaces)에 따라 closeout에는 실제 구현 후 ownership/writer responsibility 변경 유무와 이 경계의 보존 여부를 명시한다.

### Runtime Behavior Surface

직접 변경 없음. Lua와 current generation pointer는 보호 대상이다. 새 expression readpoint를 기존 product가 자동 소비하는지 검사해야 한다.

### Compatibility Surface

Exact FullType, typed fact semantics, question identity와 partial/terminal 의미를 유지한다. 새 fact ID 및 authority-qualified refs의 downstream 재결속은 영향이 있다.

### Sealed Artifact Surface

Historical subject의 manifest와 당시 code/doc/test bytes·검증 기록은 보존한다. 현재 working tree 누락을 과거 hash 재작성으로 해결하지 않는다. 우선 additive successor를 사용하되, 현재 구현의 최소 변경이 필요하면 §4에 따라 역사 보존·호환성·새 subject 결속을 함께 처리한다. 특정 adapter 실패 자체를 blocked 사유로 삼지 않는다.

### Public-Facing Output Surface

Offline KO/EN expanded·compact 의미가 달라진다. 사용자에게 실제 보이는 제품 변경과 검증은 B/C 통합 범위다.

## 9. Risk Analysis

### Architecture Risk

- audit ledger가 두 번째 semantic owner가 될 위험: truth는 기존 L3-03/04, 표현은 L3-05에 둔다.
- immutable code 결속 때문에 복구 모듈이 기존 시스템 전체를 복제할 위험: pure reader/model/resolver 재사용을 우선하되 최소 기존 구현 변경이 더 작고 타당하면 §4에 따라 선택한다.
- binding-only acquisition successor를 실제 획득 사실 정정으로 오해할 위험: content delta와 dependency binding delta를 분리해 보고한다.

### Runtime Risk

- readpoint 채택이 product를 조기 전환할 위험: 소비자 조사, current pointer 보호 및 candidate/adopted 경계 검사를 채택 조건으로 둔다.
- recovered fact를 Tooltip filler로 쓰는 위험: first-contact contributor 규칙과 B의 슬롯 소유권을 유지한다.

### Compatibility Risk

- case folding·이름 추론·선언 승자 추정으로 다른 item의 근거를 합칠 위험: exact source identity와 duplicate/absence 반례를 유지한다.
- source snapshot 차이를 기존 claim 오류로 오해할 위험: 빌드/소스 identity와 uncertainty를 분리한다.

### Regression Risk

- partial 사실을 whole question으로 과대 승격할 위험: answered/remaining scope와 terminal 증거를 검사한다.
- 남아 있는 문장 속 조건·획득 의미 누락: 전수 claim accounting과 locale expression 연결로 검사한다.
- 기존 테스트 성공의 오용: successor exact subject의 새 실행만 인정하고 historical PASS는 역사로 남긴다.

## 10. Rollback Plan

- 검증 전 실패한 candidate는 채택하지 않는다. 실패 원인과 subject hash를 기록하고 다음 candidate는 새 경로에 생성한다.
- semantic/acquisition/expression 중 하나라도 실패하면 해당 chain adoption을 중단한다. 획득 내용에 결함이 없다면 기존 L3-04 사실을 유지한다.
- 채택 도중 readback이 실패하면 이전 verified route/receipt 상태로 복귀한다. current 제품 파일은 변경하지 않았음을 확인한다.
- 채택 후 의미 결함은 새 correction successor로 처리한다. 기존 corpus/manifest/closeout을 역수정하지 않는다.
- P1에 기록한 사용자 working-tree 변경과 문서 삭제 상태를 보존한다. rollback을 이유로 `git reset`이나 일괄 checkout/삭제를 수행하지 않는다.

## 11. Governance Constraints

- Philosophy의 근거 기반 중립 정보, 100% Lua runtime, Menu/Tooltip 두 표면, Alt·최대 4줄, 게임 상태 비변경을 유지한다. Python은 offline tooling이다.
- Hub & Spoke와 SPI 경계를 유지하며 Pulse가 Iris 또는 다른 spoke에 의존하게 하지 않는다.
- L3-01 다중 의미·context-local role·fact-local qualifier, L3-02 question identity의 형식과 completion 원칙, L3-04 acquisition ownership, L3-05 표현 책임을 유지한다.
- L3-02 정의 정정은 사용자 지정 세션의 Option A 판정과 §4 admission을 따른다. 기존 identity 형식·완료 원칙은 유지하고 변경된 scope는 lineage와 residual 의무로 보존한다. 과거 manifest hash/PASS를 successor에 승계하지 않는다.
- Recipe/우클릭은 독립·동등한 정보 관점이다. 상세 관계를 Layer 3로 흡수하지 않는다.
- baseline source identity와 sealed history를 보존하며 current authority ownership을 우회하지 않는다.
- 로드맵의 미결정 사항은 §4의 계획 제안으로 명시했다. 본 문서 작성이 authority 채택·제품 전환 권한이나 실행 완료를 뜻하지 않는다.
- 변경은 문제 A와 직접 관련된 최소 범위로 한정한다. 새 정규 validator·framework·taxonomy를 요구하지 않는다.
- private composition helper의 재사용은 exact module hash와 interface에 의도적으로 결속된다. 해당 L3-05 상류 모듈이 바뀌면 recovery successor의 focused gate 재실행과 exact subject 재검증이 필요하며, 이 재검증 조건을 closeout에 남긴다. `recovery_expression.py`는 successor correction 구현이며 장기 병렬 expression authority를 만들지 않는다.

## 12. Expected Closeout State

목표 상태는 **`complete` — offline recovery successor 및 handoff 범위**다. 다음 증거가 모두 있을 때만 성립한다.

| 기준 | 필수 closeout 증거 |
|---|---|
| A1 Migration accounting completeness | exact 2,105 item과 모든 predecessor claim 관측, 원본 KO/EN clause의 독립 coverage 및 미분해 0, 비공백 내부 delta, disposition 없는 claim 0 |
| A2 Evidence-bound migration | recovered/corrected meaning의 source→typed fact→result→expression chain과 qualifier/reference integrity. 현재 자료로 진행 가능한 것으로 확인된 A 범위의 복구·판정·표현 작업이 미수행으로 남아 있지 않음 |
| A3 Question-local adjudication | 기준 9,982 key 전수 reassessment attribution 및 successor N question 전수 attribution, 양 집합 각각 누락 0·근거 없는 route-copy 0. 정의 수정과 인스턴스 추가가 모두 없으면 N=9,982/key equality. 동일 정의 내 추출 누락 복구는 baseline 보존·source-bound 신규 key·contributor 병합·instance delta를 요구한다. 정의 수정은 admitted affected-definition-only delta·전수 lineage·분모 증감 설명·residual 보존·exact definition chain을 요구한다. 별도로 변경 질문별 evidence/reason/residual, 12문항 representative 및 실제 결함 반례, partial/whole-scope 구분 |
| A4 Residual disclosure | preserved/recovered/corrected/relocated·removed/unresolved 판정과 조사 범위·uncertainty. 미판정 silent loss 없음 |
| A5 Expression successor | §4의 재사용 또는 최소 대체 구현으로 생성·검증한 revised facts의 KO/EN expanded·compact, unsupported-expression/locale 누락 0, first-contact/omission/gap 재계산, claim별 disposition→fact→양 locale expression 최종 conservation relation 및 동일 B/C subject. 실제 blocked 또는 P7 실패 시 미충족 |
| A6 Historical trace | L3-01~06 역사와 protected members 보존, additive successor readback 및 새 검증 기록 |
| A7 Count-independent completion | 수치 변화로 A1~A6을 대체하지 않으며 실제 residual과 validation ceiling 공개 |

근거가 부족한 claim이나 question attribution이 질문별 조사 후 unresolved/failure로 남는 것은 허용한다. 그러나 **현재 자료로 진행 가능한 것으로 확인된 A 범위의 의미 복구·질문 판정·표현 작업을 미수행으로 남긴 채 complete를 선언하지 않는다.** 조사 범위를 임의로 작게 잡거나, 아직 읽지 않은 확인 가능한 consumer·조건을 조사 한계로 바꾸어서는 안 된다. 실제 원본/엔진 근거 부재·해석 불확실성과 해석/구현 미완료를 구별한다. 전자는 구체적 근거와 잔여 범위를 남길 수 있고, 후자는 A2/A3/A5 중 해당 기준 미충족이다. 부족 자료를 무제한 탐색하거나 모든 미해결을 0으로 만들 의무는 없다.

Closeout 첫 결과는 실제로 복구한 의미와 아이템, 정정·제거한 의미와 이유, 여전히 표현되지 않는 기존 의미 및 그 이유다. 기존/신규 공백 전환과 비공백 내부 손실도 함께 제시한다. 미해결 사유는 실제 근거 한계와 미수행 해석/구현으로 구별한다. 이미 있는 conservation/accounting 결과로 이 내용을 보고하며 별도 보고서 형식·Gate를 신설하지 않는다. 9,982개 row를 채웠거나 manifest chain을 연결했다는 사실은 이 결과를 대체하지 않는다.

| 미완료 원인 | A closeout | phase/완료·handoff 제한 |
|---|---|---|
| 관측·분해·판정·의미 이관·표현 구현 미완료, admitted definition correction 미구현 또는 최소 정의 수정이 A 범위를 벗어남 | `partial` | 해당 A1~A5 미충족과 남은 실제 작업을 기록한다. 사용 가능한 근거의 미검토·허용된 구현의 미완성을 evidence-limited unresolved로 종결하지 않는다. 범위 밖은 별도 제안한다. |
| 허용된 입력 확보 후에도 P1 필수 baseline/member/source/tooling을 확보하지 못함 | `blocked` | 입력 수용 조건 미충족. identity 미확정 delta/보존 주장 금지, verified chain adoption 불가. 독립 조사와 구현 검토는 가능한 범위에서 계속한다. |
| 최소 대체 구현 검토 후에도 실제 계약·권한·필수 자료 제약으로 expression/definition·residual 결속·coherent adoption 진행 불가 | `blocked` | 구체적 제약과 검토한 최소 경로를 기록한다. 선호 구현 방식 실패만으로 적용하지 않는다. 해당 A3/A5/A6 또는 P8 미충족, 소비용 B/C handoff 없음. |
| 허용된 경로 안에서 unsupported-expression rule 미완성·parity/conservation 실패 | `partial` | exact P7 candidate 실패, A5 미충족. accepted fact 누락이나 일부 locale 억제로 통과 금지. 소비용 adoption/handoff 없음. |
| 구현은 끝났고 알려진 실패 없이 exact validation/adoption 실행만 남음 | `implemented_only` | PASS/adopted/complete를 주장하지 않는다. |

필수 입력/경로 blocker와 부분 성과가 함께 있으면 전체 상태는 `blocked`를 우선 기록하고, 완료한 조사 산출물은 별도 목록으로 남긴다.

어느 상태에서도 “모든 기존 문장이 정확하고 유지됨”, “2,105개 전부 설명 보유”, “모든 unresolved 해결”, “item 전부 조사 완료”, “실제 replacement product 정보 보존”, “PZ 검증 완료”, “B/C 또는 release 완료”를 이 계획의 결과로 주장하지 않는다.
