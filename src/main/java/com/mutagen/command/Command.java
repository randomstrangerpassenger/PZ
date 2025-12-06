package com.mutagen.command;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

/**
 * 명령어 메서드 마커 어노테이션.
 * 
 * 사용 예:
 * 
 * <pre>
 * public class MyCommands {
 *     {@literal @}Command(name = "heal", description = "Heal the player")
 *     public void healCommand(CommandContext ctx) {
 *         ctx.getSender().sendMessage("Healed!");
 *     }
 *     
 *     {@literal @}Command(name = "spawn", aliases = {"sp"}, permission = "mymod.spawn")
 *     public void spawnCommand(CommandContext ctx, @Arg("entity") String entity) {
 *         // ...
 *     }
 * }
 * </pre>
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Command {
    /**
     * 명령어 이름 (필수)
     */
    String name();

    /**
     * 명령어 설명
     */
    String description() default "";

    /**
     * 사용법 (자동 생성if 비어있음)
     */
    String usage() default "";

    /**
     * 별칭
     */
    String[] aliases() default {};

    /**
     * 필요 권한
     */
    String permission() default "";

    /**
     * 플레이어만 사용 가능
     */
    boolean playerOnly() default false;

    /**
     * 콘솔만 사용 가능
     */
    boolean consoleOnly() default false;
}
