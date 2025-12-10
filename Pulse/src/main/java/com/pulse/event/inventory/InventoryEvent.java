package com.pulse.event.inventory;

import com.pulse.event.Event;

/**
 * 인벤토리 관련 이벤트 기본 클래스.
 */
public abstract class InventoryEvent extends Event {

    private final Object inventory; // IsoGameCharacter의 인벤토리
    private final Object item; // InventoryItem
    private final int slot;

    protected InventoryEvent(Object inventory, Object item, int slot) {
        this.inventory = inventory;
        this.item = item;
        this.slot = slot;
    }

    public Object getInventory() {
        return inventory;
    }

    public Object getItem() {
        return item;
    }

    public int getSlot() {
        return slot;
    }
}
