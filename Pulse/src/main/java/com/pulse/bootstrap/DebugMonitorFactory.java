package com.pulse.bootstrap;

import com.pulse.PulseEnvironment;
import com.pulse.api.log.PulseLogger;
import com.pulse.mod.ModLoader;
import com.pulse.transformer.PulseClassTransformer;

import java.util.Set;

/**
 * Creates and starts the debug monitor thread.
 */
public class DebugMonitorFactory {
    private static final String LOG = PulseLogger.PULSE;

    public void startMonitor(PulseClassTransformer classTransformer) {
        new Thread(() -> runMonitor(classTransformer), "Pulse-Debug-Monitor").start();
    }

    private void runMonitor(PulseClassTransformer classTransformer) {
        PulseLogger.debug(LOG, "Monitor thread started");

        int waitCount = 0;
        // Wait up to 30 seconds for Game ClassLoader
        while (PulseEnvironment.getGameClassLoader() == null && waitCount < 300) {
            try {
                Thread.sleep(100);
                waitCount++;
            } catch (InterruptedException e) {
                break;
            }
        }

        if (PulseEnvironment.getGameClassLoader() != null) {
            PulseLogger.info(LOG, "Game ClassLoader detected after {}ms", (waitCount * 100));
            PulseLogger.debug(LOG, "ClassLoader: {}", PulseEnvironment.getGameClassLoader());

            try {
                PulseLogger.debug(LOG, "Initializing mods...");
                ModLoader.getInstance().initializeMods();
            } catch (Throwable t) {
                PulseLogger.error(LOG, "Mod initialization error: {}", t.getMessage());
                t.printStackTrace();
            }
        } else {
            PulseLogger.warn(LOG, "WARNING: Game ClassLoader not detected after 30s");
        }

        if (classTransformer != null) {
            try {
                Thread.sleep(5000);
                Set<String> transformed = classTransformer.getTransformedClasses();
                PulseLogger.debug(LOG, "Transformed classes: {}", transformed.size());
                for (String cls : transformed) {
                    PulseLogger.trace(LOG, "  - {}", cls);
                }
            } catch (InterruptedException e) {
                // ignore
            }
        }
    }
}
