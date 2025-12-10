package com.echo.event;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;

/**
 * Echo 이벤트 리스너
 * 
 * Pulse 이벤트 버스와 연동하여 자동으로 프로파일링 포인트를 측정합니다.
 * 
 * 지원 이벤트:
 * - OnTick (게임 틱)
 * - OnRenderTick (렌더링)
 * - OnZombiesUpdate (좀비 AI)
 */
public class EchoEventListener {

    private static final EchoProfiler profiler = EchoProfiler.getInstance();

    // 현재 활성 스코프 (수동 관리용)
    private static EchoProfiler.ProfilingScope currentTickScope = null;
    private static EchoProfiler.ProfilingScope currentRenderScope = null;

    /**
     * 게임 틱 시작
     * Pulse OnTick.Pre 이벤트에서 호출
     */
    public static void onTickStart() {
        if (!profiler.isEnabled())
            return;
        currentTickScope = profiler.scope(ProfilingPoint.TICK);
    }

    /**
     * 게임 틱 종료
     * Pulse OnTick.Post 이벤트에서 호출
     */
    public static void onTickEnd() {
        if (currentTickScope != null) {
            currentTickScope.close();
            currentTickScope = null;
        }
    }

    /**
     * 렌더링 시작
     */
    public static void onRenderStart() {
        if (!profiler.isEnabled())
            return;
        currentRenderScope = profiler.scope(ProfilingPoint.RENDER);
    }

    /**
     * 렌더링 종료
     */
    public static void onRenderEnd() {
        if (currentRenderScope != null) {
            currentRenderScope.close();
            currentRenderScope = null;
        }
    }

    /**
     * 좀비 AI 업데이트 래퍼
     * Callable 방식으로 기존 로직을 감싸서 측정
     */
    public static void profileZombieAI(Runnable zombieUpdate) {
        if (!profiler.isEnabled()) {
            zombieUpdate.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.ZOMBIE_AI)) {
            zombieUpdate.run();
        }
    }

    /**
     * 물리 엔진 업데이트 래퍼
     */
    public static void profilePhysics(Runnable physicsUpdate) {
        if (!profiler.isEnabled()) {
            physicsUpdate.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.PHYSICS)) {
            physicsUpdate.run();
        }
    }

    /**
     * 네트워크 처리 래퍼
     */
    public static void profileNetwork(Runnable networkUpdate) {
        if (!profiler.isEnabled()) {
            networkUpdate.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.NETWORK)) {
            networkUpdate.run();
        }
    }

    /**
     * 청크 I/O 래퍼
     */
    public static void profileChunkIO(Runnable chunkIO, String chunkInfo) {
        if (!profiler.isEnabled()) {
            chunkIO.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.CHUNK_IO, chunkInfo)) {
            chunkIO.run();
        }
    }

    /**
     * Lua 이벤트 래퍼 (On-Demand)
     */
    public static void profileLuaEvent(Runnable luaCallback, String eventName) {
        if (!profiler.isEnabled() || !profiler.isLuaProfilingEnabled()) {
            luaCallback.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.LUA_EVENT, eventName)) {
            luaCallback.run();
        }
    }

    /**
     * Lua 함수 호출 래퍼 (On-Demand)
     */
    public static void profileLuaFunction(Runnable luaFunction, String functionName) {
        if (!profiler.isEnabled() || !profiler.isLuaProfilingEnabled()) {
            luaFunction.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.LUA_FUNCTION, functionName)) {
            luaFunction.run();
        }
    }

    /**
     * 모드 틱 핸들러 래퍼
     */
    public static void profileModTick(Runnable modTick, String modId) {
        if (!profiler.isEnabled()) {
            modTick.run();
            return;
        }

        try (var scope = profiler.scope(ProfilingPoint.MOD_TICK, modId)) {
            modTick.run();
        }
    }

    /**
     * 범용 프로파일링 래퍼
     */
    public static void profile(ProfilingPoint point, Runnable task) {
        if (!profiler.isEnabled()) {
            task.run();
            return;
        }

        try (var scope = profiler.scope(point)) {
            task.run();
        }
    }

    /**
     * 범용 프로파일링 래퍼 (라벨 포함)
     */
    public static void profile(ProfilingPoint point, String label, Runnable task) {
        if (!profiler.isEnabled()) {
            task.run();
            return;
        }

        try (var scope = profiler.scope(point, label)) {
            task.run();
        }
    }
}
