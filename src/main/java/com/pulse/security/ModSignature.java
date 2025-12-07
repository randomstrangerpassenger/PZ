package com.pulse.security;

/**
 * 모드 서명 및 검증.
 * 모드 JAR의 무결성 확인.
 */
public class ModSignature {

    private final String modId;
    private final String algorithm;
    private final byte[] signature;
    private final String publicKeyId;
    private boolean verified = false;

    public ModSignature(String modId, String algorithm, byte[] signature, String publicKeyId) {
        this.modId = modId;
        this.algorithm = algorithm;
        this.signature = signature;
        this.publicKeyId = publicKeyId;
    }

    // ─────────────────────────────────────────────────────────────
    // 서명 검증
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드 JAR 서명 검증.
     */
    public boolean verify(byte[] jarData) {
        try {
            java.security.Signature sig = java.security.Signature.getInstance(algorithm);

            // 공개 키 로드 (신뢰 저장소에서)
            java.security.PublicKey publicKey = TrustStore.getPublicKey(publicKeyId);
            if (publicKey == null) {
                System.err.println("[Pulse/Security] Unknown public key: " + publicKeyId);
                return false;
            }

            sig.initVerify(publicKey);
            sig.update(jarData);
            verified = sig.verify(signature);

            if (verified) {
                System.out.println("[Pulse/Security] Signature verified: " + modId);
            } else {
                System.err.println("[Pulse/Security] Signature verification failed: " + modId);
            }

            return verified;
        } catch (Exception e) {
            System.err.println("[Pulse/Security] Signature error: " + e.getMessage());
            return false;
        }
    }

    /**
     * 파일에서 서명 검증.
     */
    public boolean verifyFile(java.io.File jarFile) {
        try {
            byte[] data = java.nio.file.Files.readAllBytes(jarFile.toPath());
            return verify(data);
        } catch (java.io.IOException e) {
            return false;
        }
    }

    // Getters
    public String getModId() {
        return modId;
    }

    public String getAlgorithm() {
        return algorithm;
    }

    public byte[] getSignature() {
        return signature.clone();
    }

    public String getPublicKeyId() {
        return publicKeyId;
    }

    public boolean isVerified() {
        return verified;
    }

    // ─────────────────────────────────────────────────────────────
    // 서명 생성 (개발용)
    // ─────────────────────────────────────────────────────────────

    /**
     * 모드 JAR 서명 생성.
     */
    public static ModSignature sign(String modId, byte[] jarData,
            java.security.PrivateKey privateKey, String publicKeyId) {
        try {
            java.security.Signature sig = java.security.Signature.getInstance("SHA256withRSA");
            sig.initSign(privateKey);
            sig.update(jarData);
            byte[] signature = sig.sign();

            return new ModSignature(modId, "SHA256withRSA", signature, publicKeyId);
        } catch (Exception e) {
            System.err.println("[Pulse/Security] Failed to sign: " + e.getMessage());
            return null;
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 신뢰 저장소
    // ─────────────────────────────────────────────────────────────

    public static class TrustStore {
        private static final java.util.Map<String, java.security.PublicKey> keys = new java.util.concurrent.ConcurrentHashMap<>();

        /**
         * 공개 키 등록.
         */
        public static void registerPublicKey(String keyId, java.security.PublicKey key) {
            keys.put(keyId, key);
        }

        /**
         * 공개 키 조회.
         */
        public static java.security.PublicKey getPublicKey(String keyId) {
            return keys.get(keyId);
        }

        /**
         * 파일에서 공개 키 로드.
         */
        public static void loadFromFile(String keyId, java.io.File keyFile) {
            try {
                byte[] keyBytes = java.nio.file.Files.readAllBytes(keyFile.toPath());
                java.security.spec.X509EncodedKeySpec spec = new java.security.spec.X509EncodedKeySpec(keyBytes);
                java.security.KeyFactory kf = java.security.KeyFactory.getInstance("RSA");
                java.security.PublicKey key = kf.generatePublic(spec);
                registerPublicKey(keyId, key);
            } catch (Exception e) {
                System.err.println("[Pulse/Security] Failed to load key: " + e.getMessage());
            }
        }
    }
}
