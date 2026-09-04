# Iris DVF Layer 3 복수 의미·정보 해상도 Successor Contract Closeout

> 문제 ID: `DVF-L3-01`
>
> 상태: `complete`
>
> 완료일: 2026-09-03
>
> contract manifest: `Iris/_docs/authority/dvf/layer3_successor/contract_manifest.json`
>
> manifest SHA-256: `6735c3eadafaf4c4fd51ae56c8d0748d32903ee996d53ed43bca38822cf0932a`

## 결과

Iris Layer 3의 current semantic authority에 대표 필드 없는 `0..N` multi-fact successor contract를 채택했다.

- exact case-sensitive FullType와 stable fact identity를 유지한다.
- 복수 `use_context`와 context-local `context_role`, fact-local `condition`/`constraint`를 정의했다.
- semantic fact, provenance, investigation/coverage, approved expression과 surface projection을 분리했다.
- Layer 3 broad context와 Layer 4 exact Recipe/Right-click/EvolvedRecipe relation의 정보 해상도 경계를 정했다.
- acquisition을 mandatory investigation axis로 두고 `resolved / investigated_unresolved / not_investigated`를 분리했다. Resolved는 acquisition 축만 완료하며 item 전체 Layer 3 investigation 완료를 단독으로 보장하지 않는다.
- Menu Layer 3와 Tooltip S2의 same-authority/different-depth, no-primary selection, Menu preservation과 dependency preservation을 채택했다.
- profile taxonomy/first-contact axis와 item-level 조사 완료 조건은 DVF-L3-02, semantic/acquisition facts는 DVF-L3-03/04, 실제 S2 fact 결합·KO/EN 표현·문장/줄 구성·omission tracking은 DVF-L3-05, runtime current adoption은 DVF-L3-06에 남겼다.
- owner approval gate는 사용자의 2026-09-03 실행 프롬프트 사전 승인으로 통과했다.

Current authority manifest와 route index는 위 contract manifest를 각각 한 번 가리킨다. 기존 product pointer와 Tooltip locator는 변경하지 않았다.

## Baseline과 보호 결과

실행 시작 HEAD는 `ef0ecc60896d729013852ef415b0e46ec89d6f81`였고, preexisting dirty state는 사용자 제공 plan 한 건뿐이었다.

- Layer 3 facts/decisions: 각각 2,105 rows, exact FullType set 동일
- predecessor facts: `primary_use` 2,097, `secondary_use` 0, `identity_hint` 2,105, `special_context` 44, `acquisition_hint` 1,105
- decisions: adopted 2,099 / unadopted 6; tool 1,144 / material 240 / output 721
- Tooltip Layer 3 owner input: fact 2,048 / explicit absence 175
- current generation: `dvf33-ed92fa5c9ed4a1ed367f5d79365d04e1996e36a05d76a33bd7b8dd2176e7f82f`, 14 members

Focused Gate가 facts, decisions, Tooltip owner input, current pointer, pointer-selected generation과 계획에 명시된 두 Lua consumer의 exact SHA-256 불변성을 확인했다. 상세 digest와 predecessor disposition은 `predecessor_inventory.json`에 있다.

## Validation

최종 G1 명령:

```powershell
uv run --project .\Iris\tooling --no-sync pytest .\Iris\build\description\v2\tests\test_layer3_successor_contract.py -q --round3-contract=diagnostic --round3-additional-source=Iris/build/description/v2/tests/test_layer3_successor_contract.py
```

결과: exit `0`, `1 passed` in `0.15s`.

외부 검토 후 같은 G1을 다시 실행한 최종 결과는 exit `0`, `1 passed` in `0.18s`다. Acquisition `resolved`는 acquisition axis 완료만 뜻하고 item 전체 investigation 완료를 함의하지 않도록 수정했으며, profile은 first-contact axis scope를 제공할 수 있고 실제 S2 fact 결합·표현·문장/줄 구성·omission tracking은 후속 DVF-L3-05가 정하도록 과잉 금지를 제거했다. 또한 predecessor의 유지 표현은 S1/S3/S4 ownership과 `0..4` logical-row structure로 한정했다.

Pytest cache가 repository root `.pytest_cache`에 쓰지 못했다는 warning 한 건이 있었으나 cache 부가 기능에만 해당하며 test와 exit status는 PASS였다.

최종 PASS 전 실패는 숨기지 않는다.

1. 첫 실행은 새 test source가 기존 Round 3 source policy에 미분류되어 collection 전 fail-closed했다. 같은 source를 planned current로 등록했다.
2. 두 번째 실행은 기본 current collection이 이 focused test가 소비하지 않는 외부 output seed를 configure 단계에서 요구해 collection 전 종료됐다. 외부 workspace를 만들지 않고 기존 additional-source/diagnostic collection boundary를 계획과 명령에 명시했다.
3. 세 번째 실행은 test 본문이 최초 PowerShell 문화권 정렬 digest와 명시된 ordinal canonicalization의 불일치를 검출했다. Exact set의 missing/extra 문제는 아니었으며 ordinal digest와 manifest/readpoint를 교정했다.
4. 교정된 최종 G1이 PASS했다.

계획에 없던 full repository suite, current-required runner 전체, Lua syntax, package/install, actual PZ 관찰과 compatibility 검사는 실행하지 않았다. Independent review는 이 계획의 required Gate가 아니므로 추가하지 않았다.

2026-09-04 사용자 요청에 따른 Git 반영 준비에서는 새 test source의 tracked 전환에 맞춰 기존 source-set binding을 tracked 50 / approved absent 0으로 갱신했다. `.gitattributes`에는 contract bundle과 human contract의 byte 보존 규칙을 추가했다. 이 VCS 정리와 후속 설명 문서 수정에는 테스트를 재실행하지 않았으며, 위 G1 PASS는 계약 구현·검토 정정 당시의 실행 결과로 유지한다.

## 완료 주장 경계

### Validated

- contract bundle JSON/schema 핵심 구조와 네 member digest
- `0..N` fact model, context-local role, fact-local qualifier binding과 axis 분리
- 대표 alias/output leakage/acquisition false-completion 금지 case
- vocabulary compatible extension과 breaking revision 경계
- Menu/Tooltip same authority, Menu preservation, no-importance-selection과 runtime inference 금지
- predecessor disposition completeness와 baseline/protected product identity
- top docs, contract manifest와 current authority route digest 일치
- required validation identity 한 건 등록

### Unvalidated but in scope

- 없음

### Out of scope / non-claims

- 2,105개 item의 successor semantic/acquisition 조사 완료
- 2,097개 predecessor `primary_use` 또는 `special_context` migration
- profile taxonomy와 first-contact axis 완료
- 전체 context/role vocabulary 확정
- KO/EN successor corpus와 Tooltip/Menu implementation
- generation/runtime/package/in-game adoption
- compatibility, freeze, release, Workshop 또는 deployment readiness

따라서 허용되는 최종 claim은 다음으로 제한한다.

> Iris Layer 3의 adopted successor semantic contract가 복수 use context, context-local role, typed facts, acquisition mandatory investigation, Layer 3/4 information-resolution boundary와 Tooltip first-contact/Menu expanded-detail 관계를 정의한다.
