/**
 * Pulse Mod Loader for Project Zomboid.
 * 
 * <p>
 * Pulse는 Project Zomboid를 위한 고성능 모드 로더입니다.
 * </p>
 * 
 * <h2>Core Packages</h2>
 * <table>
 * <tr>
 * <th>Package</th>
 * <th>Description</th>
 * </tr>
 * <tr>
 * <td>{@link com.pulse.api}</td>
 * <td>Public API for mod developers</td>
 * </tr>
 * <tr>
 * <td>{@link com.pulse.event}</td>
 * <td>Event bus and event types</td>
 * </tr>
 * <tr>
 * <td>{@link com.pulse.mod}</td>
 * <td>Mod loading and lifecycle</td>
 * </tr>
 * <tr>
 * <td>{@link com.pulse.scheduler}</td>
 * <td>Task scheduling</td>
 * </tr>
 * <tr>
 * <td>{@link com.pulse.lifecycle}</td>
 * <td>Resource cleanup</td>
 * </tr>
 * <tr>
 * <td>{@link com.pulse.mixin}</td>
 * <td>Game code hooks (internal)</td>
 * </tr>
 * </table>
 * 
 * <h2>Sub-module Projects</h2>
 * <ul>
 * <li><b>pulse-api</b> - SPI interfaces for dependent projects</li>
 * <li><b>Echo</b> - Performance profiler using Pulse API</li>
 * <li><b>Fuse</b> - AI-based optimizer</li>
 * <li><b>Nerve</b> - Network optimizer</li>
 * </ul>
 * 
 * <h2>Quick Start</h2>
 * 
 * <pre>{@code
 * public class MyMod implements PulseMod {
 *     @Override
 *     public void onInitialize() {
 *         PulseLogger.info("Pulse", "MyMod loaded!");
 * 
 *         EventBus.subscribe(GameTickEvent.class, e -> {
 *             // Handle tick
 *         });
 *     }
 * }
 * }</pre>
 * 
 * @see <a href="https://github.com/randomstrangerpassenger/PZ">GitHub
 *      Repository</a>
 * @since 1.0
 */
package com.pulse;
