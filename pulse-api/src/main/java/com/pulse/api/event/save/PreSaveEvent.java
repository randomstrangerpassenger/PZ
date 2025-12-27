package com.pulse.api.event.save;

/**
 * 저장 전 이벤트.
 * 모드 데이터를 저장하기 전에 준비할 수 있음.
 */
public class PreSaveEvent extends SaveEvent {

    public PreSaveEvent(String saveName, SaveType saveType) {
        super(saveName, saveType);
    }

    @Override
    public String getEventName() {
        return "PreSave";
    }
}
