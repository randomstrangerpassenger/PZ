# Phase 1 — Artifact / Source / Tracking Classification

> 상위 계획: `docs/Iris/Iris_Refactoring_Plan.md` §5 Generated Artifacts, §6 Change 1, Change 8.
> 측정일: 2026-06-07 (repo root cwd).
> 상태: Phase 1 분류(SEALED 사실관계). 확정판은 Phase 8 `phase8_artifact_source_classification.md`.

이 문서는 (A) runtime sealed data, (B) `Iris/output` build 산출물, (C) `Iris/build/package` package 산출물의
source/artifact 성격과 git tracked 정책을 분류한다. §5 Generated Artifacts 목록을 실측으로 재검증한 결과
**누락/추가 없이 전수 일치**했다(36개 sealed runtime 파일 전부 존재·tracked).

## A. Runtime Sealed Data — `Iris/media/lua/client/Iris/Data/`

- 분류: **generated runtime artifact (sealed_evidence)**. generator가 emit하며 **수동 편집/의미 수정 금지**(governance §11, 계획 §8 Sealed Artifact Surface).
- tracked: **36/36 tracked**, working tree clean. (15 root entrypoint + 11 Layer3 chunk + 9 UseCase chunk + `RequirementsLookup.lua` = 36; `Iris/Data` tracked 총수 36과 일치 → 미추적 generated data 없음.)
- chunk 수: Layer3 = **11**(`baseline_layer3_chunk_count`), UseCase = **9**(`baseline_usecase_chunk_count`).
- disposition: `keep_active` (mutation 금지, SHA 보호). Phase 8/9a는 아래 SHA 대비 변동 0을 검증한다.

### SHA-256 Reference Baseline (2026-06-07, Phase 8/9a 비교 기준)

`AGGREGATE_MANIFEST_SHA256 = A425385417808AD6756FAE435DC365725CD33B6D43664B585B77C243559F4559`
(정렬된 `상대경로  SHA256` 라인들의 UTF-8 SHA-256. 36개 파일 중 하나라도 변하면 aggregate가 달라진다.)

| Path | SHA-256 |
|---|---|
| Data/IrisCapabilities.lua | E9B76536BD56B481AA4B0CB094F20010352D4DED3E10ADF7E09B86C4239B04C0 |
| Data/IrisClassifications.lua | 98D9CE3162703333B02DD48D62F8739E4606EADA321A7731A35E2E586F033563 |
| Data/IrisContextOutcomes.lua | EFF2B494E30A68C89C216F12813131A9C287F36E0FE97A8929DCB06B948BDA47 |
| Data/IrisData.lua | 17ED88F3FB1ED5B6AB96B021442DFB8E34B757D34B0C0EA05508876F855296B1 |
| Data/IrisFixingIndex.lua | 51390A0B7221E12ECDA021453762D739EF06833D676D3924EF077CC49FB8BE6B |
| Data/IrisFixingIndexData.lua | 19E7046F993BFC8E42758EB168B7FDC0FD857D8ACF7EC3E287C9AC6849801FB3 |
| Data/IrisLayer3DataChunks.lua | FA9F74938023CC81A08E12BC271A22F65BEFB5DF36C0A18E85550882C82F6E2C |
| Data/IrisLayer3DataChunks/Chunk001.lua | 08373C2A0E2F6FF572021F2F82D1B322316E7886A8876664D65F022CB764B7DD |
| Data/IrisLayer3DataChunks/Chunk002.lua | 37E72049CEB83D294F52D9BB86936A3A3E05942CDAA037865532338CFAEF4764 |
| Data/IrisLayer3DataChunks/Chunk003.lua | 562C7C18AEF25538EF341764DA4A5635313352212F1BCE515B20C5DCCC90E0B9 |
| Data/IrisLayer3DataChunks/Chunk004.lua | 42753E063661679583C3430ACC6BC52EC6F47D873CBF4685DACDB603A964E440 |
| Data/IrisLayer3DataChunks/Chunk005.lua | 89C7D39902FF83166F4CFB8CEA4225359E86B62750703CFC7C4F15B44CCE5A5E |
| Data/IrisLayer3DataChunks/Chunk006.lua | 5942559C4927AB8ED948FED42F73E362B26E35D180E2206B745CAAA98ED20C09 |
| Data/IrisLayer3DataChunks/Chunk007.lua | 19661A52A3418F413AD49C7DF474A2F221A0D5C751232F1B9B3083768074966B |
| Data/IrisLayer3DataChunks/Chunk008.lua | 0DF3875BD9CD109BF70B50B4C847C99E56437D1AB8183C1A814C797A754ED924 |
| Data/IrisLayer3DataChunks/Chunk009.lua | ABBE34D842D2D1162A5828E3F3E3147CB93F1E991F89DA3009D2BB81ADD82729 |
| Data/IrisLayer3DataChunks/Chunk010.lua | 954ED61CA9F9A08FB9818A38C91925356901561B9D3CD3DD9DFD5D91BD359997 |
| Data/IrisLayer3DataChunks/Chunk011.lua | 8E0311E7D6FB020056E9FB74FBC546DCE898668F4ED7C60561E7538F5BC9D179 |
| Data/IrisMoveablesIndex.lua | BAC7FFD2A73E73CAD560AD9E84D1F007765D28D9E641DACA51A2883A50EE5E3A |
| Data/IrisMoveablesIndexData.lua | FE1B18D98CF9D6DA6D46536B60CF0242492079867321AC821800A9A9ED5447A8 |
| Data/IrisRecipeIndex.lua | B83E67D52EF5F73F84C901B1448EE480138B3D65B4ABE651940FA82883A97DAA |
| Data/IrisRecipeIndexData.lua | 4C88231A8CCB6B5BA6E3C35661D9CE80770A63AE071DCB4A4DF397E0C2A806E9 |
| Data/IrisTranslationData.lua | 19689D95E951F6FC296D7B5C92DEFF7870D462659D713939B4223D4C78E2694B |
| Data/IrisUseCaseDescriptions.lua | A2BFBBB2091BC7955E2C89A65AFBA456C9350FC3F93DF81AC3EB5CDA805F2D44 |
| Data/IrisUseCaseLabelMap.lua | 32EDC34CBE06F0A1F7346AB05581F3DA67697D16985A48912151958DC482BF42 |
| Data/layer3_renderer.lua | 7F50F16D34ABE7AF4F4C192BCFC9E8251B33108B9E6CBC06C69124FE60B897DD |
| Data/UseCaseDescriptions/Chunk001.lua | 422C80416ABD233C6DD09A15E47D8198EC5512D601AE05B50CF11BFB2DEF6257 |
| Data/UseCaseDescriptions/Chunk002.lua | D49A56428605D03F721DE83953FED2DDBE4A6199A3260FAD6D86AF5B7747F6FC |
| Data/UseCaseDescriptions/Chunk003.lua | 113C0B2518CB6DCE26E51CF2DA737FC8EA693DCA53B5C04A885CBC0DCDF65DB1 |
| Data/UseCaseDescriptions/Chunk004.lua | 6D7CED5C826A5CF694F68D1DEC0D82C102B3F592C0605D9E762CEFAEB4464E95 |
| Data/UseCaseDescriptions/Chunk005.lua | F5C0879084A24572926B829B5F16CAE058C6AF372CD0609F3E9A538496B9880B |
| Data/UseCaseDescriptions/Chunk006.lua | EA5EAA52BC642A1AAFBDD115C72FE1EE3EA3C936077C29A5804C1396D1685533 |
| Data/UseCaseDescriptions/Chunk007.lua | 7624D40E2AD363EF460BED8F6F01E622F4E3CC92BF4F43FBFAE83A6676007683 |
| Data/UseCaseDescriptions/Chunk008.lua | DD325EF435F7A19BDD48F6C07D8C6C37DE3BD1EE361A5536DBD7610E01540C27 |
| Data/UseCaseDescriptions/Chunk009.lua | 2C135C55FE7B1B1344EE3092EE902479D02BE4F5ACBE7D163A953514F73124E8 |
| Data/UseCaseDescriptions/RequirementsLookup.lua | 9E2368BF50093DFEC028CCF7A52D4AC0EE9B4407FF3CFBFC9715955F295CA696 |

## B. Build Outputs — `Iris/output/`

- tracked: **47/47 tracked**, working tree clean(`git status --short -- Iris/output/` 빈 출력).
- 분류: 대부분 **generated build artifact**. 일부는 downstream generator의 **source-like 입력**으로 재사용(아래).

| 분류 | 파일(예) | 성격 |
|---|---|---|
| generated runtime Lua (build-side 사본) | `IrisClassifications.lua`, `IrisData.lua`, `context_outcomes.lua`, `IrisManualOverrides.lua` | runtime `Iris/Data/`의 build-side 대응물. source ↔ artifact 미러 관계는 Phase 8에서 generator manifest와 연결 |
| source-like 재사용 입력 | `recipe_index.v2.4.json`, `recipe_requirements_index.v2.4.json`, `recipe_nav_registry.v2.4.json`, `action_requirement_index.v2.4.json` | INVENTORY.md P1-1: index 생성기의 입력으로 재사용(reusable as source data) |
| v2.4/v2.5 evidence/분류 JSON | `evidence_candidates.v2.4.json`, `evidence_decisions.v2.4.json`, `recipe_evidence_decisions.v2.4.json`, `field_registry.v2.4.json`, `descriptions_by_fulltype.v2.4.json`, `usecases_by_fulltype.v2.4.json`, `requirements_by_fulltype.v2.4.json`, `recipe_require_fields.v2.5.json` 등 | 빌드 파이프라인 generated 중간/최종 산출물 |
| 리포트 / 통계 | `build_report.json`, `build_report.md`, `diagnostics.json`, `diagnostics.v2.4.json`, `grouping_stats.json`, `layer3_stats.json`, `layer3_by_fulltype.json`, `layer3_validation_report.json`, `regression_test_report.json`, `validation_report.json`, `scope_outside_fulltypes.json`, `layer3_unregistered.txt` | generated 리포트(behavior 아님, evidence) |
| provenance/SHA 기록 | `layer3_build_sha.txt` | build SHA 기록 |
| legacy 스냅샷 | `legacy_root/` (디렉토리) | 과거 root 산출물 이관본(ENTRYPOINTS.md "Completed root artifact moves") |

> Phase 8 과제: 위 "source-like 재사용 입력" vs "순수 generated"의 경계를 generator manifest로 확정하고,
> 어떤 항목이 tracked source baseline이고 어떤 항목이 재생성 가능한 artifact인지 분리 기록.

## C. Package Output — `Iris/build/package/`

- tracked: **0 tracked**. `git check-ignore` → `.gitignore:6` 규칙 `Iris/build/*`에 의해 **ignored**.
- 디스크 내용: `Iris/`(패키지 미러 트리) + `Iris.package_manifest.sha256.json`.
- 분류: **package output**. tracked source와 이미 분리되어 있음(의도된 상태). Phase 8은 이 분리가 정책으로
  문서화되어 있는지 확인하고 `.gitignore` allowlist를 round/evidence 기준으로 정리(only-if-required).

## Tracked Policy 요약 & Phase 8 함의

| Surface | 디스크 | tracked | ignore 규칙 | Phase 1 disposition |
|---|---|---|---|---|
| `Iris/media/lua/client/Iris/Data/` (sealed runtime) | 36 | 36 tracked | 미적용 | `keep_active`, SHA 보호 |
| `Iris/output/` (build 산출물) | 47 | 47 tracked | 미적용 | generated, 일부 source-like(Phase 8 세분) |
| `Iris/build/package/` (package 산출물) | 존재 | 0 tracked | `.gitignore:6 Iris/build/*` | package output, 분리 유지 |

- `.gitignore`의 `Iris/build/*`는 `Iris/build` 직하를 ignore하지만, 이미 tracked인 build script(73개)는 negation/기존 추적으로 유지된다. 이 tracked/untracked 혼재의 정합성 정리는 Change 8 본과제(`.gitignore` only-if-required 수정).
- §5 Generated Artifacts 목록은 실측과 전수 일치 → 보호 범위 확장 불필요(Phase 1 deliverable 충족).
