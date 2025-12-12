package com.pulse.network;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 네트워크 패킷 통계
 */
public class NetworkPacketStats {

    private final AtomicInteger sentPacketCount = new AtomicInteger(0);
    private final AtomicInteger receivedPacketCount = new AtomicInteger(0);
    private final AtomicLong totalBytesSent = new AtomicLong(0);
    private final AtomicLong totalBytesReceived = new AtomicLong(0);

    public int getSentPacketCount() {
        return sentPacketCount.get();
    }

    public int getReceivedPacketCount() {
        return receivedPacketCount.get();
    }

    public long getTotalBytesSent() {
        return totalBytesSent.get();
    }

    public long getTotalBytesReceived() {
        return totalBytesReceived.get();
    }

    public void recordSent(int bytes) {
        sentPacketCount.incrementAndGet();
        totalBytesSent.addAndGet(bytes);
    }

    public void recordReceived(int bytes) {
        receivedPacketCount.incrementAndGet();
        totalBytesReceived.addAndGet(bytes);
    }

    public void reset() {
        sentPacketCount.set(0);
        receivedPacketCount.set(0);
        totalBytesSent.set(0);
        totalBytesReceived.set(0);
    }

    public String getReport() {
        return String.format(
                "[Pulse/Network] Stats: sent=%d packets (%d bytes), received=%d packets (%d bytes)",
                getSentPacketCount(), getTotalBytesSent(),
                getReceivedPacketCount(), getTotalBytesReceived());
    }
}
