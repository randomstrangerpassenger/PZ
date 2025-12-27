package com.pulse.api.event.save;

/**
 * 로드 후 이벤트.
 */
public class PostLoadEvent extends SaveEvent {

    private final boolean success;

    public PostLoadEvent(String saveName, SaveType saveType, boolean success) {
        super(saveName, saveType);
        this.success = success;
    }

    public boolean isSuccess() {
        return success;
    }

    @Override
    public String getEventName() {
        return "PostLoad";
    }
}
