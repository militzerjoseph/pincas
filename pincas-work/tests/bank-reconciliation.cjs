const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[2]||'app/src/main/assets/index.html','utf8');
const storage={};const elements={};
const c={console,Intl,Date,setTimeout,clearTimeout,alert(){},confirm(){return true},localStorage:{getItem(k){return storage[k]||null},setItem(k,v){storage[k]=v}},document:{addEventListener(){},getElementById(k){return elements[k]||null}},window:{addEventListener(){}}};vm.createContext(c);vm.runInContext(source.match(/<script\b[^>]*>([\s\S]*?)<\/script>/i)[1],c);
const run=s=>vm.runInContext(s,c);const get=s=>JSON.parse(JSON.stringify(run(s)));
run(`d=normalizeData({incomeCats:inc.map(name=>({name})),expenseCats:exp.map(name=>({name})),tx:[]});selectedYear=2026;selectedMonth=2;`);
assert.equal(run('d.expenseCats.length'),30);assert.equal(run('d.expenseCats[29].name'),'הוצאות בבנק');assert.equal(run('KEY'),'home_budget_pro_v3_categories');
run(`d=normalizeData(d);`);assert.equal(run('d.expenseCats.length'),30,'migration must be idempotent');
const tx=[];let id=1;
function add(month,amount,bank=false,type='expense'){tx.push({id:id++,type,date:`2026-${String(month).padStart(2,'0')}-01`,category:bank?'הוצאות בבנק':type==='income'?'משכורת בעל':'דברי מכולת',amount,recurring:bank});}
add(1,1000,false,'income');add(1,100);add(2,1200,false,'income');add(2,200);add(2,150,true);add(3,300);add(3,0,true);add(4,90);add(4,100,true);add(5,.1);add(5,.2);add(5,.25,true);add(6,5);add(6,-10,true);add(7,100);add(7,40,true);add(7,60,true);
c.tx=tx;run('d.tx=normalizeData({...d,tx}).tx');
assert.deepEqual(get("monthExpenses('2026-01')"),{recordedExpense:100,bankExpense:null,hasBank:false,expense:100,difference:null});
assert.equal(run("monthExpenses('2026-02').expense"),150);assert.equal(run("monthExpenses('2026-02').difference"),50);
assert.equal(run("monthExpenses('2026-03').expense"),300);assert.equal(run("monthExpenses('2026-03').bankExpense"),null);
assert.equal(run("monthExpenses('2026-04').difference"),-10);assert.equal(run("monthExpenses('2026-05').difference"),.05);
assert.equal(run("monthExpenses('2026-06').expense"),-10);assert.equal(run("monthExpenses('2026-07').expense"),100);
assert.equal(run("totals('2026').expense"),740.25);assert.equal(run("totals('2026').recordedExpense"),795.3);assert.equal(run("totals('2026').income"),2200);
assert.equal(run("sumTypeForPeriod('expense',2026)"),740.25);assert.equal(run('d.tx.filter(isBankTx).some(t=>t.recurring)'),false);
for(const [n,args] of [[1,'2026,2'],[2,'2026'],[3,'2026'],[4,'2026'],[5,'2026']]){
 const html=run(`makeReport${n}(${args})`);assert.equal((html.match(/data-category=/g)||[]).length,30,`report ${n} needs all categories`);assert.match(html,/הוצאות בבנק/);assert.match(html,/סה״כ הוצאות לחישוב/);
 if(n!==1)assert.match(html,/לא הוזן/);
}
const comparison=run('makeReport6(2026)');assert.equal((comparison.match(/data-comparison-row/g)||[]).length,3);assert.match(comparison,/\+/);assert.match(comparison,/−/);assert.match(comparison,/לא הוזן/);assert.match(comparison,/difference-plus/);assert.match(comparison,/difference-minus/);
// Zeroing, editing and deleting the bank record must immediately restore the ordinary totals.
run("d.tx.find(t=>isBankTx(t)&&t.date.startsWith('2026-02')).amount=0");assert.equal(run("totals('2026-02').expense"),200);
run("d.tx.find(t=>isBankTx(t)&&t.date.startsWith('2026-02')).amount=175");assert.equal(run("totals('2026-02').expense"),175);
run("d.tx=d.tx.filter(t=>!(isBankTx(t)&&t.date.startsWith('2026-02')))");assert.equal(run("totals('2026-02').expense"),200);
// An incorrectly marked old bank row must not create a recurring future bank total.
run("d.tx=[{id:100,type:'expense',category:BANK_CATEGORY,date:'2026-08-01',amount:123,recurring:true}];propagateRecurringForward('2026-08','2026-09')");assert.equal(run('d.tx.length'),1);
// Legacy restore retains original amounts/categories and adds only the reserved category.
run('d=normalizeData({incomeCats:inc.map(name=>({name})),expenseCats:exp.map(name=>({name})),tx,selectedYear:2026,selectedMonth:2})');assert.equal(run('d.expenseCats.length'),30);assert.equal(run('d.tx.length'),tx.length);
console.log('PASS: 30-category migration; nonzero/zero/missing bank; no double counting; mixed yearly totals; agorot; signed comparison; all reports; edit/delete fallback; recurring exclusion; legacy restore.');
