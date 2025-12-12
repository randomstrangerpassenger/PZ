package com.pulse.service;

import com.pulse.api.log.PulseLogger;
import org.spongepowered.asm.service.ITransformer;
import org.spongepowered.asm.service.ITransformerProvider;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

/**
 * Mixin에게 transformer 정보를 제공하는 서비스.
 * 
 * Sponge Mixin은 이 provider를 통해:
 * 1. 기존 transformer들의 존재를 인식
 * 2. transformer 제외 규칙을 관리
 * 3. delegated transformer를 통한 체이닝 지원
 */
public class PulseTransformerProvider implements ITransformerProvider {

    private static final String LOG = PulseLogger.PULSE;
    private final List<ITransformer> transformers = new ArrayList<>();
    private final List<ITransformer> delegatedTransformers = new ArrayList<>();
    private final List<String> exclusions = new ArrayList<>();

    public PulseTransformerProvider() {
        // 기본 제외 패턴
        exclusions.add("java.");
        exclusions.add("javax.");
        exclusions.add("sun.");
        exclusions.add("com.pulse.mixin."); // Mixin 클래스 자체는 제외
    }

    @Override
    public Collection<ITransformer> getTransformers() {
        return Collections.unmodifiableList(transformers);
    }

    @Override
    public Collection<ITransformer> getDelegatedTransformers() {
        return Collections.unmodifiableList(delegatedTransformers);
    }

    @Override
    public void addTransformerExclusion(String name) {
        if (name != null && !name.isEmpty()) {
            exclusions.add(name);
            PulseLogger.info(LOG, "[TransformerProvider] Added exclusion: {}", name);
        }
    }

    /**
     * transformer 등록 (Pulse 내부용)
     */
    public void registerTransformer(ITransformer transformer) {
        if (transformer != null) {
            transformers.add(transformer);
            PulseLogger.info(LOG, "[TransformerProvider] Registered transformer: {}", transformer.getClass().getName());
        }
    }

    /**
     * 클래스가 제외 대상인지 확인
     */
    public boolean isExcluded(String className) {
        for (String exclusion : exclusions) {
            if (className.startsWith(exclusion)) {
                return true;
            }
        }
        return false;
    }

    public List<String> getExclusions() {
        return Collections.unmodifiableList(exclusions);
    }
}
