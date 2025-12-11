/**
 * Pulse 런타임 환경 및 버전 호환성 계층.
 * 
 * B41과 B42 사이의 API 차이를 흡수하여 모드가 버전에 관계없이 동작하게 합니다.
 * 
 * <h2>주요 클래스</h2>
 * <ul>
 * <li>{@link com.pulse.runtime.PulseRuntime} - 게임 버전 감지</li>
 * <li>{@link com.pulse.runtime.PulseReflection} - 안전한 Reflection 유틸리티</li>
 * </ul>
 * 
 * @since Pulse 1.2
 */
package com.pulse.runtime;
