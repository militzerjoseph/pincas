const fs=require('fs'), vm=require('vm'), assert=require('assert');
const html=fs.readFileSync(__dirname+'/app/src/main/assets/index.html','utf8');
let code=html.match(/<script>([\s\S]*)<\/script>/)[1];
new vm.Script(code); // Syntax-check the shipped script, including initialization.
code=code.replace(/\nloadLocal\(\);\s*applyUiSettings\(\);\s*ensureDefaultLauncherIcon\(\);\s*initHistory\(\);\s*renderApp\(\);\s*$/,'');
const handlers={},storage=new Map();
const input={addEventListener:(event,fn)=>handlers.restore=fn};
const context={console,structuredClone,Set,Date,JSON,URL,setTimeout,clearTimeout,
 document:{getElementById:id=>id==='restoreInput'?input:null,addEventListener:()=>{}},
 window:{addEventListener:()=>{}},history:{},navigator:{userAgent:'Android'},
 localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v),removeItem:k=>storage.delete(k)}};
vm.createContext(context);vm.runInContext(code,context);
const run=s=>vm.runInContext(s,context);
const original=run('structuredClone(SEED)');original.app='בנקים';original.version=1;
context.fixture=original;
assert.equal(run('extractStocksFromBackup(fixture).links.length'),original.links.length);
assert.equal(run('extractStocksFromBackup({app:"בנקים",links:[]}).links.length'),0);
assert.throws(()=>run('extractStocksFromBackup({app:"כספים",links:[]})'));
assert.throws(()=>run('extractStocksFromBackup({app:"כספים",folders:[{id:"f_banks",name:"בנקים"}],links:[]})'));
assert.throws(()=>run('extractStocksFromBackup({links:[{title:"bad",url:"javascript:alert(1)"}],app:"בנקים"})'));
context.multi={folders:[{id:'x',name:'1.0–בנקים'},{id:'other',name:'מניות'}],links:[{id:'a',folderId:'x',title:'3.0-בנק',url:'https://example.com'},{id:'b',folderId:'other',title:'אחר',url:'https://example.com'}]};
assert.equal(run('extractStocksFromBackup(multi).links.length'),1);
assert.equal(run('extractStocksFromBackup(multi).links[0].folderId'),'f_banks');
assert.equal(run('normalizeLauncherIconObject({mode:"text",background:"dark",grid:true,textSize:"small",textColor:"yellow"}).mode'),'text');
assert.equal(run('normalizeLauncherIconObject({mode:"picture"}).mode'),'picture');
// A failed storage write during restore must leave the prior DATA intact.
run('DATA={folders:[],links:[{id:"keep",title:"keep"}],lastBackup:""}; applyUiSettings=()=>{};renderApp=()=>{};toast=()=>{};');
context.confirm=()=>true;
context.localStorage.setItem=()=>{throw Error('disk full');};
(async()=>{
 await handlers.restore.call({files:[{size:100,text:async()=>JSON.stringify(original)}]});
 assert.equal(run('DATA.links[0].id'),'keep');
 context.localStorage.setItem=(k,v)=>storage.set(k,v);
 await handlers.restore.call({files:[{size:100,text:async()=>JSON.stringify(original)}]});
 assert.equal(run('DATA.links.length'),original.links.length);
 assert.equal(JSON.parse([...storage.values()][0]).links.length,original.links.length);
 console.log('PASS: shipped JS syntax, old banks backup, folder extraction, wrong-app/URL rejection, icon choices, restore rollback and successful restore');
})().catch(e=>{console.error(e);process.exitCode=1});
