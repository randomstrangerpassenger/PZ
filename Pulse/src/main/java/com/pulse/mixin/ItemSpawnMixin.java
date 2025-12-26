package com.pulse.mixin;

import com.pulse.api.log.PulseLogger;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Unique;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import zombie.inventory.InventoryItem;

/**
 * Mixin for IsoGridSquare - injects sequenceId assignment on item spawn.
 * 
 * P0 Features:
 * - Assigns sequenceId to IsoWorldInventoryObject on creation
 * - Intercepts all AddWorldInventoryItem methods
 * - Ensures session-wide unique sequenceId for spread distribution
 * 
 * Injection Points:
 * - AddWorldInventoryItem(String, float, float, float) -> most common spawn
 * path
 * - AddWorldInventoryItem(InventoryItem, float, float, float, boolean) ->
 * direct item placement
 * 
 * NOTE: This Mixin must coordinate with WorldItemMixin to avoid duplicate
 * assignment.
 * WorldItemMixin also has lazy sequenceId assignment as a fallback.
 * 
 * @since Fuse v2.2 Area 7
 */
@Mixin(targets = "zombie.iso.IsoGridSquare")
public class ItemSpawnMixin {

    /**
     * Debug counter for spawn tracking.
     */
    @Unique
    private static final java.util.concurrent.atomic.AtomicInteger Pulse$spawnCount = new java.util.concurrent.atomic.AtomicInteger(
            0);

    /**
     * Inject into AddWorldInventoryItem(String, float, float, float).
     * This is the primary spawn path for world items created by string type.
     * 
     * We inject at RETURN to access the created IsoWorldInventoryObject via
     * reflection.
     * 
     * @param itemType The item type string
     * @param x        X offset
     * @param y        Y offset
     * @param z        Z offset
     * @param cir      Callback info returnable - contains the created InventoryItem
     */
    @Inject(method = "AddWorldInventoryItem(Ljava/lang/String;FFF)Lzombie/inventory/InventoryItem;", at = @At("RETURN"))
    private void Pulse$onAddWorldInventoryItemString(
            String itemType,
            float x,
            float y,
            float z,
            CallbackInfoReturnable<InventoryItem> cir) {
        try {
            InventoryItem item = cir.getReturnValue();
            if (item != null) {
                Pulse$assignSequenceIdToWorldItem(item);
            }
        } catch (Throwable t) {
            PulseErrorHandler.reportMixinFailure("ItemSpawnMixin.onAddWorldInventoryItemString", t);
        }
    }

    /**
     * Inject into AddWorldInventoryItem(InventoryItem, float, float, float,
     * boolean).
     * This is the direct item placement path.
     * 
     * @param item     The inventory item
     * @param x        X offset
     * @param y        Y offset
     * @param z        Z offset
     * @param transmit Whether to transmit to clients
     * @param cir      Callback info returnable
     */
    @Inject(method = "AddWorldInventoryItem(Lzombie/inventory/InventoryItem;FFFZ)Lzombie/inventory/InventoryItem;", at = @At("RETURN"))
    private void Pulse$onAddWorldInventoryItemDirect(
            InventoryItem item,
            float x,
            float y,
            float z,
            boolean transmit,
            CallbackInfoReturnable<InventoryItem> cir) {
        try {
            if (item != null) {
                Pulse$assignSequenceIdToWorldItem(item);
            }
        } catch (Throwable t) {
            PulseErrorHandler.reportMixinFailure("ItemSpawnMixin.onAddWorldInventoryItemDirect", t);
        }
    }

    /**
     * Assign sequenceId to the world item via reflection.
     * 
     * The InventoryItem has a reference to its IsoWorldInventoryObject via
     * getWorldItem().
     * We access the Mixin field Pulse$sequenceId and assign it if not already set.
     * 
     * @param item The inventory item
     */
    @Unique
    private void Pulse$assignSequenceIdToWorldItem(InventoryItem item) {
        try {
            if (item == null) {
                return;
            }

            // Get the world item reference
            zombie.iso.objects.IsoWorldInventoryObject worldItem = item.getWorldItem();
            if (worldItem == null) {
                return;
            }

            // Access the Pulse$sequenceId field via reflection
            // Note: In Mixin environment, the field is directly accessible as it's mixed
            // into the class
            java.lang.reflect.Field seqIdField = worldItem.getClass().getDeclaredField("Pulse$sequenceId");
            seqIdField.setAccessible(true);

            int currentSeqId = seqIdField.getInt(worldItem);
            if (currentSeqId == -1) {
                // Get the counter from WorldItemMixin via reflection
                Class<?> mixinClass = Class.forName("com.pulse.mixin.WorldItemMixin");
                java.lang.reflect.Field counterField = mixinClass.getDeclaredField("Pulse$sequenceCounter");
                counterField.setAccessible(true);
                java.util.concurrent.atomic.AtomicInteger counter = (java.util.concurrent.atomic.AtomicInteger) counterField
                        .get(null);

                int newSeqId = counter.getAndIncrement();
                seqIdField.setInt(worldItem, newSeqId);

                // Debug logging for first few spawns
                int spawnCount = Pulse$spawnCount.incrementAndGet();
                if (spawnCount <= 5) {
                    PulseLogger.info("Pulse/ItemSpawnMixin",
                            String.format("✅ Assigned sequenceId=%d to %s", newSeqId, item.getType()));
                }
            }

        } catch (Throwable t) {
            // Silently fail - WorldItemMixin will assign sequenceId as fallback
            // Only log occasional errors to avoid spam
            if (Pulse$spawnCount.get() % 100 == 0) {
                PulseErrorHandler.reportMixinFailure("ItemSpawnMixin.assignSequenceId", t);
            }
        }
    }
}
