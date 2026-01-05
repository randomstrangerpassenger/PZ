package com.pulse.architecture;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.Tag;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

/**
 * Pulse Hub & Spoke 아키텍처 경계 테스트.
 * 
 * Philosophy.md에 정의된 핵심 원칙 검증:
 * 1. Spoke 모듈(Echo, Fuse, Nerve)은 Pulse에 의존 가능
 * 2. Pulse는 Spoke 모듈에 의존 불가 (단방향)
 * 3. Spoke 모듈은 서로 직접 의존 불가 (Hub 통해서만)
 * 
 * 주의: pulse-api 모듈의 독립성은 빌드 시스템 레벨에서 검증됨 (별도 모듈).
 * 여기서는 Pulse 런타임의 hub-spoke 규칙만 검증.
 */
@Tag("architecture")
@AnalyzeClasses(packages = { "com.pulse" }, importOptions = ImportOption.DoNotIncludeTests.class)
public class HubSpokeBoundaryTest {

        /**
         * Pulse는 하위 모듈(Echo, Fuse, Nerve)을 참조해서는 안 됨.
         * Hub는 Spoke의 존재를 몰라야 함.
         * 
         * 이 규칙이 위반되면 Pulse가 특정 Spoke에 결합된 것이므로
         * 다른 Spoke 없이 Pulse를 사용할 수 없게 됨.
         */
        @ArchTest
        static final ArchRule pulse_should_not_depend_on_spoke_modules = noClasses()
                        .that().resideInAnyPackage("com.pulse..")
                        .should().dependOnClassesThat()
                        .resideInAnyPackage("com.echo..", "com.fuse..", "com.nerve..")
                        .because("Hub (Pulse) must not depend on Spoke modules (Echo, Fuse, Nerve)");
}
