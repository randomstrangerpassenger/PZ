# Pulse Ecosystem Logging Convention

> **Phase 4**: 로그 통일 가이드라인

## 현재 상태

| 모듈 | System.out 사용 | PulseLogger 사용 |
|------|----------------|-----------------|
| Echo | 200+ | 일부 |
| Fuse | 50+ | 대부분 |
| Pulse | 30+ | 대부분 |

---

## 표준 API

### PulseLogger

```java
import com.pulse.api.log.PulseLogger;

// 레벨별 로깅
PulseLogger.debug(LOG, "Detail message");
PulseLogger.info(LOG, "Status message");
PulseLogger.warn(LOG, "Warning message");
PulseLogger.error(LOG, "Error message", exception);

// 모듈 태그 상수
private static final String LOG = "Echo"; // 또는 "Fuse", "Pulse"
```

### 마이그레이션 패턴

| 기존 | 신규 |
|------|------|
| `System.out.println("[Echo] ...")` | `PulseLogger.info(LOG, "...")` |
| `System.err.println("[Echo] ...")` | `PulseLogger.error(LOG, "...")` |
| `System.out.printf(...)` | `PulseLogger.info(LOG, String.format(...))` |

---

## 마이그레이션 우선순위

### 🟥 HIGH (즉시)
- **EchoConfig** - 설정 로드/저장 메시지
- **EchoMod** - 초기화 메시지

### 🟧 MEDIUM (다음 릴리즈)
- **EchoProfiler** - 상태 변경 로그
- **EchoReport** - 리포트 저장 로그

### 🟩 LOW (점진적)
- **SelfValidation** - 검증 출력 (의도적 콘솔 출력)
- **ReportDiff** - CLI 도구 (stdout 유지 가능)

---

## 예외 사항

### CLI 도구
`com.echo.tool.*` 패키지는 stdout 사용 허용 (CLI 출력 목적)

### Self-Validation 출력
사용자에게 직접 표시하는 진단 메시지는 System.out 허용

---

## 점진적 마이그레이션 체크리스트

```
[ ] EchoConfig.java (15개)
[ ] EchoMod.java (5개)
[ ] EchoProfiler.java (10개)
[ ] EchoReport.java (20개)
[ ] EchoProfilerProvider.java (6개)
[ ] 기타 (150+개) - 점진적
```

---

## 참고

- PulseLogger는 내부적으로 레벨 필터링 지원
- 디버그 모드에서만 debug 로그 출력
- 프로덕션에서 info 이상만 출력
