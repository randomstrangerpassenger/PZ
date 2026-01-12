package com.pulse.api;

import com.pulse.api.log.PulseLogger;

import java.util.Collections;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Pulse 기능 지원 여부 체크 API.
 * 하위 모드가 런타임에 Pulse 버전과 기능 지원 여부를 확인할 수 있습니다.
 * 
 * <pre>
 * // 사용 예시
 * if (CapabilityFlags.supports(CapabilityFlags.LUA_BUDGET)) {
 *     // LuaBudgetManager 사용 가능
 *     LuaBudgetManager.getInstance().setBudget("mymod.tick", 5000);
 * }
 * </pre>
 * 
 * @since 1.0.1
 */
@PublicAPI(since = "1.0.1")
public final class CapabilityFlags {
    private static final String LOG = PulseLogger.PULSE;

    // ═══════════════════════════════════════════════════════════════
    // 기본 제공 기능 상수
    // ═══════════════════════════════════════════════════════════════

    /** OptimizationPoint 시스템 지원 */
    public static final String OPTIMIZATION_POINT = "PULSE_OPTIMIZATION_POINT";

    /** LuaBridge V2 (확장 API) 지원 */
    public static final String LUA_BRIDGE_V2 = "LUA_BRIDGE_V2";

    /** Mixin Injection Validator 지원 */
    public static final String MIXIN_VALIDATOR = "MIXIN_INJECTION_VALIDATOR";

    /** Lua Budget Manager 지원 */
    public static final String LUA_BUDGET = "LUA_BUDGET_MANAGER";

    /** SafeGameAccess 지원 */
    public static final String SAFE_GAME_ACCESS = "SAFE_GAME_ACCESS";

    /** 프로파일러 통합 */
    public static final String PROFILER_INTEGRATION = "PROFILER_INTEGRATION";

    /** DevMode 지원 */
    public static final String DEV_MODE = "DEV_MODE";

    // ═══════════════════════════════════════════════════════════════
    // v1.1.0 새 기능 상수
    // ═══════════════════════════════════════════════════════════════

    /** Side API 지원 */
    public static final String SIDE_API = "SIDE_API";

    /** Silent Mode 지원 */
    public static final String SILENT_MODE = "SILENT_MODE";

    /** ProfilerScope 지원 */
    public static final String PROFILER_SCOPE = "PROFILER_SCOPE";

    /** Fail-soft 정책 지원 */
    public static final String FAILSOFT = "FAILSOFT_POLICY";

    /** 버전 호환성 API 지원 */
    public static final String VERSION_COMPAT = "VERSION_COMPATIBILITY";

    /** FeatureFlags 지원 */
    public static final String FEATURE_FLAGS = "FEATURE_FLAGS";

    // ═══════════════════════════════════════════════════════════════
    // 내부 상태
    // ═══════════════════════════════════════════════════════════════

    private static final Set<String> capabilities = ConcurrentHashMap.newKeySet();
    private static volatile boolean initialized = false;

    private CapabilityFlags() {
    } // 인스턴스화 방지

    // ═══════════════════════════════════════════════════════════════
    // 초기화
    // ═══════════════════════════════════════════════════════════════

    /**
     * 기능 플래그 초기화 (Pulse 시작 시 자동 호출).
     */
    @InternalAPI
    public static void initialize() {
        if (initialized)
            return;

        // 1.0.1에서 지원하는 모든 기능 등록
        register(OPTIMIZATION_POINT);
        register(LUA_BRIDGE_V2);
        register(MIXIN_VALIDATOR);
        register(LUA_BUDGET);
        register(SAFE_GAME_ACCESS);
        register(DEV_MODE);

        // 1.1.0 추가 기능
        register(SIDE_API);
        register(SILENT_MODE);
        register(PROFILER_SCOPE);
        register(FAILSOFT);
        register(VERSION_COMPAT);
        register(FEATURE_FLAGS);

        // 프로파일러 통합은 하위 모드에서 등록

        initialized = true;
        initialized = true;
        PulseLogger.info(LOG, "CapabilityFlags initialized: {} capabilities", capabilities.size());
    }

    // ═══════════════════════════════════════════════════════════════
    // 공개 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 기능 지원 여부 확인.
     * 
     * @param capability 기능 이름 (예: "PULSE_OPTIMIZATION_POINT")
     * @return 지원하면 true
     */
    public static boolean supports(String capability) {
        if (!initialized)
            initialize();
        return capabilities.contains(capability);
    }

    /**
     * 여러 기능이 모두 지원되는지 확인.
     * 
     * @param requiredCapabilities 필요한 기능 목록
     * @return 모두 지원하면 true
     */
    public static boolean supportsAll(String... requiredCapabilities) {
        for (String cap : requiredCapabilities) {
            if (!supports(cap))
                return false;
        }
        return true;
    }

    /**
     * 여러 기능 중 하나라도 지원되는지 확인.
     * 
     * @param capabilities 기능 목록
     * @return 하나라도 지원하면 true
     */
    public static boolean supportsAny(String... capabilities) {
        for (String cap : capabilities) {
            if (supports(cap))
                return true;
        }
        return false;
    }

    /**
     * 지원되는 모든 기능 목록 반환.
     * 
     * @return 불변 Set
     */
    public static Set<String> getAllCapabilities() {
        if (!initialized)
            initialize();
        return Collections.unmodifiableSet(capabilities);
    }

    /**
     * 지원되는 기능 수.
     * 
     * @return 기능 수
     */
    public static int count() {
        if (!initialized)
            initialize();
        return capabilities.size();
    }

    // ═══════════════════════════════════════════════════════════════
    // 내부 API (모드 사용 불가)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 기능 등록 (내부용).
     * 
     * @param capability 기능 이름
     */
    @InternalAPI
    public static void register(String capability) {
        if (capability != null && !capability.isEmpty()) {
            capabilities.add(capability);
        }
    }

    /**
     * 기능 등록 해제 (내부용).
     * 
     * @param capability 기능 이름
     */
    @InternalAPI
    public static void unregister(String capability) {
        capabilities.remove(capability);
    }

    /**
     * 디버그 출력.
     */
    public static void printCapabilities() {
        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "  Pulse Capabilities ({})", capabilities.size());
        PulseLogger.info(LOG, "═══════════════════════════════════════");
        for (String cap : capabilities) {
            PulseLogger.info(LOG, "  ✓ {}", cap);
        }
        PulseLogger.info(LOG, "═══════════════════════════════════════");
    }
}
