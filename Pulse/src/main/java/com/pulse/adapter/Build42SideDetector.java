package com.pulse.adapter;

import com.pulse.api.PulseSide;
import com.pulse.api.adapter.SideDetector;

/**
 * Build42용 Side 감지기 (Placeholder).
 * 
 * v4 Phase 2: B42 대응 설계 금지 원칙에 따라 placeholder만 제공.
 * 실제 B42 API가 확정되면 구현 추가.
 * 
 * NOTE: 이 클래스는 의도적으로 UNKNOWN만 반환함.
 * B42 본격 대응 시점에 구현을 추가할 것.
 * 
 * @since Pulse 0.8.0
 */
public class Build42SideDetector implements SideDetector {

    @Override
    public PulseSide detect() {
        // B42 placeholder - 항상 UNKNOWN 반환
        // Build42 API가 확정되면 여기에 구현 추가
        return PulseSide.UNKNOWN;
    }

    @Override
    public boolean isAvailable() {
        // B42는 아직 사용 불가로 설정
        // Build42 감지 로직이 확정되면 true로 변경
        return false;
    }

    @Override
    public int getPriority() {
        return 200; // Build42가 더 높은 우선순위 (사용 가능할 때)
    }
}
