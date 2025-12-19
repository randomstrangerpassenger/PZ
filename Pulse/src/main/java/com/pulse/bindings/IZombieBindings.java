package com.pulse.bindings;

/**
 * Zombie/Entity operations binding interface.
 * 
 * <p>
 * Abstracts zombie-related operations that may differ between B41/B42.
 * </p>
 * 
 * @since Pulse 0.9
 */
public interface IZombieBindings {

    // ═══════════════════════════════════════════════════════════════
    // ID Methods
    // ═══════════════════════════════════════════════════════════════

    /**
     * Get zombie unique ID.
     * 
     * @param zombie IsoZombie instance
     * @return Zombie ID
     */
    int getZombieId(Object zombie);

    /**
     * Get zombie online ID (MP).
     * 
     * @param zombie IsoZombie instance
     * @return Online ID, -1 if not available
     */
    int getOnlineId(Object zombie);

    /**
     * Get zombie local ID.
     * 
     * @param zombie IsoZombie instance
     * @return Local ID
     */
    int getLocalId(Object zombie);

    // ═══════════════════════════════════════════════════════════════
    // Position Methods
    // ═══════════════════════════════════════════════════════════════

    /**
     * Get zombie X position.
     */
    float getX(Object zombie);

    /**
     * Get zombie Y position.
     */
    float getY(Object zombie);

    /**
     * Get zombie Z position.
     */
    float getZ(Object zombie);

    /**
     * Get squared distance to nearest player.
     * 
     * @param zombie IsoZombie instance
     * @return Squared distance (MAX_VALUE if no player)
     */
    float getDistanceSquaredToNearestPlayer(Object zombie);

    // ═══════════════════════════════════════════════════════════════
    // State Methods
    // ═══════════════════════════════════════════════════════════════

    /**
     * Check if zombie is attacking.
     */
    boolean isAttacking(Object zombie);

    /**
     * Check if zombie has a target.
     */
    boolean hasTarget(Object zombie);

    /**
     * Get zombie's current target.
     * 
     * @return Target object (IsoMovingObject), null if none
     */
    Object getTarget(Object zombie);

    /**
     * Check if zombie is a crawler.
     */
    boolean isCrawler(Object zombie);

    /**
     * Check if zombie is on the floor.
     */
    boolean isOnFloor(Object zombie);
}
