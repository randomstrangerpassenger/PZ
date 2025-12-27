package com.pulse.input;

import com.pulse.api.event.Event;

/**
 * 키 입력 이벤트.
 * 키 프레스/릴리즈 시 발생.
 */
public class KeyEvent extends Event {

    public enum Type {
        PRESS,
        RELEASE,
        REPEAT
    }

    private final Type type;
    private final int keyCode;
    private final boolean ctrl;
    private final boolean shift;
    private final boolean alt;

    public KeyEvent(Type type, int keyCode, boolean ctrl, boolean shift, boolean alt) {
        this.type = type;
        this.keyCode = keyCode;
        this.ctrl = ctrl;
        this.shift = shift;
        this.alt = alt;
    }

    public Type getType() {
        return type;
    }

    public int getKeyCode() {
        return keyCode;
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

    public boolean isPress() {
        return type == Type.PRESS;
    }

    public boolean isRelease() {
        return type == Type.RELEASE;
    }

    public boolean isRepeat() {
        return type == Type.REPEAT;
    }

    /**
     * 특정 키와 일치하는지 확인
     */
    public boolean matches(int keyCode) {
        return this.keyCode == keyCode;
    }

    /**
     * 키 바인딩과 일치하는지 확인
     */
    public boolean matches(KeyBinding binding) {
        return binding.matches(keyCode, ctrl, shift, alt);
    }

    @Override
    public String getEventName() {
        return "KeyEvent";
    }

    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("KeyEvent[");
        sb.append(type).append(", ");
        if (ctrl)
            sb.append("Ctrl+");
        if (shift)
            sb.append("Shift+");
        if (alt)
            sb.append("Alt+");
        sb.append(KeyCode.getName(keyCode)).append("]");
        return sb.toString();
    }
}
