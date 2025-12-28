package com.pulse.bootstrap;

import com.pulse.api.command.ICommandContext;
import com.pulse.api.command.ICommandRegistry;
import com.pulse.command.CommandRegistry;

import java.util.Collection;
import java.util.function.Consumer;
import java.util.stream.Collectors;

/**
 * ICommandRegistry 어댑터.
 * CommandRegistry 싱글톤을 ICommandRegistry 인터페이스에 연결.
 * 
 * @since Pulse 2.1
 */
public class CommandRegistryAdapter implements ICommandRegistry {

    private static final CommandRegistryAdapter INSTANCE = new CommandRegistryAdapter();

    private CommandRegistryAdapter() {
    }

    public static CommandRegistryAdapter getInstance() {
        return INSTANCE;
    }

    @Override
    public void register(String name, String description, Consumer<ICommandContext> executor) {
        CommandRegistry.getInstance().registerCommand(name, description, ctx -> {
            // CommandContext를 ICommandContext로 래핑
            executor.accept(new CommandContextAdapter(ctx));
        });
    }

    @Override
    public void unregister(String name) {
        // CommandRegistry에 unregister 메서드가 없으면 no-op
    }

    @Override
    public boolean hasCommand(String name) {
        return CommandRegistry.getInstance().getCommand(name) != null;
    }

    @Override
    public Collection<String> getCommandNames() {
        return CommandRegistry.getInstance().getAllCommands().stream()
                .map(cmd -> cmd.getName())
                .collect(Collectors.toSet());
    }

    @Override
    public String getPrefix() {
        return CommandRegistry.getInstance().getPrefix();
    }

    /**
     * CommandContext를 ICommandContext로 래핑하는 내부 클래스.
     */
    private static class CommandContextAdapter implements ICommandContext {
        private final com.pulse.command.CommandContext ctx;

        CommandContextAdapter(com.pulse.command.CommandContext ctx) {
            this.ctx = ctx;
        }

        @Override
        public String getCommandName() {
            return ctx.getCommandName();
        }

        @Override
        public String[] getRawArgs() {
            return ctx.getRawArgs();
        }

        @Override
        public int getArgCount() {
            return ctx.getArgCount();
        }

        @Override
        public boolean hasArg(int index) {
            return ctx.hasArg(index);
        }

        @Override
        public String getArg(int index) {
            return ctx.getArg(index);
        }

        @Override
        public String getArg(int index, String defaultValue) {
            return ctx.getArg(index, defaultValue);
        }

        @Override
        public void reply(String message) {
            ctx.reply(message);
        }

        @Override
        public void replyError(String message) {
            ctx.replyError(message);
        }
    }
}
