package com.echo.lua;

import java.lang.reflect.Field;
import java.lang.reflect.Array;
import java.util.Map;
import java.util.Collections;
import java.util.WeakHashMap;
import java.util.concurrent.atomic.LongAdder;

/**
 * Lua 함수 라벨러 - 제네릭 라벨을 실제 식별 가능한 함수 ID로 변환
 * 
 * 출력 형태:
 * - LuaClosure: "media/lua/client/ISUI/ISInventoryPage.lua:100 (render)"
 * - JavaFunction: "[Java] pcall"
 * - Unknown: "unknown:type#hash"
 * 
 * 설계 원칙:
 * 1. WeakHashMap 캐시로 메모리 누수 방지
 * 2. 리플렉션 필드는 1회만 조회
 * 3. 3단계 폴백: LuaClosure → JavaFunction → unknown
 */
public class FunctionLabeler {

    // 리플렉션 비용 최소화를 위한 캐시 (WeakHashMap으로 메모리 누수 방지)
    private static final Map<Object, String> labelCache = Collections.synchronizedMap(new WeakHashMap<>());

    // 품질 지표
    private static final LongAdder totalLabeled = new LongAdder();
    private static final LongAdder unknownLabeled = new LongAdder();
    private static final LongAdder cacheHits = new LongAdder();

    // 리플렉션 필드 캐시 (클래스별 1회만 조회)
    private static volatile Field closurePrototypeField;
    private static volatile Field protoFilenameField;
    private static volatile Field protoNameField;
    private static volatile Field protoLinesField;
    private static volatile boolean fieldsInitialized = false;

    /**
     * Function object에서 라벨 추출
     * 
     * @param func Lua 함수 객체 (LuaClosure, JavaFunction 등)
     * @return 식별 가능한 라벨 문자열
     */
    public static String labelOf(Object func) {
        if (func == null) {
            return "<null>";
        }

        // 1. Fast Path: 캐시 확인
        String cached = labelCache.get(func);
        if (cached != null) {
            cacheHits.increment();
            return cached;
        }

        // 2. 라벨 생성
        String label = createLabel(func);

        // 3. 캐싱
        labelCache.put(func, label);

        // 4. 품질 지표 업데이트
        totalLabeled.increment();
        if (label.startsWith("unknown:")) {
            unknownLabeled.increment();
        }

        return label;
    }

    private static String createLabel(Object func) {
        String className = func.getClass().getName();

        try {
            // Case A: LuaClosure (대부분의 Lua 함수)
            if (className.contains("LuaClosure")) {
                return labelLuaClosure(func);
            }

            // Case B: JavaFunction (pcall, print 등 자바 구현 함수)
            if (className.contains("JavaFunction")) {
                return labelJavaFunction(func);
            }

            // Case C: 기타 - String이면 그대로 반환
            if (func instanceof String) {
                return (String) func;
            }

            // Case D: 숫자(argCount) - 기존 방식 호환
            if (func instanceof Number) {
                return "call:" + func;
            }

            // Case E: 기타
            return "unknown:" + func.getClass().getSimpleName() + "#" +
                    Integer.toHexString(System.identityHashCode(func));

        } catch (Exception e) {
            return "unknown:error#" + Integer.toHexString(System.identityHashCode(func));
        }
    }

    /**
     * LuaClosure 라벨링
     * 출력 형태: "media/lua/client/ISUI/ISInventoryPage.lua:100 (render)"
     * "media/lua/client/ISUI/ISInventoryPage.lua:100"
     * "lua:closure#1a2b3c" (fallback)
     */
    private static String labelLuaClosure(Object closure) throws Exception {
        initFieldsIfNeeded(closure);

        if (closurePrototypeField == null) {
            return "lua:closure#" + Integer.toHexString(System.identityHashCode(closure));
        }

        Object prototype = closurePrototypeField.get(closure);
        if (prototype == null) {
            return "lua:closure#" + Integer.toHexString(System.identityHashCode(closure));
        }

        // Filename 추출
        String filename = null;
        if (protoFilenameField != null) {
            filename = (String) protoFilenameField.get(prototype);
        }

        // Name 추출 (함수명, 없을 수 있음)
        String name = null;
        if (protoNameField != null) {
            name = (String) protoNameField.get(prototype);
        }

        // Line Number 추출 (lines 배열의 첫 번째 요소)
        int line = 0;
        if (protoLinesField != null) {
            Object linesArray = protoLinesField.get(prototype);
            if (linesArray != null && Array.getLength(linesArray) > 0) {
                line = Array.getInt(linesArray, 0);
            }
        }

        // 포맷팅
        if (filename != null && !filename.isEmpty()) {
            // 파일명 간소화 (긴 경로에서 media/lua/ 이후만)
            String shortFilename = shortenFilename(filename);
            if (name != null && !name.isEmpty()) {
                return String.format("%s:%d (%s)", shortFilename, line, name);
            } else {
                return String.format("%s:%d", shortFilename, line);
            }
        }

        // Fallback
        return "lua:closure#" + Integer.toHexString(System.identityHashCode(closure));
    }

    /**
     * 파일명 간소화 - 긴 경로에서 핵심 부분만 추출
     */
    private static String shortenFilename(String filename) {
        if (filename == null)
            return "";

        // media/lua/가 포함된 경우 그 이후 부분만
        int idx = filename.indexOf("media/lua/");
        if (idx >= 0) {
            return filename.substring(idx);
        }

        // 그 외의 경우 마지막 3개 경로 컴포넌트만
        String[] parts = filename.split("[/\\\\]");
        if (parts.length <= 3) {
            return filename;
        }
        return parts[parts.length - 3] + "/" + parts[parts.length - 2] + "/" + parts[parts.length - 1];
    }

    /**
     * JavaFunction 라벨링
     * 출력 형태: "[Java] pcall", "[Java] MyMod_OnFillContextMenu"
     */
    private static String labelJavaFunction(Object javaFunc) {
        String str = javaFunc.toString();
        // toString이 유용한 정보를 주면 사용, 아니면 클래스명
        if (str != null && !str.isEmpty() && !str.contains("@")) {
            return "[Java] " + str;
        }
        return "[Java] " + javaFunc.getClass().getSimpleName();
    }

    /**
     * 리플렉션 필드 초기화 (1회만 수행)
     */
    private static synchronized void initFieldsIfNeeded(Object closure) {
        if (fieldsInitialized) {
            return;
        }

        try {
            Class<?> closureClass = closure.getClass();
            closurePrototypeField = closureClass.getField("prototype");

            Object prototype = closurePrototypeField.get(closure);
            if (prototype != null) {
                Class<?> protoClass = prototype.getClass();

                try {
                    protoFilenameField = protoClass.getField("filename");
                } catch (NoSuchFieldException ignored) {
                }

                try {
                    protoNameField = protoClass.getField("name");
                } catch (NoSuchFieldException ignored) {
                }

                try {
                    protoLinesField = protoClass.getField("lines");
                } catch (NoSuchFieldException ignored) {
                }
            }
        } catch (Exception e) {
            // 필드 없으면 null로 유지
            System.err.println("[Echo/FunctionLabeler] Field initialization failed: " + e.getMessage());
        }

        fieldsInitialized = true;
    }

    // ===== 품질 지표 API =====

    public static double getUnknownLabelRatio() {
        long total = totalLabeled.sum();
        if (total == 0)
            return 0.0;
        return (double) unknownLabeled.sum() / total;
    }

    public static double getCacheHitRatio() {
        long total = totalLabeled.sum() + cacheHits.sum();
        if (total == 0)
            return 0.0;
        return (double) cacheHits.sum() / total;
    }

    public static void resetStats() {
        totalLabeled.reset();
        unknownLabeled.reset();
        cacheHits.reset();
    }

    public static Map<String, Object> getStats() {
        return Map.of(
                "total_labeled", totalLabeled.sum(),
                "unknown_labeled", unknownLabeled.sum(),
                "unknown_ratio", Math.round(getUnknownLabelRatio() * 10000) / 100.0,
                "cache_hits", cacheHits.sum(),
                "cache_hit_ratio", Math.round(getCacheHitRatio() * 10000) / 100.0,
                "cache_size", labelCache.size());
    }
}
