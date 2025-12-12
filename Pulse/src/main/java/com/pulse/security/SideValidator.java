package com.pulse.security;

import com.pulse.api.log.PulseLogger;
import com.pulse.mod.ModContainer;
import com.pulse.mod.ModMetadata;

/**
 * 모드 사이드 검증.
 * 서버 전용/클라이언트 전용 모드 구분.
 */
public class SideValidator {

    /**
     * 현재 실행 환경.
     */
    public enum Side {
        CLIENT, // 클라이언트 (싱글 포함)
        SERVER, // 전용 서버
        BOTH // 양쪽 모두
    }

    private static Side currentSide = Side.CLIENT;
    private static final String LOG = PulseLogger.PULSE;

    /**
     * 현재 사이드 설정.
     */
    public static void setCurrentSide(Side side) {
        currentSide = side;
        PulseLogger.info(LOG, "[Side] Running on: {}", side);
    }

    /**
     * 현재 사이드 조회.
     */
    public static Side getCurrentSide() {
        return currentSide;
    }

    public static boolean isClient() {
        return currentSide == Side.CLIENT;
    }

    public static boolean isServer() {
        return currentSide == Side.SERVER;
    }

    /**
     * 모드가 현재 사이드에서 로드 가능한지 확인.
     */
    public static boolean canLoad(ModContainer mod) {
        ModMetadata meta = mod.getMetadata();
        ModSide modSide = getModSide(meta);

        switch (modSide) {
            case CLIENT_ONLY:
                return currentSide == Side.CLIENT;
            case SERVER_ONLY:
                return currentSide == Side.SERVER;
            case BOTH:
            default:
                return true;
        }
    }

    /**
     * 모드 메타데이터에서 사이드 정보 추출.
     */
    private static ModSide getModSide(ModMetadata meta) {
        // 권한 목록에서 사이드 힌트 확인
        for (String perm : meta.getPermissions()) {
            if ("client_only".equalsIgnoreCase(perm)) {
                return ModSide.CLIENT_ONLY;
            }
            if ("server_only".equalsIgnoreCase(perm)) {
                return ModSide.SERVER_ONLY;
            }
        }
        return ModSide.BOTH;
    }

    /**
     * 모드가 잘못된 사이드에서 실행 시 경고.
     */
    public static void warnIfWrongSide(String modId, ModSide requiredSide) {
        boolean valid = true;

        switch (requiredSide) {
            case CLIENT_ONLY:
                valid = currentSide == Side.CLIENT;
                break;
            case SERVER_ONLY:
                valid = currentSide == Side.SERVER;
                break;
            default:
                break;
        }

        if (!valid) {
            PulseLogger.warn(LOG, "[Side] WARNING: Mod '{}' requires {} but running on {}",
                    modId, requiredSide, currentSide);
        }
    }

    public enum ModSide {
        CLIENT_ONLY,
        SERVER_ONLY,
        BOTH
    }
}
