package com.militzer.shortcutbuilder;

import android.app.DownloadManager;
import android.app.job.JobParameters;
import android.app.job.JobService;
import android.net.Uri;
import android.os.Environment;
import android.text.TextUtils;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.util.Date;
import java.util.Locale;

public class BuildJobService extends JobService {

    public static final String KEY_NAME = "name";
    public static final String KEY_URL = "url";
    public static final String KEY_ZOOM = "zoom";
    public static final String KEY_REQUEST_ID = "request_id";
    public static final String KEY_STARTED_AT = "started_at";

    private static final String BUILD_SERVICE_URL =
            "https://script.google.com/macros/s/AKfycbw_vuH5-nlE6l1-AtP4GNRYaLTDC1X1wnRrUeUjUL1YssfK951pkd7DmMl9_bya81QF/exec";
    private static final String BUILD_STATUS_URL =
            "https://api.github.com/repos/militzerjoseph/pincas/contents/output/build-status.json?ref=shortcut-builder-output";
    private static final String GENERATED_APK_URL =
            "https://raw.githubusercontent.com/militzerjoseph/pincas/shortcut-builder-output/output/generated-app.apk";

    private volatile boolean stopped;

    @Override
    public boolean onStartJob(JobParameters params) {
        stopped = false;
        new Thread(() -> runBuild(params)).start();
        return true;
    }

    @Override
    public boolean onStopJob(JobParameters params) {
        stopped = true;
        return true;
    }

    private void runBuild(JobParameters params) {
        String name = params.getExtras().getString(KEY_NAME, "");
        String url = params.getExtras().getString(KEY_URL, "");
        int zoom = params.getExtras().getInt(KEY_ZOOM, 90);
        String requestId = params.getExtras().getString(KEY_REQUEST_ID, "");
        long startedAt = params.getExtras().getLong(KEY_STARTED_AT, System.currentTimeMillis());

        if (TextUtils.isEmpty(name) || TextUtils.isEmpty(url) || TextUtils.isEmpty(requestId)) {
            HistoryStore.updateStatus(this, requestId, "נתונים חסרים");
            jobFinished(params, false);
            return;
        }

        try {
            if (!HistoryStore.isSubmitted(this, requestId)) {
                HistoryStore.updateStatus(this, requestId, "שולח לבנייה");

                JSONObject body = new JSONObject();
                body.put("app_name", name);
                body.put("app_url", url);
                body.put("app_zoom", zoom);
                body.put("request_id", requestId);

                String responseText = httpPostJson(BUILD_SERVICE_URL, body.toString());
                if (!TextUtils.isEmpty(responseText)) {
                    try {
                        JSONObject response = new JSONObject(responseText);
                        if (response.has("ok") && !response.optBoolean("ok", true)) {
                            HistoryStore.updateStatus(this, requestId, "הבקשה נדחתה");
                            jobFinished(params, false);
                            return;
                        }
                    } catch (Exception ignored) {
                    }
                }

                HistoryStore.markSubmitted(this, requestId);
            } else {
                HistoryStore.updateStatus(this, requestId, "בבנייה");
            }

            boolean ready = waitForBuild(requestId, name, startedAt);
            if (stopped) return;

            if (!ready) {
                HistoryStore.updateStatus(this, requestId, "ממתין לבדיקה נוספת");
                jobFinished(params, true);
                return;
            }

            startAutomaticDownload(name, requestId);
            jobFinished(params, false);

        } catch (Exception e) {
            if (stopped) return;
            HistoryStore.updateStatus(this, requestId, "ממתין לרשת");
            jobFinished(params, true);
        }
    }

    private boolean waitForBuild(String requestId, String appName, long requestStartedAt) {
        for (int i = 0; i < 60 && !stopped; i++) {
            try {
                Thread.sleep(5000);
                if (stopped) return false;

                String statusText = httpGet(BUILD_STATUS_URL + "&t=" + System.currentTimeMillis());
                JSONObject status = new JSONObject(statusText);

                if (requestId.equals(status.optString("request_id"))) {
                    return true;
                }

                String statusName = status.optString("app_name");
                String builtAt = status.optString("built_at");
                if (appName.equals(statusName) && !TextUtils.isEmpty(builtAt)) {
                    try {
                        long builtAtMillis = Instant.parse(builtAt).toEpochMilli();
                        if (builtAtMillis >= requestStartedAt - 5000) return true;
                    } catch (Exception ignored) {
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            } catch (Exception ignored) {
            }
        }
        return false;
    }

    private void startAutomaticDownload(String name, String requestId) throws Exception {
        DownloadManager manager = (DownloadManager) getSystemService(DOWNLOAD_SERVICE);
        if (manager == null) throw new Exception("DownloadManager unavailable");

        String stamp = new SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(new Date());
        String fileName = safeFileName(name) + "-" + stamp + ".apk";
        String downloadUrl = GENERATED_APK_URL + "?t=" + System.currentTimeMillis();

        DownloadManager.Request request = new DownloadManager.Request(Uri.parse(downloadUrl));
        request.setTitle(name + " - APK");
        request.setDescription("מוריד את קובץ ההתקנה");
        request.setMimeType("application/vnd.android.package-archive");
        request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
        request.setAllowedOverMetered(true);
        request.setAllowedOverRoaming(true);
        request.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, fileName);

        long downloadId = manager.enqueue(request);
        HistoryStore.markDownloadStarted(this, requestId, downloadId, fileName, System.currentTimeMillis());
    }

    private String safeFileName(String name) {
        String safe = name.replaceAll("[\\\\/:*?\"<>|]", "_").trim();
        if (safe.isEmpty()) safe = "generated-app";
        return safe;
    }

    private String httpPostJson(String targetUrl, String json) throws Exception {
        HttpURLConnection conn = (HttpURLConnection) new URL(targetUrl).openConnection();
        conn.setRequestMethod("POST");
        conn.setConnectTimeout(15000);
        conn.setReadTimeout(20000);
        conn.setDoOutput(true);
        conn.setInstanceFollowRedirects(true);
        conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");

        byte[] data = json.getBytes(StandardCharsets.UTF_8);
        try (OutputStream os = conn.getOutputStream()) {
            os.write(data);
        }

        int code = conn.getResponseCode();
        InputStream in = code >= 200 && code < 400 ? conn.getInputStream() : conn.getErrorStream();
        String text = readStream(in);
        conn.disconnect();
        if (code < 200 || code >= 400) throw new Exception("HTTP " + code);
        return text;
    }

    private String httpGet(String targetUrl) throws Exception {
        HttpURLConnection conn = (HttpURLConnection) new URL(targetUrl).openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(12000);
        conn.setReadTimeout(12000);
        conn.setUseCaches(false);
        conn.setRequestProperty("Accept", "application/vnd.github.raw+json");
        conn.setRequestProperty("Cache-Control", "no-cache");
        conn.setRequestProperty("Pragma", "no-cache");
        conn.setRequestProperty("User-Agent", "ShortcutBuilder");
        conn.setRequestProperty("X-GitHub-Api-Version", "2022-11-28");

        int code = conn.getResponseCode();
        InputStream in = code >= 200 && code < 400 ? conn.getInputStream() : conn.getErrorStream();
        String text = readStream(in);
        conn.disconnect();
        if (code < 200 || code >= 400) throw new Exception("HTTP " + code);
        return text;
    }

    private String readStream(InputStream in) throws Exception {
        if (in == null) return "";
        StringBuilder sb = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {
            String line;
            while ((line = br.readLine()) != null) sb.append(line);
        }
        return sb.toString();
    }
}
