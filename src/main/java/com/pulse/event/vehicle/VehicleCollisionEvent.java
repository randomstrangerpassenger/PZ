package com.pulse.event.vehicle;

/**
 * 차량 충돌 시 발생.
 */
public class VehicleCollisionEvent extends VehicleEvent {

    private final Object otherObject; // 충돌 대상 (차량, 좀비, 건물 등)
    private final float impactForce;

    public VehicleCollisionEvent(Object vehicle, Object otherObject, float impactForce) {
        super(vehicle);
        this.otherObject = otherObject;
        this.impactForce = impactForce;
    }

    public Object getOtherObject() {
        return otherObject;
    }

    public float getImpactForce() {
        return impactForce;
    }

    @Override
    public String getEventName() {
        return "VehicleCollision";
    }
}
