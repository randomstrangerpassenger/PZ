package com.pulse.api.mixin;

import com.pulse.api.InternalAPI;
import com.pulse.api.PublicAPI;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.function.Consumer;
import java.util.stream.Collectors;

/**
 * Mixin 인젝션 검증 API.
 * Fuse/Nerve가 Mixin 인젝션 성공/실패를 확인하고 대응할 수 있습니다.
 * 
 * <pre>
 * // 사용 예시
 * InjectionResult result = MixinInjectionValidator.validateInjection(
 *         "com.fuse.mixin.ZombieAIMixin",
 *         "zombie.ai.ZombieAI");
 * 
 * if (!result.isSuccess()) {
 *     System.out.println("Mixin failed: " + result.getFailureReason());
 * }
 * 
 * // 콜백 등록
 * MixinInjectionValidator.onInjectionComplete(result -> {
 *     if (!result.isSuccess()) {
 *         Pulse.warn("Mixin failed: " + result.getMixinClass());
 *     }
 * });
 * </pre>
 * 
 * @since 1.0.1
 */
@PublicAPI(since = "1.0.1", status = PublicAPI.Status.EXPERIMENTAL)
public final class MixinInjectionValidator {

    // 인젝션 결과 저장
    private static final Map<String, InjectionResult> results = new ConcurrentHashMap<>();

    // 비활성화된 Mixin 목록 (Fail-soft용)
    private static final Set<String> disabledMixins = ConcurrentHashMap.newKeySet();

    // 콜백 리스너
    private static final List<Consumer<InjectionResult>> callbacks = new CopyOnWriteArrayList<>();
    private static final List<InjectionListener> listeners = new CopyOnWriteArrayList<>();

    private MixinInjectionValidator() {
    } // 인스턴스화 방지

    // ═══════════════════════════════════════════════════════════════
    // Mixin 비활성화 (Fail-soft용)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Mixin 비활성화.
     * 실패한 Mixin을 다시 적용하지 않도록 표시.
     * 
     * @param mixinClass Mixin 클래스 전체 경로
     */
    public static void disableMixin(String mixinClass) {
        if (mixinClass != null && !mixinClass.isEmpty()) {
            disabledMixins.add(mixinClass);
            System.out.println("[MixinInjectionValidator] Mixin disabled: " + mixinClass);
        }
    }

    /**
     * Mixin이 비활성화되어 있는지 확인.
     * 
     * @param mixinClass Mixin 클래스 전체 경로
     * @return 비활성화되어 있으면 true
     */
    public static boolean isMixinDisabled(String mixinClass) {
        return mixinClass != null && disabledMixins.contains(mixinClass);
    }

    /**
     * 비활성화된 Mixin 목록 반환.
     * 
     * @return 불변 Set
     */
    public static Set<String> getDisabledMixins() {
        return java.util.Collections.unmodifiableSet(disabledMixins);
    }

    /**
     * 비활성화된 Mixin 수.
     * 
     * @return 비활성화된 Mixin 수
     */
    public static int getDisabledCount() {
        return disabledMixins.size();
    }

    // ═══════════════════════════════════════════════════════════════
    // 결과 기록 (내부용)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 성공한 인젝션 기록.
     */
    @InternalAPI
    public static void recordSuccess(String mixinClass, String targetClass, long timeMs) {
        InjectionResult result = new InjectionResult(mixinClass, targetClass, true, null, timeMs);
        results.put(createKey(mixinClass, targetClass), result);
        notifyListeners(result);
    }

    /**
     * 실패한 인젝션 기록.
     */
    @InternalAPI
    public static void recordFailure(String mixinClass, String targetClass, String reason) {
        InjectionResult result = new InjectionResult(mixinClass, targetClass, false, reason, 0);
        results.put(createKey(mixinClass, targetClass), result);
        notifyListeners(result);
    }

    private static String createKey(String mixinClass, String targetClass) {
        return mixinClass + "->" + targetClass;
    }

    private static void notifyListeners(InjectionResult result) {
        // Consumer callbacks
        for (Consumer<InjectionResult> callback : callbacks) {
            try {
                callback.accept(result);
            } catch (Exception e) {
                System.err.println("[MixinInjectionValidator] Callback failed: " + e.getMessage());
            }
        }

        // Listener callbacks
        for (InjectionListener listener : listeners) {
            try {
                if (result.isSuccess()) {
                    listener.onInjectionSuccess(result.getMixinClass(),
                            result.getTargetClass(), result.getInjectionTimeMs());
                } else {
                    listener.onInjectionFailed(result.getMixinClass(),
                            result.getTargetClass(), result.getFailureReason());
                }
            } catch (Exception e) {
                System.err.println("[MixinInjectionValidator] Listener failed: " + e.getMessage());
            }
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 조회 API
    // ═══════════════════════════════════════════════════════════════

    /**
     * 특정 Mixin 인젝션 결과 조회.
     * 
     * @param mixinClass  Mixin 클래스 전체 경로
     * @param targetClass 대상 클래스 전체 경로
     * @return 인젝션 결과 (없으면 null)
     */
    public static InjectionResult validateInjection(String mixinClass, String targetClass) {
        return results.get(createKey(mixinClass, targetClass));
    }

    /**
     * 특정 Mixin 인젝션 결과 조회 (Optional).
     */
    public static Optional<InjectionResult> findInjection(String mixinClass, String targetClass) {
        return Optional.ofNullable(validateInjection(mixinClass, targetClass));
    }

    /**
     * 모든 인젝션 결과 조회.
     * 
     * @return 불변 리스트
     */
    public static List<InjectionResult> getAllResults() {
        return Collections.unmodifiableList(new ArrayList<>(results.values()));
    }

    /**
     * 성공한 인젝션만 조회.
     * 
     * @return 성공한 인젝션 리스트
     */
    public static List<InjectionResult> getSuccessfulInjections() {
        return results.values().stream()
                .filter(InjectionResult::isSuccess)
                .collect(Collectors.toList());
    }

    /**
     * 실패한 인젝션만 조회.
     * 
     * @return 실패한 인젝션 리스트
     */
    public static List<InjectionResult> getFailedInjections() {
        return results.values().stream()
                .filter(r -> !r.isSuccess())
                .collect(Collectors.toList());
    }

    /**
     * 특정 타깃에 대한 모든 인젝션 조회.
     * 
     * @param targetClass 대상 클래스
     * @return 해당 타깃의 모든 인젝션 결과
     */
    public static List<InjectionResult> getInjectionsForTarget(String targetClass) {
        return results.values().stream()
                .filter(r -> r.getTargetClass().equals(targetClass))
                .collect(Collectors.toList());
    }

    /**
     * 전체 인젝션 수.
     */
    public static int getTotalCount() {
        return results.size();
    }

    /**
     * 성공한 인젝션 수.
     */
    public static int getSuccessCount() {
        return (int) results.values().stream().filter(InjectionResult::isSuccess).count();
    }

    /**
     * 실패한 인젝션 수.
     */
    public static int getFailureCount() {
        return (int) results.values().stream().filter(r -> !r.isSuccess()).count();
    }

    // ═══════════════════════════════════════════════════════════════
    // 콜백 등록
    // ═══════════════════════════════════════════════════════════════

    /**
     * 인젝션 완료 시 콜백 등록.
     * 
     * @param callback 콜백 함수
     */
    public static void onInjectionComplete(Consumer<InjectionResult> callback) {
        if (callback != null) {
            callbacks.add(callback);
        }
    }

    /**
     * 인젝션 리스너 등록.
     * 
     * @param listener 리스너
     */
    public static void addListener(InjectionListener listener) {
        if (listener != null) {
            listeners.add(listener);
        }
    }

    /**
     * 인젝션 리스너 제거.
     * 
     * @param listener 리스너
     */
    public static void removeListener(InjectionListener listener) {
        listeners.remove(listener);
    }

    // ═══════════════════════════════════════════════════════════════
    // 리포트
    // ═══════════════════════════════════════════════════════════════

    /**
     * 인젝션 상태 리포트 출력.
     */
    public static void printReport() {
        System.out.println("═══════════════════════════════════════════════");
        System.out.println("  Mixin Injection Report");
        System.out.println("═══════════════════════════════════════════════");
        System.out.printf("  Total: %d | Success: %d | Failed: %d%n",
                getTotalCount(), getSuccessCount(), getFailureCount());
        System.out.println("───────────────────────────────────────────────");

        // 실패한 것들 먼저 출력
        List<InjectionResult> failures = getFailedInjections();
        if (!failures.isEmpty()) {
            System.out.println("  ✗ Failed Injections:");
            for (InjectionResult r : failures) {
                System.out.printf("    - %s → %s%n", r.getMixinClass(), r.getTargetClass());
                System.out.printf("      Reason: %s%n", r.getFailureReason());
            }
        }

        System.out.println("═══════════════════════════════════════════════");
    }

    // ═══════════════════════════════════════════════════════════════
    // 결과 클래스
    // ═══════════════════════════════════════════════════════════════

    /**
     * Mixin 인젝션 결과.
     */
    @PublicAPI(since = "1.0.1", status = PublicAPI.Status.EXPERIMENTAL)
    public static final class InjectionResult {
        private final String mixinClass;
        private final String targetClass;
        private final boolean success;
        private final String failureReason;
        private final long injectionTimeMs;
        private final long timestamp;

        InjectionResult(String mixinClass, String targetClass, boolean success,
                String failureReason, long injectionTimeMs) {
            this.mixinClass = mixinClass;
            this.targetClass = targetClass;
            this.success = success;
            this.failureReason = failureReason;
            this.injectionTimeMs = injectionTimeMs;
            this.timestamp = System.currentTimeMillis();
        }

        public String getMixinClass() {
            return mixinClass;
        }

        public String getTargetClass() {
            return targetClass;
        }

        public boolean isSuccess() {
            return success;
        }

        public String getFailureReason() {
            return failureReason;
        }

        public long getInjectionTimeMs() {
            return injectionTimeMs;
        }

        public long getTimestamp() {
            return timestamp;
        }

        @Override
        public String toString() {
            if (success) {
                return String.format("InjectionResult[%s → %s, OK, %dms]",
                        mixinClass, targetClass, injectionTimeMs);
            } else {
                return String.format("InjectionResult[%s → %s, FAILED: %s]",
                        mixinClass, targetClass, failureReason);
            }
        }
    }
}
