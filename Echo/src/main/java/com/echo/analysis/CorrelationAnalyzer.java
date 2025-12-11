package com.echo.analysis;

import com.echo.aggregate.TimingData;
import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.fuse.ZombieProfiler;

import java.util.HashMap;
import java.util.Map;

/**
 * Correlation Analyzer
 * 
 * Finds correlations between different metrics.
 * Example: Do high Zombie counts correlate with high Frame times?
 * 
 * Uses Pearson Correlation Coefficient.
 */
public class CorrelationAnalyzer {

    // Simple ring buffer for paired data
    private static final int CSV_BUFFER_SIZE = 100;
    private final double[] xBuffer = new double[CSV_BUFFER_SIZE];
    private final double[] yBuffer = new double[CSV_BUFFER_SIZE];
    private int count = 0;
    private int head = 0;

    public void addSample(double x, double y) {
        xBuffer[head] = x;
        yBuffer[head] = y;
        head = (head + 1) % CSV_BUFFER_SIZE;
        if (count < CSV_BUFFER_SIZE)
            count++;
    }

    /**
     * Calculate Pearson Correlation Coefficient (-1.0 to 1.0)
     */
    public double calculateCorrelation() {
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

    // ===================================
    // Specific Analyzers
    // ===================================

    // Zombie Count vs Tick Duration
    private final CorrelationAnalyzer zombieVsTick = new CorrelationAnalyzer();

    public void onTick() {
        // Collect data
        long zombieCount = ZombieProfiler.getInstance().getZombieCount();
        TimingData tickData = EchoProfiler.getInstance().getTimingData(ProfilingPoint.TICK);

        // We need the *last* tick duration, but TimingData aggregates.
        // Ideally we'd get the exact duration of this tick.
        // For now, let's use the average of the last 1s as a proxy if we can't get
        // instantaneous.
        // Better: Use EchoProfiler's last tick duration if exposed, or hook directly.
        // Assuming we call this POST tick.

        // Let's rely on TimingData to give us a "recent" value or average.
        double tickMs = tickData.getStats1s().getAverage() / 1000.0;

        zombieVsTick.addSample(zombieCount, tickMs);
    }

    public Map<String, Double> getCorrelations() {
        Map<String, Double> map = new HashMap<>();
        map.put("zombie_vs_tick", zombieVsTick.calculateCorrelation());
        return map;
    }
}
