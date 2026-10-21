# Work 6: signed bank expense corrections

Category 30, `הוצאות בבנק`, stores an adjustment rather than the complete bank expenditure.

- Effective expense = ordinary recorded expense minus signed bank adjustment.
- Green `+` saves a positive adjustment and reduces expense. Red `−` saves a negative adjustment and increases expense.
- Enter the unsigned magnitude first. Selecting category 30 hides the recurring control, reveals the green save button in its place, and turns the existing save button red. Each button selects the sign and saves in one action.
- Existing corrections show an unsigned magnitude; the same two buttons save changes and select the sign. The pencil unlocks the amount field.
- Corrections never recur or copy to another month. One correction per month may be added; existing legacy rows are retained.
- Missing/zero corrections are zero. All existing reports show all 30 expense categories, with explicit signed corrections and corrected summaries. Whole shekels omit `.00`; actual agorot remain exact.
- Report 6 contains one row, twelve months and a signed cumulative total. It works for a partial year and supports screen and native Android printing.

## Compatibility

New correction rows carry `bankEntryMode: adjustment`, retained in backups. Legacy Work 4/5 bank rows stored complete monthly totals; normalization converts their monthly sum once to ordinary expense minus that total, preserving effective expense. A legacy zero total remains a zero correction. Original amounts are retained in `previousBankTotal`. Multiple legacy rows are kept, with the correction on the first and zero on the rest. Normalization and restoring a new backup are idempotent. Existing ordinary transactions, categories, localStorage key, package ID, signing identity, backup locations and native print bridge are preserved.

## Validation

Model checks cover both signs, zero/missing months, partial-year net sums, edit/delete, agorot, recurring exclusion, old total conversion and restore idempotence. Phone UI checks cover both saving buttons, editing magnitude/sign, normal category controls, duplicates, backup/reload, migration and all six screen/print paths. Large-amount checks cover 250,000 monthly expenses and multi-year totals within A4 landscape tables.
