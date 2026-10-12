from pathlib import Path
import re, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter

root=Path('btl-build/manyot_android_v1')

# ---- version ----
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 6',s)
s=re.sub(r"versionName\s+'[^']+'","versionName '6.0'",s)
g.write_text(s,encoding='utf-8')

# ---- HTML settings: add sky background + text-color choices ----
p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>ביטוח לאומי - גרסה \d+</title>','<title>ביטוח לאומי - גרסה 6</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='6';",t)

# preview CSS additions/replacements
if '.icon-settings-preview.sky' not in t:
    t=t.replace('.icon-settings-preview.light{background-color:#b5bbc3}.icon-settings-preview.medium{background-color:#949aa3}.icon-settings-preview.dark{background-color:#6f7680}',
                '.icon-settings-preview.light{background-color:#b5bbc3}.icon-settings-preview.medium{background-color:#949aa3}.icon-settings-preview.dark{background-color:#6f7680}.icon-settings-preview.sky{background-color:#a9d4e8}')
if '.icon-preview-text.white' not in t:
    t=t.replace('.icon-preview-text{font-weight:400;', '.icon-preview-text{font-weight:700;')
    t=t.replace('.icon-preview-text.small{font-size:22px}.icon-preview-text.normal{font-size:26px}.icon-preview-text.large{font-size:30px}',
                '.icon-preview-text.small{font-size:24px}.icon-preview-text.normal{font-size:28px}.icon-preview-text.large{font-size:32px}\n.icon-preview-text.white{color:#fff}.icon-preview-text.black{color:#000}.icon-preview-text.charcoal{color:#343a40}.icon-preview-text.navy{color:#17365d}.icon-preview-text.yellow{color:#ffd84d}')

# Replace launcher icon JS block wholesale.
js=r'''let launcherIconSettings={background:'medium',grid:true,textSize:'normal',textColor:'white'};
function readLauncherIconSettings(){
  try{
    if(window.AndroidIcon&&AndroidIcon.getIconStyle){
      const obj=JSON.parse(String(AndroidIcon.getIconStyle()||'{}'));
      if(['light','medium','dark','sky'].includes(obj.background))launcherIconSettings.background=obj.background;
      if(typeof obj.grid==='boolean')launcherIconSettings.grid=obj.grid;
      if(['small','normal','large'].includes(obj.textSize))launcherIconSettings.textSize=obj.textSize;
      if(['white','black','charcoal','navy','yellow'].includes(obj.textColor))launcherIconSettings.textColor=obj.textColor;
    }
  }catch(e){}
  return launcherIconSettings;
}
function iconSettingsHtml(){
  const x=readLauncherIconSettings();
  const gridClass=x.grid?' grid':'';
  return `<h2>אייקון האפליקציה</h2>
    <div class="icon-settings-preview-wrap"><div class="icon-settings-preview ${x.background}${gridClass}"><span class="icon-preview-text ${x.textSize} ${x.textColor}">ב.לאומי</span></div></div>
    <div class="icon-choice-group"><div class="icon-choice-title">צבע הרקע</div><div class="icon-choice-row">
      <button class="icon-choice ${x.background==='light'?'on':''}" onclick="setLauncherIconBackground('light')">אפור בהיר</button>
      <button class="icon-choice ${x.background==='medium'?'on':''}" onclick="setLauncherIconBackground('medium')">אפור בינוני</button>
      <button class="icon-choice ${x.background==='dark'?'on':''}" onclick="setLauncherIconBackground('dark')">אפור כהה</button>
      <button class="icon-choice ${x.background==='sky'?'on':''}" onclick="setLauncherIconBackground('sky')">תכלת</button>
    </div></div>
    <div class="icon-choice-group"><div class="icon-choice-title">קווי רשת</div><div class="icon-choice-row two">
      <button class="icon-choice ${x.grid?'on':''}" onclick="setLauncherIconGrid(true)">עם קווים</button>
      <button class="icon-choice ${!x.grid?'on':''}" onclick="setLauncherIconGrid(false)">ללא קווים</button>
    </div></div>
    <div class="icon-choice-group"><div class="icon-choice-title">גודל הכיתוב בתוך האייקון</div><div class="icon-choice-row">
      <button class="icon-choice ${x.textSize==='small'?'on':''}" onclick="setLauncherIconTextSize('small')">קטן</button>
      <button class="icon-choice ${x.textSize==='normal'?'on':''}" onclick="setLauncherIconTextSize('normal')">רגיל</button>
      <button class="icon-choice ${x.textSize==='large'?'on':''}" onclick="setLauncherIconTextSize('large')">גדול</button>
    </div></div>
    <div class="icon-choice-group"><div class="icon-choice-title">צבע הכיתוב בתוך האייקון</div><div class="icon-choice-row">
      <button class="icon-choice ${x.textColor==='white'?'on':''}" onclick="setLauncherIconTextColor('white')">לבן</button>
      <button class="icon-choice ${x.textColor==='black'?'on':''}" onclick="setLauncherIconTextColor('black')">שחור</button>
      <button class="icon-choice ${x.textColor==='charcoal'?'on':''}" onclick="setLauncherIconTextColor('charcoal')">אפור כהה</button>
      <button class="icon-choice ${x.textColor==='navy'?'on':''}" onclick="setLauncherIconTextColor('navy')">כחול כהה</button>
      <button class="icon-choice ${x.textColor==='yellow'?'on':''}" onclick="setLauncherIconTextColor('yellow')">צהוב</button>
    </div></div>
    <div class="icon-note">ברירת המחדל: אפור בינוני, עם קווי רשת, כיתוב רגיל ולבן. הכיתוב הוגדל והודגש, ונשאר שורת רשת אחת למעלה.</div>
    <button class="reset-design" onclick="resetLauncherIcon()">החזר אייקון לברירת המחדל</button>
    <button class="close" onclick="backToSettings()">חזרה להגדרות</button>`;
}
function applyLauncherIconSettings(){
  try{
    if(window.AndroidIcon&&AndroidIcon.setLauncherIcon){
      AndroidIcon.setLauncherIcon(launcherIconSettings.background,!!launcherIconSettings.grid,launcherIconSettings.textSize,launcherIconSettings.textColor);
      toast('האייקון עודכן');
    }else toast('שינוי האייקון זמין בגרסת APK');
  }catch(e){toast('לא ניתן לעדכן את האייקון');}
  replaceOverlayHtml(iconSettingsHtml());
}
function setLauncherIconBackground(v){if(!['light','medium','dark','sky'].includes(v))return;launcherIconSettings.background=v;applyLauncherIconSettings();}
function setLauncherIconGrid(v){launcherIconSettings.grid=!!v;applyLauncherIconSettings();}
function setLauncherIconTextSize(v){if(!['small','normal','large'].includes(v))return;launcherIconSettings.textSize=v;applyLauncherIconSettings();}
function setLauncherIconTextColor(v){if(!['white','black','charcoal','navy','yellow'].includes(v))return;launcherIconSettings.textColor=v;applyLauncherIconSettings();}
function resetLauncherIcon(){launcherIconSettings={background:'medium',grid:true,textSize:'normal',textColor:'white'};applyLauncherIconSettings();}
function openIconSettings(){readLauncherIconSettings();openSettingsSubpage('icons');}
'''
pat=r"let launcherIconSettings=.*?function openIconSettings\(\)\{.*?\}\n"
t2,n=re.subn(pat,js,t,count=1,flags=re.S)
if n!=1:
    raise SystemExit('Could not replace launcher icon JS block')
p.write_text(t2,encoding='utf-8')

# ---- Java bridge: 4 backgrounds x 2 grid x 3 sizes x 5 text colors ----
j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
s=j.read_text(encoding='utf-8')
bridge=r'''    public class IconBridge {
        private final String PREFS = "btl_launcher_icon";
        private final String[] BACKGROUNDS = {"light", "medium", "dark", "sky"};
        private final String[] TEXT_SIZES = {"small", "normal", "large"};
        private final String[] TEXT_COLORS = {"white", "black", "charcoal", "navy", "yellow"};

        @android.webkit.JavascriptInterface
        public String getIconStyle() {
            android.content.SharedPreferences p = getSharedPreferences(PREFS, MODE_PRIVATE);
            String bg = p.getString("background", "medium");
            boolean grid = p.getBoolean("grid", true);
            String size = p.getString("textSize", "normal");
            String color = p.getString("textColor", "white");
            return "{\"background\":\"" + bg + "\",\"grid\":" + grid + ",\"textSize\":\"" + size + "\",\"textColor\":\"" + color + "\"}";
        }

        @android.webkit.JavascriptInterface
        public void setLauncherIcon(String background, boolean grid, String textSize, String textColor) {
            final String bg = valid(background, BACKGROUNDS, "medium");
            final String size = valid(textSize, TEXT_SIZES, "normal");
            final String color = valid(textColor, TEXT_COLORS, "white");
            final boolean useGrid = grid;
            runOnUiThread(() -> {
                android.content.pm.PackageManager pm = getPackageManager();
                String selected = aliasClass(bg, useGrid, size, color);
                android.content.ComponentName selectedCn = new android.content.ComponentName(getPackageName(), selected);
                pm.setComponentEnabledSetting(selectedCn,
                        android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
                        android.content.pm.PackageManager.DONT_KILL_APP);
                for (String b : BACKGROUNDS) {
                    for (boolean g : new boolean[]{false, true}) {
                        for (String z : TEXT_SIZES) {
                            for (String c : TEXT_COLORS) {
                                String alias = aliasClass(b, g, z, c);
                                if (alias.equals(selected)) continue;
                                android.content.ComponentName cn = new android.content.ComponentName(getPackageName(), alias);
                                pm.setComponentEnabledSetting(cn,
                                        android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                                        android.content.pm.PackageManager.DONT_KILL_APP);
                            }
                        }
                    }
                }
                getSharedPreferences(PREFS, MODE_PRIVATE).edit()
                        .putString("background", bg)
                        .putBoolean("grid", useGrid)
                        .putString("textSize", size)
                        .putString("textColor", color)
                        .apply();
            });
        }

        private String aliasClass(String bg, boolean grid, String size, String color) {
            return "com.militzerjoseph.manyot.Icon_" + bg + "_" + (grid ? "grid" : "plain") + "_" + size + "_" + color + "_v6";
        }

        private String valid(String v, String[] allowed, String fallback) {
            if (v != null) for (String a : allowed) if (a.equals(v)) return v;
            return fallback;
        }
    }
'''
pat=r'    public class IconBridge \{.*?\n    \}\n'
s2,n=re.subn(pat,bridge,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit('Could not replace IconBridge')
j.write_text(s2,encoding='utf-8')

# ---- Manifest: replace all aliases ----
manifest=root/'app/src/main/AndroidManifest.xml'
ET.register_namespace('android','http://schemas.android.com/apk/res/android')
ns='{http://schemas.android.com/apk/res/android}'
tree=ET.parse(manifest)
app=tree.getroot().find('application')
if app is None: raise SystemExit('No application')
for alias in list(app.findall('activity-alias')):
    if alias.get(ns+'name','').startswith('com.militzerjoseph.manyot.Icon_'):
        app.remove(alias)
app.set(ns+'icon','@drawable/ic_btl_medium_grid_normal_white')
if ns+'roundIcon' in app.attrib:
    app.set(ns+'roundIcon','@drawable/ic_btl_medium_grid_normal_white')

bgs=['light','medium','dark','sky']
sizes=['small','normal','large']
colors=['white','black','charcoal','navy','yellow']
for bg in bgs:
    for grid in [False,True]:
        for size in sizes:
            for color in colors:
                mode='grid' if grid else 'plain'
                alias=ET.SubElement(app,'activity-alias')
                alias_name=f'com.militzerjoseph.manyot.Icon_{bg}_{mode}_{size}_{color}_v6'
                alias.set(ns+'name',alias_name)
                alias.set(ns+'targetActivity','com.militzerjoseph.manyot.MainActivity')
                alias.set(ns+'exported','true')
                default=(bg=='medium' and grid and size=='normal' and color=='white')
                alias.set(ns+'enabled','true' if default else 'false')
                alias.set(ns+'icon',f'@drawable/ic_btl_{bg}_{mode}_{size}_{color}')
                alias.set(ns+'label','@string/app_name')
                filt=ET.SubElement(alias,'intent-filter')
                action=ET.SubElement(filt,'action'); action.set(ns+'name','android.intent.action.MAIN')
                cat=ET.SubElement(filt,'category'); cat.set(ns+'name','android.intent.category.LAUNCHER')
tree.write(manifest,encoding='utf-8',xml_declaration=True)

# ---- Generate 120 icon variants ----
icon_dir=root/'app/src/main/res/drawable-nodpi'
for old in icon_dir.glob('ic_btl_*.png'):
    old.unlink()
S=1024
font_candidates=[
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf',
]
font_path=next((f for f in font_candidates if Path(f).exists()),None)
if not font_path: raise SystemExit('Bold Hebrew-capable font not found')
backgrounds={
    'light':(181,187,195),
    'medium':(148,154,163),
    'dark':(111,118,128),
    'sky':(169,212,232),
}
font_sizes={'small':180,'normal':210,'large':240}
text_colors={
    'white':(250,250,250,255),
    'black':(20,20,20,255),
    'charcoal':(52,58,64,255),
    'navy':(23,54,93,255),
    'yellow':(255,216,77,255),
}
label_text='ב.לאומי'
TEXT_CENTER_Y=656

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
                tx=S//2-tw//2; ty=TEXT_CENTER_Y-th//2
                shadow=Image.new('RGBA',(S,S),(0,0,0,0))
                sd=ImageDraw.Draw(shadow)
                # light shadow for dark text, dark shadow for light/yellow text
                shadow_fill=(255,255,255,95) if color_name in ('black','charcoal','navy') else (0,0,0,100)
                kw={'font':font,'fill':shadow_fill}
                if direction: kw['direction']=direction
                sd.text((tx+4,ty+6),draw_text,**kw)
                shadow=shadow.filter(ImageFilter.GaussianBlur(4))
                im=Image.alpha_composite(im,shadow)
                d=ImageDraw.Draw(im)
                kw={'font':font,'fill':text_rgba}
                if direction: kw['direction']=direction
                d.text((tx,ty),draw_text,**kw)
                mode='grid' if use_grid else 'plain'
                im.save(icon_dir/f'ic_btl_{bg_name}_{mode}_{size_name}_{color_name}.png',optimize=True)

print('BTL V6 generated',len(list(icon_dir.glob('ic_btl_*.png'))),'icons')
