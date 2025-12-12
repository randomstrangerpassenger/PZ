/**
 * Pulse Mod Loading System.
 * 
 * <p>
 * 모드 발견, 의존성 해결, 초기화를 담당합니다.
 * </p>
 * 
 * <h2>주요 클래스</h2>
 * <ul>
 * <li>{@link com.pulse.mod.ModLoader} - 모드 로더 싱글톤</li>
 * <li>{@link com.pulse.mod.ModContainer} - 로드된 모드 래퍼</li>
 * <li>{@link com.pulse.mod.ModMetadata} - 모드 메타데이터 (pulse.mod.json)</li>
 * <li>{@link com.pulse.mod.PulseMod} - 모드 엔트리포인트 인터페이스</li>
 * <li>{@link com.pulse.mod.ModReloadManager} - 핫 리로드 지원</li>
 * </ul>
 * 
 * <h2>모드 생명주기</h2>
 * <ol>
 * <li>Discovery - mods/ 폴더에서 JAR 스캔</li>
 * <li>Metadata Loading - pulse.mod.json 파싱</li>
 * <li>Dependency Resolution - 토폴로지 정렬</li>
 * <li>Mixin Registration - Mixin 설정 등록</li>
 * <li>Initialization - {@code PulseMod.onInitialize()} 호출</li>
 * </ol>
 * 
 * @since 1.0
 */
package com.pulse.mod;
