package com.echo.measure;

import java.lang.management.GarbageCollectorMXBean;
import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryUsage;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 메모리 프로파일러
 * 
 * JVM 메모리 사용량 및 GC 이벤트 추적
 */
public class MemoryProfiler {

    private static final MemoryMXBean memoryBean = ManagementFactory.getMemoryMXBean();
    private static final List<GarbageCollectorMXBean> gcBeans = ManagementFactory.getGarbageCollectorMXBeans();

    // 최근 GC 통계 (델타 계산용)
    private static long lastGcCount = 0;
    private static long lastGcTime = 0;

    /**
     * 힙 사용량 (바이트)
     */
    public static long getHeapUsed() {
        return memoryBean.getHeapMemoryUsage().getUsed();
    }

    /**
     * 힙 최대 크기 (바이트)
     */
    public static long getHeapMax() {
        return memoryBean.getHeapMemoryUsage().getMax();
    }

    /**
     * 힙 커밋 크기 (바이트)
     */
    public static long getHeapCommitted() {
        return memoryBean.getHeapMemoryUsage().getCommitted();
    }

    /**
     * 힙 사용률 (%)
     */
    public static double getHeapUsagePercent() {
        MemoryUsage usage = memoryBean.getHeapMemoryUsage();
        long max = usage.getMax();
        if (max <= 0) {
            max = usage.getCommitted();
        }
        return max > 0 ? (usage.getUsed() * 100.0 / max) : 0;
    }

    /**
     * Non-Heap 사용량 (바이트) - Metaspace 등
     */
    public static long getNonHeapUsed() {
        return memoryBean.getNonHeapMemoryUsage().getUsed();
    }

    /**
     * 총 GC 횟수
     */
    public static long getTotalGcCount() {
        return gcBeans.stream()
                .mapToLong(GarbageCollectorMXBean::getCollectionCount)
                .filter(c -> c >= 0)
                .sum();
    }

    /**
     * 총 GC 시간 (밀리초)
     */
    public static long getTotalGcTimeMs() {
        return gcBeans.stream()
                .mapToLong(GarbageCollectorMXBean::getCollectionTime)
                .filter(t -> t >= 0)
                .sum();
    }

    /**
     * 최근 GC 횟수 (마지막 호출 이후 증가분)
     */
    public static long getRecentGcCount() {
        long current = getTotalGcCount();
        long delta = current - lastGcCount;
        lastGcCount = current;
        return delta;
    }

    /**
     * 최근 GC 시간 (마지막 호출 이후 증가분, 밀리초)
     */
    public static long getRecentGcTimeMs() {
        long current = getTotalGcTimeMs();
        long delta = current - lastGcTime;
        lastGcTime = current;
        return delta;
    }

    /**
     * GC 정보 조회
     */
    public static Map<String, Object> getGcInfo() {
        Map<String, Object> info = new LinkedHashMap<>();
        for (GarbageCollectorMXBean gc : gcBeans) {
            Map<String, Object> gcEntry = new LinkedHashMap<>();
            gcEntry.put("count", gc.getCollectionCount());
            gcEntry.put("time_ms", gc.getCollectionTime());
            info.put(gc.getName(), gcEntry);
        }
        return info;
    }

    /**
     * 콘솔 출력용 상태 문자열
     */
    public static String getStatusString() {
        StringBuilder sb = new StringBuilder();
        sb.append("💾 MEMORY STATUS\n");
        sb.append("───────────────────────────────────────────────────────\n");
        sb.append(String.format("  Heap Used:     %,d MB / %,d MB (%.1f%%)%n",
                getHeapUsed() / (1024 * 1024),
                getHeapMax() / (1024 * 1024),
                getHeapUsagePercent()));
        sb.append(String.format("  Non-Heap:      %,d MB%n",
                getNonHeapUsed() / (1024 * 1024)));
        sb.append(String.format("  GC Count:      %,d%n", getTotalGcCount()));
        sb.append(String.format("  GC Time:       %,d ms%n", getTotalGcTimeMs()));
        return sb.toString();
    }

    /**
     * JSON 출력용 Map
     */
    public static Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();

        Map<String, Object> heap = new LinkedHashMap<>();
        heap.put("used_mb", Math.round(getHeapUsed() / (1024.0 * 1024.0) * 100) / 100.0);
        heap.put("max_mb", Math.round(getHeapMax() / (1024.0 * 1024.0) * 100) / 100.0);
        heap.put("committed_mb", Math.round(getHeapCommitted() / (1024.0 * 1024.0) * 100) / 100.0);
        heap.put("usage_percent", Math.round(getHeapUsagePercent() * 100) / 100.0);
        map.put("heap", heap);

        map.put("non_heap_mb", Math.round(getNonHeapUsed() / (1024.0 * 1024.0) * 100) / 100.0);

        Map<String, Object> gc = new LinkedHashMap<>();
        gc.put("total_count", getTotalGcCount());
        gc.put("total_time_ms", getTotalGcTimeMs());
        gc.put("collectors", getGcInfo());
        map.put("gc", gc);

        return map;
    }

    /**
     * 메모리 통계 출력
     */
    public static void printStatus() {
        System.out.println(getStatusString());
    }
}
