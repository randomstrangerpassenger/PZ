package com.pulse.api.service.echo;

/**
 * @deprecated Use {@link com.pulse.api.spi.IOptimizationHintProvider} instead.
 *             This interface will be removed in Pulse 2.0.
 * 
 *             Migration:
 *             - suggestFuseTarget() → suggestTarget(CATEGORY_CPU)
 *             - suggestNerveTarget() → suggestTarget(CATEGORY_RENDER) or
 *             suggestTarget(CATEGORY_NETWORK)
 */
@Deprecated
public interface IBottleneckDetector {
    OptimizationPriority suggestNerveTarget();

    OptimizationPriority suggestFuseTarget();
}
