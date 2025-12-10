package com.echo.tool;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import java.io.FileReader;

/**
 * CLI Tool to diff two Echo Reports.
 * Usage: java -cp Echo.jar com.echo.tool.ReportDiff report1.json report2.json
 */
public class ReportDiff {

    private static final Gson GSON = new Gson();

    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage: ReportDiff <baseline.json> <candidate.json>");
            return;
        }

        String fileA = args[0];
        String fileB = args[1];

        try {
            JsonObject jsonA = GSON.fromJson(new FileReader(fileA), JsonObject.class);
            JsonObject jsonB = GSON.fromJson(new FileReader(fileB), JsonObject.class);

            if (jsonA == null || jsonB == null) {
                System.err.println("Failed to parse JSON.");
                return;
            }

            JsonObject echoA = jsonA.getAsJsonObject("echo_report");
            JsonObject echoB = jsonB.getAsJsonObject("echo_report");

            if (echoA == null || echoB == null) {
                // Try parsing as raw echo report if not wrapped
                if (jsonA.has("version"))
                    echoA = jsonA;
                if (jsonB.has("version"))
                    echoB = jsonB;
            }

            printDiff(fileA, echoA, fileB, echoB);

        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void printDiff(String nameA, JsonObject a, String nameB, JsonObject b) {
        System.out.println("ECHO REPORT DIFF");
        System.out.println("A: " + nameA + "  vs  B: " + nameB);
        System.out.println("--------------------------------------------------");

        compareSummary(a.getAsJsonObject("summary"), b.getAsJsonObject("summary"));
        // Compare other sections as needed...
    }

    private static void compareSummary(JsonObject a, JsonObject b) {
        System.out.println("\n[SUMMARY Comparison]");
        if (a == null || b == null) {
            System.out.println("  Missing summary section.");
            return;
        }

        double tickA = a.get("average_tick_ms").getAsDouble();
        double tickB = b.get("average_tick_ms").getAsDouble();

        diff("Avg Tick (ms)", tickA, tickB);

        long totalA = a.get("total_ticks").getAsLong();
        long totalB = b.get("total_ticks").getAsLong();

        diff("Total Ticks", totalA, totalB);

        double spikeA = a.get("max_tick_spike_ms").getAsDouble();
        double spikeB = b.get("max_tick_spike_ms").getAsDouble();

        diff("Max Spike (ms)", spikeA, spikeB);
    }

    private static void diff(String label, double valA, double valB) {
        double delta = valB - valA;
        double pct = (valA == 0) ? 0 : (delta / valA) * 100.0;
        String sign = delta > 0 ? "+" : "";
        String color = Math.abs(pct) < 5 ? "" : (delta < 0 ? " (Improved)" : " (Regressed)");

        System.out.printf("  %-20s: %8.2f -> %8.2f | %s%.2f (%.1f%%)%s%n",
                label, valA, valB, sign, delta, pct, color);
    }

    private static void diff(String label, long valA, long valB) {
        long delta = valB - valA;
        System.out.printf("  %-20s: %8d -> %8d | %+d%n",
                label, valA, valB, delta);
    }
}
