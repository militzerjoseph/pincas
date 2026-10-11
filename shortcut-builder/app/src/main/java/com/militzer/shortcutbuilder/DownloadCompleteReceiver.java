package com.militzer.shortcutbuilder;

import android.app.DownloadManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;

public class DownloadCompleteReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (!DownloadManager.ACTION_DOWNLOAD_COMPLETE.equals(intent.getAction())) return;

        long downloadId = intent.getLongExtra(DownloadManager.EXTRA_DOWNLOAD_ID, -1L);
        if (downloadId < 0) return;

        boolean success = false;
        DownloadManager manager = (DownloadManager) context.getSystemService(Context.DOWNLOAD_SERVICE);

        if (manager != null) {
            DownloadManager.Query query = new DownloadManager.Query().setFilterById(downloadId);
            try (Cursor cursor = manager.query(query)) {
                if (cursor != null && cursor.moveToFirst()) {
                    int statusColumn = cursor.getColumnIndex(DownloadManager.COLUMN_STATUS);
                    if (statusColumn >= 0) {
                        success = cursor.getInt(statusColumn) == DownloadManager.STATUS_SUCCESSFUL;
                    }
                }
            } catch (Exception ignored) {
            }
        }

        HistoryStore.markDownloadComplete(context, downloadId, success, System.currentTimeMillis());
    }
}
