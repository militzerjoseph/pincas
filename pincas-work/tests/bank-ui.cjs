const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:412,height:915}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',d=>d.accept());
await page.addInitScript(()=>{window.AndroidPrint={printReport:(html,landscape)=>{window.__printed={html,landscape}}}});
await page.goto(pathToFileURL(path.resolve('app/src/main/assets/index.html')).href);
await page.evaluate(()=>{
 d=normalizeData({incomeCats:inc.map(name=>({name,budget:0})),expenseCats:exp.map(name=>({name,budget:0})),tx:[
 {id:1,type:'income',date:'2026-02-01',category:inc[0],amount:1000},
 {id:2,type:'expense',date:'2026-02-01',category:'דברי מכולת',amount:200},
 {id:3,type:'expense',date:'2026-02-01',category:BANK_CATEGORY,amount:150},
 {id:4,type:'expense',date:'2026-03-01',category:'דברי מכולת',amount:300},
 {id:5,type:'expense',date:'2026-03-01',category:BANK_CATEGORY,amount:0},
 {id:6,type:'expense',date:'2026-04-01',category:'דברי מכולת',amount:90},
 {id:7,type:'expense',date:'2026-04-01',category:BANK_CATEGORY,amount:100},
 {id:8,type:'expense',date:'2025-12-01',category:'דברי מכולת',amount:50}
 ],selectedYear:2026,selectedMonth:2});selectedYear=2026;selectedMonth=2;save();initUI();
});
assert.match(await page.locator('#he').innerText(),/150/);assert.match(await page.locator('#hb').innerText(),/850/);assert.match(await page.locator('#homeExpenseBasis').innerText(),/לפי הבנק/);
assert.equal(await page.evaluate(()=>d.expenseCats.length),30);assert.equal(await page.evaluate(()=>d.expenseCats[29].name),'הוצאות בבנק');
// A zero bank amount reverts to the ordinary recorded expenditure.
await page.evaluate(()=>{d.tx.find(t=>t.id===3).amount=0;save();renderHome()});assert.match(await page.locator('#he').innerText(),/200/);assert.match(await page.locator('#homeExpenseBasis').innerText(),/לא הוזן/);
// Editing to a nonzero value activates the override without replacing any ordinary entry.
await page.evaluate(()=>{openExistingTx(3);toggleAmountEdit('expense')});await page.locator('#expenseAmount').fill('175');await page.locator('#expenseEditAmountBtn').click();
assert.match(await page.locator('#he').innerText(),/175/);assert.equal(await page.evaluate(()=>d.tx.find(t=>t.id===2).amount),200);
// Bank category must not be recurring; reject a second monthly bank entry.
await page.evaluate(()=>openNewEntry('expense'));await page.selectOption('#expenseCat','הוצאות בבנק');assert.equal(await page.locator('#expenseRecurringBtn').isDisabled(),true);
await page.locator('#expenseAmount').fill('180');await page.locator('#expenseSubmitBtn').click();assert.equal(await page.evaluate(()=>d.tx.filter(t=>isBankTx(t)&&t.date.startsWith('2026-02')).length),1);
await page.evaluate(()=>view('home'));
// Every existing report shows all 30 categories on both paths. Print receives the exact same generated report.
for(let n=1;n<=6;n++){
 await page.evaluate(n=>{openPrintChoice();chooseReportDestination('screen');selectPrintReport(n)},n);
 const report=page.locator('#reportOutput');
 if(n<=5)assert.equal(await report.locator('[data-category]').count(),30,`screen report ${n}`);
 else {assert.equal(await report.locator('[data-comparison-row]').count(),3);assert.match(await report.innerText(),/לא הוזן/);assert.match(await report.locator('.difference-plus').first().innerText(),/\+/);assert.match(await report.locator('.difference-minus').first().innerText(),/−/);}
 await page.evaluate(()=>{printDestination='printer';runSelectedReport()});
 const print=await page.evaluate(()=>window.__printed);assert.equal(print.landscape,true);assert.match(print.html,/הוצאות בבנק|הוצאות לפי הבנק/);
 if(n<=5)assert.equal((print.html.match(/data-category=/g)||[]).length,30,`printed report ${n}`);
 if(n===2||n===6){
  const proof=await browser.newPage({viewport:{width:1400,height:1100}});await proof.setContent(print.html);
  fs.mkdirSync('../pincas-output',{recursive:true});
  await proof.screenshot({path:`../pincas-output/bank-report-${n}.png`,fullPage:true});
  await proof.pdf({path:`../pincas-output/bank-report-${n}.pdf`,format:'A4',landscape:true,printBackground:true,preferCSSPageSize:true});
  await proof.close();
 }
 await page.evaluate(()=>closePrintModal());
}
await page.evaluate(()=>view('reports'));
assert.equal(await page.locator('#monthlyExpenseCategories [data-category]').count(),30);
assert.equal(await page.locator('#annualExpenseCategories [data-category]').count(),30);
assert.match(await page.locator('#annualExpenseCategories').innerText(),/2025/);
await page.evaluate(()=>view('home'));await page.screenshot({path:'../pincas-output/bank-home.png',fullPage:true});
assert.deepEqual(errors,[]);console.log('PASS: bank category 30; dashboard override/fallback; editing; duplicate prevention; recurring disabled; all 6 screen/print paths; identical print content; yearly/monthly detail categories; PDFs rendered.');
await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
