package com.pulse.api.service.echo;

public interface INetworkMetrics {
    ConnectionQuality getConnectionQuality();

    double getPacketLossRate();

    double getAvgPingMs();
}
