package com.pulse.event;

import com.pulse.api.DevMode;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

/**
 * Pulse 이벤트 버스.
 * 이벤트 등록, 발행, 구독을 관리.
 * 
 * 사용 예:
 * // 구독
 * EventBus.subscribe(GameTickEvent.class, event -> {
 * System.out.println("Game tick: " + event.getTick());
 * });
 * 
 * // 발행
 * EventBus.post(new GameTickEvent(tickCount));
 */
public class EventBus {

    private static final EventBus INSTANCE = new EventBus();

    // 이벤트 타입 → 리스너 목록
    private final Map<Class<? extends Event>, List<RegisteredListener<?>>> listeners = new ConcurrentHashMap<>();

    // 디버그 모드
    private boolean debug = false;

    // ─────────────────────────────────────────────────────────────
    // 싱글톤 접근
    // ─────────────────────────────────────────────────────────────

    public static EventBus getInstance() {
        return INSTANCE;
    }

    // ─────────────────────────────────────────────────────────────
    // 정적 메서드 (편의용)
    // ─────────────────────────────────────────────────────────────

    /**
     * 이벤트 리스너 등록 (기본 우선순위)
     */
    public static <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener) {
        INSTANCE.register(eventType, listener, EventPriority.NORMAL, null);
    }

    /**
     * 이벤트 리스너 등록 (우선순위 지정)
     */
    public static <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener,
            EventPriority priority) {
        INSTANCE.register(eventType, listener, priority, null);
    }

    /**
     * 이벤트 리스너 등록 (modId 지정 - 예외 격리용)
     */
    public static <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener,
            String modId) {
        INSTANCE.register(eventType, listener, EventPriority.NORMAL, modId);
    }

    /**
     * 이벤트 리스너 등록 (우선순위 + modId 지정)
     */
    public static <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener,
            EventPriority priority, String modId) {
        INSTANCE.register(eventType, listener, priority, modId);
    }

    /**
     * 이벤트 리스너 해제
     */
    public static <T extends Event> void unsubscribe(Class<T> eventType, EventListener<T> listener) {
        INSTANCE.unregister(eventType, listener);
    }

    /**
     * 이벤트 발행
     */
    public static <T extends Event> T post(T event) {
        return INSTANCE.fire(event);
    }

    // ─────────────────────────────────────────────────────────────
    // 인스턴스 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 리스너 등록 (modId 없이)
     */
    public <T extends Event> void register(Class<T> eventType, EventListener<T> listener,
            EventPriority priority) {
        register(eventType, listener, priority, null);
    }

    /**
     * 리스너 등록 (modId 포함 - 예외 격리용)
     */
    public <T extends Event> void register(Class<T> eventType, EventListener<T> listener,
            EventPriority priority, String modId) {
        List<RegisteredListener<?>> list = listeners.computeIfAbsent(
                eventType,
                k -> new CopyOnWriteArrayList<>());

        RegisteredListener<T> registered = new RegisteredListener<>(listener, priority, modId);
        list.add(registered);

        // 우선순위로 정렬 (높은 것이 먼저)
        list.sort((a, b) -> Integer.compare(b.priority.getValue(), a.priority.getValue()));

        if (debug) {
            String modInfo = modId != null ? " from mod " + modId : "";
            System.out.println("[Pulse/Event] Registered listener for " +
                    eventType.getSimpleName() + " with priority " + priority + modInfo);
        }
    }

    /**
     * 리스너 해제
     */
    public <T extends Event> void unregister(Class<T> eventType, EventListener<T> listener) {
        List<RegisteredListener<?>> list = listeners.get(eventType);
        if (list != null) {
            list.removeIf(reg -> reg.listener == listener);
        }
    }

    /**
     * 이벤트 발행 (모든 리스너에 전달)
     */
    @SuppressWarnings("unchecked")
    public <T extends Event> T fire(T event) {
        List<RegisteredListener<?>> list = listeners.get(event.getClass());

        if (list == null || list.isEmpty()) {
            return event;
        }

        if (debug) {
            System.out.println("[Pulse/EventBus] Firing " + event.getEventName() +
                    " to " + list.size() + " listener(s)");
        }

        for (RegisteredListener<?> registered : list) {
            // 취소된 이벤트는 더 이상 전달하지 않음 (선택적)
            if (event.isCancelled()) {
                break;
            }

            try {
                ((EventListener<T>) registered.listener).onEvent(event);
            } catch (Exception e) {
                // 예외 격리: 어느 모드에서 문제가 발생했는지 명확히 로그
                String modId = registered.modId != null ? registered.modId : "unknown";
                System.err.println("[Pulse/Event] Exception in listener {" + modId +
                        "} for event {" + event.getEventName() + "}");

                // DevMode일 때 추가 정보
                if (DevMode.isEnabled()) {
                    System.err.println("[Pulse/Event]   Listener class: " +
                            registered.listener.getClass().getName());
                    System.err.println("[Pulse/Event]   Priority: " + registered.priority);
                }

                e.printStackTrace();

                // 예외가 발생해도 다른 리스너는 계속 실행됨 (격리)
            }
        }

        return event;
    }

    /**
     * 특정 이벤트 타입의 모든 리스너 해제
     */
    public void clearListeners(Class<? extends Event> eventType) {
        listeners.remove(eventType);
    }

    /**
     * 모든 리스너 해제
     */
    public void clearAll() {
        listeners.clear();
    }

    /**
     * 등록된 리스너 수
     */
    public int getListenerCount(Class<? extends Event> eventType) {
        List<RegisteredListener<?>> list = listeners.get(eventType);
        return list != null ? list.size() : 0;
    }

    /**
     * 특정 modId로 등록된 모든 리스너 해제.
     * 모드 비활성화/리로드 시 사용.
     * 
     * @param modId 해제할 모드 ID
     * @return 해제된 리스너 수
     */
    public static int unsubscribeAll(String modId) {
        return INSTANCE.unregisterAll(modId);
    }

    private int unregisterAll(String modId) {
        if (modId == null)
            return 0;

        int removed = 0;
        for (List<RegisteredListener<?>> list : listeners.values()) {
            int before = list.size();
            list.removeIf(reg -> modId.equals(reg.modId));
            removed += (before - list.size());
        }

        if (removed > 0) {
            System.out.println("[Pulse/Event] Unregistered " + removed +
                    " listeners for mod: " + modId);
        }
        return removed;
    }

    public void setDebug(boolean debug) {
        this.debug = debug;
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    private static class RegisteredListener<T extends Event> {
        final EventListener<T> listener;
        final EventPriority priority;
        final String modId; // 예외 격리용 모드 식별자

        RegisteredListener(EventListener<T> listener, EventPriority priority, String modId) {
            this.listener = listener;
            this.priority = priority;
            this.modId = modId;
        }
    }
}
