from pathlib import Path
import re, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter

root=Path('hadashot-build/manyot_android_v1')

# ----- Android/app version -----
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 6',s)
s=re.sub(r"versionName\s+'[^']+'","versionName '6.0'",s)
g.write_text(s,encoding='utf-8')

# ----- HTML settings UI -----
p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>מניות - גרסה \d+</title>','<title>מניות - גרסה 9</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='9';",t)

css=r'''
/* Manyot V9 launcher icon designer */
.newicon-preview-wrap{display:flex;justify-content:center;margin:8px 0 18px}
.newicon-preview{width:156px;height:156px;border-radius:34px;overflow:hidden;position:relative;box-shadow:0 5px 15px #0003;border:1px solid #0002}
.newicon-top{position:absolute;left:0;right:0;top:0;height:31%;background:#e00000}
.newicon-body{position:absolute;left:0;right:0;top:31%;bottom:0;background:#17191c}
.newicon-text{position:absolute;left:7px;right:7px;top:52%;transform:translateY(-5%);text-align:center;direction:rtl;color:#fff;line-height:1;white-space:nowrap;text-shadow:0 2px 4px #0007}
.newicon-text.small{font-size:27px}.newicon-text.normal{font-size:32px}.newicon-text.large{font-size:37px}
.newicon-text.bold{font-weight:800}.newicon-text.mediumw{font-weight:600}
.icon-choice-row.five{grid-template-columns:repeat(5,minmax(0,1fr))}
.icon-choice-row.four{grid-template-columns:repeat(4,minmax(0,1fr))}
.icon-choice-row.three{grid-template-columns:repeat(3,minmax(0,1fr))}
@media(max-width:420px){.icon-choice-row.five,.icon-choice-row.four{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''
if 'Manyot V9 launcher icon designer' not in t:
    t=t.replace('</style>',css+'\n</style>',1)

js=r'''let launcherIconSettings={bodyColor:'black',topColor:'red',textColor:'white',textSize:'normal',fontWeight:'bold'};
function readLauncherIconSettings(){
  try{
    if(window.AndroidIcon&&AndroidIcon.getIconStyle){
      const obj=JSON.parse(String(AndroidIcon.getIconStyle()||'{}'));
      if(['black','charcoal','navy'].includes(obj.bodyColor))launcherIconSettings.bodyColor=obj.bodyColor;
      if(['red','burgundy','blue','green'].includes(obj.topColor))launcherIconSettings.topColor=obj.topColor;
      if(['white','black','yellow','navy','sky'].includes(obj.textColor))launcherIconSettings.textColor=obj.textColor;
      if(['small','normal','large'].includes(obj.textSize))launcherIconSettings.textSize=obj.textSize;
      if(['bold','mediumw'].includes(obj.fontWeight))launcherIconSettings.fontWeight=obj.fontWeight;
    }
  }catch(e){}
  return launcherIconSettings;
}
function iconColorValue(kind,v){
  const map={
    body:{black:'#17191c',charcoal:'#3b3f45',navy:'#18283e'},
    top:{red:'#e00000',burgundy:'#8f1730',blue:'#175bb8',green:'#21884f'},
    text:{white:'#ffffff',black:'#111111',yellow:'#ffd84d',navy:'#17365d',sky:'#8fd3ff'}
  };
  return map[kind]?.[v]||'#000';
}
function iconSettingsHtml(){
  const x=readLauncherIconSettings();
  return `<h2>אייקון האפליקציה</h2>
    <div class="newicon-preview-wrap"><div class="newicon-preview">
      <div class="newicon-top" style="background:${iconColorValue('top',x.topColor)}"></div>
      <div class="newicon-body" style="background:${iconColorValue('body',x.bodyColor)}"></div>
      <div class="newicon-text ${x.textSize} ${x.fontWeight}" style="color:${iconColorValue('text',x.textColor)}">מניות</div>
    </div></div>

    <div class="icon-choice-group"><div class="icon-choice-title">צבע החלק הכהה</div><div class="icon-choice-row three">
      <button class="icon-choice ${x.bodyColor==='black'?'on':''}" onclick="setLauncherIconBody('black')">שחור</button>
      <button class="icon-choice ${x.bodyColor==='charcoal'?'on':''}" onclick="setLauncherIconBody('charcoal')">אפור כהה</button>
      <button class="icon-choice ${x.bodyColor==='navy'?'on':''}" onclick="setLauncherIconBody('navy')">כחול כהה</button>
    </div></div>

    <div class="icon-choice-group"><div class="icon-choice-title">צבע הפס העליון</div><div class="icon-choice-row four">
      <button class="icon-choice ${x.topColor==='red'?'on':''}" onclick="setLauncherIconTop('red')">אדום</button>
      <button class="icon-choice ${x.topColor==='burgundy'?'on':''}" onclick="setLauncherIconTop('burgundy')">בורדו</button>
      <button class="icon-choice ${x.topColor==='blue'?'on':''}" onclick="setLauncherIconTop('blue')">כחול</button>
      <button class="icon-choice ${x.topColor==='green'?'on':''}" onclick="setLauncherIconTop('green')">ירוק</button>
    </div></div>

    <div class="icon-choice-group"><div class="icon-choice-title">צבע הכיתוב</div><div class="icon-choice-row five">
      <button class="icon-choice ${x.textColor==='white'?'on':''}" onclick="setLauncherIconTextColor('white')">לבן</button>
      <button class="icon-choice ${x.textColor==='black'?'on':''}" onclick="setLauncherIconTextColor('black')">שחור</button>
      <button class="icon-choice ${x.textColor==='yellow'?'on':''}" onclick="setLauncherIconTextColor('yellow')">צהוב</button>
      <button class="icon-choice ${x.textColor==='navy'?'on':''}" onclick="setLauncherIconTextColor('navy')">כחול כהה</button>
      <button class="icon-choice ${x.textColor==='sky'?'on':''}" onclick="setLauncherIconTextColor('sky')">תכלת</button>
    </div></div>

    <div class="icon-choice-group"><div class="icon-choice-title">גודל הכיתוב</div><div class="icon-choice-row three">
      <button class="icon-choice ${x.textSize==='small'?'on':''}" onclick="setLauncherIconTextSize('small')">קטן</button>
      <button class="icon-choice ${x.textSize==='normal'?'on':''}" onclick="setLauncherIconTextSize('normal')">בינוני</button>
      <button class="icon-choice ${x.textSize==='large'?'on':''}" onclick="setLauncherIconTextSize('large')">גדול</button>
    </div></div>

    <div class="icon-choice-group"><div class="icon-choice-title">עובי הכיתוב</div><div class="icon-choice-row two">
      <button class="icon-choice ${x.fontWeight==='bold'?'on':''}" onclick="setLauncherIconWeight('bold')">כמו בדוגמה</button>
      <button class="icon-choice ${x.fontWeight==='mediumw'?'on':''}" onclick="setLauncherIconWeight('mediumw')">פחות עבה</button>
    </div></div>

    <div class="icon-note">ברירת המחדל: שחור + אדום + כיתוב לבן, גודל בינוני, עובי כמו בדוגמה.</div>
    <button class="reset-design" onclick="resetLauncherIcon()">החזר אייקון לברירת המחדל</button>
    <button class="close" onclick="backToSettings()">חזרה להגדרות</button>`;
}
function applyLauncherIconSettings(){
  try{
    if(window.AndroidIcon&&AndroidIcon.setLauncherIcon){
      AndroidIcon.setLauncherIcon(launcherIconSettings.bodyColor,launcherIconSettings.topColor,launcherIconSettings.textColor,launcherIconSettings.textSize,launcherIconSettings.fontWeight);
      toast('האייקון עודכן');
    }else toast('שינוי האייקון זמין בגרסת APK');
  }catch(e){toast('לא ניתן לעדכן את האייקון');}
  replaceOverlayHtml(iconSettingsHtml());
}
function setLauncherIconBody(v){if(!['black','charcoal','navy'].includes(v))return;launcherIconSettings.bodyColor=v;applyLauncherIconSettings();}
function setLauncherIconTop(v){if(!['red','burgundy','blue','green'].includes(v))return;launcherIconSettings.topColor=v;applyLauncherIconSettings();}
function setLauncherIconTextColor(v){if(!['white','black','yellow','navy','sky'].includes(v))return;launcherIconSettings.textColor=v;applyLauncherIconSettings();}
function setLauncherIconTextSize(v){if(!['small','normal','large'].includes(v))return;launcherIconSettings.textSize=v;applyLauncherIconSettings();}
function setLauncherIconWeight(v){if(!['bold','mediumw'].includes(v))return;launcherIconSettings.fontWeight=v;applyLauncherIconSettings();}
function resetLauncherIcon(){launcherIconSettings={bodyColor:'black',topColor:'red',textColor:'white',textSize:'normal',fontWeight:'bold'};applyLauncherIconSettings();}
function openIconSettings(){readLauncherIconSettings();openSettingsSubpage('icons');}
'''
pat=r"let launcherIconSettings=.*?function openIconSettings\(\)\{.*?\}\n"
t2,n=re.subn(pat,js,t,count=1,flags=re.S)
if n!=1:
    raise SystemExit('Could not replace launcher icon JS block for V9')
p.write_text(t2,encoding='utf-8')

# ----- Java bridge -----
j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
s=j.read_text(encoding='utf-8')
bridge=r'''    public class IconBridge {
        private final String PREFS = "manyot_launcher_icon_v9";
        private final String[] BODY_COLORS = {"black", "charcoal", "navy"};
        private final String[] TOP_COLORS = {"red", "burgundy", "blue", "green"};
        private final String[] TEXT_COLORS = {"white", "black", "yellow", "navy", "sky"};
        private final String[] TEXT_SIZES = {"small", "normal", "large"};
        private final String[] FONT_WEIGHTS = {"bold", "mediumw"};

        @android.webkit.JavascriptInterface
        public String getIconStyle() {
            android.content.SharedPreferences p = getSharedPreferences(PREFS, MODE_PRIVATE);
            String body = p.getString("bodyColor", "black");
            String top = p.getString("topColor", "red");
            String text = p.getString("textColor", "white");
            String size = p.getString("textSize", "normal");
            String weight = p.getString("fontWeight", "bold");
            return "{\"bodyColor\":\"" + body + "\",\"topColor\":\"" + top + "\",\"textColor\":\"" + text + "\",\"textSize\":\"" + size + "\",\"fontWeight\":\"" + weight + "\"}";
        }

        @android.webkit.JavascriptInterface
        public void setLauncherIcon(String bodyColor, String topColor, String textColor, String textSize, String fontWeight) {
            final String body = valid(bodyColor, BODY_COLORS, "black");
            final String top = valid(topColor, TOP_COLORS, "red");
            final String text = valid(textColor, TEXT_COLORS, "white");
            final String size = valid(textSize, TEXT_SIZES, "normal");
            final String weight = valid(fontWeight, FONT_WEIGHTS, "bold");
            runOnUiThread(() -> {
                android.content.pm.PackageManager pm = getPackageManager();
                String selected = aliasClass(body, top, text, size, weight);
                android.content.ComponentName selectedCn = new android.content.ComponentName(getPackageName(), selected);
                pm.setComponentEnabledSetting(selectedCn,
                        android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
                        android.content.pm.PackageManager.DONT_KILL_APP);
                for (String b : BODY_COLORS) {
                    for (String tp : TOP_COLORS) {
                        for (String tx : TEXT_COLORS) {
                            for (String sz : TEXT_SIZES) {
                                for (String wt : FONT_WEIGHTS) {
                                    String alias = aliasClass(b, tp, tx, sz, wt);
                                    if (alias.equals(selected)) continue;
                                    android.content.ComponentName cn = new android.content.ComponentName(getPackageName(), alias);
                                    pm.setComponentEnabledSetting(cn,
                                            android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED,
                                            android.content.pm.PackageManager.DONT_KILL_APP);
                                }
                            }
                        }
                    }
                }
                getSharedPreferences(PREFS, MODE_PRIVATE).edit()
                        .putString("bodyColor", body)
                        .putString("topColor", top)
                        .putString("textColor", text)
                        .putString("textSize", size)
                        .putString("fontWeight", weight)
                        .apply();
            });
        }

        private String aliasClass(String body, String top, String text, String size, String weight) {
            return "com.militzerjoseph.manyot.Icon_" + body + "_" + top + "_" + text + "_" + size + "_" + weight + "_v9";
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
    raise SystemExit('Could not replace IconBridge for V9')
j.write_text(s2,encoding='utf-8')

# ----- Manifest aliases -----
manifest=root/'app/src/main/AndroidManifest.xml'
ET.register_namespace('android','http://schemas.android.com/apk/res/android')
ns='{http://schemas.android.com/apk/res/android}'
tree=ET.parse(manifest)
app=tree.getroot().find('application')
if app is None: raise SystemExit('No application')
for alias in list(app.findall('activity-alias')):
    if alias.get(ns+'name','').startswith('com.militzerjoseph.manyot.Icon_'):
        app.remove(alias)

body_colors=['black','charcoal','navy']
top_colors=['red','burgundy','blue','green']
text_colors=['white','black','yellow','navy','sky']
sizes=['small','normal','large']
weights=['bold','mediumw']

def drawable_name(body,top,text,size,weight):
    return f'ic_manyot_{body}_{top}_{text}_{size}_{weight}'

def alias_name(body,top,text,size,weight):
    return f'com.militzerjoseph.manyot.Icon_{body}_{top}_{text}_{size}_{weight}_v9'

default_draw=drawable_name('black','red','white','normal','bold')
app.set(ns+'icon','@drawable/'+default_draw)
if ns+'roundIcon' in app.attrib:
    app.set(ns+'roundIcon','@drawable/'+default_draw)

for body in body_colors:
    for top in top_colors:
        for text in text_colors:
            for size in sizes:
                for weight in weights:
                    alias=ET.SubElement(app,'activity-alias')
                    an=alias_name(body,top,text,size,weight)
                    alias.set(ns+'name',an)
                    alias.set(ns+'targetActivity','com.militzerjoseph.manyot.MainActivity')
                    alias.set(ns+'exported','true')
                    default=(body=='black' and top=='red' and text=='white' and size=='normal' and weight=='bold')
                    alias.set(ns+'enabled','true' if default else 'false')
                    alias.set(ns+'icon','@drawable/'+drawable_name(body,top,text,size,weight))
                    alias.set(ns+'label','@string/app_name')
                    filt=ET.SubElement(alias,'intent-filter')
                    action=ET.SubElement(filt,'action'); action.set(ns+'name','android.intent.action.MAIN')
                    cat=ET.SubElement(filt,'category'); cat.set(ns+'name','android.intent.category.LAUNCHER')
tree.write(manifest,encoding='utf-8',xml_declaration=True)

# ----- Generate launcher icon variants -----
icon_dir=root/'app/src/main/res/drawable-nodpi'
for old in icon_dir.glob('ic_manyot_*.png'):
    old.unlink()

S=1024
body_rgb={
    'black':(22,24,27),
    'charcoal':(58,63,70),
    'navy':(24,40,62),
}
top_rgb={
    'red':(225,0,0),
    'burgundy':(143,23,48),
    'blue':(23,91,184),
    'green':(33,136,79),
}
text_rgba={
    'white':(250,250,250,255),
    'black':(17,17,17,255),
    'yellow':(255,216,77,255),
    'navy':(23,54,93,255),
    'sky':(143,211,255,255),
}
font_sizes={'small':210,'normal':240,'large':270}
font_files={
    'bold':'/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    'mediumw':'/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
}
for f in font_files.values():
    if not Path(f).exists(): raise SystemExit('Hebrew-capable font not found: '+f)

label='מניות'
TOP_SPLIT=330
TEXT_CENTER_Y=620

for body_name,body in body_rgb.items():
    for top_name,top in top_rgb.items():
        for text_name,fill in text_rgba.items():
            for size_name,fs in font_sizes.items():
                for weight_name,font_file in font_files.items():
                    im=Image.new('RGBA',(S,S),(0,0,0,0))
                    mask=Image.new('L',(S,S),0)
                    md=ImageDraw.Draw(mask)
                    md.rounded_rectangle((42,42,S-42,S-42),radius=190,fill=255)

                    # soft drop shadow around the icon
                    shadow=Image.new('RGBA',(S,S),(0,0,0,0))
                    sm=mask.filter(ImageFilter.GaussianBlur(20))
                    shadow.putalpha(sm.point(lambda a:int(a*0.22)))
                    black=Image.new('RGBA',(S,S),(0,0,0,255))
                    black.putalpha(shadow.getchannel('A'))
                    im.alpha_composite(black,(8,14))

                    art=Image.new('RGBA',(S,S),(0,0,0,0))
                    ad=ImageDraw.Draw(art)
                    ad.rectangle((42,42,S-42,TOP_SPLIT),fill=(*top,255))
                    ad.rectangle((42,TOP_SPLIT,S-42,S-42),fill=(*body,255))

                    # subtle vertical gradients for glossy look
                    overlay=Image.new('RGBA',(S,S),(0,0,0,0))
                    od=ImageDraw.Draw(overlay)
                    for y in range(42,S-42):
                        if y<TOP_SPLIT:
                            rel=(y-42)/(TOP_SPLIT-42)
                            a=int(80*(1-rel))
                            od.line((42,y,S-42,y),fill=(255,255,255,a))
                        else:
                            rel=(y-TOP_SPLIT)/((S-42)-TOP_SPLIT)
                            a=int(45*rel)
                            od.line((42,y,S-42,y),fill=(0,0,0,a))
                    art=Image.alpha_composite(art,overlay)

                    # top gloss band
                    gloss=Image.new('RGBA',(S,S),(0,0,0,0))
                    gd=ImageDraw.Draw(gloss)
                    gd.rounded_rectangle((78,70,S-78,215),radius=100,fill=(255,255,255,62))
                    gloss=gloss.filter(ImageFilter.GaussianBlur(12))
                    art=Image.alpha_composite(art,gloss)

                    # boundary highlight and outer border
                    ad=ImageDraw.Draw(art)
                    ad.line((42,TOP_SPLIT,S-42,TOP_SPLIT),fill=(255,255,255,55),width=3)
                    ad.rounded_rectangle((42,42,S-42,S-42),radius=190,outline=(255,255,255,90),width=5)
                    im.paste(art,(0,0),mask)

                    font=ImageFont.truetype(font_file,fs)
                    probe=ImageDraw.Draw(Image.new('RGBA',(1,1)))
                    bbox=probe.textbbox((0,0),label,font=font,direction='rtl')
                    tw=bbox[2]-bbox[0]; th=bbox[3]-bbox[1]
                    maxw=780
                    layer=Image.new('RGBA',(tw+50,th+50),(0,0,0,0))
                    ld=ImageDraw.Draw(layer)
                    ld.text((25-bbox[0],25-bbox[1]),label,font=font,fill=fill,direction='rtl')
                    if layer.width>maxw:
                        ratio=maxw/layer.width
                        layer=layer.resize((maxw,int(layer.height*ratio)),Image.Resampling.LANCZOS)
                    tx=(S-layer.width)//2
                    ty=int(TEXT_CENTER_Y-layer.height/2)
                    alpha=layer.getchannel('A')
                    sh=Image.new('RGBA',layer.size,(0,0,0,0))
                    sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(5)).point(lambda a:int(a*0.35)))
                    im.alpha_composite(sh,(tx+5,ty+7))
                    im.alpha_composite(layer,(tx,ty))

                    im.save(icon_dir/(drawable_name(body_name,top_name,text_name,size_name,weight_name)+'.png'),optimize=True)

print('Manyot V9 ready: 360 red/dark-style icon variants; default black+red+white+normal+bold')
