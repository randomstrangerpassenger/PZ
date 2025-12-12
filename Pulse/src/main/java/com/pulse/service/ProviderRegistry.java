package com.pulse.service;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.spi.*;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * IProviderRegistry 구현체.
 * 모든 SPI 프로바이더를 관리하는 중앙 레지스트리.
 */
public class ProviderRegistry implements IProviderRegistry {

    private static final String LOG = PulseLogger.PULSE;
    private static final ProviderRegistry INSTANCE = new ProviderRegistry();

    private final Map<String, IProvider> providersById = new ConcurrentHashMap<>();
    private final List<IProviderCallback> callbacks = new ArrayList<>();
    private final Map<String, ProviderLifecycle> lifecycles = new ConcurrentHashMap<>();

    private ProviderRegistry() {
    }

    public static ProviderRegistry getInstance() {
        return INSTANCE;
    }

    @Override
    public <T extends IProvider> void register(T provider) {
        if (provider == null) {
            throw new IllegalArgumentException("Provider cannot be null");
        }

        String id = provider.getId();
        if (providersById.containsKey(id)) {
            PulseLogger.warn(LOG, "Provider already registered: {}", id);
            return;
        }

        providersById.put(id, provider);
        lifecycles.put(id, ProviderLifecycle.REGISTERED);

        PulseLogger.info(LOG, "Registered provider: {} ({}) v{}",
                provider.getName(), id, provider.getVersion());

        // 콜백 알림
        for (IProviderCallback callback : callbacks) {
            try {
                callback.onProviderRegistered(provider);
            } catch (Exception e) {
                PulseLogger.error(LOG, "Callback error: {}", e.getMessage());
            }
        }

        // 초기화
        initializeProvider(provider);
    }

    private void initializeProvider(IProvider provider) {
        String id = provider.getId();
        try {
            updateLifecycle(provider, ProviderLifecycle.INITIALIZING);
            provider.onInitialize();
            updateLifecycle(provider, ProviderLifecycle.ACTIVE);
            PulseLogger.info(LOG, "Provider initialized: {}", id);
        } catch (Exception e) {
            updateLifecycle(provider, ProviderLifecycle.ERROR);
            PulseLogger.error(LOG, "Failed to initialize provider {}: {}", id, e.getMessage());
            notifyError(provider, e);
        }
    }

    @Override
    public void unregister(String providerId) {
        IProvider provider = providersById.remove(providerId);
        if (provider != null) {
            try {
                updateLifecycle(provider, ProviderLifecycle.SHUTTING_DOWN);
                provider.onShutdown();
                updateLifecycle(provider, ProviderLifecycle.TERMINATED);
            } catch (Exception e) {
                PulseLogger.error(LOG, "Error during shutdown: {}", e.getMessage());
            }

            lifecycles.remove(providerId);
            PulseLogger.info(LOG, "Unregistered provider: {}", providerId);

            for (IProviderCallback callback : callbacks) {
                try {
                    callback.onProviderUnregistered(provider);
                } catch (Exception e) {
                    PulseLogger.error(LOG, "Callback error: {}", e.getMessage());
                }
            }
        }
    }

    @Override
    public Optional<IProvider> getProvider(String providerId) {
        return Optional.ofNullable(providersById.get(providerId));
    }

    @Override
    @SuppressWarnings("unchecked")
    public <T extends IProvider> Optional<T> getProvider(Class<T> type) {
        return providersById.values().stream()
                .filter(p -> type.isAssignableFrom(p.getClass()))
                .filter(IProvider::isEnabled)
                .max(Comparator.comparingInt(IProvider::getPriority))
                .map(p -> (T) p);
    }

    @Override
    @SuppressWarnings("unchecked")
    public <T extends IProvider> Collection<T> getProviders(Class<T> type) {
        return providersById.values().stream()
                .filter(p -> type.isAssignableFrom(p.getClass()))
                .filter(IProvider::isEnabled)
                .sorted((a, b) -> Integer.compare(b.getPriority(), a.getPriority()))
                .map(p -> (T) p)
                .collect(Collectors.toList());
    }

    @Override
    public Collection<IProvider> getAllProviders() {
        return Collections.unmodifiableCollection(providersById.values());
    }

    @Override
    public boolean isRegistered(String providerId) {
        return providersById.containsKey(providerId);
    }

    @Override
    public <T extends IProvider> boolean hasProvider(Class<T> type) {
        return providersById.values().stream()
                .anyMatch(p -> type.isAssignableFrom(p.getClass()) && p.isEnabled());
    }

    // ============================================================
    // 추가 기능
    // ============================================================

    /**
     * 콜백 등록
     */
    public void addCallback(IProviderCallback callback) {
        if (callback != null && !callbacks.contains(callback)) {
            callbacks.add(callback);
        }
    }

    /**
     * 콜백 해제
     */
    public void removeCallback(IProviderCallback callback) {
        callbacks.remove(callback);
    }

    /**
     * 프로바이더 생명주기 조회
     */
    public ProviderLifecycle getLifecycle(String providerId) {
        return lifecycles.getOrDefault(providerId, ProviderLifecycle.TERMINATED);
    }

    /**
     * 모든 프로바이더 종료
     */
    public void shutdownAll() {
        PulseLogger.info(LOG, "Shutting down all providers...");
        for (String id : new ArrayList<>(providersById.keySet())) {
            unregister(id);
        }
    }

    private void updateLifecycle(IProvider provider, ProviderLifecycle newState) {
        String id = provider.getId();
        ProviderLifecycle oldState = lifecycles.get(id);
        lifecycles.put(id, newState);

        for (IProviderCallback callback : callbacks) {
            try {
                callback.onLifecycleChanged(provider, oldState, newState);
            } catch (Exception e) {
                PulseLogger.error(LOG, "Callback error: {}", e.getMessage());
            }
        }
    }

    private void notifyError(IProvider provider, Throwable error) {
        for (IProviderCallback callback : callbacks) {
            try {
                callback.onProviderError(provider, error);
            } catch (Exception e) {
                PulseLogger.error(LOG, "Callback error: {}", e.getMessage());
            }
        }
    }
}
