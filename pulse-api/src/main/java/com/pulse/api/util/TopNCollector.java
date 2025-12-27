package com.pulse.api.util;

import java.util.*;
import java.util.function.ToDoubleFunction;
import java.util.function.ToLongFunction;

/**
 * Top N 컬렉션 유틸리티.
 * 
 * <p>
 * 컬렉션에서 상위/하위 N개 항목을 효율적으로 추출합니다.
 * </p>
 * 
 * <h3>사용 예시:</h3>
 * 
 * <pre>
 * // Long 값 기준 상위 10개
 * List&lt;LuaFunctionStats&gt; top = TopNCollector.topNByLong(
 *         stats, LuaFunctionStats::getTotalMicros, 10);
 * 
 * // Double 값 기준 상위 5개
 * List&lt;Entry&gt; top = TopNCollector.topNByDouble(
 *         entries, Entry::getAvgMs, 5);
 * </pre>
 * 
 * @since Pulse 1.6
 */
public final class TopNCollector {

    private TopNCollector() {
        // Utility class
    }

    // ═══════════════════════════════════════════════════════════════
    // Generic Top N
    // ═══════════════════════════════════════════════════════════════

    /**
     * 컬렉션에서 상위 N개 항목 추출.
     * 
     * @param items      원본 컬렉션
     * @param comparator 정렬 기준 (내림차순으로 정의해야 함)
     * @param n          추출할 개수
     * @return 상위 N개 항목 리스트
     */
    public static <T> List<T> topN(Collection<T> items,
            Comparator<T> comparator,
            int n) {
        if (items == null || items.isEmpty() || n <= 0) {
            return Collections.emptyList();
        }

        return items.stream()
                .sorted(comparator)
                .limit(n)
                .toList();
    }

    // ═══════════════════════════════════════════════════════════════
    // Convenience Methods
    // ═══════════════════════════════════════════════════════════════

    /**
     * Long 값 기준 상위 N개 추출 (내림차순).
     * 
     * @param items     원본 컬렉션
     * @param extractor long 값 추출 함수
     * @param n         추출할 개수
     * @return 상위 N개 항목
     */
    public static <T> List<T> topNByLong(Collection<T> items,
            ToLongFunction<T> extractor,
            int n) {
        return topN(items,
                Comparator.comparingLong(extractor).reversed(),
                n);
    }

    /**
     * Double 값 기준 상위 N개 추출 (내림차순).
     * 
     * @param items     원본 컬렉션
     * @param extractor double 값 추출 함수
     * @param n         추출할 개수
     * @return 상위 N개 항목
     */
    public static <T> List<T> topNByDouble(Collection<T> items,
            ToDoubleFunction<T> extractor,
            int n) {
        return topN(items,
                Comparator.comparingDouble(extractor).reversed(),
                n);
    }

    /**
     * Int 값 기준 상위 N개 추출 (내림차순).
     * 
     * @param items     원본 컬렉션
     * @param extractor int 값 추출 함수
     * @param n         추출할 개수
     * @return 상위 N개 항목
     */
    public static <T> List<T> topNByInt(Collection<T> items,
            java.util.function.ToIntFunction<T> extractor,
            int n) {
        return topN(items,
                Comparator.comparingInt(extractor).reversed(),
                n);
    }

    // ═══════════════════════════════════════════════════════════════
    // Bottom N (오름차순)
    // ═══════════════════════════════════════════════════════════════

    /**
     * Long 값 기준 하위 N개 추출 (오름차순).
     */
    public static <T> List<T> bottomNByLong(Collection<T> items,
            ToLongFunction<T> extractor,
            int n) {
        return topN(items,
                Comparator.comparingLong(extractor),
                n);
    }
}
