/**
 * Pulse Event System.
 * 
 * <p>
 * 이벤트 기반 통신을 위한 이벤트 버스 및 이벤트 타입 정의.
 * </p>
 * 
 * <h2>주요 클래스</h2>
 * <ul>
 * <li>{@link com.pulse.event.EventBus} - 이벤트 발행/구독 관리</li>
 * <li>{@link com.pulse.event.Event} - 이벤트 기본 클래스</li>
 * <li>{@link com.pulse.event.EventListener} - 이벤트 리스너 인터페이스</li>
 * <li>{@link com.pulse.event.EventPriority} - 리스너 우선순위</li>
 * </ul>
 * 
 * <h2>하위 패키지</h2>
 * <ul>
 * <li>{@code lifecycle} - 게임 생명주기 이벤트 (GameTickStart, GameTickEnd, WorldLoad
 * 등)</li>
 * <li>{@code player} - 플레이어 관련 이벤트</li>
 * <li>{@code world} - 월드 관련 이벤트</li>
 * <li>{@code network} - 네트워크 이벤트</li>
 * </ul>
 * 
 * <h2>사용 예</h2>
 * 
 * <pre>{@code
 * EventBus.subscribe(GameTickEvent.class, event -> {
 *     System.out.println("Tick: " + event.getTick());
 * });
 * 
 * EventBus.post(new GameTickEvent(tickCount));
 * }</pre>
 * 
 * @since 1.0
 */
package com.pulse.event;
