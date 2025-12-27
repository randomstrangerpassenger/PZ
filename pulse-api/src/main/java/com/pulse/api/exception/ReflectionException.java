package com.pulse.api.exception;

/**
 * Exception thrown when a reflection operation fails.
 *
 * @since 1.1.0
 */
public class ReflectionException extends PulseException {

    public ReflectionException(String message) {
        super(message);
    }

    public ReflectionException(String message, Throwable cause) {
        super(message, cause);
    }
}
