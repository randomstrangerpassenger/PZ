package com.pulse.lifecycle;

import com.pulse.api.di.PulseServices;
import com.pulse.api.log.PulseLogger;
import com.pulse.di.PulseServiceLocator;
import com.pulse.lua.LuaBridge;
import com.pulse.mod.ModLoader;

import java.io.Closeable;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Pulse 생명주기 관리자.
 * 
 * 게임 시작/종료 시 리소스 초기화 및 정리를 담당합니다.
 * 모든 Pulse 컴포넌트의 정리를 보장합니다.
 * 
 * @since 1.2.0
 */
public final class LifecycleManager {

    private static final LifecycleManager INSTANCE = new LifecycleManager();
    private static final String LOG = PulseLogger.PULSE;

    // 정리 대상 컴포넌트 목록
    private final List<ShutdownHook> shutdownHooks = new CopyOnWriteArrayList<>();
    private final List<Closeable> closeables = new CopyOnWriteArrayList<>();

    // 셧다운 상태
    private volatile boolean shuttingDown = false;
    private volatile boolean shutdownComplete = false;

    private LifecycleManager() {
        // JVM 셧다운 훅 등록
        Runtime.getRuntime().addShutdownHook(new Thread(this::shutdown, "Pulse-ShutdownHook"));
    }

    public static LifecycleManager getInstance() {
        return INSTANCE;
    }

    // ───────────────────────────────────────────────────────────────
    // 등록 API
    // ───────────────────────────────────────────────────────────────

    /**
     * 셧다운 시 호출될 훅 등록
     */
    public void registerShutdownHook(ShutdownHook hook) {
        if (!shuttingDown) {
            shutdownHooks.add(hook);
        }
    }

    /**
     * 셧다운 시 close()를 호출할 Closeable 등록
     */
    public void registerCloseable(Closeable closeable) {
        if (!shuttingDown) {
            closeables.add(closeable);
        }
    }

    /**
     * 셧다운 훅 해제
     */
    public void unregisterShutdownHook(ShutdownHook hook) {
        shutdownHooks.remove(hook);
    }

    // ───────────────────────────────────────────────────────────────
    // 초기화 / 셧다운
    // ───────────────────────────────────────────────────────────────

    /**
     * Pulse 초기화 완료 시 호출 (선택적)
     */
    public void onInitialized() {
        PulseLogger.info(LOG, "[Lifecycle] Pulse initialized");
        shuttingDown = false;
        shutdownComplete = false;
    }

    /**
     * 게임 종료 시 리소스 정리
     */
    public void shutdown() {
        if (shuttingDown || shutdownComplete) {
            return;
        }

        shuttingDown = true;
        PulseLogger.info(LOG, "[Lifecycle] Shutting down Pulse...");

        List<String> errors = new ArrayList<>();

        // 1. 사용자 정의 셧다운 훅 호출
        for (ShutdownHook hook : shutdownHooks) {
            try {
                hook.onShutdown();
            } catch (Throwable t) {
                errors.add("ShutdownHook: " + t.getMessage());
                PulseLogger.error(LOG, "[Lifecycle] Shutdown hook failed: {}", t.getMessage());
            }
        }
        shutdownHooks.clear();

        // 2. Closeable 리소스 정리
        for (Closeable closeable : closeables) {
            try {
                closeable.close();
            } catch (Throwable t) {
                errors.add("Closeable: " + t.getMessage());
                PulseLogger.error(LOG, "[Lifecycle] Closeable.close() failed: {}", t.getMessage());
            }
        }
        closeables.clear();

        // 3. 핵심 컴포넌트 정리
        try {
            PulseServices.scheduler().shutdown();
            PulseLogger.debug(LOG, "[Lifecycle] Scheduler shutdown complete");
        } catch (Throwable t) {
            errors.add("Scheduler: " + t.getMessage());
        }

        try {
            PulseServices.events().clearAll();
            PulseLogger.debug(LOG, "[Lifecycle] EventBus cleared");
        } catch (Throwable t) {
            errors.add("EventBus: " + t.getMessage());
        }

        try {
            PulseServiceLocator.getInstance().clear();
            PulseLogger.debug(LOG, "[Lifecycle] ServiceLocator cleared");
        } catch (Throwable t) {
            errors.add("ServiceLocator: " + t.getMessage());
        }

        try {
            LuaBridge.reinitialize();
            PulseLogger.debug(LOG, "[Lifecycle] LuaBridge reset");
        } catch (Throwable t) {
            errors.add("LuaBridge: " + t.getMessage());
        }

        // 4. 모드 언로드
        try {
            ModLoader loader = ModLoader.getInstance();
            loader.unloadAll();
            PulseLogger.debug(LOG, "[Lifecycle] Mods unloaded");
        } catch (Throwable t) {
            errors.add("ModLoader: " + t.getMessage());
        }

        shutdownComplete = true;

        if (errors.isEmpty()) {
            PulseLogger.info(LOG, "[Lifecycle] Pulse shutdown complete");
        } else {
            PulseLogger.warn(LOG, "[Lifecycle] Pulse shutdown complete with {} errors", errors.size());
        }
    }

    /**
     * 셧다운 상태 확인
     */
    public boolean isShuttingDown() {
        return shuttingDown;
    }

    /**
     * 셧다운 완료 여부
     */
    public boolean isShutdownComplete() {
        return shutdownComplete;
    }

    // ───────────────────────────────────────────────────────────────
    // 셧다운 훅 인터페이스
    // ───────────────────────────────────────────────────────────────

    @FunctionalInterface
    public interface ShutdownHook {
        void onShutdown();
    }
}
