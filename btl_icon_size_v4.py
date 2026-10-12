from pathlib import Path
import re, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter

root=Path('btl-build/manyot_android_v1')

# ---- Version 4 ----
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 4',s)
s=re.sub(r"versionName\s+'[^']+'","versionName '4.0'",s)
g.write_text(s,encoding='utf-8')

p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>ביטוח לאומי - גרסה \d+</title>','<title>ביטוח לאומי - גרסה 4</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='4';",t)
# Preview ratios matching the real launcher variants.
t=t.replace('.icon-preview-text.small{font-size:20px}.icon-preview-text.normal{font-size:24px}.icon-preview-text.large{font-size:28px}',
            '.icon-preview-text.small{font-size:22px}.icon-preview-text.normal{font-size:26px}.icon-preview-text.large{font-size:30px}')
t=t.replace('.icon-preview-text.small{font-size:27px}.icon-preview-text.normal{font-size:32px}.icon-preview-text.large{font-size:37px}',
            '.icon-preview-text.small{font-size:22px}.icon-preview-text.normal{font-size:26px}.icon-preview-text.large{font-size:30px}')
t=t.replace('ברירת המחדל: אפור בינוני, עם קווי רשת וכיתוב רגיל. בגרסה זו הכיתוב הוגדל להתאמה למסך הבית.',
            'ברירת המחדל: אפור בינוני, עם קווי רשת וכיתוב רגיל. הגודל הרגיל מכוון להדמיה שאושרה.')
p.write_text(t,encoding='utf-8')

# ---- Make runtime switching robust and use fresh V4 alias component names ----
j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
s=j.read_text(encoding='utf-8')
method=r'''        @android.webkit.JavascriptInterface
        public void setLauncherIcon(String background, boolean grid, String textSize) {
            final String bg = valid(background, BACKGROUNDS, "medium");
            final String size = valid(textSize, TEXT_SIZES, "normal");
            final boolean useGrid = grid;
            runOnUiThread(() -> {
                android.content.pm.PackageManager pm = getPackageManager();
                String selected = aliasClass(bg, useGrid, size);
                // Enable the requested icon FIRST, then disable all the others.
                android.content.ComponentName selectedCn = new android.content.ComponentName(getPackageName(), selected);
                pm.setComponentEnabledSetting(selectedCn,
                        android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
                        android.content.pm.PackageManager.DONT_KILL_APP);
                for (String b : BACKGROUNDS) {
                    for (boolean g : new boolean[]{false, true}) {
                        for (String z : TEXT_SIZES) {
                            String alias = aliasClass(b, g, z);
                            if (alias.equals(selected)) continue;
                            android.content.ComponentName cn = new android.content.ComponentName(getPackageName(), alias);
                            pm.setComponentEnabledSetting(cn,
                                    android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                                    android.content.pm.PackageManager.DONT_KILL_APP);
                        }
                    }
                }
                getSharedPreferences(PREFS, MODE_PRIVATE).edit()
                        .putString("background", bg)
                        .putBoolean("grid", useGrid)
                        .putString("textSize", size)
                        .apply();
            });
        }

        private String aliasClass(String bg, boolean grid, String size) {
            return "com.militzerjoseph.manyot.Icon_" + bg + "_" + (grid ? "grid" : "plain") + "_" + size + "_v4";
        }
'''
pat=r'''        @android\.webkit\.JavascriptInterface\n        public void setLauncherIcon\(String background, boolean grid, String textSize\) \{.*?\n        private String aliasClass\(String bg, boolean grid, String size\) \{.*?\n        \}\n'''
s2,n=re.subn(pat,method,s,count=1,flags=re.S)
if n!=1: raise SystemExit('Could not patch IconBridge setLauncherIcon/aliasClass')
j.write_text(s2,encoding='utf-8')

# ---- Give all launcher aliases fresh V4 component names to bypass stale launcher cache ----
manifest=root/'app/src/main/AndroidManifest.xml'
ET.register_namespace('android','http://schemas.android.com/apk/res/android')
ns='{http://schemas.android.com/apk/res/android}'
tree=ET.parse(manifest)
app=tree.getroot().find('application')
if app is None: raise SystemExit('No application')
count=0
for alias in app.findall('activity-alias'):
    name=alias.get(ns+'name','')
    if name.startswith('com.militzerjoseph.manyot.Icon_'):
        if not name.endswith('_v4'):
            alias.set(ns+'name',name+'_v4')
        count+=1
if count!=18: raise SystemExit(f'Expected 18 icon aliases, found {count}')
tree.write(manifest,encoding='utf-8',xml_declaration=True)

# ---- Rebuild 18 icons at the approved visual scale ----
icon_dir=root/'app/src/main/res/drawable-nodpi'
S=1024
font_candidates=[
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
]
font_path=next((f for f in font_candidates if Path(f).exists()),None)
if not font_path: raise SystemExit('Hebrew-capable font not found')
colors={'light':(181,187,195),'medium':(148,154,163),'dark':(111,118,128)}
# V2 was too small (112/136/160), V3 too large (200/240/280).
# Normal 185 gives text width ~60% of the 1024 icon, matching the approved mockup.
font_sizes={'small':155,'normal':185,'large':215}
label_text='ב.לאומי'
for bg_name,bg in colors.items():
    for use_grid in (False,True):
        for size_name,fs in font_sizes.items():
            im=Image.new('RGBA',(S,S),(255,255,255,0))
            mask=Image.new('L',(S,S),0)
            md=ImageDraw.Draw(mask)
            md.rounded_rectangle((42,42,S-42,S-42),radius=185,fill=255)
            base=Image.new('RGBA',(S,S),(0,0,0,0))
            px=base.load()
            for y in range(S):
                rel=max(0,min(1,(y-42)/(S-84)))
                delta=int(12*(0.5-rel))
                c=tuple(max(0,min(255,v+delta)) for v in bg)
                for x in range(S): px[x,y]=(*c,255)
            im.paste(base,(0,0),mask)
            d=ImageDraw.Draw(im)
            d.rounded_rectangle((42,42,S-42,S-42),radius=185,outline=(255,255,255,90),width=5)
            if use_grid:
                x0=y0=42; x1=y1=S-42
                for i in range(1,7):
                    x=int(x0+(x1-x0)*i/7)
                    d.line((x,y0+1,x,y1-1),fill=(255,255,255,175),width=2)
                for i in range(1,7):
                    y=int(y0+(y1-y0)*i/7)
                    d.line((x0+1,y,x1-1,y),fill=(255,255,255,175),width=2)
            font=ImageFont.truetype(font_path,fs)
            try:
                bbox=d.textbbox((0,0),label_text,font=font,direction='rtl')
                direction='rtl'; draw_text=label_text
            except Exception:
                draw_text='ימואל.ב'; direction=None
                bbox=d.textbbox((0,0),draw_text,font=font)
            tw=bbox[2]-bbox[0]; th=bbox[3]-bbox[1]
            # Approved composition: centered horizontally, in lower part of icon, fully inside safe area.
            tx=S//2-tw//2; ty=790-th//2
            shadow=Image.new('RGBA',(S,S),(0,0,0,0))
            sd=ImageDraw.Draw(shadow)
            kw={'font':font,'fill':(0,0,0,85)}
            if direction: kw['direction']=direction
            sd.text((tx+4,ty+6),draw_text,**kw)
            shadow=shadow.filter(ImageFilter.GaussianBlur(4))
            im=Image.alpha_composite(im,shadow)
            d=ImageDraw.Draw(im)
            kw={'font':font,'fill':(250,250,250,255)}
            if direction: kw['direction']=direction
            d.text((tx,ty),draw_text,**kw)
            mode='grid' if use_grid else 'plain'
            im.save(icon_dir/f'ic_btl_{bg_name}_{mode}_{size_name}.png',optimize=True)

print('BTL V4 icon sizes:',font_sizes,'with fresh v4 aliases')
