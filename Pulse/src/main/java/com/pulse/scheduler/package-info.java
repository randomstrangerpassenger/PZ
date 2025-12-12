/**
 * Pulse Scheduler System.
 * 
 * <p>
 * 게임 틱 기반 태스크 스케줄링.
 * </p>
 * 
 * <h2>주요 클래스</h2>
 * <ul>
 * <li>{@link com.pulse.scheduler.PulseScheduler} - 스케줄러 싱글톤</li>
 * <li>{@link com.pulse.scheduler.TaskHandle} - 태스크 제어 핸들</li>
 * <li>{@link com.pulse.scheduler.SchedulerConfig} - 스케줄러 설정</li>
 * </ul>
 * 
 * <h2>스케줄링 타입</h2>
 * <ul>
 * <li>{@code runLater()} - 지연 후 1회 실행</li>
 * <li>{@code runTimer()} - 주기적 반복 실행</li>
 * <li>{@code runAsync()} - 비동기 즉시 실행</li>
 * <li>{@code runSync()} - 메인 스레드에서 실행</li>
 * </ul>
 * 
 * <h2>사용 예</h2>
 * 
 * <pre>{@code
 * // 60틱(약 3초) 후 실행
 * TaskHandle handle = PulseScheduler.runLater(() -> {
 *     System.out.println("Delayed task!");
 * }, 60);
 * 
 * // 취소
 * handle.cancel();
 * }</pre>
 * 
 * @since 1.0
 */
package com.pulse.scheduler;
