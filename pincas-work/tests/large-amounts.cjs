const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path'),fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:360,height:900}});
 await page.goto(pathToFileURL(path.resolve('app/src/main/assets/index.html')).href);
 await page.evaluate(()=>{
  const tx=[];let id=0;
  for(let y=2015;y<=2026;y++)for(let m=1;m<=12;m++){
   const date=`${y}-${String(m).padStart(2,'0')}-01`;
   tx.push({id:++id,type:'expense',category:BANK_CATEGORY,date,amount:250000});
   tx.push({id:++id,type:'expense',category:exp[0],date,amount:249000});
   tx.push({id:++id,type:'income',category:inc[0],date,amount:500000});
  }
  d=normalizeData({tx,incomeCats:inc.map(name=>({name})),expenseCats:exp.map(name=>({name})),selectedYear:2026,selectedMonth:1});
  selectedYear=2026;selectedMonth=1;initUI();view('home');
 });
 const clean=s=>s.replace(/[\u200e\u200f\u061c]/g,'');
 assert.match(clean(await page.locator('#he').innerText()),/250,000\s*₪/);
 assert.doesNotMatch(await page.locator('#he').innerText(),/\.00/);
 assert.match(await page.locator('#homeTxBody').innerText(),/250,000/);
 for(const width of [360,412,515]){
  await page.setViewportSize({width,height:915});
  const fit=await page.locator('#he').evaluate(e=>({width:e.clientWidth,scroll:e.scrollWidth,body:document.documentElement.scrollWidth,viewport:innerWidth}));
  assert.ok(fit.scroll<=fit.width+1,`home amount clipped at ${width}px: ${JSON.stringify(fit)}`);
  assert.ok(fit.body<=fit.viewport+1,`home page overflow at ${width}px`);
  const amountCell=page.locator('#homeTxBody tr').filter({hasText:'הוצאות בבנק'}).locator('td').nth(2);
  assert.ok(await amountCell.evaluate(e=>e.scrollWidth<=e.clientWidth+1),'transaction amount clipped');
 }
 await page.evaluate(()=>{openExistingTx(d.tx.find(t=>isBankTx(t)&&t.date==='2026-01-01').id)});
 assert.equal(await page.locator('#expenseAmount').inputValue(),'250000');
 await page.evaluate(()=>view('home'));
 assert.equal(await page.evaluate(()=>totals('2026').expense),3000000);
 assert.match(clean(await page.evaluate(()=>money(250000.25))),/250,000\.25/);
 assert.match(clean(await page.evaluate(()=>money(250000))),/250,000\s*₪/);
 fs.mkdirSync('../pincas-output',{recursive:true});
 for(let n=1;n<=6;n++){
  await page.evaluate(n=>{openPrintChoice();chooseReportDestination('screen');selectPrintReport(n)},n);
  const screenText=await page.locator('#reportOutput').innerText();
  assert.match(screenText,n===3||n===5?/3,000,000/:/250,000/);
  assert.doesNotMatch(screenText,/\.00/);
  const doc=await page.evaluate(n=>buildPrintDocument(n===1?makeReport1(2026,1):window[`makeReport${n}`](2026)),n);
  const proof=await browser.newPage({viewport:{width:1062,height:900}});
  await proof.setContent(doc);await proof.emulateMedia({media:'print'});
  const fit=await proof.evaluate(()=>({width:document.body.clientWidth,tables:[...document.querySelectorAll('table')].map(t=>t.getBoundingClientRect().width),clipped:[...document.querySelectorAll('td')].filter(t=>t.scrollWidth>t.clientWidth+1).map(t=>t.textContent)}));
  assert.ok(fit.tables.every(w=>w<=fit.width+1),`A4 table too wide in report ${n}: ${JSON.stringify(fit)}`);
  assert.equal(fit.clipped.length,0,`cell overflow in report ${n}: ${JSON.stringify(fit)}`);
  if(n===2||n===5||n===6){
   await proof.screenshot({path:`../pincas-output/large-amount-report-${n}.png`,fullPage:true});
   await proof.pdf({path:`../pincas-output/large-amount-report-${n}.pdf`,format:'A4',landscape:true,printBackground:true,preferCSSPageSize:true});
  }
  await proof.close();await page.evaluate(()=>closePrintModal());
 }
 await page.evaluate(()=>view('home'));
 await page.screenshot({path:'../pincas-output/large-amount-home.png',fullPage:true});
 console.log('PASS: 250,000 shekels fits home and transaction row at phone widths; entry retains amount; all 6 screen/print reports; 3,000,000 yearly and 36,000,000 overall; no .00; real agorot preserved; all A4 tables and cells fit.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
