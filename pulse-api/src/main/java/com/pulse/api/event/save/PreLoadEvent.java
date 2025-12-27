package com.pulse.api.event.save;

/**
 * 로드 전 이벤트.
 */
public class PreLoadEvent extends SaveEvent {

    public PreLoadEvent(String saveName, SaveType saveType) {
        super(saveName, saveType);
    }

    @Override
    public String getEventName() {
        return "PreLoad";
    }
}
