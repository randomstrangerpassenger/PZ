package com.mutagen.mod;

import java.util.Objects;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Semantic Versioning (SemVer) 기반 버전 비교 유틸리티.
 * 
 * 지원하는 버전 형식:
 * - 1.0.0
 * - 1.0.0-alpha
 * - 1.0.0-beta.1
 * - 1.0.0+build.123
 * 
 * 지원하는 비교 연산자:
 * - = 또는 없음: 정확히 일치
 * - >: 초과
 * - >=: 이상
 * - <: 미만
 * - <=: 이하
 * - ~: 마이너 버전 호환 (예: ~1.2.3 → >=1.2.3 <1.3.0)
 * - ^: 메이저 버전 호환 (예: ^1.2.3 → >=1.2.3 <2.0.0)
 * - *: 모든 버전
 * 
 * 사용 예:
 * 
 * <pre>
 * Version v1 = Version.parse("1.2.3");
 * Version v2 = Version.parse("1.3.0");
 * 
 * v1.compareTo(v2); // -1 (v1 < v2)
 * 
 * VersionComparator.matches("1.2.3", ">=1.0.0"); // true
 * VersionComparator.matches("1.2.3", "~1.2.0"); // true
 * VersionComparator.matches("2.0.0", "^1.2.3"); // false
 * </pre>
 */
public class VersionComparator {

    // ─────────────────────────────────────────────────────────────
    // Version 클래스
    // ─────────────────────────────────────────────────────────────

    /**
     * SemVer 버전을 표현하는 불변 클래스.
     */
    public static class Version implements Comparable<Version> {

        // SemVer 정규식: major.minor.patch[-prerelease][+build]
        private static final Pattern SEMVER_PATTERN = Pattern.compile(
                "^(\\d+)(?:\\.(\\d+))?(?:\\.(\\d+))?(?:-([a-zA-Z0-9.]+))?(?:\\+([a-zA-Z0-9.]+))?$");

        private final int major;
        private final int minor;
        private final int patch;
        private final String prerelease;
        private final String build;

        public Version(int major, int minor, int patch, String prerelease, String build) {
            this.major = major;
            this.minor = minor;
            this.patch = patch;
            this.prerelease = prerelease;
            this.build = build;
        }

        public Version(int major, int minor, int patch) {
            this(major, minor, patch, null, null);
        }

        /**
         * 버전 문자열 파싱.
         * 
         * @param version 버전 문자열 (예: "1.2.3-alpha")
         * @return 파싱된 Version 객체, 실패 시 null
         */
        public static Version parse(String version) {
            if (version == null || version.trim().isEmpty()) {
                return null;
            }

            version = version.trim();

            // v 접두사 제거 (v1.0.0 → 1.0.0)
            if (version.startsWith("v") || version.startsWith("V")) {
                version = version.substring(1);
            }

            Matcher matcher = SEMVER_PATTERN.matcher(version);
            if (!matcher.matches()) {
                System.err.println("[Mutagen/Version] Invalid version format: " + version);
                return null;
            }

            int major = Integer.parseInt(matcher.group(1));
            int minor = matcher.group(2) != null ? Integer.parseInt(matcher.group(2)) : 0;
            int patch = matcher.group(3) != null ? Integer.parseInt(matcher.group(3)) : 0;
            String prerelease = matcher.group(4);
            String build = matcher.group(5);

            return new Version(major, minor, patch, prerelease, build);
        }

        public int getMajor() {
            return major;
        }

        public int getMinor() {
            return minor;
        }

        public int getPatch() {
            return patch;
        }

        public String getPrerelease() {
            return prerelease;
        }

        public String getBuild() {
            return build;
        }

        public boolean isPrerelease() {
            return prerelease != null && !prerelease.isEmpty();
        }

        @Override
        public int compareTo(Version other) {
            if (other == null)
                return 1;

            // 메이저 비교
            int result = Integer.compare(this.major, other.major);
            if (result != 0)
                return result;

            // 마이너 비교
            result = Integer.compare(this.minor, other.minor);
            if (result != 0)
                return result;

            // 패치 비교
            result = Integer.compare(this.patch, other.patch);
            if (result != 0)
                return result;

            // 프리릴리스 비교
            // 프리릴리스가 있으면 없는 것보다 낮음 (1.0.0-alpha < 1.0.0)
            if (this.prerelease == null && other.prerelease == null) {
                return 0;
            }
            if (this.prerelease == null) {
                return 1; // this가 릴리스, other가 프리릴리스
            }
            if (other.prerelease == null) {
                return -1; // this가 프리릴리스, other가 릴리스
            }

            // 둘 다 프리릴리스인 경우 문자열 비교
            return comparePrerelease(this.prerelease, other.prerelease);
        }

        private int comparePrerelease(String a, String b) {
            String[] partsA = a.split("\\.");
            String[] partsB = b.split("\\.");

            int length = Math.max(partsA.length, partsB.length);
            for (int i = 0; i < length; i++) {
                String partA = i < partsA.length ? partsA[i] : "";
                String partB = i < partsB.length ? partsB[i] : "";

                boolean aIsNumeric = partA.matches("\\d+");
                boolean bIsNumeric = partB.matches("\\d+");

                int result;
                if (aIsNumeric && bIsNumeric) {
                    result = Integer.compare(Integer.parseInt(partA), Integer.parseInt(partB));
                } else if (aIsNumeric) {
                    result = -1; // 숫자가 문자열보다 낮음
                } else if (bIsNumeric) {
                    result = 1;
                } else {
                    result = partA.compareTo(partB);
                }

                if (result != 0)
                    return result;
            }

            return 0;
        }

        @Override
        public boolean equals(Object obj) {
            if (this == obj)
                return true;
            if (obj == null || getClass() != obj.getClass())
                return false;
            Version other = (Version) obj;
            return major == other.major &&
                    minor == other.minor &&
                    patch == other.patch &&
                    Objects.equals(prerelease, other.prerelease);
        }

        @Override
        public int hashCode() {
            return Objects.hash(major, minor, patch, prerelease);
        }

        @Override
        public String toString() {
            StringBuilder sb = new StringBuilder();
            sb.append(major).append(".").append(minor).append(".").append(patch);
            if (prerelease != null) {
                sb.append("-").append(prerelease);
            }
            if (build != null) {
                sb.append("+").append(build);
            }
            return sb.toString();
        }
    }

    // ─────────────────────────────────────────────────────────────
    // 버전 비교 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 버전이 요구사항을 만족하는지 확인.
     * 
     * @param version     확인할 버전 (예: "1.2.3")
     * @param requirement 요구사항 (예: ">=1.0.0", "~1.2.0", "^1.0.0")
     * @return 만족하면 true
     */
    public static boolean matches(String version, String requirement) {
        if (version == null || version.isEmpty()) {
            return false;
        }
        if (requirement == null || requirement.isEmpty() || "*".equals(requirement)) {
            return true; // 요구사항 없음 = 모든 버전 허용
        }

        Version ver = Version.parse(version);
        if (ver == null) {
            return false;
        }

        return matchesRequirement(ver, requirement.trim());
    }

    /**
     * 두 버전을 비교.
     * 
     * @return v1 < v2 → 음수, v1 == v2 → 0, v1 > v2 → 양수
     */
    public static int compare(String v1, String v2) {
        Version ver1 = Version.parse(v1);
        Version ver2 = Version.parse(v2);

        if (ver1 == null && ver2 == null)
            return 0;
        if (ver1 == null)
            return -1;
        if (ver2 == null)
            return 1;

        return ver1.compareTo(ver2);
    }

    private static boolean matchesRequirement(Version version, String requirement) {
        // 공백으로 분리된 여러 조건 처리 (예: ">=1.0.0 <2.0.0")
        if (requirement.contains(" ")) {
            String[] parts = requirement.split("\\s+");
            for (String part : parts) {
                if (!matchesSingleRequirement(version, part.trim())) {
                    return false;
                }
            }
            return true;
        }

        return matchesSingleRequirement(version, requirement);
    }

    private static boolean matchesSingleRequirement(Version version, String req) {
        if (req.isEmpty() || "*".equals(req)) {
            return true;
        }

        // 틸드 범위: ~1.2.3 → >=1.2.3 <1.3.0
        if (req.startsWith("~")) {
            Version reqVer = Version.parse(req.substring(1));
            if (reqVer == null)
                return false;

            // 하한: >=reqVer
            if (version.compareTo(reqVer) < 0)
                return false;

            // 상한: <next minor
            Version upperBound = new Version(reqVer.major, reqVer.minor + 1, 0);
            return version.compareTo(upperBound) < 0;
        }

        // 캐럿 범위: ^1.2.3 → >=1.2.3 <2.0.0
        if (req.startsWith("^")) {
            Version reqVer = Version.parse(req.substring(1));
            if (reqVer == null)
                return false;

            // 하한: >=reqVer
            if (version.compareTo(reqVer) < 0)
                return false;

            // 상한: <next major (단, 0.x는 0.(x+1).0)
            Version upperBound;
            if (reqVer.major == 0) {
                upperBound = new Version(0, reqVer.minor + 1, 0);
            } else {
                upperBound = new Version(reqVer.major + 1, 0, 0);
            }
            return version.compareTo(upperBound) < 0;
        }

        // 비교 연산자
        if (req.startsWith(">=")) {
            Version reqVer = Version.parse(req.substring(2));
            return reqVer != null && version.compareTo(reqVer) >= 0;
        }
        if (req.startsWith("<=")) {
            Version reqVer = Version.parse(req.substring(2));
            return reqVer != null && version.compareTo(reqVer) <= 0;
        }
        if (req.startsWith(">")) {
            Version reqVer = Version.parse(req.substring(1));
            return reqVer != null && version.compareTo(reqVer) > 0;
        }
        if (req.startsWith("<")) {
            Version reqVer = Version.parse(req.substring(1));
            return reqVer != null && version.compareTo(reqVer) < 0;
        }
        if (req.startsWith("=")) {
            Version reqVer = Version.parse(req.substring(1));
            return reqVer != null && version.compareTo(reqVer) == 0;
        }

        // 연산자 없음 = 정확히 일치
        Version reqVer = Version.parse(req);
        return reqVer != null && version.compareTo(reqVer) == 0;
    }

    // ─────────────────────────────────────────────────────────────
    // 유틸리티 메서드
    // ─────────────────────────────────────────────────────────────

    /**
     * 버전 파싱 시도.
     */
    public static Version parse(String version) {
        return Version.parse(version);
    }

    /**
     * 유효한 버전 문자열인지 확인.
     */
    public static boolean isValid(String version) {
        return Version.parse(version) != null;
    }

    /**
     * 테스트용 메인 메서드.
     */
    public static void main(String[] args) {
        System.out.println("=== VersionComparator Tests ===");

        // 파싱 테스트
        System.out.println("\n[Parsing]");
        System.out.println("1.0.0 → " + Version.parse("1.0.0"));
        System.out.println("1.2.3-alpha → " + Version.parse("1.2.3-alpha"));
        System.out.println("v2.0.0-beta.1+build.123 → " + Version.parse("v2.0.0-beta.1+build.123"));

        // 비교 테스트
        System.out.println("\n[Comparison]");
        System.out.println("1.0.0 vs 1.0.1: " + compare("1.0.0", "1.0.1"));
        System.out.println("1.1.0 vs 1.0.9: " + compare("1.1.0", "1.0.9"));
        System.out.println("2.0.0-alpha vs 2.0.0: " + compare("2.0.0-alpha", "2.0.0"));

        // 매칭 테스트
        System.out.println("\n[Matching]");
        System.out.println("1.2.3 matches >=1.0.0: " + matches("1.2.3", ">=1.0.0"));
        System.out.println("1.2.3 matches <2.0.0: " + matches("1.2.3", "<2.0.0"));
        System.out.println("1.2.3 matches ~1.2.0: " + matches("1.2.3", "~1.2.0"));
        System.out.println("1.3.0 matches ~1.2.0: " + matches("1.3.0", "~1.2.0"));
        System.out.println("1.9.9 matches ^1.2.3: " + matches("1.9.9", "^1.2.3"));
        System.out.println("2.0.0 matches ^1.2.3: " + matches("2.0.0", "^1.2.3"));
        System.out.println("1.5.0 matches >=1.0.0 <2.0.0: " + matches("1.5.0", ">=1.0.0 <2.0.0"));

        System.out.println("\n=== All Tests Completed ===");
    }
}
