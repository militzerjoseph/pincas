package com.example.pincaswebapk;

import android.app.Activity;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import androidx.webkit.WebViewCompat;
import androidx.webkit.WebViewFeature;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.Locale;

public class MainActivity extends Activity {

    private static final String APP_URL = "https://script.google.com/macros/s/AKfycbyoJeN1G2EuGczP88itz2r2OKXH5GWL45c3ICe9L2kOHG2rNIFYJ98aRx0UPyZEIHyKxA/exec";
    private static final String BACKUP_SUBDIR = "גיבויים/פנקס מעטפת";
    private static final String BACKUP_RELATIVE_DIR = Environment.DIRECTORY_DOWNLOADS + "/" + BACKUP_SUBDIR + "/";

    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().setStatusBarColor(Color.WHITE);
        getWindow().setNavigationBarColor(Color.WHITE);
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR
        );

        webView = new WebView(this);
        webView.setFitsSystemWindows(true);
        setContentView(webView);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setLoadWithOverviewMode(false);
        settings.setUseWideViewPort(true);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(false);
        settings.setMediaPlaybackRequiresUserGesture(false);

        // Android exposes this object to every frame, including the Apps Script iframe.
        webView.addJavascriptInterface(new BackupBridge(this), "AndroidDownloads");

        // Apps Script HTML runs inside a sandboxed iframe. Inject the download hook at
        // document start in every frame, before the page's backup() code executes.
        installAllFrameBackupHook();

        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient());

        if (savedInstanceState == null) {
            webView.loadUrl(APP_URL);
        } else {
            webView.restoreState(savedInstanceState);
        }
    }

    private void installAllFrameBackupHook() {
        final String script =
                "(function(){" +
                "try{" +
                "if(window.__pincasAndroidBlobHook)return;" +
                "window.__pincasAndroidBlobHook=true;" +
                "if(typeof HTMLAnchorElement==='undefined')return;" +
                "var originalClick=HTMLAnchorElement.prototype.click;" +
                "HTMLAnchorElement.prototype.click=function(){" +
                "try{" +
                "var href=String(this.href||'');" +
                "var name=String(this.download||'');" +
                "if(name && href.indexOf('blob:')===0 && typeof AndroidDownloads!=='undefined'){" +
                "fetch(href).then(function(r){return r.blob();}).then(function(blob){" +
                "var reader=new FileReader();" +
                "reader.onloadend=function(){" +
                "try{AndroidDownloads.saveDataUrl(String(reader.result||''),name);}catch(e){console.error('PINCAS Android save',e);}" +
                "};" +
                "reader.readAsDataURL(blob);" +
                "}).catch(function(e){console.error('PINCAS blob read',e);});" +
                "return;" +
                "}" +
                "if(name && href.indexOf('data:')===0 && typeof AndroidDownloads!=='undefined'){" +
                "AndroidDownloads.saveDataUrl(href,name);" +
                "return;" +
                "}" +
                "}catch(e){console.error('PINCAS click hook',e);}" +
                "return originalClick.apply(this,arguments);" +
                "};" +
                "}catch(e){console.error('PINCAS hook install',e);}" +
                "})();";

        if (WebViewFeature.isFeatureSupported(WebViewFeature.DOCUMENT_START_SCRIPT)) {
            WebViewCompat.addDocumentStartJavaScript(
                    webView,
                    script,
                    Collections.singleton("*")
            );
        } else {
            // Very old WebView fallback. Modern Samsung/Android devices use the path above.
            webView.setWebViewClient(new WebViewClient() {
                @Override
                public void onPageFinished(WebView view, String url) {
                    super.onPageFinished(view, url);
                    view.evaluateJavascript(script, null);
                }
            });
        }
    }

    public class BackupBridge {
        private final Context context;

        BackupBridge(Context context) {
            this.context = context.getApplicationContext();
        }

        @JavascriptInterface
        public void saveDataUrl(String dataUrl, String requestedFileName) {
            try {
                if (dataUrl == null || dataUrl.isEmpty()) {
                    throw new IllegalArgumentException("קובץ גיבוי ריק");
                }

                int comma = dataUrl.indexOf(',');
                if (comma < 0) {
                    throw new IllegalArgumentException("קובץ גיבוי לא תקין");
                }

                String header = dataUrl.substring(0, comma);
                String body = dataUrl.substring(comma + 1);

                String mimeType = "application/octet-stream";
                if (header.startsWith("data:")) {
                    int semi = header.indexOf(';');
                    mimeType = semi > 5 ? header.substring(5, semi) : header.substring(5);
                    if (mimeType.trim().isEmpty()) {
                        mimeType = "application/octet-stream";
                    }
                }

                byte[] bytes;
                if (header.contains(";base64")) {
                    bytes = Base64.decode(body, Base64.DEFAULT);
                } else {
                    bytes = Uri.decode(body).getBytes(StandardCharsets.UTF_8);
                }

                String fileName = sanitizeFileName(requestedFileName);
                if (!fileName.contains(".")) {
                    String lowerMime = mimeType.toLowerCase(Locale.ROOT);
                    fileName += lowerMime.contains("json") ? ".json" : ".dat";
                }

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    saveWithMediaStore(bytes, fileName, mimeType);
                } else {
                    saveLegacy(bytes, fileName);
                }

                String finalFileName = fileName;
                runOnUiThread(() -> Toast.makeText(
                        MainActivity.this,
                        "הגיבוי נשמר ב-Download/גיבויים/פנקס מעטפת/" + finalFileName,
                        Toast.LENGTH_LONG
                ).show());

            } catch (Exception e) {
                String message = e.getMessage();
                if (message == null || message.trim().isEmpty()) {
                    message = e.getClass().getSimpleName();
                }
                String finalMessage = message;
                runOnUiThread(() -> Toast.makeText(
                        MainActivity.this,
                        "שגיאה בשמירת הגיבוי: " + finalMessage,
                        Toast.LENGTH_LONG
                ).show());
            }
        }

        private void saveWithMediaStore(byte[] bytes, String fileName, String mimeType) throws Exception {
            ContentResolver resolver = context.getContentResolver();
            ContentValues values = new ContentValues();
            values.put(MediaStore.Downloads.DISPLAY_NAME, fileName);
            values.put(MediaStore.Downloads.MIME_TYPE, mimeType);
            values.put(MediaStore.Downloads.RELATIVE_PATH, BACKUP_RELATIVE_DIR);
            values.put(MediaStore.Downloads.IS_PENDING, 1);

            Uri uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
            if (uri == null) {
                throw new IllegalStateException("לא ניתן ליצור קובץ גיבוי");
            }

            boolean success = false;
            try (OutputStream output = resolver.openOutputStream(uri)) {
                if (output == null) {
                    throw new IllegalStateException("לא ניתן לפתוח קובץ גיבוי");
                }
                output.write(bytes);
                output.flush();
                success = true;
            } finally {
                if (!success) {
                    resolver.delete(uri, null, null);
                }
            }

            ContentValues done = new ContentValues();
            done.put(MediaStore.Downloads.IS_PENDING, 0);
            resolver.update(uri, done, null, null);
        }

        @SuppressWarnings("deprecation")
        private void saveLegacy(byte[] bytes, String fileName) throws Exception {
            File dir = new File(
                    Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS),
                    BACKUP_SUBDIR
            );
            if (!dir.exists() && !dir.mkdirs()) {
                throw new IllegalStateException("לא ניתן ליצור תיקיית גיבוי");
            }

            File out = new File(dir, fileName);
            try (FileOutputStream stream = new FileOutputStream(out)) {
                stream.write(bytes);
                stream.flush();
            }
        }
    }

    private static String sanitizeFileName(String name) {
        if (name == null || name.trim().isEmpty()) {
            return "pincas_backup.json";
        }
        String clean = name.replaceAll("[\\\\/:*?\"<>|]", "_").trim();
        return clean.isEmpty() ? "pincas_backup.json" : clean;
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
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
