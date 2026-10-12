from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

root=Path('btl-build/manyot_android_v1')

# Version 3
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 3',s)
s=re.sub(r"versionName\s+'[^']+'","versionName '3.0'",s)
g.write_text(s,encoding='utf-8')

p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>ביטוח לאומי - גרסה \d+</title>','<title>ביטוח לאומי - גרסה 3</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='3';",t)
# Make the settings preview reflect the new, much larger real launcher text scale.
t=t.replace('.icon-preview-text.small{font-size:20px}.icon-preview-text.normal{font-size:24px}.icon-preview-text.large{font-size:28px}',
            '.icon-preview-text.small{font-size:27px}.icon-preview-text.normal{font-size:32px}.icon-preview-text.large{font-size:37px}')
t=t.replace('ברירת המחדל: אפור בינוני, עם קווי רשת וכיתוב רגיל.',
            'ברירת המחדל: אפור בינוני, עם קווי רשת וכיתוב רגיל. בגרסה זו הכיתוב הוגדל להתאמה למסך הבית.')
p.write_text(t,encoding='utf-8')

# Rebuild all 18 launcher icons with significantly larger lettering.
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
# V2 was 112/136/160. V3 is deliberately much larger so launcher display matches the approved mockup.
font_sizes={'small':200,'normal':240,'large':280}
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
            # Keep text in the approved lower area, but wider and more prominent.
            tx=S//2-tw//2; ty=790-th//2
            shadow=Image.new('RGBA',(S,S),(0,0,0,0))
            sd=ImageDraw.Draw(shadow)
            kw={'font':font,'fill':(0,0,0,90)}
            if direction: kw['direction']=direction
            sd.text((tx+5,ty+7),draw_text,**kw)
            shadow=shadow.filter(ImageFilter.GaussianBlur(5))
            im=Image.alpha_composite(im,shadow)
            d=ImageDraw.Draw(im)
            kw={'font':font,'fill':(250,250,250,255)}
            if direction: kw['direction']=direction
            d.text((tx,ty),draw_text,**kw)
            mode='grid' if use_grid else 'plain'
            im.save(icon_dir/f'ic_btl_{bg_name}_{mode}_{size_name}.png',optimize=True)

print('BTL V3 launcher icons rebuilt with sizes',font_sizes)
