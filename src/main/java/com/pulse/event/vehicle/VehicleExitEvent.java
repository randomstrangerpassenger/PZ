package com.pulse.event.vehicle;

/**
 * 플레이어가 차량에서 하차할 때 발생.
 */
public class VehicleExitEvent extends VehicleEvent {

    private final Object player;
    private final int seat;

    public VehicleExitEvent(Object vehicle, Object player, int seat) {
        super(vehicle);
        this.player = player;
        this.seat = seat;
    }

    public Object getPlayer() {
        return player;
    }

    public int getSeat() {
        return seat;
    }

    @Override
    public String getEventName() {
        return "VehicleExit";
    }
}
