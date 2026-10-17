from pathlib import Path
import re, xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

root=Path('btl-build/manyot_android_v1')

# --- Separate trial identity: never overwrite the existing Ksafim app ---
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r"applicationId\s+'[^']+'", "applicationId 'com.militzerjoseph.ksafimicontrial1'", s)
s=re.sub(r'versionCode\s+\d+', 'versionCode 1', s)
s=re.sub(r"versionName\s+'[^']+'", "versionName '1.0'", s)
g.write_text(s,encoding='utf-8')

strings=root/'app/src/main/res/values/strings.xml'
st=strings.read_text(encoding='utf-8')
st=re.sub(r'(<string\s+name="app_name">).*?(</string>)', r'\1כספים ניסיון\2', st, count=1, flags=re.S)
strings.write_text(st,encoding='utf-8')

p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>[^<]+</title>','<title>כספים ניסיון - גרסה 1</title>',t,count=1)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='1';",t)
t=re.sub(r"const APP_NAME='[^']+';","const APP_NAME='כספים ניסיון';",t)
t=re.sub(r"const STORAGE_KEY='[^']+';","const STORAGE_KEY='KSAFIM_ICON_TRIAL_V1';",t)

# Add icon mode to the existing proven color designer.
t=t.replace("let launcherIconSettings={bodyColor:", "let launcherIconSettings={iconMode:'picture',bodyColor:", 1)
t=t.replace("const obj=JSON.parse(String(AndroidIcon.getIconStyle()||'{}'));", "const obj=JSON.parse(String(AndroidIcon.getIconStyle()||'{}'));\n      if(['picture','color'].includes(obj.iconMode))launcherIconSettings.iconMode=obj.iconMode;", 1)

marker='    <div class="default-icon-banner">ברירת המחדל:'
mode_html='''    <div class="icon-choice-group"><div class="icon-choice-title">סוג האייקון</div><div class="icon-choice-row two">\n      <button class="icon-choice ${x.iconMode==='picture'?'on':''}" onclick="setLauncherIconMode('picture')">ציור + כיתוב</button>\n      <button class="icon-choice ${x.iconMode==='color'?'on':''}" onclick="setLauncherIconMode('color')">צבע + כיתוב</button>\n    </div></div>\n    <div class="default-icon-banner">ברירת המחדל: ציור של כסף + הכיתוב „כספים”. במצב צבע אפשר לבחור את הצבעים והכיתוב למטה.</div>\n\n'''
if marker not in t:
    raise SystemExit('Could not find icon settings insertion point')
t=t.replace(marker, mode_html+marker, 1)

old_call="AndroidIcon.setLauncherIcon(launcherIconSettings.bodyColor,!!launcherIconSettings.topEnabled,launcherIconSettings.topColor,launcherIconSettings.textColor,launcherIconSettings.textSize,launcherIconSettings.fontWeight);"
new_call="AndroidIcon.setLauncherIcon(launcherIconSettings.iconMode,launcherIconSettings.bodyColor,!!launcherIconSettings.topEnabled,launcherIconSettings.topColor,launcherIconSettings.textColor,launcherIconSettings.textSize,launcherIconSettings.fontWeight);"
if old_call not in t:
    raise SystemExit('Could not patch launcher icon call')
t=t.replace(old_call,new_call,1)

t=t.replace("function setLauncherIconBody(v){", "function setLauncherIconMode(v){if(!['picture','color'].includes(v))return;launcherIconSettings.iconMode=v;applyLauncherIconSettings();}\nfunction setLauncherIconBody(v){", 1)
t=t.replace("function resetLauncherIcon(){launcherIconSettings={bodyColor:", "function resetLauncherIcon(){launcherIconSettings={iconMode:'picture',bodyColor:", 1)
p.write_text(t,encoding='utf-8')

# Replace Java bridge with a two-mode-aware bridge.
j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
s=j.read_text(encoding='utf-8')
bridge=r'''    public class IconBridge {
        private final String PREFS = "ksafim_trial_launcher_icon_v1";
        private final String[] BODY_COLORS = {"black", "charcoal", "midgray", "navy", "blue", "sky", "yellowlight", "yellowdeep", "beigelight", "beigedeep"};
        private final String[] TOP_COLORS = {"red", "burgundy", "blue", "green"};
        private final String[] TOP_MODES = {"none", "red", "burgundy", "blue", "green"};
        private final String[] TEXT_COLORS = {"white", "black", "yellow", "navy", "sky"};
        private final String[] TEXT_SIZES = {"small", "normal", "large"};
        private final String[] FONT_WEIGHTS = {"bold", "mediumw"};
        private final String PICTURE_ALIAS = "com.militzerjoseph.manyot.Icon_KsafimPicture_v1";

        @android.webkit.JavascriptInterface
        public String getIconStyle() {
            android.content.SharedPreferences p = getSharedPreferences(PREFS, MODE_PRIVATE);
            String mode = p.getString("iconMode", "picture");
            String body = p.getString("bodyColor", "blue");
            boolean topEnabled = p.getBoolean("topEnabled", false);
            String top = p.getString("topColor", "red");
            String text = p.getString("textColor", "white");
            String size = p.getString("textSize", "normal");
            String weight = p.getString("fontWeight", "bold");
            return "{\"iconMode\":\"" + mode + "\",\"bodyColor\":\"" + body + "\",\"topEnabled\":" + topEnabled + ",\"topColor\":\"" + top + "\",\"textColor\":\"" + text + "\",\"textSize\":\"" + size + "\",\"fontWeight\":\"" + weight + "\"}";
        }

        @android.webkit.JavascriptInterface
        public void setLauncherIcon(String iconMode, String bodyColor, boolean topEnabled, String topColor, String textColor, String textSize, String fontWeight) {
            final String mode = "color".equals(iconMode) ? "color" : "picture";
            final String body = valid(bodyColor, BODY_COLORS, "blue");
            final boolean useTop = topEnabled;
            final String top = valid(topColor, TOP_COLORS, "red");
            final String text = valid(textColor, TEXT_COLORS, "white");
            final String size = valid(textSize, TEXT_SIZES, "normal");
            final String weight = valid(fontWeight, FONT_WEIGHTS, "bold");
            runOnUiThread(() -> {
                android.content.pm.PackageManager pm = getPackageManager();
                String topMode = useTop ? top : "none";
                String selected = "picture".equals(mode) ? PICTURE_ALIAS : aliasClass(body, topMode, text, size, weight);
                android.content.ComponentName selectedCn = new android.content.ComponentName(getPackageName(), selected);
                pm.setComponentEnabledSetting(selectedCn, android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_ENABLED, android.content.pm.PackageManager.DONT_KILL_APP);

                android.content.ComponentName pictureCn = new android.content.ComponentName(getPackageName(), PICTURE_ALIAS);
                if (!PICTURE_ALIAS.equals(selected)) {
                    pm.setComponentEnabledSetting(pictureCn, android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED, android.content.pm.PackageManager.DONT_KILL_APP);
                }
                for (String b : BODY_COLORS) for (String tm : TOP_MODES) for (String tx : TEXT_COLORS) for (String sz : TEXT_SIZES) for (String wt : FONT_WEIGHTS) {
                    String alias = aliasClass(b, tm, tx, sz, wt);
                    if (alias.equals(selected)) continue;
                    android.content.ComponentName cn = new android.content.ComponentName(getPackageName(), alias);
                    pm.setComponentEnabledSetting(cn, android.content.pm.PackageManager.COMPONENT_ENABLED_STATE_DISABLED, android.content.pm.PackageManager.DONT_KILL_APP);
                }
                getSharedPreferences(PREFS, MODE_PRIVATE).edit()
                        .putString("iconMode", mode).putString("bodyColor", body).putBoolean("topEnabled", useTop).putString("topColor", top)
                        .putString("textColor", text).putString("textSize", size).putString("fontWeight", weight).apply();
            });
        }

        private String aliasClass(String body, String topMode, String text, String size, String weight) {
            return "com.militzerjoseph.manyot.Icon_" + body + "_" + topMode + "_" + text + "_" + size + "_" + weight + "_v8";
        }
        private String valid(String v, String[] allowed, String fallback) {
            if (v != null) for (String a : allowed) if (a.equals(v)) return v;
            return fallback;
        }
    }
'''
pat=r'    public class IconBridge \{.*?\n    \}\n'
s2,n=re.subn(pat,bridge,s,count=1,flags=re.S)
if n!=1: raise SystemExit('Could not replace IconBridge for Ksafim trial')
j.write_text(s2,encoding='utf-8')

# Manifest: keep the proven color aliases, but make the picture alias the only default-enabled launcher.
manifest=root/'app/src/main/AndroidManifest.xml'
ET.register_namespace('android','http://schemas.android.com/apk/res/android')
ns='{http://schemas.android.com/apk/res/android}'
tree=ET.parse(manifest)
app=tree.getroot().find('application')
if app is None: raise SystemExit('No application')
for alias in app.findall('activity-alias'):
    if alias.get(ns+'name','').startswith('com.militzerjoseph.manyot.Icon_'):
        alias.set(ns+'enabled','false')

picture_alias_name='com.militzerjoseph.manyot.Icon_KsafimPicture_v1'
for alias in list(app.findall('activity-alias')):
    if alias.get(ns+'name','')==picture_alias_name:
        app.remove(alias)

alias=ET.SubElement(app,'activity-alias')
alias.set(ns+'name',picture_alias_name)
alias.set(ns+'targetActivity','com.militzerjoseph.manyot.MainActivity')
alias.set(ns+'exported','true')
alias.set(ns+'enabled','true')
alias.set(ns+'icon','@drawable/ic_ksafim_picture_v1')
alias.set(ns+'label','@string/app_name')
filt=ET.SubElement(alias,'intent-filter')
action=ET.SubElement(filt,'action'); action.set(ns+'name','android.intent.action.MAIN')
cat=ET.SubElement(filt,'category'); cat.set(ns+'name','android.intent.category.LAUNCHER')
app.set(ns+'icon','@drawable/ic_ksafim_picture_v1')
if ns+'roundIcon' in app.attrib: app.set(ns+'roundIcon','@drawable/ic_ksafim_picture_v1')
tree.write(manifest,encoding='utf-8',xml_declaration=True)

# Generate the default picture icon: wallet + coins + shekel sign + Ksafim text.
icon_dir=root/'app/src/main/res/drawable-nodpi'
icon_dir.mkdir(parents=True,exist_ok=True)
S=512
im=Image.new('RGBA',(S,S),(0,0,0,0))
d=ImageDraw.Draw(im)
d.rounded_rectangle((18,18,S-18,S-18),radius=108,fill=(31,86,125,255),outline=(255,255,255,65),width=4)
# soft upper panel
d.rounded_rectangle((38,38,S-38,300),radius=80,fill=(45,112,157,255))
# wallet
d.rounded_rectangle((112,165,400,310),radius=34,fill=(219,166,46,255),outline=(119,80,14,255),width=7)
d.rounded_rectangle((292,208,417,275),radius=24,fill=(243,203,92,255),outline=(119,80,14,255),width=6)
d.ellipse((333,226,359,252),fill=(119,80,14,255))
# coins
for x,y in [(105,117),(163,104),(220,120)]:
    d.ellipse((x,y,x+86,y+86),fill=(250,211,92,255),outline=(146,101,20,255),width=6)
# shekel on wallet
font_bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
if not Path(font_bold).exists(): font_bold='/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'
font_symbol=ImageFont.truetype(font_bold,82)
try: bb=d.textbbox((0,0),'₪',font=font_symbol)
except Exception: bb=(0,0,50,80)
tw=bb[2]-bb[0]
d.text(((S-tw)//2-bb[0],185-bb[1]),'₪',font=font_symbol,fill=(35,62,78,255))
# Hebrew label at bottom
label='כספים'
fs=88
font=ImageFont.truetype(font_bold,fs)
try: bb=d.textbbox((0,0),label,font=font,direction='rtl')
except Exception: bb=d.textbbox((0,0),label,font=font)
tw,th=bb[2]-bb[0],bb[3]-bb[1]
x=(S-tw)//2-bb[0]; y=384-th//2-bb[1]
try:
    d.text((x+2,y+3),label,font=font,fill=(0,0,0,90),direction='rtl')
    d.text((x,y),label,font=font,fill=(255,255,255,255),direction='rtl')
except Exception:
    d.text((x+2,y+3),label,font=font,fill=(0,0,0,90))
    d.text((x,y),label,font=font,fill=(255,255,255,255))
im.save(icon_dir/'ic_ksafim_picture_v1.png',optimize=True,compress_level=9)

print('Ksafim icon trial ready: picture is default, color designer remains available')
