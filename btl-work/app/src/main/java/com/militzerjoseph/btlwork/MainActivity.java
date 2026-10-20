package com.militzerjoseph.btlwork;

import android.app.*;
import android.content.*;
import android.content.pm.*;
import android.database.Cursor;
import android.graphics.*;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.*;
import android.provider.*;
import android.webkit.*;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;

public class MainActivity extends Activity {
    private WebView web;
    private ValueCallback<Uri[]> fileCallback;
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private SharedPreferences prefs;
    private static final int FILE=10, CLOUD=11, EXPORT=12;
    private boolean busy=false, destroyed=false;
    private String pendingJson=null;
    private boolean pendingApk=false;
    private String exportJson=null; private boolean exportApk=false;
    private String pendingIcon=null;
    private static final String[] BGS={"style","light","medium","dark","black","white","charcoal","navy","yellow","grid","plain","large","small","normal","background","color"};
    private static final String[] SIZES={"small","normal","large"};
    private static final String[] COLORS={"white","black","charcoal","navy","yellow"};

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        prefs=getSharedPreferences("btl_work",MODE_PRIVATE);
        LinearLayout frame=new LinearLayout(this);frame.setBackgroundColor(Color.WHITE);
        frame.setOrientation(LinearLayout.VERTICAL);
        frame.setOnApplyWindowInsetsListener((v,insets)->{v.setPadding(insets.getSystemWindowInsetLeft(),insets.getSystemWindowInsetTop(),insets.getSystemWindowInsetRight(),insets.getSystemWindowInsetBottom());return insets;});
        web=new WebView(this);frame.addView(web,new LinearLayout.LayoutParams(-1,-1));setContentView(frame);
        WebSettings s=web.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);
        s.setAllowFileAccess(false);s.setAllowContentAccess(true);s.setSupportMultipleWindows(false);
        web.addJavascriptInterface(new AppsBridge(),"AndroidApps");
        web.addJavascriptInterface(new ClipboardBridge(),"AndroidClipboard");
        web.addJavascriptInterface(new BackupBridge(),"AndroidBackup");
        web.addJavascriptInterface(new IconBridge(),"AndroidIcon");
        web.setWebViewClient(new WebViewClient(){
            @Override public boolean shouldOverrideUrlLoading(WebView v,WebResourceRequest r){return outside(r.getUrl().toString());}
            @Override public boolean shouldOverrideUrlLoading(WebView v,String u){return outside(u);}
        });
        web.setWebChromeClient(new WebChromeClient(){
            @Override public boolean onJsConfirm(WebView v,String u,String msg,JsResult r){new AlertDialog.Builder(MainActivity.this).setMessage(msg).setPositiveButton("כן",(d,w)->r.confirm()).setNegativeButton("ביטול",(d,w)->r.cancel()).setOnCancelListener(d->r.cancel()).show();return true;}
            @Override public boolean onJsAlert(WebView v,String u,String msg,JsResult r){new AlertDialog.Builder(MainActivity.this).setMessage(msg).setPositiveButton("אישור",(d,w)->r.confirm()).setOnCancelListener(d->r.confirm()).show();return true;}
            @Override public boolean onShowFileChooser(WebView v,ValueCallback<Uri[]> cb,FileChooserParams p){
                if(fileCallback!=null)fileCallback.onReceiveValue(null);fileCallback=cb;
                Intent in=new Intent(Intent.ACTION_OPEN_DOCUMENT).setType("*/*").addCategory(Intent.CATEGORY_OPENABLE);
                in.putExtra(Intent.EXTRA_MIME_TYPES,new String[]{"application/json","text/plain","application/octet-stream"});
                try{startActivityForResult(in,FILE);return true;}catch(Exception e){fileCallback=null;cb.onReceiveValue(null);message("לא ניתן לפתוח את בוחר הקבצים");return true;}
            }
        });
        web.loadUrl("file:///android_asset/index.html");
    }
    private boolean outside(String u){
        if("file:///android_asset/index.html".equals(u)||u.startsWith("file:///android_asset/index.html#"))return false;
        try {Uri uri=Uri.parse(u);String scheme=uri.getScheme();
            if(Arrays.asList("https","http","tel","mailto","market").contains(scheme))startActivity(new Intent(Intent.ACTION_VIEW,uri));
            else if("intent".equals(scheme)){Intent in=Intent.parseUri(u,Intent.URI_INTENT_SCHEME);in.addCategory(Intent.CATEGORY_BROWSABLE);in.setComponent(null);in.setSelector(null);try{startActivity(in);}catch(ActivityNotFoundException e){String f=in.getStringExtra("browser_fallback_url");if(f!=null&&f.startsWith("https://"))startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse(f)));}}
        }catch(Exception e){message("לא ניתן לפתוח את הקישור");}return true;
    }
    private void message(String s){runOnUiThread(()->{if(!destroyed)Toast.makeText(this,s,Toast.LENGTH_LONG).show();});}
    private void js(String s){runOnUiThread(()->{if(!destroyed)web.evaluateJavascript(s,null);});}
    public class ClipboardBridge {
        @JavascriptInterface public String getText(){try{ClipboardManager c=(ClipboardManager)getSystemService(CLIPBOARD_SERVICE);if(c.hasPrimaryClip())return String.valueOf(c.getPrimaryClip().getItemAt(0).coerceToText(MainActivity.this));}catch(Exception ignored){}return "";}
    }
    public class AppsBridge {
        @JavascriptInterface public String getLaunchableApps(){
            JSONArray out=new JSONArray();PackageManager pm=getPackageManager();
            List<ResolveInfo> apps=pm.queryIntentActivities(new Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER),0);
            apps.sort((a,b)->String.valueOf(a.loadLabel(pm)).compareToIgnoreCase(String.valueOf(b.loadLabel(pm))));Set<String> seen=new HashSet<>();
            for(ResolveInfo r:apps){String pkg=r.activityInfo.packageName;if(pkg.equals(getPackageName())||!seen.add(pkg))continue;
                try{JSONObject x=new JSONObject();x.put("name",r.loadLabel(pm));x.put("packageName",pkg);
                    Drawable d=r.loadIcon(pm);Bitmap bm=Bitmap.createBitmap(72,72,Bitmap.Config.ARGB_8888);d.setBounds(0,0,72,72);d.draw(new Canvas(bm));ByteArrayOutputStream b=new ByteArrayOutputStream();bm.compress(Bitmap.CompressFormat.PNG,100,b);bm.recycle();
                    x.put("icon","data:image/png;base64,"+android.util.Base64.encodeToString(b.toByteArray(),android.util.Base64.NO_WRAP));out.put(x);
                }catch(Exception ignored){}
            }return out.toString();
        }
        @JavascriptInterface public boolean openPackage(String p){Intent in=getPackageManager().getLaunchIntentForPackage(p);if(in==null)return false;runOnUiThread(()->{try{startActivity(in);}catch(Exception e){message("האפליקציה אינה זמינה");}});return true;}
        @JavascriptInterface public void launchApp(String p){if(!openPackage(p))message("האפליקציה אינה מותקנת בטלפון");}
    }
    public class IconBridge {
        @JavascriptInterface public String getIconStyle(){return prefs.getString("icon","{\"mode\":\"picture\",\"background\":\"style\",\"grid\":false,\"textSize\":\"large\",\"textColor\":\"white\"}");}
        @JavascriptInterface public void setStyle(String json){try{JSONObject x=new JSONObject(json);String alias="Picture";if(!x.optString("mode","picture").equals("picture")){String bg=x.optString("background"),sz=x.optString("textSize"),co=x.optString("textColor");if(!Arrays.asList(BGS).contains(bg)||!Arrays.asList(SIZES).contains(sz)||!Arrays.asList(COLORS).contains(co))return;alias="Text_"+bg+"_"+(x.optBoolean("grid")?"grid":"plain")+"_"+sz+"_"+co;}String chosen=alias;runOnUiThread(()->{pendingIcon=chosen;prefs.edit().putString("icon",json).apply();});}catch(Exception ignored){}}
    }
    private void commitIcon(){if(pendingIcon==null)return;PackageManager pm=getPackageManager();String name=getPackageName()+"."+pendingIcon;
        try{pm.setComponentEnabledSetting(new ComponentName(this,name),PackageManager.COMPONENT_ENABLED_STATE_ENABLED,PackageManager.DONT_KILL_APP);
            PackageInfo info=pm.getPackageInfo(getPackageName(),PackageManager.GET_ACTIVITIES|PackageManager.MATCH_DISABLED_COMPONENTS);
            for(ActivityInfo a:info.activities)if(a.targetActivity!=null&&!a.name.equals(name))pm.setComponentEnabledSetting(new ComponentName(this,a.name),PackageManager.COMPONENT_ENABLED_STATE_DISABLED,PackageManager.DONT_KILL_APP);
            pendingIcon=null;
        }catch(Exception e){message("לא ניתן לעדכן את האייקון");}
    }
    public class BackupBridge {
        @JavascriptInterface public String status(){JSONObject x=new JSONObject();try{x.put("cloud",!prefs.getString("cloud","").isEmpty());x.put("lastApk",prefs.getInt("apk_local",0));}catch(Exception ignored){}return x.toString();}
        @JavascriptInterface public void configureCloud(){runOnUiThread(()->pickCloud());}
        @JavascriptInterface public void disconnectCloud(){prefs.edit().remove("cloud").remove("apk_cloud").apply();message("תיקיית הענן נותקה; הקבצים הקיימים נשמרו");}
        @JavascriptInterface public void backupData(String json){runOnUiThread(()->requestBackup(json,false));}
        @JavascriptInterface public void backupApk(){runOnUiThread(()->requestBackup(null,true));}
        @JavascriptInterface public void exportData(String json){runOnUiThread(()->exportCopy(json,false));}
        @JavascriptInterface public void exportApk(){runOnUiThread(()->exportCopy(null,true));}
    }
    private void pickCloud(){try{Intent in=new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);in.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION|Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION|Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);startActivityForResult(in,CLOUD);}catch(Exception e){message("לא ניתן לפתוח בחירת תיקייה");}}
    private void requestBackup(String json,boolean apk){
        if(busy){message("גיבוי כבר מתבצע");return;}
        if(!apk){try{JSONObject x=new JSONObject(json);if(!x.optString("app").equals("ב.לאומי")||x.optJSONArray("links")==null)throw new Exception();}catch(Exception e){message("נתוני גיבוי לא תקינים");return;}}
        if(prefs.getString("cloud","").isEmpty()){
            new AlertDialog.Builder(this).setTitle("גיבוי ב.לאומי").setMessage("אפשר לשמור גם בתיקייה ב־Google Drive. בבוחר התיקיות בחר את תיקיית הגיבויים שלך בענן.")
            .setPositiveButton("בחירת תיקיית ענן",(d,w)->{pendingJson=json;pendingApk=apk;pickCloud();})
            .setNeutralButton("בטלפון בלבד",(d,w)->performBackup(json,apk)).setNegativeButton("ביטול",(d,w)->{}).show();
        }else performBackup(json,apk);
    }
    private void exportCopy(String json,boolean apk){
        if(busy){message("גיבוי כבר מתבצע");return;}
        if(apk&&prefs.getInt("apk_export",0)>=101){message("עותק APK לגרסה זו כבר נשמר דרך בוחר הקבצים");return;}
        exportJson=json;exportApk=apk;
        Intent in=new Intent(Intent.ACTION_CREATE_DOCUMENT).addCategory(Intent.CATEGORY_OPENABLE).setType(apk?"application/vnd.android.package-archive":"application/json");
        String name=apk?"Btl_Work_V101.apk":"גיבוי_ב.לאומי_"+new java.text.SimpleDateFormat("yyyy-MM-dd_HH-mm-ss",Locale.US).format(new Date())+".json";
        in.putExtra(Intent.EXTRA_TITLE,name);
        try{startActivityForResult(in,EXPORT);}catch(Exception e){exportJson=null;exportApk=false;message("לא ניתן לפתוח חלון שמירה");}
    }
    private void performBackup(String json,boolean apk){performBackup(json,apk,null);}
    private void performBackup(String json,boolean apk,Uri exportUri){
        if(busy)return;busy=true;
        io.execute(()->{
            boolean local=false,cloud=false;String error="";String folder=apk?"APK":"נתונים";
            String stamp=new java.text.SimpleDateFormat("yyyy-MM-dd_HH-mm-ss-SSS",Locale.US).format(new Date());
            String name=apk?"Btl_Work_V101.apk":"גיבוי_ב.לאומי_"+stamp+".json";
            File source=apk?new File(getApplicationInfo().sourceDir):null;byte[] bytes=apk?null:json.getBytes(StandardCharsets.UTF_8);
            try{if(apk&&prefs.getInt("apk_local",0)>=101&&hasLocal(name,folder)){local=true;}else{writeLocal(name,folder,apk?"application/vnd.android.package-archive":"application/json",source,bytes);local=true;if(apk)prefs.edit().putInt("apk_local",101).apply();}}catch(Exception e){error="שמירה בטלפון נכשלה";}
            String tree=exportUri!=null?"export":prefs.getString("cloud","");
            if(!tree.isEmpty())try{
                if(exportUri!=null){writeBytes(exportUri,source,bytes);if(apk)prefs.edit().putInt("apk_export",101).apply();cloud=true;}else{
                Uri root=Uri.parse(tree);Uri doc=DocumentsContract.buildDocumentUriUsingTree(root,DocumentsContract.getTreeDocumentId(root));
                Uri app=childDir(root,doc,"ב.לאומי");Uri dest=childDir(root,app,folder);
                Uri existing=apk?findChild(root,dest,name):null;
                if(existing==null){Uri out=DocumentsContract.createDocument(getContentResolver(),dest,apk?"application/vnd.android.package-archive":"application/json",name);if(out==null)throw new IOException();try{writeBytes(out,source,bytes);}catch(Exception e){try{DocumentsContract.deleteDocument(getContentResolver(),out);}catch(Exception ignored){}throw e;}}
                cloud=true;}
            }catch(Exception e){error+=(error.isEmpty()?"":"; ")+"שמירה בענן נכשלה — בדוק הרשאה או בחר תיקייה מחדש";}
            boolean l=local,c=cloud;String err=error;
            runOnUiThread(()->{busy=false;if(destroyed)return;
                if(!apk&&(l||c))js("backupCompleted("+JSONObject.quote(stamp)+")");
                String m=(l?"הגיבוי נשמר בטלפון":"לא נשמר גיבוי בטלפון")+(tree.isEmpty()?"":c?" וגם בתיקיית הענן":"; לא נשמר בענן");
                if(!err.isEmpty())m+="\n"+err;
                new AlertDialog.Builder(this).setTitle(apk?"גיבוי תוכנית (APK)":"גיבוי נתונים").setMessage(m).setPositiveButton("אישור",null).show();
            });
        });
    }
    private Uri findChild(Uri tree,Uri parent,String name)throws Exception{
        Uri children=DocumentsContract.buildChildDocumentsUriUsingTree(tree,DocumentsContract.getDocumentId(parent));
        try(Cursor c=getContentResolver().query(children,new String[]{DocumentsContract.Document.COLUMN_DOCUMENT_ID,DocumentsContract.Document.COLUMN_DISPLAY_NAME},null,null,null)){
            if(c==null)throw new IOException();while(c.moveToNext())if(name.equals(c.getString(1)))return DocumentsContract.buildDocumentUriUsingTree(tree,c.getString(0));
        }return null;
    }
    private Uri childDir(Uri tree,Uri parent,String name)throws Exception{Uri found=findChild(tree,parent,name);if(found!=null)return found;Uri u=DocumentsContract.createDocument(getContentResolver(),parent,DocumentsContract.Document.MIME_TYPE_DIR,name);if(u==null)throw new IOException();return u;}
    private String localPath(String folder){return Environment.DIRECTORY_DOWNLOADS+"/גיבויים/ב.לאומי/"+folder+"/";}
    private boolean hasLocal(String name,String folder){try(Cursor c=getContentResolver().query(MediaStore.Downloads.EXTERNAL_CONTENT_URI,new String[]{MediaStore.Downloads._ID},MediaStore.Downloads.DISPLAY_NAME+"=? AND "+MediaStore.Downloads.RELATIVE_PATH+"=?",new String[]{name,localPath(folder)},null)){return c!=null&&c.moveToFirst();}catch(Exception e){return false;}}
    private void writeLocal(String name,String folder,String mime,File source,byte[] bytes)throws Exception{
        ContentValues v=new ContentValues();v.put(MediaStore.Downloads.DISPLAY_NAME,name);v.put(MediaStore.Downloads.MIME_TYPE,mime);v.put(MediaStore.Downloads.RELATIVE_PATH,localPath(folder));v.put(MediaStore.Downloads.IS_PENDING,1);
        Uri u=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v);if(u==null)throw new IOException();
        try{writeBytes(u,source,bytes);v.clear();v.put(MediaStore.Downloads.IS_PENDING,0);if(getContentResolver().update(u,v,null,null)<1)throw new IOException();}catch(Exception e){getContentResolver().delete(u,null,null);throw e;}
    }
    private void writeBytes(Uri u,File source,byte[] bytes)throws Exception{try(InputStream in=source==null?new ByteArrayInputStream(bytes):new FileInputStream(source);OutputStream out=getContentResolver().openOutputStream(u,"w")){if(out==null)throw new IOException();byte[] buffer=new byte[65536];int n;while((n=in.read(buffer))!=-1)out.write(buffer,0,n);out.flush();}}
    @Override protected void onActivityResult(int req,int res,Intent data){super.onActivityResult(req,res,data);
        if(req==EXPORT){if(res==RESULT_OK&&data!=null&&data.getData()!=null)performBackup(exportJson,exportApk,data.getData());exportJson=null;exportApk=false;return;}
        if(req==FILE){if(fileCallback!=null){fileCallback.onReceiveValue(res==RESULT_OK&&data!=null&&data.getData()!=null?new Uri[]{data.getData()}:null);fileCallback=null;}return;}
        if(req==CLOUD){if(res==RESULT_OK&&data!=null&&data.getData()!=null){try{Uri uri=data.getData();int flags=data.getFlags()&(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION);if((flags&Intent.FLAG_GRANT_WRITE_URI_PERMISSION)==0)throw new IOException();getContentResolver().takePersistableUriPermission(uri,flags);prefs.edit().putString("cloud",uri.toString()).apply();message("תיקיית הענן נשמרה להמשך");if(pendingJson!=null||pendingApk)performBackup(pendingJson,pendingApk);js("refreshBackupSettings()");}catch(Exception e){message("לא ניתן לשמור הרשאה לתיקייה");}}pendingJson=null;pendingApk=false;}
    }
    @Override protected void onStop(){super.onStop();commitIcon();}
    @Override public void onBackPressed(){web.evaluateJavascript("!!document.getElementById('ov')",r->{if("true".equals(r))web.evaluateJavascript("closeOverlay()",null);else{commitIcon();finish();}});}
    @Override protected void onDestroy(){destroyed=true;if(fileCallback!=null)fileCallback.onReceiveValue(null);if(web!=null)web.destroy();io.shutdown();super.onDestroy();}
}

