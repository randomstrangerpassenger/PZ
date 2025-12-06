package com.mutagen.registry;

/**
 * 레지스트리 엔트리 참조.
 * DeferredRegister에서 반환되어 나중에 실제 값에 접근할 수 있게 함.
 * 
 * @param <T> 등록된 객체 타입
 */
public class RegistryEntry<T> {

    private final Identifier id;
    private final Registry<T> registry;
    private T value;
    private boolean resolved = false;

    RegistryEntry(Identifier id, Registry<T> registry) {
        this.id = id;
        this.registry = registry;
    }

    /**
     * 등록된 값 가져오기
     */
    public T get() {
        if (!resolved) {
            // 아직 커밋되지 않은 경우 레지스트리에서 조회 시도
            T fromRegistry = registry.get(id);
            if (fromRegistry != null) {
                this.value = fromRegistry;
                this.resolved = true;
            }
        }

        if (value == null && !resolved) {
            throw new IllegalStateException("Registry entry not yet available: " + id);
        }

        return value;
    }

    /**
     * 값이 이미 해결되었는지 확인
     */
    public boolean isResolved() {
        return resolved || registry.contains(id);
    }

    /**
     * 식별자 가져오기
     */
    public Identifier getId() {
        return id;
    }

    /**
     * 레지스트리 가져오기
     */
    public Registry<T> getRegistry() {
        return registry;
    }

    // 내부 사용
    void setValue(T value) {
        this.value = value;
        this.resolved = true;
    }

    @Override
    public String toString() {
        return "RegistryEntry[" + id + "]";
    }
}
