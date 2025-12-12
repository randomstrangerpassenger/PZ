package com.pulse.ui;

/**
 * 텍스트 라벨 위젯.
 */
public class Label extends Widget {

    private String text;
    private int textColor = UIConstants.Colors.TEXT_DEFAULT;
    private Alignment alignment = Alignment.LEFT;

    public Label(int x, int y, String text) {
        super(x, y, 0, UIConstants.Layout.TEXT_HEIGHT); // 너비는 텍스트에 맞춰 자동 조정
        this.text = text;
    }

    public Label(int x, int y, int width, int height, String text) {
        super(x, y, width, height);
        this.text = text;
    }

    @Override
    public void render(UIRenderContext ctx) {
        if (!visible || text == null)
            return;

        int absX = getAbsoluteX();
        int absY = getAbsoluteY();

        int textWidth = ctx.getTextWidth(text);
        int textX;

        switch (alignment) {
            case CENTER:
                textX = absX + (width - textWidth) / 2;
                break;
            case RIGHT:
                textX = absX + width - textWidth;
                break;
            default:
                textX = absX;
        }

        ctx.drawText(text, textX, absY, textColor);
    }

    // Getters/Setters
    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public int getTextColor() {
        return textColor;
    }

    public void setTextColor(int color) {
        this.textColor = color;
    }

    public Alignment getAlignment() {
        return alignment;
    }

    public void setAlignment(Alignment alignment) {
        this.alignment = alignment;
    }

    public enum Alignment {
        LEFT, CENTER, RIGHT
    }
}
