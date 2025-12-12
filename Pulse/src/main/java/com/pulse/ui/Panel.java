package com.pulse.ui;

import java.util.ArrayList;
import java.util.List;

/**
 * 컨테이너 패널 위젯.
 * 다른 위젯들을 포함.
 */
public class Panel extends Widget {

    private final List<Widget> children = new ArrayList<>();
    private int backgroundColor = UIConstants.Colors.PANEL_BG;
    private int borderColor = UIConstants.Colors.PANEL_BORDER;
    private boolean drawBackground = true;
    private boolean drawBorder = true;
    private int padding = UIConstants.Layout.DEFAULT_PADDING;

    public Panel(int x, int y, int width, int height) {
        super(x, y, width, height);
    }

    @Override
    public void render(UIRenderContext ctx) {
        if (!visible)
            return;

        int absX = getAbsoluteX();
        int absY = getAbsoluteY();

        // 배경
        if (drawBackground) {
            ctx.fillRect(absX, absY, width, height, backgroundColor);
        }

        // 테두리
        if (drawBorder) {
            ctx.drawRect(absX, absY, width, height, borderColor);
        }

        // 자식 위젯 렌더링
        for (Widget child : children) {
            if (child.isVisible()) {
                child.preRender(ctx);
                child.render(ctx);
                child.postRender(ctx);
            }
        }
    }

    @Override
    public boolean onMouseClick(int mouseX, int mouseY, int button) {
        if (!visible || !enabled)
            return false;

        // 역순으로 검사 (위에 있는 것이 먼저)
        for (int i = children.size() - 1; i >= 0; i--) {
            Widget child = children.get(i);
            if (child.isVisible() && child.isEnabled()) {
                if (child.onMouseClick(mouseX, mouseY, button)) {
                    return true;
                }
            }
        }
        return isMouseOver(mouseX, mouseY);
    }

    @Override
    public void onMouseMove(int mouseX, int mouseY) {
        for (Widget child : children) {
            if (child.isVisible()) {
                child.onMouseMove(mouseX, mouseY);
            }
        }
    }

    @Override
    public boolean onKeyPress(int keyCode, char character) {
        for (Widget child : children) {
            if (child.isVisible() && child.isEnabled()) {
                if (child.onKeyPress(keyCode, character)) {
                    return true;
                }
            }
        }
        return false;
    }

    // ─────────────────────────────────────────────────────────────
    // 자식 관리
    // ─────────────────────────────────────────────────────────────

    public void add(Widget widget) {
        widget.setParent(this);
        children.add(widget);
    }

    public void remove(Widget widget) {
        widget.setParent(null);
        children.remove(widget);
    }

    public void clear() {
        for (Widget child : children) {
            child.setParent(null);
        }
        children.clear();
    }

    public List<Widget> getChildren() {
        return new ArrayList<>(children);
    }

    public Widget findById(String id) {
        for (Widget child : children) {
            if (id.equals(child.getId())) {
                return child;
            }
            if (child instanceof Panel) {
                Widget found = ((Panel) child).findById(id);
                if (found != null)
                    return found;
            }
        }
        return null;
    }

    // Getters/Setters
    public int getBackgroundColor() {
        return backgroundColor;
    }

    public void setBackgroundColor(int color) {
        this.backgroundColor = color;
    }

    public int getBorderColor() {
        return borderColor;
    }

    public void setBorderColor(int color) {
        this.borderColor = color;
    }

    public boolean isDrawBackground() {
        return drawBackground;
    }

    public void setDrawBackground(boolean draw) {
        this.drawBackground = draw;
    }

    public boolean isDrawBorder() {
        return drawBorder;
    }

    public void setDrawBorder(boolean draw) {
        this.drawBorder = draw;
    }

    public int getPadding() {
        return padding;
    }

    public void setPadding(int padding) {
        this.padding = padding;
    }
}
