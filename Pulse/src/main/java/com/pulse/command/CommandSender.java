package com.pulse.command;

/**
 * 명령 발신자 인터페이스.
 * 플레이어, 콘솔, 또는 기타 소스.
 */
import com.pulse.api.log.PulseLogger;

public interface CommandSender {
    String LOG = PulseLogger.PULSE;

    /**
     * 발신자 이름
     */
    String getName();

    /**
     * 메시지 전송
     */
    void sendMessage(String message);

    /**
     * 오류 메시지 전송
     */
    void sendError(String message);

    /**
     * 플레이어인지 확인
     */
    boolean isPlayer();

    /**
     * 서버/콘솔인지 확인
     */
    boolean isConsole();

    /**
     * 권한 확인
     */
    boolean hasPermission(String permission);

    /**
     * 플레이어 객체 (플레이어인 경우)
     */
    Object getPlayer();

    // ─────────────────────────────────────────────────────────────
    // 구현체
    // ─────────────────────────────────────────────────────────────

    /**
     * 콘솔 발신자
     */
    CommandSender CONSOLE = new CommandSender() {
        @Override
        public String getName() {
            return "Console";
        }

        @Override
        public void sendMessage(String message) {
            PulseLogger.info(LOG, "[CMD] {}", message);
        }

        @Override
        public void sendError(String message) {
            PulseLogger.error(LOG, "[CMD] ERROR: {}", message);
        }

        @Override
        public boolean isPlayer() {
            return false;
        }

        @Override
        public boolean isConsole() {
            return true;
        }

        @Override
        public boolean hasPermission(String permission) {
            return true;
        }

        @Override
        public Object getPlayer() {
            return null;
        }
    };
}
