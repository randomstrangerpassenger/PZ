package com.mutagen.mod;

import java.net.URLClassLoader;

/**
 * 로드된 모드를 나타내는 컨테이너.
 * 메타데이터, 클래스로더, 모드 인스턴스를 관리.
 */
public class ModContainer {

    private final ModMetadata metadata;
    private final URLClassLoader classLoader;
    private Object modInstance; // entrypoint 클래스의 인스턴스
    private ModState state = ModState.DISCOVERED;

    public ModContainer(ModMetadata metadata, URLClassLoader classLoader) {
        this.metadata = metadata;
        this.classLoader = classLoader;
    }

    // ─────────────────────────────────────────────────────────────
    // 모드 상태
    // ─────────────────────────────────────────────────────────────

    public enum ModState {
        DISCOVERED, // JAR 발견됨
        METADATA_LOADED, // 메타데이터 파싱 완료
        DEPENDENCIES_RESOLVED, // 의존성 확인 완료
        MIXINS_APPLIED, // Mixin 적용됨
        INITIALIZED, // 초기화 완료
        ERRORED // 에러 발생
    }

    // ─────────────────────────────────────────────────────────────
    // 모드 초기화
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드 엔트리포인트 클래스를 로드하고 인스턴스화
     */
    public void initialize() throws Exception {
        String entrypoint = metadata.getEntrypoint();
        if (entrypoint == null || entrypoint.isEmpty()) {
            System.out.println("[Mutagen/Mod] " + metadata.getId() + " has no entrypoint, skipping initialization");
            state = ModState.INITIALIZED;
            return;
        }

        try {
            System.out.println("[Mutagen/Mod] Initializing mod: " + metadata.getId());

            // 엔트리포인트 클래스 로드
            Class<?> entryClass = classLoader.loadClass(entrypoint);

            // MutagenMod 인터페이스 구현 여부 확인
            if (MutagenMod.class.isAssignableFrom(entryClass)) {
                modInstance = entryClass.getDeclaredConstructor().newInstance();
                ((MutagenMod) modInstance).onInitialize();
                System.out.println("[Mutagen/Mod] ✓ " + metadata.getId() + " initialized successfully");
            } else {
                System.err.println("[Mutagen/Mod] WARNING: " + entrypoint +
                        " does not implement MutagenMod interface");
                modInstance = entryClass.getDeclaredConstructor().newInstance();
            }

            state = ModState.INITIALIZED;
            metadata.setLoaded(true);

        } catch (Exception e) {
            state = ModState.ERRORED;
            System.err.println("[Mutagen/Mod] Failed to initialize mod: " + metadata.getId());
            throw e;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // Getters
    // ─────────────────────────────────────────────────────────────

    public ModMetadata getMetadata() {
        return metadata;
    }

    public String getId() {
        return metadata.getId();
    }

    public String getVersion() {
        return metadata.getVersion();
    }

    public URLClassLoader getClassLoader() {
        return classLoader;
    }

    public Object getModInstance() {
        return modInstance;
    }

    @SuppressWarnings("unchecked")
    public <T> T getModInstance(Class<T> type) {
        if (type.isInstance(modInstance)) {
            return (T) modInstance;
        }
        return null;
    }

    public ModState getState() {
        return state;
    }

    public void setState(ModState state) {
        this.state = state;
    }

    public boolean isLoaded() {
        return state == ModState.INITIALIZED;
    }

    public boolean hasError() {
        return state == ModState.ERRORED;
    }

    @Override
    public String toString() {
        return String.format("ModContainer[%s v%s, state=%s]",
                metadata.getId(), metadata.getVersion(), state);
    }
}
