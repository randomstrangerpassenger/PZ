package com.pulse.api.exception;

/**
 * Exception thrown when a network operation fails.
 *
 * @since 1.1.0
 */
public class NetworkException extends PulseException {

    public NetworkException(String message) {
        super(message);
    }

    public NetworkException(String message, Throwable cause) {
        super(message, cause);
    }
}
