package com.pulse.mixin;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Mixin 오류 중앙 처리기.
 * 
 * Pulse 전체의 Mixin 오류를 수집하고, 진단 정보를 제공합니다.
 * 
 * @since Pulse 1.2
 */
public final class PulseErrorHandler {

    private static final List<MixinError> errorLog = Collections.synchronizedList(new ArrayList<>());
    private static final Map<String, Integer> errorCountByMixin = new ConcurrentHashMap<>();
    private static final int MAX_ERROR_LOG_SIZE = 100;

    private static volatile ErrorCallback callback = null;

    private PulseErrorHandler() {
        // Utility class
    }

    /**
     * Mixin 오류 보고
     * 
     * @param mixinId Mixin 식별자
     * @param error   발생한 오류
     */
    public static void reportMixinFailure(String mixinId, Throwable error) {
        // 오류 카운트 증가 (using lambda to avoid null safety warning)
        errorCountByMixin.merge(mixinId, 1, (a, b) -> a + b);

        // 오류 로그 저장 (최대 크기 제한)
        MixinError errorInfo = new MixinError(mixinId, error);
        synchronized (errorLog) {
            if (errorLog.size() >= MAX_ERROR_LOG_SIZE) {
                errorLog.remove(0);
            }
            errorLog.add(errorInfo);
        }

        // 콜백 호출
        ErrorCallback cb = callback;
        if (cb != null) {
            try {
                cb.onMixinError(mixinId, error);
            } catch (Throwable t) {
                // 콜백 자체 오류는 무시
            }
        }
    }

    /**
     * 오류 콜백 설정 (외부 모니터링용)
     */
    public static void setCallback(ErrorCallback cb) {
        callback = cb;
    }

    /**
     * 최근 오류 목록
     */
    public static List<MixinError> getRecentErrors() {
        synchronized (errorLog) {
            return new ArrayList<>(errorLog);
        }
    }

    /**
     * Mixin별 오류 카운트
     */
    public static Map<String, Integer> getErrorCounts() {
        return new ConcurrentHashMap<>(errorCountByMixin);
    }

    /**
     * 특정 Mixin 오류 존재 여부
     */
    public static boolean hasErrors(String mixinId) {
        return errorCountByMixin.containsKey(mixinId);
    }

    /**
     * 전체 오류 카운트
     */
    public static int getTotalErrorCount() {
        return errorCountByMixin.values().stream().mapToInt(Integer::intValue).sum();
    }

    /**
     * 오류 로그 초기화
     */
    public static void clearErrors() {
        synchronized (errorLog) {
            errorLog.clear();
        }
        errorCountByMixin.clear();
    }

    /**
     * 상태 요약 (진단용)
     */
    public static String getStatusSummary() {
        StringBuilder sb = new StringBuilder();
        sb.append("PulseErrorHandler Status:\n");
        sb.append("  Total Errors: ").append(getTotalErrorCount()).append("\n");
        sb.append("  Affected Mixins: ").append(errorCountByMixin.size()).append("\n");

        if (!errorCountByMixin.isEmpty()) {
            sb.append("  Error Breakdown:\n");
            errorCountByMixin.forEach(
                    (mixin, count) -> sb.append("    - ").append(mixin).append(": ").append(count).append("\n"));
        }

        return sb.toString();
    }

    /**
     * 오류 콜백 인터페이스
     */
    @FunctionalInterface
    public interface ErrorCallback {
        void onMixinError(String mixinId, Throwable error);
    }

    /**
     * Mixin 오류 정보 클래스
     */
    public static class MixinError {
        private final String mixinId;
        private final String errorType;
        private final String message;
        private final String stackTrace;
        private final LocalDateTime timestamp;

        public MixinError(String mixinId, Throwable error) {
            this.mixinId = mixinId;
            this.errorType = error.getClass().getSimpleName();
            this.message = error.getMessage();
            this.stackTrace = getStackTraceString(error);
            this.timestamp = LocalDateTime.now();
        }

        private static String getStackTraceString(Throwable t) {
            StringWriter sw = new StringWriter();
            t.printStackTrace(new PrintWriter(sw));
            return sw.toString();
        }

        public String getMixinId() {
            return mixinId;
        }

        public String getErrorType() {
            return errorType;
        }

        public String getMessage() {
            return message;
        }

        public String getStackTrace() {
            return stackTrace;
        }

        public LocalDateTime getTimestamp() {
            return timestamp;
        }

        @Override
        public String toString() {
            return String.format("[%s] %s in %s: %s",
                    timestamp.format(DateTimeFormatter.ISO_LOCAL_TIME),
                    errorType, mixinId, message);
        }
    }
}
