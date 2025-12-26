package com.echo.history;

import com.echo.analysis.CorrelationAnalyzer;
import com.echo.subsystem.ZombieProfiler;
import com.echo.pulse.RenderProfiler;
import com.echo.pulse.TickProfiler;

import java.util.HashMap;
import java.util.Map;

/**
 * Metric Collector
 * Collects and stores historical data for analysis.
 */
public class MetricCollector {
    private final Map<String, MetricHistory> histories = new HashMap<>();
    private static final int HISTORY_SIZE = 1000;

    public MetricCollector() {
        registerMetric("zombie_count");
        registerMetric("tick_time");
        registerMetric("fps");
    }

    public void registerMetric(String name) {
        histories.put(name, new MetricHistory(name, HISTORY_SIZE));
    }

    // Called at End of Tick
    public void collect(TickProfiler tickProfiler, RenderProfiler renderProfiler) {
        // Collect samples from profilers
        // Zombie Count (Per Tick)
        long zombieCount = ZombieProfiler.getInstance().getTickZombieCount();

        // Tick Duration (Last Tick)
        double tickTime = tickProfiler.getLastTickDurationMs();

        // FPS
        double fps = renderProfiler.getCurrentFps();

        addSample("zombie_count", (double) zombieCount);
        addSample("tick_time", tickTime);
        addSample("fps", fps);
    }

    public void addSample(String name, double value) {
        MetricHistory history = histories.get(name);
        if (history != null) {
            history.add(value);
        }
    }

    public MetricHistory getHistory(String name) {
        return histories.get(name);
    }

    public double getCorrelation(String metric1, String metric2) {
        MetricHistory h1 = getHistory(metric1);
        MetricHistory h2 = getHistory(metric2);
        return CorrelationAnalyzer.calculateCorrelation(h1, h2);
    }
}
