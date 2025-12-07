package com.pulse.event.inventory;

/**
 * 아이템이 인벤토리에서 제거될 때 발생.
 */
public class ItemRemovedEvent extends InventoryEvent {

    public ItemRemovedEvent(Object inventory, Object item, int slot) {
        super(inventory, item, slot);
    }

    @Override
    public String getEventName() {
        return "ItemRemoved";
    }
}
