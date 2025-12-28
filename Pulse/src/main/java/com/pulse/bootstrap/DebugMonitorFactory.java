package com.pulse.bootstrap;

import com.pulse.PulseEnvironment;
import com.pulse.api.di.PulseServices;
import com.pulse.api.event.Event;
import com.pulse.api.event.EventListener;
import com.pulse.api.event.EventPriority;
import com.pulse.api.event.IEventBus;
import com.pulse.api.log.PulseLogger;
import com.pulse.event.EventBus;
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
                // Initialize PulseServices before mod initialization
                initPulseServices();

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

    /**
     * Initialize PulseServices with full services.
     * This must be called before mod initialization.
     * 
     * @since v2.1 - Full service initialization (null 금지)
     */
    private void initPulseServices() {
        try {
            // Create IEventBus adapter wrapping EventBus singleton
            IEventBus eventBusAdapter = new IEventBus() {

                @Override
                public <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener,
                        String subscriberId) {
                    // Use static subscribe with modId
                    EventBus.subscribe(eventType, listener, EventPriority.NORMAL, subscriberId);
                }

                @Override
                public void unsubscribeAll(String subscriberId) {
                    EventBus.unsubscribeAllByModId(subscriberId);
                }

                @Override
                public <T extends Event> void publish(T event) {
                    EventBus.post(event);
                }

                @Override
                public void clearAll() {
                    EventBus.getInstance().clearAll();
                }

                @Override
                public void setDebug(boolean debug) {
                    EventBus.getInstance().setDebug(debug);
                }
            };

            // Full service initialization (null 금지)
            com.pulse.api.ui.IHUDOverlay hudOverlay = com.pulse.ui.HUDOverlay.getInstance();
            com.pulse.api.scheduler.IScheduler scheduler = com.pulse.scheduler.PulseScheduler.getInstance();
            com.pulse.api.command.ICommandRegistry commands = CommandRegistryAdapter.getInstance();
            com.pulse.api.hook.IPulseHookRegistry hooks = PulseHookRegistryAdapter.getInstance();
            com.pulse.api.profiler.IProfilerBridge profiler = ProfilerBridgeAdapter.getInstance();

            // Initialize PulseServices with all services
            PulseServices.init(null, eventBusAdapter, hudOverlay, scheduler, commands, hooks, profiler);
            PulseLogger.info(LOG, "PulseServices initialized (Full services)");
        } catch (Exception e) {
            PulseLogger.error(LOG, "PulseServices initialization failed: {}", e.getMessage());
            e.printStackTrace();
        }
    }
}
