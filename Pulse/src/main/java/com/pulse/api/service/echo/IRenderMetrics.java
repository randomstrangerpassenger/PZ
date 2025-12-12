package com.pulse.api.service.echo;

public interface IRenderMetrics {
    RenderEfficiency getRenderEfficiency();

    double getFps();

    double getAvgFrameTimeMs();
}
