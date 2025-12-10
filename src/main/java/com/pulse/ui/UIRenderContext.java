package com.pulse.ui;

/**
 * UI 렌더링 컨텍스트.
 * 위젯 렌더링에 필요한 그래픽 API 래퍼.
 */
public class UIRenderContext {

    private Object graphics; // PZ의 UIGraphics 또는 Graphics2D
    private float deltaTime;
    private int screenWidth;
    private int screenHeight;

    public UIRenderContext(Object graphics, float deltaTime, int screenWidth, int screenHeight) {
        this.graphics = graphics;
        this.deltaTime = deltaTime;
        this.screenWidth = screenWidth;
        this.screenHeight = screenHeight;
    }

    // ─────────────────────────────────────────────────────────────
    // 기본 그리기
    // ─────────────────────────────────────────────────────────────

    /**
     * 사각형 그리기.
     */
    public void drawRect(int x, int y, int width, int height, int color) {
        drawRect(x, y, width, height, color, 1.0f);
    }

    public void drawRect(int x, int y, int width, int height, int color, float alpha) {
        try {
            // PZ UIGraphics 사용 시도
            if (graphics != null) {
                java.lang.reflect.Method drawMethod = graphics.getClass().getMethod(
                        "DrawRect", int.class, int.class, int.class, int.class,
                        float.class, float.class, float.class, float.class);

                float r = ((color >> 16) & 0xFF) / 255.0f;
                float g = ((color >> 8) & 0xFF) / 255.0f;
                float b = (color & 0xFF) / 255.0f;

                drawMethod.invoke(graphics, x, y, width, height, r, g, b, alpha);
            }
        } catch (Exception e) {
            // 폴백: 콘솔 로그
        }
    }

    /**
     * 채워진 사각형 그리기.
     */
    public void fillRect(int x, int y, int width, int height, int color) {
        fillRect(x, y, width, height, color, 1.0f);
    }

    public void fillRect(int x, int y, int width, int height, int color, float alpha) {
        try {
            if (graphics != null) {
                java.lang.reflect.Method fillMethod = graphics.getClass().getMethod(
                        "DrawRectFilled", int.class, int.class, int.class, int.class,
                        float.class, float.class, float.class, float.class);

                float r = ((color >> 16) & 0xFF) / 255.0f;
                float g = ((color >> 8) & 0xFF) / 255.0f;
                float b = (color & 0xFF) / 255.0f;

                fillMethod.invoke(graphics, x, y, width, height, r, g, b, alpha);
            }
        } catch (Exception e) {
            // 폴백
        }
    }

    /**
     * 텍스트 그리기.
     */
    public void drawText(String text, int x, int y, int color) {
        try {
            if (graphics != null) {
                java.lang.reflect.Method textMethod = graphics.getClass().getMethod(
                        "DrawText", String.class, int.class, int.class,
                        float.class, float.class, float.class, float.class);

                float r = ((color >> 16) & 0xFF) / 255.0f;
                float g = ((color >> 8) & 0xFF) / 255.0f;
                float b = (color & 0xFF) / 255.0f;

                textMethod.invoke(graphics, text, x, y, r, g, b, 1.0f);
            }
        } catch (Exception e) {
            // 폴백
        }
    }

    /**
     * 텍스트 너비 계산.
     */
    public int getTextWidth(String text) {
        try {
            if (graphics != null) {
                java.lang.reflect.Method widthMethod = graphics.getClass().getMethod(
                        "getTextWidth", String.class);
                return (int) widthMethod.invoke(graphics, text);
            }
        } catch (Exception e) {
            // 폴백: 글자당 8픽셀
        }
        return text.length() * 8;
    }

    /**
     * 텍스트 높이.
     */
    public int getTextHeight() {
        return 16; // 기본 폰트 높이
    }

    // Getters
    public Object getGraphics() {
        return graphics;
    }

    public float getDeltaTime() {
        return deltaTime;
    }

    public int getScreenWidth() {
        return screenWidth;
    }

    public int getScreenHeight() {
        return screenHeight;
    }
}
