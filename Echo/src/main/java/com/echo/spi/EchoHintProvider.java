package com.echo.spi;

import com.echo.analysis.BottleneckDetector;
import com.echo.analysis.BottleneckDetector.Bottleneck;
import com.pulse.api.spi.IOptimizationHintProvider;
import com.pulse.api.spi.OptimizationHint;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

/**
 * Echo 힌트 제공자.
 * 
 * BottleneckDetector의 분석 결과를 OptimizationHint로 변환하여 제공.
 * Pulse SPI를 통해 Fuse에 최적화 힌트를 전달합니다.
 * 
 * @since Echo 2.0
 * @since Echo 2.1 - IProvider 메서드 구현 추가
 */
public class EchoHintProvider implements IOptimizationHintProvider {

    public static final String PROVIDER_ID = "echo.hints";
    public static final String PROVIDER_NAME = "Echo Optimization Hints";
    public static final String PROVIDER_VERSION = "1.0.0";

    private static EchoHintProvider instance;
    private boolean enabled = true;

    public static EchoHintProvider getInstance() {
        if (instance == null) {
            instance = new EchoHintProvider();
        }
        return instance;
    }

    private EchoHintProvider() {
    }

    // ═══════════════════════════════════════════════════════════════
    // IProvider Implementation
    // ═══════════════════════════════════════════════════════════════

    @Override
    public String getId() {
        return PROVIDER_ID;
    }

    @Override
    public String getName() {
        return PROVIDER_NAME;
    }

    @Override
    public String getVersion() {
        return PROVIDER_VERSION;
    }

    @Override
    public String getDescription() {
        return "Provides optimization hints based on Echo's bottleneck analysis";
    }

    @Override
    public int getPriority() {
        return 100; // Standard priority
    }

    @Override
    public void onInitialize() {
        // No special initialization needed
    }

    @Override
    public void onShutdown() {
        // No special shutdown needed
    }

    @Override
    public boolean isEnabled() {
        return enabled;
    }

    // ═══════════════════════════════════════════════════════════════
    // IOptimizationHintProvider Implementation
    // ═══════════════════════════════════════════════════════════════

    @Override
    public Optional<OptimizationHint> suggestTarget(String category) {
        try {
            BottleneckDetector detector = BottleneckDetector.getInstance();
            if (detector == null) {
                return Optional.empty();
            }

            List<Bottleneck> bottlenecks = detector.identifyTopN(10);

            for (Bottleneck b : bottlenecks) {
                String mappedCategory = mapCategory(b);
                if (mappedCategory.equals(category)) {
                    return Optional.of(createHint(b));
                }
            }
        } catch (Exception e) {
            // Fail-soft: 에러 시 빈 Optional 반환
        }

        return Optional.empty();
    }

    @Override
    public List<OptimizationHint> getTopHints(int n) {
        List<OptimizationHint> hints = new ArrayList<>();

        try {
            BottleneckDetector detector = BottleneckDetector.getInstance();
            if (detector == null) {
                return hints;
            }

            List<Bottleneck> bottlenecks = detector.identifyTopN(n);

            for (Bottleneck b : bottlenecks) {
                hints.add(createHint(b));
            }
        } catch (Exception e) {
            // Fail-soft: 에러 시 빈 리스트 반환
        }

        return hints;
    }

    @Override
    public boolean isUnderPressure() {
        try {
            BottleneckDetector detector = BottleneckDetector.getInstance();
            if (detector == null) {
                return false;
            }

            List<Bottleneck> top = detector.identifyTopN(1);
            if (!top.isEmpty()) {
                // 상위 병목이 전체의 50% 이상을 차지하면 압박 상태
                return top.get(0).ratio > 0.5;
            }
        } catch (Exception e) {
            // Fail-soft
        }
        return false;
    }

    // ═══════════════════════════════════════════════════════════════
    // Helper Methods
    // ═══════════════════════════════════════════════════════════════

    private OptimizationHint createHint(Bottleneck b) {
        String category = mapCategory(b);
        int priority = (int) (b.ratio * 100); // ratio를 priority로 변환 (0-100)
        String recommendation = String.format("Optimize %s: %.1fms (%.0f%%)",
                b.displayName, b.avgMs, b.ratio * 100);

        return new OptimizationHint(
                b.name.toLowerCase(), // targetName
                b.displayName, // displayName
                priority, // priority
                recommendation, // recommendation
                category // category
        );
    }

    private String mapCategory(Bottleneck b) {
        if (b.name == null)
            return CATEGORY_CPU;

        String name = b.name.toUpperCase();
        if (name.contains("NETWORK") || name.contains("NET")) {
            return CATEGORY_NETWORK;
        } else if (name.contains("RENDER") || name.contains("GRAPHICS")) {
            return CATEGORY_RENDER;
        } else if (name.contains("MEMORY") || name.contains("GC")) {
            return CATEGORY_MEMORY;
        } else if (name.contains("IO") || name.contains("SAVE") || name.contains("LOAD")) {
            return CATEGORY_IO;
        }
        return CATEGORY_CPU;
    }
}
