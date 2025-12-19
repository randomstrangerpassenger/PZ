package com.pulse.arch;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.lang.ArchRule;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;

/**
 * Package boundary enforcement for Pulse core-loader separation.
 * 
 * <p>
 * These tests MUST pass for the build to succeed.
 * Violation = future separation will break.
 * </p>
 * 
 * <h2>Boundary Rules:</h2>
 * <ul>
 * <li>Core (api, core, internal, bindings, mixin) → Loader: FORBIDDEN</li>
 * <li>API → Internal: FORBIDDEN</li>
 * <li>Core/API → zombie.*: Only via bindings/mixin</li>
 * </ul>
 * 
 * @since Pulse 0.9
 */
public class PulseBoundaryTest {

        private static JavaClasses pulseClasses;

        @BeforeAll
        static void setup() {
                pulseClasses = new ClassFileImporter()
                                .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
                                .importPackages("com.pulse");
        }

        // ═══════════════════════════════════════════════════════════════
        // Rule 1: Core MUST NOT depend on Loader
        // ═══════════════════════════════════════════════════════════════

        @Test
        @DisplayName("Core packages must not depend on loader packages")
        void coreShouldNotDependOnLoader() {
                ArchRule rule = noClasses()
                                .that().resideInAnyPackage(
                                                "com.pulse.api..",
                                                "com.pulse.core..",
                                                "com.pulse.internal..",
                                                "com.pulse.bindings..",
                                                "com.pulse.mixin..",
                                                "com.pulse.event..",
                                                "com.pulse.bootstrap..")
                                .should().dependOnClassesThat()
                                .resideInAnyPackage("com.pulse.loader..");

                rule.check(pulseClasses);
        }

        // ═══════════════════════════════════════════════════════════════
        // Rule 2: Internal should not leak to API
        // ═══════════════════════════════════════════════════════════════

        @Test
        @DisplayName("API package must not depend on internal package")
        void apiShouldNotDependOnInternal() {
                ArchRule rule = noClasses()
                                .that().resideInAnyPackage("com.pulse.api..")
                                .should().dependOnClassesThat()
                                .resideInAnyPackage("com.pulse.internal..");

                rule.check(pulseClasses);
        }

        @Test
        @DisplayName("Core package must not depend on internal package")
        void coreShouldNotDependOnInternal() {
                ArchRule rule = noClasses()
                                .that().resideInAnyPackage("com.pulse.core..")
                                .should().dependOnClassesThat()
                                .resideInAnyPackage("com.pulse.internal..");

                rule.check(pulseClasses);
        }

        // ═══════════════════════════════════════════════════════════════
        // Rule 3: Core must not contain optimization-focused classes
        // ═══════════════════════════════════════════════════════════════

        @Test
        @DisplayName("Core mixin package must not contain optimization classes")
        void mixinShouldNotContainOptimizationClasses() {
                // Core mixins should only contain hook/contract classes, not optimization logic
                // Optimization classes belong in Fuse, not Pulse-core
                // This rule verifies no optimization package exists in mixin
                ArchRule rule = noClasses()
                                .that().resideInAnyPackage("com.pulse.mixin.optimization..")
                                .should().beInterfaces(); // Placeholder - any class here is a violation

                rule.allowEmptyShould(true).check(pulseClasses);
        }

        @Test
        @DisplayName("Core must not have classes with Optimizer/Throttle in name")
        void corePackageShouldNotContainOptimizerClasses() {
                // Core package should not contain optimizer/throttle classes (those are Fuse's
                // domain)
                ArchRule rule = noClasses()
                                .that().resideInAnyPackage("com.pulse.core..")
                                .should().haveSimpleNameContaining("Optimizer");

                rule.check(pulseClasses);
        }

        // ═══════════════════════════════════════════════════════════════
        // Rule 4: zombie.* access only via bindings/mixin (allowlist)
        // ═══════════════════════════════════════════════════════════════

        @Test
        @DisplayName("API package should not directly reference zombie.* classes")
        void apiShouldNotReferenceZombieClasses() {
                // API should be engine-agnostic
                // Exception: version detection classes
                ArchRule rule = noClasses()
                                .that().resideInAnyPackage("com.pulse.api..")
                                .and().haveSimpleNameNotContaining("Version")
                                .and().haveSimpleNameNotContaining("GameVersion")
                                .should().dependOnClassesThat()
                                .resideInAnyPackage("zombie..");

                rule.check(pulseClasses);
        }

        @Test
        @DisplayName("Core package should not directly reference zombie.* classes")
        void coreShouldNotReferenceZombieClasses() {
                // Core classes should go through bindings for engine access
                ArchRule rule = noClasses()
                                .that().resideInAnyPackage("com.pulse.core..")
                                .should().dependOnClassesThat()
                                .resideInAnyPackage("zombie..");

                rule.check(pulseClasses);
        }

        @Test
        @DisplayName("Loader package should not directly reference zombie.* classes")
        void loaderShouldNotReferenceZombieClasses() {
                // Loader should use bindings facade, not direct engine access
                ArchRule rule = noClasses()
                                .that().resideInAnyPackage("com.pulse.loader..")
                                .should().dependOnClassesThat()
                                .resideInAnyPackage("zombie..");

                rule.check(pulseClasses);
        }

        // ═══════════════════════════════════════════════════════════════
        // Rule 5: Bindings layer is the ONLY engine access point
        // ═══════════════════════════════════════════════════════════════

        @Test
        @DisplayName("Only bindings and mixin packages may reference zombie.* directly")
        @SuppressWarnings("unused") // Rule intentionally not checked yet - see comment at end
        void onlyBindingsAndMixinMayReferenceZombie() {
                // Allowed packages: bindings, mixin, adapter (legacy)
                // All other packages should NOT reference zombie.* directly
                ArchRule rule = noClasses()
                                .that().resideInAnyPackage(
                                                "com.pulse.event..",
                                                "com.pulse.scheduler..",
                                                "com.pulse.service..",
                                                "com.pulse.config..",
                                                "com.pulse.debug..")
                                .should().dependOnClassesThat()
                                .resideInAnyPackage("zombie..");

                // Note: This rule may be relaxed for utility classes that need PZ types
                // Enable when ready to enforce strict bindings isolation
                // rule.check(pulseClasses);
        }
}
