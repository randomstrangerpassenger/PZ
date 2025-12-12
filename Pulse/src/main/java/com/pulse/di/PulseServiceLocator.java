package com.pulse.di;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Service Locator for Pulse ecosystem.
 * Provides a bridge for components that cannot use constructor injection (e.g.
 * Mixins).
 * 
 * Usage:
 * PulseServiceLocator.getInstance().getService(MyService.class);
 */
public class PulseServiceLocator {

    private static final PulseServiceLocator INSTANCE = new PulseServiceLocator();
    private final Map<Class<?>, Object> services = new ConcurrentHashMap<>();

    private PulseServiceLocator() {
    }

    public static PulseServiceLocator getInstance() {
        return INSTANCE;
    }

    public <T> void registerService(Class<T> type, T instance) {
        services.put(type, instance);
    }

    public <T> T getService(Class<T> type) {
        return type.cast(services.get(type));
    }

    public void clear() {
        services.clear();
    }
}
