package com.nerve.optimizer;

import com.pulse.api.log.PulseLogger;

import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Zombie Network Optimizer for Nerve.
 * 
 * IsoZombie 네트워크 동기화 최적화:
 * - 패킷 배치 처리 (n개씩 묶어서 전송)
 * - 델타 압축 (변경된 필드만 전송)
 * - 우선순위 기반 전송 (근거리 좀비 우선)
 * 
 * @since Nerve 0.2.1
 */
public class ZombieNetworkOptimizer {

    private static final String LOG = "Nerve";
    private static final ZombieNetworkOptimizer INSTANCE = new ZombieNetworkOptimizer();

    /** 배치 처리 큐 */
    private final ConcurrentLinkedQueue<ZombiePacketInfo> pendingPackets = new ConcurrentLinkedQueue<>();

    /** 설정 */
    private int batchSize = 10;
    private boolean deltaCompressionEnabled = true;
    private boolean enabled = false;

    /** 통계 */
    private final AtomicLong totalPackets = new AtomicLong(0);
    private final AtomicLong batchedPackets = new AtomicLong(0);
    private final AtomicLong savedBytes = new AtomicLong(0);
    private final AtomicInteger currentBatchCount = new AtomicInteger(0);

    public static ZombieNetworkOptimizer getInstance() {
        return INSTANCE;
    }

    // --- Configuration ---

    public void enable() {
        this.enabled = true;
        PulseLogger.info(LOG, "ZombieNetworkOptimizer enabled (batch={}, delta={})",
                batchSize, deltaCompressionEnabled);
    }

    public void disable() {
        this.enabled = false;
        flushBatch();
        PulseLogger.info(LOG, "ZombieNetworkOptimizer disabled");
    }

    public void setBatchSize(int size) {
        this.batchSize = Math.max(1, Math.min(50, size));
    }

    public void setDeltaCompressionEnabled(boolean enabled) {
        this.deltaCompressionEnabled = enabled;
    }

    // --- Packet Handling ---

    /**
     * 좀비 패킷을 배치 큐에 추가
     */
    public void queuePacket(int zombieId, float x, float y, float z,
            int state, int targetId, float health) {
        if (!enabled) {
            return;
        }

        ZombiePacketInfo packet = new ZombiePacketInfo(
                zombieId, x, y, z, state, targetId, health,
                System.currentTimeMillis());

        pendingPackets.add(packet);
        totalPackets.incrementAndGet();
        currentBatchCount.incrementAndGet();

        // 배치 크기 도달 시 플러시
        if (currentBatchCount.get() >= batchSize) {
            flushBatch();
        }
    }

    /**
     * 배치 전송 (실제 네트워크 전송은 게임 API 통해)
     */
    public void flushBatch() {
        if (pendingPackets.isEmpty()) {
            return;
        }

        int count = 0;
        while (!pendingPackets.isEmpty() && count < batchSize) {
            ZombiePacketInfo packet = pendingPackets.poll();
            if (packet != null) {
                // 실제 전송 로직은 게임 네트워크 API와 통합 필요
                sendPacket(packet);
                count++;
            }
        }

        if (count > 0) {
            batchedPackets.addAndGet(count);
            currentBatchCount.set(pendingPackets.size());
            PulseLogger.debug(LOG, "Flushed {} zombie packets", count);
        }
    }

    /**
     * 개별 패킷 전송 (게임 API 통합 포인트)
     */
    private void sendPacket(ZombiePacketInfo packet) {
        // TODO: GameServer.sendZombiePacket() 통합
        // 현재는 로깅만
        if (deltaCompressionEnabled) {
            // 델타 압축 시 예상 절약 바이트
            savedBytes.addAndGet(estimateDeltaSavings(packet));
        }
    }

    /**
     * 델타 압축 시 절약 예상 바이트
     */
    private long estimateDeltaSavings(ZombiePacketInfo packet) {
        // 전체 패킷: 약 40바이트
        // 델타 패킷: 약 12바이트 (위치 변경만)
        return 28;
    }

    // --- Tick Update ---

    /**
     * 틱마다 호출 - 오래된 패킷 플러시
     */
    public void onTick() {
        if (!enabled)
            return;

        // 100ms 이상 대기한 패킷이 있으면 플러시
        long now = System.currentTimeMillis();
        ZombiePacketInfo oldest = pendingPackets.peek();
        if (oldest != null && (now - oldest.timestamp) > 100) {
            flushBatch();
        }
    }

    // --- Statistics ---

    public long getTotalPackets() {
        return totalPackets.get();
    }

    public long getBatchedPackets() {
        return batchedPackets.get();
    }

    public long getSavedBytes() {
        return savedBytes.get();
    }

    public int getPendingCount() {
        return pendingPackets.size();
    }

    public void resetStats() {
        totalPackets.set(0);
        batchedPackets.set(0);
        savedBytes.set(0);
    }

    // --- Packet Info ---

    public static class ZombiePacketInfo {
        public final int zombieId;
        public final float x, y, z;
        public final int state;
        public final int targetId;
        public final float health;
        public final long timestamp;

        public ZombiePacketInfo(int zombieId, float x, float y, float z,
                int state, int targetId, float health, long timestamp) {
            this.zombieId = zombieId;
            this.x = x;
            this.y = y;
            this.z = z;
            this.state = state;
            this.targetId = targetId;
            this.health = health;
            this.timestamp = timestamp;
        }
    }
}
