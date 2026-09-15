# DVF 최신 평가 후속 교정

문장·관계 교정과 전체 재생성을 완료했다. **제련 16 ID의 현재 서바이벌 도달 가능성은 미확정**이며, 이번 결과를 그 기능의 사용 가능성까지 검증한 전체 통과로 해석하지 않는다.

기준본은 앞선 교정이 승인된 descriptions SHA256 `d2bf6b9ebfd12bf54f7b9fd88972d857e59b0823775de19996790588141d136f`이다. 원본 디렉터리의 `c9e1d15d…` 파일과 비교한 누적 변경 수가 아니다.

- 최종 descriptions: `2d338560526369cb83b017a60534c5f074115639510fe6c4aa6c20f27642c0bf`
- 최종 blocks: `b5066f7e4050bd9974a20600c721ac6b877816bed2a40016ed10acee85dab9f3`
- 2105 ID, KO/EN Compact/Expanded 8420좌표. 변경 115 ID / 352좌표.
- present 1976 ID / absent 129 ID. 새로운 absent 없음. 이 수치를 유지하려고 대체 용도를 만들지 않았다.
- 모든 기존 `preserved_fact_refs` 보존. 설명 없는 Expanded 공개 참조 유실 없음.
- 최종 520개 동일 문면 그룹 중, 변경 67개 그룹과 평가 후보·건축 관계 전체를 포함한 **86개 그룹 / 162 ID**의 네 문면을 읽었다. 이전 평가 후보 65 ID 전체를 포함한다. 이번에 변경하지 않은 전체 520개 그룹을 새로 전수 독해했다고 주장하지 않는다.

[변경 좌표·전후 문장·검토 범위 JSON](iris_dvf_latest_correction_2026-09-14_scopes.json), [검토 범위 전문](iris_dvf_latest_correction_2026-09-14_fulltext.txt), [현재 설명 HTML](iris_dvf_descriptions.html), [이번 교정 전후 비교 HTML](iris_dvf_description_review.html).

## 목적과 관계 교정

1. **찜질제 3종**: HealthPanel의 실제 적용 액션, 각 액션의 factor setter, BodyPart의 해당 factor 소비를 연결했다. Comfrey는 골절 회복, Plantain은 긁힘·베임·깊은 상처 회복, Wild garlic은 상처 감염 감소 목적을 설명한다. 원료 약초에는 치료 목적을 상속하지 않는다.
2. **시계 16종**: Classic 8종을 포함해 시간 확인을 독립적으로 인정했다. Clock의 착용품·직접 소지품 검색과 실제 시간 숫자 표시를 확인했다. 손목시계의 좌우 착용과 시간 확인을 연결하고, 탁상형에는 착용을 쓰지 않았다. 가방 내부 재귀 검색·날짜·온도는 추가하지 않았다.
3. **낚싯대 복원**: `Fix Fishing Rod`의 투입 대상과 정상 낚싯대 결과를 복원 관계로 보존했다. 두 언어·두 깊이에 수리 후 다시 낚싯대로 쓸 수 있음을 표현하고 무기 용도도 남겼다. 처리 관계를 제거한 합성 사례에서는 복원 문장을 생성하지 않는다.
4. **음료·조리 바탕**: 음료 18종과 기존 일반 문형 후보 65종을 검토했다. 진입 역할과 evolved recipe의 BaseItem/ResultItem·Name·음료 소비 관계를 활용해 마시기, 맥주·와인을 잔에 따르기, 음료·따뜻한 음료 만들기, 조리 바탕을 구분했다. 컵에 glass 재질을 강요하지 않고, Beer/Beer2/WineInGlass의 중복 마시기를 통합했다. Bowl/Pan/WaterPot는 일반 조리 문장과 구체 대상 문장을 중복하지 않으며, 다른 조리 관계는 열린 예시 범위로, 반죽 용기는 별도 역할로 보존한다. PiePrep의 파이와 달콤한 파이는 파이 범주로 묶었다. 완성 음식의 간단한 추가 재료 설명은 모두 결함으로 처리하지 않았다.
5. **좁은 건축 관계**: 동일 소비 소스에서 확인된 재료 관계 17 ID 전체를 검토했다. Garbagebag의 빗물받이, Doorknob의 문·서랍, Drawer의 서랍 달린 탁자, 끈류의 통나무 벽 등 확인된 목적을 Expanded에 표시한다. Rope의 일반 건축과 구체 대상은 합쳤다. Nails/Plank처럼 넓은 활용에 서랍 한 레시피를 독립 용도로 덧붙이지 않는다. 나무 피켓은 원본 KO/EN 메뉴 명칭과 대조했다.
6. **복합 도구 Compact**: results의 electronics/families/cutting 전체 기능 조합 후처리를 제거했다. uses의 도구 개요도 한 묶음의 일부 기능 때문에 나머지 목적을 삼키는 분기를 제거하고, 각 목적·역할의 근거를 먼저 선택한 뒤 호환되는 작업 문법을 연결한다. 모르는 목적, tool 이외의 역할, 알 수 없는 조건은 해당 요약에 흡수하지 않는 합성 테스트가 있다. 해체 대상의 계단·기둥 조명과 필요한 도구는 Expanded에 둔다. 수박 쪼개기·포장은 개별 활용 상세로 둘 수 있으며, Compact에 모든 기능을 열거하는 규칙은 두지 않았다.
7. **영어 문법**: 깨진 병과 탄약 분해의 결과명에 공통 명사구 렌더러를 적용했다. 빈 병 4종은 `a smashed bottle`을 사용한다. 세척제는 `the body, clothing, and equipment`로 병렬을 정리했다.
8. **로프 층간 이동**: 사용되지 않는 액션의 down 인자만으로 추론하지 않았다. 창문 통과 상태의 로프 검사 → 설치본 `finishclimb.xml`의 climbdownrope 전환 → ClimbDownSheetRopeState의 실제 Z 감소를 확인했다. Rope/SheetRope는 설치 후 층 사이를 오르내리는 목적을 설명한다. 모든 설치점이나 안전한 이동을 보장하지 않는다.

## 독립검수 후 가구 규칙 보완

가구 제작 결과의 구체화를 별개 `construction_targets`의 존재·해석 여부로 켜던 조건을 제거했다. 이제 가구 제작의 재료 역할과 확인된 단일 결과가 자체적으로 구체화를 허용한다. 아직 표현하지 않은 같은 재료 역할의 목공 개요가 해당 용도를 포함할 때만 그 개요에 합친다. 목공 도구 역할은 가구 제작 재료의 목적을 대신하지 않는다.

건축 관계가 전혀 없는 합성 사례, 무관한 미해석 건축 관계를 추가한 사례, 같은 역할의 목공 개요 및 다른 도구 역할 사례를 검증했다. 실제 적용 3 ID(Doorknob/Nails/Plank)의 KO/EN Compact/Expanded를 다시 읽었다. 직전 `716d4c7c…` 검수본과 전체 8420좌표를 비교해 문면 변경 0임을 확인했다. 생성기 코드 식별이 갱신되므로 descriptions 해시는 변경됐다. [추가 검수 기록](iris_dvf_furniture_rule_followup_2026-09-14.json).

## 제련 조사에서 남은 경계

[소스 해시·40개 모루 요구 레시피·16 ID 조사 기록](iris_dvf_latest_forge_reachability_2026-09-14.json), [네이티브 요구 물체 검사 판독](iris_dvf_latest_native_readings_2026-09-14.txt).

`disableFurnaceAnvil = true`가 모루·화로 제작 콜백의 메뉴 진입을 막는다. `ISAnvil.create`는 물체 이름을 `Anvil`로 설정하며, RecipeManager는 주변 IsoObject의 실제 name과 NearItem을 비교한다. 겉모양이 모루라는 사실만으로 제작 시설이 되지는 않는다.

SmithingMag1–4의 학습 레시피 선언과 도서 UI 숨김을 확인했다. 검사한 Lua 배포표에서 해당 잡지의 활성 항목은 찾지 못했다. `doMetalWorkerRecipes` 정의는 남아 있지만 세 호출 지점은 주석 처리돼 있다. 기존 BSFurnace 상호작용 분기와 네이티브 StoneFurnace 객체 팩토리는 존재한다. 이것만으로 기본 월드 시설 배치가 성립하지는 않는다.

**미확정인 연결은 기본 월드의 시설 배치·실제 이름 설정과 현재 서바이벌의 시설/학습 경로이다.** 바이너리 월드 배치를 해독하거나 게임 실행으로 검증하지 않았다. 따라서 관련 사실을 즉시 삭제하지 않았고, 선언만으로 사용 가능하다고 검증한 것으로도 처리하지 않았다. 해당 16 ID는 이 보고서에서 도달 가능성 미확정으로 명시적으로 남긴다.

치료·시계·로프의 설치본 해시와 소스 연결은 `Iris/build/description/source_support/b41_dvf_latest_purposes.json`에 보존했다. 원본 게임·원본 작업 디렉터리는 읽기만 했다.

## 검증 결과

모든 PASS는 아래 실제 명령의 종료 코드 0을 확인한 결과다.

- 관련 Python 검사: **18 passed in 44.46s**, exit 0.
  `uv run --project ./Iris/tooling python -I -B -m pytest --noconftest -c ./Iris/tooling/pyproject.toml ./Iris/build/description/v2/tests/test_layer3_composition.py::test_layer3_composition_contract ./Iris/build/description/v2/tests/test_layer3_description_composition.py::test_layer3_description_composition ./Iris/build/description/v2/tests/test_layer3_rule_generalization.py ./Iris/build/description/v2/tests/test_layer3_dvf_purpose_review.py --basetemp ./.tmp/dvf_latest/furniture-final -q -s --tb=short`
- 현재 메뉴 입력 연결: **1 passed in 2.31s**, exit 0.
  `uv run --project ./Iris/tooling python -I -B -m pytest --noconftest -c ./Iris/tooling/pyproject.toml ./Iris/build/description/v2/tests/test_layer3_product_integration.py::test_current_menu_input_binding -q --tb=short`
- Lua: **266 files OK**, exit 0.
  `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
- 전체 재생성·기준본 비교: `uv run --project ./Iris/tooling python .tmp/dvf_latest/audit.py`, exit 0.
- HTML 검증: `uv run --project ./Iris/tooling python .tmp/dvf_latest/verify_artifacts.py`, exit 0. 현재 8420좌표, 비교 352좌표, 모든 세그먼트·상세 목록 및 메타 해시 일치.
- 코드/테스트 공백 검사: `git -c core.safecrlf=false -c core.whitespace=cr-at-eol diff --check -- Iris/tooling/src/iris_tooling/domains/layer3 Iris/build/description/v2/tests`, exit 0.

현재 product_projection의 DESCRIPTION/BLOCKS만 최종 해시에 연결했다. 과거 채택 기준인 ACCEPTED_DESCRIPTION은 변경하지 않았다. HTML은 문장·데이터 검수용이며 게임 폰트·뷰포트의 실제 적합성 검증이나 제련 실행 검증을 대신하지 않는다. 커밋·배포·원본 디렉터리 반영은 하지 않았다.
