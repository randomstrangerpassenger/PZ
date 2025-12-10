package com.pulse.api;

import java.util.Collections;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 런타임 기능 플래그 시스템.
 * 개별 기능을 런타임에 활성화/비활성화할 수 있습니다.
 * Fail-soft 정책에서 실패한 기능을 비활성화하는 데 사용됩니다.
 * 
 * <pre>
 * // 사용 예시
 * if (FeatureFlags.isEnabled(FeatureFlags.MIXIN_SYSTEM)) {
 *     // Mixin 시스템 사용
 * }
 * 
 * // 기능 비활성화
 * FeatureFlags.disable("mymod.feature");
 * </pre>
 * 
 * @since 1.1.0
 */
@PublicAPI(since = "1.1.0")
public final class FeatureFlags {

    // ═══════════════════════════════════════════════════════════════
    // 표준 기능 ID
    // ═══════════════════════════════════════════════════════════════

    /** Mixin 시스템 */
    public static final String MIXIN_SYSTEM = "pulse.mixin";

    /** Lua Budget 관리 */
    public static final String LUA_BUDGET = "pulse.lua.budget";

    /** 프로파일러 */
    public static final String PROFILER = "pulse.profiler";

    /** Silent Mode */
    public static final String SILENT_MODE = "pulse.silent";

    /** Safe Game Access */
    public static final String SAFE_ACCESS = "pulse.safe_access";

    /** 네트워크 기능 */
    public static final String NETWORKING = "pulse.network";

    /** 최적화 포인트 시스템 */
    public static final String OPTIMIZATION_POINTS = "pulse.optimization";

    // ═══════════════════════════════════════════════════════════════
    // 내부 상태
    // ═══════════════════════════════════════════════════════════════

    // 비활성화된 기능 목록 (기본은 모두 활성)
    private static final Set<String> disabledFlags = ConcurrentHashMap.newKeySet();

    // 비활성화 사유
    private static final Map<String, String> disableReasons = new ConcurrentHashMap<>();

    private FeatureFlags() {
    } // 인스턴스화 방지

    // ═══════════════════════════════════════════════════════════════
    // 조회 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 기능이 활성화되어 있는지 확인.
     * 
     * @param featureId 기능 ID
     * @return 활성화되어 있으면 true
     */
    public static boolean isEnabled(String featureId) {
        if (featureId == null || featureId.isEmpty()) {
            return false;
        }
        return !disabledFlags.contains(featureId);
    }

    /**
     * 기능이 비활성화되어 있는지 확인.
     * 
     * @param featureId 기능 ID
     * @return 비활성화되어 있으면 true
     */
    public static boolean isDisabled(String featureId) {
        return !isEnabled(featureId);
    }

    /**
     * 비활성화 사유 조회.
     * 
     * @param featureId 기능 ID
     * @return 비활성화 사유 (없으면 null)
     */
    public static String getDisableReason(String featureId) {
        return disableReasons.get(featureId);
    }

    // ═══════════════════════════════════════════════════════════════
    // 설정 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 기능 활성화.
     * 
     * @param featureId 기능 ID
     */
    public static void enable(String featureId) {
        if (featureId != null && !featureId.isEmpty()) {
            disabledFlags.remove(featureId);
            disableReasons.remove(featureId);
            Pulse.log("pulse", "[FeatureFlags] Enabled: " + featureId);
        }
    }

    /**
     * 기능 비활성화.
     * 
     * @param featureId 기능 ID
     */
    public static void disable(String featureId) {
        disable(featureId, "Disabled by FeatureFlags.disable()");
    }

    /**
     * 기능 비활성화 (사유 포함).
     * 
     * @param featureId 기능 ID
     * @param reason    비활성화 사유
     */
    public static void disable(String featureId, String reason) {
        if (featureId != null && !featureId.isEmpty()) {
            disabledFlags.add(featureId);
            disableReasons.put(featureId, reason != null ? reason : "Unknown");
            Pulse.warn("pulse", "[FeatureFlags] Disabled: " + featureId + " (" + reason + ")");
        }
    }

    /**
     * 모듈 prefix로 시작하는 모든 기능 비활성화.
     * 예: disableModule("mymod") → "mymod.feature1", "mymod.feature2" 모두 비활성화
     * 
     * @param modulePrefix 모듈 prefix
     */
    public static void disableModule(String modulePrefix) {
        disableModule(modulePrefix, "Module disabled by FeatureFlags.disableModule()");
    }

    /**
     * 모듈 prefix로 시작하는 모든 기능 비활성화 (사유 포함).
     * 
     * @param modulePrefix 모듈 prefix
     * @param reason       비활성화 사유
     */
    public static void disableModule(String modulePrefix, String reason) {
        if (modulePrefix == null || modulePrefix.isEmpty()) {
            return;
        }

        // 해당 모듈 자체도 비활성화
        disable(modulePrefix, reason);

        // prefix로 시작하는 모든 기능 비활성화
        // (이미 등록된 것들만 - 새로 등록되는 것은 isEnabled에서 체크)
        for (String featureId : disabledFlags) {
            if (featureId.startsWith(modulePrefix + ".")) {
                disable(featureId, reason);
            }
        }

        Pulse.warn("pulse", "[FeatureFlags] Module disabled: " + modulePrefix);
    }

    // ═══════════════════════════════════════════════════════════════
    // 조회
    // ═══════════════════════════════════════════════════════════════

    /**
     * 모든 비활성화된 기능 목록 반환.
     * 
     * @return 불변 Set
     */
    public static Set<String> getDisabledFeatures() {
        return Collections.unmodifiableSet(disabledFlags);
    }

    /**
     * 비활성화된 기능 수.
     * 
     * @return 비활성화된 기능 수
     */
    public static int getDisabledCount() {
        return disabledFlags.size();
    }

    /**
     * 모든 플래그 초기화 (테스트용).
     */
    @InternalAPI
    public static void reset() {
        disabledFlags.clear();
        disableReasons.clear();
    }

    /**
     * 디버그 출력.
     */
    public static void printStatus() {
        System.out.println("═══════════════════════════════════════");
        System.out.println("  FeatureFlags Status");
        System.out.println("═══════════════════════════════════════");

        if (disabledFlags.isEmpty()) {
            System.out.println("  All features enabled");
        } else {
            System.out.println("  Disabled features (" + disabledFlags.size() + "):");
            for (String featureId : disabledFlags) {
                String reason = disableReasons.getOrDefault(featureId, "Unknown");
                System.out.println("    ✗ " + featureId + " - " + reason);
            }
        }

        System.out.println("═══════════════════════════════════════");
    }
}
