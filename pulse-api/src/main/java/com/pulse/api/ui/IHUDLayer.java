package com.pulse.api.ui;

/**
 * HUD 레이어 인터페이스.
 * 
 * <p>
 * 이 인터페이스는 HUD 렌더링 capability만 정의합니다.
 * 생명주기 관리(update, tick)는 Core의 영역입니다.
 * </p>
 * 
 * <h3>사용 예시</h3>
 * 
 * <pre>{@code
 * public class MyHUD implements IHUDLayer {
 *     @Override
 *     public void render(IUIRenderContext ctx) {
 *         ctx.drawText("Hello", 10, 10, 0xFFFFFF);
 *     }
 * }
 * }</pre>
 * 
 * @since Pulse 2.0 (Phase 3 API Extraction)
 */
public interface IHUDLayer {

    /**
     * HUD 렌더링.
     * 매 프레임 호출됩니다.
     * 
     * @param ctx 렌더링 컨텍스트
     */
    void render(IUIRenderContext ctx);
}
