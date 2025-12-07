package com.pulse.event.inventory;

/**
 * 아이템이 인벤토리에 추가될 때 발생.
 */
public class ItemAddedEvent extends InventoryEvent {

    public ItemAddedEvent(Object inventory, Object item, int slot) {
        super(inventory, item, slot);
    }

    @Override
    public String getEventName() {
        return "ItemAdded";
    }
}
