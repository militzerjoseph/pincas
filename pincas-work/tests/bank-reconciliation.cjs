const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[2]||'app/src/main/assets/index.html','utf8');
const storage={},elements={};
const c={console,Intl,Date,setTimeout,clearTimeout,alert(){},confirm(){return true},localStorage:{getItem(k){return storage[k]||null},setItem(k,v){storage[k]=v}},document:{addEventListener(){},getElementById(k){return elements[k]||null}},window:{addEventListener(){}}};
vm.createContext(c);vm.runInContext(source.match(/<script\b[^>]*>([\s\S]*?)<\/script>/i)[1],c);
const run=s=>vm.runInContext(s,c),get=s=>JSON.parse(JSON.stringify(run(s)));
const tx=[];let id=0;
function add(month,amount,bank=false,type='expense'){tx.push({id:++id,type,date:`2026-${String(month).padStart(2,'0')}-01`,category:bank?'הוצאות בבנק':type==='income'?'משכורת בעל':'דברי מכולת',amount,recurring:bank,bankEntryMode:bank?'adjustment':undefined});}
add(1,50000,false,'income');add(1,20000);add(1,1000,true);add(2,20000);add(2,-1500,true);add(3,300);add(4,500);add(4,0,true);add(5,.1);add(5,.2);add(5,.05,true);
c.tx=tx;run('d=normalizeData({tx});selectedYear=2026;selectedMonth=1');
assert.equal(run('d.expenseCats.length'),30);assert.equal(run('d.expenseCats[29].name'),'הוצאות בבנק');assert.equal(run('KEY'),'home_budget_pro_v3_categories');
assert.deepEqual(get("monthExpenses('2026-01')"),{recordedExpense:20000,adjustment:1000,hasBank:true,expense:19000});
assert.equal(run("totals('2026-02').expense"),21500);assert.equal(run("totals('2026-03').expense"),300);assert.equal(run("totals('2026-04').expense"),500);
assert.equal(run("totals('2026-05').expense"),.25);assert.equal(run("totals('2026').expense"),41300.25);assert.equal(run("totals('2026').adjustment"),-499.95);
assert.equal(run('d.tx.filter(isBankTx).some(t=>t.recurring)'),false);
for(let n=1;n<=6;n++){
 const html=run(`makeReport${n}(2026${n===1?',1':''})`);
 assert.doesNotMatch(html,/לא הוזן/);assert.match(html,/הוצאות בבנק/);
 if(n<6)assert.equal((html.match(/data-category=/g)||[]).length,30);
 else {assert.equal((html.match(/data-comparison-row/g)||[]).length,1);assert.match(html,/סה״כ מצטבר/);assert.match(html,/499\.95/);assert.match(html,/difference-plus/);assert.match(html,/difference-minus/);assert.match(html,/−/);assert.match(html,/\+/);}
}
// Changing or deleting a correction recalculates immediately; corrections never propagate.
run("d.tx.find(t=>isBankTx(t)&&t.date.startsWith('2026-01')).amount=0");assert.equal(run("totals('2026-01').expense"),20000);
run("d.tx.find(t=>isBankTx(t)&&t.date.startsWith('2026-01')).amount=-1000");assert.equal(run("totals('2026-01').expense"),21000);
run("d.tx=d.tx.filter(t=>!(isBankTx(t)&&t.date.startsWith('2026-01')))");assert.equal(run("totals('2026-01').expense"),20000);
run("d.tx=[{id:100,type:'expense',category:BANK_CATEGORY,date:'2026-08-01',amount:-123,bankEntryMode:'adjustment',recurring:true}];propagateRecurringForward('2026-08','2026-09')");assert.equal(run('d.tx.length'),1);
// Migrate the old absolute-bank-total semantics without changing any effective month total.
c.legacy=[{id:1,type:'expense',category:'דברי מכולת',date:'2026-01-01',amount:200},{id:2,type:'expense',category:'הוצאות בבנק',date:'2026-01-01',amount:150},{id:3,type:'expense',category:'דברי מכולת',date:'2026-02-01',amount:300},{id:4,type:'expense',category:'הוצאות בבנק',date:'2026-02-01',amount:0},{id:5,type:'expense',category:'דברי מכולת',date:'2026-03-01',amount:90},{id:6,type:'expense',category:'הוצאות בבנק',date:'2026-03-01',amount:40},{id:7,type:'expense',category:'הוצאות בבנק',date:'2026-03-01',amount:60}];
run('d=normalizeData({tx:legacy})');assert.equal(run("totals('2026-01').expense"),150);assert.equal(run('d.tx[1].amount'),50);assert.equal(run('d.tx[1].previousBankTotal'),150);
assert.equal(run("totals('2026-02').expense"),300);assert.equal(run("totals('2026-03').expense"),100);assert.equal(run('d.tx.length'),7);
const migrated=get('d');run('d=normalizeData(d)');assert.deepEqual(get('d'),migrated,'migration must run exactly once');
c.backup=JSON.parse(JSON.stringify(migrated));run('d=normalizeData(backup)');assert.deepEqual(get('d'),migrated,'new backup must not be migrated again');
assert.equal(run("amountForExpenseCategory(BANK_CATEGORY,2026,4)"),0);assert.match(run('signedDifference(0)'),/>[^<]*0/);assert.doesNotMatch(run('signedDifference(0)'),/[+−]/);
assert.match(run('money(250000)'),/250,000/);assert.doesNotMatch(run('money(250000)'),/\.00/);assert.match(run('money(250000.25)'),/\.25/);
console.log('PASS: signed adjustments reduce/increase expenses; missing/zero=0; partial-year signed sum; all 30 categories; one-row report 6; cents; edit/delete; recurrence exclusion; old full-total migration and restore idempotence.');
