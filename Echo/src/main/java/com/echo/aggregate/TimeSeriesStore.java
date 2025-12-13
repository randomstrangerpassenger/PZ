package com.echo.aggregate;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 시계열 데이터 저장소.
 * 
 * Phase 4.2: 다양한 메트릭의 시계열 데이터를 저장하고 트렌드를 분석합니다.
 * 
 * @since 1.0.1
 */
public class TimeSeriesStore {

    private static final TimeSeriesStore INSTANCE = new TimeSeriesStore();

    // 메트릭별 시계열 데이터
    private final Map<String, TimeSeries> seriesMap = new ConcurrentHashMap<>();

    // 기본 설정
    private static final int DEFAULT_MAX_SAMPLES = 3600; // 1시간 (1초당 1개)

    public static TimeSeriesStore getInstance() {
        return INSTANCE;
    }

    /**
     * 데이터 포인트 기록
     */
    public void record(String metric, double value) {
        record(metric, System.currentTimeMillis(), value);
    }

    /**
     * 타임스탬프 지정하여 기록
     */
    public void record(String metric, long timestamp, double value) {
        seriesMap.computeIfAbsent(metric, k -> new TimeSeries(DEFAULT_MAX_SAMPLES))
                .add(timestamp, value);
    }

    /**
     * 시간 범위로 조회
     */
    public TimeSeries query(String metric, TimeRange range) {
        TimeSeries series = seriesMap.get(metric);
        if (series == null)
            return new TimeSeries(0);
        return series.slice(range.startMs, range.endMs);
    }

    /**
     * 최근 N밀리초 조회
     */
    public TimeSeries queryRecent(String metric, long durationMs) {
        long now = System.currentTimeMillis();
        return query(metric, new TimeRange(now - durationMs, now));
    }

    /**
     * 트렌드 분석
     */
    public TrendAnalysis analyzeTrend(String metric, TimeRange range) {
        TimeSeries series = query(metric, range);
        return series.analyzeTrend();
    }

    /**
     * 등록된 모든 메트릭 이름
     */
    public Set<String> getMetricNames() {
        return new HashSet<>(seriesMap.keySet());
    }

    /**
     * 특정 메트릭 삭제
     */
    public void clear(String metric) {
        seriesMap.remove(metric);
    }

    /**
     * 전체 초기화
     */
    public void reset() {
        seriesMap.clear();
    }

    /**
     * JSON 출력용 요약
     */
    public Map<String, Object> toSummary() {
        Map<String, Object> summary = new LinkedHashMap<>();
        summary.put("metric_count", seriesMap.size());

        List<Map<String, Object>> metrics = new ArrayList<>();
        for (Map.Entry<String, TimeSeries> entry : seriesMap.entrySet()) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("name", entry.getKey());
            m.put("sample_count", entry.getValue().size());

            TrendAnalysis trend = entry.getValue().analyzeTrend();
            m.put("trend", trend.direction.name());
            m.put("avg", Math.round(trend.average * 100) / 100.0);
            m.put("min", trend.min);
            m.put("max", trend.max);

            metrics.add(m);
        }
        summary.put("metrics", metrics);

        return summary;
    }

    // --- 내부 클래스 ---

    /**
     * 시계열 데이터
     */
    public static class TimeSeries {
        private final LinkedList<DataPoint> points = new LinkedList<>();
        private final int maxSize;

        public TimeSeries(int maxSize) {
            this.maxSize = maxSize;
        }

        public synchronized void add(long timestamp, double value) {
            points.addLast(new DataPoint(timestamp, value));
            while (points.size() > maxSize && maxSize > 0) {
                points.removeFirst();
            }
        }

        public synchronized int size() {
            return points.size();
        }

        public synchronized TimeSeries slice(long startMs, long endMs) {
            TimeSeries sliced = new TimeSeries(maxSize);
            for (DataPoint p : points) {
                if (p.timestamp >= startMs && p.timestamp <= endMs) {
                    sliced.add(p.timestamp, p.value);
                }
            }
            return sliced;
        }

        public synchronized List<DataPoint> getPoints() {
            return new ArrayList<>(points);
        }

        public synchronized TrendAnalysis analyzeTrend() {
            if (points.isEmpty()) {
                return new TrendAnalysis(0, 0, 0, 0, TrendDirection.STABLE);
            }

            double sum = 0, min = Double.MAX_VALUE, max = Double.MIN_VALUE;
            for (DataPoint p : points) {
                sum += p.value;
                min = Math.min(min, p.value);
                max = Math.max(max, p.value);
            }
            double avg = sum / points.size();

            // 트렌드 방향 결정 (간단한 선형 회귀)
            TrendDirection direction = TrendDirection.STABLE;
            if (points.size() >= 2) {
                DataPoint first = points.getFirst();
                DataPoint last = points.getLast();
                double slope = (last.value - first.value) / (last.timestamp - first.timestamp);

                if (slope > 0.001)
                    direction = TrendDirection.INCREASING;
                else if (slope < -0.001)
                    direction = TrendDirection.DECREASING;
            }

            return new TrendAnalysis(avg, min, max, sum, direction);
        }
    }

    /**
     * 데이터 포인트
     */
    public static class DataPoint {
        public final long timestamp;
        public final double value;

        public DataPoint(long timestamp, double value) {
            this.timestamp = timestamp;
            this.value = value;
        }
    }

    /**
     * 시간 범위
     */
    public static class TimeRange {
        public final long startMs;
        public final long endMs;

        public TimeRange(long startMs, long endMs) {
            this.startMs = startMs;
            this.endMs = endMs;
        }

        public static TimeRange last(long durationMs) {
            long now = System.currentTimeMillis();
            return new TimeRange(now - durationMs, now);
        }
    }

    /**
     * 트렌드 분석 결과
     */
    public static class TrendAnalysis {
        public final double average;
        public final double min;
        public final double max;
        public final double sum;
        public final TrendDirection direction;

        public TrendAnalysis(double average, double min, double max, double sum, TrendDirection direction) {
            this.average = average;
            this.min = min;
            this.max = max;
            this.sum = sum;
            this.direction = direction;
        }
    }

    public enum TrendDirection {
        INCREASING,
        DECREASING,
        STABLE
    }
}
