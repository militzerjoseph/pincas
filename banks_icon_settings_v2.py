from pathlib import Path
import re

# Reuse the exact approved BTL V7 icon/settings mechanism, adapted to Banks.
for source in ['btl_icon_settings_v2.py','btl_icon_options_v6.py','btl_icon_scale_v7.py']:
    code=Path(source).read_text(encoding='utf-8')
    code=code.replace('btl-build','banks-build')
    code=code.replace('ב. לאומי','בנקים')
    code=code.replace('ב.לאומי','בנקים')
    code=code.replace('ביטוח לאומי','בנקים')
    code=code.replace('btl_launcher_icon','banks_launcher_icon')
    code=code.replace('ic_btl_','ic_banks_')
    exec(compile(code, source, 'exec'), {})

root=Path('banks-build/manyot_android_v1')

# Banks has only V1 so this is Banks V2, while keeping the approved V7 icon behavior.
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 2',s)
s=re.sub(r"versionName\s+'[^']+'","versionName '2.0'",s)
g.write_text(s,encoding='utf-8')

p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>בנקים - גרסה \d+</title>','<title>בנקים - גרסה 2</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='2';",t)
p.write_text(t,encoding='utf-8')

print('Banks V2 icon settings ready: approved BTL V7 design, default medium gray + grid + medium + black')
