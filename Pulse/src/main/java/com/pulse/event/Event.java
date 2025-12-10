package com.pulse.event;

/**
 * 모든 Pulse 이벤트의 기본 클래스.
 */
public abstract class Event {
    
    private boolean cancelled = false;
    private final boolean cancellable;
    
    protected Event() {
        this(false);
    }
    
    protected Event(boolean cancellable) {
        this.cancellable = cancellable;
    }
    
    /**
     * 이벤트 취소 (취소 가능한 이벤트만)
     */
    public void cancel() {
        if (!cancellable) {
            throw new UnsupportedOperationException("This event cannot be cancelled");
        }
        this.cancelled = true;
    }
    
    public boolean isCancelled() {
        return cancelled;
    }
    
    public boolean isCancellable() {
        return cancellable;
    }
    
    /**
     * 이벤트 이름 (디버깅용)
     */
    public String getEventName() {
        return getClass().getSimpleName();
    }
}
