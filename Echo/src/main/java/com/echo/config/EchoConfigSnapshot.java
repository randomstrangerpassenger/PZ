package com.echo.config;

import com.echo.LifecyclePhase;

/**
 * Echo 설정 스냅샷 (불변)
 * 
 * 핫패스에서 사용하는 설정값의 불변 스냅샷입니다.
 * - 모든 필드는 final (불변)
 * - getInstance() 호출 금지 - EchoRuntimeState.current()로만 접근
 * - 예외 발생 금지
 * 
 * @since Bundle A - Hot Path 무음화
 */
public final class EchoConfigSnapshot {

    /** 프로파일링 활성화 여부 */
    public final boolean enabled;

    /** Lua 프로파일링 활성화 여부 */
    public final boolean luaProfilingEnabled;

    /** 스파이크 임계값 (밀리초) */
    public final double spikeThresholdMs;

    /** 현재 라이프사이클 단계 */
    public final LifecyclePhase lifecyclePhase;

    /** 디버그 모드 (원샷 경고 활성화용) */
    public final boolean debugMode;

    /** 기본 스냅샷 (비활성화 상태) - 항상 사용 가능 */
    public static final EchoConfigSnapshot DEFAULT = new EchoConfigSnapshot(
            false, // enabled
            false, // luaProfilingEnabled
            33.33, // spikeThresholdMs (2프레임 @30fps)
            LifecyclePhase.NOT_INITIALIZED, // lifecyclePhase
            false // debugMode
    );

    /**
     * 스냅샷 생성
     * 
     * @param enabled             프로파일링 활성화
     * @param luaProfilingEnabled Lua 프로파일링 활성화
     * @param spikeThresholdMs    스파이크 임계값 (ms)
     * @param lifecyclePhase      라이프사이클 단계
     * @param debugMode           디버그 모드
     */
    public EchoConfigSnapshot(
            boolean enabled,
            boolean luaProfilingEnabled,
            double spikeThresholdMs,
            LifecyclePhase lifecyclePhase,
            boolean debugMode) {
        this.enabled = enabled;
        this.luaProfilingEnabled = luaProfilingEnabled;
        this.spikeThresholdMs = spikeThresholdMs;
        this.lifecyclePhase = lifecyclePhase;
        this.debugMode = debugMode;
    }

    /**
     * 활성화 상태 스냅샷 생성 헬퍼
     * 
     * @param config EchoConfig 인스턴스
     * @return 현재 설정 기반 스냅샷
     */
    public static EchoConfigSnapshot fromConfig(EchoConfig config) {
        return new EchoConfigSnapshot(
                true, // enabled (활성화 요청 시에만 호출)
                config.isLuaProfilingEnabled(),
                config.getSpikeThresholdMs(),
                LifecyclePhase.RUNNING,
                config.isDebugMode());
    }

    /**
     * 라이프사이클 변경 스냅샷 파생
     * 
     * @param newPhase 새 라이프사이클 단계
     * @return 새 스냅샷
     */
    public EchoConfigSnapshot withLifecyclePhase(LifecyclePhase newPhase) {
        return new EchoConfigSnapshot(
                this.enabled,
                this.luaProfilingEnabled,
                this.spikeThresholdMs,
                newPhase,
                this.debugMode);
    }

    /**
     * 비활성화 스냅샷 파생
     * 
     * @return enabled=false인 새 스냅샷
     */
    public EchoConfigSnapshot disabled() {
        return new EchoConfigSnapshot(
                false,
                this.luaProfilingEnabled,
                this.spikeThresholdMs,
                this.lifecyclePhase,
                this.debugMode);
    }
}
