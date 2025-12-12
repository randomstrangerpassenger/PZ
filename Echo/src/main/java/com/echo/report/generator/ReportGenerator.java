package com.echo.report.generator;

import java.util.Map;

/**
 * 리포트 생성 전략 인터페이스.
 * EchoReport에서 분리된 포맷별 리포트 생성기.
 * 
 * @since 1.1.0
 */
public interface ReportGenerator {

    /**
     * 리포트 생성.
     * 
     * @param data 리포트 데이터 (key-value)
     * @return 생성된 리포트 문자열
     */
    String generate(Map<String, Object> data);

    /**
     * 리포트 포맷 이름.
     */
    String getFormatName();

    /**
     * 파일 확장자.
     */
    String getFileExtension();
}
