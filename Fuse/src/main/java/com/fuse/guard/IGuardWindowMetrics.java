package com.fuse.guard;

/**
 * Guard 윈도우 메트릭 인터페이스.
 * 
 * @deprecated Since Fuse 2.4.0, use
 *             {@link com.pulse.api.guard.IGuardWindowMetrics} instead.
 *             This interface extends the pulse-api version for backward
 *             compatibility.
 *             Will be removed in Fuse 3.0.
 * 
 * @see com.pulse.api.guard.IGuardWindowMetrics
 * @since Fuse 2.2.0
 */
@Deprecated(since = "2.4.0", forRemoval = true)
public interface IGuardWindowMetrics extends com.pulse.api.guard.IGuardWindowMetrics {
    // All methods inherited from pulse-api version
    // This interface exists only for backward compatibility
}
