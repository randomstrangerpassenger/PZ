package com.pulse.network;

import com.pulse.PulseEnvironment;
import com.pulse.access.AccessWidener;
import com.pulse.api.GameAccess;

import java.lang.reflect.Method;
import java.nio.ByteBuffer;

/**
 * 게임 네트워크 시스템 브릿지.
 * Project Zomboid의 네트워크 시스템에 연결하여 실제 패킷 전송을 수행.
 * 
 * 게임 네트워크 클래스:
 * - zombie.network.GameClient: 클라이언트 측 네트워킹
 * - zombie.network.GameServer: 서버 측 네트워킹
 * - zombie.core.network.ByteBufferWriter: 바이트 버퍼 쓰기
 */
public class GameNetworkBridge {

    private static final GameNetworkBridge INSTANCE = new GameNetworkBridge();

    // 게임 네트워크 클래스 캐시
    private Class<?> gameClientClass;
    private Class<?> gameServerClass;
    private Class<?> byteBufferWriterClass;
    private Class<?> udpConnectionClass;

    // Pulse 커스텀 패킷 채널 ID
    private static final short Pulse_PACKET_ID = (short) 0x4D55; // "MU" in hex

    private boolean initialized = false;
    private boolean debugMode = false;

    private GameNetworkBridge() {
    }

    public static GameNetworkBridge getInstance() {
        return INSTANCE;
    }

    /**
     * 네트워크 브릿지 초기화.
     * 게임 클래스 로더가 활성화된 후에 호출되어야 함.
     */
    public void initialize() {
        if (initialized)
            return;

        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null) {
                loader = ClassLoader.getSystemClassLoader();
            }

            // 게임 클래스 로드 시도
            try {
                gameClientClass = loader.loadClass("zombie.network.GameClient");
                System.out.println("[Pulse/Network] GameClient class loaded");
            } catch (ClassNotFoundException e) {
                System.out.println("[Pulse/Network] GameClient class not found (may be server-only)");
            }

            try {
                gameServerClass = loader.loadClass("zombie.network.GameServer");
                System.out.println("[Pulse/Network] GameServer class loaded");
            } catch (ClassNotFoundException e) {
                System.out.println("[Pulse/Network] GameServer class not found (may be client-only)");
            }

            try {
                byteBufferWriterClass = loader.loadClass("zombie.core.network.ByteBufferWriter");
                System.out.println("[Pulse/Network] ByteBufferWriter class loaded");
            } catch (ClassNotFoundException e) {
                System.out.println("[Pulse/Network] ByteBufferWriter class not found");
            }

            try {
                udpConnectionClass = loader.loadClass("zombie.network.UdpConnection");
                System.out.println("[Pulse/Network] UdpConnection class loaded");
            } catch (ClassNotFoundException e) {
                System.out.println("[Pulse/Network] UdpConnection class not found");
            }

            initialized = true;
            System.out.println("[Pulse/Network] Network bridge initialized");

        } catch (Exception e) {
            System.err.println("[Pulse/Network] Failed to initialize network bridge: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 서버로 패킷 전송 (클라이언트에서 호출)
     */
    public boolean sendToServer(byte[] data) {
        if (!initialized) {
            initialize();
        }

        if (gameClientClass == null) {
            if (debugMode) {
                System.err.println("[Pulse/Network] Cannot send to server: GameClient not available");
            }
            return false;
        }

        try {
            // 방법 1: GameClient의 sendData 메서드 사용 시도
            // zombie.network.GameClient.sendData(ByteBufferWriter)

            // ByteBufferWriter 생성
            Object writer = createByteBufferWriter();
            if (writer == null) {
                return sendRawPacket(data, null);
            }

            // Pulse 패킷 ID 쓰기
            writeShort(writer, Pulse_PACKET_ID);

            // 데이터 길이 쓰기
            writeInt(writer, data.length);

            // 데이터 쓰기
            writeBytes(writer, data);

            // 전송
            Method sendMethod = findSendMethod(gameClientClass);
            if (sendMethod != null) {
                sendMethod.invoke(null, writer);
                if (debugMode) {
                    System.out.println("[Pulse/Network] Sent " + data.length + " bytes to server");
                }
                return true;
            }

            return sendRawPacket(data, null);

        } catch (Exception e) {
            System.err.println("[Pulse/Network] Error sending to server: " + e.getMessage());
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
        if (!initialized) {
            initialize();
        }

        if (gameServerClass == null) {
            if (debugMode) {
                System.err.println("[Pulse/Network] Cannot send to client: GameServer not available");
            }
            return false;
        }

        try {
            Object writer = createByteBufferWriter();
            if (writer == null) {
                return sendRawPacket(data, connection);
            }

            // Pulse 패킷 ID 쓰기
            writeShort(writer, Pulse_PACKET_ID);

            // 데이터 길이 쓰기
            writeInt(writer, data.length);

            // 데이터 쓰기
            writeBytes(writer, data);

            // UdpConnection을 통해 전송
            if (connection != null && udpConnectionClass != null &&
                    udpConnectionClass.isInstance(connection)) {
                Method sendMethod = findUdpSendMethod();
                if (sendMethod != null) {
                    sendMethod.invoke(connection, writer);
                    if (debugMode) {
                        System.out.println("[Pulse/Network] Sent " + data.length + " bytes to client");
                    }
                    return true;
                }
            }

            return sendRawPacket(data, connection);

        } catch (Exception e) {
            System.err.println("[Pulse/Network] Error sending to client: " + e.getMessage());
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
        if (!initialized) {
            initialize();
        }

        if (gameServerClass == null) {
            if (debugMode) {
                System.err.println("[Pulse/Network] Cannot send to all: GameServer not available");
            }
            return false;
        }

        try {
            // 모든 연결된 클라이언트 가져오기
            Object connections = AccessWidener.getStaticField(gameServerClass, "udpEngine");
            if (connections == null) {
                connections = AccessWidener.getStaticField(gameServerClass, "connections");
            }

            if (connections == null) {
                if (debugMode) {
                    System.out.println("[Pulse/Network] No connections found, cannot broadcast");
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
                    System.out.println("[Pulse/Network] Broadcast to " + sent + " clients");
                }
                return sent > 0;
            }

            return false;

        } catch (Exception e) {
            System.err.println("[Pulse/Network] Error broadcasting: " + e.getMessage());
            if (debugMode) {
                e.printStackTrace();
            }
            return false;
        }
    }

    /**
     * 수신된 패킷 처리.
     * 게임의 패킷 핸들러에서 호출되어야 함.
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
                System.out.println("[Pulse/Network] Received " + length + " bytes");
            }

        } catch (Exception e) {
            System.err.println("[Pulse/Network] Error handling received packet: " + e.getMessage());
            if (debugMode) {
                e.printStackTrace();
            }
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 헬퍼 메서드
    // ─────────────────────────────────────────────────────────────

    private Object createByteBufferWriter() {
        if (byteBufferWriterClass == null) {
            return null;
        }
        return AccessWidener.newInstance(byteBufferWriterClass);
    }

    private void writeShort(Object writer, short value) {
        AccessWidener.invoke(writer, "putShort", value);
    }

    private void writeInt(Object writer, int value) {
        AccessWidener.invoke(writer, "putInt", value);
    }

    private void writeBytes(Object writer, byte[] data) {
        AccessWidener.invoke(writer, "putBytes", data);
    }

    private Method findSendMethod(Class<?> clazz) {
        try {
            // 일반적인 send 메서드 패턴 찾기
            for (Method method : clazz.getDeclaredMethods()) {
                String name = method.getName().toLowerCase();
                if ((name.contains("send") || name.contains("write")) &&
                        method.getParameterCount() == 1 &&
                        byteBufferWriterClass != null &&
                        byteBufferWriterClass.isAssignableFrom(method.getParameterTypes()[0])) {
                    method.setAccessible(true);
                    return method;
                }
            }
        } catch (Exception e) {
            // 무시
        }
        return null;
    }

    private Method findUdpSendMethod() {
        if (udpConnectionClass == null)
            return null;
        try {
            for (Method method : udpConnectionClass.getDeclaredMethods()) {
                String name = method.getName().toLowerCase();
                if (name.contains("send") && method.getParameterCount() == 1) {
                    method.setAccessible(true);
                    return method;
                }
            }
        } catch (Exception e) {
            // 무시
        }
        return null;
    }

    /**
     * 폴백: 원시 바이트 배열 직접 전송 시도
     */
    private boolean sendRawPacket(byte[] data, Object target) {
        // 게임 네트워크 API를 직접 찾을 수 없는 경우
        // 이 메서드는 게임별 커스터마이징이 필요함
        if (debugMode) {
            System.out.println("[Pulse/Network] Raw packet send not implemented (" +
                    data.length + " bytes)");
        }
        return false;
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    public boolean isClient() {
        return gameClientClass != null && GameAccess.isSinglePlayer() == false;
    }

    public boolean isServer() {
        return gameServerClass != null && !GameAccess.isSinglePlayer();
    }

    public boolean isInitialized() {
        return initialized;
    }

    public void setDebugMode(boolean debug) {
        this.debugMode = debug;
    }

    /**
     * Pulse 패킷 ID 반환 (Mixin에서 패킷 타입 확인용)
     */
    public static short getPulsePacketId() {
        return Pulse_PACKET_ID;
    }
}
