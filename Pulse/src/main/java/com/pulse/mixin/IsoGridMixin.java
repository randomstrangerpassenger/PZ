package com.pulse.mixin;

import com.pulse.api.profiler.IsoGridHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;

/**
 * Mixin for IsoGrid profiling.
 * 
 * Provides hooks for floor rendering and property recalculation in
 * IsoGridSquare.
 * These hooks allow Echo to profile grid-level operations.
 * 
 * @since Pulse 0.2.0
 * @since Pulse 1.2 - Activated with enabled flag check
 */
@Mixin(targets = "zombie.iso.IsoGridSquare")
public class IsoGridMixin {

    @Inject(method = "renderFloor", at = @At("HEAD"), remap = false)
    private void Pulse$onRenderFloorStart(CallbackInfo ci) {
        if (IsoGridHook.enabled) {
            IsoGridHook.onFloorUpdateStart();
        }
    }

    @Inject(method = "renderFloor", at = @At("RETURN"), remap = false)
    private void Pulse$onRenderFloorEnd(CallbackInfo ci) {
        if (IsoGridHook.enabled) {
            IsoGridHook.onFloorUpdateEnd();
        }
    }

    // Echo 2.0 Phase 2: RecalcProperties Hook

    @Inject(method = "RecalcProperties", at = @At("HEAD"), remap = false)
    private void Pulse$onRecalcPropertiesStart(CallbackInfo ci) {
        if (IsoGridHook.enabled) {
            IsoGridHook.onRecalcPropertiesStart();
        }
    }

    @Inject(method = "RecalcProperties", at = @At("RETURN"), remap = false)
    private void Pulse$onRecalcPropertiesEnd(CallbackInfo ci) {
        if (IsoGridHook.enabled) {
            IsoGridHook.onRecalcPropertiesEnd();
        }
    }
}
