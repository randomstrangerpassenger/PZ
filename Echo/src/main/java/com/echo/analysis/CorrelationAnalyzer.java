package com.echo.analysis;

import com.echo.history.MetricHistory;

import java.util.Arrays;

/**
 * 상관관계 분석기
 * Pearson Correlation Coefficient(PCC)를 사용하여 두 메트릭 간의 상관관계를 분석합니다.
 */
public class CorrelationAnalyzer {

    /**
     * 두 히스토리 데이터의 상관계수를 계산합니다.
     * 
     * @return -1.0 ~ 1.0 사이의 값. 데이터가 부족하거나 분산이 0이면 0.0 반환.
     */
    public static double calculateCorrelation(MetricHistory h1, MetricHistory h2) {
        if (h1 == null || h2 == null)
            return 0.0;

        double[] d1 = h1.toArray();
        double[] d2 = h2.toArray();

        // 1. 데이터 길이 맞추기 (뒤에서부터, 즉 최신 데이터 기준으로 매칭)
        int len = Math.min(d1.length, d2.length);
        if (len < 5) {
            // 데이터가 너무 적으면 의미 없음 (적어도 5개 샘플은 필요)
            return 0.0;
        }

        // 최신 N개 추출
        double[] x = Arrays.copyOfRange(d1, d1.length - len, d1.length);
        double[] y = Arrays.copyOfRange(d2, d2.length - len, d2.length);

        return computePearson(x, y);
    }

    private static double computePearson(double[] x, double[] y) {
        if (x.length != y.length)
            return 0.0;
        int n = x.length;

        double sumX = 0.0;
        double sumY = 0.0;
        double sumXY = 0.0;
        double sumX2 = 0.0;
        double sumY2 = 0.0;

        for (int i = 0; i < n; i++) {
            sumX += x[i];
            sumY += y[i];
            sumXY += x[i] * y[i];
            sumX2 += x[i] * x[i];
            sumY2 += y[i] * y[i];
        }

        double numerator = n * sumXY - sumX * sumY;
        double denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

        if (denominator == 0)
            return 0.0; // 분모가 0이면(표준편차가 0이면) 상관관계 정의 불가

        return numerator / denominator;
    }

    /**
     * 상관관계 해석 (디버그용/리포트용)
     */
    public static String interpret(double correlation) {
        double abs = Math.abs(correlation);
        String direction = correlation > 0 ? "Positive" : "Negative";

        if (abs > 0.7)
            return "Strong " + direction;
        if (abs > 0.3)
            return "Moderate " + direction;
        return "Weak/None";
    }
}
