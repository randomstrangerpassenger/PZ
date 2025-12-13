package com.echo.pulse;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;

/**
 * 서브시스템 프로파일러
 * 
 * 개별 게임 서브시스템(Zombie AI, Physics, Network 등)을 측정합니다.
 * Callable wrapping 방식으로 기존 로직을 감싸서 사용합니다.
 */
public class SubsystemProfiler {

    private static final EchoProfiler profiler = EchoProfiler.getInstance();

    // --- AI 서브시스템 ---

    /**
     * 좀비 AI 업데이트 래퍼
     */
    public static void profileZombieAI(Runnable zombieUpdate) {
        profile(ProfilingPoint.ZOMBIE_AI, zombieUpdate);
    }

    /**
     * 좀비 AI 업데이트 래퍼 (라벨 포함)
     */
    public static void profileZombieAI(String label, Runnable zombieUpdate) {
        profile(ProfilingPoint.ZOMBIE_AI, label, zombieUpdate);
    }

    /**
     * NPC AI 업데이트 래퍼
     */
    public static void profileNpcAI(Runnable npcUpdate) {
        profile(ProfilingPoint.NPC_AI, npcUpdate);
    }

    /**
     * NPC AI 업데이트 래퍼 (라벨 포함)
     */
    public static void profileNpcAI(String label, Runnable npcUpdate) {
        profile(ProfilingPoint.NPC_AI, label, npcUpdate);
    }

    // --- 물리/시뮬레이션 ---

    /**
     * 물리 엔진 업데이트 래퍼
     */
    public static void profilePhysics(Runnable physicsUpdate) {
        profile(ProfilingPoint.PHYSICS, physicsUpdate);
    }

    /**
     * 시뮬레이션 업데이트 래퍼
     */
    public static void profileSimulation(Runnable simulation) {
        profile(ProfilingPoint.SIMULATION, simulation);
    }

    // --- I/O & 네트워크 ---

    /**
     * 네트워크 처리 래퍼
     */
    public static void profileNetwork(Runnable networkUpdate) {
        profile(ProfilingPoint.NETWORK, networkUpdate);
    }

    /**
     * 네트워크 처리 래퍼 (라벨 포함)
     */
    public static void profileNetwork(String label, Runnable networkUpdate) {
        profile(ProfilingPoint.NETWORK, label, networkUpdate);
    }

    /**
     * 청크 I/O 래퍼
     */
    public static void profileChunkIO(Runnable chunkIO) {
        profile(ProfilingPoint.CHUNK_IO, chunkIO);
    }

    /**
     * 청크 I/O 래퍼 (라벨 포함)
     */
    public static void profileChunkIO(String label, Runnable chunkIO) {
        profile(ProfilingPoint.CHUNK_IO, label, chunkIO);
    }

    // --- 오디오 ---

    /**
     * 오디오 처리 래퍼
     */
    public static void profileAudio(Runnable audioUpdate) {
        profile(ProfilingPoint.AUDIO, audioUpdate);
    }

    // --- 렌더링 ---

    /**
     * 렌더링 래퍼
     */
    public static void profileRender(Runnable render) {
        profile(ProfilingPoint.RENDER, render);
    }

    /**
     * 월드 렌더링 래퍼
     */
    public static void profileWorldRender(Runnable worldRender) {
        profile(ProfilingPoint.RENDER_WORLD, worldRender);
    }

    /**
     * UI 렌더링 래퍼
     */
    public static void profileUIRender(Runnable uiRender) {
        profile(ProfilingPoint.RENDER_UI, uiRender);
    }

    // --- 모드 관련 ---

    /**
     * 모드 초기화 래퍼
     */
    public static void profileModInit(String modId, Runnable modInit) {
        profile(ProfilingPoint.MOD_INIT, modId, modInit);
    }

    /**
     * 모드 틱 래퍼
     */
    public static void profileModTick(String modId, Runnable modTick) {
        profile(ProfilingPoint.MOD_TICK, modId, modTick);
    }

    // --- 커스텀 측정 ---

    /**
     * 커스텀 측정 1
     */
    public static void profileCustom1(String label, Runnable task) {
        profile(ProfilingPoint.CUSTOM_1, label, task);
    }

    /**
     * 커스텀 측정 2
     */
    public static void profileCustom2(String label, Runnable task) {
        profile(ProfilingPoint.CUSTOM_2, label, task);
    }

    /**
     * 커스텀 측정 3
     */
    public static void profileCustom3(String label, Runnable task) {
        profile(ProfilingPoint.CUSTOM_3, label, task);
    }

    // --- 범용 메서드 ---

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

    /**
     * 결과를 반환하는 프로파일링 래퍼
     */
    public static <T> T profileWithResult(ProfilingPoint point, java.util.function.Supplier<T> task) {
        if (!profiler.isEnabled()) {
            return task.get();
        }

        try (var scope = profiler.scope(point)) {
            return task.get();
        }
    }

    /**
     * 결과를 반환하는 프로파일링 래퍼 (라벨 포함)
     */
    public static <T> T profileWithResult(ProfilingPoint point, String label, java.util.function.Supplier<T> task) {
        if (!profiler.isEnabled()) {
            return task.get();
        }

        try (var scope = profiler.scope(point, label)) {
            return task.get();
        }
    }
}
