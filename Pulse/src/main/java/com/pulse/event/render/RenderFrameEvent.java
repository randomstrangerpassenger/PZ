package com.pulse.event.render;

import com.pulse.event.Event;

/**
 * 렌더 프레임 이벤트.
 * 
 * 화면 렌더링 루프에서 발생합니다.
 * Echo의 프레임 타임 분석에 사용됩니다.
 * 
 * @since Pulse 1.2
 */
public class RenderFrameEvent extends Event {

    private final long frameNumber;
    private final long durationNanos;

    public RenderFrameEvent(long frameNumber, long durationNanos) {
        super(false);
        this.frameNumber = frameNumber;
        this.durationNanos = durationNanos;
    }

    /**
     * 프레임 번호
     */
    public long getFrameNumber() {
        return frameNumber;
    }

    /**
     * 프레임 렌더링 소요 시간 (나노초)
     */
    public long getDurationNanos() {
        return durationNanos;
    }

    /**
     * 프레임 렌더링 소요 시간 (밀리초)
     */
    public double getDurationMs() {
        return durationNanos / 1_000_000.0;
    }

    /**
     * 예상 FPS (이 프레임 기준)
     */
    public double getInstantFps() {
        return durationNanos > 0 ? 1_000_000_000.0 / durationNanos : 0;
    }

    @Override
    public String getEventName() {
        return "RenderFrame";
    }
}
