package com.pulse.api.spi;

import java.util.Map;

/**
 * 네트워크 프로바이더 인터페이스.
 * Nerve와 같은 네트워크 모드가 구현.
 * 
 * 이 인터페이스는 Lua 모드와 Pulse 모드 모두 구현 가능.
 * Lua 모드는 브릿지를 통해 호출됨.
 */
public interface INetworkProvider extends IProvider {

    /**
     * 서버 연결 상태
     */
    boolean isConnected();

    /**
     * 현재 핑 (밀리초)
     */
    int getPingMs();

    /**
     * 평균 핑 (밀리초)
     */
    int getAveragePingMs();

    /**
     * 패킷 손실률 (%)
     */
    double getPacketLossPercent();

    /**
     * 송신 대역폭 (bytes/sec)
     */
    long getOutboundBandwidth();

    /**
     * 수신 대역폭 (bytes/sec)
     */
    long getInboundBandwidth();

    /**
     * 총 송신 바이트
     */
    long getTotalBytesSent();

    /**
     * 총 수신 바이트
     */
    long getTotalBytesReceived();

    /**
     * 패킷 타입별 통계
     * 
     * @return 패킷 타입 → 전송 횟수
     */
    Map<String, Long> getPacketStats();

    /**
     * 네트워크 통계 리셋
     */
    void resetStats();

    /**
     * 네트워크 품질 등급 (0=나쁨, 1=보통, 2=좋음)
     */
    default int getNetworkQuality() {
        int ping = getPingMs();
        double loss = getPacketLossPercent();

        if (ping < 50 && loss < 1.0)
            return 2; // 좋음
        if (ping < 150 && loss < 5.0)
            return 1; // 보통
        return 0; // 나쁨
    }
}
