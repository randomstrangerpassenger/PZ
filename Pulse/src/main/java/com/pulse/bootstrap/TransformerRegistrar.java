package com.pulse.bootstrap;

import com.pulse.PulseEnvironment;
import com.pulse.api.log.PulseLogger;
import com.pulse.transformer.PulseClassTransformer;
import org.spongepowered.asm.mixin.transformer.IMixinTransformer;

import java.lang.instrument.Instrumentation;

/**
 * Step 4 & 5: Obtain Mixin Transformer and register PulseClassTransformer.
 */
public class TransformerRegistrar {
    private static final String LOG = PulseLogger.PULSE;

    public PulseClassTransformer initialize(InitializationContext context) {
        PulseLogger.info(LOG, "Step 4: Waiting for Mixin transformer...");

        IMixinTransformer mixinTransformer = waitForMixinTransformer();

        if (mixinTransformer != null) {
            PulseLogger.info(LOG, "  - Mixin Transformer acquired: {}",
                    mixinTransformer.getClass().getName());
        } else {
            PulseLogger.warn(LOG, "  - WARNING: Mixin Transformer not available!");
            PulseLogger.warn(LOG, "  - Mixins may not be applied correctly.");
        }

        PulseLogger.info(LOG, "Step 4: Complete");

        return registerClassTransformer(context.getInstrumentation(), mixinTransformer);
    }

    private IMixinTransformer waitForMixinTransformer() {
        IMixinTransformer mixinTransformer = null;
        for (int i = 0; i < 10; i++) {
            mixinTransformer = PulseEnvironment.getMixinTransformer();
            if (mixinTransformer != null) {
                break;
            }
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                break;
            }
        }
        return mixinTransformer;
    }

    private PulseClassTransformer registerClassTransformer(Instrumentation inst, IMixinTransformer mixinTransformer) {
        PulseLogger.info(LOG, "Step 5: Registering class transformer...");

        PulseClassTransformer classTransformer = new PulseClassTransformer();

        if (mixinTransformer != null) {
            classTransformer.connectMixinTransformer(mixinTransformer);
        }

        inst.addTransformer(classTransformer, true);

        PulseLogger.info(LOG, "  - Transformer registered with Instrumentation");
        PulseLogger.info(LOG, "Step 5: Complete");

        return classTransformer;
    }
}
