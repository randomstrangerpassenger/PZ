package com.pulse.api.optimization;

import com.pulse.api.InternalAPI;
import com.pulse.api.PublicAPI;
import com.pulse.api.log.PulseLogger;

import java.util.Collection;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;

/**
 * OptimizationPoint 레지스트리.
 * 기본 제공 포인트와 모드가 커스텀 등록한 포인트를 관리합니다.
 * 
 * <pre>
 * // 커스텀 포인트 등록
 * OptimizationPointRegistry.register("MY_CUSTOM_POINT",
 *         "com.mymod.MyClass", "mymod.custom");
 * 
 * // 포인트 조회
 * OptimizationPointInfo info = OptimizationPointRegistry.get("ZOMBIE_AI_UPDATE");
 * </pre>
 * 
 * @since 1.0.1
 */
@PublicAPI(since = "1.0.1", status = PublicAPI.Status.EXPERIMENTAL)
public final class OptimizationPointRegistry {

    // 커스텀 등록된 포인트
    private static final Map<String, OptimizationPointInfo> customPoints = new ConcurrentHashMap<>();
    private static final String LOG = PulseLogger.PULSE;

    // 초기화 플래그
    private static volatile boolean initialized = false;

    private OptimizationPointRegistry() {
    } // 인스턴스화 방지

    // ═══════════════════════════════════════════════════════════════
    // 초기화
    // ═══════════════════════════════════════════════════════════════

    /**
     * 레지스트리 초기화 (Pulse 시작 시 자동 호출).
     */
    @InternalAPI
    public static void initialize() {
        if (initialized)
            return;

        // 기본 OptimizationPoint들을 등록
        for (OptimizationPoint point : OptimizationPoint.values()) {
            customPoints.put(point.name(), new OptimizationPointInfo(
                    point.name(),
                    point.getMixinTarget(),
                    point.getProfilerLabel(),
                    point.getTier(),
                    true // built-in
            ));
        }

        initialized = true;
        PulseLogger.info(LOG, "OptimizationPointRegistry initialized with {} built-in points",
                OptimizationPoint.values().length);
    }

    // ═══════════════════════════════════════════════════════════════
    // 등록 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 커스텀 OptimizationPoint 등록.
     * 
     * @param id            고유 식별자 (대문자 권장, 예: "MY_CUSTOM_POINT")
     * @param mixinTarget   Mixin 대상 클래스 전체 경로
     * @param profilerLabel 프로파일러 라벨
     * @return 등록 성공 여부 (이미 존재하면 false)
     */
    public static boolean register(String id, String mixinTarget, String profilerLabel) {
        return register(id, mixinTarget, profilerLabel, 3); // Tier 3 = custom
    }

    /**
     * 커스텀 OptimizationPoint 등록 (Tier 지정).
     * 
     * @param id            고유 식별자
     * @param mixinTarget   Mixin 대상 클래스 전체 경로
     * @param profilerLabel 프로파일러 라벨
     * @param tier          Tier 레벨 (3 이상 권장)
     * @return 등록 성공 여부
     */
    public static boolean register(String id, String mixinTarget, String profilerLabel, int tier) {
        if (id == null || id.isEmpty())
            return false;
        if (mixinTarget == null || mixinTarget.isEmpty())
            return false;
        if (profilerLabel == null || profilerLabel.isEmpty())
            return false;

        String normalizedId = id.toUpperCase();

        if (customPoints.containsKey(normalizedId)) {
            PulseLogger.warn(LOG, "OptimizationPoint already exists: {}", normalizedId);
            return false;
        }

        customPoints.put(normalizedId, new OptimizationPointInfo(
                normalizedId, mixinTarget, profilerLabel, tier, false));

        PulseLogger.info(LOG, "Registered custom OptimizationPoint: {}", normalizedId);
        return true;
    }

    // ═══════════════════════════════════════════════════════════════
    // 조회 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * ID로 OptimizationPointInfo 조회.
     * 
     * @param id 포인트 ID
     * @return OptimizationPointInfo or null if not found
     */
    public static OptimizationPointInfo get(String id) {
        if (!initialized)
            initialize();
        return customPoints.get(id.toUpperCase());
    }

    /**
     * ID로 OptimizationPointInfo 조회 (Optional 반환).
     * 
     * @param id 포인트 ID
     * @return Optional containing the info
     */
    public static Optional<OptimizationPointInfo> find(String id) {
        return Optional.ofNullable(get(id));
    }

    /**
     * 모든 등록된 포인트 반환.
     * 
     * @return 불변 컬렉션
     */
    public static Collection<OptimizationPointInfo> getAll() {
        if (!initialized)
            initialize();
        return Collections.unmodifiableCollection(customPoints.values());
    }

    /**
     * 등록 여부 확인.
     * 
     * @param id 포인트 ID
     * @return 등록되어 있으면 true
     */
    public static boolean isRegistered(String id) {
        if (!initialized)
            initialize();
        return customPoints.containsKey(id.toUpperCase());
    }

    /**
     * 등록된 포인트 수.
     * 
     * @return 전체 포인트 수 (built-in + custom)
     */
    public static int size() {
        if (!initialized)
            initialize();
        return customPoints.size();
    }

    /**
     * Mixin 타깃으로 포인트 찾기.
     * 
     * @param mixinTarget Mixin 대상 클래스
     * @return Optional containing the info
     */
    public static Optional<OptimizationPointInfo> findByMixinTarget(String mixinTarget) {
        if (!initialized)
            initialize();
        return customPoints.values().stream()
                .filter(info -> info.getMixinTarget().equals(mixinTarget))
                .findFirst();
    }

    /**
     * 프로파일러 라벨로 포인트 찾기.
     * 
     * @param profilerLabel 프로파일러 라벨
     * @return Optional containing the info
     */
    public static Optional<OptimizationPointInfo> findByProfilerLabel(String profilerLabel) {
        if (!initialized)
            initialize();
        return customPoints.values().stream()
                .filter(info -> info.getProfilerLabel().equals(profilerLabel))
                .findFirst();
    }

    /**
     * @deprecated Use {@link #findByProfilerLabel(String)} instead.
     */
    @Deprecated
    public static Optional<OptimizationPointInfo> findByEchoPrefix(String echoPrefix) {
        return findByProfilerLabel(echoPrefix);
    }

    // ═══════════════════════════════════════════════════════════════
    // 정보 클래스
    // ═══════════════════════════════════════════════════════════════

    /**
     * OptimizationPoint 정보를 담는 불변 객체.
     */
    @PublicAPI(since = "1.0.1", status = PublicAPI.Status.EXPERIMENTAL)
    public static final class OptimizationPointInfo {
        private final String id;
        private final String mixinTarget;
        private final String profilerLabel;
        private final int tier;
        private final boolean builtIn;

        OptimizationPointInfo(String id, String mixinTarget, String profilerLabel,
                int tier, boolean builtIn) {
            this.id = id;
            this.mixinTarget = mixinTarget;
            this.profilerLabel = profilerLabel;
            this.tier = tier;
            this.builtIn = builtIn;
        }

        public String getId() {
            return id;
        }

        public String getMixinTarget() {
            return mixinTarget;
        }

        public String getProfilerLabel() {
            return profilerLabel;
        }

        /**
         * @deprecated Use {@link #getProfilerLabel()} instead.
         */
        @Deprecated
        public String getEchoPrefix() {
            return profilerLabel;
        }

        public int getTier() {
            return tier;
        }

        public boolean isBuiltIn() {
            return builtIn;
        }

        /**
         * 프로파일러 라벨 생성.
         */
        public String createLabel(String suffix) {
            return profilerLabel + "." + suffix;
        }

        /**
         * @deprecated Use {@link #createLabel(String)} instead.
         */
        @Deprecated
        public String createEchoLabel(String suffix) {
            return createLabel(suffix);
        }

        @Override
        public String toString() {
            return String.format("OptimizationPoint[%s, tier=%d, target=%s, label=%s]",
                    id, tier, mixinTarget, profilerLabel);
        }
    }
}
