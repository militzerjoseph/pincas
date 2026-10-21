package com.example.pincashybrid

import android.app.Activity
import android.content.ContentValues
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.provider.DocumentsContract
import android.provider.MediaStore
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import org.json.JSONObject
import java.security.MessageDigest
import java.time.Instant
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

class MainActivity : AppCompatActivity() {
    private lateinit var webView: WebView
    private val printViews = mutableListOf<WebView>()
    private val worker = Executors.newSingleThreadExecutor()
    private val backupBusy = AtomicBoolean(false)
    private val prefs by lazy { getSharedPreferences("pincas_hybrid_settings", MODE_PRIVATE) }
    private val restoreRequest = 7001
    private val cloudFolderRequest = 7002
    private val localFolderRequest = 7003

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, true)
        supportActionBar?.hide()
        setContentView(R.layout.activity_main)
        webView = findViewById(R.id.webView)
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView, request: android.webkit.WebResourceRequest): Boolean {
                // The native bridges belong exclusively to the bundled ledger page.
                return request.url.toString() != "file:///android_asset/index.html"
            }
        }
        webView.webChromeClient = WebChromeClient()
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            allowFileAccess = true
            allowContentAccess = true
            cacheMode = WebSettings.LOAD_DEFAULT
            useWideViewPort = true
            loadWithOverviewMode = false
            textZoom = 100
            builtInZoomControls = false
            displayZoomControls = false
            setSupportZoom(false)
        }
        webView.addJavascriptInterface(PrintBridge(), "AndroidPrint")
        webView.addJavascriptInterface(BackupBridge(), "AndroidBackup")
        webView.addJavascriptInterface(RestoreBridge(), "AndroidRestore")
        webView.addJavascriptInterface(DisplayBridge(), "AndroidDisplay")
        webView.addJavascriptInterface(CloudBridge(), "AndroidCloud")
        webView.addJavascriptInterface(FoldersBridge(), "AndroidFolders")
        webView.setInitialScale(prefs.getInt("display_scale_percent", 80).coerceIn(60, 120))
        if (savedInstanceState == null) webView.loadUrl("file:///android_asset/index.html")
        else if (webView.restoreState(savedInstanceState) == null) webView.loadUrl("file:///android_asset/index.html")
    }

    private inner class PrintBridge {
        @JavascriptInterface fun printReport(html: String, landscape: Boolean) {
            runOnUiThread {
                if (isDestroyed || isFinishing) return@runOnUiThread
                val reportView = WebView(this@MainActivity)
                printViews.add(reportView)
                reportView.settings.javaScriptEnabled = false
                reportView.settings.allowFileAccess = false
                reportView.settings.allowContentAccess = false
                reportView.webViewClient = object : WebViewClient() {
                    private var submitted = false
                    override fun onPageFinished(view: WebView, url: String) {
                        if (submitted || isDestroyed || isFinishing) return
                        submitted = true
                        try {
                            val manager = getSystemService(android.content.Context.PRINT_SERVICE) as android.print.PrintManager
                            val media = if (landscape) android.print.PrintAttributes.MediaSize.ISO_A4.asLandscape()
                                else android.print.PrintAttributes.MediaSize.ISO_A4.asPortrait()
                            val attrs = android.print.PrintAttributes.Builder().setMediaSize(media).build()
                            manager.print("פנקס חדש — דוח", view.createPrintDocumentAdapter("דוח פנקס"), attrs)
                        } catch (_: Exception) { toast("לא ניתן לפתוח את שירות ההדפסה במכשיר") }
                    }
                }
                reportView.loadDataWithBaseURL(null, html, "text/html", "UTF-8", null)
            }
        }
    }

    private fun treeKey(kind: String) = if (kind == "cloud") "cloud_backup_tree_uri" else "local_backup_tree_uri"
    private fun lastKey(kind: String) = "${kind}_last_success_at"
    private fun documentUri(tree: Uri) = DocumentsContract.buildDocumentUriUsingTree(tree, DocumentsContract.getTreeDocumentId(tree))

    private fun folderName(tree: Uri): String {
        contentResolver.query(documentUri(tree), arrayOf(DocumentsContract.Document.COLUMN_DISPLAY_NAME), null, null, null)?.use { c ->
            if (c.moveToFirst()) return c.getString(0) ?: "תיקייה שנבחרה"
        }
        throw IllegalStateException("Folder unavailable")
    }

    private fun hasFolderAccess(tree: Uri): Boolean = contentResolver.persistedUriPermissions.any {
        it.uri == tree && it.isReadPermission && it.isWritePermission
    }

    private fun folderState(kind: String): JSONObject {
        val raw = prefs.getString(treeKey(kind), null)
        val result = JSONObject().put("configured", !raw.isNullOrBlank())
            .put("lastSuccessAt", prefs.getString(lastKey(kind), ""))
            .put("lastProgramAt", prefs.getString(lastKey(kind) + "_program", ""))
        if (raw.isNullOrBlank()) {
            return result.put("available", kind == "local")
                .put("name", if (kind == "local") "Download/גיבויים/פנקס חדש" else "לא נבחרה תיקייה")
        }
        val uri = Uri.parse(raw)
        val rootName = prefs.getString("${kind}_folder_name", "תיקייה שנבחרה") ?: "תיקייה שנבחרה"
        val name = if (rootName == "פנקס חדש") rootName else "$rootName / פנקס חדש"
        // Do not query a cloud provider merely to paint the settings screen.
        return result.put("available", hasFolderAccess(uri)).put("name", name)
    }

    private fun backupState(): String = JSONObject()
        .put("local", folderState("local"))
        .put("cloud", folderState("cloud"))
        .put("running", backupBusy.get())
        .put("lastResult", prefs.getString("last_backup_result", ""))
        .put("lastDataResult", prefs.getString("last_data_backup_result", ""))
        .toString()

    private fun notifyPage(functionName: String, json: String? = null) {
        runOnUiThread {
            if (!isDestroyed && !isFinishing) {
                val argument = json?.let { JSONObject.quote(it) } ?: ""
                webView.evaluateJavascript("if(window.$functionName){window.$functionName($argument);}", null)
            }
        }
    }

    private fun toast(message: String) = runOnUiThread {
        if (!isDestroyed) Toast.makeText(this, message, Toast.LENGTH_LONG).show()
    }

    private inner class FoldersBridge {
        @JavascriptInterface fun getBackupState(): String = backupState()
        @JavascriptInterface fun chooseLocalFolder() { chooseFolder("local") }
        @JavascriptInterface fun chooseCloudFolder() { chooseFolder("cloud") }
        @JavascriptInterface fun clearLocalFolder() { clearFolder("local") }
        @JavascriptInterface fun clearCloudFolder() { clearFolder("cloud") }
    }

    // Preserve interfaces used by earlier versions of the HTML.
    private inner class CloudBridge {
        @JavascriptInterface fun chooseCloudFolder() { chooseFolder("cloud") }
        @JavascriptInterface fun hasCloudFolder(): Boolean = !prefs.getString(treeKey("cloud"), null).isNullOrBlank()
        @JavascriptInterface fun clearCloudFolder(): Boolean { clearFolder("cloud"); return true }
    }

    private fun chooseFolder(kind: String) {
        if (backupBusy.get()) { toast("יש להמתין לסיום הגיבוי"); return }
        runOnUiThread {
            val intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE).apply {
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION or
                    Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION or Intent.FLAG_GRANT_PREFIX_URI_PERMISSION)
                prefs.getString(treeKey(kind), null)?.let { putExtra(DocumentsContract.EXTRA_INITIAL_URI, Uri.parse(it)) }
            }
            try { startActivityForResult(intent, if (kind == "local") localFolderRequest else cloudFolderRequest) }
            catch (_: Exception) { toast("לא ניתן לפתוח את בורר התיקיות במכשיר") }
        }
    }

    private fun releaseIfUnused(raw: String?) {
        if (raw.isNullOrBlank()) return
        if (listOf("local", "cloud").any { prefs.getString(treeKey(it), null) == raw }) return
        try { contentResolver.releasePersistableUriPermission(Uri.parse(raw), Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION) }
        catch (_: Exception) { }
    }

    private fun clearFolder(kind: String) {
        if (backupBusy.get()) { toast("יש להמתין לסיום הגיבוי"); return }
        val old = prefs.getString(treeKey(kind), null)
        prefs.edit().remove(treeKey(kind)).remove("${kind}_folder_name").remove(lastKey(kind)).remove(lastKey(kind) + "_program").apply()
        releaseIfUnused(old)
        notifyPage("backupFoldersChangedFromAndroid")
    }

    private inner class BackupBridge {
        @JavascriptInterface fun saveBackupAsync(json: String, fileName: String): Boolean = startBackup(json, fileName, false)
        @JavascriptInterface fun backupProgramAsync(): Boolean = startBackup(null, null, true)
    }

    private fun startBackup(json: String?, fileName: String?, program: Boolean): Boolean {
        if (!backupBusy.compareAndSet(false, true)) return false
        val localTree = prefs.getString(treeKey("local"), null)
        val cloudTree = prefs.getString(treeKey("cloud"), null)
        val localName = folderState("local").optString("name")
        val cloudName = folderState("cloud").optString("name")
        worker.execute {
            try {
                val bytes: ByteArray
                val safeName: String
                val mime: String
                if (program) {
                    check(applicationInfo.splitSourceDirs.isNullOrEmpty()) { "Split APK unsupported" }
                    bytes = java.io.File(applicationInfo.sourceDir).readBytes()
                    val version = packageManager.getPackageInfo(packageName, 0).longVersionCode
                    val hash = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }.take(12)
                    safeName = "פנקס_חדש_תוכנית_v${version}_${hash}.apk"
                    mime = "application/vnd.android.package-archive"
                } else {
                    val obj = JSONObject(requireNotNull(json))
                    require(obj.optJSONArray("tx") != null && obj.optJSONArray("incomeCats") != null && obj.optJSONArray("expenseCats") != null)
                    bytes = json.toByteArray(Charsets.UTF_8)
                    safeName = requireNotNull(fileName).replace(Regex("[\\\\/:*?\"<>|]"), "_").take(180)
                    require(safeName.endsWith(".json"))
                    mime = "application/json"
                }
                val now = Instant.now().toString()
                val summary = BackupCoordinator.run(
                    local = { if (localTree.isNullOrBlank()) saveToDownloads(bytes, safeName, mime, program) else saveToTree(bytes, safeName, localTree, mime, program) },
                    cloud = if (cloudTree.isNullOrBlank()) null else ({ saveToTree(bytes, safeName, cloudTree, mime, program) })
                )
                val local = attemptJson(summary.local, true, localName)
                val cloud = if (summary.cloud == null) JSONObject().put("configured", false).put("ok", false).put("name", cloudName)
                    else attemptJson(summary.cloud, true, cloudName)
                val result = JSONObject().put("createdAt", now).put("fileName", safeName)
                    .put("kind", if (program) "program" else "data")
                    .put("local", local).put("cloud", cloud)
                    .put("anySuccess", summary.anySuccess).put("allConfiguredSucceeded", summary.allConfiguredSucceeded)
                prefs.edit().apply {
                    val suffix = if (program) "_program" else ""
                    if (summary.local.ok) putString(lastKey("local") + suffix, now)
                    if (summary.cloud?.ok == true) putString(lastKey("cloud") + suffix, now)
                    putString("last_backup_result", result.toString())
                    if (!program) putString("last_data_backup_result", result.toString())
                }.apply()
                backupBusy.set(false)
                notifyPage("backupFinishedFromAndroid", result.toString())
            } catch (_: Exception) {
                backupBusy.set(false)
                val result = JSONObject().put("anySuccess", false).put("allConfiguredSucceeded", false)
                    .put("kind", if (program) "program" else "data")
                    .put("error", "הגיבוי לא הושלם. נסה שוב; הנתונים נשארו באפליקציה.")
                prefs.edit().putString("last_backup_result", result.toString()).apply()
                notifyPage("backupFinishedFromAndroid", result.toString())
            }
        }
        return true
    }

    private fun attemptJson(attempt: BackupAttempt, configured: Boolean, name: String) = JSONObject()
        .put("ok", attempt.ok).put("configured", configured).put("name", name)
        .put("error", attempt.error).put("skipped", attempt.skipped)

    private fun verifyBytes(uri: Uri, expected: ByteArray) {
        val expectedDigest = MessageDigest.getInstance("SHA-256").digest(expected)
        val digest = MessageDigest.getInstance("SHA-256")
        contentResolver.openInputStream(uri)?.use { input ->
            val buffer = ByteArray(8192)
            while (true) { val n = input.read(buffer); if (n < 0) break; digest.update(buffer, 0, n) }
        } ?: throw IllegalStateException("Cannot verify saved file")
        check(MessageDigest.isEqual(expectedDigest, digest.digest())) { "Verification failed" }
    }

    private fun findChild(tree: Uri, parent: Uri, name: String): Uri? {
        val children = DocumentsContract.buildChildDocumentsUriUsingTree(tree, DocumentsContract.getDocumentId(parent))
        contentResolver.query(children, arrayOf(DocumentsContract.Document.COLUMN_DOCUMENT_ID, DocumentsContract.Document.COLUMN_DISPLAY_NAME), null, null, null)?.use { c ->
            while (c.moveToNext()) if (c.getString(1) == name) return DocumentsContract.buildDocumentUriUsingTree(tree, c.getString(0))
        }
        return null
    }

    private fun appBackupFolder(tree: Uri): Uri {
        val parent = documentUri(tree)
        if (folderName(tree) == "פנקס חדש") return parent
        return findChild(tree, parent, "פנקס חדש") ?: DocumentsContract.createDocument(
            contentResolver, parent, DocumentsContract.Document.MIME_TYPE_DIR, "פנקס חדש"
        ) ?: throw IllegalStateException("Cannot create app backup folder")
    }

    private fun saveToTree(bytes: ByteArray, fileName: String, treeString: String, mime: String, skipExisting: Boolean): Boolean {
        val tree = Uri.parse(treeString)
        check(hasFolderAccess(tree)) { "Folder permission expired" }
        val parent = appBackupFolder(tree)
        if (skipExisting) findChild(tree, parent, fileName)?.let {
            try { verifyBytes(it, bytes); return false } catch (_: Exception) { /* preserve an unreadable or different file */ }
        }
        val uri = DocumentsContract.createDocument(contentResolver, parent, mime, fileName)
            ?: throw IllegalStateException("Cannot create backup")
        try {
            contentResolver.openOutputStream(uri, "w")?.use { it.write(bytes); it.flush() }
                ?: throw IllegalStateException("Cannot write backup")
            verifyBytes(uri, bytes)
        } catch (e: Exception) {
            try { DocumentsContract.deleteDocument(contentResolver, uri) } catch (_: Exception) { }
            throw e
        }
        return true
    }

    private fun saveToDownloads(bytes: ByteArray, fileName: String, mime: String, skipExisting: Boolean): Boolean {
        val relativePath = "${Environment.DIRECTORY_DOWNLOADS}/גיבויים/פנקס חדש/"
        val collection = MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
        if (skipExisting) {
            contentResolver.query(collection, arrayOf(MediaStore.Downloads._ID),
                "${MediaStore.Downloads.DISPLAY_NAME}=? AND ${MediaStore.Downloads.RELATIVE_PATH}=? AND ${MediaStore.Downloads.IS_PENDING}=0",
                arrayOf(fileName, relativePath), null)?.use { c ->
                while (c.moveToNext()) {
                    val existing = android.content.ContentUris.withAppendedId(collection, c.getLong(0))
                    try { verifyBytes(existing, bytes); return false } catch (_: Exception) { }
                }
            }
        }
        val values = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, fileName)
            put(MediaStore.Downloads.MIME_TYPE, mime)
            put(MediaStore.Downloads.RELATIVE_PATH, relativePath)
            put(MediaStore.Downloads.IS_PENDING, 1)
        }
        val uri = contentResolver.insert(collection, values) ?: throw IllegalStateException("Cannot create backup")
        try {
            contentResolver.openOutputStream(uri)?.use { it.write(bytes); it.flush() }
                ?: throw IllegalStateException("Cannot write backup")
            verifyBytes(uri, bytes)
            val complete = ContentValues().apply { put(MediaStore.Downloads.IS_PENDING, 0) }
            check(contentResolver.update(uri, complete, null, null) > 0)
        } catch (e: Exception) {
            try { contentResolver.delete(uri, null, null) } catch (_: Exception) { }
            throw e
        }
        return true
    }

    private inner class RestoreBridge {
        @JavascriptInterface fun pickRestoreFile() {
            if (backupBusy.get()) { toast("יש להמתין לסיום הגיבוי"); return }
            runOnUiThread {
                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                    putExtra(Intent.EXTRA_MIME_TYPES, arrayOf("application/json", "text/plain", "application/octet-stream"))
                    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                }
                try { startActivityForResult(intent, restoreRequest) }
                catch (_: Exception) { toast("לא ניתן לפתוח את בורר קובצי הגיבוי") }
            }
        }
    }

    private inner class DisplayBridge {
        @JavascriptInterface fun getDisplayScale(): Int = prefs.getInt("display_scale_percent", 80).coerceIn(60, 120)
        @JavascriptInterface fun setDisplayScale(percent: Int): Boolean {
            prefs.edit().putInt("display_scale_percent", percent.coerceIn(60, 120)).apply()
            runOnUiThread { webView.setInitialScale(percent.coerceIn(60, 120)); webView.reload() }
            return true
        }
    }

    @Deprecated("Retained for compatibility with the existing Android file pickers")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (resultCode != Activity.RESULT_OK) return
        val uri = data?.data ?: return
        if (requestCode == restoreRequest) {
            worker.execute {
                try {
                    val json = contentResolver.openInputStream(uri)?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }
                        ?: throw IllegalStateException("No file")
                    notifyPage("restoreFromAndroid", json)
                } catch (_: Exception) { toast("לא ניתן לקרוא את קובץ הגיבוי") }
            }
            return
        }
        if (requestCode != localFolderRequest && requestCode != cloudFolderRequest) return
        val kind = if (requestCode == localFolderRequest) "local" else "cloud"
        val flags = data.flags and (Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
        worker.execute {
            try {
                check(flags and Intent.FLAG_GRANT_READ_URI_PERMISSION != 0 && flags and Intent.FLAG_GRANT_WRITE_URI_PERMISSION != 0)
                contentResolver.takePersistableUriPermission(uri, flags)
                check(hasFolderAccess(uri))
                val name = folderName(uri)
                val other = if (kind == "local") "cloud" else "local"
                val otherRaw = prefs.getString(treeKey(other), null)
                check(otherRaw != uri.toString()) { "Same folder" }
                val old = prefs.getString(treeKey(kind), null)
                val edit = prefs.edit().putString(treeKey(kind), uri.toString()).putString("${kind}_folder_name", name)
                if (old != uri.toString()) edit.remove(lastKey(kind)).remove(lastKey(kind) + "_program")
                edit.apply()
                releaseIfUnused(old)
                toast("תיקיית הגיבוי נשמרה: $name")
                notifyPage("backupFoldersChangedFromAndroid")
            } catch (_: Exception) {
                releaseIfUnused(uri.toString())
                toast("התיקייה לא נשמרה. בחר שתי תיקיות שונות ואשר גישה לקריאה ולכתיבה. הבחירה הקודמת נשארה בתוקף.")
            }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        webView.saveState(outState)
        super.onSaveInstanceState(outState)
    }
    override fun onDestroy() {
        worker.shutdown()
        printViews.forEach { it.destroy() }
        printViews.clear()
        webView.destroy()
        super.onDestroy()
    }
}

