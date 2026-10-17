from pathlib import Path
import re, json
root=Path('btl-build/manyot_android_v1')

g=root/'app/build.gradle'
s=g.read_text(encoding='utf-8')
s=re.sub(r"applicationId\s+'[^']+'", "applicationId 'com.militzerjoseph.ksafimcard'", s)
s=re.sub(r'versionCode\s+\d+', 'versionCode 1', s)
s=re.sub(r"versionName\s+'[^']+'", "versionName '1.0'", s)
g.write_text(s,encoding='utf-8')

strings=root/'app/src/main/res/values/strings.xml'
st=strings.read_text(encoding='utf-8')
st=st.replace('ביטוח לאומי','כספים').replace('מניות','כספים').replace('חדשות','כספים')
strings.write_text(st,encoding='utf-8')

p=root/'app/src/main/assets/index.html'
t=p.read_text(encoding='utf-8')
t=re.sub(r'<title>[^<]+</title>','<title>כספים - גרסה 1</title>',t,count=1)
t=re.sub(r"const APP_VERSION='\d+';","const APP_VERSION='1';",t)
t=re.sub(r"const APP_NAME='[^']+';","const APP_NAME='כספים';",t)
t=re.sub(r"const STOCKS_ID='[^']+';","const STOCKS_ID='f_ksafim';",t)
t=re.sub(r"const STORAGE_KEY='[^']+';","const STORAGE_KEY='KSAFIM_STANDALONE_V1';",t)

seed={
  'folders':[{'id':'f_ksafim','name':'כספים','color':'#FFD86E','icon':'📁','createdAt':1}],
  'links':[
    {'id':'ks_001','folderId':'f_ksafim','title':'1-פנקס הכנסות והוצאות','url':'','shortcutType':'app','packageName':'com.example.pincaswebapk','appIcon':'','tag':'','createdAt':1,'updatedAt':1},
    {'id':'ks_002','folderId':'f_ksafim','title':'2-פנקס הוצאות','url':'','shortcutType':'app','packageName':'com.example.pincashybrid','appIcon':'','tag':'','createdAt':2,'updatedAt':2},
    {'id':'ks_003','folderId':'f_ksafim','title':'3-מחשבון הכנסה חודשית','url':'','shortcutType':'app','packageName':'com.monthlyincome.calculator.debug','appIcon':'','tag':'','createdAt':3,'updatedAt':3}
  ]
}
seedline='const SEED='+json.dumps(seed,ensure_ascii=False,separators=(',',':'))+';'
t=re.sub(r'const SEED=.*?;\n\n',seedline+'\n\n',t,count=1,flags=re.S)

for old in ['ביטוח לאומי','מניות','חדשות']:
    t=t.replace('גיבוי_'+old+'_','גיבוי_כספים_').replace('גיבוי_'+old+'.json','גיבוי_כספים.json')
    t=t.replace("payload={app:'"+old+"'","payload={app:'כספים'")
    t=t.replace("if(obj.app==='"+old+"')","if(obj.app==='כספים')")
    t=t.replace("includes('"+old+"')","includes('כספים')")
    t=t.replace('גיבוי של „'+old+'”','גיבוי של „כספים”')
    t=t.replace('תיקיית '+old,'תיקיית כספים')
    t=t.replace('הכותרת „'+old+'”','הכותרת „כספים”')
p.write_text(t,encoding='utf-8')

j=root/'app/src/main/java/com/militzerjoseph/manyot/MainActivity.java'
js=j.read_text(encoding='utf-8')
js=js.replace('גיבוי_ביטוח_לאומי.json','גיבוי_כספים.json').replace('גיבוי_מניות.json','גיבוי_כספים.json').replace('גיבוי_חדשות.json','גיבוי_כספים.json')
j.write_text(js,encoding='utf-8')
print('Ksafim base transformed')
