package com.pulse.service;

import com.pulse.api.log.PulseLogger;
import com.pulse.PulseEnvironment;
import org.spongepowered.asm.launch.platform.container.ContainerHandleVirtual;
import org.spongepowered.asm.launch.platform.container.IContainerHandle;
import org.spongepowered.asm.logging.ILogger;
import org.spongepowered.asm.mixin.MixinEnvironment.CompatibilityLevel;
import org.spongepowered.asm.mixin.MixinEnvironment.Phase;
import org.spongepowered.asm.mixin.transformer.IMixinTransformer;
import org.spongepowered.asm.mixin.transformer.IMixinTransformerFactory;
import org.spongepowered.asm.service.*;
import org.spongepowered.asm.util.ReEntranceLock;

import org.objectweb.asm.ClassReader;
import org.objectweb.asm.tree.ClassNode;

import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.util.Collection;
import java.util.Collections;

/**
 * Pulse의 핵심 Mixin 서비스 구현.
 * 
 * Sponge Mixin이 필요로 하는 모든 인터페이스를 구현:
 * - IMixinService: 메인 서비스 인터페이스
 * - IClassProvider: 클래스 로딩
 * - IClassBytecodeProvider: 바이트코드 접근
 */
public class PulseMixinService implements IMixinService, IClassProvider, IClassBytecodeProvider {

    private static final String LOG = PulseLogger.PULSE;

    private final ReEntranceLock lock = new ReEntranceLock(1);
    private final PulseTransformerProvider transformerProvider = new PulseTransformerProvider();
    private final PulseClassTracker classTracker = new PulseClassTracker();

    // Mixin이 생성한 transformer (offer()를 통해 전달됨)
    private IMixinTransformer mixinTransformer;
    private IMixinTransformerFactory transformerFactory;

    // Primary container (이 JAR 자체)
    private IContainerHandle primaryContainer;

    public PulseMixinService() {
        PulseLogger.debug(LOG, "PulseMixinService instantiated");
    }

    // --- ClassLoader Management ---

    private ClassLoader getEffectiveClassLoader() {
        // 1순위: 게임 클래스 로더
        ClassLoader gameLoader = PulseEnvironment.getGameClassLoader();
        if (gameLoader != null) {
            return gameLoader;
        }

        // 2순위: 현재 컨텍스트 클래스 로더
        ClassLoader contextLoader = Thread.currentThread().getContextClassLoader();
        if (contextLoader != null) {
            return contextLoader;
        }

        // 3순위: 시스템 클래스 로더
        return ClassLoader.getSystemClassLoader();
    }

    // --- IMixinService ---

    @Override
    public String getName() {
        return "Pulse";
    }

    @Override
    public boolean isValid() {
        return true;
    }

    @Override
    public void prepare() {
        PulseLogger.debug(LOG, "prepare() called");
    }

    @Override
    public Phase getInitialPhase() {
        // Mixin 0.8.7: Return DEFAULT phase to ensure environment is fully initialized
        // PREINIT phase causes "this.env is null" errors in MixinConfig.onLoad()
        return Phase.DEFAULT;
    }

    @Override
    public void offer(IMixinInternal internal) {
        PulseLogger.debug(LOG, "offer() called with: {}",
                (internal != null ? internal.getClass().getName() : "null"));

        if (internal instanceof IMixinTransformerFactory) {
            this.transformerFactory = (IMixinTransformerFactory) internal;
            PulseLogger.info(LOG, "Received IMixinTransformerFactory");

            // Transformer 생성
            try {
                this.mixinTransformer = transformerFactory.createTransformer();
                PulseLogger.info(LOG, "Created IMixinTransformer: {}",
                        (mixinTransformer != null ? mixinTransformer.getClass().getName() : "null"));

                // PulseEnvironment에 저장하여 외부에서 접근 가능하게 함
                PulseEnvironment.setMixinTransformer(mixinTransformer);

            } catch (Exception e) {
                PulseLogger.error(LOG, "Failed to create transformer: {}", e.getMessage());
                e.printStackTrace();
            }
        }
    }

    @Override
    public void init() {
        PulseLogger.debug(LOG, "init() called");
    }

    @Override
    public void beginPhase() {
        PulseLogger.debug(LOG, "beginPhase() called");
    }

    @Override
    public void checkEnv(Object bootSource) {
        PulseLogger.debug(LOG, "checkEnv() called");
    }

    @Override
    public ReEntranceLock getReEntranceLock() {
        return this.lock;
    }

    @Override
    public IClassProvider getClassProvider() {
        return this;
    }

    @Override
    public IClassBytecodeProvider getBytecodeProvider() {
        return this;
    }

    @Override
    public ITransformerProvider getTransformerProvider() {
        return this.transformerProvider;
    }

    @Override
    public IClassTracker getClassTracker() {
        return this.classTracker;
    }

    @Override
    public IMixinAuditTrail getAuditTrail() {
        // 감사 추적은 선택사항
        return null;
    }

    @Override
    public Collection<String> getPlatformAgents() {
        // Platform agent 클래스 이름들
        // 필요시 PulsePlatformAgent 구현 가능
        return Collections.singletonList("com.pulse.service.PulsePlatformAgent");
    }

    @Override
    public String getSideName() {
        return "CLIENT";
    }

    @Override
    public IContainerHandle getPrimaryContainer() {
        if (primaryContainer == null) {
            try {
                // 이 클래스가 포함된 JAR/폴더의 위치
                URL location = getClass().getProtectionDomain().getCodeSource().getLocation();
                primaryContainer = new ContainerHandleVirtual(getName());
                PulseLogger.debug(LOG, "Primary container location: {}", location);
            } catch (Exception e) {
                primaryContainer = new ContainerHandleVirtual(getName());
            }
        }
        return primaryContainer;
    }

    @Override
    public Collection<IContainerHandle> getMixinContainers() {
        // Mixin config를 포함하는 컨테이너들
        // 현재는 primary container만 반환
        return Collections.singletonList(getPrimaryContainer());
    }

    @Override
    public InputStream getResourceAsStream(String name) {
        PulseLogger.trace(LOG, "getResourceAsStream() called for: {}", name);

        ClassLoader cl = getEffectiveClassLoader();
        PulseLogger.trace(LOG, "  - Using ClassLoader: {}", cl.getClass().getName());

        // 여러 경로 시도
        InputStream is = cl.getResourceAsStream(name);
        PulseLogger.trace(LOG, "  - Try 1 (direct): {}", (is != null ? "FOUND" : "not found"));

        if (is == null) {
            // 슬래시로 시작하는 경로 시도
            is = cl.getResourceAsStream("/" + name);
            PulseLogger.trace(LOG, "  - Try 2 (with /): {}", (is != null ? "FOUND" : "not found"));
        }

        if (is == null) {
            // 이 클래스의 클래스로더에서 시도
            is = getClass().getClassLoader().getResourceAsStream(name);
            PulseLogger.trace(LOG, "  - Try 3 (service classloader): {}", (is != null ? "FOUND" : "not found"));
        }

        if (is == null) {
            // 시스템 클래스로더에서 시도
            is = ClassLoader.getSystemClassLoader().getResourceAsStream(name);
            PulseLogger.trace(LOG, "  - Try 4 (system classloader): {}", (is != null ? "FOUND" : "not found"));
        }

        if (is == null) {
            PulseLogger.warn(LOG, "  - FAILED to find resource: {}", name);
        } else {
            PulseLogger.trace(LOG, "  - SUCCESS: Found resource: {}", name);
        }

        return is;
    }

    @Override
    public CompatibilityLevel getMinCompatibilityLevel() {
        return CompatibilityLevel.JAVA_8;
    }

    @Override
    public CompatibilityLevel getMaxCompatibilityLevel() {
        return CompatibilityLevel.JAVA_17;
    }

    @Override
    public ILogger getLogger(String name) {
        return new MixinLogger(name);
    }

    // --- IClassProvider ---

    @Override
    public Class<?> findClass(String name) throws ClassNotFoundException {
        return findClass(name, true);
    }

    @Override
    public Class<?> findClass(String name, boolean initialize) throws ClassNotFoundException {
        classTracker.registerClass(name);
        return Class.forName(name, initialize, getEffectiveClassLoader());
    }

    @Override
    public Class<?> findAgentClass(String name, boolean initialize) throws ClassNotFoundException {
        // Agent 클래스는 시스템 클래스로더에서 로드
        return Class.forName(name, initialize, ClassLoader.getSystemClassLoader());
    }

    @Override
    public URL[] getClassPath() {
        // 클래스패스 URL 배열 반환
        // Java 9+에서는 모듈 시스템 때문에 복잡해질 수 있음
        return new URL[0];
    }

    // --- IClassBytecodeProvider ---

    @Override
    public ClassNode getClassNode(String name) throws ClassNotFoundException, IOException {
        return getClassNode(name, true);
    }

    @Override
    public ClassNode getClassNode(String name, boolean runTransformers)
            throws ClassNotFoundException, IOException {
        String resourceName = name.replace('.', '/') + ".class";
        InputStream is = getResourceAsStream(resourceName);

        if (is == null) {
            throw new ClassNotFoundException("Cannot find class bytecode: " + name +
                    " (resource: " + resourceName + ")");
        }

        try {
            ClassReader reader = new ClassReader(is);
            ClassNode node = new ClassNode();
            reader.accept(node, ClassReader.EXPAND_FRAMES);
            return node;
        } finally {
            is.close();
        }
    }

    // --- Pulse Methods ---

    /**
     * Mixin transformer 반환 (PulseClassTransformer에서 사용)
     */
    public IMixinTransformer getMixinTransformer() {
        return this.mixinTransformer;
    }

    /**
     * ClassTracker 반환 (디버깅/모니터링용)
     */
    public PulseClassTracker getClassTrackerInstance() {
        return this.classTracker;
    }
}
