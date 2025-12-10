package com.echo.monitor;

import com.echo.measure.EchoProfiler;
import com.echo.measure.ProfilingPoint;
import com.echo.aggregate.TimingData;
import com.echo.aggregate.TickHistogram;
import com.echo.aggregate.SpikeLog;
import com.echo.measure.MemoryProfiler;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpExchange;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.Executors;

/**
 * Echo 실시간 모니터링 HTTP 서버
 * 
 * 외부 도구에서 프로파일링 데이터에 접근할 수 있는 간단한 REST API 제공
 */
public class EchoMonitorServer {

    private static final int DEFAULT_PORT = 8765;
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();

    private static EchoMonitorServer instance;
    private HttpServer server;
    private boolean running = false;

    private EchoMonitorServer() {
    }

    public static EchoMonitorServer getInstance() {
        if (instance == null) {
            instance = new EchoMonitorServer();
        }
        return instance;
    }

    /**
     * 서버 시작
     */
    public void start() {
        start(DEFAULT_PORT);
    }

    public void start(int port) {
        if (running) {
            System.out.println("[Echo] Monitor server already running on port " + server.getAddress().getPort());
            return;
        }

        try {
            server = HttpServer.create(new InetSocketAddress(port), 0);
            server.setExecutor(Executors.newFixedThreadPool(2));

            // API 엔드포인트 등록
            server.createContext("/api/status", new StatusHandler());
            server.createContext("/api/summary", new SummaryHandler());
            server.createContext("/api/histogram", new HistogramHandler());
            server.createContext("/api/spikes", new SpikesHandler());
            server.createContext("/api/memory", new MemoryHandler());
            server.createContext("/", new RootHandler());

            server.start();
            running = true;
            System.out.println("[Echo] Monitor server started on http://localhost:" + port);
            System.out.println("[Echo] Endpoints: /api/status, /api/summary, /api/histogram, /api/spikes, /api/memory");
        } catch (IOException e) {
            System.err.println("[Echo] Failed to start monitor server: " + e.getMessage());
        }
    }

    /**
     * 서버 중지
     */
    public void stop() {
        if (!running || server == null) {
            System.out.println("[Echo] Monitor server not running");
            return;
        }

        server.stop(1);
        running = false;
        System.out.println("[Echo] Monitor server stopped");
    }

    public boolean isRunning() {
        return running;
    }

    // ============================================================
    // HTTP Handlers
    // ============================================================

    private static class RootHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String response = "Echo Profiler Monitor API\n\n" +
                    "Endpoints:\n" +
                    "  GET /api/status    - Profiler status\n" +
                    "  GET /api/summary   - Tick summary\n" +
                    "  GET /api/histogram - Tick distribution\n" +
                    "  GET /api/spikes    - Recent spikes\n" +
                    "  GET /api/memory    - Memory stats\n";
            sendResponse(exchange, 200, response, "text/plain");
        }
    }

    private static class StatusHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            EchoProfiler profiler = EchoProfiler.getInstance();
            Map<String, Object> status = new LinkedHashMap<>();
            status.put("enabled", profiler.isEnabled());
            status.put("lua_profiling", profiler.isLuaProfilingEnabled());
            status.put("session_duration_seconds", profiler.getSessionDurationSeconds());
            status.put("current_stack_depth", profiler.getCurrentStackDepth());
            sendJsonResponse(exchange, status);
        }
    }

    private static class SummaryHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            EchoProfiler profiler = EchoProfiler.getInstance();
            TimingData tickData = profiler.getTimingData(ProfilingPoint.TICK);

            Map<String, Object> summary = new LinkedHashMap<>();
            if (tickData != null && tickData.getCallCount() > 0) {
                summary.put("total_ticks", tickData.getCallCount());
                summary.put("average_ms", round(tickData.getAverageMicros() / 1000.0));
                summary.put("max_ms", round(tickData.getMaxMicros() / 1000.0));
                summary.put("min_ms", round(tickData.getMinMicros() / 1000.0));

                TimingData.RollingStats stats5s = tickData.getStats5s();
                Map<String, Object> rolling = new LinkedHashMap<>();
                rolling.put("avg_ms", round(stats5s.getAverage() / 1000.0));
                rolling.put("max_ms", round(stats5s.getMax() / 1000.0));
                rolling.put("samples", stats5s.getSampleCount());
                summary.put("last_5s", rolling);
            }
            sendJsonResponse(exchange, summary);
        }
    }

    private static class HistogramHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            TickHistogram histogram = EchoProfiler.getInstance().getTickHistogram();
            sendJsonResponse(exchange, histogram.toMap());
        }
    }

    private static class SpikesHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            SpikeLog spikeLog = EchoProfiler.getInstance().getSpikeLog();
            sendJsonResponse(exchange, spikeLog.toMap());
        }
    }

    private static class MemoryHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            sendJsonResponse(exchange, MemoryProfiler.toMap());
        }
    }

    // ============================================================
    // Utility Methods
    // ============================================================

    private static void sendJsonResponse(HttpExchange exchange, Object data) throws IOException {
        String json = GSON.toJson(data);
        sendResponse(exchange, 200, json, "application/json");
    }

    private static void sendResponse(HttpExchange exchange, int status, String body, String contentType)
            throws IOException {
        exchange.getResponseHeaders().add("Content-Type", contentType + "; charset=UTF-8");
        exchange.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        exchange.sendResponseHeaders(status, bytes.length);
        try (OutputStream os = exchange.getResponseBody()) {
            os.write(bytes);
        }
    }

    private static double round(double value) {
        return Math.round(value * 100.0) / 100.0;
    }
}
