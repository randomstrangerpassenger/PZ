package com.pulse.api.exception;

/**
 * Pulse 예외 계층의 루트 클래스.
 * 모든 Pulse 관련 예외는 이 클래스를 상속합니다.
 * 
 * @since 1.1.0
 */
public class PulseException extends RuntimeException {

    public PulseException(String message) {
        super(message);
    }

    public PulseException(String message, Throwable cause) {
        super(message, cause);
    }

    public PulseException(Throwable cause) {
        super(cause);
    }
}
