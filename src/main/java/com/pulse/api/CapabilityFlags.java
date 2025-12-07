package com.pulse.api;

import java.util.Collections;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Pulse 기능 지원 여부 체크 API.
 * Fuse/Nerve 등 모드가 런타임에 Pulse 버전과 기능 지원 여부를 확인할 수 있습니다.
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

    /** Echo 프로파일러 통합 */
    public static final String ECHO_INTEGRATION = "ECHO_INTEGRATION";

    /** DevMode 지원 */
    public static final String DEV_MODE = "DEV_MODE";

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

        // Echo는 별도 모드로 로드되므로 여기서는 등록하지 않음
        // Echo가 로드되면 Echo에서 ECHO_INTEGRATION을 등록

        initialized = true;
        System.out.println("[Pulse] CapabilityFlags initialized: " + capabilities.size() + " capabilities");
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
        System.out.println("═══════════════════════════════════════");
        System.out.println("  Pulse Capabilities (" + capabilities.size() + ")");
        System.out.println("═══════════════════════════════════════");
        for (String cap : capabilities) {
            System.out.println("  ✓ " + cap);
        }
        System.out.println("═══════════════════════════════════════");
    }
}
