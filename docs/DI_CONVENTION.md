# Pulse Ecosystem DI Convention

> **Phase 2**: DI 일관성 확보 및 규약 확정

## 핵심 원칙

### 1. Hybrid DI 패턴

```java
public static MyService getInstance() {
    // 1. Try ServiceLocator (Pulse 환경)
    try {
        var locator = PulseServices.getServiceLocator();
        MyService service = locator.getService(MyService.class);
        if (service != null) {
            return service;
        }
    } catch (Exception ignored) {
        // Pulse not loaded
    }
    
    // 2. Fallback (테스트/독립 실행)
    if (INSTANCE == null) {
        INSTANCE = new MyService();
    }
    return INSTANCE;
}
```

> [!CAUTION]
> **getInstance() fallback 제거 금지!**
> 테스트 및 독립 실행 시 Pulse가 없어도 동작해야 함.

### 2. 서비스 등록 시점

| 시점 | 위치 | 설명 |
|------|------|------|
| Bootstrap | `PulseBootstrap.init()` | 코어 서비스 등록 |
| Mod Init | `*Mod.init()` | 모듈별 서비스 등록 |

### 3. 모듈별 DI 책임

| 모듈 | 등록 서비스 | 등록 위치 |
|------|------------|----------|
| Pulse | `EventBus`, `ProviderRegistry` | `PulseBootstrap` |
| Echo | `EchoProfiler`, `EchoConfig` | `EchoMod.init()` |
| Fuse | `FuseThrottleController` | `FuseLifecycle.init()` |

---

## 규약

### DO ✅

1. **생성자 주입 선호**
   ```java
   public class MyService {
       private final Dependency dep;
       
       public MyService(Dependency dep) {
           this.dep = dep;
       }
   }
   ```

2. **getInstance()에 ServiceLocator 조회 포함**
   ```java
   // ServiceLocator → Fallback 순서
   ```

3. **테스트에서 setInstance() 사용**
   ```java
   @BeforeEach
   void setUp() {
       MyService.setInstance(mockService);
   }
   ```

### DON'T ❌

1. **getInstance() fallback 제거 금지**
   - 테스트/독립 실행 불가능해짐

2. **순환 의존성 금지**
   - A → B → A 금지
   - Bootstrap 순서로 해결

3. **Mixin에서 직접 new 금지**
   - ServiceLocator 통해 조회

---

## Bootstrap 순서

```
1. PulseBootstrap.init()
   ├── PulseServiceLocator 초기화
   ├── EventBus 등록
   └── ProviderRegistry 등록

2. EchoMod.init()
   ├── EchoConfig 등록
   └── EchoProfiler 등록

3. FuseMod.init()
   └── FuseLifecycle.init()
       ├── FuseThrottleController 등록
       └── 컴포넌트 연결
```

---

## 테스트 지원

### 단위 테스트

```java
@BeforeEach
void setUp() {
    // Mock 주입
    EchoProfiler.setInstance(mockProfiler);
    EchoRuntimeState.setForTest(testSnapshot);
}

@AfterEach
void tearDown() {
    // 복원
    EchoProfiler.setInstance(null);
    EchoRuntimeState.reset();
}
```

### 통합 테스트

```java
@BeforeAll
static void initPulse() {
    PulseServiceLocator.getInstance().registerService(
        EchoProfiler.class, 
        new EchoProfiler(testConfig)
    );
}
```

---

## 마이그레이션 체크리스트

- [x] `getInstance()` 패턴에 ServiceLocator 조회 추가
- [x] Fallback 유지 (제거 금지)
- [x] `setInstance()` 테스트 지원 메서드 추가
- [x] Bootstrap 순서 문서화
