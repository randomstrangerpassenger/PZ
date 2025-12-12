package com.pulse.ui;

import java.util.function.Consumer;

/**
 * 버튼 위젯.
 */
public class Button extends Widget {

    private String text;
    private Consumer<Button> onClick;
    private boolean hovered = false;
    private boolean pressed = false;

    // 색상
    // 색상
    private int backgroundColor = UIConstants.Colors.BUTTON_BG;
    private int hoverColor = UIConstants.Colors.BUTTON_HOVER_BG;
    private int pressedColor = UIConstants.Colors.BUTTON_PRESSED_BG;
    private int textColor = UIConstants.Colors.TEXT_DEFAULT;
    private int borderColor = UIConstants.Colors.BUTTON_BORDER;

    public Button(int x, int y, int width, int height, String text) {
        super(x, y, width, height);
        this.text = text;
    }

    public Button(int x, int y, int width, int height, String text, Consumer<Button> onClick) {
        this(x, y, width, height, text);
        this.onClick = onClick;
    }

    @Override
    public void render(UIRenderContext ctx) {
        if (!visible)
            return;

        int absX = getAbsoluteX();
        int absY = getAbsoluteY();

        // 배경
        int bgColor = pressed ? pressedColor : (hovered ? hoverColor : backgroundColor);
        ctx.fillRect(absX, absY, width, height, bgColor);

        // 테두리
        ctx.drawRect(absX, absY, width, height, borderColor);

        // 텍스트 (가운데 정렬)
        int textWidth = ctx.getTextWidth(text);
        int textHeight = ctx.getTextHeight();
        int textX = absX + (width - textWidth) / 2;
        int textY = absY + (height - textHeight) / 2;
        ctx.drawText(text, textX, textY, enabled ? textColor : UIConstants.Colors.DISABLED_TEXT);
    }

    @Override
    public void onMouseMove(int mouseX, int mouseY) {
        hovered = isMouseOver(mouseX, mouseY);
    }

    @Override
    public boolean onMouseClick(int mouseX, int mouseY, int button) {
        if (!visible || !enabled)
            return false;

        if (button == 0 && isMouseOver(mouseX, mouseY)) {
            pressed = true;
            if (onClick != null) {
                onClick.accept(this);
            }
            return true;
        }
        return false;
    }

    // Getters/Setters
    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public void setOnClick(Consumer<Button> onClick) {
        this.onClick = onClick;
    }

    public void setBackgroundColor(int color) {
        this.backgroundColor = color;
    }

    public void setHoverColor(int color) {
        this.hoverColor = color;
    }

    public void setTextColor(int color) {
        this.textColor = color;
    }
}
