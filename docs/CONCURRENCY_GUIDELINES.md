# Pulse 동시성 패턴 가이드

## 현재 사용 중인 동시성 패턴

### 1. ConcurrentHashMap (권장)

```java
// ✅ Good - 원자적 연산 지원
private static final Map<String, Object> cache = new ConcurrentHashMap<>();

// 안전한 compute
cache.computeIfAbsent(key, k -> expensiveComputation());
```

**사용처:**
- `ReflectionCache` - Method/Field/Class 캐싱
- `PulseServiceLocator` - 서비스 레지스트리
- `EventBus` - 이벤트 핸들러 맵

### 2. CopyOnWriteArrayList (읽기 많은 경우)

```java
// ✅ Good - 읽기 >> 쓰기 경우
private static final List<Listener> listeners = new CopyOnWriteArrayList<>();
```

**사용처:**
- `ModReloader` - 등록된 모드 목록
- `EventBus` - 이벤트 리스너

### 3. volatile + DCL (싱글톤)

```java
// ✅ Good - Double-Checked Locking
private static volatile LuaStateManager instance;

public static LuaStateManager getInstance() {
    if (instance == null) {
        synchronized (LuaStateManager.class) {
            if (instance == null) {
                instance = new LuaStateManager();
            }
        }
    }
    return instance;
}
```

### 4. AtomicLong/AtomicInteger (카운터)

```java
// ✅ Good - 잠금 없는 카운터
private static final AtomicLong callCount = new AtomicLong(0);
callCount.incrementAndGet();
```

## 유지해야 하는 패턴

### synchronizedMap + WeakHashMap

```java
// ⚠️ 유지 필요 - ConcurrentHashMap은 WeakReference 미지원
Map<K, V> cache = Collections.synchronizedMap(new WeakHashMap<>());
```

**사용처 (변경 금지):**
- `LuaCallTracker.java` - 함수 호출 추적
- `FunctionLabeler.java` - 함수 라벨링
- `DataAttachments.java` - 데이터 첨부

**주의:** 반복 시 반드시 synchronized 블록 사용

```java
synchronized (cache) {
    for (var entry : cache.entrySet()) {
        // 안전한 반복
    }
}
```

## ❌ 지양해야 하는 패턴

```java
// ❌ Bad - 락 오버헤드
Collections.synchronizedList(new ArrayList<>());  // → CopyOnWriteArrayList
Collections.synchronizedSet(new HashSet<>());     // → ConcurrentHashMap.newKeySet()
```

---

*Created: 2025-12-23*
