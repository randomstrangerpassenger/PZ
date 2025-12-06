package com.mutagen.event.lifecycle;

import com.mutagen.event.Event;

/**
 * 월드 로드 시 발생
 */
public class WorldLoadEvent extends Event {
    
    private final String worldName;
    
    public WorldLoadEvent(String worldName) {
        super(false);
        this.worldName = worldName;
    }
    
    public String getWorldName() {
        return worldName;
    }
}
