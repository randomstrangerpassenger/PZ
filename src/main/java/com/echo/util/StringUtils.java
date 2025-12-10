package com.echo.util;

/**
 * 문자열 유틸리티
 */
public final class StringUtils {

    private StringUtils() {
        // 유틸리티 클래스
    }

    /**
     * 문자열을 최대 길이로 자름
     * 
     * @param s      원본 문자열
     * @param maxLen 최대 길이
     * @return 잘린 문자열 (초과 시 "..." 추가)
     */
    public static String truncate(String s, int maxLen) {
        if (s == null)
            return "";
        return s.length() <= maxLen ? s : s.substring(0, maxLen - 3) + "...";
    }

    /**
     * 마이크로초를 밀리초 문자열로 변환
     */
    public static String formatMs(double micros) {
        return String.format("%.2f", micros / 1000.0);
    }

    /**
     * 마이크로초를 밀리초로 반올림
     */
    public static double toMs(long micros) {
        return Math.round(micros / 10.0) / 100.0;
    }

    /**
     * 밀리초 포맷 (소수점 2자리)
     */
    public static String formatDuration(long micros) {
        return String.format("%.2f ms", micros / 1000.0);
    }
}
