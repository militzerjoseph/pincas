from pathlib import Path
import re, json

root=Path('banks-build/manyot_android_v1')

# Android identity/version
g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r"applicationId\s+'[^']+'", "applicationId 'com.militzerjoseph.banks'", s)
s=re.sub(r'versionCode\s+\d+', 'versionCode 1', s)
s=re.sub(r"versionName\s+'[^']+'", "versionName '1.0'", s)
g.write_text(s,encoding='utf-8')

strings=root/'app/src/main/res/values/strings.xml'
st=strings.read_text(encoding='utf-8').replace('חדשות','בנקים').replace('מניות','בנקים')
strings.write_text(st,encoding='utf-8')

# HTML identity + seed
p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>[^<]+</title>','<title>בנקים - גרסה 1</title>',t,count=1)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='1';",t)
t=re.sub(r"const APP_NAME='[^']+';","const APP_NAME='בנקים';",t)
t=re.sub(r"const STOCKS_ID='[^']+';","const STOCKS_ID='f_banks';",t)
t=re.sub(r"const STORAGE_KEY='[^']+';","const STORAGE_KEY='BANKS_STANDALONE_V1';",t)

seed={
 'folders':[{'id':'f_banks','name':'בנקים','color':'#FFD86E','icon':'🏦','createdAt':1}],
 'links':[
  {'id':'seed_039','folderId':'f_banks','title':'3.0-מאזן הבית שוטף','url':'','shortcutType':'website','tag':'','createdAt':39,'updatedAt':39},
  {'id':'seed_040','folderId':'f_banks','title':'2.5-מאזן הבית יבוא','url':'','shortcutType':'website','tag':'','createdAt':40,'updatedAt':40},
  {'id':'seed_041','folderId':'f_banks','title':'3.5-מחשבון הכנסות מ קרן','url':'','shortcutType':'website','tag':'','createdAt':41,'updatedAt':41},
  {'id':'seed_042','folderId':'f_banks','title':'2.0-פנקס הוצאות והכנסות','url':'','shortcutType':'website','tag':'','createdAt':42,'updatedAt':42},
  {'id':'seed_043','folderId':'f_banks','title':'5.0-לאומי טרייד','url':'https://play.google.com/store/apps/details?id=com.leumi.iLeumiTrade.UI','shortcutType':'website','tag':'','createdAt':43,'updatedAt':43},
  {'id':'seed_044','folderId':'f_banks','title':'4.0-בנק לאומי אפליקציה','url':'https://play.google.com/store/apps/details?id=com.leumi.leumiwallet','shortcutType':'website','tag':'','createdAt':44,'updatedAt':44},
  {'id':'seed_045','folderId':'f_banks','title':'4.5-בנק לאומי - כניסה לחשבונך','url':'https://share.google/hECYiX1oE3TJQ5JxQ','shortcutType':'website','tag':'','createdAt':45,'updatedAt':45},
  {'id':'seed_046','folderId':'f_banks','title':'5.5-עמיתים','url':'https://play.google.com/store/apps/details?id=com.amitim','shortcutType':'website','tag':'','createdAt':46,'updatedAt':46},
 ]
}
seedline='const SEED='+json.dumps(seed,ensure_ascii=False,separators=(',',':'))+';'
t=re.sub(r'const SEED=.*?;\n\n',seedline+'\n\n',t,count=1,flags=re.S)

# Rename user-visible backup/app texts
t=t.replace('גיבוי_חדשות_','גיבוי_בנקים_').replace('גיבוי_חדשות.json','גיבוי_בנקים.json')
t=t.replace('גיבוי_מניות_','גיבוי_בנקים_').replace('גיבוי_מניות.json','גיבוי_בנקים.json')
t=t.replace("payload={app:'חדשות'","payload={app:'בנקים'").replace("payload={app:'מניות'","payload={app:'בנקים'")
t=t.replace("if(obj.app==='חדשות')","if(obj.app==='בנקים')").replace("if(obj.app==='מניות')","if(obj.app==='בנקים')")
t=t.replace("includes('חדשות')","includes('בנקים')").replace("includes('מניות')","includes('בנקים')")
t=t.replace('גיבוי של „חדשות”','גיבוי של „בנקים”').replace('גיבוי של „מניות”','גיבוי של „בנקים”')
t=t.replace('תיקיית חדשות','תיקיית בנקים').replace('תיקיית מניות','תיקיית בנקים')
t=t.replace('הכותרת „חדשות”','הכותרת „בנקים”').replace('הכותרת „מניות”','הכותרת „בנקים”')
t=t.replace('חדשות - גרסה 1','בנקים - גרסה 1')
p.write_text(t,encoding='utf-8')

# Java backup filename
j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
s=j.read_text(encoding='utf-8')
s=s.replace('גיבוי_חדשות.json','גיבוי_בנקים.json').replace('גיבוי_מניות.json','גיבוי_בנקים.json')
j.write_text(s,encoding='utf-8')
