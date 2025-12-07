package com.pulse.ui;

/**
 * UI 위젯 기본 클래스.
 * 모든 UI 요소의 상위 클래스.
 */
public abstract class Widget {

    protected int x, y;
    protected int width, height;
    protected boolean visible = true;
    protected boolean enabled = true;
    protected Widget parent;
    protected String id;

    public Widget(int x, int y, int width, int height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    // ─────────────────────────────────────────────────────────────
    // 렌더링
    // ─────────────────────────────────────────────────────────────

    /**
     * 위젯 렌더링 (하위 클래스에서 구현).
     */
    public abstract void render(UIRenderContext ctx);

    /**
     * 렌더링 전 처리.
     */
    public void preRender(UIRenderContext ctx) {
        // 선택적 오버라이드
    }

    /**
     * 렌더링 후 처리.
     */
    public void postRender(UIRenderContext ctx) {
        // 선택적 오버라이드
    }

    // ─────────────────────────────────────────────────────────────
    // 입력 처리
    // ─────────────────────────────────────────────────────────────

    /**
     * 마우스 클릭 처리.
     * 
     * @return 이벤트 소비 여부
     */
    public boolean onMouseClick(int mouseX, int mouseY, int button) {
        return false;
    }

    /**
     * 마우스 이동 처리.
     */
    public void onMouseMove(int mouseX, int mouseY) {
        // 선택적 오버라이드
    }

    /**
     * 키 입력 처리.
     * 
     * @return 이벤트 소비 여부
     */
    public boolean onKeyPress(int keyCode, char character) {
        return false;
    }

    /**
     * 마우스가 위젯 위에 있는지 확인.
     */
    public boolean isMouseOver(int mouseX, int mouseY) {
        int absX = getAbsoluteX();
        int absY = getAbsoluteY();
        return mouseX >= absX && mouseX < absX + width &&
                mouseY >= absY && mouseY < absY + height;
    }

    // ─────────────────────────────────────────────────────────────
    // 위치/크기
    // ─────────────────────────────────────────────────────────────

    public int getAbsoluteX() {
        return parent != null ? parent.getAbsoluteX() + x : x;
    }

    public int getAbsoluteY() {
        return parent != null ? parent.getAbsoluteY() + y : y;
    }

    public void setPosition(int x, int y) {
        this.x = x;
        this.y = y;
    }

    public void setSize(int width, int height) {
        this.width = width;
        this.height = height;
    }

    public void setBounds(int x, int y, int width, int height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    // Getters/Setters
    public int getX() {
        return x;
    }

    public int getY() {
        return y;
    }

    public int getWidth() {
        return width;
    }

    public int getHeight() {
        return height;
    }

    public boolean isVisible() {
        return visible;
    }

    public void setVisible(boolean visible) {
        this.visible = visible;
    }

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public Widget getParent() {
        return parent;
    }

    public void setParent(Widget parent) {
        this.parent = parent;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }
}
