package com.militzerjoseph.monthlyincome2;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ContentValues;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.FileInputStream;
import java.io.InputStream;
import java.io.OutputStream;

public class MainActivity extends Activity {
    private WebView webView;

    @SuppressLint({"SetJavaScriptEnabled", "JavascriptInterface"})
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().setStatusBarColor(Color.rgb(246, 239, 221));
        getWindow().setNavigationBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR);

        webView = new WebView(this);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(false);
        settings.setAllowContentAccess(false);
        settings.setAllowFileAccess(true);
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(false);
        settings.setMediaPlaybackRequiresUserGesture(true);

        webView.addJavascriptInterface(new AndroidBridge(), "Android");
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri uri = request.getUrl();
                String url = uri == null ? "" : uri.toString();
                return !url.startsWith("file:///android_asset/");
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                return url == null || !url.startsWith("file:///android_asset/");
            }
        });

        if (savedInstanceState == null) {
            webView.loadUrl("file:///android_asset/index.html");
        } else {
            webView.restoreState(savedInstanceState);
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        webView.saveState(outState);
        super.onSaveInstanceState(outState);
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.removeJavascriptInterface("Android");
            webView.loadUrl("about:blank");
            webView.stopLoading();
            webView.setWebViewClient(null);
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }

    public final class AndroidBridge {
        @JavascriptInterface
        public void backupApk() {
            runOnUiThread(() -> performApkBackup());
        }

        @JavascriptInterface
        public String getVersionName() {
            try {
                PackageInfo info = getPackageManager().getPackageInfo(getPackageName(), 0);
                return info.versionName == null ? "" : info.versionName;
            } catch (PackageManager.NameNotFoundException e) {
                return "";
            }
        }
    }

    private void performApkBackup() {
        Uri destination = null;
        try {
            String sourcePath = getApplicationInfo().sourceDir;
            ContentValues values = new ContentValues();
            values.put(MediaStore.MediaColumns.DISPLAY_NAME, "MonthlyIncomeCalculator_v1.apk");
            values.put(MediaStore.MediaColumns.MIME_TYPE, "application/vnd.android.package-archive");
            values.put(MediaStore.MediaColumns.RELATIVE_PATH,
                    Environment.DIRECTORY_DOWNLOADS + "/גיבויים/מחשבון הכנסה חודשית");

            destination = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (destination == null) {
                throw new IllegalStateException("Could not create backup file");
            }

            try (InputStream in = new FileInputStream(sourcePath);
                 OutputStream out = getContentResolver().openOutputStream(destination, "w")) {
                if (out == null) {
                    throw new IllegalStateException("Could not open backup destination");
                }
                byte[] buffer = new byte[64 * 1024];
                int read;
                while ((read = in.read(buffer)) != -1) {
                    out.write(buffer, 0, read);
                }
                out.flush();
            }

            Toast.makeText(this,
                    "ה-APK גובה בהצלחה לתיקיית Download/גיבויים/מחשבון הכנסה חודשית",
                    Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            if (destination != null) {
                try {
                    getContentResolver().delete(destination, null, null);
                } catch (Exception ignored) {
                }
            }
            Toast.makeText(this, "הגיבוי נכשל: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }
}
