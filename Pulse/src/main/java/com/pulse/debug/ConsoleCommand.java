package com.pulse.debug;

public class ConsoleCommand {
    private final String description;
    private final CommandExecutor executor;

    public ConsoleCommand(String description, CommandExecutor executor) {
        this.description = description;
        this.executor = executor;
    }

    public String getDescription() {
        return description;
    }

    public String execute(String args) {
        return executor.execute(args);
    }
}
