package com.pulse.di;

import com.pulse.api.di.IServiceLocator;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Pulse 생태계 서비스 로케이터 (유일한 구현체).
 * 
 * <h2>설계 원칙 (Phase 2-B)</h2>
 * <ul>
 * <li>이 클래스가 서비스 등록/조회의 <b>유일한 진입점</b></li>
 * <li>Mixin 등 DI 불가능한 컴포넌트를 위한 브릿지</li>
 * <li>등록 시점: {@code PulseBootstrap.init()} (PulseRuntime 초기화 시)</li>
 * </ul>
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 조회
 * MyService service = PulseServiceLocator.getInstance().getService(MyService.class);
 * 
 * // 등록 (PulseBootstrap에서만)
 * PulseServiceLocator.getInstance().registerService(MyService.class, myServiceInstance);
 * }</pre>
 * 
 * @since Pulse 1.0
 * @see com.pulse.api.di.PulseServices 정적 접근 API
 */
public class PulseServiceLocator implements IServiceLocator {

    private static final PulseServiceLocator INSTANCE = new PulseServiceLocator();
    private final Map<Class<?>, Object> services = new ConcurrentHashMap<>();

    private PulseServiceLocator() {
    }

    public static PulseServiceLocator getInstance() {
        return INSTANCE;
    }

    public <T> void registerService(Class<T> type, T instance) {
        services.put(type, instance);
    }

    @Override
    public <T> T getService(Class<T> type) {
        return type.cast(services.get(type));
    }

    @Override
    public <T> boolean hasService(Class<T> type) {
        return services.containsKey(type);
    }

    public void clear() {
        services.clear();
    }

    // ═══════════════════════════════════════════════════════════════
    // v4 Phase 2: 테스트/리로드 지원
    // ═══════════════════════════════════════════════════════════════

    /**
     * 서비스 레지스트리 리셋 (테스트용).
     * 기본 서비스를 다시 초기화해야 하는 경우 사용.
     */
    public void reset() {
        services.clear();
        // 필요시 기본 서비스 재등록 로직 추가 가능
    }

    /**
     * 서비스 교체 (테스트용).
     * 기존 서비스를 Mock으로 교체할 때 사용.
     * 
     * @param type        서비스 타입
     * @param newInstance 새 인스턴스
     * @param <T>         서비스 타입
     * @return 기존 인스턴스 (없었으면 null)
     */
    public <T> T replaceService(Class<T> type, T newInstance) {
        Object old = services.put(type, newInstance);
        return type.isInstance(old) ? type.cast(old) : null;
    }
}
