package com.mutagen.network;

import com.mutagen.registry.Identifier;

/**
 * 패킷 인터페이스.
 * 모든 네트워크 패킷은 이 인터페이스를 구현해야 함.
 * 
 * 사용 예:
 * 
 * <pre>
 * public class MyPacket implements Packet {
 *     private String message;
 *     
 *     public MyPacket() {} // 역직렬화용
 *     
 *     public MyPacket(String message) {
 *         this.message = message;
 *     }
 *     
 *     {@literal @}Override
 *     public void write(PacketBuffer buf) {
 *         buf.writeString(message);
 *     }
 *     
 *     {@literal @}Override
 *     public void read(PacketBuffer buf) {
 *         message = buf.readString();
 *     }
 *     
 *     {@literal @}Override
 *     public Identifier getId() {
 *         return Identifier.of("mymod", "my_packet");
 *     }
 * }
 * </pre>
 */
public interface Packet {

    /**
     * 패킷 ID
     */
    Identifier getId();

    /**
     * 패킷 데이터를 버퍼에 쓰기
     */
    void write(PacketBuffer buf);

    /**
     * 버퍼에서 패킷 데이터 읽기
     */
    void read(PacketBuffer buf);
}
