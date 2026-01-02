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
 * BottleneckDetector의 관측치를 Primitive 타입으로 제공.
 * Pulse SPI를 통해 Fuse에 메트릭을 전달합니다.
 * 
 * Hub & Spoke 원칙:
 * - Echo: 관측치만 제공 (severity, category)
 * - Fuse: 판단/정책 결정 (임계값, 조치)
 * 
 * @since Echo 2.0
 * @since Echo 2.1 - IProvider 메서드 구현 추가
 * @since Echo 3.0 - Primitive-only API
 */
public class EchoHintProvider implements IOptimizationHintProvider {

    public static final String PROVIDER_ID = "echo.hints";
    public static final String PROVIDER_NAME = "Echo Optimization Hints";
    public static final String PROVIDER_VERSION = "2.0.0";

    private static EchoHintProvider instance;
    private boolean enabled = true;

    // ═══════════════════════════════════════════════════════════════
    // Primitive Cache (Atomic Snapshot)
    // ═══════════════════════════════════════════════════════════════

    private volatile String cachedTopTargetId = null;
    private volatile int cachedTopSeverity = 0;
    private volatile String cachedTopCategory = null;

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
        return "Provides primitive metrics based on Echo's bottleneck analysis";
    }

    @Override
    public int getPriority() {
        return 100;
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
    // Snapshot Management (Echo 내부에서만 호출)
    // ═══════════════════════════════════════════════════════════════

    /**
     * 스냅샷 갱신 - Echo 내부에서만 호출.
     * 호출 시점: EchoProfiler 또는 EchoMod의 onTick()
     */
    public void updateSnapshot() {
        try {
            BottleneckDetector detector = BottleneckDetector.getInstance();
            if (detector == null) {
                clearCache();
                return;
            }

            List<Bottleneck> top = detector.identifyTopN(1);
            if (!top.isEmpty()) {
                Bottleneck b = top.get(0);
                this.cachedTopTargetId = b.name != null ? b.name.toLowerCase() : null;
                this.cachedTopSeverity = (int) (b.ratio * 100);
                this.cachedTopCategory = mapCategory(b);
            } else {
                clearCache();
            }
        } catch (Exception e) {
            // Fail-soft
            clearCache();
        }
    }

    private void clearCache() {
        this.cachedTopTargetId = null;
        this.cachedTopSeverity = 0;
        this.cachedTopCategory = null;
    }

    // ═══════════════════════════════════════════════════════════════
    // Primitive-only API (v2.0)
    // ═══════════════════════════════════════════════════════════════

    @Override
    public String getTopTargetId() {
        return cachedTopTargetId;
    }

    @Override
    public int getTopTargetSeverity() {
        return cachedTopSeverity;
    }

    @Override
    public String getTopTargetCategory() {
        return cachedTopCategory;
    }

    // ═══════════════════════════════════════════════════════════════
    // Deprecated (하위 호환)
    // ═══════════════════════════════════════════════════════════════

    @Override
    @Deprecated
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
            // Fail-soft
        }

        return Optional.empty();
    }

    @Override
    @Deprecated
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
            // Fail-soft
        }

        return hints;
    }

    @Override
    @Deprecated
    public boolean isUnderPressure() {
        return false; // Fuse가 판단해야 함
    }

    // ═══════════════════════════════════════════════════════════════
    // Helper Methods
    // ═══════════════════════════════════════════════════════════════

    @Deprecated
    private OptimizationHint createHint(Bottleneck b) {
        String category = mapCategory(b);
        int priority = (int) (b.ratio * 100);
        String recommendation = String.format("Optimize %s: %.1fms (%.0f%%)",
                b.displayName, b.avgMs, b.ratio * 100);

        return new OptimizationHint(
                b.name.toLowerCase(),
                b.displayName,
                priority,
                recommendation,
                category);
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
