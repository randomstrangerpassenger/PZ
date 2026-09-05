# Iris Layer 3 expression consumer contract

DVF-L3-05의 독립 off-live 설명 authority다. `Philosophy.md`와
`iris_dvf_layer3_fact_bound_expression_menu_tooltip_resolution_plan.md`를 따른다.
채택 여부는 아래 readpoint의 exact candidate와 adoption receipt로 판정한다.
현재 Menu·Tooltip, Lua generation, package, current registry를 전환하지 않는다.

## Readpoint와 실행

- Readpoint: `Iris/_docs/authority/dvf/layer3_expression/manifest.json`.
- Installed owner: `iris_tooling.domains.layer3.expression_results`.
- 소비: `load(repository_root, manifest_binding, mode="adopted")`.
- `candidate` 소비는 adoption을 의미하지 않는다. Adopted 소비는 기존
  L3-01~04 binding, member bytes, rule/review, exact 결과, receipt를 확인한다.
- `prepare --repository-root .`는 위 root의 `descriptions.json`과 manifest만
  생성한다. `review.json`은 producer가 승인하거나 자동 갱신하지 않는다.
- `adopt --repository-root . --candidate-sha256 <hash> --gate-exit-code 0
  --authorization <owner authorization>`는 성공한 exact candidate만 대상으로
  한다. 최종 위치의 candidate bytes를 유지하고 같은 호출에서 adopted loader를
  읽는다. 실패하면 완료 receipt를 제거하고 원래 candidate를 남긴다.

`manifest.json`은 네 입력의 고정 SHA-256, data/review/producer/test/contract의
path와 SHA-256, exact denominator, serialization을 결속한다. Candidate bytes는
채택 시 수정하지 않는다. Adoption은 `adoption.json`이 소유하며 별도 current
route/authority manifest/validation registry에 등록하지 않는다.

사용자가 요구한 해상도 교정으로 선행 subject를 철회할 때는 기존 receipt를
`superseded`로 명시한 뒤 새 candidate를 만든다. 새 manifest의 `supersedes`와 새
receipt의 `superseded_result`가 이전 hash·그 당시 Gate 결과·교정 사유를 보존한다.
새 candidate는 자체 단일 Gate와 readback을 요구한다. 교정 채택이 실패하면 완료
receipt 대신 기존 superseded 상태를 복원한다. 선행 PASS를 수정본에 승계하지 않는다.

## 데이터

`descriptions.json`의 schema는 `iris-layer3-expression-v1`이다.

- `facts`: authority ID와 fact ID를 함께 가진 `ref`, exact case-sensitive
  `item_id`, 원래 kind/payload/provenance, context와 양방향 qualifier 연결.
  Acquisition route/conditions는 원래 payload에 보존된다.
- `provenance`: authority-qualified key로 묶은 원래 provenance record.
- `expressions`: locale, 구체적인 text, claim과 represented fact refs,
  실제 문장에 표현한 dependency refs, rule 및 locale별 review identity.
- `items[].profiles`: resolver가 유지한 모든 적용 scope와 각 프로필이 기여한
  accepted fact refs. Profile 자체는 사실이나 중요도를 만들지 않는다.
- `items[].locales.ko/en.expanded`: 0..N개의 block. 각 block은 문장·expression
  refs·fact/dependency refs와 모든 기여 프로필의 조합 규칙을 가진다.
- `items[].locales.ko/en.s2`: 0..1 logical row, text, represented/dependency refs.
  줄바꿈과 의미 절단이 없으며 여러 문장을 담을 수 있다. Expanded 문장을 자르는
  대신 `description_projection`이 first-contact proposition을 별도로 합성한다.
  `detail_qualifier_refs`는 S2에서 표현하지 않은 일반 실행·상세 조건을 가리킨다.
- `fact_expressions`: 각 accepted fact가 그 locale에서 실제로 표현된
  expression ID 목록. 5,290 × 2개의 key pair가 모두 채워져야 한다.
- `tooltip_detail_omission_refs`: expanded facts 중 S2 바깥의 정상 상세 생략.
- `first_contact_obligations`: exact `(FullType, axis_id, scope_ref)`와 whole/partial
  contribution. Accepted contributor 없는 unresolved, scoped N/A를 구별한다.
- `upstream`: pending scope, 조사 미완료와 acquisition 상태를 보존한다.
  그 상태만으로 negative 문장이나 expression gap을 만들지 않는다.

Object key, qualified identity, set 직렬화는 정렬하고 UTF-8/LF compact JSON으로
저장한다. 정렬은 중요도·대표성·빈도를 뜻하지 않는다. 전역 fact/문장 수 제한은 없다.

## 조합과 표현

`expression_rules.py`는 채택된 프로필 registry에 대응하는 조합 문법과 KO/EN
기능·효과·활동·역할·21개 predicate branch를 소유한다. `acquisition_expression.py`는
채집/씨앗, 낚시, 덫, 시작 지급, 14개 회수 경로의 표현을 소유한다.

음식은 섭취/효과의 상태 조건, 문헌은 읽기와 학습 효과의 별도 조건, 의류는
착용 위치, 용기는 보관/이동 조건, 제작·조리·월드 작업은 context-local role로
block 조합 범위를 정한다. Direct는 관련 없는 기능을 묶지 않는다. 무기와
drainable 프로필만으로 공격이나 연료 기능을 만들지 않는다. 모든 기여 프로필의
조합 key를 함께 적용하며 primary profile을 고르지 않는다. 어떤 scope에도
소속되지 않은 사실은 residual block으로 남는다.

Expanded의 각 claim 바로 옆에 그 claim의 조건을 둔다. 역할은 연결된 활동과 그 활동의
조건을 함께 말한다. 서로 다른 조건 집합을 paragraph 전체의 공통 조건으로
확장하지 않는다. 동일한 사실을 여러 expression이 언급할 수 있으나 fact identity와
provenance를 합치거나 삭제하지 않는다. S2는 기능·효과·활동의 구체적인 첫 이해를
프로필별로 합성한다. 음식 섭취와 조리 재료, 음용과 갈증·오염수 중독, 도구의 여러
활동, 독서와 학습 효과처럼 함께 설명할 수 있는 claim을 합친다. 역할의 실제 의미가
repair target이면 수리 도구라고 쓰지 않는다.

S2에서 소지품·접근·권한·일반 제작 가능 여부·행동 유효성은 실행 상세로 생략하고
expanded에 보존한다. 오염된 물, 학습 수준, 호환 장치 범위와 필기구처럼 첫 이해에
필요한 조건은 실제 짧은 문장에 남긴다. 수치 임계값을 모두 옮기지 않고 조건부
가능성을 설명한다. 생략된 조건 fact를 represented라고 표시하지 않는다.
Accepted first-contact contributor는 S2 represented 또는 명시적 detail qualifier
disposition에 모두 대응하며, 비조건 기능·효과·맥락·역할은 빠뜨리지 않는다.
Character quota, 임의 fact 선택, runtime 재요약은 없다.

Acquisition은 장소·방법·의미 있는 이용 조건과 복수 경로를 표현한다. 계절 제한은
연중 전체 월 목록 대신 실제 제한된 시기를 구간으로 표현한다. 획득 장소는 양수의
item/category 선택 가능 지역을 함께 읽어 표현하지만 선택 가중치는 출력하지 않는다.
Callback·registration·marker·destination 처리, 생성 계수, raw random check,
확률 우회 표기와 일반 실행 전제는 원래 payload/provenance에만 남긴다. 실제로
얻지 못할 수도 있는 경로는 조건부 가능성으로 설명한다.

Acquisition dependency의 개별 path와 `user_proposition`은 해당 문장의 의미 근거를
가리킨다. 그 field의 모든 내부 절차를 발화했다고 주장하지 않는다. Fact 표현은
payload 원문 열거가 아니라 정확한 사용자-facing proposition 설명이다. 서로 다른
경로를 대표 하나로 합치지 않는다.

영문 코드 식별자가 필요한 획득 조건의 종류명에는 원본 식별자를 쓸 수 있다.
이는 다른 locale의 문장 fallback이 아니다. Recipe/우클릭의 exact 행동·입출력·대상
관계 catalogue는 생성하지 않는다. 음식의 accepted 효과가 없으면 허기 감소 등을
추측하지 않는다. 신규 payload/profile/번역 branch는 review 갱신 없이 complete로
닫지 않는다.

## Review와 단일 Gate

`review.json`은 입력 binding, 실제 payload selector domain digest, producer/rule
bytes, profile grammar, KO/EN 각각의 승인·검토 내용을 결속한다. 이는 이번 설명
authority의 콘텐츠 자료이며 새로운 공용 validator나 validation registry가 아니다.
Freeform fallback은 없다. 지원하지 않는 payload와 미승인 locale는 expression gap으로
실패하며, stale review/unknown ref/mixed input/member drift/path escape를 거부한다.

단일 focused source는 `Iris/build/description/v2/tests/test_layer3_expression_results.py`다.
공용 conftest의 정규 registry·저장소 밖 출력 요구를 가져오지 않도록 다음 명령을 쓴다.

```powershell
uv run --project .\Iris\tooling --no-sync python -I -B -m pytest -q -s --noconftest --import-mode=importlib -c .\Iris\tooling\pyproject.toml --basetemp .\.tmp\expression .\Iris\build\description\v2\tests\test_layer3_expression_results.py
```

Installed module hash, 네 adopted 입력, 2,105/5,290/10,580/1,057 denominator,
프로필/조건/locale, expanded/S2/omission/upstream reconciliation, 입력 순서 변경의
결정성, malformed consumer 및 실패한 adoption의 receipt 회수를 같은 Gate에서
검사한다. 기존 protected bytes와 current config를 이 실행 안에서 공유 확인한다.
별도 final-binding/aggregation/readback Gate나 전체 suite를 요구하지 않는다.

검증 한계: 실제 PZ, Menu rendering, Tooltip physical wrapping/Alt, S1/S3/S4와
최종 4줄 통합, Lua/package/install/release는 범위 밖이다. Item별 번역 취향의 전수
보증이나 upstream 조사 재인증도 아니다. Closeout은 exact 명령·exit·hash·ceiling을
한 문서에 기록한다.
