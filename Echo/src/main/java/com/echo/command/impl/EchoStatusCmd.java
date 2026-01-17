package com.echo.command.impl;

import com.echo.measure.EchoProfiler;
import com.pulse.api.Pulse;
import com.pulse.api.log.PulseLogger;
import com.pulse.api.spi.IProfilerProvider;

import java.util.Optional;

public class EchoStatusCmd {
        public static void execute(String[] args) {
                EchoProfiler profiler = EchoProfiler.getInstance();
                profiler.printStatus();

                // Enhanced Phase 3: 추가 상태 정보
                PulseLogger.info("Echo", "⚙️ CONFIGURATION");
                PulseLogger.info("Echo", "───────────────────────────────────────────────────────");
                PulseLogger.info("Echo", String.format("  Lua Profiling:   %s",
                                profiler.isLuaProfilingEnabled() ? "✅ ENABLED" : "❌ DISABLED"));
                PulseLogger.info("Echo", String.format("  Spike Threshold: %.2f ms",
                                profiler.getSpikeLog().getThresholdMs()));
                PulseLogger.info("Echo", String.format("  Stack Depth:     %d (current thread)",
                                profiler.getCurrentStackDepth()));
                PulseLogger.info("Echo", String.format("  Session Time:    %d seconds",
                                profiler.getSessionDurationSeconds()));
                PulseLogger.info("Echo", "");

                // Pulse SPI Integration Status
                PulseLogger.info("Echo", "🔗 PULSE INTEGRATION");
                PulseLogger.info("Echo", "───────────────────────────────────────────────────────");

                boolean pulseInitialized = Pulse.isInitialized();
                PulseLogger.info("Echo", String.format("  Pulse Initialized: %s",
                                pulseInitialized ? "✅ YES (v" + Pulse.getVersion() + ")" : "❌ NO"));

                if (pulseInitialized) {
                        boolean hasProvider = Pulse.hasProvider(IProfilerProvider.class);
                        if (hasProvider) {
                                Optional<IProfilerProvider> providerOpt = Pulse.getProviderRegistry()
                                                .getProvider(IProfilerProvider.class);
                                if (providerOpt.isPresent()) {
                                        IProfilerProvider provider = providerOpt.get();
                                        PulseLogger.info("Echo", String.format("  Provider Registered: ✅ %s",
                                                        provider.getId()));
                                        PulseLogger.info("Echo", String.format("  Provider Name: %s (v%s)",
                                                        provider.getName(), provider.getVersion()));
                                }
                        } else {
                                PulseLogger.info("Echo", "  Provider Registered: ❌ NOT REGISTERED");
                        }
                }
                PulseLogger.info("Echo", "");
        }
}
