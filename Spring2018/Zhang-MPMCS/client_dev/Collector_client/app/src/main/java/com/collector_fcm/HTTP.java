package com.collector_fcm;

import android.support.annotation.NonNull;

import org.json.JSONObject;

import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public final class HTTP {
    private HTTP() {
    }

    public static HttpURLConnection postJSON(@NonNull URL url, @NonNull JSONObject object)
            throws IOException {
        byte[] data = object.toString().getBytes(StandardCharsets.UTF_8);

        HttpURLConnection connection = (HttpURLConnection) url.openConnection();

        connection.setDoOutput(true);
        connection.setInstanceFollowRedirects(false);
        connection.setUseCaches(false);
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Charset", "UTF-8");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setRequestProperty("Content-Length", Integer.toString(data.length));

        try (OutputStream outputStream = connection.getOutputStream()) {
            outputStream.write(data);
        }

        return connection;
    }
}
