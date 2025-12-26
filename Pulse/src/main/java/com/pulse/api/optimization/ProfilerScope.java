package com.pulse.api.optimization;

import com.pulse.api.PublicAPI;
import com.pulse.api.FeatureFlags;
import com.pulse.api.spi.IProfilerProvider;

/**
 * 프로파일러 스코프.
 * SPI를 통해 프로파일러와 연동되는 AutoCloseable 스코프.
 * 프로파일러가 로드되지 않았을 때도 안전하게 no-op으로 동작합니다.
 * 
 * <pre>
 * // 사용 예시 - try-with-resources
 * try (ProfilerScope scope = ProfilerScope.begin(OptimizationPoint.ZOMBIE_AI_UPDATE)) {
 *     // 측정할 코드
 * }
 * // 자동으로 종료됨
 * 
 * // 커스텀 라벨 사용
 * try (ProfilerScope scope = ProfilerScope.begin("mymod.custom.operation")) {
 *     // 측정할 코드
 * }
 * </pre>
 * 
 * @since 1.1.0
 */
@PublicAPI(since = "1.1.0")
public final class ProfilerScope implements AutoCloseable {

    // No-op 싱글톤 (프로파일러 없을 때 사용)
    private static final ProfilerScope NO_OP = new ProfilerScope(null, null, false);

    // No-op Provider (Provider 없을 때 사용)
    private static final IProfilerProvider NOOP_PROVIDER = new NoOpProfilerProvider();

    // Provider 캐시
    private static volatile IProfilerProvider cachedProvider = null;
    private static volatile boolean providerChecked = false;

    private final OptimizationPoint point;
    private final String label;
    private final long startNanos;
    private final boolean active;

    // ═══════════════════════════════════════════════════════════════
    // 생성자 (private)
    // ═══════════════════════════════════════════════════════════════

    private ProfilerScope(OptimizationPoint point, String label, boolean active) {
        this.point = point;
        this.label = label;
        this.active = active;
        this.startNanos = active ? System.nanoTime() : 0;

        if (active && label != null) {
            getProvider().pushScope(label);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 팩토리 메서드
    // ═══════════════════════════════════════════════════════════════

    /**
     * OptimizationPoint로 스코프 시작.
     * 프로파일러가 없으면 no-op 스코프 반환.
     * 
     * @param point OptimizationPoint
     * @return ProfilerScope (자동 닫힘)
     */
    public static ProfilerScope begin(OptimizationPoint point) {
        if (!isProfilerAvailable()) {
            return NO_OP;
        }

        String profilerLabel = point.getFullLabel();
        return new ProfilerScope(point, profilerLabel, true);
    }

    /**
     * 커스텀 라벨로 스코프 시작.
     * 프로파일러가 없으면 no-op 스코프 반환.
     * 
     * @param label 프로파일러 라벨
     * @return ProfilerScope (자동 닫힘)
     */
    public static ProfilerScope begin(String label) {
        if (!isProfilerAvailable()) {
            return NO_OP;
        }

        return new ProfilerScope(null, label, true);
    }

    // ═══════════════════════════════════════════════════════════════
    // 상태 조회
    // ═══════════════════════════════════════════════════════════════

    /**
     * 경과 시간 (마이크로초).
     * 비활성 스코프는 0 반환.
     * 
     * @return 경과 마이크로초
     */
    public long getElapsedMicros() {
        if (!active) {
            return 0;
        }
        return (System.nanoTime() - startNanos) / 1000;
    }

    /**
     * 경과 시간 (밀리초).
     * 
     * @return 경과 밀리초
     */
    public double getElapsedMillis() {
        return getElapsedMicros() / 1000.0;
    }

    /**
     * 스코프가 활성 상태인지 확인.
     * 
     * @return 활성이면 true
     */
    public boolean isActive() {
        return active;
    }

    /**
     * 연결된 OptimizationPoint 반환.
     * 
     * @return OptimizationPoint (없으면 null)
     */
    public OptimizationPoint getPoint() {
        return point;
    }

    /**
     * 프로파일러 라벨 반환.
     * 
     * @return 라벨 문자열
     */
    public String getLabel() {
        return label;
    }

    // ═══════════════════════════════════════════════════════════════
    // AutoCloseable 구현
    // ═══════════════════════════════════════════════════════════════

    /**
     * 스코프 종료.
     * active=false면 no-op.
     */
    @Override
    public void close() {
        if (active && label != null) {
            getProvider().popScope();
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // SPI Provider 연동 (리플렉션 제거, SPI 사용)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 프로파일러 사용 가능 여부 확인.
     * 
     * @return 프로파일러 Provider가 등록되어 있으면 true
     */
    public static boolean isProfilerAvailable() {
        // 기능이 비활성화되어 있으면 false
        if (!FeatureFlags.isEnabled(FeatureFlags.PROFILER)) {
            return false;
        }

        return getProvider() != NOOP_PROVIDER;
    }

    /**
     * Provider 가용성 캐시 초기화 (테스트용).
     */
    public static void resetCache() {
        cachedProvider = null;
        providerChecked = false;
    }

    /**
     * Get the profiler provider via SPI.
     * Returns No-op provider if none registered.
     */
    private static IProfilerProvider getProvider() {
        if (!providerChecked) {
            try {
                cachedProvider = com.pulse.api.Pulse.getProviderRegistry()
                        .getProvider(IProfilerProvider.class)
                        .orElse(NOOP_PROVIDER);
            } catch (Exception e) {
                cachedProvider = NOOP_PROVIDER;
            }
            providerChecked = true;
        }
        return cachedProvider;
    }

    @Override
    public String toString() {
        if (!active) {
            return "ProfilerScope[NO_OP]";
        }
        return String.format("ProfilerScope[%s, %.3fms]", label, getElapsedMillis());
    }

    // ═══════════════════════════════════════════════════════════════
    // No-op Provider (프로파일러 없을 때 사용)
    // ═══════════════════════════════════════════════════════════════

    private static class NoOpProfilerProvider implements IProfilerProvider {
        @Override
        public String getId() {
            return "noop";
        }

        @Override
        public String getName() {
            return "No-op Profiler";
        }

        @Override
        public String getVersion() {
            return "0.0.0";
        }

        @Override
        public String getDescription() {
            return "No-op profiler provider";
        }

        @Override
        public int getPriority() {
            return 0;
        }

        @Override
        public void onInitialize() {
        }

        @Override
        public void onShutdown() {
        }

        @Override
        public boolean isEnabled() {
            return false;
        }

        @Override
        public void onTickStart() {
        }

        @Override
        public void onTickEnd(long tickTimeNanos) {
        }

        @Override
        public void onFrameStart() {
        }

        @Override
        public void onFrameEnd(long frameTimeNanos) {
        }

        @Override
        public double getCurrentFps() {
            return 0;
        }

        @Override
        public double getAverageTickTimeMs() {
            return 0;
        }

        @Override
        public double getAverageFrameTimeMs() {
            return 0;
        }

        @Override
        public void startProfiling() {
        }

        @Override
        public void stopProfiling() {
        }

        @Override
        public boolean isProfiling() {
            return false;
        }

        @Override
        public void resetData() {
        }

        @Override
        public void pushScope(String label) {
        }

        @Override
        public void popScope() {
        }
    }
}
