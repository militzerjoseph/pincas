from pathlib import Path
import re, json

root=Path('btl-build/manyot_android_v1')

# Android identity/version
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r"applicationId\s+'[^']+'", "applicationId 'com.militzerjoseph.btl'", s)
s=re.sub(r'versionCode\s+\d+', 'versionCode 1', s)
s=re.sub(r"versionName\s+'[^']+'", "versionName '1.0'", s)
g.write_text(s,encoding='utf-8')

strings=root/'app/src/main/res/values/strings.xml'
st=strings.read_text(encoding='utf-8').replace('חדשות','ביטוח לאומי').replace('מניות','ביטוח לאומי')
strings.write_text(st,encoding='utf-8')

# HTML identity + seed
p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>[^<]+</title>','<title>ביטוח לאומי - גרסה 1</title>',t,count=1)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='1';",t)
t=re.sub(r"const APP_NAME='[^']+';","const APP_NAME='ביטוח לאומי';",t)
t=re.sub(r"const STOCKS_ID='[^']+';","const STOCKS_ID='f_btl';",t)
t=re.sub(r"const STORAGE_KEY='[^']+';","const STORAGE_KEY='BTL_STANDALONE_V1';",t)

seed={
 'folders':[{'id':'f_btl','name':'ביטוח לאומי','color':'#FFD86E','icon':'👪','createdAt':1}],
 'links':[
  {'id':'seed_031','folderId':'f_btl','title':'7.05-ביטוח לאומי - התנדבות','url':'https://yairron.com/btl/','shortcutType':'website','tag':'','createdAt':31,'updatedAt':31},
  {'id':'seed_032','folderId':'f_btl','title':'7.0-המדריך לאזרח 2026','url':'','shortcutType':'website','tag':'','createdAt':32,'updatedAt':32},
  {'id':'seed_033','folderId':'f_btl','title':'7.4-אזרח ותיק *8840','url':'https://www.kolzchut.org.il/he/%D7%9E%D7%95%D7%A7%D7%93_8840','shortcutType':'website','tag':'','createdAt':33,'updatedAt':33},
  {'id':'seed_034','folderId':'f_btl','title':'7.6-ממשלה','url':'https://www.gov.il/','shortcutType':'website','tag':'','createdAt':34,'updatedAt':34},
  {'id':'seed_035','folderId':'f_btl','title':'7.3-אזרח ותיק','url':'','shortcutType':'website','tag':'','createdAt':35,'updatedAt':35},
  {'id':'seed_036','folderId':'f_btl','title':'7.1-דף הבית ביטוח לאומי','url':'','shortcutType':'website','tag':'','createdAt':36,'updatedAt':36},
  {'id':'seed_037','folderId':'f_btl','title':'7.5-מנוע זכויות הלאומי','url':'https://www.gov.il/he/service/national-rights-engine-service','shortcutType':'website','tag':'','createdAt':37,'updatedAt':37},
  {'id':'seed_038','folderId':'f_btl','title':'7.2-כל זכות','url':'','shortcutType':'website','tag':'','createdAt':38,'updatedAt':38},
 ]
}
seedline='const SEED='+json.dumps(seed,ensure_ascii=False,separators=(',',':'))+';'
t=re.sub(r'const SEED=.*?;\n\n',seedline+'\n\n',t,count=1,flags=re.S)

# Rename visible backup/app texts
t=t.replace('גיבוי_חדשות_','גיבוי_ביטוח_לאומי_').replace('גיבוי_חדשות.json','גיבוי_ביטוח_לאומי.json')
t=t.replace('גיבוי_מניות_','גיבוי_ביטוח_לאומי_').replace('גיבוי_מניות.json','גיבוי_ביטוח_לאומי.json')
t=t.replace("payload={app:'חדשות'","payload={app:'ביטוח לאומי'").replace("payload={app:'מניות'","payload={app:'ביטוח לאומי'")
t=t.replace("if(obj.app==='חדשות')","if(obj.app==='ביטוח לאומי')").replace("if(obj.app==='מניות')","if(obj.app==='ביטוח לאומי')")
t=t.replace("includes('חדשות')","includes('ביטוח לאומי')").replace("includes('מניות')","includes('ביטוח לאומי')")
t=t.replace('גיבוי של „חדשות”','גיבוי של „ביטוח לאומי”').replace('גיבוי של „מניות”','גיבוי של „ביטוח לאומי”')
t=t.replace('תיקיית חדשות','תיקיית ביטוח לאומי').replace('תיקיית מניות','תיקיית ביטוח לאומי')
t=t.replace('הכותרת „חדשות”','הכותרת „ביטוח לאומי”').replace('הכותרת „מניות”','הכותרת „ביטוח לאומי”')
p.write_text(t,encoding='utf-8')

# Java backup filename
j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
s=j.read_text(encoding='utf-8')
s=s.replace('גיבוי_חדשות.json','גיבוי_ביטוח_לאומי.json').replace('גיבוי_מניות.json','גיבוי_ביטוח_לאומי.json')
j.write_text(s,encoding='utf-8')
