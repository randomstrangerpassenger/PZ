package com.pulse.adapter.zombie;

import com.pulse.api.version.GameVersion;

/**
 * Build 42+ 전용 IsoZombie 어댑터.
 * 
 * Build 42 출시 후 구현 예정입니다.
 * 현재는 Build41ZombieAdapter를 상속받아 동일하게 동작합니다.
 * 
 * Build 42에서 변경될 수 있는 사항:
 * - 엔진 리팩토링으로 인한 메서드 이름/시그니처 변경
 * - 새로운 최적화 API 추가
 * - 패키지 구조 변경
 * 
 * @since Pulse 1.4
 */
public class Build42ZombieAdapter extends Build41ZombieAdapter {

    @Override
    public int getSupportedBuild() {
        return GameVersion.BUILD_42;
    }

    @Override
    public String getName() {
        return "Build42ZombieAdapter";
    }

    @Override
    public boolean isCompatible() {
        // Build 42 전용 클래스 확인
        try {
            return false; // 아직 출시되지 않음
        } catch (Exception e) {
            return false;
        }
    }
}
