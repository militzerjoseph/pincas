# פנקס — גרסת Work

Source baseline collected on 2026-10-20 for a separate, maintainable Android app.

Sources: PincasHybrid_H16_With_Approved_Icon.zip (Android wrapper and approved icon) with index_H18_FINAL_INFO.html (latest located HTML patch). Application ID: com.militzerjoseph.pincaswork. Namespace remains com.example.pincashybrid to preserve source references.

The original installed app and repository root index.html are unchanged. This baseline has not been built or tested as an APK. No release signing key or passwords are included.

Next: verify build-tool compatibility; preserve a permanent release signing key with an independent recovery copy; configure GitHub Actions; verify screen layout and reports, recurring entries, old GS/HTML restore, local backup and Google Drive folder behavior on the phone. A successful provider write is not yet proof of remote cloud synchronization. Local folder selection remains to be implemented.

Data and backups are private and must never be committed here. Keep localStorage key home_budget_pro_v3_categories and backup schema compatible. Test restoration with a separate copy of a backup before relying on migration.
