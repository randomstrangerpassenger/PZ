package com.pulse.service;

import com.pulse.api.log.PulseLogger;
import org.spongepowered.asm.service.IMixinServiceBootstrap;

/**
 * Mixin 서비스 부트스트랩.
 * Sponge Mixin이 서비스를 초기화할 때 가장 먼저 호출됨.
 * 
 * ServiceLoader를 통해 자동 발견됨:
 * META-INF/services/org.spongepowered.asm.service.IMixinServiceBootstrap
 */
public class PulseMixinServiceBootstrap implements IMixinServiceBootstrap {
    private static final String LOG = PulseLogger.PULSE;

    @Override
    public String getName() {
        return "Pulse";
    }

    @Override
    public String getServiceClassName() {
        return "com.pulse.service.PulseMixinService";
    }

    @Override
    public void bootstrap() {
        PulseLogger.info(LOG, "[Bootstrap] Mixin service bootstrap initiated");

        // 환경 준비 작업
        // 예: 시스템 프로퍼티 설정, 초기 상태 구성 등

        PulseLogger.info(LOG, "[Bootstrap] Bootstrap complete");
    }
}
