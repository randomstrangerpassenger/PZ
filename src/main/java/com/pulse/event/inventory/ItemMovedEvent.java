package com.pulse.event.inventory;

/**
 * 아이템이 인벤토리 내에서 이동될 때 발생.
 */
public class ItemMovedEvent extends InventoryEvent {

    private final Object targetInventory;
    private final int targetSlot;

    public ItemMovedEvent(Object inventory, Object item, int slot,
            Object targetInventory, int targetSlot) {
        super(inventory, item, slot);
        this.targetInventory = targetInventory;
        this.targetSlot = targetSlot;
    }

    public Object getTargetInventory() {
        return targetInventory;
    }

    public int getTargetSlot() {
        return targetSlot;
    }

    @Override
    public String getEventName() {
        return "ItemMoved";
    }
}
