package com.militzer.shortcutbuilder;

import android.app.DownloadManager;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.net.Uri;
import android.os.Environment;
import android.os.IBinder;
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

public class BuildForegroundService extends Service {

    public static final String KEY_NAME = "name";
    public static final String KEY_URL = "url";
    public static final String KEY_ZOOM = "zoom";
    public static final String KEY_REQUEST_ID = "request_id";
    public static final String KEY_STARTED_AT = "started_at";

    private static final String CHANNEL_ID = "apk_builds";
    private static final int NOTIFICATION_ID = 7101;

    private static final String BUILD_SERVICE_URL =
            "https://script.google.com/macros/s/AKfycbw_vuH5-nlE6l1-AtP4GNRYaLTDC1X1wnRrUeUjUL1YssfK951pkd7DmMl9_bya81QF/exec";
    private static final String BUILD_STATUS_URL =
            "https://api.github.com/repos/militzerjoseph/pincas/contents/output/build-status.json?ref=shortcut-builder-output";
    private static final String GENERATED_APK_URL =
            "https://raw.githubusercontent.com/militzerjoseph/pincas/shortcut-builder-output/output/generated-app.apk";

    private static volatile boolean running = false;
    private volatile boolean stopped = false;

    public static boolean isRunning() {
        return running;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        running = true;
        createNotificationChannel();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) {
            stopSelf(startId);
            return START_NOT_STICKY;
        }

        String name = intent.getStringExtra(KEY_NAME);
        String url = intent.getStringExtra(KEY_URL);
        int zoom = intent.getIntExtra(KEY_ZOOM, 90);
        String requestId = intent.getStringExtra(KEY_REQUEST_ID);
        long startedAt = intent.getLongExtra(KEY_STARTED_AT, System.currentTimeMillis());

        startForeground(NOTIFICATION_ID, notification("מתחיל יצירת APK..."));

        new Thread(() -> runBuild(name, url, zoom, requestId, startedAt, startId)).start();
        return START_NOT_STICKY;
    }

    @Override
    public void onDestroy() {
        stopped = true;
        running = false;
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    private void runBuild(String name, String url, int zoom, String requestId, long startedAt, int startId) {
        try {
            if (TextUtils.isEmpty(name) || TextUtils.isEmpty(url) || TextUtils.isEmpty(requestId)) {
                if (!TextUtils.isEmpty(requestId)) {
                    HistoryStore.updateStatus(this, requestId, "נתונים חסרים");
                }
                finishService(startId);
                return;
            }

            HistoryStore.updateStatus(this, requestId, "שולח לבנייה");
            updateNotification("שולח את הבקשה לשרת...");

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
                        updateNotification("הבקשה נדחתה");
                        finishService(startId);
                        return;
                    }
                } catch (Exception ignored) {
                }
            }

            HistoryStore.markSubmitted(this, requestId);
            updateNotification("ה-APK בבנייה. אפשר להשתמש בטלפון כרגיל.");

            boolean ready = waitForBuild(requestId, name, startedAt);
            if (stopped) return;

            if (!ready) {
                HistoryStore.updateStatus(this, requestId, "לא הושלם בזמן");
                updateNotification("הבנייה עדיין לא הסתיימה");
                finishService(startId);
                return;
            }

            startAutomaticDownload(name, requestId);
            updateNotification("ה-APK מוכן וההורדה התחילה");
            finishService(startId);

        } catch (Exception e) {
            if (!stopped && !TextUtils.isEmpty(requestId)) {
                HistoryStore.updateStatus(this, requestId, "שגיאה בבנייה");
                updateNotification("אירעה שגיאה בתהליך הבנייה");
            }
            finishService(startId);
        }
    }

    private boolean waitForBuild(String requestId, String appName, long requestStartedAt) {
        for (int i = 0; i < 120 && !stopped; i++) {
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

    private void createNotificationChannel() {
        NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "יצירת APK",
                NotificationManager.IMPORTANCE_LOW);
        channel.setDescription("מציג את מצב בניית ה-APK ברקע");
        NotificationManager manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (manager != null) manager.createNotificationChannel(channel);
    }

    private Notification notification(String text) {
        Intent historyIntent = new Intent(this, HistoryActivity.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(
                this,
                0,
                historyIntent,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        return new Notification.Builder(this, CHANNEL_ID)
                .setContentTitle("יוצר מעטפות")
                .setContentText(text)
                .setSmallIcon(android.R.drawable.stat_sys_download)
                .setContentIntent(pendingIntent)
                .setOngoing(true)
                .build();
    }

    private void updateNotification(String text) {
        NotificationManager manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        if (manager != null) manager.notify(NOTIFICATION_ID, notification(text));
    }

    private void finishService(int startId) {
        stopForeground(STOP_FOREGROUND_REMOVE);
        stopSelf(startId);
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
