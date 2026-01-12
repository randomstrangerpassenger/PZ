package com.pulse.event;

import com.pulse.api.DevMode;
import com.pulse.api.event.Event;
import com.pulse.api.event.EventListener;
import com.pulse.api.event.EventPriority;
import com.pulse.api.log.PulseLogger;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Pulse 이벤트 버스 - 이벤트 등록/발행/구독 관리 */
public class EventBus {

    private static final String LOG = PulseLogger.PULSE;
    private static final EventBus INSTANCE = new EventBus();

    // 이벤트 타입 → 리스너 목록
    private final Map<Class<? extends Event>, List<RegisteredListener<?>>> listeners = new ConcurrentHashMap<>();

    // Lazy Sort 최적화: 정렬이 필요한 이벤트 타입 추적
    private final Set<Class<? extends Event>> needsSort = ConcurrentHashMap.newKeySet();

    // 비동기 이벤트 실행용 스레드 풀
    private final ExecutorService asyncExecutor = Executors.newSingleThreadExecutor(
            r -> {
                Thread t = new Thread(r, "Pulse-AsyncEventBus");
                t.setDaemon(true);
                return t;
            });

    // 디버그 모드
    private boolean debug = false;

    // Singleton
    public static EventBus getInstance() {
        return INSTANCE;
    }

    // Static convenience methods
    public static <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener) {
        INSTANCE.register(eventType, listener, EventPriority.NORMAL, null);
    }

    public static <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener,
            EventPriority priority) {
        INSTANCE.register(eventType, listener, priority, null);
    }

    public static <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener,
            String modId) {
        INSTANCE.register(eventType, listener, EventPriority.NORMAL, modId);
    }

    public static <T extends Event> void subscribe(Class<T> eventType, EventListener<T> listener,
            EventPriority priority, String modId) {
        INSTANCE.register(eventType, listener, priority, modId);
    }

    public static <T extends Event> void unsubscribe(Class<T> eventType, EventListener<T> listener) {
        INSTANCE.unregister(eventType, listener);
    }

    public static <T extends Event> T post(T event) {
        return INSTANCE.fire(event);
    }

    /** 비동기 이벤트 발행 (UI/네트워크 이벤트용) */
    public static <T extends Event> void postAsync(T event) {
        INSTANCE.asyncExecutor.submit(() -> {
            try {
                INSTANCE.fire(event);
            } catch (Throwable t) {
                PulseLogger.error(LOG, "[EventBus] Async event error: {}", t.getMessage());
            }
        });
    }

    // Instance methods
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

        // Lazy Sort: 즉시 정렬하지 않고 플래그만 설정
        needsSort.add(eventType);

        // ClassLoader 디버그 (항상 출력 - 문제 진단용)
        String loaderName = eventType.getClassLoader() != null
                ? eventType.getClassLoader().getClass().getSimpleName()
                : "bootstrap";
        PulseLogger.info(LOG, "[EventBus] SUBSCRIBE: {} [loader={}] from {}",
                eventType.getName(), loaderName, modId != null ? modId : "unknown");

        if (debug) {
            String modInfo = modId != null ? " from mod " + modId : "";
            PulseLogger.debug(LOG, "Registered listener for {} with priority {}{}",
                    eventType.getSimpleName(), priority, modInfo);
        }
    }

    public <T extends Event> void unregister(Class<T> eventType, EventListener<T> listener) {
        List<RegisteredListener<?>> list = listeners.get(eventType);
        if (list != null) {
            list.removeIf(reg -> reg.listener == listener);
        }
    }

    /**
     * 이벤트 발행 (모든 리스너에 전달)
     * 
     * v2.1: ClassLoader 호환성을 위한 FQCN 기반 fallback 매칭 추가.
     * PZ 모드 로더가 모듈들을 다른 ClassLoader에서 로드할 경우,
     * 같은 이름의 클래스도 Class.equals()에서 다르게 인식됨.
     * 이를 해결하기 위해 Class 객체로 찾지 못하면 FQCN(클래스 이름)으로 fallback.
     */
    @SuppressWarnings("unchecked")
    public <T extends Event> T fire(T event) {
        Class<? extends Event> eventType = event.getClass();
        List<RegisteredListener<?>> list = listeners.get(eventType);

        // ClassLoader 디버그 (최초 1회 + 주기적)
        String eventClassName = eventType.getName();
        String eventLoaderName = eventType.getClassLoader() != null
                ? eventType.getClassLoader().getClass().getSimpleName()
                : "bootstrap";

        // ClassLoader Fallback: Class 객체로 찾지 못하면 FQCN으로 찾기
        if (list == null || list.isEmpty()) {
            list = findListenersByFQCN(eventClassName);
            if (list != null && !list.isEmpty()) {
                PulseLogger.info(LOG, "[EventBus] FQCN FALLBACK: {} [loader={}] -> found {} listeners",
                        eventClassName, eventLoaderName, list.size());
            }
        }

        if (list == null || list.isEmpty()) {
            // 첫 GameTickEndEvent에 대해서만 경고
            if (eventClassName.contains("GameTickEndEvent")) {
                PulseLogger.warn(LOG, "[EventBus] NO LISTENERS for {} [loader={}]",
                        eventClassName, eventLoaderName);
            }
            return event;
        }

        // Lazy Sort: 필요할 때만 정렬
        if (needsSort.remove(eventType)) {
            list.sort((a, b) -> Integer.compare(b.priority.getValue(), a.priority.getValue()));
        }

        if (debug) {
            PulseLogger.debug(LOG, "Firing {} to {} listener(s)", event.getEventName(), list.size());
        }

        for (RegisteredListener<?> registered : list) {
            // 취소된 이벤트는 더 이상 전달하지 않음 (선택적)
            if (event.isCancelled()) {
                break;
            }

            try {
                ((EventListener<T>) registered.listener).onEvent(event);
            } catch (ClassCastException cce) {
                // ClassLoader 불일치로 인한 ClassCastException 처리
                if (debug) {
                    PulseLogger.warn(LOG, "[EventBus] ClassCastException for {}: {}",
                            event.getEventName(), cce.getMessage());
                }
                // ClassLoader 불일치 시 리플렉션으로 호출 시도
                try {
                    invokeListenerReflectively(registered.listener, event);
                } catch (Exception reflectEx) {
                    String modId = registered.modId != null ? registered.modId : "unknown";
                    PulseLogger.error(LOG, "[EventBus] Reflective invocation failed for {}: {}",
                            modId, reflectEx.getMessage());
                }
            } catch (Exception e) {
                // 예외 격리: 어느 모드에서 문제가 발생했는지 명확히 로그
                String modId = registered.modId != null ? registered.modId : "unknown";
                PulseLogger.error(LOG, "Exception in listener {{}} for event {{}}", modId, event.getEventName());

                // DevMode일 때 추가 정보
                if (DevMode.isEnabled()) {
                    PulseLogger.error(LOG, "  Listener class: {}", registered.listener.getClass().getName());
                    PulseLogger.error(LOG, "  Priority: {}", registered.priority);
                }

                e.printStackTrace();

                // 예외가 발생해도 다른 리스너는 계속 실행됨 (격리)
            }
        }

        return event;
    }

    /**
     * FQCN(Fully Qualified Class Name)으로 리스너 찾기.
     * ClassLoader 불일치 시 fallback으로 사용.
     */
    private List<RegisteredListener<?>> findListenersByFQCN(String eventClassName) {
        for (Map.Entry<Class<? extends Event>, List<RegisteredListener<?>>> entry : listeners.entrySet()) {
            if (entry.getKey().getName().equals(eventClassName)) {
                return entry.getValue();
            }
        }
        return null;
    }

    /**
     * 리플렉션을 사용하여 리스너 호출.
     * ClassLoader 불일치로 직접 캐스팅이 불가능할 때 사용.
     */
    private void invokeListenerReflectively(Object listener, Event event) throws Exception {
        java.lang.reflect.Method onEventMethod = null;
        for (java.lang.reflect.Method method : listener.getClass().getMethods()) {
            if ("onEvent".equals(method.getName()) && method.getParameterCount() == 1) {
                onEventMethod = method;
                break;
            }
        }
        if (onEventMethod != null) {
            onEventMethod.invoke(listener, event);
        }
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
     * 특정 modId로 등록된 모든 리스너 해제 (정적 메서드 버전).
     * 모드 비활성화/리로드 시 사용.
     * 
     * @param modId 해제할 모드 ID
     * @return 해제된 리스너 수
     */
    public static int unsubscribeAllByModId(String modId) {
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
            PulseLogger.info(LOG, "Unregistered {} listeners for mod: {}", removed, modId);
        }
        return removed;
    }

    public void setDebug(boolean debug) {
        this.debug = debug;
    }

    // Internal classes
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
