package com.echo.spi;

import com.echo.analysis.BottleneckDetector;
import com.echo.analysis.BottleneckDetector.Bottleneck;
import com.pulse.api.telemetry.IOptimizationHintProvider;
import com.pulse.api.telemetry.OptimizationHint;

import java.util.ArrayList;
import java.util.List;

/**
 * Echo 힌트 제공자.
 * 
 * BottleneckDetector의 분석 결과를 OptimizationHint로 변환하여 제공.
 * 
 * @since Echo 2.0
 */
public class EchoHintProvider implements IOptimizationHintProvider {

    private static EchoHintProvider instance;

    public static EchoHintProvider getInstance() {
        if (instance == null) {
            instance = new EchoHintProvider();
        }
        return instance;
    }

    private EchoHintProvider() {
    }

    @Override
    public List<OptimizationHint> getHints() {
        List<OptimizationHint> hints = new ArrayList<>();

        try {
            BottleneckDetector detector = BottleneckDetector.getInstance();
            if (detector == null) {
                return hints;
            }

            // 상위 5개 병목을 힌트로 변환
            List<Bottleneck> bottlenecks = detector.identifyTopN(5);

            for (Bottleneck b : bottlenecks) {
                String category = mapCategory(b);
                hints.add(new OptimizationHint(
                        category,
                        b.name.toLowerCase(),
                        b.ratio, // 비율을 severity로 사용
                        1, // 샘플 카운트
                        String.format("%s: %.1fms (%.0f%%)", b.displayName, b.avgMs, b.ratio * 100)));
            }
        } catch (Exception e) {
            // Fail-soft: 에러 시 빈 리스트 반환
        }

        return hints;
    }

    private String mapCategory(Bottleneck b) {
        if (b.name == null)
            return OptimizationHint.CATEGORY_CPU;

        String name = b.name.toUpperCase();
        if (name.contains("NETWORK") || name.contains("NET")) {
            return OptimizationHint.CATEGORY_NETWORK;
        } else if (name.contains("RENDER") || name.contains("GRAPHICS")) {
            return OptimizationHint.CATEGORY_RENDER;
        } else if (name.contains("MEMORY") || name.contains("GC")) {
            return OptimizationHint.CATEGORY_MEMORY;
        }
        return OptimizationHint.CATEGORY_CPU;
    }
}
