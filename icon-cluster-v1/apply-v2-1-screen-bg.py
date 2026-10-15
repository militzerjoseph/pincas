from pathlib import Path

path = Path('icon-cluster-v1/app/src/main/java/com/militzerjoseph/iconcluster1/MainActivity.java')
s = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Patch anchor not found: {label}')
    s = s.replace(old, new, 1)

replace_once(
    '    private static final String KEY_HEADER_TEXT = "ui_header_text";\n\n    private GridLayout grid;\n',
    '    private static final String KEY_HEADER_TEXT = "ui_header_text";\n    private static final String KEY_SCREEN_BG = "ui_screen_bg";\n\n    private GridLayout grid;\n',
    'screen bg key'
)

replace_once(
    '    private FrameLayout mainHeader;\n    private TextView mainTitle;\n',
    '    private FrameLayout mainHeader;\n    private TextView mainTitle;\n    private LinearLayout mainRoot;\n',
    'main root field'
)

replace_once(
    '''        LinearLayout root = new LinearLayout(this);\n        root.setOrientation(LinearLayout.VERTICAL);\n        root.setBackgroundColor(Color.rgb(245, 245, 245));\n''',
    '''        LinearLayout root = new LinearLayout(this);\n        mainRoot = root;\n        root.setOrientation(LinearLayout.VERTICAL);\n        root.setBackgroundColor(getUiColor(KEY_SCREEN_BG, Color.parseColor("#f5f5f5")));\n''',
    'dynamic main screen background'
)

replace_once(
    '''        getWindow().setStatusBarColor(bg);\n        if (mainHeader != null) mainHeader.setBackgroundColor(bg);\n        if (mainTitle != null) {\n''',
    '''        getWindow().setStatusBarColor(bg);\n        if (mainHeader != null) mainHeader.setBackgroundColor(bg);\n        if (mainRoot != null) mainRoot.setBackgroundColor(\n                getUiColor(KEY_SCREEN_BG, Color.parseColor("#f5f5f5")));\n        if (mainTitle != null) {\n''',
    'apply screen background'
)

screen_settings = r'''
        TextView screenBgLabel = new TextView(this);
        screenBgLabel.setText("רקע המסך");
        screenBgLabel.setTextSize(17);
        screenBgLabel.setTextColor(Color.DKGRAY);
        screenBgLabel.setPadding(0, dp(16), 0, dp(6));
        root.addView(screenBgLabel);

        String[] screenBgNames = {
                "לבן רך",
                "אפור בהיר מאוד",
                "אפור בהיר",
                "שמנת בהירה",
                "בז׳ בהיר",
                "כחול־אפור בהיר"
        };
        String[] screenBgHex = {
                "#f5f5f5",
                "#eeeeee",
                "#e4e6e8",
                "#f3ecd9",
                "#eee7dc",
                "#e8edf0"
        };
        for (int i = 0; i < screenBgNames.length; i++) {
            final int screenColor = Color.parseColor(screenBgHex[i]);
            Button b = settingButton(screenBgNames[i]);
            b.setOnClickListener(v -> {
                prefs().edit().putInt(KEY_SCREEN_BG, screenColor).apply();
                applyCurrentUiSettings();
            });
            root.addView(b, new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, dp(50)));
        }

'''

replace_once(
    '        root.addView(customRow);\n\n        Button reset = settingButton("החזר לברירת המחדל");\n',
    '        root.addView(customRow);\n\n' + screen_settings + '        Button reset = settingButton("החזר לברירת המחדל");\n',
    'screen background settings section'
)

replace_once(
    '''                    .putInt(KEY_HEADER_BG, Color.parseColor("#111111"))\n                    .putInt(KEY_HEADER_TEXT, Color.WHITE)\n                    .apply();\n''',
    '''                    .putInt(KEY_HEADER_BG, Color.parseColor("#111111"))\n                    .putInt(KEY_HEADER_TEXT, Color.WHITE)\n                    .putInt(KEY_SCREEN_BG, Color.parseColor("#f5f5f5"))\n                    .apply();\n''',
    'reset screen background'
)

path.write_text(s, encoding='utf-8')
print('Applied Icon Cluster V2.1 subtle screen background choices')
