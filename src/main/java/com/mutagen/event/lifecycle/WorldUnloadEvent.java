package com.mutagen.event.lifecycle;

import com.mutagen.event.Event;

/**
 * 월드 언로드 시 발생
 */
public class WorldUnloadEvent extends Event {
    
    public WorldUnloadEvent() {
        super(false);
    }
}
