package com.pulse.debug;

@FunctionalInterface
public interface CommandExecutor {
    String execute(String args);
}
