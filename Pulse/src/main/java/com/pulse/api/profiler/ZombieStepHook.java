package com.pulse.api.profiler;

/**
 * Zombie Step Hook - Step-level throttling API.
 * 
 * Pulse provides hooks for individual zombie AI steps.
 * Fuse/other modules can implement throttle policies.
 * 
 * @since Pulse 1.3
 */
public class ZombieStepHook {

    /** Step types for throttling */
    public enum StepType {
        MOTION, // 이동 (skip 불가)
        PERCEPTION, // 인지 (throttle 가능)
        BEHAVIOR, // 행동 결정 (throttle 가능)
        TARGET, // 타겟 추적 (throttle 가능)
        COLLISION // 충돌 (skip 불가)
    }

    /** Throttle policy (Fuse에서 구현) */
    private static IZombieStepPolicy stepPolicy;

    // --- Registration ---

    public static void setStepPolicy(IZombieStepPolicy policy) {
        stepPolicy = policy;
        if (policy != null) {
            System.out.println("[Pulse] ZombieStepPolicy registered: " + policy.getClass().getSimpleName());
        }
    }

    public static void clearStepPolicy() {
        stepPolicy = null;
    }

    // --- Step Throttle Check ---

    /**
     * Check if a specific step should be skipped.
     * Called from Mixin before each step execution.
     * 
     * @param stepType Step type
     * @param distSq   Distance squared to nearest player
     * @param context  Additional context (zombie state)
     * @return true to skip this step
     */
    public static boolean shouldSkipStep(StepType stepType, float distSq, IStepContext context) {
        if (stepPolicy == null)
            return false;

        // MOTION and COLLISION are never skipped
        if (stepType == StepType.MOTION || stepType == StepType.COLLISION) {
            return false;
        }

        try {
            return stepPolicy.shouldSkipStep(stepType, distSq, context);
        } catch (Throwable t) {
            return false;
        }
    }

    /**
     * Convenience method without context.
     */
    public static boolean shouldSkipStep(StepType stepType, float distSq) {
        return shouldSkipStep(stepType, distSq, null);
    }

    // --- Interfaces ---

    /**
     * Step throttle policy interface.
     * Implemented by Fuse or other optimization modules.
     */
    public interface IZombieStepPolicy {
        /**
         * Determine if a step should be skipped.
         * 
         * @param stepType Step type
         * @param distSq   Distance squared to player
         * @param context  Zombie context (nullable)
         * @return true to skip
         */
        boolean shouldSkipStep(StepType stepType, float distSq, IStepContext context);
    }

    /**
     * Step context for additional decision making.
     */
    public interface IStepContext {
        int getIterIndex();

        int getWorldTick();

        boolean isAttacking();

        boolean hasTarget();
    }
}
