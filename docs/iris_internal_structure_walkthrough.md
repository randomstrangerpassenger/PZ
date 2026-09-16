# Iris 내부 구조 Walkthrough

> 작성일: 2026-09-16  
> 상태: 이번 세션의 리팩토링 구현·관련 자동 검사·사용자 인게임 확인 완료  
> 구현 계획: [Iris refactoring implementation plan](iris_refactoring_implementation_plan.md)

## 1. 결과 요약

이번 작업은 Iris의 설명 생성, Recovery, 공통 처리, repository runner와 Menu Lua 코드를 책임별로 나누는 작업이다. 기존 진입점과 소비 계약을 유지하면서 내부 구현을 분리했다. 마지막에는 저장소 Iris 폴더를 실행한 사용자가 3계층 설명 누락을 발견했고, 조회 분기를 수정한 뒤 **사용자가 인게임 검증 통과를 확인했다.**

최종 상태는 다음과 같다.

- 설명·Recovery·naturalization·runner·Menu Lua의 내부 책임 분리를 완료했다.
- B에서 Menu로 명시적 후보 입력을 전달하고, 검사 checkout에도 필요한 입력을 제공한다.
- 실패했던 자동 검사 3건을 수정한 뒤 해당 세 노드를 재실행하여 모두 통과했다.
- 저장소 실행의 설명 누락을 수정했고, 관련 자동 검사와 사용자 인게임 확인을 완료했다.
- 제품 accepted/current 입력 전환과 공개 배포는 수행하지 않았다.

사용자의 인게임 확인 대상은 **저장소의 Iris 폴더**다. 별도로 생성한 후보 ZIP의 인게임 검증이나 설명 corpus 전체의 의미 품질 수락을 뜻하지 않는다.

## 2. Offline 처리 구조

### 설명 조립과 Recovery

설명 조립의 순서와 orchestration은 유지하고, crafting/cooking/media/medical/supplies별 frame 처리와 assembly state를 분리했다. Lexicon은 source 조사 producer를 직접 호출하는 대신 vocabulary와 phrase view를 소비한다.

Recovery는 vocabulary, phrase views, source index, crafting roles, claims, direct/activity question review를 나누었다. 기존 orchestrator는 이 구성 요소를 연결하며 사실·판정·표현의 소유권을 유지한다. 분리된 파일은 해당 producer 입력 목록에도 반영했다.

### 공통 처리와 naturalization

| 구성 요소 | 최종 책임 |
| --- | --- |
| `iris_tooling/common/serialization.py` | 같은 계약을 사용하는 JSON serialization 등 공통 처리 |
| `iris_tooling/common/repository_context.py` | 명시적 repository context 관리 |
| 기존 build context | 공통 context의 동일 상태를 재수출하는 호환 경로 |
| `domains/public_text/composition` | Naturalization의 composition·profile·render·compiler identity 구현 |
| 기존 naturalization build 모듈 | 기존 호출 경로를 유지하는 adapter |

Lua 문자열 escaping이나 파일 쓰기는 계약이 다른 구현까지 합치지 않았다. 특히 짧은 atomic write는 부모 디렉터리 처리, 오류 메시지, journal/lock 책임이 달라 공통화하지 않았다. CLI는 고정된 lazy registry를 사용하며 PZ 실행에 필요한 인자가 없으면 대화형 입력 대기 대신 즉시 실패하도록 정리했다.

## 3. B→Menu 후보 입력과 검사 실행 구조

명시적 description/blocks 참조를 B의 직접·중첩 supply와 Menu producer 및 installer까지 전달한다. 같은 실행에서 만든 B ZIP과 owner를 Menu가 소비하도록 연결했다. 기존 accepted 기본값과 current/live 입력 거부 조건은 유지한다.

Repository runner는 다음 역할로 나누었다.

| 모듈 | 책임 |
| --- | --- |
| `repository_contracts` | 실행 계약 읽기와 해석 |
| `source_analysis/repository_sources` | 실행 소스 분류와 분석 |
| `checkout_workspace` | 검사 checkout 준비 및 선언된 입력 제공 |
| `process_results` | 프로세스 실행과 결과 처리 |
| 기존 `run_repository_tests` | 기존 진입점과 호환 호출 경로 |

Full gate의 checkout에서 필요한 B ZIP이 누락되던 문제도 보완했다. Bootstrap에 선언한 Menu 입력을 준비하고, 명시적 후보 corpus와 B owner를 같은 checkout으로 전달한다.

조합·설명·purpose·Recovery·rule-generalization의 5개 테스트 소스는 기존 전용 producer 검사 경로로 등록했다. Prose review의 before 테스트 사본은 반복 실행 의무가 없는 evidence-only로 분류했다. Active validator가 계속 요구하는 Tooltip 정책 문서는 복원했다.

## 4. Menu Lua의 책임 분리

| 파일 | 역할 |
| --- | --- |
| `IrisLayer3DataLookup.lua` | Product와 legacy 조회 factory 선택 |
| `IrisLayer3ProductLookup.lua` | Product의 세션 snapshot과 조회 |
| `IrisLayer3LegacyLookup.lua` | 기존 generation 조회, cache와 diagnostics |
| `IrisDetailChildren.lua` | Browser Detail의 child 수집·제거·위치·scroll 처리 |
| `IrisBrowserDetail.lua` | Detail 화면 구성과 child helper 호출 |
| `IrisWikiSections.lua` | Wiki 표시 및 공통 identity-field 조립 |

새 Lua 모듈은 producer/package 목록에 포함했다. 기존 facade와 cache 수명을 유지하며 runtime은 계속 Lua로 구성된다.

### 인게임에서 발견한 설명 누락과 수정

사용자는 후보 ZIP이 아닌 저장소 Iris 폴더로 실행했을 때 3계층 설명이 사라졌다고 보고했다. 저장소는 legacy generation pointer를 사용하고 optional `IrisLayer3ProductCurrent` 파일은 없는 상태였다.

기존 분기는 optional require의 보호 호출이 성공하면 product가 존재한다고 판단했다. 로더가 없는 모듈에 오류 대신 `nil`을 반환하는 경우에도 호출 성공으로 처리되어, 유효한 legacy 설명을 product 오류 경로로 잘못 보낼 수 있었다.

수정 후에는 **호출 성공 여부와 실제 반환값을 함께 확인**한다. 반환값이 `nil`이면 product 존재로 취급하지 않고 legacy 조회를 유지한다. 실제 product가 있는 경우의 기존 거부 조건은 유지한다.

기존 `lazy_lookup_acceptance_harness.lua`에 optional 모듈이 `nil`을 반환하는 조건을 반영했다. 관련 검사 통과 후 사용자가 인게임 검증 통과를 확인하여 설명 누락 대응을 완료했다.

## 5. 유지 및 보관 결정

- **테스트 위치 유지:** 기존 tooling/validation/Lua 테스트 위치와 unittest ID를 유지했다. 추가 relocation이나 framework 변환은 하지 않았다.
- **역사 실행자 보관:** 독립적인 current 반복 실행 의무가 없는 registry closure 본체와 run/validate 진입점 3개를 `Iris/_archive/registry.zip`에 보관했다. Current fixture materializer와 역사 기록은 유지했다.
- **공통화 no-op:** 계약이 다른 짧은 atomic write는 기존 구현을 유지했다.
- **r1–r5 no-op:** Untracked 로컬 자료에 새 archive 생성이나 삭제를 적용하지 않았다.

## 6. 검증 결과

아래는 기존 실행 기록의 요약이다. 서로 겹치는 실행이 있으므로 수치를 합산한 총 테스트 수를 만들지 않는다.

| 검사 범위 | 기록된 결과 |
| --- | --- |
| 최종 설명 및 CLI/context/serialization 묶음 | 32 passed, exit 0 |
| Recovery 계약 | Before 1 passed, After 1 passed, 각각 exit 0 |
| Naturalization | 양쪽 32 passed 및 15 subtests, exit 0 |
| Runner 전용 검사 | 48 passed, exit 0 |
| 정책 복원 후 B→Menu 및 CLI 묶음 | 3 passed, exit 0; Lua syntax 396개 파일, Browser/Wiki 4,210 states 및 runtime·stage/ZIP·lock/interrupt/recovery 포함 |
| Archive 검사 | 8 passed, 1 skipped, exit 0; Windows symlink 생성 불가로 skip |
| 마지막 canonical 전체 실행 | 215 passed / 3 failed, exit 1 |
| 위 실패 3개 노드의 수정 후 재실행 | **3 passed, exit 0, 61.89초** |
| 설명 누락 수정의 기존 Layer3 조회 검사 | **1 passed, exit 0, 0.32초** |
| 설명 누락 수정의 Lua 문법 검사 | **변경 파일 2개 OK, exit 0** |
| 실제 PZ | **저장소 Iris 실행에 대해 사용자 PASS 확인** |

### 마지막 전체 실행의 실패 3건

| 실패 | 원인과 수정 |
| --- | --- |
| Package support 목록 | 새 ProductLookup/LegacyLookup 모듈 2개가 테스트 기대 목록에 빠져 있어 추가했다. |
| Menu 입력 연결 | 테스트가 명시적 후보를 받지 않고 기본 입력을 읽었다. 기존 `IRIS_REFACTOR_MENU_INPUTS`를 소비하도록 수정했다. |
| G5 compiler identity | 과거 successor의 파일 수와 current 해시를 고정해 두었다. 현재 계약과 transition 목록을 참조하도록 수정하고 역사 기대값·변조 거부 검사는 유지했다. |

위 세 노드는 같은 After 작업 사본에서 함께 재실행해 통과했다. 전체 suite를 다시 실행한 것은 아니므로 이전 전체 실행을 소급하여 PASS로 표시하지 않는다. 상세 명령과 중간 실패 이력은 [구현 계획의 실행 기록](iris_refactoring_implementation_plan.md#2026-09-16-비-pz-잔여-해소)에 있다.

## 7. 작업 경계와 최종 인계

작업은 저장소 안에서 진행했다. Before/After는 `.tmp/s/b`, `.tmp/s/a`, 결과는 `.tmp/e`, 짧은 공유 checkout 경로는 `.w`를 사용했다. 검사 gate마다 별도 workspace를 늘리지 않고 기존 입력과 실행 결과를 재사용했다.

사용자의 지시에 따라 추가 raw-byte·해시 동일성 증명과 그에 따른 재생산·봉인을 중단했다. 이후 실패 3건을 PASS시키라는 요청에 한해 해당 기존 검사를 수정·재실행했다. 일회성 보조 스크립트를 정규 검사기나 새로운 validation authority로 채택하지 않았다.

실패 checkout의 재귀 삭제는 자동 승인 검토가 정책상 거부했다. 해당 자료는 비파괴 이동하여 `.tmp/e/fb/checkout`에 보존했다.

최종 판단과 구조는 다음 문서에 반영했다.

- [DECISIONS.md](DECISIONS.md): 유지·보관 결정, 검증 범위와 사용자 수락
- [ROADMAP.md](ROADMAP.md): 세션 작업 완료 상태와 기존 DVF/B42 과제 구분
- [ARCHITECTURE.md](ARCHITECTURE.md): Offline·runner·Lua 책임 및 optional pointer 처리

**이번 세션의 리팩토링과 설명 누락 대응은 완료했다.** 사용자 인게임 확인 이후 추가 검사나 봉인 작업 없이 종료했으며, 이 Walkthrough는 구현과 결과를 설명하는 문서다.
