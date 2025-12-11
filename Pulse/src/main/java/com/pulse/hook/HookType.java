package com.pulse.hook;

import java.util.List;
import java.util.Objects;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Type-safe Hook 식별자.
 * 
 * 제네릭을 사용하여 콜백 타입의 안전성을 보장합니다.
 * 각 HookType은 특정 콜백 인터페이스와 연결됩니다.
 * 
 * @param <T> 이 Hook에 등록될 콜백 타입
 * @since Pulse 1.2
 */
public final class HookType<T> {

    private final String name;
    private final Class<T> callbackType;
    private final List<T> callbacks = new CopyOnWriteArrayList<>();

    private HookType(String name, Class<T> callbackType) {
        this.name = Objects.requireNonNull(name, "Hook name cannot be null");
        this.callbackType = Objects.requireNonNull(callbackType, "Callback type cannot be null");
    }

    /**
     * 새로운 HookType 생성
     * 
     * @param name         Hook 이름
     * @param callbackType 콜백 인터페이스 클래스
     * @return 새로운 HookType 인스턴스
     */
    public static <T> HookType<T> create(String name, Class<T> callbackType) {
        return new HookType<>(name, callbackType);
    }

    /**
     * Hook 이름
     */
    public String getName() {
        return name;
    }

    /**
     * 콜백 타입 클래스
     */
    public Class<T> getCallbackType() {
        return callbackType;
    }

    /**
     * 내부 콜백 리스트 (PulseHookRegistry 전용)
     */
    List<T> getCallbacksInternal() {
        return callbacks;
    }

    @Override
    public String toString() {
        return "HookType[" + name + "]";
    }

    @Override
    public boolean equals(Object o) {
        if (this == o)
            return true;
        if (o == null || getClass() != o.getClass())
            return false;
        HookType<?> hookType = (HookType<?>) o;
        return name.equals(hookType.name) && callbackType.equals(hookType.callbackType);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, callbackType);
    }
}
