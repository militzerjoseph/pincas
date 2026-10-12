from pathlib import Path
import re

# Reuse the exact approved BTL V7 icon/settings mechanism, adapted to Manyot.
for source in ['btl_icon_settings_v2.py','btl_icon_options_v6.py','btl_icon_scale_v7.py']:
    code=Path(source).read_text(encoding='utf-8')
    code=code.replace('btl-build','hadashot-build')
    code=code.replace('ב. לאומי','מניות')
    code=code.replace('ב.לאומי','מניות')
    code=code.replace('ביטוח לאומי','מניות')
    code=code.replace('btl_launcher_icon','manyot_launcher_icon')
    code=code.replace('ic_btl_','ic_manyot_')
    exec(compile(code, source, 'exec'), {})

root=Path('hadashot-build/manyot_android_v1')

# Manyot V7 used Android versionCode 4. V8 uses 5 while preserving package/storage identity.
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 5',s)
s=re.sub(r"versionName\s+'[^']+'","versionName '5.0'",s)
g.write_text(s,encoding='utf-8')

p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>מניות - גרסה \d+</title>','<title>מניות - גרסה 8</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='8';",t)
p.write_text(t,encoding='utf-8')

print('Manyot V8 icon settings ready: approved BTL V7 design, default medium gray + grid + medium + black')
