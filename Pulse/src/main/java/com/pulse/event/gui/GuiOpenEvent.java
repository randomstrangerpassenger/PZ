package com.pulse.event.gui;

import com.pulse.api.event.Event;

/**
 * GUI 열림 이벤트.
 * 취소 가능 - GUI 열기를 막을 수 있음.
 */
public class GuiOpenEvent extends Event {

    private final Object gui; // UIElement 또는 패널
    private final String guiType; // 식별자

    public GuiOpenEvent(Object gui, String guiType) {
        this.gui = gui;
        this.guiType = guiType;
    }

    public Object getGui() {
        return gui;
    }

    public String getGuiType() {
        return guiType;
    }

    @Override
    public String getEventName() {
        return "GuiOpen";
    }
}
