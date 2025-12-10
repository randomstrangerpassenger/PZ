package com.pulse.debug;

import com.pulse.event.Event;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 이벤트 모니터.
 * 실시간으로 발생하는 이벤트 추적 및 통계.
 * 
 * 사용 예:
 * 
 * <pre>
 * EventMonitor.enable();
 * // ... 게임 플레이 ...
 * EventMonitor.printStats();
 * </pre>
 */
public class EventMonitor {

    private static final EventMonitor INSTANCE = new EventMonitor();

    private boolean enabled = false;
    private final Map<Class<? extends Event>, EventStats> stats = new ConcurrentHashMap<>();
    private final List<EventRecord> recentEvents = Collections.synchronizedList(new LinkedList<>());
    private static final int MAX_RECENT = 100;

    private EventMonitor() {
    }

    public static EventMonitor getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 제어
    // ─────────────────────────────────────────────────────────────

    public static void enable() {
        INSTANCE.enabled = true;
        System.out.println("[Pulse/EventMonitor] Monitoring enabled");
    }

    public static void disable() {
        INSTANCE.enabled = false;
        System.out.println("[Pulse/EventMonitor] Monitoring disabled");
    }

    public static boolean isEnabled() {
        return INSTANCE.enabled;
    }

    public static void reset() {
        INSTANCE.stats.clear();
        INSTANCE.recentEvents.clear();
    }

    // ─────────────────────────────────────────────────────────────
    // 이벤트 기록 (EventBus에서 호출)
    // ─────────────────────────────────────────────────────────────

    /**
     * 이벤트 발생 기록.
     */
    public static void record(Event event, long processingTimeNs) {
        if (!INSTANCE.enabled)
            return;

        Class<? extends Event> type = event.getClass();

        // 통계 업데이트
        INSTANCE.stats.computeIfAbsent(type, k -> new EventStats(type))
                .record(processingTimeNs);

        // 최근 이벤트 저장
        synchronized (INSTANCE.recentEvents) {
            INSTANCE.recentEvents.add(new EventRecord(type, processingTimeNs));
            while (INSTANCE.recentEvents.size() > MAX_RECENT) {
                INSTANCE.recentEvents.remove(0);
            }
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 통계 조회
    // ─────────────────────────────────────────────────────────────

    /**
     * 이벤트 통계 출력.
     */
    public static void printStats() {
        System.out.println("═══════════════════════════════════════");
        System.out.println("        EVENT MONITOR STATISTICS        ");
        System.out.println("═══════════════════════════════════════");

        List<EventStats> sorted = new ArrayList<>(INSTANCE.stats.values());
        sorted.sort((a, b) -> Long.compare(b.count.get(), a.count.get()));

        for (EventStats stat : sorted) {
            System.out.printf("  %-30s : %6d events, avg %.2fms\n",
                    stat.eventType.getSimpleName(),
                    stat.count.get(),
                    stat.getAverageMs());
        }

        System.out.println("═══════════════════════════════════════");
    }

    /**
     * 통계 맵 반환.
     */
    public static Map<Class<? extends Event>, EventStats> getStats() {
        return Collections.unmodifiableMap(INSTANCE.stats);
    }

    /**
     * 최근 이벤트 목록.
     */
    public static List<EventRecord> getRecentEvents() {
        return new ArrayList<>(INSTANCE.recentEvents);
    }

    // ─────────────────────────────────────────────────────────────
    // 데이터 클래스
    // ─────────────────────────────────────────────────────────────

    public static class EventStats {
        public final Class<? extends Event> eventType;
        public final AtomicLong count = new AtomicLong(0);
        public final AtomicLong totalTimeNs = new AtomicLong(0);

        EventStats(Class<? extends Event> eventType) {
            this.eventType = eventType;
        }

        void record(long processingTimeNs) {
            count.incrementAndGet();
            totalTimeNs.addAndGet(processingTimeNs);
        }

        public double getAverageMs() {
            long c = count.get();
            if (c == 0)
                return 0;
            return (totalTimeNs.get() / (double) c) / 1_000_000.0;
        }
    }

    public static class EventRecord {
        public final Class<? extends Event> eventType;
        public final long timestamp;
        public final long processingTimeNs;

        EventRecord(Class<? extends Event> eventType, long processingTimeNs) {
            this.eventType = eventType;
            this.timestamp = System.currentTimeMillis();
            this.processingTimeNs = processingTimeNs;
        }
    }
}
