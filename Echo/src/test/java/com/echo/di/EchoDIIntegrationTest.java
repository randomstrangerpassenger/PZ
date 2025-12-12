package com.echo.di;

import com.echo.config.EchoConfig;
import com.echo.lua.LuaCallTracker;
import com.echo.measure.EchoProfiler;
import com.pulse.di.PulseServiceLocator;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Verifies that the Hybrid DI system correctly allows mocking dependencies
 * for legacy singleton-based classes.
 */
public class EchoDIIntegrationTest {

    @BeforeEach
    void setUp() {
        PulseServiceLocator.getInstance().clear();
        // Reset singletons if possible?
        // Note: We can't easily reset static singletons without reflection or adding
        // reset methods.
        // For this test, we rely on the fact that getInstance() checks the Locator
        // FIRST.
    }

    @AfterEach
    void tearDown() {
        PulseServiceLocator.getInstance().clear();
    }

    @Test
    void testLuaCallTrackerUsesMockedDependencies() {
        // 1. Create Mocks (using anonymous classes for simplicity, or Mockito if
        // available)
        EchoConfig mockConfig = new EchoConfig() {
            @Override
            public boolean isLuaProfilingEnabled() {
                return true; // Force enabled
            }
        };

        EchoProfiler mockProfiler = new EchoProfiler(mockConfig) {
            @Override
            public boolean isLuaProfilingEnabled() {
                return true;
            }
        };

        // 2. Register Mocks in ServiceLocator
        PulseServiceLocator.getInstance().registerService(EchoConfig.class, mockConfig);
        PulseServiceLocator.getInstance().registerService(EchoProfiler.class, mockProfiler);

        // 3. Create LuaCallTracker via ServiceLocator (or manually injecting mocks)
        // If we use getInstance(), it should pick up the mocks if it uses the locator
        // logic internally.
        // Wait, LuaCallTracker.getInstance() logic:
        // Try Locator -> Returns service if found.
        // So if we register LuaCallTracker WITH the mocks, getInstance() returns it.

        LuaCallTracker trackerWithMocks = new LuaCallTracker(mockConfig, mockProfiler);
        PulseServiceLocator.getInstance().registerService(LuaCallTracker.class, trackerWithMocks);

        // 4. Verify generic getInstance() returns our instance
        LuaCallTracker instance = LuaCallTracker.getInstance();
        assertSame(trackerWithMocks, instance, "Should return the registered instance from ServiceLocator");

        // 5. Verify it is using our mocks
        // recordFunctionCall checks profiler.isLuaProfilingEnabled().
        // If it was using the real singleton which might be disabled, it wouldn't
        // record.
        // Our mock forces true.

        instance.recordFunctionCall("test_function", 1000);
        assertNotNull(instance.getFunctionStats("test_function"), "Should have recorded usage because mock enabled it");
    }

    @Test
    void testEchoConfigMocking() {
        // Register a mock config
        EchoConfig mockConfig = new EchoConfig() {
            @Override
            public double getSpikeThresholdMs() {
                return 9999.0;
            }
        };
        PulseServiceLocator.getInstance().registerService(EchoConfig.class, mockConfig);

        // EchoConfig.getInstance() logic:
        // Try Locator -> Return service.
        EchoConfig instance = EchoConfig.getInstance();
        assertSame(mockConfig, instance);
        assertEquals(9999.0, instance.getSpikeThresholdMs());
    }
}
