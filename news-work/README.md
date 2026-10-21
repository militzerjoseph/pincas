# חדשות — גרסה 101

Android WebView application, package `com.militzerjoseph.newswork`.
Installs alongside the previous news app. All seven original shortcut entries are preserved.
The default icon is the user-approved newspaper image without the yellow stripe.
Classic color and text icons remain available in Settings.

Data backup creates timestamped JSON files in Download/גיבויים/חדשות/נתונים.
APK backup saves one copy of each version in Download/גיבויים/חדשות/APK.
Cloud folder selection persists; document export also supports Google Drive.
Restore accepts news backups and the news folder from older Tikiyot backups.
Restore previews date, version and count and persists data before replacing current state.

Build: Java 17, Gradle 8.9, Android SDK 35; run `python prepare_icons.py`,
`node verify.cjs` and `gradle assembleRelease`. Signing material stays outside git.
On-device installation, real cloud provider and restore tests remain necessary.
