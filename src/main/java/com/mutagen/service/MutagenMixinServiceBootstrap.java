package com.mutagen.service;

import org.spongepowered.asm.service.IMixinServiceBootstrap;

/**
 * Mixin 서비스 부트스트랩.
 * Sponge Mixin이 서비스를 초기화할 때 가장 먼저 호출됨.
 * 
 * ServiceLoader를 통해 자동 발견됨:
 * META-INF/services/org.spongepowered.asm.service.IMixinServiceBootstrap
 */
public class MutagenMixinServiceBootstrap implements IMixinServiceBootstrap {

    @Override
    public String getName() {
        return "Mutagen";
    }

    @Override
    public String getServiceClassName() {
        return "com.mutagen.service.MutagenMixinService";
    }

    @Override
    public void bootstrap() {
        System.out.println("[Mutagen/Bootstrap] Mixin service bootstrap initiated");
        
        // 환경 준비 작업
        // 예: 시스템 프로퍼티 설정, 초기 상태 구성 등
        
        System.out.println("[Mutagen/Bootstrap] Bootstrap complete");
    }
}
