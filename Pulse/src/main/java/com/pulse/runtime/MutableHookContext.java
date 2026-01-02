package com.pulse.runtime;

import com.pulse.api.profiler.IHookContext;

/**
 * Zero-allocation을 위한 재사용 가능 컨텍스트.
 * 
 * ThreadLocal과 함께 사용하여 GC 압력 최소화.
 * 매 좀비마다 new Context()를 방지.
 * 
 * <p>
 * <b>사용:</b>
 * </p>
 * 
 * <pre>
 * private static final ThreadLocal&lt;MutableHookContext&gt; CTX = ThreadLocal.withInitial(MutableHookContext::new);
 * 
 * MutableHookContext ctx = CTX.get();
 * try {
 *     ctx.update("ZOMBIE_UPDATE", gameTick, zombie);
 *     policy.shouldProcess(ctx);
 * } finally {
 *     ctx.clear(); // 필수: 참조 해제
 * }
 * </pre>
 * 
 * @since Pulse 2.2
 */
public final class MutableHookContext implements IHookContext {

    private String hookId = "UNKNOWN";
    private long gameTick = 0;
    private Object target = null;
    private long timestamp = 0;

    /**
     * 컨텍스트 갱신.
     * 
     * @param hookId   훅 식별자
     * @param gameTick 월드 틱
     * @param target   대상 객체 (좀비, 아이템 등)
     */
    public void update(String hookId, long gameTick, Object target) {
        this.hookId = hookId != null ? hookId : "UNKNOWN";
        this.gameTick = gameTick;
        this.target = target;
        this.timestamp = System.nanoTime();
    }

    /**
     * 참조 해제 (메모리 누수 방지).
     * 
     * ThreadLocal 사용 시 반드시 finally 블록에서 호출해야 함.
     */
    public void clear() {
        this.target = null;
        // hookId, gameTick, timestamp는 원시값이므로 리셋 불필요
    }

    @Override
    public String hookId() {
        return hookId;
    }

    @Override
    public long gameTick() {
        return gameTick;
    }

    @Override
    public Object getTarget() {
        return target;
    }

    @Override
    public long getTimestamp() {
        return timestamp;
    }
}
