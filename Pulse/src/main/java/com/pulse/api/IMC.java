package com.pulse.api;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/**
 * 모드 간 통신 API (Inter-Mod Communication).
 * 서비스 로케이터 패턴 기반.
 * 
 * 사용 예:
 * 
 * <pre>
 * // 서비스 등록
 * IMC.registerService("mymod:inventory_api", MyInventoryAPI.class, () -> new MyInventoryAPI());
 * 
 * // 서비스 사용
 * MyInventoryAPI api = IMC.getService("mymod:inventory_api", MyInventoryAPI.class);
 * if (api != null) {
 *     api.doSomething();
 * }
 * 
 * // 메시지 전송
 * IMC.sendMessage("othermod", "config_changed", myConfigData);
 * </pre>
 */
@PublicAPI(since = "1.0.0")
public class IMC {

    private static final IMC INSTANCE = new IMC();

    // 등록된 서비스
    private final Map<String, ServiceRegistration<?>> services = new ConcurrentHashMap<>();

    // 메시지 리스너
    private final Map<String, Map<String, MessageHandler>> messageHandlers = new ConcurrentHashMap<>();

    private IMC() {
    }

    // ─────────────────────────────────────────────────────────────
    // 서비스 API
    // ─────────────────────────────────────────────────────────────

    /**
     * 서비스 등록.
     * 
     * @param id      서비스 식별자 (예: "mymod:my_api")
     * @param type    서비스 인터페이스/클래스
     * @param factory 서비스 인스턴스 생성자
     */
    public static <T> void registerService(String id, Class<T> type, Supplier<T> factory) {
        INSTANCE.services.put(id, new ServiceRegistration<>(type, factory));
        System.out.println("[Pulse/IMC] Registered service: " + id);
    }

    /**
     * 서비스 조회.
     * 
     * @param id   서비스 식별자
     * @param type 예상되는 타입
     * @return 서비스 인스턴스 또는 null
     */
    @SuppressWarnings("unchecked")
    public static <T> T getService(String id, Class<T> type) {
        ServiceRegistration<?> reg = INSTANCE.services.get(id);
        if (reg == null) {
            return null;
        }
        if (!type.isAssignableFrom(reg.type)) {
            System.err.println("[Pulse/IMC] Service type mismatch: " + id);
            return null;
        }
        return (T) reg.getInstance();
    }

    /**
     * 서비스 존재 여부 확인.
     */
    public static boolean hasService(String id) {
        return INSTANCE.services.containsKey(id);
    }

    /**
     * 서비스 등록 해제.
     */
    public static void unregisterService(String id) {
        INSTANCE.services.remove(id);
    }

    // ─────────────────────────────────────────────────────────────
    // 메시지 API
    // ─────────────────────────────────────────────────────────────

    /**
     * 다른 모드에 메시지 전송.
     * 
     * @param targetModId 대상 모드 ID
     * @param messageType 메시지 타입
     * @param data        메시지 데이터
     */
    public static void sendMessage(String targetModId, String messageType, Object data) {
        Map<String, MessageHandler> handlers = INSTANCE.messageHandlers.get(targetModId);
        if (handlers == null) {
            return; // 수신자 없음
        }

        MessageHandler handler = handlers.get(messageType);
        if (handler == null) {
            handler = handlers.get("*"); // 와일드카드 핸들러
        }

        if (handler != null) {
            try {
                handler.handle(messageType, data);
            } catch (Exception e) {
                System.err.println("[Pulse/IMC] Error handling message: " + e.getMessage());
            }
        }
    }

    /**
     * 메시지 핸들러 등록.
     * 
     * @param modId       자신의 모드 ID
     * @param messageType 수신할 메시지 타입 ("*" = 모든 메시지)
     * @param handler     핸들러
     */
    public static void registerHandler(String modId, String messageType, MessageHandler handler) {
        INSTANCE.messageHandlers
                .computeIfAbsent(modId, k -> new ConcurrentHashMap<>())
                .put(messageType, handler);
    }

    /**
     * 등록된 모든 서비스 ID 조회.
     */
    public static java.util.Set<String> getRegisteredServices() {
        return java.util.Collections.unmodifiableSet(INSTANCE.services.keySet());
    }

    // ─────────────────────────────────────────────────────────────
    // 내부 클래스
    // ─────────────────────────────────────────────────────────────

    @FunctionalInterface
    public interface MessageHandler {
        void handle(String messageType, Object data);
    }

    private static class ServiceRegistration<T> {
        final Class<T> type;
        final Supplier<T> factory;
        private T instance;

        ServiceRegistration(Class<T> type, Supplier<T> factory) {
            this.type = type;
            this.factory = factory;
        }

        synchronized T getInstance() {
            if (instance == null) {
                instance = factory.get();
            }
            return instance;
        }
    }
}
