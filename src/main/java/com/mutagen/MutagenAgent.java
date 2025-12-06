package com.mutagen;

import com.mutagen.transformer.MutagenClassTransformer;
import org.spongepowered.asm.launch.MixinBootstrap;
import org.spongepowered.asm.mixin.MixinEnvironment;
import org.spongepowered.asm.mixin.Mixins;
import org.spongepowered.asm.mixin.transformer.IMixinTransformer;

import java.lang.instrument.Instrumentation;

/**
 * Mutagen Java Agent Entry Point.
 * 
 * JVM 시작 시 -javaagent:Mutagen.jar 옵션으로 로드됨.
 * 
 * 초기화 순서:
 * 1. Instrumentation 저장
 * 2. 시스템 프로퍼티 설정
 * 3. Mixin 부트스트랩
 * 4. Mixin config 등록
 * 5. Class transformer 등록
 */
public class MutagenAgent {

    private static Instrumentation instrumentation;
    private static MutagenClassTransformer classTransformer;

    public static void premain(String agentArgs, Instrumentation inst) {
        instrumentation = inst;
        MutagenEnvironment.setInstrumentation(inst);

        System.out.println();
        System.out.println("╔══════════════════════════════════════════════════════════════╗");
        System.out.println("║              MUTAGEN MOD LOADER v1.0.0                       ║");
        System.out.println("║          Project Zomboid Modding Platform                    ║");
        System.out.println("╚══════════════════════════════════════════════════════════════╝");
        System.out.println();

        try {
            initializeMutagen(inst);
        } catch (Throwable t) {
            System.err.println("[Mutagen] ════════════════════════════════════════");
            System.err.println("[Mutagen] CRITICAL INITIALIZATION ERROR");
            System.err.println("[Mutagen] ════════════════════════════════════════");
            t.printStackTrace();
        }
    }

    private static void initializeMutagen(Instrumentation inst) {
        // ─────────────────────────────────────────────────────────────
        // STEP 1: 시스템 프로퍼티 설정 (Mixin 부트스트랩 전에!)
        // ─────────────────────────────────────────────────────────────
        System.out.println("[Mutagen] Step 1: Configuring system properties...");

        // Mixin 디버그 활성화
        System.setProperty("mixin.debug", "true");
        System.setProperty("mixin.debug.verbose", "true");
        System.setProperty("mixin.debug.export", "true");
        System.setProperty("mixin.debug.export.decompile", "false");
        System.setProperty("mixin.dumpTargetOnFailure", "true");
        System.setProperty("mixin.checks", "true");
        System.setProperty("mixin.hotSwap", "true");

        // Mixin 서비스 지정 (선택사항 - ServiceLoader가 자동 발견함)
        // System.setProperty("mixin.service",
        // "com.mutagen.service.MutagenMixinService");

        System.out.println("[Mutagen] Step 1: Complete");

        // ─────────────────────────────────────────────────────────────
        // STEP 2: Mixin 부트스트랩
        // ─────────────────────────────────────────────────────────────
        System.out.println("[Mutagen] Step 2: Bootstrapping Mixin subsystem...");

        MixinBootstrap.init();

        // 부트스트랩 직후 phase 확인
        MixinEnvironment env = MixinEnvironment.getDefaultEnvironment();
        System.out.println("[Mutagen]   - Default Environment: " + env);
        System.out.println("[Mutagen]   - Side: " + env.getSide());
        System.out.println("[Mutagen]   - Phase (after init): " + env.getPhase());

        // Phase가 DEFAULT면 config 등록이 안 될 수 있음
        // gotoPhase로 PREINIT 상태로 되돌리기 시도
        try {
            var currentPhase = env.getPhase();
            System.out.println("[Mutagen]   - Current phase: " + currentPhase);
            System.out.println("[Mutagen]   - Attempting to check/set phase for config registration...");

            // MixinEnvironment.Phase.PREINIT 또는 INIT에서만 config 등록 가능
            // Reflection으로 phase 상태 확인
            var phaseField = MixinEnvironment.class.getDeclaredField("currentPhase");
            phaseField.setAccessible(true);
            System.out.println("[Mutagen]   - Internal currentPhase: " + phaseField.get(null));
        } catch (Exception e) {
            System.out.println("[Mutagen]   - Could not inspect phase field: " + e.getMessage());
        }

        System.out.println("[Mutagen] Step 2: Complete");

        // ─────────────────────────────────────────────────────────────
        // STEP 2.5: Mixin 내부 상태 확인
        // ─────────────────────────────────────────────────────────────
        System.out.println("[Mutagen] Step 2.5: Checking Mixin internal state...");
        try {
            // MixinEnvironment 상태
            var mixinEnv = MixinEnvironment.getDefaultEnvironment();
            System.out.println("[Mutagen]   - Environment: " + mixinEnv);
            System.out.println("[Mutagen]   - Phase: " + mixinEnv.getPhase());
            System.out.println("[Mutagen]   - Side: " + mixinEnv.getSide());

            // Mixin Service 확인
            var service = org.spongepowered.asm.service.MixinService.getService();
            System.out.println("[Mutagen]   - Active Service: " + service.getName());
            System.out.println("[Mutagen]   - Service Class: " + service.getClass().getName());

            // 리소스 로딩 테스트
            var testStream = service.getResourceAsStream("mixins.mutagen.json");
            System.out
                    .println("[Mutagen]   - Service.getResourceAsStream(): " + (testStream != null ? "OK" : "FAILED"));
            if (testStream != null) {
                // 내용 읽어보기
                byte[] bytes = testStream.readAllBytes();
                System.out.println("[Mutagen]   - Config file size: " + bytes.length + " bytes");
                System.out.println(
                        "[Mutagen]   - Config content preview: " + new String(bytes, 0, Math.min(200, bytes.length)));
                testStream.close();
            }
        } catch (Throwable t) {
            System.err.println("[Mutagen]   - Error checking state: " + t.getMessage());
            t.printStackTrace();
        }

        // ─────────────────────────────────────────────────────────────
        // STEP 3: Mixin Config 등록
        // ─────────────────────────────────────────────────────────────
        System.out.println("[Mutagen] Step 3: Registering Mixin configurations...");

        // Config 파일 존재 확인
        try {
            var configStream = MutagenAgent.class.getClassLoader().getResourceAsStream("mixins.mutagen.json");
            if (configStream != null) {
                System.out.println("[Mutagen]   - Found: mixins.mutagen.json");
                configStream.close();
            } else {
                System.err.println("[Mutagen]   - WARNING: mixins.mutagen.json not found in classpath!");
            }
        } catch (Exception e) {
            System.err.println("[Mutagen]   - Error checking config file: " + e.getMessage());
        }

        try {
            System.out.println("[Mutagen]   - Calling Mixins.addConfiguration()...");

            // 먼저 현재 등록된 config 수 확인
            int beforeCount = Mixins.getConfigs().size();
            System.out.println("[Mutagen]   - Configs before: " + beforeCount);

            Mixins.addConfiguration("mixins.mutagen.json");

            int afterCount = Mixins.getConfigs().size();
            System.out.println("[Mutagen]   - Configs after: " + afterCount);

            if (afterCount == beforeCount) {
                System.err.println("[Mutagen]   - WARNING: Config was not added! Trying alternative method...");

                // 대안: MixinConfig.create()를 직접 호출 시도
                try {
                    Class<?> mixinConfigClass = Class.forName("org.spongepowered.asm.mixin.transformer.MixinConfig");
                    var createMethod = mixinConfigClass.getDeclaredMethod("create", String.class,
                            MixinEnvironment.class);
                    createMethod.setAccessible(true);

                    var config = createMethod.invoke(null, "mixins.mutagen.json",
                            MixinEnvironment.getDefaultEnvironment());
                    System.out.println("[Mutagen]   - Direct MixinConfig.create() result: " + config);

                    if (config != null) {
                        // MixinProcessor나 관련 클래스에 직접 등록 시도
                        System.out.println("[Mutagen]   - Config created successfully: " + config);
                    }
                } catch (Exception ex) {
                    System.err.println("[Mutagen]   - Alternative method failed: " + ex.getMessage());
                    ex.printStackTrace();
                }
            }

            System.out.println("[Mutagen]   - addConfiguration() completed");
        } catch (Throwable t) {
            System.err.println("[Mutagen]   - ERROR in addConfiguration(): " + t.getClass().getName());
            System.err.println("[Mutagen]   - Message: " + t.getMessage());
            t.printStackTrace();
        }

        // 등록된 config 수 확인
        try {
            System.out.println("[Mutagen]   - Calling Mixins.getConfigs()...");
            var configs = Mixins.getConfigs();
            System.out.println("[Mutagen]   - Registered configs: " + (configs != null ? configs.size() : "null"));

            if (configs != null) {
                for (var config : configs) {
                    System.out.println("[Mutagen]   - Config: " + config);
                }
            }
        } catch (Throwable t) {
            System.err.println("[Mutagen]   - ERROR in getConfigs(): " + t.getClass().getName());
            System.err.println("[Mutagen]   - Message: " + t.getMessage());
            t.printStackTrace();
        }

        System.out.println("[Mutagen] Step 3: Complete");

        // ─────────────────────────────────────────────────────────────
        // STEP 4: Mixin Transformer 획득 대기
        // ─────────────────────────────────────────────────────────────
        System.out.println("[Mutagen] Step 4: Waiting for Mixin transformer...");

        // MutagenMixinService.offer()가 호출되면 transformer가 설정됨
        // 짧은 대기 후 확인
        IMixinTransformer mixinTransformer = null;

        for (int i = 0; i < 10; i++) {
            mixinTransformer = MutagenEnvironment.getMixinTransformer();
            if (mixinTransformer != null) {
                break;
            }
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                break;
            }
        }

        if (mixinTransformer != null) {
            System.out.println("[Mutagen]   - Mixin Transformer acquired: " +
                    mixinTransformer.getClass().getName());
        } else {
            System.err.println("[Mutagen]   - WARNING: Mixin Transformer not available!");
            System.err.println("[Mutagen]   - Mixins may not be applied correctly.");
        }

        System.out.println("[Mutagen] Step 4: Complete");

        // ─────────────────────────────────────────────────────────────
        // STEP 5: Class Transformer 등록
        // ─────────────────────────────────────────────────────────────
        System.out.println("[Mutagen] Step 5: Registering class transformer...");

        classTransformer = new MutagenClassTransformer();

        // Mixin transformer 연결
        if (mixinTransformer != null) {
            classTransformer.connectMixinTransformer(mixinTransformer);
        }

        // Instrumentation에 등록 (canRetransform=true)
        inst.addTransformer(classTransformer, true);

        System.out.println("[Mutagen]   - Transformer registered with Instrumentation");
        System.out.println("[Mutagen] Step 5: Complete");

        // ─────────────────────────────────────────────────────────────
        // STEP 6: 초기화 완료
        // ─────────────────────────────────────────────────────────────
        MutagenEnvironment.markInitialized();

        System.out.println();
        System.out.println("[Mutagen] ════════════════════════════════════════════════════");
        System.out.println("[Mutagen] CORE INITIALIZATION COMPLETE");
        System.out.println("[Mutagen] ════════════════════════════════════════════════════");
        System.out.println();

        // ─────────────────────────────────────────────────────────────
        // STEP 7: 모드 로더 초기화
        // ─────────────────────────────────────────────────────────────
        System.out.println("[Mutagen] Step 7: Initializing mod loader...");

        try {
            com.mutagen.mod.ModLoader modLoader = com.mutagen.mod.ModLoader.getInstance();

            // 모드 발견
            modLoader.discoverMods();

            // 의존성 해결
            modLoader.resolveDependencies();

            // 모드 Mixin 등록
            modLoader.registerMixins();

            System.out.println("[Mutagen] Step 7: Complete");
        } catch (Throwable t) {
            System.err.println("[Mutagen] Step 7: Mod loader error (non-fatal)");
            t.printStackTrace();
        }

        System.out.println();
        System.out.println("[Mutagen] ════════════════════════════════════════════════════");
        System.out.println("[Mutagen] MUTAGEN FULLY INITIALIZED");
        System.out.println("[Mutagen] Waiting for zombie.* classes to load...");
        System.out.println("[Mutagen] ════════════════════════════════════════════════════");
        System.out.println();

        // 환경 상태 출력
        MutagenEnvironment.printStatus();

        // 디버그: 지연 체크
        startDebugMonitor();
    }

    /**
     * 디버그용 모니터링 스레드
     * 첫 zombie 클래스 로딩과 mixin 적용을 확인
     */
    private static void startDebugMonitor() {
        new Thread(() -> {
            System.out.println("[Mutagen/Debug] Monitor thread started");

            // 게임 클래스 로더가 등록될 때까지 대기
            int waitCount = 0;
            while (MutagenEnvironment.getGameClassLoader() == null && waitCount < 300) {
                try {
                    Thread.sleep(100);
                    waitCount++;
                } catch (InterruptedException e) {
                    break;
                }
            }

            if (MutagenEnvironment.getGameClassLoader() != null) {
                System.out.println("[Mutagen/Debug] Game ClassLoader detected after " +
                        (waitCount * 100) + "ms");
                System.out.println("[Mutagen/Debug] ClassLoader: " +
                        MutagenEnvironment.getGameClassLoader());

                // 모드 초기화 (게임 클래스 로더 감지 후)
                try {
                    System.out.println("[Mutagen/Debug] Initializing mods...");
                    com.mutagen.mod.ModLoader.getInstance().initializeMods();
                } catch (Throwable t) {
                    System.err.println("[Mutagen/Debug] Mod initialization error:");
                    t.printStackTrace();
                }
            } else {
                System.err.println("[Mutagen/Debug] WARNING: Game ClassLoader not detected after 30s");
            }

            // Mixin 적용 상태 확인
            if (classTransformer != null) {
                try {
                    Thread.sleep(5000); // 5초 더 대기
                    var transformed = classTransformer.getTransformedClasses();
                    System.out.println("[Mutagen/Debug] Transformed classes: " + transformed.size());
                    for (String cls : transformed) {
                        System.out.println("[Mutagen/Debug]   - " + cls);
                    }
                } catch (InterruptedException e) {
                    // ignore
                }
            }
        }, "Mutagen-Debug-Monitor").start();
    }

    public static Instrumentation getInstrumentation() {
        return instrumentation;
    }

    public static MutagenClassTransformer getClassTransformer() {
        return classTransformer;
    }
}
