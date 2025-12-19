package com.pulse.core;

import java.util.function.Consumer;

/**
 * Configuration for Pulse Core initialization.
 * Used by {@link PulseCoreBootstrap#init(PulseCoreConfig)}.
 * 
 * @since Pulse 0.9
 */
public final class PulseCoreConfig {

    private final CoreEnvironment environment;
    private final CoreFeatureFlags featureFlags;
    private final Consumer<String> logSink;

    private PulseCoreConfig(Builder builder) {
        this.environment = builder.environment;
        this.featureFlags = builder.featureFlags;
        this.logSink = builder.logSink;
    }

    public CoreEnvironment getEnvironment() {
        return environment;
    }

    public CoreFeatureFlags getFeatureFlags() {
        return featureFlags;
    }

    public Consumer<String> getLogSink() {
        return logSink;
    }

    /**
     * Create a new configuration builder.
     */
    public static Builder builder() {
        return new Builder();
    }

    /**
     * Builder for PulseCoreConfig.
     */
    public static class Builder {
        private CoreEnvironment environment = DefaultCoreEnvironment.getInstance();
        private CoreFeatureFlags featureFlags = DefaultCoreFeatureFlags.INSTANCE;
        private Consumer<String> logSink = System.out::println;

        public Builder environment(CoreEnvironment env) {
            if (env != null)
                this.environment = env;
            return this;
        }

        public Builder featureFlags(CoreFeatureFlags flags) {
            if (flags != null)
                this.featureFlags = flags;
            return this;
        }

        public Builder logSink(Consumer<String> sink) {
            if (sink != null)
                this.logSink = sink;
            return this;
        }

        public PulseCoreConfig build() {
            return new PulseCoreConfig(this);
        }
    }
}
