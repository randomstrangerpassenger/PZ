package com.pulse.network;

import com.pulse.api.Pulse;
import com.pulse.mod.ModLoader;
import com.pulse.registry.Identifier;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 서버-클라이언트 핸드셰이크 패킷.
 * 연결 시 모드 목록과 버전을 교환하여 호환성 검증.
 */
public class HandshakePacket implements Packet {

    private static final Identifier ID = Identifier.of("pulse", "handshake");

    private String loaderVersion;
    private Map<String, String> modVersions; // modId -> version
    private HandshakePhase phase;

    public HandshakePacket() {
        this.modVersions = new LinkedHashMap<>();
        this.phase = HandshakePhase.REQUEST;
    }

    public HandshakePacket(HandshakePhase phase) {
        this();
        this.phase = phase;
    }

    /**
     * 현재 로드된 모드 정보로 패킷 생성.
     */
    public static HandshakePacket create(HandshakePhase phase) {
        HandshakePacket packet = new HandshakePacket(phase);
        packet.loaderVersion = Pulse.VERSION;

        // 로드된 모드 정보 수집
        ModLoader loader = ModLoader.getInstance();
        for (String modId : loader.getLoadedModIds()) {
            var container = loader.getMod(modId);
            if (container != null) {
                packet.modVersions.put(modId, container.getMetadata().getVersion());
            }
        }

        return packet;
    }

    @Override
    public Identifier getId() {
        return ID;
    }

    @Override
    public void write(PacketBuffer buf) {
        buf.writeByte(phase.ordinal());
        buf.writeString(loaderVersion);
        buf.writeInt(modVersions.size());
        for (var entry : modVersions.entrySet()) {
            buf.writeString(entry.getKey());
            buf.writeString(entry.getValue());
        }
    }

    @Override
    public void read(PacketBuffer buf) {
        phase = HandshakePhase.values()[buf.readByte()];
        loaderVersion = buf.readString();
        int count = buf.readInt();
        modVersions = new LinkedHashMap<>();
        for (int i = 0; i < count; i++) {
            String modId = buf.readString();
            String version = buf.readString();
            modVersions.put(modId, version);
        }
    }

    public String getLoaderVersion() {
        return loaderVersion;
    }

    public Map<String, String> getModVersions() {
        return modVersions;
    }

    public HandshakePhase getPhase() {
        return phase;
    }

    public enum HandshakePhase {
        REQUEST, // 클라이언트 → 서버 (모드 목록 요청 또는 전송)
        RESPONSE, // 서버 → 클라이언트 (서버 모드 목록)
        ACCEPT, // 핸드셰이크 성공
        REJECT // 핸드셰이크 실패
    }
}
