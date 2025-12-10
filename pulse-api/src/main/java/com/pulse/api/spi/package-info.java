/**
 * Pulse SPI (Service Provider Interface) 패키지.
 * 
 * 모든 Pulse 모드(Echo, Fuse, Nerve 등)가 구현할 수 있는 범용 인터페이스 제공.
 * 특정 모드에 특혜 없이, 동일한 API로 Pulse와 연동 가능.
 * 
 * <h2>핵심 인터페이스</h2>
 * <ul>
 * <li>{@link IProvider} - 모든 프로바이더의 기본 인터페이스</li>
 * <li>{@link IProviderRegistry} - 프로바이더 등록/조회</li>
 * </ul>
 * 
 * <h2>도메인 인터페이스</h2>
 * <ul>
 * <li>{@link IProfilerProvider} - 프로파일링 (Echo 등)</li>
 * <li>{@link IOptimizerProvider} - 최적화 (Fuse 등)</li>
 * <li>{@link INetworkProvider} - 네트워크 (Nerve 등)</li>
 * </ul>
 * 
 * <h2>사용 예</h2>
 * 
 * <pre>
 * public class MyProfiler implements IProfilerProvider {
 *     public String getId() {
 *         return "my-profiler";
 *     }
 * 
 *     public String getName() {
 *         return "My Profiler";
 *     }
 * 
 *     public String getVersion() {
 *         return "1.0.0";
 *     }
 *     // ... 기타 메서드 구현
 * }
 * 
 * // Pulse에 등록
 * Pulse.getProviderRegistry().register(new MyProfiler());
 * </pre>
 */
package com.pulse.api.spi;
