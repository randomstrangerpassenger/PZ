package com.echo.pulse;

import com.echo.subsystem.PathfindingProfiler;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.profiler.PathfindingHook;

/**
 * Bridge between Pulse Mixins and Echo's PathfindingProfiler.
 * Handles timing calculation using ThreadLocal.
 */
public class PathfindingBridge implements PathfindingHook.IPathfindingCallback {

    private static PathfindingBridge INSTANCE;

    private final ThreadLocal<Long> losStart = new ThreadLocal<>();
    private final ThreadLocal<Long> gridStart = new ThreadLocal<>();

    private PathfindingBridge() {
    }

    public static void register() {
        if (INSTANCE != null)
            return;
        INSTANCE = new PathfindingBridge();
        PathfindingHook.setCallback(INSTANCE);

        // Phase 2: Sync fast-flag
        boolean enabled = com.echo.config.EchoConfig.getInstance().isEnablePathfindingDetails();

        PulseLogger.info("Echo", "PathfindingBridge registered with Pulse (Details: " + enabled + ")");
    }

    @Override
    public void onLosCalculationStart() {
        // Zero-Allocation Start (ThreadLocal for thread safety)
        long t = com.echo.measure.SubProfiler.getInstance()
                .startRaw(com.echo.measure.SubProfiler.SubLabel.PATHFINDING_LOS);
        losStart.set(t);
    }

    @Override
    public void onLosCalculationEnd() {
        Long start = losStart.get();
        if (start != null && start != -1) {
            com.echo.measure.SubProfiler.getInstance().endRaw(com.echo.measure.SubProfiler.SubLabel.PATHFINDING_LOS,
                    start);
        }
    }

    @Override
    public void onGridSearchStart() {
        // Map Grid Search to Generic Pathfinding or specific if we add PATHFINDING_GRID
        // later
        long t = com.echo.measure.SubProfiler.getInstance()
                .startRaw(com.echo.measure.SubProfiler.SubLabel.PATHFINDING_GRID);
        gridStart.set(t);
    }

    @Override
    public void onGridSearchEnd() {
        Long start = gridStart.get();
        if (start != null && start != -1) {
            com.echo.measure.SubProfiler.getInstance().endRaw(com.echo.measure.SubProfiler.SubLabel.PATHFINDING_GRID,
                    start);
        }
    }

    @Override
    public void onPathRequest() {
        PathfindingProfiler.getInstance().incrementPathRequests();
    }
}
