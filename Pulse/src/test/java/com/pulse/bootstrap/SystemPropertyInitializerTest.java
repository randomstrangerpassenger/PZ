package com.pulse.bootstrap;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.lang.instrument.Instrumentation;
import java.util.Properties;

import static org.junit.jupiter.api.Assertions.assertEquals;

@ExtendWith(MockitoExtension.class)
class SystemPropertyInitializerTest {

    @Mock
    private Instrumentation instrumentation;

    private InitializationContext context;
    private SystemPropertyInitializer initializer;
    private Properties originalProperties;

    @BeforeEach
    void setUp() {
        // 백업
        originalProperties = (Properties) System.getProperties().clone();

        context = new InitializationContext(instrumentation);
        initializer = new SystemPropertyInitializer();
    }

    @AfterEach
    void tearDown() {
        // 복원
        System.setProperties(originalProperties);
    }

    @Test
    void initialize_ShouldSetMixinProperties() {
        // Given
        System.clearProperty("mixin.debug"); // ensure it's not set initially

        // When
        initializer.initialize(context);

        // Then
        assertEquals("true", System.getProperty("mixin.debug"));
        assertEquals("true", System.getProperty("mixin.debug.verbose"));
        assertEquals("true", System.getProperty("mixin.debug.export"));
        assertEquals("false", System.getProperty("mixin.debug.export.decompile"));
        assertEquals("true", System.getProperty("mixin.dumpTargetOnFailure"));
        assertEquals("true", System.getProperty("mixin.checks"));
        assertEquals("true", System.getProperty("mixin.hotSwap"));
    }
}
