# Iris Current / Historical Physical Separation and Repository Lightweighting Walkthrough

작성일: 2026-08-26  
구현 기준 계획: [`iris_current_historical_physical_separation_and_repository_lightweighting_plan.md`](./iris_current_historical_physical_separation_and_repository_lightweighting_plan.md)  
기준 커밋: `9aa81249be7657a1e09a48d162fe96315cfd9748`  
최종 구현 커밋: `801f15f678fe9c5fd67be0f805f29ed3ba9db9b3`

## 1. 결과 요약

이번 작업은 Iris 저장소 안에 함께 존재하던 current runtime/source, historical reproduction payload, generated output, local execution residue를 물리적으로 분리하고 current 경로만 가볍게 유지하는 작업이었다.

완료된 핵심 결과는 다음과 같다.

- historical payload를 content-addressed external archive로 이전하고 복원 가능한 상태를 먼저 확립했다.
- archive가 보존한 tracked historical payload를 저장소에서 물리적으로 제거했다.
- current gate가 필요한 최소 증거만 compact current capsule로 유지했다.
- current Python tooling을 `Iris/tooling` 소유 경계로 정리하고 old tooling/runtime fallback을 제거했다.
- generated output과 runtime source의 authority를 분리하고 repository-local mutable output 의존을 제거했다.
- Layer 3는 current pointer가 선택한 generation 하나만 유지하고 predecessor generation과 fixed chunks를 제거했다.
- `.gitignore`, `.rgignore`, `.gitattributes`를 현재 역할 중심으로 단순화했다.
- 최종 clean-checkout full gate A/B, deterministic comparator, installed tooling, Lua syntax 및 package 생성까지 통과했다.
- 사용자가 후속 인게임 검증을 완료했다고 보고했다.

Git 기준으로 `9aa81249..801f15f6` 구간은 3,920개 파일에 영향을 주었으며, 5,095줄 추가와 7,140,071줄 삭제로 집계된다. 이 수치는 물리 제거 규모를 보여주는 Git diff 통계이며 runtime 성능이나 token 절감률을 의미하지 않는다.

## 2. 작업 경계와 원칙

작업은 `docs/Philosophy.md`의 Iris 규정을 유지하는 범위에서 수행했다.

- Iris는 근거 기반 정보를 읽기 전용으로 제공한다.
- 추천, 효율 평가, 우열 비교를 새로 도입하지 않는다.
- 게임 상태를 직접 변경하지 않는다.
- PZ runtime은 100% Lua를 유지한다.
- Pulse와 다른 spoke 모듈의 역할 또는 의존 경계를 침범하지 않는다.

이번 변경의 목표는 runtime 기능 추가가 아니라 저장소 물리 구조와 authority 경계를 정리하는 것이었다. 따라서 current runtime 동작을 보존하고 historical/reproduction 자료만 current checkout에서 분리하는 방향을 사용했다.

또한 실행 중 생성한 일회성 inventory/검사 보조 수단은 repository-regular validator나 새로운 canonical validation authority로 승격하지 않았다. 계획이 요구한 기존 gate와 versioned authority만 갱신했다.

## 3. 구현 흐름

### 3.1 Current / historical disposition 채택

`a2fe2f9c`에서 current/historical physical separation 결정을 채택했다. 이 단계에서 다음 역할을 명확히 분리했다.

- current runtime/source/tooling
- current gate에 필요한 compact evidence
- external historical archive
- repository-external mutable work/result/package/environment
- local custody checkout에만 남아 있는 ignored/untracked 자료

`Iris/build/main.py`는 clean checkout에서 필요한 phase module을 갖지 못한 broken legacy entrypoint로 판정하여 current authority에서 폐기했다. 이를 복구하거나 새 대체 CLI를 만들지는 않았다.

### 3.2 Tracked/local residue 제거

`9dc153ac`에서 tracked validation residue를 제거했고, 이후 current 실행과 무관한 `.tmp`, historical staging/output, legacy reports 및 repository-local generated residue를 archive/removal 대상과 current 보존 대상으로 분리했다.

local custody cleanup과 tracked removal은 서로 다른 subject로 처리했다. Git-tracked 삭제량과 custody checkout의 ignored/untracked 삭제량을 하나의 감소량으로 중복 합산하지 않았다.

### 3.3 Current runtime과 historical payload 분리

`5dc8d6f5`부터 current runtime이 historical staging/output 경로를 읽지 않도록 경계를 옮겼다. 주요 변경은 다음과 같다.

- current test fixture와 historical reproduction fixture 분리
- D16 current fixture를 current test owner로 이동
- current-required test 및 standalone validation을 compact baseline에 재결속
- current output root를 repository 밖에서 명시적으로 받도록 변경
- mutable workspace를 실행 시점에 repository-external root로 해석
- repository context를 명시적으로 전달하는 tooling 경계 도입

이 과정에서 current route가 ignored-only 파일이나 repository-local mutable output에 암묵적으로 의존하지 않도록 정리했다.

### 3.4 Historical archive 생성과 복원 계약

`c036eebd`에서 Windows long-path 복원을 지원하도록 archive restore를 보강했고, `75e1602b`에서 검증된 historical archive authority를 기록했다.

archive는 `content_addressed_zip_v2` 프로필을 사용한다.

- logical path와 object identity를 분리한다.
- 동일 content는 unique object 하나로 저장한다.
- 각 logical path는 원래 SHA-256과 object를 가리킨다.
- restore 시 duplicate path, missing object, hash mismatch를 fail-closed 처리한다.
- ZIP member 순서와 metadata를 고정하고 deflate level 9를 사용한다.

W10 측정에 기록된 archive 결과는 다음과 같다.

| 항목 | 결과 |
| --- | ---: |
| Logical files | 5,071 |
| Logical source bytes | 809,672,207 |
| Unique objects | 3,985 |
| Unique object bytes | 639,487,097 |
| Archive ZIP bytes | 39,550,318 |
| Archive SHA-256 | `24e7cd3cb97994d70d923dddfb68bf5135a887738a5dbbd2547a228fa8da972d` |

### 3.5 Compact current evidence 전환

`1f6c820f`와 `f7404725`에서 G5 compiler identity와 current capsule을 repository-external workspace routing에 맞게 전환했다.

current capsule은 historical raw payload 전체를 복제하지 않는다. current gate가 실제로 읽어야 하는 raw object만 유지하고, identity 확인으로 충분한 항목은 digest-only row로 보존한다.

W10 기준 capsule 결과는 다음과 같다.

| 항목 | 결과 |
| --- | ---: |
| Raw files | 14 |
| Raw unique objects | 12 |
| Raw retained bytes | 133,094 |
| Digest-only rows | 4 |
| Digest source bytes | 18,614,001 |
| Hard ceiling | 2,359,296 bytes |

### 3.6 Historical payload 물리 제거

archive 생성, inventory, restore parity 및 current independence 조건을 충족한 뒤 `a871879f`에서 tracked historical payload를 제거했다. `9b16c01c`은 archive-before-delete 순서와 physical removal 결과를 current authority에 기록했다.

주요 제거 surface는 다음과 같다.

- historical staging 및 attempt output
- historical evidence/CAS raw payload
- obsolete `_docs` 및 historical reports
- old generated output
- old tooling predecessor의 unique payload
- inactive Layer 3 generations
- legacy fixed Layer 3 chunks
- broken legacy root entrypoint와 stale full-table output route

current pointer-selected Layer 3 generation, stable facade, pointer, descriptor 및 current chunks는 보존했다.

### 3.7 Ignore와 byte-normalization 정책 단순화

`0ab36534`에서 `.gitignore`와 `.rgignore`를 current role 중심으로 단순화했고, `b381aa83`에서 guard가 현재 `.gitattributes` 정책을 사용하도록 결속했다.

W10 기준 visibility policy는 다음과 같다.

| 정책 | 결과 |
| --- | ---: |
| `.gitignore` total rules | 28 |
| `.gitignore` Iris rules | 2 |
| `.gitignore` negation rules | 1 |
| `.gitattributes` total rules | 97 |
| `.gitattributes` blob rules | 60 |
| `.gitattributes` normalization rules | 97 |

tracked identity는 checkout의 줄바꿈 변환 결과가 아니라 Git blob bytes/ID를 기준으로 유지했다.

### 3.8 Generated output 및 runtime authority 정리

`48517a45` 이후 classification, context outcome, Layer 3 compose 및 right-click output이 repository 안의 fallback 경로를 사용하지 않도록 정리했다.

관련 변경은 다음과 같다.

- classification install boundary를 full gate에 결속
- current output fallback 제거
- right-click output root를 실행 시점에 해석
- label-map 및 description direct runtime converter 폐기
- Layer 3 compose의 모든 output을 explicit external destination으로 요구
- diagnostic mode의 canonical output fallback 제거
- package에는 current runtime payload만 투영

`Iris/output`의 stale full-table `IrisData.lua`가 thin runtime adapter를 덮어쓰는 경로도 current route에서 제거했다.

### 3.9 Tooling과 G5 compiler identity 최종 결속

마지막 구간에서는 installed `iris_tooling` 환경과 Layer 3 compiler identity를 실제 successor source에 맞췄다.

- `d5ab56b6`: terminal Layer 3 tooling environment 결속
- `e3635fb8`: external Layer 3 compiler identity 결속
- `48cd36ff`: Layer 3 compiler aggregate binding 수정
- `e12cc7bf`: compiler identity test expectation 갱신
- `2e13049d`: 이름이 변경된 current test의 taxonomy identity 갱신
- `acdc9965` / `6ca45abe` / `bebf8763` / `801f15f6`: Reviewer가 지적한 successor append-only 위반을 단계별로 보정하고 기존 gate schema에 맞는 새 0015 successor로 current binding 이동

마지막 taxonomy 수정은 새 검증 체계를 추가한 것이 아니라, `test_diagnostic_resolver_rejects_canonical_output_path`에서 `test_diagnostic_resolver_requires_all_external_outputs`로 변경된 기존 테스트 이름을 authoritative taxonomy row에 반영한 것이다.

후속 독립 검토에서 `g5_compiler_identity_successor_0013.json`이 최초 committed bytes 대신 정정된 aggregate로 덮어써진 append-only 위반 한 건이 확인됐다. 0013을 최초 blob으로 복구하고 정정 aggregate는 새 0014 successor에 기록했다. 다음 재검토는 schema 호환 보정 과정에서 이미 commit된 0014를 다시 수정한 같은 계열 위반을 확인했다. 이에 최초 0014 blob도 복구하고 schema-compatible 정정은 새 0015 successor에 기록했으며, `full_repository_gate.json`의 current transition을 0015로 이동하고 0013·0014·0015를 required chain으로 유지했다. 일회성 cleanup mode나 새 regular schema는 추가하지 않았다.

### 3.10 Terminal local-custody 보정

최종 구현 뒤 simplified ignore policy로 노출된 dirty-main의 Iris local-custody surface를 별도 subject로 다시 판정했다.

- nonignored untracked: 295 files / 4,273,310 bytes
- ignored pipeline logs: 2 files / 3,205 bytes
- W0 당시 identity와 다른 files: 0
- current clean tree에 존재하는 files: 0
- predecessor archive에 같은 logical path가 있는 files: 0
- retained exception / unresolved: 0

295개 legacy row는 W0에서 이미 ignored custody file로 관측됐고 terminal까지 SHA-256이 하나도 바뀌지 않았다. 기존 archive에는 포함되지 않았으므로 predecessor archive를 변경하지 않고 별도의 additive external `content_addressed_zip_v2` archive를 생성했다.

| 항목 | 결과 |
| --- | ---: |
| Logical files | 295 |
| Logical/unique source bytes | 4,273,310 |
| Compressed bytes | 1,065,869 |
| Archive SHA-256 | `fbd85f142064b72d25437fcf627ee16c1fa40497a5e94196c97b99d9a0f3b749` |
| Create / verify / restore | PASS / PASS / PASS |

Archive restore는 295 files / 4,273,310 bytes의 logical tree parity를 확인했다. 그 뒤 295개 archive-backed files와 2개 regenerable log를 각각 literal path로 제거했다. Broad recursive deletion이나 glob-selected deletion은 사용하지 않았으며, exact containment, reparse ancestry, tracked-path rejection, pre-delete hash 및 post-delete absence를 transaction에서 확인했다.

Item inventory, additive selection, cleanup transaction과 raw receipts는 다음 external create-new root에만 존재한다.

`C:/Users/MW/i/physical-capacity-iris-lightweighting-terminal-inv-terminal-w10-2e13049d995d-termin-01a17c871dce`

이 one-off material은 canonical validator, regular schema 또는 새 validation claim으로 등록하지 않았다.

## 4. 경량화 측정 결과

최종 W10 packet은 exact implementation subject `801f15f678fe9c5fd67be0f805f29ed3ba9db9b3` / tree `1db498cabee54d1516e8dc0e78d6a99c8806a4a4`에 다시 결속했다. Clean implementation과 현재 dirty-main local custody는 별도 subject/root/status digest로 측정했다.

- W10 packet: `C:/Users/MW/i/physical-capacity-iris-lightweighting-terminal-inv-terminal-w10-801f15f678fe-termin-6bf8179bacfa/terminal-inventory-result/w10_packet.json`
- W10 packet SHA-256: `d6015d4385f8da6625ebe14304775797db9c5c799398309d4164401a62ce012d`
- Subject manifest SHA-256: `4e1a1f1243e82feb1c16bd26ff37e12c40eafca4e2a9ce319a1ac76495b16eac`

W10의 clean implementation subject 결과는 다음과 같다.

| 항목 | 결과 |
| --- | ---: |
| Iris tracked files | 1,753 |
| Iris tracked Git blob bytes | 71,766,663 |
| Iris physical files | 1,753 |
| Iris physical bytes | 72,344,398 |
| Local-custody Iris physical files | 1,753 |
| Local-custody Iris physical bytes | 72,154,554 |
| Local-custody ignored / untracked / filesystem-only / reparse | 0 / 0 / 0 / 0 |
| Current Layer 3 generation directories | 1 |
| Unresolved blockers | 0 |
| Unsupported keep | 0 |
| Remaining eligible removal | 0 |
| Unimplemented removal | 0 |

계획 작성 시 관측된 Iris tracked surface는 5,467 files / 약 648.09 MiB였다. 측정 방식과 commit이 다르므로 단순 성능 개선률로 해석해서는 안 되지만, historical payload가 current tracked checkout에서 물리적으로 제거되었다는 결과는 명확하다.

repository-local successor overhead는 공식에 따라 `801f15f6` tree에서 다시 계산한 1,653,400 bytes이며 ceiling 3,037,162 bytes 이내로 PASS했다. current capsule raw bytes, external archive/object/inventory/receipt bytes와 삭제·축소된 파일의 음수 delta는 이 값에 중복 합산하지 않았다.

## 5. 최종 자동 검증

최종 자동 검증은 Reviewer remediation이 반영된 commit `801f15f678fe9c5fd67be0f805f29ed3ba9db9b3`에서 수행했다. 최종 Run A/B는 서로 분리된 새 allocator-owned root에서 병렬 실행했고 comparator는 두 PASS receipt를 대상으로 한 번 실행했다.

| 검증 | 결과 |
| --- | --- |
| Clean-checkout terminal Run A | PASS, exit 0 |
| Clean-checkout terminal Run B | PASS, exit 0 |
| Deterministic A/B comparator | PASS, exit 0 |
| Pytest identities | 211 passed |
| Reported subtests | 109 passed |
| Standalone validations | 4 passed |
| Installed `iris_tooling` tests | 26 passed |
| `iris_tooling` CLI probe | PASS |
| Lua syntax | 127 files PASS |
| Current runtime package | PASS |
| Package ZIP | PASS |

최종 package output은 repository 밖에 생성했다.

- Staged package: `C:\Users\MW\i\ta-f2d4539c24a6\package-result\Iris`
- Manifest: `C:\Users\MW\i\ta-f2d4539c24a6\package-result\Iris.package_manifest.sha256.json`
- ZIP: `C:\Users\MW\i\ta-f2d4539c24a6\package-result\Iris.zip`

테스트 실행 중에는 Run A/B를 서로 분리된 allocator-owned root에서 병렬 실행했고 약 30초 간격으로 상태를 확인했다. 두 실행은 비정상 장기 실행 없이 약 5분대에 종료되었다.

### Checkpoint A/B/C/D

| Checkpoint | Exact subject commit / tree | Run A / Run B orchestration SHA-256 | Comparator / canonical result SHA-256 | Gate claim과 역할 | External locator |
| --- | --- | --- | --- | --- | --- |
| A | `9aa81249be7657a1e09a48d162fe96315cfd9748` / `c9137a3f0597b39c94000b2cc27ea28e9fab964a` | `69a5a44243706c3b2ead4f9c81a6fb84600e8fb9145846a782f23bc02c15e791` / `d4f1f11c104466925dded95ac4439f0fabc8b245913d8fd08e0fa8d142370b16` | `e7619bd1963b10c53afe34bf7411f0d10870a8c3eca28fa498a6e9bafe5c772d` / `27d1de54a779db206d2e07b35d54a4bf880f9ccb829c98fb2e0120e6a419a1b5` | `iris-lightweighting-current`; baseline admission, historical checkpoint evidence | A `C:/Users/MW/i/cp-7950a05b9877`; B `C:/Users/MW/i/cp-673ba2da67b5` |
| B | `4bc878098c9923832a7921dbb856232f7faa15d0` / `2fc221ee1c065e5737f656ce94f5f0362ce8982a` | `d561824f8a207bf154be0bbbe9d16334245fe9e0e1f5068d201e36ea03947bff` / `f1edcfc574e947cd12a02cad279b8d033314ad953fa9a7371628959f69f565fc` | `a1381640cfc764a69e0c23dadcbd5f2d59ee7f782e96a294825c467caefd7e2e` / `6deb92aa41c9defc8487bf84ad750207a08cbbd9809df251a1cf41e9018709eb` | `iris-lightweighting-current`; successor/pre-archive, historical checkpoint evidence | A `C:/Users/MW/i/cp-c1ae75279fc4`; B `C:/Users/MW/i/cp-90f73133165f` |
| C | `3c4543e624a3a4750dbb4ee1f23f8ef0e522d2a2` / `e85080ec3712da313f9290aa11f322da7c5d0ff9` | `fe223db7a9187faa7905f569c943c17b185633fc69d7876f9db6d68a7f3accb6` / `81f28011390819234121821126bdd0ef93eed5d90edf13070a26d5f91206b983` | `c1487b4f9c0bc33f07d0b9d836e9ddfd0a4311771ca7be522ab08c6ede35600e` / `7c29b14cc1268c922326fefe093ab0aea6a7e2b14493652792d4cc806209f6d6` | `iris-lightweighting-current`; synthetic pre-delete candidate, historical evidence | A `C:/Users/MW/i/cp-24adc20885d3`; B `C:/Users/MW/i/cp-e185e14cd763` |
| D | `801f15f678fe9c5fd67be0f805f29ed3ba9db9b3` / `1db498cabee54d1516e8dc0e78d6a99c8806a4a4` | `fc55fd911cc8724ef01772ec304055c4e1711774913fbac3e1b08a5d0c0b2edf` / `553a46014ce960c4bd77496b1a50a6d501a87b36c0e3c0584dbc9cd760a43f4c` | `2f1bad4abac8faa4c4eb1af847eb3eba163f5cb2288155d6aa8f93e330ccf250` / `dd309cf1a7650b2a9e2ab1871cf1d31d33720d0312ed86d65a4a9debf7c83c65` | `iris-lightweighting-current`; exact terminal implementation, current closeout machine evidence | A `C:/Users/MW/i/ta-f2d4539c24a6`; B `C:/Users/MW/i/tb-f729d02a4716` |

Checkpoint C는 external synthetic-generation receipt가 결속한 candidate에서 기존 ordinary canonical full gate를 그대로 실행했다. Cleanup 전용 execution mode, regular schema 또는 canonical validator는 추가하지 않았다.

## 6. 외부 검토와 인게임 검증

구현 commit `c2b9514f` 시점의 선행 Codex Reviewer 결과는 actionable finding 0건이었다. Terminal closeout 검토 1차는 0013 overwrite 1건을, 2차는 보정 중 발생한 0014 overwrite 1건을 보고했다. 두 predecessor를 각각 최초 committed blob으로 복구하고 current correction을 append-only 0015로 이동했다. `c2b9514f..801f15f6`의 최종 implementation, terminal receipts, W10과 documentary closeout은 최종 재검토 대상으로 남겨 두었으며, 재검토가 actionable finding 0으로 끝나기 전에는 최종 closeout을 `complete`로 표시하지 않는다.

자동 검증 완료 후 인게임 검증은 사용자가 직접 수행했다. 사용자는 2026-08-26 현재 인게임 검증이 완료되었다고 보고했다. 별도의 게임 로그나 신규 repository-local proof artifact는 생성하지 않았다.

사용자 인게임 검증은 완료됐지만 현재 문서 carrier 작성 시점의 상태는 `pending_independent_review`다.

## 7. 주요 커밋 Walkthrough

| Commit | 역할 |
| --- | --- |
| `a2fe2f9c` | Current/historical separation 결정 채택 |
| `9dc153ac` | Tracked validation residue 제거 |
| `5dc8d6f5` | Current runtime과 historical payload 분리 |
| `b8a3e91f` | Current output을 repository-external root에 결속 |
| `70ea009c` | Mutable workspace를 실행 시점에 해석 |
| `c036eebd` | Windows long-path archive restore 지원 |
| `75e1602b` | Historical archive 생성 및 authority 기록 |
| `f7404725` | Compact current capsule binding 완료 |
| `a871879f` | Archived historical payload 물리 제거 |
| `9b16c01c` | Historical physical removal 기록 |
| `0ab36534` | Repository visibility policy 단순화 |
| `48517a45` | Iris output authority 경량화 완료 |
| `72d318f9` | 남은 current output fallback 제거 |
| `5cbf4a1b` / `dab2224a` | Direct runtime converter 폐기 |
| `1c0363fd` / `c2b9514f` | Layer 3 output을 external explicit destination으로 제한 |
| `e3635fb8` / `48cd36ff` | G5 Layer 3 compiler identity와 aggregate 결속 |
| `e12cc7bf` / `2e13049d` | 최종 test expectation 및 taxonomy identity 정합화 |
| `acdc9965` / `6ca45abe` / `bebf8763` / `801f15f6` | Immutable 0013·0014 복구, append-only 0015 정정 successor와 current gate 결속 |

## 8. 최종 상태와 운영상 주의점

최종 implementation subject는 `801f15f6`다. 이후 tracked closeout carrier는 문서와 compact documentary readpoint만 변경하며 terminal machine PASS를 carrier commit의 실행 결과로 재귀속하지 않는다.

운영 시 지켜야 할 경계는 다음과 같다.

- historical 자료가 필요하면 저장소 안의 삭제된 경로를 복구 대상으로 삼지 말고 external archive locator와 restore 계약을 사용한다.
- current generator/tooling output은 명시적인 repository-external output root에 쓴다.
- current runtime package에는 pointer-selected Layer 3 generation 하나만 포함한다.
- `Iris/output`, historical staging 또는 old tooling 경로를 current authority로 다시 사용하지 않는다.
- 일회성 census/보조 스크립트를 canonical validator로 승격하지 않는다.
- runtime 기능 변경이 추가되면 이번 lightweighting PASS를 그 변경의 검증으로 재사용하지 않는다.

이번 작업은 Git history rewrite, universal external-mod compatibility, release/publish readiness 또는 runtime 성능 향상을 주장하지 않는다. 달성한 결과는 current checkout의 물리 경량화, historical 복구 경계의 외부화, current authority 단일화, 그리고 해당 구조의 자동·인게임 검증 완료다.
