package com.pulse.event.vehicle;

/**
 * 플레이어가 차량에 탑승할 때 발생.
 * 취소 가능 - 탑승을 막을 수 있음.
 */
public class VehicleEnterEvent extends VehicleEvent {

    private final Object player;
    private final int seat; // 좌석 번호 (0 = 운전석)

    public VehicleEnterEvent(Object vehicle, Object player, int seat) {
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

    public boolean isDriver() {
        return seat == 0;
    }

    @Override
    public String getEventName() {
        return "VehicleEnter";
    }
}
