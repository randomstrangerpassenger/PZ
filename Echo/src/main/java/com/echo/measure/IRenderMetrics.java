package com.echo.measure;

/**
 * 렌더링 메트릭 인터페이스.
 * 
 * @since Echo 1.0.1
 */
public interface IRenderMetrics {
    RenderEfficiency getRenderEfficiency();

    double getFps();

    double getAvgFrameTimeMs();
}
