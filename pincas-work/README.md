# Pincas Work 3

Independent Android household ledger. ID: com.militzerjoseph.pincaswork; namespace retained for existing resource references. User confirmed Work 2 launches and restores current data on 2026-10-20.

Work 3 preserves the H18 ledger screens, categories (10 income / 40 expense), recurring entries, reports, display scale, storage key and GS/HTML restore schema. Adds separate data/APK backup, persistent local/cloud folder selection, per-destination results and last-success dates, unique data backup names, and verified APK deduplication per destination. Default local directory is Download/גיבויים/פנקס חדש; chosen roots receive a פנקס חדש subfolder. Previous backup files are not removed. Installed APK is copied with the same signed bytes; no signing material is included in this repo.

Provider writes are read back and SHA-256 checked. A successful Google Drive document-provider operation is not a remote-server synchronization receipt. Cloud functionality and Android pickers still require physical phone verification. If the provider does not expose tree selection, it cannot be selected through this mechanism.

CI runs legacy restore regression checks, phone-browser layout/backup UI tests with mock Android bridges, native backup coordinator unit tests, and builds an unsigned universal APK. Sign releases using the permanent recovery archive PincasWork_Signing_Recovery.zip (private Library file libfile_f34320cd11e48191af3c6e773122fb86); never commit or publish its contents or password. Key alias: pincas-work; certificate SHA256: 0e6e35445d522715feed83216ee497fd87b4570057b4906f1509660c0b4c8010. Update in place; do not uninstall an app containing restored data.

All work remains on pincas-work-rebuild. Existing repository-root application and old installed Pincas are unchanged. Signing identity for Work 1, 2 and later is constant. Private financial data must never be committed.
