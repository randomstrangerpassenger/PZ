package com.pulse.mixin.lua;

import com.pulse.api.log.PulseLogger;
import com.pulse.api.lua.PulseLuaHook;
import com.pulse.internal.InternalLuaHook;
import com.pulse.lua.LuaEventAdapter;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

import java.util.concurrent.atomic.AtomicBoolean;

/**
 * LuaEventManager Mixin.
 * 
 * zombie.Lua.LuaEventManager.triggerEvent()를 후킹하여
 * Lua 이벤트 통계를 수집.
 * 
 * Phase 2C 설계:
 * - HEAD: incrementPathHit() + fireEventStart(eventName)
 * - RETURN: fireEventEnd()
 * - On-Demand: profilingEnabled 시에만 타이밍 측정
 * 
 * @since Pulse 1.3
 */
@Mixin(targets = "zombie.Lua.LuaEventManager")
public abstract class MixinLuaEventManager {

    /** 최초 호출 플래그 */
    @Unique
    private static final AtomicBoolean FIRST = new AtomicBoolean(false);

    // =========================================
    // triggerEvent 오버로드 0~8 (HEAD + RETURN)
    // =========================================

    // === triggerEvent(String) ===
    @Inject(method = "triggerEvent(Ljava/lang/String;)V", at = @At("HEAD"), remap = false)
    private static void Pulse$onEvent0Head(String eventName, CallbackInfo ci) {
        Pulse$onEventHead(eventName);
    }

    @Inject(method = "triggerEvent(Ljava/lang/String;)V", at = @At("RETURN"), remap = false)
    private static void Pulse$onEvent0Return(String eventName, CallbackInfo ci) {
        InternalLuaHook.fireEventEnd();
    }

    // === triggerEvent(String, Object) ===
    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;)V", at = @At("HEAD"), remap = false)
    private static void Pulse$onEvent1Head(String eventName, Object a1, CallbackInfo ci) {
        Pulse$onEventHead(eventName);
    }

    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;)V", at = @At("RETURN"), remap = false)
    private static void Pulse$onEvent1Return(String eventName, Object a1, CallbackInfo ci) {
        InternalLuaHook.fireEventEnd();
    }

    // === triggerEvent(String, Object, Object) ===
    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("HEAD"), remap = false)
    private static void Pulse$onEvent2Head(String eventName, Object a1, Object a2, CallbackInfo ci) {
        Pulse$onEventHead(eventName);
    }

    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("RETURN"), remap = false)
    private static void Pulse$onEvent2Return(String eventName, Object a1, Object a2, CallbackInfo ci) {
        InternalLuaHook.fireEventEnd();
    }

    // === triggerEvent(String, Object x 3) ===
    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("HEAD"), remap = false)
    private static void Pulse$onEvent3Head(String eventName, Object a1, Object a2, Object a3, CallbackInfo ci) {
        Pulse$onEventHead(eventName);
    }

    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("RETURN"), remap = false)
    private static void Pulse$onEvent3Return(String eventName, Object a1, Object a2, Object a3, CallbackInfo ci) {
        InternalLuaHook.fireEventEnd();
    }

    // === triggerEvent(String, Object x 4) ===
    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("HEAD"), remap = false)
    private static void Pulse$onEvent4Head(String eventName, Object a1, Object a2, Object a3, Object a4,
            CallbackInfo ci) {
        Pulse$onEventHead(eventName);
    }

    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("RETURN"), remap = false)
    private static void Pulse$onEvent4Return(String eventName, Object a1, Object a2, Object a3, Object a4,
            CallbackInfo ci) {
        InternalLuaHook.fireEventEnd();
    }

    // === triggerEvent(String, Object x 5) ===
    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("HEAD"), remap = false)
    private static void Pulse$onEvent5Head(String eventName, Object a1, Object a2, Object a3, Object a4, Object a5,
            CallbackInfo ci) {
        Pulse$onEventHead(eventName);
    }

    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("RETURN"), remap = false)
    private static void Pulse$onEvent5Return(String eventName, Object a1, Object a2, Object a3, Object a4, Object a5,
            CallbackInfo ci) {
        InternalLuaHook.fireEventEnd();
    }

    // === triggerEvent(String, Object x 6) ===
    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("HEAD"), remap = false)
    private static void Pulse$onEvent6Head(String eventName, Object a1, Object a2, Object a3, Object a4, Object a5,
            Object a6, CallbackInfo ci) {
        Pulse$onEventHead(eventName);
    }

    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("RETURN"), remap = false)
    private static void Pulse$onEvent6Return(String eventName, Object a1, Object a2, Object a3, Object a4, Object a5,
            Object a6, CallbackInfo ci) {
        InternalLuaHook.fireEventEnd();
    }

    // === triggerEvent(String, Object x 7) ===
    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("HEAD"), remap = false)
    private static void Pulse$onEvent7Head(String eventName, Object a1, Object a2, Object a3, Object a4, Object a5,
            Object a6, Object a7, CallbackInfo ci) {
        Pulse$onEventHead(eventName);
    }

    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("RETURN"), remap = false)
    private static void Pulse$onEvent7Return(String eventName, Object a1, Object a2, Object a3, Object a4, Object a5,
            Object a6, Object a7, CallbackInfo ci) {
        InternalLuaHook.fireEventEnd();
    }

    // === triggerEvent(String, Object x 8) ===
    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("HEAD"), remap = false)
    private static void Pulse$onEvent8Head(String eventName, Object a1, Object a2, Object a3, Object a4, Object a5,
            Object a6, Object a7, Object a8, CallbackInfo ci) {
        Pulse$onEventHead(eventName);
    }

    @Inject(method = "triggerEvent(Ljava/lang/String;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)V", at = @At("RETURN"), remap = false)
    private static void Pulse$onEvent8Return(String eventName, Object a1, Object a2, Object a3, Object a4, Object a5,
            Object a6, Object a7, Object a8, CallbackInfo ci) {
        InternalLuaHook.fireEventEnd();
    }

    // =========================================
    // 공통 헬퍼 메서드 (DRY)
    // =========================================

    @Unique
    private static void Pulse$onEventHead(String eventName) {
        // Phase 1B: 경로 카운터 (항상 실행, ~10ns)
        PulseLuaHook.incrementPathHit();

        // Phase 2C: 이벤트 시작 기록 (On-Demand)
        InternalLuaHook.fireEventStart(eventName);

        // Initialize on first event (before forwarding to ensure mappings exist)
        if (FIRST.compareAndSet(false, true)) {
            PulseLogger.info("Pulse/MixinLuaEventManager", "✅ First triggerEvent! Mixin is working.");

            // Initialize Lua→Java event bridges (OnSave→PreSaveEvent, etc.)
            LuaEventAdapter.initializeStandardMappings();
        }

        // Forward to LuaEventAdapter for Lua→Java bridging (OnSave, OnLoad, etc.)
        // Pass empty array for parameterless events
        LuaEventAdapter.onLuaEvent(eventName, new Object[0]);
    }
}
