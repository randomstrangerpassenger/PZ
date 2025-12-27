package com.pulse.event.vehicle;

import com.pulse.api.event.Event;

/**
 * 차량 관련 이벤트 기본 클래스.
 */
public abstract class VehicleEvent extends Event {

    private final Object vehicle; // BaseVehicle

    protected VehicleEvent(Object vehicle) {
        this.vehicle = vehicle;
    }

    public Object getVehicle() {
        return vehicle;
    }
}
