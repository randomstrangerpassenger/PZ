package com.pulse.api.service.echo;

public interface IBottleneckDetector {
    OptimizationPriority suggestNerveTarget();

    OptimizationPriority suggestFuseTarget();
}
