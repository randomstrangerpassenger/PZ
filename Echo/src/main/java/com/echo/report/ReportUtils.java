package com.echo.report;

import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

/**
 * Report 공통 유틸리티
 * 
 * Phase 1-B: ReportDataCollector에서 추출된 공통 메서드
 */
public final class ReportUtils {

    private ReportUtils() {
        // 유틸리티 클래스 - 인스턴스화 금지
    }

    /**
     * 소수점 2자리 반올림
     * 
     * @param value 원본 값
     * @return 반올림된 값
     */
    public static double round(double value) {
        return Math.round(value * 100.0) / 100.0;
    }

    /**
     * 마이크로초 → 밀리초 변환 후 반올림
     * 
     * @param micros 마이크로초
     * @return 밀리초 (소수점 2자리)
     */
    public static double microsToMs(double micros) {
        return round(micros / 1000.0);
    }

    /**
     * Instant를 ISO 형식 문자열로 변환
     * 
     * @param instant 시간
     * @return ISO-8601 문자열
     */
    public static String formatInstant(Instant instant) {
        return DateTimeFormatter.ISO_INSTANT.format(instant);
    }

    /**
     * 안전한 Map 조회 (예외 발생 시 에러 Map 반환)
     * 
     * @param supplier Map 생성 함수
     * @return 생성된 Map 또는 에러 Map
     */
    public static Map<String, Object> safeGetMap(Supplier<Map<String, Object>> supplier) {
        try {
            return supplier.get();
        } catch (Exception e) {
            Map<String, Object> err = new HashMap<>();
            err.put("error", "Data collection failed: " + e.getMessage());
            return err;
        }
    }

    /**
     * long 값을 밀리초 형식으로 변환 (소수점 2자리)
     * 
     * @param nanos 나노초
     * @return 밀리초 (소수점 2자리)
     */
    public static double nanosToMs(long nanos) {
        return round(nanos / 1_000_000.0);
    }
}
