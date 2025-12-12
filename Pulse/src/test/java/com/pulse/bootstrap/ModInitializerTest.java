package com.pulse.bootstrap;

import com.pulse.mod.ModLoader;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.lang.instrument.Instrumentation;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ModInitializerTest {

    @Mock
    private ModLoader modLoader;

    @Mock
    private Instrumentation instrumentation;

    private ModInitializer initializer;
    private InitializationContext context;

    @BeforeEach
    void setUp() {
        initializer = new ModInitializer(modLoader);
        context = new InitializationContext(instrumentation);
    }

    @Test
    void initialize_ShouldCallModLoaderMethods() {
        // When
        initializer.initialize(context);

        // Then
        verify(modLoader).discoverMods();
        verify(modLoader).resolveDependencies();
        verify(modLoader).registerMixins();
    }

    @Test
    void initialize_ShouldHandleExceptionGracefully() {
        // Given
        doThrow(new RuntimeException("Test Error")).when(modLoader).discoverMods();

        // When
        initializer.initialize(context);

        // Then
        // Should not throw exception, but log error (verified by absence of crash)
        verify(modLoader).discoverMods();
        verify(modLoader, never()).resolveDependencies();
    }
}
