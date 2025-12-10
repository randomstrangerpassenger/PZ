package com.pulse.ui;

import java.util.function.Consumer;

/**
 * 텍스트 입력 필드 위젯.
 */
public class TextField extends Widget {

    private StringBuilder text = new StringBuilder();
    private String placeholder = "";
    private int maxLength = 256;
    private int cursorPosition = 0;
    private boolean focused = false;

    // 콜백
    private Consumer<String> onTextChanged;
    private Consumer<String> onSubmit;

    // 색상
    private int backgroundColor = 0x202020;
    private int textColor = 0xFFFFFF;
    private int placeholderColor = 0x808080;
    private int borderColor = 0x404040;
    private int focusBorderColor = 0x6060FF;

    public TextField(int x, int y, int width, int height) {
        super(x, y, width, height);
    }

    public TextField(int x, int y, int width, int height, String placeholder) {
        this(x, y, width, height);
        this.placeholder = placeholder;
    }

    @Override
    public void render(UIRenderContext ctx) {
        if (!visible)
            return;

        int absX = getAbsoluteX();
        int absY = getAbsoluteY();

        // 배경
        ctx.fillRect(absX, absY, width, height, backgroundColor);

        // 테두리
        ctx.drawRect(absX, absY, width, height, focused ? focusBorderColor : borderColor);

        // 텍스트 또는 플레이스홀더
        String displayText = text.length() > 0 ? text.toString() : placeholder;
        int color = text.length() > 0 ? textColor : placeholderColor;

        int padding = 4;
        int textY = absY + (height - ctx.getTextHeight()) / 2;
        ctx.drawText(displayText, absX + padding, textY, color);

        // 커서 (포커스 시)
        if (focused && System.currentTimeMillis() % 1000 < 500) {
            String beforeCursor = text.substring(0, Math.min(cursorPosition, text.length()));
            int cursorX = absX + padding + ctx.getTextWidth(beforeCursor);
            ctx.fillRect(cursorX, absY + 2, 1, height - 4, textColor);
        }
    }

    @Override
    public boolean onMouseClick(int mouseX, int mouseY, int button) {
        boolean wasMouseOver = isMouseOver(mouseX, mouseY);
        focused = wasMouseOver && enabled;
        return wasMouseOver;
    }

    @Override
    public boolean onKeyPress(int keyCode, char character) {
        if (!focused || !enabled)
            return false;

        // 백스페이스
        if (keyCode == 14 && cursorPosition > 0) {
            text.deleteCharAt(cursorPosition - 1);
            cursorPosition--;
            notifyTextChanged();
            return true;
        }

        // Delete
        if (keyCode == 211 && cursorPosition < text.length()) {
            text.deleteCharAt(cursorPosition);
            notifyTextChanged();
            return true;
        }

        // Enter
        if (keyCode == 28) {
            if (onSubmit != null) {
                onSubmit.accept(text.toString());
            }
            return true;
        }

        // 좌/우 화살표
        if (keyCode == 203 && cursorPosition > 0) {
            cursorPosition--;
            return true;
        }
        if (keyCode == 205 && cursorPosition < text.length()) {
            cursorPosition++;
            return true;
        }

        // 일반 문자 입력
        if (character >= 32 && character < 127 && text.length() < maxLength) {
            text.insert(cursorPosition, character);
            cursorPosition++;
            notifyTextChanged();
            return true;
        }

        return false;
    }

    private void notifyTextChanged() {
        if (onTextChanged != null) {
            onTextChanged.accept(text.toString());
        }
    }

    // Getters/Setters
    public String getText() {
        return text.toString();
    }

    public void setText(String text) {
        this.text = new StringBuilder(text);
        this.cursorPosition = text.length();
    }

    public String getPlaceholder() {
        return placeholder;
    }

    public void setPlaceholder(String placeholder) {
        this.placeholder = placeholder;
    }

    public int getMaxLength() {
        return maxLength;
    }

    public void setMaxLength(int maxLength) {
        this.maxLength = maxLength;
    }

    public boolean isFocused() {
        return focused;
    }

    public void setFocused(boolean focused) {
        this.focused = focused;
    }

    public void setOnTextChanged(Consumer<String> callback) {
        this.onTextChanged = callback;
    }

    public void setOnSubmit(Consumer<String> callback) {
        this.onSubmit = callback;
    }
}
