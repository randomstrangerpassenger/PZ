package com.pulse.lua;

import com.pulse.api.log.PulseLogger;
import com.pulse.event.Event;
import com.pulse.event.EventBus;
import com.pulse.event.lifecycle.GameTickEvent;
import com.pulse.event.lifecycle.WorldLoadEvent;
import com.pulse.event.lifecycle.WorldUnloadEvent;
import com.pulse.event.player.PlayerUpdateEvent;
import com.pulse.event.player.PlayerDamageEvent;
import com.pulse.event.npc.ZombieDeathEvent;
import com.pulse.event.npc.ZombieSpawnEvent;
import com.pulse.event.environment.TimeChangeEvent;
import com.pulse.event.environment.WeatherChangeEvent;
import com.pulse.event.vehicle.VehicleEnterEvent;
import com.pulse.event.vehicle.VehicleExitEvent;
import com.pulse.event.save.PreSaveEvent;
import com.pulse.event.save.PreLoadEvent;
import com.pulse.event.save.SaveEvent;

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

    private static final String LOG = PulseLogger.PULSE;
    private static final String MOD_ID = "pulse_lua_adapter";
    private static boolean standardMappingsInitialized = false;

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
        if (javaToLuaMappings.containsKey(eventClass)) {
            return; // 이미 등록됨
        }

        javaToLuaMappings.put(eventClass, luaEventName);

        EventBus.subscribe(eventClass, event -> {
            triggerLuaEvent(luaEventName, eventToLuaArgs(event));
        }, MOD_ID);

        PulseLogger.info(LOG, "[LuaAdapter] Bridged {} → Lua:{}", eventClass.getSimpleName(), luaEventName);
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
            PulseLogger.error(LOG, "[LuaAdapter] Failed to trigger Lua event: {}", eventName);
        }
    }

    /**
     * Event 객체를 Lua 인자로 변환.
     */
    private static Object[] eventToLuaArgs(Event event) {
        // 이벤트 타입에 따라 적절한 인자 추출
        if (event instanceof GameTickEvent e) {
            return new Object[] { e.getTick() };
        }
        if (event instanceof PlayerUpdateEvent e) {
            return new Object[] { e.getPlayer() };
        }
        if (event instanceof PlayerDamageEvent e) {
            return new Object[] { e.getPlayer(), e.getDamage(), e.getDamageType() };
        }
        if (event instanceof ZombieDeathEvent e) {
            return new Object[] { e.getZombie(), e.getKiller() };
        }
        if (event instanceof ZombieSpawnEvent e) {
            return new Object[] { e.getZombie() };
        }
        if (event instanceof TimeChangeEvent e) {
            return new Object[] { e.getHour(), e.getMinute() };
        }
        if (event instanceof VehicleEnterEvent e) {
            return new Object[] { e.getVehicle(), e.getPlayer() };
        }
        if (event instanceof VehicleExitEvent e) {
            return new Object[] { e.getVehicle(), e.getPlayer() };
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

        PulseLogger.info(LOG, "[LuaAdapter] Bridged Lua:{} → {}", luaEventName, eventClass.getSimpleName());
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
            PulseLogger.error(LOG, "[LuaAdapter] Failed to register Lua callback: {}", luaEventName);
        }
    }

    /**
     * Lua에서 호출되는 콜백.
     * MixinLuaEventManager에서 triggerEvent 발생 시 호출됨.
     */
    @SuppressWarnings("unchecked")
    public static void onLuaEvent(String luaEventName, Object[] args) {
        LuaToJavaMapping<?> mapping = luaToJavaMappings.get(luaEventName);
        if (mapping == null)
            return;

        try {
            Event event = ((LuaToJavaMapping<Event>) mapping).factory.create(args);
            EventBus.post(event);
        } catch (Exception e) {
            PulseLogger.error(LOG, "[LuaAdapter] Failed to create event from Lua: {}", luaEventName, e);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 표준 이벤트 매핑 초기화
    // ─────────────────────────────────────────────────────────────

    /**
     * 표준 PZ 이벤트 ↔ Pulse 이벤트 매핑 설정.
     */
    public static void initializeStandardMappings() {
        if (standardMappingsInitialized) {
            PulseLogger.info(LOG, "[LuaAdapter] Standard mappings already initialized, skipping");
            return;
        }

        PulseLogger.info(LOG, "[LuaAdapter] Initializing standard event mappings...");

        try {
            int count = 0;

            // ═══════════════════════════════════════════════════════════
            // Java → Lua 방향
            // ═══════════════════════════════════════════════════════════

            // 라이프사이클 이벤트
            bridgeToLua(GameTickEvent.class, "OnPulseTick");
            count++;

            bridgeToLua(WorldLoadEvent.class, "OnPulseWorldLoad");
            count++;

            bridgeToLua(WorldUnloadEvent.class, "OnPulseWorldUnload");
            count++;

            // 플레이어 이벤트
            bridgeToLua(PlayerUpdateEvent.class, "OnPulsePlayerUpdate");
            count++;

            bridgeToLua(PlayerDamageEvent.class, "OnPulsePlayerDamage");
            count++;

            // 좀비 이벤트
            bridgeToLua(ZombieDeathEvent.class, "OnPulseZombieDeath");
            count++;

            bridgeToLua(ZombieSpawnEvent.class, "OnPulseZombieSpawn");
            count++;

            // 환경 이벤트
            bridgeToLua(TimeChangeEvent.class, "OnPulseTimeChange");
            count++;

            bridgeToLua(WeatherChangeEvent.class, "OnPulseWeatherChange");
            count++;

            // 차량 이벤트
            bridgeToLua(VehicleEnterEvent.class, "OnPulseVehicleEnter");
            count++;

            bridgeToLua(VehicleExitEvent.class, "OnPulseVehicleExit");
            count++;

            // ═══════════════════════════════════════════════════════════
            // Lua → Java 방향 (PZ 네이티브 이벤트 래핑)
            // ═══════════════════════════════════════════════════════════

            // 세이브 이벤트 (PZ OnSave → Pulse PreSaveEvent)
            // OnSave: 캐릭터/샌드박스 저장 후, 월드 저장 전 발생 (파라미터 없음)
            bridgeFromLua("OnSave", PreSaveEvent.class,
                    args -> {
                        PulseLogger.info(LOG, "[LuaAdapter] ★★★ OnSave event received from Lua! ★★★");
                        return new PreSaveEvent("lua_OnSave", SaveEvent.SaveType.WORLD);
                    });
            count++;
            PulseLogger.info(LOG, "[LuaAdapter] OnSave → PreSaveEvent bridge registered");

            // 로드 이벤트 (v2.0: 로그만, IOGuard 트리거 없음)
            bridgeFromLua("OnLoad", PreLoadEvent.class,
                    args -> {
                        PulseLogger.debug(LOG, "[LuaAdapter] OnLoad event received (logging only)");
                        return new PreLoadEvent("lua_OnLoad", SaveEvent.SaveType.WORLD);
                    });
            count++;

            standardMappingsInitialized = true;
            PulseLogger.info(LOG, "[LuaAdapter] Standard mappings initialized: {} events", count);
        } catch (Exception e) {
            PulseLogger.error(LOG, "[LuaAdapter] Failed to initialize standard mappings: {}", e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 매핑 현황 출력 (디버그용).
     */
    public static void printMappings() {
        PulseLogger.info(LOG, "[LuaAdapter] === Event Mappings ===");
        PulseLogger.info(LOG, "[LuaAdapter] Java → Lua:");
        for (var entry : javaToLuaMappings.entrySet()) {
            PulseLogger.info(LOG, "[LuaAdapter]   {} → {}", entry.getKey().getSimpleName(), entry.getValue());
        }
        PulseLogger.info(LOG, "[LuaAdapter] Lua → Java:");
        for (var entry : luaToJavaMappings.entrySet()) {
            PulseLogger.info(LOG, "[LuaAdapter]   {} → {}", entry.getKey(),
                    entry.getValue().eventClass.getSimpleName());
        }
        PulseLogger.info(LOG, "[LuaAdapter] =====================");
    }

    /**
     * 매핑 개수 반환.
     */
    public static int getMappingCount() {
        return javaToLuaMappings.size() + luaToJavaMappings.size();
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
    }
}
