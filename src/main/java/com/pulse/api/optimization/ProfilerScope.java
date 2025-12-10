package com.pulse.api.optimization;

import com.pulse.api.PublicAPI;
import com.pulse.api.FeatureFlags;

/**
 * 프로파일러 스코프.
 * Echo 프로파일러와 연동되는 AutoCloseable 스코프.
 * Echo가 로드되지 않았을 때도 안전하게 no-op으로 동작합니다.
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

    // No-op 싱글톤 (Echo 없을 때 사용)
    private static final ProfilerScope NO_OP = new ProfilerScope(null, null, false);

    // Echo 프로파일러 사용 가능 여부 캐시
    private static volatile Boolean echoAvailable = null;

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
            pushEchoScope(label);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 팩토리 메서드
    // ═══════════════════════════════════════════════════════════════

    /**
     * OptimizationPoint로 스코프 시작.
     * Echo가 없으면 no-op 스코프 반환.
     * 
     * @param point OptimizationPoint
     * @return ProfilerScope (자동 닫힘)
     */
    public static ProfilerScope begin(OptimizationPoint point) {
        if (!isProfilerAvailable()) {
            return NO_OP;
        }

        String echoLabel = point.getEchoLabel();
        return new ProfilerScope(point, echoLabel, true);
    }

    /**
     * 커스텀 라벨로 스코프 시작.
     * Echo가 없으면 no-op 스코프 반환.
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
            popEchoScope(label);
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Echo 프로파일러 연동
    // ═══════════════════════════════════════════════════════════════

    /**
     * Echo 프로파일러 사용 가능 여부 확인.
     * 
     * @return Echo가 로드되어 있으면 true
     */
    public static boolean isProfilerAvailable() {
        // 기능이 비활성화되어 있으면 false
        if (!FeatureFlags.isEnabled(FeatureFlags.PROFILER)) {
            return false;
        }

        // 캐시된 결과 사용
        if (echoAvailable != null) {
            return echoAvailable;
        }

        // Echo 클래스 존재 여부 확인
        try {
            Class.forName("com.pulse.echo.EchoProfiler");
            echoAvailable = true;
        } catch (ClassNotFoundException e) {
            echoAvailable = false;
        }

        return echoAvailable;
    }

    /**
     * 프로파일러 가용성 캐시 초기화 (테스트용).
     */
    public static void resetCache() {
        echoAvailable = null;
    }

    // ═══════════════════════════════════════════════════════════════
    // Echo 내부 연동 메서드
    // ═══════════════════════════════════════════════════════════════

    private static void pushEchoScope(String label) {
        try {
            // Echo가 있으면 EchoProfiler.push(label) 호출
            Class<?> echoClass = Class.forName("com.pulse.echo.EchoProfiler");
            java.lang.reflect.Method pushMethod = echoClass.getMethod("push", String.class);
            pushMethod.invoke(null, label);
        } catch (Exception e) {
            // Echo 없음 - 무시
        }
    }

    private static void popEchoScope(String label) {
        try {
            // Echo가 있으면 EchoProfiler.pop() 호출
            Class<?> echoClass = Class.forName("com.pulse.echo.EchoProfiler");
            java.lang.reflect.Method popMethod = echoClass.getMethod("pop");
            popMethod.invoke(null);
        } catch (Exception e) {
            // Echo 없음 - 무시
        }
    }

    @Override
    public String toString() {
        if (!active) {
            return "ProfilerScope[NO_OP]";
        }
        return String.format("ProfilerScope[%s, %.3fms]", label, getElapsedMillis());
    }
}
