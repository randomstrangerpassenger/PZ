/**
 * Pulse Mixin Integration.
 * 
 * <p>
 * SpongePowered Mixin을 사용하여 Project Zomboid 게임 코드에 후킹.
 * </p>
 * 
 * <h2>주요 Mixin</h2>
 * <ul>
 * <li>{@code IsoWorldMixin} - 게임 틱 후킹 {@code update()}</li>
 * <li>{@code IsoPlayerMixin} - 플레이어 동작 후킹</li>
 * <li>{@code IsoZombieMixin} - 좀비 업데이트 후킹</li>
 * <li>{@code GameClientMixin} - 네트워크 클라이언트 후킹</li>
 * <li>{@code MainScreenStateMixin} - 렌더링 후킹</li>
 * <li>{@code PathfindingMixin} - 경로 탐색 후킹</li>
 * </ul>
 * 
 * <h2>오류 처리</h2>
 * <p>
 * 모든 Mixin 메서드는 fail-soft 정책을 따릅니다:
 * </p>
 * <ul>
 * <li>try-catch로 감싸서 게임 크래시 방지</li>
 * <li>{@link com.pulse.mixin.PulseErrorHandler}로 오류 보고</li>
 * <li>오류 발생 시 해당 기능만 비활성화</li>
 * </ul>
 * 
 * @since 1.0
 */
package com.pulse.mixin;
