package com.pulse.api.di;

import com.pulse.api.access.IGameStateAccess;
import com.pulse.api.access.IWorldAccess;
import com.pulse.api.command.ICommandRegistry;
import com.pulse.api.event.IEventBus;
import com.pulse.api.hook.IPulseHookRegistry;
import com.pulse.api.profiler.IOptimizationPointRegistry;
import com.pulse.api.profiler.IProfilerBridge;
import com.pulse.api.scheduler.IScheduler;
import com.pulse.api.ui.IHUDOverlay;

/**
 * Pulse 서비스 접근 포인트.
 * 
 * @since Pulse 1.0
 * @since Pulse 2.0 - Phase 3: scheduler(), hud(), commands(), hooks(),
 *        profiler() 추가
 */
public final class PulseServices {
    private static IServiceLocator serviceLocator;
    private static IEventBus eventBus;
    private static IHUDOverlay hudOverlay;
    private static IScheduler scheduler;
    private static ICommandRegistry commandRegistry;
    private static IPulseHookRegistry hookRegistry;
    private static IProfilerBridge profilerBridge;
    private static IWorldAccess worldAccess;
    private static IGameStateAccess gameStateAccess;
    private static IOptimizationPointRegistry optimizationPointRegistry;

    private PulseServices() {
        throw new UnsupportedOperationException("Utility class");
    }

    /**
     * 서비스 로케이터 조회.
     */
    public static IServiceLocator getServiceLocator() {
        if (serviceLocator == null) {
            throw new IllegalStateException("Pulse not initialized");
        }
        return serviceLocator;
    }

    /**
     * 이벤트 버스 조회 (간편 접근자).
     */
    public static IEventBus events() {
        if (eventBus == null) {
            throw new IllegalStateException("Pulse not initialized");
        }
        return eventBus;
    }

    /**
     * 이벤트 버스 조회 (전체 메서드명).
     */
    public static IEventBus getEventBus() {
        return events();
    }

    /**
     * HUD 오버레이 조회.
     */
    public static IHUDOverlay hud() {
        if (hudOverlay == null) {
            throw new IllegalStateException("Pulse not initialized");
        }
        return hudOverlay;
    }

    /**
     * 스케줄러 조회.
     */
    public static IScheduler scheduler() {
        if (scheduler == null) {
            throw new IllegalStateException("Pulse not initialized");
        }
        return scheduler;
    }

    /**
     * 명령어 레지스트리 조회.
     * 
     * @since Pulse 2.0
     */
    public static ICommandRegistry commands() {
        if (commandRegistry == null) {
            throw new IllegalStateException("Pulse not initialized");
        }
        return commandRegistry;
    }

    /**
     * 훅 레지스트리 조회.
     * 
     * @since Pulse 2.0
     */
    public static IPulseHookRegistry hooks() {
        if (hookRegistry == null) {
            throw new IllegalStateException("Pulse not initialized");
        }
        return hookRegistry;
    }

    /**
     * 프로파일러 브릿지 조회.
     * 
     * @since Pulse 2.0
     */
    public static IProfilerBridge profiler() {
        if (profilerBridge == null) {
            throw new IllegalStateException("Pulse not initialized");
        }
        return profilerBridge;
    }

    /**
     * 월드 상태 접근.
     * 
     * @since Pulse 2.0 - Phase 4
     */
    public static IWorldAccess world() {
        if (worldAccess == null) {
            throw new IllegalStateException("Pulse not initialized");
        }
        return worldAccess;
    }

    /**
     * 게임 상태 접근.
     * 
     * @since Pulse 2.0 - Phase 4
     */
    public static IGameStateAccess gameState() {
        if (gameStateAccess == null) {
            throw new IllegalStateException("Pulse not initialized");
        }
        return gameStateAccess;
    }

    /**
     * 최적화 포인트 레지스트리 접근.
     * 
     * @since Pulse 2.0 - Phase 4
     */
    public static IOptimizationPointRegistry optimizationPoints() {
        if (optimizationPointRegistry == null) {
            throw new IllegalStateException("Pulse not initialized");
        }
        return optimizationPointRegistry;
    }

    /**
     * Pulse Core 전용 초기화 메서드.
     */
    public static void init(IServiceLocator locator, IEventBus bus, IHUDOverlay hud, IScheduler sched) {
        init(locator, bus, hud, sched, null, null, null);
    }

    /**
     * Pulse Core 전용 초기화 메서드 (전체 서비스).
     */
    public static void init(IServiceLocator locator, IEventBus bus, IHUDOverlay hud, IScheduler sched,
            ICommandRegistry commands, IPulseHookRegistry hooks, IProfilerBridge profiler) {
        init(locator, bus, hud, sched, commands, hooks, profiler, null, null);
    }

    /**
     * Pulse Core 전용 초기화 메서드 (전체 서비스 + Phase 4).
     */
    public static void init(IServiceLocator locator, IEventBus bus, IHUDOverlay hud, IScheduler sched,
            ICommandRegistry commands, IPulseHookRegistry hooks, IProfilerBridge profiler,
            IWorldAccess world, IGameStateAccess gameState) {
        // Security: StackWalker를 사용하여 호출자 검증
        StackWalker walker = StackWalker.getInstance(StackWalker.Option.RETAIN_CLASS_REFERENCE);
        Class<?> caller = walker.getCallerClass();

        if (!caller.getPackageName().startsWith("com.pulse.")) {
            throw new SecurityException("PulseServices.init() is Core-only. Caller: " + caller.getName());
        }

        if (serviceLocator != null || eventBus != null) {
            throw new IllegalStateException("Already initialized");
        }

        serviceLocator = locator;
        eventBus = bus;
        hudOverlay = hud;
        scheduler = sched;
        commandRegistry = commands;
        hookRegistry = hooks;
        profilerBridge = profiler;
        worldAccess = world;
        gameStateAccess = gameState;
    }
}
