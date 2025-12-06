package com.pulse.network;

import java.io.*;
import java.nio.charset.StandardCharsets;

/**
 * 패킷 버퍼.
 * 패킷 데이터의 직렬화/역직렬화를 담당.
 */
public class PacketBuffer {

    private final ByteArrayOutputStream outputStream;
    private final DataOutputStream out;
    private final DataInputStream in;
    private byte[] data;

    /**
     * 쓰기용 버퍼 생성
     */
    public PacketBuffer() {
        this.outputStream = new ByteArrayOutputStream();
        this.out = new DataOutputStream(outputStream);
        this.in = null;
        this.data = null;
    }

    /**
     * 읽기용 버퍼 생성
     */
    public PacketBuffer(byte[] data) {
        this.data = data;
        this.outputStream = null;
        this.out = null;
        this.in = new DataInputStream(new ByteArrayInputStream(data));
    }

    // ─────────────────────────────────────────────────────────────
    // 쓰기 메서드
    // ─────────────────────────────────────────────────────────────

    public void writeByte(int value) {
        try {
            out.writeByte(value);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void writeShort(int value) {
        try {
            out.writeShort(value);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void writeInt(int value) {
        try {
            out.writeInt(value);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void writeLong(long value) {
        try {
            out.writeLong(value);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void writeFloat(float value) {
        try {
            out.writeFloat(value);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void writeDouble(double value) {
        try {
            out.writeDouble(value);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void writeBoolean(boolean value) {
        try {
            out.writeBoolean(value);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void writeString(String value) {
        try {
            byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
            out.writeInt(bytes.length);
            out.write(bytes);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public void writeBytes(byte[] bytes) {
        try {
            out.writeInt(bytes.length);
            out.write(bytes);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 읽기 메서드
    // ─────────────────────────────────────────────────────────────

    public byte readByte() {
        try {
            return in.readByte();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public short readShort() {
        try {
            return in.readShort();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public int readInt() {
        try {
            return in.readInt();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public long readLong() {
        try {
            return in.readLong();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public float readFloat() {
        try {
            return in.readFloat();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public double readDouble() {
        try {
            return in.readDouble();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public boolean readBoolean() {
        try {
            return in.readBoolean();
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public String readString() {
        try {
            int length = in.readInt();
            byte[] bytes = new byte[length];
            in.readFully(bytes);
            return new String(bytes, StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    public byte[] readBytes() {
        try {
            int length = in.readInt();
            byte[] bytes = new byte[length];
            in.readFully(bytes);
            return bytes;
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티
    // ─────────────────────────────────────────────────────────────

    /**
     * 버퍼 데이터를 바이트 배열로 변환
     */
    public byte[] toByteArray() {
        if (outputStream != null) {
            return outputStream.toByteArray();
        }
        return data;
    }

    /**
     * 남은 바이트 수
     */
    public int remaining() {
        if (in != null) {
            try {
                return in.available();
            } catch (IOException e) {
                return 0;
            }
        }
        return 0;
    }
}
