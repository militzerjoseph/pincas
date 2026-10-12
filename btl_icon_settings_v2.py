from pathlib import Path
import re, xml.etree.ElementTree as ET

root=Path('btl-build/manyot_android_v1')

# ---- version / launcher label ----
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 2',s)
s=re.sub(r"versionName\s+'[^']+'","versionName '2.0'",s)
g.write_text(s,encoding='utf-8')

strings=root/'app/src/main/res/values/strings.xml'
st=strings.read_text(encoding='utf-8')
st=re.sub(r'(<string\s+name="app_name"[^>]*>).*?(</string>)',r'\1ב. לאומי\2',st,flags=re.S)
strings.write_text(st,encoding='utf-8')

# ---- HTML settings UI ----
p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>ביטוח לאומי - גרסה \d+</title>','<title>ביטוח לאומי - גרסה 2</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='2';",t)

css=r'''
/* ===== התאמת אייקון האפליקציה ===== */
.icon-settings-preview-wrap{display:flex;justify-content:center;margin:12px 0 18px}
.icon-settings-preview{width:126px;height:126px;border-radius:27px;position:relative;overflow:hidden;box-shadow:0 3px 10px rgba(0,0,0,.18);display:flex;align-items:flex-end;justify-content:center;padding-bottom:20px;color:#fff}
.icon-settings-preview.grid{background-image:linear-gradient(rgba(255,255,255,.58) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.58) 1px,transparent 1px);background-size:25px 25px}
.icon-settings-preview.light{background-color:#b5bbc3}.icon-settings-preview.medium{background-color:#949aa3}.icon-settings-preview.dark{background-color:#6f7680}
.icon-preview-text{font-weight:400;text-shadow:0 2px 3px rgba(0,0,0,.25);direction:rtl;white-space:nowrap}
.icon-preview-text.small{font-size:20px}.icon-preview-text.normal{font-size:24px}.icon-preview-text.large{font-size:28px}
.icon-choice-group{margin:15px 0}.icon-choice-title{font-size:17px;font-weight:650;margin-bottom:8px}
.icon-choice-row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.icon-choice-row.two{grid-template-columns:repeat(2,1fr)}
.icon-choice{border:1px solid #c9c9c9;border-radius:13px;background:#f7f7f7;padding:11px 6px;font-size:16px}
.icon-choice.on{border:2px solid #526b8d;background:#eef4fb;font-weight:650}
.icon-note{font-size:14px;color:#555;line-height:1.5;margin:12px 0}
'''
if '/* ===== התאמת אייקון האפליקציה ===== */' not in t:
    t=t.replace('</style>',css+'\n</style>',1)

needle='<button class="setting-nav-row" onclick="openColorSettings()"><span>צבעים</span><span class="setting-nav-arrow">‹</span></button>'
add=needle+'\n      <button class="setting-nav-row" onclick="openIconSettings()"><span>אייקון האפליקציה</span><span class="setting-nav-arrow">‹</span></button>'
if needle in t and 'onclick="openIconSettings()"' not in t:
    t=t.replace(needle,add,1)

manual='<li><b>אייקון האפליקציה</b>בהגדרות ניתן לבחור גוון רקע, עם או בלי קווי רשת, וגודל כיתוב. השינוי משפיע על האייקון במסך הבית.</li>'
if manual not in t:
    t=t.replace('<li><b>צבעים</b>אפשר לבחור שילוב מוכן או צבע נפרד לרקע העליון, לכיתוב העליון, לרקע המסך ולכרטיסי הקישורים.</li>',
                '<li><b>צבעים</b>אפשר לבחור שילוב מוכן או צבע נפרד לרקע העליון, לכיתוב העליון, לרקע המסך ולכרטיסי הקישורים.</li>\n        '+manual,1)

js=r'''
let launcherIconSettings={background:'medium',grid:true,textSize:'normal'};
function readLauncherIconSettings(){
  try{
    if(window.AndroidIcon&&AndroidIcon.getIconStyle){
      const obj=JSON.parse(String(AndroidIcon.getIconStyle()||'{}'));
      if(['light','medium','dark'].includes(obj.background))launcherIconSettings.background=obj.background;
      if(typeof obj.grid==='boolean')launcherIconSettings.grid=obj.grid;
      if(['small','normal','large'].includes(obj.textSize))launcherIconSettings.textSize=obj.textSize;
    }
  }catch(e){}
  return launcherIconSettings;
}
function iconSettingsHtml(){
  const x=readLauncherIconSettings();
  const gridClass=x.grid?' grid':'';
  return `<h2>אייקון האפליקציה</h2>
    <div class="icon-settings-preview-wrap"><div class="icon-settings-preview ${x.background}${gridClass}"><span class="icon-preview-text ${x.textSize}">ב.לאומי</span></div></div>
    <div class="icon-choice-group"><div class="icon-choice-title">צבע הרקע</div><div class="icon-choice-row">
      <button class="icon-choice ${x.background==='light'?'on':''}" onclick="setLauncherIconBackground('light')">אפור בהיר</button>
      <button class="icon-choice ${x.background==='medium'?'on':''}" onclick="setLauncherIconBackground('medium')">אפור בינוני</button>
      <button class="icon-choice ${x.background==='dark'?'on':''}" onclick="setLauncherIconBackground('dark')">אפור כהה</button>
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
    <div class="icon-note">ברירת המחדל: אפור בינוני, עם קווי רשת וכיתוב רגיל. שם האפליקציה מתחת לאייקון נשאר „ב. לאומי”.</div>
    <button class="reset-design" onclick="resetLauncherIcon()">החזר אייקון לברירת המחדל</button>
    <button class="close" onclick="backToSettings()">חזרה להגדרות</button>`;
}
function applyLauncherIconSettings(){
  try{
    if(window.AndroidIcon&&AndroidIcon.setLauncherIcon){
      AndroidIcon.setLauncherIcon(launcherIconSettings.background,!!launcherIconSettings.grid,launcherIconSettings.textSize);
      toast('האייקון עודכן');
    }else toast('שינוי האייקון זמין בגרסת APK');
  }catch(e){toast('לא ניתן לעדכן את האייקון');}
  replaceOverlayHtml(iconSettingsHtml());
}
function setLauncherIconBackground(v){if(!['light','medium','dark'].includes(v))return;launcherIconSettings.background=v;applyLauncherIconSettings();}
function setLauncherIconGrid(v){launcherIconSettings.grid=!!v;applyLauncherIconSettings();}
function setLauncherIconTextSize(v){if(!['small','normal','large'].includes(v))return;launcherIconSettings.textSize=v;applyLauncherIconSettings();}
function resetLauncherIcon(){launcherIconSettings={background:'medium',grid:true,textSize:'normal'};applyLauncherIconSettings();}
function openIconSettings(){readLauncherIconSettings();openSettingsSubpage('icons');}
'''
if 'function iconSettingsHtml()' not in t:
    t=t.replace('function openSettings(){openOverlayHtml(settingsHtml(),{view:\'settings-main\'},\'#settings\');}',js+'\nfunction openSettings(){openOverlayHtml(settingsHtml(),{view:\'settings-main\'},\'#settings\');}',1)

old="""function openSettingsSubpage(page){
  const valid=page==='colors'?'colors':'typography';
  history.pushState({view:'settings-sub',page:valid},'',valid==='colors'?'#settings-colors':'#settings-typography');
  replaceOverlayHtml(valid==='colors'?colorSettingsHtml():typographySettingsHtml());
  scrollTo(0,0);
}"""
new="""function openSettingsSubpage(page){
  const valid=['colors','typography','icons'].includes(page)?page:'typography';
  const hash=valid==='colors'?'#settings-colors':valid==='icons'?'#settings-icons':'#settings-typography';
  history.pushState({view:'settings-sub',page:valid},'',hash);
  replaceOverlayHtml(valid==='colors'?colorSettingsHtml():valid==='icons'?iconSettingsHtml():typographySettingsHtml());
  scrollTo(0,0);
}"""
if old in t: t=t.replace(old,new,1)
else:
    t=re.sub(r"function openSettingsSubpage\(page\)\{.*?\n\}",new,t,count=1,flags=re.S)

oldpop="replaceOverlayHtml(state.page==='colors'?colorSettingsHtml():typographySettingsHtml());"
if oldpop in t:
    t=t.replace(oldpop,"replaceOverlayHtml(state.page==='colors'?colorSettingsHtml():state.page==='icons'?iconSettingsHtml():typographySettingsHtml());",1)

p.write_text(t,encoding='utf-8')

# ---- Android Java bridge ----
j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
s=j.read_text(encoding='utf-8')
if '"AndroidIcon"' not in s:
    m=re.search(r'(?P<var>\w+)\.addJavascriptInterface\([^;\n]*"AndroidApps"\s*\);',s)
    if not m:
        raise SystemExit('Could not find AndroidApps javascript bridge registration')
    var=m.group('var')
    insert=m.group(0)+f'\n        {var}.addJavascriptInterface(new IconBridge(), "AndroidIcon");'
    s=s[:m.start()]+insert+s[m.end():]

bridge=r'''

    public class IconBridge {
        private final String PREFS = "btl_launcher_icon";
        private final String[] BACKGROUNDS = {"light", "medium", "dark"};
        private final String[] TEXT_SIZES = {"small", "normal", "large"};

        @android.webkit.JavascriptInterface
        public String getIconStyle() {
            android.content.SharedPreferences p = getSharedPreferences(PREFS, MODE_PRIVATE);
            String bg = p.getString("background", "medium");
            boolean grid = p.getBoolean("grid", true);
            String size = p.getString("textSize", "normal");
            return "{\"background\":\"" + bg + "\",\"grid\":" + grid + ",\"textSize\":\"" + size + "\"}";
        }

        @android.webkit.JavascriptInterface
        public void setLauncherIcon(String background, boolean grid, String textSize) {
            final String bg = valid(background, BACKGROUNDS, "medium");
            final String size = valid(textSize, TEXT_SIZES, "normal");
            final boolean useGrid = grid;
            runOnUiThread(() -> {
                android.content.pm.PackageManager pm = getPackageManager();
                String selected = aliasClass(bg, useGrid, size);
                for (String b : BACKGROUNDS) {
                    for (boolean g : new boolean[]{false, true}) {
                        for (String z : TEXT_SIZES) {
                            String alias = aliasClass(b, g, z);
                            android.content.ComponentName cn = new android.content.ComponentName(getPackageName(), alias);
                            int state = alias.equals(selected)
                                    ? android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_ENABLED
                                    : android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED;
                            pm.setComponentEnabledSetting(cn, state, android.content.pm.PackageManager.DONT_KILL_APP);
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
            return "com.militzerjoseph.manyot.Icon_" + bg + "_" + (grid ? "grid" : "plain") + "_" + size;
        }

        private String valid(String v, String[] allowed, String fallback) {
            if (v != null) for (String a : allowed) if (a.equals(v)) return v;
            return fallback;
        }
    }
'''
if 'public class IconBridge' not in s:
    pos=s.rfind('}')
    if pos<0: raise SystemExit('Could not locate final MainActivity brace')
    s=s[:pos]+bridge+'\n'+s[pos:]
j.write_text(s,encoding='utf-8')

# ---- AndroidManifest aliases ----
manifest=root/'app/src/main/AndroidManifest.xml'
ET.register_namespace('android','http://schemas.android.com/apk/res/android')
ns='{http://schemas.android.com/apk/res/android}'
tree=ET.parse(manifest)
mr=tree.getroot(); app=mr.find('application')
if app is None: raise SystemExit('No application in manifest')
activities=app.findall('activity')
target=None
for a in activities:
    n=a.get(ns+'name','')
    if n.endswith('MainActivity'):
        target=a; break
if target is None: raise SystemExit('MainActivity not found in manifest')
# remove launcher filter from target activity
for f in list(target.findall('intent-filter')):
    is_launcher=False
    for ac in f.findall('action'):
        if ac.get(ns+'name')=='android.intent.action.MAIN': is_launcher=True
    for cat in f.findall('category'):
        if cat.get(ns+'name')=='android.intent.category.LAUNCHER': is_launcher=True
    if is_launcher: target.remove(f)
# remove stale icon aliases, if any
for alias in list(app.findall('activity-alias')):
    if alias.get(ns+'name','').startswith('com.militzerjoseph.manyot.Icon_'):
        app.remove(alias)
# application icon follows default
app.set(ns+'icon','@drawable/ic_btl_medium_grid_normal')
if ns+'roundIcon' in app.attrib:
    app.set(ns+'roundIcon','@drawable/ic_btl_medium_grid_normal')

bgs=['light','medium','dark']; sizes=['small','normal','large']
for bg in bgs:
    for grid in [False,True]:
        for size in sizes:
            mode='grid' if grid else 'plain'
            alias=ET.SubElement(app,'activity-alias')
            alias_name=f'com.militzerjoseph.manyot.Icon_{bg}_{mode}_{size}'
            alias.set(ns+'name',alias_name)
            alias.set(ns+'targetActivity','com.militzerjoseph.manyot.MainActivity')
            alias.set(ns+'exported','true')
            alias.set(ns+'enabled','true' if (bg=='medium' and grid and size=='normal') else 'false')
            alias.set(ns+'icon',f'@drawable/ic_btl_{bg}_{mode}_{size}')
            alias.set(ns+'label','@string/app_name')
            filt=ET.SubElement(alias,'intent-filter')
            action=ET.SubElement(filt,'action'); action.set(ns+'name','android.intent.action.MAIN')
            cat=ET.SubElement(filt,'category'); cat.set(ns+'name','android.intent.category.LAUNCHER')

tree.write(manifest,encoding='utf-8',xml_declaration=True)

# ---- Generate the 18 launcher icon variants ----
from PIL import Image, ImageDraw, ImageFont, ImageFilter
icon_dir=root/'app/src/main/res/drawable-nodpi'
icon_dir.mkdir(parents=True,exist_ok=True)
S=1024
font_candidates=[
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
]
font_path=next((f for f in font_candidates if Path(f).exists()),None)
if not font_path: raise SystemExit('Hebrew-capable font not found')
colors={'light':(181,187,195),'medium':(148,154,163),'dark':(111,118,128)}
font_sizes={'small':112,'normal':136,'large':160}
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
            tx=S//2-tw//2; ty=790-th//2
            shadow=Image.new('RGBA',(S,S),(0,0,0,0))
            sd=ImageDraw.Draw(shadow)
            kw={'font':font,'fill':(0,0,0,95)}
            if direction: kw['direction']=direction
            sd.text((tx+6,ty+8),draw_text,**kw)
            shadow=shadow.filter(ImageFilter.GaussianBlur(5))
            im=Image.alpha_composite(im,shadow)
            d=ImageDraw.Draw(im)
            kw={'font':font,'fill':(250,250,250,255)}
            if direction: kw['direction']=direction
            d.text((tx,ty),draw_text,**kw)
            mode='grid' if use_grid else 'plain'
            im.save(icon_dir/f'ic_btl_{bg_name}_{mode}_{size_name}.png',optimize=True)
