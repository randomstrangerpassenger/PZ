package com.pulse.api.ui;

/**
 * UI 관련 상수.
 * 
 * UI 마법 상수들을 중앙에서 관리합니다.
 * 
 * @since 1.1.0
 */
public final class UIConstants {

    private UIConstants() {
    }

    // --- 색상 (RGBA)---

    /** 기본 배경색 - 반투명 검정 */
    public static final float[] BG_DEFAULT = { 0f, 0f, 0f, 0.7f };

    /** 기본 텍스트 색상 - 흰색 */
    public static final float[] TEXT_DEFAULT = { 1f, 1f, 1f, 1f };

    /** 경고 색상 - 노랑 */
    public static final float[] TEXT_WARNING = { 1f, 1f, 0f, 1f };

    /** 오류 색상 - 빨강 */
    public static final float[] TEXT_ERROR = { 1f, 0.2f, 0.2f, 1f };

    /** 성공 색상 - 초록 */
    public static final float[] TEXT_SUCCESS = { 0.2f, 1f, 0.2f, 1f };

    /** 정보 색상 - 파랑 */
    public static final float[] TEXT_INFO = { 0.4f, 0.6f, 1f, 1f };

    /** 디버그 색상 - 회색 */
    public static final float[] TEXT_DEBUG = { 0.7f, 0.7f, 0.7f, 1f };

    // --- HUD 위치---

    /** HUD 기본 오프셋 X */
    public static final int HUD_OFFSET_X = 10;

    /** HUD 기본 오프셋 Y */
    public static final int HUD_OFFSET_Y = 10;

    /** HUD 줄 간격 */
    public static final int HUD_LINE_HEIGHT = 16;

    /** HUD 패딩 */
    public static final int HUD_PADDING = 5;

    // --- 폰트---

    /** 기본 폰트 크기 */
    public static final int FONT_SIZE_DEFAULT = 12;

    /** 큰 폰트 크기 */
    public static final int FONT_SIZE_LARGE = 16;

    /** 작은 폰트 크기 */
    public static final int FONT_SIZE_SMALL = 10;

    // --- 애니메이션---

    /** 페이드 인 시간 (ms) */
    public static final int FADE_IN_MS = 200;

    /** 페이드 아웃 시간 (ms) */
    public static final int FADE_OUT_MS = 300;

    /** 알림 표시 시간 (ms) */
    public static final int NOTIFICATION_DURATION_MS = 3000;

    // --- 성능 표시 임계값---

    /** FPS 경고 임계값 */
    public static final int FPS_WARNING_THRESHOLD = 30;

    /** FPS 위험 임계값 */
    public static final int FPS_CRITICAL_THRESHOLD = 15;

    /** 틱 경고 임계값 (ms) */
    public static final float TICK_WARNING_THRESHOLD_MS = 20f;

    /** 틱 위험 임계값 (ms) */
    public static final float TICK_CRITICAL_THRESHOLD_MS = 50f;

    // --- 그래프---

    /** 그래프 너비 */
    public static final int GRAPH_WIDTH = 200;

    /** 그래프 높이 */
    public static final int GRAPH_HEIGHT = 60;

    /** 그래프 히스토리 크기 */
    public static final int GRAPH_HISTORY_SIZE = 100;
}
