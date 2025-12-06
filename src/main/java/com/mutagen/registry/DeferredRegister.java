package com.mutagen.registry;

import java.util.*;
import java.util.function.Supplier;

/**
 * 지연 등록 헬퍼.
 * NeoForge의 DeferredRegister와 유사한 개념.
 * 모드 초기화 시점에 등록을 수집하고, 나중에 실제 레지스트리에 커밋.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 모드 클래스에서
 * public static final DeferredRegister<MyItem> ITEMS = DeferredRegister.create("mymod", MyRegistries.ITEMS);
 * 
 * public static final RegistryEntry<MyItem> COOL_ITEM = ITEMS.register("cool_item", MyCoolItem::new);
 * 
 * // 초기화 시
 * ITEMS.registerAll();
 * </pre>
 * 
 * @param <T> 등록할 객체 타입
 */
public class DeferredRegister<T> {

    private final String modId;
    private final Registry<T> registry;
    private final List<PendingEntry<T>> pendingEntries = new ArrayList<>();
    private boolean committed = false;

    private DeferredRegister(String modId, Registry<T> registry) {
        this.modId = modId;
        this.registry = registry;
    }

    /**
     * DeferredRegister 생성
     */
    public static <T> DeferredRegister<T> create(String modId, Registry<T> registry) {
        return new DeferredRegister<>(modId, registry);
    }

    /**
     * 레지스트리 ID로 DeferredRegister 생성
     */
    public static <T> DeferredRegister<T> create(String modId, Identifier registryId) {
        Registry<T> registry = Registry.getRegistry(registryId);
        if (registry == null) {
            throw new IllegalArgumentException("Registry not found: " + registryId);
        }
        return new DeferredRegister<>(modId, registry);
    }

    // ─────────────────────────────────────────────────────────────
    // 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * 객체 등록 (지연)
     */
    public RegistryEntry<T> register(String name, Supplier<T> supplier) {
        if (committed) {
            throw new IllegalStateException("DeferredRegister already committed");
        }

        Identifier id = Identifier.of(modId, name);
        RegistryEntry<T> entry = new RegistryEntry<>(id, registry);
        pendingEntries.add(new PendingEntry<>(id, supplier, entry));

        return entry;
    }

    /**
     * 이미 생성된 객체 등록
     */
    public RegistryEntry<T> register(String name, T value) {
        return register(name, () -> value);
    }

    // ─────────────────────────────────────────────────────────────
    // 커밋
    // ─────────────────────────────────────────────────────────────

    /**
     * 모든 대기 중인 등록을 레지스트리에 커밋
     */
    public void registerAll() {
        if (committed) {
            return;
        }

        for (PendingEntry<T> pending : pendingEntries) {
            T value = pending.supplier.get();
            registry.register(pending.id, value);
            pending.entry.setValue(value);
        }

        committed = true;
        System.out.println("[Mutagen/Registry] Committed " + pendingEntries.size() +
                " entries from " + modId + " to " + registry.getRegistryId());
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    public String getModId() {
        return modId;
    }

    public Registry<T> getRegistry() {
        return registry;
    }

    public int getPendingCount() {
        return pendingEntries.size();
    }

    public boolean isCommitted() {
        return committed;
    }

    /**
     * 등록된 모든 엔트리 가져오기
     */
    public List<RegistryEntry<T>> getEntries() {
        List<RegistryEntry<T>> entries = new ArrayList<>();
        for (PendingEntry<T> pending : pendingEntries) {
            entries.add(pending.entry);
        }
        return entries;
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    private static class PendingEntry<T> {
        final Identifier id;
        final Supplier<T> supplier;
        final RegistryEntry<T> entry;

        PendingEntry(Identifier id, Supplier<T> supplier, RegistryEntry<T> entry) {
            this.id = id;
            this.supplier = supplier;
            this.entry = entry;
        }
    }
}
