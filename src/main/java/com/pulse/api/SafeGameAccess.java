package com.pulse.api;

import java.lang.reflect.Method;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Function;
import java.util.function.Supplier;

/**
 * Thread-safe하고 fallback을 제공하는 게임 객체 접근 API.
 * 안전한 리플렉션 wrapper로 예외 발생 시 fallback 값을 반환합니다.
 * 
 * <pre>
 * // 사용 예시 - 안전한 좀비 체력 조회
 * float health = SafeGameAccess.withZombie(zombie, z -> {
 *     Method getHealth = z.getClass().getMethod("getHealth");
 *     return (Float) getHealth.invoke(z);
 * }, 100.0f); // fallback 값
 * 
 * // 메인 스레드에서 실행
 * SafeGameAccess.runOnMainThread(() -> {
 *     // 게임 상태 변경
 * });
 * </pre>
 * 
 * @since 1.0.1
 */
@PublicAPI(since = "1.0.1", status = PublicAPI.Status.EXPERIMENTAL)
public final class SafeGameAccess {

    // 메인 스레드 관련
    private static volatile Thread mainThread = null;
    private static final ConcurrentLinkedQueue<Runnable> mainThreadQueue = new ConcurrentLinkedQueue<>();
    private static final AtomicBoolean processingQueue = new AtomicBoolean(false);

    private SafeGameAccess() {
    } // 인스턴스화 방지

    // ═══════════════════════════════════════════════════════════════
    // 메인 스레드 설정 (Pulse 내부용)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 메인 스레드 설정 (PulseAgent에서 호출).
     */
    @InternalAPI
    public static void setMainThread(Thread thread) {
        mainThread = thread;
    }

    /**
     * 현재 메인 스레드에서 실행 중인지 확인.
     */
    public static boolean isOnMainThread() {
        return mainThread != null && Thread.currentThread() == mainThread;
    }

    // ═══════════════════════════════════════════════════════════════
    // Zombie 관련 안전 접근
    // ═══════════════════════════════════════════════════════════════

    /**
     * 좀비 객체에 안전하게 접근.
     * 
     * @param zombie   좀비 객체 (IsoZombie)
     * @param accessor 접근자 함수
     * @param fallback 실패 시 반환값
     * @return 접근 결과 또는 fallback
     */
    public static <T> T withZombie(Object zombie, Function<Object, T> accessor, T fallback) {
        if (zombie == null)
            return fallback;
        try {
            return accessor.apply(zombie);
        } catch (Exception e) {
            if (DevMode.isEnabled()) {
                System.err.println("[SafeGameAccess] Zombie access failed: " + e.getMessage());
            }
            return fallback;
        }
    }

    /**
     * 주변 좀비 목록 안전 조회.
     * 
     * @param x      중심 X 좌표
     * @param y      중심 Y 좌표
     * @param radius 반경
     * @return 좀비 리스트 Optional
     */
    public static Optional<List<Object>> getNearbyZombiesSafe(float x, float y, float radius) {
        try {
            List<Object> zombies = GameAccess.getNearbyZombies(x, y, radius);
            return Optional.ofNullable(zombies);
        } catch (Exception e) {
            if (DevMode.isEnabled()) {
                System.err.println("[SafeGameAccess] getNearbyZombies failed: " + e.getMessage());
            }
            return Optional.empty();
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Chunk 관련 안전 접근
    // ═══════════════════════════════════════════════════════════════

    /**
     * 청크 객체에 안전하게 접근.
     * 
     * @param chunk    청크 객체 (IsoChunk)
     * @param accessor 접근자 함수
     * @param fallback 실패 시 반환값
     * @return 접근 결과 또는 fallback
     */
    public static <T> T withChunk(Object chunk, Function<Object, T> accessor, T fallback) {
        if (chunk == null)
            return fallback;
        try {
            return accessor.apply(chunk);
        } catch (Exception e) {
            if (DevMode.isEnabled()) {
                System.err.println("[SafeGameAccess] Chunk access failed: " + e.getMessage());
            }
            return fallback;
        }
    }

    /**
     * 월드 좌표로 청크 안전 조회.
     * 
     * @param wx 월드 X 좌표
     * @param wy 월드 Y 좌표
     * @return 청크 Optional
     */
    public static Optional<Object> getChunkSafe(int wx, int wy) {
        try {
            Object world = getIsoWorldInstanceInternal();
            if (world == null)
                return Optional.empty();

            // IsoWorld.CurrentCell.getChunk(wx, wy)
            Method getCellMethod = world.getClass().getMethod("getCell");
            Object cell = getCellMethod.invoke(world);
            if (cell == null)
                return Optional.empty();

            Method getChunkMethod = cell.getClass().getMethod("getChunk", int.class, int.class);
            Object chunk = getChunkMethod.invoke(cell, wx, wy);
            return Optional.ofNullable(chunk);
        } catch (Exception e) {
            if (DevMode.isEnabled()) {
                System.err.println("[SafeGameAccess] getChunk failed: " + e.getMessage());
            }
            return Optional.empty();
        }
    }

    /**
     * 내부용 IsoWorld 인스턴스 조회 (리플렉션).
     */
    private static Object getIsoWorldInstanceInternal() {
        try {
            Object world = GameAccess.getStaticField("zombie.iso.IsoWorld", "instance");
            if (world != null)
                return world;

            // 대안: 클래스 직접 로드 시도
            Class<?> isoWorldClass = GameAccess.getGameClass("zombie.iso.IsoWorld");
            if (isoWorldClass != null) {
                java.lang.reflect.Field instanceField = isoWorldClass.getDeclaredField("instance");
                instanceField.setAccessible(true);
                return instanceField.get(null);
            }
        } catch (Exception e) {
            // ignore
        }
        return null;
    }

    // ═══════════════════════════════════════════════════════════════
    // AI 관련 안전 접근
    // ═══════════════════════════════════════════════════════════════

    /**
     * AI 객체에 안전하게 접근.
     * 
     * @param ai       AI 객체
     * @param accessor 접근자 함수
     * @param fallback 실패 시 반환값
     * @return 접근 결과 또는 fallback
     */
    public static <T> T withAI(Object ai, Function<Object, T> accessor, T fallback) {
        if (ai == null)
            return fallback;
        try {
            return accessor.apply(ai);
        } catch (Exception e) {
            if (DevMode.isEnabled()) {
                System.err.println("[SafeGameAccess] AI access failed: " + e.getMessage());
            }
            return fallback;
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // Lua 관련 안전 접근
    // ═══════════════════════════════════════════════════════════════

    /**
     * Lua 상태에 안전하게 접근.
     * 
     * @param accessor 접근자 함수
     * @param fallback 실패 시 반환값
     * @return 접근 결과 또는 fallback
     */
    public static <T> T withLuaState(Function<Object, T> accessor, T fallback) {
        try {
            // LuaManager.GlobalEnvironment 접근
            Object luaEnv = GameAccess.getStaticField("se.krka.kahlua.vm.LuaState", "instance");
            if (luaEnv == null) {
                // 대체 경로
                Object platform = GameAccess.getStaticField("se.krka.kahlua.j2se.J2SEPlatform", "instance");
                if (platform != null) {
                    Method newEnvMethod = platform.getClass().getMethod("newEnvironment");
                    luaEnv = newEnvMethod.invoke(platform);
                }
            }

            if (luaEnv != null) {
                return accessor.apply(luaEnv);
            }
            return fallback;
        } catch (Exception e) {
            if (DevMode.isEnabled()) {
                System.err.println("[SafeGameAccess] Lua state access failed: " + e.getMessage());
            }
            return fallback;
        }
    }

    /**
     * Lua 호출이 스레드 안전한지 확인.
     * PZ의 Lua는 기본적으로 메인 스레드에서만 호출 가능.
     * 
     * @return 현재 스레드에서 Lua 호출이 안전하면 true
     */
    public static boolean isLuaThreadSafe() {
        return isOnMainThread();
    }

    // ═══════════════════════════════════════════════════════════════
    // 스레드 안전 실행
    // ═══════════════════════════════════════════════════════════════

    /**
     * 메인 스레드에서 실행.
     * 이미 메인 스레드에 있다면 즉시 실행,
     * 아니면 큐에 추가되어 다음 틱에 실행.
     * 
     * @param action 실행할 액션
     */
    public static void runOnMainThread(Runnable action) {
        if (action == null)
            return;

        if (isOnMainThread()) {
            try {
                action.run();
            } catch (Exception e) {
                System.err.println("[SafeGameAccess] Main thread action failed: " + e.getMessage());
                if (DevMode.isEnabled()) {
                    e.printStackTrace();
                }
            }
        } else {
            mainThreadQueue.offer(action);
        }
    }

    /**
     * 메인 스레드에서 실행하고 결과 반환 (CompletableFuture).
     * 
     * @param action 실행할 작업
     * @return CompletableFuture with result
     */
    public static <T> CompletableFuture<T> callOnMainThread(Supplier<T> action) {
        CompletableFuture<T> future = new CompletableFuture<>();

        runOnMainThread(() -> {
            try {
                T result = action.get();
                future.complete(result);
            } catch (Exception e) {
                future.completeExceptionally(e);
            }
        });

        return future;
    }

    /**
     * 큐에 있는 모든 액션 처리 (게임 틱에서 호출).
     */
    @InternalAPI
    public static void processMainThreadQueue() {
        if (!processingQueue.compareAndSet(false, true))
            return;

        try {
            Runnable action;
            int processed = 0;
            while ((action = mainThreadQueue.poll()) != null && processed < 100) {
                try {
                    action.run();
                } catch (Exception e) {
                    System.err.println("[SafeGameAccess] Queued action failed: " + e.getMessage());
                }
                processed++;
            }
        } finally {
            processingQueue.set(false);
        }
    }

    /**
     * 큐 크기 반환.
     */
    public static int getQueueSize() {
        return mainThreadQueue.size();
    }

    // ═══════════════════════════════════════════════════════════════
    // 범용 안전 접근
    // ═══════════════════════════════════════════════════════════════

    /**
     * 임의 객체에 안전하게 accessor 적용.
     * 
     * @param target   대상 객체
     * @param accessor 접근자 함수
     * @param fallback 실패 시 반환값
     * @return 결과 또는 fallback
     */
    public static <T, R> R safely(T target, Function<T, R> accessor, R fallback) {
        if (target == null)
            return fallback;
        try {
            return accessor.apply(target);
        } catch (Exception e) {
            if (DevMode.isEnabled()) {
                System.err.println("[SafeGameAccess] Safe access failed: " + e.getMessage());
            }
            return fallback;
        }
    }

    /**
     * 안전하게 메서드 호출.
     * 
     * @param target     대상 객체
     * @param methodName 메서드 이름
     * @param fallback   실패 시 반환값
     * @param args       인자들
     * @return 결과 또는 fallback
     */
    @SuppressWarnings("unchecked")
    public static <T> T safeInvoke(Object target, String methodName, T fallback, Object... args) {
        if (target == null)
            return fallback;
        try {
            Class<?>[] paramTypes = new Class<?>[args.length];
            for (int i = 0; i < args.length; i++) {
                paramTypes[i] = args[i] != null ? args[i].getClass() : Object.class;
            }

            Method method = target.getClass().getMethod(methodName, paramTypes);
            return (T) method.invoke(target, args);
        } catch (Exception e) {
            if (DevMode.isEnabled()) {
                System.err.println("[SafeGameAccess] safeInvoke(" + methodName + ") failed: " + e.getMessage());
            }
            return fallback;
        }
    }
}
