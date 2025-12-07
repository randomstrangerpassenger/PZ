package com.pulse.network;

import com.pulse.mod.ModLoader;
import com.pulse.mod.ModContainer;

import java.util.*;

/**
 * 핸드셰이크 핸들러.
 * 서버-클라이언트 모드 호환성 검증.
 */
public class HandshakeHandler {

    private static final HandshakeHandler INSTANCE = new HandshakeHandler();

    // 필수 모드 목록 (이 모드들은 클라이언트와 서버 모두에 있어야 함)
    private final Set<String> requiredMods = new HashSet<>();

    // 검증 모드
    private ValidationMode validationMode = ValidationMode.STRICT;

    private HandshakeHandler() {
    }

    public static HandshakeHandler getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 검증
    // ─────────────────────────────────────────────────────────────

    /**
     * 클라이언트 모드 목록 검증 (서버 측).
     * 
     * @param clientMods 클라이언트의 modId -> version 맵
     * @return 검증 결과
     */
    public static HandshakeResult validate(Map<String, String> clientMods) {
        return INSTANCE.validateInternal(clientMods);
    }

    private HandshakeResult validateInternal(Map<String, String> clientMods) {
        List<String> missingOnClient = new ArrayList<>();
        List<String> missingOnServer = new ArrayList<>();
        List<String> versionMismatch = new ArrayList<>();

        ModLoader loader = ModLoader.getInstance();
        Map<String, String> serverMods = new HashMap<>();

        for (String modId : loader.getLoadedModIds()) {
            ModContainer container = loader.getMod(modId);
            if (container != null) {
                serverMods.put(modId, container.getMetadata().getVersion());
            }
        }

        // 1. 서버 모드가 클라이언트에 있는지 확인
        for (var entry : serverMods.entrySet()) {
            String modId = entry.getKey();
            String serverVersion = entry.getValue();

            if (!clientMods.containsKey(modId)) {
                if (isRequired(modId)) {
                    missingOnClient.add(modId);
                }
            } else {
                String clientVersion = clientMods.get(modId);
                if (!serverVersion.equals(clientVersion)) {
                    versionMismatch.add(modId + " (server: " + serverVersion +
                            ", client: " + clientVersion + ")");
                }
            }
        }

        // 2. 클라이언트 모드가 서버에 있는지 확인
        for (String modId : clientMods.keySet()) {
            if (!serverMods.containsKey(modId) && isRequired(modId)) {
                missingOnServer.add(modId);
            }
        }

        // 결과 생성
        if (missingOnClient.isEmpty() && missingOnServer.isEmpty() &&
                (versionMismatch.isEmpty() || validationMode == ValidationMode.LENIENT)) {
            return HandshakeResult.success();
        }

        StringBuilder reason = new StringBuilder();
        if (!missingOnClient.isEmpty()) {
            reason.append("Missing on client: ").append(missingOnClient).append(". ");
        }
        if (!missingOnServer.isEmpty()) {
            reason.append("Missing on server: ").append(missingOnServer).append(". ");
        }
        if (!versionMismatch.isEmpty() && validationMode == ValidationMode.STRICT) {
            reason.append("Version mismatch: ").append(versionMismatch);
        }

        return HandshakeResult.failure(reason.toString().trim());
    }

    private boolean isRequired(String modId) {
        // pulse_ 로 시작하는 것은 필수 (핵심 모드)
        if (modId.startsWith("pulse_") || modId.equals("pulse")) {
            return true;
        }
        return requiredMods.contains(modId);
    }

    // ─────────────────────────────────────────────────────────────
    // 설정
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드를 필수로 지정.
     */
    public static void markRequired(String modId) {
        INSTANCE.requiredMods.add(modId);
    }

    /**
     * 검증 모드 설정.
     */
    public static void setValidationMode(ValidationMode mode) {
        INSTANCE.validationMode = mode;
    }

    // ─────────────────────────────────────────────────────────────
    // 패킷 핸들러 등록
    // ─────────────────────────────────────────────────────────────

    /**
     * 핸드셰이크 시스템 초기화.
     */
    public static void initialize() {
        // 패킷 등록
        NetworkManager.registerPacket(
                HandshakePacket.class,
                HandshakePacket::new,
                NetworkSide.BOTH);

        // 핸들러 등록
        NetworkManager.registerHandler(HandshakePacket.class, INSTANCE::handlePacket);

        System.out.println("[Pulse/Handshake] Initialized");
    }

    private void handlePacket(HandshakePacket packet, Object sender) {
        switch (packet.getPhase()) {
            case REQUEST:
                // 클라이언트 요청 처리 (서버 측)
                handleClientRequest(packet, sender);
                break;
            case RESPONSE:
                // 서버 응답 처리 (클라이언트 측)
                handleServerResponse(packet);
                break;
            case ACCEPT:
                System.out.println("[Pulse/Handshake] Handshake accepted");
                break;
            case REJECT:
                System.err.println("[Pulse/Handshake] Handshake rejected");
                break;
        }
    }

    private void handleClientRequest(HandshakePacket clientPacket, Object connection) {
        HandshakeResult result = validate(clientPacket.getModVersions());

        if (result.isSuccess()) {
            System.out.println("[Pulse/Handshake] Client validated successfully");
            HandshakePacket response = HandshakePacket.create(HandshakePacket.HandshakePhase.ACCEPT);
            NetworkManager.sendToClient(connection, response);
        } else {
            System.err.println("[Pulse/Handshake] Client validation failed: " + result.getReason());
            HandshakePacket response = HandshakePacket.create(HandshakePacket.HandshakePhase.REJECT);
            NetworkManager.sendToClient(connection, response);
            // TODO: 연결 종료
        }
    }

    private void handleServerResponse(HandshakePacket serverPacket) {
        // 클라이언트 측에서 서버 모드 확인
        HandshakeResult result = validate(serverPacket.getModVersions());

        if (!result.isSuccess()) {
            System.err.println("[Pulse/Handshake] Server mod mismatch: " + result.getReason());
            // TODO: 경고 표시 또는 연결 종료
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 결과 클래스
    // ─────────────────────────────────────────────────────────────

    public static class HandshakeResult {
        private final boolean success;
        private final String reason;

        private HandshakeResult(boolean success, String reason) {
            this.success = success;
            this.reason = reason;
        }

        public static HandshakeResult success() {
            return new HandshakeResult(true, null);
        }

        public static HandshakeResult failure(String reason) {
            return new HandshakeResult(false, reason);
        }

        public boolean isSuccess() {
            return success;
        }

        public String getReason() {
            return reason;
        }
    }

    public enum ValidationMode {
        STRICT, // 버전까지 일치 필요
        LENIENT // 모드 존재만 확인
    }
}
