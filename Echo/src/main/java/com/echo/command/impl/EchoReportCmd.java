package com.echo.command.impl;

import com.echo.config.EchoConfig;
import com.echo.measure.EchoProfiler;
import com.echo.report.EchoReport;

public class EchoReportCmd {
    public static void execute(String[] args) {
        EchoProfiler profiler = EchoProfiler.getInstance();
        EchoReport report = new EchoReport(profiler);
        String reportDir = EchoConfig.getInstance().getReportDirectory();

        if (args.length > 1) {
            String format = args[1].toLowerCase();
            try {
                switch (format) {
                    case "json":
                        String jsonPath = report.saveWithTimestamp(reportDir);
                        System.out.println("[Echo] JSON report saved: " + jsonPath);
                        break;
                    case "csv":
                        String csvPath = report.saveCsv(reportDir);
                        System.out.println("[Echo] CSV report saved: " + csvPath);
                        break;
                    case "html":
                        String htmlPath = report.saveHtml(reportDir);
                        System.out.println("[Echo] HTML report saved: " + htmlPath);
                        break;
                    default:
                        System.out.println("[Echo] Unknown format: " + format);
                        System.out.println("[Echo] Usage: /echo report [json|csv|html]");
                }
            } catch (Exception e) {
                System.err.println("[Echo] Failed to save report: " + e.getMessage());
            }
        } else {
            report.printToConsole();
        }
    }
}
