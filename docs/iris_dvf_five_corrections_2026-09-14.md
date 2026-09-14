# Iris DVF 다섯 지적 교정 결과 — 2026-09-14

격리 worktree에서 다섯 지적을 수정하고 전체 2,105개, KO/EN Compact/Expanded 8,420좌표를 재생성했다. 기준 문면 대비 53개 아이템의 188좌표가 변경됐다: KO C 43, KO E 51, EN C 43, EN E 51. 같은 경로의 후보와 대조 항목 86개를 선정하고, 네 문장이 같은 항목을 묶은 56개 군의 한국어·영어 C/E 전문을 읽었다. 기계 검사의 통과와 문면 검수는 별도로 수행했다.

현재 원문은 [전체 설명 HTML](iris_dvf_descriptions.html), 전후 비교는 [비교 HTML](iris_dvf_description_review.html), 전 변경 문장은 [변경 JSON](iris_dvf_five_corrections_2026-09-14_changes.json), 후보 전문은 [문면 검수 전문](iris_dvf_five_corrections_2026-09-14_fulltext.txt)에 있다.

## 기준본과 인계

- 원본: `C:/Users/MW/Downloads/coding/PZ`. 작업 위치: `C:/Users/MW/.codex/worktrees/998c/PZ`.
- 원본 `docs/Philosophy.md`를 먼저 읽고 이전 작업의 idle 상태 및 쓰기 중단 인계를 확인했다. 원본의 미커밋·미추적 128파일을 복사하고 각각 SHA-256을 대조했다. 새 checkout의 줄바꿈 변환으로 r6 `acquisition.json`의 근거 SHA가 달랐으므로, 원본 추적 파일 중 바이트가 다른 1,777파일도 정렬했다. 이 정렬은 새로운 교정 변경 범위가 아니다.
- 최초 HEAD: `92236bad397202cbbda510ea1d031877cc911933`. 문면 기준 descriptions SHA-256: `2eb17f48bdaeefe6c0960408bfa896ea80562fe8adb0d6bc8c624da72cdb84fb`. blocks 기준: `acada3e4a86ff395264dd0dc3854dd84878949f31b21f52605640373db35ed44`.
- 인계에는 아직 생성·검증하지 않은 발전기 공개 깊이, 붕대/VHS Compact 깊이, 중립적인 투척 문형 수정도 포함돼 있었다. 이 코드를 수용 완료본으로 간주하지 않고 실제 생성과 검증을 수행했다.
- 작업 중 이전 작업이 사용자 지시에 따라 원본의 기존 DVF 변경을 `196dd3d6cdaec7e71b156061a9665e7ed567094e`에 커밋·push했다. 이 작업은 원본에 쓰지 않았고 커밋·push도 하지 않았다. 전달 패치는 그 체크포인트와 원본의 실제 파일 바이트를 기준으로 작성한다. 128파일 복사분을 다시 통째로 적용하지 않는다.

## 1. 발전기 공개 깊이 — 해결

확인된 일반 목적과 특정 설정에서만 가능한 세부 대상을 구분했다. 설정을 지운 채 야외 주유기 공급을 무조건 가능하다고 바꾸지 않았다. 전력 공급 목적을 유지하고, Expanded의 예시는 같은 B41 소비 경로에서 확인된 냉장고·세탁기로 선택했다. 새 설정 대응 체계나 아이템 이름 조건은 추가하지 않았다.

- 이전 E: “가동해 주변 전기 설비에 전원을 공급할 수 있다. 야외 발전기 사용이 허용된 설정에서는 야외 주유기에도 전원을 공급할 수 있다.”
- 현재 C: “가동해 주변 전기 설비에 전원을 공급할 수 있다.”
- 현재 E: “가동해 주변의 냉장고나 세탁기 등 전기 설비에 전원을 공급할 수 있다.”
- EN E: “It can be operated to power nearby electrical equipment such as refrigerators and washing machines.”

범위는 발전기 가동 용도 1개다. 야외 설정과 주유기 관련 근거는 남아 있지만, 그 상세를 공개 문장으로 반복하지 않는다. `ISActivateGenerator.perform` → `IsoGenerator.setActivated`/`setSurroundingElectricity`의 기존 조사와 설치 클래스 해시를 대조했다.

## 2. 석고 가공 재료의 목적 — 해결

단순히 재료명과 같은 가공명을 반복하는 대신, recipe의 명시적 결과와 그 결과에 이미 확인된 기능을 한 단계만 연결한다. `result_purpose`는 결과 아이템의 기능 사실과 observation refs를 보관한다. 입력 재료나 용기가 완성 석고를 직접 바르는 물품인 것처럼 재분류하지 않는다. 모든 후속 용도를 상속하거나 혼합 수량·순서를 공개하지 않는다.

- 석고 가루 이전 C/E: “석고를 섞을 때 재료로 쓸 수 있다.”
- 현재 C/E: “도색할 구조물에 바를 석고를 만드는 재료로 쓸 수 있다.”
- EN C/E: “It can be used to make plaster for preparing structures for painting.”
- 빈 양동이·물 양동이의 같은 가공 관계: “도색할 구조물에 바를 석고를 섞는 용기로 쓸 수 있다.”
- 완성 석고 양동이: 기존 “구조물에 석고를 발라 도색을 준비할 수 있다.”를 유지했다.

실제 변경은 재료 1개와 가공 용기 2개다. 반죽·분무액·약초 찜질제 등 다른 준비 문형의 도구·재료·용기도 함께 읽었다. 요리, 작물 치료, 찜질제처럼 이미 유용한 목적 분야를 전달하는 문장은 일괄 변경하지 않았다. 근거는 `Make Bucket of Plaster`의 명시적 `BucketPlasterFull` 결과와 그 결과의 `plaster_supported_structure` 사실, `ISPaintMenu`/`ISPaintCursor`/석고 timed action의 `paintable=true` 경로다.

## 3. 폭발·화염·연막 장치의 목적과 사용 방식 — 해결

기존 일반 투척 문형 26개를 실제 선언과 B41 소비 코드로 분류했다. 25개는 효과 장치였고, `Football2` 1개는 `IsoBall` 경로였다. 모든 26개에 폭발·화염 효과를 부여하지 않았다. 기존 소음 장치 6개까지 합쳐 총 32개 투척 대상의 C/E를 검수했다.

새 목적 사실은 폭발 피해 12개, 발화 7개, 연막 6개다. 양의 `ExplosionRange`와 `ExplosionPower`, 양의 `FireRange`와 `FirePower`, 양의 `SmokeRange`를 각각 실제 사용 소비 경로와 함께 확인한다. 아이템 ID나 이름으로 효과를 추측하지 않는다.

- 연막 폭탄 이전 C: “움직임 감지, 시간 지연, 원격 작동 기능을 더해 개조할 수 있다. 투척 공격에 쓸 수 있다.”
- 현재 C: “움직임 감지, 시간 지연, 원격 작동 기능을 더해 개조할 수 있다. 연막을 퍼뜨려 좀비가 쫓던 대상을 놓치게 할 수 있다.”
- 현재 E의 목적·방식: “연막을 퍼뜨려 좀비가 쫓던 대상을 놓치게 할 수 있다. 설치하거나 던져서 사용할 수 있다.” 기존 개조 용도도 별도 단위로 남는다.
- 센서형 연막 E: “연막을 퍼뜨려 좀비가 쫓던 대상을 놓치게 할 수 있다. 설치한 뒤 움직임을 감지하면 작동한다.”
- EN 센서형 E: “It can release smoke that makes zombies lose their current target. Once placed and armed, it activates when movement is detected.”
- 폭발 장치의 목적: “폭발로 주변에 피해를 줄 수 있다.” / “It can cause blast damage nearby.”
- 화염 장치의 목적: “주변에 불을 붙이는 데 쓸 수 있다.” / “It can be used to start fires nearby.”

Expanded는 즉시 작동하는 투척, 설치, 센서, 타이머를 확인된 범위에서 구분한다. 일반 연막·소음 장치는 설치와 투척을 모두 유지한다. 타이머형은 “시간을 맞춰 설치하면 지연 작동시킬 수 있다.”로 설명한다. 센서·타이머형의 물리적 투척 요청이 존재한다는 이유만으로 투척 후 효과가 즉시 발생한다고 설명하지 않는다. 그 요청 근거는 유지하고 실제 효과가 연결된 설치 방식으로 설명한다. 원격 연결 용도도 보존한다.

`Football2`에는 “던져서 사용할 수 있다.” / “It can be thrown.”만 남겼다. 소리 유인, 공격 피해, 스포츠 효과를 추가로 추정하지 않았다.

실제 설치 `G:/Program Files (x86)/Steam/steamapps/common/ProjectZomboid`의 클래스에 `javap -c -p`를 실행했다. `IsoTrap`, `IsoGridSquare`, `IsoMolotovCocktail`, `HandWeapon`을 읽고 기존 `IsoGameCharacter`/`IsoZombie` 조사와 설치 클래스 해시를 대조했다. `IsoTrap.triggerExplosion`은 Explosion/Fire/Smoke 분기를 별도로 호출한다. `IsoGridSquare.smoke`는 범위 안 좀비의 `setTarget(null)`과 `ZombieIdleState` 전환을 수행한다. 시야 차단·안전한 탈출·재탐지 방지·효과 지속 시간은 주장하지 않는다. `IsoGameCharacter.Throw`의 Ball/그 외 분기, `HandWeapon.isInstantExplosion`, 설치 후 타이머·센서 경로도 구분했다.

조사 바인딩은 `Iris/build/description/source_support/b41_device_purposes.json`에 있다. 생산 시 게임 설치에 접근하지 않고 스냅샷 및 저장소 Lua 해시를 확인한다.

## 4. 정비 도구의 대상 범주와 역할 — 해결

같은 일반 장착·탈거 문형의 잭·타이어 렌치·드라이버를 검수했다. 추가로 렌치와 엔진 부품을 대조하는 과정에서, 기존 admitted 도구 목록이 세 ID에 한정돼 렌치의 장착·탈거가 누락됐음을 확인했다. Wrench 이름을 목록에 추가하는 대신, 차량 템플릿의 `install`과 `uninstall` 양쪽에 명시된 `keep=true` 도구를 공통으로 연결한다. 실제 템플릿 21개를 설치 B41 파일과 SHA로 대조했으며, 연결 확대로 새로 추가되는 아이템은 렌치 1개였다.

주 손 또는 양손에 요구되는 작업 도구와 보조 손 또는 소지 상태로 요구되는 보조 도구를 구분한다. 잭이 차량을 들어 올리는 애니메이션이나 별도 행동까지 추정하지 않는다. 상세 부품 ID 목록·정비 절차는 공개하지 않는다.

- 잭 이전 C/E: “차량 부품을 장착하거나 탈거하는 데 사용할 수 있다.”
- 잭 C: 이전 개요 유지.
- 잭 E: “타이어, 브레이크 및 서스펜션 장착과 탈거에 필요한 보조 도구로 쓸 수 있다.”
- EN E: “It is a required supporting tool for installing and removing tires, brakes, and suspension parts.”
- 타이어 렌치 E: “타이어 장착과 탈거에 작업 도구로 쓸 수 있다.” / “It can be used to install and remove tires.”
- 드라이버 E의 해당 단위: “전기 부품, 좌석 및 차량 유리 장착과 탈거에 작업 도구로 쓸 수 있다. 연료 탱크 장착과 탈거에 필요한 보조 도구로 쓸 수 있다.”
- 렌치 E의 추가 단위: “브레이크, 서스펜션, 연료 탱크, 배기 부품 및 차체 부품 장착과 탈거에 작업 도구로 쓸 수 있다.”

렌치의 기존 엔진 부품 회수·엔진 수리·무기 용도는 유지했다. C에는 일반 차량 부품 장착·탈거만 추가하고 E의 세부 범주를 복제하지 않았다. 기존 다른 세 도구의 C는 유지했다. 템플릿 요구, `ISVehiclePartMenu.equipRequiredItems`, 설치·탈거 timed action 및 `VehicleCommands.installPart/uninstallPart`의 실제 처리 경로를 근거로 삼았다. 단방향 요구나 소비되는 재료를 이 도구 문형으로 잘못 설명하지 않는 검사도 추가했다.

## 5. Compact 부가 결과 — 해결

붕대 용도 공통 문형 11개와 기록 매체 3개를 검수했다. 붕대 감염과 VHS의 스트레스·공포는 E에 보존하되 C가 해당 부가 결과까지 완결하지 않도록 했다. CD는 이미 감상·지루함 완화 목적을 설명하므로 변경하지 않았다. 위험·효과·조건·수치를 일괄 삭제하는 규칙은 사용하지 않았다.

- 찢어진 천 C에서 “감염된 재료로 상처를 감으면 감염을 일으킬 수 있다.”를 제거했다.
- 현재 C: “응급처치와 의류 수선에 쓸 수 있다. 건축에 재료로 쓸 수 있다. 화염 장치 및 연막 장치를 만들 때도 쓸 수 있다. 모닥불 등의 연료나 불쏘시개로 쓸 수 있다.”
- 해당 E: “상처에 감을 수 있다. 소독해서 쓸 수도 있다. 감염된 재료를 쓰면 상처가 감염될 수 있다.” 화상 처치·부목 재료·의류 수선·제작·연료의 다른 독립 용도는 모두 남는다.
- VHS C: “녹화 영상을 감상하고, 내용에 따라 지루함을 달래거나 기술과 제작법을 배울 수 있다.”
- VHS E에는 재생 매체 조건과 스트레스·공포 결과가 그대로 남는다.

부착물 효과는 전수 비교에서 변경이 없고, 오염수 등 다른 공개 위험도 유지했다. 판자·전자 부품·못·통나무의 최근 C와 E, 부목·기술서 표현을 보존했다. 표백제와 수박은 전체 설명 레코드가 기준본과 동일하다.

## 검증과 보존

최종 생성은 아래 계약 검사의 실제 전수 생산·쓰기 경로로 완료했다. 모든 좌표는 언어·표면별 present 1,976 / absent 129 / failed 0이다. 기존 Expanded fact refs, 원래 사실의 kind/payload, 제작 결과·용도 관계를 보존하고 장치 목적 25개와 렌치의 정비 용도 1개만 사실로 추가했다. 원래 관계에 `result_purpose` 및 선언된 `CanBePlaced` 정보를 더한 것을 별도로 구별해 검사했다. 두 HTML의 접힘 136, 직접 노출 12, 대상·학습 식별자 886은 동일하다. 전체 HTML의 8,420개 원문 좌표와 비교 HTML의 현재 문장이 생성 JSON과 일치한다.

```powershell
uv run --project ./Iris/tooling python -I -B -m pytest --noconftest -c ./Iris/tooling/pyproject.toml ./Iris/build/description/v2/tests/test_layer3_rule_generalization.py ./Iris/build/description/v2/tests/test_layer3_composition.py::test_layer3_composition_contract ./Iris/build/description/v2/tests/test_layer3_description_composition.py::test_layer3_description_composition --basetemp ./.tmp/five-corrections/tests-final-4 -q -s --tb=short
```

종료 코드 **0**, **8 passed in 32.05s**. 미확인·0 속성, 사용 경로 부재, Ball과 타이머·센서 구분, 임의 아이템 이름 변경, 결과 목적 근거 제거, 단방향 정비·소비 재료·보조 손 구분을 포함한다.

```powershell
uv run --project ./Iris/tooling python -I -B -m pytest --noconftest -c ./Iris/tooling/pyproject.toml ./Iris/build/description/v2/tests/test_layer3_product_integration.py::test_current_menu_input_binding --basetemp ./.tmp/five-corrections/binding-final-3 -q -s --tb=short
uv run --project ./Iris/tooling python .tmp/five-corrections/audit.py
powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1
```

현재 메뉴 입력·Expanded 투영 검사 **1 passed in 2.13s, 종료 코드 0**, 전수 보존/HTML 감사 **종료 코드 0**, Lua 문법 **266파일, 종료 코드 0**. 변경 Python 파일의 `git -c core.safecrlf=false -c core.whitespace=cr-at-eol diff --check -- <변경 파일들>`도 종료 코드 0이다. Lua 런타임 파일은 이번 교정에서 새로 수정하지 않았다. Python 작업이며 Java/JS 수정은 없다.

이전 체크포인트의 VHS Compact 기대 불일치는 승인된 표시 깊이에 맞춰 고쳤다. canonical descriptions/blocks 바인딩은 현재 생성물 SHA로 갱신했고, 메뉴 입력 읽기 및 2,105개 Expanded 투영을 패키징 없이 검증했다. 최초 전체 제품 검사는 오래된 canonical 바인딩에서 중단됐으며 패키징 단계에 도달하지 않았다. 전체 제품 패키징 검사를 통과했다고 주장하지 않는다. `ACCEPTED_TOOLTIP` 및 과거 accepted-description 바인딩은 별도 기존 제품의 정체성이므로 이번 생성물로 위조하지 않았다.

검수 중 남은 같은 유형의 누락으로 발견한 렌치까지 반영했다. 현재 교정 범위에서 알려진 미해결 문장 결함은 없다. 실제 게임 폰트·폭에서 툴팁 4줄, 실제 게임 UI 동작·효과 관찰, 새 제품 패키지 검증은 **미검증**이다. 게임 설치·패키징·커밋·push는 수행하지 않았다. 별도 영어 통조림·씨앗 교정, 런타임 전면개편, 미래 모드 어댑터 준비는 수행하지 않았다.

## 최종 바인딩과 적용 파일

- descriptions: `c9e1d15da5fe6179567d60b4e8f622ce11ac6a30ce26f5a48a47839715c7b8e1`
- blocks: `6e977a7281b867470970ba017eda096cd27e373664730686b28e53c823bd6cb7`
- B41 장치 근거 스냅샷: `29d555b32ff7e2740c06e31fce8f149543707b58636e4ddb5bdf428635e78ce0`

전달 파일은 생성 코드 5개(`description_composition_uses.py`, `description_composition_lexicon.py`, `recovery_sources.py`, `recovery_relations.py`, `product_projection.py`), 관련 검사 4개, 장치 근거 스냅샷 1개, 생성 JSON 2개, HTML 2개, 이 보고서·변경 JSON·검수 전문 3개다. 정확한 경로와 전후 파일 해시는 worktree의 `.tmp/five-corrections/delivery/manifest.json`, 적용 패치는 같은 디렉터리의 `five-corrections.patch`에 기록한다. 생성물과 코드·근거를 함께 적용해야 바인딩이 맞는다. 원본이 이후 바뀌었다면 manifest의 기준 해시와 충돌을 먼저 확인해야 한다.

원본 `196dd3d6` 및 실제 파일 바이트를 대조했고, 원본에 대한 읽기 전용 `git apply --check`는 종료 코드 0이다. 원본에는 패치를 적용하지 않았다. canonical JSON 두 개가 한 줄 형식이어서 전체 생성물을 포함하는 텍스트 패치는 약 178 MB다. 이 크기는 수정 아이템 수를 뜻하지 않는다.

적용 명령에는 일회성 `git -c core.autocrlf=false apply ...`를 사용해 전달한 바이트를 유지한다. 별도 임시 경로에서 기본 autocrlf로 적용하는 시험에서는 경로별 `.gitattributes`가 맞지 않아 일부 파일이 CRLF로 바뀌는 것을 발견했다. 이 옵션은 저장소 설정을 영구 변경하지 않는다. 원본 반영 전 manifest 기준 해시를 확인하고, 반영 후에는 17개 `after_sha256`과 생성물 바인딩을 대조해야 한다.
