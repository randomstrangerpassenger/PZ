package com.echo.ui;

/**
 * Echo UI 색상 테마
 * 
 * 부드러운 색상 팔레트를 사용하여 눈의 피로를 줄입니다.
 */
public final class EchoTheme {

    private EchoTheme() {
        // Utility class
    }

    // --- Status Colors ---

    /** 양호 상태 (청록) - FPS ≥55, Frame Time ≤16.67ms */
    public static final int GOOD = 0x4ECDC4;

    /** 경고 상태 (연한 노랑) - FPS ≥30, Frame Time ≤33.33ms */
    public static final int WARNING = 0xFFE66D;

    /** 위험 상태 (연한 빨강) - FPS <30, Frame Time >33.33ms */
    public static final int CRITICAL = 0xFF6B6B;

    // --- Base Colors ---

    /** 기본 텍스트 색상 (흰색) */
    public static final int TEXT = 0xFFFFFF;

    /** 보조 텍스트 색상 (연한 회색) */
    public static final int TEXT_SECONDARY = 0xAAAAAA;

    /** 강조 텍스트 색상 (밝은 청록) */
    public static final int TEXT_HIGHLIGHT = 0x7FDBDA;

    /** 배경 색상 (검정, Alpha 별도 적용) */
    public static final int BACKGROUND = 0x000000;

    /** 배경 불투명도 (80%) */
    public static final int BG_ALPHA = 0xCC;

    /** 패널 테두리 색상 */
    public static final int BORDER = 0x555555;

    // --- Subsystem Colors ---

    /** 렌더링 시스템 색상 */
    public static final int SUBSYSTEM_RENDER = 0x6C5CE7;

    /** AI 시스템 색상 */
    public static final int SUBSYSTEM_AI = 0xE17055;

    /** 물리 시스템 색상 */
    public static final int SUBSYSTEM_PHYSICS = 0x00B894;

    /** 네트워크 시스템 색상 */
    public static final int SUBSYSTEM_NETWORK = 0x0984E3;

    /** Lua 시스템 색상 */
    public static final int SUBSYSTEM_LUA = 0xFDCB6E;

    /** 조명 시스템 색상 */
    public static final int SUBSYSTEM_LIGHTING = 0xF39C12;

    /** 기타 시스템 색상 */
    public static final int SUBSYSTEM_OTHER = 0x95A5A6;

    // --- Utility ---

    /**
     * 등급에 따른 색상 반환
     * 
     * @param grade 0=Good, 1=Warning, 2=Critical
     * @return 해당 등급의 색상
     */
    public static int getGradeColor(int grade) {
        return switch (grade) {
            case 0 -> GOOD;
            case 1 -> WARNING;
            default -> CRITICAL;
        };
    }

    /**
     * ARGB 색상 생성
     * 
     * @param rgb   RGB 색상 (0xRRGGBB)
     * @param alpha 불투명도 (0-255)
     * @return ARGB 색상
     */
    public static int withAlpha(int rgb, int alpha) {
        return (alpha << 24) | (rgb & 0xFFFFFF);
    }

    /**
     * 배경색 (반투명 검정) 반환
     * 
     * @return ARGB 배경색
     */
    public static int getBackground() {
        return withAlpha(BACKGROUND, BG_ALPHA);
    }

    /**
     * 진행률 바 색상 (0-100%)
     * 
     * @param percent 백분율 (0-100)
     * @return 해당 백분율에 맞는 색상
     */
    public static int getPercentColor(double percent) {
        if (percent <= 50)
            return GOOD;
        if (percent <= 75)
            return WARNING;
        return CRITICAL;
    }

    // --- UIRenderContext Compatibility ---

    /**
     * 배경 RGB 색상 반환 (UIRenderContext용)
     * 
     * @return RGB 색상 (0xRRGGBB)
     */
    public static int getBackgroundRGB() {
        return BACKGROUND;
    }

    /**
     * 배경 알파 값 반환 (UIRenderContext용)
     * 
     * @return 알파 값 (0.0 - 1.0)
     */
    public static float getBackgroundAlpha() {
        return BG_ALPHA / 255.0f;
    }
}
