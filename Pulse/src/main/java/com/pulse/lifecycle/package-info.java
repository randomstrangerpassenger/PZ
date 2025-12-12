/**
 * Pulse Lifecycle Management.
 * 
 * <p>
 * 게임 시작/종료 시 리소스 초기화 및 정리를 담당합니다.
 * </p>
 * 
 * <h2>주요 클래스</h2>
 * <ul>
 * <li>{@link com.pulse.lifecycle.LifecycleManager} - 생명주기 관리자</li>
 * </ul>
 * 
 * <h2>기능</h2>
 * <ul>
 * <li>JVM 셧다운 훅 자동 등록</li>
 * <li>사용자 정의 셧다운 훅 지원</li>
 * <li>Closeable 리소스 자동 정리</li>
 * <li>핵심 컴포넌트(Scheduler, EventBus, ServiceLocator) 정리</li>
 * </ul>
 * 
 * @since 1.2
 */
package com.pulse.lifecycle;
