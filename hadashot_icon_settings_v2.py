from pathlib import Path
import re

# Reuse the exact approved BTL V7 icon/settings mechanism, adapted to Hadashot.
for source in ['btl_icon_settings_v2.py','btl_icon_options_v6.py','btl_icon_scale_v7.py']:
    code=Path(source).read_text(encoding='utf-8')
    code=code.replace('btl-build','hadashot-build')
    code=code.replace('ב. לאומי','חדשות')
    code=code.replace('ב.לאומי','חדשות')
    code=code.replace('ביטוח לאומי','חדשות')
    code=code.replace('btl_launcher_icon','hadashot_launcher_icon')
    code=code.replace('ic_btl_','ic_hadashot_')
    exec(compile(code, source, 'exec'), {})

root=Path('hadashot-build/manyot_android_v1')

# Hadashot currently has V1, so this becomes V2 while keeping the approved V7 icon behavior.
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 2',s)
s=re.sub(r"versionName\s+'[^']+'","versionName '2.0'",s)
g.write_text(s,encoding='utf-8')

p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>חדשות - גרסה \d+</title>','<title>חדשות - גרסה 2</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='2';",t)
p.write_text(t,encoding='utf-8')

print('Hadashot V2 icon settings ready: approved BTL V7 design, default medium gray + grid + medium + black')
