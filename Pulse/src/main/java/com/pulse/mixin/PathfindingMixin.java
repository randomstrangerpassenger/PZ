package com.pulse.mixin;

import com.pulse.api.profiler.PathfindingHook;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;

/**
 * Mixin for AI Pathfinding profiling.
 * 
 * @since Pulse 0.2.0
 */
@Mixin(targets = "zombie.ai.astar.AStarPathFinder")
public class PathfindingMixin {

    @Inject(method = "findPath", at = @At("HEAD"))
    private void Pulse$onFindPathStart(CallbackInfoReturnable<Object> cir) {
        PathfindingHook.onPathRequest();
        PathfindingHook.onGridSearchStart();
    }

    @Inject(method = "findPath", at = @At("RETURN"))
    private void Pulse$onFindPathEnd(CallbackInfoReturnable<Object> cir) {
        PathfindingHook.onGridSearchEnd();
    }
}
