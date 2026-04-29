# Description Validation Framework (DVF) — 계약 문서

**버전**: 1.0
**상태**: FINAL
**적용 대상**: Iris 모듈 — 3계층 개별 아이템 설명 (Individual Item Description)
**상위 규약**: Philosophy.md

---

## 1. 목적

DVF는 Iris 아이템 설명의 3계층(개별 아이템 설명)에 대해 **오프라인 빌드 시 텍스트의 구조·역할·언어 품질을 검증**하는 체계다.

### 1.1 한 줄 요약

> **수동 작성된 3계층 문장을 T-Gate가 오프라인에서 검증한 뒤, 확정 산출물을 런타임이 조용히 렌더만 한다.**

### 1.2 명칭 근거

- **DVF** = Description Validation Framework. 기존 Q-Gate(Quality Gate)와 역할 분리.
- **T-Gate** = Text 검증 게이트. T1~T4. "D-Gate"는 Q-Gate와 접두사 혼동 가능성이 있어 T를 채택.

### 1.3 데이터 소스 경로 변경 기록

초기 합의는 경로 A(속성 기반 자동 추출)였으나, v1 검토에서 3개 모델이 만장일치로 "속성값을 템플릿으로 찍어내는 자동 문장은 3계층의 본질(고유한 개별 설명)과 충돌한다"고 지적하여, **수동 작성 단일 경로로 전환**했다.

---

## 2. 4원칙

1. **계층은 독립적이다.** 3계층은 다른 계층의 구조적 역할을 대체하지 않는다.
2. **3계층은 침묵할 수 있다.** 침묵은 오류가 아니라 의도된 상태이며, 산출물에서 해당 fulltype이 부재하는 것으로 표현된다.
3. **3계층 문장은 자연스러운 한국어여야 한다.** 번역투, 레이블체, 내부 키 노출은 금지.
4. **오프라인 확정, 런타임 렌더 전용.** 런타임에서 문장 생성·수정·보정·폴백은 절대 금지.

---

## 3. 데이터 흐름

```
layer3_registry.json (수동 작성)
        │
        ▼
    T-Gate 검증 (T1→T2→T3→T4)
        │
        ▼
    컴파일 (active만 추출, fulltype 정렬)
        │
        ▼
layer3_by_fulltype.json (런타임 산출물)
        │
        ▼
layer3_renderer.lua (렌더 전용)
```

---

## 4. 레지스트리 계약

### 4.1 필드 정의

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `fulltype` | string | ✅ | 대상 아이템 (예: `Base.TinOpener`) |
| `status` | `"active"` \| `"silent"` | ✅ | 출력 상태 |
| `kind` | enum \| null | ✅ | 문장 성격 분류 |
| `text_ko` | string \| null | ✅ | 한국어 문장 |
| `anchors` | string[] | ✅ | 작성자 참고용 증거 참조 (형식만 검증, 실존 미검증) |
| `notes` | string | ✅ | 비출력 메모 |

### 4.2 kind enum

`identity`, `distinct_use`, `constraint`, `exception`, `variant_note`

### 4.3 status별 필드 계약

| status | kind | text_ko | anchors |
|---|---|---|---|
| `active` | enum 필수 | 비공백 문자열 필수 | 자유 |
| `silent` | 반드시 `null` | 반드시 `null` | 반드시 `[]` |

### 4.4 침묵의 의미

- **명시 침묵**: 레지스트리에 `status=silent` 엔트리 존재. "이 아이템은 의도적으로 3계층을 비움"
- **암묵 침묵**: 레지스트리에 엔트리 없음. "아직 3계층을 작성하지 않음"
- 두 경우 모두 산출물에 fulltype이 존재하지 않으며, 런타임은 아무것도 출력하지 않는다.

---

## 5. 산출물 계약

### 5.1 컴파일 산출물 (`layer3_by_fulltype.json`)

- active 엔트리만 포함. silent 및 미등록 fulltype은 미포함.
- `status`, `anchors`, `notes`는 미포함. `kind`와 `text_ko`만 포함.
- fulltype 사전순 정렬 (결정론적).

### 5.2 런타임 계약

```
entry = descriptions[fullType]
if entry and entry.text_ko then
    render(entry.text_ko)
end
-- 그 외: 아무것도 하지 않음
```

**절대 금지**: 문장 수정, 필터링, 재정렬, 추가, 폴백 생성, 다른 계층 데이터 보정.

---

## 6. T-Gate 체계

### 6.1 아키텍처

T-Gate는 **공통 검증 엔진** 위에서 동작하며, 계층별 정책 내용(금지 어휘, 패턴, 임계값)은 `layer3.profile.json`에서 읽는다. 문자열 정규화, 중복 검사, fulltype 조회, 리포트 생성, 컴파일 절차 등 엔진 공통 동작은 코드에 고정한다.

스키마 검증은 JSON Schema 파일을 사용하지 않고, `t1_structural.py` 내부의 typed validator로 수행한다.

### 6.2 게이트 영역 분리

| 게이트 | 질문 | 담당 영역 |
|---|---|---|
| T1 | 구조가 유효한가? | 스키마, fulltype 실존/중복, status-필드 정합성, silent 계약, kind enum, anchors 형식 |
| T2 | 다른 계층 역할을 침범하는가? | 줄바꿈, 글머리기호, 색인헤더, 비교급, 분류노출 |
| T3 | 자연스러운 한국어인가? | 종결부호, 내부키 노출, 금지어휘, 번역투, 레이블체 |
| T4 | 다른 계층과 중복되는가? | 유사도 비교 (**WARN 전용**) |

T2와 T3에 동일 키워드를 중복 등록하지 않는다.

### 6.3 순차 실행

```
T1 (FAIL→중단) → T2 (FAIL→중단) → T3 (FAIL→중단) → T4 (항상 실행, WARN만)
```

### 6.4 T1 FAIL 조건

- 스키마 위반
- fulltype이 전체 아이템 목록에 부재
- fulltype 중복
- `status=active` + (`text_ko`가 null/빈문자열/공백)
- `status=silent` + (`kind ≠ null` 또는 `text_ko ≠ null` 또는 `anchors` 비어있지 않음)
- `kind` enum 위반
- anchors 형식 오류 (문자열 배열, 각 항목 비공백)

### 6.5 T2 FAIL / WARN 조건

FAIL:
- 줄바꿈
- 글머리 기호 (`^[\s]*[-•·]\s`, `^[\s]*\d+[.)]\s`)
- 색인 헤더 (프로파일 `index_header_patterns`)
- 비교급/우열 (프로파일 `comparison_patterns`)
- 분류 노출 (프로파일 `classification_patterns`)

WARN:
- 쉼표 구분 항목 ≥4개 (쉼표 3개 이상)

### 6.6 T3 FAIL / WARN 조건

FAIL:
- 종결 부호 없이 종료 (`.`, `!`, `?` — 한국어 서술형 종결 포함)
- 내부 키 노출 (프로파일 `key_leak_patterns`: `uc\.`, `Base\.`, `module\.`)
- 슬래시 3개 이상
- 금지 어휘 (프로파일 `forbidden_terms`)
- 목록형 레이블체 (서술어 없음)

WARN:
- 길이 위반 (프로파일 `min_length`, `max_length`)
- 번역투 (프로파일 `warn_patterns.translationese`). 정규식 한계로 인해 WARN 운영. 빌드 미차단.
- `~할 수 있다` 3회 이상 반복

### 6.7 T4 (WARN 전용)

- 1·2계층 산출물 부재 시 SKIP (로그만)
- SequenceMatcher 유사도 ≥70% → WARN
- 50~70% → INFO
- 빌드를 중단하지 않음

---

## 7. 빌드 무결성

### 7.1 결정론 검증

`build_layer3.py --verify-determinism` 플래그로 2-run SHA 비교. FAIL 시 빌드 중단.

### 7.2 회귀 지표

| 지표 | 정책 |
|---|---|
| `active_count` | 상한 WARN (예: PR당 +10) |
| `silent_count` | 정책 없음 |
| `total_entries` | 상한 WARN |

래칫(감소 불가) 없음. 수동 작성은 작성자 판단 우선.

### 7.3 미작성 리포트

`layer3_unregistered.txt`에 전체 아이템 목록 중 레지스트리에 미등록된 fulltype을 출력. 빌드 차단 조건 아님.

---

## 8. anchors 계약

- 형식만 검증 (문자열 배열, 비공백). 참조 대상 실존은 미검증.
- 산출물에 미포함. 레지스트리 내부 작성자 참고용.
- 향후 필요 시 별도 합의로 검증 범위 확대.

---

## 9. Q-Gate와의 관계

DVF는 기존 Q-Gate(Q1~Q5)와 **완전히 독립**된 체계다.

- DVF 산출물을 Q4(frozen_sha)나 Q5(회귀 diff)에 등록하지 않는다.
- 결정론 검증과 회귀 지표는 DVF 자체 빌드 스크립트에서 처리한다.

---

## 10. 교차 언급 규칙

3계층과 다른 계층 사이의 교차 언급은 **허용**한다.

- 3계층 텍스트에서 다른 계층의 소재를 보조적으로 언급하는 것은 자연스러운 한국어 서술에 해당.
- 단, 다른 계층의 구조적 역할을 대체하는 것은 금지 (T2에서 검출).

---

## 변경 이력

| 버전 | 날짜 | 내용 |
|---|---|---|
| 1.0 | 2026-03-07 | 최초 작성. v3.1 확정판 기준. |
