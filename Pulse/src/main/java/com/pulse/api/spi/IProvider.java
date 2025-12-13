package com.pulse.api.spi;

/**
 * Base interface for all Pulse SPI providers.
 * 
 * @since Pulse 1.0
 */
public interface IProvider {

    /**
     * Get the unique identifier for this provider.
     */
    String getId();

    /**
     * Get the display name of this provider.
     */
    String getName();

    /**
     * Get the version of this provider.
     */
    String getVersion();

    /**
     * Get the description of this provider.
     */
    String getDescription();

    /**
     * Get the priority of this provider.
     * Higher priority providers are loaded first.
     * 
     * @return Priority constant from {@link Priority}
     */
    int getPriority();

    /**
     * Called when the provider is initialized.
     */
    void onInitialize();

    /**
     * Called when the provider is shut down.
     */
    void onShutdown();

    /**
     * Check if the provider is enabled.
     */
    boolean isEnabled();
}
