> 후속 검토에서 이 보고서의 Compact 요약은 부분 해결로 판정됐다. 현재 결과와 표시 깊이 원칙은 [Compact 후속 교정 보고서](iris_dvf_compact_depth_2026-09-14.md)를 따른다. 아래 전후 예시·바인딩은 첫 교정 당시의 기록이다.

# 전체 설명 평가의 네 지적 교정 — 2026-09-14

## 범위와 판정

감독 작업이 정정한 네 문제만 대상으로 했다. 제작·개조 목적 요약, 액체의 선행 행동과 목적 연결, 불필요한 공개 조건, 소음 장치·발전기의 B41 실제 용도 근거 연결이다. 통폐합 전반의 추가 정리나 별도 영어 통조림·씨앗 문형 개선은 새로 착수하지 않았다. Base.Bleach와 Base.Watermelon은 기준본의 전체 레코드와 동일하다.

설명은 확인된 사실 중 용도를 이해하는 데 필요한 정보를 자연스럽게 전달해야 한다. 모든 사실을 의무적으로 공개하지 않으며, 단순한 문장 수 감소나 근거 참조 보존을 문장 품질 통과로 대신하지 않는다. 새로운 개별 아이템 ID/이름 조건이나 특정 아이템의 전체 기능 조합 조건은 추가하지 않았다.

## 규칙 문제 → 교정 원칙 → 적용 범위

| 문제 | 교정 원칙 | 적용 범위 |
|---|---|---|
| 제작 분야와 수리·개조를 한 나열에 끼워 넣음 | 작업 목적과 제작 결과를 구별해 문장을 구성하고, 같은 재료 역할의 반복은 줄인다. 한국어의 장비 분야는 실제 분야를 남기고 공통 명사만 공유한다. 영어에서는 중첩된 and를 만들지 않도록 분야를 병렬화한다. | 여러 제작·수리·개조 용도가 확인된 재료 전반 |
| 세 종류 이상이면 막연한 ‘장비’로 대체 | 개수에 따른 상위 범주 치환을 제거한다. 전자 기기·소음 발생 장치·폭발 장치, 사냥·낚시·야영 등의 확인된 분야를 남긴다. | 기존 material_frames의 복합 제작 용도 |
| Compact에 포장·묶기·개별 제작 도구 예시까지 동일 비중으로 노출 | 다른 개요가 있는 경우 포장·묶기와 개별 제작 도구 예시는 Expanded에 둔다. 유일한 용도일 때는 숨기지 않는다. 탈출용 로프 고정은 독립 목적이므로 유지한다. | 포장·묶기 참가자, 개별 제작의 tool 역할. 재료와 도구를 바꿔 설명하지 않는다. |
| ‘물을 담거나 보관하거나 운반’ | 받기가 확인되면 ‘담아’로 연결하고 이후 보관·운반·공급은 액체별로 확인된 기능만 표현한다. 미확인 기능·공개 조건이 섞인 문장은 기존대로 둔다. | 액체별 기능이 결합되는 용기. 물 기능을 연료로 전이하지 않는다. |
| 언어 일치를 위해 불필요한 상세를 복제 | 부목의 제외 부위와 기술서의 정확한 완독 배율을 용도 개요에서 제외한다. 골절 고정, 적정 기술 수준, 경험치 배율 증가 및 근거는 보존한다. | 완성 부목 1개와 기술서 60개. 부착물 효과·적용 조건은 일괄 삭제하지 않는다. |
| 전자 부품의 개조 나열과 제작 분야 소실 | 세부 감지·시간·원격 기능 추가 및 조명 전원 변환은 Compact에서 장치 개조로 묶고 Expanded에서는 구별한다. 제작 분야는 구체적으로 유지한다. | 개조 재료 역할에만 적용. 도구·개조 대상 역할은 그대로 구별한다. |
| 소음 장치·발전기의 실제 목적 미연결 | 기존에 허용된 설치/가동 행동을 검토한 B41 네이티브 소비 경로와 연결한다. | 양의 NoiseRange와 설치 행동이 있는 소음 장치 6개, 발전기 가동 행동 1개 |

묶기 데이터의 material 역할만으로는 묶이는 물품과 묶는 재료를 구별할 수 없다. 이를 이름이나 다른 용도로 추정하지 않았다. 따라서 다른 용도가 있는 묶기 참가자의 묶기 설명을 공통으로 Expanded에 배치하며, 로프·시트 로프의 묶기 용도도 Expanded에 보존한다. 이 규칙은 묶기 재료를 포장 대상으로 재분류하지 않는다.

## B41 근거

`Iris/build/description/source_support/b41_device_purposes.json`에 원본 클래스 및 Lua SHA-256과 검토한 경로를 기록하고 생산자에서 스냅샷 해시와 저장소 Lua 바인딩을 검사한다. 게임 설치를 생산 단계의 의존성으로 추가하지 않았다.

- 소음: `ISPlaceTrap.perform` → `IsoTrap(HandWeapon, …)`의 NoiseRange/NoiseDuration 복사 → `triggerExplosion(false)`의 양의 NoiseRange 분기에서 WorldSoundManager.addSound → `IsoZombie.RespondToSound`의 소리 유인도 판단과 방향 전환/pathToSound. 모든 좀비가 반드시 반응한다거나 피해를 준다는 설명은 만들지 않았다. 기존 투척 사용 근거도 유지하며 공격 피해를 암시하는 문구를 덜었다.
- 전력: `ISActivateGenerator.perform` → `setActivated` → `IsoGenerator.setSurroundingElectricity`의 활성·공간·야외 설정 검사와 setHaveElectricity. 같은 메서드의 가전·냉장 보관 설비 소비 연결도 확인했다. Compact는 주변 전기 설비 공급, Expanded는 야외 설정에 따른 주유기 공급까지 설명한다. 무제한 범위나 모든 설비 호환을 주장하지 않는다.
- 조사 명령은 설치 B41에 대해 `javap -classpath <ProjectZomboid> -c -p zombie.iso.objects.IsoTrap`, `zombie.characters.IsoZombie`, `zombie.iso.objects.IsoGenerator`를 실행했다. 덤프는 `.tmp/prose/summary-*.javap`에 있다.

## 전후 예시

### Base.Plank — KO compact

이전: 골절을 고정하는 부목 재료로 쓸 수 있다. 목공 및 건축, 사냥 장비, 야영 장비 및 도구 제작에 재료로 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다.

이후: 골절을 고정하는 부목 재료로 쓸 수 있다. 목공 및 건축에 재료로 쓸 수 있다. 사냥과 야영에 쓰는 장비 및 도구를 만들 때도 쓸 수 있다. 무기로 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다.

### Base.Nails — KO compact

이전: 목공, 건축 및 무기 수리, 사냥 장비 및 낚시 장비 제작에 재료로 쓸 수 있다. 모아서 상자로 포장할 수 있다. 위층 창문 등에 탈출용 로프를 고정할 수 있다.

이후: 목공, 건축 및 무기 수리에 재료로 쓸 수 있다. 사냥과 낚시에 쓰는 장비를 만들 때도 쓸 수 있다. 위층 창문 등에 탈출용 로프를 고정할 수 있다.

### Base.Log — KO compact

이전: 목공 및 건축, 야영 장비 및 숯 제작에 재료로 쓸 수 있다. 모아서 묶을 수 있다. 수박을 쪼개는 데 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다.

이후: 목공 및 건축에 재료로 쓸 수 있다. 야영 장비 및 숯을 만들 때도 쓸 수 있다. 모닥불 등의 연료로 쓸 수 있다.

### Base.ElectronicsScrap — KO compact

이전: 장치 개조, 조명의 건전지용 개조 및 발전기 수리, 장비 제작에 재료로 쓸 수 있다.

이후: 장치 개조 및 발전기 수리에 재료로 쓸 수 있다. 전자 기기, 소음 발생 장치 및 폭발 장치를 만들 때도 쓸 수 있다.

### Base.BleachEmpty — KO compact

이전: 연료를 담거나 공급할 수 있다. 물을 담거나 보관하거나 운반할 수 있다.

이후: 연료를 담아 공급할 수 있다. 물을 담아 보관하거나 운반할 수 있다.

### Base.Splint — KO expanded

이전: 머리와 몸통을 제외한 골절 부위를 고정하는 데 쓸 수 있다.

이후: 골절 부위를 고정하는 데 쓸 수 있다.

### Base.BookCooking1 — KO expanded

이전: 자신의 기술 수준에 맞을 때 읽으면 요리 경험치 배율을 높일 수 있다. 완독 시 최대 3배다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다.

이후: 자신의 기술 수준에 맞을 때 읽으면 요리 경험치 배율을 높일 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다.

### Base.NoiseTrap — KO compact

이전: 원격 작동, 움직임 감지, 시간 지연 기능을 더해 개조할 수 있다. 투척 공격에 쓸 수 있다.

이후: 원격 작동, 움직임 감지, 시간 지연 기능을 더해 개조할 수 있다. 소음을 내 좀비의 주의를 끄는 데 쓸 수 있다.

### Base.Generator — KO compact

이전: 야외 주유기에 전원을 공급할 수 있다.

이후: 가동해 주변 전기 설비에 전원을 공급할 수 있다.

## 실제 문면 검수와 검증

- 전체 2,105개 아이템, 8,420개 언어/표면 좌표를 재생성했다.
- 기준본 대비 104개 아이템, 214개 텍스트 좌표 변경: KO C 41, EN C 37, KO E 68, EN E 68. 설명 레코드의 근거·배치 메타데이터까지 비교하면 334좌표이며 텍스트 변경 수와 다르다.
- 같은 규칙이 적용될 수 있는 375개 항목을 넓게 선정해 KO/EN C/E를 모두 실제로 읽었다. 네 문장이 모두 같은 항목을 묶으면 174군이다. 이후 영어 병렬 수정 8개 좌표도 전부 다시 읽었다. 전체 문면은 `iris_dvf_four_corrections_2026-09-14_fulltext.txt`, 전체 전후 차이는 `iris_dvf_four_corrections_2026-09-14_changes.json`에 저장했다.
- 전수 구조 비교: 기존 Expanded fact_refs가 모두 남고 새 장치 근거만 추가됨. 기존 대상 그룹 내용·순서·범위 동일. 두 HTML의 접힘 그룹 136, 직접 노출 그룹 12, 대상/학습 식별자 886 보존. HTML 원문 좌표와 생성 JSON의 문면 일치 확인.
- 설명 상태는 모든 좌표에서 이전과 동일: 각 언어/표면 present 1,976, absent 129, failed 0.
- 새 네이티브 용도 사실 7개를 정확히 검사했다. 가상 모드 이름 변경, 양의/0/미확인 NoiseRange, 사용 행동 미연결, 액체별 기능 부분집합, 미확인 기능·조건 보존을 검사했다.
- 아래 명령이 종료 코드 0, `5 passed in 35.36s`로 통과했다. 최초 검사에서 새 사실 7개를 반영하지 못한 기존 허용 집합·합계 검사가 실패해, 새 사실의 정확한 대상과 함수를 검사하도록 갱신한 뒤 통과했다.

```powershell
uv run --project .\Iris\tooling python -I -B -m pytest --noconftest -c .\Iris\tooling\pyproject.toml .\Iris\build\description\v2\tests\test_layer3_rule_generalization.py .\Iris\build\description\v2\tests\test_layer3_composition.py::test_layer3_composition_contract .\Iris\build\description\v2\tests\test_layer3_description_composition.py::test_layer3_description_composition --basetemp .\.tmp\semantic-purpose-tests-4 -q -s --tb=short
```

독립 생성과 테스트는 직렬로 실행했다. 최초 및 중간 생성은 `uv run --project .\Iris\tooling python .tmp/prose/depth_regenerate.py`, 마지막 생성은 위 계약 테스트의 전수 생산·쓰기 경로로 이루어졌다. 최종 보존/HTML 비교 명령 `uv run --project .\Iris\tooling python .tmp/prose/semantic-audit.py`와 `uv run --project .\Iris\tooling python .tmp/prose/semantic-html-audit.py`도 종료 코드 0이다.

## 한계와 미변경 범위

실제 게임 폰트·폭에서 툴팁 4줄 충족은 이번에 검증하지 않았다. 소음·전력 용도는 B41 코드 근거를 연결한 것이며 실제 게임 UI 관찰 완료를 의미하지 않는다. 여러 독립 용도를 가진 재료는 개요에도 복수 분야가 남는다. 문장을 무조건 하나로 줄이거나 모든 분야를 막연한 상위 범주로 지우지 않았다.

부착물의 반동·사거리 등 효과는 이번 공개 정보 축소 대상으로 삼지 않았다. 별도 영어 통조림·씨앗 문형, 모드 어댑터, 다른 네이티브 장치 기능 추가 조사는 진행하지 않았다. 이번 작업에서 런타임 Lua를 수정하지 않았으며 게임 설치·패키징·커밋·푸시는 하지 않았다.

## 산출물 바인딩

- `Iris/build/description/composition/descriptions.json`: `ee710a6dfb6c6fbbe71129ec82a9583d016cffc36f1597145e5e054e62b1ceab`
- `Iris/build/description/composition/blocks.json`: `acada3e4a86ff395264dd0dc3854dd84878949f31b21f52605640373db35ed44`
- `Iris/build/description/source_support/b41_device_purposes.json`: `88b08fe4fdc0bd553c1e22a3b5cb9232c5eb78ef2c1fdd1c3d448493eba8f5b6`
