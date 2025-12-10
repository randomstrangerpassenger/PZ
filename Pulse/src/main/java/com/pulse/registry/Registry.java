package com.pulse.registry;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/**
 * 범용 레지스트리.
 * 특정 타입의 객체를 식별자로 등록하고 관리.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 레지스트리 생성
 * Registry<MyItem> ITEMS = Registry.create(Identifier.of("mymod", "items"));
 * 
 * // 등록
 * ITEMS.register(Identifier.of("mymod", "cool_item"), new MyCoolItem());
 * 
 * // 조회
 * MyItem item = ITEMS.get(Identifier.of("mymod", "cool_item"));
 * </pre>
 * 
 * @param <T> 레지스트리에 저장할 객체 타입
 */
public class Registry<T> {

    private final Identifier registryId;
    private final Map<Identifier, T> entries = new ConcurrentHashMap<>();
    private final Map<Identifier, Supplier<T>> deferredEntries = new ConcurrentHashMap<>();
    private boolean frozen = false;

    // 글로벌 레지스트리 목록
    private static final Map<Identifier, Registry<?>> REGISTRIES = new ConcurrentHashMap<>();

    private Registry(Identifier registryId) {
        this.registryId = registryId;
    }

    /**
     * 새 레지스트리 생성
     */
    public static <T> Registry<T> create(Identifier registryId) {
        if (REGISTRIES.containsKey(registryId)) {
            throw new IllegalStateException("Registry already exists: " + registryId);
        }

        Registry<T> registry = new Registry<>(registryId);
        REGISTRIES.put(registryId, registry);

        System.out.println("[Pulse/Registry] Created registry: " + registryId);
        return registry;
    }

    /**
     * 기존 레지스트리 가져오기
     */
    @SuppressWarnings("unchecked")
    public static <T> Registry<T> getRegistry(Identifier registryId) {
        return (Registry<T>) REGISTRIES.get(registryId);
    }

    // ─────────────────────────────────────────────────────────────
    // 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * 객체 등록
     */
    public T register(Identifier id, T value) {
        if (frozen) {
            throw new IllegalStateException("Registry is frozen: " + registryId);
        }
        if (entries.containsKey(id)) {
            throw new IllegalArgumentException("Duplicate entry: " + id);
        }

        entries.put(id, value);
        System.out.println("[Pulse/Registry] Registered " + registryId + " -> " + id);
        return value;
    }

    /**
     * 문자열 ID로 등록
     */
    public T register(String id, T value) {
        return register(Identifier.parse(id), value);
    }

    /**
     * 지연 등록 (Supplier 사용)
     * 실제 객체는 freeze 시점에 생성됨
     */
    public void registerDeferred(Identifier id, Supplier<T> supplier) {
        if (frozen) {
            throw new IllegalStateException("Registry is frozen: " + registryId);
        }
        deferredEntries.put(id, supplier);
    }

    // ─────────────────────────────────────────────────────────────
    // 조회
    // ─────────────────────────────────────────────────────────────

    /**
     * ID로 객체 가져오기
     */
    public T get(Identifier id) {
        return entries.get(id);
    }

    /**
     * 문자열 ID로 가져오기
     */
    public T get(String id) {
        return get(Identifier.parse(id));
    }

    /**
     * ID로 Optional 가져오기
     */
    public Optional<T> getOptional(Identifier id) {
        return Optional.ofNullable(entries.get(id));
    }

    /**
     * ID 존재 여부 확인
     */
    public boolean contains(Identifier id) {
        return entries.containsKey(id);
    }

    /**
     * 객체의 ID 가져오기 (역방향 조회)
     */
    public Optional<Identifier> getId(T value) {
        for (Map.Entry<Identifier, T> entry : entries.entrySet()) {
            if (entry.getValue().equals(value)) {
                return Optional.of(entry.getKey());
            }
        }
        return Optional.empty();
    }

    // ─────────────────────────────────────────────────────────────
    // 반복
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 ID
     */
    public Set<Identifier> getIds() {
        return Collections.unmodifiableSet(entries.keySet());
    }

    /**
     * 모든 값
     */
    public Collection<T> getValues() {
        return Collections.unmodifiableCollection(entries.values());
    }

    /**
     * 모든 엔트리
     */
    public Set<Map.Entry<Identifier, T>> getEntries() {
        return Collections.unmodifiableSet(entries.entrySet());
    }

    /**
     * 등록된 항목 수
     */
    public int size() {
        return entries.size();
    }

    public boolean isEmpty() {
        return entries.isEmpty();
    }

    // ─────────────────────────────────────────────────────────────
    // 레지스트리 잠금
    // ─────────────────────────────────────────────────────────────

    /**
     * 레지스트리 잠금 (더 이상 등록 불가)
     * 지연 등록된 항목들이 이 시점에 생성됨
     */
    public void freeze() {
        if (frozen)
            return;

        // 지연 등록 처리
        for (Map.Entry<Identifier, Supplier<T>> entry : deferredEntries.entrySet()) {
            T value = entry.getValue().get();
            entries.put(entry.getKey(), value);
        }
        deferredEntries.clear();

        frozen = true;
        System.out.println("[Pulse/Registry] Frozen " + registryId + " with " + entries.size() + " entries");
    }

    public boolean isFrozen() {
        return frozen;
    }

    public Identifier getRegistryId() {
        return registryId;
    }

    /**
     * 모든 레지스트리 잠금
     */
    public static void freezeAll() {
        for (Registry<?> registry : REGISTRIES.values()) {
            registry.freeze();
        }
    }

    /**
     * 모든 레지스트리 가져오기
     */
    public static Collection<Registry<?>> getAllRegistries() {
        return Collections.unmodifiableCollection(REGISTRIES.values());
    }
}
