package com.echo.command.impl;

import com.echo.config.EchoConfig;
import com.echo.measure.EchoProfiler;
import com.echo.report.EchoReport;
import com.pulse.api.log.PulseLogger;

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
                        PulseLogger.info("Echo", "JSON report saved: " + jsonPath);
                        break;
                    case "csv":
                        String csvPath = report.saveCsv(reportDir);
                        PulseLogger.info("Echo", "CSV report saved: " + csvPath);
                        break;
                    case "html":
                        String htmlPath = report.saveHtml(reportDir);
                        PulseLogger.info("Echo", "HTML report saved: " + htmlPath);
                        break;
                    default:
                        PulseLogger.warn("Echo", "Unknown format: " + format);
                        PulseLogger.info("Echo", "Usage: /echo report [json|csv|html]");
                }
            } catch (Exception e) {
                PulseLogger.error("Echo", "Failed to save report: " + e.getMessage());
            }
        } else {
            report.printToConsole();
        }
    }
}
