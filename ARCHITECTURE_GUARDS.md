# Pulse Architecture Guards

이 문서는 Philosophy.md에 정의된 Pulse 생태계 설계 원칙을 **빌드 레벨에서 강제**하기 위한 가드 규칙을 정의합니다.

## 핵심 원칙 (Philosophy.md 기반)

### 1. 단방향 의존성 (Hub → Spoke 금지)
- ✅ Echo, Fuse, Nerve → Pulse 의존 허용
- ❌ Pulse → Echo, Fuse, Nerve 의존 **금지**

### 2. Hub & Spoke 구조 (Spoke 간 직접 의존 금지)
- ❌ Echo ↔ Fuse 직접 참조 **금지**
- ❌ Echo ↔ Nerve 직접 참조 **금지**
- ❌ Fuse ↔ Nerve 직접 참조 **금지**
- ✅ Spoke 간 통신은 반드시 Pulse(Hub)를 경유

### 3. 정책 혼입 금지
- ❌ Pulse에 최적화 알고리즘/정책 코드 추가 **금지**
- ❌ `post(event)` 류 중앙 라우팅 API 추가 **금지**
- ✅ Pulse는 "얇은 플랫폼/무정책/무모드성 기능"만 제공

---

## 빌드 강제 메커니즘

### ArchUnit 테스트 (자동 검증)

**위치**: `Pulse/src/test/java/com/pulse/architecture/HubSpokeBoundaryTest.java`

| 규칙 | 설명 |
|------|------|
| `pulse_should_not_depend_on_spoke_modules` | Pulse → Spoke 의존 금지 |
| `echo_should_not_depend_on_other_spokes` | Echo → Fuse/Nerve 금지 |
| `fuse_should_not_depend_on_other_spokes` | Fuse → Echo/Nerve 금지 |
| `nerve_should_not_depend_on_other_spokes` | Nerve → Echo/Fuse 금지 |

### Gradle `architectureCheck` 태스크

**위치**: `Pulse/build.gradle`

- 하위 모드 import 검출
- 삭제된 정책 클래스 참조 검출
- `check` 태스크에 연결됨

---

## Thin Mixin 규칙

| 허용 ✅ | 금지 ❌ |
|---------|---------|
| 훅/가드 호출 | 분기/루프 |
| 델리게이트 위임 | 데이터구조 생성 |
| 단순 리턴 | 정책 판단 |
| | 비즈니스 로직 |

---

## PR 리뷰 체크리스트

- [ ] Pulse가 이벤트를 분류/라우팅하지 않는다
- [ ] Pulse에 정책/임계값/판단이 추가되지 않는다
- [ ] Mixin은 훅+위임만 (Thin Mixin)
- [ ] Spoke 모듈 간 직접 참조가 없다
- [ ] ArchUnit 테스트 통과

---

## 위반 시 조치

1. **빌드 실패**: ArchUnit 테스트 또는 `architectureCheck` 태스크에서 차단
2. **PR 반려**: 리뷰 체크리스트 미통과 시
3. **즉시 롤백**: 프로덕션 배포 후 발견 시
