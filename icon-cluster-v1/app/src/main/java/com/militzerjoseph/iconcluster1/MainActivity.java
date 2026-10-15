package com.militzerjoseph.iconcluster1;

import android.app.Activity;
import android.app.AlertDialog;
import android.app.Dialog;
import android.content.ClipData;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.ResolveInfo;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.Drawable;
import android.os.Build;
import android.os.Bundle;
import android.view.DragEvent;
import android.view.GestureDetector;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowInsets;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.FrameLayout;
import android.widget.GridLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;

import java.text.Collator;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class MainActivity extends Activity {

    private static final String PREFS = "icon_cluster_1";
    private static final String KEY_APPS = "selected_apps";

    private GridLayout grid;
    private TextView emptyText;
    private final ArrayList<String> selectedPackages = new ArrayList<>();

    private static class AppEntry {
        String label;
        String packageName;
        Drawable icon;

        AppEntry(String label, String packageName, Drawable icon) {
            this.label = label;
            this.packageName = packageName;
            this.icon = icon;
        }
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(Color.BLACK);
        getWindow().setNavigationBarColor(Color.BLACK);
        loadSelectedApps();
        buildMainScreen();
    }

    private void buildMainScreen() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.rgb(245, 245, 245));
        root.setLayoutParams(new ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT));

        FrameLayout header = new FrameLayout(this);
        header.setBackgroundColor(Color.rgb(17, 17, 17));
        LinearLayout.LayoutParams headerParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(64));
        root.addView(header, headerParams);
        applyHeaderInsets(header);

        TextView title = new TextView(this);
        title.setText("מקבץ איקונים 1");
        title.setTextColor(Color.WHITE);
        title.setTextSize(17);
        title.setTypeface(null, Typeface.NORMAL);
        title.setGravity(Gravity.CENTER_VERTICAL | Gravity.RIGHT);
        FrameLayout.LayoutParams titleParams = new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT);
        titleParams.leftMargin = dp(70);
        titleParams.rightMargin = dp(20);
        header.addView(title, titleParams);

        Button plus = new Button(this);
        plus.setText("+");
        plus.setTextSize(27);
        plus.setTextColor(Color.rgb(255, 216, 110));
        plus.setBackgroundColor(Color.TRANSPARENT);
        plus.setAllCaps(false);
        plus.setContentDescription("הוסף אפליקציות");
        plus.setOnClickListener(v -> showAppPicker());
        FrameLayout.LayoutParams plusParams = new FrameLayout.LayoutParams(
                dp(64), dp(64), Gravity.LEFT | Gravity.BOTTOM);
        header.addView(plus, plusParams);

        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        LinearLayout content = new LinearLayout(this);
        content.setOrientation(LinearLayout.VERTICAL);
        content.setPadding(dp(8), dp(14), dp(8), dp(20));
        scroll.addView(content, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));

        emptyText = new TextView(this);
        emptyText.setText("לחץ על + כדי להוסיף אפליקציות");
        emptyText.setTextSize(18);
        emptyText.setTextColor(Color.DKGRAY);
        emptyText.setGravity(Gravity.CENTER);
        content.addView(emptyText, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(150)));

        grid = new GridLayout(this);
        grid.setColumnCount(4);
        grid.setAlignmentMode(GridLayout.ALIGN_BOUNDS);
        grid.setUseDefaultMargins(false);
        grid.setOnDragListener(this::handleGridDrag);
        content.addView(grid, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));

        setContentView(root);
        renderGrid();
    }

    private void applyHeaderInsets(FrameLayout header) {
        header.setOnApplyWindowInsetsListener((v, insets) -> {
            int topInset;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                topInset = insets.getInsets(WindowInsets.Type.statusBars()).top;
            } else {
                topInset = insets.getSystemWindowInsetTop();
            }

            v.setPadding(0, topInset, 0, 0);
            ViewGroup.LayoutParams lp = v.getLayoutParams();
            if (lp != null) {
                lp.height = dp(64) + topInset;
                v.setLayoutParams(lp);
            }
            return insets;
        });
        header.requestApplyInsets();
    }

    private void renderGrid() {
        grid.removeAllViews();
        emptyText.setVisibility(selectedPackages.isEmpty() ? View.VISIBLE : View.GONE);

        for (String pkg : selectedPackages) {
            grid.addView(createAppCell(pkg), makeCellLayoutParams());
        }
    }

    private GridLayout.LayoutParams makeCellLayoutParams() {
        GridLayout.LayoutParams lp = new GridLayout.LayoutParams();
        lp.width = 0;
        lp.height = dp(118);
        lp.columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f);
        lp.setMargins(dp(3), dp(4), dp(3), dp(4));
        return lp;
    }

    private View createAppCell(String pkg) {
        LinearLayout cell = new LinearLayout(this);
        cell.setOrientation(LinearLayout.VERTICAL);
        cell.setGravity(Gravity.CENTER);
        cell.setPadding(dp(3), dp(6), dp(3), dp(4));
        cell.setTag(pkg);

        ImageView icon = new ImageView(this);
        icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
        LinearLayout.LayoutParams iconParams = new LinearLayout.LayoutParams(dp(58), dp(58));
        cell.addView(icon, iconParams);

        TextView name = new TextView(this);
        name.setTextSize(12);
        name.setTextColor(Color.rgb(40, 40, 40));
        name.setGravity(Gravity.CENTER);
        name.setMaxLines(2);
        cell.addView(name, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                dp(42)));

        try {
            ApplicationInfo info = getPackageManager().getApplicationInfo(pkg, 0);
            name.setText(getPackageManager().getApplicationLabel(info));
            icon.setImageDrawable(getPackageManager().getApplicationIcon(info));
        } catch (Exception e) {
            name.setText(pkg);
            icon.setImageResource(android.R.drawable.sym_def_app_icon);
        }

        installCellGestures(cell, pkg);
        return cell;
    }

    private void installCellGestures(View cell, String pkg) {
        final boolean[] dragStarted = {false};

        GestureDetector detector = new GestureDetector(this,
                new GestureDetector.SimpleOnGestureListener() {
                    @Override
                    public boolean onDown(MotionEvent e) {
                        dragStarted[0] = false;
                        return true;
                    }

                    @Override
                    public boolean onSingleTapUp(MotionEvent e) {
                        if (!dragStarted[0]) launchPackage(pkg);
                        return true;
                    }

                    @Override
                    public void onLongPress(MotionEvent e) {
                        if (!dragStarted[0]) showRemoveDialog(pkg);
                    }

                    @Override
                    public boolean onScroll(MotionEvent e1, MotionEvent e2,
                                            float distanceX, float distanceY) {
                        if (!dragStarted[0] && e1 != null && e2 != null) {
                            float dx = e2.getX() - e1.getX();
                            float dy = e2.getY() - e1.getY();
                            if ((dx * dx) + (dy * dy) > dp(10) * dp(10)) {
                                dragStarted[0] = true;
                                ClipData data = ClipData.newPlainText("package", pkg);
                                View.DragShadowBuilder shadow = new View.DragShadowBuilder(cell);
                                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                                    cell.startDragAndDrop(data, shadow, pkg, 0);
                                } else {
                                    cell.startDrag(data, shadow, pkg, 0);
                                }
                                cell.setAlpha(0.35f);
                            }
                        }
                        return true;
                    }
                });

        cell.setOnTouchListener((v, event) -> {
            detector.onTouchEvent(event);
            if (event.getActionMasked() == MotionEvent.ACTION_CANCEL) {
                v.setAlpha(1f);
            }
            return true;
        });
    }

    private boolean handleGridDrag(View v, DragEvent event) {
        switch (event.getAction()) {
            case DragEvent.ACTION_DRAG_STARTED:
                return event.getLocalState() instanceof String;

            case DragEvent.ACTION_DROP:
                Object local = event.getLocalState();
                if (!(local instanceof String)) return false;
                movePackageTo((String) local, event.getX(), event.getY());
                return true;

            case DragEvent.ACTION_DRAG_ENDED:
                for (int i = 0; i < grid.getChildCount(); i++) {
                    grid.getChildAt(i).setAlpha(1f);
                }
                return true;

            default:
                return true;
        }
    }

    private void movePackageTo(String pkg, float x, float y) {
        int from = selectedPackages.indexOf(pkg);
        if (from < 0 || selectedPackages.size() < 2) return;

        int target = findNearestCellIndex(x, y);
        if (target < 0) target = selectedPackages.size() - 1;
        if (target == from) {
            renderGrid();
            return;
        }

        String moving = selectedPackages.remove(from);
        if (from < target) target--;
        if (target < 0) target = 0;
        if (target > selectedPackages.size()) target = selectedPackages.size();
        selectedPackages.add(target, moving);
        saveSelectedApps();
        renderGrid();
    }

    private int findNearestCellIndex(float x, float y) {
        int count = grid.getChildCount();
        if (count == 0) return -1;

        int nearest = 0;
        double best = Double.MAX_VALUE;
        for (int i = 0; i < count; i++) {
            View child = grid.getChildAt(i);
            float cx = child.getLeft() + child.getWidth() / 2f;
            float cy = child.getTop() + child.getHeight() / 2f;
            double dx = x - cx;
            double dy = y - cy;
            double distance = dx * dx + dy * dy;
            if (distance < best) {
                best = distance;
                nearest = i;
            }
        }
        return nearest;
    }

    private void showRemoveDialog(String pkg) {
        String label = pkg;
        try {
            ApplicationInfo info = getPackageManager().getApplicationInfo(pkg, 0);
            label = String.valueOf(getPackageManager().getApplicationLabel(info));
        } catch (Exception ignored) {
        }

        new AlertDialog.Builder(this)
                .setTitle(label)
                .setMessage("להסיר את האייקון מהמקבץ?")
                .setPositiveButton("הסר מהמקבץ", (dialog, which) -> {
                    selectedPackages.remove(pkg);
                    saveSelectedApps();
                    renderGrid();
                })
                .setNegativeButton("ביטול", null)
                .show();
    }

    private void launchPackage(String pkg) {
        try {
            Intent intent = getPackageManager().getLaunchIntentForPackage(pkg);
            if (intent == null) {
                Toast.makeText(this, "לא ניתן לפתוח את האפליקציה", Toast.LENGTH_SHORT).show();
                return;
            }
            startActivity(intent);
        } catch (Exception e) {
            Toast.makeText(this, "לא ניתן לפתוח את האפליקציה", Toast.LENGTH_SHORT).show();
        }
    }

    private void showAppPicker() {
        final List<AppEntry> apps = loadLaunchableApps();
        final Set<String> existing = new HashSet<>(selectedPackages);
        final LinkedHashSet<String> chosen = new LinkedHashSet<>();

        Dialog dialog = new Dialog(this);
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(Color.WHITE);
        root.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);

        TextView pickerTitle = new TextView(this);
        pickerTitle.setText("בחר אפליקציות");
        pickerTitle.setTextSize(17);
        pickerTitle.setTextColor(Color.WHITE);
        pickerTitle.setTypeface(null, Typeface.NORMAL);
        pickerTitle.setGravity(Gravity.CENTER_VERTICAL | Gravity.RIGHT);
        pickerTitle.setPadding(dp(20), 0, dp(20), 0);
        pickerTitle.setBackgroundColor(Color.rgb(17, 17, 17));
        root.addView(pickerTitle, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(62)));

        ScrollView scroll = new ScrollView(this);
        LinearLayout list = new LinearLayout(this);
        list.setOrientation(LinearLayout.VERTICAL);
        list.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        scroll.addView(list, new ScrollView.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT));
        root.addView(scroll, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        for (AppEntry app : apps) {
            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            row.setGravity(Gravity.CENTER_VERTICAL);
            row.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
            row.setPadding(dp(8), dp(8), dp(10), dp(8));

            CheckBox check = new CheckBox(this);
            boolean alreadyAdded = existing.contains(app.packageName);
            check.setChecked(alreadyAdded);
            check.setEnabled(!alreadyAdded);
            row.addView(check, new LinearLayout.LayoutParams(dp(48), dp(48)));

            ImageView icon = new ImageView(this);
            icon.setImageDrawable(app.icon);
            icon.setScaleType(ImageView.ScaleType.FIT_CENTER);
            row.addView(icon, new LinearLayout.LayoutParams(dp(44), dp(44)));

            TextView label = new TextView(this);
            label.setText(app.label);
            label.setTextSize(17);
            label.setTextColor(Color.rgb(30, 30, 30));
            label.setGravity(Gravity.RIGHT | Gravity.CENTER_VERTICAL);
            LinearLayout.LayoutParams labelParams = new LinearLayout.LayoutParams(0, dp(52), 1f);
            labelParams.setMarginStart(dp(10));
            row.addView(label, labelParams);

            if (!alreadyAdded) {
                View.OnClickListener toggle = v -> check.setChecked(!check.isChecked());
                row.setOnClickListener(toggle);
                icon.setOnClickListener(toggle);
                label.setOnClickListener(toggle);
                check.setOnCheckedChangeListener((buttonView, isChecked) -> {
                    if (isChecked) chosen.add(app.packageName);
                    else chosen.remove(app.packageName);
                });
            }

            View divider = new View(this);
            divider.setBackgroundColor(Color.rgb(232, 232, 232));

            list.addView(row, new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, dp(62)));
            list.addView(divider, new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, 1));
        }

        Button add = new Button(this);
        add.setText("הוסף");
        add.setTextSize(18);
        add.setAllCaps(false);
        add.setOnClickListener(v -> {
            if (!chosen.isEmpty()) {
                for (AppEntry app : apps) {
                    if (chosen.contains(app.packageName) && !selectedPackages.contains(app.packageName)) {
                        selectedPackages.add(app.packageName);
                    }
                }
                saveSelectedApps();
                renderGrid();
            }
            dialog.dismiss();
        });
        LinearLayout.LayoutParams addParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(64));
        addParams.setMargins(dp(16), dp(8), dp(16), dp(14));
        root.addView(add, addParams);

        dialog.setContentView(root);
        dialog.setOnShowListener(d -> {
            Window w = dialog.getWindow();
            if (w != null) {
                w.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
            }
        });
        dialog.show();
        Window w = dialog.getWindow();
        if (w != null) {
            w.setLayout(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);
        }
    }

    @SuppressWarnings("deprecation")
    private List<AppEntry> loadLaunchableApps() {
        ArrayList<AppEntry> result = new ArrayList<>();
        Intent launcher = new Intent(Intent.ACTION_MAIN, null);
        launcher.addCategory(Intent.CATEGORY_LAUNCHER);

        List<ResolveInfo> infos = getPackageManager().queryIntentActivities(launcher, 0);
        Set<String> seen = new HashSet<>();

        for (ResolveInfo info : infos) {
            if (info.activityInfo == null) continue;
            String pkg = info.activityInfo.packageName;
            if (pkg == null || pkg.equals(getPackageName()) || seen.contains(pkg)) continue;
            seen.add(pkg);

            String label = String.valueOf(info.loadLabel(getPackageManager()));
            Drawable icon;
            try {
                icon = info.loadIcon(getPackageManager());
            } catch (Exception e) {
                icon = getDrawable(android.R.drawable.sym_def_app_icon);
            }
            result.add(new AppEntry(label, pkg, icon));
        }

        Collator collator = Collator.getInstance(new Locale("he", "IL"));
        result.sort((a, b) -> collator.compare(a.label, b.label));
        return result;
    }

    private void loadSelectedApps() {
        selectedPackages.clear();
        String raw = getSharedPreferences(PREFS, MODE_PRIVATE).getString(KEY_APPS, "[]");
        try {
            JSONArray array = new JSONArray(raw);
            for (int i = 0; i < array.length(); i++) {
                String pkg = array.optString(i, "");
                if (!pkg.isEmpty() && !selectedPackages.contains(pkg)) selectedPackages.add(pkg);
            }
        } catch (Exception ignored) {
        }
    }

    private void saveSelectedApps() {
        JSONArray array = new JSONArray();
        for (String pkg : selectedPackages) array.put(pkg);
        getSharedPreferences(PREFS, MODE_PRIVATE)
                .edit()
                .putString(KEY_APPS, array.toString())
                .apply();
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }
}
