package com.militzer.shortcutbuilder;

import android.content.Context;
import android.content.SharedPreferences;

import org.json.JSONArray;
import org.json.JSONObject;

public final class HistoryStore {
    private static final String PREFS = "apk_build_history";
    private static final String KEY_RECORDS = "records";
    private static final int MAX_RECORDS = 100;

    private HistoryStore() { }

    public static synchronized void addRequest(Context context, String requestId, String name, long requestedAt) {
        try {
            JSONArray old = load(context);
            JSONArray next = new JSONArray();

            JSONObject item = new JSONObject();
            item.put("request_id", requestId);
            item.put("name", name);
            item.put("requested_at", requestedAt);
            item.put("status", "ממתין לבנייה");
            item.put("submitted", false);
            item.put("download_id", -1L);
            item.put("download_started_at", 0L);
            item.put("downloaded_at", 0L);
            item.put("file_name", "");
            next.put(item);

            for (int i = 0; i < old.length() && next.length() < MAX_RECORDS; i++) {
                JSONObject oldItem = old.optJSONObject(i);
                if (oldItem != null) next.put(oldItem);
            }
            save(context, next);
        } catch (Exception ignored) {
        }
    }

    public static synchronized JSONArray getRecords(Context context) {
        JSONArray src = load(context);
        JSONArray copy = new JSONArray();
        for (int i = 0; i < src.length(); i++) {
            JSONObject item = src.optJSONObject(i);
            if (item != null) copy.put(item);
        }
        return copy;
    }

    public static synchronized boolean isSubmitted(Context context, String requestId) {
        JSONArray records = load(context);
        for (int i = 0; i < records.length(); i++) {
            JSONObject item = records.optJSONObject(i);
            if (matches(item, requestId)) return item.optBoolean("submitted", false);
        }
        return false;
    }

    public static synchronized void markSubmitted(Context context, String requestId) {
        update(context, requestId, item -> {
            item.put("submitted", true);
            item.put("status", "בבנייה");
        });
    }

    public static synchronized void updateStatus(Context context, String requestId, String status) {
        update(context, requestId, item -> item.put("status", status));
    }

    public static synchronized void markDownloadStarted(Context context, String requestId, long downloadId, String fileName, long startedAt) {
        update(context, requestId, item -> {
            item.put("status", "מוריד");
            item.put("download_id", downloadId);
            item.put("download_started_at", startedAt);
            item.put("file_name", fileName);
        });
    }

    public static synchronized void markDownloadComplete(Context context, long downloadId, boolean success, long completedAt) {
        JSONArray records = load(context);
        boolean changed = false;

        for (int i = 0; i < records.length(); i++) {
            JSONObject item = records.optJSONObject(i);
            if (item != null && item.optLong("download_id", -1L) == downloadId) {
                try {
                    item.put("status", success ? "הורד" : "ההורדה נכשלה");
                    if (success) item.put("downloaded_at", completedAt);
                    changed = true;
                } catch (Exception ignored) {
                }
                break;
            }
        }

        if (changed) save(context, records);
    }

    private interface Editor {
        void edit(JSONObject item) throws Exception;
    }

    private static void update(Context context, String requestId, Editor editor) {
        JSONArray records = load(context);
        boolean changed = false;

        for (int i = 0; i < records.length(); i++) {
            JSONObject item = records.optJSONObject(i);
            if (matches(item, requestId)) {
                try {
                    editor.edit(item);
                    changed = true;
                } catch (Exception ignored) {
                }
                break;
            }
        }

        if (changed) save(context, records);
    }

    private static boolean matches(JSONObject item, String requestId) {
        return item != null && requestId.equals(item.optString("request_id"));
    }

    private static JSONArray load(Context context) {
        try {
            SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
            String raw = prefs.getString(KEY_RECORDS, "[]");
            return new JSONArray(raw == null ? "[]" : raw);
        } catch (Exception ignored) {
            return new JSONArray();
        }
    }

    private static void save(Context context, JSONArray records) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
                .edit()
                .putString(KEY_RECORDS, records.toString())
                .commit();
    }
}
