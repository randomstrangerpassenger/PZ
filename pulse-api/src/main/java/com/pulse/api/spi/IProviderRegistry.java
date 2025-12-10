package com.pulse.api.spi;

import java.util.Collection;
import java.util.Optional;

/**
 * 프로바이더 레지스트리 인터페이스.
 * Pulse가 이 인터페이스를 구현하여 프로바이더를 관리함.
 * 
 * 사용 예:
 * // 프로파일러 프로바이더 조회
 * Optional<IProfilerProvider> profiler =
 * registry.getProvider(IProfilerProvider.class);
 * 
 * // 모든 프로바이더 조회
 * Collection<IProvider> all = registry.getAllProviders();
 */
public interface IProviderRegistry {

    /**
     * 프로바이더 등록
     * 
     * @param provider 등록할 프로바이더
     * @param <T>      프로바이더 타입
     */
    <T extends IProvider> void register(T provider);

    /**
     * 프로바이더 등록 해제
     * 
     * @param providerId 프로바이더 ID
     */
    void unregister(String providerId);

    /**
     * ID로 프로바이더 조회
     * 
     * @param providerId 프로바이더 ID
     * @return 프로바이더 (없으면 Optional.empty())
     */
    Optional<IProvider> getProvider(String providerId);

    /**
     * 타입으로 프로바이더 조회
     * 
     * @param type 프로바이더 인터페이스 타입
     * @param <T>  프로바이더 타입
     * @return 해당 타입을 구현한 첫 번째 프로바이더
     */
    <T extends IProvider> Optional<T> getProvider(Class<T> type);

    /**
     * 타입으로 모든 프로바이더 조회
     * 
     * @param type 프로바이더 인터페이스 타입
     * @param <T>  프로바이더 타입
     * @return 해당 타입을 구현한 모든 프로바이더 (우선순위 정렬)
     */
    <T extends IProvider> Collection<T> getProviders(Class<T> type);

    /**
     * 등록된 모든 프로바이더 조회
     * 
     * @return 모든 프로바이더 목록
     */
    Collection<IProvider> getAllProviders();

    /**
     * 특정 프로바이더가 등록되어 있는지 확인
     * 
     * @param providerId 프로바이더 ID
     * @return 등록 여부
     */
    boolean isRegistered(String providerId);

    /**
     * 특정 타입의 프로바이더가 등록되어 있는지 확인
     * 
     * @param type 프로바이더 인터페이스 타입
     * @return 등록 여부
     */
    <T extends IProvider> boolean hasProvider(Class<T> type);
}
