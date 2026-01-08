package com.pulse.api.spi;

import java.util.Map;

/**
 * Stabilizer Snapshot Provider SPI.
 * 안정화 모듈(Fuse, Nerve 등)이 리포트 시점에 스냅샷을 제공하는 계약.
 * 
 * <h3>계약 조건</h3>
 * <ul>
 * <li>captureSnapshot()은 절대 throw 금지 (no-throw)</li>
 * <li>리포트 생성 시점 1회 호출 전제</li>
 * <li>반환 데이터는 primitive/Map only (직렬화 안정)</li>
 * </ul>
 * 
 * <h3>필수 키 (Provider 책임)</h3>
 * <ul>
 * <li>active: boolean - 기능 활성화 여부</li>
 * <li>snapshot_ok: boolean - 스냅샷 성공 여부</li>
 * <li>error_code: String - 실패 시 표준 코드</li>
 * <li>total_interventions: long - 총 개입 횟수</li>
 * <li>reason_counts: Map&lt;String, Long&gt; - 이유별 카운트</li>
 * </ul>
 * 
 * <h3>필드 책임 규약</h3>
 * <p>
 * <b>present 필드는 Echo가 결정합니다.</b> Provider는 이 키를 반환하면 안 됩니다.
 * </p>
 * 
 * <h3>isEnabled() 규약</h3>
 * <p>
 * 항상 true를 반환해야 합니다. 기능 ON/OFF는 active 필드로 표현합니다.
 * </p>
 * 
 * @since Pulse 1.1
 */
public interface IStabilizerSnapshotProvider extends IProvider {

    /**
     * Provider 상태 열거형.
     * <ul>
     * <li>ACTIVE: 기능 ON, 정상 동작 중</li>
     * <li>INACTIVE: 설치됨, 기능 OFF</li>
     * <li>FAILED: 초기화/등록 실패</li>
     * </ul>
     */
    enum ProviderStatus {
        ACTIVE,
        INACTIVE,
        FAILED
    }

    /**
     * 현재 provider 상태 반환.
     * Echo는 이 값을 snapshot의 provider_status로 기록합니다.
     * 
     * @return 현재 상태
     */
    ProviderStatus getProviderStatus();

    /**
     * 스냅샷 캡처 (no-throw 계약).
     * 
     * <p>
     * 실패 시에도 예외를 던지지 말고, Map에 다음을 포함해야 합니다:
     * </p>
     * <ul>
     * <li>snapshot_ok: false</li>
     * <li>error_code: 표준 코드 (SNAPSHOT_THROWN 등)</li>
     * </ul>
     * 
     * <p>
     * <b>주의:</b> "present" 키를 넣지 마세요. Echo가 결정합니다.
     * </p>
     * 
     * @return 스냅샷 데이터 (null 시 Echo가 SNAPSHOT_NULL로 처리)
     */
    Map<String, Object> captureSnapshot();

    /**
     * isEnabled()는 항상 true를 반환합니다.
     * INACTIVE/FAILED 상태도 리포트에 기록되어야 "0 분해"가 가능합니다.
     * 기능 ON/OFF는 snapshot의 active 필드로 표현합니다.
     * 
     * @return 항상 true
     */
    @Override
    default boolean isEnabled() {
        return true;
    }
}
