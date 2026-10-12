from pathlib import Path
import re, json

root=Path('hadashot-build/manyot_android_v1')
# Android identity/version. Keep Java namespace/package path to avoid unnecessary source moves;
# applicationId is unique so News installs beside Manyot.
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r"applicationId\s+'[^']+'", "applicationId 'com.militzerjoseph.hadashot'", s)
s=re.sub(r'versionCode\s+\d+', 'versionCode 1', s)
s=re.sub(r"versionName\s+'[^']+'", "versionName '1.0'", s)
g.write_text(s,encoding='utf-8')

strings=root/'app/src/main/res/values/strings.xml'
st=strings.read_text(encoding='utf-8').replace('מניות','חדשות')
strings.write_text(st,encoding='utf-8')

# ===== HTML =====
p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>מניות - גרסה \d+</title>','<title>חדשות - גרסה 1</title>',t)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='1';",t)
t=t.replace("const APP_NAME='מניות';","const APP_NAME='חדשות';")
t=t.replace("const STOCKS_ID='f_stocks';","const STOCKS_ID='f_news';")
t=t.replace("const STORAGE_KEY='MANYOT_STANDALONE_V1';","const STORAGE_KEY='HADASHOT_STANDALONE_V1';")

seed={
 'folders':[{'id':'f_news','name':'חדשות','color':'#D2D580','icon':'📰','createdAt':1}],
 'links':[
  {'id':'seed_001','folderId':'f_news','title':'5.1-חדשות Ynet','url':'https://share.google/C7KtLkvTTf5VbqjuE','shortcutType':'website','tag':'','createdAt':1,'updatedAt':1},
  {'id':'seed_002','folderId':'f_news','title':'5.2-מעריב','url':'https://www.maariv.co.il/','shortcutType':'website','tag':'','createdAt':2,'updatedAt':2},
  {'id':'seed_003','folderId':'f_news','title':'5.3-חדשות V1','url':'https://share.google/qTU4W1r3q2jbhjkxG','shortcutType':'website','tag':'','createdAt':3,'updatedAt':3},
  {'id':'seed_004','folderId':'f_news','title':'5.4-חדשות N12','url':'https://share.google/aFqMWY3AhOo5JE9g3','shortcutType':'website','tag':'','createdAt':4,'updatedAt':4},
  {'id':'seed_005','folderId':'f_news','title':'5.5-כלכליסט','url':'https://play.google.com/store/apps/details?id=com.opentech.calcalist','shortcutType':'website','tag':'','createdAt':5,'updatedAt':5},
 ]
}
seedline='const SEED='+json.dumps(seed,ensure_ascii=False,separators=(',',':'))+';'
t=re.sub(r'const SEED=.*?;\n\n',seedline+'\n\n',t,count=1,flags=re.S)

# News naming/backups/manual text.
t=t.replace('גיבוי_מניות_','גיבוי_חדשות_').replace('גיבוי_מניות.json','גיבוי_חדשות.json')
t=t.replace("payload={app:'מניות'","payload={app:'חדשות'")
t=t.replace("if(obj.app==='מניות')","if(obj.app==='חדשות')")
t=t.replace("includes('מניות')","includes('חדשות')")
t=t.replace('גיבוי של „מניות”','גיבוי של „חדשות”')
t=t.replace('תיקיית מניות','תיקיית חדשות')
t=t.replace('הכותרת „מניות”','הכותרת „חדשות”')

# Picker styles copied in spirit from Tikiot3: searchable list, icons, multi-select.
css='''\n.app-picker-search{width:100%;padding:12px 13px;border:2px solid #777;border-radius:14px;font-size:18px;margin:2px 0 10px}\n.app-picker-count{font-size:15px;color:#555;margin:4px 2px 8px}\n.app-picker-list{display:grid;gap:7px;max-height:48dvh;overflow:auto;padding:2px 0 8px}\n.app-row{display:grid;grid-template-columns:44px 1fr 34px;gap:10px;align-items:center;border:1px solid #ddd;background:#fafafa;border-radius:13px;padding:8px 10px;text-align:right}\n.app-row.on{background:#eef6ff;border-color:#5d8ed5}\n.app-row img{width:38px;height:38px;border-radius:9px;object-fit:contain}\n.app-row .fallback{font-size:29px;text-align:center}\n.app-row-name{font-size:17px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n.app-row-pkg{font-size:11px;color:#777;direction:ltr;text-align:left;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\n.app-row-check{font-size:22px;text-align:center}\n.app-shortcut-icon{width:34px;height:34px;border-radius:8px;object-fit:contain;display:block}\n'''
t=t.replace('.save{width:100%;',css+'\n.save{width:100%;',1)

# App shortcuts show their actual icon/package instead of "missing URL".
new_marker='''function linkMarker(l){
  if(l && l.shortcutType==='app'){
    if(l.appIcon)return '<img class="app-shortcut-icon" src="'+esc(l.appIcon)+'" alt="">';
    return '<span class="missing-mark">📱</span>';
  }
  if(!l || !l.url) return '<span class="missing-mark">✏️</span>';
  return globeSvg('website');
}'''
t=re.sub(r'function linkMarker\(l\)\{.*?\n\}',new_marker,t,count=1,flags=re.S)

# Render subtitle for native apps.
t=t.replace("${l.url?(uiPrefs().showUrl?'<small>'+esc(l.url)+'</small>':''):'<small class=\"missing\">כתובת להשלמה</small>'}",
            "${isAppShortcut(l)?('<small>'+esc(l.packageName||'אפליקציה')+'</small>'):(l.url?(uiPrefs().showUrl?'<small>'+esc(l.url)+'</small>':''):'<small class=\"missing\">כתובת להשלמה</small>')}")

# Full Tikiot3-style installed-app picker.
start=t.index('function openNewLink(){')
end=t.index('async function pasteUrl(){',start)
replacement=r'''let installedAppsCache=[];
let selectedAppPackages=new Set();

function openNewLink(){
  editId=null;editType='website';
  openOverlayHtml(`<h2>הוספת קיצור דרך</h2>
    <div class="form-stack">
      <div class="segment"><button id="webBtn" class="on" onclick="setType('website')">אתר</button><button id="appBtn" onclick="openInstalledAppsPicker()">אפליקציה</button></div>
      <input id="editTitle" class="field" placeholder="שם הקישור" autofocus>
      <div class="urlrow"><input id="editUrl" class="field" dir="ltr" placeholder="https://..."><button class="paste" onclick="pasteUrl()">הדבק URL</button></div>
    </div>
    <div class="sticky-actions"><button class="save" onclick="saveNewLinkFromForm()">שמור</button><button class="close" onclick="closeOverlay()">ביטול</button></div>`,{view:'overlay'},'#overlay',true);
}

function openInstalledAppsPicker(){
  if(!(window.AndroidApps&&AndroidApps.getLaunchableApps))return toast('רשימת האפליקציות זמינה בגרסת APK');
  let raw='[]';
  try{raw=AndroidApps.getLaunchableApps();}catch(e){}
  try{installedAppsCache=JSON.parse(String(raw||'[]'));}catch(e){installedAppsCache=[];}
  if(!Array.isArray(installedAppsCache)||!installedAppsCache.length)return toast('לא נמצאו אפליקציות');
  selectedAppPackages=new Set();
  replaceOverlayHtml(`<h2>בחר אפליקציות</h2>
    <input id="appSearch" class="app-picker-search" placeholder="חיפוש אפליקציה" oninput="renderInstalledAppsRows()">
    <div id="appPickerCount" class="app-picker-count">לא נבחרו אפליקציות</div>
    <div id="appRows" class="app-picker-list"></div>
    <div class="sticky-actions"><button class="save" onclick="addSelectedInstalledApps()">הוסף לתיק</button><button class="close" onclick="openNewLink()">חזרה</button></div>`,true);
  renderInstalledAppsRows();
}
function renderInstalledAppsRows(){
  const host=document.getElementById('appRows');if(!host)return;
  const q=(document.getElementById('appSearch')?.value||'').trim().toLowerCase();
  const rows=installedAppsCache.filter(a=>!q||String(a.name||'').toLowerCase().includes(q)||String(a.packageName||'').toLowerCase().includes(q));
  host.innerHTML=rows.length?rows.map(a=>{const pkg=String(a.packageName||'');const on=selectedAppPackages.has(pkg);return `<button class="app-row ${on?'on':''}" onclick="toggleInstalledApp('${jsq(pkg)}')">${a.icon?`<img src="${esc(a.icon)}" alt="">`:'<span class="fallback">📱</span>'}<span><div class="app-row-name">${esc(a.name||pkg)}</div><div class="app-row-pkg">${esc(pkg)}</div></span><span class="app-row-check">${on?'✓':'○'}</span></button>`;}).join(''):'<div class="empty" style="padding:16px">אין תוצאות</div>';
  updateInstalledAppsCount();
}
function toggleInstalledApp(pkg){if(selectedAppPackages.has(pkg))selectedAppPackages.delete(pkg);else selectedAppPackages.add(pkg);renderInstalledAppsRows();}
function updateInstalledAppsCount(){const el=document.getElementById('appPickerCount');if(el)el.textContent=selectedAppPackages.size?'נבחרו '+selectedAppPackages.size+' אפליקציות':'לא נבחרו אפליקציות';}
function addSelectedInstalledApps(){
  if(!selectedAppPackages.size)return toast('בחר לפחות אפליקציה אחת');
  const now=Date.now();let added=0;
  for(const a of installedAppsCache){
    const pkg=String(a.packageName||'');if(!selectedAppPackages.has(pkg))continue;
    if(DATA.links.some(l=>String(l.packageName||'')===pkg))continue;
    DATA.links.push({id:uid('l'),folderId:STOCKS_ID,title:String(a.name||pkg),url:'',shortcutType:'app',packageName:pkg,appIcon:String(a.icon||''),tag:'',createdAt:now+added,updatedAt:now+added});added++;
  }
  if(!added)return toast('האפליקציות שנבחרו כבר קיימות');
  saveLocal();toast(added===1?'האפליקציה נוספה':'האפליקציות נוספו');closeOverlay();
}

function openEdit(id,replaceCurrent){
  const l=findLink(id);if(!l)return;editId=String(id);editType=l.shortcutType||'website';
  const appNative=editType==='app'&&l.packageName;
  const x=`<h2>עריכת קיצור דרך</h2>
    <div class="form-stack">
      <div class="segment"><button id="webBtn" class="${editType==='website'?'on':''}" onclick="setType('website')">אתר</button><button id="appBtn" class="${editType==='app'?'on':''}" onclick="setType('app')">אפליקציה</button></div>
      <input id="editTitle" class="field" value="${esc(l.title)}" placeholder="שם הקישור" autofocus>
      ${appNative?`<div class="field" style="background:#f3f3f3;direction:ltr">${esc(l.packageName)}</div>`:`<div class="urlrow"><input id="editUrl" class="field" dir="ltr" value="${esc(l.url||'')}" placeholder="https://..."><button class="paste" onclick="pasteUrl()">הדבק URL</button></div>`}
    </div>
    <div class="sticky-actions"><button class="save" onclick="saveEdit()">שמור</button><button class="close" onclick="closeOverlay()">ביטול</button><button class="close danger" onclick="deleteEditingLink()">מחיקת קיצור דרך</button></div>`;
  replaceCurrent&&document.getElementById('ov')?replaceOverlayHtml(x,true):openOverlayHtml(x,{view:'overlay'},'#overlay',true);
}
function setType(x){editType=x;document.getElementById('webBtn')?.classList.toggle('on',x==='website');document.getElementById('appBtn')?.classList.toggle('on',x==='app');}
'''
t=t[:start]+replacement+t[end:]

# Save edit preserves native app identity; converting to website clears native app fields.
old="""  const title=document.getElementById('editTitle')?.value.trim()||'';
  let url=document.getElementById('editUrl')?.value.trim()||'';
  if(!title)return toast('נא להקליד שם');
  if(url&&editType==='website'&&!/^https?:\/\//i.test(url))url='https://'+url;
  l.title=title;l.url=url;l.shortcutType=editType;l.updatedAt=Date.now();"""
new="""  const title=document.getElementById('editTitle')?.value.trim()||'';
  let url=document.getElementById('editUrl')?.value.trim()||l.url||'';
  if(!title)return toast('נא להקליד שם');
  if(url&&editType==='website'&&!/^https?:\/\//i.test(url))url='https://'+url;
  l.title=title;l.url=url;l.shortcutType=editType;l.updatedAt=Date.now();
  if(editType==='website'){delete l.packageName;delete l.appIcon;}"""
t=t.replace(old,new)

# Native package launch before URL logic.
needle="""function openShortcut(id){
  const l=findLink(id);if(!l)return;
  if(!l.url)return openEdit(id,false);"""
repl="""function openShortcut(id){
  const l=findLink(id);if(!l)return;
  if(l.shortcutType==='app'&&l.packageName){
    try{if(window.AndroidApps&&AndroidApps.launchApp){AndroidApps.launchApp(String(l.packageName));return;}}catch(e){}
  }
  if(!l.url)return openEdit(id,false);"""
t=t.replace(needle,repl)

p.write_text(t,encoding='utf-8')

# ===== Java: expose Tikiot3-style app list with names, package IDs and icons =====
j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
s=j.read_text(encoding='utf-8')
s=s.replace('import android.net.Uri;','import android.net.Uri;\nimport android.graphics.Bitmap;\nimport android.graphics.Canvas;\nimport android.graphics.drawable.Drawable;\nimport android.util.Base64;')
s=s.replace('import org.json.JSONObject;','import org.json.JSONObject;\nimport org.json.JSONArray;')
s=s.replace('import java.io.OutputStream;','import java.io.OutputStream;\nimport java.io.ByteArrayOutputStream;')
marker='''        @JavascriptInterface
        public boolean openPackage(String packageName) {'''
insert='''        @JavascriptInterface
        public String getLaunchableApps() { return getLaunchableAppsJson(); }

        @JavascriptInterface
        public void launchApp(String packageName) { openPackage(packageName); }

'''
s=s.replace(marker,insert+marker,1)
helper='''
    private String drawableToDataUri(Drawable drawable) {
        if (drawable == null) return "";
        try {
            final int size = 72;
            Bitmap bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888);
            Canvas canvas = new Canvas(bitmap);
            drawable.setBounds(0,0,size,size);
            drawable.draw(canvas);
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.PNG, 85, out);
            String enc = Base64.encodeToString(out.toByteArray(), Base64.NO_WRAP);
            bitmap.recycle();
            return "data:image/png;base64," + enc;
        } catch (Exception e) { return ""; }
    }

    private String getLaunchableAppsJson() {
        JSONArray arr = new JSONArray();
        try {
            PackageManager pm = getPackageManager();
            Intent launcher = new Intent(Intent.ACTION_MAIN, null);
            launcher.addCategory(Intent.CATEGORY_LAUNCHER);
            List<ResolveInfo> resolved = pm.queryIntentActivities(launcher, PackageManager.MATCH_ALL);
            Map<String, ResolveInfo> unique = new LinkedHashMap<>();
            for (ResolveInfo ri : resolved) {
                if (ri.activityInfo == null || ri.activityInfo.packageName == null) continue;
                String pkg = ri.activityInfo.packageName;
                if (getPackageName().equals(pkg)) continue;
                if (!unique.containsKey(pkg)) unique.put(pkg,ri);
            }
            List<ResolveInfo> apps = new ArrayList<>(unique.values());
            Collections.sort(apps,(a,b)->String.valueOf(a.loadLabel(pm)).compareToIgnoreCase(String.valueOf(b.loadLabel(pm))));
            for (ResolveInfo ri : apps) {
                JSONObject o = new JSONObject();
                String pkg = ri.activityInfo.packageName;
                String label = String.valueOf(ri.loadLabel(pm));
                if (label == null || label.trim().isEmpty() || "null".equals(label)) label = pkg;
                o.put("name",label); o.put("packageName",pkg);
                try { o.put("icon",drawableToDataUri(ri.loadIcon(pm))); } catch (Exception ignored) { o.put("icon",""); }
                arr.put(o);
            }
        } catch (Exception ignored) {}
        return arr.toString();
    }

'''
s=s.replace('    private void showInstalledAppsDialog() {',helper+'    private void showInstalledAppsDialog() {',1)
s=s.replace('גיבוי_מניות.json','גיבוי_חדשות.json')
j.write_text(s,encoding='utf-8')
