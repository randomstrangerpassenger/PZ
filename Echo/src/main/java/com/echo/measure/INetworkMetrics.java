package com.echo.measure;

/**
 * 네트워크 메트릭 인터페이스.
 * 
 * @since Echo 1.0.1
 */
public interface INetworkMetrics {
    ConnectionQuality getConnectionQuality();

    double getPacketLossRate();

    double getAvgPingMs();
}
