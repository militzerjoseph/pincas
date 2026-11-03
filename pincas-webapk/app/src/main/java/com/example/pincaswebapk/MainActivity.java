package com.example.pincaswebapk;

import android.Manifest;
import android.app.Activity;
import android.app.DownloadManager;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.URLUtil;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends Activity {

    private static final String APP_URL = "https://script.google.com/macros/s/AKfycbyoJeN1G2EuGczP88itz2r2OKXH5GWL45c3ICe9L2kOHG2rNIFYJ98aRx0UPyZEIHyKxA/exec";
    private static final String BACKUP_SUBDIR = "גיבויים/פנקס מעטפת";
    private static final String BACKUP_RELATIVE_DIR = Environment.DIRECTORY_DOWNLOADS + "/" + BACKUP_SUBDIR;
    private static final int REQ_STORAGE = 501;

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

        webView.addJavascriptInterface(new DownloadBridge(this), "AndroidDownloads");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                installDownloadInterceptor(view);
            }
        });
        webView.setWebChromeClient(new WebChromeClient());

        // Fallback for normal network downloads. The PINCAS backup itself is a
        // programmatic blob download and is intercepted by JavaScript below.
        webView.setDownloadListener((url, userAgent, contentDisposition, mimeType, contentLength) -> {
            String fileName = URLUtil.guessFileName(url, contentDisposition, mimeType);
            if (fileName == null || fileName.trim().isEmpty() || fileName.startsWith("blob")) {
                fileName = defaultBackupName(mimeType);
            }

            if (url != null && url.startsWith("blob:")) {
                saveBlobFromPage(url, fileName);
            } else if (url != null && url.startsWith("data:")) {
                String js = "(function(){try{AndroidDownloads.saveDataUrl(" +
                        jsQuote(url) + "," + jsQuote(fileName) + ");}catch(e){console.error(e);}})();";
                webView.evaluateJavascript(js, null);
            } else {
                enqueueNormalDownload(url, userAgent, fileName, mimeType);
            }
        });

        if (savedInstanceState == null) {
            webView.loadUrl(APP_URL);
        } else {
            webView.restoreState(savedInstanceState);
        }
    }

    /**
     * PINCAS creates its backup with:
     *   const b = new Blob(...)
     *   a.href = URL.createObjectURL(b)
     *   a.download = '...json'
     *   a.click()
     *
     * Android WebView does not reliably forward a programmatic blob anchor click
     * to DownloadListener. Intercept the anchor click inside the loaded page,
     * convert the blob to a data URL and pass it directly to AndroidDownloads.
     */
    private void installDownloadInterceptor(WebView view) {
        String js =
                "(function(){" +
                "try{" +
                "if(window.__pincasAndroidDownloadHook)return;" +
                "window.__pincasAndroidDownloadHook=true;" +
                "var originalClick=HTMLAnchorElement.prototype.click;" +
                "HTMLAnchorElement.prototype.click=function(){" +
                "try{" +
                "var href=this.href||'';" +
                "var name=this.download||'';" +
                "if(name&&href.indexOf('blob:')===0){" +
                "fetch(href).then(function(r){return r.blob();}).then(function(b){" +
                "var fr=new FileReader();" +
                "fr.onloadend=function(){try{AndroidDownloads.saveDataUrl(fr.result,name);}catch(e){console.error(e);}};" +
                "fr.readAsDataURL(b);" +
                "}).catch(function(e){console.error('PINCAS blob backup',e);});" +
                "return;" +
                "}" +
                "if(name&&href.indexOf('data:')===0){" +
                "AndroidDownloads.saveDataUrl(href,name);" +
                "return;" +
                "}" +
                "}catch(e){console.error('PINCAS download interceptor',e);}" +
                "return originalClick.apply(this,arguments);" +
                "};" +
                "}catch(e){console.error('PINCAS hook install',e);}" +
                "})();";
        view.evaluateJavascript(js, null);
    }

    private void saveBlobFromPage(String blobUrl, String fileName) {
        String js = "(async function(){try{" +
                "const r=await fetch(" + jsQuote(blobUrl) + ");" +
                "const b=await r.blob();" +
                "const fr=new FileReader();" +
                "fr.onloadend=function(){AndroidDownloads.saveDataUrl(fr.result," + jsQuote(fileName) + ");};" +
                "fr.readAsDataURL(b);" +
                "}catch(e){console.error(e);}})();";
        webView.evaluateJavascript(js, null);
    }

    private void enqueueNormalDownload(String url, String userAgent, String fileName, String mimeType) {
        try {
            if (url == null || url.trim().isEmpty()) {
                throw new IllegalArgumentException("כתובת הורדה ריקה");
            }

            DownloadManager.Request request = new DownloadManager.Request(Uri.parse(url));
            request.setTitle(fileName);
            request.setDescription("גיבוי פנקס");
            request.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);

            if (mimeType != null && !mimeType.trim().isEmpty()) {
                request.setMimeType(mimeType);
            }
            if (userAgent != null && !userAgent.trim().isEmpty()) {
                request.addRequestHeader("User-Agent", userAgent);
            }
            String cookie = CookieManager.getInstance().getCookie(url);
            if (cookie != null && !cookie.trim().isEmpty()) {
                request.addRequestHeader("Cookie", cookie);
            }

            request.setDestinationInExternalPublicDir(
                    Environment.DIRECTORY_DOWNLOADS,
                    BACKUP_SUBDIR + "/" + sanitizeFileName(fileName)
            );

            DownloadManager dm = (DownloadManager) getSystemService(DOWNLOAD_SERVICE);
            if (dm == null) {
                throw new IllegalStateException("DownloadManager לא זמין");
            }
            dm.enqueue(request);

            Toast.makeText(this,
                    "הגיבוי נשמר ב-Download/גיבויים/פנקס מעטפת",
                    Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this,
                    "לא ניתן לשמור את הגיבוי: " + safeMessage(e),
                    Toast.LENGTH_LONG).show();
        }
    }

    private static String defaultBackupName(String mimeType) {
        String ext = ".json";
        if (mimeType != null) {
            String m = mimeType.toLowerCase(Locale.ROOT);
            if (m.contains("zip")) ext = ".zip";
            else if (m.contains("csv")) ext = ".csv";
            else if (m.contains("text/plain")) ext = ".txt";
            else if (m.contains("html")) ext = ".html";
        }
        return "pincas_backup_" +
                new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(new Date()) + ext;
    }

    private static String sanitizeFileName(String name) {
        if (name == null || name.trim().isEmpty()) return defaultBackupName(null);
        String s = name.replaceAll("[\\\\/:*?\"<>|]", "_").trim();
        return s.isEmpty() ? defaultBackupName(null) : s;
    }

    private static String jsQuote(String s) {
        if (s == null) return "null";
        return "\"" + s
                .replace("\\", "\\\\")
                .replace("\"", "\\\"")
                .replace("\n", "\\n")
                .replace("\r", "\\r") + "\"";
    }

    private static String safeMessage(Exception e) {
        String m = e.getMessage();
        return (m == null || m.trim().isEmpty()) ? e.getClass().getSimpleName() : m;
    }

    public class DownloadBridge {
        private final Context context;

        DownloadBridge(Context context) {
            this.context = context.getApplicationContext();
        }

        @JavascriptInterface
        public void saveDataUrl(String dataUrl, String requestedFileName) {
            try {
                if (dataUrl == null) throw new IllegalArgumentException("קובץ גיבוי ריק");

                int comma = dataUrl.indexOf(',');
                if (comma < 0) throw new IllegalArgumentException("קובץ גיבוי לא תקין");

                String header = dataUrl.substring(0, comma);
                String body = dataUrl.substring(comma + 1);

                String mimeType = "application/octet-stream";
                if (header.startsWith("data:")) {
                    int semi = header.indexOf(';');
                    mimeType = semi > 5 ? header.substring(5, semi) : header.substring(5);
                    if (mimeType.trim().isEmpty()) mimeType = "application/octet-stream";
                }

                byte[] bytes;
                if (header.contains(";base64")) {
                    bytes = Base64.decode(body, Base64.DEFAULT);
                } else {
                    bytes = Uri.decode(body).getBytes("UTF-8");
                }

                String fileName = sanitizeFileName(requestedFileName);
                if (!fileName.contains(".")) {
                    String m = mimeType.toLowerCase(Locale.ROOT);
                    if (m.contains("json")) fileName += ".json";
                    else if (m.contains("zip")) fileName += ".zip";
                    else if (m.contains("csv")) fileName += ".csv";
                    else if (m.contains("text/plain")) fileName += ".txt";
                    else fileName += ".dat";
                }

                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    saveWithMediaStore(bytes, fileName, mimeType);
                } else {
                    if (checkSelfPermission(Manifest.permission.WRITE_EXTERNAL_STORAGE)
                            != PackageManager.PERMISSION_GRANTED) {
                        runOnUiThread(() -> requestPermissions(
                                new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, REQ_STORAGE));
                        throw new IllegalStateException("נא לאשר הרשאת אחסון וללחוץ שוב על גיבוי");
                    }
                    saveLegacy(bytes, fileName);
                }

                String finalName = fileName;
                runOnUiThread(() -> Toast.makeText(MainActivity.this,
                        "הגיבוי נשמר ב-Download/גיבויים/פנקס מעטפת/" + finalName,
                        Toast.LENGTH_LONG).show());

            } catch (Exception e) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this,
                        "שגיאה בשמירת הגיבוי: " + safeMessage(e),
                        Toast.LENGTH_LONG).show());
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
            if (uri == null) throw new IllegalStateException("לא ניתן ליצור קובץ גיבוי");

            boolean success = false;
            try (OutputStream os = resolver.openOutputStream(uri)) {
                if (os == null) throw new IllegalStateException("לא ניתן לפתוח קובץ גיבוי");
                os.write(bytes);
                os.flush();
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
            try (FileOutputStream fos = new FileOutputStream(out)) {
                fos.write(bytes);
                fos.flush();
            }
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
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
