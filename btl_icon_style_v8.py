from pathlib import Path
import re

# Reuse the proven Manyot V9/V10 icon designer, adapted to BTL.
# BTL V7 is already built before this script runs.
for source in ['manyot_icon_style_v9.py', 'manyot_icon_style_v10.py']:
    code = Path(source).read_text(encoding='utf-8')
    code = code.replace("root=Path('hadashot-build/manyot_android_v1')", "root=Path('btl-build/manyot_android_v1')")
    code = code.replace('Manyot V9', 'BTL V8')
    code = code.replace('Manyot V10', 'BTL V8')
    code = code.replace('manyot_launcher_icon_v9', 'btl_launcher_icon_v8')
    code = code.replace('manyot_launcher_icon_v10', 'btl_launcher_icon_v8')
    code = code.replace('ic_manyot_v10_', 'ic_btl_v8_')
    code = code.replace('ic_manyot_', 'ic_btl_')
    code = code.replace('_v10', '_v8')
    code = code.replace('_v9', '_v8')
    code = code.replace('מניות', 'ב.לאומי')
    exec(compile(code, source, 'exec'), {})

root = Path('btl-build/manyot_android_v1')

# Final BTL version identity. Keep package/storage/data identity unchanged.
g = root / 'app/build.gradle'
s = g.read_text(encoding='utf-8')
s = re.sub(r'versionCode\s+\d+', 'versionCode 8', s)
s = re.sub(r"versionName\s+'[^']+'", "versionName '8.0'", s)
g.write_text(s, encoding='utf-8')

p = root / 'app/src/main/assets/index.html'
t = p.read_text(encoding='utf-8')
t = re.sub(r'<title>[^<]+</title>', '<title>ביטוח לאומי - גרסה 8</title>', t, count=1)
t = re.sub(r"const APP_VERSION='\d+';", "const APP_VERSION='8';", t)
p.write_text(t, encoding='utf-8')

print('BTL V8 ready: modern icon, expanded background palette, optional top stripe, configurable text')
