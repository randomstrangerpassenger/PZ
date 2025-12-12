package com.pulse.network;

import com.pulse.api.log.PulseLogger;
import com.pulse.mod.ModLoader;
import com.pulse.mod.ModContainer;

import java.util.*;

/**
 * 핸드셰이크 핸들러.
 * 서버-클라이언트 모드 호환성 검증.
 */
public class HandshakeHandler {

    private static final String LOG = PulseLogger.PULSE;
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

        PulseLogger.info(LOG, "Handshake system initialized");
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
                PulseLogger.info(LOG, "Handshake accepted");
                break;
            case REJECT:
                PulseLogger.error(LOG, "Handshake rejected");
                break;
        }
    }

    private void handleClientRequest(HandshakePacket clientPacket, Object connection) {
        HandshakeResult result = validate(clientPacket.getModVersions());

        // SilentMode 콜백 - 클라이언트에 Pulse가 있는지 확인
        boolean clientHasPulse = clientPacket.getModVersions().containsKey("pulse");
        com.pulse.api.SilentMode.onHandshakeReceived(clientHasPulse);

        if (result.isSuccess()) {
            PulseLogger.info(LOG, "Client validated successfully");
            HandshakePacket response = HandshakePacket.create(HandshakePacket.HandshakePhase.ACCEPT);
            NetworkManager.sendToClient(connection, response);
        } else {
            PulseLogger.error(LOG, "Client validation failed: {}", result.getReason());
            HandshakePacket response = HandshakePacket.create(HandshakePacket.HandshakePhase.REJECT);
            NetworkManager.sendToClient(connection, response);

            // 연결 종료
            disconnectClient(connection, result.getReason());
        }
    }

    private void handleServerResponse(HandshakePacket serverPacket) {
        // SilentMode 콜백 - 서버에 Pulse가 있는지 확인
        boolean serverHasPulse = serverPacket.getModVersions().containsKey("pulse");
        com.pulse.api.SilentMode.onHandshakeReceived(serverHasPulse);

        // 클라이언트 측에서 서버 모드 확인
        HandshakeResult result = validate(serverPacket.getModVersions());

        if (!result.isSuccess()) {
            PulseLogger.error(LOG, "Server mod mismatch: {}", result.getReason());

            // 경고 표시 및 연결 종료
            showModMismatchWarning(result.getReason());
            disconnectFromServer(result.getReason());
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 연결 관리
    // ─────────────────────────────────────────────────────────────

    /**
     * 클라이언트 연결 종료 (서버 측).
     */
    private void disconnectClient(Object connection, String reason) {
        try {
            // GameServer.kick 또는 유사한 메서드 호출
            Class<?> gameServerClass = Class.forName("zombie.network.GameServer");

            // connection에서 플레이어/연결 정보 추출 시도
            if (connection != null) {
                java.lang.reflect.Method disconnectMethod = gameServerClass.getMethod("disconnect", Object.class,
                        String.class);
                disconnectMethod.invoke(null, connection, "Mod mismatch: " + reason);
                PulseLogger.info(LOG, "Client disconnected: {}", reason);
            }
        } catch (ClassNotFoundException e) {
            // GameServer 클래스 없음 - 싱글플레이어이거나 다른 환경
            PulseLogger.debug(LOG, "Cannot disconnect client (not a server environment)");
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to disconnect client: {}", e.getMessage());
        }
    }

    /**
     * 서버 연결 종료 (클라이언트 측).
     */
    private void disconnectFromServer(String reason) {
        try {
            Class<?> gameClientClass = Class.forName("zombie.network.GameClient");
            java.lang.reflect.Method disconnectMethod = gameClientClass.getMethod("disconnect");
            disconnectMethod.invoke(null);
            PulseLogger.info(LOG, "Disconnected from server: {}", reason);
        } catch (ClassNotFoundException e) {
            PulseLogger.debug(LOG, "Cannot disconnect (not a client environment)");
        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to disconnect from server: {}", e.getMessage());
        }
    }

    /**
     * 모드 불일치 경고 표시.
     */
    private void showModMismatchWarning(String reason) {
        // 콘솔에 경고 출력
        PulseLogger.error(LOG, "══════════════════════════════════════════════════════════");
        PulseLogger.error(LOG, "  [Pulse] MOD MISMATCH WARNING");
        PulseLogger.error(LOG, "══════════════════════════════════════════════════════════");
        PulseLogger.error(LOG, "  {}", reason);
        PulseLogger.error(LOG, "══════════════════════════════════════════════════════════");

        // UI 모달 표시 시도 (게임 UI 사용 가능한 경우)
        try {
            Class<?> luaManagerClass = Class.forName("zombie.Lua.LuaManager");
            java.lang.reflect.Method runLuaMethod = luaManagerClass.getMethod("RunLua", String.class);
            String luaCode = String.format(
                    "getCore():doPopup('[Pulse] Mod Mismatch', '%s')",
                    reason.replace("'", "\\'"));
            runLuaMethod.invoke(null, luaCode);
        } catch (Exception e) {
            // UI 팝업 실패 - 콘솔 경고만 표시됨
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
