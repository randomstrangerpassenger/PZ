# Pulse 예외 처리 가이드라인

## 예외 계층 구조

```
PulseException (Base)
├── ConfigurationException     - 설정 관련 오류
├── InjectionException         - 의존성 주입 오류
├── InitializationException    - 초기화 오류
├── LuaInitializationException - Lua 초기화 오류
├── LuaInteropException        - Lua 연동 오류
├── MixinApplyException        - Mixin 적용 오류
├── ModLoadException           - 모드 로딩 오류 [NEW]
├── NetworkException           - 네트워크 오류
└── ReflectionException        - 리플렉션 오류
```

## 사용 가이드라인

### 1. 복구 가능 vs 치명적

| 예외 | 분류 | 처리 방식 |
|------|------|-----------|
| `ConfigurationException` | 복구 가능 | 기본값 사용 |
| `ModLoadException` | 부분 복구 | 해당 모드만 비활성화 |
| `LuaInteropException` | 복구 가능 | 해당 호출만 실패 |
| `ReflectionException` | 복구 가능 | 대체 경로 시도 |
| `InjectionException` | 치명적 | 게임 종료 권장 |
| `MixinApplyException` | 치명적 | 게임 종료 권장 |

### 2. catch(Exception) 대신 사용

```java
// ❌ Bad - 너무 광범위
try {
    mod.initialize();
} catch (Exception e) {
    log.error("Init failed", e);
}

// ✅ Good - 구체적 예외
try {
    mod.initialize();
} catch (ModLoadException e) {
    log.warn("Mod {} failed, disabling", e.getModId(), e);
    disableMod(e.getModId());
} catch (ConfigurationException e) {
    log.warn("Config error, using defaults", e);
    useDefaults();
}
```

### 3. 예외 컨텍스트 포함

```java
// ✅ Good - 디버깅에 필요한 정보 포함
throw new ModLoadException(
    modId, 
    String.format("Failed to resolve dependency: %s (required: %s)", 
        depId, requiredVersion),
    cause
);
```

## 마이그레이션 우선순위

1. **높음**: ModLoader, LuaBridge, EventBus
2. **중간**: NetworkManager, ConfigManager
3. **낮음**: 유틸리티 클래스

---

*Created: 2025-12-23*
