package com.pulse.network;

import com.pulse.PulseEnvironment;
import com.pulse.access.AccessWidener;
import com.pulse.api.log.PulseLogger;

import java.lang.reflect.Method;

/**
 * Project Zomboid 네트워크 클래스 접근 헬퍼
 */
public class NetworkAccess {

    private static final String LOG = PulseLogger.PULSE;

    // 게임 네트워크 클래스 캐시
    private Class<?> gameClientClass;
    private Class<?> gameServerClass;
    private Class<?> byteBufferWriterClass;
    private Class<?> udpConnectionClass;

    // Method Cache
    private Method clientSendMethod;
    private Method udpSendMethod;

    private boolean initialized = false;

    public void initialize() {
        if (initialized)
            return;

        try {
            ClassLoader loader = PulseEnvironment.getGameClassLoader();
            if (loader == null) {
                loader = ClassLoader.getSystemClassLoader();
            }

            // 게임 클래스 로드
            gameClientClass = loadClass(loader, "zombie.network.GameClient",
                    "GameClient class not found (may be server-only)");
            gameServerClass = loadClass(loader, "zombie.network.GameServer",
                    "GameServer class not found (may be client-only)");
            byteBufferWriterClass = loadClass(loader, "zombie.core.network.ByteBufferWriter",
                    "ByteBufferWriter class not found");
            udpConnectionClass = loadClass(loader, "zombie.network.UdpConnection", "UdpConnection class not found");

            initialized = true;

            // Cache methods
            if (gameClientClass != null) {
                clientSendMethod = findSendMethod(gameClientClass);
            }
            if (udpConnectionClass != null) {
                udpSendMethod = findUdpSendMethod();
            }

            PulseLogger.info(LOG, "Network access initialized");

        } catch (Exception e) {
            PulseLogger.error(LOG, "Failed to initialize network access: {}", e.getMessage());
            e.printStackTrace();
        }
    }

    private Class<?> loadClass(ClassLoader loader, String name, String errorMessage) {
        try {
            Class<?> clazz = loader.loadClass(name);
            PulseLogger.debug(LOG, "Loaded: " + name);
            return clazz;
        } catch (ClassNotFoundException e) {
            PulseLogger.debug(LOG, errorMessage);
            return null;
        }
    }

    public boolean isInitialized() {
        return initialized;
    }

    public Class<?> getGameClientClass() {
        return gameClientClass;
    }

    public Class<?> getGameServerClass() {
        return gameServerClass;
    }

    public Object createByteBufferWriter() {
        if (byteBufferWriterClass == null) {
            return null;
        }
        return AccessWidener.newInstance(byteBufferWriterClass);
    }

    public void writeShort(Object writer, short value) {
        AccessWidener.invoke(writer, "putShort", value);
    }

    public void writeInt(Object writer, int value) {
        AccessWidener.invoke(writer, "putInt", value);
    }

    public void writeBytes(Object writer, byte[] data) {
        AccessWidener.invoke(writer, "putBytes", data);
    }

    public Method getClientSendMethod() {
        return clientSendMethod;
    }

    public Method getUdpSendMethod() {
        return udpSendMethod;
    }

    private Method findSendMethod(Class<?> clazz) {
        try {
            for (Method method : clazz.getDeclaredMethods()) {
                String name = method.getName().toLowerCase();
                if ((name.contains("send") || name.contains("write")) &&
                        method.getParameterCount() == 1 &&
                        byteBufferWriterClass != null &&
                        byteBufferWriterClass.isAssignableFrom(method.getParameterTypes()[0])) {
                    method.setAccessible(true);
                    return method;
                }
            }
        } catch (Exception e) {
            // Ignore
        }
        return null;
    }

    private Method findUdpSendMethod() {
        if (udpConnectionClass == null)
            return null;
        try {
            for (Method method : udpConnectionClass.getDeclaredMethods()) {
                String name = method.getName().toLowerCase();
                if (name.contains("send") && method.getParameterCount() == 1) {
                    method.setAccessible(true);
                    return method;
                }
            }
        } catch (Exception e) {
            // Ignore
        }
        return null;
    }

    public boolean isUdpConnection(Object obj) {
        return udpConnectionClass != null && udpConnectionClass.isInstance(obj);
    }

    public Object getUdpEngine() {
        if (gameServerClass == null)
            return null;
        Object connections = AccessWidener.getStaticField(gameServerClass, "udpEngine");
        if (connections == null) {
            connections = AccessWidener.getStaticField(gameServerClass, "connections");
        }
        return connections;
    }
}
