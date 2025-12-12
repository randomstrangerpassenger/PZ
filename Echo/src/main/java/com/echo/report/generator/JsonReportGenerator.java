package com.echo.report.generator;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.util.Map;

/**
 * JSON 포맷 리포트 생성기.
 * 
 * @since 1.1.0
 */
public class JsonReportGenerator implements ReportGenerator {

    private static final Gson GSON = new GsonBuilder()
            .setPrettyPrinting()
            .create();

    @Override
    public String generate(Map<String, Object> data) {
        return GSON.toJson(data);
    }

    @Override
    public String getFormatName() {
        return "JSON";
    }

    @Override
    public String getFileExtension() {
        return ".json";
    }
}
