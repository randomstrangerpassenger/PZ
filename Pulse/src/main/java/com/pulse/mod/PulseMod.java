package com.pulse.mod;

/**
 * Pulse 모드 엔트리포인트 인터페이스 (호환성 레이어).
 * 
 * 이 인터페이스는 pulse-api의 PulseMod 인터페이스를 상속하여
 * 기존 모드들과의 호환성을 유지합니다.
 * 
 * @since Pulse 1.0
 * @see com.pulse.api.mod.PulseMod
 */
public interface PulseMod extends com.pulse.api.mod.PulseMod {
    // pulse-api의 PulseMod를 상속하므로 추가 메서드 없음
}
