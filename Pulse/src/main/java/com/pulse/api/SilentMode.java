package com.pulse.api;

import com.pulse.api.log.PulseLogger;

/**
 * Silent Mode 관리자.
 * 리모트(서버/클라이언트)에 Pulse가 없을 때 네트워크 기능을 조용히 비활성화합니다.
 * 
 * <pre>
 * // 사용 예시 - 핸드셰이크 수신 시
 * SilentMode.onHandshakeReceived(remotHasPulse);
 * 
 * // 네트워크 패킷 전송 전 확인
 * if (!SilentMode.shouldSuppressNetworking()) {
 *     NetworkManager.send(packet);
 * }
 * </pre>
 * 
 * @since 1.1.0
 */
@PublicAPI(since = "1.1.0")
public final class SilentMode {

    private static final String LOG = PulseLogger.PULSE;
    private static volatile boolean enabled = false;
    private static volatile boolean remotePulseDetected = false;
    private static volatile boolean handshakeCompleted = false;

    private SilentMode() {
    } // 인스턴스화 방지

    // ═══════════════════════════════════════════════════════════════
    // 핸드셰이크 연동
    // ═══════════════════════════════════════════════════════════════

    /**
     * 핸드셰이크 수신 시 호출.
     * HandshakeHandler에서 자동 호출됨.
     * 
     * @param remoteHasPulse 리모트에 Pulse가 있으면 true
     */
    public static void onHandshakeReceived(boolean remoteHasPulse) {
        remotePulseDetected = remoteHasPulse;
        handshakeCompleted = true;

        if (!remoteHasPulse) {
            enabled = true;
            Pulse.log("pulse", "[SilentMode] Enabled - remote does not have Pulse");
        } else {
            enabled = false;
            Pulse.log("pulse", "[SilentMode] Disabled - remote has Pulse");
        }
    }

    /**
     * 핸드셰이크 리셋 (연결 종료 시).
     */
    public static void reset() {
        enabled = false;
        remotePulseDetected = false;
        handshakeCompleted = false;
    }

    // ═══════════════════════════════════════════════════════════════
    // 상태 조회
    // ═══════════════════════════════════════════════════════════════

    /**
     * 리모트에 Pulse가 있는지 확인.
     * 핸드셰이크 완료 전에는 false 반환.
     * 
     * @return 리모트에 Pulse가 있으면 true
     */
    public static boolean isRemotePulseEnabled() {
        return remotePulseDetected;
    }

    /**
     * Silent Mode가 활성화되어 있는지 확인.
     * 
     * @return 활성화되어 있으면 true
     */
    public static boolean isEnabled() {
        return enabled;
    }

    /**
     * 핸드셰이크가 완료되었는지 확인.
     * 
     * @return 완료되었으면 true
     */
    public static boolean isHandshakeCompleted() {
        return handshakeCompleted;
    }

    /**
     * Silent Mode 수동 설정.
     * 
     * @param state 활성화 여부
     */
    public static void setEnabled(boolean state) {
        enabled = state;
        if (state) {
            Pulse.log("pulse", "[SilentMode] Manually enabled");
        } else {
            Pulse.log("pulse", "[SilentMode] Manually disabled");
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // 네트워크 제어
    // ═══════════════════════════════════════════════════════════════

    /**
     * Pulse 네트워크 기능을 억제해야 하는지 확인.
     * Silent Mode가 활성화되어 있으면 true.
     * 
     * @return 네트워크 기능 억제 필요 시 true
     */
    public static boolean shouldSuppressNetworking() {
        return enabled;
    }

    /**
     * Pulse 패킷 전송 가능 여부 확인.
     * Silent Mode가 비활성화되어 있으면 true.
     * 
     * @return 패킷 전송 가능 시 true
     */
    public static boolean canSendPulsePackets() {
        return !enabled && handshakeCompleted && remotePulseDetected;
    }

    /**
     * 네트워크 기능 사용 전 체크.
     * Silent Mode면 경고 로그 남기고 false 반환.
     * 
     * @param feature 기능 이름 (로깅용)
     * @return 기능 사용 가능 시 true
     */
    public static boolean checkNetworkFeature(String feature) {
        if (enabled) {
            if (DevMode.isEnabled()) {
                Pulse.warn("pulse", "[SilentMode] Feature suppressed: " + feature);
            }
            return false;
        }
        return true;
    }

    // ═══════════════════════════════════════════════════════════════
    // 디버그
    // ═══════════════════════════════════════════════════════════════

    /**
     * 상태 정보 출력.
     */
    public static void printStatus() {
        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "  SilentMode Status");
        PulseLogger.info(LOG, "═══════════════════════════════════════");
        PulseLogger.info(LOG, "  Enabled: {}", enabled);
        PulseLogger.info(LOG, "  Remote Pulse: {}", remotePulseDetected);
        PulseLogger.info(LOG, "  Handshake Done: {}", handshakeCompleted);
        PulseLogger.info(LOG, "  Can Send Packets: {}", canSendPulsePackets());
        PulseLogger.info(LOG, "═══════════════════════════════════════");
    }
}
