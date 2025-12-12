/**
 * Pulse Public API.
 * 
 * <p>
 * 이 패키지는 Pulse의 공개 API를 포함합니다. 외부 모드에서 안전하게 사용할 수 있습니다.
 * </p>
 * 
 * <h2>주요 클래스</h2>
 * <ul>
 * <li>{@link com.pulse.api.Pulse} - 메인 API 파사드</li>
 * <li>{@link com.pulse.api.GameAccess} - 게임 내부 접근 (deprecated, use access/
 * package)</li>
 * <li>{@link com.pulse.api.SafeGameAccess} - 안전한 게임 데이터 접근</li>
 * <li>{@link com.pulse.api.PulseMetrics} - 성능 메트릭 수집</li>
 * <li>{@link com.pulse.api.PulseEvents} - 이벤트 시스템 파사드</li>
 * <li>{@link com.pulse.api.PulseLog} - 로깅 파사드</li>
 * </ul>
 * 
 * <h2>하위 패키지</h2>
 * <ul>
 * <li>{@code access} - 세부 게임 데이터 접근 (World, Player, Time, Network, Zombie)</li>
 * <li>{@code exception} - Pulse 예외 계층</li>
 * <li>{@code log} - 로깅 시스템</li>
 * <li>{@code lua} - Lua 상호운용</li>
 * <li>{@code util} - 유틸리티 클래스</li>
 * </ul>
 * 
 * <h2>안정성</h2>
 * <ul>
 * <li>{@link com.pulse.api.PublicAPI} - 안정적인 공개 API 표시</li>
 * <li>{@link com.pulse.api.InternalAPI} - 내부 API (변경 가능)</li>
 * <li>{@link com.pulse.api.Experimental} - 실험적 기능 표시</li>
 * </ul>
 * 
 * @since 1.0
 */
package com.pulse.api;
