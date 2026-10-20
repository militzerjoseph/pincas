package com.example.pincashybrid

import android.app.Activity
import android.content.ContentValues
import android.content.Intent
import android.net.Uri
import android.os.Build
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
import java.nio.charset.StandardCharsets

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    private val restoreRequestCode = 7001
    private val cloudFolderRequestCode = 7002

    private val prefs by lazy {
        getSharedPreferences("pincas_hybrid_settings", MODE_PRIVATE)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        WindowCompat.setDecorFitsSystemWindows(window, true)

        supportActionBar?.hide()
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webView)

        webView.webViewClient = WebViewClient()
        webView.webChromeClient = WebChromeClient()

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
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

        webView.addJavascriptInterface(AndroidBackupBridge(), "AndroidBackup")
        webView.addJavascriptInterface(AndroidRestoreBridge(), "AndroidRestore")
        webView.addJavascriptInterface(AndroidDisplayBridge(), "AndroidDisplay")
        webView.addJavascriptInterface(AndroidCloudBridge(), "AndroidCloud")

        val savedScale = prefs
            .getInt("display_scale_percent", 80)
            .coerceIn(60, 120)

        webView.setInitialScale(savedScale)

        if (savedInstanceState == null) {
            webView.loadUrl("file:///android_asset/index.html")
        } else {
            webView.restoreState(savedInstanceState)
        }
    }

    private inner class AndroidBackupBridge {

        @JavascriptInterface
        fun saveBackup(json: String, fileName: String): String {
            val localOk = saveToDownloads(json, fileName)

            if (!localOk) {
                runOnUiThread {
                    Toast.makeText(
                        this@MainActivity,
                        "שמירת הגיבוי בטלפון נכשלה",
                        Toast.LENGTH_LONG
                    ).show()
                }
                return "LOCAL_FAILED"
            }

            val cloudTree = prefs.getString("cloud_backup_tree_uri", null)

            if (cloudTree.isNullOrBlank()) {
                runOnUiThread {
                    Toast.makeText(
                        this@MainActivity,
                        "הגיבוי נשמר בטלפון. עדיין לא נבחרה תיקיית ענן",
                        Toast.LENGTH_LONG
                    ).show()
                }
                return "LOCAL_ONLY_NO_CLOUD"
            }

            val cloudOk = saveToCloudFolder(json, fileName, cloudTree)

            runOnUiThread {
                val msg = if (cloudOk) {
                    "הגיבוי נשמר בטלפון ובענן"
                } else {
                    "הגיבוי נשמר בטלפון, אך הגיבוי לענן נכשל"
                }
                Toast.makeText(
                    this@MainActivity,
                    msg,
                    if (cloudOk) Toast.LENGTH_SHORT else Toast.LENGTH_LONG
                ).show()
            }

            return if (cloudOk) "BOTH" else "LOCAL_ONLY_CLOUD_FAILED"
        }

        private fun saveToDownloads(json: String, fileName: String): Boolean {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) return false

            var createdUri: Uri? = null

            return try {
                val values = ContentValues().apply {
                    put(MediaStore.Downloads.DISPLAY_NAME, fileName)
                    put(MediaStore.Downloads.MIME_TYPE, "application/json")
                    put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
                    put(MediaStore.Downloads.IS_PENDING, 1)
                }

                val collection =
                    MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)

                createdUri = contentResolver.insert(collection, values)
                    ?: return false

                contentResolver.openOutputStream(createdUri!!)?.use { output ->
                    output.write(json.toByteArray(StandardCharsets.UTF_8))
                    output.flush()
                } ?: run {
                    contentResolver.delete(createdUri!!, null, null)
                    return false
                }

                values.clear()
                values.put(MediaStore.Downloads.IS_PENDING, 0)
                contentResolver.update(createdUri!!, values, null, null)

                true
            } catch (e: Exception) {
                createdUri?.let {
                    try {
                        contentResolver.delete(it, null, null)
                    } catch (_: Exception) {
                    }
                }
                false
            }
        }

        private fun saveToCloudFolder(
            json: String,
            fileName: String,
            treeUriString: String
        ): Boolean {
            return try {
                val treeUri = Uri.parse(treeUriString)
                val treeDocumentId = DocumentsContract.getTreeDocumentId(treeUri)
                val parentDocumentUri =
                    DocumentsContract.buildDocumentUriUsingTree(treeUri, treeDocumentId)

                val newFileUri = DocumentsContract.createDocument(
                    contentResolver,
                    parentDocumentUri,
                    "application/json",
                    fileName
                ) ?: return false

                contentResolver.openOutputStream(newFileUri, "w")?.use { output ->
                    output.write(json.toByteArray(StandardCharsets.UTF_8))
                    output.flush()
                } ?: return false

                true
            } catch (e: Exception) {
                false
            }
        }
    }

    private inner class AndroidRestoreBridge {

        @JavascriptInterface
        fun pickRestoreFile() {
            runOnUiThread {
                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                    putExtra(
                        Intent.EXTRA_MIME_TYPES,
                        arrayOf("application/json", "text/plain", "application/octet-stream")
                    )
                }
                startActivityForResult(intent, restoreRequestCode)
            }
        }
    }

    private inner class AndroidDisplayBridge {

        @JavascriptInterface
        fun getDisplayScale(): Int {
            return prefs
                .getInt("display_scale_percent", 80)
                .coerceIn(60, 120)
        }

        @JavascriptInterface
        fun setDisplayScale(percent: Int): Boolean {
            val safePercent = percent.coerceIn(60, 120)

            prefs.edit()
                .putInt("display_scale_percent", safePercent)
                .apply()

            runOnUiThread {
                webView.setInitialScale(safePercent)
                webView.reload()
            }

            return true
        }
    }

    private inner class AndroidCloudBridge {

        @JavascriptInterface
        fun chooseCloudFolder() {
            runOnUiThread {
                val intent = Intent(Intent.ACTION_OPEN_DOCUMENT_TREE).apply {
                    addFlags(
                        Intent.FLAG_GRANT_READ_URI_PERMISSION or
                                Intent.FLAG_GRANT_WRITE_URI_PERMISSION or
                                Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION
                    )
                }
                startActivityForResult(intent, cloudFolderRequestCode)
            }
        }

        @JavascriptInterface
        fun hasCloudFolder(): Boolean {
            return !prefs.getString("cloud_backup_tree_uri", null).isNullOrBlank()
        }

        @JavascriptInterface
        fun clearCloudFolder(): Boolean {
            prefs.edit().remove("cloud_backup_tree_uri").apply()
            return true
        }
    }

    @Deprecated("Deprecated in Android API, retained here for a simple compatible file-picker flow.")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)

        if (resultCode != Activity.RESULT_OK) return

        if (requestCode == restoreRequestCode) {
            val uri = data?.data ?: return

            try {
                val json = contentResolver.openInputStream(uri)
                    ?.bufferedReader(Charsets.UTF_8)
                    ?.use { it.readText() }
                    ?: return

                val quotedJson = JSONObject.quote(json)

                webView.evaluateJavascript(
                    "window.restoreFromAndroid($quotedJson);",
                    null
                )
            } catch (e: Exception) {
                Toast.makeText(
                    this,
                    "לא ניתן לקרוא את קובץ הגיבוי",
                    Toast.LENGTH_LONG
                ).show()
            }

            return
        }

        if (requestCode == cloudFolderRequestCode) {
            val treeUri = data?.data ?: return

            val takeFlags = data.flags and (
                    Intent.FLAG_GRANT_READ_URI_PERMISSION or
                            Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                    )

            try {
                contentResolver.takePersistableUriPermission(treeUri, takeFlags)
            } catch (_: Exception) {
            }

            prefs.edit()
                .putString("cloud_backup_tree_uri", treeUri.toString())
                .apply()

            Toast.makeText(
                this,
                "תיקיית הגיבוי בענן נשמרה",
                Toast.LENGTH_SHORT
            ).show()

            webView.evaluateJavascript(
                "if(window.cloudFolderSelectedFromAndroid){window.cloudFolderSelectedFromAndroid();}",
                null
            )
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        webView.saveState(outState)
        super.onSaveInstanceState(outState)
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
