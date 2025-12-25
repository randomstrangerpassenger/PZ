package com.pulse.api.gc;

import com.pulse.event.Event;

/**
 * GC 관찰 이벤트.
 * 
 * 매 틱 발행되며, Fuse 등 외부 모듈이 구독하여 GC 압력을 판단.
 * pulse-api에 위치하여 Hub&Spoke 아키텍처 준수.
 * 
 * @since Pulse 1.1.0
 */
public class GcObservedEvent extends Event {

    private final GcSample sample;

    public GcObservedEvent(GcSample sample) {
        super(false); // non-cancellable
        this.sample = sample;
    }

    public GcSample getSample() {
        return sample;
    }

    /**
     * 이 이벤트에서 GC가 실제로 발생했는지.
     * 
     * @return sample.gcOccurred()
     */
    public boolean gcOccurred() {
        return sample != null && sample.gcOccurred();
    }
}
