package com.pulse.hook;

import com.pulse.api.log.PulseLogger;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;

/**
 * 중앙 집중식 Hook 관리자.
 * 
 * Echo, Fuse, Nerve 등 모든 모드가 공용으로 사용하는 후킹 레지스트리입니다.
 * 이 클래스는 Pulse가 버전별(B41/B42) 호환성을 관리하고,
 * 개별 모드들은 이 API를 통해 안전하게 콜백을 등록/해제합니다.
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 콜백 등록 (기본 우선순위)
 * PulseHookRegistry.register(HookTypes.TICK_PHASE, myTickCallback);
 * 
 * // 콜백 등록 (높은 우선순위)
 * PulseHookRegistry.register(HookTypes.TICK_PHASE, myPriorityCallback, PulseHookRegistry.PRIORITY_HIGH);
 * 
 * // 콜백 해제
 * PulseHookRegistry.unregister(HookTypes.TICK_PHASE, myTickCallback);
 * 
 * // 모든 콜백에 이벤트 브로드캐스트
 * PulseHookRegistry.broadcast(HookTypes.TICK_PHASE, cb -> cb.onTickStart());
 * }</pre>
 * 
 * @since Pulse 1.2
 * @since Pulse 0.9 - Added priority support and slow hook detection
 */
public final class PulseHookRegistry {

    // Priority constants
    public static final int PRIORITY_LOWEST = -1000;
    public static final int PRIORITY_LOW = -100;
    public static final int PRIORITY_NORMAL = 0;
    public static final int PRIORITY_HIGH = 100;
    public static final int PRIORITY_HIGHEST = 1000;

    // Slow hook detection
    private static final long HOOK_TIMEOUT_MS = 100;
    private static int slowHookWarningCount = 0;
    private static final int MAX_SLOW_HOOK_WARNINGS = 10;

    private static final Map<HookType<?>, Boolean> registeredTypes = new ConcurrentHashMap<>();
    private static final Map<Object, Integer> callbackPriorities = new ConcurrentHashMap<>();
    private static final Map<Object, String> callbackOwners = new ConcurrentHashMap<>();

    private static volatile boolean debugEnabled = false;
    private static final String LOG = PulseLogger.PULSE;

    private PulseHookRegistry() {
        // Utility class
    }

    /**
     * 콜백 등록 (기본 우선순위)
     * 
     * @param type     Hook 타입
     * @param callback 등록할 콜백
     * @throws NullPointerException type 또는 callback이 null인 경우
     */
    public static <T> void register(HookType<T> type, T callback) {
        register(type, callback, PRIORITY_NORMAL, null);
    }

    /**
     * 콜백 등록 (modId 지정)
     * 
     * @param type     Hook 타입
     * @param callback 등록할 콜백
     * @param modId    소유 모드 ID (리로드 시 일괄 해제용)
     */
    public static <T> void register(HookType<T> type, T callback, String modId) {
        register(type, callback, PRIORITY_NORMAL, modId);
    }

    /**
     * 콜백 등록 (우선순위 지정)
     * 
     * @param type     Hook 타입
     * @param callback 등록할 콜백
     * @param priority 우선순위 (높을수록 먼저 실행)
     * @throws NullPointerException type 또는 callback이 null인 경우
     */
    public static <T> void register(HookType<T> type, T callback, int priority) {
        register(type, callback, priority, null);
    }

    /**
     * 콜백 등록 (우선순위 + modId 지정)
     * 
     * @param type     Hook 타입
     * @param callback 등록할 콜백
     * @param priority 우선순위 (높을수록 먼저 실행)
     * @param modId    소유 모드 ID (null 가능)
     */
    public static <T> void register(HookType<T> type, T callback, int priority, String modId) {
        if (type == null) {
            throw new NullPointerException("HookType cannot be null");
        }
        if (callback == null) {
            throw new NullPointerException("Callback cannot be null");
        }

        List<T> callbacks = type.getCallbacksInternal();
        if (!callbacks.contains(callback)) {
            callbacks.add(callback);
            callbackPriorities.put(callback, priority);
            if (modId != null) {
                callbackOwners.put(callback, modId);
            }
            registeredTypes.put(type, true);

            // Sort by priority (higher first)
            sortCallbacksByPriority(callbacks);

            if (debugEnabled) {
                PulseLogger.debug(LOG, "[HookRegistry] Registered callback for {} (priority={}, total={})",
                        type.getName(), priority, callbacks.size());
            }
        }
    }

    /**
     * Sort callbacks by priority (higher priority first)
     */
    private static <T> void sortCallbacksByPriority(List<T> callbacks) {
        // Create a copy, sort it, then update the original
        List<T> sorted = new ArrayList<>(callbacks);
        sorted.sort((a, b) -> {
            int priorityA = callbackPriorities.getOrDefault(a, PRIORITY_NORMAL);
            int priorityB = callbackPriorities.getOrDefault(b, PRIORITY_NORMAL);
            return Integer.compare(priorityB, priorityA); // Descending (higher first)
        });
        callbacks.clear();
        callbacks.addAll(sorted);
    }

    /**
     * 콜백 해제
     * 
     * @param type     Hook 타입
     * @param callback 해제할 콜백
     * @return 콜백이 존재하여 제거되었으면 true
     */
    public static <T> boolean unregister(HookType<T> type, T callback) {
        if (type == null || callback == null) {
            return false;
        }

        List<T> callbacks = type.getCallbacksInternal();
        boolean removed = callbacks.remove(callback);

        if (removed) {
            callbackPriorities.remove(callback);
            callbackOwners.remove(callback);
            if (debugEnabled) {
                PulseLogger.debug(LOG, "[HookRegistry] Unregistered callback for {} (remaining: {})",
                        type.getName(), callbacks.size());
            }
        }

        return removed;
    }

    /**
     * 등록된 모든 콜백 가져오기
     * 
     * @param type Hook 타입
     * @return 등록된 콜백 리스트 (읽기 전용)
     */
    public static <T> List<T> getCallbacks(HookType<T> type) {
        if (type == null) {
            return Collections.emptyList();
        }
        return Collections.unmodifiableList(type.getCallbacksInternal());
    }

    /**
     * 콜백 존재 여부 확인
     */
    public static <T> boolean hasCallbacks(HookType<T> type) {
        return type != null && !type.getCallbacksInternal().isEmpty();
    }

    /**
     * 등록된 모든 콜백에 이벤트 브로드캐스트
     * 
     * 각 콜백에서 발생하는 예외는 로그에 기록되고, 다른 콜백 실행에 영향을 주지 않습니다.
     * Slow hook detection: 100ms 이상 걸리면 경고 로그 (rate-limited)
     * 
     * @param type   Hook 타입
     * @param action 각 콜백에 실행할 액션
     */
    public static <T> void broadcast(HookType<T> type, Consumer<T> action) {
        if (type == null || action == null) {
            return;
        }

        List<T> callbacks = type.getCallbacksInternal();
        for (T callback : callbacks) {
            long start = System.nanoTime();
            try {
                action.accept(callback);
            } catch (Throwable t) {
                PulseLogger.error(LOG, "[HookRegistry] Error in callback for {}: {}", type.getName(), t.getMessage());
                if (debugEnabled) {
                    PulseLogger.error(LOG, "Stack trace", t);
                }
            } finally {
                long elapsedMs = (System.nanoTime() - start) / 1_000_000;
                if (elapsedMs > HOOK_TIMEOUT_MS && slowHookWarningCount < MAX_SLOW_HOOK_WARNINGS) {
                    slowHookWarningCount++;
                    PulseLogger.warn(LOG, "[HookRegistry] Slow hook detected ({}ms): {} for {} (warning {}/{})",
                            elapsedMs, callback.getClass().getName(), type.getName(), slowHookWarningCount,
                            MAX_SLOW_HOOK_WARNINGS);
                }
            }
        }
    }

    /**
     * 특정 Hook의 모든 콜백 제거
     */
    public static <T> void clearCallbacks(HookType<T> type) {
        if (type != null) {
            List<T> callbacks = type.getCallbacksInternal();
            for (T callback : callbacks) {
                callbackPriorities.remove(callback);
            }
            callbacks.clear();
            if (debugEnabled) {
                PulseLogger.debug(LOG, "[HookRegistry] Cleared all callbacks for {}", type.getName());
            }
        }
    }

    /**
     * 특정 modId의 모든 콜백 제거
     * 
     * @param modId 모드 ID
     * @return 제거된 콜백 수
     */
    public static int unregisterAll(String modId) {
        if (modId == null || modId.isEmpty()) {
            return 0;
        }

        int removed = 0;

        // 모든 HookType 순회하여 해당 modId의 콜백 제거
        for (HookType<?> type : registeredTypes.keySet()) {
            removed += unregisterAllFromType(type, modId);
        }

        if (debugEnabled && removed > 0) {
            PulseLogger.debug(LOG, "[HookRegistry] Unregistered {} callbacks for mod: {}", removed, modId);
        }

        return removed;
    }

    /**
     * 특정 HookType에서 modId의 콜백 제거
     */
    private static <T> int unregisterAllFromType(HookType<T> type, String modId) {
        List<T> callbacks = type.getCallbacksInternal();
        List<T> toRemove = new java.util.ArrayList<>();

        for (T callback : callbacks) {
            String owner = callbackOwners.get(callback);
            if (modId.equals(owner)) {
                toRemove.add(callback);
            }
        }

        for (T callback : toRemove) {
            callbacks.remove(callback);
            callbackPriorities.remove(callback);
            callbackOwners.remove(callback);
        }

        return toRemove.size();
    }

    /**
     * 디버그 모드 설정
     */
    public static void setDebugEnabled(boolean enabled) {
        debugEnabled = enabled;
    }

    /**
     * 디버그 모드 상태
     */
    public static boolean isDebugEnabled() {
        return debugEnabled;
    }

    /**
     * 등록된 Hook 타입 수
     */
    public static int getRegisteredTypeCount() {
        return registeredTypes.size();
    }

    /**
     * Slow hook warning 카운터 리셋 (테스트용)
     */
    public static void resetSlowHookWarnings() {
        slowHookWarningCount = 0;
    }

    /**
     * 전체 상태 요약 (디버깅용)
     */
    public static String getStatusSummary() {
        StringBuilder sb = new StringBuilder();
        sb.append("PulseHookRegistry Status:\n");
        sb.append("  Debug: ").append(debugEnabled).append("\n");
        sb.append("  Slow Hook Warnings: ").append(slowHookWarningCount).append("/").append(MAX_SLOW_HOOK_WARNINGS)
                .append("\n");
        sb.append("  Registered Hook Types: ").append(registeredTypes.size()).append("\n");

        for (HookType<?> type : registeredTypes.keySet()) {
            int count = type.getCallbacksInternal().size();
            sb.append("    - ").append(type.getName()).append(": ").append(count).append(" callbacks\n");
        }

        return sb.toString();
    }
}
