from pathlib import Path

path = Path('icon-cluster-v1/app/src/main/java/com/militzerjoseph/iconcluster1/MainActivity.java')
s = path.read_text(encoding='utf-8')

# Add explicit move-mode state.
anchor = '    private LinearLayout mainRoot;\n'
if anchor not in s:
    raise SystemExit('Patch anchor not found: mainRoot')
s = s.replace(anchor, anchor + '    private String moveModePackage = null;\n', 1)

# Replace the old always-on gesture/drag handling with an explicit move mode.
start = s.index('    private void installCellGestures(View cell, String pkg) {')
end = s.index('    private boolean handleGridDrag(View v, DragEvent event) {', start)
new_gestures = r'''    private void installCellGestures(View cell, String pkg) {
        if (moveModePackage != null) {
            if (pkg.equals(moveModePackage)) {
                cell.setBackgroundColor(Color.parseColor("#dfe6ef"));
                final float[] down = new float[2];
                final boolean[] dragStarted = {false};

                cell.setOnTouchListener((v, event) -> {
                    switch (event.getActionMasked()) {
                        case MotionEvent.ACTION_DOWN:
                            down[0] = event.getX();
                            down[1] = event.getY();
                            dragStarted[0] = false;
                            return true;

                        case MotionEvent.ACTION_MOVE:
                            if (!dragStarted[0]) {
                                float dx = event.getX() - down[0];
                                float dy = event.getY() - down[1];
                                if ((dx * dx) + (dy * dy) > dp(6) * dp(6)) {
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

                        case MotionEvent.ACTION_UP:
                            if (!dragStarted[0]) {
                                Toast.makeText(this,
                                        "גרור את האייקון למקום הרצוי, או לחץ על אייקון היעד",
                                        Toast.LENGTH_SHORT).show();
                            }
                            return true;

                        case MotionEvent.ACTION_CANCEL:
                            cell.setAlpha(1f);
                            return true;
                    }
                    return true;
                });
            } else {
                // In move mode, tapping another icon moves the selected icon to that position.
                cell.setOnClickListener(v -> moveSelectedToPackage(pkg));
            }
            return;
        }

        GestureDetector detector = new GestureDetector(this,
                new GestureDetector.SimpleOnGestureListener() {
                    @Override
                    public boolean onDown(MotionEvent e) {
                        return true;
                    }

                    @Override
                    public boolean onSingleTapUp(MotionEvent e) {
                        launchPackage(pkg);
                        return true;
                    }

                    @Override
                    public void onLongPress(MotionEvent e) {
                        showRemoveDialog(pkg);
                    }
                });

        cell.setOnTouchListener((v, event) -> {
            detector.onTouchEvent(event);
            return true;
        });
    }

'''
s = s[:start] + new_gestures + s[end:]

# Replace coordinate move logic with a shared target-index helper; no drag is active outside move mode.
start = s.index('    private void movePackageTo(String pkg, float x, float y) {')
end = s.index('    private int findNearestCellIndex(float x, float y) {', start)
new_move = r'''    private void movePackageTo(String pkg, float x, float y) {
        int target = findNearestCellIndex(x, y);
        if (target < 0) target = selectedPackages.size() - 1;
        movePackageToIndex(pkg, target);
    }

    private void moveSelectedToPackage(String targetPkg) {
        if (moveModePackage == null) return;
        int target = selectedPackages.indexOf(targetPkg);
        if (target < 0) return;
        movePackageToIndex(moveModePackage, target);
    }

    private void movePackageToIndex(String pkg, int target) {
        int from = selectedPackages.indexOf(pkg);
        if (from < 0 || selectedPackages.size() < 2) return;
        if (target < 0) target = 0;
        if (target >= selectedPackages.size()) target = selectedPackages.size() - 1;
        if (target == from) return;

        String moving = selectedPackages.remove(from);
        if (target > selectedPackages.size()) target = selectedPackages.size();
        selectedPackages.add(target, moving);
        saveSelectedApps();
        renderGrid();
    }

'''
s = s[:start] + new_move + s[end:]

# Turn the long-press dialog into an actions menu, with removal confirmation kept as a second step.
start = s.index('    private void showRemoveDialog(String pkg) {')
end = s.index('    private void launchPackage(String pkg) {', start)
new_menu = r'''    private void showRemoveDialog(String pkg) {
        String label = getAppLabel(pkg);
        String[] actions = {"הזזה", "הסר מהמקבץ", "ביטול"};

        new AlertDialog.Builder(this)
                .setTitle(label)
                .setItems(actions, (dialog, which) -> {
                    if (which == 0) {
                        moveModePackage = pkg;
                        renderGrid();
                        Toast.makeText(this,
                                "מצב הזזה: גרור את האייקון או לחץ על אייקון היעד. חץ חזרה לסיום.",
                                Toast.LENGTH_LONG).show();
                    } else if (which == 1) {
                        confirmRemove(pkg, label);
                    }
                })
                .show();
    }

    private String getAppLabel(String pkg) {
        try {
            ApplicationInfo info = getPackageManager().getApplicationInfo(pkg, 0);
            return String.valueOf(getPackageManager().getApplicationLabel(info));
        } catch (Exception ignored) {
            return pkg;
        }
    }

    private void confirmRemove(String pkg, String label) {
        new AlertDialog.Builder(this)
                .setTitle(label)
                .setMessage("להסיר את האייקון מהמקבץ?")
                .setPositiveButton("הסר מהמקבץ", (dialog, which) -> {
                    selectedPackages.remove(pkg);
                    if (pkg.equals(moveModePackage)) moveModePackage = null;
                    saveSelectedApps();
                    renderGrid();
                })
                .setNegativeButton("ביטול", null)
                .show();
    }

'''
s = s[:start] + new_menu + s[end:]

# Back exits move mode first, without closing the app.
anchor = '    private int dp(int value) {\n'
if anchor not in s:
    raise SystemExit('Patch anchor not found: dp method')
back_method = r'''    @Override
    public void onBackPressed() {
        if (moveModePackage != null) {
            moveModePackage = null;
            renderGrid();
            Toast.makeText(this, "מצב ההזזה הסתיים", Toast.LENGTH_SHORT).show();
            return;
        }
        super.onBackPressed();
    }

'''
s = s.replace(anchor, back_method + anchor, 1)

path.write_text(s, encoding='utf-8')
print('Applied Icon Cluster V2.2 explicit move mode')
