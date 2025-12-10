package com.echo.pulse;

import com.pulse.api.profiler.IsoGridHook;

/**
 * Bridge for IsoGrid profiling hooks.
 */
public class IsoGridBridge implements IsoGridHook.IIsoGridCallback {

    private static IsoGridBridge INSTANCE;

    private final ThreadLocal<Long> floorStart = new ThreadLocal<>();
    private final ThreadLocal<Long> lightingStart = new ThreadLocal<>();
    private final ThreadLocal<Long> weatherStart = new ThreadLocal<>();
    private final ThreadLocal<Long> recalcStart = new ThreadLocal<>();

    private IsoGridBridge() {
    }

    public static void register() {
        if (INSTANCE != null)
            return;
        INSTANCE = new IsoGridBridge();
        IsoGridHook.setCallback(INSTANCE);

        // Phase 2: Sync fast-flag
        boolean detailsEnabled = com.echo.config.EchoConfig.getInstance().isEnableIsoGridDetails();

        System.out.println("[Echo] IsoGridBridge registered with Pulse (Details: " + detailsEnabled + ")");
    }

    @Override
    public void onRecalcPropertiesStart() {
        long t = com.echo.measure.SubProfiler.getInstance()
                .startRaw(com.echo.measure.SubProfiler.SubLabel.ISO_GRID_RECALC);
        // We reuse a thread local or add new one?
        // Let's assume weatherStart is free or add a new one. Recalc is frequent.
        // Adding new ThreadLocal for Recalc.
        recalcStart.set(t);
    }

    @Override
    public void onRecalcPropertiesEnd() {
        Long start = recalcStart.get();
        if (start != null && start != -1) {
            com.echo.measure.SubProfiler.getInstance().endRaw(com.echo.measure.SubProfiler.SubLabel.ISO_GRID_RECALC,
                    start);
        }
    }

    @Override
    public void onFloorUpdateStart() {
        long t = com.echo.measure.SubProfiler.getInstance()
                .startRaw(com.echo.measure.SubProfiler.SubLabel.ISO_GRID_UPDATE);
        floorStart.set(t);
    }

    @Override
    public void onFloorUpdateEnd() {
        Long start = floorStart.get();
        if (start != null && start != -1) {
            com.echo.measure.SubProfiler.getInstance().endRaw(com.echo.measure.SubProfiler.SubLabel.ISO_GRID_UPDATE,
                    start);
        }
    }

    @Override
    public void onLightingUpdateStart() {
        long t = com.echo.measure.SubProfiler.getInstance()
                .startRaw(com.echo.measure.SubProfiler.SubLabel.ISO_LIGHT_UPDATE);
        lightingStart.set(t);
    }

    @Override
    public void onLightingUpdateEnd() {
        Long start = lightingStart.get();
        if (start != null && start != -1) {
            com.echo.measure.SubProfiler.getInstance().endRaw(com.echo.measure.SubProfiler.SubLabel.ISO_LIGHT_UPDATE,
                    start);
        }
    }

    @Override
    public void onWeatherImpactStart() {
        long t = com.echo.measure.SubProfiler.getInstance()
                .startRaw(com.echo.measure.SubProfiler.SubLabel.ISO_CELL_UPDATE); // Mapping to Cell Update for now
        weatherStart.set(t);
    }

    @Override
    public void onWeatherImpactEnd() {
        Long start = weatherStart.get();
        if (start != null && start != -1) {
            com.echo.measure.SubProfiler.getInstance().endRaw(com.echo.measure.SubProfiler.SubLabel.ISO_CELL_UPDATE,
                    start);
        }
    }
}
