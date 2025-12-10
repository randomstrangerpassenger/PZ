package com.pulse.event.gui;

import com.pulse.event.Event;

/**
 * GUI 닫힘 이벤트.
 */
public class GuiCloseEvent extends Event {

    private final Object gui;
    private final String guiType;

    public GuiCloseEvent(Object gui, String guiType) {
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
        return "GuiClose";
    }
}
