package com.echo.analysis;

import com.echo.aggregate.*;
import com.echo.measure.*;
import com.echo.subsystem.*;

import java.util.*;

/**
 * 확장 상관관계 분석기.
 * 
 * 다양한 메트릭 간의 상관관계를 분석합니다.
 * 기존 CorrelationAnalyzer를 확장합니다.
 * 
 * @since 1.0.1
 */
public class ExtendedCorrelationAnalyzer {

    private static final ExtendedCorrelationAnalyzer INSTANCE = new ExtendedCorrelationAnalyzer();
    private static final int BUFFER_SIZE = 100;

    // 상관관계 버퍼들
    private final CorrelationBuffer chunkVsFrameTime = new CorrelationBuffer(BUFFER_SIZE);
    private final CorrelationBuffer entityVsSimulation = new CorrelationBuffer(BUFFER_SIZE);
    private final CorrelationBuffer memoryVsGcFreq = new CorrelationBuffer(BUFFER_SIZE);
    private final CorrelationBuffer pathfindingVsTick = new CorrelationBuffer(BUFFER_SIZE);
    private final CorrelationBuffer zombieVsTick = new CorrelationBuffer(BUFFER_SIZE);
    private final CorrelationBuffer vehicleVsTick = new CorrelationBuffer(BUFFER_SIZE);

    // 캐시된 값들
    private long lastGcCount = 0;
    private long lastTickTime = System.currentTimeMillis();

    public static ExtendedCorrelationAnalyzer getInstance() {
        return INSTANCE;
    }

    /**
     * 틱마다 호출하여 데이터 수집
     */
    public void onTick() {
        TimingData tickData = EchoProfiler.getInstance().getTimingData(ProfilingPoint.TICK);
        if (tickData == null)
            return;

        double tickMs = tickData.getStats1s().getAverage() / 1000.0;
        long now = System.currentTimeMillis();

        // 1. 좀비 vs 틱
        int zombieCount = (int) ZombieProfiler.getInstance().getZombieCount();
        zombieVsTick.addSample(zombieCount, tickMs);

        // 2. 청크 vs 프레임
        try {
            Class<?> gameAccess = Class.forName("com.pulse.api.GameAccess");
            java.lang.reflect.Method getChunks = gameAccess.getMethod("getLoadedCellCount");
            int chunkCount = ((Number) getChunks.invoke(null)).intValue();

            TimingData frameData = EchoProfiler.getInstance().getTimingData(ProfilingPoint.FRAME);
            if (frameData != null) {
                chunkVsFrameTime.addSample(chunkCount, frameData.getStats1s().getAverage() / 1000.0);
            }

            // 3. 총 엔티티 vs 시뮬레이션
            java.lang.reflect.Method getEntities = gameAccess.getMethod("getTotalEntityCount");
            int entityCount = ((Number) getEntities.invoke(null)).intValue();

            TimingData simData = EchoProfiler.getInstance().getTimingData(ProfilingPoint.SIMULATION);
            if (simData != null) {
                entityVsSimulation.addSample(entityCount, simData.getStats1s().getAverage() / 1000.0);
            }

            // 4. 차량 vs 틱
            java.lang.reflect.Method getVehicles = gameAccess.getMethod("getVehicleCount");
            int vehicleCount = ((Number) getVehicles.invoke(null)).intValue();
            vehicleVsTick.addSample(vehicleCount, tickMs);

        } catch (Exception e) {
            // Pulse 없이 실행 중
        }

        // 5. 메모리 vs GC 빈도
        long currentGcCount = MemoryProfiler.getTotalGcCount();
        double gcDelta = currentGcCount - lastGcCount;
        double timeDelta = (now - lastTickTime) / 1000.0;
        double gcFreq = timeDelta > 0 ? gcDelta / timeDelta : 0;

        double memoryUsage = MemoryProfiler.getHeapUsagePercent();
        memoryVsGcFreq.addSample(memoryUsage, gcFreq);

        lastGcCount = currentGcCount;
        lastTickTime = now;

        // 6. 패스파인딩 호출 vs 틱 (총 요청 수 사용)
        long pathfindingCalls = PathfindingProfiler.getInstance().getTotalRequests();
        pathfindingVsTick.addSample(pathfindingCalls, tickMs);
    }

    /**
     * 모든 상관관계 분석 결과
     */
    public Map<String, Object> analyze() {
        Map<String, Object> results = new LinkedHashMap<>();

        results.put("zombie_vs_tick", createCorrelationEntry(zombieVsTick, "좀비 수 vs 틱 시간"));
        results.put("chunk_vs_frame", createCorrelationEntry(chunkVsFrameTime, "청크 수 vs 프레임 시간"));
        results.put("entity_vs_simulation", createCorrelationEntry(entityVsSimulation, "엔티티 수 vs 시뮬레이션"));
        results.put("memory_vs_gc", createCorrelationEntry(memoryVsGcFreq, "메모리 사용률 vs GC 빈도"));
        results.put("pathfinding_vs_tick", createCorrelationEntry(pathfindingVsTick, "패스파인딩 호출 vs 틱"));
        results.put("vehicle_vs_tick", createCorrelationEntry(vehicleVsTick, "차량 수 vs 틱 시간"));

        // 요약
        Map<String, Object> summary = new LinkedHashMap<>();
        double strongestCorr = 0;
        String strongestName = "none";

        for (Map.Entry<String, Object> entry : results.entrySet()) {
            @SuppressWarnings("unchecked")
            Map<String, Object> data = (Map<String, Object>) entry.getValue();
            double corr = Math.abs((Double) data.get("correlation"));
            if (corr > Math.abs(strongestCorr)) {
                strongestCorr = corr;
                strongestName = entry.getKey();
            }
        }

        summary.put("strongest_correlation", strongestName);
        summary.put("strongest_value", Math.round(strongestCorr * 100) / 100.0);
        results.put("summary", summary);

        return results;
    }

    private Map<String, Object> createCorrelationEntry(CorrelationBuffer buffer, String description) {
        Map<String, Object> entry = new LinkedHashMap<>();
        double corr = buffer.calculateCorrelation();
        entry.put("correlation", Math.round(corr * 1000) / 1000.0);
        entry.put("samples", buffer.getCount());
        entry.put("description", description);
        entry.put("strength", getCorrelationStrength(corr));
        return entry;
    }

    private String getCorrelationStrength(double corr) {
        double abs = Math.abs(corr);
        if (abs >= 0.8)
            return "VERY_STRONG";
        if (abs >= 0.6)
            return "STRONG";
        if (abs >= 0.4)
            return "MODERATE";
        if (abs >= 0.2)
            return "WEAK";
        return "NONE";
    }

    /**
     * 초기화
     */
    public void reset() {
        chunkVsFrameTime.reset();
        entityVsSimulation.reset();
        memoryVsGcFreq.reset();
        pathfindingVsTick.reset();
        zombieVsTick.reset();
        vehicleVsTick.reset();
        lastGcCount = 0;
        lastTickTime = System.currentTimeMillis();
    }

    // --- 내부 클래스 ---

    private static class CorrelationBuffer {
        private final double[] xBuffer;
        private final double[] yBuffer;
        private final int size;
        private int count = 0;
        private int head = 0;

        CorrelationBuffer(int size) {
            this.size = size;
            this.xBuffer = new double[size];
            this.yBuffer = new double[size];
        }

        void addSample(double x, double y) {
            xBuffer[head] = x;
            yBuffer[head] = y;
            head = (head + 1) % size;
            if (count < size)
                count++;
        }

        int getCount() {
            return count;
        }

        void reset() {
            count = 0;
            head = 0;
        }

        double calculateCorrelation() {
            if (count < 2)
                return 0;

            double sumX = 0, sumY = 0, sumXY = 0;
            double sumX2 = 0, sumY2 = 0;

            for (int i = 0; i < count; i++) {
                double x = xBuffer[i];
                double y = yBuffer[i];
                sumX += x;
                sumY += y;
                sumXY += x * y;
                sumX2 += x * x;
                sumY2 += y * y;
            }

            double n = count;
            double numerator = n * sumXY - sumX * sumY;
            double denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

            return denominator == 0 ? 0 : numerator / denominator;
        }
    }
}
