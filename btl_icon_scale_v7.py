from pathlib import Path
import re, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter

root=Path('btl-build/manyot_android_v1')

# Version 7
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 7',s)
s=re.sub(r"versionName\s+'[^']+'","versionName '7.0'",s)
g.write_text(s,encoding='utf-8')

# Settings UI: V6 large becomes V7 medium; add a new larger size.
# Default text color in V7 is black.
p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>ביטוח לאומי - גרסה \d+</title>','<title>ביטוח לאומי - גרסה 7</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='7';",t)
t=t.replace('.icon-preview-text.small{font-size:24px}.icon-preview-text.normal{font-size:28px}.icon-preview-text.large{font-size:32px}',
            '.icon-preview-text.small{font-size:28px}.icon-preview-text.normal{font-size:32px}.icon-preview-text.large{font-size:36px}')
t=t.replace("onclick=\"setLauncherIconTextSize('normal')\">רגיל</button>",
            "onclick=\"setLauncherIconTextSize('normal')\">בינוני</button>")
t=t.replace("let launcherIconSettings={background:'medium',grid:true,textSize:'normal',textColor:'white'};",
            "let launcherIconSettings={background:'medium',grid:true,textSize:'normal',textColor:'black'};")
t=t.replace("function resetLauncherIcon(){launcherIconSettings={background:'medium',grid:true,textSize:'normal',textColor:'white'};",
            "function resetLauncherIcon(){launcherIconSettings={background:'medium',grid:true,textSize:'normal',textColor:'black'};")
t=t.replace('כיתוב רגיל ולבן', 'כיתוב בינוני ושחור')
t=t.replace('כיתוב בינוני ולבן', 'כיתוב בינוני ושחור')
t=t.replace('הכיתוב הוגדל והודגש, ונשאר שורת רשת אחת למעלה.',
            'הכיתוב נשאר באותו עובי, הועלה עוד שורת רשת אחת, והגודל שהיה גדול בגרסה הקודמת הוא כעת בינוני. ברירת המחדל של צבע הכיתוב היא שחור.')
p.write_text(t,encoding='utf-8')

# Java: fresh aliases for Samsung launcher + one-time migration of old V6 "large" to V7 "normal".
# Default text color fallback is black.
j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
s=j.read_text(encoding='utf-8')
s=s.replace(' + color + "_v6";', ' + color + "_v7";')
old='''            String size = p.getString("textSize", "normal");
            String color = p.getString("textColor", "white");'''
new='''            String size = p.getString("textSize", "normal");
            if (!p.getBoolean("v7_size_migrated", false)) {
                if ("large".equals(size)) size = "normal";
                p.edit().putString("textSize", size).putBoolean("v7_size_migrated", true).apply();
            }
            String color = p.getString("textColor", "black");'''
if old not in s:
    raise SystemExit('Could not add V7 size migration')
s=s.replace(old,new,1)
s=s.replace('valid(textColor, TEXT_COLORS, "white")','valid(textColor, TEXT_COLORS, "black")')
j.write_text(s,encoding='utf-8')

# Manifest: fresh alias names force launcher refresh after update.
# Default alias and application icon use black text.
manifest=root/'app/src/main/AndroidManifest.xml'
ET.register_namespace('android','http://schemas.android.com/apk/res/android')
ns='{http://schemas.android.com/apk/res/android}'
tree=ET.parse(manifest)
app=tree.getroot().find('application')
if app is None: raise SystemExit('No application')
count=0
for alias in app.findall('activity-alias'):
    name=alias.get(ns+'name','')
    if name.endswith('_v6') and name.startswith('com.militzerjoseph.manyot.Icon_'):
        new_name=name[:-3]+'_v7'
        alias.set(ns+'name',new_name)
        alias.set(ns+'enabled','true' if new_name.endswith('Icon_medium_grid_normal_black_v7') else 'false')
        count+=1
if count!=120:
    raise SystemExit(f'Expected 120 V6 aliases, got {count}')
app.set(ns+'icon','@drawable/ic_btl_medium_grid_normal_black')
if ns+'roundIcon' in app.attrib:
    app.set(ns+'roundIcon','@drawable/ic_btl_medium_grid_normal_black')
tree.write(manifest,encoding='utf-8',xml_declaration=True)

# Rebuild all 120 icons.
# V6 sizes were 180/210/240. In V7:
#   small  = 210
#   medium = 240  (exactly the old V6 largest)
#   large  = 270, horizontally compressed slightly so it remains inside the icon.
# The text center moves from y=656 to y=522: one more grid row upward.
icon_dir=root/'app/src/main/res/drawable-nodpi'
for old_icon in icon_dir.glob('ic_btl_*.png'):
    old_icon.unlink()

S=1024
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if not Path(font_path).exists():
    raise SystemExit('Bold Hebrew-capable font not found')

backgrounds={
    'light':(181,187,195),
    'medium':(148,154,163),
    'dark':(111,118,128),
    'sky':(169,212,232),
}
font_sizes={'small':210,'normal':240,'large':270}
horizontal_scale={'small':1.0,'normal':1.0,'large':0.90}
text_colors={
    'white':(250,250,250,255),
    'black':(20,20,20,255),
    'charcoal':(52,58,64,255),
    'navy':(23,54,93,255),
    'yellow':(255,216,77,255),
}
label_text='ב.לאומי'
TEXT_CENTER_Y=522

for bg_name,bg in backgrounds.items():
    for use_grid in (False,True):
        for size_name,fs in font_sizes.items():
            for color_name,text_rgba in text_colors.items():
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
                    for x in range(S):
                        px[x,y]=(*c,255)
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
                probe=ImageDraw.Draw(Image.new('RGBA',(1,1)))
                bbox=probe.textbbox((0,0),label_text,font=font,direction='rtl')
                tw=bbox[2]-bbox[0]; th=bbox[3]-bbox[1]
                pad=22
                text_layer=Image.new('RGBA',(tw+pad*2,th+pad*2),(0,0,0,0))
                td=ImageDraw.Draw(text_layer)
                td.text((pad-bbox[0],pad-bbox[1]),label_text,font=font,fill=text_rgba,direction='rtl')

                scale=horizontal_scale[size_name]
                if scale!=1.0:
                    text_layer=text_layer.resize((int(text_layer.width*scale),text_layer.height),Image.Resampling.LANCZOS)

                tx=(S-text_layer.width)//2
                ty=int(TEXT_CENTER_Y-text_layer.height/2)

                # Keep the same bold look and subtle shadow as V6.
                alpha=text_layer.getchannel('A')
                shadow_alpha=alpha.filter(ImageFilter.GaussianBlur(5))
                shadow=Image.new('RGBA',text_layer.size,(0,0,0,0))
                shadow.putalpha(shadow_alpha.point(lambda a: int(a*0.42)))
                im.alpha_composite(shadow,(tx+6,ty+8))
                im.alpha_composite(text_layer,(tx,ty))

                mode='grid' if use_grid else 'plain'
                im.save(icon_dir/f'ic_btl_{bg_name}_{mode}_{size_name}_{color_name}.png',optimize=True)

print('BTL V7 ready: center y=522, sizes 210/240/270, V6 large=V7 medium, default text black, weight unchanged')
