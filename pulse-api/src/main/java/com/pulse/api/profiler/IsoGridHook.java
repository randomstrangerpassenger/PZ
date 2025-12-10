package com.pulse.api.profiler;

/**
 * Hook for IsoGrid (World Map) profiling.
 * 
 * @since Pulse 0.2.0
 */
public final class IsoGridHook {

    private static volatile IIsoGridCallback callback;
    public static volatile boolean detailsEnabled = false;

    private IsoGridHook() {
    }

    public static void setCallback(IIsoGridCallback cb) {
        callback = cb;
    }

    public static void onRecalcPropertiesStart() {
        IIsoGridCallback cb = callback;
        if (cb != null)
            cb.onRecalcPropertiesStart();
    }

    public static void onRecalcPropertiesEnd() {
        IIsoGridCallback cb = callback;
        if (cb != null)
            cb.onRecalcPropertiesEnd();
    }

    public static void onFloorUpdateStart() {
        IIsoGridCallback cb = callback;
        if (cb != null)
            cb.onFloorUpdateStart();
    }

    public static void onFloorUpdateEnd() {
        IIsoGridCallback cb = callback;
        if (cb != null)
            cb.onFloorUpdateEnd();
    }

    public static void onLightingUpdateStart() {
        IIsoGridCallback cb = callback;
        if (cb != null)
            cb.onLightingUpdateStart();
    }

    public static void onLightingUpdateEnd() {
        IIsoGridCallback cb = callback;
        if (cb != null)
            cb.onLightingUpdateEnd();
    }

    public static void onWeatherImpactStart() {
        IIsoGridCallback cb = callback;
        if (cb != null)
            cb.onWeatherImpactStart();
    }

    public static void onWeatherImpactEnd() {
        IIsoGridCallback cb = callback;
        if (cb != null)
            cb.onWeatherImpactEnd();
    }

    public interface IIsoGridCallback {
        void onFloorUpdateStart();

        void onFloorUpdateEnd();

        void onRecalcPropertiesStart();

        void onRecalcPropertiesEnd();

        void onLightingUpdateStart();

        void onLightingUpdateEnd();

        void onWeatherImpactStart();

        void onWeatherImpactEnd();
    }
}
