package com.pulse.input;

/**
 * 키 코드 상수.
 * LWJGL/GLFW 키 코드와 호환.
 */
public final class KeyCode {

    private KeyCode() {
    }

    // 알 수 없는 키
    public static final int KEY_UNKNOWN = -1;

    // 특수 키
    public static final int KEY_SPACE = 32;
    public static final int KEY_APOSTROPHE = 39; // '
    public static final int KEY_COMMA = 44; // ,
    public static final int KEY_MINUS = 45; // -
    public static final int KEY_PERIOD = 46; // .
    public static final int KEY_SLASH = 47; // /

    // 숫자 키 (상단)
    public static final int KEY_0 = 48;
    public static final int KEY_1 = 49;
    public static final int KEY_2 = 50;
    public static final int KEY_3 = 51;
    public static final int KEY_4 = 52;
    public static final int KEY_5 = 53;
    public static final int KEY_6 = 54;
    public static final int KEY_7 = 55;
    public static final int KEY_8 = 56;
    public static final int KEY_9 = 57;

    // 문자 키
    public static final int KEY_A = 65;
    public static final int KEY_B = 66;
    public static final int KEY_C = 67;
    public static final int KEY_D = 68;
    public static final int KEY_E = 69;
    public static final int KEY_F = 70;
    public static final int KEY_G = 71;
    public static final int KEY_H = 72;
    public static final int KEY_I = 73;
    public static final int KEY_J = 74;
    public static final int KEY_K = 75;
    public static final int KEY_L = 76;
    public static final int KEY_M = 77;
    public static final int KEY_N = 78;
    public static final int KEY_O = 79;
    public static final int KEY_P = 80;
    public static final int KEY_Q = 81;
    public static final int KEY_R = 82;
    public static final int KEY_S = 83;
    public static final int KEY_T = 84;
    public static final int KEY_U = 85;
    public static final int KEY_V = 86;
    public static final int KEY_W = 87;
    public static final int KEY_X = 88;
    public static final int KEY_Y = 89;
    public static final int KEY_Z = 90;

    // 기능 키
    public static final int KEY_ESCAPE = 256;
    public static final int KEY_ENTER = 257;
    public static final int KEY_TAB = 258;
    public static final int KEY_BACKSPACE = 259;
    public static final int KEY_INSERT = 260;
    public static final int KEY_DELETE = 261;
    public static final int KEY_RIGHT = 262;
    public static final int KEY_LEFT = 263;
    public static final int KEY_DOWN = 264;
    public static final int KEY_UP = 265;
    public static final int KEY_PAGE_UP = 266;
    public static final int KEY_PAGE_DOWN = 267;
    public static final int KEY_HOME = 268;
    public static final int KEY_END = 269;
    public static final int KEY_CAPS_LOCK = 280;
    public static final int KEY_SCROLL_LOCK = 281;
    public static final int KEY_NUM_LOCK = 282;
    public static final int KEY_PRINT_SCREEN = 283;
    public static final int KEY_PAUSE = 284;

    // F키
    public static final int KEY_F1 = 290;
    public static final int KEY_F2 = 291;
    public static final int KEY_F3 = 292;
    public static final int KEY_F4 = 293;
    public static final int KEY_F5 = 294;
    public static final int KEY_F6 = 295;
    public static final int KEY_F7 = 296;
    public static final int KEY_F8 = 297;
    public static final int KEY_F9 = 298;
    public static final int KEY_F10 = 299;
    public static final int KEY_F11 = 300;
    public static final int KEY_F12 = 301;

    // 넘패드
    public static final int KEY_KP_0 = 320;
    public static final int KEY_KP_1 = 321;
    public static final int KEY_KP_2 = 322;
    public static final int KEY_KP_3 = 323;
    public static final int KEY_KP_4 = 324;
    public static final int KEY_KP_5 = 325;
    public static final int KEY_KP_6 = 326;
    public static final int KEY_KP_7 = 327;
    public static final int KEY_KP_8 = 328;
    public static final int KEY_KP_9 = 329;

    // 수정자 키
    public static final int KEY_LEFT_SHIFT = 340;
    public static final int KEY_LEFT_CONTROL = 341;
    public static final int KEY_LEFT_ALT = 342;
    public static final int KEY_RIGHT_SHIFT = 344;
    public static final int KEY_RIGHT_CONTROL = 345;
    public static final int KEY_RIGHT_ALT = 346;

    /**
     * 키 코드를 이름으로 변환
     */
    public static String getName(int keyCode) {
        return switch (keyCode) {
            case KEY_UNKNOWN -> "Unknown";
            case KEY_SPACE -> "Space";
            case KEY_ESCAPE -> "Escape";
            case KEY_ENTER -> "Enter";
            case KEY_TAB -> "Tab";
            case KEY_BACKSPACE -> "Backspace";
            case KEY_DELETE -> "Delete";
            case KEY_UP -> "Up";
            case KEY_DOWN -> "Down";
            case KEY_LEFT -> "Left";
            case KEY_RIGHT -> "Right";
            case KEY_LEFT_SHIFT, KEY_RIGHT_SHIFT -> "Shift";
            case KEY_LEFT_CONTROL, KEY_RIGHT_CONTROL -> "Ctrl";
            case KEY_LEFT_ALT, KEY_RIGHT_ALT -> "Alt";
            default -> {
                if (keyCode >= KEY_A && keyCode <= KEY_Z) {
                    yield String.valueOf((char) keyCode);
                } else if (keyCode >= KEY_0 && keyCode <= KEY_9) {
                    yield String.valueOf((char) keyCode);
                } else if (keyCode >= KEY_F1 && keyCode <= KEY_F12) {
                    yield "F" + (keyCode - KEY_F1 + 1);
                } else if (keyCode >= KEY_KP_0 && keyCode <= KEY_KP_9) {
                    yield "Numpad " + (keyCode - KEY_KP_0);
                }
                yield "Key " + keyCode;
            }
        };
    }
}
