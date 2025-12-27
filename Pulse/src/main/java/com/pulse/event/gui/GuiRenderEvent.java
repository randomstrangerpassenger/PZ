package com.pulse.event.gui;

import com.pulse.api.event.Event;

/**
 * GUI 렌더링 이벤트.
 * 커스텀 UI 요소를 그릴 수 있음.
 */
public class GuiRenderEvent extends Event {

    private final Object gui;
    private final String guiType;
    private final float deltaTime;

    public GuiRenderEvent(Object gui, String guiType, float deltaTime) {
        this.gui = gui;
        this.guiType = guiType;
        this.deltaTime = deltaTime;
    }

    public Object getGui() {
        return gui;
    }

    public String getGuiType() {
        return guiType;
    }

    public float getDeltaTime() {
        return deltaTime;
    }

    @Override
    public String getEventName() {
        return "GuiRender";
    }
}
