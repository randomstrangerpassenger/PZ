package com.mutagen.network;

import com.mutagen.registry.Identifier;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/**
 * 네트워크 매니저.
 * 패킷 등록, 전송, 수신을 관리.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 패킷 등록
 * NetworkManager.registerPacket(MyPacket.class, MyPacket::new, NetworkSide.SERVER);
 * 
 * // 패킷 핸들러 등록
 * NetworkManager.registerHandler(MyPacket.class, (packet, sender) -> {
 *     System.out.println("Received: " + packet.getMessage());
 * });
 * 
 * // 패킷 송신
 * NetworkManager.sendToServer(new MyPacket("Hello!"));
 * </pre>
 */
public class NetworkManager {

    private static final NetworkManager INSTANCE = new NetworkManager();

    // 등록된 패킷 타입
    private final Map<Identifier, PacketRegistration<?>> packetsByType = new ConcurrentHashMap<>();
    private final Map<Class<?>, PacketRegistration<?>> packetsByClass = new ConcurrentHashMap<>();

    private NetworkManager() {
    }

    public static NetworkManager getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 패킷 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * 패킷 타입 등록
     */
    public static <T extends Packet> void registerPacket(
            Class<T> packetClass,
            Supplier<T> factory,
            NetworkSide side) {
        INSTANCE.register(packetClass, factory, side);
    }

    /**
     * 패킷 핸들러 등록
     */
    public static <T extends Packet> void registerHandler(
            Class<T> packetClass,
            PacketHandler<T> handler) {
        INSTANCE.addHandler(packetClass, handler);
    }

    private <T extends Packet> void register(
            Class<T> packetClass,
            Supplier<T> factory,
            NetworkSide side) {

        // 임시 인스턴스로 ID 확인
        T temp = factory.get();
        Identifier id = temp.getId();

        PacketRegistration<T> registration = new PacketRegistration<>(
                id, packetClass, factory, side);

        packetsByType.put(id, registration);
        packetsByClass.put(packetClass, registration);

        System.out.println("[Mutagen/Network] Registered packet: " + id +
                " (" + side + ")");
    }

    @SuppressWarnings("unchecked")
    private <T extends Packet> void addHandler(Class<T> packetClass, PacketHandler<T> handler) {
        PacketRegistration<T> reg = (PacketRegistration<T>) packetsByClass.get(packetClass);
        if (reg != null) {
            reg.addHandler(handler);
        } else {
            System.err.println("[Mutagen/Network] Cannot add handler: packet not registered");
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 패킷 송신 (게임 네트워킹에 연결 필요)
    // ─────────────────────────────────────────────────────────────

    /**
     * 서버로 패킷 전송 (클라이언트에서 호출)
     */
    public static void sendToServer(Packet packet) {
        byte[] data = INSTANCE.serialize(packet);
        // TODO: 게임 네트워크 시스템에 연결
        System.out.println("[Mutagen/Network] Would send to server: " +
                packet.getId() + " (" + data.length + " bytes)");
    }

    /**
     * 클라이언트로 패킷 전송 (서버에서 호출)
     */
    public static void sendToClient(Object player, Packet packet) {
        byte[] data = INSTANCE.serialize(packet);
        // TODO: 게임 네트워크 시스템에 연결
        System.out.println("[Mutagen/Network] Would send to client: " +
                packet.getId() + " (" + data.length + " bytes)");
    }

    /**
     * 모든 클라이언트로 패킷 전송
     */
    public static void sendToAll(Packet packet) {
        byte[] data = INSTANCE.serialize(packet);
        // TODO: 게임 네트워크 시스템에 연결
        System.out.println("[Mutagen/Network] Would send to all: " +
                packet.getId() + " (" + data.length + " bytes)");
    }

    // ─────────────────────────────────────────────────────────────
    // 직렬화/역직렬화
    // ─────────────────────────────────────────────────────────────

    /**
     * 패킷 직렬화
     */
    public byte[] serialize(Packet packet) {
        PacketBuffer buf = new PacketBuffer();

        // 패킷 ID 쓰기
        buf.writeString(packet.getId().toString());

        // 패킷 데이터 쓰기
        packet.write(buf);

        return buf.toByteArray();
    }

    /**
     * 패킷 역직렬화
     */
    @SuppressWarnings("unchecked")
    public <T extends Packet> T deserialize(byte[] data) {
        PacketBuffer buf = new PacketBuffer(data);

        // 패킷 ID 읽기
        String idStr = buf.readString();
        Identifier id = Identifier.parse(idStr);

        // 패킷 타입 찾기
        PacketRegistration<T> reg = (PacketRegistration<T>) packetsByType.get(id);
        if (reg == null) {
            System.err.println("[Mutagen/Network] Unknown packet: " + id);
            return null;
        }

        // 패킷 인스턴스 생성 및 데이터 읽기
        T packet = reg.create();
        packet.read(buf);

        return packet;
    }

    /**
     * 수신된 패킷 처리
     */
    @SuppressWarnings("unchecked")
    public void handleReceived(byte[] data, Object sender) {
        PacketBuffer buf = new PacketBuffer(data);

        String idStr = buf.readString();
        Identifier id = Identifier.parse(idStr);

        PacketRegistration<?> reg = packetsByType.get(id);
        if (reg == null) {
            System.err.println("[Mutagen/Network] Unknown packet: " + id);
            return;
        }

        Packet packet = reg.create();
        packet.read(buf);

        // 핸들러 호출
        ((PacketRegistration<Packet>) reg).handlePacket(packet, sender);
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    @FunctionalInterface
    public interface PacketHandler<T extends Packet> {
        void handle(T packet, Object sender);
    }

    @SuppressWarnings("unused") // Public API for future game integration
    private static class PacketRegistration<T extends Packet> {
        final Identifier id;
        final Class<T> packetClass;
        final Supplier<T> factory;
        final NetworkSide side;
        final List<PacketHandler<T>> handlers = new ArrayList<>();

        PacketRegistration(Identifier id, Class<T> packetClass,
                Supplier<T> factory, NetworkSide side) {
            this.id = id;
            this.packetClass = packetClass;
            this.factory = factory;
            this.side = side;
        }

        T create() {
            return factory.get();
        }

        Class<T> getPacketClass() {
            return packetClass;
        }

        NetworkSide getSide() {
            return side;
        }

        void addHandler(PacketHandler<T> handler) {
            handlers.add(handler);
        }

        void handlePacket(T packet, Object sender) {
            for (PacketHandler<T> handler : handlers) {
                try {
                    handler.handle(packet, sender);
                } catch (Exception e) {
                    System.err.println("[Mutagen/Network] Handler error for " + id);
                    e.printStackTrace();
                }
            }
        }
    }
}
