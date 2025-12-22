package com.pulse.api.util;

import com.pulse.api.exception.InitializationException;
import com.pulse.api.log.PulseLogger;

import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.function.Supplier;

/**
 * 안전한 초기화 유틸리티.
 * 
 * 초기화 코드의 예외를 graceful하게 처리하고,
 * 실패 시 로깅 및 대체 값 반환을 지원합니다.
 * 
 * <pre>
 * // 예외 발생 시 기본값 반환
 * String value = SafeInitializer.tryGet(() -> config.getValue(), "default");
 * 
 * // 예외 발생 시 로깅만
 * SafeInitializer.tryRun("Pulse", "Loading config", () -> loadConfig());
 * 
 * // 예외 발생 시 Optional.empty()
 * Optional&lt;Service&gt; service = SafeInitializer.tryGetOptional(() -> loadService());
 * </pre>
 * 
 * @since 1.1.0
 */
public final class SafeInitializer {

    private SafeInitializer() {
    }

    /**
     * 초기화 로직 실행. 예외 발생 시 로깅 후 무시.
     * 
     * @param module    모듈명 (로깅용)
     * @param operation 작업명 (로깅용)
     * @param runnable  실행할 로직
     * @return 성공 여부
     */
    public static boolean tryRun(String module, String operation, Runnable runnable) {
        try {
            runnable.run();
            return true;
        } catch (Exception e) {
            PulseLogger.warn(module, "Failed to {}: {}", operation, e.getMessage());
            return false;
        }
    }

    /**
     * 초기화 로직 실행 (자세한 예외 로깅).
     * 
     * @param module    모듈명
     * @param operation 작업명
     * @param runnable  실행할 로직
     * @param verbose   true면 스택 트레이스도 출력
     * @return 성공 여부
     */
    public static boolean tryRun(String module, String operation, Runnable runnable, boolean verbose) {
        try {
            runnable.run();
            return true;
        } catch (Exception e) {
            if (verbose) {
                PulseLogger.error(module, "Failed to {}: {}", operation, e.getMessage(), e);
            } else {
                PulseLogger.warn(module, "Failed to {}: {}", operation, e.getMessage());
            }
            return false;
        }
    }

    /**
     * 값 반환 초기화. 예외 시 기본값 반환.
     * 
     * @param supplier     값 공급자
     * @param defaultValue 기본값
     * @param <T>          반환 타입
     * @return 결과 또는 기본값
     */
    public static <T> T tryGet(Supplier<T> supplier, T defaultValue) {
        try {
            T result = supplier.get();
            return result != null ? result : defaultValue;
        } catch (Exception e) {
            return defaultValue;
        }
    }

    /**
     * 값 반환 초기화 (로깅 포함). 예외 시 기본값 반환.
     * 
     * @param module       모듈명
     * @param operation    작업명
     * @param supplier     값 공급자
     * @param defaultValue 기본값
     * @param <T>          반환 타입
     * @return 결과 또는 기본값
     */
    public static <T> T tryGet(String module, String operation, Supplier<T> supplier, T defaultValue) {
        try {
            T result = supplier.get();
            return result != null ? result : defaultValue;
        } catch (Exception e) {
            PulseLogger.warn(module, "Failed to {}, using default: {}", operation, e.getMessage());
            return defaultValue;
        }
    }

    /**
     * Optional 반환 초기화. 예외 시 Optional.empty().
     * 
     * @param supplier 값 공급자
     * @param <T>      반환 타입
     * @return Optional 결과
     */
    public static <T> Optional<T> tryGetOptional(Supplier<T> supplier) {
        try {
            return Optional.ofNullable(supplier.get());
        } catch (Exception e) {
            return Optional.empty();
        }
    }

    /**
     * Optional 반환 초기화 (로깅 포함).
     * 
     * @param module    모듈명
     * @param operation 작업명
     * @param supplier  값 공급자
     * @param <T>       반환 타입
     * @return Optional 결과
     */
    public static <T> Optional<T> tryGetOptional(String module, String operation, Supplier<T> supplier) {
        try {
            return Optional.ofNullable(supplier.get());
        } catch (Exception e) {
            PulseLogger.debug(module, "Optional {} failed: {}", operation, e.getMessage());
            return Optional.empty();
        }
    }

    /**
     * Callable 실행. 예외 시 InitializationException으로 래핑.
     * 
     * @param component 컴포넌트명
     * @param phase     초기화 단계
     * @param callable  실행할 로직
     * @param <T>       반환 타입
     * @return 결과
     * @throws InitializationException 초기화 실패 시
     */
    public static <T> T requireOrThrow(String component, InitializationException.InitPhase phase,
            Callable<T> callable) {
        try {
            return callable.call();
        } catch (Exception e) {
            throw new InitializationException(
                    String.format("Failed to initialize %s: %s", component, e.getMessage()),
                    component, phase, e);
        }
    }

    /**
     * 조건 검증. 조건 불충족 시 예외 발생.
     * 
     * @param condition    검증할 조건
     * @param errorMessage 오류 메시지
     * @throws InitializationException 조건 불충족 시
     */
    public static void requireCondition(boolean condition, String errorMessage) {
        if (!condition) {
            throw new InitializationException(errorMessage);
        }
    }

    /**
     * null 아닌 값 검증.
     * 
     * @param value        검증할 값
     * @param errorMessage 오류 메시지
     * @param <T>          값 타입
     * @return 검증된 값
     * @throws InitializationException 값이 null인 경우
     */
    public static <T> T requireNonNull(T value, String errorMessage) {
        if (value == null) {
            throw new InitializationException(errorMessage);
        }
        return value;
    }

    /**
     * 여러 초기화 작업 순차 실행. 하나라도 실패 시 중단.
     * 
     * @param module 모듈명
     * @param tasks  실행할 작업 배열
     * @return 모든 작업 성공 여부
     */
    public static boolean tryRunAll(String module, InitTask... tasks) {
        for (InitTask task : tasks) {
            if (!tryRun(module, task.name, task.runnable)) {
                return false;
            }
        }
        return true;
    }

    /**
     * 초기화 작업 정의
     */
    public static class InitTask {
        public final String name;
        public final Runnable runnable;

        public InitTask(String name, Runnable runnable) {
            this.name = name;
            this.runnable = runnable;
        }

        public static InitTask of(String name, Runnable runnable) {
            return new InitTask(name, runnable);
        }
    }
}
