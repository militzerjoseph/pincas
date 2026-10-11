package com.militzer.shortcutbuilder;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class HistoryActivity extends Activity {
    private LinearLayout list;

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

        TextView title = text("היסטוריית יצירה והורדה", 26, Typeface.BOLD, Color.WHITE);
        title.setGravity(Gravity.CENTER);
        title.setPadding(dp(12), dp(18), dp(12), dp(18));
        title.setBackground(roundRect(Color.rgb(26, 115, 232), 20));
        root.addView(title, matchWrap(0, 0, 0, 14));

        TextView help = text(
                "כאן אפשר לראות מתי נשלחה כל בנייה, מה המצב שלה ומתי ההורדה הסתיימה.",
                15,
                Typeface.NORMAL,
                Color.rgb(80, 95, 115));
        help.setGravity(Gravity.RIGHT);
        root.addView(help, matchWrap(0, 0, 0, 12));

        list = new LinearLayout(this);
        list.setOrientation(LinearLayout.VERTICAL);
        list.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        root.addView(list, matchWrap(0, 0, 0, 0));

        setContentView(scroll);
    }

    @Override
    protected void onResume() {
        super.onResume();
        rebuildHistory();
    }

    private void rebuildHistory() {
        list.removeAllViews();
        JSONArray records = HistoryStore.getRecords(this);

        if (records.length() == 0) {
            TextView empty = text("עדיין אין היסטוריית יצירה.", 18, Typeface.NORMAL,
                    Color.rgb(90, 105, 125));
            empty.setGravity(Gravity.CENTER);
            empty.setPadding(dp(8), dp(24), dp(8), dp(24));
            list.addView(empty, matchWrap(0, 0, 0, 0));
            return;
        }

        for (int i = 0; i < records.length(); i++) {
            JSONObject item = records.optJSONObject(i);
            if (item == null) continue;

            LinearLayout card = new LinearLayout(this);
            card.setOrientation(LinearLayout.VERTICAL);
            card.setPadding(dp(14), dp(14), dp(14), dp(14));
            card.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);

            GradientDrawable bg = roundRect(Color.WHITE, 18);
            bg.setStroke(dp(1), Color.rgb(220, 228, 238));
            card.setBackground(bg);

            String name = item.optString("name", "APK");
            TextView nameView = text(name, 20, Typeface.BOLD, Color.rgb(25, 40, 65));
            nameView.setGravity(Gravity.RIGHT);
            card.addView(nameView);

            long requestedAt = item.optLong("requested_at", 0L);
            TextView sent = text(
                    "נשלח: " + formatDate(requestedAt),
                    16,
                    Typeface.NORMAL,
                    Color.rgb(70, 85, 105));
            sent.setGravity(Gravity.RIGHT);
            card.addView(sent, matchWrap(0, 5, 0, 0));

            String status = item.optString("status", "לא ידוע");
            TextView statusView = text(
                    "מצב: " + status,
                    17,
                    Typeface.BOLD,
                    Color.rgb(20, 105, 190));
            statusView.setGravity(Gravity.RIGHT);
            card.addView(statusView, matchWrap(0, 5, 0, 0));

            long downloadedAt = item.optLong("downloaded_at", 0L);
            if (downloadedAt > 0) {
                TextView downloaded = text(
                        "הורד: " + formatDate(downloadedAt),
                        16,
                        Typeface.NORMAL,
                        Color.rgb(45, 120, 70));
                downloaded.setGravity(Gravity.RIGHT);
                card.addView(downloaded, matchWrap(0, 5, 0, 0));
            }

            String fileName = item.optString("file_name", "");
            if (!fileName.isEmpty()) {
                TextView file = text(
                        "קובץ: " + fileName,
                        14,
                        Typeface.NORMAL,
                        Color.rgb(100, 110, 125));
                file.setGravity(Gravity.RIGHT);
                card.addView(file, matchWrap(0, 5, 0, 0));
            }

            list.addView(card, matchWrap(0, 0, 0, 10));
        }
    }

    private String formatDate(long time) {
        if (time <= 0) return "-";
        return new SimpleDateFormat("dd.MM.yyyy HH:mm", new Locale("he", "IL"))
                .format(new Date(time));
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

    private LinearLayout.LayoutParams matchWrap(int l, int t, int r, int b) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT);
        p.setMargins(dp(l), dp(t), dp(r), dp(b));
        return p;
    }

    private int dp(int v) {
        return Math.round(v * getResources().getDisplayMetrics().density);
    }
}
