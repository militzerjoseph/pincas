# ב.לאומי — גרסה 101

Android WebView app rebuilt from the supplied `btl_uniform_ready_v100.apk` HTML.

* Application ID: `com.militzerjoseph.btlwork` (installs alongside the original app).
* Launcher label: `ב.לאומי`; in-app title: `ב.לאומי`.
* Android 10 or newer. Java 17, Gradle 8.9, Android SDK 35.
* The approved blue/gold family illustration is the default icon; classic text/icon controls remain available.
* Data format remains `app: ב.לאומי, version: 1`, with optional `appVersion` and `launcherIcon`.
* Local backup: `Download/גיבויים/ב.לאומי/נתונים` and `Download/גיבויים/ב.לאומי/APK`.
* Optional persistent SAF cloud directory; a separate document export supports Google Drive providers without directory access.
* Restore validates app/folder identity and shortcut fields, previews date/version/count, and writes before replacing current in-memory data.
* APK exports skip the current version if the saved local file still exists. Cloud-folder exports skip an existing version filename. Manual document exports remember the last exported version.
* Run `python prepare_icons.py`, then `gradle assembleRelease`. The GitHub workflow uploads an unsigned APK and signer tools. Signing keys are kept separately, never committed.

First installation: keep the old app, make a data backup there, install this app, and restore the JSON backup. APK files do not contain the private runtime data of the installed old app.

Device checks still required: install, restore current user backup, launch website/app shortcuts, save/reselect cloud folder, create a data backup, export APK, and restore after changing a test shortcut.


Legacy BTL backups mislabeled app=בנקים are accepted only with their f_btl folder. Real banks backups are rejected.
