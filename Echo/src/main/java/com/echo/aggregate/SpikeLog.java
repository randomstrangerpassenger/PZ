package com.echo.aggregate;

import com.echo.measure.ProfilingPoint;

import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentLinkedDeque;
import java.util.concurrent.atomic.AtomicLong;

import com.echo.EchoConstants;

/**
 * 스파이크 로그
 * 
 * 성능 스파이크 이벤트를 기록하고 분석합니다.
 * Phase 4: 스택 캡처 기능 추가
 */
public class SpikeLog {

    private static final int MAX_ENTRIES = EchoConstants.SPIKE_LOG_MAX_ENTRIES;
    private static final int MAX_STACK_DEPTH = EchoConstants.SPIKE_MAX_STACK_DEPTH;

    private final Deque<SpikeEntry> entries = new ConcurrentLinkedDeque<>();
    private volatile double thresholdMs;

    // Phase 4: 스택 캡처 옵션
    private volatile boolean stackCaptureEnabled = false;
    private static final StackWalker STACK_WALKER = StackWalker.getInstance(
            StackWalker.Option.RETAIN_CLASS_REFERENCE);

    // 통계 (스레드 안전)
    private final AtomicLong totalSpikes = new AtomicLong(0);
    private final AtomicLong worstSpikeMicros = new AtomicLong(0);
    private volatile String worstSpikeLabel = "";

    public SpikeLog() {
        this(EchoConstants.DEFAULT_SPIKE_THRESHOLD_MS); // 기본 2프레임 (30fps 기준)
    }

    public SpikeLog(double thresholdMs) {
        this.thresholdMs = thresholdMs;
    }

    /**
     * 스택 캡처 활성화/비활성화
     * 주의: 성능 비용이 크므로 디버깅 시에만 사용
     */
    public void setStackCaptureEnabled(boolean enabled) {
        this.stackCaptureEnabled = enabled;
        System.out.println("[Echo] Spike stack capture: " + (enabled ? "ENABLED" : "DISABLED"));
    }

    public boolean isStackCaptureEnabled() {
        return stackCaptureEnabled;
    }

    /**
     * 스파이크 기록
     */
    public void logSpike(long durationMicros, ProfilingPoint point, String label) {
        logSpike(durationMicros, point, label, null);
    }

    /**
     * 포인트별 스파이크 카운트
     */
    public Map<ProfilingPoint, Long> getSpikesByPoint() {
        Map<ProfilingPoint, Long> result = new EnumMap<>(ProfilingPoint.class);
        for (SpikeEntry entry : entries) {
            result.merge(entry.point, 1L, Long::sum);
        }
        return result;
    }

    /**
     * 스택 트레이스 캡처 (Phase 4)
     * 비용이 크므로 옵션으로만 사용
     */
    private String captureStackTrace() {
        StringBuilder sb = new StringBuilder();
        STACK_WALKER.walk(frames -> {
            frames.limit(MAX_STACK_DEPTH)
                    .skip(3) // logSpike 호출 스택 스킵
                    .forEach(frame -> {
                        sb.append(frame.getClassName())
                                .append(".")
                                .append(frame.getMethodName())
                                .append(":")
                                .append(frame.getLineNumber())
                                .append("\n");
                    });
            return null;
        });
        return sb.toString().trim();
    }

    /**
     * 간편 스파이크 로깅 (Tick용)
     */
    public void logTickSpike(long durationMicros) {
        logSpike(durationMicros, ProfilingPoint.TICK, null);
    }

    /**
     * 최근 스파이크 목록 조회
     */
    public List<SpikeEntry> getRecentSpikes(int count) {
        List<SpikeEntry> result = new ArrayList<>();
        Iterator<SpikeEntry> iter = entries.descendingIterator();
        while (iter.hasNext() && result.size() < count) {
            result.add(iter.next());
        }
        return result;
    }

    /**
     * 모든 스파이크 조회
     */
    public List<SpikeEntry> getAllSpikes() {
        return new ArrayList<>(entries);
    }

    /**
     * 총 스파이크 수
     */
    public long getTotalSpikes() {
        return totalSpikes.get();
    }

    /**
     * 최악 스파이크 시간 (밀리초)
     */
    public double getWorstSpikeMs() {
        return worstSpikeMicros.get() / 1000.0;
    }

    /**
     * 최악 스파이크 라벨
     */
    public String getWorstSpikeLabel() {
        return worstSpikeLabel;
    }

    /**
     * 임계값 (밀리초)
     */
    public double getThresholdMs() {
        return thresholdMs;
    }

    /**
     * 임계값 설정
     * 
     * @param thresholdMs 새 임계값 (밀리초)
     */
    public void setThresholdMs(double thresholdMs) {
        this.thresholdMs = thresholdMs;
        System.out.println("[Echo] Spike threshold set to: " + thresholdMs + " ms");
    }

    // Phase 2: Context Provider (Snapshots)
    private java.util.function.Supplier<Map<String, Object>> contextProvider;

    /**
     * Set the context provider for capturing game state during spikes.
     */
    public void setContextProvider(java.util.function.Supplier<Map<String, Object>> provider) {
        this.contextProvider = provider;
    }

    /**
     * 스파이크 기록 (스택 경로 포함)
     */
    public void logSpike(long durationMicros, ProfilingPoint point, String label, String stackPath) {
        double durationMs = durationMicros / 1000.0;
        if (durationMs < thresholdMs)
            return;

        // Phase 4: 스택 캡처 (옵션)
        String capturedStack = stackPath;
        if (stackCaptureEnabled && capturedStack == null) {
            capturedStack = captureStackTrace();
        }

        // Phase 2: Context Snapshot
        Map<String, Object> context = null;
        if (contextProvider != null) {
            try {
                context = contextProvider.get();
            } catch (Exception e) {
                // Prevent crash during logging
                System.err.println("[Echo] Failed to capture spike context: " + e.getMessage());
            }
        }

        SpikeEntry entry = new SpikeEntry(
                Instant.now(),
                durationMicros,
                point,
                label,
                capturedStack,
                context);

        entries.addLast(entry);
        totalSpikes.incrementAndGet();

        // 최악 스파이크 갱신 (CAS 패턴)
        long current;
        do {
            current = worstSpikeMicros.get();
            if (durationMicros <= current)
                break;
        } while (!worstSpikeMicros.compareAndSet(current, durationMicros));

        if (durationMicros > current) {
            worstSpikeLabel = (label != null ? label : point.name());
        }

        // 최대 엔트리 수 유지
        while (entries.size() > MAX_ENTRIES) {
            entries.pollFirst();
        }
    }

    /**
     * JSON 출력용 Map
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();
        map.put("threshold_ms", thresholdMs);
        map.put("total_spikes", totalSpikes.get());
        map.put("worst_spike_ms", Math.round(getWorstSpikeMs() * 100) / 100.0);
        map.put("worst_spike_source", worstSpikeLabel);

        List<Map<String, Object>> recent = new ArrayList<>();
        for (SpikeEntry entry : getRecentSpikes(10)) {
            recent.add(entry.toMap());
        }
        map.put("recent_spikes", recent);

        return map;
    }

    /**
     * 초기화
     */
    public void reset() {
        entries.clear();
        totalSpikes.set(0);
        worstSpikeMicros.set(0);
        worstSpikeLabel = "";
    }

    // --- 스파이크 엔트리 ---

    public static class SpikeEntry {
        private final Instant timestamp;
        private final long durationMicros;
        private final ProfilingPoint point;
        private final String label;
        private final String stackPath;
        private final Map<String, Object> context; // Phase 2

        public SpikeEntry(Instant timestamp, long durationMicros,
                ProfilingPoint point, String label) {
            this(timestamp, durationMicros, point, label, null, null);
        }

        public SpikeEntry(Instant timestamp, long durationMicros,
                ProfilingPoint point, String label, String stackPath) {
            this(timestamp, durationMicros, point, label, stackPath, null);
        }

        public SpikeEntry(Instant timestamp, long durationMicros,
                ProfilingPoint point, String label, String stackPath, Map<String, Object> context) {
            this.timestamp = timestamp;
            this.durationMicros = durationMicros;
            this.point = point;
            this.label = label;
            this.stackPath = stackPath;
            this.context = context;
        }

        public Instant getTimestamp() {
            return timestamp;
        }

        public long getDurationMicros() {
            return durationMicros;
        }

        public double getDurationMs() {
            return durationMicros / 1000.0;
        }

        public ProfilingPoint getPoint() {
            return point;
        }

        public String getLabel() {
            return label;
        }

        public String getStackPath() {
            return stackPath;
        }

        public Map<String, Object> getContext() {
            return context;
        }

        public Map<String, Object> toMap() {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("timestamp", DateTimeFormatter.ISO_INSTANT.format(timestamp));
            map.put("duration_ms", Math.round(getDurationMs() * 100) / 100.0);
            map.put("point", point.name());
            map.put("label", label != null ? label : point.getDisplayName());
            if (stackPath != null) {
                map.put("stack_path", stackPath);
            }
            if (context != null) {
                map.put("context", context);
            }
            return map;
        }

        @Override
        public String toString() {
            return String.format("[%s] %.2fms - %s (%s)",
                    DateTimeFormatter.ISO_LOCAL_TIME.format(
                            timestamp.atZone(java.time.ZoneId.systemDefault())),
                    getDurationMs(),
                    point.getDisplayName(),
                    label != null ? label : "");
        }
    }
}
