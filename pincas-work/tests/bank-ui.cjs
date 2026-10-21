const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:412,height:915}});
 const errors=[],dialogs=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',async d=>{dialogs.push(d.message());await d.accept()});
 await page.addInitScript(()=>{window.AndroidPrint={printReport:(html,landscape)=>{window.__printed={html,landscape}}}});
 await page.goto(pathToFileURL(path.resolve('app/src/main/assets/index.html')).href);
 await page.evaluate(()=>{
  d=normalizeData({tx:[{id:1,type:'income',category:inc[0],date:'2026-01-01',amount:30000},{id:2,type:'expense',category:exp[0],date:'2026-01-01',amount:20000}],selectedYear:2026,selectedMonth:1});
  selectedYear=2026;selectedMonth=1;initUI();save();
 });
 await page.evaluate(()=>openNewEntry('expense'));
 await page.locator('#expenseAmount').fill('1000');
 assert.equal(await page.locator('#bankPositiveAction').isVisible(),false);
 assert.equal(await page.locator('#expenseRecurringWrap').isVisible(),true);
 await page.selectOption('#expenseCat','הוצאות בבנק');
 assert.equal(await page.locator('#expenseAmount').inputValue(),'1000','choosing category preserves amount');
 assert.equal(await page.locator('#expenseRecurringWrap').isVisible(),false);
 assert.equal(await page.locator('#bankPositiveBtn').isVisible(),true);
 assert.equal(await page.locator('#expenseSubmitBtn').isVisible(),true);
 assert.match(await page.locator('#bankPositiveBtn').innerText(),/\+/);
 assert.match(await page.locator('#expenseSubmitBtn').innerText(),/−/);
 fs.mkdirSync('../pincas-output',{recursive:true});
 await page.screenshot({path:'../pincas-output/bank-adjustment-buttons.png',fullPage:true});
 await page.locator('#bankPositiveBtn').click();
 assert.equal(await page.evaluate(()=>d.tx.find(isBankTx).amount),1000);
 assert.equal(await page.evaluate(()=>d.tx.find(isBankTx).bankEntryMode),'adjustment');
 assert.match(await page.locator('#he').innerText(),/19,000/);assert.match(await page.locator('#hb').innerText(),/11,000/);
 assert.match(await page.locator('#homeTxBody').innerText(),/\+/);
 // Editing uses unsigned magnitude and the same explicit saving buttons.
 await page.evaluate(()=>openExistingTx(d.tx.find(isBankTx).id));
 assert.equal(await page.locator('#expenseAmount').inputValue(),'1000');
 assert.equal(await page.locator('#bankPositiveBtn').isVisible(),true);
 await page.locator('#expenseEditAmountBtn').click();await page.locator('#expenseAmount').fill('1500');await page.locator('#expenseSubmitBtn').click();
 assert.equal(await page.evaluate(()=>d.tx.find(isBankTx).amount),-1500);
 assert.match(await page.locator('#he').innerText(),/21,500/);assert.match(await page.locator('#hb').innerText(),/8,500/);
 assert.match(await page.locator('#homeTxBody').innerText(),/−/);
 await page.evaluate(()=>openExistingTx(d.tx.find(isBankTx).id));
 assert.equal(await page.locator('#expenseAmount').inputValue(),'1500');
 await page.locator('#expenseEditAmountBtn').click();await page.locator('#expenseAmount').fill('0');await page.locator('#bankPositiveBtn').click();
 assert.match(await page.locator('#he').innerText(),/20,000/);
 // Duplicate monthly correction is blocked and normal categories restore the original form.
 await page.evaluate(()=>openNewEntry('expense'));await page.selectOption('#expenseCat','הוצאות בבנק');await page.locator('#expenseAmount').fill('5');await page.locator('#bankPositiveBtn').click();
 assert.equal(await page.evaluate(()=>d.tx.filter(isBankTx).length),1);assert.ok(dialogs.some(s=>s.includes('כבר קיים תיקון')));
 await page.selectOption('#expenseCat','דברי מכולת');assert.equal(await page.locator('#bankPositiveAction').isVisible(),false);assert.equal(await page.locator('#expenseRecurringWrap').isVisible(),true);
 // A new backup/restore and reload retain signed amounts, never converting them twice.
 await page.evaluate(()=>{d.tx.find(isBankTx).amount=1000;d.tx.push({id:4,type:'expense',category:exp[0],date:'2026-02-01',amount:20000},{id:5,type:'expense',category:BANK_CATEGORY,date:'2026-02-01',amount:-1500,bankEntryMode:'adjustment'});save()});
 await page.reload();assert.equal(await page.evaluate(()=>totals('2026').adjustment),-500);assert.equal(await page.evaluate(()=>totals('2026').expense),40500);
 await page.evaluate(()=>{const restored=JSON.parse(JSON.stringify(d));applyRestoreObject(restored)});
 assert.equal(await page.evaluate(()=>totals('2026').adjustment),-500);
 for(let n=1;n<=6;n++){
  await page.evaluate(n=>{openPrintChoice();chooseReportDestination('screen');selectPrintReport(n)},n);
  const report=page.locator('#reportOutput');
  if(n<=5)assert.equal(await report.locator('[data-category]').count(),30);
  else{
   assert.equal(await report.locator('[data-comparison-row]').count(),1);
   const cells=report.locator('[data-comparison-row] td');assert.equal(await cells.count(),14);
   assert.match(await cells.nth(1).innerText(),/\+.*1,000/);assert.match(await cells.nth(2).innerText(),/−.*1,500/);assert.match(await cells.nth(3).innerText(),/0/);assert.match(await cells.last().innerText(),/−.*500/);
  }
  assert.doesNotMatch(await report.innerText(),/לא הוזן/);
  await page.evaluate(()=>{printDestination='printer';runSelectedReport()});
  const print=await page.evaluate(()=>window.__printed);assert.equal(print.landscape,true);assert.match(print.html,/הוצאות בבנק/);
  if(n<=5)assert.equal((print.html.match(/data-category=/g)||[]).length,30);else assert.equal((print.html.match(/data-comparison-row/g)||[]).length,1);
  if(n===2||n===6){
   const proof=await browser.newPage({viewport:{width:1062,height:900}});await proof.setContent(print.html);
   await proof.screenshot({path:`../pincas-output/bank-report-${n}.png`,fullPage:true});
   await proof.pdf({path:`../pincas-output/bank-report-${n}.pdf`,format:'A4',landscape:true,printBackground:true,preferCSSPageSize:true});
   if(n===2){const pdf=fs.readFileSync('../pincas-output/bank-report-2.pdf').toString('latin1');assert.equal((pdf.match(/\/Type\s*\/Page\b/g)||[]).length,1)}
   await proof.close();
  }
  await page.evaluate(()=>closePrintModal());
 }
 await page.evaluate(()=>view('reports'));assert.equal(await page.locator('#monthlyExpenseCategories [data-category]').count(),30);assert.equal(await page.locator('#annualExpenseCategories [data-category]').count(),30);
 // A legacy full total remains the same effective expenditure after conversion and reload.
 await page.evaluate(()=>{d=normalizeData({tx:[{id:11,type:'expense',category:exp[0],date:'2026-01-01',amount:20000},{id:12,type:'expense',category:BANK_CATEGORY,date:'2026-01-01',amount:21000}],selectedYear:2026,selectedMonth:1});save();initUI()});
 assert.equal(await page.evaluate(()=>d.tx.find(isBankTx).amount),-1000);assert.equal(await page.evaluate(()=>totals('2026-01').expense),21000);
 await page.reload();assert.equal(await page.evaluate(()=>totals('2026-01').expense),21000);assert.equal(await page.evaluate(()=>d.tx.find(isBankTx).amount),-1000);
 await page.screenshot({path:'../pincas-output/bank-home.png',fullPage:true});
 assert.deepEqual(errors,[]);
 console.log('PASS: two signed save buttons replace recurrence; category change retains amount; plus/minus saves and edits; 0 and duplicates; normal form restored; new restore/reload; legacy total migration; all 6 screen/native print paths; report6 one row/12 months/partial-year net total; all30 categories; A4 proof.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
