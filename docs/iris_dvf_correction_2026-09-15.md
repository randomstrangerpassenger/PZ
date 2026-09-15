# Iris DVF 2026-09-15 교정 결과

기준본 `2d338560526369cb83b017a60534c5f074115639510fe6c4aa6c20f27642c0bf` 대비 38개 항목, 108개 좌표를 교정했다. 전체 2,105 ID / 8,420 좌표를 재생성했고, 1,976 present / 129 absent를 유지했다. 새 absent와 설명되지 않은 Expanded 근거 유실은 없다. 기존 preserved_fact_refs는 모든 ID에서 보존됐다.

## 교정 내용

- 실제 배치 속성 PickUpTool/PlaceTool → 도구 등록 → pickup/place 소비 경로를 연결해 Hammer, Screwdriver, Shovel, Wrench, PipeWrench의 이동·설치 용도를 복원했다. Crowbar/Cutter에는 추정 용도를 추가하지 않았다.
- 바닥 혈흔 청소는 표백제와 수건·청소 도구의 결합 관계를 Expanded에 반영했다.
- 사용자 지시에 따라 Bleach 섭취 문장은 KO ‘마실 수 있다.’ / EN ‘It can be drunk.’로 그대로 유지했다. 섭취 결과 경고는 추가하지 않았다. 설정에서 허용될 때 음식에 독을 섞는 별개의 용도만 native 후보·메뉴 조건·결과 변경 근거로 추가했다.
- 복합 칼 도구의 동물·생선 손질과 음식 나누기, 목재 가공의 투입·결과 관계를 나타냈다. 같은 입력의 결과 대안과 서로 다른 가공 관계를 구분했다. 후속 결과물의 사용처를 원래 도구의 용도로 승격하지 않았다.
- 정비 잡지 3종의 Expanded에 일반·가족용 차량, 승합차·픽업 트럭, 고성능 차량 구분을 넣고 읽기 중복 문장을 제거했다. Compact 개요는 유지했다.
- Bandaid와 같은 상처 처치 관계의 공통 동사를 ‘상처를 덮어 처치’로 정리했다. 수박만 확인된 도끼 4종·톱 2종의 Compact는 그 대상을 직접 표현했다.
- 새 모듈은 날짜 대신 역할을 나타내는 `purpose_participant_relations.py`로 정리했다. 개별 ID의 전체 특징 조합에 따른 문장 분기는 추가하지 않았다.

## 근거와 미확정 범위

`Iris/build/description/source_support/b41_dvf_relations_2026-09-15.json`의 14개 소비자 소스를 설치본과 바이트 비교했다. SHA-256: `aee91a325cc1928897a1d135970e1c9cde15582a8e3d95b6601836daeef856e9`. 실제 배치 속성과 native class 해시를 함께 연결했다.

제련·화로 검토를 16개에서 24개로 확장했다. Bellows 동작, Coal/Charcoal 연료 소비, BookBlacksmith1–5의 읽기 및 배율 적용을 확인했다. Coal의 OBSOLETE 선언도 기록했다. 숯의 독립적인 모닥불 연료 용도와 책의 읽기 용도는 유지했다. 기본 생존 세계에서 제련 시설과 기술 진행 경로에 실제 접근 가능한지는 여전히 **UNRESOLVED**다. 텍스트 검색 부재로 불가능을 단정하지 않았고 선언만으로 생존 접근 가능성을 확정하지 않았다. 기존 화로가 있다는 조건의 동작 증거와 시설 획득 증거를 구분했다. 상세: [24개 근거 감사](iris_dvf_forge_reachability_2026-09-15.json).

## 문장 및 산출물 검수

전체 523개 고유 문장군 중 변경 29개와 요청 범위·건축 관계 회귀 범위를 합친 62개 문장군(76 IDs)의 KO/EN Compact/Expanded를 직접 읽었다. 수정 후 변경 문장군도 다시 읽었다. 전체 좌표의 상태·근거 참조를 자동 비교했다. 이 검수는 게임 실행이나 게임 폰트 렌더 검증을 뜻하지 않는다.

- [현재 설명 HTML](iris_dvf_descriptions.html): 8,420 좌표.
- [기준본 대비 HTML](iris_dvf_description_review.html): 모든 변경 좌표.
- [범위·변경 전후·전체 문장군](iris_dvf_correction_2026-09-15_scopes.json).
- [직접 읽은 전체 문장](iris_dvf_correction_2026-09-15_fulltext.txt).

최종 descriptions SHA-256: `8e1eda45bb75482d69cb352a4676232b0824debc4c0be2a3d173d5c50b933c03`.
최종 blocks SHA-256: `860f6287c85b3eaf17de628b6b081eae5a4deb6b8bdac8280346454e27a27fb6`.
현재 메뉴의 DESCRIPTION/BLOCKS 바인딩을 갱신했다. ACCEPTED_DESCRIPTION은 보존했다.

## 검증

모든 아래 검증은 명시한 명령의 종료 코드 0을 확인했다.

- 조합·설명·일반화·목적 회귀: **19 passed, 40.97s**.
  `uv run --project ./Iris/tooling python -I -B -m pytest --noconftest -c ./Iris/tooling/pyproject.toml ./Iris/build/description/v2/tests/test_layer3_composition.py::test_layer3_composition_contract ./Iris/build/description/v2/tests/test_layer3_description_composition.py::test_layer3_description_composition ./Iris/build/description/v2/tests/test_layer3_rule_generalization.py ./Iris/build/description/v2/tests/test_layer3_dvf_purpose_review.py --basetemp ./.tmp/dvf_0915/final2 -q -s --tb=short`
- 현재 메뉴 바인딩: **1 passed, 2.03s**.
  `uv run --project ./Iris/tooling python -I -B -m pytest --noconftest -c ./Iris/tooling/pyproject.toml ./Iris/build/description/v2/tests/test_layer3_product_integration.py::test_current_menu_input_binding -q --tb=short`
- Lua 문법: **266 files OK**.
  `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1`
- HTML 메타데이터·8,420/108 좌표·모든 세그먼트 및 펼침 목록 본문 일치, 원본 descriptions 불변.
  `uv run --project ./Iris/tooling python .tmp/dvf_0915/verify_artifacts.py`
- Windows CRLF를 줄끝으로 취급한 diff 공백 검사 통과.
  `git -c core.fsmonitor=false -c core.safecrlf=false -c core.whitespace=cr-at-eol diff --check -- Iris/tooling/src Iris/build/description/v2/tests`

중간 검증의 예전 문장 기대값 불일치 두 건은 새 문장의 의미를 검증하도록 갱신한 뒤 위 최종 명령으로 재검증했다.

원본 디렉터리의 descriptions SHA-256은 `c9e1d15da5fe6179567d60b4e8f622ce11ac6a30ce26f5a48a47839715c7b8e1`로 유지됐다. 원본 병합·배포는 수행하지 않았다.

iris_dvf_descriptions.html SHA-256: `f9fd9801514764e40b8b405beec0859f2ff0054b58455f8a92cfd25990319835`.

iris_dvf_description_review.html SHA-256: `493a697b5bd2496162272a4db3fadaf07bb868a94be8b8dd734d19d74d3b2453`.
