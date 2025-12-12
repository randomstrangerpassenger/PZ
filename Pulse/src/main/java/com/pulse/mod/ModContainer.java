package com.pulse.mod;

import com.pulse.api.log.PulseLogger;

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
        LOADED, // 정상 로드됨 (활성 상태)
        DISABLED, // 비활성화됨 (핫 리로드)
        UNLOADED, // 언로드됨 (종료 시)
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
            PulseLogger.info(PulseLogger.PULSE, "{} has no entrypoint, skipping initialization", metadata.getId());
            state = ModState.INITIALIZED;
            return;
        }

        try {
            PulseLogger.info(PulseLogger.PULSE, "Initializing mod: {}", metadata.getId());

            // 엔트리포인트 클래스 로드
            Class<?> entryClass = classLoader.loadClass(entrypoint);

            // PulseMod 인터페이스 구현 여부 확인
            if (PulseMod.class.isAssignableFrom(entryClass)) {
                modInstance = entryClass.getDeclaredConstructor().newInstance();
                ((PulseMod) modInstance).onInitialize();
                PulseLogger.info(PulseLogger.PULSE, "✓ {} initialized successfully", metadata.getId());
            } else {
                PulseLogger.warn(PulseLogger.PULSE, "{} does not implement PulseMod interface", entrypoint);
                modInstance = entryClass.getDeclaredConstructor().newInstance();
            }

            state = ModState.INITIALIZED;
            metadata.setLoaded(true);

        } catch (Exception e) {
            state = ModState.ERRORED;
            PulseLogger.error(PulseLogger.PULSE, "Failed to initialize mod: {}", metadata.getId());
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
