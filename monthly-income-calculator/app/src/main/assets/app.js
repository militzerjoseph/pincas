const STORAGE_KEY = 'monthlyIncomeCalculator.v1';
const MAX_MONTHS = 1200;
const TABLE_MONTHS = 240;

function calculateModel(principal, annualRate, monthlyWithdrawal) {
  principal = Number(principal);
  annualRate = Number(annualRate);
  monthlyWithdrawal = Number(monthlyWithdrawal);

  if (!Number.isFinite(principal) || principal <= 0) throw new Error('קרן התחלתית חייבת להיות גדולה מאפס');
  if (!Number.isFinite(annualRate) || annualRate < 0) throw new Error('ריבית שנתית אינה תקינה');
  if (!Number.isFinite(monthlyWithdrawal) || monthlyWithdrawal <= 0) throw new Error('משיכה חודשית חייבת להיות גדולה מאפס');

  const monthlyRate = annualRate / 12 / 100;
  let balance = principal;
  let totalInterest = 0;
  let totalWithdrawals = 0;
  let months = 0;
  const rows = [];

  const sustainable = monthlyRate > 0 && monthlyWithdrawal <= principal * monthlyRate + 1e-9;
  const simulationLimit = sustainable ? TABLE_MONTHS : MAX_MONTHS;

  while (balance > 0.005 && months < simulationLimit) {
    const opening = balance;
    const interest = opening * monthlyRate;
    const beforeWithdrawal = opening + interest;
    const actualWithdrawal = Math.min(monthlyWithdrawal, beforeWithdrawal);
    balance = Math.max(0, beforeWithdrawal - actualWithdrawal);
    totalInterest += interest;
    totalWithdrawals += actualWithdrawal;
    months += 1;

    if (months <= TABLE_MONTHS) {
      rows.push({
        month: ((months - 1) % 12) + 1,
        year: Math.floor((months - 1) / 12) + 1,
        opening,
        interest,
        beforeWithdrawal,
        withdrawal: actualWithdrawal,
        closing: balance
      });
    }
  }

  const depleted = !sustainable && balance <= 0.005;
  const over100Years = !sustainable && !depleted && months >= MAX_MONTHS;

  return {
    principal,
    annualRate,
    monthlyWithdrawal,
    months,
    years: depleted ? months / 12 : Infinity,
    depleted,
    sustainable,
    over100Years,
    totalInterest,
    totalWithdrawals,
    finalBalance: balance,
    rows
  };
}

function ils(value) {
  return new Intl.NumberFormat('he-IL', {
    style: 'currency', currency: 'ILS', maximumFractionDigits: 0
  }).format(value);
}

function num(value) {
  return new Intl.NumberFormat('he-IL', { maximumFractionDigits: 2 }).format(value);
}

function loadValues() {
  let saved = null;
  try { saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null'); } catch (_) {}
  document.getElementById('principal').value = saved?.principal ?? 2500000;
  document.getElementById('annualRate').value = saved?.annualRate ?? 4;
  document.getElementById('monthlyWithdrawal').value = saved?.monthlyWithdrawal ?? 18000;
}

function saveValues() {
  const data = {
    principal: document.getElementById('principal').value,
    annualRate: document.getElementById('annualRate').value,
    monthlyWithdrawal: document.getElementById('monthlyWithdrawal').value
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function render(model) {
  const yearsEl = document.getElementById('yearsValue');
  const status = document.getElementById('statusPill');

  status.className = 'status';
  if (model.depleted) {
    yearsEl.textContent = `${num(model.years)} שנים`;
    status.textContent = `הקרן מספיקה ל-${model.months} חודשים`;
    status.classList.add('ok');
  } else if (model.sustainable) {
    yearsEl.textContent = 'לא נגמרת';
    status.textContent = 'המשיכה החודשית אינה גבוהה מהריבית החודשית ההתחלתית; הסיכומים מציגים 20 שנה';
    status.classList.add('ok');
  } else {
    yearsEl.textContent = 'מעל 100 שנים';
    status.textContent = 'הקרן לא הסתיימה במהלך 100 שנות סימולציה';
    status.classList.add('warn');
  }

  document.getElementById('finalBalance').textContent = ils(model.finalBalance);
  document.getElementById('totalInterest').textContent = ils(model.totalInterest);
  document.getElementById('totalWithdrawals').textContent = ils(model.totalWithdrawals);

  const body = document.getElementById('tableBody');
  body.textContent = '';
  const frag = document.createDocumentFragment();
  for (const r of model.rows) {
    const tr = document.createElement('tr');
    const vals = [r.month, r.year, ils(r.opening), ils(r.interest), ils(r.beforeWithdrawal), ils(r.withdrawal), ils(r.closing)];
    for (const v of vals) {
      const td = document.createElement('td');
      td.textContent = v;
      tr.appendChild(td);
    }
    frag.appendChild(tr);
  }
  body.appendChild(frag);
}

function calculateAndRender() {
  saveValues();
  try {
    const model = calculateModel(
      document.getElementById('principal').value,
      document.getElementById('annualRate').value,
      document.getElementById('monthlyWithdrawal').value
    );
    render(model);
  } catch (e) {
    document.getElementById('yearsValue').textContent = '—';
    const status = document.getElementById('statusPill');
    status.className = 'status warn';
    status.textContent = e.message || 'שגיאה בנתונים';
  }
}

function backupApk() {
  if (window.Android && typeof window.Android.backupApk === 'function') {
    window.Android.backupApk();
  } else {
    alert('גיבוי APK זמין בגרסת Android בלבד');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadValues();
  if (window.Android && typeof window.Android.getVersionName === 'function') {
    try { document.getElementById('version').textContent = window.Android.getVersionName(); } catch (_) {}
  }
  document.getElementById('calculateBtn').addEventListener('click', calculateAndRender);
  document.getElementById('backupBtn').addEventListener('click', backupApk);
  for (const id of ['principal', 'annualRate', 'monthlyWithdrawal']) {
    document.getElementById(id).addEventListener('change', saveValues);
  }
  calculateAndRender();
});

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { calculateModel };
}
