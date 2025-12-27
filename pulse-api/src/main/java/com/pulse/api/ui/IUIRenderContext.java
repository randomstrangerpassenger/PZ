package com.pulse.api.ui;

/**
 * UI 렌더링 컨텍스트 계약.
 * 
 * <p>
 * <b>UI API 원칙</b>: 이 인터페이스는 원시 그리기 primitive만 허용하며,
 * 게임 엔진 타입(zombie.*)을 절대 노출하지 않습니다.
 * </p>
 * 
 * <ul>
 * <li>허용: drawText(String, int, int, int), drawRect(...), getScreenWidth()</li>
 * <li>금지: drawTexture(Texture), getPlayer(), UIFont</li>
 * </ul>
 * 
 * @since Pulse 1.0
 */
public interface IUIRenderContext {
    /**
     * 텍스트 그리기.
     * 
     * @param text  텍스트
     * @param x     X 좌표
     * @param y     Y 좌표
     * @param color ARGB 색상
     */
    void drawText(String text, int x, int y, int color);

    /**
     * 사각형 그리기.
     * 
     * @param x      X 좌표
     * @param y      Y 좌표
     * @param width  너비
     * @param height 높이
     * @param color  ARGB 색상
     */
    void drawRect(int x, int y, int width, int height, int color);

    /**
     * 채워진 사각형 그리기.
     * 
     * @param x      X 좌표
     * @param y      Y 좌표
     * @param width  너비
     * @param height 높이
     * @param color  RGB 색상
     * @param alpha  투명도 (0.0-1.0)
     */
    void fillRect(int x, int y, int width, int height, int color, float alpha);

    /**
     * 선 그리기.
     * 
     * @param x1    시작 X
     * @param y1    시작 Y
     * @param x2    끝 X
     * @param y2    끝 Y
     * @param color ARGB 색상
     */
    void drawLine(int x1, int y1, int x2, int y2, int color);

    /**
     * 화면 너비.
     */
    int getScreenWidth();

    /**
     * 화면 높이.
     */
    int getScreenHeight();
}
