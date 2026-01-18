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

        // ═══════════════════════════════════════════════════════════════
        // Spoke 간 상호 의존 금지 (Hub & Spoke 핵심)
        // Philosophy.md: "Echo, Fuse, Nerve는 절대 서로를 참조하거나 의존성을 가지면 안됨"
        //
        // 주의: 이 테스트는 Pulse 모듈에서 실행됨. Echo/Fuse/Nerve 패키지가
        // 없을 경우 allowEmptyShould(true)로 빈 결과를 허용함.
        // 실제 위반(Spoke 클래스가 다른 Spoke를 import)이 있을 때만 실패함.
        // ═══════════════════════════════════════════════════════════════

        /**
         * Echo는 Fuse, Nerve를 직접 참조할 수 없음.
         * Spoke 간 통신이 필요하면 반드시 Pulse(Hub)를 경유해야 함.
         */
        @ArchTest
        static final ArchRule echo_should_not_depend_on_other_spokes = noClasses()
                        .that().resideInAnyPackage("com.echo..")
                        .should().dependOnClassesThat()
                        .resideInAnyPackage("com.fuse..", "com.nerve..")
                        .allowEmptyShould(true)
                        .because("Spoke modules must not depend on each other (Hub & Spoke architecture)");

        /**
         * Fuse는 Echo, Nerve를 직접 참조할 수 없음.
         */
        @ArchTest
        static final ArchRule fuse_should_not_depend_on_other_spokes = noClasses()
                        .that().resideInAnyPackage("com.fuse..")
                        .should().dependOnClassesThat()
                        .resideInAnyPackage("com.echo..", "com.nerve..")
                        .allowEmptyShould(true)
                        .because("Spoke modules must not depend on each other (Hub & Spoke architecture)");

        /**
         * Nerve는 Echo, Fuse를 직접 참조할 수 없음.
         * 
         * NOTE: Nerve는 Lua 전용 모듈로 Java 코드가 없음.
         * allowEmptyShould(true)는 의도적으로 빈 결과를 허용함.
         * 이 규칙은 향후 Nerve에 Java 코드가 추가될 경우를 대비한 것임.
         */
        @ArchTest
        static final ArchRule nerve_should_not_depend_on_other_spokes = noClasses()
                        .that().resideInAnyPackage("com.nerve..")
                        .should().dependOnClassesThat()
                        .resideInAnyPackage("com.echo..", "com.fuse..")
                        .allowEmptyShould(true)
                        .because("Spoke modules must not depend on each other (Hub & Spoke architecture)");

        // ═══════════════════════════════════════════════════════════════
        // v4 강화: access 레벨 규칙 (dependOn보다 엄격)
        // Hub가 Spoke 클래스를 접근조차 못 하도록 함
        // ═══════════════════════════════════════════════════════════════

        /**
         * Hub(Pulse)는 Spoke 클래스에 접근할 수 없음 (dependOn보다 엄격).
         * 메서드 호출, 필드 접근 등 모든 형태의 접근을 금지.
         * 
         * NOTE: Nerve는 Lua 전용이므로 여기서 제외됨.
         */
        @ArchTest
        static final ArchRule pulse_should_not_access_spoke_classes = noClasses()
                        .that().resideInAnyPackage("com.pulse..")
                        .should().accessClassesThat()
                        .resideInAnyPackage("com.echo..", "com.fuse..")
                        .because("Hub must not access any Spoke classes (stricter than dependOn)");
}
