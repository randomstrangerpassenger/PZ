package com.pulse.input;

/**
 * 키 바인딩 정의.
 * 모드에서 사용할 키 조합을 정의.
 * 
 * 사용 예:
 * 
 * <pre>
 * KeyBinding myKey = KeyBinding.create("mymod", "open_menu")
 *         .defaultKey(KeyCode.KEY_M)
 *         .withCtrl()
 *         .category("My Mod")
 *         .build();
 * 
 * KeyBindingRegistry.register(myKey);
 * </pre>
 */
public class KeyBinding {

    private final String modId;
    private final String id;
    private final String translationKey;
    private final String category;

    // 기본 키
    private int defaultKeyCode;
    private boolean defaultCtrl = false;
    private boolean defaultShift = false;
    private boolean defaultAlt = false;

    // 현재 바인딩된 키
    private int keyCode;
    private boolean ctrl = false;
    private boolean shift = false;
    private boolean alt = false;

    // 상태
    private boolean pressed = false;
    private boolean wasPressed = false;
    private int pressCount = 0;

    private KeyBinding(String modId, String id, String translationKey, String category) {
        this.modId = modId;
        this.id = id;
        this.translationKey = translationKey;
        this.category = category;
    }

    /**
     * 빌더 생성
     */
    public static Builder create(String modId, String id) {
        return new Builder(modId, id);
    }

    // ─────────────────────────────────────────────────────────────
    // 상태 체크
    // ─────────────────────────────────────────────────────────────

    /**
     * 키가 현재 눌려있는지 확인
     */
    public boolean isPressed() {
        return pressed;
    }

    /**
     * 키가 이번 틱에 눌렸는지 확인 (1회성)
     * wasPressed()와 달리 호출 시 상태가 리셋되지 않음
     */
    public boolean isDown() {
        return pressed && !wasPressed;
    }

    /**
     * 키가 이번 틱에 눌렸는지 확인하고 상태 리셋
     * 1회 입력 처리에 사용
     */
    public boolean wasPressed() {
        if (pressCount > 0) {
            pressCount--;
            return true;
        }
        return false;
    }

    /**
     * 키가 이번 틱에 릴리즈되었는지 확인
     */
    public boolean isReleased() {
        return !pressed && wasPressed;
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 상태 업데이트 (KeyBindingRegistry에서 호출)
    // ─────────────────────────────────────────────────────────────

    void updateState(boolean pressed) {
        this.wasPressed = this.pressed;
        this.pressed = pressed;

        if (pressed && !wasPressed) {
            pressCount++;
        }
    }

    void resetPressCount() {
        pressCount = 0;
    }

    // ─────────────────────────────────────────────────────────────
    // 키 설정
    // ─────────────────────────────────────────────────────────────

    /**
     * 키 바인딩 변경
     */
    public void setKey(int keyCode, boolean ctrl, boolean shift, boolean alt) {
        this.keyCode = keyCode;
        this.ctrl = ctrl;
        this.shift = shift;
        this.alt = alt;
    }

    /**
     * 기본값으로 리셋
     */
    public void resetToDefault() {
        this.keyCode = defaultKeyCode;
        this.ctrl = defaultCtrl;
        this.shift = defaultShift;
        this.alt = defaultAlt;
    }

    /**
     * 입력이 이 키 바인딩과 일치하는지 확인
     */
    public boolean matches(int inputKeyCode, boolean inputCtrl, boolean inputShift, boolean inputAlt) {
        return this.keyCode == inputKeyCode &&
                this.ctrl == inputCtrl &&
                this.shift == inputShift &&
                this.alt == inputAlt;
    }

    // ─────────────────────────────────────────────────────────────
    // Getters
    // ─────────────────────────────────────────────────────────────

    public String getModId() {
        return modId;
    }

    public String getId() {
        return id;
    }

    public String getFullId() {
        return modId + ":" + id;
    }

    public String getTranslationKey() {
        return translationKey;
    }

    public String getCategory() {
        return category;
    }

    public int getKeyCode() {
        return keyCode;
    }

    public int getDefaultKeyCode() {
        return defaultKeyCode;
    }

    public boolean hasCtrl() {
        return ctrl;
    }

    public boolean hasShift() {
        return shift;
    }

    public boolean hasAlt() {
        return alt;
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        if (ctrl)
            sb.append("Ctrl+");
        if (shift)
            sb.append("Shift+");
        if (alt)
            sb.append("Alt+");
        sb.append(KeyCode.getName(keyCode));
        return sb.toString();
    }

    // ─────────────────────────────────────────────────────────────
    // 빌더
    // ─────────────────────────────────────────────────────────────

    public static class Builder {
        private final String modId;
        private final String id;
        private String translationKey;
        private String category = "misc";
        private int keyCode = KeyCode.KEY_UNKNOWN;
        private boolean ctrl = false;
        private boolean shift = false;
        private boolean alt = false;

        private Builder(String modId, String id) {
            this.modId = modId;
            this.id = id;
            this.translationKey = "key." + modId + "." + id;
        }

        public Builder translationKey(String key) {
            this.translationKey = key;
            return this;
        }

        public Builder category(String category) {
            this.category = category;
            return this;
        }

        public Builder defaultKey(int keyCode) {
            this.keyCode = keyCode;
            return this;
        }

        public Builder withCtrl() {
            this.ctrl = true;
            return this;
        }

        public Builder withShift() {
            this.shift = true;
            return this;
        }

        public Builder withAlt() {
            this.alt = true;
            return this;
        }

        public KeyBinding build() {
            KeyBinding binding = new KeyBinding(modId, id, translationKey, category);
            binding.defaultKeyCode = keyCode;
            binding.defaultCtrl = ctrl;
            binding.defaultShift = shift;
            binding.defaultAlt = alt;
            binding.resetToDefault();
            return binding;
        }
    }
}
