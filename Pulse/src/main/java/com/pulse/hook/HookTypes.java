package com.pulse.hook;

import com.pulse.api.profiler.IsoGridHook;
import com.pulse.api.profiler.PathfindingHook;
import com.pulse.api.profiler.TickPhaseHook;
import com.pulse.api.profiler.ZombieHook;

/**
 * 사전 정의된 Hook 타입들.
 * 
 * Echo, Fuse, Nerve에서 공통으로 사용되는 Hook 타입 상수입니다.
 * 각 타입은 해당하는 콜백 인터페이스와 연결됩니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // TickPhase 콜백 등록
 * PulseHookRegistry.register(HookTypes.TICK_PHASE, myTickPhaseCallback);
 * 
 * // Zombie 프로파일링 콜백 등록
 * PulseHookRegistry.register(HookTypes.ZOMBIE, myZombieCallback);
 * }</pre>
 * 
 * @since Pulse 1.2
 */
public final class HookTypes {

    private HookTypes() {
        // Constants class
    }

    // ─────────────────────────────────────────────────────────────
    // Profiler Hooks (Echo/Fuse용)
    // ─────────────────────────────────────────────────────────────

    /**
     * Tick Phase 프로파일링 Hook
     * 
     * IsoWorld.update() 전후에 호출됩니다.
     */
    public static final HookType<TickPhaseHook.ITickPhaseCallback> TICK_PHASE = HookType.create("TICK_PHASE",
            TickPhaseHook.ITickPhaseCallback.class);

    /**
     * 좀비 업데이트 프로파일링 Hook
     * 
     * IsoZombie.update() 전후에 호출됩니다.
     */
    public static final HookType<ZombieHook.IZombieCallback> ZOMBIE = HookType.create("ZOMBIE",
            ZombieHook.IZombieCallback.class);

    /**
     * 경로 탐색 프로파일링 Hook
     * 
     * Pathfinding 관련 함수에서 호출됩니다.
     */
    public static final HookType<PathfindingHook.IPathfindingCallback> PATHFINDING = HookType.create("PATHFINDING",
            PathfindingHook.IPathfindingCallback.class);

    /**
     * IsoGrid 프로파일링 Hook
     * 
     * IsoGrid 업데이트 관련 함수에서 호출됩니다.
     */
    public static final HookType<IsoGridHook.IIsoGridCallback> ISO_GRID = HookType.create("ISO_GRID",
            IsoGridHook.IIsoGridCallback.class);

    // ─────────────────────────────────────────────────────────────
    // GamePhase Hooks (Phase 1.1에서 추가 예정)
    // ─────────────────────────────────────────────────────────────

    /**
     * 게임 틱 시작/끝 Hook
     */
    public static final HookType<IGameTickCallback> GAME_TICK = HookType.create("GAME_TICK", IGameTickCallback.class);

    /**
     * 렌더 프레임 Hook
     */
    public static final HookType<IRenderCallback> RENDER_FRAME = HookType.create("RENDER_FRAME", IRenderCallback.class);

    /**
     * 청크 로드/언로드 Hook
     */
    public static final HookType<IChunkCallback> CHUNK = HookType.create("CHUNK", IChunkCallback.class);

    /**
     * Lua Function Call Hook
     * 
     * Hooks into se.krka.kahlua.vm.KahluaThread.call/pcall
     */
    public static final HookType<ILuaCallCallback> LUA_CALL = HookType.create("LUA_CALL", ILuaCallCallback.class);

    // ─────────────────────────────────────────────────────────────
    // 콜백 인터페이스 정의 (Phase 1.1에서 구현 예정)
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua Call Callback Interface
     * 
     * NOTE: nanoTime 파라미터 메서드는 Echo 전용입니다.
     * 다른 모드는 이 파라미터에 의존하지 마세요.
     */
    public interface ILuaCallCallback {
        /**
         * Lua 함수 호출 시작 (legacy)
         * 
         * @param function Function object
         */
        default void onLuaCallStart(Object function) {
        }

        /**
         * Lua 함수 호출 종료 (legacy)
         * 
         * @param function Function object
         */
        default void onLuaCallEnd(Object function) {
        }

        /**
         * Lua 함수 호출 시작 (Echo 전용 - 정확한 시간 측정용)
         * 
         * @param function   Function object
         * @param startNanos System.nanoTime() at call start
         */
        default void onLuaCallStart(Object function, long startNanos) {
            onLuaCallStart(function); // 하위 호환성
        }

        /**
         * Lua 함수 호출 종료 (Echo 전용 - 정확한 시간 측정용)
         * 
         * @param function Function object
         * @param endNanos System.nanoTime() at call end
         */
        default void onLuaCallEnd(Object function, long endNanos) {
            onLuaCallEnd(function); // 하위 호환성
        }
    }

    /**
     * 게임 틱 콜백 인터페이스
     */
    public interface IGameTickCallback {
        /** IsoWorld.update() 진입 직전 */
        default void onGameTickStart(long tickNumber) {
        }

        /** IsoWorld.update() 종료 직후 */
        default void onGameTickEnd(long tickNumber, long durationNanos) {
        }
    }

    /**
     * 렌더 프레임 콜백 인터페이스
     */
    public interface IRenderCallback {
        /** 프레임 렌더링 시작 */
        default void onRenderStart() {
        }

        /** 프레임 렌더링 종료 */
        default void onRenderEnd(long durationNanos) {
        }
    }

    /**
     * 청크 콜백 인터페이스
     */
    public interface IChunkCallback {
        /** 청크 로드됨 */
        default void onChunkLoad(int chunkX, int chunkY) {
        }

        /** 청크 언로드됨 */
        default void onChunkUnload(int chunkX, int chunkY) {
        }
    }
}
