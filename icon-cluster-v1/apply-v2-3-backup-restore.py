from pathlib import Path

path = Path('icon-cluster-v1/app/src/main/java/com/militzerjoseph/iconcluster1/MainActivity.java')
s = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Patch anchor not found: {label}')
    s = s.replace(old, new, 1)


# Imports needed for Downloads backup, APK copy and restore picker.
replace_once(
    'import android.content.SharedPreferences;\n',
    '''import android.content.SharedPreferences;\nimport android.content.ContentUris;\nimport android.content.ContentValues;\nimport android.database.Cursor;\nimport android.net.Uri;\nimport android.os.Environment;\nimport android.provider.MediaStore;\n''',
    'backup Android imports'
)

replace_once(
    'import android.content.pm.ApplicationInfo;\n',
    'import android.content.pm.ApplicationInfo;\nimport android.content.pm.PackageInfo;\n',
    'PackageInfo import'
)

replace_once(
    'import android.widget.ImageView;\n',
    'import android.widget.ImageView;\nimport android.widget.ImageButton;\n',
    'ImageButton import'
)

replace_once(
    'import org.json.JSONArray;\n',
    'import org.json.JSONArray;\nimport org.json.JSONObject;\n',
    'JSONObject import'
)

replace_once(
    'import java.text.Collator;\n',
    '''import java.text.Collator;\nimport java.text.SimpleDateFormat;\nimport java.io.ByteArrayInputStream;\nimport java.io.ByteArrayOutputStream;\nimport java.io.FileInputStream;\nimport java.io.IOException;\nimport java.io.InputStream;\nimport java.io.OutputStream;\nimport java.nio.charset.StandardCharsets;\nimport java.util.Date;\n''',
    'Java backup imports'
)

# Backup constants. Internal APK-backup state is intentionally not part of data backup.
replace_once(
    '    private static final String KEY_SCREEN_BG = "ui_screen_bg";\n',
    '''    private static final String KEY_SCREEN_BG = "ui_screen_bg";\n    private static final String KEY_LAST_APK_BACKUP_VERSION = "last_apk_backup_version_code";\n    private static final int REQUEST_RESTORE_BACKUP = 7301;\n    private static final String DATA_BACKUP_SUBPATH = "גיבויים/מקבץ איקונים 1/נתונים";\n    private static final String APK_BACKUP_SUBPATH = "גיבויים/מקבץ איקונים 1/APK";\n''',
    'backup constants'
)

# Give the third header button room while keeping equal horizontal spacing.
replace_once(
    '        titleParams.leftMargin = dp(126);\n',
    '        titleParams.leftMargin = dp(184);\n',
    'title margin for backup button'
)

# Add a real diskette/save icon to the right of Settings, at the same spacing as Plus -> Settings.
replace_once(
    '''        settingsParams.leftMargin = dp(58);\n        header.addView(settings, settingsParams);\n\n        ScrollView scroll = new ScrollView(this);\n''',
    '''        settingsParams.leftMargin = dp(58);\n        header.addView(settings, settingsParams);\n\n        ImageButton backup = new ImageButton(this);\n        backup.setImageResource(android.R.drawable.ic_menu_save);\n        backup.setColorFilter(Color.rgb(255, 216, 110));\n        backup.setBackgroundColor(Color.TRANSPARENT);\n        backup.setScaleType(ImageView.ScaleType.CENTER_INSIDE);\n        backup.setPadding(dp(17), dp(17), dp(17), dp(17));\n        backup.setContentDescription("גיבוי ושיחזור");\n        backup.setOnClickListener(v -> showBackupMenu());\n        FrameLayout.LayoutParams backupParams = new FrameLayout.LayoutParams(\n                dp(64), dp(64), Gravity.LEFT | Gravity.BOTTOM);\n        backupParams.leftMargin = dp(116);\n        header.addView(backup, backupParams);\n\n        ScrollView scroll = new ScrollView(this);\n''',
    'backup header button'
)

# Backup / restore methods, inserted before V2.2 back handling.
anchor = '    @Override\n    public void onBackPressed() {\n'
if anchor not in s:
    raise SystemExit('Patch anchor not found: onBackPressed')

methods = r'''
    private static class BackupEntry {
        final String name;
        final Uri uri;

        BackupEntry(String name, Uri uri) {
            this.name = name;
            this.uri = uri;
        }
    }

    private void showBackupMenu() {
        String[] actions = {"גיבוי נתונים", "גיבוי תוכנית", "שיחזור"};
        new AlertDialog.Builder(this)
                .setTitle("גיבוי ושיחזור")
                .setItems(actions, (dialog, which) -> {
                    if (which == 0) {
                        backupData();
                    } else if (which == 1) {
                        backupProgramIfNew();
                    } else if (which == 2) {
                        showRestoreBackups();
                    }
                })
                .setNegativeButton("ביטול", null)
                .show();
    }

    private void backupData() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
            Toast.makeText(this, "גיבוי אוטומטי ל-Download נתמך במכשירים חדשים יותר", Toast.LENGTH_LONG).show();
            return;
        }

        try {
            JSONObject root = new JSONObject();
            root.put("schemaVersion", 1);
            root.put("app", "מקבץ איקונים 1");
            root.put("package", getPackageName());
            root.put("appVersion", getCurrentVersionName());
            root.put("createdAt", new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.US).format(new Date()));

            JSONArray apps = new JSONArray();
            for (String pkg : selectedPackages) apps.put(pkg);
            root.put("selectedApps", apps);

            JSONObject settings = new JSONObject();
            settings.put("titleSize", (int) getTitleSize());
            settings.put("titleWeight", getTitleWeight());
            settings.put("headerBg", getUiColor(KEY_HEADER_BG, Color.rgb(17, 17, 17)));
            settings.put("headerText", getUiColor(KEY_HEADER_TEXT, Color.WHITE));
            settings.put("screenBg", getUiColor(KEY_SCREEN_BG, Color.parseColor("#f5f5f5")));
            root.put("settings", settings);

            String stamp = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss", Locale.US).format(new Date());
            String fileName = "מקבץ_איקונים_1_נתונים_" + stamp + ".json";
            byte[] bytes = root.toString(2).getBytes(StandardCharsets.UTF_8);

            try (InputStream in = new ByteArrayInputStream(bytes)) {
                writeDownloadFile(DATA_BACKUP_SUBPATH, fileName, "application/json", in);
            }

            new AlertDialog.Builder(this)
                    .setTitle("הגיבוי הושלם")
                    .setMessage("נוצר גיבוי נתונים חדש בתוך:\nDownload/גיבויים/מקבץ איקונים 1/נתונים\n\n" + fileName)
                    .setPositiveButton("אישור", null)
                    .show();
        } catch (Exception e) {
            new AlertDialog.Builder(this)
                    .setTitle("הגיבוי לא הושלם")
                    .setMessage("לא ניתן היה ליצור את גיבוי הנתונים.")
                    .setPositiveButton("אישור", null)
                    .show();
        }
    }

    private void backupProgramIfNew() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
            Toast.makeText(this, "גיבוי אוטומטי ל-Download נתמך במכשירים חדשים יותר", Toast.LENGTH_LONG).show();
            return;
        }

        try {
            long currentVersion = getCurrentVersionCode();
            long lastBackedUp = prefs().getLong(KEY_LAST_APK_BACKUP_VERSION, -1L);

            if (lastBackedUp >= currentVersion) {
                new AlertDialog.Builder(this)
                        .setTitle("גיבוי תוכנית")
                        .setMessage("אין גרסה חדשה – לא בוצע גיבוי.")
                        .setPositiveButton("אישור", null)
                        .show();
                return;
            }

            String versionName = getCurrentVersionName();
            String safeVersion = versionName == null || versionName.trim().isEmpty()
                    ? String.valueOf(currentVersion)
                    : versionName.trim();
            String fileName = "מקבץ_איקונים_1_V" + safeVersion + ".apk";

            try (InputStream in = new FileInputStream(getApplicationInfo().sourceDir)) {
                writeDownloadFile(APK_BACKUP_SUBPATH, fileName,
                        "application/vnd.android.package-archive", in);
            }

            prefs().edit().putLong(KEY_LAST_APK_BACKUP_VERSION, currentVersion).apply();

            new AlertDialog.Builder(this)
                    .setTitle("גיבוי התוכנית הושלם")
                    .setMessage("נשמרה גרסת התוכנית הנוכחית בתוך:\nDownload/גיבויים/מקבץ איקונים 1/APK\n\n" + fileName)
                    .setPositiveButton("אישור", null)
                    .show();
        } catch (Exception e) {
            new AlertDialog.Builder(this)
                    .setTitle("הגיבוי לא הושלם")
                    .setMessage("לא ניתן היה ליצור גיבוי של התוכנית.")
                    .setPositiveButton("אישור", null)
                    .show();
        }
    }

    private Uri writeDownloadFile(String subPath, String fileName,
                                  String mimeType, InputStream in) throws Exception {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
            throw new IOException("Android version not supported for automatic Downloads backup");
        }

        ContentValues values = new ContentValues();
        values.put(MediaStore.MediaColumns.DISPLAY_NAME, fileName);
        values.put(MediaStore.MediaColumns.MIME_TYPE, mimeType);
        values.put(MediaStore.MediaColumns.RELATIVE_PATH,
                Environment.DIRECTORY_DOWNLOADS + "/" + subPath + "/");
        values.put(MediaStore.MediaColumns.IS_PENDING, 1);

        Uri uri = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
        if (uri == null) throw new IOException("Could not create Downloads file");

        boolean success = false;
        try {
            try (OutputStream out = getContentResolver().openOutputStream(uri, "w")) {
                if (out == null) throw new IOException("Could not open output stream");
                byte[] buffer = new byte[64 * 1024];
                int read;
                while ((read = in.read(buffer)) != -1) {
                    out.write(buffer, 0, read);
                }
                out.flush();
            }

            ContentValues done = new ContentValues();
            done.put(MediaStore.MediaColumns.IS_PENDING, 0);
            getContentResolver().update(uri, done, null, null);
            success = true;
            return uri;
        } finally {
            if (!success) {
                try {
                    getContentResolver().delete(uri, null, null);
                } catch (Exception ignored) {
                }
            }
        }
    }

    private long getCurrentVersionCode() throws Exception {
        PackageInfo info = getPackageManager().getPackageInfo(getPackageName(), 0);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            return info.getLongVersionCode();
        }
        return info.versionCode;
    }

    private String getCurrentVersionName() throws Exception {
        PackageInfo info = getPackageManager().getPackageInfo(getPackageName(), 0);
        return info.versionName == null ? "" : info.versionName;
    }

    private List<BackupEntry> getLocalDataBackups() {
        ArrayList<BackupEntry> result = new ArrayList<>();
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) return result;

        Uri collection = MediaStore.Downloads.EXTERNAL_CONTENT_URI;
        String[] projection = {
                MediaStore.MediaColumns._ID,
                MediaStore.MediaColumns.DISPLAY_NAME
        };
        String selection = MediaStore.MediaColumns.RELATIVE_PATH + "=?";
        String[] args = {
                Environment.DIRECTORY_DOWNLOADS + "/" + DATA_BACKUP_SUBPATH + "/"
        };
        String order = MediaStore.MediaColumns.DATE_ADDED + " DESC";

        try (Cursor cursor = getContentResolver().query(
                collection, projection, selection, args, order)) {
            if (cursor == null) return result;
            int idColumn = cursor.getColumnIndexOrThrow(MediaStore.MediaColumns._ID);
            int nameColumn = cursor.getColumnIndexOrThrow(MediaStore.MediaColumns.DISPLAY_NAME);
            while (cursor.moveToNext()) {
                long id = cursor.getLong(idColumn);
                String name = cursor.getString(nameColumn);
                if (name != null && name.endsWith(".json")) {
                    result.add(new BackupEntry(name, ContentUris.withAppendedId(collection, id)));
                }
            }
        } catch (Exception ignored) {
        }
        return result;
    }

    private void showRestoreBackups() {
        List<BackupEntry> backups = getLocalDataBackups();
        if (backups.isEmpty()) {
            startRestorePicker();
            return;
        }

        ArrayList<String> labels = new ArrayList<>();
        for (BackupEntry entry : backups) labels.add(entry.name);
        labels.add("בחר קובץ אחר מ-Download / Google Drive / OneDrive");

        new AlertDialog.Builder(this)
                .setTitle("בחר גיבוי לשיחזור")
                .setItems(labels.toArray(new String[0]), (dialog, which) -> {
                    if (which < backups.size()) {
                        prepareRestore(backups.get(which).uri);
                    } else {
                        startRestorePicker();
                    }
                })
                .setNegativeButton("ביטול", null)
                .show();
    }

    private void startRestorePicker() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        try {
            startActivityForResult(intent, REQUEST_RESTORE_BACKUP);
        } catch (Exception e) {
            Toast.makeText(this, "לא ניתן לפתוח את בורר הקבצים", Toast.LENGTH_LONG).show();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_RESTORE_BACKUP && resultCode == RESULT_OK
                && data != null && data.getData() != null) {
            prepareRestore(data.getData());
        }
    }

    private void prepareRestore(Uri uri) {
        try {
            String json;
            try (InputStream in = getContentResolver().openInputStream(uri)) {
                if (in == null) throw new IOException("Could not open backup");
                json = readText(in);
            }

            JSONObject root = new JSONObject(json);
            if (!"מקבץ איקונים 1".equals(root.optString("app"))) {
                throw new IOException("Wrong backup application");
            }

            JSONArray apps = root.optJSONArray("selectedApps");
            if (apps == null) throw new IOException("Missing app list");

            String date = root.optString("createdAt", "לא ידוע");
            String version = root.optString("appVersion", "לא ידועה");
            int count = apps.length();

            new AlertDialog.Builder(this)
                    .setTitle("אישור שיחזור")
                    .setMessage("תאריך הגיבוי: " + date
                            + "\nגרסת התוכנית: " + version
                            + "\nמספר איקונים: " + count
                            + "\n\nהשיחזור יחליף את הרשימה והגדרות התצוגה הנוכחיות.")
                    .setPositiveButton("שחזר", (dialog, which) -> applyRestore(root))
                    .setNegativeButton("ביטול", null)
                    .show();
        } catch (Exception e) {
            new AlertDialog.Builder(this)
                    .setTitle("שיחזור")
                    .setMessage("הקובץ שנבחר אינו גיבוי תקין של מקבץ איקונים 1.")
                    .setPositiveButton("אישור", null)
                    .show();
        }
    }

    private void applyRestore(JSONObject root) {
        try {
            JSONArray apps = root.getJSONArray("selectedApps");
            selectedPackages.clear();
            for (int i = 0; i < apps.length(); i++) {
                String pkg = apps.optString(i, "").trim();
                if (!pkg.isEmpty() && !selectedPackages.contains(pkg)) {
                    selectedPackages.add(pkg);
                }
            }
            saveSelectedApps();

            JSONObject settings = root.optJSONObject("settings");
            if (settings != null) {
                prefs().edit()
                        .putInt(KEY_TITLE_SIZE,
                                settings.optInt("titleSize", (int) getTitleSize()))
                        .putInt(KEY_TITLE_WEIGHT,
                                settings.optInt("titleWeight", getTitleWeight()))
                        .putInt(KEY_HEADER_BG,
                                settings.optInt("headerBg", getUiColor(KEY_HEADER_BG, Color.rgb(17, 17, 17))))
                        .putInt(KEY_HEADER_TEXT,
                                settings.optInt("headerText", getUiColor(KEY_HEADER_TEXT, Color.WHITE)))
                        .putInt(KEY_SCREEN_BG,
                                settings.optInt("screenBg", getUiColor(KEY_SCREEN_BG, Color.parseColor("#f5f5f5"))))
                        .apply();
            }

            moveModePackage = null;
            applyCurrentUiSettings();
            renderGrid();

            new AlertDialog.Builder(this)
                    .setTitle("השיחזור הושלם")
                    .setMessage("הנתונים וההגדרות שוחזרו בהצלחה.")
                    .setPositiveButton("אישור", null)
                    .show();
        } catch (Exception e) {
            new AlertDialog.Builder(this)
                    .setTitle("שיחזור")
                    .setMessage("לא ניתן היה להשלים את השיחזור.")
                    .setPositiveButton("אישור", null)
                    .show();
        }
    }

    private String readText(InputStream in) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buffer = new byte[32 * 1024];
        int read;
        while ((read = in.read(buffer)) != -1) {
            out.write(buffer, 0, read);
        }
        return out.toString(StandardCharsets.UTF_8.name());
    }

'''

s = s.replace(anchor, methods + anchor, 1)

path.write_text(s, encoding='utf-8')
print('Applied Icon Cluster V2.3 backup and restore')
