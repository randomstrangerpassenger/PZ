package com.pulse.api.util;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

/**
 * Exception StackTrace 축약기
 * 
 * 긴 스택 트레이스를 mod 개발자에게 유용한 형태로 축약합니다.
 * - modId 기반 필터링: 해당 mod 관련 프레임만 표시
 * - 상위 N줄 제한: 너무 긴 스택 트레이스 방지
 * - 컨텍스트 유지: 원인 체인 포함
 * 
 * @since Pulse 0.9 (Phase 4 DX)
 */
public final class PulseExceptionFormatter {

    private static final int DEFAULT_MAX_LINES = 10;

    // 항상 포함할 패키지 접두어
    // Note: External modules can register additional prefixes via SPI if needed
    private static final Set<String> ALWAYS_INCLUDE = new HashSet<>(Arrays.asList(
            "com.pulse."));

    // 제외할 패키지 (너무 많은 프레임 방지)
    private static final Set<String> EXCLUDE_PACKAGES = new HashSet<>(Arrays.asList(
            "java.lang.reflect.",
            "sun.reflect.",
            "jdk.internal.",
            "org.objectweb.asm."));

    private PulseExceptionFormatter() {
        // Utility class
    }

    /**
     * 스택 트레이스를 축약된 문자열로 변환
     * 
     * @param throwable 예외
     * @return 축약된 스택 트레이스 문자열
     */
    public static String format(Throwable throwable) {
        return format(throwable, null, DEFAULT_MAX_LINES);
    }

    /**
     * 스택 트레이스를 modId 기준으로 필터링하여 축약
     * 
     * @param throwable 예외
     * @param modId     우선 표시할 mod ID (예: "echo", "fuse")
     * @return 축약된 스택 트레이스 문자열
     */
    public static String format(Throwable throwable, String modId) {
        return format(throwable, modId, DEFAULT_MAX_LINES);
    }

    /**
     * 스택 트레이스를 modId 기준으로 필터링하여 축약
     * 
     * @param throwable 예외
     * @param modId     우선 표시할 mod ID (null이면 전체)
     * @param maxLines  최대 표시 줄 수
     * @return 축약된 스택 트레이스 문자열
     */
    public static String format(Throwable throwable, String modId, int maxLines) {
        if (throwable == null) {
            return "[null exception]";
        }

        StringBuilder sb = new StringBuilder();

        // 예외 타입과 메시지
        sb.append(throwable.getClass().getSimpleName())
                .append(": ")
                .append(throwable.getMessage() != null ? throwable.getMessage() : "(no message)")
                .append("\n");

        // 스택 트레이스 필터링
        StackTraceElement[] frames = throwable.getStackTrace();
        int printed = 0;
        int skipped = 0;
        String modPackage = modId != null ? "com." + modId + "." : null;

        for (StackTraceElement frame : frames) {
            String className = frame.getClassName();

            // 제외 패키지 체크
            if (shouldExclude(className)) {
                skipped++;
                continue;
            }

            // modId 기반 우선순위 또는 항상 포함 패키지
            boolean isRelevant = shouldInclude(className) ||
                    (modPackage != null && className.startsWith(modPackage));

            if (isRelevant || printed < 3) { // 최소 3줄은 항상 표시
                if (printed < maxLines) {
                    sb.append("    at ").append(formatFrame(frame)).append("\n");
                    printed++;
                }
            } else {
                skipped++;
            }
        }

        // 생략된 프레임 수 표시
        if (skipped > 0) {
            sb.append("    ... ").append(skipped).append(" more frames\n");
        }

        // Cause 체인 처리 (재귀)
        Throwable cause = throwable.getCause();
        if (cause != null && cause != throwable) {
            sb.append("Caused by: ");
            sb.append(format(cause, modId, Math.max(3, maxLines / 2)));
        }

        return sb.toString();
    }

    /**
     * 스택 프레임을 간결하게 포맷
     */
    private static String formatFrame(StackTraceElement frame) {
        String className = frame.getClassName();

        // 긴 클래스 이름 축약
        int lastDot = className.lastIndexOf('.');
        if (lastDot > 0 && className.length() > 50) {
            String pkg = className.substring(0, lastDot);
            String simpleName = className.substring(lastDot + 1);

            // 패키지를 축약 (예: com.mymod.measure -> c.m.measure)
            String[] parts = pkg.split("\\.");
            StringBuilder abbrev = new StringBuilder();
            for (int i = 0; i < parts.length - 1 && i < 3; i++) {
                abbrev.append(parts[i].charAt(0)).append(".");
            }
            if (parts.length > 0) {
                abbrev.append(parts[parts.length - 1]);
            }
            className = abbrev + "." + simpleName;
        }

        String location = frame.getFileName() != null
                ? frame.getFileName() + ":" + frame.getLineNumber()
                : "Unknown Source";

        return className + "." + frame.getMethodName() + "(" + location + ")";
    }

    private static boolean shouldInclude(String className) {
        for (String prefix : ALWAYS_INCLUDE) {
            if (className.startsWith(prefix)) {
                return true;
            }
        }
        return false;
    }

    private static boolean shouldExclude(String className) {
        for (String prefix : EXCLUDE_PACKAGES) {
            if (className.startsWith(prefix)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 일반적인 로그 출력용 한 줄 요약
     */
    public static String oneLiner(Throwable throwable) {
        if (throwable == null) {
            return "[null]";
        }

        StackTraceElement[] frames = throwable.getStackTrace();
        String location = frames.length > 0
                ? frames[0].getFileName() + ":" + frames[0].getLineNumber()
                : "?";

        return throwable.getClass().getSimpleName() + ": "
                + (throwable.getMessage() != null ? throwable.getMessage() : "(no message)")
                + " @ " + location;
    }
}
