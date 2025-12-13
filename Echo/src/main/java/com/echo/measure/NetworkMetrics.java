package com.echo.measure;

import java.util.*;
import com.pulse.api.service.echo.ConnectionQuality;
import com.pulse.api.service.echo.INetworkMetrics;

/**
 * 네트워크 메트릭 수집기.
 * 
 * Phase 5.1: 멀티플레이어 네트워크 성능 모니터링.
 * Ping, 패킷 통계, 대역폭, 손실률 등을 추적합니다.
 * 
 * @since 1.0.1
 */
public class NetworkMetrics implements INetworkMetrics {

    private static final NetworkMetrics INSTANCE = new NetworkMetrics();

    // 네트워크 통계
    private volatile long packetsSent = 0;
    private volatile long packetsReceived = 0;
    private volatile long packetsLost = 0;
    private volatile long bytesSent = 0;
    private volatile long bytesReceived = 0;

    // Ping 통계
    private volatile double currentPingMs = 0;
    private volatile double avgPingMs = 0;
    private volatile double maxPingMs = 0;
    private volatile double minPingMs = Double.MAX_VALUE;
    private final LinkedList<Double> pingHistory = new LinkedList<>();
    private static final int PING_HISTORY_SIZE = 100;

    // 시간 추적
    private long lastUpdateTime = System.currentTimeMillis();
    private long sessionStartTime = System.currentTimeMillis();

    // 대역폭 계산
    private volatile double uploadBandwidthKBps = 0;
    private volatile double downloadBandwidthKBps = 0;
    private long lastBytesSent = 0;
    private long lastBytesReceived = 0;

    public static NetworkMetrics getInstance() {
        return INSTANCE;
    }

    /**
     * 패킷 전송 기록
     */
    public void recordPacketSent(int bytes) {
        packetsSent++;
        bytesSent += bytes;
    }

    /**
     * 패킷 수신 기록
     */
    public void recordPacketReceived(int bytes) {
        packetsReceived++;
        bytesReceived += bytes;
    }

    /**
     * 패킷 손실 기록
     */
    public void recordPacketLost() {
        packetsLost++;
    }

    /**
     * Ping 업데이트
     */
    public void updatePing(double pingMs) {
        this.currentPingMs = pingMs;
        this.maxPingMs = Math.max(maxPingMs, pingMs);
        this.minPingMs = Math.min(minPingMs, pingMs);

        synchronized (pingHistory) {
            pingHistory.addLast(pingMs);
            while (pingHistory.size() > PING_HISTORY_SIZE) {
                pingHistory.removeFirst();
            }

            // 평균 계산
            double sum = 0;
            for (double p : pingHistory) {
                sum += p;
            }
            avgPingMs = sum / pingHistory.size();
        }
    }

    /**
     * 주기적 업데이트 (틱마다 호출)
     */
    public void update() {
        long now = System.currentTimeMillis();
        long deltaTime = now - lastUpdateTime;

        if (deltaTime >= 1000) { // 1초마다 대역폭 계산
            long sentDelta = bytesSent - lastBytesSent;
            long receivedDelta = bytesReceived - lastBytesReceived;

            uploadBandwidthKBps = (sentDelta * 1000.0 / deltaTime) / 1024.0;
            downloadBandwidthKBps = (receivedDelta * 1000.0 / deltaTime) / 1024.0;

            lastBytesSent = bytesSent;
            lastBytesReceived = bytesReceived;
            lastUpdateTime = now;
        }
    }

    // --- Getters ---

    public double getCurrentPingMs() {
        return currentPingMs;
    }

    @Override
    public double getAvgPingMs() {
        return avgPingMs;
    }

    public double getMaxPingMs() {
        return maxPingMs;
    }

    public double getMinPingMs() {
        return minPingMs == Double.MAX_VALUE ? 0 : minPingMs;
    }

    public long getPacketsSent() {
        return packetsSent;
    }

    public long getPacketsReceived() {
        return packetsReceived;
    }

    public long getPacketsLost() {
        return packetsLost;
    }

    @Override
    public double getPacketLossRate() {
        long total = packetsSent + packetsReceived;
        if (total == 0)
            return 0;
        return (double) packetsLost / (packetsLost + packetsReceived) * 100;
    }

    public long getBytesSent() {
        return bytesSent;
    }

    public long getBytesReceived() {
        return bytesReceived;
    }

    public double getUploadBandwidthKBps() {
        return uploadBandwidthKBps;
    }

    public double getDownloadBandwidthKBps() {
        return downloadBandwidthKBps;
    }

    /**
     * 세션 시간 (밀리초)
     */
    public long getSessionDurationMs() {
        return System.currentTimeMillis() - sessionStartTime;
    }

    /**
     * 연결 품질 등급
     */
    @Override
    public ConnectionQuality getConnectionQuality() {
        double loss = getPacketLossRate();
        double ping = avgPingMs;

        if (loss > 10 || ping > 300)
            return ConnectionQuality.POOR;
        if (loss > 5 || ping > 150)
            return ConnectionQuality.FAIR;
        if (loss > 2 || ping > 80)
            return ConnectionQuality.GOOD;
        return ConnectionQuality.EXCELLENT;
    }

    /**
     * 초기화
     */
    public void reset() {
        packetsSent = 0;
        packetsReceived = 0;
        packetsLost = 0;
        bytesSent = 0;
        bytesReceived = 0;
        currentPingMs = 0;
        avgPingMs = 0;
        maxPingMs = 0;
        minPingMs = Double.MAX_VALUE;
        uploadBandwidthKBps = 0;
        downloadBandwidthKBps = 0;
        lastBytesSent = 0;
        lastBytesReceived = 0;
        synchronized (pingHistory) {
            pingHistory.clear();
        }
        sessionStartTime = System.currentTimeMillis();
        lastUpdateTime = sessionStartTime;
    }

    /**
     * JSON 출력
     */
    public Map<String, Object> toMap() {
        Map<String, Object> map = new LinkedHashMap<>();

        // Ping
        Map<String, Object> ping = new LinkedHashMap<>();
        ping.put("current_ms", Math.round(currentPingMs * 10) / 10.0);
        ping.put("avg_ms", Math.round(avgPingMs * 10) / 10.0);
        ping.put("max_ms", Math.round(maxPingMs * 10) / 10.0);
        ping.put("min_ms", Math.round(getMinPingMs() * 10) / 10.0);
        map.put("ping", ping);

        // 패킷
        Map<String, Object> packets = new LinkedHashMap<>();
        packets.put("sent", packetsSent);
        packets.put("received", packetsReceived);
        packets.put("lost", packetsLost);
        packets.put("loss_rate_percent", Math.round(getPacketLossRate() * 100) / 100.0);
        map.put("packets", packets);

        // 대역폭
        Map<String, Object> bandwidth = new LinkedHashMap<>();
        bandwidth.put("upload_kbps", Math.round(uploadBandwidthKBps * 10) / 10.0);
        bandwidth.put("download_kbps", Math.round(downloadBandwidthKBps * 10) / 10.0);
        bandwidth.put("total_sent_kb", bytesSent / 1024);
        bandwidth.put("total_received_kb", bytesReceived / 1024);
        map.put("bandwidth", bandwidth);

        // 품질
        map.put("connection_quality", getConnectionQuality().name());
        map.put("session_duration_ms", getSessionDurationMs());

        return map;
    }
}
