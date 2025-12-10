package com.pulse.event.world;

import com.pulse.event.Event;

/**
 * 청크 언로드 이벤트.
 */
public class ChunkUnloadEvent extends Event {

    private final int chunkX;
    private final int chunkY;

    public ChunkUnloadEvent(int chunkX, int chunkY) {
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
        return "ChunkUnload";
    }
}
