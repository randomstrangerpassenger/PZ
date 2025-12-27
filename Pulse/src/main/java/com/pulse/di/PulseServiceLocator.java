package com.pulse.di;

import com.pulse.api.di.IServiceLocator;

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
public class PulseServiceLocator implements IServiceLocator {

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

    @Override
    public <T> T getService(Class<T> type) {
        return type.cast(services.get(type));
    }

    @Override
    public <T> boolean hasService(Class<T> type) {
        return services.containsKey(type);
    }

    public void clear() {
        services.clear();
    }
}
