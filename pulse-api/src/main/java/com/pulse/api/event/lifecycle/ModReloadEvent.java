package com.pulse.api.event.lifecycle;

import com.pulse.api.event.Event;

/**
 * 모드 리로드 이벤트.
 * 모드가 활성화/비활성화/리로드될 때 발생.
 */
public class ModReloadEvent extends Event {

    private final String modId;
    private final Action action;

    public enum Action {
        ENABLED, // 모드 활성화됨
        DISABLED, // 모드 비활성화됨
        RELOADED, // 소프트 리로드됨
        CONFIG_RELOADED, // 설정만 리로드됨
        HOT_SWAPPED // JAR 핫 스왑됨
    }

    public ModReloadEvent(String modId, Action action) {
        this.modId = modId;
        this.action = action;
    }

    public String getModId() {
        return modId;
    }

    public Action getAction() {
        return action;
    }

    @Override
    public String toString() {
        return "ModReloadEvent{modId='" + modId + "', action=" + action + "}";
    }
}
