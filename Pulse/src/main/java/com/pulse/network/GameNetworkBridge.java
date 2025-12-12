package com.pulse.network;

import com.pulse.api.log.PulseLogger;

import java.lang.reflect.Method;
import java.nio.ByteBuffer;

/**
 * 게임 네트워크 시스템 브릿지.
 * Project Zomboid의 네트워크 시스템에 연결하여 실제 패킷 전송을 수행.
 * 
 * Refactored: Uses NetworkAccess for reflection and NetworkPacketStats for
 * metrics.
 */
public class GameNetworkBridge {

    private static final String LOG = PulseLogger.PULSE;
    private static final GameNetworkBridge INSTANCE = new GameNetworkBridge();

    // Pulse 커스텀 패킷 채널 ID
    private static final short Pulse_PACKET_ID = (short) 0x4D55; // "MU" in hex

    private final NetworkAccess access = new NetworkAccess();
    private final NetworkPacketStats stats = new NetworkPacketStats();

    private boolean debugMode = false;

    private GameNetworkBridge() {
    }

    public static GameNetworkBridge getInstance() {
        return INSTANCE;
    }

    /**
     * 네트워크 브릿지 초기화.
     */
    public void initialize() {
        access.initialize();
    }

    /**
     * 서버로 패킷 전송 (클라이언트에서 호출)
     */
    public boolean sendToServer(byte[] data) {
        if (!access.isInitialized()) {
            initialize();
        }

        if (access.getGameClientClass() == null) {
            if (debugMode) {
                PulseLogger.warn(LOG, "Cannot send to server: GameClient not available");
            }
            return false;
        }

        try {
            Object writer = access.createByteBufferWriter();
            if (writer == null) {
                return sendRawPacket(data, null);
            }

            // Write packet
            access.writeShort(writer, Pulse_PACKET_ID);
            access.writeInt(writer, data.length);
            access.writeBytes(writer, data);

            // Send
            Method sendMethod = access.getClientSendMethod();
            if (sendMethod != null) {
                sendMethod.invoke(null, writer);
                if (debugMode) {
                    PulseLogger.debug(LOG, "Sent {} bytes to server", data.length);
                }
                stats.recordSent(data.length);
                return true;
            }

            return sendRawPacket(data, null);

        } catch (Exception e) {
            PulseLogger.error(LOG, "Error sending to server: {}", e.getMessage());
            if (debugMode) {
                e.printStackTrace();
            }
            return false;
        }
    }

    /**
     * 특정 클라이언트로 패킷 전송 (서버에서 호출)
     */
    public boolean sendToClient(Object connection, byte[] data) {
        if (!access.isInitialized()) {
            initialize();
        }

        if (access.getGameServerClass() == null) {
            if (debugMode) {
                PulseLogger.warn(LOG, "Cannot send to client: GameServer not available");
            }
            return false;
        }

        try {
            Object writer = access.createByteBufferWriter();
            if (writer == null) {
                return sendRawPacket(data, connection);
            }

            // Write packet
            access.writeShort(writer, Pulse_PACKET_ID);
            access.writeInt(writer, data.length);
            access.writeBytes(writer, data);

            // Send via UdpConnection
            if (connection != null && access.isUdpConnection(connection)) {
                Method sendMethod = access.getUdpSendMethod();
                if (sendMethod != null) {
                    sendMethod.invoke(connection, writer);
                    if (debugMode) {
                        PulseLogger.debug(LOG, "Sent {} bytes to client", data.length);
                    }
                    stats.recordSent(data.length);
                    return true;
                }
            }

            return sendRawPacket(data, connection);

        } catch (Exception e) {
            PulseLogger.error(LOG, "Error sending to client: {}", e.getMessage());
            if (debugMode) {
                e.printStackTrace();
            }
            return false;
        }
    }

    /**
     * 모든 클라이언트로 패킷 전송 (서버에서 호출)
     */
    public boolean sendToAll(byte[] data) {
        if (!access.isInitialized()) {
            initialize();
        }

        if (access.getGameServerClass() == null) {
            if (debugMode) {
                PulseLogger.warn(LOG, "Cannot send to all: GameServer not available");
            }
            return false;
        }

        try {
            Object connections = access.getUdpEngine();

            if (connections == null) {
                if (debugMode) {
                    PulseLogger.debug(LOG, "No connections found, cannot broadcast");
                }
                return false;
            }

            // connections가 iterable인 경우 순회
            if (connections instanceof Iterable<?>) {
                int sent = 0;
                for (Object connection : (Iterable<?>) connections) {
                    if (sendToClient(connection, data)) {
                        sent++;
                    }
                }
                if (debugMode) {
                    PulseLogger.debug(LOG, "Broadcast to {} clients", sent);
                }
                return sent > 0;
            }

            return false;

        } catch (Exception e) {
            PulseLogger.error(LOG, "Error broadcasting: {}", e.getMessage());
            if (debugMode) {
                e.printStackTrace();
            }
            return false;
        }
    }

    /**
     * 수신된 패킷 처리.
     */
    public void handleReceived(ByteBuffer buffer, Object sender) {
        try {
            // Pulse 패킷 ID 확인
            short packetId = buffer.getShort();
            if (packetId != Pulse_PACKET_ID) {
                // Pulse 패킷이 아님 - 무시
                return;
            }

            // 데이터 길이 읽기
            int length = buffer.getInt();

            // 데이터 읽기
            byte[] data = new byte[length];
            buffer.get(data);

            // NetworkManager에 전달
            NetworkManager.getInstance().handleReceived(data, sender);

            if (debugMode) {
                PulseLogger.debug(LOG, "Received {} bytes", length);
            }
            stats.recordReceived(length);

        } catch (Exception e) {
            PulseLogger.error(LOG, "Error handling received packet: {}", e.getMessage());
            if (debugMode) {
                e.printStackTrace();
            }
        }
    }

    private boolean sendRawPacket(byte[] data, Object target) {
        if (debugMode) {
            PulseLogger.debug(LOG, "Raw packet send not implemented ({} bytes)", data.length);
        }
        return false;
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    public boolean isClient() {
        return access.getGameClientClass() != null && com.pulse.api.access.NetworkAccess.isSinglePlayer() == false;
    }

    public boolean isServer() {
        return access.getGameServerClass() != null && !com.pulse.api.access.NetworkAccess.isSinglePlayer();
    }

    public boolean isInitialized() {
        return access.isInitialized();
    }

    public void setDebugMode(boolean debug) {
        this.debugMode = debug;
    }

    public static short getPulsePacketId() {
        return Pulse_PACKET_ID;
    }

    public NetworkPacketStats getStats() {
        return stats;
    }

    // Legacy delegates for stats (optional, but good for backward compat if needed)
    public int getSentPacketCount() {
        return stats.getSentPacketCount();
    }

    public int getReceivedPacketCount() {
        return stats.getReceivedPacketCount();
    }

    public long getTotalBytesSent() {
        return stats.getTotalBytesSent();
    }

    public long getTotalBytesReceived() {
        return stats.getTotalBytesReceived();
    }

    public void resetStatistics() {
        stats.reset();
    }

    public String getStatisticsReport() {
        return stats.getReport();
    }

    public void reconnect() {
        // Not easily supported with final fields, but we can re-initialize access?
        // Actually access can just try reloading.
        // For now, simple re-init.
        access.initialize();
        PulseLogger.info(LOG, "Network Access re-initialized");
    }
}
