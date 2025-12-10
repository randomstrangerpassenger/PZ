package com.pulse.event.save;

/**
 * 저장 후 이벤트.
 */
public class PostSaveEvent extends SaveEvent {

    private final boolean success;

    public PostSaveEvent(String saveName, SaveType saveType, boolean success) {
        super(saveName, saveType);
        this.success = success;
    }

    public boolean isSuccess() {
        return success;
    }

    @Override
    public String getEventName() {
        return "PostSave";
    }
}
