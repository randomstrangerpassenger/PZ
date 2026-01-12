package com.pulse.diagnostics;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 현재 틱의 엔진 상태 정보를 담는 컨텍스트.
 * 
 * Pulse가 매 틱마다 수집하여 하위 모듈에게 제공하는 성능 플래그입니다.
 * 로드맵의 "Performance Flag Broadcast" 요구사항을 충족합니다.
 * 
 * <h2>수집되는 정보</h2>
 * <ul>
 * <li>멀티플레이어 여부</li>
 * <li>좀비 업데이트 수</li>
 * <li>청크 로드/언로드 수</li>
 * <li>플레이어 수 (MP)</li>
 * <li>차량 업데이트 수</li>
 * </ul>
 * 
 * @since Pulse 1.2
 */
public final class PulseTickContext {

    private static final PulseTickContext INSTANCE = new PulseTickContext();

    // 현재 틱 정보
    private volatile long currentTick = 0;
    private volatile boolean multiplayer = false;

    // 업데이트 카운터 (틱별 리셋)
    private final AtomicInteger zombieUpdateCount = new AtomicInteger(0);
    private final AtomicInteger chunkLoadCount = new AtomicInteger(0);
    private final AtomicInteger chunkUnloadCount = new AtomicInteger(0);
    private final AtomicInteger playerCount = new AtomicInteger(0);
    private final AtomicInteger vehicleUpdateCount = new AtomicInteger(0);

    // 누적 통계 (세션)
    private final AtomicLong totalZombieUpdates = new AtomicLong(0);
    private final AtomicLong totalChunkLoads = new AtomicLong(0);

    private PulseTickContext() {
    }

    public static PulseTickContext get() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 틱 관리 (Mixin에서 호출)
    // ─────────────────────────────────────────────────────────────

    /**
     * 새 틱 시작 (카운터 리셋)
     */
    public void beginTick(long tick) {
        this.currentTick = tick;
        zombieUpdateCount.set(0);
        chunkLoadCount.set(0);
        chunkUnloadCount.set(0);
        vehicleUpdateCount.set(0);
    }

    /**
     * 틱 종료 (누적 통계 갱신)
     */
    public void endTick() {
        totalZombieUpdates.addAndGet(zombieUpdateCount.get());
        totalChunkLoads.addAndGet(chunkLoadCount.get());
    }

    // ─────────────────────────────────────────────────────────────
    // 카운터 증가 (Mixin에서 호출)
    // ─────────────────────────────────────────────────────────────

    public void incrementZombieUpdate() {
        zombieUpdateCount.incrementAndGet();
    }

    public void incrementChunkLoad() {
        chunkLoadCount.incrementAndGet();
    }

    public void incrementChunkUnload() {
        chunkUnloadCount.incrementAndGet();
    }

    public void incrementVehicleUpdate() {
        vehicleUpdateCount.incrementAndGet();
    }

    public void setPlayerCount(int count) {
        playerCount.set(count);
    }

    public void setMultiplayer(boolean mp) {
        this.multiplayer = mp;
    }

    // ─────────────────────────────────────────────────────────────
    // Getters (하위 모듈에서 호출)
    // ─────────────────────────────────────────────────────────────

    public long getCurrentTick() {
        return currentTick;
    }

    public boolean isMultiplayer() {
        return multiplayer;
    }

    public int getZombieUpdateCount() {
        return zombieUpdateCount.get();
    }

    public int getChunkLoadCount() {
        return chunkLoadCount.get();
    }

    public int getChunkUnloadCount() {
        return chunkUnloadCount.get();
    }

    public int getPlayerCount() {
        return playerCount.get();
    }

    public int getVehicleUpdateCount() {
        return vehicleUpdateCount.get();
    }

    public long getTotalZombieUpdates() {
        return totalZombieUpdates.get();
    }

    public long getTotalChunkLoads() {
        return totalChunkLoads.get();
    }

    // ─────────────────────────────────────────────────────────────
    // 진단용
    // ─────────────────────────────────────────────────────────────

    public String getSnapshot() {
        return String.format(
                "Tick=%d MP=%s Zombies=%d Chunks=+%d/-%d Players=%d Vehicles=%d",
                currentTick, multiplayer, zombieUpdateCount.get(),
                chunkLoadCount.get(), chunkUnloadCount.get(),
                playerCount.get(), vehicleUpdateCount.get());
    }
}
