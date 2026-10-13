from pathlib import Path
import re, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont, ImageFilter

root=Path('hadashot-build/manyot_android_v1')

# Version
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r'versionCode\s+\d+','versionCode 7',s)
s=re.sub(r"versionName\s+'[^']+'","versionName '7.0'",s)
g.write_text(s,encoding='utf-8')

# HTML / settings UI
p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>מניות - גרסה \d+</title>','<title>מניות - גרסה 10</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='10';",t)

css=r'''
/* Manyot V10 launcher icon designer */
.default-icon-banner{margin:8px 0 14px;padding:10px 12px;border-radius:12px;background:#f3f3f3;border:1px solid #d5d5d5;font-size:14px;font-weight:700;text-align:center}
.icon-choice-row.ten{grid-template-columns:repeat(2,minmax(0,1fr))}
.icon-choice-row.six{grid-template-columns:repeat(3,minmax(0,1fr))}
.icon-choice-row.five{grid-template-columns:repeat(5,minmax(0,1fr))}
.icon-choice-row.four{grid-template-columns:repeat(4,minmax(0,1fr))}
.icon-choice-row.three{grid-template-columns:repeat(3,minmax(0,1fr))}
.icon-choice-row.two{grid-template-columns:repeat(2,minmax(0,1fr))}
@media(max-width:420px){.icon-choice-row.five,.icon-choice-row.four,.icon-choice-row.six{grid-template-columns:repeat(2,minmax(0,1fr))}}
'''
if 'Manyot V10 launcher icon designer' not in t:
    t=t.replace('</style>',css+'\n</style>',1)

js=r'''let launcherIconSettings={bodyColor:'black',topEnabled:true,topColor:'red',textColor:'white',textSize:'normal',fontWeight:'bold'};
function readLauncherIconSettings(){
  try{
    if(window.AndroidIcon&&AndroidIcon.getIconStyle){
      const obj=JSON.parse(String(AndroidIcon.getIconStyle()||'{}'));
      if(['black','charcoal','midgray','navy','blue','sky','yellowlight','yellowdeep','beigelight','beigedeep'].includes(obj.bodyColor))launcherIconSettings.bodyColor=obj.bodyColor;
      if(typeof obj.topEnabled==='boolean')launcherIconSettings.topEnabled=obj.topEnabled;
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
    body:{black:'#17191c',charcoal:'#3b3f45',midgray:'#686d74',navy:'#18283e',blue:'#1473e6',sky:'#9fd3ec',yellowlight:'#f6df7a',yellowdeep:'#d7aa28',beigelight:'#ead7b7',beigedeep:'#b99972'},
    top:{red:'#e00000',burgundy:'#8f1730',blue:'#175bb8',green:'#21884f'},
    text:{white:'#ffffff',black:'#111111',yellow:'#ffd84d',navy:'#17365d',sky:'#8fd3ff'}
  };
  return map[kind]?.[v]||'#000';
}
function iconSettingsHtml(){
  const x=readLauncherIconSettings();
  const topH=x.topEnabled?'31%':'0%';
  const bodyTop=x.topEnabled?'31%':'0%';
  return `<h2>אייקון האפליקציה</h2>
    <div class="newicon-preview-wrap"><div class="newicon-preview">
      <div class="newicon-top" style="height:${topH};background:${iconColorValue('top',x.topColor)}"></div>
      <div class="newicon-body" style="top:${bodyTop};background:${iconColorValue('body',x.bodyColor)}"></div>
      <div class="newicon-text ${x.textSize} ${x.fontWeight}" style="color:${iconColorValue('text',x.textColor)};top:${x.topEnabled?'52%':'47%'}">מניות</div>
    </div></div>

    <div class="default-icon-banner">ברירת המחדל: שחור + פס אדום + כיתוב לבן + גודל בינוני + עובי כמו בדוגמה</div>

    <div class="icon-choice-group"><div class="icon-choice-title">צבע הרקע</div><div class="icon-choice-row ten">
      <button class="icon-choice ${x.bodyColor==='black'?'on':''}" onclick="setLauncherIconBody('black')">שחור</button>
      <button class="icon-choice ${x.bodyColor==='charcoal'?'on':''}" onclick="setLauncherIconBody('charcoal')">אפור כהה</button>
      <button class="icon-choice ${x.bodyColor==='midgray'?'on':''}" onclick="setLauncherIconBody('midgray')">אפור פחות כהה</button>
      <button class="icon-choice ${x.bodyColor==='navy'?'on':''}" onclick="setLauncherIconBody('navy')">כחול כהה</button>
      <button class="icon-choice ${x.bodyColor==='blue'?'on':''}" onclick="setLauncherIconBody('blue')">כחול חי</button>
      <button class="icon-choice ${x.bodyColor==='sky'?'on':''}" onclick="setLauncherIconBody('sky')">תכלת בהיר</button>
      <button class="icon-choice ${x.bodyColor==='yellowlight'?'on':''}" onclick="setLauncherIconBody('yellowlight')">צהוב בהיר</button>
      <button class="icon-choice ${x.bodyColor==='yellowdeep'?'on':''}" onclick="setLauncherIconBody('yellowdeep')">צהוב כהה</button>
      <button class="icon-choice ${x.bodyColor==='beigelight'?'on':''}" onclick="setLauncherIconBody('beigelight')">בז׳ בהיר</button>
      <button class="icon-choice ${x.bodyColor==='beigedeep'?'on':''}" onclick="setLauncherIconBody('beigedeep')">בז׳ כהה</button>
    </div></div>

    <div class="icon-choice-group"><div class="icon-choice-title">פס עליון</div><div class="icon-choice-row two">
      <button class="icon-choice ${x.topEnabled?'on':''}" onclick="setLauncherIconTopEnabled(true)">עם פס</button>
      <button class="icon-choice ${!x.topEnabled?'on':''}" onclick="setLauncherIconTopEnabled(false)">בלי פס</button>
    </div></div>

    <div class="icon-choice-group" style="opacity:${x.topEnabled?'1':'.45'}"><div class="icon-choice-title">צבע הפס העליון</div><div class="icon-choice-row four">
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

    <div class="default-icon-banner">ברירת המחדל נשארת תמיד: שחור + פס אדום + לבן + בינוני + מודגש</div>
    <button class="reset-design" onclick="resetLauncherIcon()">החזר אייקון לברירת המחדל</button>
    <button class="close" onclick="backToSettings()">חזרה להגדרות</button>`;
}
function applyLauncherIconSettings(){
  try{
    if(window.AndroidIcon&&AndroidIcon.setLauncherIcon){
      AndroidIcon.setLauncherIcon(launcherIconSettings.bodyColor,!!launcherIconSettings.topEnabled,launcherIconSettings.topColor,launcherIconSettings.textColor,launcherIconSettings.textSize,launcherIconSettings.fontWeight);
      toast('האייקון עודכן');
    }else toast('שינוי האייקון זמין בגרסת APK');
  }catch(e){toast('לא ניתן לעדכן את האייקון');}
  replaceOverlayHtml(iconSettingsHtml());
}
function setLauncherIconBody(v){if(!['black','charcoal','midgray','navy','blue','sky','yellowlight','yellowdeep','beigelight','beigedeep'].includes(v))return;launcherIconSettings.bodyColor=v;applyLauncherIconSettings();}
function setLauncherIconTopEnabled(v){launcherIconSettings.topEnabled=!!v;applyLauncherIconSettings();}
function setLauncherIconTop(v){if(!['red','burgundy','blue','green'].includes(v))return;launcherIconSettings.topColor=v;applyLauncherIconSettings();}
function setLauncherIconTextColor(v){if(!['white','black','yellow','navy','sky'].includes(v))return;launcherIconSettings.textColor=v;applyLauncherIconSettings();}
function setLauncherIconTextSize(v){if(!['small','normal','large'].includes(v))return;launcherIconSettings.textSize=v;applyLauncherIconSettings();}
function setLauncherIconWeight(v){if(!['bold','mediumw'].includes(v))return;launcherIconSettings.fontWeight=v;applyLauncherIconSettings();}
function resetLauncherIcon(){launcherIconSettings={bodyColor:'black',topEnabled:true,topColor:'red',textColor:'white',textSize:'normal',fontWeight:'bold'};applyLauncherIconSettings();}
function openIconSettings(){readLauncherIconSettings();openSettingsSubpage('icons');}
'''
pat=r"let launcherIconSettings=.*?function openIconSettings\(\)\{.*?\}\n"
t2,n=re.subn(pat,js,t,count=1,flags=re.S)
if n!=1: raise SystemExit('Could not replace launcher icon JS block for V10')
p.write_text(t2,encoding='utf-8')

# Java bridge
j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
s=j.read_text(encoding='utf-8')
bridge=r'''    public class IconBridge {
        private final String PREFS = "manyot_launcher_icon_v10";
        private final String[] BODY_COLORS = {"black", "charcoal", "midgray", "navy", "blue", "sky", "yellowlight", "yellowdeep", "beigelight", "beigedeep"};
        private final String[] TOP_COLORS = {"red", "burgundy", "blue", "green"};
        private final String[] TOP_MODES = {"none", "red", "burgundy", "blue", "green"};
        private final String[] TEXT_COLORS = {"white", "black", "yellow", "navy", "sky"};
        private final String[] TEXT_SIZES = {"small", "normal", "large"};
        private final String[] FONT_WEIGHTS = {"bold", "mediumw"};

        @android.webkit.JavascriptInterface
        public String getIconStyle() {
            android.content.SharedPreferences p = getSharedPreferences(PREFS, MODE_PRIVATE);
            String body = p.getString("bodyColor", "black");
            boolean topEnabled = p.getBoolean("topEnabled", true);
            String top = p.getString("topColor", "red");
            String text = p.getString("textColor", "white");
            String size = p.getString("textSize", "normal");
            String weight = p.getString("fontWeight", "bold");
            return "{\"bodyColor\":\"" + body + "\",\"topEnabled\":" + topEnabled + ",\"topColor\":\"" + top + "\",\"textColor\":\"" + text + "\",\"textSize\":\"" + size + "\",\"fontWeight\":\"" + weight + "\"}";
        }

        @android.webkit.JavascriptInterface
        public void setLauncherIcon(String bodyColor, boolean topEnabled, String topColor, String textColor, String textSize, String fontWeight) {
            final String body = valid(bodyColor, BODY_COLORS, "black");
            final boolean useTop = topEnabled;
            final String top = valid(topColor, TOP_COLORS, "red");
            final String text = valid(textColor, TEXT_COLORS, "white");
            final String size = valid(textSize, TEXT_SIZES, "normal");
            final String weight = valid(fontWeight, FONT_WEIGHTS, "bold");
            runOnUiThread(() -> {
                android.content.pm.PackageManager pm = getPackageManager();
                String topMode = useTop ? top : "none";
                String selected = aliasClass(body, topMode, text, size, weight);
                android.content.ComponentName selectedCn = new android.content.ComponentName(getPackageName(), selected);
                pm.setComponentEnabledSetting(selectedCn, android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_ENABLED, android.content.pm.PackageManager.DONT_KILL_APP);
                for (String b : BODY_COLORS) for (String tm : TOP_MODES) for (String tx : TEXT_COLORS) for (String sz : TEXT_SIZES) for (String wt : FONT_WEIGHTS) {
                    String alias = aliasClass(b, tm, tx, sz, wt);
                    if (alias.equals(selected)) continue;
                    android.content.ComponentName cn = new android.content.ComponentName(getPackageName(), alias);
                    pm.setComponentEnabledSetting(cn, android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED, android.content.pm.PackageManager.DONT_KILL_APP);
                }
                getSharedPreferences(PREFS, MODE_PRIVATE).edit()
                        .putString("bodyColor", body).putBoolean("topEnabled", useTop).putString("topColor", top)
                        .putString("textColor", text).putString("textSize", size).putString("fontWeight", weight).apply();
            });
        }

        private String aliasClass(String body, String topMode, String text, String size, String weight) {
            return "com.militzerjoseph.manyot.Icon_" + body + "_" + topMode + "_" + text + "_" + size + "_" + weight + "_v10";
        }
        private String valid(String v, String[] allowed, String fallback) {
            if (v != null) for (String a : allowed) if (a.equals(v)) return v;
            return fallback;
        }
    }
'''
pat=r'    public class IconBridge \{.*?\n    \}\n'
s2,n=re.subn(pat,bridge,s,count=1,flags=re.S)
if n!=1: raise SystemExit('Could not replace IconBridge for V10')
j.write_text(s2,encoding='utf-8')

# Manifest aliases
manifest=root/'app/src/main/AndroidManifest.xml'
ET.register_namespace('android','http://schemas.android.com/apk/res/android')
ns='{http://schemas.android.com/apk/res/android}'
tree=ET.parse(manifest)
app=tree.getroot().find('application')
if app is None: raise SystemExit('No application')
for alias in list(app.findall('activity-alias')):
    if alias.get(ns+'name','').startswith('com.militzerjoseph.manyot.Icon_'): app.remove(alias)

body_colors=['black','charcoal','midgray','navy','blue','sky','yellowlight','yellowdeep','beigelight','beigedeep']
top_modes=['none','red','burgundy','blue','green']
text_colors=['white','black','yellow','navy','sky']
sizes=['small','normal','large']
weights=['bold','mediumw']

def drawable_name(body,top,text,size,weight): return f'ic_manyot_v10_{body}_{top}_{text}_{size}_{weight}'
def alias_name(body,top,text,size,weight): return f'com.militzerjoseph.manyot.Icon_{body}_{top}_{text}_{size}_{weight}_v10'

default_draw=drawable_name('black','red','white','normal','bold')
app.set(ns+'icon','@drawable/'+default_draw)
if ns+'roundIcon' in app.attrib: app.set(ns+'roundIcon','@drawable/'+default_draw)

for body in body_colors:
    for top in top_modes:
        for text in text_colors:
            for size in sizes:
                for weight in weights:
                    alias=ET.SubElement(app,'activity-alias')
                    alias.set(ns+'name',alias_name(body,top,text,size,weight))
                    alias.set(ns+'targetActivity','com.militzerjoseph.manyot.MainActivity')
                    alias.set(ns+'exported','true')
                    is_default=(body=='black' and top=='red' and text=='white' and size=='normal' and weight=='bold')
                    alias.set(ns+'enabled','true' if is_default else 'false')
                    alias.set(ns+'icon','@drawable/'+drawable_name(body,top,text,size,weight))
                    alias.set(ns+'label','@string/app_name')
                    filt=ET.SubElement(alias,'intent-filter')
                    action=ET.SubElement(filt,'action'); action.set(ns+'name','android.intent.action.MAIN')
                    cat=ET.SubElement(filt,'category'); cat.set(ns+'name','android.intent.category.LAUNCHER')
tree.write(manifest,encoding='utf-8',xml_declaration=True)

# Generate icon variants at 512x512 to keep APK size practical.
icon_dir=root/'app/src/main/res/drawable-nodpi'
for old in icon_dir.glob('ic_manyot_*.png'): old.unlink()
S=512
R=108
body_rgb={
 'black':(23,25,28),'charcoal':(59,63,69),'midgray':(104,109,116),'navy':(24,40,62),'blue':(20,115,230),'sky':(159,211,236),
 'yellowlight':(246,223,122),'yellowdeep':(215,170,40),'beigelight':(234,215,183),'beigedeep':(185,153,114)
}
top_rgb={'red':(224,0,0),'burgundy':(143,23,48),'blue':(23,91,184),'green':(33,136,79)}
text_rgb={'white':(255,255,255),'black':(17,17,17),'yellow':(255,216,77),'navy':(23,54,93),'sky':(143,211,255)}
size_px={'small':96,'normal':116,'large':136}
font_bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
font_regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
if not Path(font_bold).exists(): font_bold='/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'
if not Path(font_regular).exists(): font_regular='/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'
label='מניות'

mask=Image.new('L',(S,S),0)
ImageDraw.Draw(mask).rounded_rectangle((18,18,S-18,S-18),radius=R,fill=255)

for body in body_colors:
  for top in top_modes:
    for text in text_colors:
      for size in sizes:
        for weight in weights:
          im=Image.new('RGBA',(S,S),(0,0,0,0))
          base=Image.new('RGBA',(S,S),body_rgb[body]+(255,))
          im.paste(base,(0,0),mask)
          if top!='none':
            stripe=Image.new('RGBA',(S,S),(0,0,0,0)); sd=ImageDraw.Draw(stripe)
            sd.rectangle((0,0,S,int(S*.31)),fill=top_rgb[top]+(255,))
            # soft glossy highlight over top strip
            gloss=Image.new('RGBA',(S,S),(0,0,0,0)); gd=ImageDraw.Draw(gloss)
            gd.rounded_rectangle((45,25,S-45,118),radius=55,fill=(255,255,255,55))
            stripe=Image.alpha_composite(stripe,gloss)
            im=Image.composite(stripe,im,mask)
          # subtle edge highlight
          edge=Image.new('RGBA',(S,S),(0,0,0,0)); ed=ImageDraw.Draw(edge)
          ed.rounded_rectangle((18,18,S-18,S-18),radius=R,outline=(255,255,255,55),width=3)
          im=Image.alpha_composite(im,edge)

          fp=font_bold if weight=='bold' else font_regular
          fs=size_px[size]
          font=ImageFont.truetype(fp,fs)
          d=ImageDraw.Draw(im)
          maxw=410
          while fs>54:
            font=ImageFont.truetype(fp,fs)
            try: bb=d.textbbox((0,0),label,font=font,direction='rtl')
            except Exception: bb=d.textbbox((0,0),label,font=font)
            if bb[2]-bb[0] <= maxw: break
            fs-=4
          try: bb=d.textbbox((0,0),label,font=font,direction='rtl')
          except Exception: bb=d.textbbox((0,0),label,font=font)
          tw,th=bb[2]-bb[0],bb[3]-bb[1]
          cy=int(S*.60) if top!='none' else int(S*.50)
          x=(S-tw)//2-bb[0]; y=cy-th//2-bb[1]
          shadow=(0,0,0,95) if text!='black' else (255,255,255,70)
          try:
            d.text((x+2,y+3),label,font=font,fill=shadow,direction='rtl')
            d.text((x,y),label,font=font,fill=text_rgb[text]+(255,),direction='rtl')
          except Exception:
            d.text((x+2,y+3),label,font=font,fill=shadow)
            d.text((x,y),label,font=font,fill=text_rgb[text]+(255,))
          out=icon_dir/(drawable_name(body,top,text,size,weight)+'.png')
          im.save(out,optimize=True,compress_level=9)

print('Manyot V10 ready:',len(list(icon_dir.glob('ic_manyot_v10_*.png'))),'icons')
