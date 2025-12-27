package com.pulse.event.chat;

import com.pulse.api.event.Event;

/**
 * 명령어 실행 시 발생.
 */
public class CommandEvent extends Event {

    private final Object player;
    private final String command;
    private final String[] args;

    public CommandEvent(Object player, String command, String[] args) {
        this.player = player;
        this.command = command;
        this.args = args;
    }

    public Object getPlayer() {
        return player;
    }

    public String getCommand() {
        return command;
    }

    public String[] getArgs() {
        return args;
    }

    @Override
    public String getEventName() {
        return "Command";
    }
}
