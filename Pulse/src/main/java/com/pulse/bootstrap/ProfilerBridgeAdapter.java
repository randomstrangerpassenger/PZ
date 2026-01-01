package com.pulse.bootstrap;

import com.pulse.api.profiler.IProfilerBridge;
import com.pulse.api.profiler.IProfilerSink;
import com.pulse.api.profiler.ProfilerBridge;
import com.pulse.api.profiler.ProfilerSink;

/**
 * IProfilerBridge 어댑터.
 * ProfilerBridge 정적 메서드들을 IProfilerBridge 인터페이스에 연결.
 * 
 * @since Pulse 2.1
 */
public class ProfilerBridgeAdapter implements IProfilerBridge {

    private static final ProfilerBridgeAdapter INSTANCE = new ProfilerBridgeAdapter();
    private IProfilerSink currentSink;

    private ProfilerBridgeAdapter() {
    }

    public static ProfilerBridgeAdapter getInstance() {
        return INSTANCE;
    }

    @Override
    public void setSink(IProfilerSink sink) {
        this.currentSink = sink;
        if (sink != null) {
            // IProfilerSink를 ProfilerSink로 래핑
            ProfilerBridge.setSink(new ProfilerSinkWrapper(sink));
        } else {
            ProfilerBridge.clearSink();
        }
    }

    @Override
    public IProfilerSink getSink() {
        return currentSink;
    }

    @Override
    public void clearSink() {
        this.currentSink = null;
        ProfilerBridge.clearSink();
    }

    @Override
    public boolean hasSink() {
        return ProfilerBridge.hasSink();
    }

    /**
     * IProfilerSink를 ProfilerSink로 래핑하는 내부 클래스.
     * ProfilerSink는 Pulse Core의 인터페이스.
     */
    private static class ProfilerSinkWrapper implements ProfilerSink {
        private final IProfilerSink delegate;

        ProfilerSinkWrapper(IProfilerSink delegate) {
            this.delegate = delegate;
        }

        /**
         * Returns the wrapped delegate sink.
         */
        @SuppressWarnings("unused") // Part of public API for external use
        public IProfilerSink getDelegate() {
            return delegate;
        }

        @Override
        public void recordZombieStep(String step, long durationMicros) {
            // IProfilerSink에는 이 메서드가 없으므로 no-op
            // Echo의 EchoProfilerSink가 직접 ProfilerSink를 구현함
        }

        @Override
        public void incrementZombieUpdates() {
            // IProfilerSink에는 이 메서드가 없으므로 no-op
        }
    }
}
