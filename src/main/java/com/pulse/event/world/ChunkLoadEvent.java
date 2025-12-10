package com.pulse.event.world;

import com.pulse.event.Event;

/**
 * 청크 로드 이벤트.
 */
public class ChunkLoadEvent extends Event {

    private final int chunkX;
    private final int chunkY;

    public ChunkLoadEvent(int chunkX, int chunkY) {
        this.chunkX = chunkX;
        this.chunkY = chunkY;
    }

    public int getChunkX() {
        return chunkX;
    }

    public int getChunkY() {
        return chunkY;
    }

    @Override
    public String getEventName() {
        return "ChunkLoad";
    }
}
