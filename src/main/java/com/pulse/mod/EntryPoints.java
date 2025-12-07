package com.pulse.mod;

/**
 * 환경별 엔트리포인트 정의.
 * 클라이언트/서버/공통 각각 다른 초기화 클래스 지정 가능.
 * 
 * pulse.mod.json 예:
 * 
 * <pre>
 * "entryPoints": {
 *     "common": "com.example.ModCommon",
 *     "client": "com.example.ModClient", 
 *     "server": "com.example.ModServer"
 * }
 * </pre>
 */
public class EntryPoints {

    private String common; // 공통 (항상 실행)
    private String client; // 클라이언트 전용
    private String server; // 서버 전용

    public String getCommon() {
        return common;
    }

    public void setCommon(String common) {
        this.common = common;
    }

    public String getClient() {
        return client;
    }

    public void setClient(String client) {
        this.client = client;
    }

    public String getServer() {
        return server;
    }

    public void setServer(String server) {
        this.server = server;
    }

    /**
     * 현재 환경에 맞는 엔트리포인트 반환.
     */
    public String getForEnvironment(Environment env) {
        switch (env) {
            case CLIENT:
                return client != null ? client : common;
            case SERVER:
                return server != null ? server : common;
            default:
                return common;
        }
    }

    public enum Environment {
        CLIENT,
        SERVER,
        INTEGRATED // 싱글플레이 (클라이언트 + 서버)
    }
}
