package com.echo.event;

import com.pulse.api.event.Event;

/**
 * EchoProfiler 리셋 이벤트.
 * 프로파일러가 리셋될 때 발행됩니다.
 * 
 * <p>
 * 이 이벤트를 통해 다른 컴포넌트들이 프로파일러 리셋에 반응할 수 있습니다.
 * </p>
 * 
 * @since 1.1.0
 */
public class ProfilerResetEvent extends Event {

    private final long timestamp;
    private final String reason;
    private final boolean fullReset;

    /**
     * 리셋 이벤트 생성.
     * 
     * @param reason    리셋 사유
     * @param fullReset 전체 리셋 여부
     */
    public ProfilerResetEvent(String reason, boolean fullReset) {
        this.timestamp = System.currentTimeMillis();
        this.reason = reason;
        this.fullReset = fullReset;
    }

    /**
     * 기본 리셋 이벤트 (일반 리셋).
     */
    public ProfilerResetEvent() {
        this("manual", false);
    }

    public long getTimestamp() {
        return timestamp;
    }

    public String getReason() {
        return reason;
    }

    public boolean isFullReset() {
        return fullReset;
    }
}
