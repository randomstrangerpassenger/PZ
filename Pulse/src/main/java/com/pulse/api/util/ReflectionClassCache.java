package com.pulse.api.util;

import com.pulse.PulseEnvironment;

import java.util.Optional;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Reflection 클래스 캐시 유틸리티.
 * 
 * 게임 클래스를 lazy loading으로 캐시하며, thread-safe한 구현입니다.
 * Double-checked locking 패턴으로 성능과 안전성을 모두 확보합니다.
 * 
 * <p>
 * 사용 예시:
 * </p>
 * 
 * <pre>
 * private static final ReflectionClassCache&lt;Object&gt; isoWorldCache = new ReflectionClassCache&lt;&gt;("zombie.iso.IsoWorld");
 * 
 * Class&lt;?&gt; worldClass = isoWorldCache.get();
 * if (worldClass != null) {
 *     // 클래스 사용
 * }
 * </pre>
 * 
 * @param <T> 캐시할 클래스 타입
 * @since 1.1.0
 */
public class ReflectionClassCache<T> {

    private final String className;
    private volatile Class<T> cachedClass;
    private final AtomicBoolean initialized = new AtomicBoolean(false);

    /**
     * 캐시 생성.
     * 
     * @param className 로드할 클래스의 완전한 이름 (예: "zombie.iso.IsoWorld")
     */
    public ReflectionClassCache(String className) {
        this.className = className;
    }

    /**
     * 캐시된 클래스를 반환합니다.
     * 첫 호출 시 lazy loading으로 클래스를 로드합니다.
     * 
     * @return 로드된 클래스, 로드 실패 시 null
     */
    @SuppressWarnings("unchecked")
    public Class<T> get() {
        if (!initialized.get()) {
            synchronized (this) {
                if (!initialized.get()) {
                    cachedClass = (Class<T>) loadClass();
                    initialized.set(true);
                }
            }
        }
        return cachedClass;
    }

    /**
     * 클래스를 Optional로 반환합니다.
     * NPE 방지용.
     * 
     * @return Optional로 감싼 클래스
     */
    public Optional<Class<T>> getOptional() {
        return Optional.ofNullable(get());
    }

    /**
     * 클래스를 반환하거나 예외를 던집니다.
     * 
     * @return 로드된 클래스
     * @throws IllegalStateException 클래스 로드 실패 시
     */
    public Class<T> getOrThrow() {
        Class<T> result = get();
        if (result == null) {
            throw new IllegalStateException("Failed to load class: " + className);
        }
        return result;
    }

    /**
     * 캐시를 갱신합니다.
     * 게임 클래스 로더가 변경된 경우 호출하세요.
     */
    public void refresh() {
        synchronized (this) {
            initialized.set(false);
            cachedClass = null;
        }
    }

    /**
     * 캐시가 초기화되었는지 확인.
     */
    public boolean isInitialized() {
        return initialized.get();
    }

    /**
     * 클래스가 성공적으로 로드되었는지 확인.
     */
    public boolean isLoaded() {
        return initialized.get() && cachedClass != null;
    }

    /**
     * 대상 클래스 이름.
     */
    public String getClassName() {
        return className;
    }

    private Class<?> loadClass() {
        ClassLoader loader = PulseEnvironment.getGameClassLoader();
        if (loader == null) {
            loader = ClassLoader.getSystemClassLoader();
        }
        try {
            return loader.loadClass(className);
        } catch (ClassNotFoundException e) {
            // 게임 클래스 로드 실패는 정상적인 상황일 수 있음
            // (예: 게임 시작 전 접근)
            return null;
        }
    }
}
