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

    // 이벤트 타입 → 리스너 목록 (1차 경로: Class 키)
    private final Map<Class<? extends Event>, List<RegisteredListener<?>>> listeners = new ConcurrentHashMap<>();

    // FQCN → 리스너 목록 인덱스 (2차 경로: ClassLoader 불일치 시 O(1) fallback)
    // v4 Phase 1: 선형 탐색(findListenersByFQCN) 제거를 위한 인덱스
    private final Map<String, List<RegisteredListener<?>>> fqcnIndex = new ConcurrentHashMap<>();

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
        // 단일 COW 리스트 유지
        List<RegisteredListener<?>> list = listeners.computeIfAbsent(
                eventType,
                k -> new CopyOnWriteArrayList<>());

        RegisteredListener<T> registered = new RegisteredListener<>(listener, priority, modId);
        list.add(registered);

        // v4 Phase 1: 등록 시점에 정렬 (fire() 시 정렬 제거)
        // 우선순위 내림차순 (HIGH → NORMAL → LOW)
        list.sort((a, b) -> Integer.compare(b.priority.getValue(), a.priority.getValue()));

        // v4 Phase 1: FQCN 인덱스 동기화 (동일 리스트 객체 참조)
        fqcnIndex.put(eventType.getName(), list);

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
            // v4 Phase 1: 비었으면 인덱스도 정리
            if (list.isEmpty()) {
                listeners.remove(eventType);
                fqcnIndex.remove(eventType.getName());
            }
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

        // v4 Phase 1: 2차 경로 - FQCN 인덱스로 O(1) 조회 (선형 탐색 제거)
        if (list == null || list.isEmpty()) {
            list = fqcnIndex.get(eventClassName);
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

        // v4 Phase 1: fire() 시 정렬 없음 - 이미 등록 시점에 정렬됨

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

    // v4 Phase 1: findListenersByFQCN 삭제됨 - fqcnIndex로 O(1) 조회로 대체

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
        // v4 Phase 1: fqcnIndex 동기화
        fqcnIndex.remove(eventType.getName());
    }

    /**
     * 모든 리스너 해제
     */
    public void clearAll() {
        listeners.clear();
        // v4 Phase 1: fqcnIndex 동기화
        fqcnIndex.clear();
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
        // v4: 삭제할 키 수집 → 루프 밖에서 remove (CHM 반복 안전성)
        List<Class<? extends Event>> keysToRemove = new ArrayList<>();

        for (Map.Entry<Class<? extends Event>, List<RegisteredListener<?>>> entry : listeners.entrySet()) {
            List<RegisteredListener<?>> list = entry.getValue();
            int before = list.size();
            list.removeIf(reg -> modId.equals(reg.modId));
            removed += (before - list.size());

            // v4 Phase 1: 비었으면 인덱스 정리 대상에 추가
            if (list.isEmpty()) {
                keysToRemove.add(entry.getKey());
            }
        }

        // v4 Phase 1: 루프 밖에서 안전하게 제거
        for (Class<? extends Event> key : keysToRemove) {
            listeners.remove(key);
            fqcnIndex.remove(key.getName());
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
