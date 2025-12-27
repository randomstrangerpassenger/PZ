package com.pulse.api.ui;

import java.util.function.Consumer;

/**
 * HUD 렌더링 포트.
 * 최소한의 "그릴 수 있다" capability만 제공.
 * 
 * <p>
 * 레이어 관리/우선순위/가시성 등은 Frame의 레퍼런스 구현 참조.
 * </p>
 * 
 * <h2>API 확장 금지 규약</h2>
 * 이 인터페이스는 의도적으로 최소화되어 있습니다.
 * 다음 기능은 절대 추가하지 않습니다:
 * <ul>
 * <li>우선순위/순서 관리</li>
 * <li>가시성(visible/hidden) 상태</li>
 * <li>레이어 그룹화</li>
 * </ul>
 * 위 기능이 필요하면 Frame 레퍼런스를 복사/포크하세요.
 * 
 * @since Pulse 1.0
 */
public interface IHUDOverlay {
    /**
     * HUD 렌더링 콜백 등록.
     * 
     * @param id       고유 식별자
     * @param renderer 렌더링 함수
     */
    void registerRenderer(String id, Consumer<IUIRenderContext> renderer);

    /**
     * HUD 렌더링 콜백 제거.
     * 
     * @param id 고유 식별자
     */
    void unregisterRenderer(String id);
}
