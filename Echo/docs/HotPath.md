# Echo Hot Path 규칙 문서

> **Bundle A 동결 문서** - 이 파일에 정의된 규칙을 위반하는 핫패스 코드 변경은 PR급 사유 필요

## 핫패스 4종 정의

| # | 경로 | 파일 | 메서드 | 호출 빈도 |
|---|------|------|--------|----------|
| 1 | Tick 계측 | `EchoProfiler.java` | `push()`, `pop()` | 매 틱 (60Hz) |
| 2 | Scope API | `EchoProfiler.java` | `scope()`, `startRaw()`, `endRaw()` | 다회/틱 |
| 3 | Spike 기록 | `SpikeLog.java` | `logSpike()` | **조건부** (threshold 통과 시) |
| 4 | Deep Analysis 수신 | Fuse/Nerve → Echo 콜백 | sink 메서드 | 조건부 |

---

## 금지 목록 (Forbidden in Hot Path)

### 절대 금지 (❌ NEVER)
```
PulseServices.*
ServiceLocator.*
EchoConfig.getInstance()
*.getInstance()  // 싱글톤 조회
```

### API/라이브러리 금지
```
Gson, JSON, YAML 파싱
String.format(), String.concat() 반복
new Object() 할당 (루프 내)
File, InputStream, OutputStream
```

### 동기화/블로킹 금지
```
synchronized
BlockingQueue
ReentrantLock
Object.wait() / notify()
Thread.sleep()
```

### 비용 큰 연산 금지
```
StackWalker.walk()
Thread.getStackTrace()
Exception 생성 (throw/catch 포함)
Reflection (Class.forName, Method.invoke)
MXBean 조회
```

### 로깅/출력 금지
```
PulseLogger.*
System.out.println()
System.err.println()
Logger.* (java.util.logging)
```

---

## 허용 연산 (✅ Allowed)

### 필드 접근
- `volatile` 필드 읽기
- `final` 필드 읽기
- 인스턴스 필드 읽기/쓰기

### 원자적 연산
- `AtomicLong.get()`, `incrementAndGet()`, `compareAndSet()`
- `AtomicBoolean.get()`, `set()`, `compareAndSet()`

### 경량 연산
- `System.nanoTime()`
- `System.currentTimeMillis()` (CAS 분기 안에서만)
- 산술 연산 (+, -, *, /)
- 비교 연산 (==, !=, <, >)

### 컬렉션 접근
- `ConcurrentHashMap.get()`, `put()` (락 프리 경로)
- `ArrayDeque.push()`, `pop()`, `peek()`
- `ConcurrentLinkedDeque.addLast()`, `pollFirst()`

---

## 핫패스 코드 규칙

### 1. Early-Exit 필수
```java
EchoConfigSnapshot state = EchoRuntimeState.current();
if (!state.enabled) return;
if (state.lifecyclePhase != LifecyclePhase.RUNNING) return;
// 이후 로직
```

### 2. 예외 발생 금지
- `throw` 문 사용 금지
- `try-catch` 내부에서 로깅/IO 금지
- 외부 콜백은 `safeXxx()` 래퍼로 격리

### 3. Dual-Mode 경고 (디버그 전용)
```java
// 릴리즈: 완전 무음
// 디버그: 세션당 1회만
if (state.debugMode && !reported.getAndSet(true)) {
    System.err.println("[Echo] 단발 경고...");
}
```

---

## 감사 명령 (Audit Command)

핫패스 파일에서 금지 토큰 검색:
```powershell
cd c:\Users\MW\Downloads\coding\PZ\Echo\src\main\java\com\echo
rg -c "PulseServices|ServiceLocator|getInstance\(\)|String\.format|synchronized|BlockingQueue|StackWalker|PulseLogger" measure/EchoProfiler.java aggregate/SpikeLog.java
```

**기대 결과**: 0 hits (또는 비핫패스 영역에서만 hit)

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-08 | 1.0 | Bundle A 초기 동결 |
