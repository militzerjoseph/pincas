from pathlib import Path

path = Path('icon-cluster-v1/app/src/main/java/com/militzerjoseph/iconcluster1/MainActivity.java')
s = path.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'Patch anchor not found: {label}')
    s = s.replace(old, new, 1)


replace_once(
    'import android.content.Intent;\n',
    'import android.content.Intent;\nimport android.content.SharedPreferences;\n',
    'SharedPreferences import'
)

replace_once(
    '    private static final String KEY_APPS = "selected_apps";\n\n    private GridLayout grid;\n    private TextView emptyText;\n',
    '''    private static final String KEY_APPS = "selected_apps";\n    private static final String KEY_TITLE_SIZE = "ui_title_size";\n    private static final String KEY_TITLE_WEIGHT = "ui_title_weight";\n    private static final String KEY_HEADER_BG = "ui_header_bg";\n    private static final String KEY_HEADER_TEXT = "ui_header_text";\n\n    private GridLayout grid;\n    private TextView emptyText;\n    private FrameLayout mainHeader;\n    private TextView mainTitle;\n''',
    'UI fields'
)

replace_once(
    '        FrameLayout header = new FrameLayout(this);\n        header.setBackgroundColor(Color.rgb(17, 17, 17));\n',
    '''        FrameLayout header = new FrameLayout(this);\n        mainHeader = header;\n        header.setBackgroundColor(getUiColor(KEY_HEADER_BG, Color.rgb(17, 17, 17)));\n''',
    'header color'
)

replace_once(
    '''        TextView title = new TextView(this);\n        title.setText("מקבץ איקונים 1");\n        title.setTextColor(Color.WHITE);\n        title.setTextSize(17);\n        title.setTypeface(null, Typeface.NORMAL);\n''',
    '''        TextView title = new TextView(this);\n        mainTitle = title;\n        title.setText("מקבץ איקונים 1");\n        title.setTextColor(getUiColor(KEY_HEADER_TEXT, Color.WHITE));\n        title.setTextSize(getTitleSize());\n        applyTitleWeight(title, getTitleWeight());\n''',
    'dynamic title style'
)

replace_once(
    '        titleParams.leftMargin = dp(70);\n',
    '        titleParams.leftMargin = dp(126);\n',
    'title left margin'
)

replace_once(
    '        header.addView(plus, plusParams);\n\n        ScrollView scroll = new ScrollView(this);\n',
    '''        header.addView(plus, plusParams);\n\n        Button settings = new Button(this);\n        settings.setText("⚙");\n        settings.setTextSize(23);\n        settings.setTextColor(Color.rgb(255, 216, 110));\n        settings.setBackgroundColor(Color.TRANSPARENT);\n        settings.setAllCaps(false);\n        settings.setContentDescription("הגדרות מסך וכותרת");\n        settings.setOnClickListener(v -> showUiSettings());\n        FrameLayout.LayoutParams settingsParams = new FrameLayout.LayoutParams(\n                dp(64), dp(64), Gravity.LEFT | Gravity.BOTTOM);\n        settingsParams.leftMargin = dp(58);\n        header.addView(settings, settingsParams);\n\n        ScrollView scroll = new ScrollView(this);\n''',
    'settings button'
)

replace_once(
    '''        pickerTitle.setText("בחר אפליקציות");\n        pickerTitle.setTextSize(17);\n        pickerTitle.setTextColor(Color.WHITE);\n        pickerTitle.setTypeface(null, Typeface.NORMAL);\n''',
    '''        pickerTitle.setText("בחר אפליקציות");\n        pickerTitle.setTextSize(getTitleSize());\n        pickerTitle.setTextColor(getUiColor(KEY_HEADER_TEXT, Color.WHITE));\n        applyTitleWeight(pickerTitle, getTitleWeight());\n''',
    'picker title typography'
)

replace_once(
    '        pickerTitle.setBackgroundColor(Color.rgb(17, 17, 17));\n',
    '        pickerTitle.setBackgroundColor(getUiColor(KEY_HEADER_BG, Color.rgb(17, 17, 17)));\n',
    'picker title color'
)

methods = r'''
    private SharedPreferences prefs() {
        return getSharedPreferences(PREFS, MODE_PRIVATE);
    }

    private float getTitleSize() {
        int v = prefs().getInt(KEY_TITLE_SIZE, 17);
        return Math.max(12, Math.min(30, v));
    }

    private int getTitleWeight() {
        int v = prefs().getInt(KEY_TITLE_WEIGHT, 400);
        if (v != 400 && v != 500 && v != 600 && v != 700) return 400;
        return v;
    }

    private int getUiColor(String key, int fallback) {
        return prefs().getInt(key, fallback);
    }

    private void applyTitleWeight(TextView view, int weight) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            view.setTypeface(Typeface.create(Typeface.DEFAULT, weight, false));
        } else {
            view.setTypeface(null, weight >= 600 ? Typeface.BOLD : Typeface.NORMAL);
        }
    }

    private void applyCurrentUiSettings() {
        int bg = getUiColor(KEY_HEADER_BG, Color.rgb(17, 17, 17));
        int text = getUiColor(KEY_HEADER_TEXT, Color.WHITE);
        getWindow().setStatusBarColor(bg);
        if (mainHeader != null) mainHeader.setBackgroundColor(bg);
        if (mainTitle != null) {
            mainTitle.setTextColor(text);
            mainTitle.setTextSize(getTitleSize());
            applyTitleWeight(mainTitle, getTitleWeight());
        }
    }

    private void saveHeaderColors(int bg, int text) {
        prefs().edit()
                .putInt(KEY_HEADER_BG, bg)
                .putInt(KEY_HEADER_TEXT, text)
                .apply();
        applyCurrentUiSettings();
    }

    private Button settingButton(String text) {
        Button b = new Button(this);
        b.setText(text);
        b.setTextSize(16);
        b.setAllCaps(false);
        return b;
    }

    private void showUiSettings() {
        final Dialog dialog = new Dialog(this);
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);

        ScrollView scroll = new ScrollView(this);
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        root.setPadding(dp(18), dp(18), dp(18), dp(24));
        root.setBackgroundColor(Color.WHITE);
        scroll.addView(root, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView heading = new TextView(this);
        heading.setText("הגדרות מסך וכותרת");
        heading.setTextSize(22);
        heading.setTextColor(Color.rgb(25, 25, 25));
        heading.setGravity(Gravity.RIGHT);
        root.addView(heading, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(52)));

        TextView sizeLabel = new TextView(this);
        sizeLabel.setText("גודל הכותרת");
        sizeLabel.setTextSize(17);
        sizeLabel.setTextColor(Color.DKGRAY);
        root.addView(sizeLabel);

        LinearLayout sizeRow = new LinearLayout(this);
        sizeRow.setOrientation(LinearLayout.HORIZONTAL);
        sizeRow.setGravity(Gravity.CENTER);
        sizeRow.setLayoutDirection(View.LAYOUT_DIRECTION_LTR);
        Button minus = settingButton("−");
        TextView sizeValue = new TextView(this);
        sizeValue.setText(String.valueOf((int) getTitleSize()));
        sizeValue.setTextSize(19);
        sizeValue.setGravity(Gravity.CENTER);
        Button plusSize = settingButton("+");
        sizeRow.addView(minus, new LinearLayout.LayoutParams(0, dp(52), 1f));
        sizeRow.addView(sizeValue, new LinearLayout.LayoutParams(0, dp(52), 1f));
        sizeRow.addView(plusSize, new LinearLayout.LayoutParams(0, dp(52), 1f));
        root.addView(sizeRow);

        minus.setOnClickListener(v -> {
            int next = Math.max(12, (int) getTitleSize() - 1);
            prefs().edit().putInt(KEY_TITLE_SIZE, next).apply();
            sizeValue.setText(String.valueOf(next));
            applyCurrentUiSettings();
        });
        plusSize.setOnClickListener(v -> {
            int next = Math.min(30, (int) getTitleSize() + 1);
            prefs().edit().putInt(KEY_TITLE_SIZE, next).apply();
            sizeValue.setText(String.valueOf(next));
            applyCurrentUiSettings();
        });

        TextView weightLabel = new TextView(this);
        weightLabel.setText("עובי הכותרת");
        weightLabel.setTextSize(17);
        weightLabel.setTextColor(Color.DKGRAY);
        weightLabel.setPadding(0, dp(12), 0, dp(4));
        root.addView(weightLabel);

        Button weight = settingButton("B  " + getTitleWeight());
        weight.setOnClickListener(v -> {
            int current = getTitleWeight();
            int next = current == 400 ? 500 : current == 500 ? 600 : current == 600 ? 700 : 400;
            prefs().edit().putInt(KEY_TITLE_WEIGHT, next).apply();
            weight.setText("B  " + next);
            applyCurrentUiSettings();
        });
        root.addView(weight, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(54)));

        TextView colorLabel = new TextView(this);
        colorLabel.setText("צבע החלק העליון");
        colorLabel.setTextSize(17);
        colorLabel.setTextColor(Color.DKGRAY);
        colorLabel.setPadding(0, dp(14), 0, dp(6));
        root.addView(colorLabel);

        String[] presetNames = {
                "BASE LINE",
                "COLOR 1 – אפור כהה",
                "COLOR 2 – קרם וחום",
                "COLOR 3 – שמנת וכחול־אפור",
                "COLOR 4 – חום וקרם"
        };
        int[][] presetColors = {
                {Color.parseColor("#111111"), Color.parseColor("#ffffff")},
                {Color.parseColor("#374151"), Color.parseColor("#ffffff")},
                {Color.parseColor("#f3ecd9"), Color.parseColor("#5c3d12")},
                {Color.parseColor("#fbf7ec"), Color.parseColor("#172033")},
                {Color.parseColor("#5c3d12"), Color.parseColor("#f6efdd")}
        };
        for (int i = 0; i < presetNames.length; i++) {
            final int bg = presetColors[i][0];
            final int text = presetColors[i][1];
            Button b = settingButton(presetNames[i]);
            b.setOnClickListener(v -> saveHeaderColors(bg, text));
            root.addView(b, new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, dp(50)));
        }

        LinearLayout customRow = new LinearLayout(this);
        customRow.setOrientation(LinearLayout.HORIZONTAL);
        customRow.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        Button bgButton = settingButton("צבע רקע עליון");
        Button textButton = settingButton("צבע כיתוב עליון");
        bgButton.setOnClickListener(v -> showColorPalette(true));
        textButton.setOnClickListener(v -> showColorPalette(false));
        customRow.addView(bgButton, new LinearLayout.LayoutParams(0, dp(54), 1f));
        customRow.addView(textButton, new LinearLayout.LayoutParams(0, dp(54), 1f));
        root.addView(customRow);

        Button reset = settingButton("החזר לברירת המחדל");
        reset.setOnClickListener(v -> {
            prefs().edit()
                    .putInt(KEY_TITLE_SIZE, 17)
                    .putInt(KEY_TITLE_WEIGHT, 400)
                    .putInt(KEY_HEADER_BG, Color.parseColor("#111111"))
                    .putInt(KEY_HEADER_TEXT, Color.WHITE)
                    .apply();
            applyCurrentUiSettings();
            dialog.dismiss();
            showUiSettings();
        });
        root.addView(reset, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(54)));

        Button close = settingButton("סגור");
        close.setOnClickListener(v -> dialog.dismiss());
        LinearLayout.LayoutParams closeParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(58));
        closeParams.setMargins(0, dp(12), 0, 0);
        root.addView(close, closeParams);

        dialog.setContentView(scroll);
        dialog.show();
        Window w = dialog.getWindow();
        if (w != null) {
            w.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
        }
    }

    private void showColorPalette(boolean background) {
        final Dialog dialog = new Dialog(this);
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        root.setPadding(dp(16), dp(18), dp(16), dp(18));
        root.setBackgroundColor(Color.WHITE);

        TextView heading = new TextView(this);
        heading.setText(background ? "בחר צבע רקע עליון" : "בחר צבע כיתוב עליון");
        heading.setTextSize(21);
        heading.setTextColor(Color.rgb(25, 25, 25));
        heading.setGravity(Gravity.RIGHT);
        root.addView(heading, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(54)));

        String[] hex = {
                "#111111","#ffffff","#f9fafb","#f1f3f5","#e5e7eb","#c4c7cc","#9ca3af",
                "#6b7280","#4b5563","#374151","#1f2937","#f3ecd9","#fbf7ec","#f6efdd",
                "#ddd2b7","#d6c6a8","#74644d","#665846","#5c3d12","#4f3b18","#172033",
                "#697386","#ffd86e","#d2d580","#ffd04b","#f4a3e7","#4f72f6","#8ee6ea",
                "#74c4ec","#c9b0f4","#ff9966","#835fc8","#e83d64","#8da34f","#fff3b0",
                "#ffd6a5","#ffc6c6","#d7f8c4","#c9f1ff","#d9d2ff","#f5d0ff","#12805c","#d92d20"
        };

        GridLayout palette = new GridLayout(this);
        palette.setColumnCount(7);
        palette.setUseDefaultMargins(false);
        for (String value : hex) {
            final int color = Color.parseColor(value);
            TextView swatch = new TextView(this);
            swatch.setBackgroundColor(color);
            swatch.setText(" ");
            swatch.setContentDescription(value);
            swatch.setOnClickListener(v -> {
                int bg = getUiColor(KEY_HEADER_BG, Color.rgb(17, 17, 17));
                int text = getUiColor(KEY_HEADER_TEXT, Color.WHITE);
                if (background) bg = color;
                else text = color;
                saveHeaderColors(bg, text);
                dialog.dismiss();
            });
            GridLayout.LayoutParams lp = new GridLayout.LayoutParams();
            lp.width = 0;
            lp.height = dp(44);
            lp.columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f);
            lp.setMargins(dp(3), dp(3), dp(3), dp(3));
            palette.addView(swatch, lp);
        }
        root.addView(palette, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));

        Button close = settingButton("ביטול");
        close.setOnClickListener(v -> dialog.dismiss());
        LinearLayout.LayoutParams closeParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(56));
        closeParams.setMargins(0, dp(12), 0, 0);
        root.addView(close, closeParams);

        dialog.setContentView(root);
        dialog.show();
        Window w = dialog.getWindow();
        if (w != null) w.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
    }

'''

replace_once(
    '    private int dp(int value) {\n',
    methods + '    private int dp(int value) {\n',
    'insert UI methods'
)

path.write_text(s, encoding='utf-8')
print('Applied Icon Cluster V2 Tikiyot3-style UI settings patch')
