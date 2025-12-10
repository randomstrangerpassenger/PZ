package com.pulse.mixin;

import com.pulse.api.mixin.MixinInjectionValidator;
import org.spongepowered.asm.mixin.extensibility.IMixinConfigPlugin;
import org.spongepowered.asm.mixin.extensibility.IMixinInfo;

import java.util.List;
import java.util.Set;

/**
 * Pulse Mixin 구성 플러그인.
 * Mixin 시스템과 fail-soft 정책을 연동합니다.
 * 
 * mixin.json에서 다음과 같이 등록:
 * 
 * <pre>
 * {
 *   "package": "com.pulse.mixin",
 *   "plugin": "com.pulse.mixin.PulseMixinPlugin",
 *   ...
 * }
 * </pre>
 * 
 * @since 1.1.0
 */
public class PulseMixinPlugin implements IMixinConfigPlugin {

    private String mixinPackage;

    @Override
    public void onLoad(String mixinPackage) {
        this.mixinPackage = mixinPackage;
        System.out.println("[Pulse/MixinPlugin] Loaded for package: " + mixinPackage);
    }

    @Override
    public String getRefMapperConfig() {
        // 기본 refmap 사용
        return null;
    }

    /**
     * Mixin 적용 여부 결정.
     * fail-soft에 의해 비활성화된 Mixin은 건너뜀.
     * 
     * @param targetClassName 대상 클래스
     * @param mixinClassName  Mixin 클래스
     * @return 적용하려면 true, 건너뛰려면 false
     */
    @Override
    public boolean shouldApplyMixin(String targetClassName, String mixinClassName) {
        // Mixin이 비활성화되어 있는지 확인
        if (MixinInjectionValidator.isMixinDisabled(mixinClassName)) {
            System.out.println("[Pulse/MixinPlugin] Skipping disabled mixin: " + mixinClassName);
            return false;
        }

        // 등록된 패키지의 Mixin인지 검증
        if (mixinPackage != null && !mixinClassName.startsWith(mixinPackage)) {
            System.out.println("[Pulse/MixinPlugin] Note: Mixin from external package: " + mixinClassName);
        }

        return true;
    }

    @Override
    public void acceptTargets(Set<String> myTargets, Set<String> otherTargets) {
        // 다른 Mixin과의 타겟 충돌 처리
        // 현재는 모든 타겟 허용
    }

    @Override
    public List<String> getMixins() {
        // 동적 Mixin 추가 (없음)
        return null;
    }

    @Override
    public void preApply(String targetClassName, org.objectweb.asm.tree.ClassNode targetClass,
            String mixinClassName, IMixinInfo mixinInfo) {
        // Mixin 적용 전 훅
        // 디버그 로깅 (DevMode에서만)
        if (com.pulse.api.DevMode.isEnabled()) {
            System.out.println("[Pulse/MixinPlugin] Pre-apply: " + mixinClassName + " → " + targetClassName);
        }
    }

    @Override
    public void postApply(String targetClassName, org.objectweb.asm.tree.ClassNode targetClass,
            String mixinClassName, IMixinInfo mixinInfo) {
        // Mixin 적용 후 훅
        // 성공 기록
        MixinInjectionValidator.recordSuccess(mixinClassName, targetClassName, 0);

        if (com.pulse.api.DevMode.isEnabled()) {
            System.out.println("[Pulse/MixinPlugin] Post-apply: " + mixinClassName + " → " + targetClassName + " ✓");
        }
    }
}
