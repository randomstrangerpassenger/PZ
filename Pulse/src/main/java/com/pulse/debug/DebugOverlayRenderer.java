package com.pulse.debug;

/**
 * 디버그 오버레이 렌더러 인터페이스.
 * 모드가 게임 화면에 디버그 정보를 표시하기 위해 구현.
 * 
 * 사용 예:
 * DebugOverlayRegistry.register("mymod", ctx -> {
 * ctx.drawText(10, 10, "My Mod Debug Info");
 * ctx.drawText(10, 30, "Value: " + myValue);
 * });
 */
@FunctionalInterface
public interface DebugOverlayRenderer {

    /**
     * 디버그 오버레이 렌더링
     * 
     * @param ctx 렌더링 컨텍스트
     */
    void render(DebugRenderContext ctx);
}
