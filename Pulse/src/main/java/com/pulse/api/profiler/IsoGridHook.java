package com.pulse.api.profiler;

/**
 * IsoGrid Hooks for Echo.
 * 
 * Allows Echo to receive IsoGrid-level timing events from Pulse mixins.
 * 
 * @since Pulse 1.1
 */
public class IsoGridHook {

    /**
     * 상세 프로파일링 활성화 플래그.
     * Mixin에서 이 값을 체크하여 성능 오버헤드를 최소화합니다.
     */
    public static volatile boolean enabled = false;

    public interface IIsoGridCallback {
        void onRecalcPropertiesStart();

        void onRecalcPropertiesEnd();

        void onFloorUpdateStart();

        void onFloorUpdateEnd();

        void onLightingUpdateStart();

        void onLightingUpdateEnd();

        void onWeatherImpactStart();

        void onWeatherImpactEnd();
    }

    private static IIsoGridCallback callback;

    public static void setCallback(IIsoGridCallback cb) {
        callback = cb;
    }

    public static void clearCallback() {
        callback = null;
    }

    public static void onRecalcPropertiesStart() {
        if (callback != null) {
            callback.onRecalcPropertiesStart();
        }
    }

    public static void onRecalcPropertiesEnd() {
        if (callback != null) {
            callback.onRecalcPropertiesEnd();
        }
    }

    public static void onFloorUpdateStart() {
        if (callback != null) {
            callback.onFloorUpdateStart();
        }
    }

    public static void onFloorUpdateEnd() {
        if (callback != null) {
            callback.onFloorUpdateEnd();
        }
    }

    public static void onLightingUpdateStart() {
        if (callback != null) {
            callback.onLightingUpdateStart();
        }
    }

    public static void onLightingUpdateEnd() {
        if (callback != null) {
            callback.onLightingUpdateEnd();
        }
    }

    public static void onWeatherImpactStart() {
        if (callback != null) {
            callback.onWeatherImpactStart();
        }
    }

    public static void onWeatherImpactEnd() {
        if (callback != null) {
            callback.onWeatherImpactEnd();
        }
    }
}
