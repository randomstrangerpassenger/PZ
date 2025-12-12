package com.pulse.ui;

/**
 * UI 관련 상수 모음.
 * 매직 넘버를 제거하고 일관된 테마를 제공하기 위함.
 * 
 * @since 1.3
 */
public final class UIConstants {
    private UIConstants() {
    }

    public static final class Colors {
        // 공통
        public static final int WHITE = 0xFFFFFF;
        public static final int BLACK = 0x000000;
        public static final int DISABLED_TEXT = 0x808080;

        // 버튼
        public static final int BUTTON_BG = 0x404040;
        public static final int BUTTON_HOVER_BG = 0x505050;
        public static final int BUTTON_PRESSED_BG = 0x303030;
        public static final int BUTTON_BORDER = 0x606060;

        // 텍스트/라벨
        public static final int TEXT_DEFAULT = 0xFFFFFF;

        // 패널/컨테이너
        public static final int PANEL_BG = 0x303030;
        public static final int PANEL_BORDER = 0x505050;

        // 입력 필드
        public static final int INPUT_BG = 0x202020;
        public static final int INPUT_BORDER = 0x404040;
        public static final int INPUT_FOCUS_BORDER = 0x6060FF;
        public static final int PLACEHOLDER = 0x808080;

        // 스크린
        public static final int SCREEN_BG = 0x000000;
    }

    public static final class Layout {
        public static final int DEFAULT_PADDING = 4;
        public static final int TEXT_HEIGHT = 16;
        public static final int DEFAULT_CHAR_WIDTH = 8; // 폰트 로드 실패 시 폴백
        public static final int CURSOR_WIDTH = 1;
        public static final int CURSOR_OFFSET = 2; // Y축 오프셋
    }

    public static final class Defaults {
        public static final int MAX_INPUT_LENGTH = 256;
        public static final int DEFAULT_SCREEN_WIDTH = 800;
        public static final int DEFAULT_SCREEN_HEIGHT = 600;
    }
}
