package com.pulse.mixin;

import com.pulse.api.profiler.IsoGridHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfo;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Mixin for IsoGrid profiling.
 * 
 * Provides hooks for floor rendering and property recalculation in
 * IsoGridSquare.
 * These hooks allow Echo to profile grid-level operations.
 * 
 * @since Pulse 0.2.0
 * @since Pulse 1.2 - Activated with enabled flag check
 * @since Pulse 1.3 - Fixed: renderFloor returns boolean, use
 *        CallbackInfoReturnable
 */
@Mixin(targets = "zombie.iso.IsoGridSquare")
public class IsoGridMixin {

    // NOTE: renderFloor returns boolean, so we need CallbackInfoReturnable
    @Inject(method = "renderFloor", at = @At("HEAD"), remap = false)
    private void Pulse$onRenderFloorStart(CallbackInfoReturnable<Boolean> cir) {
        if (IsoGridHook.enabled) {
            IsoGridHook.onFloorUpdateStart();
        }
    }

    @Inject(method = "renderFloor", at = @At("RETURN"), remap = false)
    private void Pulse$onRenderFloorEnd(CallbackInfoReturnable<Boolean> cir) {
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
