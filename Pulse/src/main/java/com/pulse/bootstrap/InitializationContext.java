package com.pulse.bootstrap;

import java.lang.instrument.Instrumentation;

/**
 * Pulse initialization context.
 * Holds references required during the initialization process.
 */
public class InitializationContext {
    private final Instrumentation instrumentation;

    public InitializationContext(Instrumentation instrumentation) {
        this.instrumentation = instrumentation;
    }

    public Instrumentation getInstrumentation() {
        return instrumentation;
    }
}
