/**
 * Pulse Hook 시스템.
 * 
 * Echo, Fuse, Nerve 등 모드들이 Pulse의 엔진 후킹을 안전하게 활용할 수 있도록
 * 중앙 집중식 Hook 관리 API를 제공합니다.
 * 
 * <h2>주요 클래스</h2>
 * <ul>
 * <li>{@link com.pulse.hook.PulseHookRegistry} - 중앙 Hook 관리자</li>
 * <li>{@link com.pulse.hook.HookType} - Type-safe Hook 식별자</li>
 * <li>{@link com.pulse.hook.HookTypes} - 사전 정의된 Hook 타입 상수</li>
 * </ul>
 * 
 * <h2>사용 예시</h2>
 * 
 * <pre>{@code
 * // 콜백 등록
 * PulseHookRegistry.register(HookTypes.TICK_PHASE, new TickPhaseHook.ITickPhaseCallback() {
 *     public long startPhase(String phase) {
 *         return System.nanoTime();
 *     }
 * 
 *     public void endPhase(String phase, long startTime) {
 *         long elapsed = System.nanoTime() - startTime;
 *         System.out.println(phase + " took " + elapsed + " ns");
 *     }
 * 
 *     public void onTickComplete() {
 *     }
 * });
 * 
 * // 콜백 브로드캐스트 (Mixin에서 호출)
 * PulseHookRegistry.broadcast(HookTypes.TICK_PHASE, cb -> cb.onTickComplete());
 * }</pre>
 * 
 * @since Pulse 1.2
 */
package com.pulse.hook;
