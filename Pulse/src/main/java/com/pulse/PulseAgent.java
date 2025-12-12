package com.pulse;

import com.pulse.api.log.PulseLogger;
import com.pulse.bootstrap.*;
import com.pulse.transformer.PulseClassTransformer;

import java.lang.instrument.Instrumentation;

/**
 * Pulse Java Agent Entry Point.
 * 
 * JVM 시작 시 -javaagent:Pulse.jar 옵션으로 로드됨.
 * 
 * 초기화 순서:
 * 1. Instrumentation 저장
 * 2. 시스템 프로퍼티 설정
 * 3. Mixin 부트스트랩
 * 4. Mixin config 등록
 * 5. Class transformer 등록
 */
public class PulseAgent {

    private static final String LOG = PulseLogger.PULSE;
    private static Instrumentation instrumentation;
    private static PulseClassTransformer classTransformer;

    public static void premain(String agentArgs, Instrumentation inst) {
        instrumentation = inst;
        PulseEnvironment.setInstrumentation(inst);

        PulseLogger.info(LOG, "");
        PulseLogger.info(LOG, "╔══════════════════════════════════════════════════════════════╗");
        PulseLogger.info(LOG, "║              Pulse MOD LOADER v1.0.0                       ║");
        PulseLogger.info(LOG, "║          Project Zomboid Modding Platform                    ║");
        PulseLogger.info(LOG, "╚══════════════════════════════════════════════════════════════╝");
        PulseLogger.info(LOG, "");

        try {
            initializePulse(inst);
        } catch (Throwable t) {
            PulseLogger.error(LOG, "════════════════════════════════════════");
            PulseLogger.error(LOG, "CRITICAL INITIALIZATION ERROR");
            PulseLogger.error(LOG, "════════════════════════════════════════");
            t.printStackTrace();
        }
    }

    private static void initializePulse(Instrumentation inst) {
        InitializationContext ctx = new InitializationContext(inst);

        // 1. System Properties
        new SystemPropertyInitializer().initialize(ctx);

        // 2. Bootstrap Loader (Mixin)
        new BootstrapLoader().initialize(ctx);

        // 3. Config Registrar
        new ConfigRegistrar().initialize(ctx);

        // 4 & 5. Transformer Registrar
        classTransformer = new TransformerRegistrar().initialize(ctx);

        // 6. Complete Initialization
        PulseEnvironment.markInitialized();

        // 6.5. Optimization Extensions
        new OptimizationInitializer().initialize(ctx);

        PulseLogger.info(LOG, "");
        PulseLogger.info(LOG, "════════════════════════════════════════════════════");
        PulseLogger.info(LOG, "CORE INITIALIZATION COMPLETE");
        PulseLogger.info(LOG, "════════════════════════════════════════════════════");
        PulseLogger.info(LOG, "");

        // 7. Mod Loader (Discovery & Mixins)
        new ModInitializer().initialize(ctx);

        PulseLogger.info(LOG, "");
        PulseLogger.info(LOG, "════════════════════════════════════════════════════");
        PulseLogger.info(LOG, "Pulse FULLY INITIALIZED");
        PulseLogger.info(LOG, "Waiting for zombie.* classes to load...");
        PulseLogger.info(LOG, "════════════════════════════════════════════════════");
        PulseLogger.info(LOG, "");

        PulseEnvironment.printStatus();

        // Start Debug Monitor
        new DebugMonitorFactory().startMonitor(classTransformer);
    }

    public static Instrumentation getInstrumentation() {
        return instrumentation;
    }

    public static PulseClassTransformer getClassTransformer() {
        return classTransformer;
    }
}
