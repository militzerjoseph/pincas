package com.militzer.shortcutbuilder;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Bundle;
import android.text.TextUtils;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity {

    private static final String TRIAL_NAME = "פנקס הכנסות";
    private static final String TRIAL_URL = "https://script.google.com/macros/s/AKfycbyoJeN1G2EuGczP88itz2r2OKXH5GWL45c3ICe9L2kOHG2rNIFYJ98aRx0UPyZEIHyKxA/exec";
    private static final String TRIAL_APK_URL = "https://raw.githubusercontent.com/militzerjoseph/pincas/shortcut-builder-output/output/pincas-income.apk";

    private EditText nameEdit;
    private EditText urlEdit;
    private TextView previewIcon;
    private TextView previewName;
    private Spinner styleSpinner;
    private int selectedColor = Color.rgb(247, 214, 119);
    private String selectedStyle = "כרטסת";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.rgb(26, 115, 232));

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(Color.rgb(246, 249, 253));

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(16), dp(18), dp(16), dp(28));
        root.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        scroll.addView(root, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView title = text("יוצר מעטפות", 30, Typeface.BOLD, Color.WHITE);
        title.setGravity(Gravity.CENTER);
        title.setPadding(dp(12), dp(20), dp(12), dp(8));
        GradientDrawable titleBg = roundRect(Color.rgb(26,115,232), 24);
        title.setBackground(titleBg);
        root.addView(title, lpMatchWrap(0, 0, 0, 6));

        TextView subtitle = text("גרסת ניסיון APK אמיתית", 17, Typeface.NORMAL, Color.WHITE);
        subtitle.setGravity(Gravity.CENTER);
        subtitle.setPadding(0, 0, 0, dp(18));
        subtitle.setBackground(titleBg);
        root.addView(subtitle, lpMatchWrap(0, -10, 0, 16));

        LinearLayout nameCard = card("1. שם שיופיע מתחת לאייקון");
        nameEdit = edit(TRIAL_NAME);
        nameEdit.setSingleLine(true);
        nameCard.addView(nameEdit, lpMatchWrap(0, 8, 0, 0));
        root.addView(nameCard, lpMatchWrap(0, 0, 0, 12));

        LinearLayout urlCard = card("2. כתובת URL");
        urlEdit = edit(TRIAL_URL);
        urlEdit.setSingleLine(true);
        urlEdit.setTextDirection(View.TEXT_DIRECTION_LTR);
        urlEdit.setGravity(Gravity.START | Gravity.CENTER_VERTICAL);
        urlCard.addView(urlEdit, lpMatchWrap(0, 8, 0, 8));

        Button paste = button("הדבק כתובת", false);
        paste.setOnClickListener(v -> pasteUrl());
        urlCard.addView(paste, lpMatchWrap(0, 0, 0, 0));
        root.addView(urlCard, lpMatchWrap(0, 0, 0, 12));

        LinearLayout styleCard = card("3. בחר סגנון אייקון");
        styleSpinner = new Spinner(this);
        String[] styles = {"כרטסת", "ריבוע מעוגל", "עיגול"};
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this,
                android.R.layout.simple_spinner_dropdown_item, styles);
        styleSpinner.setAdapter(adapter);
        styleSpinner.setPadding(dp(8), dp(8), dp(8), dp(8));
        styleCard.addView(styleSpinner, lpMatchWrap(0, 8, 0, 0));
        root.addView(styleCard, lpMatchWrap(0, 0, 0, 12));

        LinearLayout colorCard = card("4. צבע האייקון");
        LinearLayout colors = new LinearLayout(this);
        colors.setOrientation(LinearLayout.HORIZONTAL);
        colors.setGravity(Gravity.CENTER);
        colors.setLayoutDirection(View.LAYOUT_DIRECTION_LTR);
        int[] palette = {
                Color.rgb(247,214,119),
                Color.rgb(255,255,255),
                Color.rgb(157,210,255),
                Color.rgb(169,232,153),
                Color.rgb(255,176,198),
                Color.rgb(195,195,195)
        };
        for (int c : palette) {
            View swatch = new View(this);
            GradientDrawable gd = roundRect(c, 14);
            gd.setStroke(dp(1), Color.rgb(210,216,225));
            swatch.setBackground(gd);
            LinearLayout.LayoutParams sp = new LinearLayout.LayoutParams(dp(46), dp(46));
            sp.setMargins(dp(5), dp(5), dp(5), dp(5));
            swatch.setLayoutParams(sp);
            swatch.setOnClickListener(v -> {
                selectedColor = c;
                updatePreview();
            });
            colors.addView(swatch);
        }
        colorCard.addView(colors, lpMatchWrap(0, 8, 0, 0));
        root.addView(colorCard, lpMatchWrap(0, 0, 0, 12));

        LinearLayout previewCard = card("5. תצוגה מקדימה");
        previewIcon = text("📁\nChatGPT", 34, Typeface.BOLD, Color.rgb(8, 92, 72));
        previewIcon.setGravity(Gravity.CENTER);
        previewIcon.setPadding(dp(18), dp(24), dp(18), dp(24));
        previewCard.addView(previewIcon, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(170)));

        previewName = text(TRIAL_NAME, 24, Typeface.BOLD, Color.rgb(20,35,55));
        previewName.setGravity(Gravity.CENTER);
        previewCard.addView(previewName, lpMatchWrap(0, 8, 0, 0));
        root.addView(previewCard, lpMatchWrap(0, 0, 0, 12));

        Button test = button("בדוק קישור", false);
        test.setOnClickListener(v -> testLink());
        root.addView(test, lpMatchWrap(0, 0, 0, 8));

        Button create = button("צור APK לדוגמה", true);
        create.setOnClickListener(v -> downloadTrialApk());
        root.addView(create, lpMatchWrap(0, 0, 0, 8));

        TextView note = text("בגרסת הניסיון הראשונה הכפתור מוריד APK עובד של הדוגמה 'פנקס הכנסות'. לאחר אישור כל התהליך נחבר את השם, הכתובת והאייקון שבחרת לבנייה אוטומטית של APK חדש.",
                14, Typeface.NORMAL, Color.rgb(100,112,128));
        note.setGravity(Gravity.CENTER);
        note.setPadding(dp(8), dp(10), dp(8), 0);
        root.addView(note);

        nameEdit.setOnFocusChangeListener((v, hasFocus) -> { if (!hasFocus) updatePreview(); });
        styleSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                selectedStyle = styles[position];
                updatePreview();
            }
            @Override public void onNothingSelected(AdapterView<?> parent) { }
        });
        updatePreview();
        setContentView(scroll);
    }

    private void pasteUrl() {
        ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
        if (clipboard == null || !clipboard.hasPrimaryClip()) {
            toast("אין כתובת בלוח ההעתקה");
            return;
        }
        ClipData clip = clipboard.getPrimaryClip();
        if (clip == null || clip.getItemCount() == 0) {
            toast("אין כתובת בלוח ההעתקה");
            return;
        }
        CharSequence text = clip.getItemAt(0).coerceToText(this);
        if (text == null) {
            toast("לא נמצא טקסט להדבקה");
            return;
        }
        urlEdit.setText(text.toString().trim());
        urlEdit.setSelection(urlEdit.getText().length());
        toast("הכתובת הודבקה");
    }

    private void testLink() {
        String url = normalizedUrl();
        if (url == null) return;
        try {
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
        } catch (Exception e) {
            toast("לא ניתן לפתוח את הכתובת");
        }
    }

    private void downloadTrialApk() {
        String name = nameEdit.getText().toString().trim();
        String url = normalizedUrl();
        if (url == null) return;
        if (TextUtils.isEmpty(name)) {
            toast("יש להזין שם לאפליקציה");
            return;
        }
        updatePreview();

        boolean exactTrial = TRIAL_NAME.equals(name) && TRIAL_URL.equals(url);
        String msg = exactTrial
                ? "עכשיו ייפתח קובץ APK עובד של 'פנקס הכנסות'."
                : "בגרסת ניסיון זו ה-APK המורד הוא עדיין דוגמת 'פנקס הכנסות'. הנתונים ששינית משמשים כרגע לבדיקת הממשק בלבד.";

        new AlertDialog.Builder(this)
                .setTitle("הורדת APK")
                .setMessage(msg)
                .setNegativeButton("ביטול", null)
                .setPositiveButton("הורד", (d, which) -> {
                    try {
                        startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(TRIAL_APK_URL)));
                    } catch (Exception e) {
                        toast("לא ניתן לפתוח את ההורדה");
                    }
                })
                .show();
    }

    private String normalizedUrl() {
        String url = urlEdit.getText().toString().trim();
        if (TextUtils.isEmpty(url) || url.equals("https://")) {
            toast("יש להזין כתובת URL");
            return null;
        }
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "https://" + url;
            urlEdit.setText(url);
        }
        return url;
    }

    private void updatePreview() {
        if (previewName == null || previewIcon == null) return;
        String name = nameEdit == null ? TRIAL_NAME : nameEdit.getText().toString().trim();
        if (TextUtils.isEmpty(name)) name = "שם האפליקציה";
        previewName.setText(name);

        GradientDrawable bg = new GradientDrawable();
        bg.setColor(selectedColor);
        float radius;
        if ("עיגול".equals(selectedStyle)) radius = dp(90);
        else if ("ריבוע מעוגל".equals(selectedStyle)) radius = dp(28);
        else radius = dp(18);
        bg.setCornerRadius(radius);
        bg.setStroke(dp(2), Color.rgb(214, 170, 52));
        previewIcon.setBackground(bg);
        previewIcon.setText("📁\nChatGPT");
    }

    private LinearLayout card(String heading) {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setPadding(dp(14), dp(14), dp(14), dp(14));
        box.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        GradientDrawable bg = roundRect(Color.WHITE, 20);
        bg.setStroke(dp(1), Color.rgb(224,229,237));
        box.setBackground(bg);
        TextView h = text(heading, 19, Typeface.BOLD, Color.rgb(25,40,65));
        h.setGravity(Gravity.RIGHT);
        box.addView(h);
        return box;
    }

    private EditText edit(String value) {
        EditText e = new EditText(this);
        e.setText(value);
        e.setTextSize(19);
        e.setSingleLine(false);
        e.setPadding(dp(12), dp(12), dp(12), dp(12));
        e.setBackground(roundRect(Color.rgb(250,252,255), 14));
        e.setTextColor(Color.rgb(25,35,50));
        e.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        return e;
    }

    private Button button(String label, boolean primary) {
        Button b = new Button(this);
        b.setText(label);
        b.setTextSize(19);
        b.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        b.setAllCaps(false);
        b.setTextColor(primary ? Color.WHITE : Color.rgb(20,105,190));
        b.setPadding(dp(10), dp(12), dp(10), dp(12));
        b.setBackground(roundRect(primary ? Color.rgb(26,115,232) : Color.rgb(231,242,255), 16));
        return b;
    }

    private TextView text(String value, int sp, int style, int color) {
        TextView t = new TextView(this);
        t.setText(value);
        t.setTextSize(sp);
        t.setTypeface(Typeface.DEFAULT, style);
        t.setTextColor(color);
        t.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        return t;
    }

    private GradientDrawable roundRect(int color, int radiusDp) {
        GradientDrawable gd = new GradientDrawable();
        gd.setColor(color);
        gd.setCornerRadius(dp(radiusDp));
        return gd;
    }

    private LinearLayout.LayoutParams lpMatchWrap(int l, int t, int r, int b) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        p.setMargins(dp(l), dp(t), dp(r), dp(b));
        return p;
    }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }

    private void toast(String s) {
        Toast.makeText(this, s, Toast.LENGTH_SHORT).show();
    }
}
