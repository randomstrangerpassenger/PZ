package com.pulse.lua;

import com.pulse.event.Event;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * EventBus ↔ Lua 이벤트 양방향 어댑터.
 * 
 * Java 이벤트 → Lua 콜백:
 * 
 * <pre>
 * LuaEventAdapter.bridgeToLua(GameTickEvent.class, "OnTick");
 * </pre>
 * 
 * Lua 이벤트 → Java EventBus:
 * 
 * <pre>
 * LuaEventAdapter.bridgeFromLua("OnPlayerMove", PlayerMoveEvent.class,
 *         args -> new PlayerMoveEvent(args[0], args[1], args[2]));
 * </pre>
 */
public class LuaEventAdapter {

    private static final String MOD_ID = "pulse_lua_adapter";

    // Lua 이벤트 이름 → Java 이벤트 클래스
    private static final Map<String, LuaToJavaMapping<?>> luaToJavaMappings = new ConcurrentHashMap<>();

    // Java 이벤트 클래스 → Lua 이벤트 이름
    private static final Map<Class<? extends Event>, String> javaToLuaMappings = new ConcurrentHashMap<>();

    private LuaEventAdapter() {
    }

    // ─────────────────────────────────────────────────────────────
    // Java → Lua 브릿지
    // ─────────────────────────────────────────────────────────────

    /**
     * Java 이벤트가 발생하면 Lua 이벤트로 전달.
     * 
     * @param eventClass   Java 이벤트 클래스
     * @param luaEventName PZ Lua 이벤트 이름 (예: "OnTick", "OnPlayerMove")
     */
    public static <T extends Event> void bridgeToLua(Class<T> eventClass, String luaEventName) {
        javaToLuaMappings.put(eventClass, luaEventName);

        EventBus.subscribe(eventClass, event -> {
            triggerLuaEvent(luaEventName, eventToLuaArgs(event));
        }, MOD_ID);

        System.out.println("[Pulse/LuaAdapter] Bridged " +
                eventClass.getSimpleName() + " -> Lua:" + luaEventName);
    }

    /**
     * Lua 이벤트 트리거.
     */
    private static void triggerLuaEvent(String eventName, Object... args) {
        if (!LuaBridge.isAvailable())
            return;

        try {
            // Events.<eventName>.Trigger(args...)
            LuaBridge.call("Events." + eventName + ".Trigger", args);
        } catch (Exception e) {
            System.err.println("[Pulse/LuaAdapter] Failed to trigger Lua event: " + eventName);
        }
    }

    /**
     * Event 객체를 Lua 인자로 변환.
     */
    private static Object[] eventToLuaArgs(Event event) {
        // 이벤트 타입에 따라 적절한 인자 추출
        if (event instanceof GameTickEvent) {
            GameTickEvent e = (GameTickEvent) event;
            return new Object[] { e.getTick() };
        }

        // 기본: 이벤트 객체 자체를 전달
        return new Object[] { event };
    }

    // ─────────────────────────────────────────────────────────────
    // Lua → Java 브릿지
    // ─────────────────────────────────────────────────────────────

    /**
     * Lua 이벤트를 Java EventBus로 전달.
     * 
     * @param luaEventName Lua 이벤트 이름
     * @param eventClass   Java 이벤트 클래스
     * @param factory      Lua 인자 → Java 이벤트 변환 함수
     */
    public static <T extends Event> void bridgeFromLua(
            String luaEventName,
            Class<T> eventClass,
            LuaEventFactory<T> factory) {

        luaToJavaMappings.put(luaEventName, new LuaToJavaMapping<>(eventClass, factory));

        // Lua에 Java 콜백 등록
        registerLuaCallback(luaEventName);

        System.out.println("[Pulse/LuaAdapter] Bridged Lua:" +
                luaEventName + " -> " + eventClass.getSimpleName());
    }

    /**
     * Lua 이벤트에 Java 콜백 등록.
     */
    private static void registerLuaCallback(String luaEventName) {
        if (!LuaBridge.isAvailable()) {
            // 나중에 처리
            return;
        }

        try {
            // Lua 쪽에서 호출할 Java 메서드 노출
            // Events.<eventName>.Add(function) 형태로 등록

            // Java 콜백 객체 생성
            LuaCallback callback = args -> onLuaEvent(luaEventName, args);

            // Lua에 등록
            LuaBridge.call("Events." + luaEventName + ".Add", callback);
        } catch (Exception e) {
            System.err.println("[Pulse/LuaAdapter] Failed to register Lua callback: " + luaEventName);
        }
    }

    /**
     * Lua에서 호출되는 콜백.
     */
    @SuppressWarnings("unchecked")
    private static void onLuaEvent(String luaEventName, Object[] args) {
        LuaToJavaMapping<?> mapping = luaToJavaMappings.get(luaEventName);
        if (mapping == null)
            return;

        try {
            Event event = ((LuaToJavaMapping<Event>) mapping).factory.create(args);
            EventBus.post(event);
        } catch (Exception e) {
            System.err.println("[Pulse/LuaAdapter] Failed to create event from Lua: " + luaEventName);
            e.printStackTrace();
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 표준 이벤트 매핑 초기화
    // ─────────────────────────────────────────────────────────────

    /**
     * 표준 PZ 이벤트 ↔ Pulse 이벤트 매핑 설정.
     */
    public static void initializeStandardMappings() {
        // GameTickEvent → OnTick
        bridgeToLua(GameTickEvent.class, "OnTick");

        // 더 많은 매핑은 나중에 추가
        System.out.println("[Pulse/LuaAdapter] Standard mappings initialized");
    }

    // ─────────────────────────────────────────────────────────────
    // 헬퍼 클래스/인터페이스
    // ─────────────────────────────────────────────────────────────

    @FunctionalInterface
    public interface LuaEventFactory<T extends Event> {
        T create(Object[] luaArgs);
    }

    @FunctionalInterface
    public interface LuaCallback {
        void call(Object[] args);
    }

    private static class LuaToJavaMapping<T extends Event> {
        final Class<T> eventClass;
        final LuaEventFactory<T> factory;

        LuaToJavaMapping(Class<T> eventClass, LuaEventFactory<T> factory) {
            this.eventClass = eventClass;
            this.factory = factory;
        }

        Class<T> getEventClass() {
            return eventClass;
        }
    }
}
